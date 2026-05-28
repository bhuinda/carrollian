from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_graham_throat_screen import (
        DERIVE_SCRIPT,
        ETA6_REPORT,
        ETA6_TABLES,
        GRAPH_COLUMNS,
        H4_REPORT,
        H4_TABLES,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PAIR_COLUMNS,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        pair,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_graham_throat_screen import (
        DERIVE_SCRIPT,
        ETA6_REPORT,
        ETA6_TABLES,
        GRAPH_COLUMNS,
        H4_REPORT,
        H4_TABLES,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PAIR_COLUMNS,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        pair,
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


def table_rows(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_graham_throat_screen() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    graham = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_graham_throat_screen.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_graham_throat_screen_certificate.json"
    )
    ratio_csv = (OUT_DIR / "eta6_graham_throat_ratio_pairs.csv").read_text(
        encoding="utf-8"
    )
    graph_csv = (OUT_DIR / "eta6_graham_throat_graph_constraints.csv").read_text(
        encoding="utf-8"
    )
    observables_csv = (OUT_DIR / "eta6_graham_throat_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_graham_throat_screen_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if graham != expected["graham"]:
        raise AssertionError("eta6 Graham throat JSON is not reproducible")
    if ratio_csv != expected["ratio_csv"]:
        raise AssertionError("eta6 Graham throat ratio CSV is not reproducible")
    if graph_csv != expected["graph_csv"]:
        raise AssertionError("eta6 Graham throat graph CSV is not reproducible")
    if observables_csv != expected["observables_csv"]:
        raise AssertionError("eta6 Graham throat observables CSV is not reproducible")
    if certificate != expected["certificate"]:
        raise AssertionError("eta6 Graham throat certificate is not reproducible")

    for name in ["pair_table", "graph_table", "observable_table"]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"eta6 Graham throat table {name} mismatch")

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_graham_throat_screen@1"
    ):
        raise AssertionError("eta6 Graham throat report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6 Graham throat report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6 Graham throat all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6 Graham throat checks mismatch")
    if pair.parent.self_hash(report, "certificate_sha256") != report.get(
        "certificate_sha256"
    ):
        raise AssertionError("eta6 Graham throat report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6 Graham throat report hash is not reproducible")

    pair_table = np.asarray(tables["pair_table"], dtype=np.int64)
    graph_table = np.asarray(tables["graph_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(pair_table.shape) != (10, len(PAIR_COLUMNS)):
        raise AssertionError("eta6 Graham throat pair table shape mismatch")
    if tuple(graph_table.shape) != (1, len(GRAPH_COLUMNS)):
        raise AssertionError("eta6 Graham throat graph table shape mismatch")
    if tuple(observable_table.shape) != (
        len(OBSERVABLE_CODES),
        len(OBSERVABLE_COLUMNS),
    ):
        raise AssertionError("eta6 Graham throat observable table shape mismatch")

    pair_rows = table_rows(pair_table, PAIR_COLUMNS)
    graph_row = table_rows(graph_table, GRAPH_COLUMNS)[0]
    observables = {
        row["observable_code"]: row["value"]
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }
    closest = min(
        pair_rows,
        key=lambda row: (
            row["graham_ratio_abs_error_x1e12"],
            row["from_stage_id"],
            row["to_stage_id"],
        ),
    )
    if (
        closest["from_stage_id"],
        closest["to_stage_id"],
        closest["height_ratio_x1e12"],
        closest["graham_ratio_abs_error_x1e12"],
    ) != (2, 4, 1_013_227_671_291, 25_973_645_375):
        raise AssertionError("eta6 Graham throat closest ratio mismatch")
    if any(row["within_graham_tolerance_flag"] for row in pair_rows):
        raise AssertionError("eta6 Graham throat unexpectedly matched Graham ratio")
    if (
        graph_row["vertex_count"],
        graph_row["edge_count"],
        graph_row["min_degree"],
        graph_row["max_degree"],
        graph_row["cubic_flag"],
        graph_row["planar_flag"],
        graph_row["three_vertex_connected_flag"],
        graph_row["truncated_icosahedral_vertex_count_flag"],
        graph_row["truncated_icosahedral_edge_count_flag"],
    ) != (4, 6, 3, 3, 1, 1, 1, 0, 0):
        raise AssertionError("eta6 Graham throat graph constraint mismatch")

    required_observables = {
        "graham_area_x1e6": 674_981,
        "regular_area_x1e6": 649_519,
        "graham_ratio_x1e12": 1_039_201_316_666,
        "height_pair_count": 10,
        "closest_pair_from_stage_id": 2,
        "closest_pair_to_stage_id": 4,
        "closest_height_ratio_x1e12": 1_013_227_671_291,
        "closest_graham_error_x1e12": 25_973_645_375,
        "graham_ratio_match_count": 0,
        "support_fixed_flag": 1,
        "strict_height_descent_flag": 1,
        "k4_polyhedral_constraint_flag": 1,
        "truncated_icosahedral_match_flag": 0,
        "area_certificate_available_flag": 0,
    }
    for key, value in required_observables.items():
        if observables.get(OBSERVABLE_CODES[key]) != value:
            raise AssertionError(f"eta6 Graham throat observable {key} mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("h4_precursor_report", {}),
        H4_REPORT,
        "H4 precursor report input",
    )
    assert_file_hash(
        inputs.get("h4_precursor_tables", {}),
        H4_TABLES,
        "H4 precursor tables input",
    )
    assert_file_hash(
        inputs.get("eta6_support_report", {}),
        ETA6_REPORT,
        "eta6 support report input",
    )
    assert_file_hash(
        inputs.get("eta6_support_tables", {}),
        ETA6_TABLES,
        "eta6 support tables input",
    )
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if (
        manifest.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_graham_throat_screen_manifest@1"
    ):
        raise AssertionError("eta6 Graham throat manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6 Graham throat manifest report hash mismatch")
    if pair.parent.self_hash(manifest, "manifest_sha256") != manifest.get(
        "manifest_sha256"
    ):
        raise AssertionError("eta6 Graham throat manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6 Graham throat missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6 Graham throat index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6 Graham throat index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_eta6_graham_throat_screen@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_graham_throat_screen()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
