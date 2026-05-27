from __future__ import annotations

import json
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_corridor_insertion import (
        INSERTED_SYMBOL_ID,
        OUT_DIR as APERTURE_INSERTION_DIR,
        SELECTED_INSERTION_POSITION,
    )
    from .derive_c985_d20_signature_boundary_spine_branching_law import (
        OUT_DIR as BRANCHING_LAW_DIR,
    )
    from .derive_c985_d20_signature_boundary_spine_routing_prefix import (
        read_int_csv,
        table_from_rows,
    )
    from .derive_c985_d20_signature_boundary_spine_typed_corridors import (
        OUT_DIR as TYPED_CORRIDOR_DIR,
    )
    from .derive_c985_d20_signature_boundary_spine_x2_detour_fan import (
        OUT_DIR as X2_DETOUR_DIR,
    )
    from .derive_c985_d20_symbolic_associativity import (
        OUT_DIR as SYMBOLIC_ASSOCIATIVITY_DIR,
    )
    from .derive_c985_d20_symbolic_rewrite_rules import csv_text
    from .derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_d20_signature_boundary_spine_aperture_corridor_insertion import (
        INSERTED_SYMBOL_ID,
        OUT_DIR as APERTURE_INSERTION_DIR,
        SELECTED_INSERTION_POSITION,
    )
    from derive_c985_d20_signature_boundary_spine_branching_law import (
        OUT_DIR as BRANCHING_LAW_DIR,
    )
    from derive_c985_d20_signature_boundary_spine_routing_prefix import (
        read_int_csv,
        table_from_rows,
    )
    from derive_c985_d20_signature_boundary_spine_typed_corridors import (
        OUT_DIR as TYPED_CORRIDOR_DIR,
    )
    from derive_c985_d20_signature_boundary_spine_x2_detour_fan import (
        OUT_DIR as X2_DETOUR_DIR,
    )
    from derive_c985_d20_symbolic_associativity import (
        OUT_DIR as SYMBOLIC_ASSOCIATIVITY_DIR,
    )
    from derive_c985_d20_symbolic_rewrite_rules import csv_text
    from derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "c985_d20_signature_boundary_spine_x2_clean_detour_choice"
STATUS = "C985_D20_SIGNATURE_BOUNDARY_SPINE_X2_CLEAN_DETOUR_CHOICE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

X2_DETOUR_REPORT = X2_DETOUR_DIR / "report.json"
X2_DETOUR_JSON = X2_DETOUR_DIR / "signature_boundary_spine_x2_detour_fan.json"
X2_DETOUR_RETURNS = X2_DETOUR_DIR / "x2_detour_return_paths.csv"
X2_DETOUR_TABLES = X2_DETOUR_DIR / "signature_boundary_spine_x2_detour_fan_tables.npz"
X2_DETOUR_CERTIFICATE = (
    X2_DETOUR_DIR / "signature_boundary_spine_x2_detour_fan_certificate.json"
)

TYPED_CORRIDOR_REPORT = TYPED_CORRIDOR_DIR / "report.json"
TYPED_CORRIDOR_EDGES = TYPED_CORRIDOR_DIR / "corridor_edge_symbols.csv"
TYPED_CORRIDOR_TABLES = (
    TYPED_CORRIDOR_DIR / "signature_boundary_spine_typed_corridors_tables.npz"
)
TYPED_CORRIDOR_CERTIFICATE = (
    TYPED_CORRIDOR_DIR / "signature_boundary_spine_typed_corridors_certificate.json"
)

BRANCHING_LAW_REPORT = BRANCHING_LAW_DIR / "report.json"
BRANCHING_LAW_CSV = BRANCHING_LAW_DIR / "negative_branch_order.csv"
BRANCHING_LAW_TABLES = (
    BRANCHING_LAW_DIR / "signature_boundary_spine_branching_law_tables.npz"
)
BRANCHING_LAW_CERTIFICATE = (
    BRANCHING_LAW_DIR / "signature_boundary_spine_branching_law_certificate.json"
)

APERTURE_INSERTION_REPORT = APERTURE_INSERTION_DIR / "report.json"
APERTURE_INSERTION_JSON = (
    APERTURE_INSERTION_DIR / "signature_boundary_spine_aperture_corridor_insertion.json"
)
APERTURE_INSERTION_WINDOWS = (
    APERTURE_INSERTION_DIR / "aperture_corridor_inserted_windows.csv"
)
APERTURE_INSERTION_SEQUENCE = (
    APERTURE_INSERTION_DIR / "aperture_corridor_selected_sequence.csv"
)
APERTURE_INSERTION_TABLES = (
    APERTURE_INSERTION_DIR
    / "signature_boundary_spine_aperture_corridor_insertion_tables.npz"
)
APERTURE_INSERTION_CERTIFICATE = (
    APERTURE_INSERTION_DIR
    / "signature_boundary_spine_aperture_corridor_insertion_certificate.json"
)

SYMBOLIC_ASSOCIATIVITY_REPORT = SYMBOLIC_ASSOCIATIVITY_DIR / "report.json"
SYMBOLIC_ASSOCIATIVITY_CSV = SYMBOLIC_ASSOCIATIVITY_DIR / "symbolic_associativity.csv"
SYMBOLIC_ASSOCIATIVITY_TABLES = (
    SYMBOLIC_ASSOCIATIVITY_DIR / "symbolic_associativity_tables.npz"
)
SYMBOLIC_ASSOCIATIVITY_CERTIFICATE = (
    SYMBOLIC_ASSOCIATIVITY_DIR / "symbolic_associativity_certificate.json"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_x2_clean_detour_choice.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_x2_clean_detour_choice.py"
)

SLOT_NEGATIVE_CARRIER_ID = 4
SLOT_POSITIVE_CARRIER_ID = 12
SLOT_SHARED_SYMBOL_ID = 3
SLOT_BOUNDARY_SPINE_RANK = 14
SLOT_BRANCH_ORDER_RANK = 6
SLOT_BOUNDARY_MASK_EDGE_ID = 4
X2_DETOUR_CELL_EDGE_ID = 14
X2_DETOUR_CARRIER_ID = 3
SELECTED_RETURN_CELL_EDGE_ID = 11
SELECTED_RETURN_NEGATIVE_CARRIER_ID = 8
FULL_SYMBOL_BITSET = (1 << 6) - 1

RETURN_CHOICE_COLUMNS = [
    "return_choice_id",
    "x2_cell_edge_id",
    "detour_carrier_mask_class_id",
    "return_cell_edge_id",
    "return_negative_carrier_mask_class_id",
    "return_shared_symbol_id",
    "return_shared_symbol_bitset",
    "matching_boundary_spine_rank",
    "matching_boundary_mask_edge_id",
    "matching_branch_order_rank",
    "matching_first_prefix_length",
    "spine_rank_rewind_from_slot",
    "branch_order_rewind_from_slot",
    "post_tail_position",
    "tail_contacts_preserved_count",
    "tail_order_disturbance_count",
    "immediate_tail_match_flag",
    "post_return_window_canonical_triple_id",
    "post_return_window_sector_coverage_count",
    "post_return_window_signature_union_count",
    "boundary_return_matches_existing_edge_flag",
    "clean_single_x2_return_flag",
    "least_disturbance_flag",
]

TAIL_SIMULATION_COLUMNS = [
    "return_choice_id",
    "tail_contact_position",
    "boundary_spine_rank",
    "boundary_mask_edge_id",
    "tail_negative_carrier_mask_class_id",
    "tail_shared_symbol_id",
    "tail_shared_symbol_bitset",
    "tail_matches_return_flag",
    "tail_preserved_after_return_flag",
    "tail_skipped_before_return_flag",
]

OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "clean_return_choice_count": 0,
    "least_disturbance_choice_count": 1,
    "selected_return_cell_edge_id": 2,
    "selected_return_negative_carrier_id": 3,
    "selected_return_shared_symbol_id": 4,
    "selected_tail_contacts_preserved_count": 5,
    "selected_tail_order_disturbance_count": 6,
    "selected_branch_order_rewind": 7,
    "selected_spine_rank_rewind": 8,
    "selected_post_return_signature_union": 9,
    "tail_contact_count_after_slot": 10,
    "slot_boundary_spine_rank": 11,
    "slot_branch_order_rank": 12,
    "x2_detour_cell_edge_id": 13,
    "x2_detour_carrier_id": 14,
}


def singleton_symbol_id(symbol_bitset: int) -> int:
    symbols = [symbol_id for symbol_id in range(6) if symbol_bitset & (1 << symbol_id)]
    if len(symbols) != 1:
        raise AssertionError(f"expected one shared symbol, got bitset {symbol_bitset}")
    return symbols[0]


def find_one(rows: list[dict[str, int]], label: str, **criteria: int) -> dict[str, int]:
    matches = [
        row
        for row in rows
        if all(int(row.get(key, -10**9)) == value for key, value in criteria.items())
    ]
    if len(matches) != 1:
        raise AssertionError(f"expected one {label}, found {len(matches)}")
    return matches[0]


def associativity_lookup(
    rows: list[dict[str, int]],
) -> dict[tuple[int, int, int], dict[str, int]]:
    lookup: dict[tuple[int, int, int], dict[str, int]] = {}
    for row in rows:
        key = (
            int(row["left_symbol_id"]),
            int(row["middle_symbol_id"]),
            int(row["right_symbol_id"]),
        )
        lookup[key] = row
    return lookup


def build_payloads() -> dict[str, Any]:
    detour_report = load_json(X2_DETOUR_REPORT)
    detour = load_json(X2_DETOUR_JSON)
    detour_certificate = load_json(X2_DETOUR_CERTIFICATE)
    typed_report = load_json(TYPED_CORRIDOR_REPORT)
    typed_certificate = load_json(TYPED_CORRIDOR_CERTIFICATE)
    branch_report = load_json(BRANCHING_LAW_REPORT)
    branch_certificate = load_json(BRANCHING_LAW_CERTIFICATE)
    insertion_report = load_json(APERTURE_INSERTION_REPORT)
    insertion = load_json(APERTURE_INSERTION_JSON)
    insertion_certificate = load_json(APERTURE_INSERTION_CERTIFICATE)
    associativity_report = load_json(SYMBOLIC_ASSOCIATIVITY_REPORT)
    associativity_certificate = load_json(SYMBOLIC_ASSOCIATIVITY_CERTIFICATE)

    detour_tables = np.load(X2_DETOUR_TABLES, allow_pickle=False)
    typed_tables = np.load(TYPED_CORRIDOR_TABLES, allow_pickle=False)
    branch_tables = np.load(BRANCHING_LAW_TABLES, allow_pickle=False)
    insertion_tables = np.load(APERTURE_INSERTION_TABLES, allow_pickle=False)
    associativity_tables = np.load(SYMBOLIC_ASSOCIATIVITY_TABLES, allow_pickle=False)

    detour_return_table = np.asarray(detour_tables["return_path_table"], dtype=np.int64)
    typed_edge_table = np.asarray(typed_tables["corridor_edge_table"], dtype=np.int64)
    branch_order_table = np.asarray(
        branch_tables["negative_branch_order_table"], dtype=np.int64
    )
    selected_sequence_table = np.asarray(
        insertion_tables["selected_sequence_table"], dtype=np.int64
    )
    associativity_table = np.asarray(
        associativity_tables["symbolic_associativity_table"], dtype=np.int64
    )

    return_rows = read_int_csv(X2_DETOUR_RETURNS)
    corridor_rows = read_int_csv(TYPED_CORRIDOR_EDGES)
    branch_rows = read_int_csv(BRANCHING_LAW_CSV)
    insertion_windows = read_int_csv(APERTURE_INSERTION_WINDOWS)
    selected_sequence_rows = read_int_csv(APERTURE_INSERTION_SEQUENCE)
    associativity_rows = read_int_csv(SYMBOLIC_ASSOCIATIVITY_CSV)
    associativity_by_word = associativity_lookup(associativity_rows)

    slot_row = find_one(
        corridor_rows,
        "selected insertion slot",
        boundary_spine_rank=SLOT_BOUNDARY_SPINE_RANK,
        boundary_mask_edge_id=SLOT_BOUNDARY_MASK_EDGE_ID,
        negative_carrier_mask_class_id=SLOT_NEGATIVE_CARRIER_ID,
        positive_carrier_mask_class_id=SLOT_POSITIVE_CARRIER_ID,
        shared_symbol_id=SLOT_SHARED_SYMBOL_ID,
    )
    clean_return_rows = [
        row for row in return_rows if int(row["clean_single_x2_return_flag"]) == 1
    ]
    clean_return_rows = sorted(
        clean_return_rows,
        key=lambda row: int(row["return_path_id"]),
    )
    tail_rows = sorted(
        [
            row
            for row in corridor_rows
            if int(row["boundary_spine_rank"]) > SLOT_BOUNDARY_SPINE_RANK
        ],
        key=lambda row: int(row["boundary_spine_rank"]),
    )
    tail_position_by_contact = {
        (
            int(row["negative_carrier_mask_class_id"]),
            int(row["shared_symbol_id"]),
        ): index + 1
        for index, row in enumerate(tail_rows)
    }

    branch_by_negative = {
        int(row["negative_carrier_mask_class_id"]): row for row in branch_rows
    }

    choice_rows: list[dict[str, int]] = []
    for return_choice_id, return_row in enumerate(clean_return_rows):
        return_symbol_bitset = int(return_row["return_shared_symbol_bitset"])
        return_symbol_id = singleton_symbol_id(return_symbol_bitset)
        return_negative_id = int(return_row["return_negative_carrier_mask_class_id"])
        matching_corridor = find_one(
            corridor_rows,
            "typed boundary return edge",
            negative_carrier_mask_class_id=return_negative_id,
            positive_carrier_mask_class_id=int(
                return_row["detour_carrier_mask_class_id"]
            ),
            shared_symbol_id=return_symbol_id,
        )
        branch_row = branch_by_negative[return_negative_id]
        post_tail_position = tail_position_by_contact.get(
            (return_negative_id, return_symbol_id),
            0,
        )
        tail_contacts_preserved_count = (
            len(tail_rows) - post_tail_position + 1 if post_tail_position else 0
        )
        tail_order_disturbance_count = (
            post_tail_position - 1 if post_tail_position else len(tail_rows)
        )
        post_return_window = associativity_by_word[
            (SLOT_SHARED_SYMBOL_ID, INSERTED_SYMBOL_ID, return_symbol_id)
        ]
        choice_rows.append(
            {
                "return_choice_id": return_choice_id,
                "x2_cell_edge_id": int(return_row["x2_cell_edge_id"]),
                "detour_carrier_mask_class_id": int(
                    return_row["detour_carrier_mask_class_id"]
                ),
                "return_cell_edge_id": int(return_row["return_cell_edge_id"]),
                "return_negative_carrier_mask_class_id": return_negative_id,
                "return_shared_symbol_id": return_symbol_id,
                "return_shared_symbol_bitset": return_symbol_bitset,
                "matching_boundary_spine_rank": int(
                    matching_corridor["boundary_spine_rank"]
                ),
                "matching_boundary_mask_edge_id": int(
                    matching_corridor["boundary_mask_edge_id"]
                ),
                "matching_branch_order_rank": int(branch_row["branch_order_rank"]),
                "matching_first_prefix_length": int(branch_row["first_prefix_length"]),
                "spine_rank_rewind_from_slot": SLOT_BOUNDARY_SPINE_RANK
                - int(matching_corridor["boundary_spine_rank"]),
                "branch_order_rewind_from_slot": SLOT_BRANCH_ORDER_RANK
                - int(branch_row["branch_order_rank"]),
                "post_tail_position": post_tail_position,
                "tail_contacts_preserved_count": tail_contacts_preserved_count,
                "tail_order_disturbance_count": tail_order_disturbance_count,
                "immediate_tail_match_flag": int(post_tail_position == 1),
                "post_return_window_canonical_triple_id": int(
                    post_return_window["canonical_triple_id"]
                ),
                "post_return_window_sector_coverage_count": int(
                    post_return_window["sector_coverage_count"]
                ),
                "post_return_window_signature_union_count": int(
                    post_return_window["signature_union_count"]
                ),
                "boundary_return_matches_existing_edge_flag": 1,
                "clean_single_x2_return_flag": int(
                    return_row["clean_single_x2_return_flag"]
                ),
                "least_disturbance_flag": 0,
            }
        )

    best_score = min(
        (
            int(row["tail_order_disturbance_count"]),
            int(row["branch_order_rewind_from_slot"]),
            int(row["spine_rank_rewind_from_slot"]),
            -int(row["post_return_window_signature_union_count"]),
        )
        for row in choice_rows
    )
    for row in choice_rows:
        score = (
            int(row["tail_order_disturbance_count"]),
            int(row["branch_order_rewind_from_slot"]),
            int(row["spine_rank_rewind_from_slot"]),
            -int(row["post_return_window_signature_union_count"]),
        )
        row["least_disturbance_flag"] = int(score == best_score)

    selected_choice = find_one(
        choice_rows,
        "least-disturbance return choice",
        least_disturbance_flag=1,
    )

    tail_simulation_rows: list[dict[str, int]] = []
    for choice in choice_rows:
        for tail_position, tail_row in enumerate(tail_rows, start=1):
            tail_matches_return = (
                int(tail_row["negative_carrier_mask_class_id"])
                == int(choice["return_negative_carrier_mask_class_id"])
                and int(tail_row["shared_symbol_id"])
                == int(choice["return_shared_symbol_id"])
            )
            tail_simulation_rows.append(
                {
                    "return_choice_id": int(choice["return_choice_id"]),
                    "tail_contact_position": tail_position,
                    "boundary_spine_rank": int(tail_row["boundary_spine_rank"]),
                    "boundary_mask_edge_id": int(tail_row["boundary_mask_edge_id"]),
                    "tail_negative_carrier_mask_class_id": int(
                        tail_row["negative_carrier_mask_class_id"]
                    ),
                    "tail_shared_symbol_id": int(tail_row["shared_symbol_id"]),
                    "tail_shared_symbol_bitset": int(tail_row["shared_symbol_bitset"]),
                    "tail_matches_return_flag": int(tail_matches_return),
                    "tail_preserved_after_return_flag": int(
                        tail_position >= int(choice["post_tail_position"])
                    ),
                    "tail_skipped_before_return_flag": int(
                        tail_position < int(choice["post_tail_position"])
                    ),
                }
            )

    observable_values = {
        "clean_return_choice_count": len(choice_rows),
        "least_disturbance_choice_count": sum(
            int(row["least_disturbance_flag"]) for row in choice_rows
        ),
        "selected_return_cell_edge_id": int(selected_choice["return_cell_edge_id"]),
        "selected_return_negative_carrier_id": int(
            selected_choice["return_negative_carrier_mask_class_id"]
        ),
        "selected_return_shared_symbol_id": int(
            selected_choice["return_shared_symbol_id"]
        ),
        "selected_tail_contacts_preserved_count": int(
            selected_choice["tail_contacts_preserved_count"]
        ),
        "selected_tail_order_disturbance_count": int(
            selected_choice["tail_order_disturbance_count"]
        ),
        "selected_branch_order_rewind": int(
            selected_choice["branch_order_rewind_from_slot"]
        ),
        "selected_spine_rank_rewind": int(
            selected_choice["spine_rank_rewind_from_slot"]
        ),
        "selected_post_return_signature_union": int(
            selected_choice["post_return_window_signature_union_count"]
        ),
        "tail_contact_count_after_slot": len(tail_rows),
        "slot_boundary_spine_rank": SLOT_BOUNDARY_SPINE_RANK,
        "slot_branch_order_rank": SLOT_BRANCH_ORDER_RANK,
        "x2_detour_cell_edge_id": X2_DETOUR_CELL_EDGE_ID,
        "x2_detour_carrier_id": X2_DETOUR_CARRIER_ID,
    }
    observable_rows = [
        {
            "observable_id": index,
            "observable_code": code,
            "value_x1e12": int(observable_values[name]),
            "aux_id": 0,
        }
        for index, (name, code) in enumerate(
            sorted(OBSERVABLE_CODES.items(), key=lambda item: item[1])
        )
    ]

    return_choice_table = table_from_rows(RETURN_CHOICE_COLUMNS, choice_rows)
    tail_simulation_table = table_from_rows(
        TAIL_SIMULATION_COLUMNS,
        tail_simulation_rows,
    )
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    selected_sequence = [
        int(row["gate_symbol_id"])
        for row in sorted(
            selected_sequence_rows,
            key=lambda row: int(row["edited_position"]),
        )
    ]
    selected_inserted_windows = [
        row
        for row in insertion_windows
        if int(row["candidate_id"]) == SELECTED_INSERTION_POSITION
    ]
    selected_terminal_window = find_one(
        selected_inserted_windows,
        "selected terminal x2 window",
        edited_window_id=13,
        canonical_triple_id=42,
        left_symbol_id=5,
        middle_symbol_id=SLOT_SHARED_SYMBOL_ID,
        right_symbol_id=INSERTED_SYMBOL_ID,
    )

    checks = {
        "x2_detour_report_certified": detour_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_X2_DETOUR_FAN_CERTIFIED",
        "x2_detour_certificate_certified": detour_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_X2_DETOUR_FAN_CERTIFIED",
        "typed_corridor_report_certified": typed_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_TYPED_CORRIDORS_CERTIFIED",
        "typed_corridor_certificate_certified": typed_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_TYPED_CORRIDORS_CERTIFIED",
        "branching_law_report_certified": branch_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_BRANCHING_LAW_CERTIFIED",
        "branching_law_certificate_certified": branch_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_BRANCHING_LAW_CERTIFIED",
        "aperture_insertion_report_certified": insertion_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CORRIDOR_INSERTION_CERTIFIED",
        "aperture_insertion_certificate_certified": insertion_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CORRIDOR_INSERTION_CERTIFIED",
        "symbolic_associativity_report_certified": associativity_report.get("status")
        == "C985_D20_SYMBOLIC_ASSOCIATIVITY_CERTIFIED",
        "symbolic_associativity_certificate_certified": associativity_certificate.get(
            "status"
        )
        == "C985_D20_SYMBOLIC_ASSOCIATIVITY_CERTIFIED",
        "x2_detour_schema_available": detour.get("schema")
        == "c985.d20_signature_boundary_spine_x2_detour_fan@1",
        "aperture_insertion_schema_available": insertion.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_corridor_insertion@1",
        "detour_return_table_shape_is_8_by_13": tuple(detour_return_table.shape)
        == (8, 13),
        "typed_edge_table_shape_is_16_by_23": tuple(typed_edge_table.shape)
        == (16, 23),
        "branch_order_table_shape_is_6_by_21": tuple(branch_order_table.shape)
        == (6, 21),
        "selected_sequence_table_shape_is_15_by_6": tuple(
            selected_sequence_table.shape
        )
        == (15, 6),
        "associativity_table_shape_is_216_by_27": tuple(associativity_table.shape)
        == (216, 27),
        "slot_row_is_rank_14_negative4_positive12_x3": (
            int(slot_row["boundary_spine_rank"]) == SLOT_BOUNDARY_SPINE_RANK
            and int(slot_row["negative_carrier_mask_class_id"])
            == SLOT_NEGATIVE_CARRIER_ID
            and int(slot_row["positive_carrier_mask_class_id"])
            == SLOT_POSITIVE_CARRIER_ID
            and int(slot_row["shared_symbol_id"]) == SLOT_SHARED_SYMBOL_ID
        ),
        "selected_sequence_ends_with_x5_x3_x2": selected_sequence[-3:] == [5, 3, 2],
        "selected_terminal_window_is_node42": int(
            selected_terminal_window["canonical_triple_id"]
        )
        == 42,
        "selected_terminal_window_signature_is_183": int(
            selected_terminal_window["signature_union_count"]
        )
        == 183,
        "clean_return_choice_count_is_2": len(choice_rows) == 2,
        "clean_return_choices_are_edges_10_11": [
            int(row["return_cell_edge_id"]) for row in choice_rows
        ]
        == [10, 11],
        "clean_return_choices_share_x2_edge_14": sorted(
            {int(row["x2_cell_edge_id"]) for row in choice_rows}
        )
        == [X2_DETOUR_CELL_EDGE_ID],
        "clean_return_choices_use_detour_carrier_3": sorted(
            {int(row["detour_carrier_mask_class_id"]) for row in choice_rows}
        )
        == [X2_DETOUR_CARRIER_ID],
        "clean_return_choices_are_to_negatives_7_8": [
            int(row["return_negative_carrier_mask_class_id"]) for row in choice_rows
        ]
        == [7, 8],
        "tail_order_after_slot_is_neg8_x1_then_neg7_x0": [
            [
                int(row["negative_carrier_mask_class_id"]),
                int(row["shared_symbol_id"]),
            ]
            for row in tail_rows
        ]
        == [[8, 1], [7, 0]],
        "all_choices_match_existing_typed_boundary_edges": all(
            int(row["boundary_return_matches_existing_edge_flag"]) == 1
            for row in choice_rows
        ),
        "least_disturbance_choice_unique": sum(
            int(row["least_disturbance_flag"]) for row in choice_rows
        )
        == 1,
        "least_disturbance_choice_is_return_edge_11": int(
            selected_choice["return_cell_edge_id"]
        )
        == SELECTED_RETURN_CELL_EDGE_ID,
        "least_disturbance_choice_returns_to_negative_8": int(
            selected_choice["return_negative_carrier_mask_class_id"]
        )
        == SELECTED_RETURN_NEGATIVE_CARRIER_ID,
        "least_disturbance_choice_uses_x1": int(
            selected_choice["return_shared_symbol_id"]
        )
        == 1,
        "least_disturbance_choice_preserves_two_tail_contacts": int(
            selected_choice["tail_contacts_preserved_count"]
        )
        == 2,
        "least_disturbance_choice_disturbs_zero_tail_contacts": int(
            selected_choice["tail_order_disturbance_count"]
        )
        == 0,
        "least_disturbance_choice_has_min_branch_rewind": int(
            selected_choice["branch_order_rewind_from_slot"]
        )
        == min(int(row["branch_order_rewind_from_slot"]) for row in choice_rows),
        "least_disturbance_choice_has_immediate_tail_match": int(
            selected_choice["immediate_tail_match_flag"]
        )
        == 1,
        "selected_post_return_window_is_3_2_1_canonical_27": int(
            selected_choice["post_return_window_canonical_triple_id"]
        )
        == 27,
        "selected_post_return_signature_is_146": int(
            selected_choice["post_return_window_signature_union_count"]
        )
        == 146,
        "alternative_return_edge_10_preserves_one_tail_contact": int(
            choice_rows[0]["tail_contacts_preserved_count"]
        )
        == 1,
        "alternative_return_edge_10_disturbs_one_tail_contact": int(
            choice_rows[0]["tail_order_disturbance_count"]
        )
        == 1,
        "return_choice_table_shape_is_2_by_23": tuple(return_choice_table.shape)
        == (2, len(RETURN_CHOICE_COLUMNS)),
        "tail_simulation_table_shape_is_4_by_10": tuple(tail_simulation_table.shape)
        == (4, len(TAIL_SIMULATION_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    witness = {
        "slot_context": {
            "boundary_spine_rank": SLOT_BOUNDARY_SPINE_RANK,
            "boundary_mask_edge_id": SLOT_BOUNDARY_MASK_EDGE_ID,
            "negative_carrier_id": SLOT_NEGATIVE_CARRIER_ID,
            "positive_carrier_id": SLOT_POSITIVE_CARRIER_ID,
            "shared_symbol_id": SLOT_SHARED_SYMBOL_ID,
            "selected_terminal_window": [5, SLOT_SHARED_SYMBOL_ID, INSERTED_SYMBOL_ID],
            "selected_terminal_canonical_triple_id": int(
                selected_terminal_window["canonical_triple_id"]
            ),
        },
        "clean_return_choices": [
            [
                int(row["x2_cell_edge_id"]),
                int(row["return_cell_edge_id"]),
                int(row["return_negative_carrier_mask_class_id"]),
                int(row["return_shared_symbol_id"]),
            ]
            for row in choice_rows
        ],
        "tail_order_after_slot": [
            [
                int(row["negative_carrier_mask_class_id"]),
                int(row["shared_symbol_id"]),
            ]
            for row in tail_rows
        ],
        "selected_return_choice_id": int(selected_choice["return_choice_id"]),
        "selected_return_path": [
            int(selected_choice["x2_cell_edge_id"]),
            int(selected_choice["return_cell_edge_id"]),
        ],
        "selected_return_negative_carrier_id": int(
            selected_choice["return_negative_carrier_mask_class_id"]
        ),
        "selected_return_shared_symbol_id": int(
            selected_choice["return_shared_symbol_id"]
        ),
        "selected_tail_contacts_preserved_count": int(
            selected_choice["tail_contacts_preserved_count"]
        ),
        "selected_tail_order_disturbance_count": int(
            selected_choice["tail_order_disturbance_count"]
        ),
        "selected_branch_order_rewind": int(
            selected_choice["branch_order_rewind_from_slot"]
        ),
        "selected_spine_rank_rewind": int(
            selected_choice["spine_rank_rewind_from_slot"]
        ),
        "post_return_windows": [
            {
                "return_negative_carrier_id": int(
                    row["return_negative_carrier_mask_class_id"]
                ),
                "ordered_symbols": [
                    SLOT_SHARED_SYMBOL_ID,
                    INSERTED_SYMBOL_ID,
                    int(row["return_shared_symbol_id"]),
                ],
                "canonical_triple_id": int(
                    row["post_return_window_canonical_triple_id"]
                ),
                "sector_coverage_count": int(
                    row["post_return_window_sector_coverage_count"]
                ),
                "signature_union_count": int(
                    row["post_return_window_signature_union_count"]
                ),
            }
            for row in choice_rows
        ],
        "return_choice_table_sha256": sha_array(return_choice_table),
        "tail_simulation_table_sha256": sha_array(tail_simulation_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    clean_choice = {
        "schema": "c985.d20_signature_boundary_spine_x2_clean_detour_choice@1",
        "object": "d20",
        "choice_rule": {
            "source": "certified x2 detour fan clean single-x2 return paths",
            "slot": "the selected virtual x2 insertion slot after boundary-spine rank 14",
            "scoring": (
                "minimize post-slot tail disturbance, then branch-order rewind, "
                "then spine-rank rewind, then prefer larger post-return signature"
            ),
            "closure": (
                "choose a clean return into the existing typed tail without claiming "
                "a new raw carrier boundary contact"
            ),
        },
        "slot_context": witness["slot_context"],
        "return_choices": choice_rows,
        "tail_simulation": tail_simulation_rows,
        "selected_return_choice_id": witness["selected_return_choice_id"],
        "selected_return_path": witness["selected_return_path"],
        "summary": {
            "clean_return_choice_count": len(choice_rows),
            "selected_return_cell_edge_id": int(
                selected_choice["return_cell_edge_id"]
            ),
            "selected_return_negative_carrier_id": int(
                selected_choice["return_negative_carrier_mask_class_id"]
            ),
            "selected_tail_contacts_preserved_count": int(
                selected_choice["tail_contacts_preserved_count"]
            ),
            "selected_tail_order_disturbance_count": int(
                selected_choice["tail_order_disturbance_count"]
            ),
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_x2_clean_detour_choice_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_X2_CLEAN_DETOUR_CHOICE_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the x2 detour fan has exactly two clean single-x2 return choices: edge 14 then edge 10, or edge 14 then edge 11",
            "edge 10 returns to negative carrier 7 through x0 but skips the immediate post-slot tail contact",
            "edge 11 returns to negative carrier 8 through x1 and preserves the full post-slot typed tail x1 then x0",
            "the selected edge-11 return also has the smaller branch-order rewind and the larger post-return symbolic signature",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_x2_clean_detour_choice@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The clean x2 detour through carrier 3 has a unique least-disturbing "
            "typed return: after x2 edge 14, return on carrier edge 11 to "
            "negative carrier 8 through x1, preserving the post-slot tail order."
        ),
        "stage_protocol": {
            "draft": "treat the two clean x2 detour returns as competing corridor continuations",
            "witness": "materialize their typed-boundary matches, tail-order effects, and post-return symbolic windows",
            "coherence": "score choices by tail preservation, branch-order rewind, spine-rank rewind, and symbolic signature",
            "closure": "certify the least-disturbing clean return without asserting an x4 aperture completion",
            "emit": "emit clean-detour-choice JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "x2_detour_report": input_entry(
                X2_DETOUR_REPORT,
                {
                    "status": detour_report.get("status"),
                    "certificate_sha256": detour_report.get("certificate_sha256"),
                },
            ),
            "x2_detour_fan": input_entry(X2_DETOUR_JSON),
            "x2_detour_returns": input_entry(X2_DETOUR_RETURNS),
            "x2_detour_tables": input_entry(X2_DETOUR_TABLES),
            "x2_detour_certificate": input_entry(X2_DETOUR_CERTIFICATE),
            "typed_corridor_report": input_entry(
                TYPED_CORRIDOR_REPORT,
                {
                    "status": typed_report.get("status"),
                    "certificate_sha256": typed_report.get("certificate_sha256"),
                },
            ),
            "typed_corridor_edges": input_entry(TYPED_CORRIDOR_EDGES),
            "typed_corridor_tables": input_entry(TYPED_CORRIDOR_TABLES),
            "typed_corridor_certificate": input_entry(TYPED_CORRIDOR_CERTIFICATE),
            "branching_law_report": input_entry(
                BRANCHING_LAW_REPORT,
                {
                    "status": branch_report.get("status"),
                    "certificate_sha256": branch_report.get("certificate_sha256"),
                },
            ),
            "branching_law_csv": input_entry(BRANCHING_LAW_CSV),
            "branching_law_tables": input_entry(BRANCHING_LAW_TABLES),
            "branching_law_certificate": input_entry(BRANCHING_LAW_CERTIFICATE),
            "aperture_insertion_report": input_entry(
                APERTURE_INSERTION_REPORT,
                {
                    "status": insertion_report.get("status"),
                    "certificate_sha256": insertion_report.get("certificate_sha256"),
                },
            ),
            "aperture_insertion": input_entry(APERTURE_INSERTION_JSON),
            "aperture_insertion_windows": input_entry(APERTURE_INSERTION_WINDOWS),
            "aperture_insertion_sequence": input_entry(APERTURE_INSERTION_SEQUENCE),
            "aperture_insertion_tables": input_entry(APERTURE_INSERTION_TABLES),
            "aperture_insertion_certificate": input_entry(
                APERTURE_INSERTION_CERTIFICATE
            ),
            "symbolic_associativity_report": input_entry(
                SYMBOLIC_ASSOCIATIVITY_REPORT,
                {
                    "status": associativity_report.get("status"),
                    "certificate_sha256": associativity_report.get(
                        "certificate_sha256"
                    ),
                },
            ),
            "symbolic_associativity_csv": input_entry(SYMBOLIC_ASSOCIATIVITY_CSV),
            "symbolic_associativity_tables": input_entry(
                SYMBOLIC_ASSOCIATIVITY_TABLES
            ),
            "symbolic_associativity_certificate": input_entry(
                SYMBOLIC_ASSOCIATIVITY_CERTIFICATE
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_x2_clean_detour_choice": relpath(
                OUT_DIR / "signature_boundary_spine_x2_clean_detour_choice.json"
            ),
            "x2_clean_detour_return_choices_csv": relpath(
                OUT_DIR / "x2_clean_detour_return_choices.csv"
            ),
            "x2_clean_detour_tail_simulation_csv": relpath(
                OUT_DIR / "x2_clean_detour_tail_simulation.csv"
            ),
            "x2_clean_detour_observables_csv": relpath(
                OUT_DIR / "x2_clean_detour_observables.csv"
            ),
            "signature_boundary_spine_x2_clean_detour_choice_tables": relpath(
                OUT_DIR / "signature_boundary_spine_x2_clean_detour_choice_tables.npz"
            ),
            "signature_boundary_spine_x2_clean_detour_choice_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_x2_clean_detour_choice_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the two clean return choices available after the carrier-3 x2 detour",
                "their typed boundary matches against the certified corridor table",
                "tail-order preservation and branch-order rewind for each choice",
                "the unique least-disturbing clean return through edge 11 to negative carrier 8",
            ],
            "does_not_certify_because_not_required": [
                "a raw positive/negative boundary x2 splice at the original slot",
                "that mixed x2/x5 detour returns are usable",
                "the subsequent x4 contact needed for aperture node 44",
                "global optimality among multi-step detours not enumerated in this finite choice layer",
            ],
        },
        "next_highest_yield_item": (
            "Search the selected clean continuation x2 then x1 for an x4 "
            "aperture completion: enumerate one- and two-step carrier contacts "
            "after the negative-8 return and either realize node 44 or certify "
            "the local x4 obstruction."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_x2_clean_detour_choice_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified x2-detour, aperture-insertion, typed-corridor, branch-law, and symbolic-associativity artifacts",
            "extract the two clean single-x2 return choices from the detour fan",
            "match each return against the typed boundary corridor and negative-branch order",
            "score each choice by post-slot tail preservation and rewind",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_x2_clean_detour_choice": clean_choice,
        "x2_clean_detour_return_choices_csv": csv_text(
            RETURN_CHOICE_COLUMNS,
            choice_rows,
        ),
        "x2_clean_detour_tail_simulation_csv": csv_text(
            TAIL_SIMULATION_COLUMNS,
            tail_simulation_rows,
        ),
        "x2_clean_detour_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "return_choice_table": return_choice_table,
        "tail_simulation_table": tail_simulation_table,
        "observable_table": observable_table,
        "signature_boundary_spine_x2_clean_detour_choice_certificate": certificate,
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
        OUT_DIR / "signature_boundary_spine_x2_clean_detour_choice.json",
        payloads["signature_boundary_spine_x2_clean_detour_choice"],
    )
    (OUT_DIR / "x2_clean_detour_return_choices.csv").write_text(
        payloads["x2_clean_detour_return_choices_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "x2_clean_detour_tail_simulation.csv").write_text(
        payloads["x2_clean_detour_tail_simulation_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "x2_clean_detour_observables.csv").write_text(
        payloads["x2_clean_detour_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_boundary_spine_x2_clean_detour_choice_tables.npz",
        return_choice_table=payloads["return_choice_table"],
        tail_simulation_table=payloads["tail_simulation_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR / "signature_boundary_spine_x2_clean_detour_choice_certificate.json",
        payloads["signature_boundary_spine_x2_clean_detour_choice_certificate"],
    )
    write_json(OUT_DIR / "report.json", payloads["report"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    update_index(payloads["report"])


def main() -> None:
    payloads = build_payloads()
    write_payloads(payloads)
    witness = payloads["report"]["witness"]
    print(
        json.dumps(
            {
                "status": payloads["report"]["status"],
                "all_checks_pass": payloads["report"]["all_checks_pass"],
                "report": relpath(OUT_DIR / "report.json"),
                "manifest": relpath(OUT_DIR / "manifest.json"),
                "certificate_sha256": payloads["report"]["certificate_sha256"],
                "selected_return_path": witness["selected_return_path"],
                "selected_return_negative_carrier_id": witness[
                    "selected_return_negative_carrier_id"
                ],
                "selected_tail_contacts_preserved_count": witness[
                    "selected_tail_contacts_preserved_count"
                ],
                "selected_tail_order_disturbance_count": witness[
                    "selected_tail_order_disturbance_count"
                ],
                "next_highest_yield_item": payloads["report"][
                    "next_highest_yield_item"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
