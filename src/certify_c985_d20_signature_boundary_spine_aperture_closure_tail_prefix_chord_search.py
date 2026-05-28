from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_prefix_chord_search import (
        BASELINE_DELTA_TWICE,
        CHORD_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        RANK104_BRIDGE_VARIATION,
        RANK104_CLOSURE_PATH_COUNT,
        RANK104_PRE_CHORD_DELTA_TWICE,
        RANK104_TRACE,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_NODES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        REWRITE_LIFT_CANDIDATES,
        REWRITE_LIFT_CERTIFICATE,
        REWRITE_LIFT_JSON,
        REWRITE_LIFT_REPORT,
        REWRITE_LIFT_TABLES,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_prefix_chord_search import (
        BASELINE_DELTA_TWICE,
        CHORD_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        RANK104_BRIDGE_VARIATION,
        RANK104_CLOSURE_PATH_COUNT,
        RANK104_PRE_CHORD_DELTA_TWICE,
        RANK104_TRACE,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_NODES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        REWRITE_LIFT_CANDIDATES,
        REWRITE_LIFT_CERTIFICATE,
        REWRITE_LIFT_JSON,
        REWRITE_LIFT_REPORT,
        REWRITE_LIFT_TABLES,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )


EXPECTED_CHORD_ROWS = [
    (0, 42, 45, 42, 45, 183, 148, 35, 1, 0, 0, 2, 105, 72, 1, 24, 22, 0),
    (1, 27, 29, 27, 29, 146, 169, 23, 1, 0, 0, 2, 114, 79, 1, 24, 22, 0),
    (2, 44, 54, 44, 54, 185, 134, 51, 1, 0, 0, 2, 114, 87, 1, 24, 22, 0),
    (3, 28, 31, 28, 31, 169, 151, 18, 1, 0, 0, 2, 117, 71, 1, 24, 22, 1),
    (4, 34, 50, 34, 50, 177, 146, 31, 1, 0, 0, 2, 117, 77, 1, 24, 22, 1),
    (5, 27, 28, 27, 28, 146, 169, 23, 1, 0, 0, 3, 1, 1, 0, 24, 22, 0),
    (6, 29, 42, 29, 42, 169, 183, 14, 1, 0, 0, 3, 1, 1, 0, 24, 22, 0),
    (7, 34, 54, 34, 54, 177, 134, 43, 1, 0, 0, 3, 1, 1, 0, 24, 22, 0),
    (8, 44, 50, 44, 50, 185, 146, 39, 1, 0, 0, 3, 1, 0, 0, 24, 22, 0),
    (9, 31, 34, 31, 34, 151, 177, 26, 1, 0, 0, 3, 2, 2, 0, 24, 22, 0),
    (10, 44, 45, 44, 45, 185, 148, 37, 1, 0, 0, 3, 2, 2, 0, 24, 22, 0),
    (11, 28, 44, 28, 44, 169, 185, 16, 1, 0, 0, 4, 1, 1, 0, 24, 22, 0),
    (12, 29, 34, 29, 34, 169, 177, 8, 1, 0, 0, 4, 2, 2, 0, 24, 22, 0),
    (13, 48, 50, 48, 50, 132, 146, 14, 1, 0, 0, 4, 2, 1, 0, 24, 22, 0),
    (14, 42, 50, 42, 50, 183, 146, 37, 1, 0, 0, 4, 5, 2, 0, 24, 22, 0),
    (15, 29, 44, 29, 44, 169, 185, 16, 1, 0, 0, 4, 6, 6, 0, 24, 22, 0),
]
EXPECTED_OBSERVABLES = {
    "pre_chord_delta_twice": 4,
    "target_delta_twice": 2,
    "single_existing_chord_candidate_count": 16,
    "delta_repair_candidate_count": 5,
    "prefix_to_baseline_repair_candidate_count": 2,
    "closure_path_count_retained": 24,
    "bridge_variation_retained": 22,
    "repair_signature_variation_min": 18,
    "prefix_to_baseline_repair_signature_variation_min": 18,
    "pre_chord_prefix_tail_best_delta_witness_count": 18,
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


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_prefix_chord_search() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    chord_search = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_prefix_chord_search.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_prefix_chord_search_certificate.json"
    )
    chord_csv = (
        OUT_DIR / "aperture_closure_tail_prefix_chord_candidates.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR / "aperture_closure_tail_prefix_chord_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_prefix_chord_search_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        chord_search
        != expected[
            "signature_boundary_spine_aperture_closure_tail_prefix_chord_search"
        ]
    ):
        raise AssertionError("prefix-chord search JSON is not reproducible")
    if chord_csv != expected["aperture_closure_tail_prefix_chord_candidates_csv"]:
        raise AssertionError("prefix-chord candidate CSV is not reproducible")
    if observables_csv != expected["aperture_closure_tail_prefix_chord_observables_csv"]:
        raise AssertionError("prefix-chord observables CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_closure_tail_prefix_chord_search_certificate"
        ]
    ):
        raise AssertionError("prefix-chord certificate is not reproducible")

    for name in ["chord_table", "observable_table"]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"prefix-chord table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_prefix_chord_search@1":
        raise AssertionError("prefix-chord report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("prefix-chord layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("prefix-chord all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("prefix-chord checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("prefix-chord report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("prefix-chord report is not reproducible")

    missing = sorted(
        key
        for key in expected["report"]["checks"]
        if report.get("checks", {}).get(key) is not True
    )
    if missing:
        raise AssertionError(f"prefix-chord missing true checks: {missing}")

    chord_table = np.asarray(tables["chord_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if chord_table.shape != (16, len(CHORD_COLUMNS)):
        raise AssertionError("prefix-chord table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("prefix-chord observable table shape mismatch")

    chord_rows = table_rows(chord_table, CHORD_COLUMNS)
    observable_rows = table_rows(observable_table, OBSERVABLE_COLUMNS)
    if [row_tuple(row, CHORD_COLUMNS) for row in chord_rows] != EXPECTED_CHORD_ROWS:
        raise AssertionError("prefix-chord rows mismatch")
    repair_rows = [
        row for row in chord_rows if row["delta_penalty_removed_flag"] == 1
    ]
    if [
        (row["undirected_left_node_id"], row["undirected_right_node_id"])
        for row in repair_rows
    ] != [(42, 45), (27, 29), (44, 54), (28, 31), (34, 50)]:
        raise AssertionError("prefix-chord repair set mismatch")
    if [
        (row["undirected_left_node_id"], row["undirected_right_node_id"])
        for row in repair_rows
        if row["prefix_to_baseline_shortcut_flag"] == 1
    ] != [(28, 31), (34, 50)]:
        raise AssertionError("prefix-chord bridge-to-baseline set mismatch")
    if any(row["post_chord_delta_twice"] != BASELINE_DELTA_TWICE for row in repair_rows):
        raise AssertionError("prefix-chord repair delta mismatch")
    if any(
        row["closure_path_count_retained"] != RANK104_CLOSURE_PATH_COUNT
        or row["bridge_variation_retained"] != RANK104_BRIDGE_VARIATION
        for row in repair_rows
    ):
        raise AssertionError("prefix-chord retained closure/variation mismatch")
    if min(row["signature_variation"] for row in repair_rows) != 18:
        raise AssertionError("prefix-chord repair variation minimum mismatch")

    observables = {
        row["observable_code"]: row["value_x1e12"] // 10**12
        for row in observable_rows
    }
    expected_observables = {
        OBSERVABLE_CODES[key]: value for key, value in EXPECTED_OBSERVABLES.items()
    }
    if observables != expected_observables:
        raise AssertionError("prefix-chord observables mismatch")

    witness = report.get("witness", {})
    if witness.get("rank104_trace") != list(RANK104_TRACE):
        raise AssertionError("prefix-chord witness trace mismatch")
    if witness.get("pre_chord_delta_twice") != RANK104_PRE_CHORD_DELTA_TWICE:
        raise AssertionError("prefix-chord witness pre-delta mismatch")
    if witness.get("pre_chord_prefix_tail_best_delta_witness_count") != 18:
        raise AssertionError("prefix-chord witness prefix-tail mismatch")
    if witness.get("repair_chords") != [
        [42, 45],
        [27, 29],
        [44, 54],
        [28, 31],
        [34, 50],
    ]:
        raise AssertionError("prefix-chord witness repair chords mismatch")
    if witness.get("prefix_to_baseline_repair_chords") != [[28, 31], [34, 50]]:
        raise AssertionError("prefix-chord witness shortcut chords mismatch")
    if chord_search.get("summary", {}).get("delta_repair_candidate_count") != 5:
        raise AssertionError("prefix-chord summary repair count mismatch")
    if certificate.get("status") != STATUS:
        raise AssertionError("prefix-chord certificate status mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("rewrite_lift_report", {}), REWRITE_LIFT_REPORT, "rewrite lift report input")
    assert_file_hash(inputs.get("rewrite_lift_json", {}), REWRITE_LIFT_JSON, "rewrite lift JSON input")
    assert_file_hash(inputs.get("rewrite_lift_delta_witnesses", {}), REWRITE_LIFT_CANDIDATES, "rewrite lift delta witnesses input")
    assert_file_hash(inputs.get("rewrite_lift_tables", {}), REWRITE_LIFT_TABLES, "rewrite lift tables input")
    assert_file_hash(inputs.get("rewrite_lift_certificate", {}), REWRITE_LIFT_CERTIFICATE, "rewrite lift certificate input")
    assert_file_hash(inputs.get("rewrite_complex_report", {}), REWRITE_COMPLEX_REPORT, "rewrite complex report input")
    assert_file_hash(inputs.get("rewrite_complex_nodes", {}), REWRITE_COMPLEX_NODES, "rewrite complex nodes input")
    assert_file_hash(inputs.get("rewrite_complex_edges", {}), REWRITE_COMPLEX_EDGES, "rewrite complex edges input")
    assert_file_hash(inputs.get("rewrite_complex_tables", {}), REWRITE_COMPLEX_TABLES, "rewrite complex tables input")
    assert_file_hash(inputs.get("rewrite_complex_certificate", {}), REWRITE_COMPLEX_CERTIFICATE, "rewrite complex certificate input")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script input")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator input")

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_prefix_chord_search_manifest@1":
        raise AssertionError("prefix-chord manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("prefix-chord manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("prefix-chord manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("prefix-chord missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("prefix-chord index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("prefix-chord index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_prefix_chord_search@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": witness,
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_prefix_chord_search()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
