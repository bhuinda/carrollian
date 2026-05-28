from __future__ import annotations

import heapq
import json
from typing import Any

import numpy as np

try:
    from . import derive_eta6_p25 as p25
    from . import derive_eta6_p35 as p35
    from . import derive_eta6_p37 as p37
    from . import derive_eta6_p38 as p38
    from .derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    import derive_eta6_p25 as p25
    import derive_eta6_p35 as p35
    import derive_eta6_p37 as p37
    import derive_eta6_p38 as p38
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "eta6_p39"
STATUS = "ETA6_P39_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

P25_REPORT = p37.P25_REPORT
P25_TABLES = p37.P25_TABLES
P26_REPORT = p37.P26_REPORT
P27_REPORT = p37.P27_REPORT
P28_REPORT = p37.P28_REPORT
P29_REPORT = p37.P29_REPORT
P30_REPORT = p37.P30_REPORT
P31_REPORT = p37.P31_REPORT
P32_REPORT = p37.P32_REPORT
P33_REPORT = p37.P33_REPORT
P34_REPORT = p37.P34_REPORT
P35_REPORT = p37.P35_REPORT
P36_REPORT = p37.P36_REPORT
P37_REPORT = p37.OUT_DIR / "report.json"
P38_REPORT = p38.OUT_DIR / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_p39.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_p39.py"

TOP_N = 32
SEED_N = 32768
LOW_RANK_CUTOFF = 8192
PACK_BITS = 8

TOP_COLUMNS = [
    "rank",
    "p39_id",
    "source_count",
    "source_min_rank",
    "source_max_rank",
    "p25_a",
    "p25_b",
    "p25_c",
    "p25_d",
    "p25_e",
    "p25_f",
    "p24_a",
    "p24_b",
    "p24_c",
    "p24_d",
    "p24_e",
    "p24_f",
    "lift_a",
    "lift_b",
    "lift_c",
    "lift_d",
    "lift_e",
    "lift_f",
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
    "same_lift_flag",
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
    "below_p38_floor_flag",
    "below_p37_floor_flag",
    "below_p36_floor_flag",
    "below_p35_floor_flag",
    "below_p34_floor_flag",
    "below_p33_floor_flag",
    "below_p32_floor_flag",
    "below_p31_floor_flag",
    "below_p30_floor_flag",
    "below_p29_floor_flag",
    "below_p28_floor_flag",
    "below_p27_floor_flag",
    "below_p25_floor_flag",
    "support_equal_flag",
    "joint_mult_value",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBS_NAMES = [
    "p25_extension_count",
    "p31_top_seed_count",
    "p31_top32768_worst_spread",
    "p31_top32768_worst_p31_id",
    "raw_extension_count",
    "candidate_count",
    "duplicate_candidate_count",
    "multi_source_candidate_count",
    "max_source_multiplicity",
    "p25_single_floor",
    "p27_pair_floor",
    "p28_triple_floor",
    "p29_quad_floor",
    "p30_bounded_floor",
    "p31_quint_floor",
    "p32_seeded_floor",
    "p33_basin_floor",
    "p34_basin_floor",
    "p35_basin_floor",
    "p36_basin_floor",
    "p37_basin_floor",
    "p38_branch_floor",
    "p39_basin_min_spread",
    "basin_min_below_p38_flag",
    "basin_min_below_p37_flag",
    "basin_min_below_p36_flag",
    "basin_min_below_p35_flag",
    "basin_min_below_p34_flag",
    "basin_min_below_p33_flag",
    "basin_min_below_p32_flag",
    "basin_min_below_p31_flag",
    "basin_min_below_p30_flag",
    "basin_min_below_p29_flag",
    "basin_min_below_p28_flag",
    "below_p38_candidate_count",
    "below_p37_candidate_count",
    "below_p36_candidate_count",
    "below_p35_candidate_count",
    "below_p34_candidate_count",
    "below_p33_candidate_count",
    "below_p32_candidate_count",
    "below_p31_candidate_count",
    "below_p30_candidate_count",
    "below_p29_candidate_count",
    "below_p28_candidate_count",
    "below_p27_candidate_count",
    "below_p25_candidate_count",
    "support_equal_candidate_count",
    "best_p39_id",
    "best_p25_a",
    "best_p25_b",
    "best_p25_c",
    "best_p25_d",
    "best_p25_e",
    "best_p25_f",
    "best_source_count",
    "best_source_min_rank",
    "best_source_max_rank",
    "best_same_face_spread",
    "best_same_face_p39_id",
    "best_same_mask_spread",
    "best_same_mask_p39_id",
    "best_source_rank0_spread",
    "best_source_rank0_p39_id",
    "best_low8192_spread",
    "best_low8192_p39_id",
    "p26_horizon_component_count",
    "p26_checked_positive_row_total",
    "p26_min_component_margin",
    "compound_horizon_margin",
    "compound_horizon_strict_flag",
    "p26_margin_preserved_flag",
    "packed_candidate_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def pack_ids(ids: tuple[int, ...] | list[int]) -> int:
    value = 0
    for index, item in enumerate(sorted(ids)):
        value |= int(item) << (PACK_BITS * index)
    return value


def unpack_ids(value: int) -> list[int]:
    return [(value >> (PACK_BITS * index)) & 0xFF for index in range(6)]


def row_key(row: dict[str, int]) -> tuple[int, int]:
    return row["joint_support_spread"], row["p39_id"]


def push_top(
    heap: list[tuple[int, int, dict[str, int]]],
    row: dict[str, int],
) -> None:
    item = (-row["joint_support_spread"], -row["p39_id"], row)
    if len(heap) < TOP_N:
        heapq.heappush(heap, item)
    elif item > heap[0]:
        heapq.heapreplace(heap, item)


def top_rows_from_heap(heap: list[tuple[int, int, dict[str, int]]]) -> list[dict[str, int]]:
    rows = [item[2] for item in sorted(heap, key=lambda item: (-item[0], -item[1]))]
    for rank, row in enumerate(rows):
        row["rank"] = rank
    return rows


def candidate_row(
    *,
    p39_id: int,
    packed: int,
    source_info: list[int],
    ext_rows: list[dict[str, int]],
    supports: np.ndarray,
    floors: dict[str, int],
    p37_floor: int,
    p38_floor: int,
) -> dict[str, int]:
    ids = unpack_ids(packed)
    rows = [ext_rows[p25_id] for p25_id in ids]
    joint = supports[ids].sum(axis=0)
    spread = int(joint.max() - joint.min())
    lifts = [row["lift_id"] for row in rows]
    faces = [row["face_id"] for row in rows]
    masks = [row["label_mask"] for row in rows]
    return {
        "rank": 0,
        "p39_id": p39_id,
        "source_count": source_info[0],
        "source_min_rank": source_info[1],
        "source_max_rank": source_info[2],
        "p25_a": ids[0],
        "p25_b": ids[1],
        "p25_c": ids[2],
        "p25_d": ids[3],
        "p25_e": ids[4],
        "p25_f": ids[5],
        "p24_a": rows[0]["p24_row_id"],
        "p24_b": rows[1]["p24_row_id"],
        "p24_c": rows[2]["p24_row_id"],
        "p24_d": rows[3]["p24_row_id"],
        "p24_e": rows[4]["p24_row_id"],
        "p24_f": rows[5]["p24_row_id"],
        "lift_a": lifts[0],
        "lift_b": lifts[1],
        "lift_c": lifts[2],
        "lift_d": lifts[3],
        "lift_e": lifts[4],
        "lift_f": lifts[5],
        "face_a": faces[0],
        "face_b": faces[1],
        "face_c": faces[2],
        "face_d": faces[3],
        "face_e": faces[4],
        "face_f": faces[5],
        "mask_a": masks[0],
        "mask_b": masks[1],
        "mask_c": masks[2],
        "mask_d": masks[3],
        "mask_e": masks[4],
        "mask_f": masks[5],
        "same_lift_flag": int(len(set(lifts)) == 1),
        "same_face_flag": int(len(set(faces)) == 1),
        "same_mask_flag": int(len(set(masks)) == 1),
        "joint_p0_support": int(joint[0]),
        "joint_p1_support": int(joint[1]),
        "joint_p2_support": int(joint[2]),
        "joint_p3_support": int(joint[3]),
        "joint_p4_support": int(joint[4]),
        "joint_support_min": int(joint.min()),
        "joint_support_max": int(joint.max()),
        "joint_support_spread": spread,
        "below_p38_floor_flag": int(spread < p38_floor),
        "below_p37_floor_flag": int(spread < p37_floor),
        "below_p36_floor_flag": int(spread < floors["p36"]),
        "below_p35_floor_flag": int(spread < floors["p35"]),
        "below_p34_floor_flag": int(spread < floors["p34"]),
        "below_p33_floor_flag": int(spread < floors["p33"]),
        "below_p32_floor_flag": int(spread < floors["p32"]),
        "below_p31_floor_flag": int(spread < floors["p31"]),
        "below_p30_floor_flag": int(spread < floors["p30"]),
        "below_p29_floor_flag": int(spread < floors["p29"]),
        "below_p28_floor_flag": int(spread < floors["p28"]),
        "below_p27_floor_flag": int(spread < floors["p27"]),
        "below_p25_floor_flag": int(spread < floors["p25"]),
        "support_equal_flag": int(spread == 0),
        "joint_mult_value": int(sum(row["mult_value"] for row in rows)),
    }


def witness_row(row: dict[str, int]) -> dict[str, Any]:
    return {
        "rank": row["rank"],
        "p39_id": row["p39_id"],
        "source_count": row["source_count"],
        "source_min_rank": row["source_min_rank"],
        "source_max_rank": row["source_max_rank"],
        "p25_ids": [row[f"p25_{label}"] for label in "abcdef"],
        "faces": [row[f"face_{label}"] for label in "abcdef"],
        "masks": [row[f"mask_{label}"] for label in "abcdef"],
        "support": [row[f"joint_p{index}_support"] for index in range(5)],
        "spread": row["joint_support_spread"],
    }


def build_p39_rows() -> dict[str, Any]:
    p25_tables = np.load(P25_TABLES, allow_pickle=False)
    ext_rows = p35.rows_from_table(
        np.asarray(p25_tables["ext_table"], dtype=np.int64),
        p25.EXT_COLUMNS,
    )
    supports = np.asarray([p35.support(row) for row in ext_rows], dtype=np.int64)
    floors = p37.load_floors(supports)
    p37_report = load_json(P37_REPORT)
    p38_report = load_json(P38_REPORT)
    p37_floor = int(p37_report["witness"]["p37_basin_min_spread"])
    p38_floor = int(p38_report["witness"]["branch_min_floor"])
    seeds = p35.top_p31_rows(
        ext_rows,
        supports,
        seed_count=SEED_N,
        p25_floor=floors["p25"],
        p27_floor=floors["p27"],
        p28_floor=floors["p28"],
        p29_floor=floors["p29"],
        p30_floor=floors["p30"],
    )

    candidates: dict[int, list[int]] = {}
    raw_extension_count = 0
    for seed in seeds:
        seed_ids = tuple(seed[f"p25_{label}"] for label in "abcde")
        used = set(seed_ids)
        rank = seed["rank"]
        for extension_id in range(len(ext_rows)):
            if extension_id in used:
                continue
            raw_extension_count += 1
            packed = pack_ids((*seed_ids, extension_id))
            source_info = candidates.get(packed)
            if source_info is None:
                candidates[packed] = [1, rank, rank]
            else:
                source_info[0] += 1
                source_info[1] = min(source_info[1], rank)
                source_info[2] = max(source_info[2], rank)

    counts = {
        "below_p38": 0,
        "below_p37": 0,
        "below_p36": 0,
        "below_p35": 0,
        "below_p34": 0,
        "below_p33": 0,
        "below_p32": 0,
        "below_p31": 0,
        "below_p30": 0,
        "below_p29": 0,
        "below_p28": 0,
        "below_p27": 0,
        "below_p25": 0,
        "equal": 0,
    }
    best_any: dict[str, int] | None = None
    best_same_face: dict[str, int] | None = None
    best_same_mask: dict[str, int] | None = None
    best_source_rank0: dict[str, int] | None = None
    best_low8192: dict[str, int] | None = None
    top_heap: list[tuple[int, int, dict[str, int]]] = []
    multi_source_count = 0
    max_source_multiplicity = 0

    for p39_id, (packed, source_info) in enumerate(sorted(candidates.items())):
        if source_info[0] > 1:
            multi_source_count += 1
        max_source_multiplicity = max(max_source_multiplicity, source_info[0])
        row = candidate_row(
            p39_id=p39_id,
            packed=packed,
            source_info=source_info,
            ext_rows=ext_rows,
            supports=supports,
            floors=floors,
            p37_floor=p37_floor,
            p38_floor=p38_floor,
        )
        spread = row["joint_support_spread"]
        for name, floor in (
            ("below_p38", p38_floor),
            ("below_p37", p37_floor),
            ("below_p36", floors["p36"]),
            ("below_p35", floors["p35"]),
            ("below_p34", floors["p34"]),
            ("below_p33", floors["p33"]),
            ("below_p32", floors["p32"]),
            ("below_p31", floors["p31"]),
            ("below_p30", floors["p30"]),
            ("below_p29", floors["p29"]),
            ("below_p28", floors["p28"]),
            ("below_p27", floors["p27"]),
            ("below_p25", floors["p25"]),
        ):
            if spread < floor:
                counts[name] += 1
        if spread == 0:
            counts["equal"] += 1

        if best_any is None or row_key(row) < row_key(best_any):
            best_any = row
        if row["same_face_flag"] == 1 and (
            best_same_face is None or row_key(row) < row_key(best_same_face)
        ):
            best_same_face = row
        if row["same_mask_flag"] == 1 and (
            best_same_mask is None or row_key(row) < row_key(best_same_mask)
        ):
            best_same_mask = row
        if row["source_min_rank"] == 0 and (
            best_source_rank0 is None or row_key(row) < row_key(best_source_rank0)
        ):
            best_source_rank0 = row
        if row["source_min_rank"] < LOW_RANK_CUTOFF and (
            best_low8192 is None or row_key(row) < row_key(best_low8192)
        ):
            best_low8192 = row
        push_top(top_heap, row)

    if (
        best_any is None
        or best_same_face is None
        or best_same_mask is None
        or best_source_rank0 is None
        or best_low8192 is None
    ):
        raise ValueError("empty p39 search")
    top_rows = top_rows_from_heap(top_heap)

    p26_report = load_json(P26_REPORT)
    p26_boundary = p26_report["witness"]["claim_boundary"]
    p26_min_margin = min(
        component["margin"] for component in p26_report["witness"]["components"]
    )
    obs = {
        "p25_extension_count": len(ext_rows),
        "p31_top_seed_count": len(seeds),
        "p31_top32768_worst_spread": seeds[-1]["joint_support_spread"],
        "p31_top32768_worst_p31_id": seeds[-1]["p31_id"],
        "raw_extension_count": raw_extension_count,
        "candidate_count": len(candidates),
        "duplicate_candidate_count": raw_extension_count - len(candidates),
        "multi_source_candidate_count": multi_source_count,
        "max_source_multiplicity": max_source_multiplicity,
        "p25_single_floor": floors["p25"],
        "p27_pair_floor": floors["p27"],
        "p28_triple_floor": floors["p28"],
        "p29_quad_floor": floors["p29"],
        "p30_bounded_floor": floors["p30"],
        "p31_quint_floor": floors["p31"],
        "p32_seeded_floor": floors["p32"],
        "p33_basin_floor": floors["p33"],
        "p34_basin_floor": floors["p34"],
        "p35_basin_floor": floors["p35"],
        "p36_basin_floor": floors["p36"],
        "p37_basin_floor": p37_floor,
        "p38_branch_floor": p38_floor,
        "p39_basin_min_spread": best_any["joint_support_spread"],
        "basin_min_below_p38_flag": int(best_any["joint_support_spread"] < p38_floor),
        "basin_min_below_p37_flag": int(best_any["joint_support_spread"] < p37_floor),
        "basin_min_below_p36_flag": int(best_any["joint_support_spread"] < floors["p36"]),
        "basin_min_below_p35_flag": int(best_any["joint_support_spread"] < floors["p35"]),
        "basin_min_below_p34_flag": int(best_any["joint_support_spread"] < floors["p34"]),
        "basin_min_below_p33_flag": int(best_any["joint_support_spread"] < floors["p33"]),
        "basin_min_below_p32_flag": int(best_any["joint_support_spread"] < floors["p32"]),
        "basin_min_below_p31_flag": int(best_any["joint_support_spread"] < floors["p31"]),
        "basin_min_below_p30_flag": int(best_any["joint_support_spread"] < floors["p30"]),
        "basin_min_below_p29_flag": int(best_any["joint_support_spread"] < floors["p29"]),
        "basin_min_below_p28_flag": int(best_any["joint_support_spread"] < floors["p28"]),
        "below_p38_candidate_count": counts["below_p38"],
        "below_p37_candidate_count": counts["below_p37"],
        "below_p36_candidate_count": counts["below_p36"],
        "below_p35_candidate_count": counts["below_p35"],
        "below_p34_candidate_count": counts["below_p34"],
        "below_p33_candidate_count": counts["below_p33"],
        "below_p32_candidate_count": counts["below_p32"],
        "below_p31_candidate_count": counts["below_p31"],
        "below_p30_candidate_count": counts["below_p30"],
        "below_p29_candidate_count": counts["below_p29"],
        "below_p28_candidate_count": counts["below_p28"],
        "below_p27_candidate_count": counts["below_p27"],
        "below_p25_candidate_count": counts["below_p25"],
        "support_equal_candidate_count": counts["equal"],
        "best_p39_id": best_any["p39_id"],
        "best_p25_a": best_any["p25_a"],
        "best_p25_b": best_any["p25_b"],
        "best_p25_c": best_any["p25_c"],
        "best_p25_d": best_any["p25_d"],
        "best_p25_e": best_any["p25_e"],
        "best_p25_f": best_any["p25_f"],
        "best_source_count": best_any["source_count"],
        "best_source_min_rank": best_any["source_min_rank"],
        "best_source_max_rank": best_any["source_max_rank"],
        "best_same_face_spread": best_same_face["joint_support_spread"],
        "best_same_face_p39_id": best_same_face["p39_id"],
        "best_same_mask_spread": best_same_mask["joint_support_spread"],
        "best_same_mask_p39_id": best_same_mask["p39_id"],
        "best_source_rank0_spread": best_source_rank0["joint_support_spread"],
        "best_source_rank0_p39_id": best_source_rank0["p39_id"],
        "best_low8192_spread": best_low8192["joint_support_spread"],
        "best_low8192_p39_id": best_low8192["p39_id"],
        "p26_horizon_component_count": p26_boundary["checked_component_count"],
        "p26_checked_positive_row_total": p26_boundary["checked_positive_row_total"],
        "p26_min_component_margin": p26_min_margin,
        "compound_horizon_margin": min(p26_min_margin, best_any["joint_support_spread"]),
        "compound_horizon_strict_flag": int(p26_min_margin > 0),
        "p26_margin_preserved_flag": int(
            p26_boundary["support_equalizer_absent"] == 1
            and p26_boundary["universal_completion_claim"] == 0
        ),
        "packed_candidate_flag": 1,
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
        "obs": obs,
        "obs_rows": obs_rows,
        "p26_report": p26_report,
        "p37_report": p37_report,
        "p38_report": p38_report,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_p39_rows()
    top_table = p35.table_from_rows(TOP_COLUMNS, rows["top_rows"])
    obs_table = p35.table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    reports = {
        "p25": load_json(P25_REPORT),
        "p26": rows["p26_report"],
        "p27": load_json(P27_REPORT),
        "p28": load_json(P28_REPORT),
        "p29": load_json(P29_REPORT),
        "p30": load_json(P30_REPORT),
        "p31": load_json(P31_REPORT),
        "p32": load_json(P32_REPORT),
        "p33": load_json(P33_REPORT),
        "p34": load_json(P34_REPORT),
        "p35": load_json(P35_REPORT),
        "p36": load_json(P36_REPORT),
        "p37": rows["p37_report"],
        "p38": rows["p38_report"],
    }
    checks = {
        "input_certificates_available": all(
            report.get("all_checks_pass") is True for report in reports.values()
        ),
        "packed_basin_size_matches": (
            obs["p25_extension_count"],
            obs["p31_top_seed_count"],
            obs["p31_top32768_worst_spread"],
            obs["p31_top32768_worst_p31_id"],
            obs["raw_extension_count"],
            obs["candidate_count"],
            obs["duplicate_candidate_count"],
            obs["multi_source_candidate_count"],
            obs["max_source_multiplicity"],
            obs["packed_candidate_flag"],
        )
        == (144, 32_768, 19_618_592, 274_598_157, 4_554_752, 4_482_624, 72_128, 67_402, 6, 1),
        "packed_floor_stable": (
            obs["p38_branch_floor"],
            obs["p37_basin_floor"],
            obs["p39_basin_min_spread"],
            obs["basin_min_below_p38_flag"],
            obs["basin_min_below_p37_flag"],
            obs["basin_min_below_p36_flag"],
        )
        == (492_736, 492_736, 492_736, 0, 0, 1),
        "descent_counts_match": (
            obs["below_p38_candidate_count"],
            obs["below_p37_candidate_count"],
            obs["below_p36_candidate_count"],
            obs["below_p35_candidate_count"],
            obs["below_p34_candidate_count"],
            obs["below_p33_candidate_count"],
            obs["below_p32_candidate_count"],
            obs["below_p31_candidate_count"],
            obs["below_p30_candidate_count"],
            obs["below_p29_candidate_count"],
            obs["below_p28_candidate_count"],
            obs["below_p27_candidate_count"],
            obs["below_p25_candidate_count"],
            obs["support_equal_candidate_count"],
        )
        == (0, 0, 15, 632, 3_027, 5_629, 4_496, 20, 467, 67, 79, 15_526, 19_367, 0),
        "best_candidate_matches_expected": (
            obs["best_p39_id"],
            obs["best_p25_a"],
            obs["best_p25_b"],
            obs["best_p25_c"],
            obs["best_p25_d"],
            obs["best_p25_e"],
            obs["best_p25_f"],
            obs["best_source_count"],
            obs["best_source_min_rank"],
            obs["best_source_max_rank"],
        )
        == (2_335_598, 1, 47, 57, 79, 110, 128, 2, 4_756, 4_757),
        "same_face_and_source_controls_match": (
            obs["best_same_face_spread"],
            obs["best_same_face_p39_id"],
            obs["best_same_mask_spread"],
            obs["best_same_mask_p39_id"],
            obs["best_source_rank0_spread"],
            obs["best_source_rank0_p39_id"],
            obs["best_low8192_spread"],
            obs["best_low8192_p39_id"],
        )
        == (2_644_672, 30_854, 2_644_672, 30_854, 10_529_536, 75_514, 492_736, 2_335_598),
        "p26_horizon_margins_remain_strict": (
            obs["p26_horizon_component_count"],
            obs["p26_checked_positive_row_total"],
            obs["p26_min_component_margin"],
            obs["compound_horizon_margin"],
            obs["compound_horizon_strict_flag"],
            obs["p26_margin_preserved_flag"],
        )
        == (4, 7_735_158, 1, 1, 1, 1),
        "table_shapes_match_codebooks": (
            tuple(top_table.shape),
            tuple(obs_table.shape),
        )
        == (
            (TOP_N, len(TOP_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "classification": "p39_packed_widen",
        "candidate_construction": "p31 top-32768 rows + one p25 row, packed by sextuple id",
        "p38_branch_floor": obs["p38_branch_floor"],
        "p37_basin_floor": obs["p37_basin_floor"],
        "p36_basin_floor": obs["p36_basin_floor"],
        "p39_basin_min_spread": obs["p39_basin_min_spread"],
        "below_p38_candidate_count": obs["below_p38_candidate_count"],
        "below_p37_candidate_count": obs["below_p37_candidate_count"],
        "below_p36_candidate_count": obs["below_p36_candidate_count"],
        "below_p35_candidate_count": obs["below_p35_candidate_count"],
        "below_p31_candidate_count": obs["below_p31_candidate_count"],
        "support_equal_candidate_count": obs["support_equal_candidate_count"],
        "compound_horizon_margin": obs["compound_horizon_margin"],
        "candidate_count": obs["candidate_count"],
        "raw_extension_count": obs["raw_extension_count"],
        "seed_count": obs["p31_top_seed_count"],
        "seed_worst_spread": obs["p31_top32768_worst_spread"],
        "duplicate_count": obs["duplicate_candidate_count"],
        "multi_source_candidate_count": obs["multi_source_candidate_count"],
        "max_source_multiplicity": obs["max_source_multiplicity"],
        "best_candidates": [witness_row(row) for row in rows["top_rows"][:16]],
        "horizon_reading": (
            "p39 widens the packed screen to p31 top-32768; the 492736 floor "
            "survives and no raw support equalizer appears."
        ),
        "claim_boundary": {
            "p31_top32768_packed_screen": 1,
            "candidate_below_p38_found": obs["below_p38_candidate_count"],
            "candidate_below_p37_found": obs["below_p37_candidate_count"],
            "raw_support_equalizer_found": obs["support_equal_candidate_count"],
            "p26_margin_preserved": obs["p26_margin_preserved_flag"],
            "universal_completion_claim": 0,
        },
        "top_table_sha256": sha_array(top_table),
        "observable_table_sha256": sha_array(obs_table),
    }
    p39 = {
        "schema": "eta6.p39@1",
        "object": "eta6",
        "construction": {
            "source": "p31 top-32768 + p25",
            "test": "p39 packed widen screen",
            "classification": witness["classification"],
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.p39.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_P39_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "p39 checks 4482624 packed sextuples from the p31 top-32768 basin. "
            "Best spread remains 492736; no candidate below p38/p37; no "
            "equalizer; p26 margin strict."
        ),
        "stage_protocol": {
            "draft": "widen p37 with packed sextuple candidates",
            "witness": "deduplicate top-32768 extensions by packed six-id key",
            "coherence": "compare p39 against p38..p25 floors",
            "closure": "certify packed widening without support crossing",
            "emit": "emit p39 artifacts and p40 seam",
        },
        "inputs": {
            "p25_report": input_entry(P25_REPORT, {"status": reports["p25"].get("status")}),
            "p25_tables": input_entry(P25_TABLES),
            "p26_report": input_entry(P26_REPORT, {"status": reports["p26"].get("status")}),
            "p27_report": input_entry(P27_REPORT, {"status": reports["p27"].get("status")}),
            "p28_report": input_entry(P28_REPORT, {"status": reports["p28"].get("status")}),
            "p29_report": input_entry(P29_REPORT, {"status": reports["p29"].get("status")}),
            "p30_report": input_entry(P30_REPORT, {"status": reports["p30"].get("status")}),
            "p31_report": input_entry(P31_REPORT, {"status": reports["p31"].get("status")}),
            "p32_report": input_entry(P32_REPORT, {"status": reports["p32"].get("status")}),
            "p33_report": input_entry(P33_REPORT, {"status": reports["p33"].get("status")}),
            "p34_report": input_entry(P34_REPORT, {"status": reports["p34"].get("status")}),
            "p35_report": input_entry(P35_REPORT, {"status": reports["p35"].get("status")}),
            "p36_report": input_entry(P36_REPORT, {"status": reports["p36"].get("status")}),
            "p37_report": input_entry(P37_REPORT, {"status": reports["p37"].get("status")}),
            "p38_report": input_entry(P38_REPORT, {"status": reports["p38"].get("status")}),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "p39": relpath(OUT_DIR / "p39.json"),
            "top_csv": relpath(OUT_DIR / "top.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "p39 packed screen: 4482624 candidates",
                "p39 raw extension checks: 4554752",
                "no candidate below p38/p37 floor",
                "p39 best spread is 492736",
                "no p39 raw-support equalizer",
                "p26 margin stays positive",
            ],
            "does_not_certify_because_out_of_scope": [
                "complete six-move search over all p25 sextuple compounds",
                "a global six-move support-spread lower bound",
                "new simple-object semantics for the lifted carrier",
                "that eta6 is uncrossable outside the checked row universes",
            ],
        },
        "next_highest_yield_item": (
            "p40: widen packed screen again or derive a stronger seed lower bound."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.p39.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.p39.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "p39": p39,
        "top_csv": p35.csv_text(TOP_COLUMNS, rows["top_rows"]),
        "obs_csv": p35.csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "top_table": top_table,
        "obs_table": obs_table,
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
    write_json(OUT_DIR / "p39.json", payloads["p39"])
    (OUT_DIR / "top.csv").write_text(payloads["top_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        top_table=payloads["top_table"],
        observable_table=payloads["obs_table"],
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
