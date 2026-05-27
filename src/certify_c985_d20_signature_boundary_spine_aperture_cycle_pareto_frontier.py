from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_cycle_pareto_frontier import (
        CLEAN_DETOUR_CERTIFICATE,
        CLEAN_DETOUR_CHOICES,
        CLEAN_DETOUR_JSON,
        CLEAN_DETOUR_REPORT,
        CLEAN_DETOUR_TABLES,
        DOMINATED_CANDIDATE_IDS,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PARETO_CANDIDATE_COLUMNS,
        PARETO_CANDIDATE_IDS,
        PARETO_CLASS_COLUMNS,
        RANKING_CANDIDATES,
        RANKING_CERTIFICATE,
        RANKING_JSON,
        RANKING_OBSERVABLES,
        RANKING_REPORT,
        RANKING_TABLES,
        SELECTED_CANDIDATE_ID,
        STATUS,
        THEOREM_ID,
        TYPED_CORRIDOR_CERTIFICATE,
        TYPED_CORRIDOR_EDGES,
        TYPED_CORRIDOR_REPORT,
        TYPED_CORRIDOR_TABLES,
        X2_DETOUR_CERTIFICATE,
        X2_DETOUR_EDGES,
        X2_DETOUR_REPORT,
        X2_DETOUR_RETURNS,
        X2_DETOUR_TABLES,
        build_payloads,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_cycle_pareto_frontier import (
        CLEAN_DETOUR_CERTIFICATE,
        CLEAN_DETOUR_CHOICES,
        CLEAN_DETOUR_JSON,
        CLEAN_DETOUR_REPORT,
        CLEAN_DETOUR_TABLES,
        DOMINATED_CANDIDATE_IDS,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PARETO_CANDIDATE_COLUMNS,
        PARETO_CANDIDATE_IDS,
        PARETO_CLASS_COLUMNS,
        RANKING_CANDIDATES,
        RANKING_CERTIFICATE,
        RANKING_JSON,
        RANKING_OBSERVABLES,
        RANKING_REPORT,
        RANKING_TABLES,
        SELECTED_CANDIDATE_ID,
        STATUS,
        THEOREM_ID,
        TYPED_CORRIDOR_CERTIFICATE,
        TYPED_CORRIDOR_EDGES,
        TYPED_CORRIDOR_REPORT,
        TYPED_CORRIDOR_TABLES,
        X2_DETOUR_CERTIFICATE,
        X2_DETOUR_EDGES,
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


def validate_c985_d20_signature_boundary_spine_aperture_cycle_pareto_frontier() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    pareto = load_json(
        OUT_DIR / "signature_boundary_spine_aperture_cycle_pareto_frontier.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_cycle_pareto_frontier_certificate.json"
    )
    candidates_csv = (OUT_DIR / "aperture_cycle_pareto_candidates.csv").read_text(
        encoding="utf-8"
    )
    classes_csv = (OUT_DIR / "aperture_cycle_pareto_classes.csv").read_text(
        encoding="utf-8"
    )
    observables_csv = (OUT_DIR / "aperture_cycle_pareto_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(
        OUT_DIR / "signature_boundary_spine_aperture_cycle_pareto_frontier_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if pareto != expected["signature_boundary_spine_aperture_cycle_pareto_frontier"]:
        raise AssertionError("aperture cycle Pareto JSON is not reproducible")
    if candidates_csv != expected["aperture_cycle_pareto_candidates_csv"]:
        raise AssertionError("aperture cycle Pareto candidate CSV is not reproducible")
    if classes_csv != expected["aperture_cycle_pareto_classes_csv"]:
        raise AssertionError("aperture cycle Pareto class CSV is not reproducible")
    if observables_csv != expected["aperture_cycle_pareto_observables_csv"]:
        raise AssertionError("aperture cycle Pareto observable CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_cycle_pareto_frontier_certificate"
        ]
    ):
        raise AssertionError("aperture cycle Pareto certificate is not reproducible")

    for name in ["candidate_table", "class_table", "observable_table"]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"aperture cycle Pareto table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_cycle_pareto_frontier@1":
        raise AssertionError("C985 d20 aperture cycle Pareto report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 aperture cycle Pareto frontier is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 aperture cycle Pareto all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 aperture cycle Pareto checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 aperture cycle Pareto report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 aperture cycle Pareto report is not reproducible")

    missing = sorted(
        key
        for key in expected["report"]["checks"]
        if report.get("checks", {}).get(key) is not True
    )
    if missing:
        raise AssertionError(f"C985 d20 aperture cycle Pareto missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("candidate_count") != 10:
        raise AssertionError("aperture cycle Pareto candidate count mismatch")
    if witness.get("pareto_candidate_ids") != PARETO_CANDIDATE_IDS:
        raise AssertionError("aperture cycle Pareto frontier candidate IDs mismatch")
    if witness.get("dominated_candidate_ids") != DOMINATED_CANDIDATE_IDS:
        raise AssertionError("aperture cycle Pareto dominated candidate IDs mismatch")
    if witness.get("selected_candidate", {}).get("candidate_id") != SELECTED_CANDIDATE_ID:
        raise AssertionError("aperture cycle Pareto selected candidate mismatch")
    if witness.get("selected_candidate", {}).get("typed_boundary_cost") != 0:
        raise AssertionError("aperture cycle Pareto selected typed cost mismatch")
    if witness.get("selected_candidate", {}).get("trace_detour_overhead") != 3:
        raise AssertionError("aperture cycle Pareto selected overhead mismatch")
    if witness.get("selected_candidate", {}).get("signature_valley_depth") != 37:
        raise AssertionError("aperture cycle Pareto selected valley mismatch")

    pareto_classes = witness.get("pareto_classes", [])
    if len(pareto_classes) != 5:
        raise AssertionError("aperture cycle Pareto class count mismatch")
    frontier_classes = [
        row for row in pareto_classes if row.get("pareto_frontier_class") is True
    ]
    if [row.get("class_code") for row in frontier_classes] != [0, 1]:
        raise AssertionError("aperture cycle Pareto frontier class IDs mismatch")
    if frontier_classes[0].get("candidate_count") != 6:
        raise AssertionError("aperture cycle Pareto geodesic class count mismatch")
    if frontier_classes[0].get("typed_boundary_cost") != 2:
        raise AssertionError("aperture cycle Pareto geodesic typed cost mismatch")
    if frontier_classes[1].get("representative_candidate_id") != SELECTED_CANDIDATE_ID:
        raise AssertionError("aperture cycle Pareto clean x1 representative mismatch")
    if frontier_classes[1].get("typed_boundary_cost") != 0:
        raise AssertionError("aperture cycle Pareto clean x1 typed cost mismatch")

    candidate_table = np.asarray(tables["candidate_table"], dtype=np.int64)
    class_table = np.asarray(tables["class_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if candidate_table.shape != (10, len(PARETO_CANDIDATE_COLUMNS)):
        raise AssertionError("aperture cycle Pareto candidate table shape mismatch")
    if class_table.shape != (5, len(PARETO_CLASS_COLUMNS)):
        raise AssertionError("aperture cycle Pareto class table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("aperture cycle Pareto observable table shape mismatch")
    if candidate_table[:, 19].tolist() != [2, 2, 2, 2, 2, 2, 0, 1, 1, 2]:
        raise AssertionError("aperture cycle Pareto typed cost vector mismatch")
    if candidate_table[:, 22].tolist() != [1, 1, 1, 1, 1, 1, 1, 0, 0, 0]:
        raise AssertionError("aperture cycle Pareto frontier flags mismatch")
    if candidate_table[:, 23].tolist() != [0, 0, 0, 0, 0, 0, 0, 1, 1, 1]:
        raise AssertionError("aperture cycle Pareto dominated flags mismatch")
    if class_table[:, 0].tolist() != [0, 1, 2, 3, 4]:
        raise AssertionError("aperture cycle Pareto class code order mismatch")
    if class_table[:, 2].tolist() != [6, 1, 1, 1, 1]:
        raise AssertionError("aperture cycle Pareto class sizes mismatch")
    if class_table[:, 3].tolist() != [1, 1, 0, 0, 0]:
        raise AssertionError("aperture cycle Pareto class frontier flags mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("ranking_report", {}), RANKING_REPORT, "ranking report input")
    assert_file_hash(inputs.get("ranking_json", {}), RANKING_JSON, "ranking JSON input")
    assert_file_hash(inputs.get("ranking_candidates", {}), RANKING_CANDIDATES, "ranking candidates input")
    assert_file_hash(inputs.get("ranking_observables", {}), RANKING_OBSERVABLES, "ranking observables input")
    assert_file_hash(inputs.get("ranking_tables", {}), RANKING_TABLES, "ranking tables input")
    assert_file_hash(inputs.get("ranking_certificate", {}), RANKING_CERTIFICATE, "ranking certificate input")
    assert_file_hash(inputs.get("x2_detour_report", {}), X2_DETOUR_REPORT, "x2 detour report input")
    assert_file_hash(inputs.get("x2_detour_edges", {}), X2_DETOUR_EDGES, "x2 detour edges input")
    assert_file_hash(inputs.get("x2_detour_returns", {}), X2_DETOUR_RETURNS, "x2 detour returns input")
    assert_file_hash(inputs.get("x2_detour_tables", {}), X2_DETOUR_TABLES, "x2 detour tables input")
    assert_file_hash(inputs.get("x2_detour_certificate", {}), X2_DETOUR_CERTIFICATE, "x2 detour certificate input")
    assert_file_hash(inputs.get("clean_detour_report", {}), CLEAN_DETOUR_REPORT, "clean detour report input")
    assert_file_hash(inputs.get("clean_detour_json", {}), CLEAN_DETOUR_JSON, "clean detour JSON input")
    assert_file_hash(inputs.get("clean_detour_choices", {}), CLEAN_DETOUR_CHOICES, "clean detour choices input")
    assert_file_hash(inputs.get("clean_detour_tables", {}), CLEAN_DETOUR_TABLES, "clean detour tables input")
    assert_file_hash(inputs.get("clean_detour_certificate", {}), CLEAN_DETOUR_CERTIFICATE, "clean detour certificate input")
    assert_file_hash(inputs.get("typed_corridor_report", {}), TYPED_CORRIDOR_REPORT, "typed corridor report input")
    assert_file_hash(inputs.get("typed_corridor_edges", {}), TYPED_CORRIDOR_EDGES, "typed corridor edges input")
    assert_file_hash(inputs.get("typed_corridor_tables", {}), TYPED_CORRIDOR_TABLES, "typed corridor tables input")
    assert_file_hash(inputs.get("typed_corridor_certificate", {}), TYPED_CORRIDOR_CERTIFICATE, "typed corridor certificate input")

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_cycle_pareto_frontier_manifest@1":
        raise AssertionError("C985 d20 aperture cycle Pareto manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 aperture cycle Pareto manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 aperture cycle Pareto manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("C985 d20 aperture cycle Pareto missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 aperture cycle Pareto index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 aperture cycle Pareto index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_cycle_pareto_frontier@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "pareto_candidate_ids": witness.get("pareto_candidate_ids"),
        "dominated_candidate_ids": witness.get("dominated_candidate_ids"),
        "selected_candidate": witness.get("selected_candidate"),
        "pareto_classes": witness.get("pareto_classes"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_aperture_cycle_pareto_frontier()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
