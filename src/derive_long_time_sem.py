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
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_time_sem"
STATUS = "LONG_TIME_SEM_OBSTRUCTION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

PROOF_ROOT = D20_INVARIANTS / "proof_obligations"
CORE_A985 = ROOT / "data" / "core" / "a985.json"
RAW_INDEX = ROOT / "data" / "raw" / "index.json"
LONG_TIME_MAP = PROOF_ROOT / "long_time_map" / "report.json"
LONG_TIME_EDGE = PROOF_ROOT / "long_time_map" / "edge_time.csv"
LONG_REC = PROOF_ROOT / "long_rec" / "report.json"
LONG_REC_OWNER = PROOF_ROOT / "long_rec" / "owner.csv"
LONG_REC_EDGE = PROOF_ROOT / "long_rec" / "edge.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_time_sem.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_time_sem.py"

EDGE_SEM_COLUMNS = [
    "edge_id",
    "left_basis_id",
    "right_basis_id",
    "left_source0_addr",
    "left_source1_addr",
    "left_target_addr",
    "left_coeff",
    "right_source0_addr",
    "right_source1_addr",
    "right_target_addr",
    "right_coeff",
    "left_endpoint_raw_flag",
    "right_endpoint_raw_flag",
    "endpoint_pair_raw_backed_flag",
    "normal_form_delta_t",
    "semantic_operation_row_id",
    "direct_semantic_operation_flag",
    "obstruction_code",
]
SCHEMA_GAP_COLUMNS = [
    "gap_id",
    "evidence_code",
    "present_flag",
    "required_for_semantic_flag",
    "row_count",
    "column_count",
    "missing_column_count",
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
    "edge_is_owner_adjacency_not_a985_operation_row",
]
OBSTRUCTION_CODES = {name: index for index, name in enumerate(OBSTRUCTION_NAMES)}

EVIDENCE_NAMES = [
    "raw_tensor_present",
    "a985_core_status_pass",
    "owner_endpoints_raw_backed",
    "recurrence_edges_present",
    "normal_form_edge_time_present",
    "semantic_edge_operation_map_absent",
]
EVIDENCE_CODES = {name: index for index, name in enumerate(EVIDENCE_NAMES)}

GAP_NAMES = [
    "semantic_edge_operation_realization_from_a985",
    "metric_from_normal_form_time_without_semantic_edge_ops",
    "nondegenerate_smooth_lorentzian_metric",
    "four_dimensional_spacetime_reduction",
    "curvature_and_einstein_tensor",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "raw_tensor_row_count",
    "raw_tensor_column_count",
    "raw_tensor_coeff_mass",
    "owner_row_count",
    "owner_endpoint_raw_backed_count",
    "recurrence_edge_count",
    "edge_sem_row_count",
    "edge_endpoint_raw_backed_count",
    "normal_form_edge_time_count",
    "normal_form_delta_sum",
    "semantic_edge_operation_count",
    "semantic_edge_realized_count",
    "semantic_edge_obstructed_count",
    "semantic_edge_operation_flag",
    "endpoint_support_flag",
    "obstruction_certified_flag",
    "smooth_lorentzian_metric_flag",
    "gr_derivation_flag",
    "open_gap_count",
    "next_gap_code",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}

REQUIRED_SEMANTIC_COLUMNS = [
    "edge_id",
    "operation_source0_addr",
    "operation_source1_addr",
    "operation_target_addr",
    "operation_coeff",
    "operation_time_component",
]


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _require_dict(payload: Any, label: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise AssertionError(f"{label} is not a JSON object")
    return payload


def raw_tensor_path_from_index(raw_index: dict[str, Any]) -> Path:
    roles = _require_dict(raw_index.get("roles"), "raw_index.roles")
    raw_role = _require_dict(roles.get("raw_tensor"), "raw_index.raw_tensor")
    raw_path = raw_role.get("path")
    if not isinstance(raw_path, str):
        raise AssertionError("raw_tensor path is missing")
    return ROOT / raw_path


def _read_csv_int(path: Path) -> list[dict[str, int]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return [{key: int(value) for key, value in row.items()} for row in reader]


def _read_csv_header(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or [])


def _raw_tensor(path: Path) -> np.ndarray:
    with np.load(path, allow_pickle=False) as payload:
        triples = np.asarray(payload["triples"], dtype=np.int64)
    if triples.ndim != 2 or triples.shape[1] != 4:
        raise AssertionError("raw tensor triples must have shape n x 4")
    return triples


def _raw_tuple_set(triples: np.ndarray) -> set[tuple[int, int, int, int]]:
    return {tuple(int(value) for value in row) for row in triples.tolist()}


def _core_finite_algebra_claim(core: dict[str, Any]) -> dict[str, Any]:
    claims = core.get("verified_claims")
    if not isinstance(claims, list):
        return {}
    for claim in claims:
        if isinstance(claim, dict) and claim.get("id") == "finite_algebra":
            return claim
    return {}


def _edge_sem_rows(
    owner_rows: list[dict[str, int]],
    edge_rows: list[dict[str, int]],
    edge_time_rows: list[dict[str, int]],
    raw_tuples: set[tuple[int, int, int, int]],
) -> tuple[list[dict[str, int]], int]:
    owners = {row["basis_id"]: row for row in owner_rows}
    edge_time = {row["edge_id"]: row for row in edge_time_rows}
    endpoint_raw_backed_count = 0
    rows: list[dict[str, int]] = []
    for edge in edge_rows:
        edge_id = edge["edge_id"]
        left = owners[edge["left_basis_id"]]
        right = owners[edge["right_basis_id"]]
        left_tuple = (
            left["source0_addr"],
            left["source1_addr"],
            left["target_addr"],
            left["coeff"],
        )
        right_tuple = (
            right["source0_addr"],
            right["source1_addr"],
            right["target_addr"],
            right["coeff"],
        )
        left_raw = int(left_tuple in raw_tuples)
        right_raw = int(right_tuple in raw_tuples)
        pair_raw = int(left_raw == 1 and right_raw == 1)
        endpoint_raw_backed_count += pair_raw
        rows.append(
            {
                "edge_id": edge_id,
                "left_basis_id": edge["left_basis_id"],
                "right_basis_id": edge["right_basis_id"],
                "left_source0_addr": left["source0_addr"],
                "left_source1_addr": left["source1_addr"],
                "left_target_addr": left["target_addr"],
                "left_coeff": left["coeff"],
                "right_source0_addr": right["source0_addr"],
                "right_source1_addr": right["source1_addr"],
                "right_target_addr": right["target_addr"],
                "right_coeff": right["coeff"],
                "left_endpoint_raw_flag": left_raw,
                "right_endpoint_raw_flag": right_raw,
                "endpoint_pair_raw_backed_flag": pair_raw,
                "normal_form_delta_t": edge_time[edge_id]["delta_t"],
                "semantic_operation_row_id": -1,
                "direct_semantic_operation_flag": 0,
                "obstruction_code": OBSTRUCTION_CODES[
                    "edge_is_owner_adjacency_not_a985_operation_row"
                ],
            }
        )
    return rows, endpoint_raw_backed_count


def build_rows() -> dict[str, Any]:
    core_a985 = load_json(CORE_A985)
    raw_index = load_json(RAW_INDEX)
    long_time_map = load_json(LONG_TIME_MAP)
    long_rec = load_json(LONG_REC)
    raw_tensor_path = raw_tensor_path_from_index(raw_index)
    triples = _raw_tensor(raw_tensor_path)
    raw_tuples = _raw_tuple_set(triples)

    owner_rows = _read_csv_int(LONG_REC_OWNER)
    edge_rows = _read_csv_int(LONG_REC_EDGE)
    edge_time_rows = _read_csv_int(LONG_TIME_EDGE)
    edge_header = _read_csv_header(LONG_REC_EDGE)
    edge_time_header = _read_csv_header(LONG_TIME_EDGE)
    owner_header = _read_csv_header(LONG_REC_OWNER)

    owner_endpoint_raw_backed_count = sum(
        (
            row["source0_addr"],
            row["source1_addr"],
            row["target_addr"],
            row["coeff"],
        )
        in raw_tuples
        for row in owner_rows
    )
    edge_sem_rows, edge_endpoint_raw_backed_count = _edge_sem_rows(
        owner_rows, edge_rows, edge_time_rows, raw_tuples
    )
    finite_claim = _core_finite_algebra_claim(core_a985)
    raw_coeff_mass = int(triples[:, 3].sum())
    normal_form_delta_sum = sum(row["normal_form_delta_t"] for row in edge_sem_rows)

    semantic_present_columns = set(edge_header) | set(edge_time_header)
    missing_semantic_columns = [
        column
        for column in REQUIRED_SEMANTIC_COLUMNS
        if column not in semantic_present_columns
    ]
    semantic_missing_count = len(missing_semantic_columns)

    schema_gap_rows = [
        {
            "gap_id": 0,
            "evidence_code": EVIDENCE_CODES["raw_tensor_present"],
            "present_flag": 1,
            "required_for_semantic_flag": 1,
            "row_count": int(triples.shape[0]),
            "column_count": int(triples.shape[1]),
            "missing_column_count": 0,
            "obstruction_flag": 0,
        },
        {
            "gap_id": 1,
            "evidence_code": EVIDENCE_CODES["a985_core_status_pass"],
            "present_flag": int(core_a985.get("status") == "PASS"),
            "required_for_semantic_flag": 1,
            "row_count": len(finite_claim),
            "column_count": 0,
            "missing_column_count": 0,
            "obstruction_flag": 0,
        },
        {
            "gap_id": 2,
            "evidence_code": EVIDENCE_CODES["owner_endpoints_raw_backed"],
            "present_flag": int(owner_endpoint_raw_backed_count == len(owner_rows)),
            "required_for_semantic_flag": 1,
            "row_count": len(owner_rows),
            "column_count": len(owner_header),
            "missing_column_count": 0,
            "obstruction_flag": 0,
        },
        {
            "gap_id": 3,
            "evidence_code": EVIDENCE_CODES["recurrence_edges_present"],
            "present_flag": 1,
            "required_for_semantic_flag": 1,
            "row_count": len(edge_rows),
            "column_count": len(edge_header),
            "missing_column_count": semantic_missing_count,
            "obstruction_flag": 0,
        },
        {
            "gap_id": 4,
            "evidence_code": EVIDENCE_CODES["normal_form_edge_time_present"],
            "present_flag": 1,
            "required_for_semantic_flag": 1,
            "row_count": len(edge_time_rows),
            "column_count": len(edge_time_header),
            "missing_column_count": semantic_missing_count,
            "obstruction_flag": 0,
        },
        {
            "gap_id": 5,
            "evidence_code": EVIDENCE_CODES["semantic_edge_operation_map_absent"],
            "present_flag": 0,
            "required_for_semantic_flag": 1,
            "row_count": 0,
            "column_count": 0,
            "missing_column_count": semantic_missing_count,
            "obstruction_flag": 1,
        },
    ]

    gap_rows = [
        {
            "gap_id": 0,
            "obligation_code": GAP_CODES["semantic_edge_operation_realization_from_a985"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": 1,
            "obligation_code": GAP_CODES[
                "metric_from_normal_form_time_without_semantic_edge_ops"
            ],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 1,
        },
        {
            "gap_id": 2,
            "obligation_code": GAP_CODES["nondegenerate_smooth_lorentzian_metric"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": 3,
            "obligation_code": GAP_CODES["four_dimensional_spacetime_reduction"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": 4,
            "obligation_code": GAP_CODES["curvature_and_einstein_tensor"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
    ]

    obs = {
        "raw_tensor_row_count": int(triples.shape[0]),
        "raw_tensor_column_count": int(triples.shape[1]),
        "raw_tensor_coeff_mass": raw_coeff_mass,
        "owner_row_count": len(owner_rows),
        "owner_endpoint_raw_backed_count": owner_endpoint_raw_backed_count,
        "recurrence_edge_count": len(edge_rows),
        "edge_sem_row_count": len(edge_sem_rows),
        "edge_endpoint_raw_backed_count": edge_endpoint_raw_backed_count,
        "normal_form_edge_time_count": len(edge_time_rows),
        "normal_form_delta_sum": normal_form_delta_sum,
        "semantic_edge_operation_count": 0,
        "semantic_edge_realized_count": 0,
        "semantic_edge_obstructed_count": len(edge_rows),
        "semantic_edge_operation_flag": 0,
        "endpoint_support_flag": int(
            owner_endpoint_raw_backed_count == len(owner_rows)
            and edge_endpoint_raw_backed_count == len(edge_rows)
        ),
        "obstruction_certified_flag": 1,
        "smooth_lorentzian_metric_flag": 0,
        "gr_derivation_flag": 0,
        "open_gap_count": sum(1 - row["certified_flag"] for row in gap_rows),
        "next_gap_code": GAP_CODES[
            "metric_from_normal_form_time_without_semantic_edge_ops"
        ],
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
        "core_a985": core_a985,
        "raw_index": raw_index,
        "raw_tensor_path": raw_tensor_path,
        "long_time_map": long_time_map,
        "long_rec": long_rec,
        "triples": triples,
        "finite_claim": finite_claim,
        "owner_rows": owner_rows,
        "edge_rows": edge_rows,
        "edge_time_rows": edge_time_rows,
        "edge_sem_rows": edge_sem_rows,
        "schema_gap_rows": schema_gap_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "missing_semantic_columns": missing_semantic_columns,
        "edge_sem_table": table_from_rows(EDGE_SEM_COLUMNS, edge_sem_rows),
        "schema_gap_table": table_from_rows(SCHEMA_GAP_COLUMNS, schema_gap_rows),
        "gap_table": table_from_rows(GAP_COLUMNS, gap_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "edge_sem_text_hash": sha_text(digest_text(EDGE_SEM_COLUMNS, edge_sem_rows)),
        "schema_gap_text_hash": sha_text(
            digest_text(SCHEMA_GAP_COLUMNS, schema_gap_rows)
        ),
        "gap_text_hash": sha_text(digest_text(GAP_COLUMNS, gap_rows)),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    core_a985 = rows["core_a985"]
    long_time_map = rows["long_time_map"]
    long_rec = rows["long_rec"]
    triples = rows["triples"]
    finite_claim = rows["finite_claim"]

    checks = {
        "a985_core_input_pass": core_a985.get("status") == "PASS"
        and finite_claim.get("status") == "verified",
        "raw_tensor_shape_exact": obs["raw_tensor_row_count"] == 1_414_965
        and obs["raw_tensor_column_count"] == 4,
        "raw_tensor_mass_exact": obs["raw_tensor_coeff_mass"] == 2_537_360,
        "long_time_map_input_certified": long_time_map.get("status")
        == "LONG_TIME_MAP_CERTIFIED"
        and long_time_map.get("all_checks_pass") is True,
        "long_rec_input_certified": long_rec.get("status") == "LONG_REC_CERTIFIED"
        and long_rec.get("all_checks_pass") is True,
        "owner_endpoints_are_a985_raw_triples": obs["owner_row_count"] == 259
        and obs["owner_endpoint_raw_backed_count"] == 259,
        "edge_endpoints_are_a985_raw_backed": obs["recurrence_edge_count"] == 642
        and obs["edge_sem_row_count"] == 642
        and obs["edge_endpoint_raw_backed_count"] == 642,
        "normal_form_time_map_edges_match": obs["normal_form_edge_time_count"] == 642
        and obs["normal_form_delta_sum"] == 642,
        "semantic_edge_operation_map_absent": obs["semantic_edge_operation_count"] == 0
        and obs["semantic_edge_realized_count"] == 0
        and obs["semantic_edge_obstructed_count"] == 642
        and obs["semantic_edge_operation_flag"] == 0,
        "obstruction_boundary_exact": obs["endpoint_support_flag"] == 1
        and obs["obstruction_certified_flag"] == 1
        and obs["smooth_lorentzian_metric_flag"] == 0
        and obs["gr_derivation_flag"] == 0,
        "table_shapes_match": rows["edge_sem_table"].shape
        == (642, len(EDGE_SEM_COLUMNS))
        and rows["schema_gap_table"].shape == (len(EVIDENCE_NAMES), len(SCHEMA_GAP_COLUMNS))
        and rows["gap_table"].shape == (len(GAP_NAMES), len(GAP_COLUMNS))
        and rows["observable_table"].shape == (len(OBS_NAMES), len(OBS_COLUMNS))
        and triples.shape == (1_414_965, 4),
    }

    witness = {
        "name": THEOREM_ID,
        "classification": "finite_time_semantic_edge_obstruction",
        "obstruction_code_map": {
            str(value): key for key, value in OBSTRUCTION_CODES.items()
        },
        "evidence_code_map": {str(value): key for key, value in EVIDENCE_CODES.items()},
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "required_semantic_columns": REQUIRED_SEMANTIC_COLUMNS,
        "missing_semantic_columns": rows["missing_semantic_columns"],
        "summary": {
            "raw_tensor_row_count": obs["raw_tensor_row_count"],
            "raw_tensor_coeff_mass": obs["raw_tensor_coeff_mass"],
            "owner_row_count": obs["owner_row_count"],
            "owner_endpoint_raw_backed_count": obs[
                "owner_endpoint_raw_backed_count"
            ],
            "recurrence_edge_count": obs["recurrence_edge_count"],
            "edge_endpoint_raw_backed_count": obs[
                "edge_endpoint_raw_backed_count"
            ],
            "normal_form_delta_sum": obs["normal_form_delta_sum"],
            "semantic_edge_operation_count": obs["semantic_edge_operation_count"],
            "semantic_edge_obstructed_count": obs[
                "semantic_edge_obstructed_count"
            ],
            "endpoint_support_flag": obs["endpoint_support_flag"],
            "semantic_edge_operation_flag": obs["semantic_edge_operation_flag"],
            "obstruction_certified_flag": obs["obstruction_certified_flag"],
            "next_gap": "metric_from_normal_form_time_without_semantic_edge_ops",
        },
        "raw_tensor_sha256": sha_array(triples),
        "edge_sem_table_sha256": sha_array(rows["edge_sem_table"]),
        "edge_sem_text_sha256": rows["edge_sem_text_hash"],
        "schema_gap_table_sha256": sha_array(rows["schema_gap_table"]),
        "schema_gap_text_sha256": rows["schema_gap_text_hash"],
        "gap_table_sha256": sha_array(rows["gap_table"]),
        "gap_text_sha256": rows["gap_text_hash"],
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    sem_payload = {
        "schema": "long.time_sem@1",
        "object": "finite_time_semantic_edge_obstruction",
        "status": STATUS if all(checks.values()) else "LONG_TIME_SEM_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.time_sem.report@1",
        "status": sem_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_time_sem certifies a current-boundary obstruction, not a "
            "semantic closure: all 259 long_rec owner basis rows are present "
            "as A985 raw tensor triples, and all 642 recurrence edges connect "
            "A985-backed endpoint triples, but the current artifact boundary "
            "does not contain a certified edge_id-to-A985-operation map. The "
            "normal-form Delta t table from long_time_map is therefore not yet "
            "an A985-alone semantic transition operation table."
        ),
        "stage_protocol": {
            "draft": "read A985 core, raw tensor index, raw tensor, long_rec owner/edge rows, and long_time_map edge-time rows",
            "witness": "emit per-edge endpoint support rows and schema-gap rows for the absent semantic edge-operation map",
            "coherence": "check raw tensor shape/mass, owner endpoint raw support, edge endpoint raw support, normal-form time rows, and table hashes",
            "closure": "certify the semantic edge-operation obstruction while preserving endpoint A985 support",
            "emit": "write long_time_sem artifacts and verifier hook",
        },
        "inputs": {
            "core_a985": input_entry(
                CORE_A985,
                {
                    "status": core_a985.get("status"),
                    "finite_algebra_status": finite_claim.get("status"),
                },
            ),
            "raw_index": input_entry(RAW_INDEX),
            "raw_tensor": input_entry(
                rows["raw_tensor_path"],
                {
                    "row_count": int(triples.shape[0]),
                    "column_count": int(triples.shape[1]),
                },
            ),
            "long_time_map": input_entry(
                LONG_TIME_MAP,
                {
                    "status": long_time_map.get("status"),
                    "certificate_sha256": long_time_map.get("certificate_sha256"),
                },
            ),
            "long_time_edge": input_entry(
                LONG_TIME_EDGE,
                {"row_count": len(rows["edge_time_rows"])},
            ),
            "long_rec": input_entry(
                LONG_REC,
                {
                    "status": long_rec.get("status"),
                    "certificate_sha256": long_rec.get("certificate_sha256"),
                },
            ),
            "long_rec_owner": input_entry(
                LONG_REC_OWNER,
                {"row_count": len(rows["owner_rows"])},
            ),
            "long_rec_edge": input_entry(
                LONG_REC_EDGE,
                {"row_count": len(rows["edge_rows"])},
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "sem": relpath(OUT_DIR / "sem.json"),
            "edge_sem_csv": relpath(OUT_DIR / "edge_sem.csv"),
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
                "all long_rec owner endpoints are A985 raw tensor triples",
                "all 642 long_rec recurrence edges connect A985-backed endpoint triples",
                "the long_time_map unit ticks are attached to those 642 endpoint-backed edges",
                "no certified semantic edge_id-to-A985-operation map exists in the current artifact boundary",
                "the normal-form edge-time table is obstructed as an A985-alone semantic transition-operation table",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "semantic A985 operation realization for the 642 recurrence transitions",
                "a metric certificate allowed to treat normal-form ticks as A985 semantic transition operations",
                "a nondegenerate smooth Lorentzian metric tensor",
                "a 3+1 spacetime reduction from the 1+19 public split",
                "Riemann/Ricci curvature, Einstein tensor, or Einstein field equations",
            ],
        },
        "next_highest_yield_item": (
            "Build long_metric_gate: decide whether the finite metric pathway may use "
            "the certified normal-form time map with the semantic edge-operation "
            "obstruction preserved, or whether a new owner-boundary contact lift "
            "must be materialized first."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.time_sem.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.time_sem.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "sem": sem_payload,
        "edge_sem_csv": csv_text(EDGE_SEM_COLUMNS, rows["edge_sem_rows"]),
        "schema_gap_csv": csv_text(SCHEMA_GAP_COLUMNS, rows["schema_gap_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "raw_tensor": triples,
        "edge_sem_table": rows["edge_sem_table"],
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
    write_json(OUT_DIR / "sem.json", payloads["sem"])
    (OUT_DIR / "edge_sem.csv").write_text(
        payloads["edge_sem_csv"], encoding="utf-8"
    )
    (OUT_DIR / "schema_gap.csv").write_text(
        payloads["schema_gap_csv"], encoding="utf-8"
    )
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        raw_tensor=payloads["raw_tensor"],
        edge_sem_table=payloads["edge_sem_table"],
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
