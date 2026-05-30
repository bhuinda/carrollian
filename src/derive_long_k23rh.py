from __future__ import annotations

import hashlib
import json
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


THEOREM_ID = "long_k23rh"
STATUS = "SECTOR33_K23_RHC_SOURCE_LIFT_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PRIME = 1_000_003

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23rh.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23rh.py"
LONG_K23PI_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23pi" / "report.json"
LONG_HCGRADE_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_hcgrade" / "center_grade_projection.npz"
LONG_K23LIN_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23lin" / "k23lin_matrices.npz"
LONG_HCFOAM_REPORT = D20_INVARIANTS / "proof_obligations" / "long_hcfoam" / "report.json"
LONG_HCFOAM_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_hcfoam" / "r_foam_matrices.npz"

PIVOT_TEXT_HASH = "efef39fb9c52f3b2ee30424d935073b7b2104e31eaba00f8f65cab0dfe1b1cc0"
GENERATOR_TEXT_HASH = "1182dd91e2e1d344edba2c86d6ef4854718eefc92c3b792ba67f1b5b8cee4220"
OBS_TEXT_HASH = "32b0735d63daed8da02474de2423393cb0622d6619b7e6cf39169731e4ae7a4c"
MATRIX_SHA256 = "3565d286356901386a11328d655c4bc1ba5530d27f9624d342d66376a8741ffc"

PIVOT_COLUMNS = ["pivot_order", "support_column", "right_inverse_row_weight"]
GENERATOR_COLUMNS = [
    "generator_id",
    "target_nonzero_count",
    "target_nonidentity_count",
    "source_lift_nonzero_count",
    "source_lift_nonidentity_count",
    "source_lift_rank",
    "intertwiner_residual_nonzero_count",
    "kernel_identity_residual_nonzero_count",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_k23pi_certified_flag",
    "long_hcfoam_certified_flag",
    "field_prime",
    "support_dimension",
    "quotient_dimension",
    "kernel_dimension",
    "projection_rank",
    "right_inverse_column_count",
    "right_inverse_nonzero_count",
    "right_inverse_residual_nonzero_count",
    "split_basis_rank",
    "split_basis_inverse_residual_nonzero_count",
    "generator_count",
    "source_lift_generator_count",
    "source_lift_rank_sum",
    "source_lift_nonzero_total",
    "source_lift_nonidentity_total",
    "target_nonidentity_generator_count",
    "intertwiner_residual_nonzero_total",
    "kernel_identity_residual_nonzero_total",
    "r_hc_materialized_flag",
    "candidate_projection_flag",
    "final_pi_accepted_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


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
        inv = pow(int(work[rank, col]), -1, prime)
        work[rank] = (work[rank] * inv) % prime
        for row in range(rows):
            if row == rank:
                continue
            factor = int(work[row, col]) % prime
            if factor:
                work[row] = (work[row] - factor * work[rank]) % prime
        rank += 1
        if rank == rows:
            break
    return rank


def pivot_columns(matrix: np.ndarray, prime: int = PRIME) -> list[int]:
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
    return pivots


def invert_matrix(matrix: np.ndarray, prime: int = PRIME) -> np.ndarray:
    work = np.asarray(matrix, dtype=np.int64).copy() % prime
    rows, cols = work.shape
    if rows != cols:
        raise ValueError("matrix must be square")
    inverse = np.eye(rows, dtype=np.int64)
    rank = 0
    for col in range(cols):
        pivot = None
        for row in range(rank, rows):
            if int(work[row, col]) % prime:
                pivot = row
                break
        if pivot is None:
            raise ValueError("matrix is singular")
        if pivot != rank:
            work[[rank, pivot]] = work[[pivot, rank]]
            inverse[[rank, pivot]] = inverse[[pivot, rank]]
        inv = pow(int(work[rank, col]), -1, prime)
        work[rank] = (work[rank] * inv) % prime
        inverse[rank] = (inverse[rank] * inv) % prime
        for row in range(rows):
            if row == rank:
                continue
            factor = int(work[row, col]) % prime
            if factor:
                work[row] = (work[row] - factor * work[rank]) % prime
                inverse[row] = (inverse[row] - factor * inverse[rank]) % prime
        rank += 1
    return inverse


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = [
        "projection_matrix",
        "prime_kernel",
        "right_inverse",
        "split_basis",
        "split_basis_inverse",
        "r_foam_matrices",
        "r_hc_lifts",
        "observable_vector",
    ]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def build_rows() -> dict[str, Any]:
    long_k23pi = load_json(LONG_K23PI_REPORT)
    long_hcfoam = load_json(LONG_HCFOAM_REPORT)
    with np.load(LONG_HCGRADE_MATRICES, allow_pickle=False) as matrices:
        projection = np.asarray(matrices["projection_matrix"], dtype=np.int64) % PRIME
    with np.load(LONG_K23LIN_MATRICES, allow_pickle=False) as matrices:
        kernel = np.asarray(matrices["prime_kernel"], dtype=np.int64) % PRIME
    with np.load(LONG_HCFOAM_MATRICES, allow_pickle=False) as matrices:
        r_foam = np.asarray(matrices["r_foam"], dtype=np.int64) % PRIME

    pivots = pivot_columns(projection)
    pivot_minor = projection[:, pivots]
    pivot_inverse = invert_matrix(pivot_minor)
    right_inverse = np.zeros((projection.shape[1], projection.shape[0]), dtype=np.int64)
    right_inverse[pivots, :] = pivot_inverse
    split_basis = np.concatenate([kernel.T % PRIME, right_inverse], axis=1) % PRIME
    split_basis_inverse = invert_matrix(split_basis)
    identity_kernel = np.eye(kernel.shape[0], dtype=np.int64)

    pivot_rows = [
        {
            "pivot_order": index,
            "support_column": pivot,
            "right_inverse_row_weight": int(np.count_nonzero(right_inverse[pivot])),
        }
        for index, pivot in enumerate(pivots)
    ]
    generator_rows = []
    source_lifts = []
    for generator_id, target in enumerate(r_foam):
        block = np.zeros((split_basis.shape[0], split_basis.shape[0]), dtype=np.int64)
        block[: kernel.shape[0], : kernel.shape[0]] = identity_kernel
        block[kernel.shape[0] :, kernel.shape[0] :] = target
        source_lift = (split_basis @ block @ split_basis_inverse) % PRIME
        source_lifts.append(source_lift)
        generator_rows.append(
            {
                "generator_id": generator_id,
                "target_nonzero_count": int(np.count_nonzero(target)),
                "target_nonidentity_count": int(
                    np.count_nonzero((target - np.eye(target.shape[0], dtype=np.int64)) % PRIME)
                ),
                "source_lift_nonzero_count": int(np.count_nonzero(source_lift)),
                "source_lift_nonidentity_count": int(
                    np.count_nonzero((source_lift - np.eye(source_lift.shape[0], dtype=np.int64)) % PRIME)
                ),
                "source_lift_rank": rank_mod(source_lift),
                "intertwiner_residual_nonzero_count": int(np.count_nonzero((projection @ source_lift - target @ projection) % PRIME)),
                "kernel_identity_residual_nonzero_count": int(np.count_nonzero((source_lift @ kernel.T - kernel.T) % PRIME)),
            }
        )

    right_inverse_residual = (projection @ right_inverse - np.eye(projection.shape[0], dtype=np.int64)) % PRIME
    split_inverse_residual = (split_basis @ split_basis_inverse - np.eye(split_basis.shape[0], dtype=np.int64)) % PRIME
    projection_rank = rank_mod(projection)
    obs = {
        "long_k23pi_certified_flag": int(
            long_k23pi.get("status") == "SECTOR33_K23_HCGRADE_PROJECTION_KERNEL_BINDING_CERTIFIED"
            and long_k23pi.get("all_checks_pass") is True
        ),
        "long_hcfoam_certified_flag": int(long_hcfoam.get("status") == "LONG_HCFOAM_CERTIFIED" and long_hcfoam.get("all_checks_pass") is True),
        "field_prime": PRIME,
        "support_dimension": int(projection.shape[1]),
        "quotient_dimension": int(projection.shape[0]),
        "kernel_dimension": int(kernel.shape[0]),
        "projection_rank": projection_rank,
        "right_inverse_column_count": int(right_inverse.shape[1]),
        "right_inverse_nonzero_count": int(np.count_nonzero(right_inverse)),
        "right_inverse_residual_nonzero_count": int(np.count_nonzero(right_inverse_residual)),
        "split_basis_rank": rank_mod(split_basis),
        "split_basis_inverse_residual_nonzero_count": int(np.count_nonzero(split_inverse_residual)),
        "generator_count": int(r_foam.shape[0]),
        "source_lift_generator_count": len(source_lifts),
        "source_lift_rank_sum": sum(int(row["source_lift_rank"]) for row in generator_rows),
        "source_lift_nonzero_total": sum(int(row["source_lift_nonzero_count"]) for row in generator_rows),
        "source_lift_nonidentity_total": sum(int(row["source_lift_nonidentity_count"]) for row in generator_rows),
        "target_nonidentity_generator_count": sum(int(row["target_nonidentity_count"] > 0) for row in generator_rows),
        "intertwiner_residual_nonzero_total": sum(int(row["intertwiner_residual_nonzero_count"]) for row in generator_rows),
        "kernel_identity_residual_nonzero_total": sum(int(row["kernel_identity_residual_nonzero_count"]) for row in generator_rows),
        "r_hc_materialized_flag": 1,
        "candidate_projection_flag": 1,
        "final_pi_accepted_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    matrix_payload = {
        "projection_matrix": projection.astype(np.int64),
        "prime_kernel": kernel.astype(np.int64),
        "right_inverse": right_inverse.astype(np.int64),
        "split_basis": split_basis.astype(np.int64),
        "split_basis_inverse": split_basis_inverse.astype(np.int64),
        "r_foam_matrices": r_foam.astype(np.int64),
        "r_hc_lifts": np.asarray(source_lifts, dtype=np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "long_k23pi": long_k23pi,
        "long_hcfoam": long_hcfoam,
        "pivot_rows": pivot_rows,
        "generator_rows": generator_rows,
        "obs_rows": obs_rows,
        "pivot_table": table_from_rows(PIVOT_COLUMNS, pivot_rows),
        "generator_table": table_from_rows(GENERATOR_COLUMNS, generator_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "pivot_text_hash": hashlib.sha256(digest_text(PIVOT_COLUMNS, pivot_rows).encode("ascii")).hexdigest(),
        "generator_text_hash": hashlib.sha256(digest_text(GENERATOR_COLUMNS, generator_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": (obs["long_k23pi_certified_flag"], obs["long_hcfoam_certified_flag"]) == (1, 1),
        "split_basis_constructed": (
            obs["support_dimension"],
            obs["quotient_dimension"],
            obs["kernel_dimension"],
            obs["projection_rank"],
            obs["right_inverse_column_count"],
            obs["right_inverse_residual_nonzero_count"],
            obs["split_basis_rank"],
            obs["split_basis_inverse_residual_nonzero_count"],
        )
        == (56, 33, 23, 33, 33, 0, 56, 0),
        "source_lifts_materialized": (
            obs["generator_count"],
            obs["source_lift_generator_count"],
            obs["source_lift_rank_sum"],
            obs["target_nonidentity_generator_count"],
        )
        == (9, 9, 504, 9),
        "intertwiner_equations_pass": (
            obs["intertwiner_residual_nonzero_total"],
            obs["kernel_identity_residual_nonzero_total"],
        )
        == (0, 0),
        "boundary_flags_match": (
            obs["r_hc_materialized_flag"],
            obs["candidate_projection_flag"],
            obs["final_pi_accepted_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (1, 1, 0, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_candidate_projection_rhc_source_lift",
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This materializes a nontrivial source-side R_hc family for the center-grade projection candidate by acting trivially on K23 and by the checked target action on the quotient.",
    }
    seam_payload = {
        "schema": "long.k23rh.seam@1",
        "status": STATUS,
        "claim": "The checked target action lifts to explicit 56x56 source-side R_hc matrices satisfying P R_hc = R_Foam P for the center-grade projection candidate.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23pi": input_entry(
            LONG_K23PI_REPORT,
            {
                "status": rows["long_k23pi"].get("status"),
                "certificate_sha256": rows["long_k23pi"].get("certificate_sha256"),
            },
        ),
        "long_hcgrade_matrices": input_entry(LONG_HCGRADE_MATRICES),
        "long_k23lin_matrices": input_entry(LONG_K23LIN_MATRICES),
        "long_hcfoam": input_entry(
            LONG_HCFOAM_REPORT,
            {
                "status": rows["long_hcfoam"].get("status"),
                "certificate_sha256": rows["long_hcfoam"].get("certificate_sha256"),
            },
        ),
        "long_hcfoam_matrices": input_entry(LONG_HCFOAM_MATRICES),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23rh.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23rh constructs source-side R_hc lifts for the center-grade projection candidate and verifies the target intertwining equations.",
        "stage_protocol": {
            "draft": "read long_k23pi, the center-grade projection, K23 prime kernel, and checked target operators",
            "witness": "emit pivot/right-inverse rows, source-lift generator rows, observables, and matrix payloads",
            "coherence": "check right inverse, split-basis invertibility, source-lift ranks, kernel identity, and P R_hc = R_Foam P",
            "closure": "certify candidate-projection R_hc lifts without accepting the projection as final pi_Foam33",
            "emit": "write long_k23rh artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "pivot_rows_csv": relpath(OUT_DIR / "pivot_rows.csv"),
            "generator_rows_csv": relpath(OUT_DIR / "generator_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23rh_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "a 56x33 right inverse of the center-grade projection candidate",
                "a 56x56 split basis from K23 kernel columns plus quotient right-inverse columns",
                "nine explicit 56x56 source-side R_hc lift matrices",
                "each lift fixes the K23 kernel pointwise",
                "each lift satisfies P R_hc = R_Foam P for the checked target operator with zero residual",
            ],
            "does_not_certify": [
                "that the center-grade projection candidate is the accepted final pi_Foam33 table",
                "that these dense prime-field lifts are sparse, signed-row, or raw-operation-supported",
                "multiplication-structure preservation beyond the displayed intertwining equation",
                "broad bundle integration",
                "a final broad-goal closure claim",
            ],
        },
        "next_highest_yield_item": "Test whether the certified R_hc lifts preserve the finite operation/multiplication surfaces, or certify the first obstruction such as dense-support leakage against raw operation support.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23rh.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23rh.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "pivot_csv": csv_text(PIVOT_COLUMNS, rows["pivot_rows"]),
        "generator_csv": csv_text(GENERATOR_COLUMNS, rows["generator_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "pivot_table": rows["pivot_table"],
        "generator_table": rows["generator_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "pivot_text_sha256": rows["pivot_text_hash"],
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
    (OUT_DIR / "pivot_rows.csv").write_text(payloads["pivot_csv"], encoding="utf-8")
    (OUT_DIR / "generator_rows.csv").write_text(payloads["generator_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        pivot_table=payloads["pivot_table"],
        generator_table=payloads["generator_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23rh_matrices.npz", **payloads["matrix_payload"])
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
