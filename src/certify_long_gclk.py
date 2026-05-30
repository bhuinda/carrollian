from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_gclk import (
        ATOM_COLUMNS,
        CLOCK_COLUMNS,
        CYCLE_COLUMNS,
        DECAGON_COLUMNS,
        FACE_COLUMNS,
        INDEX_PATH,
        JOHNSON_COLUMNS,
        LONG_CONTACT_CSV,
        LONG_F63,
        LONG_F63_ATOM,
        LONG_GLAW,
        LONG_GLAW_LAW,
        LONG_RIM,
        LONG_RIM_ORBIT,
        LONG_TRANSITION_CSV,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        POWER_COLUMNS,
        SCHEMA_CODES,
        SCHEMA_COLUMNS,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_gclk import (
        ATOM_COLUMNS,
        CLOCK_COLUMNS,
        CYCLE_COLUMNS,
        DECAGON_COLUMNS,
        FACE_COLUMNS,
        INDEX_PATH,
        JOHNSON_COLUMNS,
        LONG_CONTACT_CSV,
        LONG_F63,
        LONG_F63_ATOM,
        LONG_GLAW,
        LONG_GLAW_LAW,
        LONG_RIM,
        LONG_RIM_ORBIT,
        LONG_TRANSITION_CSV,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        POWER_COLUMNS,
        SCHEMA_CODES,
        SCHEMA_COLUMNS,
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


def validate_long_gclk() -> dict[str, Any]:
    expected = build_payloads()
    gclk = load_json(OUT_DIR / "gclk.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if gclk != expected["gclk"]:
        raise AssertionError("long_gclk JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_gclk cert mismatch")
    for filename, key in {
        "atom.csv": "atom_csv",
        "johnson.csv": "johnson_csv",
        "cycle.csv": "cycle_csv",
        "clock.csv": "clock_csv",
        "power.csv": "power_csv",
        "decagon.csv": "decagon_csv",
        "face.csv": "face_csv",
        "schema.csv": "schema_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_gclk {filename} mismatch")

    for key, expected_array in {
        "atom_table": expected["atom_table"],
        "johnson_table": expected["johnson_table"],
        "cycle_table": expected["cycle_table"],
        "clock_table": expected["clock_table"],
        "power_table": expected["power_table"],
        "decagon_table": expected["decagon_table"],
        "face_table": expected["face_table"],
        "schema_table": expected["schema_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_gclk table mismatch: {key}")

    if report.get("schema") != "long.gclk.report@2":
        raise AssertionError("long_gclk report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_gclk report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_gclk all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_gclk checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_gclk report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_gclk report hash mismatch")

    csv_shapes = [
        ("atom.csv", ATOM_COLUMNS, 20),
        ("johnson.csv", JOHNSON_COLUMNS, 90),
        ("cycle.csv", CYCLE_COLUMNS, 20),
        ("clock.csv", CLOCK_COLUMNS, 20),
        ("power.csv", POWER_COLUMNS, 11),
        ("decagon.csv", DECAGON_COLUMNS, 20),
        ("face.csv", FACE_COLUMNS, 5),
        ("schema.csv", SCHEMA_COLUMNS, len(SCHEMA_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_gclk {filename} shape mismatch")

    table_shapes = {
        "atom_table": (20, len(ATOM_COLUMNS)),
        "johnson_table": (90, len(JOHNSON_COLUMNS)),
        "cycle_table": (20, len(CYCLE_COLUMNS)),
        "clock_table": (20, len(CLOCK_COLUMNS)),
        "power_table": (11, len(POWER_COLUMNS)),
        "decagon_table": (20, len(DECAGON_COLUMNS)),
        "face_table": (5, len(FACE_COLUMNS)),
        "schema_table": (len(SCHEMA_CODES), len(SCHEMA_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_gclk {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 4,
        "input_certified_count": 4,
        "coordinate_dimension": 6,
        "d20_atom_count": 20,
        "grade3_atom_count": 20,
        "complement_pair_count": 10,
        "johnson_vertex_count": 20,
        "johnson_edge_count": 90,
        "johnson_degree": 9,
        "hypersimplex_dimension": 5,
        "hypersimplex_f0": 20,
        "hypersimplex_f1": 90,
        "hypersimplex_f2": 120,
        "hypersimplex_f3": 60,
        "hypersimplex_f4": 12,
        "golden_selector_law_flag": 1,
        "golden_class_id": 0,
        "golden_orbit_id": 122,
        "golden_unoriented_rim_count": 144,
        "visible_cycle_edge_count": 20,
        "visible_cycle_unique_atom_count": 20,
        "visible_cycle_johnson_edge_count": 20,
        "affine_sigma_order": 5,
        "affine_clock_order": 10,
        "affine_tick_visible_shift": 2,
        "affine_tick_cycle_match_count": 20,
        "affine_fifth_tick_complement_count": 20,
        "affine_tenth_tick_identity_count": 20,
        "even_decagon_match_count": 10,
        "odd_decagon_match_count": 10,
        "s6_stabilizer_order": 5,
        "affine_stabilizer_order": 10,
        "golden_orbit_size_from_stabilizer": 144,
        "transition_row_count": 642,
        "contact_row_count": 642,
        "atom_transition_shared_key_count": 0,
        "atom_transition_schema_key_flag": 0,
        "semantic_transition_operation_flag": 0,
        "semantic_transition_realized_count": 0,
        "physical_transition_flag": 0,
        "gr_source_ready_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_gclk observable {key} mismatch")

    atom_rows = rows_from_table(np.asarray(tables["atom_table"]), ATOM_COLUMNS)
    if [row["atom_id"] for row in atom_rows] != list(range(20)):
        raise AssertionError("long_gclk atom id order mismatch")
    if any(row["coordinate_weight"] != 3 or row["grade3_flag"] != 1 for row in atom_rows):
        raise AssertionError("long_gclk atom grade mismatch")
    if any(
        row["complement_coordinate_mask"] != (row["coordinate_mask"] ^ 63)
        for row in atom_rows
    ):
        raise AssertionError("long_gclk atom complement coordinate mismatch")

    johnson_rows = rows_from_table(
        np.asarray(tables["johnson_table"]), JOHNSON_COLUMNS
    )
    if [row["edge_id"] for row in johnson_rows] != list(range(90)):
        raise AssertionError("long_gclk Johnson edge ids mismatch")
    if any(
        row["hamming_distance"] != 2
        or row["intersection_size"] != 2
        or row["johnson_edge_flag"] != 1
        for row in johnson_rows
    ):
        raise AssertionError("long_gclk Johnson edge row mismatch")

    cycle_rows = rows_from_table(np.asarray(tables["cycle_table"]), CYCLE_COLUMNS)
    if [row["visible_edge_id"] for row in cycle_rows] != list(range(20)):
        raise AssertionError("long_gclk cycle edge ids mismatch")
    if [row["visible_accumulated_time"] for row in cycle_rows] != list(range(1, 21)):
        raise AssertionError("long_gclk visible time order mismatch")
    if any(
        row["hamming_distance"] != 2
        or row["intersection_size"] != 2
        or row["johnson_edge_flag"] != 1
        or row["visible_delta_t"] != 1
        for row in cycle_rows
    ):
        raise AssertionError("long_gclk visible cycle mismatch")

    clock_rows = rows_from_table(np.asarray(tables["clock_table"]), CLOCK_COLUMNS)
    if [row["visible_index"] for row in clock_rows] != list(range(20)):
        raise AssertionError("long_gclk clock visible indices mismatch")
    if any(
        row["target_atom_id"] != row["expected_atom_id"]
        or row["visible_shift"] != 2
        or row["hidden_delta_t"] != 1
        or row["tick_match_flag"] != 1
        or row["parity_preserved_flag"] != 1
        for row in clock_rows
    ):
        raise AssertionError("long_gclk affine clock row mismatch")

    power_rows = rows_from_table(np.asarray(tables["power_table"]), POWER_COLUMNS)
    if [row["power_id"] for row in power_rows] != list(range(11)):
        raise AssertionError("long_gclk power ids mismatch")
    if any(row["cycle_match_count"] != 20 for row in power_rows):
        raise AssertionError("long_gclk power cycle match mismatch")
    if power_rows[5]["complement_match_count"] != 20:
        raise AssertionError("long_gclk fifth tick complement mismatch")
    if power_rows[10]["identity_match_count"] != 20:
        raise AssertionError("long_gclk tenth tick identity mismatch")

    decagon_rows = rows_from_table(
        np.asarray(tables["decagon_table"]), DECAGON_COLUMNS
    )
    if any(row["decagon_match_flag"] != 1 for row in decagon_rows):
        raise AssertionError("long_gclk decagon row mismatch")
    if decagon_rows[0]["seed_atom_id"] != 0 or decagon_rows[1]["seed_atom_id"] != 1:
        raise AssertionError("long_gclk decagon seed mismatch")

    face_rows = rows_from_table(np.asarray(tables["face_table"]), FACE_COLUMNS)
    if [row["face_count"] for row in face_rows] != [20, 90, 120, 60, 12]:
        raise AssertionError("long_gclk hypersimplex f-vector mismatch")

    schema_rows = rows_from_table(np.asarray(tables["schema_table"]), SCHEMA_COLUMNS)
    if [row["schema_code"] for row in schema_rows] != list(range(len(SCHEMA_CODES))):
        raise AssertionError("long_gclk schema code order mismatch")
    if any(row["shared_transition_key_flag"] != 0 for row in schema_rows):
        raise AssertionError("long_gclk shared transition key mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_gclk manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_gclk manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_gclk manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_glaw": LONG_GLAW,
        "long_glaw_law": LONG_GLAW_LAW,
        "long_f63": LONG_F63,
        "long_f63_atom": LONG_F63_ATOM,
        "long_rim": LONG_RIM,
        "long_rim_orbit": LONG_RIM_ORBIT,
        "long_transition_sem": LONG_TRANSITION_SEM,
        "long_transition_csv": LONG_TRANSITION_CSV,
        "long_contact_csv": LONG_CONTACT_CSV,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_gclk index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_gclk index report hash mismatch")

    return {
        "schema": "long.gclk.verification@2",
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
    print(json.dumps(validate_long_gclk(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
