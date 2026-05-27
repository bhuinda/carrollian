from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_typed_corridors import (
        BRANCHING_LAW_CERTIFICATE,
        BRANCHING_LAW_CSV,
        BRANCHING_LAW_JSON,
        BRANCHING_LAW_REPORT,
        BRANCHING_LAW_TABLES,
        BRANCH_CORRIDOR_COLUMNS,
        CORRIDOR_EDGE_COLUMNS,
        CORRIDOR_OBSERVABLE_COLUMNS,
        OBSERVABLE_CODES,
        OUT_DIR,
        RESIDUAL_CHART_CARRIER_CSV,
        RESIDUAL_CHART_CERTIFICATE,
        RESIDUAL_CHART_REPORT,
        RESIDUAL_CHART_TABLES,
        SPINE_PATH_CERTIFICATE,
        SPINE_PATH_EDGES,
        SPINE_PATH_REPORT,
        SPINE_PATH_TABLES,
        STATUS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ALPHABET_JSON,
        SYMBOLIC_REWRITE_CERTIFICATE,
        SYMBOLIC_REWRITE_REPORT,
        SYMBOLIC_REWRITE_RULES_CSV,
        SYMBOLIC_REWRITE_TABLES,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_typed_corridors import (
        BRANCHING_LAW_CERTIFICATE,
        BRANCHING_LAW_CSV,
        BRANCHING_LAW_JSON,
        BRANCHING_LAW_REPORT,
        BRANCHING_LAW_TABLES,
        BRANCH_CORRIDOR_COLUMNS,
        CORRIDOR_EDGE_COLUMNS,
        CORRIDOR_OBSERVABLE_COLUMNS,
        OBSERVABLE_CODES,
        OUT_DIR,
        RESIDUAL_CHART_CARRIER_CSV,
        RESIDUAL_CHART_CERTIFICATE,
        RESIDUAL_CHART_REPORT,
        RESIDUAL_CHART_TABLES,
        SPINE_PATH_CERTIFICATE,
        SPINE_PATH_EDGES,
        SPINE_PATH_REPORT,
        SPINE_PATH_TABLES,
        STATUS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ALPHABET_JSON,
        SYMBOLIC_REWRITE_CERTIFICATE,
        SYMBOLIC_REWRITE_REPORT,
        SYMBOLIC_REWRITE_RULES_CSV,
        SYMBOLIC_REWRITE_TABLES,
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


def validate_c985_d20_signature_boundary_spine_typed_corridors() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    corridors = load_json(OUT_DIR / "signature_boundary_spine_typed_corridors.json")
    certificate = load_json(
        OUT_DIR / "signature_boundary_spine_typed_corridors_certificate.json"
    )
    edge_csv = (OUT_DIR / "corridor_edge_symbols.csv").read_text(encoding="utf-8")
    branch_csv = (OUT_DIR / "branch_corridor_summary.csv").read_text(
        encoding="utf-8"
    )
    observable_csv = (OUT_DIR / "corridor_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(
        OUT_DIR / "signature_boundary_spine_typed_corridors_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if corridors != expected["signature_boundary_spine_typed_corridors"]:
        raise AssertionError("boundary spine typed corridors JSON is not reproducible")
    if edge_csv != expected["corridor_edge_symbols_csv"]:
        raise AssertionError("corridor edge symbols CSV is not reproducible")
    if branch_csv != expected["branch_corridor_summary_csv"]:
        raise AssertionError("branch corridor summary CSV is not reproducible")
    if observable_csv != expected["corridor_observables_csv"]:
        raise AssertionError("corridor observable CSV is not reproducible")
    if certificate != expected["signature_boundary_spine_typed_corridors_certificate"]:
        raise AssertionError("boundary spine typed corridors certificate is not reproducible")

    table_names = [
        "corridor_edge_table",
        "branch_corridor_table",
        "corridor_observable_table",
    ]
    for name in table_names:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"typed corridor table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_typed_corridors@1":
        raise AssertionError("C985 d20 boundary spine typed corridors report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 boundary spine typed corridors is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 boundary spine typed corridors all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 boundary spine typed corridors checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 boundary spine typed corridors report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 boundary spine typed corridors report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "branching_law_report_certified",
        "spine_path_report_certified",
        "residual_chart_report_certified",
        "symbolic_rewrite_report_certified",
        "branching_law_schema_available",
        "symbolic_alphabet_schema_available",
        "branching_law_tables_available",
        "spine_path_tables_available",
        "residual_chart_tables_available",
        "symbolic_rewrite_tables_available",
        "all_corridor_edges_have_single_shared_atom",
        "all_shared_atoms_map_to_alphabet_symbols",
        "corridor_carriers_cover_full_six_symbol_alphabet",
        "gate_symbol_sequence_matches_expected",
        "gate_symbol_histogram_matches_expected",
        "gate_missing_symbols_are_x2_x4",
        "missing_gate_pair_is_full_sector_max_rewrite_pair",
        "branch_corridor_counts_match_expected",
        "pre_flip_branches_have_full_alphabet",
        "first_non_full_branch_is_flip_mask_9",
        "obstruction_gate_symbols_match_expected",
        "delayed_obstruction_gate_is_x3",
        "corridor_edge_table_shape_is_16_by_23",
        "branch_corridor_table_shape_is_6_by_22",
        "observable_table_shape_matches_codebook",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 boundary spine typed corridors missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("gate_symbol_sequence") != [
        5,
        5,
        0,
        0,
        1,
        3,
        1,
        5,
        3,
        5,
        5,
        3,
        5,
        3,
        1,
        0,
    ]:
        raise AssertionError("typed corridor gate symbol sequence mismatch")
    if witness.get("gate_symbol_ids") != [0, 1, 3, 5]:
        raise AssertionError("typed corridor gate symbol id set mismatch")
    if witness.get("missing_gate_symbol_ids") != [2, 4]:
        raise AssertionError("typed corridor missing gate symbols mismatch")
    if witness.get("branch_corridor_symbol_counts") != [6, 6, 6, 5, 4, 3]:
        raise AssertionError("typed corridor branch symbol counts mismatch")
    if witness.get("branch_first_shared_symbols") != [5, 0, 1, 5, 3, 3]:
        raise AssertionError("typed corridor first shared symbols mismatch")
    if witness.get("branch_positive_carrier_bitsets") != [7168, 6153, 6154, 7168, 4096, 4096]:
        raise AssertionError("typed corridor positive carrier bitsets mismatch")
    if witness.get("pre_flip_full_alphabet_branch_count") != 3:
        raise AssertionError("typed corridor pre-flip full alphabet count mismatch")
    if witness.get("at_flip_full_alphabet_branch_count") != 0:
        raise AssertionError("typed corridor at-flip full alphabet count mismatch")
    if witness.get("post_flip_full_alphabet_branch_count") != 0:
        raise AssertionError("typed corridor post-flip full alphabet count mismatch")
    if witness.get("first_non_full_alphabet_branch") != {
        "prefix_length": 8,
        "negative_carrier_mask_class_id": 9,
        "corridor_symbol_count": 5,
        "missing_symbol_ids": [4],
    }:
        raise AssertionError("typed corridor first non-full branch mismatch")
    if witness.get("obstruction_first_gate_symbol_ids") != [0, 1, 3]:
        raise AssertionError("typed corridor obstruction gate symbols mismatch")
    if witness.get("delayed_obstruction_shared_symbol_id") != 3:
        raise AssertionError("typed corridor delayed obstruction gate mismatch")

    edge_table = np.asarray(tables["corridor_edge_table"], dtype=np.int64)
    branch_table = np.asarray(tables["branch_corridor_table"], dtype=np.int64)
    observable_table = np.asarray(tables["corridor_observable_table"], dtype=np.int64)

    if edge_table.shape != (16, len(CORRIDOR_EDGE_COLUMNS)):
        raise AssertionError("typed corridor edge table shape mismatch")
    if branch_table.shape != (6, len(BRANCH_CORRIDOR_COLUMNS)):
        raise AssertionError("typed corridor branch table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(CORRIDOR_OBSERVABLE_COLUMNS)):
        raise AssertionError("typed corridor observable table shape mismatch")
    if edge_table[:, 15].tolist() != witness.get("gate_symbol_sequence"):
        raise AssertionError("typed corridor edge-table gate sequence mismatch")
    if branch_table[:, 11].tolist() != [6, 6, 6, 5, 4, 3]:
        raise AssertionError("typed corridor branch-table symbol counts mismatch")
    if branch_table[:, 14].tolist() != [5, 0, 1, 5, 3, 3]:
        raise AssertionError("typed corridor branch-table first shared symbols mismatch")
    if observable_table[:, 1].tolist() != [
        code for _, code in sorted(OBSERVABLE_CODES.items(), key=lambda item: item[1])
    ]:
        raise AssertionError("typed corridor observable code order mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("branching_law_report", {}),
        BRANCHING_LAW_REPORT,
        "branching law report input",
    )
    assert_file_hash(inputs.get("branching_law", {}), BRANCHING_LAW_JSON, "branching law JSON input")
    assert_file_hash(inputs.get("branching_law_csv", {}), BRANCHING_LAW_CSV, "branching law CSV input")
    assert_file_hash(
        inputs.get("branching_law_tables", {}),
        BRANCHING_LAW_TABLES,
        "branching law tables input",
    )
    assert_file_hash(
        inputs.get("branching_law_certificate", {}),
        BRANCHING_LAW_CERTIFICATE,
        "branching law certificate input",
    )
    assert_file_hash(inputs.get("spine_path_report", {}), SPINE_PATH_REPORT, "spine path report input")
    assert_file_hash(inputs.get("spine_path_edges", {}), SPINE_PATH_EDGES, "spine path edges input")
    assert_file_hash(inputs.get("spine_path_tables", {}), SPINE_PATH_TABLES, "spine path tables input")
    assert_file_hash(
        inputs.get("spine_path_certificate", {}),
        SPINE_PATH_CERTIFICATE,
        "spine path certificate input",
    )
    assert_file_hash(
        inputs.get("residual_chart_report", {}),
        RESIDUAL_CHART_REPORT,
        "residual chart report input",
    )
    assert_file_hash(
        inputs.get("residual_chart_carriers", {}),
        RESIDUAL_CHART_CARRIER_CSV,
        "residual chart carriers input",
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
    assert_file_hash(
        inputs.get("symbolic_rewrite_report", {}),
        SYMBOLIC_REWRITE_REPORT,
        "symbolic rewrite report input",
    )
    assert_file_hash(inputs.get("symbolic_alphabet", {}), SYMBOLIC_ALPHABET_JSON, "symbolic alphabet input")
    assert_file_hash(
        inputs.get("symbolic_alphabet_csv", {}),
        SYMBOLIC_ALPHABET_CSV,
        "symbolic alphabet CSV input",
    )
    assert_file_hash(
        inputs.get("symbolic_rewrite_rules", {}),
        SYMBOLIC_REWRITE_RULES_CSV,
        "symbolic rewrite rules input",
    )
    assert_file_hash(
        inputs.get("symbolic_rewrite_tables", {}),
        SYMBOLIC_REWRITE_TABLES,
        "symbolic rewrite tables input",
    )
    assert_file_hash(
        inputs.get("symbolic_rewrite_certificate", {}),
        SYMBOLIC_REWRITE_CERTIFICATE,
        "symbolic rewrite certificate input",
    )

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_typed_corridors_manifest@1":
        raise AssertionError("C985 d20 boundary spine typed corridors manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 boundary spine typed corridors manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 boundary spine typed corridors manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("C985 d20 boundary spine typed corridors missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 boundary spine typed corridors index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 boundary spine typed corridors index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_typed_corridors@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "gate_symbol_sequence": witness.get("gate_symbol_sequence"),
        "gate_symbol_ids": witness.get("gate_symbol_ids"),
        "missing_gate_symbol_ids": witness.get("missing_gate_symbol_ids"),
        "branch_corridor_symbol_counts": witness.get(
            "branch_corridor_symbol_counts"
        ),
        "first_non_full_alphabet_branch": witness.get(
            "first_non_full_alphabet_branch"
        ),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_typed_corridors()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
