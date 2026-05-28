from __future__ import annotations

import json
import math
from typing import Any

import numpy as np

try:
    from . import derive_eta6_p5 as p5
    from . import derive_eta6_p11 as p11
    from . import derive_eta6_p13 as p13
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
    import derive_eta6_p13 as p13
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "eta6_p14"
STATUS = "ETA6_P14_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

P5_REPORT = p5.OUT_DIR / "report.json"
P5_TABLES = p5.OUT_DIR / "tables.npz"
P11_REPORT = p11.OUT_DIR / "report.json"
P11_TABLES = p11.OUT_DIR / "tables.npz"
P13_REPORT = p13.OUT_DIR / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_p14.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_p14.py"

TOP_N = 32
BATCH_CELLS = 1_000_000
TOP_COLUMNS = [
    "rank",
    "p14_id",
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
    "below_p13_floor_flag",
    "below_p11_floor_flag",
    "below_p8_floor_flag",
    "below_p7_floor_flag",
    "below_p6_floor_flag",
    "below_p5_floor_flag",
    "support_equal_flag",
    "joint_mult_value",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBS_CODES = {
    "p5_extension_count": 0,
    "p11_seed_count": 1,
    "basin_move_count": 2,
    "basin_triple_count": 3,
    "basin_six_count": 4,
    "p5_single_floor": 5,
    "p6_pair_floor": 6,
    "p7_triple_floor": 7,
    "p8_quad_floor": 8,
    "p11_quint_floor": 9,
    "p13_top32_six_floor": 10,
    "basin_six_min_spread": 11,
    "basin_six_min_below_p13_flag": 12,
    "basin_six_min_below_p11_flag": 13,
    "basin_six_min_below_p8_flag": 14,
    "below_p13_candidate_count": 15,
    "below_p11_candidate_count": 16,
    "below_p8_candidate_count": 17,
    "below_p7_candidate_count": 18,
    "below_p6_candidate_count": 19,
    "below_p5_candidate_count": 20,
    "support_equal_candidate_count": 21,
    "same_face_candidate_count": 22,
    "same_mask_candidate_count": 23,
    "best_p14_id": 24,
    "best_p5_a": 25,
    "best_p5_b": 26,
    "best_p5_c": 27,
    "best_p5_d": 28,
    "best_p5_e": 29,
    "best_p5_f": 30,
    "best_same_face_spread": 31,
    "best_same_face_p14_id": 32,
    "best_same_mask_spread": 33,
    "best_same_mask_p14_id": 34,
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
    p14_id: int,
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
    p13_floor: int,
) -> dict[str, int]:
    joint = supports[list(row_indexes)].sum(axis=0)
    spread = int(joint.max() - joint.min())
    p5_ids = [int(ids[index]) for index in row_indexes]
    face_values = [int(faces[index]) for index in row_indexes]
    mask_values = [int(masks[index]) for index in row_indexes]
    return {
        "rank": rank,
        "p14_id": int(p14_id),
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
        "below_p13_floor_flag": int(spread < p13_floor),
        "below_p11_floor_flag": int(spread < p11_floor),
        "below_p8_floor_flag": int(spread < p8_floor),
        "below_p7_floor_flag": int(spread < p7_floor),
        "below_p6_floor_flag": int(spread < p6_floor),
        "below_p5_floor_flag": int(spread < p5_floor),
        "support_equal_flag": int(spread == 0),
        "joint_mult_value": int(mults[list(row_indexes)].sum()),
    }


def build_p14_rows() -> dict[str, Any]:
    p5_tables = np.load(P5_TABLES, allow_pickle=False)
    ext_rows = rows_from_table(
        np.asarray(p5_tables["ext_table"], dtype=np.int64),
        p5.EXT_COLUMNS,
    )
    p11_tables = np.load(P11_TABLES, allow_pickle=False)
    p11_rows = rows_from_table(
        np.asarray(p11_tables["top_table"], dtype=np.int64),
        p11.TOP_COLUMNS,
    )
    row_by_id = {row["p5_id"]: row for row in ext_rows}
    basin_ids = sorted(
        {
            row[column]
            for row in p11_rows
            for column in ("p5_a", "p5_b", "p5_c", "p5_d", "p5_e")
        }
    )
    basin_rows = [row_by_id[p5_id] for p5_id in basin_ids]
    supports = np.asarray(
        [
            [row[f"p{index}_support"] for index in range(5)]
            for row in basin_rows
        ],
        dtype=np.int64,
    )
    ids = np.asarray([row["p5_id"] for row in basin_rows], dtype=np.int64)
    faces = np.asarray([row["face_id"] for row in basin_rows], dtype=np.int64)
    masks = np.asarray([row["label_mask"] for row in basin_rows], dtype=np.int64)
    mults = np.asarray([row["mult_value"] for row in basin_rows], dtype=np.int64)

    p5_floor = min(row["support_spread"] for row in ext_rows)
    p6_floor = int(load_json(p11.P6_REPORT)["witness"]["pair_min_spread"])
    p7_floor = int(load_json(p11.P7_REPORT)["witness"]["triple_min_spread"])
    p8_floor = int(load_json(p11.P8_REPORT)["witness"]["quad_min_spread"])
    p11_floor = int(load_json(P11_REPORT)["witness"]["quint_min_spread"])
    p13_floor = int(load_json(P13_REPORT)["witness"]["top32_six_min_spread"])

    below_p13 = 0
    below_p11 = 0
    below_p8 = 0
    below_p7 = 0
    below_p6 = 0
    below_p5 = 0
    equal = 0
    same_face_count = 0
    same_mask_count = 0
    six_count = 0
    p14_base = 0
    low_rows: dict[tuple[int, ...], dict[str, int]] = {}
    best_any: dict[str, int] | None = None
    best_same_face: dict[str, int] | None = None
    best_same_mask: dict[str, int] | None = None
    n = len(basin_rows)

    def add_candidate(local_id: int, indexes: tuple[int, int, int, int, int, int]) -> None:
        nonlocal best_any, best_same_face, best_same_mask
        row = ranked_row(
            rank=0,
            p14_id=local_id,
            row_indexes=indexes,
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
            p13_floor=p13_floor,
        )
        key = (row["joint_support_spread"], row["p14_id"])
        if best_any is None or key < (
            best_any["joint_support_spread"],
            best_any["p14_id"],
        ):
            best_any = row
        if row["same_face_flag"] == 1 and (
            best_same_face is None
            or key
            < (
                best_same_face["joint_support_spread"],
                best_same_face["p14_id"],
            )
        ):
            best_same_face = row
        if row["same_mask_flag"] == 1 and (
            best_same_mask is None
            or key
            < (
                best_same_mask["joint_support_spread"],
                best_same_mask["p14_id"],
            )
        ):
            best_same_mask = row
        if row["joint_support_spread"] < p8_floor:
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

    for k in range(2, n - 3):
        left = np.asarray(
            [(first, second, k) for first in range(k - 1) for second in range(first + 1, k)],
            dtype=np.int16,
        )
        right = np.asarray(
            [
                (first, second, third)
                for first in range(k + 1, n - 2)
                for second in range(first + 1, n - 1)
                for third in range(second + 1, n)
            ],
            dtype=np.int16,
        )
        if len(left) == 0 or len(right) == 0:
            continue
        right_supports = (
            supports[right[:, 0]]
            + supports[right[:, 1]]
            + supports[right[:, 2]]
        )
        right_faces = faces[right]
        right_masks = masks[right]
        batch_size = max(1, min(len(left), BATCH_CELLS // len(right)))
        for start in range(0, len(left), batch_size):
            batch_left = left[start : start + batch_size]
            left_supports = (
                supports[batch_left[:, 0]]
                + supports[batch_left[:, 1]]
                + supports[batch_left[:, 2]]
            )
            sums = left_supports[:, None, :] + right_supports[None, :, :]
            spreads = sums.max(axis=2) - sums.min(axis=2)
            six_count += int(spreads.size)
            below_p13 += int((spreads < p13_floor).sum())
            below_p11 += int((spreads < p11_floor).sum())
            below_p8 += int((spreads < p8_floor).sum())
            below_p7 += int((spreads < p7_floor).sum())
            below_p6 += int((spreads < p6_floor).sum())
            below_p5 += int((spreads < p5_floor).sum())
            equal += int((spreads == 0).sum())

            candidates: set[tuple[int, int]] = {
                np.unravel_index(int(spreads.argmin()), spreads.shape)
            }
            left_faces = faces[batch_left]
            same_face = (
                (left_faces[:, [0]] == left_faces[:, [1]])
                & (left_faces[:, [0]] == left_faces[:, [2]])
                & (left_faces[:, [0]] == right_faces[None, :, 0])
                & (left_faces[:, [0]] == right_faces[None, :, 1])
                & (left_faces[:, [0]] == right_faces[None, :, 2])
            )
            same_face_count += int(same_face.sum())
            if bool(same_face.any()):
                candidates.add(
                    np.unravel_index(
                        int(np.where(same_face, spreads, np.iinfo(np.int64).max).argmin()),
                        spreads.shape,
                    )
                )
            left_masks = masks[batch_left]
            same_mask = (
                (left_masks[:, [0]] == left_masks[:, [1]])
                & (left_masks[:, [0]] == left_masks[:, [2]])
                & (left_masks[:, [0]] == right_masks[None, :, 0])
                & (left_masks[:, [0]] == right_masks[None, :, 1])
                & (left_masks[:, [0]] == right_masks[None, :, 2])
            )
            same_mask_count += int(same_mask.sum())
            if bool(same_mask.any()):
                candidates.add(
                    np.unravel_index(
                        int(np.where(same_mask, spreads, np.iinfo(np.int64).max).argmin()),
                        spreads.shape,
                    )
                )
            candidates.update(
                (int(left_index), int(right_index))
                for left_index, right_index in np.argwhere(spreads < p8_floor)
            )
            right_count = len(right)
            for batch_index, right_index in candidates:
                indexes = tuple(int(value) for value in batch_left[batch_index]) + tuple(
                    int(value) for value in right[right_index]
                )
                add_candidate(
                    p14_base + (start + int(batch_index)) * right_count + int(right_index),
                    indexes,
                )
        p14_base += int(len(left) * len(right))

    if best_any is None or best_same_face is None or best_same_mask is None:
        raise ValueError("empty p14 search")
    top_rows = sorted(
        low_rows.values(),
        key=lambda row: (row["joint_support_spread"], row["p14_id"]),
    )[:TOP_N]
    if len(top_rows) != TOP_N:
        raise ValueError("p14 top row capture is too small")
    for rank, row in enumerate(top_rows):
        row["rank"] = rank

    obs = {
        "p5_extension_count": len(ext_rows),
        "p11_seed_count": len(p11_rows),
        "basin_move_count": n,
        "basin_triple_count": math.comb(n, 3),
        "basin_six_count": six_count,
        "p5_single_floor": p5_floor,
        "p6_pair_floor": p6_floor,
        "p7_triple_floor": p7_floor,
        "p8_quad_floor": p8_floor,
        "p11_quint_floor": p11_floor,
        "p13_top32_six_floor": p13_floor,
        "basin_six_min_spread": best_any["joint_support_spread"],
        "basin_six_min_below_p13_flag": int(best_any["joint_support_spread"] < p13_floor),
        "basin_six_min_below_p11_flag": int(best_any["joint_support_spread"] < p11_floor),
        "basin_six_min_below_p8_flag": int(best_any["joint_support_spread"] < p8_floor),
        "below_p13_candidate_count": below_p13,
        "below_p11_candidate_count": below_p11,
        "below_p8_candidate_count": below_p8,
        "below_p7_candidate_count": below_p7,
        "below_p6_candidate_count": below_p6,
        "below_p5_candidate_count": below_p5,
        "support_equal_candidate_count": equal,
        "same_face_candidate_count": same_face_count,
        "same_mask_candidate_count": same_mask_count,
        "best_p14_id": best_any["p14_id"],
        "best_p5_a": best_any["p5_a"],
        "best_p5_b": best_any["p5_b"],
        "best_p5_c": best_any["p5_c"],
        "best_p5_d": best_any["p5_d"],
        "best_p5_e": best_any["p5_e"],
        "best_p5_f": best_any["p5_f"],
        "best_same_face_spread": best_same_face["joint_support_spread"],
        "best_same_face_p14_id": best_same_face["p14_id"],
        "best_same_mask_spread": best_same_mask["joint_support_spread"],
        "best_same_mask_p14_id": best_same_mask["p14_id"],
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
        "basin_ids": basin_ids,
    }


def best_rows_for_witness(rows: list[dict[str, int]]) -> list[dict[str, Any]]:
    return [
        {
            "rank": row["rank"],
            "p14_id": row["p14_id"],
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
    rows = build_p14_rows()
    top_table = table_from_rows(TOP_COLUMNS, rows["top_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    p5_report = load_json(P5_REPORT)
    p11_report = load_json(P11_REPORT)
    p13_report = load_json(P13_REPORT)
    checks = {
        "input_certificates_available": (
            p5_report.get("all_checks_pass") is True
            and p11_report.get("all_checks_pass") is True
            and p13_report.get("all_checks_pass") is True
        ),
        "basin_size_matches": (
            obs["p5_extension_count"],
            obs["p11_seed_count"],
            obs["basin_move_count"],
            obs["basin_triple_count"],
            obs["basin_six_count"],
        )
        == (144, 32, 76, 70_300, 218_618_940),
        "basin_six_beats_p13_and_p11": (
            obs["p13_top32_six_floor"],
            obs["p11_quint_floor"],
            obs["p8_quad_floor"],
            obs["basin_six_min_spread"],
            obs["basin_six_min_below_p13_flag"],
            obs["basin_six_min_below_p11_flag"],
            obs["basin_six_min_below_p8_flag"],
        )
        == (7_982_592, 1_815_040, 2_447_744, 1_164_096, 1, 1, 1),
        "descent_counts_match": (
            obs["below_p13_candidate_count"],
            obs["below_p11_candidate_count"],
            obs["below_p8_candidate_count"],
            obs["below_p7_candidate_count"],
            obs["below_p6_candidate_count"],
            obs["below_p5_candidate_count"],
            obs["support_equal_candidate_count"],
        )
        == (3_121, 15, 39, 49, 9_237, 11_947, 0),
        "same_face_and_mask_counts_match": (
            obs["same_face_candidate_count"],
            obs["same_mask_candidate_count"],
        )
        == (4_068_820, 4_068_820),
        "best_candidate_matches_expected": (
            obs["best_p14_id"],
            obs["best_p5_a"],
            obs["best_p5_b"],
            obs["best_p5_c"],
            obs["best_p5_d"],
            obs["best_p5_e"],
            obs["best_p5_f"],
        )
        == (21_230_492, 6, 12, 19, 29, 94, 96),
        "best_same_face_and_mask_match": (
            obs["best_same_face_spread"],
            obs["best_same_face_p14_id"],
            obs["best_same_mask_spread"],
            obs["best_same_mask_p14_id"],
        )
        == (2_644_672, 25_917_422, 2_644_672, 25_917_422),
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
        "classification": "p11_basin_exact_six_move_search",
        "candidate_construction": (
            "exact pair/triple split over the union of p5 ids appearing in the "
            "p11 top-32 quintuples"
        ),
        "basin_ids": rows["basin_ids"],
        "p13_top32_six_floor": obs["p13_top32_six_floor"],
        "p11_quint_floor": obs["p11_quint_floor"],
        "basin_six_min_spread": obs["basin_six_min_spread"],
        "below_p13_candidate_count": obs["below_p13_candidate_count"],
        "below_p11_candidate_count": obs["below_p11_candidate_count"],
        "below_p8_candidate_count": obs["below_p8_candidate_count"],
        "below_p7_candidate_count": obs["below_p7_candidate_count"],
        "below_p6_candidate_count": obs["below_p6_candidate_count"],
        "below_p5_candidate_count": obs["below_p5_candidate_count"],
        "support_equal_candidate_count": obs["support_equal_candidate_count"],
        "same_face_candidate_count": obs["same_face_candidate_count"],
        "same_mask_candidate_count": obs["same_mask_candidate_count"],
        "best_candidates": best_rows_for_witness(rows["top_rows"][:16]),
        "reading": (
            "The exact p11-basin six-move search beats both the p13 exact "
            "top-32 extension floor and the p11 five-move floor, but still "
            "finds no raw-support equalizer."
        ),
        "top_table_sha256": sha_array(top_table),
        "observable_table_sha256": sha_array(obs_table),
    }
    p14 = {
        "schema": "eta6.p14@1",
        "object": "eta6",
        "construction": {
            "source": "p11 top-32 p5-id union",
            "test": "exact six-move basin pair/triple screen",
            "classification": witness["classification"],
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.p14.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_P14_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The exact 76-move p11-basin six-move search lowers best support "
            "spread to 1164096, beating p13 and p11, while no basin sextuple "
            "equalizes raw support."
        ),
        "stage_protocol": {
            "draft": "take the p5-id union of the p11 top-32 quintuples",
            "witness": "enumerate all basin sextuples by a pair/triple split",
            "coherence": "compare the exact basin floor against p13, p11, p8, p7, p6, and p5 floors",
            "closure": "certify exact basin metric descent without support equalization",
            "emit": "emit compact p14 artifacts and the next seam",
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
            "p11_report": input_entry(
                P11_REPORT,
                {
                    "status": p11_report.get("status"),
                    "certificate_sha256": p11_report.get("certificate_sha256"),
                },
            ),
            "p11_tables": input_entry(P11_TABLES),
            "p13_report": input_entry(
                P13_REPORT,
                {
                    "status": p13_report.get("status"),
                    "certificate_sha256": p13_report.get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "p14": relpath(OUT_DIR / "p14.json"),
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
                "exact six-move search over the 76 p5 rows in the p11 top-32 basin",
                "218618940 basin sextuples checked",
                "best basin six-move support spread is 1164096",
                "15 basin sextuples beat the p11 five-move floor",
                "no basin sextuple equalizes raw support",
            ],
            "does_not_certify_because_out_of_scope": [
                "complete six-move search over all 144 p5 rows",
                "a new post-surgery carrier-level eta6 gap",
                "global closure under repeated non-cubic surgeries",
                "that metric conductance has reached its final asymptote",
            ],
        },
        "next_highest_yield_item": (
            "Run p15 as a full-144 centered pair/triple nearest-neighbor screen, "
            "then promote any sub-p14 winner to the carrier-level margin test."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.p14.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.p14.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "p14": p14,
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
    write_json(OUT_DIR / "p14.json", payloads["p14"])
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
