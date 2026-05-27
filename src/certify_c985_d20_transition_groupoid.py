from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_transition_groupoid import (
        ARROW_COLUMNS,
        ASSOCIATOR_ORACLE,
        ASSOCIATOR_REPORT,
        ASSOCIATOR_SAMPLES,
        CHART_ATLAS_JSON,
        CHART_ATLAS_REPORT,
        CHART_ATLAS_TABLES,
        COMPOSITION_COLUMNS,
        CYCLE_COLUMNS,
        INDEX_PATH,
        INVERSE_COLUMNS,
        OUT_DIR,
        PENTAGON_NORMAL_FORM,
        PENTAGON_REPORT,
        PENTAGON_SAMPLES,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_transition_groupoid import (
        ARROW_COLUMNS,
        ASSOCIATOR_ORACLE,
        ASSOCIATOR_REPORT,
        ASSOCIATOR_SAMPLES,
        CHART_ATLAS_JSON,
        CHART_ATLAS_REPORT,
        CHART_ATLAS_TABLES,
        COMPOSITION_COLUMNS,
        CYCLE_COLUMNS,
        INDEX_PATH,
        INVERSE_COLUMNS,
        OUT_DIR,
        PENTAGON_NORMAL_FORM,
        PENTAGON_REPORT,
        PENTAGON_SAMPLES,
        STATUS,
        THEOREM_ID,
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


def validate_c985_d20_transition_groupoid() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    groupoid = load_json(OUT_DIR / "transition_groupoid.json")
    certificate = load_json(OUT_DIR / "transition_groupoid_certificate.json")
    cycles_csv = (OUT_DIR / "transition_groupoid_cycles.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "transition_groupoid_tables.npz", allow_pickle=False)
    ordered_transition_records = np.asarray(tables["ordered_transition_records"], dtype=np.int64)
    inverse_loop_records = np.asarray(tables["inverse_loop_records"], dtype=np.int64)
    composition_records = np.asarray(tables["composition_records"], dtype=np.int64)
    cycle_records = np.asarray(tables["cycle_records"], dtype=np.int64)
    index = load_json(INDEX_PATH)

    if groupoid != expected["transition_groupoid"]:
        raise AssertionError("transition groupoid JSON is not reproducible")
    if cycles_csv != expected["transition_groupoid_cycles_csv"]:
        raise AssertionError("transition groupoid cycle CSV is not reproducible")
    if not np.array_equal(ordered_transition_records, expected["ordered_transition_records"]):
        raise AssertionError("transition groupoid ordered transitions are not reproducible")
    if not np.array_equal(inverse_loop_records, expected["inverse_loop_records"]):
        raise AssertionError("transition groupoid inverse loops are not reproducible")
    if not np.array_equal(composition_records, expected["composition_records"]):
        raise AssertionError("transition groupoid composition records are not reproducible")
    if not np.array_equal(cycle_records, expected["cycle_records"]):
        raise AssertionError("transition groupoid cycle records are not reproducible")
    if certificate != expected["transition_groupoid_certificate"]:
        raise AssertionError("transition groupoid certificate is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_transition_groupoid@1":
        raise AssertionError("C985 d20 transition groupoid report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 transition groupoid is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 transition groupoid all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 transition groupoid checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 transition groupoid report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 transition groupoid report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "chart_atlas_report_certified",
        "associator_oracle_report_certified",
        "pentagon_normal_form_report_certified",
        "selected_chart_ids_are_0_2_10",
        "transition_arrow_count_is_50",
        "transition_pair_count_is_3",
        "triple_overlap_atom_count_is_6",
        "inverse_loop_record_count_is_50",
        "inverse_loop_failures_are_zero",
        "composition_record_count_is_36",
        "composition_failures_are_zero",
        "cycle_record_count_is_36",
        "cycle_holonomy_failures_are_zero",
        "atlas_cocycle_failures_are_zero",
        "associator_sample_rebracketing_count_is_1970",
        "associator_sample_rebracketing_failures_are_zero",
        "pentagon_exact_chain_count_matches_final_certificate",
        "pentagon_top_and_bottom_paths_share_normal_form",
        "pentagon_chain_normal_form_is_typed_length_four",
        "groupoid_and_pentagon_both_have_zero_path_defects",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 transition groupoid missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("object_count") != 3:
        raise AssertionError("transition groupoid object count mismatch")
    if witness.get("selected_chart_ids") != [0, 2, 10]:
        raise AssertionError("transition groupoid selected chart ids mismatch")
    if witness.get("arrow_count") != 50:
        raise AssertionError("transition groupoid arrow count mismatch")
    if witness.get("inverse_loop_record_count") != 50:
        raise AssertionError("transition groupoid inverse loop count mismatch")
    if witness.get("inverse_loop_failure_count") != 0:
        raise AssertionError("transition groupoid inverse loop failures mismatch")
    if witness.get("composition_record_count") != 36:
        raise AssertionError("transition groupoid composition record count mismatch")
    if witness.get("composition_failure_count") != 0:
        raise AssertionError("transition groupoid composition failures mismatch")
    if witness.get("cycle_record_count") != 36:
        raise AssertionError("transition groupoid cycle count mismatch")
    if witness.get("cycle_holonomy_failure_count") != 0:
        raise AssertionError("transition groupoid cycle holonomy failures mismatch")
    if witness.get("triple_overlap_atom_ids") != [1, 4, 7, 11, 12, 19]:
        raise AssertionError("transition groupoid triple overlap mismatch")
    if witness.get("associator_sample_rebracketing_count") != 1970:
        raise AssertionError("transition groupoid associator sample count mismatch")
    if witness.get("associator_sample_rebracketing_failures") != 0:
        raise AssertionError("transition groupoid associator sample failures mismatch")
    if witness.get("pentagon_exact_length_four_chain_count") != 16837352591360:
        raise AssertionError("transition groupoid pentagon chain count mismatch")
    if witness.get("pentagon_chain_normal_form") != "typed_length_four_chain(x0,x1,x2,x3,x4)":
        raise AssertionError("transition groupoid pentagon normal form mismatch")

    if ordered_transition_records.shape != (50, len(ARROW_COLUMNS)):
        raise AssertionError("transition groupoid ordered transition shape mismatch")
    if inverse_loop_records.shape != (50, len(INVERSE_COLUMNS)):
        raise AssertionError("transition groupoid inverse loop shape mismatch")
    if composition_records.shape != (36, len(COMPOSITION_COLUMNS)):
        raise AssertionError("transition groupoid composition shape mismatch")
    if cycle_records.shape != (36, len(CYCLE_COLUMNS)):
        raise AssertionError("transition groupoid cycle shape mismatch")
    if int(np.count_nonzero(inverse_loop_records[:, 5])) != 0:
        raise AssertionError("transition groupoid nonzero inverse defect")
    if int(np.count_nonzero(composition_records[:, 6])) != 0:
        raise AssertionError("transition groupoid nonzero composition defect")
    if int(np.count_nonzero(cycle_records[:, 4])) != 0:
        raise AssertionError("transition groupoid nonzero cycle holonomy")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("chart_atlas_report", {}), CHART_ATLAS_REPORT, "chart atlas report input")
    assert_file_hash(inputs.get("chart_atlas", {}), CHART_ATLAS_JSON, "chart atlas JSON input")
    assert_file_hash(inputs.get("chart_atlas_tables", {}), CHART_ATLAS_TABLES, "chart atlas tables input")
    assert_file_hash(inputs.get("associator_report", {}), ASSOCIATOR_REPORT, "associator report input")
    assert_file_hash(inputs.get("associator_oracle", {}), ASSOCIATOR_ORACLE, "associator oracle input")
    assert_file_hash(inputs.get("associator_samples", {}), ASSOCIATOR_SAMPLES, "associator samples input")
    assert_file_hash(inputs.get("pentagon_report", {}), PENTAGON_REPORT, "pentagon report input")
    assert_file_hash(inputs.get("pentagon_normal_form", {}), PENTAGON_NORMAL_FORM, "pentagon normal form input")
    assert_file_hash(inputs.get("pentagon_samples", {}), PENTAGON_SAMPLES, "pentagon samples input")

    if manifest.get("schema") != "c985.proof_obligation.d20_transition_groupoid_manifest@1":
        raise AssertionError("C985 d20 transition groupoid manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 transition groupoid manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 transition groupoid manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 d20 transition groupoid missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 transition groupoid index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 transition groupoid index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_transition_groupoid@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "object_count": witness.get("object_count"),
        "selected_chart_ids": witness.get("selected_chart_ids"),
        "arrow_count": witness.get("arrow_count"),
        "inverse_loop_failure_count": witness.get("inverse_loop_failure_count"),
        "composition_failure_count": witness.get("composition_failure_count"),
        "cycle_holonomy_failure_count": witness.get("cycle_holonomy_failure_count"),
        "associator_sample_rebracketing_count": witness.get("associator_sample_rebracketing_count"),
        "pentagon_exact_length_four_chain_count": witness.get("pentagon_exact_length_four_chain_count"),
        "pentagon_chain_normal_form": witness.get("pentagon_chain_normal_form"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_transition_groupoid()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
