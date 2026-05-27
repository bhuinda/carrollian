from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_morse_reeb_quotient import (
        OUT_DIR as MORSE_REEB_DIR,
    )
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
    from derive_c985_d20_morse_reeb_quotient import (
        OUT_DIR as MORSE_REEB_DIR,
    )
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


THEOREM_ID = "c985_d20_boundary_transfer_operator"
STATUS = "C985_D20_BOUNDARY_TRANSFER_OPERATOR_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

REWRITE_COMPLEX_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_rewrite_complex_hyperbolicity"
POINCARE_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_poincare_embedding"

REWRITE_COMPLEX_REPORT = REWRITE_COMPLEX_DIR / "report.json"
REWRITE_COMPLEX_JSON = REWRITE_COMPLEX_DIR / "rewrite_complex.json"
REWRITE_COMPLEX_CERTIFICATE = REWRITE_COMPLEX_DIR / "rewrite_complex_certificate.json"
POINCARE_REPORT = POINCARE_DIR / "report.json"
POINCARE_JSON = POINCARE_DIR / "poincare_embedding.json"
POINCARE_TABLES = POINCARE_DIR / "poincare_embedding.npz"
POINCARE_CERTIFICATE = POINCARE_DIR / "embedding_certificate.json"
MORSE_REEB_REPORT = MORSE_REEB_DIR / "report.json"
MORSE_REEB_JSON = MORSE_REEB_DIR / "morse_reeb_quotient.json"
MORSE_REEB_TABLES = MORSE_REEB_DIR / "morse_reeb_tables.npz"
MORSE_REEB_CERTIFICATE = MORSE_REEB_DIR / "morse_reeb_certificate.json"
MORSE_REEB_PATHS_CSV = MORSE_REEB_DIR / "directed_interval_paths.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_c985_d20_boundary_transfer_operator.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_d20_boundary_transfer_operator.py"

CORE_NODE_IDS = [10, 13, 17, 19, 28, 32, 34, 38, 41, 42, 43, 44]
MORSE_SOURCES = [10, 43]
MORSE_SINK = 44
MAX_PATH_NODE_COUNT = 7
DISTANCE_SCALE = 1_000_000_000_000
WEIGHT_SCALE = 1_000_000_000
PROBABILITY_SCALE = 1_000_000_000_000

EDGE_KIND_CODES = {
    "flow": 0,
    "return": 1,
}

OBSERVABLE_CODES = {
    "raw_weight_total_x1e9": 0,
    "return_10_probability": 1,
    "return_43_probability": 2,
    "stationary_basin_10_mass": 3,
    "stationary_basin_43_mass": 4,
    "stationary_boundary_mass": 5,
    "stationary_entropy": 6,
    "path_entropy": 7,
    "path_perplexity": 8,
    "spectral_second_modulus": 9,
    "spectral_gap": 10,
    "weighted_poincare_center_x": 11,
    "weighted_poincare_center_y": 12,
    "weighted_poincare_center_radius": 13,
    "stationary_mean_poincare_radius": 14,
    "uniform_mean_poincare_radius": 15,
    "stationary_negative_radius_correlation": 16,
    "stationary_tensor_mass_correlation": 17,
    "stationary_signature_correlation": 18,
}

SOURCE_SINK_PATH_WEIGHT_COLUMNS = [
    "path_weight_id",
    "morphism_id",
    "source_node_id",
    "path_length",
    "node_id_0",
    "node_id_1",
    "node_id_2",
    "node_id_3",
    "node_id_4",
    "node_id_5",
    "node_id_6",
    "path_tensor_mass_sum",
    "path_signature_sum",
    "path_hyperbolic_length_x1e12",
    "raw_weight_x1e9",
    "global_probability_x1e12",
    "source_probability_x1e12",
]

TRANSFER_EDGE_COLUMNS = [
    "transfer_edge_id",
    "source_node_id",
    "target_node_id",
    "edge_kind_code",
    "edge_flux_x1e9",
    "transition_probability_x1e12",
    "source_stationary_mass_x1e12",
    "target_stationary_mass_x1e12",
    "stationary_edge_flow_x1e12",
]

STATIONARY_DISTRIBUTION_COLUMNS = [
    "node_id",
    "stationary_mass_x1e12",
    "basin_code",
    "poincare_x_x1e12",
    "poincare_y_x1e12",
    "poincare_radius_x1e12",
    "tensor_path_coefficient_mass_sum",
    "signature_union_count",
    "stationary_rank",
]

FLOW_OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_node_id",
]


def scaled(value: float, scale: int = PROBABILITY_SCALE) -> int:
    return int(round(float(value) * scale))


def round12(value: float) -> float:
    return float(round(float(value), 12))


def parse_source_sink_paths(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if int(row["source_sink_path"]) != 1:
                continue
            node_ids = [
                int(row[f"node_id_{index}"])
                for index in range(MAX_PATH_NODE_COUNT)
                if int(row[f"node_id_{index}"]) >= 0
            ]
            rows.append(
                {
                    "morphism_id": int(row["morphism_id"]),
                    "source_node_id": int(row["source_node_id"]),
                    "target_node_id": int(row["target_node_id"]),
                    "path_length": int(row["path_length"]),
                    "node_ids": node_ids,
                }
            )
    return rows


def poincare_hyperbolic_distance(
    source_node_id: int,
    target_node_id: int,
    node_by_id: dict[int, dict[str, Any]],
) -> float:
    source = node_by_id[source_node_id]["poincare_barycenter"]
    target = node_by_id[target_node_id]["poincare_barycenter"]
    dx = float(source["x"]) - float(target["x"])
    dy = float(source["y"]) - float(target["y"])
    source_radius_sq = float(source["x"]) ** 2 + float(source["y"]) ** 2
    target_radius_sq = float(target["x"]) ** 2 + float(target["y"]) ** 2
    numerator = 2.0 * (dx * dx + dy * dy)
    denominator = (1.0 - source_radius_sq) * (1.0 - target_radius_sq)
    return float(math.acosh(max(1.0, 1.0 + numerator / denominator)))


def build_path_weight_rows(
    path_rows: list[dict[str, Any]],
    node_by_id: dict[int, dict[str, Any]],
) -> tuple[list[dict[str, Any]], np.ndarray, dict[str, Any]]:
    raw_records: list[dict[str, Any]] = []
    for path_weight_id, source in enumerate(path_rows):
        node_ids = [int(node_id) for node_id in source["node_ids"]]
        path_hyperbolic_length = sum(
            poincare_hyperbolic_distance(left, right, node_by_id)
            for left, right in zip(node_ids, node_ids[1:])
        )
        tensor_mass_sum = sum(
            int(node_by_id[node_id]["tensor_path_coefficient_mass_sum"])
            for node_id in node_ids
        )
        signature_sum = sum(
            int(node_by_id[node_id]["signature_union_count"]) for node_id in node_ids
        )
        raw_weight = int(round(tensor_mass_sum * WEIGHT_SCALE / (1.0 + path_hyperbolic_length)))
        raw_records.append(
            {
                "path_weight_id": path_weight_id,
                "morphism_id": int(source["morphism_id"]),
                "source_node_id": int(source["source_node_id"]),
                "target_node_id": int(source["target_node_id"]),
                "path_length": int(source["path_length"]),
                "node_ids": node_ids,
                "path_tensor_mass_sum": tensor_mass_sum,
                "path_signature_sum": signature_sum,
                "path_hyperbolic_length_x1e12": scaled(
                    path_hyperbolic_length,
                    DISTANCE_SCALE,
                ),
                "raw_weight_x1e9": raw_weight,
            }
        )

    raw_total = sum(int(row["raw_weight_x1e9"]) for row in raw_records)
    source_raw = {
        source: sum(
            int(row["raw_weight_x1e9"])
            for row in raw_records
            if int(row["source_node_id"]) == source
        )
        for source in MORSE_SOURCES
    }
    rows: list[dict[str, Any]] = []
    table_rows: list[list[int]] = []
    for row in raw_records:
        source = int(row["source_node_id"])
        padded = [*row["node_ids"], *([-1] * (MAX_PATH_NODE_COUNT - len(row["node_ids"])))]
        enriched = {
            **row,
            "node_id_0": int(padded[0]),
            "node_id_1": int(padded[1]),
            "node_id_2": int(padded[2]),
            "node_id_3": int(padded[3]),
            "node_id_4": int(padded[4]),
            "node_id_5": int(padded[5]),
            "node_id_6": int(padded[6]),
            "global_probability_x1e12": int(
                round(int(row["raw_weight_x1e9"]) * PROBABILITY_SCALE / raw_total)
            ),
            "source_probability_x1e12": int(
                round(
                    int(row["raw_weight_x1e9"])
                    * PROBABILITY_SCALE
                    / source_raw[source]
                )
            ),
        }
        rows.append(enriched)
        table_rows.append([int(enriched[column]) for column in SOURCE_SINK_PATH_WEIGHT_COLUMNS])
    summary = {
        "raw_weight_total_x1e9": raw_total,
        "source_raw_weight_x1e9": {str(source): int(source_raw[source]) for source in MORSE_SOURCES},
        "source_path_count": {
            str(source): sum(1 for row in rows if int(row["source_node_id"]) == source)
            for source in MORSE_SOURCES
        },
        "source_probability_rounding_error_x1e12": {
            str(source): int(
                sum(
                    int(row["source_probability_x1e12"])
                    for row in rows
                    if int(row["source_node_id"]) == source
                )
                - PROBABILITY_SCALE
            )
            for source in MORSE_SOURCES
        },
        "global_probability_rounding_error_x1e12": int(
            sum(int(row["global_probability_x1e12"]) for row in rows)
            - PROBABILITY_SCALE
        ),
    }
    return rows, np.asarray(table_rows, dtype=np.int64), summary


def transition_support_is_strongly_connected(support: np.ndarray) -> bool:
    node_count = int(support.shape[0])

    def reach(start: int) -> set[int]:
        seen = {start}
        queue: deque[int] = deque([start])
        while queue:
            node = queue.popleft()
            for neighbor in np.flatnonzero(support[node]):
                neighbor = int(neighbor)
                if neighbor in seen:
                    continue
                seen.add(neighbor)
                queue.append(neighbor)
        return seen

    return all(len(reach(node)) == node_count for node in range(node_count))


def stationary_distribution(transition_matrix: np.ndarray) -> np.ndarray:
    node_count = int(transition_matrix.shape[0])
    system = transition_matrix.T - np.eye(node_count)
    rhs = np.zeros(node_count, dtype=np.float64)
    system[-1, :] = 1.0
    rhs[-1] = 1.0
    return np.linalg.solve(system, rhs)


def build_transfer_matrix(
    path_weight_rows: list[dict[str, Any]],
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    node_index = {node_id: index for index, node_id in enumerate(CORE_NODE_IDS)}
    edge_flux = defaultdict(int)
    source_raw = defaultdict(int)
    for row in path_weight_rows:
        source_raw[int(row["source_node_id"])] += int(row["raw_weight_x1e9"])
        for left, right in zip(row["node_ids"], row["node_ids"][1:]):
            edge_flux[(int(left), int(right))] += int(row["raw_weight_x1e9"])

    edge_flux_matrix = np.zeros((len(CORE_NODE_IDS), len(CORE_NODE_IDS)), dtype=np.int64)
    transfer_matrix = np.zeros((len(CORE_NODE_IDS), len(CORE_NODE_IDS)), dtype=np.float64)
    for (source, target), flux in edge_flux.items():
        edge_flux_matrix[node_index[source], node_index[target]] = int(flux)
        transfer_matrix[node_index[source], node_index[target]] = float(flux)

    for source_index in range(len(CORE_NODE_IDS)):
        row_sum = float(np.sum(transfer_matrix[source_index]))
        if row_sum > 0.0:
            transfer_matrix[source_index] /= row_sum

    raw_total = sum(source_raw.values())
    sink_index = node_index[MORSE_SINK]
    for source in MORSE_SOURCES:
        transfer_matrix[sink_index, node_index[source]] = float(source_raw[source]) / raw_total
        edge_flux_matrix[sink_index, node_index[source]] = int(source_raw[source])

    support = (transfer_matrix > 0.0).astype(np.int8)
    return transfer_matrix, edge_flux_matrix, {
        "edge_flux_by_pair": dict(edge_flux),
        "source_raw_weight_x1e9": dict(source_raw),
        "support": support,
    }


def build_transfer_edge_rows(
    transition_matrix: np.ndarray,
    edge_flux_matrix: np.ndarray,
    stationary: np.ndarray,
) -> tuple[list[dict[str, Any]], np.ndarray]:
    rows: list[dict[str, Any]] = []
    table_rows: list[list[int]] = []
    for source_index, source in enumerate(CORE_NODE_IDS):
        for target_index, target in enumerate(CORE_NODE_IDS):
            if transition_matrix[source_index, target_index] <= 0.0:
                continue
            kind = "return" if source == MORSE_SINK and target in MORSE_SOURCES else "flow"
            stationary_edge_flow = float(stationary[source_index] * transition_matrix[source_index, target_index])
            row = {
                "transfer_edge_id": len(rows),
                "source_node_id": source,
                "target_node_id": target,
                "edge_kind": kind,
                "edge_kind_code": EDGE_KIND_CODES[kind],
                "edge_flux_x1e9": int(edge_flux_matrix[source_index, target_index]),
                "transition_probability_x1e12": scaled(
                    transition_matrix[source_index, target_index],
                    PROBABILITY_SCALE,
                ),
                "source_stationary_mass_x1e12": scaled(
                    stationary[source_index],
                    PROBABILITY_SCALE,
                ),
                "target_stationary_mass_x1e12": scaled(
                    stationary[target_index],
                    PROBABILITY_SCALE,
                ),
                "stationary_edge_flow_x1e12": scaled(stationary_edge_flow, PROBABILITY_SCALE),
            }
            rows.append(row)
            table_rows.append([int(row[column]) for column in TRANSFER_EDGE_COLUMNS])
    return rows, np.asarray(table_rows, dtype=np.int64)


def basin_code_by_node(morse_reeb: dict[str, Any]) -> dict[int, int]:
    return {
        int(row["node_id"]): int(row["basin_code"])
        for row in morse_reeb["core_basin_nodes"]
    }


def build_stationary_rows(
    stationary: np.ndarray,
    node_by_id: dict[int, dict[str, Any]],
    basin_codes: dict[int, int],
) -> tuple[list[dict[str, Any]], np.ndarray]:
    ranks = {
        CORE_NODE_IDS[index]: rank
        for rank, index in enumerate(
            sorted(range(len(CORE_NODE_IDS)), key=lambda item: (-float(stationary[item]), CORE_NODE_IDS[item])),
            start=1,
        )
    }
    rows: list[dict[str, Any]] = []
    table_rows: list[list[int]] = []
    for index, node_id in enumerate(CORE_NODE_IDS):
        barycenter = node_by_id[node_id]["poincare_barycenter"]
        row = {
            "node_id": node_id,
            "stationary_mass_x1e12": scaled(stationary[index], PROBABILITY_SCALE),
            "basin_code": int(basin_codes[node_id]),
            "poincare_x_x1e12": scaled(float(barycenter["x"]), PROBABILITY_SCALE),
            "poincare_y_x1e12": scaled(float(barycenter["y"]), PROBABILITY_SCALE),
            "poincare_radius_x1e12": scaled(float(barycenter["radius"]), PROBABILITY_SCALE),
            "tensor_path_coefficient_mass_sum": int(
                node_by_id[node_id]["tensor_path_coefficient_mass_sum"]
            ),
            "signature_union_count": int(node_by_id[node_id]["signature_union_count"]),
            "stationary_rank": ranks[node_id],
        }
        rows.append(row)
        table_rows.append([int(row[column]) for column in STATIONARY_DISTRIBUTION_COLUMNS])
    return rows, np.asarray(table_rows, dtype=np.int64)


def entropy(probabilities: np.ndarray) -> float:
    return float(-sum(float(value) * math.log(float(value)) for value in probabilities if value > 0.0))


def observable_rows(observables: dict[str, float | int]) -> tuple[list[dict[str, Any]], np.ndarray]:
    rows: list[dict[str, Any]] = []
    table_rows: list[list[int]] = []
    for name, code in sorted(OBSERVABLE_CODES.items(), key=lambda row: row[1]):
        value = observables[name]
        row = {
            "observable_id": len(rows),
            "observable_name": name,
            "observable_code": int(code),
            "value_x1e12": int(value)
            if name == "raw_weight_total_x1e9"
            else scaled(float(value), PROBABILITY_SCALE),
            "aux_node_id": -1,
        }
        rows.append(row)
        table_rows.append([int(row[column]) for column in FLOW_OBSERVABLE_COLUMNS])
    return rows, np.asarray(table_rows, dtype=np.int64)


def path_entropy_summary(path_weight_rows: list[dict[str, Any]]) -> dict[str, Any]:
    raw_weights = np.asarray(
        [int(row["raw_weight_x1e9"]) for row in path_weight_rows],
        dtype=np.float64,
    )
    global_probabilities = raw_weights / float(np.sum(raw_weights))
    source_summaries = []
    for source in MORSE_SOURCES:
        source_raw = np.asarray(
            [
                int(row["raw_weight_x1e9"])
                for row in path_weight_rows
                if int(row["source_node_id"]) == source
            ],
            dtype=np.float64,
        )
        source_probabilities = source_raw / float(np.sum(source_raw))
        source_entropy = entropy(source_probabilities)
        source_summaries.append(
            {
                "source_node_id": source,
                "entropy": round12(source_entropy),
                "entropy_x1e12": scaled(source_entropy, PROBABILITY_SCALE),
                "perplexity": round12(math.exp(source_entropy)),
                "perplexity_x1e12": scaled(math.exp(source_entropy), PROBABILITY_SCALE),
            }
        )
    global_entropy = entropy(global_probabilities)
    return {
        "global_entropy": round12(global_entropy),
        "global_entropy_x1e12": scaled(global_entropy, PROBABILITY_SCALE),
        "global_perplexity": round12(math.exp(global_entropy)),
        "global_perplexity_x1e12": scaled(math.exp(global_entropy), PROBABILITY_SCALE),
        "source_summaries": source_summaries,
    }


def geometric_observables(
    stationary: np.ndarray,
    node_by_id: dict[int, dict[str, Any]],
) -> dict[str, Any]:
    xs = np.asarray(
        [float(node_by_id[node_id]["poincare_barycenter"]["x"]) for node_id in CORE_NODE_IDS],
        dtype=np.float64,
    )
    ys = np.asarray(
        [float(node_by_id[node_id]["poincare_barycenter"]["y"]) for node_id in CORE_NODE_IDS],
        dtype=np.float64,
    )
    radii = np.asarray(
        [float(node_by_id[node_id]["poincare_barycenter"]["radius"]) for node_id in CORE_NODE_IDS],
        dtype=np.float64,
    )
    tensor_masses = np.asarray(
        [int(node_by_id[node_id]["tensor_path_coefficient_mass_sum"]) for node_id in CORE_NODE_IDS],
        dtype=np.float64,
    )
    signature_counts = np.asarray(
        [int(node_by_id[node_id]["signature_union_count"]) for node_id in CORE_NODE_IDS],
        dtype=np.float64,
    )
    center_x = float(stationary @ xs)
    center_y = float(stationary @ ys)
    center_radius = float(math.sqrt(center_x * center_x + center_y * center_y))
    return {
        "weighted_poincare_center": {
            "x": round12(center_x),
            "y": round12(center_y),
            "radius": round12(center_radius),
            "x_x1e12": scaled(center_x, PROBABILITY_SCALE),
            "y_x1e12": scaled(center_y, PROBABILITY_SCALE),
            "radius_x1e12": scaled(center_radius, PROBABILITY_SCALE),
        },
        "stationary_mean_poincare_radius": round12(float(stationary @ radii)),
        "stationary_mean_poincare_radius_x1e12": scaled(
            float(stationary @ radii),
            PROBABILITY_SCALE,
        ),
        "uniform_mean_poincare_radius": round12(float(np.mean(radii))),
        "uniform_mean_poincare_radius_x1e12": scaled(
            float(np.mean(radii)),
            PROBABILITY_SCALE,
        ),
        "stationary_negative_radius_correlation": round12(
            float(np.corrcoef(stationary, -radii)[0, 1])
        ),
        "stationary_negative_radius_correlation_x1e12": scaled(
            float(np.corrcoef(stationary, -radii)[0, 1]),
            PROBABILITY_SCALE,
        ),
        "stationary_tensor_mass_correlation": round12(
            float(np.corrcoef(stationary, tensor_masses)[0, 1])
        ),
        "stationary_tensor_mass_correlation_x1e12": scaled(
            float(np.corrcoef(stationary, tensor_masses)[0, 1]),
            PROBABILITY_SCALE,
        ),
        "stationary_signature_correlation": round12(
            float(np.corrcoef(stationary, signature_counts)[0, 1])
        ),
        "stationary_signature_correlation_x1e12": scaled(
            float(np.corrcoef(stationary, signature_counts)[0, 1]),
            PROBABILITY_SCALE,
        ),
    }


def build_payloads() -> dict[str, Any]:
    rewrite_report = load_json(REWRITE_COMPLEX_REPORT)
    rewrite_complex = load_json(REWRITE_COMPLEX_JSON)
    rewrite_certificate = load_json(REWRITE_COMPLEX_CERTIFICATE)
    poincare_report = load_json(POINCARE_REPORT)
    poincare_certificate = load_json(POINCARE_CERTIFICATE)
    morse_report = load_json(MORSE_REEB_REPORT)
    morse_reeb = load_json(MORSE_REEB_JSON)
    morse_certificate = load_json(MORSE_REEB_CERTIFICATE)
    morse_tables = np.load(MORSE_REEB_TABLES, allow_pickle=False)
    poincare_tables = np.load(POINCARE_TABLES, allow_pickle=False)

    node_by_id = {int(node["node_id"]): node for node in rewrite_complex["nodes"]}
    path_rows = parse_source_sink_paths(MORSE_REEB_PATHS_CSV)
    path_weight_rows, path_weight_table, path_weight_summary = build_path_weight_rows(
        path_rows,
        node_by_id,
    )
    transition_matrix, edge_flux_matrix, transfer_support = build_transfer_matrix(
        path_weight_rows
    )
    support = np.asarray(transfer_support["support"], dtype=np.int8)
    stationary = stationary_distribution(transition_matrix)
    stationary_x1e12 = np.asarray(
        [scaled(value, PROBABILITY_SCALE) for value in stationary],
        dtype=np.int64,
    )
    edge_rows, transfer_edge_table = build_transfer_edge_rows(
        transition_matrix,
        edge_flux_matrix,
        stationary,
    )
    basin_codes = basin_code_by_node(morse_reeb)
    stationary_rows, stationary_table = build_stationary_rows(
        stationary,
        node_by_id,
        basin_codes,
    )

    eigenvalues = np.linalg.eigvals(transition_matrix.T)
    eigenvalues_sorted = sorted(eigenvalues, key=lambda value: abs(value), reverse=True)
    spectral_second_modulus = float(abs(eigenvalues_sorted[1]))
    spectral_gap = float(1.0 - spectral_second_modulus)
    path_entropy = path_entropy_summary(path_weight_rows)
    geometry = geometric_observables(stationary, node_by_id)
    basin_masses = {
        "10": float(sum(stationary[index] for index, node_id in enumerate(CORE_NODE_IDS) if basin_codes[node_id] == 10)),
        "43": float(sum(stationary[index] for index, node_id in enumerate(CORE_NODE_IDS) if basin_codes[node_id] == 43)),
        "boundary": float(
            sum(stationary[index] for index, node_id in enumerate(CORE_NODE_IDS) if basin_codes[node_id] == 0)
        ),
    }
    top_paths = sorted(
        path_weight_rows,
        key=lambda row: (int(row["raw_weight_x1e9"]), -int(row["morphism_id"])),
        reverse=True,
    )[:5]
    top_edges = sorted(
        edge_rows,
        key=lambda row: (int(row["stationary_edge_flow_x1e12"]), int(row["source_node_id"]), int(row["target_node_id"])),
        reverse=True,
    )[:5]

    observables = {
        "raw_weight_total_x1e9": path_weight_summary["raw_weight_total_x1e9"],
        "return_10_probability": transition_matrix[CORE_NODE_IDS.index(44), CORE_NODE_IDS.index(10)],
        "return_43_probability": transition_matrix[CORE_NODE_IDS.index(44), CORE_NODE_IDS.index(43)],
        "stationary_basin_10_mass": basin_masses["10"],
        "stationary_basin_43_mass": basin_masses["43"],
        "stationary_boundary_mass": basin_masses["boundary"],
        "stationary_entropy": entropy(stationary),
        "path_entropy": path_entropy["global_entropy"],
        "path_perplexity": path_entropy["global_perplexity"],
        "spectral_second_modulus": spectral_second_modulus,
        "spectral_gap": spectral_gap,
        "weighted_poincare_center_x": geometry["weighted_poincare_center"]["x"],
        "weighted_poincare_center_y": geometry["weighted_poincare_center"]["y"],
        "weighted_poincare_center_radius": geometry["weighted_poincare_center"]["radius"],
        "stationary_mean_poincare_radius": geometry["stationary_mean_poincare_radius"],
        "uniform_mean_poincare_radius": geometry["uniform_mean_poincare_radius"],
        "stationary_negative_radius_correlation": geometry[
            "stationary_negative_radius_correlation"
        ],
        "stationary_tensor_mass_correlation": geometry["stationary_tensor_mass_correlation"],
        "stationary_signature_correlation": geometry["stationary_signature_correlation"],
    }
    observable_row_list, observable_table = observable_rows(observables)

    boundary_transfer = {
        "schema": "c985.d20_boundary_transfer_operator@1",
        "object": "d20",
        "source_morse_reeb_certificate": morse_report.get("certificate_sha256"),
        "transfer_rule": {
            "path_weight": "tensor_path_coefficient_mass_sum divided by one plus Poincare hyperbolic path length",
            "flow_edges": "sum source-sink path weights over each chamber-orientation edge",
            "return_kernel": "close the acyclic flow by returning from sink 44 to sources 10 and 43 in proportion to total source path weight",
            "stationary_measure": "unique stationary distribution of the closed row-stochastic transfer matrix",
            "scales": {
                "distance_scale": DISTANCE_SCALE,
                "weight_scale": WEIGHT_SCALE,
                "probability_scale": PROBABILITY_SCALE,
            },
        },
        "edge_kind_codebook": EDGE_KIND_CODES,
        "observable_codebook": OBSERVABLE_CODES,
        "source_sink_path_weights": path_weight_rows,
        "transfer_edges": edge_rows,
        "stationary_distribution": stationary_rows,
        "flow_observables": observable_row_list,
        "summary": {
            "core_node_ids": CORE_NODE_IDS,
            "source_node_ids": MORSE_SOURCES,
            "sink_node_id": MORSE_SINK,
            "source_sink_path_count": len(path_weight_rows),
            "source_path_count": path_weight_summary["source_path_count"],
            "raw_weight_total_x1e9": path_weight_summary["raw_weight_total_x1e9"],
            "source_raw_weight_x1e9": path_weight_summary["source_raw_weight_x1e9"],
            "return_probabilities_x1e12": {
                "10": scaled(transition_matrix[CORE_NODE_IDS.index(44), CORE_NODE_IDS.index(10)]),
                "43": scaled(transition_matrix[CORE_NODE_IDS.index(44), CORE_NODE_IDS.index(43)]),
            },
            "transfer_edge_count": len(edge_rows),
            "flow_edge_count": sum(1 for row in edge_rows if row["edge_kind"] == "flow"),
            "return_edge_count": sum(1 for row in edge_rows if row["edge_kind"] == "return"),
            "transition_row_sum_max_error": round12(
                float(np.max(np.abs(np.sum(transition_matrix, axis=1) - 1.0)))
            ),
            "support_strongly_connected": transition_support_is_strongly_connected(support),
            "recurrent_support_node_count": len(CORE_NODE_IDS)
            if transition_support_is_strongly_connected(support)
            else 0,
            "stationary_distribution_x1e12": {
                str(node_id): int(stationary_x1e12[index])
                for index, node_id in enumerate(CORE_NODE_IDS)
            },
            "stationary_mass_sum_x1e12": int(np.sum(stationary_x1e12)),
            "stationary_max_node_id": CORE_NODE_IDS[int(np.argmax(stationary))],
            "stationary_min_node_id": CORE_NODE_IDS[int(np.argmin(stationary))],
            "stationary_basin_masses_x1e12": {
                name: scaled(value, PROBABILITY_SCALE) for name, value in basin_masses.items()
            },
            "path_entropy": path_entropy,
            "spectral_second_modulus": round12(spectral_second_modulus),
            "spectral_second_modulus_x1e12": scaled(spectral_second_modulus),
            "spectral_gap": round12(spectral_gap),
            "spectral_gap_x1e12": scaled(spectral_gap),
            "geometric_observables": geometry,
            "top_path_weights": [
                {
                    "morphism_id": int(row["morphism_id"]),
                    "source_node_id": int(row["source_node_id"]),
                    "path_length": int(row["path_length"]),
                    "node_ids": row["node_ids"],
                    "path_hyperbolic_length_x1e12": int(row["path_hyperbolic_length_x1e12"]),
                    "path_tensor_mass_sum": int(row["path_tensor_mass_sum"]),
                    "raw_weight_x1e9": int(row["raw_weight_x1e9"]),
                }
                for row in top_paths
            ],
            "top_stationary_edge_flows": [
                {
                    "source_node_id": int(row["source_node_id"]),
                    "target_node_id": int(row["target_node_id"]),
                    "edge_kind": row["edge_kind"],
                    "stationary_edge_flow_x1e12": int(row["stationary_edge_flow_x1e12"]),
                }
                for row in top_edges
            ],
            "path_length_histogram": histogram(
                [int(row["path_length"]) for row in path_weight_rows]
            ),
        },
    }

    checks = {
        "rewrite_complex_report_certified": rewrite_report.get("status")
        == "C985_D20_REWRITE_COMPLEX_HYPERBOLICITY_CERTIFIED",
        "rewrite_complex_certificate_certified": rewrite_certificate.get("status")
        == "C985_D20_REWRITE_COMPLEX_HYPERBOLICITY_CERTIFIED",
        "poincare_report_certified": poincare_report.get("status")
        == "C985_D20_POINCARE_EMBEDDING_CERTIFIED",
        "poincare_certificate_certified": poincare_certificate.get("status")
        == "C985_D20_POINCARE_EMBEDDING_CERTIFIED",
        "morse_reeb_report_certified": morse_report.get("status")
        == "C985_D20_MORSE_REEB_QUOTIENT_CERTIFIED",
        "morse_reeb_certificate_certified": morse_certificate.get("status")
        == "C985_D20_MORSE_REEB_QUOTIENT_CERTIFIED",
        "source_sink_path_count_is_42": len(path_weight_rows) == 42,
        "source_path_counts_are_10_and_32": path_weight_summary["source_path_count"]
        == {"10": 10, "43": 32},
        "path_weight_table_shape_is_42_by_17": tuple(path_weight_table.shape)
        == (42, len(SOURCE_SINK_PATH_WEIGHT_COLUMNS)),
        "transfer_matrix_shape_is_12_by_12": tuple(transition_matrix.shape) == (12, 12),
        "transfer_row_sums_are_stochastic": boundary_transfer["summary"][
            "transition_row_sum_max_error"
        ]
        <= 1e-12,
        "transfer_edge_count_is_33": len(edge_rows) == 33,
        "flow_edge_count_is_31": boundary_transfer["summary"]["flow_edge_count"] == 31,
        "return_edge_count_is_2": boundary_transfer["summary"]["return_edge_count"] == 2,
        "return_probabilities_match": boundary_transfer["summary"][
            "return_probabilities_x1e12"
        ]
        == {"10": 283062070620, "43": 716937929380},
        "support_is_strongly_connected": boundary_transfer["summary"][
            "support_strongly_connected"
        ]
        is True,
        "recurrent_support_is_all_12_core_nodes": boundary_transfer["summary"][
            "recurrent_support_node_count"
        ]
        == 12,
        "stationary_distribution_sums_to_one": boundary_transfer["summary"][
            "stationary_mass_sum_x1e12"
        ]
        == PROBABILITY_SCALE,
        "stationary_max_node_is_44": boundary_transfer["summary"]["stationary_max_node_id"]
        == 44,
        "stationary_min_node_is_32": boundary_transfer["summary"]["stationary_min_node_id"]
        == 32,
        "stationary_vector_matches_expected": boundary_transfer["summary"][
            "stationary_distribution_x1e12"
        ]
        == {
            "10": 60964383817,
            "13": 91448650143,
            "17": 33776644764,
            "19": 45863301091,
            "28": 79786909943,
            "32": 26617242245,
            "34": 88173593812,
            "38": 83222089120,
            "41": 79481608761,
            "42": 40880734813,
            "43": 154410228837,
            "44": 215374612654,
        },
        "stationary_basin_masses_match_expected": boundary_transfer["summary"][
            "stationary_basin_masses_x1e12"
        ]
        == {"10": 121358270826, "43": 488349486805, "boundary": 390292242370},
        "spectral_gap_matches_expected": boundary_transfer["summary"]["spectral_gap_x1e12"]
        == 173671525179,
        "path_entropy_perplexity_is_broad": path_entropy["global_perplexity_x1e12"]
        >= 41_000_000_000_000,
        "weighted_poincare_center_matches_expected": geometry["weighted_poincare_center"][
            "radius_x1e12"
        ]
        == 50308637915
        and geometry["weighted_poincare_center"]["x_x1e12"] == -50213137809
        and geometry["weighted_poincare_center"]["y_x1e12"] == -3098360902,
        "weighted_center_radius_below_uniform_mean_radius": geometry[
            "weighted_poincare_center"
        ]["radius_x1e12"]
        < geometry["uniform_mean_poincare_radius_x1e12"],
        "stationary_mean_radius_above_uniform_mean_radius": geometry[
            "stationary_mean_poincare_radius_x1e12"
        ]
        > geometry["uniform_mean_poincare_radius_x1e12"],
        "stationary_negative_radius_correlation_is_negative": geometry[
            "stationary_negative_radius_correlation_x1e12"
        ]
        < 0,
        "transfer_edge_table_shape_is_33_by_9": tuple(transfer_edge_table.shape)
        == (33, len(TRANSFER_EDGE_COLUMNS)),
        "stationary_distribution_table_shape_is_12_by_9": tuple(stationary_table.shape)
        == (12, len(STATIONARY_DISTRIBUTION_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(FLOW_OBSERVABLE_COLUMNS)),
        "morse_reeb_tables_available": "directed_path_table" in morse_tables.files,
        "poincare_tables_available": "coordinate_table" in poincare_tables.files,
    }

    witness = {
        "source_sink_path_count": len(path_weight_rows),
        "source_path_count": path_weight_summary["source_path_count"],
        "raw_weight_total_x1e9": path_weight_summary["raw_weight_total_x1e9"],
        "source_raw_weight_x1e9": path_weight_summary["source_raw_weight_x1e9"],
        "global_probability_rounding_error_x1e12": path_weight_summary[
            "global_probability_rounding_error_x1e12"
        ],
        "source_probability_rounding_error_x1e12": path_weight_summary[
            "source_probability_rounding_error_x1e12"
        ],
        "transfer_edge_count": len(edge_rows),
        "flow_edge_count": boundary_transfer["summary"]["flow_edge_count"],
        "return_edge_count": boundary_transfer["summary"]["return_edge_count"],
        "return_probabilities_x1e12": boundary_transfer["summary"][
            "return_probabilities_x1e12"
        ],
        "support_strongly_connected": boundary_transfer["summary"][
            "support_strongly_connected"
        ],
        "recurrent_support_node_count": boundary_transfer["summary"][
            "recurrent_support_node_count"
        ],
        "stationary_distribution_x1e12": boundary_transfer["summary"][
            "stationary_distribution_x1e12"
        ],
        "stationary_mass_sum_x1e12": boundary_transfer["summary"][
            "stationary_mass_sum_x1e12"
        ],
        "stationary_max_node_id": boundary_transfer["summary"]["stationary_max_node_id"],
        "stationary_min_node_id": boundary_transfer["summary"]["stationary_min_node_id"],
        "stationary_basin_masses_x1e12": boundary_transfer["summary"][
            "stationary_basin_masses_x1e12"
        ],
        "path_entropy": path_entropy,
        "spectral_second_modulus_x1e12": boundary_transfer["summary"][
            "spectral_second_modulus_x1e12"
        ],
        "spectral_gap_x1e12": boundary_transfer["summary"]["spectral_gap_x1e12"],
        "geometric_observables": geometry,
        "top_path_weights": boundary_transfer["summary"]["top_path_weights"],
        "top_stationary_edge_flows": boundary_transfer["summary"][
            "top_stationary_edge_flows"
        ],
        "path_weight_table_sha256": sha_array(path_weight_table),
        "transfer_edge_table_sha256": sha_array(transfer_edge_table),
        "stationary_distribution_table_sha256": sha_array(stationary_table),
        "flow_observable_table_sha256": sha_array(observable_table),
        "transition_matrix_sha256": sha_array(transition_matrix),
        "edge_flux_matrix_sha256": sha_array(edge_flux_matrix),
        "stationary_distribution_sha256": sha_array(stationary),
        "transition_support_sha256": sha_array(support),
    }

    certificate = {
        "schema": "c985.d20_boundary_transfer_operator_certificate@1",
        "status": STATUS if all(checks.values()) else "C985_D20_BOUNDARY_TRANSFER_OPERATOR_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the 42 source-sink morphisms carry deterministic tensor/Poincare weights",
            "the induced edge-flux transfer matrix closes the acyclic flow by a source-weighted return from sink 44",
            "the closed transfer support is strongly connected, so all 12 core nodes are recurrent",
            "the unique stationary distribution is certified and concentrated most strongly at sink 44 and source 43",
            "the stationary Poincare center remains near the disk center while stationary mean radius exceeds the uniform core mean radius",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_boundary_transfer_operator@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The 42 source-sink morphisms in the certified d20 Morse/Reeb quotient "
            "induce a tensor/Poincare-weighted boundary transfer operator whose "
            "closed support is recurrent on all 12 core nodes and whose stationary "
            "measure has certified hyperbolic geometry observables."
        ),
        "stage_protocol": {
            "draft": "weight source-sink paths by tensor mass and Poincare hyperbolic length",
            "witness": "materialize path weights, transfer edges, stationary distribution, and flow observables",
            "coherence": "check row-stochasticity, strong connectivity, stationary recurrence, spectral gap, and Poincare observables",
            "closure": "certify the boundary transfer operator and its stationary hyperbolic readout",
            "emit": "emit transfer JSON/CSV/NPZ, certificate, report, verifier command, and next target",
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
            "rewrite_complex_certificate": input_entry(REWRITE_COMPLEX_CERTIFICATE),
            "poincare_report": input_entry(
                POINCARE_REPORT,
                {
                    "status": poincare_report.get("status"),
                    "certificate_sha256": poincare_report.get("certificate_sha256"),
                },
            ),
            "poincare_embedding": input_entry(POINCARE_JSON),
            "poincare_tables": input_entry(POINCARE_TABLES),
            "poincare_certificate": input_entry(POINCARE_CERTIFICATE),
            "morse_reeb_report": input_entry(
                MORSE_REEB_REPORT,
                {
                    "status": morse_report.get("status"),
                    "certificate_sha256": morse_report.get("certificate_sha256"),
                },
            ),
            "morse_reeb": input_entry(MORSE_REEB_JSON),
            "morse_reeb_tables": input_entry(MORSE_REEB_TABLES),
            "morse_reeb_certificate": input_entry(MORSE_REEB_CERTIFICATE),
            "morse_reeb_directed_paths_csv": input_entry(MORSE_REEB_PATHS_CSV),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "boundary_transfer_operator": relpath(
                OUT_DIR / "boundary_transfer_operator.json"
            ),
            "source_sink_path_weights_csv": relpath(
                OUT_DIR / "source_sink_path_weights.csv"
            ),
            "core_transfer_edges_csv": relpath(OUT_DIR / "core_transfer_edges.csv"),
            "stationary_distribution_csv": relpath(
                OUT_DIR / "stationary_distribution.csv"
            ),
            "boundary_flow_observables_csv": relpath(
                OUT_DIR / "boundary_flow_observables.csv"
            ),
            "boundary_transfer_tables": relpath(OUT_DIR / "boundary_transfer_tables.npz"),
            "boundary_transfer_certificate": relpath(
                OUT_DIR / "boundary_transfer_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "tensor/Poincare weights for all 42 source-sink morphisms",
                "the 33-edge closed transfer support: 31 flow edges plus two return edges",
                "row-stochasticity, strong connectivity, and recurrence of all 12 core nodes",
                "the unique stationary distribution and spectral gap of the transfer operator",
                "Poincare barycenter observables of the stationary flow measure",
            ],
            "does_not_certify_because_not_required": [
                "a continuum heat kernel or diffusion limit",
                "a canonical physical probability law beyond the declared weighting rule",
                "mixing-time bounds stronger than the certified spectral gap",
                "an infinite visual boundary or asymptotic Gromov boundary",
                "new C985 associator or pentagon data beyond the existing certificate",
            ],
        },
        "next_highest_yield_item": (
            "Lift the stationary boundary transfer measure from the 12-node core "
            "back to the 20-atom Poincare boundary: push mass through each normal "
            "word's three atom coordinates, then certify which d20 atoms, sectors, "
            "and signature classes carry the recurrent flow."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_boundary_transfer_operator_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified rewrite-complex, Poincare, and Morse/Reeb artifacts",
            "compute tensor/Poincare weights for the 42 source-sink morphisms",
            "build the closed row-stochastic transfer matrix with source-weighted return kernel",
            "solve and verify the stationary distribution and recurrent support",
            "compare stationary flow against Poincare barycenter observables",
            "check source hashes and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "boundary_transfer_operator": boundary_transfer,
        "source_sink_path_weights_csv": csv_text(
            SOURCE_SINK_PATH_WEIGHT_COLUMNS,
            path_weight_rows,
        ),
        "core_transfer_edges_csv": csv_text(TRANSFER_EDGE_COLUMNS, edge_rows),
        "stationary_distribution_csv": csv_text(
            STATIONARY_DISTRIBUTION_COLUMNS,
            stationary_rows,
        ),
        "boundary_flow_observables_csv": csv_text(
            FLOW_OBSERVABLE_COLUMNS,
            observable_row_list,
        ),
        "path_weight_table": path_weight_table,
        "transfer_edge_table": transfer_edge_table,
        "stationary_distribution_table": stationary_table,
        "flow_observable_table": observable_table,
        "transition_matrix": transition_matrix,
        "transition_matrix_x1e12": np.asarray(
            np.rint(transition_matrix * PROBABILITY_SCALE),
            dtype=np.int64,
        ),
        "edge_flux_matrix": edge_flux_matrix,
        "stationary_distribution": stationary,
        "stationary_distribution_x1e12": stationary_x1e12,
        "transition_support": support,
        "boundary_transfer_certificate": certificate,
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
    write_json(OUT_DIR / "boundary_transfer_operator.json", payloads["boundary_transfer_operator"])
    (OUT_DIR / "source_sink_path_weights.csv").write_text(
        payloads["source_sink_path_weights_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "core_transfer_edges.csv").write_text(
        payloads["core_transfer_edges_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "stationary_distribution.csv").write_text(
        payloads["stationary_distribution_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "boundary_flow_observables.csv").write_text(
        payloads["boundary_flow_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "boundary_transfer_tables.npz",
        path_weight_table=payloads["path_weight_table"],
        transfer_edge_table=payloads["transfer_edge_table"],
        stationary_distribution_table=payloads["stationary_distribution_table"],
        flow_observable_table=payloads["flow_observable_table"],
        transition_matrix=payloads["transition_matrix"],
        transition_matrix_x1e12=payloads["transition_matrix_x1e12"],
        edge_flux_matrix=payloads["edge_flux_matrix"],
        stationary_distribution=payloads["stationary_distribution"],
        stationary_distribution_x1e12=payloads["stationary_distribution_x1e12"],
        transition_support=payloads["transition_support"],
    )
    write_json(
        OUT_DIR / "boundary_transfer_certificate.json",
        payloads["boundary_transfer_certificate"],
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
                "source_sink_path_count": witness["source_sink_path_count"],
                "transfer_edge_count": witness["transfer_edge_count"],
                "recurrent_support_node_count": witness["recurrent_support_node_count"],
                "stationary_max_node_id": witness["stationary_max_node_id"],
                "spectral_gap_x1e12": witness["spectral_gap_x1e12"],
                "weighted_poincare_center_radius_x1e12": witness["geometric_observables"][
                    "weighted_poincare_center"
                ]["radius_x1e12"],
                "next_highest_yield_item": payloads["report"]["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
