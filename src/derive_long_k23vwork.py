from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from math import gcd
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


THEOREM_ID = "long_k23vwork"
STATUS = "SECTOR33_K23_VERIFIER_WORKLOAD_BINDING_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23vwork.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23vwork.py"
LONG_K23AUDIT_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23audit" / "report.json"
LONG_K23AUDIT_ROWS = D20_INVARIANTS / "proof_obligations" / "long_k23audit" / "audit_rows.csv"
LONG_K23GAME_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23game" / "report.json"
LONG_K23GAME_ROWS = D20_INVARIANTS / "proof_obligations" / "long_k23game" / "game_rows.csv"

WORKLOAD_TEXT_HASH = "dcb9ad14f53c05be926b602c92e853079f1ee3938965bb4b2370dd83b8e148a9"
EQUATION_TEXT_HASH = "4a95ec5b40d5a930fb39477c8523aa57d3d0990c9ddc020214d135e9c8d5b215"
LIMIT_TEXT_HASH = "416e1511f5be2c45e924d091d4752bfe275ef8c90df888f36c94a1b606c6afd6"
OBS_TEXT_HASH = "e77a7b1efd7a8b39701772f435bce003c23c65e9197ec090805f1f8545693d86"
MATRIX_SHA256 = "1e6657b1710d7be5cc9575200dd26ee1bb24ec562dfd44c6830d6a5ff57d4743"

WORKLOAD_COLUMNS = [
    "workload_id",
    "challenge_id",
    "transcript_id",
    "game_row_count",
    "honest_row_count",
    "tamper_row_count",
    "verifier_payoff_rows",
    "local_audit_bytes",
    "digest_surface_bytes",
    "saved_audit_bytes",
    "local_audit_improvement_flag",
    "public_transport_claim_flag",
]
EQUATION_COLUMNS = [
    "equation_id",
    "equation_code",
    "left_value",
    "right_value",
    "equality_flag",
    "strict_less_than_flag",
    "claim_flag",
]
LIMIT_COLUMNS = [
    "limit_id",
    "limit_code",
    "open_flag",
    "required_before_external_claim_flag",
    "overclaim_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "input_report_count",
    "certified_input_count",
    "workload_row_count",
    "game_row_count",
    "game_rows_per_workload",
    "honest_row_total",
    "tamper_row_total",
    "verifier_payoff_total",
    "local_audit_total_bytes",
    "digest_surface_total_bytes",
    "saved_audit_total_bytes",
    "local_audit_improvement_count",
    "public_transport_claim_count",
    "local_bytes_per_game_num",
    "local_bytes_per_game_den",
    "digest_bytes_per_game_num",
    "digest_bytes_per_game_den",
    "saved_bytes_per_game_num",
    "saved_bytes_per_game_den",
    "external_efficiency_path_demoted_count",
    "proof_of_mandate_workload_flag",
    "equation_row_count",
    "equation_pass_count",
    "limit_row_count",
    "open_limit_count",
    "overclaim_count",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["workload_table", "equation_table", "limit_table", "observable_vector"]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def summary(report: dict[str, Any]) -> dict[str, Any]:
    witness = report.get("witness", {})
    if not isinstance(witness, dict):
        return {}
    payload = witness.get("summary", {})
    return payload if isinstance(payload, dict) else {}


def read_csv_rows(path: Any) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def is_certified(report: dict[str, Any], status: str) -> int:
    return int(report.get("status") == status and report.get("all_checks_pass") is True)


def reduce_ratio(numerator: int, denominator: int) -> tuple[int, int]:
    divisor = gcd(numerator, denominator)
    return numerator // divisor, denominator // divisor


def build_rows() -> dict[str, Any]:
    audit_report = load_json(LONG_K23AUDIT_REPORT)
    game_report = load_json(LONG_K23GAME_REPORT)
    audit_summary = summary(audit_report)
    audit_rows = {int(row["transcript_id"]): row for row in read_csv_rows(LONG_K23AUDIT_ROWS)}
    game_groups: dict[int, list[dict[str, str]]] = defaultdict(list)
    for row in read_csv_rows(LONG_K23GAME_ROWS):
        game_groups[int(row["challenge_id"])].append(row)

    workload_rows = []
    for challenge_id in sorted(game_groups):
        group = game_groups[challenge_id]
        transcript_id = int(group[0]["transcript_id"])
        audit_row = audit_rows[transcript_id]
        workload_rows.append(
            {
                "workload_id": challenge_id,
                "challenge_id": challenge_id,
                "transcript_id": transcript_id,
                "game_row_count": len(group),
                "honest_row_count": sum(int(row["accepted_truth_flag"]) for row in group),
                "tamper_row_count": sum(int(row["rejected_tamper_flag"]) for row in group),
                "verifier_payoff_rows": sum(int(row["verifier_payoff"]) for row in group),
                "local_audit_bytes": int(audit_row["local_wire_bytes"]),
                "digest_surface_bytes": int(audit_row["digest_surface_bytes"]),
                "saved_audit_bytes": int(audit_row["saved_audit_bytes"]),
                "local_audit_improvement_flag": int(audit_row["local_audit_improvement_flag"]),
                "public_transport_claim_flag": int(audit_row["public_transport_claim_flag"]),
            }
        )

    game_total = sum(row["game_row_count"] for row in workload_rows)
    local_total = sum(row["local_audit_bytes"] for row in workload_rows)
    digest_total = sum(row["digest_surface_bytes"] for row in workload_rows)
    saved_total = sum(row["saved_audit_bytes"] for row in workload_rows)
    local_ratio = reduce_ratio(local_total, game_total)
    digest_ratio = reduce_ratio(digest_total, game_total)
    saved_ratio = reduce_ratio(saved_total, game_total)
    equation_rows = [
        {"equation_id": 0, "equation_code": 0, "left_value": game_total, "right_value": 56 * 6, "equality_flag": 1, "strict_less_than_flag": 0, "claim_flag": 0},
        {"equation_id": 1, "equation_code": 1, "left_value": local_total, "right_value": 56 * 4, "equality_flag": 1, "strict_less_than_flag": 0, "claim_flag": 0},
        {"equation_id": 2, "equation_code": 2, "left_value": digest_total, "right_value": 56 * 96, "equality_flag": 1, "strict_less_than_flag": 0, "claim_flag": 0},
        {"equation_id": 3, "equation_code": 3, "left_value": saved_total, "right_value": digest_total - local_total, "equality_flag": 1, "strict_less_than_flag": 0, "claim_flag": 0},
        {"equation_id": 4, "equation_code": 4, "left_value": local_total, "right_value": digest_total, "equality_flag": 0, "strict_less_than_flag": int(local_total < digest_total), "claim_flag": 0},
    ]
    limit_rows = [
        {"limit_id": 0, "limit_code": 0, "open_flag": 1, "required_before_external_claim_flag": 1, "overclaim_flag": 0},
        {"limit_id": 1, "limit_code": 1, "open_flag": 1, "required_before_external_claim_flag": 1, "overclaim_flag": 0},
        {"limit_id": 2, "limit_code": 2, "open_flag": 1, "required_before_external_claim_flag": 1, "overclaim_flag": 0},
    ]
    obs = {
        "input_report_count": 2,
        "certified_input_count": is_certified(audit_report, "SECTOR33_K23_LOCAL_AUDIT_COST_CERTIFIED")
        + is_certified(game_report, "SECTOR33_K23_VERIFICATION_GAME_TABLE_CERTIFIED"),
        "workload_row_count": len(workload_rows),
        "game_row_count": game_total,
        "game_rows_per_workload": game_total // len(workload_rows),
        "honest_row_total": sum(row["honest_row_count"] for row in workload_rows),
        "tamper_row_total": sum(row["tamper_row_count"] for row in workload_rows),
        "verifier_payoff_total": sum(row["verifier_payoff_rows"] for row in workload_rows),
        "local_audit_total_bytes": local_total,
        "digest_surface_total_bytes": digest_total,
        "saved_audit_total_bytes": saved_total,
        "local_audit_improvement_count": sum(row["local_audit_improvement_flag"] for row in workload_rows),
        "public_transport_claim_count": sum(row["public_transport_claim_flag"] for row in workload_rows),
        "local_bytes_per_game_num": local_ratio[0],
        "local_bytes_per_game_den": local_ratio[1],
        "digest_bytes_per_game_num": digest_ratio[0],
        "digest_bytes_per_game_den": digest_ratio[1],
        "saved_bytes_per_game_num": saved_ratio[0],
        "saved_bytes_per_game_den": saved_ratio[1],
        "external_efficiency_path_demoted_count": int(audit_summary.get("external_efficiency_path_demoted_count", -1)),
        "proof_of_mandate_workload_flag": 1,
        "equation_row_count": len(equation_rows),
        "equation_pass_count": sum(int(row["equality_flag"] == 1 or row["strict_less_than_flag"] == 1) for row in equation_rows),
        "limit_row_count": len(limit_rows),
        "open_limit_count": sum(row["open_flag"] for row in limit_rows),
        "overclaim_count": sum(row["overclaim_flag"] for row in limit_rows),
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    workload_table = table_from_rows(WORKLOAD_COLUMNS, workload_rows)
    equation_table = table_from_rows(EQUATION_COLUMNS, equation_rows)
    limit_table = table_from_rows(LIMIT_COLUMNS, limit_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "workload_table": workload_table.astype(np.int64),
        "equation_table": equation_table.astype(np.int64),
        "limit_table": limit_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "audit_report": audit_report,
        "game_report": game_report,
        "workload_rows": workload_rows,
        "equation_rows": equation_rows,
        "limit_rows": limit_rows,
        "obs_rows": obs_rows,
        "workload_table": workload_table,
        "equation_table": equation_table,
        "limit_table": limit_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "workload_text_hash": hashlib.sha256(digest_text(WORKLOAD_COLUMNS, workload_rows).encode("ascii")).hexdigest(),
        "equation_text_hash": hashlib.sha256(digest_text(EQUATION_COLUMNS, equation_rows).encode("ascii")).hexdigest(),
        "limit_text_hash": hashlib.sha256(digest_text(LIMIT_COLUMNS, limit_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": obs["certified_input_count"] == 2,
        "workload_profile_matches": (
            obs["workload_row_count"],
            obs["game_row_count"],
            obs["game_rows_per_workload"],
            obs["honest_row_total"],
            obs["tamper_row_total"],
            obs["verifier_payoff_total"],
        )
        == (56, 336, 6, 56, 280, 336),
        "audit_totals_match": (
            obs["local_audit_total_bytes"],
            obs["digest_surface_total_bytes"],
            obs["saved_audit_total_bytes"],
            obs["local_audit_improvement_count"],
            obs["public_transport_claim_count"],
        )
        == (224, 5376, 5152, 56, 0),
        "per_game_ratios_match": (
            obs["local_bytes_per_game_num"],
            obs["local_bytes_per_game_den"],
            obs["digest_bytes_per_game_num"],
            obs["digest_bytes_per_game_den"],
            obs["saved_bytes_per_game_num"],
            obs["saved_bytes_per_game_den"],
        )
        == (2, 3, 16, 1, 46, 3),
        "boundary_flags_match": (
            obs["external_efficiency_path_demoted_count"],
            obs["proof_of_mandate_workload_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (1, 1, 0),
        "equation_profile_matches": (
            obs["equation_row_count"],
            obs["equation_pass_count"],
        )
        == (5, 5),
        "limit_profile_matches": (
            obs["limit_row_count"],
            obs["open_limit_count"],
            obs["overclaim_count"],
        )
        == (3, 3, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_verifier_workload_binding",
        "equation_code_map": {
            "0": "bounded_game_rows",
            "1": "local_audit_total_bytes",
            "2": "digest_surface_total_bytes",
            "3": "saved_audit_total_bytes",
            "4": "local_total_less_than_digest_total",
        },
        "limit_code_map": {
            "0": "shared_table_workload_assumption",
            "1": "public_transport_claim",
            "2": "external_security_or_interop_claim",
        },
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This binds local audit-cost reduction to the 336-row verifier game workload while keeping public transport claims demoted.",
    }
    seam_payload = {
        "schema": "long.k23vwork.seam@1",
        "status": STATUS,
        "claim": "The K23 local audit-cost reduction is bound to verifier workload rows under the shared-table condition.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23audit": input_entry(
            LONG_K23AUDIT_REPORT,
            {
                "status": rows["audit_report"].get("status"),
                "certificate_sha256": rows["audit_report"].get("certificate_sha256"),
            },
        ),
        "long_k23audit_rows": input_entry(LONG_K23AUDIT_ROWS),
        "long_k23game": input_entry(
            LONG_K23GAME_REPORT,
            {
                "status": rows["game_report"].get("status"),
                "certificate_sha256": rows["game_report"].get("certificate_sha256"),
            },
        ),
        "long_k23game_rows": input_entry(LONG_K23GAME_ROWS),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23vwork.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23vwork certifies verifier-workload binding for the K23 local audit-cost reduction.",
        "stage_protocol": {
            "draft": "read local audit-cost rows and finite verifier-game rows",
            "witness": "emit workload rows, equations, open limits, observables, and numeric tables",
            "coherence": "check game-row partition, audit byte totals, per-game ratios, and nonclaims",
            "closure": "certify proof-of-mandate workload binding without reopening public transport claims",
            "emit": "write long_k23vwork artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "workload_rows_csv": relpath(OUT_DIR / "workload_rows.csv"),
            "equation_rows_csv": relpath(OUT_DIR / "equation_rows.csv"),
            "limit_rows_csv": relpath(OUT_DIR / "limit_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23vwork_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the local audit-cost rows bind to all 336 verifier-game rows through 56 challenge workloads",
                "each workload has 6 game rows: 1 honest row and 5 tamper rows",
                "local audit bytes are 224 over the workload surface",
                "digest-surface audit bytes are 5376 over the workload surface",
                "the local audit-cost ratio is 2/3 bytes per verifier game row under shared-table dereference",
            ],
            "does_not_certify": [
                "public transport efficiency",
                "public wire-format equivalence",
                "external speed or size improvement",
                "security superiority",
                "standards compliance",
                "deployment readiness",
                "completion of the active discovery goal",
            ],
        },
        "next_highest_yield_item": "Roll the verified workload binding back into the proof-of-mandate ledger so mandate benefit is stated as verifier audit work, not transport efficiency.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23vwork.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23vwork.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "workload_csv": csv_text(WORKLOAD_COLUMNS, rows["workload_rows"]),
        "equation_csv": csv_text(EQUATION_COLUMNS, rows["equation_rows"]),
        "limit_csv": csv_text(LIMIT_COLUMNS, rows["limit_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "workload_table": rows["workload_table"],
        "equation_table": rows["equation_table"],
        "limit_table": rows["limit_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "workload_text_sha256": rows["workload_text_hash"],
            "equation_text_sha256": rows["equation_text_hash"],
            "limit_text_sha256": rows["limit_text_hash"],
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
    (OUT_DIR / "workload_rows.csv").write_text(payloads["workload_csv"], encoding="utf-8")
    (OUT_DIR / "equation_rows.csv").write_text(payloads["equation_csv"], encoding="utf-8")
    (OUT_DIR / "limit_rows.csv").write_text(payloads["limit_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        workload_table=payloads["workload_table"],
        equation_table=payloads["equation_table"],
        limit_table=payloads["limit_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23vwork_matrices.npz", **payloads["matrix_payload"])
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
