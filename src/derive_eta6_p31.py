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
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "eta6_p31"
STATUS = "ETA6_P31_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

P25_REPORT = p25.OUT_DIR / "report.json"
P25_TABLES = p25.OUT_DIR / "tables.npz"
P26_REPORT = p26.OUT_DIR / "report.json"
P27_REPORT = p27.OUT_DIR / "report.json"
P28_REPORT = p28.OUT_DIR / "report.json"
P29_REPORT = p29.OUT_DIR / "report.json"
P30_REPORT = p30.OUT_DIR / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_p31.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_p31.py"

TOP_N = 32
TOP_COLUMNS = [
    "rank",
    "p31_id",
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
    "pair_sum_count": 1,
    "triple_sum_count": 2,
    "quint_count": 3,
    "p25_single_floor": 4,
    "p27_pair_floor": 5,
    "p28_triple_floor": 6,
    "p29_quad_floor": 7,
    "p30_bounded_floor": 8,
    "quint_min_spread": 9,
    "quint_min_below_p30_flag": 10,
    "quint_min_below_p29_flag": 11,
    "quint_min_below_p28_flag": 12,
    "below_p30_quint_count": 13,
    "below_p29_quint_count": 14,
    "below_p28_quint_count": 15,
    "below_p27_quint_count": 16,
    "below_p25_quint_count": 17,
    "support_equal_quint_count": 18,
    "best_p31_id": 19,
    "best_p25_a": 20,
    "best_p25_b": 21,
    "best_p25_c": 22,
    "best_p25_d": 23,
    "best_p25_e": 24,
    "best_face_a": 25,
    "best_face_b": 26,
    "best_face_c": 27,
    "best_face_d": 28,
    "best_face_e": 29,
    "best_same_face_spread": 30,
    "best_same_face_p31_id": 31,
    "best_same_mask_spread": 32,
    "best_same_mask_p31_id": 33,
    "p26_horizon_component_count": 34,
    "p26_checked_positive_row_total": 35,
    "p26_min_component_margin": 36,
    "compound_horizon_margin": 37,
    "compound_horizon_strict_flag": 38,
    "p26_margin_preserved_flag": 39,
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


def pair_index_arrays(n: int) -> tuple[np.ndarray, np.ndarray]:
    left: list[int] = []
    right: list[int] = []
    for i in range(n - 1):
        for j in range(i + 1, n):
            left.append(i)
            right.append(j)
    return np.asarray(left, dtype=np.int64), np.asarray(right, dtype=np.int64)


def triple_index_arrays(n: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    left: list[int] = []
    middle: list[int] = []
    right: list[int] = []
    for i in range(n - 2):
        for j in range(i + 1, n - 1):
            for k in range(j + 1, n):
                left.append(i)
                middle.append(j)
                right.append(k)
    return (
        np.asarray(left, dtype=np.int64),
        np.asarray(middle, dtype=np.int64),
        np.asarray(right, dtype=np.int64),
    )


def ranked_row(
    *,
    rank: int,
    p31_id: int,
    rows: list[dict[str, int]],
    joint: np.ndarray,
    p25_floor: int,
    p27_floor: int,
    p28_floor: int,
    p29_floor: int,
    p30_floor: int,
) -> dict[str, int]:
    spread = int(joint.max() - joint.min())
    lifts = [row["lift_id"] for row in rows]
    faces = [row["face_id"] for row in rows]
    masks = [row["label_mask"] for row in rows]
    return {
        "rank": rank,
        "p31_id": p31_id,
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
        "below_p30_floor_flag": int(spread < p30_floor),
        "below_p29_floor_flag": int(spread < p29_floor),
        "below_p28_floor_flag": int(spread < p28_floor),
        "below_p27_floor_flag": int(spread < p27_floor),
        "below_p25_floor_flag": int(spread < p25_floor),
        "support_equal_flag": int(spread == 0),
        "joint_mult_value": int(sum(row["mult_value"] for row in rows)),
    }


def build_p31_rows() -> dict[str, Any]:
    p25_tables = np.load(P25_TABLES, allow_pickle=False)
    ext_rows = rows_from_table(
        np.asarray(p25_tables["ext_table"], dtype=np.int64),
        p25.EXT_COLUMNS,
    )
    supports = np.asarray([support(row) for row in ext_rows], dtype=np.int64)
    p25_floor = int((supports.max(axis=1) - supports.min(axis=1)).min())
    p27_floor = int(load_json(P27_REPORT)["witness"]["pair_min_spread"])
    p28_floor = int(load_json(P28_REPORT)["witness"]["triple_min_spread"])
    p29_floor = int(load_json(P29_REPORT)["witness"]["quad_min_spread"])
    p30_floor = int(load_json(P30_REPORT)["witness"]["bounded_min_spread"])

    pair_left, pair_right = pair_index_arrays(len(ext_rows))
    triple_a, triple_b, triple_c = triple_index_arrays(len(ext_rows))
    pair_sums = supports[pair_left] + supports[pair_right]
    triple_sums = supports[triple_a] + supports[triple_b] + supports[triple_c]

    best_rows: list[dict[str, int]] = []
    best_any: dict[str, int] | None = None
    best_same_face: dict[str, int] | None = None
    best_same_mask: dict[str, int] | None = None
    below_p30 = 0
    below_p29 = 0
    below_p28 = 0
    below_p27 = 0
    below_p25 = 0
    equal = 0
    p31_id = 0

    for triple_id in range(len(triple_a)):
        k = int(triple_c[triple_id])
        pair_start = int(np.searchsorted(pair_left, k + 1, side="left"))
        if pair_start >= len(pair_left):
            continue
        joint_rows = pair_sums[pair_start:] + triple_sums[triple_id]
        spreads = joint_rows.max(axis=1) - joint_rows.min(axis=1)
        below_p30 += int((spreads < p30_floor).sum())
        below_p29 += int((spreads < p29_floor).sum())
        below_p28 += int((spreads < p28_floor).sum())
        below_p27 += int((spreads < p27_floor).sum())
        below_p25 += int((spreads < p25_floor).sum())
        equal += int((spreads == 0).sum())

        low_positions = np.flatnonzero(spreads < p30_floor)
        if len(low_positions) == 0:
            p31_id += len(spreads)
            continue
        for pos in low_positions:
            pair_id = pair_start + int(pos)
            rows = [
                ext_rows[int(triple_a[triple_id])],
                ext_rows[int(triple_b[triple_id])],
                ext_rows[int(triple_c[triple_id])],
                ext_rows[int(pair_left[pair_id])],
                ext_rows[int(pair_right[pair_id])],
            ]
            row = ranked_row(
                rank=0,
                p31_id=p31_id + int(pos),
                rows=rows,
                joint=joint_rows[int(pos)],
                p25_floor=p25_floor,
                p27_floor=p27_floor,
                p28_floor=p28_floor,
                p29_floor=p29_floor,
                p30_floor=p30_floor,
            )
            key = (row["joint_support_spread"], row["p31_id"])
            if best_any is None or key < (
                best_any["joint_support_spread"],
                best_any["p31_id"],
            ):
                best_any = row
            if row["same_face_flag"] == 1 and (
                best_same_face is None
                or key
                < (
                    best_same_face["joint_support_spread"],
                    best_same_face["p31_id"],
                )
            ):
                best_same_face = row
            if row["same_mask_flag"] == 1 and (
                best_same_mask is None
                or key
                < (
                    best_same_mask["joint_support_spread"],
                    best_same_mask["p31_id"],
                )
            ):
                best_same_mask = row
            best_rows.append(row)
        p31_id += len(spreads)

    if best_any is None or best_same_face is None or best_same_mask is None:
        raise ValueError("empty p31 search")
    best_rows = sorted(
        best_rows,
        key=lambda value: (value["joint_support_spread"], value["p31_id"]),
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
        "pair_sum_count": len(pair_left),
        "triple_sum_count": len(triple_a),
        "quint_count": p31_id,
        "p25_single_floor": p25_floor,
        "p27_pair_floor": p27_floor,
        "p28_triple_floor": p28_floor,
        "p29_quad_floor": p29_floor,
        "p30_bounded_floor": p30_floor,
        "quint_min_spread": best_any["joint_support_spread"],
        "quint_min_below_p30_flag": int(best_any["joint_support_spread"] < p30_floor),
        "quint_min_below_p29_flag": int(best_any["joint_support_spread"] < p29_floor),
        "quint_min_below_p28_flag": int(best_any["joint_support_spread"] < p28_floor),
        "below_p30_quint_count": below_p30,
        "below_p29_quint_count": below_p29,
        "below_p28_quint_count": below_p28,
        "below_p27_quint_count": below_p27,
        "below_p25_quint_count": below_p25,
        "support_equal_quint_count": equal,
        "best_p31_id": best_any["p31_id"],
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
        "best_same_face_p31_id": best_same_face["p31_id"],
        "best_same_mask_spread": best_same_mask["joint_support_spread"],
        "best_same_mask_p31_id": best_same_mask["p31_id"],
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
    rows = build_p31_rows()
    top_table = table_from_rows(TOP_COLUMNS, rows["top_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    p25_report = load_json(P25_REPORT)
    p26_report = rows["p26_report"]
    p27_report = load_json(P27_REPORT)
    p28_report = load_json(P28_REPORT)
    p29_report = load_json(P29_REPORT)
    p30_report = load_json(P30_REPORT)
    checks = {
        "input_certificates_available": (
            p25_report.get("all_checks_pass") is True
            and p26_report.get("all_checks_pass") is True
            and p27_report.get("all_checks_pass") is True
            and p28_report.get("all_checks_pass") is True
            and p29_report.get("all_checks_pass") is True
            and p30_report.get("all_checks_pass") is True
        ),
        "complete_screen_size_matches_144_choose_5": (
            obs["p25_extension_count"],
            obs["pair_sum_count"],
            obs["triple_sum_count"],
            obs["quint_count"],
        )
        == (144, 10_296, 487_344, 481_008_528),
        "complete_five_move_beats_p29_floor": (
            obs["p30_bounded_floor"],
            obs["p29_quad_floor"],
            obs["p28_triple_floor"],
            obs["quint_min_spread"],
            obs["quint_min_below_p30_flag"],
            obs["quint_min_below_p29_flag"],
            obs["quint_min_below_p28_flag"],
        )
        == (4_213_120, 2_447_744, 2_601_984, 1_815_040, 1, 1, 1),
        "descent_counts_match": (
            obs["below_p30_quint_count"],
            obs["below_p29_quint_count"],
            obs["below_p28_quint_count"],
            obs["below_p27_quint_count"],
            obs["below_p25_quint_count"],
            obs["support_equal_quint_count"],
        )
        == (60, 2, 4, 2_734, 3_526, 0),
        "best_quint_matches_expected": (
            obs["best_p31_id"],
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
        == (19_527_470, 1, 8, 41, 52, 54, 12, 12, 12, 22, 22),
        "best_same_face_and_mask_match": (
            obs["best_same_face_spread"],
            obs["best_same_face_p31_id"],
            obs["best_same_mask_spread"],
            obs["best_same_mask_p31_id"],
        )
        == (3_384_704, 644_687, 3_384_704, 644_687),
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
        "classification": "complete_five_move_support_spread_descent",
        "p30_bounded_floor": obs["p30_bounded_floor"],
        "p29_quad_floor": obs["p29_quad_floor"],
        "p28_triple_floor": obs["p28_triple_floor"],
        "quint_min_spread": obs["quint_min_spread"],
        "below_p30_quint_count": obs["below_p30_quint_count"],
        "below_p29_quint_count": obs["below_p29_quint_count"],
        "below_p28_quint_count": obs["below_p28_quint_count"],
        "below_p27_quint_count": obs["below_p27_quint_count"],
        "below_p25_quint_count": obs["below_p25_quint_count"],
        "support_equal_quint_count": obs["support_equal_quint_count"],
        "compound_horizon_margin": obs["compound_horizon_margin"],
        "quint_count": obs["quint_count"],
        "best_quints": [
            {
                "rank": row["rank"],
                "p31_id": row["p31_id"],
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
            "The complete lifted five-move screen reopens metric descent below "
            "the p29 four-move floor, but still finds no raw support equalizer "
            "and preserves the p26 positive margin packet."
        ),
        "claim_boundary": {
            "complete_quint_screen": 1,
            "raw_support_equalizer_found": obs["support_equal_quint_count"],
            "p26_margin_preserved": obs["p26_margin_preserved_flag"],
            "universal_completion_claim": 0,
        },
        "top_table_sha256": sha_array(top_table),
        "observable_table_sha256": sha_array(obs_table),
    }
    p31 = {
        "schema": "eta6.p31@1",
        "object": "eta6",
        "construction": {
            "source": "eta6_p25 support vectors plus eta6_p29/p30 floors",
            "test": "complete five-move lifted compound support-spread screen",
            "classification": witness["classification"],
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.p31.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_P31_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "A complete five-move screen over the 144 eta6_p25 lifted pentagon "
            "extensions checks all 481008528 unordered quintuple compounds. "
            "Exactly two quintuples lower the p29 four-move floor, and the best "
            "spread is 1815040. No quintuple equalizes raw support. The p26 "
            "finite-horizon margins remain strict on the checked packet."
        ),
        "stage_protocol": {
            "draft": "start from eta6_p25 vectors, eta6_p29 floor, eta6_p30 bounded stall, and eta6_p26 margins",
            "witness": "enumerate all ordered-disjoint triple-pair combinations",
            "coherence": "compare joint support spread against p30, p29, p28, p27, and p25 floors while preserving p26 margins",
            "closure": "certify complete five-move lifted spread descent without raw-support equalization",
            "emit": "emit compact p31 artifacts and the next six-move seam",
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
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "p31": relpath(OUT_DIR / "p31.json"),
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
                "complete five-move screen over all 481008528 unordered p25 quintuples",
                "2 five-move compounds lower the p29 four-move floor",
                "best lifted five-move support spread is 1815040",
                "no five-move compound equalizes raw support",
                "p26 finite-horizon margins remain positive on the checked packet",
            ],
            "does_not_certify_because_false_or_open": [
                "a raw-support equalizer at five moves",
                "optimality over six or more p25 moves",
                "new simple-object semantics for the lifted carrier",
                "that eta6 is uncrossable outside the checked row universes",
            ],
        },
        "next_highest_yield_item": (
            "Start p32 with a seeded six-move screen from the two p31 minimizers "
            "and the below-p30 five-move frontier."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.p31.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.p31.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "p31": p31,
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
    write_json(OUT_DIR / "p31.json", payloads["p31"])
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
