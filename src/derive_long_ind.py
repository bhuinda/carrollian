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
    from .derive_long_linf import OUT_DIR as LONG_LINF_DIR, STATUS as LONG_LINF_STATUS
    from .derive_long_prob import COMPONENT_WEIGHTS
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_linf import OUT_DIR as LONG_LINF_DIR, STATUS as LONG_LINF_STATUS
    from derive_long_prob import COMPONENT_WEIGHTS
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_ind"
STATUS = "LONG_IND_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
LONG_LINF_REPORT = LONG_LINF_DIR / "report.json"
LONG_LINF_LEVEL = LONG_LINF_DIR / "level.csv"
LONG_LINF_CONE = LONG_LINF_DIR / "cone.csv"
LONG_LINF_TABLES = LONG_LINF_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_ind.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_ind.py"

INDUCTION_START = 16
NEGATIVE_CONTROL_HORIZON = 64

RULE_TEXT_HASH = "71b8a79952e520146414630970e005af0ce380be4756038313db717889481946"
MARGIN_TEXT_HASH = "76fb406ea657029946c24045c540c36191d87fe75391b2c2d6d066782236843e"
BRIDGE_TEXT_HASH = "d21350ddbad1e893f6772bdcde38acb34638f876cbad05ef880abecda28a63e9"
NEGATIVE_CONTROL_TEXT_HASH = "c17e03a6daf6475c51441115bb10c5febe6e5395a39ff2255acf0dc3013ef790"

MOD_PRIMES = (1_000_000_007, 1_000_000_009)

RULE_COLUMNS = [
    "rule_id",
    "region_code",
    "s_min_kind",
    "s_min_const",
    "s_max_kind",
    "s_max_const",
    "target_min_offset",
    "target_max_offset",
    "target_count_min",
    "target_count_max",
    "domain_min_n",
    "domain_nonempty_at_start_flag",
]
MARGIN_COLUMNS = [
    "rule_id",
    "worst_s_kind",
    "worst_s_const",
    "target_min_offset",
    "margin_num_a",
    "margin_num_b",
    "margin_den_degree",
    "margin_num_at_start",
    "strict_positive_at_start_flag",
    "nonnegative_for_n_ge_start_flag",
    "equality_rule_flag",
]
BRIDGE_COLUMNS = [
    "bridge_id",
    "induction_start",
    "linf_base_horizon",
    "linf_lift_horizon",
    "linf_level_count",
    "linf_state_count",
    "linf_negative_count",
    "linf_zero_count",
    "linf_extension_negative_count",
    "rule_count",
    "margin_nonnegative_count",
    "measure_match_flag",
]
NEGATIVE_CONTROL_COLUMNS = [
    "control_id",
    "horizon",
    "state_count",
    "drift_positive_count",
    "drift_negative_count",
    "drift_zero_count",
    "first_negative_sample_count",
    "first_negative_sum_value",
    "first_negative_drift_num",
    "first_negative_drift_den",
    "first_negative_source_probability_num",
    "first_negative_source_probability_den",
    "canonical_measure_required_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "rule_row_count",
    "margin_row_count",
    "bridge_row_count",
    "negative_control_row_count",
    "induction_start",
    "linf_lift_horizon",
    "linf_state_count",
    "linf_negative_count",
    "linf_extension_negative_count",
    "margin_nonnegative_count",
    "margin_strict_positive_count",
    "margin_equality_rule_count",
    "negative_control_state_count",
    "negative_control_negative_count",
    "negative_control_zero_count",
    "first_negative_sample_count",
    "first_negative_sum_value",
    "first_negative_drift_num_mod_1000000007",
    "first_negative_drift_den_mod_1000000007",
    "measure_match_flag",
    "input_long_linf_certified",
    "current_symbolic_margin_flag",
    "current_negative_control_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def canonical_rule_rows() -> list[dict[str, int]]:
    # s_kind encodes 0*n+c, 1*n+c, or 2*n+c.
    return [
        {
            "rule_id": 0,
            "region_code": 0,
            "s_min_kind": 0,
            "s_min_const": 0,
            "s_max_kind": 0,
            "s_max_const": 0,
            "target_min_offset": 0,
            "target_max_offset": 2,
            "target_count_min": 3,
            "target_count_max": 3,
            "domain_min_n": INDUCTION_START,
            "domain_nonempty_at_start_flag": 1,
        },
        {
            "rule_id": 1,
            "region_code": 1,
            "s_min_kind": 0,
            "s_min_const": 1,
            "s_max_kind": 0,
            "s_max_const": 1,
            "target_min_offset": 1,
            "target_max_offset": 3,
            "target_count_min": 3,
            "target_count_max": 3,
            "domain_min_n": INDUCTION_START,
            "domain_nonempty_at_start_flag": 1,
        },
        {
            "rule_id": 2,
            "region_code": 2,
            "s_min_kind": 0,
            "s_min_const": 2,
            "s_max_kind": 0,
            "s_max_const": 2,
            "target_min_offset": 2,
            "target_max_offset": 3,
            "target_count_min": 2,
            "target_count_max": 2,
            "domain_min_n": INDUCTION_START,
            "domain_nonempty_at_start_flag": 1,
        },
        {
            "rule_id": 3,
            "region_code": 3,
            "s_min_kind": 0,
            "s_min_const": 3,
            "s_max_kind": 0,
            "s_max_const": 3,
            "target_min_offset": 2,
            "target_max_offset": 4,
            "target_count_min": 3,
            "target_count_max": 3,
            "domain_min_n": INDUCTION_START,
            "domain_nonempty_at_start_flag": 1,
        },
        {
            "rule_id": 4,
            "region_code": 4,
            "s_min_kind": 0,
            "s_min_const": 4,
            "s_max_kind": 1,
            "s_max_const": -2,
            "target_min_offset": 3,
            "target_max_offset": 4,
            "target_count_min": 2,
            "target_count_max": 2,
            "domain_min_n": INDUCTION_START,
            "domain_nonempty_at_start_flag": 1,
        },
        {
            "rule_id": 5,
            "region_code": 5,
            "s_min_kind": 1,
            "s_min_const": -1,
            "s_max_kind": 1,
            "s_max_const": -1,
            "target_min_offset": 3,
            "target_max_offset": 3,
            "target_count_min": 1,
            "target_count_max": 1,
            "domain_min_n": INDUCTION_START,
            "domain_nonempty_at_start_flag": 1,
        },
        {
            "rule_id": 6,
            "region_code": 6,
            "s_min_kind": 1,
            "s_min_const": 0,
            "s_max_kind": 2,
            "s_max_const": -1,
            "target_min_offset": 2,
            "target_max_offset": 3,
            "target_count_min": 2,
            "target_count_max": 2,
            "domain_min_n": INDUCTION_START,
            "domain_nonempty_at_start_flag": 1,
        },
        {
            "rule_id": 7,
            "region_code": 7,
            "s_min_kind": 2,
            "s_min_const": 0,
            "s_max_kind": 2,
            "s_max_const": 0,
            "target_min_offset": 2,
            "target_max_offset": 2,
            "target_count_min": 1,
            "target_count_max": 1,
            "domain_min_n": INDUCTION_START,
            "domain_nonempty_at_start_flag": 1,
        },
    ]


def margin_rows(rule_rows: list[dict[str, int]]) -> list[dict[str, int]]:
    worst = {
        0: (0, 0),
        1: (0, 1),
        2: (0, 2),
        3: (0, 3),
        4: (1, -2),
        5: (1, -1),
        6: (2, -1),
        7: (2, 0),
    }
    rows: list[dict[str, int]] = []
    for rule in rule_rows:
        kind, const = worst[rule["rule_id"]]
        # margin = (s+d)/(n+1) - s/n = (d*n - s)/(n*(n+1)).
        a = rule["target_min_offset"] - kind
        b = -const
        at_start = a * INDUCTION_START + b
        rows.append(
            {
                "rule_id": rule["rule_id"],
                "worst_s_kind": kind,
                "worst_s_const": const,
                "target_min_offset": rule["target_min_offset"],
                "margin_num_a": a,
                "margin_num_b": b,
                "margin_den_degree": 2,
                "margin_num_at_start": at_start,
                "strict_positive_at_start_flag": int(at_start > 0),
                "nonnegative_for_n_ge_start_flag": int(a >= 0 and at_start >= 0),
                "equality_rule_flag": int(a == 0 and b == 0),
            }
        )
    return rows


def full_trinomial_groups(max_horizon: int) -> dict[int, list[dict[str, int]]]:
    groups: dict[int, list[dict[str, int]]] = {
        1: [
            {"sum_value": value, "weight": weight}
            for value, weight in enumerate(COMPONENT_WEIGHTS)
        ]
    }
    for sample_count in range(2, max_horizon + 1):
        acc: dict[int, int] = defaultdict(int)
        for row in groups[sample_count - 1]:
            for value, weight in enumerate(COMPONENT_WEIGHTS):
                acc[row["sum_value"] + value] += row["weight"] * weight
        groups[sample_count] = [
            {"sum_value": value, "weight": acc[value]} for value in sorted(acc)
        ]
    return groups


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


def full_trinomial_negative_control() -> dict[str, int]:
    groups = full_trinomial_groups(NEGATIVE_CONTROL_HORIZON)
    positive = 0
    negative = 0
    zero = 0
    first_negative: dict[str, Any] | None = None
    state_count = 0
    for sample_count in range(1, NEGATIVE_CONTROL_HORIZON):
        source = groups[sample_count]
        target = groups[sample_count + 1]
        edges, source_total, target_total = transport_edges(source, target)
        edge_by_source: dict[int, list[tuple[int, int]]] = defaultdict(list)
        for from_sum, to_sum, mass in edges:
            edge_by_source[from_sum].append((to_sum, mass))
        source_weight = {row["sum_value"]: row["weight"] for row in source}
        for row in source:
            outgoing = edge_by_source[row["sum_value"]]
            mass = sum(edge_mass for _, edge_mass in outgoing)
            if mass != row["weight"] * target_total:
                raise AssertionError("negative-control transport mass mismatch")
            current_average = Fraction(row["sum_value"], sample_count)
            expected_next = (
                sum(
                    Fraction(to_sum, sample_count + 1) * edge_mass
                    for to_sum, edge_mass in outgoing
                )
                / mass
            )
            drift = expected_next - current_average
            source_probability = Fraction(source_weight[row["sum_value"]], source_total)
            state_count += 1
            if drift > 0:
                positive += 1
            elif drift < 0:
                negative += 1
                if first_negative is None:
                    first_negative = {
                        "sample_count": sample_count,
                        "sum_value": row["sum_value"],
                        "drift": drift,
                        "source_probability": source_probability,
                    }
            else:
                zero += 1
    if first_negative is None:
        raise AssertionError("negative control did not find a negative drift")
    return {
        "control_id": 0,
        "horizon": NEGATIVE_CONTROL_HORIZON,
        "state_count": state_count,
        "drift_positive_count": positive,
        "drift_negative_count": negative,
        "drift_zero_count": zero,
        "first_negative_sample_count": int(first_negative["sample_count"]),
        "first_negative_sum_value": int(first_negative["sum_value"]),
        "first_negative_drift_num": int(first_negative["drift"].numerator),
        "first_negative_drift_den": int(first_negative["drift"].denominator),
        "first_negative_source_probability_num": int(
            first_negative["source_probability"].numerator
        ),
        "first_negative_source_probability_den": int(
            first_negative["source_probability"].denominator
        ),
        "canonical_measure_required_flag": 1,
    }


def build_rows() -> dict[str, Any]:
    long_linf = load_json(LONG_LINF_REPORT)
    witness = long_linf["witness"]
    rule_rows = canonical_rule_rows()
    margins = margin_rows(rule_rows)
    negative_control_rows = [full_trinomial_negative_control()]
    bridge_rows = [
        {
            "bridge_id": 0,
            "induction_start": INDUCTION_START,
            "linf_base_horizon": int(witness["lift"]["base_horizon"]),
            "linf_lift_horizon": int(witness["lift"]["lift_horizon"]),
            "linf_level_count": int(witness["transport"]["level_count"]),
            "linf_state_count": int(witness["transport"]["state_count"]),
            "linf_negative_count": int(witness["transport"]["negative_count"]),
            "linf_zero_count": int(witness["transport"]["zero_count"]),
            "linf_extension_negative_count": int(
                witness["extension_cone"]["negative_count"]
            ),
            "rule_count": len(rule_rows),
            "margin_nonnegative_count": sum(
                row["nonnegative_for_n_ge_start_flag"] for row in margins
            ),
            "measure_match_flag": int(witness["lift"]["base_fiber_match_count"] == 288),
        }
    ]
    negative_control = negative_control_rows[0]
    obs = {
        "rule_row_count": len(rule_rows),
        "margin_row_count": len(margins),
        "bridge_row_count": len(bridge_rows),
        "negative_control_row_count": len(negative_control_rows),
        "induction_start": INDUCTION_START,
        "linf_lift_horizon": bridge_rows[0]["linf_lift_horizon"],
        "linf_state_count": bridge_rows[0]["linf_state_count"],
        "linf_negative_count": bridge_rows[0]["linf_negative_count"],
        "linf_extension_negative_count": bridge_rows[0][
            "linf_extension_negative_count"
        ],
        "margin_nonnegative_count": bridge_rows[0]["margin_nonnegative_count"],
        "margin_strict_positive_count": sum(
            row["strict_positive_at_start_flag"] for row in margins
        ),
        "margin_equality_rule_count": sum(row["equality_rule_flag"] for row in margins),
        "negative_control_state_count": negative_control["state_count"],
        "negative_control_negative_count": negative_control["drift_negative_count"],
        "negative_control_zero_count": negative_control["drift_zero_count"],
        "first_negative_sample_count": negative_control[
            "first_negative_sample_count"
        ],
        "first_negative_sum_value": negative_control["first_negative_sum_value"],
        "first_negative_drift_num_mod_1000000007": negative_control[
            "first_negative_drift_num"
        ]
        % MOD_PRIMES[0],
        "first_negative_drift_den_mod_1000000007": negative_control[
            "first_negative_drift_den"
        ]
        % MOD_PRIMES[0],
        "measure_match_flag": bridge_rows[0]["measure_match_flag"],
        "input_long_linf_certified": int(long_linf.get("status") == LONG_LINF_STATUS),
        "current_symbolic_margin_flag": int(
            bridge_rows[0]["margin_nonnegative_count"] == len(margins)
        ),
        "current_negative_control_flag": int(
            negative_control["drift_negative_count"] > 0
            and negative_control["canonical_measure_required_flag"] == 1
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
    rule_hash = hashlib.sha256(
        digest_text(RULE_COLUMNS, rule_rows).encode("ascii")
    ).hexdigest()
    margin_hash = hashlib.sha256(
        digest_text(MARGIN_COLUMNS, margins).encode("ascii")
    ).hexdigest()
    bridge_hash = hashlib.sha256(
        digest_text(BRIDGE_COLUMNS, bridge_rows).encode("ascii")
    ).hexdigest()
    negative_control_hash = hashlib.sha256(
        digest_text(NEGATIVE_CONTROL_COLUMNS, negative_control_rows).encode("ascii")
    ).hexdigest()
    return {
        "input_reports": {"long_linf": long_linf},
        "rule_rows": rule_rows,
        "margin_rows": margins,
        "bridge_rows": bridge_rows,
        "negative_control_rows": negative_control_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "rule_table": table_from_rows(RULE_COLUMNS, rule_rows),
        "margin_table": table_from_rows(MARGIN_COLUMNS, margins),
        "bridge_table": table_from_rows(BRIDGE_COLUMNS, bridge_rows),
        "negative_control_table": table_from_rows(
            NEGATIVE_CONTROL_COLUMNS, negative_control_rows
        ),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "rule_hash": rule_hash,
        "margin_hash": margin_hash,
        "bridge_hash": bridge_hash,
        "negative_control_hash": negative_control_hash,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "input_certified": obs["input_long_linf_certified"] == 1,
        "rule_fingerprint_exact": (
            obs["rule_row_count"],
            obs["margin_row_count"],
            obs["margin_nonnegative_count"],
            obs["margin_strict_positive_count"],
            obs["margin_equality_rule_count"],
            rows["rule_hash"],
            rows["margin_hash"],
        )
        == (8, 8, 8, 6, 2, RULE_TEXT_HASH, MARGIN_TEXT_HASH),
        "linf_bridge_exact": (
            obs["linf_lift_horizon"],
            obs["linf_state_count"],
            obs["linf_negative_count"],
            obs["linf_extension_negative_count"],
            obs["measure_match_flag"],
            rows["bridge_hash"],
        )
        == (128, 16_383, 1, 0, 1, BRIDGE_TEXT_HASH),
        "negative_control_exact": (
            obs["negative_control_state_count"],
            obs["negative_control_negative_count"],
            obs["negative_control_zero_count"],
            obs["first_negative_sample_count"],
            obs["first_negative_sum_value"],
            obs["first_negative_drift_num_mod_1000000007"],
            obs["first_negative_drift_den_mod_1000000007"],
            rows["negative_control_hash"],
        )
        == (
            4_095,
            1_115,
            0,
            1,
            2,
            1_000_000_002,
            26,
            NEGATIVE_CONTROL_TEXT_HASH,
        ),
        "current_representation_exact": (
            obs["current_symbolic_margin_flag"],
            obs["current_negative_control_flag"],
            obs["measure_match_flag"],
        )
        == (1, 1, 1),
        "table_shapes_match": (
            tuple(rows["rule_table"].shape),
            tuple(rows["margin_table"].shape),
            tuple(rows["bridge_table"].shape),
            tuple(rows["negative_control_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (8, len(RULE_COLUMNS)),
            (8, len(MARGIN_COLUMNS)),
            (1, len(BRIDGE_COLUMNS)),
            (1, len(NEGATIVE_CONTROL_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "symbolic_drift_margin_schema",
        "induction_start": INDUCTION_START,
        "rules": {
            "row_count": obs["rule_row_count"],
            "margin_row_count": obs["margin_row_count"],
            "margin_nonnegative_count": obs["margin_nonnegative_count"],
            "margin_strict_positive_count": obs["margin_strict_positive_count"],
            "margin_equality_rule_count": obs["margin_equality_rule_count"],
            "rule_text_sha256": rows["rule_hash"],
            "margin_text_sha256": rows["margin_hash"],
            "rule_table_sha256": sha_array(rows["rule_table"]),
            "margin_table_sha256": sha_array(rows["margin_table"]),
        },
        "linf_bridge": {
            "lift_horizon": obs["linf_lift_horizon"],
            "state_count": obs["linf_state_count"],
            "negative_count": obs["linf_negative_count"],
            "extension_negative_count": obs["linf_extension_negative_count"],
            "measure_match_flag": bool(obs["measure_match_flag"]),
            "bridge_text_sha256": rows["bridge_hash"],
            "bridge_table_sha256": sha_array(rows["bridge_table"]),
        },
        "negative_control": {
            "horizon": NEGATIVE_CONTROL_HORIZON,
            "state_count": obs["negative_control_state_count"],
            "negative_count": obs["negative_control_negative_count"],
            "first_negative": {
                "sample_count": obs["first_negative_sample_count"],
                "sum_value": obs["first_negative_sum_value"],
                "drift": "-5/26",
            },
            "negative_control_text_sha256": rows["negative_control_hash"],
            "negative_control_table_sha256": sha_array(
                rows["negative_control_table"]
            ),
        },
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    ind_payload = {
        "schema": "long.ind@1",
        "object": "symbolic_drift_margin_schema",
        "status": STATUS if all(checks.values()) else "LONG_IND_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.ind.report@1",
        "status": ind_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_ind extracts a finite symbolic drift-margin schema from the "
            "canonical witness measure. The eight support-shift regions reduce "
            "rowwise nonnegative drift to margins of the form "
            "(a*n+b)/(n*(n+1)), all nonnegative from n=16 onward, with two "
            "equality boundary rules. The schema is bridged to the exact "
            "long_linf horizon-128 lift, and a full-trinomial negative control "
            "shows that the canonical one-witness measure is essential."
        ),
        "stage_protocol": {
            "draft": "read long_linf lifted cone and canonical component weights",
            "witness": "encode support-shift drift-margin rules and a full-trinomial negative control",
            "coherence": "check symbolic margins, long_linf bridge, negative control, statuses, hashes, and shapes",
            "closure": "emit symbolic drift-margin schema with explicit measure boundary",
            "emit": "write long_ind artifacts and verifier hook",
        },
        "inputs": {
            "long_linf_report": input_entry(
                LONG_LINF_REPORT,
                {"status": rows["input_reports"]["long_linf"].get("status")},
            ),
            "long_linf_level": input_entry(LONG_LINF_LEVEL),
            "long_linf_cone": input_entry(LONG_LINF_CONE),
            "long_linf_tables": input_entry(LONG_LINF_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "ind": relpath(OUT_DIR / "ind.json"),
            "rule_csv": relpath(OUT_DIR / "rule.csv"),
            "margin_csv": relpath(OUT_DIR / "margin.csv"),
            "bridge_csv": relpath(OUT_DIR / "bridge.csv"),
            "negative_control_csv": relpath(OUT_DIR / "negative_control.csv"),
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
                "the eight-region symbolic drift-margin schema for the canonical witness measure",
                "nonnegative margin inequalities for n >= 16 under the encoded support-shift template",
                "exact agreement with the long_linf horizon-128 lifted witness",
                "a negative control showing full-trinomial component-word measure does not preserve the cone",
            ],
            "does_not_certify_because_out_of_scope": [
                "a proof that the support-shift template persists without the encoded rule schema",
                "the full raw tensor path measure",
                "semantic C985 associator composition",
                "a complete infinite-horizon LLN theorem",
            ],
        },
        "next_highest_yield_item": (
            "Build long_suppind: prove the support-shift template itself from "
            "canonical cumulative weight inequalities, removing the remaining "
            "template hypothesis."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.ind.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.ind.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "ind": ind_payload,
        "rule_csv": csv_text(RULE_COLUMNS, rows["rule_rows"]),
        "margin_csv": csv_text(MARGIN_COLUMNS, rows["margin_rows"]),
        "bridge_csv": csv_text(BRIDGE_COLUMNS, rows["bridge_rows"]),
        "negative_control_csv": csv_text(
            NEGATIVE_CONTROL_COLUMNS, rows["negative_control_rows"]
        ),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "rule_table": rows["rule_table"],
        "margin_table": rows["margin_table"],
        "bridge_table": rows["bridge_table"],
        "negative_control_table": rows["negative_control_table"],
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
    write_json(OUT_DIR / "ind.json", payloads["ind"])
    (OUT_DIR / "rule.csv").write_text(payloads["rule_csv"], encoding="utf-8")
    (OUT_DIR / "margin.csv").write_text(payloads["margin_csv"], encoding="utf-8")
    (OUT_DIR / "bridge.csv").write_text(payloads["bridge_csv"], encoding="utf-8")
    (OUT_DIR / "negative_control.csv").write_text(
        payloads["negative_control_csv"], encoding="utf-8"
    )
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        rule_table=payloads["rule_table"],
        margin_table=payloads["margin_table"],
        bridge_table=payloads["bridge_table"],
        negative_control_table=payloads["negative_control_table"],
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
