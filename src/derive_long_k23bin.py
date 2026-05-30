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


THEOREM_ID = "long_k23bin"
STATUS = "SECTOR33_K23_BINARY_ROWSPACE_PROFILE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23bin.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23bin.py"
LONG_K23_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23" / "report.json"
LONG_K23_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23" / "k23_matrices.npz"
LONG_HCSUPP_SUPPORT = D20_INVARIANTS / "proof_obligations" / "long_hcsupp" / "support_rows.csv"

BASIS_TEXT_HASH = "2d32f3a65d69e5c4d3ef1dfa27aa3d9167c190b5c6389a70925f71c1c83e1d3e"
COLUMN_TEXT_HASH = "f3a294b82b2412f430e8d398c6f184c6e5b8b09d95a37a5811f60998bca759d6"
WEIGHT_TEXT_HASH = "aa87741617bd4fff771ad517aac256959d6d487291b472756f71602d48129823"
OBS_TEXT_HASH = "12e9b1f75f1433d0f827be94ed54b2577144b7308f5e3f9224c07f11692d562b"
MATRIX_SHA256 = "ac4bd0fd73eb1b6974391b79780c488a6285fdd75a157d10fcb1e97d84f55ecf"

BASIS_COLUMNS = ["basis_row_id", "binary_weight", "binary_mask"]
COLUMN_COLUMNS = [
    "support_row_id",
    "relation_id",
    "block_i",
    "rep4",
    "basis_column_mod2_count",
    "binary_active_flag",
]
WEIGHT_COLUMNS = ["weight", "rowspace_word_count"]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_k23_certified_flag",
    "support_input_row_count",
    "kernel_basis_row_count",
    "kernel_basis_column_count",
    "binary_rank",
    "binary_rowspace_word_count",
    "min_nonzero_weight",
    "max_weight",
    "weight_one_word_count",
    "zero_column_count",
    "active_column_count",
    "odd_column_count",
    "even_nonzero_column_count",
    "binary_even_code_flag",
    "binary_doubly_even_code_flag",
    "quotient_collapse_required_flag",
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
        "kernel_mod2",
        "rref_mod2",
        "rowspace_weight_histogram",
        "column_activity",
        "observable_vector",
    ]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def build_rows() -> dict[str, Any]:
    long_k23 = load_json(LONG_K23_REPORT)
    with np.load(LONG_K23_MATRICES, allow_pickle=False) as matrices:
        kernel_basis = np.asarray(matrices["kernel_basis"], dtype=np.int64)
    support_rows = [{key: int(value) for key, value in row.items()} for row in read_csv_rows(LONG_HCSUPP_SUPPORT)]
    kernel_mod2 = (kernel_basis % 2).astype(np.uint8)
    rref, pivots = gf2_rref(kernel_mod2)
    rank = len(pivots)
    basis_masks = [row_mask(rref[row_index]) for row_index in range(rank)]
    rowspace = span_from_basis_masks(basis_masks)
    weight_hist = Counter(int(word).bit_count() for word in rowspace)
    histogram_vector = np.asarray([int(weight_hist.get(weight, 0)) for weight in range(57)], dtype=np.int64)
    column_activity = kernel_mod2.sum(axis=0).astype(np.int64)
    zero_columns = [index for index, value in enumerate(column_activity.tolist()) if int(value) == 0]
    nonzero_weights = sorted(weight for weight, count in weight_hist.items() if weight and count)

    basis_rows = [
        {
            "basis_row_id": row_index,
            "binary_weight": int(kernel_mod2[row_index].sum()),
            "binary_mask": row_mask(kernel_mod2[row_index]),
        }
        for row_index in range(kernel_mod2.shape[0])
    ]
    column_rows = [
        {
            "support_row_id": int(row["row_id"]),
            "relation_id": int(row["relation_id"]),
            "block_i": int(row["block_i"]),
            "rep4": int(row["rep4"]),
            "basis_column_mod2_count": int(column_activity[int(row["row_id"])]),
            "binary_active_flag": int(column_activity[int(row["row_id"])] > 0),
        }
        for row in support_rows
    ]
    weight_rows = [
        {
            "weight": weight,
            "rowspace_word_count": int(weight_hist.get(weight, 0)),
        }
        for weight in range(57)
    ]
    obs = {
        "long_k23_certified_flag": int(
            long_k23.get("status") == "SECTOR33_K23_PUNCTURED_MOG_SYZYGY_APERTURE_TARGET_CERTIFIED"
            and long_k23.get("all_checks_pass") is True
        ),
        "support_input_row_count": len(support_rows),
        "kernel_basis_row_count": int(kernel_basis.shape[0]),
        "kernel_basis_column_count": int(kernel_basis.shape[1]),
        "binary_rank": rank,
        "binary_rowspace_word_count": len(rowspace),
        "min_nonzero_weight": nonzero_weights[0] if nonzero_weights else 0,
        "max_weight": max(weight_hist) if weight_hist else 0,
        "weight_one_word_count": int(weight_hist.get(1, 0)),
        "zero_column_count": len(zero_columns),
        "active_column_count": int(kernel_mod2.shape[1] - len(zero_columns)),
        "odd_column_count": sum(1 for value in column_activity.tolist() if int(value) % 2 == 1),
        "even_nonzero_column_count": sum(1 for value in column_activity.tolist() if int(value) > 0 and int(value) % 2 == 0),
        "binary_even_code_flag": int(all(weight % 2 == 0 for weight, count in weight_hist.items() if count)),
        "binary_doubly_even_code_flag": int(all(weight % 4 == 0 for weight, count in weight_hist.items() if count)),
        "quotient_collapse_required_flag": int(weight_hist.get(1, 0) > 0),
        "k23_equality_certified_flag": 0,
        "m23_module_proven_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    matrix_payload = {
        "kernel_mod2": kernel_mod2.astype(np.int64),
        "rref_mod2": rref.astype(np.int64),
        "rowspace_weight_histogram": histogram_vector,
        "column_activity": column_activity.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "long_k23": long_k23,
        "basis_rows": basis_rows,
        "column_rows": column_rows,
        "weight_rows": weight_rows,
        "obs_rows": obs_rows,
        "basis_table": table_from_rows(BASIS_COLUMNS, basis_rows),
        "column_table": table_from_rows(COLUMN_COLUMNS, column_rows),
        "weight_table": table_from_rows(WEIGHT_COLUMNS, weight_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "pivots": pivots,
        "zero_columns": zero_columns,
        "basis_text_hash": hashlib.sha256(digest_text(BASIS_COLUMNS, basis_rows).encode("ascii")).hexdigest(),
        "column_text_hash": hashlib.sha256(digest_text(COLUMN_COLUMNS, column_rows).encode("ascii")).hexdigest(),
        "weight_text_hash": hashlib.sha256(digest_text(WEIGHT_COLUMNS, weight_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "long_k23_input_passes": obs["long_k23_certified_flag"] == 1,
        "binary_rank_preserves_23_rows": (
            obs["kernel_basis_row_count"],
            obs["kernel_basis_column_count"],
            obs["binary_rank"],
            obs["binary_rowspace_word_count"],
        )
        == (23, 56, 23, 8388608),
        "unit_weight_and_inactive_columns_are_explicit": (
            obs["min_nonzero_weight"],
            obs["weight_one_word_count"],
            obs["zero_column_count"],
            obs["active_column_count"],
        )
        == (1, 19, 24, 32),
        "binary_code_is_not_even": (
            obs["binary_even_code_flag"],
            obs["binary_doubly_even_code_flag"],
            obs["quotient_collapse_required_flag"],
        )
        == (0, 0, 1),
        "global_claims_remain_open": (
            obs["k23_equality_certified_flag"],
            obs["m23_module_proven_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (0, 0, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_binary_rowspace_profile",
        "summary": obs,
        "pivots": rows["pivots"],
        "zero_columns": rows["zero_columns"],
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies the GF(2) profile of the emitted K23 basis; it does not certify that this profile is independent of all possible integral kernel bases.",
    }
    seam_payload = {
        "schema": "long.k23bin.seam@1",
        "status": STATUS,
        "claim": "The emitted K23 basis has full binary rank 23, but its GF(2) rowspace contains 19 unit words and leaves 24 support columns inactive.",
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
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23bin.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23bin certifies the GF(2) rowspace profile of the emitted K23 basis.",
        "stage_protocol": {
            "draft": "read long_k23, K23 kernel matrices, and sector33 support rows",
            "witness": "emit binary basis rows, support-column activity rows, full weight histogram rows, observables, and matrix payloads",
            "coherence": "check GF(2) rank 23, 8,388,608 rowspace words, 19 unit words, and 24 inactive support columns",
            "closure": "certify the emitted-basis binary profile while keeping quotient and basis-independence claims open",
            "emit": "write long_k23bin artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "basis_rows_csv": relpath(OUT_DIR / "basis_rows.csv"),
            "column_rows_csv": relpath(OUT_DIR / "column_rows.csv"),
            "weight_rows_csv": relpath(OUT_DIR / "weight_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23bin_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the emitted K23 kernel basis has GF(2) rank 23",
                "the emitted-basis binary rowspace has 8,388,608 words",
                "the emitted-basis binary rowspace has 19 weight-one words",
                "24 of the 56 support columns are inactive in the emitted-basis GF(2) profile",
                "any useful W24-directed quotient must collapse or combine these unit directions",
            ],
            "does_not_certify": [
                "basis-independence over all possible integral K23 lattice bases",
                "a selected non-coordinate quotient map from the 56 support coordinates to W24",
                "rowspan(K23) equals the W24/Euler-punctured syzygy rowspace",
                "an M23 module action on K23",
                "a rebuild of d20.json or broad bundle closure",
            ],
        },
        "next_highest_yield_item": "Use the 19 unit words and 24 inactive columns to build a bounded quotient family, then test whether any quotient image has W24 rank, minimum weight, and containment.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23bin.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23bin.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "basis_csv": csv_text(BASIS_COLUMNS, rows["basis_rows"]),
        "column_csv": csv_text(COLUMN_COLUMNS, rows["column_rows"]),
        "weight_csv": csv_text(WEIGHT_COLUMNS, rows["weight_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "basis_table": rows["basis_table"],
        "column_table": rows["column_table"],
        "weight_table": rows["weight_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "basis_text_sha256": rows["basis_text_hash"],
            "column_text_sha256": rows["column_text_hash"],
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
    (OUT_DIR / "basis_rows.csv").write_text(payloads["basis_csv"], encoding="utf-8")
    (OUT_DIR / "column_rows.csv").write_text(payloads["column_csv"], encoding="utf-8")
    (OUT_DIR / "weight_rows.csv").write_text(payloads["weight_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        basis_table=payloads["basis_table"],
        column_table=payloads["column_table"],
        weight_table=payloads["weight_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23bin_matrices.npz", **payloads["matrix_payload"])
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
