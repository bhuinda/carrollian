from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_conductance_spine import (
        BOUNDARY_FLUX_CERTIFICATE,
        BOUNDARY_FLUX_JSON,
        BOUNDARY_FLUX_REPORT,
        BOUNDARY_FLUX_TABLES,
        BOUNDARY_MASK_EDGES,
        BOUNDARY_RATE_CERTIFICATE,
        BOUNDARY_RATE_JSON,
        BOUNDARY_RATE_PARTITIONS,
        BOUNDARY_RATE_REPORT,
        BOUNDARY_RATE_TABLES,
        CONDUCTANCE_DIRECTED_EDGE_COLUMNS,
        CONDUCTANCE_OBSERVABLE_COLUMNS,
        CONDUCTANCE_SPINE_EDGE_COLUMNS,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_conductance_spine import (
        BOUNDARY_FLUX_CERTIFICATE,
        BOUNDARY_FLUX_JSON,
        BOUNDARY_FLUX_REPORT,
        BOUNDARY_FLUX_TABLES,
        BOUNDARY_MASK_EDGES,
        BOUNDARY_RATE_CERTIFICATE,
        BOUNDARY_RATE_JSON,
        BOUNDARY_RATE_PARTITIONS,
        BOUNDARY_RATE_REPORT,
        BOUNDARY_RATE_TABLES,
        CONDUCTANCE_DIRECTED_EDGE_COLUMNS,
        CONDUCTANCE_OBSERVABLE_COLUMNS,
        CONDUCTANCE_SPINE_EDGE_COLUMNS,
        INDEX_PATH,
        OBSERVABLE_CODES,
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


def validate_c985_d20_signature_boundary_conductance_spine() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    spine = load_json(OUT_DIR / "signature_boundary_conductance_spine.json")
    certificate = load_json(
        OUT_DIR / "signature_boundary_conductance_spine_certificate.json"
    )
    edge_csv = (OUT_DIR / "boundary_conductance_spine_edges.csv").read_text(
        encoding="utf-8"
    )
    directed_csv = (OUT_DIR / "boundary_conductance_directed_edges.csv").read_text(
        encoding="utf-8"
    )
    observable_csv = (OUT_DIR / "boundary_conductance_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(
        OUT_DIR / "signature_boundary_conductance_spine_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if spine != expected["signature_boundary_conductance_spine"]:
        raise AssertionError("boundary conductance spine JSON is not reproducible")
    if edge_csv != expected["boundary_conductance_spine_edges_csv"]:
        raise AssertionError("boundary conductance spine edge CSV is not reproducible")
    if directed_csv != expected["boundary_conductance_directed_edges_csv"]:
        raise AssertionError("boundary conductance directed edge CSV is not reproducible")
    if observable_csv != expected["boundary_conductance_observables_csv"]:
        raise AssertionError("boundary conductance observable CSV is not reproducible")
    if certificate != expected["signature_boundary_conductance_spine_certificate"]:
        raise AssertionError("boundary conductance spine certificate is not reproducible")

    table_names = [
        "conductance_spine_edge_table",
        "conductance_directed_edge_table",
        "conductance_observable_table",
    ]
    for name in table_names:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"boundary conductance spine table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_conductance_spine@1":
        raise AssertionError("C985 d20 conductance spine report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 conductance spine is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 conductance spine all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 conductance spine checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 conductance spine report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 conductance spine report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "boundary_flux_report_certified",
        "boundary_flux_certificate_certified",
        "boundary_rate_report_certified",
        "boundary_rate_certificate_certified",
        "boundary_edge_count_is_16",
        "directed_boundary_edge_count_is_32",
        "total_flux_matches_boundary_rate",
        "spine_order_matches_expected",
        "top_spine_edge_matches_expected",
        "top_five_spine_matches_expected",
        "top_five_flux_fraction_matches_expected",
        "top_five_entropy_fraction_matches_expected",
        "high_and_central_edge_counts_match",
        "partition_edge_entropy_totals_match_expected",
        "central_entropy_fraction_matches_expected",
        "positive_boundary_probabilities_sum_to_upstream_exit",
        "negative_boundary_probabilities_sum_to_upstream_exit",
        "directed_twice_flows_are_reversible_by_edge",
        "directed_twice_flow_sum_matches_cut_twice",
        "edge_refined_entropy_rate_matches_expected",
        "edge_entropy_surplus_over_partition_matches_expected",
        "edge_entropy_surplus_over_quotient_matches_expected",
        "entropy_rounding_delta_within_one",
        "edge_entropy_refines_partition_entropy",
        "spine_edge_table_shape_is_16_by_19",
        "directed_edge_table_shape_is_32_by_13",
        "observable_table_shape_matches_codebook",
        "boundary_flux_json_schema_available",
        "boundary_rate_json_schema_available",
        "boundary_flux_tables_available",
        "boundary_rate_tables_available",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 conductance spine missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("boundary_edge_count") != 16:
        raise AssertionError("conductance spine boundary edge count mismatch")
    if witness.get("directed_boundary_edge_count") != 32:
        raise AssertionError("conductance spine directed edge count mismatch")
    if witness.get("total_undirected_cut_flux_x1e12") != 238962451389:
        raise AssertionError("conductance spine cut flux mismatch")
    if witness.get("spine_order_boundary_mask_edge_ids") != [
        14,
        15,
        2,
        6,
        3,
        7,
        8,
        11,
        9,
        13,
        12,
        5,
        10,
        4,
        1,
        0,
    ]:
        raise AssertionError("conductance spine order mismatch")
    if witness.get("top_spine_edge") != {
        "boundary_mask_edge_id": 14,
        "positive_carrier_mask_class_id": 11,
        "negative_carrier_mask_class_id": 13,
        "undirected_stationary_flux_x1e12": 43567340880,
        "total_entropy_contribution_x1e12": 135084234325,
    }:
        raise AssertionError("conductance spine top edge mismatch")
    if witness.get("top_five_spine") != {
        "boundary_mask_edge_ids": [14, 15, 2, 6, 3],
        "undirected_stationary_flux_x1e12": 139072996173,
        "total_entropy_contribution_x1e12": 486096919708,
        "flux_fraction_x1e12": 581986815772,
        "entropy_fraction_of_boundary_crossing_x1e12": 521357092366,
    }:
        raise AssertionError("conductance spine top-five mismatch")
    if witness.get("partition_edge_entropy_x1e12") != {
        "high_negative": 23221774728,
        "central_negative": 909146705198,
    }:
        raise AssertionError("conductance spine partition entropy mismatch")
    if witness.get("partition_edge_entropy_fraction_x1e12") != {
        "high_negative": 24906220264,
        "central_negative": 975093779736,
    }:
        raise AssertionError("conductance spine partition entropy fraction mismatch")
    if witness.get("positive_boundary_probability_sum_x1e12") != 190831926563:
        raise AssertionError("conductance spine positive probability sum mismatch")
    if witness.get("negative_boundary_probability_sum_x1e12") != 319560035288:
        raise AssertionError("conductance spine negative probability sum mismatch")
    if witness.get("edge_refined_entropy_rate_x1e12") != 1137598297346:
        raise AssertionError("conductance spine edge entropy mismatch")
    if witness.get("edge_entropy_surplus_over_partition_x1e12") != 579016158147:
        raise AssertionError("conductance spine partition entropy surplus mismatch")
    if witness.get("edge_entropy_surplus_over_quotient_x1e12") != 598158902304:
        raise AssertionError("conductance spine quotient entropy surplus mismatch")
    if witness.get("entropy_rounding_delta_x1e12") != 1:
        raise AssertionError("conductance spine entropy rounding mismatch")

    spine_table = np.asarray(tables["conductance_spine_edge_table"], dtype=np.int64)
    directed_table = np.asarray(tables["conductance_directed_edge_table"], dtype=np.int64)
    observable_table = np.asarray(tables["conductance_observable_table"], dtype=np.int64)

    if spine_table.shape != (16, len(CONDUCTANCE_SPINE_EDGE_COLUMNS)):
        raise AssertionError("conductance spine edge table shape mismatch")
    if directed_table.shape != (32, len(CONDUCTANCE_DIRECTED_EDGE_COLUMNS)):
        raise AssertionError("conductance spine directed table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(CONDUCTANCE_OBSERVABLE_COLUMNS)):
        raise AssertionError("conductance spine observable table shape mismatch")
    if spine_table[:, 1].tolist() != witness.get("spine_order_boundary_mask_edge_ids"):
        raise AssertionError("conductance spine table order mismatch")
    if int(spine_table[:, 10].sum()) != 238962451389:
        raise AssertionError("conductance spine table flux sum mismatch")
    if int(spine_table[:, 16].sum()) != 932368479926:
        raise AssertionError("conductance spine table entropy sum mismatch")
    if int(directed_table[directed_table[:, 3] == 0, 10].sum()) != 190831926563:
        raise AssertionError("conductance spine directed positive probability mismatch")
    if int(directed_table[directed_table[:, 3] == 1, 10].sum()) != 319560035288:
        raise AssertionError("conductance spine directed negative probability mismatch")
    if int(directed_table[:, 11].sum()) != 477924902778:
        raise AssertionError("conductance spine directed twice-flow sum mismatch")
    if observable_table[:, 1].tolist() != [
        code for _, code in sorted(OBSERVABLE_CODES.items(), key=lambda item: item[1])
    ]:
        raise AssertionError("conductance spine observable code order mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("boundary_flux_report", {}), BOUNDARY_FLUX_REPORT, "boundary flux report input")
    assert_file_hash(inputs.get("boundary_flux", {}), BOUNDARY_FLUX_JSON, "boundary flux JSON input")
    assert_file_hash(inputs.get("boundary_flux_tables", {}), BOUNDARY_FLUX_TABLES, "boundary flux tables input")
    assert_file_hash(
        inputs.get("boundary_flux_certificate", {}),
        BOUNDARY_FLUX_CERTIFICATE,
        "boundary flux certificate input",
    )
    assert_file_hash(inputs.get("boundary_mask_edges", {}), BOUNDARY_MASK_EDGES, "boundary mask edge input")
    assert_file_hash(inputs.get("boundary_rate_report", {}), BOUNDARY_RATE_REPORT, "boundary rate report input")
    assert_file_hash(inputs.get("boundary_rate", {}), BOUNDARY_RATE_JSON, "boundary rate JSON input")
    assert_file_hash(inputs.get("boundary_rate_tables", {}), BOUNDARY_RATE_TABLES, "boundary rate tables input")
    assert_file_hash(
        inputs.get("boundary_rate_certificate", {}),
        BOUNDARY_RATE_CERTIFICATE,
        "boundary rate certificate input",
    )
    assert_file_hash(
        inputs.get("boundary_rate_partitions", {}),
        BOUNDARY_RATE_PARTITIONS,
        "boundary rate partition input",
    )

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_conductance_spine_manifest@1":
        raise AssertionError("C985 d20 conductance spine manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 conductance spine manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 conductance spine manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 d20 conductance spine missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 conductance spine index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 conductance spine index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_conductance_spine@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "spine_order_boundary_mask_edge_ids": witness.get(
            "spine_order_boundary_mask_edge_ids"
        ),
        "top_spine_edge": witness.get("top_spine_edge"),
        "top_five_spine": witness.get("top_five_spine"),
        "edge_refined_entropy_rate_x1e12": witness.get(
            "edge_refined_entropy_rate_x1e12"
        ),
        "edge_entropy_surplus_over_partition_x1e12": witness.get(
            "edge_entropy_surplus_over_partition_x1e12"
        ),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_conductance_spine()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
