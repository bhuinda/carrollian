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
    from .derive_long_dlim import OUT_DIR as LONG_DLIM_DIR, STATUS as LONG_DLIM_STATUS
    from .derive_long_dual import (
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_TABLES,
        OUT_DIR as LONG_DUAL_DIR,
        STATUS as LONG_DUAL_STATUS,
    )
    from .derive_long_path import STATUS as LONG_PATH_STATUS
    from .derive_long_prob import (
        LONG_DUAL_PATH,
        COMPONENT_WEIGHTS,
        STATUS as LONG_PROB_STATUS,
        OUT_DIR as LONG_PROB_DIR,
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
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_dlim import OUT_DIR as LONG_DLIM_DIR, STATUS as LONG_DLIM_STATUS
    from derive_long_dual import (
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_TABLES,
        OUT_DIR as LONG_DUAL_DIR,
        STATUS as LONG_DUAL_STATUS,
    )
    from derive_long_path import STATUS as LONG_PATH_STATUS
    from derive_long_prob import (
        LONG_DUAL_PATH,
        COMPONENT_WEIGHTS,
        STATUS as LONG_PROB_STATUS,
        OUT_DIR as LONG_PROB_DIR,
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
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_linf"
STATUS = "LONG_LINF_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

LONG_DUAL_REPORT = LONG_DUAL_DIR / "report.json"
LONG_DUAL_COMPONENT = LONG_DUAL_DIR / "component.csv"
LONG_DUAL_TABLES = LONG_DUAL_DIR / "tables.npz"
LONG_PROB_REPORT = LONG_PROB_DIR / "report.json"
LONG_PROB_TABLES = LONG_PROB_DIR / "tables.npz"
LONG_DLIM_REPORT = LONG_DLIM_DIR / "report.json"
LONG_DLIM_DEFECT = LONG_DLIM_DIR / "defect.csv"
LONG_DLIM_TABLES = LONG_DLIM_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_linf.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_linf.py"

BASE_HORIZON = 16
LIFT_HORIZON = 128

FIBER_TEXT_HASH = "06c9882402e8298a037b7e40d34d5a84c10288654a120fa5777ba52c6cc46d71"
STATE_TEXT_HASH = "07e9c3585c4e43c64d97784c5d4ebd77b35087f125fd62c750cee1d921e96f60"
LEVEL_TEXT_HASH = "f89cb668a6cc6adba9d27eff1f1ab58edde49672c5830acd5cc6f576996dcaed"
CONE_TEXT_HASH = "ec8c57cbf822dfe8cbb60c66f4f69ff67722fd82a08d820e1fa08b7fd06834b1"

MOD_PRIMES = (1_000_000_007, 1_000_000_009)

FIBER_COLUMNS = [
    "fiber_id",
    "sample_count",
    "sum_value",
    "count_component0",
    "count_component1",
    "count_component2",
    "weight_digits",
    "weight_mod_1000000007",
    "weight_mod_1000000009",
    "base_witness_match_flag",
    "lift_extension_flag",
]
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
    "base_level_flag",
    "lift_extension_flag",
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
    "base_level_flag",
    "lift_extension_flag",
    "variance_shrink_flag",
    *prefixed_fraction_columns("negative_mass"),
    *prefixed_fraction_columns("mean_drift"),
    *prefixed_fraction_columns("variance"),
    *prefixed_fraction_columns("variance_shrink_gap"),
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
    "lift_extension_flag",
    *prefixed_fraction_columns("negative_mass_total"),
    *prefixed_fraction_columns("mean_drift_total"),
    *prefixed_fraction_columns("min_drift"),
    *prefixed_fraction_columns("max_drift"),
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "base_horizon",
    "lift_horizon",
    "fiber_row_count",
    "state_row_count",
    "level_row_count",
    "cone_row_count",
    "base_fiber_match_count",
    "base_fiber_count",
    "lift_extension_fiber_count",
    "drift_positive_count",
    "drift_negative_count",
    "drift_zero_count",
    "boundary_negative_count",
    "extension_level_count",
    "extension_state_count",
    "extension_negative_count",
    "extension_zero_count",
    "eventual_level_count",
    "eventual_negative_count",
    "eventual_zero_count",
    "variance_shrink_level_count",
    "max_outgoing_edge_count",
    "state_abs_drift_num_mod_sum_1000000007",
    "level_mean_drift_num_mod_sum_1000000007",
    "last_variance_num_mod_1000000007",
    "last_variance_den_mod_1000000007",
    "input_long_dual_certified",
    "input_long_path_certified",
    "input_long_prob_certified",
    "input_long_dlim_certified",
    "current_measure_match_flag",
    "current_no_second_defect_flag",
    "current_lift_cone_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def load_inputs() -> dict[str, Any]:
    return {
        "long_dual_rows": int_rows(read_csv_rows(LONG_DUAL_PATH)),
        "long_path_rows": int_rows(read_csv_rows(LONG_PATH_PATH)),
        "component_rows": int_rows(read_csv_rows(LONG_DUAL_COMPONENT)),
        "input_reports": {
            "long_dual": load_json(LONG_DUAL_REPORT),
            "long_path": load_json(LONG_PATH_REPORT),
            "long_prob": load_json(LONG_PROB_REPORT),
            "long_dlim": load_json(LONG_DLIM_REPORT),
        },
    }


def canonical_counts(sample_count: int, sum_value: int) -> tuple[int, int, int]:
    count_component2 = max(0, sum_value - sample_count)
    count_component1 = sum_value - 2 * count_component2
    count_component0 = sample_count - count_component1 - count_component2
    if min(count_component0, count_component1, count_component2) < 0:
        raise AssertionError("invalid canonical counts")
    return count_component0, count_component1, count_component2


def canonical_weight(counts: tuple[int, int, int]) -> int:
    return (
        COMPONENT_WEIGHTS[0] ** counts[0]
        * COMPONENT_WEIGHTS[1] ** counts[1]
        * COMPONENT_WEIGHTS[2] ** counts[2]
    )


def sign(value: Fraction) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def build_fibers(
    long_path_rows: list[dict[str, int]],
    long_dual_rows: list[dict[str, int]],
) -> dict[int, list[dict[str, int]]]:
    path_by_key = {
        (row["sample_count"], row["sum_value"]): row for row in long_path_rows
    }
    dual_by_key = {}
    path_sample_by_id = {row["path_id"]: row for row in long_path_rows}
    for row in long_dual_rows:
        path = path_sample_by_id[row["path_id"]]
        dual_by_key[(path["sample_count"], path["sum_value"])] = row
    groups: dict[int, list[dict[str, int]]] = {}
    fiber_id = 0
    for sample_count in range(1, LIFT_HORIZON + 1):
        rows: list[dict[str, int]] = []
        for sum_value in range(0, 2 * sample_count + 1):
            counts = canonical_counts(sample_count, sum_value)
            weight = canonical_weight(counts)
            path = path_by_key.get((sample_count, sum_value))
            dual = dual_by_key.get((sample_count, sum_value))
            if sample_count <= BASE_HORIZON:
                base_match = int(
                    path is not None
                    and dual is not None
                    and (
                        path["count_component0"],
                        path["count_component1"],
                        path["count_component2"],
                    )
                    == counts
                    and dual["dual_coeff_product_mod_1000000007"]
                    == weight % MOD_PRIMES[0]
                    and dual["dual_coeff_product_mod_1000000009"]
                    == weight % MOD_PRIMES[1]
                )
            else:
                base_match = -1
            rows.append(
                {
                    "fiber_id": fiber_id,
                    "sample_count": sample_count,
                    "sum_value": sum_value,
                    "count_component0": counts[0],
                    "count_component1": counts[1],
                    "count_component2": counts[2],
                    "weight_digits": len(str(weight)),
                    "weight_mod_1000000007": weight % MOD_PRIMES[0],
                    "weight_mod_1000000009": weight % MOD_PRIMES[1],
                    "base_witness_match_flag": base_match,
                    "lift_extension_flag": int(sample_count > BASE_HORIZON),
                    "weight": weight,
                }
            )
            fiber_id += 1
        groups[sample_count] = rows
    return groups


def fiber_rows_for_csv(groups: dict[int, list[dict[str, int]]]) -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    for sample_count in sorted(groups):
        for row in groups[sample_count]:
            rows.append({column: row[column] for column in FIBER_COLUMNS})
    return rows


def fiber_moments(rows: list[dict[str, int]], sample_count: int) -> tuple[Fraction, Fraction]:
    total = sum(row["weight"] for row in rows)
    mean = sum(Fraction(row["sum_value"], sample_count) * row["weight"] for row in rows) / total
    variance = (
        sum((Fraction(row["sum_value"], sample_count) - mean) ** 2 * row["weight"] for row in rows)
        / total
    )
    return mean, variance


def transport_edges(
    source: list[dict[str, int]], target: list[dict[str, int]]
) -> tuple[list[tuple[int, int, int]], int, int]:
    source_total = sum(row["weight"] for row in source)
    target_total = sum(row["weight"] for row in target)
    source_index = 0
    target_index = 0
    source_remaining = source[0]["weight"] * target_total
    target_remaining = target[0]["weight"] * source_total
    edges: list[tuple[int, int, int]] = []
    while source_index < len(source) and target_index < len(target):
        mass = min(source_remaining, target_remaining)
        edges.append(
            (
                source[source_index]["sum_value"],
                target[target_index]["sum_value"],
                mass,
            )
        )
        source_remaining -= mass
        target_remaining -= mass
        if source_remaining == 0:
            source_index += 1
            if source_index < len(source):
                source_remaining = source[source_index]["weight"] * target_total
        if target_remaining == 0:
            target_index += 1
            if target_index < len(target):
                target_remaining = target[target_index]["weight"] * source_total
    return edges, source_total, target_total


def build_transport_rows(groups: dict[int, list[dict[str, int]]]) -> dict[str, Any]:
    state_rows: list[dict[str, int]] = []
    level_rows: list[dict[str, int]] = []
    exact_states: list[dict[str, Any]] = []
    previous_variance: Fraction | None = None
    state_id = 0
    for sample_count in range(1, LIFT_HORIZON):
        source = groups[sample_count]
        target = groups[sample_count + 1]
        edges, source_total, target_total = transport_edges(source, target)
        edge_by_source: dict[int, list[tuple[int, int]]] = defaultdict(list)
        for from_sum, to_sum, mass in edges:
            edge_by_source[from_sum].append((to_sum, mass))
        _, source_variance = fiber_moments(source, sample_count)
        _, target_variance = fiber_moments(target, sample_count + 1)
        if previous_variance is None:
            previous_variance = source_variance
        if previous_variance != source_variance:
            raise AssertionError("variance chain mismatch")
        shrink_gap = source_variance - target_variance
        drift_records: list[dict[str, Any]] = []
        for row in source:
            outgoing = edge_by_source[row["sum_value"]]
            actual_mass = sum(mass for _, mass in outgoing)
            expected_mass = row["weight"] * target_total
            if actual_mass != expected_mass:
                raise AssertionError("transport row mass mismatch")
            current_average = Fraction(row["sum_value"], sample_count)
            expected_next = (
                sum(Fraction(to_sum, sample_count + 1) * mass for to_sum, mass in outgoing)
                / actual_mass
            )
            drift = expected_next - current_average
            source_probability = Fraction(row["weight"], source_total)
            drift_sign = sign(drift)
            boundary_defect = int(
                sample_count == 1 and row["sum_value"] == 2 and drift_sign < 0
            )
            state = {
                "state_id": state_id,
                "sample_count": sample_count,
                "sum_value": row["sum_value"],
                "outgoing_edge_count": len(outgoing),
                "current_average_num": current_average.numerator,
                "current_average_den": current_average.denominator,
                "drift_sign": drift_sign,
                "base_level_flag": int(sample_count < BASE_HORIZON),
                "lift_extension_flag": int(sample_count >= BASE_HORIZON),
                "eventual_cone_flag": int(sample_count >= 2 and drift_sign >= 0),
                "boundary_defect_flag": boundary_defect,
            }
            state.update(prefixed_fraction_fields("expected_next_average", expected_next))
            state.update(prefixed_fraction_fields("drift", drift))
            state.update(prefixed_fraction_fields("abs_drift", abs(drift)))
            state.update(prefixed_fraction_fields("source_probability", source_probability))
            state_rows.append(state)
            record = {
                "sample_count": sample_count,
                "sum_value": row["sum_value"],
                "source_probability": source_probability,
                "drift": drift,
                "drift_sign": drift_sign,
            }
            drift_records.append(record)
            exact_states.append(record)
            state_id += 1
        positive = [row for row in drift_records if row["drift"] > 0]
        negative = [row for row in drift_records if row["drift"] < 0]
        zero = [row for row in drift_records if row["drift"] == 0]
        mean_drift = sum(
            row["source_probability"] * row["drift"] for row in drift_records
        )
        level = {
            "sample_count": sample_count,
            "state_count": len(drift_records),
            "drift_positive_count": len(positive),
            "drift_negative_count": len(negative),
            "drift_zero_count": len(zero),
            "rowwise_nonnegative_flag": int(not negative),
            "eventual_cone_flag": int(sample_count >= 2 and not negative),
            "base_level_flag": int(sample_count < BASE_HORIZON),
            "lift_extension_flag": int(sample_count >= BASE_HORIZON),
            "variance_shrink_flag": int(shrink_gap > 0),
        }
        level.update(
            prefixed_fraction_fields(
                "negative_mass",
                sum(row["source_probability"] for row in negative),
            )
        )
        level.update(prefixed_fraction_fields("mean_drift", mean_drift))
        level.update(prefixed_fraction_fields("variance", source_variance))
        level.update(prefixed_fraction_fields("variance_shrink_gap", shrink_gap))
        level.update(
            prefixed_fraction_fields(
                "min_drift", min(row["drift"] for row in drift_records)
            )
        )
        level.update(
            prefixed_fraction_fields(
                "max_drift", max(row["drift"] for row in drift_records)
            )
        )
        level_rows.append(level)
        previous_variance = target_variance
    return {
        "state_rows": state_rows,
        "level_rows": level_rows,
        "exact_states": exact_states,
    }


def build_cone_rows(
    exact_states: list[dict[str, Any]],
    level_rows: list[dict[str, int]],
) -> list[dict[str, int]]:
    specs = [
        (0, 1, BASE_HORIZON - 1, 0),
        (1, 2, BASE_HORIZON - 1, 0),
        (2, BASE_HORIZON, LIFT_HORIZON - 1, 1),
        (3, 2, LIFT_HORIZON - 1, 1),
    ]
    levels_by_sample = {row["sample_count"]: row for row in level_rows}
    cone_rows: list[dict[str, int]] = []
    for cone_id, start, end, extension_flag in specs:
        states = [
            row
            for row in exact_states
            if start <= row["sample_count"] <= end
        ]
        levels = [levels_by_sample[sample_count] for sample_count in range(start, end + 1)]
        positive = [row for row in states if row["drift"] > 0]
        negative = [row for row in states if row["drift"] < 0]
        zero = [row for row in states if row["drift"] == 0]
        cone = {
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
            "lift_extension_flag": extension_flag,
        }
        cone.update(
            prefixed_fraction_fields(
                "negative_mass_total",
                sum(row["source_probability"] for row in negative),
            )
        )
        cone.update(
            prefixed_fraction_fields(
                "mean_drift_total",
                sum(row["source_probability"] * row["drift"] for row in states),
            )
        )
        cone.update(prefixed_fraction_fields("min_drift", min(row["drift"] for row in states)))
        cone.update(prefixed_fraction_fields("max_drift", max(row["drift"] for row in states)))
        cone_rows.append(cone)
    return cone_rows


def build_rows() -> dict[str, Any]:
    loaded = load_inputs()
    component_weights = tuple(
        row["signed_coeff_sum"]
        for row in sorted(loaded["component_rows"], key=lambda row: row["component_id"])
    )
    if component_weights != COMPONENT_WEIGHTS:
        raise AssertionError("component weight mismatch")
    groups = build_fibers(loaded["long_path_rows"], loaded["long_dual_rows"])
    fiber_rows = fiber_rows_for_csv(groups)
    transport = build_transport_rows(groups)
    state_rows = transport["state_rows"]
    level_rows = transport["level_rows"]
    cone_rows = build_cone_rows(transport["exact_states"], level_rows)
    extension_levels = [row for row in level_rows if row["sample_count"] >= BASE_HORIZON]
    extension_states = [row for row in state_rows if row["sample_count"] >= BASE_HORIZON]
    eventual_levels = [row for row in level_rows if row["sample_count"] >= 2]
    obs = {
        "base_horizon": BASE_HORIZON,
        "lift_horizon": LIFT_HORIZON,
        "fiber_row_count": len(fiber_rows),
        "state_row_count": len(state_rows),
        "level_row_count": len(level_rows),
        "cone_row_count": len(cone_rows),
        "base_fiber_match_count": sum(
            int(row["base_witness_match_flag"] == 1) for row in fiber_rows
        ),
        "base_fiber_count": sum(
            int(row["sample_count"] <= BASE_HORIZON) for row in fiber_rows
        ),
        "lift_extension_fiber_count": sum(
            int(row["sample_count"] > BASE_HORIZON) for row in fiber_rows
        ),
        "drift_positive_count": sum(row["drift_positive_count"] for row in level_rows),
        "drift_negative_count": sum(row["drift_negative_count"] for row in level_rows),
        "drift_zero_count": sum(row["drift_zero_count"] for row in level_rows),
        "boundary_negative_count": sum(
            row["drift_negative_count"]
            for row in level_rows
            if row["sample_count"] == 1
        ),
        "extension_level_count": len(extension_levels),
        "extension_state_count": len(extension_states),
        "extension_negative_count": sum(
            int(row["drift_sign"] < 0) for row in extension_states
        ),
        "extension_zero_count": sum(
            int(row["drift_sign"] == 0) for row in extension_states
        ),
        "eventual_level_count": len(eventual_levels),
        "eventual_negative_count": sum(
            row["drift_negative_count"] for row in eventual_levels
        ),
        "eventual_zero_count": sum(row["drift_zero_count"] for row in eventual_levels),
        "variance_shrink_level_count": sum(
            row["variance_shrink_flag"] for row in level_rows
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
        "last_variance_num_mod_1000000007": level_rows[-1][
            "variance_num_mod_1000000007"
        ],
        "last_variance_den_mod_1000000007": level_rows[-1][
            "variance_den_mod_1000000007"
        ],
        "input_long_dual_certified": int(
            loaded["input_reports"]["long_dual"].get("status") == LONG_DUAL_STATUS
        ),
        "input_long_path_certified": int(
            loaded["input_reports"]["long_path"].get("status") == LONG_PATH_STATUS
        ),
        "input_long_prob_certified": int(
            loaded["input_reports"]["long_prob"].get("status") == LONG_PROB_STATUS
        ),
        "input_long_dlim_certified": int(
            loaded["input_reports"]["long_dlim"].get("status") == LONG_DLIM_STATUS
        ),
        "current_measure_match_flag": int(
            sum(int(row["base_witness_match_flag"] == 1) for row in fiber_rows)
            == sum(int(row["sample_count"] <= BASE_HORIZON) for row in fiber_rows)
        ),
        "current_no_second_defect_flag": int(
            sum(int(row["drift_sign"] < 0) for row in extension_states) == 0
        ),
        "current_lift_cone_flag": int(
            len(extension_levels) == LIFT_HORIZON - BASE_HORIZON
            and sum(row["drift_negative_count"] for row in extension_levels) == 0
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
    fiber_hash = hashlib.sha256(
        digest_text(FIBER_COLUMNS, fiber_rows).encode("ascii")
    ).hexdigest()
    state_hash = hashlib.sha256(
        digest_text(STATE_COLUMNS, state_rows).encode("ascii")
    ).hexdigest()
    level_hash = hashlib.sha256(
        digest_text(LEVEL_COLUMNS, level_rows).encode("ascii")
    ).hexdigest()
    cone_hash = hashlib.sha256(
        digest_text(CONE_COLUMNS, cone_rows).encode("ascii")
    ).hexdigest()
    return {
        "input_reports": loaded["input_reports"],
        "fiber_rows": fiber_rows,
        "state_rows": state_rows,
        "level_rows": level_rows,
        "cone_rows": cone_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "fiber_table": table_from_rows(FIBER_COLUMNS, fiber_rows),
        "state_table": table_from_rows(STATE_COLUMNS, state_rows),
        "level_table": table_from_rows(LEVEL_COLUMNS, level_rows),
        "cone_table": table_from_rows(CONE_COLUMNS, cone_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "fiber_hash": fiber_hash,
        "state_hash": state_hash,
        "level_hash": level_hash,
        "cone_hash": cone_hash,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    input_reports = rows["input_reports"]
    checks = {
        "input_certified": (
            obs["input_long_dual_certified"],
            obs["input_long_path_certified"],
            obs["input_long_prob_certified"],
            obs["input_long_dlim_certified"],
        )
        == (1, 1, 1, 1),
        "canonical_lift_exact": (
            obs["base_horizon"],
            obs["lift_horizon"],
            obs["fiber_row_count"],
            obs["base_fiber_match_count"],
            obs["base_fiber_count"],
            obs["lift_extension_fiber_count"],
            rows["fiber_hash"],
        )
        == (16, 128, 16_640, 288, 288, 16_352, FIBER_TEXT_HASH),
        "transport_lift_exact": (
            obs["state_row_count"],
            obs["level_row_count"],
            obs["drift_positive_count"],
            obs["drift_negative_count"],
            obs["drift_zero_count"],
            obs["boundary_negative_count"],
            obs["max_outgoing_edge_count"],
            obs["state_abs_drift_num_mod_sum_1000000007"],
            rows["state_hash"],
        )
        == (
            16_383,
            127,
            16_256,
            1,
            126,
            1,
            3,
            811_687_137,
            STATE_TEXT_HASH,
        ),
        "lift_cone_exact": (
            obs["cone_row_count"],
            obs["extension_level_count"],
            obs["extension_state_count"],
            obs["extension_negative_count"],
            obs["extension_zero_count"],
            obs["eventual_level_count"],
            obs["eventual_negative_count"],
            obs["eventual_zero_count"],
            obs["variance_shrink_level_count"],
            obs["level_mean_drift_num_mod_sum_1000000007"],
            rows["level_hash"],
            rows["cone_hash"],
        )
        == (
            4,
            112,
            16_128,
            0,
            112,
            126,
            0,
            126,
            127,
            757_022_242,
            LEVEL_TEXT_HASH,
            CONE_TEXT_HASH,
        ),
        "current_representation_exact": (
            obs["current_measure_match_flag"],
            obs["current_no_second_defect_flag"],
            obs["current_lift_cone_flag"],
        )
        == (1, 1, 1),
        "table_shapes_match": (
            tuple(rows["fiber_table"].shape),
            tuple(rows["state_table"].shape),
            tuple(rows["level_table"].shape),
            tuple(rows["cone_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (16_640, len(FIBER_COLUMNS)),
            (16_383, len(STATE_COLUMNS)),
            (127, len(LEVEL_COLUMNS)),
            (4, len(CONE_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "canonical_witness_lift_eventual_cone",
        "lift": {
            "base_horizon": BASE_HORIZON,
            "lift_horizon": LIFT_HORIZON,
            "component_weights": list(COMPONENT_WEIGHTS),
            "fiber_row_count": obs["fiber_row_count"],
            "base_fiber_match_count": obs["base_fiber_match_count"],
            "lift_extension_fiber_count": obs["lift_extension_fiber_count"],
            "fiber_text_sha256": rows["fiber_hash"],
            "fiber_table_sha256": sha_array(rows["fiber_table"]),
        },
        "transport": {
            "level_count": obs["level_row_count"],
            "state_count": obs["state_row_count"],
            "positive_count": obs["drift_positive_count"],
            "negative_count": obs["drift_negative_count"],
            "zero_count": obs["drift_zero_count"],
            "state_text_sha256": rows["state_hash"],
            "state_table_sha256": sha_array(rows["state_table"]),
        },
        "extension_cone": {
            "start_sample_count": BASE_HORIZON,
            "end_sample_count": LIFT_HORIZON - 1,
            "level_count": obs["extension_level_count"],
            "state_count": obs["extension_state_count"],
            "negative_count": obs["extension_negative_count"],
            "zero_count": obs["extension_zero_count"],
            "variance_shrink_level_count": obs["variance_shrink_level_count"],
            "level_text_sha256": rows["level_hash"],
            "level_table_sha256": sha_array(rows["level_table"]),
            "cone_text_sha256": rows["cone_hash"],
            "cone_table_sha256": sha_array(rows["cone_table"]),
        },
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    linf_payload = {
        "schema": "long.linf@1",
        "object": "canonical_witness_lift_eventual_cone",
        "status": STATUS if all(checks.values()) else "LONG_LINF_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.linf.report@1",
        "status": linf_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_linf extends the certified canonical one-witness-per-sum "
            "dual measure from horizon 16 to horizon 128. The extension agrees "
            "with all 288 existing long_path/long_dual base fibers through "
            "horizon 16. Across 127 transport levels and 16,383 states, the "
            "only negative drift remains the long_dlim boundary defect at "
            "level 1; the lifted extension levels 16..127 have no negative "
            "statewise drift and one zero top state per level."
        ),
        "stage_protocol": {
            "draft": "read long_dual component weights, long_path witnesses, long_prob measure, and long_dlim defect",
            "witness": "extend the canonical sum-fiber witness rule to horizon 128 and recompute exact monotone transports",
            "coherence": "check base-fiber agreement, drift partition, lift cone, variance shrinkage, statuses, hashes, and shapes",
            "closure": "emit finite lifted eventual-cone certificate while recording the measure choice",
            "emit": "write long_linf artifacts and verifier hook",
        },
        "inputs": {
            "long_dual_report": input_entry(
                LONG_DUAL_REPORT,
                {"status": input_reports["long_dual"].get("status")},
            ),
            "long_dual_component": input_entry(LONG_DUAL_COMPONENT),
            "long_dual_path": input_entry(LONG_DUAL_PATH),
            "long_dual_tables": input_entry(LONG_DUAL_TABLES),
            "long_path_report": input_entry(
                LONG_PATH_REPORT,
                {"status": input_reports["long_path"].get("status")},
            ),
            "long_path_path": input_entry(LONG_PATH_PATH),
            "long_path_tables": input_entry(LONG_PATH_TABLES),
            "long_prob_report": input_entry(
                LONG_PROB_REPORT,
                {"status": input_reports["long_prob"].get("status")},
            ),
            "long_prob_tables": input_entry(LONG_PROB_TABLES),
            "long_dlim_report": input_entry(
                LONG_DLIM_REPORT,
                {"status": input_reports["long_dlim"].get("status")},
            ),
            "long_dlim_defect": input_entry(LONG_DLIM_DEFECT),
            "long_dlim_tables": input_entry(LONG_DLIM_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "linf": relpath(OUT_DIR / "linf.json"),
            "fiber_csv": relpath(OUT_DIR / "fiber.csv"),
            "state_csv": relpath(OUT_DIR / "state.csv"),
            "level_csv": relpath(OUT_DIR / "level.csv"),
            "cone_csv": relpath(OUT_DIR / "cone.csv"),
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
                "canonical witness-measure extension from horizon 16 to 128",
                "agreement with all existing base long_path/long_dual fibers",
                "absence of any second negative drift defect through lifted levels 16..127",
                "strict variance shrinkage across all lifted transport levels",
            ],
            "does_not_certify_because_out_of_scope": [
                "the full trinomial component-word measure",
                "semantic C985 associator composition beyond selected witnesses",
                "a raw tensor table materialized beyond horizon 16",
                "an infinite-horizon induction theorem",
            ],
        },
        "next_highest_yield_item": (
            "Build long_ind: turn the horizon-128 lifted pattern into a finite "
            "symbolic induction certificate for the canonical witness measure."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.linf.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.linf.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "linf": linf_payload,
        "fiber_csv": csv_text(FIBER_COLUMNS, rows["fiber_rows"]),
        "state_csv": csv_text(STATE_COLUMNS, rows["state_rows"]),
        "level_csv": csv_text(LEVEL_COLUMNS, rows["level_rows"]),
        "cone_csv": csv_text(CONE_COLUMNS, rows["cone_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "fiber_table": rows["fiber_table"],
        "state_table": rows["state_table"],
        "level_table": rows["level_table"],
        "cone_table": rows["cone_table"],
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
    write_json(OUT_DIR / "linf.json", payloads["linf"])
    (OUT_DIR / "fiber.csv").write_text(payloads["fiber_csv"], encoding="utf-8")
    (OUT_DIR / "state.csv").write_text(payloads["state_csv"], encoding="utf-8")
    (OUT_DIR / "level.csv").write_text(payloads["level_csv"], encoding="utf-8")
    (OUT_DIR / "cone.csv").write_text(payloads["cone_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        fiber_table=payloads["fiber_table"],
        state_table=payloads["state_table"],
        level_table=payloads["level_table"],
        cone_table=payloads["cone_table"],
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
