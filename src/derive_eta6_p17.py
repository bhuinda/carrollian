from __future__ import annotations

import itertools
import json
from collections import Counter
from typing import Any

import numpy as np

try:
    from . import derive_eta6_p5 as p5
    from . import derive_eta6_p11 as p11
    from . import derive_eta6_p15 as p15
    from . import derive_eta6_p16 as p16
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
    import derive_eta6_p15 as p15
    import derive_eta6_p16 as p16
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "eta6_p17"
STATUS = "ETA6_P17_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

P5_REPORT = p5.OUT_DIR / "report.json"
P5_TABLES = p5.OUT_DIR / "tables.npz"
P6_REPORT = p11.P6_REPORT
P7_REPORT = p11.P7_REPORT
P8_REPORT = p11.P8_REPORT
P11_REPORT = p11.OUT_DIR / "report.json"
P15_REPORT = p15.OUT_DIR / "report.json"
P16_REPORT = p16.OUT_DIR / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_eta6_p17.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_eta6_p17.py"

TOP_N = 32
BATCH_SIZE = 256
BALANCE_CLASSES = ((12, 30), (22, 45), (26, 51))
TOP_COLUMNS = [
    "rank",
    "p17_id",
    "p5_a",
    "p5_b",
    "p5_c",
    "p5_d",
    "p5_e",
    "p5_f",
    "joint_p0_support",
    "joint_p1_support",
    "joint_p2_support",
    "joint_p3_support",
    "joint_p4_support",
    "joint_support_min",
    "joint_support_max",
    "joint_support_spread",
    "below_p15_floor_flag",
    "below_p14_floor_flag",
    "below_p11_floor_flag",
    "below_p8_floor_flag",
    "below_p7_floor_flag",
    "below_p6_floor_flag",
    "below_p5_floor_flag",
    "support_equal_flag",
    "total_f4_delta",
    "abs_total_f4_delta",
    "per_face_delta_zero_flag",
    "joint_mult_value",
]
CLASS_COLUMNS = [
    "class_id",
    "face_id",
    "label_mask",
    "move_count",
    "pair_count",
    "zero_delta_pair_count",
    "unique_pair_delta_count",
    "min_abs_pair_delta",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBS_CODES = {
    "class_count": 0,
    "moves_per_class": 1,
    "pairs_per_class": 2,
    "balance_candidate_count": 3,
    "p5_single_floor": 4,
    "p6_pair_floor": 5,
    "p7_triple_floor": 6,
    "p8_quad_floor": 7,
    "p11_quint_floor": 8,
    "p14_basin_six_floor": 9,
    "p15_grid_floor": 10,
    "balance_min_spread": 11,
    "balance_min_equal_p15_flag": 12,
    "below_p15_candidate_count": 13,
    "at_p15_floor_candidate_count": 14,
    "below_p14_candidate_count": 15,
    "below_p11_candidate_count": 16,
    "below_p8_candidate_count": 17,
    "below_p7_candidate_count": 18,
    "below_p6_candidate_count": 19,
    "below_p5_candidate_count": 20,
    "support_equal_candidate_count": 21,
    "total_delta_zero_candidate_count": 22,
    "per_face_delta_zero_candidate_count": 23,
    "best_p17_id": 24,
    "best_p5_a": 25,
    "best_p5_b": 26,
    "best_p5_c": 27,
    "best_p5_d": 28,
    "best_p5_e": 29,
    "best_p5_f": 30,
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


def pair_table(
    group: list[dict[str, int]],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    pairs = []
    supports = []
    deltas = []
    mults = []
    for left, right in itertools.combinations(group, 2):
        pairs.append((left["p5_id"], right["p5_id"]))
        supports.append(
            [
                left[f"p{index}_support"] + right[f"p{index}_support"]
                for index in range(5)
            ]
        )
        deltas.append(left["f4_delta"] + right["f4_delta"])
        mults.append(left["mult_value"] + right["mult_value"])
    return (
        np.asarray(pairs, dtype=np.int16),
        np.asarray(supports, dtype=np.int64),
        np.asarray(deltas, dtype=np.int64),
        np.asarray(mults, dtype=np.int64),
    )


def candidate_row(
    *,
    rank: int,
    p17_id: int,
    p5_ids: tuple[int, int, int, int, int, int],
    joint: np.ndarray,
    total_delta: int,
    per_face_delta_zero: bool,
    joint_mult: int,
    p5_floor: int,
    p6_floor: int,
    p7_floor: int,
    p8_floor: int,
    p11_floor: int,
    p14_floor: int,
    p15_floor: int,
) -> dict[str, int]:
    spread = int(joint.max() - joint.min())
    return {
        "rank": rank,
        "p17_id": p17_id,
        "p5_a": p5_ids[0],
        "p5_b": p5_ids[1],
        "p5_c": p5_ids[2],
        "p5_d": p5_ids[3],
        "p5_e": p5_ids[4],
        "p5_f": p5_ids[5],
        "joint_p0_support": int(joint[0]),
        "joint_p1_support": int(joint[1]),
        "joint_p2_support": int(joint[2]),
        "joint_p3_support": int(joint[3]),
        "joint_p4_support": int(joint[4]),
        "joint_support_min": int(joint.min()),
        "joint_support_max": int(joint.max()),
        "joint_support_spread": spread,
        "below_p15_floor_flag": int(spread < p15_floor),
        "below_p14_floor_flag": int(spread < p14_floor),
        "below_p11_floor_flag": int(spread < p11_floor),
        "below_p8_floor_flag": int(spread < p8_floor),
        "below_p7_floor_flag": int(spread < p7_floor),
        "below_p6_floor_flag": int(spread < p6_floor),
        "below_p5_floor_flag": int(spread < p5_floor),
        "support_equal_flag": int(spread == 0),
        "total_f4_delta": int(total_delta),
        "abs_total_f4_delta": abs(int(total_delta)),
        "per_face_delta_zero_flag": int(per_face_delta_zero),
        "joint_mult_value": int(joint_mult),
    }


def build_p17_rows() -> dict[str, Any]:
    p5_tables = np.load(P5_TABLES, allow_pickle=False)
    ext_rows = rows_from_table(
        np.asarray(p5_tables["ext_table"], dtype=np.int64),
        p5.EXT_COLUMNS,
    )
    groups = [
        [
            row
            for row in ext_rows
            if (row["face_id"], row["label_mask"]) == face_mask
        ]
        for face_mask in BALANCE_CLASSES
    ]
    pair_payloads = [pair_table(group) for group in groups]
    class_rows = []
    for class_id, (face_mask, group, payload) in enumerate(
        zip(BALANCE_CLASSES, groups, pair_payloads)
    ):
        _, _, deltas, _ = payload
        delta_counts = Counter(int(value) for value in deltas)
        class_rows.append(
            {
                "class_id": class_id,
                "face_id": face_mask[0],
                "label_mask": face_mask[1],
                "move_count": len(group),
                "pair_count": len(deltas),
                "zero_delta_pair_count": delta_counts[0],
                "unique_pair_delta_count": len(delta_counts),
                "min_abs_pair_delta": min(abs(int(value)) for value in deltas),
            }
        )

    p5_floor = min(row["support_spread"] for row in ext_rows)
    p6_floor = int(load_json(P6_REPORT)["witness"]["pair_min_spread"])
    p7_floor = int(load_json(P7_REPORT)["witness"]["triple_min_spread"])
    p8_floor = int(load_json(P8_REPORT)["witness"]["quad_min_spread"])
    p11_floor = int(load_json(P11_REPORT)["witness"]["quint_min_spread"])
    p14_floor = int(load_json(p15.P14_REPORT)["witness"]["basin_six_min_spread"])
    p15_floor = int(load_json(P15_REPORT)["witness"]["grid_min_spread"])

    pairs_a, sums_a, deltas_a, mults_a = pair_payloads[0]
    pairs_b, sums_b, deltas_b, mults_b = pair_payloads[1]
    pairs_c, sums_c, deltas_c, mults_c = pair_payloads[2]

    ab_pairs = []
    ab_sums = []
    ab_deltas = []
    ab_mults = []
    ab_per_face_zero = []
    for start in range(0, len(pairs_a), 128):
        chunk_pairs = pairs_a[start : start + 128]
        chunk_sums = sums_a[start : start + 128]
        chunk_deltas = deltas_a[start : start + 128]
        chunk_mults = mults_a[start : start + 128]
        pair_block = np.concatenate(
            [
                np.repeat(chunk_pairs[:, None, :], len(pairs_b), axis=1),
                np.repeat(pairs_b[None, :, :], len(chunk_pairs), axis=0),
            ],
            axis=2,
        )
        ab_pairs.append(pair_block.reshape(-1, 4))
        ab_sums.append((chunk_sums[:, None, :] + sums_b[None, :, :]).reshape(-1, 5))
        ab_deltas.append((chunk_deltas[:, None] + deltas_b[None, :]).reshape(-1))
        ab_mults.append((chunk_mults[:, None] + mults_b[None, :]).reshape(-1))
        ab_per_face_zero.append(
            (
                (chunk_deltas[:, None] == 0)
                & (deltas_b[None, :] == 0)
            ).reshape(-1)
        )
    ab_pairs = np.concatenate(ab_pairs)
    ab_sums = np.concatenate(ab_sums)
    ab_deltas = np.concatenate(ab_deltas)
    ab_mults = np.concatenate(ab_mults)
    ab_per_face_zero = np.concatenate(ab_per_face_zero)

    below_p15 = 0
    at_p15 = 0
    below_p14 = 0
    below_p11 = 0
    below_p8 = 0
    below_p7 = 0
    below_p6 = 0
    below_p5 = 0
    equal = 0
    total_delta_zero = 0
    per_face_delta_zero = 0
    low_rows: dict[tuple[int, ...], dict[str, int]] = {}
    best_any: dict[str, int] | None = None
    candidate_count = int(len(ab_sums) * len(pairs_c))

    for start in range(0, len(ab_sums), BATCH_SIZE):
        chunk_sums = ab_sums[start : start + BATCH_SIZE]
        chunk_deltas = ab_deltas[start : start + BATCH_SIZE]
        chunk_mults = ab_mults[start : start + BATCH_SIZE]
        chunk_pairs = ab_pairs[start : start + BATCH_SIZE]
        chunk_per_face_zero = ab_per_face_zero[start : start + BATCH_SIZE]
        sums = chunk_sums[:, None, :] + sums_c[None, :, :]
        spreads = sums.max(axis=2) - sums.min(axis=2)
        below_p15 += int((spreads < p15_floor).sum())
        at_p15 += int((spreads == p15_floor).sum())
        below_p14 += int((spreads < p14_floor).sum())
        below_p11 += int((spreads < p11_floor).sum())
        below_p8 += int((spreads < p8_floor).sum())
        below_p7 += int((spreads < p7_floor).sum())
        below_p6 += int((spreads < p6_floor).sum())
        below_p5 += int((spreads < p5_floor).sum())
        equal += int((spreads == 0).sum())
        total_delta = chunk_deltas[:, None] + deltas_c[None, :]
        total_delta_zero += int((total_delta == 0).sum())
        per_face_zero = chunk_per_face_zero[:, None] & (deltas_c[None, :] == 0)
        per_face_delta_zero += int(per_face_zero.sum())

        for local_ab, pair_c in np.argwhere(spreads < p5_floor):
            p17_id = (start + int(local_ab)) * len(pairs_c) + int(pair_c)
            combo = tuple(
                int(value)
                for value in np.concatenate([chunk_pairs[local_ab], pairs_c[pair_c]])
            )
            row = candidate_row(
                rank=0,
                p17_id=p17_id,
                p5_ids=combo,
                joint=sums[local_ab, pair_c],
                total_delta=int(total_delta[local_ab, pair_c]),
                per_face_delta_zero=bool(per_face_zero[local_ab, pair_c]),
                joint_mult=int(chunk_mults[local_ab] + mults_c[pair_c]),
                p5_floor=p5_floor,
                p6_floor=p6_floor,
                p7_floor=p7_floor,
                p8_floor=p8_floor,
                p11_floor=p11_floor,
                p14_floor=p14_floor,
                p15_floor=p15_floor,
            )
            key = combo
            low_rows[key] = row
            if best_any is None or (
                row["joint_support_spread"],
                row["p17_id"],
            ) < (
                best_any["joint_support_spread"],
                best_any["p17_id"],
            ):
                best_any = row

    if best_any is None:
        raise ValueError("empty p17 balance class")
    top_rows = sorted(
        low_rows.values(),
        key=lambda row: (row["joint_support_spread"], row["p17_id"]),
    )[:TOP_N]
    for rank, row in enumerate(top_rows):
        row["rank"] = rank

    obs = {
        "class_count": len(BALANCE_CLASSES),
        "moves_per_class": len(groups[0]),
        "pairs_per_class": len(pairs_a),
        "balance_candidate_count": candidate_count,
        "p5_single_floor": p5_floor,
        "p6_pair_floor": p6_floor,
        "p7_triple_floor": p7_floor,
        "p8_quad_floor": p8_floor,
        "p11_quint_floor": p11_floor,
        "p14_basin_six_floor": p14_floor,
        "p15_grid_floor": p15_floor,
        "balance_min_spread": best_any["joint_support_spread"],
        "balance_min_equal_p15_flag": int(best_any["joint_support_spread"] == p15_floor),
        "below_p15_candidate_count": below_p15,
        "at_p15_floor_candidate_count": at_p15,
        "below_p14_candidate_count": below_p14,
        "below_p11_candidate_count": below_p11,
        "below_p8_candidate_count": below_p8,
        "below_p7_candidate_count": below_p7,
        "below_p6_candidate_count": below_p6,
        "below_p5_candidate_count": below_p5,
        "support_equal_candidate_count": equal,
        "total_delta_zero_candidate_count": total_delta_zero,
        "per_face_delta_zero_candidate_count": per_face_delta_zero,
        "best_p17_id": best_any["p17_id"],
        "best_p5_a": best_any["p5_a"],
        "best_p5_b": best_any["p5_b"],
        "best_p5_c": best_any["p5_c"],
        "best_p5_d": best_any["p5_d"],
        "best_p5_e": best_any["p5_e"],
        "best_p5_f": best_any["p5_f"],
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
        "class_rows": class_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def best_rows_for_witness(rows: list[dict[str, int]]) -> list[dict[str, Any]]:
    return [
        {
            "rank": row["rank"],
            "p17_id": row["p17_id"],
            "p5_ids": [
                row["p5_a"],
                row["p5_b"],
                row["p5_c"],
                row["p5_d"],
                row["p5_e"],
                row["p5_f"],
            ],
            "support": [
                row["joint_p0_support"],
                row["joint_p1_support"],
                row["joint_p2_support"],
                row["joint_p3_support"],
                row["joint_p4_support"],
            ],
            "spread": row["joint_support_spread"],
            "total_f4_delta": row["total_f4_delta"],
            "per_face_delta_zero": row["per_face_delta_zero_flag"],
        }
        for row in rows
    ]


def build_payloads() -> dict[str, Any]:
    rows = build_p17_rows()
    top_table = table_from_rows(TOP_COLUMNS, rows["top_rows"])
    class_table = table_from_rows(CLASS_COLUMNS, rows["class_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    p5_report = load_json(P5_REPORT)
    p6_report = load_json(P6_REPORT)
    p7_report = load_json(P7_REPORT)
    p8_report = load_json(P8_REPORT)
    p11_report = load_json(P11_REPORT)
    p15_report = load_json(P15_REPORT)
    p16_report = load_json(P16_REPORT)
    checks = {
        "input_certificates_available": (
            p5_report.get("all_checks_pass") is True
            and p6_report.get("all_checks_pass") is True
            and p7_report.get("all_checks_pass") is True
            and p8_report.get("all_checks_pass") is True
            and p11_report.get("all_checks_pass") is True
            and p15_report.get("all_checks_pass") is True
            and p16_report.get("all_checks_pass") is True
        ),
        "balance_class_size_matches": (
            obs["class_count"],
            obs["moves_per_class"],
            obs["pairs_per_class"],
            obs["balance_candidate_count"],
        )
        == (3, 48, 1_128, 1_435_249_152),
        "balance_floor_matches_p15": (
            obs["p15_grid_floor"],
            obs["balance_min_spread"],
            obs["balance_min_equal_p15_flag"],
            obs["below_p15_candidate_count"],
            obs["at_p15_floor_candidate_count"],
        )
        == (492_736, 492_736, 1, 0, 1),
        "descent_counts_match": (
            obs["below_p14_candidate_count"],
            obs["below_p11_candidate_count"],
            obs["below_p8_candidate_count"],
            obs["below_p7_candidate_count"],
            obs["below_p6_candidate_count"],
            obs["below_p5_candidate_count"],
            obs["support_equal_candidate_count"],
        )
        == (1, 1, 3, 3, 2_240, 2_929, 0),
        "delta_counts_match": (
            obs["total_delta_zero_candidate_count"],
            obs["per_face_delta_zero_candidate_count"],
        )
        == (7_077_888, 7_077_888),
        "best_candidate_matches_expected": (
            obs["best_p17_id"],
            obs["best_p5_a"],
            obs["best_p5_b"],
            obs["best_p5_c"],
            obs["best_p5_d"],
            obs["best_p5_e"],
            obs["best_p5_f"],
        )
        == (117_520_136, 1, 47, 57, 79, 110, 128),
        "class_tables_match": tuple(
            (
                row["move_count"],
                row["pair_count"],
                row["zero_delta_pair_count"],
                row["unique_pair_delta_count"],
                row["min_abs_pair_delta"],
            )
            for row in rows["class_rows"]
        )
        == ((48, 1_128, 192, 19, 0),) * 3,
        "table_shapes_match_codebooks": (
            tuple(top_table.shape),
            tuple(class_table.shape),
            tuple(obs_table.shape),
        )
        == (
            (TOP_N, len(TOP_COLUMNS)),
            (len(BALANCE_CLASSES), len(CLASS_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "classification": "exact_222_face_mask_balance_class",
        "candidate_construction": (
            "choose exactly two p5 rows from each of the three fused face/mask "
            "classes (12,30), (22,45), and (26,51)"
        ),
        "balance_candidate_count": obs["balance_candidate_count"],
        "p15_grid_floor": obs["p15_grid_floor"],
        "balance_min_spread": obs["balance_min_spread"],
        "below_p15_candidate_count": obs["below_p15_candidate_count"],
        "at_p15_floor_candidate_count": obs["at_p15_floor_candidate_count"],
        "below_p14_candidate_count": obs["below_p14_candidate_count"],
        "below_p11_candidate_count": obs["below_p11_candidate_count"],
        "below_p8_candidate_count": obs["below_p8_candidate_count"],
        "below_p7_candidate_count": obs["below_p7_candidate_count"],
        "below_p6_candidate_count": obs["below_p6_candidate_count"],
        "below_p5_candidate_count": obs["below_p5_candidate_count"],
        "support_equal_candidate_count": obs["support_equal_candidate_count"],
        "total_delta_zero_candidate_count": obs["total_delta_zero_candidate_count"],
        "per_face_delta_zero_candidate_count": obs["per_face_delta_zero_candidate_count"],
        "best_candidates": best_rows_for_witness(rows["top_rows"][:16]),
        "class_rows": rows["class_rows"],
        "reading": (
            "The exact 2+2+2 face/mask balance class confirms the p15 winner is "
            "the unique class member at the 492736 screened floor. No class "
            "member beats p15 and none equalizes raw support."
        ),
        "top_table_sha256": sha_array(top_table),
        "class_table_sha256": sha_array(class_table),
        "observable_table_sha256": sha_array(obs_table),
    }
    p17 = {
        "schema": "eta6.p17@1",
        "object": "eta6",
        "construction": {
            "source": "all p5 rows in the p15 winner's 2+2+2 face/mask class",
            "test": "exact balance-class six-move search",
            "classification": witness["classification"],
        },
        "witness": witness,
    }
    report = {
        "schema": "eta6.p17.report@1",
        "status": STATUS if all(checks.values()) else "ETA6_P17_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The exact 2+2+2 face/mask balance-class search checks "
            "1,435,249,152 sextuples. The p15 winner is the unique member at "
            "spread 492736; no balance-class sextuple beats it and none "
            "equalizes raw support."
        ),
        "stage_protocol": {
            "draft": "start from the p15 winner's 2+2+2 face/mask balance class",
            "witness": "enumerate all pair choices in the three fused face/mask classes",
            "coherence": "compare exact class floor against p15, p14, p11, p8, p7, p6, and p5 floors",
            "closure": "certify exact balance-class floor without support equalization",
            "emit": "emit compact p17 artifacts and the next seam",
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
            "p6_report": input_entry(P6_REPORT),
            "p7_report": input_entry(P7_REPORT),
            "p8_report": input_entry(P8_REPORT),
            "p11_report": input_entry(P11_REPORT),
            "p15_report": input_entry(
                P15_REPORT,
                {
                    "status": p15_report.get("status"),
                    "certificate_sha256": p15_report.get("certificate_sha256"),
                },
            ),
            "p16_report": input_entry(
                P16_REPORT,
                {
                    "status": p16_report.get("status"),
                    "certificate_sha256": p16_report.get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "p17": relpath(OUT_DIR / "p17.json"),
            "top_csv": relpath(OUT_DIR / "top.csv"),
            "class_csv": relpath(OUT_DIR / "class.csv"),
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
                "exact six-move search over the p15 winner's 2+2+2 face/mask balance class",
                "1435249152 balance-class sextuples checked",
                "p15 winner is the unique balance-class sextuple at spread 492736",
                "no balance-class sextuple beats the p15 screened floor",
                "no balance-class sextuple equalizes raw support",
            ],
            "does_not_certify_because_out_of_scope": [
                "complete six-move search over all 11143364232 p5 sextuples",
                "that no unbalanced sextuple beats 492736",
                "a rebuilt carrier after applying the p15 winner as surgery",
                "new hpol/replacement row universes beyond eta6_gap",
            ],
        },
        "next_highest_yield_item": (
            "Run p18 as a global exact six-move branch-and-bound or a wider "
            "centered-grid screen outside the 2+2+2 class."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "eta6.p17.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "eta6.p17.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "p17": p17,
        "top_csv": csv_text(TOP_COLUMNS, rows["top_rows"]),
        "class_csv": csv_text(CLASS_COLUMNS, rows["class_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "top_table": top_table,
        "class_table": class_table,
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
    write_json(OUT_DIR / "p17.json", payloads["p17"])
    (OUT_DIR / "top.csv").write_text(payloads["top_csv"], encoding="utf-8")
    (OUT_DIR / "class.csv").write_text(payloads["class_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        top_table=payloads["top_table"],
        class_table=payloads["class_table"],
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
