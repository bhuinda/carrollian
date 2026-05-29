from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_binc import (
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
    from derive_long_binc import (
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


def validate_long_binc() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_binc JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_binc cert mismatch")
    for filename, key in {
        "surface.csv": "surface_csv",
        "edge.csv": "edge_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_binc {filename} mismatch")
    for key, expected_array in {
        "surface_table": expected["surface_table"],
        "edge_table": expected["edge_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_binc table mismatch: {key}")

    if report.get("schema") != "long.binc.report@1":
        raise AssertionError("long_binc report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_binc report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_binc all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_binc checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_binc report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_binc report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("surface.csv", SURFACE_COLUMNS, len(expected["surface_table"])),
        ("edge.csv", EDGE_COLUMNS, len(expected["edge_table"])),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_binc {filename} shape mismatch")

    if hashlib.sha256(
        digest_text(SURFACE_COLUMNS, csv_rows["surface.csv"]).encode("ascii")
    ).hexdigest() != SURFACE_TEXT_HASH:
        raise AssertionError("long_binc surface hash mismatch")
    if hashlib.sha256(
        digest_text(EDGE_COLUMNS, csv_rows["edge.csv"]).encode("ascii")
    ).hexdigest() != EDGE_TEXT_HASH:
        raise AssertionError("long_binc edge hash mismatch")
    if hashlib.sha256(
        digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")
    ).hexdigest() != OBS_TEXT_HASH:
        raise AssertionError("long_binc observable hash mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": len(INPUT_REPORTS),
        "certified_input_count": len(INPUT_REPORTS),
        "connected_edge_count": 17,
        "closed_edge_count": 17,
        "public_atom_count": 20,
        "loop_step_atom_count": 25,
        "directed_pair_projection_count": 30,
        "missing_directed_pair_count": 5,
        "incidence_rank_over_q": 19,
        "zero_sum_boundary_lattice_index": 32,
        "boundary_nonunit_factor_count": 3,
        "boundary_lattice_exponent": 4,
        "packet_doublet_count": 10,
        "packet_operator_rank": 20,
        "packet_snf_factor_count": 20,
        "packet_snf_prime_count": 2,
        "raw_bridge_candidate_count": 3,
        "raw_bridge_columns_available_flag": 0,
        "raw_compatible_pair_count": 0,
        "minimal_scalar_with_pair": 6,
        "joint_boundary_packet_scalar_lcm": 12,
        "row_scalar_divisibility": 6,
        "loop_step_columns_tested": 25,
        "loop_step_columns_passing": 0,
        "low_support_candidate_count": 800,
        "low_support_even_candidate_count": 12,
        "low_support_compatible_doublet_count": 6,
        "low_support_rank_two_doublet_count": 0,
        "explicit_two_step_packet_action_flag": 1,
        "missing_restriction_bridge_count": 3,
        "scattering_generator_count": 11,
        "scattering_directed_transition_count": 22_528,
        "label_coordinate_count": 20,
        "label_transition_edge_count": 40,
        "prime_union_count": 3,
        "focused_binc_seam_closed_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    for name, value in required.items():
        if obs.get(OBS_CODES[name]) != value:
            raise AssertionError(f"long_binc observable {name} mismatch")

    inputs = report.get("inputs", {})
    for name, _code, path in INPUT_REPORTS:
        assert_file_hash(inputs.get(name, {}), path, name)
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "long.binc.manifest@1":
        raise AssertionError("long_binc manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_binc manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_binc manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_binc missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_binc proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_binc proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.binc.verification@1",
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
    print(json.dumps(validate_long_binc(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
