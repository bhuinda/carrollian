#!/usr/bin/env python3
from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap
import argparse, hashlib, json, re, sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.runtime import ensure_numpy_runtime

ensure_numpy_runtime(ROOT, __file__)

from src.certify_io import raw_tensor_relpath
from src.token_burn_guard import emit_json
from src.certificate_registry import CERTIFICATE_INDEX, certificate_relpath, load_certificate_registry
from src.invariant_report_inventory import invariant_report_inventory, invariant_report_rows
from src.paths import ROOT
from src.verify_c2_selector_lookup_witness_source_package import (
    PACKAGE_CERTIFICATE as HALLOWEEN_LOOKUP_SOURCE_PACKAGE_CERTIFICATE,
    PACKAGE_VERIFIED_STATUS as HALLOWEEN_LOOKUP_SOURCE_PACKAGE_VERIFIED_STATUS,
)

MUTABLE = {"certificate.json", "manifests/file_hashes.json", "manifests/canonical.json"}
SCHEMA_LINEAGE_SUFFIX_RE = re.compile(r"\.(?:v\d+|source_drop)(?=$|[._-])")

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
    "15_intrinsic_support_dependency_geometry": "INTRINSIC_SUPPORT_DEPENDENCY_GEOMETRY_CERTIFIED",
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
JACOBIAN_SAT_CACHE_MANIFEST = (
    "data/evidence/jacobian_cubic_symbolic_elimination/saturation_cache/manifest.json"
)
JACOBIAN_SAT_CACHE_INDEX_MANIFEST = (
    "manifests/jacobian_cubic_symbolic_elimination_saturation_cache_manifest.json"
)


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def repo_relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def schema_name(value: Any) -> Any:
    if isinstance(value, str):
        return SCHEMA_LINEAGE_SUFFIX_RE.sub("", value)
    return value


def require_schema(value: Any, expected: str, msg: str, errors: list[str]) -> None:
    require(schema_name(value) == expected, msg, errors)


def reject_json_constant(token: str) -> None:
    raise ValueError(f"invalid JSON constant: {token}")


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
        return json.load(f, parse_constant=reject_json_constant)


def require(cond: bool, msg: str, errors: list[str]) -> None:
    if not cond:
        errors.append(msg)


def certified_evidence_base_sha256(payload: dict[str, Any]) -> str:
    base = json.loads(json.dumps(payload))
    pole_packet = (
        base.get("black_hole_certified_simulator", {})
        .get("pole_packet", {})
    )
    if isinstance(pole_packet, dict):
        pole_packet.pop("conditioning_certificate", None)
    return sha_json(base)


EVIDENCE_INVARIANTS_REL = "data/invariants/d20/certified_evidence_invariants.json"
DATA_REGISTRY_REL = "data/index.json"
EXPECTED_DATA_DOMAINS = {
    "a236_compute_cache",
    "compiler_a42_d20_replay_evidence",
    "coorient_lift",
    "core_certificates",
    "d20_invariants",
    "dihedral_formulae",
    "drinfeld_certificates",
    "geometry_certificates",
    "height_coherence_integrity",
    "hcycle_game_control",
    "integrity_certificates",
    "integrity_ladders",
    "jacobian_cubic_symbolic_elimination_evidence",
    "modular_certificates",
    "quotient_selectors",
    "raw_core_seeds",
    "reproducibility_evidence",
    "selector_certificates",
    "ss_sat_evidence",
    "stack_series_evidence",
    "talagrand_python_handoff_evidence",
    "tensor_chain_evidence",
    "tube_certificates",
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
    "canonical_source_handoff_archive",
    "contract_locked_certificates_pending",
    "mixed_canonical_archive",
}


def require_sha256(value: Any, expected: str, label: str, errors: list[str]) -> None:
    require(value == expected, f"{label} sha256 mismatch", errors)


def verify_source_registry(data_registry: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    section = data_registry.get("source_registry", {})
    require(isinstance(section, dict), "source registry block missing", errors)
    if not isinstance(section, dict):
        return {"package_count": 0}

    require_schema(section.get("schema"), "d20.source_registry", "source registry schema mismatch", errors)
    require(section.get("status") == "D20_SOURCE_REGISTRY_BUILT", "source registry status mismatch", errors)
    require(section.get("package_count") == 1, "source registry package count mismatch", errors)
    registry_checks = section.get("checks", {})
    require(isinstance(registry_checks, dict), "source registry checks missing", errors)
    if isinstance(registry_checks, dict):
        require(
            registry_checks.get("halloween_lookup_source_package_registered") is True,
            "Halloween lookup source package is not registered",
            errors,
        )

    packages = section.get("packages", {})
    require(isinstance(packages, dict), "source registry packages block missing", errors)
    if not isinstance(packages, dict):
        return {"package_count": 0}

    package_id = "halloween_c2_selector_lookup_witness_source_package"
    package = packages.get(package_id, {})
    require(isinstance(package, dict), "Halloween lookup source package registry entry missing", errors)
    if not isinstance(package, dict):
        return {"package_count": len(packages)}

    certificate_path = HALLOWEEN_LOOKUP_SOURCE_PACKAGE_CERTIFICATE
    certificate_rel = certificate_path.relative_to(ROOT).as_posix()
    require_schema(
        package.get("schema"),
        "d20.source_registry.package",
        "Halloween source package registry schema mismatch",
        errors,
    )
    require(package.get("registry_id") == package_id, "Halloween source package registry id mismatch", errors)
    require(package.get("present") is True, "Halloween source package not marked present", errors)
    require(
        package.get("status") == "D20_SOURCE_PACKAGE_REGISTERED",
        "Halloween source package registry status mismatch",
        errors,
    )
    require(
        package.get("role") == "selected_witness_source_for_c2_selector_lookup",
        "Halloween source package registry role mismatch",
        errors,
    )
    require(package.get("package_name") == package_id, "Halloween source package name mismatch", errors)

    certificate_entry = package.get("certificate", {})
    require(isinstance(certificate_entry, dict), "Halloween source package certificate entry missing", errors)
    require(certificate_path.exists(), "Halloween source package certificate file missing", errors)
    certificate_payload: dict[str, Any] = {}
    certificate_payload_sha256: str | None = None
    if certificate_path.exists():
        require(
            isinstance(certificate_entry, dict)
            and certificate_entry.get("path") == certificate_rel,
            "Halloween source package certificate path mismatch",
            errors,
        )
        if isinstance(certificate_entry, dict):
            require(
                certificate_entry.get("file_sha256") == sha_file(certificate_path),
                "Halloween source package certificate file hash mismatch",
                errors,
            )
        loaded = load_json(certificate_path)
        if isinstance(loaded, dict):
            certificate_payload = loaded
            certificate_payload_sha256 = sha_json(
                {
                    key: value
                    for key, value in certificate_payload.items()
                    if key != "certificate_sha256"
                }
            )
            require(
                certificate_payload.get("certificate_sha256") == certificate_payload_sha256,
                "Halloween source package embedded certificate hash mismatch",
                errors,
            )

    if isinstance(certificate_entry, dict):
        require(
            certificate_entry.get("payload_sha256") == certificate_payload_sha256,
            "Halloween source package registry payload hash mismatch",
            errors,
        )
        require(
            certificate_entry.get("embedded_certificate_sha256")
            == certificate_payload.get("certificate_sha256"),
            "Halloween source package registry embedded hash mismatch",
            errors,
        )
        require(
            certificate_entry.get("status") == HALLOWEEN_LOOKUP_SOURCE_PACKAGE_VERIFIED_STATUS,
            "Halloween source package certificate status mismatch",
            errors,
        )
        require(
            certificate_entry.get("package_checks_pass") is True,
            "Halloween source package registry does not record passing package checks",
            errors,
        )

    package_checks = package.get("checks", {})
    require(isinstance(package_checks, dict), "Halloween source package registry checks missing", errors)
    if isinstance(package_checks, dict):
        for check_name in [
            "certificate_status_is_verified",
            "certificate_file_exists",
            "certificate_hash_matches_payload",
            "certificate_reports_all_package_checks_pass",
            "package_uses_only_halloween_source_and_lookup_artifacts",
            "selector_counts_are_543_63_480",
            "halloween_source_split_is_543_63_480",
            "source_key_is_halloween_orbits_csv",
            "artifact_keys_are_lookup_tables_and_manifest",
            "source_registry_binding_checks_pass",
        ]:
            require(package_checks.get(check_name) is True, f"Halloween source package check failed: {check_name}", errors)

    registry_binding = package.get("source_registry_binding", {})
    require(isinstance(registry_binding, dict), "Halloween source package registry binding missing", errors)
    if isinstance(registry_binding, dict):
        require_schema(
            registry_binding.get("schema"),
            "d20.source_registry.binding",
            "Halloween source package registry binding schema mismatch",
            errors,
        )
        require(registry_binding.get("registry_id") == package_id, "Halloween source package registry binding id mismatch", errors)
        require(registry_binding.get("package_name") == package_id, "Halloween source package registry binding package mismatch", errors)
        require(registry_binding.get("all_checks_pass") is True, "Halloween source package registry binding checks failed", errors)
        binding_checks = registry_binding.get("checks", {})
        require(isinstance(binding_checks, dict), "Halloween source package registry binding checks missing", errors)
        if isinstance(binding_checks, dict):
            for check_name in [
                "registry_id_matches_package_name",
                "manifest_registry_id_matches_package_name",
                "certificate_status_is_verified",
                "certificate_reports_all_package_checks_pass",
                "certificate_hash_matches_payload",
                "package_uses_only_halloween_source_and_lookup_artifacts",
            ]:
                require(
                    binding_checks.get(check_name) is True,
                    f"Halloween source package registry binding check failed: {check_name}",
                    errors,
                )

    source = package.get("source", {})
    artifacts = package.get("artifacts", {})
    require(
        isinstance(source, dict)
        and sorted(source.keys()) == ["halloween_actual_c2_kernel_orbits_csv"],
        "Halloween source package source key mismatch",
        errors,
    )
    require(
        isinstance(artifacts, dict)
        and sorted(artifacts.keys())
        == [
            "manifest",
            "selector_lookup_witness_table_csv",
            "selector_lookup_witness_table_json",
        ],
        "Halloween source package artifact key mismatch",
        errors,
    )
    if isinstance(source, dict):
        halloween_source = source.get("halloween_actual_c2_kernel_orbits_csv", {})
        if isinstance(halloween_source, dict):
            source_path = ROOT / str(halloween_source.get("path", ""))
            require(source_path.exists(), "Halloween source CSV missing", errors)
            if source_path.exists():
                require(halloween_source.get("sha256") == sha_file(source_path), "Halloween source CSV hash mismatch", errors)
            require(halloween_source.get("row_count") == 543, "Halloween source row count mismatch", errors)
            require(halloween_source.get("fixed63_orbit_count") == 63, "Halloween fixed orbit count mismatch", errors)
            require(
                halloween_source.get("paired480_two_cycle_orbit_count") == 480,
                "Halloween paired orbit count mismatch",
                errors,
            )

    if isinstance(artifacts, dict):
        for artifact_id, artifact_entry in artifacts.items():
            require(isinstance(artifact_entry, dict), f"Halloween artifact {artifact_id} entry malformed", errors)
            if not isinstance(artifact_entry, dict):
                continue
            artifact_path = ROOT / str(artifact_entry.get("path", ""))
            require(artifact_path.exists(), f"Halloween artifact {artifact_id} missing", errors)
            if artifact_path.exists():
                require(
                    artifact_entry.get("sha256") == sha_file(artifact_path),
                    f"Halloween artifact {artifact_id} hash mismatch",
                    errors,
                )

    derived = package.get("derived", {})
    require(isinstance(derived, dict), "Halloween source package derived block missing", errors)
    if isinstance(derived, dict):
        require(derived.get("row_count") == 1086, "Halloween source package lookup row count mismatch", errors)
        require(derived.get("selector_count") == 3, "Halloween source package selector count mismatch", errors)
        require(
            derived.get("selector_counts") == {"lazy63": 63, "paired_lazy480": 480, "raw543": 543},
            "Halloween source package selector counts mismatch",
            errors,
        )
        require(
            derived.get("halloween_orbit_split")
            == {
                "fixed63_orbit_count": 63,
                "paired480_two_cycle_orbit_count": 480,
                "raw543_orbit_count": 543,
            },
            "Halloween source package orbit split mismatch",
            errors,
        )

    return {"package_count": len(packages)}


def verify_data_registry(data: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    section = data.get("data_registry", {})
    require(section.get("present") is True, "data registry missing from d20.json", errors)
    require(section.get("path") == DATA_REGISTRY_REL, "data registry path mismatch", errors)
    path = ROOT / DATA_REGISTRY_REL
    require(path.exists(), "missing data registry file", errors)
    if path.exists():
        require(section.get("file_sha256") == sha_file(path), "data registry file hash mismatch", errors)
    require_schema(section.get("schema"), "d20.data_registry", "data registry schema mismatch", errors)
    require(section.get("status") == "DATA_REGISTRY_BUILT", "data registry status mismatch", errors)

    policy = section.get("policy", {})
    require(policy.get("physical_layout") == "domain_grouped_files", "data registry physical layout mismatch", errors)
    require(
        policy.get("migration_stage") == "canonical_evidence_and_invariants_integrated_after_bulk_move",
        "data registry migration stage mismatch",
        errors,
    )
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
                    exists = (base / name).exists()
                    if not exists and domain_id == "raw_core_seeds" and name in {
                        "Halloween.npz",
                        "T_985.npz",
                        "tensor_sparse.npz",
                    }:
                        resolved = ROOT / raw_tensor_relpath()
                        exists = resolved.exists() and resolved.parent == base
                    require(exists, f"{domain_id}: missing required data file {name}", errors)

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
    ss_sat = domains.get("ss_sat_evidence", {})
    require(ss_sat.get("path") == "data/evidence/ss_sat", "SS-SAT canonical path mismatch", errors)
    require(ss_sat.get("storage_status") == "canonical_standardized_layout", "SS-SAT storage status should mark standardized layout", errors)
    require(ss_sat.get("target_path") == "data/evidence/ss_sat", "SS-SAT target layout mismatch", errors)
    stack_series = domains.get("stack_series_evidence", {})
    require(stack_series.get("path") == "data/evidence/stack_series", "stack-series canonical path mismatch", errors)
    require(
        stack_series.get("storage_status") == "canonical_standardized_layout",
        "stack-series storage status should mark standardized layout",
        errors,
    )
    require(stack_series.get("target_path") == "data/evidence/stack_series", "stack-series target layout mismatch", errors)
    height = domains.get("height_coherence_integrity", {})
    require(height.get("path") == "data/integrity/height_coherence", "height-coherence canonical path mismatch", errors)
    require(
        height.get("storage_status") == "canonical_standardized_layout",
        "height-coherence storage status should mark standardized layout",
        errors,
    )
    require(height.get("target_path") == "data/integrity/height_coherence", "height-coherence target layout mismatch", errors)
    repro = domains.get("reproducibility_evidence", {})
    require(repro.get("path") == "data/evidence/reproducibility", "reproducibility canonical path mismatch", errors)
    require(
        repro.get("storage_status") == "canonical_standardized_layout",
        "reproducibility storage status should mark standardized layout",
        errors,
    )
    require(repro.get("target_path") == "data/evidence/reproducibility", "reproducibility target layout mismatch", errors)
    d20 = domains.get("d20_invariants", {})
    require(d20.get("path") == "data/invariants/d20", "d20 invariant canonical path mismatch", errors)
    require(d20.get("target_path") == "data/invariants/d20", "d20 invariant target layout mismatch", errors)
    require(d20.get("storage_status") == "canonical_standardized_layout", "d20 invariant storage status should mark standardized layout", errors)
    hcycle = domains.get("hcycle_game_control", {})
    require(hcycle.get("path") == "data/invariants/hcycle", "H-cycle canonical path mismatch", errors)
    require(hcycle.get("target_path") == "data/invariants/hcycle", "H-cycle target layout mismatch", errors)
    require(hcycle.get("storage_status") == "canonical_current_layout_flat", "H-cycle storage status should preserve flat layout", errors)
    ladders = domains.get("integrity_ladders", {})
    require(ladders.get("path") == "data/invariants/integrity", "integrity ladder canonical path mismatch", errors)
    require(ladders.get("target_path") == "data/invariants/integrity", "integrity ladder target layout mismatch", errors)
    require(ladders.get("storage_status") == "canonical_standardized_layout", "integrity ladder storage status should mark standardized layout", errors)

    source_registry_result = verify_source_registry(section, errors)

    return {
        "domain_count": len(domains),
        "source_package_count": source_registry_result.get("package_count"),
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
    require_schema(section.get("schema"), "d20.certified_evidence_invariants", "certified evidence invariants schema mismatch", errors)
    require(
        section.get("status") == "D20_CERTIFIED_EVIDENCE_INVARIANTS_INTEGRATED",
        "certified evidence invariants status mismatch",
        errors,
    )
    source_reservation = {
        "status",
        "schema",
        "source_count",
        "integration_policy",
        "witness_hashes",
        "file_sha256",
        "path",
        "present",
    }
    source_blocks = [
        k
        for k, value in section.items()
        if k not in source_reservation and isinstance(value, dict)
    ]
    require(
        section.get("source_count") == len(source_blocks),
        f"certified evidence invariant source count mismatch: {section.get('source_count')} != {len(source_blocks)}",
        errors,
    )

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
    require_schema(fab.get("schema"), "d20.fab.classical_typing", "f(a)(b) classical typing schema mismatch", errors)
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
    checks = bh.get("checks", {})
    require(isinstance(checks, dict) and bool(checks), "black-hole simulator checks missing", errors)
    for key, value in checks.items():
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
    conditioning = bh.get("pole_packet", {}).get("conditioning_certificate", {})
    conditioning_path = conditioning.get("path")
    expected_conditioning_path = "data/invariants/d20/theorems/black_hole_inverse_conditioning/report.json"
    require(conditioning_path == expected_conditioning_path, "black-hole conditioning certificate path mismatch", errors)
    conditioning_report: dict[str, Any] = {}
    if isinstance(conditioning_path, str):
        report_path = ROOT / conditioning_path
        require(report_path.exists(), "black-hole conditioning report missing", errors)
        if report_path.exists():
            require(conditioning.get("sha256") == sha_file(report_path), "black-hole conditioning report hash mismatch", errors)
            conditioning_report = load_json(report_path)
    require_schema(conditioning_report.get("schema"), "d20.black_hole.inverse_conditioning", "black-hole conditioning schema mismatch", errors)
    require(
        conditioning_report.get("status") == "D20_BLACK_HOLE_INVERSE_CONDITIONING_CERTIFIED",
        "black-hole conditioning status mismatch",
        errors,
    )
    require(conditioning_report.get("all_checks_pass") is True, "black-hole conditioning checks did not pass", errors)
    conditioning_checks = conditioning_report.get("checks", {})
    require(isinstance(conditioning_checks, dict) and bool(conditioning_checks), "black-hole conditioning checks missing", errors)
    for key, value in conditioning_checks.items():
        require(value is True, f"black-hole conditioning check failed: {key}", errors)
    source_payload = load_json(EVIDENCE_INVARIANTS_REL)
    source_base_hash = certified_evidence_base_sha256(source_payload)
    input_witness = conditioning_report.get("input_witness", {})
    require(
        input_witness.get("base_payload_sha256_without_conditioning_certificate") == source_base_hash,
        "black-hole conditioning base witness hash mismatch",
        errors,
    )
    require(conditioning.get("sample_count", 0) >= 300, "black-hole conditioning sample count too small", errors)
    require(conditioning.get("interior_max_abs_state_error", 1.0) < 1e-12, "black-hole conditioning interior precision mismatch", errors)
    require(conditioning.get("near_extremal_max_abs_state_error", 1.0) < 1e-7, "black-hole conditioning near-boundary precision mismatch", errors)
    require(
        conditioning.get("near_over_interior_forward_condition_ratio", 0.0) > 1000.0,
        "black-hole conditioning near-boundary condition ratio missing",
        errors,
    )
    require(
        conditioning.get("noise_projection_residual_over_noise_max", 0.0) > 0.01,
        "black-hole conditioning projection residual signal missing",
        errors,
    )
    sim = bh.get("simulation_summary", {})
    require(sim.get("visited_states") == 20, "black-hole simulator visited state count mismatch", errors)
    require(sim.get("integrity_projection_count") == 0, "black-hole simulator integrity projection count mismatch", errors)

    return {
        "source_count": section.get("source_count"),
        "path": section.get("path"),
    }


def verify_root(errors: list[str]) -> dict[str, Any]:
    cert = load_json("certificate.json")
    require_schema(cert.get("schema"), "d20.verifier", "root schema mismatch", errors)
    require(cert.get("status") == "D20_CERTIFIED", "root status mismatch", errors)
    h = cert.get("d20_sha256")
    body = {k: v for k, v in cert.items() if k != "d20_sha256"}
    require(isinstance(h, str) and len(h) == 64 and h == sha_json(body), "root self-hash mismatch", errors)
    return cert


def verify_root_certificates(root: dict[str, Any], registry: dict[str, Any], errors: list[str]) -> None:
    root_certificates = root.get("certificates", [])
    registry_certificates = registry.get("certificates", [])
    require(isinstance(root_certificates, list), "root certificates list missing", errors)
    require(isinstance(registry_certificates, list), "registry certificates list missing", errors)
    if not isinstance(root_certificates, list) or not isinstance(registry_certificates, list):
        return

    by_id = {entry.get("id"): entry for entry in root_certificates if isinstance(entry, dict)}
    require(len(root_certificates) == len(registry_certificates), "root certificate count does not match registry", errors)
    for entry in registry_certificates:
        if not isinstance(entry, dict):
            continue
        certificate_id = entry.get("id")
        rel = entry.get("path")
        root_entry = by_id.get(certificate_id)
        require(isinstance(root_entry, dict), f"root certificate missing id: {certificate_id}", errors)
        if not isinstance(root_entry, dict) or not isinstance(rel, str):
            continue
        p = ROOT / rel
        require(root_entry.get("certificate") == rel, f"root certificate path mismatch for {certificate_id}", errors)
        require(root_entry.get("ordinal_dir") == entry.get("ordinal_dir"), f"root ordinal_dir mismatch for {certificate_id}", errors)
        require(root_entry.get("group") == entry.get("group"), f"root group mismatch for {certificate_id}", errors)
        require(root_entry.get("status") == entry.get("expected_status"), f"root status mismatch for {certificate_id}", errors)
        if p.exists():
            require(root_entry.get("certificate_file_sha256") == sha_file(p), f"root certificate hash mismatch for {certificate_id}", errors)


def verify_root_invariant_reports(root: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    rows = invariant_report_rows()
    certified = [row for row in rows if row.get("classification") == "certified"]
    provisional = [row for row in rows if row.get("classification") == "provisional"]
    demoted = [row for row in rows if row.get("classification") == "demoted"]
    sort_key = lambda row: (str(row.get("kind", "")), str(row.get("path", "")), str(row.get("id", "")))
    certified = sorted(certified, key=sort_key)
    provisional = sorted(provisional, key=sort_key)
    demoted = sorted(demoted, key=sort_key)
    inventory = invariant_report_inventory()

    recorded_inventory = root.get("invariant_report_inventory", {})
    require(isinstance(recorded_inventory, dict), "root invariant report inventory missing", errors)
    if isinstance(recorded_inventory, dict):
        for key in (
            "schema",
            "status",
            "report_count",
            "certified_report_count",
            "provisional_report_count",
            "demoted_report_count",
        ):
            require(
                recorded_inventory.get(key) == inventory.get(key),
                f"root invariant report inventory mismatch for {key}",
                errors,
            )

    recorded_certified = root.get("certified_invariant_reports", [])
    recorded_provisional = root.get("provisional_invariant_reports", [])
    recorded_demoted = root.get("demoted_invariant_reports", [])
    require(isinstance(recorded_certified, list), "root certified invariant reports list missing", errors)
    require(isinstance(recorded_provisional, list), "root provisional invariant reports list missing", errors)
    require(isinstance(recorded_demoted, list), "root demoted invariant reports list missing", errors)
    require(
        root.get("certified_invariant_report_count") == len(certified),
        "root certified invariant report count mismatch",
        errors,
    )
    require(
        root.get("provisional_invariant_report_count") == len(provisional),
        "root provisional invariant report count mismatch",
        errors,
    )
    require(
        root.get("demoted_invariant_report_count") == len(demoted),
        "root demoted invariant report count mismatch",
        errors,
    )

    if isinstance(recorded_certified, list):
        recorded_certified = sorted(recorded_certified, key=sort_key)
        require(recorded_certified == certified, "root certified invariant reports do not match filesystem scan", errors)
    if isinstance(recorded_provisional, list):
        recorded_provisional = sorted(recorded_provisional, key=sort_key)
        require(recorded_provisional == provisional, "root provisional invariant reports do not match filesystem scan", errors)
    if isinstance(recorded_demoted, list):
        recorded_demoted = sorted(recorded_demoted, key=sort_key)
        require(recorded_demoted == demoted, "root demoted invariant reports do not match filesystem scan", errors)

    return {
        "report_count": len(rows),
        "certified_report_count": len(certified),
        "provisional_report_count": len(provisional),
        "demoted_report_count": len(demoted),
    }


def verify_genome(data: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    genome = data.get("genome", {})
    require(isinstance(genome, dict), "d20 genome missing", errors)
    if not isinstance(genome, dict):
        return {"present": False}

    require_schema(genome.get("schema"), "d20.genome", "d20 genome schema mismatch", errors)
    require(genome.get("status") == "D20_GENOME_CANONICAL", "d20 genome status mismatch", errors)
    require(genome.get("object") == "d20", "d20 genome object mismatch", errors)
    require(genome.get("entrypoint") == "src.derive_d20:derive", "d20 genome entrypoint mismatch", errors)
    require(genome.get("fixed_point", {}).get("object_hash_key") == "d20_sha256", "d20 genome fixed-point hash key mismatch", errors)

    genome_hash = genome.get("genome_sha256")
    genome_body = {k: v for k, v in genome.items() if k != "genome_sha256"}
    require(
        isinstance(genome_hash, str) and len(genome_hash) == 64 and genome_hash == sha_json(genome_body),
        "d20 genome self-hash mismatch",
        errors,
    )

    source_genes = genome.get("source_genes", [])
    require(isinstance(source_genes, list) and bool(source_genes), "d20 genome source genes missing", errors)
    if isinstance(source_genes, list):
        for gene in source_genes:
            require(isinstance(gene, dict), "d20 genome source gene is not an object", errors)
            if not isinstance(gene, dict):
                continue
            rel = gene.get("path")
            require(isinstance(rel, str), "d20 genome source gene path missing", errors)
            if not isinstance(rel, str):
                continue
            path = ROOT / rel
            require(path.exists(), f"d20 genome source gene missing: {rel}", errors)
            if path.exists():
                require(gene.get("sha256") == sha_file(path), f"d20 genome source gene hash mismatch: {rel}", errors)

    try:
        from src.derive_d20 import derive

        regenerated = derive()
    except Exception as exc:
        errors.append(f"d20 genome fixed-point exception: {type(exc).__name__}: {exc}")
        return {
            "present": True,
            "status": genome.get("status"),
            "source_gene_count": len(source_genes) if isinstance(source_genes, list) else 0,
        }

    regenerated_hash = regenerated.get("d20_sha256")
    require(regenerated_hash == data.get("d20_sha256"), "d20 genome fixed-point hash mismatch", errors)
    regenerated_body = {k: v for k, v in regenerated.items() if k != "d20_sha256"}
    require(sha_json(regenerated_body) == regenerated_hash, "d20 genome regenerated self-hash mismatch", errors)
    return {
        "present": True,
        "status": genome.get("status"),
        "genome_sha256": genome_hash,
        "source_gene_count": len(source_genes) if isinstance(source_genes, list) else 0,
        "fixed_point_hash": regenerated_hash,
        "fixed_point_verified": regenerated_hash == data.get("d20_sha256"),
    }


def verify_d20_json(errors: list[str]) -> dict[str, Any]:
    p = ROOT / "d20.json"
    require(p.exists(), "missing d20.json", errors)
    if not p.exists():
        return {}
    data = load_json(p)
    require_schema(data.get("schema"), "d20.object", "d20.json schema mismatch", errors)
    require(data.get("status") == "D20_CERTIFIED", "d20.json status mismatch", errors)
    require(data.get("object") == "d20", "d20.json object mismatch", errors)
    h = data.get("d20_sha256")
    body = {k: v for k, v in data.items() if k != "d20_sha256"}
    require(isinstance(h, str) and len(h) == 64 and h == sha_json(body), "d20.json self-hash mismatch", errors)
    genome = verify_genome(data, errors)
    required_sections = [
        "genome",
        "core_invariants",
        "optics",
        "game_theory",
        "zero_axiom_coorient",
        "universal_integral_uniqueness",
        "pre_A985_relation_body_theorem",
        "coorient_relator_profile_from_a0_a5",
        "data_registry",
        "certified_evidence_invariants",
        "tensor_chain",
        "ss_sat_evidence",
        "stack_series_evidence",
        "height_coherence",
        "reproducibility_evidence",
        "certificate_registry",
        "certificates",
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
    marker_derivation = marker.get("derivation", {})
    selected = marker_derivation.get("selected_generators", {})
    expected_marker_ints = len(selected.get("generator_indices", [])) * len(selected.get("base_points", []))
    require(expected_marker_ints > 0, "coorient generator marker expected integer count is zero", errors)
    require(marker.get("integer_count") == expected_marker_ints, "coorient generator marker integer count mismatch", errors)
    require(marker_derivation.get("uses_supplied_relation_partition") is False, "coorient marker still uses supplied relation partition", errors)
    require(marker_derivation.get("uses_pre_a985_generated_relation_body") is True, "coorient marker is not using pre-A985 relation body", errors)
    u = data.get("universal_integral_uniqueness", {})
    require(u.get("status") == "UNIVERSAL_A985_INTEGRAL_UNIQUENESS_PASS", "universal integral uniqueness status mismatch", errors)
    uc = u.get("coorient_lift_uniqueness_computation", {})
    require(uc.get("internal_base_type_candidate_triples") == 18432, "universal integral internal candidate count mismatch", errors)
    require(uc.get("coherent_signature_lift_triples") == 9216, "universal integral lift count mismatch", errors)
    require(uc.get("generated_action_order") == 9216, "universal integral generated action order mismatch", errors)
    ur = u.get("uniqueness_result", {})
    require(ur.get("A985_integral_uniqueness_computed") is True, "A985 integral uniqueness not computed", errors)
    require(ur.get("coorient_action_group_unique") is True, "coorient action group uniqueness mismatch", errors)
    require(
        ur.get("remaining_generator_coordinates_are_semantic_seed") is False,
        "generator coordinates still marked as semantic seed",
        errors,
    )
    pre = data.get("pre_A985_relation_body_theorem", {})
    require(pre.get("status") == "PRE_A985_RELATION_BODY_DERIVED_WITHOUT_RELATION_TABLE_PASS", "pre-A985 relation body theorem status mismatch", errors)
    pr = pre.get("result", {})
    require(pr.get("uses_relation_table_as_input") is False, "pre-A985 theorem uses relation table as input", errors)
    require(pr.get("A985_relation_count") == 985, "pre-A985 relation count mismatch", errors)
    require(pr.get("ordered_pair_partition_size") == 2576 * 2576, "pre-A985 relation partition size mismatch", errors)
    if pr.get("generated_tensor_witness_present") is True:
        require(pr.get("T985_support") == 1414965, "pre-A985 tensor support mismatch", errors)
    relator = data.get("coorient_relator_profile_from_a0_a5", {})
    require(
        relator.get("status") == "COORIENT_RELATOR_PROFILE_FROM_A0_A5_PASS",
        "coorient A0-A5 relator profile status mismatch",
        errors,
    )
    rel_checks = relator.get("checks", {})
    require(rel_checks.get("uses_word_presentation_certificate") is False, "coorient relator profile still reads word certificate", errors)
    require(rel_checks.get("reduced_basis_closes_full_group") is True, "coorient relator profile basis does not close full group", errors)
    require(rel_checks.get("derived_generator_count_is_positive") is True, "coorient relator profile generator count mismatch", errors)
    data_registry = verify_data_registry(data, errors)
    evidence_invariants = verify_certified_evidence_invariants(data, errors)
    tensor_chain = data.get("tensor_chain", {})
    require(tensor_chain.get("status") == "TENSOR_CHAIN_EVIDENCE_CERTIFIED", "tensor_chain status mismatch", errors)
    require(tensor_chain.get("present") is True, "tensor_chain evidence missing", errors)
    require(tensor_chain.get("path") == "data/evidence/tensor_chain", "tensor_chain path mismatch", errors)
    plain_name_view = tensor_chain.get("plain_name_view", {})
    require(plain_name_view.get("present") is True, "tensor_chain plain-name view missing", errors)
    require(plain_name_view.get("status") == "TENSOR_CHAIN_PLAIN_NAME_VIEW_GENERATED", "tensor_chain plain-name view status mismatch", errors)
    plain_name_summary = plain_name_view.get("summary", {})
    require(plain_name_summary.get("source_file_count", 0) > 0, "tensor_chain plain-name view has no files", errors)
    require(plain_name_summary.get("changed_file_alias_count", 0) > 0, "tensor_chain plain-name view has no renamed file aliases", errors)
    require(
        plain_name_summary.get("remaining_blocked_plain_token_count") == 0,
        "tensor_chain plain-name view still contains blocked glossary tokens",
        errors,
    )
    ss_sat = data.get("ss_sat_evidence", {})
    require(ss_sat.get("status") == "SS_SAT_EVIDENCE_CONSOLIDATED", "SS-SAT status mismatch", errors)
    require(ss_sat.get("present") is True, "SS-SAT evidence missing", errors)
    require(ss_sat.get("path") == "data/evidence/ss_sat", "SS-SAT path mismatch", errors)
    ss_manifest = ss_sat.get("manifest", {})
    require(ss_manifest.get("present") is True, "SS-SAT manifest missing", errors)
    require_schema(ss_manifest.get("schema"), "d20.ss_sat.manifest", "SS-SAT manifest schema mismatch", errors)
    require(ss_manifest.get("status") == "SS_SAT_MANIFEST_REFRESHED", "SS-SAT manifest status mismatch", errors)
    require(ss_manifest.get("file_count", 0) > 0, "SS-SAT manifest has no files", errors)
    ss_report = ss_sat.get("summary_report", {})
    require(ss_report.get("present") is True, "SS-SAT summary report missing", errors)
    require(ss_report.get("status") == "SS_SAT_EXTERNAL_SOLVER_EVIDENCE_CONSOLIDATED", "SS-SAT summary report status mismatch", errors)
    solver_runs = ss_sat.get("solver_runs", {})
    require(solver_runs.get("total") == 15, "SS-SAT solver run count mismatch", errors)
    require(solver_runs.get("cadical_unsat") == 5, "SS-SAT CaDiCaL UNSAT count mismatch", errors)
    require(solver_runs.get("minisat_unsat") == 5, "SS-SAT MiniSat UNSAT count mismatch", errors)
    require(solver_runs.get("kissat_unsat") == 3, "SS-SAT Kissat UNSAT count mismatch", errors)
    require(solver_runs.get("kissat_sigsegv") == 2, "SS-SAT Kissat SIGSEGV residue count mismatch", errors)
    proof_verification = ss_sat.get("proof_verification", {})
    require(proof_verification.get("cadical_drat_verified") == "5/5", "SS-SAT DRAT verification mismatch", errors)
    require(proof_verification.get("cadical_lrat_verified") == "5/5", "SS-SAT LRAT verification mismatch", errors)
    require(
        proof_verification.get("cadical_frat_embedded_lrat_verified") == "5/5",
        "SS-SAT FRAT embedded LRAT verification mismatch",
        errors,
    )
    require(
        proof_verification.get("standalone_frat_checker") == "BLOCKED_NO_STANDALONE_FRAT_CHECKER",
        "SS-SAT standalone FRAT checker residue mismatch",
        errors,
    )
    scaled_report = ss_sat.get("scaled_report", {})
    require(scaled_report.get("present") is True, "SS-SAT scaled report missing", errors)
    require(
        scaled_report.get("status") == "SS_SAT_SCALED_EVIDENCE_CAPTURED",
        "SS-SAT scaled report status mismatch",
        errors,
    )
    scaled_solver_runs = ss_sat.get("scaled_solver_runs", {})
    require(scaled_solver_runs.get("total") == 27, "SS-SAT scaled solver run count mismatch", errors)
    require(scaled_solver_runs.get("cadical_unsat") == 9, "SS-SAT scaled CaDiCaL UNSAT count mismatch", errors)
    require(scaled_solver_runs.get("minisat_unsat") == 9, "SS-SAT scaled MiniSat UNSAT count mismatch", errors)
    require(scaled_solver_runs.get("kissat_unsat") == 4, "SS-SAT scaled Kissat UNSAT count mismatch", errors)
    require(scaled_solver_runs.get("kissat_sigsegv") == 5, "SS-SAT scaled Kissat SIGSEGV residue count mismatch", errors)
    scaled_proofs = ss_sat.get("scaled_proof_verification", {})
    require(scaled_proofs.get("drat", {}).get("total") == 9, "SS-SAT scaled DRAT total mismatch", errors)
    require(scaled_proofs.get("drat", {}).get("verified") == 9, "SS-SAT scaled DRAT verification mismatch", errors)
    require(scaled_proofs.get("lrat", {}).get("total") == 9, "SS-SAT scaled LRAT total mismatch", errors)
    require(scaled_proofs.get("lrat", {}).get("verified") == 9, "SS-SAT scaled LRAT verification mismatch", errors)
    cvx_integrity = ss_sat.get("cvx_integrity", {})
    for family in ["cadical_drat", "cadical_lrat", "cadical_frat_surface"]:
        counts = cvx_integrity.get(family, {}).get("integrity_counts", {})
        require(counts.get("C", 0) > 0 and set(counts) == {"C"}, f"SS-SAT {family} integrity is not purely C", errors)
    residues = ss_sat.get("residues", [])
    require("residues/kissat_sigsegv.json" in residues, "SS-SAT Kissat residue missing", errors)
    require("residues/frat_checker_status.json" in residues, "SS-SAT FRAT checker residue missing", errors)
    require(
        "residues/full_frat_inherited_analyzer_blocked.json" in residues,
        "SS-SAT full-FRAT replay residue missing",
        errors,
    )
    stack_series = data.get("stack_series_evidence", {})
    require(stack_series.get("status") == "STACK_SERIES_EVIDENCE_INTEGRATED", "stack-series status mismatch", errors)
    require(stack_series.get("present") is True, "stack-series evidence missing", errors)
    require(stack_series.get("path") == "data/evidence/stack_series", "stack-series path mismatch", errors)
    stack_manifest = stack_series.get("manifest", {})
    require(stack_manifest.get("present") is True, "stack-series manifest missing", errors)
    require_schema(stack_manifest.get("schema"), "d20.stack_series_evidence_manifest", "stack-series manifest schema mismatch", errors)
    require(stack_manifest.get("status") == "STACK_SERIES_EVIDENCE_INTEGRATED", "stack-series manifest status mismatch", errors)
    stack_report = stack_series.get("summary_report", {})
    require(stack_report.get("present") is True, "stack-series summary report missing", errors)
    require(stack_report.get("status") == "STACK_SERIES_EVIDENCE_INTEGRATED", "stack-series summary report status mismatch", errors)
    require(stack_series.get("stage_count") == 4, "stack-series stage count mismatch", errors)
    stack_statuses = stack_series.get("stage_statuses", {})
    expected_stack_statuses = {
        "q_weighted": "D20_Q_WEIGHTED_STACK_SERIES_CERTIFIED_MOTIVIC_COHA_OPEN",
        "a985_weighted": "D20_A985_WEIGHTED_STACK_SERIES_CERTIFIED_RAW_TENSOR_SHADOW_MOTIVIC_COHA_OPEN",
        "relation_level": "D20_A985_RELATION_LEVEL_STACK_SERIES_CERTIFIED_RAW_TENSOR_MOTIVIC_COHA_OPEN",
        "relation_pair_quotient": "D20_A985_RELATION_PAIR_QUOTIENT_STACK_SERIES_CERTIFIED_MOTIVIC_COHA_OPEN",
    }
    require(stack_statuses == expected_stack_statuses, "stack-series stage status mismatch", errors)

    height = data.get("height_coherence", {})
    require(height.get("status") == "D20_UF_KERNEL_HEIGHT_COHERENCE_CERTIFIED", "height-coherence status mismatch", errors)
    require(height.get("present") is True, "height-coherence evidence missing", errors)
    require(height.get("path") == "data/integrity/height_coherence", "height-coherence path mismatch", errors)
    height_cert = height.get("certificate", {})
    require(height_cert.get("present") is True, "height-coherence certificate missing", errors)
    require_schema(height_cert.get("schema"), "d20.uf_kernel.height_coherence", "height-coherence certificate schema mismatch", errors)
    height_manifest = height.get("manifest", {})
    require(height_manifest.get("present") is True, "height-coherence manifest missing", errors)
    require_schema(height_manifest.get("schema"), "d20.height_coherence_evidence_manifest", "height-coherence manifest schema mismatch", errors)
    require(
        height_manifest.get("status") == "D20_UF_KERNEL_HEIGHT_COHERENCE_CERTIFIED",
        "height-coherence manifest status mismatch",
        errors,
    )
    require(height.get("positive_certificate_count") == 3, "height-coherence positive certificate count mismatch", errors)
    require(height.get("negative_control_count") == 1, "height-coherence negative control count mismatch", errors)
    guard = height.get("saturated_resizing_guard", {})
    require(guard.get("valid_saturated_bridge") is True, "height-coherence saturated bridge guard mismatch", errors)
    require(
        guard.get("pointwise_atom_projection_status") == "REJECTED_AS_TOO_STRONG",
        "height-coherence atom projection guard mismatch",
        errors,
    )

    repro = data.get("reproducibility_evidence", {})
    require(
        repro.get("status") == "D20_REPRODUCIBILITY_EVIDENCE_INTEGRATED",
        "reproducibility evidence status mismatch",
        errors,
    )
    require(repro.get("present") is True, "reproducibility evidence missing", errors)
    require(repro.get("path") == "data/evidence/reproducibility/python_bundle", "reproducibility path mismatch", errors)
    repro_manifest = repro.get("manifest", {})
    require(repro_manifest.get("present") is True, "reproducibility manifest missing", errors)
    require(
        schema_name(repro_manifest.get("schema")) == "d20.reproducibility_evidence_manifest",
        "reproducibility manifest schema mismatch",
        errors,
    )
    require(
        repro_manifest.get("status") == "D20_REPRODUCIBILITY_EVIDENCE_INTEGRATED",
        "reproducibility manifest status mismatch",
        errors,
    )
    require(repro.get("output_certificate_count") == 3, "reproducibility output certificate count mismatch", errors)
    repro_statuses = repro.get("output_certificate_statuses", {})
    require(set(repro_statuses.values()) == {"PASS"}, "reproducibility output certificate status mismatch", errors)
    require(repro.get("source_script_count", 0) > 0, "reproducibility source script count is zero", errors)
    fin = data.get("final_investigation", {})
    require(fin.get("status") == "D20_INVESTIGATION_FINALIZED_WITH_A985_INTEGRAL_UNIQUENESS", "final investigation status mismatch", errors)
    require(fin.get("finite_computational_closure") is True, "final investigation finite closure mismatch", errors)
    require(fin.get("A985_integral_uniqueness_computed") is True, "final investigation A985 uniqueness mismatch", errors)
    require(fin.get("coorient_action_group_unique_over_A985") is True, "final investigation coorient uniqueness mismatch", errors)
    require(fin.get("full_zero_axiom_constructor") is False, "final investigation zero-axiom boundary mismatch", errors)
    strict = fin.get("strict_scratch_constructor", fin.get("remaining_boundary", {}))
    require(strict.get("remaining_seed_integer_count_in_A985_integral_theory") == 0, "final investigation remaining A985-integral seed count mismatch", errors)
    if "strict_scratch_constructor" in fin:
        require(strict.get("entrypoint_promoted") is True, "final investigation strict-scratch promotion mismatch", errors)
    registry = data.get("certificate_registry", {})
    require_schema(registry.get("schema"), "d20.certificate_registry", "d20 certificate registry schema mismatch", errors)
    require(registry.get("status") == "CERTIFICATE_REGISTRY_BUILT", "d20 certificate registry status mismatch", errors)
    require(registry.get("path") == "data/certificates.json", "d20 certificate registry path mismatch", errors)
    require(len(registry.get("certificates", [])) == len(EXPECTED), "d20 certificate registry entry count mismatch", errors)
    if CERTIFICATE_INDEX.exists():
        require(registry.get("file_sha256") == sha_file(CERTIFICATE_INDEX), "d20 certificate registry file hash mismatch", errors)

    return {
        "schema": data.get("schema"),
        "status": data.get("status"),
        "file_sha256": sha_file(p),
        "object_sha256": h,
        "genome_sha256": genome.get("genome_sha256"),
        "genome_fixed_point_verified": genome.get("fixed_point_verified"),
        "genome_source_gene_count": genome.get("source_gene_count"),
        "size": p.stat().st_size,
        "section_count": len(data),
        "certificate_count": len(data.get("certificates", {})),
        "certificate_registry_entries": len(registry.get("certificates", [])),
        "json_invariant_file_count": len(data.get("json_invariants", {})),
        "npz_array_manifest_count": len(data.get("npz_array_manifests", {})),
        "data_registry_domain_count": data_registry.get("domain_count"),
        "source_registry_package_count": data_registry.get("source_package_count"),
        "certified_evidence_source_count": evidence_invariants.get("source_count"),
        "tensor_chain_present": bool(tensor_chain.get("present", False)),
        "ss_sat_evidence_present": bool(ss_sat.get("present", False)),
        "stack_series_evidence_present": bool(stack_series.get("present", False)),
        "height_coherence_present": bool(height.get("present", False)),
        "reproducibility_evidence_present": bool(repro.get("present", False)),
        "hcycle_present": bool(data.get("game_theory", {}).get("present", False)),
        "hcycle_primitive_cycles": data.get("game_theory", {}).get("primitive_H_cycles", {}).get("count"),
        "hcycle_state_space": data.get("game_theory", {}).get("state_space", {}).get("S20_order"),
    }


def verify_certificate_registry(errors: list[str]) -> tuple[dict[str, Any], dict[str, Any]]:
    require(CERTIFICATE_INDEX.exists(), "missing certificate registry: data/certificates.json", errors)
    if not CERTIFICATE_INDEX.exists():
        return {}, {"registry_entries": 0, "groups": []}

    data = load_certificate_registry()
    require_schema(data.get("schema"), "d20.certificate_registry", "certificate registry schema mismatch", errors)
    require(data.get("status") == "CERTIFICATE_REGISTRY_BUILT", "certificate registry status mismatch", errors)

    groups = data.get("groups", {})
    policy = data.get("policy", {})
    certificates = data.get("certificates", [])
    require(isinstance(groups, dict) and bool(groups), "certificate registry groups missing", errors)
    require(isinstance(policy, dict), "certificate registry policy missing", errors)
    require(isinstance(certificates, list) and bool(certificates), "certificate registry entries missing", errors)
    if isinstance(policy, dict):
        require(policy.get("physical_layout") == "data_subject_files", "certificate registry physical layout is not data-subject files", errors)
        require(policy.get("path_migration") == "consolidated_into_data", "certificate registry path migration is not consolidated", errors)

    ids: set[str] = set()
    dirs: set[str] = set()
    ordinals: set[int] = set()
    group_names = set(groups) if isinstance(groups, dict) else set()

    for i, entry in enumerate(certificates if isinstance(certificates, list) else []):
        require(isinstance(entry, dict), f"certificate registry entry {i} is not an object", errors)
        if not isinstance(entry, dict):
            continue

        certificate_id = entry.get("id")
        dirname = entry.get("ordinal_dir")
        ordinal = entry.get("ordinal")
        group = entry.get("group")
        rel = entry.get("path")

        require(isinstance(certificate_id, str) and bool(certificate_id), f"certificate registry entry {i} missing id", errors)
        require(certificate_id not in ids, f"duplicate certificate id: {certificate_id}", errors)
        if isinstance(certificate_id, str):
            ids.add(certificate_id)

        require(isinstance(dirname, str) and bool(dirname), f"{certificate_id}: missing ordinal_dir", errors)
        require(dirname not in dirs, f"duplicate layer ordinal_dir: {dirname}", errors)
        if isinstance(dirname, str):
            dirs.add(dirname)

        require(isinstance(ordinal, int), f"{certificate_id}: ordinal is not an integer", errors)
        require(ordinal not in ordinals, f"duplicate certificate ordinal: {ordinal}", errors)
        if isinstance(ordinal, int):
            ordinals.add(ordinal)

        require(group in group_names, f"{certificate_id}: unknown group {group!r}", errors)
        require(isinstance(rel, str), f"{certificate_id}: path is not a string", errors)
        if isinstance(group, str) and isinstance(rel, str):
            rel_path = Path(rel)
            require(rel_path.parent.as_posix() == f"data/{group}", f"{certificate_id}: path {rel!r} is not a direct child of its data group", errors)
            require(rel_path.suffix == ".json" and rel_path.name != "certificate.json", f"{certificate_id}: path {rel!r} is not a subject JSON certificate", errors)
            require((ROOT / rel).exists(), f"{certificate_id}: registry path missing: {rel}", errors)

        if isinstance(dirname, str) and dirname in EXPECTED:
            require(
                entry.get("expected_status") == EXPECTED[dirname],
                f"{certificate_id}: expected_status does not match verifier expectation for {dirname}",
                errors,
            )

        depends_on = entry.get("depends_on", [])
        require(isinstance(depends_on, list), f"{certificate_id}: depends_on is not a list", errors)
        if isinstance(depends_on, list):
            for dep in depends_on:
                require(isinstance(dep, str), f"{certificate_id}: dependency id is not a string", errors)

    require(dirs == set(EXPECTED), f"certificate registry ordinal_dir set mismatch: {sorted(dirs ^ set(EXPECTED))}", errors)
    require(ordinals == set(range(len(EXPECTED))), "certificate registry ordinal set mismatch", errors)

    for entry in certificates if isinstance(certificates, list) else []:
        if not isinstance(entry, dict):
            continue
        certificate_id = entry.get("id")
        depends_on = entry.get("depends_on", [])
        if not isinstance(depends_on, list):
            continue
        for dep in depends_on:
            if isinstance(dep, str):
                require(dep in ids, f"{certificate_id}: unknown dependency {dep}", errors)

    return data, {
        "schema": data.get("schema"),
        "status": data.get("status"),
        "registry_entries": len(certificates) if isinstance(certificates, list) else 0,
        "groups": sorted(group_names),
        "physical_layout": policy.get("physical_layout") if isinstance(policy, dict) else None,
        "path_migration": policy.get("path_migration") if isinstance(policy, dict) else None,
        "file_sha256": sha_file(CERTIFICATE_INDEX),
    }


def verify_certificate_layout(registry: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    data_root = ROOT / "data"
    require(data_root.is_dir(), "missing data directory", errors)
    if not data_root.is_dir():
        return {
            "status": "MISSING",
            "groups": [],
            "certificate_files": 0,
            "summary_files": 0,
        }

    groups = registry.get("groups", {})
    group_names = set(groups) if isinstance(groups, dict) else set()
    missing_group_dirs = sorted(group for group in group_names if not (data_root / group).is_dir())
    require(not missing_group_dirs, f"missing data certificate groups: {missing_group_dirs}", errors)

    registry_files = {
        entry.get("path")
        for entry in registry.get("certificates", [])
        if isinstance(entry, dict) and isinstance(entry.get("path"), str)
    }
    unexpected_files: list[str] = []
    summary_files: list[str] = []
    for group in group_names:
        group_dir = data_root / group
        if not group_dir.is_dir():
            continue
        for path in group_dir.iterdir():
            if not path.is_file():
                continue
            rel = path.relative_to(ROOT).as_posix()
            rel_path = Path(rel)
            if rel_path.suffix != ".json":
                unexpected_files.append(rel)
                continue
            if rel in registry_files:
                continue
            if rel_path.name.endswith(".summary.json"):
                summary_files.append(rel)
                continue
            unexpected_files.append(rel)

    require(not unexpected_files, f"unexpected certificate files: {unexpected_files}", errors)

    return {
        "status": "PASS" if not missing_group_dirs and not unexpected_files else "FAIL",
        "groups": sorted(group_names),
        "certificate_files": len(registry_files),
        "summary_files": len(summary_files),
    }


def verify_certificates(errors: list[str], registry: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    entries = registry.get("certificates", [])
    if not isinstance(entries, list) or not entries:
        entries = [
            {
                "id": dirname,
                "group": "ordinal",
                "ordinal_dir": dirname,
                "path": f"data/{dirname}/certificate.json",
                "expected_status": expected_status,
            }
            for dirname, expected_status in EXPECTED.items()
        ]

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        dirname = entry.get("ordinal_dir")
        rel = entry.get("path")
        expected_status = entry.get("expected_status")
        if not isinstance(dirname, str) or not isinstance(rel, str):
            continue
        p = ROOT / rel
        require(p.exists(), f"missing certificate: {rel}", errors)
        if not p.exists():
            continue
        data = load_json(p)
        status = data.get("status")
        if expected_status is not None:
            require(status == expected_status, f"{dirname}: status {status!r} != {expected_status!r}", errors)
        rows.append({
            "id": entry.get("id"),
            "group": entry.get("group"),
            "certificate": dirname,
            "status": status,
            "file_sha256": sha_file(p),
        })
    return rows


def verify_core_arrays(errors: list[str]) -> dict[str, Any]:
    import numpy as np

    def safe_load(path: Path, label: str) -> dict[str, Any] | None:
        try:
            return np.load(path)
        except Exception as exc:
            require(
                False,
                f"core invariant {label} load failed ({path}): {type(exc).__name__}: {exc}",
                errors,
            )
            return None

    def safe_array(payload: Any, key: str, label: str) -> Any | None:
        try:
            return np.asarray(payload[key], dtype=np.int64)
        except Exception as exc:
            require(
                False,
                f"core invariant {label} missing or invalid array '{key}': {type(exc).__name__}: {exc}",
                errors,
            )
            return None

    out: dict[str, Any] = {}
    z = safe_load(ROOT / raw_tensor_relpath(), "tensor")
    if z is None:
        return out
    triples = safe_array(z, "triples", "tensor")
    reps = safe_array(z, "reps", "tensor")
    M = safe_array(z, "M", "tensor")
    if triples is None or reps is None or M is None:
        return out
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

    q = safe_load(ROOT / "data/raw/quotients.npz", "quotients")
    if q is None:
        return out
    q42 = safe_array(q, "q42_map", "quotients")
    q12 = safe_array(q, "q12_map", "quotients")
    q42t = safe_array(q, "q42_tensor", "quotients")
    q12t = safe_array(q, "q12_tensor", "quotients")
    if q42 is None or q12 is None or q42t is None or q12t is None:
        return out
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

    b = safe_load(ROOT / "data/raw/simple_branching_matrices.npz", "simple branching")
    if b is None:
        return out
    B236_42 = safe_array(b, "B236_42", "simple branching")
    B42_12 = safe_array(b, "B42_12", "simple branching")
    B236_12 = safe_array(b, "B236_12", "simple branching")
    comp = safe_array(b, "comp", "simple branching")
    if B236_42 is None or B42_12 is None or B236_12 is None or comp is None:
        return out
    naturality = np.array_equal(B236_42 @ B42_12, B236_12) and np.array_equal(comp, B236_12)
    require(naturality, "simple branching naturality failed", errors)
    out.update({
        "simple_branching_naturality": bool(naturality),
        "B236_to_A42_shape": list(B236_42.shape),
        "B42_to_A12_shape": list(B42_12.shape),
        "B236_to_A12_shape": list(B236_12.shape),
    })

    l = safe_load(ROOT / "data/raw/leech_projective_generators.npz", "leech generators")
    if l is None:
        return out
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
    data = load_json(certificate_relpath("integrity.proof_system", registry))
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
    require(isinstance(man, dict), "manifest payload missing", errors)
    entries = man.get("entries") if isinstance(man, dict) else []
    require(isinstance(entries, list), "manifest entries missing", errors)
    if not isinstance(entries, list):
        return {"manifest_entries_checked": checked}

    for ent in entries:
        require(isinstance(ent, dict), "manifest entry is not an object", errors)
        if not isinstance(ent, dict):
            continue
        rel = ent.get("path")
        size = ent.get("size")
        sha = ent.get("sha256")
        require(isinstance(rel, str), "manifest entry missing path", errors)
        require(isinstance(size, int), "manifest entry missing size", errors)
        require(isinstance(sha, str) and len(sha) == 64, "manifest entry sha256 missing", errors)
        if not isinstance(rel, str) or not isinstance(size, int) or not (isinstance(sha, str) and len(sha) == 64):
            continue
        p = ROOT / rel
        require(p.exists(), f"manifest path missing: {rel}", errors)
        if not p.exists():
            continue
        require(p.stat().st_size == ent["size"], f"manifest size mismatch: {rel}", errors)
        require(sha_file(p) == ent["sha256"], f"manifest sha mismatch: {rel}", errors)
        checked += 1
    return {"manifest_entries_checked": checked}


def verify_jacobian_saturation_cache_manifest(errors: list[str]) -> dict[str, Any]:
    rel = JACOBIAN_SAT_CACHE_INDEX_MANIFEST
    p = ROOT / rel
    if not p.exists():
        rel = JACOBIAN_SAT_CACHE_MANIFEST
        p = ROOT / rel
        if not p.exists():
            return {"status": "MISSING", "path": rel, "note": "manifest not present"}
        payload = load_json(rel)
        manifest_errors: list[str] = []
        require(
            payload.get("schema") == "holotopy.saturation_cache_verification",
            "jacobian saturation cache manifest schema mismatch",
            manifest_errors,
        )
        require(payload.get("status") in {"PASS", "FAIL"}, "jacobian saturation cache manifest status missing", manifest_errors)

        entries = payload.get("entries")
        require(isinstance(entries, list), "jacobian saturation cache manifest entries missing", manifest_errors)

        cache_paths: set[str] = set()
        if isinstance(entries, list):
            for index, entry in enumerate(entries):
                require(
                    isinstance(entry, dict),
                    f"jacobian saturation cache manifest entry {index} is not an object",
                    manifest_errors,
                )
                if not isinstance(entry, dict):
                    continue
                cache_file = entry.get("cache_file")
                require(
                    isinstance(cache_file, str),
                    f"jacobian saturation cache manifest entry {index} missing cache_file",
                    manifest_errors,
                )
                if isinstance(cache_file, str):
                    cache_paths.add(cache_file)

        require(
            payload.get("expected_certificate_count") == len(cache_paths),
            "jacobian saturation cache manifest expected_certificate_count mismatch",
            manifest_errors,
        )
        verified_entries = [
            entry for entry in (entries if isinstance(entries, list) else [])
            if isinstance(entry, dict) and entry.get("status") == "PASS"
        ]
        require(
            payload.get("verified_certificate_count") == len(verified_entries),
            "jacobian saturation cache manifest verified_certificate_count mismatch",
            manifest_errors,
        )

        actual_cache_paths = sorted(
            repo_relative(path) for path in p.parent.glob("*.json")
            if path.name != "manifest.json"
        )
        missing = sorted(cache_paths - set(actual_cache_paths))
        extra = sorted(set(actual_cache_paths) - cache_paths)
        require(not extra, f"jacobian saturation cache manifest has extra cache files: {extra}", manifest_errors)

        require(
            payload.get("manifest_sha256")
            == sha_json({key: value for key, value in payload.items() if key != "manifest_sha256"}),
            "jacobian saturation cache manifest hash mismatch",
            manifest_errors,
        )

        if payload.get("status") == "FAIL":
            nested = payload.get("errors")
            require(
                isinstance(nested, list) and nested,
                "jacobian saturation cache manifest payload status is FAIL",
                manifest_errors,
            )

        optional_cache_errors = []
        if missing:
            optional_cache_errors.append(f"jacobian saturation cache manifest missing cache files: {missing}")
        if manifest_errors:
            errors.extend(manifest_errors)
        status = (
            "FAIL"
            if manifest_errors
            else "DEMOTED_OPTIONAL_STRICT_CACHE_MISSING"
            if optional_cache_errors
            else "PASS"
        )
        return {
            "status": status,
            "path": rel,
            "entries": len(entries) if isinstance(entries, list) else 0,
            "expected_certificate_count": payload.get("expected_certificate_count"),
            "verified_certificate_count": payload.get("verified_certificate_count"),
            "status_from_payload": payload.get("status"),
            "manifest_schema": payload.get("schema"),
            "errors": manifest_errors,
            "optional_cache_errors": optional_cache_errors,
            "policy": "strict saturation cache files are optional evidence; absence demotes this cache gate but does not fail core d20 verification",
        }

    index_payload = load_json(rel)
    manifest_errors: list[str] = []
    require(
        index_payload.get("schema") == "holotopy.saturation_cache_artifact_manifest",
        "jacobian saturation cache indexed manifest schema mismatch",
        manifest_errors,
    )
    require(
        index_payload.get("status") in {"PASS", "FAIL"},
        "jacobian saturation cache indexed manifest status missing",
        manifest_errors,
    )

    cache_manifest_rel = index_payload.get("cache_manifest")
    require(
        isinstance(cache_manifest_rel, str),
        "jacobian saturation cache indexed manifest missing cache manifest path",
        manifest_errors,
    )
    cache_manifest_path = ROOT / cache_manifest_rel if isinstance(cache_manifest_rel, str) else p
    require(
        cache_manifest_path.exists(),
        "jacobian saturation cache indexed manifest points to non-existent cache manifest",
        manifest_errors,
    )
    require(
        cache_manifest_rel == JACOBIAN_SAT_CACHE_MANIFEST,
        "jacobian saturation cache indexed manifest references unexpected cache manifest",
        manifest_errors,
    )
    cache_payload = load_json(cache_manifest_path)
    require(
        cache_payload.get("manifest_sha256") == index_payload.get("cache_manifest_sha256"),
        "jacobian saturation cache indexed manifest cache manifest hash mismatch",
        manifest_errors,
    )

    entries = index_payload.get("entries")
    require(isinstance(entries, list), "jacobian saturation cache indexed manifest entries missing", manifest_errors)

    cache_paths: set[str] = set()
    if isinstance(entries, list):
        for index, entry in enumerate(entries):
            require(
                isinstance(entry, dict),
                f"jacobian saturation cache indexed manifest entry {index} is not an object",
                manifest_errors,
            )
            if not isinstance(entry, dict):
                continue
            cache_file = entry.get("cache_file")
            require(
                isinstance(cache_file, str),
                f"jacobian saturation cache indexed manifest entry {index} missing cache_file",
                manifest_errors,
            )
            if isinstance(cache_file, str):
                cache_paths.add(cache_file)

    require(
        index_payload.get("expected_certificate_count") == len(cache_paths),
        "jacobian saturation cache indexed manifest expected_certificate_count mismatch",
        manifest_errors,
    )
    indexed_verified_entries = [
        entry for entry in (entries if isinstance(entries, list) else [])
        if isinstance(entry, dict) and entry.get("status") == "PASS"
    ]
    require(
        index_payload.get("verified_certificate_count") == len(indexed_verified_entries),
        "jacobian saturation cache indexed manifest verified_certificate_count mismatch",
        manifest_errors,
    )

    cache_dir_rel = index_payload.get("cache_directory")
    require(isinstance(cache_dir_rel, str), "jacobian saturation cache indexed manifest missing cache directory", manifest_errors)
    cache_dir_path = ROOT / cache_dir_rel if isinstance(cache_dir_rel, str) else p.parent
    if isinstance(cache_dir_rel, str):
        require(cache_dir_path.exists(), "jacobian saturation cache indexed manifest cache directory missing", manifest_errors)
        actual_cache_paths = sorted(
            repo_relative(path) for path in cache_dir_path.glob("*.json")
            if path.name != "manifest.json"
        )
    else:
        actual_cache_paths = sorted(repo_relative(path) for path in p.parent.glob("*.json") if path.name != "manifest.json")

    missing = sorted(cache_paths - set(actual_cache_paths))
    extra = sorted(set(actual_cache_paths) - cache_paths)
    require(not extra, f"jacobian saturation cache indexed manifest has extra cache files: {extra}", manifest_errors)

    require(
        index_payload.get("cache_manifest_sha256") is not None,
        "jacobian saturation cache indexed manifest missing cache manifest hash",
        manifest_errors,
    )
    require(
        index_payload.get("manifest_sha256")
        == sha_json({key: value for key, value in index_payload.items() if key != "manifest_sha256"}),
        "jacobian saturation cache indexed manifest hash mismatch",
        manifest_errors,
    )

    optional_cache_errors = []
    if missing:
        optional_cache_errors.append(f"jacobian saturation cache indexed manifest missing cache files: {missing}")
    if manifest_errors:
        errors.extend(manifest_errors)
    status = (
        "FAIL"
        if manifest_errors
        else "DEMOTED_OPTIONAL_STRICT_CACHE_MISSING"
        if optional_cache_errors
        else "PASS"
    )
    return {
        "status": status,
        "path": rel,
        "entries": len(entries) if isinstance(entries, list) else 0,
        "expected_certificate_count": index_payload.get("expected_certificate_count"),
        "verified_certificate_count": index_payload.get("verified_certificate_count"),
        "status_from_payload": index_payload.get("status"),
        "manifest_schema": index_payload.get("schema"),
        "errors": manifest_errors,
        "optional_cache_errors": optional_cache_errors,
        "policy": "strict saturation cache files are optional evidence; absence demotes this cache gate but does not fail core d20 verification",
    }


def verify_constructor_witness(errors: list[str]) -> dict[str, Any]:
    error_start = len(errors)
    try:
        from src.commands.construct import construct_from_generated_strict_scratch_pipeline

        witness = construct_from_generated_strict_scratch_pipeline()
    except Exception as exc:
        errors.append(f"constructor witness exception: {type(exc).__name__}: {exc}")
        return {"status": "ERROR", "error": f"{type(exc).__name__}: {exc}"}

    require(witness.get("schema") == "d20.constructor.generated_strict_scratch_pipeline@1", "constructor witness schema mismatch", errors)
    require(witness.get("constructor_status") == "GENERATED_STRICT_SCRATCH_CONSTRUCTOR_PASS", "constructor witness status mismatch", errors)
    require(witness.get("constructs_from_supplied_raw_seeds") is False, "constructor witness used supplied raw seeds", errors)
    require(witness.get("strict_scratch_passed") is True, "constructor witness strict-scratch check failed", errors)
    require(witness.get("full_scratch_object_constructor") is True, "constructor witness did not certify full scratch construction", errors)
    require(witness.get("missing_full_scratch_steps") == [], "constructor witness full-scratch missing-step list not empty", errors)
    require(witness.get("remaining_boundary") == [], "constructor witness full-scratch boundary list not empty", errors)

    finite = witness.get("finite_object", {})
    require(finite.get("points") == 2576, "constructor witness point count mismatch", errors)
    require(finite.get("group_order") == 9216, "constructor witness group order mismatch", errors)
    require(finite.get("relations") == 985, "constructor witness relation count mismatch", errors)
    require(finite.get("ordered_pair_partition_ok") is True, "constructor witness ordered-pair partition failed", errors)
    require(finite.get("block_mass_is_object_size_outer_product") is True, "constructor witness block mass failed", errors)

    tensor = witness.get("tensor", {}).get("report", {})
    require(tensor.get("tensor_support") == 1_414_965, "constructor witness tensor support mismatch", errors)
    require(tensor.get("coefficient_total") == 2_537_360, "constructor witness tensor coefficient total mismatch", errors)
    require(tensor.get("comparison", {}).get("matches_supplied_tensor") is True, "constructor witness tensor audit-target mismatch", errors)

    readouts = witness.get("readouts", {})
    require(readouts.get("terminal_quotients_status") == "TERMINAL_QUOTIENTS_PASS", "constructor witness terminal quotient derivation failed", errors)
    require(readouts.get("native_a236_status") == "NATIVE_A236_D20_D6_FORMULAE_PASS", "constructor witness native A236 derivation failed", errors)
    require(readouts.get("a236_profunctor_status") == "A236_PROFUNCTOR_FROM_TUBE_CACHE_PASS", "constructor witness A236 profunctor derivation failed", errors)
    require(readouts.get("a236_profunctor_remaining_boundary") == [], "constructor witness A236 profunctor boundary not empty", errors)
    require(readouts.get("simple_branching_naturality") is True, "constructor witness simple branching naturality failed", errors)
    for name, passed in witness.get("checks", {}).items():
        require(passed is True, f"constructor witness check failed: {name}", errors)

    return {
        "status": witness.get("constructor_status"),
        "audit_class": "CERTIFIED_FULL_SCRATCH_CONSTRUCTOR",
        "hard_failure": len(errors) > error_start,
        "schema": witness.get("schema"),
        "result_sha256": witness.get("constructor_result_sha256"),
        "constructs_from_supplied_raw_seeds": witness.get("constructs_from_supplied_raw_seeds"),
        "full_scratch_object_constructor": witness.get("full_scratch_object_constructor"),
        "strict_scratch_passed": witness.get("strict_scratch_passed"),
        "seed_boundary": witness.get("seed_boundary"),
        "audit_targets_not_constructor_inputs": witness.get("audit_targets_not_constructor_inputs"),
        "finite_object": finite,
        "tensor": {
            "support": tensor.get("tensor_support"),
            "coefficient_total": tensor.get("coefficient_total"),
            "tensor_sha256": tensor.get("tensor_sha256"),
        },
        "readouts": readouts,
        "checks": witness.get("checks"),
        "missing_full_scratch_steps": witness.get("missing_full_scratch_steps"),
    }


def verify_zero_axiom_strict_replay(errors: list[str]) -> dict[str, Any]:
    try:
        from src.derive_d20_zero_axiom_coorient_strict_replay_theorem import build_theorem

        report = build_theorem()
    except Exception as exc:
        errors.append(f"zero-axiom strict replay exception: {type(exc).__name__}: {exc}")
        return {"status": "ERROR", "error": f"{type(exc).__name__}: {exc}"}

    require(
        report.get("status") == "D20_ZERO_AXIOM_COORIENT_STRICT_REPLAY_CERTIFIED",
        "zero-axiom strict replay status mismatch",
        errors,
    )
    require(report.get("all_checks_pass") is True, "zero-axiom strict replay checks failed", errors)
    checks = report.get("checks", {})
    require(isinstance(checks, dict) and all(value is True for value in checks.values()), "zero-axiom strict replay check map mismatch", errors)

    derived = report.get("derived", {})
    require(
        derived.get("cache_certificate_sha256") == derived.get("fresh_certificate_sha256"),
        "zero-axiom strict replay certificate hash mismatch",
        errors,
    )
    require(
        derived.get("cache_file_sha256") == derived.get("fresh_pretty_sha256"),
        "zero-axiom strict replay byte hash mismatch",
        errors,
    )
    require(
        int(derived.get("cache_byte_length", -1)) == int(derived.get("fresh_pretty_byte_length", -2)),
        "zero-axiom strict replay byte length mismatch",
        errors,
    )
    require(derived.get("canonical_base") == [18, 67, 37], "zero-axiom strict replay base mismatch", errors)
    require(derived.get("final_signature_count") == 2576, "zero-axiom strict replay signature count mismatch", errors)
    require(derived.get("closed_action_order") == 9216, "zero-axiom strict replay closure order mismatch", errors)

    return {
        "status": report.get("status"),
        "certificate_sha256": report.get("certificate_sha256"),
        "cache_certificate_sha256": derived.get("cache_certificate_sha256"),
        "fresh_certificate_sha256": derived.get("fresh_certificate_sha256"),
        "cache_file_sha256": derived.get("cache_file_sha256"),
        "fresh_pretty_sha256": derived.get("fresh_pretty_sha256"),
        "cache_newline": derived.get("cache_newline"),
        "cache_byte_length": derived.get("cache_byte_length"),
        "fresh_pretty_byte_length": derived.get("fresh_pretty_byte_length"),
        "canonical_base": derived.get("canonical_base"),
        "final_signature_count": derived.get("final_signature_count"),
        "closed_action_order": derived.get("closed_action_order"),
        "all_checks_pass": report.get("all_checks_pass"),
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


def verify_token_burn_guard(errors: list[str]) -> dict[str, Any]:
    try:
        from src.certify_token_burn_guard import (
            compact_certificate,
            validate_token_burn_guard,
            write_token_burn_guard_artifacts,
        )
    except Exception as exc:
        errors.append(f"token-burn guard import failed: {type(exc).__name__}: {exc}")
        return {"status": "ERROR", "error": f"{type(exc).__name__}: {exc}"}

    try:
        result = validate_token_burn_guard()
        artifacts = write_token_burn_guard_artifacts(result)
        certificate = compact_certificate(result)
    except Exception as exc:
        errors.append(f"token-burn guard audit failed: {type(exc).__name__}: {exc}")
        return {"status": "ERROR", "error": f"{type(exc).__name__}: {exc}"}

    if result.get("status") != "TOKEN_BURN_GUARD_PASS":
        errors.append("token-burn guard status is not TOKEN_BURN_GUARD_PASS")

    return {
        "status": result.get("status"),
        "certificate_status": certificate.get("status"),
        "certificate_sha256": certificate.get("certificate_sha256"),
        "artifacts": artifacts,
        "coverage": certificate.get("coverage"),
        "checks": result.get("checks"),
    }


def run(mode: str) -> dict[str, Any]:
    if mode == "tamper":
        return verify_tamper_resistance()
    if mode == "token-burn":
        errors: list[str] = []
        token_burn_guard = verify_token_burn_guard(errors)
        return {
            "status": "PASS" if not errors else "FAIL",
            "mode": mode,
            "token_burn_guard": token_burn_guard,
            "errors": errors,
        }

    errors: list[str] = []
    root = verify_root(errors)
    d20 = verify_d20_json(errors)
    certificate_registry, certificate_registry_summary = verify_certificate_registry(errors)
    certificate_layout = verify_certificate_layout(certificate_registry, errors)
    verify_root_certificates(root, certificate_registry, errors)
    invariant_report_inventory_summary = verify_root_invariant_reports(root, errors)
    certificates = verify_certificates(errors, certificate_registry)
    core = verify_core_arrays(errors)
    integrity = verify_integrity(errors, certificate_registry)
    out: dict[str, Any] = {
        "status": "PASS" if not errors else "FAIL",
        "mode": mode,
        "headline": root.get("status"),
        "d20": d20,
        "certificate_registry": certificate_registry_summary,
        "certificate_layout": certificate_layout,
        "invariant_report_inventory": invariant_report_inventory_summary,
        "certificate_count": len(certificates),
        "core": core,
        "integrity": integrity,
        "errors": errors,
    }
    out["jacobian_saturation_cache_manifest"] = verify_jacobian_saturation_cache_manifest(errors)
    if out["jacobian_saturation_cache_manifest"]["status"] == "FAIL":
        out["status"] = "FAIL"
    if mode in {"audit", "rebuild"}:
        out["token_burn_guard"] = verify_token_burn_guard(errors)
        out["constructor_witness"] = verify_constructor_witness(errors)
        out["manifest"] = verify_manifest(errors)
        out["status"] = "PASS" if not errors else "FAIL"
    if mode == "strict-replay":
        out["zero_axiom_strict_replay"] = verify_zero_axiom_strict_replay(errors)
        out["status"] = "PASS" if not errors else "FAIL"
    if mode == "rebuild":
        out["rebuild"] = "d20.json and source certificates checked; generated cache is not required"
    return out


def maybe_regenerate(
    mode: str,
    pretty: bool,
    enabled: bool,
    *,
    refresh_sources: bool = True,
) -> dict[str, Any]:
    if not enabled:
        return {"regenerated_before_certification": False}
    from src.commands import regen

    regen.rebuild_d20(pretty=pretty, refresh_sources=refresh_sources)
    regen.refresh_certificate()
    count = regen.refresh_manifest()
    return {
        "regenerated_before_certification": True,
        "source_certificates_refreshed": refresh_sources,
        "manifest_entries_refreshed": count,
    }


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Verify the d20 bundle. Only --mode rebuild or --regenerate rewrites files."
    )
    ap.add_argument("--mode", choices=["fast", "audit", "rebuild", "tamper", "strict-replay", "token-burn"], default="audit")
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
    ap.add_argument(
        "--cached-source",
        action="store_true",
        help="When regenerating, reuse existing checked source artifacts instead of refreshing pre-A985/coorient/evidence data.",
    )
    args = ap.parse_args()
    should_regenerate = (args.mode == "rebuild" or args.regenerate) and not args.no_regenerate
    regen_info = maybe_regenerate(
        args.mode,
        args.pretty,
        should_regenerate,
        refresh_sources=not args.cached_source,
    )
    out = run(args.mode)
    out["regeneration"] = regen_info
    if out["status"] != "PASS":
        emit_json(out, pretty=args.pretty)
        sys.exit(1)
    emit_json(out, pretty=args.pretty)


if __name__ == "__main__":
    main()
