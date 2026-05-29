from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict, deque
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
    from .derive_long_cut import (
        OUT_DIR as LONG_CUT_DIR,
        STATUS as LONG_CUT_STATUS,
    )
    from .derive_long_lap import (
        COMPONENT_COLUMNS as LAP_COMPONENT_COLUMNS,
        NODE_COLUMNS as LAP_NODE_COLUMNS,
        OUT_DIR as LONG_LAP_DIR,
        STATUS as LONG_LAP_STATUS,
    )
    from .derive_long_rec import (
        EDGE_COLUMNS as REC_EDGE_COLUMNS,
        OUT_DIR as LONG_REC_DIR,
        OWNER_COLUMNS as REC_OWNER_COLUMNS,
        STATUS as LONG_REC_STATUS,
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
    from derive_long_cut import (
        OUT_DIR as LONG_CUT_DIR,
        STATUS as LONG_CUT_STATUS,
    )
    from derive_long_lap import (
        COMPONENT_COLUMNS as LAP_COMPONENT_COLUMNS,
        NODE_COLUMNS as LAP_NODE_COLUMNS,
        OUT_DIR as LONG_LAP_DIR,
        STATUS as LONG_LAP_STATUS,
    )
    from derive_long_rec import (
        EDGE_COLUMNS as REC_EDGE_COLUMNS,
        OUT_DIR as LONG_REC_DIR,
        OWNER_COLUMNS as REC_OWNER_COLUMNS,
        STATUS as LONG_REC_STATUS,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_flow"
STATUS = "LONG_FLOW_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

LONG_CUT_REPORT = LONG_CUT_DIR / "report.json"
LONG_LAP_REPORT = LONG_LAP_DIR / "report.json"
LONG_LAP_TABLES = LONG_LAP_DIR / "tables.npz"
LONG_REC_REPORT = LONG_REC_DIR / "report.json"
LONG_REC_TABLES = LONG_REC_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_flow.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_flow.py"

COMPONENT_COLUMNS = [
    "component_id",
    "active_owner_count",
    "crossing_edge_count",
    "inactive_owner_count",
    "boundary_count",
    "source0_boundary_count",
    "source1_boundary_count",
    "inactive_basis_min",
    "inactive_basis_max",
    "inactive_basis_sum",
    "inactive_basis_square_sum",
    "external_conductance_reduced_num",
    "external_conductance_reduced_den",
]
EDGE_COLUMNS = [
    "flow_edge_id",
    "component_id",
    "active_basis_id",
    "inactive_basis_id",
    "source0_boundary_count",
    "source1_boundary_count",
    "boundary_count",
]
OWNER_COLUMNS = [
    "inactive_basis_id",
    "weak_class_code",
    "component_mask",
    "component_count",
    "crossing_edge_count",
    "active_neighbor_count",
    "boundary_count",
    "source0_boundary_count",
    "source1_boundary_count",
    "component0_boundary_count",
    "component1_boundary_count",
    "component2_boundary_count",
    "owner_cell_count",
    "graph_degree",
    "weighted_degree",
    "residual_weighted_degree",
    "leakage_ratio_num",
    "leakage_ratio_den",
]
WEAK_COLUMNS = [
    "weak_class_code",
    "inactive_owner_count",
    "crossing_edge_count",
    "boundary_count",
    "source0_boundary_count",
    "source1_boundary_count",
    "inactive_basis_sum",
    "inactive_basis_square_sum",
    "component0_boundary_count",
    "component1_boundary_count",
    "component2_boundary_count",
]
SHELL_COLUMNS = [
    "shell_id",
    "owner_count",
    "basis_sum",
    "basis_square_sum",
    "within_edge_count",
    "within_boundary_count",
    "prev_edge_count",
    "prev_boundary_count",
    "next_edge_count",
    "next_boundary_count",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "line_point_count",
    "full_owner_count",
    "active_owner_count",
    "inactive_owner_count",
    "shell_count",
    "shell_max_distance",
    "shell1_owner_count",
    "flow_edge_count",
    "flow_boundary_count",
    "flow_source0_boundary_count",
    "flow_source1_boundary_count",
    "component_count",
    "component_external_positive_count",
    "inactive_flow_owner_count",
    "inactive_multi_component_owner_count",
    "inactive_multi_edge_owner_count",
    "inactive_flow_weight_min",
    "inactive_flow_weight_max",
    "inactive_flow_weight_square_sum",
    "inactive_flow_edge_count_min",
    "inactive_flow_edge_count_max",
    "inactive_active_neighbor_count_min",
    "inactive_active_neighbor_count_max",
    "weak_flow_class_count",
    "weak11_flow_owner_count",
    "weak12_flow_owner_count",
    "weak11_boundary_count",
    "weak12_boundary_count",
    "shell_owner_count_sum",
    "shell0_within_boundary_count",
    "shell1_prev_boundary_count",
    "shell7_owner_count",
    "shell7_next_boundary_count",
    "long_cut_input_certified",
    "long_lap_input_certified",
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


def reduce_ratio(num: int, den: int) -> tuple[int, int]:
    if den == 0:
        return 0, 0
    divisor = math.gcd(abs(num), abs(den))
    return num // divisor, den // divisor


def edge_flow_text(edge_rows: list[dict[str, int]]) -> str:
    return "".join(
        ",".join(
            str(row[column])
            for column in [
                "flow_edge_id",
                "component_id",
                "active_basis_id",
                "inactive_basis_id",
                "source0_boundary_count",
                "source1_boundary_count",
                "boundary_count",
            ]
        )
        + "\n"
        for row in edge_rows
    )


def owner_flow_text(owner_rows: list[dict[str, int]]) -> str:
    return "".join(
        ",".join(
            str(row[column])
            for column in [
                "inactive_basis_id",
                "component_mask",
                "component_count",
                "crossing_edge_count",
                "active_neighbor_count",
                "boundary_count",
                "source0_boundary_count",
                "source1_boundary_count",
                "component0_boundary_count",
                "component1_boundary_count",
                "component2_boundary_count",
            ]
        )
        + "\n"
        for row in owner_rows
    )


def build_shell_rows(
    owner_ids: list[int],
    active_owners: set[int],
    rec_edge_rows: list[dict[str, int]],
) -> tuple[list[dict[str, int]], dict[int, int]]:
    adjacency = {owner: set() for owner in owner_ids}
    for row in rec_edge_rows:
        left = int(row["left_basis_id"])
        right = int(row["right_basis_id"])
        adjacency[left].add(right)
        adjacency[right].add(left)

    distance: dict[int, int] = {owner: 0 for owner in active_owners}
    queue: deque[int] = deque(sorted(active_owners))
    while queue:
        node = queue.popleft()
        for nxt in sorted(adjacency[node]):
            if nxt in distance:
                continue
            distance[nxt] = distance[node] + 1
            queue.append(nxt)

    max_shell = max(distance.values())
    shell_rows: list[dict[str, int]] = []
    for shell_id in range(max_shell + 1):
        owners = sorted(owner for owner, shell in distance.items() if shell == shell_id)
        within_edge_count = 0
        within_boundary = 0
        prev_edge_count = 0
        prev_boundary = 0
        next_edge_count = 0
        next_boundary = 0
        for row in rec_edge_rows:
            left_shell = distance[int(row["left_basis_id"])]
            right_shell = distance[int(row["right_basis_id"])]
            boundary = int(row["boundary_count"])
            if left_shell == shell_id and right_shell == shell_id:
                within_edge_count += 1
                within_boundary += boundary
            elif {left_shell, right_shell} == {shell_id - 1, shell_id}:
                prev_edge_count += 1
                prev_boundary += boundary
            elif {left_shell, right_shell} == {shell_id, shell_id + 1}:
                next_edge_count += 1
                next_boundary += boundary
        shell_rows.append(
            {
                "shell_id": shell_id,
                "owner_count": len(owners),
                "basis_sum": sum(owners),
                "basis_square_sum": sum(owner * owner for owner in owners),
                "within_edge_count": within_edge_count,
                "within_boundary_count": within_boundary,
                "prev_edge_count": prev_edge_count,
                "prev_boundary_count": prev_boundary,
                "next_edge_count": next_edge_count,
                "next_boundary_count": next_boundary,
            }
        )
    return shell_rows, distance


def build_rows() -> dict[str, Any]:
    long_cut = load_json(LONG_CUT_REPORT)
    long_lap = load_json(LONG_LAP_REPORT)
    long_rec = load_json(LONG_REC_REPORT)
    lap_tables = np.load(LONG_LAP_TABLES, allow_pickle=False)
    rec_tables = np.load(LONG_REC_TABLES, allow_pickle=False)

    active_owners = [int(value) for value in np.asarray(lap_tables["active_owner_ids"])]
    active_set = set(active_owners)
    component_ids = [int(value) for value in np.asarray(lap_tables["component_ids"])]
    component_by_active = dict(zip(active_owners, component_ids))
    component_count = max(component_ids) + 1

    lap_node_rows = rows_from_table(np.asarray(lap_tables["node_table"]), LAP_NODE_COLUMNS)
    lap_component_rows = rows_from_table(
        np.asarray(lap_tables["component_table"]),
        [
            column
            for column in LAP_COMPONENT_COLUMNS
            if column != "tree_count_sha256"
        ],
    )
    rec_owner_rows = rows_from_table(
        np.asarray(rec_tables["owner_table"]),
        REC_OWNER_COLUMNS,
    )
    rec_edge_rows = rows_from_table(
        np.asarray(rec_tables["edge_table"]),
        REC_EDGE_COLUMNS,
    )
    owner_by_basis = {row["basis_id"]: row for row in rec_owner_rows}
    owner_ids = sorted(owner_by_basis)

    flow_edges_raw: list[dict[str, int]] = []
    owner_acc: dict[int, dict[str, Any]] = {}
    component_acc: dict[int, dict[str, Any]] = {
        component_id: {
            "component_id": component_id,
            "active_owner_count": 0,
            "crossing_edge_count": 0,
            "inactive_owners": set(),
            "boundary_count": 0,
            "source0_boundary_count": 0,
            "source1_boundary_count": 0,
        }
        for component_id in range(component_count)
    }
    for row in lap_node_rows:
        component_acc[int(row["component_id"])]["active_owner_count"] += 1

    for row in rec_edge_rows:
        left = int(row["left_basis_id"])
        right = int(row["right_basis_id"])
        left_active = left in active_set
        right_active = right in active_set
        if left_active == right_active:
            continue
        active = left if left_active else right
        inactive = right if left_active else left
        component_id = component_by_active[active]
        flow_edges_raw.append(
            {
                "component_id": component_id,
                "active_basis_id": active,
                "inactive_basis_id": inactive,
                "source0_boundary_count": int(row["source0_boundary_count"]),
                "source1_boundary_count": int(row["source1_boundary_count"]),
                "boundary_count": int(row["boundary_count"]),
            }
        )
        comp = component_acc[component_id]
        comp["crossing_edge_count"] += 1
        comp["inactive_owners"].add(inactive)
        comp["boundary_count"] += int(row["boundary_count"])
        comp["source0_boundary_count"] += int(row["source0_boundary_count"])
        comp["source1_boundary_count"] += int(row["source1_boundary_count"])

        if inactive not in owner_acc:
            owner_acc[inactive] = {
                "inactive_basis_id": inactive,
                "component_weights": [0 for _ in range(component_count)],
                "components": set(),
                "active_neighbors": set(),
                "crossing_edge_count": 0,
                "boundary_count": 0,
                "source0_boundary_count": 0,
                "source1_boundary_count": 0,
            }
        acc = owner_acc[inactive]
        acc["component_weights"][component_id] += int(row["boundary_count"])
        acc["components"].add(component_id)
        acc["active_neighbors"].add(active)
        acc["crossing_edge_count"] += 1
        acc["boundary_count"] += int(row["boundary_count"])
        acc["source0_boundary_count"] += int(row["source0_boundary_count"])
        acc["source1_boundary_count"] += int(row["source1_boundary_count"])

    flow_edge_rows: list[dict[str, int]] = []
    for flow_edge_id, row in enumerate(
        sorted(
            flow_edges_raw,
            key=lambda item: (
                item["component_id"],
                item["active_basis_id"],
                item["inactive_basis_id"],
            ),
        )
    ):
        flow_edge_rows.append({"flow_edge_id": flow_edge_id, **row})

    component_rows: list[dict[str, int]] = []
    lap_component_by_id = {
        row["component_id"]: row for row in lap_component_rows
    }
    for component_id in range(component_count):
        acc = component_acc[component_id]
        inactive_owners = sorted(acc["inactive_owners"])
        lap_component = lap_component_by_id[component_id]
        component_rows.append(
            {
                "component_id": component_id,
                "active_owner_count": int(acc["active_owner_count"]),
                "crossing_edge_count": int(acc["crossing_edge_count"]),
                "inactive_owner_count": len(inactive_owners),
                "boundary_count": int(acc["boundary_count"]),
                "source0_boundary_count": int(acc["source0_boundary_count"]),
                "source1_boundary_count": int(acc["source1_boundary_count"]),
                "inactive_basis_min": min(inactive_owners) if inactive_owners else -1,
                "inactive_basis_max": max(inactive_owners) if inactive_owners else -1,
                "inactive_basis_sum": sum(inactive_owners),
                "inactive_basis_square_sum": sum(
                    owner * owner for owner in inactive_owners
                ),
                "external_conductance_reduced_num": int(
                    lap_component["external_conductance_reduced_num"]
                ),
                "external_conductance_reduced_den": int(
                    lap_component["external_conductance_reduced_den"]
                ),
            }
        )

    owner_rows: list[dict[str, int]] = []
    for inactive in sorted(owner_acc):
        acc = owner_acc[inactive]
        owner = owner_by_basis[inactive]
        boundary = int(acc["boundary_count"])
        weighted_degree = int(owner["weighted_degree"])
        ratio_num, ratio_den = reduce_ratio(boundary, weighted_degree)
        component_mask = sum(1 << component for component in acc["components"])
        component_weights = list(acc["component_weights"])
        owner_rows.append(
            {
                "inactive_basis_id": inactive,
                "weak_class_code": int(owner["weak_class_code"]),
                "component_mask": component_mask,
                "component_count": len(acc["components"]),
                "crossing_edge_count": int(acc["crossing_edge_count"]),
                "active_neighbor_count": len(acc["active_neighbors"]),
                "boundary_count": boundary,
                "source0_boundary_count": int(acc["source0_boundary_count"]),
                "source1_boundary_count": int(acc["source1_boundary_count"]),
                "component0_boundary_count": component_weights[0],
                "component1_boundary_count": component_weights[1],
                "component2_boundary_count": component_weights[2],
                "owner_cell_count": int(owner["owner_cell_count"]),
                "graph_degree": int(owner["graph_degree"]),
                "weighted_degree": weighted_degree,
                "residual_weighted_degree": weighted_degree - boundary,
                "leakage_ratio_num": ratio_num,
                "leakage_ratio_den": ratio_den,
            }
        )

    weak_acc: dict[int, dict[str, int]] = defaultdict(
        lambda: {
            "inactive_owner_count": 0,
            "crossing_edge_count": 0,
            "boundary_count": 0,
            "source0_boundary_count": 0,
            "source1_boundary_count": 0,
            "inactive_basis_sum": 0,
            "inactive_basis_square_sum": 0,
            "component0_boundary_count": 0,
            "component1_boundary_count": 0,
            "component2_boundary_count": 0,
        }
    )
    for row in owner_rows:
        acc = weak_acc[row["weak_class_code"]]
        acc["inactive_owner_count"] += 1
        acc["crossing_edge_count"] += row["crossing_edge_count"]
        acc["boundary_count"] += row["boundary_count"]
        acc["source0_boundary_count"] += row["source0_boundary_count"]
        acc["source1_boundary_count"] += row["source1_boundary_count"]
        acc["inactive_basis_sum"] += row["inactive_basis_id"]
        acc["inactive_basis_square_sum"] += (
            row["inactive_basis_id"] * row["inactive_basis_id"]
        )
        acc["component0_boundary_count"] += row["component0_boundary_count"]
        acc["component1_boundary_count"] += row["component1_boundary_count"]
        acc["component2_boundary_count"] += row["component2_boundary_count"]
    weak_rows = [
        {"weak_class_code": weak_class_code, **dict(acc)}
        for weak_class_code, acc in sorted(weak_acc.items())
    ]

    shell_rows, shell_distance = build_shell_rows(owner_ids, active_set, rec_edge_rows)
    inactive_rows = [row for row in owner_rows if row["inactive_basis_id"] not in active_set]
    obs = {
        "line_point_count": 985,
        "full_owner_count": len(owner_ids),
        "active_owner_count": len(active_owners),
        "inactive_owner_count": len(owner_ids) - len(active_owners),
        "shell_count": len(shell_rows),
        "shell_max_distance": max(shell_distance.values()),
        "shell1_owner_count": next(
            row["owner_count"] for row in shell_rows if row["shell_id"] == 1
        ),
        "flow_edge_count": len(flow_edge_rows),
        "flow_boundary_count": sum(row["boundary_count"] for row in flow_edge_rows),
        "flow_source0_boundary_count": sum(
            row["source0_boundary_count"] for row in flow_edge_rows
        ),
        "flow_source1_boundary_count": sum(
            row["source1_boundary_count"] for row in flow_edge_rows
        ),
        "component_count": component_count,
        "component_external_positive_count": sum(
            1 for row in component_rows if row["boundary_count"] > 0
        ),
        "inactive_flow_owner_count": len(inactive_rows),
        "inactive_multi_component_owner_count": sum(
            1 for row in inactive_rows if row["component_count"] > 1
        ),
        "inactive_multi_edge_owner_count": sum(
            1 for row in inactive_rows if row["crossing_edge_count"] > 1
        ),
        "inactive_flow_weight_min": min(row["boundary_count"] for row in inactive_rows),
        "inactive_flow_weight_max": max(row["boundary_count"] for row in inactive_rows),
        "inactive_flow_weight_square_sum": sum(
            row["boundary_count"] * row["boundary_count"] for row in inactive_rows
        ),
        "inactive_flow_edge_count_min": min(
            row["crossing_edge_count"] for row in inactive_rows
        ),
        "inactive_flow_edge_count_max": max(
            row["crossing_edge_count"] for row in inactive_rows
        ),
        "inactive_active_neighbor_count_min": min(
            row["active_neighbor_count"] for row in inactive_rows
        ),
        "inactive_active_neighbor_count_max": max(
            row["active_neighbor_count"] for row in inactive_rows
        ),
        "weak_flow_class_count": len(weak_rows),
        "weak11_flow_owner_count": next(
            row["inactive_owner_count"]
            for row in weak_rows
            if row["weak_class_code"] == 11
        ),
        "weak12_flow_owner_count": next(
            row["inactive_owner_count"]
            for row in weak_rows
            if row["weak_class_code"] == 12
        ),
        "weak11_boundary_count": next(
            row["boundary_count"] for row in weak_rows if row["weak_class_code"] == 11
        ),
        "weak12_boundary_count": next(
            row["boundary_count"] for row in weak_rows if row["weak_class_code"] == 12
        ),
        "shell_owner_count_sum": sum(row["owner_count"] for row in shell_rows),
        "shell0_within_boundary_count": next(
            row["within_boundary_count"]
            for row in shell_rows
            if row["shell_id"] == 0
        ),
        "shell1_prev_boundary_count": next(
            row["prev_boundary_count"] for row in shell_rows if row["shell_id"] == 1
        ),
        "shell7_owner_count": next(
            row["owner_count"] for row in shell_rows if row["shell_id"] == 7
        ),
        "shell7_next_boundary_count": next(
            row["next_boundary_count"] for row in shell_rows if row["shell_id"] == 7
        ),
        "long_cut_input_certified": int(long_cut.get("status") == LONG_CUT_STATUS),
        "long_lap_input_certified": int(long_lap.get("status") == LONG_LAP_STATUS),
        "long_rec_input_certified": int(long_rec.get("status") == LONG_REC_STATUS),
    }
    obs_rows = [
        {"observable_id": code, "observable_code": code, "value": int(obs[name])}
        for name, code in sorted(OBS_CODES.items(), key=lambda item: item[1])
    ]
    return {
        "long_cut": long_cut,
        "long_lap": long_lap,
        "long_rec": long_rec,
        "component_rows": component_rows,
        "flow_edge_rows": flow_edge_rows,
        "owner_rows": owner_rows,
        "weak_rows": weak_rows,
        "shell_rows": shell_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    component_table = table_from_rows(COMPONENT_COLUMNS, rows["component_rows"])
    edge_table = table_from_rows(EDGE_COLUMNS, rows["flow_edge_rows"])
    owner_table = table_from_rows(OWNER_COLUMNS, rows["owner_rows"])
    weak_table = table_from_rows(WEAK_COLUMNS, rows["weak_rows"])
    shell_table = table_from_rows(SHELL_COLUMNS, rows["shell_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    edge_text_sha256 = hashlib.sha256(
        edge_flow_text(rows["flow_edge_rows"]).encode("ascii")
    ).hexdigest()
    owner_text_sha256 = hashlib.sha256(
        owner_flow_text(rows["owner_rows"]).encode("ascii")
    ).hexdigest()
    component_signature = [
        tuple(row[column] for column in COMPONENT_COLUMNS)
        for row in rows["component_rows"]
    ]
    weak_signature = [
        tuple(row[column] for column in WEAK_COLUMNS)
        for row in rows["weak_rows"]
    ]
    shell_signature = [
        tuple(row[column] for column in SHELL_COLUMNS)
        for row in rows["shell_rows"]
    ]
    checks = {
        "inputs_certified": (
            obs["long_cut_input_certified"],
            obs["long_lap_input_certified"],
            obs["long_rec_input_certified"],
        )
        == (1, 1, 1),
        "ambient_flow_fingerprint_exact": (
            obs["flow_edge_count"],
            obs["flow_boundary_count"],
            obs["flow_source0_boundary_count"],
            obs["flow_source1_boundary_count"],
        )
        == (76, 4_584, 2_407, 2_177),
        "component_fingerprint_exact": component_signature
        == [
            (0, 33, 47, 29, 1_342, 128, 1_214, 0, 155, 1_898, 177_232, 671, 1_512),
            (1, 1, 4, 4, 864, 733, 131, 4, 11, 34, 318, 1, 1),
            (2, 17, 25, 21, 2_378, 1_546, 832, 25, 212, 2_666, 397_160, 1_189, 5_977),
        ],
        "inactive_owner_fingerprint_exact": (
            obs["inactive_flow_owner_count"],
            obs["inactive_multi_component_owner_count"],
            obs["inactive_multi_edge_owner_count"],
            obs["inactive_flow_weight_min"],
            obs["inactive_flow_weight_max"],
            obs["inactive_flow_weight_square_sum"],
            obs["inactive_flow_edge_count_min"],
            obs["inactive_flow_edge_count_max"],
            obs["inactive_active_neighbor_count_min"],
            obs["inactive_active_neighbor_count_max"],
        )
        == (52, 2, 18, 1, 732, 2_031_134, 1, 5, 1, 5),
        "weak_flow_fingerprint_exact": weak_signature
        == [
            (11, 48, 69, 3_541, 1_634, 1_907, 3_736, 409_690, 1_342, 864, 1_335),
            (12, 4, 7, 1_043, 773, 270, 805, 162_195, 0, 0, 1_043),
        ],
        "shell_fingerprint_exact": shell_signature
        == [
            (0, 51, 4_512, 564_022, 91, 5_629, 0, 0, 76, 4_584),
            (1, 52, 4_541, 571_885, 59, 3_144, 76, 4_584, 113, 2_321),
            (2, 72, 8_117, 1_205_487, 78, 499, 113, 2_321, 85, 647),
            (3, 49, 8_162, 1_534_462, 45, 218, 85, 647, 32, 531),
            (4, 17, 3_757, 838_051, 16, 103, 32, 531, 17, 144),
            (5, 10, 2_398, 578_406, 9, 27, 17, 144, 11, 155),
            (6, 6, 1_413, 334_955, 5, 85, 11, 155, 4, 28),
            (7, 2, 511, 130_561, 1, 2, 4, 28, 0, 0),
        ],
        "edge_text_sha256_exact": edge_text_sha256
        == "9979cce507e5efc3632e5036288311fadd054cfe4e9d2e236a95ad97b7122af2",
        "owner_text_sha256_exact": owner_text_sha256
        == "b205bd84e62696bda5b97dea8b2496a35f05471327824225c1ed6e8637bb5a05",
        "table_shapes_match": (
            tuple(component_table.shape),
            tuple(edge_table.shape),
            tuple(owner_table.shape),
            tuple(weak_table.shape),
            tuple(shell_table.shape),
            tuple(obs_table.shape),
        )
        == (
            (3, len(COMPONENT_COLUMNS)),
            (76, len(EDGE_COLUMNS)),
            (52, len(OWNER_COLUMNS)),
            (2, len(WEAK_COLUMNS)),
            (8, len(SHELL_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    top_owners = [
        {
            key: row[key]
            for key in [
                "inactive_basis_id",
                "weak_class_code",
                "component_mask",
                "boundary_count",
                "source0_boundary_count",
                "source1_boundary_count",
                "crossing_edge_count",
                "active_neighbor_count",
            ]
        }
        for row in sorted(
            rows["owner_rows"],
            key=lambda item: (-item["boundary_count"], item["inactive_basis_id"]),
        )[:10]
    ]
    witness = {
        "name": THEOREM_ID,
        "classification": "long_rec_ambient_leakage_shell_flow",
        "scope": {
            "source": "long_lap active owner components",
            "ambient": "long_rec owner transition graph",
            "rule": "crossing edges are long_rec edges with exactly one active endpoint",
        },
        "ambient_flow": {
            "crossing_edge_count": obs["flow_edge_count"],
            "boundary_count": obs["flow_boundary_count"],
            "source0_boundary_count": obs["flow_source0_boundary_count"],
            "source1_boundary_count": obs["flow_source1_boundary_count"],
            "edge_text_sha256": edge_text_sha256,
            "edge_table_sha256": sha_array(edge_table),
        },
        "component_flow": {
            "component_rows": rows["component_rows"],
            "component_table_sha256": sha_array(component_table),
        },
        "inactive_owner_flow": {
            "owner_count": obs["inactive_flow_owner_count"],
            "multi_component_owner_count": obs[
                "inactive_multi_component_owner_count"
            ],
            "multi_edge_owner_count": obs["inactive_multi_edge_owner_count"],
            "weight_range": [
                obs["inactive_flow_weight_min"],
                obs["inactive_flow_weight_max"],
            ],
            "weight_square_sum": obs["inactive_flow_weight_square_sum"],
            "owner_text_sha256": owner_text_sha256,
            "owner_table_sha256": sha_array(owner_table),
            "top_leakage_owners": top_owners,
        },
        "weak_flow": {
            "weak_rows": rows["weak_rows"],
            "weak_table_sha256": sha_array(weak_table),
        },
        "shell_flow": {
            "shell_rows": rows["shell_rows"],
            "shell_table_sha256": sha_array(shell_table),
        },
        "observable_table_sha256": sha_array(obs_table),
    }
    flow = {
        "schema": "long.flow@1",
        "object": "long_rec_ambient_leakage_shell_flow",
        "status": STATUS if all(checks.values()) else "LONG_FLOW_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.flow.report@1",
        "status": flow["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_flow certifies the exact first ambient leakage layer from the "
            "long_lap active eta6 owner components into the full long_rec graph: "
            "76 crossing edges, boundary weight 4584, 52 shell-1 inactive owners, "
            "two weak classes, and an eight-shell ambient distance profile."
        ),
        "stage_protocol": {
            "draft": "take long_cut/long_lap as the active eta6 component boundary",
            "witness": "scan long_rec edges for active-to-inactive crossings and BFS shells",
            "coherence": "check component, owner, weak-class, shell, and text-hash fingerprints",
            "closure": "emit flow, component, edge, owner, weak, shell, table, certificate, manifest, and report artifacts",
            "emit": "write long_flow artifacts and verifier hook",
        },
        "inputs": {
            "long_cut_report": input_entry(
                LONG_CUT_REPORT,
                {"status": rows["long_cut"].get("status")},
            ),
            "long_lap_report": input_entry(
                LONG_LAP_REPORT,
                {"status": rows["long_lap"].get("status")},
            ),
            "long_lap_tables": input_entry(LONG_LAP_TABLES),
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
            "flow": relpath(OUT_DIR / "flow.json"),
            "component_csv": relpath(OUT_DIR / "component.csv"),
            "edge_csv": relpath(OUT_DIR / "edge.csv"),
            "owner_csv": relpath(OUT_DIR / "owner.csv"),
            "weak_csv": relpath(OUT_DIR / "weak.csv"),
            "shell_csv": relpath(OUT_DIR / "shell.csv"),
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
                "the exact active-to-inactive leakage edge set in long_rec",
                "which shell-1 inactive owners receive active eta6 boundary weight",
                "the weak-class split of the leakage layer",
                "the full unweighted ambient shell profile out to distance seven",
            ],
            "does_not_certify_because_out_of_scope": [
                "harmonic absorption beyond the first inactive shell",
                "support-changing recouplings outside the long_rec owner graph",
                "a universal eta6 horizon theorem",
                "metric completion of the inactive ambient shell graph",
            ],
        },
        "next_highest_yield_item": (
            "Build long_absorb: solve exact absorbing/harmonic leakage through "
            "the inactive long_rec shell graph to measure how active boundary "
            "flow dissipates past shell 1."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.flow.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.flow.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "flow": flow,
        "component_csv": csv_text(COMPONENT_COLUMNS, rows["component_rows"]),
        "edge_csv": csv_text(EDGE_COLUMNS, rows["flow_edge_rows"]),
        "owner_csv": csv_text(OWNER_COLUMNS, rows["owner_rows"]),
        "weak_csv": csv_text(WEAK_COLUMNS, rows["weak_rows"]),
        "shell_csv": csv_text(SHELL_COLUMNS, rows["shell_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "component_table": component_table,
        "edge_table": edge_table,
        "owner_table": owner_table,
        "weak_table": weak_table,
        "shell_table": shell_table,
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
    write_json(OUT_DIR / "flow.json", payloads["flow"])
    (OUT_DIR / "component.csv").write_text(
        payloads["component_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "edge.csv").write_text(payloads["edge_csv"], encoding="utf-8")
    (OUT_DIR / "owner.csv").write_text(payloads["owner_csv"], encoding="utf-8")
    (OUT_DIR / "weak.csv").write_text(payloads["weak_csv"], encoding="utf-8")
    (OUT_DIR / "shell.csv").write_text(payloads["shell_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        component_table=payloads["component_table"],
        edge_table=payloads["edge_table"],
        owner_table=payloads["owner_table"],
        weak_table=payloads["weak_table"],
        shell_table=payloads["shell_table"],
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
