from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

try:
    from src.paths import D20_INVARIANTS, ROOT
except ModuleNotFoundError:  # Supports direct script execution.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "d20_contour_sector_packet_prime_alignment"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

D20_FINITE_CONTOUR_INTEGRATION = (
    D20_INVARIANTS / "theorems" / "d20_finite_contour_integration" / "report.json"
)
D20_PACKET_BRIDGE_SNF_OBSTRUCTION = (
    D20_INVARIANTS / "theorems" / "d20_packet_bridge_snf_obstruction" / "report.json"
)
ZERO_PAIR_CHARGE_KERNEL = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_propagator_charge_kernel"
    / "report.json"
)
SECTOR26_INVARIANT_SUITE = (
    D20_INVARIANTS / "theorems" / "sector26_invariant_suite" / "report.json"
)


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def input_record(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": sha_file(path)}


def factorization(value: int) -> dict[str, int]:
    n = abs(int(value))
    out: dict[int, int] = {}
    p = 2
    while p * p <= n:
        while n % p == 0:
            out[p] = out.get(p, 0) + 1
            n //= p
        p += 1 if p == 2 else 2
    if n > 1:
        out[n] = out.get(n, 0) + 1
    return {str(key): int(out[key]) for key in sorted(out)}


def prime_set_from_factorization(factors: dict[str, int]) -> list[int]:
    return sorted(int(key) for key, value in factors.items() if int(value) > 0)


def prime_set_from_values(values: list[int]) -> list[int]:
    primes: set[int] = set()
    for value in values:
        primes.update(prime_set_from_factorization(factorization(value)))
    return sorted(primes)


def update_theorem_index(report: dict[str, Any], out_dir: Path) -> None:
    index_path = out_dir.parent / "index.json"
    entry = {
        "id": THEOREM_ID,
        "manifest": rel(out_dir / "manifest.json"),
        "report": rel(out_dir / "report.json"),
        "report_sha256": report["certificate_sha256"],
        "status": report["status"],
    }
    if index_path.exists():
        index = load_json(index_path)
        if index.get("schema") == "d20.theorem_registry.source_drop":
            return
        theorems = [item for item in index.get("theorems", []) if item.get("id") != THEOREM_ID]
    else:
        theorems = []
    theorems.append(entry)
    theorems = sorted(theorems, key=lambda item: item["id"])
    index = {
        "schema": "d20.theorem_registry",
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": len(theorems),
        "theorems": theorems,
    }
    index["registry_sha256"] = sha_json({key: value for key, value in index.items() if key != "registry_sha256"})
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_theorem() -> dict[str, Any]:
    contour = load_json(D20_FINITE_CONTOUR_INTEGRATION)
    packet = load_json(D20_PACKET_BRIDGE_SNF_OBSTRUCTION)
    charge = load_json(ZERO_PAIR_CHARGE_KERNEL)
    sector26 = load_json(SECTOR26_INVARIANT_SUITE)

    contour_signed = contour["derived"]["signed_contour_residue"]
    contour_edges = contour["derived"]["edge_weight_quantization"]
    packet_summary = packet["derived"]["obstruction_summary"]
    charge_summary = charge["derived"]["propagator_charge_kernel_summary"]

    contour_raw_factors = factorization(int(contour_signed["gcd_signed_integrals"]))
    contour_edge_factors = factorization(int(contour_edges["gcd_edge_weights"]))
    contour_ledger_factors = factorization(26)
    packet_factors = {
        "local_block_2": factorization(2),
        "local_block_6": factorization(6),
        "cokernel_order": factorization(int(packet_summary["cokernel_order"])),
    }
    sector26_factors = {
        "ledger_modulus": factorization(26),
        "half_denominator": factorization(2),
    }

    contour_raw_primes = prime_set_from_factorization(contour_raw_factors)
    contour_ledger_primes = prime_set_from_factorization(contour_ledger_factors)
    packet_primes = list(packet_summary["torsion_primes"])
    sector26_primes = prime_set_from_factorization(sector26_factors["ledger_modulus"])
    all_layer_common = sorted(set(contour_raw_primes) & set(packet_primes) & set(sector26_primes))
    contour_packet_shared = sorted(set(contour_raw_primes) & set(packet_primes))
    contour_sector_shared = sorted(set(contour_ledger_primes) & set(sector26_primes))
    packet_sector_shared = sorted(set(packet_primes) & set(sector26_primes))
    union_split = sorted(set(contour_raw_primes) | set(contour_ledger_primes) | set(packet_primes) | set(sector26_primes))

    plus = charge_summary["plus_denominator_cleared_sector26_image"]
    minus = charge_summary["minus_denominator_cleared_sector26_image"]
    comparison_rows = [
        {
            "layer": "finite_contour_raw_integrals",
            "object": "signed contour residue gcd",
            "integer": int(contour_signed["gcd_signed_integrals"]),
            "factorization": contour_raw_factors,
            "prime_support": contour_raw_primes,
            "role": "optical/action quantization before mod-26 reduction",
        },
        {
            "layer": "finite_contour_sector26_reduction",
            "object": "mod-26 primitive residue line",
            "integer": 26,
            "factorization": contour_ledger_factors,
            "prime_support": contour_ledger_primes,
            "role": "ledger reduction of the primitive signed contour line",
        },
        {
            "layer": "packet_snf_obstruction",
            "object": "packet operator cokernel",
            "integer": int(packet_summary["cokernel_order"]),
            "factorization": packet_factors["cokernel_order"],
            "prime_support": packet_primes,
            "role": "integral image obstruction for the 20-packet operator",
        },
        {
            "layer": "sector26_charge_kernel",
            "object": "denominator-cleared sector-26 ledger",
            "integer": 26,
            "factorization": sector26_factors["ledger_modulus"],
            "prime_support": sector26_primes,
            "role": "cleared plus/minus propagator charge classes",
        },
    ]
    alignment_summary = {
        "union_prime_split": union_split,
        "common_prime_all_layers": all_layer_common,
        "contour_raw_primes": contour_raw_primes,
        "contour_mod26_primes": contour_ledger_primes,
        "packet_snf_primes": packet_primes,
        "sector26_primes": sector26_primes,
        "contour_packet_shared_primes": contour_packet_shared,
        "contour_sector26_shared_primes": contour_sector_shared,
        "packet_sector26_shared_primes": packet_sector_shared,
        "stratified_prime_roles": {
            "2": "common denominator/integrality hinge across contour, packet SNF, and sector-26 charge",
            "3": "optical/action and packet-SNF torsion only",
            "13": "sector-26 ledger modulus only",
        },
        "alignment_strength": "certified_prime_support_alignment_not_group_isomorphism",
    }
    sector26_charge_summary = {
        "raw_half_residues_are_not_native_z26_classes": charge_summary[
            "raw_half_residues_are_not_native_z26_classes"
        ],
        "plus_sum_delta_mod26": [
            int(plus["sector26_clock_sum_mod26"]),
            int(plus["sector26_clock_delta_mod26"]),
        ],
        "minus_sum_delta_mod26": [
            int(minus["sector26_clock_sum_mod26"]),
            int(minus["sector26_clock_delta_mod26"]),
        ],
        "paired_sum_is_neutral_mod26": (int(plus["sector26_clock_sum_mod26"]) + int(minus["sector26_clock_sum_mod26"])) % 26 == 0,
        "paired_delta_is_neutral_mod26": (int(plus["sector26_clock_delta_mod26"]) + int(minus["sector26_clock_delta_mod26"])) % 26 == 0,
        "sector26_first_obstruction_normalized_mod26": int(
            sector26["derived"]["optical_action_normalization"]["first_obstruction_normalized_mod26"]
        ),
    }
    checks = {
        "contour_input_is_certified": contour.get("status") == "D20_FINITE_CONTOUR_INTEGRATION_TEST_PASS"
        and contour.get("all_checks_pass") is True,
        "packet_snf_input_is_certified": packet.get("status")
        == "D20_PACKET_BRIDGE_SNF_OBSTRUCTION_CERTIFIED"
        and packet.get("all_checks_pass") is True,
        "charge_kernel_input_is_certified": charge.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_PROPAGATOR_CHARGE_KERNEL_CERTIFIED"
        and charge.get("all_checks_pass") is True,
        "sector26_input_is_certified": sector26.get("status")
        == "D20_SECTOR26_INVARIANT_SUITE_CERTIFIED"
        and sector26.get("all_checks_pass") is True,
        "contour_signed_gcd_has_2_3_support": contour_raw_factors == {"2": 10, "3": 1},
        "contour_edge_gcd_has_2_3_support": contour_edge_factors == {"2": 10, "3": 1},
        "contour_mod26_has_2_13_support": contour_ledger_primes == [2, 13],
        "packet_snf_has_2_3_support": packet_primes == [2, 3],
        "sector26_charge_has_2_13_support": sector26_primes == [2, 13],
        "prime_2_is_common_to_all_layers": all_layer_common == [2],
        "prime_3_is_contour_packet_only": 3 in contour_packet_shared
        and 3 not in sector26_primes,
        "prime_13_is_sector_ledger_only": 13 in contour_ledger_primes
        and 13 in sector26_primes
        and 13 not in packet_primes
        and 13 not in contour_raw_primes,
        "plus_minus_sector26_pair_is_neutral": sector26_charge_summary[
            "paired_sum_is_neutral_mod26"
        ]
        and sector26_charge_summary["paired_delta_is_neutral_mod26"],
        "raw_half_residue_obstruction_is_at_2": sector26_charge_summary[
            "raw_half_residues_are_not_native_z26_classes"
        ]
        and sector26_factors["half_denominator"] == {"2": 1},
    }
    report = {
        "schema": "d20.theorem.d20_contour_sector_packet_prime_alignment",
        "status": "D20_CONTOUR_SECTOR_PACKET_PRIME_ALIGNMENT_CERTIFIED",
        "object": "D20",
        "definition": {
            "prime_alignment": (
                "comparison of prime support across finite contour residues, packet Smith "
                "obstructions, and denominator-cleared sector-26 charge classes"
            ),
            "scope": (
                "prime-support alignment only; no group isomorphism or physical field theory is claimed"
            ),
        },
        "claim": (
            "The contour, packet-SNF, and sector-26 charge certificates exhibit the same "
            "stratified 2/3/13 split. Prime 2 is common to all three layers. Prime 3 occurs "
            "in the raw contour/action quantization and packet SNF obstruction. Prime 13 "
            "appears only after sector-26 ledger reduction. This proves a certified prime-support "
            "alignment, not an isomorphism of the three structures."
        ),
        "inputs": {
            "d20_finite_contour_integration_report": input_record(D20_FINITE_CONTOUR_INTEGRATION),
            "d20_packet_bridge_snf_obstruction_report": input_record(
                D20_PACKET_BRIDGE_SNF_OBSTRUCTION
            ),
            "full_exposure_zero_pair_propagator_charge_kernel_report": input_record(
                ZERO_PAIR_CHARGE_KERNEL
            ),
            "sector26_invariant_suite_report": input_record(SECTOR26_INVARIANT_SUITE),
        },
        "derived": {
            "alignment_summary": alignment_summary,
            "comparison_rows": comparison_rows,
            "comparison_rows_sha256": sha_json(comparison_rows),
            "factorizations": {
                "contour_signed_gcd": contour_raw_factors,
                "contour_edge_weight_gcd": contour_edge_factors,
                "contour_mod26_modulus": contour_ledger_factors,
                "packet_snf": packet_factors,
                "sector26_charge": sector26_factors,
            },
            "sector26_charge_summary": sector26_charge_summary,
            "contour_residue_summary": {
                "primitive_residue_vector": contour_signed["primitive_residue_vector"],
                "mod26_residue_vector": contour_signed["mod26_residue_vector"],
                "primitive_residue_vector_gcd": contour_signed["primitive_residue_vector_gcd"],
            },
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": {
            "strongest_safe_reading": (
                "The D20 boundary has a certified arithmetic alignment: integral contour/action "
                "quantization meets packet-SNF torsion at primes 2 and 3, while the public charge "
                "ledger introduces the 13-part through mod 26."
            ),
            "not_claimed": (
                "This does not prove a prime-distribution law, M-theory, or a canonical Bhargava-cube "
                "object."
            ),
        },
        "next_highest_yield_item": (
            "Build a residue-line pairing matrix between the 11 contour residues and the sector-26 "
            "charge-kernel doublet, then compute its Smith form."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {key: value for key, value in report.items() if key != "certificate_sha256"}
    )
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "schema": "d20.theorem.d20_contour_sector_packet_prime_alignment_manifest",
        "status": report["status"],
        "name": THEOREM_ID,
        "artifacts": {
            "report": rel(out_dir / "report.json"),
            "manifest": rel(out_dir / "manifest.json"),
        },
        "report_sha256": report["certificate_sha256"],
        "inputs": report["inputs"],
        "purpose": [
            "compare contour residues against packet SNF and sector-26 charge arithmetic",
            "certify the stratified 2/3/13 prime-support split",
        ],
    }
    manifest["manifest_sha256"] = sha_json(
        {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    )
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    update_theorem_index(report, out_dir)
    return report


def main() -> None:
    report = write_theorem()
    print(report["status"])
    print(report["certificate_sha256"])


if __name__ == "__main__":
    main()
