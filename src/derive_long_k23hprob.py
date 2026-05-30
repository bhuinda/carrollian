from __future__ import annotations

import hashlib
import json
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


THEOREM_ID = "long_k23hprob"
STATUS = "SECTOR33_K23_HARDNESS_PROBLEM_DEFINITION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23hprob.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23hprob.py"

REPORT_PATHS = {
    "long_k23seci": D20_INVARIANTS / "proof_obligations" / "long_k23seci" / "report.json",
    "long_k23interop": D20_INVARIANTS / "proof_obligations" / "long_k23interop" / "report.json",
    "long_k23dist": D20_INVARIANTS / "proof_obligations" / "long_k23dist" / "report.json",
    "long_k23sound": D20_INVARIANTS / "proof_obligations" / "long_k23sound" / "report.json",
}
EXPECTED_STATUSES = {
    "long_k23seci": "SECTOR33_K23_SECURITY_INTEGRITY_GATE_CERTIFIED",
    "long_k23interop": "SECTOR33_K23_INTEROP_BENCHMARK_GATE_CERTIFIED",
    "long_k23dist": "SECTOR33_K23_PUBLIC_TABLE_DISTRIBUTION_DECODER_CERTIFIED",
    "long_k23sound": "SECTOR33_K23_BOUNDED_ADVERSARY_SOUNDNESS_CERTIFIED",
}

PROBLEM_TEXT_HASH = "383bb30656bba8060c8efdb441ed47dfd08d1848897f4119f5ce0b6ebbb8a7c1"
REDUCTION_TEXT_HASH = "5245d489d2f7aa94b4a8f3047ded6be58065f9b101b26fb09c22f0db34c2dc68"
GATE_TEXT_HASH = "c76bd0f8e0bb9639ad0b5768dd362987e9b50da96a59998ff818e7ae6cb721b7"
OBS_TEXT_HASH = "07d18893b410edf4fcae5b44238722fdee319fc35594375e5f24f1bc0d0b5f0c"
MATRIX_SHA256 = "7f9b029388b3bb6d9032cd5ab5eca7370f7e099fdd7b2ba51c4510fb8a08c0b7"

PROBLEM_COLUMNS = [
    "problem_id",
    "problem_code",
    "public_input_code",
    "hidden_witness_code",
    "adversary_goal_code",
    "success_condition_code",
    "finite_evidence_flag",
    "trivial_under_public_table_flag",
    "reduction_target_required_flag",
    "reduction_target_present_flag",
    "hardness_claim_flag",
]
REDUCTION_COLUMNS = [
    "reduction_id",
    "problem_id",
    "reduction_code",
    "source_assumption_code",
    "target_problem_code",
    "materialized_flag",
    "blocking_flag",
    "proof_claim_flag",
]
GATE_COLUMNS = [
    "gate_id",
    "gate_code",
    "satisfied_flag",
    "blocking_flag",
    "claim_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "input_report_count",
    "certified_input_count",
    "problem_row_count",
    "finite_evidence_problem_count",
    "public_table_trivial_problem_count",
    "nontrivial_problem_candidate_count",
    "reduction_target_required_count",
    "reduction_target_present_count",
    "hardness_claim_count",
    "reduction_row_count",
    "materialized_reduction_count",
    "blocking_reduction_count",
    "proof_claim_count",
    "gate_row_count",
    "satisfied_gate_count",
    "blocking_gate_count",
    "claim_gate_count",
    "bounded_soundness_error_numerator",
    "bounded_soundness_error_denominator",
    "valid_decode_count",
    "invalid_reject_count",
    "transcript_index_bytes",
    "objective_byte_improvement_flag",
    "hardness_problem_defined_flag",
    "deploy_ready_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["problem_table", "reduction_table", "gate_table", "observable_vector"]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def summary(report: dict[str, Any]) -> dict[str, Any]:
    witness = report.get("witness", {})
    if not isinstance(witness, dict):
        return {}
    payload = witness.get("summary", {})
    return payload if isinstance(payload, dict) else {}


def is_certified(report: dict[str, Any], status: str) -> int:
    return int(report.get("status") == status and report.get("all_checks_pass") is True)


def build_rows() -> dict[str, Any]:
    reports = {name: load_json(path) for name, path in REPORT_PATHS.items()}
    summaries = {name: summary(report) for name, report in reports.items()}
    seci = summaries["long_k23seci"]
    interop = summaries["long_k23interop"]
    dist = summaries["long_k23dist"]
    sound = summaries["long_k23sound"]

    problem_rows = [
        {
            "problem_id": 0,
            "problem_code": 0,
            "public_input_code": 0,
            "hidden_witness_code": 0,
            "adversary_goal_code": 0,
            "success_condition_code": 0,
            "finite_evidence_flag": 1,
            "trivial_under_public_table_flag": 0,
            "reduction_target_required_flag": 1,
            "reduction_target_present_flag": 0,
            "hardness_claim_flag": 0,
        },
        {
            "problem_id": 1,
            "problem_code": 1,
            "public_input_code": 1,
            "hidden_witness_code": 0,
            "adversary_goal_code": 1,
            "success_condition_code": 1,
            "finite_evidence_flag": 1,
            "trivial_under_public_table_flag": 1,
            "reduction_target_required_flag": 0,
            "reduction_target_present_flag": 0,
            "hardness_claim_flag": 0,
        },
        {
            "problem_id": 2,
            "problem_code": 2,
            "public_input_code": 2,
            "hidden_witness_code": 0,
            "adversary_goal_code": 2,
            "success_condition_code": 2,
            "finite_evidence_flag": 1,
            "trivial_under_public_table_flag": 1,
            "reduction_target_required_flag": 0,
            "reduction_target_present_flag": 0,
            "hardness_claim_flag": 0,
        },
        {
            "problem_id": 3,
            "problem_code": 3,
            "public_input_code": 3,
            "hidden_witness_code": 0,
            "adversary_goal_code": 3,
            "success_condition_code": 3,
            "finite_evidence_flag": 1,
            "trivial_under_public_table_flag": 0,
            "reduction_target_required_flag": 1,
            "reduction_target_present_flag": 0,
            "hardness_claim_flag": 0,
        },
    ]
    reduction_rows = [
        {"reduction_id": 0, "problem_id": 0, "reduction_code": 0, "source_assumption_code": 0, "target_problem_code": 0, "materialized_flag": 0, "blocking_flag": 1, "proof_claim_flag": 0},
        {"reduction_id": 1, "problem_id": 3, "reduction_code": 1, "source_assumption_code": 1, "target_problem_code": 1, "materialized_flag": 0, "blocking_flag": 1, "proof_claim_flag": 0},
        {"reduction_id": 2, "problem_id": 1, "reduction_code": 2, "source_assumption_code": 2, "target_problem_code": 2, "materialized_flag": 0, "blocking_flag": 1, "proof_claim_flag": 0},
        {"reduction_id": 3, "problem_id": 2, "reduction_code": 3, "source_assumption_code": 2, "target_problem_code": 3, "materialized_flag": 0, "blocking_flag": 1, "proof_claim_flag": 0},
    ]
    gate_rows = [
        {"gate_id": 0, "gate_code": 0, "satisfied_flag": 1, "blocking_flag": 0, "claim_flag": 0},
        {"gate_id": 1, "gate_code": 1, "satisfied_flag": 1, "blocking_flag": 0, "claim_flag": 0},
        {"gate_id": 2, "gate_code": 2, "satisfied_flag": 1, "blocking_flag": 0, "claim_flag": 0},
        {"gate_id": 3, "gate_code": 3, "satisfied_flag": 0, "blocking_flag": 1, "claim_flag": 0},
        {"gate_id": 4, "gate_code": 4, "satisfied_flag": 0, "blocking_flag": 1, "claim_flag": 0},
        {"gate_id": 5, "gate_code": 5, "satisfied_flag": 0, "blocking_flag": 1, "claim_flag": 0},
    ]
    obs = {
        "input_report_count": len(REPORT_PATHS),
        "certified_input_count": sum(is_certified(reports[name], EXPECTED_STATUSES[name]) for name in REPORT_PATHS),
        "problem_row_count": len(problem_rows),
        "finite_evidence_problem_count": sum(row["finite_evidence_flag"] for row in problem_rows),
        "public_table_trivial_problem_count": sum(row["trivial_under_public_table_flag"] for row in problem_rows),
        "nontrivial_problem_candidate_count": sum(1 - row["trivial_under_public_table_flag"] for row in problem_rows),
        "reduction_target_required_count": sum(row["reduction_target_required_flag"] for row in problem_rows),
        "reduction_target_present_count": sum(row["reduction_target_present_flag"] for row in problem_rows),
        "hardness_claim_count": sum(row["hardness_claim_flag"] for row in problem_rows),
        "reduction_row_count": len(reduction_rows),
        "materialized_reduction_count": sum(row["materialized_flag"] for row in reduction_rows),
        "blocking_reduction_count": sum(row["blocking_flag"] for row in reduction_rows),
        "proof_claim_count": sum(row["proof_claim_flag"] for row in reduction_rows),
        "gate_row_count": len(gate_rows),
        "satisfied_gate_count": sum(row["satisfied_flag"] for row in gate_rows),
        "blocking_gate_count": sum(row["blocking_flag"] for row in gate_rows),
        "claim_gate_count": sum(row["claim_flag"] for row in gate_rows),
        "bounded_soundness_error_numerator": int(seci.get("bounded_soundness_error_numerator", -1)),
        "bounded_soundness_error_denominator": int(seci.get("bounded_soundness_error_denominator", -1)),
        "valid_decode_count": int(dist.get("valid_decode_row_count", -1)),
        "invalid_reject_count": int(dist.get("invalid_reject_count", -1)),
        "transcript_index_bytes": int(interop.get("transcript_index_bytes", -1)),
        "objective_byte_improvement_flag": int(interop.get("objective_byte_improvement_flag", -1)),
        "hardness_problem_defined_flag": 1,
        "deploy_ready_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    problem_table = table_from_rows(PROBLEM_COLUMNS, problem_rows)
    reduction_table = table_from_rows(REDUCTION_COLUMNS, reduction_rows)
    gate_table = table_from_rows(GATE_COLUMNS, gate_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "problem_table": problem_table.astype(np.int64),
        "reduction_table": reduction_table.astype(np.int64),
        "gate_table": gate_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "reports": reports,
        "problem_rows": problem_rows,
        "reduction_rows": reduction_rows,
        "gate_rows": gate_rows,
        "obs_rows": obs_rows,
        "problem_table": problem_table,
        "reduction_table": reduction_table,
        "gate_table": gate_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "problem_text_hash": hashlib.sha256(digest_text(PROBLEM_COLUMNS, problem_rows).encode("ascii")).hexdigest(),
        "reduction_text_hash": hashlib.sha256(digest_text(REDUCTION_COLUMNS, reduction_rows).encode("ascii")).hexdigest(),
        "gate_text_hash": hashlib.sha256(digest_text(GATE_COLUMNS, gate_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": obs["certified_input_count"] == obs["input_report_count"] == 4,
        "problem_definition_matches": (
            obs["problem_row_count"],
            obs["finite_evidence_problem_count"],
            obs["public_table_trivial_problem_count"],
            obs["nontrivial_problem_candidate_count"],
            obs["hardness_problem_defined_flag"],
        )
        == (4, 4, 2, 2, 1),
        "reduction_gap_matches": (
            obs["reduction_target_required_count"],
            obs["reduction_target_present_count"],
            obs["reduction_row_count"],
            obs["materialized_reduction_count"],
            obs["blocking_reduction_count"],
            obs["proof_claim_count"],
        )
        == (2, 0, 4, 0, 4, 0),
        "evidence_profile_matches": (
            obs["bounded_soundness_error_numerator"],
            obs["bounded_soundness_error_denominator"],
            obs["valid_decode_count"],
            obs["invalid_reject_count"],
            obs["transcript_index_bytes"],
            obs["objective_byte_improvement_flag"],
        )
        == (0, 112_869_680, 56, 200, 56, 1),
        "gate_profile_matches": (
            obs["gate_row_count"],
            obs["satisfied_gate_count"],
            obs["blocking_gate_count"],
            obs["claim_gate_count"],
        )
        == (6, 3, 3, 0),
        "hardness_and_deploy_nonclaims_match": (
            obs["hardness_claim_count"],
            obs["deploy_ready_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (0, 0, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_hardness_problem_definition",
        "problem_code_map": {
            "0": "noncanonical_accept_forgery",
            "1": "public_opening_recovery",
            "2": "public_valid_byte_distinguishing",
            "3": "bounded_tamper_game_break",
        },
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This defines hardness candidates and rejects public-table-trivial targets as hardness claims under the current artifact boundary.",
    }
    seam_payload = {
        "schema": "long.k23hprob.seam@1",
        "status": STATUS,
        "claim": "The K23 hardness problem boundary is now explicit: finite integrity and byte efficiency are certified, but no reduction target or deploy-grade hardness proof is materialized.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        name: input_entry(
            REPORT_PATHS[name],
            {
                "status": rows["reports"][name].get("status"),
                "certificate_sha256": rows["reports"][name].get("certificate_sha256"),
            },
        )
        for name in REPORT_PATHS
    }
    inputs["derive_script"] = input_entry(DERIVE_SCRIPT)
    inputs["validator"] = input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)}
    report = {
        "schema": "long.k23hprob.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23hprob certifies the explicit hardness problem-definition boundary for the K23 protocol surface.",
        "stage_protocol": {
            "draft": "read security-integrity, interop, decoder, and bounded-soundness certificates",
            "witness": "emit problem rows, reduction rows, gate rows, observables, and numeric tables",
            "coherence": "check finite evidence, public-table-trivial targets, missing reductions, and deploy nonclaims",
            "closure": "certify the hardness target boundary without claiming hardness or deployment readiness",
            "emit": "write long_k23hprob artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "problem_rows_csv": relpath(OUT_DIR / "problem_rows.csv"),
            "reduction_rows_csv": relpath(OUT_DIR / "reduction_rows.csv"),
            "gate_rows_csv": relpath(OUT_DIR / "gate_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23hprob_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "four explicit adversary problem rows are defined",
                "two public-table-trivial targets are rejected as hardness targets",
                "two nontrivial finite-game candidates require reduction targets not yet present",
                "deployment readiness remains zero",
            ],
            "does_not_certify": [
                "computational hardness",
                "a reduction to a known hard problem",
                "a private witness source",
                "an asymptotic security family",
                "deployment readiness",
            ],
        },
        "next_highest_yield_item": "Choose the reduction route: either add a private or one-way source for the noncanonical-forgery problem, or demote the current public-table codec to integrity-only infrastructure.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23hprob.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23hprob.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "problem_csv": csv_text(PROBLEM_COLUMNS, rows["problem_rows"]),
        "reduction_csv": csv_text(REDUCTION_COLUMNS, rows["reduction_rows"]),
        "gate_csv": csv_text(GATE_COLUMNS, rows["gate_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "problem_table": rows["problem_table"],
        "reduction_table": rows["reduction_table"],
        "gate_table": rows["gate_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "problem_text_sha256": rows["problem_text_hash"],
            "reduction_text_sha256": rows["reduction_text_hash"],
            "gate_text_sha256": rows["gate_text_hash"],
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
    (OUT_DIR / "problem_rows.csv").write_text(payloads["problem_csv"], encoding="utf-8")
    (OUT_DIR / "reduction_rows.csv").write_text(payloads["reduction_csv"], encoding="utf-8")
    (OUT_DIR / "gate_rows.csv").write_text(payloads["gate_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        problem_table=payloads["problem_table"],
        reduction_table=payloads["reduction_table"],
        gate_table=payloads["gate_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23hprob_matrices.npz", **payloads["matrix_payload"])
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
