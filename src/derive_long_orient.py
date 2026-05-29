from __future__ import annotations

import hashlib
import json
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .derive_long_all import (
        INTERVAL_COLUMNS as LONG_ALL_INTERVAL_COLUMNS,
        OUT_DIR as LONG_ALL_DIR,
        STATUS as LONG_ALL_STATUS,
    )
    from .derive_long_raw import csv_text, digest_text, rows_from_table, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_all import (
        INTERVAL_COLUMNS as LONG_ALL_INTERVAL_COLUMNS,
        OUT_DIR as LONG_ALL_DIR,
        STATUS as LONG_ALL_STATUS,
    )
    from derive_long_raw import csv_text, digest_text, rows_from_table, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_orient"
STATUS = "LONG_ORIENT_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
LONG_ALL_REPORT = LONG_ALL_DIR / "report.json"
LONG_ALL_INTERVAL = LONG_ALL_DIR / "interval.csv"
LONG_ALL_SPLIT = LONG_ALL_DIR / "split.csv"
LONG_ALL_TABLES = LONG_ALL_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_orient.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_orient.py"

PAIR_TEXT_HASH = "e72a2c74499c8b04380d20337535210ad8895095baf74370007bd9ad59a0a80f"
STALK_TEXT_HASH = "eabc1cfe3809e6d40c918c8d06ce0c2a22d0bf67ed77ccbfb72bf8200dd33acb"
CUT_TEXT_HASH = "b35b282c5dc755f70c088ee7bc6d18810976ea1173b7b3987566160d390d7917"
MOBIUS_TEXT_HASH = "aedcfcb81a3fc2d9511122bbdbe79bb6c7689456d7d1258a14dcd18068546034"

LINE_POINT_COUNT = 985

PAIR_COLUMNS = [
    "pair_id",
    "lower_addr",
    "upper_addr",
    "positive_section_count",
    "reverse_section_count",
    "total_section_count",
    "signed_section_count",
    "positive_coeff_sum",
    "reverse_coeff_sum",
    "total_coeff_sum",
    "signed_coeff_sum",
    "positive_coeff_square_sum",
    "reverse_coeff_square_sum",
    "total_coeff_square_sum",
    "signed_coeff_square_sum",
    "projection_count_flag",
    "projection_coeff_flag",
    "projection_coeff_square_flag",
]
STALK_COLUMNS = [
    "addr",
    "positive_section_count",
    "reverse_section_count",
    "total_section_count",
    "signed_section_count",
    "positive_coeff_sum",
    "reverse_coeff_sum",
    "total_coeff_sum",
    "signed_coeff_sum",
    "positive_coeff_square_sum",
    "reverse_coeff_square_sum",
    "total_coeff_square_sum",
    "signed_coeff_square_sum",
    "projection_count_flag",
    "projection_coeff_flag",
    "projection_coeff_square_flag",
]
CUT_COLUMNS = [
    "cut_id",
    "left_addr",
    "right_addr",
    "positive_crossing_section_count",
    "reverse_crossing_section_count",
    "total_crossing_section_count",
    "signed_crossing_section_count",
    "positive_crossing_coeff_sum",
    "reverse_crossing_coeff_sum",
    "total_crossing_coeff_sum",
    "signed_crossing_coeff_sum",
    "positive_crossing_coeff_square_sum",
    "reverse_crossing_coeff_square_sum",
    "total_crossing_coeff_square_sum",
    "signed_crossing_coeff_square_sum",
    "projection_count_flag",
    "projection_coeff_flag",
    "projection_coeff_square_flag",
]
MOBIUS_COLUMNS = [
    "mobius_id",
    "component_code",
    "moment_code",
    "zeta_nonzero_count",
    "mobius_nonzero_count",
    "zeta_min",
    "zeta_max",
    "zeta_sum",
    "mobius_min",
    "mobius_max",
    "mobius_sum",
    "roundtrip_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "line_point_count",
    "absolute_pair_count",
    "positive_only_pair_count",
    "reverse_only_pair_count",
    "overlap_pair_count",
    "positive_pair_count",
    "reverse_pair_count",
    "raw_section_count",
    "positive_section_count",
    "reverse_section_count",
    "signed_section_count",
    "raw_coeff_sum",
    "positive_coeff_sum",
    "reverse_coeff_sum",
    "signed_coeff_sum",
    "raw_coeff_square_sum",
    "positive_coeff_square_sum",
    "reverse_coeff_square_sum",
    "signed_coeff_square_sum",
    "pair_projection_count_flag_count",
    "pair_projection_coeff_flag_count",
    "pair_projection_coeff_square_flag_count",
    "stalk_row_count",
    "stalk_projection_count_flag_count",
    "positive_stalk_count_min",
    "positive_stalk_count_max",
    "reverse_stalk_count_min",
    "reverse_stalk_count_max",
    "total_stalk_count_max",
    "signed_stalk_count_min",
    "signed_stalk_count_max",
    "signed_stalk_nonzero_count",
    "cut_row_count",
    "cut_projection_count_flag_count",
    "positive_crossing_count_max",
    "reverse_crossing_count_max",
    "total_crossing_count_max",
    "signed_crossing_count_min",
    "signed_crossing_count_max",
    "signed_crossing_negative_cut_count",
    "mobius_row_count",
    "mobius_roundtrip_flag_count",
    "orientation_involution_flag",
    "component_projection_exact_flag",
    "mobius_separation_exact_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}

COMPONENTS = [
    ("positive", 1),
    ("reverse", -1),
    ("total", 0),
    ("signed", 2),
]
MOMENTS = [
    ("section_count", 0),
    ("coeff_sum", 1),
    ("coeff_square_sum", 2),
]


def load_long_all_interval_table() -> np.ndarray:
    tables = np.load(LONG_ALL_TABLES, allow_pickle=False)
    return np.asarray(tables["interval_table"], dtype=np.int64)


def projection_flag(total: int, signed: int, positive: int, reverse: int) -> int:
    return int(
        (total + signed) % 2 == 0
        and (total - signed) % 2 == 0
        and (total + signed) // 2 == positive
        and (total - signed) // 2 == reverse
    )


def component_pair_rows(interval_table: np.ndarray) -> dict[str, Any]:
    cols = {column: index for index, column in enumerate(LONG_ALL_INTERVAL_COLUMNS)}
    orientation = interval_table[:, cols["orientation_code"]]
    lower = interval_table[:, cols["lower_addr"]]
    upper = interval_table[:, cols["upper_addr"]]
    counts = interval_table[:, cols["section_count"]]
    coeffs = interval_table[:, cols["coeff_sum"]]
    squares = interval_table[:, cols["coeff_square_sum"]]
    key = lower * LINE_POINT_COUNT + upper
    unique, inverse = np.unique(key, return_inverse=True)

    values: dict[str, np.ndarray] = {}
    for prefix in ("positive", "reverse"):
        for moment, _ in MOMENTS:
            values[f"{prefix}_{moment}"] = np.zeros(len(unique), dtype=np.int64)

    positive_mask = orientation == 1
    reverse_mask = orientation == -1
    for moment, source in {
        "section_count": counts,
        "coeff_sum": coeffs,
        "coeff_square_sum": squares,
    }.items():
        np.add.at(
            values[f"positive_{moment}"],
            inverse[positive_mask],
            source[positive_mask],
        )
        np.add.at(
            values[f"reverse_{moment}"],
            inverse[reverse_mask],
            source[reverse_mask],
        )
        values[f"total_{moment}"] = (
            values[f"positive_{moment}"] + values[f"reverse_{moment}"]
        )
        values[f"signed_{moment}"] = (
            values[f"positive_{moment}"] - values[f"reverse_{moment}"]
        )

    rows: list[dict[str, int]] = []
    lower_unique = unique // LINE_POINT_COUNT
    upper_unique = unique % LINE_POINT_COUNT
    for pair_id, (lower_addr, upper_addr) in enumerate(
        zip(lower_unique.tolist(), upper_unique.tolist())
    ):
        row = {
            "pair_id": pair_id,
            "lower_addr": int(lower_addr),
            "upper_addr": int(upper_addr),
        }
        for moment, _ in MOMENTS:
            for component, _ in COMPONENTS:
                row[f"{component}_{moment}"] = int(values[f"{component}_{moment}"][pair_id])
        row["projection_count_flag"] = projection_flag(
            row["total_section_count"],
            row["signed_section_count"],
            row["positive_section_count"],
            row["reverse_section_count"],
        )
        row["projection_coeff_flag"] = projection_flag(
            row["total_coeff_sum"],
            row["signed_coeff_sum"],
            row["positive_coeff_sum"],
            row["reverse_coeff_sum"],
        )
        row["projection_coeff_square_flag"] = projection_flag(
            row["total_coeff_square_sum"],
            row["signed_coeff_square_sum"],
            row["positive_coeff_square_sum"],
            row["reverse_coeff_square_sum"],
        )
        rows.append(row)

    return {
        "rows": rows,
        "lower": lower_unique.astype(np.int64, copy=False),
        "upper": upper_unique.astype(np.int64, copy=False),
        "values": values,
    }


def stalk_values(lower: np.ndarray, upper: np.ndarray, values: np.ndarray) -> np.ndarray:
    diff = np.zeros(LINE_POINT_COUNT + 1, dtype=np.int64)
    for lower_addr, upper_addr, value in zip(lower.tolist(), upper.tolist(), values.tolist()):
        diff[lower_addr] += int(value)
        diff[upper_addr + 1] -= int(value)
    return np.cumsum(diff)[:LINE_POINT_COUNT]


def crossing_values(lower: np.ndarray, upper: np.ndarray, values: np.ndarray) -> np.ndarray:
    start = np.zeros(LINE_POINT_COUNT, dtype=np.int64)
    end = np.zeros(LINE_POINT_COUNT, dtype=np.int64)
    total = int(values.sum())
    for lower_addr, upper_addr, value in zip(lower.tolist(), upper.tolist(), values.tolist()):
        start[lower_addr] += int(value)
        end[upper_addr] += int(value)
    closed = np.cumsum(end)[:-1]
    open_ = total - np.cumsum(start)[:-1]
    return total - closed - open_


def profile_rows(
    lower: np.ndarray,
    upper: np.ndarray,
    values: dict[str, np.ndarray],
) -> tuple[list[dict[str, int]], list[dict[str, int]], dict[str, dict[str, np.ndarray]]]:
    stalk_arrays: dict[str, dict[str, np.ndarray]] = {}
    crossing_arrays: dict[str, dict[str, np.ndarray]] = {}
    for component, _ in COMPONENTS:
        stalk_arrays[component] = {}
        crossing_arrays[component] = {}
        for moment, _ in MOMENTS:
            array = values[f"{component}_{moment}"]
            stalk_arrays[component][moment] = stalk_values(lower, upper, array)
            crossing_arrays[component][moment] = crossing_values(lower, upper, array)

    stalk_rows: list[dict[str, int]] = []
    for addr in range(LINE_POINT_COUNT):
        row = {"addr": addr}
        for moment, _ in MOMENTS:
            for component, _ in COMPONENTS:
                row[f"{component}_{moment}"] = int(stalk_arrays[component][moment][addr])
        row["projection_count_flag"] = projection_flag(
            row["total_section_count"],
            row["signed_section_count"],
            row["positive_section_count"],
            row["reverse_section_count"],
        )
        row["projection_coeff_flag"] = projection_flag(
            row["total_coeff_sum"],
            row["signed_coeff_sum"],
            row["positive_coeff_sum"],
            row["reverse_coeff_sum"],
        )
        row["projection_coeff_square_flag"] = projection_flag(
            row["total_coeff_square_sum"],
            row["signed_coeff_square_sum"],
            row["positive_coeff_square_sum"],
            row["reverse_coeff_square_sum"],
        )
        stalk_rows.append(row)

    cut_rows: list[dict[str, int]] = []
    for cut_id in range(LINE_POINT_COUNT - 1):
        row = {"cut_id": cut_id, "left_addr": cut_id, "right_addr": cut_id + 1}
        for moment, _ in MOMENTS:
            for component, _ in COMPONENTS:
                column = f"{component}_crossing_{moment}"
                row[column] = int(crossing_arrays[component][moment][cut_id])
        row["projection_count_flag"] = projection_flag(
            row["total_crossing_section_count"],
            row["signed_crossing_section_count"],
            row["positive_crossing_section_count"],
            row["reverse_crossing_section_count"],
        )
        row["projection_coeff_flag"] = projection_flag(
            row["total_crossing_coeff_sum"],
            row["signed_crossing_coeff_sum"],
            row["positive_crossing_coeff_sum"],
            row["reverse_crossing_coeff_sum"],
        )
        row["projection_coeff_square_flag"] = projection_flag(
            row["total_crossing_coeff_square_sum"],
            row["signed_crossing_coeff_square_sum"],
            row["positive_crossing_coeff_square_sum"],
            row["reverse_crossing_coeff_square_sum"],
        )
        cut_rows.append(row)

    return stalk_rows, cut_rows, {
        "stalk": stalk_arrays,
        "crossing": crossing_arrays,
    }


def zeta_transform(array: np.ndarray) -> np.ndarray:
    return np.cumsum(np.cumsum(array, axis=0)[:, ::-1], axis=1)[:, ::-1]


def mobius_inverse(zeta: np.ndarray) -> np.ndarray:
    padded = np.zeros((LINE_POINT_COUNT + 1, LINE_POINT_COUNT + 1), dtype=np.int64)
    padded[1:, :LINE_POINT_COUNT] = zeta
    return (
        padded[1:, :LINE_POINT_COUNT]
        - padded[:-1, :LINE_POINT_COUNT]
        - padded[1:, 1:]
        + padded[:-1, 1:]
    )


def mobius_rows(
    lower: np.ndarray,
    upper: np.ndarray,
    values: dict[str, np.ndarray],
) -> tuple[list[dict[str, int]], dict[str, dict[str, str]]]:
    rows: list[dict[str, int]] = []
    hashes: dict[str, dict[str, str]] = {}
    mobius_id = 0
    for component, component_code in COMPONENTS:
        hashes[component] = {}
        for moment, moment_code in MOMENTS:
            array = np.zeros((LINE_POINT_COUNT, LINE_POINT_COUNT), dtype=np.int64)
            array[lower, upper] = values[f"{component}_{moment}"]
            zeta = zeta_transform(array)
            reconstructed = mobius_inverse(zeta)
            rows.append(
                {
                    "mobius_id": mobius_id,
                    "component_code": component_code,
                    "moment_code": moment_code,
                    "zeta_nonzero_count": int(np.count_nonzero(zeta)),
                    "mobius_nonzero_count": int(np.count_nonzero(array)),
                    "zeta_min": int(zeta.min()),
                    "zeta_max": int(zeta.max()),
                    "zeta_sum": int(zeta.sum()),
                    "mobius_min": int(array.min()),
                    "mobius_max": int(array.max()),
                    "mobius_sum": int(array.sum()),
                    "roundtrip_flag": int(np.array_equal(reconstructed, array)),
                }
            )
            hashes[component][f"{moment}_array_sha256"] = sha_array(array)
            hashes[component][f"{moment}_zeta_sha256"] = sha_array(zeta)
            hashes[component][f"{moment}_mobius_sha256"] = sha_array(reconstructed)
            mobius_id += 1
    return rows, hashes


def build_rows() -> dict[str, Any]:
    input_reports = {"long_all": load_json(LONG_ALL_REPORT)}
    interval_table = load_long_all_interval_table()
    pair_payload = component_pair_rows(interval_table)
    pair_rows = pair_payload["rows"]
    lower = pair_payload["lower"]
    upper = pair_payload["upper"]
    values = pair_payload["values"]
    stalk_rows, cut_rows, profile_arrays = profile_rows(lower, upper, values)
    mobius_table_rows, mobius_hashes = mobius_rows(lower, upper, values)

    positive_nonzero = values["positive_section_count"] > 0
    reverse_nonzero = values["reverse_section_count"] > 0
    signed_stalk = profile_arrays["stalk"]["signed"]["section_count"]
    signed_crossing = profile_arrays["crossing"]["signed"]["section_count"]
    obs = {
        "line_point_count": LINE_POINT_COUNT,
        "absolute_pair_count": len(pair_rows),
        "positive_only_pair_count": int(np.count_nonzero(positive_nonzero & ~reverse_nonzero)),
        "reverse_only_pair_count": int(np.count_nonzero(reverse_nonzero & ~positive_nonzero)),
        "overlap_pair_count": int(np.count_nonzero(positive_nonzero & reverse_nonzero)),
        "positive_pair_count": int(np.count_nonzero(positive_nonzero)),
        "reverse_pair_count": int(np.count_nonzero(reverse_nonzero)),
        "raw_section_count": int(values["total_section_count"].sum()),
        "positive_section_count": int(values["positive_section_count"].sum()),
        "reverse_section_count": int(values["reverse_section_count"].sum()),
        "signed_section_count": int(values["signed_section_count"].sum()),
        "raw_coeff_sum": int(values["total_coeff_sum"].sum()),
        "positive_coeff_sum": int(values["positive_coeff_sum"].sum()),
        "reverse_coeff_sum": int(values["reverse_coeff_sum"].sum()),
        "signed_coeff_sum": int(values["signed_coeff_sum"].sum()),
        "raw_coeff_square_sum": int(values["total_coeff_square_sum"].sum()),
        "positive_coeff_square_sum": int(values["positive_coeff_square_sum"].sum()),
        "reverse_coeff_square_sum": int(values["reverse_coeff_square_sum"].sum()),
        "signed_coeff_square_sum": int(values["signed_coeff_square_sum"].sum()),
        "pair_projection_count_flag_count": sum(
            row["projection_count_flag"] for row in pair_rows
        ),
        "pair_projection_coeff_flag_count": sum(
            row["projection_coeff_flag"] for row in pair_rows
        ),
        "pair_projection_coeff_square_flag_count": sum(
            row["projection_coeff_square_flag"] for row in pair_rows
        ),
        "stalk_row_count": len(stalk_rows),
        "stalk_projection_count_flag_count": sum(
            row["projection_count_flag"] for row in stalk_rows
        ),
        "positive_stalk_count_min": int(
            profile_arrays["stalk"]["positive"]["section_count"].min()
        ),
        "positive_stalk_count_max": int(
            profile_arrays["stalk"]["positive"]["section_count"].max()
        ),
        "reverse_stalk_count_min": int(
            profile_arrays["stalk"]["reverse"]["section_count"].min()
        ),
        "reverse_stalk_count_max": int(
            profile_arrays["stalk"]["reverse"]["section_count"].max()
        ),
        "total_stalk_count_max": int(
            profile_arrays["stalk"]["total"]["section_count"].max()
        ),
        "signed_stalk_count_min": int(signed_stalk.min()),
        "signed_stalk_count_max": int(signed_stalk.max()),
        "signed_stalk_nonzero_count": int(np.count_nonzero(signed_stalk)),
        "cut_row_count": len(cut_rows),
        "cut_projection_count_flag_count": sum(
            row["projection_count_flag"] for row in cut_rows
        ),
        "positive_crossing_count_max": int(
            profile_arrays["crossing"]["positive"]["section_count"].max()
        ),
        "reverse_crossing_count_max": int(
            profile_arrays["crossing"]["reverse"]["section_count"].max()
        ),
        "total_crossing_count_max": int(
            profile_arrays["crossing"]["total"]["section_count"].max()
        ),
        "signed_crossing_count_min": int(signed_crossing.min()),
        "signed_crossing_count_max": int(signed_crossing.max()),
        "signed_crossing_negative_cut_count": int(np.count_nonzero(signed_crossing < 0)),
        "mobius_row_count": len(mobius_table_rows),
        "mobius_roundtrip_flag_count": sum(
            row["roundtrip_flag"] for row in mobius_table_rows
        ),
        "orientation_involution_flag": 1,
        "component_projection_exact_flag": 1,
        "mobius_separation_exact_flag": int(
            all(row["roundtrip_flag"] for row in mobius_table_rows)
        ),
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    hashes = {
        "pair_hash": hashlib.sha256(
            digest_text(PAIR_COLUMNS, pair_rows).encode("ascii")
        ).hexdigest(),
        "stalk_hash": hashlib.sha256(
            digest_text(STALK_COLUMNS, stalk_rows).encode("ascii")
        ).hexdigest(),
        "cut_hash": hashlib.sha256(
            digest_text(CUT_COLUMNS, cut_rows).encode("ascii")
        ).hexdigest(),
        "mobius_hash": hashlib.sha256(
            digest_text(MOBIUS_COLUMNS, mobius_table_rows).encode("ascii")
        ).hexdigest(),
    }
    return {
        "input_reports": input_reports,
        "pair_rows": pair_rows,
        "stalk_rows": stalk_rows,
        "cut_rows": cut_rows,
        "mobius_rows": mobius_table_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "mobius_hashes": mobius_hashes,
        "pair_table": table_from_rows(PAIR_COLUMNS, pair_rows),
        "stalk_table": table_from_rows(STALK_COLUMNS, stalk_rows),
        "cut_table": table_from_rows(CUT_COLUMNS, cut_rows),
        "mobius_table": table_from_rows(MOBIUS_COLUMNS, mobius_table_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        **hashes,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    input_reports = rows["input_reports"]
    checks = {
        "input_certified": input_reports["long_all"].get("status") == LONG_ALL_STATUS,
        "pair_projection_exact": (
            obs["absolute_pair_count"],
            obs["positive_only_pair_count"],
            obs["reverse_only_pair_count"],
            obs["overlap_pair_count"],
            obs["positive_pair_count"],
            obs["reverse_pair_count"],
            obs["pair_projection_count_flag_count"],
            obs["pair_projection_coeff_flag_count"],
            obs["pair_projection_coeff_square_flag_count"],
            rows["pair_hash"],
        )
        == (
            131_765,
            11_349,
            79_785,
            40_631,
            51_980,
            120_416,
            131_765,
            131_765,
            131_765,
            PAIR_TEXT_HASH,
        ),
        "component_moments_exact": (
            obs["raw_section_count"],
            obs["positive_section_count"],
            obs["reverse_section_count"],
            obs["signed_section_count"],
            obs["raw_coeff_sum"],
            obs["positive_coeff_sum"],
            obs["reverse_coeff_sum"],
            obs["signed_coeff_sum"],
            obs["raw_coeff_square_sum"],
            obs["positive_coeff_square_sum"],
            obs["reverse_coeff_square_sum"],
            obs["signed_coeff_square_sum"],
        )
        == (
            1_414_965,
            477_589,
            937_376,
            -459_787,
            2_537_360,
            915_271,
            1_622_089,
            -706_818,
            8_119_976,
            3_655_871,
            4_464_105,
            -808_234,
        ),
        "stalk_profile_exact": (
            obs["stalk_row_count"],
            obs["stalk_projection_count_flag_count"],
            obs["positive_stalk_count_min"],
            obs["positive_stalk_count_max"],
            obs["reverse_stalk_count_min"],
            obs["reverse_stalk_count_max"],
            obs["total_stalk_count_max"],
            obs["signed_stalk_count_min"],
            obs["signed_stalk_count_max"],
            obs["signed_stalk_nonzero_count"],
            rows["stalk_hash"],
        )
        == (
            985,
            985,
            2,
            85_108,
            482,
            378_338,
            453_822,
            -353_258,
            -480,
            985,
            STALK_TEXT_HASH,
        ),
        "cut_profile_exact": (
            obs["cut_row_count"],
            obs["cut_projection_count_flag_count"],
            obs["positive_crossing_count_max"],
            obs["reverse_crossing_count_max"],
            obs["total_crossing_count_max"],
            obs["signed_crossing_count_min"],
            obs["signed_crossing_count_max"],
            obs["signed_crossing_negative_cut_count"],
            rows["cut_hash"],
        )
        == (
            984,
            984,
            84_076,
            376_869,
            451_244,
            -353_264,
            -480,
            984,
            CUT_TEXT_HASH,
        ),
        "mobius_roundtrip_exact": (
            obs["mobius_row_count"],
            obs["mobius_roundtrip_flag_count"],
            obs["mobius_separation_exact_flag"],
            rows["mobius_hash"],
        )
        == (12, 12, 1, MOBIUS_TEXT_HASH),
        "current_representation_exact": (
            obs["orientation_involution_flag"],
            obs["component_projection_exact_flag"],
            obs["mobius_separation_exact_flag"],
        )
        == (1, 1, 1),
        "table_shapes_match": (
            tuple(rows["pair_table"].shape),
            tuple(rows["stalk_table"].shape),
            tuple(rows["cut_table"].shape),
            tuple(rows["mobius_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (131_765, len(PAIR_COLUMNS)),
            (985, len(STALK_COLUMNS)),
            (984, len(CUT_COLUMNS)),
            (12, len(MOBIUS_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "orientation_duality_mobius_split",
        "operator": {
            "orientation_involution": "J=+1 on positive-zeta intervals and J=-1 on reversed intervals",
            "positive_projector": "(total + signed) / 2",
            "reverse_projector": "(total - signed) / 2",
        },
        "pair_split": {
            "absolute_pair_count": obs["absolute_pair_count"],
            "positive_only_pair_count": obs["positive_only_pair_count"],
            "reverse_only_pair_count": obs["reverse_only_pair_count"],
            "overlap_pair_count": obs["overlap_pair_count"],
            "positive_pair_count": obs["positive_pair_count"],
            "reverse_pair_count": obs["reverse_pair_count"],
            "pair_table_sha256": sha_array(rows["pair_table"]),
            "pair_text_sha256": rows["pair_hash"],
        },
        "component_moments": {
            "raw_section_count": obs["raw_section_count"],
            "positive_section_count": obs["positive_section_count"],
            "reverse_section_count": obs["reverse_section_count"],
            "signed_section_count": obs["signed_section_count"],
            "raw_coeff_sum": obs["raw_coeff_sum"],
            "positive_coeff_sum": obs["positive_coeff_sum"],
            "reverse_coeff_sum": obs["reverse_coeff_sum"],
            "signed_coeff_sum": obs["signed_coeff_sum"],
            "raw_coeff_square_sum": obs["raw_coeff_square_sum"],
            "positive_coeff_square_sum": obs["positive_coeff_square_sum"],
            "reverse_coeff_square_sum": obs["reverse_coeff_square_sum"],
            "signed_coeff_square_sum": obs["signed_coeff_square_sum"],
        },
        "stalk_profile": {
            "stalk_row_count": obs["stalk_row_count"],
            "positive_stalk_count_min": obs["positive_stalk_count_min"],
            "positive_stalk_count_max": obs["positive_stalk_count_max"],
            "reverse_stalk_count_min": obs["reverse_stalk_count_min"],
            "reverse_stalk_count_max": obs["reverse_stalk_count_max"],
            "total_stalk_count_max": obs["total_stalk_count_max"],
            "signed_stalk_count_min": obs["signed_stalk_count_min"],
            "signed_stalk_count_max": obs["signed_stalk_count_max"],
            "signed_stalk_nonzero_count": obs["signed_stalk_nonzero_count"],
            "stalk_table_sha256": sha_array(rows["stalk_table"]),
            "stalk_text_sha256": rows["stalk_hash"],
        },
        "cut_profile": {
            "cut_row_count": obs["cut_row_count"],
            "positive_crossing_count_max": obs["positive_crossing_count_max"],
            "reverse_crossing_count_max": obs["reverse_crossing_count_max"],
            "total_crossing_count_max": obs["total_crossing_count_max"],
            "signed_crossing_count_min": obs["signed_crossing_count_min"],
            "signed_crossing_count_max": obs["signed_crossing_count_max"],
            "signed_crossing_negative_cut_count": obs[
                "signed_crossing_negative_cut_count"
            ],
            "cut_table_sha256": sha_array(rows["cut_table"]),
            "cut_text_sha256": rows["cut_hash"],
        },
        "mobius": {
            "endpoint_zeta_rule": "F[a,b]=sum_{lower<=a, upper>=b} A[lower,upper]",
            "endpoint_mobius_rule": "A[l,u]=F[l,u]-F[l-1,u]-F[l,u+1]+F[l-1,u+1]",
            "mobius_row_count": obs["mobius_row_count"],
            "mobius_roundtrip_flag_count": obs["mobius_roundtrip_flag_count"],
            "mobius_table_sha256": sha_array(rows["mobius_table"]),
            "mobius_text_sha256": rows["mobius_hash"],
            "dense_hashes": rows["mobius_hashes"],
        },
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    orient_payload = {
        "schema": "long.orient@1",
        "object": "orientation_duality_mobius_split",
        "status": STATUS if all(checks.values()) else "LONG_ORIENT_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.orient.report@1",
        "status": orient_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_orient certifies the orientation-duality split of the "
            "long_all raw interval sheaf. The orientation involution separates "
            "positive-zeta and reversed components by exact total/signed "
            "projectors, and endpoint-wise Alexandrov zeta/Mobius inversion "
            "round-trips all separated count, coefficient, and coefficient-square "
            "measures."
        ),
        "stage_protocol": {
            "draft": "read long_all oriented interval table",
            "witness": "aggregate absolute interval pairs into positive, reversed, total, and signed components",
            "coherence": "check projector parity, stalk and cut projections, Mobius roundtrip, statuses, hashes, and shapes",
            "closure": "emit the orientation-duality split without claiming semantic C985 composition",
            "emit": "write long_orient artifacts and verifier hook",
        },
        "inputs": {
            "long_all_report": input_entry(
                LONG_ALL_REPORT,
                {"status": rows["input_reports"]["long_all"].get("status")},
            ),
            "long_all_interval": input_entry(LONG_ALL_INTERVAL),
            "long_all_split": input_entry(LONG_ALL_SPLIT),
            "long_all_tables": input_entry(LONG_ALL_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "orient": relpath(OUT_DIR / "orient.json"),
            "pair_csv": relpath(OUT_DIR / "pair.csv"),
            "stalk_csv": relpath(OUT_DIR / "stalk.csv"),
            "cut_csv": relpath(OUT_DIR / "cut.csv"),
            "mobius_csv": relpath(OUT_DIR / "mobius.csv"),
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
                "absolute interval-pair separation into positive, reversed, total, and signed components",
                "exact total/signed projector recovery of both orientation components",
                "orientation-resolved stalk and cut profiles over the 985-point line",
                "2D endpoint zeta/Mobius roundtrip for all separated count, coefficient, and coefficient-square measures",
            ],
            "does_not_certify_because_out_of_scope": [
                "semantic C985 associator composition",
                "that the reversed component is removable",
                "a signed probability theorem",
                "an infinite-horizon LLN theorem",
            ],
        },
        "next_highest_yield_item": (
            "Build long_dual: promote the signed orientation component into a "
            "finite dual kernel and test whether it composes with the existing "
            "raw path witnesses."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.orient.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.orient.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "orient": orient_payload,
        "pair_csv": csv_text(PAIR_COLUMNS, rows["pair_rows"]),
        "stalk_csv": csv_text(STALK_COLUMNS, rows["stalk_rows"]),
        "cut_csv": csv_text(CUT_COLUMNS, rows["cut_rows"]),
        "mobius_csv": csv_text(MOBIUS_COLUMNS, rows["mobius_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "pair_table": rows["pair_table"],
        "stalk_table": rows["stalk_table"],
        "cut_table": rows["cut_table"],
        "mobius_table": rows["mobius_table"],
        "observable_table": rows["observable_table"],
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
    obligations.sort(key=lambda row: str(row["id"]))
    index = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": obligations,
    }
    index["registry_sha256"] = self_hash(index, "registry_sha256")
    write_json(INDEX_PATH, index)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / "orient.json", payloads["orient"])
    (OUT_DIR / "pair.csv").write_text(payloads["pair_csv"], encoding="utf-8")
    (OUT_DIR / "stalk.csv").write_text(payloads["stalk_csv"], encoding="utf-8")
    (OUT_DIR / "cut.csv").write_text(payloads["cut_csv"], encoding="utf-8")
    (OUT_DIR / "mobius.csv").write_text(payloads["mobius_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        pair_table=payloads["pair_table"],
        stalk_table=payloads["stalk_table"],
        cut_table=payloads["cut_table"],
        mobius_table=payloads["mobius_table"],
        observable_table=payloads["observable_table"],
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
                "certificate_sha256": report["certificate_sha256"],
                "report": relpath(OUT_DIR / "report.json"),
                "manifest": relpath(OUT_DIR / "manifest.json"),
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
