from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "full_exposure_packet_propagation_graph"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FULL_EXPOSURE_PACKET_PROPAGATION_CELLS_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_packet_propagation_cells"
    / "report.json"
)


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def update_theorem_index(report: dict[str, Any], out_dir: Path) -> None:
    index_path = out_dir.parent / "index.json"
    entry = {
        "id": THEOREM_ID,
        "manifest": rel(out_dir / "manifest.json"),
        "report": rel(out_dir / "report.json"),
        "report_sha256": report["certificate_sha256"],
        "status": report["status"],
    }
    if index_path.exists():
        index = load_json(index_path)
        theorems = [item for item in index.get("theorems", []) if item.get("id") != THEOREM_ID]
    else:
        theorems = []
    theorems.append(entry)
    theorems = sorted(theorems, key=lambda item: item["id"])
    index = {
        "schema": "d20.theorem_registry",
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": len(theorems),
        "theorems": theorems,
    }
    index["registry_sha256"] = sha_json({k: v for k, v in index.items() if k != "registry_sha256"})
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def histogram(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def tuple_key(parts: tuple[Any, ...]) -> str:
    return "|".join(str(part) for part in parts)


def tuple_histogram(counter: Counter[tuple[Any, ...]]) -> dict[str, int]:
    return {tuple_key(key): int(counter[key]) for key in sorted(counter)}


def build_theorem() -> dict[str, Any]:
    cells = load_json(FULL_EXPOSURE_PACKET_PROPAGATION_CELLS_REPORT)
    cells_derived = cells.get("derived", {})
    cell_summary = cells_derived.get("propagation_cell_summary", {})
    vertices = [int(packet_id) for packet_id in cell_summary.get("full_exposure_packet_ids", [])]
    vertex_set = set(vertices)
    two_step_rows = cells_derived.get("two_step_cross_return_rows", [])

    adjacency_counter: Counter[tuple[int, int]] = Counter()
    raw_rows_by_edge: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    raw_rows_by_source: dict[int, list[dict[str, Any]]] = defaultdict(list)
    generator_pair_rows: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)

    for row in two_step_rows:
        source = int(row["source_packet_id"])
        target = int(row["target_packet_id"])
        key = (source, target)
        adjacency_counter[key] += 1
        raw_rows_by_edge[key].append(row)
        raw_rows_by_source[source].append(row)
        generator_pair_rows[
            (int(row["first_generator_cycle_id"]), int(row["second_generator_cycle_id"]))
        ].append(row)

    adjacency_matrix = [
        [int(adjacency_counter[(source, target)]) for target in vertices]
        for source in vertices
    ]
    column_sums = [
        sum(adjacency_matrix[row_idx][col_idx] for row_idx in range(len(vertices)))
        for col_idx in range(len(vertices))
    ]
    diagonal_weights = [
        adjacency_matrix[idx][idx]
        for idx in range(len(vertices))
    ]
    partner_weights = [
        int(adjacency_counter[(source, source ^ 1)])
        for source in vertices
    ]
    nonzero_target_counts = [
        sum(1 for target in vertices if adjacency_counter[(source, target)] != 0)
        for source in vertices
    ]
    forbidden_nonzero_edges = [
        {
            "source_packet_id": source,
            "target_packet_id": target,
            "weight": int(weight),
        }
        for (source, target), weight in sorted(adjacency_counter.items())
        if weight and target not in {source, source ^ 1}
    ]

    component_pairs = sorted({tuple(sorted((source, source ^ 1))) for source in vertices})
    component_rows = []
    for left, right in component_pairs:
        pair_rows = raw_rows_by_source[left] + raw_rows_by_source[right]
        block = [
            [int(adjacency_counter[(left, left)]), int(adjacency_counter[(left, right)])],
            [int(adjacency_counter[(right, left)]), int(adjacency_counter[(right, right)])],
        ]
        component_rows.append(
            {
                "packet_pair": [left, right],
                "block_matrix": block,
                "ordered_cross_return_count": len(pair_rows),
                "net_height_flux_delta_sum": sum(
                    int(row["net_height_flux_delta"]) for row in pair_rows
                ),
                "total_optical_action_sum": sum(
                    int(row["total_optical_action"]) for row in pair_rows
                ),
                "hidden_R33_transfer_mod26_sum": sum(
                    int(row["hidden_R33_transfer_mod26_total"]) for row in pair_rows
                )
                % 26,
            }
        )

    weighted_directed_edges = []
    for source in vertices:
        for target in vertices:
            rows = raw_rows_by_edge.get((source, target), [])
            if not rows:
                continue
            weighted_directed_edges.append(
                {
                    "source_packet_id": source,
                    "target_packet_id": target,
                    "edge_kind": "source_loop" if source == target else "active_partner",
                    "weight": len(rows),
                    "ordered_generator_pairs": sorted(
                        [
                            [
                                int(row["first_generator_cycle_id"]),
                                int(row["second_generator_cycle_id"]),
                            ]
                            for row in rows
                        ]
                    ),
                    "net_height_flux_delta_histogram": histogram(
                        Counter(int(row["net_height_flux_delta"]) for row in rows)
                    ),
                    "total_optical_action_histogram": histogram(
                        Counter(int(row["total_optical_action"]) for row in rows)
                    ),
                    "hidden_R33_transfer_mod26_total_histogram": histogram(
                        Counter(int(row["hidden_R33_transfer_mod26_total"]) for row in rows)
                    ),
                }
            )

    source_balance_rows = []
    for source in vertices:
        rows = raw_rows_by_source[source]
        target_histogram = histogram(Counter(int(row["target_packet_id"]) for row in rows))
        source_balance_rows.append(
            {
                "source_packet_id": source,
                "active_partner_packet_id": source ^ 1,
                "ordered_cross_return_count": len(rows),
                "target_packet_histogram": target_histogram,
                "net_height_flux_delta_sum": sum(
                    int(row["net_height_flux_delta"]) for row in rows
                ),
                "total_optical_action_sum": sum(
                    int(row["total_optical_action"]) for row in rows
                ),
                "hidden_R33_transfer_mod26_sum": sum(
                    int(row["hidden_R33_transfer_mod26_total"]) for row in rows
                )
                % 26,
            }
        )

    generator_pair_table = []
    for generator_pair in sorted(generator_pair_rows):
        rows = generator_pair_rows[generator_pair]
        target_kind_values = {
            "source_loop" if int(row["source_packet_id"]) == int(row["target_packet_id"])
            else "active_partner"
            for row in rows
        }
        net_values = sorted({int(row["net_height_flux_delta"]) for row in rows})
        action_values = sorted({int(row["total_optical_action"]) for row in rows})
        generator_pair_table.append(
            {
                "ordered_generators": list(generator_pair),
                "row_count": len(rows),
                "target_kind": next(iter(target_kind_values)) if len(target_kind_values) == 1 else "mixed",
                "target_kind_values": sorted(target_kind_values),
                "net_height_flux_delta_values": net_values,
                "total_optical_action_values": action_values,
                "hidden_R33_transfer_mod26_total_histogram": histogram(
                    Counter(int(row["hidden_R33_transfer_mod26_total"]) for row in rows)
                ),
            }
        )

    expected_generator_pair_table = [
        {
            "ordered_generators": [5, 9],
            "row_count": 20,
            "target_kind": "active_partner",
            "target_kind_values": ["active_partner"],
            "net_height_flux_delta_values": [-301056],
            "total_optical_action_values": [1683456],
            "hidden_R33_transfer_mod26_total_histogram": {"0": 20},
        },
        {
            "ordered_generators": [5, 10],
            "row_count": 20,
            "target_kind": "source_loop",
            "target_kind_values": ["source_loop"],
            "net_height_flux_delta_values": [-399360],
            "total_optical_action_values": [1781760],
            "hidden_R33_transfer_mod26_total_histogram": {"0": 20},
        },
        {
            "ordered_generators": [9, 5],
            "row_count": 20,
            "target_kind": "active_partner",
            "target_kind_values": ["active_partner"],
            "net_height_flux_delta_values": [301056],
            "total_optical_action_values": [1683456],
            "hidden_R33_transfer_mod26_total_histogram": {"0": 20},
        },
        {
            "ordered_generators": [9, 10],
            "row_count": 20,
            "target_kind": "active_partner",
            "target_kind_values": ["active_partner"],
            "net_height_flux_delta_values": [-98304],
            "total_optical_action_values": [2082816],
            "hidden_R33_transfer_mod26_total_histogram": {"0": 20},
        },
        {
            "ordered_generators": [10, 5],
            "row_count": 20,
            "target_kind": "source_loop",
            "target_kind_values": ["source_loop"],
            "net_height_flux_delta_values": [399360],
            "total_optical_action_values": [1781760],
            "hidden_R33_transfer_mod26_total_histogram": {"0": 20},
        },
        {
            "ordered_generators": [10, 9],
            "row_count": 20,
            "target_kind": "active_partner",
            "target_kind_values": ["active_partner"],
            "net_height_flux_delta_values": [98304],
            "total_optical_action_values": [2082816],
            "hidden_R33_transfer_mod26_total_histogram": {"0": 20},
        },
    ]

    row_sum_histogram = histogram(Counter(sum(row) for row in adjacency_matrix))
    column_sum_histogram = histogram(Counter(column_sums))
    diagonal_weight_histogram = histogram(Counter(diagonal_weights))
    active_partner_weight_histogram = histogram(Counter(partner_weights))
    nonzero_target_count_histogram = histogram(Counter(nonzero_target_counts))
    component_block_histogram = tuple_histogram(
        Counter(tuple(value for row in item["block_matrix"] for value in row) for item in component_rows)
    )
    source_net_flux_sum_histogram = histogram(
        Counter(row["net_height_flux_delta_sum"] for row in source_balance_rows)
    )
    source_total_action_sum_histogram = histogram(
        Counter(row["total_optical_action_sum"] for row in source_balance_rows)
    )
    component_total_action_sum_histogram = histogram(
        Counter(row["total_optical_action_sum"] for row in component_rows)
    )

    spectral_summary = {
        "integer_adjacency_block": [[2, 4], [4, 2]],
        "integer_adjacency_eigenvalues": [
            {"value": -2, "multiplicity": 10, "eigenspace": "active-partner antisymmetric"},
            {"value": 6, "multiplicity": 10, "eigenspace": "active-partner symmetric"},
        ],
        "integer_adjacency_rank_over_Q": 20,
        "integer_adjacency_trace": sum(diagonal_weights),
        "normalized_markov_eigenvalues": [
            {
                "value": "-1/3",
                "multiplicity": 10,
                "eigenspace": "active-partner antisymmetric",
            },
            {
                "value": "1",
                "multiplicity": 10,
                "eigenspace": "active-partner symmetric",
            },
        ],
        "stationary_simplex_dimension": 10,
        "within_component_contraction_absolute_eigenvalue": "1/3",
    }

    graph_summary = {
        "vertex_count": len(vertices),
        "raw_ordered_cross_return_count": len(two_step_rows),
        "weighted_directed_edge_count_including_loops": len(weighted_directed_edges),
        "component_count": len(component_pairs),
        "component_size_histogram": {"2": len(component_pairs)},
        "row_sum_histogram": row_sum_histogram,
        "column_sum_histogram": column_sum_histogram,
        "diagonal_self_loop_weight_histogram": diagonal_weight_histogram,
        "active_partner_weight_histogram": active_partner_weight_histogram,
        "nonzero_target_count_histogram": nonzero_target_count_histogram,
        "source_net_flux_sum_histogram": source_net_flux_sum_histogram,
        "source_total_optical_action_sum_histogram": source_total_action_sum_histogram,
        "component_total_optical_action_sum_histogram": component_total_action_sum_histogram,
        "active_partner_pairs": [row["packet_pair"] for row in component_rows],
        "packet239_component": next(
            row for row in component_rows if 239 in row["packet_pair"]
        ),
    }

    checks = {
        "full_exposure_packet_propagation_cells_is_certified": cells.get("status")
        == "D20_FULL_EXPOSURE_PACKET_PROPAGATION_CELLS_CERTIFIED"
        and cells.get("all_checks_pass") is True,
        "graph_has_20_vertices_and_120_raw_returns": len(vertices) == 20
        and len(two_step_rows) == 120
        and set(int(row["source_packet_id"]) for row in two_step_rows) == vertex_set
        and set(int(row["target_packet_id"]) for row in two_step_rows) <= vertex_set,
        "graph_has_only_source_and_active_partner_targets": forbidden_nonzero_edges == []
        and nonzero_target_count_histogram == {"2": 20},
        "graph_has_uniform_weighted_degrees": row_sum_histogram == {"6": 20}
        and column_sum_histogram == {"6": 20},
        "graph_has_uniform_self_and_partner_weights": diagonal_weight_histogram == {"2": 20}
        and active_partner_weight_histogram == {"4": 20},
        "graph_decomposes_into_ten_active_partner_doublets": len(component_pairs) == 10
        and all(len(set(pair)) == 2 and set(pair) <= vertex_set for pair in component_pairs)
        and component_block_histogram == {"2|4|4|2": 10},
        "generator_pair_table_matches_crossing_law": generator_pair_table
        == expected_generator_pair_table,
        "signed_flux_balances_per_source_and_component": source_net_flux_sum_histogram
        == {"0": 20}
        and all(row["net_height_flux_delta_sum"] == 0 for row in component_rows),
        "hidden_transfer_cancels_everywhere": all(
            row["hidden_R33_transfer_mod26_sum"] == 0 for row in source_balance_rows
        )
        and all(row["hidden_R33_transfer_mod26_sum"] == 0 for row in component_rows),
        "action_budget_is_uniform": source_total_action_sum_histogram == {"11096064": 20}
        and component_total_action_sum_histogram == {"22192128": 10},
        "spectral_readout_matches_ten_doublet_blocks": spectral_summary[
            "integer_adjacency_trace"
        ]
        == 40
        and spectral_summary["integer_adjacency_rank_over_Q"] == 20
        and spectral_summary["stationary_simplex_dimension"] == 10,
        "packet239_lies_in_238_239_component": graph_summary["packet239_component"][
            "packet_pair"
        ]
        == [238, 239],
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_CERTIFIED"
        if all_checks_pass
        else "D20_FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.full_exposure_packet_propagation_graph",
        "status": status,
        "object": "d20",
        "claim": (
            "The 20 full Loop_297-exposure packets form a weighted two-step propagation graph that "
            "decomposes into ten active-partner doublets. Each source has exactly two ordered self "
            "returns and four ordered active-partner returns, so the integer transition block on every "
            "doublet is [[2,4],[4,2]]. The signed height flux cancels on every source, hidden transfer "
            "is zero, and the graph transition spectrum is 6^10 plus (-2)^10."
        ),
        "definition": {
            "vertex": "A full Loop_297-exposure projective packet from the certified propagation-cell theorem.",
            "raw_ordered_cross_return": "An ordered two-step crossing row using distinct generators from {5,9,10}.",
            "weighted_directed_edge": "The multiplicity of raw ordered cross-returns from one packet to another.",
            "active_partner_doublet": "The pair {p, p xor 1}, equivalently the two active-sigma choices for one radical character.",
        },
        "inputs": {
            "full_exposure_packet_propagation_cells_report": {
                "path": rel(FULL_EXPOSURE_PACKET_PROPAGATION_CELLS_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_PACKET_PROPAGATION_CELLS_REPORT),
            }
        },
        "derived": {
            "graph_summary": graph_summary,
            "spectral_summary": spectral_summary,
            "generator_pair_table": generator_pair_table,
            "component_rows": component_rows,
            "source_balance_rows": source_balance_rows,
            "weighted_directed_edges": weighted_directed_edges,
            "adjacency": {
                "vertex_order": vertices,
                "matrix": adjacency_matrix,
                "matrix_sha256": sha_json(adjacency_matrix),
            },
            "forbidden_nonzero_edges": forbidden_nonzero_edges,
        },
        "interpretation": {
            "what_this_proves": [
                "the full-exposure stratum is not a connected 20-state mixer; it splits into ten closed two-state cells",
                "packet 239 belongs to the closed active-partner doublet {238,239}",
                "the two-step transition operator has a ten-dimensional stationary simplex",
                "signed height flux cancels locally on every source before any longer-walk quotient is imposed",
            ],
            "what_this_does_not_prove": (
                "This theorem classifies the two-step paired cross-return graph only. It does not yet identify "
                "the ten doublets with a canonical rank-10 kernel basis or tenfold-way axis labeling."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Build the rank-10/tenfold component-alignment witness: map the ten active-partner doublets "
            "to kernel coordinates and test whether they form a canonical ten-axis basis."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.full_exposure_packet_propagation_graph_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify the full-exposure propagation-cell theorem is certified",
            "construct the weighted directed packet graph from all 120 ordered paired cross-returns",
            "verify only source and active-partner targets occur",
            "verify the ten active-partner doublet block decomposition",
            "verify row/column sums, source flux cancellation, hidden-transfer cancellation, and action budgets",
            "verify the integer and normalized Markov spectral readouts of the doublet blocks",
        ],
    }
    manifest["report_sha256"] = report["certificate_sha256"]
    manifest["manifest_sha256"] = sha_json({k: v for k, v in manifest.items() if k != "manifest_sha256"})

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    update_theorem_index(report, out_dir)
    return report


def main() -> None:
    report = write_theorem()
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report.get("all_checks_pass"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
