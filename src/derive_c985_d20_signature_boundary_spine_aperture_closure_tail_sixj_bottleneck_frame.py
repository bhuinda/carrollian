from __future__ import annotations

import csv
import json
from math import comb
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator import (
        OUT_DIR as SECOND_WINDOW_TRANSFER_DIR,
        SECOND_WINDOW_PROMOTION_STATES,
        STATUS as SECOND_WINDOW_TRANSFER_STATUS,
        TRANSFER_EDGE_COLUMNS,
        TRANSFER_STATE_COLUMNS,
        build_payloads as build_second_window_transfer_payloads,
    )
    from .derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        OBJECT_LABELS,
        input_entry,
        load_json,
        relpath,
        self_hash,
        sha_array,
        write_json,
    )
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator import (
        OUT_DIR as SECOND_WINDOW_TRANSFER_DIR,
        SECOND_WINDOW_PROMOTION_STATES,
        STATUS as SECOND_WINDOW_TRANSFER_STATUS,
        TRANSFER_EDGE_COLUMNS,
        TRANSFER_STATE_COLUMNS,
        build_payloads as build_second_window_transfer_payloads,
    )
    from derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        OBJECT_LABELS,
        input_entry,
        load_json,
        relpath,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT


THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_SIXJ_BOTTLENECK_FRAME_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

SECOND_WINDOW_TRANSFER_REPORT = SECOND_WINDOW_TRANSFER_DIR / "report.json"
SECOND_WINDOW_TRANSFER_CERTIFICATE = (
    SECOND_WINDOW_TRANSFER_DIR
    / "signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator_certificate.json"
)
SECOND_WINDOW_TRANSFER_TABLES = (
    SECOND_WINDOW_TRANSFER_DIR
    / "signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator_tables.npz"
)
SECOND_WINDOW_TRANSFER_STATES = (
    SECOND_WINDOW_TRANSFER_DIR
    / "aperture_closure_tail_second_window_transfer_states.csv"
)
SECOND_WINDOW_TRANSFER_EDGES = (
    SECOND_WINDOW_TRANSFER_DIR
    / "aperture_closure_tail_second_window_transfer_edges.csv"
)
SECOND_WINDOW_TRANSFER_CENTERS = (
    SECOND_WINDOW_TRANSFER_DIR
    / "aperture_closure_tail_second_window_transfer_centers.csv"
)

FINAL_MULTIFUSION_REPORT = (
    D20_INVARIANTS
    / "proof_obligations"
    / "c985_final_multifusion_certificate"
    / "report.json"
)
SYMBOLIC_ASSOCIATIVITY_REPORT = (
    D20_INVARIANTS
    / "proof_obligations"
    / "c985_d20_symbolic_associativity"
    / "report.json"
)
MOG_RESOLVENT = ROOT / "data" / "selectors" / "mog_resolvent_invariant.json"
WU_SPINH_6J_MARKING = ROOT / "data" / "selectors" / "wu_spinh_6j_marking.json"

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame.py"
)

LABEL_TO_CODE = {label: idx for idx, label in enumerate(OBJECT_LABELS)}
AXIS_CODES = {"B": 0, "V": 1, "S": 2}

SECTOR_FRAME_COLUMNS = [
    "sector_code",
    "axis_code",
    "polarity",
    "tetra_edge_u",
    "tetra_edge_v",
    "opposite_sector_code",
]
MOG_EDGE_COLUMNS = [
    "frame_edge_id",
    "column_a",
    "column_b",
    "label_a_code",
    "label_b_code",
    "pair_octad_index",
    "big_cell_coordinate",
    "opposite_frame_edge_id",
    "wu_radical_edge_flag",
    "wu_radical_opposite_edge_flag",
]
CUT_EDGE_COLUMNS = [
    "frame_edge_id",
    "transfer_edge_id",
    "source_state_id",
    "target_state_id",
    "edge_weight",
    "derived_transition_flag",
    "promoted_transition_flag",
    "old_spectral_cut_edge_flag",
    "spectral_cut_edge_flag",
    "undirected_stationary_flux_x1e12",
    "source_side_code",
    "target_side_code",
    "source_stationary_mass_x1e12",
    "target_stationary_mass_x1e12",
    "source_weighted_degree",
    "target_weighted_degree",
    "source_word_length",
    "target_word_length",
    "edit_prefix_length",
    "source_edit_length",
    "target_edit_length",
    "abstract_sector_code",
    "abstract_tetra_edge_u",
    "abstract_tetra_edge_v",
    "mog_column_a",
    "mog_column_b",
    "wu_radical_edge_flag",
]
OBSERVABLE_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBSERVABLE_CODES = {
    "h6_sector_count": 0,
    "abstract_tetrahedron_vertex_count": 1,
    "abstract_tetrahedron_edge_count": 2,
    "lambda2_h6_address_count": 3,
    "spin12_big_cell_dimension": 4,
    "d20_boundary_face_count": 5,
    "symbolic_canonical_triple_count": 6,
    "c985_simple_count": 7,
    "c985_object_count": 8,
    "second_window_transfer_state_count": 9,
    "second_window_transfer_edge_count": 10,
    "second_window_cut_edge_count": 11,
    "second_window_cut_flux_x1e12": 12,
    "per_cut_edge_flux_x1e12": 13,
    "old_cut_edge_count": 14,
    "promoted_cut_edge_count": 15,
    "cut_centers_coincide": 16,
    "all_spin_one_6j_numerator": 17,
    "all_spin_one_6j_denominator": 18,
    "all_spin_one_f_numerator": 19,
    "all_spin_one_f_denominator": 20,
    "w_d6_order": 21,
    "be3_order": 22,
    "mog_k4_vertex_count": 23,
    "mog_k4_edge_count": 24,
    "final_multifusion_certified": 25,
    "pentagon_length_four_chain_count": 26,
}
CENTER_COORDINATE_KEYS = [
    "center_x_x1e12",
    "center_y_x1e12",
    "center_radius_x1e12",
]


def csv_text(headers: list[str], rows: list[dict[str, Any]]) -> str:
    lines = [",".join(headers)]
    for row in rows:
        lines.append(",".join(str(row.get(header, "")) for header in headers))
    return "\n".join(lines) + "\n"


def table_from_rows(columns: list[str], rows: list[dict[str, int]]) -> np.ndarray:
    return np.asarray(
        [[int(row[column]) for column in columns] for row in rows],
        dtype=np.int64,
    )


def rows_from_table(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def word_to_text(word: list[int]) -> str:
    return ".".join(str(symbol) for symbol in word)


def load_promotion_words() -> dict[int, dict[str, Any]]:
    words: dict[int, dict[str, Any]] = {}
    with SECOND_WINDOW_PROMOTION_STATES.open("r", encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            state_id = int(row["automaton_state_id"])
            word_length = int(row["word_length"])
            word = [int(row[f"word_symbol_{idx}_id"]) for idx in range(word_length)]
            words[state_id] = {
                "word": word,
                "word_length": word_length,
                "word_text": word_to_text(word),
            }
    return words


def edit_window(source: list[int], target: list[int]) -> dict[str, Any]:
    prefix = 0
    limit = min(len(source), len(target))
    while prefix < limit and source[prefix] == target[prefix]:
        prefix += 1

    suffix = 0
    while (
        suffix < len(source) - prefix
        and suffix < len(target) - prefix
        and source[len(source) - 1 - suffix] == target[len(target) - 1 - suffix]
    ):
        suffix += 1

    source_mid = source[prefix : len(source) - suffix if suffix else len(source)]
    target_mid = target[prefix : len(target) - suffix if suffix else len(target)]
    return {
        "edit_prefix_length": prefix,
        "edit_suffix_length": suffix,
        "source_edit_symbols": source_mid,
        "target_edit_symbols": target_mid,
        "source_edit_text": word_to_text(source_mid),
        "target_edit_text": word_to_text(target_mid),
        "source_edit_length": len(source_mid),
        "target_edit_length": len(target_mid),
    }


def build_sector_frame_rows() -> list[dict[str, Any]]:
    specs = [
        ("B-", "B", -1, 0, 1, "B+"),
        ("B+", "B", 1, 2, 3, "B-"),
        ("V-", "V", -1, 0, 2, "V+"),
        ("V+", "V", 1, 1, 3, "V-"),
        ("S-", "S", -1, 0, 3, "S+"),
        ("S+", "S", 1, 1, 2, "S-"),
    ]
    return [
        {
            "sector_label": label,
            "sector_code": LABEL_TO_CODE[label],
            "axis_code": AXIS_CODES[axis],
            "axis": axis,
            "polarity": polarity,
            "tetra_edge": f"{u}{v}",
            "tetra_edge_u": u,
            "tetra_edge_v": v,
            "opposite_sector_label": opposite,
            "opposite_sector_code": LABEL_TO_CODE[opposite],
        }
        for label, axis, polarity, u, v, opposite in specs
    ]


def big_cell_coordinate_map(wu_marking: dict[str, Any]) -> dict[tuple[str, str], int]:
    out: dict[tuple[str, str], int] = {}
    for row in wu_marking["spin12_6j_bridge"]["big_cell_coordinate_map"]:
        pair = row.get("pair")
        if isinstance(pair, list) and len(pair) == 2:
            out[(str(pair[0]), str(pair[1]))] = int(row["coordinate"])
    return out


def build_mog_edge_rows(
    mog_resolvent: dict[str, Any],
    wu_marking: dict[str, Any],
) -> list[dict[str, Any]]:
    tetra = mog_resolvent["tetrahedral_6j_frame"]
    support = mog_resolvent["support_nullspace_mog_interaction"]
    radical = mog_resolvent["wu_radical_as_mog_octad"]
    coordinates = big_cell_coordinate_map(wu_marking)

    pairs = [tuple(pair) for pair in tetra["tetrahedron_edge_column_pairs"]]
    labels = [tuple(pair) for pair in tetra["tetrahedron_edge_labels"]]
    pair_indices = support["pair_octads_in_support_nullspace_indices"]
    pair_to_id = {pair: idx for idx, pair in enumerate(pairs)}
    opposite: dict[int, int] = {}
    for pair_a, pair_b in tetra["tetrahedron_opposite_edge_pairs"]:
        a = pair_to_id[tuple(pair_a)]
        b = pair_to_id[tuple(pair_b)]
        opposite[a] = b
        opposite[b] = a

    radical_pair = tuple(radical["radical_column_pair"])
    radical_opposite_pair = tuple(radical["opposite_edge_to_radical_in_K4"])
    rows: list[dict[str, Any]] = []
    for idx, (pair, label_pair, pair_octad_index) in enumerate(
        zip(pairs, labels, pair_indices)
    ):
        rows.append(
            {
                "frame_edge_id": idx,
                "column_a": int(pair[0]),
                "column_b": int(pair[1]),
                "label_a": label_pair[0],
                "label_b": label_pair[1],
                "label_a_code": LABEL_TO_CODE[label_pair[0]],
                "label_b_code": LABEL_TO_CODE[label_pair[1]],
                "pair_octad_index": int(pair_octad_index),
                "big_cell_coordinate": coordinates[label_pair],
                "opposite_frame_edge_id": opposite[idx],
                "wu_radical_edge_flag": int(pair == radical_pair),
                "wu_radical_opposite_edge_flag": int(pair == radical_opposite_pair),
            }
        )
    return rows


def build_cut_edge_rows(
    transfer_payloads: dict[str, Any],
    sector_rows: list[dict[str, Any]],
    mog_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, int]]]:
    edge_rows = rows_from_table(transfer_payloads["edge_table"], TRANSFER_EDGE_COLUMNS)
    state_rows = rows_from_table(
        transfer_payloads["state_table"],
        TRANSFER_STATE_COLUMNS,
    )
    state_by_id = {row["automaton_state_id"]: row for row in state_rows}
    word_by_state = load_promotion_words()

    cut_edges = [
        row
        for row in edge_rows
        if row["spectral_cut_edge_flag"] == 1
    ]
    cut_edges.sort(
        key=lambda row: (
            -row["undirected_stationary_flux_x1e12"],
            row["transfer_edge_id"],
        )
    )

    csv_rows: list[dict[str, Any]] = []
    numeric_rows: list[dict[str, int]] = []
    for frame_edge_id, edge in enumerate(cut_edges):
        source = state_by_id[edge["source_state_id"]]
        target = state_by_id[edge["target_state_id"]]
        source_word = word_by_state[edge["source_state_id"]]["word"]
        target_word = word_by_state[edge["target_state_id"]]["word"]
        window = edit_window(source_word, target_word)
        sector = sector_rows[frame_edge_id]
        mog = mog_rows[frame_edge_id]
        base = {
            "frame_edge_id": frame_edge_id,
            "transfer_edge_id": edge["transfer_edge_id"],
            "source_state_id": edge["source_state_id"],
            "target_state_id": edge["target_state_id"],
            "edge_weight": edge["edge_weight"],
            "derived_transition_flag": edge["derived_transition_flag"],
            "promoted_transition_flag": edge["promoted_transition_flag"],
            "old_spectral_cut_edge_flag": edge["old_spectral_cut_edge_flag"],
            "spectral_cut_edge_flag": edge["spectral_cut_edge_flag"],
            "undirected_stationary_flux_x1e12": edge[
                "undirected_stationary_flux_x1e12"
            ],
            "source_side_code": source["spectral_side_code"],
            "target_side_code": target["spectral_side_code"],
            "source_stationary_mass_x1e12": source["stationary_mass_x1e12"],
            "target_stationary_mass_x1e12": target["stationary_mass_x1e12"],
            "source_weighted_degree": source["weighted_degree"],
            "target_weighted_degree": target["weighted_degree"],
            "source_word_length": len(source_word),
            "target_word_length": len(target_word),
            "edit_prefix_length": window["edit_prefix_length"],
            "source_edit_length": window["source_edit_length"],
            "target_edit_length": window["target_edit_length"],
            "abstract_sector_code": sector["sector_code"],
            "abstract_tetra_edge_u": sector["tetra_edge_u"],
            "abstract_tetra_edge_v": sector["tetra_edge_v"],
            "mog_column_a": mog["column_a"],
            "mog_column_b": mog["column_b"],
            "wu_radical_edge_flag": mog["wu_radical_edge_flag"],
        }
        numeric_rows.append(dict(base))
        csv_rows.append(
            base
            | {
                "abstract_sector_label": sector["sector_label"],
                "abstract_tetra_edge": sector["tetra_edge"],
                "mog_edge_label": f"{mog['label_a']}^{mog['label_b']}",
                "source_word": word_to_text(source_word),
                "target_word": word_to_text(target_word),
                "source_edit": window["source_edit_text"],
                "target_edit": window["target_edit_text"],
            }
        )
    return csv_rows, numeric_rows


def build_observable_rows(
    transfer_report: dict[str, Any],
    final_report: dict[str, Any],
    symbolic_report: dict[str, Any],
    mog_resolvent: dict[str, Any],
) -> list[dict[str, int]]:
    transfer_witness = transfer_report["witness"]
    final_witness = final_report["witness"]
    symbolic_witness = symbolic_report["witness"]
    tetra = mog_resolvent["tetrahedral_6j_frame"]
    spin = mog_resolvent["spin12_mog_duality"]
    cut_center = transfer_witness["cut_center"]
    promoted_cut_center = transfer_witness["promoted_cut_center"]
    centers_coincide = all(
        cut_center[key] == promoted_cut_center[key] for key in CENTER_COORDINATE_KEYS
    )

    values = {
        "h6_sector_count": len(OBJECT_LABELS),
        "abstract_tetrahedron_vertex_count": 4,
        "abstract_tetrahedron_edge_count": 6,
        "lambda2_h6_address_count": spin["Lambda2_H6_address_count"],
        "spin12_big_cell_dimension": spin["scalar_plus_Lambda2_H6_big_cell_dimension"],
        "d20_boundary_face_count": comb(len(OBJECT_LABELS), 3),
        "symbolic_canonical_triple_count": symbolic_witness[
            "canonical_symbolic_triple_count"
        ],
        "c985_simple_count": final_witness["simple_count"],
        "c985_object_count": len(final_witness["object_labels"]),
        "second_window_transfer_state_count": transfer_witness[
            "transfer_state_count"
        ],
        "second_window_transfer_edge_count": transfer_witness["transfer_edge_count"],
        "second_window_cut_edge_count": transfer_witness["surviving_cut_flow"][
            "cut_edge_count"
        ],
        "second_window_cut_flux_x1e12": transfer_witness["surviving_cut_flow"][
            "cut_flux_x1e12"
        ],
        "per_cut_edge_flux_x1e12": transfer_witness["surviving_cut_flow"][
            "cut_flux_x1e12"
        ]
        // transfer_witness["surviving_cut_flow"]["cut_edge_count"],
        "old_cut_edge_count": transfer_witness["surviving_cut_flow"][
            "old_cut_edge_count"
        ],
        "promoted_cut_edge_count": transfer_witness["surviving_cut_flow"][
            "promoted_cut_edge_count"
        ],
        "cut_centers_coincide": int(centers_coincide),
        "all_spin_one_6j_numerator": 1,
        "all_spin_one_6j_denominator": 6,
        "all_spin_one_f_numerator": 1,
        "all_spin_one_f_denominator": 2,
        "w_d6_order": tetra["W_D6_order"],
        "be3_order": tetra["Gamma_order"],
        "mog_k4_vertex_count": len(tetra["tetrahedron_vertices_columns"]),
        "mog_k4_edge_count": len(tetra["tetrahedron_edge_column_pairs"]),
        "final_multifusion_certified": int(final_report["status"].endswith("CERTIFIED")),
        "pentagon_length_four_chain_count": final_witness[
            "pentagon_length_four_chain_count"
        ],
    }
    return [
        {
            "observable_id": idx,
            "observable_code": code,
            "value": int(values[key]),
            "scale_code": 0,
        }
        for idx, (key, code) in enumerate(OBSERVABLE_CODES.items())
    ]


def build_payloads() -> dict[str, Any]:
    transfer_report = load_json(SECOND_WINDOW_TRANSFER_REPORT)
    transfer_certificate = load_json(SECOND_WINDOW_TRANSFER_CERTIFICATE)
    final_report = load_json(FINAL_MULTIFUSION_REPORT)
    symbolic_report = load_json(SYMBOLIC_ASSOCIATIVITY_REPORT)
    mog_resolvent = load_json(MOG_RESOLVENT)
    wu_marking = load_json(WU_SPINH_6J_MARKING)
    transfer_payloads = build_second_window_transfer_payloads()

    sector_rows = build_sector_frame_rows()
    mog_rows = build_mog_edge_rows(mog_resolvent, wu_marking)
    cut_csv_rows, cut_numeric_rows = build_cut_edge_rows(
        transfer_payloads,
        sector_rows,
        mog_rows,
    )
    observable_rows = build_observable_rows(
        transfer_report,
        final_report,
        symbolic_report,
        mog_resolvent,
    )

    sector_table = table_from_rows(SECTOR_FRAME_COLUMNS, sector_rows)
    mog_table = table_from_rows(MOG_EDGE_COLUMNS, mog_rows)
    cut_table = table_from_rows(CUT_EDGE_COLUMNS, cut_numeric_rows)
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    transfer_witness = transfer_report["witness"]
    final_witness = final_report["witness"]
    symbolic_witness = symbolic_report["witness"]
    tetra = mog_resolvent["tetrahedral_6j_frame"]
    spin = mog_resolvent["spin12_mog_duality"]
    cut_edges = rows_from_table(cut_table, CUT_EDGE_COLUMNS)
    cut_fluxes = {
        row["undirected_stationary_flux_x1e12"] for row in cut_edges
    }
    cut_flux_sum = sum(
        row["undirected_stationary_flux_x1e12"] for row in cut_edges
    )
    cut_centers_coincide = all(
        transfer_witness["cut_center"][key]
        == transfer_witness["promoted_cut_center"][key]
        for key in CENTER_COORDINATE_KEYS
    )

    abstract_tetra_edges = {
        (row["tetra_edge_u"], row["tetra_edge_v"]) for row in sector_rows
    }
    mog_tetra_edges = {(row["column_a"], row["column_b"]) for row in mog_rows}
    checks = {
        "second_window_transfer_report_certified": transfer_report.get("status")
        == SECOND_WINDOW_TRANSFER_STATUS,
        "second_window_transfer_certificate_certified": transfer_certificate.get(
            "status"
        )
        == SECOND_WINDOW_TRANSFER_STATUS,
        "final_multifusion_report_certified": final_report.get("status")
        == "C985_FINITE_SEMISIMPLE_MULTIFUSION_CATEGORY_CERTIFIED",
        "symbolic_associativity_report_certified": symbolic_report.get("status")
        == "C985_D20_SYMBOLIC_ASSOCIATIVITY_CERTIFIED",
        "wu_spinh_6j_marking_certified": wu_marking.get("status")
        == "WU_SPINH_OCTAD_SPIN12_6J_MARKING_CERTIFIED_GOLAY_SELECTOR_STILL_EXTERNAL",
        "mog_resolvent_6j_k4_certified": mog_resolvent.get("status")
        == "MOG_RESOLVENT_SEXTET_AND_WU_6J_TETRAHEDRON_CERTIFIED_GOLAY_SELECTOR_STILL_EXTERNAL",
        "abstract_six_sector_tetrahedron_is_k4": (
            len(sector_rows),
            len(abstract_tetra_edges),
            sorted({endpoint for edge in abstract_tetra_edges for endpoint in edge}),
        )
        == (6, 6, [0, 1, 2, 3]),
        "mog_support_nullspace_tetrahedron_is_k4": (
            bool(
                mog_resolvent["support_nullspace_mog_interaction"][
                    "edge_set_is_complete_graph_K4"
                ]
            ),
            len(mog_rows),
            len(mog_tetra_edges),
            sorted({endpoint for edge in mog_tetra_edges for endpoint in edge}),
        )
        == (True, 6, 6, [1, 3, 4, 5]),
        "lambda2_and_spin12_counts_match": (
            spin["Lambda2_H6_address_count"],
            spin["scalar_plus_Lambda2_H6_big_cell_dimension"],
        )
        == (15, 16),
        "d20_boundary_count_is_c6_3": comb(len(OBJECT_LABELS), 3) == 20,
        "scalar_6j_anchor_is_present": (
            tetra["all_spin_one_6j_rational"],
            tetra["all_spin_one_F_rational"],
        )
        == ("1/6", "1/2"),
        "second_window_cut_is_exactly_six_edges": tuple(cut_table.shape)
        == (6, len(CUT_EDGE_COLUMNS)),
        "second_window_cut_flux_is_uniform": cut_fluxes == {170_677_590},
        "second_window_cut_flux_sum_matches_report": cut_flux_sum
        == transfer_witness["surviving_cut_flow"]["cut_flux_x1e12"],
        "all_cut_edges_are_old_and_promoted_derived_edges": all(
            row["derived_transition_flag"] == 1
            and row["promoted_transition_flag"] == 1
            and row["old_spectral_cut_edge_flag"] == 1
            and row["spectral_cut_edge_flag"] == 1
            for row in cut_edges
        ),
        "cut_edges_cross_positive_to_negative_side": all(
            row["source_side_code"] == 1 and row["target_side_code"] == -1
            for row in cut_edges
        ),
        "cut_centers_coincide": cut_centers_coincide,
        "symbolic_boundary_has_56_canonical_triples": symbolic_witness[
            "canonical_symbolic_triple_count"
        ]
        == 56,
        "c985_body_counts_match": (
            final_witness["simple_count"],
            len(final_witness["object_labels"]),
        )
        == (985, 6),
        "table_shapes_match_codebooks": (
            tuple(sector_table.shape),
            tuple(mog_table.shape),
            tuple(cut_table.shape),
            tuple(observable_table.shape),
        )
        == (
            (6, len(SECTOR_FRAME_COLUMNS)),
            (6, len(MOG_EDGE_COLUMNS)),
            (6, len(CUT_EDGE_COLUMNS)),
            (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
        ),
    }

    witness = {
        "local_6j_scalar_anchor": {
            "all_spin_one_wigner_6j": tetra["all_spin_one_6j_rational"],
            "all_spin_one_normalized_F": tetra["all_spin_one_F_rational"],
        },
        "global_body": {
            "status": final_report["status"],
            "simple_count": final_witness["simple_count"],
            "object_labels": final_witness["object_labels"],
            "pentagon_length_four_chain_count": final_witness[
                "pentagon_length_four_chain_count"
            ],
            "zigzag_failure_count": final_witness["zigzag_failure_count"],
        },
        "mog_k4_carrier": {
            "status": mog_resolvent["status"],
            "vertices_columns": tetra["tetrahedron_vertices_columns"],
            "vertices_labels": tetra["tetrahedron_vertices_labels"],
            "edge_column_pairs": tetra["tetrahedron_edge_column_pairs"],
            "edge_labels": tetra["tetrahedron_edge_labels"],
            "wu_radical_pair": mog_resolvent["wu_radical_as_mog_octad"][
                "radical_column_pair"
            ],
        },
        "boundary_readout": {
            "d20_boundary": "C(6,3)",
            "d20_boundary_face_count": comb(len(OBJECT_LABELS), 3),
            "symbolic_canonical_triple_count": symbolic_witness[
                "canonical_symbolic_triple_count"
            ],
            "normal_word_triple_count": symbolic_witness[
                "total_normal_word_triple_count"
            ],
        },
        "second_window_bottleneck": {
            "cut_edge_count": transfer_witness["surviving_cut_flow"][
                "cut_edge_count"
            ],
            "cut_flux_x1e12": transfer_witness["surviving_cut_flow"][
                "cut_flux_x1e12"
            ],
            "per_cut_edge_flux_x1e12": 170_677_590,
            "cut_centers_coincide": cut_centers_coincide,
            "cut_edge_ids": [
                row["transfer_edge_id"] for row in cut_csv_rows
            ],
        },
        "sector_frame_table_sha256": sha_array(sector_table),
        "mog_edge_table_sha256": sha_array(mog_table),
        "cut_edge_table_sha256": sha_array(cut_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    frame = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame@1",
        "object": "C985->d20",
        "parent": SECOND_WINDOW_TRANSFER_REPORT.relative_to(ROOT).as_posix(),
        "reading": {
            "local_law": "6j recoupling is the tetrahedral associator seed",
            "global_body": "C985 is the certified finite semisimple multi-fusion closure",
            "visible_boundary": "d20 is the C(6,3) boundary readout over the six H6 sectors",
            "current_bottleneck": "the second-window transfer operator still loads one six-edge aperture",
        },
        "abstract_sector_frame": sector_rows,
        "mog_k4_carrier": mog_rows,
        "cut_edge_overlay": cut_csv_rows,
        "compiler_pathway_note": (
            "This is a proof-obligation/readout artifact. It does not wire C985 "
            "into the normal lowered-scene JSON compiler pathway."
        ),
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_SIXJ_BOTTLENECK_FRAME_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The surviving second-window six-edge transfer bottleneck admits a "
            "certified 6j frame reading: the local scalar 6j/F anchors and the "
            "MOG support-nullspace K4 supply the tetrahedral carrier, the final "
            "C985 multi-fusion certificate supplies the global associator body, "
            "and the d20 C(6,3) layer supplies the visible 20-state boundary."
        ),
        "stage_protocol": {
            "draft": "collect certified second-window transfer, MOG 6j, symbolic associativity, and final C985 reports",
            "witness": "emit six cut-edge, abstract-sector, MOG-K4, and observable tables",
            "coherence": "check K4 edge counts, scalar anchors, C(6,3) boundary count, C985 coherence status, and cut-flow lineage",
            "closure": "certify the six-edge bottleneck as a 6j-framed readout, not as a new F-symbol table",
            "emit": "emit frame artifacts, certificate, report, verifier command, and next tetrahedral intervention target",
        },
        "inputs": {
            "second_window_transfer_report": input_entry(
                SECOND_WINDOW_TRANSFER_REPORT,
                {
                    "status": transfer_report.get("status"),
                    "certificate_sha256": transfer_report.get("certificate_sha256"),
                },
            ),
            "second_window_transfer_certificate": input_entry(
                SECOND_WINDOW_TRANSFER_CERTIFICATE
            ),
            "second_window_transfer_states": input_entry(
                SECOND_WINDOW_TRANSFER_STATES
            ),
            "second_window_transfer_edges": input_entry(SECOND_WINDOW_TRANSFER_EDGES),
            "second_window_transfer_centers": input_entry(
                SECOND_WINDOW_TRANSFER_CENTERS
            ),
            "second_window_transfer_tables": input_entry(
                SECOND_WINDOW_TRANSFER_TABLES
            ),
            "second_window_promotion_states": input_entry(
                SECOND_WINDOW_PROMOTION_STATES
            ),
            "final_multifusion_report": input_entry(
                FINAL_MULTIFUSION_REPORT,
                {
                    "status": final_report.get("status"),
                    "certificate_sha256": final_report.get("certificate_sha256"),
                },
            ),
            "symbolic_associativity_report": input_entry(
                SYMBOLIC_ASSOCIATIVITY_REPORT,
                {
                    "status": symbolic_report.get("status"),
                    "certificate_sha256": symbolic_report.get("certificate_sha256"),
                },
            ),
            "mog_resolvent": input_entry(
                MOG_RESOLVENT,
                {"status": mog_resolvent.get("status")},
            ),
            "wu_spinh_6j_marking": input_entry(
                WU_SPINH_6J_MARKING,
                {"status": wu_marking.get("status")},
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "sixj_frame": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame.json"
            ),
            "sixj_cut_edges_csv": relpath(OUT_DIR / "sixj_bottleneck_cut_edges.csv"),
            "sixj_abstract_sector_frame_csv": relpath(
                OUT_DIR / "sixj_abstract_sector_frame.csv"
            ),
            "sixj_mog_k4_edges_csv": relpath(OUT_DIR / "sixj_mog_k4_edges.csv"),
            "sixj_observables_csv": relpath(OUT_DIR / "sixj_frame_observables.csv"),
            "sixj_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame_tables.npz"
            ),
            "sixj_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the six surviving second-window transfer cut edges as a reproducible bottleneck overlay",
                "the abstract six-sector tetrahedron frame with C(6,2)=15 and C(6,3)=20 counts",
                "the certified MOG support-nullspace K4 6j carrier and scalar anchors 1/6 and 1/2",
                "the final C985 multi-fusion body as the global associator/coherence source for this reading",
            ],
            "does_not_certify_because_not_required": [
                "a complete numerical 6j/F-symbol table for C985",
                "a unique physical ordering of the six H6 sector labels on tetrahedron edges",
                "hydrogen spectral consequences of the scalar block",
                "MOG row-refined Golay selector completion beyond the existing obstruction boundary",
                "C985 integration into the normal lowered-scene JSON compiler pathway",
            ],
        },
        "next_highest_yield_item": (
            "Use the certified 6j frame to rank tetrahedral opposite-edge and "
            "edge-pair recoupling interventions, then test a K4-aware move "
            "that changes cut support rather than adding another local window "
            "onto the same six-edge aperture."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame_certificate@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "6j is the local tetrahedral associator seed",
            "C985 is the certified global finite multi-fusion body",
            "d20 is the C(6,3) visible boundary readout",
            "the current bottleneck is a six-edge aperture that should be attacked by K4-aware recoupling moves",
        ],
    }

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified transfer, C985 final, symbolic, MOG, and Wu/SpinH 6j reports",
            "materialize six cut edges and attach abstract sector and MOG K4 addresses",
            "check C(6,2), C(6,3), Spin12, scalar 6j/F, and K4 carrier counts",
            "check cut-flow lineage, uniform cut flux, and source/target side crossing",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "sixj_frame": frame,
        "sixj_cut_edges_csv": csv_text(
            [
                "frame_edge_id",
                "abstract_sector_label",
                "abstract_tetra_edge",
                "mog_edge_label",
                "transfer_edge_id",
                "source_state_id",
                "target_state_id",
                "undirected_stationary_flux_x1e12",
                "source_side_code",
                "target_side_code",
                "source_word_length",
                "target_word_length",
                "edit_prefix_length",
                "source_edit",
                "target_edit",
                "source_word",
                "target_word",
            ],
            cut_csv_rows,
        ),
        "sixj_abstract_sector_frame_csv": csv_text(
            [
                "sector_code",
                "sector_label",
                "axis",
                "polarity",
                "tetra_edge",
                "opposite_sector_label",
            ],
            sector_rows,
        ),
        "sixj_mog_k4_edges_csv": csv_text(
            [
                "frame_edge_id",
                "column_a",
                "column_b",
                "label_a",
                "label_b",
                "pair_octad_index",
                "big_cell_coordinate",
                "opposite_frame_edge_id",
                "wu_radical_edge_flag",
                "wu_radical_opposite_edge_flag",
            ],
            mog_rows,
        ),
        "sixj_observables_csv": csv_text(OBSERVABLE_COLUMNS, observable_rows),
        "sector_table": sector_table,
        "mog_table": mog_table,
        "cut_table": cut_table,
        "observable_table": observable_table,
        "sixj_certificate": certificate,
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
        / "signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame.json",
        payloads["sixj_frame"],
    )
    (OUT_DIR / "sixj_bottleneck_cut_edges.csv").write_text(
        payloads["sixj_cut_edges_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "sixj_abstract_sector_frame.csv").write_text(
        payloads["sixj_abstract_sector_frame_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "sixj_mog_k4_edges.csv").write_text(
        payloads["sixj_mog_k4_edges_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "sixj_frame_observables.csv").write_text(
        payloads["sixj_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame_tables.npz",
        sector_table=payloads["sector_table"],
        mog_table=payloads["mog_table"],
        cut_table=payloads["cut_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame_certificate.json",
        payloads["sixj_certificate"],
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
