from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search import (
        CELL_COMPLEX_EDGES,
        DERIVE_SCRIPT,
        FRONTIER_COLUMNS,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PARTIAL_SPLITTER_CERTIFICATE,
        PARTIAL_SPLITTER_FRONTIER,
        PARTIAL_SPLITTER_JSON,
        PARTIAL_SPLITTER_OBSERVABLES,
        PARTIAL_SPLITTER_PROFILES,
        PARTIAL_SPLITTER_REPORT,
        PARTIAL_SPLITTER_TABLES,
        PARTIAL_SPLITTER_TEMPLATES,
        PROFILE_COLUMNS,
        REWRITE_COMPLEX_EDGES,
        SHELL_COLUMNS,
        STATUS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search import (
        CELL_COMPLEX_EDGES,
        DERIVE_SCRIPT,
        FRONTIER_COLUMNS,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PARTIAL_SPLITTER_CERTIFICATE,
        PARTIAL_SPLITTER_FRONTIER,
        PARTIAL_SPLITTER_JSON,
        PARTIAL_SPLITTER_OBSERVABLES,
        PARTIAL_SPLITTER_PROFILES,
        PARTIAL_SPLITTER_REPORT,
        PARTIAL_SPLITTER_TABLES,
        PARTIAL_SPLITTER_TEMPLATES,
        PROFILE_COLUMNS,
        REWRITE_COMPLEX_EDGES,
        SHELL_COLUMNS,
        STATUS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )


EXPECTED_OBSERVABLES = {
    "neighborhood_total_word_count": 203866,
    "radius0_word_count": 2,
    "radius1_word_count": 185,
    "radius2_word_count": 7712,
    "radius3_word_count": 195967,
    "trace_valid_word_count": 139238,
    "metric_repair_candidate_count": 10792,
    "closed_positive_candidate_count": 219,
    "exact24_count": 14,
    "six_template_count": 37,
    "exact24_six_template_count": 0,
    "exact24_six_all_four_count": 0,
    "all_four_ge24_count": 13,
    "best_all_four_ge24_count": 8,
    "best_all_four_ge24_closure_excess": 4,
    "best_all_four_ge24_template_count": 7,
    "best_six_template_count": 3,
    "best_six_template_closure_excess": 8,
    "best_six_template_min_variation": 215,
    "best_six_template_template_lift_min": 4,
    "best_six_template_template_lift_max": 8,
}


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


def table_rows(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    trim = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search_certificate.json"
    )
    shells_csv = (
        OUT_DIR / "aperture_closure_tail_trim_neighborhood_shells.csv"
    ).read_text(encoding="utf-8")
    frontier_csv = (
        OUT_DIR / "aperture_closure_tail_trim_neighborhood_frontier.csv"
    ).read_text(encoding="utf-8")
    profiles_csv = (
        OUT_DIR / "aperture_closure_tail_trim_neighborhood_profiles.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR / "aperture_closure_tail_trim_neighborhood_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        trim
        != expected[
            "signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search"
        ]
    ):
        raise AssertionError("trim-neighborhood JSON is not reproducible")
    if shells_csv != expected["aperture_closure_tail_trim_neighborhood_shells_csv"]:
        raise AssertionError("trim-neighborhood shells CSV is not reproducible")
    if frontier_csv != expected["aperture_closure_tail_trim_neighborhood_frontier_csv"]:
        raise AssertionError("trim-neighborhood frontier CSV is not reproducible")
    if profiles_csv != expected["aperture_closure_tail_trim_neighborhood_profiles_csv"]:
        raise AssertionError("trim-neighborhood profiles CSV is not reproducible")
    if observables_csv != expected["aperture_closure_tail_trim_neighborhood_observables_csv"]:
        raise AssertionError("trim-neighborhood observables CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search_certificate"
        ]
    ):
        raise AssertionError("trim-neighborhood certificate is not reproducible")

    for name in [
        "shell_table",
        "frontier_table",
        "profile_table",
        "observable_table",
    ]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"trim-neighborhood table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search@1":
        raise AssertionError("trim-neighborhood report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("trim-neighborhood layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("trim-neighborhood all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("trim-neighborhood checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("trim-neighborhood report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("trim-neighborhood report is not reproducible")

    shell_table = np.asarray(tables["shell_table"], dtype=np.int64)
    frontier_table = np.asarray(tables["frontier_table"], dtype=np.int64)
    profile_table = np.asarray(tables["profile_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if shell_table.shape != (4, len(SHELL_COLUMNS)):
        raise AssertionError("trim-neighborhood shell table shape mismatch")
    if frontier_table.shape != (219, len(FRONTIER_COLUMNS)):
        raise AssertionError("trim-neighborhood frontier table shape mismatch")
    if profile_table.shape != (25, len(PROFILE_COLUMNS)):
        raise AssertionError("trim-neighborhood profile table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("trim-neighborhood observable table shape mismatch")

    observable_rows = table_rows(observable_table, OBSERVABLE_COLUMNS)
    observables = {
        row["observable_code"]: row["value_x1e12"] // 10**12
        for row in observable_rows
    }
    expected_observables = {
        OBSERVABLE_CODES[key]: value for key, value in EXPECTED_OBSERVABLES.items()
    }
    if observables != expected_observables:
        raise AssertionError("trim-neighborhood observables mismatch")

    frontier_rows = table_rows(frontier_table, FRONTIER_COLUMNS)
    if sum(row["exact24_six_all_four_flag"] for row in frontier_rows) != 0:
        raise AssertionError("trim-neighborhood found forbidden trim target")
    if sum(row["exact24_six_template_flag"] for row in frontier_rows) != 0:
        raise AssertionError("trim-neighborhood found exact24 six-template target")
    if sum(row["best_all_four_ge24_flag"] for row in frontier_rows) != 8:
        raise AssertionError("trim-neighborhood best all-four count mismatch")
    if any(
        (
            row["first_return_closed_path_count"],
            row["normalized_tail_template_count"],
            row["template_lift_count_min"],
            row["template_lift_count_max"],
        )
        != (28, 7, 4, 4)
        for row in frontier_rows
        if row["best_all_four_ge24_flag"] == 1
    ):
        raise AssertionError("trim-neighborhood best all-four profile mismatch")
    if sum(row["best_six_template_gap_flag"] for row in frontier_rows) != 3:
        raise AssertionError("trim-neighborhood best six-template gap count mismatch")
    if any(
        row["first_return_closed_path_count"] != 32
        for row in frontier_rows
        if row["best_six_template_gap_flag"] == 1
    ):
        raise AssertionError("trim-neighborhood best six-template closure mismatch")

    witness = report.get("witness", {})
    if witness.get("neighborhood_shell_counts") != [2, 185, 7712, 195967]:
        raise AssertionError("trim-neighborhood shell-count witness mismatch")
    if witness.get("closed_positive_candidate_count") != 219:
        raise AssertionError("trim-neighborhood closed-positive witness mismatch")
    if witness.get("exact24_six_template_count") != 0:
        raise AssertionError("trim-neighborhood exact24 six witness mismatch")
    if witness.get("exact24_six_all_four_count") != 0:
        raise AssertionError("trim-neighborhood exact24 six all-four witness mismatch")
    if witness.get("best_six_template_closure_excess") != 8:
        raise AssertionError("trim-neighborhood best six witness mismatch")
    if certificate.get("status") != STATUS:
        raise AssertionError("trim-neighborhood certificate status mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("partial_splitter_report", {}), PARTIAL_SPLITTER_REPORT, "partial splitter report input")
    assert_file_hash(inputs.get("partial_splitter_json", {}), PARTIAL_SPLITTER_JSON, "partial splitter JSON input")
    assert_file_hash(inputs.get("partial_splitter_frontier", {}), PARTIAL_SPLITTER_FRONTIER, "partial splitter frontier input")
    assert_file_hash(inputs.get("partial_splitter_profiles", {}), PARTIAL_SPLITTER_PROFILES, "partial splitter profiles input")
    assert_file_hash(inputs.get("partial_splitter_templates", {}), PARTIAL_SPLITTER_TEMPLATES, "partial splitter templates input")
    assert_file_hash(inputs.get("partial_splitter_observables", {}), PARTIAL_SPLITTER_OBSERVABLES, "partial splitter observables input")
    assert_file_hash(inputs.get("partial_splitter_tables", {}), PARTIAL_SPLITTER_TABLES, "partial splitter tables input")
    assert_file_hash(inputs.get("partial_splitter_certificate", {}), PARTIAL_SPLITTER_CERTIFICATE, "partial splitter certificate input")
    assert_file_hash(inputs.get("symbolic_alphabet", {}), SYMBOLIC_ALPHABET_CSV, "symbolic alphabet input")
    assert_file_hash(inputs.get("symbolic_associativity", {}), SYMBOLIC_ASSOCIATIVITY_CSV, "symbolic associativity input")
    assert_file_hash(inputs.get("rewrite_complex_edges", {}), REWRITE_COMPLEX_EDGES, "rewrite complex edges input")
    assert_file_hash(inputs.get("cell_complex_edges", {}), CELL_COMPLEX_EDGES, "cell complex edges input")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script input")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator input")

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search_manifest@1":
        raise AssertionError("trim-neighborhood manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("trim-neighborhood manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("trim-neighborhood manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("trim-neighborhood missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("trim-neighborhood index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("trim-neighborhood index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": witness,
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
