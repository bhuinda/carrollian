from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from .derive_long_k23fam import read_csv_rows
    from .derive_long_k23poly import (
        FINGERPRINT_COLUMNS,
        LONG_K23CL_MATRICES,
        OUT_DIR as LONG_K23POLY_DIR,
        WORD_COLUMNS,
        product_residual_nonzero,
    )
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from derive_long_k23fam import read_csv_rows
    from derive_long_k23poly import (
        FINGERPRINT_COLUMNS,
        LONG_K23CL_MATRICES,
        OUT_DIR as LONG_K23POLY_DIR,
        WORD_COLUMNS,
        product_residual_nonzero,
    )
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_k23rew"
STATUS = "SECTOR33_K23_BOUNDED_REWRITE_FINGERPRINT_OBSTRUCTION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PRIME = 1_000_003

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23rew.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23rew.py"
LONG_K23POLY_REPORT = LONG_K23POLY_DIR / "report.json"
LONG_K23POLY_WORDS = LONG_K23POLY_DIR / "word_rows.csv"
LONG_K23POLY_FINGERPRINTS = LONG_K23POLY_DIR / "fingerprint_rows.csv"
LONG_K23POLY_MATRICES = LONG_K23POLY_DIR / "k23poly_matrices.npz"

CLASS_TEXT_HASH = "4080f92356edfc139ea03c2bdbd69688189f9aabc0995946b3fc621ae8826d07"
MEMBER_TEXT_HASH = "a20b35cd00f77aca29b96648c6dc70c4ac2608f8527ffe7413d91dff235e2cde"
OBS_TEXT_HASH = "8b343031453124072b28f5bf439c5ac9854ebac33b0fba041d6487a9f99c8e2e"
MATRIX_SHA256 = "d9b05cf5df55cb9efddfa5ebb5a3aa8feb09ff3c3b9863f552193ff5e479445e"

CLASS_COLUMNS = [
    "class_id",
    "representative_word_id",
    "class_size",
    "word_length_min",
    "word_length_max",
    "product_residual_nonzero_count",
    "product_preserved_flag",
    "product_preserved_member_count",
    "defective_member_count",
    "mixed_product_flag",
    "closing_rewrite_exists_flag",
    "lift_fingerprint_code",
    "target_fingerprint_code",
    "residual_fingerprint_code",
]
MEMBER_COLUMNS = [
    "member_id",
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
    "long_k23poly_certified_flag",
    "word_count",
    "carrier_class_count",
    "singleton_class_count",
    "pair_class_count",
    "ten_class_count",
    "product_preserved_class_count",
    "defective_class_count",
    "mixed_product_class_count",
    "fingerprint_preserving_closing_rewrite_count",
    "identity_class_size",
    "identity_class_product_residual",
    "defective_word_count",
    "product_preserved_word_count",
    "residual_fingerprint_count",
    "word_depth",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def matrix_sha256(matrix: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(matrix, dtype=np.int64).tobytes()).hexdigest()


def fingerprint_codes(values: list[str]) -> dict[str, int]:
    return {value: index for index, value in enumerate(sorted(set(values)))}


def product_residual_tensor(lift: np.ndarray, product_tensor: np.ndarray) -> np.ndarray:
    lhs = np.einsum("kl,lij->kij", lift, product_tensor, optimize=True) % PRIME
    rhs = np.empty_like(product_tensor)
    for target_row in range(product_tensor.shape[0]):
        rhs[target_row] = (lift.T @ product_tensor[target_row] @ lift) % PRIME
    return (lhs - rhs) % PRIME


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["class_table", "member_table", "observable_vector"]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def build_rows() -> dict[str, Any]:
    long_k23poly = load_json(LONG_K23POLY_REPORT)
    word_rows = [{key: int(value) for key, value in row.items()} for row in read_csv_rows(LONG_K23POLY_WORDS)]
    fingerprint_rows = read_csv_rows(LONG_K23POLY_FINGERPRINTS)
    with np.load(LONG_K23POLY_MATRICES, allow_pickle=False) as matrices:
        generator_lifts = np.asarray(matrices["generator_lifts"], dtype=np.int64) % PRIME
        target_generators = np.asarray(matrices["target_generators"], dtype=np.int64) % PRIME
    with np.load(LONG_K23CL_MATRICES, allow_pickle=False) as matrices:
        product_tensor = np.asarray(matrices["closure_product_tensor"], dtype=np.int64) % PRIME

    fingerprint_by_word: dict[int, dict[int, str]] = defaultdict(dict)
    for row in fingerprint_rows:
        fingerprint_by_word[int(row["word_id"])][int(row["matrix_role_code"])] = row["sha256"]

    lift_hash_values = [row["sha256"] for row in fingerprint_rows if int(row["matrix_role_code"]) == 0]
    target_hash_values = [row["sha256"] for row in fingerprint_rows if int(row["matrix_role_code"]) == 1]
    lift_codes = fingerprint_codes(lift_hash_values)
    target_codes = fingerprint_codes(target_hash_values)

    word_matrix_by_id: dict[int, np.ndarray] = {}
    target_matrix_by_id: dict[int, np.ndarray] = {}
    identity_source = np.eye(generator_lifts.shape[1], dtype=np.int64)
    identity_target = np.eye(target_generators.shape[1], dtype=np.int64)
    for row in word_rows:
        word_id = row["word_id"]
        length = row["word_length"]
        first = row["first_generator_id"]
        second = row["second_generator_id"]
        if length == 0:
            word_matrix_by_id[word_id] = identity_source
            target_matrix_by_id[word_id] = identity_target
        elif length == 1:
            word_matrix_by_id[word_id] = generator_lifts[first]
            target_matrix_by_id[word_id] = target_generators[first]
        else:
            word_matrix_by_id[word_id] = (generator_lifts[second] @ generator_lifts[first]) % PRIME
            target_matrix_by_id[word_id] = (target_generators[second] @ target_generators[first]) % PRIME

    residual_hash_by_word: dict[int, str] = {}
    for row in word_rows:
        word_id = row["word_id"]
        residual = product_residual_tensor(word_matrix_by_id[word_id], product_tensor)
        residual_count = int(np.count_nonzero(residual))
        if residual_count != row["product_residual_nonzero_count"]:
            raise AssertionError(f"product residual count mismatch for word {word_id}")
        if matrix_sha256(word_matrix_by_id[word_id]) != fingerprint_by_word[word_id][0]:
            raise AssertionError(f"source fingerprint mismatch for word {word_id}")
        if matrix_sha256(target_matrix_by_id[word_id]) != fingerprint_by_word[word_id][1]:
            raise AssertionError(f"target fingerprint mismatch for word {word_id}")
        residual_hash_by_word[word_id] = matrix_sha256(residual)

    residual_codes = fingerprint_codes(list(residual_hash_by_word.values()))
    classes: dict[tuple[str, str], list[dict[str, int]]] = defaultdict(list)
    for row in word_rows:
        key = (fingerprint_by_word[row["word_id"]][0], fingerprint_by_word[row["word_id"]][1])
        classes[key].append(row)

    sorted_classes = sorted(classes.items(), key=lambda item: min(row["word_id"] for row in item[1]))
    class_rows = []
    member_rows = []
    member_id = 0
    for class_id, ((lift_hash, target_hash), members) in enumerate(sorted_classes):
        members_sorted = sorted(members, key=lambda row: row["word_id"])
        residual_counts = sorted({row["product_residual_nonzero_count"] for row in members_sorted})
        product_flags = sorted({row["product_preserved_flag"] for row in members_sorted})
        residual_hashes = sorted({residual_hash_by_word[row["word_id"]] for row in members_sorted})
        if len(residual_counts) != 1 or len(residual_hashes) != 1:
            raise AssertionError(f"class {class_id} has inconsistent residual fingerprint")
        product_preserved_member_count = sum(row["product_preserved_flag"] for row in members_sorted)
        class_rows.append(
            {
                "class_id": class_id,
                "representative_word_id": members_sorted[0]["word_id"],
                "class_size": len(members_sorted),
                "word_length_min": min(row["word_length"] for row in members_sorted),
                "word_length_max": max(row["word_length"] for row in members_sorted),
                "product_residual_nonzero_count": residual_counts[0],
                "product_preserved_flag": int(product_flags == [1]),
                "product_preserved_member_count": product_preserved_member_count,
                "defective_member_count": len(members_sorted) - product_preserved_member_count,
                "mixed_product_flag": int(len(product_flags) > 1),
                "closing_rewrite_exists_flag": int(
                    product_preserved_member_count > 0 and product_preserved_member_count < len(members_sorted)
                ),
                "lift_fingerprint_code": lift_codes[lift_hash],
                "target_fingerprint_code": target_codes[target_hash],
                "residual_fingerprint_code": residual_codes[residual_hashes[0]],
            }
        )
        for row in members_sorted:
            member_rows.append(
                {
                    "member_id": member_id,
                    "class_id": class_id,
                    "word_id": row["word_id"],
                    "word_length": row["word_length"],
                    "first_generator_id": row["first_generator_id"],
                    "second_generator_id": row["second_generator_id"],
                    "product_residual_nonzero_count": row["product_residual_nonzero_count"],
                    "product_preserved_flag": row["product_preserved_flag"],
                }
            )
            member_id += 1

    size_counts = defaultdict(int)
    for row in class_rows:
        size_counts[row["class_size"]] += 1
    identity_class = next(row for row in class_rows if row["representative_word_id"] == 0)
    obs = {
        "long_k23poly_certified_flag": int(
            long_k23poly.get("status") == "SECTOR33_K23_CONCATENATIVE_POLYMORPHISM_CARRIER_CERTIFIED"
            and long_k23poly.get("all_checks_pass") is True
        ),
        "word_count": len(word_rows),
        "carrier_class_count": len(class_rows),
        "singleton_class_count": size_counts[1],
        "pair_class_count": size_counts[2],
        "ten_class_count": size_counts[10],
        "product_preserved_class_count": sum(row["product_preserved_flag"] for row in class_rows),
        "defective_class_count": sum(int(row["product_preserved_member_count"] == 0) for row in class_rows),
        "mixed_product_class_count": sum(row["mixed_product_flag"] for row in class_rows),
        "fingerprint_preserving_closing_rewrite_count": sum(row["closing_rewrite_exists_flag"] for row in class_rows),
        "identity_class_size": identity_class["class_size"],
        "identity_class_product_residual": identity_class["product_residual_nonzero_count"],
        "defective_word_count": sum(int(row["product_preserved_flag"] == 0) for row in word_rows),
        "product_preserved_word_count": sum(row["product_preserved_flag"] for row in word_rows),
        "residual_fingerprint_count": len(residual_codes),
        "word_depth": max(row["word_length"] for row in word_rows),
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    class_table = table_from_rows(CLASS_COLUMNS, class_rows)
    member_table = table_from_rows(MEMBER_COLUMNS, member_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "class_table": class_table.astype(np.int64),
        "member_table": member_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "long_k23poly": long_k23poly,
        "class_rows": class_rows,
        "member_rows": member_rows,
        "obs_rows": obs_rows,
        "class_table": class_table,
        "member_table": member_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "class_text_hash": hashlib.sha256(digest_text(CLASS_COLUMNS, class_rows).encode("ascii")).hexdigest(),
        "member_text_hash": hashlib.sha256(digest_text(MEMBER_COLUMNS, member_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": obs["long_k23poly_certified_flag"] == 1,
        "rewrite_class_profile_matches": (
            obs["word_count"],
            obs["carrier_class_count"],
            obs["singleton_class_count"],
            obs["pair_class_count"],
            obs["ten_class_count"],
            obs["word_depth"],
        )
        == (91, 56, 29, 26, 1, 2),
        "rewrite_obstruction_matches": (
            obs["product_preserved_class_count"],
            obs["defective_class_count"],
            obs["mixed_product_class_count"],
            obs["fingerprint_preserving_closing_rewrite_count"],
        )
        == (1, 55, 0, 0),
        "identity_class_matches": (
            obs["identity_class_size"],
            obs["identity_class_product_residual"],
            obs["product_preserved_word_count"],
            obs["defective_word_count"],
        )
        == (10, 0, 10, 81),
        "boundary_flags_match": obs["complete_goal_claim_flag"] == 0,
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_bounded_rewrite_fingerprint_obstruction",
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies that depth-two fingerprint-preserving rewrites cannot close any defective product residual without changing the carrier transcript.",
    }
    seam_payload = {
        "schema": "long.k23rew.seam@1",
        "status": STATUS,
        "claim": "The depth-two K23 word carrier has no fingerprint-preserving rewrite class that mixes product-defective and product-clean words.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23poly": input_entry(
            LONG_K23POLY_REPORT,
            {
                "status": rows["long_k23poly"].get("status"),
                "certificate_sha256": rows["long_k23poly"].get("certificate_sha256"),
            },
        ),
        "long_k23poly_words": input_entry(LONG_K23POLY_WORDS),
        "long_k23poly_fingerprints": input_entry(LONG_K23POLY_FINGERPRINTS),
        "long_k23poly_matrices": input_entry(LONG_K23POLY_MATRICES),
        "long_k23cl_matrices": input_entry(LONG_K23CL_MATRICES),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23rew.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23rew certifies the bounded fingerprint-preserving rewrite obstruction.",
        "stage_protocol": {
            "draft": "read long_k23poly word rows, source/target fingerprints, matrices, and closure60 product tensor",
            "witness": "emit carrier fingerprint classes, class memberships, observables, and numeric tables",
            "coherence": "check class-size profile, residual fingerprint consistency, and absence of mixed clean/defective classes",
            "closure": "certify the bounded rewrite obstruction while leaving deeper or transcript-changing rewrites open",
            "emit": "write long_k23rew artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "class_rows_csv": relpath(OUT_DIR / "class_rows.csv"),
            "member_rows_csv": relpath(OUT_DIR / "member_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23rew_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the 91 depth-two words collapse to 56 source/target carrier fingerprint classes",
                "the class-size profile is 29 singleton classes, 26 pair classes, and one 10-word identity class",
                "each carrier fingerprint class has a stable product residual fingerprint",
                "there is one product-clean carrier class and 55 product-defective carrier classes",
                "no carrier fingerprint class mixes product-clean and product-defective words",
                "therefore no depth-two fingerprint-preserving rewrite closes a product defect",
            ],
            "does_not_certify": [
                "rewrite behavior beyond word depth two",
                "rewrites that intentionally change the source or target carrier fingerprint",
                "a quotient by non-fingerprint semantic labels",
                "a computational hardness claim",
                "bundle-wide integration",
                "a final broad-goal closure claim",
            ],
        },
        "next_highest_yield_item": "Promote the obstruction into a commit/open protocol certificate: public transcript is the source/target fingerprint pair plus residual-class code, while operator matrices remain dereferenced by hash.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23rew.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23rew.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "class_csv": csv_text(CLASS_COLUMNS, rows["class_rows"]),
        "member_csv": csv_text(MEMBER_COLUMNS, rows["member_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "class_table": rows["class_table"],
        "member_table": rows["member_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "class_text_sha256": rows["class_text_hash"],
            "member_text_sha256": rows["member_text_hash"],
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
    (OUT_DIR / "class_rows.csv").write_text(payloads["class_csv"], encoding="utf-8")
    (OUT_DIR / "member_rows.csv").write_text(payloads["member_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        class_table=payloads["class_table"],
        member_table=payloads["member_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23rew_matrices.npz", **payloads["matrix_payload"])
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
