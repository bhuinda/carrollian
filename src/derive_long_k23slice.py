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


THEOREM_ID = "long_k23slice"
STATUS = "SECTOR33_K23_REP4_6_SLICE_W24_OBSTRUCTION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23slice.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23slice.py"
LONG_K23_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23" / "report.json"
LONG_K23_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23" / "k23_matrices.npz"
LONG_HCSUPP_SUPPORT = D20_INVARIANTS / "proof_obligations" / "long_hcsupp" / "support_rows.csv"
W24_REPORT = D20_INVARIANTS / "proof_obligations" / "d20_w24_hexacode_row_alphabetization" / "report.json"
W24_ARTIFACT = ROOT / "generated" / "d20_w24_hexacode_row_alphabetization.json"

SLICE_TEXT_HASH = "3ab7ea07174023a9773ad53d047283aa92b156d1e79d4715ddd8259d1d75fbb8"
WEIGHT_TEXT_HASH = "6e173afbbc1deca5d5d0a240acad25b07238b137ceba3acf679fb844acff088f"
OBS_TEXT_HASH = "7d4962eba6ce2d27ef364037d45d4b815470c0f7f3ef4807d9d097a110abe7c7"
MATRIX_SHA256 = "16f73d88a8d05733ab9dee0b9f729259106fb73be2952572f3e16f6e4194715d"

ALLOWED_W24_WEIGHTS = {0, 8, 12, 16, 24}

SLICE_COLUMNS = [
    "slice_coordinate_id",
    "support_row_id",
    "relation_id",
    "coefficient_signed",
    "block_i",
    "rep4",
    "binary_active_flag",
    "rref_pivot_flag",
]
WEIGHT_COLUMNS = ["weight", "rowspace_word_count", "w24_allowed_weight_flag", "forbidden_weight_flag"]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_k23_certified_flag",
    "w24_code_certified_flag",
    "support_input_row_count",
    "rep4_grade_1_count",
    "rep4_grade_3_count",
    "rep4_grade_6_count",
    "rep4_grade_12_count",
    "selected_slice_rep4",
    "selected_slice_coordinate_count",
    "k23_kernel_dimension",
    "restricted_binary_rank",
    "w24_rank",
    "restricted_rank_exceeds_w24_rank_flag",
    "rowspace_word_count",
    "min_nonzero_weight",
    "forbidden_weight_class_count",
    "forbidden_word_count",
    "rowspace_doubly_even_flag",
    "permutation_invariant_weight_obstruction_flag",
    "identity_order_w24_contained_words",
    "identity_order_w24_containment_flag",
    "rep4_6_slice_w24_subcode_flag",
    "k23_equality_certified_flag",
    "m23_module_proven_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def gf2_rref(matrix: np.ndarray) -> tuple[np.ndarray, list[int]]:
    work = np.asarray(matrix, dtype=np.uint8).copy() % 2
    row_count, column_count = work.shape
    pivots: list[int] = []
    pivot_row = 0
    for column in range(column_count):
        candidates = np.flatnonzero(work[pivot_row:, column])
        if candidates.size == 0:
            continue
        source_row = pivot_row + int(candidates[0])
        if source_row != pivot_row:
            work[[pivot_row, source_row]] = work[[source_row, pivot_row]]
        for row in range(row_count):
            if row != pivot_row and work[row, column]:
                work[row] ^= work[pivot_row]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == row_count:
            break
    return work, pivots


def row_mask(row: np.ndarray) -> int:
    mask = 0
    for index, value in enumerate(np.asarray(row, dtype=np.uint8).tolist()):
        if int(value) & 1:
            mask |= 1 << index
    return mask


def span_from_basis_masks(basis_masks: list[int]) -> set[int]:
    span = {0}
    for mask in basis_masks:
        span |= {word ^ mask for word in list(span)}
    return span


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = [
        "selected_support_ids",
        "restricted_kernel_mod2",
        "rref_mod2",
        "rowspace_weight_histogram",
        "observable_vector",
    ]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def build_rows() -> dict[str, Any]:
    long_k23 = load_json(LONG_K23_REPORT)
    w24_report = load_json(W24_REPORT)
    w24_artifact = load_json(W24_ARTIFACT)
    support_rows_raw = read_csv_rows(LONG_HCSUPP_SUPPORT)
    support_rows = [{key: int(value) for key, value in row.items()} for row in support_rows_raw]
    with np.load(LONG_K23_MATRICES, allow_pickle=False) as matrices:
        kernel_basis = np.asarray(matrices["kernel_basis"], dtype=np.int64)

    rep4_counts = Counter(row["rep4"] for row in support_rows)
    selected = [row for row in support_rows if row["rep4"] == 6]
    selected_ids = [row["row_id"] for row in selected]
    restricted = (kernel_basis[:, selected_ids] % 2).astype(np.uint8)
    rref, pivots = gf2_rref(restricted)
    rank = len(pivots)
    basis_masks = [row_mask(rref[row_index]) for row_index in range(rank)]
    rowspace = span_from_basis_masks(basis_masks)
    weight_hist = Counter(int(word).bit_count() for word in rowspace)
    histogram_vector = np.asarray([int(weight_hist.get(weight, 0)) for weight in range(25)], dtype=np.int64)
    forbidden_weight_classes = sorted(weight for weight, count in weight_hist.items() if count and weight not in ALLOWED_W24_WEIGHTS)
    forbidden_word_count = sum(int(weight_hist[weight]) for weight in forbidden_weight_classes)
    nonzero_weights = sorted(weight for weight, count in weight_hist.items() if weight and count)
    min_nonzero_weight = nonzero_weights[0] if nonzero_weights else 0
    w24_generators = [int(mask) for mask in w24_artifact["golay_code"]["generator_basis_masks"]]
    w24_code = span_from_basis_masks(w24_generators)
    identity_contained = sum(1 for word in rowspace if word in w24_code)

    pivot_set = set(pivots)
    active_columns = set(np.flatnonzero(restricted.sum(axis=0) > 0).astype(int).tolist())
    slice_rows = [
        {
            "slice_coordinate_id": index,
            "support_row_id": int(row["row_id"]),
            "relation_id": int(row["relation_id"]),
            "coefficient_signed": int(row["coefficient_signed"]),
            "block_i": int(row["block_i"]),
            "rep4": int(row["rep4"]),
            "binary_active_flag": int(index in active_columns),
            "rref_pivot_flag": int(index in pivot_set),
        }
        for index, row in enumerate(selected)
    ]
    weight_rows = [
        {
            "weight": weight,
            "rowspace_word_count": int(weight_hist.get(weight, 0)),
            "w24_allowed_weight_flag": int(weight in ALLOWED_W24_WEIGHTS),
            "forbidden_weight_flag": int(weight_hist.get(weight, 0) > 0 and weight not in ALLOWED_W24_WEIGHTS),
        }
        for weight in range(25)
    ]
    obs = {
        "long_k23_certified_flag": int(
            long_k23.get("status") == "SECTOR33_K23_PUNCTURED_MOG_SYZYGY_APERTURE_TARGET_CERTIFIED"
            and long_k23.get("all_checks_pass") is True
        ),
        "w24_code_certified_flag": int(
            w24_report.get("status") == "D20_W24_HEXACODE_ROW_ALPHABETIZATION_CERTIFIED"
            and w24_report.get("all_checks_pass") is True
        ),
        "support_input_row_count": len(support_rows),
        "rep4_grade_1_count": int(rep4_counts.get(1, 0)),
        "rep4_grade_3_count": int(rep4_counts.get(3, 0)),
        "rep4_grade_6_count": int(rep4_counts.get(6, 0)),
        "rep4_grade_12_count": int(rep4_counts.get(12, 0)),
        "selected_slice_rep4": 6,
        "selected_slice_coordinate_count": len(selected),
        "k23_kernel_dimension": int(kernel_basis.shape[0]),
        "restricted_binary_rank": rank,
        "w24_rank": int(w24_artifact["golay_code"]["rank"]),
        "restricted_rank_exceeds_w24_rank_flag": int(rank > int(w24_artifact["golay_code"]["rank"])),
        "rowspace_word_count": len(rowspace),
        "min_nonzero_weight": min_nonzero_weight,
        "forbidden_weight_class_count": len(forbidden_weight_classes),
        "forbidden_word_count": forbidden_word_count,
        "rowspace_doubly_even_flag": int(all((weight % 4) == 0 for weight, count in weight_hist.items() if count)),
        "permutation_invariant_weight_obstruction_flag": int(
            rank > int(w24_artifact["golay_code"]["rank"])
            and min_nonzero_weight < int(w24_artifact["golay_code"]["minimum_nonzero_weight"])
            and forbidden_word_count > 0
        ),
        "identity_order_w24_contained_words": identity_contained,
        "identity_order_w24_containment_flag": int(identity_contained == len(rowspace)),
        "rep4_6_slice_w24_subcode_flag": 0,
        "k23_equality_certified_flag": 0,
        "m23_module_proven_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    matrix_payload = {
        "selected_support_ids": np.asarray(selected_ids, dtype=np.int64),
        "restricted_kernel_mod2": restricted.astype(np.int64),
        "rref_mod2": rref.astype(np.int64),
        "rowspace_weight_histogram": histogram_vector,
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "long_k23": long_k23,
        "w24_report": w24_report,
        "w24_artifact": w24_artifact,
        "slice_rows": slice_rows,
        "weight_rows": weight_rows,
        "obs_rows": obs_rows,
        "slice_table": table_from_rows(SLICE_COLUMNS, slice_rows),
        "weight_table": table_from_rows(WEIGHT_COLUMNS, weight_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "forbidden_weight_classes": forbidden_weight_classes,
        "basis_masks": basis_masks,
        "slice_text_hash": hashlib.sha256(digest_text(SLICE_COLUMNS, slice_rows).encode("ascii")).hexdigest(),
        "weight_text_hash": hashlib.sha256(digest_text(WEIGHT_COLUMNS, weight_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "long_k23_input_passes": obs["long_k23_certified_flag"] == 1,
        "w24_code_input_passes": obs["w24_code_certified_flag"] == 1,
        "support_grade_histogram_has_unique_24_slice": (
            obs["support_input_row_count"],
            obs["rep4_grade_1_count"],
            obs["rep4_grade_3_count"],
            obs["rep4_grade_6_count"],
            obs["rep4_grade_12_count"],
            obs["selected_slice_coordinate_count"],
        )
        == (56, 6, 14, 24, 12, 24),
        "restricted_rank_is_16_and_exceeds_w24_rank": (
            obs["restricted_binary_rank"],
            obs["w24_rank"],
            obs["restricted_rank_exceeds_w24_rank_flag"],
        )
        == (16, 12, 1),
        "rowspace_weight_profile_obstructs_w24": (
            obs["rowspace_word_count"],
            obs["min_nonzero_weight"],
            obs["forbidden_weight_class_count"],
            obs["forbidden_word_count"],
            obs["rowspace_doubly_even_flag"],
            obs["permutation_invariant_weight_obstruction_flag"],
        )
        == (65536, 1, 13, 50844, 0, 1),
        "identity_order_containment_fails": (
            obs["identity_order_w24_contained_words"],
            obs["identity_order_w24_containment_flag"],
            obs["rep4_6_slice_w24_subcode_flag"],
        )
        == (16, 0, 0),
        "global_claims_remain_open": (
            obs["k23_equality_certified_flag"],
            obs["m23_module_proven_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (0, 0, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_rep4_6_support_slice_w24_obstruction",
        "summary": obs,
        "basis_masks": rows["basis_masks"],
        "forbidden_weight_classes": rows["forbidden_weight_classes"],
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies an obstruction for the canonical rep4=6 24-coordinate support slice only; it does not rule out a non-coordinate quotient or a full 56-to-W24 binding.",
    }
    seam_payload = {
        "schema": "long.k23slice.seam@1",
        "status": STATUS,
        "claim": "The unique 24-coordinate rep4=6 sector33 support-grade slice cannot carry the K23 rowspace as a W24 subcode, because the restricted binary rowspace has rank 16 and forbidden weights.",
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
        "long_hcsupp_support": input_entry(LONG_HCSUPP_SUPPORT),
        "w24_hexacode_row_alphabetization": input_entry(
            W24_REPORT,
            {
                "status": rows["w24_report"].get("status"),
                "certificate_sha256": rows["w24_report"].get("certificate_sha256"),
            },
        ),
        "w24_artifact": input_entry(
            W24_ARTIFACT,
            {
                "status": rows["w24_artifact"].get("status"),
                "artifact_sha256_excluding_this_field": rows["w24_artifact"].get(
                    "artifact_sha256_excluding_this_field"
                ),
            },
        ),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23slice.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23slice certifies that the canonical rep4=6 24-coordinate sector33 support slice is obstructed as a W24 binding target for K23.",
        "stage_protocol": {
            "draft": "read long_k23, long_hcsupp support rows, K23 kernel matrices, and the certified W24 code endpoint",
            "witness": "emit rep4=6 slice rows, rowspace weight histogram rows, observables, and matrix payloads",
            "coherence": "check the unique 24-coordinate support-grade slice, restricted GF(2) rank, rowspace weight profile, and W24 containment failure",
            "closure": "certify a coordinate-slice obstruction while keeping quotient and full binding routes open",
            "emit": "write long_k23slice artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "slice_rows_csv": relpath(OUT_DIR / "slice_rows.csv"),
            "weight_rows_csv": relpath(OUT_DIR / "weight_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23slice_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the sector33 support rows have a unique exact 24-coordinate rep4=6 support-grade slice",
                "K23 restricted to that slice over GF(2) has rank 16",
                "the restricted rowspace has 65,536 words and minimum nonzero weight 1",
                "the restricted rowspace has 50,844 words in weight classes forbidden by W24",
                "no coordinate permutation of this rep4=6 slice can make the restricted K23 rowspace a W24 subcode",
            ],
            "does_not_certify": [
                "absence of a non-coordinate quotient map from the 56 support coordinates to W24",
                "a full 56-to-W24 syzygy basis-binding map",
                "rowspan(K23) equals the W24/Euler-punctured syzygy rowspace",
                "an M23 module action on K23",
                "a rebuild of d20.json or broad bundle closure",
            ],
        },
        "next_highest_yield_item": "Test non-coordinate 56-to-24 quotient maps that collapse the 16 unit directions before comparing the resulting rowspace with W24.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23slice.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23slice.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "slice_csv": csv_text(SLICE_COLUMNS, rows["slice_rows"]),
        "weight_csv": csv_text(WEIGHT_COLUMNS, rows["weight_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "slice_table": rows["slice_table"],
        "weight_table": rows["weight_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "slice_text_sha256": rows["slice_text_hash"],
            "weight_text_sha256": rows["weight_text_hash"],
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
    (OUT_DIR / "slice_rows.csv").write_text(payloads["slice_csv"], encoding="utf-8")
    (OUT_DIR / "weight_rows.csv").write_text(payloads["weight_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        slice_table=payloads["slice_table"],
        weight_table=payloads["weight_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23slice_matrices.npz", **payloads["matrix_payload"])
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
