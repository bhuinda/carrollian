from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_c59q import (
        BASIS_COLUMNS,
        DECISION_CODES,
        DECISION_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        INERTIA_COLUMNS,
        LONG_C59KT,
        LONG_C59ST,
        LONG_C59ST_KERNEL,
        LONG_C59ST_TENSOR,
        LONG_TIME_MAP_MATRIX,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        QUOTIENT_ENTRY_COLUMNS,
        STATUS,
        THEOREM_ID,
        build_payloads,
        exact_inertia,
        exact_rank,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_c59q import (
        BASIS_COLUMNS,
        DECISION_CODES,
        DECISION_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        INERTIA_COLUMNS,
        LONG_C59KT,
        LONG_C59ST,
        LONG_C59ST_KERNEL,
        LONG_C59ST_TENSOR,
        LONG_TIME_MAP_MATRIX,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        QUOTIENT_ENTRY_COLUMNS,
        STATUS,
        THEOREM_ID,
        build_payloads,
        exact_inertia,
        exact_rank,
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


def validate_long_c59q() -> dict[str, Any]:
    expected = build_payloads()
    c59q = load_json(OUT_DIR / "c59q.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if c59q != expected["c59q"]:
        raise AssertionError("long_c59q JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_c59q cert mismatch")
    for filename, key in {
        "basis.csv": "basis_csv",
        "quotient_entry.csv": "quotient_entry_csv",
        "inertia.csv": "inertia_csv",
        "decision.csv": "decision_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_c59q {filename} mismatch")

    for key, expected_array in {
        "basis_table": expected["basis_table"],
        "quotient_entry_table": expected["quotient_entry_table"],
        "inertia_table": expected["inertia_table"],
        "decision_table": expected["decision_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
        "quotient_matrix": expected["quotient_matrix"],
        "induced_q_table": expected["induced_q_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_c59q table mismatch: {key}")

    if report.get("schema") != "long.c59q.report@1":
        raise AssertionError("long_c59q report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_c59q report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_c59q all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_c59q checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59q report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_c59q report hash mismatch")

    csv_shapes = [
        ("basis.csv", BASIS_COLUMNS, 19),
        ("quotient_entry.csv", QUOTIENT_ENTRY_COLUMNS, 361),
        ("inertia.csv", INERTIA_COLUMNS, expected["inertia_table"].shape[0]),
        ("decision.csv", DECISION_COLUMNS, len(DECISION_CODES)),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_c59q {filename} shape mismatch")

    table_shapes = {
        "basis_table": (19, len(BASIS_COLUMNS)),
        "quotient_entry_table": (361, len(QUOTIENT_ENTRY_COLUMNS)),
        "inertia_table": (expected["inertia_table"].shape[0], len(INERTIA_COLUMNS)),
        "decision_table": (len(DECISION_CODES), len(DECISION_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
        "quotient_matrix": (19, 19),
        "induced_q_table": (1, 19),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_c59q {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 2,
        "input_certified_count": 2,
        "ambient_dimension": 20,
        "pivot_atom": 6,
        "gauge_kernel_support_count": 2,
        "quotient_dimension": 19,
        "quotient_entry_count": 361,
        "quotient_rank": 19,
        "quotient_nullity": 0,
        "inertia_positive_count": 11,
        "inertia_negative_count": 8,
        "inertia_zero_count": 0,
        "public_kernel_dimension": 19,
        "time_rank": 1,
        "quotient_dimension_matches_public_kernel_flag": 1,
        "induced_q_pub_rank": 1,
        "induced_q_pub_kernel_dimension": 18,
        "induced_time_survives_flag": 1,
        "public_kernel_boundary_identification_flag": 0,
        "one_plus_eighteen_split_flag": 1,
        "four_dimensional_metric_flag": 0,
        "physical_stress_energy_flag": 0,
        "smooth_metric_flag": 0,
        "thermal_gravity_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_c59q observable {key} mismatch")
    if obs[OBS_CODES["pivot_kernel_value"]] == 0:
        raise AssertionError("long_c59q pivot kernel value mismatch")
    if obs[OBS_CODES["active_quotient_pair_count"]] <= 0:
        raise AssertionError("long_c59q active pair count mismatch")

    basis_rows = rows_from_table(np.asarray(tables["basis_table"]), BASIS_COLUMNS)
    if [row["quotient_index"] for row in basis_rows] != list(range(19)):
        raise AssertionError("long_c59q basis order mismatch")
    if any(row["source_atom"] == 6 for row in basis_rows):
        raise AssertionError("long_c59q pivot atom present in basis")
    if sum(row["time_support_flag"] for row in basis_rows) != 1:
        raise AssertionError("long_c59q induced time support mismatch")

    matrix = np.asarray(tables["quotient_matrix"], dtype=np.int64)
    if not np.array_equal(matrix, matrix.T):
        raise AssertionError("long_c59q quotient symmetry mismatch")
    if exact_rank(matrix.tolist()) != 19:
        raise AssertionError("long_c59q exact quotient rank mismatch")
    positive, negative, zero, _rows = exact_inertia(matrix.tolist())
    if (positive, negative, zero) != (11, 8, 0):
        raise AssertionError("long_c59q exact inertia mismatch")

    quotient_entry_rows = rows_from_table(
        np.asarray(tables["quotient_entry_table"]), QUOTIENT_ENTRY_COLUMNS
    )
    if [row["entry_id"] for row in quotient_entry_rows] != list(range(361)):
        raise AssertionError("long_c59q quotient entry order mismatch")
    for row in quotient_entry_rows:
        if row["quotient_value"] != int(
            matrix[row["row_quotient_index"], row["col_quotient_index"]]
        ):
            raise AssertionError("long_c59q quotient entry matrix mismatch")
        if row["nonzero_flag"] != int(row["quotient_value"] != 0):
            raise AssertionError("long_c59q quotient entry nonzero mismatch")

    induced_q = np.asarray(tables["induced_q_table"], dtype=np.int64)[0]
    if int(np.count_nonzero(induced_q)) != 1:
        raise AssertionError("long_c59q induced q rank mismatch")

    inertia_rows = rows_from_table(np.asarray(tables["inertia_table"]), INERTIA_COLUMNS)
    if [row["pivot_id"] for row in inertia_rows] != list(range(len(inertia_rows))):
        raise AssertionError("long_c59q inertia order mismatch")
    if sum(row["positive_increment"] for row in inertia_rows) != 11:
        raise AssertionError("long_c59q inertia positive mismatch")
    if sum(row["negative_increment"] for row in inertia_rows) != 8:
        raise AssertionError("long_c59q inertia negative mismatch")
    if sum(row["zero_increment"] for row in inertia_rows) != 0:
        raise AssertionError("long_c59q inertia zero mismatch")

    decision_rows = rows_from_table(
        np.asarray(tables["decision_table"]), DECISION_COLUMNS
    )
    if [row["decision_id"] for row in decision_rows] != list(
        range(len(DECISION_CODES))
    ):
        raise AssertionError("long_c59q decision order mismatch")
    if [row["certified_flag"] for row in decision_rows] != [1, 1, 1, 1, 1, 1, 0, 1]:
        raise AssertionError("long_c59q decision certified vector mismatch")
    if [row["obstruction_flag"] for row in decision_rows] != [0, 0, 0, 0, 0, 0, 1, 0]:
        raise AssertionError("long_c59q decision obstruction vector mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 1, 1, 0, 0, 0, 0]:
        raise AssertionError("long_c59q gap certified vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 0, 0, 0, 1, 0, 0]:
        raise AssertionError("long_c59q gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_c59q manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_c59q manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59q manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_c59st": LONG_C59ST,
        "long_c59st_tensor": LONG_C59ST_TENSOR,
        "long_c59st_kernel": LONG_C59ST_KERNEL,
        "long_c59kt": LONG_C59KT,
        "long_time_map_matrix": LONG_TIME_MAP_MATRIX,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_c59q index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59q index report hash mismatch")

    return {
        "schema": "long.c59q.verification@1",
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
    print(json.dumps(validate_long_c59q(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
