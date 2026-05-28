from __future__ import annotations

import json
from itertools import combinations
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_boundary_bridge_search import (
        CELL_COMPLEX_EDGES,
        NO_REPAIR_GATE_WORD,
        OBSERVABLE_COLUMNS,
        REWRITE_COMPLEX_EDGES,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        TRACE_NODE_COLUMNS,
        build_context,
        build_trace,
        closure_profile,
        contains_undirected_edge,
        csv_text,
        input_entry,
        load_json,
        padded,
        relpath,
        self_hash,
        sha_array,
        table_from_rows,
        write_json,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_native_trace_insertion import (
        OUT_DIR as NATIVE_INSERTION_DIR,
        STATUS as NATIVE_INSERTION_STATUS,
        trace_metrics,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_rewrite_node_lift import (
        edge_key,
        read_int_csv,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_cycle_ranking import (
        REWRITE_COMPLEX_NODES,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_boundary_bridge_search import (
        CELL_COMPLEX_EDGES,
        NO_REPAIR_GATE_WORD,
        OBSERVABLE_COLUMNS,
        REWRITE_COMPLEX_EDGES,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        TRACE_NODE_COLUMNS,
        build_context,
        build_trace,
        closure_profile,
        contains_undirected_edge,
        csv_text,
        input_entry,
        load_json,
        padded,
        relpath,
        self_hash,
        sha_array,
        table_from_rows,
        write_json,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_native_trace_insertion import (
        OUT_DIR as NATIVE_INSERTION_DIR,
        STATUS as NATIVE_INSERTION_STATUS,
        trace_metrics,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_rewrite_node_lift import (
        edge_key,
        read_int_csv,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_cycle_ranking import (
        REWRITE_COMPLEX_NODES,
    )
    from derive_c985_typed_simple_object_registry import INDEX_PATH
    from paths import D20_INVARIANTS, ROOT


THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_SYMBOLIC_WINDOW_REFINEMENT_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

NATIVE_INSERTION_REPORT = NATIVE_INSERTION_DIR / "report.json"
NATIVE_INSERTION_CERTIFICATE = (
    NATIVE_INSERTION_DIR
    / "signature_boundary_spine_aperture_closure_tail_native_trace_insertion_certificate.json"
)
DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement.py"
)

SUBWINDOW_COLUMNS = [
    "subwindow_id",
    "index_mask",
    "first_symbol_id",
    "second_symbol_id",
    "third_symbol_id",
    "canonical_node_id",
    "signature_union_count",
    "endpoint_window_flag",
    "skip_window_flag",
    "repair_window_flag",
    "neutral_window_flag",
]

SPLIT_COLUMNS = [
    "split_id",
    "inserted_node_id",
    "index_mask",
    "first_symbol_id",
    "second_symbol_id",
    "third_symbol_id",
    "source_node_id",
    "target_node_id",
    "source_to_insert_edge_flag",
    "insert_to_target_edge_flag",
    "valid_rewrite_split_flag",
    "repair_31_28_flag",
    "repair_50_34_flag",
    "direct_variation",
    "split_variation",
    "variation_preserving_flag",
    "refined_trace_node_count",
    *TRACE_NODE_COLUMNS,
    "refined_trace_variation",
    "refined_trace_delta_twice",
    "refined_trace_diameter",
    "refined_trace_radius",
    "selected_refinement_flag",
]

SYMBOLIC_WINDOW_OBSERVABLE_CODES = {
    "local_block_symbol_count": 0,
    "subwindow_count": 1,
    "skip_window_count": 2,
    "endpoint_window_count": 3,
    "valid_split_count": 4,
    "repair_split_count": 5,
    "neutral_split_count": 6,
    "selected_inserted_node_id": 7,
    "selected_index_mask": 8,
    "selected_trace_variation": 9,
    "selected_trace_delta_twice": 10,
    "selected_variation_preserving_flag": 11,
    "gate_closed_path_count": 12,
    "gate_template_count": 13,
    "gate_trace_variation": 14,
    "source_node_id": 15,
    "target_node_id": 16,
    "direct_variation": 17,
    "neutral_inserted_node_id": 18,
    "neutral_variation_preserving_flag": 19,
}


def triple(row: dict[str, int]) -> tuple[int, int, int]:
    return (
        int(row["left_symbol_id"]),
        int(row["middle_symbol_id"]),
        int(row["right_symbol_id"]),
    )


def index_mask(indices: tuple[int, ...]) -> int:
    result = 0
    for index in indices:
        result |= 1 << int(index)
    return result


def find_gate_window_pair(raw_windows: list[dict[str, int]]) -> tuple[int, int]:
    for left_index in range(len(raw_windows) - 1):
        left = raw_windows[left_index]
        right = raw_windows[left_index + 1]
        if (
            int(left["canonical_triple_id"]) == 27
            and int(right["canonical_triple_id"]) == 28
            and int(left["middle_symbol_id"]) == int(right["left_symbol_id"])
            and int(left["right_symbol_id"]) == int(right["middle_symbol_id"])
        ):
            return left_index, left_index + 1
    raise AssertionError("gate 27->28 overlapping window pair not found")


def build_payload_rows() -> dict[str, Any]:
    carrier_adjacency, assoc_by_word, rewrite_edge_by_pair = build_context()
    raw_windows, gate_trace_nodes, _signatures, gate_metrics = build_trace(
        NO_REPAIR_GATE_WORD,
        assoc_by_word,
        rewrite_edge_by_pair,
    )
    gate_trace = tuple(int(value) for value in gate_trace_nodes)
    left_rank, right_rank = find_gate_window_pair(raw_windows)
    left_window = raw_windows[left_rank]
    right_window = raw_windows[right_rank]
    local_block = (
        int(left_window["left_symbol_id"]),
        int(left_window["middle_symbol_id"]),
        int(left_window["right_symbol_id"]),
        int(right_window["right_symbol_id"]),
    )
    source_node = int(left_window["canonical_triple_id"])
    target_node = int(right_window["canonical_triple_id"])
    assoc_by_triple = {triple(row): row for row in read_int_csv(SYMBOLIC_ASSOCIATIVITY_CSV)}
    signatures = {
        int(row["node_id"]): int(row["signature_union_count"])
        for row in read_int_csv(REWRITE_COMPLEX_NODES)
    }
    rewrite_edges = {
        edge_key(row["source_node_id"], row["target_node_id"])
        for row in read_int_csv(REWRITE_COMPLEX_EDGES)
    }
    direct_variation = abs(signatures[target_node] - signatures[source_node])

    subwindow_rows: list[dict[str, int]] = []
    split_rows: list[dict[str, int]] = []
    for subwindow_id, indices in enumerate(combinations(range(4), 3)):
        symbols = tuple(local_block[index] for index in indices)
        assoc = assoc_by_triple[symbols]
        node_id = int(assoc["canonical_triple_id"])
        is_endpoint = int(node_id in {source_node, target_node})
        is_skip = int(not is_endpoint)
        is_repair = int(node_id == 31)
        subwindow_rows.append(
            {
                "subwindow_id": subwindow_id,
                "index_mask": index_mask(indices),
                "first_symbol_id": symbols[0],
                "second_symbol_id": symbols[1],
                "third_symbol_id": symbols[2],
                "canonical_node_id": node_id,
                "signature_union_count": int(assoc["signature_union_count"]),
                "endpoint_window_flag": is_endpoint,
                "skip_window_flag": is_skip,
                "repair_window_flag": is_repair,
                "neutral_window_flag": int(is_skip and not is_repair),
            }
        )
        if not is_skip:
            continue
        source_to_insert = edge_key(source_node, node_id) in rewrite_edges
        insert_to_target = edge_key(node_id, target_node) in rewrite_edges
        refined_trace = (
            gate_trace[: left_rank + 2]
            + (node_id,)
            + gate_trace[left_rank + 2 :]
        )
        metrics = trace_metrics(refined_trace, signatures)
        repair_31 = contains_undirected_edge(refined_trace, 31, 28)
        repair_50 = contains_undirected_edge(refined_trace, 50, 34)
        split_variation = abs(signatures[node_id] - signatures[source_node]) + abs(
            signatures[target_node] - signatures[node_id]
        )
        split_rows.append(
            {
                "split_id": len(split_rows),
                "inserted_node_id": node_id,
                "index_mask": index_mask(indices),
                "first_symbol_id": symbols[0],
                "second_symbol_id": symbols[1],
                "third_symbol_id": symbols[2],
                "source_node_id": source_node,
                "target_node_id": target_node,
                "source_to_insert_edge_flag": int(source_to_insert),
                "insert_to_target_edge_flag": int(insert_to_target),
                "valid_rewrite_split_flag": int(source_to_insert and insert_to_target),
                "repair_31_28_flag": int(repair_31),
                "repair_50_34_flag": int(repair_50),
                "direct_variation": direct_variation,
                "split_variation": split_variation,
                "variation_preserving_flag": int(split_variation == direct_variation),
                "refined_trace_node_count": len(refined_trace),
                **{
                    column: value
                    for column, value in zip(
                        TRACE_NODE_COLUMNS,
                        padded(refined_trace, len(TRACE_NODE_COLUMNS)),
                    )
                },
                "refined_trace_variation": metrics["trace_signature_total_variation"],
                "refined_trace_delta_twice": metrics["metric_gromov_delta_twice"],
                "refined_trace_diameter": metrics["metric_diameter"],
                "refined_trace_radius": metrics["metric_radius"],
                "selected_refinement_flag": int(node_id == 31),
            }
        )

    selected = next(row for row in split_rows if row["selected_refinement_flag"] == 1)
    neutral_row = next(row for row in split_rows if row["selected_refinement_flag"] == 0)
    gate_profile = closure_profile(NO_REPAIR_GATE_WORD, carrier_adjacency)
    observable_values = {
        "local_block_symbol_count": len(local_block),
        "subwindow_count": len(subwindow_rows),
        "skip_window_count": sum(row["skip_window_flag"] for row in subwindow_rows),
        "endpoint_window_count": sum(row["endpoint_window_flag"] for row in subwindow_rows),
        "valid_split_count": sum(row["valid_rewrite_split_flag"] for row in split_rows),
        "repair_split_count": sum(row["repair_31_28_flag"] for row in split_rows),
        "neutral_split_count": sum(
            int(row["repair_31_28_flag"] == 0 and row["repair_50_34_flag"] == 0)
            for row in split_rows
        ),
        "selected_inserted_node_id": selected["inserted_node_id"],
        "selected_index_mask": selected["index_mask"],
        "selected_trace_variation": selected["refined_trace_variation"],
        "selected_trace_delta_twice": selected["refined_trace_delta_twice"],
        "selected_variation_preserving_flag": selected[
            "variation_preserving_flag"
        ],
        "gate_closed_path_count": gate_profile["first_return_closed_path_count"],
        "gate_template_count": gate_profile["normalized_tail_template_count"],
        "gate_trace_variation": int(gate_metrics["trace_signature_total_variation"]),
        "source_node_id": source_node,
        "target_node_id": target_node,
        "direct_variation": direct_variation,
        "neutral_inserted_node_id": neutral_row["inserted_node_id"],
        "neutral_variation_preserving_flag": neutral_row[
            "variation_preserving_flag"
        ],
    }
    observable_rows = [
        {
            "observable_id": index,
            "observable_code": SYMBOLIC_WINDOW_OBSERVABLE_CODES[key],
            "value_x1e12": int(value) * 10**12,
            "aux_id": -1,
        }
        for index, (key, value) in enumerate(observable_values.items())
    ]
    return {
        "gate_trace": gate_trace,
        "local_block": local_block,
        "left_rank": left_rank,
        "right_rank": right_rank,
        "subwindow_rows": subwindow_rows,
        "split_rows": split_rows,
        "observable_values": observable_values,
        "observable_rows": observable_rows,
        "gate_profile": gate_profile,
    }


def build_payloads() -> dict[str, Any]:
    native_report = load_json(NATIVE_INSERTION_REPORT)
    native_certificate = load_json(NATIVE_INSERTION_CERTIFICATE)
    payload_rows = build_payload_rows()
    subwindow_rows = payload_rows["subwindow_rows"]
    split_rows = payload_rows["split_rows"]
    observable_rows = payload_rows["observable_rows"]
    observable_values = payload_rows["observable_values"]
    gate_trace = payload_rows["gate_trace"]
    local_block = payload_rows["local_block"]
    gate_profile = payload_rows["gate_profile"]

    subwindow_table = table_from_rows(SUBWINDOW_COLUMNS, subwindow_rows)
    split_table = table_from_rows(SPLIT_COLUMNS, split_rows)
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    selected = next(row for row in split_rows if row["selected_refinement_flag"] == 1)
    neutral = next(row for row in split_rows if row["selected_refinement_flag"] == 0)
    selected_trace = tuple(
        selected[column] for column in TRACE_NODE_COLUMNS if selected[column] != -1
    )
    checks = {
        "native_trace_insertion_report_certified": native_report.get("status")
        == NATIVE_INSERTION_STATUS,
        "native_trace_insertion_certificate_certified": native_certificate.get("status")
        == NATIVE_INSERTION_STATUS,
        "gate_window_pair_is_27_to_28": (
            observable_values["source_node_id"],
            observable_values["target_node_id"],
            tuple(local_block),
        )
        == (27, 28, (3, 2, 1, 4)),
        "subwindows_are_expected_nodes": [
            row["canonical_node_id"] for row in subwindow_rows
        ]
        == [27, 41, 31, 28],
        "two_skip_windows_both_valid_rewrite_splits": (
            observable_values["skip_window_count"],
            observable_values["valid_split_count"],
        )
        == (2, 2),
        "selected_repair_split_is_node31": (
            observable_values["repair_split_count"],
            observable_values["selected_inserted_node_id"],
            observable_values["selected_index_mask"],
            selected["first_symbol_id"],
            selected["second_symbol_id"],
            selected["third_symbol_id"],
        )
        == (1, 31, 13, 3, 1, 4),
        "neutral_split_is_node41": (
            observable_values["neutral_split_count"],
            observable_values["neutral_inserted_node_id"],
        )
        == (1, 41),
        "selected_trace_matches_native_insertion": selected_trace
        == (48, 42, 27, 31, 28, 34, 29, 45, 29, 28, 34, 44),
        "selected_refinement_preserves_trace_metrics": (
            observable_values["selected_trace_variation"],
            observable_values["selected_trace_delta_twice"],
            observable_values["selected_variation_preserving_flag"],
            selected["refined_trace_diameter"],
            selected["refined_trace_radius"],
        )
        == (185, 2, 1, 5, 3),
        "neutral_refinement_preserves_direct_variation": (
            neutral["split_variation"],
            neutral["direct_variation"],
            neutral["variation_preserving_flag"],
        )
        == (23, 23, 1),
        "gate_carrier_profile_is_unchanged": (
            observable_values["gate_closed_path_count"],
            observable_values["gate_template_count"],
            observable_values["gate_trace_variation"],
        )
        == (30, 9, 185),
        "subwindow_table_shape_matches_codebook": tuple(subwindow_table.shape)
        == (4, len(SUBWINDOW_COLUMNS)),
        "split_table_shape_matches_codebook": tuple(split_table.shape)
        == (2, len(SPLIT_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(SYMBOLIC_WINDOW_OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    witness = {
        "gate_word": list(NO_REPAIR_GATE_WORD),
        "gate_trace": list(gate_trace),
        "local_block": list(local_block),
        "local_window_ranks": [payload_rows["left_rank"], payload_rows["right_rank"]],
        "subwindow_nodes": [
            {
                "symbols": [
                    row["first_symbol_id"],
                    row["second_symbol_id"],
                    row["third_symbol_id"],
                ],
                "node": row["canonical_node_id"],
            }
            for row in subwindow_rows
        ],
        "selected_refinement": {
            "symbols": [
                selected["first_symbol_id"],
                selected["second_symbol_id"],
                selected["third_symbol_id"],
            ],
            "node": selected["inserted_node_id"],
            "trace": list(selected_trace),
            "variation": selected["refined_trace_variation"],
            "delta_twice": selected["refined_trace_delta_twice"],
        },
        "neutral_refinement_node": neutral["inserted_node_id"],
        "gate_profile": {
            "closed_paths": gate_profile["first_return_closed_path_count"],
            "templates": gate_profile["normalized_tail_template_count"],
        },
        "subwindow_table_sha256": sha_array(subwindow_table),
        "split_table_sha256": sha_array(split_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    refinement = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement@1",
        "object": "d20",
        "comparison_rule": {
            "parent": NATIVE_INSERTION_REPORT.relative_to(ROOT).as_posix(),
            "gate_word": list(NO_REPAIR_GATE_WORD),
            "local_block": list(local_block),
            "refinement": "enumerate order-preserving three-symbol subwindows of the four-symbol 27->28 span",
        },
        "summary": {
            "subwindow_nodes": [row["canonical_node_id"] for row in subwindow_rows],
            "selected_inserted_node_id": selected["inserted_node_id"],
            "neutral_inserted_node_id": neutral["inserted_node_id"],
            "gate_closed_paths": gate_profile["first_return_closed_path_count"],
            "gate_templates": gate_profile["normalized_tail_template_count"],
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_SYMBOLIC_WINDOW_REFINEMENT_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the gate's adjacent 27 and 28 windows span the four-symbol block 3,2,1,4",
            "the order-preserving three-symbol subwindows produce nodes 27, 41, 31, and 28",
            "both skip windows are valid 27->node->28 rewrite splits and preserve direct variation",
            "the 3,1,4 skip window is the unique repair split because it inserts node 31",
            "the fixed gate word keeps the 30-closure, 9-template carrier profile",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The symbolic window-refinement layer lifts the native trace "
            "insertion to an associativity-window refinement on the fixed gate "
            "word. The adjacent gate windows 3,2,1 and 2,1,4 span block "
            "3,2,1,4. Its ordered three-symbol subwindows map to nodes 27, "
            "41, 31, and 28. The two skip windows split 27->28 through "
            "existing rewrite edges; 3,2,4 gives neutral node 41, while "
            "3,1,4 gives repair node 31. The selected 31 refinement exactly "
            "matches the certified trace insertion 48,42,27,31,28,34,29,45,"
            "29,28,34,44, preserves variation 185 and delta_twice 2, and "
            "leaves the gate word's 30 closed paths and 9 templates unchanged."
        ),
        "stage_protocol": {
            "draft": "localize the native trace insertion to the overlapping gate windows 27 and 28",
            "witness": "enumerate ordered subwindows of the four-symbol block and split the trace through each skip window",
            "coherence": "compare repair and neutral skip-window refinements against direct variation and gate profile",
            "closure": "certify node31 as the unique repair skip-window refinement of the 27->28 gate span",
            "emit": "emit subwindow, split, observable tables, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "native_trace_insertion_report": input_entry(
                NATIVE_INSERTION_REPORT,
                {
                    "status": native_report.get("status"),
                    "certificate_sha256": native_report.get("certificate_sha256"),
                },
            ),
            "native_trace_insertion_certificate": input_entry(
                NATIVE_INSERTION_CERTIFICATE
            ),
            "symbolic_alphabet": input_entry(SYMBOLIC_ALPHABET_CSV),
            "symbolic_associativity": input_entry(SYMBOLIC_ASSOCIATIVITY_CSV),
            "rewrite_complex_nodes": input_entry(REWRITE_COMPLEX_NODES),
            "rewrite_complex_edges": input_entry(REWRITE_COMPLEX_EDGES),
            "cell_complex_edges": input_entry(CELL_COMPLEX_EDGES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement.json"
            ),
            "aperture_closure_tail_symbolic_window_subwindows_csv": relpath(
                OUT_DIR / "aperture_closure_tail_symbolic_window_subwindows.csv"
            ),
            "aperture_closure_tail_symbolic_window_splits_csv": relpath(
                OUT_DIR / "aperture_closure_tail_symbolic_window_splits.csv"
            ),
            "aperture_closure_tail_symbolic_window_observables_csv": relpath(
                OUT_DIR / "aperture_closure_tail_symbolic_window_observables.csv"
            ),
            "signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement_tables.npz"
            ),
            "signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the fixed gate word's local 27->28 four-symbol span",
                "all ordered three-symbol subwindows of that span",
                "valid rewrite splits through the two skip windows",
                "node31 as the unique repair skip-window refinement",
            ],
            "does_not_certify_because_not_required": [
                "global insertion of derived windows into the normal language compiler",
                "other four-symbol spans outside the fixed gate seam",
                "multi-window refinements beyond the declared local block",
                "compiler lowering behavior",
            ],
        },
        "next_highest_yield_item": (
            "Promote skip-window refinement into a reusable corridor grammar: "
            "enumerate all four-symbol spans whose ordered subwindows contain "
            "a repair split, then test whether this derived-window rule closes "
            "the boundary path language beyond the gate seam."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified native trace-insertion artifacts",
            "find the gate's adjacent 27->28 overlapping windows",
            "enumerate the four ordered three-symbol subwindows",
            "check valid neutral and repair rewrite splits",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement": refinement,
        "aperture_closure_tail_symbolic_window_subwindows_csv": csv_text(
            SUBWINDOW_COLUMNS,
            subwindow_rows,
        ),
        "aperture_closure_tail_symbolic_window_splits_csv": csv_text(
            SPLIT_COLUMNS,
            split_rows,
        ),
        "aperture_closure_tail_symbolic_window_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "subwindow_table": subwindow_table,
        "split_table": split_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement_certificate": certificate,
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
        / "signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement.json",
        payloads[
            "signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement"
        ],
    )
    (OUT_DIR / "aperture_closure_tail_symbolic_window_subwindows.csv").write_text(
        payloads["aperture_closure_tail_symbolic_window_subwindows_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_symbolic_window_splits.csv").write_text(
        payloads["aperture_closure_tail_symbolic_window_splits_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_symbolic_window_observables.csv").write_text(
        payloads["aperture_closure_tail_symbolic_window_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement_tables.npz",
        subwindow_table=payloads["subwindow_table"],
        split_table=payloads["split_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement_certificate"
        ],
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
