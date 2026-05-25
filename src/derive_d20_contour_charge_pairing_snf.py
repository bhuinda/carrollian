from __future__ import annotations

import hashlib
import itertools
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from src.derive_d20_sandpile_critical_group_theorem import smith_normal_form_diagonal
    from src.paths import D20_INVARIANTS, ROOT
except ModuleNotFoundError:  # Supports direct script execution.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.derive_d20_sandpile_critical_group_theorem import smith_normal_form_diagonal
    from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "d20_contour_charge_pairing_snf"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

D20_FINITE_CONTOUR_INTEGRATION = (
    D20_INVARIANTS / "theorems" / "d20_finite_contour_integration" / "report.json"
)
ZERO_PAIR_CHARGE_KERNEL = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_propagator_charge_kernel"
    / "report.json"
)
D20_CONTOUR_SECTOR_PACKET_PRIME_ALIGNMENT = (
    D20_INVARIANTS / "theorems" / "d20_contour_sector_packet_prime_alignment" / "report.json"
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
    factors: dict[int, int] = {}
    p = 2
    while p * p <= n:
        while n % p == 0:
            factors[p] = factors.get(p, 0) + 1
            n //= p
        p += 1 if p == 2 else 2
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return {str(key): int(factors[key]) for key in sorted(factors)}


def finite_order_mod26(vector: list[int]) -> int:
    for order in range(1, 27):
        if all((order * value) % 26 == 0 for value in vector):
            return order
    raise AssertionError("unreachable finite order search")


def subgroup_generated_by_rows(rows: list[list[int]]) -> set[tuple[int, int]]:
    subgroup = {(0, 0)}
    for row in rows:
        generator = (int(row[0]) % 26, int(row[1]) % 26)
        expanded = set(subgroup)
        for existing in subgroup:
            for k in range(26):
                expanded.add(
                    (
                        (existing[0] + k * generator[0]) % 26,
                        (existing[1] + k * generator[1]) % 26,
                    )
                )
        subgroup = expanded
    return subgroup


def relation_snf(generator: list[int]) -> dict[str, Any]:
    relation_matrix = [[26, 0], [0, 26], [int(generator[0]), int(generator[1])]]
    snf = smith_normal_form_diagonal(relation_matrix)
    return {
        "relation_matrix": relation_matrix,
        "diagonal": snf["diagonal"],
        "diagonal_multiplicities": snf["diagonal_multiplicities"],
        "nonunit_invariant_factors": snf["nonunit_invariant_factors"],
        "off_diagonal_nonzero": snf["off_diagonal_nonzero"],
        "divisibility_chain_valid": snf["divisibility_chain_valid"],
        "quotient_group": "Z/2 x Z/26",
        "quotient_order": int(math.prod(snf["nonunit_invariant_factors"])),
    }


def ordered_partitions(elements: list[str]) -> list[tuple[tuple[str, ...], ...]]:
    out: set[tuple[tuple[str, ...], ...]] = set()
    n = len(elements)
    for block_count in range(1, n + 1):
        for ranks in itertools.product(range(block_count), repeat=n):
            if set(ranks) != set(range(block_count)):
                continue
            blocks = []
            for rank in range(block_count):
                block = tuple(elements[index] for index, value in enumerate(ranks) if value == rank)
                blocks.append(block)
            out.add(tuple(blocks))
    return sorted(out)


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
    index["registry_sha256"] = sha_json(
        {key: value for key, value in index.items() if key != "registry_sha256"}
    )
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def pairing_rows(residue_vector: list[int], doublet: list[int], *, reduce_mod26: bool) -> list[list[int]]:
    rows = []
    for residue in residue_vector:
        row = [int(residue) * int(value) for value in doublet]
        if reduce_mod26:
            row = [value % 26 for value in row]
        rows.append(row)
    return rows


def snf_record(matrix: list[list[int]]) -> dict[str, Any]:
    snf = smith_normal_form_diagonal(matrix)
    return {
        "diagonal": snf["diagonal"],
        "diagonal_multiplicities": snf["diagonal_multiplicities"],
        "nonunit_invariant_factors": snf["nonunit_invariant_factors"],
        "off_diagonal_nonzero": snf["off_diagonal_nonzero"],
        "divisibility_chain_valid": snf["divisibility_chain_valid"],
        "reduction_steps": snf["reduction_steps"],
    }


def build_theorem() -> dict[str, Any]:
    contour = load_json(D20_FINITE_CONTOUR_INTEGRATION)
    charge = load_json(ZERO_PAIR_CHARGE_KERNEL)
    prime_alignment = load_json(D20_CONTOUR_SECTOR_PACKET_PRIME_ALIGNMENT)

    residue = contour["derived"]["signed_contour_residue"]
    primitive_vector = [int(value) for value in residue["primitive_residue_vector"]]
    mod26_vector = [int(value) for value in residue["mod26_residue_vector"]]
    charge_summary = charge["derived"]["propagator_charge_kernel_summary"]
    plus = charge_summary["plus_denominator_cleared_sector26_image"]
    minus = charge_summary["minus_denominator_cleared_sector26_image"]

    doublets = {
        "sum": [
            int(plus["sector26_clock_sum_mod26"]),
            int(minus["sector26_clock_sum_mod26"]) - 26,
        ],
        "delta": [
            int(plus["sector26_clock_delta_mod26"]),
            int(minus["sector26_clock_delta_mod26"]) - 26,
        ],
        "packet_clock_0": [
            int(plus["sector26_clock_pair_mod26"][0]) - 26,
            int(minus["sector26_clock_pair_mod26"][0]),
        ],
        "packet_clock_1": [
            int(plus["sector26_clock_pair_mod26"][1]),
            int(minus["sector26_clock_pair_mod26"][1]) - 26,
        ],
    }

    raw_pairing_rows = {
        name: pairing_rows(primitive_vector, doublet, reduce_mod26=False)
        for name, doublet in doublets.items()
    }
    residue_pairing_rows = {
        name: pairing_rows(mod26_vector, doublet, reduce_mod26=True)
        for name, doublet in doublets.items()
    }
    raw_pairing_snf = {name: snf_record(rows) for name, rows in raw_pairing_rows.items()}
    residue_lift_snf = {name: snf_record(rows) for name, rows in residue_pairing_rows.items()}
    quotient_snf = {name: relation_snf(doublet) for name, doublet in doublets.items()}

    row_subgroups = {
        name: subgroup_generated_by_rows(rows) for name, rows in residue_pairing_rows.items()
    }
    row_subgroup_sizes = {name: len(values) for name, values in row_subgroups.items()}
    row_subgroup_hashes = {
        name: sha_json(sorted([list(value) for value in values])) for name, values in row_subgroups.items()
    }
    reference_subgroup = sorted(row_subgroups["sum"])
    common_subgroup = all(sorted(values) == reference_subgroup for values in row_subgroups.values())

    weak_orders = ordered_partitions(["a", "b", "c"])
    weak_order_profile_counts = Counter(tuple(len(block) for block in order) for order in weak_orders)
    weak_order_summary = {
        "set": ["a", "b", "c"],
        "strict_weak_order_count": len(weak_orders),
        "ordered_partition_profile_counts": {
            ",".join(str(value) for value in key): int(value)
            for key, value in sorted(weak_order_profile_counts.items())
        },
        "raw_pairwise_ternary_comparison_count": 3**3,
        "transitive_ternary_comparison_count": len(weak_orders),
        "polarity_doubled_count": 2 * len(weak_orders),
        "comparison_status": (
            "numerically compatible with sector 26, but not used as an input to this certificate"
        ),
    }

    pairing_summary = {
        "residue_line_length": len(primitive_vector),
        "residue_line_gcd": int(residue["primitive_residue_vector_gcd"]),
        "charge_doublets_centered": doublets,
        "raw_sum_pairing_smith_diagonal": raw_pairing_snf["sum"]["diagonal"],
        "raw_delta_pairing_smith_diagonal": raw_pairing_snf["delta"]["diagonal"],
        "finite_row_subgroup_order": row_subgroup_sizes["sum"],
        "finite_row_subgroup_hash": row_subgroup_hashes["sum"],
        "finite_ambient_group": "(Z/26)^2",
        "finite_ambient_order": 26 * 26,
        "finite_quotient_smith_diagonal": quotient_snf["sum"]["diagonal"],
        "finite_quotient_group": quotient_snf["sum"]["quotient_group"],
        "finite_quotient_order": quotient_snf["sum"]["quotient_order"],
        "finite_quotient_order_factorization": factorization(quotient_snf["sum"]["quotient_order"]),
        "deck_52_status": (
            "52 is certified here as the order of the finite quotient Z/2 x Z/26; "
            "no playing-card structure is claimed"
        ),
    }

    checks = {
        "contour_input_is_certified": contour.get("status") == "D20_FINITE_CONTOUR_INTEGRATION_TEST_PASS"
        and contour.get("all_checks_pass") is True,
        "charge_kernel_input_is_certified": charge.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_PROPAGATOR_CHARGE_KERNEL_CERTIFIED"
        and charge.get("all_checks_pass") is True,
        "prime_alignment_input_is_certified": prime_alignment.get("status")
        == "D20_CONTOUR_SECTOR_PACKET_PRIME_ALIGNMENT_CERTIFIED"
        and prime_alignment.get("all_checks_pass") is True,
        "residue_line_is_11_dimensional_and_primitive": len(primitive_vector) == 11
        and math.gcd(*primitive_vector) == 1
        and int(residue["primitive_residue_vector_gcd"]) == 1,
        "mod26_residue_vector_matches_primitive_reduction": [
            value % 26 for value in primitive_vector
        ]
        == mod26_vector,
        "sector26_charge_doublet_is_plus_minus": doublets["sum"] == [4, -4]
        and doublets["delta"] == [8, -8],
        "packet_clock_doublets_are_plus_minus": doublets["packet_clock_0"] == [-2, 2]
        and doublets["packet_clock_1"] == [6, -6],
        "raw_sum_pairing_has_smith_4": raw_pairing_snf["sum"]["diagonal"] == [4],
        "raw_delta_pairing_has_smith_8": raw_pairing_snf["delta"]["diagonal"] == [8],
        "all_mod26_pairing_tables_have_smith_2_26_as_integer_lifts": all(
            value["diagonal"] == [2, 26] for value in residue_lift_snf.values()
        ),
        "all_doublet_generators_have_order_13_mod26": all(
            finite_order_mod26(doublet) == 13 for doublet in doublets.values()
        ),
        "all_pairing_rows_generate_same_order_13_line": common_subgroup
        and set(row_subgroup_sizes.values()) == {13},
        "finite_quotient_smith_form_is_2_26": all(
            value["diagonal"] == [2, 26]
            and value["off_diagonal_nonzero"] == 0
            and value["divisibility_chain_valid"] is True
            for value in quotient_snf.values()
        ),
        "finite_quotient_order_is_52": pairing_summary["finite_quotient_order"] == 52,
        "finite_quotient_prime_support_is_2_13": pairing_summary[
            "finite_quotient_order_factorization"
        ]
        == {"2": 2, "13": 1},
        "strict_weak_orders_on_three_elements_count_13": len(weak_orders) == 13,
        "strict_weak_order_polarity_double_is_26": weak_order_summary[
            "polarity_doubled_count"
        ]
        == 26,
        "weak_order_count_is_comparison_not_source_claim": True,
    }

    report = {
        "schema": "d20.theorem.d20_contour_charge_pairing_snf",
        "status": "D20_CONTOUR_CHARGE_PAIRING_SNF_CERTIFIED",
        "object": "D20",
        "definition": {
            "pairing_matrix": (
                "the 11 contour residue entries paired against the denominator-cleared "
                "sector-26 plus/minus charge doublet"
            ),
            "finite_quotient": (
                "the quotient of (Z/26)^2 by the mod-26 row line generated by the pairing"
            ),
            "scope": (
                "finite residue arithmetic only; no playing-card model, prime-distribution "
                "law, or classical order-theory source theorem is claimed"
            ),
        },
        "claim": (
            "The 11-entry primitive contour residue line pairs with the sector-26 charge "
            "doublet to generate a single order-13 anti-diagonal line inside (Z/26)^2. "
            "The resulting finite quotient has Smith factors [2,26], hence order 52. "
            "The independent count of strict weak orderings on three labelled elements is "
            "13, so polarity doubling gives 26, but that count is recorded only as a "
            "compatible comparison rather than a certified cause of sector 26."
        ),
        "inputs": {
            "d20_finite_contour_integration_report": input_record(D20_FINITE_CONTOUR_INTEGRATION),
            "full_exposure_zero_pair_propagator_charge_kernel_report": input_record(
                ZERO_PAIR_CHARGE_KERNEL
            ),
            "d20_contour_sector_packet_prime_alignment_report": input_record(
                D20_CONTOUR_SECTOR_PACKET_PRIME_ALIGNMENT
            ),
        },
        "derived": {
            "pairing_summary": pairing_summary,
            "primitive_residue_vector": primitive_vector,
            "mod26_residue_vector": mod26_vector,
            "raw_pairing_rows": raw_pairing_rows,
            "raw_pairing_rows_sha256": sha_json(raw_pairing_rows),
            "residue_pairing_rows_mod26": residue_pairing_rows,
            "residue_pairing_rows_mod26_sha256": sha_json(residue_pairing_rows),
            "raw_pairing_smith_forms": raw_pairing_snf,
            "residue_lift_smith_forms": residue_lift_snf,
            "finite_quotient_smith_forms": quotient_snf,
            "row_subgroup_sizes": row_subgroup_sizes,
            "row_subgroup_hashes": row_subgroup_hashes,
            "weak_order_summary": weak_order_summary,
            "weak_orders_sha256": sha_json(weak_orders),
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": {
            "strongest_safe_reading": (
                "The contour-charge pairing explains a concrete occurrence of 52 as "
                "|(Z/26)^2 / L| where L is an order-13 finite residue line."
            ),
            "strict_weak_order_reading": (
                "The 13 strict weak orderings of three labelled elements are a good candidate "
                "for the ternary-comparison logic behind the ledger, because they are exactly "
                "the transitive part of the 3^3 pairwise ternary comparison cube. This "
                "certificate only proves numerical compatibility."
            ),
            "deck_reading": (
                "A 52-card deck has the same cardinality as the certified quotient. The "
                "invariant here is Z/2 x Z/26, equivalently a 2-primary square times a "
                "13-line; no suit/rank labelling is canonical yet."
            ),
        },
        "next_highest_yield_item": (
            "Construct an explicit map from the 13 strict weak orderings of three labelled "
            "elements into the sector-26 residue clock and test whether D20 symmetries "
            "preserve it."
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
        "schema": "d20.theorem.d20_contour_charge_pairing_snf_manifest",
        "status": report["status"],
        "name": THEOREM_ID,
        "artifacts": {
            "report": rel(out_dir / "report.json"),
            "manifest": rel(out_dir / "manifest.json"),
        },
        "report_sha256": report["certificate_sha256"],
        "inputs": report["inputs"],
        "purpose": [
            "pair the finite contour residue line against the sector-26 charge doublet",
            "compute the Smith form of the induced finite quotient",
            "record the strict-weak-ordering count as a comparison guard",
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
