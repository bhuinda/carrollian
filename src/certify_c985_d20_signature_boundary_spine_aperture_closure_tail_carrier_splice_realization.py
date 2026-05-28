from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_realization import (
        CELL_COMPLEX_EDGES,
        DERIVE_SCRIPT,
        ENDPOINT_SPLIT_CERTIFICATE,
        ENDPOINT_SPLIT_REPORT,
        ENDPOINT_SPLIT_TEMPLATES,
        EXACT_WITNESS_COLUMNS,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PREFIX_CHORD_CANDIDATES,
        PREFIX_CHORD_CERTIFICATE,
        PREFIX_CHORD_JSON,
        PREFIX_CHORD_REPORT,
        PREFIX_CHORD_TABLES,
        SELECTED_SIX_TEMPLATE_TRACE,
        SELECTED_SIX_TEMPLATE_WORD,
        SELECTED_TEMPLATE_COLUMNS,
        STATUS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        TAIL_ATOM_COLUMNS,
        TAIL_CARRIER_COLUMNS,
        TAIL_EDGE_COLUMNS,
        THEOREM_ID,
        TRACE_NODE_COLUMNS,
        VALIDATOR_SCRIPT,
        WORD_COLUMNS,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_realization import (
        CELL_COMPLEX_EDGES,
        DERIVE_SCRIPT,
        ENDPOINT_SPLIT_CERTIFICATE,
        ENDPOINT_SPLIT_REPORT,
        ENDPOINT_SPLIT_TEMPLATES,
        EXACT_WITNESS_COLUMNS,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PREFIX_CHORD_CANDIDATES,
        PREFIX_CHORD_CERTIFICATE,
        PREFIX_CHORD_JSON,
        PREFIX_CHORD_REPORT,
        PREFIX_CHORD_TABLES,
        SELECTED_SIX_TEMPLATE_TRACE,
        SELECTED_SIX_TEMPLATE_WORD,
        SELECTED_TEMPLATE_COLUMNS,
        STATUS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        TAIL_ATOM_COLUMNS,
        TAIL_CARRIER_COLUMNS,
        TAIL_EDGE_COLUMNS,
        THEOREM_ID,
        TRACE_NODE_COLUMNS,
        VALIDATOR_SCRIPT,
        WORD_COLUMNS,
        build_payloads,
        self_hash,
    )


EXPECTED_TEMPLATE_CARRIERS = [
    (9, 10, 3, 8, 13, 12),
    (9, 10, 11, 8, 13, 12),
    (9, 11, 3, 8, 13, 12),
    (10, 11, 3, 8, 13, 12),
    (11, 10, 3, 8, 13, 12),
    (11, 10, 11, 8, 13, 12),
]
EXPECTED_TEMPLATE_EDGES = [
    (34, 12, 11, 33, 43),
    (34, 38, 31, 33, 43),
    (35, 13, 11, 33, 43),
    (38, 13, 11, 33, 43),
    (38, 12, 11, 33, 43),
    (38, 38, 31, 33, 43),
]
EXPECTED_TEMPLATE_ATOMS = [(19, 7, 4, 12, 19)] * 6
EXPECTED_OBSERVABLES = {
    "bounded_search_space_count": 19500,
    "trace_valid_count": 19500,
    "trace_contains_repair_chord_count": 1726,
    "trace_contains_31_28_count": 1094,
    "trace_contains_50_34_count": 652,
    "closed_positive_chord_count": 240,
    "exact_24_delta2_splice_count": 11,
    "exact_31_28_splice_count": 6,
    "exact_50_34_splice_count": 6,
    "exact_both_chords_splice_count": 1,
    "rank104_prefix_exact_count": 5,
    "shared_rewrite_tail_exact_count": 1,
    "six_template_retention_exact_count": 1,
    "selected_six_template_word_length": 13,
    "selected_six_template_variation": 223,
    "selected_six_template_full_path_count": 240,
    "selected_six_template_closed_path_count": 24,
    "selected_six_template_delta_twice": 2,
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


def selected_word(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(row[column] for column in WORD_COLUMNS[: row["word_length"]])


def selected_trace(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(row[column] for column in TRACE_NODE_COLUMNS[: row["trace_node_count"]])


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_realization() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    splice_realization = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_carrier_splice_realization.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_carrier_splice_realization_certificate.json"
    )
    exact_csv = (
        OUT_DIR / "aperture_closure_tail_carrier_splice_exact_witnesses.csv"
    ).read_text(encoding="utf-8")
    template_csv = (
        OUT_DIR / "aperture_closure_tail_carrier_splice_selected_templates.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR / "aperture_closure_tail_carrier_splice_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_carrier_splice_realization_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        splice_realization
        != expected[
            "signature_boundary_spine_aperture_closure_tail_carrier_splice_realization"
        ]
    ):
        raise AssertionError("carrier-splice JSON is not reproducible")
    if exact_csv != expected["aperture_closure_tail_carrier_splice_exact_witnesses_csv"]:
        raise AssertionError("carrier-splice exact witness CSV is not reproducible")
    if (
        template_csv
        != expected["aperture_closure_tail_carrier_splice_selected_templates_csv"]
    ):
        raise AssertionError("carrier-splice selected template CSV is not reproducible")
    if observables_csv != expected["aperture_closure_tail_carrier_splice_observables_csv"]:
        raise AssertionError("carrier-splice observables CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_closure_tail_carrier_splice_realization_certificate"
        ]
    ):
        raise AssertionError("carrier-splice certificate is not reproducible")

    for name in ["exact_witness_table", "selected_template_table", "observable_table"]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"carrier-splice table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_realization@1":
        raise AssertionError("carrier-splice report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("carrier-splice layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("carrier-splice all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("carrier-splice checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("carrier-splice report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("carrier-splice report is not reproducible")

    exact_table = np.asarray(tables["exact_witness_table"], dtype=np.int64)
    selected_template_table = np.asarray(tables["selected_template_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if exact_table.shape != (11, len(EXACT_WITNESS_COLUMNS)):
        raise AssertionError("carrier-splice exact table shape mismatch")
    if selected_template_table.shape != (6, len(SELECTED_TEMPLATE_COLUMNS)):
        raise AssertionError("carrier-splice template table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("carrier-splice observable table shape mismatch")

    exact_rows = table_rows(exact_table, EXACT_WITNESS_COLUMNS)
    template_rows = table_rows(selected_template_table, SELECTED_TEMPLATE_COLUMNS)
    observable_rows = table_rows(observable_table, OBSERVABLE_COLUMNS)
    selected_rows = [
        row for row in exact_rows if row["selected_six_template_retention_flag"] == 1
    ]
    if len(selected_rows) != 1:
        raise AssertionError("carrier-splice selected six-template row mismatch")
    selected = selected_rows[0]
    if selected["splice_witness_id"] != 2:
        raise AssertionError("carrier-splice selected witness id mismatch")
    if selected_word(selected) != SELECTED_SIX_TEMPLATE_WORD:
        raise AssertionError("carrier-splice selected word mismatch")
    if selected_trace(selected) != SELECTED_SIX_TEMPLATE_TRACE:
        raise AssertionError("carrier-splice selected trace mismatch")
    if selected["metric_gromov_delta_twice"] != 2:
        raise AssertionError("carrier-splice selected delta mismatch")
    if selected["first_return_closed_path_count"] != 24:
        raise AssertionError("carrier-splice selected closure count mismatch")
    if selected["full_carrier_path_count"] != 240:
        raise AssertionError("carrier-splice selected full path count mismatch")
    if selected["trace_signature_total_variation"] != 223:
        raise AssertionError("carrier-splice selected variation mismatch")
    if (
        selected["has_chord_50_34_flag"],
        selected["rank104_prefix_27_31_50_flag"],
        selected["shared_rewrite_tail_suffix_flag"],
        selected["six_template_retention_flag"],
    ) != (1, 1, 1, 1):
        raise AssertionError("carrier-splice selected flags mismatch")
    if [
        row["selected_min_variation_flag"] for row in exact_rows
    ].count(1) != 1 or exact_rows[0]["selected_min_variation_flag"] != 1:
        raise AssertionError("carrier-splice min variation row mismatch")
    if exact_rows[0]["trace_signature_total_variation"] != 197:
        raise AssertionError("carrier-splice min variation value mismatch")
    if any(row["metric_gromov_delta_twice"] != 2 for row in exact_rows):
        raise AssertionError("carrier-splice exact delta values mismatch")
    if any(row["first_return_closed_path_count"] != 24 for row in exact_rows):
        raise AssertionError("carrier-splice exact closure values mismatch")
    if any(row["fixed_tail_atom_sequence_flag"] != 1 for row in exact_rows):
        raise AssertionError("carrier-splice fixed tail atom mismatch")
    if sum(row["has_chord_31_28_flag"] for row in exact_rows) != 6:
        raise AssertionError("carrier-splice 31--28 count mismatch")
    if sum(row["has_chord_50_34_flag"] for row in exact_rows) != 6:
        raise AssertionError("carrier-splice 50--34 count mismatch")
    if sum(
        row["has_chord_31_28_flag"] and row["has_chord_50_34_flag"]
        for row in exact_rows
    ) != 1:
        raise AssertionError("carrier-splice both-chord count mismatch")
    if sum(row["rank104_prefix_27_31_50_flag"] for row in exact_rows) != 5:
        raise AssertionError("carrier-splice rank104-prefix count mismatch")
    if sum(row["shared_rewrite_tail_suffix_flag"] for row in exact_rows) != 1:
        raise AssertionError("carrier-splice shared rewrite tail count mismatch")
    if sum(row["six_template_retention_flag"] for row in exact_rows) != 1:
        raise AssertionError("carrier-splice six-template count mismatch")

    if [row["selected_splice_path_count"] for row in template_rows] != [4] * 6:
        raise AssertionError("carrier-splice selected template counts mismatch")
    if [row["rank104_original_path_count"] for row in template_rows] != [4] * 6:
        raise AssertionError("carrier-splice original template counts mismatch")
    if [row_tuple(row, TAIL_CARRIER_COLUMNS) for row in template_rows] != EXPECTED_TEMPLATE_CARRIERS:
        raise AssertionError("carrier-splice template carriers mismatch")
    if [row_tuple(row, TAIL_EDGE_COLUMNS) for row in template_rows] != EXPECTED_TEMPLATE_EDGES:
        raise AssertionError("carrier-splice template edges mismatch")
    if [row_tuple(row, TAIL_ATOM_COLUMNS) for row in template_rows] != EXPECTED_TEMPLATE_ATOMS:
        raise AssertionError("carrier-splice template atoms mismatch")
    if Counter(row["tail_entry_carrier_id"] for row in template_rows) != {9: 3, 10: 1, 11: 2}:
        raise AssertionError("carrier-splice selected endpoint template distribution mismatch")

    observables = {
        row["observable_code"]: row["value_x1e12"] // 10**12
        for row in observable_rows
    }
    expected_observables = {
        OBSERVABLE_CODES[key]: value for key, value in EXPECTED_OBSERVABLES.items()
    }
    if observables != expected_observables:
        raise AssertionError("carrier-splice observables mismatch")

    witness = report.get("witness", {})
    if witness.get("selected_six_template_splice_witness_id") != 2:
        raise AssertionError("carrier-splice witness id mismatch")
    if witness.get("selected_six_template_word") != list(SELECTED_SIX_TEMPLATE_WORD):
        raise AssertionError("carrier-splice witness word mismatch")
    if witness.get("selected_six_template_trace") != list(SELECTED_SIX_TEMPLATE_TRACE):
        raise AssertionError("carrier-splice witness trace mismatch")
    if witness.get("selected_six_template_endpoint_counts") != {"9": 12, "10": 4, "11": 8}:
        raise AssertionError("carrier-splice witness endpoint counts mismatch")
    if splice_realization.get("summary", {}).get("exact_24_path_delta2_splice_count") != 11:
        raise AssertionError("carrier-splice summary exact count mismatch")
    if certificate.get("status") != STATUS:
        raise AssertionError("carrier-splice certificate status mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("prefix_chord_report", {}), PREFIX_CHORD_REPORT, "prefix chord report input")
    assert_file_hash(inputs.get("prefix_chord_json", {}), PREFIX_CHORD_JSON, "prefix chord JSON input")
    assert_file_hash(inputs.get("prefix_chord_candidates", {}), PREFIX_CHORD_CANDIDATES, "prefix chord candidates input")
    assert_file_hash(inputs.get("prefix_chord_tables", {}), PREFIX_CHORD_TABLES, "prefix chord tables input")
    assert_file_hash(inputs.get("prefix_chord_certificate", {}), PREFIX_CHORD_CERTIFICATE, "prefix chord certificate input")
    assert_file_hash(inputs.get("endpoint_split_report", {}), ENDPOINT_SPLIT_REPORT, "endpoint split report input")
    assert_file_hash(inputs.get("endpoint_split_templates", {}), ENDPOINT_SPLIT_TEMPLATES, "endpoint split templates input")
    assert_file_hash(inputs.get("endpoint_split_certificate", {}), ENDPOINT_SPLIT_CERTIFICATE, "endpoint split certificate input")
    assert_file_hash(inputs.get("cell_complex_edges", {}), CELL_COMPLEX_EDGES, "cell complex edges input")
    assert_file_hash(inputs.get("symbolic_alphabet", {}), SYMBOLIC_ALPHABET_CSV, "symbolic alphabet input")
    assert_file_hash(inputs.get("symbolic_associativity_csv", {}), SYMBOLIC_ASSOCIATIVITY_CSV, "symbolic associativity input")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script input")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator input")

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_realization_manifest@1":
        raise AssertionError("carrier-splice manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("carrier-splice manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("carrier-splice manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("carrier-splice missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("carrier-splice index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("carrier-splice index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_realization@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": witness,
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_realization()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
