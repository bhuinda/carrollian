from __future__ import annotations

import json
import math
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
    from .derive_d20_oriented_matroid_sector33_dual import (
        build_sector33_height_attachment_matrix,
        matrix_vector_product,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, cached_core_block, h_file, h_json
    from derive_d20_oriented_matroid_sector33_dual import (
        build_sector33_height_attachment_matrix,
        matrix_vector_product,
    )


REPORT_REL = "data/invariants/d20/theorems/d20_oriented_matroid_rational_signed_circuits/report.json"
EXPECTED_MATRIX_SHA256 = "127b281fb5f6d492be1d1014cc55060141e72e64f505e6a994d538d31c95875e"
EXPECTED_CIRCUIT_ROWS_SHA256 = "816a5ab2918df802c1d083ea5727c1ecce7f30cfe869972feea65e1da680b469"
EXPECTED_SIZE_HISTOGRAM = {
    "6": 1,
    "7": 2,
    "8": 12,
    "9": 46,
    "10": 61,
    "11": 143,
    "12": 349,
    "13": 795,
    "14": 1443,
    "15": 2527,
    "16": 3616,
    "17": 4145,
    "18": 4462,
    "19": 4118,
    "20": 2346,
    "21": 880,
}

INPUT_RELS = {
    "d20_json": "d20.json",
    "d20_oriented_matroid_sector33_extension_report": (
        "data/invariants/d20/theorems/d20_oriented_matroid_sector33_extension/report.json"
    ),
    "d20_oriented_matroid_sector33_dual_report": (
        "data/invariants/d20/theorems/d20_oriented_matroid_sector33_dual/report.json"
    ),
    "d20_oriented_matroid_rational_tutte_promotion_report": (
        "data/invariants/d20/theorems/d20_oriented_matroid_rational_tutte_promotion/report.json"
    ),
}


def _check_input_hash(inputs: dict[str, Any], key: str, rel_path: str) -> None:
    if inputs.get(key, {}).get("path") != rel_path:
        raise AssertionError(f"D20 rational signed circuits {key} path mismatch")
    path = ROOT / rel_path
    if path.exists() and h_file(path) != inputs[key].get("sha256"):
        if key == "d20_json":
            with path.open("r", encoding="utf-8") as f:
                d20 = json.load(f)
            if d20.get("status") == "D20_CERTIFIED":
                return
        raise AssertionError(f"D20 rational signed circuits {key} hash mismatch")


def _row_vector(row: dict[str, Any]) -> list[int]:
    support = row.get("support", [])
    coefficients = row.get("coefficients", [])
    if len(support) != len(coefficients):
        raise AssertionError("D20 rational signed circuits row length mismatch")
    if support != sorted(support):
        raise AssertionError("D20 rational signed circuits support is not sorted")
    vector = [0 for _ in range(31)]
    gcd = 0
    for element, coefficient in zip(support, coefficients):
        if not isinstance(element, int) or not 0 <= element < 31:
            raise AssertionError("D20 rational signed circuits element mismatch")
        if not isinstance(coefficient, int) or coefficient == 0:
            raise AssertionError("D20 rational signed circuits coefficient mismatch")
        vector[element] = coefficient
        gcd = math.gcd(gcd, abs(coefficient))
    if gcd != 1:
        raise AssertionError("D20 rational signed circuits primitive coefficient mismatch")
    first = next((value for value in vector if value), None)
    if first is None or first < 0:
        raise AssertionError("D20 rational signed circuits sign normalization mismatch")
    return vector


def validate_d20_oriented_matroid_rational_signed_circuits() -> Dict[str, Any]:
    rec: dict[str, Any] | None = None
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            rec = json.load(f)
    else:
        cached = cached_core_block("d20_oriented_matroid_rational_signed_circuits")
        if cached is not None:
            rec = cached
    if rec is None:
        raise FileNotFoundError("missing D20 rational signed circuits certificate")

    if rec.get("status") != "D20_ORIENTED_MATROID_RATIONAL_SIGNED_CIRCUITS_CERTIFIED":
        raise AssertionError("D20 rational signed circuits status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("D20 rational signed circuits checks did not pass")

    inputs = rec.get("inputs", {})
    for key, rel_path in INPUT_RELS.items():
        _check_input_hash(inputs, key, rel_path)

    derived = rec.get("derived", {})
    matrix_summary = derived.get("rational_matrix", {})
    if matrix_summary.get("ground_set_size") != 31 or matrix_summary.get("rank") != 20:
        raise AssertionError("D20 rational signed circuits rank/ground mismatch")
    if matrix_summary.get("integer_matrix_sha256") != EXPECTED_MATRIX_SHA256:
        raise AssertionError("D20 rational signed circuits matrix hash mismatch")
    attachment = matrix_summary.get("sector33_height_attachment", {})
    if attachment.get("active_support") != [1, 2, 11, 21, 22]:
        raise AssertionError("D20 rational signed circuits active support mismatch")
    if attachment.get("new_element_id") != 30 or attachment.get("new_element") != "e33":
        raise AssertionError("D20 rational signed circuits e33 mismatch")

    summary = derived.get("generation_summary", {})
    expected_summary = {
        "simple_cycle_count": 1757,
        "balanced_simple_cycle_dependency_count": 10,
        "unbalanced_simple_cycle_count": 1747,
        "unbalanced_cycle_pair_count": 1525131,
        "generated_dependency_support_count": 633558,
        "rational_circuit_support_count": 24946,
        "signed_rational_circuit_count": 49892,
        "circuit_rows_sha256": EXPECTED_CIRCUIT_ROWS_SHA256,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(f"D20 rational signed circuits {key} mismatch")
    if summary.get("circuit_size_histogram") != EXPECTED_SIZE_HISTOGRAM:
        raise AssertionError("D20 rational signed circuits size histogram mismatch")

    rows = derived.get("circuit_rows", [])
    if len(rows) != 24946:
        raise AssertionError("D20 rational signed circuits row count mismatch")
    if h_json(rows) != EXPECTED_CIRCUIT_ROWS_SHA256:
        raise AssertionError("D20 rational signed circuits row hash mismatch")
    if derived.get("circuit_rows_sha256") != EXPECTED_CIRCUIT_ROWS_SHA256:
        raise AssertionError("D20 rational signed circuits derived row hash mismatch")

    matrix, _attachment = build_sector33_height_attachment_matrix()
    sample_indices = sorted({0, 1, 2, 128, 1024, 4096, 8192, 16384, len(rows) - 1})
    positive_row = derived.get("positive_gamma8_e33_circuit", {})
    if positive_row != {"support": [1, 2, 11, 21, 22, 30], "coefficients": [1, 1, 1, 1, 1, 2]}:
        raise AssertionError("D20 rational signed circuits positive circuit mismatch")
    sample_rows = [rows[index] for index in sample_indices] + [positive_row]
    for row in sample_rows:
        vector = _row_vector(row)
        if any(value != 0 for value in matrix_vector_product(matrix, vector)):
            raise AssertionError("D20 rational signed circuits sampled dependency mismatch")

    dual_cocircuit = derived.get("distinguished_dual_cocircuit", {})
    if dual_cocircuit.get("support") != [1, 2, 11, 21, 22, 30]:
        raise AssertionError("D20 rational signed circuits dual cocircuit support mismatch")
    if dual_cocircuit.get("support_is_dual_cocircuit") is not True:
        raise AssertionError("D20 rational signed circuits dual cocircuit mismatch")
    if dual_cocircuit.get("complement_is_dual_hyperplane") is not True:
        raise AssertionError("D20 rational signed circuits dual hyperplane mismatch")
    if dual_cocircuit.get("is_positive") is not True:
        raise AssertionError("D20 rational signed circuits dual positivity mismatch")

    boundary = derived.get("promotion_boundary", {})
    if boundary.get("full_rational_signed_circuit_set_certified") is not True:
        raise AssertionError("D20 rational signed circuits did not certify full circuit set")
    if boundary.get("distinguished_dual_cocircuit_certified") is not True:
        raise AssertionError("D20 rational signed circuits did not certify distinguished cocircuit")
    if boundary.get("full_rational_signed_cocircuit_set_certified") is not False:
        raise AssertionError("D20 rational signed circuits overclaimed full cocircuit set")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("D20 rational signed circuits self hash mismatch")
    return rec


if __name__ == "__main__":
    rec = validate_d20_oriented_matroid_rational_signed_circuits()
    print(rec["status"])
    print(rec["certificate_sha256"])
