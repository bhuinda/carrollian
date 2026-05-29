from __future__ import annotations

import hashlib
import json
import math
from collections import deque
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
    from .derive_eta6_core import OUT_DIR as ETA6_CORE_DIR
    from .derive_long_eta2 import (
        INDUCED_EDGE_COLUMNS,
        OUT_DIR as LONG_ETA2_DIR,
        OWNER_COLUMNS_OUT as ETA2_OWNER_COLUMNS,
    )
    from .derive_long_rec import (
        EDGE_COLUMNS as REC_EDGE_COLUMNS,
        OUT_DIR as LONG_REC_DIR,
        OWNER_COLUMNS as REC_OWNER_COLUMNS,
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
    from derive_eta6_core import OUT_DIR as ETA6_CORE_DIR
    from derive_long_eta2 import (
        INDUCED_EDGE_COLUMNS,
        OUT_DIR as LONG_ETA2_DIR,
        OWNER_COLUMNS_OUT as ETA2_OWNER_COLUMNS,
    )
    from derive_long_rec import (
        EDGE_COLUMNS as REC_EDGE_COLUMNS,
        OUT_DIR as LONG_REC_DIR,
        OWNER_COLUMNS as REC_OWNER_COLUMNS,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_lap"
STATUS = "LONG_LAP_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

LONG_ETA2_REPORT = LONG_ETA2_DIR / "report.json"
LONG_ETA2_TABLES = LONG_ETA2_DIR / "tables.npz"
LONG_REC_REPORT = LONG_REC_DIR / "report.json"
LONG_REC_TABLES = LONG_REC_DIR / "tables.npz"
ETA6_CORE_REPORT = ETA6_CORE_DIR / "report.json"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_lap.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_lap.py"

RANK_PRIMES = (1_000_000_007, 1_000_000_009)

NODE_COLUMNS = [
    "owner_rank",
    "basis_id",
    "component_id",
    "weak_class_code",
    "support_occurrence_count",
    "mult_occurrence_count",
    "owner_cell_count",
    "internal_graph_degree",
    "internal_weighted_degree",
    "external_weighted_degree",
    "ambient_graph_degree",
    "ambient_weighted_degree",
]
COMPONENT_COLUMNS = [
    "component_id",
    "node_count",
    "edge_count",
    "internal_weight",
    "source0_internal_weight",
    "source1_internal_weight",
    "internal_degree_sum",
    "ambient_degree",
    "external_boundary",
    "external_conductance_num",
    "external_conductance_den",
    "external_conductance_reduced_num",
    "external_conductance_reduced_den",
    "support_occurrence_count",
    "mult_occurrence_count",
    "owner_cell_count",
    "laplacian_rank",
    "laplacian_nullity",
    "tree_count_digit_count",
    "tree_count_mod_1000000007",
    "tree_count_mod_1000000009",
    "tree_count_sha256",
]
COMPONENT_INT_COLUMNS = [
    column for column in COMPONENT_COLUMNS if column != "tree_count_sha256"
]
EDGE_COLUMNS = [
    "edge_id",
    "component_id",
    "left_basis_id",
    "right_basis_id",
    "source0_boundary_count",
    "source1_boundary_count",
    "boundary_count",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "line_point_count",
    "active_owner_count",
    "induced_edge_count",
    "induced_component_count",
    "induced_component_min_size",
    "induced_component_max_size",
    "internal_weight_total",
    "source0_internal_weight_total",
    "source1_internal_weight_total",
    "internal_degree_sum",
    "ambient_degree_sum",
    "external_boundary_total",
    "full_graph_edge_count",
    "full_graph_boundary_contact_count",
    "full_graph_directed_boundary_contact_count",
    "active_external_conductance_num",
    "active_external_conductance_den",
    "active_external_conductance_reduced_num",
    "active_external_conductance_reduced_den",
    "zero_internal_conductance_flag",
    "laplacian_trace",
    "laplacian_rank",
    "laplacian_nullity",
    "laplacian_rank_mod_1000000007",
    "laplacian_rank_mod_1000000009",
    "laplacian_row_sum_zero_flag",
    "component_rank_sum",
    "component_nullity_sum",
    "active_support_occurrence_total",
    "active_mult_occurrence_total",
    "active_owner_cell_mass",
    "eta6_hpol_margin",
    "eta6_packet_min_margin",
    "eta6_gate_floor",
    "eta6_gate_preserved_count",
    "long_eta2_input_certified",
    "long_rec_input_certified",
    "eta6_core_input_certified",
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


def components_from_edges(
    active_owners: list[int],
    edge_rows: list[dict[str, int]],
) -> tuple[dict[int, int], list[list[int]]]:
    adjacency = {owner: set() for owner in active_owners}
    for row in edge_rows:
        left = int(row["left_basis_id"])
        right = int(row["right_basis_id"])
        adjacency[left].add(right)
        adjacency[right].add(left)
    component_by_owner: dict[int, int] = {}
    components: list[list[int]] = []
    for start in active_owners:
        if start in component_by_owner:
            continue
        component_id = len(components)
        queue: deque[int] = deque([start])
        component_by_owner[start] = component_id
        component: list[int] = []
        while queue:
            node = queue.popleft()
            component.append(node)
            for nxt in sorted(adjacency[node]):
                if nxt not in component_by_owner:
                    component_by_owner[nxt] = component_id
                    queue.append(nxt)
        components.append(component)
    return component_by_owner, components


def laplacian_matrix(
    active_owners: list[int],
    edge_rows: list[dict[str, int]],
) -> np.ndarray:
    rank_by_owner = {owner: rank for rank, owner in enumerate(active_owners)}
    lap = np.zeros((len(active_owners), len(active_owners)), dtype=np.int64)
    for row in edge_rows:
        left = rank_by_owner[int(row["left_basis_id"])]
        right = rank_by_owner[int(row["right_basis_id"])]
        weight = int(row["boundary_count"])
        lap[left, left] += weight
        lap[right, right] += weight
        lap[left, right] -= weight
        lap[right, left] -= weight
    return lap


def modular_rank(matrix: np.ndarray, prime: int) -> int:
    values = [[int(value) % prime for value in row] for row in matrix.tolist()]
    row_count = len(values)
    col_count = len(values[0]) if values else 0
    rank = 0
    for col in range(col_count):
        pivot = None
        for row in range(rank, row_count):
            if values[row][col] % prime:
                pivot = row
                break
        if pivot is None:
            continue
        values[rank], values[pivot] = values[pivot], values[rank]
        inv = pow(values[rank][col], -1, prime)
        values[rank] = [(item * inv) % prime for item in values[rank]]
        for row in range(row_count):
            if row == rank:
                continue
            factor = values[row][col] % prime
            if factor:
                values[row] = [
                    (values[row][idx] - factor * values[rank][idx]) % prime
                    for idx in range(col_count)
                ]
        rank += 1
        if rank == row_count:
            break
    return rank


def bareiss_det(matrix: list[list[int]]) -> int:
    n = len(matrix)
    if n == 0:
        return 1
    if n == 1:
        return int(matrix[0][0])
    values = [row[:] for row in matrix]
    sign = 1
    previous = 1
    for k in range(n - 1):
        pivot = None
        for row in range(k, n):
            if values[row][k] != 0:
                pivot = row
                break
        if pivot is None:
            return 0
        if pivot != k:
            values[k], values[pivot] = values[pivot], values[k]
            sign *= -1
        pivot_value = values[k][k]
        for row in range(k + 1, n):
            for col in range(k + 1, n):
                values[row][col] = (
                    values[row][col] * pivot_value
                    - values[row][k] * values[k][col]
                ) // previous
        previous = pivot_value
        for row in range(k + 1, n):
            values[row][k] = 0
        for col in range(k + 1, n):
            values[k][col] = 0
    return sign * int(values[n - 1][n - 1])


def tree_count_for_component(
    component: list[int],
    edge_rows: list[dict[str, int]],
) -> int:
    if len(component) <= 1:
        return 1
    rank = {owner: index for index, owner in enumerate(component)}
    lap = [[0 for _ in component] for _ in component]
    component_set = set(component)
    for row in edge_rows:
        left_owner = int(row["left_basis_id"])
        right_owner = int(row["right_basis_id"])
        if left_owner not in component_set or right_owner not in component_set:
            continue
        left = rank[left_owner]
        right = rank[right_owner]
        weight = int(row["boundary_count"])
        lap[left][left] += weight
        lap[right][right] += weight
        lap[left][right] -= weight
        lap[right][left] -= weight
    cofactor = [row[:-1] for row in lap[:-1]]
    det = bareiss_det(cofactor)
    if det <= 0:
        raise ValueError("component tree count must be positive")
    return det


def tree_fingerprint(value: int) -> dict[str, int | str]:
    text = str(value)
    return {
        "tree_count_digit_count": len(text),
        "tree_count_mod_1000000007": value % RANK_PRIMES[0],
        "tree_count_mod_1000000009": value % RANK_PRIMES[1],
        "tree_count_sha256": hashlib.sha256(text.encode("ascii")).hexdigest(),
    }


def reduce_ratio(num: int, den: int) -> tuple[int, int]:
    if den == 0:
        return 0, 0
    divisor = math.gcd(abs(num), abs(den))
    return num // divisor, den // divisor


def build_rows() -> dict[str, Any]:
    long_eta2 = load_json(LONG_ETA2_REPORT)
    long_rec = load_json(LONG_REC_REPORT)
    eta6_core = load_json(ETA6_CORE_REPORT)
    eta2_tables = np.load(LONG_ETA2_TABLES, allow_pickle=False)
    rec_tables = np.load(LONG_REC_TABLES, allow_pickle=False)
    eta2_owner_rows = rows_from_table(
        np.asarray(eta2_tables["owner_table"], dtype=np.int64),
        ETA2_OWNER_COLUMNS,
    )
    eta2_edge_rows = rows_from_table(
        np.asarray(eta2_tables["edge_table"], dtype=np.int64),
        INDUCED_EDGE_COLUMNS,
    )
    rec_owner_rows = rows_from_table(
        np.asarray(rec_tables["owner_table"], dtype=np.int64),
        REC_OWNER_COLUMNS,
    )
    rec_edge_rows = rows_from_table(
        np.asarray(rec_tables["edge_table"], dtype=np.int64),
        REC_EDGE_COLUMNS,
    )
    rec_owner_by_id = {row["basis_id"]: row for row in rec_owner_rows}
    active_owners = [row["basis_id"] for row in eta2_owner_rows]
    component_by_owner, components = components_from_edges(active_owners, eta2_edge_rows)
    lap = laplacian_matrix(active_owners, eta2_edge_rows)
    rank_mods = {prime: modular_rank(lap, prime) for prime in RANK_PRIMES}

    internal_graph_degree = {owner: 0 for owner in active_owners}
    internal_weighted_degree = {owner: 0 for owner in active_owners}
    for row in eta2_edge_rows:
        left = int(row["left_basis_id"])
        right = int(row["right_basis_id"])
        weight = int(row["boundary_count"])
        internal_graph_degree[left] += 1
        internal_graph_degree[right] += 1
        internal_weighted_degree[left] += weight
        internal_weighted_degree[right] += weight

    node_rows: list[dict[str, int]] = []
    eta2_owner_by_id = {row["basis_id"]: row for row in eta2_owner_rows}
    for row in eta2_owner_rows:
        owner_id = int(row["basis_id"])
        rec_owner = rec_owner_by_id[owner_id]
        ambient_weighted = int(rec_owner["weighted_degree"])
        internal_weighted = int(internal_weighted_degree[owner_id])
        node_rows.append(
            {
                "owner_rank": int(row["owner_rank"]),
                "basis_id": owner_id,
                "component_id": int(component_by_owner[owner_id]),
                "weak_class_code": int(row["weak_class_code"]),
                "support_occurrence_count": int(row["support_occurrence_count"]),
                "mult_occurrence_count": int(row["mult_occurrence_count"]),
                "owner_cell_count": int(row["owner_cell_count"]),
                "internal_graph_degree": int(internal_graph_degree[owner_id]),
                "internal_weighted_degree": internal_weighted,
                "external_weighted_degree": ambient_weighted - internal_weighted,
                "ambient_graph_degree": int(rec_owner["graph_degree"]),
                "ambient_weighted_degree": ambient_weighted,
            }
        )

    edge_rows: list[dict[str, int]] = []
    for edge_id, row in enumerate(
        sorted(
            eta2_edge_rows,
            key=lambda item: (item["left_basis_id"], item["right_basis_id"]),
        )
    ):
        component_id = component_by_owner[int(row["left_basis_id"])]
        edge_rows.append(
            {
                "edge_id": edge_id,
                "component_id": component_id,
                "left_basis_id": int(row["left_basis_id"]),
                "right_basis_id": int(row["right_basis_id"]),
                "source0_boundary_count": int(row["source0_boundary_count"]),
                "source1_boundary_count": int(row["source1_boundary_count"]),
                "boundary_count": int(row["boundary_count"]),
            }
        )

    component_rows: list[dict[str, Any]] = []
    for component_id, component in enumerate(components):
        component_set = set(component)
        internal_edges = [
            row
            for row in edge_rows
            if int(row["left_basis_id"]) in component_set
            and int(row["right_basis_id"]) in component_set
        ]
        internal_weight = sum(int(row["boundary_count"]) for row in internal_edges)
        source0_internal = sum(
            int(row["source0_boundary_count"]) for row in internal_edges
        )
        source1_internal = sum(
            int(row["source1_boundary_count"]) for row in internal_edges
        )
        ambient_degree = sum(
            int(rec_owner_by_id[owner]["weighted_degree"]) for owner in component
        )
        external_boundary = ambient_degree - 2 * internal_weight
        reduced_num, reduced_den = reduce_ratio(external_boundary, ambient_degree)
        tree_count = tree_count_for_component(component, edge_rows)
        tree_data = tree_fingerprint(tree_count)
        component_rows.append(
            {
                "component_id": component_id,
                "node_count": len(component),
                "edge_count": len(internal_edges),
                "internal_weight": internal_weight,
                "source0_internal_weight": source0_internal,
                "source1_internal_weight": source1_internal,
                "internal_degree_sum": 2 * internal_weight,
                "ambient_degree": ambient_degree,
                "external_boundary": external_boundary,
                "external_conductance_num": external_boundary,
                "external_conductance_den": ambient_degree,
                "external_conductance_reduced_num": reduced_num,
                "external_conductance_reduced_den": reduced_den,
                "support_occurrence_count": sum(
                    int(eta2_owner_by_id[owner]["support_occurrence_count"])
                    for owner in component
                ),
                "mult_occurrence_count": sum(
                    int(eta2_owner_by_id[owner]["mult_occurrence_count"])
                    for owner in component
                ),
                "owner_cell_count": sum(
                    int(eta2_owner_by_id[owner]["owner_cell_count"])
                    for owner in component
                ),
                "laplacian_rank": len(component) - 1,
                "laplacian_nullity": 1,
                **tree_data,
            }
        )

    internal_weight_total = sum(row["boundary_count"] for row in edge_rows)
    source0_total = sum(row["source0_boundary_count"] for row in edge_rows)
    source1_total = sum(row["source1_boundary_count"] for row in edge_rows)
    ambient_degree_sum = sum(row["ambient_weighted_degree"] for row in node_rows)
    external_boundary_total = ambient_degree_sum - 2 * internal_weight_total
    active_reduced_num, active_reduced_den = reduce_ratio(
        external_boundary_total,
        ambient_degree_sum,
    )
    lap_rank = len(active_owners) - len(components)
    lap_nullity = len(components)
    eta6_witness = eta6_core["witness"]
    obs = {
        "line_point_count": int(
            long_rec["witness"]["line"]["point_count"]
        ),
        "active_owner_count": len(active_owners),
        "induced_edge_count": len(edge_rows),
        "induced_component_count": len(components),
        "induced_component_min_size": min(len(component) for component in components),
        "induced_component_max_size": max(len(component) for component in components),
        "internal_weight_total": internal_weight_total,
        "source0_internal_weight_total": source0_total,
        "source1_internal_weight_total": source1_total,
        "internal_degree_sum": 2 * internal_weight_total,
        "ambient_degree_sum": ambient_degree_sum,
        "external_boundary_total": external_boundary_total,
        "full_graph_edge_count": int(
            long_rec["witness"]["transition_kernel"]["edge_count"]
        ),
        "full_graph_boundary_contact_count": sum(
            int(row["boundary_count"]) for row in rec_edge_rows
        ),
        "full_graph_directed_boundary_contact_count": 2
        * sum(int(row["boundary_count"]) for row in rec_edge_rows),
        "active_external_conductance_num": external_boundary_total,
        "active_external_conductance_den": ambient_degree_sum,
        "active_external_conductance_reduced_num": active_reduced_num,
        "active_external_conductance_reduced_den": active_reduced_den,
        "zero_internal_conductance_flag": int(len(components) > 1),
        "laplacian_trace": int(np.trace(lap)),
        "laplacian_rank": lap_rank,
        "laplacian_nullity": lap_nullity,
        "laplacian_rank_mod_1000000007": rank_mods[RANK_PRIMES[0]],
        "laplacian_rank_mod_1000000009": rank_mods[RANK_PRIMES[1]],
        "laplacian_row_sum_zero_flag": int(bool(np.all(lap.sum(axis=1) == 0))),
        "component_rank_sum": sum(int(row["laplacian_rank"]) for row in component_rows),
        "component_nullity_sum": sum(
            int(row["laplacian_nullity"]) for row in component_rows
        ),
        "active_support_occurrence_total": sum(
            int(row["support_occurrence_count"]) for row in node_rows
        ),
        "active_mult_occurrence_total": sum(
            int(row["mult_occurrence_count"]) for row in node_rows
        ),
        "active_owner_cell_mass": sum(int(row["owner_cell_count"]) for row in node_rows),
        "eta6_hpol_margin": int(eta6_witness["gordan_gap"]["hpol_margin"]),
        "eta6_packet_min_margin": int(eta6_witness["margin_packet"]["min_margin"]),
        "eta6_gate_floor": int(eta6_witness["gate"]["floor"]),
        "eta6_gate_preserved_count": int(
            eta6_witness["gate"]["eta6_preserved_count"]
        ),
        "long_eta2_input_certified": int(
            long_eta2.get("status") == "LONG_ETA2_CERTIFIED"
            and long_eta2.get("all_checks_pass") is True
        ),
        "long_rec_input_certified": int(
            long_rec.get("status") == "LONG_REC_CERTIFIED"
            and long_rec.get("all_checks_pass") is True
        ),
        "eta6_core_input_certified": int(
            eta6_core.get("status") == "ETA6_CORE_CERTIFIED"
            and eta6_core.get("all_checks_pass") is True
        ),
    }
    obs_rows = [
        {"observable_id": code, "observable_code": code, "value": int(obs[name])}
        for name, code in sorted(OBS_CODES.items(), key=lambda item: item[1])
    ]
    return {
        "long_eta2": long_eta2,
        "long_rec": long_rec,
        "eta6_core": eta6_core,
        "node_rows": node_rows,
        "edge_rows": edge_rows,
        "component_rows": component_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "laplacian": lap,
        "component_ids": np.asarray(
            [component_by_owner[owner] for owner in active_owners],
            dtype=np.int16,
        ),
        "active_owner_ids": np.asarray(active_owners, dtype=np.int16),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    node_table = table_from_rows(NODE_COLUMNS, rows["node_rows"])
    component_table = table_from_rows(
        COMPONENT_INT_COLUMNS,
        rows["component_rows"],
    )
    edge_table = table_from_rows(EDGE_COLUMNS, rows["edge_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    component_signature = [
        (
            row["component_id"],
            row["node_count"],
            row["edge_count"],
            row["internal_weight"],
            row["source0_internal_weight"],
            row["source1_internal_weight"],
            row["ambient_degree"],
            row["external_boundary"],
            row["external_conductance_reduced_num"],
            row["external_conductance_reduced_den"],
            row["support_occurrence_count"],
            row["mult_occurrence_count"],
            row["owner_cell_count"],
            row["laplacian_rank"],
            row["laplacian_nullity"],
        )
        for row in rows["component_rows"]
    ]
    checks = {
        "inputs_certified": (
            obs["long_eta2_input_certified"],
            obs["long_rec_input_certified"],
            obs["eta6_core_input_certified"],
        )
        == (1, 1, 1),
        "active_subgraph_fingerprint_exact": (
            obs["line_point_count"],
            obs["active_owner_count"],
            obs["induced_edge_count"],
            obs["induced_component_count"],
            obs["induced_component_min_size"],
            obs["induced_component_max_size"],
        )
        == (985, 51, 91, 3, 1, 33),
        "weights_and_leakage_exact": (
            obs["internal_weight_total"],
            obs["source0_internal_weight_total"],
            obs["source1_internal_weight_total"],
            obs["internal_degree_sum"],
            obs["ambient_degree_sum"],
            obs["external_boundary_total"],
            obs["active_external_conductance_reduced_num"],
            obs["active_external_conductance_reduced_den"],
            obs["zero_internal_conductance_flag"],
        )
        == (5_629, 4_938, 691, 11_258, 15_842, 4_584, 2_292, 7_921, 1),
        "full_graph_context_exact": (
            obs["full_graph_edge_count"],
            obs["full_graph_boundary_contact_count"],
            obs["full_graph_directed_boundary_contact_count"],
        )
        == (642, 18_117, 36_234),
        "laplacian_rank_and_trace_exact": (
            obs["laplacian_trace"],
            obs["laplacian_rank"],
            obs["laplacian_nullity"],
            obs["laplacian_rank_mod_1000000007"],
            obs["laplacian_rank_mod_1000000009"],
            obs["laplacian_row_sum_zero_flag"],
            obs["component_rank_sum"],
            obs["component_nullity_sum"],
        )
        == (11_258, 48, 3, 48, 48, 1, 48, 3),
        "component_fingerprint_exact": component_signature
        == [
            (
                0,
                33,
                61,
                841,
                502,
                339,
                3_024,
                1_342,
                671,
                1_512,
                3_175_424_320,
                15_292_956_672,
                36_560,
                32,
                1,
            ),
            (
                1,
                1,
                0,
                0,
                0,
                0,
                864,
                864,
                1,
                1,
                1_601_231_360,
                9_154_068_480,
                96_023,
                0,
                1,
            ),
            (
                2,
                17,
                30,
                4_788,
                4_436,
                352,
                11_954,
                2_378,
                1_189,
                5_977,
                11_484_523_584,
                63_708_069_888,
                616_656,
                16,
                1,
            ),
        ],
        "owner_mass_fingerprint_exact": (
            obs["active_support_occurrence_total"],
            obs["active_mult_occurrence_total"],
            obs["active_owner_cell_mass"],
        )
        == (16_261_179_264, 88_155_095_040, 749_239),
        "eta6_margin_context_exact": (
            obs["eta6_hpol_margin"],
            obs["eta6_packet_min_margin"],
            obs["eta6_gate_floor"],
            obs["eta6_gate_preserved_count"],
        )
        == (1, 1, 492_736, 6),
        "table_shapes_match": (
            tuple(node_table.shape),
            tuple(component_table.shape),
            tuple(edge_table.shape),
            tuple(obs_table.shape),
            tuple(rows["laplacian"].shape),
            tuple(rows["component_ids"].shape),
            tuple(rows["active_owner_ids"].shape),
        )
        == (
            (51, len(NODE_COLUMNS)),
            (3, len(COMPONENT_INT_COLUMNS)),
            (91, len(EDGE_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
            (51, 51),
            (51,),
            (51,),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "long_eta2_induced_laplacian_conductance",
        "scope": {
            "kind": "51_owner_induced_subgraph",
            "source": "long_eta2 full p21 gate support-fiber projection",
            "ambient": "long_rec owner transition graph",
        },
        "active_subgraph": {
            "owner_count": obs["active_owner_count"],
            "edge_count": obs["induced_edge_count"],
            "component_count": obs["induced_component_count"],
            "component_size_range": [
                obs["induced_component_min_size"],
                obs["induced_component_max_size"],
            ],
            "node_table_sha256": sha_array(node_table),
            "edge_table_sha256": sha_array(edge_table),
            "component_table_sha256": sha_array(component_table),
            "active_owner_ids_sha256": sha_array(rows["active_owner_ids"]),
        },
        "laplacian": {
            "trace": obs["laplacian_trace"],
            "rank": obs["laplacian_rank"],
            "nullity": obs["laplacian_nullity"],
            "rank_rule": "positive weighted graph Laplacian rank is owner_count minus component_count",
            "rank_mod_1000000007": obs["laplacian_rank_mod_1000000007"],
            "rank_mod_1000000009": obs["laplacian_rank_mod_1000000009"],
            "row_sum_zero": bool(obs["laplacian_row_sum_zero_flag"]),
            "laplacian_sha256": sha_array(rows["laplacian"]),
            "component_ids_sha256": sha_array(rows["component_ids"]),
        },
        "conductance": {
            "internal_weight": obs["internal_weight_total"],
            "ambient_degree": obs["ambient_degree_sum"],
            "external_boundary": obs["external_boundary_total"],
            "active_external_ratio": [
                obs["active_external_conductance_reduced_num"],
                obs["active_external_conductance_reduced_den"],
            ],
            "internal_conductance_zero": bool(obs["zero_internal_conductance_flag"]),
            "component_rows": rows["component_rows"],
        },
        "mass": {
            "support_occurrence_total": obs["active_support_occurrence_total"],
            "mult_occurrence_total": obs["active_mult_occurrence_total"],
            "owner_cell_mass": obs["active_owner_cell_mass"],
        },
        "eta6_context": {
            "hpol_margin": obs["eta6_hpol_margin"],
            "packet_min_margin": obs["eta6_packet_min_margin"],
            "gate_floor": obs["eta6_gate_floor"],
            "gate_preserved_count": obs["eta6_gate_preserved_count"],
        },
        "observable_table_sha256": sha_array(obs_table),
    }
    lap = {
        "schema": "long.lap@1",
        "object": "long_eta2_induced_laplacian_conductance",
        "status": STATUS if all(checks.values()) else "LONG_LAP_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.lap.report@1",
        "status": lap["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_lap certifies the exact weighted Laplacian and conductance "
            "data of the 51-owner long_eta2 active subgraph inside the long_rec "
            "transition graph: three induced components, rank 48, nullity 3, "
            "and positive ambient leakage while internal conductance is zero."
        ),
        "stage_protocol": {
            "draft": "take the full long_eta2 owner fiber as the active set",
            "witness": "read long_eta2 owner/edge tables and long_rec ambient degrees",
            "coherence": "check component, leakage, rank, mass, and eta6 margin fingerprints",
            "closure": "emit weighted Laplacian, conductance, and tree-count fingerprints",
            "emit": "write long_lap artifacts and verifier hook",
        },
        "inputs": {
            "long_eta2_report": input_entry(
                LONG_ETA2_REPORT,
                {"status": rows["long_eta2"].get("status")},
            ),
            "long_eta2_tables": input_entry(LONG_ETA2_TABLES),
            "long_rec_report": input_entry(
                LONG_REC_REPORT,
                {"status": rows["long_rec"].get("status")},
            ),
            "long_rec_tables": input_entry(LONG_REC_TABLES),
            "eta6_core_report": input_entry(
                ETA6_CORE_REPORT,
                {"status": rows["eta6_core"].get("status")},
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "lap": relpath(OUT_DIR / "lap.json"),
            "node_csv": relpath(OUT_DIR / "node.csv"),
            "component_csv": relpath(OUT_DIR / "component.csv"),
            "edge_csv": relpath(OUT_DIR / "edge.csv"),
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
                "the exact weighted Laplacian of the long_eta2 active owner subgraph",
                "the induced subgraph has three components, so internal conductance is zero",
                "the active set still leaks to the ambient long_rec graph with ratio 2292/7921",
                "the eta6 margin context attached to this active set is strict in the checked packet",
            ],
            "does_not_certify_because_out_of_scope": [
                "a universal eta6 horizon theorem",
                "all possible active sets outside the p21 full gate fibers",
                "effective resistance or spectral-gap exact algebraic numbers",
                "support change under unbounded or rebuilt-carrier recoupling",
            ],
        },
        "next_highest_yield_item": (
            "Build long_cut: exact min-cut/effective-resistance fingerprints on "
            "the long_lap active set to separate metric relaxation from support crossing."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.lap.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.lap.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "lap": lap,
        "node_csv": csv_text(NODE_COLUMNS, rows["node_rows"]),
        "component_csv": csv_text(COMPONENT_COLUMNS, rows["component_rows"]),
        "edge_csv": csv_text(EDGE_COLUMNS, rows["edge_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "node_table": node_table,
        "component_table": component_table,
        "edge_table": edge_table,
        "observable_table": obs_table,
        "laplacian": rows["laplacian"],
        "component_ids": rows["component_ids"],
        "active_owner_ids": rows["active_owner_ids"],
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
    write_json(OUT_DIR / "lap.json", payloads["lap"])
    (OUT_DIR / "node.csv").write_text(payloads["node_csv"], encoding="utf-8")
    (OUT_DIR / "component.csv").write_text(
        payloads["component_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "edge.csv").write_text(payloads["edge_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        node_table=payloads["node_table"],
        component_table=payloads["component_table"],
        edge_table=payloads["edge_table"],
        observable_table=payloads["observable_table"],
        laplacian=payloads["laplacian"],
        component_ids=payloads["component_ids"],
        active_owner_ids=payloads["active_owner_ids"],
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
