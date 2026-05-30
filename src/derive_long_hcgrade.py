from __future__ import annotations

import csv
import hashlib
import itertools
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
THEOREM_ID = "long_hcgrade"
STATUS = "LONG_HCGRADE_CENTER_GRADE_RANK_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_hcgrade.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_hcgrade.py"
LONG_HCBASIS_REPORT = D20_INVARIANTS / "proof_obligations" / "long_hcbasis" / "report.json"
LONG_HCBASIS_EXPANSION = D20_INVARIANTS / "proof_obligations" / "long_hcbasis" / "expansion_rows.csv"
LONG_HCBASIS_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_hcbasis" / "center_expansion_matrices.npz"
LONG_HCBASIS_COORDS = D20_INVARIANTS / "proof_obligations" / "long_hcbasis" / "center_coordinates.csv"
LONG_HCSUPP_REPORT = D20_INVARIANTS / "proof_obligations" / "long_hcsupp" / "report.json"
LONG_HCSUPP_SUPPORT = D20_INVARIANTS / "proof_obligations" / "long_hcsupp" / "support_rows.csv"
LONG_HCSCALAR_REPORT = D20_INVARIANTS / "proof_obligations" / "long_hcscalar" / "report.json"

CENTER_TEXT_HASH = "51946de41a45ecf79195eae44419406b2cd3552ab0884dd437e886aca5d98f9e"
FEATURE_TEXT_HASH = "7f6dce3b170c0e5e118a7a7e1f2fdc2ff81c7def00f086bb69f87274db6e5f07"
SELECTED_TEXT_HASH = "a1bbd6d38f37768307d5a8f3cecafbc65ddf664a67149d40c4a36956318ca1ea"
OBS_TEXT_HASH = "33130cd4903e260fc86df2aedb610aa27d786550ef83f095cf8c0cf4af10e3ce"
MATRIX_SHA256 = "a3758b5a5e58399024319c1fbe505181cecb92ca40f0b9b23fa0bc2eb16d39a0"

CENTER_COLUMNS = [
    "center_row_id",
    "object",
    "local_center_index",
    "global_center_index",
    "selected_coordinate_mod",
    "selected_coordinate_signed",
    "support_count",
    "rank_pivot_column",
]
FEATURE_COLUMNS = [
    "feature_id",
    "feature_family_code",
    "object_filter",
    "feature_value",
    "support_count",
    "residual_support_count",
    "single_rank_gain",
    "selected_flag",
]
SELECTED_COLUMNS = [
    "selected_order",
    "feature_id",
    "feature_family_code",
    "object_filter",
    "feature_value",
    "support_count",
    "rank_after_addition",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "support_dimension",
    "center_coordinate_row_count",
    "center_projection_rank",
    "center_kernel_dimension",
    "feature_family_row_count",
    "feature_residual_rank",
    "minimum_grade_row_count",
    "rank33_combo_count",
    "selected_grade_row_count",
    "selected_projection_rank",
    "selected_kernel_dimension",
    "target_projection_rank",
    "target_kernel_dimension",
    "rank_matches_target_flag",
    "kernel_matches_target_flag",
    "center_grade_projection_materialized_flag",
    "lambda3_binding_accepted_flag",
    "pi_foam33_accepted_flag",
    "r_hc_materialized_flag",
    "full_intertwiner_claim_flag",
    "focused_hcgrade_closed_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}

FAMILY_BLOCK = 0
FAMILY_REP4 = 1
FAMILY_ABS_COEFF = 2
FAMILY_SIGN = 3
FAMILY_OBJECT_REP4 = 4
FAMILY_OBJECT_ABS = 5


def signed_mod(value: int, mod: int = FIELD_PRIME) -> int:
    value %= mod
    return value if value <= mod // 2 else value - mod


def sha_array(array: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def read_int_csv(path: Path) -> list[dict[str, int]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [{key: int(value) for key, value in row.items()} for row in csv.DictReader(handle)]


def rref_mod(matrix: np.ndarray, prime: int = FIELD_PRIME) -> tuple[int, list[int], np.ndarray]:
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
    return rank, pivots, work[:rank]


def rank_mod(matrix: np.ndarray, prime: int = FIELD_PRIME) -> int:
    return rref_mod(matrix, prime)[0]


def reduce_against_rref(row: np.ndarray, rref_rows: np.ndarray, pivots: list[int]) -> np.ndarray:
    reduced = np.asarray(row, dtype=np.int64).copy() % FIELD_PRIME
    for basis_row, pivot in zip(rref_rows, pivots):
        factor = int(reduced[pivot]) % FIELD_PRIME
        if factor:
            reduced = (reduced - factor * basis_row) % FIELD_PRIME
    return reduced


def build_center_matrix(expansion_rows: list[dict[str, int]], matrices: np.lib.npyio.NpzFile) -> tuple[np.ndarray, list[int], list[int]]:
    matrix = np.zeros((35, len(expansion_rows)), dtype=np.int64)
    global_indices: list[int] = []
    for col, row in enumerate(expansion_rows):
        obj = row["object"]
        local_index = row["local_relation_index"]
        if obj == 1:
            matrix[0:13, col] = np.asarray(matrices["basis_obj1"][local_index], dtype=np.int64) % FIELD_PRIME
        elif obj == 5:
            matrix[13:35, col] = np.asarray(matrices["basis_obj5"][local_index], dtype=np.int64) % FIELD_PRIME
        else:
            raise ValueError(f"unexpected object {obj}")
    nonzero_rows = np.nonzero(np.count_nonzero(matrix % FIELD_PRIME, axis=1))[0].astype(np.int64)
    return matrix[nonzero_rows], nonzero_rows.tolist(), np.count_nonzero(matrix[nonzero_rows] % FIELD_PRIME, axis=1).astype(int).tolist()


def feature_specs(support_rows: list[dict[str, int]]) -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []

    def add(family: int, value: int, object_filter: int, vector: list[int]) -> None:
        specs.append(
            {
                "feature_family_code": family,
                "feature_value": value,
                "object_filter": object_filter,
                "vector": np.asarray(vector, dtype=np.int64),
            }
        )

    for value in [1, 5]:
        add(FAMILY_BLOCK, value, -1, [1 if row["block_i"] == value else 0 for row in support_rows])
    for value in [1, 3, 6, 12]:
        add(FAMILY_REP4, value, -1, [1 if row["rep4"] == value else 0 for row in support_rows])
    for value in [31250, 164063, 343751, 492189]:
        add(FAMILY_ABS_COEFF, value, -1, [1 if abs(row["coefficient_signed"]) == value else 0 for row in support_rows])
    add(FAMILY_SIGN, -1, -1, [1 if row["coefficient_signed"] < 0 else 0 for row in support_rows])
    add(FAMILY_SIGN, 1, -1, [1 if row["coefficient_signed"] > 0 else 0 for row in support_rows])
    for obj in [1, 5]:
        for value in [1, 3, 6, 12]:
            if any(row["block_i"] == obj and row["rep4"] == value for row in support_rows):
                add(FAMILY_OBJECT_REP4, value, obj, [1 if row["block_i"] == obj and row["rep4"] == value else 0 for row in support_rows])
        for value in sorted({abs(row["coefficient_signed"]) for row in support_rows if row["block_i"] == obj}):
            add(
                FAMILY_OBJECT_ABS,
                value,
                obj,
                [1 if row["block_i"] == obj and abs(row["coefficient_signed"]) == value else 0 for row in support_rows],
            )
    return specs


def first_rank33_combo(center_matrix: np.ndarray, residuals: list[np.ndarray], target_rank: int) -> tuple[list[int], int]:
    feature_count = len(residuals)
    combo_count = 0
    first: list[int] | None = None
    for combo in itertools.combinations(range(feature_count), 5):
        residual_rank = rank_mod(np.vstack([residuals[index] for index in combo]))
        if center_matrix.shape[0] + residual_rank == target_rank:
            combo_count += 1
            if first is None:
                first = list(combo)
    if first is None:
        raise AssertionError("no five-row grade completion found")
    return first, combo_count


def build_rows() -> dict[str, Any]:
    hcbasis = load_json(LONG_HCBASIS_REPORT)
    hcsupp = load_json(LONG_HCSUPP_REPORT)
    hcscalar = load_json(LONG_HCSCALAR_REPORT)
    expansion_rows = read_int_csv(LONG_HCBASIS_EXPANSION)
    coord_rows = read_int_csv(LONG_HCBASIS_COORDS)
    support_rows = read_int_csv(LONG_HCSUPP_SUPPORT)
    matrices = np.load(LONG_HCBASIS_MATRICES, allow_pickle=False)

    center_matrix, global_indices, center_supports = build_center_matrix(expansion_rows, matrices)
    center_rank, center_pivots, center_rref = rref_mod(center_matrix)
    selected_coordinates = {(row["object"], row["center_basis_index"]): row for row in coord_rows}
    center_rows: list[dict[str, int]] = []
    for center_row_id, global_index in enumerate(global_indices):
        if global_index < 13:
            obj = 1
            local_index = global_index
        else:
            obj = 5
            local_index = global_index - 13
        coord = selected_coordinates[(obj, local_index)]
        center_rows.append(
            {
                "center_row_id": center_row_id,
                "object": obj,
                "local_center_index": local_index,
                "global_center_index": global_index,
                "selected_coordinate_mod": coord["coefficient_mod"],
                "selected_coordinate_signed": coord["coefficient_signed"],
                "support_count": center_supports[center_row_id],
                "rank_pivot_column": center_pivots[center_row_id],
            }
        )

    specs = feature_specs(support_rows)
    residuals = [reduce_against_rref(spec["vector"], center_rref, center_pivots) for spec in specs]
    feature_matrix = np.vstack([spec["vector"] for spec in specs])
    residual_matrix = np.vstack(residuals)
    feature_residual_rank = rank_mod(residual_matrix)
    selected_ids, rank33_combo_count = first_rank33_combo(center_matrix, residuals, 33)
    selected_feature_matrix = np.vstack([specs[index]["vector"] for index in selected_ids])
    projection_matrix = np.vstack([center_matrix, selected_feature_matrix]) % FIELD_PRIME
    selected_rank = rank_mod(projection_matrix)

    feature_rows: list[dict[str, int]] = []
    for feature_id, spec in enumerate(specs):
        single_rank = rank_mod(np.vstack([center_matrix, spec["vector"]])) - center_rank
        feature_rows.append(
            {
                "feature_id": feature_id,
                "feature_family_code": int(spec["feature_family_code"]),
                "object_filter": int(spec["object_filter"]),
                "feature_value": int(spec["feature_value"]),
                "support_count": int(np.count_nonzero(spec["vector"])),
                "residual_support_count": int(np.count_nonzero(residuals[feature_id])),
                "single_rank_gain": int(single_rank),
                "selected_flag": int(feature_id in selected_ids),
            }
        )

    selected_rows: list[dict[str, int]] = []
    running = center_matrix.copy()
    for selected_order, feature_id in enumerate(selected_ids):
        row = feature_rows[feature_id]
        running = np.vstack([running, specs[feature_id]["vector"]])
        selected_rows.append(
            {
                "selected_order": selected_order,
                "feature_id": feature_id,
                "feature_family_code": row["feature_family_code"],
                "object_filter": row["object_filter"],
                "feature_value": row["feature_value"],
                "support_count": row["support_count"],
                "rank_after_addition": rank_mod(running),
            }
        )

    scalar_summary = hcscalar.get("witness", {}).get("summary", {})
    obs = {
        "support_dimension": int(center_matrix.shape[1]),
        "center_coordinate_row_count": int(center_matrix.shape[0]),
        "center_projection_rank": int(center_rank),
        "center_kernel_dimension": int(center_matrix.shape[1] - center_rank),
        "feature_family_row_count": int(len(feature_rows)),
        "feature_residual_rank": int(feature_residual_rank),
        "minimum_grade_row_count": 5,
        "rank33_combo_count": int(rank33_combo_count),
        "selected_grade_row_count": int(len(selected_rows)),
        "selected_projection_rank": int(selected_rank),
        "selected_kernel_dimension": int(projection_matrix.shape[1] - selected_rank),
        "target_projection_rank": int(scalar_summary.get("candidate_projection_rank", -1)),
        "target_kernel_dimension": int(scalar_summary.get("candidate_kernel_dimension", -1)),
        "rank_matches_target_flag": int(selected_rank == int(scalar_summary.get("candidate_projection_rank", -1))),
        "kernel_matches_target_flag": int(projection_matrix.shape[1] - selected_rank == int(scalar_summary.get("candidate_kernel_dimension", -1))),
        "center_grade_projection_materialized_flag": 1,
        "lambda3_binding_accepted_flag": 0,
        "pi_foam33_accepted_flag": 0,
        "r_hc_materialized_flag": 0,
        "full_intertwiner_claim_flag": 0,
        "focused_hcgrade_closed_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    matrix_payload = {
        "center_matrix": center_matrix,
        "feature_matrix": feature_matrix,
        "feature_residual_matrix": residual_matrix,
        "selected_feature_matrix": selected_feature_matrix,
        "projection_matrix": projection_matrix,
    }
    matrix_sha = hashlib.sha256(
        b"".join(np.ascontiguousarray(matrix_payload[key]).tobytes() for key in matrix_payload)
    ).hexdigest()
    return {
        "hcbasis": hcbasis,
        "hcsupp": hcsupp,
        "hcscalar": hcscalar,
        "center_rows": center_rows,
        "feature_rows": feature_rows,
        "selected_rows": selected_rows,
        "obs_rows": obs_rows,
        "center_table": table_from_rows(CENTER_COLUMNS, center_rows),
        "feature_table": table_from_rows(FEATURE_COLUMNS, feature_rows),
        "selected_table": table_from_rows(SELECTED_COLUMNS, selected_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_sha,
        "obs": obs,
        "selected_feature_ids": selected_ids,
        "center_text_hash": hashlib.sha256(digest_text(CENTER_COLUMNS, center_rows).encode("ascii")).hexdigest(),
        "feature_text_hash": hashlib.sha256(digest_text(FEATURE_COLUMNS, feature_rows).encode("ascii")).hexdigest(),
        "selected_text_hash": hashlib.sha256(digest_text(SELECTED_COLUMNS, selected_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "long_hcbasis_input_passes": rows["hcbasis"].get("status") == "LONG_HCBASIS_CENTER_EXPANSION_CERTIFIED"
        and rows["hcbasis"].get("all_checks_pass") is True,
        "long_hcsupp_input_passes": rows["hcsupp"].get("status") == "LONG_HCSUPP_PROFILE_CERTIFIED"
        and rows["hcsupp"].get("all_checks_pass") is True,
        "long_hcscalar_input_passes": rows["hcscalar"].get("status") == "LONG_HCSCALAR_ABSTRACT_COMPLETION_CERTIFIED"
        and rows["hcscalar"].get("all_checks_pass") is True,
        "center_rank_is_twenty_eight": (
            obs["support_dimension"],
            obs["center_coordinate_row_count"],
            obs["center_projection_rank"],
            obs["center_kernel_dimension"],
        )
        == (56, 28, 28, 28),
        "finite_feature_family_has_five_residual_ranks": (
            obs["feature_family_row_count"],
            obs["feature_residual_rank"],
            obs["minimum_grade_row_count"],
        )
        == (24, 5, 5),
        "selected_grade_completion_has_target_shape": (
            obs["selected_grade_row_count"],
            obs["selected_projection_rank"],
            obs["selected_kernel_dimension"],
            obs["rank_matches_target_flag"],
            obs["kernel_matches_target_flag"],
        )
        == (5, 33, 23, 1, 1),
        "rank33_completions_are_finite_and_nonempty": obs["rank33_combo_count"] == 256,
        "remaining_intertwiner_inputs_marked_open": (
            obs["center_grade_projection_materialized_flag"],
            obs["lambda3_binding_accepted_flag"],
            obs["pi_foam33_accepted_flag"],
            obs["r_hc_materialized_flag"],
            obs["full_intertwiner_claim_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (1, 0, 0, 0, 0, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "height_coherent_center_grade_rank_lift",
        "summary": obs,
        "selected_feature_ids": rows["selected_feature_ids"],
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This materializes a rank-33 center-grade projection candidate, but not the accepted Lambda3 basis binding or action-return intertwiner.",
    }
    seam_payload = {
        "schema": "long.hcgrade.seam@1",
        "status": STATUS,
        "claim": "The sector33 center-coordinate projection has rank 28, and exactly five finite row-feature directions complete it to a 33x56 rank-33 candidate with kernel 23.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_hcbasis": input_entry(
            LONG_HCBASIS_REPORT,
            {
                "status": rows["hcbasis"].get("status"),
                "certificate_sha256": rows["hcbasis"].get("certificate_sha256"),
            },
        ),
        "long_hcsupp": input_entry(
            LONG_HCSUPP_REPORT,
            {
                "status": rows["hcsupp"].get("status"),
                "certificate_sha256": rows["hcsupp"].get("certificate_sha256"),
            },
        ),
        "long_hcscalar": input_entry(
            LONG_HCSCALAR_REPORT,
            {
                "status": rows["hcscalar"].get("status"),
                "certificate_sha256": rows["hcscalar"].get("certificate_sha256"),
            },
        ),
        "hcbasis_expansion": input_entry(LONG_HCBASIS_EXPANSION),
        "hcbasis_matrices": input_entry(LONG_HCBASIS_MATRICES),
        "hcbasis_coordinates": input_entry(LONG_HCBASIS_COORDS),
        "hcsupp_support": input_entry(LONG_HCSUPP_SUPPORT),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.hcgrade.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_hcgrade certifies the finite rank gap between the source center expansion and a 33-rank support projection candidate.",
        "stage_protocol": {
            "draft": "read long_hcbasis, long_hcsupp, long_hcscalar, the 56 support rows, and the center expansion matrices",
            "witness": "emit center-coordinate rows, finite row-feature rows, selected grading rows, and matrix payloads",
            "coherence": "check ranks 28 -> 33, kernel 28 -> 23, finite feature residual rank five, and open final-intertwiner flags",
            "closure": "certify the center-grade rank lift without claiming the accepted Lambda3 row binding",
            "emit": "write long_hcgrade artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "center_rows_csv": relpath(OUT_DIR / "center_rows.csv"),
            "feature_rows_csv": relpath(OUT_DIR / "feature_rows.csv"),
            "selected_grade_rows_csv": relpath(OUT_DIR / "selected_grade_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "center_grade_projection.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the source center-coordinate projection on the 56 sector33 rows has rank 28 and kernel 28",
                "the declared finite row-feature family has residual rank five modulo the center projection",
                "five grading rows are necessary in this finite feature family to reach rank 33",
                "the selected five-row completion gives a 33x56 rank-33 projection candidate with kernel 23",
            ],
            "does_not_certify": [
                "that the selected feature completion is unique among all possible row functions",
                "the accepted Lambda3(A2+H6) row binding",
                "a materialized R_hc generator family",
                "the full matrix intertwining equation",
            ],
        },
        "next_highest_yield_item": "Use the 28+5 center-grade projection candidate as the candidate pi table, then test the Foam target action against row permutations induced by the sourced C2/R7 action.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.hcgrade.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.hcgrade.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "center_csv": csv_text(CENTER_COLUMNS, rows["center_rows"]),
        "feature_csv": csv_text(FEATURE_COLUMNS, rows["feature_rows"]),
        "selected_csv": csv_text(SELECTED_COLUMNS, rows["selected_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "center_table": rows["center_table"],
        "feature_table": rows["feature_table"],
        "selected_table": rows["selected_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "center_text_sha256": rows["center_text_hash"],
            "feature_text_sha256": rows["feature_text_hash"],
            "selected_text_sha256": rows["selected_text_hash"],
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
    (OUT_DIR / "center_rows.csv").write_text(payloads["center_csv"], encoding="utf-8")
    (OUT_DIR / "feature_rows.csv").write_text(payloads["feature_csv"], encoding="utf-8")
    (OUT_DIR / "selected_grade_rows.csv").write_text(payloads["selected_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        center_table=payloads["center_table"],
        feature_table=payloads["feature_table"],
        selected_table=payloads["selected_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "center_grade_projection.npz", **payloads["matrix_payload"])
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
