from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_hcinv import (
        DERIVE_SCRIPT,
        EDGE_COLUMNS,
        EDGE_TEXT_HASH,
        INDEX_PATH,
        INPUT_REPORTS,
        INVARIANT_COLUMNS,
        INVARIANT_NAMES,
        INVARIANT_TEXT_HASH,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        SAMPLE_COLUMNS,
        SAMPLE_TEXT_HASH,
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
    from derive_long_hcinv import (
        DERIVE_SCRIPT,
        EDGE_COLUMNS,
        EDGE_TEXT_HASH,
        INDEX_PATH,
        INPUT_REPORTS,
        INVARIANT_COLUMNS,
        INVARIANT_NAMES,
        INVARIANT_TEXT_HASH,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        SAMPLE_COLUMNS,
        SAMPLE_TEXT_HASH,
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


def assert_locked_hash(label: str, actual: str, expected: str) -> None:
    if not expected:
        raise AssertionError(f"{label} witness hash is not locked")
    if actual != expected:
        raise AssertionError(f"{label} witness hash mismatch")


def validate_long_hcinv() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_hcinv JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_hcinv cert mismatch")
    for filename, key in {
        "surface.csv": "surface_csv",
        "invariant.csv": "invariant_csv",
        "edge.csv": "edge_csv",
        "sample.csv": "sample_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_hcinv {filename} mismatch")
    for key, expected_array in {
        "surface_table": expected["surface_table"],
        "invariant_table": expected["invariant_table"],
        "edge_table": expected["edge_table"],
        "sample_table": expected["sample_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_hcinv table mismatch: {key}")

    if report.get("schema") != "long.hcinv.report@1":
        raise AssertionError("long_hcinv report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_hcinv report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_hcinv all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_hcinv checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_hcinv report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_hcinv report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("surface.csv", SURFACE_COLUMNS, len(INPUT_REPORTS)),
        ("invariant.csv", INVARIANT_COLUMNS, len(INVARIANT_NAMES)),
        ("edge.csv", EDGE_COLUMNS, 15),
        ("sample.csv", SAMPLE_COLUMNS, 6),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_hcinv {filename} shape mismatch")

    assert_locked_hash(
        "surface",
        hashlib.sha256(
            digest_text(SURFACE_COLUMNS, csv_rows["surface.csv"]).encode("ascii")
        ).hexdigest(),
        SURFACE_TEXT_HASH,
    )
    assert_locked_hash(
        "invariant",
        hashlib.sha256(
            digest_text(INVARIANT_COLUMNS, csv_rows["invariant.csv"]).encode("ascii")
        ).hexdigest(),
        INVARIANT_TEXT_HASH,
    )
    assert_locked_hash(
        "edge",
        hashlib.sha256(
            digest_text(EDGE_COLUMNS, csv_rows["edge.csv"]).encode("ascii")
        ).hexdigest(),
        EDGE_TEXT_HASH,
    )
    assert_locked_hash(
        "sample",
        hashlib.sha256(
            digest_text(SAMPLE_COLUMNS, csv_rows["sample.csv"]).encode("ascii")
        ).hexdigest(),
        SAMPLE_TEXT_HASH,
    )
    assert_locked_hash(
        "observable",
        hashlib.sha256(
            digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")
        ).hexdigest(),
        OBS_TEXT_HASH,
    )

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "input_report_count": 12,
        "accepted_input_count": 12,
        "connected_edge_count": 15,
        "closed_edge_count": 10,
        "gap_edge_count": 5,
        "raw543_orbit_count": 543,
        "raw543_fixed_orbit_count": 63,
        "raw543_pair_orbit_count": 480,
        "transport_orbit_count": 543,
        "tau_projection_rank": 543,
        "tau_projection_nullity": 480,
        "residue_mask_count": 2048,
        "nonzero_height_mask_count": 2047,
        "e33_support": 56,
        "e33_positive_count": 28,
        "e33_negative_count": 28,
        "corrected_vector_count": 2048,
        "lambda_act_kernel_masks": 2048,
        "lambda_act_kernel_failures": 0,
        "zero_anomaly_orbit_count": 71,
        "nonzero_anomaly_orbit_count": 472,
        "anomaly_cocycle_gcd_abs": 3072,
        "selector_candidate_count": 543,
        "selector_free_unique_operator_flag": 0,
        "foam_support_dimension": 56,
        "foam_core_rank": 33,
        "foam_bridge_kernel_dimension": 23,
        "height_coherent_operator_materialized_flag": 0,
        "focused_hcinv_closed_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_hcinv observable {name} mismatch")

    inputs = report.get("inputs", {})
    for name, _code, path in INPUT_REPORTS:
        assert_file_hash(inputs.get(name, {}), path, name)
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "long.hcinv.manifest@1":
        raise AssertionError("long_hcinv manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_hcinv manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_hcinv manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_hcinv missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_hcinv proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_hcinv proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.hcinv.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "summary": witness.get("summary"),
            "selector_delta_samples": witness.get("selector_delta_samples"),
            "operator_boundary": witness.get("operator_boundary"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_hcinv(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
