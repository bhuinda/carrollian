from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23pot import (
        DERIVE_SCRIPT,
        LIMIT_COLUMNS,
        LIMIT_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        POTENTIAL_COLUMNS,
        POTENTIAL_TEXT_HASH,
        SPEC_COLUMNS,
        SPEC_TEXT_HASH,
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
    from derive_long_k23pot import (
        DERIVE_SCRIPT,
        LIMIT_COLUMNS,
        LIMIT_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        POTENTIAL_COLUMNS,
        POTENTIAL_TEXT_HASH,
        SPEC_COLUMNS,
        SPEC_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from derive_long_raw import rows_from_table


EXPECTED_FIRST_SPEC = (0, 0, 1, 1, 1, 0, 0, 1)
EXPECTED_LAST_SPEC = (3, 3, 1, 1, 0, 1, 0, 1)
EXPECTED_FIRST_POTENTIAL = (0, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1)
EXPECTED_LAST_POTENTIAL = (5, 5, 3, 1, 0, 1, 0, 1, 1, 0, 1)
EXPECTED_FIRST_LIMIT = (0, 0, 0, 1, 1, 0)
EXPECTED_LAST_LIMIT = (6, 6, 0, 1, 1, 0)


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


def validate_long_k23pot() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23pot_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23pot seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23pot cert mismatch")
    for filename, key in {
        "spec_rows.csv": "spec_csv",
        "potential_rows.csv": "potential_csv",
        "limit_rows.csv": "limit_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23pot {filename} mismatch")
    for key, expected_array in {
        "spec_table": expected["spec_table"],
        "potential_table": expected["potential_table"],
        "limit_table": expected["limit_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23pot table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23pot matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23pot.report@1":
        raise AssertionError("long_k23pot report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23pot report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23pot all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23pot checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23pot report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23pot report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("spec_rows.csv", SPEC_COLUMNS, 4),
        ("potential_rows.csv", POTENTIAL_COLUMNS, 6),
        ("limit_rows.csv", LIMIT_COLUMNS, 7),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23pot {filename} shape mismatch")

    assert_locked_hash(
        "spec rows",
        hashlib.sha256(digest_text(SPEC_COLUMNS, csv_rows["spec_rows.csv"]).encode("ascii")).hexdigest(),
        SPEC_TEXT_HASH,
    )
    assert_locked_hash(
        "potential rows",
        hashlib.sha256(digest_text(POTENTIAL_COLUMNS, csv_rows["potential_rows.csv"]).encode("ascii")).hexdigest(),
        POTENTIAL_TEXT_HASH,
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
        for key in ["spec_table", "potential_table", "limit_table", "observable_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    spec_rows = csv_rows["spec_rows.csv"]
    if int_tuple(spec_rows[0], SPEC_COLUMNS) != EXPECTED_FIRST_SPEC:
        raise AssertionError("long_k23pot first spec row mismatch")
    if int_tuple(spec_rows[-1], SPEC_COLUMNS) != EXPECTED_LAST_SPEC:
        raise AssertionError("long_k23pot last spec row mismatch")
    if any(int(row["official_source_flag"]) != 1 for row in spec_rows):
        raise AssertionError("long_k23pot official-source mismatch")
    if any(int(row["current_baseline_flag"]) != 1 for row in spec_rows):
        raise AssertionError("long_k23pot baseline mismatch")
    if any(int(row["external_url_present_flag"]) != 1 for row in spec_rows):
        raise AssertionError("long_k23pot source URL mismatch")

    potential_rows = csv_rows["potential_rows.csv"]
    if int_tuple(potential_rows[0], POTENTIAL_COLUMNS) != EXPECTED_FIRST_POTENTIAL:
        raise AssertionError("long_k23pot first potential row mismatch")
    if int_tuple(potential_rows[-1], POTENTIAL_COLUMNS) != EXPECTED_LAST_POTENTIAL:
        raise AssertionError("long_k23pot last potential row mismatch")
    if any(int(row["internal_evidence_flag"]) != 1 for row in potential_rows):
        raise AssertionError("long_k23pot missing internal evidence")
    if any(int(row["external_comparison_claim_flag"]) != 0 for row in potential_rows):
        raise AssertionError("long_k23pot external comparison overclaim")
    if any(int(row["benchmark_required_flag"]) != 1 for row in potential_rows):
        raise AssertionError("long_k23pot benchmark requirement mismatch")
    if any(int(row["security_proof_required_flag"]) != 1 for row in potential_rows):
        raise AssertionError("long_k23pot security-proof requirement mismatch")
    if any(int(row["deployment_claim_flag"]) != 0 for row in potential_rows):
        raise AssertionError("long_k23pot deployment overclaim")
    if any(int(row["productive_potential_flag"]) != 1 for row in potential_rows):
        raise AssertionError("long_k23pot productive potential mismatch")

    limit_rows = csv_rows["limit_rows.csv"]
    if int_tuple(limit_rows[0], LIMIT_COLUMNS) != EXPECTED_FIRST_LIMIT:
        raise AssertionError("long_k23pot first limit row mismatch")
    if int_tuple(limit_rows[-1], LIMIT_COLUMNS) != EXPECTED_LAST_LIMIT:
        raise AssertionError("long_k23pot last limit row mismatch")
    if any(int(row["claim_flag"]) != 0 or int(row["open_flag"]) != 1 for row in limit_rows):
        raise AssertionError("long_k23pot limit openness mismatch")
    if any(int(row["required_before_external_claim_flag"]) != 1 for row in limit_rows):
        raise AssertionError("long_k23pot external-claim requirement mismatch")
    if any(int(row["overclaim_flag"]) != 0 for row in limit_rows):
        raise AssertionError("long_k23pot overclaim mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "input_report_count": 1,
        "certified_input_count": 1,
        "spec_anchor_count": 4,
        "official_spec_anchor_count": 4,
        "kem_anchor_count": 2,
        "signature_anchor_count": 2,
        "guidance_anchor_count": 1,
        "potential_row_count": 6,
        "internal_evidence_count": 6,
        "efficiency_candidate_count": 4,
        "security_candidate_count": 5,
        "external_comparison_claim_count": 0,
        "benchmark_required_count": 6,
        "security_proof_required_count": 6,
        "deployment_claim_count": 0,
        "productive_potential_count": 6,
        "limit_row_count": 7,
        "open_limit_count": 7,
        "required_before_external_claim_count": 7,
        "overclaim_count": 0,
        "ledger_certified_input_count": 12,
        "ledger_row_count": 12,
        "challenge_count": 56,
        "game_row_count": 336,
        "accepted_authority_count": 56,
        "all_depth_false_accept_strategy_words": 0,
        "proof_of_mandate_ledger_flag": 1,
        "productive_potential_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23pot observable {name} mismatch")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23pot index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator script")

    return {
        "schema": "long.k23pot.verification@1",
        "status": "PASS",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23pot(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
