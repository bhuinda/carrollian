from __future__ import annotations

import json
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_geodesic_fan import (
        OUT_DIR as APERTURE_FAN_DIR,
    )
    from .derive_c985_d20_signature_boundary_spine_gate_automaton import (
        OUT_DIR as GATE_AUTOMATON_DIR,
    )
    from .derive_c985_d20_signature_boundary_spine_typed_corridors import (
        OUT_DIR as TYPED_CORRIDOR_DIR,
    )
    from .derive_c985_d20_symbolic_associativity import (
        OUT_DIR as SYMBOLIC_ASSOCIATIVITY_DIR,
    )
    from .derive_c985_d20_signature_boundary_spine_routing_prefix import (
        bitset,
        read_int_csv,
        table_from_rows,
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
    from derive_c985_d20_signature_boundary_spine_aperture_geodesic_fan import (
        OUT_DIR as APERTURE_FAN_DIR,
    )
    from derive_c985_d20_signature_boundary_spine_gate_automaton import (
        OUT_DIR as GATE_AUTOMATON_DIR,
    )
    from derive_c985_d20_signature_boundary_spine_typed_corridors import (
        OUT_DIR as TYPED_CORRIDOR_DIR,
    )
    from derive_c985_d20_symbolic_associativity import (
        OUT_DIR as SYMBOLIC_ASSOCIATIVITY_DIR,
    )
    from derive_c985_d20_signature_boundary_spine_routing_prefix import (
        bitset,
        read_int_csv,
        table_from_rows,
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


THEOREM_ID = "c985_d20_signature_boundary_spine_aperture_corridor_insertion"
STATUS = "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CORRIDOR_INSERTION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

APERTURE_FAN_REPORT = APERTURE_FAN_DIR / "report.json"
APERTURE_FAN_JSON = (
    APERTURE_FAN_DIR / "signature_boundary_spine_aperture_geodesic_fan.json"
)
APERTURE_FAN_PATHS = APERTURE_FAN_DIR / "aperture_geodesic_paths.csv"
APERTURE_FAN_TABLES = (
    APERTURE_FAN_DIR / "signature_boundary_spine_aperture_geodesic_fan_tables.npz"
)
APERTURE_FAN_CERTIFICATE = (
    APERTURE_FAN_DIR
    / "signature_boundary_spine_aperture_geodesic_fan_certificate.json"
)

GATE_AUTOMATON_REPORT = GATE_AUTOMATON_DIR / "report.json"
GATE_AUTOMATON_JSON = (
    GATE_AUTOMATON_DIR / "signature_boundary_spine_gate_automaton.json"
)
GATE_AUTOMATON_TRANSITIONS = GATE_AUTOMATON_DIR / "gate_automaton_transitions.csv"
GATE_AUTOMATON_TRIGRAMS = GATE_AUTOMATON_DIR / "gate_trigram_windows.csv"
GATE_AUTOMATON_TABLES = (
    GATE_AUTOMATON_DIR / "signature_boundary_spine_gate_automaton_tables.npz"
)
GATE_AUTOMATON_CERTIFICATE = (
    GATE_AUTOMATON_DIR / "signature_boundary_spine_gate_automaton_certificate.json"
)

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
    / "derive_c985_d20_signature_boundary_spine_aperture_corridor_insertion.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_corridor_insertion.py"
)

INSERTED_SYMBOL_ID = 2
SOURCE_TO_BRANCH_PREFIX = 14
SELECTED_INSERTION_POSITION = 14
STRICT_INTERMEDIATE_NODE_ID = 42
STRICT_SOURCE_NODE_ID = 48
APERTURE_NODE_ID = 44
OBSERVED_SIGNATURE_THRESHOLD = 175
BOUNDARY_WINDOW_CONTACT_IDS = {12, 13, 14}

CANDIDATE_COLUMNS = [
    "candidate_id",
    "insertion_position",
    "inserted_symbol_id",
    "after_original_contact_id",
    "before_original_contact_id",
    "typed_contact_subsequence_preserved_flag",
    "accepting_branch_word_preserved_count",
    "original_trigram_window_preserved_count",
    "inserted_window_count",
    "canonical_42_window_count",
    "strict_42_window_count",
    "full_sector_inserted_window_count",
    "max_inserted_window_signature_union_count",
    "boundary_window_overlap_max",
    "selected_corridor_edit_flag",
]

INSERTED_WINDOW_COLUMNS = [
    "candidate_id",
    "edited_window_id",
    "left_symbol_id",
    "middle_symbol_id",
    "right_symbol_id",
    "left_contact_id",
    "middle_contact_id",
    "right_contact_id",
    "canonical_triple_id",
    "sector_coverage_count",
    "full_sector_flag",
    "signature_union_count",
    "strict_intermediate_flag",
    "boundary_window_overlap_count",
]

SELECTED_SEQUENCE_COLUMNS = [
    "edited_position",
    "original_contact_id",
    "gate_symbol_id",
    "inserted_contact_flag",
    "source_to_branch_contact_flag",
    "accepting_state_flag",
]

INSERTION_OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "source_to_branch_original_length": 0,
    "candidate_count": 1,
    "single_x2_candidate_count": 2,
    "feasible_strict_candidate_count": 3,
    "boundary_anchored_feasible_candidate_count": 4,
    "selected_insertion_position": 5,
    "selected_accepting_branch_preserved_count": 6,
    "selected_original_window_preserved_count": 7,
    "selected_inserted_window_count": 8,
    "selected_canonical_42_window_count": 9,
    "selected_max_inserted_window_signature": 10,
    "selected_boundary_overlap": 11,
    "selected_edited_sequence_length": 12,
    "strict_intermediate_node_id": 13,
    "strict_intermediate_signature_union_count": 14,
    "strict_intermediate_sector_coverage_count": 15,
    "aperture_node_id": 16,
    "aperture_signature_union_count": 17,
    "missing_x4_after_x2_insertion_flag": 18,
    "original_branch_word_count": 19,
}


def contact_id_for_edited_index(index: int, insertion_position: int) -> int:
    if index == insertion_position:
        return 0
    if index < insertion_position:
        return index + 1
    return index


def preserved_original_window_count(insertion_position: int, original_length: int) -> int:
    count = 0
    for start in range(original_length - 2):
        if insertion_position <= start or insertion_position >= start + 3:
            count += 1
    return count


def build_payloads() -> dict[str, Any]:
    aperture_report = load_json(APERTURE_FAN_REPORT)
    aperture_fan = load_json(APERTURE_FAN_JSON)
    aperture_certificate = load_json(APERTURE_FAN_CERTIFICATE)
    gate_report = load_json(GATE_AUTOMATON_REPORT)
    gate_automaton = load_json(GATE_AUTOMATON_JSON)
    gate_certificate = load_json(GATE_AUTOMATON_CERTIFICATE)
    typed_report = load_json(TYPED_CORRIDOR_REPORT)
    typed_certificate = load_json(TYPED_CORRIDOR_CERTIFICATE)
    associativity_report = load_json(SYMBOLIC_ASSOCIATIVITY_REPORT)
    associativity_certificate = load_json(SYMBOLIC_ASSOCIATIVITY_CERTIFICATE)

    aperture_tables = np.load(APERTURE_FAN_TABLES, allow_pickle=False)
    gate_tables = np.load(GATE_AUTOMATON_TABLES, allow_pickle=False)
    typed_tables = np.load(TYPED_CORRIDOR_TABLES, allow_pickle=False)
    associativity_tables = np.load(SYMBOLIC_ASSOCIATIVITY_TABLES, allow_pickle=False)
    geodesic_path_table = np.asarray(
        aperture_tables["geodesic_path_table"], dtype=np.int64
    )
    gate_transition_table = np.asarray(
        gate_tables["gate_automaton_transition_table"], dtype=np.int64
    )
    gate_trigram_table = np.asarray(gate_tables["gate_trigram_window_table"], dtype=np.int64)
    typed_corridor_table = np.asarray(typed_tables["corridor_edge_table"], dtype=np.int64)
    associativity_table = np.asarray(
        associativity_tables["symbolic_associativity_table"], dtype=np.int64
    )

    transition_rows = read_int_csv(GATE_AUTOMATON_TRANSITIONS)
    original_sequence = [
        int(row["gate_symbol_id"])
        for row in transition_rows
        if int(row["source_to_branch_flag"]) == 1
    ]
    accepting_states = gate_report["witness"]["accepting_state_ids"]
    original_windows = read_int_csv(GATE_AUTOMATON_TRIGRAMS)
    associativity_rows = read_int_csv(SYMBOLIC_ASSOCIATIVITY_CSV)
    associativity_by_window = {
        (
            int(row["left_symbol_id"]),
            int(row["middle_symbol_id"]),
            int(row["right_symbol_id"]),
        ): row
        for row in associativity_rows
    }

    candidate_rows: list[dict[str, int]] = []
    inserted_window_rows: list[dict[str, int]] = []
    for insertion_position in range(len(original_sequence) + 1):
        edited = (
            original_sequence[:insertion_position]
            + [INSERTED_SYMBOL_ID]
            + original_sequence[insertion_position:]
        )
        inserted_windows_for_candidate: list[dict[str, int]] = []
        for start in range(len(edited) - 2):
            contact_ids = [
                contact_id_for_edited_index(index, insertion_position)
                for index in range(start, start + 3)
            ]
            if 0 not in contact_ids:
                continue
            window = tuple(int(symbol) for symbol in edited[start : start + 3])
            assoc = associativity_by_window[window]
            boundary_overlap = len(set(contact_ids) & BOUNDARY_WINDOW_CONTACT_IDS)
            inserted_window = {
                "candidate_id": insertion_position,
                "edited_window_id": start + 1,
                "left_symbol_id": window[0],
                "middle_symbol_id": window[1],
                "right_symbol_id": window[2],
                "left_contact_id": int(contact_ids[0]),
                "middle_contact_id": int(contact_ids[1]),
                "right_contact_id": int(contact_ids[2]),
                "canonical_triple_id": int(assoc["canonical_triple_id"]),
                "sector_coverage_count": int(assoc["sector_coverage_count"]),
                "full_sector_flag": int(int(assoc["sector_coverage_count"]) == 6),
                "signature_union_count": int(assoc["signature_union_count"]),
                "strict_intermediate_flag": int(
                    int(assoc["canonical_triple_id"]) == STRICT_INTERMEDIATE_NODE_ID
                    and int(assoc["sector_coverage_count"]) == 6
                    and int(assoc["signature_union_count"])
                    >= OBSERVED_SIGNATURE_THRESHOLD
                ),
                "boundary_window_overlap_count": boundary_overlap,
            }
            inserted_windows_for_candidate.append(inserted_window)
            inserted_window_rows.append(inserted_window)

        canonical_42_count = sum(
            1
            for row in inserted_windows_for_candidate
            if int(row["canonical_triple_id"]) == STRICT_INTERMEDIATE_NODE_ID
        )
        strict_42_count = sum(
            int(row["strict_intermediate_flag"])
            for row in inserted_windows_for_candidate
        )
        selected = insertion_position == SELECTED_INSERTION_POSITION
        candidate_rows.append(
            {
                "candidate_id": insertion_position,
                "insertion_position": insertion_position,
                "inserted_symbol_id": INSERTED_SYMBOL_ID,
                "after_original_contact_id": insertion_position
                if insertion_position > 0
                else -1,
                "before_original_contact_id": insertion_position + 1
                if insertion_position < len(original_sequence)
                else -1,
                "typed_contact_subsequence_preserved_flag": int(
                    [symbol for symbol in edited if symbol != INSERTED_SYMBOL_ID]
                    == original_sequence
                ),
                "accepting_branch_word_preserved_count": sum(
                    1 for state in accepting_states if insertion_position >= int(state)
                ),
                "original_trigram_window_preserved_count": preserved_original_window_count(
                    insertion_position,
                    len(original_sequence),
                ),
                "inserted_window_count": len(inserted_windows_for_candidate),
                "canonical_42_window_count": canonical_42_count,
                "strict_42_window_count": strict_42_count,
                "full_sector_inserted_window_count": sum(
                    int(row["full_sector_flag"]) for row in inserted_windows_for_candidate
                ),
                "max_inserted_window_signature_union_count": max(
                    int(row["signature_union_count"])
                    for row in inserted_windows_for_candidate
                ),
                "boundary_window_overlap_max": max(
                    int(row["boundary_window_overlap_count"])
                    for row in inserted_windows_for_candidate
                ),
                "selected_corridor_edit_flag": int(selected),
            }
        )

    selected_candidate = candidate_rows[SELECTED_INSERTION_POSITION]
    selected_sequence = (
        original_sequence[:SELECTED_INSERTION_POSITION]
        + [INSERTED_SYMBOL_ID]
        + original_sequence[SELECTED_INSERTION_POSITION:]
    )
    selected_sequence_rows: list[dict[str, int]] = []
    for index, symbol in enumerate(selected_sequence):
        contact_id = contact_id_for_edited_index(index, SELECTED_INSERTION_POSITION)
        selected_sequence_rows.append(
            {
                "edited_position": index + 1,
                "original_contact_id": contact_id,
                "gate_symbol_id": int(symbol),
                "inserted_contact_flag": int(contact_id == 0),
                "source_to_branch_contact_flag": int(index + 1 <= len(selected_sequence)),
                "accepting_state_flag": int(contact_id in accepting_states),
            }
        )

    selected_inserted_windows = [
        row
        for row in inserted_window_rows
        if int(row["candidate_id"]) == SELECTED_INSERTION_POSITION
    ]
    selected_strict_windows = [
        row
        for row in selected_inserted_windows
        if int(row["strict_intermediate_flag"]) == 1
    ]
    strict_path = aperture_report["witness"]["strict_full_sector_high_signature_paths"][0]
    feasible_candidates = [
        row for row in candidate_rows if int(row["strict_42_window_count"]) > 0
    ]
    anchored_feasible_candidates = [
        row
        for row in feasible_candidates
        if int(row["boundary_window_overlap_max"]) >= 2
    ]
    missing_symbol_bitset_after_insert = ((1 << 6) - 1) & ~bitset(selected_sequence)

    observable_values = {
        "source_to_branch_original_length": len(original_sequence),
        "candidate_count": len(candidate_rows),
        "single_x2_candidate_count": len(candidate_rows),
        "feasible_strict_candidate_count": len(feasible_candidates),
        "boundary_anchored_feasible_candidate_count": len(anchored_feasible_candidates),
        "selected_insertion_position": SELECTED_INSERTION_POSITION,
        "selected_accepting_branch_preserved_count": int(
            selected_candidate["accepting_branch_word_preserved_count"]
        ),
        "selected_original_window_preserved_count": int(
            selected_candidate["original_trigram_window_preserved_count"]
        ),
        "selected_inserted_window_count": int(
            selected_candidate["inserted_window_count"]
        ),
        "selected_canonical_42_window_count": int(
            selected_candidate["canonical_42_window_count"]
        ),
        "selected_max_inserted_window_signature": int(
            selected_candidate["max_inserted_window_signature_union_count"]
        ),
        "selected_boundary_overlap": int(
            selected_candidate["boundary_window_overlap_max"]
        ),
        "selected_edited_sequence_length": len(selected_sequence),
        "strict_intermediate_node_id": STRICT_INTERMEDIATE_NODE_ID,
        "strict_intermediate_signature_union_count": int(
            selected_strict_windows[0]["signature_union_count"]
        ),
        "strict_intermediate_sector_coverage_count": int(
            selected_strict_windows[0]["sector_coverage_count"]
        ),
        "aperture_node_id": APERTURE_NODE_ID,
        "aperture_signature_union_count": int(
            aperture_report["witness"]["aperture_node"]["signature_union_count"]
        ),
        "missing_x4_after_x2_insertion_flag": int(
            missing_symbol_bitset_after_insert & (1 << 4) != 0
        ),
        "original_branch_word_count": len(accepting_states),
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

    candidate_table = table_from_rows(CANDIDATE_COLUMNS, candidate_rows)
    inserted_window_table = table_from_rows(
        INSERTED_WINDOW_COLUMNS,
        inserted_window_rows,
    )
    selected_sequence_table = table_from_rows(
        SELECTED_SEQUENCE_COLUMNS,
        selected_sequence_rows,
    )
    observable_table = table_from_rows(INSERTION_OBSERVABLE_COLUMNS, observable_rows)

    checks = {
        "aperture_fan_report_certified": aperture_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_GEODESIC_FAN_CERTIFIED",
        "aperture_fan_certificate_certified": aperture_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_GEODESIC_FAN_CERTIFIED",
        "gate_automaton_report_certified": gate_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_GATE_AUTOMATON_CERTIFIED",
        "gate_automaton_certificate_certified": gate_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_GATE_AUTOMATON_CERTIFIED",
        "typed_corridor_report_certified": typed_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_TYPED_CORRIDORS_CERTIFIED",
        "typed_corridor_certificate_certified": typed_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_TYPED_CORRIDORS_CERTIFIED",
        "symbolic_associativity_report_certified": associativity_report.get("status")
        == "C985_D20_SYMBOLIC_ASSOCIATIVITY_CERTIFIED",
        "symbolic_associativity_certificate_certified": associativity_certificate.get("status")
        == "C985_D20_SYMBOLIC_ASSOCIATIVITY_CERTIFIED",
        "aperture_fan_schema_available": aperture_fan.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_geodesic_fan@1",
        "gate_automaton_schema_available": gate_automaton.get("schema")
        == "c985.d20_signature_boundary_spine_gate_automaton@1",
        "gate_transition_table_shape_is_16_by_16": tuple(gate_transition_table.shape)
        == (16, 16),
        "gate_trigram_table_shape_is_12_by_20": tuple(gate_trigram_table.shape)
        == (12, 20),
        "typed_corridor_table_shape_is_16_by_23": tuple(typed_corridor_table.shape)
        == (16, 23),
        "symbolic_associativity_table_shape_is_216_by_27": tuple(
            associativity_table.shape
        )
        == (216, 27),
        "aperture_geodesic_path_table_shape_is_6_by_17": tuple(
            geodesic_path_table.shape
        )
        == (6, 17),
        "strict_aperture_path_is_48_42_44": strict_path == [48, 42, 44],
        "source_to_branch_sequence_matches_gate_report": original_sequence
        == gate_report["witness"]["gate_symbol_sequence"][:SOURCE_TO_BRANCH_PREFIX],
        "source_to_branch_sequence_omits_x2": INSERTED_SYMBOL_ID
        not in original_sequence,
        "zero_edit_cannot_introduce_x2": INSERTED_SYMBOL_ID
        not in original_sequence,
        "candidate_count_is_15": len(candidate_rows) == 15,
        "feasible_strict_candidate_count_is_8": len(feasible_candidates) == 8,
        "boundary_anchored_feasible_candidate_count_is_4": len(
            anchored_feasible_candidates
        )
        == 4,
        "selected_insertion_position_is_14": SELECTED_INSERTION_POSITION == 14,
        "selected_edit_preserves_typed_contact_subsequence": int(
            selected_candidate["typed_contact_subsequence_preserved_flag"]
        )
        == 1,
        "selected_edit_preserves_all_six_branch_words": int(
            selected_candidate["accepting_branch_word_preserved_count"]
        )
        == 6,
        "selected_edit_preserves_all_twelve_original_windows": int(
            selected_candidate["original_trigram_window_preserved_count"]
        )
        == 12,
        "selected_edit_has_one_inserted_window": int(
            selected_candidate["inserted_window_count"]
        )
        == 1,
        "selected_edit_creates_one_strict_42_window": int(
            selected_candidate["strict_42_window_count"]
        )
        == 1,
        "selected_inserted_window_is_5_3_2": [
            int(selected_strict_windows[0]["left_symbol_id"]),
            int(selected_strict_windows[0]["middle_symbol_id"]),
            int(selected_strict_windows[0]["right_symbol_id"]),
        ]
        == [5, 3, 2],
        "selected_inserted_window_canonical_is_42": int(
            selected_strict_windows[0]["canonical_triple_id"]
        )
        == STRICT_INTERMEDIATE_NODE_ID,
        "selected_inserted_window_full_sector_signature_183": (
            int(selected_strict_windows[0]["sector_coverage_count"]),
            int(selected_strict_windows[0]["signature_union_count"]),
        )
        == (6, 183),
        "selected_window_overlaps_boundary_window_by_two_contacts": int(
            selected_strict_windows[0]["boundary_window_overlap_count"]
        )
        == 2,
        "selected_edit_is_unique_branch_and_window_preserving_feasible_candidate": [
            int(row["candidate_id"])
            for row in feasible_candidates
            if int(row["accepting_branch_word_preserved_count"]) == 6
            and int(row["original_trigram_window_preserved_count"]) == 12
        ]
        == [SELECTED_INSERTION_POSITION],
        "selected_sequence_length_is_15": len(selected_sequence) == 15,
        "selected_sequence_suffix_is_5_3_2": selected_sequence[-3:] == [5, 3, 2],
        "selected_sequence_still_omits_x4": bool(
            missing_symbol_bitset_after_insert & (1 << 4)
        ),
        "candidate_table_shape_is_15_by_15": tuple(candidate_table.shape)
        == (15, len(CANDIDATE_COLUMNS)),
        "inserted_window_table_shape_is_39_by_14": tuple(inserted_window_table.shape)
        == (39, len(INSERTED_WINDOW_COLUMNS)),
        "selected_sequence_table_shape_is_15_by_6": tuple(selected_sequence_table.shape)
        == (15, len(SELECTED_SEQUENCE_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(INSERTION_OBSERVABLE_COLUMNS)),
    }

    witness = {
        "original_source_to_branch_sequence": original_sequence,
        "accepting_state_ids": accepting_states,
        "strict_aperture_path": strict_path,
        "candidate_count": len(candidate_rows),
        "feasible_strict_candidate_ids": [
            int(row["candidate_id"]) for row in feasible_candidates
        ],
        "boundary_anchored_feasible_candidate_ids": [
            int(row["candidate_id"]) for row in anchored_feasible_candidates
        ],
        "selected_candidate_id": SELECTED_INSERTION_POSITION,
        "selected_edited_sequence": selected_sequence,
        "selected_new_window": {
            "edited_window_id": int(selected_strict_windows[0]["edited_window_id"]),
            "ordered_symbols": [
                int(selected_strict_windows[0]["left_symbol_id"]),
                int(selected_strict_windows[0]["middle_symbol_id"]),
                int(selected_strict_windows[0]["right_symbol_id"]),
            ],
            "contact_ids": [
                int(selected_strict_windows[0]["left_contact_id"]),
                int(selected_strict_windows[0]["middle_contact_id"]),
                int(selected_strict_windows[0]["right_contact_id"]),
            ],
            "canonical_triple_id": int(
                selected_strict_windows[0]["canonical_triple_id"]
            ),
            "sector_coverage_count": int(
                selected_strict_windows[0]["sector_coverage_count"]
            ),
            "signature_union_count": int(
                selected_strict_windows[0]["signature_union_count"]
            ),
            "boundary_window_overlap_count": int(
                selected_strict_windows[0]["boundary_window_overlap_count"]
            ),
        },
        "selected_preservation": {
            "typed_contact_subsequence_preserved": True,
            "accepting_branch_word_preserved_count": int(
                selected_candidate["accepting_branch_word_preserved_count"]
            ),
            "original_trigram_window_preserved_count": int(
                selected_candidate["original_trigram_window_preserved_count"]
            ),
            "missing_symbol_bitset_after_insert": missing_symbol_bitset_after_insert,
        },
        "candidate_table_sha256": sha_array(candidate_table),
        "inserted_window_table_sha256": sha_array(inserted_window_table),
        "selected_sequence_table_sha256": sha_array(selected_sequence_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    insertion = {
        "schema": "c985.d20_signature_boundary_spine_aperture_corridor_insertion@1",
        "object": "d20",
        "corridor_insertion_rule": {
            "source": "certified gate automaton source-to-branch sequence",
            "edit": "insert exactly one virtual x2 gate while preserving existing typed contacts as an ordered subsequence",
            "selection": "choose the unique strict node-42 insertion that preserves all branch words and all original source-to-branch trigram windows",
            "closure": "the edit opens the strict intermediate node 42 but leaves x4 absent for a later aperture step",
        },
        "selected_candidate_id": SELECTED_INSERTION_POSITION,
        "selected_edited_sequence": selected_sequence,
        "selected_new_window": witness["selected_new_window"],
        "strict_aperture_path": strict_path,
        "candidate_summary": {
            "candidate_count": len(candidate_rows),
            "feasible_strict_candidate_ids": witness["feasible_strict_candidate_ids"],
            "boundary_anchored_feasible_candidate_ids": witness[
                "boundary_anchored_feasible_candidate_ids"
            ],
            "selected_preservation": witness["selected_preservation"],
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_corridor_insertion_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CORRIDOR_INSERTION_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "zero edits cannot open the strict aperture path because the source-to-branch gate sequence omits x2",
            "eight single-x2 insertion sites create the strict intermediate canonical node 42",
            "only insertion after the current source-to-branch endpoint preserves all six branch words and all twelve original trigram windows",
            "the selected virtual x2 gate appends the new terminal window (5,3,2), canonical node 42, full-sector, signature 183",
            "the insertion opens the first step 48 -> 42 while leaving x4 absent for the remaining aperture step 42 -> 44",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_corridor_insertion@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The strict aperture path can be lifted back to the gate sequence "
            "by a unique branch-preserving one-symbol edit: insert a virtual "
            "x2 after the current source-to-branch endpoint, preserving all "
            "existing typed contacts and branch words while adding the "
            "full-sector node-42 window."
        ),
        "stage_protocol": {
            "draft": "treat the strict aperture path as a target for a one-symbol source-to-branch gate edit",
            "witness": "enumerate every single-x2 insertion candidate and all windows involving the inserted gate",
            "coherence": "check branch-word preservation, original-window preservation, node-42 creation, and x4 remaining absent",
            "closure": "certify the minimal virtual insertion without claiming an existing typed x2 contact in the source data",
            "emit": "emit insertion JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "aperture_fan_report": input_entry(
                APERTURE_FAN_REPORT,
                {
                    "status": aperture_report.get("status"),
                    "certificate_sha256": aperture_report.get("certificate_sha256"),
                },
            ),
            "aperture_fan": input_entry(APERTURE_FAN_JSON),
            "aperture_fan_paths": input_entry(APERTURE_FAN_PATHS),
            "aperture_fan_tables": input_entry(APERTURE_FAN_TABLES),
            "aperture_fan_certificate": input_entry(APERTURE_FAN_CERTIFICATE),
            "gate_automaton_report": input_entry(
                GATE_AUTOMATON_REPORT,
                {
                    "status": gate_report.get("status"),
                    "certificate_sha256": gate_report.get("certificate_sha256"),
                },
            ),
            "gate_automaton": input_entry(GATE_AUTOMATON_JSON),
            "gate_automaton_transitions": input_entry(GATE_AUTOMATON_TRANSITIONS),
            "gate_automaton_trigrams": input_entry(GATE_AUTOMATON_TRIGRAMS),
            "gate_automaton_tables": input_entry(GATE_AUTOMATON_TABLES),
            "gate_automaton_certificate": input_entry(GATE_AUTOMATON_CERTIFICATE),
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
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_aperture_corridor_insertion": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_corridor_insertion.json"
            ),
            "aperture_corridor_insertion_candidates_csv": relpath(
                OUT_DIR / "aperture_corridor_insertion_candidates.csv"
            ),
            "aperture_corridor_inserted_windows_csv": relpath(
                OUT_DIR / "aperture_corridor_inserted_windows.csv"
            ),
            "aperture_corridor_selected_sequence_csv": relpath(
                OUT_DIR / "aperture_corridor_selected_sequence.csv"
            ),
            "aperture_corridor_insertion_observables_csv": relpath(
                OUT_DIR / "aperture_corridor_insertion_observables.csv"
            ),
            "signature_boundary_spine_aperture_corridor_insertion_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_corridor_insertion_tables.npz"
            ),
            "signature_boundary_spine_aperture_corridor_insertion_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_corridor_insertion_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "all single-x2 insertion candidates over the 14-symbol source-to-branch gate word",
                "the unique candidate that preserves all six branch words and all 12 original trigram windows while creating node 42",
                "the selected virtual edited sequence and its new terminal window (5,3,2)",
                "that x4 remains absent after the selected x2 insertion",
            ],
            "does_not_certify_because_not_required": [
                "that the virtual x2 contact already exists in the certified typed-corridor source data",
                "which concrete positive/negative carrier pair would realize the inserted x2 contact",
                "the subsequent x4 insertion needed to reach aperture node 44",
                "new associator, pentagon, braiding, center, or tube-algebra data",
            ],
        },
        "next_highest_yield_item": (
            "Search the typed carrier-pair boundary for a realizable x2 contact "
            "that can occupy the selected insertion slot after state 14, then "
            "certify whether it can be spliced before the post-branch tail "
            "without changing the six existing branch words."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_corridor_insertion_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified aperture-fan, gate-automaton, typed-corridor, and symbolic-associativity artifacts",
            "enumerate every single-x2 insertion over the source-to-branch gate word",
            "score inserted windows by branch preservation, original-window preservation, and strict node-42 creation",
            "check the selected insertion preserves existing contacts as a subsequence and leaves x4 absent",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_corridor_insertion": insertion,
        "aperture_corridor_insertion_candidates_csv": csv_text(
            CANDIDATE_COLUMNS,
            candidate_rows,
        ),
        "aperture_corridor_inserted_windows_csv": csv_text(
            INSERTED_WINDOW_COLUMNS,
            inserted_window_rows,
        ),
        "aperture_corridor_selected_sequence_csv": csv_text(
            SELECTED_SEQUENCE_COLUMNS,
            selected_sequence_rows,
        ),
        "aperture_corridor_insertion_observables_csv": csv_text(
            INSERTION_OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "candidate_table": candidate_table,
        "inserted_window_table": inserted_window_table,
        "selected_sequence_table": selected_sequence_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_corridor_insertion_certificate": certificate,
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
        OUT_DIR / "signature_boundary_spine_aperture_corridor_insertion.json",
        payloads["signature_boundary_spine_aperture_corridor_insertion"],
    )
    (OUT_DIR / "aperture_corridor_insertion_candidates.csv").write_text(
        payloads["aperture_corridor_insertion_candidates_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_corridor_inserted_windows.csv").write_text(
        payloads["aperture_corridor_inserted_windows_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_corridor_selected_sequence.csv").write_text(
        payloads["aperture_corridor_selected_sequence_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_corridor_insertion_observables.csv").write_text(
        payloads["aperture_corridor_insertion_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_boundary_spine_aperture_corridor_insertion_tables.npz",
        candidate_table=payloads["candidate_table"],
        inserted_window_table=payloads["inserted_window_table"],
        selected_sequence_table=payloads["selected_sequence_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR / "signature_boundary_spine_aperture_corridor_insertion_certificate.json",
        payloads["signature_boundary_spine_aperture_corridor_insertion_certificate"],
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
                "selected_candidate_id": witness["selected_candidate_id"],
                "selected_new_window": witness["selected_new_window"],
                "selected_preservation": witness["selected_preservation"],
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
