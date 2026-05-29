from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
import math
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, product
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = (
    "data/invariants/d20/theorems/d20_boundary_packet_support3_obstruction/report.json"
)
INPUT_RELS = {
    "d20_boundary_loop_step_atom_incidence_report": (
        "data/invariants/d20/theorems/d20_boundary_loop_step_atom_incidence/report.json"
    ),
    "d20_boundary_packet_low_support_candidate_atlas_report": (
        "data/invariants/d20/theorems/d20_boundary_packet_low_support_candidate_atlas/report.json"
    ),
    "d20_packet_bridge_snf_obstruction_report": (
        "data/invariants/d20/theorems/d20_packet_bridge_snf_obstruction/report.json"
    ),
}
COEFFICIENT_SET = [-1, 1]
SUPPORT = 3
PUBLIC_ATOM_COUNT = 20
STEP_ATOM_COUNT = 25


def _check_input_hash(inputs: dict[str, Any], key: str, rel_path: str) -> None:
    if inputs.get(key, {}).get("path") != rel_path:
        raise AssertionError(f"D20 boundary support-3 obstruction {key} path mismatch")
    path = ROOT / rel_path
    if path.exists() and h_file(path) != inputs[key].get("sha256"):
        raise AssertionError(f"D20 boundary support-3 obstruction {key} hash mismatch")


def _load_json(rel_path: str) -> dict[str, Any]:
    with (ROOT / rel_path).open("r", encoding="utf-8") as f:
        return json.load(f)


def _row_parity(matrix: list[list[int]]) -> list[tuple[int, ...]]:
    return [tuple(value & 1 for value in row) for row in matrix]


def _xor_patterns(patterns: list[tuple[int, ...]], atoms: tuple[int, ...]) -> tuple[int, ...]:
    out = [0] * len(patterns[0])
    for atom in atoms:
        out = [left ^ right for left, right in zip(out, patterns[atom])]
    return tuple(out)


def _gf2_rank(patterns: list[tuple[int, ...]]) -> int:
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


def _matrix_rank_rational(matrix: list[list[int]]) -> int:
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


def _local_ok(u: int, v: int) -> bool:
    return u % 2 == 0 and v % 2 == 0 and (u + v) % 6 == 0


def _image_for_support(support: list[tuple[int, int]], matrix: list[list[int]]) -> list[int]:
    return [
        sum(coefficient * matrix[atom_id][col] for atom_id, coefficient in support)
        for col in range(len(matrix[0]))
    ]


def _enumerate_kernel_masks(patterns: list[tuple[int, ...]]) -> list[int]:
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


def _mask_atoms(mask: int, atom_count: int = PUBLIC_ATOM_COUNT) -> list[int]:
    return [atom_id for atom_id in range(atom_count) if (mask >> atom_id) & 1]


def _zero_sum_rows(
    patterns: list[tuple[int, ...]], public_atom_rows: list[dict[str, Any]], support: int
) -> list[dict[str, Any]]:
    rows = []
    for atoms in combinations(range(len(patterns)), support):
        if any(_xor_patterns(patterns, atoms)):
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


def _kernel_mask_rows(
    zero_masks: list[int], public_atom_rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    rows = []
    for mask in sorted(zero_masks, key=lambda item: (item.bit_count(), _mask_atoms(item))):
        atoms = _mask_atoms(mask)
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


def _duplicate_parity_rows(
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


def _class_histogram(patterns: list[tuple[int, ...]]) -> dict[str, int]:
    classes: dict[tuple[int, ...], int] = Counter(patterns)
    sizes = Counter(classes.values())
    return {str(key): int(sizes[key]) for key in sorted(sizes)}


def _histogram(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _signed_even_rows_for_supports(
    zero_masks: list[int], matrix: list[list[int]], max_support: int
) -> list[dict[str, Any]]:
    rows = []
    for mask in zero_masks:
        atoms = _mask_atoms(mask)
        if not atoms or len(atoms) > max_support:
            continue
        for signs in product(COEFFICIENT_SET, repeat=len(atoms)):
            support = list(zip(atoms, signs))
            image = _image_for_support(support, matrix)
            if any(value % 2 for value in image):
                raise AssertionError("D20 boundary support-3 obstruction odd signed row")
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


def _compatible_doublet_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    doublet_rank_hist: Counter[int] = Counter()
    doublet_size_hist: Counter[str] = Counter()
    negative_count = 0
    doublet_count = 0
    rank_two_count = 0
    for left, right in combinations(rows, 2):
        left_image = left["image_vector"]
        right_image = right["image_vector"]
        if not all(_local_ok(left_image[col], right_image[col]) for col in range(len(left_image))):
            continue
        doublet_count += 1
        rank = _matrix_rank_rational([left_image, right_image])
        doublet_rank_hist[rank] += 1
        doublet_size_hist[f"{left['support_size']}|{right['support_size']}"] += 1
        if right_image == [-value for value in left_image]:
            negative_count += 1
        if rank == 2:
            rank_two_count += 1
    return {
        "compatible_doublet_count": doublet_count,
        "compatible_doublet_rank_histogram": _histogram(doublet_rank_hist),
        "compatible_doublet_support_size_histogram": _histogram(doublet_size_hist),
        "compatible_doublet_negative_pair_count": negative_count,
        "rank_two_doublet_count": rank_two_count,
        "all_compatible_doublets_are_opposite_rows": negative_count == doublet_count,
    }


def validate_d20_boundary_packet_support3_obstruction() -> Dict[str, Any]:
    rec: dict[str, Any] | None = None
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            rec = json.load(f)
    else:
        cached = cached_core_block("d20_boundary_packet_support3_obstruction")
        if cached is not None:
            rec = cached
    if rec is None:
        raise FileNotFoundError("missing D20 boundary packet support-3 obstruction")

    if rec.get("schema") != "d20.theorem.d20_boundary_packet_support3_obstruction":
        raise AssertionError("D20 boundary support-3 obstruction schema mismatch")
    if rec.get("status") != "D20_BOUNDARY_PACKET_SUPPORT3_OBSTRUCTION_CERTIFIED":
        raise AssertionError("D20 boundary support-3 obstruction status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("D20 boundary support-3 obstruction checks did not pass")

    for key, rel_path in INPUT_RELS.items():
        _check_input_hash(rec.get("inputs", {}), key, rel_path)

    definition = rec.get("definition", {})
    if definition.get("coefficient_set") != COEFFICIENT_SET:
        raise AssertionError("D20 boundary support-3 obstruction coefficient set mismatch")
    if definition.get("support") != SUPPORT:
        raise AssertionError("D20 boundary support-3 obstruction support mismatch")
    if definition.get("packet_snf_image_test") != (
        "u = 0 mod 2, v = 0 mod 2, and u+v = 0 mod 6 on each packet doublet"
    ):
        raise AssertionError("D20 boundary support-3 obstruction image test mismatch")

    incidence = _load_json(INPUT_RELS["d20_boundary_loop_step_atom_incidence_report"])
    low_support = _load_json(
        INPUT_RELS["d20_boundary_packet_low_support_candidate_atlas_report"]
    )
    packet_snf = _load_json(INPUT_RELS["d20_packet_bridge_snf_obstruction_report"])
    if incidence.get("status") != "D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE_CERTIFIED":
        raise AssertionError("D20 boundary support-3 obstruction incidence input status mismatch")
    if low_support.get("status") != "D20_BOUNDARY_PACKET_LOW_SUPPORT_CANDIDATE_ATLAS_CERTIFIED":
        raise AssertionError("D20 boundary support-3 obstruction low-support input status mismatch")
    if packet_snf.get("status") != "D20_PACKET_BRIDGE_SNF_OBSTRUCTION_CERTIFIED":
        raise AssertionError("D20 boundary support-3 obstruction SNF input status mismatch")

    matrix = incidence["derived"]["boundary_atom_step_incidence_matrix"]
    public_atom_rows = incidence["derived"]["public_atom_rows"]
    if len(matrix) != PUBLIC_ATOM_COUNT or any(len(row) != STEP_ATOM_COUNT for row in matrix):
        raise AssertionError("D20 boundary support-3 obstruction incidence shape mismatch")
    patterns = _row_parity(matrix)
    zero_masks = _enumerate_kernel_masks(patterns)
    kernel_rows = _kernel_mask_rows(zero_masks, public_atom_rows)
    duplicate_rows = _duplicate_parity_rows(patterns, public_atom_rows)
    duplicate_generators = [
        sum(1 << atom for atom in row["public_atom_support"])
        for row in duplicate_rows
    ]
    duplicate_span = {0}
    for generator in duplicate_generators:
        duplicate_span |= {mask ^ generator for mask in list(duplicate_span)}
    outside_duplicate_span = [mask for mask in zero_masks if mask not in duplicate_span]
    zero_rows = {
        str(support): _zero_sum_rows(patterns, public_atom_rows, support)
        for support in range(1, 7)
    }
    signed_rows_le6 = _signed_even_rows_for_supports(zero_masks, matrix, max_support=6)

    derived = rec.get("derived", {})
    parity = derived.get("parity_summary", {})
    if parity.get("row_parity_rank_over_F2") != _gf2_rank(patterns):
        raise AssertionError("D20 boundary support-3 obstruction parity rank mismatch")
    if parity.get("row_parity_rank_over_F2") != 16:
        raise AssertionError("D20 boundary support-3 obstruction expected parity rank mismatch")
    if parity.get("f2_kernel_size") != len(zero_masks):
        raise AssertionError("D20 boundary support-3 obstruction kernel size mismatch")
    if parity.get("f2_kernel_size") != 16:
        raise AssertionError("D20 boundary support-3 obstruction expected kernel size mismatch")
    if parity.get("f2_kernel_dimension") != 4:
        raise AssertionError("D20 boundary support-3 obstruction kernel dimension mismatch")
    kernel_hist = _histogram(Counter(mask.bit_count() for mask in zero_masks))
    if parity.get("f2_kernel_support_size_histogram") != kernel_hist:
        raise AssertionError("D20 boundary support-3 obstruction kernel weight histogram mismatch")
    if kernel_hist != {"0": 1, "2": 3, "4": 3, "6": 1, "14": 1, "16": 3, "18": 3, "20": 1}:
        raise AssertionError("D20 boundary support-3 obstruction expected kernel weights mismatch")
    if parity.get("parity_class_size_histogram") != _class_histogram(patterns):
        raise AssertionError("D20 boundary support-3 obstruction parity class histogram mismatch")
    if parity.get("duplicate_parity_pair_count") != 3:
        raise AssertionError("D20 boundary support-3 obstruction duplicate pair count mismatch")
    expected_pairs = [[0, 11], [6, 17], [14, 15]]
    if parity.get("duplicate_parity_pairs") != expected_pairs:
        raise AssertionError("D20 boundary support-3 obstruction duplicate pair mismatch")
    expected_zero_counts = {support: len(rows) for support, rows in zero_rows.items()}
    if parity.get("zero_sum_support_counts") != expected_zero_counts:
        raise AssertionError("D20 boundary support-3 obstruction zero-sum counts mismatch")
    if expected_zero_counts != {"1": 0, "2": 3, "3": 0, "4": 3, "5": 0, "6": 1}:
        raise AssertionError("D20 boundary support-3 obstruction expected zero-sum profile mismatch")
    if parity.get("duplicate_pair_span_size") != len(duplicate_span):
        raise AssertionError("D20 boundary support-3 obstruction duplicate span size mismatch")
    if parity.get("kernel_equals_duplicate_pair_span") is not False:
        raise AssertionError("D20 boundary support-3 obstruction duplicate span overclaim")
    if parity.get("outside_duplicate_pair_span_count") != len(outside_duplicate_span):
        raise AssertionError("D20 boundary support-3 obstruction outside span count mismatch")
    outside_hist = _histogram(Counter(mask.bit_count() for mask in outside_duplicate_span))
    if parity.get("outside_duplicate_pair_span_support_size_histogram") != outside_hist:
        raise AssertionError("D20 boundary support-3 obstruction outside span histogram mismatch")
    if outside_hist != {"14": 1, "16": 3, "18": 3, "20": 1}:
        raise AssertionError("D20 boundary support-3 obstruction outside span expected mismatch")
    if parity.get("minimal_new_parity_dependency_support_size") != 14:
        raise AssertionError("D20 boundary support-3 obstruction minimal new support mismatch")

    if derived.get("f2_kernel_rows") != kernel_rows:
        raise AssertionError("D20 boundary support-3 obstruction kernel rows mismatch")
    if h_json(kernel_rows) != derived.get("f2_kernel_rows_sha256"):
        raise AssertionError("D20 boundary support-3 obstruction kernel row hash mismatch")

    if derived.get("duplicate_parity_rows") != duplicate_rows:
        raise AssertionError("D20 boundary support-3 obstruction duplicate rows mismatch")
    if h_json(duplicate_rows) != derived.get("duplicate_parity_rows_sha256"):
        raise AssertionError("D20 boundary support-3 obstruction duplicate row hash mismatch")
    if derived.get("zero_sum_support_rows") != zero_rows:
        raise AssertionError("D20 boundary support-3 obstruction zero-sum rows mismatch")
    if h_json(zero_rows) != derived.get("zero_sum_support_rows_sha256"):
        raise AssertionError("D20 boundary support-3 obstruction zero-sum row hash mismatch")

    support_le6 = derived.get("support_le6_summary", {})
    expected_le6_count = len(signed_rows_le6)
    if support_le6.get("signed_even_candidate_count") != expected_le6_count:
        raise AssertionError("D20 boundary support-3 obstruction support<=6 count mismatch")
    if expected_le6_count != 124:
        raise AssertionError("D20 boundary support-3 obstruction expected support<=6 count mismatch")
    support_le6_hist = _histogram(Counter(row["support_size"] for row in signed_rows_le6))
    if support_le6.get("signed_even_candidate_support_size_histogram") != support_le6_hist:
        raise AssertionError("D20 boundary support-3 obstruction support<=6 histogram mismatch")
    if support_le6_hist != {"2": 12, "4": 48, "6": 64}:
        raise AssertionError("D20 boundary support-3 obstruction expected support<=6 histogram mismatch")
    expected_rank_by_size = {
        str(support): _matrix_rank_rational(
            [
                row["image_vector"]
                for row in signed_rows_le6
                if row["support_size"] == support
            ]
        )
        for support in (2, 4, 6)
    }
    if support_le6.get("rank_by_support_size_over_Q") != expected_rank_by_size:
        raise AssertionError("D20 boundary support-3 obstruction support<=6 rank-by-size mismatch")
    if expected_rank_by_size != {"2": 6, "4": 6, "6": 6}:
        raise AssertionError("D20 boundary support-3 obstruction expected rank-by-size mismatch")
    combined_rank = _matrix_rank_rational([row["image_vector"] for row in signed_rows_le6])
    support2_rank = _matrix_rank_rational(
        [
            row["image_vector"]
            for row in signed_rows_le6
            if row["support_size"] == 2
        ]
    )
    if support_le6.get("combined_rank_over_Q") != combined_rank:
        raise AssertionError("D20 boundary support-3 obstruction support<=6 combined rank mismatch")
    if support_le6.get("rank_over_support2_span") != combined_rank - support2_rank:
        raise AssertionError("D20 boundary support-3 obstruction support<=6 rank delta mismatch")
    if combined_rank != 6 or combined_rank - support2_rank != 0:
        raise AssertionError("D20 boundary support-3 obstruction expected support<=6 rank mismatch")
    expected_doublet_summary = _compatible_doublet_summary(signed_rows_le6)
    for key, value in expected_doublet_summary.items():
        if support_le6.get(key) != value:
            raise AssertionError(
                f"D20 boundary support-3 obstruction support<=6 {key} mismatch"
            )
    if support_le6.get("compatible_doublet_count") != 62:
        raise AssertionError("D20 boundary support-3 obstruction support<=6 doublet count mismatch")
    if support_le6.get("compatible_doublet_rank_histogram") != {"1": 62}:
        raise AssertionError("D20 boundary support-3 obstruction support<=6 rank histogram mismatch")
    if support_le6.get("rank_two_doublet_count") != 0:
        raise AssertionError("D20 boundary support-3 obstruction support<=6 rank-two overclaim")

    summary = derived.get("support3_summary", {})
    support3_signed_count = math.comb(PUBLIC_ATOM_COUNT, SUPPORT) * (
        len(COEFFICIENT_SET) ** SUPPORT
    )
    if summary.get("signed_candidate_count") != support3_signed_count:
        raise AssertionError("D20 boundary support-3 obstruction signed count mismatch")
    if support3_signed_count != 9120:
        raise AssertionError("D20 boundary support-3 obstruction expected signed count mismatch")
    if summary.get("even_image_candidate_count") != 0:
        raise AssertionError("D20 boundary support-3 obstruction even candidate mismatch")
    if summary.get("compatible_doublet_count") != 0:
        raise AssertionError("D20 boundary support-3 obstruction doublet count mismatch")
    if summary.get("rank_two_doublet_count") != 0:
        raise AssertionError("D20 boundary support-3 obstruction rank-two count mismatch")
    low_summary = low_support["derived"]["low_support_summary"]
    if summary.get("support_at_most_3_even_candidate_count") != low_summary.get(
        "even_image_candidate_count"
    ):
        raise AssertionError("D20 boundary support-3 obstruction support-at-most-3 count mismatch")
    if summary.get("support_at_most_3_even_candidate_count_matches_support_2") is not True:
        raise AssertionError("D20 boundary support-3 obstruction support-2 equality mismatch")
    if summary.get("full_parity_kernel_minimal_new_dependency_support_size") != 14:
        raise AssertionError("D20 boundary support-3 obstruction summary minimal support mismatch")

    checks = rec.get("checks", {})
    if not checks or any(value is not True for value in checks.values()):
        raise AssertionError("D20 boundary support-3 obstruction check table mismatch")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("D20 boundary support-3 obstruction self hash mismatch")

    return rec


if __name__ == "__main__":
    rec = validate_d20_boundary_packet_support3_obstruction()
    print(rec["status"])
    print(rec["certificate_sha256"])
