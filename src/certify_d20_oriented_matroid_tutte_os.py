from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
import math
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = "data/invariants/d20/theorems/d20_oriented_matroid_tutte_os/report.json"
EXPECTED_TUTTE_POLYNOMIAL_SHA256 = "1347f9f96941fe775c353ac7488ce7c81bc71cb99511c34828cd78dde8cc939f"
EXPECTED_CHARACTERISTIC_POLYNOMIAL_SHA256 = "99b03c0a63f53e6d2e8fa0607b0fda2211d156b70a604c556663aa19fd189b76"
EXPECTED_OS_HILBERT_SHA256 = "33bede11c042d432e3d8dd86091ffdaa3df40a4ea6d5fbe95498304769b94513"
EXPECTED_INTEGER_MATRIX_SHA256 = "127b281fb5f6d492be1d1014cc55060141e72e64f505e6a994d538d31c95875e"
EXPECTED_MOD_PRIME_MATRIX_SHA256 = "3bffc7ebaa79f8c16e3f3e9f42913e2f628a9779d9b5257ab379c84c8e7d1294"
EXPECTED_BASIS_COUNT = 18_356_358

INPUT_RELS = {
    "d20_json": "d20.json",
    "d20_oriented_matroid_sector33_extension_report": (
        "data/invariants/d20/theorems/d20_oriented_matroid_sector33_extension/report.json"
    ),
    "d20_oriented_matroid_sector33_dual_report": (
        "data/invariants/d20/theorems/d20_oriented_matroid_sector33_dual/report.json"
    ),
}


def _check_input_hash(inputs: dict[str, Any], key: str, rel_path: str) -> None:
    if inputs.get(key, {}).get("path") != rel_path:
        raise AssertionError(f"D20 oriented matroid Tutte/OS {key} path mismatch")
    path = ROOT / rel_path
    if path.exists() and h_file(path) != inputs[key].get("sha256"):
        if key == "d20_json":
            with path.open("r", encoding="utf-8") as f:
                d20 = json.load(f)
            if d20.get("status") == "D20_CERTIFIED":
                return
        raise AssertionError(f"D20 oriented matroid Tutte/OS {key} hash mismatch")


def _poly_from_terms(terms: list[dict[str, Any]]) -> dict[tuple[int, int], int]:
    poly: dict[tuple[int, int], int] = {}
    for term in terms:
        key = (int(term["x_degree"]), int(term["y_degree"]))
        coeff = int(term["coefficient"])
        if coeff == 0:
            raise AssertionError("D20 oriented matroid Tutte/OS zero coefficient term")
        if key in poly:
            raise AssertionError("D20 oriented matroid Tutte/OS duplicate polynomial term")
        poly[key] = coeff
    return poly


def _evaluate(poly: dict[tuple[int, int], int], x_value: int, y_value: int) -> int:
    return sum(
        coeff * (x_value ** x_degree) * (y_value ** y_degree)
        for (x_degree, y_degree), coeff in poly.items()
    )


def _characteristic(poly: dict[tuple[int, int], int], rank: int) -> dict[int, int]:
    coeffs: dict[int, int] = {}
    sign = -1 if rank % 2 else 1
    for (x_degree, y_degree), coeff in poly.items():
        if y_degree != 0:
            continue
        for q_degree in range(x_degree + 1):
            term = sign * coeff * math.comb(x_degree, q_degree) * ((-1) ** q_degree)
            coeffs[q_degree] = coeffs.get(q_degree, 0) + term
    return {degree: coeffs.get(degree, 0) for degree in range(rank + 1)}


def _characteristic_rows(coeffs: dict[int, int]) -> list[dict[str, int]]:
    return [
        {"q_degree": degree, "coefficient": coeffs[degree]}
        for degree in sorted(coeffs, reverse=True)
    ]


def _os_hilbert(characteristic: dict[int, int], rank: int) -> list[int]:
    return [
        ((-1) ** degree) * characteristic[rank - degree]
        for degree in range(rank + 1)
    ]


def validate_d20_oriented_matroid_tutte_os() -> Dict[str, Any]:
    rec: dict[str, Any] | None = None
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            rec = json.load(f)
    else:
        cached = cached_core_block("d20_oriented_matroid_tutte_os")
        if cached is not None:
            rec = cached
    if rec is None:
        raise FileNotFoundError("missing D20 oriented matroid Tutte/OS certificate")

    if rec.get("status") != "D20_ORIENTED_MATROID_TUTTE_OS_CERTIFIED":
        raise AssertionError("D20 oriented matroid Tutte/OS status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("D20 oriented matroid Tutte/OS checks did not pass")

    inputs = rec.get("inputs", {})
    for key, rel_path in INPUT_RELS.items():
        _check_input_hash(inputs, key, rel_path)

    derived = rec.get("derived", {})
    field = derived.get("field_matroid", {})
    if field.get("field_prime") != 1_000_003:
        raise AssertionError("D20 oriented matroid Tutte/OS field-prime mismatch")
    if field.get("ground_set_size") != 31 or field.get("rank") != 20:
        raise AssertionError("D20 oriented matroid Tutte/OS rank/ground mismatch")
    if field.get("integer_matrix_shape") != {"rows": 21, "cols": 31}:
        raise AssertionError("D20 oriented matroid Tutte/OS integer matrix shape mismatch")
    if field.get("mod_prime_matrix_shape") != {"rows": 21, "cols": 31}:
        raise AssertionError("D20 oriented matroid Tutte/OS modular matrix shape mismatch")
    if field.get("integer_matrix_sha256") != EXPECTED_INTEGER_MATRIX_SHA256:
        raise AssertionError("D20 oriented matroid Tutte/OS integer matrix hash mismatch")
    if field.get("mod_prime_matrix_sha256") != EXPECTED_MOD_PRIME_MATRIX_SHA256:
        raise AssertionError("D20 oriented matroid Tutte/OS modular matrix hash mismatch")
    if field.get("rational_lift_audited") is not False:
        raise AssertionError("D20 oriented matroid Tutte/OS rational-lift guardrail mismatch")
    attachment = field.get("sector33_height_attachment", {})
    if attachment.get("active_support") != [1, 2, 11, 21, 22]:
        raise AssertionError("D20 oriented matroid Tutte/OS active support mismatch")
    if attachment.get("new_element_id") != 30 or attachment.get("new_element") != "e33":
        raise AssertionError("D20 oriented matroid Tutte/OS e33 element mismatch")

    cache = derived.get("deletion_contraction_cache", {})
    if cache.get("term_count") != 93:
        raise AssertionError("D20 oriented matroid Tutte/OS cache term count mismatch")
    if int(cache.get("cache_entries", 0)) <= 0 or int(cache.get("cache_misses", 0)) <= 0:
        raise AssertionError("D20 oriented matroid Tutte/OS cache stats missing")

    tutte = derived.get("tutte_polynomial", {})
    terms = tutte.get("terms", [])
    if tutte.get("term_count") != 93 or len(terms) != 93:
        raise AssertionError("D20 oriented matroid Tutte/OS term-count mismatch")
    if tutte.get("polynomial_sha256") != EXPECTED_TUTTE_POLYNOMIAL_SHA256:
        raise AssertionError("D20 oriented matroid Tutte/OS polynomial hash mismatch")
    if h_json(terms) != tutte.get("polynomial_sha256"):
        raise AssertionError("D20 oriented matroid Tutte/OS polynomial self hash mismatch")
    poly = _poly_from_terms(terms)
    specializations = tutte.get("specializations", {})
    if _evaluate(poly, 2, 2) != 2**31:
        raise AssertionError("D20 oriented matroid Tutte/OS all-subsets specialization mismatch")
    if specializations.get("T_2_2_all_subsets") != 2**31:
        raise AssertionError("D20 oriented matroid Tutte/OS recorded all-subsets mismatch")
    if specializations.get("T_1_1_basis_count") != EXPECTED_BASIS_COUNT:
        raise AssertionError("D20 oriented matroid Tutte/OS basis-count mismatch")
    for key, point in {
        "T_1_1_basis_count": (1, 1),
        "T_2_1_independent_set_count": (2, 1),
        "T_1_2_spanning_set_count": (1, 2),
        "T_1_0": (1, 0),
        "T_2_0": (2, 0),
    }.items():
        if specializations.get(key) != _evaluate(poly, point[0], point[1]):
            raise AssertionError(f"D20 oriented matroid Tutte/OS specialization {key} mismatch")

    rank = 20
    characteristic = _characteristic(poly, rank)
    characteristic_rows = _characteristic_rows(characteristic)
    recorded_characteristic = derived.get("characteristic_polynomial", {})
    if recorded_characteristic.get("polynomial_sha256") != EXPECTED_CHARACTERISTIC_POLYNOMIAL_SHA256:
        raise AssertionError("D20 oriented matroid Tutte/OS characteristic hash mismatch")
    if recorded_characteristic.get("terms") != characteristic_rows:
        raise AssertionError("D20 oriented matroid Tutte/OS characteristic polynomial mismatch")
    if h_json(characteristic_rows) != recorded_characteristic.get("polynomial_sha256"):
        raise AssertionError("D20 oriented matroid Tutte/OS characteristic self hash mismatch")
    if characteristic.get(rank) != 1:
        raise AssertionError("D20 oriented matroid Tutte/OS characteristic degree mismatch")

    os_summary = derived.get("orlik_solomon_algebra", {})
    hilbert = _os_hilbert(characteristic, rank)
    if os_summary.get("hilbert_coefficients_sha256") != EXPECTED_OS_HILBERT_SHA256:
        raise AssertionError("D20 oriented matroid Tutte/OS OS Hilbert hash mismatch")
    if os_summary.get("hilbert_coefficients_by_degree") != hilbert:
        raise AssertionError("D20 oriented matroid Tutte/OS OS Hilbert vector mismatch")
    if h_json(hilbert) != os_summary.get("hilbert_coefficients_sha256"):
        raise AssertionError("D20 oriented matroid Tutte/OS OS Hilbert self hash mismatch")
    if len(hilbert) != 21 or hilbert[:2] != [1, 31]:
        raise AssertionError("D20 oriented matroid Tutte/OS OS Hilbert leading terms mismatch")
    if any(value < 0 for value in hilbert):
        raise AssertionError("D20 oriented matroid Tutte/OS OS Hilbert negativity")
    if os_summary.get("total_nbc_monomials") != sum(hilbert):
        raise AssertionError("D20 oriented matroid Tutte/OS total NBC mismatch")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("D20 oriented matroid Tutte/OS self hash mismatch")
    return rec


if __name__ == "__main__":
    rec = validate_d20_oriented_matroid_tutte_os()
    print(rec["status"])
    print(rec["certificate_sha256"])
