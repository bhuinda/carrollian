from __future__ import annotations

import hashlib
import json
import math
from fractions import Fraction
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .derive_long_lap import (
        EDGE_COLUMNS as LAP_EDGE_COLUMNS,
        NODE_COLUMNS as LAP_NODE_COLUMNS,
        OUT_DIR as LONG_LAP_DIR,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_lap import (
        EDGE_COLUMNS as LAP_EDGE_COLUMNS,
        NODE_COLUMNS as LAP_NODE_COLUMNS,
        OUT_DIR as LONG_LAP_DIR,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_cut"
STATUS = "LONG_CUT_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

LONG_LAP_REPORT = LONG_LAP_DIR / "report.json"
LONG_LAP_TABLES = LONG_LAP_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_cut.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_cut.py"

MOD_PRIMES = (1_000_000_007, 1_000_000_009)

CUT_COLUMNS = [
    "component_id",
    "node_count",
    "edge_count",
    "min_cut_weight",
    "min_cut_side_size",
    "min_cut_other_size",
    "min_cut_side_basis_sum",
    "min_cut_side_basis_square_sum",
    "external_boundary",
    "ambient_degree",
    "external_conductance_reduced_num",
    "external_conductance_reduced_den",
]
RES_COMPONENT_COLUMNS = [
    "component_id",
    "node_count",
    "finite_pair_count",
    "resistance_min_num_digits",
    "resistance_min_den_digits",
    "resistance_min_num_mod_1000000007",
    "resistance_min_den_mod_1000000007",
    "resistance_min_num_mod_1000000009",
    "resistance_min_den_mod_1000000009",
    "resistance_max_num_digits",
    "resistance_max_den_digits",
    "resistance_max_num_mod_1000000007",
    "resistance_max_den_mod_1000000007",
    "resistance_max_num_mod_1000000009",
    "resistance_max_den_mod_1000000009",
    "resistance_sum_num_digits",
    "resistance_sum_den_digits",
    "resistance_sum_num_mod_1000000007",
    "resistance_sum_den_mod_1000000007",
    "resistance_sum_num_mod_1000000009",
    "resistance_sum_den_mod_1000000009",
    "kirchhoff_num_digits",
    "kirchhoff_den_digits",
    "kirchhoff_num_mod_1000000007",
    "kirchhoff_den_mod_1000000007",
    "kirchhoff_num_mod_1000000009",
    "kirchhoff_den_mod_1000000009",
]
PAIR_COLUMNS = [
    "pair_id",
    "component_id",
    "left_basis_id",
    "right_basis_id",
    "resistance_num",
    "resistance_den",
]
PAIR_DIGEST_COLUMNS = [
    "pair_id",
    "component_id",
    "left_basis_id",
    "right_basis_id",
    "resistance_num_digits",
    "resistance_den_digits",
    "resistance_num_mod_1000000007",
    "resistance_den_mod_1000000007",
    "resistance_num_mod_1000000009",
    "resistance_den_mod_1000000009",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "line_point_count",
    "active_owner_count",
    "component_count",
    "active_pair_count",
    "finite_resistance_pair_count",
    "infinite_resistance_pair_count",
    "active_internal_min_cut",
    "connected_component_min_cut",
    "component_external_positive_count",
    "external_degree_min",
    "external_degree_max",
    "external_degree_zero_count",
    "external_degree_sum",
    "finite_resistance_min_num",
    "finite_resistance_min_den",
    "finite_resistance_max_num_digits",
    "finite_resistance_max_den_digits",
    "finite_resistance_sum_num_digits",
    "finite_resistance_sum_den_digits",
    "finite_resistance_sum_num_mod_1000000007",
    "finite_resistance_sum_den_mod_1000000007",
    "finite_kirchhoff_num_digits",
    "finite_kirchhoff_den_digits",
    "finite_kirchhoff_num_mod_1000000007",
    "finite_kirchhoff_den_mod_1000000007",
    "long_lap_rank",
    "long_lap_nullity",
    "long_lap_input_certified",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def csv_text(columns: list[str], rows: list[dict[str, Any]]) -> str:
    lines = [",".join(columns)]
    lines.extend(",".join(str(row[column]) for column in columns) for row in rows)
    return "\n".join(lines) + "\n"


def table_from_rows(columns: list[str], rows: list[dict[str, int]]) -> np.ndarray:
    return np.asarray(
        [[int(row[column]) for column in columns] for row in rows],
        dtype=np.int64,
    )


def rows_from_table(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def fraction_record(value: Fraction) -> dict[str, int | str]:
    text = f"{value.numerator}/{value.denominator}"
    return {
        "num": value.numerator,
        "den": value.denominator,
        "num_digits": len(str(value.numerator)),
        "den_digits": len(str(value.denominator)),
        "num_mod_1000000007": value.numerator % MOD_PRIMES[0],
        "den_mod_1000000007": value.denominator % MOD_PRIMES[0],
        "num_mod_1000000009": value.numerator % MOD_PRIMES[1],
        "den_mod_1000000009": value.denominator % MOD_PRIMES[1],
        "sha256": hashlib.sha256(text.encode("ascii")).hexdigest(),
    }


def reduce_ratio(num: int, den: int) -> tuple[int, int]:
    if den == 0:
        return 0, 0
    divisor = math.gcd(abs(num), abs(den))
    return num // divisor, den // divisor


def canonical_cut_side(nodes: list[int], side: set[int]) -> list[int]:
    if len(nodes) <= 1:
        return sorted(side)
    node_set = set(nodes)
    other = node_set - side
    choices = [sorted(side), sorted(other)]
    return min(choices, key=lambda item: (len(item), item))


def stoer_wagner_min_cut(
    nodes: list[int],
    edges: list[tuple[int, int, int]],
) -> tuple[int, list[int]]:
    if len(nodes) <= 1:
        return 0, list(nodes)
    adjacency = {node: {} for node in nodes}
    for left, right, weight in edges:
        adjacency[left][right] = adjacency[left].get(right, 0) + weight
        adjacency[right][left] = adjacency[right].get(left, 0) + weight

    vertices = list(nodes)
    groups = {node: {node} for node in nodes}
    best_weight: int | None = None
    best_side: set[int] = set()
    while len(vertices) > 1:
        used: list[int] = []
        weights = {vertex: 0 for vertex in vertices}
        for index in range(len(vertices)):
            selected = max(
                (vertex for vertex in vertices if vertex not in used),
                key=lambda vertex: (weights[vertex], -vertex),
            )
            used.append(selected)
            if index == len(vertices) - 1:
                source = used[-2]
                target = selected
                cut_weight = int(weights[target])
                candidate = set(groups[target])
                if best_weight is None or cut_weight < best_weight:
                    best_weight = cut_weight
                    best_side = candidate
                elif cut_weight == best_weight:
                    candidate_side = canonical_cut_side(nodes, candidate)
                    current_side = canonical_cut_side(nodes, best_side)
                    if (len(candidate_side), candidate_side) < (
                        len(current_side),
                        current_side,
                    ):
                        best_side = candidate

                for vertex in list(vertices):
                    if vertex in (source, target):
                        continue
                    merged_weight = adjacency[source].get(vertex, 0) + adjacency[
                        target
                    ].get(vertex, 0)
                    if merged_weight:
                        adjacency[source][vertex] = merged_weight
                        adjacency[vertex][source] = merged_weight
                    else:
                        adjacency[source].pop(vertex, None)
                        adjacency[vertex].pop(source, None)
                    adjacency[vertex].pop(target, None)
                vertices.remove(target)
                groups[source] |= groups[target]
                adjacency[source].pop(target, None)
                adjacency.pop(target, None)
                groups.pop(target, None)
                break
            for vertex, weight in adjacency[selected].items():
                if vertex not in used:
                    weights[vertex] += weight
    if best_weight is None:
        return 0, list(nodes)
    return best_weight, canonical_cut_side(nodes, best_side)


def component_laplacian(
    nodes: list[int],
    edge_rows: list[dict[str, int]],
) -> list[list[int]]:
    rank = {owner: index for index, owner in enumerate(nodes)}
    lap = [[0 for _ in nodes] for _ in nodes]
    for row in edge_rows:
        left_owner = int(row["left_basis_id"])
        right_owner = int(row["right_basis_id"])
        if left_owner not in rank or right_owner not in rank:
            continue
        left = rank[left_owner]
        right = rank[right_owner]
        weight = int(row["boundary_count"])
        lap[left][left] += weight
        lap[right][right] += weight
        lap[left][right] -= weight
        lap[right][left] -= weight
    return lap


def inverse_fraction(matrix: list[list[int]]) -> list[list[Fraction]]:
    n = len(matrix)
    augmented = [
        [Fraction(value) for value in row]
        + [Fraction(int(row_index == col_index)) for col_index in range(n)]
        for row_index, row in enumerate(matrix)
    ]
    for col in range(n):
        pivot = None
        for row in range(col, n):
            if augmented[row][col]:
                pivot = row
                break
        if pivot is None:
            raise ValueError("singular resistance matrix")
        if pivot != col:
            augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        pivot_value = augmented[col][col]
        augmented[col] = [value / pivot_value for value in augmented[col]]
        for row in range(n):
            if row == col:
                continue
            scale = augmented[row][col]
            if scale:
                augmented[row] = [
                    augmented[row][index] - scale * augmented[col][index]
                    for index in range(2 * n)
                ]
    return [row[n:] for row in augmented]


def effective_resistance_rows(
    component_id: int,
    nodes: list[int],
    edge_rows: list[dict[str, int]],
    start_pair_id: int,
) -> tuple[list[dict[str, int]], list[dict[str, int]], dict[str, Any], int]:
    if len(nodes) <= 1:
        zero = Fraction(0)
        return [], [], {
            "component_id": component_id,
            "node_count": len(nodes),
            "finite_pair_count": 0,
            "min": fraction_record(zero),
            "max": fraction_record(zero),
            "sum": fraction_record(zero),
            "kirchhoff": fraction_record(zero),
            "min_pairs": [],
            "max_pairs": [],
        }, start_pair_id

    lap = component_laplacian(nodes, edge_rows)
    inverse = inverse_fraction([row[:-1] for row in lap[:-1]])
    ground = len(nodes) - 1

    def diag(index: int) -> Fraction:
        return Fraction(0) if index == ground else inverse[index][index]

    def offdiag(left: int, right: int) -> Fraction:
        if left == ground or right == ground:
            return Fraction(0)
        return inverse[left][right]

    pair_rows: list[dict[str, int]] = []
    pair_digest_rows: list[dict[str, int]] = []
    values: list[tuple[Fraction, int, int]] = []
    pair_id = start_pair_id
    for left_index, left_owner in enumerate(nodes):
        for right_index in range(left_index + 1, len(nodes)):
            right_owner = nodes[right_index]
            resistance = (
                diag(left_index)
                + diag(right_index)
                - 2 * offdiag(left_index, right_index)
            )
            values.append((resistance, left_owner, right_owner))
            record = fraction_record(resistance)
            pair_rows.append(
                {
                    "pair_id": pair_id,
                    "component_id": component_id,
                    "left_basis_id": left_owner,
                    "right_basis_id": right_owner,
                    "resistance_num": resistance.numerator,
                    "resistance_den": resistance.denominator,
                }
            )
            pair_digest_rows.append(
                {
                    "pair_id": pair_id,
                    "component_id": component_id,
                    "left_basis_id": left_owner,
                    "right_basis_id": right_owner,
                    "resistance_num_digits": int(record["num_digits"]),
                    "resistance_den_digits": int(record["den_digits"]),
                    "resistance_num_mod_1000000007": int(
                        record["num_mod_1000000007"]
                    ),
                    "resistance_den_mod_1000000007": int(
                        record["den_mod_1000000007"]
                    ),
                    "resistance_num_mod_1000000009": int(
                        record["num_mod_1000000009"]
                    ),
                    "resistance_den_mod_1000000009": int(
                        record["den_mod_1000000009"]
                    ),
                }
            )
            pair_id += 1

    min_value = min(value for value, _, _ in values)
    max_value = max(value for value, _, _ in values)
    total = sum((value for value, _, _ in values), Fraction(0))
    kirchhoff = len(nodes) * total
    stats = {
        "component_id": component_id,
        "node_count": len(nodes),
        "finite_pair_count": len(values),
        "min": fraction_record(min_value),
        "max": fraction_record(max_value),
        "sum": fraction_record(total),
        "kirchhoff": fraction_record(kirchhoff),
        "min_pairs": [
            [left, right] for value, left, right in values if value == min_value
        ],
        "max_pairs": [
            [left, right] for value, left, right in values if value == max_value
        ],
    }
    return pair_rows, pair_digest_rows, stats, pair_id


def res_component_row(stats: dict[str, Any]) -> dict[str, int]:
    return {
        "component_id": int(stats["component_id"]),
        "node_count": int(stats["node_count"]),
        "finite_pair_count": int(stats["finite_pair_count"]),
        "resistance_min_num_digits": int(stats["min"]["num_digits"]),
        "resistance_min_den_digits": int(stats["min"]["den_digits"]),
        "resistance_min_num_mod_1000000007": int(
            stats["min"]["num_mod_1000000007"]
        ),
        "resistance_min_den_mod_1000000007": int(
            stats["min"]["den_mod_1000000007"]
        ),
        "resistance_min_num_mod_1000000009": int(
            stats["min"]["num_mod_1000000009"]
        ),
        "resistance_min_den_mod_1000000009": int(
            stats["min"]["den_mod_1000000009"]
        ),
        "resistance_max_num_digits": int(stats["max"]["num_digits"]),
        "resistance_max_den_digits": int(stats["max"]["den_digits"]),
        "resistance_max_num_mod_1000000007": int(
            stats["max"]["num_mod_1000000007"]
        ),
        "resistance_max_den_mod_1000000007": int(
            stats["max"]["den_mod_1000000007"]
        ),
        "resistance_max_num_mod_1000000009": int(
            stats["max"]["num_mod_1000000009"]
        ),
        "resistance_max_den_mod_1000000009": int(
            stats["max"]["den_mod_1000000009"]
        ),
        "resistance_sum_num_digits": int(stats["sum"]["num_digits"]),
        "resistance_sum_den_digits": int(stats["sum"]["den_digits"]),
        "resistance_sum_num_mod_1000000007": int(
            stats["sum"]["num_mod_1000000007"]
        ),
        "resistance_sum_den_mod_1000000007": int(
            stats["sum"]["den_mod_1000000007"]
        ),
        "resistance_sum_num_mod_1000000009": int(
            stats["sum"]["num_mod_1000000009"]
        ),
        "resistance_sum_den_mod_1000000009": int(
            stats["sum"]["den_mod_1000000009"]
        ),
        "kirchhoff_num_digits": int(stats["kirchhoff"]["num_digits"]),
        "kirchhoff_den_digits": int(stats["kirchhoff"]["den_digits"]),
        "kirchhoff_num_mod_1000000007": int(
            stats["kirchhoff"]["num_mod_1000000007"]
        ),
        "kirchhoff_den_mod_1000000007": int(
            stats["kirchhoff"]["den_mod_1000000007"]
        ),
        "kirchhoff_num_mod_1000000009": int(
            stats["kirchhoff"]["num_mod_1000000009"]
        ),
        "kirchhoff_den_mod_1000000009": int(
            stats["kirchhoff"]["den_mod_1000000009"]
        ),
    }


def build_rows() -> dict[str, Any]:
    long_lap = load_json(LONG_LAP_REPORT)
    lap_tables = np.load(LONG_LAP_TABLES, allow_pickle=False)
    node_rows = rows_from_table(
        np.asarray(lap_tables["node_table"], dtype=np.int64),
        LAP_NODE_COLUMNS,
    )
    edge_rows = rows_from_table(
        np.asarray(lap_tables["edge_table"], dtype=np.int64),
        LAP_EDGE_COLUMNS,
    )
    active_owner_ids = [int(value) for value in lap_tables["active_owner_ids"]]
    component_ids = [int(value) for value in lap_tables["component_ids"]]
    component_id_set = sorted(set(component_ids))
    owner_component = dict(zip(active_owner_ids, component_ids))
    node_by_owner = {row["basis_id"]: row for row in node_rows}
    components = [
        [owner for owner in active_owner_ids if owner_component[owner] == component_id]
        for component_id in component_id_set
    ]

    cut_rows: list[dict[str, int]] = []
    pair_rows: list[dict[str, int]] = []
    pair_digest_rows: list[dict[str, int]] = []
    res_component_rows: list[dict[str, int]] = []
    component_stats: list[dict[str, Any]] = []
    pair_id = 0
    for component_id, component in zip(component_id_set, components):
        internal_edges = [
            row for row in edge_rows if int(row["component_id"]) == component_id
        ]
        min_cut, side = stoer_wagner_min_cut(
            component,
            [
                (
                    int(row["left_basis_id"]),
                    int(row["right_basis_id"]),
                    int(row["boundary_count"]),
                )
                for row in internal_edges
            ],
        )
        external_boundary = sum(
            int(node_by_owner[owner]["external_weighted_degree"])
            for owner in component
        )
        ambient_degree = sum(
            int(node_by_owner[owner]["ambient_weighted_degree"])
            for owner in component
        )
        ext_num, ext_den = reduce_ratio(external_boundary, ambient_degree)
        cut_rows.append(
            {
                "component_id": component_id,
                "node_count": len(component),
                "edge_count": len(internal_edges),
                "min_cut_weight": min_cut,
                "min_cut_side_size": len(side),
                "min_cut_other_size": len(component) - len(side),
                "min_cut_side_basis_sum": sum(side),
                "min_cut_side_basis_square_sum": sum(owner * owner for owner in side),
                "external_boundary": external_boundary,
                "ambient_degree": ambient_degree,
                "external_conductance_reduced_num": ext_num,
                "external_conductance_reduced_den": ext_den,
            }
        )
        new_pairs, new_pair_digests, stats, pair_id = effective_resistance_rows(
            component_id,
            component,
            internal_edges,
            pair_id,
        )
        pair_rows.extend(new_pairs)
        pair_digest_rows.extend(new_pair_digests)
        res_component_rows.append(res_component_row(stats))
        component_stats.append({**stats, "min_cut_side": side})

    finite_resistances = [
        Fraction(row["resistance_num"], row["resistance_den"]) for row in pair_rows
    ]
    finite_sum = sum(finite_resistances, Fraction(0))
    finite_kirchhoff = sum(
        Fraction(stats["kirchhoff"]["num"], stats["kirchhoff"]["den"])
        for stats in component_stats
    )
    finite_min = min(finite_resistances)
    finite_max = max(finite_resistances)
    active_pair_count = math.comb(len(active_owner_ids), 2)
    external_degrees = [int(row["external_weighted_degree"]) for row in node_rows]
    lap_witness = long_lap["witness"]
    obs = {
        "line_point_count": 985,
        "active_owner_count": len(active_owner_ids),
        "component_count": len(components),
        "active_pair_count": active_pair_count,
        "finite_resistance_pair_count": len(pair_rows),
        "infinite_resistance_pair_count": active_pair_count - len(pair_rows),
        "active_internal_min_cut": 0 if len(components) > 1 else min(
            row["min_cut_weight"] for row in cut_rows
        ),
        "connected_component_min_cut": min(
            row["min_cut_weight"] for row in cut_rows if row["node_count"] > 1
        ),
        "component_external_positive_count": sum(
            1 for row in cut_rows if row["external_boundary"] > 0
        ),
        "external_degree_min": min(external_degrees),
        "external_degree_max": max(external_degrees),
        "external_degree_zero_count": sum(1 for degree in external_degrees if degree == 0),
        "external_degree_sum": sum(external_degrees),
        "finite_resistance_min_num": finite_min.numerator,
        "finite_resistance_min_den": finite_min.denominator,
        "finite_resistance_max_num_digits": len(str(finite_max.numerator)),
        "finite_resistance_max_den_digits": len(str(finite_max.denominator)),
        "finite_resistance_sum_num_digits": len(str(finite_sum.numerator)),
        "finite_resistance_sum_den_digits": len(str(finite_sum.denominator)),
        "finite_resistance_sum_num_mod_1000000007": finite_sum.numerator
        % MOD_PRIMES[0],
        "finite_resistance_sum_den_mod_1000000007": finite_sum.denominator
        % MOD_PRIMES[0],
        "finite_kirchhoff_num_digits": len(str(finite_kirchhoff.numerator)),
        "finite_kirchhoff_den_digits": len(str(finite_kirchhoff.denominator)),
        "finite_kirchhoff_num_mod_1000000007": finite_kirchhoff.numerator
        % MOD_PRIMES[0],
        "finite_kirchhoff_den_mod_1000000007": finite_kirchhoff.denominator
        % MOD_PRIMES[0],
        "long_lap_rank": int(lap_witness["laplacian"]["rank"]),
        "long_lap_nullity": int(lap_witness["laplacian"]["nullity"]),
        "long_lap_input_certified": int(
            long_lap.get("status") == "LONG_LAP_CERTIFIED"
            and long_lap.get("all_checks_pass") is True
        ),
    }
    obs_rows = [
        {"observable_id": code, "observable_code": code, "value": int(obs[name])}
        for name, code in sorted(OBS_CODES.items(), key=lambda item: item[1])
    ]
    return {
        "long_lap": long_lap,
        "cut_rows": cut_rows,
        "res_component_rows": res_component_rows,
        "pair_rows": pair_rows,
        "pair_digest_rows": pair_digest_rows,
        "component_stats": component_stats,
        "obs": obs,
        "obs_rows": obs_rows,
        "finite_summary": {
            "min": fraction_record(finite_min),
            "max": fraction_record(finite_max),
            "sum": fraction_record(finite_sum),
            "kirchhoff": fraction_record(finite_kirchhoff),
        },
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    cut_table = table_from_rows(CUT_COLUMNS, rows["cut_rows"])
    res_component_table = table_from_rows(
        RES_COMPONENT_COLUMNS,
        rows["res_component_rows"],
    )
    pair_digest_table = table_from_rows(
        PAIR_DIGEST_COLUMNS,
        rows["pair_digest_rows"],
    )
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    pair_csv = csv_text(PAIR_COLUMNS, rows["pair_rows"])
    cut_signature = [
        (
            row["component_id"],
            row["node_count"],
            row["edge_count"],
            row["min_cut_weight"],
            row["min_cut_side_size"],
            row["min_cut_other_size"],
            row["min_cut_side_basis_sum"],
            row["min_cut_side_basis_square_sum"],
            row["external_boundary"],
            row["ambient_degree"],
            row["external_conductance_reduced_num"],
            row["external_conductance_reduced_den"],
        )
        for row in rows["cut_rows"]
    ]
    checks = {
        "long_lap_input_certified": obs["long_lap_input_certified"] == 1,
        "pair_partition_exact": (
            obs["active_owner_count"],
            obs["component_count"],
            obs["active_pair_count"],
            obs["finite_resistance_pair_count"],
            obs["infinite_resistance_pair_count"],
            obs["long_lap_rank"],
            obs["long_lap_nullity"],
        )
        == (51, 3, 1_275, 664, 611, 48, 3),
        "cut_fingerprint_exact": cut_signature
        == [
            (0, 33, 61, 2, 1, 32, 138, 19_044, 1_342, 3_024, 671, 1_512),
            (1, 1, 0, 0, 1, 0, 7, 49, 864, 864, 1, 1),
            (2, 17, 30, 2, 1, 16, 174, 30_276, 2_378, 11_954, 1_189, 5_977),
        ],
        "active_cut_split_exact": (
            obs["active_internal_min_cut"],
            obs["connected_component_min_cut"],
            obs["component_external_positive_count"],
        )
        == (0, 2, 3),
        "external_degree_fingerprint_exact": (
            obs["external_degree_min"],
            obs["external_degree_max"],
            obs["external_degree_zero_count"],
            obs["external_degree_sum"],
        )
        == (0, 1_003, 14, 4_584),
        "resistance_fingerprint_exact": (
            obs["finite_resistance_min_num"],
            obs["finite_resistance_min_den"],
            obs["finite_resistance_max_num_digits"],
            obs["finite_resistance_max_den_digits"],
            obs["finite_resistance_sum_num_digits"],
            obs["finite_resistance_sum_den_digits"],
            obs["finite_resistance_sum_num_mod_1000000007"],
            obs["finite_resistance_sum_den_mod_1000000007"],
            obs["finite_kirchhoff_num_digits"],
            obs["finite_kirchhoff_den_digits"],
            obs["finite_kirchhoff_num_mod_1000000007"],
            obs["finite_kirchhoff_den_mod_1000000007"],
        )
        == (1, 733, 32, 32, 57, 54, 818_911_361, 398_565_772, 57, 53, 20_321_197, 36_233_252),
        "pair_csv_sha256_exact": hashlib.sha256(pair_csv.encode("utf-8")).hexdigest()
        == "ca8e79cb1408dbcd1953dd482d29500b66a451d2bfa6b1a0649a4c03aca54bcc",
        "table_shapes_match": (
            tuple(cut_table.shape),
            tuple(res_component_table.shape),
            tuple(pair_digest_table.shape),
            tuple(obs_table.shape),
        )
        == (
            (3, len(CUT_COLUMNS)),
            (3, len(RES_COMPONENT_COLUMNS)),
            (664, len(PAIR_DIGEST_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "long_lap_cut_resistance",
        "scope": {
            "source": "long_lap active owner graph",
            "rule": "finite effective resistance is computed inside connected active components; cross-component resistance is infinite",
        },
        "cut": {
            "active_internal_min_cut": obs["active_internal_min_cut"],
            "connected_component_min_cut": obs["connected_component_min_cut"],
            "component_external_positive_count": obs[
                "component_external_positive_count"
            ],
            "component_rows": [
                {**row, "min_cut_side": stats["min_cut_side"]}
                for row, stats in zip(rows["cut_rows"], rows["component_stats"])
            ],
            "cut_table_sha256": sha_array(cut_table),
        },
        "resistance": {
            "active_pair_count": obs["active_pair_count"],
            "finite_pair_count": obs["finite_resistance_pair_count"],
            "infinite_pair_count": obs["infinite_resistance_pair_count"],
            "finite_summary": rows["finite_summary"],
            "component_stats": rows["component_stats"],
            "pair_csv_sha256": hashlib.sha256(pair_csv.encode("utf-8")).hexdigest(),
            "pair_digest_table_sha256": sha_array(pair_digest_table),
            "res_component_table_sha256": sha_array(res_component_table),
        },
        "external_degree": {
            "min": obs["external_degree_min"],
            "max": obs["external_degree_max"],
            "zero_count": obs["external_degree_zero_count"],
            "sum": obs["external_degree_sum"],
        },
        "lap_context": {
            "rank": obs["long_lap_rank"],
            "nullity": obs["long_lap_nullity"],
        },
        "observable_table_sha256": sha_array(obs_table),
    }
    cut = {
        "schema": "long.cut@1",
        "object": "long_lap_cut_resistance",
        "status": STATUS if all(checks.values()) else "LONG_CUT_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.cut.report@1",
        "status": cut["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_cut certifies exact cut and effective-resistance fingerprints "
            "for the long_lap active owner graph: 664 finite within-component "
            "resistance pairs, 611 infinite cross-component pairs, active "
            "min-cut zero, and positive component-to-ambient leakage."
        ),
        "stage_protocol": {
            "draft": "reuse the long_lap active owner graph",
            "witness": "compute exact min cuts and rational effective resistances",
            "coherence": "check pair partition, cut rows, resistance fingerprints, and external leakage",
            "closure": "emit cut, component-resistance, pair-resistance, table, certificate, manifest, and report artifacts",
            "emit": "write long_cut artifacts and verifier hook",
        },
        "inputs": {
            "long_lap_report": input_entry(
                LONG_LAP_REPORT,
                {"status": rows["long_lap"].get("status")},
            ),
            "long_lap_tables": input_entry(LONG_LAP_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "cut": relpath(OUT_DIR / "cut.json"),
            "cut_csv": relpath(OUT_DIR / "cut.csv"),
            "res_component_csv": relpath(OUT_DIR / "res_component.csv"),
            "pair_csv": relpath(OUT_DIR / "pair.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the active owner graph has 664 finite resistance pairs and 611 cross-component infinite pairs",
                "the whole active graph has min-cut zero because it has three components",
                "each nontrivial connected active component has weighted min-cut two",
                "every active component has positive leakage to the ambient long_rec graph",
            ],
            "does_not_certify_because_out_of_scope": [
                "resistance through inactive ambient owner nodes",
                "support-changing recouplings outside the long_eta2 active owner set",
                "unbounded rebuilt-carrier repairs",
                "spectral-gap algebraic-number certificates",
            ],
        },
        "next_highest_yield_item": (
            "Build long_flow: solve the ambient leakage flow from the active components "
            "into long_rec to identify which inactive owners carry the relaxation."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.cut.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.cut.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "cut": cut,
        "cut_csv": csv_text(CUT_COLUMNS, rows["cut_rows"]),
        "res_component_csv": csv_text(
            RES_COMPONENT_COLUMNS,
            rows["res_component_rows"],
        ),
        "pair_csv": pair_csv,
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "cut_table": cut_table,
        "res_component_table": res_component_table,
        "pair_digest_table": pair_digest_table,
        "observable_table": obs_table,
        "cert": cert,
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
    obligations.sort(key=lambda row: str(row["id"]))
    index = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": obligations,
    }
    index["registry_sha256"] = self_hash(index, "registry_sha256")
    write_json(INDEX_PATH, index)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / "cut.json", payloads["cut"])
    (OUT_DIR / "cut.csv").write_text(payloads["cut_csv"], encoding="utf-8")
    (OUT_DIR / "res_component.csv").write_text(
        payloads["res_component_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "pair.csv").write_text(payloads["pair_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        cut_table=payloads["cut_table"],
        res_component_table=payloads["res_component_table"],
        pair_digest_table=payloads["pair_digest_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(OUT_DIR / "cert.json", payloads["cert"])
    write_json(OUT_DIR / "report.json", payloads["report"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    update_index(payloads["report"])


def main() -> None:
    payloads = build_payloads()
    write_payloads(payloads)
    report = payloads["report"]
    print(
        json.dumps(
            {
                "status": report["status"],
                "all_checks_pass": report["all_checks_pass"],
                "certificate_sha256": report["certificate_sha256"],
                "report": relpath(OUT_DIR / "report.json"),
                "manifest": relpath(OUT_DIR / "manifest.json"),
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
