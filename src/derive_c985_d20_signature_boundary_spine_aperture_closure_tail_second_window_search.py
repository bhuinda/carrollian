from __future__ import annotations

import json
from collections import Counter
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_flow_window_lift import (
        block_code,
        split_scaled,
        touch_blocks,
        word_blocks,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_promoted_transfer_operator import (
        OUT_DIR as PROMOTED_TRANSFER_DIR,
        SIDE_FLOW_COLUMNS,
        STATUS as PROMOTED_TRANSFER_STATUS,
        TRANSFER_EDGE_COLUMNS,
        TRANSFER_STATE_COLUMNS,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_promoted_window import (
        EDGE_COLUMNS as PROMOTED_EDGE_COLUMNS,
        OUT_DIR as PROMOTED_WINDOW_DIR,
        PROMOTED_BLOCK,
        STATE_COLUMNS as PROMOTED_STATE_COLUMNS,
        STATUS as PROMOTED_WINDOW_STATUS,
        csv_text,
        input_entry,
        load_json,
        relpath,
        self_hash,
        sha_array,
        table_from_rows,
        write_json,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_skip_window_grammar import (
        OBSERVABLE_COLUMNS,
        TARGET_DELTA_TWICE,
        TARGET_VARIATION_INCLUSIVE_BOUND,
        WORD_COLUMNS,
        build_context,
        build_trace,
        closure_profile,
        contains_undirected_edge,
        derived_spans,
        grammar_rows,
        one_edit_neighbors,
        padded,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_transfer_operator import (
        DERIVED_EDGE_WEIGHT,
        SCALE,
        round_div,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_flow_window_lift import (
        block_code,
        split_scaled,
        touch_blocks,
        word_blocks,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_promoted_transfer_operator import (
        OUT_DIR as PROMOTED_TRANSFER_DIR,
        SIDE_FLOW_COLUMNS,
        STATUS as PROMOTED_TRANSFER_STATUS,
        TRANSFER_EDGE_COLUMNS,
        TRANSFER_STATE_COLUMNS,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_promoted_window import (
        EDGE_COLUMNS as PROMOTED_EDGE_COLUMNS,
        OUT_DIR as PROMOTED_WINDOW_DIR,
        PROMOTED_BLOCK,
        STATE_COLUMNS as PROMOTED_STATE_COLUMNS,
        STATUS as PROMOTED_WINDOW_STATUS,
        csv_text,
        input_entry,
        load_json,
        relpath,
        self_hash,
        sha_array,
        table_from_rows,
        write_json,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_skip_window_grammar import (
        OBSERVABLE_COLUMNS,
        TARGET_DELTA_TWICE,
        TARGET_VARIATION_INCLUSIVE_BOUND,
        WORD_COLUMNS,
        build_context,
        build_trace,
        closure_profile,
        contains_undirected_edge,
        derived_spans,
        grammar_rows,
        one_edit_neighbors,
        padded,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_transfer_operator import (
        DERIVED_EDGE_WEIGHT,
        SCALE,
        round_div,
    )
    from derive_c985_typed_simple_object_registry import INDEX_PATH
    from paths import D20_INVARIANTS, ROOT


THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_search"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_SECOND_WINDOW_SEARCH_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

PROMOTED_TRANSFER_REPORT = PROMOTED_TRANSFER_DIR / "report.json"
PROMOTED_TRANSFER_CERTIFICATE = (
    PROMOTED_TRANSFER_DIR
    / "signature_boundary_spine_aperture_closure_tail_promoted_transfer_operator_certificate.json"
)
PROMOTED_TRANSFER_TABLES = (
    PROMOTED_TRANSFER_DIR
    / "signature_boundary_spine_aperture_closure_tail_promoted_transfer_operator_tables.npz"
)
PROMOTED_WINDOW_REPORT = PROMOTED_WINDOW_DIR / "report.json"
PROMOTED_WINDOW_CERTIFICATE = (
    PROMOTED_WINDOW_DIR
    / "signature_boundary_spine_aperture_closure_tail_promoted_window_certificate.json"
)
PROMOTED_WINDOW_TABLES = (
    PROMOTED_WINDOW_DIR
    / "signature_boundary_spine_aperture_closure_tail_promoted_window_tables.npz"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_search.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_search.py"
)

SOURCE_WORD_COLUMNS = [
    column.replace("word_", "source_word_") for column in WORD_COLUMNS
]
TARGET_WORD_COLUMNS = [
    column.replace("word_", "target_word_") for column in WORD_COLUMNS
]

CUT_EDGE_COLUMNS = [
    "cut_rank_id",
    "transfer_edge_id",
    "source_state_id",
    "target_state_id",
    "source_side_code",
    "target_side_code",
    "edge_weight",
    "undirected_stationary_flux_x1e12",
    "old_spectral_cut_edge_flag",
    "promoted_transition_flag",
    "promoted_only_transition_flag",
    "target_unpromoted_old_cut_edge_flag",
    "edit_position",
    "source_symbol_id",
    "target_symbol_id",
    "source_word_length",
    *SOURCE_WORD_COLUMNS,
    "target_word_length",
    *TARGET_WORD_COLUMNS,
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
    "new_target_cut_flux_x1e12",
    "target_cut_flux_reduction_x1e12",
    "new_target_weighted_conductance_x1e12",
    "target_conductance_reduction_x1e12",
]

CANDIDATE_WORD_COLUMNS = [
    "candidate_word_id",
    "candidate_move_id",
    "assigned_side_code",
    "neighbor_state_count",
    "neighbor_state_id_min",
    "closed_path_count",
    "template_count",
    "trace_variation",
    "word_length",
    *WORD_COLUMNS,
]

SECOND_WINDOW_OBSERVABLE_CODES = {
    "surviving_cut_edge_count": 0,
    "promoted_support_cut_edge_count": 1,
    "unpromoted_old_cut_edge_count": 2,
    "target_transfer_edge_id": 3,
    "target_cut_flux": 4,
    "target_endpoint_state_count": 5,
    "target_neighbor_candidate_count": 6,
    "target_trace_failure_count": 7,
    "target_bad_metric_count": 8,
    "target_not_closed_count": 9,
    "target_already_supported_count": 10,
    "target_metric_closed_virtual_count": 11,
    "target_cut_window_block_count": 12,
    "candidate_move_count": 13,
    "clean_candidate_move_count": 14,
    "selected_block_code": 15,
    "selected_candidate_word_count": 16,
    "selected_same_side_edge_count": 17,
    "selected_negative_side_edge_count": 18,
    "selected_target_cut_flux_reduction": 19,
    "selected_target_conductance_reduction": 20,
}

FLOAT_OBSERVABLES = set()


def table_rows(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def word_from_state(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(row[column] for column in WORD_COLUMNS if row[column] != -1)


def contains_promoted_block(word: tuple[int, ...]) -> bool:
    return any(block == PROMOTED_BLOCK for _rank, block in word_blocks(word))


def load_rows() -> dict[str, Any]:
    promoted_tables = np.load(PROMOTED_WINDOW_TABLES, allow_pickle=False)
    transfer_tables = np.load(PROMOTED_TRANSFER_TABLES, allow_pickle=False)
    return {
        "promoted_states": table_rows(
            np.asarray(promoted_tables["state_table"], dtype=np.int64),
            PROMOTED_STATE_COLUMNS,
        ),
        "promoted_edges": table_rows(
            np.asarray(promoted_tables["edge_table"], dtype=np.int64),
            PROMOTED_EDGE_COLUMNS,
        ),
        "transfer_states": table_rows(
            np.asarray(transfer_tables["state_table"], dtype=np.int64),
            TRANSFER_STATE_COLUMNS,
        ),
        "transfer_edges": table_rows(
            np.asarray(transfer_tables["edge_table"], dtype=np.int64),
            TRANSFER_EDGE_COLUMNS,
        ),
        "transfer_sides": table_rows(
            np.asarray(transfer_tables["side_table"], dtype=np.int64),
            SIDE_FLOW_COLUMNS,
        ),
    }


def evaluate_candidates(
    endpoint_state_ids: set[int],
    word_by_state: dict[int, tuple[int, ...]],
    existing_words: set[tuple[int, ...]],
    repair_rows_by_block: dict[
        tuple[int, int, int, int],
        list[dict[str, int]],
    ],
) -> tuple[list[dict[str, Any]], Counter[str]]:
    candidate_words: set[tuple[int, ...]] = set()
    for state_id in endpoint_state_ids:
        candidate_words.update(one_edit_neighbors(word_by_state[state_id]))
    candidate_words = {word for word in candidate_words if word not in existing_words}

    carrier_adjacency, assoc_by_word, rewrite_edge_by_pair = build_context()
    stats: Counter[str] = Counter()
    stats["target_neighbor_candidate_count"] = len(candidate_words)
    candidates = []
    for word in sorted(candidate_words):
        try:
            _windows, trace_nodes, _signatures, metrics = build_trace(
                word,
                assoc_by_word,
                rewrite_edge_by_pair,
            )
        except Exception:
            stats["target_trace_failure_count"] += 1
            continue
        if (
            int(metrics["metric_gromov_delta_twice"]) != TARGET_DELTA_TWICE
            or int(metrics["trace_signature_total_variation"])
            > TARGET_VARIATION_INCLUSIVE_BOUND
        ):
            stats["target_bad_metric_count"] += 1
            continue
        profile = closure_profile(word, carrier_adjacency)
        if profile["first_return_closed_path_count"] <= 0:
            stats["target_not_closed_count"] += 1
            continue
        trace = tuple(int(value) for value in trace_nodes)
        native_repair = int(
            contains_undirected_edge(trace, 31, 28)
            or contains_undirected_edge(trace, 50, 34)
        )
        skip_repair = int(bool(derived_spans(word, repair_rows_by_block)))
        promoted_repair = int(contains_promoted_block(word))
        if native_repair or skip_repair or promoted_repair:
            stats["target_already_supported_count"] += 1
            continue
        stats["target_metric_closed_virtual_count"] += 1
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
    source = load_rows()
    promoted_states = source["promoted_states"]
    promoted_edges = source["promoted_edges"]
    transfer_edges = source["transfer_edges"]
    transfer_sides = source["transfer_sides"]
    state_by_id = {row["automaton_state_id"]: row for row in promoted_states}
    word_by_state = {
        state_id: word_from_state(row) for state_id, row in state_by_id.items()
    }
    existing_words = set(word_by_state.values())

    promoted_edge_by_pair = {
        (row["source_state_id"], row["target_state_id"]): row
        for row in promoted_edges
    }
    cut_edges = [row for row in transfer_edges if row["spectral_cut_edge_flag"] == 1]
    target_edges = [
        row
        for row in cut_edges
        if row["old_spectral_cut_edge_flag"] == 1
        and row["promoted_transition_flag"] == 0
    ]
    if len(target_edges) != 1:
        raise AssertionError("expected a unique unpromoted old cut edge")
    target_edge = target_edges[0]

    cut_edge_rows = []
    for rank, transfer_edge in enumerate(
        sorted(
            cut_edges,
            key=lambda row: (
                -row["undirected_stationary_flux_x1e12"],
                row["transfer_edge_id"],
            ),
        )
    ):
        pair = (transfer_edge["source_state_id"], transfer_edge["target_state_id"])
        promoted_edge = promoted_edge_by_pair[pair]
        source_word = word_by_state[pair[0]]
        target_word = word_by_state[pair[1]]
        cut_edge_rows.append(
            {
                "cut_rank_id": rank,
                "transfer_edge_id": transfer_edge["transfer_edge_id"],
                "source_state_id": pair[0],
                "target_state_id": pair[1],
                "source_side_code": state_by_id[pair[0]]["spectral_side_code"],
                "target_side_code": state_by_id[pair[1]]["spectral_side_code"],
                "edge_weight": transfer_edge["edge_weight"],
                "undirected_stationary_flux_x1e12": transfer_edge[
                    "undirected_stationary_flux_x1e12"
                ],
                "old_spectral_cut_edge_flag": transfer_edge[
                    "old_spectral_cut_edge_flag"
                ],
                "promoted_transition_flag": transfer_edge["promoted_transition_flag"],
                "promoted_only_transition_flag": transfer_edge[
                    "promoted_only_transition_flag"
                ],
                "target_unpromoted_old_cut_edge_flag": int(
                    transfer_edge["transfer_edge_id"]
                    == target_edge["transfer_edge_id"]
                ),
                "edit_position": promoted_edge["edit_position"],
                "source_symbol_id": promoted_edge["source_symbol_id"],
                "target_symbol_id": promoted_edge["target_symbol_id"],
                "source_word_length": len(source_word),
                **{
                    column: value
                    for column, value in zip(
                        SOURCE_WORD_COLUMNS,
                        padded(source_word, len(WORD_COLUMNS)),
                    )
                },
                "target_word_length": len(target_word),
                **{
                    column: value
                    for column, value in zip(
                        TARGET_WORD_COLUMNS,
                        padded(target_word, len(WORD_COLUMNS)),
                    )
                },
            }
        )

    target_pair = (
        target_edge["source_state_id"],
        target_edge["target_state_id"],
    )
    target_promoted_edge = promoted_edge_by_pair[target_pair]
    target_endpoint_ids = set(target_pair)
    _repair_rows, _grammar_stats, repair_rows_by_block = grammar_rows()
    candidate_pool, candidate_stats = evaluate_candidates(
        target_endpoint_ids,
        word_by_state,
        existing_words,
        repair_rows_by_block,
    )

    cut_window_rows = []
    cut_blocks: set[tuple[int, int, int, int]] = set()
    occurrences: list[tuple[int, int, tuple[int, int, int, int]]] = []
    for endpoint_state_id in target_pair:
        for rank, block in touch_blocks(
            word_by_state[endpoint_state_id],
            target_promoted_edge["edit_position"],
        ):
            occurrences.append((endpoint_state_id, rank, block))
    shares = split_scaled(
        target_edge["undirected_stationary_flux_x1e12"],
        len(occurrences),
    )
    for (endpoint_state_id, rank, block), share in zip(occurrences, shares):
        cut_blocks.add(block)
        cut_window_rows.append(
            {
                "cut_window_id": len(cut_window_rows),
                "transfer_edge_id": target_edge["transfer_edge_id"],
                "endpoint_state_id": endpoint_state_id,
                "endpoint_side_code": state_by_id[endpoint_state_id][
                    "spectral_side_code"
                ],
                "window_rank": rank,
                "edit_position": target_promoted_edge["edit_position"],
                "block_symbol_0_id": block[0],
                "block_symbol_1_id": block[1],
                "block_symbol_2_id": block[2],
                "block_symbol_3_id": block[3],
                "cut_flux_share_x1e12": share,
            }
        )

    merged_word_to_state = {
        word_by_state[row["automaton_state_id"]]: row["automaton_state_id"]
        for row in promoted_states
        if row["merged_recurrent_class_flag"] == 1
    }
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
            if len(side_codes) != 1:
                cross_rejected_by_block[block] += 1
                continue
            record = {
                **candidate,
                "assigned_side_code": next(iter(side_codes)),
                "neighbor_state_ids": neighbor_state_ids,
                "neighbor_state_count": len(neighbor_state_ids),
                "block": block,
            }
            candidate_by_block[block].append(record)
            candidate_records.append(record)

    base_cut_weight = target_edge["edge_weight"]
    base_cut_flux_x1e12 = target_edge["undirected_stationary_flux_x1e12"]
    base_total_edge_weight = sum(edge["edge_weight"] for edge in transfer_edges)
    negative_volume = next(
        row["weighted_volume"]
        for row in transfer_sides
        if row["spectral_side_code"] == -1
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
                "new_target_cut_flux_x1e12": new_cut_flux,
                "target_cut_flux_reduction_x1e12": base_cut_flux_x1e12
                - new_cut_flux,
                "new_target_weighted_conductance_x1e12": new_conductance,
                "target_conductance_reduction_x1e12": base_conductance_x1e12
                - new_conductance,
            }
        )

    selected_move = max(
        (
            row
            for row in move_rows
            if row["clean_move_flag"] == 1 and row["negative_side_edge_count"] > 0
        ),
        key=lambda row: (
            row["target_conductance_reduction_x1e12"],
            row["target_cut_flux_reduction_x1e12"],
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
    candidate_word_rows = []
    for record in sorted(
        candidate_by_block[selected_block],
        key=lambda row: (row["word"], row["assigned_side_code"]),
    ):
        word = record["word"]
        candidate_word_rows.append(
            {
                "candidate_word_id": len(candidate_word_rows),
                "candidate_move_id": selected_move["candidate_move_id"],
                "assigned_side_code": record["assigned_side_code"],
                "neighbor_state_count": record["neighbor_state_count"],
                "neighbor_state_id_min": min(record["neighbor_state_ids"]),
                "closed_path_count": record["closed_path_count"],
                "template_count": record["template_count"],
                "trace_variation": record["trace_variation"],
                "word_length": len(word),
                **{
                    column: value
                    for column, value in zip(
                        WORD_COLUMNS,
                        padded(word, len(WORD_COLUMNS)),
                    )
                },
            }
        )

    observable_values = {
        "surviving_cut_edge_count": len(cut_edges),
        "promoted_support_cut_edge_count": sum(
            row["promoted_transition_flag"] for row in cut_edges
        ),
        "unpromoted_old_cut_edge_count": len(target_edges),
        "target_transfer_edge_id": target_edge["transfer_edge_id"],
        "target_cut_flux": target_edge["undirected_stationary_flux_x1e12"]
        / SCALE,
        "target_endpoint_state_count": len(target_endpoint_ids),
        "target_neighbor_candidate_count": candidate_stats[
            "target_neighbor_candidate_count"
        ],
        "target_trace_failure_count": candidate_stats["target_trace_failure_count"],
        "target_bad_metric_count": candidate_stats["target_bad_metric_count"],
        "target_not_closed_count": candidate_stats["target_not_closed_count"],
        "target_already_supported_count": candidate_stats[
            "target_already_supported_count"
        ],
        "target_metric_closed_virtual_count": candidate_stats[
            "target_metric_closed_virtual_count"
        ],
        "target_cut_window_block_count": len(cut_blocks),
        "candidate_move_count": len(move_rows),
        "clean_candidate_move_count": sum(row["clean_move_flag"] for row in move_rows),
        "selected_block_code": block_code(selected_block),
        "selected_candidate_word_count": selected_move["candidate_word_count"],
        "selected_same_side_edge_count": selected_move["same_side_edge_count"],
        "selected_negative_side_edge_count": selected_move["negative_side_edge_count"],
        "selected_target_cut_flux_reduction": selected_move[
            "target_cut_flux_reduction_x1e12"
        ]
        / SCALE,
        "selected_target_conductance_reduction": selected_move[
            "target_conductance_reduction_x1e12"
        ]
        / SCALE,
    }
    observable_rows = []
    for observable_id, (key, code) in enumerate(SECOND_WINDOW_OBSERVABLE_CODES.items()):
        value = observable_values[key]
        scaled = int(value) * SCALE if key not in FLOAT_OBSERVABLES else int(value)
        if key in {
            "target_cut_flux",
            "selected_target_cut_flux_reduction",
            "selected_target_conductance_reduction",
        }:
            scaled = int(round(float(value) * SCALE))
        observable_rows.append(
            {
                "observable_id": observable_id,
                "observable_code": code,
                "value_x1e12": scaled,
                "aux_id": -1,
            }
        )

    return {
        "cut_edge_rows": cut_edge_rows,
        "cut_window_rows": cut_window_rows,
        "move_rows": move_rows,
        "candidate_word_rows": candidate_word_rows,
        "observable_rows": observable_rows,
        "observable_values": observable_values,
        "candidate_stats": dict(candidate_stats),
        "target_edge": target_edge,
        "selected_block": selected_block,
        "selected_move": selected_move,
    }


def build_payloads() -> dict[str, Any]:
    promoted_transfer_report = load_json(PROMOTED_TRANSFER_REPORT)
    promoted_transfer_certificate = load_json(PROMOTED_TRANSFER_CERTIFICATE)
    promoted_window_report = load_json(PROMOTED_WINDOW_REPORT)
    promoted_window_certificate = load_json(PROMOTED_WINDOW_CERTIFICATE)
    rows = build_payload_rows()

    cut_edge_table = table_from_rows(CUT_EDGE_COLUMNS, rows["cut_edge_rows"])
    cut_window_table = table_from_rows(CUT_WINDOW_COLUMNS, rows["cut_window_rows"])
    candidate_move_table = table_from_rows(CANDIDATE_MOVE_COLUMNS, rows["move_rows"])
    candidate_word_table = table_from_rows(
        CANDIDATE_WORD_COLUMNS,
        rows["candidate_word_rows"],
    )
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, rows["observable_rows"])
    observable_values = rows["observable_values"]
    selected_move = rows["selected_move"]
    checks = {
        "promoted_transfer_report_certified": promoted_transfer_report.get("status")
        == PROMOTED_TRANSFER_STATUS,
        "promoted_transfer_certificate_certified": promoted_transfer_certificate.get(
            "status"
        )
        == PROMOTED_TRANSFER_STATUS,
        "promoted_window_report_certified": promoted_window_report.get("status")
        == PROMOTED_WINDOW_STATUS,
        "promoted_window_certificate_certified": promoted_window_certificate.get(
            "status"
        )
        == PROMOTED_WINDOW_STATUS,
        "cut_edge_ranking_is_expected": (
            observable_values["surviving_cut_edge_count"],
            observable_values["promoted_support_cut_edge_count"],
            observable_values["unpromoted_old_cut_edge_count"],
            observable_values["target_transfer_edge_id"],
        )
        == (6, 5, 1, 2447),
        "target_candidate_stats_are_expected": (
            observable_values["target_endpoint_state_count"],
            observable_values["target_neighbor_candidate_count"],
            observable_values["target_trace_failure_count"],
            observable_values["target_bad_metric_count"],
            observable_values["target_not_closed_count"],
            observable_values["target_already_supported_count"],
            observable_values["target_metric_closed_virtual_count"],
        )
        == (2, 211, 46, 138, 22, 2, 3),
        "target_window_search_counts_are_expected": (
            observable_values["target_cut_window_block_count"],
            observable_values["candidate_move_count"],
            observable_values["clean_candidate_move_count"],
        )
        == (7, 7, 4),
        "selected_second_window_is_expected": (
            observable_values["selected_block_code"],
            selected_move["candidate_word_count"],
            selected_move["same_side_edge_count"],
            selected_move["negative_side_edge_count"],
            selected_move["target_cut_flux_reduction_x1e12"],
            selected_move["target_conductance_reduction_x1e12"],
        )
        == (1_455, 1, 1, 1, 29_226, 1_070_270),
        "candidate_word_witness_is_expected": tuple(
            rows["candidate_word_rows"][0][column] for column in WORD_COLUMNS[:14]
        )
        == (2, 5, 1, 4, 5, 5, 1, 1, 5, 5, 2, 1, 4, 5),
        "table_shapes_match_codebooks": (
            tuple(cut_edge_table.shape) == (6, len(CUT_EDGE_COLUMNS))
            and tuple(cut_window_table.shape) == (8, len(CUT_WINDOW_COLUMNS))
            and tuple(candidate_move_table.shape)
            == (7, len(CANDIDATE_MOVE_COLUMNS))
            and tuple(candidate_word_table.shape)
            == (1, len(CANDIDATE_WORD_COLUMNS))
            and tuple(observable_table.shape)
            == (len(SECOND_WINDOW_OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS))
        ),
    }

    witness = {
        "target_transfer_edge_id": rows["target_edge"]["transfer_edge_id"],
        "selected_second_window_block": list(rows["selected_block"]),
        "candidate_stats": rows["candidate_stats"],
        "selected_move": {
            key: int(value)
            for key, value in selected_move.items()
            if isinstance(value, (int, np.integer))
        },
        "selected_candidate_word": [
            rows["candidate_word_rows"][0][column] for column in WORD_COLUMNS[:14]
        ],
        "cut_edge_table_sha256": sha_array(cut_edge_table),
        "cut_window_table_sha256": sha_array(cut_window_table),
        "candidate_move_table_sha256": sha_array(candidate_move_table),
        "candidate_word_table_sha256": sha_array(candidate_word_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    search = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_second_window_search@1",
        "object": "d20",
        "parents": {
            "promoted_transfer": PROMOTED_TRANSFER_REPORT.relative_to(ROOT).as_posix(),
            "promoted_window": PROMOTED_WINDOW_REPORT.relative_to(ROOT).as_posix(),
        },
        "search_rule": [
            "rank the six surviving promoted-transfer cut edges by flux",
            "select the unique old cut edge not touching promoted-window support",
            "enumerate one-edit virtual neighbors of its two endpoint states",
            "reject words already native, skip-derived, or promoted-window supported",
            "rank clean cut-local four-symbol blocks that add same-side negative support",
        ],
        "summary": {
            "target_transfer_edge_id": rows["target_edge"]["transfer_edge_id"],
            "selected_second_window_block": list(rows["selected_block"]),
            "selected_candidate_word_count": selected_move["candidate_word_count"],
            "target_cut_flux_reduction_x1e12": selected_move[
                "target_cut_flux_reduction_x1e12"
            ],
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_second_window_search_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_SECOND_WINDOW_SEARCH_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "there is exactly one surviving old cut edge not touching 5,5,2,5 promoted support",
            "the target edge has exactly three metric-closed virtual one-edit candidates after excluding current support",
            "the best clean negative-side second-window rule is block 1,4,5,5",
            "the selected rule adds one negative-side virtual word and predicts a local cut-flux reduction",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_second_window_search@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "Ranking the six surviving promoted-transfer cut edges isolates a "
            "single old cut edge not touching 5,5,2,5 support: transfer edge "
            "2447 between states 797 and 828. Its endpoint one-edit "
            "neighborhood has 211 virtual words; after metric, closure, and "
            "current-support filters, three remain. The best clean negative "
            "second-window rule is block 1,4,5,5. It contributes one "
            "negative-side virtual word, predicts target-edge cut flux "
            "170969397/1e12 -> 170940171/1e12, and lowers the one-edge "
            "negative-side conductance from 732064422/1e12 to "
            "730994152/1e12."
        ),
        "stage_protocol": {
            "draft": "rank surviving promoted-transfer cut edges and isolate the unpromoted old-cut edge",
            "witness": "emit cut-edge, target-window, candidate-move, candidate-word, and observable tables",
            "coherence": "check metric/closure/current-support filters and clean negative-side move ranking",
            "closure": "certify the selected second-window block and local flux/conductance prediction",
            "emit": "emit search artifacts, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "promoted_transfer_report": input_entry(
                PROMOTED_TRANSFER_REPORT,
                {
                    "status": promoted_transfer_report.get("status"),
                    "certificate_sha256": promoted_transfer_report.get(
                        "certificate_sha256"
                    ),
                },
            ),
            "promoted_transfer_certificate": input_entry(
                PROMOTED_TRANSFER_CERTIFICATE
            ),
            "promoted_transfer_tables": input_entry(PROMOTED_TRANSFER_TABLES),
            "promoted_window_report": input_entry(
                PROMOTED_WINDOW_REPORT,
                {
                    "status": promoted_window_report.get("status"),
                    "certificate_sha256": promoted_window_report.get(
                        "certificate_sha256"
                    ),
                },
            ),
            "promoted_window_certificate": input_entry(PROMOTED_WINDOW_CERTIFICATE),
            "promoted_window_tables": input_entry(PROMOTED_WINDOW_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "second_window_search": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_second_window_search.json"
            ),
            "cut_edges_csv": relpath(
                OUT_DIR / "aperture_closure_tail_second_window_cut_edges.csv"
            ),
            "target_cut_windows_csv": relpath(
                OUT_DIR / "aperture_closure_tail_second_window_target_windows.csv"
            ),
            "candidate_moves_csv": relpath(
                OUT_DIR / "aperture_closure_tail_second_window_candidate_moves.csv"
            ),
            "candidate_words_csv": relpath(
                OUT_DIR / "aperture_closure_tail_second_window_candidate_words.csv"
            ),
            "observables_csv": relpath(
                OUT_DIR / "aperture_closure_tail_second_window_observables.csv"
            ),
            "tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_second_window_search_tables.npz"
            ),
            "certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_second_window_search_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the ranked six-edge promoted-transfer cut witness",
                "the unique unpromoted old-cut target edge",
                "the target endpoint virtual-neighbor metric/closure/support filter",
                "the selected clean second-window candidate block and predicted local effect",
            ],
            "does_not_certify_because_not_required": [
                "global promotion of the second-window rule",
                "fresh spectral recomputation after adding block 1,4,5,5",
                "multi-window interactions with blocks other than the selected target-local block",
                "compiler integration of the second-window rule",
            ],
        },
        "next_highest_yield_item": (
            "Promote the selected 1,4,5,5 second-window rule globally, rebuild "
            "the promoted automaton, and test whether the old six-edge cut "
            "finally changes support or remains stable."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_second_window_search_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified promoted-transfer and promoted-window artifacts",
            "rank surviving cut edges and isolate the unpromoted old-cut edge",
            "enumerate and filter one-edit virtual target-neighborhood words",
            "rank clean second-window block moves and certify the selected witness",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "second_window_search": search,
        "cut_edges_csv": csv_text(CUT_EDGE_COLUMNS, rows["cut_edge_rows"]),
        "target_cut_windows_csv": csv_text(CUT_WINDOW_COLUMNS, rows["cut_window_rows"]),
        "candidate_moves_csv": csv_text(CANDIDATE_MOVE_COLUMNS, rows["move_rows"]),
        "candidate_words_csv": csv_text(
            CANDIDATE_WORD_COLUMNS,
            rows["candidate_word_rows"],
        ),
        "observables_csv": csv_text(OBSERVABLE_COLUMNS, rows["observable_rows"]),
        "cut_edge_table": cut_edge_table,
        "cut_window_table": cut_window_table,
        "candidate_move_table": candidate_move_table,
        "candidate_word_table": candidate_word_table,
        "observable_table": observable_table,
        "certificate": certificate,
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
        / "signature_boundary_spine_aperture_closure_tail_second_window_search.json",
        payloads["second_window_search"],
    )
    (OUT_DIR / "aperture_closure_tail_second_window_cut_edges.csv").write_text(
        payloads["cut_edges_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_second_window_target_windows.csv").write_text(
        payloads["target_cut_windows_csv"],
        encoding="utf-8",
    )
    (
        OUT_DIR / "aperture_closure_tail_second_window_candidate_moves.csv"
    ).write_text(
        payloads["candidate_moves_csv"],
        encoding="utf-8",
    )
    (
        OUT_DIR / "aperture_closure_tail_second_window_candidate_words.csv"
    ).write_text(
        payloads["candidate_words_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_second_window_observables.csv").write_text(
        payloads["observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_second_window_search_tables.npz",
        cut_edge_table=payloads["cut_edge_table"],
        cut_window_table=payloads["cut_window_table"],
        candidate_move_table=payloads["candidate_move_table"],
        candidate_word_table=payloads["candidate_word_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_second_window_search_certificate.json",
        payloads["certificate"],
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
