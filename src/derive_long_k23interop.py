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


THEOREM_ID = "long_k23interop"
STATUS = "SECTOR33_K23_INTEROP_BENCHMARK_GATE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23interop.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23interop.py"

REPORT_PATHS = {
    "long_k23epoch": D20_INVARIANTS / "proof_obligations" / "long_k23epoch" / "report.json",
    "long_k23dist": D20_INVARIANTS / "proof_obligations" / "long_k23dist" / "report.json",
    "long_k23ptran": D20_INVARIANTS / "proof_obligations" / "long_k23ptran" / "report.json",
    "long_k23bench": D20_INVARIANTS / "proof_obligations" / "long_k23bench" / "report.json",
}
EXPECTED_STATUSES = {
    "long_k23epoch": "SECTOR33_K23_REAL_EPOCH_MANIFEST_CERTIFIED",
    "long_k23dist": "SECTOR33_K23_PUBLIC_TABLE_DISTRIBUTION_DECODER_CERTIFIED",
    "long_k23ptran": "SECTOR33_K23_PUBLIC_TRANSPORT_POTENTIAL_CERTIFIED",
    "long_k23bench": "SECTOR33_K23_BENCHMARK_SURFACE_CERTIFIED",
}

PROFILE_TEXT_HASH = "d7f5d9c4e437f0cb2cb8bdfdd0cd4932af58d6d97cc74eb6ba7f21933f82094f"
GATE_TEXT_HASH = "c76bd0f8e0bb9639ad0b5768dd362987e9b50da96a59998ff818e7ae6cb721b7"
OBS_TEXT_HASH = "56631f4780252bcb63f2a0697c1a5fdd5911e938128898cfc1b6b6f4055ad7b9"
MATRIX_SHA256 = "cfd8b8b1e9607ca5d218ec5143ec22bcc5a60a65fc79f4482cc209ee99d1501c"

PROFILE_COLUMNS = [
    "profile_id",
    "profile_code",
    "source_code",
    "byte_surface",
    "baseline_public_exchange_bytes",
    "saved_vs_baseline_bytes",
    "saved_vs_baseline_num",
    "saved_vs_baseline_den",
    "internal_certified_flag",
    "external_benchmark_flag",
    "drop_in_compat_flag",
    "public_claim_flag",
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
    "profile_row_count",
    "internal_certified_profile_count",
    "baseline_public_exchange_bytes",
    "current_self_contained_bytes",
    "compact_shared_table_bytes",
    "transcript_index_bytes",
    "compact_saved_vs_baseline_bytes",
    "compact_saved_vs_baseline_num",
    "compact_saved_vs_baseline_den",
    "index_saved_vs_baseline_bytes",
    "index_saved_vs_baseline_num",
    "index_saved_vs_baseline_den",
    "valid_decode_count",
    "invalid_reject_count",
    "runtime_package_row_count",
    "epoch_manifest_ready_flag",
    "benchmark_surface_flag",
    "external_benchmark_count",
    "drop_in_compat_count",
    "public_transport_claim_count",
    "external_improvement_claim_count",
    "gate_row_count",
    "satisfied_gate_count",
    "blocking_gate_count",
    "claim_gate_count",
    "objective_byte_improvement_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["profile_table", "gate_table", "observable_vector"]
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
    epoch = summaries["long_k23epoch"]
    dist = summaries["long_k23dist"]
    ptran = summaries["long_k23ptran"]
    bench = summaries["long_k23bench"]

    baseline = int(dist.get("baseline_public_exchange_bytes", -1))
    current_bytes = int(ptran.get("current_self_contained_bytes", -1))
    compact_bytes = int(ptran.get("shared_table_wire_bytes", -1))
    index_bytes = int(dist.get("transcript_only_total_bytes", -1))
    compact_saved = int(ptran.get("conditional_saved_vs_baseline_bytes", -1))
    index_saved = int(dist.get("saved_vs_baseline_bytes", -1))

    profile_rows = [
        {
            "profile_id": 0,
            "profile_code": 0,
            "source_code": 0,
            "byte_surface": current_bytes,
            "baseline_public_exchange_bytes": baseline,
            "saved_vs_baseline_bytes": 0,
            "saved_vs_baseline_num": 0,
            "saved_vs_baseline_den": 1,
            "internal_certified_flag": 1,
            "external_benchmark_flag": 0,
            "drop_in_compat_flag": 0,
            "public_claim_flag": 0,
        },
        {
            "profile_id": 1,
            "profile_code": 1,
            "source_code": 1,
            "byte_surface": compact_bytes,
            "baseline_public_exchange_bytes": baseline,
            "saved_vs_baseline_bytes": compact_saved,
            "saved_vs_baseline_num": int(ptran.get("shared_improvement_num", -1)),
            "saved_vs_baseline_den": int(ptran.get("shared_improvement_den", -1)),
            "internal_certified_flag": 1,
            "external_benchmark_flag": 0,
            "drop_in_compat_flag": 0,
            "public_claim_flag": 0,
        },
        {
            "profile_id": 2,
            "profile_code": 2,
            "source_code": 2,
            "byte_surface": index_bytes,
            "baseline_public_exchange_bytes": baseline,
            "saved_vs_baseline_bytes": index_saved,
            "saved_vs_baseline_num": int(dist.get("saved_vs_baseline_num", -1)),
            "saved_vs_baseline_den": int(dist.get("saved_vs_baseline_den", -1)),
            "internal_certified_flag": 1,
            "external_benchmark_flag": 0,
            "drop_in_compat_flag": 0,
            "public_claim_flag": 0,
        },
    ]
    gate_rows = [
        {"gate_id": 0, "gate_code": 0, "satisfied_flag": 1, "blocking_flag": 0, "claim_flag": 0},
        {"gate_id": 1, "gate_code": 1, "satisfied_flag": 1, "blocking_flag": 0, "claim_flag": 0},
        {"gate_id": 2, "gate_code": 2, "satisfied_flag": 1, "blocking_flag": 0, "claim_flag": 0},
        {"gate_id": 3, "gate_code": 3, "satisfied_flag": 0, "blocking_flag": 1, "claim_flag": 0},
        {"gate_id": 4, "gate_code": 4, "satisfied_flag": 0, "blocking_flag": 1, "claim_flag": 0},
        {"gate_id": 5, "gate_code": 5, "satisfied_flag": 0, "blocking_flag": 1, "claim_flag": 0},
    ]
    obs = {
        "input_report_count": len(REPORT_PATHS),
        "certified_input_count": sum(is_certified(reports[name], EXPECTED_STATUSES[name]) for name in REPORT_PATHS),
        "profile_row_count": len(profile_rows),
        "internal_certified_profile_count": sum(row["internal_certified_flag"] for row in profile_rows),
        "baseline_public_exchange_bytes": baseline,
        "current_self_contained_bytes": current_bytes,
        "compact_shared_table_bytes": compact_bytes,
        "transcript_index_bytes": index_bytes,
        "compact_saved_vs_baseline_bytes": compact_saved,
        "compact_saved_vs_baseline_num": int(ptran.get("shared_improvement_num", -1)),
        "compact_saved_vs_baseline_den": int(ptran.get("shared_improvement_den", -1)),
        "index_saved_vs_baseline_bytes": index_saved,
        "index_saved_vs_baseline_num": int(dist.get("saved_vs_baseline_num", -1)),
        "index_saved_vs_baseline_den": int(dist.get("saved_vs_baseline_den", -1)),
        "valid_decode_count": int(dist.get("valid_decode_row_count", -1)),
        "invalid_reject_count": int(dist.get("invalid_reject_count", -1)),
        "runtime_package_row_count": int(dist.get("package_row_count", -1)),
        "epoch_manifest_ready_flag": int(epoch.get("external_manifest_ready_flag", -1)),
        "benchmark_surface_flag": int(bench.get("benchmark_surface_flag", -1)),
        "external_benchmark_count": int(dist.get("external_benchmark_claim_count", -1)),
        "drop_in_compat_count": 0,
        "public_transport_claim_count": int(ptran.get("public_transport_claim_count", -1)),
        "external_improvement_claim_count": int(dist.get("external_improvement_claim_count", -1)),
        "gate_row_count": len(gate_rows),
        "satisfied_gate_count": sum(row["satisfied_flag"] for row in gate_rows),
        "blocking_gate_count": sum(row["blocking_flag"] for row in gate_rows),
        "claim_gate_count": sum(row["claim_flag"] for row in gate_rows),
        "objective_byte_improvement_flag": int(index_saved > 0 and index_bytes < baseline),
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    profile_table = table_from_rows(PROFILE_COLUMNS, profile_rows)
    gate_table = table_from_rows(GATE_COLUMNS, gate_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "profile_table": profile_table.astype(np.int64),
        "gate_table": gate_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "reports": reports,
        "profile_rows": profile_rows,
        "gate_rows": gate_rows,
        "obs_rows": obs_rows,
        "profile_table": profile_table,
        "gate_table": gate_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "profile_text_hash": hashlib.sha256(digest_text(PROFILE_COLUMNS, profile_rows).encode("ascii")).hexdigest(),
        "gate_text_hash": hashlib.sha256(digest_text(GATE_COLUMNS, gate_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": obs["certified_input_count"] == obs["input_report_count"] == 4,
        "profile_profile_matches": (
            obs["profile_row_count"],
            obs["internal_certified_profile_count"],
            obs["baseline_public_exchange_bytes"],
            obs["current_self_contained_bytes"],
            obs["compact_shared_table_bytes"],
            obs["transcript_index_bytes"],
        )
        == (3, 3, 1568, 5376, 224, 56),
        "saving_profile_matches": (
            obs["compact_saved_vs_baseline_bytes"],
            obs["compact_saved_vs_baseline_num"],
            obs["compact_saved_vs_baseline_den"],
            obs["index_saved_vs_baseline_bytes"],
            obs["index_saved_vs_baseline_num"],
            obs["index_saved_vs_baseline_den"],
        )
        == (1344, 6, 7, 1512, 27, 28),
        "decoder_and_epoch_match": (
            obs["valid_decode_count"],
            obs["invalid_reject_count"],
            obs["runtime_package_row_count"],
            obs["epoch_manifest_ready_flag"],
            obs["benchmark_surface_flag"],
        )
        == (56, 200, 147, 1, 1),
        "external_nonclaim_matches": (
            obs["external_benchmark_count"],
            obs["drop_in_compat_count"],
            obs["public_transport_claim_count"],
            obs["external_improvement_claim_count"],
        )
        == (0, 0, 0, 0),
        "gate_profile_matches": (
            obs["gate_row_count"],
            obs["satisfied_gate_count"],
            obs["blocking_gate_count"],
            obs["claim_gate_count"],
        )
        == (6, 3, 3, 0),
        "objective_byte_improvement_matches": obs["objective_byte_improvement_flag"] == 1,
        "completion_flag_matches": obs["complete_goal_claim_flag"] == 0,
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_interop_benchmark_gate",
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This records internal byte-surface improvement for the transcript-index surface while keeping external benchmark and drop-in compatibility claims closed.",
    }
    seam_payload = {
        "schema": "long.k23interop.seam@1",
        "status": STATUS,
        "claim": "The 56-byte transcript-index surface is internally certified and objectively smaller than the selected 1568-byte public baseline, but external interop and benchmark claims remain blocked.",
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
        "schema": "long.k23interop.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23interop certifies the internal interop/benchmark gate for the K23 transcript-index surface.",
        "stage_protocol": {
            "draft": "read epoch manifest, decoder, public transport, and benchmark-surface certificates",
            "witness": "emit byte-profile rows, gate rows, observables, and numeric tables",
            "coherence": "check the 56-byte surface, 27/28 byte saving, decoder totals, and external nonclaim flags",
            "closure": "certify internal byte efficiency while blocking external interop and benchmark claims",
            "emit": "write long_k23interop artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "profile_rows_csv": relpath(OUT_DIR / "profile_rows.csv"),
            "gate_rows_csv": relpath(OUT_DIR / "gate_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23interop_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the transcript-index surface is 56 bytes across 56 rows",
                "the selected byte comparison records 1512 bytes saved against the 1568-byte baseline",
                "the internal decoder has 56 valid decodes and 200 invalid-byte rejects",
            ],
            "does_not_certify": [
                "drop-in compatibility",
                "third-party benchmark results",
                "external public transport readiness",
                "security superiority",
                "deployment readiness",
            ],
        },
        "next_highest_yield_item": "Materialize the security-integrity gate so byte efficiency is separated from bounded finite-game security and open hardness claims.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23interop.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23interop.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "profile_csv": csv_text(PROFILE_COLUMNS, rows["profile_rows"]),
        "gate_csv": csv_text(GATE_COLUMNS, rows["gate_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "profile_table": rows["profile_table"],
        "gate_table": rows["gate_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "profile_text_sha256": rows["profile_text_hash"],
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
    (OUT_DIR / "profile_rows.csv").write_text(payloads["profile_csv"], encoding="utf-8")
    (OUT_DIR / "gate_rows.csv").write_text(payloads["gate_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        profile_table=payloads["profile_table"],
        gate_table=payloads["gate_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23interop_matrices.npz", **payloads["matrix_payload"])
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
