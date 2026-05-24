#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
from typing import Any

from src.certify_io import raw_tensor_relpath
from src.layer_registry import LAYER_INDEX, layer_relpath, load_layer_registry

ROOT = Path(__file__).resolve().parent
MUTABLE = {"certificate.json", "manifests/file_hashes.json", "manifests/canonical.json"}

EXPECTED = {
    "00_core": "PASS",
    "01_tube_projection_section": None,
    "02_drinfeld_boundary": "DRINFELD_GROTHENDIECK_BOUNDARY_CERTIFIED",
    "03_drinfeld_grothendieck_center": "DRINFELD_GROTHENDIECK_CENTER_CERTIFIED",
    "04_drinfeld_idempotent_gluing": "DRINFELD_IDEMPOTENT_GLUING_CERTIFIED",
    "05_drinfeld_wedderburn_trace": "DRINFELD_WEDDERBURN_TRACE_CERTIFIED",
    "06_drinfeld_full_A985_lift": "DRINFELD_FULL_A985_LIFT_CERTIFIED",
    "07_ribbon_modular_boundary": "RIBBON_TWIST_TRIVIAL_AND_MODULAR_S_OBSTRUCTED",
    "08_modular_completion_obstruction": "MODULAR_COMPLETION_OBSTRUCTION_CERTIFIED",
    "09_tube_kernel_descent_audit": "TUBE_KERNEL_DESCENT_AUDIT_CERTIFIED",
    "10_adjoined_hopf_operator": "ADJOINED_HOPF_OPERATOR_CONSTRUCTED",
    "11_twist_completion_test": "TWIST_COMPLETION_OBSTRUCTED_FOR_ADJOINED_HOPF_OPERATOR",
    "12_derived_line_surface_trace": "DERIVED_LINE_SURFACE_TRACE_OPERATOR_CERTIFIED",
    "13_hesse_tube_character_pencil": "HESSE_TUBE_CHARACTER_PENCIL_CERTIFIED",
    "14_lasso_uniqueness_pseudomodular_audit": "LASSO_UNIQUENESS_AND_PSEUDOMODULAR_INVARIANT_AUDIT_CERTIFIED",
    "15_intrinsic_carrier_dependency_geometry": "INTRINSIC_CARRIER_DEPENDENCY_GEOMETRY_CERTIFIED",
    "16_mds_arc_hilbert_geometry": "MDS_ARC_HILBERT_AND_QUINTIC_WALL_CERTIFIED",
    "17_wu_golay_quintic_resolvent": "WU_GOLAY_QUINTIC_RESOLVENT_CERTIFIED_WITH_GOLAY_EXTENSION_UNRESOLVED",
    "18_canonical_24_syzygy_frame": "CANONICAL_24_COORDINATE_SYZYGY_FRAME_CERTIFIED_GOLAY_SELECTION_STILL_OPEN",
    "19_quadratic_golay_selector_obstruction": "QUADRATIC_GOLAY_SELECTOR_OBSTRUCTION_CERTIFIED",
    "20_wu_spinh_6j_marking": "WU_SPINH_OCTAD_SPIN12_6J_MARKING_CERTIFIED_GOLAY_SELECTOR_STILL_EXTERNAL",
    "21_mog_resolvent_invariant": "MOG_RESOLVENT_SEXTET_AND_WU_6J_TETRAHEDRON_CERTIFIED_GOLAY_SELECTOR_STILL_EXTERNAL",
    "22_mog_canonicity_boundary": "MOG_COLUMN_SEXTET_CANONICITY_CERTIFIED_FULL_ROW_GOLAY_SELECTOR_STILL_EXTERNAL",
    "23_full_row_refined_selector_obstruction": "FULL_ROW_REFINED_GOLAY_SELECTOR_OBSTRUCTION_CERTIFIED_HEXACODE_REQUIRED",
    "24_hexacode_row_selector": "HEXACODE_ROW_SELECTOR_CONSTRUCTED_GOLAY_CERTIFIED_CANONICALITY_EXTERNAL",
    "25_proof_system_integrity": "PROOF_SYSTEM_INTEGRITY_LADDER_BUILT",
}


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(rel: str | Path) -> Any:
    p = ROOT / rel if isinstance(rel, str) else rel
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def require(cond: bool, msg: str, errors: list[str]) -> None:
    if not cond:
        errors.append(msg)


EVIDENCE_INVARIANTS_REL = "data/d20/certified_evidence_invariants.json"
DATA_REGISTRY_REL = "data/index.json"
EXPECTED_DATA_DOMAINS = {
    "a236_compute_cache",
    "coorient_lift",
    "d20_invariants",
    "dihedral_formulae",
    "hcycle_game_control",
    "integrity_ladders",
    "quotient_selectors",
    "raw_core_seeds",
    "tensor_chain_evidence",
}
ALLOWED_DATA_ROLES = {
    "core_seed",
    "derived_invariant",
    "derived_selector",
    "evidence_archive",
    "evidence_cache",
    "reference_formula",
}
ALLOWED_DATA_STORAGE = {
    "canonical_current_layout",
    "canonical_current_layout_flat",
    "canonical_standardized_layout",
    "mixed_canonical_archive",
}


def require_sha256(value: Any, expected: str, label: str, errors: list[str]) -> None:
    require(value == expected, f"{label} sha256 mismatch", errors)


def verify_data_registry(data: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    section = data.get("data_registry", {})
    require(section.get("present") is True, "data registry missing from d20.json", errors)
    require(section.get("path") == DATA_REGISTRY_REL, "data registry path mismatch", errors)
    path = ROOT / DATA_REGISTRY_REL
    require(path.exists(), "missing data registry file", errors)
    if path.exists():
        require(section.get("file_sha256") == sha_file(path), "data registry file hash mismatch", errors)
    require(section.get("schema") == "d20.data_registry.v1", "data registry schema mismatch", errors)
    require(section.get("status") == "DATA_REGISTRY_BUILT", "data registry status mismatch", errors)

    policy = section.get("policy", {})
    require(policy.get("physical_layout") == "domain_grouped_files", "data registry physical layout mismatch", errors)
    require(policy.get("migration_stage") == "registry_first_before_bulk_move", "data registry migration stage mismatch", errors)
    ingest_policy = policy.get("ingest_policy", "")
    require(isinstance(ingest_policy, str) and "transient" in ingest_policy, "data registry ingest policy mismatch", errors)

    data_root = ROOT / "data"
    actual_dirs = sorted(p.name for p in data_root.iterdir() if p.is_dir())
    actual_files = sorted(p.name for p in data_root.iterdir() if p.is_file())
    declared_dirs = sorted(policy.get("canonical_top_level_directories", []))
    declared_files = sorted(policy.get("canonical_top_level_files", []))
    require(declared_dirs == actual_dirs, f"data top-level directory set mismatch: {sorted(set(declared_dirs) ^ set(actual_dirs))}", errors)
    require(actual_files == declared_files, f"data top-level file set mismatch: {sorted(set(declared_files) ^ set(actual_files))}", errors)
    require(section.get("observed_top_level_directories") == actual_dirs, "data registry observed directory list mismatch", errors)
    require(section.get("observed_top_level_files") == actual_files, "data registry observed file list mismatch", errors)

    domains = section.get("domains", {})
    require(isinstance(domains, dict), "data registry domains block missing", errors)
    if not isinstance(domains, dict):
        return {"domain_count": 0, "top_level_directories": actual_dirs}
    require(set(domains) == EXPECTED_DATA_DOMAINS, f"data registry domain set mismatch: {sorted(set(domains) ^ EXPECTED_DATA_DOMAINS)}", errors)

    observations = section.get("domain_observations", {})
    require(isinstance(observations, dict), "data registry observations block missing", errors)

    for domain_id, entry in domains.items():
        require(isinstance(entry, dict), f"data registry domain {domain_id} is not an object", errors)
        if not isinstance(entry, dict):
            continue
        rel = entry.get("path")
        require(isinstance(rel, str) and rel.startswith("data/"), f"{domain_id}: path is not under data/", errors)
        require(isinstance(rel, str) and "ingest" not in rel.split("/"), f"{domain_id}: path points at ingest", errors)
        if not isinstance(rel, str):
            continue
        base = ROOT / rel
        require(base.is_dir(), f"{domain_id}: data domain directory missing: {rel}", errors)
        require(entry.get("canonical_role") in ALLOWED_DATA_ROLES, f"{domain_id}: unknown canonical role", errors)
        require(entry.get("storage_status") in ALLOWED_DATA_STORAGE, f"{domain_id}: unknown storage status", errors)
        target = entry.get("target_path")
        require(isinstance(target, str) and target.startswith("data/"), f"{domain_id}: target path is not under data/", errors)
        require(isinstance(entry.get("migration_policy"), str) and bool(entry.get("migration_policy")), f"{domain_id}: migration policy missing", errors)
        classes = entry.get("file_classes", [])
        require(isinstance(classes, list) and bool(classes), f"{domain_id}: file classes missing", errors)
        if isinstance(classes, list):
            for file_class in classes:
                require(isinstance(file_class, str) and bool(file_class), f"{domain_id}: bad file class", errors)
        required_files = entry.get("required_files", [])
        require(isinstance(required_files, list) and bool(required_files), f"{domain_id}: required files missing", errors)
        if isinstance(required_files, list):
            for name in required_files:
                require(isinstance(name, str), f"{domain_id}: required file is not a string", errors)
                if isinstance(name, str):
                    require((base / name).exists(), f"{domain_id}: missing required data file {name}", errors)

        obs = observations.get(domain_id, {}) if isinstance(observations, dict) else {}
        require(isinstance(obs, dict), f"{domain_id}: observation missing", errors)
        if isinstance(obs, dict):
            require(obs.get("present") is True, f"{domain_id}: observed domain missing", errors)
            require(obs.get("path") == rel, f"{domain_id}: observed path mismatch", errors)
            require(obs.get("file_count", 0) > 0, f"{domain_id}: observed file count is zero", errors)
            require(obs.get("missing_required_files") == [], f"{domain_id}: observed missing required files", errors)

    tensor = domains.get("tensor_chain_evidence", {})
    require(tensor.get("path") == "data/evidence/tensor_chain", "tensor-chain canonical path mismatch", errors)
    require(tensor.get("storage_status") == "canonical_standardized_layout", "tensor-chain storage status should mark standardized layout", errors)
    require(tensor.get("target_path") == "data/evidence/tensor_chain", "tensor-chain target layout mismatch", errors)

    return {
        "domain_count": len(domains),
        "top_level_directories": actual_dirs,
    }


def verify_certified_evidence_invariants(data: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    section = data.get("certified_evidence_invariants", {})
    require(section.get("present") is True, "certified evidence invariants missing", errors)
    require(section.get("path") == EVIDENCE_INVARIANTS_REL, "certified evidence invariants path mismatch", errors)
    path = ROOT / EVIDENCE_INVARIANTS_REL
    require(path.exists(), "missing certified evidence invariants file", errors)
    if path.exists():
        require(section.get("file_sha256") == sha_file(path), "certified evidence invariants file hash mismatch", errors)
    require(section.get("schema") == "d20.certified_evidence_invariants.v1", "certified evidence invariants schema mismatch", errors)
    require(
        section.get("status") == "D20_CERTIFIED_EVIDENCE_INVARIANTS_INTEGRATED",
        "certified evidence invariants status mismatch",
        errors,
    )
    require(section.get("source_count") == 3, "certified evidence invariant source count mismatch", errors)

    policy = section.get("integration_policy", {})
    require(policy.get("raw_drops_are_transient") is True, "certified evidence raw-drop policy mismatch", errors)
    require(policy.get("main_certificate_reads_raw_drop_paths") is False, "certified evidence still reads raw drop paths", errors)
    require(policy.get("canonical_storage") == EVIDENCE_INVARIANTS_REL, "certified evidence canonical storage mismatch", errors)

    hashes = section.get("witness_hashes", {})
    require_sha256(hashes.get("computability_certificate_file_sha256"), "22d8f873ab39d244db917b64c2060370f49cd56e865c41e7eef7b0d575a69855", "computability witness file", errors)
    require_sha256(hashes.get("computability_certificate_self_sha256"), "d6c04263385a476c9b4a52309eecea18c40a62dd864318edc8df9ca5d61de572", "computability witness self", errors)
    require_sha256(hashes.get("classical_typing_certificate_file_sha256"), "df4e7e7db625a2ebd009a4d17549d6a45357d7a3717f29d8dd6a44f4a8de24e6", "classical typing witness file", errors)
    require_sha256(hashes.get("classical_typing_certificate_self_sha256"), "1e7f6becb9990b5ab88fa929293c86e3f69587aa4faeb52ff03927ba97f448ad", "classical typing witness self", errors)
    require_sha256(hashes.get("black_hole_certificate_file_sha256"), "80550ca1147846870c4cca1f3c5be26781cd0ff0a6edb92b1705f125e84e1029", "black-hole witness file", errors)
    require_sha256(hashes.get("black_hole_certificate_payload_sha256"), "f48790265b61f2963d5c1478764ff2011a587b192b12504c49e3b22201b41130", "black-hole witness payload", errors)
    require(
        hashes.get("black_hole_payload_hash_recomputed") == hashes.get("black_hole_certificate_payload_sha256"),
        "black-hole witness recomputed payload hash mismatch",
        errors,
    )

    comp = section.get("computability_proof", {})
    require(comp.get("status") == "D20_COMPUTABILITY_PROOF_PASS", "computability proof status mismatch", errors)
    counts = comp.get("counts", {})
    require(counts.get("A_roles") == 42, "computability proof A role count mismatch", errors)
    require(counts.get("B_atoms") == 20, "computability proof B atom count mismatch", errors)
    require(counts.get("matrix_shape") == [42, 20], "computability proof matrix shape mismatch", errors)
    require(comp.get("row_sum_id_loop") == 10, "computability proof id/loop row sum mismatch", errors)
    require(comp.get("row_sum_arrow") == 4, "computability proof arrow row sum mismatch", errors)
    require(comp.get("col_sum_all_b") == 12, "computability proof column sum mismatch", errors)
    require(comp.get("rank_Q_f") == 15, "computability proof f-rank mismatch", errors)
    require(comp.get("ker_A_dim") == 27, "computability proof A-kernel dimension mismatch", errors)
    require(comp.get("ker_B_dim") == 5, "computability proof B-kernel dimension mismatch", errors)
    require(comp.get("A_d20") == 1_341_849_600, "computability proof A_d20 mismatch", errors)
    require(comp.get("S_d20") == 14_560, "computability proof S_d20 mismatch", errors)
    require(comp.get("sum_a_Ia") == 16_102_195_200, "computability proof integral sum value mismatch", errors)
    require(comp.get("sum_a_Ia_equals_12_A_d20") is True, "computability proof integral sum mismatch", errors)
    require(comp.get("epsilon0") == 589_824, "computability proof epsilon0 mismatch", errors)
    require(comp.get("Gamma3_infinity") == 9_216, "computability proof Gamma3 infinity mismatch", errors)
    require(comp.get("kappa_D6") == 23_040, "computability proof D6 kappa mismatch", errors)
    require(comp.get("nu") == "5/2", "computability proof nu mismatch", errors)
    require(comp.get("packet_count") == 455, "computability proof packet count mismatch", errors)
    require(comp.get("identity_5epsilon0_equals_128kappa") is True, "computability proof 5epsilon0 identity mismatch", errors)
    denom = comp.get("local_entropy_denominator_histogram", {})
    require(denom == {"1": 8, "3": 8, "5": 22, "15": 4}, "computability proof entropy denominator histogram mismatch", errors)
    qsig = comp.get("A985_quarter_signature", {})
    require(qsig.get("floor_sum") == 243, "computability proof A985 quarter floor sum mismatch", errors)
    require(qsig.get("mod4_sum") == 13, "computability proof A985 mod4 sum mismatch", errors)
    require(qsig.get("mod4_rank_Q") == 3, "computability proof A985 mod4 rank mismatch", errors)
    leech = comp.get("Leech_packet_identities", {})
    require(leech.get("98280=455*6^3") is True, "computability proof Leech 98280 identity mismatch", errors)
    require(leech.get("196560=455*2*6^3") is True, "computability proof Leech 196560 identity mismatch", errors)

    fab = section.get("classical_typing", {})
    require(fab.get("schema") == "d20.fab.classical_typing.v1", "f(a)(b) classical typing schema mismatch", errors)
    require(fab.get("status") == "FAB_CLASSICAL_TYPING_VERIFIER_PASS", "f(a)(b) classical typing status mismatch", errors)
    require(fab.get("primitive_notation") == "f(a)(b)", "f(a)(b) primitive notation mismatch", errors)
    require(fab.get("deprecated_name") == "AreaInc", "f(a)(b) deprecated name mismatch", errors)
    finv = fab.get("invariants", {})
    require(finv.get("rank_Q_f_matrix") == 15, "f(a)(b) rank mismatch", errors)
    require(finv.get("atom_kernel_dimension") == 5, "f(a)(b) atom kernel dimension mismatch", errors)
    require(finv.get("role_relation_kernel_dimension") == 27, "f(a)(b) role kernel dimension mismatch", errors)
    require(finv.get("pointwise_trace_sum_a_f(a)(b)") == 12, "f(a)(b) pointwise trace mismatch", errors)
    require(finv.get("column_support_counts_unique") == [4, 10], "f(a)(b) support-count signature mismatch", errors)
    require(finv.get("sum_a_I(a)") == 16_102_195_200, "f(a)(b) integral sum value mismatch", errors)
    require(finv.get("sum_a_I(a)_equals_12_A_d20") is True, "f(a)(b) integral sum mismatch", errors)
    require(finv.get("A_d20") == 1_341_849_600, "f(a)(b) A_d20 mismatch", errors)
    require(finv.get("S_d20") == 14_560, "f(a)(b) S_d20 mismatch", errors)
    require(finv.get("W_D6") == 23_040, "f(a)(b) W_D6 mismatch", errors)
    fab_sets = fab.get("sets", {})
    require(fab_sets.get("A_size") == 42, "f(a)(b) A size mismatch", errors)
    require(fab_sets.get("B_size") == 20, "f(a)(b) B size mismatch", errors)
    require(fab_sets.get("H6") == ["B-", "B+", "V-", "V+", "S-", "S+"], "f(a)(b) H6 order mismatch", errors)

    bh = section.get("black_hole_certified_simulator", {})
    require(bh.get("schema") == "d20.black_hole.certified_simulator@3", "black-hole simulator schema mismatch", errors)
    require(bh.get("status") == "D20_BLACK_HOLE_CERTIFIED_SIMULATOR_PASS", "black-hole simulator status mismatch", errors)
    require(bh.get("all_checks_pass") is True, "black-hole simulator checks not all pass", errors)
    for key, value in bh.get("checks", {}).items():
        require(value is True, f"black-hole simulator check failed: {key}", errors)
    dinv = bh.get("d20_invariants", {})
    core = dinv.get("core", {})
    require(core.get("d20_status") == "D20_CERTIFIED", "black-hole simulator d20 status mismatch", errors)
    require(core.get("relation_count_A985") == 985, "black-hole simulator relation count mismatch", errors)
    require(core.get("tensor_support_A985") == 1_414_965, "black-hole simulator tensor support mismatch", errors)
    require(core.get("tensor_coefficient_total_A985") == 2_537_360, "black-hole simulator tensor coefficient mismatch", errors)
    require(core.get("object_pair_matrix_shape") == [6, 6], "black-hole simulator object-pair shape mismatch", errors)
    require(core.get("A42_classes") == 42, "black-hole simulator A42 count mismatch", errors)
    require(core.get("A12_classes") == 12, "black-hole simulator A12 count mismatch", errors)
    require(core.get("A42_to_A12_consistent") is True, "black-hole simulator A42/A12 consistency mismatch", errors)
    require(core.get("dodecad_shell_size") == 2576, "black-hole simulator dodecad shell size mismatch", errors)
    board = dinv.get("board", {})
    require(board.get("vertices") == 20, "black-hole simulator board vertex count mismatch", errors)
    require(board.get("edges") == 30, "black-hole simulator board edge count mismatch", errors)
    require(board.get("degree") == 3, "black-hole simulator board degree mismatch", errors)
    require(board.get("girth") == 5, "black-hole simulator board girth mismatch", errors)
    require(board.get("diameter") == 5, "black-hole simulator board diameter mismatch", errors)
    require(board.get("cycle_rank") == 11, "black-hole simulator board cycle-rank mismatch", errors)
    require(board.get("automorphism_count") == 120, "black-hole simulator board automorphism mismatch", errors)
    require(board.get("faces_are_all_C6_3") is True, "black-hole simulator board face mismatch", errors)
    q = dinv.get("quinticity_area_law", {})
    require(q.get("epsilon0") == 589_824, "black-hole simulator epsilon0 mismatch", errors)
    require(q.get("Gamma_3_infty_order") == 9_216, "black-hole simulator Gamma_3_infty order mismatch", errors)
    require(q.get("W_D6_order") == 23_040, "black-hole simulator W_D6 order mismatch", errors)
    require(q.get("W_D6_over_Gamma_3_infty") == "5/2", "black-hole simulator W_D6/Gamma ratio mismatch", errors)
    require(q.get("protected_entropy_packet") == "32", "black-hole simulator protected entropy packet mismatch", errors)
    require(q.get("closed_packets_in_E_d20") == 455, "black-hole simulator closed packet count mismatch", errors)
    require(q.get("S_d20") == 14_560, "black-hole simulator S_d20 mismatch", errors)
    rgba = dinv.get("rgba_forcing", {})
    require(rgba.get("RGBA_total") == 32, "black-hole simulator RGBA total mismatch", errors)
    require(rgba.get("RGB_visible_payload_dim") == 24, "black-hole simulator RGB payload dimension mismatch", errors)
    require(rgba.get("complete_BVS_count") == 8, "black-hole simulator complete BVS count mismatch", errors)
    require(rgba.get("boundary_count") == 12, "black-hole simulator boundary count mismatch", errors)
    wall = dinv.get("tropical_wall_summary", {})
    require(wall.get("collision_levels") == [72, 96], "black-hole simulator wall collision levels mismatch", errors)
    require(wall.get("wall_gap") == 24, "black-hole simulator wall gap mismatch", errors)
    require(wall.get("closed_wall_gap") == 120, "black-hole simulator closed wall gap mismatch", errors)
    require(wall.get("face_mass_count") == 20, "black-hole simulator face mass count mismatch", errors)
    inverse = bh.get("pole_packet", {}).get("exact_inverse_audit", {})
    require(inverse.get("max_abs_err_M", 1.0) < 1e-12, "black-hole simulator inverse M precision mismatch", errors)
    require(inverse.get("max_abs_err_a", 1.0) < 1e-12, "black-hole simulator inverse a precision mismatch", errors)
    require(inverse.get("max_abs_err_Q", 1.0) < 1e-12, "black-hole simulator inverse Q precision mismatch", errors)
    sim = bh.get("simulation_summary", {})
    require(sim.get("visited_states") == 20, "black-hole simulator visited state count mismatch", errors)
    require(sim.get("integrity_projection_count") == 0, "black-hole simulator integrity projection count mismatch", errors)

    return {
        "source_count": section.get("source_count"),
        "path": section.get("path"),
    }


def verify_root(errors: list[str]) -> dict[str, Any]:
    cert = load_json("certificate.json")
    require(cert.get("schema") in {"d20.verifier.v1", "d20.verifier.v2"}, "root schema mismatch", errors)
    require(cert.get("status") == "D20_CERTIFIED", "root status mismatch", errors)
    h = cert.get("d20_sha256")
    body = {k: v for k, v in cert.items() if k != "d20_sha256"}
    require(isinstance(h, str) and len(h) == 64 and h == sha_json(body), "root self-hash mismatch", errors)
    return cert


def verify_root_layers(root: dict[str, Any], registry: dict[str, Any], errors: list[str]) -> None:
    root_layers = root.get("layers", [])
    registry_layers = registry.get("layers", [])
    require(isinstance(root_layers, list), "root layers list missing", errors)
    require(isinstance(registry_layers, list), "registry layers list missing", errors)
    if not isinstance(root_layers, list) or not isinstance(registry_layers, list):
        return

    by_id = {entry.get("id"): entry for entry in root_layers if isinstance(entry, dict)}
    require(len(root_layers) == len(registry_layers), "root layer count does not match registry", errors)
    for entry in registry_layers:
        if not isinstance(entry, dict):
            continue
        layer_id = entry.get("id")
        rel = entry.get("path")
        root_entry = by_id.get(layer_id)
        require(isinstance(root_entry, dict), f"root certificate missing layer id: {layer_id}", errors)
        if not isinstance(root_entry, dict) or not isinstance(rel, str):
            continue
        p = ROOT / rel
        require(root_entry.get("certificate") == rel, f"root layer path mismatch for {layer_id}", errors)
        require(root_entry.get("legacy_dir") == entry.get("legacy_dir"), f"root legacy_dir mismatch for {layer_id}", errors)
        require(root_entry.get("group") == entry.get("group"), f"root group mismatch for {layer_id}", errors)
        require(root_entry.get("status") == entry.get("expected_status"), f"root status mismatch for {layer_id}", errors)
        if p.exists():
            require(root_entry.get("certificate_file_sha256") == sha_file(p), f"root layer hash mismatch for {layer_id}", errors)


def verify_d20_json(errors: list[str]) -> dict[str, Any]:
    p = ROOT / "d20.json"
    require(p.exists(), "missing d20.json", errors)
    if not p.exists():
        return {}
    data = load_json(p)
    require(data.get("schema") == "d20.object.v2", "d20.json schema mismatch", errors)
    require(data.get("status") == "D20_CERTIFIED", "d20.json status mismatch", errors)
    require(data.get("object") == "d20", "d20.json object mismatch", errors)
    h = data.get("d20_sha256")
    body = {k: v for k, v in data.items() if k != "d20_sha256"}
    require(isinstance(h, str) and len(h) == 64 and h == sha_json(body), "d20.json self-hash mismatch", errors)
    required_sections = [
        "core_invariants",
        "optics",
        "game_theory",
        "zero_axiom_coorient",
        "universal_integral_uniqueness",
        "pre_A985_relation_body_theorem",
        "data_registry",
        "certified_evidence_invariants",
        "tensor_chain",
        "layer_registry",
        "layer_certificates",
        "json_invariants",
        "npz_array_manifests",
        "source_manifest",
    ]
    for sec in required_sections:
        require(sec in data, f"d20.json missing section: {sec}", errors)
    z = data.get("zero_axiom_coorient", {})
    require(z.get("status") == "D20_ZERO_AXIOM_COORIENT_REDUCTION_PASS", "zero_axiom_coorient status mismatch", errors)
    base = z.get("canonical_base_derivation", {})
    require(base.get("base") == [18, 67, 37], "zero_axiom canonical base mismatch", errors)
    require(base.get("matches_stored_canonical_base") is True, "zero_axiom canonical base not matched", errors)
    require(base.get("separates_all_points") is True, "zero_axiom base does not separate all points", errors)
    marker = z.get("coorient_generator_marker", {})
    require(marker.get("integer_count") == 12, "coorient generator marker integer count mismatch", errors)
    u = data.get("universal_integral_uniqueness", {})
    require(u.get("status") == "UNIVERSAL_A985_INTEGRAL_UNIQUENESS_PASS", "universal integral uniqueness status mismatch", errors)
    uc = u.get("coorient_lift_uniqueness_computation", {})
    require(uc.get("internal_base_type_candidate_triples") == 18432, "universal integral internal candidate count mismatch", errors)
    require(uc.get("coherent_signature_lift_triples") == 9216, "universal integral lift count mismatch", errors)
    require(uc.get("generated_action_order") == 9216, "universal integral generated action order mismatch", errors)
    ur = u.get("uniqueness_result", {})
    require(ur.get("A985_integral_uniqueness_computed") is True, "A985 integral uniqueness not computed", errors)
    require(ur.get("coorient_action_group_unique") is True, "coorient action group uniqueness mismatch", errors)
    require(ur.get("remaining_12_integers_are_semantic_seed") is False, "12 integers still marked as semantic seed", errors)
    pre = data.get("pre_A985_relation_body_theorem", {})
    require(pre.get("status") == "PRE_A985_RELATION_BODY_DERIVED_WITHOUT_RELATION_TABLE_PASS", "pre-A985 relation body theorem status mismatch", errors)
    pr = pre.get("result", {})
    require(pr.get("uses_relation_table_as_input") is False, "pre-A985 theorem uses relation table as input", errors)
    require(pr.get("A985_relation_count") == 985, "pre-A985 relation count mismatch", errors)
    require(pr.get("T985_support") == 1414965, "pre-A985 tensor support mismatch", errors)
    data_registry = verify_data_registry(data, errors)
    evidence_invariants = verify_certified_evidence_invariants(data, errors)
    tensor_chain = data.get("tensor_chain", {})
    require(tensor_chain.get("status") == "TENSOR_CHAIN_EVIDENCE_CERTIFIED", "tensor_chain status mismatch", errors)
    require(tensor_chain.get("present") is True, "tensor_chain evidence missing", errors)
    require(tensor_chain.get("public_name") == "tensor_chain", "tensor_chain public name mismatch", errors)
    require(tensor_chain.get("path") == "data/evidence/tensor_chain", "tensor_chain path mismatch", errors)
    plain_name_view = tensor_chain.get("plain_name_view", {})
    require(plain_name_view.get("present") is True, "tensor_chain plain-name view missing", errors)
    require(plain_name_view.get("status") == "TENSOR_CHAIN_PLAIN_NAME_VIEW_GENERATED", "tensor_chain plain-name view status mismatch", errors)
    plain_name_summary = plain_name_view.get("summary", {})
    require(plain_name_summary.get("source_file_count", 0) > 0, "tensor_chain plain-name view has no files", errors)
    require(plain_name_summary.get("changed_file_alias_count", 0) > 0, "tensor_chain plain-name view has no renamed file aliases", errors)
    require(
        plain_name_summary.get("remaining_legacy_plain_token_count") == 0,
        "tensor_chain plain-name view still contains legacy glossary tokens",
        errors,
    )
    fin = data.get("final_investigation", {})
    require(fin.get("status") == "D20_INVESTIGATION_FINALIZED_WITH_A985_INTEGRAL_UNIQUENESS", "final investigation status mismatch", errors)
    require(fin.get("finite_computational_closure") is True, "final investigation finite closure mismatch", errors)
    require(fin.get("A985_integral_uniqueness_computed") is True, "final investigation A985 uniqueness mismatch", errors)
    require(fin.get("coorient_action_group_unique_over_A985") is True, "final investigation coorient uniqueness mismatch", errors)
    require(fin.get("full_zero_axiom_constructor") is False, "final investigation zero-axiom boundary mismatch", errors)
    rb = fin.get("remaining_boundary", {})
    require(rb.get("remaining_seed_integer_count_in_A985_integral_theory") == 0, "final investigation remaining A985-integral seed count mismatch", errors)
    registry = data.get("layer_registry", {})
    require(registry.get("schema") == "d20.layer_registry.v1", "d20 layer registry schema mismatch", errors)
    require(registry.get("status") == "LAYER_REGISTRY_BUILT", "d20 layer registry status mismatch", errors)
    require(registry.get("path") == "layers/index.json", "d20 layer registry path mismatch", errors)
    require(len(registry.get("layers", [])) == len(EXPECTED), "d20 layer registry entry count mismatch", errors)
    if LAYER_INDEX.exists():
        require(registry.get("file_sha256") == sha_file(LAYER_INDEX), "d20 layer registry file hash mismatch", errors)

    return {
        "schema": data.get("schema"),
        "status": data.get("status"),
        "file_sha256": sha_file(p),
        "object_sha256": h,
        "size": p.stat().st_size,
        "section_count": len(data),
        "layer_count": len(data.get("layer_certificates", {})),
        "layer_registry_entries": len(registry.get("layers", [])),
        "json_invariant_file_count": len(data.get("json_invariants", {})),
        "npz_array_manifest_count": len(data.get("npz_array_manifests", {})),
        "data_registry_domain_count": data_registry.get("domain_count"),
        "certified_evidence_source_count": evidence_invariants.get("source_count"),
        "tensor_chain_present": bool(tensor_chain.get("present", False)),
        "hcycle_present": bool(data.get("game_theory", {}).get("present", False)),
        "hcycle_primitive_cycles": data.get("game_theory", {}).get("primitive_H_cycles", {}).get("count"),
        "hcycle_state_space": data.get("game_theory", {}).get("state_space", {}).get("S20_order"),
    }


def verify_layer_registry(errors: list[str]) -> tuple[dict[str, Any], dict[str, Any]]:
    require(LAYER_INDEX.exists(), "missing layer registry: layers/index.json", errors)
    if not LAYER_INDEX.exists():
        return {}, {"registry_entries": 0, "groups": []}

    data = load_layer_registry()
    require(data.get("schema") == "d20.layer_registry.v1", "layer registry schema mismatch", errors)
    require(data.get("status") == "LAYER_REGISTRY_BUILT", "layer registry status mismatch", errors)

    groups = data.get("groups", {})
    policy = data.get("policy", {})
    layers = data.get("layers", [])
    require(isinstance(groups, dict) and bool(groups), "layer registry groups missing", errors)
    require(isinstance(policy, dict), "layer registry policy missing", errors)
    require(isinstance(layers, list) and bool(layers), "layer registry layers missing", errors)
    if isinstance(policy, dict):
        require(policy.get("physical_layout") == "semantic_grouped_files", "layer registry physical layout is not flat semantic groups", errors)
        require(policy.get("path_migration") == "complete", "layer registry path migration is not complete", errors)

    ids: set[str] = set()
    dirs: set[str] = set()
    ordinals: set[int] = set()
    group_names = set(groups) if isinstance(groups, dict) else set()

    for i, entry in enumerate(layers if isinstance(layers, list) else []):
        require(isinstance(entry, dict), f"layer registry entry {i} is not an object", errors)
        if not isinstance(entry, dict):
            continue

        layer_id = entry.get("id")
        dirname = entry.get("legacy_dir")
        ordinal = entry.get("ordinal")
        group = entry.get("group")
        rel = entry.get("path")
        legacy_rel = entry.get("legacy_path")

        require(isinstance(layer_id, str) and bool(layer_id), f"layer registry entry {i} missing id", errors)
        require(layer_id not in ids, f"duplicate layer id: {layer_id}", errors)
        if isinstance(layer_id, str):
            ids.add(layer_id)

        require(isinstance(dirname, str) and bool(dirname), f"{layer_id}: missing legacy_dir", errors)
        require(dirname not in dirs, f"duplicate layer legacy_dir: {dirname}", errors)
        if isinstance(dirname, str):
            dirs.add(dirname)

        require(isinstance(ordinal, int), f"{layer_id}: ordinal is not an integer", errors)
        require(ordinal not in ordinals, f"duplicate layer ordinal: {ordinal}", errors)
        if isinstance(ordinal, int):
            ordinals.add(ordinal)

        require(group in group_names, f"{layer_id}: unknown group {group!r}", errors)
        require(isinstance(rel, str), f"{layer_id}: path is not a string", errors)
        if isinstance(dirname, str):
            expected_legacy_rel = f"layers/{dirname}/certificate.json"
            require(legacy_rel == expected_legacy_rel, f"{layer_id}: legacy_path {legacy_rel!r} != {expected_legacy_rel!r}", errors)
        if isinstance(group, str) and isinstance(rel, str):
            rel_path = Path(rel)
            require(rel_path.parent.as_posix() == f"layers/{group}", f"{layer_id}: path {rel!r} is not a direct child of its group", errors)
            require(rel_path.suffix == ".json" and rel_path.name != "certificate.json", f"{layer_id}: path {rel!r} is not a flat JSON certificate", errors)
            require((ROOT / rel).exists(), f"{layer_id}: registry path missing: {rel}", errors)
            require(rel != legacy_rel, f"{layer_id}: path still points at legacy layout", errors)

        if isinstance(dirname, str) and dirname in EXPECTED:
            require(
                entry.get("expected_status") == EXPECTED[dirname],
                f"{layer_id}: expected_status does not match verifier expectation for {dirname}",
                errors,
            )

        depends_on = entry.get("depends_on", [])
        require(isinstance(depends_on, list), f"{layer_id}: depends_on is not a list", errors)
        if isinstance(depends_on, list):
            for dep in depends_on:
                require(isinstance(dep, str), f"{layer_id}: dependency id is not a string", errors)

    require(dirs == set(EXPECTED), f"layer registry legacy_dir set mismatch: {sorted(dirs ^ set(EXPECTED))}", errors)
    require(ordinals == set(range(len(EXPECTED))), "layer registry ordinal set mismatch", errors)

    for entry in layers if isinstance(layers, list) else []:
        if not isinstance(entry, dict):
            continue
        layer_id = entry.get("id")
        depends_on = entry.get("depends_on", [])
        if not isinstance(depends_on, list):
            continue
        for dep in depends_on:
            if isinstance(dep, str):
                require(dep in ids, f"{layer_id}: unknown dependency {dep}", errors)

    return data, {
        "schema": data.get("schema"),
        "status": data.get("status"),
        "registry_entries": len(layers) if isinstance(layers, list) else 0,
        "groups": sorted(group_names),
        "physical_layout": policy.get("physical_layout") if isinstance(policy, dict) else None,
        "path_migration": policy.get("path_migration") if isinstance(policy, dict) else None,
        "file_sha256": sha_file(LAYER_INDEX),
    }


def verify_layer_layout(registry: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    layer_root = ROOT / "layers"
    require(layer_root.is_dir(), "missing layers directory", errors)
    if not layer_root.is_dir():
        return {
            "status": "MISSING",
            "groups": [],
            "certificate_files": 0,
            "summary_files": 0,
        }

    groups = registry.get("groups", {})
    group_names = set(groups) if isinstance(groups, dict) else set()
    actual_top_dirs = {p.name for p in layer_root.iterdir() if p.is_dir()}
    top_files = {p.name for p in layer_root.iterdir() if p.is_file()}

    require(actual_top_dirs == group_names, f"layer group directory set mismatch: {sorted(actual_top_dirs ^ group_names)}", errors)
    require(top_files <= {"index.json"}, f"unexpected top-level layer files: {sorted(top_files - {'index.json'})}", errors)

    nested_dirs = [
        p.relative_to(ROOT).as_posix()
        for p in layer_root.rglob("*")
        if p.is_dir() and p.parent != layer_root
    ]
    require(not nested_dirs, f"nested layer directories are not allowed: {nested_dirs}", errors)

    registry_files = {
        entry.get("path")
        for entry in registry.get("layers", [])
        if isinstance(entry, dict) and isinstance(entry.get("path"), str)
    }
    unexpected_files: list[str] = []
    summary_files: list[str] = []
    for path in layer_root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel == "layers/index.json":
            continue
        rel_path = Path(rel)
        parts = rel_path.parts
        is_direct_group_file = len(parts) == 3 and parts[0] == "layers" and parts[1] in group_names
        if not is_direct_group_file or rel_path.suffix != ".json":
            unexpected_files.append(rel)
            continue
        if rel in registry_files:
            continue
        if rel_path.name.endswith(".summary.json"):
            summary_files.append(rel)
            continue
        unexpected_files.append(rel)

    require(not unexpected_files, f"unexpected layer files: {unexpected_files}", errors)

    return {
        "status": "PASS" if not nested_dirs and not unexpected_files and actual_top_dirs == group_names and top_files <= {"index.json"} else "FAIL",
        "groups": sorted(actual_top_dirs),
        "certificate_files": len(registry_files),
        "summary_files": len(summary_files),
    }


def verify_layers(errors: list[str], registry: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    entries = registry.get("layers", [])
    if not isinstance(entries, list) or not entries:
        entries = [
            {
                "id": dirname,
                "group": "legacy",
                "legacy_dir": dirname,
                "path": f"layers/{dirname}/certificate.json",
                "expected_status": expected_status,
            }
            for dirname, expected_status in EXPECTED.items()
        ]

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        dirname = entry.get("legacy_dir")
        rel = entry.get("path")
        expected_status = entry.get("expected_status")
        if not isinstance(dirname, str) or not isinstance(rel, str):
            continue
        p = ROOT / rel
        require(p.exists(), f"missing layer certificate: {rel}", errors)
        if not p.exists():
            continue
        data = load_json(p)
        status = data.get("status")
        if expected_status is not None:
            require(status == expected_status, f"{dirname}: status {status!r} != {expected_status!r}", errors)
        rows.append({
            "id": entry.get("id"),
            "group": entry.get("group"),
            "layer": dirname,
            "status": status,
            "file_sha256": sha_file(p),
        })
    return rows


def verify_core_arrays(errors: list[str]) -> dict[str, Any]:
    import numpy as np

    out: dict[str, Any] = {}
    z = np.load(ROOT / raw_tensor_relpath())
    triples = np.asarray(z["triples"], dtype=np.int64)
    reps = np.asarray(z["reps"], dtype=np.int64)
    M = np.asarray(z["M"], dtype=np.int64)
    require(triples.shape == (1_414_965, 4), f"tensor triples shape mismatch: {triples.shape}", errors)
    require(int(triples[:, 3].sum()) == 2_537_360, "tensor coefficient total mismatch", errors)
    require(reps.shape == (985, 5), f"reps shape mismatch: {reps.shape}", errors)
    require(M.shape == (6, 6), f"object-pair matrix shape mismatch: {M.shape}", errors)
    out.update({
        "tensor_support": int(triples.shape[0]),
        "tensor_coefficient_total": int(triples[:, 3].sum()),
        "relation_count": int(reps.shape[0]),
        "object_pair_matrix_shape": list(M.shape),
    })

    q = np.load(ROOT / "data/raw/quotients.npz")
    q42 = np.asarray(q["q42_map"], dtype=np.int64)
    q12 = np.asarray(q["q12_map"], dtype=np.int64)
    q42t = np.asarray(q["q42_tensor"], dtype=np.int64)
    q12t = np.asarray(q["q12_tensor"], dtype=np.int64)
    require(q42.shape == (985,), f"q42 map shape mismatch: {q42.shape}", errors)
    require(q12.shape == (985,), f"q12 map shape mismatch: {q12.shape}", errors)
    require(q42t.shape == (42, 42, 42), f"q42 tensor shape mismatch: {q42t.shape}", errors)
    require(q12t.shape == (12, 12, 12), f"q12 tensor shape mismatch: {q12t.shape}", errors)
    consistent = True
    for c in range(42):
        vals = np.unique(q12[q42 == c])
        if vals.size != 1:
            consistent = False
            break
    require(consistent, "q42 -> q12 consistency failed", errors)
    out.update({
        "q42_classes": 42,
        "q12_classes": 12,
        "q42_to_q12_consistent": bool(consistent),
        "q42_tensor_nonzero": int(np.count_nonzero(q42t)),
        "q12_tensor_nonzero": int(np.count_nonzero(q12t)),
    })

    b = np.load(ROOT / "data/raw/simple_branching_matrices.npz")
    B236_42 = np.asarray(b["B236_42"], dtype=np.int64)
    B42_12 = np.asarray(b["B42_12"], dtype=np.int64)
    B236_12 = np.asarray(b["B236_12"], dtype=np.int64)
    comp = np.asarray(b["comp"], dtype=np.int64)
    naturality = np.array_equal(B236_42 @ B42_12, B236_12) and np.array_equal(comp, B236_12)
    require(naturality, "simple branching naturality failed", errors)
    out.update({
        "simple_branching_naturality": bool(naturality),
        "B236_to_A42_shape": list(B236_42.shape),
        "B42_to_A12_shape": list(B42_12.shape),
        "B236_to_A12_shape": list(B236_12.shape),
    })

    l = np.load(ROOT / "data/raw/leech_projective_generators.npz")
    arr_keys = sorted(l.files)
    shape_found = None
    for k in arr_keys:
        a = np.asarray(l[k])
        if a.shape == (98280, 24):
            shape_found = list(a.shape)
            break
    require(shape_found == [98280, 24], "Leech projective generator shape [98280,24] not found", errors)
    out.update({"leech_projective_vectors_shape": shape_found})
    return out


def verify_integrity(errors: list[str], registry: dict[str, Any]) -> dict[str, Any]:
    data = load_json(layer_relpath("integrity.proof_system", registry))
    summary = data.get("summary", {})
    fb = summary.get("finite_base", {})
    expected = {
        "primitive_kernel_sector": [33],
        "public_rank": 20,
        "public_kernel_dimension": 19,
        "operation_algebra_dimension": 36,
        "integrity_integral_dimension": 1,
        "integrity_integral_codimension": 35,
        "Pi33_in_full_operation_algebra": False,
        "delta33_after_public_integral_operations": False,
    }
    for k, v in expected.items():
        require(fb.get(k) == v, f"integrity gate mismatch {k}: {fb.get(k)!r} != {v!r}", errors)
    return fb


def verify_manifest(errors: list[str]) -> dict[str, Any]:
    man = load_json("manifests/file_hashes.json")
    checked = 0
    for ent in man.get("entries", []):
        rel = ent["path"]
        p = ROOT / rel
        require(p.exists(), f"manifest path missing: {rel}", errors)
        if not p.exists():
            continue
        require(p.stat().st_size == ent["size"], f"manifest size mismatch: {rel}", errors)
        require(sha_file(p) == ent["sha256"], f"manifest sha mismatch: {rel}", errors)
        checked += 1
    return {"manifest_entries_checked": checked}


def verify_constructor_witness(errors: list[str]) -> dict[str, Any]:
    try:
        from src.certify_constructor import construct_from_supplied_raw_seeds

        witness = construct_from_supplied_raw_seeds()
    except Exception as exc:
        errors.append(f"constructor witness exception: {type(exc).__name__}: {exc}")
        return {"status": "ERROR", "error": f"{type(exc).__name__}: {exc}"}

    require(witness.get("schema") == "d20.constructor.supplied_raw_seed_result", "constructor witness schema mismatch", errors)
    require(witness.get("constructor_status") == "RAW_SEED_CONSTRUCTOR_PASS", "constructor witness status mismatch", errors)
    require(witness.get("constructs_from_supplied_raw_seeds") is True, "constructor witness did not use supplied raw seeds", errors)
    require(witness.get("full_scratch_object_constructor") is False, "constructor witness overclaims full scratch construction", errors)
    require(witness.get("zero_axiom_reduction_available") is True, "constructor witness zero-axiom reduction missing", errors)

    finite = witness.get("finite_object", {})
    require(finite.get("points") == 2576, "constructor witness point count mismatch", errors)
    require(finite.get("group_order_from_seed") == 9216, "constructor witness group order mismatch", errors)
    require(finite.get("relations") == 985, "constructor witness relation count mismatch", errors)
    require(finite.get("object_pair_relation_matrix_matches_tensor_header") is True, "constructor witness relation matrix mismatch", errors)
    require(finite.get("ordered_pair_partition_ok") is True, "constructor witness ordered-pair partition failed", errors)
    require(finite.get("block_mass_is_object_size_outer_product") is True, "constructor witness block mass failed", errors)

    tensor = witness.get("tensor", {})
    require(tensor.get("support") == 1_414_965, "constructor witness tensor support mismatch", errors)
    require(tensor.get("coefficient_total") == 2_537_360, "constructor witness tensor coefficient total mismatch", errors)

    quotients = witness.get("generated_quotients", {})
    q42 = quotients.get("q42", {})
    q12 = quotients.get("q12", {})
    require(q42.get("matches_supplied_q42_tensor") is True, "constructor witness q42 tensor mismatch", errors)
    require(q12.get("matches_supplied_q12_tensor") is True, "constructor witness q12 tensor mismatch", errors)
    require(quotients.get("q42_to_q12_consistent") is True, "constructor witness q42 -> q12 consistency failed", errors)

    branching = witness.get("simple_branching", {})
    require(branching.get("naturality_exact") is True, "constructor witness simple branching naturality failed", errors)
    require(branching.get("defect_l1") == 0, "constructor witness simple branching defect mismatch", errors)

    return {
        "status": witness.get("constructor_status"),
        "schema": witness.get("schema"),
        "result_sha256": witness.get("constructor_result_sha256"),
        "constructs_from_supplied_raw_seeds": witness.get("constructs_from_supplied_raw_seeds"),
        "full_scratch_object_constructor": witness.get("full_scratch_object_constructor"),
        "seed_boundary": witness.get("seed_boundary"),
        "finite_object": finite,
        "tensor": {
            "support": tensor.get("support"),
            "coefficient_total": tensor.get("coefficient_total"),
            "tensor_sha256": tensor.get("tensor_sha256"),
        },
        "generated_quotients": {
            "q42_matches_supplied_tensor": q42.get("matches_supplied_q42_tensor"),
            "q12_matches_supplied_tensor": q12.get("matches_supplied_q12_tensor"),
            "q42_to_q12_consistent": quotients.get("q42_to_q12_consistent"),
        },
        "simple_branching": branching,
        "missing_full_scratch_steps": witness.get("missing_full_scratch_steps"),
    }


def verify_tamper_resistance() -> dict[str, Any]:
    data = load_json("d20.json")
    clean_errors: list[str] = []
    verify_certified_evidence_invariants(data, clean_errors)

    def cloned() -> dict[str, Any]:
        return json.loads(json.dumps(data))

    cases: list[dict[str, Any]] = []

    def add_case(name: str, expected_error: str, mutate: Any) -> None:
        tampered = cloned()
        mutate(tampered["certified_evidence_invariants"])
        errors: list[str] = []
        verify_certified_evidence_invariants(tampered, errors)
        cases.append({
            "name": name,
            "expected_error": expected_error,
            "detected": expected_error in errors,
            "errors": errors,
        })

    add_case(
        "computability witness hash",
        "computability witness file sha256 mismatch",
        lambda section: section["witness_hashes"].__setitem__("computability_certificate_file_sha256", "0" * 64),
    )
    add_case(
        "black-hole epsilon0",
        "black-hole simulator epsilon0 mismatch",
        lambda section: section["black_hole_certified_simulator"]["d20_invariants"]["quinticity_area_law"].__setitem__("epsilon0", 0),
    )

    errors = list(clean_errors)
    for case in cases:
        if not case["detected"]:
            errors.append(f"tamper case did not fail closed: {case['name']}")

    return {
        "status": "PASS" if not errors else "FAIL",
        "mode": "tamper",
        "clean_evidence": "PASS" if not clean_errors else "FAIL",
        "cases": cases,
        "errors": errors,
    }


def run(mode: str) -> dict[str, Any]:
    if mode == "tamper":
        return verify_tamper_resistance()

    errors: list[str] = []
    root = verify_root(errors)
    d20 = verify_d20_json(errors)
    layer_registry, layer_registry_summary = verify_layer_registry(errors)
    layer_layout = verify_layer_layout(layer_registry, errors)
    verify_root_layers(root, layer_registry, errors)
    layers = verify_layers(errors, layer_registry)
    core = verify_core_arrays(errors)
    integrity = verify_integrity(errors, layer_registry)
    out: dict[str, Any] = {
        "status": "PASS" if not errors else "FAIL",
        "mode": mode,
        "headline": root.get("status"),
        "d20": d20,
        "layer_registry": layer_registry_summary,
        "layer_layout": layer_layout,
        "layer_count": len(layers),
        "core": core,
        "integrity": integrity,
        "errors": errors,
    }
    if mode in {"audit", "rebuild"}:
        out["constructor_witness"] = verify_constructor_witness(errors)
        out["manifest"] = verify_manifest(errors)
        out["status"] = "PASS" if not errors else "FAIL"
    if mode == "rebuild":
        out["rebuild"] = "d20.json and source certificates checked; generated cache is not required"
    return out


def maybe_regenerate(mode: str, pretty: bool, enabled: bool) -> dict[str, Any]:
    if not enabled:
        return {"regenerated_before_certification": False}
    import regen
    regen.rebuild_d20(pretty=pretty)
    regen.refresh_certificate()
    count = regen.refresh_manifest()
    return {"regenerated_before_certification": True, "manifest_entries_refreshed": count}


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Verify the d20 bundle. Only --mode rebuild or --regenerate rewrites files."
    )
    ap.add_argument("--mode", choices=["fast", "audit", "rebuild", "tamper"], default="audit")
    ap.add_argument("--pretty", action="store_true")
    ap.add_argument(
        "--regenerate",
        action="store_true",
        help="Rebuild d20.json and refresh certificate/manifest hashes before verification.",
    )
    ap.add_argument(
        "--no-regenerate",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    args = ap.parse_args()
    should_regenerate = (args.mode == "rebuild" or args.regenerate) and not args.no_regenerate
    regen_info = maybe_regenerate(args.mode, args.pretty, should_regenerate)
    out = run(args.mode)
    out["regeneration"] = regen_info
    if out["status"] != "PASS":
        print(json.dumps(out, indent=2 if args.pretty else None, sort_keys=True))
        sys.exit(1)
    print(json.dumps(out, indent=2 if args.pretty else None, sort_keys=True))


if __name__ == "__main__":
    main()
