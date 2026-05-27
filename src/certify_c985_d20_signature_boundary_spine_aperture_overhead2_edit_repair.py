from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_overhead2_edit_repair import (
        CANDIDATE_COLUMNS,
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        DERIVE_SCRIPT,
        MINIMUM_COLUMNS,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        OVERHEAD2_CARRIER_CERTIFICATE,
        OVERHEAD2_CARRIER_JSON,
        OVERHEAD2_CARRIER_REPORT,
        OVERHEAD2_CARRIER_TABLES,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        STATUS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        WEAK_CRITERION,
        STRONG_CRITERION,
        WORD_COLUMNS,
        build_payloads,
        row_word,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_overhead2_edit_repair import (
        CANDIDATE_COLUMNS,
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        DERIVE_SCRIPT,
        MINIMUM_COLUMNS,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        OVERHEAD2_CARRIER_CERTIFICATE,
        OVERHEAD2_CARRIER_JSON,
        OVERHEAD2_CARRIER_REPORT,
        OVERHEAD2_CARRIER_TABLES,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        STATUS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        WEAK_CRITERION,
        STRONG_CRITERION,
        WORD_COLUMNS,
        build_payloads,
        row_word,
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


def minimum_rows_by_key(table: np.ndarray) -> dict[tuple[int, int], dict[str, int]]:
    rows = {}
    for values in table:
        row = {
            column: int(values[index])
            for index, column in enumerate(MINIMUM_COLUMNS)
        }
        rows[(row["target_word_id"], row["criterion_code"])] = row
    return rows


def validate_c985_d20_signature_boundary_spine_aperture_overhead2_edit_repair() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    edit_repair = load_json(
        OUT_DIR / "signature_boundary_spine_aperture_overhead2_edit_repair.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead2_edit_repair_certificate.json"
    )
    candidates_csv = (
        OUT_DIR / "aperture_overhead2_edit_repair_candidates.csv"
    ).read_text(encoding="utf-8")
    minima_csv = (OUT_DIR / "aperture_overhead2_edit_repair_minima.csv").read_text(
        encoding="utf-8"
    )
    observables_csv = (
        OUT_DIR / "aperture_overhead2_edit_repair_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR / "signature_boundary_spine_aperture_overhead2_edit_repair_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        edit_repair
        != expected["signature_boundary_spine_aperture_overhead2_edit_repair"]
    ):
        raise AssertionError("overhead2 edit-repair JSON is not reproducible")
    if candidates_csv != expected["aperture_overhead2_edit_repair_candidates_csv"]:
        raise AssertionError("overhead2 edit-repair candidates CSV is not reproducible")
    if minima_csv != expected["aperture_overhead2_edit_repair_minima_csv"]:
        raise AssertionError("overhead2 edit-repair minima CSV is not reproducible")
    if observables_csv != expected["aperture_overhead2_edit_repair_observables_csv"]:
        raise AssertionError("overhead2 edit-repair observables CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_overhead2_edit_repair_certificate"
        ]
    ):
        raise AssertionError("overhead2 edit-repair certificate is not reproducible")

    for name in ["candidate_table", "minimum_table", "observable_table"]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"overhead2 edit-repair table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_overhead2_edit_repair@1":
        raise AssertionError("C985 d20 overhead2 edit-repair report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 overhead2 edit-repair layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 overhead2 edit-repair all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 overhead2 edit-repair checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 overhead2 edit-repair report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 overhead2 edit-repair report is not reproducible")

    missing = sorted(
        key
        for key in expected["report"]["checks"]
        if report.get("checks", {}).get(key) is not True
    )
    if missing:
        raise AssertionError(f"C985 d20 overhead2 edit-repair missing true checks: {missing}")

    candidate_table = np.asarray(tables["candidate_table"], dtype=np.int64)
    minimum_table = np.asarray(tables["minimum_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if candidate_table.shape != (596, len(CANDIDATE_COLUMNS)):
        raise AssertionError("overhead2 edit-repair candidate table shape mismatch")
    if minimum_table.shape != (4, len(MINIMUM_COLUMNS)):
        raise AssertionError("overhead2 edit-repair minimum table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("overhead2 edit-repair observable table shape mismatch")

    weak_idx = CANDIDATE_COLUMNS.index("weak_repair_flag")
    strong_idx = CANDIDATE_COLUMNS.index("strong_repair_flag")
    beat_idx = CANDIDATE_COLUMNS.index("beats_baseline_overhead_flag")
    edit_idx = CANDIDATE_COLUMNS.index("edit_distance")
    if int(np.sum(candidate_table[:, weak_idx])) != 37:
        raise AssertionError("overhead2 edit-repair weak count mismatch")
    if int(np.sum(candidate_table[:, strong_idx])) != 19:
        raise AssertionError("overhead2 edit-repair strong count mismatch")
    if int(np.sum(candidate_table[:, beat_idx])) != 0:
        raise AssertionError("overhead2 edit-repair unexpectedly beats baseline")
    if int(np.sum(candidate_table[candidate_table[:, edit_idx] == 0, weak_idx])) != 0:
        raise AssertionError("exact overhead2 words unexpectedly repair")

    rows = minimum_rows_by_key(minimum_table)
    expected_minima = {
        (0, WEAK_CRITERION): (1, 1, (2, 1, 4, 5, 2, 5), 3, 0),
        (0, STRONG_CRITERION): (2, 2, (2, 1, 4, 3, 2, 5, 4), 5, 1),
        (1, WEAK_CRITERION): (1, 1, (2, 1, 5, 2, 5, 4), 3, 1),
        (1, STRONG_CRITERION): (1, 1, (2, 1, 5, 2, 5, 4), 3, 1),
    }
    for key, expected_values in expected_minima.items():
        row = rows.get(key)
        if row is None:
            raise AssertionError(f"missing edit-repair minimum row {key}")
        min_edit, min_count, best_word, overhead, consumed = expected_values
        if row["minimal_edit_distance"] != min_edit:
            raise AssertionError(f"minimum edit distance mismatch for {key}")
        if row["minimal_repair_count"] != min_count:
            raise AssertionError(f"minimum repair count mismatch for {key}")
        if row_word(row) != best_word:
            raise AssertionError(f"best word mismatch for {key}")
        if row["best_trace_detour_overhead"] != overhead:
            raise AssertionError(f"best overhead mismatch for {key}")
        if row["best_target_consumed_before_node44_flag"] != consumed:
            raise AssertionError(f"target consumption flag mismatch for {key}")

    witness = report.get("witness", {})
    if witness.get("target_words") != [[2, 1, 4, 2, 5], [2, 1, 5, 2, 4]]:
        raise AssertionError("overhead2 edit-repair target words mismatch")
    if witness.get("weak_repairs_beating_baseline_count") != 0:
        raise AssertionError("overhead2 edit-repair weak beating count mismatch")
    if witness.get("strong_repairs_beating_baseline_count") != 0:
        raise AssertionError("overhead2 edit-repair strong beating count mismatch")
    minimum_witness = witness.get("minimum_repairs", {})
    if minimum_witness.get("0:0", {}).get("best_word") != [2, 1, 4, 5, 2, 5]:
        raise AssertionError("target0 weak witness word mismatch")
    if minimum_witness.get("0:1", {}).get("best_word") != [2, 1, 4, 3, 2, 5, 4]:
        raise AssertionError("target0 strong witness word mismatch")
    if minimum_witness.get("1:0", {}).get("best_word") != [2, 1, 5, 2, 5, 4]:
        raise AssertionError("target1 weak witness word mismatch")
    if minimum_witness.get("1:1", {}).get("best_word") != [2, 1, 5, 2, 5, 4]:
        raise AssertionError("target1 strong witness word mismatch")
    if witness.get("candidate_table_sha256") != expected["report"]["witness"]["candidate_table_sha256"]:
        raise AssertionError("candidate table witness hash mismatch")
    if witness.get("minimum_table_sha256") != expected["report"]["witness"]["minimum_table_sha256"]:
        raise AssertionError("minimum table witness hash mismatch")
    if witness.get("observable_table_sha256") != expected["report"]["witness"]["observable_table_sha256"]:
        raise AssertionError("observable table witness hash mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("overhead2_carrier_report", {}), OVERHEAD2_CARRIER_REPORT, "overhead2 carrier report input")
    assert_file_hash(inputs.get("overhead2_carrier_json", {}), OVERHEAD2_CARRIER_JSON, "overhead2 carrier JSON input")
    assert_file_hash(inputs.get("overhead2_carrier_tables", {}), OVERHEAD2_CARRIER_TABLES, "overhead2 carrier tables input")
    assert_file_hash(inputs.get("overhead2_carrier_certificate", {}), OVERHEAD2_CARRIER_CERTIFICATE, "overhead2 carrier certificate input")
    assert_file_hash(inputs.get("cell_complex_report", {}), CELL_COMPLEX_REPORT, "cell complex report input")
    assert_file_hash(inputs.get("cell_complex_edges", {}), CELL_COMPLEX_EDGES, "cell complex edges input")
    assert_file_hash(inputs.get("cell_complex_tables", {}), CELL_COMPLEX_TABLES, "cell complex tables input")
    assert_file_hash(inputs.get("cell_complex_certificate", {}), CELL_COMPLEX_CERTIFICATE, "cell complex certificate input")
    assert_file_hash(inputs.get("rewrite_complex_report", {}), REWRITE_COMPLEX_REPORT, "rewrite complex report input")
    assert_file_hash(inputs.get("rewrite_complex_edges", {}), REWRITE_COMPLEX_EDGES, "rewrite complex edges input")
    assert_file_hash(inputs.get("rewrite_complex_tables", {}), REWRITE_COMPLEX_TABLES, "rewrite complex tables input")
    assert_file_hash(inputs.get("rewrite_complex_certificate", {}), REWRITE_COMPLEX_CERTIFICATE, "rewrite complex certificate input")
    assert_file_hash(inputs.get("symbolic_associativity_report", {}), SYMBOLIC_ASSOCIATIVITY_REPORT, "symbolic associativity report input")
    assert_file_hash(inputs.get("symbolic_associativity_csv", {}), SYMBOLIC_ASSOCIATIVITY_CSV, "symbolic associativity CSV input")
    assert_file_hash(inputs.get("symbolic_associativity_tables", {}), SYMBOLIC_ASSOCIATIVITY_TABLES, "symbolic associativity tables input")
    assert_file_hash(inputs.get("symbolic_associativity_certificate", {}), SYMBOLIC_ASSOCIATIVITY_CERTIFICATE, "symbolic associativity certificate input")
    assert_file_hash(inputs.get("symbolic_alphabet", {}), SYMBOLIC_ALPHABET_CSV, "symbolic alphabet input")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script input")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator input")

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_overhead2_edit_repair_manifest@1":
        raise AssertionError("C985 d20 overhead2 edit-repair manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 overhead2 edit-repair manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 overhead2 edit-repair manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("C985 d20 overhead2 edit-repair missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 overhead2 edit-repair index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 overhead2 edit-repair index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_overhead2_edit_repair@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "minimum_repairs": witness.get("minimum_repairs"),
        "weak_repairs_beating_baseline_count": witness.get(
            "weak_repairs_beating_baseline_count"
        ),
        "strong_repairs_beating_baseline_count": witness.get(
            "strong_repairs_beating_baseline_count"
        ),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_aperture_overhead2_edit_repair()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
