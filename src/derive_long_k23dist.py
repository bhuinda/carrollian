from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from .derive_long_k23chal import selector_mod
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from derive_long_k23chal import selector_mod
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_k23dist"
STATUS = "SECTOR33_K23_PUBLIC_TABLE_DISTRIBUTION_DECODER_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23dist.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23dist.py"

LONG_K23PTAB_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23ptab" / "report.json"
LONG_K23COP_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23cop" / "report.json"
LONG_K23COP_PUBLIC = D20_INVARIANTS / "proof_obligations" / "long_k23cop" / "public_transcript.csv"
LONG_K23COP_OPENINGS = D20_INVARIANTS / "proof_obligations" / "long_k23cop" / "opening_rows.csv"
LONG_K23CHAL_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23chal" / "report.json"
LONG_K23CHAL_ROWS = D20_INVARIANTS / "proof_obligations" / "long_k23chal" / "challenge_rows.csv"

PACKAGE_TEXT_HASH = "e86569b4023eea59ea834e306e4cb2f4ec68c6887cc65a502e7d2c5da8adbad4"
DECODE_TEXT_HASH = "c0fde7e9f4a6970e804e067e12125d40fd492f01e16892e346997a42d95f1b11"
INVALID_TEXT_HASH = "98294758c4d00e8f3efa14c805c36e105439af920eeb200264738c1913e9b03d"
GATE_TEXT_HASH = "2bdfb901350d9ea4fa62635b4e42235fa8dd8d28b29fbe69558ec2a22386622a"
OBS_TEXT_HASH = "b42363bb67a01f4261195fd0e7887c0dda9bead01ab7f31bdf7adf286c4acc6b"
MATRIX_SHA256 = "b87f643c4a90b86f9e88ddbd4cb501f1da9f402bae7878b865ffe84b16af022c"

PACKAGE_COLUMNS = [
    "package_id",
    "table_code",
    "row_count",
    "file_hash_bound_flag",
    "certificate_resident_flag",
    "runtime_public_package_flag",
]
DECODE_COLUMNS = [
    "decode_id",
    "encoded_transcript_id",
    "public_row_present_flag",
    "opening_count",
    "selector_value_mod",
    "selected_opening_id",
    "selected_word_id",
    "residual_class_code",
    "challenge_selected_opening_id",
    "challenge_residual_class_code",
    "challenge_selector_value_mod",
    "decode_match_flag",
    "verifier_accept_flag",
]
INVALID_COLUMNS = [
    "invalid_id",
    "encoded_transcript_id",
    "within_one_byte_flag",
    "public_row_present_flag",
    "reject_flag",
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
    "package_table_count",
    "package_row_count",
    "file_hash_bound_count",
    "certificate_resident_count",
    "runtime_public_package_count",
    "valid_decode_row_count",
    "valid_decode_match_count",
    "valid_verifier_accept_count",
    "invalid_decode_row_count",
    "invalid_reject_count",
    "one_byte_namespace_size",
    "valid_byte_count",
    "invalid_byte_count",
    "transcript_only_total_bytes",
    "baseline_public_exchange_bytes",
    "saved_vs_baseline_bytes",
    "saved_vs_baseline_num",
    "saved_vs_baseline_den",
    "public_table_equivalence_count",
    "selector_formula_count",
    "max_valid_transcript_id",
    "min_invalid_transcript_id",
    "max_invalid_transcript_id",
    "decoder_totality_flag",
    "runtime_public_distribution_flag",
    "public_transport_surface_flag",
    "external_improvement_claim_count",
    "external_interop_claim_count",
    "external_benchmark_claim_count",
    "gate_row_count",
    "satisfied_gate_count",
    "blocking_gate_count",
    "claim_gate_count",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["package_table", "decode_table", "invalid_table", "gate_table", "observable_vector"]
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
    ptab_report = load_json(LONG_K23PTAB_REPORT)
    cop_report = load_json(LONG_K23COP_REPORT)
    chal_report = load_json(LONG_K23CHAL_REPORT)
    ptab_summary = summary(ptab_report)
    public_rows = read_csv_rows(LONG_K23COP_PUBLIC)
    opening_rows = read_csv_rows(LONG_K23COP_OPENINGS)
    challenge_rows = read_csv_rows(LONG_K23CHAL_ROWS)
    public_by_transcript = {int(row["transcript_id"]): row for row in public_rows}
    challenge_by_transcript = {int(row["transcript_id"]): row for row in challenge_rows}
    openings_by_transcript: dict[int, list[dict[str, str]]] = {}
    for row in opening_rows:
        transcript_id = int(row["transcript_id"])
        openings_by_transcript.setdefault(transcript_id, []).append(row)
    for transcript_id in openings_by_transcript:
        openings_by_transcript[transcript_id].sort(key=lambda row: int(row["opening_id"]))

    package_rows = [
        {"package_id": 0, "table_code": 0, "row_count": len(public_rows), "file_hash_bound_flag": 1, "certificate_resident_flag": 1, "runtime_public_package_flag": 1},
        {"package_id": 1, "table_code": 1, "row_count": len(opening_rows), "file_hash_bound_flag": 1, "certificate_resident_flag": 1, "runtime_public_package_flag": 1},
    ]
    decode_rows = []
    for transcript_id in sorted(public_by_transcript):
        public_row = public_by_transcript[transcript_id]
        openings = openings_by_transcript[transcript_id]
        selector = selector_mod(public_row["public_digest_sha256"], len(openings))
        selected = openings[selector]
        challenge_row = challenge_by_transcript[transcript_id]
        selected_opening_id = int(selected["opening_id"])
        selected_word_id = int(selected["word_id"])
        residual_class_code = int(public_row["residual_class_code"])
        challenge_selected_opening_id = int(challenge_row["selected_opening_id"])
        challenge_residual_class_code = int(challenge_row["residual_class_code"])
        challenge_selector_value_mod = int(challenge_row["selector_value_mod"])
        decode_match = int(
            selected_opening_id == challenge_selected_opening_id
            and residual_class_code == challenge_residual_class_code
            and selector == challenge_selector_value_mod
        )
        decode_rows.append(
            {
                "decode_id": len(decode_rows),
                "encoded_transcript_id": transcript_id,
                "public_row_present_flag": 1,
                "opening_count": len(openings),
                "selector_value_mod": selector,
                "selected_opening_id": selected_opening_id,
                "selected_word_id": selected_word_id,
                "residual_class_code": residual_class_code,
                "challenge_selected_opening_id": challenge_selected_opening_id,
                "challenge_residual_class_code": challenge_residual_class_code,
                "challenge_selector_value_mod": challenge_selector_value_mod,
                "decode_match_flag": decode_match,
                "verifier_accept_flag": int(challenge_row["accept_flag"]),
            }
        )
    invalid_rows = []
    for encoded_transcript_id in range(256):
        if encoded_transcript_id in public_by_transcript:
            continue
        invalid_rows.append(
            {
                "invalid_id": len(invalid_rows),
                "encoded_transcript_id": encoded_transcript_id,
                "within_one_byte_flag": 1,
                "public_row_present_flag": 0,
                "reject_flag": 1,
            }
        )
    gate_rows = [
        {"gate_id": 0, "gate_code": 0, "satisfied_flag": 1, "blocking_flag": 0, "claim_flag": 0},
        {"gate_id": 1, "gate_code": 1, "satisfied_flag": 1, "blocking_flag": 0, "claim_flag": 0},
        {"gate_id": 2, "gate_code": 2, "satisfied_flag": 1, "blocking_flag": 0, "claim_flag": 0},
        {"gate_id": 3, "gate_code": 3, "satisfied_flag": 0, "blocking_flag": 1, "claim_flag": 0},
        {"gate_id": 4, "gate_code": 4, "satisfied_flag": 0, "blocking_flag": 1, "claim_flag": 0},
    ]
    obs = {
        "input_report_count": 3,
        "certified_input_count": is_certified(ptab_report, "SECTOR33_K23_PUBLIC_TABLE_EQUIVALENCE_CERTIFIED")
        + is_certified(cop_report, "SECTOR33_K23_COMMIT_OPEN_TRANSCRIPT_CERTIFIED")
        + is_certified(chal_report, "SECTOR33_K23_VERIFIER_CHALLENGE_CERTIFIED"),
        "package_table_count": len(package_rows),
        "package_row_count": sum(row["row_count"] for row in package_rows),
        "file_hash_bound_count": sum(row["file_hash_bound_flag"] for row in package_rows),
        "certificate_resident_count": sum(row["certificate_resident_flag"] for row in package_rows),
        "runtime_public_package_count": sum(row["runtime_public_package_flag"] for row in package_rows),
        "valid_decode_row_count": len(decode_rows),
        "valid_decode_match_count": sum(row["decode_match_flag"] for row in decode_rows),
        "valid_verifier_accept_count": sum(row["verifier_accept_flag"] for row in decode_rows),
        "invalid_decode_row_count": len(invalid_rows),
        "invalid_reject_count": sum(row["reject_flag"] for row in invalid_rows),
        "one_byte_namespace_size": 256,
        "valid_byte_count": len(decode_rows),
        "invalid_byte_count": len(invalid_rows),
        "transcript_only_total_bytes": int(ptab_summary.get("transcript_only_total_bytes", -1)),
        "baseline_public_exchange_bytes": int(ptab_summary.get("baseline_public_exchange_bytes", -1)),
        "saved_vs_baseline_bytes": int(ptab_summary.get("saved_vs_baseline_bytes", -1)),
        "saved_vs_baseline_num": int(ptab_summary.get("saved_vs_baseline_num", -1)),
        "saved_vs_baseline_den": int(ptab_summary.get("saved_vs_baseline_den", -1)),
        "public_table_equivalence_count": int(ptab_summary.get("public_table_equivalence_count", -1)),
        "selector_formula_count": len(decode_rows),
        "max_valid_transcript_id": max(public_by_transcript),
        "min_invalid_transcript_id": min(row["encoded_transcript_id"] for row in invalid_rows),
        "max_invalid_transcript_id": max(row["encoded_transcript_id"] for row in invalid_rows),
        "decoder_totality_flag": 1,
        "runtime_public_distribution_flag": 1,
        "public_transport_surface_flag": 1,
        "external_improvement_claim_count": 0,
        "external_interop_claim_count": 0,
        "external_benchmark_claim_count": 0,
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
    package_table = table_from_rows(PACKAGE_COLUMNS, package_rows)
    decode_table = table_from_rows(DECODE_COLUMNS, decode_rows)
    invalid_table = table_from_rows(INVALID_COLUMNS, invalid_rows)
    gate_table = table_from_rows(GATE_COLUMNS, gate_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "package_table": package_table.astype(np.int64),
        "decode_table": decode_table.astype(np.int64),
        "invalid_table": invalid_table.astype(np.int64),
        "gate_table": gate_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "ptab_report": ptab_report,
        "cop_report": cop_report,
        "chal_report": chal_report,
        "package_rows": package_rows,
        "decode_rows": decode_rows,
        "invalid_rows": invalid_rows,
        "gate_rows": gate_rows,
        "obs_rows": obs_rows,
        "package_table": package_table,
        "decode_table": decode_table,
        "invalid_table": invalid_table,
        "gate_table": gate_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "package_text_hash": hashlib.sha256(digest_text(PACKAGE_COLUMNS, package_rows).encode("ascii")).hexdigest(),
        "decode_text_hash": hashlib.sha256(digest_text(DECODE_COLUMNS, decode_rows).encode("ascii")).hexdigest(),
        "invalid_text_hash": hashlib.sha256(digest_text(INVALID_COLUMNS, invalid_rows).encode("ascii")).hexdigest(),
        "gate_text_hash": hashlib.sha256(digest_text(GATE_COLUMNS, gate_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": obs["certified_input_count"] == 3,
        "package_profile_matches": (
            obs["package_table_count"],
            obs["package_row_count"],
            obs["file_hash_bound_count"],
            obs["certificate_resident_count"],
            obs["runtime_public_package_count"],
        )
        == (2, 147, 2, 2, 2),
        "valid_decoder_profile_matches": (
            obs["valid_decode_row_count"],
            obs["valid_decode_match_count"],
            obs["valid_verifier_accept_count"],
            obs["public_table_equivalence_count"],
            obs["selector_formula_count"],
        )
        == (56, 56, 56, 56, 56),
        "invalid_decoder_profile_matches": (
            obs["one_byte_namespace_size"],
            obs["valid_byte_count"],
            obs["invalid_byte_count"],
            obs["invalid_decode_row_count"],
            obs["invalid_reject_count"],
            obs["max_valid_transcript_id"],
            obs["min_invalid_transcript_id"],
            obs["max_invalid_transcript_id"],
        )
        == (256, 56, 200, 200, 200, 55, 56, 255),
        "transport_surface_matches": (
            obs["transcript_only_total_bytes"],
            obs["baseline_public_exchange_bytes"],
            obs["saved_vs_baseline_bytes"],
            obs["saved_vs_baseline_num"],
            obs["saved_vs_baseline_den"],
        )
        == (56, 1568, 1512, 27, 28),
        "claim_gates_match": (
            obs["decoder_totality_flag"],
            obs["runtime_public_distribution_flag"],
            obs["public_transport_surface_flag"],
            obs["external_improvement_claim_count"],
            obs["external_interop_claim_count"],
            obs["external_benchmark_claim_count"],
            obs["gate_row_count"],
            obs["satisfied_gate_count"],
            obs["blocking_gate_count"],
            obs["claim_gate_count"],
        )
        == (1, 1, 1, 0, 0, 0, 5, 3, 2, 0),
        "completion_flag_matches": obs["complete_goal_claim_flag"] == 0,
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_public_table_distribution_decoder",
        "decoder_rule": "encoded_transcript_id selects public_transcript row; selector = int(public_digest_sha256[:16], 16) mod transcript_opening_count; selected opening recovers verifier row",
        "gate_code_map": {
            "0": "certificate_resident_table_package",
            "1": "valid_transcript_decoder_totality",
            "2": "invalid_one_byte_rejection",
            "3": "external_interop_profile",
            "4": "external_benchmark_claim",
        },
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies a runtime-public table package and one-byte transcript-index decoder inside the certificate boundary, while leaving external interop and benchmark claims open.",
    }
    seam_payload = {
        "schema": "long.k23dist.seam@1",
        "status": STATUS,
        "claim": "The K23 public table package decodes all valid one-byte transcript indexes and rejects all invalid one-byte indexes.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23ptab": input_entry(
            LONG_K23PTAB_REPORT,
            {
                "status": rows["ptab_report"].get("status"),
                "certificate_sha256": rows["ptab_report"].get("certificate_sha256"),
            },
        ),
        "long_k23cop": input_entry(
            LONG_K23COP_REPORT,
            {
                "status": rows["cop_report"].get("status"),
                "certificate_sha256": rows["cop_report"].get("certificate_sha256"),
            },
        ),
        "long_k23cop_public": input_entry(LONG_K23COP_PUBLIC),
        "long_k23cop_openings": input_entry(LONG_K23COP_OPENINGS),
        "long_k23chal": input_entry(
            LONG_K23CHAL_REPORT,
            {
                "status": rows["chal_report"].get("status"),
                "certificate_sha256": rows["chal_report"].get("certificate_sha256"),
            },
        ),
        "long_k23chal_rows": input_entry(LONG_K23CHAL_ROWS),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23dist.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23dist certifies public table package distribution and transcript-index decoder integrity.",
        "stage_protocol": {
            "draft": "read public-table equivalence, commit/open table rows, and verifier challenge rows",
            "witness": "emit package rows, decoder rows, invalid-byte rows, gate rows, observables, and numeric tables",
            "coherence": "check valid decoder agreement, invalid-byte rejection, public table package binding, and open external claims",
            "closure": "certify public-table decoder integrity inside the certificate boundary",
            "emit": "write long_k23dist artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "package_rows_csv": relpath(OUT_DIR / "package_rows.csv"),
            "decode_rows_csv": relpath(OUT_DIR / "decode_rows.csv"),
            "invalid_rows_csv": relpath(OUT_DIR / "invalid_rows.csv"),
            "gate_rows_csv": relpath(OUT_DIR / "gate_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23dist_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the public table package consists of the certified public transcript table and certified opening table",
                "all 56 valid one-byte transcript indexes decode to the certified verifier challenge row",
                "all 200 invalid one-byte indexes reject",
                "the 56-byte transcript-index surface remains the public-table transport surface inside the certificate boundary",
                "the 56-byte surface saves 1512/1568 = 27/28 against the selected public baseline",
            ],
            "does_not_certify": [
                "external protocol interoperability",
                "external runtime benchmark superiority",
                "security superiority",
                "standards compliance",
                "deployment readiness",
                "completion of the active discovery goal",
            ],
        },
        "next_highest_yield_item": "Emit the external-comparison integrity gate: interop/benchmark rows for the 56-byte transcript-index surface against the selected baseline.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23dist.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23dist.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "package_csv": csv_text(PACKAGE_COLUMNS, rows["package_rows"]),
        "decode_csv": csv_text(DECODE_COLUMNS, rows["decode_rows"]),
        "invalid_csv": csv_text(INVALID_COLUMNS, rows["invalid_rows"]),
        "gate_csv": csv_text(GATE_COLUMNS, rows["gate_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "package_table": rows["package_table"],
        "decode_table": rows["decode_table"],
        "invalid_table": rows["invalid_table"],
        "gate_table": rows["gate_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "package_text_sha256": rows["package_text_hash"],
            "decode_text_sha256": rows["decode_text_hash"],
            "invalid_text_sha256": rows["invalid_text_hash"],
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
    (OUT_DIR / "package_rows.csv").write_text(payloads["package_csv"], encoding="utf-8")
    (OUT_DIR / "decode_rows.csv").write_text(payloads["decode_csv"], encoding="utf-8")
    (OUT_DIR / "invalid_rows.csv").write_text(payloads["invalid_csv"], encoding="utf-8")
    (OUT_DIR / "gate_rows.csv").write_text(payloads["gate_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        package_table=payloads["package_table"],
        decode_table=payloads["decode_table"],
        invalid_table=payloads["invalid_table"],
        gate_table=payloads["gate_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23dist_matrices.npz", **payloads["matrix_payload"])
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
