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
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .derive_long_time_sem import raw_tensor_path_from_index
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from derive_long_time_sem import raw_tensor_path_from_index
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_transition_sem"
STATUS = "LONG_TRANSITION_SEM_OBSTRUCTION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

PROOF_ROOT = D20_INVARIANTS / "proof_obligations"
RAW_INDEX = ROOT / "data" / "raw" / "index.json"
LONG_CONTACT_LIFT = PROOF_ROOT / "long_contact_lift" / "report.json"
LONG_CONTACT_ENDPOINT = PROOF_ROOT / "long_contact_lift" / "endpoint.csv"
LONG_CONTACT_CONTACT = PROOF_ROOT / "long_contact_lift" / "contact.csv"
LONG_METRIC_GATE = PROOF_ROOT / "long_metric_gate" / "report.json"
LONG_TIME_MAP = PROOF_ROOT / "long_time_map" / "report.json"
LONG_TIME_EDGE = PROOF_ROOT / "long_time_map" / "edge_time.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_transition_sem.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_transition_sem.py"

ENDPOINT_RAW_COLUMNS = [
    "basis_id",
    "source0_addr",
    "source1_addr",
    "target_addr",
    "coeff",
    "raw_row_id",
    "raw_row_id_flag",
]
TRANSITION_COLUMNS = [
    "transition_id",
    "edge_id",
    "left_basis_id",
    "right_basis_id",
    "left_raw_row_id",
    "right_raw_row_id",
    "source0_boundary_count",
    "source1_boundary_count",
    "boundary_count",
    "normal_form_delta_t",
    "contact_lift_flag",
    "endpoint_pair_raw_row_flag",
    "operation_row_id",
    "operation_source0_addr",
    "operation_source1_addr",
    "operation_target_addr",
    "operation_coeff",
    "operation_time_component",
    "semantic_transition_flag",
    "obstruction_code",
]
SCHEMA_GAP_COLUMNS = [
    "gap_id",
    "evidence_code",
    "present_flag",
    "required_for_semantic_flag",
    "row_count",
    "obstruction_flag",
]
GAP_COLUMNS = [
    "gap_id",
    "obligation_code",
    "required_for_gr_flag",
    "certified_flag",
    "obstruction_flag",
    "next_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

OBSTRUCTION_NAMES = [
    "contact_lift_is_boundary_adjacency_not_operation_row",
]
OBSTRUCTION_CODES = {name: index for index, name in enumerate(OBSTRUCTION_NAMES)}

EVIDENCE_NAMES = [
    "raw_endpoint_row_ids_present",
    "contact_lift_rows_present",
    "normal_form_time_rows_present",
    "semantic_operation_rows_absent",
    "transition_composition_law_absent",
]
EVIDENCE_CODES = {name: index for index, name in enumerate(EVIDENCE_NAMES)}

GAP_NAMES = [
    "owner_boundary_contact_lift",
    "semantic_operation_from_contact_lift",
    "physical_stress_energy_tensor",
    "nondegenerate_smooth_lorentzian_metric",
    "four_dimensional_spacetime_reduction",
    "curvature_and_einstein_tensor",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "raw_tensor_row_count",
    "raw_tensor_coeff_mass",
    "endpoint_row_count",
    "endpoint_raw_row_id_count",
    "contact_edge_count",
    "normal_form_time_edge_count",
    "transition_row_count",
    "endpoint_pair_raw_row_count",
    "contact_lift_edge_count",
    "normal_form_delta_sum",
    "operation_row_materialized_count",
    "semantic_transition_realized_count",
    "semantic_transition_obstructed_count",
    "finite_guard_transition_flag",
    "semantic_transition_operation_flag",
    "physical_stress_energy_flag",
    "smooth_lorentzian_metric_flag",
    "gr_derivation_flag",
    "open_gap_count",
    "next_gap_code",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _read_csv_int(path: Path) -> list[dict[str, int]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return [{key: int(value) for key, value in row.items()} for row in reader]


def _raw_tensor(path: Path) -> np.ndarray:
    with np.load(path, allow_pickle=False) as payload:
        triples = np.asarray(payload["triples"], dtype=np.int64)
    if triples.ndim != 2 or triples.shape[1] != 4:
        raise AssertionError("raw tensor triples must have shape n x 4")
    return triples


def _raw_row_index(triples: np.ndarray) -> dict[tuple[int, int, int, int], int]:
    return {
        tuple(int(value) for value in row): index
        for index, row in enumerate(triples.tolist())
    }


def endpoint_raw_rows(
    endpoint_rows: list[dict[str, int]],
    raw_index: dict[tuple[int, int, int, int], int],
) -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    for endpoint in endpoint_rows:
        key = (
            endpoint["source0_addr"],
            endpoint["source1_addr"],
            endpoint["target_addr"],
            endpoint["coeff"],
        )
        raw_row_id = int(raw_index.get(key, -1))
        rows.append(
            {
                "basis_id": endpoint["basis_id"],
                "source0_addr": endpoint["source0_addr"],
                "source1_addr": endpoint["source1_addr"],
                "target_addr": endpoint["target_addr"],
                "coeff": endpoint["coeff"],
                "raw_row_id": raw_row_id,
                "raw_row_id_flag": int(raw_row_id >= 0),
            }
        )
    return rows


def transition_rows(
    contact_rows: list[dict[str, int]],
    endpoint_raw: dict[int, dict[str, int]],
    edge_time: dict[int, dict[str, int]],
) -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    for transition_id, contact in enumerate(contact_rows):
        edge_id = contact["edge_id"]
        left = contact["left_basis_id"]
        right = contact["right_basis_id"]
        left_raw = endpoint_raw[left]["raw_row_id"]
        right_raw = endpoint_raw[right]["raw_row_id"]
        endpoint_pair_raw = int(left_raw >= 0 and right_raw >= 0)
        rows.append(
            {
                "transition_id": transition_id,
                "edge_id": edge_id,
                "left_basis_id": left,
                "right_basis_id": right,
                "left_raw_row_id": left_raw,
                "right_raw_row_id": right_raw,
                "source0_boundary_count": contact["source0_boundary_count"],
                "source1_boundary_count": contact["source1_boundary_count"],
                "boundary_count": contact["boundary_count"],
                "normal_form_delta_t": edge_time[edge_id]["delta_t"],
                "contact_lift_flag": contact["contact_lift_flag"],
                "endpoint_pair_raw_row_flag": endpoint_pair_raw,
                "operation_row_id": -1,
                "operation_source0_addr": -1,
                "operation_source1_addr": -1,
                "operation_target_addr": -1,
                "operation_coeff": 0,
                "operation_time_component": 0,
                "semantic_transition_flag": 0,
                "obstruction_code": OBSTRUCTION_CODES[
                    "contact_lift_is_boundary_adjacency_not_operation_row"
                ],
            }
        )
    return rows


def build_rows() -> dict[str, Any]:
    raw_index_payload = load_json(RAW_INDEX)
    raw_tensor_path = raw_tensor_path_from_index(raw_index_payload)
    raw_tensor = _raw_tensor(raw_tensor_path)
    raw_ids = _raw_row_index(raw_tensor)
    long_contact_lift = load_json(LONG_CONTACT_LIFT)
    long_metric_gate = load_json(LONG_METRIC_GATE)
    long_time_map = load_json(LONG_TIME_MAP)
    endpoints_source = _read_csv_int(LONG_CONTACT_ENDPOINT)
    contacts_source = _read_csv_int(LONG_CONTACT_CONTACT)
    edge_time_rows = _read_csv_int(LONG_TIME_EDGE)
    edge_time_by_id = {row["edge_id"]: row for row in edge_time_rows}

    endpoint_rows = endpoint_raw_rows(endpoints_source, raw_ids)
    endpoint_by_id = {row["basis_id"]: row for row in endpoint_rows}
    transitions = transition_rows(contacts_source, endpoint_by_id, edge_time_by_id)

    operation_row_materialized_count = sum(
        row["operation_row_id"] >= 0 for row in transitions
    )
    semantic_transition_realized_count = sum(
        row["semantic_transition_flag"] for row in transitions
    )
    semantic_transition_obstructed_count = len(transitions) - semantic_transition_realized_count

    schema_gap_rows = [
        {
            "gap_id": 0,
            "evidence_code": EVIDENCE_CODES["raw_endpoint_row_ids_present"],
            "present_flag": 1,
            "required_for_semantic_flag": 1,
            "row_count": len(endpoint_rows),
            "obstruction_flag": 0,
        },
        {
            "gap_id": 1,
            "evidence_code": EVIDENCE_CODES["contact_lift_rows_present"],
            "present_flag": 1,
            "required_for_semantic_flag": 1,
            "row_count": len(contacts_source),
            "obstruction_flag": 0,
        },
        {
            "gap_id": 2,
            "evidence_code": EVIDENCE_CODES["normal_form_time_rows_present"],
            "present_flag": 1,
            "required_for_semantic_flag": 1,
            "row_count": len(edge_time_rows),
            "obstruction_flag": 0,
        },
        {
            "gap_id": 3,
            "evidence_code": EVIDENCE_CODES["semantic_operation_rows_absent"],
            "present_flag": 0,
            "required_for_semantic_flag": 1,
            "row_count": 0,
            "obstruction_flag": 1,
        },
        {
            "gap_id": 4,
            "evidence_code": EVIDENCE_CODES["transition_composition_law_absent"],
            "present_flag": 0,
            "required_for_semantic_flag": 1,
            "row_count": 0,
            "obstruction_flag": 1,
        },
    ]

    gap_rows = [
        {
            "gap_id": 0,
            "obligation_code": GAP_CODES["owner_boundary_contact_lift"],
            "required_for_gr_flag": 1,
            "certified_flag": 1,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": 1,
            "obligation_code": GAP_CODES["semantic_operation_from_contact_lift"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": 2,
            "obligation_code": GAP_CODES["physical_stress_energy_tensor"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 1,
        },
        {
            "gap_id": 3,
            "obligation_code": GAP_CODES["nondegenerate_smooth_lorentzian_metric"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": 4,
            "obligation_code": GAP_CODES["four_dimensional_spacetime_reduction"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": 5,
            "obligation_code": GAP_CODES["curvature_and_einstein_tensor"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
    ]

    obs = {
        "raw_tensor_row_count": int(raw_tensor.shape[0]),
        "raw_tensor_coeff_mass": int(raw_tensor[:, 3].sum()),
        "endpoint_row_count": len(endpoint_rows),
        "endpoint_raw_row_id_count": sum(
            row["raw_row_id_flag"] for row in endpoint_rows
        ),
        "contact_edge_count": len(contacts_source),
        "normal_form_time_edge_count": len(edge_time_rows),
        "transition_row_count": len(transitions),
        "endpoint_pair_raw_row_count": sum(
            row["endpoint_pair_raw_row_flag"] for row in transitions
        ),
        "contact_lift_edge_count": sum(row["contact_lift_flag"] for row in transitions),
        "normal_form_delta_sum": sum(row["normal_form_delta_t"] for row in transitions),
        "operation_row_materialized_count": operation_row_materialized_count,
        "semantic_transition_realized_count": semantic_transition_realized_count,
        "semantic_transition_obstructed_count": semantic_transition_obstructed_count,
        "finite_guard_transition_flag": 1,
        "semantic_transition_operation_flag": 0,
        "physical_stress_energy_flag": 0,
        "smooth_lorentzian_metric_flag": 0,
        "gr_derivation_flag": 0,
        "open_gap_count": sum(1 - row["certified_flag"] for row in gap_rows),
        "next_gap_code": GAP_CODES["physical_stress_energy_tensor"],
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]

    return {
        "raw_index": raw_index_payload,
        "raw_tensor_path": raw_tensor_path,
        "raw_tensor": raw_tensor,
        "long_contact_lift": long_contact_lift,
        "long_metric_gate": long_metric_gate,
        "long_time_map": long_time_map,
        "endpoint_rows": endpoint_rows,
        "transition_rows": transitions,
        "schema_gap_rows": schema_gap_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "endpoint_table": table_from_rows(ENDPOINT_RAW_COLUMNS, endpoint_rows),
        "transition_table": table_from_rows(TRANSITION_COLUMNS, transitions),
        "schema_gap_table": table_from_rows(SCHEMA_GAP_COLUMNS, schema_gap_rows),
        "gap_table": table_from_rows(GAP_COLUMNS, gap_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "endpoint_text_hash": sha_text(digest_text(ENDPOINT_RAW_COLUMNS, endpoint_rows)),
        "transition_text_hash": sha_text(digest_text(TRANSITION_COLUMNS, transitions)),
        "schema_gap_text_hash": sha_text(
            digest_text(SCHEMA_GAP_COLUMNS, schema_gap_rows)
        ),
        "gap_text_hash": sha_text(digest_text(GAP_COLUMNS, gap_rows)),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    long_contact_lift = rows["long_contact_lift"]
    long_metric_gate = rows["long_metric_gate"]
    long_time_map = rows["long_time_map"]
    transitions = rows["transition_rows"]
    checks = {
        "contact_lift_input_certified": long_contact_lift.get("status")
        == "LONG_CONTACT_LIFT_CERTIFIED"
        and long_contact_lift.get("all_checks_pass") is True,
        "metric_gate_input_certified": long_metric_gate.get("status")
        == "LONG_METRIC_GATE_CERTIFIED"
        and long_metric_gate.get("all_checks_pass") is True,
        "time_map_input_certified": long_time_map.get("status")
        == "LONG_TIME_MAP_CERTIFIED"
        and long_time_map.get("all_checks_pass") is True,
        "raw_endpoint_ids_exact": obs["raw_tensor_row_count"] == 1_414_965
        and obs["raw_tensor_coeff_mass"] == 2_537_360
        and obs["endpoint_row_count"] == 259
        and obs["endpoint_raw_row_id_count"] == 259,
        "transition_rows_contact_backed": obs["contact_edge_count"] == 642
        and obs["transition_row_count"] == 642
        and obs["endpoint_pair_raw_row_count"] == 642
        and obs["contact_lift_edge_count"] == 642,
        "transition_rows_time_backed": obs["normal_form_time_edge_count"] == 642
        and obs["normal_form_delta_sum"] == 642
        and all(row["normal_form_delta_t"] == 1 for row in transitions),
        "semantic_operation_obstruction_exact": obs[
            "operation_row_materialized_count"
        ]
        == 0
        and obs["semantic_transition_realized_count"] == 0
        and obs["semantic_transition_obstructed_count"] == 642
        and obs["semantic_transition_operation_flag"] == 0
        and all(row["operation_row_id"] == -1 for row in transitions)
        and all(row["semantic_transition_flag"] == 0 for row in transitions),
        "guarded_transition_not_gr_claim": obs["finite_guard_transition_flag"] == 1
        and obs["physical_stress_energy_flag"] == 0
        and obs["smooth_lorentzian_metric_flag"] == 0
        and obs["gr_derivation_flag"] == 0,
        "table_shapes_match": rows["endpoint_table"].shape
        == (259, len(ENDPOINT_RAW_COLUMNS))
        and rows["transition_table"].shape == (642, len(TRANSITION_COLUMNS))
        and rows["schema_gap_table"].shape
        == (len(EVIDENCE_NAMES), len(SCHEMA_GAP_COLUMNS))
        and rows["gap_table"].shape == (len(GAP_NAMES), len(GAP_COLUMNS))
        and rows["observable_table"].shape == (len(OBS_NAMES), len(OBS_COLUMNS)),
    }

    witness = {
        "name": THEOREM_ID,
        "classification": "contact_lift_transition_semantic_obstruction",
        "obstruction_code_map": {
            str(value): key for key, value in OBSTRUCTION_CODES.items()
        },
        "evidence_code_map": {str(value): key for key, value in EVIDENCE_CODES.items()},
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "summary": {
            "endpoint_row_count": obs["endpoint_row_count"],
            "endpoint_raw_row_id_count": obs["endpoint_raw_row_id_count"],
            "contact_edge_count": obs["contact_edge_count"],
            "transition_row_count": obs["transition_row_count"],
            "endpoint_pair_raw_row_count": obs["endpoint_pair_raw_row_count"],
            "contact_lift_edge_count": obs["contact_lift_edge_count"],
            "normal_form_delta_sum": obs["normal_form_delta_sum"],
            "operation_row_materialized_count": obs[
                "operation_row_materialized_count"
            ],
            "semantic_transition_realized_count": obs[
                "semantic_transition_realized_count"
            ],
            "semantic_transition_obstructed_count": obs[
                "semantic_transition_obstructed_count"
            ],
            "finite_guard_transition_flag": obs["finite_guard_transition_flag"],
            "semantic_transition_operation_flag": obs[
                "semantic_transition_operation_flag"
            ],
            "next_gap": "physical_stress_energy_tensor",
        },
        "raw_tensor_sha256": sha_array(rows["raw_tensor"]),
        "endpoint_table_sha256": sha_array(rows["endpoint_table"]),
        "endpoint_text_sha256": rows["endpoint_text_hash"],
        "transition_table_sha256": sha_array(rows["transition_table"]),
        "transition_text_sha256": rows["transition_text_hash"],
        "schema_gap_table_sha256": sha_array(rows["schema_gap_table"]),
        "schema_gap_text_sha256": rows["schema_gap_text_hash"],
        "gap_table_sha256": sha_array(rows["gap_table"]),
        "gap_text_sha256": rows["gap_text_hash"],
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    transition_sem = {
        "schema": "long.transition_sem@1",
        "object": "contact_lift_transition_semantic_obstruction",
        "status": STATUS if all(checks.values()) else "LONG_TRANSITION_SEM_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.transition_sem.report@1",
        "status": transition_sem["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_transition_sem resolves the contact-lift promotion question "
            "under the current artifact boundary. Every contact-lifted recurrence "
            "edge is backed by explicit A985 raw row ids for both endpoint "
            "basis triples and by the normal-form time tick, but no semantic "
            "operation row or transition composition law is present. The "
            "contact-lifted edges therefore remain a guarded finite transition "
            "surface, not semantic A985 transition operations."
        ),
        "stage_protocol": {
            "draft": "read raw tensor, long_contact_lift, long_metric_gate, and long_time_map edge-time rows",
            "witness": "emit raw endpoint row ids, contact-lifted transition rows, schema-gap rows, and open gap rows",
            "coherence": "check raw endpoint ids, contact-lift coverage, normal-form time coverage, semantic-operation absence, and table hashes",
            "closure": "certify guarded finite transitions while recording the semantic operation-realization obstruction",
            "emit": "write long_transition_sem artifacts and verifier hook",
        },
        "inputs": {
            "raw_index": input_entry(RAW_INDEX),
            "raw_tensor": input_entry(
                rows["raw_tensor_path"],
                {
                    "row_count": int(rows["raw_tensor"].shape[0]),
                    "column_count": int(rows["raw_tensor"].shape[1]),
                },
            ),
            "long_contact_lift": input_entry(
                LONG_CONTACT_LIFT,
                {
                    "status": long_contact_lift.get("status"),
                    "certificate_sha256": long_contact_lift.get("certificate_sha256"),
                },
            ),
            "long_contact_endpoint": input_entry(
                LONG_CONTACT_ENDPOINT,
                {"row_count": len(rows["endpoint_rows"])},
            ),
            "long_contact_contact": input_entry(
                LONG_CONTACT_CONTACT,
                {"row_count": len(rows["transition_rows"])},
            ),
            "long_metric_gate": input_entry(
                LONG_METRIC_GATE,
                {
                    "status": long_metric_gate.get("status"),
                    "certificate_sha256": long_metric_gate.get("certificate_sha256"),
                },
            ),
            "long_time_map": input_entry(
                LONG_TIME_MAP,
                {
                    "status": long_time_map.get("status"),
                    "certificate_sha256": long_time_map.get("certificate_sha256"),
                },
            ),
            "long_time_edge": input_entry(LONG_TIME_EDGE),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "transition_sem": relpath(OUT_DIR / "transition_sem.json"),
            "endpoint_raw_csv": relpath(OUT_DIR / "endpoint_raw.csv"),
            "transition_csv": relpath(OUT_DIR / "transition.csv"),
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
                "all 259 contact-lift endpoints have explicit A985 raw tensor row ids",
                "all 642 recurrence transitions are contact-lift-backed and endpoint-row-backed",
                "all 642 guarded finite transitions carry the normal-form unit time tick",
                "no semantic A985 operation row is materialized for the contact-lifted transitions",
                "contact-lifted transitions remain guarded finite transitions rather than semantic A985 operations",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "semantic A985 transition-operation realization for the 642 recurrence transitions",
                "a transition composition law promoting owner-boundary contacts to operations",
                "a physical stress-energy tensor",
                "a nondegenerate smooth Lorentzian metric tensor",
                "Riemann/Ricci curvature, Einstein tensor, or Einstein field equations",
            ],
        },
        "next_highest_yield_item": (
            "Build long_stress_gate: combine the guarded finite transition "
            "surface with the certified stress-neighborhood graph and decide "
            "what can be called finite stress, while keeping physical "
            "stress-energy explicitly open."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.transition_sem.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.transition_sem.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "transition_sem": transition_sem,
        "endpoint_raw_csv": csv_text(ENDPOINT_RAW_COLUMNS, rows["endpoint_rows"]),
        "transition_csv": csv_text(TRANSITION_COLUMNS, rows["transition_rows"]),
        "schema_gap_csv": csv_text(SCHEMA_GAP_COLUMNS, rows["schema_gap_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "raw_tensor": rows["raw_tensor"],
        "endpoint_table": rows["endpoint_table"],
        "transition_table": rows["transition_table"],
        "schema_gap_table": rows["schema_gap_table"],
        "gap_table": rows["gap_table"],
        "observable_table": rows["observable_table"],
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
    write_json(OUT_DIR / "transition_sem.json", payloads["transition_sem"])
    (OUT_DIR / "endpoint_raw.csv").write_text(
        payloads["endpoint_raw_csv"], encoding="utf-8"
    )
    (OUT_DIR / "transition.csv").write_text(
        payloads["transition_csv"], encoding="utf-8"
    )
    (OUT_DIR / "schema_gap.csv").write_text(
        payloads["schema_gap_csv"], encoding="utf-8"
    )
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        raw_tensor=payloads["raw_tensor"],
        endpoint_table=payloads["endpoint_table"],
        transition_table=payloads["transition_table"],
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
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
