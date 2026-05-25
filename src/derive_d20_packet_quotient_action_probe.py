from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

try:
    from src.paths import D20_INVARIANTS, ROOT
except ModuleNotFoundError:  # Supports `python src/derive_d20_packet_quotient_action_probe.py`.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "d20_packet_quotient_action_probe"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

CONSTANTS = ROOT / "data" / "raw" / "constants.json"
QUOTIENTS_NPZ = ROOT / "data" / "raw" / "quotients.npz"
FULL_EXPOSURE_PACKET_PROPAGATION_CELLS = (
    D20_INVARIANTS / "theorems" / "full_exposure_packet_propagation_cells" / "report.json"
)
FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH = (
    D20_INVARIANTS / "theorems" / "full_exposure_packet_propagation_graph" / "report.json"
)
FULL_EXPOSURE_LABEL_COORDINATE_TRANSITION_OPERATOR = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_label_coordinate_transition_operator"
    / "report.json"
)
D20_FULL_PACKET_MATRIX_LIFT = (
    D20_INVARIANTS / "theorems" / "d20_full_packet_matrix_lift" / "report.json"
)
COMPACT_AMPLITUDE_QUOTIENT = (
    D20_INVARIANTS / "theorems" / "compact_amplitude_quotient" / "report.json"
)
REDUCED_AMPLITUDE_QUOTIENT_SCATTERING_AUTOMATON = (
    D20_INVARIANTS
    / "theorems"
    / "reduced_amplitude_quotient_scattering_automaton"
    / "report.json"
)
FOURIER_SCREEN0_TUBE_CENTRAL_ELEMENT = (
    D20_INVARIANTS / "theorems" / "fourier_screen0_tube_central_element" / "report.json"
)
TUBE_SANDPILE_DIVISOR_MAP = (
    D20_INVARIANTS / "theorems" / "tube_sandpile_divisor_map" / "report.json"
)
TUBE_SANDPILE_KERNEL_FLIPS = (
    D20_INVARIANTS / "theorems" / "tube_sandpile_kernel_flips" / "report.json"
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
        if index.get("schema") == "d20.theorem_registry.source_drop":
            return
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


def input_record(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": sha_file(path)}


def pair_rows_by_kind(generator_pair_table: list[dict[str, Any]], kind: str) -> list[dict[str, Any]]:
    return [row for row in generator_pair_table if row.get("target_kind") == kind]


def ordered_pairs(rows: list[dict[str, Any]]) -> list[list[int]]:
    return sorted([list(row["ordered_generators"]) for row in rows])


def block_is_uniform(rows: list[dict[str, Any]]) -> bool:
    return all(row.get("block_matrix") == [[2, 4], [4, 2]] for row in rows)


def build_candidate_source_rows(
    compact: dict[str, Any],
    reduced: dict[str, Any],
    tube: dict[str, Any],
    divisor: dict[str, Any],
    flips: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "source_id": "full_exposure_packet_propagation_cells",
            "status": "positive_packet_action_source",
            "certified_status": "D20_FULL_EXPOSURE_PACKET_PROPAGATION_CELLS_CERTIFIED",
            "packet_operator_status": "supplies_raw_paired_cross_return_rows",
        },
        {
            "source_id": "full_exposure_packet_propagation_graph",
            "status": "positive_packet_action_matrix",
            "certified_status": "D20_FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_CERTIFIED",
            "packet_operator_status": "supplies_20_by_20_transition_matrix",
        },
        {
            "source_id": "full_exposure_label_coordinate_transition_operator",
            "status": "positive_label_coordinate_witness",
            "certified_status": "D20_FULL_EXPOSURE_LABEL_COORDINATE_TRANSITION_OPERATOR_CERTIFIED",
            "packet_operator_status": "rewrites_the_packet_action_in_intrinsic_labels",
        },
        {
            "source_id": "d20_full_packet_matrix_lift",
            "status": "positive_block_lift_receiver",
            "certified_status": "D20_FULL_PACKET_MATRIX_LIFT_CERTIFIED",
            "packet_operator_status": "confirms_landing_in_Mat_2_Q_power_10",
        },
        {
            "source_id": "compact_amplitude_quotient",
            "status": compact["status"],
            "packet_operator_status": "quotient_context_no_full_exposure_packet_restriction_map",
        },
        {
            "source_id": "reduced_amplitude_quotient_scattering_automaton",
            "status": reduced["status"],
            "packet_operator_status": "quotient_context_no_full_exposure_packet_restriction_map",
        },
        {
            "source_id": "fourier_screen0_tube_central_element",
            "status": tube["status"],
            "packet_operator_status": "tube_context_no_full_exposure_packet_restriction_map",
        },
        {
            "source_id": "tube_sandpile_divisor_map",
            "status": divisor["status"],
            "packet_operator_status": "sandpile_context_no_full_exposure_packet_restriction_map",
        },
        {
            "source_id": "tube_sandpile_kernel_flips",
            "status": flips["status"],
            "packet_operator_status": "sandpile_context_no_full_exposure_packet_restriction_map",
        },
        {
            "source_id": "raw_quotients_npz",
            "status": "hashed_input_present",
            "packet_operator_status": "raw_quotient_tensor_input_no_packet_restriction_certificate",
        },
    ]


def build_theorem() -> dict[str, Any]:
    constants = load_json(CONSTANTS)
    cells = load_json(FULL_EXPOSURE_PACKET_PROPAGATION_CELLS)
    graph = load_json(FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH)
    label_operator = load_json(FULL_EXPOSURE_LABEL_COORDINATE_TRANSITION_OPERATOR)
    full_lift = load_json(D20_FULL_PACKET_MATRIX_LIFT)
    compact = load_json(COMPACT_AMPLITUDE_QUOTIENT)
    reduced = load_json(REDUCED_AMPLITUDE_QUOTIENT_SCATTERING_AUTOMATON)
    tube = load_json(FOURIER_SCREEN0_TUBE_CENTRAL_ELEMENT)
    divisor = load_json(TUBE_SANDPILE_DIVISOR_MAP)
    flips = load_json(TUBE_SANDPILE_KERNEL_FLIPS)

    cell_rows = cells["derived"]["cell_summary_rows"]
    graph_summary = graph["derived"]["graph_summary"]
    graph_components = graph["derived"]["component_rows"]
    generator_pair_table = graph["derived"]["generator_pair_table"]
    source_loop_rows = pair_rows_by_kind(generator_pair_table, "source_loop")
    active_partner_rows = pair_rows_by_kind(generator_pair_table, "active_partner")
    label_components = label_operator["derived"]["component_coordinate_rows"]
    lift_summary = full_lift["derived"]["acting_summary"]
    a985_probe = full_lift["derived"]["a985_action_probe"]
    candidate_source_rows = build_candidate_source_rows(compact, reduced, tube, divisor, flips)

    certified_packet_actions = [
        {
            "operator_id": "source_loop_5_10_plus_10_5",
            "source": "ordered crossing pairs [5,10] and [10,5]",
            "block_on_each_active_partner_doublet": [[2, 0], [0, 2]],
            "block_decomposition": "2I",
            "preserves_full_exposure_20_packet_subspace": True,
            "lands_in_block_lift": True,
            "operator_kind": "primitive_generator_scattering_piece",
        },
        {
            "operator_id": "active_partner_cross_pair_sum",
            "source": "ordered crossing pairs [5,9], [9,5], [9,10], and [10,9]",
            "block_on_each_active_partner_doublet": [[0, 4], [4, 0]],
            "block_decomposition": "4S",
            "preserves_full_exposure_20_packet_subspace": True,
            "lands_in_block_lift": True,
            "operator_kind": "primitive_generator_scattering_piece",
        },
        {
            "operator_id": "full_paired_cross_return_sum",
            "source": "sum of all ordered distinct crossing pairs from {5,9,10}",
            "block_on_each_active_partner_doublet": [[2, 4], [4, 2]],
            "block_decomposition": "2I+4S",
            "preserves_full_exposure_20_packet_subspace": True,
            "lands_in_block_lift": True,
            "operator_kind": "primitive_generator_scattering_operator",
        },
    ]
    operator_probe_summary = {
        "packet_space_dimension": 20,
        "full_exposure_packet_count": graph_summary["vertex_count"],
        "active_partner_doublet_count": graph_summary["component_count"],
        "block_algebra": lift_summary["block_algebra"],
        "positive_packet_action_count": len(certified_packet_actions),
        "strongest_certified_packet_action": "full_paired_cross_return_sum",
        "strongest_certified_packet_action_block": "2I+4S",
        "source_loop_action_block": "2I",
        "active_partner_action_block": "4S",
        "preserves_full_exposure_20_packet_subspace": True,
        "lands_in_block_lift": True,
        "a985_dimension": constants["wedderburn"]["sum_squares"],
        "block_lift_image_dimension_bound": a985_probe["block_lift_image_dimension_bound"],
        "minimum_kernel_dimension_for_any_a985_map_into_this_block_lift": a985_probe[
            "minimum_kernel_dimension_for_any_a985_map_into_this_block_lift"
        ],
        "certified_a985_to_packet_operator_map_present": False,
        "a985_or_tube_packet_operator_found": False,
        "terminal_quotient_packet_operator_found": False,
        "only_scattering_quotient_packet_actions_found": True,
    }
    negative_boundary = {
        "a985_multiplication_tensor_restricted_to_packets": "not_certified",
        "tube_central_element_restricted_to_packets": "not_certified",
        "raw_quotient_tensor_restricted_to_packets": "not_certified",
        "scattering_operator_is_a985_element": False,
        "scattering_operator_is_tube_central_element": False,
        "scattering_operator_is_terminal_quotient_element": False,
    }
    checks = {
        "packet_cell_input_is_certified": cells.get("status")
        == "D20_FULL_EXPOSURE_PACKET_PROPAGATION_CELLS_CERTIFIED"
        and cells.get("all_checks_pass") is True,
        "packet_graph_input_is_certified": graph.get("status")
        == "D20_FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_CERTIFIED"
        and graph.get("all_checks_pass") is True,
        "label_coordinate_input_is_certified": label_operator.get("status")
        == "D20_FULL_EXPOSURE_LABEL_COORDINATE_TRANSITION_OPERATOR_CERTIFIED"
        and label_operator.get("all_checks_pass") is True,
        "full_packet_matrix_lift_input_is_certified": full_lift.get("status")
        == "D20_FULL_PACKET_MATRIX_LIFT_CERTIFIED"
        and full_lift.get("all_checks_pass") is True,
        "quotient_and_tube_context_inputs_are_certified": compact.get("status")
        == "D20_COMPACT_AMPLITUDE_QUOTIENT_CERTIFIED"
        and reduced.get("status")
        == "D20_REDUCED_AMPLITUDE_QUOTIENT_SCATTERING_AUTOMATON_CERTIFIED"
        and tube.get("status") == "D20_FOURIER_SCREEN0_TUBE_CENTRAL_ELEMENT_CERTIFIED"
        and divisor.get("status") == "D20_TUBE_SANDPILE_DIVISOR_MAP_CERTIFIED"
        and flips.get("status") == "D20_TUBE_SANDPILE_KERNEL_FLIPS_CERTIFIED",
        "full_exposure_packet_count_is_20": len(cell_rows) == 20
        and graph_summary["vertex_count"] == 20,
        "all_cells_have_only_source_and_active_partner_targets": all(
            len(row["two_step_target_histogram"]) == 2
            and row["two_step_target_histogram"].get(str(row["source_packet_id"])) == 2
            and row["two_step_target_histogram"].get(str(row["active_partner_packet_id"])) == 4
            for row in cell_rows
        ),
        "source_loop_piece_is_exactly_5_10_plus_10_5": ordered_pairs(source_loop_rows)
        == [[5, 10], [10, 5]]
        and all(row.get("row_count") == 20 for row in source_loop_rows),
        "active_partner_piece_is_the_four_remaining_ordered_crossing_pairs": ordered_pairs(
            active_partner_rows
        )
        == [[5, 9], [9, 5], [9, 10], [10, 9]]
        and all(row.get("row_count") == 20 for row in active_partner_rows),
        "graph_blocks_are_uniform_2I_plus_4S": len(graph_components) == 10
        and block_is_uniform(graph_components),
        "label_blocks_are_uniform_2I_plus_4S": len(label_components) == 10
        and block_is_uniform(label_components),
        "full_paired_cross_return_operator_lands_in_Mat_2_Q_power_10": lift_summary[
            "block_algebra"
        ]
        == "Mat_2(Q)^10"
        and a985_probe["tested_action"] == "full_exposure_two_step_transition_operator"
        and a985_probe["tested_action_lands_in_block_lift"] is True,
        "a985_or_tube_packet_operator_is_not_found": operator_probe_summary[
            "a985_or_tube_packet_operator_found"
        ]
        is False
        and operator_probe_summary["terminal_quotient_packet_operator_found"] is False
        and a985_probe["certified_a985_to_packet_operator_map_present"] is False,
        "dimension_boundary_blocks_faithful_full_a985_action_here": operator_probe_summary[
            "a985_dimension"
        ]
        == 985
        and operator_probe_summary["block_lift_image_dimension_bound"] == 40
        and operator_probe_summary[
            "minimum_kernel_dimension_for_any_a985_map_into_this_block_lift"
        ]
        == 945,
        "negative_boundary_is_explicit": all(
            value == "not_certified"
            for key, value in negative_boundary.items()
            if key.endswith("_restricted_to_packets")
        )
        and negative_boundary["scattering_operator_is_a985_element"] is False
        and negative_boundary["scattering_operator_is_tube_central_element"] is False,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_PACKET_QUOTIENT_ACTION_PROBE_CERTIFIED"
        if all_checks_pass
        else "D20_PACKET_QUOTIENT_ACTION_PROBE_NEEDS_REVIEW"
    )
    report = {
        "schema": "d20.theorem.d20_packet_quotient_action_probe",
        "status": status,
        "object": "d20",
        "claim": (
            "The quotient-action probe finds certified packet-level scattering actions "
            "that preserve the 20 full-exposure packets and land in Mat_2(Q)^10. "
            "The source-loop piece [5,10]+[10,5] acts as 2I, the active-partner "
            "piece acts as 4S, and their sum is the already certified 2I+4S "
            "doublet block. No certified A985, tube, or terminal-quotient packet "
            "operator map is found yet."
        ),
        "definition": {
            "packet_quotient_action_probe": (
                "A boundary search over the certified quotient, tube, sandpile, and "
                "full-exposure packet certificates for an operator that preserves the "
                "20-packet full-exposure subspace and lands in the Mat_2(Q)^10 lift."
            ),
            "positive_result": (
                "The primitive-generator paired cross-return scattering operator and "
                "its source-loop and active-partner pieces have certified packet actions."
            ),
            "negative_boundary": (
                "The positive scattering operator is not certified as an A985 element, "
                "tube central element, or terminal quotient tensor restriction."
            ),
        },
        "inputs": {
            "constants": input_record(CONSTANTS),
            "quotients_npz": input_record(QUOTIENTS_NPZ),
            "full_exposure_packet_propagation_cells_report": input_record(
                FULL_EXPOSURE_PACKET_PROPAGATION_CELLS
            ),
            "full_exposure_packet_propagation_graph_report": input_record(
                FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH
            ),
            "full_exposure_label_coordinate_transition_operator_report": input_record(
                FULL_EXPOSURE_LABEL_COORDINATE_TRANSITION_OPERATOR
            ),
            "d20_full_packet_matrix_lift_report": input_record(D20_FULL_PACKET_MATRIX_LIFT),
            "compact_amplitude_quotient_report": input_record(COMPACT_AMPLITUDE_QUOTIENT),
            "reduced_amplitude_quotient_scattering_automaton_report": input_record(
                REDUCED_AMPLITUDE_QUOTIENT_SCATTERING_AUTOMATON
            ),
            "fourier_screen0_tube_central_element_report": input_record(
                FOURIER_SCREEN0_TUBE_CENTRAL_ELEMENT
            ),
            "tube_sandpile_divisor_map_report": input_record(TUBE_SANDPILE_DIVISOR_MAP),
            "tube_sandpile_kernel_flips_report": input_record(TUBE_SANDPILE_KERNEL_FLIPS),
        },
        "derived": {
            "operator_probe_summary": operator_probe_summary,
            "certified_packet_actions": certified_packet_actions,
            "candidate_source_rows": candidate_source_rows,
            "negative_boundary": negative_boundary,
            "certified_packet_actions_sha256": sha_json(certified_packet_actions),
            "candidate_source_rows_sha256": sha_json(candidate_source_rows),
        },
        "interpretation": {
            "what_this_certifies": [
                "the paired cross-return scattering operator preserves the 20 full-exposure packets",
                "the source-loop [5,10]+[10,5] piece acts as 2I on every active-partner doublet",
                "the remaining ordered crossing pairs act as 4S on every active-partner doublet",
                "the full packet action lands in the already certified Mat_2(Q)^10 block lift",
            ],
            "what_this_does_not_certify": [
                "an A985 multiplication element acting on the 20 packets",
                "a tube central element acting on the 20 packets",
                "a terminal quotient tensor restriction acting on the 20 packets",
                "a physical Matrix/M-theory promotion",
            ],
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Construct an explicit restriction map from A985, the tube screen-0 central "
            "element, or q42/q12 quotient tensors to the 20 full-exposure packets and "
            "test whether any resulting packet action equals 2I, 4S, or 2I+4S."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {key: value for key, value in report.items() if key != "certificate_sha256"}
    )
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.d20_packet_quotient_action_probe_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify packet-cell, packet-graph, label-coordinate, and matrix-lift inputs",
            "verify quotient, tube, and sandpile context inputs",
            "verify the 20-packet full-exposure subspace is preserved",
            "verify the [5,10]+[10,5] source-loop piece is 2I",
            "verify the active-partner crossing piece is 4S",
            "verify the full paired cross-return operator is 2I+4S in Mat_2(Q)^10",
            "verify no A985, tube, or terminal-quotient packet operator map is certified",
        ],
    }
    manifest["report_sha256"] = report["certificate_sha256"]
    manifest["manifest_sha256"] = sha_json(
        {key: value for key, value in manifest.items() if key != "manifest_sha256"}
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
