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


THEOREM_ID = "long_k23op"
STATUS = "SECTOR33_K23_RHC_DENSE_SUPPORT_OBSTRUCTION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PRIME = 1_000_003

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23op.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23op.py"
LONG_K23RH_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23rh" / "report.json"
LONG_K23RH_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23rh" / "k23rh_matrices.npz"
LONG_HCSUPP_REPORT = D20_INVARIANTS / "proof_obligations" / "long_hcsupp" / "report.json"
LONG_HCSUPP_SUPPORT = D20_INVARIANTS / "proof_obligations" / "long_hcsupp" / "support_rows.csv"
LONG_HCPERM_REPORT = D20_INVARIANTS / "proof_obligations" / "long_hcperm" / "report.json"

GENERATOR_TEXT_HASH = "5dda4f09c0ca1960ab0a70d2e50e49e3d7db16f18957a0a09c2510af2b4360e3"
GRADE_TEXT_HASH = "b9bcee53cd32dc6254299b966e0b4fd88ea26ed9a1105d4c25aa5864ab572832"
OBS_TEXT_HASH = "2f40482a793556bd5f51cd7693fab35c67f7d81ac31c89291111eaa80fbab343"
MATRIX_SHA256 = "ae53f2c8e66631190e120bbd2928bf9aba3ed8eef5e3e44d0eb4c35a70d0f48a"

FAMILIES = [
    ("block_i", 0),
    ("rep4", 1),
    ("sign", 2),
    ("abs_coeff", 3),
    ("block_rep4", 4),
]
GENERATOR_COLUMNS = [
    "generator_id",
    "source_lift_nonzero_count",
    "source_lift_nonidentity_count",
    "source_lift_rank",
    "row_nonzero_min",
    "row_nonzero_max",
    "column_nonzero_min",
    "column_nonzero_max",
    "row_singleton_count",
    "column_singleton_count",
    "signed_unit_entry_count",
    "nonunit_entry_count",
    "distinct_nonzero_value_count",
    "signed_monomial_flag",
    "dense_support_obstruction_flag",
]
GRADE_COLUMNS = [
    "generator_id",
    "family_id",
    "family_code",
    "label_count",
    "inside_nonzero_count",
    "leak_nonzero_count",
    "leak_label_count",
    "preserved_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_k23rh_certified_flag",
    "long_hcsupp_certified_flag",
    "long_hcperm_certified_flag",
    "support_row_count",
    "generator_count",
    "grading_family_count",
    "generator_row_count",
    "grade_row_count",
    "signed_monomial_generator_count",
    "dense_obstruction_generator_count",
    "total_nonzero_count",
    "total_nonidentity_count",
    "row_singleton_total",
    "column_singleton_total",
    "signed_unit_entry_total",
    "nonunit_entry_total",
    "max_row_nonzero_count",
    "max_column_nonzero_count",
    "block_i_total_leak_nonzero_count",
    "rep4_total_leak_nonzero_count",
    "sign_total_leak_nonzero_count",
    "abs_coeff_total_leak_nonzero_count",
    "block_rep4_total_leak_nonzero_count",
    "all_gradings_preserved_generator_count",
    "signed_operation_support_obstruction_flag",
    "multiplication_preservation_tested_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def rank_mod(matrix: np.ndarray, prime: int = PRIME) -> int:
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


def family_labels(row: dict[str, int]) -> dict[str, int]:
    sign = 1 if int(row["coefficient_signed"]) > 0 else -1
    return {
        "block_i": int(row["block_i"]),
        "rep4": int(row["rep4"]),
        "sign": sign,
        "abs_coeff": abs(int(row["coefficient_signed"])),
        "block_rep4": int(row["block_i"]) * 100 + int(row["rep4"]),
    }


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = [
        "r_hc_lifts",
        "family_label_matrix",
        "generator_table",
        "grade_table",
        "observable_vector",
    ]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def build_rows() -> dict[str, Any]:
    long_k23rh = load_json(LONG_K23RH_REPORT)
    long_hcsupp = load_json(LONG_HCSUPP_REPORT)
    long_hcperm = load_json(LONG_HCPERM_REPORT)
    support_rows = [{key: int(value) for key, value in row.items()} for row in read_csv_rows(LONG_HCSUPP_SUPPORT)]
    with np.load(LONG_K23RH_MATRICES, allow_pickle=False) as matrices:
        r_hc_lifts = np.asarray(matrices["r_hc_lifts"], dtype=np.int64) % PRIME

    label_vectors: dict[str, list[int]] = {
        family_name: [family_labels(row)[family_name] for row in support_rows]
        for family_name, _family_id in FAMILIES
    }
    family_label_matrix = np.asarray([label_vectors[family_name] for family_name, _family_id in FAMILIES], dtype=np.int64)
    generator_rows = []
    grade_rows = []
    identity = np.eye(r_hc_lifts.shape[1], dtype=np.int64)
    for generator_id, operator in enumerate(r_hc_lifts):
        row_nonzero = np.count_nonzero(operator, axis=1)
        column_nonzero = np.count_nonzero(operator, axis=0)
        nonzero_values = operator[operator != 0]
        signed_unit_count = int(np.count_nonzero(np.isin(nonzero_values, [1, PRIME - 1])))
        nonunit_count = int(nonzero_values.size - signed_unit_count)
        signed_monomial = (
            int(np.min(row_nonzero)) == 1
            and int(np.max(row_nonzero)) == 1
            and int(np.min(column_nonzero)) == 1
            and int(np.max(column_nonzero)) == 1
            and nonunit_count == 0
        )
        generator_rows.append(
            {
                "generator_id": generator_id,
                "source_lift_nonzero_count": int(np.count_nonzero(operator)),
                "source_lift_nonidentity_count": int(np.count_nonzero((operator - identity) % PRIME)),
                "source_lift_rank": rank_mod(operator),
                "row_nonzero_min": int(np.min(row_nonzero)),
                "row_nonzero_max": int(np.max(row_nonzero)),
                "column_nonzero_min": int(np.min(column_nonzero)),
                "column_nonzero_max": int(np.max(column_nonzero)),
                "row_singleton_count": int(np.count_nonzero(row_nonzero == 1)),
                "column_singleton_count": int(np.count_nonzero(column_nonzero == 1)),
                "signed_unit_entry_count": signed_unit_count,
                "nonunit_entry_count": nonunit_count,
                "distinct_nonzero_value_count": len({int(value) for value in nonzero_values.tolist()}),
                "signed_monomial_flag": int(signed_monomial),
                "dense_support_obstruction_flag": int(not signed_monomial),
            }
        )
        for family_name, family_id in FAMILIES:
            labels = label_vectors[family_name]
            values = sorted(set(labels))
            inside_nonzero = 0
            leak_nonzero = 0
            leak_label_count = 0
            for value in values:
                inside = [index for index, label in enumerate(labels) if label == value]
                outside = [index for index, label in enumerate(labels) if label != value]
                inside_count = int(np.count_nonzero(operator[np.ix_(inside, inside)]))
                leak_count = int(np.count_nonzero(operator[np.ix_(inside, outside)]))
                inside_nonzero += inside_count
                leak_nonzero += leak_count
                leak_label_count += int(leak_count > 0)
            grade_rows.append(
                {
                    "generator_id": generator_id,
                    "family_id": family_id,
                    "family_code": family_id,
                    "label_count": len(values),
                    "inside_nonzero_count": inside_nonzero,
                    "leak_nonzero_count": leak_nonzero,
                    "leak_label_count": leak_label_count,
                    "preserved_flag": int(leak_nonzero == 0),
                }
            )

    grade_by_family = {
        family_name: [row for row in grade_rows if int(row["family_id"]) == family_id]
        for family_name, family_id in FAMILIES
    }
    obs = {
        "long_k23rh_certified_flag": int(
            long_k23rh.get("status") == "SECTOR33_K23_RHC_SOURCE_LIFT_CERTIFIED"
            and long_k23rh.get("all_checks_pass") is True
        ),
        "long_hcsupp_certified_flag": int(
            long_hcsupp.get("status") == "LONG_HCSUPP_PROFILE_CERTIFIED"
            and long_hcsupp.get("all_checks_pass") is True
        ),
        "long_hcperm_certified_flag": int(
            long_hcperm.get("status") == "LONG_HCPERM_SIGNED_COLUMN_LIFT_OBSTRUCTION_CERTIFIED"
            and long_hcperm.get("all_checks_pass") is True
        ),
        "support_row_count": len(support_rows),
        "generator_count": int(r_hc_lifts.shape[0]),
        "grading_family_count": len(FAMILIES),
        "generator_row_count": len(generator_rows),
        "grade_row_count": len(grade_rows),
        "signed_monomial_generator_count": sum(int(row["signed_monomial_flag"]) for row in generator_rows),
        "dense_obstruction_generator_count": sum(int(row["dense_support_obstruction_flag"]) for row in generator_rows),
        "total_nonzero_count": sum(int(row["source_lift_nonzero_count"]) for row in generator_rows),
        "total_nonidentity_count": sum(int(row["source_lift_nonidentity_count"]) for row in generator_rows),
        "row_singleton_total": sum(int(row["row_singleton_count"]) for row in generator_rows),
        "column_singleton_total": sum(int(row["column_singleton_count"]) for row in generator_rows),
        "signed_unit_entry_total": sum(int(row["signed_unit_entry_count"]) for row in generator_rows),
        "nonunit_entry_total": sum(int(row["nonunit_entry_count"]) for row in generator_rows),
        "max_row_nonzero_count": max(int(row["row_nonzero_max"]) for row in generator_rows),
        "max_column_nonzero_count": max(int(row["column_nonzero_max"]) for row in generator_rows),
        "block_i_total_leak_nonzero_count": sum(int(row["leak_nonzero_count"]) for row in grade_by_family["block_i"]),
        "rep4_total_leak_nonzero_count": sum(int(row["leak_nonzero_count"]) for row in grade_by_family["rep4"]),
        "sign_total_leak_nonzero_count": sum(int(row["leak_nonzero_count"]) for row in grade_by_family["sign"]),
        "abs_coeff_total_leak_nonzero_count": sum(int(row["leak_nonzero_count"]) for row in grade_by_family["abs_coeff"]),
        "block_rep4_total_leak_nonzero_count": sum(int(row["leak_nonzero_count"]) for row in grade_by_family["block_rep4"]),
        "all_gradings_preserved_generator_count": sum(
            int(all(row["preserved_flag"] for row in grade_rows if int(row["generator_id"]) == generator_id))
            for generator_id in range(int(r_hc_lifts.shape[0]))
        ),
        "signed_operation_support_obstruction_flag": int(all(int(row["dense_support_obstruction_flag"]) for row in generator_rows)),
        "multiplication_preservation_tested_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    matrix_payload = {
        "r_hc_lifts": r_hc_lifts.astype(np.int64),
        "family_label_matrix": family_label_matrix.astype(np.int64),
        "generator_table": table_from_rows(GENERATOR_COLUMNS, generator_rows),
        "grade_table": table_from_rows(GRADE_COLUMNS, grade_rows),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "long_k23rh": long_k23rh,
        "long_hcsupp": long_hcsupp,
        "long_hcperm": long_hcperm,
        "generator_rows": generator_rows,
        "grade_rows": grade_rows,
        "obs_rows": obs_rows,
        "generator_table": table_from_rows(GENERATOR_COLUMNS, generator_rows),
        "grade_table": table_from_rows(GRADE_COLUMNS, grade_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "generator_text_hash": hashlib.sha256(digest_text(GENERATOR_COLUMNS, generator_rows).encode("ascii")).hexdigest(),
        "grade_text_hash": hashlib.sha256(digest_text(GRADE_COLUMNS, grade_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": (
            obs["long_k23rh_certified_flag"],
            obs["long_hcsupp_certified_flag"],
            obs["long_hcperm_certified_flag"],
        )
        == (1, 1, 1),
        "shape_matches": (
            obs["support_row_count"],
            obs["generator_count"],
            obs["grading_family_count"],
            obs["generator_row_count"],
            obs["grade_row_count"],
        )
        == (56, 9, 5, 9, 45),
        "dense_obstruction_matches": (
            obs["signed_monomial_generator_count"],
            obs["dense_obstruction_generator_count"],
            obs["total_nonzero_count"],
            obs["total_nonidentity_count"],
            obs["nonunit_entry_total"],
        )
        == (0, 9, 5508, 5288, 3047),
        "grading_leak_profile_matches": (
            obs["block_i_total_leak_nonzero_count"],
            obs["rep4_total_leak_nonzero_count"],
            obs["sign_total_leak_nonzero_count"],
            obs["abs_coeff_total_leak_nonzero_count"],
            obs["block_rep4_total_leak_nonzero_count"],
            obs["all_gradings_preserved_generator_count"],
        )
        == (787, 3526, 2557, 2066, 3745, 0),
        "boundary_flags_match": (
            obs["signed_operation_support_obstruction_flag"],
            obs["multiplication_preservation_tested_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (1, 0, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_rhc_dense_support_obstruction",
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies that the materialized R_hc lifts are dense prime-field operators, not signed row-support operations on the 56 certified support rows.",
    }
    seam_payload = {
        "schema": "long.k23op.seam@1",
        "status": STATUS,
        "claim": "The candidate-projection R_hc lifts satisfy the quotient equation but fail the finite signed support-operation test on the 56 support rows.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23rh": input_entry(
            LONG_K23RH_REPORT,
            {
                "status": rows["long_k23rh"].get("status"),
                "certificate_sha256": rows["long_k23rh"].get("certificate_sha256"),
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
        "long_hcperm": input_entry(
            LONG_HCPERM_REPORT,
            {
                "status": rows["long_hcperm"].get("status"),
                "certificate_sha256": rows["long_hcperm"].get("certificate_sha256"),
            },
        ),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23op.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23op certifies the dense support-operation obstruction for the materialized R_hc lift family.",
        "stage_protocol": {
            "draft": "read long_k23rh lift matrices, long_hcsupp support rows, and long_hcperm signed-lift obstruction",
            "witness": "emit per-generator density rows, support-grading leak rows, observables, and matrices",
            "coherence": "check signed-monomial failure, exact density totals, and support-grading leakage totals",
            "closure": "certify dense signed-support obstruction without claiming multiplication nonpreservation",
            "emit": "write long_k23op artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "generator_rows_csv": relpath(OUT_DIR / "generator_rows.csv"),
            "grade_rows_csv": relpath(OUT_DIR / "grade_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23op_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "none of the nine materialized R_hc lifts is signed-monomial on the 56 support rows",
                "all nine lifts have dense-support obstruction under the current row-support operation test",
                "the lift family has 5,508 nonzero entries and 3,047 non-unit nonzero entries across nine generators",
                "the lift family leaks across the certified block_i, rep4, sign, absolute-coefficient, and block/rep4 support gradings",
                "the prior signed-column lift obstruction and the new dense lift are consistent: the target action lifts linearly, but not as a signed finite support operation",
            ],
            "does_not_certify": [
                "failure of every possible non-dense source-side lift",
                "failure of every projection outside the current center-grade candidate",
                "multiplication-structure nonpreservation",
                "a raw A985 action or homomorphism on the 56 support rows",
                "broad bundle integration",
                "a final broad-goal closure claim",
            ],
        },
        "next_highest_yield_item": "Move from row-support obstruction to multiplication: build the induced 56-support product/projection algebra needed to test whether any R_hc-compatible lift preserves the finite multiplication surface.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23op.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23op.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "generator_csv": csv_text(GENERATOR_COLUMNS, rows["generator_rows"]),
        "grade_csv": csv_text(GRADE_COLUMNS, rows["grade_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "generator_table": rows["generator_table"],
        "grade_table": rows["grade_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "generator_text_sha256": rows["generator_text_hash"],
            "grade_text_sha256": rows["grade_text_hash"],
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
    (OUT_DIR / "generator_rows.csv").write_text(payloads["generator_csv"], encoding="utf-8")
    (OUT_DIR / "grade_rows.csv").write_text(payloads["grade_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        generator_table=payloads["generator_table"],
        grade_table=payloads["grade_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23op_matrices.npz", **payloads["matrix_payload"])
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
