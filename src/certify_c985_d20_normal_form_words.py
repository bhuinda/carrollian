from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_normal_form_words import (
        ATLAS_JSON,
        ATLAS_NPZ,
        ATLAS_REPORT,
        CHART_ATLAS_JSON,
        CHART_ATLAS_REPORT,
        GEOMETRY_REPORT,
        GROUPOID_JSON,
        GROUPOID_REPORT,
        GROUPOID_TABLES,
        INDEX_PATH,
        OBJECT_SECTOR_CUBES,
        OUT_DIR,
        RELATION_GEOMETRY_SIGNATURES,
        STATUS,
        THEOREM_ID,
        WORD_COLUMNS,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_normal_form_words import (
        ATLAS_JSON,
        ATLAS_NPZ,
        ATLAS_REPORT,
        CHART_ATLAS_JSON,
        CHART_ATLAS_REPORT,
        GEOMETRY_REPORT,
        GROUPOID_JSON,
        GROUPOID_REPORT,
        GROUPOID_TABLES,
        INDEX_PATH,
        OBJECT_SECTOR_CUBES,
        OUT_DIR,
        RELATION_GEOMETRY_SIGNATURES,
        STATUS,
        THEOREM_ID,
        WORD_COLUMNS,
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


def validate_c985_d20_normal_form_words() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    words = load_json(OUT_DIR / "normal_form_words.json")
    certificate = load_json(OUT_DIR / "normal_form_words_certificate.json")
    words_csv = (OUT_DIR / "normal_form_words.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "normal_form_word_tables.npz", allow_pickle=False)
    word_table = np.asarray(tables["normal_form_word_table"], dtype=np.int64)
    atom_table = np.asarray(tables["normal_form_atom_table"], dtype=np.int64)
    index = load_json(INDEX_PATH)

    if words != expected["normal_form_words"]:
        raise AssertionError("d20 normal-form words JSON is not reproducible")
    if words_csv != expected["normal_form_words_csv"]:
        raise AssertionError("d20 normal-form words CSV is not reproducible")
    if not np.array_equal(word_table, expected["normal_form_word_table"]):
        raise AssertionError("d20 normal-form word table is not reproducible")
    if not np.array_equal(atom_table, expected["normal_form_atom_table"]):
        raise AssertionError("d20 normal-form atom table is not reproducible")
    if certificate != expected["normal_form_words_certificate"]:
        raise AssertionError("d20 normal-form words certificate is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_normal_form_words@1":
        raise AssertionError("C985 d20 normal-form words report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 normal-form words are not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 normal-form words all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 normal-form words checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 normal-form words report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 normal-form words report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "transition_groupoid_report_certified",
        "chart_atlas_report_certified",
        "boundary_atlas_report_certified",
        "tensor_geometry_report_certified",
        "cycle_record_count_is_36",
        "normal_form_word_count_is_36",
        "unique_cycle_atom_count_is_6",
        "all_cycle_delta_sums_are_zero",
        "each_unique_atom_appears_in_6_words",
        "word_sector_coverage_histogram_is_24_five_12_six",
        "unique_atom_sector_coverage_histogram_is_4_five_2_six",
        "object_sector_cube_recomputes_atlas_support",
        "object_sector_cube_recomputes_atlas_mass",
        "unique_atom_signature_class_count_is_221",
        "unique_atom_tensor_path_support_is_216432",
        "unique_atom_tensor_path_mass_is_344576",
        "unique_atom_mass_matches_chart_atlas_triple_overlap",
        "word_multiplicity_mass_is_6_times_unique_mass",
        "word_multiplicity_support_is_6_times_unique_support",
        "groupoid_cycle_holonomy_failures_are_zero",
        "normal_words_compare_to_pentagon_normal_form",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 normal-form words missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("word_count") != 36:
        raise AssertionError("normal-form word count mismatch")
    if witness.get("unique_atom_count") != 6:
        raise AssertionError("normal-form unique atom count mismatch")
    if witness.get("unique_atom_ids") != [1, 4, 7, 11, 12, 19]:
        raise AssertionError("normal-form unique atoms mismatch")
    if witness.get("unique_atom_signature_class_count") != 221:
        raise AssertionError("normal-form signature class count mismatch")
    if witness.get("unique_atom_tensor_path_support") != 216432:
        raise AssertionError("normal-form unique atom support mismatch")
    if witness.get("unique_atom_tensor_path_coefficient_mass") != 344576:
        raise AssertionError("normal-form unique atom mass mismatch")
    if witness.get("word_multiplicity_tensor_path_support") != 1298592:
        raise AssertionError("normal-form word multiplicity support mismatch")
    if witness.get("word_multiplicity_tensor_path_coefficient_mass") != 2067456:
        raise AssertionError("normal-form word multiplicity mass mismatch")
    if witness.get("groupoid_cycle_holonomy_failure_count") != 0:
        raise AssertionError("normal-form groupoid holonomy mismatch")
    if witness.get("pentagon_chain_normal_form") != "typed_length_four_chain(x0,x1,x2,x3,x4)":
        raise AssertionError("normal-form pentagon comparison mismatch")

    if word_table.shape != (36, len(WORD_COLUMNS)):
        raise AssertionError("normal-form word table shape mismatch")
    if atom_table.shape != (6, 8):
        raise AssertionError("normal-form atom table shape mismatch")
    if int(np.count_nonzero(word_table[:, 8])) != 0:
        raise AssertionError("normal-form words have nonzero cycle sums")
    if int(np.count_nonzero(atom_table[:, 2] != atom_table[:, 3])) != 0:
        raise AssertionError("normal-form support does not match atlas")
    if int(np.count_nonzero(atom_table[:, 4] != atom_table[:, 5])) != 0:
        raise AssertionError("normal-form mass does not match atlas")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("transition_groupoid_report", {}), GROUPOID_REPORT, "groupoid report input")
    assert_file_hash(inputs.get("transition_groupoid", {}), GROUPOID_JSON, "groupoid JSON input")
    assert_file_hash(inputs.get("transition_groupoid_tables", {}), GROUPOID_TABLES, "groupoid tables input")
    assert_file_hash(inputs.get("chart_atlas_report", {}), CHART_ATLAS_REPORT, "chart atlas report input")
    assert_file_hash(inputs.get("chart_atlas", {}), CHART_ATLAS_JSON, "chart atlas JSON input")
    assert_file_hash(inputs.get("boundary_atlas_report", {}), ATLAS_REPORT, "boundary atlas report input")
    assert_file_hash(inputs.get("boundary_atlas", {}), ATLAS_JSON, "boundary atlas JSON input")
    assert_file_hash(inputs.get("boundary_atlas_npz", {}), ATLAS_NPZ, "boundary atlas NPZ input")
    assert_file_hash(inputs.get("tensor_geometry_report", {}), GEOMETRY_REPORT, "tensor geometry report input")
    assert_file_hash(inputs.get("object_sector_cubes", {}), OBJECT_SECTOR_CUBES, "object sector cubes input")
    assert_file_hash(
        inputs.get("relation_geometry_signatures", {}),
        RELATION_GEOMETRY_SIGNATURES,
        "relation signatures input",
    )

    if manifest.get("schema") != "c985.proof_obligation.d20_normal_form_words_manifest@1":
        raise AssertionError("C985 d20 normal-form words manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 normal-form words manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 normal-form words manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 d20 normal-form words missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 normal-form words index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 normal-form words index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_normal_form_words@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "word_count": witness.get("word_count"),
        "unique_atom_ids": witness.get("unique_atom_ids"),
        "unique_atom_signature_class_count": witness.get("unique_atom_signature_class_count"),
        "unique_atom_tensor_path_support": witness.get("unique_atom_tensor_path_support"),
        "unique_atom_tensor_path_coefficient_mass": witness.get(
            "unique_atom_tensor_path_coefficient_mass"
        ),
        "word_sector_coverage_histogram": witness.get("word_sector_coverage_histogram"),
        "groupoid_cycle_holonomy_failure_count": witness.get("groupoid_cycle_holonomy_failure_count"),
        "pentagon_chain_normal_form": witness.get("pentagon_chain_normal_form"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_normal_form_words()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
