from __future__ import annotations

import json
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_cycle_pareto_frontier import (
        OUT_DIR as PARETO_DIR,
        PARETO_CANDIDATE_COLUMNS,
    )
    from .derive_c985_d20_signature_boundary_spine_routing_prefix import (
        read_int_csv,
        table_from_rows,
    )
    from .derive_c985_d20_signature_boundary_spine_x2_detour_fan import (
        DETOUR_EDGE_COLUMNS,
        OUT_DIR as X2_DETOUR_DIR,
    )
    from .derive_c985_d20_signature_residual_cell_complex import (
        OUT_DIR as CELL_COMPLEX_DIR,
    )
    from .derive_c985_d20_symbolic_rewrite_rules import (
        ALPHABET_COLUMNS,
        OUT_DIR as SYMBOLIC_REWRITE_DIR,
        csv_text,
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
    from derive_c985_d20_signature_boundary_spine_aperture_cycle_pareto_frontier import (
        OUT_DIR as PARETO_DIR,
        PARETO_CANDIDATE_COLUMNS,
    )
    from derive_c985_d20_signature_boundary_spine_routing_prefix import (
        read_int_csv,
        table_from_rows,
    )
    from derive_c985_d20_signature_boundary_spine_x2_detour_fan import (
        DETOUR_EDGE_COLUMNS,
        OUT_DIR as X2_DETOUR_DIR,
    )
    from derive_c985_d20_signature_residual_cell_complex import (
        OUT_DIR as CELL_COMPLEX_DIR,
    )
    from derive_c985_d20_symbolic_rewrite_rules import (
        ALPHABET_COLUMNS,
        OUT_DIR as SYMBOLIC_REWRITE_DIR,
        csv_text,
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


THEOREM_ID = "c985_d20_signature_boundary_spine_aperture_mixed_contact_atoms"
STATUS = "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_MIXED_CONTACT_ATOMS_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

PARETO_REPORT = PARETO_DIR / "report.json"
PARETO_JSON = PARETO_DIR / "signature_boundary_spine_aperture_cycle_pareto_frontier.json"
PARETO_CANDIDATES = PARETO_DIR / "aperture_cycle_pareto_candidates.csv"
PARETO_TABLES = PARETO_DIR / "signature_boundary_spine_aperture_cycle_pareto_frontier_tables.npz"
PARETO_CERTIFICATE = (
    PARETO_DIR
    / "signature_boundary_spine_aperture_cycle_pareto_frontier_certificate.json"
)

X2_DETOUR_REPORT = X2_DETOUR_DIR / "report.json"
X2_DETOUR_EDGES = X2_DETOUR_DIR / "x2_detour_edges.csv"
X2_DETOUR_TABLES = X2_DETOUR_DIR / "signature_boundary_spine_x2_detour_fan_tables.npz"
X2_DETOUR_CERTIFICATE = (
    X2_DETOUR_DIR / "signature_boundary_spine_x2_detour_fan_certificate.json"
)

CELL_COMPLEX_REPORT = CELL_COMPLEX_DIR / "report.json"
CELL_COMPLEX_EDGES = CELL_COMPLEX_DIR / "carrier_region_edges.csv"
CELL_COMPLEX_TABLES = CELL_COMPLEX_DIR / "signature_residual_cell_complex_tables.npz"
CELL_COMPLEX_CERTIFICATE = (
    CELL_COMPLEX_DIR / "signature_residual_cell_complex_certificate.json"
)

SYMBOLIC_REWRITE_REPORT = SYMBOLIC_REWRITE_DIR / "report.json"
SYMBOLIC_ALPHABET = SYMBOLIC_REWRITE_DIR / "symbolic_alphabet.csv"
SYMBOLIC_REWRITE_TABLES = SYMBOLIC_REWRITE_DIR / "symbolic_rewrite_tables.npz"
SYMBOLIC_REWRITE_CERTIFICATE = (
    SYMBOLIC_REWRITE_DIR / "symbolic_rewrite_certificate.json"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_mixed_contact_atoms.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_mixed_contact_atoms.py"
)

X2_SYMBOL_ID = 2
X5_SYMBOL_ID = 5
X2_ATOM_ID = 7
X5_ATOM_ID = 19
SELECTED_CANDIDATE_ID = 6
ZERO_OVERHEAD_CANDIDATE_IDS = [0, 1, 2, 3, 4, 5]
MIXED_FIRST_EDGE_IDS = [39, 41]
CLEAN_FIRST_EDGE_ID = 14

ATOM_CONTACT_COLUMNS = [
    "atom_contact_id",
    "cell_edge_id",
    "source_carrier_mask_class_id",
    "target_carrier_mask_class_id",
    "source_carrier_atom_mask",
    "target_carrier_atom_mask",
    "shared_atom_id",
    "shared_symbol_id",
    "shared_symbol_bitset",
    "symbol_sector_mask",
    "symbol_signature_class_count",
    "x2_atom_witness_flag",
    "x5_atom_cowitness_flag",
]

EDGE_RESOLUTION_COLUMNS = [
    "first_contact_edge_id",
    "candidate_count",
    "geodesic_candidate_count",
    "pareto_candidate_count",
    "dominated_candidate_count",
    "source_carrier_mask_class_id",
    "target_carrier_mask_class_id",
    "shared_atom_count",
    "shared_symbol_count",
    "x2_atom_witness_count",
    "x5_atom_cowitness_count",
    "shared_atom_bitset",
    "shared_symbol_bitset",
    "carrier_mask_pure_x2_flag",
    "carrier_mask_mixed_x2_x5_flag",
    "atom_level_x2_witness_flag",
    "requires_atom_selector_flag",
    "ambiguity_intrinsic_in_carrier_quotient_flag",
]

CANDIDATE_RESOLUTION_COLUMNS = [
    "candidate_id",
    "rank_order",
    "first_contact_edge_id",
    "trace_detour_overhead",
    "signature_valley_depth",
    "metric_gromov_delta_twice",
    "typed_boundary_cost",
    "geodesic_optimal_flag",
    "pareto_frontier_flag",
    "dominated_flag",
    "carrier_mask_pure_x2_flag",
    "carrier_mask_mixed_x2_x5_flag",
    "atom_level_x2_witness_flag",
    "atom_x5_cowitness_flag",
    "requires_atom_selector_flag",
    "ambiguity_intrinsic_in_carrier_quotient_flag",
]

OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "candidate_count": 0,
    "first_contact_edge_count": 1,
    "mixed_first_contact_edge_count": 2,
    "clean_first_contact_edge_count": 3,
    "mixed_first_contact_candidate_count": 4,
    "zero_overhead_mixed_candidate_count": 5,
    "pure_x2_zero_overhead_candidate_count": 6,
    "atom_level_x2_witness_candidate_count": 7,
    "mixed_edge_x5_cowitness_count": 8,
    "ambiguity_intrinsic_edge_count": 9,
    "carrier_mask_ambiguity_intrinsic_flag": 10,
    "zero_overhead_requires_atom_selector_flag": 11,
    "selected_candidate_id": 12,
    "selected_candidate_clean_carrier_edge_flag": 13,
    "x2_atom_id": 14,
    "x5_atom_id": 15,
}


def bit_ids(mask: int) -> list[int]:
    return [index for index in range(64) if int(mask) & (1 << index)]


def bitset(values: list[int]) -> int:
    output = 0
    for value in values:
        output |= 1 << int(value)
    return output


def shared_contact(edge: dict[str, int], atom_to_symbol: dict[int, int]) -> dict[str, Any]:
    shared_atoms = bit_ids(
        int(edge["source_carrier_atom_mask"]) & int(edge["target_carrier_atom_mask"])
    )
    shared_symbols = sorted({atom_to_symbol[atom_id] for atom_id in shared_atoms})
    return {
        "shared_atoms": shared_atoms,
        "shared_symbols": shared_symbols,
        "shared_atom_bitset": bitset(shared_atoms),
        "shared_symbol_bitset": bitset(shared_symbols),
    }


def build_payloads() -> dict[str, Any]:
    pareto_report = load_json(PARETO_REPORT)
    pareto = load_json(PARETO_JSON)
    pareto_certificate = load_json(PARETO_CERTIFICATE)
    x2_detour_report = load_json(X2_DETOUR_REPORT)
    x2_detour_certificate = load_json(X2_DETOUR_CERTIFICATE)
    cell_report = load_json(CELL_COMPLEX_REPORT)
    cell_certificate = load_json(CELL_COMPLEX_CERTIFICATE)
    symbolic_report = load_json(SYMBOLIC_REWRITE_REPORT)
    symbolic_certificate = load_json(SYMBOLIC_REWRITE_CERTIFICATE)

    pareto_tables = np.load(PARETO_TABLES, allow_pickle=False)
    x2_detour_tables = np.load(X2_DETOUR_TABLES, allow_pickle=False)
    cell_tables = np.load(CELL_COMPLEX_TABLES, allow_pickle=False)
    symbolic_tables = np.load(SYMBOLIC_REWRITE_TABLES, allow_pickle=False)
    pareto_candidate_table = np.asarray(
        pareto_tables["candidate_table"], dtype=np.int64
    )
    x2_detour_edge_table = np.asarray(x2_detour_tables["edge_table"], dtype=np.int64)
    cell_edge_table = np.asarray(cell_tables["carrier_region_edge_table"], dtype=np.int64)
    symbolic_alphabet_table = np.asarray(
        symbolic_tables["alphabet_table"], dtype=np.int64
    )

    candidate_rows = read_int_csv(PARETO_CANDIDATES)
    detour_edges = read_int_csv(X2_DETOUR_EDGES)
    cell_edges = read_int_csv(CELL_COMPLEX_EDGES)
    alphabet_rows = read_int_csv(SYMBOLIC_ALPHABET)

    alphabet_by_atom = {int(row["atom_id"]): row for row in alphabet_rows}
    atom_to_symbol = {
        int(row["atom_id"]): int(row["symbol_id"]) for row in alphabet_rows
    }
    detour_by_cell_edge = {int(row["cell_edge_id"]): row for row in detour_edges}
    cell_edge_by_id = {int(row["cell_edge_id"]): row for row in cell_edges}
    first_edge_ids = sorted({int(row["cell_edge_0_id"]) for row in candidate_rows})

    atom_contact_rows: list[dict[str, int]] = []
    edge_resolution_rows: list[dict[str, int]] = []
    for edge_id in first_edge_ids:
        edge = cell_edge_by_id[edge_id]
        contact = shared_contact(edge, atom_to_symbol)
        candidate_members = [
            row
            for row in candidate_rows
            if int(row["cell_edge_0_id"]) == edge_id
        ]
        x2_witness_count = sum(
            1 for atom_id in contact["shared_atoms"] if atom_to_symbol[atom_id] == X2_SYMBOL_ID
        )
        x5_cowitness_count = sum(
            1 for atom_id in contact["shared_atoms"] if atom_to_symbol[atom_id] == X5_SYMBOL_ID
        )
        detour = detour_by_cell_edge[edge_id]
        pure_x2 = int(
            x2_witness_count > 0
            and x5_cowitness_count == 0
            and int(detour["single_x2_flag"]) == 1
        )
        mixed = int(
            x2_witness_count > 0
            and x5_cowitness_count > 0
            and int(detour["mixed_x2_x5_flag"]) == 1
        )
        for atom_id in contact["shared_atoms"]:
            symbol_id = atom_to_symbol[atom_id]
            symbol_row = alphabet_by_atom[atom_id]
            atom_contact_rows.append(
                {
                    "atom_contact_id": len(atom_contact_rows),
                    "cell_edge_id": edge_id,
                    "source_carrier_mask_class_id": int(
                        edge["source_carrier_mask_class_id"]
                    ),
                    "target_carrier_mask_class_id": int(
                        edge["target_carrier_mask_class_id"]
                    ),
                    "source_carrier_atom_mask": int(edge["source_carrier_atom_mask"]),
                    "target_carrier_atom_mask": int(edge["target_carrier_atom_mask"]),
                    "shared_atom_id": atom_id,
                    "shared_symbol_id": symbol_id,
                    "shared_symbol_bitset": 1 << symbol_id,
                    "symbol_sector_mask": int(symbol_row["sector_mask"]),
                    "symbol_signature_class_count": int(
                        symbol_row["signature_class_count"]
                    ),
                    "x2_atom_witness_flag": int(symbol_id == X2_SYMBOL_ID),
                    "x5_atom_cowitness_flag": int(symbol_id == X5_SYMBOL_ID),
                }
            )
        edge_resolution_rows.append(
            {
                "first_contact_edge_id": edge_id,
                "candidate_count": len(candidate_members),
                "geodesic_candidate_count": sum(
                    int(row["geodesic_optimal_flag"]) for row in candidate_members
                ),
                "pareto_candidate_count": sum(
                    int(row["pareto_frontier_flag"]) for row in candidate_members
                ),
                "dominated_candidate_count": sum(
                    int(row["dominated_flag"]) for row in candidate_members
                ),
                "source_carrier_mask_class_id": int(
                    edge["source_carrier_mask_class_id"]
                ),
                "target_carrier_mask_class_id": int(
                    edge["target_carrier_mask_class_id"]
                ),
                "shared_atom_count": len(contact["shared_atoms"]),
                "shared_symbol_count": len(contact["shared_symbols"]),
                "x2_atom_witness_count": x2_witness_count,
                "x5_atom_cowitness_count": x5_cowitness_count,
                "shared_atom_bitset": int(contact["shared_atom_bitset"]),
                "shared_symbol_bitset": int(contact["shared_symbol_bitset"]),
                "carrier_mask_pure_x2_flag": pure_x2,
                "carrier_mask_mixed_x2_x5_flag": mixed,
                "atom_level_x2_witness_flag": int(x2_witness_count > 0),
                "requires_atom_selector_flag": int(mixed == 1),
                "ambiguity_intrinsic_in_carrier_quotient_flag": int(mixed == 1),
            }
        )

    edge_resolution_by_id = {
        int(row["first_contact_edge_id"]): row for row in edge_resolution_rows
    }
    candidate_resolution_rows: list[dict[str, int]] = []
    for candidate in candidate_rows:
        edge_id = int(candidate["cell_edge_0_id"])
        edge_row = edge_resolution_by_id[edge_id]
        candidate_resolution_rows.append(
            {
                "candidate_id": int(candidate["candidate_id"]),
                "rank_order": int(candidate["rank_order"]),
                "first_contact_edge_id": edge_id,
                "trace_detour_overhead": int(candidate["trace_detour_overhead"]),
                "signature_valley_depth": int(candidate["signature_valley_depth"]),
                "metric_gromov_delta_twice": int(
                    candidate["metric_gromov_delta_twice"]
                ),
                "typed_boundary_cost": int(candidate["typed_boundary_cost"]),
                "geodesic_optimal_flag": int(candidate["geodesic_optimal_flag"]),
                "pareto_frontier_flag": int(candidate["pareto_frontier_flag"]),
                "dominated_flag": int(candidate["dominated_flag"]),
                "carrier_mask_pure_x2_flag": int(
                    edge_row["carrier_mask_pure_x2_flag"]
                ),
                "carrier_mask_mixed_x2_x5_flag": int(
                    edge_row["carrier_mask_mixed_x2_x5_flag"]
                ),
                "atom_level_x2_witness_flag": int(
                    edge_row["atom_level_x2_witness_flag"]
                ),
                "atom_x5_cowitness_flag": int(edge_row["x5_atom_cowitness_count"] > 0),
                "requires_atom_selector_flag": int(
                    edge_row["requires_atom_selector_flag"]
                ),
                "ambiguity_intrinsic_in_carrier_quotient_flag": int(
                    edge_row["ambiguity_intrinsic_in_carrier_quotient_flag"]
                ),
            }
        )

    mixed_edge_rows = [
        row
        for row in edge_resolution_rows
        if int(row["carrier_mask_mixed_x2_x5_flag"]) == 1
    ]
    clean_edge_rows = [
        row
        for row in edge_resolution_rows
        if int(row["carrier_mask_pure_x2_flag"]) == 1
    ]
    zero_overhead_rows = [
        row for row in candidate_resolution_rows if int(row["trace_detour_overhead"]) == 0
    ]
    mixed_candidate_rows = [
        row
        for row in candidate_resolution_rows
        if int(row["carrier_mask_mixed_x2_x5_flag"]) == 1
    ]
    atom_x2_candidate_rows = [
        row
        for row in candidate_resolution_rows
        if int(row["atom_level_x2_witness_flag"]) == 1
    ]
    selected_row = next(
        row
        for row in candidate_resolution_rows
        if int(row["candidate_id"]) == SELECTED_CANDIDATE_ID
    )
    observable_values = {
        "candidate_count": len(candidate_resolution_rows),
        "first_contact_edge_count": len(edge_resolution_rows),
        "mixed_first_contact_edge_count": len(mixed_edge_rows),
        "clean_first_contact_edge_count": len(clean_edge_rows),
        "mixed_first_contact_candidate_count": len(mixed_candidate_rows),
        "zero_overhead_mixed_candidate_count": len(
            [
                row
                for row in zero_overhead_rows
                if int(row["carrier_mask_mixed_x2_x5_flag"]) == 1
            ]
        ),
        "pure_x2_zero_overhead_candidate_count": len(
            [
                row
                for row in zero_overhead_rows
                if int(row["carrier_mask_pure_x2_flag"]) == 1
            ]
        ),
        "atom_level_x2_witness_candidate_count": len(atom_x2_candidate_rows),
        "mixed_edge_x5_cowitness_count": len(
            [row for row in mixed_edge_rows if int(row["x5_atom_cowitness_count"]) > 0]
        ),
        "ambiguity_intrinsic_edge_count": len(
            [
                row
                for row in edge_resolution_rows
                if int(row["ambiguity_intrinsic_in_carrier_quotient_flag"]) == 1
            ]
        ),
        "carrier_mask_ambiguity_intrinsic_flag": int(len(mixed_edge_rows) == 2),
        "zero_overhead_requires_atom_selector_flag": int(
            all(int(row["requires_atom_selector_flag"]) == 1 for row in zero_overhead_rows)
        ),
        "selected_candidate_id": SELECTED_CANDIDATE_ID,
        "selected_candidate_clean_carrier_edge_flag": int(
            selected_row["carrier_mask_pure_x2_flag"]
        ),
        "x2_atom_id": X2_ATOM_ID,
        "x5_atom_id": X5_ATOM_ID,
    }
    observable_rows = [
        {
            "observable_id": code,
            "observable_code": code,
            "value_x1e12": int(observable_values[name]),
            "aux_id": -1,
        }
        for name, code in sorted(OBSERVABLE_CODES.items(), key=lambda item: item[1])
    ]

    atom_contact_table = table_from_rows(ATOM_CONTACT_COLUMNS, atom_contact_rows)
    edge_resolution_table = table_from_rows(EDGE_RESOLUTION_COLUMNS, edge_resolution_rows)
    candidate_resolution_table = table_from_rows(
        CANDIDATE_RESOLUTION_COLUMNS,
        candidate_resolution_rows,
    )
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    edge_shared_atom_map = {
        int(row["first_contact_edge_id"]): bit_ids(int(row["shared_atom_bitset"]))
        for row in edge_resolution_rows
    }
    candidate_requires_selector = [
        int(row["candidate_id"])
        for row in candidate_resolution_rows
        if int(row["requires_atom_selector_flag"]) == 1
    ]
    pure_x2_zero_overhead_candidates = [
        int(row["candidate_id"])
        for row in zero_overhead_rows
        if int(row["carrier_mask_pure_x2_flag"]) == 1
    ]

    checks = {
        "pareto_report_certified": pareto_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CYCLE_PARETO_FRONTIER_CERTIFIED",
        "pareto_certificate_certified": pareto_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CYCLE_PARETO_FRONTIER_CERTIFIED",
        "x2_detour_report_certified": x2_detour_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_X2_DETOUR_FAN_CERTIFIED",
        "x2_detour_certificate_certified": x2_detour_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_X2_DETOUR_FAN_CERTIFIED",
        "cell_complex_report_certified": cell_report.get("status")
        == "C985_D20_SIGNATURE_RESIDUAL_CELL_COMPLEX_CERTIFIED",
        "cell_complex_certificate_certified": cell_certificate.get("status")
        == "C985_D20_SIGNATURE_RESIDUAL_CELL_COMPLEX_CERTIFIED",
        "symbolic_rewrite_report_certified": symbolic_report.get("status")
        == "C985_D20_SYMBOLIC_REWRITE_RULES_CERTIFIED",
        "symbolic_rewrite_certificate_certified": symbolic_certificate.get("status")
        == "C985_D20_SYMBOLIC_REWRITE_RULES_CERTIFIED",
        "pareto_schema_available": pareto.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_cycle_pareto_frontier@1",
        "pareto_candidate_table_shape_is_10_by_25": tuple(
            pareto_candidate_table.shape
        )
        == (10, len(PARETO_CANDIDATE_COLUMNS)),
        "x2_detour_edge_table_shape_is_13_by_15": tuple(x2_detour_edge_table.shape)
        == (13, len(DETOUR_EDGE_COLUMNS)),
        "cell_complex_edge_table_shape_is_44_by_13": tuple(cell_edge_table.shape)
        == (44, 13),
        "symbolic_alphabet_table_shape_is_6_by_9": tuple(symbolic_alphabet_table.shape)
        == (6, len(ALPHABET_COLUMNS)),
        "x2_atom_mapping_is_atom_7": atom_to_symbol.get(X2_ATOM_ID) == X2_SYMBOL_ID,
        "x5_atom_mapping_is_atom_19": atom_to_symbol.get(X5_ATOM_ID) == X5_SYMBOL_ID,
        "first_contact_edges_are_14_39_41": first_edge_ids
        == [CLEAN_FIRST_EDGE_ID, *MIXED_FIRST_EDGE_IDS],
        "edge14_is_clean_atom_7_only": edge_shared_atom_map.get(CLEAN_FIRST_EDGE_ID)
        == [X2_ATOM_ID],
        "edge39_is_atom_7_and_19": edge_shared_atom_map.get(39)
        == [X2_ATOM_ID, X5_ATOM_ID],
        "edge41_is_atom_7_and_19": edge_shared_atom_map.get(41)
        == [X2_ATOM_ID, X5_ATOM_ID],
        "mixed_edges_have_x2_and_x5_cowitnesses": all(
            int(row["x2_atom_witness_count"]) == 1
            and int(row["x5_atom_cowitness_count"]) == 1
            for row in mixed_edge_rows
        ),
        "clean_edge_has_x2_without_x5_cowitness": len(clean_edge_rows) == 1
        and int(clean_edge_rows[0]["x2_atom_witness_count"]) == 1
        and int(clean_edge_rows[0]["x5_atom_cowitness_count"]) == 0,
        "zero_overhead_candidates_are_mixed_edges": [
            int(row["candidate_id"]) for row in zero_overhead_rows
        ]
        == ZERO_OVERHEAD_CANDIDATE_IDS
        and all(
            int(row["carrier_mask_mixed_x2_x5_flag"]) == 1
            for row in zero_overhead_rows
        ),
        "zero_overhead_has_no_carrier_pure_x2_candidate": pure_x2_zero_overhead_candidates
        == [],
        "all_candidates_have_atom_level_x2_witness": len(atom_x2_candidate_rows) == 10,
        "mixed_candidates_require_atom_selector": candidate_requires_selector
        == [0, 1, 2, 3, 4, 5, 7, 9],
        "selected_candidate_is_clean_without_selector": int(
            selected_row["candidate_id"]
        )
        == SELECTED_CANDIDATE_ID
        and int(selected_row["carrier_mask_pure_x2_flag"]) == 1
        and int(selected_row["requires_atom_selector_flag"]) == 0,
        "atom_contact_table_shape_is_5_by_13": tuple(atom_contact_table.shape)
        == (5, len(ATOM_CONTACT_COLUMNS)),
        "edge_resolution_table_shape_is_3_by_18": tuple(edge_resolution_table.shape)
        == (3, len(EDGE_RESOLUTION_COLUMNS)),
        "candidate_resolution_table_shape_is_10_by_16": tuple(
            candidate_resolution_table.shape
        )
        == (10, len(CANDIDATE_RESOLUTION_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    witness = {
        "first_contact_edges": first_edge_ids,
        "mixed_first_contact_edges": MIXED_FIRST_EDGE_IDS,
        "clean_first_contact_edge": CLEAN_FIRST_EDGE_ID,
        "edge_shared_atom_map": {
            str(edge_id): edge_shared_atom_map[edge_id] for edge_id in first_edge_ids
        },
        "zero_overhead_candidate_ids": ZERO_OVERHEAD_CANDIDATE_IDS,
        "candidate_ids_requiring_atom_selector": candidate_requires_selector,
        "pure_x2_zero_overhead_candidate_ids": pure_x2_zero_overhead_candidates,
        "selected_clean_candidate_id": SELECTED_CANDIDATE_ID,
        "atom_level_reading": {
            "x2_atom_id": X2_ATOM_ID,
            "x5_atom_id": X5_ATOM_ID,
            "carrier_mask_quotient_ambiguity": True,
            "x2_atom_witness_exists_on_mixed_edges": True,
            "x5_cowitness_exists_on_mixed_edges": True,
        },
        "atom_contact_table_sha256": sha_array(atom_contact_table),
        "edge_resolution_table_sha256": sha_array(edge_resolution_table),
        "candidate_resolution_table_sha256": sha_array(candidate_resolution_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    mixed_contact_atoms = {
        "schema": "c985.d20_signature_boundary_spine_aperture_mixed_contact_atoms@1",
        "object": "d20",
        "atom_resolution_rule": {
            "question": (
                "whether the mixed x2/x5 first contacts that support the "
                "zero-overhead aperture cycles can be read as pure x2"
            ),
            "answer": (
                "they contain an atom-level x2 witness, atom 7, but the "
                "carrier-mask contact also contains an x5 co-witness, atom 19"
            ),
            "quotient_boundary": (
                "without adding an atom selector, carrier-mask edges 39 and "
                "41 remain intrinsically mixed x2/x5 contacts"
            ),
        },
        "mixed_first_contact_edges": MIXED_FIRST_EDGE_IDS,
        "clean_first_contact_edge": CLEAN_FIRST_EDGE_ID,
        "candidate_ids_requiring_atom_selector": candidate_requires_selector,
        "summary": observable_values,
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_mixed_contact_atoms_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_MIXED_CONTACT_ATOMS_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "each zero-overhead aperture cycle has a first contact on carrier-mask edge 39 or 41",
            "edges 39 and 41 both share atom 7, the x2 atom, so an atom-level x2 witness exists",
            "the same edges also share atom 19, the x5 atom, so the carrier-mask quotient does not resolve them to pure x2",
            "the clean selected candidate uses edge 14, whose shared atom set is exactly atom 7",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_mixed_contact_atoms@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The zero-overhead aperture cycles can be given atom-level x2 "
            "witnesses on edges 39 and 41, but those same carrier-mask "
            "contacts also carry x5 atom 19. Thus pure x2 resolution requires "
            "an atom selector; the carrier-mask quotient itself remains mixed."
        ),
        "stage_protocol": {
            "draft": "audit the first-contact carrier edges used by the Pareto-ranked aperture cycles",
            "witness": "materialize shared atom ids, symbol ids, and candidate selector requirements",
            "coherence": "compare atom-level x2 witnesses with carrier-mask clean versus mixed classifications",
            "closure": "certify quotient-level ambiguity without claiming an atom-selector refinement yet",
            "emit": "emit mixed-contact atom JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "pareto_report": input_entry(
                PARETO_REPORT,
                {
                    "status": pareto_report.get("status"),
                    "certificate_sha256": pareto_report.get("certificate_sha256"),
                },
            ),
            "pareto_json": input_entry(PARETO_JSON),
            "pareto_candidates": input_entry(PARETO_CANDIDATES),
            "pareto_tables": input_entry(PARETO_TABLES),
            "pareto_certificate": input_entry(PARETO_CERTIFICATE),
            "x2_detour_report": input_entry(
                X2_DETOUR_REPORT,
                {
                    "status": x2_detour_report.get("status"),
                    "certificate_sha256": x2_detour_report.get(
                        "certificate_sha256"
                    ),
                },
            ),
            "x2_detour_edges": input_entry(X2_DETOUR_EDGES),
            "x2_detour_tables": input_entry(X2_DETOUR_TABLES),
            "x2_detour_certificate": input_entry(X2_DETOUR_CERTIFICATE),
            "cell_complex_report": input_entry(
                CELL_COMPLEX_REPORT,
                {
                    "status": cell_report.get("status"),
                    "certificate_sha256": cell_report.get("certificate_sha256"),
                },
            ),
            "cell_complex_edges": input_entry(CELL_COMPLEX_EDGES),
            "cell_complex_tables": input_entry(CELL_COMPLEX_TABLES),
            "cell_complex_certificate": input_entry(CELL_COMPLEX_CERTIFICATE),
            "symbolic_rewrite_report": input_entry(
                SYMBOLIC_REWRITE_REPORT,
                {
                    "status": symbolic_report.get("status"),
                    "certificate_sha256": symbolic_report.get(
                        "certificate_sha256"
                    ),
                },
            ),
            "symbolic_alphabet": input_entry(SYMBOLIC_ALPHABET),
            "symbolic_rewrite_tables": input_entry(SYMBOLIC_REWRITE_TABLES),
            "symbolic_rewrite_certificate": input_entry(SYMBOLIC_REWRITE_CERTIFICATE),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_aperture_mixed_contact_atoms": relpath(
                OUT_DIR / "signature_boundary_spine_aperture_mixed_contact_atoms.json"
            ),
            "aperture_mixed_contact_atom_witnesses_csv": relpath(
                OUT_DIR / "aperture_mixed_contact_atom_witnesses.csv"
            ),
            "aperture_first_contact_edge_resolution_csv": relpath(
                OUT_DIR / "aperture_first_contact_edge_resolution.csv"
            ),
            "aperture_candidate_atom_resolution_csv": relpath(
                OUT_DIR / "aperture_candidate_atom_resolution.csv"
            ),
            "aperture_mixed_contact_atom_observables_csv": relpath(
                OUT_DIR / "aperture_mixed_contact_atom_observables.csv"
            ),
            "signature_boundary_spine_aperture_mixed_contact_atoms_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_mixed_contact_atoms_tables.npz"
            ),
            "signature_boundary_spine_aperture_mixed_contact_atoms_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_mixed_contact_atoms_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the atom-level shared-contact decomposition for first-contact edges 14, 39, and 41",
                "that every ranked aperture candidate has an atom-level x2 first-contact witness",
                "that zero-overhead candidates require atom selection because their carrier-mask contact also carries x5",
                "that selected candidate 6 is carrier-mask pure x2 on first contact edge 14",
            ],
            "does_not_certify_because_not_required": [
                "a new atom-refined carrier graph",
                "that an atom selector preserves all downstream carrier-cycle metrics",
                "a pure-x2 carrier-mask geodesic candidate",
                "new categorical F-symbols, pivotality, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Build the atom-selector refinement for the zero-overhead class: "
            "split edges 39 and 41 into atom-contact transitions, force the "
            "first atom to x2, and test whether the resulting atom-selected "
            "cycle preserves the geodesic trace without x5 leakage."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_mixed_contact_atoms_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified Pareto, x2-detour, residual cell-complex, and symbolic-alphabet artifacts",
            "extract first-contact carrier-mask edges for every ranked aperture candidate",
            "decompose each first contact into shared atom and symbol witnesses",
            "distinguish atom-level x2 witnesses from carrier-mask pure x2 contacts",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_mixed_contact_atoms": mixed_contact_atoms,
        "aperture_mixed_contact_atom_witnesses_csv": csv_text(
            ATOM_CONTACT_COLUMNS,
            atom_contact_rows,
        ),
        "aperture_first_contact_edge_resolution_csv": csv_text(
            EDGE_RESOLUTION_COLUMNS,
            edge_resolution_rows,
        ),
        "aperture_candidate_atom_resolution_csv": csv_text(
            CANDIDATE_RESOLUTION_COLUMNS,
            candidate_resolution_rows,
        ),
        "aperture_mixed_contact_atom_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "atom_contact_table": atom_contact_table,
        "edge_resolution_table": edge_resolution_table,
        "candidate_resolution_table": candidate_resolution_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_mixed_contact_atoms_certificate": certificate,
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
        OUT_DIR / "signature_boundary_spine_aperture_mixed_contact_atoms.json",
        payloads["signature_boundary_spine_aperture_mixed_contact_atoms"],
    )
    (OUT_DIR / "aperture_mixed_contact_atom_witnesses.csv").write_text(
        payloads["aperture_mixed_contact_atom_witnesses_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_first_contact_edge_resolution.csv").write_text(
        payloads["aperture_first_contact_edge_resolution_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_candidate_atom_resolution.csv").write_text(
        payloads["aperture_candidate_atom_resolution_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_mixed_contact_atom_observables.csv").write_text(
        payloads["aperture_mixed_contact_atom_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_boundary_spine_aperture_mixed_contact_atoms_tables.npz",
        atom_contact_table=payloads["atom_contact_table"],
        edge_resolution_table=payloads["edge_resolution_table"],
        candidate_resolution_table=payloads["candidate_resolution_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR / "signature_boundary_spine_aperture_mixed_contact_atoms_certificate.json",
        payloads["signature_boundary_spine_aperture_mixed_contact_atoms_certificate"],
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
                "edge_shared_atom_map": witness["edge_shared_atom_map"],
                "candidate_ids_requiring_atom_selector": witness[
                    "candidate_ids_requiring_atom_selector"
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
