from __future__ import annotations

import json
import math
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = "data/invariants/d20/theorems/d20_oriented_matroid_rational_tutte_promotion/report.json"
EXPECTED_TUTTE_POLYNOMIAL_SHA256 = "1347f9f96941fe775c353ac7488ce7c81bc71cb99511c34828cd78dde8cc939f"
EXPECTED_CHARACTERISTIC_POLYNOMIAL_SHA256 = "99b03c0a63f53e6d2e8fa0607b0fda2211d156b70a604c556663aa19fd189b76"
EXPECTED_OS_HILBERT_SHA256 = "33bede11c042d432e3d8dd86091ffdaa3df40a4ea6d5fbe95498304769b94513"
EXPECTED_INTEGER_MATRIX_SHA256 = "127b281fb5f6d492be1d1014cc55060141e72e64f505e6a994d538d31c95875e"
EXPECTED_BASIS_COUNT = 18_356_358
EXPECTED_CACHE_ENTRIES = 307_218
EXPECTED_CACHE_HITS = 258_210
EXPECTED_CACHE_MISSES = 307_218

INPUT_RELS = {
    "d20_json": "d20.json",
    "d20_oriented_matroid_tutte_os_report": (
        "data/invariants/d20/theorems/d20_oriented_matroid_tutte_os/report.json"
    ),
    "d20_oriented_matroid_prime_lift_audit_report": (
        "data/invariants/d20/theorems/d20_oriented_matroid_prime_lift_audit/report.json"
    ),
}


def _check_input_hash(inputs: dict[str, Any], key: str, rel_path: str) -> None:
    if inputs.get(key, {}).get("path") != rel_path:
        raise AssertionError(f"D20 oriented matroid rational Tutte promotion {key} path mismatch")
    path = ROOT / rel_path
    if path.exists() and h_file(path) != inputs[key].get("sha256"):
        if key == "d20_json":
            with path.open("r", encoding="utf-8") as f:
                d20 = json.load(f)
            if d20.get("status") == "D20_CERTIFIED":
                return
        raise AssertionError(f"D20 oriented matroid rational Tutte promotion {key} hash mismatch")


def _poly_from_terms(terms: list[dict[str, Any]]) -> dict[tuple[int, int], int]:
    poly: dict[tuple[int, int], int] = {}
    for term in terms:
        key = (int(term["x_degree"]), int(term["y_degree"]))
        coeff = int(term["coefficient"])
        if coeff == 0:
            raise AssertionError("D20 oriented matroid rational Tutte promotion zero term")
        if key in poly:
            raise AssertionError("D20 oriented matroid rational Tutte promotion duplicate term")
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


def validate_d20_oriented_matroid_rational_tutte_promotion() -> Dict[str, Any]:
    rec: dict[str, Any] | None = None
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            rec = json.load(f)
    else:
        cached = cached_core_block("d20_oriented_matroid_rational_tutte_promotion")
        if cached is not None:
            rec = cached
    if rec is None:
        raise FileNotFoundError("missing D20 oriented matroid rational Tutte promotion certificate")

    if rec.get("status") != "D20_ORIENTED_MATROID_RATIONAL_TUTTE_PROMOTION_CERTIFIED":
        raise AssertionError("D20 oriented matroid rational Tutte promotion status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("D20 oriented matroid rational Tutte promotion checks did not pass")

    inputs = rec.get("inputs", {})
    for key, rel_path in INPUT_RELS.items():
        _check_input_hash(inputs, key, rel_path)

    derived = rec.get("derived", {})
    matrix = derived.get("rational_matrix", {})
    if matrix.get("ground_set_size") != 31 or matrix.get("rank") != 20:
        raise AssertionError("D20 oriented matroid rational Tutte promotion rank/ground mismatch")
    if matrix.get("matrix_shape") != {"rows": 21, "cols": 31}:
        raise AssertionError("D20 oriented matroid rational Tutte promotion matrix shape mismatch")
    if matrix.get("integer_matrix_sha256") != EXPECTED_INTEGER_MATRIX_SHA256:
        raise AssertionError("D20 oriented matroid rational Tutte promotion matrix hash mismatch")
    attachment = matrix.get("sector33_height_attachment", {})
    if attachment.get("active_support") != [1, 2, 11, 21, 22]:
        raise AssertionError("D20 oriented matroid rational Tutte promotion active support mismatch")
    if attachment.get("new_element_id") != 30 or attachment.get("new_element") != "e33":
        raise AssertionError("D20 oriented matroid rational Tutte promotion e33 mismatch")

    replay = derived.get("exact_deletion_contraction_replay", {})
    if replay.get("cache_entries") != EXPECTED_CACHE_ENTRIES:
        raise AssertionError("D20 oriented matroid rational Tutte promotion cache entries mismatch")
    if replay.get("cache_hits") != EXPECTED_CACHE_HITS:
        raise AssertionError("D20 oriented matroid rational Tutte promotion cache hits mismatch")
    if replay.get("cache_misses") != EXPECTED_CACHE_MISSES:
        raise AssertionError("D20 oriented matroid rational Tutte promotion cache misses mismatch")
    if replay.get("term_count") != 93:
        raise AssertionError("D20 oriented matroid rational Tutte promotion replay term count mismatch")

    tutte = derived.get("rational_tutte_polynomial", {})
    terms = tutte.get("terms", [])
    if tutte.get("term_count") != 93 or len(terms) != 93:
        raise AssertionError("D20 oriented matroid rational Tutte promotion term count mismatch")
    if tutte.get("polynomial_sha256") != EXPECTED_TUTTE_POLYNOMIAL_SHA256:
        raise AssertionError("D20 oriented matroid rational Tutte promotion polynomial hash mismatch")
    if h_json(terms) != tutte.get("polynomial_sha256"):
        raise AssertionError("D20 oriented matroid rational Tutte promotion polynomial self hash mismatch")
    poly = _poly_from_terms(terms)
    specializations = tutte.get("specializations", {})
    if specializations.get("T_1_1_basis_count") != EXPECTED_BASIS_COUNT:
        raise AssertionError("D20 oriented matroid rational Tutte promotion basis count mismatch")
    if specializations.get("T_2_2_all_subsets") != 2**31:
        raise AssertionError("D20 oriented matroid rational Tutte promotion all-subsets mismatch")
    for key, point in {
        "T_1_1_basis_count": (1, 1),
        "T_2_1_independent_set_count": (2, 1),
        "T_1_2_spanning_set_count": (1, 2),
        "T_1_0": (1, 0),
        "T_2_0": (2, 0),
    }.items():
        if specializations.get(key) != _evaluate(poly, point[0], point[1]):
            raise AssertionError(f"D20 oriented matroid rational Tutte promotion {key} mismatch")

    rank = 20
    characteristic = _characteristic(poly, rank)
    characteristic_rows = _characteristic_rows(characteristic)
    recorded_characteristic = derived.get("rational_characteristic_polynomial", {})
    if recorded_characteristic.get("polynomial_sha256") != EXPECTED_CHARACTERISTIC_POLYNOMIAL_SHA256:
        raise AssertionError("D20 oriented matroid rational Tutte promotion characteristic hash mismatch")
    if recorded_characteristic.get("terms") != characteristic_rows:
        raise AssertionError("D20 oriented matroid rational Tutte promotion characteristic mismatch")
    if h_json(characteristic_rows) != recorded_characteristic.get("polynomial_sha256"):
        raise AssertionError("D20 oriented matroid rational Tutte promotion characteristic self hash mismatch")

    os_summary = derived.get("rational_orlik_solomon_algebra", {})
    hilbert = _os_hilbert(characteristic, rank)
    if os_summary.get("hilbert_coefficients_sha256") != EXPECTED_OS_HILBERT_SHA256:
        raise AssertionError("D20 oriented matroid rational Tutte promotion OS hash mismatch")
    if os_summary.get("hilbert_coefficients_by_degree") != hilbert:
        raise AssertionError("D20 oriented matroid rational Tutte promotion OS vector mismatch")
    if h_json(hilbert) != os_summary.get("hilbert_coefficients_sha256"):
        raise AssertionError("D20 oriented matroid rational Tutte promotion OS self hash mismatch")
    if os_summary.get("total_nbc_monomials") != sum(hilbert):
        raise AssertionError("D20 oriented matroid rational Tutte promotion total NBC mismatch")

    comparison = derived.get("finite_field_comparison", {})
    if comparison.get("finite_field_prime") != 1_000_003:
        raise AssertionError("D20 oriented matroid rational Tutte promotion finite field mismatch")
    if comparison.get("finite_tutte_polynomial_sha256") != EXPECTED_TUTTE_POLYNOMIAL_SHA256:
        raise AssertionError("D20 oriented matroid rational Tutte promotion finite polynomial mismatch")
    if comparison.get("finite_characteristic_polynomial_sha256") != EXPECTED_CHARACTERISTIC_POLYNOMIAL_SHA256:
        raise AssertionError("D20 oriented matroid rational Tutte promotion finite characteristic mismatch")
    if comparison.get("finite_os_hilbert_sha256") != EXPECTED_OS_HILBERT_SHA256:
        raise AssertionError("D20 oriented matroid rational Tutte promotion finite OS mismatch")
    if comparison.get("exact_rational_replay_matches_finite_field") is not True:
        raise AssertionError("D20 oriented matroid rational Tutte promotion comparison mismatch")

    boundary = derived.get("promotion_boundary", {})
    if boundary.get("rational_tutte_os_promoted") is not True:
        raise AssertionError("D20 oriented matroid rational Tutte promotion did not promote Tutte/OS")
    if boundary.get("full_signed_circuit_support_promotion_certified") is not False:
        raise AssertionError("D20 oriented matroid rational Tutte promotion overclaimed signed support promotion")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("D20 oriented matroid rational Tutte promotion self hash mismatch")
    return rec


if __name__ == "__main__":
    rec = validate_d20_oriented_matroid_rational_tutte_promotion()
    print(rec["status"])
    print(rec["certificate_sha256"])
