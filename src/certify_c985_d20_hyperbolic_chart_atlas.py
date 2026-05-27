from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_hyperbolic_chart_atlas import (
        ATLAS_JSON,
        FILTRATION_REPORT,
        FILTRATION_TABLES,
        INDEX_PATH,
        NERVE_JSON,
        NERVE_REPORT,
        NERVE_TABLES,
        OUT_DIR,
        RELATION_GEOMETRY_SIGNATURES,
        STATUS,
        THEOREM_ID,
        TRANSITION_COLUMNS,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_hyperbolic_chart_atlas import (
        ATLAS_JSON,
        FILTRATION_REPORT,
        FILTRATION_TABLES,
        INDEX_PATH,
        NERVE_JSON,
        NERVE_REPORT,
        NERVE_TABLES,
        OUT_DIR,
        RELATION_GEOMETRY_SIGNATURES,
        STATUS,
        THEOREM_ID,
        TRANSITION_COLUMNS,
        build_payloads,
        self_hash,
    )


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


def validate_c985_d20_hyperbolic_chart_atlas() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    atlas = load_json(OUT_DIR / "hyperbolic_chart_atlas.json")
    certificate = load_json(OUT_DIR / "atlas_certificate.json")
    transition_csv = (OUT_DIR / "atlas_transition_maps.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "hyperbolic_chart_atlas_tables.npz", allow_pickle=False)
    selected_chart_ids = np.asarray(tables["selected_chart_ids"], dtype=np.int64)
    selected_incidence = np.asarray(tables["selected_incidence"], dtype=np.int8)
    atom_cover_counts = np.asarray(tables["atom_cover_counts"], dtype=np.int64)
    transition_pair_records = np.asarray(tables["transition_pair_records"], dtype=np.int64)
    ordered_transition_records = np.asarray(tables["ordered_transition_records"], dtype=np.int64)
    transition_cocycle_records = np.asarray(tables["transition_cocycle_records"], dtype=np.int64)
    triple_overlap_atom_ids = np.asarray(tables["triple_overlap_atom_ids"], dtype=np.int64)
    index = load_json(INDEX_PATH)

    if atlas != expected["hyperbolic_chart_atlas"]:
        raise AssertionError("hyperbolic chart atlas JSON is not reproducible")
    if transition_csv != expected["atlas_transition_maps_csv"]:
        raise AssertionError("hyperbolic chart atlas transition CSV is not reproducible")
    if not np.array_equal(selected_chart_ids, expected["selected_chart_ids"]):
        raise AssertionError("hyperbolic chart atlas selected chart ids are not reproducible")
    if not np.array_equal(selected_incidence, expected["selected_incidence"]):
        raise AssertionError("hyperbolic chart atlas selected incidence is not reproducible")
    if not np.array_equal(atom_cover_counts, expected["atom_cover_counts"]):
        raise AssertionError("hyperbolic chart atlas atom cover counts are not reproducible")
    if not np.array_equal(transition_pair_records, expected["transition_pair_records"]):
        raise AssertionError("hyperbolic chart atlas transition pair records are not reproducible")
    if not np.array_equal(ordered_transition_records, expected["ordered_transition_records"]):
        raise AssertionError("hyperbolic chart atlas ordered transitions are not reproducible")
    if not np.array_equal(transition_cocycle_records, expected["transition_cocycle_records"]):
        raise AssertionError("hyperbolic chart atlas cocycle records are not reproducible")
    if not np.array_equal(triple_overlap_atom_ids, expected["triple_overlap_atom_ids"]):
        raise AssertionError("hyperbolic chart atlas triple overlap atoms are not reproducible")
    if certificate != expected["atlas_certificate"]:
        raise AssertionError("hyperbolic chart atlas certificate is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_hyperbolic_chart_atlas@1":
        raise AssertionError("C985 d20 hyperbolic chart atlas report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 hyperbolic chart atlas is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 hyperbolic chart atlas all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 hyperbolic chart atlas checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 hyperbolic chart atlas report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 hyperbolic chart atlas report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "signature_class_nerve_report_certified",
        "landmark_filtration_report_certified",
        "source_chart_count_is_20",
        "exact_minimum_atom_cover_size_is_3",
        "exact_minimum_atom_cover_count_is_4",
        "selected_chart_ids_are_0_2_10",
        "selected_chart_size_sum_is_39",
        "selected_atlas_covers_all_20_atoms",
        "selected_pair_count_is_3",
        "selected_pair_min_atom_intersection_is_6",
        "selected_pair_min_signature_intersection_is_221",
        "selected_pair_full_signature_intersection_count_is_2",
        "undirected_transition_atom_count_is_25",
        "ordered_transition_record_count_is_50",
        "triple_overlap_atom_count_is_6",
        "triple_overlap_signature_count_is_221",
        "triple_overlap_mass_is_344576",
        "atom_cover_histogram_is_7_7_6",
        "unique_atom_count_is_7",
        "transition_rank_displacement_l1_sum_is_125",
        "transition_rank_displacement_max_is_12",
        "transition_cocycle_failure_count_is_0",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 hyperbolic chart atlas missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("minimum_atom_cover_size") != 3:
        raise AssertionError("hyperbolic chart atlas minimum cover size mismatch")
    if witness.get("minimum_atom_cover_count") != 4:
        raise AssertionError("hyperbolic chart atlas minimum cover count mismatch")
    if witness.get("selected_chart_ids") != [0, 2, 10]:
        raise AssertionError("hyperbolic chart atlas selected chart mismatch")
    if witness.get("selected_chart_size_sum") != 39:
        raise AssertionError("hyperbolic chart atlas selected chart size sum mismatch")
    if witness.get("selected_union_atom_count") != 20:
        raise AssertionError("hyperbolic chart atlas selected union atom count mismatch")
    if witness.get("selected_pair_count") != 3:
        raise AssertionError("hyperbolic chart atlas selected pair count mismatch")
    if witness.get("selected_pair_atom_intersection_min") != 6:
        raise AssertionError("hyperbolic chart atlas selected pair atom floor mismatch")
    if witness.get("selected_pair_signature_intersection_min") != 221:
        raise AssertionError("hyperbolic chart atlas selected pair signature floor mismatch")
    if witness.get("selected_pair_full_signature_intersection_count") != 2:
        raise AssertionError("hyperbolic chart atlas full-signature overlap count mismatch")
    if witness.get("undirected_transition_atom_count") != 25:
        raise AssertionError("hyperbolic chart atlas undirected transition count mismatch")
    if witness.get("ordered_transition_record_count") != 50:
        raise AssertionError("hyperbolic chart atlas ordered transition count mismatch")
    if witness.get("triple_overlap_atom_ids") != [1, 4, 7, 11, 12, 19]:
        raise AssertionError("hyperbolic chart atlas triple overlap atoms mismatch")
    if witness.get("triple_overlap_signature_count") != 221:
        raise AssertionError("hyperbolic chart atlas triple overlap signature count mismatch")
    if witness.get("triple_overlap_mass") != 344576:
        raise AssertionError("hyperbolic chart atlas triple overlap mass mismatch")
    if witness.get("unique_atom_count") != 7:
        raise AssertionError("hyperbolic chart atlas unique atom count mismatch")
    if witness.get("transition_rank_displacement_l1_sum") != 125:
        raise AssertionError("hyperbolic chart atlas rank displacement L1 mismatch")
    if witness.get("transition_rank_displacement_max") != 12:
        raise AssertionError("hyperbolic chart atlas max rank displacement mismatch")
    if witness.get("transition_cocycle_failure_count") != 0:
        raise AssertionError("hyperbolic chart atlas cocycle failure mismatch")

    if selected_chart_ids.shape != (3,):
        raise AssertionError("hyperbolic chart atlas selected ids shape mismatch")
    if selected_incidence.shape != (3, 20):
        raise AssertionError("hyperbolic chart atlas selected incidence shape mismatch")
    if atom_cover_counts.shape != (20,):
        raise AssertionError("hyperbolic chart atlas atom cover count shape mismatch")
    if transition_pair_records.shape != (3, 8):
        raise AssertionError("hyperbolic chart atlas transition pair shape mismatch")
    if ordered_transition_records.shape != (50, len(TRANSITION_COLUMNS)):
        raise AssertionError("hyperbolic chart atlas ordered transition shape mismatch")
    if transition_cocycle_records.shape != (6, 5):
        raise AssertionError("hyperbolic chart atlas cocycle record shape mismatch")
    if triple_overlap_atom_ids.shape != (6,):
        raise AssertionError("hyperbolic chart atlas triple overlap shape mismatch")
    if int(selected_incidence.sum()) != 39:
        raise AssertionError("hyperbolic chart atlas selected incidence sum mismatch")
    if int(np.count_nonzero(atom_cover_counts == 1)) != 7:
        raise AssertionError("hyperbolic chart atlas unique coverage count mismatch")
    if int(np.count_nonzero(atom_cover_counts == 2)) != 7:
        raise AssertionError("hyperbolic chart atlas double coverage count mismatch")
    if int(np.count_nonzero(atom_cover_counts == 3)) != 6:
        raise AssertionError("hyperbolic chart atlas triple coverage count mismatch")
    if int(transition_pair_records[:, 3].min()) != 221:
        raise AssertionError("hyperbolic chart atlas pair signature floor mismatch")
    if int(np.count_nonzero(transition_pair_records[:, 3] == 233)) != 2:
        raise AssertionError("hyperbolic chart atlas full pair signature count mismatch")
    if int(np.count_nonzero(transition_cocycle_records[:, 4])) != 0:
        raise AssertionError("hyperbolic chart atlas nonzero cocycle detected")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("signature_class_nerve_report", {}), NERVE_REPORT, "nerve report input")
    assert_file_hash(inputs.get("signature_class_nerve", {}), NERVE_JSON, "nerve JSON input")
    assert_file_hash(inputs.get("signature_class_nerve_tables", {}), NERVE_TABLES, "nerve tables input")
    assert_file_hash(inputs.get("filtration_report", {}), FILTRATION_REPORT, "filtration report input")
    assert_file_hash(inputs.get("filtration_tables", {}), FILTRATION_TABLES, "filtration tables input")
    assert_file_hash(inputs.get("boundary_atlas", {}), ATLAS_JSON, "atlas input")
    assert_file_hash(
        inputs.get("relation_geometry_signatures", {}),
        RELATION_GEOMETRY_SIGNATURES,
        "relation signatures input",
    )

    if manifest.get("schema") != "c985.proof_obligation.d20_hyperbolic_chart_atlas_manifest@1":
        raise AssertionError("C985 d20 hyperbolic chart atlas manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 hyperbolic chart atlas manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 hyperbolic chart atlas manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 d20 hyperbolic chart atlas missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 hyperbolic chart atlas index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 hyperbolic chart atlas index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_hyperbolic_chart_atlas@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "minimum_atom_cover_size": witness.get("minimum_atom_cover_size"),
        "minimum_atom_cover_count": witness.get("minimum_atom_cover_count"),
        "selected_chart_ids": witness.get("selected_chart_ids"),
        "selected_chart_size_sum": witness.get("selected_chart_size_sum"),
        "selected_pair_signature_intersection_min": witness.get(
            "selected_pair_signature_intersection_min"
        ),
        "ordered_transition_record_count": witness.get("ordered_transition_record_count"),
        "triple_overlap_atom_ids": witness.get("triple_overlap_atom_ids"),
        "triple_overlap_signature_count": witness.get("triple_overlap_signature_count"),
        "transition_cocycle_failure_count": witness.get("transition_cocycle_failure_count"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_hyperbolic_chart_atlas()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
