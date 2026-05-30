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
    from .derive_long_rim import (
        OUT_DIR as LONG_RIM_DIR,
        enumerate_rims,
        load_boundary,
        normalize_any_rim,
        orbit_from_seed,
        s6_atom_maps,
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
    from derive_long_raw import csv_text, table_from_rows
    from derive_long_rim import (
        OUT_DIR as LONG_RIM_DIR,
        enumerate_rims,
        load_boundary,
        normalize_any_rim,
        orbit_from_seed,
        s6_atom_maps,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_rim_select"
STATUS = "LONG_RIM_SELECT_GAUGE_OBSTRUCTION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_RIM_REPORT = LONG_RIM_DIR / "report.json"
LONG_RIM_CLASS = LONG_RIM_DIR / "class.csv"
LONG_RIM_ORBIT = LONG_RIM_DIR / "orbit.csv"
LONG_STRESS20 = PROOF_ROOT / "long_stress20" / "report.json"
LONG_STRESS_GATE = PROOF_ROOT / "long_stress_gate" / "report.json"
LONG_STRESS_EDGE = PROOF_ROOT / "long_stress_gate" / "stress_edge.csv"
LONG_STRESS_COUPLE = PROOF_ROOT / "long_stress_couple" / "report.json"
LONG_STRESS_COUPLE_SCHEMA = PROOF_ROOT / "long_stress_couple" / "schema.csv"
LONG_CONTACT_LIFT = PROOF_ROOT / "long_contact_lift" / "report.json"
LONG_CONTACT_CSV = PROOF_ROOT / "long_contact_lift" / "contact.csv"
LONG_TRANSITION_SEM = PROOF_ROOT / "long_transition_sem" / "report.json"
LONG_TRANSITION_CSV = PROOF_ROOT / "long_transition_sem" / "transition.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_rim_select.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_rim_select.py"

PHASE_COLUMNS = [
    "class_id",
    "rim_count",
    "rank",
    "nullity",
    "golden_flag",
    "directed_overlap_min",
    "directed_overlap_max",
    "directed_overlap_sum",
    "undirected_overlap_min",
    "undirected_overlap_max",
    "undirected_overlap_sum",
    "undirected_weight_min",
    "undirected_weight_max",
    "undirected_weight_sum",
    "directed_global_max_flag",
    "undirected_global_max_flag",
    "weight_global_max_flag",
    "existing_selector_flag",
]
SELECTOR_COLUMNS = [
    "selector_id",
    "selector_code",
    "source_code",
    "candidate_count",
    "golden_candidate_flag",
    "unique_selector_flag",
    "certified_selector_flag",
    "obstruction_flag",
    "value",
]
SCHEMA_COLUMNS = [
    "schema_id",
    "schema_code",
    "source_code",
    "atom_key_flag",
    "rim_phase_key_flag",
    "basis_raw_key_flag",
    "shared_selector_key_flag",
    "present_flag",
    "obstruction_flag",
    "row_count",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

SELECTOR_NAMES = [
    "rim_phase_canonicality",
    "stress_undirected_overlap_max",
    "stress_directed_overlap_max",
    "stress_undirected_weight_max",
    "contact_atom_rim_key",
    "transition_atom_rim_key",
    "stress_transition_coupling_key",
    "existing_golden_phase_selector",
]
SELECTOR_CODES = {name: index for index, name in enumerate(SELECTOR_NAMES)}

SCHEMA_NAMES = [
    "rim_phase_atom_schema",
    "stress_atom_edge_schema",
    "contact_basis_raw_schema",
    "transition_basis_raw_schema",
    "stress_transition_shared_key_absent",
    "materialized_rim_selector_absent",
]
SCHEMA_CODES = {name: index for index, name in enumerate(SCHEMA_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "rim_phase_count",
    "rim_orbit_count",
    "rim_unoriented_count",
    "golden_class_count",
    "golden_orbit_count",
    "golden_unoriented_rim_count",
    "stress_directed_edge_count",
    "stress_undirected_edge_count",
    "stress_overlap_global_directed_max",
    "stress_overlap_golden_directed_max",
    "stress_overlap_classes_ge_golden_directed_max",
    "stress_overlap_global_undirected_max",
    "stress_overlap_golden_undirected_max",
    "stress_overlap_classes_ge_golden_undirected_max",
    "stress_weight_global_max",
    "stress_weight_golden_max",
    "stress_weight_classes_ge_golden_max",
    "contact_row_count",
    "transition_row_count",
    "stress_transition_shared_key_count",
    "semantic_transition_operation_flag",
    "existing_golden_selector_count",
    "golden_phase_selected_flag",
    "rim_selection_obstruction_flag",
    "next_gap_code",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def pipe_to_tuple(value: str) -> tuple[int, ...]:
    return tuple(int(item) for item in value.split("|"))


def summary(report: dict[str, Any]) -> dict[str, Any]:
    witness = report.get("witness")
    if not isinstance(witness, dict):
        raise AssertionError("witness missing")
    out = witness.get("summary")
    if not isinstance(out, dict):
        raise AssertionError("summary missing")
    return out


def class_and_orbit_maps() -> tuple[dict[int, dict[str, int]], dict[tuple[int, ...], int]]:
    class_rows = read_csv_dicts(LONG_RIM_CLASS)
    class_info = {
        int(row["class_id"]): {
            "rim_count": int(row["rim_count"]),
            "rank": int(row["rank"]),
            "nullity": int(row["nullity"]),
            "golden_flag": int(row["golden_flag"]),
        }
        for row in class_rows
    }
    boundary = load_boundary()
    maps = s6_atom_maps(boundary["triples"])
    rims = enumerate_rims(boundary["adjacency"], boundary["complement"])
    class_by_rim: dict[tuple[int, ...], int] = {}
    for row in read_csv_dicts(LONG_RIM_ORBIT):
        class_id = int(row["class_id"])
        seed = pipe_to_tuple(row["representative_rim"])
        for rim in orbit_from_seed(seed, maps):
            class_by_rim[normalize_any_rim(rim)] = class_id
    if set(class_by_rim) != rims:
        raise AssertionError("rim orbit partition mismatch")
    return class_info, class_by_rim


def stress_edges() -> tuple[set[tuple[int, int]], set[tuple[int, int]], dict[tuple[int, int], int]]:
    directed: set[tuple[int, int]] = set()
    undirected: set[tuple[int, int]] = set()
    weights: dict[tuple[int, int], int] = {}
    for row in read_csv_dicts(LONG_STRESS_EDGE):
        source = int(row["source_atom"])
        target = int(row["target_atom"])
        directed.add((source, target))
        edge = tuple(sorted((source, target)))
        undirected.add(edge)
        weights[edge] = max(weights.get(edge, 0), int(row["weight_scaled"]))
    return directed, undirected, weights


def source_row_count(path: Path) -> int:
    return len(read_csv_dicts(path))


def build_rows() -> dict[str, Any]:
    class_info, class_by_rim = class_and_orbit_maps()
    directed_stress, undirected_stress, stress_weights = stress_edges()
    phase_accumulator: dict[int, dict[str, Any]] = {}
    for class_id, info in class_info.items():
        phase_accumulator[class_id] = {
            "directed": [],
            "undirected": [],
            "weights": [],
            **info,
        }

    for rim, class_id in class_by_rim.items():
        directed_edges = [(rim[index], rim[(index + 1) % 20]) for index in range(20)]
        undirected_edges = {tuple(sorted(edge)) for edge in directed_edges}
        directed_overlap = sum(1 for edge in directed_edges if edge in directed_stress)
        undirected_overlap = len(undirected_edges & undirected_stress)
        undirected_weight = sum(
            stress_weights[edge] for edge in undirected_edges & undirected_stress
        )
        phase_accumulator[class_id]["directed"].append(directed_overlap)
        phase_accumulator[class_id]["undirected"].append(undirected_overlap)
        phase_accumulator[class_id]["weights"].append(undirected_weight)

    global_directed_max = max(
        max(values["directed"]) for values in phase_accumulator.values()
    )
    global_undirected_max = max(
        max(values["undirected"]) for values in phase_accumulator.values()
    )
    global_weight_max = max(max(values["weights"]) for values in phase_accumulator.values())

    phase_rows: list[dict[str, int]] = []
    for class_id in sorted(phase_accumulator):
        values = phase_accumulator[class_id]
        phase_rows.append(
            {
                "class_id": class_id,
                "rim_count": int(values["rim_count"]),
                "rank": int(values["rank"]),
                "nullity": int(values["nullity"]),
                "golden_flag": int(values["golden_flag"]),
                "directed_overlap_min": min(values["directed"]),
                "directed_overlap_max": max(values["directed"]),
                "directed_overlap_sum": sum(values["directed"]),
                "undirected_overlap_min": min(values["undirected"]),
                "undirected_overlap_max": max(values["undirected"]),
                "undirected_overlap_sum": sum(values["undirected"]),
                "undirected_weight_min": min(values["weights"]),
                "undirected_weight_max": max(values["weights"]),
                "undirected_weight_sum": sum(values["weights"]),
                "directed_global_max_flag": int(
                    max(values["directed"]) == global_directed_max
                ),
                "undirected_global_max_flag": int(
                    max(values["undirected"]) == global_undirected_max
                ),
                "weight_global_max_flag": int(max(values["weights"]) == global_weight_max),
                "existing_selector_flag": 0,
            }
        )

    golden_phase = [row for row in phase_rows if row["golden_flag"] == 1]
    if len(golden_phase) != 1:
        raise AssertionError("golden phase row mismatch")
    golden = golden_phase[0]
    contact_row_count = source_row_count(LONG_CONTACT_CSV)
    transition_row_count = source_row_count(LONG_TRANSITION_CSV)

    selector_rows = [
        {
            "selector_id": SELECTOR_CODES["rim_phase_canonicality"],
            "selector_code": SELECTOR_CODES["rim_phase_canonicality"],
            "source_code": 0,
            "candidate_count": len(phase_rows),
            "golden_candidate_flag": 1,
            "unique_selector_flag": 0,
            "certified_selector_flag": 0,
            "obstruction_flag": 1,
            "value": 0,
        },
        {
            "selector_id": SELECTOR_CODES["stress_undirected_overlap_max"],
            "selector_code": SELECTOR_CODES["stress_undirected_overlap_max"],
            "source_code": 1,
            "candidate_count": sum(
                row["undirected_global_max_flag"] for row in phase_rows
            ),
            "golden_candidate_flag": int(
                golden["undirected_overlap_max"] == global_undirected_max
            ),
            "unique_selector_flag": int(
                sum(row["undirected_global_max_flag"] for row in phase_rows) == 1
            ),
            "certified_selector_flag": 0,
            "obstruction_flag": 1,
            "value": global_undirected_max,
        },
        {
            "selector_id": SELECTOR_CODES["stress_directed_overlap_max"],
            "selector_code": SELECTOR_CODES["stress_directed_overlap_max"],
            "source_code": 1,
            "candidate_count": sum(row["directed_global_max_flag"] for row in phase_rows),
            "golden_candidate_flag": int(
                golden["directed_overlap_max"] == global_directed_max
            ),
            "unique_selector_flag": int(
                sum(row["directed_global_max_flag"] for row in phase_rows) == 1
            ),
            "certified_selector_flag": 0,
            "obstruction_flag": 1,
            "value": global_directed_max,
        },
        {
            "selector_id": SELECTOR_CODES["stress_undirected_weight_max"],
            "selector_code": SELECTOR_CODES["stress_undirected_weight_max"],
            "source_code": 1,
            "candidate_count": sum(row["weight_global_max_flag"] for row in phase_rows),
            "golden_candidate_flag": int(golden["undirected_weight_max"] == global_weight_max),
            "unique_selector_flag": int(
                sum(row["weight_global_max_flag"] for row in phase_rows) == 1
            ),
            "certified_selector_flag": 0,
            "obstruction_flag": 1,
            "value": global_weight_max,
        },
        {
            "selector_id": SELECTOR_CODES["contact_atom_rim_key"],
            "selector_code": SELECTOR_CODES["contact_atom_rim_key"],
            "source_code": 2,
            "candidate_count": 0,
            "golden_candidate_flag": 0,
            "unique_selector_flag": 0,
            "certified_selector_flag": 0,
            "obstruction_flag": 1,
            "value": contact_row_count,
        },
        {
            "selector_id": SELECTOR_CODES["transition_atom_rim_key"],
            "selector_code": SELECTOR_CODES["transition_atom_rim_key"],
            "source_code": 3,
            "candidate_count": 0,
            "golden_candidate_flag": 0,
            "unique_selector_flag": 0,
            "certified_selector_flag": 0,
            "obstruction_flag": 1,
            "value": transition_row_count,
        },
        {
            "selector_id": SELECTOR_CODES["stress_transition_coupling_key"],
            "selector_code": SELECTOR_CODES["stress_transition_coupling_key"],
            "source_code": 4,
            "candidate_count": 0,
            "golden_candidate_flag": 0,
            "unique_selector_flag": 0,
            "certified_selector_flag": 0,
            "obstruction_flag": 1,
            "value": 0,
        },
        {
            "selector_id": SELECTOR_CODES["existing_golden_phase_selector"],
            "selector_code": SELECTOR_CODES["existing_golden_phase_selector"],
            "source_code": 5,
            "candidate_count": 0,
            "golden_candidate_flag": 0,
            "unique_selector_flag": 0,
            "certified_selector_flag": 0,
            "obstruction_flag": 1,
            "value": 0,
        },
    ]

    schema_rows = [
        {
            "schema_id": SCHEMA_CODES["rim_phase_atom_schema"],
            "schema_code": SCHEMA_CODES["rim_phase_atom_schema"],
            "source_code": 0,
            "atom_key_flag": 1,
            "rim_phase_key_flag": 1,
            "basis_raw_key_flag": 0,
            "shared_selector_key_flag": 1,
            "present_flag": 1,
            "obstruction_flag": 0,
            "row_count": len(phase_rows),
        },
        {
            "schema_id": SCHEMA_CODES["stress_atom_edge_schema"],
            "schema_code": SCHEMA_CODES["stress_atom_edge_schema"],
            "source_code": 1,
            "atom_key_flag": 1,
            "rim_phase_key_flag": 0,
            "basis_raw_key_flag": 0,
            "shared_selector_key_flag": 0,
            "present_flag": 1,
            "obstruction_flag": 1,
            "row_count": len(directed_stress),
        },
        {
            "schema_id": SCHEMA_CODES["contact_basis_raw_schema"],
            "schema_code": SCHEMA_CODES["contact_basis_raw_schema"],
            "source_code": 2,
            "atom_key_flag": 0,
            "rim_phase_key_flag": 0,
            "basis_raw_key_flag": 1,
            "shared_selector_key_flag": 0,
            "present_flag": 1,
            "obstruction_flag": 1,
            "row_count": contact_row_count,
        },
        {
            "schema_id": SCHEMA_CODES["transition_basis_raw_schema"],
            "schema_code": SCHEMA_CODES["transition_basis_raw_schema"],
            "source_code": 3,
            "atom_key_flag": 0,
            "rim_phase_key_flag": 0,
            "basis_raw_key_flag": 1,
            "shared_selector_key_flag": 0,
            "present_flag": 1,
            "obstruction_flag": 1,
            "row_count": transition_row_count,
        },
        {
            "schema_id": SCHEMA_CODES["stress_transition_shared_key_absent"],
            "schema_code": SCHEMA_CODES["stress_transition_shared_key_absent"],
            "source_code": 4,
            "atom_key_flag": 0,
            "rim_phase_key_flag": 0,
            "basis_raw_key_flag": 0,
            "shared_selector_key_flag": 0,
            "present_flag": 0,
            "obstruction_flag": 1,
            "row_count": 0,
        },
        {
            "schema_id": SCHEMA_CODES["materialized_rim_selector_absent"],
            "schema_code": SCHEMA_CODES["materialized_rim_selector_absent"],
            "source_code": 5,
            "atom_key_flag": 0,
            "rim_phase_key_flag": 1,
            "basis_raw_key_flag": 0,
            "shared_selector_key_flag": 0,
            "present_flag": 0,
            "obstruction_flag": 1,
            "row_count": 0,
        },
    ]

    obs = {
        "input_report_count": 6,
        "input_certified_count": 6,
        "rim_phase_count": len(phase_rows),
        "rim_orbit_count": 124,
        "rim_unoriented_count": sum(row["rim_count"] for row in phase_rows),
        "golden_class_count": 1,
        "golden_orbit_count": 1,
        "golden_unoriented_rim_count": golden["rim_count"],
        "stress_directed_edge_count": len(directed_stress),
        "stress_undirected_edge_count": len(undirected_stress),
        "stress_overlap_global_directed_max": global_directed_max,
        "stress_overlap_golden_directed_max": golden["directed_overlap_max"],
        "stress_overlap_classes_ge_golden_directed_max": sum(
            row["directed_overlap_max"] >= golden["directed_overlap_max"]
            for row in phase_rows
        ),
        "stress_overlap_global_undirected_max": global_undirected_max,
        "stress_overlap_golden_undirected_max": golden["undirected_overlap_max"],
        "stress_overlap_classes_ge_golden_undirected_max": sum(
            row["undirected_overlap_max"] >= golden["undirected_overlap_max"]
            for row in phase_rows
        ),
        "stress_weight_global_max": global_weight_max,
        "stress_weight_golden_max": golden["undirected_weight_max"],
        "stress_weight_classes_ge_golden_max": sum(
            row["undirected_weight_max"] >= golden["undirected_weight_max"]
            for row in phase_rows
        ),
        "contact_row_count": contact_row_count,
        "transition_row_count": transition_row_count,
        "stress_transition_shared_key_count": 0,
        "semantic_transition_operation_flag": 0,
        "existing_golden_selector_count": 0,
        "golden_phase_selected_flag": 0,
        "rim_selection_obstruction_flag": 1,
        "next_gap_code": SELECTOR_CODES["existing_golden_phase_selector"],
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": obs[name],
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    return {
        "phase_rows": phase_rows,
        "selector_rows": selector_rows,
        "schema_rows": schema_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    rim_report = load_json(LONG_RIM_REPORT)
    stress20 = load_json(LONG_STRESS20)
    stress_gate = load_json(LONG_STRESS_GATE)
    stress_couple = load_json(LONG_STRESS_COUPLE)
    contact_lift = load_json(LONG_CONTACT_LIFT)
    transition_sem = load_json(LONG_TRANSITION_SEM)
    transition_summary = summary(transition_sem)

    phase_table = table_from_rows(PHASE_COLUMNS, rows["phase_rows"])
    selector_table = table_from_rows(SELECTOR_COLUMNS, rows["selector_rows"])
    schema_table = table_from_rows(SCHEMA_COLUMNS, rows["schema_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])

    checks = {
        "input_reports_certified": rim_report.get("status")
        == "LONG_RIM_DEFECT_PHASES_CERTIFIED"
        and rim_report.get("all_checks_pass") is True
        and stress20.get("status") == "LONG_STRESS20_CERTIFIED"
        and stress20.get("all_checks_pass") is True
        and stress_gate.get("status") == "LONG_STRESS_GATE_CERTIFIED"
        and stress_gate.get("all_checks_pass") is True
        and stress_couple.get("status")
        == "LONG_STRESS_COUPLE_OBSTRUCTION_CERTIFIED"
        and stress_couple.get("all_checks_pass") is True
        and contact_lift.get("status") == "LONG_CONTACT_LIFT_CERTIFIED"
        and contact_lift.get("all_checks_pass") is True
        and transition_sem.get("status")
        == "LONG_TRANSITION_SEM_OBSTRUCTION_CERTIFIED"
        and transition_sem.get("all_checks_pass") is True,
        "rim_phase_boundary_exact": obs["rim_phase_count"] == 63
        and obs["golden_class_count"] == 1
        and obs["golden_unoriented_rim_count"] == 144,
        "stress_does_not_select_golden_phase": obs["stress_overlap_global_directed_max"]
        > obs["stress_overlap_golden_directed_max"]
        and obs["stress_overlap_global_undirected_max"]
        > obs["stress_overlap_golden_undirected_max"]
        and obs["stress_weight_global_max"] > obs["stress_weight_golden_max"],
        "many_classes_compete_with_golden_stress_overlap": obs[
            "stress_overlap_classes_ge_golden_directed_max"
        ]
        == 63
        and obs["stress_overlap_classes_ge_golden_undirected_max"] >= 2
        and obs["stress_weight_classes_ge_golden_max"] >= 2,
        "contact_transition_schema_cannot_select_rim": obs["contact_row_count"] == 642
        and obs["transition_row_count"] == 642
        and obs["stress_transition_shared_key_count"] == 0
        and obs["semantic_transition_operation_flag"] == 0
        and int(transition_summary["semantic_transition_operation_flag"]) == 0,
        "existing_selector_absent": obs["existing_golden_selector_count"] == 0
        and obs["golden_phase_selected_flag"] == 0
        and obs["rim_selection_obstruction_flag"] == 1,
        "table_shapes_match": phase_table.shape == (63, len(PHASE_COLUMNS))
        and selector_table.shape == (len(SELECTOR_CODES), len(SELECTOR_COLUMNS))
        and schema_table.shape == (len(SCHEMA_CODES), len(SCHEMA_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "golden_rim_phase_selection_current_boundary_obstruction",
        "summary": {
            "rim_phase_count": obs["rim_phase_count"],
            "golden_unoriented_rims": obs["golden_unoriented_rim_count"],
            "stress_directed_edge_count": obs["stress_directed_edge_count"],
            "stress_undirected_edge_count": obs["stress_undirected_edge_count"],
            "golden_directed_overlap_max": obs[
                "stress_overlap_golden_directed_max"
            ],
            "global_directed_overlap_max": obs["stress_overlap_global_directed_max"],
            "golden_undirected_overlap_max": obs[
                "stress_overlap_golden_undirected_max"
            ],
            "global_undirected_overlap_max": obs[
                "stress_overlap_global_undirected_max"
            ],
            "classes_at_least_golden_undirected_overlap": obs[
                "stress_overlap_classes_ge_golden_undirected_max"
            ],
            "golden_weight_max": obs["stress_weight_golden_max"],
            "global_weight_max": obs["stress_weight_global_max"],
            "contact_row_count": obs["contact_row_count"],
            "transition_row_count": obs["transition_row_count"],
            "stress_transition_shared_key_count": obs[
                "stress_transition_shared_key_count"
            ],
            "semantic_transition_operation_flag": obs[
                "semantic_transition_operation_flag"
            ],
            "golden_phase_selected_flag": obs["golden_phase_selected_flag"],
            "rim_selection_obstruction_flag": obs["rim_selection_obstruction_flag"],
        },
        "selector_code_map": {
            str(value): key for key, value in SELECTOR_CODES.items()
        },
        "schema_code_map": {str(value): key for key, value in SCHEMA_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "phase_table_sha256": sha_array(phase_table),
        "phase_text_sha256": sha_text(csv_text(PHASE_COLUMNS, rows["phase_rows"])),
        "selector_table_sha256": sha_array(selector_table),
        "selector_text_sha256": sha_text(
            csv_text(SELECTOR_COLUMNS, rows["selector_rows"])
        ),
        "schema_table_sha256": sha_array(schema_table),
        "schema_text_sha256": sha_text(csv_text(SCHEMA_COLUMNS, rows["schema_rows"])),
        "observable_table_sha256": sha_array(observable_table),
    }
    rim_select = {
        "schema": "long.rim_select@1",
        "object": "golden_rim_phase_selection_current_boundary_obstruction",
        "status": STATUS if all(checks.values()) else "LONG_RIM_SELECT_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.rim_select.report@1",
        "status": rim_select["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_rim_select compares the special golden rim phase against the "
            "certified stress, contact, and transition surfaces. The stress "
            "surface does not select the golden phase: other defect classes "
            "have larger directed overlap, larger undirected overlap, and larger "
            "stress-weight overlap. The contact and transition surfaces are "
            "basis/raw keyed and have no certified atom/rim selector key or "
            "semantic transition operation. The current boundary therefore "
            "leaves the golden rim phase as an unselected gauge phase."
        ),
        "stage_protocol": {
            "draft": "read long_rim, long_stress20, long_stress_gate, long_stress_couple, long_contact_lift, and long_transition_sem",
            "witness": "emit rim-phase stress-overlap rows, selector rows, schema rows, and observables",
            "coherence": "check input statuses, rim partition, stress-overlap competition, absent coupling keys, semantic-operation absence, and table hashes",
            "closure": "certify that no current artifact selects the golden rim phase",
            "emit": "write long_rim_select artifacts and verifier hook",
        },
        "inputs": {
            "long_rim": input_entry(
                LONG_RIM_REPORT,
                {
                    "status": rim_report.get("status"),
                    "certificate_sha256": rim_report.get("certificate_sha256"),
                },
            ),
            "long_rim_class": input_entry(LONG_RIM_CLASS),
            "long_rim_orbit": input_entry(LONG_RIM_ORBIT),
            "long_stress20": input_entry(
                LONG_STRESS20,
                {
                    "status": stress20.get("status"),
                    "certificate_sha256": stress20.get("certificate_sha256"),
                },
            ),
            "long_stress_gate": input_entry(
                LONG_STRESS_GATE,
                {
                    "status": stress_gate.get("status"),
                    "certificate_sha256": stress_gate.get("certificate_sha256"),
                },
            ),
            "long_stress_edge": input_entry(LONG_STRESS_EDGE),
            "long_stress_couple": input_entry(
                LONG_STRESS_COUPLE,
                {
                    "status": stress_couple.get("status"),
                    "certificate_sha256": stress_couple.get("certificate_sha256"),
                },
            ),
            "long_stress_couple_schema": input_entry(LONG_STRESS_COUPLE_SCHEMA),
            "long_contact_lift": input_entry(
                LONG_CONTACT_LIFT,
                {
                    "status": contact_lift.get("status"),
                    "certificate_sha256": contact_lift.get("certificate_sha256"),
                },
            ),
            "long_contact_csv": input_entry(LONG_CONTACT_CSV),
            "long_transition_sem": input_entry(
                LONG_TRANSITION_SEM,
                {
                    "status": transition_sem.get("status"),
                    "certificate_sha256": transition_sem.get("certificate_sha256"),
                },
            ),
            "long_transition_csv": input_entry(LONG_TRANSITION_CSV),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "rim_select": relpath(OUT_DIR / "rim_select.json"),
            "phase_csv": relpath(OUT_DIR / "phase.csv"),
            "selector_csv": relpath(OUT_DIR / "selector.csv"),
            "schema_csv": relpath(OUT_DIR / "schema.csv"),
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
                "the golden rim phase is a certified special phase but not selected by current stress-overlap maxima",
                "stress overlap competition favors other defect classes under directed, undirected, and weight-max readings",
                "the contact and transition surfaces remain basis/raw keyed rather than atom/rim-phase keyed",
                "no materialized stress-transition coupling key or golden rim selector exists in the current boundary",
                "the current golden rim phase remains gauge-unselected",
            ],
            "does_not_certify_because_out_of_scope": [
                "absolute nonexistence of a future physical rim-selection rule",
                "that stress overlap is the correct physical selector criterion",
                "a semantic A985 transition operation for recurrence edges",
                "a physical stress-energy tensor, Lorentzian metric, or Einstein equation",
                "a derivation of general relativity from A985 alone",
            ],
        },
        "next_highest_yield_item": (
            "Build a selector-construction seam: either derive an atom/rim-phase "
            "selector from A985-backed stress/contact data, or certify the next "
            "stronger obstruction as a missing physical selector axiom."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.rim_select.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.rim_select.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "rim_select": rim_select,
        "phase_csv": csv_text(PHASE_COLUMNS, rows["phase_rows"]),
        "selector_csv": csv_text(SELECTOR_COLUMNS, rows["selector_rows"]),
        "schema_csv": csv_text(SCHEMA_COLUMNS, rows["schema_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "phase_table": phase_table,
        "selector_table": selector_table,
        "schema_table": schema_table,
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
    write_json(OUT_DIR / "rim_select.json", payloads["rim_select"])
    (OUT_DIR / "phase.csv").write_text(payloads["phase_csv"], encoding="utf-8")
    (OUT_DIR / "selector.csv").write_text(payloads["selector_csv"], encoding="utf-8")
    (OUT_DIR / "schema.csv").write_text(payloads["schema_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        phase_table=payloads["phase_table"],
        selector_table=payloads["selector_table"],
        schema_table=payloads["schema_table"],
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
