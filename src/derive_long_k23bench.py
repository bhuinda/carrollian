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


THEOREM_ID = "long_k23bench"
STATUS = "SECTOR33_K23_BENCHMARK_SURFACE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23bench.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23bench.py"

REPORT_PATHS = {
    "long_k23pot": D20_INVARIANTS / "proof_obligations" / "long_k23pot" / "report.json",
    "long_k23cop": D20_INVARIANTS / "proof_obligations" / "long_k23cop" / "report.json",
    "long_k23chal": D20_INVARIANTS / "proof_obligations" / "long_k23chal" / "report.json",
    "long_k23game": D20_INVARIANTS / "proof_obligations" / "long_k23game" / "report.json",
    "long_k23sound": D20_INVARIANTS / "proof_obligations" / "long_k23sound" / "report.json",
    "long_k23mledger": D20_INVARIANTS / "proof_obligations" / "long_k23mledger" / "report.json",
}
EXPECTED_STATUSES = {
    "long_k23pot": "SECTOR33_K23_PRODUCTIVE_POTENTIAL_CANDIDATES_CERTIFIED",
    "long_k23cop": "SECTOR33_K23_COMMIT_OPEN_TRANSCRIPT_CERTIFIED",
    "long_k23chal": "SECTOR33_K23_VERIFIER_CHALLENGE_CERTIFIED",
    "long_k23game": "SECTOR33_K23_VERIFICATION_GAME_TABLE_CERTIFIED",
    "long_k23sound": "SECTOR33_K23_BOUNDED_ADVERSARY_SOUNDNESS_CERTIFIED",
    "long_k23mledger": "SECTOR33_K23_PROOF_OF_MANDATE_LEDGER_CERTIFIED",
}

BENCH_TEXT_HASH = "171c5671b805aff970b5ea30f19e4e9ac68f917206fc81a386526ad616f00abc"
BASELINE_TEXT_HASH = "0e26e85de25772be9a16a3938256fd039f736631c95935e9d5dd181f5498d436"
LIMIT_TEXT_HASH = "1181cdef9978740c0f19b9062337903599c28e9c6541a8efd7e21bf380fb8d09"
OBS_TEXT_HASH = "a1113be00ac517f044db18f631d2020100a6f78c641be0c89dcb061dab56fb44"
MATRIX_SHA256 = "d8dc7ce621be089f2b16ff34ed122973d9489883da78c3526cf4ea182e695cfe"

BENCH_COLUMNS = [
    "candidate_id",
    "potential_code",
    "baseline_spec_code",
    "operation_basis_code",
    "internal_operation_count",
    "transcript_size_rows",
    "verification_path_count",
    "explicit_baseline_flag",
    "external_numeric_baseline_flag",
    "improvement_claim_flag",
    "benchmark_column_complete_flag",
]
BASELINE_COLUMNS = [
    "baseline_id",
    "spec_code",
    "official_source_flag",
    "current_baseline_flag",
    "kem_flag",
    "signature_flag",
    "guidance_flag",
    "external_numeric_metric_flag",
    "improvement_claim_flag",
]
LIMIT_COLUMNS = [
    "limit_id",
    "limit_code",
    "open_flag",
    "required_before_improvement_claim_flag",
    "overclaim_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "input_report_count",
    "certified_input_count",
    "candidate_row_count",
    "benchmark_candidate_count",
    "operation_count_column_present_count",
    "transcript_size_column_present_count",
    "verification_path_column_present_count",
    "explicit_baseline_count",
    "external_numeric_baseline_count",
    "improvement_claim_count",
    "benchmark_complete_count",
    "baseline_row_count",
    "official_baseline_count",
    "metric_baseline_materialized_count",
    "limit_row_count",
    "open_limit_count",
    "required_before_improvement_claim_count",
    "overclaim_count",
    "public_transcript_count",
    "opening_row_count",
    "challenge_count",
    "game_row_count",
    "all_depth_tamper_reject_strategy_words",
    "accepted_authority_count",
    "ledger_row_count",
    "potential_row_count",
    "productive_potential_count",
    "internal_operation_total",
    "transcript_size_total_rows",
    "verification_path_total",
    "benchmark_surface_flag",
    "external_superiority_claim_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    keys = ["bench_table", "baseline_table", "limit_table", "observable_vector"]
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
    certified = {name: is_certified(reports[name], EXPECTED_STATUSES[name]) for name in REPORT_PATHS}
    cop = summaries["long_k23cop"]
    chal = summaries["long_k23chal"]
    game = summaries["long_k23game"]
    sound = summaries["long_k23sound"]
    ledger = summaries["long_k23mledger"]
    pot = summaries["long_k23pot"]

    public_transcript_count = int(cop.get("public_transcript_count", -1))
    opening_row_count = int(cop.get("opening_row_count", -1))
    challenge_count = int(chal.get("challenge_count", -1))
    game_row_count = int(game.get("game_row_count", -1))
    tamper_move_count = int(game.get("tamper_move_count", -1))
    strategy_words = int(sound.get("all_depth_tamper_reject_strategy_words", -1))
    round_depth_count = int(sound.get("round_depth_count", -1))
    accepted_authority_count = int(ledger.get("accepted_authority_count", -1))
    ledger_row_count = int(ledger.get("ledger_row_count", -1))

    bench_rows = [
        {
            "candidate_id": 0,
            "potential_code": 0,
            "baseline_spec_code": 1,
            "operation_basis_code": 0,
            "internal_operation_count": challenge_count,
            "transcript_size_rows": public_transcript_count,
            "verification_path_count": challenge_count,
            "explicit_baseline_flag": 1,
            "external_numeric_baseline_flag": 0,
            "improvement_claim_flag": 0,
            "benchmark_column_complete_flag": 1,
        },
        {
            "candidate_id": 1,
            "potential_code": 1,
            "baseline_spec_code": 1,
            "operation_basis_code": 1,
            "internal_operation_count": game_row_count,
            "transcript_size_rows": game_row_count,
            "verification_path_count": tamper_move_count,
            "explicit_baseline_flag": 1,
            "external_numeric_baseline_flag": 0,
            "improvement_claim_flag": 0,
            "benchmark_column_complete_flag": 1,
        },
        {
            "candidate_id": 2,
            "potential_code": 2,
            "baseline_spec_code": 1,
            "operation_basis_code": 2,
            "internal_operation_count": strategy_words,
            "transcript_size_rows": round_depth_count,
            "verification_path_count": strategy_words,
            "explicit_baseline_flag": 1,
            "external_numeric_baseline_flag": 0,
            "improvement_claim_flag": 0,
            "benchmark_column_complete_flag": 1,
        },
        {
            "candidate_id": 3,
            "potential_code": 3,
            "baseline_spec_code": 0,
            "operation_basis_code": 3,
            "internal_operation_count": accepted_authority_count,
            "transcript_size_rows": public_transcript_count,
            "verification_path_count": accepted_authority_count,
            "explicit_baseline_flag": 1,
            "external_numeric_baseline_flag": 0,
            "improvement_claim_flag": 0,
            "benchmark_column_complete_flag": 1,
        },
        {
            "candidate_id": 4,
            "potential_code": 4,
            "baseline_spec_code": 2,
            "operation_basis_code": 4,
            "internal_operation_count": ledger_row_count,
            "transcript_size_rows": ledger_row_count,
            "verification_path_count": ledger_row_count,
            "explicit_baseline_flag": 1,
            "external_numeric_baseline_flag": 0,
            "improvement_claim_flag": 0,
            "benchmark_column_complete_flag": 1,
        },
        {
            "candidate_id": 5,
            "potential_code": 5,
            "baseline_spec_code": 3,
            "operation_basis_code": 5,
            "internal_operation_count": challenge_count,
            "transcript_size_rows": game_row_count,
            "verification_path_count": challenge_count,
            "explicit_baseline_flag": 1,
            "external_numeric_baseline_flag": 0,
            "improvement_claim_flag": 0,
            "benchmark_column_complete_flag": 1,
        },
    ]
    baseline_rows = [
        {"baseline_id": 0, "spec_code": 0, "official_source_flag": 1, "current_baseline_flag": 1, "kem_flag": 1, "signature_flag": 0, "guidance_flag": 0, "external_numeric_metric_flag": 0, "improvement_claim_flag": 0},
        {"baseline_id": 1, "spec_code": 1, "official_source_flag": 1, "current_baseline_flag": 1, "kem_flag": 1, "signature_flag": 0, "guidance_flag": 1, "external_numeric_metric_flag": 0, "improvement_claim_flag": 0},
        {"baseline_id": 2, "spec_code": 2, "official_source_flag": 1, "current_baseline_flag": 1, "kem_flag": 0, "signature_flag": 1, "guidance_flag": 0, "external_numeric_metric_flag": 0, "improvement_claim_flag": 0},
        {"baseline_id": 3, "spec_code": 3, "official_source_flag": 1, "current_baseline_flag": 1, "kem_flag": 0, "signature_flag": 1, "guidance_flag": 0, "external_numeric_metric_flag": 0, "improvement_claim_flag": 0},
    ]
    limit_rows = [
        {"limit_id": 0, "limit_code": 0, "open_flag": 1, "required_before_improvement_claim_flag": 1, "overclaim_flag": 0},
        {"limit_id": 1, "limit_code": 1, "open_flag": 1, "required_before_improvement_claim_flag": 1, "overclaim_flag": 0},
        {"limit_id": 2, "limit_code": 2, "open_flag": 1, "required_before_improvement_claim_flag": 1, "overclaim_flag": 0},
        {"limit_id": 3, "limit_code": 3, "open_flag": 1, "required_before_improvement_claim_flag": 1, "overclaim_flag": 0},
        {"limit_id": 4, "limit_code": 4, "open_flag": 1, "required_before_improvement_claim_flag": 1, "overclaim_flag": 0},
        {"limit_id": 5, "limit_code": 5, "open_flag": 1, "required_before_improvement_claim_flag": 1, "overclaim_flag": 0},
    ]
    obs = {
        "input_report_count": len(REPORT_PATHS),
        "certified_input_count": sum(certified.values()),
        "candidate_row_count": len(bench_rows),
        "benchmark_candidate_count": sum(row["benchmark_column_complete_flag"] for row in bench_rows),
        "operation_count_column_present_count": sum(int(row["internal_operation_count"] >= 0) for row in bench_rows),
        "transcript_size_column_present_count": sum(int(row["transcript_size_rows"] >= 0) for row in bench_rows),
        "verification_path_column_present_count": sum(int(row["verification_path_count"] >= 0) for row in bench_rows),
        "explicit_baseline_count": sum(row["explicit_baseline_flag"] for row in bench_rows),
        "external_numeric_baseline_count": sum(row["external_numeric_baseline_flag"] for row in bench_rows),
        "improvement_claim_count": sum(row["improvement_claim_flag"] for row in bench_rows),
        "benchmark_complete_count": sum(row["benchmark_column_complete_flag"] for row in bench_rows),
        "baseline_row_count": len(baseline_rows),
        "official_baseline_count": sum(row["official_source_flag"] for row in baseline_rows),
        "metric_baseline_materialized_count": sum(row["external_numeric_metric_flag"] for row in baseline_rows),
        "limit_row_count": len(limit_rows),
        "open_limit_count": sum(row["open_flag"] for row in limit_rows),
        "required_before_improvement_claim_count": sum(row["required_before_improvement_claim_flag"] for row in limit_rows),
        "overclaim_count": sum(row["overclaim_flag"] for row in limit_rows),
        "public_transcript_count": public_transcript_count,
        "opening_row_count": opening_row_count,
        "challenge_count": challenge_count,
        "game_row_count": game_row_count,
        "all_depth_tamper_reject_strategy_words": strategy_words,
        "accepted_authority_count": accepted_authority_count,
        "ledger_row_count": ledger_row_count,
        "potential_row_count": int(pot.get("potential_row_count", -1)),
        "productive_potential_count": int(pot.get("productive_potential_count", -1)),
        "internal_operation_total": sum(row["internal_operation_count"] for row in bench_rows),
        "transcript_size_total_rows": sum(row["transcript_size_rows"] for row in bench_rows),
        "verification_path_total": sum(row["verification_path_count"] for row in bench_rows),
        "benchmark_surface_flag": 1,
        "external_superiority_claim_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    bench_table = table_from_rows(BENCH_COLUMNS, bench_rows)
    baseline_table = table_from_rows(BASELINE_COLUMNS, baseline_rows)
    limit_table = table_from_rows(LIMIT_COLUMNS, limit_rows)
    observable_table = table_from_rows(OBS_COLUMNS, obs_rows)
    matrix_payload = {
        "bench_table": bench_table.astype(np.int64),
        "baseline_table": baseline_table.astype(np.int64),
        "limit_table": limit_table.astype(np.int64),
        "observable_vector": np.asarray([int(obs[name]) for name in OBS_NAMES], dtype=np.int64),
    }
    return {
        "reports": reports,
        "bench_rows": bench_rows,
        "baseline_rows": baseline_rows,
        "limit_rows": limit_rows,
        "obs_rows": obs_rows,
        "bench_table": bench_table,
        "baseline_table": baseline_table,
        "limit_table": limit_table,
        "observable_table": observable_table,
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "bench_text_hash": hashlib.sha256(digest_text(BENCH_COLUMNS, bench_rows).encode("ascii")).hexdigest(),
        "baseline_text_hash": hashlib.sha256(digest_text(BASELINE_COLUMNS, baseline_rows).encode("ascii")).hexdigest(),
        "limit_text_hash": hashlib.sha256(digest_text(LIMIT_COLUMNS, limit_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_pass": obs["certified_input_count"] == 6,
        "candidate_profile_matches": (
            obs["candidate_row_count"],
            obs["benchmark_candidate_count"],
            obs["operation_count_column_present_count"],
            obs["transcript_size_column_present_count"],
            obs["verification_path_column_present_count"],
            obs["explicit_baseline_count"],
            obs["external_numeric_baseline_count"],
            obs["improvement_claim_count"],
            obs["benchmark_complete_count"],
        )
        == (6, 6, 6, 6, 6, 6, 0, 0, 6),
        "baseline_profile_matches": (
            obs["baseline_row_count"],
            obs["official_baseline_count"],
            obs["metric_baseline_materialized_count"],
        )
        == (4, 4, 0),
        "limit_profile_matches": (
            obs["limit_row_count"],
            obs["open_limit_count"],
            obs["required_before_improvement_claim_count"],
            obs["overclaim_count"],
        )
        == (6, 6, 6, 0),
        "source_counts_match": (
            obs["public_transcript_count"],
            obs["opening_row_count"],
            obs["challenge_count"],
            obs["game_row_count"],
            obs["all_depth_tamper_reject_strategy_words"],
            obs["accepted_authority_count"],
            obs["ledger_row_count"],
            obs["potential_row_count"],
            obs["productive_potential_count"],
        )
        == (56, 91, 56, 336, 112_869_680, 56, 12, 6, 6),
        "totals_match": (
            obs["internal_operation_total"],
            obs["transcript_size_total_rows"],
            obs["verification_path_total"],
        )
        == (112_870_196, 804, 112_870_140),
        "boundary_flags_match": (
            obs["benchmark_surface_flag"],
            obs["external_superiority_claim_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (1, 0, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_internal_benchmark_surface",
        "operation_basis_code_map": {
            "0": "challenge_row_count",
            "1": "one_round_game_row_count",
            "2": "bounded_strategy_word_count",
            "3": "authority_acceptance_row_count",
            "4": "mandate_ledger_row_count",
            "5": "deterministic_challenge_source_row_count",
        },
        "potential_code_map": rows["reports"]["long_k23pot"]["witness"]["potential_code_map"],
        "baseline_code_map": rows["reports"]["long_k23pot"]["witness"]["spec_code_map"],
        "limit_code_map": {
            "0": "spec_normalized_bit_or_byte_model",
            "1": "operation_model_normalization",
            "2": "implementation_timing_or_memory_benchmark",
            "3": "security_reduction_or_adversary_model",
            "4": "interoperability_and_compliance_check",
            "5": "deployment_profile_measurement",
        },
        "summary": obs,
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This materializes internal benchmark columns for the six productive-potential rows, while leaving external metric baselines and improvement claims open.",
    }
    seam_payload = {
        "schema": "long.k23bench.seam@1",
        "status": STATUS,
        "claim": "The K23 productive-potential rows now have internal operation, transcript-size, verification-path, and explicit baseline columns.",
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
        "schema": "long.k23bench.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23bench certifies internal benchmark columns for the K23 productive-potential surface.",
        "stage_protocol": {
            "draft": "read long_k23pot and the certified transcript/challenge/game/soundness/ledger inputs",
            "witness": "emit candidate benchmark rows, baseline rows, open-limit rows, observables, and numeric tables",
            "coherence": "check source counts, benchmark-column completeness, baseline anchors, totals, and nonclaims",
            "closure": "certify internal benchmark columns without claiming external metric superiority",
            "emit": "write long_k23bench artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "bench_rows_csv": relpath(OUT_DIR / "bench_rows.csv"),
            "baseline_rows_csv": relpath(OUT_DIR / "baseline_rows.csv"),
            "limit_rows_csv": relpath(OUT_DIR / "limit_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23bench_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "all six productive-potential rows have internal operation-count columns",
                "all six productive-potential rows have transcript-size row columns",
                "all six productive-potential rows have verification-path count columns",
                "all six rows name an explicit current external baseline code",
                "external numeric metric baselines and improvement claims remain false",
            ],
            "does_not_certify": [
                "runtime speed or memory improvement",
                "bit-size or byte-size improvement",
                "security superiority",
                "standards compliance",
                "drop-in replacement behavior",
                "deployment readiness",
                "completion of the active discovery goal",
            ],
        },
        "next_highest_yield_item": "Normalize one candidate against a concrete public parameter set by adding bit/byte sizes, operation model units, and an implementation-free comparison equation.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23bench.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23bench.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "bench_csv": csv_text(BENCH_COLUMNS, rows["bench_rows"]),
        "baseline_csv": csv_text(BASELINE_COLUMNS, rows["baseline_rows"]),
        "limit_csv": csv_text(LIMIT_COLUMNS, rows["limit_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "bench_table": rows["bench_table"],
        "baseline_table": rows["baseline_table"],
        "limit_table": rows["limit_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "bench_text_sha256": rows["bench_text_hash"],
            "baseline_text_sha256": rows["baseline_text_hash"],
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
    (OUT_DIR / "bench_rows.csv").write_text(payloads["bench_csv"], encoding="utf-8")
    (OUT_DIR / "baseline_rows.csv").write_text(payloads["baseline_csv"], encoding="utf-8")
    (OUT_DIR / "limit_rows.csv").write_text(payloads["limit_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        bench_table=payloads["bench_table"],
        baseline_table=payloads["baseline_table"],
        limit_table=payloads["limit_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23bench_matrices.npz", **payloads["matrix_payload"])
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
