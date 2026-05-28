from __future__ import annotations

import heapq
import json
from typing import Any

import numpy as np

try:
    from . import derive_eta6_p25 as p25
    from . import derive_eta6_p35 as p35
    from . import derive_eta6_p36 as p36
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
    import derive_eta6_p36 as p36
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "eta6_p37"
STATUS = "ETA6_P37_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

P25_REPORT = p36.P25_REPORT
P25_TABLES = p36.P25_TABLES
P26_REPORT = p36.P26_REPORT
P27_REPORT = p36.P27_REPORT
P28_REPORT = p36.P28_REPORT
P29_REPORT = p36.P29_REPORT
P30_REPORT = p36.P30_REPORT
P31_REPORT = p36.P31_REPORT
P32_REPORT = p36.P32_REPORT
P33_REPORT = p36.P33_REPORT
P34_REPORT = p36.P34_REPORT
P35_REPORT = p36.P35_REPORT
P36_REPORT = p36.OUT_DIR / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_p37.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_p37.py"

TOP_N = 32
SEED_N = 8192
LOW_RANK_CUTOFF = 2048

TOP_COLUMNS = [
    "p37_id" if column == "p36_id" else column
    for column in p36.TOP_COLUMNS
]
TOP_COLUMNS.insert(
    TOP_COLUMNS.index("below_p35_floor_flag"),
    "below_p36_floor_flag",
)

OBS_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBS_NAMES = [
    "p25_extension_count",
    "p31_top_seed_count",
    "p31_top8192_worst_spread",
    "p31_top8192_worst_p31_id",
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
    "p37_basin_min_spread",
    "basin_min_below_p36_flag",
    "basin_min_below_p35_flag",
    "basin_min_below_p34_flag",
    "basin_min_below_p33_flag",
    "basin_min_below_p32_flag",
    "basin_min_below_p31_flag",
    "basin_min_below_p30_flag",
    "basin_min_below_p29_flag",
    "basin_min_below_p28_flag",
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
    "best_p37_id",
    "best_p25_a",
    "best_p25_b",
    "best_p25_c",
    "best_p25_d",
    "best_p25_e",
    "best_p25_f",
    "best_source_count",
    "best_source_min_rank",
    "best_source_max_rank",
    "best_face_a",
    "best_face_b",
    "best_face_c",
    "best_face_d",
    "best_face_e",
    "best_face_f",
    "best_same_face_spread",
    "best_same_face_p37_id",
    "best_same_mask_spread",
    "best_same_mask_p37_id",
    "best_source_rank0_spread",
    "best_source_rank0_p37_id",
    "best_low2048_spread",
    "best_low2048_p37_id",
    "p26_horizon_component_count",
    "p26_checked_positive_row_total",
    "p26_min_component_margin",
    "compound_horizon_margin",
    "compound_horizon_strict_flag",
    "p26_margin_preserved_flag",
    "top_heap_bound",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def row_key(row: dict[str, int]) -> tuple[int, int]:
    return row["joint_support_spread"], row["p37_id"]


def remap_row(
    row: dict[str, int],
    p37_id: int,
    *,
    p36_floor: int,
    p35_floor: int,
    p34_floor: int,
) -> dict[str, int]:
    row = dict(row)
    row["p37_id"] = row.pop("p35_id")
    if row["p37_id"] != p37_id:
        raise ValueError("p37 id remap mismatch")
    spread = row["joint_support_spread"]
    row["below_p36_floor_flag"] = int(spread < p36_floor)
    row["below_p35_floor_flag"] = int(spread < p35_floor)
    row["below_p34_floor_flag"] = int(spread < p34_floor)
    return row


def push_top(
    heap: list[tuple[int, int, int, dict[str, int]]],
    row: dict[str, int],
) -> None:
    item = (
        -row["joint_support_spread"],
        -row["p37_id"],
        row["p37_id"],
        row,
    )
    if len(heap) < TOP_N:
        heapq.heappush(heap, item)
    elif item > heap[0]:
        heapq.heapreplace(heap, item)


def top_rows_from_heap(
    heap: list[tuple[int, int, int, dict[str, int]]],
) -> list[dict[str, int]]:
    rows = [item[3] for item in sorted(heap, key=lambda item: (-item[0], -item[1]))]
    for rank, row in enumerate(rows):
        row["rank"] = rank
    return rows


def witness_row(row: dict[str, int]) -> dict[str, Any]:
    return {
        "rank": row["rank"],
        "p37_id": row["p37_id"],
        "source_count": row["source_count"],
        "source_min_rank": row["source_min_rank"],
        "source_max_rank": row["source_max_rank"],
        "p25_ids": [row[f"p25_{label}"] for label in "abcdef"],
        "faces": [row[f"face_{label}"] for label in "abcdef"],
        "masks": [row[f"mask_{label}"] for label in "abcdef"],
        "support": [row[f"joint_p{index}_support"] for index in range(5)],
        "spread": row["joint_support_spread"],
    }


def load_floors(supports: np.ndarray) -> dict[str, int]:
    return {
        "p25": int((supports.max(axis=1) - supports.min(axis=1)).min()),
        "p27": int(load_json(P27_REPORT)["witness"]["pair_min_spread"]),
        "p28": int(load_json(P28_REPORT)["witness"]["triple_min_spread"]),
        "p29": int(load_json(P29_REPORT)["witness"]["quad_min_spread"]),
        "p30": int(load_json(P30_REPORT)["witness"]["bounded_min_spread"]),
        "p31": int(load_json(P31_REPORT)["witness"]["quint_min_spread"]),
        "p32": int(load_json(P32_REPORT)["witness"]["seeded_six_min_spread"]),
        "p33": int(load_json(P33_REPORT)["witness"]["p33_basin_min_spread"]),
        "p34": int(load_json(P34_REPORT)["witness"]["p34_basin_min_spread"]),
        "p35": int(load_json(P35_REPORT)["witness"]["p35_basin_min_spread"]),
        "p36": int(load_json(P36_REPORT)["witness"]["p36_basin_min_spread"]),
    }


def build_p37_rows() -> dict[str, Any]:
    p25_tables = np.load(P25_TABLES, allow_pickle=False)
    ext_rows = p35.rows_from_table(
        np.asarray(p25_tables["ext_table"], dtype=np.int64),
        p25.EXT_COLUMNS,
    )
    supports = np.asarray([p35.support(row) for row in ext_rows], dtype=np.int64)
    support_by_id = {row["p25_id"]: p35.support(row) for row in ext_rows}
    row_by_id = {row["p25_id"]: row for row in ext_rows}
    floors = load_floors(supports)
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

    candidates: dict[tuple[int, int, int, int, int, int], set[int]] = {}
    raw_extension_count = 0
    for seed in seeds:
        seed_ids = tuple(seed[f"p25_{label}"] for label in "abcde")
        used = set(seed_ids)
        for extension_id in range(len(ext_rows)):
            if extension_id in used:
                continue
            raw_extension_count += 1
            key = tuple(sorted([*seed_ids, extension_id]))
            candidates.setdefault(key, set()).add(seed["rank"])

    counts = {
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
    best_low2048: dict[str, int] | None = None
    top_heap: list[tuple[int, int, int, dict[str, int]]] = []

    for p37_id, (candidate, source_rank_set) in enumerate(sorted(candidates.items())):
        rows = [row_by_id[p25_id] for p25_id in candidate]
        joint = sum(
            (support_by_id[p25_id] for p25_id in candidate),
            np.zeros(5, dtype=np.int64),
        )
        base_row = p35.ranked_row(
            rank=0,
            p35_id=p37_id,
            source_ranks=sorted(source_rank_set),
            rows=rows,
            joint=joint,
            p25_floor=floors["p25"],
            p27_floor=floors["p27"],
            p28_floor=floors["p28"],
            p29_floor=floors["p29"],
            p30_floor=floors["p30"],
            p31_floor=floors["p31"],
            p32_floor=floors["p32"],
            p33_floor=floors["p33"],
        )
        row = remap_row(
            base_row,
            p37_id,
            p36_floor=floors["p36"],
            p35_floor=floors["p35"],
            p34_floor=floors["p34"],
        )
        spread = row["joint_support_spread"]
        for name, floor_key in (
            ("below_p36", "p36"),
            ("below_p35", "p35"),
            ("below_p34", "p34"),
            ("below_p33", "p33"),
            ("below_p32", "p32"),
            ("below_p31", "p31"),
            ("below_p30", "p30"),
            ("below_p29", "p29"),
            ("below_p28", "p28"),
            ("below_p27", "p27"),
            ("below_p25", "p25"),
        ):
            if spread < floors[floor_key]:
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
            best_low2048 is None or row_key(row) < row_key(best_low2048)
        ):
            best_low2048 = row
        push_top(top_heap, row)

    if (
        best_any is None
        or best_same_face is None
        or best_same_mask is None
        or best_source_rank0 is None
        or best_low2048 is None
    ):
        raise ValueError("empty p37 search")
    top_rows = top_rows_from_heap(top_heap)

    p26_report = load_json(P26_REPORT)
    p26_boundary = p26_report["witness"]["claim_boundary"]
    p26_min_margin = min(
        component["margin"] for component in p26_report["witness"]["components"]
    )
    obs = {
        "p25_extension_count": len(ext_rows),
        "p31_top_seed_count": len(seeds),
        "p31_top8192_worst_spread": seeds[-1]["joint_support_spread"],
        "p31_top8192_worst_p31_id": seeds[-1]["p31_id"],
        "raw_extension_count": raw_extension_count,
        "candidate_count": len(candidates),
        "duplicate_candidate_count": raw_extension_count - len(candidates),
        "multi_source_candidate_count": sum(
            1 for ranks in candidates.values() if len(ranks) > 1
        ),
        "max_source_multiplicity": max(len(ranks) for ranks in candidates.values()),
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
        "p37_basin_min_spread": best_any["joint_support_spread"],
        "basin_min_below_p36_flag": int(best_any["joint_support_spread"] < floors["p36"]),
        "basin_min_below_p35_flag": int(best_any["joint_support_spread"] < floors["p35"]),
        "basin_min_below_p34_flag": int(best_any["joint_support_spread"] < floors["p34"]),
        "basin_min_below_p33_flag": int(best_any["joint_support_spread"] < floors["p33"]),
        "basin_min_below_p32_flag": int(best_any["joint_support_spread"] < floors["p32"]),
        "basin_min_below_p31_flag": int(best_any["joint_support_spread"] < floors["p31"]),
        "basin_min_below_p30_flag": int(best_any["joint_support_spread"] < floors["p30"]),
        "basin_min_below_p29_flag": int(best_any["joint_support_spread"] < floors["p29"]),
        "basin_min_below_p28_flag": int(best_any["joint_support_spread"] < floors["p28"]),
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
        "best_p37_id": best_any["p37_id"],
        "best_p25_a": best_any["p25_a"],
        "best_p25_b": best_any["p25_b"],
        "best_p25_c": best_any["p25_c"],
        "best_p25_d": best_any["p25_d"],
        "best_p25_e": best_any["p25_e"],
        "best_p25_f": best_any["p25_f"],
        "best_source_count": best_any["source_count"],
        "best_source_min_rank": best_any["source_min_rank"],
        "best_source_max_rank": best_any["source_max_rank"],
        "best_face_a": best_any["face_a"],
        "best_face_b": best_any["face_b"],
        "best_face_c": best_any["face_c"],
        "best_face_d": best_any["face_d"],
        "best_face_e": best_any["face_e"],
        "best_face_f": best_any["face_f"],
        "best_same_face_spread": best_same_face["joint_support_spread"],
        "best_same_face_p37_id": best_same_face["p37_id"],
        "best_same_mask_spread": best_same_mask["joint_support_spread"],
        "best_same_mask_p37_id": best_same_mask["p37_id"],
        "best_source_rank0_spread": best_source_rank0["joint_support_spread"],
        "best_source_rank0_p37_id": best_source_rank0["p37_id"],
        "best_low2048_spread": best_low2048["joint_support_spread"],
        "best_low2048_p37_id": best_low2048["p37_id"],
        "p26_horizon_component_count": p26_boundary["checked_component_count"],
        "p26_checked_positive_row_total": p26_boundary["checked_positive_row_total"],
        "p26_min_component_margin": p26_min_margin,
        "compound_horizon_margin": min(p26_min_margin, best_any["joint_support_spread"]),
        "compound_horizon_strict_flag": int(p26_min_margin > 0),
        "p26_margin_preserved_flag": int(
            p26_boundary["support_equalizer_absent"] == 1
            and p26_boundary["universal_completion_claim"] == 0
        ),
        "top_heap_bound": TOP_N,
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
    }


def build_payloads() -> dict[str, Any]:
    rows = build_p37_rows()
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
    }
    checks = {
        "input_certificates_available": all(
            report.get("all_checks_pass") is True for report in reports.values()
        ),
        "basin_size_matches": (
            obs["p25_extension_count"],
            obs["p31_top_seed_count"],
            obs["p31_top8192_worst_spread"],
            obs["p31_top8192_worst_p31_id"],
            obs["raw_extension_count"],
            obs["candidate_count"],
            obs["duplicate_candidate_count"],
            obs["multi_source_candidate_count"],
            obs["max_source_multiplicity"],
        )
        == (144, 8192, 13_824_512, 291_297_468, 1_138_688, 1_130_631, 8_057, 7_651, 4),
        "basin_improves_checked_floors": (
            obs["p36_basin_floor"],
            obs["p35_basin_floor"],
            obs["p31_quint_floor"],
            obs["p37_basin_min_spread"],
            obs["basin_min_below_p36_flag"],
            obs["basin_min_below_p35_flag"],
            obs["basin_min_below_p31_flag"],
            obs["basin_min_below_p28_flag"],
        )
        == (1_667_584, 4_589_696, 1_815_040, 492_736, 1, 1, 1, 1),
        "descent_counts_match": (
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
        == (13, 460, 1_846, 3_237, 2_652, 18, 359, 53, 63, 8_223, 10_083, 0),
        "best_candidate_matches_expected": (
            obs["best_p37_id"],
            obs["best_p25_a"],
            obs["best_p25_b"],
            obs["best_p25_c"],
            obs["best_p25_d"],
            obs["best_p25_e"],
            obs["best_p25_f"],
            obs["best_source_count"],
            obs["best_source_min_rank"],
            obs["best_source_max_rank"],
            obs["best_face_a"],
            obs["best_face_b"],
            obs["best_face_c"],
            obs["best_face_d"],
            obs["best_face_e"],
            obs["best_face_f"],
        )
        == (142_070, 1, 47, 57, 79, 110, 128, 2, 4_756, 4_757, 12, 12, 22, 22, 26, 26),
        "best_same_face_and_mask_match": (
            obs["best_same_face_spread"],
            obs["best_same_face_p37_id"],
            obs["best_same_mask_spread"],
            obs["best_same_mask_p37_id"],
        )
        == (2_644_672, 458_516, 2_644_672, 458_516),
        "source_controls_match": (
            obs["best_source_rank0_spread"],
            obs["best_source_rank0_p37_id"],
            obs["best_low2048_spread"],
            obs["best_low2048_p37_id"],
        )
        == (10_529_536, 102_342, 1_667_584, 113_357),
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
        "classification": "p37_descent",
        "candidate_construction": "p31 top-8192 rows + one p25 row",
        "p36_basin_floor": obs["p36_basin_floor"],
        "p35_basin_floor": obs["p35_basin_floor"],
        "p34_basin_floor": obs["p34_basin_floor"],
        "p33_basin_floor": obs["p33_basin_floor"],
        "p32_seeded_floor": obs["p32_seeded_floor"],
        "p31_quint_floor": obs["p31_quint_floor"],
        "p30_bounded_floor": obs["p30_bounded_floor"],
        "p29_quad_floor": obs["p29_quad_floor"],
        "p28_triple_floor": obs["p28_triple_floor"],
        "p37_basin_min_spread": obs["p37_basin_min_spread"],
        "below_p36_candidate_count": obs["below_p36_candidate_count"],
        "below_p35_candidate_count": obs["below_p35_candidate_count"],
        "below_p34_candidate_count": obs["below_p34_candidate_count"],
        "below_p33_candidate_count": obs["below_p33_candidate_count"],
        "below_p32_candidate_count": obs["below_p32_candidate_count"],
        "below_p31_candidate_count": obs["below_p31_candidate_count"],
        "below_p30_candidate_count": obs["below_p30_candidate_count"],
        "below_p29_candidate_count": obs["below_p29_candidate_count"],
        "below_p28_candidate_count": obs["below_p28_candidate_count"],
        "below_p27_candidate_count": obs["below_p27_candidate_count"],
        "below_p25_candidate_count": obs["below_p25_candidate_count"],
        "support_equal_candidate_count": obs["support_equal_candidate_count"],
        "compound_horizon_margin": obs["compound_horizon_margin"],
        "candidate_count": obs["candidate_count"],
        "seed_count": obs["p31_top_seed_count"],
        "seed_worst_spread": obs["p31_top8192_worst_spread"],
        "duplicate_count": obs["duplicate_candidate_count"],
        "best_candidates": [witness_row(row) for row in rows["top_rows"][:16]],
        "horizon_reading": (
            "p37 lowers the checked six-move basin floor to 492736, but still "
            "does not equalize support."
        ),
        "claim_boundary": {
            "p31_top8192_basin_screen": 1,
            "raw_support_equalizer_found": obs["support_equal_candidate_count"],
            "p26_margin_preserved": obs["p26_margin_preserved_flag"],
            "universal_completion_claim": 0,
        },
        "top_table_sha256": sha_array(top_table),
        "observable_table_sha256": sha_array(obs_table),
    }
    p37 = {
        "schema": "eta6.p37@1",
        "object": "eta6",
        "construction": {
            "source": "p31 top-8192 + p25",
            "test": "p37 basin screen",
            "classification": witness["classification"],
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.p37.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_P37_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "p37 checks 1130631 sextuples from the p31 top-8192 basin. Best "
            "spread 492736 beats p36; no equalizer; p26 margin strict."
        ),
        "stage_protocol": {
            "draft": "rescan complete p31 top-8192 and p26 margin",
            "witness": "extend each p31 top-8192 row by one p25 row",
            "coherence": "compare p37 against p36..p25 floors",
            "closure": "certify p37 basin descent without support crossing",
            "emit": "emit p37 artifacts and p38 seam",
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
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "p37": relpath(OUT_DIR / "p37.json"),
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
                "p37 screen: 1130631 candidates",
                "p37 beats p36",
                "p37 best spread is 492736",
                "no p37 raw-support equalizer",
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
            "p38: branch-bound p37 basin before widening again."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.p37.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.p37.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "p37": p37,
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
    write_json(OUT_DIR / "p37.json", payloads["p37"])
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
