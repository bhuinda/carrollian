from __future__ import annotations

import csv
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


THEOREM_ID = "long_k23wire"
STATUS = "SECTOR33_K23_COMPACT_WIRE_MAP_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23wire.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23wire.py"
LONG_K23NORM_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23norm" / "report.json"
LONG_K23NORM_ROWS = D20_INVARIANTS / "proof_obligations" / "long_k23norm" / "normalization_rows.csv"
LONG_K23CHAL_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23chal" / "report.json"
LONG_K23CHAL_ROWS = D20_INVARIANTS / "proof_obligations" / "long_k23chal" / "challenge_rows.csv"

WIRE_TEXT_HASH = "bd05f2cdd991184de03350ac7eed034ea2b08d0bff71a77ad3fb8ff03911ab4d"
EQUATION_TEXT_HASH = "2666f1c8fd8de1b9978f1347924a721dee62706e27641141f0d884df38ba07e6"
LIMIT_TEXT_HASH = "b5235b4af52f7c1a115fc8a7c72af531320f853035d8539a02a1e761beac5709"
OBS_TEXT_HASH = "39f1a47d54d3c432993a51f51eb35a9ee94c2a6d3f4e390babddf14d60138de3"
MATRIX_SHA256 = "e5c8bb9114222049eaeff25eb3fe602a4d0abffd49f7c4a08e15f7065d02d34b"

WIRE_COLUMNS = [
    "wire_id",
    "transcript_id",
    "selected_opening_id",
    "residual_class_code",
    "selector_value_mod",
    "transcript_index_bytes",
    "opening_index_bytes",
    "residual_code_bytes",
    "selector_bytes",
    "wire_row_bytes",
    "table_index_dependency_flag",
    "digest_free_wire_flag",
    "wire_equivalence_claim_flag",
    "external_improvement_claim_flag",
]
EQUATION_COLUMNS = [
    "equation_id",
    "equation_code",
    "left_value",
    "right_value",
    "equality_flag",
    "strict_less_than_flag",
    "claim_flag",
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
    "wire_row_count",
    "max_transcript_id",
    "max_selected_opening_id",
    "max_residual_class_code",
    "max_selector_value_mod",
    "one_byte_field_count",
    "wire_row_bytes",
    "wire_total_bytes",
    "norm_internal_public_digest_bytes",
    "norm_baseline_public_exchange_bytes",
    "saved_vs_internal_digest_bytes",
    "delta_vs_baseline_public_bytes",
    "compact_vs_internal_digest_flag",
    "compact_vs_baseline_public_flag",
    "digest_free_wire_count",
    "table_index_dependency_count",
    "wire_equivalence_claim_count",
    "external_improvement_claim_count",
    "equation_row_count",
    "equation_pass_count",
    "limit_row_count",
    "open_limit_count",
    "overclaim_count",
    "compact_wire_map_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["wire_table", "equation_table", "limit_table", "observable_vector"]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


def summary(report: dict[str, Any]) -> dict[str, Any]:
    witness = report.get("witness", {})
    if not isinstance(witness, dict):
        return {}
    payload = witness.get("summary", {})
    return payload if isinstance(payload, dict) else {}


def read_csv_rows(path: Any) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def is_certified(report: dict[str, Any], status: str) -> int:
    return int(report.get("status") == status and report.get("all_checks_pass") is True)


def build_rows() -> dict[str, Any]:
    norm_report = load_json(LONG_K23NORM_REPORT)
    chal_report = load_json(LONG_K23CHAL_REPORT)
    norm_summary = summary(norm_report)
    norm_row = read_csv_rows(LONG_K23NORM_ROWS)[0]
    challenge_rows = read_csv_rows(LONG_K23CHAL_ROWS)
    wire_rows = []
    for row in challenge_rows:
        wire_rows.append(
            {
                "wire_id": int(row["challenge_id"]),
                "transcript_id": int(row["transcript_id"]),
                "selected_opening_id": int(row["selected_opening_id"]),
                "residual_class_code": int(row["residual_class_code"]),
                "selector_value_mod": int(row["selector_value_mod"]),
                "transcript_index_bytes": 1,
                "opening_index_bytes": 1,
                "residual_code_bytes": 1,
                "selector_bytes": 1,
                "wire_row_bytes": 4,
                "table_index_dependency_flag": 1,
                "digest_free_wire_flag": 1,
                "wire_equivalence_claim_flag": 0,
                "external_improvement_claim_flag": 0,
            }
        )
    wire_total_bytes = sum(row["wire_row_bytes"] for row in wire_rows)
    internal_public_digest_bytes = int(norm_row["internal_public_digest_bytes"])
    baseline_public_exchange_bytes = int(norm_row["baseline_public_exchange_bytes"])
    saved_vs_internal = internal_public_digest_bytes - wire_total_bytes
    delta_vs_baseline = wire_total_bytes - baseline_public_exchange_bytes
    equation_rows = [
        {"equation_id": 0, "equation_code": 0, "left_value": wire_total_bytes, "right_value": 56 * 4, "equality_flag": 1, "strict_less_than_flag": 0, "claim_flag": 0},
        {"equation_id": 1, "equation_code": 1, "left_value": saved_vs_internal, "right_value": internal_public_digest_bytes - wire_total_bytes, "equality_flag": 1, "strict_less_than_flag": 0, "claim_flag": 0},
        {"equation_id": 2, "equation_code": 2, "left_value": wire_total_bytes, "right_value": internal_public_digest_bytes, "equality_flag": 0, "strict_less_than_flag": int(wire_total_bytes < internal_public_digest_bytes), "claim_flag": 0},
        {"equation_id": 3, "equation_code": 3, "left_value": wire_total_bytes, "right_value": baseline_public_exchange_bytes, "equality_flag": 0, "strict_less_than_flag": int(wire_total_bytes < baseline_public_exchange_bytes), "claim_flag": 0},
        {"equation_id": 4, "equation_code": 4, "left_value": delta_vs_baseline, "right_value": wire_total_bytes - baseline_public_exchange_bytes, "equality_flag": 1, "strict_less_than_flag": 0, "claim_flag": 0},
    ]
    limit_rows = [
        {"limit_id": 0, "limit_code": 0, "open_flag": 1, "required_before_external_claim_flag": 1, "overclaim_flag": 0},
        {"limit_id": 1, "limit_code": 1, "open_flag": 1, "required_before_external_claim_flag": 1, "overclaim_flag": 0},
        {"limit_id": 2, "limit_code": 2, "open_flag": 1, "required_before_external_claim_flag": 1, "overclaim_flag": 0},
        {"limit_id": 3, "limit_code": 3, "open_flag": 1, "required_before_external_claim_flag": 1, "overclaim_flag": 0},
    ]
    obs = {
        "input_report_count": 2,
        "certified_input_count": is_certified(norm_report, "SECTOR33_K23_MLKEM512_NORMALIZATION_CERTIFIED")
        + is_certified(chal_report, "SECTOR33_K23_VERIFIER_CHALLENGE_CERTIFIED"),
        "wire_row_count": len(wire_rows),
        "max_transcript_id": max(row["transcript_id"] for row in wire_rows),
        "max_selected_opening_id": max(row["selected_opening_id"] for row in wire_rows),
        "max_residual_class_code": max(row["residual_class_code"] for row in wire_rows),
        "max_selector_value_mod": max(row["selector_value_mod"] for row in wire_rows),
        "one_byte_field_count": 4,
        "wire_row_bytes": 4,
        "wire_total_bytes": wire_total_bytes,
        "norm_internal_public_digest_bytes": internal_public_digest_bytes,
        "norm_baseline_public_exchange_bytes": baseline_public_exchange_bytes,
        "saved_vs_internal_digest_bytes": saved_vs_internal,
        "delta_vs_baseline_public_bytes": delta_vs_baseline,
        "compact_vs_internal_digest_flag": int(wire_total_bytes < internal_public_digest_bytes),
        "compact_vs_baseline_public_flag": int(wire_total_bytes < baseline_public_exchange_bytes),
        "digest_free_wire_count": sum(row["digest_free_wire_flag"] for row in wire_rows),
        "table_index_dependency_count": sum(row["table_index_dependency_flag"] for row in wire_rows),
        "wire_equivalence_claim_count": sum(row["wire_equivalence_claim_flag"] for row in wire_rows),
        "external_improvement_claim_count": sum(row["external_improvement_claim_flag"] for row in wire_rows),
        "equation_row_count": len(equation_rows),
        "equation_pass_count": sum(int(row["equality_flag"] == 1 or row["strict_less_than_flag"] == 1) for row in equation_rows),
        "limit_row_count": len(limit_rows),
        "open_limit_count": sum(row["open_flag"] for row in limit_rows),
        "overclaim_count": sum(row["overclaim_flag"] for row in limit_rows),
        "compact_wire_map_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    wire_table = table_from_rows(WIRE_COLUMNS, wire_rows)
    equation_table = table_from_rows(EQUATION_COLUMNS, equation_rows)
    limit_table = table_from_rows(LIMIT_COLUMNS, limit_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "wire_table": wire_table.astype(np.int64),
        "equation_table": equation_table.astype(np.int64),
        "limit_table": limit_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "norm_report": norm_report,
        "chal_report": chal_report,
        "norm_summary": norm_summary,
        "wire_rows": wire_rows,
        "equation_rows": equation_rows,
        "limit_rows": limit_rows,
        "obs_rows": obs_rows,
        "wire_table": wire_table,
        "equation_table": equation_table,
        "limit_table": limit_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "wire_text_hash": hashlib.sha256(digest_text(WIRE_COLUMNS, wire_rows).encode("ascii")).hexdigest(),
        "equation_text_hash": hashlib.sha256(digest_text(EQUATION_COLUMNS, equation_rows).encode("ascii")).hexdigest(),
        "limit_text_hash": hashlib.sha256(digest_text(LIMIT_COLUMNS, limit_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": obs["certified_input_count"] == 2,
        "one_byte_ranges_match": (
            obs["wire_row_count"],
            obs["max_transcript_id"],
            obs["max_selected_opening_id"],
            obs["max_residual_class_code"],
            obs["max_selector_value_mod"],
        )
        == (56, 55, 90, 55, 5),
        "wire_profile_matches": (
            obs["one_byte_field_count"],
            obs["wire_row_bytes"],
            obs["wire_total_bytes"],
            obs["digest_free_wire_count"],
            obs["table_index_dependency_count"],
        )
        == (4, 4, 224, 56, 56),
        "compact_equations_match": (
            obs["norm_internal_public_digest_bytes"],
            obs["norm_baseline_public_exchange_bytes"],
            obs["saved_vs_internal_digest_bytes"],
            obs["delta_vs_baseline_public_bytes"],
            obs["compact_vs_internal_digest_flag"],
            obs["compact_vs_baseline_public_flag"],
            obs["equation_row_count"],
            obs["equation_pass_count"],
        )
        == (5376, 1568, 5152, -1344, 1, 1, 5, 5),
        "claim_boundary_matches": (
            obs["wire_equivalence_claim_count"],
            obs["external_improvement_claim_count"],
            obs["compact_wire_map_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (0, 0, 1, 0),
        "limit_profile_matches": (
            obs["limit_row_count"],
            obs["open_limit_count"],
            obs["overclaim_count"],
        )
        == (4, 4, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_compact_table_index_wire_map",
        "wire_field_map": {
            "0": "transcript_id",
            "1": "selected_opening_id",
            "2": "residual_class_code",
            "3": "selector_value_mod",
        },
        "equation_code_map": {
            "0": "wire_total_bytes",
            "1": "saved_vs_internal_digest_bytes",
            "2": "wire_total_less_than_internal_digest_bytes",
            "3": "wire_total_less_than_baseline_public_exchange_bytes",
            "4": "delta_vs_baseline_public_bytes",
        },
        "limit_code_map": {
            "0": "shared_certified_table_required",
            "1": "wire_format_equivalence",
            "2": "security_reduction",
            "3": "interop_or_deployment",
        },
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This certifies a compact table-indexed local wire map for the selected candidate, while leaving public wire equivalence and external improvement claims open.",
    }
    seam_payload = {
        "schema": "long.k23wire.seam@1",
        "status": STATUS,
        "claim": "The selected K23 normalization row has a compact shared-table wire map over the certified challenge table.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23norm": input_entry(
            LONG_K23NORM_REPORT,
            {
                "status": rows["norm_report"].get("status"),
                "certificate_sha256": rows["norm_report"].get("certificate_sha256"),
            },
        ),
        "long_k23norm_rows": input_entry(LONG_K23NORM_ROWS),
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
        "schema": "long.k23wire.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23wire certifies a compact table-indexed wire map for the selected K23 candidate.",
        "stage_protocol": {
            "draft": "read long_k23norm and the certified challenge table",
            "witness": "emit wire rows, byte equations, open-limit rows, observables, and numeric tables",
            "coherence": "check one-byte index ranges, compact-byte equations, and explicit nonclaims",
            "closure": "certify compact shared-table encoding without claiming public wire equivalence or external improvement",
            "emit": "write long_k23wire artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "wire_rows_csv": relpath(OUT_DIR / "wire_rows.csv"),
            "equation_rows_csv": relpath(OUT_DIR / "equation_rows.csv"),
            "limit_rows_csv": relpath(OUT_DIR / "limit_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23wire_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "all 56 challenge rows can be represented by four one-byte table-index fields",
                "the compact local wire map totals 224 bytes over the 56-row challenge surface",
                "the local wire map is smaller than the digest-row surface and the selected baseline public byte count",
                "the map depends on a shared certified table",
            ],
            "does_not_certify": [
                "public wire-format equivalence",
                "external speed or size improvement",
                "security superiority",
                "standards compliance",
                "drop-in replacement behavior",
                "deployment readiness",
                "completion of the active discovery goal",
            ],
        },
        "next_highest_yield_item": "Decide whether shared-table dependence is acceptable: either lift the compact wire map into a self-contained public transcript or demote the external-efficiency path.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23wire.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23wire.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "wire_csv": csv_text(WIRE_COLUMNS, rows["wire_rows"]),
        "equation_csv": csv_text(EQUATION_COLUMNS, rows["equation_rows"]),
        "limit_csv": csv_text(LIMIT_COLUMNS, rows["limit_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "wire_table": rows["wire_table"],
        "equation_table": rows["equation_table"],
        "limit_table": rows["limit_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "wire_text_sha256": rows["wire_text_hash"],
            "equation_text_sha256": rows["equation_text_hash"],
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
    (OUT_DIR / "wire_rows.csv").write_text(payloads["wire_csv"], encoding="utf-8")
    (OUT_DIR / "equation_rows.csv").write_text(payloads["equation_csv"], encoding="utf-8")
    (OUT_DIR / "limit_rows.csv").write_text(payloads["limit_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        wire_table=payloads["wire_table"],
        equation_table=payloads["equation_table"],
        limit_table=payloads["limit_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23wire_matrices.npz", **payloads["matrix_payload"])
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
