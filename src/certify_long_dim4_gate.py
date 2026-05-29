from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_dim4_gate import (
        ATLAS,
        CANDIDATE_CODES,
        CANDIDATE_COLUMNS,
        DECISION_CODES,
        DECISION_COLUMNS,
        DERIVE_SCRIPT,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_BINC,
        LONG_BINC_OBS,
        LONG_C2UF,
        LONG_C2UF_OBS,
        LONG_METRIC_RANK_GATE,
        LONG_PSEC,
        LONG_PSEC_OBS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_dim4_gate import (
        ATLAS,
        CANDIDATE_CODES,
        CANDIDATE_COLUMNS,
        DECISION_CODES,
        DECISION_COLUMNS,
        DERIVE_SCRIPT,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_BINC,
        LONG_BINC_OBS,
        LONG_C2UF,
        LONG_C2UF_OBS,
        LONG_METRIC_RANK_GATE,
        LONG_PSEC,
        LONG_PSEC_OBS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
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


def validate_long_dim4_gate() -> dict[str, Any]:
    expected = build_payloads()
    dim4_gate = load_json(OUT_DIR / "dim4_gate.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if dim4_gate != expected["dim4_gate"]:
        raise AssertionError("long_dim4_gate JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_dim4_gate cert mismatch")
    for filename, key in {
        "candidate.csv": "candidate_csv",
        "decision.csv": "decision_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_dim4_gate {filename} mismatch")

    for key, expected_array in {
        "candidate_table": expected["candidate_table"],
        "decision_table": expected["decision_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_dim4_gate table mismatch: {key}")

    if report.get("schema") != "long.dim4_gate.report@1":
        raise AssertionError("long_dim4_gate report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_dim4_gate report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_dim4_gate all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_dim4_gate checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_dim4_gate report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_dim4_gate report hash mismatch")

    csv_shapes = [
        ("candidate.csv", CANDIDATE_COLUMNS, len(CANDIDATE_CODES)),
        ("decision.csv", DECISION_COLUMNS, len(DECISION_CODES)),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_dim4_gate {filename} shape mismatch")

    table_shapes = {
        "candidate_table": (len(CANDIDATE_CODES), len(CANDIDATE_COLUMNS)),
        "decision_table": (len(DECISION_CODES), len(DECISION_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_dim4_gate {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 5,
        "input_certified_count": 5,
        "time_rank": 1,
        "public_rank": 20,
        "public_kernel_dimension": 19,
        "public_quotient_dimension": 1,
        "required_spatial_rank": 3,
        "residual_rank_excess_over_three": 16,
        "rank_gate_dim4_flag": 0,
        "atlas_atom_count": 20,
        "atlas_complement_pair_count": 10,
        "binc_public_atom_count": 20,
        "binc_incidence_rank_over_q": 19,
        "binc_raw_compatible_pair_count": 0,
        "binc_low_support_rank_two_doublet_count": 0,
        "binc_missing_restriction_bridge_count": 3,
        "c2_quotient_state_count": 543,
        "c2_selector_count": 8,
        "c2_physical_selector_axiom_flag": 0,
        "psec_sector_count": 39,
        "psec_open_normalization_sector_count": 30,
        "psec_dimension_one_fixed_sector_count": 7,
        "psec_remaining_projective_gauge_dimension": 940,
        "certified_dim4_candidate_count": 0,
        "dim4_reduction_certified_flag": 0,
        "current_boundary_obstruction_flag": 1,
        "smooth_metric_signature_flag": 0,
        "stress_energy_flag": 0,
        "curvature_einstein_flag": 0,
        "gr_derivation_flag": 0,
        "open_gap_count": 5,
        "next_gap_code": GAP_CODES["nondegenerate_smooth_lorentzian_metric"],
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_dim4_gate observable {key} mismatch")

    candidate_rows = rows_from_table(
        np.asarray(tables["candidate_table"]), CANDIDATE_COLUMNS
    )
    if [row["candidate_id"] for row in candidate_rows] != list(range(len(CANDIDATE_CODES))):
        raise AssertionError("long_dim4_gate candidate ids mismatch")
    if any(row["dim4_candidate_flag"] != 0 for row in candidate_rows):
        raise AssertionError("long_dim4_gate unexpected dim4 candidate")
    if any(row["obstruction_flag"] != 1 for row in candidate_rows):
        raise AssertionError("long_dim4_gate candidate obstruction mismatch")

    decision_rows = rows_from_table(
        np.asarray(tables["decision_table"]), DECISION_COLUMNS
    )
    if any(row["pass_flag"] != 1 for row in decision_rows):
        raise AssertionError("long_dim4_gate decision pass mismatch")
    dim4_decision = decision_rows[DECISION_CODES["dim4_reduction_certified"]]
    if (
        dim4_decision["certified_flag"] != 0
        or dim4_decision["obstruction_flag"] != 1
        or dim4_decision["value"] != 0
    ):
        raise AssertionError("long_dim4_gate dim4 decision mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    dim4_gap = [
        row
        for row in gap_rows
        if row["gap_code"] == GAP_CODES["four_dimensional_spacetime_reduction"]
    ]
    if (
        len(dim4_gap) != 1
        or dim4_gap[0]["open_flag"] != 0
        or dim4_gap[0]["obstruction_flag"] != 1
    ):
        raise AssertionError("long_dim4_gate dim4 gap mismatch")
    next_rows = [row for row in gap_rows if row["next_flag"] == 1]
    if (
        len(next_rows) != 1
        or next_rows[0]["gap_code"] != GAP_CODES["nondegenerate_smooth_lorentzian_metric"]
    ):
        raise AssertionError("long_dim4_gate next gap mismatch")
    if sum(row["open_flag"] for row in gap_rows) != 5:
        raise AssertionError("long_dim4_gate open gap count mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_metric_rank_gate": LONG_METRIC_RANK_GATE,
        "long_binc": LONG_BINC,
        "long_binc_obs": LONG_BINC_OBS,
        "long_psec": LONG_PSEC,
        "long_psec_obs": LONG_PSEC_OBS,
        "long_c2uf": LONG_C2UF,
        "long_c2uf_obs": LONG_C2UF_OBS,
        "atlas": ATLAS,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.dim4_gate.manifest@1":
        raise AssertionError("long_dim4_gate manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_dim4_gate manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_dim4_gate manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_dim4_gate missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_dim4_gate proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_dim4_gate proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.dim4_gate.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "summary": witness.get("summary"),
            "candidate_code_map": witness.get("candidate_code_map"),
            "gap_code_map": witness.get("gap_code_map"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_dim4_gate(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
