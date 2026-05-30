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


THEOREM_ID = "long_k23ext"
STATUS = "SECTOR33_K23_CLOSURE60_EXTENSION_SEAM_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PRIME = 1_000_003

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23ext.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23ext.py"
LONG_K23CL_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23cl" / "report.json"
LONG_K23CL_CLOSURE_ROWS = D20_INVARIANTS / "proof_obligations" / "long_k23cl" / "closure_rows.csv"
LONG_K23CL_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23cl" / "k23cl_matrices.npz"
LONG_K23RH_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23rh" / "report.json"
LONG_K23RH_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23rh" / "k23rh_matrices.npz"

FINGERPRINT_TEXT_HASH = "9ed358cbe786178cd78c3affd93f33863f1f6ecfe3bfc224aab2d3712765c4ff"
OBSTRUCTION_TEXT_HASH = "e53c9d1582bd3b12e40df19f767624046155bd934ad49c7055efcdde874382e8"
OBS_TEXT_HASH = "afd529c1a0f0578b4048746d0e3cddbaa2907504b150e8d72bd266b65c2d4c07"
MATRIX_SHA256 = "d27a978ec189233bb214edcdb1869f10bd381d25b63041628a01a3cefddb1e57"

FINGERPRINT_COLUMNS = [
    "closure_row_id",
    "relation_id",
    "original_support_flag",
    "added_by_leak_flag",
    "target_support_count",
    "left_support_count",
    "right_support_count",
    "left_rank",
    "right_rank",
    "square_support_count",
    "square_coefficient_total_mod_p",
    "fingerprint_class_id",
]
OBSTRUCTION_COLUMNS = [
    "generator_id",
    "old_target_old_pair_residual_nonzero_count",
    "old_pair_columns_with_residual",
    "old_target_rows_with_residual",
    "block_only_extension_possible_flag",
    "cross_boundary_mixing_required_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_k23cl_certified_flag",
    "long_k23rh_certified_flag",
    "closure_support_row_count",
    "added_relation_count",
    "generator_count",
    "old_source_dimension",
    "closure_dimension",
    "old_pair_count",
    "old_target_count",
    "old_slice_residual_nonzero_total",
    "old_slice_residual_nonzero_min",
    "old_slice_residual_nonzero_max",
    "old_slice_failed_generator_count",
    "old_pair_residual_column_min",
    "old_pair_residual_column_max",
    "old_target_residual_row_min",
    "old_target_residual_row_max",
    "cross_boundary_required_generator_count",
    "fingerprint_class_count",
    "added_relation_fingerprint_class_count",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def rank_mod_p(matrix: np.ndarray, prime: int = PRIME) -> int:
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
        for row in range(rows):
            if row == rank:
                continue
            factor = int(work[row, col])
            if factor:
                work[row] = (work[row] - factor * work[rank]) % prime
        rank += 1
        if rank == rows:
            break
    return rank


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = [
        "fingerprint_table",
        "obstruction_table",
        "old_slice_residual_vector",
        "observable_vector",
    ]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def build_rows() -> dict[str, Any]:
    long_k23cl = load_json(LONG_K23CL_REPORT)
    long_k23rh = load_json(LONG_K23RH_REPORT)
    closure_rows = [{key: int(value) for key, value in row.items()} for row in read_csv_rows(LONG_K23CL_CLOSURE_ROWS)]
    with np.load(LONG_K23CL_MATRICES, allow_pickle=False) as matrices:
        product_tensor = np.asarray(matrices["closure_product_tensor"], dtype=np.int64) % PRIME
    with np.load(LONG_K23RH_MATRICES, allow_pickle=False) as matrices:
        r_hc_lifts = np.asarray(matrices["r_hc_lifts"], dtype=np.int64) % PRIME

    fingerprint_rows = []
    raw_fingerprints = []
    for closure_row in closure_rows:
        row_id = closure_row["closure_row_id"]
        left_matrix = product_tensor[:, row_id, :]
        right_matrix = product_tensor[:, :, row_id]
        square_vector = product_tensor[:, row_id, row_id]
        raw_fingerprint = (
            int(np.count_nonzero(product_tensor[row_id, :, :])),
            int(np.count_nonzero(left_matrix)),
            int(np.count_nonzero(right_matrix)),
            rank_mod_p(left_matrix),
            rank_mod_p(right_matrix),
            int(np.count_nonzero(square_vector)),
            int(np.sum(square_vector) % PRIME),
        )
        raw_fingerprints.append(raw_fingerprint)
        fingerprint_rows.append(
            {
                "closure_row_id": row_id,
                "relation_id": closure_row["relation_id"],
                "original_support_flag": closure_row["original_support_flag"],
                "added_by_leak_flag": closure_row["added_by_leak_flag"],
                "target_support_count": raw_fingerprint[0],
                "left_support_count": raw_fingerprint[1],
                "right_support_count": raw_fingerprint[2],
                "left_rank": raw_fingerprint[3],
                "right_rank": raw_fingerprint[4],
                "square_support_count": raw_fingerprint[5],
                "square_coefficient_total_mod_p": raw_fingerprint[6],
                "fingerprint_class_id": -1,
            }
        )
    class_ids = {fingerprint: index for index, fingerprint in enumerate(sorted(set(raw_fingerprints)))}
    for row, fingerprint in zip(fingerprint_rows, raw_fingerprints, strict=True):
        row["fingerprint_class_id"] = class_ids[fingerprint]

    obstruction_rows = []
    residual_counts = []
    residual_pair_counts = []
    residual_target_counts = []
    old_dim = int(r_hc_lifts.shape[1])
    old_product = product_tensor[:old_dim, :old_dim, :old_dim]
    for generator_id, lift in enumerate(r_hc_lifts):
        lhs = np.einsum("kl,lij->kij", lift, old_product, optimize=True) % PRIME
        rhs = np.empty_like(old_product)
        for target_row in range(old_dim):
            rhs[target_row] = (lift.T @ product_tensor[target_row, :old_dim, :old_dim] @ lift) % PRIME
        residual = (lhs - rhs) % PRIME
        residual_count = int(np.count_nonzero(residual))
        pair_count = int(np.count_nonzero(residual.reshape(old_dim, -1).any(axis=0)))
        target_count = int(np.count_nonzero(residual.any(axis=(1, 2))))
        residual_counts.append(residual_count)
        residual_pair_counts.append(pair_count)
        residual_target_counts.append(target_count)
        obstruction_rows.append(
            {
                "generator_id": generator_id,
                "old_target_old_pair_residual_nonzero_count": residual_count,
                "old_pair_columns_with_residual": pair_count,
                "old_target_rows_with_residual": target_count,
                "block_only_extension_possible_flag": int(residual_count == 0),
                "cross_boundary_mixing_required_flag": int(residual_count != 0),
            }
        )

    added_classes = sorted({row["fingerprint_class_id"] for row in fingerprint_rows if row["added_by_leak_flag"]})
    obs = {
        "long_k23cl_certified_flag": int(
            long_k23cl.get("status") == "SECTOR33_K23_MULTIPLICATION_CLOSURE60_CERTIFIED"
            and long_k23cl.get("all_checks_pass") is True
        ),
        "long_k23rh_certified_flag": int(
            long_k23rh.get("status") == "SECTOR33_K23_RHC_SOURCE_LIFT_CERTIFIED"
            and long_k23rh.get("all_checks_pass") is True
        ),
        "closure_support_row_count": len(closure_rows),
        "added_relation_count": sum(row["added_by_leak_flag"] for row in closure_rows),
        "generator_count": int(r_hc_lifts.shape[0]),
        "old_source_dimension": old_dim,
        "closure_dimension": int(product_tensor.shape[0]),
        "old_pair_count": old_dim * old_dim,
        "old_target_count": old_dim,
        "old_slice_residual_nonzero_total": sum(residual_counts),
        "old_slice_residual_nonzero_min": min(residual_counts),
        "old_slice_residual_nonzero_max": max(residual_counts),
        "old_slice_failed_generator_count": sum(int(count != 0) for count in residual_counts),
        "old_pair_residual_column_min": min(residual_pair_counts),
        "old_pair_residual_column_max": max(residual_pair_counts),
        "old_target_residual_row_min": min(residual_target_counts),
        "old_target_residual_row_max": max(residual_target_counts),
        "cross_boundary_required_generator_count": sum(
            int(row["cross_boundary_mixing_required_flag"]) for row in obstruction_rows
        ),
        "fingerprint_class_count": len(class_ids),
        "added_relation_fingerprint_class_count": len(added_classes),
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    fingerprint_table = table_from_rows(FINGERPRINT_COLUMNS, fingerprint_rows)
    obstruction_table = table_from_rows(OBSTRUCTION_COLUMNS, obstruction_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "fingerprint_table": fingerprint_table.astype(np.int64),
        "obstruction_table": obstruction_table.astype(np.int64),
        "old_slice_residual_vector": np.asarray(residual_counts, dtype=np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "long_k23cl": long_k23cl,
        "long_k23rh": long_k23rh,
        "fingerprint_rows": fingerprint_rows,
        "obstruction_rows": obstruction_rows,
        "obs_rows": obs_rows,
        "fingerprint_table": fingerprint_table,
        "obstruction_table": obstruction_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "fingerprint_text_hash": hashlib.sha256(
            digest_text(FINGERPRINT_COLUMNS, fingerprint_rows).encode("ascii")
        ).hexdigest(),
        "obstruction_text_hash": hashlib.sha256(
            digest_text(OBSTRUCTION_COLUMNS, obstruction_rows).encode("ascii")
        ).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": (
            obs["long_k23cl_certified_flag"],
            obs["long_k23rh_certified_flag"],
        )
        == (1, 1),
        "dimension_profile_matches": (
            obs["closure_support_row_count"],
            obs["added_relation_count"],
            obs["generator_count"],
            obs["old_source_dimension"],
            obs["closure_dimension"],
        )
        == (60, 4, 9, 56, 60),
        "old_slice_obstruction_matches": (
            obs["old_pair_count"],
            obs["old_target_count"],
            obs["old_slice_residual_nonzero_total"],
            obs["old_slice_residual_nonzero_min"],
            obs["old_slice_residual_nonzero_max"],
            obs["old_slice_failed_generator_count"],
            obs["cross_boundary_required_generator_count"],
        )
        == (3136, 56, 936661, 81629, 127386, 9, 9),
        "old_residual_coverage_matches": (
            obs["old_pair_residual_column_min"],
            obs["old_pair_residual_column_max"],
            obs["old_target_residual_row_min"],
            obs["old_target_residual_row_max"],
        )
        == (2402, 2992, 54, 56),
        "fingerprint_profile_matches": (
            obs["fingerprint_class_count"],
            obs["added_relation_fingerprint_class_count"],
        )
        == (20, 4),
        "boundary_flags_match": obs["complete_goal_claim_flag"] == 0,
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_closure60_extension_seam",
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies that a four-row-only extension cannot repair the old-target old-pair product residuals; any viable 60-row lift must mix across the 56+4 boundary.",
    }
    seam_payload = {
        "schema": "long.k23ext.seam@1",
        "status": STATUS,
        "claim": "The closed 60-relation product surface has a fixed old-slice obstruction for all nine R_hc generators, so a viable extension cannot act only on the four added rows.",
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
        "schema": "long.k23ext.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23ext certifies the first 60-row extension seam for the sector33 K23 product surface.",
        "stage_protocol": {
            "draft": "read long_k23cl, the 60-row product tensor, and the nine source-side R_hc lifts",
            "witness": "emit relation fingerprint rows, generator obstruction rows, observables, and matrix payloads",
            "coherence": "check input certificates, dimension counts, old-slice residual counts, and fingerprint class counts",
            "closure": "certify that any product-preserving 60-row lift must mix across the 56+4 boundary",
            "emit": "write long_k23ext artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "relation_fingerprints_csv": relpath(OUT_DIR / "relation_fingerprints.csv"),
            "extension_obstructions_csv": relpath(OUT_DIR / "extension_obstructions.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23ext_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "all nine current R_hc generators have nonzero old-target old-pair residuals on the 60-relation product surface",
                "the residual counts range from 81,629 to 127,386, with total 936,661",
                "the obstruction slice touches 54 to 56 old target rows across the nine generators",
                "any product-preserving 60-row lift must use cross-boundary mixing rather than only assigning an action to the four added rows",
                "the 60 relation rows collapse into 20 product-fingerprint classes, with the four added rows occupying four distinct classes",
            ],
            "does_not_certify": [
                "existence or nonexistence of a fully mixed 60x60 product-preserving lift",
                "a solution for the cross-boundary entries",
                "a final operator carrier",
                "bundle-wide integration",
                "a final broad-goal closure claim",
            ],
        },
        "next_highest_yield_item": "Set up the fully mixed 60x60 extension equations using the old-slice obstruction as a guardrail, then solve or demote the cross-boundary lift candidate by certificate.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23ext.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23ext.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "fingerprints_csv": csv_text(FINGERPRINT_COLUMNS, rows["fingerprint_rows"]),
        "obstructions_csv": csv_text(OBSTRUCTION_COLUMNS, rows["obstruction_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "fingerprint_table": rows["fingerprint_table"],
        "obstruction_table": rows["obstruction_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "fingerprint_text_sha256": rows["fingerprint_text_hash"],
            "obstruction_text_sha256": rows["obstruction_text_hash"],
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
    (OUT_DIR / "relation_fingerprints.csv").write_text(payloads["fingerprints_csv"], encoding="utf-8")
    (OUT_DIR / "extension_obstructions.csv").write_text(payloads["obstructions_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        fingerprint_table=payloads["fingerprint_table"],
        obstruction_table=payloads["obstruction_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23ext_matrices.npz", **payloads["matrix_payload"])
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
