from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from fractions import Fraction
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
    from .derive_long_mart import (
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_TABLES,
        LONG_PROB_REPORT,
        LONG_PROB_TABLES,
        OUT_DIR as LONG_MART_DIR,
        STATUS as LONG_MART_STATUS,
        fiber_moments,
        grouped_weights,
        transport_edges,
    )
    from .derive_long_path import STATUS as LONG_PATH_STATUS
    from .derive_long_prob import (
        STATUS as LONG_PROB_STATUS,
        prefixed_fraction_columns,
        prefixed_fraction_fields,
    )
    from .derive_long_raw import (
        csv_text,
        digest_text,
        int_rows,
        read_csv_rows,
        rows_from_table,
        table_from_rows,
    )
    from .derive_long_stop import OUT_DIR as LONG_STOP_DIR, STATUS as LONG_STOP_STATUS
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_mart import (
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_TABLES,
        LONG_PROB_REPORT,
        LONG_PROB_TABLES,
        OUT_DIR as LONG_MART_DIR,
        STATUS as LONG_MART_STATUS,
        fiber_moments,
        grouped_weights,
        transport_edges,
    )
    from derive_long_path import STATUS as LONG_PATH_STATUS
    from derive_long_prob import (
        STATUS as LONG_PROB_STATUS,
        prefixed_fraction_columns,
        prefixed_fraction_fields,
    )
    from derive_long_raw import (
        csv_text,
        digest_text,
        int_rows,
        read_csv_rows,
        rows_from_table,
        table_from_rows,
    )
    from derive_long_stop import OUT_DIR as LONG_STOP_DIR, STATUS as LONG_STOP_STATUS
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_dlim"
STATUS = "LONG_DLIM_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
LONG_MART_REPORT = LONG_MART_DIR / "report.json"
LONG_MART_STATE = LONG_MART_DIR / "state.csv"
LONG_MART_LEVEL = LONG_MART_DIR / "level.csv"
LONG_MART_TABLES = LONG_MART_DIR / "tables.npz"
LONG_STOP_REPORT = LONG_STOP_DIR / "report.json"
LONG_STOP_STOP = LONG_STOP_DIR / "stop.csv"
LONG_STOP_TAIL = LONG_STOP_DIR / "tail.csv"
LONG_STOP_TABLES = LONG_STOP_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_dlim.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_dlim.py"

STATE_TEXT_HASH = "f468740a68c071dae2a2f2accbd81609e356d6c3e1dd6eb0dca624811eee54cd"
LEVEL_TEXT_HASH = "a0678fe4d0502a09f1d33d3095ef9f6898c5677cfc1499dc69031c6bd80e5955"
CONE_TEXT_HASH = "5bf07949ef8c9792fd78858ed07fed61085b0356d6382f640cd0db607eac0444"
DEFECT_TEXT_HASH = "0365cdd464ea71f05473a2269cba00262920d157a3bcc6d0ea1ad67651b2fda0"

MOD_PRIMES = (1_000_000_007, 1_000_000_009)

STATE_COLUMNS = [
    "state_id",
    "sample_count",
    "sum_value",
    "outgoing_edge_count",
    "current_average_num",
    "current_average_den",
    *prefixed_fraction_columns("expected_next_average"),
    *prefixed_fraction_columns("drift"),
    *prefixed_fraction_columns("abs_drift"),
    *prefixed_fraction_columns("source_probability"),
    "drift_sign",
    "eventual_cone_flag",
    "boundary_defect_flag",
]
LEVEL_COLUMNS = [
    "sample_count",
    "state_count",
    "drift_positive_count",
    "drift_negative_count",
    "drift_zero_count",
    "rowwise_nonnegative_flag",
    "eventual_cone_flag",
    "boundary_defect_level_flag",
    "variance_shrink_flag",
    *prefixed_fraction_columns("negative_mass"),
    *prefixed_fraction_columns("positive_mass"),
    *prefixed_fraction_columns("zero_mass"),
    *prefixed_fraction_columns("mean_drift"),
    *prefixed_fraction_columns("min_drift"),
    *prefixed_fraction_columns("max_drift"),
]
CONE_COLUMNS = [
    "cone_id",
    "start_sample_count",
    "end_sample_count",
    "level_count",
    "state_count",
    "drift_positive_count",
    "drift_negative_count",
    "drift_zero_count",
    "rowwise_nonnegative_level_count",
    "variance_shrink_level_count",
    "cone_nonnegative_flag",
    *prefixed_fraction_columns("negative_mass_total"),
    *prefixed_fraction_columns("mean_drift_total"),
    *prefixed_fraction_columns("min_drift"),
    *prefixed_fraction_columns("max_drift"),
]
DEFECT_COLUMNS = [
    "defect_id",
    "state_id",
    "sample_count",
    "sum_value",
    "outgoing_edge_count",
    "current_average_num",
    "current_average_den",
    "expected_next_average_num",
    "expected_next_average_den",
    "drift_num",
    "drift_den",
    "source_weight",
    "source_total",
    "source_probability_num",
    "source_probability_den",
    "boundary_defect_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "state_row_count",
    "level_row_count",
    "cone_row_count",
    "defect_row_count",
    "drift_positive_count",
    "drift_negative_count",
    "drift_zero_count",
    "boundary_state_count",
    "boundary_negative_count",
    "eventual_level_count",
    "eventual_state_count",
    "eventual_negative_count",
    "eventual_zero_count",
    "variance_shrink_level_count",
    "tail_gap_nonnegative_count",
    "stopped_tail_gap_nonnegative_count",
    "defect_sample_count",
    "defect_sum_value",
    "defect_drift_num_mod_1000000007",
    "defect_drift_den_mod_1000000007",
    "defect_source_probability_num",
    "defect_source_probability_den",
    "max_outgoing_edge_count",
    "state_abs_drift_num_mod_sum_1000000007",
    "level_mean_drift_num_mod_sum_1000000007",
    "cone_negative_mass_num_mod_sum_1000000007",
    "input_long_prob_certified",
    "input_long_path_certified",
    "input_long_mart_certified",
    "input_long_stop_certified",
    "current_single_boundary_defect_flag",
    "current_eventual_cone_flag",
    "current_stopped_tail_bridge_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def load_inputs() -> dict[str, Any]:
    return {
        "path_rows": int_rows(read_csv_rows(LONG_PATH_PATH)),
        "input_reports": {
            "long_prob": load_json(LONG_PROB_REPORT),
            "long_path": load_json(LONG_PATH_REPORT),
            "long_mart": load_json(LONG_MART_REPORT),
            "long_stop": load_json(LONG_STOP_REPORT),
        },
    }


def sign(value: Fraction) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def exact_transport_rows(path_rows: list[dict[str, int]]) -> dict[str, Any]:
    groups = grouped_weights(path_rows)
    state_rows: list[dict[str, int]] = []
    level_rows: list[dict[str, int]] = []
    defect_rows: list[dict[str, int]] = []
    exact_states: list[dict[str, Any]] = []
    state_id = 0
    for sample_count in range(1, max(groups)):
        source = groups[sample_count]
        target = groups[sample_count + 1]
        edges, source_total, target_total = transport_edges(source, target)
        _, source_mean, source_variance = fiber_moments(source, sample_count)
        _, target_mean, target_variance = fiber_moments(target, sample_count + 1)
        source_weight = {row["sum_value"]: row["weight"] for row in source}
        edge_by_source: dict[int, list[tuple[int, int]]] = defaultdict(list)
        for from_sum, to_sum, mass in edges:
            edge_by_source[from_sum].append((to_sum, mass))

        drift_records: list[dict[str, Any]] = []
        for row in source:
            source_sum = row["sum_value"]
            outgoing = edge_by_source[source_sum]
            actual_mass = sum(mass for _, mass in outgoing)
            expected_mass = row["weight"] * target_total
            if actual_mass != expected_mass:
                raise AssertionError("transport row mass mismatch")
            current_average = Fraction(source_sum, sample_count)
            expected_next = (
                sum(Fraction(to_sum, sample_count + 1) * mass for to_sum, mass in outgoing)
                / actual_mass
            )
            drift = expected_next - current_average
            source_probability = Fraction(row["weight"], source_total)
            drift_sign = sign(drift)
            boundary_defect = int(
                sample_count == 1 and source_sum == 2 and drift_sign < 0
            )
            state = {
                "state_id": state_id,
                "sample_count": sample_count,
                "sum_value": source_sum,
                "outgoing_edge_count": len(outgoing),
                "current_average_num": current_average.numerator,
                "current_average_den": current_average.denominator,
                "drift_sign": drift_sign,
                "eventual_cone_flag": int(sample_count >= 2 and drift_sign >= 0),
                "boundary_defect_flag": boundary_defect,
            }
            state.update(
                prefixed_fraction_fields("expected_next_average", expected_next)
            )
            state.update(prefixed_fraction_fields("drift", drift))
            state.update(prefixed_fraction_fields("abs_drift", abs(drift)))
            state.update(prefixed_fraction_fields("source_probability", source_probability))
            state_rows.append(state)
            record = {
                "state_id": state_id,
                "sample_count": sample_count,
                "sum_value": source_sum,
                "outgoing_edge_count": len(outgoing),
                "current_average": current_average,
                "expected_next": expected_next,
                "drift": drift,
                "source_weight": row["weight"],
                "source_total": source_total,
                "source_probability": source_probability,
                "drift_sign": drift_sign,
                "boundary_defect": boundary_defect,
            }
            exact_states.append(record)
            drift_records.append(record)
            if boundary_defect:
                defect_rows.append(
                    {
                        "defect_id": len(defect_rows),
                        "state_id": state_id,
                        "sample_count": sample_count,
                        "sum_value": source_sum,
                        "outgoing_edge_count": len(outgoing),
                        "current_average_num": current_average.numerator,
                        "current_average_den": current_average.denominator,
                        "expected_next_average_num": expected_next.numerator,
                        "expected_next_average_den": expected_next.denominator,
                        "drift_num": drift.numerator,
                        "drift_den": drift.denominator,
                        "source_weight": row["weight"],
                        "source_total": source_total,
                        "source_probability_num": source_probability.numerator,
                        "source_probability_den": source_probability.denominator,
                        "boundary_defect_flag": 1,
                    }
                )
            state_id += 1

        positive = [record for record in drift_records if record["drift"] > 0]
        negative = [record for record in drift_records if record["drift"] < 0]
        zero = [record for record in drift_records if record["drift"] == 0]
        mean_drift = sum(
            record["source_probability"] * record["drift"] for record in drift_records
        )
        if mean_drift != target_mean - source_mean:
            raise AssertionError("mean drift mismatch")
        shrink_gap = source_variance - target_variance
        level = {
            "sample_count": sample_count,
            "state_count": len(drift_records),
            "drift_positive_count": len(positive),
            "drift_negative_count": len(negative),
            "drift_zero_count": len(zero),
            "rowwise_nonnegative_flag": int(not negative),
            "eventual_cone_flag": int(sample_count >= 2 and not negative),
            "boundary_defect_level_flag": int(
                sample_count == 1 and len(negative) == 1
            ),
            "variance_shrink_flag": int(shrink_gap > 0),
        }
        level.update(
            prefixed_fraction_fields(
                "negative_mass",
                sum(record["source_probability"] for record in negative),
            )
        )
        level.update(
            prefixed_fraction_fields(
                "positive_mass",
                sum(record["source_probability"] for record in positive),
            )
        )
        level.update(
            prefixed_fraction_fields(
                "zero_mass",
                sum(record["source_probability"] for record in zero),
            )
        )
        level.update(prefixed_fraction_fields("mean_drift", mean_drift))
        level.update(
            prefixed_fraction_fields(
                "min_drift", min(record["drift"] for record in drift_records)
            )
        )
        level.update(
            prefixed_fraction_fields(
                "max_drift", max(record["drift"] for record in drift_records)
            )
        )
        level_rows.append(level)
    return {
        "state_rows": state_rows,
        "level_rows": level_rows,
        "defect_rows": defect_rows,
        "exact_states": exact_states,
    }


def build_cone_rows(
    exact_states: list[dict[str, Any]],
    level_rows: list[dict[str, int]],
) -> list[dict[str, int]]:
    cone_specs = [(0, 1, 1), (1, 2, 15)]
    cone_rows: list[dict[str, int]] = []
    levels_by_sample = {row["sample_count"]: row for row in level_rows}
    for cone_id, start, end in cone_specs:
        states = [
            row
            for row in exact_states
            if start <= row["sample_count"] <= end
        ]
        levels = [levels_by_sample[sample_count] for sample_count in range(start, end + 1)]
        positive = [row for row in states if row["drift"] > 0]
        negative = [row for row in states if row["drift"] < 0]
        zero = [row for row in states if row["drift"] == 0]
        row = {
            "cone_id": cone_id,
            "start_sample_count": start,
            "end_sample_count": end,
            "level_count": len(levels),
            "state_count": len(states),
            "drift_positive_count": len(positive),
            "drift_negative_count": len(negative),
            "drift_zero_count": len(zero),
            "rowwise_nonnegative_level_count": sum(
                level["rowwise_nonnegative_flag"] for level in levels
            ),
            "variance_shrink_level_count": sum(
                level["variance_shrink_flag"] for level in levels
            ),
            "cone_nonnegative_flag": int(not negative),
        }
        row.update(
            prefixed_fraction_fields(
                "negative_mass_total",
                sum(state["source_probability"] for state in negative),
            )
        )
        row.update(
            prefixed_fraction_fields(
                "mean_drift_total",
                sum(
                    state["source_probability"] * state["drift"]
                    for state in states
                ),
            )
        )
        row.update(
            prefixed_fraction_fields("min_drift", min(state["drift"] for state in states))
        )
        row.update(
            prefixed_fraction_fields("max_drift", max(state["drift"] for state in states))
        )
        cone_rows.append(row)
    return cone_rows


def build_rows() -> dict[str, Any]:
    loaded = load_inputs()
    transport = exact_transport_rows(loaded["path_rows"])
    state_rows = transport["state_rows"]
    level_rows = transport["level_rows"]
    defect_rows = transport["defect_rows"]
    cone_rows = build_cone_rows(transport["exact_states"], level_rows)
    stop_report = loaded["input_reports"]["long_stop"]
    stop_witness = stop_report.get("witness", {})
    tail_gap_count = int(stop_witness.get("tail", {}).get("gap_nonnegative_count", -1))
    stopped_gap_count = int(
        stop_witness.get("stopped_tail", {}).get("gap_nonnegative_count", -1)
    )
    eventual_levels = [row for row in level_rows if row["sample_count"] >= 2]
    boundary_levels = [row for row in level_rows if row["sample_count"] == 1]
    defect = defect_rows[0] if defect_rows else {}
    obs = {
        "state_row_count": len(state_rows),
        "level_row_count": len(level_rows),
        "cone_row_count": len(cone_rows),
        "defect_row_count": len(defect_rows),
        "drift_positive_count": sum(row["drift_positive_count"] for row in level_rows),
        "drift_negative_count": sum(row["drift_negative_count"] for row in level_rows),
        "drift_zero_count": sum(row["drift_zero_count"] for row in level_rows),
        "boundary_state_count": sum(row["state_count"] for row in boundary_levels),
        "boundary_negative_count": sum(
            row["drift_negative_count"] for row in boundary_levels
        ),
        "eventual_level_count": len(eventual_levels),
        "eventual_state_count": sum(row["state_count"] for row in eventual_levels),
        "eventual_negative_count": sum(
            row["drift_negative_count"] for row in eventual_levels
        ),
        "eventual_zero_count": sum(row["drift_zero_count"] for row in eventual_levels),
        "variance_shrink_level_count": sum(
            row["variance_shrink_flag"] for row in level_rows
        ),
        "tail_gap_nonnegative_count": tail_gap_count,
        "stopped_tail_gap_nonnegative_count": stopped_gap_count,
        "defect_sample_count": int(defect.get("sample_count", -1)),
        "defect_sum_value": int(defect.get("sum_value", -1)),
        "defect_drift_num_mod_1000000007": int(defect.get("drift_num", 0))
        % MOD_PRIMES[0],
        "defect_drift_den_mod_1000000007": int(defect.get("drift_den", 0))
        % MOD_PRIMES[0],
        "defect_source_probability_num": int(
            defect.get("source_probability_num", 0)
        ),
        "defect_source_probability_den": int(
            defect.get("source_probability_den", 0)
        ),
        "max_outgoing_edge_count": max(row["outgoing_edge_count"] for row in state_rows),
        "state_abs_drift_num_mod_sum_1000000007": sum(
            row["abs_drift_num_mod_1000000007"] for row in state_rows
        )
        % MOD_PRIMES[0],
        "level_mean_drift_num_mod_sum_1000000007": sum(
            row["mean_drift_num_mod_1000000007"] for row in level_rows
        )
        % MOD_PRIMES[0],
        "cone_negative_mass_num_mod_sum_1000000007": sum(
            row["negative_mass_total_num_mod_1000000007"] for row in cone_rows
        )
        % MOD_PRIMES[0],
        "input_long_prob_certified": int(
            loaded["input_reports"]["long_prob"].get("status") == LONG_PROB_STATUS
        ),
        "input_long_path_certified": int(
            loaded["input_reports"]["long_path"].get("status") == LONG_PATH_STATUS
        ),
        "input_long_mart_certified": int(
            loaded["input_reports"]["long_mart"].get("status") == LONG_MART_STATUS
        ),
        "input_long_stop_certified": int(
            loaded["input_reports"]["long_stop"].get("status") == LONG_STOP_STATUS
        ),
        "current_single_boundary_defect_flag": int(
            len(defect_rows) == 1
            and defect.get("sample_count") == 1
            and defect.get("sum_value") == 2
            and defect.get("drift_num") == -3
            and defect.get("drift_den") == 214
        ),
        "current_eventual_cone_flag": int(
            len(eventual_levels) == 14
            and sum(row["drift_negative_count"] for row in eventual_levels) == 0
        ),
        "current_stopped_tail_bridge_flag": int(
            tail_gap_count == 48 and stopped_gap_count == 48
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
    state_hash = hashlib.sha256(
        digest_text(STATE_COLUMNS, state_rows).encode("ascii")
    ).hexdigest()
    level_hash = hashlib.sha256(
        digest_text(LEVEL_COLUMNS, level_rows).encode("ascii")
    ).hexdigest()
    cone_hash = hashlib.sha256(
        digest_text(CONE_COLUMNS, cone_rows).encode("ascii")
    ).hexdigest()
    defect_hash = hashlib.sha256(
        digest_text(DEFECT_COLUMNS, defect_rows).encode("ascii")
    ).hexdigest()
    return {
        "input_reports": loaded["input_reports"],
        "state_rows": state_rows,
        "level_rows": level_rows,
        "cone_rows": cone_rows,
        "defect_rows": defect_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "state_table": table_from_rows(STATE_COLUMNS, state_rows),
        "level_table": table_from_rows(LEVEL_COLUMNS, level_rows),
        "cone_table": table_from_rows(CONE_COLUMNS, cone_rows),
        "defect_table": table_from_rows(DEFECT_COLUMNS, defect_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "state_hash": state_hash,
        "level_hash": level_hash,
        "cone_hash": cone_hash,
        "defect_hash": defect_hash,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    input_reports = rows["input_reports"]
    checks = {
        "input_certified": (
            obs["input_long_prob_certified"],
            obs["input_long_path_certified"],
            obs["input_long_mart_certified"],
            obs["input_long_stop_certified"],
        )
        == (1, 1, 1, 1),
        "drift_partition_exact": (
            obs["state_row_count"],
            obs["level_row_count"],
            obs["drift_positive_count"],
            obs["drift_negative_count"],
            obs["drift_zero_count"],
            obs["max_outgoing_edge_count"],
            obs["state_abs_drift_num_mod_sum_1000000007"],
            rows["state_hash"],
        )
        == (255, 15, 240, 1, 14, 3, 236_694_364, STATE_TEXT_HASH),
        "defect_exact": (
            obs["defect_row_count"],
            obs["defect_sample_count"],
            obs["defect_sum_value"],
            obs["defect_drift_num_mod_1000000007"],
            obs["defect_drift_den_mod_1000000007"],
            obs["defect_source_probability_num"],
            obs["defect_source_probability_den"],
            rows["defect_hash"],
        )
        == (
            1,
            1,
            2,
            1_000_000_004,
            214,
            8,
            13,
            DEFECT_TEXT_HASH,
        ),
        "eventual_cone_exact": (
            obs["cone_row_count"],
            obs["boundary_state_count"],
            obs["boundary_negative_count"],
            obs["eventual_level_count"],
            obs["eventual_state_count"],
            obs["eventual_negative_count"],
            obs["eventual_zero_count"],
            obs["variance_shrink_level_count"],
            obs["level_mean_drift_num_mod_sum_1000000007"],
            obs["cone_negative_mass_num_mod_sum_1000000007"],
            rows["level_hash"],
            rows["cone_hash"],
        )
        == (
            2,
            3,
            1,
            14,
            252,
            0,
            14,
            15,
            94_532_799,
            8,
            LEVEL_TEXT_HASH,
            CONE_TEXT_HASH,
        ),
        "stopped_tail_bridge_exact": (
            obs["tail_gap_nonnegative_count"],
            obs["stopped_tail_gap_nonnegative_count"],
            obs["current_stopped_tail_bridge_flag"],
        )
        == (48, 48, 1),
        "current_representation_exact": (
            obs["current_single_boundary_defect_flag"],
            obs["current_eventual_cone_flag"],
            obs["current_stopped_tail_bridge_flag"],
        )
        == (1, 1, 1),
        "table_shapes_match": (
            tuple(rows["state_table"].shape),
            tuple(rows["level_table"].shape),
            tuple(rows["cone_table"].shape),
            tuple(rows["defect_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (255, len(STATE_COLUMNS)),
            (15, len(LEVEL_COLUMNS)),
            (2, len(CONE_COLUMNS)),
            (1, len(DEFECT_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "finite_drift_limit_obstruction",
        "drift_partition": {
            "state_count": obs["state_row_count"],
            "level_count": obs["level_row_count"],
            "positive_count": obs["drift_positive_count"],
            "negative_count": obs["drift_negative_count"],
            "zero_count": obs["drift_zero_count"],
            "state_text_sha256": rows["state_hash"],
            "state_table_sha256": sha_array(rows["state_table"]),
        },
        "boundary_defect": {
            "defect_count": obs["defect_row_count"],
            "sample_count": obs["defect_sample_count"],
            "sum_value": obs["defect_sum_value"],
            "drift": "-3/214",
            "source_probability": "8/13",
            "defect_text_sha256": rows["defect_hash"],
            "defect_table_sha256": sha_array(rows["defect_table"]),
        },
        "eventual_cone": {
            "start_sample_count": 2,
            "end_sample_count": 15,
            "level_count": obs["eventual_level_count"],
            "state_count": obs["eventual_state_count"],
            "negative_count": obs["eventual_negative_count"],
            "zero_count": obs["eventual_zero_count"],
            "variance_shrink_level_count": obs["variance_shrink_level_count"],
            "level_text_sha256": rows["level_hash"],
            "level_table_sha256": sha_array(rows["level_table"]),
            "cone_text_sha256": rows["cone_hash"],
            "cone_table_sha256": sha_array(rows["cone_table"]),
        },
        "stopped_tail_bridge": {
            "tail_gap_nonnegative_count": obs["tail_gap_nonnegative_count"],
            "stopped_tail_gap_nonnegative_count": obs[
                "stopped_tail_gap_nonnegative_count"
            ],
        },
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    dlim_payload = {
        "schema": "long.dlim@1",
        "object": "finite_drift_limit_obstruction",
        "status": STATUS if all(checks.values()) else "LONG_DLIM_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.dlim.report@1",
        "status": dlim_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_dlim extracts the finite drift-limit obstruction from "
            "long_mart and long_stop. The transport has exactly one negative "
            "statewise drift, at sample_count=1 and sum_value=2 with drift "
            "-3/214 and source probability 8/13. From sample_count 2 through "
            "15, all 252 statewise drifts are nonnegative, while variance "
            "continues to shrink and the stopped-tail bridge remains certified."
        ),
        "stage_protocol": {
            "draft": "read long_mart transport, long_prob/path fibers, and long_stop stopped-tail bounds",
            "witness": "recompute exact statewise drifts and isolate the single boundary defect",
            "coherence": "check drift partition, defect row, eventual cone, stopped-tail bridge, statuses, hashes, and shapes",
            "closure": "emit finite drift-limit obstruction and eventual cone certificate",
            "emit": "write long_dlim artifacts and verifier hook",
        },
        "inputs": {
            "long_prob_report": input_entry(
                LONG_PROB_REPORT,
                {"status": input_reports["long_prob"].get("status")},
            ),
            "long_prob_tables": input_entry(LONG_PROB_TABLES),
            "long_path_report": input_entry(
                LONG_PATH_REPORT,
                {"status": input_reports["long_path"].get("status")},
            ),
            "long_path_path": input_entry(LONG_PATH_PATH),
            "long_path_tables": input_entry(LONG_PATH_TABLES),
            "long_mart_report": input_entry(
                LONG_MART_REPORT,
                {"status": input_reports["long_mart"].get("status")},
            ),
            "long_mart_state": input_entry(LONG_MART_STATE),
            "long_mart_level": input_entry(LONG_MART_LEVEL),
            "long_mart_tables": input_entry(LONG_MART_TABLES),
            "long_stop_report": input_entry(
                LONG_STOP_REPORT,
                {"status": input_reports["long_stop"].get("status")},
            ),
            "long_stop_tail": input_entry(LONG_STOP_TAIL),
            "long_stop_stop": input_entry(LONG_STOP_STOP),
            "long_stop_tables": input_entry(LONG_STOP_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "dlim": relpath(OUT_DIR / "dlim.json"),
            "state_csv": relpath(OUT_DIR / "state.csv"),
            "level_csv": relpath(OUT_DIR / "level.csv"),
            "cone_csv": relpath(OUT_DIR / "cone.csv"),
            "defect_csv": relpath(OUT_DIR / "defect.csv"),
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
                "the exact single negative statewise drift defect in the finite transport",
                "the eventual rowwise nonnegative drift cone from sample_count 2 through 15",
                "strict variance shrinkage across all 15 transport levels",
                "compatibility with the long_stop stopped-tail bounds",
            ],
            "does_not_certify_because_out_of_scope": [
                "an infinite-horizon drift theorem",
                "uniqueness of the monotone transport operator",
                "semantic C985 associator composition",
                "a public Markov-law martingale process",
            ],
        },
        "next_highest_yield_item": (
            "Build long_linf: test whether the eventual nonnegative drift cone "
            "extends under the next finite tensor lift, or whether a second "
            "boundary defect appears beyond horizon 16."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.dlim.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.dlim.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "dlim": dlim_payload,
        "state_csv": csv_text(STATE_COLUMNS, rows["state_rows"]),
        "level_csv": csv_text(LEVEL_COLUMNS, rows["level_rows"]),
        "cone_csv": csv_text(CONE_COLUMNS, rows["cone_rows"]),
        "defect_csv": csv_text(DEFECT_COLUMNS, rows["defect_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "state_table": rows["state_table"],
        "level_table": rows["level_table"],
        "cone_table": rows["cone_table"],
        "defect_table": rows["defect_table"],
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
    write_json(OUT_DIR / "dlim.json", payloads["dlim"])
    (OUT_DIR / "state.csv").write_text(payloads["state_csv"], encoding="utf-8")
    (OUT_DIR / "level.csv").write_text(payloads["level_csv"], encoding="utf-8")
    (OUT_DIR / "cone.csv").write_text(payloads["cone_csv"], encoding="utf-8")
    (OUT_DIR / "defect.csv").write_text(payloads["defect_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        state_table=payloads["state_table"],
        level_table=payloads["level_table"],
        cone_table=payloads["cone_table"],
        defect_table=payloads["defect_table"],
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
