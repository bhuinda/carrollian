from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_hyperbolic_boundary_graph import (
        ATLAS_JSON,
        ATLAS_NPZ,
        ATLAS_REPORT,
        INDEX_PATH,
        OUT_DIR,
        PAIR_COLUMNS,
        RELATION_GEOMETRY_SIGNATURES,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_hyperbolic_boundary_graph import (
        ATLAS_JSON,
        ATLAS_NPZ,
        ATLAS_REPORT,
        INDEX_PATH,
        OUT_DIR,
        PAIR_COLUMNS,
        RELATION_GEOMETRY_SIGNATURES,
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


def validate_c985_d20_hyperbolic_boundary_graph() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    graph = load_json(OUT_DIR / "boundary_hyperbolic_graph.json")
    certificate = load_json(OUT_DIR / "hyperbolic_certificate.json")
    edges_csv = (OUT_DIR / "boundary_hyperbolic_edges.csv").read_text(encoding="utf-8")
    metrics = np.load(OUT_DIR / "boundary_hyperbolic_metrics.npz", allow_pickle=False)
    pair_records = np.asarray(metrics["pair_records"], dtype=np.int64)
    johnson_distances = np.asarray(metrics["johnson_distances"], dtype=np.int64)
    signature_distances = np.asarray(metrics["signature_distances"], dtype=np.int64)
    affinity_distances = np.asarray(metrics["affinity_distances"], dtype=np.int64)
    index = load_json(INDEX_PATH)

    if graph != expected["boundary_hyperbolic_graph"]:
        raise AssertionError("boundary hyperbolic graph JSON is not reproducible")
    if edges_csv != expected["boundary_hyperbolic_edges_csv"]:
        raise AssertionError("boundary hyperbolic edge CSV is not reproducible")
    if not np.array_equal(pair_records, expected["pair_records"]):
        raise AssertionError("boundary pair records are not reproducible")
    if not np.array_equal(johnson_distances, expected["johnson_distances"]):
        raise AssertionError("Johnson distance matrix is not reproducible")
    if not np.array_equal(signature_distances, expected["signature_distances"]):
        raise AssertionError("signature distance matrix is not reproducible")
    if not np.array_equal(affinity_distances, expected["affinity_distances"]):
        raise AssertionError("affinity distance matrix is not reproducible")
    if certificate != expected["hyperbolic_certificate"]:
        raise AssertionError("hyperbolic certificate is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_hyperbolic_boundary_graph@1":
        raise AssertionError("C985 d20 hyperbolic graph report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 hyperbolic graph is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 hyperbolic graph all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 hyperbolic graph checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 hyperbolic graph report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 hyperbolic graph report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "atlas_report_certified",
        "atom_count_is_20",
        "pair_count_is_190",
        "pair_layer_counts_match_c_h6_3",
        "johnson_edge_count_is_90",
        "complement_pair_count_is_10",
        "signature_class_union_is_233",
        "johnson_graph_is_connected",
        "signature_metric_graph_is_connected",
        "affinity_metric_graph_is_connected",
        "johnson_diameter_is_3",
        "johnson_delta_numerator_is_2",
        "signature_delta_numerator_is_146",
        "affinity_delta_numerator_is_41",
        "max_complement_mass_contrast_is_155776",
        "pair_records_shape_is_190_by_15",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 hyperbolic graph missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("atom_count") != 20:
        raise AssertionError("hyperbolic graph atom count mismatch")
    if witness.get("pair_count") != 190:
        raise AssertionError("hyperbolic graph pair count mismatch")
    if witness.get("johnson_edge_count") != 90:
        raise AssertionError("hyperbolic graph Johnson edge count mismatch")
    if witness.get("complement_pair_count") != 10:
        raise AssertionError("hyperbolic graph complement pair count mismatch")
    if witness.get("signature_class_count") != 233:
        raise AssertionError("hyperbolic graph signature class count mismatch")
    if witness.get("johnson_delta_fraction") != [2, 2]:
        raise AssertionError("unweighted Johnson hyperbolicity mismatch")
    if witness.get("signature_delta_fraction") != [146, 2]:
        raise AssertionError("signature-distance hyperbolicity mismatch")
    if witness.get("affinity_delta_fraction") != [41, 2]:
        raise AssertionError("signature-affinity hyperbolicity mismatch")
    if witness.get("max_complement_mass_contrast") != 155776:
        raise AssertionError("complement mass contrast mismatch")
    if pair_records.shape != (190, len(PAIR_COLUMNS)):
        raise AssertionError("pair record matrix shape mismatch")
    if johnson_distances.shape != (20, 20):
        raise AssertionError("Johnson distance matrix shape mismatch")
    if signature_distances.shape != (20, 20):
        raise AssertionError("signature distance matrix shape mismatch")
    if affinity_distances.shape != (20, 20):
        raise AssertionError("affinity distance matrix shape mismatch")
    if int(johnson_distances.max()) != 3:
        raise AssertionError("Johnson graph diameter mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("boundary_atlas_report", {}), ATLAS_REPORT, "atlas report input")
    assert_file_hash(inputs.get("boundary_atlas", {}), ATLAS_JSON, "atlas JSON input")
    assert_file_hash(inputs.get("boundary_atlas_npz", {}), ATLAS_NPZ, "atlas NPZ input")
    assert_file_hash(
        inputs.get("relation_geometry_signatures", {}),
        RELATION_GEOMETRY_SIGNATURES,
        "relation signatures input",
    )

    if manifest.get("schema") != "c985.proof_obligation.d20_hyperbolic_boundary_graph_manifest@1":
        raise AssertionError("C985 d20 hyperbolic graph manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 hyperbolic graph manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 hyperbolic graph manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 d20 hyperbolic graph missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 hyperbolic graph index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 hyperbolic graph index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_hyperbolic_boundary_graph@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "atom_count": witness.get("atom_count"),
        "johnson_edge_count": witness.get("johnson_edge_count"),
        "complement_pair_count": witness.get("complement_pair_count"),
        "johnson_diameter": witness.get("johnson_diameter"),
        "johnson_delta_fraction": witness.get("johnson_delta_fraction"),
        "signature_distance_diameter": witness.get("signature_distance_diameter"),
        "signature_delta_fraction": witness.get("signature_delta_fraction"),
        "affinity_distance_diameter": witness.get("affinity_distance_diameter"),
        "affinity_delta_fraction": witness.get("affinity_delta_fraction"),
        "max_complement_mass_contrast": witness.get("max_complement_mass_contrast"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_hyperbolic_boundary_graph()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
