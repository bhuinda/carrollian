from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23ptab import (
        DERIVE_SCRIPT,
        EQUIV_COLUMNS,
        EQUIV_TEXT_HASH,
        GATE_COLUMNS,
        GATE_TEXT_HASH,
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
    from derive_long_k23ptab import (
        DERIVE_SCRIPT,
        EQUIV_COLUMNS,
        EQUIV_TEXT_HASH,
        GATE_COLUMNS,
        GATE_TEXT_HASH,
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


EXPECTED_FIRST_EQUIV = (0, 0, 5, 5, 27, 27, 5, 5, 1, 4, 1, 1)
EXPECTED_LAST_EQUIV = (55, 55, 90, 90, 39, 39, 0, 0, 1, 4, 1, 1)
EXPECTED_FIRST_GATE = (0, 0, 1, 0, 0)
EXPECTED_LAST_GATE = (4, 4, 0, 1, 0)


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


def validate_long_k23ptab() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23ptab_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23ptab seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23ptab cert mismatch")
    for filename, key in {
        "equiv_rows.csv": "equiv_csv",
        "gate_rows.csv": "gate_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23ptab {filename} mismatch")
    for key, expected_array in {
        "equiv_table": expected["equiv_table"],
        "gate_table": expected["gate_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23ptab table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23ptab matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23ptab.report@1":
        raise AssertionError("long_k23ptab report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23ptab report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23ptab all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23ptab checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23ptab report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23ptab report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("equiv_rows.csv", EQUIV_COLUMNS, 56),
        ("gate_rows.csv", GATE_COLUMNS, 5),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23ptab {filename} shape mismatch")

    assert_locked_hash(
        "equivalence rows",
        hashlib.sha256(digest_text(EQUIV_COLUMNS, csv_rows["equiv_rows.csv"]).encode("ascii")).hexdigest(),
        EQUIV_TEXT_HASH,
    )
    assert_locked_hash(
        "gate rows",
        hashlib.sha256(digest_text(GATE_COLUMNS, csv_rows["gate_rows.csv"]).encode("ascii")).hexdigest(),
        GATE_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in ["equiv_table", "gate_table", "observable_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    equiv_rows = csv_rows["equiv_rows.csv"]
    if int_tuple(equiv_rows[0], EQUIV_COLUMNS) != EXPECTED_FIRST_EQUIV:
        raise AssertionError("long_k23ptab first equivalence row mismatch")
    if int_tuple(equiv_rows[-1], EQUIV_COLUMNS) != EXPECTED_LAST_EQUIV:
        raise AssertionError("long_k23ptab last equivalence row mismatch")
    if any(int(row["derived_match_flag"]) != 1 for row in equiv_rows):
        raise AssertionError("long_k23ptab derivation mismatch")
    if any(int(row["public_table_equivalence_flag"]) != 1 for row in equiv_rows):
        raise AssertionError("long_k23ptab equivalence mismatch")
    if any(int(row["transcript_only_bytes"]) != 1 or int(row["wire_row_bytes"]) != 4 for row in equiv_rows):
        raise AssertionError("long_k23ptab byte profile mismatch")

    gate_rows = csv_rows["gate_rows.csv"]
    if int_tuple(gate_rows[0], GATE_COLUMNS) != EXPECTED_FIRST_GATE:
        raise AssertionError("long_k23ptab first gate row mismatch")
    if int_tuple(gate_rows[-1], GATE_COLUMNS) != EXPECTED_LAST_GATE:
        raise AssertionError("long_k23ptab last gate row mismatch")
    if sum(int(row["satisfied_flag"]) for row in gate_rows) != 2:
        raise AssertionError("long_k23ptab satisfied gate count mismatch")
    if sum(int(row["blocking_flag"]) for row in gate_rows) != 3:
        raise AssertionError("long_k23ptab blocking gate count mismatch")
    if any(int(row["claim_flag"]) != 0 for row in gate_rows):
        raise AssertionError("long_k23ptab claim gate overclaim")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "input_report_count": 3,
        "certified_input_count": 3,
        "public_transcript_count": 56,
        "opening_row_count": 91,
        "wire_row_count": 56,
        "equiv_row_count": 56,
        "derived_match_count": 56,
        "public_table_equivalence_count": 56,
        "transcript_only_bytes_per_row": 1,
        "wire_row_bytes": 4,
        "transcript_only_total_bytes": 56,
        "wire_total_bytes": 224,
        "baseline_public_exchange_bytes": 1568,
        "saved_vs_wire_bytes": 168,
        "saved_vs_baseline_bytes": 1512,
        "saved_vs_wire_num": 3,
        "saved_vs_wire_den": 4,
        "saved_vs_baseline_num": 27,
        "saved_vs_baseline_den": 28,
        "selector_formula_count": 56,
        "max_transcript_id": 55,
        "max_selected_opening_id": 90,
        "max_residual_class_code": 55,
        "max_selector_value_mod": 5,
        "one_byte_transcript_index_flag": 1,
        "certificate_resident_table_flag": 1,
        "per_message_transport_potential_flag": 1,
        "external_improvement_claim_count": 0,
        "runtime_distribution_claim_count": 0,
        "gate_row_count": 5,
        "satisfied_gate_count": 2,
        "blocking_gate_count": 3,
        "claim_gate_count": 0,
        "public_transport_potential_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23ptab observable {name} mismatch")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23ptab index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator")
    if manifest.get("report_sha256") != report["certificate_sha256"]:
        raise AssertionError("long_k23ptab manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_k23ptab manifest self hash mismatch")

    return {
        "status": "PASS",
        "schema": "long.k23ptab.verification@1",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": expected["report"]["witness"]["summary"],
        "next_highest_yield_item": expected["report"]["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23ptab(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
