from __future__ import annotations

import csv
import hashlib
import itertools
import json
from collections import deque
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_k23stab"
STATUS = "SECTOR33_K23_PUNCTURED_SELECTOR_M23_STABILIZER_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23stab.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23stab.py"
LONG_K23SEL_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23sel" / "report.json"
LONG_K23SEL_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23sel" / "k23sel_matrices.npz"

BLOCK_TEXT_HASH = "35b9ed11f016a25ebd0fa2fd1dd56493533a6ad1f4d4cc4417be9a9033188084"
GENERATOR_TEXT_HASH = "589b323888b173bc7e4abe0b10423d988a1fa445d2fb784269c4c35ed26fb88c"
SCHREIER_TEXT_HASH = "b6e89c4cafa7c189f8707a0f3f1cdeb1e7530524acf5a5db9381843e6bebca44"
BASE_STABILIZER_TEXT_HASH = "0fb4f23711bd31db4331b1e395ff3c6881f5ecd6da3a7c4d0ee029eb74ab207e"
OBS_TEXT_HASH = "ff8ee7b9bf4b162d0e0ec41b798eb71223e8d866c3f1635a5f94f0ffb9579252"
MATRIX_SHA256 = "b7ca55d387299518bc4ce5e923ca0ff7191d7e5013e7ad424c312a2d905e0261"

M23_ORDER = 10_200_960
BASE_ORDERED_4_TUPLE_COUNT = 23 * 22 * 21 * 20
EXPECTED_BASE4_STABILIZER_COUNT = 48
POINT_COUNT = 23
BLOCK_SIZE = 7
BASE_TUPLE = [0, 1, 2, 3]
GENERATOR_PERMS = [
    [1, 0, 2, 3, 4, 17, 13, 12, 20, 9, 10, 11, 7, 6, 14, 21, 22, 5, 19, 18, 8, 15, 16],
    [1, 2, 3, 4, 0, 11, 19, 20, 15, 10, 6, 17, 7, 8, 21, 16, 12, 5, 13, 14, 9, 22, 18],
    [0, 2, 4, 6, 1, 14, 18, 5, 17, 21, 8, 13, 12, 22, 7, 9, 16, 10, 3, 19, 20, 15, 11],
]

IMAGE_COLUMNS = [f"image_{index:02d}" for index in range(POINT_COUNT)]
BLOCK_COLUMNS = [
    "block_id",
    "mask",
    "weight",
    "base_tuple_intersection_count",
    "contains_base_tuple_flag",
]
GENERATOR_COLUMNS = [
    "generator_id",
    "order",
    "fixed_point_count",
    "moved_point_count",
    "block_image_count",
    "preserves_all_blocks_flag",
] + IMAGE_COLUMNS
SCHREIER_COLUMNS = [
    "level",
    "base_point",
    "orbit_size",
    "input_generator_count",
    "schreier_generator_count",
    "cumulative_order_prefix",
]
BASE_STABILIZER_COLUMNS = ["stabilizer_id", "order", "fixed_point_count", "moved_point_count"] + IMAGE_COLUMNS
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_k23sel_certified_flag",
    "point_count",
    "block_count",
    "block_size",
    "weight7_block_count",
    "four_subset_count",
    "four_subset_expected_count",
    "unique_block_per_4_subset_flag",
    "generator_count",
    "generator_preserve_count",
    "generated_group_order",
    "expected_m23_order",
    "group_order_matches_m23_flag",
    "schreier_level_count",
    "schreier_terminal_stabilizer_generator_count",
    "base_ordered_4_tuple_count",
    "base4_pointwise_stabilizer_count",
    "base4_pointwise_stabilizer_expected_count",
    "automorphism_upper_bound",
    "upper_bound_matches_generated_order_flag",
    "full_design_automorphism_group_certified_flag",
    "m23_type_action_certified_flag",
    "support_action_on_k23_proven_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def bits(mask: int) -> list[int]:
    return [index for index in range(POINT_COUNT) if (int(mask) >> index) & 1]


def mask_from_points(points: list[int] | tuple[int, ...]) -> int:
    mask = 0
    for point in points:
        mask |= 1 << int(point)
    return mask


def apply_perm_to_mask(perm: tuple[int, ...], mask: int) -> int:
    out = 0
    for point in bits(mask):
        out |= 1 << perm[point]
    return out


def compose(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(left[right[index]] for index in range(len(left)))


def inverse(perm: tuple[int, ...]) -> tuple[int, ...]:
    out = [0] * len(perm)
    for index, image in enumerate(perm):
        out[image] = index
    return tuple(out)


def is_identity(perm: tuple[int, ...]) -> bool:
    return all(index == image for index, image in enumerate(perm))


def perm_order(perm: tuple[int, ...]) -> int:
    seen = [False] * len(perm)
    order = 1
    for start in range(len(perm)):
        if seen[start]:
            continue
        length = 0
        point = start
        while not seen[point]:
            seen[point] = True
            point = perm[point]
            length += 1
        if length:
            order = int(np.lcm(order, length))
    return order


def design_tables(blocks: list[int]) -> tuple[set[int], dict[int, int], set[int]]:
    block_set = set(blocks)
    four_subset_to_block: dict[int, int] = {}
    allowed_large_subsets: set[int] = set()
    for block in blocks:
        block_points = bits(block)
        for size in (5, 6, 7):
            for combo in itertools.combinations(block_points, size):
                allowed_large_subsets.add(mask_from_points(combo))
        for combo in itertools.combinations(block_points, 4):
            key = mask_from_points(combo)
            if key in four_subset_to_block:
                raise AssertionError("duplicate 4-subset block witness")
            four_subset_to_block[key] = block
    return block_set, four_subset_to_block, allowed_large_subsets


def enumerate_base4_stabilizer(
    blocks: list[int],
    block_set: set[int],
    four_subset_to_block: dict[int, int],
    allowed_large_subsets: set[int],
) -> tuple[list[tuple[int, ...]], int]:
    blocks_by_point = [[] for _ in range(POINT_COUNT)]
    for block in blocks:
        for point in bits(block):
            blocks_by_point[point].append(block)
    mapping = [-1] * POINT_COUNT
    inverse_mapping = [-1] * POINT_COUNT
    for point in BASE_TUPLE:
        mapping[point] = point
        inverse_mapping[point] = point
    full_mask = (1 << POINT_COUNT) - 1
    solutions: list[tuple[int, ...]] = []
    node_count = 0

    def candidate_set(source_point: int) -> int:
        candidates = full_mask
        for block in blocks_by_point[source_point]:
            image_mask = 0
            mapped_count = 0
            for point in bits(block):
                if mapping[point] >= 0:
                    image_mask |= 1 << mapping[point]
                    mapped_count += 1
            if mapped_count >= 4:
                if mapped_count >= 5 and image_mask not in allowed_large_subsets:
                    return 0
                key = mask_from_points(bits(image_mask)[:4])
                target_block = four_subset_to_block.get(key)
                if target_block is None:
                    return 0
                candidates &= target_block
        for image in range(POINT_COUNT):
            if inverse_mapping[image] >= 0:
                candidates &= ~(1 << image)
        return candidates

    def valid_assign(source_point: int, image_point: int) -> bool:
        for block in blocks_by_point[source_point]:
            image_mask = 1 << image_point
            mapped_count = 1
            for point in bits(block):
                if point != source_point and mapping[point] >= 0:
                    image_mask |= 1 << mapping[point]
                    mapped_count += 1
            if mapped_count >= 5 and image_mask not in allowed_large_subsets:
                return False
        return True

    def recurse() -> None:
        nonlocal node_count
        node_count += 1
        if all(image >= 0 for image in mapping):
            perm = tuple(mapping)
            for block in blocks:
                if apply_perm_to_mask(perm, block) not in block_set:
                    return
            solutions.append(perm)
            return
        best_source = -1
        best_candidates = 0
        best_count = POINT_COUNT + 1
        for source_point in range(POINT_COUNT):
            if mapping[source_point] >= 0:
                continue
            candidates = candidate_set(source_point)
            count = int(candidates.bit_count())
            if count == 0:
                return
            if count < best_count:
                best_source = source_point
                best_candidates = candidates
                best_count = count
        for image_point in bits(best_candidates):
            if not valid_assign(best_source, image_point):
                continue
            mapping[best_source] = image_point
            inverse_mapping[image_point] = best_source
            recurse()
            inverse_mapping[image_point] = -1
            mapping[best_source] = -1

    recurse()
    return sorted(set(solutions)), node_count


def schreier_order(generators: list[tuple[int, ...]]) -> tuple[int, list[dict[str, int]]]:
    identity = tuple(range(POINT_COUNT))
    levels: list[dict[str, int]] = []

    def recurse(current_generators: list[tuple[int, ...]], base_points: list[int], depth: int) -> int:
        unique_generators = list(dict.fromkeys(perm for perm in current_generators if not is_identity(perm)))
        if not unique_generators or not base_points:
            return 1
        base_point = base_points[0]
        symmetric_generators = list(dict.fromkeys(unique_generators + [inverse(perm) for perm in unique_generators]))
        orbit_transversal: dict[int, tuple[int, ...]] = {base_point: identity}
        queue: deque[int] = deque([base_point])
        while queue:
            orbit_point = queue.popleft()
            transporter = orbit_transversal[orbit_point]
            for generator in symmetric_generators:
                image = generator[orbit_point]
                if image not in orbit_transversal:
                    orbit_transversal[image] = compose(generator, transporter)
                    queue.append(image)
        stabilizer_generators: list[tuple[int, ...]] = []
        seen: set[tuple[int, ...]] = set()
        for orbit_point, transporter in list(orbit_transversal.items()):
            for generator in symmetric_generators:
                image = generator[orbit_point]
                schreier_generator = compose(
                    inverse(orbit_transversal[image]),
                    compose(generator, transporter),
                )
                if not is_identity(schreier_generator) and schreier_generator not in seen:
                    seen.add(schreier_generator)
                    stabilizer_generators.append(schreier_generator)
        level = {
            "level": depth,
            "base_point": base_point,
            "orbit_size": len(orbit_transversal),
            "input_generator_count": len(unique_generators),
            "schreier_generator_count": len(stabilizer_generators),
            "cumulative_order_prefix": 0,
        }
        levels.append(level)
        sub_order = recurse(stabilizer_generators, base_points[1:], depth + 1)
        return len(orbit_transversal) * sub_order

    order = recurse(generators, list(range(POINT_COUNT)), 0)
    running = 1
    for level in levels:
        running *= int(level["orbit_size"])
        level["cumulative_order_prefix"] = running
    return order, levels


def build_rows() -> dict[str, Any]:
    long_k23sel = load_json(LONG_K23SEL_REPORT)
    with np.load(LONG_K23SEL_MATRICES, allow_pickle=False) as matrices:
        punctured_words = [int(value) for value in np.asarray(matrices["punctured_codeword_masks"]).tolist()]
    blocks = sorted(mask for mask in punctured_words if int(mask).bit_count() == BLOCK_SIZE)
    block_set, four_subset_to_block, allowed_large_subsets = design_tables(blocks)
    generators = [tuple(perm) for perm in GENERATOR_PERMS]
    group_order, schreier_rows = schreier_order(generators)
    base_stabilizer, base4_search_node_count = enumerate_base4_stabilizer(
        blocks,
        block_set,
        four_subset_to_block,
        allowed_large_subsets,
    )
    block_rows = [
        {
            "block_id": block_id,
            "mask": block,
            "weight": int(block).bit_count(),
            "base_tuple_intersection_count": sum(int((block >> point) & 1) for point in BASE_TUPLE),
            "contains_base_tuple_flag": int((block & mask_from_points(BASE_TUPLE)) == mask_from_points(BASE_TUPLE)),
        }
        for block_id, block in enumerate(blocks)
    ]
    generator_rows = []
    generator_preserve_count = 0
    for generator_id, perm in enumerate(generators):
        image_blocks = {apply_perm_to_mask(perm, block) for block in blocks}
        preserves = image_blocks == block_set
        generator_preserve_count += int(preserves)
        row = {
            "generator_id": generator_id,
            "order": perm_order(perm),
            "fixed_point_count": sum(int(index == image) for index, image in enumerate(perm)),
            "moved_point_count": sum(int(index != image) for index, image in enumerate(perm)),
            "block_image_count": len(image_blocks),
            "preserves_all_blocks_flag": int(preserves),
        }
        row.update({f"image_{index:02d}": image for index, image in enumerate(perm)})
        generator_rows.append(row)
    base_stabilizer_rows = []
    for stabilizer_id, perm in enumerate(base_stabilizer):
        row = {
            "stabilizer_id": stabilizer_id,
            "order": perm_order(perm),
            "fixed_point_count": sum(int(index == image) for index, image in enumerate(perm)),
            "moved_point_count": sum(int(index != image) for index, image in enumerate(perm)),
        }
        row.update({f"image_{index:02d}": image for index, image in enumerate(perm)})
        base_stabilizer_rows.append(row)
    upper_bound = BASE_ORDERED_4_TUPLE_COUNT * len(base_stabilizer)
    obs = {
        "long_k23sel_certified_flag": int(
            long_k23sel.get("status") == "SECTOR33_K23_CANONICAL_FRAME_GOLAY_SELECTOR_CERTIFIED"
            and long_k23sel.get("all_checks_pass") is True
        ),
        "point_count": POINT_COUNT,
        "block_count": len(blocks),
        "block_size": BLOCK_SIZE,
        "weight7_block_count": len(blocks),
        "four_subset_count": len(four_subset_to_block),
        "four_subset_expected_count": int(np.math.comb(POINT_COUNT, 4)) if hasattr(np, "math") else 8855,
        "unique_block_per_4_subset_flag": int(len(four_subset_to_block) == 8855),
        "generator_count": len(generators),
        "generator_preserve_count": generator_preserve_count,
        "generated_group_order": group_order,
        "expected_m23_order": M23_ORDER,
        "group_order_matches_m23_flag": int(group_order == M23_ORDER),
        "schreier_level_count": len(schreier_rows),
        "schreier_terminal_stabilizer_generator_count": int(schreier_rows[-1]["schreier_generator_count"]) if schreier_rows else 0,
        "base_ordered_4_tuple_count": BASE_ORDERED_4_TUPLE_COUNT,
        "base4_pointwise_stabilizer_count": len(base_stabilizer),
        "base4_pointwise_stabilizer_expected_count": EXPECTED_BASE4_STABILIZER_COUNT,
        "automorphism_upper_bound": upper_bound,
        "upper_bound_matches_generated_order_flag": int(upper_bound == group_order == M23_ORDER),
        "full_design_automorphism_group_certified_flag": int(upper_bound == group_order == M23_ORDER),
        "m23_type_action_certified_flag": int(
            generator_preserve_count == len(generators)
            and len(blocks) == 253
            and len(four_subset_to_block) == 8855
            and upper_bound == group_order == M23_ORDER
        ),
        "support_action_on_k23_proven_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    matrix_payload = {
        "block_masks": np.asarray(blocks, dtype=np.int64),
        "generator_permutations": np.asarray(GENERATOR_PERMS, dtype=np.int64),
        "base4_stabilizer_permutations": np.asarray(base_stabilizer, dtype=np.int64),
        "schreier_level_table": table_from_rows(SCHREIER_COLUMNS, schreier_rows),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "long_k23sel": long_k23sel,
        "block_rows": block_rows,
        "generator_rows": generator_rows,
        "schreier_rows": schreier_rows,
        "base_stabilizer_rows": base_stabilizer_rows,
        "obs_rows": obs_rows,
        "block_table": table_from_rows(BLOCK_COLUMNS, block_rows),
        "generator_table": table_from_rows(GENERATOR_COLUMNS, generator_rows),
        "schreier_table": table_from_rows(SCHREIER_COLUMNS, schreier_rows),
        "base_stabilizer_table": table_from_rows(BASE_STABILIZER_COLUMNS, base_stabilizer_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "base4_search_node_count": base4_search_node_count,
        "block_text_hash": hashlib.sha256(digest_text(BLOCK_COLUMNS, block_rows).encode("ascii")).hexdigest(),
        "generator_text_hash": hashlib.sha256(digest_text(GENERATOR_COLUMNS, generator_rows).encode("ascii")).hexdigest(),
        "schreier_text_hash": hashlib.sha256(digest_text(SCHREIER_COLUMNS, schreier_rows).encode("ascii")).hexdigest(),
        "base_stabilizer_text_hash": hashlib.sha256(
            digest_text(BASE_STABILIZER_COLUMNS, base_stabilizer_rows).encode("ascii")
        ).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = [
        "block_masks",
        "generator_permutations",
        "base4_stabilizer_permutations",
        "schreier_level_table",
        "observable_vector",
    ]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": obs["long_k23sel_certified_flag"] == 1,
        "punctured_design_profile_matches": (
            obs["point_count"],
            obs["block_count"],
            obs["block_size"],
            obs["weight7_block_count"],
            obs["four_subset_count"],
            obs["four_subset_expected_count"],
            obs["unique_block_per_4_subset_flag"],
        )
        == (23, 253, 7, 253, 8855, 8855, 1),
        "generators_preserve_design": (
            obs["generator_count"],
            obs["generator_preserve_count"],
        )
        == (3, 3),
        "schreier_order_matches_m23": (
            obs["generated_group_order"],
            obs["expected_m23_order"],
            obs["group_order_matches_m23_flag"],
            obs["schreier_level_count"],
            obs["schreier_terminal_stabilizer_generator_count"],
        )
        == (M23_ORDER, M23_ORDER, 1, 6, 0),
        "automorphism_upper_bound_is_sharp": (
            obs["base_ordered_4_tuple_count"],
            obs["base4_pointwise_stabilizer_count"],
            obs["base4_pointwise_stabilizer_expected_count"],
            obs["automorphism_upper_bound"],
            obs["upper_bound_matches_generated_order_flag"],
        )
        == (BASE_ORDERED_4_TUPLE_COUNT, 48, 48, M23_ORDER, 1),
        "m23_type_action_boundary": (
            obs["full_design_automorphism_group_certified_flag"],
            obs["m23_type_action_certified_flag"],
            obs["support_action_on_k23_proven_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (1, 1, 0, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_punctured_selector_m23_stabilizer",
        "summary": obs,
        "generator_permutations": GENERATOR_PERMS,
        "schreier_orbit_sizes": [int(row["orbit_size"]) for row in rows["schreier_rows"]],
        "base4_search_node_count": rows["base4_search_node_count"],
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies the full automorphism group of the Euler-deleted weight-7 selector design as the generated M23-order action; the lifted action on the signed K23 support map remains open.",
    }
    seam_payload = {
        "schema": "long.k23stab.seam@1",
        "status": STATUS,
        "claim": "The Euler-deleted selector has a 253-block S(4,7,23) design whose full automorphism group is generated by three certified block-preserving permutations of order 10200960.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23sel": input_entry(
            LONG_K23SEL_REPORT,
            {
                "status": rows["long_k23sel"].get("status"),
                "certificate_sha256": rows["long_k23sel"].get("certificate_sha256"),
            },
        ),
        "long_k23sel_matrices": input_entry(LONG_K23SEL_MATRICES),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23stab.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23stab certifies the M23-type stabilizer action of the punctured K23 selector design.",
        "stage_protocol": {
            "draft": "read long_k23sel and its punctured selector word masks",
            "witness": "emit weight-7 design blocks, generator permutations, Schreier orbit levels, base-4 pointwise stabilizer rows, observables, and matrices",
            "coherence": "check S(4,7,23) block counts, generator block preservation, generated group order, and sharp automorphism upper bound",
            "closure": "certify the full Euler-deleted selector design automorphism group while keeping the lifted K23 support action open",
            "emit": "write long_k23stab artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "block_rows_csv": relpath(OUT_DIR / "block_rows.csv"),
            "generator_rows_csv": relpath(OUT_DIR / "generator_rows.csv"),
            "schreier_rows_csv": relpath(OUT_DIR / "schreier_rows.csv"),
            "base_stabilizer_rows_csv": relpath(OUT_DIR / "base_stabilizer_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23stab_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the Euler-deleted selector weight-7 words form a 253-block S(4,7,23) design",
                "three explicit coordinate permutations preserve all 253 design blocks",
                "the generated permutation group has Schreier orbit product 10200960",
                "the pointwise stabilizer of the ordered base 4-tuple has exactly 48 automorphisms by finite search",
                "the resulting automorphism upper bound equals the generated group order, so the full design automorphism group is certified at M23 order",
            ],
            "does_not_certify": [
                "that the M23 action lifts to the signed 56-by-24 K23 support map",
                "a linear representation of M23 on the prime-field K23 lift",
                "intrinsic recovery of the selector from the naive binary shadow",
                "a rebuild of d20.json or broad bundle closure",
            ],
        },
        "next_highest_yield_item": "Lift the certified M23-order punctured selector action through the signed K23 support map and test which generators preserve the 56-support binding.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23stab.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23stab.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "block_csv": csv_text(BLOCK_COLUMNS, rows["block_rows"]),
        "generator_csv": csv_text(GENERATOR_COLUMNS, rows["generator_rows"]),
        "schreier_csv": csv_text(SCHREIER_COLUMNS, rows["schreier_rows"]),
        "base_stabilizer_csv": csv_text(BASE_STABILIZER_COLUMNS, rows["base_stabilizer_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "block_table": rows["block_table"],
        "generator_table": rows["generator_table"],
        "schreier_table": rows["schreier_table"],
        "base_stabilizer_table": rows["base_stabilizer_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "block_text_sha256": rows["block_text_hash"],
            "generator_text_sha256": rows["generator_text_hash"],
            "schreier_text_sha256": rows["schreier_text_hash"],
            "base_stabilizer_text_sha256": rows["base_stabilizer_text_hash"],
            "obs_text_sha256": rows["obs_text_hash"],
            "matrix_sha256": rows["matrix_sha256"],
        },
    }


def update_index(report: dict[str, Any]) -> None:
    if INDEX_PATH.exists():
        index_payload = load_json(INDEX_PATH)
        obligations = [
            row
            for row in index_payload.get("obligations", [])
            if isinstance(row, dict) and row.get("id") != THEOREM_ID
        ]
        schema = index_payload.get("schema", "d20.proof_obligation_registry.source_drop")
    else:
        obligations = []
        schema = "d20.proof_obligation_registry.source_drop"
    obligations.append(
        {
            "id": THEOREM_ID,
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
            "report_sha256": report["certificate_sha256"],
            "status": report["status"],
        }
    )
    obligations.sort(key=lambda row: str(row["id"]))
    index = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": obligations,
    }
    index["registry_sha256"] = self_hash(index, "registry_sha256")
    write_json(INDEX_PATH, index)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "block_rows.csv").write_text(payloads["block_csv"], encoding="utf-8")
    (OUT_DIR / "generator_rows.csv").write_text(payloads["generator_csv"], encoding="utf-8")
    (OUT_DIR / "schreier_rows.csv").write_text(payloads["schreier_csv"], encoding="utf-8")
    (OUT_DIR / "base_stabilizer_rows.csv").write_text(payloads["base_stabilizer_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        block_table=payloads["block_table"],
        generator_table=payloads["generator_table"],
        schreier_table=payloads["schreier_table"],
        base_stabilizer_table=payloads["base_stabilizer_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23stab_matrices.npz", **payloads["matrix_payload"])
    write_json(OUT_DIR / "cert.json", payloads["cert"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    write_json(OUT_DIR / "report.json", payloads["report"])
    update_index(payloads["report"])


def main() -> None:
    payloads = build_payloads()
    write_payloads(payloads)
    report = payloads["report"]
    print(
        json.dumps(
            {
                "status": report["status"],
                "all_checks_pass": report["all_checks_pass"],
                "certificate_sha256": report["certificate_sha256"],
                "computed_hashes": payloads["computed_hashes"],
                "summary": report["witness"]["summary"],
                "report": relpath(OUT_DIR / "report.json"),
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
