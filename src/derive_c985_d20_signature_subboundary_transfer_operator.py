from __future__ import annotations

import json
from fractions import Fraction
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_boundary_transfer_operator import (
        OUT_DIR as BOUNDARY_TRANSFER_DIR,
    )
    from .derive_c985_d20_recurrent_signature_subboundary import (
        OUT_DIR as SIGNATURE_SUBBOUNDARY_DIR,
        atom_ids_from_mask,
        padded_atom_ids,
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
    from derive_c985_d20_boundary_transfer_operator import (
        OUT_DIR as BOUNDARY_TRANSFER_DIR,
    )
    from derive_c985_d20_recurrent_signature_subboundary import (
        OUT_DIR as SIGNATURE_SUBBOUNDARY_DIR,
        atom_ids_from_mask,
        padded_atom_ids,
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


THEOREM_ID = "c985_d20_signature_subboundary_transfer_operator"
STATUS = "C985_D20_SIGNATURE_SUBBOUNDARY_TRANSFER_OPERATOR_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

SIGNATURE_SUBBOUNDARY_REPORT = SIGNATURE_SUBBOUNDARY_DIR / "report.json"
SIGNATURE_SUBBOUNDARY_JSON = SIGNATURE_SUBBOUNDARY_DIR / "recurrent_signature_subboundary.json"
SIGNATURE_SUBBOUNDARY_TABLES = (
    SIGNATURE_SUBBOUNDARY_DIR / "recurrent_signature_subboundary_tables.npz"
)
SIGNATURE_SUBBOUNDARY_CERTIFICATE = (
    SIGNATURE_SUBBOUNDARY_DIR / "recurrent_signature_subboundary_certificate.json"
)

BOUNDARY_TRANSFER_REPORT = BOUNDARY_TRANSFER_DIR / "report.json"
BOUNDARY_TRANSFER_JSON = BOUNDARY_TRANSFER_DIR / "boundary_transfer_operator.json"
BOUNDARY_TRANSFER_TABLES = BOUNDARY_TRANSFER_DIR / "boundary_transfer_tables.npz"
BOUNDARY_TRANSFER_CERTIFICATE = BOUNDARY_TRANSFER_DIR / "boundary_transfer_certificate.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_c985_d20_signature_subboundary_transfer_operator.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_d20_signature_subboundary_transfer_operator.py"

PROBABILITY_SCALE = 1_000_000_000_000

SIGNATURE_TRANSFER_EDGE_COLUMNS = [
    "transfer_edge_id",
    "source_signature_class_id",
    "target_signature_class_id",
    "shared_active_atom_count",
    "source_carrier_atom_mask",
    "target_carrier_atom_mask",
    "source_signature_flow_mass_x1e12",
    "target_signature_flow_mass_x1e12",
    "source_to_target_probability_x1e12",
    "target_to_source_probability_x1e12",
    "undirected_stationary_flux_x1e12",
]

SIGNATURE_STATIONARY_COLUMNS = [
    "signature_vertex_id",
    "signature_class_id",
    "stationary_mass_x1e12",
    "signature_flow_mass_x1e12",
    "stationary_to_flow_delta_x1e12",
    "carrier_atom_mask",
    "active_atom_count",
    "degree",
    "carrier_mask_class_id",
    "stationary_rank",
    "signature_flow_rank",
]

MASK_STATIONARY_COLUMNS = [
    "carrier_mask_class_id",
    "carrier_atom_mask",
    "signature_class_count",
    "stationary_mass_x1e12",
    "signature_flow_mass_x1e12",
    "stationary_to_flow_delta_x1e12",
    "mask_stationary_rank",
    "mask_flow_rank",
    "mask_graph_degree",
    "carrier_atom_id_0",
    "carrier_atom_id_1",
    "carrier_atom_id_2",
    "carrier_atom_id_3",
]

ATOM_STATIONARY_COLUMNS = [
    "atom_id",
    "stationary_participation_mass_x1e12",
    "signature_flow_participation_mass_x1e12",
    "stationary_to_flow_delta_x1e12",
    "stationary_rank",
    "signature_flow_rank",
    "carrier_signature_count",
]

SIGNATURE_TRANSFER_OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "active_signature_count": 0,
    "transfer_edge_count": 1,
    "top_stationary_signature_mass": 2,
    "top_stationary_signature_count": 3,
    "stationary_entropy": 4,
    "stationary_perplexity": 5,
    "spectral_gap": 6,
    "spectral_second_modulus": 7,
    "core_spectral_gap": 8,
    "spectral_gap_delta_vs_core": 9,
    "spectral_gap_ratio_to_core": 10,
    "stationary_flow_total_variation": 11,
    "stationary_flow_correlation": 12,
    "row_entropy_min": 13,
    "row_entropy_max": 14,
    "row_entropy_mean": 15,
    "row_entropy_stationary_mean": 16,
    "transition_probability_min": 17,
    "transition_probability_max": 18,
    "undirected_stationary_flux_min": 19,
    "undirected_stationary_flux_max": 20,
    "top_mask_stationary_mass": 21,
    "top_atom_stationary_mass": 22,
}


def scaled_float(value: float) -> int:
    return int(round(float(value) * PROBABILITY_SCALE))


def ranks_descending(values: dict[int, int]) -> dict[int, int]:
    return {
        key: rank
        for rank, key in enumerate(
            sorted(values, key=lambda item: (-int(values[item]), int(item))),
            start=1,
        )
    }


def scale_rational_vector(
    numerators: list[int],
    denominator: int,
    *,
    scale: int = PROBABILITY_SCALE,
) -> list[int]:
    floors = [(int(numerator) * scale) // int(denominator) for numerator in numerators]
    remainder = scale - sum(floors)
    residues = [
        (int(numerator) * scale) % int(denominator)
        for numerator in numerators
    ]
    order = sorted(range(len(numerators)), key=lambda index: (-residues[index], index))
    scaled = floors[:]
    for index in order[:remainder]:
        scaled[index] += 1
    return [int(value) for value in scaled]


def scale_fraction_vector(
    values: list[Fraction],
    *,
    scale: int = PROBABILITY_SCALE,
) -> list[int]:
    floors = [
        (value.numerator * scale) // value.denominator
        for value in values
    ]
    remainder = scale - sum(floors)
    residues = [
        Fraction((value.numerator * scale) % value.denominator, value.denominator)
        for value in values
    ]
    order = sorted(range(len(values)), key=lambda index: (-residues[index], index))
    scaled = floors[:]
    for index in order[:remainder]:
        scaled[index] += 1
    return [int(value) for value in scaled]


def table_from_rows(columns: list[str], rows: list[dict[str, int]]) -> np.ndarray:
    return np.asarray([[int(row[column]) for column in columns] for row in rows], dtype=np.int64)


def transition_support_components(support: np.ndarray) -> int:
    node_count = int(support.shape[0])
    seen: set[int] = set()
    count = 0
    for start in range(node_count):
        if start in seen:
            continue
        count += 1
        stack = [start]
        seen.add(start)
        while stack:
            node = stack.pop()
            for neighbor in np.nonzero(support[node])[0]:
                neighbor_id = int(neighbor)
                if neighbor_id not in seen:
                    seen.add(neighbor_id)
                    stack.append(neighbor_id)
    return count


def build_kernel(
    vertex_table: np.ndarray,
    edge_table: np.ndarray,
) -> dict[str, Any]:
    vertex_count = int(vertex_table.shape[0])
    signature_ids = [int(value) for value in vertex_table[:, 1]]
    signature_mass = [int(value) for value in vertex_table[:, 2]]
    class_to_index = {signature_id: index for index, signature_id in enumerate(signature_ids)}

    shared = np.zeros((vertex_count, vertex_count), dtype=np.int64)
    for row in edge_table:
        source = class_to_index[int(row[1])]
        target = class_to_index[int(row[2])]
        shared[source, target] = int(row[3])
        shared[target, source] = int(row[3])

    row_weight = [
        int(sum(int(shared[source, target]) * signature_mass[target] for target in range(vertex_count)))
        for source in range(vertex_count)
    ]
    conductance_degree = [
        int(signature_mass[source]) * int(row_weight[source])
        for source in range(vertex_count)
    ]
    total_degree = int(sum(conductance_degree))

    transition_matrix_x1e12 = np.zeros((vertex_count, vertex_count), dtype=np.int64)
    for source in range(vertex_count):
        numerators = [
            int(shared[source, target]) * signature_mass[target]
            for target in range(vertex_count)
        ]
        transition_matrix_x1e12[source, :] = np.asarray(
            scale_rational_vector(numerators, row_weight[source]),
            dtype=np.int64,
        )

    stationary_scaled = np.asarray(
        scale_rational_vector(conductance_degree, total_degree),
        dtype=np.int64,
    )

    transition_matrix = np.zeros((vertex_count, vertex_count), dtype=np.float64)
    for source in range(vertex_count):
        transition_matrix[source, :] = [
            (int(shared[source, target]) * signature_mass[target]) / row_weight[source]
            for target in range(vertex_count)
        ]
    stationary = np.asarray(
        [degree / total_degree for degree in conductance_degree],
        dtype=np.float64,
    )

    symmetric_similarity = np.zeros((vertex_count, vertex_count), dtype=np.float64)
    for source in range(vertex_count):
        for target in np.nonzero(shared[source])[0]:
            conductance = (
                float(shared[source, target])
                * float(signature_mass[source] / PROBABILITY_SCALE)
                * float(signature_mass[target] / PROBABILITY_SCALE)
            )
            source_degree = float(conductance_degree[source]) / (PROBABILITY_SCALE**2)
            target_degree = float(conductance_degree[int(target)]) / (PROBABILITY_SCALE**2)
            symmetric_similarity[source, int(target)] = conductance / (
                source_degree * target_degree
            ) ** 0.5

    eigenvalues = np.sort(np.linalg.eigvalsh(symmetric_similarity))[::-1]
    second_modulus = max(abs(float(eigenvalues[1])), abs(float(eigenvalues[-1])))
    spectral_gap = 1.0 - second_modulus

    return {
        "shared_active_atom_matrix": shared,
        "transition_matrix_x1e12": transition_matrix_x1e12,
        "transition_matrix": transition_matrix,
        "stationary_scaled": stationary_scaled,
        "stationary": stationary,
        "row_weight": row_weight,
        "conductance_degree": conductance_degree,
        "total_degree": total_degree,
        "symmetric_similarity_eigenvalues": eigenvalues,
        "symmetric_similarity_spectrum_x1e12": np.asarray(
            [scaled_float(value) for value in eigenvalues],
            dtype=np.int64,
        ),
        "spectral_second_modulus_x1e12": scaled_float(second_modulus),
        "spectral_gap_x1e12": scaled_float(spectral_gap),
        "support_component_count": transition_support_components(shared > 0),
        "stationary_residual_max_x1e12": scaled_float(
            float(np.max(np.abs(stationary @ transition_matrix - stationary)))
        ),
        "row_sum_residual_max_x1e12": scaled_float(
            float(np.max(np.abs(transition_matrix.sum(axis=1) - 1.0)))
        ),
    }


def stationary_atom_rows(
    vertex_table: np.ndarray,
    stationary_degrees: list[int],
    total_degree: int,
) -> tuple[list[dict[str, int]], np.ndarray]:
    stationary_parts = [Fraction(0, 1) for _ in range(20)]
    flow_parts = [Fraction(0, 1) for _ in range(20)]
    carrier_counts = {atom_id: 0 for atom_id in range(20)}
    for vertex_id, row in enumerate(vertex_table):
        carrier_ids = atom_ids_from_mask(int(row[5]))
        for atom_id in carrier_ids:
            stationary_parts[atom_id] += Fraction(
                int(stationary_degrees[vertex_id]),
                int(total_degree) * len(carrier_ids),
            )
            flow_parts[atom_id] += Fraction(
                int(row[3]),
                PROBABILITY_SCALE * len(carrier_ids),
            )
            carrier_counts[atom_id] += 1

    stationary_scaled = scale_fraction_vector(stationary_parts)
    flow_scaled = scale_fraction_vector(flow_parts)
    stationary_ranks = ranks_descending(
        {atom_id: stationary_scaled[atom_id] for atom_id in range(20)}
    )
    flow_ranks = ranks_descending({atom_id: flow_scaled[atom_id] for atom_id in range(20)})

    rows: list[dict[str, int]] = []
    for atom_id in range(20):
        if stationary_scaled[atom_id] == 0 and flow_scaled[atom_id] == 0:
            continue
        rows.append(
            {
                "atom_id": atom_id,
                "stationary_participation_mass_x1e12": int(stationary_scaled[atom_id]),
                "signature_flow_participation_mass_x1e12": int(flow_scaled[atom_id]),
                "stationary_to_flow_delta_x1e12": int(
                    stationary_scaled[atom_id] - flow_scaled[atom_id]
                ),
                "stationary_rank": int(stationary_ranks[atom_id]),
                "signature_flow_rank": int(flow_ranks[atom_id]),
                "carrier_signature_count": int(carrier_counts[atom_id]),
            }
        )
    return rows, table_from_rows(ATOM_STATIONARY_COLUMNS, rows)


def build_payloads() -> dict[str, Any]:
    subboundary_report = load_json(SIGNATURE_SUBBOUNDARY_REPORT)
    subboundary = load_json(SIGNATURE_SUBBOUNDARY_JSON)
    subboundary_certificate = load_json(SIGNATURE_SUBBOUNDARY_CERTIFICATE)
    boundary_transfer_report = load_json(BOUNDARY_TRANSFER_REPORT)
    boundary_transfer = load_json(BOUNDARY_TRANSFER_JSON)
    boundary_transfer_certificate = load_json(BOUNDARY_TRANSFER_CERTIFICATE)
    subboundary_tables = np.load(SIGNATURE_SUBBOUNDARY_TABLES, allow_pickle=False)
    boundary_transfer_tables = np.load(BOUNDARY_TRANSFER_TABLES, allow_pickle=False)

    source_vertex_table = np.asarray(subboundary_tables["signature_vertex_table"], dtype=np.int64)
    source_edge_table = np.asarray(subboundary_tables["signature_edge_table"], dtype=np.int64)
    source_mask_table = np.asarray(subboundary_tables["carrier_mask_class_table"], dtype=np.int64)
    source_adjacency = np.asarray(subboundary_tables["signature_adjacency"], dtype=np.int8)
    kernel = build_kernel(source_vertex_table, source_edge_table)

    stationary_scaled = np.asarray(kernel["stationary_scaled"], dtype=np.int64)
    transition_matrix_x1e12 = np.asarray(kernel["transition_matrix_x1e12"], dtype=np.int64)
    shared = np.asarray(kernel["shared_active_atom_matrix"], dtype=np.int64)
    signature_mass = [int(value) for value in source_vertex_table[:, 2]]
    signature_ids = [int(value) for value in source_vertex_table[:, 1]]
    class_to_index = {signature_id: index for index, signature_id in enumerate(signature_ids)}

    stationary_ranks = ranks_descending(
        {int(row[1]): int(stationary_scaled[index]) for index, row in enumerate(source_vertex_table)}
    )

    stationary_rows: list[dict[str, int]] = []
    for vertex_id, row in enumerate(source_vertex_table):
        signature_id = int(row[1])
        stationary_rows.append(
            {
                "signature_vertex_id": int(row[0]),
                "signature_class_id": signature_id,
                "stationary_mass_x1e12": int(stationary_scaled[vertex_id]),
                "signature_flow_mass_x1e12": int(row[2]),
                "stationary_to_flow_delta_x1e12": int(stationary_scaled[vertex_id] - int(row[2])),
                "carrier_atom_mask": int(row[3]),
                "active_atom_count": int(row[4]),
                "degree": int(row[5]),
                "carrier_mask_class_id": int(row[7]),
                "stationary_rank": int(stationary_ranks[signature_id]),
                "signature_flow_rank": int(row[8]),
            }
        )

    undirected_flux_numerators: list[int] = []
    for edge in source_edge_table:
        source = class_to_index[int(edge[1])]
        target = class_to_index[int(edge[2])]
        undirected_flux_numerators.append(
            2
            * signature_mass[source]
            * int(edge[3])
            * signature_mass[target]
        )
    undirected_flux_scaled = scale_rational_vector(
        undirected_flux_numerators,
        int(kernel["total_degree"]),
    )

    edge_rows: list[dict[str, int]] = []
    for edge_index, edge in enumerate(source_edge_table):
        source = class_to_index[int(edge[1])]
        target = class_to_index[int(edge[2])]
        edge_rows.append(
            {
                "transfer_edge_id": int(edge[0]),
                "source_signature_class_id": int(edge[1]),
                "target_signature_class_id": int(edge[2]),
                "shared_active_atom_count": int(edge[3]),
                "source_carrier_atom_mask": int(edge[4]),
                "target_carrier_atom_mask": int(edge[5]),
                "source_signature_flow_mass_x1e12": int(signature_mass[source]),
                "target_signature_flow_mass_x1e12": int(signature_mass[target]),
                "source_to_target_probability_x1e12": int(
                    transition_matrix_x1e12[source, target]
                ),
                "target_to_source_probability_x1e12": int(
                    transition_matrix_x1e12[target, source]
                ),
                "undirected_stationary_flux_x1e12": int(
                    undirected_flux_scaled[edge_index]
                ),
            }
        )

    mask_stationary_values: dict[int, int] = {}
    mask_flow_values: dict[int, int] = {}
    mask_class_counts: dict[int, int] = {}
    for vertex_id, row in enumerate(source_vertex_table):
        mask_class = int(row[7])
        mask_stationary_values[mask_class] = (
            mask_stationary_values.get(mask_class, 0) + int(stationary_scaled[vertex_id])
        )
        mask_flow_values[mask_class] = mask_flow_values.get(mask_class, 0) + int(row[2])
        mask_class_counts[mask_class] = mask_class_counts.get(mask_class, 0) + 1
    mask_stationary_ranks = ranks_descending(mask_stationary_values)
    mask_flow_ranks = ranks_descending(mask_flow_values)

    mask_rows: list[dict[str, int]] = []
    for row in source_mask_table:
        mask_class = int(row[0])
        carrier_ids = atom_ids_from_mask(int(row[1]))
        padded = padded_atom_ids(carrier_ids)
        mask_rows.append(
            {
                "carrier_mask_class_id": mask_class,
                "carrier_atom_mask": int(row[1]),
                "signature_class_count": int(mask_class_counts[mask_class]),
                "stationary_mass_x1e12": int(mask_stationary_values[mask_class]),
                "signature_flow_mass_x1e12": int(mask_flow_values[mask_class]),
                "stationary_to_flow_delta_x1e12": int(
                    mask_stationary_values[mask_class] - mask_flow_values[mask_class]
                ),
                "mask_stationary_rank": int(mask_stationary_ranks[mask_class]),
                "mask_flow_rank": int(mask_flow_ranks[mask_class]),
                "mask_graph_degree": int(row[5]),
                "carrier_atom_id_0": padded[0],
                "carrier_atom_id_1": padded[1],
                "carrier_atom_id_2": padded[2],
                "carrier_atom_id_3": padded[3],
            }
        )

    atom_rows, atom_table = stationary_atom_rows(
        np.asarray(
            [
                [
                    int(row["signature_vertex_id"]),
                    int(row["signature_class_id"]),
                    int(row["stationary_mass_x1e12"]),
                    int(row["signature_flow_mass_x1e12"]),
                    int(row["stationary_to_flow_delta_x1e12"]),
                    int(row["carrier_atom_mask"]),
                ]
                for row in stationary_rows
            ],
            dtype=np.int64,
        ),
        [int(value) for value in kernel["conductance_degree"]],
        int(kernel["total_degree"]),
    )

    stationary_table = table_from_rows(SIGNATURE_STATIONARY_COLUMNS, stationary_rows)
    edge_table = table_from_rows(SIGNATURE_TRANSFER_EDGE_COLUMNS, edge_rows)
    mask_table = table_from_rows(MASK_STATIONARY_COLUMNS, mask_rows)

    stationary = np.asarray(kernel["stationary"], dtype=np.float64)
    signature_flow = np.asarray(signature_mass, dtype=np.float64) / PROBABILITY_SCALE
    total_variation = 0.5 * float(np.sum(np.abs(stationary - signature_flow)))
    stationary_flow_correlation = float(np.corrcoef(stationary, signature_flow)[0, 1])
    stationary_entropy = float(-np.sum(stationary * np.log(stationary)))
    stationary_perplexity = float(np.exp(stationary_entropy))
    transition_matrix = np.asarray(kernel["transition_matrix"], dtype=np.float64)
    row_entropies = np.asarray(
        [
            -np.sum(row[row > 0] * np.log(row[row > 0]))
            for row in transition_matrix
        ],
        dtype=np.float64,
    )
    positive_probabilities = transition_matrix_x1e12[transition_matrix_x1e12 > 0]
    undirected_flux_array = np.asarray(undirected_flux_scaled, dtype=np.int64)
    core_gap_x1e12 = int(boundary_transfer_report["witness"]["spectral_gap_x1e12"])
    spectral_gap_x1e12 = int(kernel["spectral_gap_x1e12"])
    top_stationary_mass = int(stationary_scaled.max())
    top_stationary_ids = [
        int(source_vertex_table[index, 1])
        for index, value in enumerate(stationary_scaled)
        if int(value) == top_stationary_mass
    ]
    top_mask_mass = max(mask_stationary_values.values())
    top_mask_class_ids = [
        int(mask_class)
        for mask_class, value in mask_stationary_values.items()
        if int(value) == top_mask_mass
    ]
    top_atom_mass = max(int(row["stationary_participation_mass_x1e12"]) for row in atom_rows)
    top_atom_ids = [
        int(row["atom_id"])
        for row in atom_rows
        if int(row["stationary_participation_mass_x1e12"]) == top_atom_mass
    ]

    observable_values = {
        "active_signature_count": int(source_vertex_table.shape[0]),
        "transfer_edge_count": int(source_edge_table.shape[0]),
        "top_stationary_signature_mass": top_stationary_mass,
        "top_stationary_signature_count": len(top_stationary_ids),
        "stationary_entropy": scaled_float(stationary_entropy),
        "stationary_perplexity": scaled_float(stationary_perplexity),
        "spectral_gap": spectral_gap_x1e12,
        "spectral_second_modulus": int(kernel["spectral_second_modulus_x1e12"]),
        "core_spectral_gap": core_gap_x1e12,
        "spectral_gap_delta_vs_core": spectral_gap_x1e12 - core_gap_x1e12,
        "spectral_gap_ratio_to_core": scaled_float(
            spectral_gap_x1e12 / core_gap_x1e12
        ),
        "stationary_flow_total_variation": scaled_float(total_variation),
        "stationary_flow_correlation": scaled_float(stationary_flow_correlation),
        "row_entropy_min": scaled_float(float(row_entropies.min())),
        "row_entropy_max": scaled_float(float(row_entropies.max())),
        "row_entropy_mean": scaled_float(float(row_entropies.mean())),
        "row_entropy_stationary_mean": scaled_float(float(np.dot(stationary, row_entropies))),
        "transition_probability_min": int(positive_probabilities.min()),
        "transition_probability_max": int(positive_probabilities.max()),
        "undirected_stationary_flux_min": int(undirected_flux_array.min()),
        "undirected_stationary_flux_max": int(undirected_flux_array.max()),
        "top_mask_stationary_mass": int(top_mask_mass),
        "top_atom_stationary_mass": int(top_atom_mass),
    }

    observable_rows: list[dict[str, int]] = []
    for name, code in sorted(OBSERVABLE_CODES.items(), key=lambda item: item[1]):
        observable_rows.append(
            {
                "observable_id": len(observable_rows),
                "observable_code": int(code),
                "value_x1e12": int(observable_values[name]),
                "aux_id": -1,
            }
        )
    observable_table = table_from_rows(
        SIGNATURE_TRANSFER_OBSERVABLE_COLUMNS,
        observable_rows,
    )

    transfer_operator = {
        "schema": "c985.d20_signature_subboundary_transfer_operator@1",
        "object": "d20",
        "transfer_rule": {
            "vertices": "the 221 active relation-signature classes of the recurrent signature subboundary",
            "support": "the certified shared-active-carrier signature-intersection graph",
            "edge_conductance": "c_ij = shared_active_atom_count(i,j) * signature_flow_mass_i * signature_flow_mass_j",
            "transition_probability": "P_ij = c_ij / sum_k c_ik, equivalently shared(i,j) * mass_j / sum_k shared(i,k) * mass_k",
            "stationary_measure": "pi_i is proportional to sum_j c_ij; the chain is reversible by symmetric conductance",
        },
        "source_support": {
            "active_signature_class_count": int(source_vertex_table.shape[0]),
            "transfer_edge_count": int(source_edge_table.shape[0]),
            "carrier_mask_count": int(source_mask_table.shape[0]),
            "subboundary_diameter": int(subboundary_report["witness"]["signature_graph_diameter"]),
            "subboundary_delta_fraction": subboundary_report["witness"][
                "signature_graph_delta_fraction"
            ],
        },
        "stationary_summary": {
            "stationary_mass_sum_x1e12": int(stationary_scaled.sum()),
            "top_signature_class_ids": top_stationary_ids,
            "top_stationary_mass_x1e12": top_stationary_mass,
            "minimum_stationary_mass_x1e12": int(stationary_scaled.min()),
            "minimum_stationary_signature_class_ids": [
                int(source_vertex_table[index, 1])
                for index, value in enumerate(stationary_scaled)
                if int(value) == int(stationary_scaled.min())
            ],
            "stationary_entropy_x1e12": scaled_float(stationary_entropy),
            "stationary_perplexity_x1e12": scaled_float(stationary_perplexity),
            "stationary_flow_total_variation_x1e12": scaled_float(total_variation),
            "stationary_flow_correlation_x1e12": scaled_float(stationary_flow_correlation),
        },
        "spectral_summary": {
            "spectral_gap_x1e12": spectral_gap_x1e12,
            "spectral_second_modulus_x1e12": int(kernel["spectral_second_modulus_x1e12"]),
            "lambda_2_x1e12": int(kernel["symmetric_similarity_spectrum_x1e12"][1]),
            "lambda_min_x1e12": int(kernel["symmetric_similarity_spectrum_x1e12"][-1]),
            "positive_eigenvalue_count_above_1e_minus_9": int(
                np.sum(np.asarray(kernel["symmetric_similarity_eigenvalues"]) > 1e-9)
            ),
            "stationary_residual_max_x1e12": int(kernel["stationary_residual_max_x1e12"]),
            "row_sum_residual_max_x1e12": int(kernel["row_sum_residual_max_x1e12"]),
        },
        "comparison_with_core_transfer": {
            "core_spectral_gap_x1e12": core_gap_x1e12,
            "signature_spectral_gap_x1e12": spectral_gap_x1e12,
            "signature_gap_delta_x1e12": spectral_gap_x1e12 - core_gap_x1e12,
            "signature_gap_ratio_to_core_x1e12": scaled_float(
                spectral_gap_x1e12 / core_gap_x1e12
            ),
            "core_recurrent_support_node_count": int(
                boundary_transfer_report["witness"]["recurrent_support_node_count"]
            ),
            "signature_recurrent_support_node_count": int(source_vertex_table.shape[0]),
        },
        "mask_stationary_summary": {
            "top_mask_class_ids": top_mask_class_ids,
            "top_mask_stationary_mass_x1e12": int(top_mask_mass),
            "top_mask_carrier_atom_masks": [
                int(row["carrier_atom_mask"])
                for row in mask_rows
                if int(row["carrier_mask_class_id"]) in top_mask_class_ids
            ],
        },
        "atom_stationary_summary": {
            "top_atom_ids": top_atom_ids,
            "top_atom_stationary_mass_x1e12": int(top_atom_mass),
            "stationary_atom_order": [
                int(row["atom_id"])
                for row in sorted(atom_rows, key=lambda item: int(item["stationary_rank"]))
            ],
        },
        "top_stationary_signature_classes": [
            {
                "signature_class_id": int(row["signature_class_id"]),
                "stationary_mass_x1e12": int(row["stationary_mass_x1e12"]),
                "signature_flow_mass_x1e12": int(row["signature_flow_mass_x1e12"]),
                "carrier_atom_mask": int(row["carrier_atom_mask"]),
                "carrier_atom_ids": atom_ids_from_mask(int(row["carrier_atom_mask"])),
                "stationary_rank": int(row["stationary_rank"]),
                "signature_flow_rank": int(row["signature_flow_rank"]),
            }
            for row in sorted(stationary_rows, key=lambda item: int(item["stationary_rank"]))[:16]
        ],
        "top_stationary_flux_edges": [
            {
                "transfer_edge_id": int(row["transfer_edge_id"]),
                "source_signature_class_id": int(row["source_signature_class_id"]),
                "target_signature_class_id": int(row["target_signature_class_id"]),
                "shared_active_atom_count": int(row["shared_active_atom_count"]),
                "undirected_stationary_flux_x1e12": int(
                    row["undirected_stationary_flux_x1e12"]
                ),
            }
            for row in sorted(
                edge_rows,
                key=lambda item: (
                    -int(item["undirected_stationary_flux_x1e12"]),
                    int(item["transfer_edge_id"]),
                ),
            )[:16]
        ],
    }

    checks = {
        "signature_subboundary_report_certified": subboundary_report.get("status")
        == "C985_D20_RECURRENT_SIGNATURE_SUBBOUNDARY_CERTIFIED",
        "signature_subboundary_certificate_certified": subboundary_certificate.get("status")
        == "C985_D20_RECURRENT_SIGNATURE_SUBBOUNDARY_CERTIFIED",
        "boundary_transfer_report_certified": boundary_transfer_report.get("status")
        == "C985_D20_BOUNDARY_TRANSFER_OPERATOR_CERTIFIED",
        "boundary_transfer_certificate_certified": boundary_transfer_certificate.get("status")
        == "C985_D20_BOUNDARY_TRANSFER_OPERATOR_CERTIFIED",
        "active_signature_count_is_221": int(source_vertex_table.shape[0]) == 221,
        "transfer_edge_count_is_13035": int(source_edge_table.shape[0]) == 13035,
        "support_matches_subboundary_adjacency": np.array_equal(
            (shared > 0).astype(np.int8),
            source_adjacency,
        ),
        "support_is_connected": int(kernel["support_component_count"]) == 1,
        "transition_matrix_shape_is_221_by_221": tuple(transition_matrix_x1e12.shape)
        == (221, 221),
        "transition_rows_sum_to_one_x1e12": bool(
            np.all(transition_matrix_x1e12.sum(axis=1) == PROBABILITY_SCALE)
        ),
        "stationary_distribution_sums_to_one_x1e12": int(stationary_scaled.sum())
        == PROBABILITY_SCALE,
        "stationary_residual_is_zero_at_x1e12": int(
            kernel["stationary_residual_max_x1e12"]
        )
        == 0,
        "row_sum_residual_is_zero_at_x1e12": int(kernel["row_sum_residual_max_x1e12"])
        == 0,
        "spectral_gap_matches_expected": spectral_gap_x1e12 == 412747463786,
        "spectral_second_modulus_matches_expected": int(
            kernel["spectral_second_modulus_x1e12"]
        )
        == 587252536214,
        "spectral_gap_exceeds_core_gap": spectral_gap_x1e12 > core_gap_x1e12,
        "spectral_gap_delta_matches_expected": spectral_gap_x1e12 - core_gap_x1e12
        == 239075938607,
        "spectral_gap_ratio_matches_expected": scaled_float(
            spectral_gap_x1e12 / core_gap_x1e12
        )
        == 2376598370750,
        "top_stationary_signatures_are_106_to_115": top_stationary_ids
        == [106, 107, 108, 109, 110, 111, 112, 113, 114, 115],
        "top_stationary_signature_mass_matches_expected": top_stationary_mass
        == 11783387736,
        "top_mask_class_is_11": top_mask_class_ids == [11],
        "top_mask_stationary_mass_matches_expected": int(top_mask_mass) == 235667754700,
        "top_atom_is_19": top_atom_ids == [19],
        "top_atom_stationary_mass_matches_expected": int(top_atom_mass) == 215486440125,
        "stationary_flow_total_variation_matches_expected": scaled_float(total_variation)
        == 164666435075,
        "stationary_flow_correlation_matches_expected": scaled_float(
            stationary_flow_correlation
        )
        == 869103997875,
        "transition_probability_range_matches_expected": int(positive_probabilities.min())
        == 661404733
        and int(positive_probabilities.max()) == 27508677866,
        "undirected_flux_range_matches_expected": int(undirected_flux_array.min())
        == 2517490
        and int(undirected_flux_array.max()) == 390010460,
        "signature_stationary_table_shape_is_221_by_11": tuple(stationary_table.shape)
        == (221, len(SIGNATURE_STATIONARY_COLUMNS)),
        "signature_transfer_edge_table_shape_is_13035_by_11": tuple(edge_table.shape)
        == (13035, len(SIGNATURE_TRANSFER_EDGE_COLUMNS)),
        "mask_stationary_table_shape_is_14_by_13": tuple(mask_table.shape)
        == (14, len(MASK_STATIONARY_COLUMNS)),
        "atom_stationary_table_shape_is_6_by_7": tuple(atom_table.shape)
        == (6, len(ATOM_STATIONARY_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(SIGNATURE_TRANSFER_OBSERVABLE_COLUMNS)),
        "spectrum_shape_is_221": tuple(
            np.asarray(kernel["symmetric_similarity_spectrum_x1e12"]).shape
        )
        == (221,),
        "subboundary_json_schema_available": subboundary.get("schema")
        == "c985.d20_recurrent_signature_subboundary@1",
        "boundary_transfer_json_schema_available": boundary_transfer.get("schema")
        == "c985.d20_boundary_transfer_operator@1",
        "boundary_transfer_tables_available": "transition_matrix"
        in boundary_transfer_tables.files,
    }

    witness = {
        "active_signature_class_count": int(source_vertex_table.shape[0]),
        "transfer_edge_count": int(source_edge_table.shape[0]),
        "carrier_mask_count": int(source_mask_table.shape[0]),
        "stationary_mass_sum_x1e12": int(stationary_scaled.sum()),
        "top_stationary_signature_class_ids": top_stationary_ids,
        "top_stationary_signature_mass_x1e12": top_stationary_mass,
        "minimum_stationary_mass_x1e12": int(stationary_scaled.min()),
        "minimum_stationary_signature_class_ids": transfer_operator["stationary_summary"][
            "minimum_stationary_signature_class_ids"
        ],
        "top_mask_class_ids": top_mask_class_ids,
        "top_mask_stationary_mass_x1e12": int(top_mask_mass),
        "top_atom_ids": top_atom_ids,
        "top_atom_stationary_mass_x1e12": int(top_atom_mass),
        "stationary_atom_order": transfer_operator["atom_stationary_summary"][
            "stationary_atom_order"
        ],
        "spectral_gap_x1e12": spectral_gap_x1e12,
        "spectral_second_modulus_x1e12": int(kernel["spectral_second_modulus_x1e12"]),
        "core_spectral_gap_x1e12": core_gap_x1e12,
        "spectral_gap_delta_vs_core_x1e12": spectral_gap_x1e12 - core_gap_x1e12,
        "spectral_gap_ratio_to_core_x1e12": scaled_float(
            spectral_gap_x1e12 / core_gap_x1e12
        ),
        "stationary_entropy_x1e12": scaled_float(stationary_entropy),
        "stationary_perplexity_x1e12": scaled_float(stationary_perplexity),
        "stationary_flow_total_variation_x1e12": scaled_float(total_variation),
        "stationary_flow_correlation_x1e12": scaled_float(stationary_flow_correlation),
        "row_entropy_min_x1e12": scaled_float(float(row_entropies.min())),
        "row_entropy_max_x1e12": scaled_float(float(row_entropies.max())),
        "row_entropy_mean_x1e12": scaled_float(float(row_entropies.mean())),
        "row_entropy_stationary_mean_x1e12": scaled_float(
            float(np.dot(stationary, row_entropies))
        ),
        "transition_probability_min_x1e12": int(positive_probabilities.min()),
        "transition_probability_max_x1e12": int(positive_probabilities.max()),
        "undirected_stationary_flux_min_x1e12": int(undirected_flux_array.min()),
        "undirected_stationary_flux_max_x1e12": int(undirected_flux_array.max()),
        "stationary_table_sha256": sha_array(stationary_table),
        "transfer_edge_table_sha256": sha_array(edge_table),
        "mask_stationary_table_sha256": sha_array(mask_table),
        "atom_stationary_table_sha256": sha_array(atom_table),
        "observable_table_sha256": sha_array(observable_table),
        "transition_matrix_x1e12_sha256": sha_array(transition_matrix_x1e12),
        "symmetric_similarity_spectrum_x1e12_sha256": sha_array(
            np.asarray(kernel["symmetric_similarity_spectrum_x1e12"], dtype=np.int64)
        ),
    }

    certificate = {
        "schema": "c985.d20_signature_subboundary_transfer_operator_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_SUBBOUNDARY_TRANSFER_OPERATOR_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "shared-carrier conductance gives a reversible transfer kernel on all 221 recurrent signature classes",
            "the transfer support is exactly the certified recurrent signature subboundary graph",
            "the stationary measure is reproducible from integer signature-flow masses and shared active atom counts",
            "the signature transfer spectral gap is larger than the 12-node core transfer spectral gap",
            "the induced stationary measure shifts the largest carrier block to mask 524434 and atom 19",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_subboundary_transfer_operator@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The recurrent signature subboundary carries a certified reversible "
            "transfer operator whose edge conductance is shared active carrier "
            "count times the two endpoint signature-flow masses. Its stationary "
            "measure is exact at scale 1e12, its support is all 221 recurrent "
            "signature classes, and its spectral gap exceeds the 12-node core "
            "transfer gap."
        ),
        "stage_protocol": {
            "draft": "put a local shared-carrier conductance on the certified recurrent signature graph",
            "witness": "materialize transition edges, row-stochastic matrix, stationary law, mask/atom marginals, and spectral observables",
            "coherence": "check reversibility, support equality, stochasticity, stationarity, spectral gap comparison, and table reproducibility",
            "closure": "certify the signature-subboundary transfer operator without claiming continuum diffusion or new categorical data",
            "emit": "emit transfer JSON/CSV/NPZ, certificate, report, verifier command, and next spectral target",
        },
        "inputs": {
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
            "boundary_transfer_report": input_entry(
                BOUNDARY_TRANSFER_REPORT,
                {
                    "status": boundary_transfer_report.get("status"),
                    "certificate_sha256": boundary_transfer_report.get(
                        "certificate_sha256"
                    ),
                },
            ),
            "boundary_transfer": input_entry(BOUNDARY_TRANSFER_JSON),
            "boundary_transfer_tables": input_entry(BOUNDARY_TRANSFER_TABLES),
            "boundary_transfer_certificate": input_entry(BOUNDARY_TRANSFER_CERTIFICATE),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_transfer_operator": relpath(OUT_DIR / "signature_transfer_operator.json"),
            "signature_transfer_edges_csv": relpath(OUT_DIR / "signature_transfer_edges.csv"),
            "signature_stationary_distribution_csv": relpath(
                OUT_DIR / "signature_stationary_distribution.csv"
            ),
            "signature_mask_stationary_csv": relpath(OUT_DIR / "signature_mask_stationary.csv"),
            "signature_atom_stationary_csv": relpath(OUT_DIR / "signature_atom_stationary.csv"),
            "signature_transfer_observables_csv": relpath(
                OUT_DIR / "signature_transfer_observables.csv"
            ),
            "signature_transfer_tables": relpath(OUT_DIR / "signature_transfer_tables.npz"),
            "signature_transfer_certificate": relpath(OUT_DIR / "signature_transfer_certificate.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "a reversible Markov transfer operator on the recurrent signature subboundary",
                "row-stochastic transition probabilities at exact scale 1e12",
                "stationary distribution, mask marginal, atom marginal, and flux tables",
                "spectral gap, second modulus, and comparison to the 12-node core transfer gap",
                "the shift from top atom-flow signature carriers to top transfer-stationary carriers",
            ],
            "does_not_certify_because_not_required": [
                "a unique physically canonical signature transition law beyond the declared conductance rule",
                "mixing-time bounds beyond the certified spectral gap comparison",
                "continuum diffusion, heat kernel limits, or asymptotic boundary measures",
                "new associator, pentagon, pivotal, spherical, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Read the transfer operator spectrally: certify the second eigenmode "
            "and its nodal cut on the 221-node signature subboundary, then compare "
            "that metastable split with the carrier-mask quotient and the original "
            "core source lobes."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_subboundary_transfer_operator_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load the certified recurrent signature subboundary and boundary transfer operator",
            "build shared-carrier conductances from signature-flow masses",
            "materialize row-stochastic transition probabilities and stationary distribution",
            "verify reversibility support, exact row sums, stationarity residual, and spectral gap",
            "compare the signature transfer spectral gap against the 12-node core transfer gap",
            "check mask/atom marginals, source hashes, artifact reproducibility, and registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_transfer_operator": transfer_operator,
        "signature_transfer_edges_csv": csv_text(
            SIGNATURE_TRANSFER_EDGE_COLUMNS,
            edge_rows,
        ),
        "signature_stationary_distribution_csv": csv_text(
            SIGNATURE_STATIONARY_COLUMNS,
            stationary_rows,
        ),
        "signature_mask_stationary_csv": csv_text(MASK_STATIONARY_COLUMNS, mask_rows),
        "signature_atom_stationary_csv": csv_text(ATOM_STATIONARY_COLUMNS, atom_rows),
        "signature_transfer_observables_csv": csv_text(
            SIGNATURE_TRANSFER_OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "signature_transfer_edge_table": edge_table,
        "signature_stationary_table": stationary_table,
        "signature_mask_stationary_table": mask_table,
        "signature_atom_stationary_table": atom_table,
        "signature_transfer_observable_table": observable_table,
        "signature_transfer_matrix_x1e12": transition_matrix_x1e12,
        "symmetric_similarity_spectrum_x1e12": np.asarray(
            kernel["symmetric_similarity_spectrum_x1e12"],
            dtype=np.int64,
        ),
        "signature_stationary_distribution_x1e12": stationary_scaled,
        "signature_shared_active_atom_matrix": shared,
        "signature_transfer_certificate": certificate,
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
    write_json(OUT_DIR / "signature_transfer_operator.json", payloads["signature_transfer_operator"])
    (OUT_DIR / "signature_transfer_edges.csv").write_text(
        payloads["signature_transfer_edges_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "signature_stationary_distribution.csv").write_text(
        payloads["signature_stationary_distribution_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "signature_mask_stationary.csv").write_text(
        payloads["signature_mask_stationary_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "signature_atom_stationary.csv").write_text(
        payloads["signature_atom_stationary_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "signature_transfer_observables.csv").write_text(
        payloads["signature_transfer_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_transfer_tables.npz",
        signature_transfer_edge_table=payloads["signature_transfer_edge_table"],
        signature_stationary_table=payloads["signature_stationary_table"],
        signature_mask_stationary_table=payloads["signature_mask_stationary_table"],
        signature_atom_stationary_table=payloads["signature_atom_stationary_table"],
        signature_transfer_observable_table=payloads[
            "signature_transfer_observable_table"
        ],
        signature_transfer_matrix_x1e12=payloads["signature_transfer_matrix_x1e12"],
        symmetric_similarity_spectrum_x1e12=payloads[
            "symmetric_similarity_spectrum_x1e12"
        ],
        signature_stationary_distribution_x1e12=payloads[
            "signature_stationary_distribution_x1e12"
        ],
        signature_shared_active_atom_matrix=payloads[
            "signature_shared_active_atom_matrix"
        ],
    )
    write_json(OUT_DIR / "signature_transfer_certificate.json", payloads["signature_transfer_certificate"])
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
                "active_signature_class_count": witness[
                    "active_signature_class_count"
                ],
                "transfer_edge_count": witness["transfer_edge_count"],
                "spectral_gap_x1e12": witness["spectral_gap_x1e12"],
                "core_spectral_gap_x1e12": witness["core_spectral_gap_x1e12"],
                "top_stationary_signature_class_ids": witness[
                    "top_stationary_signature_class_ids"
                ],
                "top_atom_ids": witness["top_atom_ids"],
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
