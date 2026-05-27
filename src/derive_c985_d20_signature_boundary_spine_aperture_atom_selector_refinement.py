from __future__ import annotations

import json
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_cycle_ranking import (
        CANDIDATE_COLUMNS as RANKING_CANDIDATE_COLUMNS,
        OUT_DIR as RANKING_DIR,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_mixed_contact_atoms import (
        CANDIDATE_RESOLUTION_COLUMNS as MIXED_CANDIDATE_COLUMNS,
        OUT_DIR as MIXED_CONTACT_DIR,
    )
    from .derive_c985_d20_signature_boundary_spine_routing_prefix import (
        read_int_csv,
        table_from_rows,
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
    from derive_c985_d20_signature_boundary_spine_aperture_cycle_ranking import (
        CANDIDATE_COLUMNS as RANKING_CANDIDATE_COLUMNS,
        OUT_DIR as RANKING_DIR,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_mixed_contact_atoms import (
        CANDIDATE_RESOLUTION_COLUMNS as MIXED_CANDIDATE_COLUMNS,
        OUT_DIR as MIXED_CONTACT_DIR,
    )
    from derive_c985_d20_signature_boundary_spine_routing_prefix import (
        read_int_csv,
        table_from_rows,
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


THEOREM_ID = "c985_d20_signature_boundary_spine_aperture_atom_selector_refinement"
STATUS = "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_ATOM_SELECTOR_REFINEMENT_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

MIXED_CONTACT_REPORT = MIXED_CONTACT_DIR / "report.json"
MIXED_CONTACT_JSON = (
    MIXED_CONTACT_DIR / "signature_boundary_spine_aperture_mixed_contact_atoms.json"
)
MIXED_CONTACT_CANDIDATES = MIXED_CONTACT_DIR / "aperture_candidate_atom_resolution.csv"
MIXED_CONTACT_EDGES = MIXED_CONTACT_DIR / "aperture_first_contact_edge_resolution.csv"
MIXED_CONTACT_TABLES = (
    MIXED_CONTACT_DIR / "signature_boundary_spine_aperture_mixed_contact_atoms_tables.npz"
)
MIXED_CONTACT_CERTIFICATE = (
    MIXED_CONTACT_DIR / "signature_boundary_spine_aperture_mixed_contact_atoms_certificate.json"
)

RANKING_REPORT = RANKING_DIR / "report.json"
RANKING_JSON = RANKING_DIR / "signature_boundary_spine_aperture_cycle_ranking.json"
RANKING_CANDIDATES = RANKING_DIR / "aperture_cycle_ranked_candidates.csv"
RANKING_TABLES = RANKING_DIR / "signature_boundary_spine_aperture_cycle_ranking_tables.npz"
RANKING_CERTIFICATE = (
    RANKING_DIR / "signature_boundary_spine_aperture_cycle_ranking_certificate.json"
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
    / "derive_c985_d20_signature_boundary_spine_aperture_atom_selector_refinement.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_atom_selector_refinement.py"
)

X2_ATOM_ID = 7
X5_ATOM_ID = 19
SELECTED_ATOM_WORD = [7, 19, 12, 11]
SELECTED_SYMBOL_WORD = [2, 5, 4, 3]
ZERO_OVERHEAD_CANDIDATE_IDS = [0, 1, 2, 3, 4, 5]
ZERO_OVERHEAD_FIRST_EDGE_IDS = [39, 41]
ZERO_OVERHEAD_WINDOW_NODES = [44, 50, 41, 42]

SELECTOR_STEP_COLUMNS = [
    "candidate_id",
    "step_rank",
    "source_carrier_mask_class_id",
    "target_carrier_mask_class_id",
    "cell_edge_id",
    "carrier_shared_atom_bitset",
    "carrier_shared_symbol_bitset",
    "carrier_shared_atom_count",
    "carrier_shared_symbol_count",
    "ranked_symbol_id",
    "selected_atom_id",
    "selected_symbol_id",
    "selected_atom_bitset",
    "unselected_atom_bitset",
    "selected_atom_in_shared_contact_flag",
    "selected_symbol_matches_ranked_symbol_flag",
    "selector_required_flag",
    "first_contact_flag",
    "selected_x2_first_contact_flag",
    "selected_x5_first_contact_leakage_flag",
    "unselected_x5_first_contact_cowitness_flag",
    "intended_x5_second_step_flag",
]

SELECTOR_CANDIDATE_COLUMNS = [
    "candidate_id",
    "rank_order",
    "carrier_0_id",
    "carrier_1_id",
    "carrier_2_id",
    "carrier_3_id",
    "carrier_4_id",
    "cell_edge_0_id",
    "cell_edge_1_id",
    "cell_edge_2_id",
    "cell_edge_3_id",
    "selected_atom_0_id",
    "selected_atom_1_id",
    "selected_atom_2_id",
    "selected_atom_3_id",
    "selected_symbol_0_id",
    "selected_symbol_1_id",
    "selected_symbol_2_id",
    "selected_symbol_3_id",
    "cycle_window_node_0_id",
    "cycle_window_node_1_id",
    "cycle_window_node_2_id",
    "cycle_window_node_3_id",
    "trace_detour_overhead",
    "signature_valley_depth",
    "metric_gromov_delta_twice",
    "trace_signature_total_variation",
    "first_contact_shared_atom_bitset",
    "first_contact_selected_atom_bitset",
    "first_contact_unselected_atom_bitset",
    "first_contact_x5_cowitness_flag",
    "first_contact_selected_x5_leakage_flag",
    "atom_selector_required_flag",
    "atom_word_matches_ranked_symbols_flag",
    "geodesic_trace_preserved_flag",
    "x5_intended_second_step_flag",
    "forgetful_projection_mixed_flag",
]

OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "selector_candidate_count": 0,
    "selector_step_count": 1,
    "first_selector_required_count": 2,
    "first_x2_selected_count": 3,
    "first_selected_x5_leakage_count": 4,
    "first_unselected_x5_cowitness_count": 5,
    "intended_second_x5_step_count": 6,
    "distinct_selected_atom_word_count": 7,
    "distinct_selected_symbol_word_count": 8,
    "geodesic_trace_preserved_count": 9,
    "zero_overhead_preserved_count": 10,
    "carrier_mask_pure_zero_overhead_count": 11,
    "forgetful_projection_mixed_count": 12,
    "selected_atom_word_code": 13,
    "selected_symbol_word_code": 14,
}


def bit_ids(mask: int) -> list[int]:
    return [index for index in range(64) if int(mask) & (1 << index)]


def bitset(values: list[int]) -> int:
    output = 0
    for value in values:
        output |= 1 << int(value)
    return output


def word_code(values: list[int]) -> int:
    output = 0
    for value in values:
        output = output * 100 + int(value)
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


def select_atom_for_symbol(
    shared_atoms: list[int],
    atom_to_symbol: dict[int, int],
    symbol_id: int,
) -> int:
    matching = [
        atom_id
        for atom_id in shared_atoms
        if int(atom_to_symbol[atom_id]) == int(symbol_id)
    ]
    if len(matching) != 1:
        raise AssertionError(
            f"expected one atom for symbol {symbol_id}, found {matching}"
        )
    return matching[0]


def build_payloads() -> dict[str, Any]:
    mixed_report = load_json(MIXED_CONTACT_REPORT)
    mixed_contact = load_json(MIXED_CONTACT_JSON)
    mixed_certificate = load_json(MIXED_CONTACT_CERTIFICATE)
    ranking_report = load_json(RANKING_REPORT)
    ranking = load_json(RANKING_JSON)
    ranking_certificate = load_json(RANKING_CERTIFICATE)
    cell_report = load_json(CELL_COMPLEX_REPORT)
    cell_certificate = load_json(CELL_COMPLEX_CERTIFICATE)
    symbolic_report = load_json(SYMBOLIC_REWRITE_REPORT)
    symbolic_certificate = load_json(SYMBOLIC_REWRITE_CERTIFICATE)

    mixed_tables = np.load(MIXED_CONTACT_TABLES, allow_pickle=False)
    ranking_tables = np.load(RANKING_TABLES, allow_pickle=False)
    cell_tables = np.load(CELL_COMPLEX_TABLES, allow_pickle=False)
    symbolic_tables = np.load(SYMBOLIC_REWRITE_TABLES, allow_pickle=False)
    mixed_candidate_table = np.asarray(
        mixed_tables["candidate_resolution_table"], dtype=np.int64
    )
    ranking_candidate_table = np.asarray(
        ranking_tables["candidate_table"], dtype=np.int64
    )
    cell_edge_table = np.asarray(cell_tables["carrier_region_edge_table"], dtype=np.int64)
    symbolic_alphabet_table = np.asarray(
        symbolic_tables["alphabet_table"], dtype=np.int64
    )

    mixed_candidate_rows = read_int_csv(MIXED_CONTACT_CANDIDATES)
    mixed_edge_rows = read_int_csv(MIXED_CONTACT_EDGES)
    ranking_rows = read_int_csv(RANKING_CANDIDATES)
    cell_edges = read_int_csv(CELL_COMPLEX_EDGES)
    alphabet_rows = read_int_csv(SYMBOLIC_ALPHABET)

    atom_to_symbol = {
        int(row["atom_id"]): int(row["symbol_id"]) for row in alphabet_rows
    }
    cell_edge_by_id = {int(row["cell_edge_id"]): row for row in cell_edges}
    mixed_candidate_by_id = {
        int(row["candidate_id"]): row for row in mixed_candidate_rows
    }
    mixed_edge_by_id = {
        int(row["first_contact_edge_id"]): row for row in mixed_edge_rows
    }
    zero_overhead_rows = [
        row
        for row in ranking_rows
        if int(row["candidate_id"]) in ZERO_OVERHEAD_CANDIDATE_IDS
    ]

    step_rows: list[dict[str, int]] = []
    candidate_rows: list[dict[str, int]] = []
    for ranking_row in zero_overhead_rows:
        candidate_id = int(ranking_row["candidate_id"])
        selected_atoms: list[int] = []
        selected_symbols: list[int] = []
        first_contact_shared_atom_bitset = 0
        first_contact_unselected_atom_bitset = 0
        first_contact_selected_atom_bitset = 0
        first_contact_x5_cowitness_flag = 0
        first_contact_selected_x5_leakage_flag = 0
        atom_selector_required_flag = 0
        x5_intended_second_step_flag = 0
        for step_rank in range(4):
            source_carrier = int(ranking_row[f"carrier_{step_rank}_id"])
            target_carrier = int(ranking_row[f"carrier_{step_rank + 1}_id"])
            cell_edge_id = int(ranking_row[f"cell_edge_{step_rank}_id"])
            ranked_symbol_id = int(ranking_row[f"symbol_{step_rank}_id"])
            contact = shared_contact(cell_edge_by_id[cell_edge_id], atom_to_symbol)
            selected_atom_id = select_atom_for_symbol(
                contact["shared_atoms"],
                atom_to_symbol,
                ranked_symbol_id,
            )
            selected_symbol_id = atom_to_symbol[selected_atom_id]
            selected_atoms.append(selected_atom_id)
            selected_symbols.append(selected_symbol_id)
            unselected_atoms = [
                atom_id
                for atom_id in contact["shared_atoms"]
                if atom_id != selected_atom_id
            ]
            first_contact = int(step_rank == 0)
            selector_required = int(len(contact["shared_atoms"]) > 1)
            selected_x5_first_leakage = int(
                first_contact and selected_atom_id == X5_ATOM_ID
            )
            unselected_x5_first_cowitness = int(
                first_contact and X5_ATOM_ID in unselected_atoms
            )
            intended_x5_second_step = int(
                step_rank == 1
                and selected_atom_id == X5_ATOM_ID
                and selected_symbol_id == 5
            )
            if first_contact:
                first_contact_shared_atom_bitset = int(contact["shared_atom_bitset"])
                first_contact_selected_atom_bitset = 1 << selected_atom_id
                first_contact_unselected_atom_bitset = bitset(unselected_atoms)
                first_contact_x5_cowitness_flag = unselected_x5_first_cowitness
                first_contact_selected_x5_leakage_flag = selected_x5_first_leakage
                atom_selector_required_flag = selector_required
            if intended_x5_second_step:
                x5_intended_second_step_flag = 1
            step_rows.append(
                {
                    "candidate_id": candidate_id,
                    "step_rank": step_rank,
                    "source_carrier_mask_class_id": source_carrier,
                    "target_carrier_mask_class_id": target_carrier,
                    "cell_edge_id": cell_edge_id,
                    "carrier_shared_atom_bitset": int(contact["shared_atom_bitset"]),
                    "carrier_shared_symbol_bitset": int(contact["shared_symbol_bitset"]),
                    "carrier_shared_atom_count": len(contact["shared_atoms"]),
                    "carrier_shared_symbol_count": len(contact["shared_symbols"]),
                    "ranked_symbol_id": ranked_symbol_id,
                    "selected_atom_id": selected_atom_id,
                    "selected_symbol_id": selected_symbol_id,
                    "selected_atom_bitset": 1 << selected_atom_id,
                    "unselected_atom_bitset": bitset(unselected_atoms),
                    "selected_atom_in_shared_contact_flag": int(
                        selected_atom_id in contact["shared_atoms"]
                    ),
                    "selected_symbol_matches_ranked_symbol_flag": int(
                        selected_symbol_id == ranked_symbol_id
                    ),
                    "selector_required_flag": selector_required,
                    "first_contact_flag": first_contact,
                    "selected_x2_first_contact_flag": int(
                        first_contact and selected_atom_id == X2_ATOM_ID
                    ),
                    "selected_x5_first_contact_leakage_flag": selected_x5_first_leakage,
                    "unselected_x5_first_contact_cowitness_flag": (
                        unselected_x5_first_cowitness
                    ),
                    "intended_x5_second_step_flag": intended_x5_second_step,
                }
            )

        cycle_windows = [
            int(ranking_row[f"cycle_window_node_{index}_id"]) for index in range(4)
        ]
        geodesic_preserved = int(
            selected_atoms == SELECTED_ATOM_WORD
            and selected_symbols == SELECTED_SYMBOL_WORD
            and cycle_windows == ZERO_OVERHEAD_WINDOW_NODES
            and int(ranking_row["trace_detour_overhead"]) == 0
            and int(ranking_row["signature_valley_depth"]) == 0
            and int(ranking_row["metric_gromov_delta_twice"]) == 0
            and int(ranking_row["geodesic_equivalent_flag"]) == 1
        )
        mixed_candidate = mixed_candidate_by_id[candidate_id]
        candidate_rows.append(
            {
                "candidate_id": candidate_id,
                "rank_order": int(ranking_row["rank_order"]),
                "carrier_0_id": int(ranking_row["carrier_0_id"]),
                "carrier_1_id": int(ranking_row["carrier_1_id"]),
                "carrier_2_id": int(ranking_row["carrier_2_id"]),
                "carrier_3_id": int(ranking_row["carrier_3_id"]),
                "carrier_4_id": int(ranking_row["carrier_4_id"]),
                "cell_edge_0_id": int(ranking_row["cell_edge_0_id"]),
                "cell_edge_1_id": int(ranking_row["cell_edge_1_id"]),
                "cell_edge_2_id": int(ranking_row["cell_edge_2_id"]),
                "cell_edge_3_id": int(ranking_row["cell_edge_3_id"]),
                "selected_atom_0_id": selected_atoms[0],
                "selected_atom_1_id": selected_atoms[1],
                "selected_atom_2_id": selected_atoms[2],
                "selected_atom_3_id": selected_atoms[3],
                "selected_symbol_0_id": selected_symbols[0],
                "selected_symbol_1_id": selected_symbols[1],
                "selected_symbol_2_id": selected_symbols[2],
                "selected_symbol_3_id": selected_symbols[3],
                "cycle_window_node_0_id": cycle_windows[0],
                "cycle_window_node_1_id": cycle_windows[1],
                "cycle_window_node_2_id": cycle_windows[2],
                "cycle_window_node_3_id": cycle_windows[3],
                "trace_detour_overhead": int(ranking_row["trace_detour_overhead"]),
                "signature_valley_depth": int(ranking_row["signature_valley_depth"]),
                "metric_gromov_delta_twice": int(
                    ranking_row["metric_gromov_delta_twice"]
                ),
                "trace_signature_total_variation": int(
                    ranking_row["trace_signature_total_variation"]
                ),
                "first_contact_shared_atom_bitset": first_contact_shared_atom_bitset,
                "first_contact_selected_atom_bitset": first_contact_selected_atom_bitset,
                "first_contact_unselected_atom_bitset": (
                    first_contact_unselected_atom_bitset
                ),
                "first_contact_x5_cowitness_flag": first_contact_x5_cowitness_flag,
                "first_contact_selected_x5_leakage_flag": (
                    first_contact_selected_x5_leakage_flag
                ),
                "atom_selector_required_flag": atom_selector_required_flag,
                "atom_word_matches_ranked_symbols_flag": int(
                    selected_symbols
                    == [int(ranking_row[f"symbol_{index}_id"]) for index in range(4)]
                ),
                "geodesic_trace_preserved_flag": geodesic_preserved,
                "x5_intended_second_step_flag": x5_intended_second_step_flag,
                "forgetful_projection_mixed_flag": int(
                    mixed_candidate["carrier_mask_mixed_x2_x5_flag"]
                ),
            }
        )

    selected_atom_words = {
        tuple(int(row[f"selected_atom_{index}_id"]) for index in range(4))
        for row in candidate_rows
    }
    selected_symbol_words = {
        tuple(int(row[f"selected_symbol_{index}_id"]) for index in range(4))
        for row in candidate_rows
    }
    observable_values = {
        "selector_candidate_count": len(candidate_rows),
        "selector_step_count": len(step_rows),
        "first_selector_required_count": sum(
            int(row["atom_selector_required_flag"]) for row in candidate_rows
        ),
        "first_x2_selected_count": sum(
            int(row["selected_x2_first_contact_flag"])
            for row in step_rows
            if int(row["first_contact_flag"]) == 1
        ),
        "first_selected_x5_leakage_count": sum(
            int(row["selected_x5_first_contact_leakage_flag"])
            for row in step_rows
        ),
        "first_unselected_x5_cowitness_count": sum(
            int(row["unselected_x5_first_contact_cowitness_flag"])
            for row in step_rows
        ),
        "intended_second_x5_step_count": sum(
            int(row["intended_x5_second_step_flag"]) for row in step_rows
        ),
        "distinct_selected_atom_word_count": len(selected_atom_words),
        "distinct_selected_symbol_word_count": len(selected_symbol_words),
        "geodesic_trace_preserved_count": sum(
            int(row["geodesic_trace_preserved_flag"]) for row in candidate_rows
        ),
        "zero_overhead_preserved_count": sum(
            int(row["trace_detour_overhead"] == 0) for row in candidate_rows
        ),
        "carrier_mask_pure_zero_overhead_count": sum(
            1
            for row in candidate_rows
            if int(row["first_contact_x5_cowitness_flag"]) == 0
        ),
        "forgetful_projection_mixed_count": sum(
            int(row["forgetful_projection_mixed_flag"]) for row in candidate_rows
        ),
        "selected_atom_word_code": word_code(SELECTED_ATOM_WORD),
        "selected_symbol_word_code": word_code(SELECTED_SYMBOL_WORD),
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

    selector_step_table = table_from_rows(SELECTOR_STEP_COLUMNS, step_rows)
    selector_candidate_table = table_from_rows(
        SELECTOR_CANDIDATE_COLUMNS,
        candidate_rows,
    )
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    candidate_edge_cycles = [
        [int(row[f"cell_edge_{index}_id"]) for index in range(4)]
        for row in candidate_rows
    ]
    candidate_carrier_cycles = [
        [int(row[f"carrier_{index}_id"]) for index in range(5)]
        for row in candidate_rows
    ]
    first_edges = sorted({int(row["cell_edge_0_id"]) for row in candidate_rows})

    checks = {
        "mixed_contact_report_certified": mixed_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_MIXED_CONTACT_ATOMS_CERTIFIED",
        "mixed_contact_certificate_certified": mixed_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_MIXED_CONTACT_ATOMS_CERTIFIED",
        "ranking_report_certified": ranking_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CYCLE_RANKING_CERTIFIED",
        "ranking_certificate_certified": ranking_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CYCLE_RANKING_CERTIFIED",
        "cell_complex_report_certified": cell_report.get("status")
        == "C985_D20_SIGNATURE_RESIDUAL_CELL_COMPLEX_CERTIFIED",
        "cell_complex_certificate_certified": cell_certificate.get("status")
        == "C985_D20_SIGNATURE_RESIDUAL_CELL_COMPLEX_CERTIFIED",
        "symbolic_rewrite_report_certified": symbolic_report.get("status")
        == "C985_D20_SYMBOLIC_REWRITE_RULES_CERTIFIED",
        "symbolic_rewrite_certificate_certified": symbolic_certificate.get("status")
        == "C985_D20_SYMBOLIC_REWRITE_RULES_CERTIFIED",
        "mixed_contact_schema_available": mixed_contact.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_mixed_contact_atoms@1",
        "ranking_schema_available": ranking.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_cycle_ranking@1",
        "mixed_candidate_table_shape_is_10_by_16": tuple(
            mixed_candidate_table.shape
        )
        == (10, len(MIXED_CANDIDATE_COLUMNS)),
        "ranking_candidate_table_shape_is_10_by_34": tuple(
            ranking_candidate_table.shape
        )
        == (10, len(RANKING_CANDIDATE_COLUMNS)),
        "cell_complex_edge_table_shape_is_44_by_13": tuple(cell_edge_table.shape)
        == (44, 13),
        "symbolic_alphabet_table_shape_is_6_by_9": tuple(symbolic_alphabet_table.shape)
        == (6, len(ALPHABET_COLUMNS)),
        "zero_overhead_candidate_ids_match": [
            int(row["candidate_id"]) for row in candidate_rows
        ]
        == ZERO_OVERHEAD_CANDIDATE_IDS,
        "zero_overhead_first_edges_are_39_and_41": first_edges
        == ZERO_OVERHEAD_FIRST_EDGE_IDS,
        "all_selected_atom_words_are_7_19_12_11": selected_atom_words
        == {tuple(SELECTED_ATOM_WORD)},
        "all_selected_symbol_words_are_2_5_4_3": selected_symbol_words
        == {tuple(SELECTED_SYMBOL_WORD)},
        "all_first_contacts_select_x2_atom_7": [
            int(row["selected_atom_0_id"]) for row in candidate_rows
        ]
        == [X2_ATOM_ID] * 6,
        "all_first_contacts_keep_unselected_x5_cowitness": [
            int(row["first_contact_unselected_atom_bitset"]) for row in candidate_rows
        ]
        == [1 << X5_ATOM_ID] * 6,
        "no_first_contact_selected_x5_leakage": all(
            int(row["first_contact_selected_x5_leakage_flag"]) == 0
            for row in candidate_rows
        ),
        "all_second_steps_are_intended_x5": all(
            int(row["x5_intended_second_step_flag"]) == 1 for row in candidate_rows
        ),
        "all_atom_words_match_ranked_symbols": all(
            int(row["atom_word_matches_ranked_symbols_flag"]) == 1
            for row in candidate_rows
        ),
        "all_geodesic_traces_preserved": all(
            int(row["geodesic_trace_preserved_flag"]) == 1 for row in candidate_rows
        ),
        "forgetful_projection_remains_mixed": all(
            int(row["forgetful_projection_mixed_flag"]) == 1
            for row in candidate_rows
        ),
        "zero_overhead_cycle_windows_match": all(
            [int(row[f"cycle_window_node_{index}_id"]) for index in range(4)]
            == ZERO_OVERHEAD_WINDOW_NODES
            for row in candidate_rows
        ),
        "selector_step_table_shape_is_24_by_22": tuple(selector_step_table.shape)
        == (24, len(SELECTOR_STEP_COLUMNS)),
        "selector_candidate_table_shape_is_6_by_37": tuple(
            selector_candidate_table.shape
        )
        == (6, len(SELECTOR_CANDIDATE_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    witness = {
        "selector_candidate_ids": [int(row["candidate_id"]) for row in candidate_rows],
        "candidate_edge_cycles": candidate_edge_cycles,
        "candidate_carrier_cycles": candidate_carrier_cycles,
        "selected_atom_word": SELECTED_ATOM_WORD,
        "selected_symbol_word": SELECTED_SYMBOL_WORD,
        "cycle_window_nodes": ZERO_OVERHEAD_WINDOW_NODES,
        "first_contact_reading": {
            "selected_atom_id": X2_ATOM_ID,
            "selected_symbol_id": 2,
            "unselected_cowitness_atom_id": X5_ATOM_ID,
            "unselected_cowitness_symbol_id": 5,
            "selected_x5_leakage_count": observable_values[
                "first_selected_x5_leakage_count"
            ],
            "forgetful_projection_remains_mixed": True,
        },
        "geodesic_metrics": {
            "trace_detour_overhead": 0,
            "signature_valley_depth": 0,
            "metric_gromov_delta": 0.0,
            "trace_signature_total_variation": 53,
        },
        "selector_step_table_sha256": sha_array(selector_step_table),
        "selector_candidate_table_sha256": sha_array(selector_candidate_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    atom_selector_refinement = {
        "schema": "c985.d20_signature_boundary_spine_aperture_atom_selector_refinement@1",
        "object": "d20",
        "selector_rule": {
            "domain": "six zero-overhead aperture cycles with first contact on carrier-mask edge 39 or 41",
            "first_contact_selector": "choose atom 7, the x2 atom, from the mixed shared atom set {7,19}",
            "forgetful_projection": "forgetting selected atoms returns to mixed carrier-mask contacts, not pure x2 carrier edges",
            "intended_x5": "atom 19 appears as the selected second step of the word x2,x5,x4,x3, not as selected first-contact leakage",
        },
        "selected_atom_word": SELECTED_ATOM_WORD,
        "selected_symbol_word": SELECTED_SYMBOL_WORD,
        "zero_overhead_candidate_ids": ZERO_OVERHEAD_CANDIDATE_IDS,
        "summary": observable_values,
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_atom_selector_refinement_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_ATOM_SELECTOR_REFINEMENT_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the six zero-overhead carrier cycles admit a consistent atom selector with atom word 7,19,12,11",
            "the selected symbol word is x2,x5,x4,x3, matching the ranked zero-overhead cycles",
            "the first contact selects x2 atom 7 and has no selected x5 leakage, while x5 atom 19 remains an unselected cowitness",
            "forgetting the selector returns to mixed carrier-mask edges 39 or 41, so the refinement is atom-level rather than a pure carrier-mask edge",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_atom_selector_refinement@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The zero-overhead aperture class can be atom-selected so its "
            "first contact is x2 atom 7 with no selected x5 leakage, and the "
            "geodesic trace remains unchanged. The refinement does not erase "
            "the carrier-mask ambiguity: forgetting the atom selector returns "
            "to mixed x2/x5 edges 39 or 41."
        ),
        "stage_protocol": {
            "draft": "split the zero-overhead mixed carrier contacts into selected atom witnesses",
            "witness": "materialize one selected atom per cycle step and the unselected first-contact x5 cowitness",
            "coherence": "check selected atom words, selected symbol words, cycle windows, and geodesic metrics",
            "closure": "certify atom-level selection without claiming a new pure carrier-mask edge",
            "emit": "emit atom-selector JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "mixed_contact_report": input_entry(
                MIXED_CONTACT_REPORT,
                {
                    "status": mixed_report.get("status"),
                    "certificate_sha256": mixed_report.get("certificate_sha256"),
                },
            ),
            "mixed_contact_json": input_entry(MIXED_CONTACT_JSON),
            "mixed_contact_candidates": input_entry(MIXED_CONTACT_CANDIDATES),
            "mixed_contact_edges": input_entry(MIXED_CONTACT_EDGES),
            "mixed_contact_tables": input_entry(MIXED_CONTACT_TABLES),
            "mixed_contact_certificate": input_entry(MIXED_CONTACT_CERTIFICATE),
            "ranking_report": input_entry(
                RANKING_REPORT,
                {
                    "status": ranking_report.get("status"),
                    "certificate_sha256": ranking_report.get("certificate_sha256"),
                },
            ),
            "ranking_json": input_entry(RANKING_JSON),
            "ranking_candidates": input_entry(RANKING_CANDIDATES),
            "ranking_tables": input_entry(RANKING_TABLES),
            "ranking_certificate": input_entry(RANKING_CERTIFICATE),
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
            "signature_boundary_spine_aperture_atom_selector_refinement": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_atom_selector_refinement.json"
            ),
            "aperture_atom_selector_steps_csv": relpath(
                OUT_DIR / "aperture_atom_selector_steps.csv"
            ),
            "aperture_atom_selector_candidates_csv": relpath(
                OUT_DIR / "aperture_atom_selector_candidates.csv"
            ),
            "aperture_atom_selector_observables_csv": relpath(
                OUT_DIR / "aperture_atom_selector_observables.csv"
            ),
            "signature_boundary_spine_aperture_atom_selector_refinement_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_atom_selector_refinement_tables.npz"
            ),
            "signature_boundary_spine_aperture_atom_selector_refinement_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_atom_selector_refinement_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "atom-selector witnesses for the six zero-overhead aperture cycles",
                "that selected first-contact atoms are x2 and not x5",
                "that the intended selected x5 appears only as the second step of the zero-overhead word",
                "that the ranked geodesic trace metrics survive atom selection",
            ],
            "does_not_certify_because_not_required": [
                "a new carrier-mask pure x2 edge replacing edges 39 or 41",
                "a global atom-refined carrier graph beyond the six zero-overhead cycles",
                "typed-tail preservation for the zero-overhead class",
                "new categorical F-symbols, pivotality, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Build the atom-selected geodesic/type tradeoff: compare the "
            "zero-overhead atom-selected class against the clean x1-tail "
            "cycle after charging only selected first-contact leakage, then "
            "certify whether the Pareto frontier collapses at atom level or "
            "whether x1-tail preservation remains a separate obstruction."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_atom_selector_refinement_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified mixed-contact, ranking, residual cell-complex, and symbolic alphabet artifacts",
            "filter the six zero-overhead aperture candidates",
            "select exactly one atom per carrier contact matching the ranked symbol word",
            "check that first-contact x2 selection removes selected x5 leakage while preserving the geodesic trace",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_atom_selector_refinement": (
            atom_selector_refinement
        ),
        "aperture_atom_selector_steps_csv": csv_text(
            SELECTOR_STEP_COLUMNS,
            step_rows,
        ),
        "aperture_atom_selector_candidates_csv": csv_text(
            SELECTOR_CANDIDATE_COLUMNS,
            candidate_rows,
        ),
        "aperture_atom_selector_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "selector_step_table": selector_step_table,
        "selector_candidate_table": selector_candidate_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_atom_selector_refinement_certificate": certificate,
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
        OUT_DIR / "signature_boundary_spine_aperture_atom_selector_refinement.json",
        payloads["signature_boundary_spine_aperture_atom_selector_refinement"],
    )
    (OUT_DIR / "aperture_atom_selector_steps.csv").write_text(
        payloads["aperture_atom_selector_steps_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_atom_selector_candidates.csv").write_text(
        payloads["aperture_atom_selector_candidates_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_atom_selector_observables.csv").write_text(
        payloads["aperture_atom_selector_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_boundary_spine_aperture_atom_selector_refinement_tables.npz",
        selector_step_table=payloads["selector_step_table"],
        selector_candidate_table=payloads["selector_candidate_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_atom_selector_refinement_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_atom_selector_refinement_certificate"
        ],
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
                "selector_candidate_ids": witness["selector_candidate_ids"],
                "selected_atom_word": witness["selected_atom_word"],
                "selected_symbol_word": witness["selected_symbol_word"],
                "first_contact_reading": witness["first_contact_reading"],
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
