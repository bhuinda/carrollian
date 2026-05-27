from __future__ import annotations

import json
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_typed_corridors import (
        OUT_DIR as TYPED_CORRIDOR_DIR,
    )
    from .derive_c985_d20_symbolic_associativity import (
        OUT_DIR as SYMBOLIC_ASSOCIATIVITY_DIR,
    )
    from .derive_c985_d20_signature_boundary_spine_routing_prefix import (
        bitset,
        popcount,
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
    from derive_c985_d20_signature_boundary_spine_typed_corridors import (
        OUT_DIR as TYPED_CORRIDOR_DIR,
    )
    from derive_c985_d20_symbolic_associativity import (
        OUT_DIR as SYMBOLIC_ASSOCIATIVITY_DIR,
    )
    from derive_c985_d20_signature_boundary_spine_routing_prefix import (
        bitset,
        popcount,
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


THEOREM_ID = "c985_d20_signature_boundary_spine_gate_automaton"
STATUS = "C985_D20_SIGNATURE_BOUNDARY_SPINE_GATE_AUTOMATON_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

TYPED_CORRIDOR_REPORT = TYPED_CORRIDOR_DIR / "report.json"
TYPED_CORRIDOR_JSON = TYPED_CORRIDOR_DIR / "signature_boundary_spine_typed_corridors.json"
TYPED_CORRIDOR_EDGE_CSV = TYPED_CORRIDOR_DIR / "corridor_edge_symbols.csv"
TYPED_CORRIDOR_BRANCH_CSV = TYPED_CORRIDOR_DIR / "branch_corridor_summary.csv"
TYPED_CORRIDOR_TABLES = (
    TYPED_CORRIDOR_DIR / "signature_boundary_spine_typed_corridors_tables.npz"
)
TYPED_CORRIDOR_CERTIFICATE = (
    TYPED_CORRIDOR_DIR / "signature_boundary_spine_typed_corridors_certificate.json"
)

SYMBOLIC_ASSOCIATIVITY_REPORT = SYMBOLIC_ASSOCIATIVITY_DIR / "report.json"
SYMBOLIC_ASSOCIATIVITY_JSON = SYMBOLIC_ASSOCIATIVITY_DIR / "symbolic_associativity.json"
SYMBOLIC_ASSOCIATIVITY_CSV = SYMBOLIC_ASSOCIATIVITY_DIR / "symbolic_associativity.csv"
SYMBOLIC_ASSOCIATIVITY_TABLES = (
    SYMBOLIC_ASSOCIATIVITY_DIR / "symbolic_associativity_tables.npz"
)
SYMBOLIC_ASSOCIATIVITY_CERTIFICATE = (
    SYMBOLIC_ASSOCIATIVITY_DIR / "symbolic_associativity_certificate.json"
)

DERIVE_SCRIPT = (
    ROOT / "src" / "derive_c985_d20_signature_boundary_spine_gate_automaton.py"
)
VALIDATOR_SCRIPT = (
    ROOT / "src" / "certify_c985_d20_signature_boundary_spine_gate_automaton.py"
)

FULL_ALPHABET_SYMBOL_BITSET = (1 << 6) - 1
SOURCE_TO_BRANCH_PREFIX = 14

AUTOMATON_TRANSITION_COLUMNS = [
    "transition_id",
    "from_state_id",
    "to_state_id",
    "boundary_spine_rank",
    "boundary_mask_edge_id",
    "gate_symbol_id",
    "negative_branch_order_rank",
    "negative_carrier_mask_class_id",
    "phase_code",
    "accepting_state_flag",
    "accepted_negative_carrier_mask_class_id",
    "source_to_branch_flag",
    "post_branch_tail_flag",
    "boundary_partition_code",
    "undirected_stationary_flux_x1e12",
    "total_entropy_contribution_x1e12",
]

BRANCH_WORD_COLUMNS = [
    "branch_order_rank",
    "negative_carrier_mask_class_id",
    "accept_state_id",
    "word_length",
    "word_code_base6",
    "word_symbol_bitset",
    "missing_gate_symbol_bitset",
    "trigram_window_count",
    "unique_trigram_count",
    "associativity_certified_window_count",
    "full_sector_window_count",
    "min_signature_union_count",
    "max_signature_union_count",
    "canonical_triple_bitset",
]

TRIGRAM_WINDOW_COLUMNS = [
    "window_id",
    "start_state_id",
    "end_state_id",
    "left_symbol_id",
    "middle_symbol_id",
    "right_symbol_id",
    "triple_id",
    "canonical_triple_id",
    "canonical_first_symbol_id",
    "canonical_second_symbol_id",
    "canonical_third_symbol_id",
    "left_final_matches_right_final",
    "matches_direct_sorted_normal_form",
    "sector_coverage_count",
    "full_sector_flag",
    "signature_union_count",
    "word_triple_multiplicity",
    "left_path_swap_count",
    "right_path_swap_count",
    "canonical_triple_first_occurrence_flag",
]

GATE_AUTOMATON_OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "automaton_transition_count": 0,
    "source_to_branch_transition_count": 1,
    "post_branch_tail_transition_count": 2,
    "accepting_branch_state_count": 3,
    "source_to_branch_trigram_window_count": 4,
    "source_to_branch_unique_trigram_count": 5,
    "associativity_certified_window_count": 6,
    "full_sector_trigram_window_count": 7,
    "source_to_branch_gate_symbol_bitset": 8,
    "missing_gate_symbol_bitset": 9,
    "unique_canonical_triple_count": 10,
    "canonical_triple_bitset": 11,
    "min_trigram_signature_union": 12,
    "max_trigram_signature_union": 13,
    "global_associativity_max_signature_union": 14,
    "global_max_signature_gap": 15,
    "trigram_word_multiplicity_sum": 16,
    "trigram_sector_coverage_sum": 17,
    "full_sector_canonical_triple_id": 18,
    "longest_branch_word_length": 19,
    "first_branch_with_trigram_mask_id": 20,
}


def encode_word(symbols: list[int]) -> int:
    value = 0
    for symbol in symbols:
        value = value * 6 + int(symbol)
    return int(value)


def decode_bitset(value: int) -> list[int]:
    return [index for index in range(64) if int(value) & (1 << index)]


def build_payloads() -> dict[str, Any]:
    typed_report = load_json(TYPED_CORRIDOR_REPORT)
    typed_corridors = load_json(TYPED_CORRIDOR_JSON)
    associativity_report = load_json(SYMBOLIC_ASSOCIATIVITY_REPORT)
    symbolic_associativity = load_json(SYMBOLIC_ASSOCIATIVITY_JSON)

    typed_tables = np.load(TYPED_CORRIDOR_TABLES, allow_pickle=False)
    associativity_tables = np.load(SYMBOLIC_ASSOCIATIVITY_TABLES, allow_pickle=False)

    edge_rows = read_int_csv(TYPED_CORRIDOR_EDGE_CSV)
    branch_rows = read_int_csv(TYPED_CORRIDOR_BRANCH_CSV)
    associativity_rows = read_int_csv(SYMBOLIC_ASSOCIATIVITY_CSV)
    associativity_by_triple = {
        (
            int(row["left_symbol_id"]),
            int(row["middle_symbol_id"]),
            int(row["right_symbol_id"]),
        ): row
        for row in associativity_rows
    }

    accepting_by_state = {
        int(row["first_prefix_length"]): int(row["negative_carrier_mask_class_id"])
        for row in branch_rows
    }
    gate_symbols = [int(row["shared_symbol_id"]) for row in edge_rows]
    branch_prefixes = sorted(accepting_by_state)

    transition_rows: list[dict[str, int]] = []
    for index, row in enumerate(edge_rows, start=1):
        to_state = int(row["boundary_spine_rank"])
        accepted_mask = accepting_by_state.get(to_state, -1)
        transition_rows.append(
            {
                "transition_id": index,
                "from_state_id": index - 1,
                "to_state_id": index,
                "boundary_spine_rank": to_state,
                "boundary_mask_edge_id": int(row["boundary_mask_edge_id"]),
                "gate_symbol_id": int(row["shared_symbol_id"]),
                "negative_branch_order_rank": int(row["negative_branch_order_rank"]),
                "negative_carrier_mask_class_id": int(
                    row["negative_carrier_mask_class_id"]
                ),
                "phase_code": int(row["phase_code"]),
                "accepting_state_flag": int(accepted_mask >= 0),
                "accepted_negative_carrier_mask_class_id": accepted_mask,
                "source_to_branch_flag": int(index <= SOURCE_TO_BRANCH_PREFIX),
                "post_branch_tail_flag": int(index > SOURCE_TO_BRANCH_PREFIX),
                "boundary_partition_code": int(row["boundary_partition_code"]),
                "undirected_stationary_flux_x1e12": int(
                    row["undirected_stationary_flux_x1e12"]
                ),
                "total_entropy_contribution_x1e12": int(
                    row["total_entropy_contribution_x1e12"]
                ),
            }
        )

    source_to_branch_symbols = gate_symbols[:SOURCE_TO_BRANCH_PREFIX]
    source_windows = [
        tuple(source_to_branch_symbols[index : index + 3])
        for index in range(len(source_to_branch_symbols) - 2)
    ]
    seen_canonical: set[int] = set()
    trigram_rows: list[dict[str, int]] = []
    for index, window in enumerate(source_windows, start=1):
        assoc = associativity_by_triple[window]
        canonical_id = int(assoc["canonical_triple_id"])
        first_occurrence = int(canonical_id not in seen_canonical)
        seen_canonical.add(canonical_id)
        trigram_rows.append(
            {
                "window_id": index,
                "start_state_id": index - 1,
                "end_state_id": index + 2,
                "left_symbol_id": window[0],
                "middle_symbol_id": window[1],
                "right_symbol_id": window[2],
                "triple_id": int(assoc["triple_id"]),
                "canonical_triple_id": canonical_id,
                "canonical_first_symbol_id": int(
                    assoc["canonical_first_symbol_id"]
                ),
                "canonical_second_symbol_id": int(
                    assoc["canonical_second_symbol_id"]
                ),
                "canonical_third_symbol_id": int(
                    assoc["canonical_third_symbol_id"]
                ),
                "left_final_matches_right_final": int(
                    assoc["left_final_matches_right_final"]
                ),
                "matches_direct_sorted_normal_form": int(
                    assoc["matches_direct_sorted_normal_form"]
                ),
                "sector_coverage_count": int(assoc["sector_coverage_count"]),
                "full_sector_flag": int(int(assoc["sector_coverage_count"]) == 6),
                "signature_union_count": int(assoc["signature_union_count"]),
                "word_triple_multiplicity": int(assoc["word_triple_multiplicity"]),
                "left_path_swap_count": int(assoc["left_path_swap_count"]),
                "right_path_swap_count": int(assoc["right_path_swap_count"]),
                "canonical_triple_first_occurrence_flag": first_occurrence,
            }
        )

    branch_word_rows: list[dict[str, int]] = []
    for branch in branch_rows:
        accept_state = int(branch["first_prefix_length"])
        word = gate_symbols[:accept_state]
        windows = [tuple(word[index : index + 3]) for index in range(max(0, len(word) - 2))]
        assoc_windows = [associativity_by_triple[window] for window in windows]
        canonical_bitset = bitset(
            {int(row["canonical_triple_id"]) for row in assoc_windows}
        )
        signature_counts = [int(row["signature_union_count"]) for row in assoc_windows]
        branch_word_rows.append(
            {
                "branch_order_rank": int(branch["branch_order_rank"]),
                "negative_carrier_mask_class_id": int(
                    branch["negative_carrier_mask_class_id"]
                ),
                "accept_state_id": accept_state,
                "word_length": len(word),
                "word_code_base6": encode_word(word),
                "word_symbol_bitset": bitset(set(word)),
                "missing_gate_symbol_bitset": FULL_ALPHABET_SYMBOL_BITSET
                & ~bitset(set(word)),
                "trigram_window_count": len(windows),
                "unique_trigram_count": len(set(windows)),
                "associativity_certified_window_count": sum(
                    1
                    for row in assoc_windows
                    if int(row["left_final_matches_right_final"]) == 1
                    and int(row["matches_direct_sorted_normal_form"]) == 1
                ),
                "full_sector_window_count": sum(
                    1 for row in assoc_windows if int(row["sector_coverage_count"]) == 6
                ),
                "min_signature_union_count": min(signature_counts)
                if signature_counts
                else 0,
                "max_signature_union_count": max(signature_counts)
                if signature_counts
                else 0,
                "canonical_triple_bitset": canonical_bitset,
            }
        )

    source_gate_symbol_bitset = bitset(set(source_to_branch_symbols))
    missing_gate_symbol_bitset = FULL_ALPHABET_SYMBOL_BITSET & ~source_gate_symbol_bitset
    canonical_triple_ids = sorted(
        {int(row["canonical_triple_id"]) for row in trigram_rows}
    )
    canonical_triple_bitset = bitset(set(canonical_triple_ids))
    full_sector_rows = [
        row for row in trigram_rows if int(row["full_sector_flag"]) == 1
    ]
    global_max_signature_union = int(
        associativity_report["witness"]["symbolic_triple_signature_union_count_max"]
    )
    max_signature_union = max(
        int(row["signature_union_count"]) for row in trigram_rows
    )
    min_signature_union = min(
        int(row["signature_union_count"]) for row in trigram_rows
    )
    first_branch_with_trigram = next(
        row for row in branch_word_rows if int(row["trigram_window_count"]) > 0
    )

    observable_values = {
        "automaton_transition_count": len(transition_rows),
        "source_to_branch_transition_count": SOURCE_TO_BRANCH_PREFIX,
        "post_branch_tail_transition_count": len(gate_symbols)
        - SOURCE_TO_BRANCH_PREFIX,
        "accepting_branch_state_count": len(branch_prefixes),
        "source_to_branch_trigram_window_count": len(trigram_rows),
        "source_to_branch_unique_trigram_count": len(set(source_windows)),
        "associativity_certified_window_count": sum(
            1
            for row in trigram_rows
            if int(row["left_final_matches_right_final"]) == 1
            and int(row["matches_direct_sorted_normal_form"]) == 1
        ),
        "full_sector_trigram_window_count": len(full_sector_rows),
        "source_to_branch_gate_symbol_bitset": source_gate_symbol_bitset,
        "missing_gate_symbol_bitset": missing_gate_symbol_bitset,
        "unique_canonical_triple_count": len(canonical_triple_ids),
        "canonical_triple_bitset": canonical_triple_bitset,
        "min_trigram_signature_union": min_signature_union,
        "max_trigram_signature_union": max_signature_union,
        "global_associativity_max_signature_union": global_max_signature_union,
        "global_max_signature_gap": global_max_signature_union
        - max_signature_union,
        "trigram_word_multiplicity_sum": sum(
            int(row["word_triple_multiplicity"]) for row in trigram_rows
        ),
        "trigram_sector_coverage_sum": sum(
            int(row["sector_coverage_count"]) for row in trigram_rows
        ),
        "full_sector_canonical_triple_id": int(
            full_sector_rows[0]["canonical_triple_id"]
        ),
        "longest_branch_word_length": max(
            int(row["word_length"]) for row in branch_word_rows
        ),
        "first_branch_with_trigram_mask_id": int(
            first_branch_with_trigram["negative_carrier_mask_class_id"]
        ),
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

    transition_table = table_from_rows(AUTOMATON_TRANSITION_COLUMNS, transition_rows)
    branch_word_table = table_from_rows(BRANCH_WORD_COLUMNS, branch_word_rows)
    trigram_table = table_from_rows(TRIGRAM_WINDOW_COLUMNS, trigram_rows)
    observable_table = table_from_rows(
        GATE_AUTOMATON_OBSERVABLE_COLUMNS,
        observable_rows,
    )

    checks = {
        "typed_corridor_report_certified": typed_report.get("all_checks_pass")
        is True,
        "symbolic_associativity_report_certified": associativity_report.get(
            "all_checks_pass"
        )
        is True,
        "typed_corridor_schema_available": typed_corridors.get("schema")
        == "c985.d20_signature_boundary_spine_typed_corridors@1",
        "symbolic_associativity_schema_available": symbolic_associativity.get(
            "schema"
        )
        == "c985.d20_symbolic_associativity@1",
        "typed_corridor_tables_available": "corridor_edge_table" in typed_tables.files,
        "symbolic_associativity_tables_available": "symbolic_associativity_table"
        in associativity_tables.files,
        "gate_sequence_matches_typed_corridors": gate_symbols
        == typed_report["witness"]["gate_symbol_sequence"],
        "accepting_states_match_branch_prefixes": branch_prefixes
        == [1, 3, 5, 8, 12, 14],
        "transition_count_is_16": len(transition_rows) == 16,
        "source_to_branch_prefix_is_14": SOURCE_TO_BRANCH_PREFIX == 14,
        "post_branch_tail_count_is_2": observable_values[
            "post_branch_tail_transition_count"
        ]
        == 2,
        "branch_word_lengths_match_expected": [
            int(row["word_length"]) for row in branch_word_rows
        ]
        == [1, 3, 5, 8, 12, 14],
        "source_to_branch_windows_match_expected": [
            (
                int(row["left_symbol_id"]),
                int(row["middle_symbol_id"]),
                int(row["right_symbol_id"]),
            )
            for row in trigram_rows
        ]
        == [
            (5, 5, 0),
            (5, 0, 0),
            (0, 0, 1),
            (0, 1, 3),
            (1, 3, 1),
            (3, 1, 5),
            (1, 5, 3),
            (5, 3, 5),
            (3, 5, 5),
            (5, 5, 3),
            (5, 3, 5),
            (3, 5, 3),
        ],
        "all_source_to_branch_trigrams_are_associativity_certified": observable_values[
            "associativity_certified_window_count"
        ]
        == len(trigram_rows),
        "source_to_branch_unique_trigram_count_is_11": observable_values[
            "source_to_branch_unique_trigram_count"
        ]
        == 11,
        "source_to_branch_canonical_triples_match_expected": canonical_triple_ids
        == [1, 5, 8, 20, 23, 32, 48, 51],
        "source_to_branch_sector_coverage_histogram_matches_expected": [
            sum(1 for row in trigram_rows if int(row["sector_coverage_count"]) == value)
            for value in (3, 4, 5, 6)
        ]
        == [0, 1, 9, 2],
        "source_to_branch_signature_range_matches_expected": (
            min_signature_union,
            max_signature_union,
        )
        == (90, 175),
        "observed_max_below_global_associativity_max": (
            max_signature_union,
            global_max_signature_union,
            observable_values["global_max_signature_gap"],
        )
        == (175, 185, 10),
        "full_sector_windows_use_canonical_triple_32": sorted(
            {int(row["canonical_triple_id"]) for row in full_sector_rows}
        )
        == [32],
        "source_to_branch_gate_symbols_omit_x2_x4": (
            source_gate_symbol_bitset,
            missing_gate_symbol_bitset,
        )
        == (43, 20),
        "transition_table_shape_is_16_by_16": tuple(transition_table.shape)
        == (16, len(AUTOMATON_TRANSITION_COLUMNS)),
        "branch_word_table_shape_is_6_by_14": tuple(branch_word_table.shape)
        == (6, len(BRANCH_WORD_COLUMNS)),
        "trigram_table_shape_is_12_by_20": tuple(trigram_table.shape)
        == (12, len(TRIGRAM_WINDOW_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(GATE_AUTOMATON_OBSERVABLE_COLUMNS)),
    }

    branch_words = [
        {
            "negative_carrier_mask_class_id": int(branch["negative_carrier_mask_class_id"]),
            "accept_state_id": int(branch["first_prefix_length"]),
            "gate_symbol_word": gate_symbols[: int(branch["first_prefix_length"])],
        }
        for branch in branch_rows
    ]
    witness = {
        "gate_symbol_sequence": gate_symbols,
        "accepting_state_ids": branch_prefixes,
        "branch_words": branch_words,
        "source_to_branch_trigram_windows": [
            [int(row["left_symbol_id"]), int(row["middle_symbol_id"]), int(row["right_symbol_id"])]
            for row in trigram_rows
        ],
        "source_to_branch_unique_trigram_count": observable_values[
            "source_to_branch_unique_trigram_count"
        ],
        "source_to_branch_canonical_triple_ids": canonical_triple_ids,
        "source_to_branch_sector_coverage_histogram": [
            {
                "value": value,
                "count": sum(
                    1
                    for row in trigram_rows
                    if int(row["sector_coverage_count"]) == value
                ),
            }
            for value in (3, 4, 5, 6)
        ],
        "full_sector_trigram_windows": [
            [int(row["left_symbol_id"]), int(row["middle_symbol_id"]), int(row["right_symbol_id"])]
            for row in full_sector_rows
        ],
        "source_to_branch_signature_union_range": {
            "min": min_signature_union,
            "max": max_signature_union,
            "global_symbolic_associativity_max": global_max_signature_union,
            "gap_to_global_max": observable_values["global_max_signature_gap"],
        },
        "missing_gate_symbol_ids": decode_bitset(missing_gate_symbol_bitset),
        "transition_table_sha256": sha_array(transition_table),
        "branch_word_table_sha256": sha_array(branch_word_table),
        "trigram_window_table_sha256": sha_array(trigram_table),
        "gate_automaton_observable_table_sha256": sha_array(observable_table),
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_gate_automaton_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_GATE_AUTOMATON_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the typed corridor spine gives a 16-transition gate automaton with six accepting branch states",
            "source-to-branch paths end at states 1, 3, 5, 8, 12, and 14",
            "all 12 length-three gate windows on source-to-branch paths are certified symbolic associativity diamonds",
            "the source-to-branch windows use eight canonical symbolic triples and two full-sector windows",
            "the gate automaton misses the global length-three max-signature triple because gate letters omit x2 and x4",
        ],
    }

    automaton = {
        "schema": "c985.d20_signature_boundary_spine_gate_automaton@1",
        "object": "d20",
        "automaton_rule": {
            "source": "certified typed-corridor gate sequence",
            "states": "state k is the prefix of length k in the entropy-ordered corridor sequence",
            "transitions": "transition k appends the kth certified gate letter",
            "accepting_states": "first-arrival prefixes of negative carrier branches",
            "associativity_comparison": "each length-three gate window is checked against the certified symbolic associativity table",
        },
        "gate_symbol_sequence": witness["gate_symbol_sequence"],
        "accepting_state_ids": witness["accepting_state_ids"],
        "branch_words": witness["branch_words"],
        "source_to_branch_trigram_windows": witness[
            "source_to_branch_trigram_windows"
        ],
        "source_to_branch_canonical_triple_ids": witness[
            "source_to_branch_canonical_triple_ids"
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_gate_automaton@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The typed corridor grammar lifts to a finite gate automaton whose "
            "six source-to-branch paths have 12 length-three gate windows, all "
            "certified by the symbolic associativity diamond; its observed "
            "triple readout reaches signature union 175 but not the global "
            "symbolic maximum 185 because x2 and x4 never appear as gate "
            "letters."
        ),
        "stage_protocol": {
            "draft": "view the typed-corridor gate sequence as a finite path automaton",
            "witness": "materialize branch-accepting states and length-three gate windows",
            "coherence": "check every source-to-branch window against symbolic associativity diamonds",
            "closure": "certify the finite gate automaton without claiming arbitrary-word confluence",
            "emit": "emit gate-automaton JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "typed_corridor_report": input_entry(
                TYPED_CORRIDOR_REPORT,
                {
                    "status": typed_report.get("status"),
                    "certificate_sha256": typed_report.get("certificate_sha256"),
                },
            ),
            "typed_corridors": input_entry(TYPED_CORRIDOR_JSON),
            "typed_corridor_edges": input_entry(TYPED_CORRIDOR_EDGE_CSV),
            "typed_corridor_branches": input_entry(TYPED_CORRIDOR_BRANCH_CSV),
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
            "symbolic_associativity": input_entry(SYMBOLIC_ASSOCIATIVITY_JSON),
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
            "signature_boundary_spine_gate_automaton": relpath(
                OUT_DIR / "signature_boundary_spine_gate_automaton.json"
            ),
            "gate_automaton_transitions_csv": relpath(
                OUT_DIR / "gate_automaton_transitions.csv"
            ),
            "gate_branch_words_csv": relpath(OUT_DIR / "gate_branch_words.csv"),
            "gate_trigram_windows_csv": relpath(
                OUT_DIR / "gate_trigram_windows.csv"
            ),
            "gate_automaton_observables_csv": relpath(
                OUT_DIR / "gate_automaton_observables.csv"
            ),
            "signature_boundary_spine_gate_automaton_tables": relpath(
                OUT_DIR / "signature_boundary_spine_gate_automaton_tables.npz"
            ),
            "signature_boundary_spine_gate_automaton_certificate": relpath(
                OUT_DIR / "signature_boundary_spine_gate_automaton_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the finite gate automaton induced by the typed-corridor sequence",
                "source-to-branch gate words for all six negative carrier branches",
                "associativity-diamond certification for all length-three source-to-branch gate windows",
                "the gap between observed gate-triple signature union 175 and global symbolic-associativity maximum 185",
            ],
            "does_not_certify_because_not_required": [
                "confluence or language recognition for arbitrary gate-letter words",
                "that the automaton is invariant under alternative spine rankings",
                "higher-eigenmode automata",
                "new associator, pentagon, pivotal, spherical, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Turn the gate automaton into a hyperbolic language graph: build the "
            "prefix/trigram state graph of observed gate words, measure its "
            "finite metric boundary, and compare its missing x2/x4 aperture with "
            "the full 56-node symbolic rewrite complex."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_gate_automaton_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified typed-corridor and symbolic-associativity artifacts",
            "materialize the gate automaton and branch-accepting states",
            "enumerate source-to-branch length-three gate windows",
            "verify every gate window against the symbolic associativity diamond table",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_gate_automaton": automaton,
        "gate_automaton_transitions_csv": csv_text(
            AUTOMATON_TRANSITION_COLUMNS,
            transition_rows,
        ),
        "gate_branch_words_csv": csv_text(BRANCH_WORD_COLUMNS, branch_word_rows),
        "gate_trigram_windows_csv": csv_text(TRIGRAM_WINDOW_COLUMNS, trigram_rows),
        "gate_automaton_observables_csv": csv_text(
            GATE_AUTOMATON_OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "gate_automaton_transition_table": transition_table,
        "gate_branch_word_table": branch_word_table,
        "gate_trigram_window_table": trigram_table,
        "gate_automaton_observable_table": observable_table,
        "signature_boundary_spine_gate_automaton_certificate": certificate,
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
        OUT_DIR / "signature_boundary_spine_gate_automaton.json",
        payloads["signature_boundary_spine_gate_automaton"],
    )
    (OUT_DIR / "gate_automaton_transitions.csv").write_text(
        payloads["gate_automaton_transitions_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "gate_branch_words.csv").write_text(
        payloads["gate_branch_words_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "gate_trigram_windows.csv").write_text(
        payloads["gate_trigram_windows_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "gate_automaton_observables.csv").write_text(
        payloads["gate_automaton_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_boundary_spine_gate_automaton_tables.npz",
        gate_automaton_transition_table=payloads[
            "gate_automaton_transition_table"
        ],
        gate_branch_word_table=payloads["gate_branch_word_table"],
        gate_trigram_window_table=payloads["gate_trigram_window_table"],
        gate_automaton_observable_table=payloads[
            "gate_automaton_observable_table"
        ],
    )
    write_json(
        OUT_DIR / "signature_boundary_spine_gate_automaton_certificate.json",
        payloads["signature_boundary_spine_gate_automaton_certificate"],
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
                "accepting_state_ids": witness["accepting_state_ids"],
                "source_to_branch_unique_trigram_count": witness[
                    "source_to_branch_unique_trigram_count"
                ],
                "source_to_branch_canonical_triple_ids": witness[
                    "source_to_branch_canonical_triple_ids"
                ],
                "source_to_branch_signature_union_range": witness[
                    "source_to_branch_signature_union_range"
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
