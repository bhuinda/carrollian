from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_c59p3r import (
        GAP_CODES,
        GAP_COLUMNS,
        GATE_CODES,
        GATE_COLUMNS,
        INDEX_PATH,
        LONG_C59P3B,
        LONG_C59P3B_BRIDGE,
        LONG_C59P3B_OBS,
        LONG_OPROM,
        LONG_OPROM_OBS,
        LONG_OPROM_PROMOTION,
        LONG_RSEM,
        LONG_RSEM_OBS,
        LONG_RSEM_RELATION,
        LONG_RSEM_TICK,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        RELATION_STRESS_COLUMNS,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_c59p3r import (
        GAP_CODES,
        GAP_COLUMNS,
        GATE_CODES,
        GATE_COLUMNS,
        INDEX_PATH,
        LONG_C59P3B,
        LONG_C59P3B_BRIDGE,
        LONG_C59P3B_OBS,
        LONG_OPROM,
        LONG_OPROM_OBS,
        LONG_OPROM_PROMOTION,
        LONG_RSEM,
        LONG_RSEM_OBS,
        LONG_RSEM_RELATION,
        LONG_RSEM_TICK,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        RELATION_STRESS_COLUMNS,
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


def validate_long_c59p3r() -> dict[str, Any]:
    expected = build_payloads()
    c59p3r = load_json(OUT_DIR / "c59p3r.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if c59p3r != expected["c59p3r"]:
        raise AssertionError("long_c59p3r JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_c59p3r cert mismatch")
    for filename, key in {
        "relation_stress.csv": "relation_stress_csv",
        "gate.csv": "gate_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_c59p3r {filename} mismatch")

    for key, expected_array in {
        "relation_stress_table": expected["relation_stress_table"],
        "gate_table": expected["gate_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_c59p3r table mismatch: {key}")

    if report.get("schema") != "long.c59p3r.report@1":
        raise AssertionError("long_c59p3r report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_c59p3r report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_c59p3r all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_c59p3r checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3r report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_c59p3r report hash mismatch")

    csv_shapes = [
        ("relation_stress.csv", RELATION_STRESS_COLUMNS, 59),
        ("gate.csv", GATE_COLUMNS, len(GATE_CODES)),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_c59p3r {filename} shape mismatch")

    table_shapes = {
        "relation_stress_table": (59, len(RELATION_STRESS_COLUMNS)),
        "gate_table": (len(GATE_CODES), len(GATE_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_c59p3r {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 3,
        "input_certified_count": 3,
        "relation_row_count": 59,
        "guarded_relation_row_count": 59,
        "guarded_semantic_tick_count": 20,
        "multivalued_tick_count": 13,
        "matched_transition_row_count": 59,
        "operation_row_match_count": 0,
        "semantic_transition_match_count": 0,
        "promotion_success_count": 0,
        "promotion_blocked_count": 59,
        "operation_promotion_flag": 0,
        "semantic_a985_operation_flag": 0,
        "endpoint_atom_column_count": 0,
        "raw_endpoint_stress_atom_bridge_flag": 0,
        "current_schema_consumes_atom_score_flag": 0,
        "relation_stress_extension_success_count": 0,
        "relation_stress_extension_blocked_count": 59,
        "relation_stress_extension_flag": 0,
        "physical_selector_axiom_flag": 0,
        "thermal_gravity_flag": 0,
        "next_gap_code": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_c59p3r observable {key} mismatch")

    relation_rows = rows_from_table(
        np.asarray(tables["relation_stress_table"]), RELATION_STRESS_COLUMNS
    )
    if [row["relation_id"] for row in relation_rows] != list(range(59)):
        raise AssertionError("long_c59p3r relation ids mismatch")
    if sum(row["guarded_relation_semantic_flag"] for row in relation_rows) != 59:
        raise AssertionError("long_c59p3r guarded relation count mismatch")
    if sum(row["transition_row_present_flag"] for row in relation_rows) != 59:
        raise AssertionError("long_c59p3r transition-present count mismatch")
    zero_columns = [
        "operation_row_present_flag",
        "semantic_transition_flag",
        "operation_promotion_flag",
        "endpoint_atom_key_flag",
        "stress_atom_bridge_flag",
        "stress_score_consumed_flag",
        "relation_stress_extension_flag",
    ]
    for column in zero_columns:
        if any(row[column] != 0 for row in relation_rows):
            raise AssertionError(f"long_c59p3r nonzero relation column: {column}")
    if sum(row["obstruction_code"] for row in relation_rows) != 59:
        raise AssertionError("long_c59p3r relation obstruction count mismatch")

    gate_rows = rows_from_table(np.asarray(tables["gate_table"]), GATE_COLUMNS)
    if [row["gate_id"] for row in gate_rows] != list(range(len(GATE_CODES))):
        raise AssertionError("long_c59p3r gate order mismatch")
    if [row["present_flag"] for row in gate_rows] != [1, 0, 0, 0, 0, 0, 0]:
        raise AssertionError("long_c59p3r gate present vector mismatch")
    if [row["certified_flag"] for row in gate_rows] != [1, 0, 0, 0, 0, 0, 0]:
        raise AssertionError("long_c59p3r gate certified vector mismatch")
    if [row["obstruction_flag"] for row in gate_rows] != [0, 1, 1, 1, 1, 1, 1]:
        raise AssertionError("long_c59p3r gate obstruction vector mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 0, 0, 0, 0, 0, 0]:
        raise AssertionError("long_c59p3r gap certified vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 1, 0, 0, 0, 0, 0]:
        raise AssertionError("long_c59p3r gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_c59p3r manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_c59p3r manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3r manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_c59p3b": LONG_C59P3B,
        "long_c59p3b_bridge": LONG_C59P3B_BRIDGE,
        "long_c59p3b_obs": LONG_C59P3B_OBS,
        "long_rsem": LONG_RSEM,
        "long_rsem_relation": LONG_RSEM_RELATION,
        "long_rsem_tick": LONG_RSEM_TICK,
        "long_rsem_obs": LONG_RSEM_OBS,
        "long_oprom": LONG_OPROM,
        "long_oprom_promotion": LONG_OPROM_PROMOTION,
        "long_oprom_obs": LONG_OPROM_OBS,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_c59p3r index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3r index report hash mismatch")

    return {
        "schema": "long.c59p3r.verification@1",
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
    print(json.dumps(validate_long_c59p3r(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
