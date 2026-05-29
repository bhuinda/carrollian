from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_psec import (
        DERIVE_SCRIPT,
        EDGE_COLUMNS,
        EDGE_TEXT_HASH,
        INDEX_PATH,
        INPUT_REPORTS,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        STATUS,
        SURFACE_COLUMNS,
        SURFACE_TEXT_HASH,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_psec import (
        DERIVE_SCRIPT,
        EDGE_COLUMNS,
        EDGE_TEXT_HASH,
        INDEX_PATH,
        INPUT_REPORTS,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        STATUS,
        SURFACE_COLUMNS,
        SURFACE_TEXT_HASH,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
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


def validate_long_psec() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_psec JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_psec cert mismatch")
    for filename, key in {
        "surface.csv": "surface_csv",
        "edge.csv": "edge_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_psec {filename} mismatch")
    for key, expected_array in {
        "surface_table": expected["surface_table"],
        "edge_table": expected["edge_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_psec table mismatch: {key}")

    if report.get("schema") != "long.psec.report@1":
        raise AssertionError("long_psec report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_psec report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_psec all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_psec checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_psec report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_psec report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("surface.csv", SURFACE_COLUMNS, len(expected["surface_table"])),
        ("edge.csv", EDGE_COLUMNS, len(expected["edge_table"])),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_psec {filename} shape mismatch")

    if hashlib.sha256(
        digest_text(SURFACE_COLUMNS, csv_rows["surface.csv"]).encode("ascii")
    ).hexdigest() != SURFACE_TEXT_HASH:
        raise AssertionError("long_psec surface hash mismatch")
    if hashlib.sha256(
        digest_text(EDGE_COLUMNS, csv_rows["edge.csv"]).encode("ascii")
    ).hexdigest() != EDGE_TEXT_HASH:
        raise AssertionError("long_psec edge hash mismatch")
    if hashlib.sha256(
        digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")
    ).hexdigest() != OBS_TEXT_HASH:
        raise AssertionError("long_psec observable hash mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": len(INPUT_REPORTS),
        "certified_input_count": len(INPUT_REPORTS),
        "connected_edge_count": 28,
        "closed_edge_count": 28,
        "sector_count": 39,
        "matrix_unit_count": 985,
        "central_page_count": 39,
        "character_row_count": 38_415,
        "coverage_table_count": 55,
        "covered_rows_total": 365_113,
        "direct_sector_rows": 364_987,
        "direct_sector_rows_resolved": 364_987,
        "alias_registry_rows": 39,
        "atom_domain_rows": 20,
        "registered_support_count": 7,
        "support_projector_count": 7,
        "burning_generator_count": 3,
        "burning_trace_profile_rows": 117,
        "open_normalization_sector_count": 30,
        "dimension_one_fixed_sector_count": 7,
        "remaining_projective_gauge_dimension": 940,
        "focused_psec_seam_closed_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    for name, value in required.items():
        if obs.get(OBS_CODES[name]) != value:
            raise AssertionError(f"long_psec observable {name} mismatch")

    inputs = report.get("inputs", {})
    for name, _code, path in INPUT_REPORTS:
        assert_file_hash(inputs.get(name, {}), path, name)
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "long.psec.manifest@1":
        raise AssertionError("long_psec manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_psec manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_psec manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_psec missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_psec proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_psec proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.psec.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "summary": witness.get("summary"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_psec(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
