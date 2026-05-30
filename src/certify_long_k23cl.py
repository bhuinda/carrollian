from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23cl import (
        CLOSURE_COLUMNS,
        CLOSURE_TEXT_HASH,
        DERIVE_SCRIPT,
        EXTENSION_COLUMNS,
        EXTENSION_TEXT_HASH,
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
    from derive_long_k23cl import (
        CLOSURE_COLUMNS,
        CLOSURE_TEXT_HASH,
        DERIVE_SCRIPT,
        EXTENSION_COLUMNS,
        EXTENSION_TEXT_HASH,
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


EXPECTED_ADDED_RELATIONS = [151, 152, 153, 154]
EXPECTED_EXTENSION_RESIDUALS = {
    0: (127469, 0, 802, 787),
    1: (128750, 0, 789, 769),
    2: (120874, 0, 741, 729),
    3: (127901, 0, 840, 822),
    4: (85902, 0, 441, 401),
    5: (84894, 0, 446, 408),
    6: (87495, 0, 519, 482),
    7: (98930, 0, 564, 526),
    8: (82229, 0, 402, 364),
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


def validate_long_k23cl() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23cl_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23cl seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23cl cert mismatch")
    for filename, key in {
        "closure_rows.csv": "closure_csv",
        "product_rows.csv": "product_csv",
        "pair_rows.csv": "pair_csv",
        "extension_rows.csv": "extension_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23cl {filename} mismatch")
    for key, expected_array in {
        "closure_table": expected["closure_table"],
        "product_table": expected["product_table"],
        "pair_table": expected["pair_table"],
        "extension_table": expected["extension_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23cl table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23cl matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23cl.report@1":
        raise AssertionError("long_k23cl report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23cl report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23cl all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23cl checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23cl report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23cl report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("closure_rows.csv", CLOSURE_COLUMNS, 60),
        ("product_rows.csv", PRODUCT_COLUMNS, 6579),
        ("pair_rows.csv", PAIR_COLUMNS, 2192),
        ("extension_rows.csv", EXTENSION_COLUMNS, 9),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23cl {filename} shape mismatch")

    assert_locked_hash(
        "closure rows",
        hashlib.sha256(digest_text(CLOSURE_COLUMNS, csv_rows["closure_rows.csv"]).encode("ascii")).hexdigest(),
        CLOSURE_TEXT_HASH,
    )
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
        "extension rows",
        hashlib.sha256(digest_text(EXTENSION_COLUMNS, csv_rows["extension_rows.csv"]).encode("ascii")).hexdigest(),
        EXTENSION_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in [
            "closure_product_tensor",
            "r_hc_lifts",
            "identity_extension_residual_vector",
            "observable_vector",
        ]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "long_k23mul_certified_flag": 1,
        "long_hcsupp_certified_flag": 1,
        "original_support_row_count": 56,
        "added_relation_count": 4,
        "closure_support_row_count": 60,
        "first_leak_target_count": 4,
        "raw_product_row_count": 6579,
        "inside_closure_product_row_count": 6579,
        "outside_closure_product_row_count": 0,
        "raw_product_coefficient_total": 14336,
        "projected_product_tensor_nonzero_count": 6579,
        "support_pair_count": 3600,
        "nonzero_pair_count": 2192,
        "zero_pair_count": 1408,
        "closed_pair_count": 2192,
        "leaking_pair_count": 0,
        "closure_product_closed_flag": 1,
        "current_r_hc_action_dimension": 56,
        "closure_action_dimension": 60,
        "missing_new_relation_action_count": 4,
        "identity_extension_tested_flag": 1,
        "identity_extension_preserving_generator_count": 0,
        "identity_extension_residual_nonzero_total": 944444,
        "identity_extension_residual_nonzero_min": 82229,
        "identity_extension_residual_nonzero_max": 128750,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23cl observable {name} mismatch")

    added_relations = [
        int(row["relation_id"])
        for row in csv_rows["closure_rows.csv"]
        if int(row["added_by_leak_flag"]) == 1
    ]
    if added_relations != EXPECTED_ADDED_RELATIONS:
        raise AssertionError("long_k23cl added relation list mismatch")

    for row in csv_rows["extension_rows.csv"]:
        generator_id = int(row["generator_id"])
        expected_tuple = EXPECTED_EXTENSION_RESIDUALS[generator_id]
        actual_tuple = (
            int(row["identity_extension_residual_nonzero_count"]),
            int(row["identity_extension_preserved_flag"]),
            int(row["identity_extension_nonzero_count"]),
            int(row["identity_extension_nonidentity_count"]),
        )
        if actual_tuple != expected_tuple:
            raise AssertionError(f"long_k23cl extension row mismatch: {generator_id}")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23cl index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator script")

    return {
        "schema": "long.k23cl.verification@1",
        "status": "PASS",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23cl(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
