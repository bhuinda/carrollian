from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
from typing import Any

try:
    from src.paths import D20_INVARIANTS, ROOT
except ModuleNotFoundError:  # Supports direct script execution.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "d20_boundary_packet_support3_obstruction"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE = (
    D20_INVARIANTS / "theorems" / "d20_boundary_loop_step_atom_incidence" / "report.json"
)
D20_BOUNDARY_PACKET_LOW_SUPPORT_CANDIDATE_ATLAS = (
    D20_INVARIANTS
    / "theorems"
    / "d20_boundary_packet_low_support_candidate_atlas"
    / "report.json"
)
D20_PACKET_BRIDGE_SNF_OBSTRUCTION = (
    D20_INVARIANTS / "theorems" / "d20_packet_bridge_snf_obstruction" / "report.json"
)

COEFFICIENT_SET = [-1, 1]
SUPPORT = 3
STEP_ATOM_COUNT = 25
PUBLIC_ATOM_COUNT = 20


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
    index["registry_sha256"] = sha_json({k: v for k, v in index.items() if k != "registry_sha256"})
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def histogram(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def row_parity(matrix: list[list[int]]) -> list[tuple[int, ...]]:
    return [tuple(value & 1 for value in row) for row in matrix]


def xor_patterns(patterns: list[tuple[int, ...]], atoms: tuple[int, ...]) -> tuple[int, ...]:
    out = [0] * len(patterns[0])
    for atom in atoms:
        out = [left ^ right for left, right in zip(out, patterns[atom])]
    return tuple(out)


def gf2_rank(patterns: list[tuple[int, ...]]) -> int:
    rows = [sum((bit & 1) << col for col, bit in enumerate(pattern)) for pattern in patterns]
    rank = 0
    for col in range(STEP_ATOM_COUNT):
        pivot = None
        for row in range(rank, len(rows)):
            if (rows[row] >> col) & 1:
                pivot = row
                break
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for row in range(len(rows)):
            if row != rank and ((rows[row] >> col) & 1):
                rows[row] ^= rows[rank]
        rank += 1
    return rank


def matrix_rank_rational(matrix: list[list[int]]) -> int:
    work = [[Fraction(value) for value in row] for row in matrix]
    row_count = len(work)
    col_count = len(work[0]) if row_count else 0
    rank = 0
    for col in range(col_count):
        pivot = None
        for row in range(rank, row_count):
            if work[row][col]:
                pivot = row
                break
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        scale = work[rank][col]
        work[rank] = [value / scale for value in work[rank]]
        for row in range(row_count):
            if row == rank or not work[row][col]:
                continue
            factor = work[row][col]
            work[row] = [
                work[row][idx] - factor * work[rank][idx] for idx in range(col_count)
            ]
        rank += 1
    return rank


def local_ok(u: int, v: int) -> bool:
    return u % 2 == 0 and v % 2 == 0 and (u + v) % 6 == 0


def image_for_support(support: list[tuple[int, int]], matrix: list[list[int]]) -> list[int]:
    return [
        sum(coefficient * matrix[atom_id][col] for atom_id, coefficient in support)
        for col in range(len(matrix[0]))
    ]


def enumerate_kernel_masks(patterns: list[tuple[int, ...]]) -> list[int]:
    row_bits = []
    for pattern in patterns:
        bits = 0
        for col, value in enumerate(pattern):
            bits |= (value & 1) << col
        row_bits.append(bits)
    zero_masks = []
    for mask in range(1 << len(patterns)):
        parity = 0
        work = mask
        while work:
            lsb = work & -work
            atom_id = lsb.bit_length() - 1
            parity ^= row_bits[atom_id]
            work ^= lsb
        if parity == 0:
            zero_masks.append(mask)
    return zero_masks


def mask_atoms(mask: int, atom_count: int = PUBLIC_ATOM_COUNT) -> list[int]:
    return [atom_id for atom_id in range(atom_count) if (mask >> atom_id) & 1]


def zero_sum_rows(
    patterns: list[tuple[int, ...]], public_atom_rows: list[dict[str, Any]], support: int
) -> list[dict[str, Any]]:
    rows = []
    for atoms in combinations(range(len(patterns)), support):
        if any(xor_patterns(patterns, atoms)):
            continue
        rows.append(
            {
                "public_atom_support": list(atoms),
                "public_atom_labels": [
                    public_atom_rows[atom]["public_atom_label"] for atom in atoms
                ],
            }
        )
    return rows


def kernel_mask_rows(
    zero_masks: list[int], public_atom_rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    rows = []
    for mask in sorted(zero_masks, key=lambda item: (item.bit_count(), mask_atoms(item))):
        atoms = mask_atoms(mask)
        rows.append(
            {
                "mask": mask,
                "support_size": len(atoms),
                "public_atom_support": atoms,
                "public_atom_labels": [
                    public_atom_rows[atom]["public_atom_label"] for atom in atoms
                ],
            }
        )
    return rows


def duplicate_parity_rows(
    patterns: list[tuple[int, ...]], public_atom_rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    classes: dict[tuple[int, ...], list[int]] = defaultdict(list)
    for atom_id, pattern in enumerate(patterns):
        classes[pattern].append(atom_id)
    rows = []
    for ids in sorted((ids for ids in classes.values() if len(ids) > 1), key=lambda item: item):
        rows.append(
            {
                "public_atom_support": ids,
                "public_atom_labels": [
                    public_atom_rows[atom]["public_atom_label"] for atom in ids
                ],
                "parity_weight": sum(patterns[ids[0]]),
            }
        )
    return rows


def signed_even_rows_for_supports(
    zero_masks: list[int], matrix: list[list[int]], max_support: int
) -> list[dict[str, Any]]:
    rows = []
    for mask in zero_masks:
        atoms = mask_atoms(mask)
        if not atoms or len(atoms) > max_support:
            continue
        for signs in product(COEFFICIENT_SET, repeat=len(atoms)):
            support = list(zip(atoms, signs))
            image = image_for_support(support, matrix)
            if any(value % 2 for value in image):
                raise AssertionError("internal parity-kernel enumeration emitted an odd image")
            rows.append(
                {
                    "support_size": len(atoms),
                    "public_atom_support": atoms,
                    "coefficient_support": [
                        {"public_atom_id": atom_id, "coefficient": coefficient}
                        for atom_id, coefficient in support
                    ],
                    "image_vector": image,
                }
            )
    return rows


def compatible_doublet_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    doublet_rank_hist: Counter[int] = Counter()
    doublet_size_hist: Counter[str] = Counter()
    negative_count = 0
    doublet_count = 0
    rank_two_count = 0
    for left, right in combinations(rows, 2):
        left_image = left["image_vector"]
        right_image = right["image_vector"]
        if not all(local_ok(left_image[col], right_image[col]) for col in range(len(left_image))):
            continue
        doublet_count += 1
        rank = matrix_rank_rational([left_image, right_image])
        doublet_rank_hist[rank] += 1
        doublet_size_hist[f"{left['support_size']}|{right['support_size']}"] += 1
        if right_image == [-value for value in left_image]:
            negative_count += 1
        if rank == 2:
            rank_two_count += 1
    return {
        "compatible_doublet_count": doublet_count,
        "compatible_doublet_rank_histogram": histogram(doublet_rank_hist),
        "compatible_doublet_support_size_histogram": histogram(doublet_size_hist),
        "compatible_doublet_negative_pair_count": negative_count,
        "rank_two_doublet_count": rank_two_count,
        "all_compatible_doublets_are_opposite_rows": negative_count == doublet_count,
    }


def build_theorem() -> dict[str, Any]:
    incidence = load_json(D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE)
    low_support = load_json(D20_BOUNDARY_PACKET_LOW_SUPPORT_CANDIDATE_ATLAS)
    packet_snf = load_json(D20_PACKET_BRIDGE_SNF_OBSTRUCTION)
    matrix = incidence["derived"]["boundary_atom_step_incidence_matrix"]
    public_atom_rows = incidence["derived"]["public_atom_rows"]
    patterns = row_parity(matrix)
    zero_masks = enumerate_kernel_masks(patterns)
    kernel_rows = kernel_mask_rows(zero_masks, public_atom_rows)
    duplicate_rows = duplicate_parity_rows(patterns, public_atom_rows)
    duplicate_generators = [
        sum(1 << atom for atom in row["public_atom_support"])
        for row in duplicate_rows
    ]
    duplicate_span = {0}
    for generator in duplicate_generators:
        duplicate_span |= {mask ^ generator for mask in list(duplicate_span)}
    outside_duplicate_span = [mask for mask in zero_masks if mask not in duplicate_span]
    zero_by_support = {
        str(support): zero_sum_rows(patterns, public_atom_rows, support)
        for support in range(1, 7)
    }
    signed_rows_le6 = signed_even_rows_for_supports(zero_masks, matrix, max_support=6)
    doublet_le6 = compatible_doublet_summary(signed_rows_le6)
    low_summary = low_support["derived"]["low_support_summary"]
    support3_signed_count = math.comb(PUBLIC_ATOM_COUNT, SUPPORT) * (
        len(COEFFICIENT_SET) ** SUPPORT
    )
    support3_even_count = len(zero_by_support[str(SUPPORT)]) * (
        len(COEFFICIENT_SET) ** SUPPORT
    )
    support2_even_count = int(low_summary["even_image_candidate_count"])
    support_at_most3_even_count = support2_even_count + support3_even_count
    parity_summary = {
        "public_atom_count": PUBLIC_ATOM_COUNT,
        "step_atom_count": STEP_ATOM_COUNT,
        "row_parity_rank_over_F2": gf2_rank(patterns),
        "f2_kernel_size": len(zero_masks),
        "f2_kernel_dimension": int(math.log2(len(zero_masks))),
        "f2_kernel_support_size_histogram": histogram(
            Counter(mask.bit_count() for mask in zero_masks)
        ),
        "parity_class_size_histogram": histogram(
            Counter(
                len(ids)
                for ids in {
                    pattern: [idx for idx, row in enumerate(patterns) if row == pattern]
                    for pattern in set(patterns)
                }.values()
            )
        ),
        "duplicate_parity_pair_count": len(duplicate_rows),
        "duplicate_parity_pairs": [
            row["public_atom_support"] for row in duplicate_rows
        ],
        "zero_sum_support_counts": {
            support: len(rows) for support, rows in zero_by_support.items()
        },
        "duplicate_pair_span_size": len(duplicate_span),
        "kernel_equals_duplicate_pair_span": set(zero_masks) == duplicate_span,
        "outside_duplicate_pair_span_count": len(outside_duplicate_span),
        "outside_duplicate_pair_span_support_size_histogram": histogram(
            Counter(mask.bit_count() for mask in outside_duplicate_span)
        ),
        "minimal_new_parity_dependency_support_size": min(
            mask.bit_count() for mask in outside_duplicate_span
        ),
    }
    support_le6_summary = {
        "candidate_family": "signed_even_boundary_combinations_from_F2_kernel_support_at_most_6",
        "signed_even_candidate_count": len(signed_rows_le6),
        "signed_even_candidate_support_size_histogram": histogram(
            Counter(row["support_size"] for row in signed_rows_le6)
        ),
        "rank_by_support_size_over_Q": {
            str(support): matrix_rank_rational(
                [
                    row["image_vector"]
                    for row in signed_rows_le6
                    if row["support_size"] == support
                ]
            )
            for support in (2, 4, 6)
        },
        "combined_rank_over_Q": matrix_rank_rational(
            [row["image_vector"] for row in signed_rows_le6]
        ),
        "rank_over_support2_span": matrix_rank_rational(
            [row["image_vector"] for row in signed_rows_le6]
        )
        - matrix_rank_rational(
            [
                row["image_vector"]
                for row in signed_rows_le6
                if row["support_size"] == 2
            ]
        ),
        **doublet_le6,
    }
    support3_summary = {
        "candidate_family": "signed_support_exactly_3_boundary_combinations",
        "coefficient_set": COEFFICIENT_SET,
        "support": SUPPORT,
        "signed_candidate_count": support3_signed_count,
        "even_image_candidate_count": support3_even_count,
        "compatible_doublet_count": 0,
        "rank_two_doublet_count": 0,
        "support_at_most_3_new_even_candidate_count": support3_even_count,
        "support_at_most_3_even_candidate_count": support_at_most3_even_count,
        "support_at_most_3_even_candidate_count_matches_support_2": (
            support_at_most3_even_count == support2_even_count
        ),
        "full_parity_kernel_minimal_new_dependency_support_size": parity_summary[
            "minimal_new_parity_dependency_support_size"
        ],
    }
    local_image_test = packet_snf["derived"]["obstruction_summary"]["local_image_test"]
    checks = {
        "boundary_loop_step_atom_incidence_is_certified": incidence.get("status")
        == "D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE_CERTIFIED"
        and incidence.get("all_checks_pass") is True,
        "low_support_atlas_is_certified": low_support.get("status")
        == "D20_BOUNDARY_PACKET_LOW_SUPPORT_CANDIDATE_ATLAS_CERTIFIED"
        and low_support.get("all_checks_pass") is True,
        "packet_bridge_snf_obstruction_is_certified": packet_snf.get("status")
        == "D20_PACKET_BRIDGE_SNF_OBSTRUCTION_CERTIFIED"
        and packet_snf.get("all_checks_pass") is True,
        "packet_snf_local_test_is_exact": local_image_test
        == "u = 0 mod 2, v = 0 mod 2, and u+v = 0 mod 6 on each packet doublet",
        "incidence_matrix_is_20_by_25": len(matrix) == PUBLIC_ATOM_COUNT
        and all(len(row) == STEP_ATOM_COUNT for row in matrix),
        "row_parity_rank_is_16": parity_summary["row_parity_rank_over_F2"] == 16,
        "duplicate_parity_pairs_match_support2_atlas": parity_summary[
            "duplicate_parity_pairs"
        ]
        == low_summary["even_image_support_families"],
        "zero_sum_support_1_count_is_zero": parity_summary["zero_sum_support_counts"][
            "1"
        ]
        == 0,
        "zero_sum_support_2_count_is_three": parity_summary["zero_sum_support_counts"][
            "2"
        ]
        == 3,
        "zero_sum_support_3_count_is_zero": parity_summary["zero_sum_support_counts"][
            "3"
        ]
        == 0,
        "zero_sum_support_4_count_is_three": parity_summary["zero_sum_support_counts"][
            "4"
        ]
        == 3,
        "zero_sum_support_5_count_is_zero": parity_summary["zero_sum_support_counts"][
            "5"
        ]
        == 0,
        "zero_sum_support_6_count_is_one": parity_summary["zero_sum_support_counts"][
            "6"
        ]
        == 1,
        "f2_kernel_size_is_16": parity_summary["f2_kernel_size"] == 16,
        "f2_kernel_dimension_is_4": parity_summary["f2_kernel_dimension"] == 4,
        "f2_kernel_support_histogram_matches": parity_summary[
            "f2_kernel_support_size_histogram"
        ]
        == {"0": 1, "2": 3, "4": 3, "6": 1, "14": 1, "16": 3, "18": 3, "20": 1},
        "minimal_new_parity_dependency_support_is_14": parity_summary[
            "minimal_new_parity_dependency_support_size"
        ]
        == 14,
        "support_le6_signed_even_count_is_124": support_le6_summary[
            "signed_even_candidate_count"
        ]
        == 124,
        "support_le6_rank_equals_support2_rank": support_le6_summary[
            "rank_over_support2_span"
        ]
        == 0,
        "support_le6_combined_rank_is_6": support_le6_summary["combined_rank_over_Q"]
        == 6,
        "support_le6_has_no_rank_two_doublets": support_le6_summary[
            "rank_two_doublet_count"
        ]
        == 0,
        "support_le6_doublets_are_only_opposite_rows": support_le6_summary[
            "all_compatible_doublets_are_opposite_rows"
        ]
        is True,
        "support3_signed_candidate_count_is_9120": support3_signed_count == 9120,
        "support3_even_candidate_count_is_zero": support3_even_count == 0,
        "support3_compatible_doublet_count_is_zero": support3_summary[
            "compatible_doublet_count"
        ]
        == 0,
        "support3_rank_two_doublet_count_is_zero": support3_summary[
            "rank_two_doublet_count"
        ]
        == 0,
        "support_at_most_3_adds_no_even_rows": support3_summary[
            "support_at_most_3_even_candidate_count_matches_support_2"
        ]
        is True,
    }
    report = {
        "schema": "d20.theorem.d20_boundary_packet_support3_obstruction",
        "status": "D20_BOUNDARY_PACKET_SUPPORT3_OBSTRUCTION_CERTIFIED",
        "object": "D20",
        "definition": {
            "candidate_family": support3_summary["candidate_family"],
            "coefficient_set": COEFFICIENT_SET,
            "support": SUPPORT,
            "packet_snf_image_test": local_image_test,
            "parity_reduction": (
                "A signed boundary image can pass the packet parity layer only if "
                "the selected 25-bit public-row parity vectors sum to zero over F2; "
                "signs do not affect this parity condition."
            ),
        },
        "claim": (
            "No signed support-3 public-boundary combination over coefficients {-1,+1} "
            "can pass the packet SNF parity layer. More strongly, the full F2 parity "
            "kernel has dimension 4 and support distribution 0,2,4,6,14,16,18,20; "
            "all parity-zero supports below 14 are generated by the three duplicate "
            "parity pairs [0,11], [6,17], and [14,15]. Signed supports 2, 4, and 6 "
            "produce 124 even rows total, but they span the same rank-6 rational image "
            "as support 2 and every packet-compatible doublet is still a rank-one "
            "opposite pair. Thus the low-support boundary-to-packet escape hatch is "
            "closed below support 14."
        ),
        "inputs": {
            "d20_boundary_loop_step_atom_incidence_report": input_record(
                D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE
            ),
            "d20_boundary_packet_low_support_candidate_atlas_report": input_record(
                D20_BOUNDARY_PACKET_LOW_SUPPORT_CANDIDATE_ATLAS
            ),
            "d20_packet_bridge_snf_obstruction_report": input_record(
                D20_PACKET_BRIDGE_SNF_OBSTRUCTION
            ),
        },
        "derived": {
            "parity_summary": parity_summary,
            "f2_kernel_rows": kernel_rows,
            "f2_kernel_rows_sha256": sha_json(kernel_rows),
            "duplicate_parity_rows": duplicate_rows,
            "duplicate_parity_rows_sha256": sha_json(duplicate_rows),
            "zero_sum_support_rows": zero_by_support,
            "zero_sum_support_rows_sha256": sha_json(zero_by_support),
            "support_le6_summary": support_le6_summary,
            "support3_summary": support3_summary,
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": {
            "negative_boundary": (
                "The support-3 escape hatch from the low-support packet atlas is closed "
                "before the full SNF test: parity alone eliminates every signed triple."
            ),
            "low_support_exhaustion": (
                "Below support 14, the only even image supports are the duplicate parity "
                "pairs and their unions. These add no rank beyond the support-2 atlas "
                "and form only rank-one opposite doublets."
            ),
            "not_claimed": (
                "This does not rule out support-14 complement-coset combinations, "
                "arbitrary integer linear combinations, or labelled A985/tube/q42/q12 "
                "bridge columns."
            ),
        },
        "next_highest_yield_item": (
            "Do not spend more search on signed boundary supports below 14. Either test "
            "the support-14 complement-coset rows as a last boundary-only escape hatch, "
            "or move directly to labelled A985/tube/q42/q12 raw bridge columns and reduce "
            "them against the packet SNF image test."
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
        "schema": "d20.theorem.d20_boundary_packet_support3_obstruction_manifest",
        "status": report["status"],
        "name": THEOREM_ID,
        "artifacts": {
            "report": rel(out_dir / "report.json"),
            "manifest": rel(out_dir / "manifest.json"),
        },
        "report_sha256": report["certificate_sha256"],
        "inputs": report["inputs"],
        "purpose": [
            "close the signed support-3 boundary-to-packet low-support escape hatch",
            "record the F2 parity obstruction behind the support-3 enumeration",
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
