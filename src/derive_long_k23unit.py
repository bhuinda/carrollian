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


THEOREM_ID = "long_k23unit"
STATUS = "SECTOR33_K23_CLOSURE60_UNIT_PROJECTION_OBSTRUCTION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PRIME = 1_000_003

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23unit.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23unit.py"
LONG_K23CL_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23cl" / "report.json"
LONG_K23FIX_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23fix" / "report.json"
LONG_K23CL_CLOSURE_ROWS = D20_INVARIANTS / "proof_obligations" / "long_k23cl" / "closure_rows.csv"
LONG_K23CL_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23cl" / "k23cl_matrices.npz"
LONG_K23RH_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23rh" / "report.json"
LONG_K23RH_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23rh" / "k23rh_matrices.npz"

UNIT_TEXT_HASH = "e8f508b51e0730fdaac9e08bbc7bb85f3812c3269b1efbc80660aeda7e10a575"
GENERATOR_TEXT_HASH = "04d27cfea1bebea7b3d933ba3e430cc236a5c5c912ba02f6424fc8d6dcc83dea"
OBS_TEXT_HASH = "c563c0bc7c1721c149dae4a95ab2acbd0e7696b55222cfdcdd9fced66b89677a"
MATRIX_SHA256 = "9ad762823f926f37da152350ff08817c1eef86b438814ec1fde15dd321ac1645"

UNIT_COLUMNS = [
    "unit_row_id",
    "closure_row_id",
    "relation_id",
    "coefficient_mod",
]
GENERATOR_COLUMNS = [
    "generator_id",
    "r_foam_rank",
    "projected_unit_residual_nonzero_count",
    "projected_unit_residual_sum_mod_p",
    "first_residual_row",
    "first_residual_value",
    "unit_projection_fixed_flag",
    "quotient_action_automorphism_possible_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_k23cl_certified_flag",
    "long_k23fix_certified_flag",
    "long_k23rh_certified_flag",
    "closure_dimension",
    "projection_rank",
    "target_dimension",
    "generator_count",
    "unit_system_rank",
    "unit_system_inconsistent_count",
    "unit_free_dimension",
    "unit_support_count",
    "unit_left_residual_nonzero_count",
    "unit_right_residual_nonzero_count",
    "projected_unit_support_count",
    "r_foam_rank_sum",
    "unit_projection_fixed_generator_count",
    "unit_projection_moved_generator_count",
    "automorphism_obstructed_generator_count",
    "closure60_quotient_automorphism_obstructed_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def rank_mod(matrix: np.ndarray, prime: int = PRIME) -> int:
    work = np.asarray(matrix, dtype=np.int64).copy() % prime
    rows, cols = work.shape
    rank = 0
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
        rank += 1
        if rank == rows:
            break
    return rank


def solve_unique_unit(product_tensor: np.ndarray) -> tuple[np.ndarray, int, int, int]:
    dim = int(product_tensor.shape[0])
    rows = []
    rhs = []
    for basis_row in range(dim):
        for target_row in range(dim):
            rows.append(product_tensor[target_row, :, basis_row])
            rhs.append(1 if target_row == basis_row else 0)
            rows.append(product_tensor[target_row, basis_row, :])
            rhs.append(1 if target_row == basis_row else 0)
    matrix = np.asarray(rows, dtype=np.int64) % PRIME
    vector = np.asarray(rhs, dtype=np.int64) % PRIME
    augmented = np.hstack([matrix, vector[:, None]])
    equation_count, variable_count = matrix.shape
    rank = 0
    pivots: list[int] = []
    for col in range(variable_count):
        pivot = None
        for row in range(rank, equation_count):
            if int(augmented[row, col]) % PRIME:
                pivot = row
                break
        if pivot is None:
            continue
        if pivot != rank:
            augmented[[rank, pivot]] = augmented[[pivot, rank]]
        inv = pow(int(augmented[rank, col]), PRIME - 2, PRIME)
        augmented[rank] = (augmented[rank] * inv) % PRIME
        for row in np.nonzero(augmented[:, col])[0]:
            if row != rank:
                augmented[row] = (augmented[row] - int(augmented[row, col]) * augmented[rank]) % PRIME
        pivots.append(col)
        rank += 1
        if rank == variable_count:
            break
    inconsistent_count = 0
    for row in range(rank, equation_count):
        if not np.any(augmented[row, :variable_count]) and int(augmented[row, variable_count]) % PRIME:
            inconsistent_count += 1
    solution = np.zeros(variable_count, dtype=np.int64)
    if inconsistent_count == 0:
        for row, col in enumerate(pivots):
            solution[col] = int(augmented[row, variable_count]) % PRIME
    return solution, rank, inconsistent_count, variable_count - rank


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = [
        "unit_vector",
        "projected_unit_vector",
        "generator_table",
        "observable_vector",
    ]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def build_rows() -> dict[str, Any]:
    long_k23cl = load_json(LONG_K23CL_REPORT)
    long_k23fix = load_json(LONG_K23FIX_REPORT)
    long_k23rh = load_json(LONG_K23RH_REPORT)
    closure_rows = [{key: int(value) for key, value in row.items()} for row in read_csv_rows(LONG_K23CL_CLOSURE_ROWS)]
    relation_by_row = {row["closure_row_id"]: row["relation_id"] for row in closure_rows}
    with np.load(LONG_K23CL_MATRICES, allow_pickle=False) as matrices:
        product_tensor = np.asarray(matrices["closure_product_tensor"], dtype=np.int64) % PRIME
    with np.load(LONG_K23RH_MATRICES, allow_pickle=False) as matrices:
        projection_matrix = np.asarray(matrices["projection_matrix"], dtype=np.int64) % PRIME
        r_foam_matrices = np.asarray(matrices["r_foam_matrices"], dtype=np.int64) % PRIME

    unit_vector, unit_rank, unit_inconsistent, unit_free_dim = solve_unique_unit(product_tensor)
    left_residual = np.einsum("i,kij->kj", unit_vector, product_tensor, optimize=True) % PRIME
    right_residual = np.einsum("j,kij->ki", unit_vector, product_tensor, optimize=True) % PRIME
    identity = np.eye(product_tensor.shape[0], dtype=np.int64)
    left_residual_count = int(np.count_nonzero((left_residual - identity) % PRIME))
    right_residual_count = int(np.count_nonzero((right_residual - identity) % PRIME))

    projection60 = np.zeros((projection_matrix.shape[0], product_tensor.shape[0]), dtype=np.int64)
    projection60[:, : projection_matrix.shape[1]] = projection_matrix
    projected_unit = (projection60 @ unit_vector) % PRIME

    unit_rows = [
        {
            "unit_row_id": unit_row_id,
            "closure_row_id": closure_row_id,
            "relation_id": relation_by_row[closure_row_id],
            "coefficient_mod": int(unit_vector[closure_row_id]),
        }
        for unit_row_id, closure_row_id in enumerate(np.nonzero(unit_vector)[0].tolist())
    ]
    generator_rows = []
    residual_counts = []
    rank_sum = 0
    for generator_id, r_foam in enumerate(r_foam_matrices):
        rank = rank_mod(r_foam)
        rank_sum += rank
        residual = (r_foam @ projected_unit - projected_unit) % PRIME
        residual_count = int(np.count_nonzero(residual))
        residual_counts.append(residual_count)
        first = int(np.nonzero(residual)[0][0]) if residual_count else -1
        generator_rows.append(
            {
                "generator_id": generator_id,
                "r_foam_rank": rank,
                "projected_unit_residual_nonzero_count": residual_count,
                "projected_unit_residual_sum_mod_p": int(np.sum(residual) % PRIME),
                "first_residual_row": first,
                "first_residual_value": int(residual[first]) if first >= 0 else 0,
                "unit_projection_fixed_flag": int(residual_count == 0),
                "quotient_action_automorphism_possible_flag": int(residual_count == 0),
            }
        )

    obs = {
        "long_k23cl_certified_flag": int(
            long_k23cl.get("status") == "SECTOR33_K23_MULTIPLICATION_CLOSURE60_CERTIFIED"
            and long_k23cl.get("all_checks_pass") is True
        ),
        "long_k23fix_certified_flag": int(
            long_k23fix.get("status") == "SECTOR33_K23_FIXED_OLD_MIXED_EXTENSION_OBSTRUCTED"
            and long_k23fix.get("all_checks_pass") is True
        ),
        "long_k23rh_certified_flag": int(
            long_k23rh.get("status") == "SECTOR33_K23_RHC_SOURCE_LIFT_CERTIFIED"
            and long_k23rh.get("all_checks_pass") is True
        ),
        "closure_dimension": int(product_tensor.shape[0]),
        "projection_rank": rank_mod(projection_matrix),
        "target_dimension": int(r_foam_matrices.shape[1]),
        "generator_count": int(r_foam_matrices.shape[0]),
        "unit_system_rank": unit_rank,
        "unit_system_inconsistent_count": unit_inconsistent,
        "unit_free_dimension": unit_free_dim,
        "unit_support_count": int(np.count_nonzero(unit_vector)),
        "unit_left_residual_nonzero_count": left_residual_count,
        "unit_right_residual_nonzero_count": right_residual_count,
        "projected_unit_support_count": int(np.count_nonzero(projected_unit)),
        "r_foam_rank_sum": rank_sum,
        "unit_projection_fixed_generator_count": sum(int(count == 0) for count in residual_counts),
        "unit_projection_moved_generator_count": sum(int(count != 0) for count in residual_counts),
        "automorphism_obstructed_generator_count": sum(int(count != 0) for count in residual_counts),
        "closure60_quotient_automorphism_obstructed_flag": int(all(count != 0 for count in residual_counts)),
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    unit_table = table_from_rows(UNIT_COLUMNS, unit_rows)
    generator_table = table_from_rows(GENERATOR_COLUMNS, generator_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "unit_vector": unit_vector.astype(np.int64),
        "projected_unit_vector": projected_unit.astype(np.int64),
        "generator_table": generator_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "long_k23cl": long_k23cl,
        "long_k23fix": long_k23fix,
        "long_k23rh": long_k23rh,
        "unit_rows": unit_rows,
        "generator_rows": generator_rows,
        "obs_rows": obs_rows,
        "unit_table": unit_table,
        "generator_table": generator_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "unit_text_hash": hashlib.sha256(digest_text(UNIT_COLUMNS, unit_rows).encode("ascii")).hexdigest(),
        "generator_text_hash": hashlib.sha256(digest_text(GENERATOR_COLUMNS, generator_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": (
            obs["long_k23cl_certified_flag"],
            obs["long_k23fix_certified_flag"],
            obs["long_k23rh_certified_flag"],
        )
        == (1, 1, 1),
        "dimension_profile_matches": (
            obs["closure_dimension"],
            obs["projection_rank"],
            obs["target_dimension"],
            obs["generator_count"],
        )
        == (60, 33, 33, 9),
        "unit_profile_matches": (
            obs["unit_system_rank"],
            obs["unit_system_inconsistent_count"],
            obs["unit_free_dimension"],
            obs["unit_support_count"],
            obs["unit_left_residual_nonzero_count"],
            obs["unit_right_residual_nonzero_count"],
            obs["projected_unit_support_count"],
        )
        == (60, 0, 0, 2, 0, 0, 4),
        "target_action_profile_matches": (
            obs["r_foam_rank_sum"],
            obs["unit_projection_fixed_generator_count"],
            obs["unit_projection_moved_generator_count"],
            obs["automorphism_obstructed_generator_count"],
            obs["closure60_quotient_automorphism_obstructed_flag"],
        )
        == (297, 0, 9, 9, 1),
        "boundary_flags_match": obs["complete_goal_claim_flag"] == 0,
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_closure60_unit_projection_obstruction",
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies that the closed 60-row algebra has a unique unit whose projected class is moved by every checked quotient generator; therefore no invertible product action can satisfy the current quotient intertwining.",
    }
    seam_payload = {
        "schema": "long.k23unit.seam@1",
        "status": STATUS,
        "claim": "The corrected closure60 product has a unique two-sided unit, and the target quotient action moves its projected class for all nine generators.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23cl": input_entry(
            LONG_K23CL_REPORT,
            {
                "status": rows["long_k23cl"].get("status"),
                "certificate_sha256": rows["long_k23cl"].get("certificate_sha256"),
            },
        ),
        "long_k23fix": input_entry(
            LONG_K23FIX_REPORT,
            {
                "status": rows["long_k23fix"].get("status"),
                "certificate_sha256": rows["long_k23fix"].get("certificate_sha256"),
            },
        ),
        "long_k23cl_closure_rows": input_entry(LONG_K23CL_CLOSURE_ROWS),
        "long_k23cl_matrices": input_entry(LONG_K23CL_MATRICES),
        "long_k23rh": input_entry(
            LONG_K23RH_REPORT,
            {
                "status": rows["long_k23rh"].get("status"),
                "certificate_sha256": rows["long_k23rh"].get("certificate_sha256"),
            },
        ),
        "long_k23rh_matrices": input_entry(LONG_K23RH_MATRICES),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23unit.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23unit certifies the closure60 unit-projection obstruction to a quotient-preserving product action.",
        "stage_protocol": {
            "draft": "read corrected long_k23cl, long_k23fix, and the R_hc projection/target matrices",
            "witness": "emit the unique unit support and projected-unit residual rows for all target generators",
            "coherence": "check unit uniqueness, two-sided unit residuals, projection rank, target ranks, and moved projected-unit counts",
            "closure": "obstruct invertible product actions satisfying the current quotient intertwining",
            "emit": "write long_k23unit artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "unit_rows_csv": relpath(OUT_DIR / "unit_rows.csv"),
            "generator_rows_csv": relpath(OUT_DIR / "generator_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23unit_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the closure60 product has a unique two-sided unit supported on relation rows 163 and 893",
                "the current 33-row projection sends that unit to a nonzero 4-support quotient vector",
                "all nine checked quotient generators are full-rank target maps",
                "each checked quotient generator moves the projected unit",
                "there is no invertible product action on closure60 satisfying the current quotient intertwining with the fixed old projection",
            ],
            "does_not_certify": [
                "nonexistence of non-invertible product endomorphisms",
                "nonexistence under a changed old projection",
                "nonexistence under a nonunital product-action convention",
                "a final operator carrier",
                "bundle-wide integration",
                "a final broad-goal closure claim",
            ],
        },
        "next_highest_yield_item": "Decide whether to demote the current quotient-action target or replace the projection/target pairing so the projected unit is fixed before attempting another 60-row product action.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23unit.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23unit.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "unit_csv": csv_text(UNIT_COLUMNS, rows["unit_rows"]),
        "generator_csv": csv_text(GENERATOR_COLUMNS, rows["generator_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "unit_table": rows["unit_table"],
        "generator_table": rows["generator_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "unit_text_sha256": rows["unit_text_hash"],
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
    (OUT_DIR / "unit_rows.csv").write_text(payloads["unit_csv"], encoding="utf-8")
    (OUT_DIR / "generator_rows.csv").write_text(payloads["generator_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        unit_table=payloads["unit_table"],
        generator_table=payloads["generator_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23unit_matrices.npz", **payloads["matrix_payload"])
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
