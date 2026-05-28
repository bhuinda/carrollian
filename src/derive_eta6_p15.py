from __future__ import annotations

import itertools
import json
import math
from collections import defaultdict
from typing import Any

import numpy as np

try:
    from . import derive_eta6_p5 as p5
    from . import derive_eta6_p11 as p11
    from . import derive_eta6_p14 as p14
    from .derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    import derive_eta6_p5 as p5
    import derive_eta6_p11 as p11
    import derive_eta6_p14 as p14
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "eta6_p15"
STATUS = "ETA6_P15_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

P5_REPORT = p5.OUT_DIR / "report.json"
P5_TABLES = p5.OUT_DIR / "tables.npz"
P6_REPORT = p11.P6_REPORT
P7_REPORT = p11.P7_REPORT
P8_REPORT = p11.P8_REPORT
P11_REPORT = p11.OUT_DIR / "report.json"
P14_REPORT = p14.OUT_DIR / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_p15.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_p15.py"

TOP_N = 32
CELL_WIDTHS = [1_048_576, 2_097_152, 4_194_304, 8_388_608]
OFFSETS = list(itertools.product([-1, 0, 1], repeat=4))
TOP_COLUMNS = [
    "rank",
    "p15_id",
    "p5_a",
    "p5_b",
    "p5_c",
    "p5_d",
    "p5_e",
    "p5_f",
    "face_a",
    "face_b",
    "face_c",
    "face_d",
    "face_e",
    "face_f",
    "mask_a",
    "mask_b",
    "mask_c",
    "mask_d",
    "mask_e",
    "mask_f",
    "same_face_flag",
    "same_mask_flag",
    "joint_p0_support",
    "joint_p1_support",
    "joint_p2_support",
    "joint_p3_support",
    "joint_p4_support",
    "joint_support_min",
    "joint_support_max",
    "joint_support_spread",
    "below_p14_floor_flag",
    "below_p11_floor_flag",
    "below_p8_floor_flag",
    "below_p7_floor_flag",
    "below_p6_floor_flag",
    "below_p5_floor_flag",
    "support_equal_flag",
    "joint_mult_value",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
SCALE_COLUMNS = [
    "scale_id",
    "cell_width",
    "grid_cell_count",
    "raw_pair_count",
    "raw_lookup_count",
    "new_unique_candidate_count",
]
OBS_CODES = {
    "p5_extension_count": 0,
    "triple_count": 1,
    "full_six_count": 2,
    "grid_scale_count": 3,
    "grid_neighbor_count": 4,
    "raw_pair_count": 5,
    "raw_lookup_count": 6,
    "unique_candidate_count": 7,
    "p5_single_floor": 8,
    "p6_pair_floor": 9,
    "p7_triple_floor": 10,
    "p8_quad_floor": 11,
    "p11_quint_floor": 12,
    "p14_basin_six_floor": 13,
    "grid_min_spread": 14,
    "grid_min_below_p14_flag": 15,
    "grid_min_below_p11_flag": 16,
    "grid_min_below_p8_flag": 17,
    "below_p14_candidate_count": 18,
    "below_p11_candidate_count": 19,
    "below_p8_candidate_count": 20,
    "below_p7_candidate_count": 21,
    "below_p6_candidate_count": 22,
    "below_p5_candidate_count": 23,
    "support_equal_candidate_count": 24,
    "same_face_candidate_count": 25,
    "same_mask_candidate_count": 26,
    "best_p15_id": 27,
    "best_p5_a": 28,
    "best_p5_b": 29,
    "best_p5_c": 30,
    "best_p5_d": 31,
    "best_p5_e": 32,
    "best_p5_f": 33,
    "best_same_face_spread": 34,
    "best_same_face_p15_id": 35,
    "best_same_mask_spread": 36,
    "best_same_mask_p15_id": 37,
}


def csv_text(columns: list[str], rows: list[dict[str, Any]]) -> str:
    lines = [",".join(columns)]
    lines.extend(",".join(str(row[column]) for column in columns) for row in rows)
    return "\n".join(lines) + "\n"


def table_from_rows(columns: list[str], rows: list[dict[str, int]]) -> np.ndarray:
    return np.asarray(
        [[int(row[column]) for column in columns] for row in rows],
        dtype=np.int64,
    )


def rows_from_table(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def ranked_row(
    *,
    rank: int,
    p15_id: int,
    row_indexes: tuple[int, int, int, int, int, int],
    supports: np.ndarray,
    ids: np.ndarray,
    faces: np.ndarray,
    masks: np.ndarray,
    mults: np.ndarray,
    p5_floor: int,
    p6_floor: int,
    p7_floor: int,
    p8_floor: int,
    p11_floor: int,
    p14_floor: int,
) -> dict[str, int]:
    joint = supports[list(row_indexes)].sum(axis=0)
    spread = int(joint.max() - joint.min())
    p5_ids = [int(ids[index]) for index in row_indexes]
    face_values = [int(faces[index]) for index in row_indexes]
    mask_values = [int(masks[index]) for index in row_indexes]
    return {
        "rank": rank,
        "p15_id": int(p15_id),
        "p5_a": p5_ids[0],
        "p5_b": p5_ids[1],
        "p5_c": p5_ids[2],
        "p5_d": p5_ids[3],
        "p5_e": p5_ids[4],
        "p5_f": p5_ids[5],
        "face_a": face_values[0],
        "face_b": face_values[1],
        "face_c": face_values[2],
        "face_d": face_values[3],
        "face_e": face_values[4],
        "face_f": face_values[5],
        "mask_a": mask_values[0],
        "mask_b": mask_values[1],
        "mask_c": mask_values[2],
        "mask_d": mask_values[3],
        "mask_e": mask_values[4],
        "mask_f": mask_values[5],
        "same_face_flag": int(len(set(face_values)) == 1),
        "same_mask_flag": int(len(set(mask_values)) == 1),
        "joint_p0_support": int(joint[0]),
        "joint_p1_support": int(joint[1]),
        "joint_p2_support": int(joint[2]),
        "joint_p3_support": int(joint[3]),
        "joint_p4_support": int(joint[4]),
        "joint_support_min": int(joint.min()),
        "joint_support_max": int(joint.max()),
        "joint_support_spread": spread,
        "below_p14_floor_flag": int(spread < p14_floor),
        "below_p11_floor_flag": int(spread < p11_floor),
        "below_p8_floor_flag": int(spread < p8_floor),
        "below_p7_floor_flag": int(spread < p7_floor),
        "below_p6_floor_flag": int(spread < p6_floor),
        "below_p5_floor_flag": int(spread < p5_floor),
        "support_equal_flag": int(spread == 0),
        "joint_mult_value": int(mults[list(row_indexes)].sum()),
    }


def build_grid_candidates(
    *,
    triples: np.ndarray,
    triple_supports: np.ndarray,
) -> tuple[set[tuple[int, ...]], list[dict[str, int]], int, int]:
    diffs = triple_supports[:, 1:] - triple_supports[:, [0]]
    candidates: set[tuple[int, ...]] = set()
    scale_rows: list[dict[str, int]] = []
    raw_pair_count = 0
    raw_lookup_count = 0
    for scale_id, cell_width in enumerate(CELL_WIDTHS):
        grid: defaultdict[tuple[int, int, int, int], list[int]] = defaultdict(list)
        quantized = np.floor_divide(diffs, cell_width).astype(np.int32)
        for index, key in enumerate(map(tuple, quantized)):
            grid[key].append(index)
        scale_pair_count = 0
        scale_lookup_count = 0
        before_count = len(candidates)
        for anchor_index in range(len(triples)):
            target = tuple(
                np.floor_divide(-diffs[anchor_index], cell_width).astype(np.int32)
            )
            raw_hits: list[int] = []
            for offset in OFFSETS:
                raw_hits.extend(
                    grid.get(
                        tuple(target[axis] + offset[axis] for axis in range(4)),
                        (),
                    )
                )
            if not raw_hits:
                continue
            hit_indexes = np.asarray(raw_hits, dtype=np.int32)
            anchor = triples[anchor_index]
            disjoint = hit_indexes > anchor_index
            hit_triples = triples[hit_indexes]
            disjoint &= (
                (hit_triples[:, 0] != anchor[0])
                & (hit_triples[:, 1] != anchor[0])
                & (hit_triples[:, 2] != anchor[0])
            )
            disjoint &= (
                (hit_triples[:, 0] != anchor[1])
                & (hit_triples[:, 1] != anchor[1])
                & (hit_triples[:, 2] != anchor[1])
            )
            disjoint &= (
                (hit_triples[:, 0] != anchor[2])
                & (hit_triples[:, 1] != anchor[2])
                & (hit_triples[:, 2] != anchor[2])
            )
            hit_indexes = hit_indexes[disjoint]
            scale_lookup_count += len(raw_hits)
            scale_pair_count += len(hit_indexes)
            for hit_index in hit_indexes:
                candidates.add(
                    tuple(
                        sorted(
                            [
                                *map(int, anchor),
                                *map(int, triples[int(hit_index)]),
                            ]
                        )
                    )
                )
        raw_pair_count += scale_pair_count
        raw_lookup_count += scale_lookup_count
        scale_rows.append(
            {
                "scale_id": scale_id,
                "cell_width": cell_width,
                "grid_cell_count": len(grid),
                "raw_pair_count": scale_pair_count,
                "raw_lookup_count": scale_lookup_count,
                "new_unique_candidate_count": len(candidates) - before_count,
            }
        )
    return candidates, scale_rows, raw_pair_count, raw_lookup_count


def build_p15_rows() -> dict[str, Any]:
    p5_tables = np.load(P5_TABLES, allow_pickle=False)
    ext_rows = rows_from_table(
        np.asarray(p5_tables["ext_table"], dtype=np.int64),
        p5.EXT_COLUMNS,
    )
    supports = np.asarray(
        [
            [row[f"p{index}_support"] for index in range(5)]
            for row in ext_rows
        ],
        dtype=np.int64,
    )
    ids = np.asarray([row["p5_id"] for row in ext_rows], dtype=np.int64)
    faces = np.asarray([row["face_id"] for row in ext_rows], dtype=np.int64)
    masks = np.asarray([row["label_mask"] for row in ext_rows], dtype=np.int64)
    mults = np.asarray([row["mult_value"] for row in ext_rows], dtype=np.int64)
    triples = np.asarray(
        list(itertools.combinations(range(len(ext_rows)), 3)),
        dtype=np.int16,
    )
    triple_supports = (
        supports[triples[:, 0]]
        + supports[triples[:, 1]]
        + supports[triples[:, 2]]
    )
    candidates, scale_rows, raw_pair_count, raw_lookup_count = build_grid_candidates(
        triples=triples,
        triple_supports=triple_supports,
    )

    p5_floor = min(row["support_spread"] for row in ext_rows)
    p6_floor = int(load_json(P6_REPORT)["witness"]["pair_min_spread"])
    p7_floor = int(load_json(P7_REPORT)["witness"]["triple_min_spread"])
    p8_floor = int(load_json(P8_REPORT)["witness"]["quad_min_spread"])
    p11_floor = int(load_json(P11_REPORT)["witness"]["quint_min_spread"])
    p14_floor = int(load_json(P14_REPORT)["witness"]["basin_six_min_spread"])

    below_p14 = 0
    below_p11 = 0
    below_p8 = 0
    below_p7 = 0
    below_p6 = 0
    below_p5 = 0
    equal = 0
    same_face_count = 0
    same_mask_count = 0
    low_rows: dict[tuple[int, ...], dict[str, int]] = {}
    best_any: dict[str, int] | None = None
    best_same_face: dict[str, int] | None = None
    best_same_mask: dict[str, int] | None = None

    for p15_id, candidate in enumerate(sorted(candidates)):
        row = ranked_row(
            rank=0,
            p15_id=p15_id,
            row_indexes=candidate,
            supports=supports,
            ids=ids,
            faces=faces,
            masks=masks,
            mults=mults,
            p5_floor=p5_floor,
            p6_floor=p6_floor,
            p7_floor=p7_floor,
            p8_floor=p8_floor,
            p11_floor=p11_floor,
            p14_floor=p14_floor,
        )
        spread = row["joint_support_spread"]
        if spread < p14_floor:
            below_p14 += 1
        if spread < p11_floor:
            below_p11 += 1
        if spread < p8_floor:
            below_p8 += 1
        if spread < p7_floor:
            below_p7 += 1
        if spread < p6_floor:
            below_p6 += 1
        if spread < p5_floor:
            below_p5 += 1
        if spread == 0:
            equal += 1
        if row["same_face_flag"] == 1:
            same_face_count += 1
        if row["same_mask_flag"] == 1:
            same_mask_count += 1
        key = (spread, p15_id)
        if best_any is None or key < (
            best_any["joint_support_spread"],
            best_any["p15_id"],
        ):
            best_any = row
        if row["same_face_flag"] == 1 and (
            best_same_face is None
            or key
            < (
                best_same_face["joint_support_spread"],
                best_same_face["p15_id"],
            )
        ):
            best_same_face = row
        if row["same_mask_flag"] == 1 and (
            best_same_mask is None
            or key
            < (
                best_same_mask["joint_support_spread"],
                best_same_mask["p15_id"],
            )
        ):
            best_same_mask = row
        if spread < p8_floor:
            low_rows[
                (
                    row["p5_a"],
                    row["p5_b"],
                    row["p5_c"],
                    row["p5_d"],
                    row["p5_e"],
                    row["p5_f"],
                )
            ] = row

    if best_any is None or best_same_face is None or best_same_mask is None:
        raise ValueError("empty p15 screen")
    top_rows = sorted(
        low_rows.values(),
        key=lambda row: (row["joint_support_spread"], row["p15_id"]),
    )[:TOP_N]
    if len(top_rows) != TOP_N:
        raise ValueError("p15 top row capture is too small")
    for rank, row in enumerate(top_rows):
        row["rank"] = rank

    obs = {
        "p5_extension_count": len(ext_rows),
        "triple_count": len(triples),
        "full_six_count": math.comb(len(ext_rows), 6),
        "grid_scale_count": len(CELL_WIDTHS),
        "grid_neighbor_count": len(OFFSETS),
        "raw_pair_count": raw_pair_count,
        "raw_lookup_count": raw_lookup_count,
        "unique_candidate_count": len(candidates),
        "p5_single_floor": p5_floor,
        "p6_pair_floor": p6_floor,
        "p7_triple_floor": p7_floor,
        "p8_quad_floor": p8_floor,
        "p11_quint_floor": p11_floor,
        "p14_basin_six_floor": p14_floor,
        "grid_min_spread": best_any["joint_support_spread"],
        "grid_min_below_p14_flag": int(best_any["joint_support_spread"] < p14_floor),
        "grid_min_below_p11_flag": int(best_any["joint_support_spread"] < p11_floor),
        "grid_min_below_p8_flag": int(best_any["joint_support_spread"] < p8_floor),
        "below_p14_candidate_count": below_p14,
        "below_p11_candidate_count": below_p11,
        "below_p8_candidate_count": below_p8,
        "below_p7_candidate_count": below_p7,
        "below_p6_candidate_count": below_p6,
        "below_p5_candidate_count": below_p5,
        "support_equal_candidate_count": equal,
        "same_face_candidate_count": same_face_count,
        "same_mask_candidate_count": same_mask_count,
        "best_p15_id": best_any["p15_id"],
        "best_p5_a": best_any["p5_a"],
        "best_p5_b": best_any["p5_b"],
        "best_p5_c": best_any["p5_c"],
        "best_p5_d": best_any["p5_d"],
        "best_p5_e": best_any["p5_e"],
        "best_p5_f": best_any["p5_f"],
        "best_same_face_spread": best_same_face["joint_support_spread"],
        "best_same_face_p15_id": best_same_face["p15_id"],
        "best_same_mask_spread": best_same_mask["joint_support_spread"],
        "best_same_mask_p15_id": best_same_mask["p15_id"],
    }
    obs_rows = [
        {
            "observable_id": code,
            "observable_code": code,
            "value": int(obs[name]),
            "scale_code": 0,
        }
        for name, code in sorted(OBS_CODES.items(), key=lambda item: item[1])
    ]
    return {
        "top_rows": top_rows,
        "scale_rows": scale_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def best_rows_for_witness(rows: list[dict[str, int]]) -> list[dict[str, Any]]:
    return [
        {
            "rank": row["rank"],
            "p15_id": row["p15_id"],
            "p5_ids": [
                row["p5_a"],
                row["p5_b"],
                row["p5_c"],
                row["p5_d"],
                row["p5_e"],
                row["p5_f"],
            ],
            "faces": [
                row["face_a"],
                row["face_b"],
                row["face_c"],
                row["face_d"],
                row["face_e"],
                row["face_f"],
            ],
            "masks": [
                row["mask_a"],
                row["mask_b"],
                row["mask_c"],
                row["mask_d"],
                row["mask_e"],
                row["mask_f"],
            ],
            "support": [
                row["joint_p0_support"],
                row["joint_p1_support"],
                row["joint_p2_support"],
                row["joint_p3_support"],
                row["joint_p4_support"],
            ],
            "spread": row["joint_support_spread"],
            "same_face": row["same_face_flag"],
            "same_mask": row["same_mask_flag"],
        }
        for row in rows
    ]


def build_payloads() -> dict[str, Any]:
    rows = build_p15_rows()
    top_table = table_from_rows(TOP_COLUMNS, rows["top_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    scale_table = table_from_rows(SCALE_COLUMNS, rows["scale_rows"])
    obs = rows["obs"]
    p5_report = load_json(P5_REPORT)
    p6_report = load_json(P6_REPORT)
    p7_report = load_json(P7_REPORT)
    p8_report = load_json(P8_REPORT)
    p11_report = load_json(P11_REPORT)
    p14_report = load_json(P14_REPORT)
    checks = {
        "input_certificates_available": (
            p5_report.get("all_checks_pass") is True
            and p6_report.get("all_checks_pass") is True
            and p7_report.get("all_checks_pass") is True
            and p8_report.get("all_checks_pass") is True
            and p11_report.get("all_checks_pass") is True
            and p14_report.get("all_checks_pass") is True
        ),
        "grid_scope_matches": (
            obs["p5_extension_count"],
            obs["triple_count"],
            obs["full_six_count"],
            obs["grid_scale_count"],
            obs["grid_neighbor_count"],
            obs["raw_pair_count"],
            obs["raw_lookup_count"],
            obs["unique_candidate_count"],
        )
        == (144, 487_344, 11_143_364_232, 4, 81, 2_093_627, 4_499_291, 434_839),
        "scale_rows_match": tuple(
            (
                row["scale_id"],
                row["cell_width"],
                row["grid_cell_count"],
                row["raw_pair_count"],
                row["raw_lookup_count"],
                row["new_unique_candidate_count"],
            )
            for row in rows["scale_rows"]
        )
        == (
            (0, 1_048_576, 487_334, 498, 1_070, 114),
            (1, 2_097_152, 487_135, 8_042, 17_316, 1_661),
            (2, 4_194_304, 484_709, 125_055, 268_567, 25_993),
            (3, 8_388_608, 449_585, 1_960_032, 4_212_338, 407_071),
        ),
        "grid_six_beats_p14": (
            obs["p14_basin_six_floor"],
            obs["p11_quint_floor"],
            obs["p8_quad_floor"],
            obs["grid_min_spread"],
            obs["grid_min_below_p14_flag"],
            obs["grid_min_below_p11_flag"],
            obs["grid_min_below_p8_flag"],
        )
        == (1_164_096, 1_815_040, 2_447_744, 492_736, 1, 1, 1),
        "descent_counts_match": (
            obs["below_p14_candidate_count"],
            obs["below_p11_candidate_count"],
            obs["below_p8_candidate_count"],
            obs["below_p7_candidate_count"],
            obs["below_p6_candidate_count"],
            obs["below_p5_candidate_count"],
            obs["support_equal_candidate_count"],
        )
        == (1, 25, 101, 119, 30_547, 39_233, 0),
        "same_face_and_mask_counts_match": (
            obs["same_face_candidate_count"],
            obs["same_mask_candidate_count"],
        )
        == (4_020, 4_020),
        "best_candidate_matches_expected": (
            obs["best_p15_id"],
            obs["best_p5_a"],
            obs["best_p5_b"],
            obs["best_p5_c"],
            obs["best_p5_d"],
            obs["best_p5_e"],
            obs["best_p5_f"],
        )
        == (58_834, 1, 47, 57, 79, 110, 128),
        "best_same_face_and_mask_match": (
            obs["best_same_face_spread"],
            obs["best_same_face_p15_id"],
            obs["best_same_mask_spread"],
            obs["best_same_mask_p15_id"],
        )
        == (2_644_672, 180_252, 2_644_672, 180_252),
        "table_shapes_match_codebooks": (
            tuple(top_table.shape),
            tuple(obs_table.shape),
            tuple(scale_table.shape),
        )
        == (
            (TOP_N, len(TOP_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
            (len(CELL_WIDTHS), len(SCALE_COLUMNS)),
        ),
    }
    witness = {
        "classification": "full144_centered_grid_six_move_screen",
        "candidate_construction": (
            "all p5 triples are indexed by four centered support differences; "
            "four cell widths probe the 81 neighboring cells around each "
            "negative target, then disjoint triple-pairs are deduplicated as "
            "sextuples"
        ),
        "cell_widths": CELL_WIDTHS,
        "full_six_count": obs["full_six_count"],
        "unique_candidate_count": obs["unique_candidate_count"],
        "raw_pair_count": obs["raw_pair_count"],
        "p14_basin_six_floor": obs["p14_basin_six_floor"],
        "grid_min_spread": obs["grid_min_spread"],
        "below_p14_candidate_count": obs["below_p14_candidate_count"],
        "below_p11_candidate_count": obs["below_p11_candidate_count"],
        "below_p8_candidate_count": obs["below_p8_candidate_count"],
        "below_p7_candidate_count": obs["below_p7_candidate_count"],
        "below_p6_candidate_count": obs["below_p6_candidate_count"],
        "below_p5_candidate_count": obs["below_p5_candidate_count"],
        "support_equal_candidate_count": obs["support_equal_candidate_count"],
        "same_face_candidate_count": obs["same_face_candidate_count"],
        "same_mask_candidate_count": obs["same_mask_candidate_count"],
        "best_candidates": best_rows_for_witness(rows["top_rows"][:16]),
        "scale_rows": rows["scale_rows"],
        "reading": (
            "The bounded full-144 centered grid screen finds one screened "
            "sextuple below the p14 basin floor, lowering support spread to "
            "492736, but it still finds no raw-support equalizer."
        ),
        "top_table_sha256": sha_array(top_table),
        "observable_table_sha256": sha_array(obs_table),
        "scale_table_sha256": sha_array(scale_table),
    }
    p15 = {
        "schema": "eta6.p15@1",
        "object": "eta6",
        "construction": {
            "source": "all 144 p5 rows",
            "test": "bounded centered grid six-move screen",
            "classification": witness["classification"],
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.p15.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_P15_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The bounded full-144 centered grid screen lowers the screened "
            "six-move support floor to 492736, beating p14, while no screened "
            "candidate equalizes raw support."
        ),
        "stage_protocol": {
            "draft": "index all p5 triples by centered support differences",
            "witness": "probe four grid widths around each complementary triple target",
            "coherence": "deduplicate sextuples and compare against p14, p11, p8, p7, p6, and p5 floors",
            "closure": "certify bounded full-144 metric descent without screened support equalization",
            "emit": "emit compact p15 artifacts and the next seam",
        },
        "inputs": {
            "p5_report": input_entry(
                P5_REPORT,
                {
                    "status": p5_report.get("status"),
                    "certificate_sha256": p5_report.get("certificate_sha256"),
                },
            ),
            "p5_tables": input_entry(P5_TABLES),
            "p6_report": input_entry(
                P6_REPORT,
                {
                    "status": p6_report.get("status"),
                    "certificate_sha256": p6_report.get("certificate_sha256"),
                },
            ),
            "p7_report": input_entry(
                P7_REPORT,
                {
                    "status": p7_report.get("status"),
                    "certificate_sha256": p7_report.get("certificate_sha256"),
                },
            ),
            "p8_report": input_entry(
                P8_REPORT,
                {
                    "status": p8_report.get("status"),
                    "certificate_sha256": p8_report.get("certificate_sha256"),
                },
            ),
            "p11_report": input_entry(
                P11_REPORT,
                {
                    "status": p11_report.get("status"),
                    "certificate_sha256": p11_report.get("certificate_sha256"),
                },
            ),
            "p14_report": input_entry(
                P14_REPORT,
                {
                    "status": p14_report.get("status"),
                    "certificate_sha256": p14_report.get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "p15": relpath(OUT_DIR / "p15.json"),
            "top_csv": relpath(OUT_DIR / "top.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "scale_csv": relpath(OUT_DIR / "scale.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "bounded full-144 centered grid screen over all 487344 p5 triples",
                "2093627 raw disjoint triple-pairs checked across four grid scales",
                "434839 unique screened sextuples checked",
                "best screened six-move support spread is 492736",
                "no screened sextuple equalizes raw support",
            ],
            "does_not_certify_because_out_of_scope": [
                "complete six-move search over all 11143364232 p5 sextuples",
                "that no unscreened sextuple beats 492736",
                "a new post-surgery carrier-level eta6 gap",
                "global closure under repeated non-cubic surgeries",
            ],
        },
        "next_highest_yield_item": (
            "Run p16 as a carrier-level margin test on the p15 winner and its "
            "nearest symmetry mates."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.p15.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.p15.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "p15": p15,
        "top_csv": csv_text(TOP_COLUMNS, rows["top_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "scale_csv": csv_text(SCALE_COLUMNS, rows["scale_rows"]),
        "top_table": top_table,
        "obs_table": obs_table,
        "scale_table": scale_table,
        "cert": cert,
        "report": report,
        "manifest": manifest,
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
    updated = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": sorted(obligations, key=lambda row: row["id"]),
    }
    updated["registry_sha256"] = self_hash(updated, "registry_sha256")
    write_json(INDEX_PATH, updated)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / "p15.json", payloads["p15"])
    (OUT_DIR / "top.csv").write_text(payloads["top_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    (OUT_DIR / "scale.csv").write_text(payloads["scale_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        top_table=payloads["top_table"],
        observable_table=payloads["obs_table"],
        scale_table=payloads["scale_table"],
    )
    write_json(OUT_DIR / "cert.json", payloads["cert"])
    write_json(OUT_DIR / "report.json", payloads["report"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
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
                "report": relpath(OUT_DIR / "report.json"),
                "manifest": relpath(OUT_DIR / "manifest.json"),
                "certificate_sha256": report["certificate_sha256"],
                "witness": report["witness"],
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
