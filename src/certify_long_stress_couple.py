from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_raw import rows_from_table
    from .derive_long_stress_couple import (
        DERIVE_SCRIPT,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_STRESS_EDGE_CSV,
        LONG_STRESS_GATE,
        LONG_TRANSITION_CSV,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        SCHEMA_CODES,
        SCHEMA_COLUMNS,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_raw import rows_from_table
    from derive_long_stress_couple import (
        DERIVE_SCRIPT,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_STRESS_EDGE_CSV,
        LONG_STRESS_GATE,
        LONG_TRANSITION_CSV,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        SCHEMA_CODES,
        SCHEMA_COLUMNS,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )


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


def validate_long_stress_couple() -> dict[str, Any]:
    expected = build_payloads()
    stress_couple = load_json(OUT_DIR / "stress_couple.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if stress_couple != expected["stress_couple"]:
        raise AssertionError("long_stress_couple JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_stress_couple cert mismatch")
    for filename, key in {
        "schema.csv": "schema_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_stress_couple {filename} mismatch")

    for key, expected_array in {
        "schema_table": expected["schema_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_stress_couple table mismatch: {key}")

    if report.get("schema") != "long.stress_couple.report@1":
        raise AssertionError("long_stress_couple report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_stress_couple report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_stress_couple all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_stress_couple checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_stress_couple report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_stress_couple report hash mismatch")

    csv_shapes = [
        ("schema.csv", SCHEMA_COLUMNS, len(SCHEMA_CODES)),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_stress_couple {filename} shape mismatch")

    table_shapes = {
        "schema_table": (len(SCHEMA_CODES), len(SCHEMA_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_stress_couple {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_artifact_count": 3,
        "stress_gate_certified_flag": 1,
        "transition_row_count": 642,
        "stress_edge_row_count": 100,
        "transition_basis_column_count": 2,
        "transition_raw_column_count": 2,
        "transition_atom_column_count": 0,
        "stress_atom_column_count": 3,
        "stress_basis_column_count": 0,
        "shared_certified_coupling_key_count": 0,
        "materialized_coupling_row_count": 0,
        "coupling_map_certified_flag": 0,
        "current_boundary_obstruction_flag": 1,
        "physical_stress_energy_flag": 0,
        "smooth_lorentzian_metric_flag": 0,
        "curvature_einstein_tensor_flag": 0,
        "gr_derivation_flag": 0,
        "open_gap_count": 4,
        "next_gap_code": GAP_CODES["nondegenerate_smooth_lorentzian_metric"],
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_stress_couple observable {key} mismatch")

    schema_rows = rows_from_table(np.asarray(tables["schema_table"]), SCHEMA_COLUMNS)
    if [row["schema_row_id"] for row in schema_rows] != list(range(len(SCHEMA_CODES))):
        raise AssertionError("long_stress_couple schema ids mismatch")
    if sum(row["obstruction_flag"] for row in schema_rows) != 4:
        raise AssertionError("long_stress_couple obstruction schema count mismatch")
    shared_rows = [
        row
        for row in schema_rows
        if row["schema_code"] == SCHEMA_CODES["shared_certified_coupling_key_absent"]
    ]
    if (
        len(shared_rows) != 1
        or shared_rows[0]["value"] != 0
        or shared_rows[0]["obstruction_flag"] != 1
    ):
        raise AssertionError("long_stress_couple shared-key obstruction mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    coupling_rows = [
        row
        for row in gap_rows
        if row["gap_code"] == GAP_CODES["stress_transition_coupling_map"]
    ]
    if (
        len(coupling_rows) != 1
        or coupling_rows[0]["open_flag"] != 0
        or coupling_rows[0]["obstruction_flag"] != 1
    ):
        raise AssertionError("long_stress_couple coupling gap closure mismatch")
    next_rows = [row for row in gap_rows if row["next_flag"] == 1]
    if (
        len(next_rows) != 1
        or next_rows[0]["gap_code"]
        != GAP_CODES["nondegenerate_smooth_lorentzian_metric"]
    ):
        raise AssertionError("long_stress_couple next gap mismatch")
    if sum(row["open_flag"] for row in gap_rows) != 4:
        raise AssertionError("long_stress_couple open gap count mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_stress_gate": LONG_STRESS_GATE,
        "long_transition_csv": LONG_TRANSITION_CSV,
        "long_stress_edge_csv": LONG_STRESS_EDGE_CSV,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.stress_couple.manifest@1":
        raise AssertionError("long_stress_couple manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_stress_couple manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_stress_couple manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_stress_couple missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_stress_couple proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_stress_couple proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.stress_couple.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "summary": witness.get("summary"),
            "schema_code_map": witness.get("schema_code_map"),
            "gap_code_map": witness.get("gap_code_map"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_stress_couple(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
