from __future__ import annotations

import itertools
import json
from typing import Any

import numpy as np

try:
    from . import derive_eta6_p25 as p25
    from . import derive_eta6_p26 as p26
    from . import derive_eta6_p27 as p27
    from . import derive_eta6_p28 as p28
    from . import derive_eta6_p29 as p29
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
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "eta6_p30"
STATUS = "ETA6_P30_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

P25_REPORT = p25.OUT_DIR / "report.json"
P25_TABLES = p25.OUT_DIR / "tables.npz"
P26_REPORT = p26.OUT_DIR / "report.json"
P27_REPORT = p27.OUT_DIR / "report.json"
P28_REPORT = p28.OUT_DIR / "report.json"
P28_TABLES = p28.OUT_DIR / "tables.npz"
P29_REPORT = p29.OUT_DIR / "report.json"
P29_TABLES = p29.OUT_DIR / "tables.npz"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_p30.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_p30.py"

TOP_N = 32
SOURCE_P29_PLUS1 = 1
SOURCE_P28_PLUS2 = 2
SOURCE_P29_TRIAD = 4

TOP_COLUMNS = [
    "rank",
    "p30_id",
    "source_mask",
    "p25_a",
    "p25_b",
    "p25_c",
    "p25_d",
    "p25_e",
    "p24_a",
    "p24_b",
    "p24_c",
    "p24_d",
    "p24_e",
    "lift_a",
    "lift_b",
    "lift_c",
    "lift_d",
    "lift_e",
    "face_a",
    "face_b",
    "face_c",
    "face_d",
    "face_e",
    "mask_a",
    "mask_b",
    "mask_c",
    "mask_d",
    "mask_e",
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
    "p28_top_count": 1,
    "p29_top_count": 2,
    "p29_triad_count": 3,
    "p29_plus1_candidate_count": 4,
    "p28_plus2_new_candidate_count": 5,
    "p28_p29_candidate_count": 6,
    "p29_triad_new_candidate_count": 7,
    "candidate_count": 8,
    "p25_single_floor": 9,
    "p27_pair_floor": 10,
    "p28_triple_floor": 11,
    "p29_quad_floor": 12,
    "bounded_min_spread": 13,
    "bounded_min_below_p29_flag": 14,
    "bounded_min_below_p28_flag": 15,
    "below_p29_candidate_count": 16,
    "below_p28_candidate_count": 17,
    "below_p27_candidate_count": 18,
    "below_p25_candidate_count": 19,
    "support_equal_candidate_count": 20,
    "best_p30_id": 21,
    "best_p25_a": 22,
    "best_p25_b": 23,
    "best_p25_c": 24,
    "best_p25_d": 25,
    "best_p25_e": 26,
    "best_face_a": 27,
    "best_face_b": 28,
    "best_face_c": 29,
    "best_face_d": 30,
    "best_face_e": 31,
    "best_same_face_spread": 32,
    "best_same_face_p30_id": 33,
    "best_same_mask_spread": 34,
    "best_same_mask_p30_id": 35,
    "p26_horizon_component_count": 36,
    "p26_checked_positive_row_total": 37,
    "p26_min_component_margin": 38,
    "compound_horizon_margin": 39,
    "compound_horizon_strict_flag": 40,
    "p26_margin_preserved_flag": 41,
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


def add_candidate(
    candidates: dict[tuple[int, int, int, int, int], int],
    candidate: list[int] | tuple[int, int, int, int, int],
    source_mask: int,
) -> None:
    key = tuple(sorted(int(value) for value in candidate))
    candidates[key] = candidates.get(key, 0) | source_mask


def frontier_candidates(
    ext_rows: list[dict[str, int]],
    p28_top_rows: list[dict[str, int]],
    p29_top_rows: list[dict[str, int]],
) -> tuple[dict[tuple[int, int, int, int, int], int], dict[str, int]]:
    ids = [row["p25_id"] for row in ext_rows]
    candidates: dict[tuple[int, int, int, int, int], int] = {}
    for row in p29_top_rows:
        quad = [row["p25_a"], row["p25_b"], row["p25_c"], row["p25_d"]]
        used = set(quad)
        for extension_id in ids:
            if extension_id not in used:
                add_candidate(candidates, [*quad, extension_id], SOURCE_P29_PLUS1)
    p29_plus1_count = len(candidates)

    before_p28 = len(candidates)
    for row in p28_top_rows:
        triple = [row["p25_a"], row["p25_b"], row["p25_c"]]
        used = set(triple)
        rest = [extension_id for extension_id in ids if extension_id not in used]
        for left, right in itertools.combinations(rest, 2):
            add_candidate(candidates, [*triple, left, right], SOURCE_P28_PLUS2)
    p28_plus2_new_count = len(candidates) - before_p28
    p28_p29_count = len(candidates)

    triads: set[tuple[int, int, int]] = set()
    for row in p29_top_rows:
        quad = [row["p25_a"], row["p25_b"], row["p25_c"], row["p25_d"]]
        for triad in itertools.combinations(quad, 3):
            triads.add(tuple(sorted(triad)))

    before_triad = len(candidates)
    for triad in sorted(triads):
        used = set(triad)
        rest = [extension_id for extension_id in ids if extension_id not in used]
        for left, right in itertools.combinations(rest, 2):
            add_candidate(candidates, [*triad, left, right], SOURCE_P29_TRIAD)
    p29_triad_new_count = len(candidates) - before_triad
    counts = {
        "p29_plus1_candidate_count": p29_plus1_count,
        "p28_plus2_new_candidate_count": p28_plus2_new_count,
        "p28_p29_candidate_count": p28_p29_count,
        "p29_triad_count": len(triads),
        "p29_triad_new_candidate_count": p29_triad_new_count,
        "candidate_count": len(candidates),
    }
    return candidates, counts


def ranked_row(
    *,
    rank: int,
    p30_id: int,
    source_mask: int,
    rows: list[dict[str, int]],
    joint: np.ndarray,
    p25_floor: int,
    p27_floor: int,
    p28_floor: int,
    p29_floor: int,
) -> dict[str, int]:
    spread = int(joint.max() - joint.min())
    lifts = [row["lift_id"] for row in rows]
    faces = [row["face_id"] for row in rows]
    masks = [row["label_mask"] for row in rows]
    return {
        "rank": rank,
        "p30_id": p30_id,
        "source_mask": source_mask,
        "p25_a": rows[0]["p25_id"],
        "p25_b": rows[1]["p25_id"],
        "p25_c": rows[2]["p25_id"],
        "p25_d": rows[3]["p25_id"],
        "p25_e": rows[4]["p25_id"],
        "p24_a": rows[0]["p24_row_id"],
        "p24_b": rows[1]["p24_row_id"],
        "p24_c": rows[2]["p24_row_id"],
        "p24_d": rows[3]["p24_row_id"],
        "p24_e": rows[4]["p24_row_id"],
        "lift_a": lifts[0],
        "lift_b": lifts[1],
        "lift_c": lifts[2],
        "lift_d": lifts[3],
        "lift_e": lifts[4],
        "face_a": faces[0],
        "face_b": faces[1],
        "face_c": faces[2],
        "face_d": faces[3],
        "face_e": faces[4],
        "mask_a": masks[0],
        "mask_b": masks[1],
        "mask_c": masks[2],
        "mask_d": masks[3],
        "mask_e": masks[4],
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
        "below_p29_floor_flag": int(spread < p29_floor),
        "below_p28_floor_flag": int(spread < p28_floor),
        "below_p27_floor_flag": int(spread < p27_floor),
        "below_p25_floor_flag": int(spread < p25_floor),
        "support_equal_flag": int(spread == 0),
        "joint_mult_value": int(sum(row["mult_value"] for row in rows)),
    }


def build_p30_rows() -> dict[str, Any]:
    p25_tables = np.load(P25_TABLES, allow_pickle=False)
    p28_tables = np.load(P28_TABLES, allow_pickle=False)
    p29_tables = np.load(P29_TABLES, allow_pickle=False)
    ext_rows = rows_from_table(
        np.asarray(p25_tables["ext_table"], dtype=np.int64),
        p25.EXT_COLUMNS,
    )
    p28_top_rows = rows_from_table(
        np.asarray(p28_tables["top_table"], dtype=np.int64),
        p28.TOP_COLUMNS,
    )
    p29_top_rows = rows_from_table(
        np.asarray(p29_tables["top_table"], dtype=np.int64),
        p29.TOP_COLUMNS,
    )
    row_by_id = {row["p25_id"]: row for row in ext_rows}
    support_by_id = {row["p25_id"]: support(row) for row in ext_rows}
    supports = np.asarray([support(row) for row in ext_rows], dtype=np.int64)
    p25_floor = int((supports.max(axis=1) - supports.min(axis=1)).min())
    p27_floor = int(load_json(P27_REPORT)["witness"]["pair_min_spread"])
    p28_floor = int(load_json(P28_REPORT)["witness"]["triple_min_spread"])
    p29_floor = int(load_json(P29_REPORT)["witness"]["quad_min_spread"])
    candidates, source_counts = frontier_candidates(
        ext_rows,
        p28_top_rows,
        p29_top_rows,
    )

    best_rows: list[dict[str, int]] = []
    best_any: dict[str, int] | None = None
    best_same_face: dict[str, int] | None = None
    best_same_mask: dict[str, int] | None = None
    below_p29 = 0
    below_p28 = 0
    below_p27 = 0
    below_p25 = 0
    equal = 0

    for p30_id, candidate in enumerate(sorted(candidates)):
        rows = [row_by_id[p25_id] for p25_id in candidate]
        joint = sum(
            (support_by_id[p25_id] for p25_id in candidate),
            np.zeros(5, dtype=np.int64),
        )
        row = ranked_row(
            rank=0,
            p30_id=p30_id,
            source_mask=candidates[candidate],
            rows=rows,
            joint=joint,
            p25_floor=p25_floor,
            p27_floor=p27_floor,
            p28_floor=p28_floor,
            p29_floor=p29_floor,
        )
        spread = row["joint_support_spread"]
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
        key = (spread, p30_id)
        if best_any is None or key < (
            best_any["joint_support_spread"],
            best_any["p30_id"],
        ):
            best_any = row
        if row["same_face_flag"] == 1 and (
            best_same_face is None
            or key
            < (
                best_same_face["joint_support_spread"],
                best_same_face["p30_id"],
            )
        ):
            best_same_face = row
        if row["same_mask_flag"] == 1 and (
            best_same_mask is None
            or key
            < (
                best_same_mask["joint_support_spread"],
                best_same_mask["p30_id"],
            )
        ):
            best_same_mask = row
        best_rows.append(row)
        best_rows.sort(
            key=lambda value: (value["joint_support_spread"], value["p30_id"])
        )
        if len(best_rows) > 512:
            best_rows = best_rows[:64]

    if best_any is None or best_same_face is None or best_same_mask is None:
        raise ValueError("empty p30 search")
    best_rows = sorted(
        best_rows,
        key=lambda value: (value["joint_support_spread"], value["p30_id"]),
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
        "p28_top_count": len(p28_top_rows),
        "p29_top_count": len(p29_top_rows),
        **source_counts,
        "p25_single_floor": p25_floor,
        "p27_pair_floor": p27_floor,
        "p28_triple_floor": p28_floor,
        "p29_quad_floor": p29_floor,
        "bounded_min_spread": best_any["joint_support_spread"],
        "bounded_min_below_p29_flag": int(best_any["joint_support_spread"] < p29_floor),
        "bounded_min_below_p28_flag": int(best_any["joint_support_spread"] < p28_floor),
        "below_p29_candidate_count": below_p29,
        "below_p28_candidate_count": below_p28,
        "below_p27_candidate_count": below_p27,
        "below_p25_candidate_count": below_p25,
        "support_equal_candidate_count": equal,
        "best_p30_id": best_any["p30_id"],
        "best_p25_a": best_any["p25_a"],
        "best_p25_b": best_any["p25_b"],
        "best_p25_c": best_any["p25_c"],
        "best_p25_d": best_any["p25_d"],
        "best_p25_e": best_any["p25_e"],
        "best_face_a": best_any["face_a"],
        "best_face_b": best_any["face_b"],
        "best_face_c": best_any["face_c"],
        "best_face_d": best_any["face_d"],
        "best_face_e": best_any["face_e"],
        "best_same_face_spread": best_same_face["joint_support_spread"],
        "best_same_face_p30_id": best_same_face["p30_id"],
        "best_same_mask_spread": best_same_mask["joint_support_spread"],
        "best_same_mask_p30_id": best_same_mask["p30_id"],
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
    rows = build_p30_rows()
    top_table = table_from_rows(TOP_COLUMNS, rows["top_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    p25_report = load_json(P25_REPORT)
    p26_report = rows["p26_report"]
    p27_report = load_json(P27_REPORT)
    p28_report = load_json(P28_REPORT)
    p29_report = load_json(P29_REPORT)
    checks = {
        "input_certificates_available": (
            p25_report.get("all_checks_pass") is True
            and p26_report.get("all_checks_pass") is True
            and p27_report.get("all_checks_pass") is True
            and p28_report.get("all_checks_pass") is True
            and p29_report.get("all_checks_pass") is True
        ),
        "bounded_frontier_size_matches": (
            obs["p25_extension_count"],
            obs["p28_top_count"],
            obs["p29_top_count"],
            obs["p29_triad_count"],
            obs["p29_plus1_candidate_count"],
            obs["p28_plus2_new_candidate_count"],
            obs["p28_p29_candidate_count"],
            obs["p29_triad_new_candidate_count"],
            obs["candidate_count"],
        )
        == (144, 32, 32, 124, 4_476, 311_592, 316_068, 1_175_402, 1_491_470),
        "bounded_five_move_stalls_above_p29_floor": (
            obs["p29_quad_floor"],
            obs["p28_triple_floor"],
            obs["bounded_min_spread"],
            obs["bounded_min_below_p29_flag"],
            obs["bounded_min_below_p28_flag"],
            obs["below_p29_candidate_count"],
            obs["below_p28_candidate_count"],
            obs["support_equal_candidate_count"],
        )
        == (2_447_744, 2_601_984, 4_213_120, 0, 0, 0, 0, 0),
        "descent_counts_match": (
            obs["below_p27_candidate_count"],
            obs["below_p25_candidate_count"],
        )
        == (236, 328),
        "best_candidate_matches_expected": (
            obs["best_p30_id"],
            obs["best_p25_a"],
            obs["best_p25_b"],
            obs["best_p25_c"],
            obs["best_p25_d"],
            obs["best_p25_e"],
            obs["best_face_a"],
            obs["best_face_b"],
            obs["best_face_c"],
            obs["best_face_d"],
            obs["best_face_e"],
        )
        == (96_125, 2, 16, 28, 44, 122, 12, 12, 12, 12, 26),
        "best_same_face_and_mask_match": (
            obs["best_same_face_spread"],
            obs["best_same_face_p30_id"],
            obs["best_same_mask_spread"],
            obs["best_same_mask_p30_id"],
        )
        == (4_912_640, 72_396, 4_912_640, 72_396),
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
        "classification": "bounded_five_move_frontier_stall",
        "candidate_construction": (
            "deduplicated union of p29-top one-step extensions, p28-top two-step "
            "extensions, and p29-top triad shadows"
        ),
        "p29_quad_floor": obs["p29_quad_floor"],
        "p28_triple_floor": obs["p28_triple_floor"],
        "bounded_min_spread": obs["bounded_min_spread"],
        "below_p29_candidate_count": obs["below_p29_candidate_count"],
        "below_p28_candidate_count": obs["below_p28_candidate_count"],
        "below_p27_candidate_count": obs["below_p27_candidate_count"],
        "below_p25_candidate_count": obs["below_p25_candidate_count"],
        "support_equal_candidate_count": obs["support_equal_candidate_count"],
        "compound_horizon_margin": obs["compound_horizon_margin"],
        "candidate_count": obs["candidate_count"],
        "best_candidates": [
            {
                "rank": row["rank"],
                "p30_id": row["p30_id"],
                "source_mask": row["source_mask"],
                "p25_ids": [
                    row["p25_a"],
                    row["p25_b"],
                    row["p25_c"],
                    row["p25_d"],
                    row["p25_e"],
                ],
                "p24_rows": [
                    row["p24_a"],
                    row["p24_b"],
                    row["p24_c"],
                    row["p24_d"],
                    row["p24_e"],
                ],
                "lifts": [
                    row["lift_a"],
                    row["lift_b"],
                    row["lift_c"],
                    row["lift_d"],
                    row["lift_e"],
                ],
                "faces": [
                    row["face_a"],
                    row["face_b"],
                    row["face_c"],
                    row["face_d"],
                    row["face_e"],
                ],
                "masks": [
                    row["mask_a"],
                    row["mask_b"],
                    row["mask_c"],
                    row["mask_d"],
                    row["mask_e"],
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
        "horizon_reading": (
            "The bounded lifted five-move frontier does not continue the p29 "
            "descent. It stays above both the p29 and p28 floors, finds no raw "
            "support equalizer, and preserves the p26 positive margin packet."
        ),
        "claim_boundary": {
            "bounded_five_move_screen": 1,
            "raw_support_equalizer_found": obs["support_equal_candidate_count"],
            "p26_margin_preserved": obs["p26_margin_preserved_flag"],
            "universal_completion_claim": 0,
        },
        "top_table_sha256": sha_array(top_table),
        "observable_table_sha256": sha_array(obs_table),
    }
    p30 = {
        "schema": "eta6.p30@1",
        "object": "eta6",
        "construction": {
            "source": "eta6_p25 vectors plus eta6_p28/p29 top frontiers",
            "test": "bounded five-move lifted compound support-spread screen",
            "classification": witness["classification"],
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.p30.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_P30_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "A bounded lifted five-move screen around the p28/p29 top frontiers "
            "checks 1491470 deduplicated candidates. The best spread is "
            "4213120, so the bounded frontier does not beat the p29 four-move "
            "floor 2447744 or the p28 three-move floor 2601984. No checked "
            "candidate equalizes raw support, and the p26 finite-horizon "
            "margins remain strict."
        ),
        "stage_protocol": {
            "draft": "start from eta6_p25 vectors and eta6_p28/p29 frontiers",
            "witness": "deduplicate p29+1, p28+2, and p29-triad-shadow five-move candidates",
            "coherence": "compare bounded five-move spread against p29, p28, p27, and p25 floors while preserving p26 margins",
            "closure": "certify bounded five-move stall without raw-support equalization",
            "emit": "emit compact p30 artifacts and the next wider five-move seam",
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
            "p28_tables": input_entry(P28_TABLES),
            "p29_report": input_entry(
                P29_REPORT,
                {
                    "status": p29_report.get("status"),
                    "certificate_sha256": p29_report.get("certificate_sha256"),
                },
            ),
            "p29_tables": input_entry(P29_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "p30": relpath(OUT_DIR / "p30.json"),
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
                "bounded lifted five-move frontier over 1491470 candidates",
                "no bounded five-move candidate beats the p29 four-move floor",
                "no bounded five-move candidate beats the p28 three-move floor",
                "best bounded five-move support spread is 4213120",
                "no bounded five-move candidate equalizes raw support",
                "p26 finite-horizon margins remain positive on the checked packet",
            ],
            "does_not_certify_because_out_of_scope": [
                "complete five-move search over all p25 quintuple compounds",
                "a global five-move support-spread lower bound",
                "new simple-object semantics for the lifted carrier",
                "that eta6 is uncrossable outside the checked row universes",
            ],
        },
        "next_highest_yield_item": (
            "Run p31 as a pruned wider five-move search seeded by all p29 "
            "subquad frontiers whose lower envelopes can still approach the p29 floor."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.p30.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.p30.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "p30": p30,
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
    write_json(OUT_DIR / "p30.json", payloads["p30"])
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
