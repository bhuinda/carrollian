from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_basis import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_KERN_REPORT,
        LONG_TRI_REPORT,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PAIR_BASIS_COLUMNS,
        RAW_TENSOR,
        STATUS,
        THEOREM_ID,
        TRI_BASIS_COLUMNS,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_basis import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_KERN_REPORT,
        LONG_TRI_REPORT,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PAIR_BASIS_COLUMNS,
        RAW_TENSOR,
        STATUS,
        THEOREM_ID,
        TRI_BASIS_COLUMNS,
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


def validate_long_basis() -> dict[str, Any]:
    expected = build_payloads()
    basis = load_json(OUT_DIR / "basis.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if basis != expected["basis"]:
        raise AssertionError("long_basis basis JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_basis cert mismatch")
    if (OUT_DIR / "tri_basis.csv").read_text(encoding="utf-8") != expected["tri_basis_csv"]:
        raise AssertionError("long_basis tri basis CSV mismatch")
    if (OUT_DIR / "pair_basis.csv").read_text(encoding="utf-8") != expected["pair_basis_csv"]:
        raise AssertionError("long_basis pair basis CSV mismatch")
    if (OUT_DIR / "obs.csv").read_text(encoding="utf-8") != expected["obs_csv"]:
        raise AssertionError("long_basis obs CSV mismatch")

    for key, expected_array in {
        "tri_basis_table": expected["tri_basis_table"],
        "pair_basis_table": expected["pair_basis_table"],
        "observable_table": expected["obs_table"],
        "basis_frontier": expected["basis_frontier"],
        "basis_pair_closures": expected["basis_pair_closures"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_basis table mismatch: {key}")

    if report.get("schema") != "long.basis.report@1":
        raise AssertionError("long_basis report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_basis report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_basis all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_basis checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_basis report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_basis report hash mismatch")

    tri_header, tri_rows = read_csv(OUT_DIR / "tri_basis.csv")
    pair_header, pair_rows = read_csv(OUT_DIR / "pair_basis.csv")
    if tri_header != TRI_BASIS_COLUMNS or len(tri_rows) != 259:
        raise AssertionError("long_basis tri basis CSV shape mismatch")
    if pair_header != PAIR_BASIS_COLUMNS or len(pair_rows) != 18:
        raise AssertionError("long_basis pair basis CSV shape mismatch")

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
        "tri_basis_count": 259,
        "tri_basis_weight_sum": 596,
        "tri_basis_square_sum": 5366,
        "tri_basis_source0_min": 118,
        "tri_basis_source0_max": 984,
        "tri_basis_source1_min": 714,
        "tri_basis_source1_max": 984,
        "tri_basis_target_min": 0,
        "tri_basis_target_max": 893,
        "tri_basis_output_support_count": 164,
        "tri_basis_output_max_multiplicity": 5,
        "tri_basis_regenerates_frontier": 1,
        "tri_basis_irredundant_flag": 1,
        "tri_frontier_pair_count": 970_225,
        "tri_frontier_min": 0,
        "tri_frontier_max": 893,
        "tri_closure_size": 551_559_917,
        "pair_basis_total": 18,
        "pair_basis_01_count": 6,
        "pair_basis_02_count": 6,
        "pair_basis_12_count": 6,
        "pair_basis_regenerates_pair_closures": 1,
        "pair_basis_irredundant_flag": 1,
        "long_tri_input_certified": 1,
        "long_kern_input_certified": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_basis observable {key} mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "raw_tensor": RAW_TENSOR,
        "long_kern_report": LONG_KERN_REPORT,
        "long_tri_report": LONG_TRI_REPORT,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.basis.manifest@1":
        raise AssertionError("long_basis manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_basis manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_basis manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_basis missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_basis index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("long_basis index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.basis.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": {
            "line": witness.get("line"),
            "ternary_basis": {
                "basis_count": witness.get("ternary_basis", {}).get("basis_count"),
                "basis_weight_sum": witness.get("ternary_basis", {}).get("basis_weight_sum"),
                "target_range": witness.get("ternary_basis", {}).get("target_range"),
                "regenerates_frontier": witness.get("ternary_basis", {}).get(
                    "regenerates_frontier"
                ),
                "irredundant": witness.get("ternary_basis", {}).get("irredundant"),
            },
            "pair_basis": witness.get("pair_basis"),
            "closure": witness.get("closure"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_basis(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
