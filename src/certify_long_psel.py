from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_psel import (
        CLAUSE_CODES,
        CONTRACT_COLUMNS,
        INDEX_PATH,
        LONG_BINC,
        LONG_DIM4_GATE,
        LONG_PAX,
        LONG_OPROM,
        LONG_RIM,
        LONG_RIM_SELECT,
        LONG_SEL,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_psel import (
        CLAUSE_CODES,
        CONTRACT_COLUMNS,
        INDEX_PATH,
        LONG_BINC,
        LONG_DIM4_GATE,
        LONG_PAX,
        LONG_OPROM,
        LONG_RIM,
        LONG_RIM_SELECT,
        LONG_SEL,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from derive_long_raw import rows_from_table


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


def validate_long_psel() -> dict[str, Any]:
    expected = build_payloads()
    psel = load_json(OUT_DIR / "psel.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if psel != expected["psel"]:
        raise AssertionError("long_psel JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_psel cert mismatch")
    for filename, key in {
        "contract.csv": "contract_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_psel {filename} mismatch")

    for key, expected_array in {
        "contract_table": expected["contract_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_psel table mismatch: {key}")

    if report.get("schema") != "long.psel.report@1":
        raise AssertionError("long_psel report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_psel report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_psel all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_psel checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_psel report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_psel report hash mismatch")

    csv_shapes = [
        ("contract.csv", CONTRACT_COLUMNS, len(CLAUSE_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_psel {filename} shape mismatch")

    table_shapes = {
        "contract_table": (len(CLAUSE_CODES), len(CONTRACT_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_psel {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 8,
        "input_certified_count": 8,
        "contract_clause_count": 10,
        "contract_pass_count": 4,
        "contract_fail_count": 6,
        "first_failure_clause_code": CLAUSE_CODES["physical_selector_axiom_present"],
        "downstream_blocked_clause_count": 5,
        "atom_count": 20,
        "complement_pair_count": 10,
        "rim_phase_count": 63,
        "golden_class_count": 1,
        "golden_unoriented_rim_count": 144,
        "formal_c2_selector_count": 8,
        "physical_selector_axiom_flag": 0,
        "physical_selector_candidate_count": 1,
        "raw_compatible_packet_pair_count": 0,
        "missing_restriction_bridge_count": 3,
        "semantic_transition_operation_flag": 0,
        "stress_transition_shared_key_count": 0,
        "dim4_reduction_certified_flag": 0,
        "certified_dim4_candidate_count": 0,
        "gr_source_selector_ready_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_psel observable {key} mismatch")

    contract_rows = rows_from_table(
        np.asarray(tables["contract_table"]), CONTRACT_COLUMNS
    )
    if sum(row["first_failure_flag"] for row in contract_rows) != 1:
        raise AssertionError("long_psel first failure marker mismatch")
    first_failure = [row for row in contract_rows if row["first_failure_flag"] == 1][0]
    if first_failure["clause_code"] != CLAUSE_CODES["physical_selector_axiom_present"]:
        raise AssertionError("long_psel first failure clause mismatch")
    if [row["pass_flag"] for row in contract_rows[:4]] != [1, 1, 1, 1]:
        raise AssertionError("long_psel prefix pass mismatch")
    if any(row["pass_flag"] != 0 for row in contract_rows[4:]):
        raise AssertionError("long_psel downstream pass mismatch")
    if sum(row["downstream_blocked_flag"] for row in contract_rows) != 5:
        raise AssertionError("long_psel downstream blocked count mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_psel manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_psel manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_psel manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_sel": LONG_SEL,
        "long_rim": LONG_RIM,
        "long_rim_select": LONG_RIM_SELECT,
        "long_binc": LONG_BINC,
        "long_transition_sem": LONG_TRANSITION_SEM,
        "long_dim4_gate": LONG_DIM4_GATE,
        "long_pax": LONG_PAX,
        "long_oprom": LONG_OPROM,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_psel index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_psel index report hash mismatch")

    return {
        "schema": "long.psel.verification@1",
        "status": "PASS",
        "verified_report": str((OUT_DIR / "report.json").relative_to(ROOT)).replace(
            "\\", "/"
        ),
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "closure_boundary": report["closure_boundary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_psel(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
