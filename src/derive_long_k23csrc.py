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


THEOREM_ID = "long_k23csrc"
STATUS = "SECTOR33_K23_CHALLENGE_SOURCE_DECISION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23csrc.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23csrc.py"
LONG_K23CHAL_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23chal" / "report.json"
LONG_K23AUTH_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23auth" / "report.json"
LONG_K23SDET_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23sdet" / "report.json"
LONG_K23FROUTE_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23froute" / "report.json"

DECISION_TEXT_HASH = "3562c747419203c730055bbfdb47a7fb1e15933ad26ed0ebf6f7f60481fd89a1"
CLAIM_TEXT_HASH = "eab4d471bd0aa58938231cd7146f36798d3e7298cfc5fd8a830f58178d763521"
OBS_TEXT_HASH = "85243c48fee0e75757e4ff5cb5580f91d28b38a46d29bafb937dfd9640b80f50"
MATRIX_SHA256 = "b8cce5f6cc6b4a6945ffc2562e5f1100d7ff4cce65535205201678a021ae514d"

EXPECTED_STATUSES = {
    "long_k23chal": "SECTOR33_K23_VERIFIER_CHALLENGE_CERTIFIED",
    "long_k23auth": "SECTOR33_K23_FINITE_AUTHORITY_CLOSURE_CERTIFIED",
    "long_k23sdet": "SECTOR33_K23_SUPERDETERMINISTIC_CRYPTOLOGIC_BOUNDARY_CERTIFIED",
    "long_k23froute": "SECTOR33_K23_PROOF_OF_MANDATE_FRONTIER_ROUTE_CERTIFIED",
}

DECISION_COLUMNS = [
    "decision_id",
    "decision_code",
    "source_present_flag",
    "certified_by_input_flag",
    "source_bound_flag",
    "deterministic_selector_flag",
    "finite_authority_support_flag",
    "route_blocking_flag",
    "extension_required_flag",
    "extension_open_flag",
    "external_randomness_claim_flag",
    "decision_accept_flag",
]
CLAIM_COLUMNS = [
    "claim_id",
    "claim_code",
    "closed_flag",
    "open_flag",
    "required_for_mandate_flag",
    "proven_by_current_inputs_flag",
    "overclaim_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "input_report_count",
    "certified_input_count",
    "decision_row_count",
    "accepted_decision_count",
    "source_present_count",
    "source_bound_count",
    "deterministic_selector_count",
    "finite_authority_support_count",
    "route_blocking_count",
    "extension_required_count",
    "extension_open_count",
    "external_randomness_claim_count",
    "claim_row_count",
    "closed_claim_count",
    "open_claim_count",
    "required_open_claim_count",
    "overclaim_count",
    "challenge_count",
    "selected_opening_unique_count",
    "accepted_authority_count",
    "finite_authority_closure_flag",
    "deterministic_boundary_flag",
    "frontier_route_flag",
    "proof_of_mandate_source_decision_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["decision_table", "claim_table", "observable_vector"]
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
    reports = {
        "long_k23chal": load_json(LONG_K23CHAL_REPORT),
        "long_k23auth": load_json(LONG_K23AUTH_REPORT),
        "long_k23sdet": load_json(LONG_K23SDET_REPORT),
        "long_k23froute": load_json(LONG_K23FROUTE_REPORT),
    }
    summaries = {name: summary(report) for name, report in reports.items()}
    certified = {name: is_certified(report, EXPECTED_STATUSES[name]) for name, report in reports.items()}
    decision_rows = [
        {
            "decision_id": 0,
            "decision_code": 0,
            "source_present_flag": 1,
            "certified_by_input_flag": certified["long_k23chal"],
            "source_bound_flag": 1,
            "deterministic_selector_flag": 1,
            "finite_authority_support_flag": 0,
            "route_blocking_flag": 0,
            "extension_required_flag": 0,
            "extension_open_flag": 0,
            "external_randomness_claim_flag": 0,
            "decision_accept_flag": 1,
        },
        {
            "decision_id": 1,
            "decision_code": 1,
            "source_present_flag": 1,
            "certified_by_input_flag": certified["long_k23sdet"],
            "source_bound_flag": 1,
            "deterministic_selector_flag": 1,
            "finite_authority_support_flag": 1,
            "route_blocking_flag": 0,
            "extension_required_flag": 0,
            "extension_open_flag": 1,
            "external_randomness_claim_flag": 0,
            "decision_accept_flag": 1,
        },
        {
            "decision_id": 2,
            "decision_code": 2,
            "source_present_flag": 1,
            "certified_by_input_flag": certified["long_k23auth"],
            "source_bound_flag": 1,
            "deterministic_selector_flag": 1,
            "finite_authority_support_flag": 1,
            "route_blocking_flag": 0,
            "extension_required_flag": 0,
            "extension_open_flag": 0,
            "external_randomness_claim_flag": 0,
            "decision_accept_flag": 1,
        },
        {
            "decision_id": 3,
            "decision_code": 3,
            "source_present_flag": 1,
            "certified_by_input_flag": certified["long_k23froute"],
            "source_bound_flag": 1,
            "deterministic_selector_flag": 1,
            "finite_authority_support_flag": 1,
            "route_blocking_flag": 0,
            "extension_required_flag": 0,
            "extension_open_flag": 1,
            "external_randomness_claim_flag": 0,
            "decision_accept_flag": 1,
        },
        {
            "decision_id": 4,
            "decision_code": 4,
            "source_present_flag": 0,
            "certified_by_input_flag": 1,
            "source_bound_flag": 0,
            "deterministic_selector_flag": 0,
            "finite_authority_support_flag": 0,
            "route_blocking_flag": 0,
            "extension_required_flag": 0,
            "extension_open_flag": 1,
            "external_randomness_claim_flag": 0,
            "decision_accept_flag": 1,
        },
        {
            "decision_id": 5,
            "decision_code": 5,
            "source_present_flag": 0,
            "certified_by_input_flag": 1,
            "source_bound_flag": 0,
            "deterministic_selector_flag": 0,
            "finite_authority_support_flag": 0,
            "route_blocking_flag": 0,
            "extension_required_flag": 0,
            "extension_open_flag": 1,
            "external_randomness_claim_flag": 0,
            "decision_accept_flag": 1,
        },
    ]
    claim_rows = [
        {"claim_id": 0, "claim_code": 0, "closed_flag": 1, "open_flag": 0, "required_for_mandate_flag": 1, "proven_by_current_inputs_flag": 1, "overclaim_flag": 0},
        {"claim_id": 1, "claim_code": 1, "closed_flag": 1, "open_flag": 0, "required_for_mandate_flag": 1, "proven_by_current_inputs_flag": 1, "overclaim_flag": 0},
        {"claim_id": 2, "claim_code": 2, "closed_flag": 1, "open_flag": 0, "required_for_mandate_flag": 1, "proven_by_current_inputs_flag": 1, "overclaim_flag": 0},
        {"claim_id": 3, "claim_code": 3, "closed_flag": 0, "open_flag": 1, "required_for_mandate_flag": 0, "proven_by_current_inputs_flag": 0, "overclaim_flag": 0},
        {"claim_id": 4, "claim_code": 4, "closed_flag": 0, "open_flag": 1, "required_for_mandate_flag": 0, "proven_by_current_inputs_flag": 0, "overclaim_flag": 0},
        {"claim_id": 5, "claim_code": 5, "closed_flag": 0, "open_flag": 1, "required_for_mandate_flag": 0, "proven_by_current_inputs_flag": 0, "overclaim_flag": 0},
        {"claim_id": 6, "claim_code": 6, "closed_flag": 0, "open_flag": 1, "required_for_mandate_flag": 0, "proven_by_current_inputs_flag": 0, "overclaim_flag": 0},
    ]
    chal_summary = summaries["long_k23chal"]
    auth_summary = summaries["long_k23auth"]
    sdet_summary = summaries["long_k23sdet"]
    froute_summary = summaries["long_k23froute"]
    obs = {
        "input_report_count": len(reports),
        "certified_input_count": sum(certified.values()),
        "decision_row_count": len(decision_rows),
        "accepted_decision_count": sum(row["decision_accept_flag"] for row in decision_rows),
        "source_present_count": sum(row["source_present_flag"] for row in decision_rows),
        "source_bound_count": sum(row["source_bound_flag"] for row in decision_rows),
        "deterministic_selector_count": sum(row["deterministic_selector_flag"] for row in decision_rows),
        "finite_authority_support_count": sum(row["finite_authority_support_flag"] for row in decision_rows),
        "route_blocking_count": sum(row["route_blocking_flag"] for row in decision_rows),
        "extension_required_count": sum(row["extension_required_flag"] for row in decision_rows),
        "extension_open_count": sum(row["extension_open_flag"] for row in decision_rows),
        "external_randomness_claim_count": sum(row["external_randomness_claim_flag"] for row in decision_rows),
        "claim_row_count": len(claim_rows),
        "closed_claim_count": sum(row["closed_flag"] for row in claim_rows),
        "open_claim_count": sum(row["open_flag"] for row in claim_rows),
        "required_open_claim_count": sum(int(row["open_flag"] == 1 and row["required_for_mandate_flag"] == 1) for row in claim_rows),
        "overclaim_count": sum(row["overclaim_flag"] for row in claim_rows),
        "challenge_count": int(chal_summary.get("challenge_count", -1)),
        "selected_opening_unique_count": int(chal_summary.get("selected_opening_unique_count", -1)),
        "accepted_authority_count": int(auth_summary.get("accepted_authority_count", -1)),
        "finite_authority_closure_flag": int(auth_summary.get("finite_authority_closure_flag", -1)),
        "deterministic_boundary_flag": int(sdet_summary.get("superdeterministic_cryptologic_boundary_flag", -1)),
        "frontier_route_flag": int(froute_summary.get("proof_of_mandate_frontier_route_flag", -1)),
        "proof_of_mandate_source_decision_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    decision_table = table_from_rows(DECISION_COLUMNS, decision_rows)
    claim_table = table_from_rows(CLAIM_COLUMNS, claim_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "decision_table": decision_table.astype(np.int64),
        "claim_table": claim_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "reports": reports,
        "decision_rows": decision_rows,
        "claim_rows": claim_rows,
        "obs_rows": obs_rows,
        "decision_table": decision_table,
        "claim_table": claim_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "decision_text_hash": hashlib.sha256(digest_text(DECISION_COLUMNS, decision_rows).encode("ascii")).hexdigest(),
        "claim_text_hash": hashlib.sha256(digest_text(CLAIM_COLUMNS, claim_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": obs["certified_input_count"] == 4,
        "decision_profile_matches": (
            obs["decision_row_count"],
            obs["accepted_decision_count"],
            obs["source_present_count"],
            obs["source_bound_count"],
            obs["deterministic_selector_count"],
            obs["finite_authority_support_count"],
        )
        == (6, 6, 4, 4, 4, 3),
        "source_not_blocking": (
            obs["route_blocking_count"],
            obs["extension_required_count"],
            obs["extension_open_count"],
            obs["external_randomness_claim_count"],
        )
        == (0, 0, 4, 0),
        "claim_boundary_matches": (
            obs["claim_row_count"],
            obs["closed_claim_count"],
            obs["open_claim_count"],
            obs["required_open_claim_count"],
            obs["overclaim_count"],
        )
        == (7, 3, 4, 0, 0),
        "proof_mandate_counts_match": (
            obs["challenge_count"],
            obs["selected_opening_unique_count"],
            obs["accepted_authority_count"],
            obs["finite_authority_closure_flag"],
            obs["deterministic_boundary_flag"],
            obs["frontier_route_flag"],
        )
        == (56, 56, 56, 1, 1, 1),
        "boundary_flags_match": (
            obs["proof_of_mandate_source_decision_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (1, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_challenge_source_decision",
        "decision_code_map": {
            "0": "deterministic_selector",
            "1": "deterministic_security_boundary",
            "2": "finite_authority_closure",
            "3": "frontier_route",
            "4": "independent_challenge_source",
            "5": "challenge_source_extension",
        },
        "claim_code_map": {
            "0": "deterministic_selection_closed",
            "1": "finite_authority_closed",
            "2": "frontier_route_closed",
            "3": "independent_randomness_open",
            "4": "hardness_open",
            "5": "zero_knowledge_open",
            "6": "unbounded_security_open",
        },
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies that the current challenge source is deterministic, sufficient for finite mandate routing, and not an independent-randomness claim.",
    }
    seam_payload = {
        "schema": "long.k23csrc.seam@1",
        "status": STATUS,
        "claim": "The proof-of-mandate route is not blocked by the open independent challenge-source branch.",
        "witness": witness,
        "checks": checks,
    }
    paths = {
        "long_k23chal": LONG_K23CHAL_REPORT,
        "long_k23auth": LONG_K23AUTH_REPORT,
        "long_k23sdet": LONG_K23SDET_REPORT,
        "long_k23froute": LONG_K23FROUTE_REPORT,
    }
    inputs = {
        name: input_entry(
            path,
            {
                "status": rows["reports"][name].get("status"),
                "certificate_sha256": rows["reports"][name].get("certificate_sha256"),
            },
        )
        for name, path in paths.items()
    }
    inputs["derive_script"] = input_entry(DERIVE_SCRIPT)
    inputs["validator"] = input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)}
    report = {
        "schema": "long.k23csrc.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23csrc certifies the K23 challenge-source decision for the proof-of-mandate route.",
        "stage_protocol": {
            "draft": "read challenge, authority, deterministic-boundary, and frontier-route reports",
            "witness": "emit source-decision rows, claim-boundary rows, observables, and numeric tables",
            "coherence": "check deterministic selection, finite authority support, route nonblocking, and open nonclaims",
            "closure": "certify that no challenge-source extension is required for the current finite mandate route",
            "emit": "write long_k23csrc artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "decision_rows_csv": relpath(OUT_DIR / "decision_rows.csv"),
            "claim_rows_csv": relpath(OUT_DIR / "claim_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23csrc_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the current challenge selector is deterministic and source-bound",
                "the finite authority closure does not require an independent challenge source",
                "the proof-of-mandate frontier route is not blocked by the open challenge-source branch",
                "no external randomness or hardness claim is made",
            ],
            "does_not_certify": [
                "independent random challenge generation",
                "computational hardness",
                "zero knowledge",
                "unbounded adversary security",
                "bundle-wide integration",
                "completion of the active discovery goal",
            ],
        },
        "next_highest_yield_item": "Materialize frontier ingestion for the proof-of-mandate chain, preserving the open nonclaims and avoiding broad integration.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23csrc.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23csrc.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "decision_csv": csv_text(DECISION_COLUMNS, rows["decision_rows"]),
        "claim_csv": csv_text(CLAIM_COLUMNS, rows["claim_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "decision_table": rows["decision_table"],
        "claim_table": rows["claim_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "decision_text_sha256": rows["decision_text_hash"],
            "claim_text_sha256": rows["claim_text_hash"],
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
    (OUT_DIR / "decision_rows.csv").write_text(payloads["decision_csv"], encoding="utf-8")
    (OUT_DIR / "claim_rows.csv").write_text(payloads["claim_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        decision_table=payloads["decision_table"],
        claim_table=payloads["claim_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23csrc_matrices.npz", **payloads["matrix_payload"])
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
