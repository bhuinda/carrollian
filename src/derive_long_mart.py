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
    from .derive_long_prob import (
        COMPONENT_WEIGHTS,
        LONG_DUAL_PATH,
        LONG_DUAL_REPORT,
        LONG_DUAL_TABLES,
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_TABLES,
        OUT_DIR as LONG_PROB_DIR,
        STATUS as LONG_PROB_STATUS,
        prefixed_fraction_columns,
        prefixed_fraction_fields,
    )
    from .derive_long_dual import STATUS as LONG_DUAL_STATUS
    from .derive_long_path import STATUS as LONG_PATH_STATUS
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
    from derive_long_prob import (
        COMPONENT_WEIGHTS,
        LONG_DUAL_PATH,
        LONG_DUAL_REPORT,
        LONG_DUAL_TABLES,
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_TABLES,
        OUT_DIR as LONG_PROB_DIR,
        STATUS as LONG_PROB_STATUS,
        prefixed_fraction_columns,
        prefixed_fraction_fields,
    )
    from derive_long_dual import STATUS as LONG_DUAL_STATUS
    from derive_long_path import STATUS as LONG_PATH_STATUS
    from derive_long_raw import (
        csv_text,
        digest_text,
        int_rows,
        read_csv_rows,
        rows_from_table,
        table_from_rows,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_mart"
STATUS = "LONG_MART_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
LONG_PROB_REPORT = LONG_PROB_DIR / "report.json"
LONG_PROB_DIST = LONG_PROB_DIR / "dist.csv"
LONG_PROB_MOMENT = LONG_PROB_DIR / "moment.csv"
LONG_PROB_TABLES = LONG_PROB_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_mart.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_mart.py"

EDGE_TEXT_HASH = "3de7fbbacc5185fc75790934273604d2c33d0ac7662f8678dfd8fb2fe6501157"
STATE_TEXT_HASH = "a1ffd52e24fa06a6695cd1acbb9150dcf34a503305a5ad454bc124fd8a052cb1"
LEVEL_TEXT_HASH = "c9e787f0503359662ddbc15260876d68f3f10e5236c205abb9038cecec5820d7"

MOD_PRIMES = (1_000_000_007, 1_000_000_009)

EDGE_COLUMNS = [
    "edge_id",
    "from_sample_count",
    "from_sum_value",
    "to_sample_count",
    "to_sum_value",
    "transport_mass_digits",
    "transport_mass_mod_1000000007",
    "transport_mass_mod_1000000009",
    *prefixed_fraction_columns("row_prob"),
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
    "drift_sign",
    *prefixed_fraction_columns("conditional_variance"),
]
LEVEL_COLUMNS = [
    "sample_count",
    "source_row_count",
    "target_row_count",
    "edge_count",
    "transport_mass_digits",
    "transport_mass_mod_1000000007",
    "transport_mass_mod_1000000009",
    "row_marginal_flag_count",
    "col_marginal_flag_count",
    "drift_positive_count",
    "drift_negative_count",
    "drift_zero_count",
    "max_outgoing_edge_count",
    *prefixed_fraction_columns("source_variance"),
    *prefixed_fraction_columns("target_variance"),
    *prefixed_fraction_columns("variance_shrink_gap"),
    *prefixed_fraction_columns("conditional_noise"),
    *prefixed_fraction_columns("predicted_variance"),
    *prefixed_fraction_columns("variance_decomp_gap"),
    "variance_shrink_flag",
    "variance_decomp_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "level_row_count",
    "edge_row_count",
    "state_row_count",
    "source_row_count_sum",
    "target_row_count_sum",
    "row_marginal_flag_count",
    "col_marginal_flag_count",
    "drift_positive_count",
    "drift_negative_count",
    "drift_zero_count",
    "eventual_submartingale_level_count",
    "global_martingale_row_count",
    "variance_shrink_level_count",
    "variance_decomp_level_count",
    "max_outgoing_edge_count",
    "transport_mass_mod_sum_1000000007",
    "conditional_noise_num_mod_sum_1000000007",
    "predicted_variance_num_mod_sum_1000000007",
    "drift_abs_num_mod_sum_1000000007",
    "first_level_negative_drift_count",
    "last_level_positive_drift_count",
    "current_transport_operator_flag",
    "current_global_martingale_flag",
    "current_eventual_submartingale_flag",
    "current_variance_supermartingale_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def path_weight(row: dict[str, int]) -> int:
    return (
        COMPONENT_WEIGHTS[0] ** row["count_component0"]
        * COMPONENT_WEIGHTS[1] ** row["count_component1"]
        * COMPONENT_WEIGHTS[2] ** row["count_component2"]
    )


def load_inputs() -> dict[str, Any]:
    path_rows = int_rows(read_csv_rows(LONG_PATH_PATH))
    input_reports = {
        "long_prob": load_json(LONG_PROB_REPORT),
        "long_dual": load_json(LONG_DUAL_REPORT),
        "long_path": load_json(LONG_PATH_REPORT),
    }
    return {
        "path_rows": path_rows,
        "input_reports": input_reports,
    }


def grouped_weights(path_rows: list[dict[str, int]]) -> dict[int, list[dict[str, int]]]:
    groups: dict[int, list[dict[str, int]]] = defaultdict(list)
    for row in path_rows:
        groups[row["sample_count"]].append(
            {"sum_value": row["sum_value"], "weight": path_weight(row)}
        )
    for sample_count in groups:
        groups[sample_count].sort(key=lambda row: row["sum_value"])
    return groups


def fiber_moments(rows: list[dict[str, int]], sample_count: int) -> tuple[int, Fraction, Fraction]:
    total_weight = sum(row["weight"] for row in rows)
    weighted_mean = sum(row["sum_value"] * row["weight"] for row in rows)
    mean = Fraction(weighted_mean, total_weight * sample_count)
    variance = (
        sum((Fraction(row["sum_value"], sample_count) - mean) ** 2 * row["weight"] for row in rows)
        / total_weight
    )
    return total_weight, mean, variance


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


def build_rows() -> dict[str, Any]:
    loaded = load_inputs()
    groups = grouped_weights(loaded["path_rows"])
    edge_rows: list[dict[str, int]] = []
    state_rows: list[dict[str, int]] = []
    level_rows: list[dict[str, int]] = []
    edge_id = 0
    state_id = 0
    obs_accum = {
        "row_marginal_flag_count": 0,
        "col_marginal_flag_count": 0,
        "drift_positive_count": 0,
        "drift_negative_count": 0,
        "drift_zero_count": 0,
        "eventual_submartingale_level_count": 0,
        "global_martingale_row_count": 0,
        "variance_shrink_level_count": 0,
        "variance_decomp_level_count": 0,
        "max_outgoing_edge_count": 0,
        "transport_mass_mod_sum_1000000007": 0,
        "conditional_noise_num_mod_sum_1000000007": 0,
        "predicted_variance_num_mod_sum_1000000007": 0,
        "drift_abs_num_mod_sum_1000000007": 0,
        "first_level_negative_drift_count": 0,
        "last_level_positive_drift_count": 0,
    }
    for sample_count in range(1, max(groups)):
        source = groups[sample_count]
        target = groups[sample_count + 1]
        edges, source_total, target_total = transport_edges(source, target)
        common_denominator = source_total * target_total
        source_by_sum = {row["sum_value"]: row["weight"] for row in source}
        target_by_sum = {row["sum_value"]: row["weight"] for row in target}
        edge_by_source: dict[int, list[tuple[int, int]]] = defaultdict(list)
        edge_by_target: dict[int, list[tuple[int, int]]] = defaultdict(list)
        level_transport_mass = 0
        for from_sum, to_sum, mass in edges:
            edge_by_source[from_sum].append((to_sum, mass))
            edge_by_target[to_sum].append((from_sum, mass))
            level_transport_mass += mass
            row_probability = Fraction(mass, source_by_sum[from_sum] * target_total)
            row = {
                "edge_id": edge_id,
                "from_sample_count": sample_count,
                "from_sum_value": from_sum,
                "to_sample_count": sample_count + 1,
                "to_sum_value": to_sum,
                "transport_mass_digits": len(str(mass)),
                "transport_mass_mod_1000000007": mass % MOD_PRIMES[0],
                "transport_mass_mod_1000000009": mass % MOD_PRIMES[1],
            }
            row.update(prefixed_fraction_fields("row_prob", row_probability))
            edge_rows.append(row)
            edge_id += 1
        source_weight, source_mean, source_variance = fiber_moments(source, sample_count)
        target_weight, target_mean, target_variance = fiber_moments(
            target, sample_count + 1
        )
        if source_weight != source_total or target_weight != target_total:
            raise AssertionError("transport total mismatch")
        row_marginal_flags = 0
        col_marginal_flags = 0
        conditional_noise = Fraction(0)
        predicted_variance = Fraction(0)
        drift_positive = 0
        drift_negative = 0
        drift_zero = 0
        for row in source:
            source_sum = row["sum_value"]
            outgoing = edge_by_source[source_sum]
            expected_row_mass = row["weight"] * target_total
            actual_row_mass = sum(mass for _, mass in outgoing)
            row_marginal_flags += int(actual_row_mass == expected_row_mass)
            current_average = Fraction(source_sum, sample_count)
            expected_next = (
                sum(Fraction(to_sum, sample_count + 1) * mass for to_sum, mass in outgoing)
                / actual_row_mass
            )
            drift = expected_next - current_average
            conditional_variance = (
                sum(
                    (Fraction(to_sum, sample_count + 1) - expected_next) ** 2 * mass
                    for to_sum, mass in outgoing
                )
                / actual_row_mass
            )
            source_probability = Fraction(row["weight"], source_total)
            conditional_noise += source_probability * conditional_variance
            predicted_variance += source_probability * (expected_next - target_mean) ** 2
            if drift > 0:
                drift_sign = 1
                drift_positive += 1
            elif drift < 0:
                drift_sign = -1
                drift_negative += 1
            else:
                drift_sign = 0
                drift_zero += 1
            obs_accum["drift_abs_num_mod_sum_1000000007"] = (
                obs_accum["drift_abs_num_mod_sum_1000000007"]
                + abs(drift).numerator
            ) % MOD_PRIMES[0]
            state = {
                "state_id": state_id,
                "sample_count": sample_count,
                "sum_value": source_sum,
                "outgoing_edge_count": len(outgoing),
                "current_average_num": current_average.numerator,
                "current_average_den": current_average.denominator,
                "drift_sign": drift_sign,
            }
            state.update(prefixed_fraction_fields("expected_next_average", expected_next))
            state.update(prefixed_fraction_fields("drift", drift))
            state.update(prefixed_fraction_fields("conditional_variance", conditional_variance))
            state_rows.append(state)
            state_id += 1
        for row in target:
            target_sum = row["sum_value"]
            actual_col_mass = sum(mass for _, mass in edge_by_target[target_sum])
            col_marginal_flags += int(actual_col_mass == row["weight"] * source_total)
        decomp_gap = target_variance - conditional_noise - predicted_variance
        shrink_gap = source_variance - target_variance
        max_outgoing = max(len(values) for values in edge_by_source.values())
        level = {
            "sample_count": sample_count,
            "source_row_count": len(source),
            "target_row_count": len(target),
            "edge_count": len(edges),
            "transport_mass_digits": len(str(level_transport_mass)),
            "transport_mass_mod_1000000007": level_transport_mass % MOD_PRIMES[0],
            "transport_mass_mod_1000000009": level_transport_mass % MOD_PRIMES[1],
            "row_marginal_flag_count": row_marginal_flags,
            "col_marginal_flag_count": col_marginal_flags,
            "drift_positive_count": drift_positive,
            "drift_negative_count": drift_negative,
            "drift_zero_count": drift_zero,
            "max_outgoing_edge_count": max_outgoing,
            "variance_shrink_flag": int(shrink_gap > 0),
            "variance_decomp_flag": int(decomp_gap == 0),
        }
        level.update(prefixed_fraction_fields("source_variance", source_variance))
        level.update(prefixed_fraction_fields("target_variance", target_variance))
        level.update(prefixed_fraction_fields("variance_shrink_gap", shrink_gap))
        level.update(prefixed_fraction_fields("conditional_noise", conditional_noise))
        level.update(prefixed_fraction_fields("predicted_variance", predicted_variance))
        level.update(prefixed_fraction_fields("variance_decomp_gap", decomp_gap))
        level_rows.append(level)
        obs_accum["row_marginal_flag_count"] += row_marginal_flags
        obs_accum["col_marginal_flag_count"] += col_marginal_flags
        obs_accum["drift_positive_count"] += drift_positive
        obs_accum["drift_negative_count"] += drift_negative
        obs_accum["drift_zero_count"] += drift_zero
        obs_accum["global_martingale_row_count"] += drift_zero
        obs_accum["variance_shrink_level_count"] += int(shrink_gap > 0)
        obs_accum["variance_decomp_level_count"] += int(decomp_gap == 0)
        obs_accum["eventual_submartingale_level_count"] += int(
            sample_count >= 2 and drift_negative == 0
        )
        obs_accum["max_outgoing_edge_count"] = max(
            obs_accum["max_outgoing_edge_count"], max_outgoing
        )
        obs_accum["transport_mass_mod_sum_1000000007"] = (
            obs_accum["transport_mass_mod_sum_1000000007"]
            + level_transport_mass
        ) % MOD_PRIMES[0]
        obs_accum["conditional_noise_num_mod_sum_1000000007"] = (
            obs_accum["conditional_noise_num_mod_sum_1000000007"]
            + conditional_noise.numerator
        ) % MOD_PRIMES[0]
        obs_accum["predicted_variance_num_mod_sum_1000000007"] = (
            obs_accum["predicted_variance_num_mod_sum_1000000007"]
            + predicted_variance.numerator
        ) % MOD_PRIMES[0]
        if sample_count == 1:
            obs_accum["first_level_negative_drift_count"] = drift_negative
        if sample_count == max(groups) - 1:
            obs_accum["last_level_positive_drift_count"] = drift_positive
    obs = {
        "level_row_count": len(level_rows),
        "edge_row_count": len(edge_rows),
        "state_row_count": len(state_rows),
        "source_row_count_sum": sum(row["source_row_count"] for row in level_rows),
        "target_row_count_sum": sum(row["target_row_count"] for row in level_rows),
        **obs_accum,
        "current_transport_operator_flag": 1,
        "current_global_martingale_flag": 0,
        "current_eventual_submartingale_flag": int(
            obs_accum["eventual_submartingale_level_count"] == len(level_rows) - 1
        ),
        "current_variance_supermartingale_flag": int(
            obs_accum["variance_shrink_level_count"] == len(level_rows)
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
    edge_hash = hashlib.sha256(
        digest_text(EDGE_COLUMNS, edge_rows).encode("ascii")
    ).hexdigest()
    state_hash = hashlib.sha256(
        digest_text(STATE_COLUMNS, state_rows).encode("ascii")
    ).hexdigest()
    level_hash = hashlib.sha256(
        digest_text(LEVEL_COLUMNS, level_rows).encode("ascii")
    ).hexdigest()
    return {
        "input_reports": loaded["input_reports"],
        "edge_rows": edge_rows,
        "state_rows": state_rows,
        "level_rows": level_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "edge_table": table_from_rows(EDGE_COLUMNS, edge_rows),
        "state_table": table_from_rows(STATE_COLUMNS, state_rows),
        "level_table": table_from_rows(LEVEL_COLUMNS, level_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "edge_hash": edge_hash,
        "state_hash": state_hash,
        "level_hash": level_hash,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    input_reports = rows["input_reports"]
    checks = {
        "input_certified": (
            input_reports["long_prob"].get("status"),
            input_reports["long_dual"].get("status"),
            input_reports["long_path"].get("status"),
        )
        == (LONG_PROB_STATUS, LONG_DUAL_STATUS, LONG_PATH_STATUS),
        "transport_exact": (
            obs["level_row_count"],
            obs["edge_row_count"],
            obs["state_row_count"],
            obs["source_row_count_sum"],
            obs["target_row_count_sum"],
            obs["row_marginal_flag_count"],
            obs["col_marginal_flag_count"],
            obs["max_outgoing_edge_count"],
            obs["transport_mass_mod_sum_1000000007"],
            rows["edge_hash"],
        )
        == (
            15,
            525,
            255,
            255,
            285,
            255,
            285,
            3,
            290_450_850,
            EDGE_TEXT_HASH,
        ),
        "drift_profile_exact": (
            obs["drift_positive_count"],
            obs["drift_negative_count"],
            obs["drift_zero_count"],
            obs["eventual_submartingale_level_count"],
            obs["global_martingale_row_count"],
            obs["first_level_negative_drift_count"],
            obs["last_level_positive_drift_count"],
            obs["drift_abs_num_mod_sum_1000000007"],
            rows["state_hash"],
        )
        == (
            240,
            1,
            14,
            14,
            14,
            1,
            30,
            236_694_364,
            STATE_TEXT_HASH,
        ),
        "variance_operator_exact": (
            obs["variance_shrink_level_count"],
            obs["variance_decomp_level_count"],
            obs["conditional_noise_num_mod_sum_1000000007"],
            obs["predicted_variance_num_mod_sum_1000000007"],
            obs["current_variance_supermartingale_flag"],
            rows["level_hash"],
        )
        == (
            15,
            15,
            139_149_809,
            847_852_262,
            1,
            LEVEL_TEXT_HASH,
        ),
        "current_representation_exact": (
            obs["current_transport_operator_flag"],
            obs["current_global_martingale_flag"],
            obs["current_eventual_submartingale_flag"],
            obs["current_variance_supermartingale_flag"],
        )
        == (1, 0, 1, 1),
        "table_shapes_match": (
            tuple(rows["edge_table"].shape),
            tuple(rows["state_table"].shape),
            tuple(rows["level_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (525, len(EDGE_COLUMNS)),
            (255, len(STATE_COLUMNS)),
            (15, len(LEVEL_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "finite_transport_conditional_expectation_operator",
        "transport": {
            "method": "monotone integer quantile transport between consecutive dual probability fibers",
            "level_count": obs["level_row_count"],
            "edge_count": obs["edge_row_count"],
            "state_count": obs["state_row_count"],
            "row_marginal_flag_count": obs["row_marginal_flag_count"],
            "col_marginal_flag_count": obs["col_marginal_flag_count"],
            "max_outgoing_edge_count": obs["max_outgoing_edge_count"],
            "edge_table_sha256": sha_array(rows["edge_table"]),
            "edge_text_sha256": rows["edge_hash"],
        },
        "drift": {
            "positive_count": obs["drift_positive_count"],
            "negative_count": obs["drift_negative_count"],
            "zero_count": obs["drift_zero_count"],
            "global_martingale_row_count": obs["global_martingale_row_count"],
            "eventual_submartingale_level_count": obs[
                "eventual_submartingale_level_count"
            ],
            "first_level_negative_drift_count": obs[
                "first_level_negative_drift_count"
            ],
            "state_table_sha256": sha_array(rows["state_table"]),
            "state_text_sha256": rows["state_hash"],
        },
        "variance": {
            "variance_shrink_level_count": obs["variance_shrink_level_count"],
            "variance_decomp_level_count": obs["variance_decomp_level_count"],
            "conditional_noise_num_mod_sum_1000000007": obs[
                "conditional_noise_num_mod_sum_1000000007"
            ],
            "predicted_variance_num_mod_sum_1000000007": obs[
                "predicted_variance_num_mod_sum_1000000007"
            ],
            "level_table_sha256": sha_array(rows["level_table"]),
            "level_text_sha256": rows["level_hash"],
        },
        "current_representation": {
            "transport_operator": bool(obs["current_transport_operator_flag"]),
            "global_martingale": bool(obs["current_global_martingale_flag"]),
            "eventual_submartingale": bool(
                obs["current_eventual_submartingale_flag"]
            ),
            "variance_supermartingale": bool(
                obs["current_variance_supermartingale_flag"]
            ),
        },
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    mart_payload = {
        "schema": "long.mart@1",
        "object": "finite_transport_conditional_expectation_operator",
        "status": STATUS if all(checks.values()) else "LONG_MART_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.mart.report@1",
        "status": mart_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_mart derives the finite conditional expectation operator "
            "behind long_prob by monotone integer transport between consecutive "
            "sample-count fibers. The sample-average process is not a global "
            "martingale because of a single first-level negative drift row, but "
            "it is rowwise submartingale from level 2 onward; the variance "
            "process strictly decreases at every level and each target variance "
            "decomposes exactly into conditional-noise plus predicted-variance "
            "terms."
        ),
        "stage_protocol": {
            "draft": "read long_prob probabilities and long_path finite path coordinates",
            "witness": "construct exact monotone transport between consecutive sample-count fibers",
            "coherence": "check row/column marginals, drift profile, variance decomposition, statuses, hashes, and shapes",
            "closure": "emit conditional expectation operator with martingale boundary defect recorded",
            "emit": "write long_mart artifacts and verifier hook",
        },
        "inputs": {
            "long_prob_report": input_entry(
                LONG_PROB_REPORT,
                {"status": rows["input_reports"]["long_prob"].get("status")},
            ),
            "long_prob_dist": input_entry(LONG_PROB_DIST),
            "long_prob_moment": input_entry(LONG_PROB_MOMENT),
            "long_prob_tables": input_entry(LONG_PROB_TABLES),
            "long_dual_report": input_entry(
                LONG_DUAL_REPORT,
                {"status": rows["input_reports"]["long_dual"].get("status")},
            ),
            "long_dual_path": input_entry(LONG_DUAL_PATH),
            "long_dual_tables": input_entry(LONG_DUAL_TABLES),
            "long_path_report": input_entry(
                LONG_PATH_REPORT,
                {"status": rows["input_reports"]["long_path"].get("status")},
            ),
            "long_path_path": input_entry(LONG_PATH_PATH),
            "long_path_tables": input_entry(LONG_PATH_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "mart": relpath(OUT_DIR / "mart.json"),
            "edge_csv": relpath(OUT_DIR / "edge.csv"),
            "state_csv": relpath(OUT_DIR / "state.csv"),
            "level_csv": relpath(OUT_DIR / "level.csv"),
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
                "an exact finite conditional transport operator between consecutive dual probability fibers",
                "exact row and column marginal preservation for all 15 transitions",
                "the sample average is not globally martingale and is rowwise submartingale from level 2 onward",
                "strict variance shrinkage and exact conditional variance decomposition at every level",
            ],
            "does_not_certify_because_out_of_scope": [
                "uniqueness of the transport operator",
                "a transition operator on the full raw tensor support",
                "semantic C985 associator composition",
                "an infinite-horizon martingale theorem",
            ],
        },
        "next_highest_yield_item": (
            "Build long_stop: turn the finite transport operator into stopping/"
            "tail certificates and compare optional-stopping bounds against the "
            "existing finite concentration certificates."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.mart.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.mart.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "mart": mart_payload,
        "edge_csv": csv_text(EDGE_COLUMNS, rows["edge_rows"]),
        "state_csv": csv_text(STATE_COLUMNS, rows["state_rows"]),
        "level_csv": csv_text(LEVEL_COLUMNS, rows["level_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "edge_table": rows["edge_table"],
        "state_table": rows["state_table"],
        "level_table": rows["level_table"],
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
    write_json(OUT_DIR / "mart.json", payloads["mart"])
    (OUT_DIR / "edge.csv").write_text(payloads["edge_csv"], encoding="utf-8")
    (OUT_DIR / "state.csv").write_text(payloads["state_csv"], encoding="utf-8")
    (OUT_DIR / "level.csv").write_text(payloads["level_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        edge_table=payloads["edge_table"],
        state_table=payloads["state_table"],
        level_table=payloads["level_table"],
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
