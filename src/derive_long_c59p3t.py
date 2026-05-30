from __future__ import annotations

import csv
import hashlib
import json
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


THEOREM_ID = "long_c59p3t"
STATUS = "LONG_C59P3T_TRANSITION_STRESS_LIFT_GATE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_C59P3A = PROOF_ROOT / "long_c59p3a" / "report.json"
LONG_C59P3A_OVERLAP = PROOF_ROOT / "long_c59p3a" / "overlap.csv"
LONG_TRANSITION_SEM = PROOF_ROOT / "long_transition_sem" / "report.json"
LONG_TRANSITION_CSV = PROOF_ROOT / "long_transition_sem" / "transition.csv"
LONG_CONTACT_LIFT = PROOF_ROOT / "long_contact_lift" / "report.json"
LONG_CONTACT_CSV = PROOF_ROOT / "long_contact_lift" / "contact.csv"
LONG_ENDPOINT_CSV = PROOF_ROOT / "long_contact_lift" / "endpoint.csv"
LONG_STRESS_GATE = PROOF_ROOT / "long_stress_gate" / "report.json"
LONG_STRESS_EDGE = PROOF_ROOT / "long_stress_gate" / "stress_edge.csv"
LONG_STRESS_COUPLE = PROOF_ROOT / "long_stress_couple" / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_c59p3t.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_c59p3t.py"

SURFACE_COLUMNS = [
    "surface_id",
    "surface_code",
    "row_count",
    "column_count",
    "has_transition_id",
    "has_edge_id",
    "has_basis_key",
    "has_raw_key",
    "has_stress_edge_id",
    "has_source_atom",
    "has_target_atom",
    "has_selector_id",
]
JOIN_COLUMNS = [
    "join_id",
    "join_code",
    "left_surface_code",
    "right_surface_code",
    "shared_key_count",
    "candidate_row_count",
    "certified_flag",
    "obstruction_flag",
]
DECISION_COLUMNS = [
    "decision_id",
    "decision_code",
    "value",
    "certified_flag",
    "obstruction_flag",
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

SURFACE_NAMES = [
    "atom_overlap_orientation_score",
    "guarded_transition_surface",
    "contact_lift_surface",
    "endpoint_raw_surface",
    "stress_edge_surface",
]
SURFACE_CODES = {name: index for index, name in enumerate(SURFACE_NAMES)}
JOIN_NAMES = [
    "overlap_to_stress_edge",
    "transition_to_contact",
    "contact_to_endpoint",
    "transition_to_stress_edge",
    "transition_to_overlap_score",
    "contact_to_overlap_score",
    "endpoint_to_overlap_score",
]
JOIN_CODES = {name: index for index, name in enumerate(JOIN_NAMES)}
DECISION_NAMES = [
    "atom_overlap_orientation_candidate_available",
    "overlap_stress_join_available",
    "transition_contact_join_available",
    "transition_atom_key_available",
    "transition_stress_key_available",
    "atom_transition_bridge_available",
    "transition_stress_map_available",
    "semantic_transition_operation_available",
]
DECISION_CODES = {name: index for index, name in enumerate(DECISION_NAMES)}
GAP_NAMES = [
    "atom_overlap_orientation_candidate",
    "transition_atom_key_bridge",
    "transition_to_stress_coupling_map",
    "semantic_transition_operation",
    "physical_selector_axiom",
    "four_dimensional_metric_reduction",
    "thermal_gravity_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}
OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "overlap_row_count",
    "transition_row_count",
    "contact_row_count",
    "endpoint_row_count",
    "stress_edge_row_count",
    "overlap_stress_shared_key_count",
    "transition_contact_shared_key_count",
    "contact_endpoint_bridge_flag",
    "transition_stress_shared_key_count",
    "transition_overlap_shared_key_count",
    "contact_overlap_shared_key_count",
    "endpoint_overlap_shared_key_count",
    "transition_atom_column_count",
    "transition_stress_edge_column_count",
    "contact_atom_column_count",
    "endpoint_atom_column_count",
    "atom_overlap_orientation_candidate_flag",
    "atom_transition_bridge_flag",
    "transition_stress_map_certified_flag",
    "semantic_transition_operation_flag",
    "current_schema_consumes_atom_score_flag",
    "physical_selector_axiom_flag",
    "four_dimensional_metric_flag",
    "thermal_gravity_flag",
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


def summary(report: dict[str, Any]) -> dict[str, Any]:
    witness = report.get("witness", {})
    value = witness.get("summary", {})
    if not isinstance(value, dict):
        raise AssertionError("report witness summary is not an object")
    return value


def has_any(columns: list[str], names: set[str]) -> int:
    return int(any(column in names for column in columns))


def surface_row(
    surface_code: int,
    columns: list[str],
    row_count: int,
) -> dict[str, int]:
    column_set = set(columns)
    return {
        "surface_id": surface_code,
        "surface_code": surface_code,
        "row_count": row_count,
        "column_count": len(columns),
        "has_transition_id": int("transition_id" in column_set),
        "has_edge_id": int("edge_id" in column_set),
        "has_basis_key": has_any(column_set, {"basis_id", "left_basis_id", "right_basis_id"}),
        "has_raw_key": has_any(
            column_set,
            {
                "raw_row_id",
                "left_raw_row_id",
                "right_raw_row_id",
                "source0_addr",
                "source1_addr",
                "target_addr",
            },
        ),
        "has_stress_edge_id": int("stress_edge_id" in column_set),
        "has_source_atom": int("source_atom" in column_set),
        "has_target_atom": int("target_atom" in column_set),
        "has_selector_id": int("selector_id" in column_set),
    }


def shared_count(left: list[str], right: list[str], keys: set[str] | None = None) -> int:
    if keys is None:
        return len(set(left) & set(right))
    return len((set(left) & set(right)) & keys)


def build_rows() -> dict[str, Any]:
    c59p3a = load_json(LONG_C59P3A)
    transition_sem = load_json(LONG_TRANSITION_SEM)
    contact_lift = load_json(LONG_CONTACT_LIFT)
    stress_gate = load_json(LONG_STRESS_GATE)
    stress_couple = load_json(LONG_STRESS_COUPLE)

    overlap_columns, overlap_rows_raw = read_csv_rows(LONG_C59P3A_OVERLAP)
    transition_columns, transition_rows_raw = read_csv_rows(LONG_TRANSITION_CSV)
    contact_columns, contact_rows_raw = read_csv_rows(LONG_CONTACT_CSV)
    endpoint_columns, endpoint_rows_raw = read_csv_rows(LONG_ENDPOINT_CSV)
    stress_columns, stress_rows_raw = read_csv_rows(LONG_STRESS_EDGE)

    surface_rows = [
        surface_row(
            SURFACE_CODES["atom_overlap_orientation_score"],
            overlap_columns,
            len(overlap_rows_raw),
        ),
        surface_row(
            SURFACE_CODES["guarded_transition_surface"],
            transition_columns,
            len(transition_rows_raw),
        ),
        surface_row(
            SURFACE_CODES["contact_lift_surface"],
            contact_columns,
            len(contact_rows_raw),
        ),
        surface_row(
            SURFACE_CODES["endpoint_raw_surface"],
            endpoint_columns,
            len(endpoint_rows_raw),
        ),
        surface_row(
            SURFACE_CODES["stress_edge_surface"],
            stress_columns,
            len(stress_rows_raw),
        ),
    ]

    stress_key_columns = {
        "stress_edge_id",
        "source_atom",
        "target_atom",
        "weight_scaled",
        "signed_tension_scaled",
    }
    transition_contact_keys = {
        "edge_id",
        "left_basis_id",
        "right_basis_id",
        "source0_boundary_count",
        "source1_boundary_count",
        "boundary_count",
        "contact_lift_flag",
    }
    overlap_stress_shared = shared_count(overlap_columns, stress_columns, stress_key_columns)
    transition_contact_shared = shared_count(
        transition_columns, contact_columns, transition_contact_keys
    )
    transition_stress_shared = shared_count(
        transition_columns, stress_columns, {"stress_edge_id", "source_atom", "target_atom"}
    )
    transition_overlap_shared = shared_count(
        transition_columns, overlap_columns, {"stress_edge_id", "source_atom", "target_atom", "selector_id"}
    )
    contact_overlap_shared = shared_count(
        contact_columns, overlap_columns, {"stress_edge_id", "source_atom", "target_atom", "selector_id"}
    )
    endpoint_overlap_shared = shared_count(
        endpoint_columns, overlap_columns, {"stress_edge_id", "source_atom", "target_atom", "selector_id"}
    )
    contact_endpoint_bridge_flag = int(
        "left_basis_id" in contact_columns
        and "right_basis_id" in contact_columns
        and "basis_id" in endpoint_columns
    )

    join_rows = [
        {
            "join_id": JOIN_CODES["overlap_to_stress_edge"],
            "join_code": JOIN_CODES["overlap_to_stress_edge"],
            "left_surface_code": SURFACE_CODES["atom_overlap_orientation_score"],
            "right_surface_code": SURFACE_CODES["stress_edge_surface"],
            "shared_key_count": overlap_stress_shared,
            "candidate_row_count": len(overlap_rows_raw),
            "certified_flag": 1,
            "obstruction_flag": 0,
        },
        {
            "join_id": JOIN_CODES["transition_to_contact"],
            "join_code": JOIN_CODES["transition_to_contact"],
            "left_surface_code": SURFACE_CODES["guarded_transition_surface"],
            "right_surface_code": SURFACE_CODES["contact_lift_surface"],
            "shared_key_count": transition_contact_shared,
            "candidate_row_count": len(transition_rows_raw),
            "certified_flag": 1,
            "obstruction_flag": 0,
        },
        {
            "join_id": JOIN_CODES["contact_to_endpoint"],
            "join_code": JOIN_CODES["contact_to_endpoint"],
            "left_surface_code": SURFACE_CODES["contact_lift_surface"],
            "right_surface_code": SURFACE_CODES["endpoint_raw_surface"],
            "shared_key_count": int(contact_endpoint_bridge_flag),
            "candidate_row_count": len(endpoint_rows_raw),
            "certified_flag": contact_endpoint_bridge_flag,
            "obstruction_flag": 0,
        },
        {
            "join_id": JOIN_CODES["transition_to_stress_edge"],
            "join_code": JOIN_CODES["transition_to_stress_edge"],
            "left_surface_code": SURFACE_CODES["guarded_transition_surface"],
            "right_surface_code": SURFACE_CODES["stress_edge_surface"],
            "shared_key_count": transition_stress_shared,
            "candidate_row_count": 0,
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "join_id": JOIN_CODES["transition_to_overlap_score"],
            "join_code": JOIN_CODES["transition_to_overlap_score"],
            "left_surface_code": SURFACE_CODES["guarded_transition_surface"],
            "right_surface_code": SURFACE_CODES["atom_overlap_orientation_score"],
            "shared_key_count": transition_overlap_shared,
            "candidate_row_count": 0,
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "join_id": JOIN_CODES["contact_to_overlap_score"],
            "join_code": JOIN_CODES["contact_to_overlap_score"],
            "left_surface_code": SURFACE_CODES["contact_lift_surface"],
            "right_surface_code": SURFACE_CODES["atom_overlap_orientation_score"],
            "shared_key_count": contact_overlap_shared,
            "candidate_row_count": 0,
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "join_id": JOIN_CODES["endpoint_to_overlap_score"],
            "join_code": JOIN_CODES["endpoint_to_overlap_score"],
            "left_surface_code": SURFACE_CODES["endpoint_raw_surface"],
            "right_surface_code": SURFACE_CODES["atom_overlap_orientation_score"],
            "shared_key_count": endpoint_overlap_shared,
            "candidate_row_count": 0,
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
    ]

    c59p3a_summary = summary(c59p3a)
    transition_summary = summary(transition_sem)
    stress_summary = summary(stress_couple)
    transition_atom_column_count = int("source_atom" in transition_columns) + int(
        "target_atom" in transition_columns
    )
    contact_atom_column_count = int("source_atom" in contact_columns) + int(
        "target_atom" in contact_columns
    )
    endpoint_atom_column_count = int("source_atom" in endpoint_columns) + int(
        "target_atom" in endpoint_columns
    )
    transition_stress_edge_column_count = int("stress_edge_id" in transition_columns)
    atom_transition_bridge_flag = int(
        transition_overlap_shared > 0
        or contact_overlap_shared > 0
        or endpoint_overlap_shared > 0
    )
    transition_stress_map_flag = int(stress_summary["coupling_map_certified_flag"])
    semantic_transition_flag = int(
        transition_summary["semantic_transition_operation_flag"]
    )
    current_schema_consumes_atom_score_flag = int(
        atom_transition_bridge_flag == 1 and transition_stress_map_flag == 1
    )
    obs = {
        "input_report_count": 5,
        "input_certified_count": int(certified(c59p3a))
        + int(certified(transition_sem))
        + int(certified(contact_lift))
        + int(certified(stress_gate))
        + int(certified(stress_couple)),
        "overlap_row_count": len(overlap_rows_raw),
        "transition_row_count": len(transition_rows_raw),
        "contact_row_count": len(contact_rows_raw),
        "endpoint_row_count": len(endpoint_rows_raw),
        "stress_edge_row_count": len(stress_rows_raw),
        "overlap_stress_shared_key_count": overlap_stress_shared,
        "transition_contact_shared_key_count": transition_contact_shared,
        "contact_endpoint_bridge_flag": contact_endpoint_bridge_flag,
        "transition_stress_shared_key_count": transition_stress_shared,
        "transition_overlap_shared_key_count": transition_overlap_shared,
        "contact_overlap_shared_key_count": contact_overlap_shared,
        "endpoint_overlap_shared_key_count": endpoint_overlap_shared,
        "transition_atom_column_count": transition_atom_column_count,
        "transition_stress_edge_column_count": transition_stress_edge_column_count,
        "contact_atom_column_count": contact_atom_column_count,
        "endpoint_atom_column_count": endpoint_atom_column_count,
        "atom_overlap_orientation_candidate_flag": int(
            c59p3a_summary["atom_overlap_orientation_candidate_flag"]
        ),
        "atom_transition_bridge_flag": atom_transition_bridge_flag,
        "transition_stress_map_certified_flag": transition_stress_map_flag,
        "semantic_transition_operation_flag": semantic_transition_flag,
        "current_schema_consumes_atom_score_flag": current_schema_consumes_atom_score_flag,
        "physical_selector_axiom_flag": int(c59p3a_summary["physical_selector_axiom_flag"]),
        "four_dimensional_metric_flag": 0,
        "thermal_gravity_flag": 0,
        "next_gap_code": GAP_CODES["transition_atom_key_bridge"],
    }
    decision_rows = [
        {
            "decision_id": DECISION_CODES[
                "atom_overlap_orientation_candidate_available"
            ],
            "decision_code": DECISION_CODES[
                "atom_overlap_orientation_candidate_available"
            ],
            "value": obs["atom_overlap_orientation_candidate_flag"],
            "certified_flag": obs["atom_overlap_orientation_candidate_flag"],
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES["overlap_stress_join_available"],
            "decision_code": DECISION_CODES["overlap_stress_join_available"],
            "value": obs["overlap_stress_shared_key_count"],
            "certified_flag": 1,
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES["transition_contact_join_available"],
            "decision_code": DECISION_CODES["transition_contact_join_available"],
            "value": obs["transition_contact_shared_key_count"],
            "certified_flag": 1,
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES["transition_atom_key_available"],
            "decision_code": DECISION_CODES["transition_atom_key_available"],
            "value": obs["transition_atom_column_count"],
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "decision_id": DECISION_CODES["transition_stress_key_available"],
            "decision_code": DECISION_CODES["transition_stress_key_available"],
            "value": obs["transition_stress_edge_column_count"],
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "decision_id": DECISION_CODES["atom_transition_bridge_available"],
            "decision_code": DECISION_CODES["atom_transition_bridge_available"],
            "value": obs["atom_transition_bridge_flag"],
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "decision_id": DECISION_CODES["transition_stress_map_available"],
            "decision_code": DECISION_CODES["transition_stress_map_available"],
            "value": obs["transition_stress_map_certified_flag"],
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "decision_id": DECISION_CODES["semantic_transition_operation_available"],
            "decision_code": DECISION_CODES[
                "semantic_transition_operation_available"
            ],
            "value": obs["semantic_transition_operation_flag"],
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
    ]
    gap_rows = [
        {
            "gap_id": GAP_CODES["atom_overlap_orientation_candidate"],
            "gap_code": GAP_CODES["atom_overlap_orientation_candidate"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["transition_atom_key_bridge"],
            "gap_code": GAP_CODES["transition_atom_key_bridge"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 1,
        },
        {
            "gap_id": GAP_CODES["transition_to_stress_coupling_map"],
            "gap_code": GAP_CODES["transition_to_stress_coupling_map"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["semantic_transition_operation"],
            "gap_code": GAP_CODES["semantic_transition_operation"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
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
            "gap_id": GAP_CODES["four_dimensional_metric_reduction"],
            "gap_code": GAP_CODES["four_dimensional_metric_reduction"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["thermal_gravity_derivation"],
            "gap_code": GAP_CODES["thermal_gravity_derivation"],
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
        "c59p3a": c59p3a,
        "transition_sem": transition_sem,
        "contact_lift": contact_lift,
        "stress_gate": stress_gate,
        "stress_couple": stress_couple,
        "surface_rows": surface_rows,
        "join_rows": join_rows,
        "decision_rows": decision_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    surface_table = table_from_rows(SURFACE_COLUMNS, rows["surface_rows"])
    join_table = table_from_rows(JOIN_COLUMNS, rows["join_rows"])
    decision_table = table_from_rows(DECISION_COLUMNS, rows["decision_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "source_surfaces_exact": obs["overlap_row_count"] == 14
        and obs["transition_row_count"] == 642
        and obs["contact_row_count"] == 642
        and obs["endpoint_row_count"] == 259
        and obs["stress_edge_row_count"] == 100,
        "existing_joins_preserved": obs["overlap_stress_shared_key_count"] == 5
        and obs["transition_contact_shared_key_count"] == 7
        and obs["contact_endpoint_bridge_flag"] == 1,
        "atom_score_not_consumed_by_transition_schema": obs[
            "transition_stress_shared_key_count"
        ]
        == 0
        and obs["transition_overlap_shared_key_count"] == 0
        and obs["contact_overlap_shared_key_count"] == 0
        and obs["endpoint_overlap_shared_key_count"] == 0
        and obs["transition_atom_column_count"] == 0
        and obs["transition_stress_edge_column_count"] == 0,
        "bridge_and_map_absent": obs["atom_transition_bridge_flag"] == 0
        and obs["transition_stress_map_certified_flag"] == 0
        and obs["current_schema_consumes_atom_score_flag"] == 0,
        "physical_boundaries_preserved": obs["semantic_transition_operation_flag"] == 0
        and obs["physical_selector_axiom_flag"] == 0
        and obs["four_dimensional_metric_flag"] == 0
        and obs["thermal_gravity_flag"] == 0,
        "table_shapes_match": surface_table.shape == (len(SURFACE_CODES), len(SURFACE_COLUMNS))
        and join_table.shape == (len(JOIN_CODES), len(JOIN_COLUMNS))
        and decision_table.shape == (len(DECISION_CODES), len(DECISION_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "transition_stress_lift_gate",
        "summary": {
            "overlap_row_count": obs["overlap_row_count"],
            "transition_row_count": obs["transition_row_count"],
            "contact_row_count": obs["contact_row_count"],
            "endpoint_row_count": obs["endpoint_row_count"],
            "stress_edge_row_count": obs["stress_edge_row_count"],
            "overlap_stress_shared_key_count": obs[
                "overlap_stress_shared_key_count"
            ],
            "transition_contact_shared_key_count": obs[
                "transition_contact_shared_key_count"
            ],
            "transition_atom_column_count": obs["transition_atom_column_count"],
            "transition_stress_edge_column_count": obs[
                "transition_stress_edge_column_count"
            ],
            "atom_transition_bridge_flag": obs["atom_transition_bridge_flag"],
            "transition_stress_map_certified_flag": obs[
                "transition_stress_map_certified_flag"
            ],
            "current_schema_consumes_atom_score_flag": obs[
                "current_schema_consumes_atom_score_flag"
            ],
            "semantic_transition_operation_flag": obs[
                "semantic_transition_operation_flag"
            ],
            "physical_selector_axiom_flag": obs["physical_selector_axiom_flag"],
        },
        "surface_code_map": {
            str(value): key for key, value in SURFACE_CODES.items()
        },
        "join_code_map": {str(value): key for key, value in JOIN_CODES.items()},
        "decision_code_map": {
            str(value): key for key, value in DECISION_CODES.items()
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "surface_table_sha256": sha_array(surface_table),
        "join_table_sha256": sha_array(join_table),
        "decision_table_sha256": sha_array(decision_table),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
        "surface_text_sha256": sha_text(csv_text(SURFACE_COLUMNS, rows["surface_rows"])),
        "join_text_sha256": sha_text(csv_text(JOIN_COLUMNS, rows["join_rows"])),
    }
    c59p3t = {
        "schema": "long.c59p3t@1",
        "object": "transition_stress_lift_gate",
        "status": STATUS if all(checks.values()) else "LONG_C59P3T_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.c59p3t.report@1",
        "status": c59p3t["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_c59p3t tests whether the formal atom-overlap stress orientation "
            "score can be consumed by the guarded transition surface. The score "
            "joins to the stress-edge surface and transitions join to contact "
            "rows, but the transition/contact/endpoint schemas still have no "
            "certified atom or stress-edge key into the overlap score."
        ),
        "stage_protocol": {
            "draft": "read long_c59p3a, long_transition_sem, long_contact_lift, long_stress_gate, and long_stress_couple",
            "witness": "emit surface schema rows, join rows, decisions, gaps, and observables",
            "coherence": "check existing joins, absent atom/stress keys, absent atom-transition bridge, and preserved physical exclusions",
            "closure": "certify the current transition-stress lift gate around the atom-overlap orientation score",
            "emit": "write long_c59p3t artifacts and verifier hook",
        },
        "inputs": {
            "long_c59p3a": input_entry(
                LONG_C59P3A,
                {
                    "status": rows["c59p3a"].get("status"),
                    "certificate_sha256": rows["c59p3a"].get("certificate_sha256"),
                },
            ),
            "long_c59p3a_overlap": input_entry(LONG_C59P3A_OVERLAP),
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
            "long_contact_lift": input_entry(
                LONG_CONTACT_LIFT,
                {
                    "status": rows["contact_lift"].get("status"),
                    "certificate_sha256": rows["contact_lift"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_contact_csv": input_entry(LONG_CONTACT_CSV),
            "long_endpoint_csv": input_entry(LONG_ENDPOINT_CSV),
            "long_stress_gate": input_entry(
                LONG_STRESS_GATE,
                {
                    "status": rows["stress_gate"].get("status"),
                    "certificate_sha256": rows["stress_gate"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_stress_edge": input_entry(LONG_STRESS_EDGE),
            "long_stress_couple": input_entry(
                LONG_STRESS_COUPLE,
                {
                    "status": rows["stress_couple"].get("status"),
                    "certificate_sha256": rows["stress_couple"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "c59p3t": relpath(OUT_DIR / "c59p3t.json"),
            "surface_csv": relpath(OUT_DIR / "surface.csv"),
            "join_csv": relpath(OUT_DIR / "join.csv"),
            "decision_csv": relpath(OUT_DIR / "decision.csv"),
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
                "the atom-overlap orientation score is joined to atom-keyed stress edges",
                "the guarded transition surface is joined to contact rows",
                "contact rows are bridged to raw endpoint rows by basis id",
                "no transition/contact/endpoint schema currently exposes the stress atom key consumed by the score",
                "no current transition-to-stress map consumes the atom-overlap score",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "a basis/raw-endpoint-to-stress-atom bridge",
                "a transition-to-stress coupling map",
                "semantic transition-operation realization",
                "acceptance of a physical selector axiom",
                "a four-dimensional metric reduction or thermal-gravity derivation",
            ],
        },
        "next_highest_yield_item": (
            "Construct the missing basis/raw-endpoint-to-stress-atom bridge, or "
            "certify that the current raw endpoint ontology cannot produce one."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.c59p3t.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.c59p3t.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "c59p3t": c59p3t,
        "surface_csv": csv_text(SURFACE_COLUMNS, rows["surface_rows"]),
        "join_csv": csv_text(JOIN_COLUMNS, rows["join_rows"]),
        "decision_csv": csv_text(DECISION_COLUMNS, rows["decision_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "surface_table": surface_table,
        "join_table": join_table,
        "decision_table": decision_table,
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
    write_json(OUT_DIR / "c59p3t.json", payloads["c59p3t"])
    (OUT_DIR / "surface.csv").write_text(payloads["surface_csv"], encoding="utf-8")
    (OUT_DIR / "join.csv").write_text(payloads["join_csv"], encoding="utf-8")
    (OUT_DIR / "decision.csv").write_text(
        payloads["decision_csv"], encoding="utf-8"
    )
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        surface_table=payloads["surface_table"],
        join_table=payloads["join_table"],
        decision_table=payloads["decision_table"],
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
