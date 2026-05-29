from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_eta2 import (
        DERIVE_SCRIPT,
        ETA6_CORE_REPORT,
        ETA6_P21_REPORT,
        ETA6_P5_TABLES,
        FUSION_TENSOR,
        GATE_COLUMNS,
        INDEX_PATH,
        INDUCED_EDGE_COLUMNS,
        LONG_ETA_REPORT,
        LONG_REC_REPORT,
        LONG_REC_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        OWNER_COLUMNS_OUT,
        PARENT_COLUMNS,
        SOURCE_TARGET,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_eta2 import (
        DERIVE_SCRIPT,
        ETA6_CORE_REPORT,
        ETA6_P21_REPORT,
        ETA6_P5_TABLES,
        FUSION_TENSOR,
        GATE_COLUMNS,
        INDEX_PATH,
        INDUCED_EDGE_COLUMNS,
        LONG_ETA_REPORT,
        LONG_REC_REPORT,
        LONG_REC_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        OWNER_COLUMNS_OUT,
        PARENT_COLUMNS,
        SOURCE_TARGET,
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


def assert_file_hash(entry: dict[str, Any], expected_path: Path, label: str) -> None:
    expected_rel = expected_path.relative_to(ROOT).as_posix()
    if entry.get("path") != expected_rel:
        raise AssertionError(f"{label} path mismatch: {entry.get('path')}")
    if entry.get("sha256") != h_file(expected_path):
        raise AssertionError(f"{label} sha256 mismatch")


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def table_rows(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def validate_long_eta2() -> dict[str, Any]:
    expected = build_payloads()
    eta2 = load_json(OUT_DIR / "eta2.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if eta2 != expected["eta2"]:
        raise AssertionError("long_eta2 eta2 JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_eta2 cert mismatch")
    for filename, key in {
        "parent.csv": "parent_csv",
        "gate.csv": "gate_csv",
        "owner.csv": "owner_csv",
        "edge.csv": "edge_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_eta2 {filename} mismatch")

    for key, expected_array in {
        "parent_table": expected["parent_table"],
        "gate_table": expected["gate_table"],
        "owner_table": expected["owner_table"],
        "edge_table": expected["edge_table"],
        "observable_table": expected["observable_table"],
        "active_owner_ids": expected["active_owner_ids"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_eta2 table mismatch: {key}")

    if report.get("schema") != "long.eta2.report@1":
        raise AssertionError("long_eta2 report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_eta2 report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_eta2 all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_eta2 checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_eta2 report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_eta2 report hash mismatch")

    parent_header, parent_rows = read_csv(OUT_DIR / "parent.csv")
    gate_header, gate_rows = read_csv(OUT_DIR / "gate.csv")
    owner_header, owner_rows = read_csv(OUT_DIR / "owner.csv")
    edge_header, edge_rows = read_csv(OUT_DIR / "edge.csv")
    if parent_header != PARENT_COLUMNS or len(parent_rows) != 30:
        raise AssertionError("long_eta2 parent CSV shape mismatch")
    if gate_header != GATE_COLUMNS or len(gate_rows) != 6:
        raise AssertionError("long_eta2 gate CSV shape mismatch")
    if owner_header != OWNER_COLUMNS_OUT or len(owner_rows) != 51:
        raise AssertionError("long_eta2 owner CSV shape mismatch")
    if edge_header != INDUCED_EDGE_COLUMNS or len(edge_rows) != 91:
        raise AssertionError("long_eta2 edge CSV shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "line_point_count": 985,
        "gate_count": 6,
        "parenthesization_count": 5,
        "parent_row_count": 30,
        "gate_support_total": 5_420_393_088,
        "gate_mult_total": 29_385_031_680,
        "support_occurrence_total": 16_261_179_264,
        "mult_occurrence_total": 88_155_095_040,
        "active_owner_count": 51,
        "owner_support_occurrence_min": 2352,
        "owner_support_occurrence_max": 4_271_578_880,
        "owner_mult_occurrence_min": 110_592,
        "owner_mult_occurrence_max": 15_373_172_736,
        "slack_min": 0,
        "slack_max": 239,
        "slack_sum": 1_387_594_500_520,
        "owner_weak_class_count": 2,
        "weak11_owner_count": 50,
        "weak12_owner_count": 1,
        "weak11_support_occurrence": 13_114_415_232,
        "weak12_support_occurrence": 3_146_764_032,
        "weak11_mult_occurrence": 74_773_168_128,
        "weak12_mult_occurrence": 13_381_926_912,
        "owner_induced_edge_count": 91,
        "owner_induced_boundary_count": 5629,
        "owner_induced_source0_boundary_count": 4938,
        "owner_induced_source1_boundary_count": 691,
        "owner_pair_count": 1275,
        "owner_distance_min": 1,
        "owner_distance_max": 11,
        "owner_distance_sum": 6674,
        "owner_cell_mass": 749_239,
        "owner_cell_min": 1,
        "owner_cell_max": 197_910,
        "induced_component_count": 3,
        "induced_component_max_size": 33,
        "long_component_count": 1,
        "support_projection_flag": 1,
        "mult_projection_flag": 1,
        "p5_expected_counts_match": 1,
        "eta6_core_input_certified": 1,
        "eta6_p21_input_certified": 1,
        "long_eta_input_certified": 1,
        "long_rec_input_certified": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_eta2 observable {key} mismatch")

    finite_lln = report.get("witness", {}).get("finite_lln", {})
    required_bigints = {
        "support_owner_population": 16_261_179_264,
        "support_owner_var_den": 264_425_951_055_943_581_696,
        "support_owner_var_num_sum": 226_219_720_156_830_131_200,
        "mult_owner_population": 88_155_095_040,
        "mult_owner_var_den": 7_771_320_781_511_432_601_600,
        "mult_owner_var_num_sum": 6_851_211_013_076_451_065_856,
    }
    for key, value in required_bigints.items():
        if finite_lln.get(key) != value:
            raise AssertionError(f"long_eta2 finite_lln {key} mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "source_target": SOURCE_TARGET,
        "fusion_tensor": FUSION_TENSOR,
        "eta6_core_report": ETA6_CORE_REPORT,
        "eta6_p21_report": ETA6_P21_REPORT,
        "eta6_p5_tables": ETA6_P5_TABLES,
        "long_eta_report": LONG_ETA_REPORT,
        "long_rec_report": LONG_REC_REPORT,
        "long_rec_tables": LONG_REC_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.eta2.manifest@1":
        raise AssertionError("long_eta2 manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_eta2 manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_eta2 manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_eta2 missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_eta2 index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("long_eta2 index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.eta2.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": {
            "fiber_scope": witness.get("fiber_scope"),
            "gate": witness.get("gate"),
            "projection": witness.get("projection"),
            "weak_projection": witness.get("weak_projection"),
            "transition": witness.get("transition"),
            "finite_lln": witness.get("finite_lln"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_eta2(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
