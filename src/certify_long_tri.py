from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_tri import (
        DERIVE_SCRIPT,
        FRONT_COLUMNS,
        INDEX_PATH,
        LONG_KERN_REPORT,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        RAW_TENSOR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        WEAK_COLUMNS,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_tri import (
        DERIVE_SCRIPT,
        FRONT_COLUMNS,
        INDEX_PATH,
        LONG_KERN_REPORT,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        RAW_TENSOR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        WEAK_COLUMNS,
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


def validate_long_tri() -> dict[str, Any]:
    expected = build_payloads()
    tri = load_json(OUT_DIR / "tri.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if tri != expected["tri"]:
        raise AssertionError("long_tri JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_tri cert mismatch")
    if (OUT_DIR / "front.csv").read_text(encoding="utf-8") != expected["front_csv"]:
        raise AssertionError("long_tri front CSV mismatch")
    if (OUT_DIR / "weak.csv").read_text(encoding="utf-8") != expected["weak_csv"]:
        raise AssertionError("long_tri weak CSV mismatch")
    if (OUT_DIR / "obs.csv").read_text(encoding="utf-8") != expected["obs_csv"]:
        raise AssertionError("long_tri obs CSV mismatch")

    for key, expected_array in {
        "front_table": expected["front_table"],
        "weak_table": expected["weak_table"],
        "observable_table": expected["obs_table"],
        "frontier": expected["frontier"],
        "pair_count": expected["pair_count"],
        "pair_weight": expected["pair_weight"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_tri table mismatch: {key}")

    if report.get("schema") != "long.tri.report@1":
        raise AssertionError("long_tri report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_tri report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_tri all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_tri checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_tri report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_tri report hash mismatch")

    front_header, front_rows = read_csv(OUT_DIR / "front.csv")
    weak_header, weak_rows = read_csv(OUT_DIR / "weak.csv")
    if front_header != FRONT_COLUMNS or len(front_rows) != 985:
        raise AssertionError("long_tri front CSV shape mismatch")
    if weak_header != WEAK_COLUMNS or len(weak_rows) != 13:
        raise AssertionError("long_tri weak CSV shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "line_point_count": 985,
        "tensor_support_count": 1_414_965,
        "tensor_coeff_sum": 2_537_360,
        "tensor_coeff_square_sum": 8_119_976,
        "domain_word_count": 955_671_625,
        "source_pair_support_count": 198_029,
        "source_pair_empty_count": 772_196,
        "source_pair_fiber_min": 1,
        "source_pair_fiber_max": 48,
        "frontier_pair_count": 970_225,
        "frontier_none_count": 0,
        "frontier_min": 0,
        "frontier_max": 893,
        "closure_size": 551_559_917,
        "closure_extra": 550_144_952,
        "closure_domain_gap": 404_111_708,
        "closure_monotone_source0": 1,
        "closure_monotone_source1": 1,
        "closure_target_upward_flag": 1,
        "weak_order_class_count": 13,
        "weak_support_count_sum": 1_414_965,
        "weak_support_weight_sum": 2_537_360,
        "weak_support_square_sum": 8_119_976,
        "weak_closure_count_sum": 551_559_917,
        "long_kern_input_certified": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_tri observable {key} mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "raw_tensor": RAW_TENSOR,
        "long_kern_report": LONG_KERN_REPORT,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.tri.manifest@1":
        raise AssertionError("long_tri manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_tri manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_tri manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_tri missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_tri index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("long_tri index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.tri.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": {
            "line": witness.get("line"),
            "frontier": witness.get("frontier"),
            "closure": witness.get("closure"),
            "weak_order": {
                "class_count": witness.get("weak_order", {}).get("class_count"),
                "support_counts": witness.get("weak_order", {}).get("support_counts"),
                "closure_counts": witness.get("weak_order", {}).get("closure_counts"),
            },
            "finite_lln": witness.get("finite_lln"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_tri(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
