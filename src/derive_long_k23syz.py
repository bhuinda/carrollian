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


THEOREM_ID = "long_k23syz"
STATUS = "SECTOR33_K23_CANONICAL_SYZYGY_FRAME_BINDING_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PRIME = 1_000_003

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23syz.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23syz.py"
LONG_K23_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23" / "report.json"
LONG_K23_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23" / "k23_matrices.npz"
LONG_K23LIFT_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23lift" / "report.json"
CANONICAL_FRAME = ROOT / "data" / "geometry" / "canonical_24_syzygy_frame.json"
LONG_HCSUPP_SUPPORT = D20_INVARIANTS / "proof_obligations" / "long_hcsupp" / "support_rows.csv"

SUPPORT_TEXT_HASH = "8f4d2aeb895073992a81a9530b9275fa9620a21c24e505e880c463862d29df05"
ENTRY_TEXT_HASH = "c8fabad4be8a4a811a9e076e115f125bc9e8b5702e99c14211bb94e4f0374e70"
ROW_CHECK_TEXT_HASH = "6853abd67eadefe6b836717419835f05d853e23ad1a79f380a4617130a6605e7"
COEFF_TEXT_HASH = "8795476e542f3a76f0332c7ce9da410cd4b91fe76b5cd2d72b18903813b769da"
OBS_TEXT_HASH = "78f3f1759c3299504585788ec71ae4b9a86a5cca08ba8a4d2a3602d4cfec75ae"
MATRIX_SHA256 = "9fee1c993b44fbcf45fa1147e6bd15c3143b8c8d52874699ea3254e34ff2db19"

SUPPORT_COLUMNS = [
    "support_row_id",
    "relation_id",
    "block_i",
    "rep4",
    "pivot_flag",
    "frame_support_mask",
    "frame_support_weight",
    "euler_nonzero_flag",
    "syzygy_nonzero_count",
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
    "frame_coordinate",
    "coordinate_role_code",
    "syzygy_index",
    "coefficient_mod",
    "coefficient_signed",
]
ROW_CHECK_COLUMNS = [
    "k23_basis_row_id",
    "target_frame_mask",
    "reconstructed_frame_mask",
    "target_euler_value",
    "reconstructed_euler_value",
    "residual_nonzero_count",
    "residual_mod_sum",
]
COEFF_COLUMNS = ["coefficient_signed", "entry_count"]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_k23_certified_flag",
    "long_k23lift_certified_flag",
    "canonical_frame_certified_flag",
    "prime_field",
    "support_row_count",
    "k23_basis_row_count",
    "canonical_coordinate_count",
    "euler_coordinate_count",
    "syzygy_coordinate_count",
    "target_euler_nonzero_count",
    "target_syzygy_rank",
    "prime_rank",
    "pivot_column_count",
    "frame_lift_row_count",
    "frame_lift_column_count",
    "active_frame_support_row_count",
    "inactive_frame_support_row_count",
    "frame_lift_nonzero_entry_count",
    "euler_lift_nonzero_entry_count",
    "syzygy_lift_nonzero_entry_count",
    "zero_residual_row_count",
    "prime_residual_nonzero_entry_count",
    "reconstructed_syzygy_rank",
    "rowspace_identity_certified_flag",
    "coefficient_distinct_count",
    "coefficient_min_signed",
    "coefficient_max_signed",
    "negative_coefficient_count",
    "positive_coefficient_count",
    "half_residue_entry_count",
    "signed_l1_total",
    "golay_selector_certified_flag",
    "m23_module_proven_flag",
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


def gf_rank_mod(matrix: np.ndarray, prime: int = PRIME) -> int:
    work = np.asarray(matrix, dtype=np.int64).copy() % prime
    row_count, column_count = work.shape
    rank = 0
    for column in range(column_count):
        source_row = -1
        for row in range(rank, row_count):
            if int(work[row, column]) % prime != 0:
                source_row = row
                break
        if source_row < 0:
            continue
        if source_row != rank:
            work[[rank, source_row]] = work[[source_row, rank]]
        factor = pow(int(work[rank, column]) % prime, prime - 2, prime)
        work[rank] = (work[rank] * factor) % prime
        for row in range(row_count):
            if row != rank and int(work[row, column]) % prime != 0:
                factor = int(work[row, column]) % prime
                work[row] = (work[row] - factor * work[rank]) % prime
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


def build_target_frame(row_count: int) -> np.ndarray:
    target = np.zeros((row_count, 24), dtype=np.int64)
    for row in range(row_count):
        target[row, row + 1] = 1
    return target


def solve_frame_lift(kernel_basis: np.ndarray, target_frame: np.ndarray) -> dict[str, Any]:
    rref, transform, pivots = prime_rref_with_transform(kernel_basis)
    transformed_target = (transform @ target_frame) % PRIME
    lift = np.zeros((kernel_basis.shape[1], target_frame.shape[1]), dtype=np.int64)
    for rref_row, pivot_column in enumerate(pivots):
        lift[pivot_column] = transformed_target[rref_row]
    reconstructed = (kernel_basis @ lift) % PRIME
    residual = (reconstructed - target_frame) % PRIME
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
        "frame_lift_mod",
        "frame_lift_signed",
        "target_frame_table",
        "reconstructed_frame_table",
        "residual_table",
        "observable_vector",
    ]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def build_rows() -> dict[str, Any]:
    long_k23 = load_json(LONG_K23_REPORT)
    long_k23lift = load_json(LONG_K23LIFT_REPORT)
    canonical_frame = load_json(CANONICAL_FRAME)
    support_rows_raw = [{key: int(value) for key, value in row.items()} for row in read_csv_rows(LONG_HCSUPP_SUPPORT)]
    with np.load(LONG_K23_MATRICES, allow_pickle=False) as matrices:
        kernel_basis = np.asarray(matrices["kernel_basis"], dtype=np.int64) % PRIME
    target_frame = build_target_frame(kernel_basis.shape[0])
    solved = solve_frame_lift(kernel_basis, target_frame)
    signed_lift = np.vectorize(signed_value)(solved["lift"]).astype(np.int64)
    support_rows = []
    pivot_set = set(solved["pivots"])
    for support_row in support_rows_raw:
        row_id = int(support_row["row_id"])
        signed_values = [int(value) for value in signed_lift[row_id].tolist() if int(value) != 0]
        frame_mask = row_mask(solved["lift"][row_id])
        support_rows.append(
            {
                "support_row_id": row_id,
                "relation_id": int(support_row["relation_id"]),
                "block_i": int(support_row["block_i"]),
                "rep4": int(support_row["rep4"]),
                "pivot_flag": int(row_id in pivot_set),
                "frame_support_mask": frame_mask,
                "frame_support_weight": int(frame_mask).bit_count(),
                "euler_nonzero_flag": int(solved["lift"][row_id, 0] != 0),
                "syzygy_nonzero_count": int(np.count_nonzero(solved["lift"][row_id, 1:])),
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
        for frame_coordinate in range(solved["lift"].shape[1]):
            coeff_mod = int(solved["lift"][support_row_id, frame_coordinate])
            if coeff_mod == 0:
                continue
            entry_rows.append(
                {
                    "entry_id": entry_id,
                    "support_row_id": support_row_id,
                    "frame_coordinate": frame_coordinate,
                    "coordinate_role_code": 0 if frame_coordinate == 0 else 1,
                    "syzygy_index": frame_coordinate - 1 if frame_coordinate > 0 else -1,
                    "coefficient_mod": coeff_mod,
                    "coefficient_signed": signed_value(coeff_mod),
                }
            )
            entry_id += 1
    row_check_rows = []
    residual_nonzero_total = 0
    for row_id in range(target_frame.shape[0]):
        residual_row = solved["residual"][row_id]
        residual_nonzero = int(np.count_nonzero(residual_row))
        residual_nonzero_total += residual_nonzero
        row_check_rows.append(
            {
                "k23_basis_row_id": row_id,
                "target_frame_mask": row_mask(target_frame[row_id]),
                "reconstructed_frame_mask": row_mask(solved["reconstructed"][row_id]),
                "target_euler_value": int(target_frame[row_id, 0]),
                "reconstructed_euler_value": int(solved["reconstructed"][row_id, 0]),
                "residual_nonzero_count": residual_nonzero,
                "residual_mod_sum": int(residual_row.sum() % PRIME),
            }
        )
    coeff_counter = Counter(int(row["coefficient_signed"]) for row in entry_rows)
    coeff_rows = [
        {"coefficient_signed": coeff, "entry_count": int(coeff_counter[coeff])}
        for coeff in sorted(coeff_counter)
    ]
    frame_meta = canonical_frame.get("canonical_frame", {})
    audit = canonical_frame.get("Golay_binary_audit", {})
    obs = {
        "long_k23_certified_flag": int(
            long_k23.get("status") == "SECTOR33_K23_PUNCTURED_MOG_SYZYGY_APERTURE_TARGET_CERTIFIED"
            and long_k23.get("all_checks_pass") is True
        ),
        "long_k23lift_certified_flag": int(
            long_k23lift.get("status") == "SECTOR33_K23_SIGNED_PRIME_SUPPORT_LIFT_CERTIFIED"
            and long_k23lift.get("all_checks_pass") is True
        ),
        "canonical_frame_certified_flag": int(
            canonical_frame.get("status") == "CANONICAL_24_COORDINATE_SYZYGY_FRAME_CERTIFIED_GOLAY_SELECTION_STILL_OPEN"
            and int(frame_meta.get("coordinate_count", 0)) == 24
            and int(frame_meta.get("syzygy_dimension", 0)) == 23
        ),
        "prime_field": PRIME,
        "support_row_count": kernel_basis.shape[1],
        "k23_basis_row_count": kernel_basis.shape[0],
        "canonical_coordinate_count": int(frame_meta.get("coordinate_count", 0)),
        "euler_coordinate_count": 1,
        "syzygy_coordinate_count": int(frame_meta.get("syzygy_dimension", 0)),
        "target_euler_nonzero_count": int(np.count_nonzero(target_frame[:, 0])),
        "target_syzygy_rank": gf_rank_mod(target_frame[:, 1:]),
        "prime_rank": len(solved["pivots"]),
        "pivot_column_count": len(solved["pivots"]),
        "frame_lift_row_count": solved["lift"].shape[0],
        "frame_lift_column_count": solved["lift"].shape[1],
        "active_frame_support_row_count": sum(int(row["frame_support_weight"] > 0) for row in support_rows),
        "inactive_frame_support_row_count": sum(int(row["frame_support_weight"] == 0) for row in support_rows),
        "frame_lift_nonzero_entry_count": len(entry_rows),
        "euler_lift_nonzero_entry_count": sum(int(row["frame_coordinate"] == 0) for row in entry_rows),
        "syzygy_lift_nonzero_entry_count": sum(int(row["frame_coordinate"] > 0) for row in entry_rows),
        "zero_residual_row_count": sum(int(row["residual_nonzero_count"] == 0) for row in row_check_rows),
        "prime_residual_nonzero_entry_count": residual_nonzero_total,
        "reconstructed_syzygy_rank": gf_rank_mod(solved["reconstructed"][:, 1:]),
        "rowspace_identity_certified_flag": int(np.array_equal(solved["reconstructed"], target_frame)),
        "coefficient_distinct_count": len(coeff_counter),
        "coefficient_min_signed": min(coeff_counter) if coeff_counter else 0,
        "coefficient_max_signed": max(coeff_counter) if coeff_counter else 0,
        "negative_coefficient_count": sum(count for coeff, count in coeff_counter.items() if coeff < 0),
        "positive_coefficient_count": sum(count for coeff, count in coeff_counter.items() if coeff > 0),
        "half_residue_entry_count": int(coeff_counter.get(-500001, 0)),
        "signed_l1_total": sum(abs(int(row["coefficient_signed"])) for row in entry_rows),
        "golay_selector_certified_flag": int(bool(audit.get("passes_extended_golay_weight_test", False))),
        "m23_module_proven_flag": 0,
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
        "frame_lift_mod": solved["lift"].astype(np.int64),
        "frame_lift_signed": signed_lift.astype(np.int64),
        "target_frame_table": target_frame.astype(np.int64),
        "reconstructed_frame_table": solved["reconstructed"].astype(np.int64),
        "residual_table": solved["residual"].astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "long_k23": long_k23,
        "long_k23lift": long_k23lift,
        "canonical_frame": canonical_frame,
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
            obs["long_k23lift_certified_flag"],
            obs["canonical_frame_certified_flag"],
        )
        == (1, 1, 1),
        "canonical_target_shape_matches": (
            obs["prime_field"],
            obs["support_row_count"],
            obs["k23_basis_row_count"],
            obs["canonical_coordinate_count"],
            obs["euler_coordinate_count"],
            obs["syzygy_coordinate_count"],
            obs["target_euler_nonzero_count"],
            obs["target_syzygy_rank"],
        )
        == (PRIME, 56, 23, 24, 1, 23, 0, 23),
        "frame_lift_shape_matches": (
            obs["prime_rank"],
            obs["pivot_column_count"],
            obs["frame_lift_row_count"],
            obs["frame_lift_column_count"],
            obs["active_frame_support_row_count"],
            obs["inactive_frame_support_row_count"],
            obs["frame_lift_nonzero_entry_count"],
        )
        == (23, 23, 56, 24, 23, 33, 43),
        "euler_is_killed_and_syzygy_identity_reconstructs": (
            obs["euler_lift_nonzero_entry_count"],
            obs["syzygy_lift_nonzero_entry_count"],
            obs["zero_residual_row_count"],
            obs["prime_residual_nonzero_entry_count"],
            obs["reconstructed_syzygy_rank"],
            obs["rowspace_identity_certified_flag"],
        )
        == (0, 43, 23, 0, 23, 1),
        "coefficient_profile_matches": (
            obs["coefficient_distinct_count"],
            obs["coefficient_min_signed"],
            obs["coefficient_max_signed"],
            obs["negative_coefficient_count"],
            obs["positive_coefficient_count"],
            obs["half_residue_entry_count"],
            obs["signed_l1_total"],
        )
        == (5, -500001, 2, 29, 14, 2, 1000050),
        "golay_selector_and_module_remain_open": (
            obs["golay_selector_certified_flag"],
            obs["m23_module_proven_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (0, 0, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_canonical_syzygy_frame_binding",
        "summary": obs,
        "pivot_columns": rows["pivot_columns"],
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies an exact prime-field binding of K23 to the canonical Euler-plus-syzygy coordinate frame; the binary selector and M23 action remain open.",
    }
    seam_payload = {
        "schema": "long.k23syz.seam@1",
        "status": STATUS,
        "claim": "The K23 basis binds exactly to the canonical 24-coordinate frame by killing Euler and mapping the 23 basis rows to the 23 syzygy coordinates.",
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
        "long_k23lift": input_entry(
            LONG_K23LIFT_REPORT,
            {
                "status": rows["long_k23lift"].get("status"),
                "certificate_sha256": rows["long_k23lift"].get("certificate_sha256"),
            },
        ),
        "canonical_24_syzygy_frame": input_entry(
            CANONICAL_FRAME,
            {
                "status": rows["canonical_frame"].get("status"),
                "canonical_24_syzygy_frame_sha256": rows["canonical_frame"].get(
                    "canonical_24_syzygy_frame_sha256"
                ),
            },
        ),
        "long_hcsupp_support": input_entry(LONG_HCSUPP_SUPPORT),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23syz.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23syz certifies the explicit K23 binding to the canonical Euler-plus-23-syzygy coordinate frame.",
        "stage_protocol": {
            "draft": "read long_k23, long_k23lift, the canonical 24 syzygy frame, and sector33 support rows",
            "witness": "emit support-frame rows, nonzero coefficient rows, row reconstruction checks, coefficient histogram, observables, and matrices",
            "coherence": "check Euler-zero target, syzygy identity rank, exact prime residual zero, and coefficient profile",
            "closure": "certify canonical syzygy-frame binding while keeping the binary selector and module action open",
            "emit": "write long_k23syz artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "support_frame_rows_csv": relpath(OUT_DIR / "support_frame_rows.csv"),
            "coefficient_rows_csv": relpath(OUT_DIR / "coefficient_rows.csv"),
            "row_check_rows_csv": relpath(OUT_DIR / "row_check_rows.csv"),
            "coefficient_histogram_csv": relpath(OUT_DIR / "coefficient_histogram.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23syz_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the canonical frame has one Euler coordinate and 23 syzygy coordinates",
                "an explicit 56-by-24 prime-field support map kills Euler",
                "the same map reconstructs the 23-by-23 syzygy identity with zero residual",
                "K23 is therefore bound to the canonical punctured syzygy coordinate frame over the certified prime field",
            ],
            "does_not_certify": [
                "the quadratic/isotropic binary selector inside the canonical frame",
                "that the canonical frame's naive binary shadow is the Golay code",
                "an M23 module action on K23",
                "uniqueness or canonicity of the support map",
                "a rebuild of d20.json or broad bundle closure",
            ],
        },
        "next_highest_yield_item": "Use the canonical syzygy-frame binding to search for the quadratic/isotropic binary selector inside W24, then test whether the induced stabilizer action is M23-type.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23syz.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23syz.manifest@1",
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
    (OUT_DIR / "support_frame_rows.csv").write_text(payloads["support_csv"], encoding="utf-8")
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
    np.savez_compressed(OUT_DIR / "k23syz_matrices.npz", **payloads["matrix_payload"])
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
