from __future__ import annotations

import json
from collections import Counter
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
        TARGET_DELTA_TWICE,
        TARGET_VARIATION_INCLUSIVE_BOUND,
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
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_rewrite_node_lift import (
        edge_key,
        read_int_csv,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge import (
        OUT_DIR as VIRTUAL_GRAFT_DIR,
        STATUS as VIRTUAL_GRAFT_STATUS,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_cycle_ranking import (
        APERTURE_NODE_ID,
        GEODESIC_NODE_IDS,
        REWRITE_COMPLEX_NODES,
        STRICT_INTERMEDIATE_NODE_ID,
        gromov_delta_twice,
        shortest_paths,
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
        TARGET_DELTA_TWICE,
        TARGET_VARIATION_INCLUSIVE_BOUND,
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
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_rewrite_node_lift import (
        edge_key,
        read_int_csv,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge import (
        OUT_DIR as VIRTUAL_GRAFT_DIR,
        STATUS as VIRTUAL_GRAFT_STATUS,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_cycle_ranking import (
        APERTURE_NODE_ID,
        GEODESIC_NODE_IDS,
        REWRITE_COMPLEX_NODES,
        STRICT_INTERMEDIATE_NODE_ID,
        gromov_delta_twice,
        shortest_paths,
    )
    from derive_c985_typed_simple_object_registry import INDEX_PATH
    from paths import D20_INVARIANTS, ROOT


THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_native_trace_insertion"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_NATIVE_TRACE_INSERTION_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

VIRTUAL_GRAFT_REPORT = VIRTUAL_GRAFT_DIR / "report.json"
VIRTUAL_GRAFT_CERTIFICATE = (
    VIRTUAL_GRAFT_DIR
    / "signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge_certificate.json"
)
DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_native_trace_insertion.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_native_trace_insertion.py"
)

SUBSTITUTION_OPERATION_CODE = 0
INSERTION_OPERATION_CODE = 1

SUMMARY_COLUMNS = [
    "operation_code",
    "attempt_count",
    "valid_rewrite_path_count",
    "repair_edge_candidate_count",
    "delta2_variation_le223_count",
    "variation185_count",
    "selected_realization_count",
]

CANDIDATE_COLUMNS = [
    "candidate_id",
    "operation_code",
    "insert_after_trace_rank",
    "substitute_trace_rank",
    "original_node_id",
    "patch_node_id",
    "trace_node_count",
    *TRACE_NODE_COLUMNS,
    "repair_31_28_flag",
    "repair_50_34_flag",
    "metric_gromov_delta_twice",
    "trace_signature_total_variation",
    "metric_diameter",
    "metric_radius",
    "variation_preserving_flag",
    "selected_realization_flag",
]

NATIVE_INSERTION_OBSERVABLE_CODES = {
    "gate_trace_node_count": 0,
    "gate_trace_variation": 1,
    "gate_delta_twice": 2,
    "gate_closed_path_count": 3,
    "gate_template_count": 4,
    "gate_native_repair_flag": 5,
    "substitution_attempt_count": 6,
    "substitution_valid_path_count": 7,
    "substitution_repair_candidate_count": 8,
    "substitution_delta2_variation_le223_count": 9,
    "insertion_attempt_count": 10,
    "insertion_valid_path_count": 11,
    "insertion_repair_candidate_count": 12,
    "insertion_delta2_variation_le223_count": 13,
    "insertion_variation185_count": 14,
    "selected_insert_after_trace_rank": 15,
    "selected_inserted_node_id": 16,
    "selected_trace_variation": 17,
    "selected_trace_delta_twice": 18,
    "selected_trace_node_count": 19,
    "selected_31_28_repair_flag": 20,
    "selected_50_34_repair_flag": 21,
    "accepted_31_28_candidate_count": 22,
    "accepted_50_34_candidate_count": 23,
}


def trace_is_valid(
    trace: tuple[int, ...],
    rewrite_edges: set[tuple[int, int]],
) -> bool:
    return all(
        source == target or edge_key(source, target) in rewrite_edges
        for source, target in zip(trace, trace[1:])
    )


def trace_metrics(
    trace: tuple[int, ...],
    signatures: dict[int, int],
) -> dict[str, int]:
    all_nodes: list[int] = []
    for node_id in [*GEODESIC_NODE_IDS, *trace]:
        if node_id not in all_nodes:
            all_nodes.append(int(node_id))
    rank_by_node = {node_id: rank for rank, node_id in enumerate(all_nodes)}
    adjacency = np.zeros((len(all_nodes), len(all_nodes)), dtype=np.int8)
    for source, target in [
        *zip(trace, trace[1:]),
        (STRICT_INTERMEDIATE_NODE_ID, APERTURE_NODE_ID),
    ]:
        if source == target:
            continue
        adjacency[rank_by_node[source], rank_by_node[target]] = 1
        adjacency[rank_by_node[target], rank_by_node[source]] = 1
    distances = shortest_paths(adjacency)
    return {
        "trace_signature_total_variation": int(
            sum(
                abs(signatures[trace[index + 1]] - signatures[trace[index]])
                for index in range(len(trace) - 1)
            )
        ),
        "metric_gromov_delta_twice": gromov_delta_twice(distances),
        "metric_diameter": int(np.max(distances)),
        "metric_radius": int(np.min(np.max(distances, axis=1))),
    }


def collapsed(values: list[int]) -> tuple[int, ...]:
    result: list[int] = []
    for value in values:
        if not result or result[-1] != value:
            result.append(value)
    return tuple(result)


def operation_rows(
    gate_trace: tuple[int, ...],
    node_ids: list[int],
    rewrite_edges: set[tuple[int, int]],
    signatures: dict[int, int],
) -> tuple[list[dict[str, int]], list[dict[str, int]]]:
    summary_by_operation: dict[int, Counter[str]] = {
        SUBSTITUTION_OPERATION_CODE: Counter(),
        INSERTION_OPERATION_CODE: Counter(),
    }
    candidate_rows: list[dict[str, int]] = []

    def observe_candidate(
        *,
        operation_code: int,
        insert_after_trace_rank: int,
        substitute_trace_rank: int,
        original_node_id: int,
        patch_node_id: int,
        candidate_trace: tuple[int, ...],
    ) -> None:
        summary = summary_by_operation[operation_code]
        summary["attempt_count"] += 1
        if not trace_is_valid(candidate_trace, rewrite_edges):
            return
        summary["valid_rewrite_path_count"] += 1
        repair_31 = contains_undirected_edge(candidate_trace, 31, 28)
        repair_50 = contains_undirected_edge(candidate_trace, 50, 34)
        if not (repair_31 or repair_50):
            return
        summary["repair_edge_candidate_count"] += 1
        metrics = trace_metrics(candidate_trace, signatures)
        if (
            metrics["metric_gromov_delta_twice"] != TARGET_DELTA_TWICE
            or metrics["trace_signature_total_variation"]
            > TARGET_VARIATION_INCLUSIVE_BOUND
        ):
            return
        summary["delta2_variation_le223_count"] += 1
        if metrics["trace_signature_total_variation"] == 185:
            summary["variation185_count"] += 1
        selected = int(
            operation_code == INSERTION_OPERATION_CODE
            and insert_after_trace_rank == 2
            and patch_node_id == 31
            and metrics["trace_signature_total_variation"] == 185
            and repair_31
        )
        summary["selected_realization_count"] += selected
        candidate_rows.append(
            {
                "candidate_id": len(candidate_rows),
                "operation_code": operation_code,
                "insert_after_trace_rank": insert_after_trace_rank,
                "substitute_trace_rank": substitute_trace_rank,
                "original_node_id": original_node_id,
                "patch_node_id": patch_node_id,
                "trace_node_count": len(candidate_trace),
                **{
                    column: value
                    for column, value in zip(
                        TRACE_NODE_COLUMNS,
                        padded(candidate_trace, len(TRACE_NODE_COLUMNS)),
                    )
                },
                "repair_31_28_flag": int(repair_31),
                "repair_50_34_flag": int(repair_50),
                "metric_gromov_delta_twice": metrics["metric_gromov_delta_twice"],
                "trace_signature_total_variation": metrics[
                    "trace_signature_total_variation"
                ],
                "metric_diameter": metrics["metric_diameter"],
                "metric_radius": metrics["metric_radius"],
                "variation_preserving_flag": int(
                    metrics["trace_signature_total_variation"] == 185
                ),
                "selected_realization_flag": selected,
            }
        )

    for trace_rank in range(1, len(gate_trace) - 1):
        original_node = gate_trace[trace_rank]
        for node_id in node_ids:
            if node_id == original_node:
                continue
            candidate = list(gate_trace)
            candidate[trace_rank] = node_id
            candidate_trace = collapsed(candidate)
            if candidate_trace[0] != gate_trace[0] or candidate_trace[-1] != gate_trace[-1]:
                continue
            observe_candidate(
                operation_code=SUBSTITUTION_OPERATION_CODE,
                insert_after_trace_rank=-1,
                substitute_trace_rank=trace_rank,
                original_node_id=original_node,
                patch_node_id=node_id,
                candidate_trace=candidate_trace,
            )

    for trace_rank in range(len(gate_trace) - 1):
        for node_id in node_ids:
            if node_id in {gate_trace[trace_rank], gate_trace[trace_rank + 1]}:
                continue
            candidate_trace = (
                gate_trace[: trace_rank + 1]
                + (node_id,)
                + gate_trace[trace_rank + 1 :]
            )
            observe_candidate(
                operation_code=INSERTION_OPERATION_CODE,
                insert_after_trace_rank=trace_rank,
                substitute_trace_rank=-1,
                original_node_id=-1,
                patch_node_id=node_id,
                candidate_trace=candidate_trace,
            )

    summary_rows = [
        {
            "operation_code": operation_code,
            "attempt_count": summary["attempt_count"],
            "valid_rewrite_path_count": summary["valid_rewrite_path_count"],
            "repair_edge_candidate_count": summary["repair_edge_candidate_count"],
            "delta2_variation_le223_count": summary[
                "delta2_variation_le223_count"
            ],
            "variation185_count": summary["variation185_count"],
            "selected_realization_count": summary["selected_realization_count"],
        }
        for operation_code, summary in sorted(summary_by_operation.items())
    ]
    return summary_rows, candidate_rows


def build_payload_rows() -> dict[str, Any]:
    carrier_adjacency, assoc_by_word, rewrite_edge_by_pair = build_context()
    _raw_windows, gate_trace_nodes, _gate_signatures, gate_metrics = build_trace(
        NO_REPAIR_GATE_WORD,
        assoc_by_word,
        rewrite_edge_by_pair,
    )
    gate_trace = tuple(int(value) for value in gate_trace_nodes)
    rewrite_edges = {
        edge_key(row["source_node_id"], row["target_node_id"])
        for row in read_int_csv(REWRITE_COMPLEX_EDGES)
    }
    node_rows = read_int_csv(REWRITE_COMPLEX_NODES)
    signatures = {
        int(row["node_id"]): int(row["signature_union_count"]) for row in node_rows
    }
    node_ids = sorted(signatures)
    summary_rows, candidate_rows = operation_rows(
        gate_trace,
        node_ids,
        rewrite_edges,
        signatures,
    )
    selected = next(row for row in candidate_rows if row["selected_realization_flag"] == 1)
    gate_profile = closure_profile(NO_REPAIR_GATE_WORD, carrier_adjacency)
    gate_native_repair = int(
        contains_undirected_edge(gate_trace, 31, 28)
        or contains_undirected_edge(gate_trace, 50, 34)
    )
    substitution_summary = next(
        row
        for row in summary_rows
        if row["operation_code"] == SUBSTITUTION_OPERATION_CODE
    )
    insertion_summary = next(
        row for row in summary_rows if row["operation_code"] == INSERTION_OPERATION_CODE
    )
    observable_values = {
        "gate_trace_node_count": len(gate_trace),
        "gate_trace_variation": int(gate_metrics["trace_signature_total_variation"]),
        "gate_delta_twice": int(gate_metrics["metric_gromov_delta_twice"]),
        "gate_closed_path_count": gate_profile["first_return_closed_path_count"],
        "gate_template_count": gate_profile["normalized_tail_template_count"],
        "gate_native_repair_flag": gate_native_repair,
        "substitution_attempt_count": substitution_summary["attempt_count"],
        "substitution_valid_path_count": substitution_summary[
            "valid_rewrite_path_count"
        ],
        "substitution_repair_candidate_count": substitution_summary[
            "repair_edge_candidate_count"
        ],
        "substitution_delta2_variation_le223_count": substitution_summary[
            "delta2_variation_le223_count"
        ],
        "insertion_attempt_count": insertion_summary["attempt_count"],
        "insertion_valid_path_count": insertion_summary["valid_rewrite_path_count"],
        "insertion_repair_candidate_count": insertion_summary[
            "repair_edge_candidate_count"
        ],
        "insertion_delta2_variation_le223_count": insertion_summary[
            "delta2_variation_le223_count"
        ],
        "insertion_variation185_count": insertion_summary["variation185_count"],
        "selected_insert_after_trace_rank": selected["insert_after_trace_rank"],
        "selected_inserted_node_id": selected["patch_node_id"],
        "selected_trace_variation": selected["trace_signature_total_variation"],
        "selected_trace_delta_twice": selected["metric_gromov_delta_twice"],
        "selected_trace_node_count": selected["trace_node_count"],
        "selected_31_28_repair_flag": selected["repair_31_28_flag"],
        "selected_50_34_repair_flag": selected["repair_50_34_flag"],
        "accepted_31_28_candidate_count": sum(
            row["repair_31_28_flag"] for row in candidate_rows
        ),
        "accepted_50_34_candidate_count": sum(
            row["repair_50_34_flag"] for row in candidate_rows
        ),
    }
    observable_rows = [
        {
            "observable_id": index,
            "observable_code": NATIVE_INSERTION_OBSERVABLE_CODES[key],
            "value_x1e12": int(value) * 10**12,
            "aux_id": -1,
        }
        for index, (key, value) in enumerate(observable_values.items())
    ]
    return {
        "gate_trace": gate_trace,
        "gate_profile": gate_profile,
        "summary_rows": summary_rows,
        "candidate_rows": candidate_rows,
        "observable_values": observable_values,
        "observable_rows": observable_rows,
    }


def build_payloads() -> dict[str, Any]:
    virtual_report = load_json(VIRTUAL_GRAFT_REPORT)
    virtual_certificate = load_json(VIRTUAL_GRAFT_CERTIFICATE)
    payload_rows = build_payload_rows()
    gate_trace = payload_rows["gate_trace"]
    gate_profile = payload_rows["gate_profile"]
    summary_rows = payload_rows["summary_rows"]
    candidate_rows = payload_rows["candidate_rows"]
    observable_values = payload_rows["observable_values"]
    observable_rows = payload_rows["observable_rows"]
    observable_rows = payload_rows["observable_rows"]

    summary_table = table_from_rows(SUMMARY_COLUMNS, summary_rows)
    candidate_table = table_from_rows(CANDIDATE_COLUMNS, candidate_rows)
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)
    selected = next(row for row in candidate_rows if row["selected_realization_flag"] == 1)
    selected_trace = tuple(
        selected[column] for column in TRACE_NODE_COLUMNS if selected[column] != -1
    )

    checks = {
        "virtual_graft_report_certified": virtual_report.get("status")
        == VIRTUAL_GRAFT_STATUS,
        "virtual_graft_certificate_certified": virtual_certificate.get("status")
        == VIRTUAL_GRAFT_STATUS,
        "gate_profile_is_preserved_target": (
            observable_values["gate_trace_variation"],
            observable_values["gate_delta_twice"],
            observable_values["gate_closed_path_count"],
            observable_values["gate_template_count"],
            observable_values["gate_native_repair_flag"],
        )
        == (185, 2, 30, 9, 0),
        "substitution_search_has_no_repair_realization": (
            observable_values["substitution_attempt_count"],
            observable_values["substitution_valid_path_count"],
            observable_values["substitution_repair_candidate_count"],
            observable_values["substitution_delta2_variation_le223_count"],
        )
        == (495, 49, 0, 0),
        "insertion_search_counts_are_expected": (
            observable_values["insertion_attempt_count"],
            observable_values["insertion_valid_path_count"],
            observable_values["insertion_repair_candidate_count"],
            observable_values["insertion_delta2_variation_le223_count"],
            observable_values["insertion_variation185_count"],
        )
        == (540, 57, 4, 3, 1),
        "selected_insertion_is_27_31_28": (
            observable_values["selected_insert_after_trace_rank"],
            observable_values["selected_inserted_node_id"],
            observable_values["selected_trace_variation"],
            observable_values["selected_trace_delta_twice"],
            observable_values["selected_trace_node_count"],
            observable_values["selected_31_28_repair_flag"],
            observable_values["selected_50_34_repair_flag"],
        )
        == (2, 31, 185, 2, 12, 1, 0)
        and selected_trace
        == (48, 42, 27, 31, 28, 34, 29, 45, 29, 28, 34, 44),
        "accepted_candidates_are_31_28_only": (
            observable_values["accepted_31_28_candidate_count"],
            observable_values["accepted_50_34_candidate_count"],
        )
        == (3, 0),
        "summary_table_shape_matches_codebook": tuple(summary_table.shape)
        == (2, len(SUMMARY_COLUMNS)),
        "candidate_table_shape_matches_codebook": tuple(candidate_table.shape)
        == (3, len(CANDIDATE_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(NATIVE_INSERTION_OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    witness = {
        "gate_word": list(NO_REPAIR_GATE_WORD),
        "gate_trace": list(gate_trace),
        "gate_profile": {
            "variation": observable_values["gate_trace_variation"],
            "delta_twice": observable_values["gate_delta_twice"],
            "closed_paths": gate_profile["first_return_closed_path_count"],
            "templates": gate_profile["normalized_tail_template_count"],
        },
        "selected_trace": list(selected_trace),
        "selected_insert_after_trace_rank": selected["insert_after_trace_rank"],
        "selected_inserted_node_id": selected["patch_node_id"],
        "substitution_summary": next(
            row
            for row in summary_rows
            if row["operation_code"] == SUBSTITUTION_OPERATION_CODE
        ),
        "insertion_summary": next(
            row for row in summary_rows if row["operation_code"] == INSERTION_OPERATION_CODE
        ),
        "summary_table_sha256": sha_array(summary_table),
        "candidate_table_sha256": sha_array(candidate_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    insertion = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_native_trace_insertion@1",
        "object": "d20",
        "comparison_rule": {
            "parent": VIRTUAL_GRAFT_REPORT.relative_to(ROOT).as_posix(),
            "gate_word": list(NO_REPAIR_GATE_WORD),
            "operations": [
                "substitute one internal trace node with any rewrite-complex node",
                "insert one rewrite-complex node into any gate trace edge",
            ],
            "acceptance_filter": [
                "all trace edges exist in the rewrite complex",
                "trace contains native 31--28 or 50--34",
                "metric_gromov_delta_twice = 2",
                "trace_signature_total_variation <= 223",
            ],
        },
        "summary": {
            "substitution_accepted_count": observable_values[
                "substitution_delta2_variation_le223_count"
            ],
            "insertion_accepted_count": observable_values[
                "insertion_delta2_variation_le223_count"
            ],
            "variation_preserving_insertion_count": observable_values[
                "insertion_variation185_count"
            ],
            "selected_trace": list(selected_trace),
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_native_trace_insertion_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_NATIVE_TRACE_INSERTION_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the no-repair gate word has 30 closed paths and 9 templates but no native repair edge",
            "single-node substitution cannot realize a native repair edge under the declared metric/variation filter",
            "single-node insertion has three accepted 31--28 realizations and no 50--34 realization",
            "the unique variation-preserving insertion routes the gate trace through 27->31->28",
            "the word-level carrier profile is unchanged because the gate word is unchanged",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_native_trace_insertion@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The native trace-insertion layer realizes the virtual 31--28 "
            "repair edge without changing the gate word. The original gate "
            "trace has variation 185, delta_twice 2, 30 closed paths, 9 "
            "templates, and no native repair edge. Exhausting 495 one-node "
            "substitutions gives 49 valid rewrite paths but zero native repair "
            "realizations. Exhausting 540 one-node insertions gives 57 valid "
            "rewrite paths, 4 native repair candidates, and 3 accepted "
            "delta2/variation<=223 candidates. Exactly one insertion preserves "
            "variation 185: insert existing rewrite node 31 after trace rank 2, "
            "turning 27->28 into 27->31->28. The carrier profile remains 30 "
            "closed paths and 9 templates because the word is unchanged."
        ),
        "stage_protocol": {
            "draft": "treat the virtual repair edge as a trace-level realization problem on the fixed gate word",
            "witness": "enumerate one-node substitutions and insertions against the rewrite-complex edge set",
            "coherence": "compare accepted traces against the gate's variation, delta, and closure/template profile",
            "closure": "certify the unique variation-preserving native 31--28 trace insertion",
            "emit": "emit operation summaries, accepted candidates, observables, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "virtual_graft_report": input_entry(
                VIRTUAL_GRAFT_REPORT,
                {
                    "status": virtual_report.get("status"),
                    "certificate_sha256": virtual_report.get("certificate_sha256"),
                },
            ),
            "virtual_graft_certificate": input_entry(VIRTUAL_GRAFT_CERTIFICATE),
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
            "signature_boundary_spine_aperture_closure_tail_native_trace_insertion": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_native_trace_insertion.json"
            ),
            "aperture_closure_tail_native_trace_insertion_summary_csv": relpath(
                OUT_DIR / "aperture_closure_tail_native_trace_insertion_summary.csv"
            ),
            "aperture_closure_tail_native_trace_insertion_candidates_csv": relpath(
                OUT_DIR
                / "aperture_closure_tail_native_trace_insertion_candidates.csv"
            ),
            "aperture_closure_tail_native_trace_insertion_observables_csv": relpath(
                OUT_DIR
                / "aperture_closure_tail_native_trace_insertion_observables.csv"
            ),
            "signature_boundary_spine_aperture_closure_tail_native_trace_insertion_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_native_trace_insertion_tables.npz"
            ),
            "signature_boundary_spine_aperture_closure_tail_native_trace_insertion_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_native_trace_insertion_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the fixed no-repair gate word and its carrier closure/template profile",
                "all one-node substitutions of internal gate trace nodes",
                "all one-node insertions into gate trace edges",
                "native 31--28 trace insertion through existing rewrite-complex edges",
            ],
            "does_not_certify_because_not_required": [
                "a word-level sliding-window realization of the inserted trace node",
                "multi-node trace insertions",
                "native 50--34 realization beyond the exhausted one-node insertion space",
                "compiler lowering behavior",
            ],
        },
        "next_highest_yield_item": (
            "Lift the native trace insertion back to symbols: search for the "
            "minimal word augmentation or associativity-window refinement that "
            "creates canonical node 31 between the gate's 27 and 28 windows "
            "while preserving the 30-closure, 9-template carrier profile."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_native_trace_insertion_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified virtual-graft artifacts",
            "evaluate the fixed gate trace and carrier profile",
            "exhaust one-node trace substitutions and insertions",
            "check selected 27->31->28 insertion and operation counts",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_closure_tail_native_trace_insertion": insertion,
        "aperture_closure_tail_native_trace_insertion_summary_csv": csv_text(
            SUMMARY_COLUMNS,
            summary_rows,
        ),
        "aperture_closure_tail_native_trace_insertion_candidates_csv": csv_text(
            CANDIDATE_COLUMNS,
            candidate_rows,
        ),
        "aperture_closure_tail_native_trace_insertion_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "summary_table": summary_table,
        "candidate_table": candidate_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_closure_tail_native_trace_insertion_certificate": certificate,
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
        / "signature_boundary_spine_aperture_closure_tail_native_trace_insertion.json",
        payloads[
            "signature_boundary_spine_aperture_closure_tail_native_trace_insertion"
        ],
    )
    (
        OUT_DIR / "aperture_closure_tail_native_trace_insertion_summary.csv"
    ).write_text(
        payloads["aperture_closure_tail_native_trace_insertion_summary_csv"],
        encoding="utf-8",
    )
    (
        OUT_DIR / "aperture_closure_tail_native_trace_insertion_candidates.csv"
    ).write_text(
        payloads["aperture_closure_tail_native_trace_insertion_candidates_csv"],
        encoding="utf-8",
    )
    (
        OUT_DIR / "aperture_closure_tail_native_trace_insertion_observables.csv"
    ).write_text(
        payloads["aperture_closure_tail_native_trace_insertion_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_native_trace_insertion_tables.npz",
        summary_table=payloads["summary_table"],
        candidate_table=payloads["candidate_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_native_trace_insertion_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_closure_tail_native_trace_insertion_certificate"
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
