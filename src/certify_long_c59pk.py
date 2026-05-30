from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_c59pk import (
        DECISION_CODES,
        DECISION_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        INERTIA_COLUMNS,
        LONG_C59Q,
        LONG_C59Q_BASIS,
        LONG_C59Q_QUOTIENT,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        RESTRICTED_ENTRY_COLUMNS,
        RESTRICT_BASIS_COLUMNS,
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
    from derive_long_c59pk import (
        DECISION_CODES,
        DECISION_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        INERTIA_COLUMNS,
        LONG_C59Q,
        LONG_C59Q_BASIS,
        LONG_C59Q_QUOTIENT,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        RESTRICTED_ENTRY_COLUMNS,
        RESTRICT_BASIS_COLUMNS,
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


def validate_long_c59pk() -> dict[str, Any]:
    expected = build_payloads()
    c59pk = load_json(OUT_DIR / "c59pk.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if c59pk != expected["c59pk"]:
        raise AssertionError("long_c59pk JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_c59pk cert mismatch")
    for filename, key in {
        "restrict_basis.csv": "restrict_basis_csv",
        "restricted_entry.csv": "restricted_entry_csv",
        "inertia.csv": "inertia_csv",
        "decision.csv": "decision_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_c59pk {filename} mismatch")

    for key, expected_array in {
        "restrict_basis_table": expected["restrict_basis_table"],
        "restricted_entry_table": expected["restricted_entry_table"],
        "inertia_table": expected["inertia_table"],
        "decision_table": expected["decision_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
        "restricted_matrix": expected["restricted_matrix"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_c59pk table mismatch: {key}")

    if report.get("schema") != "long.c59pk.report@1":
        raise AssertionError("long_c59pk report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_c59pk report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_c59pk all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_c59pk checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59pk report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_c59pk report hash mismatch")

    csv_shapes = [
        ("restrict_basis.csv", RESTRICT_BASIS_COLUMNS, 18),
        ("restricted_entry.csv", RESTRICTED_ENTRY_COLUMNS, 324),
        ("inertia.csv", INERTIA_COLUMNS, expected["inertia_table"].shape[0]),
        ("decision.csv", DECISION_COLUMNS, len(DECISION_CODES)),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_c59pk {filename} shape mismatch")

    table_shapes = {
        "restrict_basis_table": (18, len(RESTRICT_BASIS_COLUMNS)),
        "restricted_entry_table": (324, len(RESTRICTED_ENTRY_COLUMNS)),
        "inertia_table": (expected["inertia_table"].shape[0], len(INERTIA_COLUMNS)),
        "decision_table": (len(DECISION_CODES), len(DECISION_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
        "restricted_matrix": (18, 18),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_c59pk {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 1,
        "input_certified_count": 1,
        "quotient_dimension": 19,
        "induced_q_pub_rank": 1,
        "restricted_dimension": 18,
        "restricted_entry_count": 324,
        "restricted_rank": 18,
        "restricted_nullity": 0,
        "inertia_positive_count": 10,
        "inertia_negative_count": 8,
        "inertia_zero_count": 0,
        "time_trace_removed_flag": 1,
        "three_spatial_rank_flag": 0,
        "four_dimensional_metric_flag": 0,
        "physical_stress_energy_flag": 0,
        "smooth_metric_flag": 0,
        "thermal_gravity_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_c59pk observable {key} mismatch")
    if obs[OBS_CODES["active_restricted_pair_count"]] <= 0:
        raise AssertionError("long_c59pk active pair count mismatch")

    basis_rows = rows_from_table(
        np.asarray(tables["restrict_basis_table"]), RESTRICT_BASIS_COLUMNS
    )
    if [row["restricted_index"] for row in basis_rows] != list(range(18)):
        raise AssertionError("long_c59pk basis order mismatch")
    if any(row["q_pub_value"] != 0 for row in basis_rows):
        raise AssertionError("long_c59pk q_pub basis mismatch")
    if any(row["induced_kernel_flag"] != 1 for row in basis_rows):
        raise AssertionError("long_c59pk kernel basis flag mismatch")

    matrix = np.asarray(tables["restricted_matrix"], dtype=np.int64)
    if not np.array_equal(matrix, matrix.T):
        raise AssertionError("long_c59pk restricted symmetry mismatch")
    if exact_rank(matrix.tolist()) != 18:
        raise AssertionError("long_c59pk exact rank mismatch")
    positive, negative, zero, _rows = exact_inertia(matrix.tolist())
    if (positive, negative, zero) != (10, 8, 0):
        raise AssertionError("long_c59pk exact inertia mismatch")

    entry_rows = rows_from_table(
        np.asarray(tables["restricted_entry_table"]), RESTRICTED_ENTRY_COLUMNS
    )
    if [row["entry_id"] for row in entry_rows] != list(range(324)):
        raise AssertionError("long_c59pk entry order mismatch")
    for row in entry_rows:
        if row["restricted_value"] != int(
            matrix[row["row_restricted_index"], row["col_restricted_index"]]
        ):
            raise AssertionError("long_c59pk entry matrix mismatch")
        if row["nonzero_flag"] != int(row["restricted_value"] != 0):
            raise AssertionError("long_c59pk entry nonzero mismatch")

    inertia_rows = rows_from_table(np.asarray(tables["inertia_table"]), INERTIA_COLUMNS)
    if [row["pivot_id"] for row in inertia_rows] != list(range(len(inertia_rows))):
        raise AssertionError("long_c59pk inertia order mismatch")
    if sum(row["positive_increment"] for row in inertia_rows) != 10:
        raise AssertionError("long_c59pk inertia positive mismatch")
    if sum(row["negative_increment"] for row in inertia_rows) != 8:
        raise AssertionError("long_c59pk inertia negative mismatch")
    if sum(row["zero_increment"] for row in inertia_rows) != 0:
        raise AssertionError("long_c59pk inertia zero mismatch")

    decision_rows = rows_from_table(
        np.asarray(tables["decision_table"]), DECISION_COLUMNS
    )
    if [row["decision_id"] for row in decision_rows] != list(
        range(len(DECISION_CODES))
    ):
        raise AssertionError("long_c59pk decision order mismatch")
    if [row["certified_flag"] for row in decision_rows] != [1, 1, 1, 1, 0, 0]:
        raise AssertionError("long_c59pk decision certified vector mismatch")
    if [row["obstruction_flag"] for row in decision_rows] != [0, 0, 0, 0, 1, 1]:
        raise AssertionError("long_c59pk decision obstruction vector mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 1, 0, 0, 0, 0]:
        raise AssertionError("long_c59pk gap certified vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 0, 1, 0, 0, 0]:
        raise AssertionError("long_c59pk gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_c59pk manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_c59pk manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59pk manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_c59q": LONG_C59Q,
        "long_c59q_basis": LONG_C59Q_BASIS,
        "long_c59q_quotient": LONG_C59Q_QUOTIENT,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_c59pk index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59pk index report hash mismatch")

    return {
        "schema": "long.c59pk.verification@1",
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
    print(json.dumps(validate_long_c59pk(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
