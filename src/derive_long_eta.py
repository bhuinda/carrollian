from __future__ import annotations

import json
from collections import Counter, deque
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
    from .derive_eta6_f4 import OUT_DIR as ETA6_F4_DIR, SAMPLE_COLUMNS
    from .derive_eta6_p5 import EXT_COLUMNS, OUT_DIR as ETA6_P5_DIR
    from .derive_eta6_p21 import BEST_IDS, GATE_COLUMNS, OUT_DIR as ETA6_P21_DIR
    from .derive_long_rec import EDGE_COLUMNS, OUT_DIR as LONG_REC_DIR, OWNER_COLUMNS
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
    from derive_eta6_f4 import OUT_DIR as ETA6_F4_DIR, SAMPLE_COLUMNS
    from derive_eta6_p5 import EXT_COLUMNS, OUT_DIR as ETA6_P5_DIR
    from derive_eta6_p21 import BEST_IDS, GATE_COLUMNS, OUT_DIR as ETA6_P21_DIR
    from derive_long_rec import EDGE_COLUMNS, OUT_DIR as LONG_REC_DIR, OWNER_COLUMNS
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_eta"
STATUS = "LONG_ETA_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
ETA6_CORE_REPORT = ETA6_CORE_DIR / "report.json"
ETA6_P21_REPORT = ETA6_P21_DIR / "report.json"
ETA6_P21_TABLES = ETA6_P21_DIR / "tables.npz"
ETA6_P5_TABLES = ETA6_P5_DIR / "tables.npz"
ETA6_F4_TABLES = ETA6_F4_DIR / "tables.npz"
LONG_REC_REPORT = LONG_REC_DIR / "report.json"
LONG_REC_TABLES = LONG_REC_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_eta.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_eta.py"

PAIR_ROLES = [
    ("left_inner", "left_alpha", "left_beta", "left_delta"),
    ("left_outer", "left_delta", "left_chi", "left_epsilon"),
    ("right_inner", "right_beta", "right_chi", "right_eta"),
    ("right_outer", "right_alpha", "right_eta", "right_epsilon"),
]
PAIR_ROLE_CODES = {name: code for code, (name, *_rest) in enumerate(PAIR_ROLES)}
BRIDGE_COLUMNS = [
    "bridge_id",
    "gate_id",
    "p5_id",
    "f4_row_id",
    "face_id",
    "label_mask",
    "pair_role_code",
    "source0_addr",
    "source1_addr",
    "sample_output_addr",
    "frontier_addr",
    "closure_slack",
    "owner_basis_id",
    "owner_target_addr",
    "owner_weak_class_code",
    "component_id",
    "output_in_closure_flag",
    "eta6_preserved_flag",
    "owner_cell_count",
    "graph_degree",
    "weighted_degree",
]
GATE_COLUMNS_OUT = [
    "gate_id",
    "p5_id",
    "f4_row_id",
    "face_id",
    "label_mask",
    "f4_delta",
    "support_spread",
    "eta6_preserved_flag",
    "projected_owner_count",
    "closure_pass_count",
    "span_min_distance",
    "span_max_distance",
    "span_distance_sum",
    "closure_slack_min",
    "closure_slack_max",
    "closure_slack_sum",
]
OWNER_BRIDGE_COLUMNS = [
    "owner_rank",
    "basis_id",
    "weak_class_code",
    "owner_cell_count",
    "graph_degree",
    "weighted_degree",
    "bridge_touch_count",
    "gate_touch_count",
    "component_id",
    "induced_degree",
]
INDUCED_EDGE_COLUMNS = [
    "induced_edge_id",
    "left_basis_id",
    "right_basis_id",
    "source0_boundary_count",
    "source1_boundary_count",
    "boundary_count",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "line_point_count",
    "gate_count",
    "gate_id_sum",
    "bridge_pair_cell_count",
    "bridge_pair_role_count",
    "p5_gate_ids_match",
    "eta6_preserved_gate_count",
    "bridge_output_closure_pass_count",
    "bridge_closure_slack_min",
    "bridge_closure_slack_max",
    "bridge_closure_slack_sum",
    "bridge_unique_owner_count",
    "bridge_owner_cell_mass",
    "bridge_owner_component_count",
    "bridge_owner_weak_class_count",
    "bridge_pair_weak11_count",
    "bridge_pair_weak12_count",
    "bridge_induced_edge_count",
    "bridge_induced_boundary_count",
    "bridge_induced_source0_boundary_count",
    "bridge_induced_source1_boundary_count",
    "bridge_unique_owner_pair_count",
    "bridge_unique_owner_distance_min",
    "bridge_unique_owner_distance_max",
    "bridge_unique_owner_distance_sum",
    "gate_span_distance_max",
    "gate_span_distance_sum",
    "f4_sample_row_count",
    "face_count",
    "label_mask_count",
    "sample_level_bridge_flag",
    "eta6_core_input_certified",
    "eta6_p21_input_certified",
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


def shortest_distance(adjacency: list[set[int]], start: int, stop: int) -> int:
    if start == stop:
        return 0
    seen = {start}
    queue: deque[tuple[int, int]] = deque([(start, 0)])
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


def build_rows() -> dict[str, Any]:
    eta6_core = load_json(ETA6_CORE_REPORT)
    eta6_p21 = load_json(ETA6_P21_REPORT)
    long_rec = load_json(LONG_REC_REPORT)
    p21_tables = np.load(ETA6_P21_TABLES, allow_pickle=False)
    p5_tables = np.load(ETA6_P5_TABLES, allow_pickle=False)
    f4_tables = np.load(ETA6_F4_TABLES, allow_pickle=False)
    rec_tables = np.load(LONG_REC_TABLES, allow_pickle=False)
    gate_rows = rows_from_table(np.asarray(p21_tables["gate_table"], dtype=np.int64), GATE_COLUMNS)
    p5_rows = rows_from_table(np.asarray(p5_tables["ext_table"], dtype=np.int64), EXT_COLUMNS)
    f4_sample_rows = rows_from_table(np.asarray(f4_tables["sample_table"], dtype=np.int64), SAMPLE_COLUMNS)
    owner_grid = np.asarray(rec_tables["owner_grid"], dtype=np.int16)
    owner_frontier = np.asarray(rec_tables["owner_frontier"], dtype=np.int16)
    owner_table = np.asarray(rec_tables["owner_table"], dtype=np.int64)
    edge_table = np.asarray(rec_tables["edge_table"], dtype=np.int64)
    component_ids = np.asarray(rec_tables["component_ids"], dtype=np.int16)
    owner_by_id = {int(row[0]): row for row in owner_table}
    p5_by_id = {row["p5_id"]: row for row in p5_rows}
    f4_by_row = {row["row_id"]: row for row in f4_sample_rows}
    adjacency = [set() for _ in range(int(owner_table.shape[0]))]
    edge_by_pair: dict[tuple[int, int], np.ndarray] = {}
    for row in edge_table:
        left = int(row[EDGE_COLUMNS.index("left_basis_id")])
        right = int(row[EDGE_COLUMNS.index("right_basis_id")])
        adjacency[left].add(right)
        adjacency[right].add(left)
        edge_by_pair[(left, right)] = row
        edge_by_pair[(right, left)] = row

    bridge_rows: list[dict[str, int]] = []
    gate_summary_rows: list[dict[str, int]] = []
    for gate in gate_rows:
        gate_id = gate["gate_id"]
        p5_id = gate["p5_id"]
        p5 = p5_by_id[p5_id]
        sample = f4_by_row[p5["f4_row_id"]]
        gate_owners: list[int] = []
        gate_slacks: list[int] = []
        closure_pass_count = 0
        for pair_role_code, (_role, left_name, right_name, output_name) in enumerate(PAIR_ROLES):
            source0 = sample[left_name]
            source1 = sample[right_name]
            output = sample[output_name]
            owner_id = int(owner_grid[source0, source1])
            frontier = int(owner_frontier[source0, source1])
            owner = owner_by_id[owner_id]
            slack = output - frontier
            pass_flag = int(slack >= 0)
            closure_pass_count += pass_flag
            gate_owners.append(owner_id)
            gate_slacks.append(slack)
            bridge_rows.append(
                {
                    "bridge_id": len(bridge_rows),
                    "gate_id": gate_id,
                    "p5_id": p5_id,
                    "f4_row_id": p5["f4_row_id"],
                    "face_id": gate["face_id"],
                    "label_mask": gate["label_mask"],
                    "pair_role_code": pair_role_code,
                    "source0_addr": source0,
                    "source1_addr": source1,
                    "sample_output_addr": output,
                    "frontier_addr": frontier,
                    "closure_slack": slack,
                    "owner_basis_id": owner_id,
                    "owner_target_addr": int(owner[OWNER_COLUMNS.index("target_addr")]),
                    "owner_weak_class_code": int(owner[OWNER_COLUMNS.index("weak_class_code")]),
                    "component_id": int(component_ids[owner_id]),
                    "output_in_closure_flag": pass_flag,
                    "eta6_preserved_flag": gate["eta6_preserved_flag"],
                    "owner_cell_count": int(owner[OWNER_COLUMNS.index("owner_cell_count")]),
                    "graph_degree": int(owner[OWNER_COLUMNS.index("graph_degree")]),
                    "weighted_degree": int(owner[OWNER_COLUMNS.index("weighted_degree")]),
                }
            )
        gate_distances = pairwise_distances(adjacency, gate_owners)
        gate_summary_rows.append(
            {
                "gate_id": gate_id,
                "p5_id": p5_id,
                "f4_row_id": p5["f4_row_id"],
                "face_id": gate["face_id"],
                "label_mask": gate["label_mask"],
                "f4_delta": gate["f4_delta"],
                "support_spread": gate["support_spread"],
                "eta6_preserved_flag": gate["eta6_preserved_flag"],
                "projected_owner_count": len(set(gate_owners)),
                "closure_pass_count": closure_pass_count,
                "span_min_distance": min(gate_distances),
                "span_max_distance": max(gate_distances),
                "span_distance_sum": sum(gate_distances),
                "closure_slack_min": min(gate_slacks),
                "closure_slack_max": max(gate_slacks),
                "closure_slack_sum": sum(gate_slacks),
            }
        )

    bridge_owner_ids = sorted({row["owner_basis_id"] for row in bridge_rows})
    bridge_owner_set = set(bridge_owner_ids)
    touch_counts = Counter(row["owner_basis_id"] for row in bridge_rows)
    gate_touch_counts: Counter[int] = Counter()
    for owner_id in bridge_owner_ids:
        gate_touch_counts[owner_id] = len(
            {row["gate_id"] for row in bridge_rows if row["owner_basis_id"] == owner_id}
        )
    induced_edges = []
    for row in edge_table:
        left = int(row[EDGE_COLUMNS.index("left_basis_id")])
        right = int(row[EDGE_COLUMNS.index("right_basis_id")])
        if left in bridge_owner_set and right in bridge_owner_set:
            induced_edges.append(row)
    induced_adjacency = {owner_id: 0 for owner_id in bridge_owner_ids}
    for row in induced_edges:
        induced_adjacency[int(row[EDGE_COLUMNS.index("left_basis_id")])] += 1
        induced_adjacency[int(row[EDGE_COLUMNS.index("right_basis_id")])] += 1
    owner_bridge_rows = []
    for owner_rank, owner_id in enumerate(bridge_owner_ids):
        owner = owner_by_id[owner_id]
        owner_bridge_rows.append(
            {
                "owner_rank": owner_rank,
                "basis_id": owner_id,
                "weak_class_code": int(owner[OWNER_COLUMNS.index("weak_class_code")]),
                "owner_cell_count": int(owner[OWNER_COLUMNS.index("owner_cell_count")]),
                "graph_degree": int(owner[OWNER_COLUMNS.index("graph_degree")]),
                "weighted_degree": int(owner[OWNER_COLUMNS.index("weighted_degree")]),
                "bridge_touch_count": int(touch_counts[owner_id]),
                "gate_touch_count": int(gate_touch_counts[owner_id]),
                "component_id": int(component_ids[owner_id]),
                "induced_degree": int(induced_adjacency[owner_id]),
            }
        )
    induced_edge_rows = []
    for induced_edge_id, row in enumerate(induced_edges):
        induced_edge_rows.append(
            {
                "induced_edge_id": induced_edge_id,
                "left_basis_id": int(row[EDGE_COLUMNS.index("left_basis_id")]),
                "right_basis_id": int(row[EDGE_COLUMNS.index("right_basis_id")]),
                "source0_boundary_count": int(row[EDGE_COLUMNS.index("source0_boundary_count")]),
                "source1_boundary_count": int(row[EDGE_COLUMNS.index("source1_boundary_count")]),
                "boundary_count": int(row[EDGE_COLUMNS.index("boundary_count")]),
            }
        )

    unique_distances = pairwise_distances(adjacency, bridge_owner_ids)
    weak_counts = Counter(row["owner_weak_class_code"] for row in bridge_rows)
    gate_ids = [row["p5_id"] for row in gate_rows]
    obs = {
        "line_point_count": int(owner_grid.shape[0]),
        "gate_count": len(gate_rows),
        "gate_id_sum": sum(gate_ids),
        "bridge_pair_cell_count": len(bridge_rows),
        "bridge_pair_role_count": len(PAIR_ROLES),
        "p5_gate_ids_match": int(tuple(gate_ids) == tuple(BEST_IDS)),
        "eta6_preserved_gate_count": sum(row["eta6_preserved_flag"] for row in gate_rows),
        "bridge_output_closure_pass_count": sum(row["output_in_closure_flag"] for row in bridge_rows),
        "bridge_closure_slack_min": min(row["closure_slack"] for row in bridge_rows),
        "bridge_closure_slack_max": max(row["closure_slack"] for row in bridge_rows),
        "bridge_closure_slack_sum": sum(row["closure_slack"] for row in bridge_rows),
        "bridge_unique_owner_count": len(bridge_owner_ids),
        "bridge_owner_cell_mass": sum(row["owner_cell_count"] for row in owner_bridge_rows),
        "bridge_owner_component_count": len({row["component_id"] for row in owner_bridge_rows}),
        "bridge_owner_weak_class_count": len({row["owner_weak_class_code"] for row in bridge_rows}),
        "bridge_pair_weak11_count": int(weak_counts[11]),
        "bridge_pair_weak12_count": int(weak_counts[12]),
        "bridge_induced_edge_count": len(induced_edge_rows),
        "bridge_induced_boundary_count": sum(row["boundary_count"] for row in induced_edge_rows),
        "bridge_induced_source0_boundary_count": sum(row["source0_boundary_count"] for row in induced_edge_rows),
        "bridge_induced_source1_boundary_count": sum(row["source1_boundary_count"] for row in induced_edge_rows),
        "bridge_unique_owner_pair_count": len(unique_distances),
        "bridge_unique_owner_distance_min": min(unique_distances),
        "bridge_unique_owner_distance_max": max(unique_distances),
        "bridge_unique_owner_distance_sum": sum(unique_distances),
        "gate_span_distance_max": max(row["span_max_distance"] for row in gate_summary_rows),
        "gate_span_distance_sum": sum(row["span_distance_sum"] for row in gate_summary_rows),
        "f4_sample_row_count": len({row["f4_row_id"] for row in gate_summary_rows}),
        "face_count": len({row["face_id"] for row in gate_summary_rows}),
        "label_mask_count": len({row["label_mask"] for row in gate_summary_rows}),
        "sample_level_bridge_flag": 1,
        "eta6_core_input_certified": int(
            eta6_core.get("status") == "ETA6_CORE_CERTIFIED"
            and eta6_core.get("all_checks_pass") is True
        ),
        "eta6_p21_input_certified": int(
            eta6_p21.get("status") == "ETA6_P21_CERTIFIED"
            and eta6_p21.get("all_checks_pass") is True
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
        "long_rec": long_rec,
        "bridge_rows": bridge_rows,
        "gate_rows": gate_summary_rows,
        "owner_bridge_rows": owner_bridge_rows,
        "induced_edge_rows": induced_edge_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "bridge_owner_ids": np.asarray(bridge_owner_ids, dtype=np.int16),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    bridge_table = table_from_rows(BRIDGE_COLUMNS, rows["bridge_rows"])
    gate_table = table_from_rows(GATE_COLUMNS_OUT, rows["gate_rows"])
    owner_bridge_table = table_from_rows(OWNER_BRIDGE_COLUMNS, rows["owner_bridge_rows"])
    induced_edge_table = table_from_rows(INDUCED_EDGE_COLUMNS, rows["induced_edge_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    checks = {
        "eta6_inputs_certified": (
            obs["eta6_core_input_certified"],
            obs["eta6_p21_input_certified"],
            obs["long_rec_input_certified"],
        )
        == (1, 1, 1),
        "gate_ids_match_eta6_core": (
            obs["gate_count"],
            obs["gate_id_sum"],
            obs["p5_gate_ids_match"],
            obs["eta6_preserved_gate_count"],
        )
        == (6, 422, 1, 6),
        "bridge_projection_is_total_and_closed": (
            obs["bridge_pair_cell_count"],
            obs["bridge_pair_role_count"],
            obs["bridge_output_closure_pass_count"],
            obs["bridge_closure_slack_min"],
            obs["bridge_closure_slack_max"],
            obs["bridge_closure_slack_sum"],
        )
        == (24, 4, 24, 0, 176, 774),
        "bridge_owner_fingerprint": (
            obs["bridge_unique_owner_count"],
            obs["bridge_owner_cell_mass"],
            obs["bridge_owner_component_count"],
            obs["bridge_owner_weak_class_count"],
            obs["bridge_pair_weak11_count"],
            obs["bridge_pair_weak12_count"],
        )
        == (11, 726_003, 1, 2, 22, 2),
        "bridge_transition_fingerprint": (
            obs["bridge_induced_edge_count"],
            obs["bridge_induced_boundary_count"],
            obs["bridge_induced_source0_boundary_count"],
            obs["bridge_induced_source1_boundary_count"],
            obs["bridge_unique_owner_pair_count"],
            obs["bridge_unique_owner_distance_min"],
            obs["bridge_unique_owner_distance_max"],
            obs["bridge_unique_owner_distance_sum"],
            obs["gate_span_distance_max"],
            obs["gate_span_distance_sum"],
        )
        == (6, 2620, 2199, 421, 55, 1, 10, 258, 9, 71),
        "bridge_source_fingerprint": (
            obs["f4_sample_row_count"],
            obs["face_count"],
            obs["label_mask_count"],
            obs["sample_level_bridge_flag"],
        )
        == (6, 3, 3, 1),
        "table_shapes_match": (
            tuple(bridge_table.shape),
            tuple(gate_table.shape),
            tuple(owner_bridge_table.shape),
            tuple(induced_edge_table.shape),
            tuple(obs_table.shape),
            tuple(rows["bridge_owner_ids"].shape),
        )
        == (
            (24, len(BRIDGE_COLUMNS)),
            (6, len(GATE_COLUMNS_OUT)),
            (11, len(OWNER_BRIDGE_COLUMNS)),
            (6, len(INDUCED_EDGE_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
            (11,),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "eta6_gate_sample_bridge_to_long_rec",
        "bridge_scope": {
            "kind": "sample_level_f_address_projection",
            "rule": (
                "for each p21 gate p5 row, use its p5 f4_row_id to read the "
                "eta6_f4 sampled C985 relation addresses, then project the four "
                "sampled source pairs into long_rec owner cells"
            ),
            "semantic_limit": (
                "this does not claim all eta6 support rows or all future recouplings "
                "are covered by the sampled bridge"
            ),
        },
        "gate": {
            "p5_ids": list(BEST_IDS),
            "gate_count": obs["gate_count"],
            "eta6_preserved_gate_count": obs["eta6_preserved_gate_count"],
            "f4_sample_row_count": obs["f4_sample_row_count"],
            "face_count": obs["face_count"],
            "label_mask_count": obs["label_mask_count"],
        },
        "projection": {
            "pair_roles": [role for role, *_rest in PAIR_ROLES],
            "bridge_pair_cell_count": obs["bridge_pair_cell_count"],
            "closure_pass_count": obs["bridge_output_closure_pass_count"],
            "closure_slack_range": [
                obs["bridge_closure_slack_min"],
                obs["bridge_closure_slack_max"],
            ],
            "closure_slack_sum": obs["bridge_closure_slack_sum"],
            "bridge_table_sha256": sha_array(bridge_table),
            "gate_table_sha256": sha_array(gate_table),
        },
        "owners": {
            "unique_owner_count": obs["bridge_unique_owner_count"],
            "owner_cell_mass": obs["bridge_owner_cell_mass"],
            "component_count": obs["bridge_owner_component_count"],
            "weak_class_count": obs["bridge_owner_weak_class_count"],
            "weak_counts": {"11": obs["bridge_pair_weak11_count"], "12": obs["bridge_pair_weak12_count"]},
            "owner_bridge_table_sha256": sha_array(owner_bridge_table),
            "bridge_owner_ids_sha256": sha_array(rows["bridge_owner_ids"]),
        },
        "transition": {
            "induced_edge_count": obs["bridge_induced_edge_count"],
            "induced_boundary_count": obs["bridge_induced_boundary_count"],
            "unique_owner_pair_count": obs["bridge_unique_owner_pair_count"],
            "unique_owner_distance_range": [
                obs["bridge_unique_owner_distance_min"],
                obs["bridge_unique_owner_distance_max"],
            ],
            "unique_owner_distance_sum": obs["bridge_unique_owner_distance_sum"],
            "gate_span_distance_max": obs["gate_span_distance_max"],
            "gate_span_distance_sum": obs["gate_span_distance_sum"],
            "induced_edge_table_sha256": sha_array(induced_edge_table),
        },
        "observable_table_sha256": sha_array(obs_table),
    }
    eta = {
        "schema": "long.eta@1",
        "object": "eta6_gate_sample_bridge_to_long_rec",
        "status": STATUS if all(checks.values()) else "LONG_ETA_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.eta.report@1",
        "status": eta["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_eta certifies a sample-level bridge from the eta6 p21 surgery "
            "gate into the long_rec transition kernel: all 24 sampled F-address "
            "source-pair cells land inside the long_rec closure, touch 11 owners "
            "in one connected component, and expose a small induced transition subgraph."
        ),
        "stage_protocol": {
            "draft": "reuse eta6_core, eta6_p21, eta6_f4/p5 tables, and long_rec",
            "witness": "project p21 gate sample F-address pairs into long_rec owner cells",
            "coherence": "check closure membership, preserved gate flags, and transition connectivity",
            "closure": "emit the bounded sample bridge with explicit non-universal scope",
            "emit": "write long_eta artifacts and verifier hook",
        },
        "inputs": {
            "eta6_core_report": input_entry(
                ETA6_CORE_REPORT,
                {"status": rows["eta6_core"].get("status")},
            ),
            "eta6_p21_report": input_entry(
                ETA6_P21_REPORT,
                {"status": rows["eta6_p21"].get("status")},
            ),
            "eta6_p21_tables": input_entry(ETA6_P21_TABLES),
            "eta6_p5_tables": input_entry(ETA6_P5_TABLES),
            "eta6_f4_tables": input_entry(ETA6_F4_TABLES),
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
            "eta": relpath(OUT_DIR / "eta.json"),
            "bridge_csv": relpath(OUT_DIR / "bridge.csv"),
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
                "the p21 eta6 gate sample F-addresses project into long_rec owner cells",
                "each sampled source-pair output is inside the long_rec frontier closure",
                "the projected owners occupy one connected long_rec transition component",
                "the projected bridge has an exact finite owner/edge fingerprint",
            ],
            "does_not_certify_because_out_of_scope": [
                "all eta6 support rows, because this is a sampled F-address bridge",
                "eta6 invariance under every long_rec transition",
                "post-surgery rebuilt-carrier semantics",
                "a universal eta6 horizon theorem",
            ],
        },
        "next_highest_yield_item": (
            "Build long_eta2: expand from sampled f4 addresses to all p21 gate "
            "support fibers, then compare the resulting owner subgraph with eta6_core."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.eta.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.eta.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "eta": eta,
        "bridge_csv": csv_text(BRIDGE_COLUMNS, rows["bridge_rows"]),
        "gate_csv": csv_text(GATE_COLUMNS_OUT, rows["gate_rows"]),
        "owner_csv": csv_text(OWNER_BRIDGE_COLUMNS, rows["owner_bridge_rows"]),
        "edge_csv": csv_text(INDUCED_EDGE_COLUMNS, rows["induced_edge_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "bridge_table": bridge_table,
        "gate_table": gate_table,
        "owner_bridge_table": owner_bridge_table,
        "induced_edge_table": induced_edge_table,
        "observable_table": obs_table,
        "bridge_owner_ids": rows["bridge_owner_ids"],
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
    write_json(OUT_DIR / "eta.json", payloads["eta"])
    (OUT_DIR / "bridge.csv").write_text(payloads["bridge_csv"], encoding="utf-8")
    (OUT_DIR / "gate.csv").write_text(payloads["gate_csv"], encoding="utf-8")
    (OUT_DIR / "owner.csv").write_text(payloads["owner_csv"], encoding="utf-8")
    (OUT_DIR / "edge.csv").write_text(payloads["edge_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        bridge_table=payloads["bridge_table"],
        gate_table=payloads["gate_table"],
        owner_bridge_table=payloads["owner_bridge_table"],
        induced_edge_table=payloads["induced_edge_table"],
        observable_table=payloads["observable_table"],
        bridge_owner_ids=payloads["bridge_owner_ids"],
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
