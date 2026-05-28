from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality import (
        CARRIER_SPLICE_CERTIFICATE,
        CARRIER_SPLICE_EXACT_WITNESSES,
        CARRIER_SPLICE_JSON,
        CARRIER_SPLICE_OBSERVABLES,
        CARRIER_SPLICE_REPORT,
        CARRIER_SPLICE_SELECTED_TEMPLATES,
        CARRIER_SPLICE_TABLES,
        CLASS_COLUMNS,
        DERIVE_SCRIPT,
        FRONTIER_COLUMNS,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        SELECTED_SIX_TEMPLATE_TRACE,
        SELECTED_SIX_TEMPLATE_WORD,
        SELECTED_SPLICE_WITNESS_ID,
        SELECTED_VARIATION,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality import (
        CARRIER_SPLICE_CERTIFICATE,
        CARRIER_SPLICE_EXACT_WITNESSES,
        CARRIER_SPLICE_JSON,
        CARRIER_SPLICE_OBSERVABLES,
        CARRIER_SPLICE_REPORT,
        CARRIER_SPLICE_SELECTED_TEMPLATES,
        CARRIER_SPLICE_TABLES,
        CLASS_COLUMNS,
        DERIVE_SCRIPT,
        FRONTIER_COLUMNS,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        SELECTED_SIX_TEMPLATE_TRACE,
        SELECTED_SIX_TEMPLATE_WORD,
        SELECTED_SPLICE_WITNESS_ID,
        SELECTED_VARIATION,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )


EXPECTED_FRONTIER_ROWS = [
    (0, 12, 7, 2, 2, 197, 24, 192, 2, 12, 12, 0, 0, 24, 0, 1, 1, 0, 0, 1, 0),
    (1, 13, 8, 3, 2, 199, 24, 160, 3, 8, 8, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0),
    (2, 13, 8, 3, 2, 223, 24, 240, 6, 4, 4, 12, 4, 8, 0, 1, 1, 1, 1, 0, 1),
    (3, 13, 8, 3, 2, 229, 24, 160, 3, 8, 8, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0),
    (4, 13, 8, 3, 2, 229, 24, 160, 3, 8, 8, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0),
    (5, 13, 8, 3, 2, 249, 24, 160, 3, 8, 8, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0),
    (6, 13, 8, 3, 2, 255, 24, 480, 3, 8, 8, 0, 8, 16, 0, 1, 1, 0, 0, 0, 0),
    (7, 10, 5, 0, 2, 289, 24, 160, 3, 8, 8, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0),
    (8, 12, 7, 2, 2, 289, 24, 640, 3, 8, 8, 0, 8, 16, 1, 0, 0, 0, 0, 0, 0),
    (9, 12, 7, 2, 2, 301, 24, 192, 2, 12, 12, 0, 0, 24, 1, 0, 0, 0, 0, 0, 0),
    (10, 13, 8, 3, 2, 347, 24, 320, 3, 8, 8, 0, 8, 16, 1, 1, 0, 0, 0, 0, 0),
]
EXPECTED_CLASS_ROWS = [
    (0, 0, 11, 197, 347, 0, 1, 1, 2, 0),
    (1, 1, 5, 197, 255, 0, 1, 1, 2, 0),
    (2, 2, 1, 223, 223, 2, 1, 1, 0, 0),
    (3, 3, 1, 223, 223, 2, 1, 1, 0, 0),
    (4, 4, 2, 197, 199, 0, 0, 0, 2, 0),
    (5, 5, 1, 347, 347, 10, 0, 0, 0, 0),
]
EXPECTED_OBSERVABLES = {
    "exact_24_delta2_splice_count": 11,
    "selected_splice_witness_id": 2,
    "selected_variation": 223,
    "six_template_retention_exact_count": 1,
    "six_template_min_variation": 223,
    "six_template_lower_than_selected_count": 0,
    "lower_than_selected_exact_count": 2,
    "lower_than_selected_six_template_count": 0,
    "rank104_prefix_exact_count": 5,
    "shared_rewrite_tail_exact_count": 1,
    "both_repair_chords_exact_count": 1,
    "all_exact_min_variation": 197,
    "all_exact_min_variation_witness_id": 0,
    "selected_endpoint_9_count": 12,
    "selected_endpoint_10_count": 4,
    "selected_endpoint_11_count": 8,
    "selected_template_lift_count": 4,
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


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    optimality = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality_certificate.json"
    )
    frontier_csv = (
        OUT_DIR / "aperture_closure_tail_carrier_splice_frontier.csv"
    ).read_text(encoding="utf-8")
    classes_csv = (
        OUT_DIR / "aperture_closure_tail_carrier_splice_optimality_classes.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR / "aperture_closure_tail_carrier_splice_optimality_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        optimality
        != expected[
            "signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality"
        ]
    ):
        raise AssertionError("carrier-splice optimality JSON is not reproducible")
    if frontier_csv != expected["aperture_closure_tail_carrier_splice_frontier_csv"]:
        raise AssertionError("carrier-splice optimality frontier CSV is not reproducible")
    if (
        classes_csv
        != expected["aperture_closure_tail_carrier_splice_optimality_classes_csv"]
    ):
        raise AssertionError("carrier-splice optimality classes CSV is not reproducible")
    if (
        observables_csv
        != expected[
            "aperture_closure_tail_carrier_splice_optimality_observables_csv"
        ]
    ):
        raise AssertionError("carrier-splice optimality observables CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality_certificate"
        ]
    ):
        raise AssertionError("carrier-splice optimality certificate is not reproducible")

    for name in ["frontier_table", "class_table", "observable_table"]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(
                f"carrier-splice optimality table {name} is not reproducible"
            )

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality@1":
        raise AssertionError("carrier-splice optimality report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("carrier-splice optimality layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("carrier-splice optimality all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("carrier-splice optimality checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("carrier-splice optimality report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("carrier-splice optimality report is not reproducible")

    frontier_table = np.asarray(tables["frontier_table"], dtype=np.int64)
    class_table = np.asarray(tables["class_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if frontier_table.shape != (11, len(FRONTIER_COLUMNS)):
        raise AssertionError("carrier-splice optimality frontier shape mismatch")
    if class_table.shape != (6, len(CLASS_COLUMNS)):
        raise AssertionError("carrier-splice optimality class shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("carrier-splice optimality observable shape mismatch")

    frontier_rows = table_rows(frontier_table, FRONTIER_COLUMNS)
    class_rows = table_rows(class_table, CLASS_COLUMNS)
    observable_rows = table_rows(observable_table, OBSERVABLE_COLUMNS)
    if [row_tuple(row, FRONTIER_COLUMNS) for row in frontier_rows] != EXPECTED_FRONTIER_ROWS:
        raise AssertionError("carrier-splice optimality frontier rows mismatch")
    if [row_tuple(row, CLASS_COLUMNS) for row in class_rows] != EXPECTED_CLASS_ROWS:
        raise AssertionError("carrier-splice optimality class rows mismatch")
    observables = {
        row["observable_code"]: row["value_x1e12"] // 10**12
        for row in observable_rows
    }
    expected_observables = {
        OBSERVABLE_CODES[key]: value for key, value in EXPECTED_OBSERVABLES.items()
    }
    if observables != expected_observables:
        raise AssertionError("carrier-splice optimality observables mismatch")

    selected = next(
        row for row in frontier_rows if row["splice_witness_id"] == SELECTED_SPLICE_WITNESS_ID
    )
    if selected["trace_signature_total_variation"] != SELECTED_VARIATION:
        raise AssertionError("carrier-splice optimality selected variation mismatch")
    if selected["six_template_retention_flag"] != 1:
        raise AssertionError("carrier-splice optimality selected retention mismatch")
    if any(
        row["six_template_retention_flag"] == 1
        for row in frontier_rows
        if row["trace_signature_total_variation"] < SELECTED_VARIATION
    ):
        raise AssertionError("carrier-splice optimality lower retained row exists")
    if [row["splice_witness_id"] for row in frontier_rows if row["trace_signature_total_variation"] < SELECTED_VARIATION] != [0, 1]:
        raise AssertionError("carrier-splice optimality lower witness ids mismatch")

    witness = report.get("witness", {})
    if witness.get("selected_splice_witness_id") != SELECTED_SPLICE_WITNESS_ID:
        raise AssertionError("carrier-splice optimality witness id mismatch")
    if witness.get("selected_word") != list(SELECTED_SIX_TEMPLATE_WORD):
        raise AssertionError("carrier-splice optimality witness word mismatch")
    if witness.get("selected_trace") != list(SELECTED_SIX_TEMPLATE_TRACE):
        raise AssertionError("carrier-splice optimality witness trace mismatch")
    if witness.get("selected_variation") != SELECTED_VARIATION:
        raise AssertionError("carrier-splice optimality witness variation mismatch")
    if witness.get("lower_variation_exact_witness_ids") != [0, 1]:
        raise AssertionError("carrier-splice optimality lower witness mismatch")
    if witness.get("lower_variation_six_template_count") != 0:
        raise AssertionError("carrier-splice optimality lower retained count mismatch")
    if optimality.get("summary", {}).get("bounded_minimum_variation") != SELECTED_VARIATION:
        raise AssertionError("carrier-splice optimality summary mismatch")
    if certificate.get("status") != STATUS:
        raise AssertionError("carrier-splice optimality certificate status mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("carrier_splice_report", {}), CARRIER_SPLICE_REPORT, "carrier splice report input")
    assert_file_hash(inputs.get("carrier_splice_json", {}), CARRIER_SPLICE_JSON, "carrier splice JSON input")
    assert_file_hash(inputs.get("carrier_splice_exact_witnesses", {}), CARRIER_SPLICE_EXACT_WITNESSES, "carrier splice exact witnesses input")
    assert_file_hash(inputs.get("carrier_splice_selected_templates", {}), CARRIER_SPLICE_SELECTED_TEMPLATES, "carrier splice selected templates input")
    assert_file_hash(inputs.get("carrier_splice_observables", {}), CARRIER_SPLICE_OBSERVABLES, "carrier splice observables input")
    assert_file_hash(inputs.get("carrier_splice_tables", {}), CARRIER_SPLICE_TABLES, "carrier splice tables input")
    assert_file_hash(inputs.get("carrier_splice_certificate", {}), CARRIER_SPLICE_CERTIFICATE, "carrier splice certificate input")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script input")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator input")

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality_manifest@1":
        raise AssertionError("carrier-splice optimality manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("carrier-splice optimality manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("carrier-splice optimality manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("carrier-splice optimality missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("carrier-splice optimality index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("carrier-splice optimality index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": witness,
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
