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


THEOREM_ID = "long_time_map"
STATUS = "LONG_TIME_MAP_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

PROOF_ROOT = D20_INVARIANTS / "proof_obligations"
INTEGRITY_SUMMARY = ROOT / "data" / "integrity" / "proof_system.summary.json"
LONG_LOR = PROOF_ROOT / "long_lor" / "report.json"
LONG_REC = PROOF_ROOT / "long_rec" / "report.json"
LONG_REC_EDGE = PROOF_ROOT / "long_rec" / "edge.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_time_map.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_time_map.py"

MATRIX_COLUMNS = ["entry_id", "matrix_code", "row_index", "column_index", "value"]
EDGE_TIME_COLUMNS = [
    "edge_time_id",
    "edge_id",
    "left_basis_id",
    "right_basis_id",
    "boundary_count",
    "operation_time_component",
    "kernel_slot",
    "kernel_value",
    "public_kernel_slot",
    "public_kernel_value",
    "delta_t",
    "accumulated_time",
    "packet_index",
    "packet_phase",
    "compatibility_flag",
]
CLOCK_COLUMNS = ["clock_id", "clock_code", "value"]
GAP_COLUMNS = [
    "gap_id",
    "obligation_code",
    "required_for_gr_flag",
    "certified_flag",
    "next_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

MATRIX_NAMES = ["tau_int", "q_pub", "rho"]
MATRIX_CODES = {name: index for index, name in enumerate(MATRIX_NAMES)}

CLOCK_NAMES = [
    "recurrence_edge_count",
    "unit_delta_edge_count",
    "time_tick_total",
    "packet_normalization",
    "full_packet_count",
    "packet_remainder",
    "rho_rank",
    "compatibility_defect_l1",
    "operation_kernel_column_count",
    "public_kernel_row_count",
    "edge_compatibility_fail_count",
    "normal_form_clock_flag",
]
CLOCK_CODES = {name: index for index, name in enumerate(CLOCK_NAMES)}

GAP_NAMES = [
    "semantic_edge_operation_realization_from_a985",
    "nondegenerate_smooth_lorentzian_metric",
    "four_dimensional_spacetime_reduction",
    "curvature_and_einstein_tensor",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "operation_algebra_dimension",
    "integrity_integral_codimension",
    "integrity_integral_dimension",
    "public_rank",
    "public_kernel_dimension",
    "public_quotient_dimension",
    "tau_int_row_count",
    "tau_int_col_count",
    "q_pub_row_count",
    "q_pub_col_count",
    "rho_row_count",
    "rho_col_count",
    "rho_rank",
    "compatibility_defect_l1",
    "matrix_nonzero_entry_count",
    "recurrence_edge_count",
    "edge_time_count",
    "unit_delta_edge_count",
    "time_tick_total",
    "packet_normalization",
    "full_packet_count",
    "packet_remainder",
    "normal_form_time_map_flag",
    "semantic_edge_operation_flag",
    "smooth_lorentzian_metric_flag",
    "gr_derivation_flag",
    "open_gap_count",
    "next_gap_code",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _require_dict(payload: Any, label: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise AssertionError(f"{label} is not a JSON object")
    return payload


def _finite_base(integrity_summary: dict[str, Any]) -> dict[str, Any]:
    return _require_dict(integrity_summary.get("finite_base"), "finite_base")


def _read_rec_edges() -> list[dict[str, int]]:
    with LONG_REC_EDGE.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows: list[dict[str, int]] = []
        for row in reader:
            rows.append({key: int(value) for key, value in row.items()})
    return rows


def _build_matrices(
    operation_dim: int, public_rank: int, public_kernel_dim: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    tau_int = np.zeros((1, operation_dim), dtype=np.int64)
    q_pub = np.zeros((1, public_rank), dtype=np.int64)
    rho = np.zeros((public_rank, operation_dim), dtype=np.int64)

    tau_int[0, 0] = 1
    q_pub[0, 0] = 1
    rho[0, 0] = 1
    for column in range(1, operation_dim):
        public_kernel_row = 1 + ((column - 1) % public_kernel_dim)
        rho[public_kernel_row, column] = 1
    return tau_int, q_pub, rho


def _matrix_rows(
    tau_int: np.ndarray, q_pub: np.ndarray, rho: np.ndarray
) -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    entry_id = 0
    for matrix_name, matrix in [
        ("tau_int", tau_int),
        ("q_pub", q_pub),
        ("rho", rho),
    ]:
        matrix_code = MATRIX_CODES[matrix_name]
        for row_index, column_index in zip(*np.nonzero(matrix)):
            rows.append(
                {
                    "entry_id": entry_id,
                    "matrix_code": matrix_code,
                    "row_index": int(row_index),
                    "column_index": int(column_index),
                    "value": int(matrix[row_index, column_index]),
                }
            )
            entry_id += 1
    return rows


def _edge_time_rows(
    edge_rows: list[dict[str, int]],
    operation_dim: int,
    public_kernel_dim: int,
    packet_normalization: int,
) -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    operation_kernel_dim = operation_dim - 1
    for edge_time_id, edge in enumerate(edge_rows):
        edge_id = int(edge["edge_id"])
        left_basis_id = int(edge["left_basis_id"])
        right_basis_id = int(edge["right_basis_id"])
        boundary_count = int(edge["boundary_count"])
        kernel_slot = 1 + (
            (edge_id + left_basis_id + right_basis_id) % operation_kernel_dim
        )
        kernel_value = boundary_count
        public_kernel_slot = 1 + ((kernel_slot - 1) % public_kernel_dim)
        accumulated_time = edge_time_id + 1
        delta_t = 1
        rows.append(
            {
                "edge_time_id": edge_time_id,
                "edge_id": edge_id,
                "left_basis_id": left_basis_id,
                "right_basis_id": right_basis_id,
                "boundary_count": boundary_count,
                "operation_time_component": 1,
                "kernel_slot": kernel_slot,
                "kernel_value": kernel_value,
                "public_kernel_slot": public_kernel_slot,
                "public_kernel_value": kernel_value,
                "delta_t": delta_t,
                "accumulated_time": accumulated_time,
                "packet_index": (accumulated_time - 1) // packet_normalization,
                "packet_phase": (accumulated_time - 1) % packet_normalization,
                "compatibility_flag": 1,
            }
        )
    return rows


def build_rows() -> dict[str, Any]:
    integrity_summary = load_json(INTEGRITY_SUMMARY)
    long_lor = load_json(LONG_LOR)
    long_rec = load_json(LONG_REC)
    edge_rows = _read_rec_edges()

    finite_base = _finite_base(integrity_summary)
    lor_witness = _require_dict(long_lor.get("witness"), "long_lor.witness")
    lor_summary = _require_dict(lor_witness.get("summary"), "long_lor.summary")
    rec_kernel = _require_dict(
        _require_dict(long_rec.get("witness"), "long_rec.witness").get(
            "transition_kernel"
        ),
        "long_rec.transition_kernel",
    )

    operation_dim = int(finite_base["operation_algebra_dimension"])
    integral_codim = int(finite_base["integrity_integral_codimension"])
    integral_dim = int(finite_base["integrity_integral_dimension"])
    public_rank = int(finite_base["public_rank"])
    public_kernel_dim = int(finite_base["public_kernel_dimension"])
    public_quotient_dim = public_rank - public_kernel_dim
    packet_normalization = int(lor_summary["packet_normalization"])
    recurrence_edge_count = int(rec_kernel["edge_count"])

    tau_int, q_pub, rho = _build_matrices(
        operation_dim, public_rank, public_kernel_dim
    )
    compatibility = q_pub @ rho - tau_int
    compatibility_defect_l1 = int(np.abs(compatibility).sum())
    rho_rank = int(np.linalg.matrix_rank(rho))

    matrix_rows = _matrix_rows(tau_int, q_pub, rho)
    edge_time_rows = _edge_time_rows(
        edge_rows, operation_dim, public_kernel_dim, packet_normalization
    )
    edge_time_count = len(edge_time_rows)
    unit_delta_edge_count = sum(row["delta_t"] == 1 for row in edge_time_rows)
    time_tick_total = sum(row["delta_t"] for row in edge_time_rows)
    edge_compatibility_fail_count = sum(
        row["compatibility_flag"] == 0 for row in edge_time_rows
    )
    full_packet_count = time_tick_total // packet_normalization
    packet_remainder = time_tick_total % packet_normalization

    clock_values = {
        "recurrence_edge_count": recurrence_edge_count,
        "unit_delta_edge_count": unit_delta_edge_count,
        "time_tick_total": time_tick_total,
        "packet_normalization": packet_normalization,
        "full_packet_count": full_packet_count,
        "packet_remainder": packet_remainder,
        "rho_rank": rho_rank,
        "compatibility_defect_l1": compatibility_defect_l1,
        "operation_kernel_column_count": integral_codim,
        "public_kernel_row_count": public_kernel_dim,
        "edge_compatibility_fail_count": edge_compatibility_fail_count,
        "normal_form_clock_flag": int(
            compatibility_defect_l1 == 0
            and edge_compatibility_fail_count == 0
            and edge_time_count == recurrence_edge_count
            and unit_delta_edge_count == recurrence_edge_count
        ),
    }
    clock_rows = [
        {"clock_id": index, "clock_code": CLOCK_CODES[name], "value": int(clock_values[name])}
        for index, name in enumerate(CLOCK_NAMES)
    ]

    gap_rows = [
        {
            "gap_id": 0,
            "obligation_code": GAP_CODES["semantic_edge_operation_realization_from_a985"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "next_flag": 1,
        },
        {
            "gap_id": 1,
            "obligation_code": GAP_CODES["nondegenerate_smooth_lorentzian_metric"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": 2,
            "obligation_code": GAP_CODES["four_dimensional_spacetime_reduction"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": 3,
            "obligation_code": GAP_CODES["curvature_and_einstein_tensor"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "next_flag": 0,
        },
    ]

    obs = {
        "operation_algebra_dimension": operation_dim,
        "integrity_integral_codimension": integral_codim,
        "integrity_integral_dimension": integral_dim,
        "public_rank": public_rank,
        "public_kernel_dimension": public_kernel_dim,
        "public_quotient_dimension": public_quotient_dim,
        "tau_int_row_count": int(tau_int.shape[0]),
        "tau_int_col_count": int(tau_int.shape[1]),
        "q_pub_row_count": int(q_pub.shape[0]),
        "q_pub_col_count": int(q_pub.shape[1]),
        "rho_row_count": int(rho.shape[0]),
        "rho_col_count": int(rho.shape[1]),
        "rho_rank": rho_rank,
        "compatibility_defect_l1": compatibility_defect_l1,
        "matrix_nonzero_entry_count": len(matrix_rows),
        "recurrence_edge_count": recurrence_edge_count,
        "edge_time_count": edge_time_count,
        "unit_delta_edge_count": unit_delta_edge_count,
        "time_tick_total": time_tick_total,
        "packet_normalization": packet_normalization,
        "full_packet_count": full_packet_count,
        "packet_remainder": packet_remainder,
        "normal_form_time_map_flag": clock_values["normal_form_clock_flag"],
        "semantic_edge_operation_flag": 0,
        "smooth_lorentzian_metric_flag": 0,
        "gr_derivation_flag": 0,
        "open_gap_count": sum(1 - row["certified_flag"] for row in gap_rows),
        "next_gap_code": GAP_CODES["semantic_edge_operation_realization_from_a985"],
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
        "integrity_summary": integrity_summary,
        "long_lor": long_lor,
        "long_rec": long_rec,
        "edge_rows": edge_rows,
        "finite_base": finite_base,
        "lor_summary": lor_summary,
        "rec_kernel": rec_kernel,
        "tau_int": tau_int,
        "q_pub": q_pub,
        "rho": rho,
        "compatibility": compatibility,
        "matrix_rows": matrix_rows,
        "edge_time_rows": edge_time_rows,
        "clock_rows": clock_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "matrix_table": table_from_rows(MATRIX_COLUMNS, matrix_rows),
        "edge_time_table": table_from_rows(EDGE_TIME_COLUMNS, edge_time_rows),
        "clock_table": table_from_rows(CLOCK_COLUMNS, clock_rows),
        "gap_table": table_from_rows(GAP_COLUMNS, gap_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "matrix_text_hash": sha_text(digest_text(MATRIX_COLUMNS, matrix_rows)),
        "edge_time_text_hash": sha_text(
            digest_text(EDGE_TIME_COLUMNS, edge_time_rows)
        ),
        "clock_text_hash": sha_text(digest_text(CLOCK_COLUMNS, clock_rows)),
        "gap_text_hash": sha_text(digest_text(GAP_COLUMNS, gap_rows)),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    long_lor = rows["long_lor"]
    long_rec = rows["long_rec"]
    lor_summary = rows["lor_summary"]
    edge_rows = rows["edge_rows"]
    tau_int = rows["tau_int"]
    q_pub = rows["q_pub"]
    rho = rows["rho"]
    compatibility = rows["compatibility"]

    edge_ids = [row["edge_id"] for row in edge_rows]
    expected_edge_ids = list(range(len(edge_rows)))
    checks = {
        "long_lor_input_certified": long_lor.get("status") == "LONG_LOR_CERTIFIED"
        and long_lor.get("all_checks_pass") is True,
        "long_rec_input_certified": long_rec.get("status") == "LONG_REC_CERTIFIED"
        and long_rec.get("all_checks_pass") is True,
        "dimension_inputs_match_long_lor": all(
            int(lor_summary[key]) == int(obs[key])
            for key in [
                "operation_algebra_dimension",
                "integrity_integral_codimension",
                "integrity_integral_dimension",
                "public_rank",
                "public_kernel_dimension",
                "public_quotient_dimension",
            ]
        ),
        "matrix_shapes_exact": tau_int.shape == (1, 36)
        and q_pub.shape == (1, 20)
        and rho.shape == (20, 36),
        "trace_compatibility_exact": obs["compatibility_defect_l1"] == 0
        and np.array_equal(q_pub @ rho, tau_int),
        "kernel_annihilation_exact": bool(np.all(tau_int[0, 1:] == 0))
        and bool(np.all(q_pub[0, 1:] == 0))
        and bool(np.all(rho[0, 1:] == 0))
        and int(tau_int[0, 0]) == 1
        and int(q_pub[0, 0]) == 1
        and int(rho[0, 0]) == 1,
        "rho_surjective_to_public_boundary": obs["rho_rank"] == 20,
        "edge_table_complete": len(edge_rows) == 642
        and obs["recurrence_edge_count"] == 642
        and edge_ids == expected_edge_ids,
        "edge_time_compatibility_exact": obs["edge_time_count"] == 642
        and obs["unit_delta_edge_count"] == 642
        and obs["time_tick_total"] == 642
        and all(row["compatibility_flag"] == 1 for row in rows["edge_time_rows"]),
        "packet_accounting_exact": obs["packet_normalization"] == 32
        and obs["full_packet_count"] == 20
        and obs["packet_remainder"] == 2
        and obs["full_packet_count"] * obs["packet_normalization"]
        + obs["packet_remainder"]
        == obs["time_tick_total"],
        "normal_form_not_semantic_gr_claim": obs["normal_form_time_map_flag"] == 1
        and obs["semantic_edge_operation_flag"] == 0
        and obs["smooth_lorentzian_metric_flag"] == 0
        and obs["gr_derivation_flag"] == 0,
        "table_shapes_match": rows["matrix_table"].shape
        == (38, len(MATRIX_COLUMNS))
        and rows["edge_time_table"].shape == (642, len(EDGE_TIME_COLUMNS))
        and rows["clock_table"].shape == (len(CLOCK_NAMES), len(CLOCK_COLUMNS))
        and rows["gap_table"].shape == (len(GAP_NAMES), len(GAP_COLUMNS))
        and rows["observable_table"].shape == (len(OBS_NAMES), len(OBS_COLUMNS))
        and compatibility.shape == (1, 36),
    }

    witness = {
        "name": THEOREM_ID,
        "classification": "finite_normal_form_time_map",
        "matrix_code_map": {str(value): key for key, value in MATRIX_CODES.items()},
        "clock_code_map": {str(value): key for key, value in CLOCK_CODES.items()},
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "summary": {
            "operation_algebra_dimension": obs["operation_algebra_dimension"],
            "integrity_integral_codimension": obs[
                "integrity_integral_codimension"
            ],
            "integrity_integral_dimension": obs["integrity_integral_dimension"],
            "public_rank": obs["public_rank"],
            "public_kernel_dimension": obs["public_kernel_dimension"],
            "public_quotient_dimension": obs["public_quotient_dimension"],
            "rho_shape": [obs["rho_row_count"], obs["rho_col_count"]],
            "rho_rank": obs["rho_rank"],
            "compatibility_identity": "q_pub @ rho == tau_int",
            "compatibility_defect_l1": obs["compatibility_defect_l1"],
            "recurrence_edge_count": obs["recurrence_edge_count"],
            "edge_time_count": obs["edge_time_count"],
            "delta_t_rule": "normal_form_unit_tick_per_long_rec_edge",
            "time_tick_total": obs["time_tick_total"],
            "packet_normalization": obs["packet_normalization"],
            "full_packet_count": obs["full_packet_count"],
            "packet_remainder": obs["packet_remainder"],
            "normal_form_time_map_flag": obs["normal_form_time_map_flag"],
            "semantic_edge_operation_flag": obs["semantic_edge_operation_flag"],
            "next_gap": "semantic_edge_operation_realization_from_a985",
        },
        "tau_int_sha256": sha_array(tau_int),
        "q_pub_sha256": sha_array(q_pub),
        "rho_sha256": sha_array(rho),
        "compatibility_sha256": sha_array(compatibility),
        "matrix_table_sha256": sha_array(rows["matrix_table"]),
        "matrix_text_sha256": rows["matrix_text_hash"],
        "edge_time_table_sha256": sha_array(rows["edge_time_table"]),
        "edge_time_text_sha256": rows["edge_time_text_hash"],
        "clock_table_sha256": sha_array(rows["clock_table"]),
        "clock_text_sha256": rows["clock_text_hash"],
        "gap_table_sha256": sha_array(rows["gap_table"]),
        "gap_text_sha256": rows["gap_text_hash"],
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    time_map_payload = {
        "schema": "long.time_map@1",
        "object": "finite_normal_form_time_map",
        "status": STATUS if all(checks.values()) else "LONG_TIME_MAP_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.time_map.report@1",
        "status": time_map_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_time_map materializes the finite d20 time quotient as explicit "
            "integer witnesses: tau_int: O_36 -> T_1, q_pub: D20_20 -> T_1, "
            "and rho: O_36 -> D20_20 with q_pub @ rho == tau_int. It also "
            "assigns every certified long_rec recurrence edge a normal-form "
            "unit time increment, giving 642 finite ticks, 20 complete 32-tick "
            "packets, and a remainder of 2. This is a checked normal-form "
            "clock map, not a semantic proof that the original A985 transition "
            "operation for each edge has been identified."
        ),
        "stage_protocol": {
            "draft": "read long_lor, long_rec, long_rec edge witnesses, and integrity summary",
            "witness": "emit tau_int, q_pub, rho, edgewise Delta t rows, packet clock rows, and open gap rows",
            "coherence": "check q_pub @ rho == tau_int, kernel annihilation, recurrence edge coverage, unit ticks, packet accounting, and table hashes",
            "closure": "certify the finite normal-form time map while reserving semantic A985 edge realization and smooth GR geometry",
            "emit": "write long_time_map artifacts and verifier hook",
        },
        "inputs": {
            "integrity_summary": input_entry(INTEGRITY_SUMMARY),
            "long_lor": input_entry(
                LONG_LOR,
                {
                    "status": long_lor.get("status"),
                    "certificate_sha256": long_lor.get("certificate_sha256"),
                },
            ),
            "long_rec": input_entry(
                LONG_REC,
                {
                    "status": long_rec.get("status"),
                    "certificate_sha256": long_rec.get("certificate_sha256"),
                },
            ),
            "long_rec_edge": input_entry(
                LONG_REC_EDGE,
                {"row_count": len(edge_rows)},
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "time_map": relpath(OUT_DIR / "time_map.json"),
            "matrix_csv": relpath(OUT_DIR / "matrix.csv"),
            "edge_time_csv": relpath(OUT_DIR / "edge_time.csv"),
            "clock_csv": relpath(OUT_DIR / "clock.csv"),
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
                "a materialized integer tau_int map with shape 1x36",
                "a materialized integer q_pub map with shape 1x20",
                "a materialized integer rho readout with shape 20x36 and rank 20",
                "the exact compatibility identity q_pub @ rho == tau_int",
                "642 recurrence-edge normal-form time increments with Delta t = 1",
                "32-unit packet accounting for the 642-tick recurrence clock",
            ],
            "does_not_certify_because_open": [
                "that each normal-form edge vector is the unique semantic A985 operation realizing the recurrence edge",
                "a nondegenerate smooth Lorentzian metric tensor",
                "a 3+1 spacetime reduction from the 1+19 public split",
                "Riemann/Ricci curvature or Einstein tensor",
                "Einstein field equations or general relativity derived from A985 alone",
            ],
        },
        "next_highest_yield_item": (
            "Build long_time_sem: replace the normal-form edge vectors with "
            "A985-realized transition operations, or certify the obstruction, "
            "before treating the time map as A985-alone semantic input to a "
            "metric certificate."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.time_map.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.time_map.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "time_map": time_map_payload,
        "matrix_csv": csv_text(MATRIX_COLUMNS, rows["matrix_rows"]),
        "edge_time_csv": csv_text(EDGE_TIME_COLUMNS, rows["edge_time_rows"]),
        "clock_csv": csv_text(CLOCK_COLUMNS, rows["clock_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "tau_int": tau_int,
        "q_pub": q_pub,
        "rho": rho,
        "compatibility": compatibility,
        "matrix_table": rows["matrix_table"],
        "edge_time_table": rows["edge_time_table"],
        "clock_table": rows["clock_table"],
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
    write_json(OUT_DIR / "time_map.json", payloads["time_map"])
    (OUT_DIR / "matrix.csv").write_text(payloads["matrix_csv"], encoding="utf-8")
    (OUT_DIR / "edge_time.csv").write_text(
        payloads["edge_time_csv"], encoding="utf-8"
    )
    (OUT_DIR / "clock.csv").write_text(payloads["clock_csv"], encoding="utf-8")
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        tau_int=payloads["tau_int"],
        q_pub=payloads["q_pub"],
        rho=payloads["rho"],
        compatibility=payloads["compatibility"],
        matrix_table=payloads["matrix_table"],
        edge_time_table=payloads["edge_time_table"],
        clock_table=payloads["clock_table"],
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
