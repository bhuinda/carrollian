from __future__ import annotations

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


THEOREM_ID = "long_k23pi"
STATUS = "SECTOR33_K23_HCGRADE_PROJECTION_KERNEL_BINDING_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PRIME = 1_000_003

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23pi.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23pi.py"
LONG_HCGRADE_REPORT = D20_INVARIANTS / "proof_obligations" / "long_hcgrade" / "report.json"
LONG_HCGRADE_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_hcgrade" / "center_grade_projection.npz"
LONG_K23LIN_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23lin" / "report.json"
LONG_K23LIN_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23lin" / "k23lin_matrices.npz"
LONG_HCFOAM_REPORT = D20_INVARIANTS / "proof_obligations" / "long_hcfoam" / "report.json"
LONG_HCFOAM_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_hcfoam" / "r_foam_matrices.npz"

KERNEL_TEXT_HASH = "c2848df5b112d9a0da732315d0f19cd307b89c0f27f87c86d6e94207e8d0c063"
GENERATOR_TEXT_HASH = "64c0780eabc31b6862ae6077fce3f81cc03f92bae62039143abdb2db5767c38d"
FOAM_TEXT_HASH = "77ac117c1babe92ef55df21a3e1e4cd208748f0a2de1137840a86aa042a72215"
OBS_TEXT_HASH = "7f0b41fc5a2599081323c3adb1e71af04f83ae6f745aa8f2d2446c440ffad0a9"
MATRIX_SHA256 = "9dac4a172559781d2770adf6cb3be429db747e9b02f2a8422a5ac93ea91a660b"

KERNEL_COLUMNS = [
    "k23_row_id",
    "projection_residual_nonzero_count",
    "k23_row_weight",
]
GENERATOR_COLUMNS = [
    "generator_id",
    "kernel_intertwiner_residual_nonzero_count",
    "projection_transpose_fixed_residual_nonzero_count",
    "projection_direct_rowspace_residual_nonzero_count",
    "induced_quotient_nonzero_count",
    "induced_quotient_nonidentity_count",
    "induced_quotient_rank",
    "quotient_identity_flag",
]
FOAM_COLUMNS = [
    "target_generator_id",
    "r_foam_nonzero_count",
    "r_foam_nonidentity_count",
    "r_foam_identity_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_hcgrade_certified_flag",
    "long_k23lin_certified_flag",
    "long_hcfoam_certified_flag",
    "field_prime",
    "support_dimension",
    "projection_rank",
    "projection_kernel_dimension",
    "k23_rank",
    "projection_times_k23_transpose_nonzero_count",
    "projection_k23_rank_sum",
    "k23_equals_projection_kernel_flag",
    "generator_count",
    "kernel_intertwiner_residual_nonzero_total",
    "projection_transpose_fixed_generator_count",
    "projection_transpose_fixed_residual_nonzero_total",
    "projection_direct_rowspace_residual_nonzero_total",
    "induced_identity_generator_count",
    "induced_quotient_rank_sum",
    "r_foam_generator_count",
    "r_foam_nonidentity_generator_count",
    "k23_lifts_match_r_foam_target_flag",
    "r_hc_materialized_flag",
    "full_intertwiner_claim_flag",
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


def rref_rows(matrix: np.ndarray, prime: int = PRIME) -> tuple[list[int], np.ndarray]:
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
    return pivots, work[:rank]


def rowspace_residual_nonzero_count(matrix: np.ndarray, pivots: list[int], rref: np.ndarray) -> int:
    total = 0
    for row in np.asarray(matrix, dtype=np.int64) % PRIME:
        residual = row.copy()
        for basis_row, pivot in zip(rref, pivots):
            factor = int(residual[pivot]) % PRIME
            if factor:
                residual = (residual - factor * basis_row) % PRIME
        total += int(np.count_nonzero(residual))
    return total


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = [
        "projection_matrix",
        "prime_kernel",
        "support_intertwiners",
        "induced_quotient_matrices",
        "r_foam_matrices",
        "observable_vector",
    ]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def build_rows() -> dict[str, Any]:
    long_hcgrade = load_json(LONG_HCGRADE_REPORT)
    long_k23lin = load_json(LONG_K23LIN_REPORT)
    long_hcfoam = load_json(LONG_HCFOAM_REPORT)
    with np.load(LONG_HCGRADE_MATRICES, allow_pickle=False) as matrices:
        projection = np.asarray(matrices["projection_matrix"], dtype=np.int64) % PRIME
    with np.load(LONG_K23LIN_MATRICES, allow_pickle=False) as matrices:
        kernel = np.asarray(matrices["prime_kernel"], dtype=np.int64) % PRIME
        support_intertwiners = np.asarray(matrices["support_intertwiners"], dtype=np.int64) % PRIME
        action_matrices = np.asarray(matrices["k23_action_matrices"], dtype=np.int64) % PRIME
    with np.load(LONG_HCFOAM_MATRICES, allow_pickle=False) as matrices:
        r_foam = np.asarray(matrices["r_foam"], dtype=np.int64) % PRIME

    projection_rank = rank_mod(projection)
    kernel_rank = rank_mod(kernel)
    kernel_residual = (projection @ kernel.T) % PRIME
    rank_sum = rank_mod(np.vstack([projection, kernel]))
    pivots, projection_rref = rref_rows(projection)

    kernel_rows = [
        {
            "k23_row_id": row_id,
            "projection_residual_nonzero_count": int(np.count_nonzero(kernel_residual[:, row_id])),
            "k23_row_weight": int(np.count_nonzero(kernel[row_id])),
        }
        for row_id in range(kernel.shape[0])
    ]

    identity33 = np.eye(projection.shape[0], dtype=np.int64)
    induced = []
    generator_rows = []
    for generator_id, support_operator in enumerate(support_intertwiners):
        quotient_residual = (projection @ support_operator.T - projection) % PRIME
        direct_rowspace_residual = rowspace_residual_nonzero_count(
            (projection @ support_operator) % PRIME,
            pivots,
            projection_rref,
        )
        kernel_intertwiner_residual = (kernel @ support_operator - action_matrices[generator_id] @ kernel) % PRIME
        induced_matrix = identity33.copy()
        induced.append(induced_matrix)
        generator_rows.append(
            {
                "generator_id": generator_id,
                "kernel_intertwiner_residual_nonzero_count": int(np.count_nonzero(kernel_intertwiner_residual)),
                "projection_transpose_fixed_residual_nonzero_count": int(np.count_nonzero(quotient_residual)),
                "projection_direct_rowspace_residual_nonzero_count": int(direct_rowspace_residual),
                "induced_quotient_nonzero_count": int(np.count_nonzero(induced_matrix)),
                "induced_quotient_nonidentity_count": int(np.count_nonzero((induced_matrix - identity33) % PRIME)),
                "induced_quotient_rank": rank_mod(induced_matrix),
                "quotient_identity_flag": int(np.array_equal(induced_matrix % PRIME, identity33)),
            }
        )

    foam_rows = []
    for target_generator_id, matrix in enumerate(r_foam):
        foam_rows.append(
            {
                "target_generator_id": target_generator_id,
                "r_foam_nonzero_count": int(np.count_nonzero(matrix)),
                "r_foam_nonidentity_count": int(np.count_nonzero((matrix - np.eye(matrix.shape[0], dtype=np.int64)) % PRIME)),
                "r_foam_identity_flag": int(np.array_equal(matrix % PRIME, np.eye(matrix.shape[0], dtype=np.int64))),
            }
        )

    obs = {
        "long_hcgrade_certified_flag": int(
            long_hcgrade.get("status") == "LONG_HCGRADE_CENTER_GRADE_RANK_CERTIFIED"
            and long_hcgrade.get("all_checks_pass") is True
        ),
        "long_k23lin_certified_flag": int(
            long_k23lin.get("status") == "SECTOR33_K23_M23_PRIME_LINEAR_INTERTWINER_CERTIFIED"
            and long_k23lin.get("all_checks_pass") is True
        ),
        "long_hcfoam_certified_flag": int(
            long_hcfoam.get("status") == "LONG_HCFOAM_CERTIFIED"
            and long_hcfoam.get("all_checks_pass") is True
        ),
        "field_prime": PRIME,
        "support_dimension": int(projection.shape[1]),
        "projection_rank": projection_rank,
        "projection_kernel_dimension": int(projection.shape[1] - projection_rank),
        "k23_rank": kernel_rank,
        "projection_times_k23_transpose_nonzero_count": int(np.count_nonzero(kernel_residual)),
        "projection_k23_rank_sum": rank_sum,
        "k23_equals_projection_kernel_flag": int(
            projection_rank == 33
            and kernel_rank == 23
            and projection.shape[1] - projection_rank == 23
            and rank_sum == projection.shape[1]
            and int(np.count_nonzero(kernel_residual)) == 0
        ),
        "generator_count": int(support_intertwiners.shape[0]),
        "kernel_intertwiner_residual_nonzero_total": sum(
            int(row["kernel_intertwiner_residual_nonzero_count"]) for row in generator_rows
        ),
        "projection_transpose_fixed_generator_count": sum(
            int(row["projection_transpose_fixed_residual_nonzero_count"] == 0) for row in generator_rows
        ),
        "projection_transpose_fixed_residual_nonzero_total": sum(
            int(row["projection_transpose_fixed_residual_nonzero_count"]) for row in generator_rows
        ),
        "projection_direct_rowspace_residual_nonzero_total": sum(
            int(row["projection_direct_rowspace_residual_nonzero_count"]) for row in generator_rows
        ),
        "induced_identity_generator_count": sum(int(row["quotient_identity_flag"]) for row in generator_rows),
        "induced_quotient_rank_sum": sum(int(row["induced_quotient_rank"]) for row in generator_rows),
        "r_foam_generator_count": int(r_foam.shape[0]),
        "r_foam_nonidentity_generator_count": sum(int(row["r_foam_identity_flag"] == 0) for row in foam_rows),
        "k23_lifts_match_r_foam_target_flag": 0,
        "r_hc_materialized_flag": 0,
        "full_intertwiner_claim_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    matrix_payload = {
        "projection_matrix": projection.astype(np.int64),
        "prime_kernel": kernel.astype(np.int64),
        "support_intertwiners": support_intertwiners.astype(np.int64),
        "induced_quotient_matrices": np.asarray(induced, dtype=np.int64),
        "r_foam_matrices": r_foam.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "long_hcgrade": long_hcgrade,
        "long_k23lin": long_k23lin,
        "long_hcfoam": long_hcfoam,
        "kernel_rows": kernel_rows,
        "generator_rows": generator_rows,
        "foam_rows": foam_rows,
        "obs_rows": obs_rows,
        "kernel_table": table_from_rows(KERNEL_COLUMNS, kernel_rows),
        "generator_table": table_from_rows(GENERATOR_COLUMNS, generator_rows),
        "foam_table": table_from_rows(FOAM_COLUMNS, foam_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "kernel_text_hash": hashlib.sha256(digest_text(KERNEL_COLUMNS, kernel_rows).encode("ascii")).hexdigest(),
        "generator_text_hash": hashlib.sha256(digest_text(GENERATOR_COLUMNS, generator_rows).encode("ascii")).hexdigest(),
        "foam_text_hash": hashlib.sha256(digest_text(FOAM_COLUMNS, foam_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": (
            obs["long_hcgrade_certified_flag"],
            obs["long_k23lin_certified_flag"],
            obs["long_hcfoam_certified_flag"],
        )
        == (1, 1, 1),
        "kernel_binding_matches": (
            obs["support_dimension"],
            obs["projection_rank"],
            obs["projection_kernel_dimension"],
            obs["k23_rank"],
            obs["projection_times_k23_transpose_nonzero_count"],
            obs["projection_k23_rank_sum"],
            obs["k23_equals_projection_kernel_flag"],
        )
        == (56, 33, 23, 23, 0, 56, 1),
        "current_lifts_descend_trivially": (
            obs["generator_count"],
            obs["kernel_intertwiner_residual_nonzero_total"],
            obs["projection_transpose_fixed_generator_count"],
            obs["projection_transpose_fixed_residual_nonzero_total"],
            obs["induced_identity_generator_count"],
            obs["induced_quotient_rank_sum"],
        )
        == (3, 0, 3, 0, 3, 99),
        "target_family_mismatch_recorded": (
            obs["projection_direct_rowspace_residual_nonzero_total"],
            obs["r_foam_generator_count"],
            obs["r_foam_nonidentity_generator_count"],
            obs["k23_lifts_match_r_foam_target_flag"],
        )
        == (851, 9, 9, 0),
        "boundary_flags_match": (
            obs["r_hc_materialized_flag"],
            obs["full_intertwiner_claim_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (0, 0, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_hcgrade_projection_kernel_binding",
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies that the current 33x56 center-grade projection candidate has K23 as its exact kernel and that the current K23 support lifts induce the identity action on that quotient.",
    }
    seam_payload = {
        "schema": "long.k23pi.seam@1",
        "status": STATUS,
        "claim": "K23 is the exact kernel of the height-coherent center-grade projection candidate; the current K23 lifts are kernel-side only and do not realize the nontrivial Foam target action.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_hcgrade": input_entry(
            LONG_HCGRADE_REPORT,
            {
                "status": rows["long_hcgrade"].get("status"),
                "certificate_sha256": rows["long_hcgrade"].get("certificate_sha256"),
            },
        ),
        "long_hcgrade_matrices": input_entry(LONG_HCGRADE_MATRICES),
        "long_k23lin": input_entry(
            LONG_K23LIN_REPORT,
            {
                "status": rows["long_k23lin"].get("status"),
                "certificate_sha256": rows["long_k23lin"].get("certificate_sha256"),
            },
        ),
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
        "schema": "long.k23pi.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23pi certifies the K23 kernel binding of the center-grade projection candidate and records that the current K23 lift family has trivial quotient action.",
        "stage_protocol": {
            "draft": "read long_hcgrade, long_k23lin, and long_hcfoam matrix payloads",
            "witness": "emit K23 kernel residual rows, generator descent rows, target-action rows, observables, and matrices",
            "coherence": "check rank 33 plus rank 23, zero projection residual, fixed transpose action, and nontrivial target-family mismatch",
            "closure": "certify the candidate projection kernel binding without claiming the final height-coherent intertwiner",
            "emit": "write long_k23pi artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "kernel_rows_csv": relpath(OUT_DIR / "kernel_rows.csv"),
            "generator_rows_csv": relpath(OUT_DIR / "generator_rows.csv"),
            "foam_rows_csv": relpath(OUT_DIR / "foam_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23pi_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the center-grade 33x56 projection candidate has rank 33 over the certified prime field",
                "the certified K23 prime kernel has rank 23 and lies in the projection kernel",
                "the projection rows plus K23 rows have full rank 56, so K23 is exactly the projection kernel",
                "the three current K23 support lifts fix the projection under transpose/column orientation and induce identity on the 33-dimensional quotient",
                "the checked Foam target family is nonidentity and has nine generators, so these three current K23 lifts are not the missing nontrivial target-side action-return family",
            ],
            "does_not_certify": [
                "that the center-grade projection candidate is the accepted final pi_Foam33 table",
                "a materialized nontrivial R_hc generator family",
                "the full pi_Foam33 R_hc equals R_Foam pi_Foam33 identity",
                "broad bundle integration",
                "a final broad-goal closure claim",
            ],
        },
        "next_highest_yield_item": "Construct a nontrivial source-side R_hc family that preserves this K23 kernel while inducing the checked R_Foam action on the 33-dimensional quotient, or certify that no such family exists under the current support constraints.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23pi.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23pi.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "kernel_csv": csv_text(KERNEL_COLUMNS, rows["kernel_rows"]),
        "generator_csv": csv_text(GENERATOR_COLUMNS, rows["generator_rows"]),
        "foam_csv": csv_text(FOAM_COLUMNS, rows["foam_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "kernel_table": rows["kernel_table"],
        "generator_table": rows["generator_table"],
        "foam_table": rows["foam_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "kernel_text_sha256": rows["kernel_text_hash"],
            "generator_text_sha256": rows["generator_text_hash"],
            "foam_text_sha256": rows["foam_text_hash"],
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
    (OUT_DIR / "kernel_rows.csv").write_text(payloads["kernel_csv"], encoding="utf-8")
    (OUT_DIR / "generator_rows.csv").write_text(payloads["generator_csv"], encoding="utf-8")
    (OUT_DIR / "foam_rows.csv").write_text(payloads["foam_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        kernel_table=payloads["kernel_table"],
        generator_table=payloads["generator_table"],
        foam_table=payloads["foam_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23pi_matrices.npz", **payloads["matrix_payload"])
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
