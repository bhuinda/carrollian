from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from .derive_long_k23fam import read_csv_rows
    from .derive_long_k23rew import (
        LONG_K23CL_MATRICES,
        LONG_K23POLY_FINGERPRINTS,
        LONG_K23POLY_MATRICES,
        LONG_K23POLY_WORDS,
        OUT_DIR as LONG_K23REW_DIR,
        matrix_sha256,
        product_residual_tensor,
    )
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from derive_long_k23fam import read_csv_rows
    from derive_long_k23rew import (
        LONG_K23CL_MATRICES,
        LONG_K23POLY_FINGERPRINTS,
        LONG_K23POLY_MATRICES,
        LONG_K23POLY_WORDS,
        OUT_DIR as LONG_K23REW_DIR,
        matrix_sha256,
        product_residual_tensor,
    )
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_k23cop"
STATUS = "SECTOR33_K23_COMMIT_OPEN_TRANSCRIPT_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PRIME = 1_000_003

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23cop.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23cop.py"
LONG_K23REW_REPORT = LONG_K23REW_DIR / "report.json"
LONG_K23REW_CLASSES = LONG_K23REW_DIR / "class_rows.csv"
LONG_K23REW_MEMBERS = LONG_K23REW_DIR / "member_rows.csv"

PUBLIC_TEXT_HASH = "1720b36d894d06cd232ccfff38287cb7bae956e7c290abf661cff696a844cc99"
OPENING_TEXT_HASH = "1e4e2e246a8ea0959ad827ab062a6ee79ce1f10cd6e17365572b63ca51933cea"
OBS_TEXT_HASH = "290b0515c55763b9f068e1f0f7655a1928a68dc0f9580b1ce4f5098f8a87e1eb"
MATRIX_SHA256 = "674d1533c8ff056a5c00e7893f7937c81674e490586716de3f7083bc50d68162"

PUBLIC_COLUMNS = [
    "transcript_id",
    "class_id",
    "source_fingerprint",
    "target_fingerprint",
    "residual_class_code",
    "product_preserved_flag",
    "member_word_count",
    "public_digest_sha256",
]
OPENING_COLUMNS = [
    "opening_id",
    "transcript_id",
    "class_id",
    "word_id",
    "word_length",
    "first_generator_id",
    "second_generator_id",
    "source_matrix_sha256",
    "target_matrix_sha256",
    "residual_tensor_sha256",
    "product_residual_nonzero_count",
    "product_preserved_flag",
    "opening_digest_sha256",
]
PUBLIC_NUMERIC_COLUMNS = [
    "transcript_id",
    "class_id",
    "residual_class_code",
    "product_preserved_flag",
    "member_word_count",
]
OPENING_NUMERIC_COLUMNS = [
    "opening_id",
    "transcript_id",
    "class_id",
    "word_id",
    "word_length",
    "first_generator_id",
    "second_generator_id",
    "product_residual_nonzero_count",
    "product_preserved_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_k23rew_certified_flag",
    "public_transcript_count",
    "opening_row_count",
    "public_digest_unique_count",
    "opening_digest_unique_count",
    "source_fingerprint_unique_count",
    "target_fingerprint_unique_count",
    "residual_class_count",
    "clean_public_transcript_count",
    "defective_public_transcript_count",
    "clean_opening_count",
    "defective_opening_count",
    "transcript_opening_mismatch_count",
    "matrix_hash_mismatch_count",
    "product_residual_mismatch_count",
    "public_matrix_entry_column_count",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def digest_public(class_id: int, source_hash: str, target_hash: str, residual_code: int) -> str:
    payload = f"{class_id},{source_hash},{target_hash},{residual_code}\n"
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def digest_opening(
    class_id: int,
    word_id: int,
    source_hash: str,
    target_hash: str,
    residual_hash: str,
) -> str:
    payload = f"{class_id},{word_id},{source_hash},{target_hash},{residual_hash}\n"
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["public_numeric_table", "opening_numeric_table", "observable_vector"]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def build_word_matrices(
    word_rows: list[dict[str, int]],
    generator_lifts: np.ndarray,
    target_generators: np.ndarray,
) -> tuple[dict[int, np.ndarray], dict[int, np.ndarray]]:
    source_by_word: dict[int, np.ndarray] = {}
    target_by_word: dict[int, np.ndarray] = {}
    identity_source = np.eye(generator_lifts.shape[1], dtype=np.int64)
    identity_target = np.eye(target_generators.shape[1], dtype=np.int64)
    for row in word_rows:
        word_id = row["word_id"]
        length = row["word_length"]
        first = row["first_generator_id"]
        second = row["second_generator_id"]
        if length == 0:
            source_by_word[word_id] = identity_source
            target_by_word[word_id] = identity_target
        elif length == 1:
            source_by_word[word_id] = generator_lifts[first]
            target_by_word[word_id] = target_generators[first]
        else:
            source_by_word[word_id] = (generator_lifts[second] @ generator_lifts[first]) % PRIME
            target_by_word[word_id] = (target_generators[second] @ target_generators[first]) % PRIME
    return source_by_word, target_by_word


def build_rows() -> dict[str, Any]:
    long_k23rew = load_json(LONG_K23REW_REPORT)
    class_rows = [{key: int(value) for key, value in row.items()} for row in read_csv_rows(LONG_K23REW_CLASSES)]
    member_rows = [{key: int(value) for key, value in row.items()} for row in read_csv_rows(LONG_K23REW_MEMBERS)]
    word_rows = [{key: int(value) for key, value in row.items()} for row in read_csv_rows(LONG_K23POLY_WORDS)]
    fingerprint_rows = read_csv_rows(LONG_K23POLY_FINGERPRINTS)
    with np.load(LONG_K23POLY_MATRICES, allow_pickle=False) as matrices:
        generator_lifts = np.asarray(matrices["generator_lifts"], dtype=np.int64) % PRIME
        target_generators = np.asarray(matrices["target_generators"], dtype=np.int64) % PRIME
    with np.load(LONG_K23CL_MATRICES, allow_pickle=False) as matrices:
        product_tensor = np.asarray(matrices["closure_product_tensor"], dtype=np.int64) % PRIME

    fingerprints_by_word: dict[int, dict[int, str]] = defaultdict(dict)
    for row in fingerprint_rows:
        fingerprints_by_word[int(row["word_id"])][int(row["matrix_role_code"])] = row["sha256"]
    words_by_id = {row["word_id"]: row for row in word_rows}
    members_by_class: dict[int, list[dict[str, int]]] = defaultdict(list)
    for row in member_rows:
        members_by_class[row["class_id"]].append(row)

    source_by_word, target_by_word = build_word_matrices(word_rows, generator_lifts, target_generators)

    residual_hash_by_word: dict[int, str] = {}
    matrix_hash_mismatch_count = 0
    product_residual_mismatch_count = 0
    for word_id, word in words_by_id.items():
        source_hash = matrix_sha256(source_by_word[word_id])
        target_hash = matrix_sha256(target_by_word[word_id])
        if source_hash != fingerprints_by_word[word_id][0]:
            matrix_hash_mismatch_count += 1
        if target_hash != fingerprints_by_word[word_id][1]:
            matrix_hash_mismatch_count += 1
        residual_tensor = product_residual_tensor(source_by_word[word_id], product_tensor)
        residual_count = int(np.count_nonzero(residual_tensor))
        if residual_count != word["product_residual_nonzero_count"]:
            product_residual_mismatch_count += 1
        residual_hash_by_word[word_id] = matrix_sha256(residual_tensor)

    public_rows = []
    opening_rows = []
    public_numeric_rows = []
    opening_numeric_rows = []
    transcript_opening_mismatch_count = 0
    opening_id = 0
    for transcript_id, class_row in enumerate(sorted(class_rows, key=lambda row: row["class_id"])):
        class_id = class_row["class_id"]
        members = sorted(members_by_class[class_id], key=lambda row: row["word_id"])
        representative_word_id = class_row["representative_word_id"]
        source_hash = fingerprints_by_word[representative_word_id][0]
        target_hash = fingerprints_by_word[representative_word_id][1]
        public_digest = digest_public(
            class_id,
            source_hash,
            target_hash,
            class_row["residual_fingerprint_code"],
        )
        public_rows.append(
            {
                "transcript_id": transcript_id,
                "class_id": class_id,
                "source_fingerprint": source_hash,
                "target_fingerprint": target_hash,
                "residual_class_code": class_row["residual_fingerprint_code"],
                "product_preserved_flag": class_row["product_preserved_flag"],
                "member_word_count": class_row["class_size"],
                "public_digest_sha256": public_digest,
            }
        )
        public_numeric_rows.append(
            {
                "transcript_id": transcript_id,
                "class_id": class_id,
                "residual_class_code": class_row["residual_fingerprint_code"],
                "product_preserved_flag": class_row["product_preserved_flag"],
                "member_word_count": class_row["class_size"],
            }
        )
        for member in members:
            word_id = member["word_id"]
            word = words_by_id[word_id]
            member_source_hash = fingerprints_by_word[word_id][0]
            member_target_hash = fingerprints_by_word[word_id][1]
            if member_source_hash != source_hash or member_target_hash != target_hash:
                transcript_opening_mismatch_count += 1
            residual_hash = residual_hash_by_word[word_id]
            opening_digest = digest_opening(class_id, word_id, member_source_hash, member_target_hash, residual_hash)
            opening_rows.append(
                {
                    "opening_id": opening_id,
                    "transcript_id": transcript_id,
                    "class_id": class_id,
                    "word_id": word_id,
                    "word_length": word["word_length"],
                    "first_generator_id": word["first_generator_id"],
                    "second_generator_id": word["second_generator_id"],
                    "source_matrix_sha256": member_source_hash,
                    "target_matrix_sha256": member_target_hash,
                    "residual_tensor_sha256": residual_hash,
                    "product_residual_nonzero_count": word["product_residual_nonzero_count"],
                    "product_preserved_flag": word["product_preserved_flag"],
                    "opening_digest_sha256": opening_digest,
                }
            )
            opening_numeric_rows.append(
                {
                    "opening_id": opening_id,
                    "transcript_id": transcript_id,
                    "class_id": class_id,
                    "word_id": word_id,
                    "word_length": word["word_length"],
                    "first_generator_id": word["first_generator_id"],
                    "second_generator_id": word["second_generator_id"],
                    "product_residual_nonzero_count": word["product_residual_nonzero_count"],
                    "product_preserved_flag": word["product_preserved_flag"],
                }
            )
            opening_id += 1

    public_matrix_entry_columns = [
        column for column in PUBLIC_COLUMNS if column.endswith("_entry") or column.endswith("_value")
    ]
    obs = {
        "long_k23rew_certified_flag": int(
            long_k23rew.get("status") == "SECTOR33_K23_BOUNDED_REWRITE_FINGERPRINT_OBSTRUCTION_CERTIFIED"
            and long_k23rew.get("all_checks_pass") is True
        ),
        "public_transcript_count": len(public_rows),
        "opening_row_count": len(opening_rows),
        "public_digest_unique_count": len({row["public_digest_sha256"] for row in public_rows}),
        "opening_digest_unique_count": len({row["opening_digest_sha256"] for row in opening_rows}),
        "source_fingerprint_unique_count": len({row["source_fingerprint"] for row in public_rows}),
        "target_fingerprint_unique_count": len({row["target_fingerprint"] for row in public_rows}),
        "residual_class_count": len({row["residual_class_code"] for row in public_rows}),
        "clean_public_transcript_count": sum(row["product_preserved_flag"] for row in public_rows),
        "defective_public_transcript_count": sum(int(row["product_preserved_flag"] == 0) for row in public_rows),
        "clean_opening_count": sum(row["product_preserved_flag"] for row in opening_rows),
        "defective_opening_count": sum(int(row["product_preserved_flag"] == 0) for row in opening_rows),
        "transcript_opening_mismatch_count": transcript_opening_mismatch_count,
        "matrix_hash_mismatch_count": matrix_hash_mismatch_count,
        "product_residual_mismatch_count": product_residual_mismatch_count,
        "public_matrix_entry_column_count": len(public_matrix_entry_columns),
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    public_numeric_table = table_from_rows(PUBLIC_NUMERIC_COLUMNS, public_numeric_rows)
    opening_numeric_table = table_from_rows(OPENING_NUMERIC_COLUMNS, opening_numeric_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "public_numeric_table": public_numeric_table.astype(np.int64),
        "opening_numeric_table": opening_numeric_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "long_k23rew": long_k23rew,
        "public_rows": public_rows,
        "opening_rows": opening_rows,
        "obs_rows": obs_rows,
        "public_numeric_table": public_numeric_table,
        "opening_numeric_table": opening_numeric_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "public_text_hash": hashlib.sha256(digest_text(PUBLIC_COLUMNS, public_rows).encode("ascii")).hexdigest(),
        "opening_text_hash": hashlib.sha256(digest_text(OPENING_COLUMNS, opening_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": obs["long_k23rew_certified_flag"] == 1,
        "protocol_profile_matches": (
            obs["public_transcript_count"],
            obs["opening_row_count"],
            obs["public_digest_unique_count"],
            obs["opening_digest_unique_count"],
            obs["source_fingerprint_unique_count"],
            obs["target_fingerprint_unique_count"],
            obs["residual_class_count"],
        )
        == (56, 91, 56, 91, 56, 56, 56),
        "clean_defective_profile_matches": (
            obs["clean_public_transcript_count"],
            obs["defective_public_transcript_count"],
            obs["clean_opening_count"],
            obs["defective_opening_count"],
        )
        == (1, 55, 10, 81),
        "open_verification_exact": (
            obs["transcript_opening_mismatch_count"],
            obs["matrix_hash_mismatch_count"],
            obs["product_residual_mismatch_count"],
        )
        == (0, 0, 0),
        "public_transcript_has_no_matrix_entries": obs["public_matrix_entry_column_count"] == 0,
        "boundary_flags_match": obs["complete_goal_claim_flag"] == 0,
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_commit_open_transcript",
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies a finite commit/open transcript surface: public rows carry source and target fingerprints plus residual class codes, while open rows dereference word matrices and residual tensors by hash.",
    }
    seam_payload = {
        "schema": "long.k23cop.seam@1",
        "status": STATUS,
        "claim": "The bounded K23 word carrier has a checked public transcript/opening split over the rewrite fingerprint classes.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23rew": input_entry(
            LONG_K23REW_REPORT,
            {
                "status": rows["long_k23rew"].get("status"),
                "certificate_sha256": rows["long_k23rew"].get("certificate_sha256"),
            },
        ),
        "long_k23rew_classes": input_entry(LONG_K23REW_CLASSES),
        "long_k23rew_members": input_entry(LONG_K23REW_MEMBERS),
        "long_k23poly_words": input_entry(LONG_K23POLY_WORDS),
        "long_k23poly_fingerprints": input_entry(LONG_K23POLY_FINGERPRINTS),
        "long_k23poly_matrices": input_entry(LONG_K23POLY_MATRICES),
        "long_k23cl_matrices": input_entry(LONG_K23CL_MATRICES),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23cop.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23cop certifies the K23 commit/open transcript surface.",
        "stage_protocol": {
            "draft": "read long_k23rew classes and memberships plus long_k23poly word fingerprints and matrices",
            "witness": "emit public transcript rows, opening rows, observables, and numeric protocol tables",
            "coherence": "check transcript uniqueness, opening-to-transcript consistency, matrix hash dereferences, and residual counts",
            "closure": "certify the finite transcript/opening split while leaving secrecy and hardness claims open",
            "emit": "write long_k23cop artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "public_transcript_csv": relpath(OUT_DIR / "public_transcript.csv"),
            "opening_rows_csv": relpath(OUT_DIR / "opening_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23cop_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "56 public transcript rows, one for each bounded rewrite fingerprint class",
                "91 opening rows, one for each checked depth-two word",
                "each public transcript digest is unique",
                "each opening digest is unique",
                "each opening row dereferences source, target, and residual objects by hash",
                "every opening row matches exactly one public transcript",
                "the public transcript rows contain fingerprint hashes and residual codes, not matrix entries",
            ],
            "does_not_certify": [
                "hash collision resistance beyond ordinary SHA-256 use",
                "secrecy of repository-visible witness matrices",
                "zero knowledge",
                "soundness beyond the bounded depth-two witness set",
                "bundle-wide integration",
                "a final broad-goal closure claim",
            ],
        },
        "next_highest_yield_item": "Build the verifier-challenge layer: choose transcript classes, open selected rows, and certify deterministic accept/reject rules over the public digest and dereference hashes.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23cop.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23cop.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "public_csv": csv_text(PUBLIC_COLUMNS, rows["public_rows"]),
        "opening_csv": csv_text(OPENING_COLUMNS, rows["opening_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "public_numeric_table": rows["public_numeric_table"],
        "opening_numeric_table": rows["opening_numeric_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "public_text_sha256": rows["public_text_hash"],
            "opening_text_sha256": rows["opening_text_hash"],
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
    (OUT_DIR / "public_transcript.csv").write_text(payloads["public_csv"], encoding="utf-8")
    (OUT_DIR / "opening_rows.csv").write_text(payloads["opening_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        public_numeric_table=payloads["public_numeric_table"],
        opening_numeric_table=payloads["opening_numeric_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23cop_matrices.npz", **payloads["matrix_payload"])
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
