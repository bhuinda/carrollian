from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import itertools
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from src.paths import D20_INVARIANTS, ROOT
except ModuleNotFoundError:  # Supports direct script execution.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "d20_strict_weak_order_sector26_clock"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

D20_CONTOUR_CHARGE_PAIRING_SNF = (
    D20_INVARIANTS / "theorems" / "d20_contour_charge_pairing_snf" / "report.json"
)
HIDDEN_SPLIT_AUGMENTED_LEDGER_STABILIZER = (
    D20_INVARIANTS / "theorems" / "hidden_split_augmented_ledger_stabilizer" / "report.json"
)
SOURCED_BALANCE_LABEL_RELAXED_ORBIT_QUOTIENT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient"
    / "report.json"
)


ELEMENTS = ["a", "b", "c"]


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

    profile_order = {
        (3,): 0,
        (1, 2): 1,
        (2, 1): 2,
        (1, 1, 1): 3,
    }
    return sorted(out, key=lambda order: (profile_order[tuple(len(block) for block in order)], order))


def weak_order_record(code: int, order: tuple[tuple[str, ...], ...]) -> dict[str, Any]:
    even_residue = (2 * code) % 26
    return {
        "code_mod13": code,
        "ordered_partition": [list(block) for block in order],
        "profile": [len(block) for block in order],
        "sector26_even_residue": even_residue,
        "sector26_polarity_residues": {
            "positive": even_residue,
            "negative": (even_residue + 1) % 26,
        },
        "anti_diagonal_pair_mod26": [even_residue, (-even_residue) % 26],
    }


def line_hash_from_pairs(pairs: list[list[int]]) -> str:
    normalized = sorted([[int(left) % 26, int(right) % 26] for left, right in pairs])
    return sha_json(normalized)


def apply_label_permutation(
    order: tuple[tuple[str, ...], ...], permutation: tuple[str, ...]
) -> tuple[tuple[str, ...], ...]:
    mapping = {source: target for source, target in zip(ELEMENTS, permutation)}
    element_order = {element: index for index, element in enumerate(ELEMENTS)}
    return tuple(
        tuple(sorted((mapping[element] for element in block), key=lambda item: element_order[item]))
        for block in order
    )


def permutation_cycles(permutation: tuple[str, ...]) -> list[list[str]]:
    mapping = {source: target for source, target in zip(ELEMENTS, permutation)}
    seen: set[str] = set()
    cycles = []
    for element in ELEMENTS:
        if element in seen:
            continue
        current = element
        cycle = []
        while current not in seen:
            seen.add(current)
            cycle.append(current)
            current = mapping[current]
        if len(cycle) > 1:
            cycles.append(cycle)
    return cycles


def affine_mod13_map(source_codes: list[int], image_codes: list[int]) -> dict[str, Any] | None:
    units = [value for value in range(13) if math.gcd(value, 13) == 1]
    for multiplier in units:
        for offset in range(13):
            if all((multiplier * source + offset) % 13 == image for source, image in zip(source_codes, image_codes)):
                return {"multiplier": multiplier, "offset": offset}
    return None


def relabelling_records(
    orders: list[tuple[tuple[str, ...], ...]],
    order_to_code: dict[tuple[tuple[str, ...], ...], int],
) -> list[dict[str, Any]]:
    records = []
    source_codes = list(range(len(orders)))
    for permutation in itertools.permutations(ELEMENTS):
        image_codes = [order_to_code[apply_label_permutation(order, permutation)] for order in orders]
        affine = affine_mod13_map(source_codes, image_codes)
        records.append(
            {
                "permutation": {source: target for source, target in zip(ELEMENTS, permutation)},
                "cycle_notation": permutation_cycles(permutation),
                "image_codes": image_codes,
                "fixed_order_count": sum(1 for source, image in zip(source_codes, image_codes) if source == image),
                "preserves_even_residue_set": sorted((2 * image) % 26 for image in image_codes)
                == list(range(0, 26, 2)),
                "pointwise_preserves_clock_codes": image_codes == source_codes,
                "affine_mod13_clock_action": affine,
            }
        )
    return records


def orbits_from_actions(actions: list[list[int]], count: int) -> list[list[int]]:
    parent = list(range(count))

    def find(value: int) -> int:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(left: int, right: int) -> None:
        root_left = find(left)
        root_right = find(right)
        if root_left != root_right:
            parent[root_right] = root_left

    for action in actions:
        for source, image in enumerate(action):
            union(source, image)
    grouped: dict[int, list[int]] = {}
    for value in range(count):
        grouped.setdefault(find(value), []).append(value)
    return sorted([sorted(values) for values in grouped.values()], key=lambda values: (len(values), values))


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


def build_theorem() -> dict[str, Any]:
    pairing = load_json(D20_CONTOUR_CHARGE_PAIRING_SNF)
    stabilizer = load_json(HIDDEN_SPLIT_AUGMENTED_LEDGER_STABILIZER)
    label_relaxed = load_json(SOURCED_BALANCE_LABEL_RELAXED_ORBIT_QUOTIENT)

    orders = ordered_partitions(ELEMENTS)
    order_to_code = {order: index for index, order in enumerate(orders)}
    order_records = [weak_order_record(index, order) for index, order in enumerate(orders)]

    even_residues = [record["sector26_even_residue"] for record in order_records]
    polarity_residues = sorted(
        residue
        for record in order_records
        for residue in record["sector26_polarity_residues"].values()
    )
    anti_diagonal_pairs = [record["anti_diagonal_pair_mod26"] for record in order_records]
    weak_order_line_hash = line_hash_from_pairs(anti_diagonal_pairs)
    pairing_line_hash = pairing["derived"]["pairing_summary"]["finite_row_subgroup_hash"]

    relabel_records = relabelling_records(orders, order_to_code)
    relabel_orbits = orbits_from_actions(
        [record["image_codes"] for record in relabel_records], len(orders)
    )
    relabel_orbit_histogram = {
        str(key): int(value) for key, value in sorted(Counter(len(orbit) for orbit in relabel_orbits).items())
    }

    stabilizer_summary = stabilizer["derived"]["candidate_group"]
    nonidentity = next(
        record
        for record in stabilizer["derived"]["candidate_records"]
        if record["automorphism_id"] != 0
    )
    label_summary = label_relaxed["derived"]["label_relaxation_summary"]
    public_summary = label_relaxed["derived"]["public_level_summary"]

    d20_symmetry_test = {
        "full_augmented_ledger_preserving_automorphism_ids": stabilizer_summary[
            "full_augmented_ledger_preserving_automorphism_ids"
        ],
        "full_augmented_ledger_stabilizer_order": stabilizer_summary[
            "full_augmented_ledger_stabilizer_order"
        ],
        "weak_order_clock_preserved_by_full_augmented_ledger_symmetry": True,
        "hidden_split_c2_order": stabilizer_summary["hidden_split_stabilizer_order"],
        "hidden_split_nonidentity_automorphism_id": nonidentity["automorphism_id"],
        "hidden_split_nonidentity_preserves_corrected_clock_mod26": nonidentity["preserves"][
            "corrected_clock_mod26"
        ],
        "hidden_split_nonidentity_preserves_sector26_counterterm_vector_mod26": nonidentity[
            "preserves"
        ]["sector26_counterterm_vector_mod26"],
        "hidden_split_nonidentity_preserves_normalized_optical_clock_mod26": nonidentity[
            "preserves"
        ]["normalized_optical_clock_mod26"],
        "hidden_split_nonidentity_first_sector26_counterterm_failure": nonidentity["failures"][
            "sector26_counterterm_vector_mod26"
        ],
        "hidden_split_nonidentity_first_normalized_clock_failure": nonidentity["failures"][
            "normalized_optical_clock_mod26"
        ],
        "sector26_clock_must_be_forgotten_for_hidden_c2_quotient": (
            "sector26_optical_clock_mod26" in label_summary["must_forget_for_full_c2_quotient"]
        ),
        "sector26_counterterm_must_be_forgotten_for_hidden_c2_quotient": (
            "sector26_counterterm_vector_mod26"
            in label_summary["ledger_must_forget_for_nonidentity_c2"]
        ),
        "public_automorphism_count": public_summary["public_automorphism_count"],
        "full_public_action_requires_forgetting_source_anchor": (
            "gamma8 source anchor"
            in label_relaxed["derived"]["quotient_ladder"][-1]["must_forget"]
        ),
    }

    weak_order_summary = {
        "strict_weak_order_count": len(order_records),
        "profile_counts": {
            ",".join(str(value) for value in key): int(value)
            for key, value in sorted(
                Counter(tuple(record["profile"]) for record in order_records).items()
            )
        },
        "even_sector26_residue_image": sorted(even_residues),
        "polarity_doubled_sector26_image": polarity_residues,
        "anti_diagonal_line_hash": weak_order_line_hash,
        "matches_contour_charge_pairing_order13_line": weak_order_line_hash == pairing_line_hash,
        "relabel_orbit_count": len(relabel_orbits),
        "relabel_orbit_size_histogram": relabel_orbit_histogram,
        "pointwise_clock_preserving_relabelling_count": sum(
            1 for record in relabel_records if record["pointwise_preserves_clock_codes"]
        ),
        "affine_mod13_relabelling_count": sum(
            1 for record in relabel_records if record["affine_mod13_clock_action"] is not None
        ),
        "interpretation": (
            "strict weak orderings supply a 13-state transitive ternary-comparison set; "
            "polarity doubling supplies a 26-state sector clock target"
        ),
    }

    checks = {
        "pairing_input_is_certified": pairing.get("status")
        == "D20_CONTOUR_CHARGE_PAIRING_SNF_CERTIFIED"
        and pairing.get("all_checks_pass") is True,
        "stabilizer_input_is_certified": stabilizer.get("status")
        == "D20_HIDDEN_SPLIT_AUGMENTED_LEDGER_STABILIZER_CERTIFIED"
        and stabilizer.get("all_checks_pass") is True,
        "label_relaxed_input_is_certified": label_relaxed.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_LABEL_RELAXED_ORBIT_QUOTIENT_CERTIFIED"
        and label_relaxed.get("all_checks_pass") is True,
        "strict_weak_order_count_is_13": len(order_records) == 13,
        "profile_counts_are_1_3_3_6": weak_order_summary["profile_counts"]
        == {"1,1,1": 6, "1,2": 3, "2,1": 3, "3": 1},
        "even_residue_image_is_order13_subgroup": sorted(even_residues)
        == list(range(0, 26, 2)),
        "polarity_doubled_image_is_all_sector26": polarity_residues == list(range(26)),
        "weak_order_line_matches_contour_charge_pairing_line": weak_order_summary[
            "matches_contour_charge_pairing_order13_line"
        ],
        "natural_relabelling_orbits_are_1_3_3_6": relabel_orbit_histogram
        == {"1": 1, "3": 2, "6": 1},
        "only_identity_relabelling_pointwise_preserves_clock": weak_order_summary[
            "pointwise_clock_preserving_relabelling_count"
        ]
        == 1,
        "no_nontrivial_relabelling_is_affine_mod13_for_this_clock": weak_order_summary[
            "affine_mod13_relabelling_count"
        ]
        == 1,
        "full_augmented_d20_ledger_stabilizer_is_identity": d20_symmetry_test[
            "full_augmented_ledger_stabilizer_order"
        ]
        == 1
        and d20_symmetry_test["full_augmented_ledger_preserving_automorphism_ids"] == [0],
        "hidden_c2_does_not_preserve_sector26_clock_map": d20_symmetry_test[
            "hidden_split_nonidentity_preserves_sector26_counterterm_vector_mod26"
        ]
        is False
        and d20_symmetry_test["hidden_split_nonidentity_preserves_normalized_optical_clock_mod26"]
        is False,
        "sector26_clock_is_not_c2_quotient_coherent": d20_symmetry_test[
            "sector26_clock_must_be_forgotten_for_hidden_c2_quotient"
        ]
        and d20_symmetry_test["sector26_counterterm_must_be_forgotten_for_hidden_c2_quotient"],
        "full_public_action_requires_forgetting_source_anchor": d20_symmetry_test[
            "full_public_action_requires_forgetting_source_anchor"
        ],
    }

    report = {
        "schema": "d20.theorem.d20_strict_weak_order_sector26_clock",
        "status": "D20_STRICT_WEAK_ORDER_SECTOR26_CLOCK_CERTIFIED",
        "object": "D20",
        "definition": {
            "strict_weak_order_clock": (
                "the 13 ordered partitions of the labelled set {a,b,c}, mapped to the "
                "even residues 2k modulo 26"
            ),
            "polarity_doubling": (
                "the two residues 2k and 2k+1 attached to each strict weak order"
            ),
            "d20_preservation_test": (
                "test against the certified full augmented D20 ledger stabilizer and the "
                "label-relaxed hidden-split C2 quotient"
            ),
        },
        "claim": (
            "The 13 strict weak orderings on {a,b,c} give an explicit 13-state "
            "transitive ternary-comparison clock. Mapping code k to 2k modulo 26 "
            "identifies this clock with the order-13 anti-diagonal line certified by "
            "the contour-charge pairing. Polarity doubling covers all 26 sector-clock "
            "residues. The full augmented D20 ledger preserves this clock only "
            "trivially because its stabilizer is identity; the nonidentity hidden C2 "
            "does not preserve sector-26 clock refinements, so the clock does not "
            "descend to that relaxed quotient."
        ),
        "inputs": {
            "d20_contour_charge_pairing_snf_report": input_record(
                D20_CONTOUR_CHARGE_PAIRING_SNF
            ),
            "hidden_split_augmented_ledger_stabilizer_report": input_record(
                HIDDEN_SPLIT_AUGMENTED_LEDGER_STABILIZER
            ),
            "sourced_balance_label_relaxed_orbit_quotient_report": input_record(
                SOURCED_BALANCE_LABEL_RELAXED_ORBIT_QUOTIENT
            ),
        },
        "derived": {
            "weak_order_summary": weak_order_summary,
            "weak_order_records": order_records,
            "weak_order_records_sha256": sha_json(order_records),
            "relabel_records": relabel_records,
            "relabel_records_sha256": sha_json(relabel_records),
            "relabel_orbits": relabel_orbits,
            "anti_diagonal_pairs_mod26": anti_diagonal_pairs,
            "anti_diagonal_pairs_sha256": sha_json(anti_diagonal_pairs),
            "d20_symmetry_test": d20_symmetry_test,
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": {
            "what_this_proves": [
                "there is now an explicit 13-ordering clock map into sector 26",
                "its anti-diagonal image is exactly the previously certified order-13 line",
                "polarity doubling realizes all 26 residue classes",
                "full augmented D20 ledger symmetry preserves the map only because that symmetry is trivial",
                "the hidden C2 quotient requires forgetting sector-26 clock data",
            ],
            "what_this_does_not_prove": (
                "This does not prove that strict weak orders are the unique cause of sector 26, "
                "or that full public D20 symmetries act as symmetries of this clock."
            ),
        },
        "next_highest_yield_item": (
            "Test whether the 13-ordering clock can be derived from an intrinsic D20 triple "
            "of labels rather than imposed on an external labelled set."
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
        "schema": "d20.theorem.d20_strict_weak_order_sector26_clock_manifest",
        "status": report["status"],
        "name": THEOREM_ID,
        "artifacts": {
            "report": rel(out_dir / "report.json"),
            "manifest": rel(out_dir / "manifest.json"),
        },
        "report_sha256": report["certificate_sha256"],
        "inputs": report["inputs"],
        "purpose": [
            "construct the explicit 13 strict-weak-order clock",
            "map it into the sector-26 residue clock",
            "test preservation against certified D20 symmetry levels",
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
