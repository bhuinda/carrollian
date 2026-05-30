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


FIELD_PRIME = 1_000_003
H6_LABELS = ["B-", "B+", "V-", "V+", "S-", "S+"]

THEOREM_ID = "long_hcbasis"
STATUS = "LONG_HCBASIS_CENTER_EXPANSION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_hcbasis.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_hcbasis.py"
LONG_HCSUPP_REPORT = D20_INVARIANTS / "proof_obligations" / "long_hcsupp" / "report.json"
E33_ENTRIES = (
    ROOT
    / "data"
    / "evidence"
    / "talagrand_python_handoff"
    / "work"
    / "e33_full_corrected_transport"
    / "e33_vector_entries.csv"
)
CORE_A985 = ROOT / "data" / "core" / "a985.json"
RELATION_MEMBERSHIPS = ROOT / "data" / "raw" / "relation_memberships.npz"
TENSOR_NPZ = ROOT / "data" / "raw" / "Halloween.npz"

BASIS_TEXT_HASH = "1f2ffd28dc434795250950a6ef3a3c7e32ec5d329a087617c450301077b56307"
COORD_TEXT_HASH = "0dfc029ca9c37a73e5a9f95abf3f8e5d532704bf0932ba2b75427f31f76d84ef"
EXPANSION_TEXT_HASH = "2b32a0a1193acf034ef8bac7d4b455b1600c9b136f095a441857b9896cefd1cc"
OBS_TEXT_HASH = "35641c1434e3585cbbdc587968c389f0842bcc7078068bd8ce103484e09cc99d"
MATRIX_SHA256 = "cce3c7ab19b7dbdbf36422bac2aef4d46893a659ab2354770a8b3e786033a5b9"

BASIS_COLUMNS = [
    "basis_id",
    "object",
    "local_pre_idempotent",
    "closed_loop_relation_count",
    "center_dimension",
    "center_basis_rank",
    "primitive_coordinate_nonzero_count",
    "local_support_count",
    "positive_count",
    "negative_count",
    "signed_sum",
    "abs_sum",
]
COORD_COLUMNS = [
    "coord_id",
    "object",
    "local_pre_idempotent",
    "center_basis_index",
    "coefficient_mod",
    "coefficient_signed",
    "nonzero_flag",
]
EXPANSION_COLUMNS = [
    "expansion_id",
    "object",
    "local_pre_idempotent",
    "local_relation_index",
    "relation_id",
    "coefficient_mod",
    "coefficient_signed",
    "e33_match_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "selected_piece_count",
    "selected_object_0",
    "selected_local_pre_idempotent_0",
    "selected_object_1",
    "selected_local_pre_idempotent_1",
    "bplus_closed_loop_relation_count",
    "splus_closed_loop_relation_count",
    "bplus_center_dimension",
    "splus_center_dimension",
    "bplus_local_support_count",
    "splus_local_support_count",
    "total_local_support_count",
    "total_positive_count",
    "total_negative_count",
    "total_signed_sum",
    "bplus_matches_e33_flag",
    "splus_matches_e33_flag",
    "summed_vector_matches_e33_flag",
    "bplus_idempotent_flag",
    "splus_idempotent_flag",
    "summed_sector33_idempotent_flag",
    "center_basis_expansion_materialized_flag",
    "relation_to_lambda3_binding_materialized_flag",
    "pi_foam33_materialized_flag",
    "r_hc_materialized_flag",
    "focused_hcbasis_closed_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}

SELECTED_KEYS = [(1, 12), (5, 6)]


def signed_mod(value: int, mod: int = FIELD_PRIME) -> int:
    value %= mod
    return value if value <= mod // 2 else value - mod


def sha_array(array: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def rref_nullspace_mod(matrix: np.ndarray, mod: int) -> np.ndarray:
    matrix = np.asarray(matrix, dtype=np.int64).copy() % mod
    row_count, col_count = matrix.shape
    rank = 0
    pivots: list[int] = []
    pivot_set: set[int] = set()
    for col in range(col_count):
        rows = np.nonzero(matrix[rank:, col])[0]
        if rows.size == 0:
            continue
        pivot = rank + int(rows[0])
        if pivot != rank:
            matrix[[rank, pivot]] = matrix[[pivot, rank]]
        inv = pow(int(matrix[rank, col]), -1, mod)
        matrix[rank, :] = (matrix[rank, :] * inv) % mod
        indices = np.nonzero(matrix[:, col])[0]
        indices = indices[indices != rank]
        if len(indices):
            values = matrix[indices, col].copy()
            matrix[indices, :] = (matrix[indices, :] - values[:, None] * matrix[rank, :]) % mod
        pivots.append(col)
        pivot_set.add(col)
        rank += 1
        if rank == row_count:
            break

    free = [col for col in range(col_count) if col not in pivot_set]
    basis = np.zeros((col_count, len(free)), dtype=np.int64)
    for idx, free_col in enumerate(free):
        basis[free_col, idx] = 1
    if free:
        for row, pivot_col in enumerate(pivots):
            basis[pivot_col, :] = (-matrix[row, free]) % mod
    return basis


def multiply(triples: np.ndarray, left: np.ndarray, right: np.ndarray) -> np.ndarray:
    alpha = triples[:, 0]
    beta = triples[:, 1]
    gamma = triples[:, 2]
    weights = triples[:, 3] % FIELD_PRIME
    values = (((left[alpha] % FIELD_PRIME) * (right[beta] % FIELD_PRIME)) % FIELD_PRIME * weights) % FIELD_PRIME
    out = np.zeros(left.shape[0], dtype=np.int64)
    np.add.at(out, gamma, values)
    return out % FIELD_PRIME


def rank_mod(matrix: np.ndarray, prime: int = FIELD_PRIME) -> int:
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


def read_e33_vector() -> np.ndarray:
    vector = np.zeros(985, dtype=np.int64)
    with E33_ENTRIES.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            vector[int(row["relation_id"])] = int(row["coefficient_mod"]) % FIELD_PRIME
    return vector


def local_center_data(
    core: dict[str, Any],
    triples: np.ndarray,
    block_i: np.ndarray,
    block_j: np.ndarray,
    obj: int,
    local_pre_idempotent: int,
) -> dict[str, Any]:
    ids = np.where((block_i == obj) & (block_j == obj))[0].astype(np.int64)
    local_index_by_relation = {int(relation): idx for idx, relation in enumerate(ids.tolist())}
    mask = np.isin(triples[:, 0], ids) & np.isin(triples[:, 1], ids) & np.isin(triples[:, 2], ids)
    sub = triples[mask]
    n = int(len(ids))
    tensor = np.zeros((n, n, n), dtype=np.int64)
    for alpha, beta, gamma, value in sub.tolist():
        tensor[
            local_index_by_relation[int(alpha)],
            local_index_by_relation[int(beta)],
            local_index_by_relation[int(gamma)],
        ] = int(value)

    commutator_rows = [(tensor[:, alpha, :] - tensor[alpha, :, :]).T for alpha in range(n)]
    center_basis = rref_nullspace_mod(np.vstack(commutator_rows), FIELD_PRIME)
    stored = core["blocks"][obj]
    primitive_coordinates = np.asarray(stored["primitive_idempotent_coordinates"], dtype=np.int64) % FIELD_PRIME
    if center_basis.shape[1] != int(stored["center_dimension"]):
        raise ValueError(f"center dimension mismatch for object {obj}")
    if primitive_coordinates.shape != (center_basis.shape[1], center_basis.shape[1]):
        raise ValueError(f"primitive coordinate shape mismatch for object {obj}")
    selected_coordinates = primitive_coordinates[local_pre_idempotent]
    local_vec = (center_basis @ selected_coordinates) % FIELD_PRIME
    global_vec = np.zeros(int(block_i.shape[0]), dtype=np.int64)
    global_vec[ids] = local_vec
    return {
        "ids": ids,
        "center_basis": center_basis,
        "selected_coordinates": selected_coordinates,
        "local_vec": local_vec,
        "global_vec": global_vec,
        "stored": stored,
    }


def build_rows() -> dict[str, Any]:
    hcsupp = load_json(LONG_HCSUPP_REPORT)
    core = load_json(CORE_A985)["blocks"]["tube_center_primitive_idempotents"]
    relation_npz = np.load(RELATION_MEMBERSHIPS, allow_pickle=False)
    block_i = np.asarray(relation_npz["block_i"], dtype=np.int64)
    block_j = np.asarray(relation_npz["block_j"], dtype=np.int64)
    triples = np.asarray(np.load(TENSOR_NPZ, allow_pickle=False)["triples"], dtype=np.int64)
    e33 = read_e33_vector()

    basis_rows: list[dict[str, int]] = []
    coord_rows: list[dict[str, int]] = []
    expansion_rows: list[dict[str, int]] = []
    pieces: list[dict[str, Any]] = []
    summed = np.zeros_like(e33)
    coord_id = 0
    expansion_id = 0
    for basis_id, (obj, local_pre_idempotent) in enumerate(SELECTED_KEYS):
        data = local_center_data(core, triples, block_i, block_j, obj, local_pre_idempotent)
        ids = np.asarray(data["ids"], dtype=np.int64)
        local_vec = np.asarray(data["local_vec"], dtype=np.int64)
        global_vec = np.asarray(data["global_vec"], dtype=np.int64)
        selected_coordinates = np.asarray(data["selected_coordinates"], dtype=np.int64)
        support_local = np.nonzero(local_vec % FIELD_PRIME)[0]
        signed_values = [signed_mod(int(local_vec[index])) for index in support_local]
        summed = (summed + global_vec) % FIELD_PRIME
        expected_piece = np.zeros_like(e33)
        expected_piece[ids] = e33[ids]
        piece_matches = bool(np.array_equal(global_vec % FIELD_PRIME, expected_piece % FIELD_PRIME))
        square = multiply(triples, global_vec, global_vec)
        is_idempotent = bool(np.array_equal(square % FIELD_PRIME, global_vec % FIELD_PRIME))
        basis_rows.append(
            {
                "basis_id": basis_id,
                "object": obj,
                "local_pre_idempotent": local_pre_idempotent,
                "closed_loop_relation_count": int(len(ids)),
                "center_dimension": int(data["center_basis"].shape[1]),
                "center_basis_rank": rank_mod(np.asarray(data["center_basis"], dtype=np.int64)),
                "primitive_coordinate_nonzero_count": int(np.count_nonzero(selected_coordinates % FIELD_PRIME)),
                "local_support_count": int(len(support_local)),
                "positive_count": sum(value > 0 for value in signed_values),
                "negative_count": sum(value < 0 for value in signed_values),
                "signed_sum": int(sum(signed_values)),
                "abs_sum": int(sum(abs(value) for value in signed_values)),
            }
        )
        for center_basis_index, value in enumerate(selected_coordinates.tolist()):
            coord_rows.append(
                {
                    "coord_id": coord_id,
                    "object": obj,
                    "local_pre_idempotent": local_pre_idempotent,
                    "center_basis_index": center_basis_index,
                    "coefficient_mod": int(value) % FIELD_PRIME,
                    "coefficient_signed": signed_mod(int(value)),
                    "nonzero_flag": int(int(value) % FIELD_PRIME != 0),
                }
            )
            coord_id += 1
        for local_relation_index in support_local.tolist():
            relation_id = int(ids[local_relation_index])
            expansion_rows.append(
                {
                    "expansion_id": expansion_id,
                    "object": obj,
                    "local_pre_idempotent": local_pre_idempotent,
                    "local_relation_index": int(local_relation_index),
                    "relation_id": relation_id,
                    "coefficient_mod": int(local_vec[local_relation_index]) % FIELD_PRIME,
                    "coefficient_signed": signed_mod(int(local_vec[local_relation_index])),
                    "e33_match_flag": int(int(local_vec[local_relation_index]) % FIELD_PRIME == int(e33[relation_id]) % FIELD_PRIME),
                }
            )
            expansion_id += 1
        pieces.append(
            {
                "object": obj,
                "label": H6_LABELS[obj],
                "local_pre_idempotent": local_pre_idempotent,
                "matches_e33_piece": piece_matches,
                "idempotent": is_idempotent,
                "support": int(len(support_local)),
                "center_basis_sha256": sha_array(np.asarray(data["center_basis"], dtype=np.int64)),
                "local_vector_sha256": sha_array(local_vec),
                "global_vector_sha256": sha_array(global_vec),
            }
        )

    total_signed_values = [signed_mod(int(value)) for value in summed[np.nonzero(summed % FIELD_PRIME)[0]]]
    obs = {
        "selected_piece_count": len(SELECTED_KEYS),
        "selected_object_0": SELECTED_KEYS[0][0],
        "selected_local_pre_idempotent_0": SELECTED_KEYS[0][1],
        "selected_object_1": SELECTED_KEYS[1][0],
        "selected_local_pre_idempotent_1": SELECTED_KEYS[1][1],
        "bplus_closed_loop_relation_count": basis_rows[0]["closed_loop_relation_count"],
        "splus_closed_loop_relation_count": basis_rows[1]["closed_loop_relation_count"],
        "bplus_center_dimension": basis_rows[0]["center_dimension"],
        "splus_center_dimension": basis_rows[1]["center_dimension"],
        "bplus_local_support_count": basis_rows[0]["local_support_count"],
        "splus_local_support_count": basis_rows[1]["local_support_count"],
        "total_local_support_count": int(np.count_nonzero(summed % FIELD_PRIME)),
        "total_positive_count": sum(value > 0 for value in total_signed_values),
        "total_negative_count": sum(value < 0 for value in total_signed_values),
        "total_signed_sum": int(sum(total_signed_values)),
        "bplus_matches_e33_flag": int(bool(pieces[0]["matches_e33_piece"])),
        "splus_matches_e33_flag": int(bool(pieces[1]["matches_e33_piece"])),
        "summed_vector_matches_e33_flag": int(np.array_equal(summed % FIELD_PRIME, e33 % FIELD_PRIME)),
        "bplus_idempotent_flag": int(bool(pieces[0]["idempotent"])),
        "splus_idempotent_flag": int(bool(pieces[1]["idempotent"])),
        "summed_sector33_idempotent_flag": int(np.array_equal(multiply(triples, summed, summed) % FIELD_PRIME, summed % FIELD_PRIME)),
        "center_basis_expansion_materialized_flag": 1,
        "relation_to_lambda3_binding_materialized_flag": 0,
        "pi_foam33_materialized_flag": 0,
        "r_hc_materialized_flag": 0,
        "focused_hcbasis_closed_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    matrix_payload = {
        "basis_obj1": local_center_data(core, triples, block_i, block_j, 1, 12)["center_basis"],
        "basis_obj5": local_center_data(core, triples, block_i, block_j, 5, 6)["center_basis"],
        "sector33_vector": summed,
        "e33_vector": e33,
    }
    matrix_hash = hashlib.sha256(
        b"".join(np.ascontiguousarray(value).tobytes() for value in matrix_payload.values())
    ).hexdigest()
    return {
        "hcsupp": hcsupp,
        "basis_rows": basis_rows,
        "coord_rows": coord_rows,
        "expansion_rows": expansion_rows,
        "obs_rows": obs_rows,
        "basis_table": table_from_rows(BASIS_COLUMNS, basis_rows),
        "coord_table": table_from_rows(COORD_COLUMNS, coord_rows),
        "expansion_table": table_from_rows(EXPANSION_COLUMNS, expansion_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_hash,
        "obs": obs,
        "pieces": pieces,
        "basis_text_hash": hashlib.sha256(digest_text(BASIS_COLUMNS, basis_rows).encode("ascii")).hexdigest(),
        "coord_text_hash": hashlib.sha256(digest_text(COORD_COLUMNS, coord_rows).encode("ascii")).hexdigest(),
        "expansion_text_hash": hashlib.sha256(digest_text(EXPANSION_COLUMNS, expansion_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "long_hcsupp_input_passes": rows["hcsupp"].get("status") == "LONG_HCSUPP_PROFILE_CERTIFIED" and rows["hcsupp"].get("all_checks_pass") is True,
        "selected_keys_match_sector33_profile": (
            obs["selected_object_0"],
            obs["selected_local_pre_idempotent_0"],
            obs["selected_object_1"],
            obs["selected_local_pre_idempotent_1"],
        )
        == (1, 12, 5, 6),
        "local_center_dimensions_match_source": (
            obs["bplus_closed_loop_relation_count"],
            obs["splus_closed_loop_relation_count"],
            obs["bplus_center_dimension"],
            obs["splus_center_dimension"],
        )
        == (16, 104, 13, 22),
        "local_expansions_match_e33": (
            obs["bplus_local_support_count"],
            obs["splus_local_support_count"],
            obs["bplus_matches_e33_flag"],
            obs["splus_matches_e33_flag"],
            obs["summed_vector_matches_e33_flag"],
        )
        == (12, 44, 1, 1, 1),
        "idempotent_laws_hold": (
            obs["bplus_idempotent_flag"],
            obs["splus_idempotent_flag"],
            obs["summed_sector33_idempotent_flag"],
        )
        == (1, 1, 1),
        "sign_balance_matches_e33": (
            obs["total_local_support_count"],
            obs["total_positive_count"],
            obs["total_negative_count"],
            obs["total_signed_sum"],
        )
        == (56, 28, 28, 0),
        "remaining_intertwiner_inputs_marked_open": (
            obs["center_basis_expansion_materialized_flag"],
            obs["relation_to_lambda3_binding_materialized_flag"],
            obs["pi_foam33_materialized_flag"],
            obs["r_hc_materialized_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (1, 0, 0, 0, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "height_coherent_local_center_expansion",
        "summary": obs,
        "pieces": rows["pieces"],
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This materializes the local center-basis expansion of the sector33 e33 vector, but not the Lambda3(A2+H6) basis binding or pi_Foam33.",
    }
    seam_payload = {
        "schema": "long.hcbasis.seam@1",
        "status": STATUS,
        "claim": "The two sector33 local pre-idempotents are reconstructed from T_985 local center bases and sum exactly to the materialized e33 relation vector.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_hcsupp": input_entry(LONG_HCSUPP_REPORT, {"status": rows["hcsupp"].get("status"), "certificate_sha256": rows["hcsupp"].get("certificate_sha256")}),
        "e33_entries": input_entry(E33_ENTRIES),
        "core_a985": input_entry(CORE_A985),
        "relation_memberships": input_entry(RELATION_MEMBERSHIPS),
        "t985_tensor": input_entry(TENSOR_NPZ),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.hcbasis.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_hcbasis certifies the source reconstruction of e33 from the B+ local 12 and S+ local 6 center-basis expansions.",
        "stage_protocol": {
            "draft": "read long_hcsupp, e33 rows, raw relation memberships, T_985, and stored tube-center primitive coordinates",
            "witness": "emit local center summaries, primitive-coordinate rows, relation expansion rows, and matrix payloads",
            "coherence": "check center dimensions, support counts, coefficient equality with e33, idempotent laws, and open pi/R_hc flags",
            "closure": "certify the local center-basis expansion without claiming the Lambda3 binding",
            "emit": "write long_hcbasis artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "basis_summary_csv": relpath(OUT_DIR / "basis_summary.csv"),
            "center_coordinates_csv": relpath(OUT_DIR / "center_coordinates.csv"),
            "expansion_rows_csv": relpath(OUT_DIR / "expansion_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "center_expansion_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the selected sector33 local pre-idempotents are B+ local 12 and S+ local 6",
                "the local center dimensions are 13 for B+ and 22 for S+",
                "the reconstructed local vectors have support 12 and 44 and sum exactly to e33",
                "the selected local pieces and their sum satisfy the idempotent law over the certified tensor",
            ],
            "does_not_certify": [
                "the relation-row to Lambda3(A2+H6) basis binding",
                "the actual pi_Foam33 relation-support projection table",
                "a materialized R_hc generator family",
                "the full matrix intertwining equation",
            ],
        },
        "next_highest_yield_item": "Use the materialized center-basis expansion to search for a canonical 56-row grading or filtration that can be compared to the ordered Lambda3(A2+H6) basis.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.hcbasis.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {"schema": "long.hcbasis.manifest@1", "name": THEOREM_ID, "status": STATUS, "inputs": inputs, "outputs": report["outputs"], "report_sha256": report["certificate_sha256"]}
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "basis_csv": csv_text(BASIS_COLUMNS, rows["basis_rows"]),
        "coord_csv": csv_text(COORD_COLUMNS, rows["coord_rows"]),
        "expansion_csv": csv_text(EXPANSION_COLUMNS, rows["expansion_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "basis_table": rows["basis_table"],
        "coord_table": rows["coord_table"],
        "expansion_table": rows["expansion_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "basis_text_sha256": rows["basis_text_hash"],
            "coord_text_sha256": rows["coord_text_hash"],
            "expansion_text_sha256": rows["expansion_text_hash"],
            "obs_text_sha256": rows["obs_text_hash"],
            "matrix_sha256": rows["matrix_sha256"],
        },
    }


def update_index(report: dict[str, Any]) -> None:
    if INDEX_PATH.exists():
        index_payload = load_json(INDEX_PATH)
        obligations = [row for row in index_payload.get("obligations", []) if isinstance(row, dict) and row.get("id") != THEOREM_ID]
        schema = index_payload.get("schema", "d20.proof_obligation_registry.source_drop")
    else:
        obligations = []
        schema = "d20.proof_obligation_registry.source_drop"
    obligations.append({"id": THEOREM_ID, "manifest": relpath(OUT_DIR / "manifest.json"), "report": relpath(OUT_DIR / "report.json"), "report_sha256": report["certificate_sha256"], "status": report["status"]})
    obligations.sort(key=lambda row: str(row["id"]))
    index = {"schema": schema, "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT", "obligation_count": len(obligations), "obligations": obligations}
    index["registry_sha256"] = self_hash(index, "registry_sha256")
    write_json(INDEX_PATH, index)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "basis_summary.csv").write_text(payloads["basis_csv"], encoding="utf-8")
    (OUT_DIR / "center_coordinates.csv").write_text(payloads["coord_csv"], encoding="utf-8")
    (OUT_DIR / "expansion_rows.csv").write_text(payloads["expansion_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        basis_table=payloads["basis_table"],
        coord_table=payloads["coord_table"],
        expansion_table=payloads["expansion_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "center_expansion_matrices.npz", **payloads["matrix_payload"])
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
