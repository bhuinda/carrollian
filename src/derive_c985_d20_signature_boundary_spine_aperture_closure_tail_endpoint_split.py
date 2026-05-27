from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_rich_outlier_geometry import (
        OUT_DIR as CLOSURE_OUTLIER_DIR,
        SELECTED_BRANCH_COLUMNS,
        STATUS as CLOSURE_OUTLIER_STATUS,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_overhead3_weak_promotion_audit import (
        ORIGIN_CARRIER_ID,
        first_return_closed,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_rank104_strongification_branch_geometry import (
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        SYMBOLIC_ALPHABET_CSV,
        build_carrier_adjacency,
        carrier_paths,
        csv_text,
        input_entry,
        read_int_csv,
        relpath,
        self_hash,
        sha_array,
        table_from_rows,
        write_json,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    from derive_c985_d20_signature_boundary_spine_aperture_closure_rich_outlier_geometry import (
        OUT_DIR as CLOSURE_OUTLIER_DIR,
        SELECTED_BRANCH_COLUMNS,
        STATUS as CLOSURE_OUTLIER_STATUS,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_overhead3_weak_promotion_audit import (
        ORIGIN_CARRIER_ID,
        first_return_closed,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_rank104_strongification_branch_geometry import (
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        SYMBOLIC_ALPHABET_CSV,
        build_carrier_adjacency,
        carrier_paths,
        csv_text,
        input_entry,
        read_int_csv,
        relpath,
        self_hash,
        sha_array,
        table_from_rows,
        write_json,
    )
    from derive_c985_typed_simple_object_registry import INDEX_PATH
    from paths import D20_INVARIANTS, ROOT


THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_endpoint_split"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_ENDPOINT_SPLIT_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

CLOSURE_OUTLIER_REPORT = CLOSURE_OUTLIER_DIR / "report.json"
CLOSURE_OUTLIER_JSON = (
    CLOSURE_OUTLIER_DIR
    / "signature_boundary_spine_aperture_closure_rich_outlier_geometry.json"
)
CLOSURE_OUTLIER_SELECTED_BRANCHES = (
    CLOSURE_OUTLIER_DIR / "aperture_closure_outlier_selected_branches.csv"
)
CLOSURE_OUTLIER_TABLES = (
    CLOSURE_OUTLIER_DIR
    / "signature_boundary_spine_aperture_closure_rich_outlier_geometry_tables.npz"
)
CLOSURE_OUTLIER_CERTIFICATE = (
    CLOSURE_OUTLIER_DIR
    / "signature_boundary_spine_aperture_closure_rich_outlier_geometry_certificate.json"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_endpoint_split.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_endpoint_split.py"
)

WITNESS_IDS = (9, 23)
BASELINE_OUTLIER_ID = 9
RANK104_OUTLIER_ID = 23
SHARED_TAIL_WORD = (5, 2, 1, 4, 5)
TAIL_START_SYMBOL_INDEX = {
    BASELINE_OUTLIER_ID: 4,
    RANK104_OUTLIER_ID: 5,
}
TAIL_ENTRY_CARRIERS = (9, 10, 11)
FIXED_TAIL_ATOMS = (19, 7, 4, 12, 19)
FINAL_PRE_ORIGIN_CARRIER_ID = 13

MAX_WORD_LENGTH = 10
MAX_CARRIER_LENGTH = MAX_WORD_LENGTH + 1
MAX_EDGE_LENGTH = MAX_WORD_LENGTH
MAX_TAIL_CARRIER_LENGTH = len(SHARED_TAIL_WORD) + 1
MAX_TAIL_EDGE_LENGTH = len(SHARED_TAIL_WORD)

WORD_COLUMNS = [f"symbol_{index}_id" for index in range(MAX_WORD_LENGTH)]
CARRIER_COLUMNS = [f"carrier_{index}_id" for index in range(MAX_CARRIER_LENGTH)]
EDGE_COLUMNS = [f"cell_edge_{index}_id" for index in range(MAX_EDGE_LENGTH)]
ATOM_COLUMNS = [f"selected_atom_{index}_id" for index in range(MAX_EDGE_LENGTH)]
TAIL_CARRIER_COLUMNS = [
    f"tail_carrier_{index}_id" for index in range(MAX_TAIL_CARRIER_LENGTH)
]
TAIL_EDGE_COLUMNS = [
    f"tail_cell_edge_{index}_id" for index in range(MAX_TAIL_EDGE_LENGTH)
]
TAIL_ATOM_COLUMNS = [
    f"tail_selected_atom_{index}_id" for index in range(MAX_TAIL_EDGE_LENGTH)
]

WITNESS_SUMMARY_COLUMNS = [
    "witness_id",
    "word_length",
    *WORD_COLUMNS,
    "shared_tail_start_symbol_index",
    "pre_tail_symbol_count",
    "full_carrier_path_count",
    "first_return_closed_path_count",
    "normalized_tail_template_count",
    "tail_entry_carrier_count",
    "tail_entry_9_path_count",
    "tail_entry_10_path_count",
    "tail_entry_11_path_count",
    "template_lift_count_min",
    "template_lift_count_max",
    "fixed_tail_atom_sequence_flag",
    "final_pre_origin_carrier_id",
    "final_pre_origin_path_count",
    "intermediate_origin_hit_count",
]

CLOSED_PATH_COLUMNS = [
    "witness_id",
    "closed_path_id",
    "word_length",
    "shared_tail_start_symbol_index",
    "normalized_tail_template_id",
    "tail_entry_carrier_id",
    "final_pre_origin_carrier_id",
    "first_return_closed_flag",
    *CARRIER_COLUMNS,
    *EDGE_COLUMNS,
    *ATOM_COLUMNS,
    *TAIL_CARRIER_COLUMNS,
    *TAIL_EDGE_COLUMNS,
    *TAIL_ATOM_COLUMNS,
]

TAIL_TEMPLATE_COLUMNS = [
    "normalized_tail_template_id",
    "tail_entry_carrier_id",
    "baseline_outlier_path_count",
    "rank104_outlier_path_count",
    "rank104_to_baseline_multiplier_x1e6",
    *TAIL_CARRIER_COLUMNS,
    *TAIL_EDGE_COLUMNS,
    *TAIL_ATOM_COLUMNS,
]

ENDPOINT_COLUMNS = [
    "witness_id",
    "tail_entry_carrier_id",
    "normalized_tail_template_count",
    "closed_path_count",
    "path_count_per_template_min",
    "path_count_per_template_max",
]

OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "baseline_closed_path_count": 0,
    "rank104_closed_path_count": 1,
    "closure_multiplier_x1e6": 2,
    "normalized_tail_template_count": 3,
    "baseline_template_lift_count": 4,
    "rank104_template_lift_count": 5,
    "tail_entry_carrier_count": 6,
    "tail_entry_9_baseline_count": 7,
    "tail_entry_9_rank104_count": 8,
    "tail_entry_10_baseline_count": 9,
    "tail_entry_10_rank104_count": 10,
    "tail_entry_11_baseline_count": 11,
    "tail_entry_11_rank104_count": 12,
    "fixed_tail_atom_sequence_flag": 13,
    "final_pre_origin_carrier_id": 14,
    "intermediate_origin_hit_count": 15,
}


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} is not a JSON object")
    return payload


def read_int_dict_csv(path: Path) -> list[dict[str, int]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            {key: int(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def padded(values: tuple[int, ...], length: int) -> tuple[int, ...]:
    return values + tuple(-1 for _ in range(length - len(values)))


def selected_word(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(row[column] for column in WORD_COLUMNS[: row["word_length"]])


def shared_tail_start(word: tuple[int, ...]) -> int:
    starts = [
        index
        for index in range(len(word) - len(SHARED_TAIL_WORD) + 1)
        if word[index : index + len(SHARED_TAIL_WORD)] == SHARED_TAIL_WORD
    ]
    if not starts:
        raise AssertionError(f"shared tail word absent from {word}")
    return starts[-1]


def first_return_flag(carriers: tuple[int, ...]) -> int:
    return int(
        carriers[-1] == ORIGIN_CARRIER_ID
        and ORIGIN_CARRIER_ID not in carriers[1:-1]
    )


def tail_slices(
    state: tuple[int, tuple[int, ...], tuple[int, ...], tuple[int, ...]],
    start_index: int,
) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    _start, carriers, edge_ids, atom_ids = state
    return (
        carriers[start_index:],
        edge_ids[start_index:],
        atom_ids[start_index:],
    )


def build_payloads() -> dict[str, Any]:
    closure_report = load_json(CLOSURE_OUTLIER_REPORT)
    closure_json = load_json(CLOSURE_OUTLIER_JSON)
    closure_certificate = load_json(CLOSURE_OUTLIER_CERTIFICATE)
    cell_report = load_json(CELL_COMPLEX_REPORT)
    cell_certificate = load_json(CELL_COMPLEX_CERTIFICATE)
    selected_rows = read_int_dict_csv(CLOSURE_OUTLIER_SELECTED_BRANCHES)
    selected_by_id = {row["witness_id"]: row for row in selected_rows}

    alphabet_rows = read_int_csv(SYMBOLIC_ALPHABET_CSV)
    atom_to_symbol = {
        int(row["atom_id"]): int(row["symbol_id"]) for row in alphabet_rows
    }
    adjacency, _carriers = build_carrier_adjacency(
        read_int_csv(CELL_COMPLEX_EDGES),
        atom_to_symbol,
    )

    full_states_by_witness: dict[int, list[tuple[int, tuple[int, ...], tuple[int, ...], tuple[int, ...]]]] = {}
    closed_by_witness: dict[int, list[tuple[int, tuple[int, ...], tuple[int, ...], tuple[int, ...]]]] = {}
    template_counts_by_witness: dict[int, Counter[tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]]] = {}

    for witness_id in WITNESS_IDS:
        word = selected_word(selected_by_id[witness_id])
        start_index = shared_tail_start(word)
        if start_index != TAIL_START_SYMBOL_INDEX[witness_id]:
            raise AssertionError("unexpected shared tail start")
        full_states = carrier_paths(word, adjacency)
        closed_states = first_return_closed(full_states)
        full_states_by_witness[witness_id] = full_states
        closed_by_witness[witness_id] = closed_states
        template_counts_by_witness[witness_id] = Counter(
            tail_slices(state, start_index) for state in closed_states
        )

    normalized_templates = sorted(
        template_counts_by_witness[BASELINE_OUTLIER_ID],
        key=lambda template: template[0],
    )
    template_id_by_carriers = {
        template[0]: index for index, template in enumerate(normalized_templates)
    }
    summary_rows = []
    closed_path_rows = []
    endpoint_rows = []
    for witness_id in WITNESS_IDS:
        word = selected_word(selected_by_id[witness_id])
        start_index = TAIL_START_SYMBOL_INDEX[witness_id]
        closed_states = closed_by_witness[witness_id]
        template_counts = template_counts_by_witness[witness_id]
        endpoint_counts = Counter(template[0][0] for template in template_counts for _ in range(template_counts[template]))
        lift_counts = list(template_counts.values())
        final_pre_origin_counts = Counter(state[1][-2] for state in closed_states)
        intermediate_origin_hits = sum(
            1 for _start, carriers, _edges, _atoms in closed_states if ORIGIN_CARRIER_ID in carriers[1:-1]
        )
        summary_rows.append(
            {
                "witness_id": witness_id,
                "word_length": len(word),
                **{
                    column: value
                    for column, value in zip(WORD_COLUMNS, padded(word, MAX_WORD_LENGTH))
                },
                "shared_tail_start_symbol_index": start_index,
                "pre_tail_symbol_count": start_index,
                "full_carrier_path_count": len(full_states_by_witness[witness_id]),
                "first_return_closed_path_count": len(closed_states),
                "normalized_tail_template_count": len(template_counts),
                "tail_entry_carrier_count": len(endpoint_counts),
                "tail_entry_9_path_count": endpoint_counts[9],
                "tail_entry_10_path_count": endpoint_counts[10],
                "tail_entry_11_path_count": endpoint_counts[11],
                "template_lift_count_min": min(lift_counts),
                "template_lift_count_max": max(lift_counts),
                "fixed_tail_atom_sequence_flag": int(
                    all(template[2] == FIXED_TAIL_ATOMS for template in template_counts)
                ),
                "final_pre_origin_carrier_id": FINAL_PRE_ORIGIN_CARRIER_ID,
                "final_pre_origin_path_count": final_pre_origin_counts[
                    FINAL_PRE_ORIGIN_CARRIER_ID
                ],
                "intermediate_origin_hit_count": intermediate_origin_hits,
            }
        )
        for endpoint in TAIL_ENTRY_CARRIERS:
            member_counts = [
                count
                for template, count in template_counts.items()
                if template[0][0] == endpoint
            ]
            endpoint_rows.append(
                {
                    "witness_id": witness_id,
                    "tail_entry_carrier_id": endpoint,
                    "normalized_tail_template_count": len(member_counts),
                    "closed_path_count": sum(member_counts),
                    "path_count_per_template_min": min(member_counts),
                    "path_count_per_template_max": max(member_counts),
                }
            )
        for path_id, state in enumerate(closed_states):
            _start, carriers, edge_ids, atom_ids = state
            tail_carriers, tail_edges, tail_atoms = tail_slices(state, start_index)
            template_id = template_id_by_carriers[tail_carriers]
            closed_path_rows.append(
                {
                    "witness_id": witness_id,
                    "closed_path_id": path_id,
                    "word_length": len(word),
                    "shared_tail_start_symbol_index": start_index,
                    "normalized_tail_template_id": template_id,
                    "tail_entry_carrier_id": tail_carriers[0],
                    "final_pre_origin_carrier_id": carriers[-2],
                    "first_return_closed_flag": first_return_flag(carriers),
                    **{
                        column: value
                        for column, value in zip(
                            CARRIER_COLUMNS,
                            padded(carriers, MAX_CARRIER_LENGTH),
                        )
                    },
                    **{
                        column: value
                        for column, value in zip(
                            EDGE_COLUMNS,
                            padded(edge_ids, MAX_EDGE_LENGTH),
                        )
                    },
                    **{
                        column: value
                        for column, value in zip(
                            ATOM_COLUMNS,
                            padded(atom_ids, MAX_EDGE_LENGTH),
                        )
                    },
                    **{
                        column: value
                        for column, value in zip(TAIL_CARRIER_COLUMNS, tail_carriers)
                    },
                    **{
                        column: value
                        for column, value in zip(TAIL_EDGE_COLUMNS, tail_edges)
                    },
                    **{
                        column: value
                        for column, value in zip(TAIL_ATOM_COLUMNS, tail_atoms)
                    },
                }
            )

    template_rows = []
    for template_id, template in enumerate(normalized_templates):
        tail_carriers, tail_edges, tail_atoms = template
        baseline_count = template_counts_by_witness[BASELINE_OUTLIER_ID][template]
        rank104_count = template_counts_by_witness[RANK104_OUTLIER_ID][template]
        template_rows.append(
            {
                "normalized_tail_template_id": template_id,
                "tail_entry_carrier_id": tail_carriers[0],
                "baseline_outlier_path_count": baseline_count,
                "rank104_outlier_path_count": rank104_count,
                "rank104_to_baseline_multiplier_x1e6": rank104_count
                * 10**6
                // baseline_count,
                **{
                    column: value
                    for column, value in zip(TAIL_CARRIER_COLUMNS, tail_carriers)
                },
                **{
                    column: value
                    for column, value in zip(TAIL_EDGE_COLUMNS, tail_edges)
                },
                **{
                    column: value
                    for column, value in zip(TAIL_ATOM_COLUMNS, tail_atoms)
                },
            }
        )

    summary_table = table_from_rows(WITNESS_SUMMARY_COLUMNS, summary_rows)
    closed_path_table = table_from_rows(CLOSED_PATH_COLUMNS, closed_path_rows)
    template_table = table_from_rows(TAIL_TEMPLATE_COLUMNS, template_rows)
    endpoint_table = table_from_rows(ENDPOINT_COLUMNS, endpoint_rows)
    observable_values = {
        "baseline_closed_path_count": summary_rows[0]["first_return_closed_path_count"],
        "rank104_closed_path_count": summary_rows[1]["first_return_closed_path_count"],
        "closure_multiplier_x1e6": summary_rows[1]["first_return_closed_path_count"]
        * 10**6
        // summary_rows[0]["first_return_closed_path_count"],
        "normalized_tail_template_count": len(normalized_templates),
        "baseline_template_lift_count": summary_rows[0]["template_lift_count_min"],
        "rank104_template_lift_count": summary_rows[1]["template_lift_count_min"],
        "tail_entry_carrier_count": len(TAIL_ENTRY_CARRIERS),
        "tail_entry_9_baseline_count": summary_rows[0]["tail_entry_9_path_count"],
        "tail_entry_9_rank104_count": summary_rows[1]["tail_entry_9_path_count"],
        "tail_entry_10_baseline_count": summary_rows[0]["tail_entry_10_path_count"],
        "tail_entry_10_rank104_count": summary_rows[1]["tail_entry_10_path_count"],
        "tail_entry_11_baseline_count": summary_rows[0]["tail_entry_11_path_count"],
        "tail_entry_11_rank104_count": summary_rows[1]["tail_entry_11_path_count"],
        "fixed_tail_atom_sequence_flag": int(
            all(row["fixed_tail_atom_sequence_flag"] == 1 for row in summary_rows)
        ),
        "final_pre_origin_carrier_id": FINAL_PRE_ORIGIN_CARRIER_ID,
        "intermediate_origin_hit_count": sum(
            row["intermediate_origin_hit_count"] for row in summary_rows
        ),
    }
    observable_rows = [
        {
            "observable_id": index,
            "observable_code": OBSERVABLE_CODES[key],
            "value_x1e12": int(value) * 10**12,
            "aux_id": -1,
        }
        for index, (key, value) in enumerate(observable_values.items())
    ]
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    checks = {
        "closure_outlier_report_certified": closure_report.get("status")
        == CLOSURE_OUTLIER_STATUS,
        "closure_outlier_certificate_certified": closure_certificate.get("status")
        == CLOSURE_OUTLIER_STATUS,
        "closure_outlier_schema_available": closure_json.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_closure_rich_outlier_geometry@1",
        "cell_complex_report_certified": cell_report.get("status")
        == "C985_D20_SIGNATURE_RESIDUAL_CELL_COMPLEX_CERTIFIED",
        "cell_complex_certificate_certified": cell_certificate.get("status")
        == "C985_D20_SIGNATURE_RESIDUAL_CELL_COMPLEX_CERTIFIED",
        "selected_branch_table_shape_matches_parent": len(selected_rows) == 3
        and len(SELECTED_BRANCH_COLUMNS) == 40,
        "selected_words_have_shared_tail_at_expected_indices": all(
            shared_tail_start(selected_word(selected_by_id[witness_id]))
            == TAIL_START_SYMBOL_INDEX[witness_id]
            for witness_id in WITNESS_IDS
        ),
        "closed_path_counts_match_parent_12_and_24": [
            row["first_return_closed_path_count"] for row in summary_rows
        ]
        == [12, 24],
        "full_path_counts_are_120_and_240": [
            row["full_carrier_path_count"] for row in summary_rows
        ]
        == [120, 240],
        "tail_template_sets_are_identical": set(
            template_counts_by_witness[BASELINE_OUTLIER_ID]
        )
        == set(template_counts_by_witness[RANK104_OUTLIER_ID]),
        "six_normalized_tail_templates": len(normalized_templates) == 6,
        "template_lift_counts_double_uniformly": all(
            row["baseline_outlier_path_count"] == 2
            and row["rank104_outlier_path_count"] == 4
            and row["rank104_to_baseline_multiplier_x1e6"] == 2_000_000
            for row in template_rows
        ),
        "tail_entry_endpoint_counts_double": endpoint_rows
        == [
            {
                "witness_id": 9,
                "tail_entry_carrier_id": 9,
                "normalized_tail_template_count": 3,
                "closed_path_count": 6,
                "path_count_per_template_min": 2,
                "path_count_per_template_max": 2,
            },
            {
                "witness_id": 9,
                "tail_entry_carrier_id": 10,
                "normalized_tail_template_count": 1,
                "closed_path_count": 2,
                "path_count_per_template_min": 2,
                "path_count_per_template_max": 2,
            },
            {
                "witness_id": 9,
                "tail_entry_carrier_id": 11,
                "normalized_tail_template_count": 2,
                "closed_path_count": 4,
                "path_count_per_template_min": 2,
                "path_count_per_template_max": 2,
            },
            {
                "witness_id": 23,
                "tail_entry_carrier_id": 9,
                "normalized_tail_template_count": 3,
                "closed_path_count": 12,
                "path_count_per_template_min": 4,
                "path_count_per_template_max": 4,
            },
            {
                "witness_id": 23,
                "tail_entry_carrier_id": 10,
                "normalized_tail_template_count": 1,
                "closed_path_count": 4,
                "path_count_per_template_min": 4,
                "path_count_per_template_max": 4,
            },
            {
                "witness_id": 23,
                "tail_entry_carrier_id": 11,
                "normalized_tail_template_count": 2,
                "closed_path_count": 8,
                "path_count_per_template_min": 4,
                "path_count_per_template_max": 4,
            },
        ],
        "fixed_tail_atom_sequence_is_19_7_4_12_19": all(
            row["fixed_tail_atom_sequence_flag"] == 1 for row in summary_rows
        )
        and all(tuple(row[column] for column in TAIL_ATOM_COLUMNS) == FIXED_TAIL_ATOMS for row in template_rows),
        "all_closed_paths_are_first_return_and_finish_through_carrier13": all(
            row["first_return_closed_flag"] == 1
            and row["final_pre_origin_carrier_id"] == FINAL_PRE_ORIGIN_CARRIER_ID
            for row in closed_path_rows
        ),
        "summary_table_shape_matches_codebook": tuple(summary_table.shape)
        == (2, len(WITNESS_SUMMARY_COLUMNS)),
        "closed_path_table_shape_matches_codebook": tuple(closed_path_table.shape)
        == (36, len(CLOSED_PATH_COLUMNS)),
        "template_table_shape_matches_codebook": tuple(template_table.shape)
        == (6, len(TAIL_TEMPLATE_COLUMNS)),
        "endpoint_table_shape_matches_codebook": tuple(endpoint_table.shape)
        == (6, len(ENDPOINT_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    witness = {
        "baseline_outlier": {
            "witness_id": BASELINE_OUTLIER_ID,
            "word": list(selected_word(selected_by_id[BASELINE_OUTLIER_ID])),
            "shared_tail_start_symbol_index": TAIL_START_SYMBOL_INDEX[
                BASELINE_OUTLIER_ID
            ],
            "closed_path_count": summary_rows[0]["first_return_closed_path_count"],
            "normalized_tail_template_count": len(normalized_templates),
            "template_lift_count": summary_rows[0]["template_lift_count_min"],
            "tail_entry_counts": {
                "9": summary_rows[0]["tail_entry_9_path_count"],
                "10": summary_rows[0]["tail_entry_10_path_count"],
                "11": summary_rows[0]["tail_entry_11_path_count"],
            },
        },
        "rank104_outlier": {
            "witness_id": RANK104_OUTLIER_ID,
            "word": list(selected_word(selected_by_id[RANK104_OUTLIER_ID])),
            "shared_tail_start_symbol_index": TAIL_START_SYMBOL_INDEX[
                RANK104_OUTLIER_ID
            ],
            "closed_path_count": summary_rows[1]["first_return_closed_path_count"],
            "normalized_tail_template_count": len(normalized_templates),
            "template_lift_count": summary_rows[1]["template_lift_count_min"],
            "tail_entry_counts": {
                "9": summary_rows[1]["tail_entry_9_path_count"],
                "10": summary_rows[1]["tail_entry_10_path_count"],
                "11": summary_rows[1]["tail_entry_11_path_count"],
            },
        },
        "shared_tail_word": list(SHARED_TAIL_WORD),
        "fixed_tail_atom_sequence": list(FIXED_TAIL_ATOMS),
        "normalized_tail_templates": [
            {
                "template_id": row["normalized_tail_template_id"],
                "tail_entry_carrier_id": row["tail_entry_carrier_id"],
                "carrier_tail": [row[column] for column in TAIL_CARRIER_COLUMNS],
                "edge_tail": [row[column] for column in TAIL_EDGE_COLUMNS],
                "baseline_count": row["baseline_outlier_path_count"],
                "rank104_count": row["rank104_outlier_path_count"],
            }
            for row in template_rows
        ],
        "summary_table_sha256": sha_array(summary_table),
        "closed_path_table_sha256": sha_array(closed_path_table),
        "template_table_sha256": sha_array(template_table),
        "endpoint_table_sha256": sha_array(endpoint_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    endpoint_split = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_endpoint_split@1",
        "object": "d20",
        "comparison_rule": {
            "baseline_outlier": BASELINE_OUTLIER_ID,
            "rank104_outlier": RANK104_OUTLIER_ID,
            "shared_tail_word": list(SHARED_TAIL_WORD),
            "normalized_tail_template": "carrier/edge/atom suffix induced by the shared tail word",
        },
        "summary": {
            "baseline_closed_path_count": summary_rows[0][
                "first_return_closed_path_count"
            ],
            "rank104_closed_path_count": summary_rows[1][
                "first_return_closed_path_count"
            ],
            "normalized_tail_template_count": len(normalized_templates),
            "baseline_template_lift_count": summary_rows[0][
                "template_lift_count_min"
            ],
            "rank104_template_lift_count": summary_rows[1][
                "template_lift_count_min"
            ],
            "tail_entry_counts": {
                str(row["witness_id"]): {
                    "9": row["tail_entry_9_path_count"],
                    "10": row["tail_entry_10_path_count"],
                    "11": row["tail_entry_11_path_count"],
                }
                for row in summary_rows
            },
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_endpoint_split_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_ENDPOINT_SPLIT_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "witnesses 9 and 23 use the same six normalized carrier-tail templates for the shared tail word x5,x2,x1,x4,x5",
            "witness 9 has two first-return lifts of each tail template, giving 12 closed paths",
            "witness 23 has four first-return lifts of each tail template, giving 24 closed paths",
            "tail-entry carrier endpoint counts double uniformly: 9 has 6/2/4 over carriers 9/10/11, while 23 has 12/4/8",
            "all closed paths use the fixed tail atom sequence 19,7,4,12,19 and return through carrier 13 into origin carrier 12",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_endpoint_split@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The 12/24 closure multiplicity split is a prefix-lift split over "
            "the same six carrier-tail templates. Both closure-rich outliers "
            "share the tail word x5,x2,x1,x4,x5, the same tail atom sequence "
            "19,7,4,12,19, and the same return through carrier 13 into origin "
            "carrier 12. Witness 9 lifts each normalized tail template twice; "
            "witness 23 lifts each one four times. The tail-entry endpoint "
            "counts therefore double uniformly across carriers 9, 10, and 11."
        ),
        "stage_protocol": {
            "draft": "take the shared closure tail from the closure-rich outlier certificate",
            "witness": "enumerate first-return closed carrier paths for witnesses 9 and 23",
            "coherence": "normalize carrier/edge/atom suffix templates for the shared tail word",
            "closure": "certify that the 12/24 split is uniform doubling of template lifts and endpoint counts",
            "emit": "emit summaries, closed paths, normalized templates, endpoint counts, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "closure_outlier_report": input_entry(
                CLOSURE_OUTLIER_REPORT,
                {
                    "status": closure_report.get("status"),
                    "certificate_sha256": closure_report.get("certificate_sha256"),
                },
            ),
            "closure_outlier_json": input_entry(CLOSURE_OUTLIER_JSON),
            "closure_outlier_selected_branches": input_entry(
                CLOSURE_OUTLIER_SELECTED_BRANCHES
            ),
            "closure_outlier_tables": input_entry(CLOSURE_OUTLIER_TABLES),
            "closure_outlier_certificate": input_entry(CLOSURE_OUTLIER_CERTIFICATE),
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
            "symbolic_alphabet": input_entry(SYMBOLIC_ALPHABET_CSV),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_aperture_closure_tail_endpoint_split": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_endpoint_split.json"
            ),
            "aperture_closure_tail_witness_summaries_csv": relpath(
                OUT_DIR / "aperture_closure_tail_witness_summaries.csv"
            ),
            "aperture_closure_tail_closed_paths_csv": relpath(
                OUT_DIR / "aperture_closure_tail_closed_paths.csv"
            ),
            "aperture_closure_tail_templates_csv": relpath(
                OUT_DIR / "aperture_closure_tail_templates.csv"
            ),
            "aperture_closure_tail_endpoint_counts_csv": relpath(
                OUT_DIR / "aperture_closure_tail_endpoint_counts.csv"
            ),
            "aperture_closure_tail_observables_csv": relpath(
                OUT_DIR / "aperture_closure_tail_observables.csv"
            ),
            "signature_boundary_spine_aperture_closure_tail_endpoint_split_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_endpoint_split_tables.npz"
            ),
            "signature_boundary_spine_aperture_closure_tail_endpoint_split_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_endpoint_split_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the first-return closed carrier paths for witnesses 9 and 23",
                "the six normalized carrier-tail templates for the shared tail word",
                "the uniform two-versus-four lift count per normalized template",
                "the doubled endpoint counts across tail-entry carriers 9, 10, and 11",
                "the fixed tail atom sequence and final carrier13-to-origin closure",
            ],
            "does_not_certify_because_not_required": [
                "non-first-return carrier paths ending away from origin",
                "closure-rich outliers outside witnesses 9 and 23",
                "edit costs above three",
                "categorical pivotal, spherical, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Lift the six normalized tail templates back to rewrite nodes 54 and 45: "
            "identify which carrier-tail templates are responsible for the delta_twice "
            "increase in witness 23 despite its lower signature variation."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_endpoint_split_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified closure-rich outlier geometry artifacts",
            "recompute rooted carrier paths for witnesses 9 and 23 from the residual cell complex",
            "filter first-return closed paths and normalize the shared tail word suffix",
            "check uniform template doubling and endpoint count doubling",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_closure_tail_endpoint_split": endpoint_split,
        "aperture_closure_tail_witness_summaries_csv": csv_text(
            WITNESS_SUMMARY_COLUMNS,
            summary_rows,
        ),
        "aperture_closure_tail_closed_paths_csv": csv_text(
            CLOSED_PATH_COLUMNS,
            closed_path_rows,
        ),
        "aperture_closure_tail_templates_csv": csv_text(
            TAIL_TEMPLATE_COLUMNS,
            template_rows,
        ),
        "aperture_closure_tail_endpoint_counts_csv": csv_text(
            ENDPOINT_COLUMNS,
            endpoint_rows,
        ),
        "aperture_closure_tail_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "summary_table": summary_table,
        "closed_path_table": closed_path_table,
        "template_table": template_table,
        "endpoint_table": endpoint_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_closure_tail_endpoint_split_certificate": certificate,
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
        / "signature_boundary_spine_aperture_closure_tail_endpoint_split.json",
        payloads["signature_boundary_spine_aperture_closure_tail_endpoint_split"],
    )
    (OUT_DIR / "aperture_closure_tail_witness_summaries.csv").write_text(
        payloads["aperture_closure_tail_witness_summaries_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_closed_paths.csv").write_text(
        payloads["aperture_closure_tail_closed_paths_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_templates.csv").write_text(
        payloads["aperture_closure_tail_templates_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_endpoint_counts.csv").write_text(
        payloads["aperture_closure_tail_endpoint_counts_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_observables.csv").write_text(
        payloads["aperture_closure_tail_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_endpoint_split_tables.npz",
        summary_table=payloads["summary_table"],
        closed_path_table=payloads["closed_path_table"],
        template_table=payloads["template_table"],
        endpoint_table=payloads["endpoint_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_endpoint_split_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_closure_tail_endpoint_split_certificate"
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
                "baseline_outlier": witness["baseline_outlier"],
                "rank104_outlier": witness["rank104_outlier"],
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
