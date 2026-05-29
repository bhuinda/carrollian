from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_lln import (
        ADDR_COLUMNS,
        CHAIN_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LLN_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        RAW_TENSOR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_lln import (
        ADDR_COLUMNS,
        CHAIN_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LLN_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
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


def validate_long_lln() -> dict[str, Any]:
    expected = build_payloads()
    line = load_json(OUT_DIR / "line.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if line != expected["line"]:
        raise AssertionError("long_lln line JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_lln cert mismatch")
    if (OUT_DIR / "addr.csv").read_text(encoding="utf-8") != expected["addr_csv"]:
        raise AssertionError("long_lln addr CSV mismatch")
    if (OUT_DIR / "chain.csv").read_text(encoding="utf-8") != expected["chain_csv"]:
        raise AssertionError("long_lln chain CSV mismatch")
    if (OUT_DIR / "lln.csv").read_text(encoding="utf-8") != expected["lln_csv"]:
        raise AssertionError("long_lln LLN CSV mismatch")
    if (OUT_DIR / "obs.csv").read_text(encoding="utf-8") != expected["obs_csv"]:
        raise AssertionError("long_lln obs CSV mismatch")

    for key, expected_array in {
        "zeta": expected["zeta"],
        "mobius": expected["mobius"],
        "addr_table": expected["addr_table"],
        "chain_table": expected["chain_table"],
        "lln_table": expected["lln_table"],
        "observable_table": expected["obs_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_lln table mismatch: {key}")

    if report.get("schema") != "long.lln.report@1":
        raise AssertionError("long_lln report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_lln report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_lln all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_lln checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_lln report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_lln report hash mismatch")

    addr_header, addr_rows = read_csv(OUT_DIR / "addr.csv")
    chain_header, chain_rows = read_csv(OUT_DIR / "chain.csv")
    lln_header, lln_rows = read_csv(OUT_DIR / "lln.csv")
    if addr_header != ADDR_COLUMNS or len(addr_rows) != 985:
        raise AssertionError("long_lln addr CSV shape mismatch")
    if chain_header != CHAIN_COLUMNS or len(chain_rows) != 7:
        raise AssertionError("long_lln chain CSV shape mismatch")
    if lln_header != LLN_COLUMNS or len(lln_rows) != 8:
        raise AssertionError("long_lln LLN CSV shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "line_point_count": 985,
        "line_open_count": 986,
        "line_closed_count": 986,
        "line_interval_count": 485_605,
        "tensor_support_count": 1_414_965,
        "tensor_domain_word_count": 955_671_625,
        "tensor_coeff_sum": 2_537_360,
        "tensor_coeff_square_sum": 8_119_976,
        "tensor_coeff_min": 1,
        "tensor_coeff_max": 64,
        "tensor_address_columns_cover_line": 1,
        "tensor_lookup_positive": 1,
        "zeta_nonzero_count": 485_605,
        "mobius_nonzero_count": 1_969,
        "zeta_boolean_idempotent": 1,
        "mobius_inverse_flag": 1,
        "marginals_sum_to_support": 1,
        "weighted_marginals_sum_to_coeff_sum": 1,
        "centered_lookup_sum_zero": 1,
        "finite_lln_formula_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_lln observable {key} mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "raw_tensor": RAW_TENSOR,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.lln.manifest@1":
        raise AssertionError("long_lln manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_lln manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_lln manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_lln missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_lln index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("long_lln index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.lln.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": {
            "line": witness.get("line"),
            "tensor_lookup": witness.get("tensor_lookup"),
            "finite_lln": witness.get("finite_lln"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_lln(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
