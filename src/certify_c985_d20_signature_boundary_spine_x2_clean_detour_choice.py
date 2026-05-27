from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_x2_clean_detour_choice import (
        APERTURE_INSERTION_CERTIFICATE,
        APERTURE_INSERTION_JSON,
        APERTURE_INSERTION_REPORT,
        APERTURE_INSERTION_SEQUENCE,
        APERTURE_INSERTION_TABLES,
        APERTURE_INSERTION_WINDOWS,
        BRANCHING_LAW_CERTIFICATE,
        BRANCHING_LAW_CSV,
        BRANCHING_LAW_REPORT,
        BRANCHING_LAW_TABLES,
        OBSERVABLE_COLUMNS,
        OBSERVABLE_CODES,
        OUT_DIR,
        RETURN_CHOICE_COLUMNS,
        STATUS,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        TAIL_SIMULATION_COLUMNS,
        THEOREM_ID,
        TYPED_CORRIDOR_CERTIFICATE,
        TYPED_CORRIDOR_EDGES,
        TYPED_CORRIDOR_REPORT,
        TYPED_CORRIDOR_TABLES,
        X2_DETOUR_CERTIFICATE,
        X2_DETOUR_JSON,
        X2_DETOUR_REPORT,
        X2_DETOUR_RETURNS,
        X2_DETOUR_TABLES,
        build_payloads,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_x2_clean_detour_choice import (
        APERTURE_INSERTION_CERTIFICATE,
        APERTURE_INSERTION_JSON,
        APERTURE_INSERTION_REPORT,
        APERTURE_INSERTION_SEQUENCE,
        APERTURE_INSERTION_TABLES,
        APERTURE_INSERTION_WINDOWS,
        BRANCHING_LAW_CERTIFICATE,
        BRANCHING_LAW_CSV,
        BRANCHING_LAW_REPORT,
        BRANCHING_LAW_TABLES,
        OBSERVABLE_COLUMNS,
        OBSERVABLE_CODES,
        OUT_DIR,
        RETURN_CHOICE_COLUMNS,
        STATUS,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        TAIL_SIMULATION_COLUMNS,
        THEOREM_ID,
        TYPED_CORRIDOR_CERTIFICATE,
        TYPED_CORRIDOR_EDGES,
        TYPED_CORRIDOR_REPORT,
        TYPED_CORRIDOR_TABLES,
        X2_DETOUR_CERTIFICATE,
        X2_DETOUR_JSON,
        X2_DETOUR_REPORT,
        X2_DETOUR_RETURNS,
        X2_DETOUR_TABLES,
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


def validate_c985_d20_signature_boundary_spine_x2_clean_detour_choice() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    clean_choice = load_json(
        OUT_DIR / "signature_boundary_spine_x2_clean_detour_choice.json"
    )
    certificate = load_json(
        OUT_DIR / "signature_boundary_spine_x2_clean_detour_choice_certificate.json"
    )
    return_choices_csv = (OUT_DIR / "x2_clean_detour_return_choices.csv").read_text(
        encoding="utf-8"
    )
    tail_simulation_csv = (
        OUT_DIR / "x2_clean_detour_tail_simulation.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (OUT_DIR / "x2_clean_detour_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(
        OUT_DIR / "signature_boundary_spine_x2_clean_detour_choice_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if clean_choice != expected["signature_boundary_spine_x2_clean_detour_choice"]:
        raise AssertionError("x2 clean detour choice JSON is not reproducible")
    if return_choices_csv != expected["x2_clean_detour_return_choices_csv"]:
        raise AssertionError("x2 clean detour return-choice CSV is not reproducible")
    if tail_simulation_csv != expected["x2_clean_detour_tail_simulation_csv"]:
        raise AssertionError("x2 clean detour tail simulation CSV is not reproducible")
    if observables_csv != expected["x2_clean_detour_observables_csv"]:
        raise AssertionError("x2 clean detour observable CSV is not reproducible")
    if (
        certificate
        != expected["signature_boundary_spine_x2_clean_detour_choice_certificate"]
    ):
        raise AssertionError("x2 clean detour choice certificate is not reproducible")

    table_names = [
        "return_choice_table",
        "tail_simulation_table",
        "observable_table",
    ]
    for name in table_names:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"x2 clean detour choice table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_x2_clean_detour_choice@1":
        raise AssertionError("C985 d20 x2 clean detour choice report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 x2 clean detour choice is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 x2 clean detour choice all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 x2 clean detour choice checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 x2 clean detour choice report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 x2 clean detour choice report is not reproducible")

    checks = report.get("checks", {})
    required_true = set(expected["report"]["checks"])
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(
            f"C985 d20 x2 clean detour choice missing true checks: {missing}"
        )

    witness = report.get("witness", {})
    if witness.get("clean_return_choices") != [[14, 10, 7, 0], [14, 11, 8, 1]]:
        raise AssertionError("x2 clean detour return choices mismatch")
    if witness.get("tail_order_after_slot") != [[8, 1], [7, 0]]:
        raise AssertionError("x2 clean detour tail order mismatch")
    if witness.get("selected_return_choice_id") != 1:
        raise AssertionError("x2 clean detour selected choice id mismatch")
    if witness.get("selected_return_path") != [14, 11]:
        raise AssertionError("x2 clean detour selected return path mismatch")
    if witness.get("selected_return_negative_carrier_id") != 8:
        raise AssertionError("x2 clean detour selected negative carrier mismatch")
    if witness.get("selected_return_shared_symbol_id") != 1:
        raise AssertionError("x2 clean detour selected symbol mismatch")
    if witness.get("selected_tail_contacts_preserved_count") != 2:
        raise AssertionError("x2 clean detour selected tail preservation mismatch")
    if witness.get("selected_tail_order_disturbance_count") != 0:
        raise AssertionError("x2 clean detour selected tail disturbance mismatch")
    if witness.get("selected_branch_order_rewind") != 3:
        raise AssertionError("x2 clean detour branch rewind mismatch")
    if witness.get("selected_spine_rank_rewind") != 9:
        raise AssertionError("x2 clean detour spine rewind mismatch")
    if witness.get("slot_context", {}).get("selected_terminal_canonical_triple_id") != 42:
        raise AssertionError("x2 clean detour slot terminal node mismatch")
    if witness.get("post_return_windows") != [
        {
            "return_negative_carrier_id": 7,
            "ordered_symbols": [3, 2, 0],
            "canonical_triple_id": 12,
            "sector_coverage_count": 5,
            "signature_union_count": 142,
        },
        {
            "return_negative_carrier_id": 8,
            "ordered_symbols": [3, 2, 1],
            "canonical_triple_id": 27,
            "sector_coverage_count": 5,
            "signature_union_count": 146,
        },
    ]:
        raise AssertionError("x2 clean detour post-return windows mismatch")

    return_choice_table = np.asarray(tables["return_choice_table"], dtype=np.int64)
    tail_simulation_table = np.asarray(tables["tail_simulation_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)

    if return_choice_table.shape != (2, len(RETURN_CHOICE_COLUMNS)):
        raise AssertionError("x2 clean detour return-choice table shape mismatch")
    if tail_simulation_table.shape != (4, len(TAIL_SIMULATION_COLUMNS)):
        raise AssertionError("x2 clean detour tail simulation table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("x2 clean detour observable table shape mismatch")
    if return_choice_table.tolist() != [
        [0, 14, 3, 10, 7, 0, 1, 3, 2, 2, 3, 11, 4, 2, 1, 1, 0, 12, 5, 142, 1, 1, 0],
        [1, 14, 3, 11, 8, 1, 2, 5, 3, 3, 5, 9, 3, 1, 2, 0, 1, 27, 5, 146, 1, 1, 1],
    ]:
        raise AssertionError("x2 clean detour return-choice table rows mismatch")
    if tail_simulation_table.tolist() != [
        [0, 1, 15, 1, 8, 1, 2, 0, 0, 1],
        [0, 2, 16, 0, 7, 0, 1, 1, 1, 0],
        [1, 1, 15, 1, 8, 1, 2, 1, 1, 0],
        [1, 2, 16, 0, 7, 0, 1, 0, 1, 0],
    ]:
        raise AssertionError("x2 clean detour tail simulation table rows mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("x2_detour_report", {}), X2_DETOUR_REPORT, "x2 detour report input")
    assert_file_hash(inputs.get("x2_detour_fan", {}), X2_DETOUR_JSON, "x2 detour JSON input")
    assert_file_hash(inputs.get("x2_detour_returns", {}), X2_DETOUR_RETURNS, "x2 detour returns input")
    assert_file_hash(inputs.get("x2_detour_tables", {}), X2_DETOUR_TABLES, "x2 detour table input")
    assert_file_hash(inputs.get("x2_detour_certificate", {}), X2_DETOUR_CERTIFICATE, "x2 detour certificate input")
    assert_file_hash(inputs.get("typed_corridor_report", {}), TYPED_CORRIDOR_REPORT, "typed corridor report input")
    assert_file_hash(inputs.get("typed_corridor_edges", {}), TYPED_CORRIDOR_EDGES, "typed corridor edge input")
    assert_file_hash(inputs.get("typed_corridor_tables", {}), TYPED_CORRIDOR_TABLES, "typed corridor table input")
    assert_file_hash(inputs.get("typed_corridor_certificate", {}), TYPED_CORRIDOR_CERTIFICATE, "typed corridor certificate input")
    assert_file_hash(inputs.get("branching_law_report", {}), BRANCHING_LAW_REPORT, "branching law report input")
    assert_file_hash(inputs.get("branching_law_csv", {}), BRANCHING_LAW_CSV, "branching law CSV input")
    assert_file_hash(inputs.get("branching_law_tables", {}), BRANCHING_LAW_TABLES, "branching law table input")
    assert_file_hash(inputs.get("branching_law_certificate", {}), BRANCHING_LAW_CERTIFICATE, "branching law certificate input")
    assert_file_hash(inputs.get("aperture_insertion_report", {}), APERTURE_INSERTION_REPORT, "aperture insertion report input")
    assert_file_hash(inputs.get("aperture_insertion", {}), APERTURE_INSERTION_JSON, "aperture insertion JSON input")
    assert_file_hash(inputs.get("aperture_insertion_windows", {}), APERTURE_INSERTION_WINDOWS, "aperture insertion windows input")
    assert_file_hash(inputs.get("aperture_insertion_sequence", {}), APERTURE_INSERTION_SEQUENCE, "aperture insertion sequence input")
    assert_file_hash(inputs.get("aperture_insertion_tables", {}), APERTURE_INSERTION_TABLES, "aperture insertion table input")
    assert_file_hash(inputs.get("aperture_insertion_certificate", {}), APERTURE_INSERTION_CERTIFICATE, "aperture insertion certificate input")
    assert_file_hash(inputs.get("symbolic_associativity_report", {}), SYMBOLIC_ASSOCIATIVITY_REPORT, "symbolic associativity report input")
    assert_file_hash(inputs.get("symbolic_associativity_csv", {}), SYMBOLIC_ASSOCIATIVITY_CSV, "symbolic associativity CSV input")
    assert_file_hash(inputs.get("symbolic_associativity_tables", {}), SYMBOLIC_ASSOCIATIVITY_TABLES, "symbolic associativity table input")
    assert_file_hash(inputs.get("symbolic_associativity_certificate", {}), SYMBOLIC_ASSOCIATIVITY_CERTIFICATE, "symbolic associativity certificate input")

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_x2_clean_detour_choice_manifest@1":
        raise AssertionError("C985 d20 x2 clean detour choice manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 x2 clean detour choice manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 x2 clean detour choice manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("C985 d20 x2 clean detour choice missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 x2 clean detour choice index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 x2 clean detour choice index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_x2_clean_detour_choice@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "selected_return_path": witness.get("selected_return_path"),
        "selected_return_negative_carrier_id": witness.get(
            "selected_return_negative_carrier_id"
        ),
        "selected_return_shared_symbol_id": witness.get(
            "selected_return_shared_symbol_id"
        ),
        "selected_tail_contacts_preserved_count": witness.get(
            "selected_tail_contacts_preserved_count"
        ),
        "selected_tail_order_disturbance_count": witness.get(
            "selected_tail_order_disturbance_count"
        ),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_x2_clean_detour_choice()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
