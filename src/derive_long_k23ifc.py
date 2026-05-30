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


THEOREM_ID = "long_k23ifc"
STATUS = "SECTOR33_K23_INTEGRITY_TOOL_INTERFACE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23ifc.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23ifc.py"

REPORT_PATHS = {
    "long_k23osint": D20_INVARIANTS / "proof_obligations" / "long_k23osint" / "report.json",
    "long_k23dist": D20_INVARIANTS / "proof_obligations" / "long_k23dist" / "report.json",
    "long_k23mand": D20_INVARIANTS / "proof_obligations" / "long_k23mand" / "report.json",
    "long_k23hprob": D20_INVARIANTS / "proof_obligations" / "long_k23hprob" / "report.json",
    "long_k23epoch": D20_INVARIANTS / "proof_obligations" / "long_k23epoch" / "report.json",
}
EXPECTED_STATUSES = {
    "long_k23osint": "SECTOR33_K23_OPEN_SOURCE_INTEGRITY_ROUTE_CERTIFIED",
    "long_k23dist": "SECTOR33_K23_PUBLIC_TABLE_DISTRIBUTION_DECODER_CERTIFIED",
    "long_k23mand": "SECTOR33_K23_SOURCE_BOUND_MANDATE_CERTIFIED",
    "long_k23hprob": "SECTOR33_K23_HARDNESS_PROBLEM_DEFINITION_CERTIFIED",
    "long_k23epoch": "SECTOR33_K23_REAL_EPOCH_MANIFEST_CERTIFIED",
}
CSV_PATHS = {
    "decode_rows": D20_INVARIANTS / "proof_obligations" / "long_k23dist" / "decode_rows.csv",
    "invalid_rows": D20_INVARIANTS / "proof_obligations" / "long_k23dist" / "invalid_rows.csv",
    "mandate_rows": D20_INVARIANTS / "proof_obligations" / "long_k23mand" / "mandate_rows.csv",
}

TOOL_TEXT_HASH = "454d60ec194ab67b6536a2db9af551f7e7aa944635fc31ae72c222914d175e27"
FIELD_TEXT_HASH = "9e07e23254fc0c5d77944d48b6436dd11ddd988d52ada208b247d006341af34f"
REJECTION_TEXT_HASH = "0e91ba0db3d589b8702fd046b377c37a1ae4e4ec47922895a304cf75948df9a1"
AUDIT_TEXT_HASH = "77b5abcbd64de45564270ce48f92efae2865b9157aba7890567718ab9237f64b"
GATE_TEXT_HASH = "a5c5a7068ce359ab21dbd50b281d0e18300f9882f5b970537d6968b6ca3db59e"
OBS_TEXT_HASH = "8e1d2b6ea2a1c2e4a630c598460bb63ee3add6a48d6bd3525c163068dc72a0b8"
MATRIX_SHA256 = "967cc4c2ad5f93b4fa8c8068d6d3794129b017925da10f1e2fa7a3dca6adf743"

TOOL_COLUMNS = [
    "tool_id",
    "tool_code",
    "source_code",
    "input_contract_code",
    "output_contract_code",
    "primary_rejection_code",
    "public_tool_flag",
    "deterministic_flag",
    "integrity_check_flag",
    "audit_transcript_flag",
    "hardness_claim_flag",
]
FIELD_COLUMNS = [
    "field_id",
    "field_code",
    "direction_code",
    "source_code",
    "required_flag",
    "public_flag",
    "one_byte_flag",
    "row_count",
]
REJECTION_COLUMNS = [
    "rejection_id",
    "rejection_code",
    "source_code",
    "observed_count",
    "reject_flag",
    "terminal_flag",
    "public_flag",
]
AUDIT_COLUMNS = [
    "audit_id",
    "audit_code",
    "field_code",
    "source_code",
    "row_count",
    "required_flag",
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
    "input_csv_count",
    "tool_row_count",
    "public_tool_count",
    "deterministic_tool_count",
    "integrity_check_tool_count",
    "audit_transcript_tool_count",
    "hardness_claim_count",
    "field_row_count",
    "required_field_count",
    "public_field_count",
    "one_byte_field_count",
    "input_field_count",
    "output_field_count",
    "audit_field_count",
    "rejection_row_count",
    "reject_code_count",
    "terminal_code_count",
    "public_code_count",
    "accept_valid_count",
    "invalid_reject_count",
    "nonhardness_reject_count",
    "missing_reduction_boundary_count",
    "audit_row_count",
    "required_audit_field_count",
    "valid_decode_count",
    "decode_match_count",
    "verifier_accept_count",
    "one_byte_namespace_size",
    "package_row_count",
    "mandate_row_count",
    "selector_match_count",
    "digest_bound_count",
    "external_randomness_used_count",
    "materialized_version_count",
    "migration_pass_count",
    "transcript_index_bytes",
    "integrity_tooling_ready_flag",
    "interface_contract_ready_flag",
    "deploy_ready_flag",
    "gate_row_count",
    "satisfied_gate_count",
    "blocking_gate_count",
    "claim_gate_count",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = [
        "tool_table",
        "field_table",
        "rejection_table",
        "audit_table",
        "gate_table",
        "observable_vector",
    ]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def summary(report: dict[str, Any]) -> dict[str, Any]:
    witness = report.get("witness", {})
    if not isinstance(witness, dict):
        return {}
    payload = witness.get("summary", {})
    return payload if isinstance(payload, dict) else {}


def is_certified(report: dict[str, Any], status: str) -> int:
    return int(report.get("status") == status and report.get("all_checks_pass") is True)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_rows() -> dict[str, Any]:
    reports = {name: load_json(path) for name, path in REPORT_PATHS.items()}
    summaries = {name: summary(report) for name, report in reports.items()}
    osint = summaries["long_k23osint"]
    dist = summaries["long_k23dist"]
    mand = summaries["long_k23mand"]
    hprob = summaries["long_k23hprob"]
    epoch = summaries["long_k23epoch"]

    decode_rows_csv = read_csv_rows(CSV_PATHS["decode_rows"])
    invalid_rows_csv = read_csv_rows(CSV_PATHS["invalid_rows"])
    mandate_rows_csv = read_csv_rows(CSV_PATHS["mandate_rows"])
    decode_match_count = sum(int(row["decode_match_flag"]) for row in decode_rows_csv)
    verifier_accept_count = sum(int(row["verifier_accept_flag"]) for row in decode_rows_csv)
    selector_match_count = sum(int(row["selector_match_flag"]) for row in mandate_rows_csv)
    digest_bound_count = sum(int(row["digest_bound_flag"]) for row in mandate_rows_csv)
    external_randomness_used_count = sum(int(row["external_randomness_used_flag"]) for row in mandate_rows_csv)

    valid_decode_count = int(dist.get("valid_decode_row_count", -1))
    invalid_reject_count = int(dist.get("invalid_reject_count", -1))
    package_row_count = int(dist.get("package_row_count", -1))
    namespace_size = int(dist.get("one_byte_namespace_size", -1))
    mandate_row_count = int(mand.get("mandate_row_count", -1))
    nonhardness_reject_count = int(hprob.get("public_table_trivial_problem_count", -1))
    missing_reduction_boundary_count = int(osint.get("open_tool_boundary_count", -1))

    tool_rows = [
        {"tool_id": 0, "tool_code": 0, "source_code": 1, "input_contract_code": 0, "output_contract_code": 0, "primary_rejection_code": 1, "public_tool_flag": 1, "deterministic_flag": 1, "integrity_check_flag": 1, "audit_transcript_flag": 1, "hardness_claim_flag": 0},
        {"tool_id": 1, "tool_code": 1, "source_code": 4, "input_contract_code": 1, "output_contract_code": 1, "primary_rejection_code": 2, "public_tool_flag": 1, "deterministic_flag": 1, "integrity_check_flag": 1, "audit_transcript_flag": 1, "hardness_claim_flag": 0},
        {"tool_id": 2, "tool_code": 2, "source_code": 3, "input_contract_code": 2, "output_contract_code": 2, "primary_rejection_code": 2, "public_tool_flag": 1, "deterministic_flag": 1, "integrity_check_flag": 1, "audit_transcript_flag": 1, "hardness_claim_flag": 0},
        {"tool_id": 3, "tool_code": 4, "source_code": 5, "input_contract_code": 3, "output_contract_code": 3, "primary_rejection_code": 0, "public_tool_flag": 1, "deterministic_flag": 1, "integrity_check_flag": 1, "audit_transcript_flag": 1, "hardness_claim_flag": 0},
        {"tool_id": 4, "tool_code": 5, "source_code": 1, "input_contract_code": 0, "output_contract_code": 4, "primary_rejection_code": 1, "public_tool_flag": 1, "deterministic_flag": 1, "integrity_check_flag": 1, "audit_transcript_flag": 1, "hardness_claim_flag": 0},
    ]
    field_rows = [
        {"field_id": 0, "field_code": 0, "direction_code": 0, "source_code": 1, "required_flag": 1, "public_flag": 1, "one_byte_flag": 1, "row_count": namespace_size},
        {"field_id": 1, "field_code": 1, "direction_code": 0, "source_code": 5, "required_flag": 1, "public_flag": 1, "one_byte_flag": 0, "row_count": 1},
        {"field_id": 2, "field_code": 2, "direction_code": 0, "source_code": 5, "required_flag": 1, "public_flag": 1, "one_byte_flag": 0, "row_count": int(epoch.get("version_row_count", -1))},
        {"field_id": 3, "field_code": 3, "direction_code": 1, "source_code": 1, "required_flag": 1, "public_flag": 1, "one_byte_flag": 0, "row_count": valid_decode_count},
        {"field_id": 4, "field_code": 4, "direction_code": 1, "source_code": 1, "required_flag": 1, "public_flag": 1, "one_byte_flag": 0, "row_count": valid_decode_count},
        {"field_id": 5, "field_code": 5, "direction_code": 1, "source_code": 1, "required_flag": 1, "public_flag": 1, "one_byte_flag": 0, "row_count": valid_decode_count},
        {"field_id": 6, "field_code": 6, "direction_code": 1, "source_code": 1, "required_flag": 1, "public_flag": 1, "one_byte_flag": 0, "row_count": valid_decode_count},
        {"field_id": 7, "field_code": 7, "direction_code": 1, "source_code": 1, "required_flag": 1, "public_flag": 1, "one_byte_flag": 0, "row_count": invalid_reject_count},
        {"field_id": 8, "field_code": 8, "direction_code": 2, "source_code": 2, "required_flag": 1, "public_flag": 1, "one_byte_flag": 0, "row_count": mandate_row_count},
        {"field_id": 9, "field_code": 9, "direction_code": 2, "source_code": 2, "required_flag": 1, "public_flag": 1, "one_byte_flag": 0, "row_count": mandate_row_count},
    ]
    rejection_rows = [
        {"rejection_id": 0, "rejection_code": 0, "source_code": 1, "observed_count": valid_decode_count, "reject_flag": 0, "terminal_flag": 1, "public_flag": 1},
        {"rejection_id": 1, "rejection_code": 1, "source_code": 1, "observed_count": invalid_reject_count, "reject_flag": 1, "terminal_flag": 1, "public_flag": 1},
        {"rejection_id": 2, "rejection_code": 2, "source_code": 3, "observed_count": nonhardness_reject_count, "reject_flag": 1, "terminal_flag": 1, "public_flag": 1},
        {"rejection_id": 3, "rejection_code": 3, "source_code": 0, "observed_count": missing_reduction_boundary_count, "reject_flag": 1, "terminal_flag": 0, "public_flag": 1},
    ]
    audit_rows = [
        {"audit_id": 0, "audit_code": 0, "field_code": 0, "source_code": 1, "row_count": namespace_size, "required_flag": 1},
        {"audit_id": 1, "audit_code": 1, "field_code": 3, "source_code": 1, "row_count": valid_decode_count, "required_flag": 1},
        {"audit_id": 2, "audit_code": 2, "field_code": 4, "source_code": 1, "row_count": valid_decode_count, "required_flag": 1},
        {"audit_id": 3, "audit_code": 3, "field_code": 5, "source_code": 1, "row_count": valid_decode_count, "required_flag": 1},
        {"audit_id": 4, "audit_code": 4, "field_code": 6, "source_code": 1, "row_count": valid_decode_count, "required_flag": 1},
        {"audit_id": 5, "audit_code": 5, "field_code": 7, "source_code": 1, "row_count": invalid_reject_count, "required_flag": 1},
        {"audit_id": 6, "audit_code": 6, "field_code": 8, "source_code": 2, "row_count": mandate_row_count, "required_flag": 1},
        {"audit_id": 7, "audit_code": 7, "field_code": 9, "source_code": 2, "row_count": mandate_row_count, "required_flag": 1},
    ]
    gate_rows = [
        {"gate_id": 0, "gate_code": 0, "satisfied_flag": 1, "blocking_flag": 0, "claim_flag": 0},
        {"gate_id": 1, "gate_code": 1, "satisfied_flag": 1, "blocking_flag": 0, "claim_flag": 0},
        {"gate_id": 2, "gate_code": 2, "satisfied_flag": 1, "blocking_flag": 0, "claim_flag": 0},
        {"gate_id": 3, "gate_code": 3, "satisfied_flag": 1, "blocking_flag": 0, "claim_flag": 0},
        {"gate_id": 4, "gate_code": 4, "satisfied_flag": 0, "blocking_flag": 1, "claim_flag": 0},
    ]
    obs = {
        "input_report_count": len(REPORT_PATHS),
        "certified_input_count": sum(is_certified(reports[name], EXPECTED_STATUSES[name]) for name in REPORT_PATHS),
        "input_csv_count": len(CSV_PATHS),
        "tool_row_count": len(tool_rows),
        "public_tool_count": sum(row["public_tool_flag"] for row in tool_rows),
        "deterministic_tool_count": sum(row["deterministic_flag"] for row in tool_rows),
        "integrity_check_tool_count": sum(row["integrity_check_flag"] for row in tool_rows),
        "audit_transcript_tool_count": sum(row["audit_transcript_flag"] for row in tool_rows),
        "hardness_claim_count": sum(row["hardness_claim_flag"] for row in tool_rows),
        "field_row_count": len(field_rows),
        "required_field_count": sum(row["required_flag"] for row in field_rows),
        "public_field_count": sum(row["public_flag"] for row in field_rows),
        "one_byte_field_count": sum(row["one_byte_flag"] for row in field_rows),
        "input_field_count": sum(int(row["direction_code"] == 0) for row in field_rows),
        "output_field_count": sum(int(row["direction_code"] == 1) for row in field_rows),
        "audit_field_count": sum(int(row["direction_code"] == 2) for row in field_rows),
        "rejection_row_count": len(rejection_rows),
        "reject_code_count": sum(row["reject_flag"] for row in rejection_rows),
        "terminal_code_count": sum(row["terminal_flag"] for row in rejection_rows),
        "public_code_count": sum(row["public_flag"] for row in rejection_rows),
        "accept_valid_count": valid_decode_count,
        "invalid_reject_count": invalid_reject_count,
        "nonhardness_reject_count": nonhardness_reject_count,
        "missing_reduction_boundary_count": missing_reduction_boundary_count,
        "audit_row_count": len(audit_rows),
        "required_audit_field_count": sum(row["required_flag"] for row in audit_rows),
        "valid_decode_count": valid_decode_count,
        "decode_match_count": decode_match_count,
        "verifier_accept_count": verifier_accept_count,
        "one_byte_namespace_size": namespace_size,
        "package_row_count": package_row_count,
        "mandate_row_count": mandate_row_count,
        "selector_match_count": selector_match_count,
        "digest_bound_count": digest_bound_count,
        "external_randomness_used_count": external_randomness_used_count,
        "materialized_version_count": int(epoch.get("materialized_version_count", -1)),
        "migration_pass_count": int(epoch.get("migration_pass_count", -1)),
        "transcript_index_bytes": int(osint.get("transcript_index_bytes", -1)),
        "integrity_tooling_ready_flag": int(osint.get("integrity_tooling_ready_flag", -1)),
        "interface_contract_ready_flag": 1,
        "deploy_ready_flag": int(osint.get("deploy_ready_flag", -1)),
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
    tool_table = table_from_rows(TOOL_COLUMNS, tool_rows)
    field_table = table_from_rows(FIELD_COLUMNS, field_rows)
    rejection_table = table_from_rows(REJECTION_COLUMNS, rejection_rows)
    audit_table = table_from_rows(AUDIT_COLUMNS, audit_rows)
    gate_table = table_from_rows(GATE_COLUMNS, gate_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "tool_table": tool_table.astype(np.int64),
        "field_table": field_table.astype(np.int64),
        "rejection_table": rejection_table.astype(np.int64),
        "audit_table": audit_table.astype(np.int64),
        "gate_table": gate_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "reports": reports,
        "tool_rows": tool_rows,
        "field_rows": field_rows,
        "rejection_rows": rejection_rows,
        "audit_rows": audit_rows,
        "gate_rows": gate_rows,
        "obs_rows": obs_rows,
        "tool_table": tool_table,
        "field_table": field_table,
        "rejection_table": rejection_table,
        "audit_table": audit_table,
        "gate_table": gate_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "tool_text_hash": hashlib.sha256(digest_text(TOOL_COLUMNS, tool_rows).encode("ascii")).hexdigest(),
        "field_text_hash": hashlib.sha256(digest_text(FIELD_COLUMNS, field_rows).encode("ascii")).hexdigest(),
        "rejection_text_hash": hashlib.sha256(digest_text(REJECTION_COLUMNS, rejection_rows).encode("ascii")).hexdigest(),
        "audit_text_hash": hashlib.sha256(digest_text(AUDIT_COLUMNS, audit_rows).encode("ascii")).hexdigest(),
        "gate_text_hash": hashlib.sha256(digest_text(GATE_COLUMNS, gate_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": obs["certified_input_count"] == obs["input_report_count"] == 5 and obs["input_csv_count"] == 3,
        "tool_profile_matches": (
            obs["tool_row_count"],
            obs["public_tool_count"],
            obs["deterministic_tool_count"],
            obs["integrity_check_tool_count"],
            obs["audit_transcript_tool_count"],
            obs["hardness_claim_count"],
        )
        == (5, 5, 5, 5, 5, 0),
        "field_profile_matches": (
            obs["field_row_count"],
            obs["required_field_count"],
            obs["public_field_count"],
            obs["one_byte_field_count"],
            obs["input_field_count"],
            obs["output_field_count"],
            obs["audit_field_count"],
        )
        == (10, 10, 10, 1, 3, 5, 2),
        "rejection_profile_matches": (
            obs["rejection_row_count"],
            obs["reject_code_count"],
            obs["terminal_code_count"],
            obs["public_code_count"],
            obs["accept_valid_count"],
            obs["invalid_reject_count"],
            obs["nonhardness_reject_count"],
            obs["missing_reduction_boundary_count"],
        )
        == (4, 3, 3, 4, 56, 200, 2, 1),
        "audit_profile_matches": (
            obs["audit_row_count"],
            obs["required_audit_field_count"],
            obs["valid_decode_count"],
            obs["decode_match_count"],
            obs["verifier_accept_count"],
            obs["one_byte_namespace_size"],
            obs["package_row_count"],
        )
        == (8, 8, 56, 56, 56, 256, 147),
        "mandate_and_epoch_match": (
            obs["mandate_row_count"],
            obs["selector_match_count"],
            obs["digest_bound_count"],
            obs["external_randomness_used_count"],
            obs["materialized_version_count"],
            obs["migration_pass_count"],
        )
        == (56, 56, 56, 0, 2, 1),
        "route_claims_match": (
            obs["transcript_index_bytes"],
            obs["integrity_tooling_ready_flag"],
            obs["interface_contract_ready_flag"],
            obs["deploy_ready_flag"],
        )
        == (56, 1, 1, 0),
        "gate_profile_matches": (
            obs["gate_row_count"],
            obs["satisfied_gate_count"],
            obs["blocking_gate_count"],
            obs["claim_gate_count"],
        )
        == (5, 4, 1, 0),
        "completion_flag_matches": obs["complete_goal_claim_flag"] == 0,
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_integrity_tool_interface",
        "field_code_map": {
            "0": "encoded_transcript_id",
            "1": "epoch_id",
            "2": "version_code",
            "3": "selected_opening_id",
            "4": "residual_class_code",
            "5": "selector_value_mod",
            "6": "verifier_accept_flag",
            "7": "reject_code",
            "8": "selector_match_flag",
            "9": "digest_bound_flag",
        },
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This materializes exact interface rows for the selected public integrity-tooling route.",
    }
    seam_payload = {
        "schema": "long.k23ifc.seam@1",
        "status": STATUS,
        "claim": "The selected K23 integrity route now has exact public inputs, outputs, rejection codes, and audit transcript fields.",
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
    for name, path in CSV_PATHS.items():
        inputs[name] = input_entry(path)
    inputs["derive_script"] = input_entry(DERIVE_SCRIPT)
    inputs["validator"] = input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)}
    report = {
        "schema": "long.k23ifc.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23ifc certifies the exact integrity tooling interface contract for the selected K23 route.",
        "stage_protocol": {
            "draft": "read open-source integrity route, decoder, mandate, hardness-boundary, epoch reports, and row witnesses",
            "witness": "emit tool rows, field rows, rejection-code rows, audit rows, gate rows, observables, and tables",
            "coherence": "check field counts, rejection semantics, decoder totals, mandate audit fields, and nondeployment guardrails",
            "closure": "certify the interface contract without claiming deploy-grade cryptographic hardness",
            "emit": "write long_k23ifc artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "tool_rows_csv": relpath(OUT_DIR / "tool_rows.csv"),
            "field_rows_csv": relpath(OUT_DIR / "field_rows.csv"),
            "rejection_rows_csv": relpath(OUT_DIR / "rejection_rows.csv"),
            "audit_rows_csv": relpath(OUT_DIR / "audit_rows.csv"),
            "gate_rows_csv": relpath(OUT_DIR / "gate_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23ifc_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "five public deterministic integrity tools have explicit interface rows",
                "ten required public interface fields are listed",
                "four terminal/boundary result codes are listed",
                "eight audit transcript fields are listed and bound to decoder and mandate witnesses",
            ],
            "does_not_certify": [
                "cryptographic hardness",
                "deployment readiness",
                "secret witness protection",
                "external benchmark compatibility",
                "zero knowledge",
            ],
        },
        "next_highest_yield_item": "Emit a minimal verifier-contract adapter that consumes the interface rows and produces deterministic accept/reject audit rows.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23ifc.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23ifc.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "tool_csv": csv_text(TOOL_COLUMNS, rows["tool_rows"]),
        "field_csv": csv_text(FIELD_COLUMNS, rows["field_rows"]),
        "rejection_csv": csv_text(REJECTION_COLUMNS, rows["rejection_rows"]),
        "audit_csv": csv_text(AUDIT_COLUMNS, rows["audit_rows"]),
        "gate_csv": csv_text(GATE_COLUMNS, rows["gate_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "tool_table": rows["tool_table"],
        "field_table": rows["field_table"],
        "rejection_table": rows["rejection_table"],
        "audit_table": rows["audit_table"],
        "gate_table": rows["gate_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "tool_text_sha256": rows["tool_text_hash"],
            "field_text_sha256": rows["field_text_hash"],
            "rejection_text_sha256": rows["rejection_text_hash"],
            "audit_text_sha256": rows["audit_text_hash"],
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
    (OUT_DIR / "tool_rows.csv").write_text(payloads["tool_csv"], encoding="utf-8")
    (OUT_DIR / "field_rows.csv").write_text(payloads["field_csv"], encoding="utf-8")
    (OUT_DIR / "rejection_rows.csv").write_text(payloads["rejection_csv"], encoding="utf-8")
    (OUT_DIR / "audit_rows.csv").write_text(payloads["audit_csv"], encoding="utf-8")
    (OUT_DIR / "gate_rows.csv").write_text(payloads["gate_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        tool_table=payloads["tool_table"],
        field_table=payloads["field_table"],
        rejection_table=payloads["rejection_table"],
        audit_table=payloads["audit_table"],
        gate_table=payloads["gate_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23ifc_matrices.npz", **payloads["matrix_payload"])
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
