from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "full_exposure_label_coordinate_transition_operator"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FULL_EXPOSURE_CANONICAL_LABELLED_FRAME_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_canonical_labelled_frame"
    / "report.json"
)
FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_packet_propagation_graph"
    / "report.json"
)
FULL_EXPOSURE_PACKET_PROPAGATION_CELLS_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_packet_propagation_cells"
    / "report.json"
)


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


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


def label_coordinate(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "frame_index": row["frame_index"],
        "canonical_frame_key_sha256": sha_json(row["canonical_frame_key"]),
        "canonical_frame_key": row["canonical_frame_key"],
        "mass_frame": row["mass_frame"],
        "clock_frame": row["clock_frame"],
        "gamma_frame": row["gamma_frame"],
        "sector26_clock_pair": row["sector26_clock_pair"],
        "sector26_clock_sum_mod26": row["sector26_clock_sum_mod26"],
        "sector26_clock_delta_mod26": row["sector26_clock_delta_mod26"],
        "sector26_clock_zero_pair": row["sector26_clock_zero_pair"],
        "sector26_clock_zero_touched": row["sector26_clock_zero_touched"],
        "fine_spectral_charge_key": row["fine_spectral_charge_key"],
        "charge_frame_key": row["charge_frame_key"],
    }


def build_label_transition_rows(
    frame_rows: list[dict[str, Any]],
    weighted_edges: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    frame_by_packet = {int(row["packet_id"]): row for row in frame_rows}
    rows = []
    for edge_id, edge in enumerate(weighted_edges):
        source_packet = int(edge["source_packet_id"])
        target_packet = int(edge["target_packet_id"])
        source = frame_by_packet[source_packet]
        target = frame_by_packet[target_packet]
        rows.append(
            {
                "edge_id": edge_id,
                "edge_kind": edge["edge_kind"],
                "weight": int(edge["weight"]),
                "source": label_coordinate(source),
                "target": label_coordinate(target),
                "ordered_generator_pairs": edge["ordered_generator_pairs"],
                "net_height_flux_delta_histogram": edge["net_height_flux_delta_histogram"],
                "total_optical_action_histogram": edge["total_optical_action_histogram"],
                "hidden_R33_transfer_mod26_total_histogram": edge[
                    "hidden_R33_transfer_mod26_total_histogram"
                ],
                "witness_packet_edge": {
                    "source_packet_id": source_packet,
                    "target_packet_id": target_packet,
                },
            }
        )
    return rows


def build_component_coordinate_rows(
    frame_rows: list[dict[str, Any]],
    component_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    frame_by_packet = {int(row["packet_id"]): row for row in frame_rows}
    rows = []
    for component_id, component in enumerate(component_rows):
        packets = [int(packet) for packet in component["packet_pair"]]
        coordinates = [label_coordinate(frame_by_packet[packet]) for packet in packets]
        rows.append(
            {
                "component_id": component_id,
                "frame_indices": [coord["frame_index"] for coord in coordinates],
                "coordinate_key_sha256_pair": [
                    coord["canonical_frame_key_sha256"] for coord in coordinates
                ],
                "coordinates": coordinates,
                "block_matrix": component["block_matrix"],
                "ordered_cross_return_count": component["ordered_cross_return_count"],
                "net_height_flux_delta_sum": component["net_height_flux_delta_sum"],
                "hidden_R33_transfer_mod26_sum": component[
                    "hidden_R33_transfer_mod26_sum"
                ],
                "total_optical_action_sum": component["total_optical_action_sum"],
                "witness_packet_pair": packets,
            }
        )
    return rows


def histogram(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def build_theorem() -> dict[str, Any]:
    frame = load_json(FULL_EXPOSURE_CANONICAL_LABELLED_FRAME_REPORT)
    graph = load_json(FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_REPORT)
    cells = load_json(FULL_EXPOSURE_PACKET_PROPAGATION_CELLS_REPORT)

    frame_rows = frame.get("derived", {}).get("canonical_frame_rows", [])
    weighted_edges = graph.get("derived", {}).get("weighted_directed_edges", [])
    component_rows = graph.get("derived", {}).get("component_rows", [])
    label_transition_rows = build_label_transition_rows(frame_rows, weighted_edges)
    component_coordinate_rows = build_component_coordinate_rows(frame_rows, component_rows)

    row_sums: dict[str, int] = defaultdict(int)
    target_counts: dict[str, set[str]] = defaultdict(set)
    for row in label_transition_rows:
        source_key = row["source"]["canonical_frame_key_sha256"]
        target_key = row["target"]["canonical_frame_key_sha256"]
        row_sums[source_key] += int(row["weight"])
        target_counts[source_key].add(target_key)

    zero_pair_rows = [
        row
        for row in label_transition_rows
        if row["source"]["sector26_clock_zero_pair"]
        and row["source"]["sector26_clock_zero_touched"]
    ]
    transition_summary = {
        "coordinate_count": len(frame_rows),
        "label_transition_edge_count": len(label_transition_rows),
        "component_count": len(component_coordinate_rows),
        "edge_kind_weight_histogram": histogram(
            Counter(f"{row['edge_kind']}|{row['weight']}" for row in label_transition_rows)
        ),
        "row_sum_histogram": histogram(Counter(row_sums.values())),
        "target_count_per_source_histogram": histogram(
            Counter(len(value) for value in target_counts.values())
        ),
        "component_block_histogram": histogram(
            Counter(json.dumps(row["block_matrix"]) for row in component_coordinate_rows)
        ),
        "hidden_transfer_histogram_by_edge": histogram(
            Counter(
                json.dumps(row["hidden_R33_transfer_mod26_total_histogram"], sort_keys=True)
                for row in label_transition_rows
            )
        ),
        "zero_pair_source_transition_rows": zero_pair_rows,
    }

    zero_pair_target_weights = {
        row["edge_kind"]: {
            "weight": row["weight"],
            "target_frame_index": row["target"]["frame_index"],
            "target_clock_frame": row["target"]["clock_frame"],
            "target_sector26_clock_sum_mod26": row["target"]["sector26_clock_sum_mod26"],
            "target_fine_spectral_charge_key": row["target"]["fine_spectral_charge_key"],
            "witness_target_packet_id": row["witness_packet_edge"]["target_packet_id"],
        }
        for row in zero_pair_rows
    }

    checks = {
        "canonical_labelled_frame_is_certified": frame.get("status")
        == "D20_FULL_EXPOSURE_CANONICAL_LABELLED_FRAME_CERTIFIED"
        and frame.get("all_checks_pass") is True,
        "packet_propagation_graph_is_certified": graph.get("status")
        == "D20_FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_CERTIFIED"
        and graph.get("all_checks_pass") is True,
        "packet_propagation_cells_are_certified": cells.get("status")
        == "D20_FULL_EXPOSURE_PACKET_PROPAGATION_CELLS_CERTIFIED"
        and cells.get("all_checks_pass") is True,
        "frame_keys_are_injective_coordinates": len(
            {sha_json(row["canonical_frame_key"]) for row in frame_rows}
        )
        == 20
        and frame.get("checks", {}).get("canonical_frame_key_is_injective") is True,
        "all_weighted_edges_lift_to_label_coordinates": len(label_transition_rows) == 40
        and all(row["source"]["canonical_frame_key"] for row in label_transition_rows)
        and all(row["target"]["canonical_frame_key"] for row in label_transition_rows),
        "label_operator_has_expected_weight_profile": transition_summary[
            "edge_kind_weight_histogram"
        ]
        == {"active_partner|4": 20, "source_loop|2": 20}
        and transition_summary["row_sum_histogram"] == {"6": 20}
        and transition_summary["target_count_per_source_histogram"] == {"2": 20},
        "label_operator_has_ten_uniform_doublet_blocks": transition_summary[
            "component_count"
        ]
        == 10
        and transition_summary["component_block_histogram"] == {"[[2, 4], [4, 2]]": 10},
        "label_operator_preserves_hidden_transfer_zero": transition_summary[
            "hidden_transfer_histogram_by_edge"
        ]
        == {'{"0": 2}': 20, '{"0": 4}': 20},
        "zero_pair_coordinate_transitions_are_identified": len(zero_pair_rows) == 2
        and zero_pair_target_weights
        == {
            "source_loop": {
                "weight": 2,
                "target_frame_index": 0,
                "target_clock_frame": "zero_pair",
                "target_sector26_clock_sum_mod26": 0,
                "target_fine_spectral_charge_key": "32|0|0|0|25",
                "witness_target_packet_id": 239,
            },
            "active_partner": {
                "weight": 4,
                "target_frame_index": 2,
                "target_clock_frame": "delta8_nonzero",
                "target_sector26_clock_sum_mod26": 4,
                "target_fine_spectral_charge_key": "28|4|8|0|25",
                "witness_target_packet_id": 238,
            },
        },
        "raw_cell_count_matches_label_operator_expansion": cells.get("derived", {})
        .get("propagation_cell_summary", {})
        .get("two_step_cross_return_row_count")
        == sum(row["weight"] for row in label_transition_rows)
        == 120,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FULL_EXPOSURE_LABEL_COORDINATE_TRANSITION_OPERATOR_CERTIFIED"
        if all_checks_pass
        else "D20_FULL_EXPOSURE_LABEL_COORDINATE_TRANSITION_OPERATOR_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.full_exposure_label_coordinate_transition_operator",
        "status": status,
        "object": "d20",
        "claim": (
            "The full-exposure two-step transition operator can be written entirely in the intrinsic "
            "canonical labelled-frame coordinates. In those coordinates it remains ten uniform doublet "
            "blocks [[2,4],[4,2]], and the zero-pair coordinate has a certified self-loop of weight 2 "
            "plus an active-partner transition of weight 4."
        ),
        "definition": {
            "label_coordinate": (
                "The injective canonical frame key and its named mass, clock, gamma, sector-26, and fine "
                "spectral labels."
            ),
            "label_transition_operator": (
                "The weighted full-exposure packet propagation graph rewritten with source and target "
                "label coordinates; packet ids are retained only as witness fields."
            ),
        },
        "inputs": {
            "full_exposure_canonical_labelled_frame_report": {
                "path": rel(FULL_EXPOSURE_CANONICAL_LABELLED_FRAME_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_CANONICAL_LABELLED_FRAME_REPORT),
            },
            "full_exposure_packet_propagation_graph_report": {
                "path": rel(FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_REPORT),
            },
            "full_exposure_packet_propagation_cells_report": {
                "path": rel(FULL_EXPOSURE_PACKET_PROPAGATION_CELLS_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_PACKET_PROPAGATION_CELLS_REPORT),
            },
        },
        "derived": {
            "transition_summary": transition_summary,
            "zero_pair_target_weights": zero_pair_target_weights,
            "label_transition_rows": label_transition_rows,
            "label_transition_rows_sha256": sha_json(label_transition_rows),
            "component_coordinate_rows": component_coordinate_rows,
            "component_coordinate_rows_sha256": sha_json(component_coordinate_rows),
        },
        "interpretation": {
            "what_this_proves": [
                "the transition operator no longer needs packet ids as coordinates because canonical frame keys are injective",
                "the full-exposure operator is still exactly ten uniform active-partner doublet blocks",
                "the packet-239 zero-pair coordinate propagates to itself with weight 2 and to its active partner's label coordinate with weight 4",
            ],
            "what_this_does_not_prove": (
                "This does not diagonalize the labelled operator or interpret the zero-pair coordinate as a "
                "vacuum eigenstate. It only rewrites the certified transition operator in intrinsic labels."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Diagonalize the label-coordinate transition operator and test whether the zero-pair coordinate "
            "defines a distinguished eigenfunctional or boundary condition rather than only a labelled state."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {k: v for k, v in report.items() if k != "certificate_sha256"}
    )
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.full_exposure_label_coordinate_transition_operator_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify canonical labelled frame, propagation graph, and propagation-cell inputs",
            "rewrite all 40 weighted directed graph edges in injective label coordinates",
            "verify the 120 raw two-step rows expand to the 40 weighted label-coordinate edges",
            "verify the ten uniform [[2,4],[4,2]] active-partner blocks",
            "verify the zero-pair coordinate self-loop and active-partner label transition",
        ],
    }
    manifest["report_sha256"] = report["certificate_sha256"]
    manifest["manifest_sha256"] = sha_json(
        {k: v for k, v in manifest.items() if k != "manifest_sha256"}
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    update_theorem_index(report, out_dir)
    return report


def main() -> None:
    report = write_theorem()
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report.get("all_checks_pass"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
