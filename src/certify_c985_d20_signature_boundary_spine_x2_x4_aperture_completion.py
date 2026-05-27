from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_x2_x4_aperture_completion import (
        APERTURE_COMPLETION_PATH_COLUMNS,
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_JSON,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        CLEAN_DETOUR_CERTIFICATE,
        CLEAN_DETOUR_CHOICES,
        CLEAN_DETOUR_JSON,
        CLEAN_DETOUR_REPORT,
        CLEAN_DETOUR_TABLES,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        RESIDUAL_CHART_CARRIER_CSV,
        STATUS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        THEOREM_ID,
        TYPED_CORRIDOR_CERTIFICATE,
        TYPED_CORRIDOR_EDGES,
        TYPED_CORRIDOR_REPORT,
        TYPED_CORRIDOR_TABLES,
        X4_FIRST_EDGE_COLUMNS,
        build_payloads,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_x2_x4_aperture_completion import (
        APERTURE_COMPLETION_PATH_COLUMNS,
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_JSON,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        CLEAN_DETOUR_CERTIFICATE,
        CLEAN_DETOUR_CHOICES,
        CLEAN_DETOUR_JSON,
        CLEAN_DETOUR_REPORT,
        CLEAN_DETOUR_TABLES,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        RESIDUAL_CHART_CARRIER_CSV,
        STATUS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        THEOREM_ID,
        TYPED_CORRIDOR_CERTIFICATE,
        TYPED_CORRIDOR_EDGES,
        TYPED_CORRIDOR_REPORT,
        TYPED_CORRIDOR_TABLES,
        X4_FIRST_EDGE_COLUMNS,
        build_payloads,
        self_hash,
    )
    from derive_c985_typed_simple_object_registry import INDEX_PATH


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} is not a JSON object")
    return payload


def assert_file_hash(entry: dict[str, Any], expected_path: Path, label: str) -> None:
    expected_rel = expected_path.relative_to(ROOT).as_posix()
    if entry.get("path") != expected_rel:
        raise AssertionError(f"{label} path mismatch: {entry.get('path')} != {expected_rel}")
    if entry.get("sha256") != h_file(expected_path):
        raise AssertionError(f"{label} sha256 mismatch")


def validate_c985_d20_signature_boundary_spine_x2_x4_aperture_completion() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    completion = load_json(
        OUT_DIR / "signature_boundary_spine_x2_x4_aperture_completion.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_x2_x4_aperture_completion_certificate.json"
    )
    first_edges_csv = (OUT_DIR / "x2_x4_aperture_first_edges.csv").read_text(
        encoding="utf-8"
    )
    completion_paths_csv = (
        OUT_DIR / "x2_x4_aperture_completion_paths.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR / "x2_x4_aperture_completion_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR / "signature_boundary_spine_x2_x4_aperture_completion_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if completion != expected["signature_boundary_spine_x2_x4_aperture_completion"]:
        raise AssertionError("x2-x4 aperture completion JSON is not reproducible")
    if first_edges_csv != expected["x2_x4_aperture_first_edges_csv"]:
        raise AssertionError("x2-x4 aperture first-edge CSV is not reproducible")
    if completion_paths_csv != expected["x2_x4_aperture_completion_paths_csv"]:
        raise AssertionError("x2-x4 aperture path CSV is not reproducible")
    if observables_csv != expected["x2_x4_aperture_completion_observables_csv"]:
        raise AssertionError("x2-x4 aperture observable CSV is not reproducible")
    if (
        certificate
        != expected["signature_boundary_spine_x2_x4_aperture_completion_certificate"]
    ):
        raise AssertionError("x2-x4 aperture completion certificate is not reproducible")

    table_names = [
        "x4_first_edge_table",
        "aperture_completion_path_table",
        "observable_table",
    ]
    for name in table_names:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"x2-x4 aperture table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_x2_x4_aperture_completion@1":
        raise AssertionError("C985 d20 x2-x4 aperture report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 x2-x4 aperture completion is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 x2-x4 aperture all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 x2-x4 aperture checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 x2-x4 aperture report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 x2-x4 aperture report is not reproducible")

    checks = report.get("checks", {})
    missing = sorted(
        key for key in expected["report"]["checks"] if checks.get(key) is not True
    )
    if missing:
        raise AssertionError(f"C985 d20 x2-x4 aperture missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("selected_clean_return_path") != [14, 11]:
        raise AssertionError("x2-x4 aperture selected clean return mismatch")
    if witness.get("post_return_carrier_id") != 8:
        raise AssertionError("x2-x4 aperture post-return carrier mismatch")
    if witness.get("incident_x4_edge_ids") != [21, 24, 27, 33]:
        raise AssertionError("x2-x4 aperture incident x4 edges mismatch")
    if witness.get("direct_boundary_x4_edge_count") != 0:
        raise AssertionError("x2-x4 aperture direct x4 boundary count mismatch")
    if witness.get("two_step_boundary_return_count") != 8:
        raise AssertionError("x2-x4 aperture two-step path count mismatch")
    if witness.get("node44_completion_paths") != [[33, 40], [33, 42], [33, 43]]:
        raise AssertionError("x2-x4 aperture node44 completion paths mismatch")
    if witness.get("selected_origin_returning_completion") != [33, 43]:
        raise AssertionError("x2-x4 aperture selected origin return mismatch")
    if witness.get("selected_completion_positive_return_carrier_id") != 12:
        raise AssertionError("x2-x4 aperture selected positive carrier mismatch")
    if witness.get("aperture_word") != [2, 4, 5]:
        raise AssertionError("x2-x4 aperture word mismatch")
    if witness.get("aperture_canonical_triple_id") != 44:
        raise AssertionError("x2-x4 aperture canonical node mismatch")
    if witness.get("aperture_signature_union_count") != 185:
        raise AssertionError("x2-x4 aperture signature mismatch")
    if witness.get("completion_cycle") != {
        "carrier_ids": [12, 3, 8, 13, 12],
        "cell_edge_ids": [14, 11, 33, 43],
        "symbol_ids": [2, 1, 4, 5],
    }:
        raise AssertionError("x2-x4 aperture completion cycle mismatch")

    first_edge_table = np.asarray(tables["x4_first_edge_table"], dtype=np.int64)
    completion_path_table = np.asarray(
        tables["aperture_completion_path_table"], dtype=np.int64
    )
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)

    if first_edge_table.shape != (4, len(X4_FIRST_EDGE_COLUMNS)):
        raise AssertionError("x2-x4 aperture first-edge table shape mismatch")
    if completion_path_table.shape != (8, len(APERTURE_COMPLETION_PATH_COLUMNS)):
        raise AssertionError("x2-x4 aperture path table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("x2-x4 aperture observable table shape mismatch")
    if first_edge_table.tolist() != [
        [0, 21, 5, 8, 5, 2, 0, 4096, 16, 1, 1, 0, 0, 0],
        [1, 24, 6, 8, 6, 2, 0, 6144, 24, 2, 0, 1, 0, 1],
        [2, 27, 7, 8, 7, 2, 0, 6144, 24, 2, 0, 1, 0, 4],
        [3, 33, 8, 13, 13, 2, 0, 4096, 16, 1, 1, 0, 0, 3],
    ]:
        raise AssertionError("x2-x4 aperture first-edge table rows mismatch")
    if completion_path_table.tolist() != [
        [0, 24, 6, 25, 12, 6, 24, 2, 3, 8, 12, 5, 5, 2, 1, 0, 41, 6, 167, 0],
        [1, 27, 7, 1, 0, 7, 24, 2, 0, 1, 16, 0, 2, -2, 0, 0, 13, 6, 165, 0],
        [2, 27, 7, 10, 3, 7, 24, 2, 0, 1, 3, 2, 2, 11, 0, 0, 13, 6, 165, 0],
        [3, 27, 7, 28, 11, 7, 24, 2, 0, 1, 4, 6, 2, 10, 0, 0, 13, 6, 165, 0],
        [4, 27, 7, 29, 12, 7, 24, 2, 3, 8, 6, 7, 2, 8, 1, 0, 41, 6, 167, 0],
        [5, 33, 13, 40, 10, 13, 16, 1, 5, 32, 10, 13, 1, 4, 0, 1, 44, 6, 185, 0],
        [6, 33, 13, 42, 11, 13, 16, 1, 5, 32, 1, 14, 1, 13, 0, 1, 44, 6, 185, 0],
        [7, 33, 13, 43, 12, 13, 16, 1, 5, 32, 2, 15, 1, 12, 1, 1, 44, 6, 185, 1],
    ]:
        raise AssertionError("x2-x4 aperture path table rows mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("clean_detour_report", {}), CLEAN_DETOUR_REPORT, "clean detour report input")
    assert_file_hash(inputs.get("clean_detour_choice", {}), CLEAN_DETOUR_JSON, "clean detour JSON input")
    assert_file_hash(inputs.get("clean_detour_choices", {}), CLEAN_DETOUR_CHOICES, "clean detour choices input")
    assert_file_hash(inputs.get("clean_detour_tables", {}), CLEAN_DETOUR_TABLES, "clean detour table input")
    assert_file_hash(inputs.get("clean_detour_certificate", {}), CLEAN_DETOUR_CERTIFICATE, "clean detour certificate input")
    assert_file_hash(inputs.get("cell_complex_report", {}), CELL_COMPLEX_REPORT, "cell complex report input")
    assert_file_hash(inputs.get("cell_complex", {}), CELL_COMPLEX_JSON, "cell complex JSON input")
    assert_file_hash(inputs.get("cell_complex_edges", {}), CELL_COMPLEX_EDGES, "cell complex edge input")
    assert_file_hash(inputs.get("cell_complex_tables", {}), CELL_COMPLEX_TABLES, "cell complex table input")
    assert_file_hash(inputs.get("cell_complex_certificate", {}), CELL_COMPLEX_CERTIFICATE, "cell complex certificate input")
    assert_file_hash(inputs.get("typed_corridor_report", {}), TYPED_CORRIDOR_REPORT, "typed corridor report input")
    assert_file_hash(inputs.get("typed_corridor_edges", {}), TYPED_CORRIDOR_EDGES, "typed corridor edge input")
    assert_file_hash(inputs.get("typed_corridor_tables", {}), TYPED_CORRIDOR_TABLES, "typed corridor table input")
    assert_file_hash(inputs.get("typed_corridor_certificate", {}), TYPED_CORRIDOR_CERTIFICATE, "typed corridor certificate input")
    assert_file_hash(inputs.get("symbolic_associativity_report", {}), SYMBOLIC_ASSOCIATIVITY_REPORT, "symbolic associativity report input")
    assert_file_hash(inputs.get("symbolic_associativity_csv", {}), SYMBOLIC_ASSOCIATIVITY_CSV, "symbolic associativity CSV input")
    assert_file_hash(inputs.get("symbolic_associativity_tables", {}), SYMBOLIC_ASSOCIATIVITY_TABLES, "symbolic associativity table input")
    assert_file_hash(inputs.get("symbolic_associativity_certificate", {}), SYMBOLIC_ASSOCIATIVITY_CERTIFICATE, "symbolic associativity certificate input")
    assert_file_hash(inputs.get("residual_chart_carriers", {}), RESIDUAL_CHART_CARRIER_CSV, "residual chart carrier input")
    assert_file_hash(inputs.get("symbolic_alphabet", {}), SYMBOLIC_ALPHABET_CSV, "symbolic alphabet input")

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_x2_x4_aperture_completion_manifest@1":
        raise AssertionError("C985 d20 x2-x4 aperture manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 x2-x4 aperture manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 x2-x4 aperture manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("C985 d20 x2-x4 aperture missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 x2-x4 aperture index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 x2-x4 aperture index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_x2_x4_aperture_completion@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "direct_boundary_x4_edge_count": witness.get("direct_boundary_x4_edge_count"),
        "node44_completion_paths": witness.get("node44_completion_paths"),
        "selected_origin_returning_completion": witness.get(
            "selected_origin_returning_completion"
        ),
        "completion_cycle": witness.get("completion_cycle"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_x2_x4_aperture_completion()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
