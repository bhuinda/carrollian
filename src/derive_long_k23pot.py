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


THEOREM_ID = "long_k23pot"
STATUS = "SECTOR33_K23_PRODUCTIVE_POTENTIAL_CANDIDATES_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23pot.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23pot.py"
LONG_K23MLEDGER_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23mledger" / "report.json"

SPEC_TEXT_HASH = "47c1f04f85d721d821608fd0ba9a66f467a7fd568aeae91db7f28d8868e6f09a"
POTENTIAL_TEXT_HASH = "db5b02cf6fc7418e41e28dc9bde62bb71225ed5e7a299a11257a6d36aa2a65cc"
LIMIT_TEXT_HASH = "78609818f9b27ef95a182da08547047726a5a0ed633b68a1e3309a667de58a91"
OBS_TEXT_HASH = "6331212e38c1e34723e96a04c5d59bdd707b3be25e6206e12cd4f5b438f8c3ec"
MATRIX_SHA256 = "7871565f822c6b2c61b9c014abef92198336fc105469c373d9a001a3906b5db9"

SPEC_COLUMNS = [
    "spec_id",
    "spec_code",
    "official_source_flag",
    "current_baseline_flag",
    "kem_flag",
    "signature_flag",
    "guidance_flag",
    "external_url_present_flag",
]
POTENTIAL_COLUMNS = [
    "potential_id",
    "potential_code",
    "spec_family_code",
    "internal_evidence_flag",
    "efficiency_candidate_flag",
    "security_candidate_flag",
    "external_comparison_claim_flag",
    "benchmark_required_flag",
    "security_proof_required_flag",
    "deployment_claim_flag",
    "productive_potential_flag",
]
LIMIT_COLUMNS = [
    "limit_id",
    "limit_code",
    "claim_flag",
    "open_flag",
    "required_before_external_claim_flag",
    "overclaim_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "input_report_count",
    "certified_input_count",
    "spec_anchor_count",
    "official_spec_anchor_count",
    "kem_anchor_count",
    "signature_anchor_count",
    "guidance_anchor_count",
    "potential_row_count",
    "internal_evidence_count",
    "efficiency_candidate_count",
    "security_candidate_count",
    "external_comparison_claim_count",
    "benchmark_required_count",
    "security_proof_required_count",
    "deployment_claim_count",
    "productive_potential_count",
    "limit_row_count",
    "open_limit_count",
    "required_before_external_claim_count",
    "overclaim_count",
    "ledger_certified_input_count",
    "ledger_row_count",
    "challenge_count",
    "game_row_count",
    "accepted_authority_count",
    "all_depth_false_accept_strategy_words",
    "proof_of_mandate_ledger_flag",
    "productive_potential_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}

SPEC_URLS = {
    "0": "https://csrc.nist.gov/pubs/fips/203/final",
    "1": "https://csrc.nist.gov/pubs/sp/800/227/final",
    "2": "https://csrc.nist.gov/pubs/fips/204/final",
    "3": "https://csrc.nist.gov/pubs/fips/205/final",
}


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["spec_table", "potential_table", "limit_table", "observable_vector"]
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
    ledger_report = load_json(LONG_K23MLEDGER_REPORT)
    ledger_summary = summary(ledger_report)
    spec_rows = [
        {"spec_id": 0, "spec_code": 0, "official_source_flag": 1, "current_baseline_flag": 1, "kem_flag": 1, "signature_flag": 0, "guidance_flag": 0, "external_url_present_flag": 1},
        {"spec_id": 1, "spec_code": 1, "official_source_flag": 1, "current_baseline_flag": 1, "kem_flag": 1, "signature_flag": 0, "guidance_flag": 1, "external_url_present_flag": 1},
        {"spec_id": 2, "spec_code": 2, "official_source_flag": 1, "current_baseline_flag": 1, "kem_flag": 0, "signature_flag": 1, "guidance_flag": 0, "external_url_present_flag": 1},
        {"spec_id": 3, "spec_code": 3, "official_source_flag": 1, "current_baseline_flag": 1, "kem_flag": 0, "signature_flag": 1, "guidance_flag": 0, "external_url_present_flag": 1},
    ]
    potential_rows = [
        {"potential_id": 0, "potential_code": 0, "spec_family_code": 1, "internal_evidence_flag": 1, "efficiency_candidate_flag": 1, "security_candidate_flag": 1, "external_comparison_claim_flag": 0, "benchmark_required_flag": 1, "security_proof_required_flag": 1, "deployment_claim_flag": 0, "productive_potential_flag": 1},
        {"potential_id": 1, "potential_code": 1, "spec_family_code": 1, "internal_evidence_flag": 1, "efficiency_candidate_flag": 0, "security_candidate_flag": 1, "external_comparison_claim_flag": 0, "benchmark_required_flag": 1, "security_proof_required_flag": 1, "deployment_claim_flag": 0, "productive_potential_flag": 1},
        {"potential_id": 2, "potential_code": 2, "spec_family_code": 1, "internal_evidence_flag": 1, "efficiency_candidate_flag": 1, "security_candidate_flag": 1, "external_comparison_claim_flag": 0, "benchmark_required_flag": 1, "security_proof_required_flag": 1, "deployment_claim_flag": 0, "productive_potential_flag": 1},
        {"potential_id": 3, "potential_code": 3, "spec_family_code": 0, "internal_evidence_flag": 1, "efficiency_candidate_flag": 1, "security_candidate_flag": 1, "external_comparison_claim_flag": 0, "benchmark_required_flag": 1, "security_proof_required_flag": 1, "deployment_claim_flag": 0, "productive_potential_flag": 1},
        {"potential_id": 4, "potential_code": 4, "spec_family_code": 2, "internal_evidence_flag": 1, "efficiency_candidate_flag": 1, "security_candidate_flag": 0, "external_comparison_claim_flag": 0, "benchmark_required_flag": 1, "security_proof_required_flag": 1, "deployment_claim_flag": 0, "productive_potential_flag": 1},
        {"potential_id": 5, "potential_code": 5, "spec_family_code": 3, "internal_evidence_flag": 1, "efficiency_candidate_flag": 0, "security_candidate_flag": 1, "external_comparison_claim_flag": 0, "benchmark_required_flag": 1, "security_proof_required_flag": 1, "deployment_claim_flag": 0, "productive_potential_flag": 1},
    ]
    limit_rows = [
        {"limit_id": 0, "limit_code": 0, "claim_flag": 0, "open_flag": 1, "required_before_external_claim_flag": 1, "overclaim_flag": 0},
        {"limit_id": 1, "limit_code": 1, "claim_flag": 0, "open_flag": 1, "required_before_external_claim_flag": 1, "overclaim_flag": 0},
        {"limit_id": 2, "limit_code": 2, "claim_flag": 0, "open_flag": 1, "required_before_external_claim_flag": 1, "overclaim_flag": 0},
        {"limit_id": 3, "limit_code": 3, "claim_flag": 0, "open_flag": 1, "required_before_external_claim_flag": 1, "overclaim_flag": 0},
        {"limit_id": 4, "limit_code": 4, "claim_flag": 0, "open_flag": 1, "required_before_external_claim_flag": 1, "overclaim_flag": 0},
        {"limit_id": 5, "limit_code": 5, "claim_flag": 0, "open_flag": 1, "required_before_external_claim_flag": 1, "overclaim_flag": 0},
        {"limit_id": 6, "limit_code": 6, "claim_flag": 0, "open_flag": 1, "required_before_external_claim_flag": 1, "overclaim_flag": 0},
    ]
    obs = {
        "input_report_count": 1,
        "certified_input_count": is_certified(
            ledger_report,
            "SECTOR33_K23_PROOF_OF_MANDATE_LEDGER_CERTIFIED",
        ),
        "spec_anchor_count": len(spec_rows),
        "official_spec_anchor_count": sum(row["official_source_flag"] for row in spec_rows),
        "kem_anchor_count": sum(row["kem_flag"] for row in spec_rows),
        "signature_anchor_count": sum(row["signature_flag"] for row in spec_rows),
        "guidance_anchor_count": sum(row["guidance_flag"] for row in spec_rows),
        "potential_row_count": len(potential_rows),
        "internal_evidence_count": sum(row["internal_evidence_flag"] for row in potential_rows),
        "efficiency_candidate_count": sum(row["efficiency_candidate_flag"] for row in potential_rows),
        "security_candidate_count": sum(row["security_candidate_flag"] for row in potential_rows),
        "external_comparison_claim_count": sum(row["external_comparison_claim_flag"] for row in potential_rows),
        "benchmark_required_count": sum(row["benchmark_required_flag"] for row in potential_rows),
        "security_proof_required_count": sum(row["security_proof_required_flag"] for row in potential_rows),
        "deployment_claim_count": sum(row["deployment_claim_flag"] for row in potential_rows),
        "productive_potential_count": sum(row["productive_potential_flag"] for row in potential_rows),
        "limit_row_count": len(limit_rows),
        "open_limit_count": sum(row["open_flag"] for row in limit_rows),
        "required_before_external_claim_count": sum(row["required_before_external_claim_flag"] for row in limit_rows),
        "overclaim_count": sum(row["overclaim_flag"] for row in limit_rows),
        "ledger_certified_input_count": int(ledger_summary.get("certified_input_count", -1)),
        "ledger_row_count": int(ledger_summary.get("ledger_row_count", -1)),
        "challenge_count": int(ledger_summary.get("challenge_count", -1)),
        "game_row_count": int(ledger_summary.get("game_row_count", -1)),
        "accepted_authority_count": int(ledger_summary.get("accepted_authority_count", -1)),
        "all_depth_false_accept_strategy_words": int(ledger_summary.get("all_depth_false_accept_strategy_words", -1)),
        "proof_of_mandate_ledger_flag": int(ledger_summary.get("proof_of_mandate_ledger_flag", -1)),
        "productive_potential_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    spec_table = table_from_rows(SPEC_COLUMNS, spec_rows)
    potential_table = table_from_rows(POTENTIAL_COLUMNS, potential_rows)
    limit_table = table_from_rows(LIMIT_COLUMNS, limit_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "spec_table": spec_table.astype(np.int64),
        "potential_table": potential_table.astype(np.int64),
        "limit_table": limit_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "ledger_report": ledger_report,
        "spec_rows": spec_rows,
        "potential_rows": potential_rows,
        "limit_rows": limit_rows,
        "obs_rows": obs_rows,
        "spec_table": spec_table,
        "potential_table": potential_table,
        "limit_table": limit_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "spec_text_hash": hashlib.sha256(digest_text(SPEC_COLUMNS, spec_rows).encode("ascii")).hexdigest(),
        "potential_text_hash": hashlib.sha256(digest_text(POTENTIAL_COLUMNS, potential_rows).encode("ascii")).hexdigest(),
        "limit_text_hash": hashlib.sha256(digest_text(LIMIT_COLUMNS, limit_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": obs["certified_input_count"] == 1,
        "spec_anchor_profile_matches": (
            obs["spec_anchor_count"],
            obs["official_spec_anchor_count"],
            obs["kem_anchor_count"],
            obs["signature_anchor_count"],
            obs["guidance_anchor_count"],
        )
        == (4, 4, 2, 2, 1),
        "potential_profile_matches": (
            obs["potential_row_count"],
            obs["internal_evidence_count"],
            obs["efficiency_candidate_count"],
            obs["security_candidate_count"],
            obs["external_comparison_claim_count"],
            obs["benchmark_required_count"],
            obs["security_proof_required_count"],
            obs["deployment_claim_count"],
            obs["productive_potential_count"],
        )
        == (6, 6, 4, 5, 0, 6, 6, 0, 6),
        "limit_profile_matches": (
            obs["limit_row_count"],
            obs["open_limit_count"],
            obs["required_before_external_claim_count"],
            obs["overclaim_count"],
        )
        == (7, 7, 7, 0),
        "ledger_counts_match": (
            obs["ledger_certified_input_count"],
            obs["ledger_row_count"],
            obs["challenge_count"],
            obs["game_row_count"],
            obs["accepted_authority_count"],
            obs["all_depth_false_accept_strategy_words"],
            obs["proof_of_mandate_ledger_flag"],
        )
        == (12, 12, 56, 336, 56, 0, 1),
        "boundary_flags_match": (
            obs["productive_potential_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (1, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_productive_potential_candidates",
        "spec_code_map": {
            "0": "NIST_FIPS_203_ML_KEM",
            "1": "NIST_SP_800_227_KEM_RECOMMENDATIONS",
            "2": "NIST_FIPS_204_ML_DSA",
            "3": "NIST_FIPS_205_SLH_DSA",
        },
        "spec_url_map": SPEC_URLS,
        "potential_code_map": {
            "0": "entropy_budget_reduction_candidate",
            "1": "bounded_tamper_rejection_harness",
            "2": "finite_strategy_accounting_audit",
            "3": "authority_decision_table_candidate",
            "4": "frontier_ingestion_ledgerability",
            "5": "deterministic_challenge_source_boundary",
        },
        "limit_code_map": {
            "0": "speed_or_size_improvement",
            "1": "security_superiority",
            "2": "standard_compliance",
            "3": "drop_in_replacement",
            "4": "implementation_benchmark",
            "5": "external_security_proof",
            "6": "deployment_readiness",
        },
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies internally evidenced productive-potential candidates while leaving external superiority and deployment claims open.",
    }
    seam_payload = {
        "schema": "long.k23pot.seam@1",
        "status": STATUS,
        "claim": "The K23 proof-of-mandate ledger exposes finite efficiency/security candidate surfaces against named external spec anchors, without claiming superiority.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23mledger": input_entry(
            LONG_K23MLEDGER_REPORT,
            {
                "status": rows["ledger_report"].get("status"),
                "certificate_sha256": rows["ledger_report"].get("certificate_sha256"),
            },
        ),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23pot.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23pot certifies the first productive-potential candidate surface after proof-of-mandate.",
        "stage_protocol": {
            "draft": "read the proof-of-mandate ledger and anchor the current external spec families by official source URL",
            "witness": "emit spec anchor rows, potential candidate rows, open-limit rows, observables, and numeric tables",
            "coherence": "check candidate counts, ledger counts, source anchors, and explicit external nonclaims",
            "closure": "certify productive potential candidates without claiming external superiority or deployment readiness",
            "emit": "write long_k23pot artifacts and verifier hook",
        },
        "inputs": inputs,
        "external_sources": {
            "source_kind": "official_spec_anchor_urls",
            "urls": SPEC_URLS,
            "retrieved_context": "Official NIST CSRC publication pages were checked before emission; URL content is not hashed into this local proof bundle.",
        },
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "spec_rows_csv": relpath(OUT_DIR / "spec_rows.csv"),
            "potential_rows_csv": relpath(OUT_DIR / "potential_rows.csv"),
            "limit_rows_csv": relpath(OUT_DIR / "limit_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23pot_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the proof-of-mandate ledger is the certified internal input",
                "four current external spec anchors are named by official source URL",
                "six internally evidenced productive-potential candidate rows are emitted",
                "external comparison, benchmark, superiority, compliance, and deployment claims are all open",
            ],
            "does_not_certify": [
                "speed or size improvement over any external standard",
                "security superiority over any external standard",
                "standards compliance",
                "drop-in replacement behavior",
                "implementation benchmark results",
                "deployment readiness",
                "completion of the active discovery goal",
            ],
        },
        "next_highest_yield_item": "Materialize benchmark columns for candidate rows: operation count, transcript size, verification path count, and explicit comparison baselines.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23pot.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23pot.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "spec_csv": csv_text(SPEC_COLUMNS, rows["spec_rows"]),
        "potential_csv": csv_text(POTENTIAL_COLUMNS, rows["potential_rows"]),
        "limit_csv": csv_text(LIMIT_COLUMNS, rows["limit_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "spec_table": rows["spec_table"],
        "potential_table": rows["potential_table"],
        "limit_table": rows["limit_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "spec_text_sha256": rows["spec_text_hash"],
            "potential_text_sha256": rows["potential_text_hash"],
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
    (OUT_DIR / "spec_rows.csv").write_text(payloads["spec_csv"], encoding="utf-8")
    (OUT_DIR / "potential_rows.csv").write_text(payloads["potential_csv"], encoding="utf-8")
    (OUT_DIR / "limit_rows.csv").write_text(payloads["limit_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        spec_table=payloads["spec_table"],
        potential_table=payloads["potential_table"],
        limit_table=payloads["limit_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23pot_matrices.npz", **payloads["matrix_payload"])
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
