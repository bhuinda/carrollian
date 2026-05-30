from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_raw import rows_from_table
    from .derive_long_sel import (
        INDEX_PATH,
        LONG_BINC,
        LONG_C2UF,
        LONG_DIM4_GATE,
        LONG_PSEC,
        LONG_RIM_SELECT,
        LONG_TRANSITION_SEM,
        OBSTRUCTION_COLUMNS,
        OBSTRUCTION_CODES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        SELECTOR_COLUMNS,
        SELECTOR_CODES,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_raw import rows_from_table
    from derive_long_sel import (
        INDEX_PATH,
        LONG_BINC,
        LONG_C2UF,
        LONG_DIM4_GATE,
        LONG_PSEC,
        LONG_RIM_SELECT,
        LONG_TRANSITION_SEM,
        OBSTRUCTION_COLUMNS,
        OBSTRUCTION_CODES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        SELECTOR_COLUMNS,
        SELECTOR_CODES,
        STATUS,
        THEOREM_ID,
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


def validate_long_sel() -> dict[str, Any]:
    expected = build_payloads()
    sel = load_json(OUT_DIR / "sel.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if sel != expected["sel"]:
        raise AssertionError("long_sel JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_sel cert mismatch")
    for filename, key in {
        "selector.csv": "selector_csv",
        "obstruction.csv": "obstruction_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_sel {filename} mismatch")

    for key, expected_array in {
        "selector_table": expected["selector_table"],
        "obstruction_table": expected["obstruction_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_sel table mismatch: {key}")

    if report.get("schema") != "long.sel.report@1":
        raise AssertionError("long_sel report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_sel report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_sel all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_sel checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_sel report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_sel report hash mismatch")

    csv_shapes = [
        ("selector.csv", SELECTOR_COLUMNS, len(SELECTOR_CODES)),
        ("obstruction.csv", OBSTRUCTION_COLUMNS, len(OBSTRUCTION_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_sel {filename} shape mismatch")

    table_shapes = {
        "selector_table": (len(SELECTOR_CODES), len(SELECTOR_COLUMNS)),
        "obstruction_table": (len(OBSTRUCTION_CODES), len(OBSTRUCTION_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_sel {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 6,
        "input_certified_count": 6,
        "c2_selector_count": 8,
        "c2_noncontractible_selector_count": 3,
        "c2_singleton_selector_count": 5,
        "c2_physical_selector_axiom_flag": 0,
        "c2_formal_univalence_flag": 0,
        "c2_lazy63_selector_count": 63,
        "c2_raw543_selector_count": 543,
        "rim_phase_count": 63,
        "golden_phase_selected_flag": 0,
        "golden_unoriented_rim_count": 144,
        "stress_transition_shared_key_count": 0,
        "semantic_transition_operation_flag": 0,
        "raw_compatible_packet_pair_count": 0,
        "low_support_compatible_doublet_count": 6,
        "low_support_rank_two_doublet_count": 0,
        "missing_restriction_bridge_count": 3,
        "psec_open_normalization_sector_count": 30,
        "psec_remaining_projective_gauge_dimension": 940,
        "certified_dim4_candidate_count": 0,
        "dim4_reduction_certified_flag": 0,
        "physical_selector_candidate_count": 0,
        "missing_physical_selector_axiom_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_sel observable {key} mismatch")
    if not (
        obs[OBS_CODES["stress_overlap_global_directed_max"]]
        > obs[OBS_CODES["stress_overlap_golden_directed_max"]]
    ):
        raise AssertionError("long_sel stress gap mismatch")

    selector_rows = rows_from_table(
        np.asarray(tables["selector_table"]), SELECTOR_COLUMNS
    )
    if any(row["physical_selector_flag"] != 0 for row in selector_rows):
        raise AssertionError("long_sel unexpected physical selector")
    if any(row["open_obstruction_flag"] != 1 for row in selector_rows):
        raise AssertionError("long_sel selector obstruction mismatch")
    if sum(row["rim_phase_key_flag"] for row in selector_rows) != 2:
        raise AssertionError("long_sel rim-phase selector row mismatch")
    if sum(row["formal_selector_flag"] for row in selector_rows) != 3:
        raise AssertionError("long_sel formal selector row mismatch")

    obstruction_rows = rows_from_table(
        np.asarray(tables["obstruction_table"]), OBSTRUCTION_COLUMNS
    )
    if any(row["open_flag"] != 1 for row in obstruction_rows):
        raise AssertionError("long_sel obstruction open flag mismatch")
    if any(row["certified_obstruction_flag"] != 1 for row in obstruction_rows):
        raise AssertionError("long_sel certified obstruction flag mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_sel manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_sel manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_sel manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_rim_select": LONG_RIM_SELECT,
        "long_c2uf": LONG_C2UF,
        "long_psec": LONG_PSEC,
        "long_binc": LONG_BINC,
        "long_dim4_gate": LONG_DIM4_GATE,
        "long_transition_sem": LONG_TRANSITION_SEM,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_sel index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_sel index report hash mismatch")

    return {
        "schema": "long.sel.verification@1",
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
    print(json.dumps(validate_long_sel(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
