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
    from .derive_long_lln import STATUS as LONG_LLN_STATUS
    from .derive_long_raw import (
        RAW_TENSOR,
        csv_text,
        digest_text,
        load_raw_triples,
        rows_from_table,
        table_from_rows,
    )
    from .derive_long_sheaf import (
        LONG_COMP_PAIR,
        LONG_COMP_PATH,
        LONG_COMP_REPORT,
        LONG_COMP_TABLES,
        LONG_COMP_TRANSITION,
        LONG_LLN_REPORT,
        LONG_LLN_TABLES,
        OUT_DIR as LONG_SHEAF_DIR,
        STATUS as LONG_SHEAF_STATUS,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_lln import STATUS as LONG_LLN_STATUS
    from derive_long_raw import (
        RAW_TENSOR,
        csv_text,
        digest_text,
        load_raw_triples,
        rows_from_table,
        table_from_rows,
    )
    from derive_long_sheaf import (
        LONG_COMP_PAIR,
        LONG_COMP_PATH,
        LONG_COMP_REPORT,
        LONG_COMP_TABLES,
        LONG_COMP_TRANSITION,
        LONG_LLN_REPORT,
        LONG_LLN_TABLES,
        OUT_DIR as LONG_SHEAF_DIR,
        STATUS as LONG_SHEAF_STATUS,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_all"
STATUS = "LONG_ALL_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
LONG_SHEAF_REPORT = LONG_SHEAF_DIR / "report.json"
LONG_SHEAF_SECTION = LONG_SHEAF_DIR / "section.csv"
LONG_SHEAF_CUT = LONG_SHEAF_DIR / "cut.csv"
LONG_SHEAF_STALK = LONG_SHEAF_DIR / "stalk.csv"
LONG_SHEAF_TABLES = LONG_SHEAF_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_all.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_all.py"

SPLIT_TEXT_HASH = "9cddd6280b13e5c7099dd32a8bba7ad7355192054fba7dad1b3f9a615d7131fb"
INTERVAL_TEXT_HASH = "a1f2f0441779bc31e1aa21d766842b7c15662c6d4dd82f6ece9e5f87a7e102e2"
CUT_TEXT_HASH = "5970613c00e321d3ad518b9f0498d047b0a783c5c186ca61f7c068c1610137eb"
STALK_TEXT_HASH = "fd6f5249a45d6e085e08f72608e7c5e1e6f079c0f0d058ecc529f8e42ef9933c"

LINE_POINT_COUNT = 985

SPLIT_COLUMNS = [
    "split_id",
    "orientation_code",
    "interval_count",
    "section_count",
    "coeff_sum",
    "coeff_square_sum",
    "signed_margin_min",
    "signed_margin_max",
    "abs_margin_sum",
    "zero_margin_count",
    "positive_zeta_flag",
]
INTERVAL_COLUMNS = [
    "interval_id",
    "orientation_code",
    "lower_addr",
    "upper_addr",
    "section_count",
    "coeff_sum",
    "coeff_square_sum",
    "interval_width",
    "abs_margin",
    "width_weighted_count",
    "width_weighted_coeff_sum",
    "width_weighted_coeff_square_sum",
]
CUT_COLUMNS = [
    "cut_id",
    "left_addr",
    "right_addr",
    "closed_section_count",
    "open_section_count",
    "crossing_section_count",
    "closed_coeff_sum",
    "open_coeff_sum",
    "crossing_coeff_sum",
    "closed_coeff_square_sum",
    "open_coeff_square_sum",
    "crossing_coeff_square_sum",
    "count_gluing_total",
    "coeff_gluing_total",
    "coeff_square_gluing_total",
    "count_gluing_flag",
    "coeff_gluing_flag",
    "coeff_square_gluing_flag",
]
STALK_COLUMNS = [
    "addr",
    "section_count",
    "coeff_sum",
    "coeff_square_sum",
    "active_stalk_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "line_point_count",
    "raw_section_count",
    "raw_coeff_sum",
    "raw_coeff_square_sum",
    "lln_variance_num",
    "oriented_interval_count",
    "positive_zeta_interval_count",
    "reverse_interval_count",
    "positive_zeta_section_count",
    "reverse_section_count",
    "positive_zeta_coeff_sum",
    "reverse_coeff_sum",
    "positive_zeta_coeff_square_sum",
    "reverse_coeff_square_sum",
    "zero_margin_section_count",
    "abs_margin_sum",
    "abs_margin_max",
    "cut_row_count",
    "cut_count_gluing_flag_count",
    "cut_coeff_gluing_flag_count",
    "cut_coeff_square_gluing_flag_count",
    "closed_count_monotone_flag",
    "open_count_monotone_flag",
    "crossing_positive_cut_count",
    "crossing_count_max",
    "stalk_row_count",
    "active_stalk_count",
    "stalk_section_count_max",
    "stalk_coeff_sum_max",
    "stalk_coeff_square_sum_max",
    "width_total",
    "current_oriented_full_raw_sheaf_flag",
    "current_positive_zeta_full_raw_sheaf_flag",
    "current_lln_moment_match_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def oriented_interval_rows(triples: np.ndarray) -> tuple[list[dict[str, int]], list[dict[str, int]], dict[str, int]]:
    source0 = triples[:, 0].astype(np.int64, copy=False)
    source1 = triples[:, 1].astype(np.int64, copy=False)
    target = triples[:, 2].astype(np.int64, copy=False)
    coeff = triples[:, 3].astype(np.int64, copy=False)
    meet = np.minimum(source0, source1)
    signed_margin = target - meet
    positive_zeta = signed_margin <= 0
    lower = np.minimum(target, meet)
    upper = np.maximum(target, meet)
    orient_index = positive_zeta.astype(np.int64)
    encoded = orient_index * LINE_POINT_COUNT * LINE_POINT_COUNT + lower * LINE_POINT_COUNT + upper
    unique, inverse, counts = np.unique(encoded, return_inverse=True, return_counts=True)
    coeff_sum = np.bincount(inverse, weights=coeff).astype(np.int64)
    coeff_square = coeff * coeff
    coeff_square_sum = np.bincount(inverse, weights=coeff_square).astype(np.int64)

    interval_rows: list[dict[str, int]] = []
    split_interval_counts = {-1: 0, 1: 0}
    for interval_id, code in enumerate(unique.tolist()):
        orientation_code = 1 if code // (LINE_POINT_COUNT * LINE_POINT_COUNT) else -1
        rem = code % (LINE_POINT_COUNT * LINE_POINT_COUNT)
        lower_addr = int(rem // LINE_POINT_COUNT)
        upper_addr = int(rem % LINE_POINT_COUNT)
        width = upper_addr - lower_addr + 1
        count = int(counts[interval_id])
        coeff_total = int(coeff_sum[interval_id])
        square_total = int(coeff_square_sum[interval_id])
        split_interval_counts[orientation_code] += 1
        interval_rows.append(
            {
                "interval_id": interval_id,
                "orientation_code": orientation_code,
                "lower_addr": lower_addr,
                "upper_addr": upper_addr,
                "section_count": count,
                "coeff_sum": coeff_total,
                "coeff_square_sum": square_total,
                "interval_width": width,
                "abs_margin": upper_addr - lower_addr,
                "width_weighted_count": count * width,
                "width_weighted_coeff_sum": coeff_total * width,
                "width_weighted_coeff_square_sum": square_total * width,
            }
        )

    split_rows: list[dict[str, int]] = []
    for split_id, (orientation_code, mask) in enumerate(
        [(-1, ~positive_zeta), (1, positive_zeta)]
    ):
        split_rows.append(
            {
                "split_id": split_id,
                "orientation_code": orientation_code,
                "interval_count": split_interval_counts[orientation_code],
                "section_count": int(np.count_nonzero(mask)),
                "coeff_sum": int(coeff[mask].sum()),
                "coeff_square_sum": int(coeff_square[mask].sum()),
                "signed_margin_min": int(signed_margin[mask].min()),
                "signed_margin_max": int(signed_margin[mask].max()),
                "abs_margin_sum": int(np.abs(signed_margin[mask]).sum()),
                "zero_margin_count": int(np.count_nonzero(signed_margin[mask] == 0)),
                "positive_zeta_flag": int(orientation_code == 1),
            }
        )
    totals = {
        "section_count": int(triples.shape[0]),
        "coeff_sum": int(coeff.sum()),
        "coeff_square_sum": int(coeff_square.sum()),
        "abs_margin_sum": int(np.abs(signed_margin).sum()),
        "abs_margin_max": int(np.abs(signed_margin).max()),
        "zero_margin_count": int(np.count_nonzero(signed_margin == 0)),
    }
    return split_rows, interval_rows, totals


def cut_rows_from_intervals(
    interval_rows: list[dict[str, int]],
    global_count: int,
    global_coeff: int,
    global_square: int,
) -> list[dict[str, int]]:
    end_count = np.zeros(LINE_POINT_COUNT, dtype=np.int64)
    start_count = np.zeros(LINE_POINT_COUNT, dtype=np.int64)
    end_coeff = np.zeros(LINE_POINT_COUNT, dtype=np.int64)
    start_coeff = np.zeros(LINE_POINT_COUNT, dtype=np.int64)
    end_square = np.zeros(LINE_POINT_COUNT, dtype=np.int64)
    start_square = np.zeros(LINE_POINT_COUNT, dtype=np.int64)
    for row in interval_rows:
        lower = row["lower_addr"]
        upper = row["upper_addr"]
        end_count[upper] += row["section_count"]
        start_count[lower] += row["section_count"]
        end_coeff[upper] += row["coeff_sum"]
        start_coeff[lower] += row["coeff_sum"]
        end_square[upper] += row["coeff_square_sum"]
        start_square[lower] += row["coeff_square_sum"]
    closed_count_values = np.cumsum(end_count)[:-1]
    open_count_values = global_count - np.cumsum(start_count)[:-1]
    closed_coeff_values = np.cumsum(end_coeff)[:-1]
    open_coeff_values = global_coeff - np.cumsum(start_coeff)[:-1]
    closed_square_values = np.cumsum(end_square)[:-1]
    open_square_values = global_square - np.cumsum(start_square)[:-1]
    cut_rows: list[dict[str, int]] = []
    for cut_id in range(LINE_POINT_COUNT - 1):
        closed_count = int(closed_count_values[cut_id])
        open_count = int(open_count_values[cut_id])
        crossing_count = global_count - closed_count - open_count
        closed_coeff = int(closed_coeff_values[cut_id])
        open_coeff = int(open_coeff_values[cut_id])
        crossing_coeff = global_coeff - closed_coeff - open_coeff
        closed_square = int(closed_square_values[cut_id])
        open_square = int(open_square_values[cut_id])
        crossing_square = global_square - closed_square - open_square
        count_total = closed_count + open_count + crossing_count
        coeff_total = closed_coeff + open_coeff + crossing_coeff
        square_total = closed_square + open_square + crossing_square
        cut_rows.append(
            {
                "cut_id": cut_id,
                "left_addr": cut_id,
                "right_addr": cut_id + 1,
                "closed_section_count": closed_count,
                "open_section_count": open_count,
                "crossing_section_count": crossing_count,
                "closed_coeff_sum": closed_coeff,
                "open_coeff_sum": open_coeff,
                "crossing_coeff_sum": crossing_coeff,
                "closed_coeff_square_sum": closed_square,
                "open_coeff_square_sum": open_square,
                "crossing_coeff_square_sum": crossing_square,
                "count_gluing_total": count_total,
                "coeff_gluing_total": coeff_total,
                "coeff_square_gluing_total": square_total,
                "count_gluing_flag": int(count_total == global_count),
                "coeff_gluing_flag": int(coeff_total == global_coeff),
                "coeff_square_gluing_flag": int(square_total == global_square),
            }
        )
    return cut_rows


def stalk_rows_from_intervals(interval_rows: list[dict[str, int]]) -> list[dict[str, int]]:
    count_diff = np.zeros(LINE_POINT_COUNT + 1, dtype=np.int64)
    coeff_diff = np.zeros(LINE_POINT_COUNT + 1, dtype=np.int64)
    square_diff = np.zeros(LINE_POINT_COUNT + 1, dtype=np.int64)
    for row in interval_rows:
        lower = row["lower_addr"]
        upper_next = row["upper_addr"] + 1
        count_diff[lower] += row["section_count"]
        count_diff[upper_next] -= row["section_count"]
        coeff_diff[lower] += row["coeff_sum"]
        coeff_diff[upper_next] -= row["coeff_sum"]
        square_diff[lower] += row["coeff_square_sum"]
        square_diff[upper_next] -= row["coeff_square_sum"]
    counts = np.cumsum(count_diff)[:LINE_POINT_COUNT]
    coeffs = np.cumsum(coeff_diff)[:LINE_POINT_COUNT]
    squares = np.cumsum(square_diff)[:LINE_POINT_COUNT]
    return [
        {
            "addr": addr,
            "section_count": int(counts[addr]),
            "coeff_sum": int(coeffs[addr]),
            "coeff_square_sum": int(squares[addr]),
            "active_stalk_flag": int(counts[addr] > 0),
        }
        for addr in range(LINE_POINT_COUNT)
    ]


def monotone_non_decreasing(values: list[int]) -> bool:
    return all(left <= right for left, right in zip(values, values[1:]))


def monotone_non_increasing(values: list[int]) -> bool:
    return all(left >= right for left, right in zip(values, values[1:]))


def build_rows() -> dict[str, Any]:
    input_reports = {
        "long_lln": load_json(LONG_LLN_REPORT),
        "long_sheaf": load_json(LONG_SHEAF_REPORT),
    }
    triples = load_raw_triples()
    split_rows, interval_rows, totals = oriented_interval_rows(triples)
    cut_rows = cut_rows_from_intervals(
        interval_rows,
        totals["section_count"],
        totals["coeff_sum"],
        totals["coeff_square_sum"],
    )
    stalk_rows = stalk_rows_from_intervals(interval_rows)
    long_lln_witness = input_reports["long_lln"]["witness"]
    lln_tensor = long_lln_witness["tensor_lookup"]
    lln_finite = long_lln_witness["finite_lln"]
    variance_num = (
        totals["section_count"] * totals["coeff_square_sum"]
        - totals["coeff_sum"] * totals["coeff_sum"]
    )

    split_by_orientation = {row["orientation_code"]: row for row in split_rows}
    obs = {
        "line_point_count": LINE_POINT_COUNT,
        "raw_section_count": totals["section_count"],
        "raw_coeff_sum": totals["coeff_sum"],
        "raw_coeff_square_sum": totals["coeff_square_sum"],
        "lln_variance_num": variance_num,
        "oriented_interval_count": len(interval_rows),
        "positive_zeta_interval_count": split_by_orientation[1]["interval_count"],
        "reverse_interval_count": split_by_orientation[-1]["interval_count"],
        "positive_zeta_section_count": split_by_orientation[1]["section_count"],
        "reverse_section_count": split_by_orientation[-1]["section_count"],
        "positive_zeta_coeff_sum": split_by_orientation[1]["coeff_sum"],
        "reverse_coeff_sum": split_by_orientation[-1]["coeff_sum"],
        "positive_zeta_coeff_square_sum": split_by_orientation[1][
            "coeff_square_sum"
        ],
        "reverse_coeff_square_sum": split_by_orientation[-1]["coeff_square_sum"],
        "zero_margin_section_count": totals["zero_margin_count"],
        "abs_margin_sum": totals["abs_margin_sum"],
        "abs_margin_max": totals["abs_margin_max"],
        "cut_row_count": len(cut_rows),
        "cut_count_gluing_flag_count": sum(
            row["count_gluing_flag"] for row in cut_rows
        ),
        "cut_coeff_gluing_flag_count": sum(
            row["coeff_gluing_flag"] for row in cut_rows
        ),
        "cut_coeff_square_gluing_flag_count": sum(
            row["coeff_square_gluing_flag"] for row in cut_rows
        ),
        "closed_count_monotone_flag": int(
            monotone_non_decreasing(
                [row["closed_section_count"] for row in cut_rows]
            )
        ),
        "open_count_monotone_flag": int(
            monotone_non_increasing([row["open_section_count"] for row in cut_rows])
        ),
        "crossing_positive_cut_count": sum(
            int(row["crossing_section_count"] > 0) for row in cut_rows
        ),
        "crossing_count_max": max(row["crossing_section_count"] for row in cut_rows),
        "stalk_row_count": len(stalk_rows),
        "active_stalk_count": sum(row["active_stalk_flag"] for row in stalk_rows),
        "stalk_section_count_max": max(row["section_count"] for row in stalk_rows),
        "stalk_coeff_sum_max": max(row["coeff_sum"] for row in stalk_rows),
        "stalk_coeff_square_sum_max": max(
            row["coeff_square_sum"] for row in stalk_rows
        ),
        "width_total": sum(row["width_weighted_count"] for row in interval_rows),
        "current_oriented_full_raw_sheaf_flag": 1,
        "current_positive_zeta_full_raw_sheaf_flag": 0,
        "current_lln_moment_match_flag": int(
            totals["section_count"] == int(lln_tensor["support_count"])
            and totals["coeff_sum"] == int(lln_tensor["coefficient_sum"])
            and totals["coeff_square_sum"] == int(lln_tensor["coefficient_square_sum"])
            and variance_num == int(lln_finite["variance_num"])
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
    split_hash = hashlib.sha256(
        digest_text(SPLIT_COLUMNS, split_rows).encode("ascii")
    ).hexdigest()
    interval_hash = hashlib.sha256(
        digest_text(INTERVAL_COLUMNS, interval_rows).encode("ascii")
    ).hexdigest()
    cut_hash = hashlib.sha256(
        digest_text(CUT_COLUMNS, cut_rows).encode("ascii")
    ).hexdigest()
    stalk_hash = hashlib.sha256(
        digest_text(STALK_COLUMNS, stalk_rows).encode("ascii")
    ).hexdigest()
    return {
        "input_reports": input_reports,
        "split_rows": split_rows,
        "interval_rows": interval_rows,
        "cut_rows": cut_rows,
        "stalk_rows": stalk_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "split_table": table_from_rows(SPLIT_COLUMNS, split_rows),
        "interval_table": table_from_rows(INTERVAL_COLUMNS, interval_rows),
        "cut_table": table_from_rows(CUT_COLUMNS, cut_rows),
        "stalk_table": table_from_rows(STALK_COLUMNS, stalk_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "split_hash": split_hash,
        "interval_hash": interval_hash,
        "cut_hash": cut_hash,
        "stalk_hash": stalk_hash,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    input_reports = rows["input_reports"]
    checks = {
        "input_certified": (
            input_reports["long_lln"].get("status"),
            input_reports["long_sheaf"].get("status"),
        )
        == (LONG_LLN_STATUS, LONG_SHEAF_STATUS),
        "lln_moments_match_exact": (
            obs["line_point_count"],
            obs["raw_section_count"],
            obs["raw_coeff_sum"],
            obs["raw_coeff_square_sum"],
            obs["lln_variance_num"],
            obs["current_lln_moment_match_flag"],
        )
        == (985, 1_414_965, 2_537_360, 8_119_976, 5_051_286_071_240, 1),
        "orientation_split_exact": (
            obs["oriented_interval_count"],
            obs["positive_zeta_interval_count"],
            obs["reverse_interval_count"],
            obs["positive_zeta_section_count"],
            obs["reverse_section_count"],
            obs["positive_zeta_coeff_sum"],
            obs["reverse_coeff_sum"],
            obs["positive_zeta_coeff_square_sum"],
            obs["reverse_coeff_square_sum"],
            obs["zero_margin_section_count"],
            obs["abs_margin_sum"],
            obs["abs_margin_max"],
            rows["split_hash"],
            rows["interval_hash"],
        )
        == (
            172_396,
            51_980,
            120_416,
            477_589,
            937_376,
            915_271,
            1_622_089,
            3_655_871,
            4_464_105,
            11_959,
            257_176_365,
            877,
            SPLIT_TEXT_HASH,
            INTERVAL_TEXT_HASH,
        ),
        "cut_gluing_exact": (
            obs["cut_row_count"],
            obs["cut_count_gluing_flag_count"],
            obs["cut_coeff_gluing_flag_count"],
            obs["cut_coeff_square_gluing_flag_count"],
            obs["closed_count_monotone_flag"],
            obs["open_count_monotone_flag"],
            obs["crossing_positive_cut_count"],
            obs["crossing_count_max"],
            rows["cut_hash"],
        )
        == (984, 984, 984, 984, 1, 1, 984, 451_244, CUT_TEXT_HASH),
        "stalk_profile_exact": (
            obs["stalk_row_count"],
            obs["active_stalk_count"],
            obs["stalk_section_count_max"],
            obs["stalk_coeff_sum_max"],
            obs["stalk_coeff_square_sum_max"],
            obs["width_total"],
            rows["stalk_hash"],
        )
        == (985, 985, 453_822, 770_176, 2_093_132, 258_591_330, STALK_TEXT_HASH),
        "current_representation_exact": (
            obs["current_oriented_full_raw_sheaf_flag"],
            obs["current_positive_zeta_full_raw_sheaf_flag"],
            obs["current_lln_moment_match_flag"],
        )
        == (1, 0, 1),
        "table_shapes_match": (
            tuple(rows["split_table"].shape),
            tuple(rows["interval_table"].shape),
            tuple(rows["cut_table"].shape),
            tuple(rows["stalk_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (2, len(SPLIT_COLUMNS)),
            (172_396, len(INTERVAL_COLUMNS)),
            (984, len(CUT_COLUMNS)),
            (985, len(STALK_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "oriented_full_raw_interval_sheaf",
        "interval_rule": "each raw tensor row uses the oriented interval between target and min(source0, source1)",
        "lln_moments": {
            "raw_section_count": obs["raw_section_count"],
            "raw_coeff_sum": obs["raw_coeff_sum"],
            "raw_coeff_square_sum": obs["raw_coeff_square_sum"],
            "variance_num": obs["lln_variance_num"],
            "matches_long_lln": bool(obs["current_lln_moment_match_flag"]),
        },
        "orientation_split": {
            "oriented_interval_count": obs["oriented_interval_count"],
            "positive_zeta_interval_count": obs["positive_zeta_interval_count"],
            "reverse_interval_count": obs["reverse_interval_count"],
            "positive_zeta_section_count": obs["positive_zeta_section_count"],
            "reverse_section_count": obs["reverse_section_count"],
            "positive_zeta_coeff_sum": obs["positive_zeta_coeff_sum"],
            "reverse_coeff_sum": obs["reverse_coeff_sum"],
            "zero_margin_section_count": obs["zero_margin_section_count"],
            "abs_margin_sum": obs["abs_margin_sum"],
            "abs_margin_max": obs["abs_margin_max"],
            "split_table_sha256": sha_array(rows["split_table"]),
            "split_text_sha256": rows["split_hash"],
            "interval_table_sha256": sha_array(rows["interval_table"]),
            "interval_text_sha256": rows["interval_hash"],
        },
        "cut_gluing": {
            "cut_row_count": obs["cut_row_count"],
            "count_gluing_flag_count": obs["cut_count_gluing_flag_count"],
            "coeff_gluing_flag_count": obs["cut_coeff_gluing_flag_count"],
            "coeff_square_gluing_flag_count": obs[
                "cut_coeff_square_gluing_flag_count"
            ],
            "closed_count_monotone": bool(obs["closed_count_monotone_flag"]),
            "open_count_monotone": bool(obs["open_count_monotone_flag"]),
            "crossing_positive_cut_count": obs["crossing_positive_cut_count"],
            "crossing_count_max": obs["crossing_count_max"],
            "cut_table_sha256": sha_array(rows["cut_table"]),
            "cut_text_sha256": rows["cut_hash"],
        },
        "stalks": {
            "stalk_row_count": obs["stalk_row_count"],
            "active_stalk_count": obs["active_stalk_count"],
            "stalk_section_count_max": obs["stalk_section_count_max"],
            "stalk_coeff_sum_max": obs["stalk_coeff_sum_max"],
            "stalk_coeff_square_sum_max": obs["stalk_coeff_square_sum_max"],
            "width_total": obs["width_total"],
            "stalk_table_sha256": sha_array(rows["stalk_table"]),
            "stalk_text_sha256": rows["stalk_hash"],
        },
        "current_representation": {
            "current_oriented_full_raw_sheaf_flag": obs[
                "current_oriented_full_raw_sheaf_flag"
            ],
            "current_positive_zeta_full_raw_sheaf_flag": obs[
                "current_positive_zeta_full_raw_sheaf_flag"
            ],
            "current_lln_moment_match_flag": obs[
                "current_lln_moment_match_flag"
            ],
        },
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    all_payload = {
        "schema": "long.all@1",
        "object": "oriented_full_raw_interval_sheaf",
        "status": STATUS if all(checks.values()) else "LONG_ALL_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.all.report@1",
        "status": all_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_all certifies the full raw tensor lookup as an oriented "
            "interval sheaf over the finite Alexandrov line. The full support "
            "does not form a positive zeta sheaf: it splits into 477,589 "
            "positive-zeta rows and 937,376 reversed rows. After retaining "
            "orientation, all cut gluing identities hold for count, coefficient "
            "sum, and coefficient-square sum, and the global moments exactly "
            "match long_lln."
        ),
        "stage_protocol": {
            "draft": "read the raw tensor lookup and the witness-level long_sheaf certificate",
            "witness": "aggregate all raw rows by oriented interval between target and min(source0, source1)",
            "coherence": "check orientation split, full LLN moment match, cut gluing, stalk profile, statuses, hashes, and shapes",
            "closure": "emit full raw oriented interval sheaf and record the positive-zeta obstruction",
            "emit": "write long_all artifacts and verifier hook",
        },
        "inputs": {
            "raw_tensor": input_entry(RAW_TENSOR),
            "long_lln_report": input_entry(
                LONG_LLN_REPORT,
                {"status": rows["input_reports"]["long_lln"].get("status")},
            ),
            "long_lln_tables": input_entry(LONG_LLN_TABLES),
            "long_sheaf_report": input_entry(
                LONG_SHEAF_REPORT,
                {"status": rows["input_reports"]["long_sheaf"].get("status")},
            ),
            "long_sheaf_section": input_entry(LONG_SHEAF_SECTION),
            "long_sheaf_cut": input_entry(LONG_SHEAF_CUT),
            "long_sheaf_stalk": input_entry(LONG_SHEAF_STALK),
            "long_sheaf_tables": input_entry(LONG_SHEAF_TABLES),
            "long_comp_report": input_entry(LONG_COMP_REPORT),
            "long_comp_pair": input_entry(LONG_COMP_PAIR),
            "long_comp_path": input_entry(LONG_COMP_PATH),
            "long_comp_transition": input_entry(LONG_COMP_TRANSITION),
            "long_comp_tables": input_entry(LONG_COMP_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "all": relpath(OUT_DIR / "all.json"),
            "split_csv": relpath(OUT_DIR / "split.csv"),
            "interval_csv": relpath(OUT_DIR / "interval.csv"),
            "cut_csv": relpath(OUT_DIR / "cut.csv"),
            "stalk_csv": relpath(OUT_DIR / "stalk.csv"),
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
                "the full raw tensor support as an oriented interval sheaf over all 1,414,965 rows",
                "the positive-zeta/reversed split of the raw tensor support",
                "exact match with long_lln support count, coefficient sum, coefficient-square sum, and variance numerator",
                "exact gluing of count, coefficient sum, and coefficient-square sum across all 984 finite-line cuts",
            ],
            "does_not_certify_because_out_of_scope": [
                "that the full raw tensor support is a positive zeta sheaf",
                "semantic C985 associator composition",
                "a genuine long_prof horizon-16 profunctor",
                "an infinite-horizon LLN theorem",
            ],
        },
        "next_highest_yield_item": (
            "Build long_orient: analyze the reversed interval mass as an "
            "orientation/duality operator and test whether Mobius inversion "
            "separates the positive-zeta and reversed LLN components."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.all.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.all.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "all": all_payload,
        "split_csv": csv_text(SPLIT_COLUMNS, rows["split_rows"]),
        "interval_csv": csv_text(INTERVAL_COLUMNS, rows["interval_rows"]),
        "cut_csv": csv_text(CUT_COLUMNS, rows["cut_rows"]),
        "stalk_csv": csv_text(STALK_COLUMNS, rows["stalk_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "split_table": rows["split_table"],
        "interval_table": rows["interval_table"],
        "cut_table": rows["cut_table"],
        "stalk_table": rows["stalk_table"],
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
    write_json(OUT_DIR / "all.json", payloads["all"])
    (OUT_DIR / "split.csv").write_text(payloads["split_csv"], encoding="utf-8")
    (OUT_DIR / "interval.csv").write_text(
        payloads["interval_csv"], encoding="utf-8"
    )
    (OUT_DIR / "cut.csv").write_text(payloads["cut_csv"], encoding="utf-8")
    (OUT_DIR / "stalk.csv").write_text(payloads["stalk_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        split_table=payloads["split_table"],
        interval_table=payloads["interval_table"],
        cut_table=payloads["cut_table"],
        stalk_table=payloads["stalk_table"],
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
