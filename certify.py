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
    tensor_chain = data.get("tensor_chain", {})
    require(tensor_chain.get("status") == "TENSOR_CHAIN_EVIDENCE_CERTIFIED", "tensor_chain status mismatch", errors)
    require(tensor_chain.get("present") is True, "tensor_chain evidence missing", errors)
    require(tensor_chain.get("public_name") == "tensor_chain", "tensor_chain public name mismatch", errors)
    require(tensor_chain.get("path") == "data/tensor_chain", "tensor_chain path mismatch", errors)
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


def run(mode: str) -> dict[str, Any]:
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
    ap.add_argument("--mode", choices=["fast", "audit", "rebuild"], default="audit")
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
