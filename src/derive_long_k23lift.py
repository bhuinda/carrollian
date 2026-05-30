from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
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


THEOREM_ID = "long_k23lift"
STATUS = "SECTOR33_K23_SIGNED_PRIME_SUPPORT_LIFT_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PRIME = 1_000_003

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23lift.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23lift.py"
LONG_K23_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23" / "report.json"
LONG_K23_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23" / "k23_matrices.npz"
LONG_K23SRC_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23src" / "report.json"
LONG_K23SRC_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23src" / "k23src_matrices.npz"
LONG_K23BIND_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23bind" / "report.json"
LONG_K23BIND_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23bind" / "k23bind_matrices.npz"
LONG_HCSUPP_SUPPORT = D20_INVARIANTS / "proof_obligations" / "long_hcsupp" / "support_rows.csv"

SUPPORT_TEXT_HASH = "174d744a255b47d49b6f45d156cef18f5234ad0a74b9e9c0dbda2c9f1acf64ca"
ENTRY_TEXT_HASH = "6dfa95ecaef64b6d341c95f309131fbb119666ffcc47c47ca5fb1d86a88eb632"
ROW_CHECK_TEXT_HASH = "2d540f33eb1a016c630dbd10e808bc686283e329938c1ab7cd7a12b036c55ae2"
COEFF_TEXT_HASH = "c369e4e4fd795f29237ac3792424a6965860b570136fa29af428f9241155295a"
OBS_TEXT_HASH = "3322a32aca28d9a1e521c632d36a4ca90c7ae8613487dd10f2beca0ad9cc99f3"
MATRIX_SHA256 = "ef10af53bb8dc6c3a8600d53072467c5671e37128ade81aa93f1f751f0c846e6"

SUPPORT_COLUMNS = [
    "support_row_id",
    "relation_id",
    "block_i",
    "rep4",
    "pivot_flag",
    "binary_binding_mask",
    "signed_support_mask",
    "support_match_flag",
    "signed_support_weight",
    "signed_sum",
    "signed_l1",
    "min_signed",
    "max_signed",
    "negative_count",
    "positive_count",
]
ENTRY_COLUMNS = [
    "entry_id",
    "support_row_id",
    "source_coordinate",
    "coefficient_mod",
    "coefficient_signed",
    "binary_binding_entry",
    "support_match_flag",
    "residue_parity",
]
ROW_CHECK_COLUMNS = [
    "k23_basis_row_id",
    "target_source_mask",
    "reconstructed_source_mask",
    "residual_nonzero_count",
    "residual_mod_sum",
]
COEFF_COLUMNS = ["coefficient_signed", "entry_count"]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_k23_certified_flag",
    "long_k23src_certified_flag",
    "long_k23bind_certified_flag",
    "prime_field",
    "support_row_count",
    "k23_basis_row_count",
    "source_coordinate_count",
    "prime_rank",
    "pivot_column_count",
    "signed_lift_row_count",
    "signed_lift_column_count",
    "active_signed_support_row_count",
    "inactive_signed_support_row_count",
    "signed_lift_nonzero_entry_count",
    "binary_binding_nonzero_entry_count",
    "support_overlap_entry_count",
    "signed_only_entry_count",
    "binary_only_entry_count",
    "support_profile_match_flag",
    "prime_residual_nonzero_entry_count",
    "zero_residual_row_count",
    "reconstructed_image_rank",
    "coefficient_distinct_count",
    "coefficient_min_signed",
    "coefficient_max_signed",
    "negative_coefficient_count",
    "positive_coefficient_count",
    "signed_l1_total",
    "residue_parity_mismatch_count",
    "signed_prime_lift_certified_flag",
    "parity_is_algebraic_reduction_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def mod_inv(value: int) -> int:
    return pow(int(value) % PRIME, PRIME - 2, PRIME)


def signed_value(value: int) -> int:
    value = int(value) % PRIME
    if value > PRIME // 2:
        return value - PRIME
    return value


def row_mask(row: np.ndarray) -> int:
    mask = 0
    for index, value in enumerate(np.asarray(row).tolist()):
        if int(value) != 0:
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


def prime_rref_with_transform(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray, list[int]]:
    work = np.asarray(matrix, dtype=np.int64).copy() % PRIME
    row_count, column_count = work.shape
    transform = np.eye(row_count, dtype=np.int64)
    pivots: list[int] = []
    pivot_row = 0
    for column in range(column_count):
        source_row = -1
        for row in range(pivot_row, row_count):
            if int(work[row, column]) % PRIME != 0:
                source_row = row
                break
        if source_row < 0:
            continue
        if source_row != pivot_row:
            work[[pivot_row, source_row]] = work[[source_row, pivot_row]]
            transform[[pivot_row, source_row]] = transform[[source_row, pivot_row]]
        factor = mod_inv(int(work[pivot_row, column]))
        work[pivot_row] = (work[pivot_row] * factor) % PRIME
        transform[pivot_row] = (transform[pivot_row] * factor) % PRIME
        for row in range(row_count):
            if row != pivot_row and int(work[row, column]) % PRIME != 0:
                factor = int(work[row, column]) % PRIME
                work[row] = (work[row] - factor * work[pivot_row]) % PRIME
                transform[row] = (transform[row] - factor * transform[pivot_row]) % PRIME
        pivots.append(column)
        pivot_row += 1
        if pivot_row == row_count:
            break
    return work, transform, pivots


def masks_to_table(masks: np.ndarray, width: int = 24) -> np.ndarray:
    return np.asarray(
        [[(int(mask) >> coord) & 1 for coord in range(width)] for mask in np.asarray(masks, dtype=np.int64).tolist()],
        dtype=np.int64,
    )


def solve_prime_lift(kernel_basis: np.ndarray, target_matrix: np.ndarray) -> dict[str, Any]:
    rref, transform, pivots = prime_rref_with_transform(kernel_basis)
    transformed_target = (transform @ target_matrix) % PRIME
    lift = np.zeros((kernel_basis.shape[1], target_matrix.shape[1]), dtype=np.int64)
    for rref_row, pivot_column in enumerate(pivots):
        lift[pivot_column] = transformed_target[rref_row]
    reconstructed = (kernel_basis @ lift) % PRIME
    residual = (reconstructed - target_matrix) % PRIME
    return {
        "rref": rref,
        "transform": transform,
        "pivots": pivots,
        "lift": lift,
        "reconstructed": reconstructed,
        "residual": residual,
    }


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = [
        "prime_kernel",
        "row_operation_matrix",
        "pivot_columns",
        "signed_lift_mod",
        "signed_lift_signed",
        "binary_binding",
        "target_source_table",
        "reconstructed_source_table",
        "residual_table",
        "observable_vector",
    ]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def build_rows() -> dict[str, Any]:
    long_k23 = load_json(LONG_K23_REPORT)
    long_k23src = load_json(LONG_K23SRC_REPORT)
    long_k23bind = load_json(LONG_K23BIND_REPORT)
    support_rows_raw = [{key: int(value) for key, value in row.items()} for row in read_csv_rows(LONG_HCSUPP_SUPPORT)]
    with np.load(LONG_K23_MATRICES, allow_pickle=False) as matrices:
        kernel_basis = np.asarray(matrices["kernel_basis"], dtype=np.int64) % PRIME
    with np.load(LONG_K23SRC_MATRICES, allow_pickle=False) as matrices:
        target_source_images = np.asarray(matrices["extension_source_images"], dtype=np.int64)
    with np.load(LONG_K23BIND_MATRICES, allow_pickle=False) as matrices:
        binary_binding = np.asarray(matrices["binding_matrix"], dtype=np.int64)
    target_matrix = masks_to_table(target_source_images)
    solved = solve_prime_lift(kernel_basis, target_matrix)
    signed_lift = np.vectorize(signed_value)(solved["lift"]).astype(np.int64)
    signed_support = (solved["lift"] != 0).astype(np.int64)
    binary_support = (binary_binding != 0).astype(np.int64)
    reconstructed_masks = np.asarray([row_mask(row) for row in solved["reconstructed"]], dtype=np.int64)
    support_rows = []
    for support_row in support_rows_raw:
        row_id = int(support_row["row_id"])
        signed_values = [int(value) for value in signed_lift[row_id].tolist() if int(value) != 0]
        support_rows.append(
            {
                "support_row_id": row_id,
                "relation_id": int(support_row["relation_id"]),
                "block_i": int(support_row["block_i"]),
                "rep4": int(support_row["rep4"]),
                "pivot_flag": int(row_id in solved["pivots"]),
                "binary_binding_mask": row_mask(binary_support[row_id]),
                "signed_support_mask": row_mask(signed_support[row_id]),
                "support_match_flag": int(np.array_equal(signed_support[row_id], binary_support[row_id])),
                "signed_support_weight": len(signed_values),
                "signed_sum": sum(signed_values),
                "signed_l1": sum(abs(value) for value in signed_values),
                "min_signed": min(signed_values) if signed_values else 0,
                "max_signed": max(signed_values) if signed_values else 0,
                "negative_count": sum(1 for value in signed_values if value < 0),
                "positive_count": sum(1 for value in signed_values if value > 0),
            }
        )
    entry_rows = []
    entry_id = 0
    for support_row_id in range(solved["lift"].shape[0]):
        for source_coordinate in range(solved["lift"].shape[1]):
            coeff_mod = int(solved["lift"][support_row_id, source_coordinate])
            binary_entry = int(binary_binding[support_row_id, source_coordinate] != 0)
            if coeff_mod == 0 and binary_entry == 0:
                continue
            entry_rows.append(
                {
                    "entry_id": entry_id,
                    "support_row_id": support_row_id,
                    "source_coordinate": source_coordinate,
                    "coefficient_mod": coeff_mod,
                    "coefficient_signed": signed_value(coeff_mod),
                    "binary_binding_entry": binary_entry,
                    "support_match_flag": int((coeff_mod != 0) == bool(binary_entry)),
                    "residue_parity": int(coeff_mod % 2),
                }
            )
            entry_id += 1
    row_check_rows = []
    residual_nonzero_total = 0
    for row_id, target_mask in enumerate(target_source_images.tolist()):
        residual_row = solved["residual"][row_id]
        residual_nonzero = int(np.count_nonzero(residual_row))
        residual_nonzero_total += residual_nonzero
        row_check_rows.append(
            {
                "k23_basis_row_id": row_id,
                "target_source_mask": int(target_mask),
                "reconstructed_source_mask": int(reconstructed_masks[row_id]),
                "residual_nonzero_count": residual_nonzero,
                "residual_mod_sum": int(residual_row.sum() % PRIME),
            }
        )
    coeff_counter = Counter(int(row["coefficient_signed"]) for row in entry_rows if int(row["coefficient_signed"]) != 0)
    coeff_rows = [
        {"coefficient_signed": coeff, "entry_count": int(coeff_counter[coeff])}
        for coeff in sorted(coeff_counter)
    ]
    parity_matrix = np.asarray(solved["lift"] % 2, dtype=np.int64)
    obs = {
        "long_k23_certified_flag": int(
            long_k23.get("status") == "SECTOR33_K23_PUNCTURED_MOG_SYZYGY_APERTURE_TARGET_CERTIFIED"
            and long_k23.get("all_checks_pass") is True
        ),
        "long_k23src_certified_flag": int(
            long_k23src.get("status") == "SECTOR33_K23_SOURCE_W24_RANK12_EXTENSION_CERTIFIED"
            and long_k23src.get("all_checks_pass") is True
        ),
        "long_k23bind_certified_flag": int(
            long_k23bind.get("status") == "SECTOR33_K23_BINARY_SUPPORT_BINDING_CERTIFIED"
            and long_k23bind.get("all_checks_pass") is True
        ),
        "prime_field": PRIME,
        "support_row_count": kernel_basis.shape[1],
        "k23_basis_row_count": kernel_basis.shape[0],
        "source_coordinate_count": target_matrix.shape[1],
        "prime_rank": len(solved["pivots"]),
        "pivot_column_count": len(solved["pivots"]),
        "signed_lift_row_count": solved["lift"].shape[0],
        "signed_lift_column_count": solved["lift"].shape[1],
        "active_signed_support_row_count": int((signed_support.sum(axis=1) > 0).sum()),
        "inactive_signed_support_row_count": int((signed_support.sum(axis=1) == 0).sum()),
        "signed_lift_nonzero_entry_count": int(signed_support.sum()),
        "binary_binding_nonzero_entry_count": int(binary_support.sum()),
        "support_overlap_entry_count": int((signed_support & binary_support).sum()),
        "signed_only_entry_count": int((signed_support & (1 - binary_support)).sum()),
        "binary_only_entry_count": int(((1 - signed_support) & binary_support).sum()),
        "support_profile_match_flag": int(np.array_equal(signed_support, binary_support)),
        "prime_residual_nonzero_entry_count": residual_nonzero_total,
        "zero_residual_row_count": sum(int(row["residual_nonzero_count"] == 0) for row in row_check_rows),
        "reconstructed_image_rank": gf2_rank(np.asarray(solved["reconstructed"] != 0, dtype=np.uint8)),
        "coefficient_distinct_count": len(coeff_counter),
        "coefficient_min_signed": min(coeff_counter) if coeff_counter else 0,
        "coefficient_max_signed": max(coeff_counter) if coeff_counter else 0,
        "negative_coefficient_count": sum(count for coeff, count in coeff_counter.items() if coeff < 0),
        "positive_coefficient_count": sum(count for coeff, count in coeff_counter.items() if coeff > 0),
        "signed_l1_total": sum(abs(int(row["coefficient_signed"])) for row in entry_rows),
        "residue_parity_mismatch_count": int((parity_matrix != binary_support).sum()),
        "signed_prime_lift_certified_flag": int(residual_nonzero_total == 0),
        "parity_is_algebraic_reduction_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    matrix_payload = {
        "prime_kernel": kernel_basis.astype(np.int64),
        "row_operation_matrix": solved["transform"].astype(np.int64),
        "pivot_columns": np.asarray(solved["pivots"], dtype=np.int64),
        "signed_lift_mod": solved["lift"].astype(np.int64),
        "signed_lift_signed": signed_lift.astype(np.int64),
        "binary_binding": binary_binding.astype(np.int64),
        "target_source_table": target_matrix.astype(np.int64),
        "reconstructed_source_table": solved["reconstructed"].astype(np.int64),
        "residual_table": solved["residual"].astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "long_k23": long_k23,
        "long_k23src": long_k23src,
        "long_k23bind": long_k23bind,
        "support_rows": support_rows,
        "entry_rows": entry_rows,
        "row_check_rows": row_check_rows,
        "coeff_rows": coeff_rows,
        "obs_rows": obs_rows,
        "support_table": table_from_rows(SUPPORT_COLUMNS, support_rows),
        "entry_table": table_from_rows(ENTRY_COLUMNS, entry_rows),
        "row_check_table": table_from_rows(ROW_CHECK_COLUMNS, row_check_rows),
        "coeff_table": table_from_rows(COEFF_COLUMNS, coeff_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "pivot_columns": solved["pivots"],
        "support_text_hash": hashlib.sha256(digest_text(SUPPORT_COLUMNS, support_rows).encode("ascii")).hexdigest(),
        "entry_text_hash": hashlib.sha256(digest_text(ENTRY_COLUMNS, entry_rows).encode("ascii")).hexdigest(),
        "row_check_text_hash": hashlib.sha256(digest_text(ROW_CHECK_COLUMNS, row_check_rows).encode("ascii")).hexdigest(),
        "coeff_text_hash": hashlib.sha256(digest_text(COEFF_COLUMNS, coeff_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": (
            obs["long_k23_certified_flag"],
            obs["long_k23src_certified_flag"],
            obs["long_k23bind_certified_flag"],
        )
        == (1, 1, 1),
        "prime_lift_shape_matches": (
            obs["prime_field"],
            obs["support_row_count"],
            obs["k23_basis_row_count"],
            obs["source_coordinate_count"],
            obs["prime_rank"],
            obs["pivot_column_count"],
        )
        == (PRIME, 56, 23, 24, 23, 23),
        "signed_support_matches_binary_support": (
            obs["active_signed_support_row_count"],
            obs["inactive_signed_support_row_count"],
            obs["signed_lift_nonzero_entry_count"],
            obs["binary_binding_nonzero_entry_count"],
            obs["support_overlap_entry_count"],
            obs["signed_only_entry_count"],
            obs["binary_only_entry_count"],
            obs["support_profile_match_flag"],
        )
        == (13, 43, 112, 112, 112, 0, 0, 1),
        "prime_reconstruction_is_exact": (
            obs["prime_residual_nonzero_entry_count"],
            obs["zero_residual_row_count"],
            obs["reconstructed_image_rank"],
            obs["signed_prime_lift_certified_flag"],
        )
        == (0, 23, 12, 1),
        "coefficient_profile_matches": (
            obs["coefficient_distinct_count"],
            obs["coefficient_min_signed"],
            obs["coefficient_max_signed"],
            obs["negative_coefficient_count"],
            obs["positive_coefficient_count"],
            obs["signed_l1_total"],
        )
        == (3, -2, 1, 62, 50, 120),
        "parity_boundary_recorded": (
            obs["residue_parity_mismatch_count"],
            obs["parity_is_algebraic_reduction_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (54, 0, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_signed_prime_support_lift",
        "summary": obs,
        "pivot_columns": rows["pivot_columns"],
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies an exact signed prime-field lift whose nonzero support matches the binary binding; residue parity is recorded only as a diagnostic, not as an algebraic reduction.",
    }
    seam_payload = {
        "schema": "long.k23lift.seam@1",
        "status": STATUS,
        "claim": "The binary support binding lifts to an exact prime-field 56-to-24 signed support map with the same nonzero support and zero reconstruction residual.",
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
        "long_k23bind": input_entry(
            LONG_K23BIND_REPORT,
            {
                "status": rows["long_k23bind"].get("status"),
                "certificate_sha256": rows["long_k23bind"].get("certificate_sha256"),
            },
        ),
        "long_k23bind_matrices": input_entry(LONG_K23BIND_MATRICES),
        "long_hcsupp_support": input_entry(LONG_HCSUPP_SUPPORT),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23lift.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23lift certifies an exact signed prime-field support lift of the K23 source assignment, with nonzero support matching the binary support binding.",
        "stage_protocol": {
            "draft": "read long_k23, long_k23src, long_k23bind, prime K23 coefficients, and support rows",
            "witness": "emit signed support rows, nonzero coefficient rows, row reconstruction checks, coefficient histogram, observables, and matrices",
            "coherence": "check prime rank, exact residual zero, support equality against binary binding, and coefficient profile",
            "closure": "certify signed prime-field lift while keeping parity reduction and module action out of scope",
            "emit": "write long_k23lift artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "support_signed_rows_csv": relpath(OUT_DIR / "support_signed_rows.csv"),
            "coefficient_rows_csv": relpath(OUT_DIR / "coefficient_rows.csv"),
            "row_check_rows_csv": relpath(OUT_DIR / "row_check_rows.csv"),
            "coefficient_histogram_csv": relpath(OUT_DIR / "coefficient_histogram.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23lift_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the actual prime-field K23 coefficient matrix has rank 23 for this solve",
                "an explicit 56-by-24 prime-field lift reconstructs all 23 source-assignment rows with zero residual",
                "the signed coefficients are supported on exactly the same 112 entries as the binary binding",
                "the nonzero signed coefficients are only -2, -1, and 1",
            ],
            "does_not_certify": [
                "that residue parity is an algebraic reduction from the prime field to binary support",
                "uniqueness or canonicity of the signed lift",
                "a one-hot partition of support coordinates",
                "an M23 module action on K23",
                "a rebuild of d20.json or broad bundle closure",
            ],
        },
        "next_highest_yield_item": "Use the signed support lift to test compatibility with the canonical 24 syzygy frame, then either certify K23-to-syzygy rowspace equality or emit the exact remaining obstruction.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23lift.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23lift.manifest@1",
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
        "entry_csv": csv_text(ENTRY_COLUMNS, rows["entry_rows"]),
        "row_check_csv": csv_text(ROW_CHECK_COLUMNS, rows["row_check_rows"]),
        "coeff_csv": csv_text(COEFF_COLUMNS, rows["coeff_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "support_table": rows["support_table"],
        "entry_table": rows["entry_table"],
        "row_check_table": rows["row_check_table"],
        "coeff_table": rows["coeff_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "support_text_sha256": rows["support_text_hash"],
            "entry_text_sha256": rows["entry_text_hash"],
            "row_check_text_sha256": rows["row_check_text_hash"],
            "coeff_text_sha256": rows["coeff_text_hash"],
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
    (OUT_DIR / "support_signed_rows.csv").write_text(payloads["support_csv"], encoding="utf-8")
    (OUT_DIR / "coefficient_rows.csv").write_text(payloads["entry_csv"], encoding="utf-8")
    (OUT_DIR / "row_check_rows.csv").write_text(payloads["row_check_csv"], encoding="utf-8")
    (OUT_DIR / "coefficient_histogram.csv").write_text(payloads["coeff_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        support_table=payloads["support_table"],
        entry_table=payloads["entry_table"],
        row_check_table=payloads["row_check_table"],
        coeff_table=payloads["coeff_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23lift_matrices.npz", **payloads["matrix_payload"])
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
