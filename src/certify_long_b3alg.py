from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_b3alg import (
        B3MOD_CLASS_CSV,
        B3MOD_PERMCHAR_CSV,
        B3MOD_REPORT,
        CLASS_COLUMNS,
        COORIENT_NPZ,
        EXPECTED_GROUP_ORDER,
        EXPECTED_POINTS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_KR39,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PRODUCT_COLUMNS,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_b3alg import (
        B3MOD_CLASS_CSV,
        B3MOD_PERMCHAR_CSV,
        B3MOD_REPORT,
        CLASS_COLUMNS,
        COORIENT_NPZ,
        EXPECTED_GROUP_ORDER,
        EXPECTED_POINTS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_KR39,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PRODUCT_COLUMNS,
        STATUS,
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


def validate_long_b3alg() -> dict[str, Any]:
    expected = build_payloads()
    class_algebra = load_json(OUT_DIR / "class_algebra.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if class_algebra != expected["class_algebra"]:
        raise AssertionError("long_b3alg class algebra JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_b3alg cert mismatch")
    for filename, key in {
        "class.csv": "class_csv",
        "class_product.csv": "product_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_b3alg {filename} mismatch")

    for key, expected_array in {
        "class_table": expected["class_table"],
        "product_table": expected["product_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
        "structure_tensor": expected["structure_tensor"],
        "pair_count_tensor": expected["pair_count_tensor"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_b3alg table mismatch: {key}")

    if report.get("schema") != "long.b3alg.report@1":
        raise AssertionError("long_b3alg report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_b3alg report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_b3alg all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_b3alg checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_b3alg report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_b3alg report hash mismatch")

    product_count = report["witness"]["summary"]["nonzero_product_row_count"]
    csv_shapes = [
        ("class.csv", CLASS_COLUMNS, 41),
        ("class_product.csv", PRODUCT_COLUMNS, product_count),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_b3alg {filename} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "group_order": EXPECTED_GROUP_ORDER,
        "degree": EXPECTED_POINTS,
        "class_count": 41,
        "class_size_sum": EXPECTED_GROUP_ORDER,
        "dense_product_entry_count": 41 * 41 * 41,
        "identity_class": 0,
        "identity_law_pass_flag": 1,
        "inverse_law_pass_flag": 1,
        "commutativity_pass_flag": 1,
        "associativity_pass_flag": 1,
        "balance_pass_flag": 1,
        "irreducible_table_present_flag": 0,
        "next_gap_code": 5,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_b3alg observable {key} mismatch")
    if obs.get(OBS_CODES["nonzero_product_row_count"]) != product_count:
        raise AssertionError("long_b3alg product-count observable mismatch")
    if obs.get(OBS_CODES["max_structure_constant"], 0) <= 0:
        raise AssertionError("long_b3alg max structure constant invalid")

    class_rows = rows_from_table(np.asarray(tables["class_table"]), CLASS_COLUMNS)
    if [row["class_id"] for row in class_rows] != list(range(41)):
        raise AssertionError("long_b3alg class ids mismatch")
    if sum(row["class_size"] for row in class_rows) != EXPECTED_GROUP_ORDER:
        raise AssertionError("long_b3alg class-size sum mismatch")
    if sum(row["identity_class_flag"] for row in class_rows) != 1:
        raise AssertionError("long_b3alg identity class count mismatch")

    tensor = np.asarray(tables["structure_tensor"])
    pair_counts = np.asarray(tables["pair_count_tensor"])
    if tensor.shape != (41, 41, 41):
        raise AssertionError("long_b3alg tensor shape mismatch")
    if pair_counts.shape != (41, 41, 41):
        raise AssertionError("long_b3alg pair-count tensor shape mismatch")
    sizes = np.asarray([row["class_size"] for row in class_rows], dtype=np.int64)
    balance = np.einsum("ijk,k->ij", tensor, sizes, optimize=True)
    if not np.array_equal(balance, sizes[:, None] * sizes[None, :]):
        raise AssertionError("long_b3alg balance law mismatch")
    if not np.array_equal(tensor, np.swapaxes(tensor, 0, 1)):
        raise AssertionError("long_b3alg commutativity mismatch")
    left = np.einsum("ijl,lkm->ijkm", tensor, tensor, optimize=True)
    right = np.einsum("jkl,ilm->ijkm", tensor, tensor, optimize=True)
    if not np.array_equal(left, right):
        raise AssertionError("long_b3alg associativity mismatch")
    if tensor[0, :, :].diagonal().sum() != 41:
        raise AssertionError("long_b3alg left identity diagonal mismatch")
    if tensor[:, 0, :].diagonal().sum() != 41:
        raise AssertionError("long_b3alg right identity diagonal mismatch")

    product_rows = rows_from_table(
        np.asarray(tables["product_table"]), PRODUCT_COLUMNS
    )
    if [row["row_id"] for row in product_rows] != list(range(product_count)):
        raise AssertionError("long_b3alg product row ids mismatch")
    if len(product_rows) != int(np.count_nonzero(tensor)):
        raise AssertionError("long_b3alg product row nonzero count mismatch")
    for row in product_rows:
        if row["pair_count"] != row["class_size"] * row["structure_constant"]:
            raise AssertionError("long_b3alg product row divisibility mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 1, 1, 1, 1, 0, 0]:
        raise AssertionError("long_b3alg gap certified vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 0, 0, 0, 0, 1, 0]:
        raise AssertionError("long_b3alg gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_b3alg manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_b3alg manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_b3alg manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_b3mod": B3MOD_REPORT,
        "long_kr39": LONG_KR39,
        "coorient_npz": COORIENT_NPZ,
        "b3mod_class_csv": B3MOD_CLASS_CSV,
        "b3mod_permutation_character_csv": B3MOD_PERMCHAR_CSV,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_b3alg index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_b3alg index report hash mismatch")

    return {
        "schema": "long.b3alg.verification@1",
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
    print(json.dumps(validate_long_b3alg(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
