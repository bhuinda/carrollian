from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_poincare_embedding import (
        ATLAS_JSON,
        ATLAS_REPORT,
        COORDINATE_COLUMNS,
        GRAPH_JSON,
        GRAPH_METRICS,
        GRAPH_REPORT,
        INDEX_PATH,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_poincare_embedding import (
        ATLAS_JSON,
        ATLAS_REPORT,
        COORDINATE_COLUMNS,
        GRAPH_JSON,
        GRAPH_METRICS,
        GRAPH_REPORT,
        INDEX_PATH,
        OUT_DIR,
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


def validate_c985_d20_poincare_embedding() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    embedding = load_json(OUT_DIR / "poincare_embedding.json")
    certificate = load_json(OUT_DIR / "embedding_certificate.json")
    coordinates_csv = (OUT_DIR / "poincare_coordinates.csv").read_text(encoding="utf-8")
    svg = (OUT_DIR / "poincare_embedding.svg").read_text(encoding="utf-8")
    embedding_npz = np.load(OUT_DIR / "poincare_embedding.npz", allow_pickle=False)
    coordinate_table = np.asarray(embedding_npz["coordinate_table"], dtype=np.float64)
    poincare_distances = np.asarray(embedding_npz["poincare_distances"], dtype=np.float64)
    target_metric = np.asarray(embedding_npz["target_metric"], dtype=np.float64)
    index = load_json(INDEX_PATH)

    if embedding != expected["poincare_embedding"]:
        raise AssertionError("Poincare embedding JSON is not reproducible")
    if coordinates_csv != expected["poincare_coordinates_csv"]:
        raise AssertionError("Poincare coordinate CSV is not reproducible")
    if svg != expected["poincare_embedding_svg"]:
        raise AssertionError("Poincare embedding SVG is not reproducible")
    if not np.allclose(coordinate_table, expected["coordinate_table"], rtol=0.0, atol=1e-12):
        raise AssertionError("Poincare coordinate table is not reproducible")
    if not np.allclose(poincare_distances, expected["poincare_distances"], rtol=0.0, atol=1e-12):
        raise AssertionError("Poincare distance matrix is not reproducible")
    if not np.allclose(target_metric, expected["target_metric"], rtol=0.0, atol=1e-12):
        raise AssertionError("Poincare target metric is not reproducible")
    if certificate != expected["embedding_certificate"]:
        raise AssertionError("Poincare embedding certificate is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_poincare_embedding@1":
        raise AssertionError("C985 d20 Poincare embedding report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 Poincare embedding is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 Poincare embedding all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 Poincare embedding checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 Poincare embedding report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 Poincare embedding report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "hyperbolic_graph_report_certified",
        "boundary_atlas_report_certified",
        "affinity_distance_matrix_shape_is_20_by_20",
        "leading_two_mds_eigenvalues_are_positive",
        "selected_radius_step_is_182",
        "selected_radius_is_0_91",
        "all_points_inside_open_poincare_disk",
        "max_embedding_radius_is_0_91",
        "poincare_distance_matrix_is_20_by_20",
        "poincare_distance_correlation_above_0_71",
        "poincare_rms_stress_below_1_02",
        "top5_mass_top5_central_overlap_is_4",
        "top5_signature_top5_central_overlap_is_4",
        "lightest_atom_is_outermost",
        "heaviest_atom_is_in_top5_central",
        "richest_signature_atom_is_in_top5_central",
        "radius_mass_correlation_is_negative",
        "radius_signature_correlation_is_negative",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 Poincare embedding missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("atom_count") != 20:
        raise AssertionError("Poincare embedding atom count mismatch")
    if witness.get("source_metric") != "signature_affinity_boundary":
        raise AssertionError("Poincare embedding source metric mismatch")
    if witness.get("source_metric_diameter") != 54:
        raise AssertionError("Poincare embedding source metric diameter mismatch")
    if witness.get("selected_radius_step") != 182:
        raise AssertionError("Poincare selected radius step mismatch")
    if witness.get("selected_radius") != 0.91:
        raise AssertionError("Poincare selected radius mismatch")
    if witness.get("top5_mass_central_overlap") != 4:
        raise AssertionError("Poincare mass/central overlap mismatch")
    if witness.get("top5_signature_central_overlap") != 4:
        raise AssertionError("Poincare signature/central overlap mismatch")
    if witness.get("lightest_atom") != witness.get("outermost_atom"):
        raise AssertionError("Poincare lightest atom is not outermost")
    if coordinate_table.shape != (20, len(COORDINATE_COLUMNS)):
        raise AssertionError("Poincare coordinate table shape mismatch")
    if poincare_distances.shape != (20, 20):
        raise AssertionError("Poincare distance matrix shape mismatch")
    if target_metric.shape != (20, 20):
        raise AssertionError("Poincare target metric shape mismatch")
    if not np.all(coordinate_table[:, 3] < 1.0):
        raise AssertionError("Poincare coordinate radius outside disk")
    if not np.isclose(float(coordinate_table[:, 3].max()), 0.91, atol=1e-12):
        raise AssertionError("Poincare max radius mismatch")
    if not np.allclose(poincare_distances, poincare_distances.T):
        raise AssertionError("Poincare distance matrix is not symmetric")
    if not np.allclose(np.diag(poincare_distances), 0.0):
        raise AssertionError("Poincare distance diagonal is not zero")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("hyperbolic_graph_report", {}), GRAPH_REPORT, "graph report input")
    assert_file_hash(inputs.get("hyperbolic_graph", {}), GRAPH_JSON, "graph JSON input")
    assert_file_hash(inputs.get("hyperbolic_metrics", {}), GRAPH_METRICS, "graph metrics input")
    assert_file_hash(inputs.get("boundary_atlas_report", {}), ATLAS_REPORT, "atlas report input")
    assert_file_hash(inputs.get("boundary_atlas", {}), ATLAS_JSON, "atlas JSON input")

    if manifest.get("schema") != "c985.proof_obligation.d20_poincare_embedding_manifest@1":
        raise AssertionError("C985 d20 Poincare embedding manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 Poincare embedding manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 Poincare embedding manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 d20 Poincare embedding missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 Poincare embedding index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 Poincare embedding index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_poincare_embedding@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "selected_radius": witness.get("selected_radius"),
        "poincare_metric_diameter": witness.get("poincare_metric_diameter"),
        "rms_stress": witness.get("rms_stress"),
        "distance_correlation": witness.get("distance_correlation"),
        "radius_range": [witness.get("radius_min"), witness.get("radius_max")],
        "lightest_atom": witness.get("lightest_atom"),
        "heaviest_atom": witness.get("heaviest_atom"),
        "richest_signature_atom": witness.get("richest_signature_atom"),
        "top5_mass_central_overlap": witness.get("top5_mass_central_overlap"),
        "top5_signature_central_overlap": witness.get("top5_signature_central_overlap"),
        "radius_mass_correlation": witness.get("radius_mass_correlation"),
        "radius_signature_correlation": witness.get("radius_signature_correlation"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_poincare_embedding()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
