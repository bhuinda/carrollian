from __future__ import annotations

import json
from typing import Any

import numpy as np

try:
    from . import derive_eta6_p25 as p25
    from . import derive_eta6_p26 as p26
    from . import derive_eta6_p27 as p27
    from . import derive_eta6_p28 as p28
    from . import derive_eta6_p29 as p29
    from . import derive_eta6_p30 as p30
    from . import derive_eta6_p31 as p31
    from . import derive_eta6_p32 as p32
    from . import derive_eta6_p33 as p33
    from . import derive_eta6_p34 as p34
    from . import derive_eta6_p35 as p35
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
    import derive_eta6_p26 as p26
    import derive_eta6_p27 as p27
    import derive_eta6_p28 as p28
    import derive_eta6_p29 as p29
    import derive_eta6_p30 as p30
    import derive_eta6_p31 as p31
    import derive_eta6_p32 as p32
    import derive_eta6_p33 as p33
    import derive_eta6_p34 as p34
    import derive_eta6_p35 as p35
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "eta6_p36"
STATUS = "ETA6_P36_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

P25_REPORT = p25.OUT_DIR / "report.json"
P25_TABLES = p25.OUT_DIR / "tables.npz"
P26_REPORT = p26.OUT_DIR / "report.json"
P27_REPORT = p27.OUT_DIR / "report.json"
P28_REPORT = p28.OUT_DIR / "report.json"
P29_REPORT = p29.OUT_DIR / "report.json"
P30_REPORT = p30.OUT_DIR / "report.json"
P31_REPORT = p31.OUT_DIR / "report.json"
P32_REPORT = p32.OUT_DIR / "report.json"
P33_REPORT = p33.OUT_DIR / "report.json"
P34_REPORT = p34.OUT_DIR / "report.json"
P35_REPORT = p35.OUT_DIR / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_p36.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_p36.py"

TOP_N = 32
SEED_N = 2048
LOW_RANK_CUTOFF = 512
TOP_COLUMNS = [
    "rank",
    "p36_id",
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
OBS_CODES = {
    "p25_extension_count": 0,
    "p31_top_seed_count": 1,
    "p31_top2048_worst_spread": 2,
    "p31_top2048_worst_p31_id": 3,
    "raw_extension_count": 4,
    "candidate_count": 5,
    "duplicate_candidate_count": 6,
    "multi_source_candidate_count": 7,
    "max_source_multiplicity": 8,
    "p25_single_floor": 9,
    "p27_pair_floor": 10,
    "p28_triple_floor": 11,
    "p29_quad_floor": 12,
    "p30_bounded_floor": 13,
    "p31_quint_floor": 14,
    "p32_seeded_floor": 15,
    "p33_basin_floor": 16,
    "p34_basin_floor": 17,
    "p35_basin_floor": 18,
    "p36_basin_min_spread": 19,
    "basin_min_below_p35_flag": 20,
    "basin_min_below_p34_flag": 21,
    "basin_min_below_p33_flag": 22,
    "basin_min_below_p32_flag": 23,
    "basin_min_below_p31_flag": 24,
    "basin_min_below_p30_flag": 25,
    "basin_min_below_p29_flag": 26,
    "basin_min_below_p28_flag": 27,
    "below_p35_candidate_count": 28,
    "below_p34_candidate_count": 29,
    "below_p33_candidate_count": 30,
    "below_p32_candidate_count": 31,
    "below_p31_candidate_count": 32,
    "below_p30_candidate_count": 33,
    "below_p29_candidate_count": 34,
    "below_p28_candidate_count": 35,
    "below_p27_candidate_count": 36,
    "below_p25_candidate_count": 37,
    "support_equal_candidate_count": 38,
    "best_p36_id": 39,
    "best_p25_a": 40,
    "best_p25_b": 41,
    "best_p25_c": 42,
    "best_p25_d": 43,
    "best_p25_e": 44,
    "best_p25_f": 45,
    "best_source_count": 46,
    "best_source_min_rank": 47,
    "best_source_max_rank": 48,
    "best_face_a": 49,
    "best_face_b": 50,
    "best_face_c": 51,
    "best_face_d": 52,
    "best_face_e": 53,
    "best_face_f": 54,
    "best_same_face_spread": 55,
    "best_same_face_p36_id": 56,
    "best_same_mask_spread": 57,
    "best_same_mask_p36_id": 58,
    "best_source_rank0_spread": 59,
    "best_source_rank0_p36_id": 60,
    "best_low512_spread": 61,
    "best_low512_p36_id": 62,
    "p26_horizon_component_count": 63,
    "p26_checked_positive_row_total": 64,
    "p26_min_component_margin": 65,
    "compound_horizon_margin": 66,
    "compound_horizon_strict_flag": 67,
    "p26_margin_preserved_flag": 68,
}


def remap_row(row: dict[str, int], p36_id: int, p35_floor: int, p34_floor: int) -> dict[str, int]:
    row = dict(row)
    row["p36_id"] = row.pop("p35_id")
    spread = row["joint_support_spread"]
    row["below_p35_floor_flag"] = int(spread < p35_floor)
    row["below_p34_floor_flag"] = int(spread < p34_floor)
    if row["p36_id"] != p36_id:
        raise ValueError("p36 id remap mismatch")
    return row


def build_p36_rows() -> dict[str, Any]:
    p25_tables = np.load(P25_TABLES, allow_pickle=False)
    ext_rows = p35.rows_from_table(
        np.asarray(p25_tables["ext_table"], dtype=np.int64),
        p25.EXT_COLUMNS,
    )
    supports = np.asarray([p35.support(row) for row in ext_rows], dtype=np.int64)
    support_by_id = {row["p25_id"]: p35.support(row) for row in ext_rows}
    row_by_id = {row["p25_id"]: row for row in ext_rows}
    p25_floor = int((supports.max(axis=1) - supports.min(axis=1)).min())
    p27_floor = int(load_json(P27_REPORT)["witness"]["pair_min_spread"])
    p28_floor = int(load_json(P28_REPORT)["witness"]["triple_min_spread"])
    p29_floor = int(load_json(P29_REPORT)["witness"]["quad_min_spread"])
    p30_floor = int(load_json(P30_REPORT)["witness"]["bounded_min_spread"])
    p31_floor = int(load_json(P31_REPORT)["witness"]["quint_min_spread"])
    p32_floor = int(load_json(P32_REPORT)["witness"]["seeded_six_min_spread"])
    p33_floor = int(load_json(P33_REPORT)["witness"]["p33_basin_min_spread"])
    p34_floor = int(load_json(P34_REPORT)["witness"]["p34_basin_min_spread"])
    p35_floor = int(load_json(P35_REPORT)["witness"]["p35_basin_min_spread"])
    seeds = p35.top_p31_rows(
        ext_rows,
        supports,
        seed_count=SEED_N,
        p25_floor=p25_floor,
        p27_floor=p27_floor,
        p28_floor=p28_floor,
        p29_floor=p29_floor,
        p30_floor=p30_floor,
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

    best_rows: list[dict[str, int]] = []
    best_any: dict[str, int] | None = None
    best_same_face: dict[str, int] | None = None
    best_same_mask: dict[str, int] | None = None
    best_source_rank0: dict[str, int] | None = None
    best_low512: dict[str, int] | None = None
    below_p35 = 0
    below_p34 = 0
    below_p33 = 0
    below_p32 = 0
    below_p31 = 0
    below_p30 = 0
    below_p29 = 0
    below_p28 = 0
    below_p27 = 0
    below_p25 = 0
    equal = 0

    for p36_id, (candidate, source_rank_set) in enumerate(sorted(candidates.items())):
        rows = [row_by_id[p25_id] for p25_id in candidate]
        joint = sum(
            (support_by_id[p25_id] for p25_id in candidate),
            np.zeros(5, dtype=np.int64),
        )
        base_row = p35.ranked_row(
            rank=0,
            p35_id=p36_id,
            source_ranks=sorted(source_rank_set),
            rows=rows,
            joint=joint,
            p25_floor=p25_floor,
            p27_floor=p27_floor,
            p28_floor=p28_floor,
            p29_floor=p29_floor,
            p30_floor=p30_floor,
            p31_floor=p31_floor,
            p32_floor=p32_floor,
            p33_floor=p33_floor,
        )
        row = remap_row(base_row, p36_id, p35_floor, p34_floor)
        spread = row["joint_support_spread"]
        if spread < p35_floor:
            below_p35 += 1
        if spread < p34_floor:
            below_p34 += 1
        if spread < p33_floor:
            below_p33 += 1
        if spread < p32_floor:
            below_p32 += 1
        if spread < p31_floor:
            below_p31 += 1
        if spread < p30_floor:
            below_p30 += 1
        if spread < p29_floor:
            below_p29 += 1
        if spread < p28_floor:
            below_p28 += 1
        if spread < p27_floor:
            below_p27 += 1
        if spread < p25_floor:
            below_p25 += 1
        if spread == 0:
            equal += 1
        key = (spread, p36_id)
        if best_any is None or key < (
            best_any["joint_support_spread"],
            best_any["p36_id"],
        ):
            best_any = row
        if row["same_face_flag"] == 1 and (
            best_same_face is None
            or key
            < (
                best_same_face["joint_support_spread"],
                best_same_face["p36_id"],
            )
        ):
            best_same_face = row
        if row["same_mask_flag"] == 1 and (
            best_same_mask is None
            or key
            < (
                best_same_mask["joint_support_spread"],
                best_same_mask["p36_id"],
            )
        ):
            best_same_mask = row
        if row["source_min_rank"] == 0 and (
            best_source_rank0 is None
            or key
            < (
                best_source_rank0["joint_support_spread"],
                best_source_rank0["p36_id"],
            )
        ):
            best_source_rank0 = row
        if row["source_min_rank"] < LOW_RANK_CUTOFF and (
            best_low512 is None
            or key
            < (
                best_low512["joint_support_spread"],
                best_low512["p36_id"],
            )
        ):
            best_low512 = row
        best_rows.append(row)

    if (
        best_any is None
        or best_same_face is None
        or best_same_mask is None
        or best_source_rank0 is None
        or best_low512 is None
    ):
        raise ValueError("empty p36 search")
    best_rows = sorted(
        best_rows,
        key=lambda value: (value["joint_support_spread"], value["p36_id"]),
    )[:TOP_N]
    for rank, row in enumerate(best_rows):
        row["rank"] = rank

    p26_report = load_json(P26_REPORT)
    p26_boundary = p26_report["witness"]["claim_boundary"]
    p26_min_margin = min(
        component["margin"] for component in p26_report["witness"]["components"]
    )
    obs = {
        "p25_extension_count": len(ext_rows),
        "p31_top_seed_count": len(seeds),
        "p31_top2048_worst_spread": seeds[-1]["joint_support_spread"],
        "p31_top2048_worst_p31_id": seeds[-1]["p31_id"],
        "raw_extension_count": raw_extension_count,
        "candidate_count": len(candidates),
        "duplicate_candidate_count": raw_extension_count - len(candidates),
        "multi_source_candidate_count": sum(
            1 for ranks in candidates.values() if len(ranks) > 1
        ),
        "max_source_multiplicity": max(len(ranks) for ranks in candidates.values()),
        "p25_single_floor": p25_floor,
        "p27_pair_floor": p27_floor,
        "p28_triple_floor": p28_floor,
        "p29_quad_floor": p29_floor,
        "p30_bounded_floor": p30_floor,
        "p31_quint_floor": p31_floor,
        "p32_seeded_floor": p32_floor,
        "p33_basin_floor": p33_floor,
        "p34_basin_floor": p34_floor,
        "p35_basin_floor": p35_floor,
        "p36_basin_min_spread": best_any["joint_support_spread"],
        "basin_min_below_p35_flag": int(best_any["joint_support_spread"] < p35_floor),
        "basin_min_below_p34_flag": int(best_any["joint_support_spread"] < p34_floor),
        "basin_min_below_p33_flag": int(best_any["joint_support_spread"] < p33_floor),
        "basin_min_below_p32_flag": int(best_any["joint_support_spread"] < p32_floor),
        "basin_min_below_p31_flag": int(best_any["joint_support_spread"] < p31_floor),
        "basin_min_below_p30_flag": int(best_any["joint_support_spread"] < p30_floor),
        "basin_min_below_p29_flag": int(best_any["joint_support_spread"] < p29_floor),
        "basin_min_below_p28_flag": int(best_any["joint_support_spread"] < p28_floor),
        "below_p35_candidate_count": below_p35,
        "below_p34_candidate_count": below_p34,
        "below_p33_candidate_count": below_p33,
        "below_p32_candidate_count": below_p32,
        "below_p31_candidate_count": below_p31,
        "below_p30_candidate_count": below_p30,
        "below_p29_candidate_count": below_p29,
        "below_p28_candidate_count": below_p28,
        "below_p27_candidate_count": below_p27,
        "below_p25_candidate_count": below_p25,
        "support_equal_candidate_count": equal,
        "best_p36_id": best_any["p36_id"],
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
        "best_same_face_p36_id": best_same_face["p36_id"],
        "best_same_mask_spread": best_same_mask["joint_support_spread"],
        "best_same_mask_p36_id": best_same_mask["p36_id"],
        "best_source_rank0_spread": best_source_rank0["joint_support_spread"],
        "best_source_rank0_p36_id": best_source_rank0["p36_id"],
        "best_low512_spread": best_low512["joint_support_spread"],
        "best_low512_p36_id": best_low512["p36_id"],
        "p26_horizon_component_count": p26_boundary["checked_component_count"],
        "p26_checked_positive_row_total": p26_boundary["checked_positive_row_total"],
        "p26_min_component_margin": p26_min_margin,
        "compound_horizon_margin": min(p26_min_margin, best_any["joint_support_spread"]),
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
        "top_rows": best_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "p26_report": p26_report,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_p36_rows()
    top_table = p35.table_from_rows(TOP_COLUMNS, rows["top_rows"])
    obs_table = p35.table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    p25_report = load_json(P25_REPORT)
    p26_report = rows["p26_report"]
    p27_report = load_json(P27_REPORT)
    p28_report = load_json(P28_REPORT)
    p29_report = load_json(P29_REPORT)
    p30_report = load_json(P30_REPORT)
    p31_report = load_json(P31_REPORT)
    p32_report = load_json(P32_REPORT)
    p33_report = load_json(P33_REPORT)
    p34_report = load_json(P34_REPORT)
    p35_report = load_json(P35_REPORT)
    checks = {
        "input_certificates_available": (
            p25_report.get("all_checks_pass") is True
            and p26_report.get("all_checks_pass") is True
            and p27_report.get("all_checks_pass") is True
            and p28_report.get("all_checks_pass") is True
            and p29_report.get("all_checks_pass") is True
            and p30_report.get("all_checks_pass") is True
            and p31_report.get("all_checks_pass") is True
            and p32_report.get("all_checks_pass") is True
            and p33_report.get("all_checks_pass") is True
            and p34_report.get("all_checks_pass") is True
            and p35_report.get("all_checks_pass") is True
        ),
        "basin_size_matches": (
            obs["p25_extension_count"],
            obs["p31_top_seed_count"],
            obs["p31_top2048_worst_spread"],
            obs["p31_top2048_worst_p31_id"],
            obs["raw_extension_count"],
            obs["candidate_count"],
            obs["duplicate_candidate_count"],
            obs["multi_source_candidate_count"],
            obs["max_source_multiplicity"],
        )
        == (144, 2048, 9_747_264, 73_407_855, 284_672, 283_830, 842, 818, 3),
        "basin_improves_checked_floors": (
            obs["p35_basin_floor"],
            obs["p34_basin_floor"],
            obs["p33_basin_floor"],
            obs["p32_seeded_floor"],
            obs["p31_quint_floor"],
            obs["p30_bounded_floor"],
            obs["p29_quad_floor"],
            obs["p28_triple_floor"],
            obs["p36_basin_min_spread"],
            obs["basin_min_below_p35_flag"],
            obs["basin_min_below_p34_flag"],
            obs["basin_min_below_p33_flag"],
            obs["basin_min_below_p32_flag"],
            obs["basin_min_below_p31_flag"],
            obs["basin_min_below_p30_flag"],
            obs["basin_min_below_p29_flag"],
            obs["basin_min_below_p28_flag"],
        )
        == (
            4_589_696,
            6_796_608,
            7_982_592,
            7_541_600,
            1_815_040,
            4_213_120,
            2_447_744,
            2_601_984,
            1_667_584,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
        ),
        "descent_counts_match": (
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
        == (89, 523, 998, 790, 1, 66, 5, 7, 2_874, 3_630, 0),
        "best_candidate_matches_expected": (
            obs["best_p36_id"],
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
        == (26_360, 1, 14, 32, 47, 57, 79, 2, 1_902, 1_903, 12, 12, 12, 12, 22, 22),
        "best_same_face_and_mask_match": (
            obs["best_same_face_spread"],
            obs["best_same_face_p36_id"],
            obs["best_same_mask_spread"],
            obs["best_same_mask_p36_id"],
        )
        == (3_416_832, 39_461, 3_416_832, 39_461),
        "source_controls_match": (
            obs["best_source_rank0_spread"],
            obs["best_source_rank0_p36_id"],
            obs["best_low512_spread"],
            obs["best_low512_p36_id"],
        )
        == (10_529_536, 24_398, 4_589_696, 161_406),
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
        "classification": "p36_descent",
        "candidate_construction": "p31 top-2048 rows + one p25 row",
        "p35_basin_floor": obs["p35_basin_floor"],
        "p34_basin_floor": obs["p34_basin_floor"],
        "p33_basin_floor": obs["p33_basin_floor"],
        "p32_seeded_floor": obs["p32_seeded_floor"],
        "p31_quint_floor": obs["p31_quint_floor"],
        "p30_bounded_floor": obs["p30_bounded_floor"],
        "p29_quad_floor": obs["p29_quad_floor"],
        "p28_triple_floor": obs["p28_triple_floor"],
        "p36_basin_min_spread": obs["p36_basin_min_spread"],
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
        "seed_worst_spread": obs["p31_top2048_worst_spread"],
        "duplicate_count": obs["duplicate_candidate_count"],
        "best_candidates": [
            {
                "rank": row["rank"],
                "p36_id": row["p36_id"],
                "source_count": row["source_count"],
                "source_min_rank": row["source_min_rank"],
                "source_max_rank": row["source_max_rank"],
                "p25_ids": [
                    row["p25_a"],
                    row["p25_b"],
                    row["p25_c"],
                    row["p25_d"],
                    row["p25_e"],
                    row["p25_f"],
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
            }
            for row in rows["top_rows"][:16]
        ],
        "horizon_reading": (
            "p36 crosses the checked p31/p30/p29/p28 spread floors inside the "
            "top-2048 basin, but still does not equalize support."
        ),
        "claim_boundary": {
            "p31_top2048_basin_screen": 1,
            "raw_support_equalizer_found": obs["support_equal_candidate_count"],
            "p26_margin_preserved": obs["p26_margin_preserved_flag"],
            "universal_completion_claim": 0,
        },
        "top_table_sha256": sha_array(top_table),
        "observable_table_sha256": sha_array(obs_table),
    }
    p36 = {
        "schema": "eta6.p36@1",
        "object": "eta6",
        "construction": {
            "source": "p31 top-2048 + p25",
            "test": "p36 basin screen",
            "classification": witness["classification"],
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.p36.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_P36_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "p36 checks 283830 sextuples from the p31 top-2048 basin. Best "
            "spread 1667584 beats p35 and p31/p30/p29/p28; no equalizer; "
            "p26 margin strict."
        ),
        "stage_protocol": {
            "draft": "rescan complete p31 top-2048 and p26 margin",
            "witness": "extend each p31 top-2048 row by one p25 row",
            "coherence": "compare p36 against p35..p25 floors",
            "closure": "certify p36 basin descent without support crossing",
            "emit": "emit p36 artifacts and p37 seam",
        },
        "inputs": {
            "p25_report": input_entry(P25_REPORT, {"status": p25_report.get("status")}),
            "p25_tables": input_entry(P25_TABLES),
            "p26_report": input_entry(P26_REPORT, {"status": p26_report.get("status")}),
            "p27_report": input_entry(P27_REPORT, {"status": p27_report.get("status")}),
            "p28_report": input_entry(P28_REPORT, {"status": p28_report.get("status")}),
            "p29_report": input_entry(P29_REPORT, {"status": p29_report.get("status")}),
            "p30_report": input_entry(P30_REPORT, {"status": p30_report.get("status")}),
            "p31_report": input_entry(P31_REPORT, {"status": p31_report.get("status")}),
            "p32_report": input_entry(P32_REPORT, {"status": p32_report.get("status")}),
            "p33_report": input_entry(P33_REPORT, {"status": p33_report.get("status")}),
            "p34_report": input_entry(P34_REPORT, {"status": p34_report.get("status")}),
            "p35_report": input_entry(P35_REPORT, {"status": p35_report.get("status")}),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "p36": relpath(OUT_DIR / "p36.json"),
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
                "p36 screen: 283830 candidates",
                "p36 beats p35 and p31",
                "p36 best spread is 1667584",
                "no p36 raw-support equalizer",
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
            "p37: expand to p31 top-8192 and add branch-bound lower checks."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.p36.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.p36.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "p36": p36,
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
    write_json(OUT_DIR / "p36.json", payloads["p36"])
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
