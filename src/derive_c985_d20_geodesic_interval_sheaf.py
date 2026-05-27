from __future__ import annotations

import json
from collections import deque
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_symbolic_rewrite_rules import csv_text, histogram
    from .derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_d20_symbolic_rewrite_rules import csv_text, histogram
    from derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "c985_d20_geodesic_interval_sheaf"
STATUS = "C985_D20_GEODESIC_INTERVAL_SHEAF_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

REWRITE_COMPLEX_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_rewrite_complex_hyperbolicity"
SYMBOLIC_REWRITE_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_symbolic_rewrite_rules"

REWRITE_COMPLEX_REPORT = REWRITE_COMPLEX_DIR / "report.json"
REWRITE_COMPLEX_JSON = REWRITE_COMPLEX_DIR / "rewrite_complex.json"
REWRITE_COMPLEX_TABLES = REWRITE_COMPLEX_DIR / "rewrite_complex_tables.npz"
REWRITE_COMPLEX_CERTIFICATE = REWRITE_COMPLEX_DIR / "rewrite_complex_certificate.json"
SYMBOLIC_REWRITE_REPORT = SYMBOLIC_REWRITE_DIR / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_c985_d20_geodesic_interval_sheaf.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_d20_geodesic_interval_sheaf.py"

HIGH_SIGNATURE_THRESHOLD = 155
DISTANCE_SCALE = 10_000_000_000

INTERVAL_COLUMNS = [
    "interval_id",
    "source_node_id",
    "target_node_id",
    "graph_distance",
    "interval_node_count",
    "shortest_path_count",
    "min_sector_coverage_count",
    "max_sector_coverage_count",
    "full_sector_preserved",
    "min_signature_union_count",
    "max_signature_union_count",
    "high_signature_threshold",
    "high_signature_preserved",
    "full_high_preserved",
    "min_tensor_path_coefficient_mass_sum",
    "max_tensor_path_coefficient_mass_sum",
    "endpoint_poincare_distance_x1e10",
    "interval_poincare_diameter_x1e10",
]


def round10(value: float) -> float:
    return float(round(float(value), 10))


def scaled_distance(value: float) -> int:
    return int(round(float(value) * DISTANCE_SCALE))


def shortest_path_count(
    adjacency: np.ndarray,
    graph_distances: np.ndarray,
    source: int,
    target: int,
) -> int:
    if source == target:
        return 1
    node_count = int(adjacency.shape[0])
    target_distance = int(graph_distances[source, target])
    ways = np.zeros(node_count, dtype=np.int64)
    ways[source] = 1
    queue: deque[int] = deque([source])
    ordered: list[int] = []
    seen = np.zeros(node_count, dtype=bool)
    seen[source] = True
    while queue:
        node = queue.popleft()
        ordered.append(node)
        for neighbor in np.flatnonzero(adjacency[node]):
            if int(graph_distances[source, neighbor]) == int(graph_distances[source, node]) + 1:
                if int(graph_distances[source, neighbor]) <= target_distance and not seen[neighbor]:
                    seen[neighbor] = True
                    queue.append(int(neighbor))

    for node in sorted(ordered, key=lambda item: int(graph_distances[source, item])):
        if int(graph_distances[source, node] + graph_distances[node, target]) != target_distance:
            continue
        for neighbor in np.flatnonzero(adjacency[node]):
            if int(graph_distances[source, neighbor]) != int(graph_distances[source, node]) + 1:
                continue
            if int(graph_distances[source, neighbor] + graph_distances[neighbor, target]) == target_distance:
                ways[neighbor] += ways[node]
    return int(ways[target])


def build_intervals(
    nodes: list[dict[str, Any]],
    adjacency: np.ndarray,
    graph_distances: np.ndarray,
    node_poincare_distances: np.ndarray,
) -> tuple[list[dict[str, Any]], np.ndarray, np.ndarray]:
    interval_rows: list[dict[str, Any]] = []
    table_rows: list[list[int]] = []
    membership_rows: list[np.ndarray] = []
    node_count = len(nodes)

    for source in range(node_count):
        for target in range(source, node_count):
            graph_distance = int(graph_distances[source, target])
            interval_nodes = [
                node
                for node in range(node_count)
                if int(graph_distances[source, node] + graph_distances[node, target]) == graph_distance
            ]
            membership = np.zeros(node_count, dtype=np.int8)
            membership[np.asarray(interval_nodes, dtype=np.int64)] = 1
            sector_values = [int(nodes[node]["sector_coverage_count"]) for node in interval_nodes]
            signature_values = [int(nodes[node]["signature_union_count"]) for node in interval_nodes]
            mass_values = [
                int(nodes[node]["tensor_path_coefficient_mass_sum"])
                for node in interval_nodes
            ]
            full_sector = min(sector_values) == 6
            high_signature = min(signature_values) >= HIGH_SIGNATURE_THRESHOLD
            interval_poincare_diameter = 0.0
            for left in interval_nodes:
                for right in interval_nodes:
                    interval_poincare_diameter = max(
                        interval_poincare_diameter,
                        float(node_poincare_distances[left, right]),
                    )
            row = {
                "interval_id": len(interval_rows),
                "source_node_id": source,
                "target_node_id": target,
                "source_word": nodes[source]["canonical_word"],
                "target_word": nodes[target]["canonical_word"],
                "graph_distance": graph_distance,
                "interval_node_count": len(interval_nodes),
                "interval_node_ids": interval_nodes,
                "interval_words": [nodes[node]["canonical_word"] for node in interval_nodes],
                "shortest_path_count": shortest_path_count(
                    adjacency,
                    graph_distances,
                    source,
                    target,
                ),
                "min_sector_coverage_count": min(sector_values),
                "max_sector_coverage_count": max(sector_values),
                "full_sector_preserved": int(full_sector),
                "min_signature_union_count": min(signature_values),
                "max_signature_union_count": max(signature_values),
                "high_signature_threshold": HIGH_SIGNATURE_THRESHOLD,
                "high_signature_preserved": int(high_signature),
                "full_high_preserved": int(full_sector and high_signature),
                "min_tensor_path_coefficient_mass_sum": min(mass_values),
                "max_tensor_path_coefficient_mass_sum": max(mass_values),
                "endpoint_poincare_distance": round10(node_poincare_distances[source, target]),
                "endpoint_poincare_distance_x1e10": scaled_distance(
                    node_poincare_distances[source, target]
                ),
                "interval_poincare_diameter": round10(interval_poincare_diameter),
                "interval_poincare_diameter_x1e10": scaled_distance(interval_poincare_diameter),
            }
            interval_rows.append(row)
            table_rows.append([int(row[column]) for column in INTERVAL_COLUMNS])
            membership_rows.append(membership)

    return (
        interval_rows,
        np.asarray(table_rows, dtype=np.int64),
        np.vstack(membership_rows).astype(np.int8),
    )


def build_payloads() -> dict[str, Any]:
    rewrite_report = load_json(REWRITE_COMPLEX_REPORT)
    rewrite_complex = load_json(REWRITE_COMPLEX_JSON)
    rewrite_certificate = load_json(REWRITE_COMPLEX_CERTIFICATE)
    symbolic_rewrite_report = load_json(SYMBOLIC_REWRITE_REPORT)
    rewrite_tables = np.load(REWRITE_COMPLEX_TABLES, allow_pickle=False)
    node_table = np.asarray(rewrite_tables["node_table"], dtype=np.int64)
    edge_table = np.asarray(rewrite_tables["edge_table"], dtype=np.int64)
    adjacency = np.asarray(rewrite_tables["adjacency"], dtype=np.int8)
    graph_distances = np.asarray(rewrite_tables["graph_distances"], dtype=np.int64)
    node_poincare_coordinates = np.asarray(
        rewrite_tables["node_poincare_coordinates"], dtype=np.float64
    )
    node_poincare_distances = np.asarray(
        rewrite_tables["node_poincare_distances"], dtype=np.float64
    )
    nodes = rewrite_complex["nodes"]
    interval_rows, interval_table, membership_matrix = build_intervals(
        nodes,
        adjacency,
        graph_distances,
        node_poincare_distances,
    )

    full_sector_intervals = [row for row in interval_rows if int(row["full_sector_preserved"]) == 1]
    high_signature_intervals = [
        row for row in interval_rows if int(row["high_signature_preserved"]) == 1
    ]
    full_high_intervals = [row for row in interval_rows if int(row["full_high_preserved"]) == 1]
    longest_full_high_distance = max(int(row["graph_distance"]) for row in full_high_intervals)
    longest_full_high_intervals = [
        {
            "source_node_id": int(row["source_node_id"]),
            "target_node_id": int(row["target_node_id"]),
            "source_word": row["source_word"],
            "target_word": row["target_word"],
            "graph_distance": int(row["graph_distance"]),
            "interval_node_ids": row["interval_node_ids"],
            "min_signature_union_count": int(row["min_signature_union_count"]),
            "endpoint_poincare_distance": row["endpoint_poincare_distance"],
        }
        for row in full_high_intervals
        if int(row["graph_distance"]) == longest_full_high_distance
    ]
    full_high_by_poincare = sorted(
        full_high_intervals,
        key=lambda row: (
            float(row["endpoint_poincare_distance"]),
            int(row["graph_distance"]),
            -int(row["source_node_id"]),
            -int(row["target_node_id"]),
        ),
        reverse=True,
    )
    poincare_diameter_interval = max(
        interval_rows,
        key=lambda row: (
            float(row["endpoint_poincare_distance"]),
            int(row["graph_distance"]),
        ),
    )
    path_count_hist = histogram([int(row["shortest_path_count"]) for row in interval_rows])
    distance_hist = histogram([int(row["graph_distance"]) for row in interval_rows])
    interval_size_hist = histogram([int(row["interval_node_count"]) for row in interval_rows])
    full_high_distance_hist = histogram(
        [int(row["graph_distance"]) for row in full_high_intervals]
    )

    interval_sheaf = {
        "schema": "c985.d20_geodesic_interval_sheaf@1",
        "object": "d20",
        "source_rewrite_complex_certificate": rewrite_report.get("certificate_sha256"),
        "source_symbolic_rewrite_certificate": symbolic_rewrite_report.get("certificate_sha256"),
        "sheaf_rule": {
            "base": "all unordered pairs of 56 rewrite-complex nodes, identities included",
            "stalk": "graph geodesic interval {v | d(source,v)+d(v,target)=d(source,target)}",
            "high_signature_threshold": HIGH_SIGNATURE_THRESHOLD,
            "threshold_source": "certified maximum binary rewrite signature-union count",
            "poincare_lift": "endpoint and interval diameters use certified barycentric Poincare distances",
        },
        "intervals": interval_rows,
        "summary": {
            "node_count": len(nodes),
            "interval_count": len(interval_rows),
            "distance_histogram": distance_hist,
            "interval_node_count_histogram": interval_size_hist,
            "shortest_path_count_histogram": path_count_hist,
            "max_shortest_path_count": max(int(row["shortest_path_count"]) for row in interval_rows),
            "max_interval_node_count": max(int(row["interval_node_count"]) for row in interval_rows),
            "full_sector_preserving_interval_count": len(full_sector_intervals),
            "high_signature_threshold": HIGH_SIGNATURE_THRESHOLD,
            "high_signature_preserving_interval_count": len(high_signature_intervals),
            "full_high_preserving_interval_count": len(full_high_intervals),
            "full_high_preserving_distance_histogram": full_high_distance_hist,
            "longest_full_high_graph_distance": longest_full_high_distance,
            "longest_full_high_intervals": longest_full_high_intervals,
            "top_full_high_poincare_interval": {
                "source_node_id": int(full_high_by_poincare[0]["source_node_id"]),
                "target_node_id": int(full_high_by_poincare[0]["target_node_id"]),
                "graph_distance": int(full_high_by_poincare[0]["graph_distance"]),
                "endpoint_poincare_distance": full_high_by_poincare[0][
                    "endpoint_poincare_distance"
                ],
                "interval_node_ids": full_high_by_poincare[0]["interval_node_ids"],
                "min_signature_union_count": int(
                    full_high_by_poincare[0]["min_signature_union_count"]
                ),
            },
            "poincare_diameter_interval": {
                "source_node_id": int(poincare_diameter_interval["source_node_id"]),
                "target_node_id": int(poincare_diameter_interval["target_node_id"]),
                "graph_distance": int(poincare_diameter_interval["graph_distance"]),
                "interval_node_count": int(poincare_diameter_interval["interval_node_count"]),
                "endpoint_poincare_distance": poincare_diameter_interval[
                    "endpoint_poincare_distance"
                ],
                "full_sector_preserved": int(poincare_diameter_interval["full_sector_preserved"]),
                "high_signature_preserved": int(poincare_diameter_interval["high_signature_preserved"]),
            },
        },
    }

    checks = {
        "rewrite_complex_report_certified": rewrite_report.get("status")
        == "C985_D20_REWRITE_COMPLEX_HYPERBOLICITY_CERTIFIED",
        "rewrite_complex_certificate_certified": rewrite_certificate.get("status")
        == "C985_D20_REWRITE_COMPLEX_HYPERBOLICITY_CERTIFIED",
        "symbolic_rewrite_report_certified": symbolic_rewrite_report.get("status")
        == "C985_D20_SYMBOLIC_REWRITE_RULES_CERTIFIED",
        "high_signature_threshold_matches_binary_rewrite_max": symbolic_rewrite_report.get(
            "witness", {}
        ).get("binary_rule_signature_union_count_max")
        == HIGH_SIGNATURE_THRESHOLD,
        "node_table_shape_is_56_by_17": tuple(node_table.shape) == (56, 17),
        "edge_table_shape_is_315_by_13": tuple(edge_table.shape) == (315, 13),
        "adjacency_shape_is_56_by_56": tuple(adjacency.shape) == (56, 56),
        "graph_distance_shape_is_56_by_56": tuple(graph_distances.shape) == (56, 56),
        "node_poincare_coordinate_shape_is_56_by_7": tuple(node_poincare_coordinates.shape)
        == (56, 7),
        "node_poincare_distance_shape_is_56_by_56": tuple(node_poincare_distances.shape)
        == (56, 56),
        "interval_count_is_1596": len(interval_rows) == 1596,
        "interval_table_shape_is_1596_by_18": tuple(interval_table.shape)
        == (1596, len(INTERVAL_COLUMNS)),
        "interval_membership_shape_is_1596_by_56": tuple(membership_matrix.shape) == (1596, 56),
        "interval_distance_histogram_is_56_315_720_505": distance_hist
        == [
            {"value": 0, "count": 56},
            {"value": 1, "count": 315},
            {"value": 2, "count": 720},
            {"value": 3, "count": 505},
        ],
        "interval_node_count_histogram_matches": interval_size_hist
        == [
            {"value": 1, "count": 56},
            {"value": 2, "count": 315},
            {"value": 3, "count": 90},
            {"value": 4, "count": 375},
            {"value": 6, "count": 390},
            {"value": 8, "count": 60},
            {"value": 10, "count": 180},
            {"value": 14, "count": 120},
            {"value": 20, "count": 10},
        ],
        "shortest_path_count_histogram_matches": path_count_hist
        == [
            {"value": 1, "count": 476},
            {"value": 2, "count": 360},
            {"value": 3, "count": 120},
            {"value": 4, "count": 270},
            {"value": 6, "count": 60},
            {"value": 9, "count": 180},
            {"value": 18, "count": 120},
            {"value": 36, "count": 10},
        ],
        "max_shortest_path_count_is_36": max(int(row["shortest_path_count"]) for row in interval_rows)
        == 36,
        "max_interval_node_count_is_20": max(int(row["interval_node_count"]) for row in interval_rows)
        == 20,
        "all_interval_stalks_nonempty": bool(np.all(np.sum(membership_matrix, axis=1) > 0)),
        "interval_membership_counts_match_table": bool(
            np.all(np.sum(membership_matrix, axis=1) == interval_table[:, 4])
        ),
        "full_sector_preserving_interval_count_is_59": len(full_sector_intervals) == 59,
        "high_signature_preserving_interval_count_is_69": len(high_signature_intervals) == 69,
        "full_high_preserving_interval_count_is_46": len(full_high_intervals) == 46,
        "full_high_preserving_distance_histogram_is_12_zero_31_one_3_two": full_high_distance_hist
        == [
            {"value": 0, "count": 12},
            {"value": 1, "count": 31},
            {"value": 2, "count": 3},
        ],
        "longest_full_high_graph_distance_is_2": longest_full_high_distance == 2,
        "longest_full_high_interval_count_is_3": len(longest_full_high_intervals) == 3,
        "top_full_high_poincare_interval_is_13_44": [
            int(full_high_by_poincare[0]["source_node_id"]),
            int(full_high_by_poincare[0]["target_node_id"]),
        ]
        == [13, 44],
        "top_full_high_poincare_distance_is_0_2453959784": full_high_by_poincare[0][
            "endpoint_poincare_distance"
        ]
        == 0.2453959784,
        "poincare_diameter_interval_is_0_55": [
            int(poincare_diameter_interval["source_node_id"]),
            int(poincare_diameter_interval["target_node_id"]),
        ]
        == [0, 55],
        "poincare_diameter_interval_graph_distance_is_3": int(
            poincare_diameter_interval["graph_distance"]
        )
        == 3,
        "poincare_diameter_interval_not_full_or_high_preserving": int(
            poincare_diameter_interval["full_high_preserved"]
        )
        == 0,
    }

    witness = {
        "node_count": len(nodes),
        "interval_count": len(interval_rows),
        "high_signature_threshold": HIGH_SIGNATURE_THRESHOLD,
        "distance_histogram": distance_hist,
        "interval_node_count_histogram": interval_size_hist,
        "shortest_path_count_histogram": path_count_hist,
        "max_shortest_path_count": max(int(row["shortest_path_count"]) for row in interval_rows),
        "max_interval_node_count": max(int(row["interval_node_count"]) for row in interval_rows),
        "full_sector_preserving_interval_count": len(full_sector_intervals),
        "high_signature_preserving_interval_count": len(high_signature_intervals),
        "full_high_preserving_interval_count": len(full_high_intervals),
        "full_high_preserving_distance_histogram": full_high_distance_hist,
        "longest_full_high_graph_distance": longest_full_high_distance,
        "longest_full_high_intervals": longest_full_high_intervals,
        "top_full_high_poincare_interval": interval_sheaf["summary"][
            "top_full_high_poincare_interval"
        ],
        "poincare_diameter_interval": interval_sheaf["summary"]["poincare_diameter_interval"],
        "interval_table_sha256": sha_array(interval_table),
        "interval_membership_sha256": sha_array(membership_matrix),
        "source_graph_distances_sha256": sha_array(graph_distances),
        "source_node_poincare_distances_sha256": sha_array(node_poincare_distances),
    }

    certificate = {
        "schema": "c985.d20_geodesic_interval_sheaf_certificate@1",
        "status": STATUS if all(checks.values()) else "C985_D20_GEODESIC_INTERVAL_SHEAF_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "all 1,596 unordered rewrite-complex node pairs have explicit geodesic interval stalks",
            "59 intervals preserve full six-sector coverage across every geodesic node",
            "69 intervals preserve the inherited high-signature threshold across every geodesic node",
            "46 intervals preserve both full-sector coverage and high-signature support",
            "the Poincare-diameter interval is identified and is not full-high preserving",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_geodesic_interval_sheaf@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The certified 56-node d20 rewrite complex admits a geodesic interval "
            "sheaf over all unordered node pairs, and the intervals preserving "
            "full-sector coverage plus high relation-signature support are exactly "
            "identified."
        ),
        "stage_protocol": {
            "draft": "use certified rewrite-complex graph distances and Poincare barycenter distances",
            "witness": "materialize all unordered geodesic interval stalks and preservation flags",
            "coherence": "check interval membership, shortest-path counts, full-sector preservation, high-signature preservation, and Poincare diameter behavior",
            "closure": "certify geodesic interval preservation at the d20 rewrite-complex readout level",
            "emit": "emit interval-sheaf JSON/CSV/NPZ, certificate, report, and next hyperbolic target",
        },
        "inputs": {
            "rewrite_complex_report": input_entry(
                REWRITE_COMPLEX_REPORT,
                {
                    "status": rewrite_report.get("status"),
                    "certificate_sha256": rewrite_report.get("certificate_sha256"),
                },
            ),
            "rewrite_complex": input_entry(REWRITE_COMPLEX_JSON),
            "rewrite_complex_tables": input_entry(REWRITE_COMPLEX_TABLES),
            "rewrite_complex_certificate": input_entry(REWRITE_COMPLEX_CERTIFICATE),
            "symbolic_rewrite_report": input_entry(
                SYMBOLIC_REWRITE_REPORT,
                {
                    "status": symbolic_rewrite_report.get("status"),
                    "certificate_sha256": symbolic_rewrite_report.get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "geodesic_interval_sheaf": relpath(OUT_DIR / "geodesic_interval_sheaf.json"),
            "geodesic_intervals_csv": relpath(OUT_DIR / "geodesic_intervals.csv"),
            "geodesic_interval_tables": relpath(OUT_DIR / "geodesic_interval_tables.npz"),
            "geodesic_interval_certificate": relpath(OUT_DIR / "geodesic_interval_certificate.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "geodesic interval stalks for all unordered node pairs of the 56-node rewrite complex",
                "shortest-path counts and interval-node membership tables",
                "full-sector and high-signature preservation flags for every interval",
                "the exact 46 intervals preserving both full-sector coverage and high-signature support",
                "Poincare endpoint and interval-diameter comparisons for the interval sheaf",
            ],
            "does_not_certify_because_not_required": [
                "arbitrary-length symbolic rewrite confluence",
                "new C985 associator or pentagon data beyond the existing certificate",
                "a packet bridge from d20 atoms to A985/tube coordinates",
                "pivotal, spherical, unitary, braiding, ribbon, or Drinfeld-center data",
            ],
        },
        "next_highest_yield_item": (
            "Collapse the 46 full-high geodesic intervals into a preserved-core "
            "subcomplex, then certify its connected components and hyperbolic "
            "boundary inside the 56-node rewrite complex."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_geodesic_interval_sheaf_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified rewrite-complex graph and Poincare tables",
            "materialize every unordered geodesic interval stalk",
            "count shortest paths and interval-node memberships",
            "check full-sector and high-signature preservation thresholds",
            "check source hashes and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "geodesic_interval_sheaf": interval_sheaf,
        "geodesic_intervals_csv": csv_text(INTERVAL_COLUMNS, interval_rows),
        "interval_table": interval_table,
        "interval_membership": membership_matrix,
        "geodesic_interval_certificate": certificate,
        "report": report,
        "manifest": manifest,
    }


def update_index(report: dict[str, Any]) -> None:
    if INDEX_PATH.exists():
        index_payload = load_json(INDEX_PATH)
        obligations = [
            row
            for row in index_payload.get("obligations", [])
            if isinstance(row, dict) and row.get("id") != THEOREM_ID
        ]
        schema = index_payload.get("schema", "d20.proof_obligation_registry.source_drop")
    else:
        obligations = []
        schema = "d20.proof_obligation_registry.source_drop"
    obligations.append(
        {
            "id": THEOREM_ID,
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
            "report_sha256": report["certificate_sha256"],
            "status": report["status"],
        }
    )
    updated = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": sorted(obligations, key=lambda row: row["id"]),
    }
    updated["registry_sha256"] = self_hash(updated, "registry_sha256")
    write_json(INDEX_PATH, updated)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / "geodesic_interval_sheaf.json", payloads["geodesic_interval_sheaf"])
    (OUT_DIR / "geodesic_intervals.csv").write_text(
        payloads["geodesic_intervals_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "geodesic_interval_tables.npz",
        interval_table=payloads["interval_table"],
        interval_membership=payloads["interval_membership"],
    )
    write_json(OUT_DIR / "geodesic_interval_certificate.json", payloads["geodesic_interval_certificate"])
    write_json(OUT_DIR / "report.json", payloads["report"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    update_index(payloads["report"])


def main() -> None:
    payloads = build_payloads()
    write_payloads(payloads)
    witness = payloads["report"]["witness"]
    print(
        json.dumps(
            {
                "status": payloads["report"]["status"],
                "all_checks_pass": payloads["report"]["all_checks_pass"],
                "report": relpath(OUT_DIR / "report.json"),
                "manifest": relpath(OUT_DIR / "manifest.json"),
                "certificate_sha256": payloads["report"]["certificate_sha256"],
                "interval_count": witness["interval_count"],
                "full_sector_preserving_interval_count": witness[
                    "full_sector_preserving_interval_count"
                ],
                "high_signature_preserving_interval_count": witness[
                    "high_signature_preserving_interval_count"
                ],
                "full_high_preserving_interval_count": witness[
                    "full_high_preserving_interval_count"
                ],
                "longest_full_high_graph_distance": witness["longest_full_high_graph_distance"],
                "next_highest_yield_item": payloads["report"]["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
