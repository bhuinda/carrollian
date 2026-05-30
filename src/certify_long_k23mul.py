from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23mul import (
        DERIVE_SCRIPT,
        GENERATOR_COLUMNS,
        GENERATOR_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        PAIR_COLUMNS,
        PAIR_TEXT_HASH,
        PRODUCT_COLUMNS,
        PRODUCT_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_k23mul import (
        DERIVE_SCRIPT,
        GENERATOR_COLUMNS,
        GENERATOR_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        PAIR_COLUMNS,
        PAIR_TEXT_HASH,
        PRODUCT_COLUMNS,
        PRODUCT_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from derive_long_raw import rows_from_table


EXPECTED_GENERATOR_RESIDUALS = {
    0: (126508, 0, 798, 787),
    1: (127386, 0, 785, 769),
    2: (119638, 0, 737, 729),
    3: (126830, 0, 836, 822),
    4: (85096, 0, 437, 401),
    5: (84139, 0, 442, 408),
    6: (87136, 0, 515, 482),
    7: (98299, 0, 560, 526),
    8: (81629, 0, 398, 364),
}


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


def assert_locked_hash(label: str, actual: str, expected: str) -> None:
    if not expected:
        raise AssertionError(f"{label} witness hash is not locked")
    if actual != expected:
        raise AssertionError(f"{label} witness hash mismatch")


def validate_long_k23mul() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23mul_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23mul seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23mul cert mismatch")
    for filename, key in {
        "product_rows.csv": "product_csv",
        "pair_rows.csv": "pair_csv",
        "generator_rows.csv": "generator_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23mul {filename} mismatch")
    for key, expected_array in {
        "product_table": expected["product_table"],
        "pair_table": expected["pair_table"],
        "generator_table": expected["generator_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23mul table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23mul matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23mul.report@1":
        raise AssertionError("long_k23mul report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23mul report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23mul all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23mul checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23mul report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23mul report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("product_rows.csv", PRODUCT_COLUMNS, 6272),
        ("pair_rows.csv", PAIR_COLUMNS, 2080),
        ("generator_rows.csv", GENERATOR_COLUMNS, 9),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23mul {filename} shape mismatch")

    assert_locked_hash(
        "product rows",
        hashlib.sha256(digest_text(PRODUCT_COLUMNS, csv_rows["product_rows.csv"]).encode("ascii")).hexdigest(),
        PRODUCT_TEXT_HASH,
    )
    assert_locked_hash(
        "pair rows",
        hashlib.sha256(digest_text(PAIR_COLUMNS, csv_rows["pair_rows.csv"]).encode("ascii")).hexdigest(),
        PAIR_TEXT_HASH,
    )
    assert_locked_hash(
        "generator rows",
        hashlib.sha256(digest_text(GENERATOR_COLUMNS, csv_rows["generator_rows.csv"]).encode("ascii")).hexdigest(),
        GENERATOR_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in [
            "projected_product_tensor",
            "r_hc_lifts",
            "generator_residual_vector",
            "observable_vector",
        ]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "long_k23op_certified_flag": 1,
        "long_hcsupp_certified_flag": 1,
        "support_row_count": 56,
        "support_pair_count": 3136,
        "nonzero_pair_count": 2080,
        "zero_pair_count": 1056,
        "closed_pair_count": 2020,
        "leaking_pair_count": 60,
        "raw_support_product_row_count": 6272,
        "inside_support_product_row_count": 6204,
        "outside_support_product_row_count": 68,
        "raw_support_product_coefficient_total": 11976,
        "inside_support_product_coefficient_total": 11872,
        "outside_support_product_coefficient_total": 104,
        "projected_product_tensor_nonzero_count": 6204,
        "support_product_closed_flag": 0,
        "generator_count": 9,
        "projected_product_preserving_generator_count": 0,
        "projected_product_residual_nonzero_total": 936661,
        "projected_product_residual_nonzero_min": 81629,
        "projected_product_residual_nonzero_max": 127386,
        "projected_product_obstruction_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23mul observable {name} mismatch")

    for row in csv_rows["generator_rows.csv"]:
        generator_id = int(row["generator_id"])
        expected_tuple = EXPECTED_GENERATOR_RESIDUALS[generator_id]
        actual_tuple = (
            int(row["projected_product_residual_nonzero_count"]),
            int(row["projected_product_preserved_flag"]),
            int(row["source_lift_nonzero_count"]),
            int(row["source_lift_nonidentity_count"]),
        )
        if actual_tuple != expected_tuple:
            raise AssertionError(f"long_k23mul generator row mismatch: {generator_id}")

    outside_product_rows = sum(int(row["inside_support_flag"] == "0") for row in csv_rows["product_rows.csv"])
    if outside_product_rows != 68:
        raise AssertionError("long_k23mul outside product row count mismatch")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23mul index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator script")

    return {
        "schema": "long.k23mul.verification@1",
        "status": "PASS",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23mul(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
