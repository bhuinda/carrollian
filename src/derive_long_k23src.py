from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from .derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .generate_source import build_source_code
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from generate_source import build_source_code
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_k23src"
STATUS = "SECTOR33_K23_SOURCE_W24_RANK12_EXTENSION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23src.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23src.py"
SOURCE_SCRIPT = ROOT / "src" / "generate_source.py"
LONG_K23MERGE_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23merge" / "report.json"
LONG_K23MERGE_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23merge" / "k23merge_matrices.npz"
LONG_RM13MAP_REPORT = D20_INVARIANTS / "proof_obligations" / "long_rm13map" / "report.json"
LONG_RM13MAP_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_rm13map" / "rm13map_matrices.npz"
W24_REPORT = D20_INVARIANTS / "proof_obligations" / "d20_w24_hexacode_row_alphabetization" / "report.json"
W24_ARTIFACT = ROOT / "generated" / "d20_w24_hexacode_row_alphabetization.json"

EXTENSION_TEXT_HASH = "089ca7bbcf06717dcf5534724978a26fd98622fbbfc9849ab0e9b4e97c896de0"
BASIS_TEXT_HASH = "3866b4f6ed247b94ea326b737a9ecdb2daa5d13574a81c8ff7952710a3726fc9"
OBS_TEXT_HASH = "625e1d71ed0b74e5d06218c4b4dbe144586321cd033c39320f2b3ea3e9d221fa"
MATRIX_SHA256 = "09341c36a2422f45b747303f5fcc5938d521d7dc2a4837d98eea394cdf90a575"

EXTENSION_COLUMNS = [
    "k23_basis_row_id",
    "original_target_mask",
    "original_source_mask",
    "extension_source_mask",
    "extension_source_weight",
    "fixed_original_nonzero_flag",
    "added_extension_flag",
    "source_endpoint_member_flag",
    "extension_target_mask",
    "target_w24_member_flag",
]
BASIS_COLUMNS = [
    "basis_row_id",
    "k23_basis_row_id",
    "source_mask",
    "source_weight",
    "target_mask",
    "target_weight",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_k23merge_certified_flag",
    "long_rm13map_certified_flag",
    "external_w24_certified_flag",
    "source_endpoint_word_count",
    "target_w24_word_count",
    "original_image_row_count",
    "original_nonzero_image_row_count",
    "original_source_image_rank",
    "fixed_original_nonzero_row_count",
    "added_extension_row_count",
    "extension_row_count",
    "extension_nonzero_row_count",
    "extension_source_member_row_count",
    "extension_target_member_row_count",
    "extension_source_rank",
    "extension_target_rank",
    "extension_rowspace_word_count",
    "extension_rowspace_equals_source_endpoint_flag",
    "extension_target_rowspace_equals_w24_flag",
    "support_binding_certified_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def vector_mask(vector: tuple[int, ...]) -> int:
    mask = 0
    for index, value in enumerate(vector):
        if int(value):
            mask |= 1 << index
    return mask


def span_from_basis_masks(basis_masks: list[int]) -> set[int]:
    span = {0}
    for mask in basis_masks:
        span |= {word ^ int(mask) for word in list(span)}
    return span


def build_w24_code(artifact: dict[str, Any]) -> set[int]:
    return span_from_basis_masks([int(mask) for mask in artifact["golay_code"]["generator_basis_masks"]])


def row_mask(row: np.ndarray) -> int:
    mask = 0
    for index, value in enumerate(np.asarray(row, dtype=np.uint8).tolist()):
        if int(value) & 1:
            mask |= 1 << index
    return mask


def gf2_rank(masks: list[int]) -> int:
    basis: dict[int, int] = {}
    rank = 0
    for mask in masks:
        value = int(mask)
        while value:
            pivot = value.bit_length() - 1
            if pivot in basis:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                rank += 1
                break
    return rank


def map_mask(mask: int, permutation: list[int]) -> int:
    out = 0
    for source_coord, target_coord in enumerate(permutation):
        if (int(mask) >> source_coord) & 1:
            out |= 1 << target_coord
    return out


def preimage_mask(mask: int, permutation: list[int]) -> int:
    out = 0
    for source_coord, target_coord in enumerate(permutation):
        if (int(mask) >> target_coord) & 1:
            out |= 1 << source_coord
    return out


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = [
        "original_source_images",
        "extension_source_images",
        "extension_target_images",
        "basis_source_masks",
        "basis_target_masks",
        "observable_vector",
    ]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def extend_source_images(original_source_rows: list[int], source_code: set[int]) -> tuple[list[int], list[int]]:
    fixed_rows = [row_id for row_id, mask in enumerate(original_source_rows) if int(mask) != 0]
    extension_rows = list(original_source_rows)
    current_basis = [int(original_source_rows[row_id]) for row_id in fixed_rows]
    chosen_basis_rows = list(fixed_rows)
    open_rows = [row_id for row_id, mask in enumerate(original_source_rows) if int(mask) == 0]
    open_index = 0
    for word in sorted(source_code):
        if int(word) == 0:
            continue
        if gf2_rank(current_basis + [int(word)]) <= gf2_rank(current_basis):
            continue
        if open_index >= len(open_rows):
            raise ValueError("not enough open K23 basis rows to extend source image")
        row_id = open_rows[open_index]
        open_index += 1
        extension_rows[row_id] = int(word)
        current_basis.append(int(word))
        chosen_basis_rows.append(row_id)
        if gf2_rank(current_basis) == 12:
            break
    if gf2_rank(current_basis) != 12:
        raise ValueError("source extension did not reach rank 12")
    return extension_rows, chosen_basis_rows


def build_rows() -> dict[str, Any]:
    long_k23merge = load_json(LONG_K23MERGE_REPORT)
    long_rm13map = load_json(LONG_RM13MAP_REPORT)
    w24_report = load_json(W24_REPORT)
    w24_artifact = load_json(W24_ARTIFACT)
    source_code = {vector_mask(vector) for vector in build_source_code()["G24"]}
    target_code = build_w24_code(w24_artifact)
    with np.load(LONG_K23MERGE_MATRICES, allow_pickle=False) as matrices:
        image_generators = np.asarray(matrices["image_generators"], dtype=np.int64)
    with np.load(LONG_RM13MAP_MATRICES, allow_pickle=False) as matrices:
        permutation = np.asarray(matrices["permutation_vector"], dtype=np.int64).tolist()
    original_target_rows = [row_mask(row) for row in image_generators]
    original_source_rows = [preimage_mask(mask, permutation) for mask in original_target_rows]
    extension_source_rows, basis_row_ids = extend_source_images(original_source_rows, source_code)
    extension_target_rows = [map_mask(mask, permutation) for mask in extension_source_rows]
    extension_rows = []
    basis_ids = set(basis_row_ids)
    fixed_original_rows = {row_id for row_id, mask in enumerate(original_source_rows) if int(mask) != 0}
    for row_id, source_mask in enumerate(extension_source_rows):
        extension_rows.append(
            {
                "k23_basis_row_id": row_id,
                "original_target_mask": int(original_target_rows[row_id]),
                "original_source_mask": int(original_source_rows[row_id]),
                "extension_source_mask": int(source_mask),
                "extension_source_weight": int(source_mask).bit_count(),
                "fixed_original_nonzero_flag": int(row_id in fixed_original_rows),
                "added_extension_flag": int(row_id in basis_ids and row_id not in fixed_original_rows),
                "source_endpoint_member_flag": int(int(source_mask) in source_code),
                "extension_target_mask": int(extension_target_rows[row_id]),
                "target_w24_member_flag": int(int(extension_target_rows[row_id]) in target_code),
            }
        )
    basis_rows = [
        {
            "basis_row_id": basis_id,
            "k23_basis_row_id": row_id,
            "source_mask": int(extension_source_rows[row_id]),
            "source_weight": int(extension_source_rows[row_id]).bit_count(),
            "target_mask": int(extension_target_rows[row_id]),
            "target_weight": int(extension_target_rows[row_id]).bit_count(),
        }
        for basis_id, row_id in enumerate(basis_row_ids)
    ]
    extension_rowspace = span_from_basis_masks(extension_source_rows)
    target_rowspace = span_from_basis_masks(extension_target_rows)
    obs = {
        "long_k23merge_certified_flag": int(
            long_k23merge.get("status") == "SECTOR33_K23_ACTIVE_MERGE_W24_RANK2_SUBCODE_CERTIFIED"
            and long_k23merge.get("all_checks_pass") is True
        ),
        "long_rm13map_certified_flag": int(
            long_rm13map.get("status") == "RM13_SOURCE_TO_W24_COORDINATE_MAP_CERTIFIED"
            and long_rm13map.get("all_checks_pass") is True
        ),
        "external_w24_certified_flag": int(
            w24_report.get("status") == "D20_W24_HEXACODE_ROW_ALPHABETIZATION_CERTIFIED"
            and w24_report.get("all_checks_pass") is True
        ),
        "source_endpoint_word_count": len(source_code),
        "target_w24_word_count": len(target_code),
        "original_image_row_count": len(original_source_rows),
        "original_nonzero_image_row_count": sum(1 for mask in original_source_rows if int(mask) != 0),
        "original_source_image_rank": gf2_rank(original_source_rows),
        "fixed_original_nonzero_row_count": len(fixed_original_rows),
        "added_extension_row_count": sum(row["added_extension_flag"] for row in extension_rows),
        "extension_row_count": len(extension_source_rows),
        "extension_nonzero_row_count": sum(1 for mask in extension_source_rows if int(mask) != 0),
        "extension_source_member_row_count": sum(row["source_endpoint_member_flag"] for row in extension_rows),
        "extension_target_member_row_count": sum(row["target_w24_member_flag"] for row in extension_rows),
        "extension_source_rank": gf2_rank(extension_source_rows),
        "extension_target_rank": gf2_rank(extension_target_rows),
        "extension_rowspace_word_count": len(extension_rowspace),
        "extension_rowspace_equals_source_endpoint_flag": int(extension_rowspace == source_code),
        "extension_target_rowspace_equals_w24_flag": int(target_rowspace == target_code),
        "support_binding_certified_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    matrix_payload = {
        "original_source_images": np.asarray(original_source_rows, dtype=np.int64),
        "extension_source_images": np.asarray(extension_source_rows, dtype=np.int64),
        "extension_target_images": np.asarray(extension_target_rows, dtype=np.int64),
        "basis_source_masks": np.asarray([row["source_mask"] for row in basis_rows], dtype=np.int64),
        "basis_target_masks": np.asarray([row["target_mask"] for row in basis_rows], dtype=np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "long_k23merge": long_k23merge,
        "long_rm13map": long_rm13map,
        "w24_report": w24_report,
        "w24_artifact": w24_artifact,
        "extension_rows": extension_rows,
        "basis_rows": basis_rows,
        "obs_rows": obs_rows,
        "extension_table": table_from_rows(EXTENSION_COLUMNS, extension_rows),
        "basis_table": table_from_rows(BASIS_COLUMNS, basis_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "fixed_row_ids": sorted(fixed_original_rows),
        "basis_row_ids": basis_row_ids,
        "extension_text_hash": hashlib.sha256(digest_text(EXTENSION_COLUMNS, extension_rows).encode("ascii")).hexdigest(),
        "basis_text_hash": hashlib.sha256(digest_text(BASIS_COLUMNS, basis_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": (
            obs["long_k23merge_certified_flag"],
            obs["long_rm13map_certified_flag"],
            obs["external_w24_certified_flag"],
        )
        == (1, 1, 1),
        "original_rank2_image_is_preserved": (
            obs["original_image_row_count"],
            obs["original_nonzero_image_row_count"],
            obs["original_source_image_rank"],
            obs["fixed_original_nonzero_row_count"],
        )
        == (23, 2, 2, 2),
        "extension_has_expected_shape": (
            obs["added_extension_row_count"],
            obs["extension_row_count"],
            obs["extension_nonzero_row_count"],
            obs["extension_source_member_row_count"],
            obs["extension_target_member_row_count"],
        )
        == (10, 23, 12, 23, 23),
        "extension_generates_source_and_target_codes": (
            obs["source_endpoint_word_count"],
            obs["target_w24_word_count"],
            obs["extension_source_rank"],
            obs["extension_target_rank"],
            obs["extension_rowspace_word_count"],
            obs["extension_rowspace_equals_source_endpoint_flag"],
            obs["extension_target_rowspace_equals_w24_flag"],
        )
        == (4096, 4096, 12, 12, 4096, 1, 1),
        "support_binding_remains_open": (
            obs["support_binding_certified_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (0, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_source_w24_rank12_extension",
        "summary": obs,
        "fixed_row_ids": rows["fixed_row_ids"],
        "basis_row_ids": rows["basis_row_ids"],
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies a source-code row assignment extending the transported K23 rank-2 image to a rank-12 endpoint code; it is not yet a support-coordinate binding map.",
    }
    seam_payload = {
        "schema": "long.k23src.seam@1",
        "status": STATUS,
        "claim": "The transported nonzero K23 image rows extend to a rank-12 source endpoint image, so the current obstruction is the missing support-coordinate binding rather than the source code itself.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23merge": input_entry(
            LONG_K23MERGE_REPORT,
            {
                "status": rows["long_k23merge"].get("status"),
                "certificate_sha256": rows["long_k23merge"].get("certificate_sha256"),
            },
        ),
        "long_k23merge_matrices": input_entry(LONG_K23MERGE_MATRICES),
        "long_rm13map": input_entry(
            LONG_RM13MAP_REPORT,
            {
                "status": rows["long_rm13map"].get("status"),
                "certificate_sha256": rows["long_rm13map"].get("certificate_sha256"),
            },
        ),
        "long_rm13map_matrices": input_entry(LONG_RM13MAP_MATRICES),
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
        "source_constructor": input_entry(SOURCE_SCRIPT),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23src.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23src certifies that the RM13-transported K23 rank-2 image extends to a rank-12 source endpoint row assignment, while leaving support binding open.",
        "stage_protocol": {
            "draft": "read long_k23merge, long_rm13map, source constructor, and W24 target artifacts",
            "witness": "emit K23 extension rows, selected basis rows, observables, and source/target image matrices",
            "coherence": "check fixed rank-2 image preservation, source/target code membership, rank 12, and rowspace equality",
            "closure": "certify source-side extension and keep support-coordinate binding explicitly open",
            "emit": "write long_k23src artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "extension_rows_csv": relpath(OUT_DIR / "extension_rows.csv"),
            "basis_rows_csv": relpath(OUT_DIR / "basis_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23src_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the two nonzero transported K23 image rows are preserved",
                "ten additional K23 basis rows can be assigned source endpoint words",
                "the resulting 23-row source assignment has rank 12",
                "the assignment spans the full source endpoint code and remaps onto the current W24 target",
            ],
            "does_not_certify": [
                "that the assignment is induced by the 56 sector33 support coordinates",
                "rowspan(K23) equals the W24/Euler-punctured syzygy rowspace",
                "an M23 module action on K23",
                "a rebuild of d20.json or broad bundle closure",
            ],
        },
        "next_highest_yield_item": "Use the rank-12 source assignment as the target for a 56-support binding solver: search for a column map from sector33 support coordinates whose K23 row images reproduce these source-code rows.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23src.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23src.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "extension_csv": csv_text(EXTENSION_COLUMNS, rows["extension_rows"]),
        "basis_csv": csv_text(BASIS_COLUMNS, rows["basis_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "extension_table": rows["extension_table"],
        "basis_table": rows["basis_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "extension_text_sha256": rows["extension_text_hash"],
            "basis_text_sha256": rows["basis_text_hash"],
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
    (OUT_DIR / "extension_rows.csv").write_text(payloads["extension_csv"], encoding="utf-8")
    (OUT_DIR / "basis_rows.csv").write_text(payloads["basis_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        extension_table=payloads["extension_table"],
        basis_table=payloads["basis_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23src_matrices.npz", **payloads["matrix_payload"])
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
