from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

try:
    from src.paths import D20_INVARIANTS, ROOT
except ModuleNotFoundError:  # Supports `python src/derive_d20_explicit_packet_restriction_map_test.py`.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "d20_explicit_packet_restriction_map_test"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

CONSTANTS = ROOT / "data" / "raw" / "constants.json"
QUOTIENTS_NPZ = ROOT / "data" / "raw" / "quotients.npz"
RELATION_MEMBERSHIPS_NPZ = ROOT / "data" / "raw" / "relation_memberships.npz"
FULL_EXPOSURE_CANONICAL_LABELLED_FRAME = (
    D20_INVARIANTS / "theorems" / "full_exposure_canonical_labelled_frame" / "report.json"
)
PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE = (
    D20_INVARIANTS / "theorems" / "projective_packet_spectral_charge_table" / "report.json"
)
REDUCED_AMPLITUDE_QUOTIENT_SCATTERING_AUTOMATON = (
    D20_INVARIANTS
    / "theorems"
    / "reduced_amplitude_quotient_scattering_automaton"
    / "report.json"
)
FULL_EXPOSURE_PACKET_PROPAGATION_CELLS = (
    D20_INVARIANTS / "theorems" / "full_exposure_packet_propagation_cells" / "report.json"
)
FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH = (
    D20_INVARIANTS / "theorems" / "full_exposure_packet_propagation_graph" / "report.json"
)
FOURIER_SCREEN0_TUBE_CENTRAL_ELEMENT = (
    D20_INVARIANTS / "theorems" / "fourier_screen0_tube_central_element" / "report.json"
)
D20_PACKET_QUOTIENT_ACTION_PROBE = (
    D20_INVARIANTS / "theorems" / "d20_packet_quotient_action_probe" / "report.json"
)

CROSSING_GENERATORS = [5, 9, 10]
KERNEL_SIMPLE_SOURCE_BITS = [0, 1, 2, 3, 4, 6, 7, 8]
ACTIVE_LEFT_COORD = 8
ACTIVE_RIGHT_COORD = 9
PARITY_SOURCE_BIT = 5
PACKET_BRIDGE_FIELDS = {
    "packet_id",
    "mode_mask",
    "mode_masks",
    "radical_character",
    "active_sigma",
}
RELATION_BRIDGE_FIELDS = {
    "relation_id",
    "relation",
    "q42_class",
    "q12_class",
    "block_i",
    "block_j",
    "object",
    "object_label",
}


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


def histogram(values: list[Any]) -> dict[str, int]:
    counter = Counter(values)
    return {str(key): int(counter[key]) for key in sorted(counter)}


def packet_key_from_mode_pair(mode_to_packet: dict[int, int], modes: list[int]) -> int | None:
    key = packet_key_with_parity(modes)
    if key["parity"] != "kernel":
        return None
    packet_id = int(key["packet_id"])
    packets = {mode_to_packet.get(int(mask)) for mask in modes}
    if packets != {packet_id}:
        return None
    return packet_id


def source_parity(mask: int) -> int:
    return ((mask >> 5) ^ (mask >> 9) ^ (mask >> 10)) & 1


def coord_from_kernel_mask(mask: int) -> int:
    coord = 0
    for coord_idx, source_bit in enumerate(KERNEL_SIMPLE_SOURCE_BITS):
        if (mask >> source_bit) & 1:
            coord |= 1 << coord_idx
    if (mask >> 9) & 1:
        coord |= 1 << ACTIVE_LEFT_COORD
    if (mask >> 10) & 1:
        coord |= 1 << ACTIVE_RIGHT_COORD
    return coord


def packet_key_with_parity(mode_pair: list[int]) -> dict[str, Any]:
    parity_values = [source_parity(mask) for mask in mode_pair]
    if parity_values[0] != parity_values[1]:
        raise ValueError(f"mixed parity mode pair {mode_pair}")
    parity_value = parity_values[0]
    kernel_coords = []
    for mask in mode_pair:
        kernel_mask = mask ^ (1 << PARITY_SOURCE_BIT) if parity_value else mask
        kernel_coords.append(coord_from_kernel_mask(kernel_mask))
    radical_values = [coord & 0xFF for coord in kernel_coords]
    active_sigma_values = [(coord >> ACTIVE_LEFT_COORD) & 1 for coord in kernel_coords]
    active_beta_values = sorted((coord >> ACTIVE_RIGHT_COORD) & 1 for coord in kernel_coords)
    if len(set(radical_values)) != 1 or len(set(active_sigma_values)) != 1:
        raise ValueError(f"mode pair does not define a packet {mode_pair}")
    if active_beta_values != [0, 1]:
        raise ValueError(f"mode pair does not span active beta pair {mode_pair}")
    radical = radical_values[0]
    active_sigma = active_sigma_values[0]
    packet_id = radical * 2 + active_sigma
    return {
        "parity": "odd" if parity_value else "kernel",
        "radical_character": radical,
        "active_sigma": active_sigma,
        "packet_id": packet_id if parity_value == 0 else None,
        "packet_key": f"odd:{radical}:{active_sigma}" if parity_value else f"kernel:{packet_id}",
    }


def build_transition_map(rows: list[dict[str, Any]]) -> dict[tuple[int, int], dict[str, Any]]:
    out: dict[tuple[int, int], dict[str, Any]] = {}
    for row in rows:
        generator = int(row["generator_cycle_id"])
        if generator in CROSSING_GENERATORS:
            out[(int(row["source_mask"]), generator)] = row
    return out


def build_mask_packet_projection(
    packet_rows: list[dict[str, Any]],
    full_packet_ids: list[int],
) -> tuple[dict[int, int], dict[int, int], list[dict[str, Any]]]:
    mode_to_packet = {}
    for packet in packet_rows:
        packet_id = int(packet["packet_id"])
        for mode in packet["mode_masks"]:
            mode_to_packet[int(mode)] = packet_id

    full_id_set = set(full_packet_ids)
    full_mode_to_packet = {
        int(mode): int(packet["packet_id"])
        for packet in packet_rows
        if int(packet["packet_id"]) in full_id_set
        for mode in packet["mode_masks"]
    }
    projection_rows = [
        {
            "mode_mask": int(mode),
            "packet_id": int(packet_id),
        }
        for mode, packet_id in sorted(full_mode_to_packet.items())
    ]
    return mode_to_packet, full_mode_to_packet, projection_rows


def restrict_crossing_automaton_to_packets(
    packet_rows_by_id: dict[int, dict[str, Any]],
    full_packet_ids: list[int],
    mode_to_packet: dict[int, int],
    transitions: dict[tuple[int, int], dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    one_step_rows = []
    source_rows = []
    for source_packet_id in sorted(full_packet_ids):
        source_modes = [int(mask) for mask in packet_rows_by_id[source_packet_id]["mode_masks"]]
        one_step_target_kinds = []
        two_step_counter: Counter[int] = Counter()
        ordered_pair_rows = []
        for generator in CROSSING_GENERATORS:
            transition_rows = [transitions[(mode, generator)] for mode in source_modes]
            target_modes = [int(row["target_mask"]) for row in transition_rows]
            target_key = packet_key_with_parity(target_modes)
            target_kinds = [target_key["parity"]]
            one_step_target_kinds.extend(target_kinds)
            one_step_rows.append(
                {
                    "source_packet_id": source_packet_id,
                    "generator_cycle_id": generator,
                    "source_modes": source_modes,
                    "target_modes": target_modes,
                    "target_packet_key": target_key["packet_key"],
                    "target_parity_values": target_kinds,
                    "target_is_kernel_packet": target_key["parity"] == "kernel",
                }
            )
        for first in CROSSING_GENERATORS:
            for second in CROSSING_GENERATORS:
                if first == second:
                    continue
                target_modes = []
                hidden_packet_path = []
                for mode in source_modes:
                    first_row = transitions[(mode, first)]
                    second_row = transitions[(int(first_row["target_mask"]), second)]
                    target_modes.append(int(second_row["target_mask"]))
                    hidden_packet_path.append(
                        [
                            str(first_row["source_hidden_packet"]),
                            str(first_row["target_hidden_packet"]),
                            str(second_row["target_hidden_packet"]),
                        ]
                    )
                target_packet_id = packet_key_from_mode_pair(mode_to_packet, target_modes)
                if target_packet_id is not None:
                    two_step_counter[int(target_packet_id)] += 1
                ordered_pair_rows.append(
                    {
                        "ordered_generators": [first, second],
                        "target_modes": target_modes,
                        "target_packet_id": target_packet_id,
                        "returns_to_source_packet": target_packet_id == source_packet_id,
                        "returns_to_active_partner": target_packet_id == (source_packet_id ^ 1),
                        "hidden_packet_paths": hidden_packet_path,
                    }
                )
        source_rows.append(
            {
                "source_packet_id": source_packet_id,
                "active_partner_packet_id": source_packet_id ^ 1,
                "source_modes": source_modes,
                "one_step_target_kind_histogram": histogram(one_step_target_kinds),
                "two_step_target_histogram": {
                    str(packet_id): int(two_step_counter[packet_id])
                    for packet_id in sorted(two_step_counter)
                },
                "source_return_ordered_crossings": sorted(
                    row["ordered_generators"]
                    for row in ordered_pair_rows
                    if row["returns_to_source_packet"]
                ),
                "active_partner_ordered_crossings": sorted(
                    row["ordered_generators"]
                    for row in ordered_pair_rows
                    if row["returns_to_active_partner"]
                ),
            }
        )
    return one_step_rows, source_rows


def block_rows_from_source_rows(source_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    blocks = []
    by_source = {int(row["source_packet_id"]): row for row in source_rows}
    for source in sorted(by_source):
        if source in seen:
            continue
        partner = source ^ 1
        first = by_source[source]["two_step_target_histogram"]
        second = by_source[partner]["two_step_target_histogram"]
        blocks.append(
            {
                "packet_pair": sorted([source, partner]),
                "block_matrix": [
                    [int(first.get(str(source), 0)), int(first.get(str(partner), 0))],
                    [int(second.get(str(source), 0)), int(second.get(str(partner), 0))],
                ],
            }
        )
        seen.add(source)
        seen.add(partner)
    return blocks


def build_theorem() -> dict[str, Any]:
    constants = load_json(CONSTANTS)
    frame = load_json(FULL_EXPOSURE_CANONICAL_LABELLED_FRAME)
    spectral = load_json(PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE)
    automaton = load_json(REDUCED_AMPLITUDE_QUOTIENT_SCATTERING_AUTOMATON)
    cells = load_json(FULL_EXPOSURE_PACKET_PROPAGATION_CELLS)
    graph = load_json(FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH)
    tube = load_json(FOURIER_SCREEN0_TUBE_CENTRAL_ELEMENT)
    packet_probe = load_json(D20_PACKET_QUOTIENT_ACTION_PROBE)
    quotients = np.load(QUOTIENTS_NPZ)
    memberships = np.load(RELATION_MEMBERSHIPS_NPZ)

    full_packet_ids = sorted(int(row["packet_id"]) for row in frame["derived"]["canonical_frame_rows"])
    packet_rows = spectral["derived"]["packet_spectral_charge_rows"]
    packet_rows_by_id = {int(row["packet_id"]): row for row in packet_rows}
    mode_to_packet, full_mode_to_packet, projection_rows = build_mask_packet_projection(
        packet_rows,
        full_packet_ids,
    )
    transitions = build_transition_map(automaton["derived"]["reduced_transition_rows"])
    one_step_rows, source_rows = restrict_crossing_automaton_to_packets(
        packet_rows_by_id,
        full_packet_ids,
        mode_to_packet,
        transitions,
    )
    automaton_block_rows = block_rows_from_source_rows(source_rows)
    graph_block_rows = [
        {
            "packet_pair": sorted([int(packet) for packet in row["packet_pair"]]),
            "block_matrix": row["block_matrix"],
        }
        for row in graph["derived"]["component_rows"]
    ]

    quotient_shapes = {
        key: list(quotients[key].shape)
        for key in ("q42_map", "q12_map", "q42_tensor", "q12_tensor", "block_i", "block_j")
    }
    relation_shapes = {
        key: list(memberships[key].shape)
        for key in ("encoded_pairs", "offsets", "object_of_point", "reps", "block_i", "block_j")
    }
    packet_row_fields = set(packet_rows[0])
    automaton_row_fields = set(automaton["derived"]["reduced_transition_rows"][0])
    quotient_array_names = set(quotients.files)
    relation_array_names = set(memberships.files)
    tube_fields = set(tube["derived"])
    missing_bridge_inventory = [
        {
            "candidate": "A985_relation_basis_to_full_packets",
            "source_domain": "relation_id[0..984]",
            "available_source_keys": sorted(relation_array_names),
            "target_domain": "20 full-exposure packet ids and 40 packet modes",
            "status": "blocked_missing_relation_to_packet_projection",
        },
        {
            "candidate": "screen0_tube_element_to_full_packets",
            "source_domain": "six signed object identity relations inside the closed-loop tube",
            "available_source_keys": sorted(tube_fields),
            "target_domain": "20 full-exposure packet ids and 40 packet modes",
            "status": "blocked_missing_object_or_relation_to_packet_projection",
        },
        {
            "candidate": "q42_q12_tensor_to_full_packets",
            "source_domain": "q42/q12 quotient classes of A985 relations",
            "available_source_keys": sorted(quotient_array_names),
            "target_domain": "20 full-exposure packet ids and 40 packet modes",
            "status": "blocked_missing_quotient_class_to_packet_projection",
        },
    ]
    restriction_summary = {
        "constructed_restriction": "reduced_scattering_automaton_mask_to_full_packet_projection",
        "constructed_projection_mode_count": len(projection_rows),
        "constructed_projection_packet_count": len(full_packet_ids),
        "crossing_generators_tested": CROSSING_GENERATORS,
        "one_step_kernel_packet_action_exists": False,
        "two_step_packet_action_exists": True,
        "two_step_block": "2I+4S",
        "block_algebra": "Mat_2(Q)^10",
        "a985_relation_restriction_constructed": False,
        "tube_screen0_restriction_constructed": False,
        "q42_q12_restriction_constructed": False,
        "missing_bridge_count": len(missing_bridge_inventory),
    }
    domain_inventory = {
        "a985_relation_count": int(constants["wedderburn"]["sum_squares"]),
        "relation_membership_shapes": relation_shapes,
        "q42_class_count": int(quotients["q42_tensor"].shape[0]),
        "q12_class_count": int(quotients["q12_tensor"].shape[0]),
        "quotient_shapes": quotient_shapes,
        "tube_closed_loop_basis_count": int(tube["derived"]["closed_loop_basis_count"]),
        "tube_identity_relation_count": len(tube["derived"]["identity_relations_by_object"]),
        "automaton_mask_state_count": int(automaton["derived"]["automaton_summary"]["state_count"]),
        "kernel_mode_count": len(mode_to_packet),
        "packet_count": len(packet_rows),
        "full_exposure_packet_count": len(full_packet_ids),
        "full_exposure_mode_count": len(full_mode_to_packet),
    }
    checks = {
        "full_exposure_frame_is_certified": frame.get("status")
        == "D20_FULL_EXPOSURE_CANONICAL_LABELLED_FRAME_CERTIFIED"
        and frame.get("all_checks_pass") is True,
        "spectral_packet_table_is_certified": spectral.get("status")
        == "D20_PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_CERTIFIED"
        and spectral.get("all_checks_pass") is True,
        "reduced_scattering_automaton_is_certified": automaton.get("status")
        == "D20_REDUCED_AMPLITUDE_QUOTIENT_SCATTERING_AUTOMATON_CERTIFIED"
        and automaton.get("all_checks_pass") is True,
        "packet_cells_and_graph_are_certified": cells.get("status")
        == "D20_FULL_EXPOSURE_PACKET_PROPAGATION_CELLS_CERTIFIED"
        and cells.get("all_checks_pass") is True
        and graph.get("status") == "D20_FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_CERTIFIED"
        and graph.get("all_checks_pass") is True,
        "tube_and_packet_probe_inputs_are_certified": tube.get("status")
        == "D20_FOURIER_SCREEN0_TUBE_CENTRAL_ELEMENT_CERTIFIED"
        and tube.get("all_checks_pass") is True
        and packet_probe.get("status") == "D20_PACKET_QUOTIENT_ACTION_PROBE_CERTIFIED"
        and packet_probe.get("all_checks_pass") is True,
        "raw_quotient_and_relation_shapes_match_a985": quotient_shapes["q42_map"] == [985]
        and quotient_shapes["q12_map"] == [985]
        and quotient_shapes["q42_tensor"] == [42, 42, 42]
        and quotient_shapes["q12_tensor"] == [12, 12, 12]
        and relation_shapes["block_i"] == [985]
        and relation_shapes["block_j"] == [985],
        "full_packet_projection_has_40_modes_and_20_packets": len(projection_rows) == 40
        and len(full_packet_ids) == 20
        and histogram([row["packet_id"] for row in projection_rows]) == {
            str(packet_id): 2 for packet_id in full_packet_ids
        },
        "scattering_transition_map_has_all_crossing_entries": len(transitions) == 2048 * 3,
        "one_step_crossing_leaves_kernel_packet_space": all(
            row["target_parity_values"] == ["odd"]
            and row["target_is_kernel_packet"] is False
            for row in one_step_rows
        ),
        "two_step_restriction_matches_certified_packet_cells": {
            str(row["source_packet_id"]): row["two_step_target_histogram"]
            for row in source_rows
        }
        == {
            str(row["source_packet_id"]): row["two_step_target_histogram"]
            for row in cells["derived"]["cell_summary_rows"]
        },
        "source_return_pairs_match_5_10_and_10_5": all(
            row["source_return_ordered_crossings"] == [[5, 10], [10, 5]]
            for row in source_rows
        ),
        "automaton_blocks_match_full_packet_graph": automaton_block_rows == graph_block_rows,
        "constructed_restriction_matches_previous_probe": packet_probe["derived"][
            "operator_probe_summary"
        ]["strongest_certified_packet_action"]
        == "full_paired_cross_return_sum"
        and packet_probe["derived"]["operator_probe_summary"]["lands_in_block_lift"] is True,
        "a985_tube_q42_q12_packet_projection_is_absent": not (
            PACKET_BRIDGE_FIELDS & relation_array_names
        )
        and not (PACKET_BRIDGE_FIELDS & quotient_array_names)
        and not (PACKET_BRIDGE_FIELDS & tube_fields)
        and not (RELATION_BRIDGE_FIELDS & packet_row_fields)
        and not (RELATION_BRIDGE_FIELDS & automaton_row_fields),
        "negative_restriction_boundary_is_explicit": all(
            row["status"].startswith("blocked_missing_") for row in missing_bridge_inventory
        )
        and restriction_summary["a985_relation_restriction_constructed"] is False
        and restriction_summary["tube_screen0_restriction_constructed"] is False
        and restriction_summary["q42_q12_restriction_constructed"] is False,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_EXPLICIT_PACKET_RESTRICTION_MAP_TEST_CERTIFIED"
        if all_checks_pass
        else "D20_EXPLICIT_PACKET_RESTRICTION_MAP_TEST_NEEDS_REVIEW"
    )
    report = {
        "schema": "d20.theorem.d20_explicit_packet_restriction_map_test",
        "status": status,
        "object": "d20",
        "claim": (
            "An explicit restriction map exists from the reduced scattering automaton to "
            "the 20 full-exposure packets: project each kernel mode mask to its packet, "
            "then compose ordered crossing generators 5, 9, and 10 twice. This recovers "
            "the certified 2I+4S packet block in Mat_2(Q)^10. No corresponding raw A985, "
            "screen-0 tube, or q42/q12 quotient-to-packet restriction map is present in "
            "the current certificates."
        ),
        "definition": {
            "constructed_restriction_map": (
                "mode_mask -> projective packet id, restricted to the 40 kernel modes "
                "belonging to the 20 full-exposure packets."
            ),
            "two_step_packet_action": (
                "The ordered distinct crossing pairs from {5,9,10}, composed in the "
                "reduced scattering automaton and projected back to full-exposure packets."
            ),
            "blocked_restriction_maps": (
                "The A985 relation basis, screen-0 tube element, and q42/q12 quotient "
                "tensors currently have no certified relation/object/quotient-class to "
                "packet-mode projection."
            ),
        },
        "inputs": {
            "constants": input_record(CONSTANTS),
            "quotients_npz": input_record(QUOTIENTS_NPZ),
            "relation_memberships_npz": input_record(RELATION_MEMBERSHIPS_NPZ),
            "full_exposure_canonical_labelled_frame_report": input_record(
                FULL_EXPOSURE_CANONICAL_LABELLED_FRAME
            ),
            "projective_packet_spectral_charge_table_report": input_record(
                PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE
            ),
            "reduced_amplitude_quotient_scattering_automaton_report": input_record(
                REDUCED_AMPLITUDE_QUOTIENT_SCATTERING_AUTOMATON
            ),
            "full_exposure_packet_propagation_cells_report": input_record(
                FULL_EXPOSURE_PACKET_PROPAGATION_CELLS
            ),
            "full_exposure_packet_propagation_graph_report": input_record(
                FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH
            ),
            "fourier_screen0_tube_central_element_report": input_record(
                FOURIER_SCREEN0_TUBE_CENTRAL_ELEMENT
            ),
            "d20_packet_quotient_action_probe_report": input_record(D20_PACKET_QUOTIENT_ACTION_PROBE),
        },
        "derived": {
            "domain_inventory": domain_inventory,
            "restriction_summary": restriction_summary,
            "full_packet_mode_projection_rows": projection_rows,
            "automaton_restricted_source_rows": source_rows,
            "automaton_block_rows": automaton_block_rows,
            "missing_bridge_inventory": missing_bridge_inventory,
            "full_packet_mode_projection_rows_sha256": sha_json(projection_rows),
            "automaton_restricted_source_rows_sha256": sha_json(source_rows),
            "automaton_block_rows_sha256": sha_json(automaton_block_rows),
            "missing_bridge_inventory_sha256": sha_json(missing_bridge_inventory),
        },
        "interpretation": {
            "what_this_certifies": [
                "the reduced scattering automaton has an explicit 40-mode to 20-packet projection",
                "one crossing step leaves the kernel packet space, so the packet action is two-step",
                "the two-step restricted action exactly matches the certified 2I+4S full-packet graph",
                "the current A985, tube, and q42/q12 data still lack a certified projection to packet modes",
            ],
            "what_this_does_not_certify": [
                "an A985 relation acting on the 20 packet basis",
                "the screen-0 tube central element acting on the 20 packet basis",
                "a q42/q12 tensor action on the 20 packet basis",
                "a Matrix/M-theory promotion",
            ],
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Build the missing bridge explicitly: attach relation/object/q42/q12 labels to "
            "kernel mode masks, or prove that no such label-compatible projection can "
            "intertwine the scattering 2I+4S packet action."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {key: value for key, value in report.items() if key != "certificate_sha256"}
    )
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.d20_explicit_packet_restriction_map_test_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify full-exposure packet, scattering automaton, tube, and quotient inputs",
            "construct the 40-mode to 20-packet projection",
            "compose crossing generators 5, 9, and 10 inside the reduced automaton",
            "verify one-step crossings leave the kernel packet space",
            "verify two-step crossings recover the certified full-packet cells and graph",
            "verify raw A985, tube, and q42/q12 packet projections are not present",
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
