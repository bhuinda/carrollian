from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23rew import (
        CLASS_COLUMNS,
        CLASS_TEXT_HASH,
        DERIVE_SCRIPT,
        MATRIX_SHA256,
        MEMBER_COLUMNS,
        MEMBER_TEXT_HASH,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
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
    from derive_long_k23rew import (
        CLASS_COLUMNS,
        CLASS_TEXT_HASH,
        DERIVE_SCRIPT,
        MATRIX_SHA256,
        MEMBER_COLUMNS,
        MEMBER_TEXT_HASH,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from derive_long_raw import rows_from_table


EXPECTED_IDENTITY_CLASS = (0, 0, 10, 0, 2, 0, 1, 10, 0, 0, 0)
EXPECTED_FIRST_DEFECTIVE_CLASS = (1, 1, 1, 1, 1, 131728, 0, 0, 1, 0, 0)
EXPECTED_LAST_CLASS = (55, 85, 1, 2, 2, 141210, 0, 0, 1, 0, 0)


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


def class_tuple(row: dict[str, str]) -> tuple[int, ...]:
    return (
        int(row["class_id"]),
        int(row["representative_word_id"]),
        int(row["class_size"]),
        int(row["word_length_min"]),
        int(row["word_length_max"]),
        int(row["product_residual_nonzero_count"]),
        int(row["product_preserved_flag"]),
        int(row["product_preserved_member_count"]),
        int(row["defective_member_count"]),
        int(row["mixed_product_flag"]),
        int(row["closing_rewrite_exists_flag"]),
    )


def validate_long_k23rew() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23rew_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23rew seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23rew cert mismatch")
    for filename, key in {
        "class_rows.csv": "class_csv",
        "member_rows.csv": "member_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23rew {filename} mismatch")
    for key, expected_array in {
        "class_table": expected["class_table"],
        "member_table": expected["member_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23rew table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23rew matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23rew.report@1":
        raise AssertionError("long_k23rew report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23rew report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23rew all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23rew checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23rew report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23rew report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("class_rows.csv", CLASS_COLUMNS, 56),
        ("member_rows.csv", MEMBER_COLUMNS, 91),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23rew {filename} shape mismatch")

    assert_locked_hash(
        "class rows",
        hashlib.sha256(digest_text(CLASS_COLUMNS, csv_rows["class_rows.csv"]).encode("ascii")).hexdigest(),
        CLASS_TEXT_HASH,
    )
    assert_locked_hash(
        "member rows",
        hashlib.sha256(digest_text(MEMBER_COLUMNS, csv_rows["member_rows.csv"]).encode("ascii")).hexdigest(),
        MEMBER_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in ["class_table", "member_table", "observable_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "long_k23poly_certified_flag": 1,
        "word_count": 91,
        "carrier_class_count": 56,
        "singleton_class_count": 29,
        "pair_class_count": 26,
        "ten_class_count": 1,
        "product_preserved_class_count": 1,
        "defective_class_count": 55,
        "mixed_product_class_count": 0,
        "fingerprint_preserving_closing_rewrite_count": 0,
        "identity_class_size": 10,
        "identity_class_product_residual": 0,
        "defective_word_count": 81,
        "product_preserved_word_count": 10,
        "residual_fingerprint_count": 56,
        "word_depth": 2,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23rew observable {name} mismatch")

    class_rows = csv_rows["class_rows.csv"]
    if class_tuple(class_rows[0]) != EXPECTED_IDENTITY_CLASS:
        raise AssertionError("long_k23rew identity class mismatch")
    if class_tuple(class_rows[1]) != EXPECTED_FIRST_DEFECTIVE_CLASS:
        raise AssertionError("long_k23rew first defective class mismatch")
    if class_tuple(class_rows[-1]) != EXPECTED_LAST_CLASS:
        raise AssertionError("long_k23rew last class mismatch")
    if any(int(row["mixed_product_flag"]) for row in class_rows):
        raise AssertionError("long_k23rew unexpected mixed product class")
    if any(int(row["closing_rewrite_exists_flag"]) for row in class_rows):
        raise AssertionError("long_k23rew unexpected closing rewrite")
    preserved_classes = [row for row in class_rows if int(row["product_preserved_flag"])]
    if len(preserved_classes) != 1 or int(preserved_classes[0]["class_size"]) != 10:
        raise AssertionError("long_k23rew preserved class profile mismatch")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23rew index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator script")

    return {
        "schema": "long.k23rew.verification@1",
        "status": "PASS",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23rew(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
