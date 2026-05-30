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


THEOREM_ID = "long_k23crypt"
STATUS = "SECTOR33_K23_CRYPTOLOGIC_POTENTIAL_FRONTIER_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23crypt.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23crypt.py"

REPORT_PATHS = {
    "long_k23pot": D20_INVARIANTS / "proof_obligations" / "long_k23pot" / "report.json",
    "long_k23bench": D20_INVARIANTS / "proof_obligations" / "long_k23bench" / "report.json",
    "long_k23norm": D20_INVARIANTS / "proof_obligations" / "long_k23norm" / "report.json",
    "long_k23wire": D20_INVARIANTS / "proof_obligations" / "long_k23wire" / "report.json",
    "long_k23wdep": D20_INVARIANTS / "proof_obligations" / "long_k23wdep" / "report.json",
    "long_k23audit": D20_INVARIANTS / "proof_obligations" / "long_k23audit" / "report.json",
    "long_k23vwork": D20_INVARIANTS / "proof_obligations" / "long_k23vwork" / "report.json",
    "long_k23sound": D20_INVARIANTS / "proof_obligations" / "long_k23sound" / "report.json",
    "long_k23auth": D20_INVARIANTS / "proof_obligations" / "long_k23auth" / "report.json",
    "long_k23sdet": D20_INVARIANTS / "proof_obligations" / "long_k23sdet" / "report.json",
}
EXPECTED_STATUSES = {
    "long_k23pot": "SECTOR33_K23_PRODUCTIVE_POTENTIAL_CANDIDATES_CERTIFIED",
    "long_k23bench": "SECTOR33_K23_BENCHMARK_SURFACE_CERTIFIED",
    "long_k23norm": "SECTOR33_K23_MLKEM512_NORMALIZATION_CERTIFIED",
    "long_k23wire": "SECTOR33_K23_COMPACT_WIRE_MAP_CERTIFIED",
    "long_k23wdep": "SECTOR33_K23_WIRE_DEPENDENCY_DECISION_CERTIFIED",
    "long_k23audit": "SECTOR33_K23_LOCAL_AUDIT_COST_CERTIFIED",
    "long_k23vwork": "SECTOR33_K23_VERIFIER_WORKLOAD_BINDING_CERTIFIED",
    "long_k23sound": "SECTOR33_K23_BOUNDED_ADVERSARY_SOUNDNESS_CERTIFIED",
    "long_k23auth": "SECTOR33_K23_FINITE_AUTHORITY_CLOSURE_CERTIFIED",
    "long_k23sdet": "SECTOR33_K23_SUPERDETERMINISTIC_CRYPTOLOGIC_BOUNDARY_CERTIFIED",
}

FRONTIER_TEXT_HASH = "dbd1ebae15f933e644de581f96ac1fa5d19626aeec85be2119eb336954fad7d4"
SCORE_TEXT_HASH = "8b95c76ccaaa813d53305a2472443c47c5bdbc82618f8f8106f84bf30a862db5"
LIMIT_TEXT_HASH = "5e90de64cae125541b7a4fcc96055259ed106c90c61afb8278d445ca487438a9"
OBS_TEXT_HASH = "480311ada2c02f9a3ec4eb35f6a4043bc8e62764a3ad9c1248caf9e7b0582397"
MATRIX_SHA256 = "e8275e359551beaa0ee0957b15f4c8cb5bfa097705d7c54359422feece4fa2fa"

FRONTIER_COLUMNS = [
    "frontier_id",
    "frontier_code",
    "evidence_source_code",
    "efficiency_axis_flag",
    "security_axis_flag",
    "existing_spec_axis_flag",
    "local_evidence_flag",
    "external_baseline_flag",
    "blocker_count",
    "external_improvement_claim_flag",
    "security_superiority_claim_flag",
    "productive_frontier_flag",
]
SCORE_COLUMNS = [
    "score_id",
    "frontier_id",
    "efficiency_signal",
    "security_signal",
    "baseline_signal",
    "dependency_penalty",
    "proof_gap_penalty",
    "claim_penalty",
    "ready_for_external_claim_flag",
    "productive_score",
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
    "frontier_row_count",
    "efficiency_frontier_count",
    "security_frontier_count",
    "existing_spec_frontier_count",
    "local_evidence_count",
    "external_baseline_count",
    "blocker_total",
    "external_improvement_claim_count",
    "security_superiority_claim_count",
    "productive_frontier_count",
    "score_row_count",
    "efficiency_signal_total",
    "security_signal_total",
    "baseline_signal_total",
    "productive_score_total",
    "ready_for_external_claim_count",
    "limit_row_count",
    "open_limit_count",
    "required_before_external_claim_count",
    "overclaim_count",
    "spec_anchor_count",
    "official_spec_anchor_count",
    "external_numeric_baseline_count",
    "baseline_public_exchange_bytes",
    "wire_total_bytes",
    "current_model_self_contained_bytes",
    "local_audit_total_bytes",
    "digest_surface_total_bytes",
    "saved_audit_total_bytes",
    "local_bytes_per_game_num",
    "local_bytes_per_game_den",
    "bounded_soundness_error_numerator",
    "bounded_soundness_error_denominator",
    "false_accept_strategy_words",
    "external_randomness_claim_count",
    "zero_knowledge_claim_flag",
    "hardness_claim_flag",
    "public_transport_claim_count",
    "external_efficiency_path_demoted_count",
    "productive_potential_flag",
    "cryptologic_frontier_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["frontier_table", "score_table", "limit_table", "observable_vector"]
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
    certified = {name: is_certified(reports[name], EXPECTED_STATUSES[name]) for name in REPORT_PATHS}
    pot = summaries["long_k23pot"]
    norm = summaries["long_k23norm"]
    wire = summaries["long_k23wire"]
    wdep = summaries["long_k23wdep"]
    audit = summaries["long_k23audit"]
    vwork = summaries["long_k23vwork"]
    sound = summaries["long_k23sound"]
    auth = summaries["long_k23auth"]
    sdet = summaries["long_k23sdet"]

    frontier_rows = [
        {"frontier_id": 0, "frontier_code": 0, "evidence_source_code": 0, "efficiency_axis_flag": 0, "security_axis_flag": 0, "existing_spec_axis_flag": 1, "local_evidence_flag": 1, "external_baseline_flag": 1, "blocker_count": 1, "external_improvement_claim_flag": 0, "security_superiority_claim_flag": 0, "productive_frontier_flag": 1},
        {"frontier_id": 1, "frontier_code": 1, "evidence_source_code": 1, "efficiency_axis_flag": 1, "security_axis_flag": 1, "existing_spec_axis_flag": 1, "local_evidence_flag": 1, "external_baseline_flag": 1, "blocker_count": 7, "external_improvement_claim_flag": 0, "security_superiority_claim_flag": 0, "productive_frontier_flag": 1},
        {"frontier_id": 2, "frontier_code": 2, "evidence_source_code": 2, "efficiency_axis_flag": 1, "security_axis_flag": 0, "existing_spec_axis_flag": 1, "local_evidence_flag": 1, "external_baseline_flag": 1, "blocker_count": 5, "external_improvement_claim_flag": 0, "security_superiority_claim_flag": 0, "productive_frontier_flag": 1},
        {"frontier_id": 3, "frontier_code": 3, "evidence_source_code": 3, "efficiency_axis_flag": 1, "security_axis_flag": 0, "existing_spec_axis_flag": 1, "local_evidence_flag": 1, "external_baseline_flag": 1, "blocker_count": 3, "external_improvement_claim_flag": 0, "security_superiority_claim_flag": 0, "productive_frontier_flag": 1},
        {"frontier_id": 4, "frontier_code": 4, "evidence_source_code": 4, "efficiency_axis_flag": 0, "security_axis_flag": 1, "existing_spec_axis_flag": 0, "local_evidence_flag": 1, "external_baseline_flag": 0, "blocker_count": 4, "external_improvement_claim_flag": 0, "security_superiority_claim_flag": 0, "productive_frontier_flag": 1},
        {"frontier_id": 5, "frontier_code": 5, "evidence_source_code": 5, "efficiency_axis_flag": 1, "security_axis_flag": 1, "existing_spec_axis_flag": 0, "local_evidence_flag": 1, "external_baseline_flag": 0, "blocker_count": 4, "external_improvement_claim_flag": 0, "security_superiority_claim_flag": 0, "productive_frontier_flag": 1},
    ]
    score_rows = []
    for row in frontier_rows:
        efficiency_signal = row["efficiency_axis_flag"] * row["local_evidence_flag"]
        security_signal = row["security_axis_flag"] * row["local_evidence_flag"]
        baseline_signal = row["existing_spec_axis_flag"] * row["external_baseline_flag"]
        claim_penalty = row["external_improvement_claim_flag"] + row["security_superiority_claim_flag"]
        score_rows.append(
            {
                "score_id": row["frontier_id"],
                "frontier_id": row["frontier_id"],
                "efficiency_signal": efficiency_signal,
                "security_signal": security_signal,
                "baseline_signal": baseline_signal,
                "dependency_penalty": int(row["blocker_count"] > 0),
                "proof_gap_penalty": int(row["blocker_count"] > 0),
                "claim_penalty": claim_penalty,
                "ready_for_external_claim_flag": int(row["blocker_count"] == 0 and claim_penalty == 0),
                "productive_score": efficiency_signal + security_signal + baseline_signal - claim_penalty,
            }
        )
    limit_rows = [
        {"limit_id": 0, "limit_code": 0, "open_flag": 1, "required_before_external_claim_flag": 1, "overclaim_flag": 0},
        {"limit_id": 1, "limit_code": 1, "open_flag": 1, "required_before_external_claim_flag": 1, "overclaim_flag": 0},
        {"limit_id": 2, "limit_code": 2, "open_flag": 1, "required_before_external_claim_flag": 1, "overclaim_flag": 0},
        {"limit_id": 3, "limit_code": 3, "open_flag": 1, "required_before_external_claim_flag": 1, "overclaim_flag": 0},
        {"limit_id": 4, "limit_code": 4, "open_flag": 1, "required_before_external_claim_flag": 1, "overclaim_flag": 0},
        {"limit_id": 5, "limit_code": 5, "open_flag": 1, "required_before_external_claim_flag": 1, "overclaim_flag": 0},
        {"limit_id": 6, "limit_code": 6, "open_flag": 1, "required_before_external_claim_flag": 1, "overclaim_flag": 0},
        {"limit_id": 7, "limit_code": 7, "open_flag": 1, "required_before_external_claim_flag": 1, "overclaim_flag": 0},
    ]
    obs = {
        "input_report_count": len(REPORT_PATHS),
        "certified_input_count": sum(certified.values()),
        "frontier_row_count": len(frontier_rows),
        "efficiency_frontier_count": sum(row["efficiency_axis_flag"] for row in frontier_rows),
        "security_frontier_count": sum(row["security_axis_flag"] for row in frontier_rows),
        "existing_spec_frontier_count": sum(row["existing_spec_axis_flag"] for row in frontier_rows),
        "local_evidence_count": sum(row["local_evidence_flag"] for row in frontier_rows),
        "external_baseline_count": sum(row["external_baseline_flag"] for row in frontier_rows),
        "blocker_total": sum(row["blocker_count"] for row in frontier_rows),
        "external_improvement_claim_count": sum(row["external_improvement_claim_flag"] for row in frontier_rows),
        "security_superiority_claim_count": sum(row["security_superiority_claim_flag"] for row in frontier_rows),
        "productive_frontier_count": sum(row["productive_frontier_flag"] for row in frontier_rows),
        "score_row_count": len(score_rows),
        "efficiency_signal_total": sum(row["efficiency_signal"] for row in score_rows),
        "security_signal_total": sum(row["security_signal"] for row in score_rows),
        "baseline_signal_total": sum(row["baseline_signal"] for row in score_rows),
        "productive_score_total": sum(row["productive_score"] for row in score_rows),
        "ready_for_external_claim_count": sum(row["ready_for_external_claim_flag"] for row in score_rows),
        "limit_row_count": len(limit_rows),
        "open_limit_count": sum(row["open_flag"] for row in limit_rows),
        "required_before_external_claim_count": sum(row["required_before_external_claim_flag"] for row in limit_rows),
        "overclaim_count": sum(row["overclaim_flag"] for row in limit_rows),
        "spec_anchor_count": int(pot.get("spec_anchor_count", -1)),
        "official_spec_anchor_count": int(pot.get("official_spec_anchor_count", -1)),
        "external_numeric_baseline_count": int(norm.get("external_numeric_baseline_count", -1)),
        "baseline_public_exchange_bytes": int(norm.get("baseline_public_exchange_bytes", -1)),
        "wire_total_bytes": int(wire.get("wire_total_bytes", -1)),
        "current_model_self_contained_bytes": int(wdep.get("current_model_self_contained_bytes", -1)),
        "local_audit_total_bytes": int(vwork.get("local_audit_total_bytes", -1)),
        "digest_surface_total_bytes": int(vwork.get("digest_surface_total_bytes", -1)),
        "saved_audit_total_bytes": int(audit.get("saved_audit_total_bytes", -1)),
        "local_bytes_per_game_num": int(vwork.get("local_bytes_per_game_num", -1)),
        "local_bytes_per_game_den": int(vwork.get("local_bytes_per_game_den", -1)),
        "bounded_soundness_error_numerator": int(sound.get("bounded_soundness_error_numerator", -1)),
        "bounded_soundness_error_denominator": int(sound.get("bounded_soundness_error_denominator", -1)),
        "false_accept_strategy_words": int(auth.get("all_depth_false_accept_strategy_words", -1)),
        "external_randomness_claim_count": int(sdet.get("external_randomness_claim_count", -1)),
        "zero_knowledge_claim_flag": int(sound.get("zero_knowledge_claim_flag", -1)),
        "hardness_claim_flag": int(sound.get("hardness_claim_flag", -1)),
        "public_transport_claim_count": int(vwork.get("public_transport_claim_count", -1)),
        "external_efficiency_path_demoted_count": int(vwork.get("external_efficiency_path_demoted_count", -1)),
        "productive_potential_flag": int(pot.get("productive_potential_flag", -1)),
        "cryptologic_frontier_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    frontier_table = table_from_rows(FRONTIER_COLUMNS, frontier_rows)
    score_table = table_from_rows(SCORE_COLUMNS, score_rows)
    limit_table = table_from_rows(LIMIT_COLUMNS, limit_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "frontier_table": frontier_table.astype(np.int64),
        "score_table": score_table.astype(np.int64),
        "limit_table": limit_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "reports": reports,
        "frontier_rows": frontier_rows,
        "score_rows": score_rows,
        "limit_rows": limit_rows,
        "obs_rows": obs_rows,
        "frontier_table": frontier_table,
        "score_table": score_table,
        "limit_table": limit_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "frontier_text_hash": hashlib.sha256(digest_text(FRONTIER_COLUMNS, frontier_rows).encode("ascii")).hexdigest(),
        "score_text_hash": hashlib.sha256(digest_text(SCORE_COLUMNS, score_rows).encode("ascii")).hexdigest(),
        "limit_text_hash": hashlib.sha256(digest_text(LIMIT_COLUMNS, limit_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": obs["certified_input_count"] == 10,
        "frontier_profile_matches": (
            obs["frontier_row_count"],
            obs["efficiency_frontier_count"],
            obs["security_frontier_count"],
            obs["existing_spec_frontier_count"],
            obs["local_evidence_count"],
            obs["external_baseline_count"],
            obs["productive_frontier_count"],
        )
        == (6, 4, 3, 4, 6, 4, 6),
        "claim_boundaries_match": (
            obs["external_improvement_claim_count"],
            obs["security_superiority_claim_count"],
            obs["ready_for_external_claim_count"],
            obs["overclaim_count"],
            obs["complete_goal_claim_flag"],
        )
        == (0, 0, 0, 0, 0),
        "score_profile_matches": (
            obs["score_row_count"],
            obs["efficiency_signal_total"],
            obs["security_signal_total"],
            obs["baseline_signal_total"],
            obs["productive_score_total"],
        )
        == (6, 4, 3, 4, 11),
        "limit_profile_matches": (
            obs["limit_row_count"],
            obs["open_limit_count"],
            obs["required_before_external_claim_count"],
            obs["blocker_total"],
        )
        == (8, 8, 8, 24),
        "external_baseline_profile_matches": (
            obs["spec_anchor_count"],
            obs["official_spec_anchor_count"],
            obs["external_numeric_baseline_count"],
            obs["baseline_public_exchange_bytes"],
        )
        == (4, 4, 1, 1568),
        "efficiency_evidence_matches": (
            obs["wire_total_bytes"],
            obs["current_model_self_contained_bytes"],
            obs["local_audit_total_bytes"],
            obs["digest_surface_total_bytes"],
            obs["saved_audit_total_bytes"],
            obs["local_bytes_per_game_num"],
            obs["local_bytes_per_game_den"],
            obs["public_transport_claim_count"],
            obs["external_efficiency_path_demoted_count"],
        )
        == (224, 5376, 224, 5376, 5152, 2, 3, 0, 1),
        "security_evidence_matches": (
            obs["bounded_soundness_error_numerator"],
            obs["bounded_soundness_error_denominator"],
            obs["false_accept_strategy_words"],
            obs["external_randomness_claim_count"],
            obs["zero_knowledge_claim_flag"],
            obs["hardness_claim_flag"],
        )
        == (0, 112869680, 0, 0, 0, 0),
        "boundary_flags_match": (
            obs["productive_potential_flag"],
            obs["cryptologic_frontier_flag"],
        )
        == (1, 1),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_cryptologic_potential_frontier",
        "frontier_code_map": {
            "0": "existing_public_spec_anchor",
            "1": "candidate_inventory",
            "2": "normalized_benchmark_surface",
            "3": "shared_table_workload_efficiency",
            "4": "bounded_game_security_posture",
            "5": "deterministic_source_conditioning",
        },
        "limit_code_map": {
            "0": "external_runtime_benchmark",
            "1": "public_self_contained_wire_map",
            "2": "hardness_or_reduction_proof",
            "3": "probabilistic_soundness_model",
            "4": "zero_knowledge_proof",
            "5": "standards_interop_profile",
            "6": "constant_time_or_side_channel_profile",
            "7": "current_spec_update_audit",
        },
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This scores productive cryptologic potential against existing-spec anchors while keeping external improvement and security-superiority claims at zero.",
    }
    seam_payload = {
        "schema": "long.k23crypt.seam@1",
        "status": STATUS,
        "claim": "The K23 proof-of-mandate chain has typed cryptologic efficiency/security potential rows, with existing-spec comparison kept provisional.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        name: input_entry(
            path,
            {
                "status": rows["reports"][name].get("status"),
                "certificate_sha256": rows["reports"][name].get("certificate_sha256"),
            },
        )
        for name, path in REPORT_PATHS.items()
    }
    inputs["derive_script"] = input_entry(DERIVE_SCRIPT)
    inputs["validator"] = input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)}
    report = {
        "schema": "long.k23crypt.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23crypt certifies typed productive-potential frontier rows for cryptologic efficiency and security work.",
        "stage_protocol": {
            "draft": "read K23 potential, benchmark, normalization, wire, dependency, audit, workload, soundness, authority, and deterministic-source reports",
            "witness": "emit frontier rows, score rows, open limits, observables, and numeric tables",
            "coherence": "check input certification, potential axes, score totals, external baselines, efficiency evidence, security evidence, and nonclaims",
            "closure": "certify the productive-potential frontier without asserting external improvement or security superiority",
            "emit": "write long_k23crypt artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "frontier_rows_csv": relpath(OUT_DIR / "frontier_rows.csv"),
            "score_rows_csv": relpath(OUT_DIR / "score_rows.csv"),
            "limit_rows_csv": relpath(OUT_DIR / "limit_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23crypt_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "six typed cryptologic potential frontier rows exist",
                "four frontier rows carry an efficiency axis and three carry a security axis",
                "four frontier rows are tied to existing-spec comparison anchors",
                "local verifier-side audit/workload efficiency evidence is present under the shared-table condition",
                "bounded finite-game security-posture evidence is present with zero false-accept strategy words in the certified bounded model",
            ],
            "does_not_certify": [
                "external speed or size improvement",
                "security superiority",
                "cryptographic hardness",
                "zero knowledge",
                "probabilistic or unbounded soundness",
                "public self-contained transport efficiency",
                "standards compliance",
                "deployment readiness",
                "completion of the active discovery goal",
            ],
        },
        "next_highest_yield_item": "Choose the next comparison-ready branch: either remove the shared-table dependency for a public wire claim or emit a dedicated threat-model/hardness frontier for the security axis.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23crypt.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23crypt.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "frontier_csv": csv_text(FRONTIER_COLUMNS, rows["frontier_rows"]),
        "score_csv": csv_text(SCORE_COLUMNS, rows["score_rows"]),
        "limit_csv": csv_text(LIMIT_COLUMNS, rows["limit_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "frontier_table": rows["frontier_table"],
        "score_table": rows["score_table"],
        "limit_table": rows["limit_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "frontier_text_sha256": rows["frontier_text_hash"],
            "score_text_sha256": rows["score_text_hash"],
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
    (OUT_DIR / "frontier_rows.csv").write_text(payloads["frontier_csv"], encoding="utf-8")
    (OUT_DIR / "score_rows.csv").write_text(payloads["score_csv"], encoding="utf-8")
    (OUT_DIR / "limit_rows.csv").write_text(payloads["limit_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        frontier_table=payloads["frontier_table"],
        score_table=payloads["score_table"],
        limit_table=payloads["limit_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23crypt_matrices.npz", **payloads["matrix_payload"])
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
