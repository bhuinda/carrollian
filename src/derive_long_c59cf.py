from __future__ import annotations

import csv
import hashlib
import heapq
import json
from pathlib import Path
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
    from .derive_long_raw import csv_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_raw import csv_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_c59cf"
STATUS = "LONG_C59CF_MINIMAL_COUNTERFLOW_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_C59E = PROOF_ROOT / "long_c59e" / "report.json"
LONG_C59E_EDGE_FLUX = PROOF_ROOT / "long_c59e" / "edge_flux.csv"
LONG_C59E_NODE_BALANCE = PROOF_ROOT / "long_c59e" / "node_balance.csv"
LONG_STRESS_GATE = PROOF_ROOT / "long_stress_gate" / "report.json"
LONG_STRESS_EDGE = PROOF_ROOT / "long_stress_gate" / "stress_edge.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_c59cf.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_c59cf.py"

COUNTERFLOW_COLUMNS = [
    "counterflow_id",
    "stress_edge_id",
    "source_atom",
    "target_atom",
    "counterflow_scaled",
    "unit_cost",
    "cost_scaled",
    "existing_edge_flag",
    "tight_dual_flag",
]
CORRECTED_EDGE_COLUMNS = [
    "stress_edge_id",
    "source_atom",
    "target_atom",
    "initial_flux_scaled",
    "counterflow_scaled",
    "corrected_flux_scaled",
    "edge_used_initial_flag",
    "edge_used_counterflow_flag",
    "edge_used_corrected_flag",
]
CORRECTED_NODE_COLUMNS = [
    "atom_id",
    "initial_outgoing_flux_scaled",
    "initial_incoming_flux_scaled",
    "initial_divergence_scaled",
    "counterflow_outgoing_scaled",
    "counterflow_incoming_scaled",
    "counterflow_divergence_scaled",
    "corrected_divergence_scaled",
    "corrected_abs_divergence_scaled",
    "corrected_local_conserved_flag",
]
DUAL_POTENTIAL_COLUMNS = [
    "atom_id",
    "balance_scaled",
    "dual_potential",
    "dual_contribution_scaled",
]
DUAL_EDGE_COLUMNS = [
    "stress_edge_id",
    "source_atom",
    "target_atom",
    "counterflow_scaled",
    "dual_drop",
    "dual_slack",
    "dual_feasible_flag",
    "tight_dual_flag",
    "complementary_slackness_flag",
]
GAP_COLUMNS = [
    "gap_id",
    "gap_code",
    "certified_flag",
    "open_flag",
    "obstruction_flag",
    "next_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

GAP_NAMES = [
    "counterflow_materialized",
    "corrected_local_conservation",
    "minimality_dual_certificate",
    "finite_conserved_edge_current",
    "finite_stress_tensor_lift",
    "smooth_lorentzian_metric",
    "thermal_gravity_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "stress_node_count",
    "stress_directed_edge_count",
    "initial_defect_node_count",
    "initial_total_abs_defect_scaled",
    "supply_node_count",
    "demand_node_count",
    "supply_total_scaled",
    "demand_total_scaled",
    "counterflow_row_count",
    "counterflow_used_edge_count",
    "counterflow_total_scaled",
    "counterflow_cost_scaled",
    "primal_cost_scaled",
    "dual_bound_scaled",
    "primal_dual_gap_scaled",
    "dual_feasible_flag",
    "complementary_slackness_flag",
    "minimal_counterflow_flag",
    "corrected_local_conserved_node_count",
    "corrected_defect_node_count",
    "corrected_total_abs_defect_scaled",
    "corrected_max_abs_defect_scaled",
    "corrected_global_divergence_scaled",
    "corrected_local_conservation_flag",
    "finite_conserved_edge_current_flag",
    "physical_stress_energy_flag",
    "smooth_metric_flag",
    "thermal_gravity_flag",
    "next_gap_code",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_csv_int(path: Path) -> list[dict[str, int]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return [{key: int(value) for key, value in row.items()} for row in reader]


def certified(report: dict[str, Any]) -> bool:
    return report.get("all_checks_pass") is True and "CERTIFIED" in str(
        report.get("status", "")
    )


def min_cost_counterflow(
    balances: list[int],
    stress_edges: list[dict[str, int]],
) -> tuple[dict[int, int], list[int], int, int]:
    """Route positive correction balances to negative balances at unit edge cost."""
    node_count = len(balances)
    source = node_count
    sink = node_count + 1
    graph: list[list[list[Any]]] = [[] for _ in range(node_count + 2)]
    arc_refs: list[tuple[int, int, int, int, int]] = []

    def add_arc(
        u: int,
        v: int,
        capacity: int,
        cost: int,
        edge_id: int | None = None,
    ) -> tuple[int, int]:
        graph[u].append([v, capacity, cost, len(graph[v]), edge_id])
        graph[v].append([u, 0, -cost, len(graph[u]) - 1, None])
        return u, len(graph[u]) - 1

    total_supply = sum(max(value, 0) for value in balances)
    for atom, balance in enumerate(balances):
        if balance > 0:
            add_arc(source, atom, balance, 0)
        elif balance < 0:
            add_arc(atom, sink, -balance, 0)

    for edge in stress_edges:
        ref_u, ref_i = add_arc(
            edge["source_atom"],
            edge["target_atom"],
            total_supply,
            1,
            edge["stress_edge_id"],
        )
        arc_refs.append(
            (
                edge["stress_edge_id"],
                edge["source_atom"],
                edge["target_atom"],
                ref_u,
                ref_i,
            )
        )

    potentials = [0] * (node_count + 2)
    flow = 0
    cost = 0
    unreachable = 10**100
    while flow < total_supply:
        distance = [unreachable] * (node_count + 2)
        parent: list[tuple[int, int] | None] = [None] * (node_count + 2)
        distance[source] = 0
        heap: list[tuple[int, int]] = [(0, source)]
        while heap:
            dist_u, u = heapq.heappop(heap)
            if dist_u != distance[u]:
                continue
            for edge_index, arc in enumerate(graph[u]):
                v, capacity, edge_cost, _reverse, _edge_id = arc
                if capacity <= 0:
                    continue
                reduced_cost = edge_cost + potentials[u] - potentials[v]
                next_distance = dist_u + reduced_cost
                if next_distance < distance[v]:
                    distance[v] = next_distance
                    parent[v] = (u, edge_index)
                    heapq.heappush(heap, (next_distance, v))

        if parent[sink] is None:
            break

        for index, value in enumerate(distance):
            if value < unreachable:
                potentials[index] += value

        augment = total_supply - flow
        v = sink
        while v != source:
            u, edge_index = parent[v]  # type: ignore[misc]
            augment = min(augment, graph[u][edge_index][1])
            v = u

        v = sink
        while v != source:
            u, edge_index = parent[v]  # type: ignore[misc]
            arc = graph[u][edge_index]
            arc[1] -= augment
            reverse_index = arc[3]
            graph[v][reverse_index][1] += augment
            cost += augment * arc[2]
            v = u
        flow += augment

    edge_flow: dict[int, int] = {}
    for edge_id, _u, _v, ref_u, ref_i in arc_refs:
        remaining = graph[ref_u][ref_i][1]
        used = total_supply - remaining
        if used:
            edge_flow[edge_id] = used

    dual_potential = [-potentials[index] for index in range(node_count)]
    shift = min(dual_potential) if dual_potential else 0
    dual_potential = [value - shift for value in dual_potential]
    return edge_flow, dual_potential, flow, cost


def build_rows() -> dict[str, Any]:
    c59e = load_json(LONG_C59E)
    stress_gate = load_json(LONG_STRESS_GATE)
    edge_flux_rows_source = read_csv_int(LONG_C59E_EDGE_FLUX)
    node_balance_rows_source = read_csv_int(LONG_C59E_NODE_BALANCE)
    stress_edges = read_csv_int(LONG_STRESS_EDGE)

    initial_flux_by_edge = {
        row["stress_edge_id"]: row["net_flux_scaled"]
        for row in edge_flux_rows_source
    }
    balances = [
        -row["divergence_scaled"]
        for row in sorted(node_balance_rows_source, key=lambda row: row["atom_id"])
    ]
    counterflow_by_edge, dual_potentials, routed_flow, routed_cost = (
        min_cost_counterflow(balances, stress_edges)
    )

    edge_by_id = {row["stress_edge_id"]: row for row in stress_edges}
    dual_edge_rows = []
    for edge in stress_edges:
        edge_id = edge["stress_edge_id"]
        source_atom = edge["source_atom"]
        target_atom = edge["target_atom"]
        counterflow = counterflow_by_edge.get(edge_id, 0)
        dual_drop = dual_potentials[source_atom] - dual_potentials[target_atom]
        dual_slack = 1 - dual_drop
        dual_feasible_flag = int(dual_slack >= 0)
        tight_dual_flag = int(dual_slack == 0)
        complementary_slackness_flag = int(counterflow == 0 or dual_slack == 0)
        dual_edge_rows.append(
            {
                "stress_edge_id": edge_id,
                "source_atom": source_atom,
                "target_atom": target_atom,
                "counterflow_scaled": counterflow,
                "dual_drop": dual_drop,
                "dual_slack": dual_slack,
                "dual_feasible_flag": dual_feasible_flag,
                "tight_dual_flag": tight_dual_flag,
                "complementary_slackness_flag": complementary_slackness_flag,
            }
        )

    dual_edge_by_id = {row["stress_edge_id"]: row for row in dual_edge_rows}
    counterflow_rows = []
    for counterflow_id, edge_id in enumerate(sorted(counterflow_by_edge)):
        edge = edge_by_id[edge_id]
        counterflow = counterflow_by_edge[edge_id]
        counterflow_rows.append(
            {
                "counterflow_id": counterflow_id,
                "stress_edge_id": edge_id,
                "source_atom": edge["source_atom"],
                "target_atom": edge["target_atom"],
                "counterflow_scaled": counterflow,
                "unit_cost": 1,
                "cost_scaled": counterflow,
                "existing_edge_flag": 1,
                "tight_dual_flag": dual_edge_by_id[edge_id]["tight_dual_flag"],
            }
        )

    corrected_edge_rows = []
    for edge in stress_edges:
        edge_id = edge["stress_edge_id"]
        initial_flux = initial_flux_by_edge.get(edge_id, 0)
        counterflow = counterflow_by_edge.get(edge_id, 0)
        corrected_flux = initial_flux + counterflow
        corrected_edge_rows.append(
            {
                "stress_edge_id": edge_id,
                "source_atom": edge["source_atom"],
                "target_atom": edge["target_atom"],
                "initial_flux_scaled": initial_flux,
                "counterflow_scaled": counterflow,
                "corrected_flux_scaled": corrected_flux,
                "edge_used_initial_flag": int(initial_flux != 0),
                "edge_used_counterflow_flag": int(counterflow != 0),
                "edge_used_corrected_flag": int(corrected_flux != 0),
            }
        )

    counterflow_out = {atom: 0 for atom in range(20)}
    counterflow_in = {atom: 0 for atom in range(20)}
    for row in counterflow_rows:
        counterflow_out[row["source_atom"]] += row["counterflow_scaled"]
        counterflow_in[row["target_atom"]] += row["counterflow_scaled"]

    corrected_node_rows = []
    for row in sorted(node_balance_rows_source, key=lambda row: row["atom_id"]):
        atom = row["atom_id"]
        counter_out = counterflow_out[atom]
        counter_in = counterflow_in[atom]
        counter_divergence = counter_out - counter_in
        corrected_divergence = row["divergence_scaled"] + counter_divergence
        corrected_abs = abs(corrected_divergence)
        corrected_node_rows.append(
            {
                "atom_id": atom,
                "initial_outgoing_flux_scaled": row["outgoing_flux_scaled"],
                "initial_incoming_flux_scaled": row["incoming_flux_scaled"],
                "initial_divergence_scaled": row["divergence_scaled"],
                "counterflow_outgoing_scaled": counter_out,
                "counterflow_incoming_scaled": counter_in,
                "counterflow_divergence_scaled": counter_divergence,
                "corrected_divergence_scaled": corrected_divergence,
                "corrected_abs_divergence_scaled": corrected_abs,
                "corrected_local_conserved_flag": int(corrected_divergence == 0),
            }
        )

    dual_potential_rows = []
    for atom, balance in enumerate(balances):
        potential = dual_potentials[atom]
        dual_potential_rows.append(
            {
                "atom_id": atom,
                "balance_scaled": balance,
                "dual_potential": potential,
                "dual_contribution_scaled": balance * potential,
            }
        )

    initial_total_abs_defect = sum(
        abs(row["divergence_scaled"]) for row in node_balance_rows_source
    )
    supply_total = sum(max(value, 0) for value in balances)
    demand_total = -sum(min(value, 0) for value in balances)
    primal_cost = sum(row["cost_scaled"] for row in counterflow_rows)
    dual_bound = sum(row["dual_contribution_scaled"] for row in dual_potential_rows)
    corrected_total_abs_defect = sum(
        row["corrected_abs_divergence_scaled"] for row in corrected_node_rows
    )
    corrected_max_abs_defect = max(
        row["corrected_abs_divergence_scaled"] for row in corrected_node_rows
    )
    corrected_defect_node_count = sum(
        row["corrected_abs_divergence_scaled"] != 0 for row in corrected_node_rows
    )
    corrected_local_conserved_node_count = sum(
        row["corrected_local_conserved_flag"] for row in corrected_node_rows
    )
    corrected_global_divergence = sum(
        row["corrected_divergence_scaled"] for row in corrected_node_rows
    )
    obs = {
        "input_report_count": 2,
        "input_certified_count": int(certified(c59e)) + int(certified(stress_gate)),
        "stress_node_count": len(node_balance_rows_source),
        "stress_directed_edge_count": len(stress_edges),
        "initial_defect_node_count": sum(
            row["divergence_scaled"] != 0 for row in node_balance_rows_source
        ),
        "initial_total_abs_defect_scaled": initial_total_abs_defect,
        "supply_node_count": sum(value > 0 for value in balances),
        "demand_node_count": sum(value < 0 for value in balances),
        "supply_total_scaled": supply_total,
        "demand_total_scaled": demand_total,
        "counterflow_row_count": len(counterflow_rows),
        "counterflow_used_edge_count": len(counterflow_rows),
        "counterflow_total_scaled": sum(
            row["counterflow_scaled"] for row in counterflow_rows
        ),
        "counterflow_cost_scaled": primal_cost,
        "primal_cost_scaled": routed_cost,
        "dual_bound_scaled": dual_bound,
        "primal_dual_gap_scaled": routed_cost - dual_bound,
        "dual_feasible_flag": int(
            all(row["dual_feasible_flag"] == 1 for row in dual_edge_rows)
        ),
        "complementary_slackness_flag": int(
            all(row["complementary_slackness_flag"] == 1 for row in dual_edge_rows)
        ),
        "minimal_counterflow_flag": int(
            routed_flow == supply_total
            and routed_cost == primal_cost
            and routed_cost == dual_bound
            and all(row["dual_feasible_flag"] == 1 for row in dual_edge_rows)
            and all(
                row["complementary_slackness_flag"] == 1 for row in dual_edge_rows
            )
        ),
        "corrected_local_conserved_node_count": corrected_local_conserved_node_count,
        "corrected_defect_node_count": corrected_defect_node_count,
        "corrected_total_abs_defect_scaled": corrected_total_abs_defect,
        "corrected_max_abs_defect_scaled": corrected_max_abs_defect,
        "corrected_global_divergence_scaled": corrected_global_divergence,
        "corrected_local_conservation_flag": int(
            corrected_local_conserved_node_count == len(corrected_node_rows)
            and corrected_total_abs_defect == 0
        ),
        "finite_conserved_edge_current_flag": int(corrected_total_abs_defect == 0),
        "physical_stress_energy_flag": 0,
        "smooth_metric_flag": 0,
        "thermal_gravity_flag": 0,
        "next_gap_code": GAP_CODES["finite_stress_tensor_lift"],
    }
    gap_rows = [
        {
            "gap_id": GAP_CODES["counterflow_materialized"],
            "gap_code": GAP_CODES["counterflow_materialized"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["corrected_local_conservation"],
            "gap_code": GAP_CODES["corrected_local_conservation"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["minimality_dual_certificate"],
            "gap_code": GAP_CODES["minimality_dual_certificate"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["finite_conserved_edge_current"],
            "gap_code": GAP_CODES["finite_conserved_edge_current"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["finite_stress_tensor_lift"],
            "gap_code": GAP_CODES["finite_stress_tensor_lift"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 0,
            "next_flag": 1,
        },
        {
            "gap_id": GAP_CODES["smooth_lorentzian_metric"],
            "gap_code": GAP_CODES["smooth_lorentzian_metric"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["thermal_gravity_derivation"],
            "gap_code": GAP_CODES["thermal_gravity_derivation"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
    ]
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": obs[name],
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    return {
        "c59e": c59e,
        "stress_gate": stress_gate,
        "counterflow_rows": counterflow_rows,
        "corrected_edge_rows": corrected_edge_rows,
        "corrected_node_rows": corrected_node_rows,
        "dual_potential_rows": dual_potential_rows,
        "dual_edge_rows": dual_edge_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    counterflow_table = table_from_rows(COUNTERFLOW_COLUMNS, rows["counterflow_rows"])
    corrected_edge_table = table_from_rows(
        CORRECTED_EDGE_COLUMNS, rows["corrected_edge_rows"]
    )
    corrected_node_table = table_from_rows(
        CORRECTED_NODE_COLUMNS, rows["corrected_node_rows"]
    )
    dual_potential_table = table_from_rows(
        DUAL_POTENTIAL_COLUMNS, rows["dual_potential_rows"]
    )
    dual_edge_table = table_from_rows(DUAL_EDGE_COLUMNS, rows["dual_edge_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "counterflow_materialized_on_existing_edges": obs["counterflow_row_count"] > 0
        and obs["counterflow_row_count"] == obs["counterflow_used_edge_count"]
        and all(row["existing_edge_flag"] == 1 for row in rows["counterflow_rows"]),
        "counterflow_balances_initial_defect": obs["supply_total_scaled"]
        == obs["demand_total_scaled"]
        and obs["counterflow_total_scaled"] == obs["supply_total_scaled"]
        and all(
            row["counterflow_divergence_scaled"]
            == -row["initial_divergence_scaled"]
            for row in rows["corrected_node_rows"]
        ),
        "corrected_local_conservation_exact": obs[
            "corrected_local_conservation_flag"
        ]
        == 1
        and obs["corrected_local_conserved_node_count"] == 20
        and obs["corrected_defect_node_count"] == 0
        and obs["corrected_total_abs_defect_scaled"] == 0
        and obs["corrected_global_divergence_scaled"] == 0,
        "minimality_dual_certificate": obs["dual_feasible_flag"] == 1
        and obs["complementary_slackness_flag"] == 1
        and obs["minimal_counterflow_flag"] == 1
        and obs["primal_dual_gap_scaled"] == 0,
        "physical_metric_boundaries_preserved": obs[
            "finite_conserved_edge_current_flag"
        ]
        == 1
        and obs["physical_stress_energy_flag"] == 0
        and obs["smooth_metric_flag"] == 0
        and obs["thermal_gravity_flag"] == 0,
        "table_shapes_match": counterflow_table.shape[1]
        == len(COUNTERFLOW_COLUMNS)
        and counterflow_table.shape[0] == obs["counterflow_row_count"]
        and corrected_edge_table.shape == (100, len(CORRECTED_EDGE_COLUMNS))
        and corrected_node_table.shape == (20, len(CORRECTED_NODE_COLUMNS))
        and dual_potential_table.shape == (20, len(DUAL_POTENTIAL_COLUMNS))
        and dual_edge_table.shape == (100, len(DUAL_EDGE_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "c59x_minimal_counterflow",
        "objective": "minimize unit directed-edge hop mass over existing stress edges",
        "summary": {
            "stress_directed_edge_count": obs["stress_directed_edge_count"],
            "initial_defect_node_count": obs["initial_defect_node_count"],
            "initial_total_abs_defect_scaled": obs[
                "initial_total_abs_defect_scaled"
            ],
            "supply_total_scaled": obs["supply_total_scaled"],
            "demand_total_scaled": obs["demand_total_scaled"],
            "counterflow_row_count": obs["counterflow_row_count"],
            "counterflow_total_scaled": obs["counterflow_total_scaled"],
            "primal_cost_scaled": obs["primal_cost_scaled"],
            "dual_bound_scaled": obs["dual_bound_scaled"],
            "primal_dual_gap_scaled": obs["primal_dual_gap_scaled"],
            "minimal_counterflow_flag": obs["minimal_counterflow_flag"],
            "corrected_local_conserved_node_count": obs[
                "corrected_local_conserved_node_count"
            ],
            "corrected_defect_node_count": obs["corrected_defect_node_count"],
            "corrected_total_abs_defect_scaled": obs[
                "corrected_total_abs_defect_scaled"
            ],
            "corrected_global_divergence_scaled": obs[
                "corrected_global_divergence_scaled"
            ],
            "finite_conserved_edge_current_flag": obs[
                "finite_conserved_edge_current_flag"
            ],
            "physical_stress_energy_flag": obs["physical_stress_energy_flag"],
            "smooth_metric_flag": obs["smooth_metric_flag"],
            "thermal_gravity_flag": obs["thermal_gravity_flag"],
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "counterflow_table_sha256": sha_array(counterflow_table),
        "counterflow_text_sha256": sha_text(
            csv_text(COUNTERFLOW_COLUMNS, rows["counterflow_rows"])
        ),
        "corrected_edge_table_sha256": sha_array(corrected_edge_table),
        "corrected_node_table_sha256": sha_array(corrected_node_table),
        "dual_potential_table_sha256": sha_array(dual_potential_table),
        "dual_edge_table_sha256": sha_array(dual_edge_table),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    c59cf = {
        "schema": "long.c59cf@1",
        "object": "c59x_minimal_counterflow",
        "status": STATUS if all(checks.values()) else "LONG_C59CF_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.c59cf.report@1",
        "status": c59cf["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_c59cf cancels the finite local defect from long_c59e by "
            "adding a nonnegative counterflow on existing directed stress edges. "
            "The unit-edge objective is minimal by a primal-dual certificate. "
            "This certifies a finite conserved edge current, not a physical "
            "stress-energy tensor, smooth metric, or thermal-gravity derivation."
        ),
        "stage_protocol": {
            "draft": "read long_c59e node defects and directed stress edges",
            "witness": "emit counterflow rows, corrected edge/node balances, dual potentials, dual edge slacks, gaps, and observables",
            "coherence": "check existing-edge support, node cancellation, primal-dual minimality, and physical exclusions",
            "closure": "certify finite minimal counterflow and corrected local conservation",
            "emit": "write long_c59cf artifacts and verifier hook",
        },
        "inputs": {
            "long_c59e": input_entry(
                LONG_C59E,
                {
                    "status": rows["c59e"].get("status"),
                    "certificate_sha256": rows["c59e"].get("certificate_sha256"),
                },
            ),
            "long_c59e_edge_flux": input_entry(LONG_C59E_EDGE_FLUX),
            "long_c59e_node_balance": input_entry(LONG_C59E_NODE_BALANCE),
            "long_stress_gate": input_entry(
                LONG_STRESS_GATE,
                {
                    "status": rows["stress_gate"].get("status"),
                    "certificate_sha256": rows["stress_gate"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_stress_edge": input_entry(LONG_STRESS_EDGE),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "c59cf": relpath(OUT_DIR / "c59cf.json"),
            "counterflow_csv": relpath(OUT_DIR / "counterflow.csv"),
            "corrected_edge_csv": relpath(OUT_DIR / "corrected_edge.csv"),
            "corrected_node_csv": relpath(OUT_DIR / "corrected_node.csv"),
            "dual_potential_csv": relpath(OUT_DIR / "dual_potential.csv"),
            "dual_edge_csv": relpath(OUT_DIR / "dual_edge.csv"),
            "gap_csv": relpath(OUT_DIR / "gap.csv"),
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
                "a nonnegative counterflow on existing directed stress edges",
                "exact cancellation of all 20 local node defects from long_c59e",
                "unit-edge minimality by primal cost, dual bound, zero gap, and complementary slackness",
                "a finite conserved directed-edge current",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "a finite stress-tensor lift from the conserved edge current",
                "a physical stress-energy tensor",
                "a smooth Lorentzian metric",
                "curvature, Einstein tensor, or field equations",
                "a thermal-gravity derivation",
            ],
        },
        "next_highest_yield_item": (
            "Lift the conserved finite edge current into an explicit symmetric "
            "node-pair stress tensor candidate, then run the rank/signature "
            "metric gate against that tensor."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.c59cf.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.c59cf.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "c59cf": c59cf,
        "counterflow_csv": csv_text(COUNTERFLOW_COLUMNS, rows["counterflow_rows"]),
        "corrected_edge_csv": csv_text(
            CORRECTED_EDGE_COLUMNS, rows["corrected_edge_rows"]
        ),
        "corrected_node_csv": csv_text(
            CORRECTED_NODE_COLUMNS, rows["corrected_node_rows"]
        ),
        "dual_potential_csv": csv_text(
            DUAL_POTENTIAL_COLUMNS, rows["dual_potential_rows"]
        ),
        "dual_edge_csv": csv_text(DUAL_EDGE_COLUMNS, rows["dual_edge_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "counterflow_table": counterflow_table,
        "corrected_edge_table": corrected_edge_table,
        "corrected_node_table": corrected_node_table,
        "dual_potential_table": dual_potential_table,
        "dual_edge_table": dual_edge_table,
        "gap_table": gap_table,
        "observable_table": observable_table,
        "cert": cert,
        "manifest": manifest,
        "report": report,
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
    write_json(OUT_DIR / "c59cf.json", payloads["c59cf"])
    (OUT_DIR / "counterflow.csv").write_text(
        payloads["counterflow_csv"], encoding="utf-8"
    )
    (OUT_DIR / "corrected_edge.csv").write_text(
        payloads["corrected_edge_csv"], encoding="utf-8"
    )
    (OUT_DIR / "corrected_node.csv").write_text(
        payloads["corrected_node_csv"], encoding="utf-8"
    )
    (OUT_DIR / "dual_potential.csv").write_text(
        payloads["dual_potential_csv"], encoding="utf-8"
    )
    (OUT_DIR / "dual_edge.csv").write_text(
        payloads["dual_edge_csv"], encoding="utf-8"
    )
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        counterflow_table=payloads["counterflow_table"],
        corrected_edge_table=payloads["corrected_edge_table"],
        corrected_node_table=payloads["corrected_node_table"],
        dual_potential_table=payloads["dual_potential_table"],
        dual_edge_table=payloads["dual_edge_table"],
        gap_table=payloads["gap_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(OUT_DIR / "cert.json", payloads["cert"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    write_json(OUT_DIR / "report.json", payloads["report"])
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
                "summary": report["witness"]["summary"],
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
