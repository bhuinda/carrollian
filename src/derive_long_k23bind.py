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


THEOREM_ID = "long_k23bind"
STATUS = "SECTOR33_K23_BINARY_SUPPORT_BINDING_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23bind.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23bind.py"
LONG_K23_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23" / "report.json"
LONG_K23_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23" / "k23_matrices.npz"
LONG_K23SRC_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23src" / "report.json"
LONG_K23SRC_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23src" / "k23src_matrices.npz"
LONG_HCSUPP_SUPPORT = D20_INVARIANTS / "proof_obligations" / "long_hcsupp" / "support_rows.csv"

SUPPORT_TEXT_HASH = "62a8c37613702e2e51e390d7676f8eb01e01a7fe9286fd6fea24bb90b2f4b44e"
COORDINATE_TEXT_HASH = "15454672525602d71b736d2918d2376fdd6c8aaa4c88893efaa365229529cf0d"
ROW_CHECK_TEXT_HASH = "2d540f33eb1a016c630dbd10e808bc686283e329938c1ab7cd7a12b036c55ae2"
OBS_TEXT_HASH = "f856b621b33cae3dd360322904b04dc3195e4524620711c22b9bda9758b68eb5"
MATRIX_SHA256 = "7ce48a63cda5258dfd356794a5f990a783b1db4897dd768d627b3e3e4177bb23"

SUPPORT_COLUMNS = [
    "support_row_id",
    "relation_id",
    "block_i",
    "rep4",
    "pivot_flag",
    "binding_source_mask",
    "binding_source_weight",
    "active_binding_flag",
]
COORDINATE_COLUMNS = [
    "source_coordinate",
    "target_column_weight",
    "support_preimage_mask",
    "support_preimage_weight",
]
ROW_CHECK_COLUMNS = [
    "k23_basis_row_id",
    "target_source_mask",
    "reconstructed_source_mask",
    "residual_source_mask",
    "residual_weight",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_k23_certified_flag",
    "long_k23src_certified_flag",
    "support_row_count",
    "k23_basis_row_count",
    "source_coordinate_count",
    "support_normalized_rank",
    "pivot_column_count",
    "binding_matrix_row_count",
    "binding_matrix_column_count",
    "active_binding_support_row_count",
    "inactive_binding_support_row_count",
    "binding_nonzero_entry_count",
    "coordinate_preimage_nonempty_count",
    "row_check_count",
    "zero_residual_row_count",
    "max_residual_weight",
    "reconstructed_image_rank",
    "reconstructed_nonzero_row_count",
    "binary_support_binding_certified_flag",
    "signed_integral_binding_certified_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def row_mask(row: np.ndarray) -> int:
    mask = 0
    for index, value in enumerate(np.asarray(row, dtype=np.uint8).tolist()):
        if int(value) & 1:
            mask |= 1 << index
    return mask


def gf2_rank(matrix: np.ndarray) -> int:
    work = np.asarray(matrix, dtype=np.uint8).copy() % 2
    row_count, column_count = work.shape
    rank = 0
    for column in range(column_count):
        candidates = np.flatnonzero(work[rank:, column])
        if candidates.size == 0:
            continue
        source_row = rank + int(candidates[0])
        if source_row != rank:
            work[[rank, source_row]] = work[[source_row, rank]]
        for row in range(row_count):
            if row != rank and work[row, column]:
                work[row] ^= work[rank]
        rank += 1
        if rank == row_count:
            break
    return rank


def gf2_rref_with_transform(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray, list[int]]:
    work = np.asarray(matrix, dtype=np.uint8).copy() % 2
    row_count, column_count = work.shape
    transform = np.eye(row_count, dtype=np.uint8)
    pivots: list[int] = []
    pivot_row = 0
    for column in range(column_count):
        candidates = np.flatnonzero(work[pivot_row:, column])
        if candidates.size == 0:
            continue
        source_row = pivot_row + int(candidates[0])
        if source_row != pivot_row:
            work[[pivot_row, source_row]] = work[[source_row, pivot_row]]
            transform[[pivot_row, source_row]] = transform[[source_row, pivot_row]]
        for row in range(row_count):
            if row != pivot_row and work[row, column]:
                work[row] ^= work[pivot_row]
                transform[row] ^= transform[pivot_row]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == row_count:
            break
    return work, transform, pivots


def masks_to_table(masks: np.ndarray, width: int = 24) -> np.ndarray:
    return np.asarray(
        [[(int(mask) >> coord) & 1 for coord in range(width)] for mask in np.asarray(masks, dtype=np.int64).tolist()],
        dtype=np.uint8,
    )


def support_mask(values: list[int]) -> int:
    mask = 0
    for value in values:
        mask |= 1 << int(value)
    return mask


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = [
        "support_kernel",
        "row_operation_matrix",
        "pivot_columns",
        "binding_matrix",
        "target_source_images",
        "reconstructed_source_images",
        "residual_source_images",
        "observable_vector",
    ]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def solve_binding(support_kernel: np.ndarray, target_matrix: np.ndarray) -> dict[str, Any]:
    rref, transform, pivots = gf2_rref_with_transform(support_kernel)
    transformed_target = (transform @ target_matrix) % 2
    binding = np.zeros((support_kernel.shape[1], target_matrix.shape[1]), dtype=np.uint8)
    for rref_row, pivot_column in enumerate(pivots):
        binding[pivot_column] = transformed_target[rref_row]
    reconstructed = (support_kernel @ binding) % 2
    residual = reconstructed ^ target_matrix
    return {
        "rref": rref,
        "transform": transform,
        "pivots": pivots,
        "binding": binding,
        "reconstructed": reconstructed,
        "residual": residual,
    }


def build_rows() -> dict[str, Any]:
    long_k23 = load_json(LONG_K23_REPORT)
    long_k23src = load_json(LONG_K23SRC_REPORT)
    support_rows_raw = [{key: int(value) for key, value in row.items()} for row in read_csv_rows(LONG_HCSUPP_SUPPORT)]
    with np.load(LONG_K23_MATRICES, allow_pickle=False) as matrices:
        kernel_basis = np.asarray(matrices["kernel_basis"], dtype=np.int64)
    with np.load(LONG_K23SRC_MATRICES, allow_pickle=False) as matrices:
        target_source_images = np.asarray(matrices["extension_source_images"], dtype=np.int64)
    support_kernel = (kernel_basis != 0).astype(np.uint8)
    target_matrix = masks_to_table(target_source_images)
    solved = solve_binding(support_kernel, target_matrix)
    reconstructed_masks = np.asarray([row_mask(row) for row in solved["reconstructed"]], dtype=np.int64)
    residual_masks = np.asarray([row_mask(row) for row in solved["residual"]], dtype=np.int64)
    pivot_set = set(solved["pivots"])
    support_rows = []
    for support_row in support_rows_raw:
        row_id = int(support_row["row_id"])
        binding_mask = row_mask(solved["binding"][row_id])
        support_rows.append(
            {
                "support_row_id": row_id,
                "relation_id": int(support_row["relation_id"]),
                "block_i": int(support_row["block_i"]),
                "rep4": int(support_row["rep4"]),
                "pivot_flag": int(row_id in pivot_set),
                "binding_source_mask": binding_mask,
                "binding_source_weight": int(binding_mask).bit_count(),
                "active_binding_flag": int(binding_mask != 0),
            }
        )
    coordinate_rows = []
    for source_coordinate in range(target_matrix.shape[1]):
        support_sources = np.flatnonzero(solved["binding"][:, source_coordinate]).astype(int).tolist()
        coordinate_rows.append(
            {
                "source_coordinate": source_coordinate,
                "target_column_weight": int(target_matrix[:, source_coordinate].sum()),
                "support_preimage_mask": support_mask(support_sources),
                "support_preimage_weight": len(support_sources),
            }
        )
    row_check_rows = []
    for row_id, target_mask in enumerate(target_source_images.tolist()):
        residual_mask = int(residual_masks[row_id])
        row_check_rows.append(
            {
                "k23_basis_row_id": row_id,
                "target_source_mask": int(target_mask),
                "reconstructed_source_mask": int(reconstructed_masks[row_id]),
                "residual_source_mask": residual_mask,
                "residual_weight": residual_mask.bit_count(),
            }
        )
    obs = {
        "long_k23_certified_flag": int(
            long_k23.get("status") == "SECTOR33_K23_PUNCTURED_MOG_SYZYGY_APERTURE_TARGET_CERTIFIED"
            and long_k23.get("all_checks_pass") is True
        ),
        "long_k23src_certified_flag": int(
            long_k23src.get("status") == "SECTOR33_K23_SOURCE_W24_RANK12_EXTENSION_CERTIFIED"
            and long_k23src.get("all_checks_pass") is True
        ),
        "support_row_count": len(support_rows_raw),
        "k23_basis_row_count": support_kernel.shape[0],
        "source_coordinate_count": target_matrix.shape[1],
        "support_normalized_rank": gf2_rank(support_kernel),
        "pivot_column_count": len(solved["pivots"]),
        "binding_matrix_row_count": solved["binding"].shape[0],
        "binding_matrix_column_count": solved["binding"].shape[1],
        "active_binding_support_row_count": sum(row["active_binding_flag"] for row in support_rows),
        "inactive_binding_support_row_count": sum(1 - row["active_binding_flag"] for row in support_rows),
        "binding_nonzero_entry_count": int(solved["binding"].sum()),
        "coordinate_preimage_nonempty_count": sum(int(row["support_preimage_weight"] > 0) for row in coordinate_rows),
        "row_check_count": len(row_check_rows),
        "zero_residual_row_count": sum(int(row["residual_weight"] == 0) for row in row_check_rows),
        "max_residual_weight": max(row["residual_weight"] for row in row_check_rows),
        "reconstructed_image_rank": gf2_rank(masks_to_table(reconstructed_masks)),
        "reconstructed_nonzero_row_count": sum(int(mask != 0) for mask in reconstructed_masks.tolist()),
        "binary_support_binding_certified_flag": int(np.array_equal(solved["reconstructed"], target_matrix)),
        "signed_integral_binding_certified_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    matrix_payload = {
        "support_kernel": support_kernel.astype(np.int64),
        "row_operation_matrix": solved["transform"].astype(np.int64),
        "pivot_columns": np.asarray(solved["pivots"], dtype=np.int64),
        "binding_matrix": solved["binding"].astype(np.int64),
        "target_source_images": target_source_images.astype(np.int64),
        "reconstructed_source_images": reconstructed_masks.astype(np.int64),
        "residual_source_images": residual_masks.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "long_k23": long_k23,
        "long_k23src": long_k23src,
        "support_rows": support_rows,
        "coordinate_rows": coordinate_rows,
        "row_check_rows": row_check_rows,
        "obs_rows": obs_rows,
        "support_table": table_from_rows(SUPPORT_COLUMNS, support_rows),
        "coordinate_table": table_from_rows(COORDINATE_COLUMNS, coordinate_rows),
        "row_check_table": table_from_rows(ROW_CHECK_COLUMNS, row_check_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "pivot_columns": solved["pivots"],
        "support_text_hash": hashlib.sha256(digest_text(SUPPORT_COLUMNS, support_rows).encode("ascii")).hexdigest(),
        "coordinate_text_hash": hashlib.sha256(digest_text(COORDINATE_COLUMNS, coordinate_rows).encode("ascii")).hexdigest(),
        "row_check_text_hash": hashlib.sha256(digest_text(ROW_CHECK_COLUMNS, row_check_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": (obs["long_k23_certified_flag"], obs["long_k23src_certified_flag"]) == (1, 1),
        "support_shape_matches": (
            obs["support_row_count"],
            obs["k23_basis_row_count"],
            obs["source_coordinate_count"],
            obs["support_normalized_rank"],
            obs["pivot_column_count"],
        )
        == (56, 23, 24, 23, 23),
        "binding_matrix_shape_matches": (
            obs["binding_matrix_row_count"],
            obs["binding_matrix_column_count"],
            obs["active_binding_support_row_count"],
            obs["inactive_binding_support_row_count"],
            obs["binding_nonzero_entry_count"],
            obs["coordinate_preimage_nonempty_count"],
        )
        == (56, 24, 13, 43, 112, 24),
        "row_reconstruction_is_exact": (
            obs["row_check_count"],
            obs["zero_residual_row_count"],
            obs["max_residual_weight"],
            obs["reconstructed_image_rank"],
            obs["reconstructed_nonzero_row_count"],
            obs["binary_support_binding_certified_flag"],
        )
        == (23, 23, 0, 12, 12, 1),
        "signed_binding_remains_open": (
            obs["signed_integral_binding_certified_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (0, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_binary_support_binding",
        "summary": obs,
        "pivot_columns": rows["pivot_columns"],
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies a binary support-normalized map from the 56 sector33 support coordinates to the 24 source endpoint coordinates; signed integral lifting remains open.",
    }
    seam_payload = {
        "schema": "long.k23bind.seam@1",
        "status": STATUS,
        "claim": "The rank-12 source-side K23 assignment is reproduced exactly by a 56-support binary binding matrix against the support-normalized K23 basis.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23": input_entry(
            LONG_K23_REPORT,
            {
                "status": rows["long_k23"].get("status"),
                "certificate_sha256": rows["long_k23"].get("certificate_sha256"),
            },
        ),
        "long_k23_matrices": input_entry(LONG_K23_MATRICES),
        "long_k23src": input_entry(
            LONG_K23SRC_REPORT,
            {
                "status": rows["long_k23src"].get("status"),
                "certificate_sha256": rows["long_k23src"].get("certificate_sha256"),
            },
        ),
        "long_k23src_matrices": input_entry(LONG_K23SRC_MATRICES),
        "long_hcsupp_support": input_entry(LONG_HCSUPP_SUPPORT),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23bind.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23bind certifies that the 56 sector33 support coordinates admit a binary support-normalized binding onto the rank-12 source endpoint assignment.",
        "stage_protocol": {
            "draft": "read long_k23, long_k23src, K23 matrices, source assignment, and sector33 support rows",
            "witness": "emit support binding rows, source-coordinate preimage rows, row reconstruction checks, observables, and matrices",
            "coherence": "check support rank, pivot columns, exact K23 row reconstruction, and zero residual",
            "closure": "certify binary support binding while keeping signed/integral lifting and module action open",
            "emit": "write long_k23bind artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "support_binding_rows_csv": relpath(OUT_DIR / "support_binding_rows.csv"),
            "coordinate_preimage_rows_csv": relpath(OUT_DIR / "coordinate_preimage_rows.csv"),
            "row_check_rows_csv": relpath(OUT_DIR / "row_check_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23bind_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the support-normalized K23 basis has rank 23 over 56 support coordinates",
                "an explicit 56-by-24 binary binding matrix exists",
                "the binding reconstructs all 23 source-assignment rows with zero residual",
                "the reconstructed image has rank 12 and is the same source-side assignment certified by long_k23src",
            ],
            "does_not_certify": [
                "a signed or integral lift using the prime-field coefficients",
                "uniqueness or canonicity of the support binding",
                "a one-hot partition of support coordinates",
                "an M23 module action on K23",
                "a rebuild of d20.json or broad bundle closure",
            ],
        },
        "next_highest_yield_item": "Attempt the signed prime-field lift of this binary support binding: solve the same 56-to-24 map against the actual K23 coefficients and compare its reduction to the certified binary binding.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23bind.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23bind.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "support_csv": csv_text(SUPPORT_COLUMNS, rows["support_rows"]),
        "coordinate_csv": csv_text(COORDINATE_COLUMNS, rows["coordinate_rows"]),
        "row_check_csv": csv_text(ROW_CHECK_COLUMNS, rows["row_check_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "support_table": rows["support_table"],
        "coordinate_table": rows["coordinate_table"],
        "row_check_table": rows["row_check_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "support_text_sha256": rows["support_text_hash"],
            "coordinate_text_sha256": rows["coordinate_text_hash"],
            "row_check_text_sha256": rows["row_check_text_hash"],
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
    (OUT_DIR / "support_binding_rows.csv").write_text(payloads["support_csv"], encoding="utf-8")
    (OUT_DIR / "coordinate_preimage_rows.csv").write_text(payloads["coordinate_csv"], encoding="utf-8")
    (OUT_DIR / "row_check_rows.csv").write_text(payloads["row_check_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        support_table=payloads["support_table"],
        coordinate_table=payloads["coordinate_table"],
        row_check_table=payloads["row_check_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23bind_matrices.npz", **payloads["matrix_payload"])
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
