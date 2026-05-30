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


THEOREM_ID = "long_k23tgt"
STATUS = "SECTOR33_K23_TARGET_UNIT_APERTURE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PRIME = 1_000_003

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23tgt.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23tgt.py"
LONG_K23UNIT_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23unit" / "report.json"
LONG_K23UNIT_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23unit" / "k23unit_matrices.npz"
LONG_K23RH_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23rh" / "report.json"
LONG_K23RH_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23rh" / "k23rh_matrices.npz"

FIXED_TEXT_HASH = "996ba176421ba67f0d9f56fccbe2ac2adfd5b8aee9d86cad2bacc139db8c6b1e"
PROJECTED_UNIT_TEXT_HASH = "7a6dc6806a1fbfeba698b37340dd4142ea33ca9ca7a12d0236ef20beae56997e"
GENERATOR_TEXT_HASH = "39dd93d5fae4d8ff2f93669b30d364bd179dca4401985ba512d211814e9630e6"
OBS_TEXT_HASH = "4b68069ad135efd0456b08cba11b0ac9b208e12494c5fd02540f7cf3470cede1"
MATRIX_SHA256 = "905f3880b2b711f9aab3757a5988c3b00b0c1699a8f66118c32b7a5e91286f30"

FIXED_COLUMNS = [
    "basis_id",
    "target_row_id",
    "coordinate_mod",
    "support_count",
]
PROJECTED_UNIT_COLUMNS = [
    "target_row_id",
    "projected_unit_value",
    "common_fixed_basis_row_flag",
    "projected_unit_support_flag",
]
GENERATOR_COLUMNS = [
    "generator_id",
    "r_foam_rank",
    "individual_fixed_dimension",
    "projected_unit_residual_nonzero_count",
    "projected_unit_fixed_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_k23unit_certified_flag",
    "long_k23rh_certified_flag",
    "target_dimension",
    "generator_count",
    "stacked_fixed_equation_row_count",
    "stacked_fixed_equation_rank",
    "common_fixed_dimension",
    "common_fixed_basis_row_count",
    "individual_fixed_dimension_min",
    "individual_fixed_dimension_max",
    "r_foam_rank_sum",
    "projected_unit_support_count",
    "projected_unit_common_fixed_coordinate_count",
    "projected_unit_residual_nonzero_total",
    "projected_unit_in_common_fixed_space_flag",
    "target_has_unit_aperture_flag",
    "new_projection_columns_can_repair_flag",
    "old_projection_must_change_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def rank_mod(matrix: np.ndarray, prime: int = PRIME) -> int:
    _rref, rank, _pivots = rref(matrix, prime)
    return rank


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


def nullspace_basis(matrix: np.ndarray) -> np.ndarray:
    echelon, rank, pivots = rref(matrix)
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
    if not basis:
        return np.zeros((0, cols), dtype=np.int64)
    return np.asarray(basis, dtype=np.int64)


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = [
        "common_fixed_basis",
        "projected_unit_vector",
        "generator_table",
        "observable_vector",
    ]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def build_rows() -> dict[str, Any]:
    long_k23unit = load_json(LONG_K23UNIT_REPORT)
    long_k23rh = load_json(LONG_K23RH_REPORT)
    with np.load(LONG_K23RH_MATRICES, allow_pickle=False) as matrices:
        r_foam_matrices = np.asarray(matrices["r_foam_matrices"], dtype=np.int64) % PRIME
    with np.load(LONG_K23UNIT_MATRICES, allow_pickle=False) as matrices:
        projected_unit = np.asarray(matrices["projected_unit_vector"], dtype=np.int64) % PRIME
        unit_vector = np.asarray(matrices["unit_vector"], dtype=np.int64) % PRIME

    target_dim = int(r_foam_matrices.shape[1])
    identity = np.eye(target_dim, dtype=np.int64)
    fixed_equations = np.vstack([(generator - identity) % PRIME for generator in r_foam_matrices])
    common_fixed_basis = nullspace_basis(fixed_equations)
    common_fixed_rows = set(np.nonzero(np.any(common_fixed_basis != 0, axis=0))[0].tolist())
    projected_unit_support = set(np.nonzero(projected_unit)[0].tolist())

    fixed_rows = []
    for basis_id, vector in enumerate(common_fixed_basis):
        support = np.nonzero(vector)[0].tolist()
        for target_row_id in support:
            fixed_rows.append(
                {
                    "basis_id": basis_id,
                    "target_row_id": int(target_row_id),
                    "coordinate_mod": int(vector[target_row_id]),
                    "support_count": len(support),
                }
            )
    projected_unit_rows = [
        {
            "target_row_id": target_row_id,
            "projected_unit_value": int(projected_unit[target_row_id]),
            "common_fixed_basis_row_flag": int(target_row_id in common_fixed_rows),
            "projected_unit_support_flag": int(target_row_id in projected_unit_support),
        }
        for target_row_id in range(target_dim)
        if target_row_id in common_fixed_rows or target_row_id in projected_unit_support
    ]
    generator_rows = []
    individual_fixed_dimensions = []
    residual_counts = []
    rank_sum = 0
    for generator_id, generator in enumerate(r_foam_matrices):
        generator_rank = rank_mod(generator)
        fixed_rank = rank_mod((generator - identity) % PRIME)
        individual_fixed_dimension = target_dim - fixed_rank
        residual_count = int(np.count_nonzero((generator @ projected_unit - projected_unit) % PRIME))
        rank_sum += generator_rank
        individual_fixed_dimensions.append(individual_fixed_dimension)
        residual_counts.append(residual_count)
        generator_rows.append(
            {
                "generator_id": generator_id,
                "r_foam_rank": generator_rank,
                "individual_fixed_dimension": individual_fixed_dimension,
                "projected_unit_residual_nonzero_count": residual_count,
                "projected_unit_fixed_flag": int(residual_count == 0),
            }
        )

    basis_span_rank = rank_mod(common_fixed_basis.T) if common_fixed_basis.size else 0
    augmented_span_rank = rank_mod(np.column_stack([common_fixed_basis.T, projected_unit]))
    projected_unit_in_fixed_space = int(augmented_span_rank == basis_span_rank)
    obs = {
        "long_k23unit_certified_flag": int(
            long_k23unit.get("status") == "SECTOR33_K23_CLOSURE60_UNIT_PROJECTION_OBSTRUCTION_CERTIFIED"
            and long_k23unit.get("all_checks_pass") is True
        ),
        "long_k23rh_certified_flag": int(
            long_k23rh.get("status") == "SECTOR33_K23_RHC_SOURCE_LIFT_CERTIFIED"
            and long_k23rh.get("all_checks_pass") is True
        ),
        "target_dimension": target_dim,
        "generator_count": int(r_foam_matrices.shape[0]),
        "stacked_fixed_equation_row_count": int(fixed_equations.shape[0]),
        "stacked_fixed_equation_rank": rank_mod(fixed_equations),
        "common_fixed_dimension": int(common_fixed_basis.shape[0]),
        "common_fixed_basis_row_count": len(fixed_rows),
        "individual_fixed_dimension_min": min(individual_fixed_dimensions),
        "individual_fixed_dimension_max": max(individual_fixed_dimensions),
        "r_foam_rank_sum": rank_sum,
        "projected_unit_support_count": int(np.count_nonzero(projected_unit)),
        "projected_unit_common_fixed_coordinate_count": len(projected_unit_support & common_fixed_rows),
        "projected_unit_residual_nonzero_total": sum(residual_counts),
        "projected_unit_in_common_fixed_space_flag": projected_unit_in_fixed_space,
        "target_has_unit_aperture_flag": int(common_fixed_basis.shape[0] > 0),
        "new_projection_columns_can_repair_flag": int(np.count_nonzero(unit_vector[56:]) != 0),
        "old_projection_must_change_flag": int(np.count_nonzero(unit_vector[56:]) == 0 and not projected_unit_in_fixed_space),
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    fixed_table = table_from_rows(FIXED_COLUMNS, fixed_rows)
    projected_unit_table = table_from_rows(PROJECTED_UNIT_COLUMNS, projected_unit_rows)
    generator_table = table_from_rows(GENERATOR_COLUMNS, generator_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "common_fixed_basis": common_fixed_basis.astype(np.int64),
        "projected_unit_vector": projected_unit.astype(np.int64),
        "generator_table": generator_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "long_k23unit": long_k23unit,
        "long_k23rh": long_k23rh,
        "fixed_rows": fixed_rows,
        "projected_unit_rows": projected_unit_rows,
        "generator_rows": generator_rows,
        "obs_rows": obs_rows,
        "fixed_table": fixed_table,
        "projected_unit_table": projected_unit_table,
        "generator_table": generator_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "fixed_text_hash": hashlib.sha256(digest_text(FIXED_COLUMNS, fixed_rows).encode("ascii")).hexdigest(),
        "projected_unit_text_hash": hashlib.sha256(
            digest_text(PROJECTED_UNIT_COLUMNS, projected_unit_rows).encode("ascii")
        ).hexdigest(),
        "generator_text_hash": hashlib.sha256(digest_text(GENERATOR_COLUMNS, generator_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": (
            obs["long_k23unit_certified_flag"],
            obs["long_k23rh_certified_flag"],
        )
        == (1, 1),
        "fixed_space_profile_matches": (
            obs["target_dimension"],
            obs["generator_count"],
            obs["stacked_fixed_equation_row_count"],
            obs["stacked_fixed_equation_rank"],
            obs["common_fixed_dimension"],
            obs["common_fixed_basis_row_count"],
        )
        == (33, 9, 297, 30, 3, 3),
        "generator_profile_matches": (
            obs["individual_fixed_dimension_min"],
            obs["individual_fixed_dimension_max"],
            obs["r_foam_rank_sum"],
        )
        == (17, 17, 297),
        "projected_unit_profile_matches": (
            obs["projected_unit_support_count"],
            obs["projected_unit_common_fixed_coordinate_count"],
            obs["projected_unit_residual_nonzero_total"],
            obs["projected_unit_in_common_fixed_space_flag"],
            obs["target_has_unit_aperture_flag"],
        )
        == (4, 0, 37, 0, 1),
        "repair_boundary_matches": (
            obs["new_projection_columns_can_repair_flag"],
            obs["old_projection_must_change_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (0, 1, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_target_unit_aperture",
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies that the target action has a 3-dimensional common fixed aperture, but the current projected unit misses it; repair requires changing the old projection, not merely adding new projection columns.",
    }
    seam_payload = {
        "schema": "long.k23tgt.seam@1",
        "status": STATUS,
        "claim": "The 33-dimensional target action has common fixed rows 0, 1, and 17, while the current projected closure60 unit lies outside that fixed aperture.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23unit": input_entry(
            LONG_K23UNIT_REPORT,
            {
                "status": rows["long_k23unit"].get("status"),
                "certificate_sha256": rows["long_k23unit"].get("certificate_sha256"),
            },
        ),
        "long_k23unit_matrices": input_entry(LONG_K23UNIT_MATRICES),
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
        "schema": "long.k23tgt.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23tgt certifies the target-side unit aperture and current projection miss.",
        "stage_protocol": {
            "draft": "read long_k23unit and the checked target action matrices",
            "witness": "emit common fixed-basis rows, current projected-unit rows, generator fixed-dimension rows, and observables",
            "coherence": "check stacked fixed-space rank, individual fixed dimensions, projected-unit membership, and repair boundary flags",
            "closure": "certify that the target side has a repair aperture while the old projection must change",
            "emit": "write long_k23tgt artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "fixed_basis_csv": relpath(OUT_DIR / "fixed_basis.csv"),
            "projected_unit_csv": relpath(OUT_DIR / "projected_unit.csv"),
            "generator_rows_csv": relpath(OUT_DIR / "generator_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23tgt_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the common fixed subspace of the nine checked target generators has dimension 3",
                "the fixed aperture is represented by target rows 0, 1, and 17",
                "the current projected closure60 unit is supported on target rows 6, 10, 28, and 32",
                "the current projected unit is not in the common fixed aperture",
                "because the closure60 unit has no support on the four appended rows, adding new projection columns cannot repair the current projection miss",
            ],
            "does_not_certify": [
                "a replacement projection",
                "a product action for a replacement projection",
                "that the target action must be demoted absolutely",
                "bundle-wide integration",
                "a final broad-goal closure claim",
            ],
        },
        "next_highest_yield_item": "Construct a replacement projection candidate that maps the closure60 unit into the 3-dimensional fixed aperture while preserving rank 33, then test product-action compatibility against that repaired projection.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23tgt.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23tgt.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "fixed_csv": csv_text(FIXED_COLUMNS, rows["fixed_rows"]),
        "projected_unit_csv": csv_text(PROJECTED_UNIT_COLUMNS, rows["projected_unit_rows"]),
        "generator_csv": csv_text(GENERATOR_COLUMNS, rows["generator_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "fixed_table": rows["fixed_table"],
        "projected_unit_table": rows["projected_unit_table"],
        "generator_table": rows["generator_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "fixed_text_sha256": rows["fixed_text_hash"],
            "projected_unit_text_sha256": rows["projected_unit_text_hash"],
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
    (OUT_DIR / "fixed_basis.csv").write_text(payloads["fixed_csv"], encoding="utf-8")
    (OUT_DIR / "projected_unit.csv").write_text(payloads["projected_unit_csv"], encoding="utf-8")
    (OUT_DIR / "generator_rows.csv").write_text(payloads["generator_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        fixed_table=payloads["fixed_table"],
        projected_unit_table=payloads["projected_unit_table"],
        generator_table=payloads["generator_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23tgt_matrices.npz", **payloads["matrix_payload"])
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
