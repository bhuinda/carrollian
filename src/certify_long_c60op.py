from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_c60op import (
        COMPOSITION_COLUMNS,
        FAMILY_CODES,
        FAMILY_COLUMNS,
        INDEX_PATH,
        LONG_OPROM,
        LONG_OPROM_PROMOTION,
        LONG_RSEM,
        LONG_RSEM_RELATION,
        OBS_CODES,
        OBS_COLUMNS,
        OPCODE_COLUMNS,
        OUT_DIR,
        RESULT_STATUS,
        RULE_CODES,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_c60op import (
        COMPOSITION_COLUMNS,
        FAMILY_CODES,
        FAMILY_COLUMNS,
        INDEX_PATH,
        LONG_OPROM,
        LONG_OPROM_PROMOTION,
        LONG_RSEM,
        LONG_RSEM_RELATION,
        OBS_CODES,
        OBS_COLUMNS,
        OPCODE_COLUMNS,
        OUT_DIR,
        RESULT_STATUS,
        RULE_CODES,
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


def validate_long_c60op() -> dict[str, Any]:
    expected = build_payloads()
    c60op = load_json(OUT_DIR / "c60op.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if c60op != expected["c60op"]:
        raise AssertionError("long_c60op JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_c60op cert mismatch")
    for filename, key in {
        "opcode.csv": "opcode_csv",
        "family.csv": "family_csv",
        "composition.csv": "composition_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_c60op {filename} mismatch")

    for key, expected_array in {
        "opcode_table": expected["opcode_table"],
        "family_table": expected["family_table"],
        "composition_table": expected["composition_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_c60op table mismatch: {key}")

    if report.get("schema") != "long.c60op.report@1":
        raise AssertionError("long_c60op report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_c60op report status mismatch")
    if report.get("result_status") != RESULT_STATUS:
        raise AssertionError("long_c60op result status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_c60op all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_c60op checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c60op report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_c60op report hash mismatch")

    csv_shapes = [
        ("opcode.csv", OPCODE_COLUMNS, 59),
        ("family.csv", FAMILY_COLUMNS, len(FAMILY_CODES)),
        ("composition.csv", COMPOSITION_COLUMNS, 174),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_c60op {filename} shape mismatch")

    table_shapes = {
        "opcode_table": (59, len(OPCODE_COLUMNS)),
        "family_table": (len(FAMILY_CODES), len(FAMILY_COLUMNS)),
        "composition_table": (174, len(COMPOSITION_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_c60op {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 2,
        "input_certified_count": 2,
        "semantic_opcode_row_count": 59,
        "golden_tick_covered_count": 20,
        "c60_transition_edge_used_count": 30,
        "c60_endpoint_atom_used_count": 60,
        "raw_endpoint_backed_row_count": 59,
        "unit_time_row_count": 59,
        "alpha_flux_law_pass_row_count": 59,
        "semantic_opcode_assigned_row_count": 59,
        "adjacent_composition_check_count": 174,
        "adjacent_composition_failure_count": 0,
        "selector_flux_transfer_count": 36,
        "alpha_flux_balance_count": 21,
        "static_selector_anchor_count": 2,
        "c60_hexagon_tick_state_count": 20,
        "c60_transition_bond_count": 30,
        "c60_endpoint_atom_count": 60,
        "oprom_operation_promotion_flag": 0,
        "semantic_a985_operation_flag": 0,
        "physical_signature_validated_flag": 0,
        "manufacturability_validation_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_c60op observable {key} mismatch")

    opcode_rows = rows_from_table(np.asarray(tables["opcode_table"]), OPCODE_COLUMNS)
    if [row["opcode_id"] for row in opcode_rows] != list(range(59)):
        raise AssertionError("long_c60op opcode id order mismatch")
    if len({row["visible_index"] for row in opcode_rows}) != 20:
        raise AssertionError("long_c60op visible tick coverage mismatch")
    if len({row["c60_edge_id"] for row in opcode_rows}) != 30:
        raise AssertionError("long_c60op c60 edge coverage mismatch")
    atoms = {
        atom
        for row in opcode_rows
        for atom in [row["c60_source_atom_id"], row["c60_target_atom_id"]]
    }
    if atoms != set(range(60)):
        raise AssertionError("long_c60op endpoint atom coverage mismatch")
    if any(row["semantic_a985_operation_flag"] != 0 for row in opcode_rows):
        raise AssertionError("long_c60op A985 operation boundary mismatch")
    if any(row["physical_signature_validated_flag"] != 0 for row in opcode_rows):
        raise AssertionError("long_c60op physical signature boundary mismatch")

    family_rows = rows_from_table(np.asarray(tables["family_table"]), FAMILY_COLUMNS)
    if [row["opcode_count"] for row in family_rows] != [36, 21, 2]:
        raise AssertionError("long_c60op family count mismatch")

    composition_rows = rows_from_table(
        np.asarray(tables["composition_table"]), COMPOSITION_COLUMNS
    )
    if len(composition_rows) != 174:
        raise AssertionError("long_c60op composition row count mismatch")
    if any(row["pass_flag"] != 1 for row in composition_rows):
        raise AssertionError("long_c60op composition failure mismatch")
    if sorted({row["rule_code"] for row in composition_rows}) != list(
        range(len(RULE_CODES))
    ):
        raise AssertionError("long_c60op composition rule coverage mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_c60op manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_c60op manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c60op manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_rsem": LONG_RSEM,
        "long_rsem_relation": LONG_RSEM_RELATION,
        "long_oprom": LONG_OPROM,
        "long_oprom_promotion": LONG_OPROM_PROMOTION,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_c60op index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c60op index report hash mismatch")

    return {
        "schema": "long.c60op.verification@1",
        "status": "PASS",
        "verified_report": str((OUT_DIR / "report.json").relative_to(ROOT)).replace(
            "\\", "/"
        ),
        "certificate_sha256": report["certificate_sha256"],
        "result_status": report["result_status"],
        "summary": report["witness"]["summary"],
        "closure_boundary": report["closure_boundary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_c60op(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
