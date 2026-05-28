from __future__ import annotations

import json
from collections import deque
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_endpoint_split import (
        input_entry,
        relpath,
        self_hash,
        sha_array,
        table_from_rows,
        write_json,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_rewrite_node_lift import (
        APERTURE_NODE_ID,
        BASELINE_OUTLIER_ID,
        BRIDGE_BY_WITNESS,
        GEODESIC_NODE_IDS,
        OUT_DIR as REWRITE_LIFT_DIR,
        PREFIX_DRIVER_NODES,
        RANK104_OUTLIER_ID,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_NODES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        SHARED_REWRITE_TAIL,
        STATUS as REWRITE_LIFT_STATUS,
        STRICT_INTERMEDIATE_NODE_ID,
        csv_text,
        load_json,
        read_int_csv,
        signature_map,
        variation,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_endpoint_split import (
        input_entry,
        relpath,
        self_hash,
        sha_array,
        table_from_rows,
        write_json,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_rewrite_node_lift import (
        APERTURE_NODE_ID,
        BASELINE_OUTLIER_ID,
        BRIDGE_BY_WITNESS,
        GEODESIC_NODE_IDS,
        OUT_DIR as REWRITE_LIFT_DIR,
        PREFIX_DRIVER_NODES,
        RANK104_OUTLIER_ID,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_NODES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        SHARED_REWRITE_TAIL,
        STATUS as REWRITE_LIFT_STATUS,
        STRICT_INTERMEDIATE_NODE_ID,
        csv_text,
        load_json,
        read_int_csv,
        signature_map,
        variation,
    )
    from derive_c985_typed_simple_object_registry import INDEX_PATH
    from paths import D20_INVARIANTS, ROOT


THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_prefix_chord_search"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_PREFIX_CHORD_SEARCH_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

REWRITE_LIFT_REPORT = REWRITE_LIFT_DIR / "report.json"
REWRITE_LIFT_JSON = (
    REWRITE_LIFT_DIR
    / "signature_boundary_spine_aperture_closure_tail_rewrite_node_lift.json"
)
REWRITE_LIFT_CANDIDATES = (
    REWRITE_LIFT_DIR / "aperture_closure_tail_rewrite_delta_witnesses.csv"
)
REWRITE_LIFT_TABLES = (
    REWRITE_LIFT_DIR
    / "signature_boundary_spine_aperture_closure_tail_rewrite_node_lift_tables.npz"
)
REWRITE_LIFT_CERTIFICATE = (
    REWRITE_LIFT_DIR
    / "signature_boundary_spine_aperture_closure_tail_rewrite_node_lift_certificate.json"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_prefix_chord_search.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_prefix_chord_search.py"
)

RANK104_TRACE = (48, 42, 27, 31, 50, 54, 45, 29, 28, 34, 44)
BASELINE_DELTA_TWICE = 2
RANK104_PRE_CHORD_DELTA_TWICE = 4
RANK104_CLOSURE_PATH_COUNT = 24
RANK104_BRIDGE_VARIATION = 22
BRIDGE_BASELINE_SHORTCUT_CHORDS = frozenset(
    {frozenset((31, 28)), frozenset((50, 34))}
)

CHORD_COLUMNS = [
    "candidate_id",
    "source_node_id",
    "target_node_id",
    "undirected_left_node_id",
    "undirected_right_node_id",
    "source_signature_count",
    "target_signature_count",
    "signature_variation",
    "existing_rewrite_edge_flag",
    "trace_edge_flag",
    "ambient_geodesic_edge_flag",
    "post_chord_delta_twice",
    "best_delta_witness_count",
    "prefix_tail_best_delta_witness_count",
    "delta_penalty_removed_flag",
    "closure_path_count_retained",
    "bridge_variation_retained",
    "prefix_to_baseline_shortcut_flag",
]

OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "pre_chord_delta_twice": 0,
    "target_delta_twice": 1,
    "single_existing_chord_candidate_count": 2,
    "delta_repair_candidate_count": 3,
    "prefix_to_baseline_repair_candidate_count": 4,
    "closure_path_count_retained": 5,
    "bridge_variation_retained": 6,
    "repair_signature_variation_min": 7,
    "prefix_to_baseline_repair_signature_variation_min": 8,
    "pre_chord_prefix_tail_best_delta_witness_count": 9,
}


def undirected_key(left: int, right: int) -> tuple[int, int]:
    return tuple(sorted((int(left), int(right))))


def unique_nodes(trace: tuple[int, ...]) -> list[int]:
    nodes: list[int] = []
    for node in [*GEODESIC_NODE_IDS, *trace]:
        if node not in nodes:
            nodes.append(int(node))
    return nodes


def graph_delta_witnesses(
    trace_nodes: tuple[int, ...],
    extra_edges: tuple[tuple[int, int], ...] = (),
) -> tuple[int, list[dict[str, Any]]]:
    nodes = unique_nodes(trace_nodes)
    adjacency = {node: set() for node in nodes}
    for source, target in zip(trace_nodes, trace_nodes[1:]):
        adjacency[int(source)].add(int(target))
        adjacency[int(target)].add(int(source))
    adjacency[STRICT_INTERMEDIATE_NODE_ID].add(APERTURE_NODE_ID)
    adjacency[APERTURE_NODE_ID].add(STRICT_INTERMEDIATE_NODE_ID)
    for source, target in extra_edges:
        adjacency[int(source)].add(int(target))
        adjacency[int(target)].add(int(source))

    distances: dict[tuple[int, int], int] = {}
    for source in nodes:
        queue: deque[tuple[int, int]] = deque([(source, 0)])
        seen = {source}
        while queue:
            node, distance = queue.popleft()
            distances[(source, node)] = distance
            for neighbor in adjacency[node]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append((neighbor, distance + 1))

    best_delta = -1
    best_rows: list[dict[str, Any]] = []
    for quad in combinations(nodes, 4):
        a, b, c, d = quad
        sums = sorted(
            [
                distances[(a, b)] + distances[(c, d)],
                distances[(a, c)] + distances[(b, d)],
                distances[(a, d)] + distances[(b, c)],
            ]
        )
        delta = sums[2] - sums[1]
        row = {
            "quad": tuple(int(node) for node in quad),
            "pair_sums": tuple(int(value) for value in sums),
            "delta_twice": int(delta),
        }
        if delta > best_delta:
            best_delta = delta
            best_rows = [row]
        elif delta == best_delta:
            best_rows.append(row)
    return int(best_delta), best_rows


def prefix_tail_best_count(rows: list[dict[str, Any]]) -> int:
    return sum(
        any(node in row["quad"] for node in PREFIX_DRIVER_NODES)
        and any(node in row["quad"] for node in SHARED_REWRITE_TAIL)
        for row in rows
    )


def build_payloads() -> dict[str, Any]:
    rewrite_lift_report = load_json(REWRITE_LIFT_REPORT)
    rewrite_lift_json = load_json(REWRITE_LIFT_JSON)
    rewrite_lift_certificate = load_json(REWRITE_LIFT_CERTIFICATE)
    rewrite_report = load_json(REWRITE_COMPLEX_REPORT)
    rewrite_certificate = load_json(REWRITE_COMPLEX_CERTIFICATE)
    rewrite_nodes = read_int_csv(REWRITE_COMPLEX_NODES)
    rewrite_edges = read_int_csv(REWRITE_COMPLEX_EDGES)
    signatures = signature_map(rewrite_nodes)

    rank104_witness = rewrite_lift_report["witness"]["rank104_outlier"]
    rank104_trace = tuple(int(node) for node in rank104_witness["trace"])
    if rank104_trace != RANK104_TRACE:
        raise AssertionError("rank104 trace mismatch")

    base_edges = {
        undirected_key(source, target)
        for source, target in zip(rank104_trace, rank104_trace[1:])
    }
    base_edges.add(undirected_key(STRICT_INTERMEDIATE_NODE_ID, APERTURE_NODE_ID))
    node_set = set(unique_nodes(rank104_trace))

    pre_delta, pre_delta_rows = graph_delta_witnesses(rank104_trace)
    if pre_delta != RANK104_PRE_CHORD_DELTA_TWICE:
        raise AssertionError("rank104 pre-chord delta mismatch")

    seen_chords: set[tuple[int, int]] = set()
    candidate_rows: list[dict[str, int]] = []
    for edge in rewrite_edges:
        source = int(edge["source_node_id"])
        target = int(edge["target_node_id"])
        if source not in node_set or target not in node_set:
            continue
        chord_key = undirected_key(source, target)
        if chord_key in base_edges or chord_key in seen_chords:
            continue
        seen_chords.add(chord_key)
        post_delta, post_rows = graph_delta_witnesses(
            rank104_trace,
            ((source, target),),
        )
        candidate_rows.append(
            {
                "candidate_id": -1,
                "source_node_id": source,
                "target_node_id": target,
                "undirected_left_node_id": chord_key[0],
                "undirected_right_node_id": chord_key[1],
                "source_signature_count": signatures[source],
                "target_signature_count": signatures[target],
                "signature_variation": abs(signatures[target] - signatures[source]),
                "existing_rewrite_edge_flag": 1,
                "trace_edge_flag": 0,
                "ambient_geodesic_edge_flag": 0,
                "post_chord_delta_twice": post_delta,
                "best_delta_witness_count": len(post_rows),
                "prefix_tail_best_delta_witness_count": prefix_tail_best_count(
                    post_rows
                ),
                "delta_penalty_removed_flag": int(
                    post_delta == BASELINE_DELTA_TWICE
                ),
                "closure_path_count_retained": RANK104_CLOSURE_PATH_COUNT,
                "bridge_variation_retained": RANK104_BRIDGE_VARIATION,
                "prefix_to_baseline_shortcut_flag": int(
                    frozenset(chord_key) in BRIDGE_BASELINE_SHORTCUT_CHORDS
                    and post_delta == BASELINE_DELTA_TWICE
                ),
            }
        )
    candidate_rows.sort(
        key=lambda row: (
            row["post_chord_delta_twice"],
            row["best_delta_witness_count"],
            row["undirected_left_node_id"],
            row["undirected_right_node_id"],
        )
    )
    for index, row in enumerate(candidate_rows):
        row["candidate_id"] = index

    repair_rows = [
        row
        for row in candidate_rows
        if row["delta_penalty_removed_flag"] == 1
    ]
    prefix_shortcut_rows = [
        row
        for row in repair_rows
        if row["prefix_to_baseline_shortcut_flag"] == 1
    ]
    repair_variation_min = min(row["signature_variation"] for row in repair_rows)
    prefix_repair_variation_min = min(
        row["signature_variation"] for row in prefix_shortcut_rows
    )
    observable_values = {
        "pre_chord_delta_twice": pre_delta,
        "target_delta_twice": BASELINE_DELTA_TWICE,
        "single_existing_chord_candidate_count": len(candidate_rows),
        "delta_repair_candidate_count": len(repair_rows),
        "prefix_to_baseline_repair_candidate_count": len(prefix_shortcut_rows),
        "closure_path_count_retained": RANK104_CLOSURE_PATH_COUNT,
        "bridge_variation_retained": RANK104_BRIDGE_VARIATION,
        "repair_signature_variation_min": repair_variation_min,
        "prefix_to_baseline_repair_signature_variation_min": (
            prefix_repair_variation_min
        ),
        "pre_chord_prefix_tail_best_delta_witness_count": prefix_tail_best_count(
            pre_delta_rows
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

    chord_table = table_from_rows(CHORD_COLUMNS, candidate_rows)
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    repair_chords = [
        [row["undirected_left_node_id"], row["undirected_right_node_id"]]
        for row in repair_rows
    ]
    prefix_shortcut_chords = [
        [row["undirected_left_node_id"], row["undirected_right_node_id"]]
        for row in prefix_shortcut_rows
    ]
    checks = {
        "rewrite_lift_report_certified": rewrite_lift_report.get("status")
        == REWRITE_LIFT_STATUS,
        "rewrite_lift_certificate_certified": rewrite_lift_certificate.get("status")
        == REWRITE_LIFT_STATUS,
        "rewrite_lift_schema_available": rewrite_lift_json.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_closure_tail_rewrite_node_lift@1",
        "rewrite_complex_report_certified": rewrite_report.get("status")
        == "C985_D20_REWRITE_COMPLEX_HYPERBOLICITY_CERTIFIED",
        "rewrite_complex_certificate_certified": rewrite_certificate.get("status")
        == "C985_D20_REWRITE_COMPLEX_HYPERBOLICITY_CERTIFIED",
        "rank104_trace_is_unchanged": rank104_trace == RANK104_TRACE,
        "pre_chord_delta_penalty_reproduced": pre_delta
        == RANK104_PRE_CHORD_DELTA_TWICE
        and prefix_tail_best_count(pre_delta_rows) == 18,
        "single_existing_chord_search_space_has_16_candidates": len(candidate_rows)
        == 16,
        "five_existing_single_chords_remove_delta_penalty": repair_chords
        == [[42, 45], [27, 29], [44, 54], [28, 31], [34, 50]],
        "two_bridge_to_baseline_shortcuts_are_repair_chords": prefix_shortcut_chords
        == [[28, 31], [34, 50]],
        "rank104_closure_count_and_bridge_variation_are_retained": all(
            row["closure_path_count_retained"] == RANK104_CLOSURE_PATH_COUNT
            and row["bridge_variation_retained"] == RANK104_BRIDGE_VARIATION
            for row in repair_rows
        ),
        "best_bridge_to_baseline_shortcut_has_signature_variation_18": (
            prefix_repair_variation_min == 18
        ),
        "chord_table_shape_matches_codebook": tuple(chord_table.shape)
        == (16, len(CHORD_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    witness = {
        "rank104_outlier_id": RANK104_OUTLIER_ID,
        "rank104_trace": list(rank104_trace),
        "rank104_bridge": list(BRIDGE_BY_WITNESS[RANK104_OUTLIER_ID]),
        "rank104_bridge_variation_retained": RANK104_BRIDGE_VARIATION,
        "rank104_closure_path_count_retained": RANK104_CLOSURE_PATH_COUNT,
        "pre_chord_delta_twice": pre_delta,
        "pre_chord_best_delta_witness_count": len(pre_delta_rows),
        "pre_chord_prefix_tail_best_delta_witness_count": prefix_tail_best_count(
            pre_delta_rows
        ),
        "repair_chords": repair_chords,
        "prefix_to_baseline_repair_chords": prefix_shortcut_chords,
        "chord_table_sha256": sha_array(chord_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    chord_search = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_prefix_chord_search@1",
        "object": "d20",
        "comparison_rule": {
            "rank104_outlier": RANK104_OUTLIER_ID,
            "baseline_delta_twice": BASELINE_DELTA_TWICE,
            "rank104_trace": list(rank104_trace),
            "shared_rewrite_tail": list(SHARED_REWRITE_TAIL),
        },
        "summary": {
            "single_existing_chord_candidate_count": len(candidate_rows),
            "delta_repair_candidate_count": len(repair_rows),
            "prefix_to_baseline_repair_candidate_count": len(prefix_shortcut_rows),
            "rank104_closure_path_count_retained": RANK104_CLOSURE_PATH_COUNT,
            "rank104_bridge_variation_retained": RANK104_BRIDGE_VARIATION,
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_prefix_chord_search_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_PREFIX_CHORD_SEARCH_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the rank104 prefix-tail delta penalty is removable by a single omitted rewrite-complex chord in the local trace metric",
            "exactly five existing single chords lower rank104 delta_twice from 4 to the baseline value 2",
            "two of those five are bridge-to-baseline shortcut chords: 31--28 and 50--34",
            "the search does not alter the rank104 trace, low-variation bridge, or 24 first-return closure paths",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_prefix_chord_search@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "Searching the full rewrite complex restricted to the rank104 "
            "closure-rich trace finds 16 omitted single chords among the local "
            "trace nodes. Five already-existing rewrite-complex chords lower "
            "the local metric delta_twice from 4 to the baseline value 2 while "
            "leaving the rank104 trace, 22-variation bridge, and 24 closed "
            "carrier paths unchanged. The two repair chords that splice the "
            "rank104 bridge back toward the baseline shortcut are 31--28 and "
            "50--34. This certifies the missing metric chord, not yet a "
            "carrier-word replacement."
        ),
        "stage_protocol": {
            "draft": "start from the certified rewrite-node lift and keep the rank104 closure-rich trace fixed",
            "witness": "enumerate existing rewrite-complex edges among the trace nodes that are absent from the trace metric",
            "coherence": "add each candidate as one undirected chord and recompute exact four-point delta",
            "closure": "certify the single-chord repairs that remove the prefix-tail delta penalty without changing closure count",
            "emit": "emit chord candidates, observables, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "rewrite_lift_report": input_entry(
                REWRITE_LIFT_REPORT,
                {
                    "status": rewrite_lift_report.get("status"),
                    "certificate_sha256": rewrite_lift_report.get(
                        "certificate_sha256"
                    ),
                },
            ),
            "rewrite_lift_json": input_entry(REWRITE_LIFT_JSON),
            "rewrite_lift_delta_witnesses": input_entry(REWRITE_LIFT_CANDIDATES),
            "rewrite_lift_tables": input_entry(REWRITE_LIFT_TABLES),
            "rewrite_lift_certificate": input_entry(REWRITE_LIFT_CERTIFICATE),
            "rewrite_complex_report": input_entry(
                REWRITE_COMPLEX_REPORT,
                {
                    "status": rewrite_report.get("status"),
                    "certificate_sha256": rewrite_report.get("certificate_sha256"),
                },
            ),
            "rewrite_complex_nodes": input_entry(REWRITE_COMPLEX_NODES),
            "rewrite_complex_edges": input_entry(REWRITE_COMPLEX_EDGES),
            "rewrite_complex_tables": input_entry(REWRITE_COMPLEX_TABLES),
            "rewrite_complex_certificate": input_entry(REWRITE_COMPLEX_CERTIFICATE),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_aperture_closure_tail_prefix_chord_search": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_prefix_chord_search.json"
            ),
            "aperture_closure_tail_prefix_chord_candidates_csv": relpath(
                OUT_DIR / "aperture_closure_tail_prefix_chord_candidates.csv"
            ),
            "aperture_closure_tail_prefix_chord_observables_csv": relpath(
                OUT_DIR / "aperture_closure_tail_prefix_chord_observables.csv"
            ),
            "signature_boundary_spine_aperture_closure_tail_prefix_chord_search_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_prefix_chord_search_tables.npz"
            ),
            "signature_boundary_spine_aperture_closure_tail_prefix_chord_search_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_prefix_chord_search_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "single-chord metric repairs inside the existing rewrite complex",
                "which omitted chords lower rank104 delta_twice from 4 to 2",
                "the two bridge-to-baseline shortcut repair chords 31--28 and 50--34",
                "retention of the rank104 trace, 22-variation bridge, and 24 closure paths under metric augmentation",
            ],
            "does_not_certify_because_not_required": [
                "a new carrier-word witness realizing the chord as a selected-symbol splice",
                "new first-return path enumeration after changing the word",
                "edit costs above one inserted metric chord",
                "categorical pivotal, spherical, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Try to realize one of the two bridge-to-baseline repair chords "
            "31--28 or 50--34 as an actual carrier-preserving word splice, "
            "then re-enumerate first-return closure paths to see whether the "
            "24-path rank104 multiplicity survives with delta_twice 2."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_prefix_chord_search_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified rewrite-node lift and rewrite-complex artifacts",
            "recompute rank104 local trace metric delta",
            "enumerate omitted existing rewrite-complex chords on the trace nodes",
            "verify the five single-chord delta repairs and two bridge-to-baseline repairs",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_closure_tail_prefix_chord_search": chord_search,
        "aperture_closure_tail_prefix_chord_candidates_csv": csv_text(
            CHORD_COLUMNS,
            candidate_rows,
        ),
        "aperture_closure_tail_prefix_chord_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "chord_table": chord_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_closure_tail_prefix_chord_search_certificate": certificate,
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
        / "signature_boundary_spine_aperture_closure_tail_prefix_chord_search.json",
        payloads["signature_boundary_spine_aperture_closure_tail_prefix_chord_search"],
    )
    (OUT_DIR / "aperture_closure_tail_prefix_chord_candidates.csv").write_text(
        payloads["aperture_closure_tail_prefix_chord_candidates_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_prefix_chord_observables.csv").write_text(
        payloads["aperture_closure_tail_prefix_chord_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_prefix_chord_search_tables.npz",
        chord_table=payloads["chord_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_prefix_chord_search_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_closure_tail_prefix_chord_search_certificate"
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
