from __future__ import annotations

import json
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_routing_prefix import (
        bitset,
        popcount,
        read_int_csv,
        table_from_rows,
    )
    from .derive_c985_d20_signature_boundary_spine_typed_corridors import (
        OUT_DIR as TYPED_CORRIDOR_DIR,
        RESIDUAL_CHART_CARRIER_CSV,
        SYMBOLIC_ALPHABET_CSV,
    )
    from .derive_c985_d20_signature_boundary_spine_x2_clean_detour_choice import (
        OUT_DIR as CLEAN_DETOUR_DIR,
    )
    from .derive_c985_d20_signature_residual_cell_complex import (
        OUT_DIR as CELL_COMPLEX_DIR,
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
    from derive_c985_d20_signature_boundary_spine_routing_prefix import (
        bitset,
        popcount,
        read_int_csv,
        table_from_rows,
    )
    from derive_c985_d20_signature_boundary_spine_typed_corridors import (
        OUT_DIR as TYPED_CORRIDOR_DIR,
        RESIDUAL_CHART_CARRIER_CSV,
        SYMBOLIC_ALPHABET_CSV,
    )
    from derive_c985_d20_signature_boundary_spine_x2_clean_detour_choice import (
        OUT_DIR as CLEAN_DETOUR_DIR,
    )
    from derive_c985_d20_signature_residual_cell_complex import (
        OUT_DIR as CELL_COMPLEX_DIR,
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


THEOREM_ID = "c985_d20_signature_boundary_spine_x2_x4_aperture_completion"
STATUS = "C985_D20_SIGNATURE_BOUNDARY_SPINE_X2_X4_APERTURE_COMPLETION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

CLEAN_DETOUR_REPORT = CLEAN_DETOUR_DIR / "report.json"
CLEAN_DETOUR_JSON = (
    CLEAN_DETOUR_DIR / "signature_boundary_spine_x2_clean_detour_choice.json"
)
CLEAN_DETOUR_CHOICES = CLEAN_DETOUR_DIR / "x2_clean_detour_return_choices.csv"
CLEAN_DETOUR_TABLES = (
    CLEAN_DETOUR_DIR / "signature_boundary_spine_x2_clean_detour_choice_tables.npz"
)
CLEAN_DETOUR_CERTIFICATE = (
    CLEAN_DETOUR_DIR
    / "signature_boundary_spine_x2_clean_detour_choice_certificate.json"
)

CELL_COMPLEX_REPORT = CELL_COMPLEX_DIR / "report.json"
CELL_COMPLEX_JSON = CELL_COMPLEX_DIR / "signature_residual_cell_complex.json"
CELL_COMPLEX_EDGES = CELL_COMPLEX_DIR / "carrier_region_edges.csv"
CELL_COMPLEX_TABLES = CELL_COMPLEX_DIR / "signature_residual_cell_complex_tables.npz"
CELL_COMPLEX_CERTIFICATE = CELL_COMPLEX_DIR / "signature_residual_cell_complex_certificate.json"

TYPED_CORRIDOR_REPORT = TYPED_CORRIDOR_DIR / "report.json"
TYPED_CORRIDOR_EDGES = TYPED_CORRIDOR_DIR / "corridor_edge_symbols.csv"
TYPED_CORRIDOR_TABLES = (
    TYPED_CORRIDOR_DIR / "signature_boundary_spine_typed_corridors_tables.npz"
)
TYPED_CORRIDOR_CERTIFICATE = (
    TYPED_CORRIDOR_DIR / "signature_boundary_spine_typed_corridors_certificate.json"
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
    / "derive_c985_d20_signature_boundary_spine_x2_x4_aperture_completion.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_x2_x4_aperture_completion.py"
)

ORIGIN_POSITIVE_CARRIER_ID = 12
X2_DETOUR_CARRIER_ID = 3
SELECTED_RETURN_NEGATIVE_CARRIER_ID = 8
NEGATIVE_13_CARRIER_ID = 13
SELECTED_X2_EDGE_ID = 14
SELECTED_X1_RETURN_EDGE_ID = 11
SELECTED_X4_FIRST_EDGE_ID = 33
SELECTED_X5_RETURN_EDGE_ID = 43
INSERTED_X2_SYMBOL_ID = 2
APERTURE_X4_SYMBOL_ID = 4
APERTURE_X5_SYMBOL_ID = 5
APERTURE_NODE_ID = 44
APERTURE_SIGNATURE_UNION_COUNT = 185
SLOT_BOUNDARY_SPINE_RANK = 14

X4_FIRST_EDGE_COLUMNS = [
    "x4_first_edge_id",
    "cell_edge_id",
    "source_carrier_mask_class_id",
    "target_carrier_mask_class_id",
    "x4_target_carrier_mask_class_id",
    "edge_partition_code",
    "is_positive_negative_boundary",
    "shared_atom_bitset",
    "shared_symbol_bitset",
    "shared_symbol_count",
    "pure_x4_flag",
    "mixed_x3_x4_flag",
    "direct_boundary_completion_flag",
    "one_step_boundary_return_count",
]

APERTURE_COMPLETION_PATH_COLUMNS = [
    "completion_path_id",
    "first_cell_edge_id",
    "x4_target_carrier_mask_class_id",
    "return_cell_edge_id",
    "return_positive_carrier_mask_class_id",
    "return_negative_carrier_mask_class_id",
    "first_shared_symbol_bitset",
    "first_shared_symbol_count",
    "return_shared_symbol_id",
    "return_shared_symbol_bitset",
    "matching_boundary_spine_rank",
    "matching_boundary_mask_edge_id",
    "matching_branch_order_rank",
    "spine_rank_rewind_from_slot",
    "origin_positive_return_flag",
    "node44_aperture_completion_flag",
    "aperture_canonical_triple_id",
    "aperture_sector_coverage_count",
    "aperture_signature_union_count",
    "selected_origin_returning_completion_flag",
]

OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "incident_x4_edge_count": 0,
    "direct_boundary_x4_edge_count": 1,
    "two_step_boundary_return_count": 2,
    "node44_completion_count": 3,
    "origin_returning_completion_count": 4,
    "selected_x4_first_edge_id": 5,
    "selected_x5_return_edge_id": 6,
    "aperture_canonical_triple_id": 7,
    "aperture_signature_union_count": 8,
    "completion_cycle_edge_count": 9,
    "completion_cycle_symbol_count": 10,
}


def carrier_atom_ids(row: dict[str, int]) -> list[int]:
    return [
        int(row[f"carrier_atom_id_{index}"])
        for index in range(4)
        if int(row[f"carrier_atom_id_{index}"]) >= 0
    ]


def shared_symbol_ids(edge: dict[str, int], atom_to_symbol: dict[int, int]) -> list[int]:
    shared_atom_bitset = int(edge["source_carrier_atom_mask"]) & int(
        edge["target_carrier_atom_mask"]
    )
    return sorted(
        {
            atom_to_symbol[atom_id]
            for atom_id in range(64)
            if shared_atom_bitset & (1 << atom_id)
        }
    )


def singleton_symbol_id(symbol_bitset: int) -> int:
    symbols = [symbol_id for symbol_id in range(6) if symbol_bitset & (1 << symbol_id)]
    if len(symbols) != 1:
        raise AssertionError(f"expected one shared symbol, got bitset {symbol_bitset}")
    return symbols[0]


def edge_other(edge: dict[str, int], carrier_id: int) -> int:
    source = int(edge["source_carrier_mask_class_id"])
    target = int(edge["target_carrier_mask_class_id"])
    if source == carrier_id:
        return target
    if target == carrier_id:
        return source
    raise AssertionError(f"edge {edge['cell_edge_id']} is not incident to {carrier_id}")


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
        lookup[
            (
                int(row["left_symbol_id"]),
                int(row["middle_symbol_id"]),
                int(row["right_symbol_id"]),
            )
        ] = row
    return lookup


def positive_negative_ids(
    edge: dict[str, int],
    carrier_rows: dict[int, dict[str, int]],
) -> tuple[int, int]:
    source = int(edge["source_carrier_mask_class_id"])
    target = int(edge["target_carrier_mask_class_id"])
    source_sign = int(carrier_rows[source]["nodal_sign"])
    target_sign = int(carrier_rows[target]["nodal_sign"])
    if source_sign > 0 and target_sign < 0:
        return source, target
    if target_sign > 0 and source_sign < 0:
        return target, source
    raise AssertionError(f"edge {edge['cell_edge_id']} is not positive/negative")


def build_payloads() -> dict[str, Any]:
    clean_report = load_json(CLEAN_DETOUR_REPORT)
    clean_choice = load_json(CLEAN_DETOUR_JSON)
    clean_certificate = load_json(CLEAN_DETOUR_CERTIFICATE)
    cell_report = load_json(CELL_COMPLEX_REPORT)
    cell_complex = load_json(CELL_COMPLEX_JSON)
    cell_certificate = load_json(CELL_COMPLEX_CERTIFICATE)
    typed_report = load_json(TYPED_CORRIDOR_REPORT)
    typed_certificate = load_json(TYPED_CORRIDOR_CERTIFICATE)
    associativity_report = load_json(SYMBOLIC_ASSOCIATIVITY_REPORT)
    associativity_certificate = load_json(SYMBOLIC_ASSOCIATIVITY_CERTIFICATE)

    clean_tables = np.load(CLEAN_DETOUR_TABLES, allow_pickle=False)
    cell_tables = np.load(CELL_COMPLEX_TABLES, allow_pickle=False)
    typed_tables = np.load(TYPED_CORRIDOR_TABLES, allow_pickle=False)
    associativity_tables = np.load(SYMBOLIC_ASSOCIATIVITY_TABLES, allow_pickle=False)

    clean_choice_table = np.asarray(clean_tables["return_choice_table"], dtype=np.int64)
    cell_edge_table = np.asarray(cell_tables["carrier_region_edge_table"], dtype=np.int64)
    typed_edge_table = np.asarray(typed_tables["corridor_edge_table"], dtype=np.int64)
    associativity_table = np.asarray(
        associativity_tables["symbolic_associativity_table"], dtype=np.int64
    )

    clean_choice_rows = read_int_csv(CLEAN_DETOUR_CHOICES)
    cell_edge_rows = read_int_csv(CELL_COMPLEX_EDGES)
    corridor_rows = read_int_csv(TYPED_CORRIDOR_EDGES)
    associativity_rows = read_int_csv(SYMBOLIC_ASSOCIATIVITY_CSV)
    carrier_rows = {
        int(row["carrier_mask_class_id"]): row
        for row in read_int_csv(RESIDUAL_CHART_CARRIER_CSV)
    }
    atom_to_symbol = {
        int(row["atom_id"]): int(row["symbol_id"])
        for row in read_int_csv(SYMBOLIC_ALPHABET_CSV)
    }
    associativity_by_word = associativity_lookup(associativity_rows)

    edge_by_id = {int(row["cell_edge_id"]): row for row in cell_edge_rows}
    adjacency: dict[int, list[dict[str, int]]] = {}
    for row in cell_edge_rows:
        adjacency.setdefault(int(row["source_carrier_mask_class_id"]), []).append(row)
        adjacency.setdefault(int(row["target_carrier_mask_class_id"]), []).append(row)

    selected_clean_choice = find_one(
        clean_choice_rows,
        "selected clean detour choice",
        least_disturbance_flag=1,
        return_negative_carrier_mask_class_id=SELECTED_RETURN_NEGATIVE_CARRIER_ID,
        return_cell_edge_id=SELECTED_X1_RETURN_EDGE_ID,
    )

    x4_edges = [
        row
        for row in adjacency[SELECTED_RETURN_NEGATIVE_CARRIER_ID]
        if APERTURE_X4_SYMBOL_ID in shared_symbol_ids(row, atom_to_symbol)
    ]
    x4_edges = sorted(x4_edges, key=lambda row: int(row["cell_edge_id"]))

    first_edge_rows: list[dict[str, int]] = []
    completion_rows: list[dict[str, int]] = []
    for x4_first_edge_id, edge in enumerate(x4_edges):
        target = edge_other(edge, SELECTED_RETURN_NEGATIVE_CARRIER_ID)
        shared_atom_bitset = int(edge["source_carrier_atom_mask"]) & int(
            edge["target_carrier_atom_mask"]
        )
        first_symbols = shared_symbol_ids(edge, atom_to_symbol)
        first_symbol_bitset = bitset(first_symbols)
        boundary_returns = [
            candidate
            for candidate in adjacency[target]
            if int(candidate["cell_edge_id"]) != int(edge["cell_edge_id"])
            and int(candidate["is_positive_negative_boundary"]) == 1
        ]
        boundary_returns = sorted(
            boundary_returns,
            key=lambda row: int(row["cell_edge_id"]),
        )
        first_edge_rows.append(
            {
                "x4_first_edge_id": x4_first_edge_id,
                "cell_edge_id": int(edge["cell_edge_id"]),
                "source_carrier_mask_class_id": int(
                    edge["source_carrier_mask_class_id"]
                ),
                "target_carrier_mask_class_id": int(
                    edge["target_carrier_mask_class_id"]
                ),
                "x4_target_carrier_mask_class_id": target,
                "edge_partition_code": int(edge["edge_partition_code"]),
                "is_positive_negative_boundary": int(
                    edge["is_positive_negative_boundary"]
                ),
                "shared_atom_bitset": shared_atom_bitset,
                "shared_symbol_bitset": first_symbol_bitset,
                "shared_symbol_count": popcount(first_symbol_bitset),
                "pure_x4_flag": int(first_symbols == [APERTURE_X4_SYMBOL_ID]),
                "mixed_x3_x4_flag": int(first_symbols == [3, APERTURE_X4_SYMBOL_ID]),
                "direct_boundary_completion_flag": int(
                    int(edge["is_positive_negative_boundary"]) == 1
                ),
                "one_step_boundary_return_count": len(boundary_returns),
            }
        )

        for return_edge in boundary_returns:
            positive_id, negative_id = positive_negative_ids(return_edge, carrier_rows)
            return_symbols = shared_symbol_ids(return_edge, atom_to_symbol)
            return_symbol_bitset = bitset(return_symbols)
            return_symbol_id = singleton_symbol_id(return_symbol_bitset)
            matching_corridor = find_one(
                corridor_rows,
                "typed boundary return",
                negative_carrier_mask_class_id=negative_id,
                positive_carrier_mask_class_id=positive_id,
                shared_symbol_id=return_symbol_id,
            )
            aperture_window = associativity_by_word[
                (
                    INSERTED_X2_SYMBOL_ID,
                    APERTURE_X4_SYMBOL_ID,
                    return_symbol_id,
                )
            ]
            node44_flag = int(
                int(aperture_window["canonical_triple_id"]) == APERTURE_NODE_ID
            )
            completion_rows.append(
                {
                    "completion_path_id": len(completion_rows),
                    "first_cell_edge_id": int(edge["cell_edge_id"]),
                    "x4_target_carrier_mask_class_id": target,
                    "return_cell_edge_id": int(return_edge["cell_edge_id"]),
                    "return_positive_carrier_mask_class_id": positive_id,
                    "return_negative_carrier_mask_class_id": negative_id,
                    "first_shared_symbol_bitset": first_symbol_bitset,
                    "first_shared_symbol_count": popcount(first_symbol_bitset),
                    "return_shared_symbol_id": return_symbol_id,
                    "return_shared_symbol_bitset": return_symbol_bitset,
                    "matching_boundary_spine_rank": int(
                        matching_corridor["boundary_spine_rank"]
                    ),
                    "matching_boundary_mask_edge_id": int(
                        matching_corridor["boundary_mask_edge_id"]
                    ),
                    "matching_branch_order_rank": int(
                        matching_corridor["negative_branch_order_rank"]
                    ),
                    "spine_rank_rewind_from_slot": SLOT_BOUNDARY_SPINE_RANK
                    - int(matching_corridor["boundary_spine_rank"]),
                    "origin_positive_return_flag": int(
                        positive_id == ORIGIN_POSITIVE_CARRIER_ID
                    ),
                    "node44_aperture_completion_flag": node44_flag,
                    "aperture_canonical_triple_id": int(
                        aperture_window["canonical_triple_id"]
                    ),
                    "aperture_sector_coverage_count": int(
                        aperture_window["sector_coverage_count"]
                    ),
                    "aperture_signature_union_count": int(
                        aperture_window["signature_union_count"]
                    ),
                    "selected_origin_returning_completion_flag": int(
                        int(edge["cell_edge_id"]) == SELECTED_X4_FIRST_EDGE_ID
                        and int(return_edge["cell_edge_id"])
                        == SELECTED_X5_RETURN_EDGE_ID
                        and node44_flag == 1
                        and positive_id == ORIGIN_POSITIVE_CARRIER_ID
                    ),
                }
            )

    selected_completion = find_one(
        completion_rows,
        "selected origin-returning aperture completion",
        selected_origin_returning_completion_flag=1,
    )
    node44_completion_rows = [
        row for row in completion_rows if int(row["node44_aperture_completion_flag"]) == 1
    ]

    observable_values = {
        "incident_x4_edge_count": len(first_edge_rows),
        "direct_boundary_x4_edge_count": sum(
            int(row["direct_boundary_completion_flag"]) for row in first_edge_rows
        ),
        "two_step_boundary_return_count": len(completion_rows),
        "node44_completion_count": len(node44_completion_rows),
        "origin_returning_completion_count": sum(
            int(row["selected_origin_returning_completion_flag"])
            for row in completion_rows
        ),
        "selected_x4_first_edge_id": SELECTED_X4_FIRST_EDGE_ID,
        "selected_x5_return_edge_id": SELECTED_X5_RETURN_EDGE_ID,
        "aperture_canonical_triple_id": APERTURE_NODE_ID,
        "aperture_signature_union_count": APERTURE_SIGNATURE_UNION_COUNT,
        "completion_cycle_edge_count": 4,
        "completion_cycle_symbol_count": 4,
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

    x4_first_edge_table = table_from_rows(X4_FIRST_EDGE_COLUMNS, first_edge_rows)
    aperture_completion_path_table = table_from_rows(
        APERTURE_COMPLETION_PATH_COLUMNS,
        completion_rows,
    )
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    completion_cycle = {
        "carrier_ids": [
            ORIGIN_POSITIVE_CARRIER_ID,
            X2_DETOUR_CARRIER_ID,
            SELECTED_RETURN_NEGATIVE_CARRIER_ID,
            NEGATIVE_13_CARRIER_ID,
            ORIGIN_POSITIVE_CARRIER_ID,
        ],
        "cell_edge_ids": [
            SELECTED_X2_EDGE_ID,
            SELECTED_X1_RETURN_EDGE_ID,
            SELECTED_X4_FIRST_EDGE_ID,
            SELECTED_X5_RETURN_EDGE_ID,
        ],
        "symbol_ids": [
            INSERTED_X2_SYMBOL_ID,
            1,
            APERTURE_X4_SYMBOL_ID,
            APERTURE_X5_SYMBOL_ID,
        ],
    }

    checks = {
        "clean_detour_report_certified": clean_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_X2_CLEAN_DETOUR_CHOICE_CERTIFIED",
        "clean_detour_certificate_certified": clean_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_X2_CLEAN_DETOUR_CHOICE_CERTIFIED",
        "cell_complex_report_certified": cell_report.get("status")
        == "C985_D20_SIGNATURE_RESIDUAL_CELL_COMPLEX_CERTIFIED",
        "cell_complex_certificate_certified": cell_certificate.get("status")
        == "C985_D20_SIGNATURE_RESIDUAL_CELL_COMPLEX_CERTIFIED",
        "typed_corridor_report_certified": typed_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_TYPED_CORRIDORS_CERTIFIED",
        "typed_corridor_certificate_certified": typed_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_TYPED_CORRIDORS_CERTIFIED",
        "symbolic_associativity_report_certified": associativity_report.get("status")
        == "C985_D20_SYMBOLIC_ASSOCIATIVITY_CERTIFIED",
        "symbolic_associativity_certificate_certified": associativity_certificate.get(
            "status"
        )
        == "C985_D20_SYMBOLIC_ASSOCIATIVITY_CERTIFIED",
        "clean_detour_schema_available": clean_choice.get("schema")
        == "c985.d20_signature_boundary_spine_x2_clean_detour_choice@1",
        "cell_complex_schema_available": cell_complex.get("schema")
        == "c985.d20_signature_residual_cell_complex@1",
        "clean_choice_table_shape_is_2_by_23": tuple(clean_choice_table.shape)
        == (2, 23),
        "cell_complex_edge_table_shape_is_44_by_13": tuple(cell_edge_table.shape)
        == (44, 13),
        "typed_edge_table_shape_is_16_by_23": tuple(typed_edge_table.shape)
        == (16, 23),
        "associativity_table_shape_is_216_by_27": tuple(associativity_table.shape)
        == (216, 27),
        "selected_clean_choice_is_x2_edge14_return_edge11": [
            int(selected_clean_choice["x2_cell_edge_id"]),
            int(selected_clean_choice["return_cell_edge_id"]),
        ]
        == [SELECTED_X2_EDGE_ID, SELECTED_X1_RETURN_EDGE_ID],
        "selected_clean_choice_returns_to_negative8_x1": [
            int(selected_clean_choice["return_negative_carrier_mask_class_id"]),
            int(selected_clean_choice["return_shared_symbol_id"]),
        ]
        == [SELECTED_RETURN_NEGATIVE_CARRIER_ID, 1],
        "incident_x4_edges_from_negative8_match_expected": [
            int(row["cell_edge_id"]) for row in first_edge_rows
        ]
        == [21, 24, 27, 33],
        "all_incident_x4_edges_are_internal": all(
            int(row["direct_boundary_completion_flag"]) == 0
            for row in first_edge_rows
        ),
        "direct_boundary_x4_completion_count_is_zero": observable_values[
            "direct_boundary_x4_edge_count"
        ]
        == 0,
        "x4_edge33_targets_negative13": int(
            find_one(first_edge_rows, "edge33 first x4 contact", cell_edge_id=33)[
                "x4_target_carrier_mask_class_id"
            ]
        )
        == NEGATIVE_13_CARRIER_ID,
        "two_step_boundary_return_count_is_8": len(completion_rows) == 8,
        "node44_completion_count_is_3": len(node44_completion_rows) == 3,
        "node44_completions_are_edge33_then_x5_returns": [
            [int(row["first_cell_edge_id"]), int(row["return_cell_edge_id"])]
            for row in node44_completion_rows
        ]
        == [[33, 40], [33, 42], [33, 43]],
        "origin_returning_completion_unique": sum(
            int(row["selected_origin_returning_completion_flag"])
            for row in completion_rows
        )
        == 1,
        "selected_completion_is_edge33_then_edge43": [
            int(selected_completion["first_cell_edge_id"]),
            int(selected_completion["return_cell_edge_id"]),
        ]
        == [SELECTED_X4_FIRST_EDGE_ID, SELECTED_X5_RETURN_EDGE_ID],
        "selected_completion_returns_to_origin_positive12": int(
            selected_completion["return_positive_carrier_mask_class_id"]
        )
        == ORIGIN_POSITIVE_CARRIER_ID,
        "selected_completion_realizes_node44": int(
            selected_completion["node44_aperture_completion_flag"]
        )
        == 1,
        "aperture_word_x2_x4_x5_is_node44": int(
            selected_completion["aperture_canonical_triple_id"]
        )
        == APERTURE_NODE_ID,
        "aperture_signature_is_185": int(
            selected_completion["aperture_signature_union_count"]
        )
        == APERTURE_SIGNATURE_UNION_COUNT,
        "completion_cycle_edges_match_expected": completion_cycle["cell_edge_ids"]
        == [14, 11, 33, 43],
        "completion_cycle_symbols_match_expected": completion_cycle["symbol_ids"]
        == [2, 1, 4, 5],
        "x4_first_edge_table_shape_is_4_by_14": tuple(x4_first_edge_table.shape)
        == (4, len(X4_FIRST_EDGE_COLUMNS)),
        "aperture_completion_path_table_shape_is_8_by_20": tuple(
            aperture_completion_path_table.shape
        )
        == (8, len(APERTURE_COMPLETION_PATH_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    witness = {
        "selected_clean_return_path": [SELECTED_X2_EDGE_ID, SELECTED_X1_RETURN_EDGE_ID],
        "post_return_carrier_id": SELECTED_RETURN_NEGATIVE_CARRIER_ID,
        "incident_x4_edge_ids": [
            int(row["cell_edge_id"]) for row in first_edge_rows
        ],
        "direct_boundary_x4_edge_count": observable_values[
            "direct_boundary_x4_edge_count"
        ],
        "two_step_boundary_return_count": len(completion_rows),
        "node44_completion_paths": [
            [int(row["first_cell_edge_id"]), int(row["return_cell_edge_id"])]
            for row in node44_completion_rows
        ],
        "selected_origin_returning_completion": [
            int(selected_completion["first_cell_edge_id"]),
            int(selected_completion["return_cell_edge_id"]),
        ],
        "selected_completion_positive_return_carrier_id": int(
            selected_completion["return_positive_carrier_mask_class_id"]
        ),
        "aperture_word": [
            INSERTED_X2_SYMBOL_ID,
            APERTURE_X4_SYMBOL_ID,
            APERTURE_X5_SYMBOL_ID,
        ],
        "aperture_canonical_triple_id": APERTURE_NODE_ID,
        "aperture_signature_union_count": APERTURE_SIGNATURE_UNION_COUNT,
        "completion_cycle": completion_cycle,
        "x4_first_edge_table_sha256": sha_array(x4_first_edge_table),
        "aperture_completion_path_table_sha256": sha_array(
            aperture_completion_path_table
        ),
        "observable_table_sha256": sha_array(observable_table),
    }

    completion = {
        "schema": "c985.d20_signature_boundary_spine_x2_x4_aperture_completion@1",
        "object": "d20",
        "completion_rule": {
            "source": "certified least-disturbing clean x2 return to negative carrier 8",
            "search": "enumerate x4 carrier contacts incident to carrier 8 and one-step positive/negative boundary returns from their targets",
            "direct_boundary_result": "no incident x4 edge from carrier 8 is a positive/negative boundary contact",
            "two_step_result": "carrier 8 reaches carrier 13 by a pure x4 internal edge, and carrier 13 has x5 boundary returns realizing node 44",
        },
        "x4_first_edges": first_edge_rows,
        "aperture_completion_paths": completion_rows,
        "selected_origin_returning_completion": witness[
            "selected_origin_returning_completion"
        ],
        "completion_cycle": completion_cycle,
        "summary": {
            "incident_x4_edge_count": len(first_edge_rows),
            "direct_boundary_x4_edge_count": observable_values[
                "direct_boundary_x4_edge_count"
            ],
            "two_step_boundary_return_count": len(completion_rows),
            "node44_completion_count": len(node44_completion_rows),
            "selected_origin_returning_completion": witness[
                "selected_origin_returning_completion"
            ],
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_x2_x4_aperture_completion_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_X2_X4_APERTURE_COMPLETION_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "after the selected x2,x1 clean return, carrier 8 has four incident x4 contacts and none are typed-boundary contacts",
            "the pure x4 contact edge 33 moves from carrier 8 to carrier 13",
            "carrier 13 has three x5 positive/negative boundary returns, each realizing the aperture word x2,x4,x5 as canonical node 44",
            "the origin-returning completion uses edge 33 then edge 43, closing the carrier cycle 12-3-8-13-12",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_x2_x4_aperture_completion@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The selected clean x2,x1 continuation has no direct boundary x4 "
            "contact, but it does have a certified two-step aperture completion: "
            "edge 33 supplies x4 to carrier 13, then edge 43 returns by x5 to "
            "the origin positive carrier 12, realizing canonical node 44."
        ),
        "stage_protocol": {
            "draft": "start from the certified clean return to negative carrier 8 and enumerate local x4 contacts",
            "witness": "materialize x4 first edges, boundary-return paths, node-44 completions, and the origin-returning cycle",
            "coherence": "check direct x4 obstruction, two-step x4/x5 completions, typed-boundary matches, and symbolic node 44",
            "closure": "certify a local aperture completion without claiming it preserves the full typed tail globally",
            "emit": "emit x2-x4 aperture-completion JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "clean_detour_report": input_entry(
                CLEAN_DETOUR_REPORT,
                {
                    "status": clean_report.get("status"),
                    "certificate_sha256": clean_report.get("certificate_sha256"),
                },
            ),
            "clean_detour_choice": input_entry(CLEAN_DETOUR_JSON),
            "clean_detour_choices": input_entry(CLEAN_DETOUR_CHOICES),
            "clean_detour_tables": input_entry(CLEAN_DETOUR_TABLES),
            "clean_detour_certificate": input_entry(CLEAN_DETOUR_CERTIFICATE),
            "cell_complex_report": input_entry(
                CELL_COMPLEX_REPORT,
                {
                    "status": cell_report.get("status"),
                    "certificate_sha256": cell_report.get("certificate_sha256"),
                },
            ),
            "cell_complex": input_entry(CELL_COMPLEX_JSON),
            "cell_complex_edges": input_entry(CELL_COMPLEX_EDGES),
            "cell_complex_tables": input_entry(CELL_COMPLEX_TABLES),
            "cell_complex_certificate": input_entry(CELL_COMPLEX_CERTIFICATE),
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
            "residual_chart_carriers": input_entry(RESIDUAL_CHART_CARRIER_CSV),
            "symbolic_alphabet": input_entry(SYMBOLIC_ALPHABET_CSV),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_x2_x4_aperture_completion": relpath(
                OUT_DIR / "signature_boundary_spine_x2_x4_aperture_completion.json"
            ),
            "x2_x4_aperture_first_edges_csv": relpath(
                OUT_DIR / "x2_x4_aperture_first_edges.csv"
            ),
            "x2_x4_aperture_completion_paths_csv": relpath(
                OUT_DIR / "x2_x4_aperture_completion_paths.csv"
            ),
            "x2_x4_aperture_completion_observables_csv": relpath(
                OUT_DIR / "x2_x4_aperture_completion_observables.csv"
            ),
            "signature_boundary_spine_x2_x4_aperture_completion_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_x2_x4_aperture_completion_tables.npz"
            ),
            "signature_boundary_spine_x2_x4_aperture_completion_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_x2_x4_aperture_completion_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the direct x4 boundary obstruction after the selected negative-8 return",
                "all one- and two-step local x4 boundary-return paths from carrier 8",
                "the three two-step node-44 aperture completions through carrier 13",
                "the unique origin-returning completion cycle using edges 14, 11, 33, and 43",
            ],
            "does_not_certify_because_not_required": [
                "that the origin-returning cycle is globally optimal among longer detours",
                "that the completion preserves the complete original typed tail after the cycle",
                "mixed x3/x4 first-contact disambiguation beyond the finite local table",
                "new categorical F-symbols, braiding, pivotality, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Promote the local aperture completion into a carrier-cycle language "
            "certificate: compute the metric and rewrite-window effects of the "
            "cycle 12-3-8-13-12 with symbols x2,x1,x4,x5, and compare it to "
            "the ambient language-graph geodesic 48-42-44."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_x2_x4_aperture_completion_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified clean-detour, residual cell-complex, typed-corridor, and symbolic-associativity artifacts",
            "enumerate x4 carrier contacts incident to the selected negative-8 return state",
            "classify direct boundary obstruction and two-step boundary returns",
            "identify node-44 aperture completions and the origin-returning cycle",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_x2_x4_aperture_completion": completion,
        "x2_x4_aperture_first_edges_csv": csv_text(
            X4_FIRST_EDGE_COLUMNS,
            first_edge_rows,
        ),
        "x2_x4_aperture_completion_paths_csv": csv_text(
            APERTURE_COMPLETION_PATH_COLUMNS,
            completion_rows,
        ),
        "x2_x4_aperture_completion_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "x4_first_edge_table": x4_first_edge_table,
        "aperture_completion_path_table": aperture_completion_path_table,
        "observable_table": observable_table,
        "signature_boundary_spine_x2_x4_aperture_completion_certificate": certificate,
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
        OUT_DIR / "signature_boundary_spine_x2_x4_aperture_completion.json",
        payloads["signature_boundary_spine_x2_x4_aperture_completion"],
    )
    (OUT_DIR / "x2_x4_aperture_first_edges.csv").write_text(
        payloads["x2_x4_aperture_first_edges_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "x2_x4_aperture_completion_paths.csv").write_text(
        payloads["x2_x4_aperture_completion_paths_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "x2_x4_aperture_completion_observables.csv").write_text(
        payloads["x2_x4_aperture_completion_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_boundary_spine_x2_x4_aperture_completion_tables.npz",
        x4_first_edge_table=payloads["x4_first_edge_table"],
        aperture_completion_path_table=payloads["aperture_completion_path_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR / "signature_boundary_spine_x2_x4_aperture_completion_certificate.json",
        payloads["signature_boundary_spine_x2_x4_aperture_completion_certificate"],
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
                "direct_boundary_x4_edge_count": witness[
                    "direct_boundary_x4_edge_count"
                ],
                "node44_completion_paths": witness["node44_completion_paths"],
                "selected_origin_returning_completion": witness[
                    "selected_origin_returning_completion"
                ],
                "completion_cycle": witness["completion_cycle"],
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
