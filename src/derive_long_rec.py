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
    from .derive_long_basis import (
        OUT_DIR as LONG_BASIS_DIR,
        TRI_BASIS_COLUMNS,
        build_payloads as build_long_basis_payloads,
    )
    from .derive_long_tri import WEAK_CLASSES
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_basis import (
        OUT_DIR as LONG_BASIS_DIR,
        TRI_BASIS_COLUMNS,
        build_payloads as build_long_basis_payloads,
    )
    from derive_long_tri import WEAK_CLASSES
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_rec"
STATUS = "LONG_REC_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
LONG_BASIS_REPORT = D20_INVARIANTS / "proof_obligations" / "long_basis" / "report.json"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_rec.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_rec.py"

OWNER_COLUMNS = [
    "basis_id",
    "source0_addr",
    "source1_addr",
    "target_addr",
    "coeff",
    "weak_class_code",
    "owner_cell_count",
    "graph_degree",
    "weighted_degree",
    "owner_lln_var_num",
    "owner_lln_var_den",
]
EDGE_COLUMNS = [
    "edge_id",
    "left_basis_id",
    "right_basis_id",
    "source0_boundary_count",
    "source1_boundary_count",
    "boundary_count",
    "left_weak_class_code",
    "right_weak_class_code",
    "edge_lln_var_num",
    "edge_lln_var_den",
]
WEAK_OWNER_COLUMNS = [
    "class_id",
    "class_name",
    "basis_count",
    "owner_cell_count",
    "owner_lln_var_num",
    "owner_lln_var_den",
]
WEAK_EDGE_COLUMNS = [
    "weak_edge_id",
    "left_class_id",
    "right_class_id",
    "boundary_count",
    "edge_lln_var_num",
    "edge_lln_var_den",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "line_point_count",
    "basis_count",
    "frontier_cell_count",
    "active_owner_count",
    "owner_cell_count_sum",
    "owner_cell_count_min",
    "owner_cell_count_max",
    "frontier_sum",
    "frontier_square_sum",
    "frontier_min",
    "frontier_max",
    "transition_node_count",
    "transition_edge_count",
    "transition_component_count",
    "transition_component_max_size",
    "transition_degree_min",
    "transition_degree_max",
    "transition_weighted_degree_min",
    "transition_weighted_degree_max",
    "source0_boundary_contact_count",
    "source1_boundary_contact_count",
    "boundary_contact_count",
    "directed_boundary_contact_count",
    "self_neighbor_contact_count",
    "owner_lln_var_den",
    "owner_lln_var_num_sum",
    "edge_lln_var_den",
    "edge_lln_var_num_sum",
    "weak_owner_class_count",
    "weak_owner_cell_count_max",
    "weak_owner_lln_var_num_sum",
    "weak_edge_class_pair_count",
    "weak_edge_lln_var_num_sum",
    "owner_grid_complete",
    "owner_frontier_regenerates_long_basis",
    "transition_symmetric",
    "transition_row_positive",
    "long_basis_input_certified",
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


def owner_grid_from_basis(
    tri_basis_table: np.ndarray,
    n: int,
) -> tuple[np.ndarray, np.ndarray]:
    owner = np.full((n, n), -1, dtype=np.int16)
    frontier = np.full((n, n), n, dtype=np.int16)
    target_index = TRI_BASIS_COLUMNS.index("target_addr")
    id_index = TRI_BASIS_COLUMNS.index("basis_id")
    source0_index = TRI_BASIS_COLUMNS.index("source0_addr")
    source1_index = TRI_BASIS_COLUMNS.index("source1_addr")
    order = np.lexsort((tri_basis_table[:, id_index], tri_basis_table[:, target_index]))
    for row in tri_basis_table[order]:
        basis_id = int(row[id_index])
        source0 = int(row[source0_index])
        source1 = int(row[source1_index])
        target = int(row[target_index])
        sub = frontier[: source0 + 1, : source1 + 1]
        mask = target < sub
        if not bool(mask.any()):
            continue
        sub[mask] = target
        owner_sub = owner[: source0 + 1, : source1 + 1]
        owner_sub[mask] = basis_id
        owner[: source0 + 1, : source1 + 1] = owner_sub
    return owner, frontier


def encoded_edge_counts(owner: np.ndarray, basis_count: int) -> tuple[dict[tuple[int, int], list[int]], list[int], int]:
    axis_totals: list[int] = []
    merged: dict[tuple[int, int], list[int]] = {}
    self_contacts = 0
    for axis, (left, right) in enumerate(
        ((owner[:-1, :], owner[1:, :]), (owner[:, :-1], owner[:, 1:]))
    ):
        differs = left != right
        self_contacts += int(left.size - differs.sum())
        src = left[differs].astype(np.int64, copy=False)
        dst = right[differs].astype(np.int64, copy=False)
        lo = np.minimum(src, dst)
        hi = np.maximum(src, dst)
        encoded = lo * basis_count + hi
        unique, counts = np.unique(encoded, return_counts=True)
        axis_total = int(counts.sum())
        axis_totals.append(axis_total)
        for code, count in zip(unique.tolist(), counts.tolist()):
            key = (int(code // basis_count), int(code % basis_count))
            merged.setdefault(key, [0, 0])[axis] = int(count)
    return merged, axis_totals, self_contacts


def graph_components(basis_count: int, edges: dict[tuple[int, int], list[int]]) -> tuple[int, int, np.ndarray]:
    adjacency = [set() for _ in range(basis_count)]
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    component_ids = np.full(basis_count, -1, dtype=np.int16)
    component_sizes: list[int] = []
    for start in range(basis_count):
        if component_ids[start] >= 0:
            continue
        component_id = len(component_sizes)
        queue: deque[int] = deque([start])
        component_ids[start] = component_id
        size = 0
        while queue:
            node = queue.popleft()
            size += 1
            for nxt in adjacency[node]:
                if component_ids[nxt] < 0:
                    component_ids[nxt] = component_id
                    queue.append(nxt)
        component_sizes.append(size)
    return len(component_sizes), max(component_sizes), component_ids


def build_rows() -> dict[str, Any]:
    basis_payload = build_long_basis_payloads()
    tri_basis_table = np.asarray(basis_payload["tri_basis_table"], dtype=np.int64)
    basis_frontier = np.asarray(basis_payload["basis_frontier"], dtype=np.int16)
    long_basis = load_json(LONG_BASIS_REPORT)
    n = int(basis_payload["report"]["witness"]["line"]["point_count"])
    basis_count = int(tri_basis_table.shape[0])
    owner, owner_frontier = owner_grid_from_basis(tri_basis_table, n)
    owner_counts = np.bincount(owner.ravel().astype(np.int64), minlength=basis_count).astype(np.int64)
    edges, axis_totals, self_contacts = encoded_edge_counts(owner, basis_count)
    component_count, component_max_size, component_ids = graph_components(basis_count, edges)
    graph_degree = np.zeros(basis_count, dtype=np.int64)
    weighted_degree = np.zeros(basis_count, dtype=np.int64)
    for (left, right), (source0_count, source1_count) in edges.items():
        count = int(source0_count + source1_count)
        graph_degree[left] += 1
        graph_degree[right] += 1
        weighted_degree[left] += count
        weighted_degree[right] += count
    frontier_values = owner_frontier.ravel().astype(np.int64)
    frontier_cell_count = int(owner.size)
    boundary_contact_count = int(sum(source0 + source1 for source0, source1 in edges.values()))
    owner_var_den = frontier_cell_count * frontier_cell_count
    edge_var_den = boundary_contact_count * boundary_contact_count
    weak_codes = tri_basis_table[:, TRI_BASIS_COLUMNS.index("weak_class_code")]
    owner_rows: list[dict[str, int]] = []
    for basis_id, row in enumerate(tri_basis_table):
        count = int(owner_counts[basis_id])
        owner_rows.append(
            {
                "basis_id": basis_id,
                "source0_addr": int(row[TRI_BASIS_COLUMNS.index("source0_addr")]),
                "source1_addr": int(row[TRI_BASIS_COLUMNS.index("source1_addr")]),
                "target_addr": int(row[TRI_BASIS_COLUMNS.index("target_addr")]),
                "coeff": int(row[TRI_BASIS_COLUMNS.index("coeff")]),
                "weak_class_code": int(weak_codes[basis_id]),
                "owner_cell_count": count,
                "graph_degree": int(graph_degree[basis_id]),
                "weighted_degree": int(weighted_degree[basis_id]),
                "owner_lln_var_num": count * (frontier_cell_count - count),
                "owner_lln_var_den": owner_var_den,
            }
        )
    edge_rows: list[dict[str, int]] = []
    for edge_id, ((left, right), (source0_count, source1_count)) in enumerate(
        sorted(edges.items())
    ):
        boundary_count = int(source0_count + source1_count)
        edge_rows.append(
            {
                "edge_id": edge_id,
                "left_basis_id": int(left),
                "right_basis_id": int(right),
                "source0_boundary_count": int(source0_count),
                "source1_boundary_count": int(source1_count),
                "boundary_count": boundary_count,
                "left_weak_class_code": int(weak_codes[left]),
                "right_weak_class_code": int(weak_codes[right]),
                "edge_lln_var_num": boundary_count * (boundary_contact_count - boundary_count),
                "edge_lln_var_den": edge_var_den,
            }
        )
    weak_owner_counts = np.bincount(
        weak_codes[owner.ravel().astype(np.int64)].astype(np.int64),
        minlength=len(WEAK_CLASSES),
    ).astype(np.int64)
    weak_basis_counts = np.bincount(weak_codes.astype(np.int64), minlength=len(WEAK_CLASSES)).astype(np.int64)
    weak_owner_rows: list[dict[str, int | str]] = []
    for class_id, class_name in enumerate(WEAK_CLASSES):
        count = int(weak_owner_counts[class_id])
        weak_owner_rows.append(
            {
                "class_id": class_id,
                "class_name": class_name,
                "basis_count": int(weak_basis_counts[class_id]),
                "owner_cell_count": count,
                "owner_lln_var_num": count * (frontier_cell_count - count),
                "owner_lln_var_den": owner_var_den,
            }
        )
    weak_edge_counter: Counter[tuple[int, int]] = Counter()
    for row in edge_rows:
        left_class = int(row["left_weak_class_code"])
        right_class = int(row["right_weak_class_code"])
        if right_class < left_class:
            left_class, right_class = right_class, left_class
        weak_edge_counter[(left_class, right_class)] += int(row["boundary_count"])
    weak_edge_rows: list[dict[str, int]] = []
    for weak_edge_id, ((left_class, right_class), count) in enumerate(
        sorted(weak_edge_counter.items())
    ):
        weak_edge_rows.append(
            {
                "weak_edge_id": weak_edge_id,
                "left_class_id": int(left_class),
                "right_class_id": int(right_class),
                "boundary_count": int(count),
                "edge_lln_var_num": int(count) * (boundary_contact_count - int(count)),
                "edge_lln_var_den": edge_var_den,
            }
        )
    owner_table = table_from_rows(OWNER_COLUMNS, owner_rows)
    edge_table = table_from_rows(EDGE_COLUMNS, edge_rows)
    weak_owner_numeric_rows = [
        {key: value for key, value in row.items() if key != "class_name"}
        for row in weak_owner_rows
    ]
    weak_owner_table = table_from_rows(
        [column for column in WEAK_OWNER_COLUMNS if column != "class_name"],
        weak_owner_numeric_rows,
    )
    weak_edge_table = table_from_rows(WEAK_EDGE_COLUMNS, weak_edge_rows)
    obs = {
        "line_point_count": n,
        "basis_count": basis_count,
        "frontier_cell_count": frontier_cell_count,
        "active_owner_count": int(np.count_nonzero(owner_counts)),
        "owner_cell_count_sum": int(owner_counts.sum()),
        "owner_cell_count_min": int(owner_counts.min()),
        "owner_cell_count_max": int(owner_counts.max()),
        "frontier_sum": int(frontier_values.sum()),
        "frontier_square_sum": int(np.dot(frontier_values, frontier_values)),
        "frontier_min": int(frontier_values.min()),
        "frontier_max": int(frontier_values.max()),
        "transition_node_count": basis_count,
        "transition_edge_count": int(len(edge_rows)),
        "transition_component_count": int(component_count),
        "transition_component_max_size": int(component_max_size),
        "transition_degree_min": int(graph_degree.min()),
        "transition_degree_max": int(graph_degree.max()),
        "transition_weighted_degree_min": int(weighted_degree.min()),
        "transition_weighted_degree_max": int(weighted_degree.max()),
        "source0_boundary_contact_count": int(axis_totals[0]),
        "source1_boundary_contact_count": int(axis_totals[1]),
        "boundary_contact_count": boundary_contact_count,
        "directed_boundary_contact_count": 2 * boundary_contact_count,
        "self_neighbor_contact_count": int(self_contacts),
        "owner_lln_var_den": owner_var_den,
        "owner_lln_var_num_sum": int(owner_table[:, OWNER_COLUMNS.index("owner_lln_var_num")].sum()),
        "edge_lln_var_den": edge_var_den,
        "edge_lln_var_num_sum": int(edge_table[:, EDGE_COLUMNS.index("edge_lln_var_num")].sum()),
        "weak_owner_class_count": int(np.count_nonzero(weak_owner_counts)),
        "weak_owner_cell_count_max": int(weak_owner_counts.max()),
        "weak_owner_lln_var_num_sum": int(
            weak_owner_table[:, WEAK_OWNER_COLUMNS.index("owner_lln_var_num") - 1].sum()
        ),
        "weak_edge_class_pair_count": int(len(weak_edge_rows)),
        "weak_edge_lln_var_num_sum": int(
            weak_edge_table[:, WEAK_EDGE_COLUMNS.index("edge_lln_var_num")].sum()
        ),
        "owner_grid_complete": int(np.all(owner >= 0)),
        "owner_frontier_regenerates_long_basis": int(np.array_equal(owner_frontier, basis_frontier)),
        "transition_symmetric": 1,
        "transition_row_positive": int(bool(np.all(weighted_degree > 0))),
        "long_basis_input_certified": int(
            long_basis.get("status") == "LONG_BASIS_CERTIFIED"
            and long_basis.get("all_checks_pass") is True
        ),
    }
    obs_rows = [
        {"observable_id": code, "observable_code": code, "value": int(obs[name])}
        for name, code in sorted(OBS_CODES.items(), key=lambda item: item[1])
    ]
    return {
        "basis_payload": basis_payload,
        "long_basis": long_basis,
        "owner": owner,
        "owner_frontier": owner_frontier,
        "component_ids": component_ids,
        "owner_table": owner_table,
        "edge_table": edge_table,
        "weak_owner_table": weak_owner_table,
        "weak_edge_table": weak_edge_table,
        "owner_rows": owner_rows,
        "edge_rows": edge_rows,
        "weak_owner_rows": weak_owner_rows,
        "weak_edge_rows": weak_edge_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    checks = {
        "long_basis_input_certified": obs["long_basis_input_certified"] == 1,
        "line_size_matches_basis": obs["line_point_count"] == 985,
        "owner_grid_complete": obs["owner_grid_complete"] == 1,
        "owner_frontier_regenerates_long_basis": obs["owner_frontier_regenerates_long_basis"] == 1,
        "owner_partition_exact": (
            obs["basis_count"],
            obs["frontier_cell_count"],
            obs["active_owner_count"],
            obs["owner_cell_count_sum"],
            obs["owner_cell_count_min"],
            obs["owner_cell_count_max"],
        )
        == (259, 970_225, 259, 970_225, 1, 197_910),
        "frontier_moments_exact": (
            obs["frontier_sum"],
            obs["frontier_square_sum"],
            obs["frontier_min"],
            obs["frontier_max"],
        )
        == (404_111_708, 233_520_639_830, 0, 893),
        "transition_graph_exact": (
            obs["transition_node_count"],
            obs["transition_edge_count"],
            obs["transition_component_count"],
            obs["transition_component_max_size"],
            obs["transition_degree_min"],
            obs["transition_degree_max"],
            obs["transition_weighted_degree_min"],
            obs["transition_weighted_degree_max"],
        )
        == (259, 642, 1, 259, 3, 13, 3, 1736),
        "transition_boundary_exact": (
            obs["source0_boundary_contact_count"],
            obs["source1_boundary_contact_count"],
            obs["boundary_contact_count"],
            obs["directed_boundary_contact_count"],
            obs["self_neighbor_contact_count"],
        )
        == (12_707, 5_410, 18_117, 36_234, 1_920_363),
        "finite_lln_moments_exact": (
            obs["owner_lln_var_den"],
            obs["owner_lln_var_num_sum"],
            obs["edge_lln_var_den"],
            obs["edge_lln_var_num_sum"],
            obs["weak_owner_lln_var_num_sum"],
            obs["weak_edge_lln_var_num_sum"],
        )
        == (
            941_336_550_625,
            837_883_117_934,
            328_225_689,
            321_236_252,
            361_363_966_216,
            135_408_656,
        ),
        "weak_transition_exact": (
            obs["weak_owner_class_count"],
            obs["weak_owner_cell_count_max"],
            obs["weak_edge_class_pair_count"],
        )
        == (5, 718_941, 8),
        "transition_kernel_is_symmetric_and_total": (
            obs["transition_symmetric"],
            obs["transition_row_positive"],
        )
        == (1, 1),
        "table_shapes_match": (
            tuple(rows["owner_table"].shape),
            tuple(rows["edge_table"].shape),
            tuple(rows["weak_owner_table"].shape),
            tuple(rows["weak_edge_table"].shape),
            tuple(obs_table.shape),
            tuple(rows["owner"].shape),
        )
        == (
            (259, len(OWNER_COLUMNS)),
            (642, len(EDGE_COLUMNS)),
            (13, len(WEAK_OWNER_COLUMNS) - 1),
            (8, len(WEAK_EDGE_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
            (985, 985),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "finite_alexandrov_line_basis_transition_kernel",
        "line": {
            "point_count": obs["line_point_count"],
            "frontier_cell_count": obs["frontier_cell_count"],
            "basis_count": obs["basis_count"],
        },
        "owner_partition": {
            "rule": "each source-pair cell is owned by the lowest-target basis generator covering it; ties keep the lowest basis id",
            "active_owner_count": obs["active_owner_count"],
            "owner_cell_count_min": obs["owner_cell_count_min"],
            "owner_cell_count_max": obs["owner_cell_count_max"],
            "owner_grid_sha256": sha_array(rows["owner"]),
            "owner_table_sha256": sha_array(rows["owner_table"]),
        },
        "transition_kernel": {
            "rule": "two generators are adjacent when their owned frontier cells share a source0 or source1 grid boundary",
            "node_count": obs["transition_node_count"],
            "edge_count": obs["transition_edge_count"],
            "component_count": obs["transition_component_count"],
            "component_max_size": obs["transition_component_max_size"],
            "degree_range": [obs["transition_degree_min"], obs["transition_degree_max"]],
            "weighted_degree_range": [
                obs["transition_weighted_degree_min"],
                obs["transition_weighted_degree_max"],
            ],
            "source0_boundary_contacts": obs["source0_boundary_contact_count"],
            "source1_boundary_contacts": obs["source1_boundary_contact_count"],
            "boundary_contacts": obs["boundary_contact_count"],
            "directed_boundary_contacts": obs["directed_boundary_contact_count"],
            "symmetric": bool(obs["transition_symmetric"]),
            "row_positive": bool(obs["transition_row_positive"]),
            "edge_table_sha256": sha_array(rows["edge_table"]),
        },
        "frontier_moments": {
            "frontier_sum": obs["frontier_sum"],
            "frontier_square_sum": obs["frontier_square_sum"],
            "frontier_min": obs["frontier_min"],
            "frontier_max": obs["frontier_max"],
            "owner_frontier_sha256": sha_array(rows["owner_frontier"]),
        },
        "weak_transition": {
            "classes": WEAK_CLASSES,
            "owner_class_count": obs["weak_owner_class_count"],
            "owner_cell_count_max": obs["weak_owner_cell_count_max"],
            "weak_edge_class_pair_count": obs["weak_edge_class_pair_count"],
            "weak_owner_table_sha256": sha_array(rows["weak_owner_table"]),
            "weak_edge_table_sha256": sha_array(rows["weak_edge_table"]),
        },
        "finite_lln": {
            "owner_sample_space": "985^2 source-pair frontier cells",
            "owner_event_rule": "for owner count m among N cells, Var(mean_k)=m*(N-m)/(N^2*k)",
            "edge_sample_space": "undirected owner boundary contacts",
            "edge_event_rule": "for edge boundary count m among B contacts, Var(mean_k)=m*(B-m)/(B^2*k)",
            "owner_lln_var_den": obs["owner_lln_var_den"],
            "edge_lln_var_den": obs["edge_lln_var_den"],
        },
        "observable_table_sha256": sha_array(obs_table),
    }
    rec = {
        "schema": "long.rec@1",
        "object": "finite_alexandrov_line_basis_transition_kernel",
        "status": STATUS if all(checks.values()) else "LONG_REC_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.rec.report@1",
        "status": rec["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_rec certifies the finite transition kernel induced by the "
            "long_basis lower-envelope ownership partition: every frontier cell "
            "has a basis owner, adjacent cells induce a connected symmetric "
            "transition graph, and owner/edge events have exact finite LLN data."
        ),
        "stage_protocol": {
            "draft": "reuse long_basis and its regenerated frontier",
            "witness": "compute frontier owners and boundary-induced transition edges",
            "coherence": "check ownership covers the line square and regenerates the frontier",
            "closure": "check graph connectivity, transition counts, and exact LLN moments",
            "emit": "write long_rec artifacts and verifier hook",
        },
        "inputs": {
            "long_basis_report": input_entry(
                LONG_BASIS_REPORT,
                {"status": rows["long_basis"].get("status")},
            ),
            "long_basis_tables": input_entry(LONG_BASIS_DIR / "tables.npz"),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "rec": relpath(OUT_DIR / "rec.json"),
            "owner_csv": relpath(OUT_DIR / "owner.csv"),
            "edge_csv": relpath(OUT_DIR / "edge.csv"),
            "weak_owner_csv": relpath(OUT_DIR / "weak_owner.csv"),
            "weak_edge_csv": relpath(OUT_DIR / "weak_edge.csv"),
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
                "a complete owner partition of the 985x985 Alexandrov source-pair frontier",
                "the connected symmetric transition graph induced by adjacent owner cells",
                "weak-class transition aggregation over the owner graph",
                "exact finite LLN variance data for owner events and boundary-edge events",
            ],
            "does_not_certify_because_out_of_scope": [
                "eta6 preservation, because no canonical eta6-to-long_basis bridge is provided here",
                "semantic recoupling moves outside the tensor lookup lower envelope",
                "continuous or asymptotic LLN limits",
                "a transition kernel for C985 associator addresses beyond the line projection",
            ],
        },
        "next_highest_yield_item": (
            "Build long_eta: a verified bridge from eta6 carrier ids into "
            "long_rec owners, then test eta6 preservation on the transition graph."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.rec.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.rec.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "rec": rec,
        "owner_csv": csv_text(OWNER_COLUMNS, rows["owner_rows"]),
        "edge_csv": csv_text(EDGE_COLUMNS, rows["edge_rows"]),
        "weak_owner_csv": csv_text(WEAK_OWNER_COLUMNS, rows["weak_owner_rows"]),
        "weak_edge_csv": csv_text(WEAK_EDGE_COLUMNS, rows["weak_edge_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "owner_table": rows["owner_table"],
        "edge_table": rows["edge_table"],
        "weak_owner_table": rows["weak_owner_table"],
        "weak_edge_table": rows["weak_edge_table"],
        "observable_table": obs_table,
        "owner_grid": rows["owner"],
        "owner_frontier": rows["owner_frontier"],
        "component_ids": rows["component_ids"],
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
    write_json(OUT_DIR / "rec.json", payloads["rec"])
    (OUT_DIR / "owner.csv").write_text(payloads["owner_csv"], encoding="utf-8")
    (OUT_DIR / "edge.csv").write_text(payloads["edge_csv"], encoding="utf-8")
    (OUT_DIR / "weak_owner.csv").write_text(payloads["weak_owner_csv"], encoding="utf-8")
    (OUT_DIR / "weak_edge.csv").write_text(payloads["weak_edge_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        owner_table=payloads["owner_table"],
        edge_table=payloads["edge_table"],
        weak_owner_table=payloads["weak_owner_table"],
        weak_edge_table=payloads["weak_edge_table"],
        observable_table=payloads["observable_table"],
        owner_grid=payloads["owner_grid"],
        owner_frontier=payloads["owner_frontier"],
        component_ids=payloads["component_ids"],
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
