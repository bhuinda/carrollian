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
    from . import derive_eta6_p39 as p39
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
    import derive_eta6_p39 as p39
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "eta6_p40"
STATUS = "ETA6_P40_CERTIFIED"
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
P39_REPORT = p39.OUT_DIR / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_p40.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_p40.py"

TOP_N = 32
SEED_N = 131_072

BRANCH_COLUMNS = [
    "rank",
    "seed_rank",
    "p31_id",
    "seed_spread",
    "ext_p25_id",
    "p25_a",
    "p25_b",
    "p25_c",
    "p25_d",
    "p25_e",
    "p25_f",
    "face_a",
    "face_b",
    "face_c",
    "face_d",
    "face_e",
    "face_f",
    "branch_p0_support",
    "branch_p1_support",
    "branch_p2_support",
    "branch_p3_support",
    "branch_p4_support",
    "branch_support_min",
    "branch_support_max",
    "branch_min_spread",
    "below_p39_floor_flag",
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
]
OBS_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBS_NAMES = [
    "p25_extension_count",
    "p31_top_seed_count",
    "p31_top131072_worst_spread",
    "p31_top131072_worst_p31_id",
    "raw_extension_count",
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
    "p39_basin_floor",
    "branch_min_floor",
    "branch_min_below_p39_count",
    "branch_min_equal_p39_count",
    "branch_min_below_p38_count",
    "branch_min_below_p37_count",
    "branch_support_equal_count",
    "branch_min_below_p36_count",
    "branch_min_below_p35_count",
    "branch_min_below_p34_count",
    "branch_min_below_p33_count",
    "branch_min_below_p32_count",
    "branch_min_below_p31_count",
    "branch_min_below_p30_count",
    "branch_min_below_p29_count",
    "branch_min_below_p28_count",
    "branch_min_below_p27_count",
    "branch_min_below_p25_count",
    "branch_min_max",
    "branch_min_sum",
    "best_seed_rank",
    "best_p31_id",
    "best_ext_p25_id",
    "best_seed_spread",
    "p26_horizon_component_count",
    "p26_checked_positive_row_total",
    "p26_min_component_margin",
    "compound_horizon_margin",
    "compound_horizon_strict_flag",
    "p26_margin_preserved_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def branch_key(row: dict[str, int]) -> tuple[int, int, int]:
    return row["branch_min_spread"], row["seed_rank"], row["ext_p25_id"]


def push_top(
    heap: list[tuple[int, int, int, dict[str, int]]],
    row: dict[str, int],
) -> None:
    item = (
        -row["branch_min_spread"],
        -row["seed_rank"],
        -row["ext_p25_id"],
        row,
    )
    if len(heap) < TOP_N:
        heapq.heappush(heap, item)
    elif item > heap[0]:
        heapq.heapreplace(heap, item)


def top_rows_from_heap(
    heap: list[tuple[int, int, int, dict[str, int]]],
) -> list[dict[str, int]]:
    rows = [item[3] for item in sorted(heap, key=lambda item: (-item[0], -item[1], -item[2]))]
    for rank, row in enumerate(rows):
        row["rank"] = rank
    return rows


def branch_row(
    *,
    rank: int,
    seed: dict[str, int],
    ext_row: dict[str, int],
    joint: np.ndarray,
    floors: dict[str, int],
    p37_floor: int,
    p38_floor: int,
    p39_floor: int,
) -> dict[str, int]:
    seed_ids = [seed[f"p25_{label}"] for label in "abcde"]
    spread = int(joint.max() - joint.min())
    faces = [seed[f"face_{label}"] for label in "abcde"] + [ext_row["face_id"]]
    return {
        "rank": rank,
        "seed_rank": seed["rank"],
        "p31_id": seed["p31_id"],
        "seed_spread": seed["joint_support_spread"],
        "ext_p25_id": ext_row["p25_id"],
        "p25_a": seed_ids[0],
        "p25_b": seed_ids[1],
        "p25_c": seed_ids[2],
        "p25_d": seed_ids[3],
        "p25_e": seed_ids[4],
        "p25_f": ext_row["p25_id"],
        "face_a": faces[0],
        "face_b": faces[1],
        "face_c": faces[2],
        "face_d": faces[3],
        "face_e": faces[4],
        "face_f": faces[5],
        "branch_p0_support": int(joint[0]),
        "branch_p1_support": int(joint[1]),
        "branch_p2_support": int(joint[2]),
        "branch_p3_support": int(joint[3]),
        "branch_p4_support": int(joint[4]),
        "branch_support_min": int(joint.min()),
        "branch_support_max": int(joint.max()),
        "branch_min_spread": spread,
        "below_p39_floor_flag": int(spread < p39_floor),
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
    }


def witness_row(row: dict[str, int]) -> dict[str, Any]:
    return {
        "rank": row["rank"],
        "seed_rank": row["seed_rank"],
        "p31_id": row["p31_id"],
        "seed_spread": row["seed_spread"],
        "ext_p25_id": row["ext_p25_id"],
        "p25_ids": [row[f"p25_{label}"] for label in "abcdef"],
        "faces": [row[f"face_{label}"] for label in "abcdef"],
        "support": [row[f"branch_p{index}_support"] for index in range(5)],
        "spread": row["branch_min_spread"],
    }


def build_p40_rows() -> dict[str, Any]:
    p25_tables = np.load(P25_TABLES, allow_pickle=False)
    ext_rows = p35.rows_from_table(
        np.asarray(p25_tables["ext_table"], dtype=np.int64),
        p25.EXT_COLUMNS,
    )
    supports = np.asarray([p35.support(row) for row in ext_rows], dtype=np.int64)
    floors = p37.load_floors(supports)
    p37_report = load_json(P37_REPORT)
    p38_report = load_json(P38_REPORT)
    p39_report = load_json(P39_REPORT)
    p37_floor = int(p37_report["witness"]["p37_basin_min_spread"])
    p38_floor = int(p38_report["witness"]["branch_min_floor"])
    p39_floor = int(p39_report["witness"]["p39_basin_min_spread"])
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

    counts = {
        "below_p39": 0,
        "equal_p39": 0,
        "below_p38": 0,
        "below_p37": 0,
        "equal_zero": 0,
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
    }
    raw_extension_count = 0
    branch_min_sum = 0
    branch_min_max = 0
    top_heap: list[tuple[int, int, int, dict[str, int]]] = []
    best: dict[str, int] | None = None
    max_int = np.iinfo(np.int64).max

    for seed in seeds:
        seed_ids = np.asarray([seed[f"p25_{label}"] for label in "abcde"], dtype=np.int64)
        seed_joint = supports[seed_ids].sum(axis=0)
        joint_table = supports + seed_joint
        spreads = joint_table.max(axis=1) - joint_table.min(axis=1)
        spreads[seed_ids] = max_int
        ext_id = int(np.argmin(spreads))
        raw_extension_count += len(ext_rows) - len(seed_ids)
        row = branch_row(
            rank=0,
            seed=seed,
            ext_row=ext_rows[ext_id],
            joint=joint_table[ext_id],
            floors=floors,
            p37_floor=p37_floor,
            p38_floor=p38_floor,
            p39_floor=p39_floor,
        )
        spread = row["branch_min_spread"]
        branch_min_sum += spread
        branch_min_max = max(branch_min_max, spread)
        if spread < p39_floor:
            counts["below_p39"] += 1
        if spread == p39_floor:
            counts["equal_p39"] += 1
        if spread < p38_floor:
            counts["below_p38"] += 1
        if spread < p37_floor:
            counts["below_p37"] += 1
        if spread == 0:
            counts["equal_zero"] += 1
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
        if best is None or branch_key(row) < branch_key(best):
            best = row
        push_top(top_heap, row)

    if best is None:
        raise ValueError("empty p40 search")
    top_rows = top_rows_from_heap(top_heap)
    p26_report = load_json(P26_REPORT)
    p26_boundary = p26_report["witness"]["claim_boundary"]
    p26_min_margin = min(
        component["margin"] for component in p26_report["witness"]["components"]
    )
    obs = {
        "p25_extension_count": len(ext_rows),
        "p31_top_seed_count": len(seeds),
        "p31_top131072_worst_spread": seeds[-1]["joint_support_spread"],
        "p31_top131072_worst_p31_id": seeds[-1]["p31_id"],
        "raw_extension_count": raw_extension_count,
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
        "p39_basin_floor": p39_floor,
        "branch_min_floor": best["branch_min_spread"],
        "branch_min_below_p39_count": counts["below_p39"],
        "branch_min_equal_p39_count": counts["equal_p39"],
        "branch_min_below_p38_count": counts["below_p38"],
        "branch_min_below_p37_count": counts["below_p37"],
        "branch_support_equal_count": counts["equal_zero"],
        "branch_min_below_p36_count": counts["below_p36"],
        "branch_min_below_p35_count": counts["below_p35"],
        "branch_min_below_p34_count": counts["below_p34"],
        "branch_min_below_p33_count": counts["below_p33"],
        "branch_min_below_p32_count": counts["below_p32"],
        "branch_min_below_p31_count": counts["below_p31"],
        "branch_min_below_p30_count": counts["below_p30"],
        "branch_min_below_p29_count": counts["below_p29"],
        "branch_min_below_p28_count": counts["below_p28"],
        "branch_min_below_p27_count": counts["below_p27"],
        "branch_min_below_p25_count": counts["below_p25"],
        "branch_min_max": branch_min_max,
        "branch_min_sum": branch_min_sum,
        "best_seed_rank": best["seed_rank"],
        "best_p31_id": best["p31_id"],
        "best_ext_p25_id": best["ext_p25_id"],
        "best_seed_spread": best["seed_spread"],
        "p26_horizon_component_count": p26_boundary["checked_component_count"],
        "p26_checked_positive_row_total": p26_boundary["checked_positive_row_total"],
        "p26_min_component_margin": p26_min_margin,
        "compound_horizon_margin": min(p26_min_margin, best["branch_min_spread"]),
        "compound_horizon_strict_flag": int(p26_min_margin > 0),
        "p26_margin_preserved_flag": int(
            p26_boundary["support_equalizer_absent"] == 1
            and p26_boundary["universal_completion_claim"] == 0
        ),
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
        "p39_report": p39_report,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_p40_rows()
    branch_table = p35.table_from_rows(BRANCH_COLUMNS, rows["top_rows"])
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
        "p39": rows["p39_report"],
    }
    checks = {
        "input_certificates_available": all(
            report.get("all_checks_pass") is True for report in reports.values()
        ),
        "branch_env_size_matches": (
            obs["p25_extension_count"],
            obs["p31_top_seed_count"],
            obs["p31_top131072_worst_spread"],
            obs["p31_top131072_worst_p31_id"],
            obs["raw_extension_count"],
        )
        == (144, 131_072, 28_075_840, 308_298_973, 18_219_008),
        "branch_floor_stable": (
            obs["p39_basin_floor"],
            obs["p38_branch_floor"],
            obs["p37_basin_floor"],
            obs["branch_min_floor"],
            obs["branch_min_below_p39_count"],
            obs["branch_min_equal_p39_count"],
            obs["branch_min_below_p38_count"],
            obs["branch_min_below_p37_count"],
            obs["branch_support_equal_count"],
        )
        == (492_736, 492_736, 492_736, 492_736, 0, 2, 0, 0, 0),
        "branch_counts_match": (
            obs["branch_min_below_p36_count"],
            obs["branch_min_below_p35_count"],
            obs["branch_min_below_p34_count"],
            obs["branch_min_below_p33_count"],
            obs["branch_min_below_p32_count"],
            obs["branch_min_below_p31_count"],
            obs["branch_min_below_p30_count"],
            obs["branch_min_below_p29_count"],
            obs["branch_min_below_p28_count"],
            obs["branch_min_below_p27_count"],
            obs["branch_min_below_p25_count"],
        )
        == (26, 1_046, 4_674, 8_050, 6_652, 40, 792, 118, 140, 20_354, 24_720),
        "branch_stats_match": (
            obs["branch_min_max"],
            obs["branch_min_sum"],
            obs["best_seed_rank"],
            obs["best_p31_id"],
            obs["best_ext_p25_id"],
            obs["best_seed_spread"],
        )
        == (33_327_776, 2_100_868_571_648, 4_756, 29_509_840, 128, 12_025_920),
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
            tuple(branch_table.shape),
            tuple(obs_table.shape),
        )
        == (
            (TOP_N, len(BRANCH_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "classification": "p40_branch_env",
        "candidate_construction": "p31 top-131072 seed branches + exact best p25 extension",
        "p39_basin_floor": obs["p39_basin_floor"],
        "p38_branch_floor": obs["p38_branch_floor"],
        "p37_basin_floor": obs["p37_basin_floor"],
        "branch_min_floor": obs["branch_min_floor"],
        "branch_min_below_p39_count": obs["branch_min_below_p39_count"],
        "branch_min_equal_p39_count": obs["branch_min_equal_p39_count"],
        "branch_min_below_p38_count": obs["branch_min_below_p38_count"],
        "branch_min_below_p37_count": obs["branch_min_below_p37_count"],
        "branch_support_equal_count": obs["branch_support_equal_count"],
        "branch_min_below_p36_count": obs["branch_min_below_p36_count"],
        "branch_min_below_p35_count": obs["branch_min_below_p35_count"],
        "branch_min_below_p31_count": obs["branch_min_below_p31_count"],
        "branch_min_max": obs["branch_min_max"],
        "branch_min_average_num": obs["branch_min_sum"],
        "branch_min_average_den": obs["p31_top_seed_count"],
        "compound_horizon_margin": obs["compound_horizon_margin"],
        "seed_count": obs["p31_top_seed_count"],
        "raw_extension_count": obs["raw_extension_count"],
        "seed_worst_spread": obs["p31_top131072_worst_spread"],
        "best_branches": [witness_row(row) for row in rows["top_rows"][:16]],
        "horizon_reading": (
            "p40 widens the branch envelope to p31 top-131072; the 492736 "
            "floor survives and no raw support equalizer appears."
        ),
        "claim_boundary": {
            "p31_top131072_branch_env": 1,
            "branch_below_p39_found": obs["branch_min_below_p39_count"],
            "branch_below_p38_found": obs["branch_min_below_p38_count"],
            "branch_below_p37_found": obs["branch_min_below_p37_count"],
            "raw_support_equalizer_found": obs["branch_support_equal_count"],
            "p26_margin_preserved": obs["p26_margin_preserved_flag"],
            "universal_completion_claim": 0,
        },
        "branch_table_sha256": sha_array(branch_table),
        "observable_table_sha256": sha_array(obs_table),
    }
    p40 = {
        "schema": "eta6.p40@1",
        "object": "eta6",
        "construction": {
            "source": "p31 top-131072 + p25",
            "test": "p40 branch envelope",
            "classification": witness["classification"],
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.p40.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_P40_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "p40 checks the exact best extension of each p31 top-131072 seed "
            "branch over 18219008 raw extensions. Branch floor stays 492736; "
            "no branch below p39/p38/p37; no equalizer; p26 margin strict."
        ),
        "stage_protocol": {
            "draft": "widen the branch envelope",
            "witness": "take exact best p25 extension per seed",
            "coherence": "compare branch minima against p39..p25 floors",
            "closure": "certify the widened branch envelope without support crossing",
            "emit": "emit p40 artifacts and p41 seam",
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
            "p39_report": input_entry(P39_REPORT, {"status": reports["p39"].get("status")}),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "p40": relpath(OUT_DIR / "p40.json"),
            "branch_csv": relpath(OUT_DIR / "branch.csv"),
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
                "p40 branch screen: 131072 seed branches",
                "p40 raw extension checks: 18219008",
                "no branch below p39/p38/p37 floor",
                "p40 branch floor is 492736",
                "no p40 raw-support equalizer",
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
            "p41: packed top-65536 screen or branch top-262144."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.p40.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.p40.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "p40": p40,
        "branch_csv": p35.csv_text(BRANCH_COLUMNS, rows["top_rows"]),
        "obs_csv": p35.csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "branch_table": branch_table,
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
    write_json(OUT_DIR / "p40.json", payloads["p40"])
    (OUT_DIR / "branch.csv").write_text(payloads["branch_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        branch_table=payloads["branch_table"],
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
