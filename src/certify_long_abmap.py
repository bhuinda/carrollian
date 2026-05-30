from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_abmap import (
        CSP_COLUMNS,
        DOMAIN_COLUMNS,
        EDGE_COLUMNS,
        INDEX_PATH,
        LONG_BINC,
        LONG_GCLK,
        LONG_GCLK_CLOCK,
        LONG_TLIFT,
        LONG_TRANSITION_CSV,
        LONG_TRANSITION_SEM,
        LOOP_INCIDENCE,
        LOOP_INCIDENCE_CSV,
        MATCH_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PRUNE_COLUMNS,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_abmap import (
        CSP_COLUMNS,
        DOMAIN_COLUMNS,
        EDGE_COLUMNS,
        INDEX_PATH,
        LONG_BINC,
        LONG_GCLK,
        LONG_GCLK_CLOCK,
        LONG_TLIFT,
        LONG_TRANSITION_CSV,
        LONG_TRANSITION_SEM,
        LOOP_INCIDENCE,
        LOOP_INCIDENCE_CSV,
        MATCH_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PRUNE_COLUMNS,
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


def validate_long_abmap() -> dict[str, Any]:
    expected = build_payloads()
    abmap = load_json(OUT_DIR / "abmap.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if abmap != expected["abmap"]:
        raise AssertionError("long_abmap JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_abmap cert mismatch")
    for filename, key in {
        "domain.csv": "domain_csv",
        "edge.csv": "edge_csv",
        "match.csv": "match_csv",
        "prune.csv": "prune_csv",
        "csp.csv": "csp_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_abmap {filename} mismatch")

    for key, expected_array in {
        "domain_table": expected["domain_table"],
        "edge_table": expected["edge_table"],
        "match_table": expected["match_table"],
        "prune_table": expected["prune_table"],
        "csp_table": expected["csp_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_abmap table mismatch: {key}")

    if report.get("schema") != "long.abmap.report@1":
        raise AssertionError("long_abmap report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_abmap report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_abmap all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_abmap checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_abmap report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_abmap report hash mismatch")

    csv_shapes = [
        ("domain.csv", DOMAIN_COLUMNS, 90),
        ("edge.csv", EDGE_COLUMNS, 40),
        ("match.csv", MATCH_COLUMNS, 83),
        ("prune.csv", PRUNE_COLUMNS, 6),
        ("csp.csv", CSP_COLUMNS, 2),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_abmap {filename} shape mismatch")

    table_shapes = {
        "domain_table": (90, len(DOMAIN_COLUMNS)),
        "edge_table": (40, len(EDGE_COLUMNS)),
        "match_table": (83, len(MATCH_COLUMNS)),
        "prune_table": (6, len(PRUNE_COLUMNS)),
        "csp_table": (2, len(CSP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_abmap {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 5,
        "input_certified_count": 5,
        "atom_count": 20,
        "loop_step_atom_count": 25,
        "domain_row_count": 90,
        "affine_tick_count": 20,
        "transition_row_count": 642,
        "directed_edge_covered_count": 15,
        "directed_candidate_pair_count": 24,
        "directed_functorial_map_exists_flag": 0,
        "directed_final_domain_count": 0,
        "undirected_edge_covered_count": 20,
        "undirected_candidate_pair_count": 59,
        "undirected_max_pair_multiplicity": 6,
        "undirected_relation_cover_flag": 1,
        "undirected_functorial_map_exists_flag": 0,
        "undirected_final_domain_count": 0,
        "atom_to_basis_function_certified_flag": 0,
        "semantic_transition_operation_flag": 0,
        "physical_selector_axiom_flag": 0,
        "gr_source_ready_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_abmap observable {key} mismatch")

    domain_rows = rows_from_table(np.asarray(tables["domain_table"]), DOMAIN_COLUMNS)
    if [row["domain_row_id"] for row in domain_rows] != list(range(90)):
        raise AssertionError("long_abmap domain ids mismatch")
    if any(row["candidate_basis_id"] != row["step_atom_id"] for row in domain_rows):
        raise AssertionError("long_abmap identity step-basis candidate mismatch")
    if any(row["identity_step_basis_flag"] != 1 for row in domain_rows):
        raise AssertionError("long_abmap identity flag mismatch")

    edge_rows = rows_from_table(np.asarray(tables["edge_table"]), EDGE_COLUMNS)
    directed_edges = [row for row in edge_rows if row["orientation_code"] == 0]
    undirected_edges = [row for row in edge_rows if row["orientation_code"] == 1]
    if sum(row["covered_flag"] for row in directed_edges) != 15:
        raise AssertionError("long_abmap directed cover count mismatch")
    if sum(row["covered_flag"] for row in undirected_edges) != 20:
        raise AssertionError("long_abmap undirected cover count mismatch")
    if sum(row["candidate_pair_count"] for row in directed_edges) != 24:
        raise AssertionError("long_abmap directed pair count mismatch")
    if sum(row["candidate_pair_count"] for row in undirected_edges) != 59:
        raise AssertionError("long_abmap undirected pair count mismatch")

    match_rows = rows_from_table(np.asarray(tables["match_table"]), MATCH_COLUMNS)
    if [row["match_id"] for row in match_rows] != list(range(83)):
        raise AssertionError("long_abmap match ids mismatch")
    if any(row["semantic_transition_flag"] != 0 for row in match_rows):
        raise AssertionError("long_abmap semantic transition match mismatch")

    prune_rows = rows_from_table(np.asarray(tables["prune_table"]), PRUNE_COLUMNS)
    expected_prune = [
        (0, 1, 89, 1, 19),
        (0, 2, 1, 0, 20),
        (0, 3, 0, 0, 20),
        (1, 1, 79, 11, 13),
        (1, 2, 11, 0, 20),
        (1, 3, 0, 0, 20),
    ]
    actual_prune = [
        (
            row["orientation_code"],
            row["iteration"],
            row["removed_domain_count"],
            row["remaining_domain_count"],
            row["empty_atom_count"],
        )
        for row in prune_rows
    ]
    if actual_prune != expected_prune:
        raise AssertionError("long_abmap prune trace mismatch")

    csp_rows = rows_from_table(np.asarray(tables["csp_table"]), CSP_COLUMNS)
    if [row["functorial_map_exists_flag"] for row in csp_rows] != [0, 0]:
        raise AssertionError("long_abmap functor marker mismatch")
    if [row["final_domain_count"] for row in csp_rows] != [0, 0]:
        raise AssertionError("long_abmap final domain mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_abmap manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_abmap manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_abmap manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_gclk": LONG_GCLK,
        "long_gclk_clock": LONG_GCLK_CLOCK,
        "long_tlift": LONG_TLIFT,
        "long_binc": LONG_BINC,
        "loop_incidence": LOOP_INCIDENCE,
        "loop_incidence_csv": LOOP_INCIDENCE_CSV,
        "long_transition_sem": LONG_TRANSITION_SEM,
        "long_transition_csv": LONG_TRANSITION_CSV,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_abmap index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_abmap index report hash mismatch")

    return {
        "schema": "long.abmap.verification@1",
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
    print(json.dumps(validate_long_abmap(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
