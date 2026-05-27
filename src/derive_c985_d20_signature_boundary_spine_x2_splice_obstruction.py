from __future__ import annotations

import json
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_corridor_insertion import (
        OUT_DIR as APERTURE_INSERTION_DIR,
    )
    from .derive_c985_d20_signature_boundary_spine_typed_corridors import (
        OUT_DIR as TYPED_CORRIDOR_DIR,
        RESIDUAL_CHART_CARRIER_CSV,
        SYMBOLIC_ALPHABET_CSV,
    )
    from .derive_c985_d20_signature_residual_cell_complex import (
        EDGE_WITHIN_CENTRAL,
        OUT_DIR as CELL_COMPLEX_DIR,
    )
    from .derive_c985_d20_signature_boundary_spine_routing_prefix import (
        bitset,
        popcount,
        read_int_csv,
        table_from_rows,
    )
    from .derive_c985_d20_symbolic_rewrite_rules import csv_text, histogram
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
        OUT_DIR as APERTURE_INSERTION_DIR,
    )
    from derive_c985_d20_signature_boundary_spine_typed_corridors import (
        OUT_DIR as TYPED_CORRIDOR_DIR,
        RESIDUAL_CHART_CARRIER_CSV,
        SYMBOLIC_ALPHABET_CSV,
    )
    from derive_c985_d20_signature_residual_cell_complex import (
        EDGE_WITHIN_CENTRAL,
        OUT_DIR as CELL_COMPLEX_DIR,
    )
    from derive_c985_d20_signature_boundary_spine_routing_prefix import (
        bitset,
        popcount,
        read_int_csv,
        table_from_rows,
    )
    from derive_c985_d20_symbolic_rewrite_rules import csv_text, histogram
    from derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "c985_d20_signature_boundary_spine_x2_splice_obstruction"
STATUS = "C985_D20_SIGNATURE_BOUNDARY_SPINE_X2_SPLICE_OBSTRUCTION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

APERTURE_INSERTION_REPORT = APERTURE_INSERTION_DIR / "report.json"
APERTURE_INSERTION_JSON = (
    APERTURE_INSERTION_DIR
    / "signature_boundary_spine_aperture_corridor_insertion.json"
)
APERTURE_INSERTION_CANDIDATES = (
    APERTURE_INSERTION_DIR / "aperture_corridor_insertion_candidates.csv"
)
APERTURE_INSERTION_TABLES = (
    APERTURE_INSERTION_DIR
    / "signature_boundary_spine_aperture_corridor_insertion_tables.npz"
)
APERTURE_INSERTION_CERTIFICATE = (
    APERTURE_INSERTION_DIR
    / "signature_boundary_spine_aperture_corridor_insertion_certificate.json"
)

TYPED_CORRIDOR_REPORT = TYPED_CORRIDOR_DIR / "report.json"
TYPED_CORRIDOR_JSON = TYPED_CORRIDOR_DIR / "signature_boundary_spine_typed_corridors.json"
TYPED_CORRIDOR_EDGES = TYPED_CORRIDOR_DIR / "corridor_edge_symbols.csv"
TYPED_CORRIDOR_TABLES = (
    TYPED_CORRIDOR_DIR / "signature_boundary_spine_typed_corridors_tables.npz"
)
TYPED_CORRIDOR_CERTIFICATE = (
    TYPED_CORRIDOR_DIR / "signature_boundary_spine_typed_corridors_certificate.json"
)

CELL_COMPLEX_REPORT = CELL_COMPLEX_DIR / "report.json"
CELL_COMPLEX_JSON = CELL_COMPLEX_DIR / "signature_residual_cell_complex.json"
CELL_COMPLEX_EDGES = CELL_COMPLEX_DIR / "carrier_region_edges.csv"
CELL_COMPLEX_TABLES = CELL_COMPLEX_DIR / "signature_residual_cell_complex_tables.npz"
CELL_COMPLEX_CERTIFICATE = CELL_COMPLEX_DIR / "signature_residual_cell_complex_certificate.json"

DERIVE_SCRIPT = (
    ROOT / "src" / "derive_c985_d20_signature_boundary_spine_x2_splice_obstruction.py"
)
VALIDATOR_SCRIPT = (
    ROOT / "src" / "certify_c985_d20_signature_boundary_spine_x2_splice_obstruction.py"
)

INSERTED_SYMBOL_ID = 2
SELECTED_INSERTION_POSITION = 14
SLOT_POSITIVE_CARRIER_ID = 12
SLOT_NEGATIVE_CARRIER_ID = 4
LAST_SOURCE_TO_BRANCH_CONTACT = 14
POST_BRANCH_TAIL_CONTACTS = [15, 16]

SPLICE_CANDIDATE_COLUMNS = [
    "cell_edge_id",
    "source_carrier_mask_class_id",
    "target_carrier_mask_class_id",
    "edge_partition_code",
    "source_region_code",
    "target_region_code",
    "is_region_boundary",
    "is_positive_negative_boundary",
    "shared_atom_count",
    "shared_atom_bitset",
    "shared_symbol_bitset",
    "shared_symbol_count",
    "x2_shared_flag",
    "x4_shared_flag",
    "single_shared_symbol_flag",
    "incident_to_slot_positive_carrier_flag",
    "incident_to_slot_negative_carrier_flag",
    "boundary_realizable_x2_flag",
    "splice_slot_eligible_flag",
    "positive_internal_x2_flag",
]

X2_NEAR_MISS_COLUMNS = [
    "near_miss_id",
    "cell_edge_id",
    "source_carrier_mask_class_id",
    "target_carrier_mask_class_id",
    "edge_partition_code",
    "source_region_code",
    "target_region_code",
    "shared_atom_bitset",
    "shared_symbol_bitset",
    "single_shared_symbol_flag",
    "incident_to_slot_positive_carrier_flag",
    "incident_to_slot_negative_carrier_flag",
    "boundary_realizable_x2_flag",
    "reason_code",
]

SLOT_AUDIT_COLUMNS = [
    "slot_audit_id",
    "boundary_spine_rank",
    "boundary_mask_edge_id",
    "positive_carrier_mask_class_id",
    "negative_carrier_mask_class_id",
    "shared_symbol_id",
    "x2_contact_flag",
    "selected_slot_boundary_flag",
    "post_branch_tail_flag",
]

SPLICE_OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "carrier_pair_edge_count": 0,
    "positive_negative_boundary_edge_count": 1,
    "shared_x2_edge_count": 2,
    "boundary_shared_x2_edge_count": 3,
    "slot_eligible_x2_edge_count": 4,
    "slot_positive_incident_x2_edge_count": 5,
    "slot_negative_incident_x2_edge_count": 6,
    "single_shared_x2_edge_count": 7,
    "positive_internal_x2_edge_count": 8,
    "existing_spine_x2_gate_count": 9,
    "post_branch_tail_contact_count": 10,
    "post_branch_tail_x2_contact_count": 11,
    "selected_insertion_position": 12,
    "slot_positive_carrier_id": 13,
    "slot_negative_carrier_id": 14,
    "last_source_to_branch_shared_symbol": 15,
    "near_miss_count": 16,
    "actual_splice_possible_flag": 17,
}


def carrier_atom_ids(row: dict[str, int]) -> list[int]:
    return [
        int(row[f"carrier_atom_id_{index}"])
        for index in range(4)
        if int(row[f"carrier_atom_id_{index}"]) >= 0
    ]


def build_payloads() -> dict[str, Any]:
    insertion_report = load_json(APERTURE_INSERTION_REPORT)
    insertion = load_json(APERTURE_INSERTION_JSON)
    insertion_certificate = load_json(APERTURE_INSERTION_CERTIFICATE)
    typed_report = load_json(TYPED_CORRIDOR_REPORT)
    typed_corridors = load_json(TYPED_CORRIDOR_JSON)
    typed_certificate = load_json(TYPED_CORRIDOR_CERTIFICATE)
    cell_report = load_json(CELL_COMPLEX_REPORT)
    cell_complex = load_json(CELL_COMPLEX_JSON)
    cell_certificate = load_json(CELL_COMPLEX_CERTIFICATE)

    insertion_tables = np.load(APERTURE_INSERTION_TABLES, allow_pickle=False)
    typed_tables = np.load(TYPED_CORRIDOR_TABLES, allow_pickle=False)
    cell_tables = np.load(CELL_COMPLEX_TABLES, allow_pickle=False)
    insertion_candidate_table = np.asarray(
        insertion_tables["candidate_table"], dtype=np.int64
    )
    typed_edge_table = np.asarray(typed_tables["corridor_edge_table"], dtype=np.int64)
    cell_edge_table = np.asarray(cell_tables["carrier_region_edge_table"], dtype=np.int64)

    carrier_rows = {
        int(row["carrier_mask_class_id"]): row
        for row in read_int_csv(RESIDUAL_CHART_CARRIER_CSV)
    }
    atom_to_symbol = {
        int(row["atom_id"]): int(row["symbol_id"])
        for row in read_int_csv(SYMBOLIC_ALPHABET_CSV)
    }
    cell_edge_rows_source = read_int_csv(CELL_COMPLEX_EDGES)
    typed_edge_rows = read_int_csv(TYPED_CORRIDOR_EDGES)

    candidate_rows: list[dict[str, int]] = []
    for row in cell_edge_rows_source:
        source = int(row["source_carrier_mask_class_id"])
        target = int(row["target_carrier_mask_class_id"])
        source_atoms = carrier_atom_ids(carrier_rows[source])
        target_atoms = carrier_atom_ids(carrier_rows[target])
        shared_atoms = sorted(set(source_atoms) & set(target_atoms))
        shared_symbols = sorted({atom_to_symbol[atom_id] for atom_id in shared_atoms})
        shared_symbol_bitset = bitset(shared_symbols)
        x2_shared = int(INSERTED_SYMBOL_ID in shared_symbols)
        boundary_realizable = int(
            x2_shared
            and int(row["is_positive_negative_boundary"]) == 1
            and len(shared_symbols) == 1
        )
        incident_positive = int(
            source == SLOT_POSITIVE_CARRIER_ID or target == SLOT_POSITIVE_CARRIER_ID
        )
        incident_negative = int(
            source == SLOT_NEGATIVE_CARRIER_ID or target == SLOT_NEGATIVE_CARRIER_ID
        )
        candidate_rows.append(
            {
                "cell_edge_id": int(row["cell_edge_id"]),
                "source_carrier_mask_class_id": source,
                "target_carrier_mask_class_id": target,
                "edge_partition_code": int(row["edge_partition_code"]),
                "source_region_code": int(row["source_region_code"]),
                "target_region_code": int(row["target_region_code"]),
                "is_region_boundary": int(row["is_region_boundary"]),
                "is_positive_negative_boundary": int(
                    row["is_positive_negative_boundary"]
                ),
                "shared_atom_count": len(shared_atoms),
                "shared_atom_bitset": bitset(shared_atoms),
                "shared_symbol_bitset": shared_symbol_bitset,
                "shared_symbol_count": popcount(shared_symbol_bitset),
                "x2_shared_flag": x2_shared,
                "x4_shared_flag": int(4 in shared_symbols),
                "single_shared_symbol_flag": int(len(shared_symbols) == 1),
                "incident_to_slot_positive_carrier_flag": incident_positive,
                "incident_to_slot_negative_carrier_flag": incident_negative,
                "boundary_realizable_x2_flag": boundary_realizable,
                "splice_slot_eligible_flag": int(
                    boundary_realizable and (incident_positive or incident_negative)
                ),
                "positive_internal_x2_flag": int(
                    x2_shared
                    and int(row["source_region_code"]) > 0
                    and int(row["target_region_code"]) > 0
                    and int(row["is_positive_negative_boundary"]) == 0
                ),
            }
        )

    x2_rows = [row for row in candidate_rows if int(row["x2_shared_flag"]) == 1]
    near_miss_rows: list[dict[str, int]] = []
    for near_miss_id, row in enumerate(x2_rows):
        near_miss_rows.append(
            {
                "near_miss_id": near_miss_id,
                "cell_edge_id": int(row["cell_edge_id"]),
                "source_carrier_mask_class_id": int(
                    row["source_carrier_mask_class_id"]
                ),
                "target_carrier_mask_class_id": int(
                    row["target_carrier_mask_class_id"]
                ),
                "edge_partition_code": int(row["edge_partition_code"]),
                "source_region_code": int(row["source_region_code"]),
                "target_region_code": int(row["target_region_code"]),
                "shared_atom_bitset": int(row["shared_atom_bitset"]),
                "shared_symbol_bitset": int(row["shared_symbol_bitset"]),
                "single_shared_symbol_flag": int(row["single_shared_symbol_flag"]),
                "incident_to_slot_positive_carrier_flag": int(
                    row["incident_to_slot_positive_carrier_flag"]
                ),
                "incident_to_slot_negative_carrier_flag": int(
                    row["incident_to_slot_negative_carrier_flag"]
                ),
                "boundary_realizable_x2_flag": int(
                    row["boundary_realizable_x2_flag"]
                ),
                "reason_code": 1
                if int(row["is_positive_negative_boundary"]) == 0
                else 2,
            }
        )

    slot_contact_ranks = [LAST_SOURCE_TO_BRANCH_CONTACT, *POST_BRANCH_TAIL_CONTACTS]
    slot_rows = [
        row
        for row in typed_edge_rows
        if int(row["boundary_spine_rank"]) in slot_contact_ranks
    ]
    slot_audit_rows: list[dict[str, int]] = []
    for index, row in enumerate(slot_rows):
        rank = int(row["boundary_spine_rank"])
        slot_audit_rows.append(
            {
                "slot_audit_id": index,
                "boundary_spine_rank": rank,
                "boundary_mask_edge_id": int(row["boundary_mask_edge_id"]),
                "positive_carrier_mask_class_id": int(
                    row["positive_carrier_mask_class_id"]
                ),
                "negative_carrier_mask_class_id": int(
                    row["negative_carrier_mask_class_id"]
                ),
                "shared_symbol_id": int(row["shared_symbol_id"]),
                "x2_contact_flag": int(int(row["shared_symbol_id"]) == INSERTED_SYMBOL_ID),
                "selected_slot_boundary_flag": int(
                    rank == LAST_SOURCE_TO_BRANCH_CONTACT
                ),
                "post_branch_tail_flag": int(rank in POST_BRANCH_TAIL_CONTACTS),
            }
        )

    positive_negative_rows = [
        row for row in candidate_rows if int(row["is_positive_negative_boundary"]) == 1
    ]
    boundary_x2_rows = [
        row for row in positive_negative_rows if int(row["x2_shared_flag"]) == 1
    ]
    eligible_x2_rows = [
        row for row in candidate_rows if int(row["splice_slot_eligible_flag"]) == 1
    ]
    slot_positive_x2_rows = [
        row
        for row in x2_rows
        if int(row["incident_to_slot_positive_carrier_flag"]) == 1
    ]
    slot_negative_x2_rows = [
        row
        for row in x2_rows
        if int(row["incident_to_slot_negative_carrier_flag"]) == 1
    ]
    typed_x2_rows = [
        row for row in typed_edge_rows if int(row["shared_symbol_id"]) == INSERTED_SYMBOL_ID
    ]
    post_tail_x2_rows = [
        row
        for row in slot_audit_rows
        if int(row["post_branch_tail_flag"]) == 1
        and int(row["x2_contact_flag"]) == 1
    ]
    last_contact = next(
        row
        for row in typed_edge_rows
        if int(row["boundary_spine_rank"]) == LAST_SOURCE_TO_BRANCH_CONTACT
    )

    observable_values = {
        "carrier_pair_edge_count": len(candidate_rows),
        "positive_negative_boundary_edge_count": len(positive_negative_rows),
        "shared_x2_edge_count": len(x2_rows),
        "boundary_shared_x2_edge_count": len(boundary_x2_rows),
        "slot_eligible_x2_edge_count": len(eligible_x2_rows),
        "slot_positive_incident_x2_edge_count": len(slot_positive_x2_rows),
        "slot_negative_incident_x2_edge_count": len(slot_negative_x2_rows),
        "single_shared_x2_edge_count": sum(
            int(row["single_shared_symbol_flag"]) for row in x2_rows
        ),
        "positive_internal_x2_edge_count": sum(
            int(row["positive_internal_x2_flag"]) for row in x2_rows
        ),
        "existing_spine_x2_gate_count": len(typed_x2_rows),
        "post_branch_tail_contact_count": len(POST_BRANCH_TAIL_CONTACTS),
        "post_branch_tail_x2_contact_count": len(post_tail_x2_rows),
        "selected_insertion_position": SELECTED_INSERTION_POSITION,
        "slot_positive_carrier_id": SLOT_POSITIVE_CARRIER_ID,
        "slot_negative_carrier_id": SLOT_NEGATIVE_CARRIER_ID,
        "last_source_to_branch_shared_symbol": int(last_contact["shared_symbol_id"]),
        "near_miss_count": len(near_miss_rows),
        "actual_splice_possible_flag": int(len(eligible_x2_rows) > 0),
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

    candidate_table = table_from_rows(SPLICE_CANDIDATE_COLUMNS, candidate_rows)
    near_miss_table = table_from_rows(X2_NEAR_MISS_COLUMNS, near_miss_rows)
    slot_audit_table = table_from_rows(SLOT_AUDIT_COLUMNS, slot_audit_rows)
    observable_table = table_from_rows(SPLICE_OBSERVABLE_COLUMNS, observable_rows)

    checks = {
        "aperture_insertion_report_certified": insertion_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CORRIDOR_INSERTION_CERTIFIED",
        "aperture_insertion_certificate_certified": insertion_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CORRIDOR_INSERTION_CERTIFIED",
        "typed_corridor_report_certified": typed_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_TYPED_CORRIDORS_CERTIFIED",
        "typed_corridor_certificate_certified": typed_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_TYPED_CORRIDORS_CERTIFIED",
        "cell_complex_report_certified": cell_report.get("status")
        == "C985_D20_SIGNATURE_RESIDUAL_CELL_COMPLEX_CERTIFIED",
        "cell_complex_certificate_certified": cell_certificate.get("status")
        == "C985_D20_SIGNATURE_RESIDUAL_CELL_COMPLEX_CERTIFIED",
        "aperture_insertion_schema_available": insertion.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_corridor_insertion@1",
        "typed_corridor_schema_available": typed_corridors.get("schema")
        == "c985.d20_signature_boundary_spine_typed_corridors@1",
        "cell_complex_schema_available": cell_complex.get("schema")
        == "c985.d20_signature_residual_cell_complex@1",
        "insertion_candidate_table_shape_is_15_by_15": tuple(
            insertion_candidate_table.shape
        )
        == (15, 15),
        "typed_corridor_edge_table_shape_is_16_by_23": tuple(typed_edge_table.shape)
        == (16, 23),
        "cell_complex_edge_table_shape_is_44_by_13": tuple(cell_edge_table.shape)
        == (44, 13),
        "selected_insertion_is_after_state_14": insertion_report["witness"][
            "selected_candidate_id"
        ]
        == SELECTED_INSERTION_POSITION,
        "selected_virtual_window_is_node_42": insertion_report["witness"][
            "selected_new_window"
        ]["canonical_triple_id"]
        == 42,
        "slot_contact_is_positive_12_negative_4": (
            int(last_contact["positive_carrier_mask_class_id"]),
            int(last_contact["negative_carrier_mask_class_id"]),
        )
        == (SLOT_POSITIVE_CARRIER_ID, SLOT_NEGATIVE_CARRIER_ID),
        "slot_contact_shared_symbol_is_x3": int(last_contact["shared_symbol_id"]) == 3,
        "carrier_pair_edge_count_is_44": len(candidate_rows) == 44,
        "positive_negative_boundary_edge_count_is_16": len(positive_negative_rows)
        == 16,
        "shared_x2_edge_count_is_10": len(x2_rows) == 10,
        "boundary_shared_x2_edge_count_is_0": len(boundary_x2_rows) == 0,
        "slot_eligible_x2_edge_count_is_0": len(eligible_x2_rows) == 0,
        "slot_positive_incident_x2_edge_count_is_4": len(slot_positive_x2_rows)
        == 4,
        "slot_negative_incident_x2_edge_count_is_0": len(slot_negative_x2_rows)
        == 0,
        "single_shared_x2_edge_count_is_6": observable_values[
            "single_shared_x2_edge_count"
        ]
        == 6,
        "positive_internal_x2_edge_count_is_10": observable_values[
            "positive_internal_x2_edge_count"
        ]
        == 10,
        "existing_spine_x2_gate_count_is_0": len(typed_x2_rows) == 0,
        "post_branch_tail_x2_contact_count_is_0": len(post_tail_x2_rows) == 0,
        "post_branch_tail_symbols_are_x1_x0": [
            int(row["shared_symbol_id"])
            for row in slot_audit_rows
            if int(row["post_branch_tail_flag"]) == 1
        ]
        == [1, 0],
        "all_x2_near_misses_are_within_central_positive_region": all(
            int(row["edge_partition_code"]) == EDGE_WITHIN_CENTRAL
            for row in x2_rows
        ),
        "x2_near_miss_edges_match_expected": [
            int(row["cell_edge_id"]) for row in x2_rows
        ]
        == [6, 7, 8, 9, 12, 13, 14, 38, 39, 41],
        "slot_positive_incident_near_miss_edges_match_expected": [
            int(row["cell_edge_id"]) for row in slot_positive_x2_rows
        ]
        == [9, 14, 39, 41],
        "candidate_table_shape_is_44_by_20": tuple(candidate_table.shape)
        == (44, len(SPLICE_CANDIDATE_COLUMNS)),
        "near_miss_table_shape_is_10_by_14": tuple(near_miss_table.shape)
        == (10, len(X2_NEAR_MISS_COLUMNS)),
        "slot_audit_table_shape_is_3_by_9": tuple(slot_audit_table.shape)
        == (3, len(SLOT_AUDIT_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(SPLICE_OBSERVABLE_COLUMNS)),
    }

    witness = {
        "selected_virtual_insertion": {
            "candidate_id": SELECTED_INSERTION_POSITION,
            "slot_after_state": LAST_SOURCE_TO_BRANCH_CONTACT,
            "required_symbol_id": INSERTED_SYMBOL_ID,
            "slot_positive_carrier_mask_class_id": SLOT_POSITIVE_CARRIER_ID,
            "slot_negative_carrier_mask_class_id": SLOT_NEGATIVE_CARRIER_ID,
        },
        "carrier_pair_edge_count": len(candidate_rows),
        "positive_negative_boundary_edge_count": len(positive_negative_rows),
        "shared_x2_edge_count": len(x2_rows),
        "boundary_shared_x2_edge_count": len(boundary_x2_rows),
        "slot_eligible_x2_edge_count": len(eligible_x2_rows),
        "slot_positive_incident_x2_edge_ids": [
            int(row["cell_edge_id"]) for row in slot_positive_x2_rows
        ],
        "slot_negative_incident_x2_edge_ids": [
            int(row["cell_edge_id"]) for row in slot_negative_x2_rows
        ],
        "x2_near_miss_edge_ids": [int(row["cell_edge_id"]) for row in x2_rows],
        "x2_near_miss_partition_histogram": histogram(
            [int(row["edge_partition_code"]) for row in x2_rows]
        ),
        "positive_negative_boundary_shared_symbol_histogram": histogram(
            [
                int(row["shared_symbol_bitset"])
                for row in positive_negative_rows
            ]
        ),
        "slot_audit_rows": slot_audit_rows,
        "actual_splice_possible": False,
        "candidate_table_sha256": sha_array(candidate_table),
        "near_miss_table_sha256": sha_array(near_miss_table),
        "slot_audit_table_sha256": sha_array(slot_audit_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    obstruction = {
        "schema": "c985.d20_signature_boundary_spine_x2_splice_obstruction@1",
        "object": "d20",
        "splice_obstruction_rule": {
            "source": "certified virtual x2 insertion plus the certified 44-edge carrier-mask cell complex",
            "realizable_contact": "a spliceable x2 contact must be a positive/negative boundary carrier-pair edge sharing x2",
            "slot": "after source-to-branch state 14, whose current typed contact is positive carrier 12 to negative carrier 4",
            "result": "the finite carrier-pair boundary has no such x2 edge; all x2 carrier-pair contacts are central-positive internal edges",
        },
        "selected_virtual_insertion": witness["selected_virtual_insertion"],
        "actual_splice_possible": False,
        "x2_near_miss_edge_ids": witness["x2_near_miss_edge_ids"],
        "slot_positive_incident_x2_edge_ids": witness[
            "slot_positive_incident_x2_edge_ids"
        ],
        "slot_audit_rows": slot_audit_rows,
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_x2_splice_obstruction_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_X2_SPLICE_OBSTRUCTION_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the selected virtual x2 insertion targets the slot after boundary-spine state 14",
            "the certified carrier-mask cell complex has 10 x2-sharing carrier-pair edges",
            "none of those x2-sharing edges lies on the positive/negative boundary used by the typed spine",
            "four x2 near misses touch the slot's positive carrier 12, but all are central-positive internal edges",
            "the current post-branch tail contacts are x1 and x0, so no existing tail contact realizes the virtual x2 splice",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_x2_splice_obstruction@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The virtual x2 aperture insertion cannot be realized as an actual "
            "carrier-pair boundary splice in the current certified finite "
            "boundary: every x2 carrier-pair contact is internal to the "
            "positive central region, and the positive/negative boundary has "
            "zero shared-x2 edges."
        ),
        "stage_protocol": {
            "draft": "treat the selected virtual x2 insertion as a request for a real carrier-pair boundary contact",
            "witness": "enumerate all 44 carrier-pair cell-complex edges and all shared-x2 near misses",
            "coherence": "check boundary membership, slot incidence, post-tail symbols, and typed-spine x2 absence",
            "closure": "certify the finite obstruction without claiming there is no x2 contact outside the current carrier-mask boundary model",
            "emit": "emit x2-splice obstruction JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "aperture_insertion_report": input_entry(
                APERTURE_INSERTION_REPORT,
                {
                    "status": insertion_report.get("status"),
                    "certificate_sha256": insertion_report.get(
                        "certificate_sha256"
                    ),
                },
            ),
            "aperture_insertion": input_entry(APERTURE_INSERTION_JSON),
            "aperture_insertion_candidates": input_entry(
                APERTURE_INSERTION_CANDIDATES
            ),
            "aperture_insertion_tables": input_entry(APERTURE_INSERTION_TABLES),
            "aperture_insertion_certificate": input_entry(
                APERTURE_INSERTION_CERTIFICATE
            ),
            "typed_corridor_report": input_entry(
                TYPED_CORRIDOR_REPORT,
                {
                    "status": typed_report.get("status"),
                    "certificate_sha256": typed_report.get("certificate_sha256"),
                },
            ),
            "typed_corridors": input_entry(TYPED_CORRIDOR_JSON),
            "typed_corridor_edges": input_entry(TYPED_CORRIDOR_EDGES),
            "typed_corridor_tables": input_entry(TYPED_CORRIDOR_TABLES),
            "typed_corridor_certificate": input_entry(TYPED_CORRIDOR_CERTIFICATE),
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
            "residual_chart_carriers": input_entry(RESIDUAL_CHART_CARRIER_CSV),
            "symbolic_alphabet": input_entry(SYMBOLIC_ALPHABET_CSV),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_x2_splice_obstruction": relpath(
                OUT_DIR / "signature_boundary_spine_x2_splice_obstruction.json"
            ),
            "x2_splice_candidate_edges_csv": relpath(
                OUT_DIR / "x2_splice_candidate_edges.csv"
            ),
            "x2_splice_near_misses_csv": relpath(
                OUT_DIR / "x2_splice_near_misses.csv"
            ),
            "x2_splice_slot_audit_csv": relpath(
                OUT_DIR / "x2_splice_slot_audit.csv"
            ),
            "x2_splice_observables_csv": relpath(
                OUT_DIR / "x2_splice_observables.csv"
            ),
            "signature_boundary_spine_x2_splice_obstruction_tables": relpath(
                OUT_DIR / "signature_boundary_spine_x2_splice_obstruction_tables.npz"
            ),
            "signature_boundary_spine_x2_splice_obstruction_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_x2_splice_obstruction_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the finite search over all 44 carrier-pair edges in the certified residual cell complex",
                "that no positive/negative carrier-boundary edge shares x2",
                "that no existing typed-spine or post-branch-tail contact has shared gate x2",
                "the four central-positive x2 near misses incident to slot positive carrier 12",
            ],
            "does_not_certify_because_not_required": [
                "nonexistence of x2 contacts outside the current 14-carrier mask quotient",
                "a positive-internal detour that leaves and later returns to the boundary spine",
                "a new carrier mask class or new raw relation outside the certified residual cell complex",
                "the subsequent x4 insertion needed to reach aperture node 44",
            ],
        },
        "next_highest_yield_item": (
            "Certify the positive-internal x2 detour fan incident to carrier 12: "
            "measure whether edges 9, 14, 39, and 41 can form a controlled "
            "off-boundary excursion that realizes node 42 before returning to "
            "the typed boundary."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_x2_splice_obstruction_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified aperture-insertion, typed-corridor, and residual cell-complex artifacts",
            "enumerate all carrier-pair edges and their shared symbolic alphabet letters",
            "prove the positive/negative carrier boundary contains no shared-x2 edge",
            "audit the selected slot and post-branch tail contacts for x2 absence",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_x2_splice_obstruction": obstruction,
        "x2_splice_candidate_edges_csv": csv_text(
            SPLICE_CANDIDATE_COLUMNS,
            candidate_rows,
        ),
        "x2_splice_near_misses_csv": csv_text(
            X2_NEAR_MISS_COLUMNS,
            near_miss_rows,
        ),
        "x2_splice_slot_audit_csv": csv_text(
            SLOT_AUDIT_COLUMNS,
            slot_audit_rows,
        ),
        "x2_splice_observables_csv": csv_text(
            SPLICE_OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "candidate_table": candidate_table,
        "near_miss_table": near_miss_table,
        "slot_audit_table": slot_audit_table,
        "observable_table": observable_table,
        "signature_boundary_spine_x2_splice_obstruction_certificate": certificate,
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
        OUT_DIR / "signature_boundary_spine_x2_splice_obstruction.json",
        payloads["signature_boundary_spine_x2_splice_obstruction"],
    )
    (OUT_DIR / "x2_splice_candidate_edges.csv").write_text(
        payloads["x2_splice_candidate_edges_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "x2_splice_near_misses.csv").write_text(
        payloads["x2_splice_near_misses_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "x2_splice_slot_audit.csv").write_text(
        payloads["x2_splice_slot_audit_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "x2_splice_observables.csv").write_text(
        payloads["x2_splice_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_boundary_spine_x2_splice_obstruction_tables.npz",
        candidate_table=payloads["candidate_table"],
        near_miss_table=payloads["near_miss_table"],
        slot_audit_table=payloads["slot_audit_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR / "signature_boundary_spine_x2_splice_obstruction_certificate.json",
        payloads["signature_boundary_spine_x2_splice_obstruction_certificate"],
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
                "actual_splice_possible": witness["actual_splice_possible"],
                "shared_x2_edge_count": witness["shared_x2_edge_count"],
                "boundary_shared_x2_edge_count": witness[
                    "boundary_shared_x2_edge_count"
                ],
                "slot_positive_incident_x2_edge_ids": witness[
                    "slot_positive_incident_x2_edge_ids"
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
