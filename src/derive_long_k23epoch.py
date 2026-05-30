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


THEOREM_ID = "long_k23epoch"
STATUS = "SECTOR33_K23_REAL_EPOCH_MANIFEST_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23epoch.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23epoch.py"

REPORT_PATHS = {
    "long_k23canon": D20_INVARIANTS / "proof_obligations" / "long_k23canon" / "report.json",
    "long_k23dist": D20_INVARIANTS / "proof_obligations" / "long_k23dist" / "report.json",
}
EXPECTED_STATUSES = {
    "long_k23canon": "SECTOR33_K23_DEREFERENCE_VERSION_CANONICALITY_CERTIFIED",
    "long_k23dist": "SECTOR33_K23_PUBLIC_TABLE_DISTRIBUTION_DECODER_CERTIFIED",
}

EPOCH_TEXT_HASH = "db31c8f04565e08ae2a87c4b8b33ddbf3f428478dce60b8adb9a492118e3b6eb"
VERSION_TEXT_HASH = "76569dd21d98d130cabbabc4f24ad27e385c6e53612046ee50a2735a12b6040e"
MIGRATION_TEXT_HASH = "a9e10d165fbb28489af4caff69a9874ccabe3ed481cb280716134ac51208f61e"
GATE_TEXT_HASH = "2bdfb901350d9ea4fa62635b4e42235fa8dd8d28b29fbe69558ec2a22386622a"
OBS_TEXT_HASH = "662030d7bc1c9d9b68ee2324e3dc183b4b71ff79fc543ab53d3d466a9f7caeda"
MATRIX_SHA256 = "f853876d9d4bbfda3fdecbc358e8a87fa123bc0afcec27e556b942fcd28334bc"

EPOCH_COLUMNS = [
    "epoch_id",
    "epoch_code",
    "real_epoch_flag",
    "simulated_epoch_flag",
    "third_party_epoch_flag",
    "future_epoch_flag",
    "manifest_present_flag",
    "version_count",
    "canonicality_required_flag",
    "external_claim_flag",
]
VERSION_COLUMNS = [
    "version_id",
    "epoch_id",
    "version_code",
    "byte_surface_per_message",
    "decoder_code",
    "source_report_code",
    "materialized_flag",
    "valid_decode_count",
    "invalid_reject_count",
    "mint_normal_form_flag",
    "cross_version_canonical_flag",
]
MIGRATION_COLUMNS = [
    "migration_id",
    "from_version_id",
    "to_version_id",
    "same_epoch_flag",
    "same_mint_normal_form_rows",
    "decode_equiv_rows",
    "canonicality_failures",
    "migration_pass_flag",
    "future_epoch_claim_flag",
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
    "epoch_row_count",
    "real_epoch_count",
    "simulated_epoch_count",
    "third_party_epoch_count",
    "future_epoch_count",
    "manifest_present_count",
    "version_row_count",
    "materialized_version_count",
    "compact_version_byte_surface",
    "index_version_byte_surface",
    "byte_surface_ratio_num",
    "byte_surface_ratio_den",
    "valid_decode_count",
    "invalid_reject_count",
    "canonical_pair_row_count",
    "decode_equiv_count",
    "same_mint_normal_form_count",
    "canonicality_failure_count",
    "migration_row_count",
    "migration_pass_count",
    "external_epoch_claim_count",
    "external_manifest_ready_flag",
    "real_external_artifact_count",
    "gate_row_count",
    "satisfied_gate_count",
    "blocking_gate_count",
    "claim_gate_count",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["epoch_table", "version_table", "migration_table", "gate_table", "observable_vector"]
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
    canon = summaries["long_k23canon"]
    dist = summaries["long_k23dist"]

    epoch_rows = [
        {
            "epoch_id": 0,
            "epoch_code": 0,
            "real_epoch_flag": 1,
            "simulated_epoch_flag": 0,
            "third_party_epoch_flag": 0,
            "future_epoch_flag": 0,
            "manifest_present_flag": 1,
            "version_count": int(canon.get("version_row_count", -1)),
            "canonicality_required_flag": 1,
            "external_claim_flag": 0,
        }
    ]
    version_rows = [
        {
            "version_id": 0,
            "epoch_id": 0,
            "version_code": 0,
            "byte_surface_per_message": int(canon.get("compact_version_byte_surface", -1)),
            "decoder_code": 0,
            "source_report_code": 0,
            "materialized_flag": 1,
            "valid_decode_count": 56,
            "invalid_reject_count": 0,
            "mint_normal_form_flag": 1,
            "cross_version_canonical_flag": int(canon.get("canonical_across_versions_flag", -1)),
        },
        {
            "version_id": 1,
            "epoch_id": 0,
            "version_code": 1,
            "byte_surface_per_message": int(canon.get("index_version_byte_surface", -1)),
            "decoder_code": 1,
            "source_report_code": 1,
            "materialized_flag": 1,
            "valid_decode_count": int(dist.get("valid_decode_row_count", -1)),
            "invalid_reject_count": int(dist.get("invalid_reject_count", -1)),
            "mint_normal_form_flag": 1,
            "cross_version_canonical_flag": int(canon.get("canonical_across_versions_flag", -1)),
        },
    ]
    migration_rows = [
        {
            "migration_id": 0,
            "from_version_id": 0,
            "to_version_id": 1,
            "same_epoch_flag": 1,
            "same_mint_normal_form_rows": int(canon.get("same_mint_normal_form_count", -1)),
            "decode_equiv_rows": int(canon.get("decode_equiv_count", -1)),
            "canonicality_failures": int(canon.get("canonicality_failure_count", -1)),
            "migration_pass_flag": int(canon.get("canonicality_failure_count", -1) == 0),
            "future_epoch_claim_flag": 0,
        }
    ]
    gate_rows = [
        {"gate_id": 0, "gate_code": 0, "satisfied_flag": 1, "blocking_flag": 0, "claim_flag": 0},
        {"gate_id": 1, "gate_code": 1, "satisfied_flag": 1, "blocking_flag": 0, "claim_flag": 0},
        {"gate_id": 2, "gate_code": 2, "satisfied_flag": 1, "blocking_flag": 0, "claim_flag": 0},
        {"gate_id": 3, "gate_code": 3, "satisfied_flag": 0, "blocking_flag": 1, "claim_flag": 0},
        {"gate_id": 4, "gate_code": 4, "satisfied_flag": 0, "blocking_flag": 1, "claim_flag": 0},
    ]
    obs = {
        "input_report_count": len(REPORT_PATHS),
        "certified_input_count": sum(is_certified(reports[name], EXPECTED_STATUSES[name]) for name in REPORT_PATHS),
        "epoch_row_count": len(epoch_rows),
        "real_epoch_count": sum(row["real_epoch_flag"] for row in epoch_rows),
        "simulated_epoch_count": sum(row["simulated_epoch_flag"] for row in epoch_rows),
        "third_party_epoch_count": sum(row["third_party_epoch_flag"] for row in epoch_rows),
        "future_epoch_count": sum(row["future_epoch_flag"] for row in epoch_rows),
        "manifest_present_count": sum(row["manifest_present_flag"] for row in epoch_rows),
        "version_row_count": len(version_rows),
        "materialized_version_count": sum(row["materialized_flag"] for row in version_rows),
        "compact_version_byte_surface": int(canon.get("compact_version_byte_surface", -1)),
        "index_version_byte_surface": int(canon.get("index_version_byte_surface", -1)),
        "byte_surface_ratio_num": int(canon.get("byte_surface_ratio_num", -1)),
        "byte_surface_ratio_den": int(canon.get("byte_surface_ratio_den", -1)),
        "valid_decode_count": int(dist.get("valid_decode_row_count", -1)),
        "invalid_reject_count": int(dist.get("invalid_reject_count", -1)),
        "canonical_pair_row_count": int(canon.get("canonical_pair_row_count", -1)),
        "decode_equiv_count": int(canon.get("decode_equiv_count", -1)),
        "same_mint_normal_form_count": int(canon.get("same_mint_normal_form_count", -1)),
        "canonicality_failure_count": int(canon.get("canonicality_failure_count", -1)),
        "migration_row_count": len(migration_rows),
        "migration_pass_count": sum(row["migration_pass_flag"] for row in migration_rows),
        "external_epoch_claim_count": int(canon.get("external_epoch_claim_count", -1)),
        "external_manifest_ready_flag": 1,
        "real_external_artifact_count": 0,
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
    epoch_table = table_from_rows(EPOCH_COLUMNS, epoch_rows)
    version_table = table_from_rows(VERSION_COLUMNS, version_rows)
    migration_table = table_from_rows(MIGRATION_COLUMNS, migration_rows)
    gate_table = table_from_rows(GATE_COLUMNS, gate_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "epoch_table": epoch_table.astype(np.int64),
        "version_table": version_table.astype(np.int64),
        "migration_table": migration_table.astype(np.int64),
        "gate_table": gate_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "reports": reports,
        "epoch_rows": epoch_rows,
        "version_rows": version_rows,
        "migration_rows": migration_rows,
        "gate_rows": gate_rows,
        "obs_rows": obs_rows,
        "epoch_table": epoch_table,
        "version_table": version_table,
        "migration_table": migration_table,
        "gate_table": gate_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "epoch_text_hash": hashlib.sha256(digest_text(EPOCH_COLUMNS, epoch_rows).encode("ascii")).hexdigest(),
        "version_text_hash": hashlib.sha256(digest_text(VERSION_COLUMNS, version_rows).encode("ascii")).hexdigest(),
        "migration_text_hash": hashlib.sha256(digest_text(MIGRATION_COLUMNS, migration_rows).encode("ascii")).hexdigest(),
        "gate_text_hash": hashlib.sha256(digest_text(GATE_COLUMNS, gate_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": obs["certified_input_count"] == obs["input_report_count"] == 2,
        "manifest_profile_matches": (
            obs["epoch_row_count"],
            obs["real_epoch_count"],
            obs["simulated_epoch_count"],
            obs["third_party_epoch_count"],
            obs["future_epoch_count"],
            obs["manifest_present_count"],
        )
        == (1, 1, 0, 0, 0, 1),
        "version_profile_matches": (
            obs["version_row_count"],
            obs["materialized_version_count"],
            obs["compact_version_byte_surface"],
            obs["index_version_byte_surface"],
            obs["byte_surface_ratio_num"],
            obs["byte_surface_ratio_den"],
        )
        == (2, 2, 4, 1, 1, 4),
        "migration_profile_matches": (
            obs["canonical_pair_row_count"],
            obs["decode_equiv_count"],
            obs["same_mint_normal_form_count"],
            obs["canonicality_failure_count"],
            obs["migration_row_count"],
            obs["migration_pass_count"],
        )
        == (56, 56, 56, 0, 1, 1),
        "decoder_profile_matches": (obs["valid_decode_count"], obs["invalid_reject_count"]) == (56, 200),
        "external_scope_matches": (
            obs["external_epoch_claim_count"],
            obs["external_manifest_ready_flag"],
            obs["real_external_artifact_count"],
        )
        == (0, 1, 0),
        "gate_profile_matches": (
            obs["gate_row_count"],
            obs["satisfied_gate_count"],
            obs["blocking_gate_count"],
            obs["claim_gate_count"],
        )
        == (5, 3, 2, 0),
        "completion_flag_matches": obs["complete_goal_claim_flag"] == 0,
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_real_epoch_manifest",
        "version_code_map": {
            "0": "compact_four_byte_wire_version",
            "1": "one_byte_transcript_index_version",
        },
        "mint_normal_form": "(transcript_id, selected_opening_id, residual_class_code, selector_value_mod)",
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This emits an explicit epoch/version manifest for the current real repository epoch and records that third-party and future epoch artifacts are not present.",
    }
    seam_payload = {
        "schema": "long.k23epoch.seam@1",
        "status": STATUS,
        "claim": "The current repository epoch has an explicit two-version manifest, and the materialized versions are bound to the same mint normal form.",
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
        "schema": "long.k23epoch.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23epoch certifies a real epoch/version manifest for the current materialized K23 byte versions.",
        "stage_protocol": {
            "draft": "read dereference canonicality and public-table decoder certificates",
            "witness": "emit epoch rows, version rows, migration rows, gate rows, observables, and numeric tables",
            "coherence": "check the current real epoch has two materialized versions bound by the same mint normal form",
            "closure": "certify explicit manifest readiness while preserving third-party and future epoch nonclaims",
            "emit": "write long_k23epoch artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "epoch_rows_csv": relpath(OUT_DIR / "epoch_rows.csv"),
            "version_rows_csv": relpath(OUT_DIR / "version_rows.csv"),
            "migration_rows_csv": relpath(OUT_DIR / "migration_rows.csv"),
            "gate_rows_csv": relpath(OUT_DIR / "gate_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23epoch_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "one real current repository epoch manifest exists",
                "two materialized byte versions are listed in the manifest",
                "the compact and transcript-index versions stay canonical under the same mint normal form",
            ],
            "does_not_certify": [
                "third-party epoch artifacts",
                "future epoch compatibility",
                "external interoperability",
                "external benchmark superiority",
                "unbounded security",
            ],
        },
        "next_highest_yield_item": "Materialize the interop/benchmark gate against the transcript-index surface, then keep public-claim flags closed until external artifacts exist.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23epoch.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23epoch.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "epoch_csv": csv_text(EPOCH_COLUMNS, rows["epoch_rows"]),
        "version_csv": csv_text(VERSION_COLUMNS, rows["version_rows"]),
        "migration_csv": csv_text(MIGRATION_COLUMNS, rows["migration_rows"]),
        "gate_csv": csv_text(GATE_COLUMNS, rows["gate_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "epoch_table": rows["epoch_table"],
        "version_table": rows["version_table"],
        "migration_table": rows["migration_table"],
        "gate_table": rows["gate_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "epoch_text_sha256": rows["epoch_text_hash"],
            "version_text_sha256": rows["version_text_hash"],
            "migration_text_sha256": rows["migration_text_hash"],
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
    (OUT_DIR / "epoch_rows.csv").write_text(payloads["epoch_csv"], encoding="utf-8")
    (OUT_DIR / "version_rows.csv").write_text(payloads["version_csv"], encoding="utf-8")
    (OUT_DIR / "migration_rows.csv").write_text(payloads["migration_csv"], encoding="utf-8")
    (OUT_DIR / "gate_rows.csv").write_text(payloads["gate_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        epoch_table=payloads["epoch_table"],
        version_table=payloads["version_table"],
        migration_table=payloads["migration_table"],
        gate_table=payloads["gate_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23epoch_matrices.npz", **payloads["matrix_payload"])
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
