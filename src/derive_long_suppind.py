from __future__ import annotations

import hashlib
import json
from collections import defaultdict
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
    from .derive_long_ind import (
        OUT_DIR as LONG_IND_DIR,
        RULE_COLUMNS as LONG_IND_RULE_COLUMNS,
        RULE_TEXT_HASH as LONG_IND_RULE_TEXT_HASH,
        STATUS as LONG_IND_STATUS,
    )
    from .derive_long_linf import (
        LIFT_HORIZON,
        OUT_DIR as LONG_LINF_DIR,
        STATUS as LONG_LINF_STATUS,
        canonical_counts,
        canonical_weight,
        transport_edges,
    )
    from .derive_long_prob import COMPONENT_WEIGHTS
    from .derive_long_raw import csv_text, digest_text, int_rows, read_csv_rows, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_ind import (
        OUT_DIR as LONG_IND_DIR,
        RULE_COLUMNS as LONG_IND_RULE_COLUMNS,
        RULE_TEXT_HASH as LONG_IND_RULE_TEXT_HASH,
        STATUS as LONG_IND_STATUS,
    )
    from derive_long_linf import (
        LIFT_HORIZON,
        OUT_DIR as LONG_LINF_DIR,
        STATUS as LONG_LINF_STATUS,
        canonical_counts,
        canonical_weight,
        transport_edges,
    )
    from derive_long_prob import COMPONENT_WEIGHTS
    from derive_long_raw import csv_text, digest_text, int_rows, read_csv_rows, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_suppind"
STATUS = "LONG_SUPPIND_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

LONG_IND_REPORT = LONG_IND_DIR / "report.json"
LONG_IND_RULE = LONG_IND_DIR / "rule.csv"
LONG_IND_TABLES = LONG_IND_DIR / "tables.npz"
LONG_LINF_REPORT = LONG_LINF_DIR / "report.json"
LONG_LINF_TABLES = LONG_LINF_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_suppind.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_suppind.py"

INDUCTION_START = 16
SOURCE_END = LIFT_HORIZON - 1

SUPPORT_TEXT_HASH = "3db7ccc99709fab46790e580e6a8c54512a530bf880af963bcc7b4da7306dae7"
RULE_SUMMARY_TEXT_HASH = "8f1bf9e64a45cf0fe1bc4e0c21f9eebff962da0f0ed836f3c9077420f186c9eb"
BRIDGE_TEXT_HASH = "7b1cdb9736e4155f7078b9c2563b358c16d0d8c627311bc5f7cca39134bf80f8"

MOD_PRIMES = (1_000_000_007, 1_000_000_009)

SUPPORT_COLUMNS = [
    "support_id",
    "sample_count",
    "sum_value",
    "rule_id",
    "target_min_sum",
    "target_max_sum",
    "actual_min_sum",
    "actual_max_sum",
    "actual_target_count",
    "expected_target_count",
    "lower_gap_sign",
    "lower_gap_zero_flag",
    "lower_gap_digits",
    "lower_gap_mod_1000000007",
    "lower_gap_mod_1000000009",
    "upper_gap_sign",
    "upper_gap_zero_flag",
    "upper_gap_digits",
    "upper_gap_mod_1000000007",
    "upper_gap_mod_1000000009",
    "support_inside_flag",
    "target_count_match_flag",
    "cumulative_certificate_flag",
]
RULE_SUMMARY_COLUMNS = [
    "rule_id",
    "state_count",
    "target_min_offset",
    "target_max_offset",
    "expected_target_count_min",
    "expected_target_count_max",
    "actual_target_count_min",
    "actual_target_count_max",
    "lower_gap_nonnegative_count",
    "upper_gap_nonnegative_count",
    "lower_gap_zero_count",
    "upper_gap_zero_count",
    "support_inside_count",
    "target_count_match_count",
    "cumulative_certificate_count",
    "lower_min_digits",
    "lower_min_mod_1000000007",
    "lower_min_mod_1000000009",
    "upper_min_digits",
    "upper_min_mod_1000000007",
    "upper_min_mod_1000000009",
    "rule_certificate_flag",
]
BRIDGE_COLUMNS = [
    "bridge_id",
    "induction_start",
    "source_end_sample_count",
    "lift_horizon",
    "support_state_count",
    "rule_count",
    "support_certified_count",
    "lower_gap_nonnegative_count",
    "upper_gap_nonnegative_count",
    "target_count_match_count",
    "long_ind_certified_flag",
    "long_linf_certified_flag",
    "long_ind_rule_hash_match_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "induction_start",
    "source_end_sample_count",
    "lift_horizon",
    "support_state_count",
    "rule_summary_count",
    "bridge_row_count",
    "lower_gap_nonnegative_count",
    "upper_gap_nonnegative_count",
    "lower_gap_zero_count",
    "upper_gap_zero_count",
    "support_inside_count",
    "target_count_match_count",
    "cumulative_certificate_count",
    "rule_certificate_count",
    "actual_target_count_min",
    "actual_target_count_max",
    "rule0_state_count",
    "rule4_state_count",
    "rule6_state_count",
    "input_long_ind_certified",
    "input_long_linf_certified",
    "long_ind_rule_hash_match_flag",
    "current_support_rule_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sign(value: int) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def digits(value: int) -> int:
    return len(str(abs(value)))


def gap_fields(prefix: str, value: int) -> dict[str, int]:
    return {
        f"{prefix}_sign": sign(value),
        f"{prefix}_zero_flag": int(value == 0),
        f"{prefix}_digits": digits(value),
        f"{prefix}_mod_1000000007": value % MOD_PRIMES[0],
        f"{prefix}_mod_1000000009": value % MOD_PRIMES[1],
    }


def build_groups() -> dict[int, list[dict[str, int]]]:
    groups: dict[int, list[dict[str, int]]] = {}
    for sample_count in range(INDUCTION_START, LIFT_HORIZON + 1):
        rows = []
        for sum_value in range(0, 2 * sample_count + 1):
            rows.append(
                {
                    "sum_value": sum_value,
                    "weight": canonical_weight(
                        canonical_counts(sample_count, sum_value)
                    ),
                }
            )
        groups[sample_count] = rows
    return groups


def prefix_tables(groups: dict[int, list[dict[str, int]]]) -> dict[int, list[int]]:
    tables: dict[int, list[int]] = {}
    for sample_count, rows in groups.items():
        total = 0
        cumulatives = []
        for row in rows:
            total += row["weight"]
            cumulatives.append(total)
        tables[sample_count] = cumulatives
    return tables


def prefix(cumulatives: list[int], sum_value: int) -> int:
    if sum_value < 0:
        return 0
    if sum_value >= len(cumulatives):
        return cumulatives[-1]
    return cumulatives[sum_value]


def select_rule_id(sample_count: int, sum_value: int) -> int:
    if sum_value == 0:
        return 0
    if sum_value == 1:
        return 1
    if sum_value == 2:
        return 2
    if sum_value == 3:
        return 3
    if 4 <= sum_value <= sample_count - 2:
        return 4
    if sum_value == sample_count - 1:
        return 5
    if sample_count <= sum_value <= 2 * sample_count - 1:
        return 6
    if sum_value == 2 * sample_count:
        return 7
    raise AssertionError("sum value does not match a support rule")


def build_support_rows(
    groups: dict[int, list[dict[str, int]]],
    cumulatives: dict[int, list[int]],
    rule_rows: list[dict[str, int]],
) -> list[dict[str, int]]:
    rules = {row["rule_id"]: row for row in rule_rows}
    support_rows: list[dict[str, int]] = []
    support_id = 0
    for sample_count in range(INDUCTION_START, SOURCE_END + 1):
        source = groups[sample_count]
        target = groups[sample_count + 1]
        source_total = cumulatives[sample_count][-1]
        target_total = cumulatives[sample_count + 1][-1]
        edges, _, _ = transport_edges(source, target)
        edge_by_source: dict[int, list[int]] = defaultdict(list)
        for from_sum, to_sum, mass in edges:
            if mass > 0:
                edge_by_source[from_sum].append(to_sum)
        for row in source:
            sum_value = row["sum_value"]
            rule_id = select_rule_id(sample_count, sum_value)
            rule = rules[rule_id]
            target_min = sum_value + rule["target_min_offset"]
            target_max = sum_value + rule["target_max_offset"]
            actual_targets = sorted(set(edge_by_source[sum_value]))
            actual_min = actual_targets[0]
            actual_max = actual_targets[-1]
            actual_count = len(actual_targets)
            expected_count = rule["target_count_min"]
            lower_gap = (
                prefix(cumulatives[sample_count], sum_value - 1) * target_total
                - prefix(cumulatives[sample_count + 1], target_min - 1)
                * source_total
            )
            upper_gap = (
                prefix(cumulatives[sample_count + 1], target_max) * source_total
                - prefix(cumulatives[sample_count], sum_value) * target_total
            )
            support_inside = int(actual_min >= target_min and actual_max <= target_max)
            target_count_match = int(
                actual_count == expected_count
                and rule["target_count_min"] == rule["target_count_max"]
            )
            row_payload = {
                "support_id": support_id,
                "sample_count": sample_count,
                "sum_value": sum_value,
                "rule_id": rule_id,
                "target_min_sum": target_min,
                "target_max_sum": target_max,
                "actual_min_sum": actual_min,
                "actual_max_sum": actual_max,
                "actual_target_count": actual_count,
                "expected_target_count": expected_count,
                "_lower_gap_value": lower_gap,
                "_upper_gap_value": upper_gap,
            }
            row_payload.update(gap_fields("lower_gap", lower_gap))
            row_payload.update(gap_fields("upper_gap", upper_gap))
            row_payload.update(
                {
                    "support_inside_flag": support_inside,
                    "target_count_match_flag": target_count_match,
                    "cumulative_certificate_flag": int(
                        lower_gap >= 0
                        and upper_gap >= 0
                        and support_inside
                        and target_count_match
                    ),
                }
            )
            support_rows.append(row_payload)
            support_id += 1
    return support_rows


def summarize_rules(
    support_rows: list[dict[str, int]],
    rule_rows: list[dict[str, int]],
) -> list[dict[str, int]]:
    rows_by_rule: dict[int, list[dict[str, int]]] = defaultdict(list)
    for row in support_rows:
        rows_by_rule[row["rule_id"]].append(row)
    rule_by_id = {row["rule_id"]: row for row in rule_rows}
    summaries: list[dict[str, int]] = []
    for rule_id in sorted(rule_by_id):
        rows = rows_by_rule[rule_id]
        rule = rule_by_id[rule_id]
        lower_min = min(row["_lower_gap_value"] for row in rows)
        upper_min = min(row["_upper_gap_value"] for row in rows)
        summaries.append(
            {
                "rule_id": rule_id,
                "state_count": len(rows),
                "target_min_offset": rule["target_min_offset"],
                "target_max_offset": rule["target_max_offset"],
                "expected_target_count_min": rule["target_count_min"],
                "expected_target_count_max": rule["target_count_max"],
                "actual_target_count_min": min(row["actual_target_count"] for row in rows),
                "actual_target_count_max": max(row["actual_target_count"] for row in rows),
                "lower_gap_nonnegative_count": sum(
                    int(row["lower_gap_sign"] >= 0) for row in rows
                ),
                "upper_gap_nonnegative_count": sum(
                    int(row["upper_gap_sign"] >= 0) for row in rows
                ),
                "lower_gap_zero_count": sum(row["lower_gap_zero_flag"] for row in rows),
                "upper_gap_zero_count": sum(row["upper_gap_zero_flag"] for row in rows),
                "support_inside_count": sum(row["support_inside_flag"] for row in rows),
                "target_count_match_count": sum(
                    row["target_count_match_flag"] for row in rows
                ),
                "cumulative_certificate_count": sum(
                    row["cumulative_certificate_flag"] for row in rows
                ),
                "lower_min_digits": digits(lower_min),
                "lower_min_mod_1000000007": lower_min % MOD_PRIMES[0],
                "lower_min_mod_1000000009": lower_min % MOD_PRIMES[1],
                "upper_min_digits": digits(upper_min),
                "upper_min_mod_1000000007": upper_min % MOD_PRIMES[0],
                "upper_min_mod_1000000009": upper_min % MOD_PRIMES[1],
                "rule_certificate_flag": int(
                    sum(row["cumulative_certificate_flag"] for row in rows)
                    == len(rows)
                ),
            }
        )
    return summaries


def build_rows() -> dict[str, Any]:
    long_ind = load_json(LONG_IND_REPORT)
    long_linf = load_json(LONG_LINF_REPORT)
    rule_rows = int_rows(read_csv_rows(LONG_IND_RULE))
    rule_hash = hashlib.sha256(
        digest_text(LONG_IND_RULE_COLUMNS, rule_rows).encode("ascii")
    ).hexdigest()
    groups = build_groups()
    cumulatives = prefix_tables(groups)
    support_rows = build_support_rows(groups, cumulatives, rule_rows)
    rule_summary_rows = summarize_rules(support_rows, rule_rows)
    bridge_rows = [
        {
            "bridge_id": 0,
            "induction_start": INDUCTION_START,
            "source_end_sample_count": SOURCE_END,
            "lift_horizon": LIFT_HORIZON,
            "support_state_count": len(support_rows),
            "rule_count": len(rule_summary_rows),
            "support_certified_count": sum(
                row["cumulative_certificate_flag"] for row in support_rows
            ),
            "lower_gap_nonnegative_count": sum(
                int(row["lower_gap_sign"] >= 0) for row in support_rows
            ),
            "upper_gap_nonnegative_count": sum(
                int(row["upper_gap_sign"] >= 0) for row in support_rows
            ),
            "target_count_match_count": sum(
                row["target_count_match_flag"] for row in support_rows
            ),
            "long_ind_certified_flag": int(long_ind.get("status") == LONG_IND_STATUS),
            "long_linf_certified_flag": int(
                long_linf.get("status") == LONG_LINF_STATUS
            ),
            "long_ind_rule_hash_match_flag": int(
                rule_hash == LONG_IND_RULE_TEXT_HASH
                and rule_hash
                == long_ind["witness"]["rules"]["rule_text_sha256"]
            ),
        }
    ]
    obs = {
        "induction_start": INDUCTION_START,
        "source_end_sample_count": SOURCE_END,
        "lift_horizon": LIFT_HORIZON,
        "support_state_count": len(support_rows),
        "rule_summary_count": len(rule_summary_rows),
        "bridge_row_count": len(bridge_rows),
        "lower_gap_nonnegative_count": bridge_rows[0]["lower_gap_nonnegative_count"],
        "upper_gap_nonnegative_count": bridge_rows[0]["upper_gap_nonnegative_count"],
        "lower_gap_zero_count": sum(row["lower_gap_zero_flag"] for row in support_rows),
        "upper_gap_zero_count": sum(row["upper_gap_zero_flag"] for row in support_rows),
        "support_inside_count": sum(row["support_inside_flag"] for row in support_rows),
        "target_count_match_count": bridge_rows[0]["target_count_match_count"],
        "cumulative_certificate_count": bridge_rows[0]["support_certified_count"],
        "rule_certificate_count": sum(
            row["rule_certificate_flag"] for row in rule_summary_rows
        ),
        "actual_target_count_min": min(
            row["actual_target_count"] for row in support_rows
        ),
        "actual_target_count_max": max(
            row["actual_target_count"] for row in support_rows
        ),
        "rule0_state_count": rule_summary_rows[0]["state_count"],
        "rule4_state_count": rule_summary_rows[4]["state_count"],
        "rule6_state_count": rule_summary_rows[6]["state_count"],
        "input_long_ind_certified": bridge_rows[0]["long_ind_certified_flag"],
        "input_long_linf_certified": bridge_rows[0]["long_linf_certified_flag"],
        "long_ind_rule_hash_match_flag": bridge_rows[0][
            "long_ind_rule_hash_match_flag"
        ],
        "current_support_rule_flag": int(
            bridge_rows[0]["support_certified_count"] == len(support_rows)
            and sum(row["rule_certificate_flag"] for row in rule_summary_rows)
            == len(rule_summary_rows)
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
    support_hash = hashlib.sha256(
        digest_text(SUPPORT_COLUMNS, support_rows).encode("ascii")
    ).hexdigest()
    rule_summary_hash = hashlib.sha256(
        digest_text(RULE_SUMMARY_COLUMNS, rule_summary_rows).encode("ascii")
    ).hexdigest()
    bridge_hash = hashlib.sha256(
        digest_text(BRIDGE_COLUMNS, bridge_rows).encode("ascii")
    ).hexdigest()
    return {
        "input_reports": {"long_ind": long_ind, "long_linf": long_linf},
        "support_rows": support_rows,
        "rule_summary_rows": rule_summary_rows,
        "bridge_rows": bridge_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "support_table": table_from_rows(SUPPORT_COLUMNS, support_rows),
        "rule_summary_table": table_from_rows(
            RULE_SUMMARY_COLUMNS, rule_summary_rows
        ),
        "bridge_table": table_from_rows(BRIDGE_COLUMNS, bridge_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "support_hash": support_hash,
        "rule_summary_hash": rule_summary_hash,
        "bridge_hash": bridge_hash,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "input_certified": (
            obs["input_long_ind_certified"],
            obs["input_long_linf_certified"],
            obs["long_ind_rule_hash_match_flag"],
        )
        == (1, 1, 1),
        "support_inequalities_exact": (
            obs["support_state_count"],
            obs["lower_gap_nonnegative_count"],
            obs["upper_gap_nonnegative_count"],
            obs["lower_gap_zero_count"],
            obs["upper_gap_zero_count"],
            rows["support_hash"],
        )
        == (
            16_128,
            16_128,
            16_128,
            112,
            112,
            SUPPORT_TEXT_HASH,
        ),
        "support_rule_exact": (
            obs["rule_summary_count"],
            obs["support_inside_count"],
            obs["target_count_match_count"],
            obs["cumulative_certificate_count"],
            obs["rule_certificate_count"],
            obs["actual_target_count_min"],
            obs["actual_target_count_max"],
            rows["rule_summary_hash"],
        )
        == (
            8,
            16_128,
            16_128,
            16_128,
            8,
            1,
            3,
            RULE_SUMMARY_TEXT_HASH,
        ),
        "rule_population_exact": (
            obs["rule0_state_count"],
            obs["rule4_state_count"],
            obs["rule6_state_count"],
            rows["bridge_hash"],
        )
        == (112, 7_448, 8_008, BRIDGE_TEXT_HASH),
        "current_representation_exact": obs["current_support_rule_flag"] == 1,
        "table_shapes_match": (
            tuple(rows["support_table"].shape),
            tuple(rows["rule_summary_table"].shape),
            tuple(rows["bridge_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (16_128, len(SUPPORT_COLUMNS)),
            (8, len(RULE_SUMMARY_COLUMNS)),
            (1, len(BRIDGE_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "support_shift_cumulative_inequality_certificate",
        "support": {
            "induction_start": INDUCTION_START,
            "source_end_sample_count": SOURCE_END,
            "lift_horizon": LIFT_HORIZON,
            "component_weights": list(COMPONENT_WEIGHTS),
            "state_count": obs["support_state_count"],
            "lower_gap_nonnegative_count": obs["lower_gap_nonnegative_count"],
            "upper_gap_nonnegative_count": obs["upper_gap_nonnegative_count"],
            "lower_gap_zero_count": obs["lower_gap_zero_count"],
            "upper_gap_zero_count": obs["upper_gap_zero_count"],
            "support_text_sha256": rows["support_hash"],
            "support_table_sha256": sha_array(rows["support_table"]),
        },
        "rules": {
            "rule_count": obs["rule_summary_count"],
            "certified_rule_count": obs["rule_certificate_count"],
            "support_inside_count": obs["support_inside_count"],
            "target_count_match_count": obs["target_count_match_count"],
            "actual_target_count_min": obs["actual_target_count_min"],
            "actual_target_count_max": obs["actual_target_count_max"],
            "rule_summary_text_sha256": rows["rule_summary_hash"],
            "rule_summary_table_sha256": sha_array(rows["rule_summary_table"]),
        },
        "bridge": {
            "long_ind_certified": bool(obs["input_long_ind_certified"]),
            "long_linf_certified": bool(obs["input_long_linf_certified"]),
            "long_ind_rule_hash_match": bool(obs["long_ind_rule_hash_match_flag"]),
            "bridge_text_sha256": rows["bridge_hash"],
            "bridge_table_sha256": sha_array(rows["bridge_table"]),
        },
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    suppind_payload = {
        "schema": "long.suppind@1",
        "object": "support_shift_cumulative_inequality_certificate",
        "status": STATUS if all(checks.values()) else "LONG_SUPPIND_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.suppind.report@1",
        "status": suppind_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_suppind proves the eight support-shift regions used by "
            "long_ind on the whole long_linf lifted extension cone. For each "
            "canonical source state n=16..127, exact prefix-mass inequalities "
            "exclude all target sums below and above the claimed interval, and "
            "the monotone transport target count matches the rule row."
        ),
        "stage_protocol": {
            "draft": "read long_ind support rules and long_linf canonical lift boundary",
            "witness": "compute exact source/target cumulative mass gaps and monotone transport supports",
            "coherence": "check lower and upper gap signs, rule counts, input statuses, hashes, and shapes",
            "closure": "emit finite support-shift certificate with explicit cumulative inequalities",
            "emit": "write long_suppind artifacts and verifier hook",
        },
        "inputs": {
            "long_ind_report": input_entry(
                LONG_IND_REPORT,
                {"status": rows["input_reports"]["long_ind"].get("status")},
            ),
            "long_ind_rule": input_entry(LONG_IND_RULE),
            "long_ind_tables": input_entry(LONG_IND_TABLES),
            "long_linf_report": input_entry(
                LONG_LINF_REPORT,
                {"status": rows["input_reports"]["long_linf"].get("status")},
            ),
            "long_linf_tables": input_entry(LONG_LINF_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "suppind": relpath(OUT_DIR / "suppind.json"),
            "support_csv": relpath(OUT_DIR / "support.csv"),
            "rule_summary_csv": relpath(OUT_DIR / "rule_summary.csv"),
            "bridge_csv": relpath(OUT_DIR / "bridge.csv"),
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
                "the long_ind support-shift template on all lifted source states n=16..127",
                "exact nonnegative lower and upper cumulative prefix gaps for 16,128 states",
                "agreement between the claimed support interval and exact monotone transport target counts",
                "the bridge from long_ind rules to the long_linf canonical witness lift",
            ],
            "does_not_certify_because_out_of_scope": [
                "a closed-form recurrence proof of these cumulative inequalities for every n >= 128",
                "the full trinomial component-word measure",
                "semantic C985 associator composition",
                "a complete infinite-horizon LLN theorem",
            ],
        },
        "next_highest_yield_item": (
            "Build long_recind: convert the finite support-gap tables into "
            "closed recurrence inequalities so the support-shift proof no "
            "longer stops at horizon 128."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.suppind.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.suppind.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "suppind": suppind_payload,
        "support_csv": csv_text(SUPPORT_COLUMNS, rows["support_rows"]),
        "rule_summary_csv": csv_text(
            RULE_SUMMARY_COLUMNS, rows["rule_summary_rows"]
        ),
        "bridge_csv": csv_text(BRIDGE_COLUMNS, rows["bridge_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "support_table": rows["support_table"],
        "rule_summary_table": rows["rule_summary_table"],
        "bridge_table": rows["bridge_table"],
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
    write_json(OUT_DIR / "suppind.json", payloads["suppind"])
    (OUT_DIR / "support.csv").write_text(payloads["support_csv"], encoding="utf-8")
    (OUT_DIR / "rule_summary.csv").write_text(
        payloads["rule_summary_csv"], encoding="utf-8"
    )
    (OUT_DIR / "bridge.csv").write_text(payloads["bridge_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        support_table=payloads["support_table"],
        rule_summary_table=payloads["rule_summary_table"],
        bridge_table=payloads["bridge_table"],
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
