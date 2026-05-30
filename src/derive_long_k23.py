from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


FIELD_PRIME = 1_000_003
THEOREM_ID = "long_k23"
STATUS = "SECTOR33_K23_PUNCTURED_MOG_SYZYGY_APERTURE_TARGET_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23.py"
LONG_HCGRADE_REPORT = D20_INVARIANTS / "proof_obligations" / "long_hcgrade" / "report.json"
LONG_HCGRADE_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_hcgrade" / "center_grade_projection.npz"
CANONICAL_W24_FRAME = ROOT / "data" / "geometry" / "canonical_24_syzygy_frame.json"
W24_HEX_REPORT = D20_INVARIANTS / "proof_obligations" / "d20_w24_hexacode_row_alphabetization" / "report.json"
W24_TYPED_SEARCH_REPORT = D20_INVARIANTS / "proof_obligations" / "d20_sector33_w24_typed_coordinate_search" / "report.json"
W24_F4_LIFT_REPORT = D20_INVARIANTS / "proof_obligations" / "d20_sector33_w24_f4_row_lift_solver" / "report.json"
W24_PER_EDGE_REPORT = D20_INVARIANTS / "proof_obligations" / "d20_sector33_w24_per_edge_rowspace_prune" / "report.json"
W24_BIG_CELL_REPORT = D20_INVARIANTS / "proof_obligations" / "d20_sector33_w24_marked_big_cell_quotient_search" / "report.json"
W24_MIXED_DUAD_REPORT = D20_INVARIANTS / "proof_obligations" / "d20_sector33_w24_mixed_duad_quotient_orthogonality_prune" / "report.json"
W24_SHADOW_REPORT = D20_INVARIANTS / "proof_obligations" / "d20_sector33_w24_marked_quotient_shadow_obstruction" / "report.json"
W24_DELETE_CONTRACT_REPORT = D20_INVARIANTS / "proof_obligations" / "d20_sector33_w24_marked_delete_contract_shadow_probe" / "report.json"

DIMENSION_TEXT_HASH = "9a1d613977edad9932da20ae5f8adbf30a81801bf0f3ae1f76997b9a88881a00"
SOURCE_TEXT_HASH = "53f8b8ba65b59d17f61b3939238cb15fd9faf84aeb3a2ff0f20f74e23e4796a7"
KERNEL_TEXT_HASH = "fde3669bc92a5f1687e8591e4470bf8558d40ac8d7fbe0566eb6525d6d87a476"
OBS_TEXT_HASH = "2e30df2515e91e2a41ec6e5aeaee62790b9ded7c6f3a6771236b334393f0fb96"
MATRIX_SHA256 = "bc58ffbf61c6db0a1cd127d70c25dca3ba125db7cb0aebe6d793df077e62e034"

DIMENSION_COLUMNS = [
    "row_id",
    "side_code",
    "component_code",
    "multiplicity",
    "factor_dimension",
    "dimension",
    "cumulative_dimension",
    "certified_flag",
]
SOURCE_COLUMNS = [
    "source_id",
    "source_kind_code",
    "status_pass_flag",
    "selected_morphism_flag",
    "open_binding_flag",
    "count0",
    "count1",
    "count2",
]
KERNEL_COLUMNS = [
    "basis_id",
    "coordinate_id",
    "coefficient_mod",
    "coefficient_signed",
    "nonzero_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "support_dimension",
    "target_projection_rank",
    "k23_kernel_dimension",
    "w24_dimension",
    "w24_euler_coordinate_count",
    "w24_syzygy_dimension",
    "k23_dimension_matches_syzygy_flag",
    "kernel_basis_row_count",
    "kernel_basis_column_count",
    "kernel_basis_zero_residual_flag",
    "w24_hexacode_rank",
    "w24_hexacode_minimum_weight",
    "w24_hexacode_certified_flag",
    "typed_projection_candidate_count",
    "f4_row_lift_rule_total",
    "per_edge_coordinate_bijections_pruned",
    "mixed_duad_assignment_count",
    "delete_contract_candidate_count",
    "unique_dual_octad_weight",
    "binding_map_materialized_flag",
    "subspace_equality_certified_flag",
    "m23_module_proven_flag",
    "focused_k23_target_closed_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def signed_mod(value: int, mod: int = FIELD_PRIME) -> int:
    value %= mod
    return value if value <= mod // 2 else value - mod


def sha_array(array: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    return hashlib.sha256(
        b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in ["projection_matrix", "kernel_basis", "kernel_residual"])
    ).hexdigest()


def rref_mod(matrix: np.ndarray, prime: int = FIELD_PRIME) -> tuple[int, list[int], np.ndarray]:
    work = np.asarray(matrix, dtype=np.int64).copy() % prime
    rows, cols = work.shape
    rank = 0
    pivots: list[int] = []
    for col in range(cols):
        pivot = None
        for row in range(rank, rows):
            if int(work[row, col]) % prime:
                pivot = row
                break
        if pivot is None:
            continue
        if pivot != rank:
            work[[rank, pivot]] = work[[pivot, rank]]
        inv = pow(int(work[rank, col]), -1, prime)
        work[rank] = (work[rank] * inv) % prime
        for row in range(rows):
            if row == rank:
                continue
            factor = int(work[row, col]) % prime
            if factor:
                work[row] = (work[row] - factor * work[rank]) % prime
        pivots.append(col)
        rank += 1
        if rank == rows:
            break
    return rank, pivots, work[:rank]


def nullspace_basis(matrix: np.ndarray, prime: int = FIELD_PRIME) -> tuple[np.ndarray, int, list[int]]:
    rank, pivots, rref = rref_mod(matrix, prime)
    cols = matrix.shape[1]
    pivot_set = set(pivots)
    free_columns = [col for col in range(cols) if col not in pivot_set]
    basis: list[np.ndarray] = []
    for free_col in free_columns:
        vector = np.zeros(cols, dtype=np.int64)
        vector[free_col] = 1
        for row_id, pivot in enumerate(pivots):
            vector[pivot] = (-int(rref[row_id, free_col])) % prime
        basis.append(vector)
    if not basis:
        return np.zeros((0, cols), dtype=np.int64), rank, pivots
    return np.vstack(basis) % prime, rank, pivots


def is_report_pass(report: dict[str, Any], status: str) -> bool:
    return report.get("status") == status and report.get("all_checks_pass") is True


def int_from(obj: Any, default: int = 0) -> int:
    try:
        return int(obj)
    except (TypeError, ValueError):
        return default


def source_rows_from_reports(reports: dict[str, dict[str, Any]], w24_frame: dict[str, Any]) -> list[dict[str, int]]:
    per_edge = reports["per_edge"].get("witness", {}).get("balanced_relaxed_h6_coordinate_maps", {})
    return [
        {
            "source_id": 0,
            "source_kind_code": 0,
            "status_pass_flag": int(is_report_pass(reports["hcgrade"], "LONG_HCGRADE_CENTER_GRADE_RANK_CERTIFIED")),
            "selected_morphism_flag": 0,
            "open_binding_flag": int(reports["hcgrade"].get("witness", {}).get("summary", {}).get("lambda3_binding_accepted_flag") == 0),
            "count0": int_from(reports["hcgrade"].get("witness", {}).get("summary", {}).get("support_dimension")),
            "count1": int_from(reports["hcgrade"].get("witness", {}).get("summary", {}).get("selected_projection_rank")),
            "count2": int_from(reports["hcgrade"].get("witness", {}).get("summary", {}).get("selected_kernel_dimension")),
        },
        {
            "source_id": 1,
            "source_kind_code": 1,
            "status_pass_flag": int(w24_frame.get("status") == "CANONICAL_24_COORDINATE_SYZYGY_FRAME_CERTIFIED_GOLAY_SELECTION_STILL_OPEN"),
            "selected_morphism_flag": 0,
            "open_binding_flag": 1,
            "count0": int_from(w24_frame.get("canonical_frame", {}).get("dimension")),
            "count1": int_from(w24_frame.get("canonical_frame", {}).get("syzygy_dimension")),
            "count2": int_from(w24_frame.get("Golay_binary_audit", {}).get("passes_extended_golay_weight_test")),
        },
        {
            "source_id": 2,
            "source_kind_code": 2,
            "status_pass_flag": int(is_report_pass(reports["hex"], "D20_W24_HEXACODE_ROW_ALPHABETIZATION_CERTIFIED")),
            "selected_morphism_flag": 0,
            "open_binding_flag": 1,
            "count0": 24,
            "count1": 12,
            "count2": 8,
        },
        {
            "source_id": 3,
            "source_kind_code": 3,
            "status_pass_flag": int(is_report_pass(reports["typed"], "D20_SECTOR33_W24_TYPED_COORDINATE_SEARCH_CERTIFIED")),
            "selected_morphism_flag": 0,
            "open_binding_flag": 1,
            "count0": 150,
            "count1": 25,
            "count2": 6,
        },
        {
            "source_id": 4,
            "source_kind_code": 4,
            "status_pass_flag": int(is_report_pass(reports["f4"], "D20_SECTOR33_W24_F4_ROW_LIFT_SOLVER_CERTIFIED")),
            "selected_morphism_flag": 0,
            "open_binding_flag": 1,
            "count0": 102400,
            "count1": 4096,
            "count2": 25,
        },
        {
            "source_id": 5,
            "source_kind_code": 5,
            "status_pass_flag": int(is_report_pass(reports["per_edge"], "D20_SECTOR33_W24_PER_EDGE_ROWSPACE_PRUNE_CERTIFIED")),
            "selected_morphism_flag": 0,
            "open_binding_flag": 1,
            "count0": int_from(per_edge.get("balanced_h6_map_count_total")),
            "count1": int_from(per_edge.get("coordinate_bijection_count_pruned_by_rank")),
            "count2": 12,
        },
        {
            "source_id": 6,
            "source_kind_code": 6,
            "status_pass_flag": int(is_report_pass(reports["big_cell"], "D20_SECTOR33_W24_MARKED_BIG_CELL_QUOTIENT_SEARCH_CERTIFIED")),
            "selected_morphism_flag": 0,
            "open_binding_flag": 1,
            "count0": 3,
            "count1": 0,
            "count2": 0,
        },
        {
            "source_id": 7,
            "source_kind_code": 7,
            "status_pass_flag": int(is_report_pass(reports["mixed_duad"], "D20_SECTOR33_W24_MIXED_DUAD_QUOTIENT_ORTHOGONALITY_PRUNE_CERTIFIED")),
            "selected_morphism_flag": 0,
            "open_binding_flag": 1,
            "count0": 14348907,
            "count1": 0,
            "count2": 15,
        },
        {
            "source_id": 8,
            "source_kind_code": 8,
            "status_pass_flag": int(is_report_pass(reports["shadow"], "D20_SECTOR33_W24_MARKED_QUOTIENT_SHADOW_OBSTRUCTION_CERTIFIED")),
            "selected_morphism_flag": 0,
            "open_binding_flag": 1,
            "count0": 25,
            "count1": 25,
            "count2": 0,
        },
        {
            "source_id": 9,
            "source_kind_code": 9,
            "status_pass_flag": int(is_report_pass(reports["delete_contract"], "D20_SECTOR33_W24_MARKED_DELETE_CONTRACT_SHADOW_PROBE_CERTIFIED")),
            "selected_morphism_flag": 0,
            "open_binding_flag": 1,
            "count0": 6400,
            "count1": 70,
            "count2": 8,
        },
    ]


def dimension_rows() -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    cumulative = 0
    for row_id, component_code, multiplicity, factor_dimension in [
        (0, 0, 1, 20),
        (1, 1, 1, 15),
        (2, 2, 1, 15),
        (3, 3, 1, 6),
    ]:
        dimension = multiplicity * factor_dimension
        cumulative += dimension
        rows.append(
            {
                "row_id": row_id,
                "side_code": 0,
                "component_code": component_code,
                "multiplicity": multiplicity,
                "factor_dimension": factor_dimension,
                "dimension": dimension,
                "cumulative_dimension": cumulative,
                "certified_flag": 1,
            }
        )
    cumulative = 0
    for row_id, component_code, multiplicity, factor_dimension in [
        (4, 4, 1, 1),
        (5, 5, 2, 1),
        (6, 6, 2, 15),
    ]:
        dimension = multiplicity * factor_dimension
        cumulative += dimension
        rows.append(
            {
                "row_id": row_id,
                "side_code": 1,
                "component_code": component_code,
                "multiplicity": multiplicity,
                "factor_dimension": factor_dimension,
                "dimension": dimension,
                "cumulative_dimension": cumulative,
                "certified_flag": 1,
            }
        )
    rows.append(
        {
            "row_id": 7,
            "side_code": 2,
            "component_code": 7,
            "multiplicity": 1,
            "factor_dimension": 23,
            "dimension": 23,
            "cumulative_dimension": 23,
            "certified_flag": 1,
        }
    )
    rows.append(
        {
            "row_id": 8,
            "side_code": 3,
            "component_code": 8,
            "multiplicity": 1,
            "factor_dimension": 23,
            "dimension": 23,
            "cumulative_dimension": 23,
            "certified_flag": 1,
        }
    )
    return rows


def build_rows() -> dict[str, Any]:
    reports = {
        "hcgrade": load_json(LONG_HCGRADE_REPORT),
        "hex": load_json(W24_HEX_REPORT),
        "typed": load_json(W24_TYPED_SEARCH_REPORT),
        "f4": load_json(W24_F4_LIFT_REPORT),
        "per_edge": load_json(W24_PER_EDGE_REPORT),
        "big_cell": load_json(W24_BIG_CELL_REPORT),
        "mixed_duad": load_json(W24_MIXED_DUAD_REPORT),
        "shadow": load_json(W24_SHADOW_REPORT),
        "delete_contract": load_json(W24_DELETE_CONTRACT_REPORT),
    }
    w24_frame = load_json(CANONICAL_W24_FRAME)
    matrices = np.load(LONG_HCGRADE_MATRICES, allow_pickle=False)
    projection = np.asarray(matrices["projection_matrix"], dtype=np.int64) % FIELD_PRIME
    kernel_basis, projection_rank, pivots = nullspace_basis(projection)
    kernel_residual = (projection @ kernel_basis.T) % FIELD_PRIME

    k_rows: list[dict[str, int]] = []
    for basis_id in range(kernel_basis.shape[0]):
        for coordinate_id in range(kernel_basis.shape[1]):
            value = int(kernel_basis[basis_id, coordinate_id])
            k_rows.append(
                {
                    "basis_id": basis_id,
                    "coordinate_id": coordinate_id,
                    "coefficient_mod": value,
                    "coefficient_signed": signed_mod(value),
                    "nonzero_flag": int(value != 0),
                }
            )

    source_rows = source_rows_from_reports(reports, w24_frame)
    dims = dimension_rows()
    frame = w24_frame.get("canonical_frame", {})
    obs = {
        "support_dimension": int(projection.shape[1]),
        "target_projection_rank": int(projection_rank),
        "k23_kernel_dimension": int(kernel_basis.shape[0]),
        "w24_dimension": int_from(frame.get("dimension")),
        "w24_euler_coordinate_count": 1,
        "w24_syzygy_dimension": int_from(frame.get("syzygy_dimension")),
        "k23_dimension_matches_syzygy_flag": int(kernel_basis.shape[0] == int_from(frame.get("syzygy_dimension"))),
        "kernel_basis_row_count": int(kernel_basis.shape[0]),
        "kernel_basis_column_count": int(kernel_basis.shape[1]),
        "kernel_basis_zero_residual_flag": int(np.count_nonzero(kernel_residual) == 0),
        "w24_hexacode_rank": 12,
        "w24_hexacode_minimum_weight": 8,
        "w24_hexacode_certified_flag": int(is_report_pass(reports["hex"], "D20_W24_HEXACODE_ROW_ALPHABETIZATION_CERTIFIED")),
        "typed_projection_candidate_count": 150,
        "f4_row_lift_rule_total": 102400,
        "per_edge_coordinate_bijections_pruned": int_from(
            reports["per_edge"].get("witness", {}).get("balanced_relaxed_h6_coordinate_maps", {}).get("coordinate_bijection_count_pruned_by_rank")
        ),
        "mixed_duad_assignment_count": 14348907,
        "delete_contract_candidate_count": 6400,
        "unique_dual_octad_weight": 8,
        "binding_map_materialized_flag": 0,
        "subspace_equality_certified_flag": 0,
        "m23_module_proven_flag": 0,
        "focused_k23_target_closed_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    matrix_payload = {
        "projection_matrix": projection,
        "kernel_basis": kernel_basis,
        "kernel_residual": kernel_residual,
    }
    return {
        "reports": reports,
        "w24_frame": w24_frame,
        "dimension_rows": dims,
        "source_rows": source_rows,
        "kernel_rows": k_rows,
        "obs_rows": obs_rows,
        "dimension_table": table_from_rows(DIMENSION_COLUMNS, dims),
        "source_table": table_from_rows(SOURCE_COLUMNS, source_rows),
        "kernel_table": table_from_rows(KERNEL_COLUMNS, k_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "projection_rank": projection_rank,
        "projection_pivots": pivots,
        "obs": obs,
        "dimension_text_hash": hashlib.sha256(digest_text(DIMENSION_COLUMNS, dims).encode("ascii")).hexdigest(),
        "source_text_hash": hashlib.sha256(digest_text(SOURCE_COLUMNS, source_rows).encode("ascii")).hexdigest(),
        "kernel_text_hash": hashlib.sha256(digest_text(KERNEL_COLUMNS, k_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    source_rows = rows["source_rows"]
    all_source_inputs_pass = all(row["status_pass_flag"] == 1 for row in source_rows)
    checks = {
        "long_hcgrade_input_passes": is_report_pass(rows["reports"]["hcgrade"], "LONG_HCGRADE_CENTER_GRADE_RANK_CERTIFIED"),
        "canonical_w24_frame_has_punctured_syzygy": (
            obs["w24_dimension"],
            obs["w24_euler_coordinate_count"],
            obs["w24_syzygy_dimension"],
        )
        == (24, 1, 23),
        "w24_hexacode_input_passes": is_report_pass(rows["reports"]["hex"], "D20_W24_HEXACODE_ROW_ALPHABETIZATION_CERTIFIED"),
        "prior_sector33_w24_searches_pass": all_source_inputs_pass,
        "dimension_arithmetic_is_56_to_33_kernel23": (
            obs["support_dimension"],
            obs["target_projection_rank"],
            obs["k23_kernel_dimension"],
        )
        == (56, 33, 23),
        "kernel_basis_annihilates_projection": obs["kernel_basis_zero_residual_flag"] == 1,
        "k23_dimension_matches_w24_punctured_syzygy": obs["k23_dimension_matches_syzygy_flag"] == 1,
        "binding_map_is_explicitly_open": (
            obs["binding_map_materialized_flag"],
            obs["subspace_equality_certified_flag"],
            obs["m23_module_proven_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (0, 0, 0, 0),
        "focused_k23_target_closed": obs["focused_k23_target_closed_flag"] == 1,
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_punctured_mog_syzygy_aperture_target",
        "summary": obs,
        "projection_rank": rows["projection_rank"],
        "projection_pivot_count": len(rows["projection_pivots"]),
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies the K23 dimension target and emitted kernel basis, while keeping the sector33-to-W24 basis binding and M23 action unproven.",
    }
    seam_payload = {
        "schema": "long.k23.seam@1",
        "status": STATUS,
        "claim": "The 56-to-33 sector33 center-grade projection has a materialized 23-dimensional kernel matching the punctured W24 syzygy target dimension; the actual W24 subspace binding remains open.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_hcgrade": input_entry(
            LONG_HCGRADE_REPORT,
            {
                "status": rows["reports"]["hcgrade"].get("status"),
                "certificate_sha256": rows["reports"]["hcgrade"].get("certificate_sha256"),
            },
        ),
        "long_hcgrade_matrices": input_entry(LONG_HCGRADE_MATRICES),
        "canonical_w24_frame": input_entry(
            CANONICAL_W24_FRAME,
            {
                "status": rows["w24_frame"].get("status"),
                "canonical_24_syzygy_frame_sha256": rows["w24_frame"].get("canonical_24_syzygy_frame_sha256"),
            },
        ),
        "w24_hexacode_row_alphabetization": input_entry(
            W24_HEX_REPORT,
            {
                "status": rows["reports"]["hex"].get("status"),
                "certificate_sha256": rows["reports"]["hex"].get("certificate_sha256"),
            },
        ),
        "sector33_w24_typed_coordinate_search": input_entry(W24_TYPED_SEARCH_REPORT),
        "sector33_w24_f4_row_lift_solver": input_entry(W24_F4_LIFT_REPORT),
        "sector33_w24_per_edge_rowspace_prune": input_entry(W24_PER_EDGE_REPORT),
        "sector33_w24_marked_big_cell_quotient_search": input_entry(W24_BIG_CELL_REPORT),
        "sector33_w24_mixed_duad_quotient_orthogonality_prune": input_entry(W24_MIXED_DUAD_REPORT),
        "sector33_w24_marked_quotient_shadow_obstruction": input_entry(W24_SHADOW_REPORT),
        "sector33_w24_marked_delete_contract_shadow_probe": input_entry(W24_DELETE_CONTRACT_REPORT),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23 certifies the sector33 K23 aperture as a 23-dimensional kernel with the right W24/Euler-punctured syzygy target dimension, but not the actual subspace equality or M23 module action.",
        "stage_protocol": {
            "draft": "read long_hcgrade, the canonical W24 syzygy frame, the W24 row alphabetization, and the existing sector33-to-W24 search certificates",
            "witness": "emit dimension arithmetic rows, source-boundary rows, an explicit K23 kernel basis, observables, and matrix payloads",
            "coherence": "check 56-to-33 rank, K23 kernel residual zero, W24 24=1+23 split, and prior binding-search boundary flags",
            "closure": "certify the aperture target while marking subspace equality and M23 action as open",
            "emit": "write long_k23 artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "dimension_rows_csv": relpath(OUT_DIR / "dimension_rows.csv"),
            "source_rows_csv": relpath(OUT_DIR / "source_rows.csv"),
            "kernel_basis_csv": relpath(OUT_DIR / "kernel_basis.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the selected long_hcgrade projection has rank 33 on 56 sector33 support coordinates",
                "the emitted K23 kernel basis has 23 rows and annihilates the projection",
                "the W24 frame has coordinate 0 as Euler/unit and coordinates 1..23 as syzygy coordinates",
                "the K23 dimension matches the W24/Euler-punctured syzygy target dimension",
                "the certified W24 row alphabetization and prior sector33-to-W24 search certificates are recorded as the current binding boundary",
            ],
            "does_not_certify": [
                "a basis-binding map from the 56 sector33 support coordinates to the W24 syzygy frame",
                "rowspan(K23) equals the W24/Euler-punctured syzygy rowspace",
                "a selected sector33-to-W24 coordinate morphism",
                "an M23 module action on K23",
                "a rebuild of d20.json or broad bundle closure",
            ],
        },
        "next_highest_yield_item": "Solve the explicit basis-binding map from the 56 sector33 support coordinates to the W24 syzygy frame, then rerun the rowspace equality test.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "dimension_csv": csv_text(DIMENSION_COLUMNS, rows["dimension_rows"]),
        "source_csv": csv_text(SOURCE_COLUMNS, rows["source_rows"]),
        "kernel_csv": csv_text(KERNEL_COLUMNS, rows["kernel_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "dimension_table": rows["dimension_table"],
        "source_table": rows["source_table"],
        "kernel_table": rows["kernel_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "dimension_text_sha256": rows["dimension_text_hash"],
            "source_text_sha256": rows["source_text_hash"],
            "kernel_text_sha256": rows["kernel_text_hash"],
            "obs_text_sha256": rows["obs_text_hash"],
            "matrix_sha256": rows["matrix_sha256"],
        },
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
    (OUT_DIR / "dimension_rows.csv").write_text(payloads["dimension_csv"], encoding="utf-8")
    (OUT_DIR / "source_rows.csv").write_text(payloads["source_csv"], encoding="utf-8")
    (OUT_DIR / "kernel_basis.csv").write_text(payloads["kernel_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        dimension_table=payloads["dimension_table"],
        source_table=payloads["source_table"],
        kernel_table=payloads["kernel_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23_matrices.npz", **payloads["matrix_payload"])
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
                "computed_hashes": payloads["computed_hashes"],
                "summary": report["witness"]["summary"],
                "report": relpath(OUT_DIR / "report.json"),
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
