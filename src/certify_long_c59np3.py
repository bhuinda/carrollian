from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_c59np3 import (
        CANDIDATE_COLUMNS,
        DECISION_CODES,
        DECISION_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        GRAM_COLUMNS,
        INDEX_PATH,
        LONG_C59PK,
        LONG_C59PK_BASIS,
        LONG_C59PK_RESTRICTED,
        LONG_C59S3,
        LONG_DIM4_GATE,
        LONG_SEL,
        MINOR_COLUMNS,
        MINOR_EXACT_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PLANE_COLUMNS,
        SEARCH_COLUMNS,
        STATUS,
        THEOREM_ID,
        VECTOR_COLUMNS,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_c59np3 import (
        CANDIDATE_COLUMNS,
        DECISION_CODES,
        DECISION_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        GRAM_COLUMNS,
        INDEX_PATH,
        LONG_C59PK,
        LONG_C59PK_BASIS,
        LONG_C59PK_RESTRICTED,
        LONG_C59S3,
        LONG_DIM4_GATE,
        LONG_SEL,
        MINOR_COLUMNS,
        MINOR_EXACT_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PLANE_COLUMNS,
        SEARCH_COLUMNS,
        STATUS,
        THEOREM_ID,
        VECTOR_COLUMNS,
        build_payloads,
        self_hash,
    )
    from derive_long_raw import rows_from_table


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} is not a JSON object")
    return payload


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def assert_file_hash(entry: dict[str, Any], expected_path: Path, label: str) -> None:
    expected_rel = expected_path.relative_to(ROOT).as_posix()
    if entry.get("path") != expected_rel:
        raise AssertionError(f"{label} path mismatch: {entry.get('path')}")
    if entry.get("sha256") != h_file(expected_path):
        raise AssertionError(f"{label} sha256 mismatch")


def determinant2(matrix: list[list[int]]) -> int:
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def determinant3(matrix: list[list[int]]) -> int:
    return (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def validate_long_c59np3() -> dict[str, Any]:
    expected = build_payloads()
    c59np3 = load_json(OUT_DIR / "c59np3.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if c59np3 != expected["c59np3"]:
        raise AssertionError("long_c59np3 JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_c59np3 cert mismatch")
    for filename, key in {
        "candidate.csv": "candidate_csv",
        "search.csv": "search_csv",
        "plane.csv": "plane_csv",
        "vector.csv": "vector_csv",
        "gram.csv": "gram_csv",
        "minor.csv": "minor_csv",
        "minor_exact.csv": "minor_exact_csv",
        "decision.csv": "decision_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_c59np3 {filename} mismatch")

    for key, expected_array in {
        "candidate_table": expected["candidate_table"],
        "search_table": expected["search_table"],
        "plane_table": expected["plane_table"],
        "vector_table": expected["vector_table"],
        "gram_table": expected["gram_table"],
        "minor_table": expected["minor_table"],
        "decision_table": expected["decision_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_c59np3 table mismatch: {key}")

    if report.get("schema") != "long.c59np3.report@1":
        raise AssertionError("long_c59np3 report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_c59np3 report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_c59np3 all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_c59np3 checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59np3 report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_c59np3 report hash mismatch")

    csv_shapes = [
        ("candidate.csv", CANDIDATE_COLUMNS, 324),
        ("search.csv", SEARCH_COLUMNS, 2),
        ("plane.csv", PLANE_COLUMNS, 2),
        ("vector.csv", VECTOR_COLUMNS, 12),
        ("gram.csv", GRAM_COLUMNS, 18),
        ("minor.csv", MINOR_COLUMNS, 6),
        ("minor_exact.csv", MINOR_EXACT_COLUMNS, 6),
        ("decision.csv", DECISION_COLUMNS, len(DECISION_CODES)),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_c59np3 {filename} shape mismatch")

    table_shapes = {
        "candidate_table": (324, len(CANDIDATE_COLUMNS)),
        "search_table": (2, len(SEARCH_COLUMNS)),
        "plane_table": (2, len(PLANE_COLUMNS)),
        "vector_table": (12, len(VECTOR_COLUMNS)),
        "gram_table": (18, len(GRAM_COLUMNS)),
        "minor_table": (6, len(MINOR_COLUMNS)),
        "decision_table": (len(DECISION_CODES), len(DECISION_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_c59np3 {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 4,
        "input_certified_count": 4,
        "restricted_dimension": 18,
        "candidate_family_size": 324,
        "positive_plane_found_flag": 1,
        "negative_plane_found_flag": 1,
        "nonprincipal_definite_plane_count": 2,
        "positive_plane_candidate_a": 20,
        "positive_plane_candidate_b": 54,
        "positive_plane_candidate_c": 153,
        "negative_plane_candidate_a": 21,
        "negative_plane_candidate_b": 55,
        "negative_plane_candidate_c": 171,
        "principal_positive_definite_count": 0,
        "principal_negative_definite_count": 0,
        "principal_only_candidate_boundary_retired_flag": 1,
        "physical_selector_axiom_flag": 0,
        "dim4_reduction_certified_flag": 0,
        "formal_nonprincipal_selector_flag": 1,
        "canonical_physical_selection_flag": 0,
        "four_dimensional_metric_flag": 0,
        "physical_stress_energy_flag": 0,
        "smooth_metric_flag": 0,
        "thermal_gravity_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_c59np3 observable {key} mismatch")

    candidate_rows = rows_from_table(
        np.asarray(tables["candidate_table"]), CANDIDATE_COLUMNS
    )
    if [row["candidate_id"] for row in candidate_rows] != list(range(324)):
        raise AssertionError("long_c59np3 candidate id order mismatch")
    if candidate_rows[20]["a_restricted_index"] != 0:
        raise AssertionError("long_c59np3 positive candidate 20 mismatch")
    if candidate_rows[20]["b_restricted_index"] != 2:
        raise AssertionError("long_c59np3 positive candidate 20 support mismatch")
    if candidate_rows[153]["a_restricted_index"] != 4:
        raise AssertionError("long_c59np3 positive candidate 153 mismatch")
    if candidate_rows[153]["b_coefficient"] != -1:
        raise AssertionError("long_c59np3 positive candidate 153 sign mismatch")

    search_rows = rows_from_table(np.asarray(tables["search_table"]), SEARCH_COLUMNS)
    if [row["candidate_a"] for row in search_rows] != [20, 21]:
        raise AssertionError("long_c59np3 search candidate_a mismatch")
    if [row["candidate_b"] for row in search_rows] != [54, 55]:
        raise AssertionError("long_c59np3 search candidate_b mismatch")
    if [row["candidate_c"] for row in search_rows] != [153, 171]:
        raise AssertionError("long_c59np3 search candidate_c mismatch")
    if any(row["lex_first_flag"] != 1 for row in search_rows):
        raise AssertionError("long_c59np3 search lex-first mismatch")

    plane_rows = rows_from_table(np.asarray(tables["plane_table"]), PLANE_COLUMNS)
    if [row["plane_id"] for row in plane_rows] != [0, 1]:
        raise AssertionError("long_c59np3 plane id order mismatch")
    if [row["nonprincipal_flag"] for row in plane_rows] != [1, 1]:
        raise AssertionError("long_c59np3 nonprincipal flag mismatch")
    if [row["coordinate_rank"] for row in plane_rows] != [3, 3]:
        raise AssertionError("long_c59np3 plane rank mismatch")
    if [row["coordinate_support_count"] for row in plane_rows] != [6, 6]:
        raise AssertionError("long_c59np3 support count mismatch")
    if [
        (
            row["inertia_positive"],
            row["inertia_negative"],
            row["inertia_zero"],
        )
        for row in plane_rows
    ] != [(3, 0, 0), (0, 3, 0)]:
        raise AssertionError("long_c59np3 plane inertia mismatch")

    gram_rows = rows_from_table(np.asarray(tables["gram_table"]), GRAM_COLUMNS)
    gram_by_plane: dict[int, list[list[int]]] = {}
    for plane_id in [0, 1]:
        matrix = [[0 for _ in range(3)] for _ in range(3)]
        for row in [item for item in gram_rows if item["plane_id"] == plane_id]:
            matrix[row["row_vector_id"]][row["col_vector_id"]] = row["gram_value"]
        gram_by_plane[plane_id] = matrix
    positive_gram = gram_by_plane[0]
    negative_gram = gram_by_plane[1]
    if positive_gram != [
        [5578631728, 2357260089, 0],
        [2357260089, 1436794764, 1004158646],
        [0, 1004158646, 5442054750],
    ]:
        raise AssertionError("long_c59np3 positive Gram mismatch")
    if negative_gram != [
        [-5578631728, -2357260089, 0],
        [-2357260089, -1436794764, 0],
        [0, 0, -9759376608],
    ]:
        raise AssertionError("long_c59np3 negative Gram mismatch")
    if not (
        positive_gram[0][0] > 0
        and determinant2([row[:2] for row in positive_gram[:2]]) > 0
        and determinant3(positive_gram) > 0
    ):
        raise AssertionError("long_c59np3 positive definiteness mismatch")
    if not (
        negative_gram[0][0] < 0
        and determinant2([row[:2] for row in negative_gram[:2]]) > 0
        and determinant3(negative_gram) < 0
    ):
        raise AssertionError("long_c59np3 negative definiteness mismatch")

    _minor_header, minor_exact_rows = read_csv(OUT_DIR / "minor_exact.csv")
    exact_by_key = {
        (int(row["plane_id"]), int(row["minor_order"])): int(row["minor_exact"])
        for row in minor_exact_rows
    }
    expected_exact = {
        (0, 1): positive_gram[0][0],
        (0, 2): determinant2([row[:2] for row in positive_gram[:2]]),
        (0, 3): determinant3(positive_gram),
        (1, 1): negative_gram[0][0],
        (1, 2): determinant2([row[:2] for row in negative_gram[:2]]),
        (1, 3): determinant3(negative_gram),
    }
    if exact_by_key != expected_exact:
        raise AssertionError("long_c59np3 exact minor mismatch")

    vector_rows = rows_from_table(np.asarray(tables["vector_table"]), VECTOR_COLUMNS)
    if len(vector_rows) != 12:
        raise AssertionError("long_c59np3 vector row count mismatch")
    if sorted({row["restricted_index"] for row in vector_rows if row["plane_id"] == 0}) != [
        0,
        1,
        2,
        3,
        4,
        10,
    ]:
        raise AssertionError("long_c59np3 positive vector support mismatch")
    if sorted({row["restricted_index"] for row in vector_rows if row["plane_id"] == 1}) != [
        0,
        1,
        2,
        3,
        5,
        7,
    ]:
        raise AssertionError("long_c59np3 negative vector support mismatch")

    decision_rows = rows_from_table(
        np.asarray(tables["decision_table"]), DECISION_COLUMNS
    )
    if [row["decision_id"] for row in decision_rows] != list(
        range(len(DECISION_CODES))
    ):
        raise AssertionError("long_c59np3 decision order mismatch")
    if [row["certified_flag"] for row in decision_rows] != [1, 1, 1, 0, 0, 0]:
        raise AssertionError("long_c59np3 decision certified vector mismatch")
    if [row["obstruction_flag"] for row in decision_rows] != [0, 0, 0, 1, 1, 1]:
        raise AssertionError("long_c59np3 decision obstruction vector mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 0, 0, 0, 0, 0]:
        raise AssertionError("long_c59np3 gap certified vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 1, 0, 0, 0, 0]:
        raise AssertionError("long_c59np3 gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_c59np3 manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_c59np3 manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59np3 manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_c59pk": LONG_C59PK,
        "long_c59pk_basis": LONG_C59PK_BASIS,
        "long_c59pk_restricted": LONG_C59PK_RESTRICTED,
        "long_c59s3": LONG_C59S3,
        "long_sel": LONG_SEL,
        "long_dim4_gate": LONG_DIM4_GATE,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_c59np3 index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59np3 index report hash mismatch")

    return {
        "schema": "long.c59np3.verification@1",
        "status": "PASS",
        "verified_report": str((OUT_DIR / "report.json").relative_to(ROOT)).replace(
            "\\", "/"
        ),
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "closure_boundary": report["closure_boundary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_c59np3(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
