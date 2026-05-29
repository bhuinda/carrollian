from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_gr import (
        DERIVE_SCRIPT,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        INPUTS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        SURFACE_COLUMNS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_gr import (
        DERIVE_SCRIPT,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        INPUTS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        SURFACE_COLUMNS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
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


def validate_long_gr() -> dict[str, Any]:
    expected = build_payloads()
    pathway = load_json(OUT_DIR / "pathway.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if pathway != expected["pathway"]:
        raise AssertionError("long_gr pathway JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_gr cert mismatch")
    for filename, key in {
        "surface.csv": "surface_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_gr {filename} mismatch")

    for key, expected_array in {
        "surface_table": expected["surface_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_gr table mismatch: {key}")

    if report.get("schema") != "long.gr.report@1":
        raise AssertionError("long_gr report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_gr report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_gr all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_gr checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_gr report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_gr report hash mismatch")

    csv_shapes = [
        ("surface.csv", SURFACE_COLUMNS, 10),
        ("gap.csv", GAP_COLUMNS, 6),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_gr {filename} shape mismatch")

    table_shapes = {
        "surface_table": (10, len(SURFACE_COLUMNS)),
        "gap_table": (6, len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_gr {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 10,
        "input_certified_count": 10,
        "surface_count": 10,
        "certified_surface_count": 10,
        "a985_chain_surface_count": 10,
        "finite_surface_count": 10,
        "continuum_surface_count": 0,
        "gr_derivation_surface_count": 0,
        "open_gr_gap_count": 6,
        "required_gr_gap_count": 6,
        "certified_gr_gap_count": 0,
        "next_gap_code": GAP_CODES["smooth_four_dimensional_lorentzian_limit"],
        "pathway_certified_flag": 1,
        "a985_alone_gr_derivation_complete_flag": 0,
        "continuum_gr_claim_flag": 0,
        "physical_stress_energy_certified_flag": 0,
        "long_gate_required_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_gr observable {key} mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    next_rows = [row for row in gap_rows if row["next_flag"] == 1]
    if (
        len(next_rows) != 1
        or next_rows[0]["obligation_code"]
        != GAP_CODES["smooth_four_dimensional_lorentzian_limit"]
    ):
        raise AssertionError("long_gr next gap mismatch")
    if any(row["certified_flag"] != 0 for row in gap_rows):
        raise AssertionError("long_gr should not certify GR bridge gaps")

    inputs = report.get("inputs", {})
    for key, (path, _) in INPUTS.items():
        assert_file_hash(inputs.get(key, {}), path, key)
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive_script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "long.gr.manifest@1":
        raise AssertionError("long_gr manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_gr manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_gr manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_gr missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_gr proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_gr proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.gr.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "summary": witness.get("summary"),
            "gap_code_map": witness.get("gap_code_map"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_gr(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
