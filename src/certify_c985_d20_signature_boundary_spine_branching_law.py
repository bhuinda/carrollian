from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_branching_law import (
        BRANCH_ORDER_COLUMNS,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PHASE_SUMMARY_COLUMNS,
        RESIDUAL_CHART_CARRIER_CSV,
        RESIDUAL_CHART_CERTIFICATE,
        RESIDUAL_CHART_JSON,
        RESIDUAL_CHART_REPORT,
        RESIDUAL_CHART_TABLES,
        ROUTING_PREFIX_CERTIFICATE,
        ROUTING_PREFIX_JSON,
        ROUTING_PREFIX_REPORT,
        ROUTING_PREFIX_SUMMARY,
        ROUTING_PREFIX_TABLES,
        SPINE_PATH_CERTIFICATE,
        SPINE_PATH_EDGES,
        SPINE_PATH_REPORT,
        SPINE_PATH_TABLES,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_branching_law import (
        BRANCH_ORDER_COLUMNS,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PHASE_SUMMARY_COLUMNS,
        RESIDUAL_CHART_CARRIER_CSV,
        RESIDUAL_CHART_CERTIFICATE,
        RESIDUAL_CHART_JSON,
        RESIDUAL_CHART_REPORT,
        RESIDUAL_CHART_TABLES,
        ROUTING_PREFIX_CERTIFICATE,
        ROUTING_PREFIX_JSON,
        ROUTING_PREFIX_REPORT,
        ROUTING_PREFIX_SUMMARY,
        ROUTING_PREFIX_TABLES,
        SPINE_PATH_CERTIFICATE,
        SPINE_PATH_EDGES,
        SPINE_PATH_REPORT,
        SPINE_PATH_TABLES,
        STATUS,
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


def validate_c985_d20_signature_boundary_spine_branching_law() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    branch_law = load_json(OUT_DIR / "signature_boundary_spine_branching_law.json")
    certificate = load_json(
        OUT_DIR / "signature_boundary_spine_branching_law_certificate.json"
    )
    branch_csv = (OUT_DIR / "negative_branch_order.csv").read_text(
        encoding="utf-8"
    )
    phase_csv = (OUT_DIR / "branch_phase_summary.csv").read_text(encoding="utf-8")
    observable_csv = (OUT_DIR / "branch_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(
        OUT_DIR / "signature_boundary_spine_branching_law_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if branch_law != expected["signature_boundary_spine_branching_law"]:
        raise AssertionError("boundary spine branching law JSON is not reproducible")
    if branch_csv != expected["negative_branch_order_csv"]:
        raise AssertionError("negative branch order CSV is not reproducible")
    if phase_csv != expected["branch_phase_summary_csv"]:
        raise AssertionError("branch phase summary CSV is not reproducible")
    if observable_csv != expected["branch_observables_csv"]:
        raise AssertionError("branch observable CSV is not reproducible")
    if certificate != expected["signature_boundary_spine_branching_law_certificate"]:
        raise AssertionError("boundary spine branching law certificate is not reproducible")

    table_names = [
        "negative_branch_order_table",
        "branch_phase_summary_table",
        "branch_observable_table",
    ]
    for name in table_names:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"boundary spine branching table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_branching_law@1":
        raise AssertionError("C985 d20 boundary spine branching law report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 boundary spine branching law is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 boundary spine branching law all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 boundary spine branching law checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 boundary spine branching law report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 boundary spine branching law report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "spine_path_report_certified",
        "routing_prefix_report_certified",
        "residual_chart_report_certified",
        "spine_path_certificate_available",
        "routing_prefix_certificate_available",
        "residual_chart_certificate_available",
        "routing_prefix_schema_available",
        "residual_chart_schema_available",
        "spine_path_tables_available",
        "routing_prefix_tables_available",
        "residual_chart_tables_available",
        "branch_order_matches_expected",
        "branch_first_prefixes_match_expected",
        "phase_new_bitsets_match_expected",
        "phase_edge_counts_match_expected",
        "obstruction_branch_order_matches_expected",
        "obstruction_phase_counts_match_expected",
        "flip_new_mask_is_non_obstruction_9",
        "delayed_obstruction_is_mask_4",
        "all_boundary_active_negative_reached_before_high_contact",
        "inactive_negative_region_is_mask_5",
        "branch_table_shape_is_6_by_21",
        "phase_table_shape_is_3_by_16",
        "observable_table_shape_matches_codebook",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 boundary spine branching law missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("residual_flip_prefix_length") != 8:
        raise AssertionError("branching law residual flip prefix mismatch")
    if witness.get("negative_branch_order") != [13, 7, 8, 9, 6, 4]:
        raise AssertionError("branching law negative branch order mismatch")
    if witness.get("negative_branch_first_prefixes") != [1, 3, 5, 8, 12, 14]:
        raise AssertionError("branching law first-prefix sequence mismatch")
    if witness.get("negative_branch_first_edge_ids") != [14, 2, 3, 11, 5, 4]:
        raise AssertionError("branching law first-edge sequence mismatch")
    if witness.get("pre_flip_new_negative_mask_ids") != [7, 8, 13]:
        raise AssertionError("branching law pre-flip new masks mismatch")
    if witness.get("at_flip_new_negative_mask_ids") != [9]:
        raise AssertionError("branching law at-flip new masks mismatch")
    if witness.get("post_flip_new_negative_mask_ids") != [4, 6]:
        raise AssertionError("branching law post-flip new masks mismatch")
    if witness.get("previous_obstruction_mask_class_ids") != [4, 7, 8]:
        raise AssertionError("branching law previous obstruction masks mismatch")
    if witness.get("obstruction_branch_order") != [7, 8, 4]:
        raise AssertionError("branching law obstruction order mismatch")
    if witness.get("obstruction_branch_first_prefixes") != [3, 5, 14]:
        raise AssertionError("branching law obstruction prefix mismatch")
    if witness.get("pre_flip_obstruction_mask_ids") != [7, 8]:
        raise AssertionError("branching law pre-flip obstruction mismatch")
    if witness.get("at_flip_obstruction_mask_ids") != []:
        raise AssertionError("branching law at-flip obstruction mismatch")
    if witness.get("post_flip_obstruction_mask_ids") != [4]:
        raise AssertionError("branching law post-flip obstruction mismatch")
    if witness.get("flip_new_negative_mask_id") != 9:
        raise AssertionError("branching law flip new mask mismatch")
    if witness.get("delayed_obstruction_mask_id") != 4:
        raise AssertionError("branching law delayed obstruction mismatch")
    if witness.get("all_boundary_active_negative_reached_prefix") != 14:
        raise AssertionError("branching law branch completion prefix mismatch")
    if witness.get("first_high_negative_prefix") != 15:
        raise AssertionError("branching law first high-negative prefix mismatch")
    if witness.get("boundary_active_negative_mask_ids") != [4, 6, 7, 8, 9, 13]:
        raise AssertionError("branching law boundary-active negative masks mismatch")
    if witness.get("inactive_negative_region_mask_ids") != [5]:
        raise AssertionError("branching law inactive negative mask mismatch")

    branch_table = np.asarray(tables["negative_branch_order_table"], dtype=np.int64)
    phase_table = np.asarray(tables["branch_phase_summary_table"], dtype=np.int64)
    observable_table = np.asarray(tables["branch_observable_table"], dtype=np.int64)

    if branch_table.shape != (6, len(BRANCH_ORDER_COLUMNS)):
        raise AssertionError("negative branch order table shape mismatch")
    if phase_table.shape != (3, len(PHASE_SUMMARY_COLUMNS)):
        raise AssertionError("branch phase summary table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("branch observable table shape mismatch")
    if branch_table[:, 1].tolist() != [13, 7, 8, 9, 6, 4]:
        raise AssertionError("negative branch order table sequence mismatch")
    if branch_table[:, 2].tolist() != [1, 3, 5, 8, 12, 14]:
        raise AssertionError("negative branch order table prefix mismatch")
    if branch_table[:, 6].tolist() != [-1, -1, -1, 0, 1, 1]:
        raise AssertionError("negative branch order phase sequence mismatch")
    if branch_table[:, 7].tolist() != [0, 1, 1, 0, 0, 1]:
        raise AssertionError("negative branch order obstruction flags mismatch")
    if phase_table[:, 0].tolist() != [-1, 0, 1]:
        raise AssertionError("branch phase summary phase order mismatch")
    if phase_table[:, 3].tolist() != [8576, 512, 80]:
        raise AssertionError("branch phase summary new-mask bitsets mismatch")
    if phase_table[:, 6].tolist() != [2, 0, 1]:
        raise AssertionError("branch phase summary obstruction counts mismatch")
    if observable_table[:, 1].tolist() != [
        code for _, code in sorted(OBSERVABLE_CODES.items(), key=lambda item: item[1])
    ]:
        raise AssertionError("branch observable code order mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("spine_path_report", {}), SPINE_PATH_REPORT, "spine path report input")
    assert_file_hash(inputs.get("spine_path_edges", {}), SPINE_PATH_EDGES, "spine path edges input")
    assert_file_hash(inputs.get("spine_path_tables", {}), SPINE_PATH_TABLES, "spine path tables input")
    assert_file_hash(
        inputs.get("spine_path_certificate", {}),
        SPINE_PATH_CERTIFICATE,
        "spine path certificate input",
    )
    assert_file_hash(
        inputs.get("routing_prefix_report", {}),
        ROUTING_PREFIX_REPORT,
        "routing prefix report input",
    )
    assert_file_hash(inputs.get("routing_prefix", {}), ROUTING_PREFIX_JSON, "routing prefix JSON input")
    assert_file_hash(
        inputs.get("routing_prefix_summary", {}),
        ROUTING_PREFIX_SUMMARY,
        "routing prefix summary input",
    )
    assert_file_hash(
        inputs.get("routing_prefix_tables", {}),
        ROUTING_PREFIX_TABLES,
        "routing prefix tables input",
    )
    assert_file_hash(
        inputs.get("routing_prefix_certificate", {}),
        ROUTING_PREFIX_CERTIFICATE,
        "routing prefix certificate input",
    )
    assert_file_hash(
        inputs.get("residual_chart_report", {}),
        RESIDUAL_CHART_REPORT,
        "residual chart report input",
    )
    assert_file_hash(inputs.get("residual_chart", {}), RESIDUAL_CHART_JSON, "residual chart JSON input")
    assert_file_hash(
        inputs.get("residual_chart_carriers", {}),
        RESIDUAL_CHART_CARRIER_CSV,
        "residual chart carrier input",
    )
    assert_file_hash(
        inputs.get("residual_chart_tables", {}),
        RESIDUAL_CHART_TABLES,
        "residual chart tables input",
    )
    assert_file_hash(
        inputs.get("residual_chart_certificate", {}),
        RESIDUAL_CHART_CERTIFICATE,
        "residual chart certificate input",
    )

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_branching_law_manifest@1":
        raise AssertionError("C985 d20 boundary spine branching law manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 boundary spine branching law manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 boundary spine branching law manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("C985 d20 boundary spine branching law missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 boundary spine branching law index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 boundary spine branching law index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_branching_law@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "negative_branch_order": witness.get("negative_branch_order"),
        "negative_branch_first_prefixes": witness.get(
            "negative_branch_first_prefixes"
        ),
        "obstruction_branch_order": witness.get("obstruction_branch_order"),
        "pre_flip_new_negative_mask_ids": witness.get(
            "pre_flip_new_negative_mask_ids"
        ),
        "at_flip_new_negative_mask_ids": witness.get(
            "at_flip_new_negative_mask_ids"
        ),
        "post_flip_new_negative_mask_ids": witness.get(
            "post_flip_new_negative_mask_ids"
        ),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_branching_law()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
