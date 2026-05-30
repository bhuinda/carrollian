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


THEOREM_ID = "long_k23proj"
STATUS = "SECTOR33_K23_REPAIRED_PROJECTION_PRODUCT_OBSTRUCTION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PRIME = 1_000_003

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23proj.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23proj.py"
LONG_K23CL_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23cl" / "report.json"
LONG_K23CL_CLOSURE_ROWS = D20_INVARIANTS / "proof_obligations" / "long_k23cl" / "closure_rows.csv"
LONG_K23CL_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23cl" / "k23cl_matrices.npz"
LONG_K23UNIT_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23unit" / "report.json"
LONG_K23UNIT_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23unit" / "k23unit_matrices.npz"
LONG_K23TGT_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23tgt" / "report.json"
LONG_K23RH_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23rh" / "report.json"
LONG_K23RH_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23rh" / "k23rh_matrices.npz"

EDIT_TEXT_HASH = "e0b4fc7fe195f17d08c89d927351a39f9e223ca1ad23155a34050e51c97b4fdb"
GENERATOR_TEXT_HASH = "69ba925f3372cb143a21961416ee1540e3320a396c19d8fa2b98c944951c8027"
OBS_TEXT_HASH = "11f21ae19c9fee453810a37882d861b9773198b47fa53c251f162b53d1fa7a72"
MATRIX_SHA256 = "1e6687a529bc8bdc59fdf295f08e85f5c2fb09cc6fa7a9ec10c9a25ad3523062"

EDIT_COLUMNS = [
    "edit_id",
    "target_row_id",
    "closure_row_id",
    "relation_id",
    "old_value",
    "new_value",
    "delta_mod",
    "edit_role_code",
]
GENERATOR_COLUMNS = [
    "generator_id",
    "quotient_intertwiner_residual_nonzero_count",
    "unit_residual_nonzero_count",
    "product_residual_nonzero_count",
    "lift_nonzero_count",
    "lift_nonidentity_count",
    "product_preserved_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_k23cl_certified_flag",
    "long_k23unit_certified_flag",
    "long_k23tgt_certified_flag",
    "long_k23rh_certified_flag",
    "closure_dimension",
    "target_dimension",
    "old_projection_rank",
    "unit_repaired_base_rank",
    "repaired_projection_rank",
    "kernel_dimension",
    "right_inverse_residual_nonzero_count",
    "split_basis_rank",
    "repaired_unit_support_count",
    "repaired_unit_target_row",
    "projection_edit_row_count",
    "quotient_intertwiner_residual_nonzero_total",
    "unit_residual_nonzero_total",
    "product_residual_nonzero_total",
    "product_residual_nonzero_min",
    "product_residual_nonzero_max",
    "product_preserved_generator_count",
    "product_obstructed_generator_count",
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


def right_inverse(projection: np.ndarray) -> tuple[np.ndarray, list[int]]:
    _echelon, rank, pivots = rref(projection)
    if rank != projection.shape[0]:
        raise AssertionError("projection is not full rank")
    pivot_block = projection[:, pivots]
    pivot_inverse = invert_square(pivot_block)
    result = np.zeros((projection.shape[1], projection.shape[0]), dtype=np.int64)
    result[pivots, :] = pivot_inverse
    return result, pivots


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = [
        "repaired_projection",
        "repaired_lifts",
        "generator_table",
        "observable_vector",
    ]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def build_rows() -> dict[str, Any]:
    long_k23cl = load_json(LONG_K23CL_REPORT)
    long_k23unit = load_json(LONG_K23UNIT_REPORT)
    long_k23tgt = load_json(LONG_K23TGT_REPORT)
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
    fixed_unit = np.zeros(projection.shape[0], dtype=np.int64)
    fixed_unit[0] = 1
    delta = (fixed_unit - projected_unit) % PRIME
    unit_repaired_base = projection.copy()
    unit_repaired_base[:, 8] = (unit_repaired_base[:, 8] + delta) % PRIME
    repaired_projection = unit_repaired_base.copy()
    repaired_projection[6, 56] = (repaired_projection[6, 56] + 1) % PRIME

    edit_rows = []
    edit_id = 0
    for target_row_id, delta_value in enumerate(delta.tolist()):
        if delta_value:
            old_value = int(projection[target_row_id, 8])
            new_value = int(unit_repaired_base[target_row_id, 8])
            edit_rows.append(
                {
                    "edit_id": edit_id,
                    "target_row_id": target_row_id,
                    "closure_row_id": 8,
                    "relation_id": relation_by_row[8],
                    "old_value": old_value,
                    "new_value": new_value,
                    "delta_mod": int(delta_value),
                    "edit_role_code": 0,
                }
            )
            edit_id += 1
    edit_rows.append(
        {
            "edit_id": edit_id,
            "target_row_id": 6,
            "closure_row_id": 56,
            "relation_id": relation_by_row[56],
            "old_value": 0,
            "new_value": 1,
            "delta_mod": 1,
            "edit_role_code": 1,
        }
    )

    kernel = nullspace_basis(repaired_projection)
    right_inv, _pivot_columns = right_inverse(repaired_projection)
    split_basis = np.column_stack([kernel.T, right_inv]) % PRIME
    split_inverse = invert_square(split_basis)
    repaired_lifts = []
    generator_rows = []
    product_residuals = []
    quotient_residuals = []
    unit_residuals = []
    for generator_id, r_foam in enumerate(r_foam_matrices):
        diagonal_action = np.zeros((product_tensor.shape[0], product_tensor.shape[0]), dtype=np.int64)
        diagonal_action[: kernel.shape[0], : kernel.shape[0]] = np.eye(kernel.shape[0], dtype=np.int64)
        diagonal_action[kernel.shape[0] :, kernel.shape[0] :] = r_foam
        lift = (split_basis @ diagonal_action @ split_inverse) % PRIME
        repaired_lifts.append(lift)
        quotient_residual = int(np.count_nonzero((repaired_projection @ lift - r_foam @ repaired_projection) % PRIME))
        unit_residual = int(np.count_nonzero((lift @ unit_vector - unit_vector) % PRIME))
        lhs = np.einsum("kl,lij->kij", lift, product_tensor, optimize=True) % PRIME
        rhs = np.empty_like(product_tensor)
        for target_row in range(product_tensor.shape[0]):
            rhs[target_row] = (lift.T @ product_tensor[target_row] @ lift) % PRIME
        product_residual = int(np.count_nonzero((lhs - rhs) % PRIME))
        quotient_residuals.append(quotient_residual)
        unit_residuals.append(unit_residual)
        product_residuals.append(product_residual)
        generator_rows.append(
            {
                "generator_id": generator_id,
                "quotient_intertwiner_residual_nonzero_count": quotient_residual,
                "unit_residual_nonzero_count": unit_residual,
                "product_residual_nonzero_count": product_residual,
                "lift_nonzero_count": int(np.count_nonzero(lift)),
                "lift_nonidentity_count": int(np.count_nonzero((lift - np.eye(product_tensor.shape[0], dtype=np.int64)) % PRIME)),
                "product_preserved_flag": int(product_residual == 0),
            }
        )

    repaired_unit = (repaired_projection @ unit_vector) % PRIME
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
        "long_k23rh_certified_flag": int(
            long_k23rh.get("status") == "SECTOR33_K23_RHC_SOURCE_LIFT_CERTIFIED"
            and long_k23rh.get("all_checks_pass") is True
        ),
        "closure_dimension": int(product_tensor.shape[0]),
        "target_dimension": int(repaired_projection.shape[0]),
        "old_projection_rank": rank_mod(projection),
        "unit_repaired_base_rank": rank_mod(unit_repaired_base),
        "repaired_projection_rank": rank_mod(repaired_projection),
        "kernel_dimension": int(kernel.shape[0]),
        "right_inverse_residual_nonzero_count": int(
            np.count_nonzero((repaired_projection @ right_inv - np.eye(repaired_projection.shape[0], dtype=np.int64)) % PRIME)
        ),
        "split_basis_rank": rank_mod(split_basis),
        "repaired_unit_support_count": int(np.count_nonzero(repaired_unit)),
        "repaired_unit_target_row": int(np.nonzero(repaired_unit)[0][0]),
        "projection_edit_row_count": len(edit_rows),
        "quotient_intertwiner_residual_nonzero_total": sum(quotient_residuals),
        "unit_residual_nonzero_total": sum(unit_residuals),
        "product_residual_nonzero_total": sum(product_residuals),
        "product_residual_nonzero_min": min(product_residuals),
        "product_residual_nonzero_max": max(product_residuals),
        "product_preserved_generator_count": sum(int(value == 0) for value in product_residuals),
        "product_obstructed_generator_count": sum(int(value != 0) for value in product_residuals),
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    edit_table = table_from_rows(EDIT_COLUMNS, edit_rows)
    generator_table = table_from_rows(GENERATOR_COLUMNS, generator_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "repaired_projection": repaired_projection.astype(np.int64),
        "repaired_lifts": np.asarray(repaired_lifts, dtype=np.int64),
        "generator_table": generator_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "long_k23cl": long_k23cl,
        "long_k23unit": long_k23unit,
        "long_k23tgt": long_k23tgt,
        "long_k23rh": long_k23rh,
        "edit_rows": edit_rows,
        "generator_rows": generator_rows,
        "obs_rows": obs_rows,
        "edit_table": edit_table,
        "generator_table": generator_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "edit_text_hash": hashlib.sha256(digest_text(EDIT_COLUMNS, edit_rows).encode("ascii")).hexdigest(),
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
            obs["long_k23rh_certified_flag"],
        )
        == (1, 1, 1, 1),
        "projection_repair_profile_matches": (
            obs["closure_dimension"],
            obs["target_dimension"],
            obs["old_projection_rank"],
            obs["unit_repaired_base_rank"],
            obs["repaired_projection_rank"],
            obs["kernel_dimension"],
            obs["right_inverse_residual_nonzero_count"],
            obs["split_basis_rank"],
            obs["repaired_unit_support_count"],
            obs["repaired_unit_target_row"],
            obs["projection_edit_row_count"],
        )
        == (60, 33, 33, 32, 33, 27, 0, 60, 1, 0, 6),
        "quotient_lift_profile_matches": (
            obs["quotient_intertwiner_residual_nonzero_total"],
            obs["unit_residual_nonzero_total"],
        )
        == (0, 0),
        "product_obstruction_profile_matches": (
            obs["product_residual_nonzero_total"],
            obs["product_residual_nonzero_min"],
            obs["product_residual_nonzero_max"],
            obs["product_preserved_generator_count"],
            obs["product_obstructed_generator_count"],
        )
        == (1009706, 79106, 147893, 0, 9),
        "boundary_flags_match": obs["complete_goal_claim_flag"] == 0,
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_repaired_projection_product_obstruction",
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies a rank-33 replacement projection that fixes the closure60 unit class and has exact quotient lifts, while those induced lifts still fail to preserve the 60-row product.",
    }
    seam_payload = {
        "schema": "long.k23proj.seam@1",
        "status": STATUS,
        "claim": "A repaired projection can place the closure60 unit into the target fixed aperture, but the induced quotient lifts remain product-obstructed.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23cl": input_entry(
            LONG_K23CL_REPORT,
            {"status": rows["long_k23cl"].get("status"), "certificate_sha256": rows["long_k23cl"].get("certificate_sha256")},
        ),
        "long_k23unit": input_entry(
            LONG_K23UNIT_REPORT,
            {"status": rows["long_k23unit"].get("status"), "certificate_sha256": rows["long_k23unit"].get("certificate_sha256")},
        ),
        "long_k23tgt": input_entry(
            LONG_K23TGT_REPORT,
            {"status": rows["long_k23tgt"].get("status"), "certificate_sha256": rows["long_k23tgt"].get("certificate_sha256")},
        ),
        "long_k23rh": input_entry(
            LONG_K23RH_REPORT,
            {"status": rows["long_k23rh"].get("status"), "certificate_sha256": rows["long_k23rh"].get("certificate_sha256")},
        ),
        "long_k23cl_closure_rows": input_entry(LONG_K23CL_CLOSURE_ROWS),
        "long_k23cl_matrices": input_entry(LONG_K23CL_MATRICES),
        "long_k23unit_matrices": input_entry(LONG_K23UNIT_MATRICES),
        "long_k23rh_matrices": input_entry(LONG_K23RH_MATRICES),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23proj.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23proj certifies the first repaired-projection quotient lift and its product obstruction.",
        "stage_protocol": {
            "draft": "read closure60 product, closure unit, target aperture, and checked target action",
            "witness": "emit projection edits, repaired quotient-lift rows, observables, and matrices",
            "coherence": "check repaired projection rank, unit target row, right inverse, split basis, quotient residuals, and product residuals",
            "closure": "certify quotient-level repair while preserving the product-action obstruction",
            "emit": "write long_k23proj artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "projection_edits_csv": relpath(OUT_DIR / "projection_edits.csv"),
            "generator_rows_csv": relpath(OUT_DIR / "generator_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23proj_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "a rank-33 repaired projection mapping the closure60 unit to fixed target row 0",
                "the unit-only old-column repair has rank 32, so one appended projection column is needed to restore rank",
                "the induced split-basis source lifts satisfy the quotient intertwining with zero residual",
                "the induced lifts fix the closure60 unit",
                "all nine induced lifts fail to preserve the 60-row product",
            ],
            "does_not_certify": [
                "nonexistence of some other repaired projection with product-preserving lifts",
                "a final projection table",
                "a final operator carrier",
                "bundle-wide integration",
                "a final broad-goal closure claim",
            ],
        },
        "next_highest_yield_item": "Search the repaired-projection family, not just this first candidate, for a product-preserving quotient lift or certify a family-level obstruction.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23proj.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23proj.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "edits_csv": csv_text(EDIT_COLUMNS, rows["edit_rows"]),
        "generator_csv": csv_text(GENERATOR_COLUMNS, rows["generator_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "edit_table": rows["edit_table"],
        "generator_table": rows["generator_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "edit_text_sha256": rows["edit_text_hash"],
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
    (OUT_DIR / "projection_edits.csv").write_text(payloads["edits_csv"], encoding="utf-8")
    (OUT_DIR / "generator_rows.csv").write_text(payloads["generator_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        edit_table=payloads["edit_table"],
        generator_table=payloads["generator_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23proj_matrices.npz", **payloads["matrix_payload"])
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
