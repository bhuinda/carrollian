from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_class_nerve import (
        ATLAS_JSON,
        FILTRATION_REPORT,
        FILTRATION_TABLES,
        GRAPH_JSON,
        GRAPH_METRICS,
        GRAPH_REPORT,
        INDEX_PATH,
        LANDMARK_FILTRATION_JSON,
        NERVE_PAIR_COLUMNS,
        OUT_DIR,
        RELATION_GEOMETRY_SIGNATURES,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_class_nerve import (
        ATLAS_JSON,
        FILTRATION_REPORT,
        FILTRATION_TABLES,
        GRAPH_JSON,
        GRAPH_METRICS,
        GRAPH_REPORT,
        INDEX_PATH,
        LANDMARK_FILTRATION_JSON,
        NERVE_PAIR_COLUMNS,
        OUT_DIR,
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


def validate_c985_d20_signature_class_nerve() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    nerve = load_json(OUT_DIR / "signature_class_nerve.json")
    certificate = load_json(OUT_DIR / "nerve_certificate.json")
    pair_csv = (OUT_DIR / "nerve_pair_records.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "signature_class_nerve_tables.npz", allow_pickle=False)
    nerve_pair_records = np.asarray(tables["nerve_pair_records"], dtype=np.int64)
    chart_rows = np.asarray(tables["chart_rows"], dtype=np.int64)
    chart_atom_incidence = np.asarray(tables["chart_atom_incidence"], dtype=np.int8)
    atom_chart_membership = np.asarray(tables["atom_chart_membership"], dtype=np.int8)
    chart_intersection_atom_counts = np.asarray(
        tables["chart_intersection_atom_counts"],
        dtype=np.int64,
    )
    chart_intersection_signature_counts = np.asarray(
        tables["chart_intersection_signature_counts"],
        dtype=np.int64,
    )
    chart_intersection_tensor_mass = np.asarray(
        tables["chart_intersection_tensor_mass"],
        dtype=np.int64,
    )
    signature_deficit_contrast = np.asarray(tables["signature_deficit_contrast"], dtype=np.int64)
    atom_deficit_distances = np.asarray(tables["atom_deficit_distances"], dtype=np.int64)
    membership_hamming_distances = np.asarray(
        tables["membership_hamming_distances"],
        dtype=np.int64,
    )
    index = load_json(INDEX_PATH)

    if nerve != expected["signature_class_nerve"]:
        raise AssertionError("signature-class nerve JSON is not reproducible")
    if pair_csv != expected["nerve_pair_records_csv"]:
        raise AssertionError("signature-class nerve pair CSV is not reproducible")
    if not np.array_equal(nerve_pair_records, expected["nerve_pair_records"]):
        raise AssertionError("signature-class nerve pair records are not reproducible")
    if not np.array_equal(chart_rows, expected["chart_rows"]):
        raise AssertionError("signature-class nerve chart rows are not reproducible")
    if not np.array_equal(chart_atom_incidence, expected["chart_atom_incidence"]):
        raise AssertionError("signature-class nerve chart incidence is not reproducible")
    if not np.array_equal(atom_chart_membership, expected["atom_chart_membership"]):
        raise AssertionError("signature-class nerve atom membership is not reproducible")
    if not np.array_equal(
        chart_intersection_atom_counts,
        expected["chart_intersection_atom_counts"],
    ):
        raise AssertionError("signature-class nerve atom intersections are not reproducible")
    if not np.array_equal(
        chart_intersection_signature_counts,
        expected["chart_intersection_signature_counts"],
    ):
        raise AssertionError("signature-class nerve signature intersections are not reproducible")
    if not np.array_equal(
        chart_intersection_tensor_mass,
        expected["chart_intersection_tensor_mass"],
    ):
        raise AssertionError("signature-class nerve mass intersections are not reproducible")
    if not np.array_equal(signature_deficit_contrast, expected["signature_deficit_contrast"]):
        raise AssertionError("signature-class nerve signature deficit matrix is not reproducible")
    if not np.array_equal(atom_deficit_distances, expected["atom_deficit_distances"]):
        raise AssertionError("signature-class nerve atom-deficit distances are not reproducible")
    if not np.array_equal(membership_hamming_distances, expected["membership_hamming_distances"]):
        raise AssertionError("signature-class nerve membership Hamming distances are not reproducible")
    if certificate != expected["nerve_certificate"]:
        raise AssertionError("signature-class nerve certificate is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_class_nerve@1":
        raise AssertionError("C985 d20 signature-class nerve report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 signature-class nerve is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 signature-class nerve all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 signature-class nerve checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 signature-class nerve report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 signature-class nerve report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "filtration_report_certified",
        "hyperbolic_graph_report_certified",
        "landmark_filtration_signature_class_count_is_233",
        "atom_count_is_20",
        "chart_count_is_20",
        "every_chart_has_full_signature_coverage",
        "chart_size_min_is_7",
        "chart_size_max_is_14",
        "chart_size_sum_is_240",
        "chart_atom_incidence_shape_is_20_by_20",
        "nerve_pair_record_count_is_190",
        "chart_pair_atom_intersection_min_is_4",
        "chart_pair_signature_intersection_min_is_197",
        "chart_pair_signature_intersection_max_is_233",
        "minimum_signature_intersection_pair_count_is_4",
        "atom_deficit_metric_triangle_holds",
        "atom_deficit_delta_numerator_is_4",
        "atom_deficit_witness_is_0_4_10_14",
        "atom_deficit_witness_overlaps_affinity_witness_in_3_atoms",
        "membership_hamming_metric_triangle_holds",
        "membership_hamming_delta_numerator_is_16",
        "membership_hamming_witness_is_1_7_10_14",
        "johnson_witness_common_chart_count_is_1",
        "signature_distance_witness_common_chart_count_is_1",
        "affinity_witness_common_chart_count_is_0",
        "johnson_witness_centered_intersection_signature_coverage_is_207",
        "signature_witness_centered_intersection_signature_coverage_is_203",
        "affinity_witness_centered_intersection_signature_coverage_is_197",
        "affinity_witness_centered_signature_coverage_hits_pairwise_floor",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 signature-class nerve missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("chart_count") != 20:
        raise AssertionError("signature-class nerve chart count mismatch")
    if witness.get("signature_class_count") != 233:
        raise AssertionError("signature-class nerve signature class count mismatch")
    if witness.get("chart_size_min") != 7 or witness.get("chart_size_max") != 14:
        raise AssertionError("signature-class nerve chart size bounds mismatch")
    if witness.get("chart_size_sum") != 240:
        raise AssertionError("signature-class nerve chart size sum mismatch")
    if witness.get("nerve_pair_count") != 190:
        raise AssertionError("signature-class nerve pair count mismatch")
    if witness.get("pair_signature_intersection_min") != 197:
        raise AssertionError("signature-class nerve signature intersection floor mismatch")
    if witness.get("pair_signature_intersection_max") != 233:
        raise AssertionError("signature-class nerve signature intersection ceiling mismatch")
    if witness.get("minimum_signature_intersection_pair_count") != 4:
        raise AssertionError("signature-class nerve minimum intersection pair count mismatch")
    if witness.get("atom_deficit_delta_fraction") != [4, 2]:
        raise AssertionError("signature-class nerve atom-deficit delta mismatch")
    if witness.get("atom_deficit_witness_atom_ids") != [0, 4, 10, 14]:
        raise AssertionError("signature-class nerve atom-deficit witness mismatch")
    if witness.get("membership_hamming_delta_fraction") != [16, 2]:
        raise AssertionError("signature-class nerve membership Hamming delta mismatch")
    if witness.get("membership_hamming_witness_atom_ids") != [1, 7, 10, 14]:
        raise AssertionError("signature-class nerve membership Hamming witness mismatch")
    if witness.get("affinity_witness_common_chart_count") != 0:
        raise AssertionError("signature-class nerve affinity witness common chart mismatch")
    if witness.get("affinity_witness_centered_intersection_signature_coverage") != 197:
        raise AssertionError("signature-class nerve affinity witness signature floor mismatch")
    if witness.get("affinity_overlap_with_atom_deficit_witness_count") != 3:
        raise AssertionError("signature-class nerve affinity/atom-deficit overlap mismatch")

    if nerve_pair_records.shape != (190, len(NERVE_PAIR_COLUMNS)):
        raise AssertionError("signature-class nerve pair record shape mismatch")
    if chart_rows.shape != (20, 4):
        raise AssertionError("signature-class nerve chart row shape mismatch")
    if chart_atom_incidence.shape != (20, 20):
        raise AssertionError("signature-class nerve chart incidence shape mismatch")
    if atom_chart_membership.shape != (20, 20):
        raise AssertionError("signature-class nerve atom membership shape mismatch")
    if chart_intersection_atom_counts.shape != (20, 20):
        raise AssertionError("signature-class nerve atom intersection matrix shape mismatch")
    if chart_intersection_signature_counts.shape != (20, 20):
        raise AssertionError("signature-class nerve signature intersection matrix shape mismatch")
    if chart_intersection_tensor_mass.shape != (20, 20):
        raise AssertionError("signature-class nerve mass intersection matrix shape mismatch")
    if signature_deficit_contrast.shape != (20, 20):
        raise AssertionError("signature-class nerve signature deficit matrix shape mismatch")
    if atom_deficit_distances.shape != (20, 20):
        raise AssertionError("signature-class nerve atom-deficit distance shape mismatch")
    if membership_hamming_distances.shape != (20, 20):
        raise AssertionError("signature-class nerve membership Hamming distance shape mismatch")
    if int(nerve_pair_records[:, 4].min()) != 4:
        raise AssertionError("signature-class nerve minimum atom intersection mismatch")
    if int(nerve_pair_records[:, 5].min()) != 197:
        raise AssertionError("signature-class nerve minimum signature intersection mismatch")
    if int(nerve_pair_records[:, 5].max()) != 233:
        raise AssertionError("signature-class nerve maximum signature intersection mismatch")
    if int(atom_deficit_distances.max()) != 16:
        raise AssertionError("signature-class nerve atom-deficit diameter mismatch")
    if int(membership_hamming_distances.max()) != 20:
        raise AssertionError("signature-class nerve membership Hamming diameter mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("filtration_report", {}), FILTRATION_REPORT, "filtration report input")
    assert_file_hash(
        inputs.get("landmark_filtration", {}),
        LANDMARK_FILTRATION_JSON,
        "landmark filtration input",
    )
    assert_file_hash(inputs.get("filtration_tables", {}), FILTRATION_TABLES, "filtration tables input")
    assert_file_hash(inputs.get("hyperbolic_graph_report", {}), GRAPH_REPORT, "graph report input")
    assert_file_hash(inputs.get("hyperbolic_graph", {}), GRAPH_JSON, "graph JSON input")
    assert_file_hash(inputs.get("hyperbolic_metrics", {}), GRAPH_METRICS, "graph metrics input")
    assert_file_hash(inputs.get("boundary_atlas", {}), ATLAS_JSON, "atlas input")
    assert_file_hash(
        inputs.get("relation_geometry_signatures", {}),
        RELATION_GEOMETRY_SIGNATURES,
        "relation signatures input",
    )

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_class_nerve_manifest@1":
        raise AssertionError("C985 d20 signature-class nerve manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 signature-class nerve manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 signature-class nerve manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 d20 signature-class nerve missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 signature-class nerve index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 signature-class nerve index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_class_nerve@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "chart_count": witness.get("chart_count"),
        "chart_size_range": [witness.get("chart_size_min"), witness.get("chart_size_max")],
        "pair_signature_intersection_range": [
            witness.get("pair_signature_intersection_min"),
            witness.get("pair_signature_intersection_max"),
        ],
        "atom_deficit_delta_fraction": witness.get("atom_deficit_delta_fraction"),
        "atom_deficit_witness_atom_ids": witness.get("atom_deficit_witness_atom_ids"),
        "membership_hamming_delta_fraction": witness.get("membership_hamming_delta_fraction"),
        "membership_hamming_witness_atom_ids": witness.get("membership_hamming_witness_atom_ids"),
        "affinity_witness_common_chart_count": witness.get("affinity_witness_common_chart_count"),
        "affinity_witness_centered_intersection_signature_coverage": witness.get(
            "affinity_witness_centered_intersection_signature_coverage"
        ),
        "affinity_overlap_with_atom_deficit_witness_count": witness.get(
            "affinity_overlap_with_atom_deficit_witness_count"
        ),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_class_nerve()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
