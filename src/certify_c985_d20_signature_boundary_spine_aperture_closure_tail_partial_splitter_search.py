from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_partial_splitter_search import (
        CELL_COMPLEX_EDGES,
        DERIVE_SCRIPT,
        FRONTIER_COLUMNS,
        INDEX_PATH,
        LOWER_LIFT_CERTIFICATE,
        LOWER_LIFT_EDGES,
        LOWER_LIFT_JSON,
        LOWER_LIFT_OBSERVABLES,
        LOWER_LIFT_PROFILES,
        LOWER_LIFT_REPORT,
        LOWER_LIFT_TABLES,
        LOWER_LIFT_TEMPLATES,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PROFILE_COLUMNS,
        REWRITE_COMPLEX_EDGES,
        STATUS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        TEMPLATE_COLUMNS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_partial_splitter_search import (
        CELL_COMPLEX_EDGES,
        DERIVE_SCRIPT,
        FRONTIER_COLUMNS,
        INDEX_PATH,
        LOWER_LIFT_CERTIFICATE,
        LOWER_LIFT_EDGES,
        LOWER_LIFT_JSON,
        LOWER_LIFT_OBSERVABLES,
        LOWER_LIFT_PROFILES,
        LOWER_LIFT_REPORT,
        LOWER_LIFT_TABLES,
        LOWER_LIFT_TEMPLATES,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PROFILE_COLUMNS,
        REWRITE_COMPLEX_EDGES,
        STATUS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        TEMPLATE_COLUMNS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )


EXPECTED_FRONTIER_ROWS = [
    (0, 12, 7, 7, 2, 137, 12, 12, 3, 4, 4, 3, 1, 1, 0, 0, 0, 0, 0, 0, 0, 12, 0, 1, 1, 0),
    (1, 11, 6, 11, 2, 169, 16, 8, 3, 4, 8, 2, 1, 0, 0, 0, 0, 0, 0, 8, 8, 0, 1, 0, 0, 0),
    (2, 12, 7, 11, 2, 169, 92, 68, 9, 4, 12, 1, 1, 0, 0, 0, 0, 0, 36, 4, 16, 36, 1, 0, 0, 0),
    (3, 13, 8, 13, 2, 169, 16, 8, 3, 4, 8, 2, 1, 0, 0, 0, 0, 0, 0, 8, 8, 0, 1, 0, 0, 0),
    (4, 10, 5, 10, 2, 175, 8, 16, 2, 4, 4, 2, 1, 1, 0, 0, 0, 0, 0, 0, 8, 0, 1, 0, 0, 0),
    (5, 13, 8, 10, 2, 175, 8, 16, 2, 4, 4, 2, 1, 1, 0, 0, 0, 0, 0, 0, 8, 0, 1, 0, 0, 0),
    (6, 13, 8, 11, 2, 175, 8, 16, 2, 4, 4, 2, 1, 1, 0, 0, 0, 0, 0, 0, 8, 0, 1, 0, 0, 0),
    (7, 13, 8, 11, 2, 179, 8, 16, 2, 4, 4, 2, 1, 1, 0, 0, 0, 0, 0, 0, 8, 0, 1, 0, 0, 0),
    (8, 12, 7, 12, 2, 195, 12, 12, 3, 4, 4, 3, 1, 1, 0, 0, 0, 0, 0, 4, 8, 0, 0, 1, 1, 0),
    (9, 13, 8, 12, 2, 195, 60, 36, 9, 4, 8, 3, 1, 0, 0, 0, 0, 0, 24, 4, 8, 24, 0, 1, 1, 0),
    (10, 12, 7, 11, 2, 197, 24, 0, 2, 12, 12, 0, 0, 0, 1, 0, 0, 0, 0, 0, 24, 0, 0, 1, 1, 0),
    (11, 13, 8, 13, 2, 197, 84, 60, 7, 12, 12, 0, 0, 0, 0, 0, 0, 0, 36, 12, 0, 36, 0, 1, 1, 0),
    (12, 13, 8, 10, 2, 199, 24, 0, 3, 8, 8, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 24, 0, 1, 1, 0),
    (13, 11, 6, 12, 2, 201, 4, 20, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 1, 0, 0),
    (14, 11, 6, 12, 2, 215, 16, 8, 3, 4, 8, 2, 1, 0, 0, 0, 0, 0, 0, 8, 8, 0, 1, 0, 0, 0),
    (15, 12, 7, 12, 2, 215, 92, 68, 9, 4, 12, 1, 1, 0, 0, 0, 0, 0, 36, 4, 16, 36, 1, 0, 0, 0),
    (16, 13, 8, 14, 2, 215, 16, 8, 3, 4, 8, 2, 1, 0, 0, 0, 0, 0, 0, 8, 8, 0, 1, 0, 0, 0),
    (17, 12, 7, 13, 2, 217, 8, 16, 2, 4, 4, 2, 1, 1, 0, 0, 0, 0, 0, 0, 8, 0, 1, 0, 0, 0),
    (18, 13, 8, 12, 2, 217, 28, 4, 3, 8, 12, 0, 0, 0, 0, 0, 0, 0, 0, 12, 16, 0, 1, 0, 0, 0),
    (19, 13, 8, 12, 2, 217, 28, 4, 7, 4, 4, 7, 1, 1, 0, 0, 1, 1, 12, 4, 0, 12, 1, 0, 0, 0),
    (20, 11, 6, 12, 2, 219, 28, 4, 7, 4, 4, 7, 1, 1, 0, 0, 1, 1, 12, 4, 0, 12, 1, 0, 0, 0),
    (21, 13, 8, 13, 2, 219, 28, 4, 3, 8, 12, 0, 0, 0, 0, 0, 0, 0, 0, 12, 16, 0, 1, 0, 0, 0),
]

EXPECTED_TEMPLATE_ROWS = [
    (19, 0, 9, 4, 1, 9, 10, 3, 8, 13, 12, 34, 12, 11, 33, 43, 19, 7, 4, 12, 19),
    (19, 1, 9, 4, 1, 9, 10, 11, 8, 13, 12, 34, 38, 31, 33, 43, 19, 7, 4, 12, 19),
    (19, 2, 9, 4, 1, 9, 11, 3, 8, 13, 12, 35, 13, 11, 33, 43, 19, 7, 4, 12, 19),
    (19, 3, 10, 4, 1, 10, 11, 3, 8, 13, 12, 38, 13, 11, 33, 43, 19, 7, 4, 12, 19),
    (19, 4, 13, 4, 0, 13, 10, 3, 8, 13, 12, 40, 12, 11, 33, 43, 19, 7, 4, 12, 19),
    (19, 5, 13, 4, 0, 13, 10, 11, 8, 13, 12, 40, 38, 31, 33, 43, 19, 7, 4, 12, 19),
    (19, 6, 13, 4, 0, 13, 11, 3, 8, 13, 12, 42, 13, 11, 33, 43, 19, 7, 4, 12, 19),
    (20, 0, 9, 4, 1, 9, 10, 3, 8, 13, 12, 34, 12, 11, 33, 43, 19, 7, 4, 12, 19),
    (20, 1, 9, 4, 1, 9, 10, 11, 8, 13, 12, 34, 38, 31, 33, 43, 19, 7, 4, 12, 19),
    (20, 2, 9, 4, 1, 9, 11, 3, 8, 13, 12, 35, 13, 11, 33, 43, 19, 7, 4, 12, 19),
    (20, 3, 10, 4, 1, 10, 11, 3, 8, 13, 12, 38, 13, 11, 33, 43, 19, 7, 4, 12, 19),
    (20, 4, 13, 4, 0, 13, 10, 3, 8, 13, 12, 40, 12, 11, 33, 43, 19, 7, 4, 12, 19),
    (20, 5, 13, 4, 0, 13, 10, 11, 8, 13, 12, 40, 38, 31, 33, 43, 19, 7, 4, 12, 19),
    (20, 6, 13, 4, 0, 13, 11, 3, 8, 13, 12, 42, 13, 11, 33, 43, 19, 7, 4, 12, 19),
]

EXPECTED_OBSERVABLES = {
    "sub223_delta2_closed_positive_count": 22,
    "sub223_exact24_count": 2,
    "sub223_exact24_any_four_lift_count": 0,
    "sub223_exact24_partial_splitter_count": 0,
    "sub223_any_four_lift_count": 16,
    "sub223_all_four_lift_count": 9,
    "sub223_all_four_ge24_count": 2,
    "best_oversplitter_count": 2,
    "best_oversplitter_min_variation": 217,
    "best_oversplitter_max_variation": 219,
    "best_oversplitter_closed_path_count": 28,
    "best_oversplitter_template_count": 7,
    "best_oversplitter_closure_excess": 4,
    "best_oversplitter_endpoint_9_count": 12,
    "best_oversplitter_endpoint_10_count": 4,
    "best_oversplitter_endpoint_11_count": 0,
    "best_oversplitter_endpoint_13_count": 12,
    "selected_six_template_variation": 223,
    "selected_six_template_closed_paths": 24,
    "selected_six_template_template_count": 6,
    "selected_gap_over_best_oversplitter_min": 4,
    "selected_gap_over_best_oversplitter_max": 6,
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


def row_tuple(row: dict[str, int], columns: list[str]) -> tuple[int, ...]:
    return tuple(row[column] for column in columns)


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_partial_splitter_search() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    splitter = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_partial_splitter_search.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_partial_splitter_search_certificate.json"
    )
    frontier_csv = (
        OUT_DIR / "aperture_closure_tail_partial_splitter_frontier.csv"
    ).read_text(encoding="utf-8")
    profiles_csv = (
        OUT_DIR / "aperture_closure_tail_partial_splitter_profiles.csv"
    ).read_text(encoding="utf-8")
    templates_csv = (
        OUT_DIR / "aperture_closure_tail_partial_splitter_templates.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR / "aperture_closure_tail_partial_splitter_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_partial_splitter_search_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        splitter
        != expected[
            "signature_boundary_spine_aperture_closure_tail_partial_splitter_search"
        ]
    ):
        raise AssertionError("partial-splitter JSON is not reproducible")
    if frontier_csv != expected["aperture_closure_tail_partial_splitter_frontier_csv"]:
        raise AssertionError("partial-splitter frontier CSV is not reproducible")
    if profiles_csv != expected["aperture_closure_tail_partial_splitter_profiles_csv"]:
        raise AssertionError("partial-splitter profiles CSV is not reproducible")
    if templates_csv != expected["aperture_closure_tail_partial_splitter_templates_csv"]:
        raise AssertionError("partial-splitter templates CSV is not reproducible")
    if observables_csv != expected["aperture_closure_tail_partial_splitter_observables_csv"]:
        raise AssertionError("partial-splitter observables CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_closure_tail_partial_splitter_search_certificate"
        ]
    ):
        raise AssertionError("partial-splitter certificate is not reproducible")

    for name in [
        "frontier_table",
        "profile_table",
        "template_table",
        "observable_table",
    ]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"partial-splitter table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_partial_splitter_search@1":
        raise AssertionError("partial-splitter report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("partial-splitter layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("partial-splitter all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("partial-splitter checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("partial-splitter report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("partial-splitter report is not reproducible")

    frontier_table = np.asarray(tables["frontier_table"], dtype=np.int64)
    profile_table = np.asarray(tables["profile_table"], dtype=np.int64)
    template_table = np.asarray(tables["template_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if frontier_table.shape != (22, len(FRONTIER_COLUMNS)):
        raise AssertionError("partial-splitter frontier table shape mismatch")
    if profile_table.shape != (5, len(PROFILE_COLUMNS)):
        raise AssertionError("partial-splitter profile table shape mismatch")
    if template_table.shape != (14, len(TEMPLATE_COLUMNS)):
        raise AssertionError("partial-splitter template table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("partial-splitter observable table shape mismatch")

    frontier_rows = table_rows(frontier_table, FRONTIER_COLUMNS)
    template_rows = table_rows(template_table, TEMPLATE_COLUMNS)
    observable_rows = table_rows(observable_table, OBSERVABLE_COLUMNS)
    if [row_tuple(row, FRONTIER_COLUMNS) for row in frontier_rows] != EXPECTED_FRONTIER_ROWS:
        raise AssertionError("partial-splitter frontier rows mismatch")
    if [row_tuple(row, TEMPLATE_COLUMNS) for row in template_rows] != EXPECTED_TEMPLATE_ROWS:
        raise AssertionError("partial-splitter template rows mismatch")
    observables = {
        row["observable_code"]: row["value_x1e12"] // 10**12
        for row in observable_rows
    }
    expected_observables = {
        OBSERVABLE_CODES[key]: value for key, value in EXPECTED_OBSERVABLES.items()
    }
    if observables != expected_observables:
        raise AssertionError("partial-splitter observables mismatch")

    exact24_ids = [row["partial_candidate_id"] for row in frontier_rows if row["exact_24_flag"] == 1]
    if exact24_ids != [10, 12]:
        raise AssertionError("partial-splitter exact-24 ids mismatch")
    if any(row["exact_24_any_four_lift_flag"] for row in frontier_rows):
        raise AssertionError("partial-splitter exact-24 row has four-lift template")
    oversplitter_ids = [
        row["partial_candidate_id"]
        for row in frontier_rows
        if row["best_oversplitter_flag"] == 1
    ]
    if oversplitter_ids != [19, 20]:
        raise AssertionError("partial-splitter oversplitter ids mismatch")
    if any(
        (
            row["first_return_closed_path_count"],
            row["normalized_tail_template_count"],
            row["four_lift_template_count"],
            row["tail_entry_9_path_count"],
            row["tail_entry_10_path_count"],
            row["tail_entry_11_path_count"],
            row["tail_entry_13_path_count"],
        )
        != (28, 7, 7, 12, 4, 0, 12)
        for row in frontier_rows
        if row["best_oversplitter_flag"] == 1
    ):
        raise AssertionError("partial-splitter oversplitter profile mismatch")
    for candidate_id in [19, 20]:
        rows = [row for row in template_rows if row["partial_candidate_id"] == candidate_id]
        if len(rows) != 7:
            raise AssertionError("partial-splitter oversplitter template count mismatch")
        if sum(row["rank104_template_match_flag"] for row in rows) != 4:
            raise AssertionError("partial-splitter rank104 template match mismatch")
        if sum(row["tail_entry_carrier_id"] == 13 for row in rows) != 3:
            raise AssertionError("partial-splitter endpoint13 template count mismatch")
        if any(row["splice_path_count"] != 4 for row in rows):
            raise AssertionError("partial-splitter non-four oversplitter template")

    witness = report.get("witness", {})
    if witness.get("sub223_exact24_candidate_ids") != [10, 12]:
        raise AssertionError("partial-splitter witness exact ids mismatch")
    if witness.get("sub223_exact24_partial_splitter_count") != 0:
        raise AssertionError("partial-splitter witness exact partial count mismatch")
    if witness.get("best_oversplitter_candidate_ids") != [19, 20]:
        raise AssertionError("partial-splitter witness oversplitter ids mismatch")
    if witness.get("best_oversplitter_variations") != [217, 219]:
        raise AssertionError("partial-splitter witness oversplitter variations mismatch")
    if certificate.get("status") != STATUS:
        raise AssertionError("partial-splitter certificate status mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("lower_lift_report", {}), LOWER_LIFT_REPORT, "lower lift report input")
    assert_file_hash(inputs.get("lower_lift_json", {}), LOWER_LIFT_JSON, "lower lift JSON input")
    assert_file_hash(inputs.get("lower_lift_profiles", {}), LOWER_LIFT_PROFILES, "lower lift profiles input")
    assert_file_hash(inputs.get("lower_lift_templates", {}), LOWER_LIFT_TEMPLATES, "lower lift templates input")
    assert_file_hash(inputs.get("lower_lift_edges", {}), LOWER_LIFT_EDGES, "lower lift edges input")
    assert_file_hash(inputs.get("lower_lift_observables", {}), LOWER_LIFT_OBSERVABLES, "lower lift observables input")
    assert_file_hash(inputs.get("lower_lift_tables", {}), LOWER_LIFT_TABLES, "lower lift tables input")
    assert_file_hash(inputs.get("lower_lift_certificate", {}), LOWER_LIFT_CERTIFICATE, "lower lift certificate input")
    assert_file_hash(inputs.get("symbolic_alphabet", {}), SYMBOLIC_ALPHABET_CSV, "symbolic alphabet input")
    assert_file_hash(inputs.get("symbolic_associativity", {}), SYMBOLIC_ASSOCIATIVITY_CSV, "symbolic associativity input")
    assert_file_hash(inputs.get("rewrite_complex_edges", {}), REWRITE_COMPLEX_EDGES, "rewrite complex edges input")
    assert_file_hash(inputs.get("cell_complex_edges", {}), CELL_COMPLEX_EDGES, "cell complex edges input")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script input")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator input")

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_partial_splitter_search_manifest@1":
        raise AssertionError("partial-splitter manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("partial-splitter manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("partial-splitter manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("partial-splitter missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("partial-splitter index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("partial-splitter index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_partial_splitter_search@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": witness,
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_aperture_closure_tail_partial_splitter_search()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
