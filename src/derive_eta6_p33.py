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
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "eta6_p33"
STATUS = "ETA6_P33_CERTIFIED"
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
P31_TABLES = p31.OUT_DIR / "tables.npz"
P32_REPORT = p32.OUT_DIR / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_p33.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_p33.py"

TOP_N = 32
SEED_N = 32
TOP_COLUMNS = [
    "rank",
    "p33_id",
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
    "raw_extension_count": 2,
    "candidate_count": 3,
    "duplicate_candidate_count": 4,
    "multi_source_candidate_count": 5,
    "max_source_multiplicity": 6,
    "p25_single_floor": 7,
    "p27_pair_floor": 8,
    "p28_triple_floor": 9,
    "p29_quad_floor": 10,
    "p30_bounded_floor": 11,
    "p31_quint_floor": 12,
    "p32_seeded_floor": 13,
    "p33_basin_min_spread": 14,
    "basin_min_below_p32_flag": 15,
    "basin_min_below_p31_flag": 16,
    "basin_min_below_p30_flag": 17,
    "basin_min_below_p29_flag": 18,
    "basin_min_below_p28_flag": 19,
    "below_p32_candidate_count": 20,
    "below_p31_candidate_count": 21,
    "below_p30_candidate_count": 22,
    "below_p29_candidate_count": 23,
    "below_p28_candidate_count": 24,
    "below_p27_candidate_count": 25,
    "below_p25_candidate_count": 26,
    "support_equal_candidate_count": 27,
    "best_p33_id": 28,
    "best_p25_a": 29,
    "best_p25_b": 30,
    "best_p25_c": 31,
    "best_p25_d": 32,
    "best_p25_e": 33,
    "best_p25_f": 34,
    "best_source_count": 35,
    "best_source_min_rank": 36,
    "best_source_max_rank": 37,
    "best_face_a": 38,
    "best_face_b": 39,
    "best_face_c": 40,
    "best_face_d": 41,
    "best_face_e": 42,
    "best_face_f": 43,
    "best_same_face_spread": 44,
    "best_same_face_p33_id": 45,
    "best_same_mask_spread": 46,
    "best_same_mask_p33_id": 47,
    "best_source_rank0_spread": 48,
    "best_source_rank0_p33_id": 49,
    "p26_horizon_component_count": 50,
    "p26_checked_positive_row_total": 51,
    "p26_min_component_margin": 52,
    "compound_horizon_margin": 53,
    "compound_horizon_strict_flag": 54,
    "p26_margin_preserved_flag": 55,
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


def support(row: dict[str, int]) -> np.ndarray:
    return np.asarray([row[f"p{index}_support"] for index in range(5)], dtype=np.int64)


def ranked_row(
    *,
    rank: int,
    p33_id: int,
    source_ranks: list[int],
    rows: list[dict[str, int]],
    joint: np.ndarray,
    p25_floor: int,
    p27_floor: int,
    p28_floor: int,
    p29_floor: int,
    p30_floor: int,
    p31_floor: int,
    p32_floor: int,
) -> dict[str, int]:
    spread = int(joint.max() - joint.min())
    lifts = [row["lift_id"] for row in rows]
    faces = [row["face_id"] for row in rows]
    masks = [row["label_mask"] for row in rows]
    return {
        "rank": rank,
        "p33_id": p33_id,
        "source_count": len(source_ranks),
        "source_min_rank": min(source_ranks),
        "source_max_rank": max(source_ranks),
        "p25_a": rows[0]["p25_id"],
        "p25_b": rows[1]["p25_id"],
        "p25_c": rows[2]["p25_id"],
        "p25_d": rows[3]["p25_id"],
        "p25_e": rows[4]["p25_id"],
        "p25_f": rows[5]["p25_id"],
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
        "below_p32_floor_flag": int(spread < p32_floor),
        "below_p31_floor_flag": int(spread < p31_floor),
        "below_p30_floor_flag": int(spread < p30_floor),
        "below_p29_floor_flag": int(spread < p29_floor),
        "below_p28_floor_flag": int(spread < p28_floor),
        "below_p27_floor_flag": int(spread < p27_floor),
        "below_p25_floor_flag": int(spread < p25_floor),
        "support_equal_flag": int(spread == 0),
        "joint_mult_value": int(sum(row["mult_value"] for row in rows)),
    }


def build_p33_rows() -> dict[str, Any]:
    p25_tables = np.load(P25_TABLES, allow_pickle=False)
    ext_rows = rows_from_table(
        np.asarray(p25_tables["ext_table"], dtype=np.int64),
        p25.EXT_COLUMNS,
    )
    supports = np.asarray([support(row) for row in ext_rows], dtype=np.int64)
    support_by_id = {row["p25_id"]: support(row) for row in ext_rows}
    row_by_id = {row["p25_id"]: row for row in ext_rows}
    p31_tables = np.load(P31_TABLES, allow_pickle=False)
    p31_top = rows_from_table(
        np.asarray(p31_tables["top_table"], dtype=np.int64),
        p31.TOP_COLUMNS,
    )[:SEED_N]
    p25_floor = int((supports.max(axis=1) - supports.min(axis=1)).min())
    p27_floor = int(load_json(P27_REPORT)["witness"]["pair_min_spread"])
    p28_floor = int(load_json(P28_REPORT)["witness"]["triple_min_spread"])
    p29_floor = int(load_json(P29_REPORT)["witness"]["quad_min_spread"])
    p30_floor = int(load_json(P30_REPORT)["witness"]["bounded_min_spread"])
    p31_floor = int(load_json(P31_REPORT)["witness"]["quint_min_spread"])
    p32_floor = int(load_json(P32_REPORT)["witness"]["seeded_six_min_spread"])

    candidates: dict[tuple[int, int, int, int, int, int], set[int]] = {}
    raw_extension_count = 0
    for seed in p31_top:
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
    below_p32 = 0
    below_p31 = 0
    below_p30 = 0
    below_p29 = 0
    below_p28 = 0
    below_p27 = 0
    below_p25 = 0
    equal = 0

    for p33_id, (candidate, source_rank_set) in enumerate(sorted(candidates.items())):
        rows = [row_by_id[p25_id] for p25_id in candidate]
        joint = sum(
            (support_by_id[p25_id] for p25_id in candidate),
            np.zeros(5, dtype=np.int64),
        )
        source_ranks = sorted(source_rank_set)
        row = ranked_row(
            rank=0,
            p33_id=p33_id,
            source_ranks=source_ranks,
            rows=rows,
            joint=joint,
            p25_floor=p25_floor,
            p27_floor=p27_floor,
            p28_floor=p28_floor,
            p29_floor=p29_floor,
            p30_floor=p30_floor,
            p31_floor=p31_floor,
            p32_floor=p32_floor,
        )
        spread = row["joint_support_spread"]
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
        key = (spread, p33_id)
        if best_any is None or key < (
            best_any["joint_support_spread"],
            best_any["p33_id"],
        ):
            best_any = row
        if row["same_face_flag"] == 1 and (
            best_same_face is None
            or key
            < (
                best_same_face["joint_support_spread"],
                best_same_face["p33_id"],
            )
        ):
            best_same_face = row
        if row["same_mask_flag"] == 1 and (
            best_same_mask is None
            or key
            < (
                best_same_mask["joint_support_spread"],
                best_same_mask["p33_id"],
            )
        ):
            best_same_mask = row
        if row["source_min_rank"] == 0 and (
            best_source_rank0 is None
            or key
            < (
                best_source_rank0["joint_support_spread"],
                best_source_rank0["p33_id"],
            )
        ):
            best_source_rank0 = row
        best_rows.append(row)

    if (
        best_any is None
        or best_same_face is None
        or best_same_mask is None
        or best_source_rank0 is None
    ):
        raise ValueError("empty p33 search")
    best_rows = sorted(
        best_rows,
        key=lambda value: (value["joint_support_spread"], value["p33_id"]),
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
        "p31_top_seed_count": len(p31_top),
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
        "p33_basin_min_spread": best_any["joint_support_spread"],
        "basin_min_below_p32_flag": int(best_any["joint_support_spread"] < p32_floor),
        "basin_min_below_p31_flag": int(best_any["joint_support_spread"] < p31_floor),
        "basin_min_below_p30_flag": int(best_any["joint_support_spread"] < p30_floor),
        "basin_min_below_p29_flag": int(best_any["joint_support_spread"] < p29_floor),
        "basin_min_below_p28_flag": int(best_any["joint_support_spread"] < p28_floor),
        "below_p32_candidate_count": below_p32,
        "below_p31_candidate_count": below_p31,
        "below_p30_candidate_count": below_p30,
        "below_p29_candidate_count": below_p29,
        "below_p28_candidate_count": below_p28,
        "below_p27_candidate_count": below_p27,
        "below_p25_candidate_count": below_p25,
        "support_equal_candidate_count": equal,
        "best_p33_id": best_any["p33_id"],
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
        "best_same_face_p33_id": best_same_face["p33_id"],
        "best_same_mask_spread": best_same_mask["joint_support_spread"],
        "best_same_mask_p33_id": best_same_mask["p33_id"],
        "best_source_rank0_spread": best_source_rank0["joint_support_spread"],
        "best_source_rank0_p33_id": best_source_rank0["p33_id"],
        "p26_horizon_component_count": p26_boundary["checked_component_count"],
        "p26_checked_positive_row_total": p26_boundary["checked_positive_row_total"],
        "p26_min_component_margin": p26_min_margin,
        "compound_horizon_margin": min(p26_min_margin, best_any["joint_support_spread"]),
        "compound_horizon_strict_flag": int(
            p26_min_margin > 0
            and best_any["joint_support_spread"] > 0
            and equal == 0
        ),
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
    rows = build_p33_rows()
    top_table = table_from_rows(TOP_COLUMNS, rows["top_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    p25_report = load_json(P25_REPORT)
    p26_report = rows["p26_report"]
    p27_report = load_json(P27_REPORT)
    p28_report = load_json(P28_REPORT)
    p29_report = load_json(P29_REPORT)
    p30_report = load_json(P30_REPORT)
    p31_report = load_json(P31_REPORT)
    p32_report = load_json(P32_REPORT)
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
        ),
        "basin_size_matches": (
            obs["p25_extension_count"],
            obs["p31_top_seed_count"],
            obs["raw_extension_count"],
            obs["candidate_count"],
            obs["duplicate_candidate_count"],
            obs["multi_source_candidate_count"],
            obs["max_source_multiplicity"],
        )
        == (144, 32, 4_448, 4_447, 1, 1, 2),
        "basin_stalls_above_p32": (
            obs["p32_seeded_floor"],
            obs["p31_quint_floor"],
            obs["p30_bounded_floor"],
            obs["p33_basin_min_spread"],
            obs["basin_min_below_p32_flag"],
            obs["basin_min_below_p31_flag"],
            obs["basin_min_below_p30_flag"],
            obs["basin_min_below_p29_flag"],
            obs["basin_min_below_p28_flag"],
        )
        == (7_541_600, 1_815_040, 4_213_120, 7_982_592, 0, 0, 0, 0, 0),
        "descent_counts_match": (
            obs["below_p32_candidate_count"],
            obs["below_p31_candidate_count"],
            obs["below_p30_candidate_count"],
            obs["below_p29_candidate_count"],
            obs["below_p28_candidate_count"],
            obs["below_p27_candidate_count"],
            obs["below_p25_candidate_count"],
            obs["support_equal_candidate_count"],
        )
        == (0, 0, 0, 0, 0, 46, 78, 0),
        "best_candidate_matches_expected": (
            obs["best_p33_id"],
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
        == (762, 2, 8, 52, 56, 116, 141, 1, 24, 24, 12, 12, 22, 22, 26, 26),
        "best_same_face_and_mask_match": (
            obs["best_same_face_spread"],
            obs["best_same_face_p33_id"],
            obs["best_same_mask_spread"],
            obs["best_same_mask_p33_id"],
        )
        == (9_602_944, 29, 9_602_944, 29),
        "rank0_source_stalls": (
            obs["best_source_rank0_spread"],
            obs["best_source_rank0_p33_id"],
        )
        == (10_529_536, 484),
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
        "classification": "p33_stall",
        "candidate_construction": "p31 top-32 rows + one p25 row",
        "p32_seeded_floor": obs["p32_seeded_floor"],
        "p31_quint_floor": obs["p31_quint_floor"],
        "p30_bounded_floor": obs["p30_bounded_floor"],
        "p33_basin_min_spread": obs["p33_basin_min_spread"],
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
        "duplicate_count": obs["duplicate_candidate_count"],
        "best_candidates": [
            {
                "rank": row["rank"],
                "p33_id": row["p33_id"],
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
                "p24_rows": [
                    row["p24_a"],
                    row["p24_b"],
                    row["p24_c"],
                    row["p24_d"],
                    row["p24_e"],
                    row["p24_f"],
                ],
                "lifts": [
                    row["lift_a"],
                    row["lift_b"],
                    row["lift_c"],
                    row["lift_d"],
                    row["lift_e"],
                    row["lift_f"],
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
            for row in rows["top_rows"][:16]
        ],
        "horizon_reading": "p33 basin stalls above p32; no equalizer; p26 margin stays strict.",
        "claim_boundary": {
            "p31_top32_basin_screen": 1,
            "raw_support_equalizer_found": obs["support_equal_candidate_count"],
            "p26_margin_preserved": obs["p26_margin_preserved_flag"],
            "universal_completion_claim": 0,
        },
        "top_table_sha256": sha_array(top_table),
        "observable_table_sha256": sha_array(obs_table),
    }
    p33 = {
        "schema": "eta6.p33@1",
        "object": "eta6",
        "construction": {
            "source": "p31 top-32 + p25",
            "test": "p33 basin screen",
            "classification": witness["classification"],
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.p33.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_P33_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "p33 checks 4447 sextuples from the p31 top-32 basin. Best spread "
            "7982592 is above p32, p31, and p30; no equalizer; p26 margin strict."
        ),
        "stage_protocol": {
            "draft": "start from p31 top-32 and p26 margin",
            "witness": "extend each p31 top row by one p25 row",
            "coherence": "compare p33 against p32..p25 floors",
            "closure": "certify p33 basin stall with no equalizer",
            "emit": "emit p33 artifacts and p34 seam",
        },
        "inputs": {
            "p25_report": input_entry(
                P25_REPORT,
                {
                    "status": p25_report.get("status"),
                    "certificate_sha256": p25_report.get("certificate_sha256"),
                },
            ),
            "p25_tables": input_entry(P25_TABLES),
            "p26_report": input_entry(
                P26_REPORT,
                {
                    "status": p26_report.get("status"),
                    "certificate_sha256": p26_report.get("certificate_sha256"),
                },
            ),
            "p27_report": input_entry(
                P27_REPORT,
                {
                    "status": p27_report.get("status"),
                    "certificate_sha256": p27_report.get("certificate_sha256"),
                },
            ),
            "p28_report": input_entry(
                P28_REPORT,
                {
                    "status": p28_report.get("status"),
                    "certificate_sha256": p28_report.get("certificate_sha256"),
                },
            ),
            "p29_report": input_entry(
                P29_REPORT,
                {
                    "status": p29_report.get("status"),
                    "certificate_sha256": p29_report.get("certificate_sha256"),
                },
            ),
            "p30_report": input_entry(
                P30_REPORT,
                {
                    "status": p30_report.get("status"),
                    "certificate_sha256": p30_report.get("certificate_sha256"),
                },
            ),
            "p31_report": input_entry(
                P31_REPORT,
                {
                    "status": p31_report.get("status"),
                    "certificate_sha256": p31_report.get("certificate_sha256"),
                },
            ),
            "p31_tables": input_entry(P31_TABLES),
            "p32_report": input_entry(
                P32_REPORT,
                {
                    "status": p32_report.get("status"),
                    "certificate_sha256": p32_report.get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "p33": relpath(OUT_DIR / "p33.json"),
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
                "p33 screen: 4447 candidates",
                "no p33 candidate beats p32",
                "p33 best spread is 7982592",
                "no p33 raw-support equalizer",
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
            "p34: branch-bound full six-move lower bound, or expand the basin to p31 top-128."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.p33.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.p33.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "p33": p33,
        "top_csv": csv_text(TOP_COLUMNS, rows["top_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
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
    write_json(OUT_DIR / "p33.json", payloads["p33"])
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
