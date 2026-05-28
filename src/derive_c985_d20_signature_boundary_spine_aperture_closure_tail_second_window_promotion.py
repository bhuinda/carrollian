from __future__ import annotations

import json
from collections import Counter
from typing import Any

import numpy as np

try:
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_promoted_window as parent
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_search import (
        OUT_DIR as SECOND_WINDOW_DIR,
        STATUS as SECOND_WINDOW_STATUS,
    )
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_promoted_window as parent
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_search import (
        OUT_DIR as SECOND_WINDOW_DIR,
        STATUS as SECOND_WINDOW_STATUS,
    )
    from paths import D20_INVARIANTS, ROOT


THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_promotion"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_SECOND_WINDOW_PROMOTION_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

FIRST_WINDOW_BLOCK = parent.PROMOTED_BLOCK
SECOND_WINDOW_BLOCK = (1, 4, 5, 5)
PROMOTION_BLOCKS = (FIRST_WINDOW_BLOCK, SECOND_WINDOW_BLOCK)
SCALE = parent.SCALE

PROMOTED_WINDOW_REPORT = parent.OUT_DIR / "report.json"
PROMOTED_WINDOW_CERTIFICATE = (
    parent.OUT_DIR
    / "signature_boundary_spine_aperture_closure_tail_promoted_window_certificate.json"
)
PROMOTED_WINDOW_TABLES = (
    parent.OUT_DIR
    / "signature_boundary_spine_aperture_closure_tail_promoted_window_tables.npz"
)
SECOND_WINDOW_REPORT = SECOND_WINDOW_DIR / "report.json"
SECOND_WINDOW_CERTIFICATE = (
    SECOND_WINDOW_DIR
    / "signature_boundary_spine_aperture_closure_tail_second_window_search_certificate.json"
)
SECOND_WINDOW_TABLES = (
    SECOND_WINDOW_DIR
    / "signature_boundary_spine_aperture_closure_tail_second_window_search_tables.npz"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_promotion.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_promotion.py"
)

CELL_COLUMNS = parent.CELL_COLUMNS
COMPONENT_COLUMNS = parent.COMPONENT_COLUMNS
PATH_COLUMNS = parent.PATH_COLUMNS
STATE_COLUMNS = parent.STATE_COLUMNS
EDGE_COLUMNS = parent.EDGE_COLUMNS
RECURRENT_CLASS_COLUMNS = parent.RECURRENT_CLASS_COLUMNS
NATIVE_CLASS_COLUMNS = parent.NATIVE_CLASS_COLUMNS
SPECTRAL_CUT_COLUMNS = parent.SPECTRAL_CUT_COLUMNS
POINCARE_COLUMNS = parent.POINCARE_COLUMNS
OBSERVABLE_COLUMNS = parent.OBSERVABLE_COLUMNS
WORD_COLUMNS = parent.WORD_COLUMNS

SECOND_WINDOW_PROMOTION_OBSERVABLE_CODES = {
    "boundary_union_word_count": 0,
    "trace_failure_word_count": 1,
    "bad_metric_word_count": 2,
    "metric_ok_word_count": 3,
    "closed_positive_metric_word_count": 4,
    "parent_state_count": 5,
    "state_count": 6,
    "new_state_count_vs_parent": 7,
    "parent_edge_count": 8,
    "undirected_edge_count": 9,
    "new_edge_count_vs_parent": 10,
    "component_count": 11,
    "combined_promoted_state_count": 12,
    "combined_promoted_only_state_count": 13,
    "merged_recurrent_class_size": 14,
    "merged_promoted_only_state_count": 15,
    "left_to_right_path_exists": 16,
    "shortest_path_length": 17,
    "parent_cut_edge_count": 18,
    "parent_cut_edge_survival_count": 19,
    "parent_cut_edge_still_cut_count": 20,
    "spectral_cut_edge_count": 21,
    "spectral_cut_promoted_edge_count": 22,
    "spectral_cut_promoted_only_edge_count": 23,
    "merged_lambda_2": 24,
    "merged_lambda_3": 25,
    "merged_cut_conductance": 26,
    "first_block_code": 27,
    "second_block_code": 28,
    "second_window_candidate_word_count": 29,
    "second_window_target_transfer_edge_id": 30,
}

X1E12_OBSERVABLES = {
    "merged_lambda_2",
    "merged_lambda_3",
    "merged_cut_conductance",
}


def table_rows(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def promoted_spans(
    word: tuple[int, ...],
) -> list[tuple[int, tuple[int, int, int, int]]]:
    sequence = tuple(parent.PREFIX_SYMBOLS) + word + word[:2]
    spans = []
    for rank in range(len(sequence) - 3):
        block = tuple(int(value) for value in sequence[rank : rank + 4])
        if block in PROMOTION_BLOCKS:
            spans.append((rank, block))
    return spans


def load_parent_promoted_geometry() -> dict[str, Any]:
    tables = np.load(PROMOTED_WINDOW_TABLES, allow_pickle=False)
    state_rows = table_rows(
        np.asarray(tables["state_table"], dtype=np.int64),
        STATE_COLUMNS,
    )
    edge_rows = table_rows(
        np.asarray(tables["edge_table"], dtype=np.int64),
        EDGE_COLUMNS,
    )
    spectral_rows = table_rows(
        np.asarray(tables["spectral_cut_table"], dtype=np.int64),
        SPECTRAL_CUT_COLUMNS,
    )
    word_by_state = {
        row["automaton_state_id"]: parent.word_from_row(row) for row in state_rows
    }
    parent_edges: set[tuple[tuple[int, ...], tuple[int, ...]]] = set()
    parent_cut_edges: set[tuple[tuple[int, ...], tuple[int, ...]]] = set()
    for row in edge_rows:
        key = parent.edge_word_key(
            word_by_state[row["source_state_id"]],
            word_by_state[row["target_state_id"]],
        )
        parent_edges.add(key)
        if row["new_spectral_cut_edge_flag"] == 1:
            parent_cut_edges.add(key)
    return {
        "state_count": len(state_rows),
        "edge_count": len(parent_edges),
        "old_edges": parent_edges,
        "old_cut_edges": parent_cut_edges,
        "parent_spectral_row": spectral_rows[0],
    }


def load_second_window_selection() -> dict[str, Any]:
    report = parent.load_json(SECOND_WINDOW_REPORT)
    witness = report.get("witness", {})
    selected_block = tuple(int(value) for value in witness["selected_second_window_block"])
    selected_word = tuple(int(value) for value in witness["selected_candidate_word"])
    selected_move = witness["selected_move"]
    return {
        "status": report.get("status"),
        "certificate_sha256": report.get("certificate_sha256"),
        "target_transfer_edge_id": int(witness["target_transfer_edge_id"]),
        "block": selected_block,
        "candidate_word": selected_word,
        "candidate_word_count": int(selected_move["candidate_word_count"]),
        "same_side_edge_count": int(selected_move["same_side_edge_count"]),
        "negative_side_edge_count": int(selected_move["negative_side_edge_count"]),
        "new_target_cut_flux_x1e12": int(
            selected_move["new_target_cut_flux_x1e12"]
        ),
        "new_target_weighted_conductance_x1e12": int(
            selected_move["new_target_weighted_conductance_x1e12"]
        ),
    }


def evaluate_second_window_language(
    repair_rows_by_block: dict[
        tuple[int, int, int, int],
        list[dict[str, int]],
    ],
) -> dict[str, Any]:
    original_promoted_spans = parent.promoted_spans
    parent.promoted_spans = promoted_spans
    try:
        return parent.evaluate_language(repair_rows_by_block)
    finally:
        parent.promoted_spans = original_promoted_spans


def build_payload_rows() -> dict[str, Any]:
    _repair_rows, grammar_stats, repair_rows_by_block = parent.grammar_rows()
    language = evaluate_second_window_language(repair_rows_by_block)
    graph = parent.build_graph(language["rows_by_word"])
    parent_geometry = load_parent_promoted_geometry()
    automaton = parent.build_automaton_rows(graph, parent_geometry)
    second_selection = load_second_window_selection()
    stats = Counter(language["stats"])
    merged_component = next(
        row for row in graph["component_rows"] if row["merged_boundary_flag"] == 1
    )
    spectral_row = automaton["spectral_rows"][0]
    observable_values = {
        "boundary_union_word_count": stats["boundary_union_word_count"],
        "trace_failure_word_count": stats["trace_failure_word_count"],
        "bad_metric_word_count": stats["bad_metric_word_count"],
        "metric_ok_word_count": stats["metric_ok_word_count"],
        "closed_positive_metric_word_count": stats[
            "closed_positive_metric_word_count"
        ],
        "parent_state_count": parent_geometry["state_count"],
        "state_count": len(automaton["state_rows"]),
        "new_state_count_vs_parent": len(automaton["state_rows"])
        - parent_geometry["state_count"],
        "parent_edge_count": parent_geometry["edge_count"],
        "undirected_edge_count": len(automaton["edge_rows"]),
        "new_edge_count_vs_parent": len(automaton["edge_rows"])
        - parent_geometry["edge_count"],
        "component_count": len(automaton["class_rows"]),
        "combined_promoted_state_count": sum(
            row["promoted_window_repair_flag"] for row in automaton["state_rows"]
        ),
        "combined_promoted_only_state_count": sum(
            row["promoted_only_flag"] for row in automaton["state_rows"]
        ),
        "merged_recurrent_class_size": spectral_row["state_count"],
        "merged_promoted_only_state_count": merged_component[
            "promoted_only_cell_count"
        ],
        "left_to_right_path_exists": graph["left_to_right_path_exists"],
        "shortest_path_length": graph["shortest_path_length"],
        "parent_cut_edge_count": spectral_row["old_cut_edge_count"],
        "parent_cut_edge_survival_count": spectral_row["old_cut_edge_survival_count"],
        "parent_cut_edge_still_cut_count": spectral_row[
            "old_cut_edge_still_cut_count"
        ],
        "spectral_cut_edge_count": spectral_row["cut_edge_count"],
        "spectral_cut_promoted_edge_count": spectral_row["promoted_cut_edge_count"],
        "spectral_cut_promoted_only_edge_count": spectral_row[
            "promoted_only_cut_edge_count"
        ],
        "merged_lambda_2": spectral_row["lambda_2_x1e12"],
        "merged_lambda_3": spectral_row["lambda_3_x1e12"],
        "merged_cut_conductance": spectral_row["cut_conductance_x1e12"],
        "first_block_code": parent.block_code(FIRST_WINDOW_BLOCK),
        "second_block_code": parent.block_code(SECOND_WINDOW_BLOCK),
        "second_window_candidate_word_count": second_selection[
            "candidate_word_count"
        ],
        "second_window_target_transfer_edge_id": second_selection[
            "target_transfer_edge_id"
        ],
    }
    observable_rows = []
    for observable_id, (key, code) in enumerate(
        SECOND_WINDOW_PROMOTION_OBSERVABLE_CODES.items()
    ):
        value = int(observable_values[key])
        scaled = value if key in X1E12_OBSERVABLES else value * SCALE
        observable_rows.append(
            {
                "observable_id": observable_id,
                "observable_code": code,
                "value_x1e12": scaled,
                "aux_id": -1,
            }
        )
    return {
        **graph,
        **automaton,
        "grammar_stats": grammar_stats,
        "language_stats": dict(stats),
        "parent_geometry": parent_geometry,
        "second_selection": second_selection,
        "observable_values": observable_values,
        "observable_rows": observable_rows,
    }


def build_payloads() -> dict[str, Any]:
    promoted_report = parent.load_json(PROMOTED_WINDOW_REPORT)
    promoted_certificate = parent.load_json(PROMOTED_WINDOW_CERTIFICATE)
    second_report = parent.load_json(SECOND_WINDOW_REPORT)
    second_certificate = parent.load_json(SECOND_WINDOW_CERTIFICATE)
    rows = build_payload_rows()

    cell_table = parent.table_from_rows(CELL_COLUMNS, rows["cell_rows"])
    component_table = parent.table_from_rows(COMPONENT_COLUMNS, rows["component_rows"])
    path_table = parent.table_from_rows(PATH_COLUMNS, rows["path_rows"])
    state_table = parent.table_from_rows(STATE_COLUMNS, rows["state_rows"])
    edge_table = parent.table_from_rows(EDGE_COLUMNS, rows["edge_rows"])
    recurrent_class_table = parent.table_from_rows(
        RECURRENT_CLASS_COLUMNS,
        rows["class_rows"],
    )
    native_recurrent_class_table = parent.table_from_rows(
        NATIVE_CLASS_COLUMNS,
        rows["native_class_rows"],
    )
    spectral_cut_table = parent.table_from_rows(
        SPECTRAL_CUT_COLUMNS,
        rows["spectral_rows"],
    )
    poincare_table = parent.table_from_rows(POINCARE_COLUMNS, rows["poincare_rows"])
    observable_table = parent.table_from_rows(OBSERVABLE_COLUMNS, rows["observable_rows"])

    observable_values = rows["observable_values"]
    spectral_row = rows["spectral_rows"][0]
    second_selection = rows["second_selection"]
    parent_spectral = rows["parent_geometry"]["parent_spectral_row"]
    checks = {
        "promoted_window_report_certified": promoted_report.get("status")
        == parent.STATUS,
        "promoted_window_certificate_certified": promoted_certificate.get("status")
        == parent.STATUS,
        "second_window_report_certified": second_report.get("status")
        == SECOND_WINDOW_STATUS,
        "second_window_certificate_certified": second_certificate.get("status")
        == SECOND_WINDOW_STATUS,
        "selected_second_window_block_is_promoted": second_selection["block"]
        == SECOND_WINDOW_BLOCK,
        "boundary_language_counts_are_expected": (
            observable_values["boundary_union_word_count"],
            observable_values["trace_failure_word_count"],
            observable_values["bad_metric_word_count"],
            observable_values["metric_ok_word_count"],
            observable_values["closed_positive_metric_word_count"],
        )
        == (234_678, 68_103, 140_378, 26_197, 984),
        "second_promotion_extends_parent_by_five_cells": (
            observable_values["parent_state_count"],
            observable_values["state_count"],
            observable_values["new_state_count_vs_parent"],
            observable_values["parent_edge_count"],
            observable_values["undirected_edge_count"],
            observable_values["new_edge_count_vs_parent"],
        )
        == (855, 860, 5, 2_561, 2_571, 10),
        "combined_promotion_counts_are_expected": (
            observable_values["combined_promoted_state_count"],
            observable_values["combined_promoted_only_state_count"],
            observable_values["merged_recurrent_class_size"],
            observable_values["merged_promoted_only_state_count"],
        )
        == (132, 14, 798, 11),
        "boundary_pair_remains_merged": (
            observable_values["left_to_right_path_exists"],
            observable_values["shortest_path_length"],
            spectral_row["left_side_code"],
            spectral_row["gate_side_code"],
            spectral_row["right_side_code"],
        )
        == (1, 2, 1, 1, 1),
        "parent_cut_lineage_stays_fixed": (
            observable_values["parent_cut_edge_count"],
            observable_values["parent_cut_edge_survival_count"],
            observable_values["parent_cut_edge_still_cut_count"],
            spectral_row["old_cut_edge_same_side_count"],
        )
        == (6, 6, 6, 0),
        "second_promotion_hits_all_cut_edges_without_moving_cut": (
            spectral_row["cut_edge_count"],
            spectral_row["derived_cut_edge_count"],
            spectral_row["promoted_cut_edge_count"],
            spectral_row["promoted_only_cut_edge_count"],
        )
        == (6, 6, 6, 0),
        "spectral_values_are_expected": (
            spectral_row["lambda_2_x1e12"],
            spectral_row["lambda_3_x1e12"],
            spectral_row["cut_conductance_x1e12"],
        )
        == (2_422_953_000, 9_097_373_000, 4_329_004_000),
        "spectral_readout_changes_from_parent": (
            spectral_row["lambda_2_x1e12"] > parent_spectral["lambda_2_x1e12"]
            and spectral_row["cut_conductance_x1e12"]
            < parent_spectral["cut_conductance_x1e12"]
        ),
        "table_shapes_match_codebooks": (
            tuple(cell_table.shape) == (observable_values["state_count"], len(CELL_COLUMNS))
            and tuple(component_table.shape)
            == (observable_values["component_count"], len(COMPONENT_COLUMNS))
            and tuple(path_table.shape) == (3, len(PATH_COLUMNS))
            and tuple(state_table.shape)
            == (observable_values["state_count"], len(STATE_COLUMNS))
            and tuple(edge_table.shape)
            == (observable_values["undirected_edge_count"], len(EDGE_COLUMNS))
            and tuple(recurrent_class_table.shape)
            == (observable_values["component_count"], len(RECURRENT_CLASS_COLUMNS))
            and tuple(native_recurrent_class_table.shape)[1]
            == len(NATIVE_CLASS_COLUMNS)
            and tuple(spectral_cut_table.shape) == (1, len(SPECTRAL_CUT_COLUMNS))
            and tuple(poincare_table.shape)[1] == len(POINCARE_COLUMNS)
            and tuple(observable_table.shape)
            == (
                len(SECOND_WINDOW_PROMOTION_OBSERVABLE_CODES),
                len(OBSERVABLE_COLUMNS),
            )
        ),
    }

    witness = {
        "promotion_blocks": [list(block) for block in PROMOTION_BLOCKS],
        "second_window_selection": {
            key: (list(value) if isinstance(value, tuple) else value)
            for key, value in second_selection.items()
        },
        "language_stats": rows["language_stats"],
        "state_count": observable_values["state_count"],
        "undirected_edge_count": observable_values["undirected_edge_count"],
        "component_sizes": rows["component_sizes"],
        "native_class_sizes": rows["native_class_sizes"],
        "promotion_profile": {
            "parent_state_count": observable_values["parent_state_count"],
            "new_state_count_vs_parent": observable_values[
                "new_state_count_vs_parent"
            ],
            "parent_edge_count": observable_values["parent_edge_count"],
            "new_edge_count_vs_parent": observable_values[
                "new_edge_count_vs_parent"
            ],
            "combined_promoted_state_count": observable_values[
                "combined_promoted_state_count"
            ],
            "combined_promoted_only_state_count": observable_values[
                "combined_promoted_only_state_count"
            ],
        },
        "parent_cut_lineage": {
            "parent_cut_edge_count": spectral_row["old_cut_edge_count"],
            "parent_cut_edge_survival_count": spectral_row[
                "old_cut_edge_survival_count"
            ],
            "parent_cut_edge_still_cut_count": spectral_row[
                "old_cut_edge_still_cut_count"
            ],
            "parent_cut_edge_same_side_count": spectral_row[
                "old_cut_edge_same_side_count"
            ],
        },
        "spectral_cut": {
            "parent_lambda_2_x1e12": parent_spectral["lambda_2_x1e12"],
            "lambda_2_x1e12": spectral_row["lambda_2_x1e12"],
            "parent_cut_conductance_x1e12": parent_spectral[
                "cut_conductance_x1e12"
            ],
            "cut_conductance_x1e12": spectral_row["cut_conductance_x1e12"],
            "cut_edge_count": spectral_row["cut_edge_count"],
            "derived_cut_edge_count": spectral_row["derived_cut_edge_count"],
            "promoted_cut_edge_count": spectral_row["promoted_cut_edge_count"],
            "promoted_only_cut_edge_count": spectral_row[
                "promoted_only_cut_edge_count"
            ],
            "positive_state_count": spectral_row["positive_state_count"],
            "negative_state_count": spectral_row["negative_state_count"],
            "positive_volume": spectral_row["positive_volume"],
            "negative_volume": spectral_row["negative_volume"],
        },
        "cell_table_sha256": parent.sha_array(cell_table),
        "component_table_sha256": parent.sha_array(component_table),
        "path_table_sha256": parent.sha_array(path_table),
        "state_table_sha256": parent.sha_array(state_table),
        "edge_table_sha256": parent.sha_array(edge_table),
        "recurrent_class_table_sha256": parent.sha_array(recurrent_class_table),
        "native_recurrent_class_table_sha256": parent.sha_array(
            native_recurrent_class_table
        ),
        "spectral_cut_table_sha256": parent.sha_array(spectral_cut_table),
        "poincare_table_sha256": parent.sha_array(poincare_table),
        "observable_table_sha256": parent.sha_array(observable_table),
    }

    promotion = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_second_window_promotion@1",
        "object": "d20",
        "parents": {
            "promoted_window": PROMOTED_WINDOW_REPORT.relative_to(ROOT).as_posix(),
            "second_window_search": SECOND_WINDOW_REPORT.relative_to(ROOT).as_posix(),
        },
        "promotion_rule": {
            "blocks": [list(block) for block in PROMOTION_BLOCKS],
            "source": [
                "first block from the promoted flow-window rule",
                "second block from the target-local promoted-transfer cut search",
            ],
            "language_test": [
                "use the certified radius-three boundary-pair word union",
                "filter to delta_twice=2, variation<=223, and closed positivity",
                "admit native repair words, skip-derived repair words, or words containing either promoted four-symbol window",
            ],
        },
        "summary": {
            "state_count": observable_values["state_count"],
            "new_state_count_vs_parent": observable_values[
                "new_state_count_vs_parent"
            ],
            "undirected_edge_count": observable_values["undirected_edge_count"],
            "spectral_cut_edge_count": spectral_row["cut_edge_count"],
            "parent_cut_edge_still_cut_count": spectral_row[
                "old_cut_edge_still_cut_count"
            ],
            "spectral_cut_promoted_edge_count": spectral_row[
                "promoted_cut_edge_count"
            ],
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_second_window_promotion_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_SECOND_WINDOW_PROMOTION_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the selected 1,4,5,5 second-window rule can be promoted globally beside 5,5,2,5",
            "the combined promotion adds five cells and ten one-edit edges beyond the parent promoted automaton",
            "the left-gate-right boundary path remains length two in the dominant component",
            "the parent six-edge cut survives unchanged as the fresh Fiedler cut",
            "all six surviving cut edges now touch promoted-window support, closing the previous support gap without dissolving the bottleneck",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_second_window_promotion@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "Promoting the second-window block 1,4,5,5 globally alongside "
            "5,5,2,5 adds five closed-positive cells beyond the 855-state "
            "parent promoted automaton, giving 860 states and 2,571 "
            "undirected one-edit edges. The dominant component grows to 798 "
            "states and keeps the left -> gate -> right path at length two. "
            "The old six-edge parent cut does not move: all six parent cut "
            "edges survive and all six remain on the fresh Fiedler cut. The "
            "support gap closes because all six cut edges now touch promoted "
            "window support; lambda_2 rises to 2422953000/1e12 and the "
            "cut conductance drops to 4329004000/1e12, but the structural "
            "six-edge aperture remains."
        ),
        "stage_protocol": {
            "draft": "promote the second-window block beside the first promoted block",
            "witness": "enumerate combined-promotion cells and rebuild the one-edit automaton",
            "coherence": "compare parent promoted edges, parent cut edges, and new spectral support",
            "closure": "certify the boundary merge and fresh spectral/Poincare geometry",
            "emit": "emit second-window promotion artifacts, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "promoted_window_report": parent.input_entry(
                PROMOTED_WINDOW_REPORT,
                {
                    "status": promoted_report.get("status"),
                    "certificate_sha256": promoted_report.get("certificate_sha256"),
                },
            ),
            "promoted_window_certificate": parent.input_entry(
                PROMOTED_WINDOW_CERTIFICATE
            ),
            "promoted_window_tables": parent.input_entry(PROMOTED_WINDOW_TABLES),
            "second_window_report": parent.input_entry(
                SECOND_WINDOW_REPORT,
                {
                    "status": second_report.get("status"),
                    "certificate_sha256": second_report.get("certificate_sha256"),
                },
            ),
            "second_window_certificate": parent.input_entry(SECOND_WINDOW_CERTIFICATE),
            "second_window_tables": parent.input_entry(SECOND_WINDOW_TABLES),
            "derive_script": parent.input_entry(DERIVE_SCRIPT),
            "validator": parent.input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": parent.relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "second_window_promotion": parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_second_window_promotion.json"
            ),
            "second_window_promotion_cells_csv": parent.relpath(
                OUT_DIR / "aperture_closure_tail_second_window_promotion_cells.csv"
            ),
            "second_window_promotion_components_csv": parent.relpath(
                OUT_DIR
                / "aperture_closure_tail_second_window_promotion_components.csv"
            ),
            "second_window_promotion_path_csv": parent.relpath(
                OUT_DIR / "aperture_closure_tail_second_window_promotion_path.csv"
            ),
            "second_window_promotion_states_csv": parent.relpath(
                OUT_DIR / "aperture_closure_tail_second_window_promotion_states.csv"
            ),
            "second_window_promotion_edges_csv": parent.relpath(
                OUT_DIR / "aperture_closure_tail_second_window_promotion_edges.csv"
            ),
            "second_window_promotion_recurrent_classes_csv": parent.relpath(
                OUT_DIR
                / "aperture_closure_tail_second_window_promotion_recurrent_classes.csv"
            ),
            "second_window_promotion_native_recurrent_classes_csv": parent.relpath(
                OUT_DIR
                / "aperture_closure_tail_second_window_promotion_native_recurrent_classes.csv"
            ),
            "second_window_promotion_spectral_cut_csv": parent.relpath(
                OUT_DIR
                / "aperture_closure_tail_second_window_promotion_spectral_cut.csv"
            ),
            "second_window_promotion_poincare_csv": parent.relpath(
                OUT_DIR / "aperture_closure_tail_second_window_promotion_poincare.csv"
            ),
            "second_window_promotion_observables_csv": parent.relpath(
                OUT_DIR
                / "aperture_closure_tail_second_window_promotion_observables.csv"
            ),
            "second_window_promotion_tables": parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_second_window_promotion_tables.npz"
            ),
            "second_window_promotion_certificate": parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_second_window_promotion_certificate.json"
            ),
            "manifest": parent.relpath(OUT_DIR / "manifest.json"),
            "report": parent.relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the combined 5,5,2,5 and 1,4,5,5 promotion over the certified radius-three boundary-pair union",
                "the combined-promotion grammar cell/component decomposition",
                "the rebuilt one-edit automaton and native recurrent classes",
                "parent promoted spectral-cut lineage under the combined promotion",
                "the fresh spectral cut and two-mode Poincare disk readout of the combined-promotion dominant class",
            ],
            "does_not_certify_because_not_required": [
                "stationary transfer flow on the combined-promotion automaton",
                "boundary words outside the certified radius-three side union",
                "promotion closure beyond the two certified window blocks",
                "normal JSON compiler wiring for C985 objects",
            ],
        },
        "next_highest_yield_item": (
            "Run the native-biased transfer operator on the second-window "
            "promoted automaton now that every surviving cut edge touches "
            "promoted support, and test whether stationary flow still loads "
            "the same six-edge aperture."
        ),
    }
    report["certificate_sha256"] = parent.self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_second_window_promotion_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified promoted-window and second-window-search artifacts",
            "promote the selected 1,4,5,5 window beside the existing 5,5,2,5 window",
            "rebuild grammar components and the one-edit combined-promotion automaton",
            "track parent promoted spectral-cut lineage and recompute fresh spectral/Poincare geometry",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = parent.self_hash(manifest, "manifest_sha256")

    return {
        "second_window_promotion": promotion,
        "second_window_promotion_cells_csv": parent.csv_text(
            CELL_COLUMNS,
            rows["cell_rows"],
        ),
        "second_window_promotion_components_csv": parent.csv_text(
            COMPONENT_COLUMNS,
            rows["component_rows"],
        ),
        "second_window_promotion_path_csv": parent.csv_text(
            PATH_COLUMNS,
            rows["path_rows"],
        ),
        "second_window_promotion_states_csv": parent.csv_text(
            STATE_COLUMNS,
            rows["state_rows"],
        ),
        "second_window_promotion_edges_csv": parent.csv_text(
            EDGE_COLUMNS,
            rows["edge_rows"],
        ),
        "second_window_promotion_recurrent_classes_csv": parent.csv_text(
            RECURRENT_CLASS_COLUMNS,
            rows["class_rows"],
        ),
        "second_window_promotion_native_recurrent_classes_csv": parent.csv_text(
            NATIVE_CLASS_COLUMNS,
            rows["native_class_rows"],
        ),
        "second_window_promotion_spectral_cut_csv": parent.csv_text(
            SPECTRAL_CUT_COLUMNS,
            rows["spectral_rows"],
        ),
        "second_window_promotion_poincare_csv": parent.csv_text(
            POINCARE_COLUMNS,
            rows["poincare_rows"],
        ),
        "second_window_promotion_observables_csv": parent.csv_text(
            OBSERVABLE_COLUMNS,
            rows["observable_rows"],
        ),
        "cell_table": cell_table,
        "component_table": component_table,
        "path_table": path_table,
        "state_table": state_table,
        "edge_table": edge_table,
        "recurrent_class_table": recurrent_class_table,
        "native_recurrent_class_table": native_recurrent_class_table,
        "spectral_cut_table": spectral_cut_table,
        "poincare_table": poincare_table,
        "observable_table": observable_table,
        "second_window_promotion_certificate": certificate,
        "report": report,
        "manifest": manifest,
    }


def update_index(report: dict[str, Any]) -> None:
    if parent.INDEX_PATH.exists():
        index_payload = parent.load_json(parent.INDEX_PATH)
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
    parent.write_json(parent.INDEX_PATH, updated)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    parent.write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_second_window_promotion.json",
        payloads["second_window_promotion"],
    )
    (OUT_DIR / "aperture_closure_tail_second_window_promotion_cells.csv").write_text(
        payloads["second_window_promotion_cells_csv"],
        encoding="utf-8",
    )
    (
        OUT_DIR / "aperture_closure_tail_second_window_promotion_components.csv"
    ).write_text(
        payloads["second_window_promotion_components_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_second_window_promotion_path.csv").write_text(
        payloads["second_window_promotion_path_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_second_window_promotion_states.csv").write_text(
        payloads["second_window_promotion_states_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_second_window_promotion_edges.csv").write_text(
        payloads["second_window_promotion_edges_csv"],
        encoding="utf-8",
    )
    (
        OUT_DIR
        / "aperture_closure_tail_second_window_promotion_recurrent_classes.csv"
    ).write_text(
        payloads["second_window_promotion_recurrent_classes_csv"],
        encoding="utf-8",
    )
    (
        OUT_DIR
        / "aperture_closure_tail_second_window_promotion_native_recurrent_classes.csv"
    ).write_text(
        payloads["second_window_promotion_native_recurrent_classes_csv"],
        encoding="utf-8",
    )
    (
        OUT_DIR / "aperture_closure_tail_second_window_promotion_spectral_cut.csv"
    ).write_text(
        payloads["second_window_promotion_spectral_cut_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_second_window_promotion_poincare.csv").write_text(
        payloads["second_window_promotion_poincare_csv"],
        encoding="utf-8",
    )
    (
        OUT_DIR / "aperture_closure_tail_second_window_promotion_observables.csv"
    ).write_text(
        payloads["second_window_promotion_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_second_window_promotion_tables.npz",
        cell_table=payloads["cell_table"],
        component_table=payloads["component_table"],
        path_table=payloads["path_table"],
        state_table=payloads["state_table"],
        edge_table=payloads["edge_table"],
        recurrent_class_table=payloads["recurrent_class_table"],
        native_recurrent_class_table=payloads["native_recurrent_class_table"],
        spectral_cut_table=payloads["spectral_cut_table"],
        poincare_table=payloads["poincare_table"],
        observable_table=payloads["observable_table"],
    )
    parent.write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_second_window_promotion_certificate.json",
        payloads["second_window_promotion_certificate"],
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
