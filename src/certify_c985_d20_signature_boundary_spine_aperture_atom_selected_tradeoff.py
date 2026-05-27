from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_atom_selected_tradeoff import (
        ATOM_SELECTED_DOMINATED_IDS,
        ATOM_SELECTED_FRONTIER_IDS,
        ATOM_SELECTOR_CANDIDATES,
        ATOM_SELECTOR_CERTIFICATE,
        ATOM_SELECTOR_JSON,
        ATOM_SELECTOR_REPORT,
        ATOM_SELECTOR_STEPS,
        ATOM_SELECTOR_TABLES,
        MIXED_CONTACT_CANDIDATES,
        MIXED_CONTACT_CERTIFICATE,
        MIXED_CONTACT_EDGES,
        MIXED_CONTACT_REPORT,
        MIXED_CONTACT_TABLES,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PARETO_CANDIDATES,
        PARETO_CERTIFICATE,
        PARETO_CLASSES,
        PARETO_JSON,
        PARETO_REPORT,
        PARETO_TABLES,
        SELECTED_CLEAN_X1_CANDIDATE_ID,
        STATUS,
        THEOREM_ID,
        TRADEOFF_CANDIDATE_COLUMNS,
        TRADEOFF_CLASS_COLUMNS,
        X2_ATOM_ID,
        ZERO_OVERHEAD_CANDIDATE_IDS,
        build_payloads,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_atom_selected_tradeoff import (
        ATOM_SELECTED_DOMINATED_IDS,
        ATOM_SELECTED_FRONTIER_IDS,
        ATOM_SELECTOR_CANDIDATES,
        ATOM_SELECTOR_CERTIFICATE,
        ATOM_SELECTOR_JSON,
        ATOM_SELECTOR_REPORT,
        ATOM_SELECTOR_STEPS,
        ATOM_SELECTOR_TABLES,
        MIXED_CONTACT_CANDIDATES,
        MIXED_CONTACT_CERTIFICATE,
        MIXED_CONTACT_EDGES,
        MIXED_CONTACT_REPORT,
        MIXED_CONTACT_TABLES,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PARETO_CANDIDATES,
        PARETO_CERTIFICATE,
        PARETO_CLASSES,
        PARETO_JSON,
        PARETO_REPORT,
        PARETO_TABLES,
        SELECTED_CLEAN_X1_CANDIDATE_ID,
        STATUS,
        THEOREM_ID,
        TRADEOFF_CANDIDATE_COLUMNS,
        TRADEOFF_CLASS_COLUMNS,
        X2_ATOM_ID,
        ZERO_OVERHEAD_CANDIDATE_IDS,
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


def validate_c985_d20_signature_boundary_spine_aperture_atom_selected_tradeoff() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    tradeoff = load_json(
        OUT_DIR / "signature_boundary_spine_aperture_atom_selected_tradeoff.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_atom_selected_tradeoff_certificate.json"
    )
    candidates_csv = (
        OUT_DIR / "aperture_atom_selected_tradeoff_candidates.csv"
    ).read_text(encoding="utf-8")
    classes_csv = (OUT_DIR / "aperture_atom_selected_tradeoff_classes.csv").read_text(
        encoding="utf-8"
    )
    observables_csv = (
        OUT_DIR / "aperture_atom_selected_tradeoff_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR / "signature_boundary_spine_aperture_atom_selected_tradeoff_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if tradeoff != expected["signature_boundary_spine_aperture_atom_selected_tradeoff"]:
        raise AssertionError("atom-selected tradeoff JSON is not reproducible")
    if candidates_csv != expected["aperture_atom_selected_tradeoff_candidates_csv"]:
        raise AssertionError("atom-selected tradeoff candidate CSV is not reproducible")
    if classes_csv != expected["aperture_atom_selected_tradeoff_classes_csv"]:
        raise AssertionError("atom-selected tradeoff class CSV is not reproducible")
    if observables_csv != expected["aperture_atom_selected_tradeoff_observables_csv"]:
        raise AssertionError("atom-selected tradeoff observable CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_atom_selected_tradeoff_certificate"
        ]
    ):
        raise AssertionError("atom-selected tradeoff certificate is not reproducible")

    for name in ["candidate_table", "class_table", "observable_table"]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"atom-selected tradeoff table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_atom_selected_tradeoff@1":
        raise AssertionError("C985 d20 atom-selected tradeoff report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 atom-selected tradeoff is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 atom-selected tradeoff all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 atom-selected tradeoff checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 atom-selected tradeoff report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 atom-selected tradeoff report is not reproducible")

    missing = sorted(
        key
        for key in expected["report"]["checks"]
        if report.get("checks", {}).get(key) is not True
    )
    if missing:
        raise AssertionError(f"C985 d20 atom-selected tradeoff missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("frontier_candidate_ids") != ATOM_SELECTED_FRONTIER_IDS:
        raise AssertionError("atom-selected tradeoff frontier IDs mismatch")
    if witness.get("dominated_candidate_ids") != ATOM_SELECTED_DOMINATED_IDS:
        raise AssertionError("atom-selected tradeoff dominated IDs mismatch")
    if witness.get("zero_overhead_cost_transition") != {
        "atom_selected_tail_cost": 1,
        "old_typed_boundary_cost": 2,
        "reason": "selected first-contact x5 leakage is zero, but x1 tail is still abandoned",
    }:
        raise AssertionError("atom-selected tradeoff zero-overhead transition mismatch")
    if witness.get("x1_tail_class") != {
        "atom_selected_tail_cost": 0,
        "candidate_ids": [SELECTED_CLEAN_X1_CANDIDATE_ID, 7],
        "signature_valley_depth": 37,
        "trace_detour_overhead": 3,
    }:
        raise AssertionError("atom-selected tradeoff x1-tail class mismatch")

    frontier_classes = [
        row for row in witness.get("frontier_classes", []) if row.get("frontier_class")
    ]
    if [row.get("class_code") for row in frontier_classes] != [0, 1]:
        raise AssertionError("atom-selected tradeoff frontier class code mismatch")
    if frontier_classes[0].get("atom_selected_tail_cost") != 1:
        raise AssertionError("atom-selected tradeoff geodesic cost mismatch")
    if frontier_classes[1].get("atom_selected_tail_cost") != 0:
        raise AssertionError("atom-selected tradeoff x1-tail cost mismatch")

    candidate_table = np.asarray(tables["candidate_table"], dtype=np.int64)
    class_table = np.asarray(tables["class_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if candidate_table.shape != (10, len(TRADEOFF_CANDIDATE_COLUMNS)):
        raise AssertionError("atom-selected tradeoff candidate table shape mismatch")
    if class_table.shape != (3, len(TRADEOFF_CLASS_COLUMNS)):
        raise AssertionError("atom-selected tradeoff class table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("atom-selected tradeoff observable table shape mismatch")

    selected_atom_idx = TRADEOFF_CANDIDATE_COLUMNS.index(
        "selected_first_contact_atom_id"
    )
    selected_leak_idx = TRADEOFF_CANDIDATE_COLUMNS.index(
        "selected_first_contact_x5_leakage_flag"
    )
    atom_cost_idx = TRADEOFF_CANDIDATE_COLUMNS.index("atom_selected_tail_cost")
    frontier_idx = TRADEOFF_CANDIDATE_COLUMNS.index(
        "atom_selected_pareto_frontier_flag"
    )
    dominated_idx = TRADEOFF_CANDIDATE_COLUMNS.index("atom_selected_dominated_flag")
    class_idx = TRADEOFF_CANDIDATE_COLUMNS.index("atom_selected_class_code")
    if candidate_table[:, selected_atom_idx].tolist() != [X2_ATOM_ID] * 10:
        raise AssertionError("atom-selected tradeoff selected atom vector mismatch")
    if candidate_table[:, selected_leak_idx].tolist() != [0] * 10:
        raise AssertionError("atom-selected tradeoff selected leakage vector mismatch")
    if candidate_table[:, atom_cost_idx].tolist() != [1, 1, 1, 1, 1, 1, 0, 0, 1, 1]:
        raise AssertionError("atom-selected tradeoff atom cost vector mismatch")
    if candidate_table[:, frontier_idx].tolist() != [1, 1, 1, 1, 1, 1, 1, 1, 0, 0]:
        raise AssertionError("atom-selected tradeoff frontier vector mismatch")
    if candidate_table[:, dominated_idx].tolist() != [0, 0, 0, 0, 0, 0, 0, 0, 1, 1]:
        raise AssertionError("atom-selected tradeoff dominated vector mismatch")
    if candidate_table[:, class_idx].tolist() != [0, 0, 0, 0, 0, 0, 1, 1, 2, 2]:
        raise AssertionError("atom-selected tradeoff class vector mismatch")

    if class_table[:, 0].tolist() != [0, 1, 2]:
        raise AssertionError("atom-selected tradeoff class order mismatch")
    if class_table[:, 2].tolist() != [6, 2, 2]:
        raise AssertionError("atom-selected tradeoff class sizes mismatch")
    if class_table[:, 3].tolist() != [1, 1, 0]:
        raise AssertionError("atom-selected tradeoff class frontier flags mismatch")
    if class_table[:, 7].tolist() != [1, 0, 1]:
        raise AssertionError("atom-selected tradeoff class costs mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("atom_selector_report", {}), ATOM_SELECTOR_REPORT, "atom selector report input")
    assert_file_hash(inputs.get("atom_selector_json", {}), ATOM_SELECTOR_JSON, "atom selector JSON input")
    assert_file_hash(inputs.get("atom_selector_candidates", {}), ATOM_SELECTOR_CANDIDATES, "atom selector candidates input")
    assert_file_hash(inputs.get("atom_selector_steps", {}), ATOM_SELECTOR_STEPS, "atom selector steps input")
    assert_file_hash(inputs.get("atom_selector_tables", {}), ATOM_SELECTOR_TABLES, "atom selector tables input")
    assert_file_hash(inputs.get("atom_selector_certificate", {}), ATOM_SELECTOR_CERTIFICATE, "atom selector certificate input")
    assert_file_hash(inputs.get("mixed_contact_report", {}), MIXED_CONTACT_REPORT, "mixed contact report input")
    assert_file_hash(inputs.get("mixed_contact_candidates", {}), MIXED_CONTACT_CANDIDATES, "mixed contact candidates input")
    assert_file_hash(inputs.get("mixed_contact_edges", {}), MIXED_CONTACT_EDGES, "mixed contact edges input")
    assert_file_hash(inputs.get("mixed_contact_tables", {}), MIXED_CONTACT_TABLES, "mixed contact tables input")
    assert_file_hash(inputs.get("mixed_contact_certificate", {}), MIXED_CONTACT_CERTIFICATE, "mixed contact certificate input")
    assert_file_hash(inputs.get("pareto_report", {}), PARETO_REPORT, "Pareto report input")
    assert_file_hash(inputs.get("pareto_json", {}), PARETO_JSON, "Pareto JSON input")
    assert_file_hash(inputs.get("pareto_candidates", {}), PARETO_CANDIDATES, "Pareto candidates input")
    assert_file_hash(inputs.get("pareto_classes", {}), PARETO_CLASSES, "Pareto classes input")
    assert_file_hash(inputs.get("pareto_tables", {}), PARETO_TABLES, "Pareto tables input")
    assert_file_hash(inputs.get("pareto_certificate", {}), PARETO_CERTIFICATE, "Pareto certificate input")

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_atom_selected_tradeoff_manifest@1":
        raise AssertionError("C985 d20 atom-selected tradeoff manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 atom-selected tradeoff manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 atom-selected tradeoff manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("C985 d20 atom-selected tradeoff missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 atom-selected tradeoff index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 atom-selected tradeoff index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_atom_selected_tradeoff@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "frontier_candidate_ids": witness.get("frontier_candidate_ids"),
        "dominated_candidate_ids": witness.get("dominated_candidate_ids"),
        "frontier_classes": witness.get("frontier_classes"),
        "zero_overhead_cost_transition": witness.get(
            "zero_overhead_cost_transition"
        ),
        "x1_tail_class": witness.get("x1_tail_class"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_aperture_atom_selected_tradeoff()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
