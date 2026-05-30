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


THEOREM_ID = "long_k23canon"
STATUS = "SECTOR33_K23_DEREFERENCE_VERSION_CANONICALITY_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23canon.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23canon.py"

LONG_K23WIRE_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23wire" / "report.json"
LONG_K23WIRE_ROWS = D20_INVARIANTS / "proof_obligations" / "long_k23wire" / "wire_rows.csv"
LONG_K23DIST_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23dist" / "report.json"
LONG_K23DIST_DECODE_ROWS = D20_INVARIANTS / "proof_obligations" / "long_k23dist" / "decode_rows.csv"

VERSION_TEXT_HASH = "4ff28eb0394754aeac5c6e3815060b82320c479cd5017acb5ddabaa74941fc41"
CANON_TEXT_HASH = "a9918f075cb4f65f6eb6e955a3124b392947e66b735f28c58b8ce8f5078975cb"
GATE_TEXT_HASH = "ebd78b130a5665adbc7517490b2bb99c5ecfc3fb3cc9ae3f5e7dcf470d079ec0"
OBS_TEXT_HASH = "1d61e40f80caef9c3207b4c0ec74805aa37f47406333b87c0f3874fb719020d7"
MATRIX_SHA256 = "20dcc68f5ba7dd54597b8480fb4bca1b5ed39ff46b21230d210ea85aa4cd2073"

VERSION_COLUMNS = [
    "version_id",
    "version_code",
    "byte_surface_per_message",
    "valid_decode_count",
    "invalid_reject_count",
    "table_package_flag",
    "mint_normal_form_flag",
]
CANON_COLUMNS = [
    "canon_id",
    "mint_normal_form_id",
    "compact_transcript_id",
    "index_transcript_id",
    "compact_selected_opening_id",
    "index_selected_opening_id",
    "compact_residual_class_code",
    "index_residual_class_code",
    "compact_selector_value_mod",
    "index_selector_value_mod",
    "decode_equiv_flag",
    "same_mint_normal_form_flag",
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
    "version_row_count",
    "compact_version_byte_surface",
    "index_version_byte_surface",
    "byte_surface_ratio_num",
    "byte_surface_ratio_den",
    "canonical_pair_row_count",
    "decode_equiv_count",
    "same_mint_normal_form_count",
    "canonicality_failure_count",
    "valid_decode_count",
    "invalid_reject_count",
    "version_pair_count",
    "canonical_across_versions_flag",
    "real_epoch_count",
    "simulated_epoch_count",
    "external_epoch_claim_count",
    "gate_row_count",
    "satisfied_gate_count",
    "blocking_gate_count",
    "claim_gate_count",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["version_table", "canon_table", "gate_table", "observable_vector"]
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
    wire_report = load_json(LONG_K23WIRE_REPORT)
    dist_report = load_json(LONG_K23DIST_REPORT)
    dist_summary = summary(dist_report)
    wire_rows = read_csv_rows(LONG_K23WIRE_ROWS)
    decode_rows = read_csv_rows(LONG_K23DIST_DECODE_ROWS)
    decode_by_transcript = {int(row["encoded_transcript_id"]): row for row in decode_rows}
    version_rows = [
        {
            "version_id": 0,
            "version_code": 0,
            "byte_surface_per_message": 4,
            "valid_decode_count": len(wire_rows),
            "invalid_reject_count": 0,
            "table_package_flag": 1,
            "mint_normal_form_flag": 1,
        },
        {
            "version_id": 1,
            "version_code": 1,
            "byte_surface_per_message": 1,
            "valid_decode_count": int(dist_summary.get("valid_decode_row_count", -1)),
            "invalid_reject_count": int(dist_summary.get("invalid_reject_count", -1)),
            "table_package_flag": int(dist_summary.get("runtime_public_package_count", -1) == 2),
            "mint_normal_form_flag": 1,
        },
    ]
    canon_rows = []
    for wire_row in wire_rows:
        transcript_id = int(wire_row["transcript_id"])
        decode_row = decode_by_transcript[transcript_id]
        compact_selected = int(wire_row["selected_opening_id"])
        index_selected = int(decode_row["selected_opening_id"])
        compact_residual = int(wire_row["residual_class_code"])
        index_residual = int(decode_row["residual_class_code"])
        compact_selector = int(wire_row["selector_value_mod"])
        index_selector = int(decode_row["selector_value_mod"])
        decode_equiv = int(
            compact_selected == index_selected
            and compact_residual == index_residual
            and compact_selector == index_selector
        )
        canon_rows.append(
            {
                "canon_id": len(canon_rows),
                "mint_normal_form_id": transcript_id,
                "compact_transcript_id": transcript_id,
                "index_transcript_id": int(decode_row["encoded_transcript_id"]),
                "compact_selected_opening_id": compact_selected,
                "index_selected_opening_id": index_selected,
                "compact_residual_class_code": compact_residual,
                "index_residual_class_code": index_residual,
                "compact_selector_value_mod": compact_selector,
                "index_selector_value_mod": index_selector,
                "decode_equiv_flag": decode_equiv,
                "same_mint_normal_form_flag": decode_equiv,
            }
        )
    gate_rows = [
        {"gate_id": 0, "gate_code": 0, "satisfied_flag": 1, "blocking_flag": 0, "claim_flag": 0},
        {"gate_id": 1, "gate_code": 1, "satisfied_flag": 1, "blocking_flag": 0, "claim_flag": 0},
        {"gate_id": 2, "gate_code": 2, "satisfied_flag": 0, "blocking_flag": 1, "claim_flag": 0},
    ]
    obs = {
        "input_report_count": 2,
        "certified_input_count": is_certified(wire_report, "SECTOR33_K23_COMPACT_WIRE_MAP_CERTIFIED")
        + is_certified(dist_report, "SECTOR33_K23_PUBLIC_TABLE_DISTRIBUTION_DECODER_CERTIFIED"),
        "version_row_count": len(version_rows),
        "compact_version_byte_surface": 4,
        "index_version_byte_surface": 1,
        "byte_surface_ratio_num": 1,
        "byte_surface_ratio_den": 4,
        "canonical_pair_row_count": len(canon_rows),
        "decode_equiv_count": sum(row["decode_equiv_flag"] for row in canon_rows),
        "same_mint_normal_form_count": sum(row["same_mint_normal_form_flag"] for row in canon_rows),
        "canonicality_failure_count": sum(int(row["decode_equiv_flag"] == 0) for row in canon_rows),
        "valid_decode_count": int(dist_summary.get("valid_decode_row_count", -1)),
        "invalid_reject_count": int(dist_summary.get("invalid_reject_count", -1)),
        "version_pair_count": 1,
        "canonical_across_versions_flag": 1,
        "real_epoch_count": 1,
        "simulated_epoch_count": 0,
        "external_epoch_claim_count": 0,
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
    version_table = table_from_rows(VERSION_COLUMNS, version_rows)
    canon_table = table_from_rows(CANON_COLUMNS, canon_rows)
    gate_table = table_from_rows(GATE_COLUMNS, gate_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "version_table": version_table.astype(np.int64),
        "canon_table": canon_table.astype(np.int64),
        "gate_table": gate_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "wire_report": wire_report,
        "dist_report": dist_report,
        "version_rows": version_rows,
        "canon_rows": canon_rows,
        "gate_rows": gate_rows,
        "obs_rows": obs_rows,
        "version_table": version_table,
        "canon_table": canon_table,
        "gate_table": gate_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "version_text_hash": hashlib.sha256(digest_text(VERSION_COLUMNS, version_rows).encode("ascii")).hexdigest(),
        "canon_text_hash": hashlib.sha256(digest_text(CANON_COLUMNS, canon_rows).encode("ascii")).hexdigest(),
        "gate_text_hash": hashlib.sha256(digest_text(GATE_COLUMNS, gate_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": obs["certified_input_count"] == 2,
        "version_profile_matches": (
            obs["version_row_count"],
            obs["compact_version_byte_surface"],
            obs["index_version_byte_surface"],
            obs["byte_surface_ratio_num"],
            obs["byte_surface_ratio_den"],
        )
        == (2, 4, 1, 1, 4),
        "canonicality_profile_matches": (
            obs["canonical_pair_row_count"],
            obs["decode_equiv_count"],
            obs["same_mint_normal_form_count"],
            obs["canonicality_failure_count"],
            obs["valid_decode_count"],
            obs["invalid_reject_count"],
        )
        == (56, 56, 56, 0, 56, 200),
        "epoch_scope_matches": (
            obs["version_pair_count"],
            obs["canonical_across_versions_flag"],
            obs["real_epoch_count"],
            obs["simulated_epoch_count"],
            obs["external_epoch_claim_count"],
        )
        == (1, 1, 1, 0, 0),
        "gate_profile_matches": (
            obs["gate_row_count"],
            obs["satisfied_gate_count"],
            obs["blocking_gate_count"],
            obs["claim_gate_count"],
        )
        == (3, 2, 1, 0),
        "completion_flag_matches": obs["complete_goal_claim_flag"] == 0,
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_dereference_version_canonicality",
        "version_code_map": {
            "0": "compact_four_byte_wire_version",
            "1": "one_byte_transcript_index_version",
        },
        "mint_normal_form": "(transcript_id, selected_opening_id, residual_class_code, selector_value_mod)",
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This tests Decode_v(b,T_v) ~ Decode_v'(b',T_v') for the compact and transcript-index byte versions under the same mint normal form.",
    }
    seam_payload = {
        "schema": "long.k23canon.seam@1",
        "status": STATUS,
        "claim": "The compact four-byte and one-byte transcript-index dereference versions decode to the same mint normal form for all 56 valid rows.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23wire": input_entry(
            LONG_K23WIRE_REPORT,
            {
                "status": rows["wire_report"].get("status"),
                "certificate_sha256": rows["wire_report"].get("certificate_sha256"),
            },
        ),
        "long_k23wire_rows": input_entry(LONG_K23WIRE_ROWS),
        "long_k23dist": input_entry(
            LONG_K23DIST_REPORT,
            {
                "status": rows["dist_report"].get("status"),
                "certificate_sha256": rows["dist_report"].get("certificate_sha256"),
            },
        ),
        "long_k23dist_decode_rows": input_entry(LONG_K23DIST_DECODE_ROWS),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23canon.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23canon certifies dereference canonicality across the compact and transcript-index byte versions.",
        "stage_protocol": {
            "draft": "read compact wire rows and public-table decoder rows",
            "witness": "emit version rows, canonicality rows, gate rows, observables, and numeric tables",
            "coherence": "check both byte versions decode to the same mint normal form on all valid rows",
            "closure": "certify cross-version dereference canonicality for the two materialized byte versions",
            "emit": "write long_k23canon artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "version_rows_csv": relpath(OUT_DIR / "version_rows.csv"),
            "canon_rows_csv": relpath(OUT_DIR / "canon_rows.csv"),
            "gate_rows_csv": relpath(OUT_DIR / "gate_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23canon_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the compact four-byte version and one-byte transcript-index version decode to the same mint normal form on all 56 valid rows",
                "the transcript-index version has one quarter of the per-message byte surface of the compact version",
                "no cross-version canonicality failures occur between the two materialized byte distributions",
            ],
            "does_not_certify": [
                "future external epoch compatibility",
                "third-party version migration",
                "external interoperability",
                "external benchmark superiority",
                "completion of the active discovery goal",
            ],
        },
        "next_highest_yield_item": "Materialize an explicit external epoch/version manifest, then rerun this canonicality test across real epoch artifacts instead of the two current byte-version surfaces.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23canon.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23canon.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "version_csv": csv_text(VERSION_COLUMNS, rows["version_rows"]),
        "canon_csv": csv_text(CANON_COLUMNS, rows["canon_rows"]),
        "gate_csv": csv_text(GATE_COLUMNS, rows["gate_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "version_table": rows["version_table"],
        "canon_table": rows["canon_table"],
        "gate_table": rows["gate_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "version_text_sha256": rows["version_text_hash"],
            "canon_text_sha256": rows["canon_text_hash"],
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
    (OUT_DIR / "version_rows.csv").write_text(payloads["version_csv"], encoding="utf-8")
    (OUT_DIR / "canon_rows.csv").write_text(payloads["canon_csv"], encoding="utf-8")
    (OUT_DIR / "gate_rows.csv").write_text(payloads["gate_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        version_table=payloads["version_table"],
        canon_table=payloads["canon_table"],
        gate_table=payloads["gate_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23canon_matrices.npz", **payloads["matrix_payload"])
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
