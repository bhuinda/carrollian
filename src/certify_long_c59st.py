from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_c59st import (
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        INERTIA_COLUMNS,
        KERNEL_COLUMNS,
        LONG_C59CF,
        LONG_C59CF_CORRECTED_EDGE,
        LONG_C59CF_CORRECTED_NODE,
        LONG_METRIC_RANK_GATE,
        METRIC_CODES,
        METRIC_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PAIR_COLUMNS,
        STATUS,
        TENSOR_ENTRY_COLUMNS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_c59st import (
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        INERTIA_COLUMNS,
        KERNEL_COLUMNS,
        LONG_C59CF,
        LONG_C59CF_CORRECTED_EDGE,
        LONG_C59CF_CORRECTED_NODE,
        LONG_METRIC_RANK_GATE,
        METRIC_CODES,
        METRIC_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PAIR_COLUMNS,
        STATUS,
        TENSOR_ENTRY_COLUMNS,
        THEOREM_ID,
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


def validate_long_c59st() -> dict[str, Any]:
    expected = build_payloads()
    c59st = load_json(OUT_DIR / "c59st.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if c59st != expected["c59st"]:
        raise AssertionError("long_c59st JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_c59st cert mismatch")
    for filename, key in {
        "tensor_entry.csv": "tensor_entry_csv",
        "pair.csv": "pair_csv",
        "kernel.csv": "kernel_csv",
        "inertia.csv": "inertia_csv",
        "metric.csv": "metric_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_c59st {filename} mismatch")

    for key, expected_array in {
        "tensor_entry_table": expected["tensor_entry_table"],
        "pair_table": expected["pair_table"],
        "kernel_table": expected["kernel_table"],
        "inertia_table": expected["inertia_table"],
        "metric_table": expected["metric_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
        "symmetric_matrix": expected["symmetric_matrix"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_c59st table mismatch: {key}")

    if report.get("schema") != "long.c59st.report@1":
        raise AssertionError("long_c59st report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_c59st report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_c59st all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_c59st checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59st report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_c59st report hash mismatch")

    csv_shapes = [
        ("tensor_entry.csv", TENSOR_ENTRY_COLUMNS, 400),
        ("pair.csv", PAIR_COLUMNS, 190),
        ("kernel.csv", KERNEL_COLUMNS, 20),
        (
            "inertia.csv",
            INERTIA_COLUMNS,
            expected["inertia_table"].shape[0],
        ),
        ("metric.csv", METRIC_COLUMNS, len(METRIC_CODES)),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_c59st {filename} shape mismatch")

    table_shapes = {
        "tensor_entry_table": (400, len(TENSOR_ENTRY_COLUMNS)),
        "pair_table": (190, len(PAIR_COLUMNS)),
        "kernel_table": (20, len(KERNEL_COLUMNS)),
        "inertia_table": (expected["inertia_table"].shape[0], len(INERTIA_COLUMNS)),
        "metric_table": (len(METRIC_CODES), len(METRIC_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
        "symmetric_matrix": (20, 20),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_c59st {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 2,
        "input_certified_count": 2,
        "stress_node_count": 20,
        "directed_edge_count": 100,
        "tensor_entry_count": 400,
        "pair_row_count": 190,
        "active_pair_count": 40,
        "symmetric_tensor_flag": 1,
        "diagonal_zero_count": 20,
        "conserved_node_count": 20,
        "tensor_rank": 19,
        "tensor_nullity": 1,
        "inertia_positive_count": 11,
        "inertia_negative_count": 8,
        "inertia_zero_count": 1,
        "public_kernel_dimension": 19,
        "time_rank": 1,
        "rank_matches_public_kernel_flag": 1,
        "nullity_matches_time_rank_flag": 1,
        "kernel_support_count": 2,
        "kernel_time_identification_flag": 0,
        "lorentzian_signature_flag": 0,
        "four_dimensional_metric_flag": 0,
        "finite_stress_candidate_flag": 1,
        "physical_stress_energy_flag": 0,
        "smooth_metric_flag": 0,
        "thermal_gravity_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_c59st observable {key} mismatch")

    tensor_rows = rows_from_table(
        np.asarray(tables["tensor_entry_table"]), TENSOR_ENTRY_COLUMNS
    )
    if [row["entry_id"] for row in tensor_rows] != list(range(400)):
        raise AssertionError("long_c59st tensor entry order mismatch")
    matrix = np.asarray(tables["symmetric_matrix"], dtype=np.int64)
    if not np.array_equal(matrix, matrix.T):
        raise AssertionError("long_c59st symmetric matrix mismatch")
    if any(int(matrix[index, index]) != 0 for index in range(20)):
        raise AssertionError("long_c59st diagonal mismatch")
    for row in tensor_rows:
        atom_i = row["row_atom"]
        atom_j = row["col_atom"]
        if row["symmetric_flux_scaled"] != int(matrix[atom_i, atom_j]):
            raise AssertionError("long_c59st tensor row matrix mismatch")
        if row["symmetric_flux_scaled"] != row["directed_flux_scaled"] + row[
            "transpose_flux_scaled"
        ]:
            raise AssertionError("long_c59st tensor symmetrization mismatch")
        if row["nonzero_flag"] != int(row["symmetric_flux_scaled"] != 0):
            raise AssertionError("long_c59st tensor nonzero flag mismatch")

    pair_rows = rows_from_table(np.asarray(tables["pair_table"]), PAIR_COLUMNS)
    if [row["pair_id"] for row in pair_rows] != list(range(190)):
        raise AssertionError("long_c59st pair order mismatch")
    if sum(row["symmetric_nonzero_flag"] for row in pair_rows) != 40:
        raise AssertionError("long_c59st active pair count mismatch")
    for row in pair_rows:
        if row["symmetric_flux_scaled"] != row["forward_flux_scaled"] + row[
            "reverse_flux_scaled"
        ]:
            raise AssertionError("long_c59st pair symmetrization mismatch")
        if row["abs_symmetric_flux_scaled"] != abs(row["symmetric_flux_scaled"]):
            raise AssertionError("long_c59st pair abs mismatch")
        if row["directed_support_count"] != int(row["forward_flux_scaled"] != 0) + int(
            row["reverse_flux_scaled"] != 0
        ):
            raise AssertionError("long_c59st pair support mismatch")

    kernel_rows = rows_from_table(np.asarray(tables["kernel_table"]), KERNEL_COLUMNS)
    kernel = np.asarray([row["kernel_value"] for row in kernel_rows], dtype=object)
    if [row["atom_id"] for row in kernel_rows] != list(range(20)):
        raise AssertionError("long_c59st kernel order mismatch")
    if sum(row["kernel_nonzero_flag"] for row in kernel_rows) != 2:
        raise AssertionError("long_c59st kernel support mismatch")
    product = matrix.astype(object).dot(kernel)
    if any(int(value) != 0 for value in product):
        raise AssertionError("long_c59st kernel vector mismatch")

    inertia_rows = rows_from_table(np.asarray(tables["inertia_table"]), INERTIA_COLUMNS)
    if [row["pivot_id"] for row in inertia_rows] != list(range(len(inertia_rows))):
        raise AssertionError("long_c59st inertia order mismatch")
    if sum(row["positive_increment"] for row in inertia_rows) != 11:
        raise AssertionError("long_c59st inertia positive mismatch")
    if sum(row["negative_increment"] for row in inertia_rows) != 8:
        raise AssertionError("long_c59st inertia negative mismatch")
    if sum(row["zero_increment"] for row in inertia_rows) != 1:
        raise AssertionError("long_c59st inertia zero mismatch")

    metric_rows = rows_from_table(np.asarray(tables["metric_table"]), METRIC_COLUMNS)
    if [row["metric_row_id"] for row in metric_rows] != list(range(len(METRIC_CODES))):
        raise AssertionError("long_c59st metric order mismatch")
    certified_vector = [row["certified_flag"] for row in metric_rows]
    obstruction_vector = [row["obstruction_flag"] for row in metric_rows]
    if certified_vector != [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0]:
        raise AssertionError("long_c59st metric certified vector mismatch")
    if obstruction_vector != [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1]:
        raise AssertionError("long_c59st metric obstruction vector mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 1, 1, 0, 0, 0, 0]:
        raise AssertionError("long_c59st gap certified vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 0, 0, 1, 0, 0, 0]:
        raise AssertionError("long_c59st gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_c59st manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_c59st manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59st manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_c59cf": LONG_C59CF,
        "long_c59cf_corrected_edge": LONG_C59CF_CORRECTED_EDGE,
        "long_c59cf_corrected_node": LONG_C59CF_CORRECTED_NODE,
        "long_metric_rank_gate": LONG_METRIC_RANK_GATE,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_c59st index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59st index report hash mismatch")

    return {
        "schema": "long.c59st.verification@1",
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
    print(json.dumps(validate_long_c59st(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
