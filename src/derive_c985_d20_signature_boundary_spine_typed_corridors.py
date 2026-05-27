from __future__ import annotations

import json
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_branching_law import (
        OUT_DIR as BRANCHING_LAW_DIR,
    )
    from .derive_c985_d20_signature_boundary_spine_poincare_path import (
        OUT_DIR as SPINE_PATH_DIR,
    )
    from .derive_c985_d20_signature_geodesic_residual_chart import (
        OUT_DIR as RESIDUAL_CHART_DIR,
    )
    from .derive_c985_d20_signature_residual_cell_complex import (
        EDGE_CENTRAL_NEGATIVE,
        EDGE_HIGH_NEGATIVE,
    )
    from .derive_c985_d20_symbolic_rewrite_rules import (
        OUT_DIR as SYMBOLIC_REWRITE_DIR,
        csv_text,
    )
    from .derive_c985_d20_signature_boundary_spine_routing_prefix import (
        bitset,
        popcount,
        read_int_csv,
        table_from_rows,
    )
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
    from derive_c985_d20_signature_boundary_spine_branching_law import (
        OUT_DIR as BRANCHING_LAW_DIR,
    )
    from derive_c985_d20_signature_boundary_spine_poincare_path import (
        OUT_DIR as SPINE_PATH_DIR,
    )
    from derive_c985_d20_signature_geodesic_residual_chart import (
        OUT_DIR as RESIDUAL_CHART_DIR,
    )
    from derive_c985_d20_signature_residual_cell_complex import (
        EDGE_CENTRAL_NEGATIVE,
        EDGE_HIGH_NEGATIVE,
    )
    from derive_c985_d20_symbolic_rewrite_rules import (
        OUT_DIR as SYMBOLIC_REWRITE_DIR,
        csv_text,
    )
    from derive_c985_d20_signature_boundary_spine_routing_prefix import (
        bitset,
        popcount,
        read_int_csv,
        table_from_rows,
    )
    from derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "c985_d20_signature_boundary_spine_typed_corridors"
STATUS = "C985_D20_SIGNATURE_BOUNDARY_SPINE_TYPED_CORRIDORS_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

BRANCHING_LAW_REPORT = BRANCHING_LAW_DIR / "report.json"
BRANCHING_LAW_JSON = BRANCHING_LAW_DIR / "signature_boundary_spine_branching_law.json"
BRANCHING_LAW_CSV = BRANCHING_LAW_DIR / "negative_branch_order.csv"
BRANCHING_LAW_TABLES = (
    BRANCHING_LAW_DIR / "signature_boundary_spine_branching_law_tables.npz"
)
BRANCHING_LAW_CERTIFICATE = (
    BRANCHING_LAW_DIR / "signature_boundary_spine_branching_law_certificate.json"
)

SPINE_PATH_REPORT = SPINE_PATH_DIR / "report.json"
SPINE_PATH_EDGES = SPINE_PATH_DIR / "boundary_spine_poincare_edges.csv"
SPINE_PATH_TABLES = SPINE_PATH_DIR / "signature_boundary_spine_poincare_path_tables.npz"
SPINE_PATH_CERTIFICATE = (
    SPINE_PATH_DIR / "signature_boundary_spine_poincare_path_certificate.json"
)

RESIDUAL_CHART_REPORT = RESIDUAL_CHART_DIR / "report.json"
RESIDUAL_CHART_CARRIER_CSV = RESIDUAL_CHART_DIR / "carrier_residual_chart.csv"
RESIDUAL_CHART_TABLES = RESIDUAL_CHART_DIR / "signature_geodesic_residual_chart_tables.npz"
RESIDUAL_CHART_CERTIFICATE = (
    RESIDUAL_CHART_DIR / "signature_geodesic_residual_chart_certificate.json"
)

SYMBOLIC_REWRITE_REPORT = SYMBOLIC_REWRITE_DIR / "report.json"
SYMBOLIC_ALPHABET_JSON = SYMBOLIC_REWRITE_DIR / "symbolic_alphabet.json"
SYMBOLIC_ALPHABET_CSV = SYMBOLIC_REWRITE_DIR / "symbolic_alphabet.csv"
SYMBOLIC_REWRITE_RULES_CSV = SYMBOLIC_REWRITE_DIR / "rewrite_rules.csv"
SYMBOLIC_REWRITE_TABLES = SYMBOLIC_REWRITE_DIR / "symbolic_rewrite_tables.npz"
SYMBOLIC_REWRITE_CERTIFICATE = SYMBOLIC_REWRITE_DIR / "symbolic_rewrite_certificate.json"

DERIVE_SCRIPT = (
    ROOT / "src" / "derive_c985_d20_signature_boundary_spine_typed_corridors.py"
)
VALIDATOR_SCRIPT = (
    ROOT / "src" / "certify_c985_d20_signature_boundary_spine_typed_corridors.py"
)

FULL_ALPHABET_SYMBOL_BITSET = (1 << 6) - 1

CORRIDOR_EDGE_COLUMNS = [
    "boundary_spine_rank",
    "boundary_mask_edge_id",
    "negative_branch_order_rank",
    "negative_carrier_mask_class_id",
    "positive_carrier_mask_class_id",
    "boundary_partition_code",
    "phase_code",
    "first_arrival_flag",
    "previous_obstruction_flag",
    "positive_carrier_atom_bitset",
    "negative_carrier_atom_bitset",
    "shared_atom_bitset",
    "positive_symbol_bitset",
    "negative_symbol_bitset",
    "corridor_symbol_bitset",
    "shared_symbol_id",
    "shared_symbol_bitset",
    "shared_symbol_self_rule_id",
    "shared_symbol_sector_mask",
    "shared_symbol_signature_class_count",
    "corridor_symbol_count",
    "undirected_stationary_flux_x1e12",
    "total_entropy_contribution_x1e12",
]

BRANCH_CORRIDOR_COLUMNS = [
    "branch_order_rank",
    "negative_carrier_mask_class_id",
    "first_prefix_length",
    "first_boundary_mask_edge_id",
    "first_phase_code",
    "previous_obstruction_flag",
    "positive_carrier_count",
    "positive_carrier_bitset",
    "positive_symbol_bitset",
    "negative_symbol_bitset",
    "corridor_symbol_bitset",
    "corridor_symbol_count",
    "missing_symbol_bitset",
    "full_alphabet_coverage_flag",
    "first_shared_symbol_id",
    "shared_symbol_bitset",
    "shared_symbol_count",
    "total_edge_count",
    "central_negative_edge_count",
    "high_negative_edge_count",
    "total_flux_for_branch_x1e12",
    "total_entropy_for_branch_x1e12",
]

CORRIDOR_OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "corridor_edge_count": 0,
    "negative_branch_count": 1,
    "alphabet_symbol_count": 2,
    "corridor_carrier_symbol_count": 3,
    "corridor_gate_symbol_count": 4,
    "corridor_gate_missing_symbol_bitset": 5,
    "corridor_gate_x0_count": 6,
    "corridor_gate_x1_count": 7,
    "corridor_gate_x3_count": 8,
    "corridor_gate_x5_count": 9,
    "pre_flip_full_alphabet_branch_count": 10,
    "at_flip_full_alphabet_branch_count": 11,
    "post_flip_full_alphabet_branch_count": 12,
    "first_non_full_alphabet_branch_prefix": 13,
    "first_non_full_alphabet_negative_mask": 14,
    "missing_gate_full_sector_rule_count": 15,
    "missing_gate_max_signature_union": 16,
    "missing_gate_canonical_pair_id": 17,
    "delayed_obstruction_shared_symbol_id": 18,
    "obstruction_first_gate_symbol_signature": 19,
}


def decode_bitset(value: int) -> list[int]:
    return [index for index in range(64) if int(value) & (1 << index)]


def carrier_atom_ids(carrier_row: dict[str, int]) -> list[int]:
    return [
        int(carrier_row[f"carrier_atom_id_{index}"])
        for index in range(4)
        if int(carrier_row[f"carrier_atom_id_{index}"]) >= 0
    ]


def symbol_bitset_for_atoms(atom_ids: list[int], atom_to_symbol: dict[int, int]) -> int:
    return bitset({atom_to_symbol[int(atom_id)] for atom_id in atom_ids})


def phase_name(phase_code: int) -> str:
    if int(phase_code) < 0:
        return "pre_flip"
    if int(phase_code) == 0:
        return "at_flip"
    return "post_flip"


def build_payloads() -> dict[str, Any]:
    branching_report = load_json(BRANCHING_LAW_REPORT)
    branching_law = load_json(BRANCHING_LAW_JSON)
    spine_report = load_json(SPINE_PATH_REPORT)
    residual_report = load_json(RESIDUAL_CHART_REPORT)
    symbolic_report = load_json(SYMBOLIC_REWRITE_REPORT)
    symbolic_alphabet = load_json(SYMBOLIC_ALPHABET_JSON)

    branching_tables = np.load(BRANCHING_LAW_TABLES, allow_pickle=False)
    spine_tables = np.load(SPINE_PATH_TABLES, allow_pickle=False)
    residual_tables = np.load(RESIDUAL_CHART_TABLES, allow_pickle=False)
    symbolic_tables = np.load(SYMBOLIC_REWRITE_TABLES, allow_pickle=False)

    branch_rows = read_int_csv(BRANCHING_LAW_CSV)
    spine_rows = read_int_csv(SPINE_PATH_EDGES)
    carrier_rows = {
        int(row["carrier_mask_class_id"]): row
        for row in read_int_csv(RESIDUAL_CHART_CARRIER_CSV)
    }
    alphabet_rows = read_int_csv(SYMBOLIC_ALPHABET_CSV)
    rewrite_rows = read_int_csv(SYMBOLIC_REWRITE_RULES_CSV)

    atom_to_symbol = {
        int(row["atom_id"]): int(row["symbol_id"]) for row in alphabet_rows
    }
    symbol_to_alphabet = {
        int(row["symbol_id"]): row for row in alphabet_rows
    }
    self_rule_by_symbol = {
        int(row["left_symbol_id"]): row
        for row in rewrite_rows
        if int(row["left_symbol_id"]) == int(row["right_symbol_id"])
    }
    branch_by_negative = {
        int(row["negative_carrier_mask_class_id"]): row for row in branch_rows
    }

    corridor_edge_rows: list[dict[str, int]] = []
    for row in spine_rows:
        positive_id = int(row["positive_carrier_mask_class_id"])
        negative_id = int(row["negative_carrier_mask_class_id"])
        branch = branch_by_negative[negative_id]
        positive_atoms = carrier_atom_ids(carrier_rows[positive_id])
        negative_atoms = carrier_atom_ids(carrier_rows[negative_id])
        shared_atoms = sorted(set(positive_atoms) & set(negative_atoms))
        shared_symbols = sorted(atom_to_symbol[atom_id] for atom_id in shared_atoms)
        shared_symbol_id = shared_symbols[0] if len(shared_symbols) == 1 else -1
        positive_symbol_bitset = symbol_bitset_for_atoms(positive_atoms, atom_to_symbol)
        negative_symbol_bitset = symbol_bitset_for_atoms(negative_atoms, atom_to_symbol)
        shared_symbol_bitset = bitset(shared_symbols)
        alphabet_row = symbol_to_alphabet[shared_symbol_id]
        self_rule = self_rule_by_symbol[shared_symbol_id]
        corridor_edge_rows.append(
            {
                "boundary_spine_rank": int(row["boundary_spine_rank"]),
                "boundary_mask_edge_id": int(row["boundary_mask_edge_id"]),
                "negative_branch_order_rank": int(branch["branch_order_rank"]),
                "negative_carrier_mask_class_id": negative_id,
                "positive_carrier_mask_class_id": positive_id,
                "boundary_partition_code": int(row["boundary_partition_code"]),
                "phase_code": int(branch["first_phase_code"]),
                "first_arrival_flag": int(
                    int(row["boundary_spine_rank"])
                    == int(branch["first_prefix_length"])
                ),
                "previous_obstruction_flag": int(
                    branch["previous_obstruction_flag"]
                ),
                "positive_carrier_atom_bitset": int(
                    carrier_rows[positive_id]["carrier_atom_mask"]
                ),
                "negative_carrier_atom_bitset": int(
                    carrier_rows[negative_id]["carrier_atom_mask"]
                ),
                "shared_atom_bitset": bitset(shared_atoms),
                "positive_symbol_bitset": positive_symbol_bitset,
                "negative_symbol_bitset": negative_symbol_bitset,
                "corridor_symbol_bitset": positive_symbol_bitset
                | negative_symbol_bitset,
                "shared_symbol_id": shared_symbol_id,
                "shared_symbol_bitset": shared_symbol_bitset,
                "shared_symbol_self_rule_id": int(self_rule["rule_id"]),
                "shared_symbol_sector_mask": int(alphabet_row["sector_mask"]),
                "shared_symbol_signature_class_count": int(
                    alphabet_row["signature_class_count"]
                ),
                "corridor_symbol_count": popcount(
                    positive_symbol_bitset | negative_symbol_bitset
                ),
                "undirected_stationary_flux_x1e12": int(
                    row["undirected_stationary_flux_x1e12"]
                ),
                "total_entropy_contribution_x1e12": int(
                    row["total_entropy_contribution_x1e12"]
                ),
            }
        )

    branch_corridor_rows: list[dict[str, int]] = []
    for branch in branch_rows:
        negative_id = int(branch["negative_carrier_mask_class_id"])
        edge_subset = [
            row
            for row in corridor_edge_rows
            if int(row["negative_carrier_mask_class_id"]) == negative_id
        ]
        positive_carriers = {
            int(row["positive_carrier_mask_class_id"]) for row in edge_subset
        }
        shared_symbols = {int(row["shared_symbol_id"]) for row in edge_subset}
        positive_symbol_bitset = 0
        for row in edge_subset:
            positive_symbol_bitset |= int(row["positive_symbol_bitset"])
        negative_symbol_bitset = int(edge_subset[0]["negative_symbol_bitset"])
        corridor_symbol_bitset = positive_symbol_bitset | negative_symbol_bitset
        first_edge = next(row for row in edge_subset if int(row["first_arrival_flag"]) == 1)
        branch_corridor_rows.append(
            {
                "branch_order_rank": int(branch["branch_order_rank"]),
                "negative_carrier_mask_class_id": negative_id,
                "first_prefix_length": int(branch["first_prefix_length"]),
                "first_boundary_mask_edge_id": int(branch["first_boundary_mask_edge_id"]),
                "first_phase_code": int(branch["first_phase_code"]),
                "previous_obstruction_flag": int(branch["previous_obstruction_flag"]),
                "positive_carrier_count": len(positive_carriers),
                "positive_carrier_bitset": bitset(positive_carriers),
                "positive_symbol_bitset": positive_symbol_bitset,
                "negative_symbol_bitset": negative_symbol_bitset,
                "corridor_symbol_bitset": corridor_symbol_bitset,
                "corridor_symbol_count": popcount(corridor_symbol_bitset),
                "missing_symbol_bitset": FULL_ALPHABET_SYMBOL_BITSET
                & ~corridor_symbol_bitset,
                "full_alphabet_coverage_flag": int(
                    corridor_symbol_bitset == FULL_ALPHABET_SYMBOL_BITSET
                ),
                "first_shared_symbol_id": int(first_edge["shared_symbol_id"]),
                "shared_symbol_bitset": bitset(shared_symbols),
                "shared_symbol_count": len(shared_symbols),
                "total_edge_count": len(edge_subset),
                "central_negative_edge_count": sum(
                    1
                    for row in edge_subset
                    if int(row["boundary_partition_code"]) == EDGE_CENTRAL_NEGATIVE
                ),
                "high_negative_edge_count": sum(
                    1
                    for row in edge_subset
                    if int(row["boundary_partition_code"]) == EDGE_HIGH_NEGATIVE
                ),
                "total_flux_for_branch_x1e12": sum(
                    int(row["undirected_stationary_flux_x1e12"])
                    for row in edge_subset
                ),
                "total_entropy_for_branch_x1e12": sum(
                    int(row["total_entropy_contribution_x1e12"])
                    for row in edge_subset
                ),
            }
        )

    gate_symbol_sequence = [
        int(row["shared_symbol_id"]) for row in corridor_edge_rows
    ]
    gate_symbol_histogram = {
        symbol_id: gate_symbol_sequence.count(symbol_id) for symbol_id in range(6)
    }
    gate_symbol_bitset = bitset(set(gate_symbol_sequence))
    missing_gate_symbol_bitset = FULL_ALPHABET_SYMBOL_BITSET & ~gate_symbol_bitset
    missing_gate_symbols = decode_bitset(missing_gate_symbol_bitset)
    carrier_symbol_bitset = 0
    for row in corridor_edge_rows:
        carrier_symbol_bitset |= int(row["corridor_symbol_bitset"])

    phase_full_counts = {
        phase: sum(
            1
            for row in branch_corridor_rows
            if phase_name(int(row["first_phase_code"])) == phase
            and int(row["full_alphabet_coverage_flag"]) == 1
        )
        for phase in ("pre_flip", "at_flip", "post_flip")
    }
    first_non_full = next(
        row
        for row in branch_corridor_rows
        if int(row["full_alphabet_coverage_flag"]) == 0
    )
    missing_gate_rules = [
        row
        for row in rewrite_rows
        if sorted([int(row["left_symbol_id"]), int(row["right_symbol_id"])])
        == missing_gate_symbols
        and int(row["left_symbol_id"]) != int(row["right_symbol_id"])
    ]
    obstruction_first_gate_symbols = [
        int(row["first_shared_symbol_id"])
        for row in branch_corridor_rows
        if int(row["previous_obstruction_flag"]) == 1
    ]
    delayed_obstruction_shared_symbol_id = next(
        int(row["first_shared_symbol_id"])
        for row in branch_corridor_rows
        if int(row["previous_obstruction_flag"]) == 1
        and int(row["first_phase_code"]) > 0
    )
    obstruction_first_gate_signature = sum(
        (index + 1) * symbol_id
        for index, symbol_id in enumerate(obstruction_first_gate_symbols)
    )

    observable_values = {
        "corridor_edge_count": len(corridor_edge_rows),
        "negative_branch_count": len(branch_corridor_rows),
        "alphabet_symbol_count": len(alphabet_rows),
        "corridor_carrier_symbol_count": popcount(carrier_symbol_bitset),
        "corridor_gate_symbol_count": popcount(gate_symbol_bitset),
        "corridor_gate_missing_symbol_bitset": missing_gate_symbol_bitset,
        "corridor_gate_x0_count": gate_symbol_histogram[0],
        "corridor_gate_x1_count": gate_symbol_histogram[1],
        "corridor_gate_x3_count": gate_symbol_histogram[3],
        "corridor_gate_x5_count": gate_symbol_histogram[5],
        "pre_flip_full_alphabet_branch_count": phase_full_counts["pre_flip"],
        "at_flip_full_alphabet_branch_count": phase_full_counts["at_flip"],
        "post_flip_full_alphabet_branch_count": phase_full_counts["post_flip"],
        "first_non_full_alphabet_branch_prefix": int(
            first_non_full["first_prefix_length"]
        ),
        "first_non_full_alphabet_negative_mask": int(
            first_non_full["negative_carrier_mask_class_id"]
        ),
        "missing_gate_full_sector_rule_count": len(missing_gate_rules),
        "missing_gate_max_signature_union": max(
            int(row["signature_union_count"]) for row in missing_gate_rules
        ),
        "missing_gate_canonical_pair_id": int(
            missing_gate_rules[0]["canonical_pair_id"]
        ),
        "delayed_obstruction_shared_symbol_id": delayed_obstruction_shared_symbol_id,
        "obstruction_first_gate_symbol_signature": obstruction_first_gate_signature,
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

    corridor_edge_table = table_from_rows(CORRIDOR_EDGE_COLUMNS, corridor_edge_rows)
    branch_corridor_table = table_from_rows(
        BRANCH_CORRIDOR_COLUMNS,
        branch_corridor_rows,
    )
    corridor_observable_table = table_from_rows(
        CORRIDOR_OBSERVABLE_COLUMNS,
        observable_rows,
    )

    checks = {
        "branching_law_report_certified": branching_report.get("all_checks_pass")
        is True,
        "spine_path_report_certified": spine_report.get("all_checks_pass") is True,
        "residual_chart_report_certified": residual_report.get("all_checks_pass")
        is True,
        "symbolic_rewrite_report_certified": symbolic_report.get("all_checks_pass")
        is True,
        "branching_law_schema_available": branching_law.get("schema")
        == "c985.d20_signature_boundary_spine_branching_law@1",
        "symbolic_alphabet_schema_available": symbolic_alphabet.get("schema")
        == "c985.d20_symbolic_alphabet_rewrites@1",
        "branching_law_tables_available": "negative_branch_order_table"
        in branching_tables.files,
        "spine_path_tables_available": "spine_poincare_edge_table"
        in spine_tables.files,
        "residual_chart_tables_available": "carrier_residual_chart_table"
        in residual_tables.files,
        "symbolic_rewrite_tables_available": "rewrite_rule_table"
        in symbolic_tables.files,
        "all_corridor_edges_have_single_shared_atom": all(
            popcount(int(row["shared_atom_bitset"])) == 1 for row in corridor_edge_rows
        ),
        "all_shared_atoms_map_to_alphabet_symbols": all(
            int(row["shared_symbol_id"]) in symbol_to_alphabet
            for row in corridor_edge_rows
        ),
        "corridor_carriers_cover_full_six_symbol_alphabet": carrier_symbol_bitset
        == FULL_ALPHABET_SYMBOL_BITSET,
        "gate_symbol_sequence_matches_expected": gate_symbol_sequence
        == [5, 5, 0, 0, 1, 3, 1, 5, 3, 5, 5, 3, 5, 3, 1, 0],
        "gate_symbol_histogram_matches_expected": [
            gate_symbol_histogram[index] for index in range(6)
        ]
        == [3, 3, 0, 4, 0, 6],
        "gate_missing_symbols_are_x2_x4": missing_gate_symbols == [2, 4],
        "missing_gate_pair_is_full_sector_max_rewrite_pair": len(missing_gate_rules)
        == 2
        and all(int(row["sector_coverage_count"]) == 6 for row in missing_gate_rules)
        and all(
            int(row["signature_union_count"]) == 155 for row in missing_gate_rules
        )
        and {int(row["rule_id"]) for row in missing_gate_rules} == {16, 26},
        "branch_corridor_counts_match_expected": [
            int(row["corridor_symbol_count"]) for row in branch_corridor_rows
        ]
        == [6, 6, 6, 5, 4, 3],
        "pre_flip_branches_have_full_alphabet": phase_full_counts
        == {"pre_flip": 3, "at_flip": 0, "post_flip": 0},
        "first_non_full_branch_is_flip_mask_9": (
            int(first_non_full["first_prefix_length"]),
            int(first_non_full["negative_carrier_mask_class_id"]),
        )
        == (8, 9),
        "obstruction_gate_symbols_match_expected": obstruction_first_gate_symbols
        == [0, 1, 3],
        "delayed_obstruction_gate_is_x3": delayed_obstruction_shared_symbol_id == 3,
        "corridor_edge_table_shape_is_16_by_23": tuple(corridor_edge_table.shape)
        == (16, len(CORRIDOR_EDGE_COLUMNS)),
        "branch_corridor_table_shape_is_6_by_22": tuple(branch_corridor_table.shape)
        == (6, len(BRANCH_CORRIDOR_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(corridor_observable_table.shape)
        == (len(OBSERVABLE_CODES), len(CORRIDOR_OBSERVABLE_COLUMNS)),
    }

    witness = {
        "gate_symbol_sequence": gate_symbol_sequence,
        "gate_symbol_histogram": [
            {"symbol_id": symbol_id, "count": gate_symbol_histogram[symbol_id]}
            for symbol_id in range(6)
        ],
        "gate_symbol_ids": decode_bitset(gate_symbol_bitset),
        "missing_gate_symbol_ids": missing_gate_symbols,
        "missing_gate_rewrite_rules": [
            {
                "rule_id": int(row["rule_id"]),
                "left_symbol_id": int(row["left_symbol_id"]),
                "right_symbol_id": int(row["right_symbol_id"]),
                "canonical_pair_id": int(row["canonical_pair_id"]),
                "sector_coverage_count": int(row["sector_coverage_count"]),
                "signature_union_count": int(row["signature_union_count"]),
            }
            for row in missing_gate_rules
        ],
        "branch_corridor_symbol_counts": [
            int(row["corridor_symbol_count"]) for row in branch_corridor_rows
        ],
        "branch_first_shared_symbols": [
            int(row["first_shared_symbol_id"]) for row in branch_corridor_rows
        ],
        "branch_positive_carrier_bitsets": [
            int(row["positive_carrier_bitset"]) for row in branch_corridor_rows
        ],
        "pre_flip_full_alphabet_branch_count": phase_full_counts["pre_flip"],
        "at_flip_full_alphabet_branch_count": phase_full_counts["at_flip"],
        "post_flip_full_alphabet_branch_count": phase_full_counts["post_flip"],
        "first_non_full_alphabet_branch": {
            "prefix_length": int(first_non_full["first_prefix_length"]),
            "negative_carrier_mask_class_id": int(
                first_non_full["negative_carrier_mask_class_id"]
            ),
            "corridor_symbol_count": int(first_non_full["corridor_symbol_count"]),
            "missing_symbol_ids": decode_bitset(
                int(first_non_full["missing_symbol_bitset"])
            ),
        },
        "obstruction_first_gate_symbol_ids": obstruction_first_gate_symbols,
        "delayed_obstruction_shared_symbol_id": delayed_obstruction_shared_symbol_id,
        "corridor_edge_table_sha256": sha_array(corridor_edge_table),
        "branch_corridor_table_sha256": sha_array(branch_corridor_table),
        "corridor_observable_table_sha256": sha_array(corridor_observable_table),
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_typed_corridors_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_TYPED_CORRIDORS_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "all 16 boundary-spine contacts have exactly one shared active atom",
            "the shared contact atoms form the gate-letter sequence x5,x5,x0,x0,x1,x3,x1,x5,x3,x5,x5,x3,x5,x3,x1,x0",
            "the gate grammar uses symbols x0, x1, x3, and x5 while omitting x2 and x4",
            "the omitted gate pair x2/x4 is exactly the full-sector, max-signature binary rewrite pair",
            "all pre-flip negative branch corridors cover the full six-symbol alphabet; the prefix-8 branch is the first non-full corridor",
        ],
    }

    typed_corridors = {
        "schema": "c985.d20_signature_boundary_spine_typed_corridors@1",
        "object": "d20",
        "corridor_rule": {
            "source": "certified negative-carrier branch law and six-symbol rewrite alphabet",
            "contact": "each boundary-spine edge is typed by the unique shared active atom between its positive and negative carrier masks",
            "gate_symbol": "the shared active atom is translated to its certified symbolic alphabet letter",
            "rewrite_comparison": "compare missing gate letters with the certified binary rewrite rules",
        },
        "gate_symbol_sequence": witness["gate_symbol_sequence"],
        "gate_symbol_ids": witness["gate_symbol_ids"],
        "missing_gate_symbol_ids": witness["missing_gate_symbol_ids"],
        "branch_corridor_symbol_counts": witness["branch_corridor_symbol_counts"],
        "first_non_full_alphabet_branch": witness["first_non_full_alphabet_branch"],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_typed_corridors@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The negative-branch spine has a typed corridor grammar: every "
            "boundary contact is delivered by one shared six-symbol alphabet "
            "letter, the gate letters are x0, x1, x3, and x5, and the missing "
            "gate pair x2/x4 is exactly the full-sector max-signature binary "
            "rewrite pair."
        ),
        "stage_protocol": {
            "draft": "attach positive and negative carrier masks to each branch corridor",
            "witness": "materialize carrier atom sets, shared gate atoms, and symbolic gate letters",
            "coherence": "compare corridor gate letters with the certified six-symbol rewrite alphabet",
            "closure": "certify finite typed corridors without claiming a new symbolic product",
            "emit": "emit typed-corridor JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "branching_law_report": input_entry(
                BRANCHING_LAW_REPORT,
                {
                    "status": branching_report.get("status"),
                    "certificate_sha256": branching_report.get("certificate_sha256"),
                },
            ),
            "branching_law": input_entry(BRANCHING_LAW_JSON),
            "branching_law_csv": input_entry(BRANCHING_LAW_CSV),
            "branching_law_tables": input_entry(BRANCHING_LAW_TABLES),
            "branching_law_certificate": input_entry(BRANCHING_LAW_CERTIFICATE),
            "spine_path_report": input_entry(
                SPINE_PATH_REPORT,
                {
                    "status": spine_report.get("status"),
                    "certificate_sha256": spine_report.get("certificate_sha256"),
                },
            ),
            "spine_path_edges": input_entry(SPINE_PATH_EDGES),
            "spine_path_tables": input_entry(SPINE_PATH_TABLES),
            "spine_path_certificate": input_entry(SPINE_PATH_CERTIFICATE),
            "residual_chart_report": input_entry(
                RESIDUAL_CHART_REPORT,
                {
                    "status": residual_report.get("status"),
                    "certificate_sha256": residual_report.get("certificate_sha256"),
                },
            ),
            "residual_chart_carriers": input_entry(RESIDUAL_CHART_CARRIER_CSV),
            "residual_chart_tables": input_entry(RESIDUAL_CHART_TABLES),
            "residual_chart_certificate": input_entry(RESIDUAL_CHART_CERTIFICATE),
            "symbolic_rewrite_report": input_entry(
                SYMBOLIC_REWRITE_REPORT,
                {
                    "status": symbolic_report.get("status"),
                    "certificate_sha256": symbolic_report.get("certificate_sha256"),
                },
            ),
            "symbolic_alphabet": input_entry(SYMBOLIC_ALPHABET_JSON),
            "symbolic_alphabet_csv": input_entry(SYMBOLIC_ALPHABET_CSV),
            "symbolic_rewrite_rules": input_entry(SYMBOLIC_REWRITE_RULES_CSV),
            "symbolic_rewrite_tables": input_entry(SYMBOLIC_REWRITE_TABLES),
            "symbolic_rewrite_certificate": input_entry(SYMBOLIC_REWRITE_CERTIFICATE),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_typed_corridors": relpath(
                OUT_DIR / "signature_boundary_spine_typed_corridors.json"
            ),
            "corridor_edge_symbols_csv": relpath(
                OUT_DIR / "corridor_edge_symbols.csv"
            ),
            "branch_corridor_summary_csv": relpath(
                OUT_DIR / "branch_corridor_summary.csv"
            ),
            "corridor_observables_csv": relpath(
                OUT_DIR / "corridor_observables.csv"
            ),
            "signature_boundary_spine_typed_corridors_tables": relpath(
                OUT_DIR / "signature_boundary_spine_typed_corridors_tables.npz"
            ),
            "signature_boundary_spine_typed_corridors_certificate": relpath(
                OUT_DIR / "signature_boundary_spine_typed_corridors_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "positive and negative carrier-mask corridors for each negative branch",
                "the unique shared active atom and symbolic gate letter for every boundary-spine contact",
                "that the corridor carriers cover the full six-symbol alphabet while the gate letters omit x2 and x4",
                "that the omitted gate pair x2/x4 is the certified full-sector max-signature binary rewrite pair",
            ],
            "does_not_certify_because_not_required": [
                "a new product or rewrite rule beyond the existing six-symbol alphabet",
                "that the corridor grammar is invariant under alternative spine rankings",
                "higher-eigenmode corridor grammars",
                "new associator, pentagon, pivotal, spherical, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Lift the typed corridor grammar into a finite transition automaton: "
            "certify which gate-letter words occur along source-to-branch paths, "
            "then compare those words with the length-three symbolic "
            "associativity diamonds."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_typed_corridors_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified branching-law, Poincare-spine, residual-chart, and symbolic-rewrite artifacts",
            "attach positive and negative carrier masks to each branch corridor",
            "translate shared active atoms to six-symbol alphabet letters",
            "compare missing gate letters with the certified binary rewrite rules",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_typed_corridors": typed_corridors,
        "corridor_edge_symbols_csv": csv_text(
            CORRIDOR_EDGE_COLUMNS,
            corridor_edge_rows,
        ),
        "branch_corridor_summary_csv": csv_text(
            BRANCH_CORRIDOR_COLUMNS,
            branch_corridor_rows,
        ),
        "corridor_observables_csv": csv_text(
            CORRIDOR_OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "corridor_edge_table": corridor_edge_table,
        "branch_corridor_table": branch_corridor_table,
        "corridor_observable_table": corridor_observable_table,
        "signature_boundary_spine_typed_corridors_certificate": certificate,
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
        OUT_DIR / "signature_boundary_spine_typed_corridors.json",
        payloads["signature_boundary_spine_typed_corridors"],
    )
    (OUT_DIR / "corridor_edge_symbols.csv").write_text(
        payloads["corridor_edge_symbols_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "branch_corridor_summary.csv").write_text(
        payloads["branch_corridor_summary_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "corridor_observables.csv").write_text(
        payloads["corridor_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_boundary_spine_typed_corridors_tables.npz",
        corridor_edge_table=payloads["corridor_edge_table"],
        branch_corridor_table=payloads["branch_corridor_table"],
        corridor_observable_table=payloads["corridor_observable_table"],
    )
    write_json(
        OUT_DIR / "signature_boundary_spine_typed_corridors_certificate.json",
        payloads["signature_boundary_spine_typed_corridors_certificate"],
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
                "gate_symbol_sequence": witness["gate_symbol_sequence"],
                "missing_gate_symbol_ids": witness["missing_gate_symbol_ids"],
                "branch_corridor_symbol_counts": witness[
                    "branch_corridor_symbol_counts"
                ],
                "first_non_full_alphabet_branch": witness[
                    "first_non_full_alphabet_branch"
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
