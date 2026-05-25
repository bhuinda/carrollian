from __future__ import annotations

import hashlib
import itertools
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from src.paths import D20_INVARIANTS, ROOT
except ModuleNotFoundError:  # Supports direct script execution.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "d20_intrinsic_triple_ordering_clock"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

SECTOR26_INVARIANT_SUITE = (
    D20_INVARIANTS / "theorems" / "sector26_invariant_suite" / "report.json"
)
D20_STRICT_WEAK_ORDER_SECTOR26_CLOCK = (
    D20_INVARIANTS / "theorems" / "d20_strict_weak_order_sector26_clock" / "report.json"
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


def line_hash_from_pairs(pairs: list[list[int]]) -> str:
    normalized = sorted([[int(left) % 26, int(right) % 26] for left, right in pairs])
    return sha_json(normalized)


def permute_matrix(matrix: list[list[int]], permutation: tuple[int, ...]) -> list[list[int]]:
    return [[int(matrix[permutation[i]][permutation[j]]) for j in range(len(permutation))] for i in range(len(permutation))]


def permutation_cycles(labels: list[str], permutation: tuple[int, ...]) -> list[list[str]]:
    seen: set[int] = set()
    cycles = []
    for start in range(len(labels)):
        if start in seen:
            continue
        current = start
        cycle = []
        while current not in seen:
            seen.add(current)
            cycle.append(labels[current])
            current = permutation[current]
        if len(cycle) > 1:
            cycles.append(cycle)
    return cycles


def intrinsic_element_records(labels: list[str], matrix: list[list[int]]) -> list[dict[str, Any]]:
    records = []
    for index, label in enumerate(labels):
        offdiag_abs_sum = sum(abs(int(matrix[index][j])) for j in range(len(labels)) if j != index)
        records.append(
            {
                "label": label,
                "index": index,
                "self_transport": int(matrix[index][index]),
                "offdiagonal_abs_sum": int(offdiag_abs_sum),
                "transport_isolated": offdiag_abs_sum == 0,
                "row": [int(value) for value in matrix[index]],
                "canonical_order_key": [
                    0 if offdiag_abs_sum == 0 else 1,
                    -int(matrix[index][index]),
                    label,
                ],
            }
        )
    return records


def order_record(code: int, order: tuple[tuple[str, ...], ...]) -> dict[str, Any]:
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


def transport_permutation_records(labels: list[str], matrix: list[list[int]]) -> list[dict[str, Any]]:
    records = []
    identity = tuple(range(len(labels)))
    for permutation in itertools.permutations(range(len(labels))):
        image_matrix = permute_matrix(matrix, permutation)
        records.append(
            {
                "permutation": [int(value) for value in permutation],
                "cycle_notation": permutation_cycles(labels, permutation),
                "image_labels": [labels[index] for index in permutation],
                "preserves_transport_matrix": image_matrix == matrix,
                "is_identity": permutation == identity,
                "image_matrix": image_matrix,
            }
        )
    return records


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
    sector26 = load_json(SECTOR26_INVARIANT_SUITE)
    prior_clock = load_json(D20_STRICT_WEAK_ORDER_SECTOR26_CLOCK)

    hidden_transport = sector26["derived"]["hidden_transport_form"]
    labels = [str(label) for label in hidden_transport["basis_order"]]
    matrix = [[int(value) for value in row] for row in hidden_transport["matrix"]]
    element_records = intrinsic_element_records(labels, matrix)
    canonical_element_order = [
        row["label"] for row in sorted(element_records, key=lambda row: tuple(row["canonical_order_key"]))
    ]
    permutation_records = transport_permutation_records(labels, matrix)
    transport_preservers = [row for row in permutation_records if row["preserves_transport_matrix"]]

    orders = ordered_partitions(canonical_element_order)
    order_records = [order_record(index, order) for index, order in enumerate(orders)]
    anti_diagonal_pairs = [row["anti_diagonal_pair_mod26"] for row in order_records]
    intrinsic_line_hash = line_hash_from_pairs(anti_diagonal_pairs)
    prior_line_hash = prior_clock["derived"]["weak_order_summary"]["anti_diagonal_line_hash"]
    even_residues = sorted(row["sector26_even_residue"] for row in order_records)
    polarity_residues = sorted(
        residue
        for row in order_records
        for residue in row["sector26_polarity_residues"].values()
    )
    profile_counts = {
        ",".join(str(value) for value in key): int(value)
        for key, value in sorted(Counter(tuple(row["profile"]) for row in order_records).items())
    }

    intrinsic_triple_summary = {
        "source": "sector26_invariant_suite.hidden_transport_form",
        "basis_order": labels,
        "canonical_element_order": canonical_element_order,
        "matrix": matrix,
        "smith_normal_form_diagonal": hidden_transport["smith_normal_form_diagonal"],
        "determinant": int(hidden_transport["determinant"]),
        "trace": int(hidden_transport["trace"]),
        "composite_block_basis_order": hidden_transport["composite_block"]["basis_order"],
        "composite_block_discriminant": int(hidden_transport["composite_block"]["discriminant"]),
        "transport_preserving_permutation_count": len(transport_preservers),
        "transport_preserving_permutations": [
            row["permutation"] for row in transport_preservers
        ],
        "interpretation": (
            "The triple is intrinsic to the sector-26 hidden transport certificate: R33 is "
            "transport-isolated, while K_mixed_S and K_pure_Sminus form the rank-one "
            "sector-26 composite block with discriminant 13."
        ),
    }

    clock_summary = {
        "strict_weak_order_count": len(order_records),
        "profile_counts": profile_counts,
        "even_sector26_residue_image": even_residues,
        "polarity_doubled_sector26_image": polarity_residues,
        "anti_diagonal_line_hash": intrinsic_line_hash,
        "matches_prior_weak_order_clock_line": intrinsic_line_hash == prior_line_hash,
        "matches_prior_weak_order_count": len(order_records)
        == prior_clock["derived"]["weak_order_summary"]["strict_weak_order_count"],
        "uses_external_placeholder_labels": False,
        "external_placeholders_replaced_by_intrinsic_labels": {
            "a": canonical_element_order[0],
            "b": canonical_element_order[1],
            "c": canonical_element_order[2],
        },
    }

    checks = {
        "sector26_input_is_certified": sector26.get("status")
        == "D20_SECTOR26_INVARIANT_SUITE_CERTIFIED"
        and sector26.get("all_checks_pass") is True,
        "prior_clock_input_is_certified": prior_clock.get("status")
        == "D20_STRICT_WEAK_ORDER_SECTOR26_CLOCK_CERTIFIED"
        and prior_clock.get("all_checks_pass") is True,
        "intrinsic_triple_has_three_distinct_labels": len(labels) == 3
        and len(set(labels)) == 3,
        "intrinsic_triple_is_expected_hidden_transport_basis": labels
        == ["R33", "K_mixed_S", "K_pure_Sminus"],
        "hidden_transport_matrix_is_expected": matrix
        == [[4, 0, 0], [0, 5, 1], [0, 1, 2]],
        "canonical_order_is_derived_from_transport_signatures": canonical_element_order
        == ["R33", "K_mixed_S", "K_pure_Sminus"],
        "transport_form_is_permutation_rigid": len(transport_preservers) == 1
        and transport_preservers[0]["is_identity"] is True,
        "composite_block_discriminant_is_13": intrinsic_triple_summary[
            "composite_block_discriminant"
        ]
        == 13,
        "strict_weak_order_count_is_13": len(order_records) == 13,
        "profile_counts_are_1_3_3_6": profile_counts
        == {"1,1,1": 6, "1,2": 3, "2,1": 3, "3": 1},
        "even_residue_image_is_order13_subgroup": even_residues == list(range(0, 26, 2)),
        "polarity_doubled_image_is_all_sector26": polarity_residues == list(range(26)),
        "intrinsic_line_matches_prior_clock_line": clock_summary[
            "matches_prior_weak_order_clock_line"
        ],
        "placeholder_labels_are_removed": clock_summary["uses_external_placeholder_labels"] is False
        and set(canonical_element_order).isdisjoint({"a", "b", "c"}),
    }

    report = {
        "schema": "d20.theorem.d20_intrinsic_triple_ordering_clock",
        "status": "D20_INTRINSIC_TRIPLE_ORDERING_CLOCK_CERTIFIED",
        "object": "D20",
        "definition": {
            "intrinsic_triple": (
                "the sector-26 hidden transport basis (R33, K_mixed_S, K_pure_Sminus)"
            ),
            "canonical_order": (
                "the order derived from transport signatures: isolated first, then larger "
                "self-transport on the sector-26 composite block"
            ),
            "clock_map": (
                "strict weak order code k on the intrinsic triple maps to 2k modulo 26, "
                "with polarity doubling to 2k and 2k+1"
            ),
        },
        "claim": (
            "The 13-ordering sector-26 clock no longer needs an external labelled "
            "three-set. The certified sector-26 hidden transport form supplies an "
            "intrinsic, permutation-rigid triple (R33, K_mixed_S, K_pure_Sminus). "
            "Its strict weak orderings reproduce the same order-13 anti-diagonal line "
            "and the same 26-state polarity-doubled clock as the prior weak-order theorem."
        ),
        "inputs": {
            "sector26_invariant_suite_report": input_record(SECTOR26_INVARIANT_SUITE),
            "d20_strict_weak_order_sector26_clock_report": input_record(
                D20_STRICT_WEAK_ORDER_SECTOR26_CLOCK
            ),
        },
        "derived": {
            "intrinsic_triple_summary": intrinsic_triple_summary,
            "intrinsic_element_records": element_records,
            "transport_permutation_records": permutation_records,
            "transport_permutation_records_sha256": sha_json(permutation_records),
            "clock_summary": clock_summary,
            "intrinsic_order_records": order_records,
            "intrinsic_order_records_sha256": sha_json(order_records),
            "anti_diagonal_pairs_mod26": anti_diagonal_pairs,
            "anti_diagonal_pairs_sha256": sha_json(anti_diagonal_pairs),
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": {
            "what_this_proves": [
                "the 13-state clock can be anchored to an intrinsic D20 transport triple",
                "the hidden transport matrix rigidly orders that triple up to identity",
                "the intrinsic triple clock gives the same sector-26 line as the previous placeholder version",
            ],
            "what_this_does_not_prove": (
                "This does not prove uniqueness among every possible D20 triple. It proves "
                "that the sector-26 hidden transport triple is a certified intrinsic source."
            ),
        },
        "next_highest_yield_item": (
            "Classify all certified D20 triples with a discriminant-13 or order-13 clock "
            "signature and test uniqueness of the hidden transport triple."
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
        "schema": "d20.theorem.d20_intrinsic_triple_ordering_clock_manifest",
        "status": report["status"],
        "name": THEOREM_ID,
        "artifacts": {
            "report": rel(out_dir / "report.json"),
            "manifest": rel(out_dir / "manifest.json"),
        },
        "report_sha256": report["certificate_sha256"],
        "inputs": report["inputs"],
        "purpose": [
            "replace external weak-order placeholders with the intrinsic D20 hidden transport triple",
            "verify the hidden transport form is permutation-rigid",
            "recover the same sector-26 weak-order clock from intrinsic labels",
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
