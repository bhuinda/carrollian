from __future__ import annotations

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = "data/invariants/d20/theorems/d20_oriented_matroid_prime_lift_audit/report.json"
AUDIT_PRIMES = [1_000_003, 1_000_033, 1_000_037, 1_000_039, 1_000_081]
EXPECTED_TUTTE_POLYNOMIAL_SHA256 = "1347f9f96941fe775c353ac7488ce7c81bc71cb99511c34828cd78dde8cc939f"
EXPECTED_BASIS_COUNT = 18_356_358
EXPECTED_CACHE_ENTRIES = 307_218
EXPECTED_CACHE_HITS = 258_210
EXPECTED_CACHE_MISSES = 307_218

INPUT_RELS = {
    "d20_json": "d20.json",
    "d20_oriented_matroid_sector33_extension_report": (
        "data/invariants/d20/theorems/d20_oriented_matroid_sector33_extension/report.json"
    ),
    "d20_oriented_matroid_sector33_dual_report": (
        "data/invariants/d20/theorems/d20_oriented_matroid_sector33_dual/report.json"
    ),
    "d20_oriented_matroid_tutte_os_report": (
        "data/invariants/d20/theorems/d20_oriented_matroid_tutte_os/report.json"
    ),
}


def _check_input_hash(inputs: dict[str, Any], key: str, rel_path: str) -> None:
    if inputs.get(key, {}).get("path") != rel_path:
        raise AssertionError(f"D20 oriented matroid prime lift audit {key} path mismatch")
    path = ROOT / rel_path
    if path.exists() and h_file(path) != inputs[key].get("sha256"):
        if key == "d20_json":
            with path.open("r", encoding="utf-8") as f:
                d20 = json.load(f)
            if d20.get("status") == "D20_CERTIFIED":
                return
        raise AssertionError(f"D20 oriented matroid prime lift audit {key} hash mismatch")


def _current_tutte_os_certificate_sha256() -> str | None:
    path = ROOT / INPUT_RELS["d20_oriented_matroid_tutte_os_report"]
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f).get("certificate_sha256")


def validate_d20_oriented_matroid_prime_lift_audit() -> Dict[str, Any]:
    rec: dict[str, Any] | None = None
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            rec = json.load(f)
    else:
        cached = cached_core_block("d20_oriented_matroid_prime_lift_audit")
        if cached is not None:
            rec = cached
    if rec is None:
        raise FileNotFoundError("missing D20 oriented matroid prime lift audit certificate")

    if rec.get("status") != "D20_ORIENTED_MATROID_PRIME_LIFT_AUDIT_CERTIFIED":
        raise AssertionError("D20 oriented matroid prime lift audit status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("D20 oriented matroid prime lift audit checks did not pass")

    inputs = rec.get("inputs", {})
    for key, rel_path in INPUT_RELS.items():
        _check_input_hash(inputs, key, rel_path)

    derived = rec.get("derived", {})
    if derived.get("audit_primes") != AUDIT_PRIMES:
        raise AssertionError("D20 oriented matroid prime lift audit prime list mismatch")
    baseline = derived.get("baseline", {})
    if baseline.get("field_prime") != 1_000_003:
        raise AssertionError("D20 oriented matroid prime lift audit baseline field mismatch")
    if baseline.get("tutte_polynomial_sha256") != EXPECTED_TUTTE_POLYNOMIAL_SHA256:
        raise AssertionError("D20 oriented matroid prime lift audit baseline polynomial mismatch")
    if baseline.get("basis_count") != EXPECTED_BASIS_COUNT:
        raise AssertionError("D20 oriented matroid prime lift audit baseline basis count mismatch")
    current_tutte_report_sha256 = _current_tutte_os_certificate_sha256()
    if current_tutte_report_sha256 is not None and baseline.get("report_sha256") != current_tutte_report_sha256:
        raise AssertionError("D20 oriented matroid prime lift audit baseline report mismatch")

    records = derived.get("prime_field_records", [])
    if len(records) != len(AUDIT_PRIMES):
        raise AssertionError("D20 oriented matroid prime lift audit record count mismatch")
    for expected_prime, record in zip(AUDIT_PRIMES, records):
        if record.get("field_prime") != expected_prime:
            raise AssertionError("D20 oriented matroid prime lift audit record prime mismatch")
        if record.get("is_prime") is not True:
            raise AssertionError("D20 oriented matroid prime lift audit non-prime record")
        if record.get("rank") != 20 or record.get("ground_set_size") != 31:
            raise AssertionError("D20 oriented matroid prime lift audit rank/ground mismatch")
        if record.get("term_count") != 93:
            raise AssertionError("D20 oriented matroid prime lift audit term-count mismatch")
        if record.get("polynomial_sha256") != EXPECTED_TUTTE_POLYNOMIAL_SHA256:
            raise AssertionError("D20 oriented matroid prime lift audit polynomial hash mismatch")
        specializations = record.get("specializations", {})
        if specializations.get("T_1_1_basis_count") != EXPECTED_BASIS_COUNT:
            raise AssertionError("D20 oriented matroid prime lift audit basis count mismatch")
        if specializations.get("T_2_2_all_subsets") != 2**31:
            raise AssertionError("D20 oriented matroid prime lift audit all-subsets mismatch")
        cache = record.get("cache_stats", {})
        if cache.get("term_count") != 93:
            raise AssertionError("D20 oriented matroid prime lift audit cache term-count mismatch")
        if cache.get("cache_entries") != EXPECTED_CACHE_ENTRIES:
            raise AssertionError("D20 oriented matroid prime lift audit cache-entry mismatch")
        if cache.get("cache_hits") != EXPECTED_CACHE_HITS:
            raise AssertionError("D20 oriented matroid prime lift audit cache-hit mismatch")
        if cache.get("cache_misses") != EXPECTED_CACHE_MISSES:
            raise AssertionError("D20 oriented matroid prime lift audit cache-miss mismatch")

    stability = derived.get("prime_stability_summary", {})
    if stability.get("stable_tutte_hashes") != [EXPECTED_TUTTE_POLYNOMIAL_SHA256]:
        raise AssertionError("D20 oriented matroid prime lift audit stable hash mismatch")
    if stability.get("stable_basis_counts") != [EXPECTED_BASIS_COUNT]:
        raise AssertionError("D20 oriented matroid prime lift audit stable basis mismatch")
    if stability.get("all_primes_match_baseline") is not True:
        raise AssertionError("D20 oriented matroid prime lift audit stability mismatch")

    rational = derived.get("exact_rational_audit", {})
    if rational.get("ground_set_size") != 31 or rational.get("matrix_rank_over_q") != 20:
        raise AssertionError("D20 oriented matroid prime lift audit exact rank mismatch")
    if rational.get("positive_circuit_support") != [1, 2, 11, 21, 22, 30]:
        raise AssertionError("D20 oriented matroid prime lift audit circuit support mismatch")
    if rational.get("positive_circuit_coefficients") != [1, 1, 1, 1, 1, 2]:
        raise AssertionError("D20 oriented matroid prime lift audit circuit coefficients mismatch")
    if rational.get("positive_circuit_coefficient_gcd") != 1:
        raise AssertionError("D20 oriented matroid prime lift audit circuit primitive mismatch")
    if any(value != 0 for value in rational.get("positive_circuit_kernel_image", [])):
        raise AssertionError("D20 oriented matroid prime lift audit circuit image mismatch")
    if rational.get("positive_support_rank_over_q") != 5:
        raise AssertionError("D20 oriented matroid prime lift audit support rank mismatch")
    if sorted(rational.get("positive_support_deletion_ranks_over_q", {}).values()) != [
        5,
        5,
        5,
        5,
        5,
        5,
    ]:
        raise AssertionError("D20 oriented matroid prime lift audit deletion ranks mismatch")
    if rational.get("positive_support_is_exact_q_circuit") is not True:
        raise AssertionError("D20 oriented matroid prime lift audit exact circuit mismatch")

    boundary = derived.get("promotion_boundary", {})
    if boundary.get("full_rational_promotion_certified") is not False:
        raise AssertionError("D20 oriented matroid prime lift audit overclaimed promotion")
    if "remaining_gate" not in boundary:
        raise AssertionError("D20 oriented matroid prime lift audit missing promotion gate")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("D20 oriented matroid prime lift audit self hash mismatch")
    return rec


if __name__ == "__main__":
    rec = validate_d20_oriented_matroid_prime_lift_audit()
    print(rec["status"])
    print(rec["certificate_sha256"])
