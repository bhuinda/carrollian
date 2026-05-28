from __future__ import annotations

import json
import math
from typing import Any

import numpy as np

try:
    from . import derive_eta6_p5 as p5
    from . import derive_eta6_p6 as p6
    from . import derive_eta6_p7 as p7
    from . import derive_eta6_p8 as p8
    from . import derive_eta6_p9 as p9
    from . import derive_eta6_p10 as p10
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
    import derive_eta6_p6 as p6
    import derive_eta6_p7 as p7
    import derive_eta6_p8 as p8
    import derive_eta6_p9 as p9
    import derive_eta6_p10 as p10
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "eta6_p11"
STATUS = "ETA6_P11_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

P5_REPORT = p5.OUT_DIR / "report.json"
P5_TABLES = p5.OUT_DIR / "tables.npz"
P6_REPORT = p6.OUT_DIR / "report.json"
P7_REPORT = p7.OUT_DIR / "report.json"
P8_REPORT = p8.OUT_DIR / "report.json"
P9_REPORT = p9.OUT_DIR / "report.json"
P10_REPORT = p10.OUT_DIR / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_p11.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_p11.py"

TOP_N = 32
BATCH_SIZE = 256
TOP_COLUMNS = [
    "rank",
    "p11_id",
    "p5_a",
    "p5_b",
    "p5_c",
    "p5_d",
    "p5_e",
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
    "below_p10_floor_flag",
    "below_p9_floor_flag",
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
    "pair_count": 1,
    "triple_count": 2,
    "quint_count": 3,
    "p5_single_floor": 4,
    "p6_pair_floor": 5,
    "p7_triple_floor": 6,
    "p8_quad_floor": 7,
    "p9_bounded_floor": 8,
    "p10_shadow_floor": 9,
    "quint_min_spread": 10,
    "quint_min_below_p10_flag": 11,
    "quint_min_below_p9_flag": 12,
    "quint_min_below_p8_flag": 13,
    "below_p10_candidate_count": 14,
    "below_p9_candidate_count": 15,
    "below_p8_candidate_count": 16,
    "below_p7_candidate_count": 17,
    "below_p6_candidate_count": 18,
    "below_p5_candidate_count": 19,
    "support_equal_candidate_count": 20,
    "best_p11_id": 21,
    "best_p5_a": 22,
    "best_p5_b": 23,
    "best_p5_c": 24,
    "best_p5_d": 25,
    "best_p5_e": 26,
    "best_face_a": 27,
    "best_face_b": 28,
    "best_face_c": 29,
    "best_face_d": 30,
    "best_face_e": 31,
    "best_same_face_spread": 32,
    "best_same_face_p11_id": 33,
    "best_same_mask_spread": 34,
    "best_same_mask_p11_id": 35,
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
    p11_id: int,
    row_indexes: tuple[int, int, int, int, int],
    supports: np.ndarray,
    ids: np.ndarray,
    faces: np.ndarray,
    masks: np.ndarray,
    mults: np.ndarray,
    p5_floor: int,
    p6_floor: int,
    p7_floor: int,
    p8_floor: int,
    p9_floor: int,
    p10_floor: int,
) -> dict[str, int]:
    joint = supports[list(row_indexes)].sum(axis=0)
    spread = int(joint.max() - joint.min())
    p5_ids = [int(ids[index]) for index in row_indexes]
    face_values = [int(faces[index]) for index in row_indexes]
    mask_values = [int(masks[index]) for index in row_indexes]
    return {
        "rank": rank,
        "p11_id": int(p11_id),
        "p5_a": p5_ids[0],
        "p5_b": p5_ids[1],
        "p5_c": p5_ids[2],
        "p5_d": p5_ids[3],
        "p5_e": p5_ids[4],
        "face_a": face_values[0],
        "face_b": face_values[1],
        "face_c": face_values[2],
        "face_d": face_values[3],
        "face_e": face_values[4],
        "mask_a": mask_values[0],
        "mask_b": mask_values[1],
        "mask_c": mask_values[2],
        "mask_d": mask_values[3],
        "mask_e": mask_values[4],
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
        "below_p10_floor_flag": int(spread < p10_floor),
        "below_p9_floor_flag": int(spread < p9_floor),
        "below_p8_floor_flag": int(spread < p8_floor),
        "below_p7_floor_flag": int(spread < p7_floor),
        "below_p6_floor_flag": int(spread < p6_floor),
        "below_p5_floor_flag": int(spread < p5_floor),
        "support_equal_flag": int(spread == 0),
        "joint_mult_value": int(mults[list(row_indexes)].sum()),
    }


def build_p11_rows() -> dict[str, Any]:
    p5_tables = np.load(P5_TABLES, allow_pickle=False)
    ext_table = np.asarray(p5_tables["ext_table"], dtype=np.int64)
    ext_rows = rows_from_table(ext_table, p5.EXT_COLUMNS)
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

    p5_floor = min(row["support_spread"] for row in ext_rows)
    p6_floor = int(load_json(P6_REPORT)["witness"]["pair_min_spread"])
    p7_floor = int(load_json(P7_REPORT)["witness"]["triple_min_spread"])
    p8_floor = int(load_json(P8_REPORT)["witness"]["quad_min_spread"])
    p9_floor = int(load_json(P9_REPORT)["witness"]["bounded_min_spread"])
    p10_floor = int(load_json(P10_REPORT)["witness"]["shadow_min_spread"])

    floors = [p10_floor, p9_floor, p8_floor, p7_floor, p6_floor, p5_floor]
    below = [0, 0, 0, 0, 0, 0]
    equal = 0
    p11_id = 0
    quint_count = 0
    low_rows: dict[tuple[int, ...], dict[str, int]] = {}
    best_any: dict[str, int] | None = None
    best_same_face: dict[str, int] | None = None
    best_same_mask: dict[str, int] | None = None
    n = len(ext_rows)

    def add_candidate(local_id: int, indexes: tuple[int, int, int, int, int]) -> None:
        nonlocal best_any, best_same_face, best_same_mask
        row = ranked_row(
            rank=0,
            p11_id=local_id,
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
            p9_floor=p9_floor,
            p10_floor=p10_floor,
        )
        key = (row["joint_support_spread"], row["p11_id"])
        if best_any is None or key < (
            best_any["joint_support_spread"],
            best_any["p11_id"],
        ):
            best_any = row
        if row["same_face_flag"] == 1 and (
            best_same_face is None
            or key
            < (
                best_same_face["joint_support_spread"],
                best_same_face["p11_id"],
            )
        ):
            best_same_face = row
        if row["same_mask_flag"] == 1 and (
            best_same_mask is None
            or key
            < (
                best_same_mask["joint_support_spread"],
                best_same_mask["p11_id"],
            )
        ):
            best_same_mask = row
        if row["joint_support_spread"] < p9_floor:
            low_rows[
                (
                    row["p5_a"],
                    row["p5_b"],
                    row["p5_c"],
                    row["p5_d"],
                    row["p5_e"],
                )
            ] = row

    for k in range(2, n - 2):
        pairs = np.asarray(
            [(left, right) for left in range(k + 1, n - 1) for right in range(left + 1, n)],
            dtype=np.int16,
        )
        if len(pairs) == 0:
            continue
        pair_supports = supports[pairs[:, 0]] + supports[pairs[:, 1]]
        pair_faces = faces[pairs]
        pair_masks = masks[pairs]
        triples = np.asarray(
            [(left, mid, k) for left in range(k - 1) for mid in range(left + 1, k)],
            dtype=np.int16,
        )
        triple_supports = (
            supports[triples[:, 0]]
            + supports[triples[:, 1]]
            + supports[triples[:, 2]]
        )
        for start in range(0, len(triples), BATCH_SIZE):
            batch_triples = triples[start : start + BATCH_SIZE]
            sums = triple_supports[start : start + BATCH_SIZE, None, :] + pair_supports[None, :, :]
            spreads = sums.max(axis=2) - sums.min(axis=2)
            quint_count += int(spreads.size)
            for index, floor in enumerate(floors):
                below[index] += int((spreads < floor).sum())
            equal += int((spreads == 0).sum())

            candidates: set[tuple[int, int]] = {
                np.unravel_index(int(spreads.argmin()), spreads.shape)
            }
            batch_faces = faces[batch_triples]
            same_face = (
                (batch_faces[:, [0]] == batch_faces[:, [1]])
                & (batch_faces[:, [0]] == batch_faces[:, [2]])
                & (batch_faces[:, [0]] == pair_faces[None, :, 0])
                & (batch_faces[:, [0]] == pair_faces[None, :, 1])
            )
            if bool(same_face.any()):
                candidates.add(
                    np.unravel_index(
                        int(np.where(same_face, spreads, np.iinfo(np.int64).max).argmin()),
                        spreads.shape,
                    )
                )
            batch_masks = masks[batch_triples]
            same_mask = (
                (batch_masks[:, [0]] == batch_masks[:, [1]])
                & (batch_masks[:, [0]] == batch_masks[:, [2]])
                & (batch_masks[:, [0]] == pair_masks[None, :, 0])
                & (batch_masks[:, [0]] == pair_masks[None, :, 1])
            )
            if bool(same_mask.any()):
                candidates.add(
                    np.unravel_index(
                        int(np.where(same_mask, spreads, np.iinfo(np.int64).max).argmin()),
                        spreads.shape,
                    )
                )
            for batch_index, pair_index in np.argwhere(spreads < p9_floor):
                candidates.add((int(batch_index), int(pair_index)))

            base_id = p11_id
            pair_count = len(pairs)
            for batch_index, pair_index in candidates:
                indexes = tuple(int(value) for value in batch_triples[batch_index]) + tuple(
                    int(value) for value in pairs[pair_index]
                )
                add_candidate(base_id + batch_index * pair_count + pair_index, indexes)
            p11_id += int(len(batch_triples) * pair_count)

    if best_any is None or best_same_face is None or best_same_mask is None:
        raise ValueError("empty p11 search")
    top_rows = sorted(
        low_rows.values(),
        key=lambda row: (row["joint_support_spread"], row["p11_id"]),
    )[:TOP_N]
    for rank, row in enumerate(top_rows):
        row["rank"] = rank

    obs = {
        "p5_extension_count": n,
        "pair_count": math.comb(n, 2),
        "triple_count": math.comb(n, 3),
        "quint_count": quint_count,
        "p5_single_floor": p5_floor,
        "p6_pair_floor": p6_floor,
        "p7_triple_floor": p7_floor,
        "p8_quad_floor": p8_floor,
        "p9_bounded_floor": p9_floor,
        "p10_shadow_floor": p10_floor,
        "quint_min_spread": best_any["joint_support_spread"],
        "quint_min_below_p10_flag": int(best_any["joint_support_spread"] < p10_floor),
        "quint_min_below_p9_flag": int(best_any["joint_support_spread"] < p9_floor),
        "quint_min_below_p8_flag": int(best_any["joint_support_spread"] < p8_floor),
        "below_p10_candidate_count": below[0],
        "below_p9_candidate_count": below[1],
        "below_p8_candidate_count": below[2],
        "below_p7_candidate_count": below[3],
        "below_p6_candidate_count": below[4],
        "below_p5_candidate_count": below[5],
        "support_equal_candidate_count": equal,
        "best_p11_id": best_any["p11_id"],
        "best_p5_a": best_any["p5_a"],
        "best_p5_b": best_any["p5_b"],
        "best_p5_c": best_any["p5_c"],
        "best_p5_d": best_any["p5_d"],
        "best_p5_e": best_any["p5_e"],
        "best_face_a": best_any["face_a"],
        "best_face_b": best_any["face_b"],
        "best_face_c": best_any["face_c"],
        "best_face_d": best_any["face_d"],
        "best_face_e": best_any["face_e"],
        "best_same_face_spread": best_same_face["joint_support_spread"],
        "best_same_face_p11_id": best_same_face["p11_id"],
        "best_same_mask_spread": best_same_mask["joint_support_spread"],
        "best_same_mask_p11_id": best_same_mask["p11_id"],
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
    }


def best_rows_for_witness(rows: list[dict[str, int]]) -> list[dict[str, Any]]:
    return [
        {
            "rank": row["rank"],
            "p11_id": row["p11_id"],
            "p5_ids": [
                row["p5_a"],
                row["p5_b"],
                row["p5_c"],
                row["p5_d"],
                row["p5_e"],
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
        for row in rows
    ]


def build_payloads() -> dict[str, Any]:
    rows = build_p11_rows()
    top_table = table_from_rows(TOP_COLUMNS, rows["top_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    p5_report = load_json(P5_REPORT)
    p6_report = load_json(P6_REPORT)
    p7_report = load_json(P7_REPORT)
    p8_report = load_json(P8_REPORT)
    p9_report = load_json(P9_REPORT)
    p10_report = load_json(P10_REPORT)
    checks = {
        "input_certificates_available": (
            p5_report.get("all_checks_pass") is True
            and p6_report.get("all_checks_pass") is True
            and p7_report.get("all_checks_pass") is True
            and p8_report.get("all_checks_pass") is True
            and p9_report.get("all_checks_pass") is True
            and p10_report.get("all_checks_pass") is True
        ),
        "complete_five_move_size_matches_144_choose_5": (
            obs["p5_extension_count"],
            obs["pair_count"],
            obs["triple_count"],
            obs["quint_count"],
        )
        == (144, 10_296, 487_344, 481_008_528),
        "five_move_beats_p8_floor": (
            obs["p10_shadow_floor"],
            obs["p9_bounded_floor"],
            obs["p8_quad_floor"],
            obs["quint_min_spread"],
            obs["quint_min_below_p10_flag"],
            obs["quint_min_below_p9_flag"],
            obs["quint_min_below_p8_flag"],
        )
        == (4_213_120, 5_601_664, 2_447_744, 1_815_040, 1, 1, 1),
        "descent_counts_match": (
            obs["below_p10_candidate_count"],
            obs["below_p9_candidate_count"],
            obs["below_p8_candidate_count"],
            obs["below_p7_candidate_count"],
            obs["below_p6_candidate_count"],
            obs["below_p5_candidate_count"],
            obs["support_equal_candidate_count"],
        )
        == (60, 226, 2, 4, 2_734, 3_526, 0),
        "best_candidate_matches_expected": (
            obs["best_p11_id"],
            obs["best_p5_a"],
            obs["best_p5_b"],
            obs["best_p5_c"],
            obs["best_p5_d"],
            obs["best_p5_e"],
            obs["best_face_a"],
            obs["best_face_b"],
            obs["best_face_c"],
            obs["best_face_d"],
            obs["best_face_e"],
        )
        == (67_415_100, 1, 8, 41, 52, 54, 12, 12, 12, 22, 22),
        "best_same_face_and_mask_match": (
            obs["best_same_face_spread"],
            obs["best_same_face_p11_id"],
            obs["best_same_mask_spread"],
            obs["best_same_mask_p11_id"],
        )
        == (3_384_704, 15_777_042, 3_384_704, 15_777_042),
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
        "candidate_construction": "canonical exact i<j<k<l<m scan over all p5 quintuple compounds",
        "p8_quad_floor": obs["p8_quad_floor"],
        "p9_bounded_floor": obs["p9_bounded_floor"],
        "p10_shadow_floor": obs["p10_shadow_floor"],
        "quint_min_spread": obs["quint_min_spread"],
        "below_p10_candidate_count": obs["below_p10_candidate_count"],
        "below_p9_candidate_count": obs["below_p9_candidate_count"],
        "below_p8_candidate_count": obs["below_p8_candidate_count"],
        "below_p7_candidate_count": obs["below_p7_candidate_count"],
        "below_p6_candidate_count": obs["below_p6_candidate_count"],
        "below_p5_candidate_count": obs["below_p5_candidate_count"],
        "support_equal_candidate_count": obs["support_equal_candidate_count"],
        "best_candidates": best_rows_for_witness(rows["top_rows"][:16]),
        "reading": (
            "The complete five-move screen beats the p8 four-move floor, so "
            "p8 was not the metric floor. Raw support still never equalizes."
        ),
        "top_table_sha256": sha_array(top_table),
        "observable_table_sha256": sha_array(obs_table),
    }
    p11 = {
        "schema": "eta6.p11@1",
        "object": "eta6",
        "construction": {
            "source": "eta6_p5 support vectors",
            "test": "complete five-move eta6-preserving compound support-spread screen",
            "classification": witness["classification"],
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.p11.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_P11_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The complete five-move eta6-preserving compound screen over "
            "481008528 p5 quintuples beats the p8 four-move floor: the best "
            "spread is 1815040, with two candidates below p8. No five-move "
            "candidate equalizes raw support."
        ),
        "stage_protocol": {
            "draft": "start from the 144 eta6_p5 support vectors",
            "witness": "scan every canonical unordered five-move compound exactly",
            "coherence": "compare full five-move spread against p10, p9, p8, p7, p6, and p5 floors",
            "closure": "certify full five-move metric descent without support equalization",
            "emit": "emit compact p11 artifacts and the next seam",
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
            "p9_report": input_entry(
                P9_REPORT,
                {
                    "status": p9_report.get("status"),
                    "certificate_sha256": p9_report.get("certificate_sha256"),
                },
            ),
            "p10_report": input_entry(
                P10_REPORT,
                {
                    "status": p10_report.get("status"),
                    "certificate_sha256": p10_report.get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "p11": relpath(OUT_DIR / "p11.json"),
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
                "complete five-move screen over all 481008528 unordered p5 quintuples",
                "2 five-move candidates beat the p8 four-move floor",
                "best five-move support spread is 1815040",
                "no five-move candidate equalizes raw support",
            ],
            "does_not_certify_because_out_of_scope": [
                "support equalization at six or more p5 moves",
                "point-level geometric surgery on the p2 carrier",
                "global closure under repeated non-cubic surgeries",
                "that metric conductance has reached its final asymptote",
            ],
        },
        "next_highest_yield_item": (
            "Use the two p8-beating p11 rows as seeds for a six-move extension "
            "screen and a carrier-level eta6 gap check."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.p11.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.p11.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "p11": p11,
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
    write_json(OUT_DIR / "p11.json", payloads["p11"])
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
