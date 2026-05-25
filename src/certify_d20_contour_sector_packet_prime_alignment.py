from __future__ import annotations

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = "data/invariants/d20/theorems/d20_contour_sector_packet_prime_alignment/report.json"
INPUT_RELS = {
    "d20_finite_contour_integration_report": (
        "data/invariants/d20/theorems/d20_finite_contour_integration/report.json"
    ),
    "d20_packet_bridge_snf_obstruction_report": (
        "data/invariants/d20/theorems/d20_packet_bridge_snf_obstruction/report.json"
    ),
    "full_exposure_zero_pair_propagator_charge_kernel_report": (
        "data/invariants/d20/theorems/full_exposure_zero_pair_propagator_charge_kernel/report.json"
    ),
    "sector26_invariant_suite_report": (
        "data/invariants/d20/theorems/sector26_invariant_suite/report.json"
    ),
}


def _check_input_hash(inputs: dict[str, Any], key: str, rel_path: str) -> None:
    if inputs.get(key, {}).get("path") != rel_path:
        raise AssertionError(f"D20 contour/sector/packet prime alignment {key} path mismatch")
    path = ROOT / rel_path
    if path.exists() and h_file(path) != inputs[key].get("sha256"):
        raise AssertionError(f"D20 contour/sector/packet prime alignment {key} hash mismatch")


def validate_d20_contour_sector_packet_prime_alignment() -> Dict[str, Any]:
    rec: dict[str, Any] | None = None
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            rec = json.load(f)
    else:
        cached = cached_core_block("d20_contour_sector_packet_prime_alignment")
        if cached is not None:
            rec = cached
    if rec is None:
        raise FileNotFoundError("missing D20 contour/sector/packet prime alignment certificate")

    if rec.get("status") != "D20_CONTOUR_SECTOR_PACKET_PRIME_ALIGNMENT_CERTIFIED":
        raise AssertionError("D20 contour/sector/packet prime alignment status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("D20 contour/sector/packet prime alignment checks did not pass")

    inputs = rec.get("inputs", {})
    for key, rel_path in INPUT_RELS.items():
        _check_input_hash(inputs, key, rel_path)

    derived = rec.get("derived", {})
    summary = derived.get("alignment_summary", {})
    if summary.get("union_prime_split") != [2, 3, 13]:
        raise AssertionError("D20 contour/sector/packet prime union mismatch")
    if summary.get("common_prime_all_layers") != [2]:
        raise AssertionError("D20 contour/sector/packet common-prime mismatch")
    if summary.get("contour_raw_primes") != [2, 3]:
        raise AssertionError("D20 contour raw prime mismatch")
    if summary.get("contour_mod26_primes") != [2, 13]:
        raise AssertionError("D20 contour mod-26 prime mismatch")
    if summary.get("packet_snf_primes") != [2, 3]:
        raise AssertionError("D20 packet SNF prime mismatch")
    if summary.get("sector26_primes") != [2, 13]:
        raise AssertionError("D20 sector-26 prime mismatch")
    if summary.get("contour_packet_shared_primes") != [2, 3]:
        raise AssertionError("D20 contour/packet shared-prime mismatch")
    if summary.get("contour_sector26_shared_primes") != [2, 13]:
        raise AssertionError("D20 contour/sector shared-prime mismatch")
    if summary.get("packet_sector26_shared_primes") != [2]:
        raise AssertionError("D20 packet/sector shared-prime mismatch")
    if summary.get("alignment_strength") != "certified_prime_support_alignment_not_group_isomorphism":
        raise AssertionError("D20 contour/sector/packet overclaim guard mismatch")

    factors = derived.get("factorizations", {})
    if factors.get("contour_signed_gcd") != {"2": 10, "3": 1}:
        raise AssertionError("D20 contour signed factorization mismatch")
    if factors.get("contour_edge_weight_gcd") != {"2": 10, "3": 1}:
        raise AssertionError("D20 contour edge factorization mismatch")
    if factors.get("contour_mod26_modulus") != {"2": 1, "13": 1}:
        raise AssertionError("D20 contour mod-26 factorization mismatch")
    if factors.get("packet_snf", {}).get("local_block_2") != {"2": 1}:
        raise AssertionError("D20 packet local 2 factorization mismatch")
    if factors.get("packet_snf", {}).get("local_block_6") != {"2": 1, "3": 1}:
        raise AssertionError("D20 packet local 6 factorization mismatch")
    if factors.get("sector26_charge", {}).get("ledger_modulus") != {"2": 1, "13": 1}:
        raise AssertionError("D20 sector-26 ledger factorization mismatch")
    if factors.get("sector26_charge", {}).get("half_denominator") != {"2": 1}:
        raise AssertionError("D20 half-denominator factorization mismatch")

    comparison_rows = derived.get("comparison_rows", [])
    if len(comparison_rows) != 4:
        raise AssertionError("D20 contour/sector/packet comparison row count mismatch")
    if h_json(comparison_rows) != derived.get("comparison_rows_sha256"):
        raise AssertionError("D20 contour/sector/packet comparison row hash mismatch")

    sector = derived.get("sector26_charge_summary", {})
    if sector.get("raw_half_residues_are_not_native_z26_classes") is not True:
        raise AssertionError("D20 sector-26 half-residue mismatch")
    if sector.get("plus_sum_delta_mod26") != [4, 8]:
        raise AssertionError("D20 sector-26 plus class mismatch")
    if sector.get("minus_sum_delta_mod26") != [22, 18]:
        raise AssertionError("D20 sector-26 minus class mismatch")
    if sector.get("paired_sum_is_neutral_mod26") is not True:
        raise AssertionError("D20 sector-26 paired sum mismatch")
    if sector.get("paired_delta_is_neutral_mod26") is not True:
        raise AssertionError("D20 sector-26 paired delta mismatch")

    checks = rec.get("checks", {})
    required_true = [
        "prime_2_is_common_to_all_layers",
        "prime_3_is_contour_packet_only",
        "prime_13_is_sector_ledger_only",
        "plus_minus_sector26_pair_is_neutral",
        "raw_half_residue_obstruction_is_at_2",
    ]
    for key in required_true:
        if checks.get(key) is not True:
            raise AssertionError(f"D20 contour/sector/packet check failed: {key}")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("D20 contour/sector/packet prime alignment self hash mismatch")

    return rec


if __name__ == "__main__":
    rec = validate_d20_contour_sector_packet_prime_alignment()
    print(rec["status"])
    print(rec["certificate_sha256"])
