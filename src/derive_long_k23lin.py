from __future__ import annotations

import hashlib
import json
from collections import Counter
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


THEOREM_ID = "long_k23lin"
STATUS = "SECTOR33_K23_M23_PRIME_LINEAR_INTERTWINER_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PRIME = 1_000_003

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23lin.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23lin.py"
LONG_K23SYZ_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23syz" / "report.json"
LONG_K23SYZ_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23syz" / "k23syz_matrices.npz"
LONG_K23STAB_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23stab" / "report.json"
LONG_K23STAB_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23stab" / "k23stab_matrices.npz"
LONG_K23ACT_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23act" / "report.json"

COMPLEMENT_TEXT_HASH = "25fb226e9f0dc4c41d93dc843d79f6fc5c7519f27922fc9d1316093d3a083b51"
GENERATOR_TEXT_HASH = "628a508980c2cdbe1243784f47a96ff7be2eabaae487f589726c91a2b9b84ae3"
COEFF_TEXT_HASH = "82e86408e5cac56a296bb22a6a4b703704ff34c6525cdb593e36206cdf64ed26"
OBS_TEXT_HASH = "63d25e7ce944ae46b9ad81e6a082fe7aade6e20df148026333673b905eb95f02"
MATRIX_SHA256 = "6bb82b010280202330940f327dad12a3056b962e9ecee9e9cb26fb955843359b"

COMPLEMENT_COLUMNS = [
    "complement_vector_id",
    "free_support_column",
    "support_mask",
    "support_weight",
    "signed_l1",
    "kernel_residual_nonzero_count",
]
GENERATOR_COLUMNS = [
    "generator_id",
    "action_order",
    "support_operator_rank",
    "support_operator_nullity",
    "support_operator_nonzero_count",
    "support_inverse_nonzero_count",
    "k23_residual_nonzero_count",
    "frame_residual_nonzero_count",
    "inverse_residual_nonzero_count",
    "support_operator_order",
    "coefficient_distinct_count",
    "coefficient_min_signed",
    "coefficient_max_signed",
    "negative_coefficient_count",
    "positive_coefficient_count",
    "signed_l1_total",
]
COEFF_COLUMNS = ["generator_id", "coefficient_signed", "entry_count"]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_k23syz_certified_flag",
    "long_k23stab_certified_flag",
    "long_k23act_certified_flag",
    "prime_field",
    "support_row_count",
    "frame_coordinate_count",
    "k23_basis_row_count",
    "frame_lift_syzygy_rank",
    "kernel_complement_dimension",
    "kernel_complement_rank",
    "kernel_complement_residual_nonzero_count",
    "basis_change_rank",
    "basis_change_inverse_residual_nonzero_count",
    "generator_count",
    "linear_lift_generator_count",
    "invertible_support_operator_count",
    "k23_intertwiner_residual_nonzero_count",
    "frame_intertwiner_residual_nonzero_count",
    "inverse_residual_nonzero_count",
    "support_operator_rank_sum",
    "support_operator_nullity_sum",
    "row_action_obstruction_preserved_flag",
    "prime_linear_lift_certified_flag",
    "m23_k23_module_action_certified_flag",
    "unique_lift_proven_flag",
    "row_permutation_lift_proven_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def mod_inv(value: int) -> int:
    return pow(int(value) % PRIME, PRIME - 2, PRIME)


def signed_value(value: int) -> int:
    value = int(value) % PRIME
    if value > PRIME // 2:
        return value - PRIME
    return value


def row_support_mask(row: np.ndarray) -> int:
    mask = 0
    for index, value in enumerate(np.asarray(row).tolist()):
        if int(value) % PRIME != 0:
            mask |= 1 << index
    return mask


def gf_rank_mod(matrix: np.ndarray) -> int:
    _, pivots = rref_mod(np.asarray(matrix, dtype=np.int64))
    return len(pivots)


def rref_mod(matrix: np.ndarray) -> tuple[np.ndarray, list[int]]:
    work = np.asarray(matrix, dtype=np.int64).copy() % PRIME
    row_count, column_count = work.shape
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
        factor = mod_inv(int(work[pivot_row, column]))
        work[pivot_row] = (work[pivot_row] * factor) % PRIME
        for row in range(row_count):
            if row != pivot_row and int(work[row, column]) % PRIME != 0:
                factor = int(work[row, column]) % PRIME
                work[row] = (work[row] - factor * work[pivot_row]) % PRIME
        pivots.append(column)
        pivot_row += 1
        if pivot_row == row_count:
            break
    return work, pivots


def nullspace_basis(matrix: np.ndarray) -> tuple[np.ndarray, list[int], list[int]]:
    rref, pivots = rref_mod(matrix)
    column_count = rref.shape[1]
    free_columns = [column for column in range(column_count) if column not in set(pivots)]
    basis_columns = []
    for free_column in free_columns:
        vector = np.zeros(column_count, dtype=np.int64)
        vector[free_column] = 1
        for row, pivot_column in enumerate(pivots):
            vector[pivot_column] = (-int(rref[row, free_column])) % PRIME
        basis_columns.append(vector)
    return np.stack(basis_columns, axis=1).astype(np.int64), pivots, free_columns


def invert_matrix(matrix: np.ndarray) -> np.ndarray:
    work = np.asarray(matrix, dtype=np.int64).copy() % PRIME
    size = work.shape[0]
    aug = np.concatenate([work, np.eye(size, dtype=np.int64)], axis=1) % PRIME
    pivot_row = 0
    for column in range(size):
        source_row = -1
        for row in range(pivot_row, size):
            if int(aug[row, column]) % PRIME != 0:
                source_row = row
                break
        if source_row < 0:
            raise AssertionError("matrix is singular")
        if source_row != pivot_row:
            aug[[pivot_row, source_row]] = aug[[source_row, pivot_row]]
        factor = mod_inv(int(aug[pivot_row, column]))
        aug[pivot_row] = (aug[pivot_row] * factor) % PRIME
        for row in range(size):
            if row != pivot_row and int(aug[row, column]) % PRIME != 0:
                factor = int(aug[row, column]) % PRIME
                aug[row] = (aug[row] - factor * aug[pivot_row]) % PRIME
        pivot_row += 1
    return aug[:, size:].astype(np.int64)


def perm_order(perm: list[int]) -> int:
    seen = [False] * len(perm)
    order = 1
    for start in range(len(perm)):
        if seen[start]:
            continue
        length = 0
        point = start
        while not seen[point]:
            seen[point] = True
            point = int(perm[point])
            length += 1
        if length:
            order = int(np.lcm(order, length))
    return order


def matrix_order(matrix: np.ndarray, limit: int = 500) -> int:
    size = matrix.shape[0]
    running = np.eye(size, dtype=np.int64)
    target = np.eye(size, dtype=np.int64)
    for order in range(1, limit + 1):
        running = (running @ matrix) % PRIME
        if np.array_equal(running, target):
            return order
    return -1


def permutation_matrices(perm: list[int]) -> tuple[np.ndarray, np.ndarray]:
    action = np.zeros((23, 23), dtype=np.int64)
    frame = np.zeros((24, 24), dtype=np.int64)
    frame[0, 0] = 1
    for index, image in enumerate(perm):
        action[index, int(image)] = 1
        frame[index + 1, int(image) + 1] = 1
    return action, frame


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = [
        "prime_kernel",
        "frame_lift_mod",
        "kernel_complement",
        "basis_change",
        "basis_change_inverse",
        "generator_permutations",
        "k23_action_matrices",
        "frame_permutation_matrices",
        "support_intertwiners",
        "support_intertwiner_inverses",
        "observable_vector",
    ]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def build_rows() -> dict[str, Any]:
    long_k23syz = load_json(LONG_K23SYZ_REPORT)
    long_k23stab = load_json(LONG_K23STAB_REPORT)
    long_k23act = load_json(LONG_K23ACT_REPORT)
    with np.load(LONG_K23SYZ_MATRICES, allow_pickle=False) as matrices:
        kernel = np.asarray(matrices["prime_kernel"], dtype=np.int64) % PRIME
        frame_lift = np.asarray(matrices["frame_lift_mod"], dtype=np.int64) % PRIME
    with np.load(LONG_K23STAB_MATRICES, allow_pickle=False) as matrices:
        generator_permutations = np.asarray(matrices["generator_permutations"], dtype=np.int64)
    syzygy_lift = frame_lift[:, 1:]
    complement, pivots, free_columns = nullspace_basis(kernel)
    basis_change = np.concatenate([syzygy_lift, complement], axis=1) % PRIME
    basis_change_inverse = invert_matrix(basis_change)
    complement_rows = []
    complement_residual = (kernel @ complement) % PRIME
    for index in range(complement.shape[1]):
        vector = complement[:, index]
        signed_values = [signed_value(int(value)) for value in vector.tolist() if int(value) % PRIME != 0]
        complement_rows.append(
            {
                "complement_vector_id": index,
                "free_support_column": int(free_columns[index]),
                "support_mask": row_support_mask(vector),
                "support_weight": int(np.count_nonzero(vector)),
                "signed_l1": sum(abs(value) for value in signed_values),
                "kernel_residual_nonzero_count": int(np.count_nonzero(complement_residual[:, index])),
            }
        )
    generator_rows = []
    coeff_rows = []
    action_matrices = []
    frame_perm_matrices = []
    support_intertwiners = []
    support_intertwiner_inverses = []
    total_k23_residual = 0
    total_frame_residual = 0
    total_inverse_residual = 0
    for generator_id, perm_array in enumerate(generator_permutations.tolist()):
        perm = [int(value) for value in perm_array]
        action, frame_perm = permutation_matrices(perm)
        diagonal = np.zeros((56, 56), dtype=np.int64)
        diagonal[:23, :23] = action
        diagonal[23:, 23:] = np.eye(33, dtype=np.int64)
        support_operator = (basis_change @ diagonal @ basis_change_inverse) % PRIME
        support_inverse = invert_matrix(support_operator)
        action_matrices.append(action)
        frame_perm_matrices.append(frame_perm)
        support_intertwiners.append(support_operator)
        support_intertwiner_inverses.append(support_inverse)
        k23_residual = (kernel @ support_operator - action @ kernel) % PRIME
        frame_residual = (support_operator @ frame_lift - frame_lift @ frame_perm) % PRIME
        inverse_residual = (support_operator @ support_inverse - np.eye(56, dtype=np.int64)) % PRIME
        total_k23_residual += int(np.count_nonzero(k23_residual))
        total_frame_residual += int(np.count_nonzero(frame_residual))
        total_inverse_residual += int(np.count_nonzero(inverse_residual))
        signed_entries = [
            signed_value(int(value))
            for value in support_operator.reshape(-1).tolist()
            if int(value) % PRIME != 0
        ]
        counter = Counter(signed_entries)
        for coeff in sorted(counter):
            coeff_rows.append(
                {
                    "generator_id": generator_id,
                    "coefficient_signed": int(coeff),
                    "entry_count": int(counter[coeff]),
                }
            )
        generator_rows.append(
            {
                "generator_id": generator_id,
                "action_order": perm_order(perm),
                "support_operator_rank": gf_rank_mod(support_operator),
                "support_operator_nullity": 56 - gf_rank_mod(support_operator),
                "support_operator_nonzero_count": int(np.count_nonzero(support_operator)),
                "support_inverse_nonzero_count": int(np.count_nonzero(support_inverse)),
                "k23_residual_nonzero_count": int(np.count_nonzero(k23_residual)),
                "frame_residual_nonzero_count": int(np.count_nonzero(frame_residual)),
                "inverse_residual_nonzero_count": int(np.count_nonzero(inverse_residual)),
                "support_operator_order": matrix_order(support_operator),
                "coefficient_distinct_count": len(counter),
                "coefficient_min_signed": min(counter) if counter else 0,
                "coefficient_max_signed": max(counter) if counter else 0,
                "negative_coefficient_count": sum(count for coeff, count in counter.items() if coeff < 0),
                "positive_coefficient_count": sum(count for coeff, count in counter.items() if coeff > 0),
                "signed_l1_total": sum(abs(value) for value in signed_entries),
            }
        )
    obs = {
        "long_k23syz_certified_flag": int(
            long_k23syz.get("status") == "SECTOR33_K23_CANONICAL_SYZYGY_FRAME_BINDING_CERTIFIED"
            and long_k23syz.get("all_checks_pass") is True
        ),
        "long_k23stab_certified_flag": int(
            long_k23stab.get("status") == "SECTOR33_K23_PUNCTURED_SELECTOR_M23_STABILIZER_CERTIFIED"
            and long_k23stab.get("all_checks_pass") is True
        ),
        "long_k23act_certified_flag": int(
            long_k23act.get("status") == "SECTOR33_K23_M23_SUPPORT_BINDING_ROW_ACTION_OBSTRUCTED"
            and long_k23act.get("all_checks_pass") is True
        ),
        "prime_field": PRIME,
        "support_row_count": kernel.shape[1],
        "frame_coordinate_count": frame_lift.shape[1],
        "k23_basis_row_count": kernel.shape[0],
        "frame_lift_syzygy_rank": gf_rank_mod(syzygy_lift),
        "kernel_complement_dimension": complement.shape[1],
        "kernel_complement_rank": gf_rank_mod(complement),
        "kernel_complement_residual_nonzero_count": int(np.count_nonzero(complement_residual)),
        "basis_change_rank": gf_rank_mod(basis_change),
        "basis_change_inverse_residual_nonzero_count": int(
            np.count_nonzero((basis_change @ basis_change_inverse - np.eye(56, dtype=np.int64)) % PRIME)
        ),
        "generator_count": len(generator_rows),
        "linear_lift_generator_count": sum(
            int(
                row["k23_residual_nonzero_count"] == 0
                and row["frame_residual_nonzero_count"] == 0
                and row["inverse_residual_nonzero_count"] == 0
            )
            for row in generator_rows
        ),
        "invertible_support_operator_count": sum(int(row["support_operator_rank"] == 56) for row in generator_rows),
        "k23_intertwiner_residual_nonzero_count": total_k23_residual,
        "frame_intertwiner_residual_nonzero_count": total_frame_residual,
        "inverse_residual_nonzero_count": total_inverse_residual,
        "support_operator_rank_sum": sum(row["support_operator_rank"] for row in generator_rows),
        "support_operator_nullity_sum": sum(row["support_operator_nullity"] for row in generator_rows),
        "row_action_obstruction_preserved_flag": int(
            long_k23act.get("witness", {}).get("summary", {}).get("support_binding_row_action_obstructed_flag", 0)
        ),
        "prime_linear_lift_certified_flag": int(
            total_k23_residual == 0
            and total_frame_residual == 0
            and total_inverse_residual == 0
            and all(row["support_operator_rank"] == 56 for row in generator_rows)
        ),
        "m23_k23_module_action_certified_flag": int(
            long_k23stab.get("witness", {}).get("summary", {}).get("m23_type_action_certified_flag", 0)
            and total_k23_residual == 0
        ),
        "unique_lift_proven_flag": 0,
        "row_permutation_lift_proven_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    matrix_payload = {
        "prime_kernel": kernel.astype(np.int64),
        "frame_lift_mod": frame_lift.astype(np.int64),
        "kernel_complement": complement.astype(np.int64),
        "basis_change": basis_change.astype(np.int64),
        "basis_change_inverse": basis_change_inverse.astype(np.int64),
        "generator_permutations": generator_permutations.astype(np.int64),
        "k23_action_matrices": np.asarray(action_matrices, dtype=np.int64),
        "frame_permutation_matrices": np.asarray(frame_perm_matrices, dtype=np.int64),
        "support_intertwiners": np.asarray(support_intertwiners, dtype=np.int64),
        "support_intertwiner_inverses": np.asarray(support_intertwiner_inverses, dtype=np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "long_k23syz": long_k23syz,
        "long_k23stab": long_k23stab,
        "long_k23act": long_k23act,
        "complement_rows": complement_rows,
        "generator_rows": generator_rows,
        "coeff_rows": coeff_rows,
        "obs_rows": obs_rows,
        "complement_table": table_from_rows(COMPLEMENT_COLUMNS, complement_rows),
        "generator_table": table_from_rows(GENERATOR_COLUMNS, generator_rows),
        "coeff_table": table_from_rows(COEFF_COLUMNS, coeff_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "pivots": pivots,
        "free_columns": free_columns,
        "complement_text_hash": hashlib.sha256(digest_text(COMPLEMENT_COLUMNS, complement_rows).encode("ascii")).hexdigest(),
        "generator_text_hash": hashlib.sha256(digest_text(GENERATOR_COLUMNS, generator_rows).encode("ascii")).hexdigest(),
        "coeff_text_hash": hashlib.sha256(digest_text(COEFF_COLUMNS, coeff_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": (
            obs["long_k23syz_certified_flag"],
            obs["long_k23stab_certified_flag"],
            obs["long_k23act_certified_flag"],
        )
        == (1, 1, 1),
        "basis_decomposition_matches": (
            obs["prime_field"],
            obs["support_row_count"],
            obs["frame_coordinate_count"],
            obs["k23_basis_row_count"],
            obs["frame_lift_syzygy_rank"],
            obs["kernel_complement_dimension"],
            obs["kernel_complement_rank"],
            obs["kernel_complement_residual_nonzero_count"],
            obs["basis_change_rank"],
            obs["basis_change_inverse_residual_nonzero_count"],
        )
        == (PRIME, 56, 24, 23, 23, 33, 33, 0, 56, 0),
        "linear_intertwiner_equations_pass": (
            obs["generator_count"],
            obs["linear_lift_generator_count"],
            obs["invertible_support_operator_count"],
            obs["k23_intertwiner_residual_nonzero_count"],
            obs["frame_intertwiner_residual_nonzero_count"],
            obs["inverse_residual_nonzero_count"],
            obs["support_operator_rank_sum"],
            obs["support_operator_nullity_sum"],
        )
        == (3, 3, 3, 0, 0, 0, 168, 0),
        "module_boundary_matches": (
            obs["row_action_obstruction_preserved_flag"],
            obs["prime_linear_lift_certified_flag"],
            obs["m23_k23_module_action_certified_flag"],
            obs["unique_lift_proven_flag"],
            obs["row_permutation_lift_proven_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (1, 1, 1, 0, 0, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_m23_prime_linear_intertwiner",
        "summary": obs,
        "pivot_columns": rows["pivots"],
        "free_columns": rows["free_columns"],
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies invertible prime-field support intertwiners for the three M23 design generators by fixing a 33-dimensional kernel complement; row-permutation lifting remains obstructed and uniqueness is not claimed.",
    }
    seam_payload = {
        "schema": "long.k23lin.seam@1",
        "status": STATUS,
        "claim": "The certified M23-order selector action has explicit invertible prime-field support intertwiners satisfying K R_g = A_g K and R_g F = F P_g for the three design generators.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23syz": input_entry(
            LONG_K23SYZ_REPORT,
            {
                "status": rows["long_k23syz"].get("status"),
                "certificate_sha256": rows["long_k23syz"].get("certificate_sha256"),
            },
        ),
        "long_k23syz_matrices": input_entry(LONG_K23SYZ_MATRICES),
        "long_k23stab": input_entry(
            LONG_K23STAB_REPORT,
            {
                "status": rows["long_k23stab"].get("status"),
                "certificate_sha256": rows["long_k23stab"].get("certificate_sha256"),
            },
        ),
        "long_k23stab_matrices": input_entry(LONG_K23STAB_MATRICES),
        "long_k23act": input_entry(
            LONG_K23ACT_REPORT,
            {
                "status": rows["long_k23act"].get("status"),
                "certificate_sha256": rows["long_k23act"].get("certificate_sha256"),
            },
        ),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23lin.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23lin certifies the prime-field M23 intertwiners for the K23 support/frame binding.",
        "stage_protocol": {
            "draft": "read long_k23syz, long_k23stab, long_k23act, and their matrices",
            "witness": "emit kernel-complement rows, generator intertwiner rows, coefficient histograms, observables, and matrices",
            "coherence": "check the 23+33 basis decomposition, exact K and frame intertwining residuals, and invertibility",
            "closure": "certify prime-linear M23 support intertwiners while preserving the row-action obstruction and non-uniqueness boundary",
            "emit": "write long_k23lin artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "complement_rows_csv": relpath(OUT_DIR / "complement_rows.csv"),
            "generator_rows_csv": relpath(OUT_DIR / "generator_rows.csv"),
            "coefficient_histogram_csv": relpath(OUT_DIR / "coefficient_histogram.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23lin_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the syzygy frame-lift columns plus a computed kernel complement form a 56-dimensional support basis",
                "for each of the three M23 design generators there is an explicit invertible 56-by-56 support operator",
                "each support operator satisfies K R_g = A_g K with zero residual",
                "each support operator satisfies R_g F = F P_g with zero residual",
                "the K23 rowspace therefore carries the certified M23-order action through the canonical frame binding",
            ],
            "does_not_certify": [
                "that the support lift is unique or canonical",
                "that the M23 action is a row-permutation or signed-row action on the current support rows",
                "that the same lift preserves additional A985 multiplication or physical structure",
                "a rebuild of d20.json or broad bundle closure",
            ],
        },
        "next_highest_yield_item": "Test whether the certified prime-linear K23 intertwiners preserve any additional sector33 structure: support grading, signed coefficients, or the height-coherent projection layer.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23lin.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23lin.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "complement_csv": csv_text(COMPLEMENT_COLUMNS, rows["complement_rows"]),
        "generator_csv": csv_text(GENERATOR_COLUMNS, rows["generator_rows"]),
        "coeff_csv": csv_text(COEFF_COLUMNS, rows["coeff_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "complement_table": rows["complement_table"],
        "generator_table": rows["generator_table"],
        "coeff_table": rows["coeff_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "complement_text_sha256": rows["complement_text_hash"],
            "generator_text_sha256": rows["generator_text_hash"],
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
    (OUT_DIR / "complement_rows.csv").write_text(payloads["complement_csv"], encoding="utf-8")
    (OUT_DIR / "generator_rows.csv").write_text(payloads["generator_csv"], encoding="utf-8")
    (OUT_DIR / "coefficient_histogram.csv").write_text(payloads["coeff_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        complement_table=payloads["complement_table"],
        generator_table=payloads["generator_table"],
        coeff_table=payloads["coeff_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23lin_matrices.npz", **payloads["matrix_payload"])
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
