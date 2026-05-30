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


THEOREM_ID = "long_k23fam"
STATUS = "SECTOR33_K23_MINIMAL_REPAIRED_PROJECTION_FAMILY_OBSTRUCTED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PRIME = 1_000_003

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23fam.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23fam.py"
LONG_K23CL_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23cl" / "report.json"
LONG_K23CL_CLOSURE_ROWS = D20_INVARIANTS / "proof_obligations" / "long_k23cl" / "closure_rows.csv"
LONG_K23CL_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23cl" / "k23cl_matrices.npz"
LONG_K23UNIT_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23unit" / "report.json"
LONG_K23UNIT_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23unit" / "k23unit_matrices.npz"
LONG_K23TGT_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23tgt" / "report.json"
LONG_K23PROJ_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23proj" / "report.json"
LONG_K23RH_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23rh" / "report.json"
LONG_K23RH_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23rh" / "k23rh_matrices.npz"

CANDIDATE_TEXT_HASH = "8199118537939d612c2a15e518957a0ad9c1090b73c58be9b1569feb48680bff"
GENERATOR_TEXT_HASH = "3228e823b2710a811af8da5fa1038bb9e7ca8518d4ba15becc182c97118b74d4"
OBS_TEXT_HASH = "9f9bee2f29853477155153c6e573f364d413f63ca0aab7906d96b78a10a679f1"
MATRIX_SHA256 = "bb527da75e9f239db51e42a2be40c67ce23310db51304fb4097ee11ec6d01e4a"

CANDIDATE_COLUMNS = [
    "candidate_id",
    "fixed_target_row",
    "changed_unit_column",
    "changed_unit_relation",
    "appended_column",
    "appended_relation",
    "appended_target_row",
    "unit_repaired_base_rank",
    "repaired_projection_rank",
    "kernel_dimension",
    "quotient_residual_total",
    "unit_residual_total",
    "product_residual_total",
    "product_residual_min",
    "product_residual_max",
    "product_preserved_generator_count",
]
GENERATOR_COLUMNS = [
    "candidate_id",
    "generator_id",
    "quotient_intertwiner_residual_nonzero_count",
    "unit_residual_nonzero_count",
    "product_residual_nonzero_count",
    "product_preserved_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_k23cl_certified_flag",
    "long_k23unit_certified_flag",
    "long_k23tgt_certified_flag",
    "long_k23proj_certified_flag",
    "long_k23rh_certified_flag",
    "closure_dimension",
    "target_dimension",
    "fixed_target_row_count",
    "old_unit_column_count",
    "appended_column_count",
    "raw_candidate_count",
    "rank_restoring_candidate_count",
    "generator_count",
    "candidate_generator_row_count",
    "quotient_residual_total",
    "unit_residual_total",
    "product_residual_total_min",
    "product_residual_total_max",
    "best_candidate_id",
    "best_candidate_product_residual_total",
    "product_preserved_candidate_count",
    "product_obstructed_candidate_count",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def rref(matrix: np.ndarray, prime: int = PRIME) -> tuple[np.ndarray, int, list[int]]:
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
        inv = pow(int(work[rank, col]), prime - 2, prime)
        work[rank] = (work[rank] * inv) % prime
        for row in np.nonzero(work[:, col])[0]:
            if row != rank:
                work[row] = (work[row] - int(work[row, col]) * work[rank]) % prime
        pivots.append(col)
        rank += 1
        if rank == rows:
            break
    return work, rank, pivots


def rank_mod(matrix: np.ndarray) -> int:
    _echelon, rank, _pivots = rref(matrix)
    return rank


def nullspace_basis(matrix: np.ndarray) -> np.ndarray:
    echelon, _rank, pivots = rref(matrix)
    cols = matrix.shape[1]
    free_cols = [col for col in range(cols) if col not in pivots]
    basis = []
    for free_col in free_cols:
        vector = np.zeros(cols, dtype=np.int64)
        vector[free_col] = 1
        for row, pivot_col in reversed(list(enumerate(pivots))):
            tail = int(np.dot(echelon[row, pivot_col + 1 :], vector[pivot_col + 1 :]) % PRIME)
            vector[pivot_col] = (-tail) % PRIME
        basis.append(vector)
    return np.asarray(basis, dtype=np.int64)


def invert_square(matrix: np.ndarray) -> np.ndarray:
    size = matrix.shape[0]
    augmented = np.hstack([np.asarray(matrix, dtype=np.int64) % PRIME, np.eye(size, dtype=np.int64)])
    rank = 0
    for col in range(size):
        pivot = None
        for row in range(rank, size):
            if int(augmented[row, col]) % PRIME:
                pivot = row
                break
        if pivot is None:
            raise AssertionError("matrix is singular")
        if pivot != rank:
            augmented[[rank, pivot]] = augmented[[pivot, rank]]
        inv = pow(int(augmented[rank, col]), PRIME - 2, PRIME)
        augmented[rank] = (augmented[rank] * inv) % PRIME
        for row in np.nonzero(augmented[:, col])[0]:
            if row != rank:
                augmented[row] = (augmented[row] - int(augmented[row, col]) * augmented[rank]) % PRIME
        rank += 1
    return augmented[:, size:]


def right_inverse(projection: np.ndarray) -> np.ndarray:
    _echelon, rank, pivots = rref(projection)
    if rank != projection.shape[0]:
        raise AssertionError("projection is not full rank")
    pivot_inverse = invert_square(projection[:, pivots])
    result = np.zeros((projection.shape[1], projection.shape[0]), dtype=np.int64)
    result[pivots, :] = pivot_inverse
    return result


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = [
        "candidate_table",
        "generator_table",
        "candidate_product_residual_vector",
        "observable_vector",
    ]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def build_rows() -> dict[str, Any]:
    long_k23cl = load_json(LONG_K23CL_REPORT)
    long_k23unit = load_json(LONG_K23UNIT_REPORT)
    long_k23tgt = load_json(LONG_K23TGT_REPORT)
    long_k23proj = load_json(LONG_K23PROJ_REPORT)
    long_k23rh = load_json(LONG_K23RH_REPORT)
    closure_rows = [{key: int(value) for key, value in row.items()} for row in read_csv_rows(LONG_K23CL_CLOSURE_ROWS)]
    relation_by_row = {row["closure_row_id"]: row["relation_id"] for row in closure_rows}
    with np.load(LONG_K23CL_MATRICES, allow_pickle=False) as matrices:
        product_tensor = np.asarray(matrices["closure_product_tensor"], dtype=np.int64) % PRIME
    with np.load(LONG_K23UNIT_MATRICES, allow_pickle=False) as matrices:
        unit_vector = np.asarray(matrices["unit_vector"], dtype=np.int64) % PRIME
    with np.load(LONG_K23RH_MATRICES, allow_pickle=False) as matrices:
        old_projection = np.asarray(matrices["projection_matrix"], dtype=np.int64) % PRIME
        r_foam_matrices = np.asarray(matrices["r_foam_matrices"], dtype=np.int64) % PRIME

    projection = np.zeros((old_projection.shape[0], product_tensor.shape[0]), dtype=np.int64)
    projection[:, : old_projection.shape[1]] = old_projection
    projected_unit = (projection @ unit_vector) % PRIME

    fixed_target_rows = [0, 1, 17]
    old_unit_columns = [8, 14]
    appended_columns = [56, 57, 58, 59]
    candidate_rows = []
    generator_rows = []
    candidate_product_totals = []
    raw_candidate_count = 0
    candidate_id = 0
    for fixed_target_row in fixed_target_rows:
        fixed_unit = np.zeros(projection.shape[0], dtype=np.int64)
        fixed_unit[fixed_target_row] = 1
        delta = (fixed_unit - projected_unit) % PRIME
        for changed_unit_column in old_unit_columns:
            unit_repaired_base = projection.copy()
            unit_repaired_base[:, changed_unit_column] = (
                unit_repaired_base[:, changed_unit_column] + delta
            ) % PRIME
            base_rank = rank_mod(unit_repaired_base)
            for appended_column in appended_columns:
                for appended_target_row in range(projection.shape[0]):
                    raw_candidate_count += 1
                    repaired_projection = unit_repaired_base.copy()
                    repaired_projection[appended_target_row, appended_column] = (
                        repaired_projection[appended_target_row, appended_column] + 1
                    ) % PRIME
                    if rank_mod(repaired_projection) != projection.shape[0]:
                        continue
                    kernel = nullspace_basis(repaired_projection)
                    right_inv = right_inverse(repaired_projection)
                    split_basis = np.column_stack([kernel.T, right_inv]) % PRIME
                    split_inverse = invert_square(split_basis)
                    quotient_total = 0
                    unit_total = 0
                    product_residuals = []
                    for generator_id, r_foam in enumerate(r_foam_matrices):
                        diagonal_action = np.zeros((product_tensor.shape[0], product_tensor.shape[0]), dtype=np.int64)
                        diagonal_action[: kernel.shape[0], : kernel.shape[0]] = np.eye(kernel.shape[0], dtype=np.int64)
                        diagonal_action[kernel.shape[0] :, kernel.shape[0] :] = r_foam
                        lift = (split_basis @ diagonal_action @ split_inverse) % PRIME
                        quotient_residual = int(
                            np.count_nonzero((repaired_projection @ lift - r_foam @ repaired_projection) % PRIME)
                        )
                        unit_residual = int(np.count_nonzero((lift @ unit_vector - unit_vector) % PRIME))
                        lhs = np.einsum("kl,lij->kij", lift, product_tensor, optimize=True) % PRIME
                        rhs = np.empty_like(product_tensor)
                        for target_row in range(product_tensor.shape[0]):
                            rhs[target_row] = (lift.T @ product_tensor[target_row] @ lift) % PRIME
                        product_residual = int(np.count_nonzero((lhs - rhs) % PRIME))
                        quotient_total += quotient_residual
                        unit_total += unit_residual
                        product_residuals.append(product_residual)
                        generator_rows.append(
                            {
                                "candidate_id": candidate_id,
                                "generator_id": generator_id,
                                "quotient_intertwiner_residual_nonzero_count": quotient_residual,
                                "unit_residual_nonzero_count": unit_residual,
                                "product_residual_nonzero_count": product_residual,
                                "product_preserved_flag": int(product_residual == 0),
                            }
                        )
                    product_total = sum(product_residuals)
                    candidate_product_totals.append(product_total)
                    candidate_rows.append(
                        {
                            "candidate_id": candidate_id,
                            "fixed_target_row": fixed_target_row,
                            "changed_unit_column": changed_unit_column,
                            "changed_unit_relation": relation_by_row[changed_unit_column],
                            "appended_column": appended_column,
                            "appended_relation": relation_by_row[appended_column],
                            "appended_target_row": appended_target_row,
                            "unit_repaired_base_rank": base_rank,
                            "repaired_projection_rank": projection.shape[0],
                            "kernel_dimension": int(kernel.shape[0]),
                            "quotient_residual_total": quotient_total,
                            "unit_residual_total": unit_total,
                            "product_residual_total": product_total,
                            "product_residual_min": min(product_residuals),
                            "product_residual_max": max(product_residuals),
                            "product_preserved_generator_count": sum(int(value == 0) for value in product_residuals),
                        }
                    )
                    candidate_id += 1

    best_candidate_id = min(candidate_rows, key=lambda row: row["product_residual_total"])["candidate_id"]
    obs = {
        "long_k23cl_certified_flag": int(
            long_k23cl.get("status") == "SECTOR33_K23_MULTIPLICATION_CLOSURE60_CERTIFIED"
            and long_k23cl.get("all_checks_pass") is True
        ),
        "long_k23unit_certified_flag": int(
            long_k23unit.get("status") == "SECTOR33_K23_CLOSURE60_UNIT_PROJECTION_OBSTRUCTION_CERTIFIED"
            and long_k23unit.get("all_checks_pass") is True
        ),
        "long_k23tgt_certified_flag": int(
            long_k23tgt.get("status") == "SECTOR33_K23_TARGET_UNIT_APERTURE_CERTIFIED"
            and long_k23tgt.get("all_checks_pass") is True
        ),
        "long_k23proj_certified_flag": int(
            long_k23proj.get("status") == "SECTOR33_K23_REPAIRED_PROJECTION_PRODUCT_OBSTRUCTION_CERTIFIED"
            and long_k23proj.get("all_checks_pass") is True
        ),
        "long_k23rh_certified_flag": int(
            long_k23rh.get("status") == "SECTOR33_K23_RHC_SOURCE_LIFT_CERTIFIED"
            and long_k23rh.get("all_checks_pass") is True
        ),
        "closure_dimension": int(product_tensor.shape[0]),
        "target_dimension": int(projection.shape[0]),
        "fixed_target_row_count": len(fixed_target_rows),
        "old_unit_column_count": len(old_unit_columns),
        "appended_column_count": len(appended_columns),
        "raw_candidate_count": raw_candidate_count,
        "rank_restoring_candidate_count": len(candidate_rows),
        "generator_count": int(r_foam_matrices.shape[0]),
        "candidate_generator_row_count": len(generator_rows),
        "quotient_residual_total": sum(row["quotient_intertwiner_residual_nonzero_count"] for row in generator_rows),
        "unit_residual_total": sum(row["unit_residual_nonzero_count"] for row in generator_rows),
        "product_residual_total_min": min(candidate_product_totals),
        "product_residual_total_max": max(candidate_product_totals),
        "best_candidate_id": best_candidate_id,
        "best_candidate_product_residual_total": min(candidate_product_totals),
        "product_preserved_candidate_count": sum(
            int(row["product_preserved_generator_count"] > 0) for row in candidate_rows
        ),
        "product_obstructed_candidate_count": sum(
            int(row["product_preserved_generator_count"] == 0) for row in candidate_rows
        ),
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    candidate_table = table_from_rows(CANDIDATE_COLUMNS, candidate_rows)
    generator_table = table_from_rows(GENERATOR_COLUMNS, generator_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "candidate_table": candidate_table.astype(np.int64),
        "generator_table": generator_table.astype(np.int64),
        "candidate_product_residual_vector": np.asarray(candidate_product_totals, dtype=np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "long_k23cl": long_k23cl,
        "long_k23unit": long_k23unit,
        "long_k23tgt": long_k23tgt,
        "long_k23proj": long_k23proj,
        "long_k23rh": long_k23rh,
        "candidate_rows": candidate_rows,
        "generator_rows": generator_rows,
        "obs_rows": obs_rows,
        "candidate_table": candidate_table,
        "generator_table": generator_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "candidate_text_hash": hashlib.sha256(digest_text(CANDIDATE_COLUMNS, candidate_rows).encode("ascii")).hexdigest(),
        "generator_text_hash": hashlib.sha256(digest_text(GENERATOR_COLUMNS, generator_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": (
            obs["long_k23cl_certified_flag"],
            obs["long_k23unit_certified_flag"],
            obs["long_k23tgt_certified_flag"],
            obs["long_k23proj_certified_flag"],
            obs["long_k23rh_certified_flag"],
        )
        == (1, 1, 1, 1, 1),
        "family_profile_matches": (
            obs["closure_dimension"],
            obs["target_dimension"],
            obs["fixed_target_row_count"],
            obs["old_unit_column_count"],
            obs["appended_column_count"],
            obs["raw_candidate_count"],
            obs["rank_restoring_candidate_count"],
            obs["generator_count"],
            obs["candidate_generator_row_count"],
        )
        == (60, 33, 3, 2, 4, 792, 24, 9, 216),
        "quotient_and_unit_residuals_zero": (
            obs["quotient_residual_total"],
            obs["unit_residual_total"],
        )
        == (0, 0),
        "product_family_obstructed": (
            obs["product_residual_total_min"],
            obs["product_residual_total_max"],
            obs["best_candidate_id"],
            obs["best_candidate_product_residual_total"],
            obs["product_preserved_candidate_count"],
            obs["product_obstructed_candidate_count"],
        )
        == (958530, 1014453, 10, 958530, 0, 24),
        "boundary_flags_match": obs["complete_goal_claim_flag"] == 0,
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_minimal_repaired_projection_family_obstruction",
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies that all 24 rank-restoring unit-entry minimal repaired projections have exact quotient and unit behavior, but none preserve the closure60 product.",
    }
    seam_payload = {
        "schema": "long.k23fam.seam@1",
        "status": STATUS,
        "claim": "The finite minimal repaired-projection family is product-obstructed for all rank-restoring candidates.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23cl": input_entry(LONG_K23CL_REPORT, {"status": rows["long_k23cl"].get("status"), "certificate_sha256": rows["long_k23cl"].get("certificate_sha256")}),
        "long_k23unit": input_entry(LONG_K23UNIT_REPORT, {"status": rows["long_k23unit"].get("status"), "certificate_sha256": rows["long_k23unit"].get("certificate_sha256")}),
        "long_k23tgt": input_entry(LONG_K23TGT_REPORT, {"status": rows["long_k23tgt"].get("status"), "certificate_sha256": rows["long_k23tgt"].get("certificate_sha256")}),
        "long_k23proj": input_entry(LONG_K23PROJ_REPORT, {"status": rows["long_k23proj"].get("status"), "certificate_sha256": rows["long_k23proj"].get("certificate_sha256")}),
        "long_k23rh": input_entry(LONG_K23RH_REPORT, {"status": rows["long_k23rh"].get("status"), "certificate_sha256": rows["long_k23rh"].get("certificate_sha256")}),
        "long_k23cl_closure_rows": input_entry(LONG_K23CL_CLOSURE_ROWS),
        "long_k23cl_matrices": input_entry(LONG_K23CL_MATRICES),
        "long_k23unit_matrices": input_entry(LONG_K23UNIT_MATRICES),
        "long_k23rh_matrices": input_entry(LONG_K23RH_MATRICES),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23fam.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23fam certifies the finite minimal repaired-projection family obstruction.",
        "stage_protocol": {
            "draft": "read closure60 product, target aperture, repaired projection seed, and R_hc target action",
            "witness": "emit rank-restoring candidate rows, candidate-generator product residual rows, observables, and matrices",
            "coherence": "check family size, quotient residuals, unit residuals, product residual extrema, and best candidate",
            "closure": "obstruct the minimal repaired-projection product-action family while leaving broader projection families open",
            "emit": "write long_k23fam artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "candidate_rows_csv": relpath(OUT_DIR / "candidate_rows.csv"),
            "generator_rows_csv": relpath(OUT_DIR / "generator_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23fam_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the unit-entry minimal repaired-projection search has 792 raw candidates and 24 rank-restoring candidates",
                "all 24 rank-restoring candidates have zero quotient-intertwiner residual and zero unit residual",
                "no rank-restoring candidate preserves the closure60 product for any of the nine checked generators",
                "the best candidate is candidate 10 with product residual total 958,530",
            ],
            "does_not_certify": [
                "nonexistence for all possible repaired projections",
                "nonexistence for non-unit appended projection coefficients",
                "nonexistence for nonunital or concatenative action models",
                "bundle-wide integration",
                "a final broad-goal closure claim",
            ],
        },
        "next_highest_yield_item": "Use this finite product-action obstruction as the handoff certificate for a concatenative polymorphism certificate on the closure60 alphabet.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23fam.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23fam.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "candidate_csv": csv_text(CANDIDATE_COLUMNS, rows["candidate_rows"]),
        "generator_csv": csv_text(GENERATOR_COLUMNS, rows["generator_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "candidate_table": rows["candidate_table"],
        "generator_table": rows["generator_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "candidate_text_sha256": rows["candidate_text_hash"],
            "generator_text_sha256": rows["generator_text_hash"],
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
    (OUT_DIR / "candidate_rows.csv").write_text(payloads["candidate_csv"], encoding="utf-8")
    (OUT_DIR / "generator_rows.csv").write_text(payloads["generator_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        candidate_table=payloads["candidate_table"],
        generator_table=payloads["generator_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23fam_matrices.npz", **payloads["matrix_payload"])
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
