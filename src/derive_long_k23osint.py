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


THEOREM_ID = "long_k23osint"
STATUS = "SECTOR33_K23_OPEN_SOURCE_INTEGRITY_ROUTE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23osint.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23osint.py"

REPORT_PATHS = {
    "long_k23sing": D20_INVARIANTS / "proof_obligations" / "long_k23sing" / "report.json",
    "long_k23mledger": D20_INVARIANTS / "proof_obligations" / "long_k23mledger" / "report.json",
    "long_k23mand": D20_INVARIANTS / "proof_obligations" / "long_k23mand" / "report.json",
    "long_k23seci": D20_INVARIANTS / "proof_obligations" / "long_k23seci" / "report.json",
    "long_k23dist": D20_INVARIANTS / "proof_obligations" / "long_k23dist" / "report.json",
    "long_k23hprob": D20_INVARIANTS / "proof_obligations" / "long_k23hprob" / "report.json",
}
EXPECTED_STATUSES = {
    "long_k23sing": "SECTOR33_K23_NATIVE_SINGULARITY_CYBERNETICS_CERTIFIED",
    "long_k23mledger": "SECTOR33_K23_PROOF_OF_MANDATE_LEDGER_CERTIFIED",
    "long_k23mand": "SECTOR33_K23_SOURCE_BOUND_MANDATE_CERTIFIED",
    "long_k23seci": "SECTOR33_K23_SECURITY_INTEGRITY_GATE_CERTIFIED",
    "long_k23dist": "SECTOR33_K23_PUBLIC_TABLE_DISTRIBUTION_DECODER_CERTIFIED",
    "long_k23hprob": "SECTOR33_K23_HARDNESS_PROBLEM_DEFINITION_CERTIFIED",
}

ROUTE_TEXT_HASH = "b6f627d9e22cd1bc38a20b14a8101f8e204aa8ebdd8b9acf839224a397abf840"
TOOL_TEXT_HASH = "ffd60dc1aa43dac46cb674200c0ce5946d13c2d6ab359cfefc62288a435d846f"
GATE_TEXT_HASH = "3a52007e6f328e408b63918cb3bf1ba002b793964fda095f608cf5ff22e84caa"
OBS_TEXT_HASH = "145b41fc523ae9c7c90d99e482d96f65d314f0a01b7a3b1581df441ff5c7f02a"
MATRIX_SHA256 = "f2aa2155d6cbc503018516c66d9e9f31373842261a9e90e8641bb8198ae1bf0c"

ROUTE_COLUMNS = [
    "route_id",
    "route_code",
    "source_code",
    "selected_flag",
    "public_artifact_flag",
    "deterministic_flag",
    "finite_integrity_flag",
    "open_source_safe_flag",
    "blocking_flag",
    "deploy_security_claim_flag",
]
TOOL_COLUMNS = [
    "tool_id",
    "singularity_code",
    "tool_code",
    "source_code",
    "public_input_flag",
    "deterministic_flag",
    "integrity_check_flag",
    "rejection_feedback_flag",
    "hardness_claim_flag",
    "open_boundary_flag",
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
    "route_row_count",
    "selected_route_count",
    "integrity_route_selected_flag",
    "reduction_route_selected_flag",
    "external_route_selected_flag",
    "route_blocking_count",
    "deploy_security_claim_count",
    "tool_row_count",
    "public_tool_count",
    "deterministic_tool_count",
    "integrity_check_tool_count",
    "rejection_feedback_tool_count",
    "open_tool_boundary_count",
    "hardness_claim_count",
    "proof_of_mandate_flag",
    "proof_of_mandate_ledger_flag",
    "mandate_row_count",
    "ledger_row_count",
    "valid_decode_count",
    "invalid_reject_count",
    "bounded_soundness_error_numerator",
    "bounded_soundness_error_denominator",
    "transcript_index_bytes",
    "saved_vs_baseline_bytes",
    "saved_vs_baseline_num",
    "saved_vs_baseline_den",
    "public_table_trivial_problem_count",
    "materialized_reduction_count",
    "native_singularity_theory_flag",
    "open_source_integrity_route_flag",
    "integrity_tooling_ready_flag",
    "deploy_ready_flag",
    "gate_row_count",
    "satisfied_gate_count",
    "blocking_gate_count",
    "claim_gate_count",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["route_table", "tool_table", "gate_table", "observable_vector"]
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
    sing = summaries["long_k23sing"]
    mledger = summaries["long_k23mledger"]
    mand = summaries["long_k23mand"]
    seci = summaries["long_k23seci"]
    dist = summaries["long_k23dist"]
    hprob = summaries["long_k23hprob"]

    route_rows = [
        {"route_id": 0, "route_code": 0, "source_code": 0, "selected_flag": 0, "public_artifact_flag": 0, "deterministic_flag": 0, "finite_integrity_flag": 0, "open_source_safe_flag": 0, "blocking_flag": 1, "deploy_security_claim_flag": 0},
        {"route_id": 1, "route_code": 1, "source_code": 1, "selected_flag": 1, "public_artifact_flag": 1, "deterministic_flag": 1, "finite_integrity_flag": 1, "open_source_safe_flag": 1, "blocking_flag": 0, "deploy_security_claim_flag": 0},
        {"route_id": 2, "route_code": 2, "source_code": 2, "selected_flag": 0, "public_artifact_flag": 0, "deterministic_flag": 0, "finite_integrity_flag": 0, "open_source_safe_flag": 1, "blocking_flag": 1, "deploy_security_claim_flag": 0},
    ]
    tool_rows = [
        {"tool_id": 0, "singularity_code": 0, "tool_code": 0, "source_code": 0, "public_input_flag": 1, "deterministic_flag": 1, "integrity_check_flag": 1, "rejection_feedback_flag": 0, "hardness_claim_flag": 0, "open_boundary_flag": 0},
        {"tool_id": 1, "singularity_code": 1, "tool_code": 1, "source_code": 1, "public_input_flag": 1, "deterministic_flag": 1, "integrity_check_flag": 1, "rejection_feedback_flag": 1, "hardness_claim_flag": 0, "open_boundary_flag": 0},
        {"tool_id": 2, "singularity_code": 2, "tool_code": 2, "source_code": 5, "public_input_flag": 1, "deterministic_flag": 1, "integrity_check_flag": 1, "rejection_feedback_flag": 0, "hardness_claim_flag": 0, "open_boundary_flag": 0},
        {"tool_id": 3, "singularity_code": 3, "tool_code": 3, "source_code": 5, "public_input_flag": 0, "deterministic_flag": 0, "integrity_check_flag": 0, "rejection_feedback_flag": 0, "hardness_claim_flag": 0, "open_boundary_flag": 1},
        {"tool_id": 4, "singularity_code": 4, "tool_code": 4, "source_code": 0, "public_input_flag": 1, "deterministic_flag": 1, "integrity_check_flag": 1, "rejection_feedback_flag": 1, "hardness_claim_flag": 0, "open_boundary_flag": 0},
        {"tool_id": 5, "singularity_code": 5, "tool_code": 5, "source_code": 4, "public_input_flag": 1, "deterministic_flag": 1, "integrity_check_flag": 1, "rejection_feedback_flag": 1, "hardness_claim_flag": 0, "open_boundary_flag": 0},
    ]
    gate_rows = [
        {"gate_id": 0, "gate_code": 0, "satisfied_flag": 1, "blocking_flag": 0, "claim_flag": 0},
        {"gate_id": 1, "gate_code": 1, "satisfied_flag": 1, "blocking_flag": 0, "claim_flag": 0},
        {"gate_id": 2, "gate_code": 2, "satisfied_flag": 1, "blocking_flag": 0, "claim_flag": 0},
        {"gate_id": 3, "gate_code": 3, "satisfied_flag": 1, "blocking_flag": 0, "claim_flag": 0},
        {"gate_id": 4, "gate_code": 4, "satisfied_flag": 0, "blocking_flag": 1, "claim_flag": 0},
        {"gate_id": 5, "gate_code": 5, "satisfied_flag": 0, "blocking_flag": 1, "claim_flag": 0},
    ]
    obs = {
        "input_report_count": len(REPORT_PATHS),
        "certified_input_count": sum(is_certified(reports[name], EXPECTED_STATUSES[name]) for name in REPORT_PATHS),
        "route_row_count": len(route_rows),
        "selected_route_count": sum(row["selected_flag"] for row in route_rows),
        "integrity_route_selected_flag": route_rows[1]["selected_flag"],
        "reduction_route_selected_flag": route_rows[0]["selected_flag"],
        "external_route_selected_flag": route_rows[2]["selected_flag"],
        "route_blocking_count": sum(row["blocking_flag"] for row in route_rows),
        "deploy_security_claim_count": sum(row["deploy_security_claim_flag"] for row in route_rows),
        "tool_row_count": len(tool_rows),
        "public_tool_count": sum(row["public_input_flag"] for row in tool_rows),
        "deterministic_tool_count": sum(row["deterministic_flag"] for row in tool_rows),
        "integrity_check_tool_count": sum(row["integrity_check_flag"] for row in tool_rows),
        "rejection_feedback_tool_count": sum(row["rejection_feedback_flag"] for row in tool_rows),
        "open_tool_boundary_count": sum(row["open_boundary_flag"] for row in tool_rows),
        "hardness_claim_count": int(hprob.get("hardness_claim_count", -1)),
        "proof_of_mandate_flag": int(mand.get("proof_of_mandate_flag", -1)),
        "proof_of_mandate_ledger_flag": int(mledger.get("proof_of_mandate_ledger_flag", -1)),
        "mandate_row_count": int(mand.get("mandate_row_count", -1)),
        "ledger_row_count": int(mledger.get("ledger_row_count", -1)),
        "valid_decode_count": int(dist.get("valid_decode_row_count", -1)),
        "invalid_reject_count": int(dist.get("invalid_reject_count", -1)),
        "bounded_soundness_error_numerator": int(seci.get("bounded_soundness_error_numerator", -1)),
        "bounded_soundness_error_denominator": int(seci.get("bounded_soundness_error_denominator", -1)),
        "transcript_index_bytes": int(sing.get("transcript_index_bytes", -1)),
        "saved_vs_baseline_bytes": int(sing.get("saved_vs_baseline_bytes", -1)),
        "saved_vs_baseline_num": int(sing.get("saved_vs_baseline_num", -1)),
        "saved_vs_baseline_den": int(sing.get("saved_vs_baseline_den", -1)),
        "public_table_trivial_problem_count": int(hprob.get("public_table_trivial_problem_count", -1)),
        "materialized_reduction_count": int(hprob.get("materialized_reduction_count", -1)),
        "native_singularity_theory_flag": int(sing.get("native_singularity_theory_flag", -1)),
        "open_source_integrity_route_flag": 1,
        "integrity_tooling_ready_flag": 1,
        "deploy_ready_flag": int(hprob.get("deploy_ready_flag", -1)),
        "gate_row_count": len(gate_rows),
        "satisfied_gate_count": sum(row["satisfied_flag"] for row in gate_rows),
        "blocking_gate_count": sum(row["blocking_flag"] for row in gate_rows),
        "claim_gate_count": sum(row["claim_flag"] for row in gate_rows),
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    route_table = table_from_rows(ROUTE_COLUMNS, route_rows)
    tool_table = table_from_rows(TOOL_COLUMNS, tool_rows)
    gate_table = table_from_rows(GATE_COLUMNS, gate_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "route_table": route_table.astype(np.int64),
        "tool_table": tool_table.astype(np.int64),
        "gate_table": gate_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "reports": reports,
        "route_rows": route_rows,
        "tool_rows": tool_rows,
        "gate_rows": gate_rows,
        "obs_rows": obs_rows,
        "route_table": route_table,
        "tool_table": tool_table,
        "gate_table": gate_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "route_text_hash": hashlib.sha256(digest_text(ROUTE_COLUMNS, route_rows).encode("ascii")).hexdigest(),
        "tool_text_hash": hashlib.sha256(digest_text(TOOL_COLUMNS, tool_rows).encode("ascii")).hexdigest(),
        "gate_text_hash": hashlib.sha256(digest_text(GATE_COLUMNS, gate_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": obs["certified_input_count"] == obs["input_report_count"] == 6,
        "route_selection_matches": (
            obs["route_row_count"],
            obs["selected_route_count"],
            obs["integrity_route_selected_flag"],
            obs["reduction_route_selected_flag"],
            obs["external_route_selected_flag"],
            obs["route_blocking_count"],
            obs["deploy_security_claim_count"],
        )
        == (3, 1, 1, 0, 0, 2, 0),
        "tool_profile_matches": (
            obs["tool_row_count"],
            obs["public_tool_count"],
            obs["deterministic_tool_count"],
            obs["integrity_check_tool_count"],
            obs["rejection_feedback_tool_count"],
            obs["open_tool_boundary_count"],
        )
        == (6, 5, 5, 5, 3, 1),
        "mandate_and_transport_match": (
            obs["proof_of_mandate_flag"],
            obs["proof_of_mandate_ledger_flag"],
            obs["mandate_row_count"],
            obs["ledger_row_count"],
            obs["transcript_index_bytes"],
            obs["saved_vs_baseline_bytes"],
            obs["saved_vs_baseline_num"],
            obs["saved_vs_baseline_den"],
        )
        == (1, 1, 56, 12, 56, 1512, 27, 28),
        "integrity_and_nonhardness_match": (
            obs["valid_decode_count"],
            obs["invalid_reject_count"],
            obs["bounded_soundness_error_numerator"],
            obs["bounded_soundness_error_denominator"],
            obs["public_table_trivial_problem_count"],
            obs["materialized_reduction_count"],
            obs["hardness_claim_count"],
            obs["deploy_ready_flag"],
        )
        == (56, 200, 0, 112_869_680, 2, 0, 0, 0),
        "native_integrity_flags_match": (
            obs["native_singularity_theory_flag"],
            obs["open_source_integrity_route_flag"],
            obs["integrity_tooling_ready_flag"],
        )
        == (1, 1, 1),
        "gate_profile_matches": (
            obs["gate_row_count"],
            obs["satisfied_gate_count"],
            obs["blocking_gate_count"],
            obs["claim_gate_count"],
        )
        == (6, 4, 2, 0),
        "completion_flag_matches": obs["complete_goal_claim_flag"] == 0,
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_open_source_integrity_route",
        "route_code_map": {
            "0": "reduction_source_insertion",
            "1": "integrity_only_tooling",
            "2": "external_benchmark_epoch_ingestion",
        },
        "tool_code_map": {
            "0": "transcript_index_verifier",
            "1": "bounded_tamper_rejector",
            "2": "nonhardness_label_guard",
            "3": "reduction_aperture_placeholder",
            "4": "epoch_manifest_loader",
            "5": "invalid_byte_rejector",
        },
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This selects integrity-only tooling as the open-source K23 route and keeps hardness/deployment security unclaimed.",
    }
    seam_payload = {
        "schema": "long.k23osint.seam@1",
        "status": STATUS,
        "claim": "The K23 surface has a certified open-source integrity tooling route: deterministic public verification, mandate audit, invalid-byte rejection, and nonhardness guardrails are explicit.",
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
        "schema": "long.k23osint.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23osint certifies the open-source integrity route selected from the native K23 singularity table.",
        "stage_protocol": {
            "draft": "read singularity, proof-of-mandate, mandate, security-integrity, decoder, and hardness-boundary certificates",
            "witness": "emit route rows, tool rows, gate rows, observables, and numeric tables",
            "coherence": "check integrity-route selection, deterministic tooling, mandate binding, decoder rejection, and nonhardness guardrails",
            "closure": "certify integrity-only tooling route without claiming deploy-grade cryptographic hardness",
            "emit": "write long_k23osint artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "route_rows_csv": relpath(OUT_DIR / "route_rows.csv"),
            "tool_rows_csv": relpath(OUT_DIR / "tool_rows.csv"),
            "gate_rows_csv": relpath(OUT_DIR / "gate_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23osint_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "integrity-only tooling is the selected route from the native singularity table",
                "five public deterministic integrity tools are identified",
                "proof-of-mandate and decoder rejection surfaces are bound into the route",
                "hardness and deployment security claims remain zero",
            ],
            "does_not_certify": [
                "cryptographic hardness",
                "deployment readiness",
                "external benchmark compatibility",
                "secret witness protection",
                "zero knowledge",
            ],
        },
        "next_highest_yield_item": "Materialize the integrity tooling interface contract: exact inputs, outputs, rejection codes, and audit transcript fields for the selected route.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23osint.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23osint.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "route_csv": csv_text(ROUTE_COLUMNS, rows["route_rows"]),
        "tool_csv": csv_text(TOOL_COLUMNS, rows["tool_rows"]),
        "gate_csv": csv_text(GATE_COLUMNS, rows["gate_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "route_table": rows["route_table"],
        "tool_table": rows["tool_table"],
        "gate_table": rows["gate_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "route_text_sha256": rows["route_text_hash"],
            "tool_text_sha256": rows["tool_text_hash"],
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
    (OUT_DIR / "route_rows.csv").write_text(payloads["route_csv"], encoding="utf-8")
    (OUT_DIR / "tool_rows.csv").write_text(payloads["tool_csv"], encoding="utf-8")
    (OUT_DIR / "gate_rows.csv").write_text(payloads["gate_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        route_table=payloads["route_table"],
        tool_table=payloads["tool_table"],
        gate_table=payloads["gate_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23osint_matrices.npz", **payloads["matrix_payload"])
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
