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


THEOREM_ID = "long_k23mul"
STATUS = "SECTOR33_K23_RHC_PROJECTED_PRODUCT_OBSTRUCTION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PRIME = 1_000_003

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23mul.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23mul.py"
LONG_K23OP_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23op" / "report.json"
LONG_K23RH_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23rh" / "k23rh_matrices.npz"
LONG_HCSUPP_REPORT = D20_INVARIANTS / "proof_obligations" / "long_hcsupp" / "report.json"
LONG_HCSUPP_SUPPORT = D20_INVARIANTS / "proof_obligations" / "long_hcsupp" / "support_rows.csv"
RAW_TENSOR = ROOT / "data" / "raw" / "Halloween.npz"

PRODUCT_TEXT_HASH = "9e85ad8a3e3890d8f347c1dc7d77c1981fca5f1d361cdb6d96501593f01dd4b7"
PAIR_TEXT_HASH = "44438544129c3b384611667314c8264e7732fcef9d7b8efc7785634c052972bd"
GENERATOR_TEXT_HASH = "6aa9544bf38a2e0a41b402edc4003a0586be68f5a03039bb487e9a887737c905"
OBS_TEXT_HASH = "aee26d48af024c09a18545652e26a7b7ed46e11ac66df5d7df8f6e2a7d2d7ca3"
MATRIX_SHA256 = "74980542cf3d6a8734371ab006efdec59eacfdef7ea45927907c133e3e212c5d"

PRODUCT_COLUMNS = [
    "product_row_id",
    "left_support_row",
    "right_support_row",
    "left_relation_id",
    "right_relation_id",
    "target_relation_id",
    "target_support_row",
    "inside_support_flag",
    "coefficient",
]
PAIR_COLUMNS = [
    "pair_row_id",
    "left_support_row",
    "right_support_row",
    "product_row_count",
    "inside_product_row_count",
    "outside_product_row_count",
    "coefficient_total",
]
GENERATOR_COLUMNS = [
    "generator_id",
    "projected_product_residual_nonzero_count",
    "projected_product_preserved_flag",
    "source_lift_nonzero_count",
    "source_lift_nonidentity_count",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_k23op_certified_flag",
    "long_hcsupp_certified_flag",
    "support_row_count",
    "support_pair_count",
    "nonzero_pair_count",
    "zero_pair_count",
    "closed_pair_count",
    "leaking_pair_count",
    "raw_support_product_row_count",
    "inside_support_product_row_count",
    "outside_support_product_row_count",
    "raw_support_product_coefficient_total",
    "inside_support_product_coefficient_total",
    "outside_support_product_coefficient_total",
    "projected_product_tensor_nonzero_count",
    "support_product_closed_flag",
    "generator_count",
    "projected_product_preserving_generator_count",
    "projected_product_residual_nonzero_total",
    "projected_product_residual_nonzero_min",
    "projected_product_residual_nonzero_max",
    "projected_product_obstruction_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = [
        "projected_product_tensor",
        "r_hc_lifts",
        "generator_residual_vector",
        "observable_vector",
    ]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def build_rows() -> dict[str, Any]:
    long_k23op = load_json(LONG_K23OP_REPORT)
    long_hcsupp = load_json(LONG_HCSUPP_REPORT)
    support_rows = [{key: int(value) for key, value in row.items()} for row in read_csv_rows(LONG_HCSUPP_SUPPORT)]
    support_relations = [row["relation_id"] for row in support_rows]
    support_index = {relation_id: index for index, relation_id in enumerate(support_relations)}
    support_set = set(support_relations)
    with np.load(RAW_TENSOR, allow_pickle=False) as tensor:
        triples = np.asarray(tensor["triples"], dtype=np.int64)
    with np.load(LONG_K23RH_MATRICES, allow_pickle=False) as matrices:
        r_hc_lifts = np.asarray(matrices["r_hc_lifts"], dtype=np.int64) % PRIME

    mask = np.isin(triples[:, 0], support_relations) & np.isin(triples[:, 1], support_relations)
    support_products = triples[mask]
    product_rows = []
    pair_accumulator: dict[tuple[int, int], dict[str, int]] = defaultdict(
        lambda: {
            "product_row_count": 0,
            "inside_product_row_count": 0,
            "outside_product_row_count": 0,
            "coefficient_total": 0,
        }
    )
    projected_product = np.zeros((len(support_rows), len(support_rows), len(support_rows)), dtype=np.int64)
    inside_coeff = 0
    outside_coeff = 0
    for product_row_id, (left_relation, right_relation, target_relation, coefficient) in enumerate(support_products.tolist()):
        left_row = support_index[int(left_relation)]
        right_row = support_index[int(right_relation)]
        target_row = support_index.get(int(target_relation), -1)
        inside_flag = int(target_row >= 0)
        product_rows.append(
            {
                "product_row_id": product_row_id,
                "left_support_row": left_row,
                "right_support_row": right_row,
                "left_relation_id": int(left_relation),
                "right_relation_id": int(right_relation),
                "target_relation_id": int(target_relation),
                "target_support_row": target_row,
                "inside_support_flag": inside_flag,
                "coefficient": int(coefficient),
            }
        )
        pair = pair_accumulator[(left_row, right_row)]
        pair["product_row_count"] += 1
        pair["inside_product_row_count"] += inside_flag
        pair["outside_product_row_count"] += int(not inside_flag)
        pair["coefficient_total"] += int(coefficient)
        if inside_flag:
            inside_coeff += int(coefficient)
            projected_product[target_row, left_row, right_row] = (
                projected_product[target_row, left_row, right_row] + int(coefficient)
            ) % PRIME
        else:
            outside_coeff += int(coefficient)

    pair_rows = []
    for pair_row_id, ((left_row, right_row), counts) in enumerate(sorted(pair_accumulator.items())):
        pair_rows.append(
            {
                "pair_row_id": pair_row_id,
                "left_support_row": left_row,
                "right_support_row": right_row,
                "product_row_count": counts["product_row_count"],
                "inside_product_row_count": counts["inside_product_row_count"],
                "outside_product_row_count": counts["outside_product_row_count"],
                "coefficient_total": counts["coefficient_total"],
            }
        )

    identity = np.eye(len(support_rows), dtype=np.int64)
    generator_rows = []
    residual_counts = []
    for generator_id, operator in enumerate(r_hc_lifts):
        lhs = np.einsum("kl,lij->kij", operator, projected_product, optimize=True) % PRIME
        rhs = np.empty_like(projected_product)
        for target_row in range(len(support_rows)):
            rhs[target_row] = (operator.T @ projected_product[target_row] @ operator) % PRIME
        residual_count = int(np.count_nonzero((lhs - rhs) % PRIME))
        residual_counts.append(residual_count)
        generator_rows.append(
            {
                "generator_id": generator_id,
                "projected_product_residual_nonzero_count": residual_count,
                "projected_product_preserved_flag": int(residual_count == 0),
                "source_lift_nonzero_count": int(np.count_nonzero(operator)),
                "source_lift_nonidentity_count": int(np.count_nonzero((operator - identity) % PRIME)),
            }
        )

    outside_rows = sum(int(row["inside_support_flag"] == 0) for row in product_rows)
    obs = {
        "long_k23op_certified_flag": int(
            long_k23op.get("status") == "SECTOR33_K23_RHC_DENSE_SUPPORT_OBSTRUCTION_CERTIFIED"
            and long_k23op.get("all_checks_pass") is True
        ),
        "long_hcsupp_certified_flag": int(
            long_hcsupp.get("status") == "LONG_HCSUPP_PROFILE_CERTIFIED"
            and long_hcsupp.get("all_checks_pass") is True
        ),
        "support_row_count": len(support_rows),
        "support_pair_count": len(support_rows) * len(support_rows),
        "nonzero_pair_count": len(pair_rows),
        "zero_pair_count": len(support_rows) * len(support_rows) - len(pair_rows),
        "closed_pair_count": sum(int(row["outside_product_row_count"] == 0) for row in pair_rows),
        "leaking_pair_count": sum(int(row["outside_product_row_count"] > 0) for row in pair_rows),
        "raw_support_product_row_count": len(product_rows),
        "inside_support_product_row_count": len(product_rows) - outside_rows,
        "outside_support_product_row_count": outside_rows,
        "raw_support_product_coefficient_total": int(sum(row["coefficient"] for row in product_rows)),
        "inside_support_product_coefficient_total": int(inside_coeff),
        "outside_support_product_coefficient_total": int(outside_coeff),
        "projected_product_tensor_nonzero_count": int(np.count_nonzero(projected_product)),
        "support_product_closed_flag": int(outside_rows == 0),
        "generator_count": int(r_hc_lifts.shape[0]),
        "projected_product_preserving_generator_count": sum(
            int(row["projected_product_preserved_flag"]) for row in generator_rows
        ),
        "projected_product_residual_nonzero_total": sum(residual_counts),
        "projected_product_residual_nonzero_min": min(residual_counts),
        "projected_product_residual_nonzero_max": max(residual_counts),
        "projected_product_obstruction_flag": int(all(count > 0 for count in residual_counts)),
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    matrix_payload = {
        "projected_product_tensor": projected_product.astype(np.int64),
        "r_hc_lifts": r_hc_lifts.astype(np.int64),
        "generator_residual_vector": np.asarray(residual_counts, dtype=np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "long_k23op": long_k23op,
        "long_hcsupp": long_hcsupp,
        "product_rows": product_rows,
        "pair_rows": pair_rows,
        "generator_rows": generator_rows,
        "obs_rows": obs_rows,
        "product_table": table_from_rows(PRODUCT_COLUMNS, product_rows),
        "pair_table": table_from_rows(PAIR_COLUMNS, pair_rows),
        "generator_table": table_from_rows(GENERATOR_COLUMNS, generator_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "product_text_hash": hashlib.sha256(digest_text(PRODUCT_COLUMNS, product_rows).encode("ascii")).hexdigest(),
        "pair_text_hash": hashlib.sha256(digest_text(PAIR_COLUMNS, pair_rows).encode("ascii")).hexdigest(),
        "generator_text_hash": hashlib.sha256(digest_text(GENERATOR_COLUMNS, generator_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": (
            obs["long_k23op_certified_flag"],
            obs["long_hcsupp_certified_flag"],
        )
        == (1, 1),
        "raw_support_product_profile_matches": (
            obs["support_row_count"],
            obs["support_pair_count"],
            obs["nonzero_pair_count"],
            obs["zero_pair_count"],
            obs["raw_support_product_row_count"],
            obs["inside_support_product_row_count"],
            obs["outside_support_product_row_count"],
        )
        == (56, 3136, 2080, 1056, 6272, 6204, 68),
        "raw_support_product_leak_matches": (
            obs["closed_pair_count"],
            obs["leaking_pair_count"],
            obs["raw_support_product_coefficient_total"],
            obs["inside_support_product_coefficient_total"],
            obs["outside_support_product_coefficient_total"],
            obs["support_product_closed_flag"],
        )
        == (2020, 60, 11976, 11872, 104, 0),
        "projected_product_obstruction_matches": (
            obs["projected_product_tensor_nonzero_count"],
            obs["generator_count"],
            obs["projected_product_preserving_generator_count"],
            obs["projected_product_residual_nonzero_total"],
            obs["projected_product_residual_nonzero_min"],
            obs["projected_product_residual_nonzero_max"],
            obs["projected_product_obstruction_flag"],
        )
        == (6204, 9, 0, 936661, 81629, 127386, 1),
        "boundary_flags_match": obs["complete_goal_claim_flag"] == 0,
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_rhc_projected_product_obstruction",
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies the raw 56-support multiplication leak and shows that the materialized R_hc lifts do not preserve the projected 56-support product.",
    }
    seam_payload = {
        "schema": "long.k23mul.seam@1",
        "status": STATUS,
        "claim": "The 56 support relation span is not closed under raw multiplication, and the projected support product is not preserved by any of the nine materialized R_hc lifts.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23op": input_entry(
            LONG_K23OP_REPORT,
            {
                "status": rows["long_k23op"].get("status"),
                "certificate_sha256": rows["long_k23op"].get("certificate_sha256"),
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
        "raw_tensor": input_entry(RAW_TENSOR),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23mul.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23mul certifies that the materialized R_hc lifts fail the current projected 56-support multiplication surface.",
        "stage_protocol": {
            "draft": "read long_k23op, the 56 support rows, R_hc lift matrices, and the raw multiplication tensor",
            "witness": "emit raw support product rows, pair closure rows, generator residual rows, observables, and projected product matrices",
            "coherence": "check support closure counts, product leakage, projected tensor size, and R_hc projected-product residuals",
            "closure": "certify the current projected-product obstruction without claiming nonexistence of all possible product-compatible lifts",
            "emit": "write long_k23mul artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "product_rows_csv": relpath(OUT_DIR / "product_rows.csv"),
            "pair_rows_csv": relpath(OUT_DIR / "pair_rows.csv"),
            "generator_rows_csv": relpath(OUT_DIR / "generator_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23mul_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "raw products of the 56 support relations have 6,272 nonzero product rows",
                "68 raw product rows leak outside the 56 support relation set",
                "60 nonzero support-relation pairs have at least one outside-support product row",
                "the projected inside-support product has 6,204 nonzero tensor entries",
                "none of the nine materialized R_hc lifts preserves that projected product",
            ],
            "does_not_certify": [
                "nonexistence of a different R_hc-compatible lift preserving another product surface",
                "nonexistence of a corrected product on a larger closure containing the 68 leaked rows",
                "full raw A985 multiplication preservation or failure for all possible completions",
                "broad bundle integration",
                "a final broad-goal closure claim",
            ],
        },
        "next_highest_yield_item": "Close the 56-support multiplication leak by adjoining the leaked target relations, then retest closure and R_hc compatibility on the enlarged support surface.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23mul.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23mul.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "product_csv": csv_text(PRODUCT_COLUMNS, rows["product_rows"]),
        "pair_csv": csv_text(PAIR_COLUMNS, rows["pair_rows"]),
        "generator_csv": csv_text(GENERATOR_COLUMNS, rows["generator_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "product_table": rows["product_table"],
        "pair_table": rows["pair_table"],
        "generator_table": rows["generator_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "product_text_sha256": rows["product_text_hash"],
            "pair_text_sha256": rows["pair_text_hash"],
            "generator_text_sha256": rows["generator_text_hash"],
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
    (OUT_DIR / "product_rows.csv").write_text(payloads["product_csv"], encoding="utf-8")
    (OUT_DIR / "pair_rows.csv").write_text(payloads["pair_csv"], encoding="utf-8")
    (OUT_DIR / "generator_rows.csv").write_text(payloads["generator_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        product_table=payloads["product_table"],
        pair_table=payloads["pair_table"],
        generator_table=payloads["generator_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23mul_matrices.npz", **payloads["matrix_payload"])
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
