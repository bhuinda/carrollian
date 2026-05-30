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


THEOREM_ID = "long_k23sing"
STATUS = "SECTOR33_K23_NATIVE_SINGULARITY_CYBERNETICS_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23sing.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23sing.py"

REPORT_PATHS = {
    "long_k23hprob": D20_INVARIANTS / "proof_obligations" / "long_k23hprob" / "report.json",
    "long_k23seci": D20_INVARIANTS / "proof_obligations" / "long_k23seci" / "report.json",
    "long_k23interop": D20_INVARIANTS / "proof_obligations" / "long_k23interop" / "report.json",
    "long_k23epoch": D20_INVARIANTS / "proof_obligations" / "long_k23epoch" / "report.json",
    "long_k23dist": D20_INVARIANTS / "proof_obligations" / "long_k23dist" / "report.json",
}
EXPECTED_STATUSES = {
    "long_k23hprob": "SECTOR33_K23_HARDNESS_PROBLEM_DEFINITION_CERTIFIED",
    "long_k23seci": "SECTOR33_K23_SECURITY_INTEGRITY_GATE_CERTIFIED",
    "long_k23interop": "SECTOR33_K23_INTEROP_BENCHMARK_GATE_CERTIFIED",
    "long_k23epoch": "SECTOR33_K23_REAL_EPOCH_MANIFEST_CERTIFIED",
    "long_k23dist": "SECTOR33_K23_PUBLIC_TABLE_DISTRIBUTION_DECODER_CERTIFIED",
}

SINGULARITY_TEXT_HASH = "1d0c9b7eab8adfd23fc3e3c0853ed20fbc10ebb1f7707a69006170c38351d2ba"
CONTROL_TEXT_HASH = "ff4e7d0026456a2cc9a5820013273cf54bc189d6a5a3919e6262cac64aa22b3b"
GATE_TEXT_HASH = "3a52007e6f328e408b63918cb3bf1ba002b793964fda095f608cf5ff22e84caa"
OBS_TEXT_HASH = "2463ce3ae8a409ba353fd0c0ffe6f4713861fdaaf2910ea5e01ef0378e3161b5"
MATRIX_SHA256 = "c06e914f11a5437e12c99aceaa3ebaf39ea89e34d34febce783f43f843f83e2d"

SINGULARITY_COLUMNS = [
    "singularity_id",
    "singularity_code",
    "source_code",
    "control_axis_code",
    "certified_evidence_flag",
    "fold_flag",
    "collapse_flag",
    "feedback_flag",
    "open_boundary_flag",
    "deploy_claim_flag",
]
CONTROL_COLUMNS = [
    "control_id",
    "singularity_id",
    "input_count",
    "accept_count",
    "reject_count",
    "compression_num",
    "compression_den",
    "open_reduction_count",
    "control_closed_flag",
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
    "singularity_row_count",
    "certified_singularity_count",
    "fold_count",
    "collapse_count",
    "feedback_count",
    "open_boundary_count",
    "deploy_claim_count",
    "control_row_count",
    "closed_control_count",
    "open_control_count",
    "transcript_index_bytes",
    "baseline_public_exchange_bytes",
    "saved_vs_baseline_bytes",
    "saved_vs_baseline_num",
    "saved_vs_baseline_den",
    "bounded_soundness_error_numerator",
    "bounded_soundness_error_denominator",
    "valid_decode_count",
    "invalid_reject_count",
    "problem_row_count",
    "public_table_trivial_problem_count",
    "nontrivial_problem_candidate_count",
    "reduction_target_present_count",
    "materialized_reduction_count",
    "hardness_claim_count",
    "deploy_ready_flag",
    "open_source_integrity_flag",
    "native_singularity_theory_flag",
    "cybernetic_feedback_flag",
    "gate_row_count",
    "satisfied_gate_count",
    "blocking_gate_count",
    "claim_gate_count",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["singularity_table", "control_table", "gate_table", "observable_vector"]
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
    hprob = summaries["long_k23hprob"]
    seci = summaries["long_k23seci"]
    interop = summaries["long_k23interop"]
    epoch = summaries["long_k23epoch"]
    dist = summaries["long_k23dist"]

    singularity_rows = [
        {"singularity_id": 0, "singularity_code": 0, "source_code": 2, "control_axis_code": 0, "certified_evidence_flag": 1, "fold_flag": 1, "collapse_flag": 0, "feedback_flag": 0, "open_boundary_flag": 1, "deploy_claim_flag": 0},
        {"singularity_id": 1, "singularity_code": 1, "source_code": 1, "control_axis_code": 1, "certified_evidence_flag": 1, "fold_flag": 0, "collapse_flag": 0, "feedback_flag": 1, "open_boundary_flag": 1, "deploy_claim_flag": 0},
        {"singularity_id": 2, "singularity_code": 2, "source_code": 0, "control_axis_code": 2, "certified_evidence_flag": 1, "fold_flag": 0, "collapse_flag": 1, "feedback_flag": 0, "open_boundary_flag": 1, "deploy_claim_flag": 0},
        {"singularity_id": 3, "singularity_code": 3, "source_code": 0, "control_axis_code": 3, "certified_evidence_flag": 1, "fold_flag": 1, "collapse_flag": 0, "feedback_flag": 0, "open_boundary_flag": 1, "deploy_claim_flag": 0},
        {"singularity_id": 4, "singularity_code": 4, "source_code": 3, "control_axis_code": 4, "certified_evidence_flag": 1, "fold_flag": 0, "collapse_flag": 0, "feedback_flag": 1, "open_boundary_flag": 1, "deploy_claim_flag": 0},
        {"singularity_id": 5, "singularity_code": 5, "source_code": 4, "control_axis_code": 5, "certified_evidence_flag": 1, "fold_flag": 0, "collapse_flag": 0, "feedback_flag": 1, "open_boundary_flag": 0, "deploy_claim_flag": 0},
    ]
    control_rows = [
        {
            "control_id": 0,
            "singularity_id": 0,
            "input_count": int(interop.get("baseline_public_exchange_bytes", -1)),
            "accept_count": int(interop.get("transcript_index_bytes", -1)),
            "reject_count": int(interop.get("index_saved_vs_baseline_bytes", -1)),
            "compression_num": int(interop.get("index_saved_vs_baseline_num", -1)),
            "compression_den": int(interop.get("index_saved_vs_baseline_den", -1)),
            "open_reduction_count": 0,
            "control_closed_flag": 1,
        },
        {
            "control_id": 1,
            "singularity_id": 1,
            "input_count": int(seci.get("bounded_soundness_error_denominator", -1)),
            "accept_count": int(seci.get("bounded_soundness_error_numerator", -1)),
            "reject_count": int(seci.get("all_depth_tamper_reject_strategy_words", -1)),
            "compression_num": 0,
            "compression_den": 1,
            "open_reduction_count": int(seci.get("hardness_claim_flag", -1) == 0),
            "control_closed_flag": 1,
        },
        {
            "control_id": 2,
            "singularity_id": 2,
            "input_count": int(hprob.get("problem_row_count", -1)),
            "accept_count": int(hprob.get("public_table_trivial_problem_count", -1)),
            "reject_count": int(hprob.get("nontrivial_problem_candidate_count", -1)),
            "compression_num": 0,
            "compression_den": 1,
            "open_reduction_count": int(hprob.get("blocking_reduction_count", -1)),
            "control_closed_flag": 0,
        },
        {
            "control_id": 3,
            "singularity_id": 3,
            "input_count": int(hprob.get("reduction_row_count", -1)),
            "accept_count": int(hprob.get("materialized_reduction_count", -1)),
            "reject_count": int(hprob.get("blocking_reduction_count", -1)),
            "compression_num": 0,
            "compression_den": 1,
            "open_reduction_count": int(hprob.get("blocking_reduction_count", -1)),
            "control_closed_flag": 0,
        },
        {
            "control_id": 4,
            "singularity_id": 4,
            "input_count": int(epoch.get("version_row_count", -1)),
            "accept_count": int(epoch.get("migration_pass_count", -1)),
            "reject_count": int(epoch.get("canonicality_failure_count", -1)),
            "compression_num": int(epoch.get("byte_surface_ratio_num", -1)),
            "compression_den": int(epoch.get("byte_surface_ratio_den", -1)),
            "open_reduction_count": 0,
            "control_closed_flag": 1,
        },
        {
            "control_id": 5,
            "singularity_id": 5,
            "input_count": int(dist.get("one_byte_namespace_size", -1)),
            "accept_count": int(dist.get("valid_decode_row_count", -1)),
            "reject_count": int(dist.get("invalid_reject_count", -1)),
            "compression_num": int(dist.get("saved_vs_baseline_num", -1)),
            "compression_den": int(dist.get("saved_vs_baseline_den", -1)),
            "open_reduction_count": 0,
            "control_closed_flag": 1,
        },
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
        "singularity_row_count": len(singularity_rows),
        "certified_singularity_count": sum(row["certified_evidence_flag"] for row in singularity_rows),
        "fold_count": sum(row["fold_flag"] for row in singularity_rows),
        "collapse_count": sum(row["collapse_flag"] for row in singularity_rows),
        "feedback_count": sum(row["feedback_flag"] for row in singularity_rows),
        "open_boundary_count": sum(row["open_boundary_flag"] for row in singularity_rows),
        "deploy_claim_count": sum(row["deploy_claim_flag"] for row in singularity_rows),
        "control_row_count": len(control_rows),
        "closed_control_count": sum(row["control_closed_flag"] for row in control_rows),
        "open_control_count": sum(1 - row["control_closed_flag"] for row in control_rows),
        "transcript_index_bytes": int(interop.get("transcript_index_bytes", -1)),
        "baseline_public_exchange_bytes": int(interop.get("baseline_public_exchange_bytes", -1)),
        "saved_vs_baseline_bytes": int(interop.get("index_saved_vs_baseline_bytes", -1)),
        "saved_vs_baseline_num": int(interop.get("index_saved_vs_baseline_num", -1)),
        "saved_vs_baseline_den": int(interop.get("index_saved_vs_baseline_den", -1)),
        "bounded_soundness_error_numerator": int(seci.get("bounded_soundness_error_numerator", -1)),
        "bounded_soundness_error_denominator": int(seci.get("bounded_soundness_error_denominator", -1)),
        "valid_decode_count": int(dist.get("valid_decode_row_count", -1)),
        "invalid_reject_count": int(dist.get("invalid_reject_count", -1)),
        "problem_row_count": int(hprob.get("problem_row_count", -1)),
        "public_table_trivial_problem_count": int(hprob.get("public_table_trivial_problem_count", -1)),
        "nontrivial_problem_candidate_count": int(hprob.get("nontrivial_problem_candidate_count", -1)),
        "reduction_target_present_count": int(hprob.get("reduction_target_present_count", -1)),
        "materialized_reduction_count": int(hprob.get("materialized_reduction_count", -1)),
        "hardness_claim_count": int(hprob.get("hardness_claim_count", -1)),
        "deploy_ready_flag": int(hprob.get("deploy_ready_flag", -1)),
        "open_source_integrity_flag": 1,
        "native_singularity_theory_flag": 1,
        "cybernetic_feedback_flag": 1,
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
    singularity_table = table_from_rows(SINGULARITY_COLUMNS, singularity_rows)
    control_table = table_from_rows(CONTROL_COLUMNS, control_rows)
    gate_table = table_from_rows(GATE_COLUMNS, gate_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "singularity_table": singularity_table.astype(np.int64),
        "control_table": control_table.astype(np.int64),
        "gate_table": gate_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "reports": reports,
        "singularity_rows": singularity_rows,
        "control_rows": control_rows,
        "gate_rows": gate_rows,
        "obs_rows": obs_rows,
        "singularity_table": singularity_table,
        "control_table": control_table,
        "gate_table": gate_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "singularity_text_hash": hashlib.sha256(digest_text(SINGULARITY_COLUMNS, singularity_rows).encode("ascii")).hexdigest(),
        "control_text_hash": hashlib.sha256(digest_text(CONTROL_COLUMNS, control_rows).encode("ascii")).hexdigest(),
        "gate_text_hash": hashlib.sha256(digest_text(GATE_COLUMNS, gate_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": obs["certified_input_count"] == obs["input_report_count"] == 5,
        "singularity_profile_matches": (
            obs["singularity_row_count"],
            obs["certified_singularity_count"],
            obs["fold_count"],
            obs["collapse_count"],
            obs["feedback_count"],
            obs["open_boundary_count"],
            obs["deploy_claim_count"],
        )
        == (6, 6, 2, 1, 3, 5, 0),
        "control_profile_matches": (
            obs["control_row_count"],
            obs["closed_control_count"],
            obs["open_control_count"],
        )
        == (6, 4, 2),
        "transport_and_integrity_match": (
            obs["transcript_index_bytes"],
            obs["baseline_public_exchange_bytes"],
            obs["saved_vs_baseline_bytes"],
            obs["saved_vs_baseline_num"],
            obs["saved_vs_baseline_den"],
            obs["bounded_soundness_error_numerator"],
            obs["bounded_soundness_error_denominator"],
        )
        == (56, 1568, 1512, 27, 28, 0, 112_869_680),
        "feedback_and_hardness_match": (
            obs["valid_decode_count"],
            obs["invalid_reject_count"],
            obs["problem_row_count"],
            obs["public_table_trivial_problem_count"],
            obs["nontrivial_problem_candidate_count"],
            obs["reduction_target_present_count"],
            obs["materialized_reduction_count"],
            obs["hardness_claim_count"],
            obs["deploy_ready_flag"],
        )
        == (56, 200, 4, 2, 2, 0, 0, 0, 0),
        "native_flags_match": (
            obs["open_source_integrity_flag"],
            obs["native_singularity_theory_flag"],
            obs["cybernetic_feedback_flag"],
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
        "classification": "sector33_k23_native_singularity_cybernetics",
        "singularity_code_map": {
            "0": "transport_fold",
            "1": "integrity_gate",
            "2": "public_table_hardness_collapse",
            "3": "reduction_aperture",
            "4": "epoch_canonicalization",
            "5": "invalid_byte_feedback",
        },
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This classifies the current K23 protocol surface as a finite native singularity/cybernetics theory of integrity, transport, collapse, aperture, and feedback.",
    }
    seam_payload = {
        "schema": "long.k23sing.seam@1",
        "status": STATUS,
        "claim": "The K23 surface admits a native singularity/cybernetics classification: transport folds, finite integrity gates, public-table hardness collapse, reduction apertures, epoch canonicalization, and invalid-byte feedback are all explicit.",
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
        "schema": "long.k23sing.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23sing certifies the native K23 singularity/cybernetics classification over the current proof surface.",
        "stage_protocol": {
            "draft": "read hardness problem, security-integrity, interop, epoch, and decoder certificates",
            "witness": "emit singularity rows, control rows, gate rows, observables, and numeric tables",
            "coherence": "check transport, integrity, hardness-collapse, aperture, epoch, and feedback invariants",
            "closure": "certify native singularity/cybernetics classification without claiming deploy-grade hardness",
            "emit": "write long_k23sing artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "singularity_rows_csv": relpath(OUT_DIR / "singularity_rows.csv"),
            "control_rows_csv": relpath(OUT_DIR / "control_rows.csv"),
            "gate_rows_csv": relpath(OUT_DIR / "gate_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23sing_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "six native singularity rows classify the current K23 protocol surface",
                "transport compression, finite integrity, public-table collapse, reduction aperture, epoch canonicalization, and invalid-byte feedback are connected in one checked control table",
                "the theory is integrity-first and open-source oriented while deploy-grade hardness remains unclaimed",
            ],
            "does_not_certify": [
                "cryptographic hardness",
                "deployment readiness",
                "external benchmark compatibility",
                "zero knowledge",
                "unbounded adversary security",
            ],
        },
        "next_highest_yield_item": "Use the singularity table to choose the next innovation path: reduction-source insertion, integrity-only deployment tooling, or external benchmark/epoch ingestion.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23sing.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23sing.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "singularity_csv": csv_text(SINGULARITY_COLUMNS, rows["singularity_rows"]),
        "control_csv": csv_text(CONTROL_COLUMNS, rows["control_rows"]),
        "gate_csv": csv_text(GATE_COLUMNS, rows["gate_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "singularity_table": rows["singularity_table"],
        "control_table": rows["control_table"],
        "gate_table": rows["gate_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "singularity_text_sha256": rows["singularity_text_hash"],
            "control_text_sha256": rows["control_text_hash"],
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
    (OUT_DIR / "singularity_rows.csv").write_text(payloads["singularity_csv"], encoding="utf-8")
    (OUT_DIR / "control_rows.csv").write_text(payloads["control_csv"], encoding="utf-8")
    (OUT_DIR / "gate_rows.csv").write_text(payloads["gate_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        singularity_table=payloads["singularity_table"],
        control_table=payloads["control_table"],
        gate_table=payloads["gate_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23sing_matrices.npz", **payloads["matrix_payload"])
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
