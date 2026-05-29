from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_kern import (
        AXIS_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_LLN_REPORT,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PAIR_COLUMNS,
        RAW_TENSOR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_kern import (
        AXIS_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_LLN_REPORT,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PAIR_COLUMNS,
        RAW_TENSOR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} is not a JSON object")
    return payload


def assert_file_hash(entry: dict[str, Any], expected_path: Path, label: str) -> None:
    expected_rel = expected_path.relative_to(ROOT).as_posix()
    if entry.get("path") != expected_rel:
        raise AssertionError(f"{label} path mismatch: {entry.get('path')}")
    if entry.get("sha256") != h_file(expected_path):
        raise AssertionError(f"{label} sha256 mismatch")


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def table_rows(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def validate_long_kern() -> dict[str, Any]:
    expected = build_payloads()
    kernel = load_json(OUT_DIR / "kernel.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if kernel != expected["kernel"]:
        raise AssertionError("long_kern kernel JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_kern cert mismatch")
    if (OUT_DIR / "axis.csv").read_text(encoding="utf-8") != expected["axis_csv"]:
        raise AssertionError("long_kern axis CSV mismatch")
    if (OUT_DIR / "pair.csv").read_text(encoding="utf-8") != expected["pair_csv"]:
        raise AssertionError("long_kern pair CSV mismatch")
    if (OUT_DIR / "obs.csv").read_text(encoding="utf-8") != expected["obs_csv"]:
        raise AssertionError("long_kern obs CSV mismatch")

    for key, expected_array in {
        "axis_table": expected["axis_table"],
        "pair_table": expected["pair_table"],
        "observable_table": expected["obs_table"],
        "pair_counts": expected["pair_counts"],
        "pair_weights": expected["pair_weights"],
        "closures": expected["closures"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_kern table mismatch: {key}")

    if report.get("schema") != "long.kern.report@1":
        raise AssertionError("long_kern report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_kern report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_kern all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_kern checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_kern report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_kern report hash mismatch")

    axis_header, axis_rows = read_csv(OUT_DIR / "axis.csv")
    pair_header, pair_rows = read_csv(OUT_DIR / "pair.csv")
    if axis_header != AXIS_COLUMNS or len(axis_rows) != 2_955:
        raise AssertionError("long_kern axis CSV shape mismatch")
    if pair_header != PAIR_COLUMNS or len(pair_rows) != 3:
        raise AssertionError("long_kern pair CSV shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required_flags = {
        "line_point_count": 985,
        "axis_count": 3,
        "pair_kernel_count": 3,
        "tensor_support_count": 1_414_965,
        "tensor_coeff_sum": 2_537_360,
        "axis_point_count_total": 4_244_895,
        "axis_point_weight_total": 7_612_080,
        "axis_all_points_seen": 1,
        "axis_prefix_suffix_monotone": 1,
        "axis_open_lln_flag": 1,
        "pair_weight_sum_total": 7_612_080,
        "pair_all_rows_seen": 1,
        "pair_all_cols_seen": 1,
        "pair_closure_profunctor_count": 3,
        "long_lln_input_certified": 1,
    }
    for key, value in required_flags.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_kern observable {key} mismatch")
    if obs.get(OBS_CODES["pair_closure_extra_total"], 0) <= 0:
        raise AssertionError("long_kern pair closure extra is not positive")

    inputs = report.get("inputs", {})
    for key, path in {
        "raw_tensor": RAW_TENSOR,
        "long_lln_report": LONG_LLN_REPORT,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.kern.manifest@1":
        raise AssertionError("long_kern manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_kern manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_kern manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_kern missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_kern index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("long_kern index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.kern.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": {
            "line": witness.get("line"),
            "support": witness.get("support"),
            "principal_open_lln": witness.get("principal_open_lln"),
            "kernel_summary": {
                "closure_extra_total": witness.get("kernels", {}).get("closure_extra_total"),
                "pair_count_sha256": witness.get("kernels", {}).get("pair_count_sha256"),
                "closure_sha256": witness.get("kernels", {}).get("closure_sha256"),
            },
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_kern(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
