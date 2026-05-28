from __future__ import annotations

import csv
import json
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np

try:
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_promoted_window as parent
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_flow_window_lift import (
        touch_blocks,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_promotion import (
        FIRST_WINDOW_BLOCK,
        OUT_DIR as SECOND_WINDOW_PROMOTION_DIR,
        SECOND_WINDOW_BLOCK,
        STATUS as SECOND_WINDOW_PROMOTION_STATUS,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame import (
        OUT_DIR as SIXJ_FRAME_DIR,
        STATUS as SIXJ_FRAME_STATUS,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_promoted_window as parent
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_flow_window_lift import (
        touch_blocks,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_promotion import (
        FIRST_WINDOW_BLOCK,
        OUT_DIR as SECOND_WINDOW_PROMOTION_DIR,
        SECOND_WINDOW_BLOCK,
        STATUS as SECOND_WINDOW_PROMOTION_STATUS,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame import (
        OUT_DIR as SIXJ_FRAME_DIR,
        STATUS as SIXJ_FRAME_STATUS,
    )
    from derive_c985_typed_simple_object_registry import INDEX_PATH
    from paths import D20_INVARIANTS, ROOT


THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_SIXJ_RECOUPLING_PAIR_OBSTRUCTION_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

SECOND_WINDOW_PROMOTION_REPORT = SECOND_WINDOW_PROMOTION_DIR / "report.json"
SECOND_WINDOW_PROMOTION_CERTIFICATE = (
    SECOND_WINDOW_PROMOTION_DIR
    / "signature_boundary_spine_aperture_closure_tail_second_window_promotion_certificate.json"
)
SECOND_WINDOW_PROMOTION_TABLES = (
    SECOND_WINDOW_PROMOTION_DIR
    / "signature_boundary_spine_aperture_closure_tail_second_window_promotion_tables.npz"
)
SECOND_WINDOW_PROMOTION_STATES = (
    SECOND_WINDOW_PROMOTION_DIR
    / "aperture_closure_tail_second_window_promotion_states.csv"
)
SECOND_WINDOW_PROMOTION_EDGES = (
    SECOND_WINDOW_PROMOTION_DIR
    / "aperture_closure_tail_second_window_promotion_edges.csv"
)
SIXJ_FRAME_REPORT = SIXJ_FRAME_DIR / "report.json"
SIXJ_FRAME_CERTIFICATE = (
    SIXJ_FRAME_DIR
    / "signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame_certificate.json"
)
SIXJ_FRAME_CUT_EDGES = SIXJ_FRAME_DIR / "sixj_bottleneck_cut_edges.csv"

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction.py"
)

BASE_BLOCKS = (FIRST_WINDOW_BLOCK, SECOND_WINDOW_BLOCK)
MIN_TOUCH_COUNT = 2

BLOCK_COLUMNS = [
    "block_id",
    "block_code",
    "touch_count",
    "cut_edge_touch_count",
    "opposite_pair_touch_count",
    "already_promoted_flag",
    "candidate_flag",
]
INTERVENTION_COLUMNS = [
    "intervention_id",
    "intervention_size",
    "block_code_a",
    "block_code_b",
    "candidate_touch_count",
    "cut_edge_touch_count",
    "opposite_pair_touch_count",
    "state_count",
    "new_state_count",
    "edge_count",
    "new_edge_count",
    "cut_edge_count",
    "old_cut_edge_still_cut_count",
    "old_cut_edge_same_side_count",
    "promoted_cut_edge_count",
    "promoted_only_cut_edge_count",
    "lambda_2_x1e12",
    "cut_conductance_x1e12",
    "conductance_reduction_x1e12",
    "support_changed_flag",
    "selected_best_flag",
]
OBSERVABLE_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBSERVABLE_CODES = {
    "base_state_count": 0,
    "base_edge_count": 1,
    "base_cut_edge_count": 2,
    "base_cut_conductance_x1e12": 3,
    "touch_block_count": 4,
    "candidate_block_count": 5,
    "single_intervention_count": 6,
    "pair_intervention_count": 7,
    "total_intervention_count": 8,
    "support_changing_intervention_count": 9,
    "best_block_code_a": 10,
    "best_block_code_b": 11,
    "best_state_count": 12,
    "best_edge_count": 13,
    "best_cut_edge_count": 14,
    "best_old_cut_edge_still_cut_count": 15,
    "best_lambda_2_x1e12": 16,
    "best_cut_conductance_x1e12": 17,
    "best_conductance_reduction_x1e12": 18,
    "closed_metric_word_count": 19,
}


def csv_text(headers: list[str], rows: list[dict[str, Any]]) -> str:
    lines = [",".join(headers)]
    for row in rows:
        lines.append(",".join(str(row.get(header, "")) for header in headers))
    return "\n".join(lines) + "\n"


def block_text(block: tuple[int, int, int, int]) -> str:
    return ".".join(str(symbol) for symbol in block)


def block_code(block: tuple[int, int, int, int]) -> int:
    return parent.block_code(block)


def table_from_rows(columns: list[str], rows: list[dict[str, int]]) -> np.ndarray:
    return np.asarray(
        [[int(row[column]) for column in columns] for row in rows],
        dtype=np.int64,
    )


def table_rows(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} is not a JSON object")
    return payload


def load_second_window_geometry() -> dict[str, Any]:
    state_rows: list[dict[str, int]] = []
    with SECOND_WINDOW_PROMOTION_STATES.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as fh:
        for row in csv.DictReader(fh):
            state_rows.append({key: int(value) for key, value in row.items()})

    word_by_state = {
        row["automaton_state_id"]: parent.word_from_row(row) for row in state_rows
    }
    old_edges: set[tuple[tuple[int, ...], tuple[int, ...]]] = set()
    old_cut_edges: set[tuple[tuple[int, ...], tuple[int, ...]]] = set()
    cut_blocks_by_edge: dict[int, Counter[tuple[int, int, int, int]]] = {}
    touch_counts: Counter[tuple[int, int, int, int]] = Counter()
    edge_touch_counts: Counter[tuple[int, int, int, int]] = Counter()

    with SECOND_WINDOW_PROMOTION_EDGES.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as fh:
        for raw in csv.DictReader(fh):
            row = {key: int(value) for key, value in raw.items()}
            source_word = word_by_state[row["source_state_id"]]
            target_word = word_by_state[row["target_state_id"]]
            key = parent.edge_word_key(source_word, target_word)
            old_edges.add(key)
            if row["new_spectral_cut_edge_flag"] != 1:
                continue
            old_cut_edges.add(key)
            per_edge: Counter[tuple[int, int, int, int]] = Counter()
            for state_id in (row["source_state_id"], row["target_state_id"]):
                for _rank, block in touch_blocks(
                    word_by_state[state_id],
                    row["edit_position"],
                ):
                    per_edge[block] += 1
                    touch_counts[block] += 1
            cut_blocks_by_edge[row["automaton_edge_id"]] = per_edge
            for block in per_edge:
                edge_touch_counts[block] += 1

    return {
        "state_count": len(state_rows),
        "edge_count": len(old_edges),
        "old_edges": old_edges,
        "old_cut_edges": old_cut_edges,
        "cut_blocks_by_edge": cut_blocks_by_edge,
        "touch_counts": touch_counts,
        "edge_touch_counts": edge_touch_counts,
    }


def precompute_closed_metric_records() -> dict[tuple[int, ...], dict[str, Any]]:
    _repair_rows, _grammar_stats, repair_rows_by_block = parent.grammar_rows()
    left_radius = parent.radius_from(
        parent.LEFT_REPAIR_BOUNDARY_WORD,
        parent.MAX_SIDE_EDIT_RADIUS,
    )
    right_radius = parent.radius_from(
        parent.RIGHT_REPAIR_BOUNDARY_WORD,
        parent.MAX_SIDE_EDIT_RADIUS,
    )
    candidate_words = sorted(set(left_radius) | set(right_radius))
    carrier_adjacency, assoc_by_word, rewrite_edge_by_pair = parent.build_context()

    records: dict[tuple[int, ...], dict[str, Any]] = {}
    for word in candidate_words:
        try:
            _raw_windows, trace_nodes, _trace_signatures, metrics = parent.build_trace(
                word,
                assoc_by_word,
                rewrite_edge_by_pair,
            )
        except Exception:
            continue
        trace = tuple(int(value) for value in trace_nodes)
        delta_twice = int(metrics["metric_gromov_delta_twice"])
        variation = int(metrics["trace_signature_total_variation"])
        if (
            delta_twice != parent.TARGET_DELTA_TWICE
            or variation > parent.TARGET_VARIATION_INCLUSIVE_BOUND
        ):
            continue
        profile = parent.closure_profile(word, carrier_adjacency)
        if profile["first_return_closed_path_count"] <= 0:
            continue
        native_repair = int(
            parent.contains_undirected_edge(trace, 31, 28)
            or parent.contains_undirected_edge(trace, 50, 34)
        )
        skip_spans = parent.derived_spans(word, repair_rows_by_block)
        first_skip_rank, first_skip_block, _first_rows = (
            skip_spans[0] if skip_spans else (-1, (-1, -1, -1, -1), [])
        )
        sequence = tuple(parent.PREFIX_SYMBOLS) + word + word[:2]
        all_blocks = [
            (rank, tuple(int(value) for value in sequence[rank : rank + 4]))
            for rank in range(len(sequence) - 3)
        ]
        records[word] = {
            "word": word,
            "left_edit_radius": left_radius.get(word, 99),
            "right_edit_radius": right_radius.get(word, 99),
            "trace": trace,
            "delta_twice": delta_twice,
            "variation": variation,
            "native_repair": native_repair,
            "skip_derived_repair": int(bool(skip_spans)),
            "first_skip_span_rank": first_skip_rank,
            "first_skip_block": first_skip_block,
            "all_blocks": all_blocks,
            "profile": profile,
        }
    return records


def rows_for_blocks(
    records: dict[tuple[int, ...], dict[str, Any]],
    promoted_blocks: set[tuple[int, int, int, int]],
) -> dict[tuple[int, ...], dict[str, Any]]:
    rows: dict[tuple[int, ...], dict[str, Any]] = {}
    for word, record in records.items():
        promoted_spans = [
            (rank, block)
            for rank, block in record["all_blocks"]
            if block in promoted_blocks
        ]
        promoted_repair = int(bool(promoted_spans))
        skip_repair = record["skip_derived_repair"]
        native_repair = record["native_repair"]
        derived_repair = int(skip_repair or promoted_repair)
        if not (native_repair or derived_repair):
            continue
        first_promoted_rank, first_promoted_block = (
            promoted_spans[0] if promoted_spans else (-1, (-1, -1, -1, -1))
        )
        row = {
            key: record[key]
            for key in [
                "word",
                "left_edit_radius",
                "right_edit_radius",
                "trace",
                "delta_twice",
                "variation",
                "native_repair",
                "skip_derived_repair",
                "first_skip_span_rank",
                "first_skip_block",
                "profile",
            ]
        }
        row.update(
            promoted_window_repair=promoted_repair,
            derived_repair=derived_repair,
            derived_only=int(derived_repair and not native_repair),
            skip_derived_only=int(skip_repair and not native_repair),
            promoted_only=int(
                promoted_repair and not (native_repair or skip_repair)
            ),
            first_promoted_span_rank=first_promoted_rank,
            first_promoted_block=first_promoted_block,
        )
        rows[word] = row
    return rows


def opposite_pair_touch_count(
    blocks: tuple[tuple[int, int, int, int], ...],
    cut_blocks_by_edge: dict[int, Counter[tuple[int, int, int, int]]],
) -> int:
    edge_ids = sorted(cut_blocks_by_edge)
    opposite_edge_ids = [
        (edge_ids[0], edge_ids[5]),
        (edge_ids[1], edge_ids[4]),
        (edge_ids[2], edge_ids[3]),
    ]
    return sum(
        int(
            any(block in cut_blocks_by_edge[left] for block in blocks)
            and any(block in cut_blocks_by_edge[right] for block in blocks)
        )
        for left, right in opposite_edge_ids
    )


def evaluate_intervention(
    intervention_id: int,
    blocks: tuple[tuple[int, int, int, int], ...],
    records: dict[tuple[int, ...], dict[str, Any]],
    geometry: dict[str, Any],
    base_conductance: int,
) -> dict[str, int]:
    promoted_blocks = set(BASE_BLOCKS) | set(blocks)
    rows_by_word = rows_for_blocks(records, promoted_blocks)
    graph = parent.build_graph(rows_by_word)
    automaton = parent.build_automaton_rows(graph, geometry)
    spectral = automaton["spectral_rows"][0]
    block_a = blocks[0]
    block_b = blocks[1] if len(blocks) == 2 else (-1, -1, -1, -1)
    cut_blocks_by_edge = geometry["cut_blocks_by_edge"]
    touched_edges = {
        edge_id
        for edge_id, per_edge in cut_blocks_by_edge.items()
        if any(block in per_edge for block in blocks)
    }
    touch_count = sum(geometry["touch_counts"][block] for block in blocks)
    return {
        "intervention_id": intervention_id,
        "intervention_size": len(blocks),
        "block_code_a": block_code(block_a),
        "block_code_b": -1 if block_b == (-1, -1, -1, -1) else block_code(block_b),
        "candidate_touch_count": touch_count,
        "cut_edge_touch_count": len(touched_edges),
        "opposite_pair_touch_count": opposite_pair_touch_count(
            blocks,
            cut_blocks_by_edge,
        ),
        "state_count": len(automaton["state_rows"]),
        "new_state_count": len(automaton["state_rows"]) - geometry["state_count"],
        "edge_count": len(automaton["edge_rows"]),
        "new_edge_count": len(automaton["edge_rows"]) - geometry["edge_count"],
        "cut_edge_count": spectral["cut_edge_count"],
        "old_cut_edge_still_cut_count": spectral["old_cut_edge_still_cut_count"],
        "old_cut_edge_same_side_count": spectral["old_cut_edge_same_side_count"],
        "promoted_cut_edge_count": spectral["promoted_cut_edge_count"],
        "promoted_only_cut_edge_count": spectral["promoted_only_cut_edge_count"],
        "lambda_2_x1e12": spectral["lambda_2_x1e12"],
        "cut_conductance_x1e12": spectral["cut_conductance_x1e12"],
        "conductance_reduction_x1e12": base_conductance
        - spectral["cut_conductance_x1e12"],
        "support_changed_flag": int(
            spectral["old_cut_edge_still_cut_count"] < 6
            or spectral["old_cut_edge_same_side_count"] > 0
        ),
        "selected_best_flag": 0,
    }


def build_payload_rows() -> dict[str, Any]:
    geometry = load_second_window_geometry()
    records = precompute_closed_metric_records()
    touch_counts: Counter[tuple[int, int, int, int]] = geometry["touch_counts"]
    edge_touch_counts: Counter[tuple[int, int, int, int]] = geometry[
        "edge_touch_counts"
    ]
    base_promoted = set(BASE_BLOCKS)
    candidate_blocks = [
        block
        for block, count in sorted(
            touch_counts.items(),
            key=lambda item: (-item[1], block_code(item[0])),
        )
        if count >= MIN_TOUCH_COUNT and block not in base_promoted
    ]

    block_rows = []
    for block_id, block in enumerate(
        sorted(touch_counts, key=lambda item: (-touch_counts[item], block_code(item)))
    ):
        is_candidate = int(block in candidate_blocks)
        block_rows.append(
            {
                "block_id": block_id,
                "block": block_text(block),
                "block_code": block_code(block),
                "touch_count": touch_counts[block],
                "cut_edge_touch_count": edge_touch_counts[block],
                "opposite_pair_touch_count": opposite_pair_touch_count(
                    (block,),
                    geometry["cut_blocks_by_edge"],
                ),
                "already_promoted_flag": int(block in base_promoted),
                "candidate_flag": is_candidate,
            }
        )

    base_spectral = parent.table_rows(
        np.asarray(
            np.load(SECOND_WINDOW_PROMOTION_TABLES, allow_pickle=False)[
                "spectral_cut_table"
            ],
            dtype=np.int64,
        ),
        parent.SPECTRAL_CUT_COLUMNS,
    )[0]
    base_conductance = base_spectral["cut_conductance_x1e12"]

    interventions: list[tuple[tuple[int, int, int, int], ...]] = [
        (block,) for block in candidate_blocks
    ]
    interventions.extend(tuple(pair) for pair in combinations(candidate_blocks, 2))

    intervention_rows = [
        evaluate_intervention(
            intervention_id,
            blocks,
            records,
            geometry,
            base_conductance,
        )
        for intervention_id, blocks in enumerate(interventions)
    ]
    best = min(
        intervention_rows,
        key=lambda row: (
            row["support_changed_flag"] == 0,
            row["cut_conductance_x1e12"],
            -row["lambda_2_x1e12"],
            row["intervention_size"],
            row["block_code_a"],
            row["block_code_b"],
        ),
    )
    best["selected_best_flag"] = 1

    observable_values = {
        "base_state_count": geometry["state_count"],
        "base_edge_count": geometry["edge_count"],
        "base_cut_edge_count": base_spectral["cut_edge_count"],
        "base_cut_conductance_x1e12": base_conductance,
        "touch_block_count": len(touch_counts),
        "candidate_block_count": len(candidate_blocks),
        "single_intervention_count": len(candidate_blocks),
        "pair_intervention_count": len(candidate_blocks) * (len(candidate_blocks) - 1)
        // 2,
        "total_intervention_count": len(intervention_rows),
        "support_changing_intervention_count": sum(
            row["support_changed_flag"] for row in intervention_rows
        ),
        "best_block_code_a": best["block_code_a"],
        "best_block_code_b": best["block_code_b"],
        "best_state_count": best["state_count"],
        "best_edge_count": best["edge_count"],
        "best_cut_edge_count": best["cut_edge_count"],
        "best_old_cut_edge_still_cut_count": best[
            "old_cut_edge_still_cut_count"
        ],
        "best_lambda_2_x1e12": best["lambda_2_x1e12"],
        "best_cut_conductance_x1e12": best["cut_conductance_x1e12"],
        "best_conductance_reduction_x1e12": best[
            "conductance_reduction_x1e12"
        ],
        "closed_metric_word_count": len(records),
    }
    observable_rows = [
        {
            "observable_id": observable_id,
            "observable_code": code,
            "value": int(observable_values[key]),
            "scale_code": 0,
        }
        for observable_id, (key, code) in enumerate(OBSERVABLE_CODES.items())
    ]

    return {
        "geometry": geometry,
        "record_count": len(records),
        "candidate_blocks": candidate_blocks,
        "block_rows": block_rows,
        "intervention_rows": intervention_rows,
        "observable_rows": observable_rows,
        "observable_values": observable_values,
    }


def build_payloads() -> dict[str, Any]:
    promotion_report = load_json(SECOND_WINDOW_PROMOTION_REPORT)
    promotion_certificate = load_json(SECOND_WINDOW_PROMOTION_CERTIFICATE)
    sixj_report = load_json(SIXJ_FRAME_REPORT)
    sixj_certificate = load_json(SIXJ_FRAME_CERTIFICATE)
    rows = build_payload_rows()

    block_table = table_from_rows(BLOCK_COLUMNS, rows["block_rows"])
    intervention_table = table_from_rows(
        INTERVENTION_COLUMNS,
        rows["intervention_rows"],
    )
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, rows["observable_rows"])
    observable_values = rows["observable_values"]
    best = next(row for row in rows["intervention_rows"] if row["selected_best_flag"])

    checks = {
        "sixj_frame_report_certified": sixj_report.get("status") == SIXJ_FRAME_STATUS,
        "sixj_frame_certificate_certified": sixj_certificate.get("status")
        == SIXJ_FRAME_STATUS,
        "second_window_promotion_report_certified": promotion_report.get("status")
        == SECOND_WINDOW_PROMOTION_STATUS,
        "second_window_promotion_certificate_certified": promotion_certificate.get(
            "status"
        )
        == SECOND_WINDOW_PROMOTION_STATUS,
        "base_cut_is_six_edges": (
            observable_values["base_state_count"],
            observable_values["base_edge_count"],
            observable_values["base_cut_edge_count"],
            observable_values["base_cut_conductance_x1e12"],
        )
        == (860, 2_571, 6, 4_329_004_000),
        "candidate_scope_is_k4_local_touch_count_at_least_two": (
            observable_values["touch_block_count"],
            observable_values["candidate_block_count"],
            observable_values["single_intervention_count"],
            observable_values["pair_intervention_count"],
            observable_values["total_intervention_count"],
        )
        == (15, 9, 9, 36, 45),
        "closed_metric_record_count_is_expected": observable_values[
            "closed_metric_word_count"
        ]
        == 984,
        "no_single_or_pair_candidate_changes_old_cut_support": observable_values[
            "support_changing_intervention_count"
        ]
        == 0,
        "best_pair_is_tail_mirror_pair": (
            observable_values["best_block_code_a"],
            observable_values["best_block_code_b"],
        )
        == (5_255, 5_252),
        "best_pair_improves_conductance_but_keeps_six_old_edges": (
            observable_values["best_state_count"],
            observable_values["best_edge_count"],
            observable_values["best_cut_edge_count"],
            observable_values["best_old_cut_edge_still_cut_count"],
            observable_values["best_cut_conductance_x1e12"],
            observable_values["best_conductance_reduction_x1e12"],
        )
        == (894, 2_695, 6, 6, 3_708_282_000, 620_722_000),
        "all_intervention_rows_keep_old_cut_edges": all(
            row["old_cut_edge_still_cut_count"] == 6
            and row["old_cut_edge_same_side_count"] == 0
            for row in rows["intervention_rows"]
        ),
        "table_shapes_match_codebooks": (
            tuple(block_table.shape),
            tuple(intervention_table.shape),
            tuple(observable_table.shape),
        )
        == (
            (15, len(BLOCK_COLUMNS)),
            (45, len(INTERVENTION_COLUMNS)),
            (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
        ),
    }

    witness = {
        "base_blocks": [block_text(block) for block in BASE_BLOCKS],
        "candidate_block_codes": [
            block_code(block) for block in rows["candidate_blocks"]
        ],
        "intervention_count": observable_values["total_intervention_count"],
        "support_changing_intervention_count": observable_values[
            "support_changing_intervention_count"
        ],
        "best_intervention": best,
        "block_table_sha256": parent.sha_array(block_table),
        "intervention_table_sha256": parent.sha_array(intervention_table),
        "observable_table_sha256": parent.sha_array(observable_table),
    }

    obstruction = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction@1",
        "object": "C985->d20",
        "parents": {
            "sixj_frame": SIXJ_FRAME_REPORT.relative_to(ROOT).as_posix(),
            "second_window_promotion": SECOND_WINDOW_PROMOTION_REPORT.relative_to(
                ROOT
            ).as_posix(),
        },
        "search_scope": {
            "base_blocks": [block_text(block) for block in BASE_BLOCKS],
            "candidate_rule": (
                "non-promoted four-symbol blocks touching the current six cut "
                f"edges at least {MIN_TOUCH_COUNT} times"
            ),
            "candidate_block_codes": [
                block_code(block) for block in rows["candidate_blocks"]
            ],
            "interventions": "all singleton candidates and all unordered candidate pairs",
        },
        "summary": {
            "intervention_count": observable_values["total_intervention_count"],
            "support_changing_intervention_count": observable_values[
                "support_changing_intervention_count"
            ],
            "best_block_codes": [
                observable_values["best_block_code_a"],
                observable_values["best_block_code_b"],
            ],
            "best_cut_conductance_x1e12": observable_values[
                "best_cut_conductance_x1e12"
            ],
            "best_old_cut_edge_still_cut_count": observable_values[
                "best_old_cut_edge_still_cut_count"
            ],
        },
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_SIXJ_RECOUPLING_PAIR_OBSTRUCTION_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "Within the certified 6j bottleneck frame, every K4-local singleton "
            "or unordered pair recoupling made from the nine non-promoted "
            "touch blocks with support at least two keeps all six old cut edges "
            "on the fresh spectral cut. The best pair, 5,2,5,5 with 5,2,5,2, "
            "lowers conductance from 4329004000/1e12 to 3708282000/1e12, but "
            "it still leaves the old six-edge aperture intact."
        ),
        "stage_protocol": {
            "draft": "use the certified 6j frame and second-window promoted automaton",
            "witness": "enumerate K4-local touch blocks and singleton/pair recoupling interventions",
            "coherence": "rebuild the promoted grammar for each intervention and compare fresh spectral cuts to the old six cut edges",
            "closure": "certify the rank-two recoupling obstruction and selected conductance-improving non-solution",
            "emit": "emit block, intervention, observable, certificate, report, verifier command, and next higher-order target",
        },
        "inputs": {
            "sixj_frame_report": parent.input_entry(
                SIXJ_FRAME_REPORT,
                {
                    "status": sixj_report.get("status"),
                    "certificate_sha256": sixj_report.get("certificate_sha256"),
                },
            ),
            "sixj_frame_certificate": parent.input_entry(SIXJ_FRAME_CERTIFICATE),
            "sixj_frame_cut_edges": parent.input_entry(SIXJ_FRAME_CUT_EDGES),
            "second_window_promotion_report": parent.input_entry(
                SECOND_WINDOW_PROMOTION_REPORT,
                {
                    "status": promotion_report.get("status"),
                    "certificate_sha256": promotion_report.get(
                        "certificate_sha256"
                    ),
                },
            ),
            "second_window_promotion_certificate": parent.input_entry(
                SECOND_WINDOW_PROMOTION_CERTIFICATE
            ),
            "second_window_promotion_tables": parent.input_entry(
                SECOND_WINDOW_PROMOTION_TABLES
            ),
            "second_window_promotion_states": parent.input_entry(
                SECOND_WINDOW_PROMOTION_STATES
            ),
            "second_window_promotion_edges": parent.input_entry(
                SECOND_WINDOW_PROMOTION_EDGES
            ),
            "derive_script": parent.input_entry(DERIVE_SCRIPT),
            "validator": parent.input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": parent.relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "recoupling_pair_obstruction": parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction.json"
            ),
            "recoupling_touch_blocks_csv": parent.relpath(
                OUT_DIR / "sixj_recoupling_touch_blocks.csv"
            ),
            "recoupling_interventions_csv": parent.relpath(
                OUT_DIR / "sixj_recoupling_pair_interventions.csv"
            ),
            "recoupling_observables_csv": parent.relpath(
                OUT_DIR / "sixj_recoupling_pair_observables.csv"
            ),
            "recoupling_tables": parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction_tables.npz"
            ),
            "recoupling_certificate": parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction_certificate.json"
            ),
            "manifest": parent.relpath(OUT_DIR / "manifest.json"),
            "report": parent.relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "exhaustive singleton and unordered-pair search over the declared K4-local touch-block scope",
                "fresh spectral-cut comparison for each tested recoupling intervention",
                "absence of old-six-edge support change at recoupling rank one or two within that scope",
                "the best conductance-improving pair still leaves the six old cut edges intact",
            ],
            "does_not_certify_because_not_required": [
                "triple-block or face-level 6j recoupling interventions",
                "arbitrary blocks that do not touch the current six-edge aperture",
                "a full C985 numerical F-symbol table",
                "compiler integration of the tested recoupling rules",
            ],
        },
        "next_highest_yield_item": (
            "Escalate from edge-pair recoupling to tetrahedral face/triple "
            "recoupling: test three-block interventions indexed by the four "
            "K4 faces, because rank-one and rank-two K4-local moves preserve "
            "the old six-edge aperture."
        ),
    }
    report["certificate_sha256"] = parent.self_hash(report, "certificate_sha256")

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction_certificate@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the six-edge aperture is stable under tested K4-local singleton recouplings",
            "the six-edge aperture is stable under tested K4-local pair recouplings",
            "the best pair is a conductance improvement but not a support-changing recoupling",
            "the next test must be face/triple-level recoupling",
        ],
    }

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified 6j frame and second-window promotion artifacts",
            "enumerate K4-local cut-touch blocks and candidate singleton/pair interventions",
            "rebuild grammar, graph, automaton, and fresh spectral cut for every intervention",
            "check old cut support, conductance ranking, table shapes, hashes, and registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = parent.self_hash(manifest, "manifest_sha256")

    return {
        "recoupling_pair_obstruction": obstruction,
        "recoupling_touch_blocks_csv": csv_text(
            [
                "block_id",
                "block",
                "block_code",
                "touch_count",
                "cut_edge_touch_count",
                "opposite_pair_touch_count",
                "already_promoted_flag",
                "candidate_flag",
            ],
            rows["block_rows"],
        ),
        "recoupling_interventions_csv": csv_text(
            INTERVENTION_COLUMNS,
            rows["intervention_rows"],
        ),
        "recoupling_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            rows["observable_rows"],
        ),
        "block_table": block_table,
        "intervention_table": intervention_table,
        "observable_table": observable_table,
        "recoupling_certificate": certificate,
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
            "manifest": parent.relpath(OUT_DIR / "manifest.json"),
            "report": parent.relpath(OUT_DIR / "report.json"),
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
    updated["registry_sha256"] = parent.self_hash(updated, "registry_sha256")
    parent.write_json(INDEX_PATH, updated)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    parent.write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction.json",
        payloads["recoupling_pair_obstruction"],
    )
    (OUT_DIR / "sixj_recoupling_touch_blocks.csv").write_text(
        payloads["recoupling_touch_blocks_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "sixj_recoupling_pair_interventions.csv").write_text(
        payloads["recoupling_interventions_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "sixj_recoupling_pair_observables.csv").write_text(
        payloads["recoupling_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction_tables.npz",
        block_table=payloads["block_table"],
        intervention_table=payloads["intervention_table"],
        observable_table=payloads["observable_table"],
    )
    parent.write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction_certificate.json",
        payloads["recoupling_certificate"],
    )
    parent.write_json(OUT_DIR / "report.json", payloads["report"])
    parent.write_json(OUT_DIR / "manifest.json", payloads["manifest"])
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
                "report": parent.relpath(OUT_DIR / "report.json"),
                "manifest": parent.relpath(OUT_DIR / "manifest.json"),
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
