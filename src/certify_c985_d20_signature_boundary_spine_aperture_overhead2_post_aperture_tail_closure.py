from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure import (
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        CLOSED_PATH_COLUMNS,
        DERIVE_SCRIPT,
        EDIT_REPAIR_CANDIDATES,
        EDIT_REPAIR_CERTIFICATE,
        EDIT_REPAIR_JSON,
        EDIT_REPAIR_REPORT,
        EDIT_REPAIR_TABLES,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        REPAIR_COLUMNS,
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
        build_payloads,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure import (
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        CLOSED_PATH_COLUMNS,
        DERIVE_SCRIPT,
        EDIT_REPAIR_CANDIDATES,
        EDIT_REPAIR_CERTIFICATE,
        EDIT_REPAIR_JSON,
        EDIT_REPAIR_REPORT,
        EDIT_REPAIR_TABLES,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        REPAIR_COLUMNS,
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


def validate_c985_d20_signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    tail_closure = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure_certificate.json"
    )
    repairs_csv = (
        OUT_DIR / "aperture_overhead2_post_aperture_tail_repairs.csv"
    ).read_text(encoding="utf-8")
    closed_paths_csv = (
        OUT_DIR / "aperture_overhead2_post_aperture_tail_closed_paths.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR / "aperture_overhead2_post_aperture_tail_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        tail_closure
        != expected[
            "signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure"
        ]
    ):
        raise AssertionError("post-aperture tail closure JSON is not reproducible")
    if repairs_csv != expected["aperture_overhead2_post_aperture_tail_repairs_csv"]:
        raise AssertionError("post-aperture tail repairs CSV is not reproducible")
    if (
        closed_paths_csv
        != expected["aperture_overhead2_post_aperture_tail_closed_paths_csv"]
    ):
        raise AssertionError("post-aperture tail closed paths CSV is not reproducible")
    if (
        observables_csv
        != expected["aperture_overhead2_post_aperture_tail_observables_csv"]
    ):
        raise AssertionError("post-aperture tail observables CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure_certificate"
        ]
    ):
        raise AssertionError("post-aperture tail closure certificate is not reproducible")

    for name in ["repair_table", "closed_path_table", "observable_table"]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"post-aperture tail table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure@1":
        raise AssertionError("C985 d20 post-aperture tail closure report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 post-aperture tail closure layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 post-aperture tail closure all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 post-aperture tail closure checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 post-aperture tail closure report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 post-aperture tail closure report is not reproducible")

    missing = sorted(
        key
        for key in expected["report"]["checks"]
        if report.get("checks", {}).get(key) is not True
    )
    if missing:
        raise AssertionError(f"C985 d20 post-aperture tail closure missing true checks: {missing}")

    repair_table = np.asarray(tables["repair_table"], dtype=np.int64)
    closed_path_table = np.asarray(tables["closed_path_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if repair_table.shape != (2, len(REPAIR_COLUMNS)):
        raise AssertionError("post-aperture tail repair table shape mismatch")
    if closed_path_table.shape != (20, len(CLOSED_PATH_COLUMNS)):
        raise AssertionError("post-aperture tail closed-path table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("post-aperture tail observable table shape mismatch")

    target_idx = REPAIR_COLUMNS.index("target_word_id")
    post_tail_len_idx = REPAIR_COLUMNS.index("post_aperture_tail_length")
    post_tail_symbol_idx = REPAIR_COLUMNS.index("post_aperture_tail_symbol_0_id")
    target_after_idx = REPAIR_COLUMNS.index("target_consumed_after_node44_flag")
    full_paths_idx = REPAIR_COLUMNS.index("full_repair_path_count")
    full_closed_idx = REPAIR_COLUMNS.index("full_repair_closed_path_count")
    min_closure_idx = REPAIR_COLUMNS.index("minimal_extra_closure_length")
    closure_symbol_idx = REPAIR_COLUMNS.index("closure_suffix_symbol_0_id")
    closure_closed_idx = REPAIR_COLUMNS.index("closure_closed_path_count")
    repair_by_target = {
        int(row[target_idx]): row
        for row in repair_table
    }
    if int(repair_by_target[0][post_tail_len_idx]) != 1:
        raise AssertionError("target0 post-aperture tail length mismatch")
    if int(repair_by_target[0][post_tail_symbol_idx]) != 5:
        raise AssertionError("target0 post-aperture tail symbol mismatch")
    if int(repair_by_target[0][target_after_idx]) != 1:
        raise AssertionError("target0 target-after-node44 flag mismatch")
    if int(repair_by_target[0][full_paths_idx]) != 48:
        raise AssertionError("target0 full path count mismatch")
    if int(repair_by_target[0][full_closed_idx]) != 8:
        raise AssertionError("target0 closed full path count mismatch")
    if int(repair_by_target[0][min_closure_idx]) != 0:
        raise AssertionError("target0 closure length mismatch")

    if int(repair_by_target[1][post_tail_len_idx]) != 0:
        raise AssertionError("target1 post-aperture tail length mismatch")
    if int(repair_by_target[1][target_after_idx]) != 0:
        raise AssertionError("target1 target-after-node44 flag mismatch")
    if int(repair_by_target[1][full_paths_idx]) != 16:
        raise AssertionError("target1 full path count mismatch")
    if int(repair_by_target[1][full_closed_idx]) != 0:
        raise AssertionError("target1 closed full path count mismatch")
    if int(repair_by_target[1][min_closure_idx]) != 1:
        raise AssertionError("target1 closure length mismatch")
    if int(repair_by_target[1][closure_symbol_idx]) != 3:
        raise AssertionError("target1 closure suffix mismatch")
    if int(repair_by_target[1][closure_closed_idx]) != 12:
        raise AssertionError("target1 closed closure path count mismatch")

    closed_repair_idx = CLOSED_PATH_COLUMNS.index("repair_id")
    closed_counts = {
        repair_id: int(np.sum(closed_path_table[:, closed_repair_idx] == repair_id))
        for repair_id in [0, 1]
    }
    if closed_counts != {0: 8, 1: 12}:
        raise AssertionError("closed path row split mismatch")

    witness = report.get("witness", {})
    repairs = witness.get("one_contact_weak_repairs", {})
    if repairs.get("0", {}).get("repair_word") != [2, 1, 4, 5, 2, 5]:
        raise AssertionError("target0 repair witness word mismatch")
    if repairs.get("0", {}).get("best_closure_suffix") != []:
        raise AssertionError("target0 closure suffix witness mismatch")
    if repairs.get("0", {}).get("closure_closed_path_count") != 8:
        raise AssertionError("target0 closure count witness mismatch")
    if repairs.get("1", {}).get("repair_word") != [2, 1, 5, 2, 5, 4]:
        raise AssertionError("target1 repair witness word mismatch")
    if repairs.get("1", {}).get("best_closure_suffix") != [3]:
        raise AssertionError("target1 closure suffix witness mismatch")
    if repairs.get("1", {}).get("closure_closed_path_count") != 12:
        raise AssertionError("target1 closure count witness mismatch")
    if witness.get("closed_path_count_by_repair") != {"0": 8, "1": 12}:
        raise AssertionError("closed path witness split mismatch")
    if witness.get("repair_table_sha256") != expected["report"]["witness"]["repair_table_sha256"]:
        raise AssertionError("repair table witness hash mismatch")
    if witness.get("closed_path_table_sha256") != expected["report"]["witness"]["closed_path_table_sha256"]:
        raise AssertionError("closed path table witness hash mismatch")
    if witness.get("observable_table_sha256") != expected["report"]["witness"]["observable_table_sha256"]:
        raise AssertionError("observable table witness hash mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("edit_repair_report", {}), EDIT_REPAIR_REPORT, "edit repair report input")
    assert_file_hash(inputs.get("edit_repair_json", {}), EDIT_REPAIR_JSON, "edit repair JSON input")
    assert_file_hash(inputs.get("edit_repair_candidates", {}), EDIT_REPAIR_CANDIDATES, "edit repair candidates input")
    assert_file_hash(inputs.get("edit_repair_tables", {}), EDIT_REPAIR_TABLES, "edit repair tables input")
    assert_file_hash(inputs.get("edit_repair_certificate", {}), EDIT_REPAIR_CERTIFICATE, "edit repair certificate input")
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

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure_manifest@1":
        raise AssertionError("C985 d20 post-aperture tail closure manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 post-aperture tail closure manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 post-aperture tail closure manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("C985 d20 post-aperture tail closure missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 post-aperture tail closure index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 post-aperture tail closure index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "one_contact_weak_repairs": witness.get("one_contact_weak_repairs"),
        "closed_path_count_by_repair": witness.get("closed_path_count_by_repair"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
