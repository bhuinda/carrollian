from __future__ import annotations

import json
from collections import Counter, defaultdict, deque
from typing import Any

import numpy as np

try:
    from .derive_c985_fusion_multiplicity_typing import OUT_DIR as FUSION_DIR
    from .derive_c985_typed_simple_object_registry import (
        OUT_DIR as REGISTRY_DIR,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .derive_eta6_core import OUT_DIR as ETA6_CORE_DIR
    from .derive_eta6_p5 import EXT_COLUMNS, OUT_DIR as ETA6_P5_DIR
    from .derive_eta6_p21 import BEST_IDS, OUT_DIR as ETA6_P21_DIR
    from .derive_long_eta import OUT_DIR as LONG_ETA_DIR
    from .derive_long_rec import EDGE_COLUMNS, OUT_DIR as LONG_REC_DIR, OWNER_COLUMNS
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_fusion_multiplicity_typing import OUT_DIR as FUSION_DIR
    from derive_c985_typed_simple_object_registry import (
        OUT_DIR as REGISTRY_DIR,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_eta6_core import OUT_DIR as ETA6_CORE_DIR
    from derive_eta6_p5 import EXT_COLUMNS, OUT_DIR as ETA6_P5_DIR
    from derive_eta6_p21 import BEST_IDS, OUT_DIR as ETA6_P21_DIR
    from derive_long_eta import OUT_DIR as LONG_ETA_DIR
    from derive_long_rec import EDGE_COLUMNS, OUT_DIR as LONG_REC_DIR, OWNER_COLUMNS
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_eta2"
STATUS = "LONG_ETA2_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
SOURCE_TARGET = REGISTRY_DIR / "source_target.npy"
FUSION_TENSOR = FUSION_DIR / "fusion_tensor_coo.npz"
ETA6_CORE_REPORT = ETA6_CORE_DIR / "report.json"
ETA6_P21_REPORT = ETA6_P21_DIR / "report.json"
ETA6_P5_TABLES = ETA6_P5_DIR / "tables.npz"
LONG_ETA_REPORT = LONG_ETA_DIR / "report.json"
LONG_REC_REPORT = LONG_REC_DIR / "report.json"
LONG_REC_TABLES = LONG_REC_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_eta2.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_eta2.py"

PARENTHESIZATION_COUNT = 5
PARENT_COLUMNS = [
    "row_id",
    "gate_id",
    "p5_id",
    "parenthesization_id",
    "support_count",
    "expected_support_count",
    "mult_count",
    "expected_mult_count",
    "active_owner_count",
    "support_occurrence_count",
    "mult_occurrence_count",
    "slack_min",
    "slack_max",
    "slack_sum",
    "support_match_flag",
    "mult_match_flag",
]
GATE_COLUMNS = [
    "gate_id",
    "p5_id",
    "support_total",
    "mult_total",
    "active_owner_count",
    "support_occurrence_count",
    "mult_occurrence_count",
    "slack_min",
    "slack_max",
    "slack_sum",
]
OWNER_COLUMNS_OUT = [
    "owner_rank",
    "basis_id",
    "weak_class_code",
    "component_id",
    "owner_cell_count",
    "graph_degree",
    "weighted_degree",
    "support_occurrence_count",
    "mult_occurrence_count",
    "induced_degree",
]
INDUCED_EDGE_COLUMNS = [
    "induced_edge_id",
    "left_basis_id",
    "right_basis_id",
    "source0_boundary_count",
    "source1_boundary_count",
    "boundary_count",
    "left_support_occurrence_count",
    "right_support_occurrence_count",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "line_point_count",
    "gate_count",
    "parenthesization_count",
    "parent_row_count",
    "gate_support_total",
    "gate_mult_total",
    "support_occurrence_total",
    "mult_occurrence_total",
    "active_owner_count",
    "owner_support_occurrence_min",
    "owner_support_occurrence_max",
    "owner_mult_occurrence_min",
    "owner_mult_occurrence_max",
    "slack_min",
    "slack_max",
    "slack_sum",
    "owner_weak_class_count",
    "weak11_owner_count",
    "weak12_owner_count",
    "weak11_support_occurrence",
    "weak12_support_occurrence",
    "weak11_mult_occurrence",
    "weak12_mult_occurrence",
    "owner_induced_edge_count",
    "owner_induced_boundary_count",
    "owner_induced_source0_boundary_count",
    "owner_induced_source1_boundary_count",
    "owner_pair_count",
    "owner_distance_min",
    "owner_distance_max",
    "owner_distance_sum",
    "owner_cell_mass",
    "owner_cell_min",
    "owner_cell_max",
    "induced_component_count",
    "induced_component_max_size",
    "long_component_count",
    "support_projection_flag",
    "mult_projection_flag",
    "p5_expected_counts_match",
    "eta6_core_input_certified",
    "eta6_p21_input_certified",
    "long_eta_input_certified",
    "long_rec_input_certified",
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


def relation_tables(source_target: np.ndarray) -> tuple[dict[tuple[int, int], list[int]], dict[tuple[int, int], set[int]]]:
    by_pair = {(source, target): [] for source in range(6) for target in range(6)}
    for relation_id, (source, target) in enumerate(source_target):
        by_pair[(int(source), int(target))].append(int(relation_id))
    return by_pair, {key: set(value) for key, value in by_pair.items()}


def fusion_out(triples: np.ndarray) -> dict[tuple[int, int], list[tuple[int, int]]]:
    out: dict[tuple[int, int], list[tuple[int, int]]] = defaultdict(list)
    for left, right, output, coeff in triples:
        out[(int(left), int(right))].append((int(output), int(coeff)))
    return out


def add_scaled(target: dict[int, int], source: dict[int, int], scale: int) -> None:
    if scale == 0:
        return
    for key, value in source.items():
        target[key] = target.get(key, 0) + value * scale


State = tuple[int, int, dict[int, int], dict[int, int], int, int, int, int]


def init_state(
    pair: tuple[int, int],
    by_pair: dict[tuple[int, int], list[int]],
) -> dict[int, State]:
    return {
        relation: (1, 1, {}, {}, 0, 0, 10**9, -(10**9))
        for relation in by_pair[pair]
    }


def compose_state(
    left: dict[int, State],
    right: dict[int, State],
    output_pair: tuple[int, int],
    *,
    allowed_by_pair: dict[tuple[int, int], set[int]],
    out: dict[tuple[int, int], list[tuple[int, int]]],
    owner_grid: np.ndarray,
    frontier: np.ndarray,
) -> dict[int, State]:
    allowed = allowed_by_pair[output_pair]
    grouped: dict[int, list[Any]] = {}
    for left_relation, (
        left_support,
        left_mult,
        left_owner_support,
        left_owner_mult,
        left_slack_count,
        left_slack_sum,
        left_slack_min,
        left_slack_max,
    ) in left.items():
        for right_relation, (
            right_support,
            right_mult,
            right_owner_support,
            right_owner_mult,
            right_slack_count,
            right_slack_sum,
            right_slack_min,
            right_slack_max,
        ) in right.items():
            owner_id = int(owner_grid[left_relation, right_relation])
            frontier_target = int(frontier[left_relation, right_relation])
            for output_relation, coeff in out.get((left_relation, right_relation), ()):
                if output_relation not in allowed:
                    continue
                support = left_support * right_support
                mult = left_mult * right_mult * int(coeff)
                slack = int(output_relation) - frontier_target
                row = grouped.setdefault(
                    output_relation,
                    [0, 0, {}, {}, 0, 0, 10**9, -(10**9)],
                )
                row[0] += support
                row[1] += mult
                add_scaled(row[2], left_owner_support, right_support)
                add_scaled(row[2], right_owner_support, left_support)
                row[2][owner_id] = row[2].get(owner_id, 0) + support
                add_scaled(row[3], left_owner_mult, right_mult * int(coeff))
                add_scaled(row[3], right_owner_mult, left_mult * int(coeff))
                row[3][owner_id] = row[3].get(owner_id, 0) + mult
                row[4] += (
                    left_slack_count * right_support
                    + right_slack_count * left_support
                    + support
                )
                row[5] += (
                    left_slack_sum * right_support
                    + right_slack_sum * left_support
                    + support * slack
                )
                row[6] = min(
                    row[6],
                    left_slack_min if left_slack_count else 10**9,
                    right_slack_min if right_slack_count else 10**9,
                    slack,
                )
                row[7] = max(
                    row[7],
                    left_slack_max if left_slack_count else -(10**9),
                    right_slack_max if right_slack_count else -(10**9),
                    slack,
                )
    return {relation: tuple(values) for relation, values in grouped.items()}  # type: ignore[return-value]


def total_state(state: dict[int, State]) -> tuple[int, int, Counter[int], Counter[int], int, int, int, int]:
    support = 0
    mult = 0
    owner_support: Counter[int] = Counter()
    owner_mult: Counter[int] = Counter()
    slack_count = 0
    slack_sum = 0
    slack_min = 10**9
    slack_max = -(10**9)
    for (
        item_support,
        item_mult,
        item_owner_support,
        item_owner_mult,
        item_slack_count,
        item_slack_sum,
        item_slack_min,
        item_slack_max,
    ) in state.values():
        support += item_support
        mult += item_mult
        owner_support.update(item_owner_support)
        owner_mult.update(item_owner_mult)
        slack_count += item_slack_count
        slack_sum += item_slack_sum
        slack_min = min(slack_min, item_slack_min)
        slack_max = max(slack_max, item_slack_max)
    return support, mult, owner_support, owner_mult, slack_count, slack_sum, slack_min, slack_max


def pentagon_states(
    order: tuple[int, int, int, int, int],
    *,
    by_pair: dict[tuple[int, int], list[int]],
    allowed_by_pair: dict[tuple[int, int], set[int]],
    out: dict[tuple[int, int], list[tuple[int, int]]],
    owner_grid: np.ndarray,
    frontier: np.ndarray,
) -> list[dict[int, State]]:
    a, b, c, d, e = order
    init = lambda pair: init_state(pair, by_pair)
    compose = lambda left, right, pair: compose_state(
        left,
        right,
        pair,
        allowed_by_pair=allowed_by_pair,
        out=out,
        owner_grid=owner_grid,
        frontier=frontier,
    )
    ab = init((a, b))
    bc = init((b, c))
    cd = init((c, d))
    de = init((d, e))
    return [
        compose(compose(compose(ab, bc, (a, c)), cd, (a, d)), de, (a, e)),
        compose(compose(ab, compose(bc, cd, (b, d)), (a, d)), de, (a, e)),
        compose(compose(ab, bc, (a, c)), compose(cd, de, (c, e)), (a, e)),
        compose(ab, compose(compose(bc, cd, (b, d)), de, (b, e)), (a, e)),
        compose(ab, compose(bc, compose(cd, de, (c, e)), (b, e)), (a, e)),
    ]


def shortest_distance(adjacency: list[set[int]], start: int, stop: int) -> int:
    if start == stop:
        return 0
    queue: deque[tuple[int, int]] = deque([(start, 0)])
    seen = {start}
    while queue:
        node, distance = queue.popleft()
        for nxt in adjacency[node]:
            if nxt == stop:
                return distance + 1
            if nxt not in seen:
                seen.add(nxt)
                queue.append((nxt, distance + 1))
    return -1


def pairwise_distances(adjacency: list[set[int]], nodes: list[int]) -> list[int]:
    return [
        shortest_distance(adjacency, left, right)
        for index, left in enumerate(nodes)
        for right in nodes[index + 1 :]
    ]


def induced_components(adjacency: list[set[int]], nodes: list[int]) -> list[list[int]]:
    node_set = set(nodes)
    seen: set[int] = set()
    components: list[list[int]] = []
    for start in nodes:
        if start in seen:
            continue
        stack = [start]
        seen.add(start)
        component: list[int] = []
        while stack:
            node = stack.pop()
            component.append(node)
            for nxt in adjacency[node]:
                if nxt in node_set and nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        components.append(component)
    return components


def build_rows() -> dict[str, Any]:
    eta6_core = load_json(ETA6_CORE_REPORT)
    eta6_p21 = load_json(ETA6_P21_REPORT)
    long_eta = load_json(LONG_ETA_REPORT)
    long_rec = load_json(LONG_REC_REPORT)
    source_target = np.load(SOURCE_TARGET, allow_pickle=False)
    triples = np.load(FUSION_TENSOR, allow_pickle=False)["triples"]
    by_pair, allowed_by_pair = relation_tables(source_target)
    out = fusion_out(triples)
    p5_table = np.asarray(
        np.load(ETA6_P5_TABLES, allow_pickle=False)["ext_table"],
        dtype=np.int64,
    )
    p5_rows = {
        row["p5_id"]: row
        for row in rows_from_table(p5_table, EXT_COLUMNS)
    }
    rec_tables = np.load(LONG_REC_TABLES, allow_pickle=False)
    owner_grid = np.asarray(rec_tables["owner_grid"], dtype=np.int16)
    frontier = np.asarray(rec_tables["owner_frontier"], dtype=np.int16)
    owner_table = np.asarray(rec_tables["owner_table"], dtype=np.int64)
    edge_table = np.asarray(rec_tables["edge_table"], dtype=np.int64)
    component_ids = np.asarray(rec_tables["component_ids"], dtype=np.int16)
    adjacency = [set() for _ in range(int(owner_table.shape[0]))]
    for row in edge_table:
        left = int(row[EDGE_COLUMNS.index("left_basis_id")])
        right = int(row[EDGE_COLUMNS.index("right_basis_id")])
        adjacency[left].add(right)
        adjacency[right].add(left)

    parent_rows: list[dict[str, int]] = []
    gate_rows: list[dict[str, int]] = []
    all_owner_support: Counter[int] = Counter()
    all_owner_mult: Counter[int] = Counter()
    row_id = 0
    for gate_id, p5_id in enumerate(BEST_IDS):
        p5 = p5_rows[int(p5_id)]
        states = pentagon_states(
            (p5["a"], p5["b"], p5["c"], p5["d"], p5["e"]),
            by_pair=by_pair,
            allowed_by_pair=allowed_by_pair,
            out=out,
            owner_grid=owner_grid,
            frontier=frontier,
        )
        gate_owner_support: Counter[int] = Counter()
        gate_owner_mult: Counter[int] = Counter()
        gate_support_total = 0
        gate_mult_total = 0
        gate_occurrence_total = 0
        gate_mult_occurrence_total = 0
        gate_slack_sum = 0
        gate_slack_min = 10**9
        gate_slack_max = -(10**9)
        for parenthesization_id, state in enumerate(states):
            (
                support_count,
                mult_count,
                owner_support,
                owner_mult,
                slack_count,
                slack_sum,
                slack_min,
                slack_max,
            ) = total_state(state)
            expected_support = p5[f"p{parenthesization_id}_support"]
            expected_mult = p5[f"p{parenthesization_id}_mult"]
            support_occurrence = int(sum(owner_support.values()))
            mult_occurrence = int(sum(owner_mult.values()))
            parent_rows.append(
                {
                    "row_id": row_id,
                    "gate_id": gate_id,
                    "p5_id": int(p5_id),
                    "parenthesization_id": parenthesization_id,
                    "support_count": support_count,
                    "expected_support_count": expected_support,
                    "mult_count": mult_count,
                    "expected_mult_count": expected_mult,
                    "active_owner_count": len(owner_support),
                    "support_occurrence_count": support_occurrence,
                    "mult_occurrence_count": mult_occurrence,
                    "slack_min": slack_min,
                    "slack_max": slack_max,
                    "slack_sum": slack_sum,
                    "support_match_flag": int(support_count == expected_support),
                    "mult_match_flag": int(mult_count == expected_mult),
                }
            )
            row_id += 1
            gate_owner_support.update(owner_support)
            gate_owner_mult.update(owner_mult)
            all_owner_support.update(owner_support)
            all_owner_mult.update(owner_mult)
            gate_support_total += support_count
            gate_mult_total += mult_count
            gate_occurrence_total += support_occurrence
            gate_mult_occurrence_total += mult_occurrence
            gate_slack_sum += slack_sum
            gate_slack_min = min(gate_slack_min, slack_min)
            gate_slack_max = max(gate_slack_max, slack_max)
        gate_rows.append(
            {
                "gate_id": gate_id,
                "p5_id": int(p5_id),
                "support_total": gate_support_total,
                "mult_total": gate_mult_total,
                "active_owner_count": len(gate_owner_support),
                "support_occurrence_count": gate_occurrence_total,
                "mult_occurrence_count": gate_mult_occurrence_total,
                "slack_min": gate_slack_min,
                "slack_max": gate_slack_max,
                "slack_sum": gate_slack_sum,
            }
        )

    active_owners = sorted(all_owner_support)
    active_owner_set = set(active_owners)
    induced_edges = []
    for row in edge_table:
        left = int(row[EDGE_COLUMNS.index("left_basis_id")])
        right = int(row[EDGE_COLUMNS.index("right_basis_id")])
        if left in active_owner_set and right in active_owner_set:
            induced_edges.append(row)
    induced_degree = Counter()
    for row in induced_edges:
        induced_degree[int(row[EDGE_COLUMNS.index("left_basis_id")])] += 1
        induced_degree[int(row[EDGE_COLUMNS.index("right_basis_id")])] += 1
    owner_rows = []
    for owner_rank, owner_id in enumerate(active_owners):
        owner = owner_table[owner_id]
        owner_rows.append(
            {
                "owner_rank": owner_rank,
                "basis_id": owner_id,
                "weak_class_code": int(owner[OWNER_COLUMNS.index("weak_class_code")]),
                "component_id": int(component_ids[owner_id]),
                "owner_cell_count": int(owner[OWNER_COLUMNS.index("owner_cell_count")]),
                "graph_degree": int(owner[OWNER_COLUMNS.index("graph_degree")]),
                "weighted_degree": int(owner[OWNER_COLUMNS.index("weighted_degree")]),
                "support_occurrence_count": int(all_owner_support[owner_id]),
                "mult_occurrence_count": int(all_owner_mult[owner_id]),
                "induced_degree": int(induced_degree[owner_id]),
            }
        )
    edge_rows = []
    for induced_edge_id, row in enumerate(induced_edges):
        left = int(row[EDGE_COLUMNS.index("left_basis_id")])
        right = int(row[EDGE_COLUMNS.index("right_basis_id")])
        edge_rows.append(
            {
                "induced_edge_id": induced_edge_id,
                "left_basis_id": left,
                "right_basis_id": right,
                "source0_boundary_count": int(row[EDGE_COLUMNS.index("source0_boundary_count")]),
                "source1_boundary_count": int(row[EDGE_COLUMNS.index("source1_boundary_count")]),
                "boundary_count": int(row[EDGE_COLUMNS.index("boundary_count")]),
                "left_support_occurrence_count": int(all_owner_support[left]),
                "right_support_occurrence_count": int(all_owner_support[right]),
            }
        )
    distances = pairwise_distances(adjacency, active_owners)
    components = induced_components(adjacency, active_owners)
    weak_owner_counts = Counter(row["weak_class_code"] for row in owner_rows)
    weak_support_occurrences = Counter()
    weak_mult_occurrences = Counter()
    for row in owner_rows:
        weak_code = row["weak_class_code"]
        weak_support_occurrences[weak_code] += row["support_occurrence_count"]
        weak_mult_occurrences[weak_code] += row["mult_occurrence_count"]
    support_population = int(sum(all_owner_support.values()))
    mult_population = int(sum(all_owner_mult.values()))
    support_var_num_sum = int(
        sum(count * (support_population - count) for count in all_owner_support.values())
    )
    mult_var_num_sum = int(
        sum(count * (mult_population - count) for count in all_owner_mult.values())
    )
    obs = {
        "line_point_count": int(owner_grid.shape[0]),
        "gate_count": len(BEST_IDS),
        "parenthesization_count": PARENTHESIZATION_COUNT,
        "parent_row_count": len(parent_rows),
        "gate_support_total": sum(row["support_total"] for row in gate_rows),
        "gate_mult_total": sum(row["mult_total"] for row in gate_rows),
        "support_occurrence_total": support_population,
        "mult_occurrence_total": mult_population,
        "active_owner_count": len(active_owners),
        "owner_support_occurrence_min": min(all_owner_support.values()),
        "owner_support_occurrence_max": max(all_owner_support.values()),
        "owner_mult_occurrence_min": min(all_owner_mult.values()),
        "owner_mult_occurrence_max": max(all_owner_mult.values()),
        "slack_min": min(row["slack_min"] for row in parent_rows),
        "slack_max": max(row["slack_max"] for row in parent_rows),
        "slack_sum": sum(row["slack_sum"] for row in parent_rows),
        "owner_weak_class_count": len(weak_owner_counts),
        "weak11_owner_count": int(weak_owner_counts[11]),
        "weak12_owner_count": int(weak_owner_counts[12]),
        "weak11_support_occurrence": int(weak_support_occurrences[11]),
        "weak12_support_occurrence": int(weak_support_occurrences[12]),
        "weak11_mult_occurrence": int(weak_mult_occurrences[11]),
        "weak12_mult_occurrence": int(weak_mult_occurrences[12]),
        "owner_induced_edge_count": len(edge_rows),
        "owner_induced_boundary_count": sum(row["boundary_count"] for row in edge_rows),
        "owner_induced_source0_boundary_count": sum(
            row["source0_boundary_count"] for row in edge_rows
        ),
        "owner_induced_source1_boundary_count": sum(
            row["source1_boundary_count"] for row in edge_rows
        ),
        "owner_pair_count": len(distances),
        "owner_distance_min": min(distances),
        "owner_distance_max": max(distances),
        "owner_distance_sum": sum(distances),
        "owner_cell_mass": sum(row["owner_cell_count"] for row in owner_rows),
        "owner_cell_min": min(row["owner_cell_count"] for row in owner_rows),
        "owner_cell_max": max(row["owner_cell_count"] for row in owner_rows),
        "induced_component_count": len(components),
        "induced_component_max_size": max(len(component) for component in components),
        "long_component_count": len({row["component_id"] for row in owner_rows}),
        "support_projection_flag": int(
            all(row["support_occurrence_count"] == 3 * row["support_count"] for row in parent_rows)
        ),
        "mult_projection_flag": int(
            all(row["mult_occurrence_count"] == 3 * row["mult_count"] for row in parent_rows)
        ),
        "p5_expected_counts_match": int(
            all(row["support_match_flag"] == 1 and row["mult_match_flag"] == 1 for row in parent_rows)
        ),
        "eta6_core_input_certified": int(
            eta6_core.get("status") == "ETA6_CORE_CERTIFIED"
            and eta6_core.get("all_checks_pass") is True
        ),
        "eta6_p21_input_certified": int(
            eta6_p21.get("status") == "ETA6_P21_CERTIFIED"
            and eta6_p21.get("all_checks_pass") is True
        ),
        "long_eta_input_certified": int(
            long_eta.get("status") == "LONG_ETA_CERTIFIED"
            and long_eta.get("all_checks_pass") is True
        ),
        "long_rec_input_certified": int(
            long_rec.get("status") == "LONG_REC_CERTIFIED"
            and long_rec.get("all_checks_pass") is True
        ),
    }
    obs_rows = [
        {"observable_id": code, "observable_code": code, "value": int(obs[name])}
        for name, code in sorted(OBS_CODES.items(), key=lambda item: item[1])
    ]
    return {
        "eta6_core": eta6_core,
        "eta6_p21": eta6_p21,
        "long_eta": long_eta,
        "long_rec": long_rec,
        "parent_rows": parent_rows,
        "gate_rows": gate_rows,
        "owner_rows": owner_rows,
        "edge_rows": edge_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "active_owner_ids": np.asarray(active_owners, dtype=np.int16),
        "finite_lln": {
            "support_owner_population": support_population,
            "support_owner_var_den": support_population * support_population,
            "support_owner_var_num_sum": support_var_num_sum,
            "mult_owner_population": mult_population,
            "mult_owner_var_den": mult_population * mult_population,
            "mult_owner_var_num_sum": mult_var_num_sum,
        },
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    parent_table = table_from_rows(PARENT_COLUMNS, rows["parent_rows"])
    gate_table = table_from_rows(GATE_COLUMNS, rows["gate_rows"])
    owner_table = table_from_rows(OWNER_COLUMNS_OUT, rows["owner_rows"])
    edge_table = table_from_rows(INDUCED_EDGE_COLUMNS, rows["edge_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    checks = {
        "inputs_certified": (
            obs["eta6_core_input_certified"],
            obs["eta6_p21_input_certified"],
            obs["long_eta_input_certified"],
            obs["long_rec_input_certified"],
        )
        == (1, 1, 1, 1),
        "gate_and_parenthesization_counts": (
            obs["gate_count"],
            obs["parenthesization_count"],
            obs["parent_row_count"],
        )
        == (6, 5, 30),
        "p5_expected_counts_match": obs["p5_expected_counts_match"] == 1,
        "owner_occurrence_projection_exact": (
            obs["gate_support_total"],
            obs["gate_mult_total"],
            obs["support_occurrence_total"],
            obs["mult_occurrence_total"],
            obs["support_projection_flag"],
            obs["mult_projection_flag"],
        )
        == (5_420_393_088, 29_385_031_680, 16_261_179_264, 88_155_095_040, 1, 1),
        "owner_fingerprint_exact": (
            obs["active_owner_count"],
            obs["owner_support_occurrence_min"],
            obs["owner_support_occurrence_max"],
            obs["owner_mult_occurrence_min"],
            obs["owner_mult_occurrence_max"],
            obs["owner_cell_mass"],
            obs["owner_cell_min"],
            obs["owner_cell_max"],
        )
        == (51, 2352, 4_271_578_880, 110_592, 15_373_172_736, 749_239, 1, 197_910),
        "slack_fingerprint_exact": (
            obs["slack_min"],
            obs["slack_max"],
            obs["slack_sum"],
        )
        == (0, 239, 1_387_594_500_520),
        "weak_fingerprint_exact": (
            obs["owner_weak_class_count"],
            obs["weak11_owner_count"],
            obs["weak12_owner_count"],
            obs["weak11_support_occurrence"],
            obs["weak12_support_occurrence"],
            obs["weak11_mult_occurrence"],
            obs["weak12_mult_occurrence"],
        )
        == (
            2,
            50,
            1,
            13_114_415_232,
            3_146_764_032,
            74_773_168_128,
            13_381_926_912,
        ),
        "transition_fingerprint_exact": (
            obs["owner_induced_edge_count"],
            obs["owner_induced_boundary_count"],
            obs["owner_induced_source0_boundary_count"],
            obs["owner_induced_source1_boundary_count"],
            obs["owner_pair_count"],
            obs["owner_distance_min"],
            obs["owner_distance_max"],
            obs["owner_distance_sum"],
            obs["induced_component_count"],
            obs["induced_component_max_size"],
            obs["long_component_count"],
        )
        == (91, 5629, 4938, 691, 1275, 1, 11, 6674, 3, 33, 1),
        "finite_lln_bigints_exact": rows["finite_lln"]
        == {
            "support_owner_population": 16_261_179_264,
            "support_owner_var_den": 264_425_951_055_943_581_696,
            "support_owner_var_num_sum": 226_219_720_156_830_131_200,
            "mult_owner_population": 88_155_095_040,
            "mult_owner_var_den": 7_771_320_781_511_432_601_600,
            "mult_owner_var_num_sum": 6_851_211_013_076_451_065_856,
        },
        "table_shapes_match": (
            tuple(parent_table.shape),
            tuple(gate_table.shape),
            tuple(owner_table.shape),
            tuple(edge_table.shape),
            tuple(obs_table.shape),
            tuple(rows["active_owner_ids"].shape),
        )
        == (
            (30, len(PARENT_COLUMNS)),
            (6, len(GATE_COLUMNS)),
            (51, len(OWNER_COLUMNS_OUT)),
            (91, len(INDUCED_EDGE_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
            (51,),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "eta6_gate_full_fiber_projection_to_long_rec",
        "fiber_scope": {
            "kind": "full_p21_gate_support_fibers",
            "rule": (
                "for each p21 gate p5 row and each pentagon parenthesization, "
                "aggregate every binary tensor lookup cell in every support path "
                "and project that source pair to its long_rec owner"
            ),
            "support_occurrence_rule": "each 5-label support path has exactly three binary lookup cells",
        },
        "gate": {
            "p5_ids": list(BEST_IDS),
            "gate_count": obs["gate_count"],
            "parenthesization_count": obs["parenthesization_count"],
            "parent_row_count": obs["parent_row_count"],
            "support_total": obs["gate_support_total"],
            "mult_total": obs["gate_mult_total"],
        },
        "projection": {
            "support_occurrence_total": obs["support_occurrence_total"],
            "mult_occurrence_total": obs["mult_occurrence_total"],
            "active_owner_count": obs["active_owner_count"],
            "support_occurrence_range": [
                obs["owner_support_occurrence_min"],
                obs["owner_support_occurrence_max"],
            ],
            "mult_occurrence_range": [
                obs["owner_mult_occurrence_min"],
                obs["owner_mult_occurrence_max"],
            ],
            "slack_range": [obs["slack_min"], obs["slack_max"]],
            "slack_sum": obs["slack_sum"],
            "parent_table_sha256": sha_array(parent_table),
            "gate_table_sha256": sha_array(gate_table),
            "owner_table_sha256": sha_array(owner_table),
        },
        "weak_projection": {
            "owner_weak_class_count": obs["owner_weak_class_count"],
            "weak11_owner_count": obs["weak11_owner_count"],
            "weak12_owner_count": obs["weak12_owner_count"],
            "weak11_support_occurrence": obs["weak11_support_occurrence"],
            "weak12_support_occurrence": obs["weak12_support_occurrence"],
            "weak11_mult_occurrence": obs["weak11_mult_occurrence"],
            "weak12_mult_occurrence": obs["weak12_mult_occurrence"],
        },
        "transition": {
            "induced_edge_count": obs["owner_induced_edge_count"],
            "induced_boundary_count": obs["owner_induced_boundary_count"],
            "owner_pair_count": obs["owner_pair_count"],
            "owner_distance_range": [obs["owner_distance_min"], obs["owner_distance_max"]],
            "owner_distance_sum": obs["owner_distance_sum"],
            "induced_component_count": obs["induced_component_count"],
            "induced_component_max_size": obs["induced_component_max_size"],
            "long_component_count": obs["long_component_count"],
            "edge_table_sha256": sha_array(edge_table),
            "active_owner_ids_sha256": sha_array(rows["active_owner_ids"]),
        },
        "finite_lln": {
            **rows["finite_lln"],
            "support_owner_event_rule": "for owner occurrence count m in population N, Var(mean_k)=m*(N-m)/(N^2*k)",
            "mult_owner_event_rule": "same formula on the multiplicity-weighted owner occurrence population",
        },
        "observable_table_sha256": sha_array(obs_table),
    }
    eta2 = {
        "schema": "long.eta2@1",
        "object": "eta6_gate_full_fiber_projection_to_long_rec",
        "status": STATUS if all(checks.values()) else "LONG_ETA2_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.eta2.report@1",
        "status": eta2["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_eta2 expands long_eta from sampled F-addresses to the full p21 "
            "gate support fibers: all five parenthesizations for all six gate rows "
            "are aggregated into exact support and multiplicity owner-occurrence "
            "measures on long_rec."
        ),
        "stage_protocol": {
            "draft": "reuse eta6_core, eta6_p21, long_eta, long_rec, and raw C985 fusion tensors",
            "witness": "aggregate every binary lookup cell in all p21 gate support fibers",
            "coherence": "match p5 support/multiplicity counts and owner occurrence totals",
            "closure": "emit exact owner, weak-class, transition, and finite LLN fingerprints",
            "emit": "write long_eta2 artifacts and verifier hook",
        },
        "inputs": {
            "source_target": input_entry(SOURCE_TARGET),
            "fusion_tensor": input_entry(FUSION_TENSOR),
            "eta6_core_report": input_entry(
                ETA6_CORE_REPORT,
                {"status": rows["eta6_core"].get("status")},
            ),
            "eta6_p21_report": input_entry(
                ETA6_P21_REPORT,
                {"status": rows["eta6_p21"].get("status")},
            ),
            "eta6_p5_tables": input_entry(ETA6_P5_TABLES),
            "long_eta_report": input_entry(
                LONG_ETA_REPORT,
                {"status": rows["long_eta"].get("status")},
            ),
            "long_rec_report": input_entry(
                LONG_REC_REPORT,
                {"status": rows["long_rec"].get("status")},
            ),
            "long_rec_tables": input_entry(LONG_REC_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "eta2": relpath(OUT_DIR / "eta2.json"),
            "parent_csv": relpath(OUT_DIR / "parent.csv"),
            "gate_csv": relpath(OUT_DIR / "gate.csv"),
            "owner_csv": relpath(OUT_DIR / "owner.csv"),
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
                "all p21 gate support fibers match their p5 support and multiplicity counts",
                "every binary lookup cell in those support fibers is projected to a long_rec owner",
                "exact support and multiplicity owner-occurrence LLN populations",
                "the owner/weak/transition fingerprints of the full p21 gate fiber projection",
            ],
            "does_not_certify_because_out_of_scope": [
                "seven-or-more p5 move searches",
                "post-surgery rebuilt-carrier semantics",
                "eta6 invariance under every possible long_rec transition",
                "a universal eta6 horizon theorem",
            ],
        },
        "next_highest_yield_item": (
            "Build long_lap: Laplacian/conductance invariants on the 51-owner "
            "long_eta2 induced subgraph and compare them with eta6_core margins."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.eta2.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.eta2.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "eta2": eta2,
        "parent_csv": csv_text(PARENT_COLUMNS, rows["parent_rows"]),
        "gate_csv": csv_text(GATE_COLUMNS, rows["gate_rows"]),
        "owner_csv": csv_text(OWNER_COLUMNS_OUT, rows["owner_rows"]),
        "edge_csv": csv_text(INDUCED_EDGE_COLUMNS, rows["edge_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "parent_table": parent_table,
        "gate_table": gate_table,
        "owner_table": owner_table,
        "edge_table": edge_table,
        "observable_table": obs_table,
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
    write_json(OUT_DIR / "eta2.json", payloads["eta2"])
    (OUT_DIR / "parent.csv").write_text(payloads["parent_csv"], encoding="utf-8")
    (OUT_DIR / "gate.csv").write_text(payloads["gate_csv"], encoding="utf-8")
    (OUT_DIR / "owner.csv").write_text(payloads["owner_csv"], encoding="utf-8")
    (OUT_DIR / "edge.csv").write_text(payloads["edge_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        parent_table=payloads["parent_table"],
        gate_table=payloads["gate_table"],
        owner_table=payloads["owner_table"],
        edge_table=payloads["edge_table"],
        observable_table=payloads["observable_table"],
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
