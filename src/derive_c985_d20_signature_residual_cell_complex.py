from __future__ import annotations

import csv
import json
from collections import Counter, deque
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_recurrent_signature_subboundary import (
        OUT_DIR as SIGNATURE_SUBBOUNDARY_DIR,
    )
    from .derive_c985_d20_signature_geodesic_residual_chart import (
        OUT_DIR as RESIDUAL_CHART_DIR,
    )
    from .derive_c985_d20_signature_transfer_spectral_cut import (
        OUT_DIR as SPECTRAL_CUT_DIR,
    )
    from .derive_c985_d20_symbolic_rewrite_rules import csv_text
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
    from derive_c985_d20_recurrent_signature_subboundary import (
        OUT_DIR as SIGNATURE_SUBBOUNDARY_DIR,
    )
    from derive_c985_d20_signature_geodesic_residual_chart import (
        OUT_DIR as RESIDUAL_CHART_DIR,
    )
    from derive_c985_d20_signature_transfer_spectral_cut import (
        OUT_DIR as SPECTRAL_CUT_DIR,
    )
    from derive_c985_d20_symbolic_rewrite_rules import csv_text
    from derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "c985_d20_signature_residual_cell_complex"
STATUS = "C985_D20_SIGNATURE_RESIDUAL_CELL_COMPLEX_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

RESIDUAL_CHART_REPORT = RESIDUAL_CHART_DIR / "report.json"
RESIDUAL_CHART_JSON = RESIDUAL_CHART_DIR / "signature_geodesic_residual_chart.json"
RESIDUAL_CHART_TABLES = (
    RESIDUAL_CHART_DIR / "signature_geodesic_residual_chart_tables.npz"
)
RESIDUAL_CHART_CERTIFICATE = (
    RESIDUAL_CHART_DIR / "signature_geodesic_residual_chart_certificate.json"
)
RESIDUAL_CHART_CARRIER_CSV = RESIDUAL_CHART_DIR / "carrier_residual_chart.csv"
RESIDUAL_CHART_SIGNATURE_CSV = RESIDUAL_CHART_DIR / "signature_residual_chart.csv"

SPECTRAL_CUT_REPORT = SPECTRAL_CUT_DIR / "report.json"
SPECTRAL_CUT_JSON = SPECTRAL_CUT_DIR / "signature_transfer_spectral_cut.json"
SPECTRAL_CUT_TABLES = SPECTRAL_CUT_DIR / "signature_transfer_spectral_cut_tables.npz"
SPECTRAL_CUT_CERTIFICATE = SPECTRAL_CUT_DIR / "signature_transfer_spectral_cut_certificate.json"
SPECTRAL_MASK_SUMMARY = SPECTRAL_CUT_DIR / "carrier_mask_eigenmode_summary.csv"

SIGNATURE_SUBBOUNDARY_REPORT = SIGNATURE_SUBBOUNDARY_DIR / "report.json"
SIGNATURE_SUBBOUNDARY_JSON = (
    SIGNATURE_SUBBOUNDARY_DIR / "recurrent_signature_subboundary.json"
)
SIGNATURE_SUBBOUNDARY_TABLES = (
    SIGNATURE_SUBBOUNDARY_DIR / "recurrent_signature_subboundary_tables.npz"
)
SIGNATURE_SUBBOUNDARY_CERTIFICATE = (
    SIGNATURE_SUBBOUNDARY_DIR / "recurrent_signature_subboundary_certificate.json"
)

DERIVE_SCRIPT = ROOT / "src" / "derive_c985_d20_signature_residual_cell_complex.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_d20_signature_residual_cell_complex.py"

PROBABILITY_SCALE = 1_000_000_000_000

REGION_HIGH = 2
REGION_CENTRAL = 1
REGION_NEGATIVE = -1

EDGE_WITHIN_HIGH = 0
EDGE_WITHIN_CENTRAL = 1
EDGE_WITHIN_NEGATIVE = 2
EDGE_HIGH_CENTRAL = 3
EDGE_HIGH_NEGATIVE = 4
EDGE_CENTRAL_NEGATIVE = 5

VERTEX_COLUMNS = [
    "carrier_mask_class_id",
    "carrier_atom_mask",
    "elbow_region_code",
    "nodal_sign",
    "positive_region_flag",
    "signature_class_count",
    "stationary_mass_x1e12",
    "mask_graph_degree",
    "computed_cut_boundary_degree",
    "spectral_cut_boundary_degree",
    "high_cap_flag",
    "central_gate_flag",
    "negative_region_flag",
    "axis_coordinate_x1e12",
    "signed_residual_coordinate_x1e12",
    "carrier_atom_id_0",
    "carrier_atom_id_1",
    "carrier_atom_id_2",
    "carrier_atom_id_3",
]

EDGE_COLUMNS = [
    "cell_edge_id",
    "source_carrier_mask_class_id",
    "target_carrier_mask_class_id",
    "source_region_code",
    "target_region_code",
    "source_nodal_sign",
    "target_nodal_sign",
    "edge_partition_code",
    "is_region_boundary",
    "is_positive_negative_boundary",
    "is_internal_positive_boundary",
    "source_carrier_atom_mask",
    "target_carrier_atom_mask",
]

SUMMARY_COLUMNS = [
    "summary_id",
    "summary_code",
    "vertex_count",
    "signature_class_count",
    "stationary_mass_x1e12",
    "edge_count",
    "boundary_edge_count",
    "component_count",
]

OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "carrier_vertex_count": 0,
    "carrier_edge_count": 1,
    "high_cap_vertex_count": 2,
    "central_gate_vertex_count": 3,
    "negative_region_vertex_count": 4,
    "high_cap_signature_count": 5,
    "central_gate_signature_count": 6,
    "negative_region_signature_count": 7,
    "high_cap_stationary_mass": 8,
    "central_gate_stationary_mass": 9,
    "negative_region_stationary_mass": 10,
    "positive_negative_boundary_edge_count": 11,
    "spectral_cut_mask_edge_count": 12,
    "high_negative_boundary_edge_count": 13,
    "central_negative_boundary_edge_count": 14,
    "high_central_internal_edge_count": 15,
    "central_internal_edge_count": 16,
    "negative_internal_edge_count": 17,
    "positive_region_component_count": 18,
    "negative_region_component_count": 19,
    "region_adjacency_edge_count": 20,
    "boundary_degree_l1_delta": 21,
    "spectral_boundary_symmetric_difference_count": 22,
}


def read_int_csv(path: Any) -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows.append({key: int(value) for key, value in row.items()})
    return rows


def edge_partition_code(left_region: int, right_region: int) -> int:
    pair = {int(left_region), int(right_region)}
    if pair == {REGION_HIGH}:
        return EDGE_WITHIN_HIGH
    if pair == {REGION_CENTRAL}:
        return EDGE_WITHIN_CENTRAL
    if pair == {REGION_NEGATIVE}:
        return EDGE_WITHIN_NEGATIVE
    if pair == {REGION_HIGH, REGION_CENTRAL}:
        return EDGE_HIGH_CENTRAL
    if pair == {REGION_HIGH, REGION_NEGATIVE}:
        return EDGE_HIGH_NEGATIVE
    if pair == {REGION_CENTRAL, REGION_NEGATIVE}:
        return EDGE_CENTRAL_NEGATIVE
    raise ValueError(f"unknown region pair: {left_region}, {right_region}")


def component_count(vertices: list[int], edges: list[tuple[int, int]]) -> int:
    vertex_set = {int(vertex) for vertex in vertices}
    if not vertex_set:
        return 0
    adjacency: dict[int, set[int]] = {vertex: set() for vertex in vertex_set}
    for left, right in edges:
        if left in vertex_set and right in vertex_set:
            adjacency[left].add(right)
            adjacency[right].add(left)
    remaining = set(vertex_set)
    count = 0
    while remaining:
        count += 1
        start = remaining.pop()
        queue: deque[int] = deque([start])
        while queue:
            node = queue.popleft()
            for neighbor in adjacency[node]:
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    queue.append(neighbor)
    return count


def table_from_rows(columns: list[str], rows: list[dict[str, int]]) -> np.ndarray:
    return np.asarray(
        [[int(row[column]) for column in columns] for row in rows],
        dtype=np.int64,
    )


def build_payloads() -> dict[str, Any]:
    residual_report = load_json(RESIDUAL_CHART_REPORT)
    residual_chart = load_json(RESIDUAL_CHART_JSON)
    residual_certificate = load_json(RESIDUAL_CHART_CERTIFICATE)
    spectral_report = load_json(SPECTRAL_CUT_REPORT)
    spectral_cut = load_json(SPECTRAL_CUT_JSON)
    spectral_certificate = load_json(SPECTRAL_CUT_CERTIFICATE)
    subboundary_report = load_json(SIGNATURE_SUBBOUNDARY_REPORT)
    subboundary = load_json(SIGNATURE_SUBBOUNDARY_JSON)
    subboundary_certificate = load_json(SIGNATURE_SUBBOUNDARY_CERTIFICATE)
    residual_tables = np.load(RESIDUAL_CHART_TABLES, allow_pickle=False)
    spectral_tables = np.load(SPECTRAL_CUT_TABLES, allow_pickle=False)
    subboundary_tables = np.load(SIGNATURE_SUBBOUNDARY_TABLES, allow_pickle=False)

    carrier_rows_source = read_int_csv(RESIDUAL_CHART_CARRIER_CSV)
    spectral_mask_rows = read_int_csv(SPECTRAL_MASK_SUMMARY)
    carrier_by_id = {
        int(row["carrier_mask_class_id"]): row for row in carrier_rows_source
    }
    spectral_by_id = {
        int(row["carrier_mask_class_id"]): row for row in spectral_mask_rows
    }
    adjacency = np.asarray(subboundary_tables["mask_class_adjacency"], dtype=np.int8)
    edge_pairs = [
        (left, right)
        for left in range(adjacency.shape[0])
        for right in range(left + 1, adjacency.shape[1])
        if int(adjacency[left, right]) != 0
    ]

    boundary_degree = Counter()
    edge_rows: list[dict[str, int]] = []
    region_pair_counter: Counter[int] = Counter()
    region_adjacency_pairs: set[tuple[int, int]] = set()
    positive_negative_boundary_edges: list[tuple[int, int]] = []
    for edge_id, (left, right) in enumerate(edge_pairs):
        left_row = carrier_by_id[left]
        right_row = carrier_by_id[right]
        left_region = int(left_row["elbow_region_code"])
        right_region = int(right_row["elbow_region_code"])
        partition_code = edge_partition_code(left_region, right_region)
        is_region_boundary = int(left_region != right_region)
        is_positive_negative_boundary = int((left_region > 0) != (right_region > 0))
        is_internal_positive_boundary = int(
            {left_region, right_region} == {REGION_HIGH, REGION_CENTRAL}
        )
        if is_positive_negative_boundary:
            positive_negative_boundary_edges.append((left, right))
            boundary_degree[left] += 1
            boundary_degree[right] += 1
        region_pair_counter[partition_code] += 1
        if is_region_boundary:
            region_adjacency_pairs.add(tuple(sorted((left_region, right_region))))
        edge_rows.append(
            {
                "cell_edge_id": edge_id,
                "source_carrier_mask_class_id": left,
                "target_carrier_mask_class_id": right,
                "source_region_code": left_region,
                "target_region_code": right_region,
                "source_nodal_sign": int(left_row["nodal_sign"]),
                "target_nodal_sign": int(right_row["nodal_sign"]),
                "edge_partition_code": partition_code,
                "is_region_boundary": is_region_boundary,
                "is_positive_negative_boundary": is_positive_negative_boundary,
                "is_internal_positive_boundary": is_internal_positive_boundary,
                "source_carrier_atom_mask": int(left_row["carrier_atom_mask"]),
                "target_carrier_atom_mask": int(right_row["carrier_atom_mask"]),
            }
        )

    vertex_rows: list[dict[str, int]] = []
    for carrier_id in sorted(carrier_by_id):
        row = carrier_by_id[carrier_id]
        region = int(row["elbow_region_code"])
        spectral_boundary_degree = int(
            spectral_by_id[carrier_id]["cut_boundary_mask_edge_count"]
        )
        vertex_rows.append(
            {
                "carrier_mask_class_id": carrier_id,
                "carrier_atom_mask": int(row["carrier_atom_mask"]),
                "elbow_region_code": region,
                "nodal_sign": int(row["nodal_sign"]),
                "positive_region_flag": int(region > 0),
                "signature_class_count": int(row["signature_class_count"]),
                "stationary_mass_x1e12": int(row["stationary_mass_x1e12"]),
                "mask_graph_degree": int(sum(int(value) for value in adjacency[carrier_id])),
                "computed_cut_boundary_degree": int(boundary_degree[carrier_id]),
                "spectral_cut_boundary_degree": spectral_boundary_degree,
                "high_cap_flag": int(region == REGION_HIGH),
                "central_gate_flag": int(region == REGION_CENTRAL),
                "negative_region_flag": int(region == REGION_NEGATIVE),
                "axis_coordinate_x1e12": int(row["axis_coordinate_x1e12"]),
                "signed_residual_coordinate_x1e12": int(
                    row["signed_residual_coordinate_x1e12"]
                ),
                "carrier_atom_id_0": int(row["carrier_atom_id_0"]),
                "carrier_atom_id_1": int(row["carrier_atom_id_1"]),
                "carrier_atom_id_2": int(row["carrier_atom_id_2"]),
                "carrier_atom_id_3": int(row["carrier_atom_id_3"]),
            }
        )

    high_ids = [row["carrier_mask_class_id"] for row in vertex_rows if row["elbow_region_code"] == REGION_HIGH]
    central_ids = [row["carrier_mask_class_id"] for row in vertex_rows if row["elbow_region_code"] == REGION_CENTRAL]
    negative_ids = [row["carrier_mask_class_id"] for row in vertex_rows if row["elbow_region_code"] == REGION_NEGATIVE]
    positive_ids = high_ids + central_ids

    def summarize(summary_id: int, summary_code: int, ids: list[int]) -> dict[str, int]:
        rows = [carrier_by_id[carrier_id] for carrier_id in ids]
        region_edges = [
            edge
            for edge in edge_pairs
            if edge[0] in set(ids) and edge[1] in set(ids)
        ]
        boundary_edges = [
            edge
            for edge in edge_pairs
            if (edge[0] in set(ids)) != (edge[1] in set(ids))
        ]
        return {
            "summary_id": summary_id,
            "summary_code": summary_code,
            "vertex_count": len(ids),
            "signature_class_count": sum(int(row["signature_class_count"]) for row in rows),
            "stationary_mass_x1e12": sum(int(row["stationary_mass_x1e12"]) for row in rows),
            "edge_count": len(region_edges),
            "boundary_edge_count": len(boundary_edges),
            "component_count": component_count(ids, edge_pairs),
        }

    summary_rows = [
        summarize(0, REGION_HIGH, high_ids),
        summarize(1, REGION_CENTRAL, central_ids),
        summarize(2, REGION_NEGATIVE, negative_ids),
        summarize(3, 10, positive_ids),
    ]

    spectral_boundary_edges = {
        tuple(sorted((int(row["source_carrier_mask_class_id"]), int(row["target_carrier_mask_class_id"]))))
        for row in edge_rows
        if int(row["source_nodal_sign"]) != int(row["target_nodal_sign"])
    }
    chart_boundary_edges = {tuple(edge) for edge in positive_negative_boundary_edges}
    boundary_symmetric_difference = chart_boundary_edges.symmetric_difference(
        spectral_boundary_edges
    )
    boundary_degree_l1_delta = sum(
        abs(
            int(row["computed_cut_boundary_degree"])
            - int(row["spectral_cut_boundary_degree"])
        )
        for row in vertex_rows
    )

    observable_values = {
        "carrier_vertex_count": len(vertex_rows),
        "carrier_edge_count": len(edge_rows),
        "high_cap_vertex_count": len(high_ids),
        "central_gate_vertex_count": len(central_ids),
        "negative_region_vertex_count": len(negative_ids),
        "high_cap_signature_count": summary_rows[0]["signature_class_count"],
        "central_gate_signature_count": summary_rows[1]["signature_class_count"],
        "negative_region_signature_count": summary_rows[2]["signature_class_count"],
        "high_cap_stationary_mass": summary_rows[0]["stationary_mass_x1e12"],
        "central_gate_stationary_mass": summary_rows[1]["stationary_mass_x1e12"],
        "negative_region_stationary_mass": summary_rows[2]["stationary_mass_x1e12"],
        "positive_negative_boundary_edge_count": len(positive_negative_boundary_edges),
        "spectral_cut_mask_edge_count": int(spectral_report["witness"]["mask_cut_edge_count"]),
        "high_negative_boundary_edge_count": region_pair_counter[EDGE_HIGH_NEGATIVE],
        "central_negative_boundary_edge_count": region_pair_counter[EDGE_CENTRAL_NEGATIVE],
        "high_central_internal_edge_count": region_pair_counter[EDGE_HIGH_CENTRAL],
        "central_internal_edge_count": region_pair_counter[EDGE_WITHIN_CENTRAL],
        "negative_internal_edge_count": region_pair_counter[EDGE_WITHIN_NEGATIVE],
        "positive_region_component_count": component_count(positive_ids, edge_pairs),
        "negative_region_component_count": component_count(negative_ids, edge_pairs),
        "region_adjacency_edge_count": len(region_adjacency_pairs),
        "boundary_degree_l1_delta": boundary_degree_l1_delta,
        "spectral_boundary_symmetric_difference_count": len(boundary_symmetric_difference),
    }
    observable_rows = [
        {
            "observable_id": index,
            "observable_code": int(code),
            "value_x1e12": int(observable_values[name]),
            "aux_id": -1,
        }
        for index, (name, code) in enumerate(
            sorted(OBSERVABLE_CODES.items(), key=lambda item: item[1])
        )
    ]

    vertex_table = table_from_rows(VERTEX_COLUMNS, vertex_rows)
    edge_table = table_from_rows(EDGE_COLUMNS, edge_rows)
    summary_table = table_from_rows(SUMMARY_COLUMNS, summary_rows)
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    cell_complex = {
        "schema": "c985.d20_signature_residual_cell_complex@1",
        "object": "d20",
        "cell_rule": {
            "zero_cells": "14 carrier-mask quotient classes from the recurrent signature subboundary",
            "one_cells": "44 carrier-mask quotient graph edges",
            "region_cells": "the residual-chart high-axis cap, central residual gate, and negative region",
            "boundary_comparison": "positive-negative residual region edges compared with the spectral nodal carrier-mask cut edges",
        },
        "region_cells": {
            "high_axis_cap": high_ids,
            "central_residual_gate": central_ids,
            "negative_region": negative_ids,
            "positive_region": positive_ids,
        },
        "region_adjacency": {
            "high_central_edge_count": int(region_pair_counter[EDGE_HIGH_CENTRAL]),
            "high_negative_edge_count": int(region_pair_counter[EDGE_HIGH_NEGATIVE]),
            "central_negative_edge_count": int(region_pair_counter[EDGE_CENTRAL_NEGATIVE]),
            "region_adjacency_pair_count": len(region_adjacency_pairs),
        },
        "spectral_boundary": {
            "positive_negative_boundary_edge_count": len(positive_negative_boundary_edges),
            "spectral_mask_cut_edge_count": int(spectral_report["witness"]["mask_cut_edge_count"]),
            "boundary_degree_l1_delta": boundary_degree_l1_delta,
            "symmetric_difference_count": len(boundary_symmetric_difference),
            "boundary_edges": [
                {"source": int(left), "target": int(right)}
                for left, right in positive_negative_boundary_edges
            ],
        },
        "carrier_region_vertices": [
            {key: int(value) for key, value in row.items()} for row in vertex_rows
        ],
        "carrier_region_edges": [
            {key: int(value) for key, value in row.items()} for row in edge_rows
        ],
    }

    checks = {
        "residual_chart_report_certified": residual_report.get("status")
        == "C985_D20_SIGNATURE_GEODESIC_RESIDUAL_CHART_CERTIFIED",
        "residual_chart_certificate_certified": residual_certificate.get("status")
        == "C985_D20_SIGNATURE_GEODESIC_RESIDUAL_CHART_CERTIFIED",
        "spectral_cut_report_certified": spectral_report.get("status")
        == "C985_D20_SIGNATURE_TRANSFER_SPECTRAL_CUT_CERTIFIED",
        "spectral_cut_certificate_certified": spectral_certificate.get("status")
        == "C985_D20_SIGNATURE_TRANSFER_SPECTRAL_CUT_CERTIFIED",
        "signature_subboundary_report_certified": subboundary_report.get("status")
        == "C985_D20_RECURRENT_SIGNATURE_SUBBOUNDARY_CERTIFIED",
        "signature_subboundary_certificate_certified": subboundary_certificate.get("status")
        == "C985_D20_RECURRENT_SIGNATURE_SUBBOUNDARY_CERTIFIED",
        "carrier_vertex_count_is_14": len(vertex_rows) == 14,
        "carrier_edge_count_is_44": len(edge_rows) == 44,
        "region_vertex_sets_match_residual_chart": (
            high_ids,
            central_ids,
            negative_ids,
        )
        == ([0, 1], [2, 3, 10, 11, 12], [4, 5, 6, 7, 8, 9, 13]),
        "region_masses_match_residual_chart": (
            summary_rows[0]["signature_class_count"],
            summary_rows[0]["stationary_mass_x1e12"],
            summary_rows[1]["signature_class_count"],
            summary_rows[1]["stationary_mass_x1e12"],
            summary_rows[2]["signature_class_count"],
            summary_rows[2]["stationary_mass_x1e12"],
        )
        == (24, 10418982028, 97, 615688126181, 100, 373892891791),
        "edge_partition_counts_match_expected": (
            region_pair_counter[EDGE_HIGH_CENTRAL],
            region_pair_counter[EDGE_HIGH_NEGATIVE],
            region_pair_counter[EDGE_CENTRAL_NEGATIVE],
            region_pair_counter[EDGE_WITHIN_CENTRAL],
            region_pair_counter[EDGE_WITHIN_NEGATIVE],
            region_pair_counter[EDGE_WITHIN_HIGH],
        )
        == (4, 2, 14, 10, 14, 0),
        "positive_negative_boundary_count_matches_spectral_cut": len(positive_negative_boundary_edges)
        == int(spectral_report["witness"]["mask_cut_edge_count"])
        == 16,
        "boundary_degrees_match_spectral_cut": boundary_degree_l1_delta == 0,
        "boundary_edge_set_matches_spectral_cut": len(boundary_symmetric_difference)
        == 0,
        "positive_region_is_connected": component_count(positive_ids, edge_pairs) == 1,
        "negative_region_is_connected": component_count(negative_ids, edge_pairs) == 1,
        "region_adjacency_graph_is_complete_triangle": region_adjacency_pairs
        == {
            tuple(sorted((REGION_HIGH, REGION_CENTRAL))),
            tuple(sorted((REGION_HIGH, REGION_NEGATIVE))),
            tuple(sorted((REGION_CENTRAL, REGION_NEGATIVE))),
        },
        "vertex_table_shape_is_14_by_19": tuple(vertex_table.shape)
        == (14, len(VERTEX_COLUMNS)),
        "edge_table_shape_is_44_by_13": tuple(edge_table.shape)
        == (44, len(EDGE_COLUMNS)),
        "summary_table_shape_is_4_by_8": tuple(summary_table.shape)
        == (4, len(SUMMARY_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
        "residual_chart_tables_available": "carrier_residual_chart_table"
        in residual_tables.files,
        "spectral_cut_tables_available": "mask_eigenmode_table" in spectral_tables.files,
        "signature_subboundary_tables_available": "mask_class_adjacency"
        in subboundary_tables.files,
        "residual_chart_json_schema_available": residual_chart.get("schema")
        == "c985.d20_signature_geodesic_residual_chart@1",
        "spectral_cut_json_schema_available": spectral_cut.get("schema")
        == "c985.d20_signature_transfer_spectral_cut@1",
        "signature_subboundary_json_schema_available": subboundary.get("schema")
        == "c985.d20_recurrent_signature_subboundary@1",
    }

    witness = {
        "carrier_vertex_count": observable_values["carrier_vertex_count"],
        "carrier_edge_count": observable_values["carrier_edge_count"],
        "high_cap_mask_class_ids": high_ids,
        "central_gate_mask_class_ids": central_ids,
        "negative_region_mask_class_ids": negative_ids,
        "positive_region_mask_class_ids": positive_ids,
        "region_signature_counts": {
            "high_cap": summary_rows[0]["signature_class_count"],
            "central_gate": summary_rows[1]["signature_class_count"],
            "negative_region": summary_rows[2]["signature_class_count"],
        },
        "region_stationary_masses_x1e12": {
            "high_cap": summary_rows[0]["stationary_mass_x1e12"],
            "central_gate": summary_rows[1]["stationary_mass_x1e12"],
            "negative_region": summary_rows[2]["stationary_mass_x1e12"],
        },
        "edge_partition_counts": {
            "high_central": int(region_pair_counter[EDGE_HIGH_CENTRAL]),
            "high_negative": int(region_pair_counter[EDGE_HIGH_NEGATIVE]),
            "central_negative": int(region_pair_counter[EDGE_CENTRAL_NEGATIVE]),
            "central_central": int(region_pair_counter[EDGE_WITHIN_CENTRAL]),
            "negative_negative": int(region_pair_counter[EDGE_WITHIN_NEGATIVE]),
            "high_high": int(region_pair_counter[EDGE_WITHIN_HIGH]),
        },
        "positive_negative_boundary_edge_count": len(positive_negative_boundary_edges),
        "spectral_mask_cut_edge_count": int(spectral_report["witness"]["mask_cut_edge_count"]),
        "boundary_degree_l1_delta": boundary_degree_l1_delta,
        "spectral_boundary_symmetric_difference_count": len(boundary_symmetric_difference),
        "positive_region_component_count": component_count(positive_ids, edge_pairs),
        "negative_region_component_count": component_count(negative_ids, edge_pairs),
        "region_adjacency_pair_count": len(region_adjacency_pairs),
        "carrier_region_vertex_table_sha256": sha_array(vertex_table),
        "carrier_region_edge_table_sha256": sha_array(edge_table),
        "region_boundary_summary_table_sha256": sha_array(summary_table),
        "cell_complex_observable_table_sha256": sha_array(observable_table),
    }

    certificate = {
        "schema": "c985.d20_signature_residual_cell_complex_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_RESIDUAL_CELL_COMPLEX_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the residual-chart high, central, and negative regions form a finite three-region cell structure on the 14-node carrier-mask quotient graph",
            "the positive region is connected even after being split into high-axis and central-residual cells",
            "the residual chart's positive-negative boundary has exactly the 16 carrier-mask crossing edges certified by the spectral cut",
            "per-carrier boundary degrees match the spectral cut boundary-degree table with zero L1 error",
            "the three region cells have complete region adjacency: high-central, high-negative, and central-negative contacts all occur",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_residual_cell_complex@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The exact two-coordinate residual chart induces a finite "
            "three-region cell complex on the carrier-mask quotient graph, and "
            "its positive-negative boundary is exactly the 16-edge carrier-mask "
            "spectral cut boundary."
        ),
        "stage_protocol": {
            "draft": "use the residual-chart regions as cells over the certified carrier-mask quotient graph",
            "witness": "materialize carrier-region vertices, graph edges, region summaries, and boundary observables",
            "coherence": "compare positive-negative region-boundary edges and degrees with the spectral cut",
            "closure": "certify finite cell adjacency without claiming a continuum cell decomposition",
            "emit": "emit cell-complex JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "residual_chart_report": input_entry(
                RESIDUAL_CHART_REPORT,
                {
                    "status": residual_report.get("status"),
                    "certificate_sha256": residual_report.get("certificate_sha256"),
                },
            ),
            "residual_chart": input_entry(RESIDUAL_CHART_JSON),
            "residual_chart_tables": input_entry(RESIDUAL_CHART_TABLES),
            "residual_chart_certificate": input_entry(RESIDUAL_CHART_CERTIFICATE),
            "residual_chart_carrier_csv": input_entry(RESIDUAL_CHART_CARRIER_CSV),
            "residual_chart_signature_csv": input_entry(RESIDUAL_CHART_SIGNATURE_CSV),
            "spectral_cut_report": input_entry(
                SPECTRAL_CUT_REPORT,
                {
                    "status": spectral_report.get("status"),
                    "certificate_sha256": spectral_report.get("certificate_sha256"),
                },
            ),
            "spectral_cut": input_entry(SPECTRAL_CUT_JSON),
            "spectral_cut_tables": input_entry(SPECTRAL_CUT_TABLES),
            "spectral_cut_certificate": input_entry(SPECTRAL_CUT_CERTIFICATE),
            "spectral_mask_summary": input_entry(SPECTRAL_MASK_SUMMARY),
            "signature_subboundary_report": input_entry(
                SIGNATURE_SUBBOUNDARY_REPORT,
                {
                    "status": subboundary_report.get("status"),
                    "certificate_sha256": subboundary_report.get("certificate_sha256"),
                },
            ),
            "signature_subboundary": input_entry(SIGNATURE_SUBBOUNDARY_JSON),
            "signature_subboundary_tables": input_entry(SIGNATURE_SUBBOUNDARY_TABLES),
            "signature_subboundary_certificate": input_entry(
                SIGNATURE_SUBBOUNDARY_CERTIFICATE
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_residual_cell_complex": relpath(
                OUT_DIR / "signature_residual_cell_complex.json"
            ),
            "carrier_region_vertices_csv": relpath(OUT_DIR / "carrier_region_vertices.csv"),
            "carrier_region_edges_csv": relpath(OUT_DIR / "carrier_region_edges.csv"),
            "region_boundary_summary_csv": relpath(OUT_DIR / "region_boundary_summary.csv"),
            "cell_complex_observables_csv": relpath(OUT_DIR / "cell_complex_observables.csv"),
            "signature_residual_cell_complex_tables": relpath(
                OUT_DIR / "signature_residual_cell_complex_tables.npz"
            ),
            "signature_residual_cell_complex_certificate": relpath(
                OUT_DIR / "signature_residual_cell_complex_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "finite carrier-mask region cells induced by the residual chart",
                "all 44 carrier-mask quotient graph edges classified by region contact type",
                "exact equality between residual-chart positive-negative boundary edges and spectral cut carrier-mask crossing edges",
                "connectedness of the positive and negative induced carrier regions",
            ],
            "does_not_certify_because_not_required": [
                "a continuum CW complex or manifold boundary",
                "a canonical cell decomposition beyond the declared residual-chart regions",
                "metric curvature of the three-region quotient",
                "new associator, pentagon, pivotal, spherical, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Lift the 16 certified boundary edges back to signature-transfer "
            "flux: split the 4,007 crossing signature edges by high-negative "
            "versus central-negative carrier contact and certify which boundary "
            "cell carries the cut conductance."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_residual_cell_complex_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified residual-chart, spectral-cut, and recurrent-subboundary artifacts",
            "classify all carrier-mask quotient graph vertices and edges by residual-chart region",
            "compare residual positive-negative region boundary with spectral carrier-mask cut",
            "verify boundary-degree equality, region connectedness, and table reproducibility",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_residual_cell_complex": cell_complex,
        "carrier_region_vertices_csv": csv_text(VERTEX_COLUMNS, vertex_rows),
        "carrier_region_edges_csv": csv_text(EDGE_COLUMNS, edge_rows),
        "region_boundary_summary_csv": csv_text(SUMMARY_COLUMNS, summary_rows),
        "cell_complex_observables_csv": csv_text(OBSERVABLE_COLUMNS, observable_rows),
        "carrier_region_vertex_table": vertex_table,
        "carrier_region_edge_table": edge_table,
        "region_boundary_summary_table": summary_table,
        "cell_complex_observable_table": observable_table,
        "signature_residual_cell_complex_certificate": certificate,
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
    write_json(
        OUT_DIR / "signature_residual_cell_complex.json",
        payloads["signature_residual_cell_complex"],
    )
    (OUT_DIR / "carrier_region_vertices.csv").write_text(
        payloads["carrier_region_vertices_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "carrier_region_edges.csv").write_text(
        payloads["carrier_region_edges_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "region_boundary_summary.csv").write_text(
        payloads["region_boundary_summary_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "cell_complex_observables.csv").write_text(
        payloads["cell_complex_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_residual_cell_complex_tables.npz",
        carrier_region_vertex_table=payloads["carrier_region_vertex_table"],
        carrier_region_edge_table=payloads["carrier_region_edge_table"],
        region_boundary_summary_table=payloads["region_boundary_summary_table"],
        cell_complex_observable_table=payloads["cell_complex_observable_table"],
    )
    write_json(
        OUT_DIR / "signature_residual_cell_complex_certificate.json",
        payloads["signature_residual_cell_complex_certificate"],
    )
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
                "carrier_vertex_count": witness["carrier_vertex_count"],
                "carrier_edge_count": witness["carrier_edge_count"],
                "edge_partition_counts": witness["edge_partition_counts"],
                "positive_negative_boundary_edge_count": witness[
                    "positive_negative_boundary_edge_count"
                ],
                "boundary_degree_l1_delta": witness["boundary_degree_l1_delta"],
                "next_highest_yield_item": payloads["report"][
                    "next_highest_yield_item"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
