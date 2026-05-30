from __future__ import annotations

import csv
import hashlib
import json
from math import gcd
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


THEOREM_ID = "long_k23ptab"
STATUS = "SECTOR33_K23_PUBLIC_TABLE_EQUIVALENCE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23ptab.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23ptab.py"

LONG_K23COP_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23cop" / "report.json"
LONG_K23COP_PUBLIC = D20_INVARIANTS / "proof_obligations" / "long_k23cop" / "public_transcript.csv"
LONG_K23COP_OPENINGS = D20_INVARIANTS / "proof_obligations" / "long_k23cop" / "opening_rows.csv"
LONG_K23WIRE_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23wire" / "report.json"
LONG_K23WIRE_ROWS = D20_INVARIANTS / "proof_obligations" / "long_k23wire" / "wire_rows.csv"
LONG_K23PTRAN_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23ptran" / "report.json"

EQUIV_TEXT_HASH = "08dc263784c0a132ab0a8d67de020e07073f00275ca70fbbd7480c0caaa73517"
GATE_TEXT_HASH = "ecdf1e0531665bf954ccde173e9ce3af1ba0fab5f37dabae1a22187510662b34"
OBS_TEXT_HASH = "7f2821eed8bd480452f16ca1d73c68ce4cf18e33279cc6cacc3e6897a5021d17"
MATRIX_SHA256 = "382771c94a874fa0a05b533015443e0c9137fe760de8382efadc1bd5f34a4af4"

EQUIV_COLUMNS = [
    "equiv_id",
    "transcript_id",
    "derived_selected_opening_id",
    "wire_selected_opening_id",
    "derived_residual_class_code",
    "wire_residual_class_code",
    "derived_selector_value_mod",
    "wire_selector_value_mod",
    "transcript_only_bytes",
    "wire_row_bytes",
    "derived_match_flag",
    "public_table_equivalence_flag",
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
    "public_transcript_count",
    "opening_row_count",
    "wire_row_count",
    "equiv_row_count",
    "derived_match_count",
    "public_table_equivalence_count",
    "transcript_only_bytes_per_row",
    "wire_row_bytes",
    "transcript_only_total_bytes",
    "wire_total_bytes",
    "baseline_public_exchange_bytes",
    "saved_vs_wire_bytes",
    "saved_vs_baseline_bytes",
    "saved_vs_wire_num",
    "saved_vs_wire_den",
    "saved_vs_baseline_num",
    "saved_vs_baseline_den",
    "selector_formula_count",
    "max_transcript_id",
    "max_selected_opening_id",
    "max_residual_class_code",
    "max_selector_value_mod",
    "one_byte_transcript_index_flag",
    "certificate_resident_table_flag",
    "per_message_transport_potential_flag",
    "external_improvement_claim_count",
    "runtime_distribution_claim_count",
    "gate_row_count",
    "satisfied_gate_count",
    "blocking_gate_count",
    "claim_gate_count",
    "public_transport_potential_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["equiv_table", "gate_table", "observable_vector"]
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


def reduce_ratio(numerator: int, denominator: int) -> tuple[int, int]:
    divisor = gcd(abs(numerator), abs(denominator))
    return numerator // divisor, denominator // divisor


def build_rows() -> dict[str, Any]:
    cop_report = load_json(LONG_K23COP_REPORT)
    wire_report = load_json(LONG_K23WIRE_REPORT)
    ptran_report = load_json(LONG_K23PTRAN_REPORT)
    ptran_summary = summary(ptran_report)
    public_rows = read_csv_rows(LONG_K23COP_PUBLIC)
    opening_rows = read_csv_rows(LONG_K23COP_OPENINGS)
    wire_rows = read_csv_rows(LONG_K23WIRE_ROWS)

    openings_by_transcript: dict[int, list[dict[str, str]]] = {}
    for row in opening_rows:
        transcript_id = int(row["transcript_id"])
        openings_by_transcript.setdefault(transcript_id, []).append(row)
    for transcript_id in openings_by_transcript:
        openings_by_transcript[transcript_id].sort(key=lambda row: int(row["opening_id"]))
    wire_by_transcript = {int(row["transcript_id"]): row for row in wire_rows}

    equiv_rows = []
    for public_row in public_rows:
        transcript_id = int(public_row["transcript_id"])
        openings = openings_by_transcript[transcript_id]
        selector = selector_mod(public_row["public_digest_sha256"], len(openings))
        selected = openings[selector]
        wire_row = wire_by_transcript[transcript_id]
        derived_selected_opening_id = int(selected["opening_id"])
        derived_residual_class_code = int(public_row["residual_class_code"])
        derived_selector_value_mod = selector
        wire_selected_opening_id = int(wire_row["selected_opening_id"])
        wire_residual_class_code = int(wire_row["residual_class_code"])
        wire_selector_value_mod = int(wire_row["selector_value_mod"])
        derived_match = int(
            derived_selected_opening_id == wire_selected_opening_id
            and derived_residual_class_code == wire_residual_class_code
            and derived_selector_value_mod == wire_selector_value_mod
        )
        equiv_rows.append(
            {
                "equiv_id": len(equiv_rows),
                "transcript_id": transcript_id,
                "derived_selected_opening_id": derived_selected_opening_id,
                "wire_selected_opening_id": wire_selected_opening_id,
                "derived_residual_class_code": derived_residual_class_code,
                "wire_residual_class_code": wire_residual_class_code,
                "derived_selector_value_mod": derived_selector_value_mod,
                "wire_selector_value_mod": wire_selector_value_mod,
                "transcript_only_bytes": 1,
                "wire_row_bytes": int(wire_row["wire_row_bytes"]),
                "derived_match_flag": derived_match,
                "public_table_equivalence_flag": derived_match,
            }
        )

    transcript_total = sum(row["transcript_only_bytes"] for row in equiv_rows)
    wire_total = sum(row["wire_row_bytes"] for row in equiv_rows)
    baseline = int(ptran_summary.get("baseline_public_exchange_bytes", -1))
    saved_vs_wire = wire_total - transcript_total
    saved_vs_baseline = baseline - transcript_total
    saved_wire_ratio = reduce_ratio(saved_vs_wire, wire_total)
    saved_baseline_ratio = reduce_ratio(saved_vs_baseline, baseline)
    gate_rows = [
        {"gate_id": 0, "gate_code": 0, "satisfied_flag": 1, "blocking_flag": 0, "claim_flag": 0},
        {"gate_id": 1, "gate_code": 1, "satisfied_flag": 1, "blocking_flag": 0, "claim_flag": 0},
        {"gate_id": 2, "gate_code": 2, "satisfied_flag": 0, "blocking_flag": 1, "claim_flag": 0},
        {"gate_id": 3, "gate_code": 3, "satisfied_flag": 0, "blocking_flag": 1, "claim_flag": 0},
        {"gate_id": 4, "gate_code": 4, "satisfied_flag": 0, "blocking_flag": 1, "claim_flag": 0},
    ]
    obs = {
        "input_report_count": 3,
        "certified_input_count": is_certified(cop_report, "SECTOR33_K23_COMMIT_OPEN_TRANSCRIPT_CERTIFIED")
        + is_certified(wire_report, "SECTOR33_K23_COMPACT_WIRE_MAP_CERTIFIED")
        + is_certified(ptran_report, "SECTOR33_K23_PUBLIC_TRANSPORT_POTENTIAL_CERTIFIED"),
        "public_transcript_count": len(public_rows),
        "opening_row_count": len(opening_rows),
        "wire_row_count": len(wire_rows),
        "equiv_row_count": len(equiv_rows),
        "derived_match_count": sum(row["derived_match_flag"] for row in equiv_rows),
        "public_table_equivalence_count": sum(row["public_table_equivalence_flag"] for row in equiv_rows),
        "transcript_only_bytes_per_row": 1,
        "wire_row_bytes": 4,
        "transcript_only_total_bytes": transcript_total,
        "wire_total_bytes": wire_total,
        "baseline_public_exchange_bytes": baseline,
        "saved_vs_wire_bytes": saved_vs_wire,
        "saved_vs_baseline_bytes": saved_vs_baseline,
        "saved_vs_wire_num": saved_wire_ratio[0],
        "saved_vs_wire_den": saved_wire_ratio[1],
        "saved_vs_baseline_num": saved_baseline_ratio[0],
        "saved_vs_baseline_den": saved_baseline_ratio[1],
        "selector_formula_count": len(equiv_rows),
        "max_transcript_id": max(row["transcript_id"] for row in equiv_rows),
        "max_selected_opening_id": max(row["derived_selected_opening_id"] for row in equiv_rows),
        "max_residual_class_code": max(row["derived_residual_class_code"] for row in equiv_rows),
        "max_selector_value_mod": max(row["derived_selector_value_mod"] for row in equiv_rows),
        "one_byte_transcript_index_flag": int(max(row["transcript_id"] for row in equiv_rows) < 256),
        "certificate_resident_table_flag": 1,
        "per_message_transport_potential_flag": 1,
        "external_improvement_claim_count": 0,
        "runtime_distribution_claim_count": 0,
        "gate_row_count": len(gate_rows),
        "satisfied_gate_count": sum(row["satisfied_flag"] for row in gate_rows),
        "blocking_gate_count": sum(row["blocking_flag"] for row in gate_rows),
        "claim_gate_count": sum(row["claim_flag"] for row in gate_rows),
        "public_transport_potential_flag": int(ptran_summary.get("public_transport_potential_flag", -1)),
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    equiv_table = table_from_rows(EQUIV_COLUMNS, equiv_rows)
    gate_table = table_from_rows(GATE_COLUMNS, gate_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "equiv_table": equiv_table.astype(np.int64),
        "gate_table": gate_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "cop_report": cop_report,
        "wire_report": wire_report,
        "ptran_report": ptran_report,
        "equiv_rows": equiv_rows,
        "gate_rows": gate_rows,
        "obs_rows": obs_rows,
        "equiv_table": equiv_table,
        "gate_table": gate_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "equiv_text_hash": hashlib.sha256(digest_text(EQUIV_COLUMNS, equiv_rows).encode("ascii")).hexdigest(),
        "gate_text_hash": hashlib.sha256(digest_text(GATE_COLUMNS, gate_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": obs["certified_input_count"] == 3,
        "equivalence_profile_matches": (
            obs["public_transcript_count"],
            obs["opening_row_count"],
            obs["wire_row_count"],
            obs["equiv_row_count"],
            obs["derived_match_count"],
            obs["public_table_equivalence_count"],
        )
        == (56, 91, 56, 56, 56, 56),
        "transport_byte_profile_matches": (
            obs["transcript_only_bytes_per_row"],
            obs["wire_row_bytes"],
            obs["transcript_only_total_bytes"],
            obs["wire_total_bytes"],
            obs["baseline_public_exchange_bytes"],
            obs["saved_vs_wire_bytes"],
            obs["saved_vs_baseline_bytes"],
            obs["saved_vs_wire_num"],
            obs["saved_vs_wire_den"],
            obs["saved_vs_baseline_num"],
            obs["saved_vs_baseline_den"],
        )
        == (1, 4, 56, 224, 1568, 168, 1512, 3, 4, 27, 28),
        "one_byte_ranges_match": (
            obs["max_transcript_id"],
            obs["max_selected_opening_id"],
            obs["max_residual_class_code"],
            obs["max_selector_value_mod"],
            obs["one_byte_transcript_index_flag"],
        )
        == (55, 90, 55, 5, 1),
        "claim_gates_match": (
            obs["certificate_resident_table_flag"],
            obs["per_message_transport_potential_flag"],
            obs["external_improvement_claim_count"],
            obs["runtime_distribution_claim_count"],
            obs["gate_row_count"],
            obs["satisfied_gate_count"],
            obs["blocking_gate_count"],
            obs["claim_gate_count"],
        )
        == (1, 1, 0, 0, 5, 2, 3, 0),
        "frontier_flags_match": (
            obs["public_transport_potential_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (1, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_public_table_equivalence",
        "selector_formula": "selector = int(public_digest_sha256[:16], 16) mod transcript_opening_count",
        "gate_code_map": {
            "0": "certificate_resident_table",
            "1": "wire_field_derivation_equivalence",
            "2": "runtime_public_distribution",
            "3": "external_interop_profile",
            "4": "external_benchmark_claim",
        },
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies that the four-byte compact wire row is derivable from a one-byte transcript index when the certified transcript/opening table is already public.",
    }
    seam_payload = {
        "schema": "long.k23ptab.seam@1",
        "status": STATUS,
        "claim": "The K23 shared table is certificate-resident and recovers the compact wire fields from transcript_id.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23cop": input_entry(
            LONG_K23COP_REPORT,
            {
                "status": rows["cop_report"].get("status"),
                "certificate_sha256": rows["cop_report"].get("certificate_sha256"),
            },
        ),
        "long_k23cop_public": input_entry(LONG_K23COP_PUBLIC),
        "long_k23cop_openings": input_entry(LONG_K23COP_OPENINGS),
        "long_k23wire": input_entry(
            LONG_K23WIRE_REPORT,
            {
                "status": rows["wire_report"].get("status"),
                "certificate_sha256": rows["wire_report"].get("certificate_sha256"),
            },
        ),
        "long_k23wire_rows": input_entry(LONG_K23WIRE_ROWS),
        "long_k23ptran": input_entry(
            LONG_K23PTRAN_REPORT,
            {
                "status": rows["ptran_report"].get("status"),
                "certificate_sha256": rows["ptran_report"].get("certificate_sha256"),
            },
        ),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23ptab.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23ptab certifies certificate-resident public-table equivalence for the compact K23 wire row.",
        "stage_protocol": {
            "draft": "read commit/open transcript, compact wire rows, and public-transport potential report",
            "witness": "emit equivalence rows, claim gates, observables, and numeric tables",
            "coherence": "recompute selected opening, residual code, and selector from transcript_id plus certified transcript/opening table",
            "closure": "certify transcript-index equivalence under certificate-resident table assumptions",
            "emit": "write long_k23ptab artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "equiv_rows_csv": relpath(OUT_DIR / "equiv_rows.csv"),
            "gate_rows_csv": relpath(OUT_DIR / "gate_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23ptab_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "all 56 compact wire rows are recovered from transcript_id plus the certified transcript/opening table",
                "the per-row transport field can be reduced from four one-byte fields to one one-byte transcript index under the certificate-resident table condition",
                "the transcript-index surface is 56 bytes over the 56-row challenge surface",
                "the transcript-index surface saves 168/224 = 3/4 against the compact wire row surface",
                "the transcript-index surface saves 1512/1568 = 27/28 against the selected public baseline",
            ],
            "does_not_certify": [
                "external runtime distribution of the table",
                "drop-in public protocol compatibility",
                "external speed or size improvement",
                "security superiority",
                "standards compliance",
                "deployment readiness",
                "completion of the active discovery goal",
            ],
        },
        "next_highest_yield_item": "Turn certificate-resident table equivalence into a runtime public-table distribution certificate, or separately prove a self-contained transcript-index compression.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23ptab.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23ptab.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "equiv_csv": csv_text(EQUIV_COLUMNS, rows["equiv_rows"]),
        "gate_csv": csv_text(GATE_COLUMNS, rows["gate_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "equiv_table": rows["equiv_table"],
        "gate_table": rows["gate_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "equiv_text_sha256": rows["equiv_text_hash"],
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
    (OUT_DIR / "equiv_rows.csv").write_text(payloads["equiv_csv"], encoding="utf-8")
    (OUT_DIR / "gate_rows.csv").write_text(payloads["gate_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        equiv_table=payloads["equiv_table"],
        gate_table=payloads["gate_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23ptab_matrices.npz", **payloads["matrix_payload"])
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
