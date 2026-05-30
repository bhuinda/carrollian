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


THEOREM_ID = "long_k23fix"
STATUS = "SECTOR33_K23_FIXED_OLD_MIXED_EXTENSION_OBSTRUCTED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PRIME = 1_000_003

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23fix.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23fix.py"
LONG_K23CL_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23cl" / "report.json"
LONG_K23EXT_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23ext" / "report.json"
LONG_K23CL_CLOSURE_ROWS = D20_INVARIANTS / "proof_obligations" / "long_k23cl" / "closure_rows.csv"
LONG_K23CL_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23cl" / "k23cl_matrices.npz"
LONG_K23RH_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23rh" / "report.json"
LONG_K23RH_MATRICES = D20_INVARIANTS / "proof_obligations" / "long_k23rh" / "k23rh_matrices.npz"

OBSTRUCTION_TEXT_HASH = "d59f339372edd3862998062e51daaca12fc639d922ef869cce532800cf3bc72f"
OBS_TEXT_HASH = "7cac7d80bff507d3792dc18bbd5f06733caac8e0054b879606e931e717ecf860"
MATRIX_SHA256 = "d0b986e4db0e25736c3141c892427a09c41f5d8a092611be17f936428671e741"

OBSTRUCTION_COLUMNS = [
    "generator_id",
    "target_residual_nonzero_count",
    "linear_support_row_count",
    "linear_impossible_row_count",
    "quadratic_target_row_count",
    "exact_support_row_count",
    "exact_impossible_row_count",
    "first_impossible_target_row",
    "first_impossible_left_row",
    "first_impossible_right_row",
    "first_impossible_target_relation",
    "first_impossible_left_relation",
    "first_impossible_right_relation",
    "first_impossible_required_value",
    "fixed_old_extension_possible_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_k23cl_certified_flag",
    "long_k23ext_certified_flag",
    "long_k23rh_certified_flag",
    "generator_count",
    "old_dimension",
    "new_dimension",
    "closure_dimension",
    "old_slice_equation_count",
    "target_residual_nonzero_total",
    "linear_impossible_total",
    "linear_impossible_min",
    "linear_impossible_max",
    "exact_impossible_total",
    "exact_impossible_min",
    "exact_impossible_max",
    "failed_generator_count",
    "fixed_old_extension_obstructed_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["obstruction_table", "observable_vector", "exact_impossible_vector"]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def build_rows() -> dict[str, Any]:
    long_k23cl = load_json(LONG_K23CL_REPORT)
    long_k23ext = load_json(LONG_K23EXT_REPORT)
    long_k23rh = load_json(LONG_K23RH_REPORT)
    closure_rows = [{key: int(value) for key, value in row.items()} for row in read_csv_rows(LONG_K23CL_CLOSURE_ROWS)]
    relation_by_row = {row["closure_row_id"]: row["relation_id"] for row in closure_rows}
    with np.load(LONG_K23CL_MATRICES, allow_pickle=False) as matrices:
        product_tensor = np.asarray(matrices["closure_product_tensor"], dtype=np.int64) % PRIME
    with np.load(LONG_K23RH_MATRICES, allow_pickle=False) as matrices:
        r_hc_lifts = np.asarray(matrices["r_hc_lifts"], dtype=np.int64) % PRIME

    old_dim = int(r_hc_lifts.shape[1])
    new_dim = int(product_tensor.shape[0] - old_dim)
    new_product_to_old_inputs = product_tensor[old_dim:, :old_dim, :old_dim]
    obstruction_rows = []
    target_counts = []
    linear_impossible_counts = []
    exact_impossible_counts = []
    for generator_id, lift in enumerate(r_hc_lifts):
        rhs = np.empty((old_dim, old_dim, old_dim), dtype=np.int64)
        for target_row in range(old_dim):
            rhs[target_row] = (lift.T @ product_tensor[target_row, :old_dim, :old_dim] @ lift) % PRIME
        lhs = np.einsum("kl,lij->kij", lift, product_tensor[:old_dim, :old_dim, :old_dim], optimize=True) % PRIME
        target = (rhs - lhs) % PRIME

        term1 = np.zeros((new_dim, old_dim, old_dim), dtype=np.int64)
        term2 = np.zeros((new_dim, old_dim, old_dim), dtype=np.int64)
        for new_index in range(new_dim):
            new_row = old_dim + new_index
            term1[new_index] = (product_tensor[:old_dim, new_row, :old_dim] @ lift) % PRIME
            term2[new_index] = (product_tensor[:old_dim, :old_dim, new_row] @ lift) % PRIME
        linear_nonzero = np.zeros_like(target, dtype=bool)
        linear_nonzero |= np.any(new_product_to_old_inputs != 0, axis=0)[None, :, :]
        linear_nonzero |= np.any(term1 != 0, axis=0)[:, None, :]
        linear_nonzero |= np.any(term2 != 0, axis=0)[:, :, None]
        quadratic_target_rows = np.any(product_tensor[:old_dim, old_dim:, old_dim:] != 0, axis=(1, 2))
        exact_nonzero = linear_nonzero | quadratic_target_rows[:, None, None]
        linear_impossible = (~linear_nonzero) & (target != 0)
        exact_impossible = (~exact_nonzero) & (target != 0)
        first = np.argwhere(exact_impossible)[0].tolist() if np.any(exact_impossible) else [-1, -1, -1]
        target_counts.append(int(np.count_nonzero(target)))
        linear_impossible_counts.append(int(np.count_nonzero(linear_impossible)))
        exact_impossible_counts.append(int(np.count_nonzero(exact_impossible)))
        obstruction_rows.append(
            {
                "generator_id": generator_id,
                "target_residual_nonzero_count": int(np.count_nonzero(target)),
                "linear_support_row_count": int(np.count_nonzero(linear_nonzero)),
                "linear_impossible_row_count": int(np.count_nonzero(linear_impossible)),
                "quadratic_target_row_count": int(np.count_nonzero(quadratic_target_rows)),
                "exact_support_row_count": int(np.count_nonzero(exact_nonzero)),
                "exact_impossible_row_count": int(np.count_nonzero(exact_impossible)),
                "first_impossible_target_row": first[0],
                "first_impossible_left_row": first[1],
                "first_impossible_right_row": first[2],
                "first_impossible_target_relation": relation_by_row.get(first[0], -1),
                "first_impossible_left_relation": relation_by_row.get(first[1], -1),
                "first_impossible_right_relation": relation_by_row.get(first[2], -1),
                "first_impossible_required_value": int(target[tuple(first)]) if first[0] >= 0 else 0,
                "fixed_old_extension_possible_flag": int(not np.any(exact_impossible)),
            }
        )

    obs = {
        "long_k23cl_certified_flag": int(
            long_k23cl.get("status") == "SECTOR33_K23_MULTIPLICATION_CLOSURE60_CERTIFIED"
            and long_k23cl.get("all_checks_pass") is True
        ),
        "long_k23ext_certified_flag": int(
            long_k23ext.get("status") == "SECTOR33_K23_CLOSURE60_EXTENSION_SEAM_CERTIFIED"
            and long_k23ext.get("all_checks_pass") is True
        ),
        "long_k23rh_certified_flag": int(
            long_k23rh.get("status") == "SECTOR33_K23_RHC_SOURCE_LIFT_CERTIFIED"
            and long_k23rh.get("all_checks_pass") is True
        ),
        "generator_count": int(r_hc_lifts.shape[0]),
        "old_dimension": old_dim,
        "new_dimension": new_dim,
        "closure_dimension": int(product_tensor.shape[0]),
        "old_slice_equation_count": old_dim * old_dim * old_dim,
        "target_residual_nonzero_total": sum(target_counts),
        "linear_impossible_total": sum(linear_impossible_counts),
        "linear_impossible_min": min(linear_impossible_counts),
        "linear_impossible_max": max(linear_impossible_counts),
        "exact_impossible_total": sum(exact_impossible_counts),
        "exact_impossible_min": min(exact_impossible_counts),
        "exact_impossible_max": max(exact_impossible_counts),
        "failed_generator_count": sum(int(row["fixed_old_extension_possible_flag"] == 0) for row in obstruction_rows),
        "fixed_old_extension_obstructed_flag": int(all(row["fixed_old_extension_possible_flag"] == 0 for row in obstruction_rows)),
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    obstruction_table = table_from_rows(OBSTRUCTION_COLUMNS, obstruction_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "obstruction_table": obstruction_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
        "exact_impossible_vector": np.asarray(exact_impossible_counts, dtype=np.int64),
    }
    return {
        "long_k23cl": long_k23cl,
        "long_k23ext": long_k23ext,
        "long_k23rh": long_k23rh,
        "obstruction_rows": obstruction_rows,
        "obs_rows": obs_rows,
        "obstruction_table": obstruction_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "obstruction_text_hash": hashlib.sha256(
            digest_text(OBSTRUCTION_COLUMNS, obstruction_rows).encode("ascii")
        ).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": (
            obs["long_k23cl_certified_flag"],
            obs["long_k23ext_certified_flag"],
            obs["long_k23rh_certified_flag"],
        )
        == (1, 1, 1),
        "dimension_profile_matches": (
            obs["generator_count"],
            obs["old_dimension"],
            obs["new_dimension"],
            obs["closure_dimension"],
            obs["old_slice_equation_count"],
        )
        == (9, 56, 4, 60, 175616),
        "target_residual_profile_matches": obs["target_residual_nonzero_total"] == 936661,
        "linear_impossible_profile_matches": (
            obs["linear_impossible_total"],
            obs["linear_impossible_min"],
            obs["linear_impossible_max"],
        )
        == (924257, 80990, 125386),
        "exact_impossible_profile_matches": (
            obs["exact_impossible_total"],
            obs["exact_impossible_min"],
            obs["exact_impossible_max"],
            obs["failed_generator_count"],
            obs["fixed_old_extension_obstructed_flag"],
        )
        == (922141, 80954, 125169, 9, 1),
        "boundary_flags_match": obs["complete_goal_claim_flag"] == 0,
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_fixed_old_mixed_extension_obstruction",
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies that no 60x60 product-preserving extension with the certified 56x56 old block fixed can exist; every generator has old-slice residual equations with zero possible correction terms.",
    }
    seam_payload = {
        "schema": "long.k23fix.seam@1",
        "status": STATUS,
        "claim": "The fixed-old mixed extension ansatz M=[[A,B],[C,D]] is obstructed for all nine R_hc generators on the old-target old-input product slice.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23cl": input_entry(
            LONG_K23CL_REPORT,
            {
                "status": rows["long_k23cl"].get("status"),
                "certificate_sha256": rows["long_k23cl"].get("certificate_sha256"),
            },
        ),
        "long_k23ext": input_entry(
            LONG_K23EXT_REPORT,
            {
                "status": rows["long_k23ext"].get("status"),
                "certificate_sha256": rows["long_k23ext"].get("certificate_sha256"),
            },
        ),
        "long_k23cl_closure_rows": input_entry(LONG_K23CL_CLOSURE_ROWS),
        "long_k23cl_matrices": input_entry(LONG_K23CL_MATRICES),
        "long_k23rh": input_entry(
            LONG_K23RH_REPORT,
            {
                "status": rows["long_k23rh"].get("status"),
                "certificate_sha256": rows["long_k23rh"].get("certificate_sha256"),
            },
        ),
        "long_k23rh_matrices": input_entry(LONG_K23RH_MATRICES),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23fix.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23fix certifies the fixed-old 60x60 mixed-extension obstruction for the sector33 K23 product surface.",
        "stage_protocol": {
            "draft": "read the corrected long_k23cl closure, long_k23ext seam, and the nine R_hc source lifts",
            "witness": "emit generator obstruction rows and observable rows for the fixed-old mixed ansatz",
            "coherence": "check input certificates, dimensions, residual profiles, and exact impossible-row counts",
            "closure": "obstruct the fixed-old 60x60 product-preserving extension while leaving variable-old-block extensions open",
            "emit": "write long_k23fix artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "fixed_obstructions_csv": relpath(OUT_DIR / "fixed_obstructions.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23fix_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the corrected 60-row closure preserves the old 56-row basis and appends four leaked rows",
                "for M=[[A,B],[C,D]] with A equal to the certified old R_hc lift, the old-target old-input slice has exact impossible rows for every generator",
                "D does not enter those old-slice equations, and the B, C, and C*C correction supports are zero on the displayed impossible rows",
                "the exact impossible-row total is 922,141 across the nine generators",
            ],
            "does_not_certify": [
                "nonexistence of a 60x60 product-preserving action when the old 56x56 block is allowed to change",
                "a solution for a variable-old-block extension",
                "a final operator carrier",
                "bundle-wide integration",
                "a final broad-goal closure claim",
            ],
        },
        "next_highest_yield_item": "Relax the old-block constraint and solve the quotient-preserving 60x60 equations, using the fixed-old obstruction to rule out any solution that keeps the old R_hc block unchanged.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23fix.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23fix.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "obstructions_csv": csv_text(OBSTRUCTION_COLUMNS, rows["obstruction_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "obstruction_table": rows["obstruction_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "obstruction_text_sha256": rows["obstruction_text_hash"],
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
    (OUT_DIR / "fixed_obstructions.csv").write_text(payloads["obstructions_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        obstruction_table=payloads["obstruction_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23fix_matrices.npz", **payloads["matrix_payload"])
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
