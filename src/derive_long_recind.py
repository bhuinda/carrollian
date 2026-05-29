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
    from .derive_long_raw import csv_text, digest_text, int_rows, read_csv_rows, table_from_rows
    from .derive_long_suppind import (
        LONG_IND_RULE,
        OUT_DIR as LONG_SUPPIND_DIR,
        STATUS as LONG_SUPPIND_STATUS,
        build_groups,
        build_support_rows,
        prefix_tables,
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
    from derive_long_raw import csv_text, digest_text, int_rows, read_csv_rows, table_from_rows
    from derive_long_suppind import (
        LONG_IND_RULE,
        OUT_DIR as LONG_SUPPIND_DIR,
        STATUS as LONG_SUPPIND_STATUS,
        build_groups,
        build_support_rows,
        prefix_tables,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_recind"
STATUS = "LONG_RECIND_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

LONG_SUPPIND_REPORT = LONG_SUPPIND_DIR / "report.json"
LONG_SUPPIND_SUPPORT = LONG_SUPPIND_DIR / "support.csv"
LONG_SUPPIND_RULE_SUMMARY = LONG_SUPPIND_DIR / "rule_summary.csv"
LONG_SUPPIND_TABLES = LONG_SUPPIND_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_recind.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_recind.py"

INDUCTION_START = 16
SOURCE_END = 127
RECURRENCE_FACTOR = 12

SEED_TEXT_HASH = "b683f629cb3500f81847266784a61ccdf89e541a723f70b1cb8cca4a6a42d69f"
TRANSITION_TEXT_HASH = "edf63b6cece22d70256b1dd4cd911572a4633eefa8449d98c86ae769c7355cc7"
TYPE_SUMMARY_TEXT_HASH = "f4cedd9895accbd4bdc25641489ddef6363a85d82d1d9049b7e0940b38d8ebe3"
BRIDGE_TEXT_HASH = "907b24866882575e4875efc92c90ee9f2087ae79a6bdda116b7ad96cc7773bc6"

MOD_PRIMES = (1_000_000_007, 1_000_000_009)

SEED_COLUMNS = [
    "seed_id",
    "support_id",
    "sample_count",
    "sum_value",
    "rule_id",
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
    "seed_certificate_flag",
]
TRANSITION_COLUMNS = [
    "transition_id",
    "predecessor_support_id",
    "successor_support_id",
    "predecessor_sample_count",
    "successor_sample_count",
    "predecessor_sum_value",
    "successor_sum_value",
    "predecessor_rule_id",
    "successor_rule_id",
    "transition_type_code",
    "recurrence_factor",
    "lower_delta_sign",
    "lower_delta_zero_flag",
    "lower_delta_digits",
    "lower_delta_mod_1000000007",
    "lower_delta_mod_1000000009",
    "upper_delta_sign",
    "upper_delta_zero_flag",
    "upper_delta_digits",
    "upper_delta_mod_1000000007",
    "upper_delta_mod_1000000009",
    "transition_certificate_flag",
]
TYPE_SUMMARY_COLUMNS = [
    "transition_type_code",
    "predecessor_rule_id",
    "successor_rule_id",
    "transition_count",
    "lower_delta_nonnegative_count",
    "upper_delta_nonnegative_count",
    "lower_delta_zero_count",
    "upper_delta_zero_count",
    "transition_certificate_count",
    "lower_min_digits",
    "lower_min_mod_1000000007",
    "lower_min_mod_1000000009",
    "upper_min_digits",
    "upper_min_mod_1000000007",
    "upper_min_mod_1000000009",
    "type_certificate_flag",
]
BRIDGE_COLUMNS = [
    "bridge_id",
    "induction_start",
    "source_end_sample_count",
    "seed_count",
    "transition_count",
    "transition_type_count",
    "seed_certificate_count",
    "transition_certificate_count",
    "long_suppind_certified_flag",
    "support_row_count_match_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "induction_start",
    "source_end_sample_count",
    "recurrence_factor",
    "seed_count",
    "transition_count",
    "transition_type_count",
    "seed_certificate_count",
    "transition_certificate_count",
    "lower_delta_nonnegative_count",
    "upper_delta_nonnegative_count",
    "lower_delta_zero_count",
    "upper_delta_zero_count",
    "type_certificate_count",
    "support_state_count",
    "long_suppind_support_state_count",
    "long_suppind_certified_flag",
    "support_row_count_match_flag",
    "current_recurrence_graph_flag",
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


def transition_code(predecessor_rule_id: int, successor_rule_id: int) -> int:
    return predecessor_rule_id * 8 + successor_rule_id


def predecessor_key(row: dict[str, int]) -> tuple[int, int]:
    sample_count = row["sample_count"]
    sum_value = row["sum_value"]
    rule_id = row["rule_id"]
    previous_sample = sample_count - 1
    if rule_id <= 4:
        return previous_sample, sum_value
    if rule_id == 5:
        return previous_sample, sum_value
    if rule_id == 6:
        return previous_sample, sum_value - 1
    if rule_id == 7:
        return previous_sample, 2 * previous_sample
    raise AssertionError("unknown support rule")


def load_support_rows() -> list[dict[str, int]]:
    rule_rows = int_rows(read_csv_rows(LONG_IND_RULE))
    groups = build_groups()
    return build_support_rows(groups, prefix_tables(groups), rule_rows)


def build_seed_rows(support_rows: list[dict[str, int]]) -> list[dict[str, int]]:
    rows = []
    seed_id = 0
    for row in support_rows:
        if row["sample_count"] != INDUCTION_START:
            continue
        payload = {
            "seed_id": seed_id,
            "support_id": row["support_id"],
            "sample_count": row["sample_count"],
            "sum_value": row["sum_value"],
            "rule_id": row["rule_id"],
            "lower_gap_sign": row["lower_gap_sign"],
            "lower_gap_zero_flag": row["lower_gap_zero_flag"],
            "lower_gap_digits": row["lower_gap_digits"],
            "lower_gap_mod_1000000007": row["lower_gap_mod_1000000007"],
            "lower_gap_mod_1000000009": row["lower_gap_mod_1000000009"],
            "upper_gap_sign": row["upper_gap_sign"],
            "upper_gap_zero_flag": row["upper_gap_zero_flag"],
            "upper_gap_digits": row["upper_gap_digits"],
            "upper_gap_mod_1000000007": row["upper_gap_mod_1000000007"],
            "upper_gap_mod_1000000009": row["upper_gap_mod_1000000009"],
            "seed_certificate_flag": int(
                row["_lower_gap_value"] >= 0 and row["_upper_gap_value"] >= 0
            ),
        }
        rows.append(payload)
        seed_id += 1
    return rows


def build_transition_rows(support_rows: list[dict[str, int]]) -> list[dict[str, int]]:
    rows_by_key = {
        (row["sample_count"], row["sum_value"]): row for row in support_rows
    }
    rows = []
    transition_id = 0
    for row in support_rows:
        if row["sample_count"] == INDUCTION_START:
            continue
        predecessor = rows_by_key.get(predecessor_key(row))
        if predecessor is None:
            raise AssertionError("missing recurrence predecessor")
        lower_delta = (
            row["_lower_gap_value"]
            - RECURRENCE_FACTOR * predecessor["_lower_gap_value"]
        )
        upper_delta = (
            row["_upper_gap_value"]
            - RECURRENCE_FACTOR * predecessor["_upper_gap_value"]
        )
        payload = {
            "transition_id": transition_id,
            "predecessor_support_id": predecessor["support_id"],
            "successor_support_id": row["support_id"],
            "predecessor_sample_count": predecessor["sample_count"],
            "successor_sample_count": row["sample_count"],
            "predecessor_sum_value": predecessor["sum_value"],
            "successor_sum_value": row["sum_value"],
            "predecessor_rule_id": predecessor["rule_id"],
            "successor_rule_id": row["rule_id"],
            "transition_type_code": transition_code(
                predecessor["rule_id"], row["rule_id"]
            ),
            "recurrence_factor": RECURRENCE_FACTOR,
        }
        payload.update(gap_fields("lower_delta", lower_delta))
        payload.update(gap_fields("upper_delta", upper_delta))
        payload.update(
            {
                "_lower_delta_value": lower_delta,
                "_upper_delta_value": upper_delta,
                "transition_certificate_flag": int(
                    lower_delta >= 0 and upper_delta >= 0
                ),
            }
        )
        rows.append(payload)
        transition_id += 1
    return rows


def summarize_transition_types(
    transition_rows: list[dict[str, int]]
) -> list[dict[str, int]]:
    rows_by_type: dict[int, list[dict[str, int]]] = defaultdict(list)
    for row in transition_rows:
        rows_by_type[row["transition_type_code"]].append(row)
    summary_rows = []
    for type_code in sorted(rows_by_type):
        rows = rows_by_type[type_code]
        lower_min = min(row["_lower_delta_value"] for row in rows)
        upper_min = min(row["_upper_delta_value"] for row in rows)
        predecessor_rule_id = rows[0]["predecessor_rule_id"]
        successor_rule_id = rows[0]["successor_rule_id"]
        summary_rows.append(
            {
                "transition_type_code": type_code,
                "predecessor_rule_id": predecessor_rule_id,
                "successor_rule_id": successor_rule_id,
                "transition_count": len(rows),
                "lower_delta_nonnegative_count": sum(
                    int(row["_lower_delta_value"] >= 0) for row in rows
                ),
                "upper_delta_nonnegative_count": sum(
                    int(row["_upper_delta_value"] >= 0) for row in rows
                ),
                "lower_delta_zero_count": sum(
                    row["lower_delta_zero_flag"] for row in rows
                ),
                "upper_delta_zero_count": sum(
                    row["upper_delta_zero_flag"] for row in rows
                ),
                "transition_certificate_count": sum(
                    row["transition_certificate_flag"] for row in rows
                ),
                "lower_min_digits": digits(lower_min),
                "lower_min_mod_1000000007": lower_min % MOD_PRIMES[0],
                "lower_min_mod_1000000009": lower_min % MOD_PRIMES[1],
                "upper_min_digits": digits(upper_min),
                "upper_min_mod_1000000007": upper_min % MOD_PRIMES[0],
                "upper_min_mod_1000000009": upper_min % MOD_PRIMES[1],
                "type_certificate_flag": int(
                    sum(row["transition_certificate_flag"] for row in rows)
                    == len(rows)
                ),
            }
        )
    return summary_rows


def build_rows() -> dict[str, Any]:
    long_suppind = load_json(LONG_SUPPIND_REPORT)
    support_rows = load_support_rows()
    seed_rows = build_seed_rows(support_rows)
    transition_rows = build_transition_rows(support_rows)
    type_summary_rows = summarize_transition_types(transition_rows)
    support_csv_count = len(int_rows(read_csv_rows(LONG_SUPPIND_SUPPORT)))
    bridge_rows = [
        {
            "bridge_id": 0,
            "induction_start": INDUCTION_START,
            "source_end_sample_count": SOURCE_END,
            "seed_count": len(seed_rows),
            "transition_count": len(transition_rows),
            "transition_type_count": len(type_summary_rows),
            "seed_certificate_count": sum(
                row["seed_certificate_flag"] for row in seed_rows
            ),
            "transition_certificate_count": sum(
                row["transition_certificate_flag"] for row in transition_rows
            ),
            "long_suppind_certified_flag": int(
                long_suppind.get("status") == LONG_SUPPIND_STATUS
            ),
            "support_row_count_match_flag": int(support_csv_count == len(support_rows)),
        }
    ]
    obs = {
        "induction_start": INDUCTION_START,
        "source_end_sample_count": SOURCE_END,
        "recurrence_factor": RECURRENCE_FACTOR,
        "seed_count": len(seed_rows),
        "transition_count": len(transition_rows),
        "transition_type_count": len(type_summary_rows),
        "seed_certificate_count": bridge_rows[0]["seed_certificate_count"],
        "transition_certificate_count": bridge_rows[0][
            "transition_certificate_count"
        ],
        "lower_delta_nonnegative_count": sum(
            int(row["_lower_delta_value"] >= 0) for row in transition_rows
        ),
        "upper_delta_nonnegative_count": sum(
            int(row["_upper_delta_value"] >= 0) for row in transition_rows
        ),
        "lower_delta_zero_count": sum(
            row["lower_delta_zero_flag"] for row in transition_rows
        ),
        "upper_delta_zero_count": sum(
            row["upper_delta_zero_flag"] for row in transition_rows
        ),
        "type_certificate_count": sum(
            row["type_certificate_flag"] for row in type_summary_rows
        ),
        "support_state_count": len(support_rows),
        "long_suppind_support_state_count": int(
            long_suppind["witness"]["support"]["state_count"]
        ),
        "long_suppind_certified_flag": bridge_rows[0][
            "long_suppind_certified_flag"
        ],
        "support_row_count_match_flag": bridge_rows[0][
            "support_row_count_match_flag"
        ],
        "current_recurrence_graph_flag": int(
            bridge_rows[0]["seed_certificate_count"] == len(seed_rows)
            and bridge_rows[0]["transition_certificate_count"]
            == len(transition_rows)
            and sum(row["type_certificate_flag"] for row in type_summary_rows)
            == len(type_summary_rows)
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
    seed_hash = hashlib.sha256(
        digest_text(SEED_COLUMNS, seed_rows).encode("ascii")
    ).hexdigest()
    transition_hash = hashlib.sha256(
        digest_text(TRANSITION_COLUMNS, transition_rows).encode("ascii")
    ).hexdigest()
    type_summary_hash = hashlib.sha256(
        digest_text(TYPE_SUMMARY_COLUMNS, type_summary_rows).encode("ascii")
    ).hexdigest()
    bridge_hash = hashlib.sha256(
        digest_text(BRIDGE_COLUMNS, bridge_rows).encode("ascii")
    ).hexdigest()
    return {
        "input_reports": {"long_suppind": long_suppind},
        "seed_rows": seed_rows,
        "transition_rows": transition_rows,
        "type_summary_rows": type_summary_rows,
        "bridge_rows": bridge_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "seed_table": table_from_rows(SEED_COLUMNS, seed_rows),
        "transition_table": table_from_rows(TRANSITION_COLUMNS, transition_rows),
        "type_summary_table": table_from_rows(
            TYPE_SUMMARY_COLUMNS, type_summary_rows
        ),
        "bridge_table": table_from_rows(BRIDGE_COLUMNS, bridge_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "seed_hash": seed_hash,
        "transition_hash": transition_hash,
        "type_summary_hash": type_summary_hash,
        "bridge_hash": bridge_hash,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "input_certified": (
            obs["long_suppind_certified_flag"],
            obs["support_row_count_match_flag"],
        )
        == (1, 1),
        "seed_exact": (
            obs["seed_count"],
            obs["seed_certificate_count"],
            rows["seed_hash"],
        )
        == (33, 33, SEED_TEXT_HASH),
        "transition_exact": (
            obs["transition_count"],
            obs["transition_certificate_count"],
            obs["lower_delta_nonnegative_count"],
            obs["upper_delta_nonnegative_count"],
            obs["lower_delta_zero_count"],
            obs["upper_delta_zero_count"],
            rows["transition_hash"],
        )
        == (
            16_095,
            16_095,
            16_095,
            16_095,
            111,
            111,
            TRANSITION_TEXT_HASH,
        ),
        "type_summary_exact": (
            obs["transition_type_count"],
            obs["type_certificate_count"],
            rows["type_summary_hash"],
        )
        == (10, 10, TYPE_SUMMARY_TEXT_HASH),
        "bridge_exact": (
            obs["support_state_count"],
            obs["long_suppind_support_state_count"],
            obs["recurrence_factor"],
            rows["bridge_hash"],
        )
        == (16_128, 16_128, 12, BRIDGE_TEXT_HASH),
        "current_representation_exact": obs["current_recurrence_graph_flag"] == 1,
        "table_shapes_match": (
            tuple(rows["seed_table"].shape),
            tuple(rows["transition_table"].shape),
            tuple(rows["type_summary_table"].shape),
            tuple(rows["bridge_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (33, len(SEED_COLUMNS)),
            (16_095, len(TRANSITION_COLUMNS)),
            (10, len(TYPE_SUMMARY_COLUMNS)),
            (1, len(BRIDGE_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "finite_support_gap_recurrence_graph",
        "recurrence": {
            "induction_start": INDUCTION_START,
            "source_end_sample_count": SOURCE_END,
            "factor": RECURRENCE_FACTOR,
            "seed_count": obs["seed_count"],
            "transition_count": obs["transition_count"],
            "transition_type_count": obs["transition_type_count"],
            "lower_delta_nonnegative_count": obs["lower_delta_nonnegative_count"],
            "upper_delta_nonnegative_count": obs["upper_delta_nonnegative_count"],
            "seed_text_sha256": rows["seed_hash"],
            "transition_text_sha256": rows["transition_hash"],
            "type_summary_text_sha256": rows["type_summary_hash"],
            "seed_table_sha256": sha_array(rows["seed_table"]),
            "transition_table_sha256": sha_array(rows["transition_table"]),
            "type_summary_table_sha256": sha_array(rows["type_summary_table"]),
        },
        "bridge": {
            "long_suppind_certified": bool(obs["long_suppind_certified_flag"]),
            "support_row_count_match": bool(obs["support_row_count_match_flag"]),
            "bridge_text_sha256": rows["bridge_hash"],
            "bridge_table_sha256": sha_array(rows["bridge_table"]),
        },
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    recind_payload = {
        "schema": "long.recind@1",
        "object": "finite_support_gap_recurrence_graph",
        "status": STATUS if all(checks.values()) else "LONG_RECIND_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.recind.report@1",
        "status": recind_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_recind compresses the long_suppind support-gap table into a "
            "finite recurrence graph. The 33 n=16 seed states have nonnegative "
            "lower and upper gaps, and every later lifted state n=17..127 has "
            "a predecessor with lower_gap_new >= 12*lower_gap_old and "
            "upper_gap_new >= 12*upper_gap_old."
        ),
        "stage_protocol": {
            "draft": "read long_suppind support rows and exact gap values",
            "witness": "build seed states, recurrence predecessors, and transition-type summaries",
            "coherence": "check seed signs, recurrence deltas, type counts, input status, hashes, and shapes",
            "closure": "emit finite recurrence graph for lifted support-gap propagation",
            "emit": "write long_recind artifacts and verifier hook",
        },
        "inputs": {
            "long_suppind_report": input_entry(
                LONG_SUPPIND_REPORT,
                {"status": rows["input_reports"]["long_suppind"].get("status")},
            ),
            "long_suppind_support": input_entry(LONG_SUPPIND_SUPPORT),
            "long_suppind_rule_summary": input_entry(LONG_SUPPIND_RULE_SUMMARY),
            "long_suppind_tables": input_entry(LONG_SUPPIND_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "recind": relpath(OUT_DIR / "recind.json"),
            "seed_csv": relpath(OUT_DIR / "seed.csv"),
            "transition_csv": relpath(OUT_DIR / "transition.csv"),
            "type_summary_csv": relpath(OUT_DIR / "type_summary.csv"),
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
                "finite recurrence propagation of all long_suppind support gaps across n=16..127",
                "33 nonnegative seed states at n=16",
                "16,095 nonnegative recurrence transitions with factor 12",
                "10 recurrence transition types covering all lifted support states",
            ],
            "does_not_certify_because_out_of_scope": [
                "closed symbolic positivity of the recurrence deltas for every n >= 128",
                "the full trinomial component-word measure",
                "semantic C985 associator composition",
                "a complete infinite-horizon LLN theorem",
            ],
        },
        "next_highest_yield_item": (
            "Build long_formind: derive closed affine-exponent formulas for "
            "the 10 recurrence transition types and prove their deltas "
            "nonnegative for every n beyond the lifted cone."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.recind.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.recind.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "recind": recind_payload,
        "seed_csv": csv_text(SEED_COLUMNS, rows["seed_rows"]),
        "transition_csv": csv_text(TRANSITION_COLUMNS, rows["transition_rows"]),
        "type_summary_csv": csv_text(
            TYPE_SUMMARY_COLUMNS, rows["type_summary_rows"]
        ),
        "bridge_csv": csv_text(BRIDGE_COLUMNS, rows["bridge_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "seed_table": rows["seed_table"],
        "transition_table": rows["transition_table"],
        "type_summary_table": rows["type_summary_table"],
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
    write_json(OUT_DIR / "recind.json", payloads["recind"])
    (OUT_DIR / "seed.csv").write_text(payloads["seed_csv"], encoding="utf-8")
    (OUT_DIR / "transition.csv").write_text(
        payloads["transition_csv"], encoding="utf-8"
    )
    (OUT_DIR / "type_summary.csv").write_text(
        payloads["type_summary_csv"], encoding="utf-8"
    )
    (OUT_DIR / "bridge.csv").write_text(payloads["bridge_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        seed_table=payloads["seed_table"],
        transition_table=payloads["transition_table"],
        type_summary_table=payloads["type_summary_table"],
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
