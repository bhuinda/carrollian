from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
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


THEOREM_ID = "long_k23cl"
STATUS = "SECTOR33_K23_MULTIPLICATION_CLOSURE60_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PRIME = 1_000_003

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23cl.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23cl.py"
LONG_K23MUL_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23mul" / "report.json"
LONG_K23RH_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23rh" / "k23rh_matrices.npz"
LONG_HCSUPP_REPORT = D20_INVARIANTS / "proof_obligations" / "long_hcsupp" / "report.json"
LONG_HCSUPP_SUPPORT = D20_INVARIANTS / "proof_obligations" / "long_hcsupp" / "support_rows.csv"
RELATION_MEMBERSHIPS = ROOT / "data" / "raw" / "relation_memberships.npz"
RAW_TENSOR = ROOT / "data" / "raw" / "Halloween.npz"

CLOSURE_TEXT_HASH = "3990f894b05ad2cedae335a422c2cfa06cff04c5259f7cbc5417f1c9a3a29540"
PRODUCT_TEXT_HASH = "184185b044d75e307b312aad85ca457fc980088f975470cb42cb0f351509176e"
PAIR_TEXT_HASH = "9a4875bac97143ec7c1e73ddf601ae08e865902149a0ed45b39aead821f35110"
EXTENSION_TEXT_HASH = "bb874662e35ef1899d969236ffd45b9a54d8cc9506ad896f8ec3ec6f1c7078cf"
OBS_TEXT_HASH = "7dc226c44364995c5f6050656b41fec7bd49b3f93c8934bd8add6ae6957d76e5"
MATRIX_SHA256 = "8bb04b74d39b6ebec161c1b9375e41a90130bcff5fb5776b32c4f358feb5995b"

CLOSURE_COLUMNS = [
    "closure_row_id",
    "relation_id",
    "original_support_flag",
    "added_by_leak_flag",
    "block_i",
    "block_j",
    "rep0",
    "rep1",
    "rep2",
    "rep3",
    "rep4",
]
PRODUCT_COLUMNS = [
    "product_row_id",
    "left_closure_row",
    "right_closure_row",
    "target_closure_row",
    "left_relation_id",
    "right_relation_id",
    "target_relation_id",
    "coefficient",
]
PAIR_COLUMNS = [
    "pair_row_id",
    "left_closure_row",
    "right_closure_row",
    "product_row_count",
    "coefficient_total",
]
EXTENSION_COLUMNS = [
    "generator_id",
    "identity_extension_residual_nonzero_count",
    "identity_extension_preserved_flag",
    "identity_extension_nonzero_count",
    "identity_extension_nonidentity_count",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_k23mul_certified_flag",
    "long_hcsupp_certified_flag",
    "original_support_row_count",
    "added_relation_count",
    "closure_support_row_count",
    "first_leak_target_count",
    "raw_product_row_count",
    "inside_closure_product_row_count",
    "outside_closure_product_row_count",
    "raw_product_coefficient_total",
    "projected_product_tensor_nonzero_count",
    "support_pair_count",
    "nonzero_pair_count",
    "zero_pair_count",
    "closed_pair_count",
    "leaking_pair_count",
    "closure_product_closed_flag",
    "current_r_hc_action_dimension",
    "closure_action_dimension",
    "missing_new_relation_action_count",
    "identity_extension_tested_flag",
    "identity_extension_preserving_generator_count",
    "identity_extension_residual_nonzero_total",
    "identity_extension_residual_nonzero_min",
    "identity_extension_residual_nonzero_max",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = [
        "closure_product_tensor",
        "r_hc_lifts",
        "identity_extension_residual_vector",
        "observable_vector",
    ]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def support_product_profile(triples: np.ndarray, relation_ids: list[int]) -> tuple[np.ndarray, np.ndarray]:
    mask = np.isin(triples[:, 0], relation_ids) & np.isin(triples[:, 1], relation_ids)
    return triples[mask], mask


def build_rows() -> dict[str, Any]:
    long_k23mul = load_json(LONG_K23MUL_REPORT)
    long_hcsupp = load_json(LONG_HCSUPP_REPORT)
    base_support_rows = [{key: int(value) for key, value in row.items()} for row in read_csv_rows(LONG_HCSUPP_SUPPORT)]
    base_relations = [row["relation_id"] for row in base_support_rows]
    base_set = set(base_relations)
    with np.load(RAW_TENSOR, allow_pickle=False) as tensor:
        triples = np.asarray(tensor["triples"], dtype=np.int64)
    base_products, _base_mask = support_product_profile(triples, base_relations)
    first_leaks = sorted({int(row[2]) for row in base_products if int(row[2]) not in base_set})
    closure_relations = base_relations + [relation_id for relation_id in first_leaks if relation_id not in base_set]
    closure_index = {relation_id: index for index, relation_id in enumerate(closure_relations)}
    closure_set = set(closure_relations)

    with np.load(RELATION_MEMBERSHIPS, allow_pickle=False) as memberships:
        block_i = np.asarray(memberships["block_i"], dtype=np.int64)
        block_j = np.asarray(memberships["block_j"], dtype=np.int64)
        reps = np.asarray(memberships["reps"], dtype=np.int64)
    closure_rows = []
    for row_id, relation_id in enumerate(closure_relations):
        closure_rows.append(
            {
                "closure_row_id": row_id,
                "relation_id": relation_id,
                "original_support_flag": int(relation_id in base_set),
                "added_by_leak_flag": int(relation_id in first_leaks),
                "block_i": int(block_i[relation_id]),
                "block_j": int(block_j[relation_id]),
                "rep0": int(reps[relation_id, 0]),
                "rep1": int(reps[relation_id, 1]),
                "rep2": int(reps[relation_id, 2]),
                "rep3": int(reps[relation_id, 3]),
                "rep4": int(reps[relation_id, 4]),
            }
        )

    closure_products, _closure_mask = support_product_profile(triples, closure_relations)
    product_rows = []
    pair_accumulator: dict[tuple[int, int], dict[str, int]] = defaultdict(
        lambda: {"product_row_count": 0, "coefficient_total": 0}
    )
    product_tensor = np.zeros((len(closure_relations), len(closure_relations), len(closure_relations)), dtype=np.int64)
    outside_count = 0
    for product_row_id, (left_relation, right_relation, target_relation, coefficient) in enumerate(closure_products.tolist()):
        left_row = closure_index[int(left_relation)]
        right_row = closure_index[int(right_relation)]
        target_row = closure_index.get(int(target_relation), -1)
        outside_count += int(target_row < 0)
        if target_row >= 0:
            product_tensor[target_row, left_row, right_row] = (
                product_tensor[target_row, left_row, right_row] + int(coefficient)
            ) % PRIME
        product_rows.append(
            {
                "product_row_id": product_row_id,
                "left_closure_row": left_row,
                "right_closure_row": right_row,
                "target_closure_row": target_row,
                "left_relation_id": int(left_relation),
                "right_relation_id": int(right_relation),
                "target_relation_id": int(target_relation),
                "coefficient": int(coefficient),
            }
        )
        pair = pair_accumulator[(left_row, right_row)]
        pair["product_row_count"] += 1
        pair["coefficient_total"] += int(coefficient)
    pair_rows = []
    for pair_row_id, ((left_row, right_row), counts) in enumerate(sorted(pair_accumulator.items())):
        pair_rows.append(
            {
                "pair_row_id": pair_row_id,
                "left_closure_row": left_row,
                "right_closure_row": right_row,
                "product_row_count": counts["product_row_count"],
                "coefficient_total": counts["coefficient_total"],
            }
        )

    with np.load(LONG_K23RH_MATRICES, allow_pickle=False) as matrices:
        r_hc_lifts = np.asarray(matrices["r_hc_lifts"], dtype=np.int64) % PRIME
    extension_rows = []
    residual_counts = []
    identity60 = np.eye(len(closure_relations), dtype=np.int64)
    for generator_id, lift56 in enumerate(r_hc_lifts):
        extended = identity60.copy()
        extended[: lift56.shape[0], : lift56.shape[1]] = lift56
        lhs = np.einsum("kl,lij->kij", extended, product_tensor, optimize=True) % PRIME
        rhs = np.empty_like(product_tensor)
        for target_row in range(len(closure_relations)):
            rhs[target_row] = (extended.T @ product_tensor[target_row] @ extended) % PRIME
        residual_count = int(np.count_nonzero((lhs - rhs) % PRIME))
        residual_counts.append(residual_count)
        extension_rows.append(
            {
                "generator_id": generator_id,
                "identity_extension_residual_nonzero_count": residual_count,
                "identity_extension_preserved_flag": int(residual_count == 0),
                "identity_extension_nonzero_count": int(np.count_nonzero(extended)),
                "identity_extension_nonidentity_count": int(np.count_nonzero((extended - identity60) % PRIME)),
            }
        )

    obs = {
        "long_k23mul_certified_flag": int(
            long_k23mul.get("status") == "SECTOR33_K23_RHC_PROJECTED_PRODUCT_OBSTRUCTION_CERTIFIED"
            and long_k23mul.get("all_checks_pass") is True
        ),
        "long_hcsupp_certified_flag": int(
            long_hcsupp.get("status") == "LONG_HCSUPP_PROFILE_CERTIFIED"
            and long_hcsupp.get("all_checks_pass") is True
        ),
        "original_support_row_count": len(base_relations),
        "added_relation_count": len(first_leaks),
        "closure_support_row_count": len(closure_relations),
        "first_leak_target_count": len(first_leaks),
        "raw_product_row_count": len(product_rows),
        "inside_closure_product_row_count": len(product_rows) - outside_count,
        "outside_closure_product_row_count": outside_count,
        "raw_product_coefficient_total": int(sum(row["coefficient"] for row in product_rows)),
        "projected_product_tensor_nonzero_count": int(np.count_nonzero(product_tensor)),
        "support_pair_count": len(closure_relations) * len(closure_relations),
        "nonzero_pair_count": len(pair_rows),
        "zero_pair_count": len(closure_relations) * len(closure_relations) - len(pair_rows),
        "closed_pair_count": len(pair_rows) if outside_count == 0 else 0,
        "leaking_pair_count": 0 if outside_count == 0 else -1,
        "closure_product_closed_flag": int(outside_count == 0),
        "current_r_hc_action_dimension": int(r_hc_lifts.shape[1]),
        "closure_action_dimension": len(closure_relations),
        "missing_new_relation_action_count": len(closure_relations) - int(r_hc_lifts.shape[1]),
        "identity_extension_tested_flag": 1,
        "identity_extension_preserving_generator_count": sum(int(row["identity_extension_preserved_flag"]) for row in extension_rows),
        "identity_extension_residual_nonzero_total": sum(residual_counts),
        "identity_extension_residual_nonzero_min": min(residual_counts),
        "identity_extension_residual_nonzero_max": max(residual_counts),
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    matrix_payload = {
        "closure_product_tensor": product_tensor.astype(np.int64),
        "r_hc_lifts": r_hc_lifts.astype(np.int64),
        "identity_extension_residual_vector": np.asarray(residual_counts, dtype=np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "long_k23mul": long_k23mul,
        "long_hcsupp": long_hcsupp,
        "closure_rows": closure_rows,
        "product_rows": product_rows,
        "pair_rows": pair_rows,
        "extension_rows": extension_rows,
        "obs_rows": obs_rows,
        "closure_table": table_from_rows(CLOSURE_COLUMNS, closure_rows),
        "product_table": table_from_rows(PRODUCT_COLUMNS, product_rows),
        "pair_table": table_from_rows(PAIR_COLUMNS, pair_rows),
        "extension_table": table_from_rows(EXTENSION_COLUMNS, extension_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "closure_text_hash": hashlib.sha256(digest_text(CLOSURE_COLUMNS, closure_rows).encode("ascii")).hexdigest(),
        "product_text_hash": hashlib.sha256(digest_text(PRODUCT_COLUMNS, product_rows).encode("ascii")).hexdigest(),
        "pair_text_hash": hashlib.sha256(digest_text(PAIR_COLUMNS, pair_rows).encode("ascii")).hexdigest(),
        "extension_text_hash": hashlib.sha256(digest_text(EXTENSION_COLUMNS, extension_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": (
            obs["long_k23mul_certified_flag"],
            obs["long_hcsupp_certified_flag"],
        )
        == (1, 1),
        "closure_support_profile_matches": (
            obs["original_support_row_count"],
            obs["added_relation_count"],
            obs["closure_support_row_count"],
            obs["first_leak_target_count"],
        )
        == (56, 4, 60, 4),
        "closure_product_profile_matches": (
            obs["raw_product_row_count"],
            obs["inside_closure_product_row_count"],
            obs["outside_closure_product_row_count"],
            obs["raw_product_coefficient_total"],
            obs["projected_product_tensor_nonzero_count"],
            obs["closure_product_closed_flag"],
        )
        == (6579, 6579, 0, 14336, 6579, 1),
        "pair_profile_matches": (
            obs["support_pair_count"],
            obs["nonzero_pair_count"],
            obs["zero_pair_count"],
            obs["closed_pair_count"],
            obs["leaking_pair_count"],
        )
        == (3600, 2192, 1408, 2192, 0),
        "identity_extension_obstruction_matches": (
            obs["current_r_hc_action_dimension"],
            obs["closure_action_dimension"],
            obs["missing_new_relation_action_count"],
            obs["identity_extension_tested_flag"],
            obs["identity_extension_preserving_generator_count"],
            obs["identity_extension_residual_nonzero_total"],
            obs["identity_extension_residual_nonzero_min"],
            obs["identity_extension_residual_nonzero_max"],
        )
        == (56, 60, 4, 1, 0, 944444, 82229, 128750),
        "boundary_flags_match": obs["complete_goal_claim_flag"] == 0,
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_multiplication_closure60",
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "added_relations": [row["relation_id"] for row in rows["closure_rows"] if row["added_by_leak_flag"]],
        "boundary": "This certifies the 60-relation raw multiplication closure obtained by adjoining the four leaked target relations to the original 56 support rows.",
    }
    seam_payload = {
        "schema": "long.k23cl.seam@1",
        "status": STATUS,
        "claim": "Adjoining the four leaked target relations closes the raw support product at 60 relations; the current 56-dimensional R_hc action has no materialized action on the four added rows, and its identity extension does not preserve the closed product.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23mul": input_entry(
            LONG_K23MUL_REPORT,
            {
                "status": rows["long_k23mul"].get("status"),
                "certificate_sha256": rows["long_k23mul"].get("certificate_sha256"),
            },
        ),
        "long_k23rh_matrices": input_entry(LONG_K23RH_MATRICES),
        "long_hcsupp": input_entry(
            LONG_HCSUPP_REPORT,
            {
                "status": rows["long_hcsupp"].get("status"),
                "certificate_sha256": rows["long_hcsupp"].get("certificate_sha256"),
            },
        ),
        "long_hcsupp_support": input_entry(LONG_HCSUPP_SUPPORT),
        "relation_memberships": input_entry(RELATION_MEMBERSHIPS),
        "raw_tensor": input_entry(RAW_TENSOR),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23cl.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23cl certifies the 60-relation multiplication closure of the sector33 K23 support surface.",
        "stage_protocol": {
            "draft": "read long_k23mul, the 56 support rows, raw relation memberships, raw multiplication tensor, and R_hc lifts",
            "witness": "emit 60 closure rows, closed product rows, pair rows, identity-extension residual rows, observables, and matrices",
            "coherence": "check leaked relation set, closure product rows, pair counts, zero outside leakage, and identity-extension residuals",
            "closure": "certify the 60-row multiplication closure while keeping the missing four-row R_hc action open",
            "emit": "write long_k23cl artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "closure_rows_csv": relpath(OUT_DIR / "closure_rows.csv"),
            "product_rows_csv": relpath(OUT_DIR / "product_rows.csv"),
            "pair_rows_csv": relpath(OUT_DIR / "pair_rows.csv"),
            "extension_rows_csv": relpath(OUT_DIR / "extension_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23cl_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the first leaked target relation set is exactly 151, 152, 153, 154",
                "adjoining those four rows gives a 60-relation support surface",
                "raw multiplication of the 60-relation surface has 6,579 product rows and zero outside-support target rows",
                "the 60-relation product has 2,192 nonzero support pairs and 1,408 zero pairs",
                "the identity extension of the current 56-dimensional R_hc lifts to the four new rows does not preserve the 60-relation product",
            ],
            "does_not_certify": [
                "a nontrivial R_hc action on the four added relation rows",
                "existence or nonexistence of a 60x60 R_hc-compatible product automorphism",
                "that the 60-relation surface is the final physical/operator carrier",
                "broad bundle integration",
                "a final broad-goal closure claim",
            ],
        },
        "next_highest_yield_item": "Solve for a 60x60 extension of the R_hc action on the four added relations and test whether any extension preserves the now-closed 60-relation multiplication surface.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23cl.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23cl.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "closure_csv": csv_text(CLOSURE_COLUMNS, rows["closure_rows"]),
        "product_csv": csv_text(PRODUCT_COLUMNS, rows["product_rows"]),
        "pair_csv": csv_text(PAIR_COLUMNS, rows["pair_rows"]),
        "extension_csv": csv_text(EXTENSION_COLUMNS, rows["extension_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "closure_table": rows["closure_table"],
        "product_table": rows["product_table"],
        "pair_table": rows["pair_table"],
        "extension_table": rows["extension_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "closure_text_sha256": rows["closure_text_hash"],
            "product_text_sha256": rows["product_text_hash"],
            "pair_text_sha256": rows["pair_text_hash"],
            "extension_text_sha256": rows["extension_text_hash"],
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
    (OUT_DIR / "closure_rows.csv").write_text(payloads["closure_csv"], encoding="utf-8")
    (OUT_DIR / "product_rows.csv").write_text(payloads["product_csv"], encoding="utf-8")
    (OUT_DIR / "pair_rows.csv").write_text(payloads["pair_csv"], encoding="utf-8")
    (OUT_DIR / "extension_rows.csv").write_text(payloads["extension_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        closure_table=payloads["closure_table"],
        product_table=payloads["product_table"],
        pair_table=payloads["pair_table"],
        extension_table=payloads["extension_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23cl_matrices.npz", **payloads["matrix_payload"])
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
