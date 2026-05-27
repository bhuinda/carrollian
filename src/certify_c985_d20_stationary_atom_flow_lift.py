from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_stationary_atom_flow_lift import (
        ATLAS_CERTIFICATE,
        ATLAS_JSON,
        ATLAS_REPORT,
        ATLAS_TABLES,
        ATOM_FLOW_COLUMNS,
        ATOM_FLOW_OBSERVABLE_COLUMNS,
        BOUNDARY_TRANSFER_CERTIFICATE,
        BOUNDARY_TRANSFER_JSON,
        BOUNDARY_TRANSFER_REPORT,
        BOUNDARY_TRANSFER_TABLES,
        NODE_ATOM_CONTRIBUTION_COLUMNS,
        OUT_DIR,
        POINCARE_CERTIFICATE,
        POINCARE_JSON,
        POINCARE_REPORT,
        POINCARE_TABLES,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_JSON,
        REWRITE_COMPLEX_REPORT,
        SECTOR_FLOW_COLUMNS,
        SIGNATURE_FLOW_COLUMNS,
        STATUS,
        SYMBOLIC_CERTIFICATE,
        SYMBOLIC_JSON,
        SYMBOLIC_REPORT,
        SYMBOLIC_TABLES,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_stationary_atom_flow_lift import (
        ATLAS_CERTIFICATE,
        ATLAS_JSON,
        ATLAS_REPORT,
        ATLAS_TABLES,
        ATOM_FLOW_COLUMNS,
        ATOM_FLOW_OBSERVABLE_COLUMNS,
        BOUNDARY_TRANSFER_CERTIFICATE,
        BOUNDARY_TRANSFER_JSON,
        BOUNDARY_TRANSFER_REPORT,
        BOUNDARY_TRANSFER_TABLES,
        NODE_ATOM_CONTRIBUTION_COLUMNS,
        OUT_DIR,
        POINCARE_CERTIFICATE,
        POINCARE_JSON,
        POINCARE_REPORT,
        POINCARE_TABLES,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_JSON,
        REWRITE_COMPLEX_REPORT,
        SECTOR_FLOW_COLUMNS,
        SIGNATURE_FLOW_COLUMNS,
        STATUS,
        SYMBOLIC_CERTIFICATE,
        SYMBOLIC_JSON,
        SYMBOLIC_REPORT,
        SYMBOLIC_TABLES,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from derive_c985_typed_simple_object_registry import INDEX_PATH


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} is not a JSON object")
    return payload


def assert_file_hash(entry: dict[str, Any], expected_path: Path, label: str) -> None:
    expected_rel = expected_path.relative_to(ROOT).as_posix()
    if entry.get("path") != expected_rel:
        raise AssertionError(f"{label} path mismatch: {entry.get('path')} != {expected_rel}")
    if entry.get("sha256") != h_file(expected_path):
        raise AssertionError(f"{label} sha256 mismatch")


def validate_c985_d20_stationary_atom_flow_lift() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    atom_flow_lift = load_json(OUT_DIR / "stationary_atom_flow_lift.json")
    certificate = load_json(OUT_DIR / "stationary_atom_flow_certificate.json")
    contribution_csv = (OUT_DIR / "node_atom_contributions.csv").read_text(
        encoding="utf-8"
    )
    atom_csv = (OUT_DIR / "atom_flow.csv").read_text(encoding="utf-8")
    sector_csv = (OUT_DIR / "sector_flow.csv").read_text(encoding="utf-8")
    signature_csv = (OUT_DIR / "signature_flow.csv").read_text(encoding="utf-8")
    observable_csv = (OUT_DIR / "atom_flow_observables.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "stationary_atom_flow_tables.npz", allow_pickle=False)
    index = load_json(INDEX_PATH)

    if atom_flow_lift != expected["stationary_atom_flow_lift"]:
        raise AssertionError("d20 stationary atom-flow lift JSON is not reproducible")
    if contribution_csv != expected["node_atom_contributions_csv"]:
        raise AssertionError("d20 stationary atom-flow contribution CSV is not reproducible")
    if atom_csv != expected["atom_flow_csv"]:
        raise AssertionError("d20 stationary atom-flow atom CSV is not reproducible")
    if sector_csv != expected["sector_flow_csv"]:
        raise AssertionError("d20 stationary atom-flow sector CSV is not reproducible")
    if signature_csv != expected["signature_flow_csv"]:
        raise AssertionError("d20 stationary atom-flow signature CSV is not reproducible")
    if observable_csv != expected["atom_flow_observables_csv"]:
        raise AssertionError("d20 stationary atom-flow observable CSV is not reproducible")
    if certificate != expected["stationary_atom_flow_certificate"]:
        raise AssertionError("d20 stationary atom-flow certificate is not reproducible")

    table_names = [
        "node_atom_contribution_table",
        "atom_flow_table",
        "sector_flow_table",
        "signature_flow_table",
        "atom_signature_membership",
        "atom_flow_observable_table",
    ]
    for name in table_names:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"d20 stationary atom-flow table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_stationary_atom_flow_lift@1":
        raise AssertionError("C985 d20 stationary atom-flow report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 stationary atom-flow lift is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 stationary atom-flow all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 stationary atom-flow checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 stationary atom-flow report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 stationary atom-flow report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "rewrite_complex_report_certified",
        "rewrite_complex_certificate_certified",
        "boundary_atlas_report_certified",
        "boundary_atlas_certificate_certified",
        "poincare_report_certified",
        "poincare_certificate_certified",
        "symbolic_report_certified",
        "symbolic_certificate_certified",
        "boundary_transfer_report_certified",
        "boundary_transfer_certificate_certified",
        "core_node_count_is_12",
        "node_atom_contribution_count_is_36",
        "node_atom_contribution_table_shape_is_36_by_8",
        "active_atom_ids_are_symbolic_alphabet",
        "active_atom_count_is_6",
        "inactive_atom_count_is_14",
        "atom_flow_mass_sums_to_one",
        "active_atom_masses_match_expected",
        "top_atom_is_12",
        "top_atom_mass_matches_expected",
        "all_six_sectors_active",
        "sector_flow_mass_sums_to_one",
        "sector_masses_match_expected",
        "top_sector_is_vplus",
        "signature_support_count_is_221",
        "inactive_signature_count_is_12",
        "inactive_signature_ids_are_expected",
        "signature_flow_mass_sums_to_one",
        "top_signature_classes_are_78_to_84",
        "top_signature_mass_matches_expected",
        "atom_flow_center_matches_core_with_integer_tolerance",
        "atom_flow_center_radius_matches_expected",
        "atom_flow_mean_radius_is_0_144485801805",
        "atom_flow_table_shape_is_20_by_14",
        "sector_flow_table_shape_is_6_by_5",
        "signature_flow_table_shape_is_233_by_6",
        "observable_table_shape_matches_codebook",
        "symbolic_membership_shape_is_6_by_233",
        "atlas_atom_table_shape_is_20_rows",
        "poincare_coordinate_table_shape_is_20_rows",
        "boundary_transfer_stationary_table_available",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 stationary atom-flow missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("active_atom_ids") != [1, 4, 7, 11, 12, 19]:
        raise AssertionError("stationary atom-flow active atoms mismatch")
    if witness.get("active_atom_count") != 6 or witness.get("inactive_atom_count") != 14:
        raise AssertionError("stationary atom-flow atom support count mismatch")
    if witness.get("atom_flow_mass_sum_x1e12") != 1_000_000_000_000:
        raise AssertionError("stationary atom-flow atom mass sum mismatch")
    if witness.get("atom_flow_mass_x1e12", {}).get("12") != 330723741064:
        raise AssertionError("stationary atom-flow top atom mass mismatch")
    if witness.get("top_atom_ids") != [12]:
        raise AssertionError("stationary atom-flow top atom mismatch")
    if witness.get("active_sector_count") != 6:
        raise AssertionError("stationary atom-flow sector support mismatch")
    if witness.get("sector_flow_mass_sum_x1e12") != 1_000_000_000_000:
        raise AssertionError("stationary atom-flow sector mass sum mismatch")
    if witness.get("top_sector_labels") != ["V+"]:
        raise AssertionError("stationary atom-flow top sector mismatch")
    if witness.get("active_signature_class_count") != 221:
        raise AssertionError("stationary atom-flow active signature count mismatch")
    if witness.get("inactive_signature_class_count") != 12:
        raise AssertionError("stationary atom-flow inactive signature count mismatch")
    if witness.get("inactive_signature_class_ids") != [39, 40, 41, 42, 43, 44, 184, 185, 186, 187, 188, 189]:
        raise AssertionError("stationary atom-flow inactive signatures mismatch")
    if witness.get("signature_flow_mass_sum_x1e12") != 1_000_000_000_000:
        raise AssertionError("stationary atom-flow signature mass sum mismatch")
    if witness.get("top_signature_class_ids") != [78, 79, 80, 81, 82, 83, 84]:
        raise AssertionError("stationary atom-flow top signatures mismatch")
    geometry = witness.get("geometric_observables", {})
    if geometry.get("atom_flow_center_radius_x1e12") != 50308637906:
        raise AssertionError("stationary atom-flow center radius mismatch")
    if geometry.get("atom_flow_mean_poincare_radius_x1e12") != 144485801805:
        raise AssertionError("stationary atom-flow mean radius mismatch")
    if geometry.get("core_center_radius_delta_abs_x1e12", 99) > 16:
        raise AssertionError("stationary atom-flow core center radius delta mismatch")

    contribution_table = np.asarray(tables["node_atom_contribution_table"], dtype=np.int64)
    atom_table = np.asarray(tables["atom_flow_table"], dtype=np.int64)
    sector_table = np.asarray(tables["sector_flow_table"], dtype=np.int64)
    signature_table = np.asarray(tables["signature_flow_table"], dtype=np.int64)
    membership = np.asarray(tables["atom_signature_membership"], dtype=np.int8)
    observable_table = np.asarray(tables["atom_flow_observable_table"], dtype=np.int64)

    if contribution_table.shape != (36, len(NODE_ATOM_CONTRIBUTION_COLUMNS)):
        raise AssertionError("stationary atom-flow contribution table shape mismatch")
    if atom_table.shape != (20, len(ATOM_FLOW_COLUMNS)):
        raise AssertionError("stationary atom-flow atom table shape mismatch")
    if sector_table.shape != (6, len(SECTOR_FLOW_COLUMNS)):
        raise AssertionError("stationary atom-flow sector table shape mismatch")
    if signature_table.shape != (233, len(SIGNATURE_FLOW_COLUMNS)):
        raise AssertionError("stationary atom-flow signature table shape mismatch")
    if membership.shape != (20, 233):
        raise AssertionError("stationary atom-flow membership table shape mismatch")
    if observable_table.shape != (13, len(ATOM_FLOW_OBSERVABLE_COLUMNS)):
        raise AssertionError("stationary atom-flow observable table shape mismatch")
    if int(np.sum(atom_table[:, 1])) != 1_000_000_000_000:
        raise AssertionError("stationary atom-flow atom table mass sum mismatch")
    if int(np.sum(sector_table[:, 2])) != 1_000_000_000_000:
        raise AssertionError("stationary atom-flow sector table mass sum mismatch")
    if int(np.sum(signature_table[:, 1])) != 1_000_000_000_000:
        raise AssertionError("stationary atom-flow signature table mass sum mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("rewrite_complex_report", {}), REWRITE_COMPLEX_REPORT, "rewrite complex report input")
    assert_file_hash(inputs.get("rewrite_complex", {}), REWRITE_COMPLEX_JSON, "rewrite complex input")
    assert_file_hash(inputs.get("rewrite_complex_certificate", {}), REWRITE_COMPLEX_CERTIFICATE, "rewrite complex certificate input")
    assert_file_hash(inputs.get("boundary_atlas_report", {}), ATLAS_REPORT, "boundary atlas report input")
    assert_file_hash(inputs.get("boundary_atlas", {}), ATLAS_JSON, "boundary atlas input")
    assert_file_hash(inputs.get("boundary_atlas_tables", {}), ATLAS_TABLES, "boundary atlas tables input")
    assert_file_hash(inputs.get("boundary_atlas_certificate", {}), ATLAS_CERTIFICATE, "boundary atlas certificate input")
    assert_file_hash(inputs.get("poincare_report", {}), POINCARE_REPORT, "Poincare report input")
    assert_file_hash(inputs.get("poincare_embedding", {}), POINCARE_JSON, "Poincare input")
    assert_file_hash(inputs.get("poincare_tables", {}), POINCARE_TABLES, "Poincare tables input")
    assert_file_hash(inputs.get("poincare_certificate", {}), POINCARE_CERTIFICATE, "Poincare certificate input")
    assert_file_hash(inputs.get("symbolic_report", {}), SYMBOLIC_REPORT, "symbolic report input")
    assert_file_hash(inputs.get("symbolic_alphabet", {}), SYMBOLIC_JSON, "symbolic alphabet input")
    assert_file_hash(inputs.get("symbolic_tables", {}), SYMBOLIC_TABLES, "symbolic tables input")
    assert_file_hash(inputs.get("symbolic_certificate", {}), SYMBOLIC_CERTIFICATE, "symbolic certificate input")
    assert_file_hash(inputs.get("boundary_transfer_report", {}), BOUNDARY_TRANSFER_REPORT, "boundary transfer report input")
    assert_file_hash(inputs.get("boundary_transfer", {}), BOUNDARY_TRANSFER_JSON, "boundary transfer input")
    assert_file_hash(inputs.get("boundary_transfer_tables", {}), BOUNDARY_TRANSFER_TABLES, "boundary transfer tables input")
    assert_file_hash(inputs.get("boundary_transfer_certificate", {}), BOUNDARY_TRANSFER_CERTIFICATE, "boundary transfer certificate input")

    if manifest.get("schema") != "c985.proof_obligation.d20_stationary_atom_flow_lift_manifest@1":
        raise AssertionError("C985 d20 stationary atom-flow manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 stationary atom-flow manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 stationary atom-flow manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 d20 stationary atom-flow missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 stationary atom-flow index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 stationary atom-flow index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_stationary_atom_flow_lift@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "active_atom_ids": witness.get("active_atom_ids"),
        "top_atom_ids": witness.get("top_atom_ids"),
        "top_sector_labels": witness.get("top_sector_labels"),
        "active_signature_class_count": witness.get("active_signature_class_count"),
        "inactive_signature_class_ids": witness.get("inactive_signature_class_ids"),
        "atom_flow_center_radius_x1e12": geometry.get("atom_flow_center_radius_x1e12"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_stationary_atom_flow_lift()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
