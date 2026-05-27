from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_mixed_contact_atoms import (
        ATOM_CONTACT_COLUMNS,
        CANDIDATE_RESOLUTION_COLUMNS,
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        CLEAN_FIRST_EDGE_ID,
        EDGE_RESOLUTION_COLUMNS,
        MIXED_FIRST_EDGE_IDS,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PARETO_CANDIDATES,
        PARETO_CERTIFICATE,
        PARETO_JSON,
        PARETO_REPORT,
        PARETO_TABLES,
        SELECTED_CANDIDATE_ID,
        STATUS,
        SYMBOLIC_ALPHABET,
        SYMBOLIC_REWRITE_CERTIFICATE,
        SYMBOLIC_REWRITE_REPORT,
        SYMBOLIC_REWRITE_TABLES,
        THEOREM_ID,
        X2_ATOM_ID,
        X2_DETOUR_CERTIFICATE,
        X2_DETOUR_EDGES,
        X2_DETOUR_REPORT,
        X2_DETOUR_TABLES,
        X5_ATOM_ID,
        ZERO_OVERHEAD_CANDIDATE_IDS,
        build_payloads,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_mixed_contact_atoms import (
        ATOM_CONTACT_COLUMNS,
        CANDIDATE_RESOLUTION_COLUMNS,
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        CLEAN_FIRST_EDGE_ID,
        EDGE_RESOLUTION_COLUMNS,
        MIXED_FIRST_EDGE_IDS,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PARETO_CANDIDATES,
        PARETO_CERTIFICATE,
        PARETO_JSON,
        PARETO_REPORT,
        PARETO_TABLES,
        SELECTED_CANDIDATE_ID,
        STATUS,
        SYMBOLIC_ALPHABET,
        SYMBOLIC_REWRITE_CERTIFICATE,
        SYMBOLIC_REWRITE_REPORT,
        SYMBOLIC_REWRITE_TABLES,
        THEOREM_ID,
        X2_ATOM_ID,
        X2_DETOUR_CERTIFICATE,
        X2_DETOUR_EDGES,
        X2_DETOUR_REPORT,
        X2_DETOUR_TABLES,
        X5_ATOM_ID,
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


def validate_c985_d20_signature_boundary_spine_aperture_mixed_contact_atoms() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    mixed_contact_atoms = load_json(
        OUT_DIR / "signature_boundary_spine_aperture_mixed_contact_atoms.json"
    )
    certificate = load_json(
        OUT_DIR / "signature_boundary_spine_aperture_mixed_contact_atoms_certificate.json"
    )
    atom_contacts_csv = (
        OUT_DIR / "aperture_mixed_contact_atom_witnesses.csv"
    ).read_text(encoding="utf-8")
    edge_resolution_csv = (
        OUT_DIR / "aperture_first_contact_edge_resolution.csv"
    ).read_text(encoding="utf-8")
    candidate_resolution_csv = (
        OUT_DIR / "aperture_candidate_atom_resolution.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR / "aperture_mixed_contact_atom_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR / "signature_boundary_spine_aperture_mixed_contact_atoms_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        mixed_contact_atoms
        != expected["signature_boundary_spine_aperture_mixed_contact_atoms"]
    ):
        raise AssertionError("mixed contact atom JSON is not reproducible")
    if atom_contacts_csv != expected["aperture_mixed_contact_atom_witnesses_csv"]:
        raise AssertionError("mixed contact atom witness CSV is not reproducible")
    if edge_resolution_csv != expected["aperture_first_contact_edge_resolution_csv"]:
        raise AssertionError("first-contact edge resolution CSV is not reproducible")
    if candidate_resolution_csv != expected["aperture_candidate_atom_resolution_csv"]:
        raise AssertionError("candidate atom resolution CSV is not reproducible")
    if observables_csv != expected["aperture_mixed_contact_atom_observables_csv"]:
        raise AssertionError("mixed contact atom observable CSV is not reproducible")
    if (
        certificate
        != expected["signature_boundary_spine_aperture_mixed_contact_atoms_certificate"]
    ):
        raise AssertionError("mixed contact atom certificate is not reproducible")

    for name in [
        "atom_contact_table",
        "edge_resolution_table",
        "candidate_resolution_table",
        "observable_table",
    ]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"mixed contact atom table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_mixed_contact_atoms@1":
        raise AssertionError("C985 d20 mixed contact atom report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 mixed contact atom layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 mixed contact atom all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 mixed contact atom checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 mixed contact atom report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 mixed contact atom report is not reproducible")

    missing = sorted(
        key
        for key in expected["report"]["checks"]
        if report.get("checks", {}).get(key) is not True
    )
    if missing:
        raise AssertionError(f"C985 d20 mixed contact atom missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("first_contact_edges") != [CLEAN_FIRST_EDGE_ID, *MIXED_FIRST_EDGE_IDS]:
        raise AssertionError("mixed contact atom first-contact edge set mismatch")
    if witness.get("mixed_first_contact_edges") != MIXED_FIRST_EDGE_IDS:
        raise AssertionError("mixed contact atom mixed edge set mismatch")
    if witness.get("clean_first_contact_edge") != CLEAN_FIRST_EDGE_ID:
        raise AssertionError("mixed contact atom clean edge mismatch")
    if witness.get("edge_shared_atom_map") != {
        "14": [X2_ATOM_ID],
        "39": [X2_ATOM_ID, X5_ATOM_ID],
        "41": [X2_ATOM_ID, X5_ATOM_ID],
    }:
        raise AssertionError("mixed contact atom shared atom map mismatch")
    if witness.get("zero_overhead_candidate_ids") != ZERO_OVERHEAD_CANDIDATE_IDS:
        raise AssertionError("mixed contact atom zero-overhead candidate IDs mismatch")
    if witness.get("candidate_ids_requiring_atom_selector") != [0, 1, 2, 3, 4, 5, 7, 9]:
        raise AssertionError("mixed contact atom selector candidate IDs mismatch")
    if witness.get("pure_x2_zero_overhead_candidate_ids") != []:
        raise AssertionError("mixed contact atom pure zero-overhead candidate mismatch")
    if witness.get("selected_clean_candidate_id") != SELECTED_CANDIDATE_ID:
        raise AssertionError("mixed contact atom selected candidate mismatch")
    atom_reading = witness.get("atom_level_reading", {})
    if atom_reading.get("carrier_mask_quotient_ambiguity") is not True:
        raise AssertionError("mixed contact atom ambiguity reading mismatch")
    if atom_reading.get("x2_atom_witness_exists_on_mixed_edges") is not True:
        raise AssertionError("mixed contact atom x2 witness reading mismatch")
    if atom_reading.get("x5_cowitness_exists_on_mixed_edges") is not True:
        raise AssertionError("mixed contact atom x5 cowitness reading mismatch")

    atom_contact_table = np.asarray(tables["atom_contact_table"], dtype=np.int64)
    edge_resolution_table = np.asarray(tables["edge_resolution_table"], dtype=np.int64)
    candidate_resolution_table = np.asarray(
        tables["candidate_resolution_table"], dtype=np.int64
    )
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if atom_contact_table.shape != (5, len(ATOM_CONTACT_COLUMNS)):
        raise AssertionError("mixed contact atom witness table shape mismatch")
    if edge_resolution_table.shape != (3, len(EDGE_RESOLUTION_COLUMNS)):
        raise AssertionError("mixed contact edge resolution table shape mismatch")
    if candidate_resolution_table.shape != (10, len(CANDIDATE_RESOLUTION_COLUMNS)):
        raise AssertionError("mixed contact candidate resolution table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("mixed contact observable table shape mismatch")
    if edge_resolution_table[:, 0].tolist() != [14, 39, 41]:
        raise AssertionError("mixed contact edge-resolution edge order mismatch")
    if edge_resolution_table[:, 11].tolist() != [128, 524416, 524416]:
        raise AssertionError("mixed contact shared atom bitset mismatch")
    if edge_resolution_table[:, 13].tolist() != [1, 0, 0]:
        raise AssertionError("mixed contact pure x2 edge flags mismatch")
    if edge_resolution_table[:, 14].tolist() != [0, 1, 1]:
        raise AssertionError("mixed contact mixed edge flags mismatch")
    if candidate_resolution_table[:, 14].tolist() != [1, 1, 1, 1, 1, 1, 0, 1, 0, 1]:
        raise AssertionError("mixed contact candidate selector flags mismatch")
    if candidate_resolution_table[:, 15].tolist() != [1, 1, 1, 1, 1, 1, 0, 1, 0, 1]:
        raise AssertionError("mixed contact candidate ambiguity flags mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("pareto_report", {}), PARETO_REPORT, "Pareto report input")
    assert_file_hash(inputs.get("pareto_json", {}), PARETO_JSON, "Pareto JSON input")
    assert_file_hash(inputs.get("pareto_candidates", {}), PARETO_CANDIDATES, "Pareto candidates input")
    assert_file_hash(inputs.get("pareto_tables", {}), PARETO_TABLES, "Pareto tables input")
    assert_file_hash(inputs.get("pareto_certificate", {}), PARETO_CERTIFICATE, "Pareto certificate input")
    assert_file_hash(inputs.get("x2_detour_report", {}), X2_DETOUR_REPORT, "x2 detour report input")
    assert_file_hash(inputs.get("x2_detour_edges", {}), X2_DETOUR_EDGES, "x2 detour edges input")
    assert_file_hash(inputs.get("x2_detour_tables", {}), X2_DETOUR_TABLES, "x2 detour tables input")
    assert_file_hash(inputs.get("x2_detour_certificate", {}), X2_DETOUR_CERTIFICATE, "x2 detour certificate input")
    assert_file_hash(inputs.get("cell_complex_report", {}), CELL_COMPLEX_REPORT, "cell complex report input")
    assert_file_hash(inputs.get("cell_complex_edges", {}), CELL_COMPLEX_EDGES, "cell complex edges input")
    assert_file_hash(inputs.get("cell_complex_tables", {}), CELL_COMPLEX_TABLES, "cell complex tables input")
    assert_file_hash(inputs.get("cell_complex_certificate", {}), CELL_COMPLEX_CERTIFICATE, "cell complex certificate input")
    assert_file_hash(inputs.get("symbolic_rewrite_report", {}), SYMBOLIC_REWRITE_REPORT, "symbolic rewrite report input")
    assert_file_hash(inputs.get("symbolic_alphabet", {}), SYMBOLIC_ALPHABET, "symbolic alphabet input")
    assert_file_hash(inputs.get("symbolic_rewrite_tables", {}), SYMBOLIC_REWRITE_TABLES, "symbolic rewrite tables input")
    assert_file_hash(inputs.get("symbolic_rewrite_certificate", {}), SYMBOLIC_REWRITE_CERTIFICATE, "symbolic rewrite certificate input")

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_mixed_contact_atoms_manifest@1":
        raise AssertionError("C985 d20 mixed contact atom manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 mixed contact atom manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 mixed contact atom manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("C985 d20 mixed contact atom layer missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 mixed contact atom index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 mixed contact atom index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_mixed_contact_atoms@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "edge_shared_atom_map": witness.get("edge_shared_atom_map"),
        "candidate_ids_requiring_atom_selector": witness.get(
            "candidate_ids_requiring_atom_selector"
        ),
        "pure_x2_zero_overhead_candidate_ids": witness.get(
            "pure_x2_zero_overhead_candidate_ids"
        ),
        "atom_level_reading": witness.get("atom_level_reading"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_aperture_mixed_contact_atoms()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
