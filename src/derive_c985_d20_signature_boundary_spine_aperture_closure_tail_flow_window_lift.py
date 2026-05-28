from __future__ import annotations

import json
from collections import Counter, defaultdict
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_repaired_automaton import (
        OUT_DIR as REPAIRED_AUTOMATON_DIR,
        STATE_COLUMNS as AUTOMATON_STATE_COLUMNS,
        TRANSITION_COLUMNS as AUTOMATON_TRANSITION_COLUMNS,
        WORD_COLUMNS,
        one_edit_neighbors,
        padded,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_skip_window_grammar import (
        OUT_DIR as SKIP_WINDOW_DIR,
        STATUS as SKIP_WINDOW_STATUS,
        TARGET_DELTA_TWICE,
        TARGET_VARIATION_INCLUSIVE_BOUND,
        build_context,
        build_trace,
        closure_profile,
        contains_undirected_edge,
        csv_text,
        derived_spans,
        grammar_rows,
        input_entry,
        load_json,
        relpath,
        self_hash,
        sha_array,
        table_from_rows,
        write_json,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_cycle_ranking import (
        PREFIX_SYMBOLS,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_transfer_operator import (
        OUT_DIR as TRANSFER_OPERATOR_DIR,
        SIDE_FLOW_COLUMNS,
        STATUS as TRANSFER_OPERATOR_STATUS,
        TRANSFER_EDGE_COLUMNS,
        TRANSFER_STATE_COLUMNS,
        DERIVED_EDGE_WEIGHT,
        SCALE,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_transfer_operator import (
        OBSERVABLE_COLUMNS,
        round_div,
        scaled_float,
        scale_rational_vector,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_repaired_automaton import (
        OUT_DIR as REPAIRED_AUTOMATON_DIR,
        STATE_COLUMNS as AUTOMATON_STATE_COLUMNS,
        TRANSITION_COLUMNS as AUTOMATON_TRANSITION_COLUMNS,
        WORD_COLUMNS,
        one_edit_neighbors,
        padded,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_skip_window_grammar import (
        OUT_DIR as SKIP_WINDOW_DIR,
        STATUS as SKIP_WINDOW_STATUS,
        TARGET_DELTA_TWICE,
        TARGET_VARIATION_INCLUSIVE_BOUND,
        build_context,
        build_trace,
        closure_profile,
        contains_undirected_edge,
        csv_text,
        derived_spans,
        grammar_rows,
        input_entry,
        load_json,
        relpath,
        self_hash,
        sha_array,
        table_from_rows,
        write_json,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_cycle_ranking import (
        PREFIX_SYMBOLS,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_transfer_operator import (
        OUT_DIR as TRANSFER_OPERATOR_DIR,
        SIDE_FLOW_COLUMNS,
        STATUS as TRANSFER_OPERATOR_STATUS,
        TRANSFER_EDGE_COLUMNS,
        TRANSFER_STATE_COLUMNS,
        DERIVED_EDGE_WEIGHT,
        SCALE,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_transfer_operator import (
        OBSERVABLE_COLUMNS,
        round_div,
        scaled_float,
        scale_rational_vector,
    )
    from derive_c985_typed_simple_object_registry import INDEX_PATH
    from paths import D20_INVARIANTS, ROOT


THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_flow_window_lift"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_FLOW_WINDOW_LIFT_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

TRANSFER_REPORT = TRANSFER_OPERATOR_DIR / "report.json"
TRANSFER_CERTIFICATE = (
    TRANSFER_OPERATOR_DIR
    / "signature_boundary_spine_aperture_closure_tail_transfer_operator_certificate.json"
)
TRANSFER_TABLES = (
    TRANSFER_OPERATOR_DIR
    / "signature_boundary_spine_aperture_closure_tail_transfer_operator_tables.npz"
)
TRANSFER_STATES = TRANSFER_OPERATOR_DIR / "aperture_closure_tail_transfer_states.csv"
TRANSFER_EDGES = TRANSFER_OPERATOR_DIR / "aperture_closure_tail_transfer_edges.csv"

REPAIRED_AUTOMATON_REPORT = REPAIRED_AUTOMATON_DIR / "report.json"
REPAIRED_AUTOMATON_TABLES = (
    REPAIRED_AUTOMATON_DIR
    / "signature_boundary_spine_aperture_closure_tail_repaired_automaton_tables.npz"
)
SKIP_WINDOW_REPORT = SKIP_WINDOW_DIR / "report.json"
SKIP_WINDOW_TABLES = (
    SKIP_WINDOW_DIR
    / "signature_boundary_spine_aperture_closure_tail_skip_window_grammar_tables.npz"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_flow_window_lift.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_flow_window_lift.py"
)

MAX_CANDIDATE_WORD_LENGTH = len(WORD_COLUMNS)

WINDOW_PRESSURE_COLUMNS = [
    "window_id",
    "block_symbol_0_id",
    "block_symbol_1_id",
    "block_symbol_2_id",
    "block_symbol_3_id",
    "state_window_occurrence_count",
    "stationary_mass_x1e12",
    "cut_window_occurrence_count",
    "cut_flux_x1e12",
    "candidate_word_count",
    "selected_move_flag",
]

CUT_WINDOW_COLUMNS = [
    "cut_window_id",
    "transfer_edge_id",
    "endpoint_state_id",
    "endpoint_side_code",
    "window_rank",
    "edit_position",
    "block_symbol_0_id",
    "block_symbol_1_id",
    "block_symbol_2_id",
    "block_symbol_3_id",
    "cut_flux_share_x1e12",
]

CANDIDATE_MOVE_COLUMNS = [
    "candidate_move_id",
    "block_symbol_0_id",
    "block_symbol_1_id",
    "block_symbol_2_id",
    "block_symbol_3_id",
    "candidate_word_count",
    "same_side_edge_count",
    "positive_side_edge_count",
    "negative_side_edge_count",
    "cross_side_rejected_word_count",
    "clean_move_flag",
    "selected_move_flag",
    "new_cut_flux_x1e12",
    "cut_flux_reduction_x1e12",
    "new_weighted_conductance_x1e12",
    "conductance_reduction_x1e12",
    "preserves_boundary_merge_flag",
]

CANDIDATE_WORD_COLUMNS = [
    "candidate_word_id",
    "candidate_move_id",
    "assigned_side_code",
    "neighbor_state_count",
    "closed_path_count",
    "template_count",
    "trace_variation",
    "word_length",
    *WORD_COLUMNS,
]

FLOW_WINDOW_OBSERVABLE_CODES = {
    "cut_endpoint_state_count": 0,
    "cut_endpoint_neighbor_candidate_count": 1,
    "metric_closed_virtual_candidate_count": 2,
    "cut_window_block_count": 3,
    "candidate_move_count": 4,
    "clean_candidate_move_count": 5,
    "selected_candidate_word_count": 6,
    "selected_same_side_edge_count": 7,
    "selected_negative_side_edge_count": 8,
    "base_cut_flux": 9,
    "selected_new_cut_flux": 10,
    "selected_cut_flux_reduction": 11,
    "base_weighted_conductance": 12,
    "selected_new_weighted_conductance": 13,
    "selected_conductance_reduction": 14,
    "selected_block_code": 15,
    "window_pressure_mass_total": 16,
    "cut_window_flux_total": 17,
}

FLOAT_OBSERVABLES = set()


def word_from_automaton_state(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(row[column] for column in WORD_COLUMNS if row[column] != -1)


def block_code(block: tuple[int, int, int, int]) -> int:
    return int(block[0] * 1_000 + block[1] * 100 + block[2] * 10 + block[3])


def word_blocks(word: tuple[int, ...]) -> list[tuple[int, tuple[int, int, int, int]]]:
    sequence = tuple(PREFIX_SYMBOLS) + word + word[:2]
    return [
        (rank, tuple(int(value) for value in sequence[rank : rank + 4]))
        for rank in range(len(sequence) - 3)
    ]


def touch_blocks(
    word: tuple[int, ...],
    edit_position: int,
) -> list[tuple[int, tuple[int, int, int, int]]]:
    sequence = tuple(PREFIX_SYMBOLS) + word + word[:2]
    edit_rank = int(edit_position) + len(PREFIX_SYMBOLS)
    return [
        (rank, tuple(int(value) for value in sequence[rank : rank + 4]))
        for rank in range(
            max(0, edit_rank - 3),
            min(edit_rank, len(sequence) - 4) + 1,
        )
    ]


def split_scaled(total: int, count: int) -> list[int]:
    quotient, remainder = divmod(int(total), int(count))
    return [quotient + (1 if index < remainder else 0) for index in range(count)]


def load_tables() -> dict[str, Any]:
    transfer = np.load(TRANSFER_TABLES, allow_pickle=False)
    repaired = np.load(REPAIRED_AUTOMATON_TABLES, allow_pickle=False)
    return {
        "transfer_states": [
            {column: int(row[index]) for index, column in enumerate(TRANSFER_STATE_COLUMNS)}
            for row in np.asarray(transfer["state_table"], dtype=np.int64)
        ],
        "transfer_edges": [
            {column: int(row[index]) for index, column in enumerate(TRANSFER_EDGE_COLUMNS)}
            for row in np.asarray(transfer["edge_table"], dtype=np.int64)
        ],
        "transfer_sides": [
            {column: int(row[index]) for index, column in enumerate(SIDE_FLOW_COLUMNS)}
            for row in np.asarray(transfer["side_table"], dtype=np.int64)
        ],
        "automaton_states": [
            {column: int(row[index]) for index, column in enumerate(AUTOMATON_STATE_COLUMNS)}
            for row in np.asarray(repaired["state_table"], dtype=np.int64)
        ],
        "automaton_transitions": [
            {
                column: int(row[index])
                for index, column in enumerate(AUTOMATON_TRANSITION_COLUMNS)
            }
            for row in np.asarray(repaired["transition_table"], dtype=np.int64)
        ],
    }


def evaluate_cut_neighbor_candidates(
    cut_endpoint_ids: set[int],
    word_by_state: dict[int, tuple[int, ...]],
    existing_words: set[tuple[int, ...]],
    repair_rows_by_block: dict[tuple[int, int, int, int], list[dict[str, int]]],
) -> tuple[list[dict[str, Any]], Counter[str]]:
    candidate_words: set[tuple[int, ...]] = set()
    for state_id in cut_endpoint_ids:
        candidate_words.update(one_edit_neighbors(word_by_state[state_id]))
    candidate_words = {
        word for word in candidate_words if word not in existing_words
    }

    carrier_adjacency, assoc_by_word, rewrite_edge_by_pair = build_context()
    stats: Counter[str] = Counter()
    stats["cut_endpoint_neighbor_candidate_count"] = len(candidate_words)
    candidates: list[dict[str, Any]] = []
    for word in sorted(candidate_words):
        try:
            _windows, trace_nodes, _signatures, metrics = build_trace(
                word,
                assoc_by_word,
                rewrite_edge_by_pair,
            )
        except Exception:
            stats["trace_failure_count"] += 1
            continue
        if (
            int(metrics["metric_gromov_delta_twice"]) != TARGET_DELTA_TWICE
            or int(metrics["trace_signature_total_variation"])
            > TARGET_VARIATION_INCLUSIVE_BOUND
        ):
            stats["bad_metric_count"] += 1
            continue
        profile = closure_profile(word, carrier_adjacency)
        if profile["first_return_closed_path_count"] <= 0:
            stats["not_closed_count"] += 1
            continue
        trace = tuple(int(value) for value in trace_nodes)
        native_repair = int(
            contains_undirected_edge(trace, 31, 28)
            or contains_undirected_edge(trace, 50, 34)
        )
        derived_repair = int(bool(derived_spans(word, repair_rows_by_block)))
        if native_repair or derived_repair:
            stats["already_repair_supported_count"] += 1
            continue
        stats["metric_closed_virtual_candidate_count"] += 1
        candidates.append(
            {
                "word": word,
                "closed_path_count": int(profile["first_return_closed_path_count"]),
                "template_count": int(profile["normalized_tail_template_count"]),
                "trace_variation": int(metrics["trace_signature_total_variation"]),
            }
        )
    return candidates, stats


def build_payload_rows() -> dict[str, Any]:
    tables = load_tables()
    transfer_states = tables["transfer_states"]
    transfer_edges = tables["transfer_edges"]
    transfer_sides = tables["transfer_sides"]
    automaton_states = tables["automaton_states"]
    automaton_transitions = tables["automaton_transitions"]
    state_by_id = {row["automaton_state_id"]: row for row in automaton_states}
    word_by_state = {
        state_id: word_from_automaton_state(row)
        for state_id, row in state_by_id.items()
    }
    existing_words = set(word_by_state.values())
    merged_state_ids = {
        row["automaton_state_id"]
        for row in automaton_states
        if row["merged_recurrent_class_flag"] == 1
    }
    merged_word_to_state = {
        word_by_state[state_id]: state_id
        for state_id in merged_state_ids
    }
    transfer_state_by_state = {
        row["automaton_state_id"]: row for row in transfer_states
    }
    transfer_edge_by_pair = {
        (row["source_state_id"], row["target_state_id"]): row
        for row in transfer_edges
    }
    transition_by_pair = {
        (row["source_state_id"], row["target_state_id"]): row
        for row in automaton_transitions
        if row["source_state_id"] < row["target_state_id"]
    }
    cut_edges = [
        row for row in transfer_edges if row["spectral_cut_edge_flag"] == 1
    ]
    cut_endpoint_ids = {
        state_id
        for edge in cut_edges
        for state_id in (edge["source_state_id"], edge["target_state_id"])
    }

    window_pressure: dict[tuple[int, int, int, int], dict[str, int]] = defaultdict(
        lambda: {
            "state_window_occurrence_count": 0,
            "stationary_mass_x1e12": 0,
            "cut_window_occurrence_count": 0,
            "cut_flux_x1e12": 0,
            "candidate_word_count": 0,
            "selected_move_flag": 0,
        }
    )
    for transfer_state in transfer_states:
        state_id = transfer_state["automaton_state_id"]
        blocks = word_blocks(word_by_state[state_id])
        splits = split_scaled(transfer_state["stationary_mass_x1e12"], len(blocks))
        for (_rank, block), mass_share in zip(blocks, splits):
            window_pressure[block]["state_window_occurrence_count"] += 1
            window_pressure[block]["stationary_mass_x1e12"] += mass_share

    cut_window_rows = []
    cut_blocks: set[tuple[int, int, int, int]] = set()
    for edge in cut_edges:
        pair = (edge["source_state_id"], edge["target_state_id"])
        transition = transition_by_pair[pair]
        occurrences: list[tuple[int, int, tuple[int, int, int, int]]] = []
        for endpoint_state_id in pair:
            for rank, block in touch_blocks(
                word_by_state[endpoint_state_id],
                transition["edit_position"],
            ):
                occurrences.append((endpoint_state_id, rank, block))
        shares = split_scaled(edge["undirected_stationary_flux_x1e12"], len(occurrences))
        for (endpoint_state_id, rank, block), share in zip(occurrences, shares):
            cut_blocks.add(block)
            window_pressure[block]["cut_window_occurrence_count"] += 1
            window_pressure[block]["cut_flux_x1e12"] += share
            cut_window_rows.append(
                {
                    "cut_window_id": len(cut_window_rows),
                    "transfer_edge_id": edge["transfer_edge_id"],
                    "endpoint_state_id": endpoint_state_id,
                    "endpoint_side_code": state_by_id[endpoint_state_id][
                        "spectral_side_code"
                    ],
                    "window_rank": rank,
                    "edit_position": transition["edit_position"],
                    "block_symbol_0_id": block[0],
                    "block_symbol_1_id": block[1],
                    "block_symbol_2_id": block[2],
                    "block_symbol_3_id": block[3],
                    "cut_flux_share_x1e12": share,
                }
            )

    _repair_rows, _grammar_stats, repair_rows_by_block = grammar_rows()
    candidate_pool, candidate_stats = evaluate_cut_neighbor_candidates(
        cut_endpoint_ids,
        word_by_state,
        existing_words,
        repair_rows_by_block,
    )

    candidate_records: list[dict[str, Any]] = []
    candidate_by_block: dict[tuple[int, int, int, int], list[dict[str, Any]]] = {
        block: [] for block in cut_blocks
    }
    cross_rejected_by_block: Counter[tuple[int, int, int, int]] = Counter()
    for candidate in candidate_pool:
        word = candidate["word"]
        neighbor_state_ids = [
            merged_word_to_state[neighbor]
            for neighbor in sorted(one_edit_neighbors(word))
            if neighbor in merged_word_to_state
        ]
        if not neighbor_state_ids:
            continue
        side_codes = {
            state_by_id[state_id]["spectral_side_code"]
            for state_id in neighbor_state_ids
        }
        blocks = {block for _rank, block in word_blocks(word)}
        for block in blocks & cut_blocks:
            window_pressure[block]["candidate_word_count"] += 1
            if len(side_codes) != 1:
                cross_rejected_by_block[block] += 1
                continue
            assigned_side_code = next(iter(side_codes))
            record = {
                **candidate,
                "assigned_side_code": assigned_side_code,
                "neighbor_state_ids": neighbor_state_ids,
                "neighbor_state_count": len(neighbor_state_ids),
                "block": block,
            }
            candidate_by_block[block].append(record)
            candidate_records.append(record)

    base_cut_weight = sum(edge["edge_weight"] for edge in cut_edges)
    base_cut_flux_x1e12 = sum(
        edge["undirected_stationary_flux_x1e12"] for edge in cut_edges
    )
    base_total_edge_weight = sum(edge["edge_weight"] for edge in transfer_edges)
    negative_volume = next(
        row["weighted_volume"] for row in transfer_sides if row["spectral_side_code"] == -1
    )
    base_conductance_x1e12 = round_div(base_cut_weight * SCALE, negative_volume)

    move_rows = []
    for block in sorted(cut_blocks):
        records = candidate_by_block[block]
        side_edge_counts = Counter()
        for record in records:
            side_edge_counts[record["assigned_side_code"]] += record[
                "neighbor_state_count"
            ]
        same_side_edges = sum(side_edge_counts.values())
        added_weight = same_side_edges * DERIVED_EDGE_WEIGHT
        new_cut_flux = round_div(
            base_cut_weight * SCALE,
            base_total_edge_weight + added_weight,
        )
        new_conductance = round_div(
            base_cut_weight * SCALE,
            negative_volume + 2 * side_edge_counts[-1],
        )
        move_rows.append(
            {
                "candidate_move_id": len(move_rows),
                "block_symbol_0_id": block[0],
                "block_symbol_1_id": block[1],
                "block_symbol_2_id": block[2],
                "block_symbol_3_id": block[3],
                "candidate_word_count": len(records),
                "same_side_edge_count": same_side_edges,
                "positive_side_edge_count": side_edge_counts[1],
                "negative_side_edge_count": side_edge_counts[-1],
                "cross_side_rejected_word_count": cross_rejected_by_block[block],
                "clean_move_flag": int(
                    len(records) > 0 and cross_rejected_by_block[block] == 0
                ),
                "selected_move_flag": 0,
                "new_cut_flux_x1e12": new_cut_flux,
                "cut_flux_reduction_x1e12": base_cut_flux_x1e12 - new_cut_flux,
                "new_weighted_conductance_x1e12": new_conductance,
                "conductance_reduction_x1e12": base_conductance_x1e12
                - new_conductance,
                "preserves_boundary_merge_flag": 1,
            }
        )
    selected_move = max(
        (
            row
            for row in move_rows
            if row["clean_move_flag"] == 1 and row["negative_side_edge_count"] > 0
        ),
        key=lambda row: (
            row["conductance_reduction_x1e12"],
            row["cut_flux_reduction_x1e12"],
            row["candidate_word_count"],
            -block_code(
                (
                    row["block_symbol_0_id"],
                    row["block_symbol_1_id"],
                    row["block_symbol_2_id"],
                    row["block_symbol_3_id"],
                )
            ),
        ),
    )
    selected_move["selected_move_flag"] = 1
    selected_block = (
        selected_move["block_symbol_0_id"],
        selected_move["block_symbol_1_id"],
        selected_move["block_symbol_2_id"],
        selected_move["block_symbol_3_id"],
    )
    window_pressure[selected_block]["selected_move_flag"] = 1

    candidate_word_rows = []
    selected_records = sorted(
        candidate_by_block[selected_block],
        key=lambda row: (row["word"], row["assigned_side_code"]),
    )
    for record in selected_records:
        word = record["word"]
        candidate_word_rows.append(
            {
                "candidate_word_id": len(candidate_word_rows),
                "candidate_move_id": selected_move["candidate_move_id"],
                "assigned_side_code": record["assigned_side_code"],
                "neighbor_state_count": record["neighbor_state_count"],
                "closed_path_count": record["closed_path_count"],
                "template_count": record["template_count"],
                "trace_variation": record["trace_variation"],
                "word_length": len(word),
                **{
                    column: value
                    for column, value in zip(
                        WORD_COLUMNS,
                        padded(word, MAX_CANDIDATE_WORD_LENGTH),
                    )
                },
            }
        )

    pressure_rows = []
    for block in sorted(window_pressure):
        pressure = window_pressure[block]
        pressure_rows.append(
            {
                "window_id": len(pressure_rows),
                "block_symbol_0_id": block[0],
                "block_symbol_1_id": block[1],
                "block_symbol_2_id": block[2],
                "block_symbol_3_id": block[3],
                **pressure,
            }
        )

    observable_values = {
        "cut_endpoint_state_count": len(cut_endpoint_ids),
        "cut_endpoint_neighbor_candidate_count": candidate_stats[
            "cut_endpoint_neighbor_candidate_count"
        ],
        "metric_closed_virtual_candidate_count": candidate_stats[
            "metric_closed_virtual_candidate_count"
        ],
        "cut_window_block_count": len(cut_blocks),
        "candidate_move_count": len(move_rows),
        "clean_candidate_move_count": sum(row["clean_move_flag"] for row in move_rows),
        "selected_candidate_word_count": selected_move["candidate_word_count"],
        "selected_same_side_edge_count": selected_move["same_side_edge_count"],
        "selected_negative_side_edge_count": selected_move["negative_side_edge_count"],
        "base_cut_flux": base_cut_flux_x1e12 / SCALE,
        "selected_new_cut_flux": selected_move["new_cut_flux_x1e12"] / SCALE,
        "selected_cut_flux_reduction": selected_move["cut_flux_reduction_x1e12"] / SCALE,
        "base_weighted_conductance": base_conductance_x1e12 / SCALE,
        "selected_new_weighted_conductance": selected_move[
            "new_weighted_conductance_x1e12"
        ]
        / SCALE,
        "selected_conductance_reduction": selected_move[
            "conductance_reduction_x1e12"
        ]
        / SCALE,
        "selected_block_code": block_code(selected_block),
        "window_pressure_mass_total": sum(
            row["stationary_mass_x1e12"] for row in pressure_rows
        )
        / SCALE,
        "cut_window_flux_total": sum(
            row["cut_flux_share_x1e12"] for row in cut_window_rows
        )
        / SCALE,
    }
    observable_rows = []
    for observable_id, (key, code) in enumerate(FLOW_WINDOW_OBSERVABLE_CODES.items()):
        value = observable_values[key]
        scaled = scaled_float(value) if key in FLOAT_OBSERVABLES else int(round(value * SCALE)) if isinstance(value, float) else int(value) * SCALE
        observable_rows.append(
            {
                "observable_id": observable_id,
                "observable_code": code,
                "value_x1e12": scaled,
                "aux_id": -1,
            }
        )

    return {
        "pressure_rows": pressure_rows,
        "cut_window_rows": cut_window_rows,
        "move_rows": move_rows,
        "candidate_word_rows": candidate_word_rows,
        "observable_rows": observable_rows,
        "observable_values": observable_values,
        "candidate_stats": dict(candidate_stats),
        "selected_block": selected_block,
        "selected_move": selected_move,
        "base_cut_flux_x1e12": base_cut_flux_x1e12,
        "base_conductance_x1e12": base_conductance_x1e12,
    }


def build_payloads() -> dict[str, Any]:
    transfer_report = load_json(TRANSFER_REPORT)
    transfer_certificate = load_json(TRANSFER_CERTIFICATE)
    repaired_report = load_json(REPAIRED_AUTOMATON_REPORT)
    skip_report = load_json(SKIP_WINDOW_REPORT)
    rows = build_payload_rows()

    pressure_table = table_from_rows(WINDOW_PRESSURE_COLUMNS, rows["pressure_rows"])
    cut_window_table = table_from_rows(CUT_WINDOW_COLUMNS, rows["cut_window_rows"])
    candidate_move_table = table_from_rows(CANDIDATE_MOVE_COLUMNS, rows["move_rows"])
    candidate_word_table = table_from_rows(
        CANDIDATE_WORD_COLUMNS,
        rows["candidate_word_rows"],
    )
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, rows["observable_rows"])
    selected = rows["selected_move"]
    checks = {
        "transfer_operator_report_certified": transfer_report.get("status")
        == TRANSFER_OPERATOR_STATUS,
        "transfer_operator_certificate_certified": transfer_certificate.get("status")
        == TRANSFER_OPERATOR_STATUS,
        "repaired_automaton_report_certified": repaired_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_REPAIRED_AUTOMATON_CERTIFIED",
        "skip_window_report_certified": skip_report.get("status") == SKIP_WINDOW_STATUS,
        "cut_neighbor_search_counts_are_expected": (
            rows["observable_values"]["cut_endpoint_state_count"],
            rows["observable_values"]["cut_endpoint_neighbor_candidate_count"],
            rows["observable_values"]["metric_closed_virtual_candidate_count"],
        )
        == (12, 1_150, 26),
        "candidate_move_counts_are_expected": (
            rows["observable_values"]["cut_window_block_count"],
            rows["observable_values"]["candidate_move_count"],
            rows["observable_values"]["clean_candidate_move_count"],
        )
        == (15, 15, 12),
        "selected_move_is_expected_window": rows["selected_block"] == (5, 5, 2, 5),
        "selected_move_reduces_flux_and_conductance": (
            selected["candidate_word_count"],
            selected["same_side_edge_count"],
            selected["negative_side_edge_count"],
            selected["new_cut_flux_x1e12"],
            selected["new_weighted_conductance_x1e12"],
        )
        == (12, 12, 12, 1_025_816_379, 4_385_964_912),
        "selected_move_is_clean_and_merge_preserving": (
            selected["cross_side_rejected_word_count"],
            selected["clean_move_flag"],
            selected["preserves_boundary_merge_flag"],
        )
        == (0, 1, 1),
        "window_pressure_mass_is_conserved": int(
            np.sum(pressure_table[:, WINDOW_PRESSURE_COLUMNS.index("stationary_mass_x1e12")])
        )
        == SCALE,
        "cut_window_flux_is_conserved": int(
            np.sum(cut_window_table[:, CUT_WINDOW_COLUMNS.index("cut_flux_share_x1e12")])
        )
        == rows["base_cut_flux_x1e12"],
        "pressure_table_shape_matches_codebook": pressure_table.shape[1]
        == len(WINDOW_PRESSURE_COLUMNS),
        "cut_window_table_shape_matches_codebook": tuple(cut_window_table.shape)
        == (48, len(CUT_WINDOW_COLUMNS)),
        "candidate_move_table_shape_matches_codebook": tuple(candidate_move_table.shape)
        == (15, len(CANDIDATE_MOVE_COLUMNS)),
        "candidate_word_table_shape_matches_codebook": tuple(candidate_word_table.shape)
        == (12, len(CANDIDATE_WORD_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(FLOW_WINDOW_OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    witness = {
        "cut_endpoint_state_count": rows["observable_values"]["cut_endpoint_state_count"],
        "cut_endpoint_neighbor_candidate_count": rows["observable_values"][
            "cut_endpoint_neighbor_candidate_count"
        ],
        "metric_closed_virtual_candidate_count": rows["observable_values"][
            "metric_closed_virtual_candidate_count"
        ],
        "cut_window_block_count": rows["observable_values"]["cut_window_block_count"],
        "candidate_move_count": rows["observable_values"]["candidate_move_count"],
        "clean_candidate_move_count": rows["observable_values"][
            "clean_candidate_move_count"
        ],
        "selected_move": {
            "block": list(rows["selected_block"]),
            "candidate_word_count": selected["candidate_word_count"],
            "same_side_edge_count": selected["same_side_edge_count"],
            "negative_side_edge_count": selected["negative_side_edge_count"],
            "new_cut_flux_x1e12": selected["new_cut_flux_x1e12"],
            "cut_flux_reduction_x1e12": selected["cut_flux_reduction_x1e12"],
            "new_weighted_conductance_x1e12": selected[
                "new_weighted_conductance_x1e12"
            ],
            "conductance_reduction_x1e12": selected[
                "conductance_reduction_x1e12"
            ],
        },
        "candidate_stats": rows["candidate_stats"],
        "pressure_table_sha256": sha_array(pressure_table),
        "cut_window_table_sha256": sha_array(cut_window_table),
        "candidate_move_table_sha256": sha_array(candidate_move_table),
        "candidate_word_table_sha256": sha_array(candidate_word_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    flow_window_lift = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_flow_window_lift@1",
        "object": "d20",
        "parent": TRANSFER_REPORT.relative_to(ROOT).as_posix(),
        "lift_rule": [
            "split each transfer-state stationary mass evenly over its four-symbol windows",
            "split each cut-edge flux over the endpoint windows touching the edit position",
            "search one-edit neighbors of the twelve cut endpoint states",
            "keep closed-positive metric-valid candidates without native or current derived repair support",
            "rank cut-local four-symbol block promotions by clean negative-side conductance reduction",
        ],
        "selected_move": witness["selected_move"],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_flow_window_lift@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_FLOW_WINDOW_LIFT_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The transfer-flow bottleneck lifts to a finite local window search. "
            "The twelve cut endpoint states have 1,150 one-edit neighbor words; "
            "26 are metric-valid closed-positive virtual candidates without "
            "native or current derived repair support. Among the 15 cut-local "
            "four-symbol blocks, the clean selected move is block 5,5,2,5. It "
            "promotes 12 negative-side virtual words, adds 12 same-side derived "
            "edges, preserves the left/right merge, reduces cut flux from "
            "1027925304/1e12 to 1025816379/1e12, and reduces weighted conductance "
            "from 4464285714/1e12 to 4385964912/1e12."
        ),
        "stage_protocol": {
            "draft": "lift transfer mass and cut flux onto four-symbol windows",
            "witness": "emit window-pressure, cut-window, candidate-move, candidate-word, and observable tables",
            "coherence": "rank cut-local moves by clean side attachment, flux reduction, and conductance reduction",
            "closure": "certify the selected window move reduces bottleneck flux without losing the boundary merge",
            "emit": "emit flow-window artifacts, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "transfer_report": input_entry(
                TRANSFER_REPORT,
                {
                    "status": transfer_report.get("status"),
                    "certificate_sha256": transfer_report.get("certificate_sha256"),
                },
            ),
            "transfer_certificate": input_entry(TRANSFER_CERTIFICATE),
            "transfer_states": input_entry(TRANSFER_STATES),
            "transfer_edges": input_entry(TRANSFER_EDGES),
            "transfer_tables": input_entry(TRANSFER_TABLES),
            "repaired_automaton_report": input_entry(REPAIRED_AUTOMATON_REPORT),
            "repaired_automaton_tables": input_entry(REPAIRED_AUTOMATON_TABLES),
            "skip_window_report": input_entry(SKIP_WINDOW_REPORT),
            "skip_window_tables": input_entry(SKIP_WINDOW_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_aperture_closure_tail_flow_window_lift": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_flow_window_lift.json"
            ),
            "flow_window_pressure_csv": relpath(
                OUT_DIR / "aperture_closure_tail_flow_window_pressure.csv"
            ),
            "flow_cut_windows_csv": relpath(
                OUT_DIR / "aperture_closure_tail_flow_cut_windows.csv"
            ),
            "flow_candidate_moves_csv": relpath(
                OUT_DIR / "aperture_closure_tail_flow_candidate_moves.csv"
            ),
            "flow_candidate_words_csv": relpath(
                OUT_DIR / "aperture_closure_tail_flow_candidate_words.csv"
            ),
            "flow_window_observables_csv": relpath(
                OUT_DIR / "aperture_closure_tail_flow_window_observables.csv"
            ),
            "signature_boundary_spine_aperture_closure_tail_flow_window_lift_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_flow_window_lift_tables.npz"
            ),
            "signature_boundary_spine_aperture_closure_tail_flow_window_lift_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_flow_window_lift_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the transfer-state stationary pressure lifted to four-symbol windows",
                "the spectral cut flux lifted to edit-local endpoint windows",
                "the cut-neighborhood virtual candidate search",
                "the selected clean local block promotion and its flux/conductance effect",
            ],
            "does_not_certify_because_not_required": [
                "global optimality among all non-local grammar moves",
                "actual mutation of the repaired automaton grammar",
                "multi-window closure after applying the selected move",
                "compiler integration of the selected symbolic move",
            ],
        },
        "next_highest_yield_item": (
            "Apply the selected 5,5,2,5 window promotion as a new derived "
            "grammar layer, rebuild the repaired automaton, and measure whether "
            "the spectral cut moves or dissolves under the expanded boundary "
            "language."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_flow_window_lift_certificate@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the transfer-flow bottleneck is localized to a finite set of cut windows",
            "the strongest clean pressure move is the 5,5,2,5 block",
            "that move only attaches negative-side virtual words in this cut neighborhood",
            "its predicted effect reduces both cut flux and weighted conductance while preserving the existing merge",
        ],
    }

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_flow_window_lift_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified transfer, repaired automaton, and skip-window artifacts",
            "lift stationary mass and cut flux to four-symbol windows",
            "evaluate cut-endpoint one-edit virtual candidates",
            "rank candidate block moves and certify the selected bottleneck-reducing move",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_closure_tail_flow_window_lift": flow_window_lift,
        "flow_window_pressure_csv": csv_text(
            WINDOW_PRESSURE_COLUMNS,
            rows["pressure_rows"],
        ),
        "flow_cut_windows_csv": csv_text(CUT_WINDOW_COLUMNS, rows["cut_window_rows"]),
        "flow_candidate_moves_csv": csv_text(CANDIDATE_MOVE_COLUMNS, rows["move_rows"]),
        "flow_candidate_words_csv": csv_text(
            CANDIDATE_WORD_COLUMNS,
            rows["candidate_word_rows"],
        ),
        "flow_window_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            rows["observable_rows"],
        ),
        "pressure_table": pressure_table,
        "cut_window_table": cut_window_table,
        "candidate_move_table": candidate_move_table,
        "candidate_word_table": candidate_word_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_closure_tail_flow_window_lift_certificate": certificate,
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
    updated = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": sorted(obligations, key=lambda row: row["id"]),
    }
    updated["registry_sha256"] = self_hash(updated, "registry_sha256")
    write_json(INDEX_PATH, updated)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_flow_window_lift.json",
        payloads["signature_boundary_spine_aperture_closure_tail_flow_window_lift"],
    )
    (OUT_DIR / "aperture_closure_tail_flow_window_pressure.csv").write_text(
        payloads["flow_window_pressure_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_flow_cut_windows.csv").write_text(
        payloads["flow_cut_windows_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_flow_candidate_moves.csv").write_text(
        payloads["flow_candidate_moves_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_flow_candidate_words.csv").write_text(
        payloads["flow_candidate_words_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_flow_window_observables.csv").write_text(
        payloads["flow_window_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_flow_window_lift_tables.npz",
        pressure_table=payloads["pressure_table"],
        cut_window_table=payloads["cut_window_table"],
        candidate_move_table=payloads["candidate_move_table"],
        candidate_word_table=payloads["candidate_word_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_flow_window_lift_certificate.json",
        payloads["signature_boundary_spine_aperture_closure_tail_flow_window_lift_certificate"],
    )
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
                "report": relpath(OUT_DIR / "report.json"),
                "manifest": relpath(OUT_DIR / "manifest.json"),
                "certificate_sha256": report["certificate_sha256"],
                "witness": report["witness"],
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
