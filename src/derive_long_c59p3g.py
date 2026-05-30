from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
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
    from .derive_long_raw import csv_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_raw import csv_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_c59p3g"
STATUS = "LONG_C59P3G_OPERATION_SCHEMA_GAP_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_C59P3M = PROOF_ROOT / "long_c59p3m" / "report.json"
LONG_C59P3M_JOIN = PROOF_ROOT / "long_c59p3m" / "join.csv"
LONG_TRANSITION_SEM = PROOF_ROOT / "long_transition_sem" / "report.json"
LONG_TRANSITION_CSV = PROOF_ROOT / "long_transition_sem" / "transition.csv"
LONG_TRANSITION_SCHEMA_GAP = PROOF_ROOT / "long_transition_sem" / "schema_gap.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_c59p3g.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_c59p3g.py"

JOIN_SCHEMA_COLUMNS = [
    "join_id",
    "carrier_id",
    "relation_id",
    "transition_id",
    "contact_lift_flag",
    "endpoint_pair_raw_row_flag",
    "normal_form_delta_t",
    "operation_row_id",
    "operation_source0_addr",
    "operation_source1_addr",
    "operation_target_addr",
    "operation_coeff",
    "operation_time_component",
    "semantic_transition_flag",
    "operation_sentinel_flag",
    "transition_ready_flag",
    "operation_backed_flag",
    "blocking_schema_gap_code",
]
TRANSITION_SCHEMA_COLUMNS = [
    "active_transition_id",
    "transition_id",
    "active_relation_count",
    "active_join_count",
    "contact_lift_flag",
    "endpoint_pair_raw_row_flag",
    "normal_form_delta_t",
    "operation_row_id",
    "operation_sentinel_flag",
    "semantic_transition_flag",
    "transition_ready_flag",
    "operation_backed_flag",
]
SCHEMA_GAP_COLUMNS = [
    "schema_gap_id",
    "evidence_code",
    "source_present_flag",
    "required_for_semantic_flag",
    "source_row_count",
    "source_obstruction_flag",
    "active_join_impacted_count",
    "active_transition_impacted_count",
    "blocks_operation_backing_flag",
]
GAP_COLUMNS = [
    "gap_id",
    "gap_code",
    "certified_flag",
    "open_flag",
    "obstruction_flag",
    "next_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

SCHEMA_EVIDENCE_NAMES = [
    "raw_endpoint_row_ids_present",
    "contact_lift_rows_present",
    "normal_form_time_rows_present",
    "semantic_operation_rows_absent",
    "transition_composition_law_absent",
]
SCHEMA_EVIDENCE_CODES = {
    name: index for index, name in enumerate(SCHEMA_EVIDENCE_NAMES)
}

GAP_NAMES = [
    "normalized_join_certified",
    "active_transition_schema_present",
    "operation_columns_all_sentinel",
    "semantic_transition_flags_absent",
    "transition_composition_law_absent",
    "operation_backed_normalized_counterterm",
    "physical_selector_axiom",
    "metric_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "join_row_count",
    "active_relation_count",
    "active_transition_count",
    "contact_lift_join_count",
    "endpoint_pair_raw_row_join_count",
    "unit_time_join_count",
    "operation_row_sentinel_join_count",
    "operation_addr_sentinel_join_count",
    "operation_coeff_zero_join_count",
    "operation_time_component_zero_join_count",
    "semantic_transition_zero_join_count",
    "transition_ready_join_count",
    "operation_backed_join_count",
    "schema_gap_operation_rows_absent_flag",
    "schema_gap_composition_law_absent_flag",
    "operation_schema_gap_flag",
    "physical_selector_axiom_flag",
    "metric_derivation_flag",
    "next_gap_code",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def certified(report: dict[str, Any]) -> bool:
    return report.get("all_checks_pass") is True and (
        "CERTIFIED" in str(report.get("status", ""))
        or "OBSTRUCTION_CERTIFIED" in str(report.get("status", ""))
    )


def operation_sentinel(transition: dict[str, str]) -> bool:
    return (
        int(transition["operation_row_id"]) == -1
        and int(transition["operation_source0_addr"]) == -1
        and int(transition["operation_source1_addr"]) == -1
        and int(transition["operation_target_addr"]) == -1
        and int(transition["operation_coeff"]) == 0
        and int(transition["operation_time_component"]) == 0
        and int(transition["semantic_transition_flag"]) == 0
    )


def transition_ready(transition: dict[str, str]) -> bool:
    return (
        int(transition["contact_lift_flag"]) == 1
        and int(transition["endpoint_pair_raw_row_flag"]) == 1
        and int(transition["normal_form_delta_t"]) == 1
    )


def build_rows() -> dict[str, Any]:
    c59p3m = load_json(LONG_C59P3M)
    transition_sem = load_json(LONG_TRANSITION_SEM)
    _, join_raw = read_csv_rows(LONG_C59P3M_JOIN)
    _, transition_raw = read_csv_rows(LONG_TRANSITION_CSV)
    _, source_schema_gap_rows = read_csv_rows(LONG_TRANSITION_SCHEMA_GAP)

    transition_by_id = {
        int(row["transition_id"]): row for row in transition_raw
    }
    active_relations = {int(row["relation_id"]) for row in join_raw}
    joins_by_transition: dict[int, list[dict[str, str]]] = defaultdict(list)
    relations_by_transition: dict[int, set[int]] = defaultdict(set)
    join_schema_rows = []
    for row in join_raw:
        transition_id = int(row["transition_id"])
        transition = transition_by_id[transition_id]
        ready_flag = int(transition_ready(transition))
        sentinel_flag = int(operation_sentinel(transition))
        operation_backed_flag = int(
            ready_flag == 1
            and sentinel_flag == 0
            and int(transition["semantic_transition_flag"]) == 1
        )
        joins_by_transition[transition_id].append(row)
        relations_by_transition[transition_id].add(int(row["relation_id"]))
        join_schema_rows.append(
            {
                "join_id": int(row["join_id"]),
                "carrier_id": int(row["carrier_id"]),
                "relation_id": int(row["relation_id"]),
                "transition_id": transition_id,
                "contact_lift_flag": int(transition["contact_lift_flag"]),
                "endpoint_pair_raw_row_flag": int(
                    transition["endpoint_pair_raw_row_flag"]
                ),
                "normal_form_delta_t": int(transition["normal_form_delta_t"]),
                "operation_row_id": int(transition["operation_row_id"]),
                "operation_source0_addr": int(transition["operation_source0_addr"]),
                "operation_source1_addr": int(transition["operation_source1_addr"]),
                "operation_target_addr": int(transition["operation_target_addr"]),
                "operation_coeff": int(transition["operation_coeff"]),
                "operation_time_component": int(
                    transition["operation_time_component"]
                ),
                "semantic_transition_flag": int(
                    transition["semantic_transition_flag"]
                ),
                "operation_sentinel_flag": sentinel_flag,
                "transition_ready_flag": ready_flag,
                "operation_backed_flag": operation_backed_flag,
                "blocking_schema_gap_code": SCHEMA_EVIDENCE_CODES[
                    "semantic_operation_rows_absent"
                ],
            }
        )

    transition_schema_rows = []
    for active_transition_id, transition_id in enumerate(sorted(joins_by_transition)):
        transition = transition_by_id[transition_id]
        ready_flag = int(transition_ready(transition))
        sentinel_flag = int(operation_sentinel(transition))
        transition_schema_rows.append(
            {
                "active_transition_id": active_transition_id,
                "transition_id": transition_id,
                "active_relation_count": len(relations_by_transition[transition_id]),
                "active_join_count": len(joins_by_transition[transition_id]),
                "contact_lift_flag": int(transition["contact_lift_flag"]),
                "endpoint_pair_raw_row_flag": int(
                    transition["endpoint_pair_raw_row_flag"]
                ),
                "normal_form_delta_t": int(transition["normal_form_delta_t"]),
                "operation_row_id": int(transition["operation_row_id"]),
                "operation_sentinel_flag": sentinel_flag,
                "semantic_transition_flag": int(
                    transition["semantic_transition_flag"]
                ),
                "transition_ready_flag": ready_flag,
                "operation_backed_flag": int(
                    ready_flag == 1
                    and sentinel_flag == 0
                    and int(transition["semantic_transition_flag"]) == 1
                ),
            }
        )

    active_transition_count = len(transition_schema_rows)
    schema_gap_rows = []
    for row in source_schema_gap_rows:
        evidence_code = int(row["evidence_code"])
        blocks = int(
            evidence_code
            in {
                SCHEMA_EVIDENCE_CODES["semantic_operation_rows_absent"],
                SCHEMA_EVIDENCE_CODES["transition_composition_law_absent"],
            }
        )
        impacted_join_count = len(join_schema_rows) if blocks else 0
        impacted_transition_count = active_transition_count if blocks else 0
        schema_gap_rows.append(
            {
                "schema_gap_id": int(row["gap_id"]),
                "evidence_code": evidence_code,
                "source_present_flag": int(row["present_flag"]),
                "required_for_semantic_flag": int(
                    row["required_for_semantic_flag"]
                ),
                "source_row_count": int(row["row_count"]),
                "source_obstruction_flag": int(row["obstruction_flag"]),
                "active_join_impacted_count": impacted_join_count,
                "active_transition_impacted_count": impacted_transition_count,
                "blocks_operation_backing_flag": blocks,
            }
        )

    operation_addr_sentinel_count = sum(
        int(
            row["operation_source0_addr"] == -1
            and row["operation_source1_addr"] == -1
            and row["operation_target_addr"] == -1
        )
        for row in join_schema_rows
    )
    obs = {
        "input_report_count": 2,
        "input_certified_count": sum(
            int(certified(report)) for report in (c59p3m, transition_sem)
        ),
        "join_row_count": len(join_schema_rows),
        "active_relation_count": len(active_relations),
        "active_transition_count": active_transition_count,
        "contact_lift_join_count": sum(
            row["contact_lift_flag"] for row in join_schema_rows
        ),
        "endpoint_pair_raw_row_join_count": sum(
            row["endpoint_pair_raw_row_flag"] for row in join_schema_rows
        ),
        "unit_time_join_count": sum(row["normal_form_delta_t"] for row in join_schema_rows),
        "operation_row_sentinel_join_count": sum(
            int(row["operation_row_id"] == -1) for row in join_schema_rows
        ),
        "operation_addr_sentinel_join_count": operation_addr_sentinel_count,
        "operation_coeff_zero_join_count": sum(
            int(row["operation_coeff"] == 0) for row in join_schema_rows
        ),
        "operation_time_component_zero_join_count": sum(
            int(row["operation_time_component"] == 0) for row in join_schema_rows
        ),
        "semantic_transition_zero_join_count": sum(
            int(row["semantic_transition_flag"] == 0) for row in join_schema_rows
        ),
        "transition_ready_join_count": sum(
            row["transition_ready_flag"] for row in join_schema_rows
        ),
        "operation_backed_join_count": sum(
            row["operation_backed_flag"] for row in join_schema_rows
        ),
        "schema_gap_operation_rows_absent_flag": next(
            row["source_obstruction_flag"]
            for row in schema_gap_rows
            if row["evidence_code"]
            == SCHEMA_EVIDENCE_CODES["semantic_operation_rows_absent"]
        ),
        "schema_gap_composition_law_absent_flag": next(
            row["source_obstruction_flag"]
            for row in schema_gap_rows
            if row["evidence_code"]
            == SCHEMA_EVIDENCE_CODES["transition_composition_law_absent"]
        ),
        "operation_schema_gap_flag": 1,
        "physical_selector_axiom_flag": 0,
        "metric_derivation_flag": 0,
        "next_gap_code": GAP_CODES["operation_backed_normalized_counterterm"],
    }
    gap_rows = [
        {
            "gap_id": GAP_CODES["normalized_join_certified"],
            "gap_code": GAP_CODES["normalized_join_certified"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["active_transition_schema_present"],
            "gap_code": GAP_CODES["active_transition_schema_present"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["operation_columns_all_sentinel"],
            "gap_code": GAP_CODES["operation_columns_all_sentinel"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["semantic_transition_flags_absent"],
            "gap_code": GAP_CODES["semantic_transition_flags_absent"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["transition_composition_law_absent"],
            "gap_code": GAP_CODES["transition_composition_law_absent"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["operation_backed_normalized_counterterm"],
            "gap_code": GAP_CODES["operation_backed_normalized_counterterm"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 1,
        },
        {
            "gap_id": GAP_CODES["physical_selector_axiom"],
            "gap_code": GAP_CODES["physical_selector_axiom"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["metric_derivation"],
            "gap_code": GAP_CODES["metric_derivation"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
    ]
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": obs[name],
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    return {
        "c59p3m": c59p3m,
        "transition_sem": transition_sem,
        "join_schema_rows": join_schema_rows,
        "transition_schema_rows": transition_schema_rows,
        "schema_gap_rows": schema_gap_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    join_schema_table = table_from_rows(
        JOIN_SCHEMA_COLUMNS, rows["join_schema_rows"]
    )
    transition_schema_table = table_from_rows(
        TRANSITION_SCHEMA_COLUMNS, rows["transition_schema_rows"]
    )
    schema_gap_table = table_from_rows(SCHEMA_GAP_COLUMNS, rows["schema_gap_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "active_transition_schema_total": obs["join_row_count"] == 229
        and obs["active_relation_count"] == 49
        and obs["active_transition_count"] == 29,
        "active_transitions_ready": obs["contact_lift_join_count"] == 229
        and obs["endpoint_pair_raw_row_join_count"] == 229
        and obs["unit_time_join_count"] == 229
        and obs["transition_ready_join_count"] == 229,
        "operation_columns_are_sentinel": obs[
            "operation_row_sentinel_join_count"
        ]
        == 229
        and obs["operation_addr_sentinel_join_count"] == 229
        and obs["operation_coeff_zero_join_count"] == 229
        and obs["operation_time_component_zero_join_count"] == 229,
        "semantic_flags_absent": obs["semantic_transition_zero_join_count"] == 229
        and obs["operation_backed_join_count"] == 0,
        "schema_gap_rows_explain_obstruction": obs[
            "schema_gap_operation_rows_absent_flag"
        ]
        == 1
        and obs["schema_gap_composition_law_absent_flag"] == 1
        and obs["operation_schema_gap_flag"] == 1,
        "physical_boundaries_preserved": obs["physical_selector_axiom_flag"] == 0
        and obs["metric_derivation_flag"] == 0,
        "table_shapes_match": join_schema_table.shape
        == (229, len(JOIN_SCHEMA_COLUMNS))
        and transition_schema_table.shape == (29, len(TRANSITION_SCHEMA_COLUMNS))
        and schema_gap_table.shape == (5, len(SCHEMA_GAP_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "operation_schema_gap",
        "summary": {
            "join_row_count": obs["join_row_count"],
            "active_relation_count": obs["active_relation_count"],
            "active_transition_count": obs["active_transition_count"],
            "transition_ready_join_count": obs["transition_ready_join_count"],
            "operation_row_sentinel_join_count": obs[
                "operation_row_sentinel_join_count"
            ],
            "operation_addr_sentinel_join_count": obs[
                "operation_addr_sentinel_join_count"
            ],
            "semantic_transition_zero_join_count": obs[
                "semantic_transition_zero_join_count"
            ],
            "operation_backed_join_count": obs["operation_backed_join_count"],
            "schema_gap_operation_rows_absent_flag": obs[
                "schema_gap_operation_rows_absent_flag"
            ],
            "schema_gap_composition_law_absent_flag": obs[
                "schema_gap_composition_law_absent_flag"
            ],
        },
        "schema_evidence_code_map": {
            str(value): key for key, value in SCHEMA_EVIDENCE_CODES.items()
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "join_schema_table_sha256": sha_array(join_schema_table),
        "join_schema_text_sha256": sha_text(
            csv_text(JOIN_SCHEMA_COLUMNS, rows["join_schema_rows"])
        ),
        "transition_schema_table_sha256": sha_array(transition_schema_table),
        "schema_gap_table_sha256": sha_array(schema_gap_table),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    c59p3g = {
        "schema": "long.c59p3g@1",
        "object": "operation_schema_gap",
        "status": STATUS if all(checks.values()) else "LONG_C59P3G_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.c59p3g.report@1",
        "status": c59p3g["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_c59p3g certifies the schema-level reason the 49 active "
            "normalized promotion witnesses from long_c59p3m do not become "
            "operation-backed rows. Their 229 joined rows touch 29 transition "
            "ids that are contact-backed, endpoint-backed, and unit-time-backed, "
            "but every joined row has operation sentinel fields and no semantic "
            "transition flag. The transition schema-gap table records semantic "
            "operation rows and the transition composition law as absent."
        ),
        "stage_protocol": {
            "draft": "read long_c59p3m joins, long_transition_sem transition rows, and schema-gap rows",
            "witness": "emit per-join schema rows, per-active-transition rows, schema-gap rows, gaps, and observables",
            "coherence": "check active transition coverage, ready transition evidence, operation sentinel fields, absent semantic flags, and preserved physical gaps",
            "closure": "certify the operation-schema gap after normalized promotion routing",
            "emit": "write long_c59p3g artifacts and verifier hook",
        },
        "inputs": {
            "long_c59p3m": input_entry(
                LONG_C59P3M,
                {
                    "status": rows["c59p3m"].get("status"),
                    "certificate_sha256": rows["c59p3m"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_c59p3m_join": input_entry(LONG_C59P3M_JOIN),
            "long_transition_sem": input_entry(
                LONG_TRANSITION_SEM,
                {
                    "status": rows["transition_sem"].get("status"),
                    "certificate_sha256": rows["transition_sem"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_transition_csv": input_entry(LONG_TRANSITION_CSV),
            "long_transition_schema_gap": input_entry(LONG_TRANSITION_SCHEMA_GAP),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "c59p3g": relpath(OUT_DIR / "c59p3g.json"),
            "join_schema_csv": relpath(OUT_DIR / "join_schema.csv"),
            "transition_schema_csv": relpath(OUT_DIR / "transition_schema.csv"),
            "schema_gap_csv": relpath(OUT_DIR / "schema_gap.csv"),
            "gap_csv": relpath(OUT_DIR / "gap.csv"),
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
                "the 229 normalized promotion joins touch 49 relation witnesses and 29 transition ids",
                "all 229 joined transition rows are contact-backed, raw-endpoint-backed, and unit-time-backed",
                "all 229 joined rows have operation row id -1 and operation address sentinels",
                "all 229 joined rows have zero operation coefficient, zero operation time component, and semantic_transition_flag=0",
                "the upstream schema-gap table marks semantic operation rows and the transition composition law absent",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "operation-backed normalized counterterm rows",
                "a transition composition law",
                "new semantic operation rows",
                "a physical selector axiom",
                "a four-dimensional metric reduction",
                "a physical field equation",
            ],
        },
        "next_highest_yield_item": (
            "Construct the missing transition composition law from raw endpoint "
            "pairs to operation rows, or certify that the current A985 operation "
            "schema has no admissible address map for the 29 active transition ids."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.c59p3g.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.c59p3g.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "c59p3g": c59p3g,
        "join_schema_csv": csv_text(
            JOIN_SCHEMA_COLUMNS, rows["join_schema_rows"]
        ),
        "transition_schema_csv": csv_text(
            TRANSITION_SCHEMA_COLUMNS, rows["transition_schema_rows"]
        ),
        "schema_gap_csv": csv_text(SCHEMA_GAP_COLUMNS, rows["schema_gap_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "join_schema_table": join_schema_table,
        "transition_schema_table": transition_schema_table,
        "schema_gap_table": schema_gap_table,
        "gap_table": gap_table,
        "observable_table": observable_table,
        "cert": cert,
        "manifest": manifest,
        "report": report,
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
    write_json(OUT_DIR / "c59p3g.json", payloads["c59p3g"])
    (OUT_DIR / "join_schema.csv").write_text(
        payloads["join_schema_csv"], encoding="utf-8"
    )
    (OUT_DIR / "transition_schema.csv").write_text(
        payloads["transition_schema_csv"], encoding="utf-8"
    )
    (OUT_DIR / "schema_gap.csv").write_text(
        payloads["schema_gap_csv"], encoding="utf-8"
    )
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        join_schema_table=payloads["join_schema_table"],
        transition_schema_table=payloads["transition_schema_table"],
        schema_gap_table=payloads["schema_gap_table"],
        gap_table=payloads["gap_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(OUT_DIR / "cert.json", payloads["cert"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    write_json(OUT_DIR / "report.json", payloads["report"])
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
                "summary": report["witness"]["summary"],
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
