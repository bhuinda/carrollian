from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23bench import (
        BASELINE_COLUMNS,
        BASELINE_TEXT_HASH,
        BENCH_COLUMNS,
        BENCH_TEXT_HASH,
        DERIVE_SCRIPT,
        LIMIT_COLUMNS,
        LIMIT_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_k23bench import (
        BASELINE_COLUMNS,
        BASELINE_TEXT_HASH,
        BENCH_COLUMNS,
        BENCH_TEXT_HASH,
        DERIVE_SCRIPT,
        LIMIT_COLUMNS,
        LIMIT_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from derive_long_raw import rows_from_table


EXPECTED_FIRST_BENCH = (0, 0, 1, 0, 56, 56, 56, 1, 0, 0, 1)
EXPECTED_LAST_BENCH = (5, 5, 3, 5, 56, 336, 56, 1, 0, 0, 1)
EXPECTED_STRATEGY_BENCH = (2, 2, 1, 2, 112_869_680, 8, 112_869_680, 1, 0, 0, 1)
EXPECTED_FIRST_BASELINE = (0, 0, 1, 1, 1, 0, 0, 0, 0)
EXPECTED_LAST_BASELINE = (3, 3, 1, 1, 0, 1, 0, 0, 0)
EXPECTED_FIRST_LIMIT = (0, 0, 1, 1, 0)
EXPECTED_LAST_LIMIT = (5, 5, 1, 1, 0)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} is not a JSON object")
    return payload


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def assert_file_hash(entry: dict[str, Any], expected_path: Path, label: str) -> None:
    expected_rel = expected_path.relative_to(ROOT).as_posix()
    if entry.get("path") != expected_rel:
        raise AssertionError(f"{label} path mismatch: {entry.get('path')}")
    if entry.get("sha256") != h_file(expected_path):
        raise AssertionError(f"{label} sha256 mismatch")


def assert_locked_hash(label: str, actual: str, expected: str) -> None:
    if not expected:
        raise AssertionError(f"{label} witness hash is not locked")
    if actual != expected:
        raise AssertionError(f"{label} witness hash mismatch")


def int_tuple(row: dict[str, str], columns: list[str]) -> tuple[int, ...]:
    return tuple(int(row[column]) for column in columns)


def validate_long_k23bench() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23bench_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23bench seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23bench cert mismatch")
    for filename, key in {
        "bench_rows.csv": "bench_csv",
        "baseline_rows.csv": "baseline_csv",
        "limit_rows.csv": "limit_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23bench {filename} mismatch")
    for key, expected_array in {
        "bench_table": expected["bench_table"],
        "baseline_table": expected["baseline_table"],
        "limit_table": expected["limit_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23bench table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23bench matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23bench.report@1":
        raise AssertionError("long_k23bench report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23bench report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23bench all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23bench checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23bench report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23bench report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("bench_rows.csv", BENCH_COLUMNS, 6),
        ("baseline_rows.csv", BASELINE_COLUMNS, 4),
        ("limit_rows.csv", LIMIT_COLUMNS, 6),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23bench {filename} shape mismatch")

    assert_locked_hash(
        "benchmark rows",
        hashlib.sha256(digest_text(BENCH_COLUMNS, csv_rows["bench_rows.csv"]).encode("ascii")).hexdigest(),
        BENCH_TEXT_HASH,
    )
    assert_locked_hash(
        "baseline rows",
        hashlib.sha256(digest_text(BASELINE_COLUMNS, csv_rows["baseline_rows.csv"]).encode("ascii")).hexdigest(),
        BASELINE_TEXT_HASH,
    )
    assert_locked_hash(
        "limit rows",
        hashlib.sha256(digest_text(LIMIT_COLUMNS, csv_rows["limit_rows.csv"]).encode("ascii")).hexdigest(),
        LIMIT_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in ["bench_table", "baseline_table", "limit_table", "observable_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    bench_rows = csv_rows["bench_rows.csv"]
    if int_tuple(bench_rows[0], BENCH_COLUMNS) != EXPECTED_FIRST_BENCH:
        raise AssertionError("long_k23bench first benchmark row mismatch")
    if int_tuple(bench_rows[2], BENCH_COLUMNS) != EXPECTED_STRATEGY_BENCH:
        raise AssertionError("long_k23bench strategy benchmark row mismatch")
    if int_tuple(bench_rows[-1], BENCH_COLUMNS) != EXPECTED_LAST_BENCH:
        raise AssertionError("long_k23bench last benchmark row mismatch")
    if any(int(row["explicit_baseline_flag"]) != 1 for row in bench_rows):
        raise AssertionError("long_k23bench explicit baseline mismatch")
    if any(int(row["external_numeric_baseline_flag"]) != 0 for row in bench_rows):
        raise AssertionError("long_k23bench external numeric overclaim")
    if any(int(row["improvement_claim_flag"]) != 0 for row in bench_rows):
        raise AssertionError("long_k23bench improvement overclaim")
    if any(int(row["benchmark_column_complete_flag"]) != 1 for row in bench_rows):
        raise AssertionError("long_k23bench benchmark completeness mismatch")
    if any(int(row["internal_operation_count"]) < 0 for row in bench_rows):
        raise AssertionError("long_k23bench negative operation count")
    if any(int(row["transcript_size_rows"]) < 0 for row in bench_rows):
        raise AssertionError("long_k23bench negative transcript size")
    if any(int(row["verification_path_count"]) < 0 for row in bench_rows):
        raise AssertionError("long_k23bench negative path count")

    baseline_rows = csv_rows["baseline_rows.csv"]
    if int_tuple(baseline_rows[0], BASELINE_COLUMNS) != EXPECTED_FIRST_BASELINE:
        raise AssertionError("long_k23bench first baseline row mismatch")
    if int_tuple(baseline_rows[-1], BASELINE_COLUMNS) != EXPECTED_LAST_BASELINE:
        raise AssertionError("long_k23bench last baseline row mismatch")
    if any(int(row["official_source_flag"]) != 1 for row in baseline_rows):
        raise AssertionError("long_k23bench official baseline mismatch")
    if any(int(row["external_numeric_metric_flag"]) != 0 for row in baseline_rows):
        raise AssertionError("long_k23bench metric baseline overclaim")
    if any(int(row["improvement_claim_flag"]) != 0 for row in baseline_rows):
        raise AssertionError("long_k23bench baseline improvement overclaim")

    limit_rows = csv_rows["limit_rows.csv"]
    if int_tuple(limit_rows[0], LIMIT_COLUMNS) != EXPECTED_FIRST_LIMIT:
        raise AssertionError("long_k23bench first limit row mismatch")
    if int_tuple(limit_rows[-1], LIMIT_COLUMNS) != EXPECTED_LAST_LIMIT:
        raise AssertionError("long_k23bench last limit row mismatch")
    if any(int(row["open_flag"]) != 1 for row in limit_rows):
        raise AssertionError("long_k23bench limit openness mismatch")
    if any(int(row["required_before_improvement_claim_flag"]) != 1 for row in limit_rows):
        raise AssertionError("long_k23bench requirement mismatch")
    if any(int(row["overclaim_flag"]) != 0 for row in limit_rows):
        raise AssertionError("long_k23bench limit overclaim")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "input_report_count": 6,
        "certified_input_count": 6,
        "candidate_row_count": 6,
        "benchmark_candidate_count": 6,
        "operation_count_column_present_count": 6,
        "transcript_size_column_present_count": 6,
        "verification_path_column_present_count": 6,
        "explicit_baseline_count": 6,
        "external_numeric_baseline_count": 0,
        "improvement_claim_count": 0,
        "benchmark_complete_count": 6,
        "baseline_row_count": 4,
        "official_baseline_count": 4,
        "metric_baseline_materialized_count": 0,
        "limit_row_count": 6,
        "open_limit_count": 6,
        "required_before_improvement_claim_count": 6,
        "overclaim_count": 0,
        "public_transcript_count": 56,
        "opening_row_count": 91,
        "challenge_count": 56,
        "game_row_count": 336,
        "all_depth_tamper_reject_strategy_words": 112_869_680,
        "accepted_authority_count": 56,
        "ledger_row_count": 12,
        "potential_row_count": 6,
        "productive_potential_count": 6,
        "internal_operation_total": 112_870_196,
        "transcript_size_total_rows": 804,
        "verification_path_total": 112_870_140,
        "benchmark_surface_flag": 1,
        "external_superiority_claim_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23bench observable {name} mismatch")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23bench index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator script")

    return {
        "schema": "long.k23bench.verification@1",
        "status": "PASS",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23bench(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
