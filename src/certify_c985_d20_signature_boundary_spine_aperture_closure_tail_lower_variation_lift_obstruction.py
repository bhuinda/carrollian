from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction import (
        CARRIER_SPLICE_CERTIFICATE,
        CARRIER_SPLICE_EXACT_WITNESSES,
        CARRIER_SPLICE_JSON,
        CARRIER_SPLICE_OPTIMALITY_CERTIFICATE,
        CARRIER_SPLICE_OPTIMALITY_CLASSES,
        CARRIER_SPLICE_OPTIMALITY_FRONTIER,
        CARRIER_SPLICE_OPTIMALITY_JSON,
        CARRIER_SPLICE_OPTIMALITY_OBSERVABLES,
        CARRIER_SPLICE_OPTIMALITY_REPORT,
        CARRIER_SPLICE_OPTIMALITY_TABLES,
        CARRIER_SPLICE_OPTIMALITY_STATUS,
        CARRIER_SPLICE_REPORT,
        CARRIER_SPLICE_SELECTED_TEMPLATES,
        CARRIER_SPLICE_TABLES,
        DERIVE_SCRIPT,
        ENDPOINT_SPLIT_TEMPLATES,
        INDEX_PATH,
        LIFT_EDGE_COLUMNS,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PROFILE_COLUMNS,
        SELECTED_SIX_TEMPLATE_TRACE,
        SELECTED_SIX_TEMPLATE_VARIATION,
        SELECTED_SIX_TEMPLATE_WITNESS_ID,
        SELECTED_SIX_TEMPLATE_WORD,
        STATUS,
        TEMPLATE_COLUMNS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction import (
        CARRIER_SPLICE_CERTIFICATE,
        CARRIER_SPLICE_EXACT_WITNESSES,
        CARRIER_SPLICE_JSON,
        CARRIER_SPLICE_OPTIMALITY_CERTIFICATE,
        CARRIER_SPLICE_OPTIMALITY_CLASSES,
        CARRIER_SPLICE_OPTIMALITY_FRONTIER,
        CARRIER_SPLICE_OPTIMALITY_JSON,
        CARRIER_SPLICE_OPTIMALITY_OBSERVABLES,
        CARRIER_SPLICE_OPTIMALITY_REPORT,
        CARRIER_SPLICE_OPTIMALITY_TABLES,
        CARRIER_SPLICE_OPTIMALITY_STATUS,
        CARRIER_SPLICE_REPORT,
        CARRIER_SPLICE_SELECTED_TEMPLATES,
        CARRIER_SPLICE_TABLES,
        DERIVE_SCRIPT,
        ENDPOINT_SPLIT_TEMPLATES,
        INDEX_PATH,
        LIFT_EDGE_COLUMNS,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PROFILE_COLUMNS,
        SELECTED_SIX_TEMPLATE_TRACE,
        SELECTED_SIX_TEMPLATE_VARIATION,
        SELECTED_SIX_TEMPLATE_WITNESS_ID,
        SELECTED_SIX_TEMPLATE_WORD,
        STATUS,
        TEMPLATE_COLUMNS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )


EXPECTED_PROFILE_ROWS = [
    (0, 0, 12, 7, 2, 2, 197, 26, 24, 192, 2, 12, 12, 2, 0, 0, 0, 24, 0, 0, 1, 0, 1, 0),
    (1, 0, 13, 8, 3, 2, 199, 24, 24, 160, 3, 8, 8, 0, 3, 0, 0, 0, 24, 0, 1, 0, 1, 0),
    (2, 1, 13, 8, 3, 2, 223, 0, 24, 240, 6, 4, 4, 6, 0, 12, 4, 8, 0, 0, 1, 1, 0, 1),
]

EXPECTED_TEMPLATE_ROWS = [
    (0, 0, 4, 11, 12, 4, 1, 11, 10, 3, 8, 13, 12, 38, 12, 11, 33, 43, 19, 7, 4, 12, 19),
    (0, 1, 5, 11, 12, 4, 1, 11, 10, 11, 8, 13, 12, 38, 38, 31, 33, 43, 19, 7, 4, 12, 19),
    (1, 0, -1, 13, 8, 0, 0, 13, 10, 3, 8, 13, 12, 40, 12, 11, 33, 43, 19, 7, 4, 12, 19),
    (1, 1, -1, 13, 8, 0, 0, 13, 10, 11, 8, 13, 12, 40, 38, 31, 33, 43, 19, 7, 4, 12, 19),
    (1, 2, -1, 13, 8, 0, 0, 13, 11, 3, 8, 13, 12, 42, 13, 11, 33, 43, 19, 7, 4, 12, 19),
    (2, 0, 0, 9, 4, 4, 1, 9, 10, 3, 8, 13, 12, 34, 12, 11, 33, 43, 19, 7, 4, 12, 19),
    (2, 1, 1, 9, 4, 4, 1, 9, 10, 11, 8, 13, 12, 34, 38, 31, 33, 43, 19, 7, 4, 12, 19),
    (2, 2, 2, 9, 4, 4, 1, 9, 11, 3, 8, 13, 12, 35, 13, 11, 33, 43, 19, 7, 4, 12, 19),
    (2, 3, 3, 10, 4, 4, 1, 10, 11, 3, 8, 13, 12, 38, 13, 11, 33, 43, 19, 7, 4, 12, 19),
    (2, 4, 4, 11, 4, 4, 1, 11, 10, 3, 8, 13, 12, 38, 12, 11, 33, 43, 19, 7, 4, 12, 19),
    (2, 5, 5, 11, 4, 4, 1, 11, 10, 11, 8, 13, 12, 38, 38, 31, 33, 43, 19, 7, 4, 12, 19),
]

EXPECTED_LIFT_EDGE_ROWS = [
    (0, 0, 2, 197, 223, 26, 2, 2, 1, 24, 24, 1, 2, 6, 4, 12, 4, -8, 2, 6, 4, 12, 4, -16, 0, 1, 0),
    (1, 1, 2, 199, 223, 24, 2, 2, 1, 24, 24, 1, 3, 6, 3, 8, 4, -4, 0, 6, 6, 12, 4, 8, -24, 1, 0),
]

EXPECTED_OBSERVABLES = {
    "lower_variation_witness_count": 2,
    "lower_variation_min": 197,
    "lower_variation_max": 199,
    "lower_variation_template_count_min": 2,
    "lower_variation_template_count_max": 3,
    "lower_variation_endpoint11_only_count": 1,
    "lower_variation_endpoint13_only_count": 1,
    "selected_lift_witness_id": 2,
    "selected_lift_variation": 223,
    "selected_lift_template_count": 6,
    "selected_lift_delta_twice": 2,
    "selected_lift_closed_paths": 24,
    "min_variation_gap_to_six_template_lift": 24,
    "max_variation_gap_to_six_template_lift": 26,
    "lift_reintroduces_delta4_count": 0,
    "lower_variation_direct_six_template_lift_count": 0,
    "lower_variation_rank104_template_match_max": 2,
    "selected_lift_endpoint_9_count": 12,
    "selected_lift_endpoint_10_count": 4,
    "selected_lift_endpoint_11_count": 8,
    "selected_lift_endpoint_13_count": 0,
}


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


def table_rows(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def row_tuple(row: dict[str, int], columns: list[str]) -> tuple[int, ...]:
    return tuple(row[column] for column in columns)


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    obstruction = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction_certificate.json"
    )
    profiles_csv = (
        OUT_DIR / "aperture_closure_tail_lower_variation_profiles.csv"
    ).read_text(encoding="utf-8")
    templates_csv = (
        OUT_DIR / "aperture_closure_tail_lower_variation_templates.csv"
    ).read_text(encoding="utf-8")
    lift_edges_csv = (
        OUT_DIR / "aperture_closure_tail_lower_variation_lift_edges.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR / "aperture_closure_tail_lower_variation_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        obstruction
        != expected[
            "signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction"
        ]
    ):
        raise AssertionError("lower-variation lift obstruction JSON is not reproducible")
    if profiles_csv != expected["aperture_closure_tail_lower_variation_profiles_csv"]:
        raise AssertionError("lower-variation profiles CSV is not reproducible")
    if templates_csv != expected["aperture_closure_tail_lower_variation_templates_csv"]:
        raise AssertionError("lower-variation templates CSV is not reproducible")
    if lift_edges_csv != expected["aperture_closure_tail_lower_variation_lift_edges_csv"]:
        raise AssertionError("lower-variation lift edges CSV is not reproducible")
    if (
        observables_csv
        != expected["aperture_closure_tail_lower_variation_observables_csv"]
    ):
        raise AssertionError("lower-variation observables CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction_certificate"
        ]
    ):
        raise AssertionError("lower-variation lift obstruction certificate is not reproducible")

    for name in [
        "profile_table",
        "template_table",
        "lift_edge_table",
        "observable_table",
    ]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(
                f"lower-variation lift obstruction table {name} is not reproducible"
            )

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction@1":
        raise AssertionError("lower-variation lift obstruction report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("lower-variation lift obstruction layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("lower-variation lift obstruction all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("lower-variation lift obstruction checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("lower-variation lift obstruction report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("lower-variation lift obstruction report is not reproducible")

    profile_table = np.asarray(tables["profile_table"], dtype=np.int64)
    template_table = np.asarray(tables["template_table"], dtype=np.int64)
    lift_edge_table = np.asarray(tables["lift_edge_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if profile_table.shape != (3, len(PROFILE_COLUMNS)):
        raise AssertionError("lower-variation profile table shape mismatch")
    if template_table.shape != (11, len(TEMPLATE_COLUMNS)):
        raise AssertionError("lower-variation template table shape mismatch")
    if lift_edge_table.shape != (2, len(LIFT_EDGE_COLUMNS)):
        raise AssertionError("lower-variation lift edge table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("lower-variation observable table shape mismatch")

    profile_rows = table_rows(profile_table, PROFILE_COLUMNS)
    template_rows = table_rows(template_table, TEMPLATE_COLUMNS)
    lift_edge_rows = table_rows(lift_edge_table, LIFT_EDGE_COLUMNS)
    observable_rows = table_rows(observable_table, OBSERVABLE_COLUMNS)
    if [row_tuple(row, PROFILE_COLUMNS) for row in profile_rows] != EXPECTED_PROFILE_ROWS:
        raise AssertionError("lower-variation profile rows mismatch")
    if [row_tuple(row, TEMPLATE_COLUMNS) for row in template_rows] != EXPECTED_TEMPLATE_ROWS:
        raise AssertionError("lower-variation template rows mismatch")
    if [row_tuple(row, LIFT_EDGE_COLUMNS) for row in lift_edge_rows] != EXPECTED_LIFT_EDGE_ROWS:
        raise AssertionError("lower-variation lift edge rows mismatch")

    observables = {
        row["observable_code"]: row["value_x1e12"] // 10**12
        for row in observable_rows
    }
    expected_observables = {
        OBSERVABLE_CODES[key]: value for key, value in EXPECTED_OBSERVABLES.items()
    }
    if observables != expected_observables:
        raise AssertionError("lower-variation observables mismatch")

    selected_profile = next(
        row
        for row in profile_rows
        if row["splice_witness_id"] == SELECTED_SIX_TEMPLATE_WITNESS_ID
    )
    if selected_profile["trace_signature_total_variation"] != SELECTED_SIX_TEMPLATE_VARIATION:
        raise AssertionError("lower-variation selected lift variation mismatch")
    if selected_profile["normalized_tail_template_count"] != 6:
        raise AssertionError("lower-variation selected lift template count mismatch")
    if any(
        row["six_template_retention_flag"] == 1
        for row in profile_rows
        if row["trace_signature_total_variation"] < SELECTED_SIX_TEMPLATE_VARIATION
    ):
        raise AssertionError("lower-variation profile unexpectedly retains six templates")
    if sum(row["delta4_reintroduced_flag"] for row in lift_edge_rows) != 0:
        raise AssertionError("lower-variation lift reintroduced delta4")

    witness = report.get("witness", {})
    if witness.get("lower_variation_witness_ids") != [0, 1]:
        raise AssertionError("lower-variation witness ids mismatch")
    if witness.get("selected_six_template_lift_witness_id") != SELECTED_SIX_TEMPLATE_WITNESS_ID:
        raise AssertionError("lower-variation selected witness mismatch")
    if witness.get("selected_six_template_lift_word") != list(SELECTED_SIX_TEMPLATE_WORD):
        raise AssertionError("lower-variation selected word mismatch")
    if witness.get("selected_six_template_lift_trace") != list(SELECTED_SIX_TEMPLATE_TRACE):
        raise AssertionError("lower-variation selected trace mismatch")
    if witness.get("selected_six_template_lift_variation") != SELECTED_SIX_TEMPLATE_VARIATION:
        raise AssertionError("lower-variation selected variation mismatch")
    if witness.get("lift_gap_from_witness_0") != 26:
        raise AssertionError("lower-variation witness 0 lift gap mismatch")
    if witness.get("lift_gap_from_witness_1") != 24:
        raise AssertionError("lower-variation witness 1 lift gap mismatch")
    if obstruction.get("summary", {}).get("lift_reintroduces_delta4_count") != 0:
        raise AssertionError("lower-variation obstruction summary mismatch")
    if certificate.get("status") != STATUS:
        raise AssertionError("lower-variation certificate status mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("carrier_splice_report", {}), CARRIER_SPLICE_REPORT, "carrier splice report input")
    assert_file_hash(inputs.get("carrier_splice_json", {}), CARRIER_SPLICE_JSON, "carrier splice JSON input")
    assert_file_hash(inputs.get("carrier_splice_exact_witnesses", {}), CARRIER_SPLICE_EXACT_WITNESSES, "carrier splice exact witnesses input")
    assert_file_hash(inputs.get("carrier_splice_selected_templates", {}), CARRIER_SPLICE_SELECTED_TEMPLATES, "carrier splice selected templates input")
    assert_file_hash(inputs.get("carrier_splice_tables", {}), CARRIER_SPLICE_TABLES, "carrier splice tables input")
    assert_file_hash(inputs.get("carrier_splice_certificate", {}), CARRIER_SPLICE_CERTIFICATE, "carrier splice certificate input")
    assert_file_hash(inputs.get("carrier_splice_optimality_report", {}), CARRIER_SPLICE_OPTIMALITY_REPORT, "carrier splice optimality report input")
    assert_file_hash(inputs.get("carrier_splice_optimality_json", {}), CARRIER_SPLICE_OPTIMALITY_JSON, "carrier splice optimality JSON input")
    assert_file_hash(inputs.get("carrier_splice_optimality_frontier", {}), CARRIER_SPLICE_OPTIMALITY_FRONTIER, "carrier splice optimality frontier input")
    assert_file_hash(inputs.get("carrier_splice_optimality_classes", {}), CARRIER_SPLICE_OPTIMALITY_CLASSES, "carrier splice optimality classes input")
    assert_file_hash(inputs.get("carrier_splice_optimality_observables", {}), CARRIER_SPLICE_OPTIMALITY_OBSERVABLES, "carrier splice optimality observables input")
    assert_file_hash(inputs.get("carrier_splice_optimality_tables", {}), CARRIER_SPLICE_OPTIMALITY_TABLES, "carrier splice optimality tables input")
    assert_file_hash(inputs.get("carrier_splice_optimality_certificate", {}), CARRIER_SPLICE_OPTIMALITY_CERTIFICATE, "carrier splice optimality certificate input")
    assert_file_hash(inputs.get("endpoint_split_templates", {}), ENDPOINT_SPLIT_TEMPLATES, "endpoint split templates input")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script input")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator input")

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction_manifest@1":
        raise AssertionError("lower-variation lift obstruction manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("lower-variation lift obstruction manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("lower-variation lift obstruction manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("lower-variation lift obstruction missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("lower-variation lift obstruction index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("lower-variation lift obstruction index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    if CARRIER_SPLICE_OPTIMALITY_STATUS != "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_CARRIER_SPLICE_OPTIMALITY_CERTIFIED":
        raise AssertionError("carrier splice optimality status constant mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": witness,
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
