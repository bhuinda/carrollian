from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from .derive_long_k23fam import (
        invert_square,
        nullspace_basis,
        read_csv_rows,
        right_inverse,
    )
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from derive_long_k23fam import (
        invert_square,
        nullspace_basis,
        read_csv_rows,
        right_inverse,
    )
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_k23poly"
STATUS = "SECTOR33_K23_CONCATENATIVE_POLYMORPHISM_CARRIER_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PRIME = 1_000_003

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23poly.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23poly.py"
LONG_K23CL_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23cl" / "report.json"
LONG_K23CL_CLOSURE_ROWS = D20_INVARIANTS / "proof_obligations" / "long_k23cl" / "closure_rows.csv"
LONG_K23CL_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23cl" / "k23cl_matrices.npz"
LONG_K23UNIT_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23unit" / "report.json"
LONG_K23UNIT_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23unit" / "k23unit_matrices.npz"
LONG_K23RH_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23rh" / "report.json"
LONG_K23RH_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23rh" / "k23rh_matrices.npz"
LONG_K23FAM_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23fam" / "report.json"
LONG_K23FAM_CANDIDATES = D20_INVARIANTS / "proof_obligations" / "long_k23fam" / "candidate_rows.csv"

BEST_CANDIDATE_ID = 10
WORD_DEPTH = 2
WORD_TEXT_HASH = "47a9a2fadcb79a285ef733af76d47933d6bdad0ba5a251931df8cfbf2db97ed4"
FINGERPRINT_TEXT_HASH = "56957f95237d9a8c688ffc8206fd48cbac4c9cebcdb0af4783d80048d6b5c3f3"
OBS_TEXT_HASH = "6296b9b561fc31920910c20b337d76e0a3157995c64d19cb174404ffa7f4c141"
MATRIX_SHA256 = "f864a8b2ceef97db9cf107eed3b54278067e349d432bfbc72992beb4f05b1b2f"

WORD_COLUMNS = [
    "word_id",
    "word_length",
    "first_generator_id",
    "second_generator_id",
    "quotient_residual_nonzero_count",
    "unit_residual_nonzero_count",
    "product_residual_nonzero_count",
    "product_preserved_flag",
    "lift_nonzero_count",
    "target_nonzero_count",
]
FINGERPRINT_COLUMNS = [
    "fingerprint_id",
    "word_id",
    "matrix_role_code",
    "sha256",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_k23cl_certified_flag",
    "long_k23unit_certified_flag",
    "long_k23rh_certified_flag",
    "long_k23fam_certified_flag",
    "best_candidate_id",
    "closure_dimension",
    "target_dimension",
    "generator_count",
    "word_depth",
    "word_count",
    "identity_word_count",
    "length_one_word_count",
    "length_two_word_count",
    "fingerprint_row_count",
    "quotient_residual_total",
    "unit_residual_total",
    "identity_product_residual",
    "length_one_product_preserved_count",
    "length_two_product_preserved_count",
    "nonidentity_product_preserved_count",
    "square_word_count",
    "square_return_word_count",
    "offdiagonal_length_two_word_count",
    "offdiagonal_product_preserved_count",
    "unique_lift_fingerprint_count",
    "unique_target_fingerprint_count",
    "word_product_residual_min",
    "word_product_residual_max",
    "nonidentity_product_residual_min",
    "nonidentity_product_residual_max",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def matrix_sha256(matrix: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(matrix, dtype=np.int64).tobytes()).hexdigest()


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = [
        "generator_lifts",
        "target_generators",
        "word_table",
        "word_product_residual_vector",
        "observable_vector",
    ]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def product_residual_nonzero(lift: np.ndarray, product_tensor: np.ndarray) -> int:
    lhs = np.einsum("kl,lij->kij", lift, product_tensor, optimize=True) % PRIME
    rhs = np.empty_like(product_tensor)
    for target_row in range(product_tensor.shape[0]):
        rhs[target_row] = (lift.T @ product_tensor[target_row] @ lift) % PRIME
    return int(np.count_nonzero((lhs - rhs) % PRIME))


def load_best_candidate() -> dict[str, int]:
    candidates = [{key: int(value) for key, value in row.items()} for row in read_csv_rows(LONG_K23FAM_CANDIDATES)]
    matches = [row for row in candidates if row["candidate_id"] == BEST_CANDIDATE_ID]
    if len(matches) != 1:
        raise AssertionError("best candidate row missing")
    return matches[0]


def build_repaired_projection(
    old_projection: np.ndarray,
    product_tensor: np.ndarray,
    unit_vector: np.ndarray,
    best_candidate: dict[str, int],
) -> np.ndarray:
    projection = np.zeros((old_projection.shape[0], product_tensor.shape[0]), dtype=np.int64)
    projection[:, : old_projection.shape[1]] = old_projection
    fixed_unit = np.zeros(projection.shape[0], dtype=np.int64)
    fixed_unit[best_candidate["fixed_target_row"]] = 1
    delta = (fixed_unit - projection @ unit_vector) % PRIME
    repaired = projection.copy()
    changed_unit_column = best_candidate["changed_unit_column"]
    appended_column = best_candidate["appended_column"]
    appended_target_row = best_candidate["appended_target_row"]
    repaired[:, changed_unit_column] = (repaired[:, changed_unit_column] + delta) % PRIME
    repaired[appended_target_row, appended_column] = (repaired[appended_target_row, appended_column] + 1) % PRIME
    return repaired % PRIME


def build_generator_lifts(
    repaired_projection: np.ndarray,
    r_foam_matrices: np.ndarray,
) -> np.ndarray:
    kernel = nullspace_basis(repaired_projection)
    right_inv = right_inverse(repaired_projection)
    split_basis = np.column_stack([kernel.T, right_inv]) % PRIME
    split_inverse = invert_square(split_basis)
    lifts = []
    for r_foam in r_foam_matrices:
        diagonal_action = np.zeros((repaired_projection.shape[1], repaired_projection.shape[1]), dtype=np.int64)
        diagonal_action[: kernel.shape[0], : kernel.shape[0]] = np.eye(kernel.shape[0], dtype=np.int64)
        diagonal_action[kernel.shape[0] :, kernel.shape[0] :] = r_foam
        lifts.append((split_basis @ diagonal_action @ split_inverse) % PRIME)
    return np.asarray(lifts, dtype=np.int64)


def word_specs(generator_count: int) -> list[tuple[int, int, int]]:
    specs: list[tuple[int, int, int]] = [(0, -1, -1)]
    for first in range(generator_count):
        specs.append((1, first, -1))
    for first in range(generator_count):
        for second in range(generator_count):
            specs.append((2, first, second))
    return specs


def compose_word(
    spec: tuple[int, int, int],
    lifts: np.ndarray,
    targets: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    length, first, second = spec
    if length == 0:
        return (
            np.eye(lifts.shape[1], dtype=np.int64),
            np.eye(targets.shape[1], dtype=np.int64),
        )
    if length == 1:
        return lifts[first], targets[first]
    return (lifts[second] @ lifts[first]) % PRIME, (targets[second] @ targets[first]) % PRIME


def build_rows() -> dict[str, Any]:
    long_k23cl = load_json(LONG_K23CL_REPORT)
    long_k23unit = load_json(LONG_K23UNIT_REPORT)
    long_k23rh = load_json(LONG_K23RH_REPORT)
    long_k23fam = load_json(LONG_K23FAM_REPORT)
    best_candidate = load_best_candidate()
    closure_rows = [{key: int(value) for key, value in row.items()} for row in read_csv_rows(LONG_K23CL_CLOSURE_ROWS)]
    with np.load(LONG_K23CL_MATRICES, allow_pickle=False) as matrices:
        product_tensor = np.asarray(matrices["closure_product_tensor"], dtype=np.int64) % PRIME
    with np.load(LONG_K23UNIT_MATRICES, allow_pickle=False) as matrices:
        unit_vector = np.asarray(matrices["unit_vector"], dtype=np.int64) % PRIME
    with np.load(LONG_K23RH_MATRICES, allow_pickle=False) as matrices:
        old_projection = np.asarray(matrices["projection_matrix"], dtype=np.int64) % PRIME
        r_foam_matrices = np.asarray(matrices["r_foam_matrices"], dtype=np.int64) % PRIME

    repaired_projection = build_repaired_projection(old_projection, product_tensor, unit_vector, best_candidate)
    generator_lifts = build_generator_lifts(repaired_projection, r_foam_matrices)

    word_rows = []
    fingerprint_rows = []
    product_residuals = []
    quotient_residuals = []
    unit_residuals = []
    fingerprint_id = 0
    for word_id, spec in enumerate(word_specs(generator_lifts.shape[0])):
        length, first, second = spec
        lift_word, target_word = compose_word(spec, generator_lifts, r_foam_matrices)
        quotient_residual = int(np.count_nonzero((repaired_projection @ lift_word - target_word @ repaired_projection) % PRIME))
        unit_residual = int(np.count_nonzero((lift_word @ unit_vector - unit_vector) % PRIME))
        product_residual = product_residual_nonzero(lift_word, product_tensor)
        product_residuals.append(product_residual)
        quotient_residuals.append(quotient_residual)
        unit_residuals.append(unit_residual)
        word_rows.append(
            {
                "word_id": word_id,
                "word_length": length,
                "first_generator_id": first,
                "second_generator_id": second,
                "quotient_residual_nonzero_count": quotient_residual,
                "unit_residual_nonzero_count": unit_residual,
                "product_residual_nonzero_count": product_residual,
                "product_preserved_flag": int(product_residual == 0),
                "lift_nonzero_count": int(np.count_nonzero(lift_word)),
                "target_nonzero_count": int(np.count_nonzero(target_word)),
            }
        )
        for role_code, matrix in ((0, lift_word), (1, target_word)):
            fingerprint_rows.append(
                {
                    "fingerprint_id": fingerprint_id,
                    "word_id": word_id,
                    "matrix_role_code": role_code,
                    "sha256": matrix_sha256(matrix),
                }
            )
            fingerprint_id += 1

    length_one_rows = [row for row in word_rows if row["word_length"] == 1]
    length_two_rows = [row for row in word_rows if row["word_length"] == 2]
    square_rows = [row for row in length_two_rows if row["first_generator_id"] == row["second_generator_id"]]
    offdiagonal_rows = [row for row in length_two_rows if row["first_generator_id"] != row["second_generator_id"]]
    nonidentity_rows = [row for row in word_rows if row["word_length"] > 0]
    identity_lift_hash = fingerprint_rows[0]["sha256"]
    identity_target_hash = fingerprint_rows[1]["sha256"]
    lift_hashes = {
        row["word_id"]: row["sha256"] for row in fingerprint_rows if row["matrix_role_code"] == 0
    }
    target_hashes = {
        row["word_id"]: row["sha256"] for row in fingerprint_rows if row["matrix_role_code"] == 1
    }
    square_return_word_count = sum(
        int(
            lift_hashes[row["word_id"]] == identity_lift_hash
            and target_hashes[row["word_id"]] == identity_target_hash
        )
        for row in square_rows
    )
    obs = {
        "long_k23cl_certified_flag": int(
            long_k23cl.get("status") == "SECTOR33_K23_MULTIPLICATION_CLOSURE60_CERTIFIED"
            and long_k23cl.get("all_checks_pass") is True
        ),
        "long_k23unit_certified_flag": int(
            long_k23unit.get("status") == "SECTOR33_K23_CLOSURE60_UNIT_PROJECTION_OBSTRUCTION_CERTIFIED"
            and long_k23unit.get("all_checks_pass") is True
        ),
        "long_k23rh_certified_flag": int(
            long_k23rh.get("status") == "SECTOR33_K23_RHC_SOURCE_LIFT_CERTIFIED"
            and long_k23rh.get("all_checks_pass") is True
        ),
        "long_k23fam_certified_flag": int(
            long_k23fam.get("status") == "SECTOR33_K23_MINIMAL_REPAIRED_PROJECTION_FAMILY_OBSTRUCTED"
            and long_k23fam.get("all_checks_pass") is True
        ),
        "best_candidate_id": BEST_CANDIDATE_ID,
        "closure_dimension": int(product_tensor.shape[0]),
        "target_dimension": int(repaired_projection.shape[0]),
        "generator_count": int(generator_lifts.shape[0]),
        "word_depth": WORD_DEPTH,
        "word_count": len(word_rows),
        "identity_word_count": sum(int(row["word_length"] == 0) for row in word_rows),
        "length_one_word_count": len(length_one_rows),
        "length_two_word_count": len(length_two_rows),
        "fingerprint_row_count": len(fingerprint_rows),
        "quotient_residual_total": sum(quotient_residuals),
        "unit_residual_total": sum(unit_residuals),
        "identity_product_residual": word_rows[0]["product_residual_nonzero_count"],
        "length_one_product_preserved_count": sum(row["product_preserved_flag"] for row in length_one_rows),
        "length_two_product_preserved_count": sum(row["product_preserved_flag"] for row in length_two_rows),
        "nonidentity_product_preserved_count": sum(row["product_preserved_flag"] for row in nonidentity_rows),
        "square_word_count": len(square_rows),
        "square_return_word_count": square_return_word_count,
        "offdiagonal_length_two_word_count": len(offdiagonal_rows),
        "offdiagonal_product_preserved_count": sum(row["product_preserved_flag"] for row in offdiagonal_rows),
        "unique_lift_fingerprint_count": len(set(lift_hashes.values())),
        "unique_target_fingerprint_count": len(set(target_hashes.values())),
        "word_product_residual_min": min(product_residuals),
        "word_product_residual_max": max(product_residuals),
        "nonidentity_product_residual_min": min(row["product_residual_nonzero_count"] for row in nonidentity_rows),
        "nonidentity_product_residual_max": max(row["product_residual_nonzero_count"] for row in nonidentity_rows),
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    word_table = table_from_rows(WORD_COLUMNS, word_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "generator_lifts": generator_lifts.astype(np.int64),
        "target_generators": r_foam_matrices.astype(np.int64),
        "word_table": word_table.astype(np.int64),
        "word_product_residual_vector": np.asarray(product_residuals, dtype=np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "long_k23cl": long_k23cl,
        "long_k23unit": long_k23unit,
        "long_k23rh": long_k23rh,
        "long_k23fam": long_k23fam,
        "closure_rows": closure_rows,
        "word_rows": word_rows,
        "fingerprint_rows": fingerprint_rows,
        "obs_rows": obs_rows,
        "word_table": word_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "word_text_hash": hashlib.sha256(digest_text(WORD_COLUMNS, word_rows).encode("ascii")).hexdigest(),
        "fingerprint_text_hash": hashlib.sha256(
            digest_text(FINGERPRINT_COLUMNS, fingerprint_rows).encode("ascii")
        ).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": (
            obs["long_k23cl_certified_flag"],
            obs["long_k23unit_certified_flag"],
            obs["long_k23rh_certified_flag"],
            obs["long_k23fam_certified_flag"],
        )
        == (1, 1, 1, 1),
        "word_profile_matches": (
            obs["closure_dimension"],
            obs["target_dimension"],
            obs["generator_count"],
            obs["word_depth"],
            obs["word_count"],
            obs["identity_word_count"],
            obs["length_one_word_count"],
            obs["length_two_word_count"],
            obs["fingerprint_row_count"],
        )
        == (60, 33, 9, 2, 91, 1, 9, 81, 182),
        "concatenative_quotient_unit_exact": (
            obs["quotient_residual_total"],
            obs["unit_residual_total"],
        )
        == (0, 0),
        "product_boundary_matches": (
            obs["identity_product_residual"],
            obs["length_one_product_preserved_count"],
            obs["length_two_product_preserved_count"],
            obs["nonidentity_product_preserved_count"],
        )
        == (0, 0, 9, 9),
        "square_return_profile_matches": (
            obs["square_word_count"],
            obs["square_return_word_count"],
            obs["offdiagonal_length_two_word_count"],
            obs["offdiagonal_product_preserved_count"],
        )
        == (9, 9, 72, 0),
        "boundary_flags_match": obs["complete_goal_claim_flag"] == 0,
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_concatenative_polymorphism_carrier",
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies a word-composable quotient/unit carrier for the best repaired projection while preserving the product-action obstruction at generator and off-diagonal length-two word depth.",
    }
    seam_payload = {
        "schema": "long.k23poly.seam@1",
        "status": STATUS,
        "claim": "The best repaired K23 projection supports a concatenative quotient/unit carrier through the nine generator alphabet, but not a product-preserving algebra action.",
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
        "long_k23rh": input_entry(
            LONG_K23RH_REPORT,
            {"status": rows["long_k23rh"].get("status"), "certificate_sha256": rows["long_k23rh"].get("certificate_sha256")},
        ),
        "long_k23fam": input_entry(
            LONG_K23FAM_REPORT,
            {"status": rows["long_k23fam"].get("status"), "certificate_sha256": rows["long_k23fam"].get("certificate_sha256")},
        ),
        "long_k23cl_closure_rows": input_entry(LONG_K23CL_CLOSURE_ROWS),
        "long_k23cl_matrices": input_entry(LONG_K23CL_MATRICES),
        "long_k23unit_matrices": input_entry(LONG_K23UNIT_MATRICES),
        "long_k23rh_matrices": input_entry(LONG_K23RH_MATRICES),
        "long_k23fam_candidates": input_entry(LONG_K23FAM_CANDIDATES),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23poly.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23poly certifies the K23 word-level concatenative carrier boundary.",
        "stage_protocol": {
            "draft": "read closure60 product, unit, R_hc target action, and the certified minimal projection-family obstruction",
            "witness": "emit length-zero, length-one, and length-two word rows plus matrix fingerprint dereference rows",
            "coherence": "check quotient/unit residuals, word counts, product residual boundary, and matrix payload hash",
            "closure": "certify word-level quotient/unit concatenation while keeping generator product preservation and broader word-depth product behavior open",
            "emit": "write long_k23poly artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "word_rows_csv": relpath(OUT_DIR / "word_rows.csv"),
            "fingerprint_rows_csv": relpath(OUT_DIR / "fingerprint_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23poly_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the best minimal repaired projection is candidate 10 from long_k23fam",
                "the nine generator lifts compose as finite words over the closure60 carrier",
                "all depth-0, depth-1, and depth-2 words have zero quotient-intertwiner residual",
                "all depth-0, depth-1, and depth-2 words fix the closure60 unit",
                "all generator words and all off-diagonal depth-two words remain product-obstructed",
                "the nine square depth-two words return to the identity source and target fingerprints",
                "the fingerprint table gives stable matrix dereference hashes for every tested source and target word matrix",
            ],
            "does_not_certify": [
                "product preservation for any generator or off-diagonal depth-two word",
                "a finite-depth exhaustive word-language theorem beyond depth two",
                "that a different repaired-projection family cannot support a stronger carrier",
                "continuum geometry",
                "bundle-wide integration",
                "a final broad-goal closure claim",
            ],
        },
        "next_highest_yield_item": "Promote the depth-two word carrier into a bounded rewrite-system search: test whether residual fingerprints admit a finite congruence that closes product defects without changing the quotient/unit carrier.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23poly.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23poly.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "word_csv": csv_text(WORD_COLUMNS, rows["word_rows"]),
        "fingerprint_csv": csv_text(FINGERPRINT_COLUMNS, rows["fingerprint_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "word_table": rows["word_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "word_text_sha256": rows["word_text_hash"],
            "fingerprint_text_sha256": rows["fingerprint_text_hash"],
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
    (OUT_DIR / "word_rows.csv").write_text(payloads["word_csv"], encoding="utf-8")
    (OUT_DIR / "fingerprint_rows.csv").write_text(payloads["fingerprint_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        word_table=payloads["word_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23poly_matrices.npz", **payloads["matrix_payload"])
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
