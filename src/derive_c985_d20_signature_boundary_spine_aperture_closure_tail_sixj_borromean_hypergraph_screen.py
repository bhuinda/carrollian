from __future__ import annotations

import json
from itertools import combinations
from typing import Any

import numpy as np

try:
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen as nonlocal_screen
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen as nonlocal_screen
    from derive_c985_typed_simple_object_registry import INDEX_PATH
    from paths import D20_INVARIANTS, ROOT


pair = nonlocal_screen.pair

THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_borromean_hypergraph_screen"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_SIXJ_BORROMEAN_HYPERGRAPH_SCREEN_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

NONLOCAL_SCREEN_REPORT = nonlocal_screen.OUT_DIR / "report.json"
NONLOCAL_SCREEN_CERTIFICATE = (
    nonlocal_screen.OUT_DIR
    / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen_certificate.json"
)
NONLOCAL_SCREEN_TABLES = (
    nonlocal_screen.OUT_DIR
    / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen_tables.npz"
)
NONLOCAL_SCREEN_JSON = (
    nonlocal_screen.OUT_DIR
    / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen.json"
)
ASSOCIATOR_REPORT = nonlocal_screen.ASSOCIATOR_REPORT
PENTAGON_REPORT = nonlocal_screen.PENTAGON_REPORT

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_borromean_hypergraph_screen.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_borromean_hypergraph_screen.py"
)

EXPECTED_SELECTED_CODES = [1452, 4521, 2114, 1145, 5214, 5521]

HYPEREDGE_COLUMNS = [
    "hyperedge_id",
    "block_code_a",
    "block_code_b",
    "block_code_c",
    "pairwise_shadow_inert_flag",
    "state_count",
    "new_state_count",
    "edge_count",
    "new_edge_count",
    "cut_edge_count",
    "old_cut_edge_still_cut_count",
    "old_cut_edge_same_side_count",
    "promoted_cut_edge_count",
    "promoted_only_cut_edge_count",
    "lambda_2_x1e12",
    "cut_conductance_x1e12",
    "conductance_reduction_x1e12",
    "support_changed_flag",
    "borromean_opening_flag",
    "selected_best_flag",
]
OBSERVABLE_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBSERVABLE_CODES = {
    "closed_metric_word_count": 0,
    "base_state_count": 1,
    "base_edge_count": 2,
    "base_cut_edge_count": 3,
    "base_cut_conductance_x1e12": 4,
    "selected_f_address_count": 5,
    "ordinary_repair_edge_count": 6,
    "ordinary_singleton_shadow_count": 7,
    "ordinary_pair_shadow_count": 8,
    "ordinary_shadow_support_changing_count": 9,
    "hyperedge_count": 10,
    "pairwise_inert_hyperedge_count": 11,
    "borromean_opening_hyperedge_count": 12,
    "support_changing_hyperedge_count": 13,
    "conductance_improving_hyperedge_count": 14,
    "best_block_code_a": 15,
    "best_block_code_b": 16,
    "best_block_code_c": 17,
    "best_state_count": 18,
    "best_edge_count": 19,
    "best_cut_edge_count": 20,
    "best_old_cut_edge_still_cut_count": 21,
    "best_lambda_2_x1e12": 22,
    "best_cut_conductance_x1e12": 23,
    "best_conductance_reduction_x1e12": 24,
    "max_cut_edge_count": 25,
    "min_old_cut_edge_still_cut_count": 26,
}


def table_from_rows(columns: list[str], rows: list[dict[str, int]]) -> np.ndarray:
    return np.asarray(
        [[int(row[column]) for column in columns] for row in rows],
        dtype=np.int64,
    )


def table_rows(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def load_json(path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} is not a JSON object")
    return payload


def selected_blocks_from_screen(screen: dict[str, Any]) -> list[tuple[int, int, int, int]]:
    codes = screen["search_scope"]["selected_nonlocal_block_codes"]
    return [nonlocal_screen.block_tuple_from_code(code) for code in codes]


def shadow_map(
    shadow_rows: list[dict[str, int]],
) -> dict[frozenset[int], dict[str, int]]:
    mapped: dict[frozenset[int], dict[str, int]] = {}
    for row in shadow_rows:
        codes = [row["block_code_a"]]
        if row["block_code_b"] != -1:
            codes.append(row["block_code_b"])
        mapped[frozenset(codes)] = row
    return mapped


def evaluate_hyperedge(
    hyperedge_id: int,
    blocks: tuple[tuple[int, int, int, int], ...],
    records: dict[tuple[int, ...], dict[str, Any]],
    geometry: dict[str, Any],
    base_conductance: int,
    shadows: dict[frozenset[int], dict[str, int]],
) -> dict[str, int]:
    block_codes = [pair.block_code(block) for block in blocks]
    projection_keys = [
        frozenset((code,))
        for code in block_codes
    ] + [
        frozenset(pair_codes)
        for pair_codes in combinations(block_codes, 2)
    ]
    pairwise_shadow_inert = all(
        shadows[key]["support_changed_flag"] == 0
        and shadows[key]["old_cut_edge_still_cut_count"] == 6
        and shadows[key]["old_cut_edge_same_side_count"] == 0
        for key in projection_keys
    )

    rows_by_word = pair.rows_for_blocks(records, set(pair.BASE_BLOCKS) | set(blocks))
    graph = pair.parent.build_graph(rows_by_word)
    automaton = pair.parent.build_automaton_rows(graph, geometry)
    spectral = automaton["spectral_rows"][0]
    support_changed = int(
        spectral["old_cut_edge_still_cut_count"] < 6
        or spectral["old_cut_edge_same_side_count"] > 0
    )
    return {
        "hyperedge_id": hyperedge_id,
        "block_code_a": block_codes[0],
        "block_code_b": block_codes[1],
        "block_code_c": block_codes[2],
        "pairwise_shadow_inert_flag": int(pairwise_shadow_inert),
        "state_count": len(automaton["state_rows"]),
        "new_state_count": len(automaton["state_rows"]) - geometry["state_count"],
        "edge_count": len(automaton["edge_rows"]),
        "new_edge_count": len(automaton["edge_rows"]) - geometry["edge_count"],
        "cut_edge_count": spectral["cut_edge_count"],
        "old_cut_edge_still_cut_count": spectral["old_cut_edge_still_cut_count"],
        "old_cut_edge_same_side_count": spectral["old_cut_edge_same_side_count"],
        "promoted_cut_edge_count": spectral["promoted_cut_edge_count"],
        "promoted_only_cut_edge_count": spectral["promoted_only_cut_edge_count"],
        "lambda_2_x1e12": spectral["lambda_2_x1e12"],
        "cut_conductance_x1e12": spectral["cut_conductance_x1e12"],
        "conductance_reduction_x1e12": base_conductance
        - spectral["cut_conductance_x1e12"],
        "support_changed_flag": support_changed,
        "borromean_opening_flag": int(pairwise_shadow_inert and support_changed),
        "selected_best_flag": 0,
    }


def build_payload_rows() -> dict[str, Any]:
    nonlocal_report = load_json(NONLOCAL_SCREEN_REPORT)
    nonlocal_certificate = load_json(NONLOCAL_SCREEN_CERTIFICATE)
    nonlocal_screen_json = load_json(NONLOCAL_SCREEN_JSON)
    associator_report = load_json(ASSOCIATOR_REPORT)
    pentagon_report = load_json(PENTAGON_REPORT)

    nonlocal_tables = np.load(NONLOCAL_SCREEN_TABLES, allow_pickle=False)
    shadow_rows = table_rows(
        np.asarray(nonlocal_tables["intervention_table"], dtype=np.int64),
        nonlocal_screen.INTERVENTION_COLUMNS,
    )
    shadows = shadow_map(shadow_rows)

    geometry = pair.load_second_window_geometry()
    records = pair.precompute_closed_metric_records()
    base_spectral = pair.parent.table_rows(
        np.asarray(
            np.load(pair.SECOND_WINDOW_PROMOTION_TABLES, allow_pickle=False)[
                "spectral_cut_table"
            ],
            dtype=np.int64,
        ),
        pair.parent.SPECTRAL_CUT_COLUMNS,
    )[0]

    selected_blocks = selected_blocks_from_screen(nonlocal_screen_json)
    hyperedges = list(combinations(selected_blocks, 3))
    hyperedge_rows = [
        evaluate_hyperedge(
            hyperedge_id,
            blocks,
            records,
            geometry,
            base_spectral["cut_conductance_x1e12"],
            shadows,
        )
        for hyperedge_id, blocks in enumerate(hyperedges)
    ]
    best = min(
        hyperedge_rows,
        key=lambda row: (
            -row["borromean_opening_flag"],
            row["cut_conductance_x1e12"],
            -row["lambda_2_x1e12"],
            row["block_code_a"],
            row["block_code_b"],
            row["block_code_c"],
        ),
    )
    best["selected_best_flag"] = 1

    singleton_shadow_count = sum(row["intervention_size"] == 1 for row in shadow_rows)
    pair_shadow_count = sum(row["intervention_size"] == 2 for row in shadow_rows)
    observable_values = {
        "closed_metric_word_count": len(records),
        "base_state_count": geometry["state_count"],
        "base_edge_count": geometry["edge_count"],
        "base_cut_edge_count": base_spectral["cut_edge_count"],
        "base_cut_conductance_x1e12": base_spectral["cut_conductance_x1e12"],
        "selected_f_address_count": len(selected_blocks),
        "ordinary_repair_edge_count": len(shadow_rows),
        "ordinary_singleton_shadow_count": singleton_shadow_count,
        "ordinary_pair_shadow_count": pair_shadow_count,
        "ordinary_shadow_support_changing_count": sum(
            row["support_changed_flag"] for row in shadow_rows
        ),
        "hyperedge_count": len(hyperedge_rows),
        "pairwise_inert_hyperedge_count": sum(
            row["pairwise_shadow_inert_flag"] for row in hyperedge_rows
        ),
        "borromean_opening_hyperedge_count": sum(
            row["borromean_opening_flag"] for row in hyperedge_rows
        ),
        "support_changing_hyperedge_count": sum(
            row["support_changed_flag"] for row in hyperedge_rows
        ),
        "conductance_improving_hyperedge_count": sum(
            row["cut_conductance_x1e12"] < base_spectral["cut_conductance_x1e12"]
            for row in hyperedge_rows
        ),
        "best_block_code_a": best["block_code_a"],
        "best_block_code_b": best["block_code_b"],
        "best_block_code_c": best["block_code_c"],
        "best_state_count": best["state_count"],
        "best_edge_count": best["edge_count"],
        "best_cut_edge_count": best["cut_edge_count"],
        "best_old_cut_edge_still_cut_count": best["old_cut_edge_still_cut_count"],
        "best_lambda_2_x1e12": best["lambda_2_x1e12"],
        "best_cut_conductance_x1e12": best["cut_conductance_x1e12"],
        "best_conductance_reduction_x1e12": best[
            "conductance_reduction_x1e12"
        ],
        "max_cut_edge_count": max(row["cut_edge_count"] for row in hyperedge_rows),
        "min_old_cut_edge_still_cut_count": min(
            row["old_cut_edge_still_cut_count"] for row in hyperedge_rows
        ),
    }
    observable_rows = [
        {
            "observable_id": observable_id,
            "observable_code": code,
            "value": int(observable_values[key]),
            "scale_code": 0,
        }
        for observable_id, (key, code) in enumerate(OBSERVABLE_CODES.items())
    ]

    return {
        "nonlocal_report": nonlocal_report,
        "nonlocal_certificate": nonlocal_certificate,
        "nonlocal_screen_json": nonlocal_screen_json,
        "associator_report": associator_report,
        "pentagon_report": pentagon_report,
        "selected_blocks": selected_blocks,
        "shadow_rows": shadow_rows,
        "hyperedge_rows": hyperedge_rows,
        "observable_rows": observable_rows,
        "observable_values": observable_values,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_payload_rows()
    hyperedge_table = table_from_rows(HYPEREDGE_COLUMNS, rows["hyperedge_rows"])
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, rows["observable_rows"])
    observable_values = rows["observable_values"]
    selected_codes = [pair.block_code(block) for block in rows["selected_blocks"]]
    best = next(row for row in rows["hyperedge_rows"] if row["selected_best_flag"])

    checks = {
        "nonlocal_screen_report_certified": rows["nonlocal_report"].get("status")
        == nonlocal_screen.STATUS,
        "nonlocal_screen_certificate_certified": rows["nonlocal_certificate"].get(
            "status"
        )
        == nonlocal_screen.STATUS,
        "associator_oracle_certified": rows["associator_report"].get("status")
        == "C985_ASSOCIATOR_REBRACKETING_ORACLE_CERTIFIED",
        "pentagon_normal_form_certified": rows["pentagon_report"].get("status")
        == "C985_PENTAGON_CHAIN_NORMAL_FORM_CERTIFIED",
        "hypergraph_scope_is_top_six_nonlocal_f_addresses": (
            selected_codes,
            observable_values["selected_f_address_count"],
            observable_values["ordinary_repair_edge_count"],
            observable_values["hyperedge_count"],
        )
        == (EXPECTED_SELECTED_CODES, 6, 21, 20),
        "all_singleton_and_pair_shadows_are_inert": observable_values[
            "ordinary_shadow_support_changing_count"
        ]
        == 0,
        "all_hyperedges_have_pairwise_inert_shadows": observable_values[
            "pairwise_inert_hyperedge_count"
        ]
        == observable_values["hyperedge_count"],
        "no_top_six_borromean_hyperedge_opens_aperture": (
            observable_values["borromean_opening_hyperedge_count"],
            observable_values["support_changing_hyperedge_count"],
            observable_values["min_old_cut_edge_still_cut_count"],
        )
        == (0, 0, 6),
        "top_six_hyperedges_do_not_improve_conductance": observable_values[
            "conductance_improving_hyperedge_count"
        ]
        == 0,
        "best_hyperedge_is_2114_5214_5521_and_keeps_old_cut": (
            observable_values["best_block_code_a"],
            observable_values["best_block_code_b"],
            observable_values["best_block_code_c"],
            observable_values["best_state_count"],
            observable_values["best_edge_count"],
            observable_values["best_cut_edge_count"],
            observable_values["best_old_cut_edge_still_cut_count"],
            observable_values["best_lambda_2_x1e12"],
            observable_values["best_cut_conductance_x1e12"],
            observable_values["best_conductance_reduction_x1e12"],
        )
        == (2114, 5214, 5521, 980, 3_122, 11, 6, 2_480_783_000, 4_670_913_000, -341_909_000),
        "table_shapes_match_codebooks": (
            tuple(hyperedge_table.shape),
            tuple(observable_table.shape),
        )
        == (
            (20, len(HYPEREDGE_COLUMNS)),
            (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
        ),
    }

    witness = {
        "selected_nonlocal_f_address_codes": selected_codes,
        "ordinary_repair_edge_count": observable_values["ordinary_repair_edge_count"],
        "hyperedge_count": observable_values["hyperedge_count"],
        "pairwise_inert_hyperedge_count": observable_values[
            "pairwise_inert_hyperedge_count"
        ],
        "borromean_opening_hyperedge_count": observable_values[
            "borromean_opening_hyperedge_count"
        ],
        "support_changing_hyperedge_count": observable_values[
            "support_changing_hyperedge_count"
        ],
        "conductance_improving_hyperedge_count": observable_values[
            "conductance_improving_hyperedge_count"
        ],
        "best_hyperedge": best,
        "hyperedge_table_sha256": pair.parent.sha_array(hyperedge_table),
        "observable_table_sha256": pair.parent.sha_array(observable_table),
    }

    hypergraph = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_sixj_borromean_hypergraph_screen@1",
        "object": "C985->d20",
        "parent": NONLOCAL_SCREEN_REPORT.relative_to(ROOT).as_posix(),
        "global_coherence_inputs": {
            "associator_report": ASSOCIATOR_REPORT.relative_to(ROOT).as_posix(),
            "pentagon_report": PENTAGON_REPORT.relative_to(ROOT).as_posix(),
        },
        "repair_hypergraph": {
            "vertex_partitions": {
                "cut_edge_vertices": 6,
                "repair_window_vertices": selected_codes,
                "f_address_vertices": selected_codes,
                "carrier_state_vertices": {
                    "base_count": observable_values["base_state_count"],
                    "best_joint_count": best["state_count"],
                },
            },
            "ordinary_edges": {
                "source": NONLOCAL_SCREEN_REPORT.relative_to(ROOT).as_posix(),
                "singleton_shadow_count": observable_values[
                    "ordinary_singleton_shadow_count"
                ],
                "pair_shadow_count": observable_values["ordinary_pair_shadow_count"],
                "support_changing_shadow_count": observable_values[
                    "ordinary_shadow_support_changing_count"
                ],
            },
            "hyperedges": {
                "triple_count": observable_values["hyperedge_count"],
                "pairwise_inert_count": observable_values[
                    "pairwise_inert_hyperedge_count"
                ],
                "borromean_opening_count": observable_values[
                    "borromean_opening_hyperedge_count"
                ],
            },
        },
        "summary": {
            "best_hyperedge_codes": [
                best["block_code_a"],
                best["block_code_b"],
                best["block_code_c"],
            ],
            "best_cut_conductance_x1e12": best["cut_conductance_x1e12"],
            "best_old_cut_edge_still_cut_count": best[
                "old_cut_edge_still_cut_count"
            ],
            "borromean_opening_hyperedge_count": observable_values[
                "borromean_opening_hyperedge_count"
            ],
        },
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_borromean_hypergraph_screen@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_SIXJ_BORROMEAN_HYPERGRAPH_SCREEN_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The bounded Borromean hypergraph screen uses the top-six nonlocal "
            "F-addresses whose singleton and pair shadows are already certified "
            "inert, then tests all 20 triple hyperedges. No tested hyperedge "
            "opens the six-edge aperture; every triple keeps all six old cut "
            "edges, and none improves conductance."
        ),
        "stage_protocol": {
            "draft": "start from the certified nonlocal F-symbol singleton/pair screen",
            "witness": "promote the selected F-addresses into a repair hypergraph with triple hyperedges",
            "coherence": "bind pairwise inert shadows to certified associator and pentagon reports",
            "closure": "test every top-six nonlocal triple hyperedge against fresh spectral cuts",
            "emit": "emit hypergraph, hyperedge table, observables, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "nonlocal_screen_report": pair.parent.input_entry(
                NONLOCAL_SCREEN_REPORT,
                {
                    "status": rows["nonlocal_report"].get("status"),
                    "certificate_sha256": rows["nonlocal_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "nonlocal_screen_certificate": pair.parent.input_entry(
                NONLOCAL_SCREEN_CERTIFICATE
            ),
            "nonlocal_screen_tables": pair.parent.input_entry(NONLOCAL_SCREEN_TABLES),
            "nonlocal_screen_json": pair.parent.input_entry(NONLOCAL_SCREEN_JSON),
            "associator_report": pair.parent.input_entry(
                ASSOCIATOR_REPORT,
                {
                    "status": rows["associator_report"].get("status"),
                    "certificate_sha256": rows["associator_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "pentagon_report": pair.parent.input_entry(
                PENTAGON_REPORT,
                {
                    "status": rows["pentagon_report"].get("status"),
                    "certificate_sha256": rows["pentagon_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "derive_script": pair.parent.input_entry(DERIVE_SCRIPT),
            "validator": pair.parent.input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": pair.parent.relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "hypergraph": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_sixj_borromean_hypergraph_screen.json"
            ),
            "hyperedge_csv": pair.parent.relpath(
                OUT_DIR / "sixj_borromean_hypergraph_hyperedges.csv"
            ),
            "observables_csv": pair.parent.relpath(
                OUT_DIR / "sixj_borromean_hypergraph_observables.csv"
            ),
            "tables": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_sixj_borromean_hypergraph_screen_tables.npz"
            ),
            "certificate": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_sixj_borromean_hypergraph_screen_certificate.json"
            ),
            "manifest": pair.parent.relpath(OUT_DIR / "manifest.json"),
            "report": pair.parent.relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "top-six nonlocal F-address repair hypergraph",
                "certified inert singleton and pair shadows for every tested hyperedge",
                "fresh spectral-cut test for all 20 top-six nonlocal triple hyperedges",
                "no bounded top-six Borromean opening class exists at triple level",
            ],
            "does_not_certify_because_not_required": [
                "all triples over the 145 mobile nonlocal F-addresses",
                "quadruple or higher hyperedges",
                "a complete numerical C985 F-symbol table",
                "full rigidity under the complete associator geometry",
            ],
        },
        "next_highest_yield_item": (
            "Search wider Borromean classes by using the top mobile nonlocal "
            "F-addresses beyond the first six, or prove a structural invariant "
            "that forces all pairwise-inert nonlocal triple hyperedges to keep "
            "the six old cut edges."
        ),
    }
    report["certificate_sha256"] = pair.parent.self_hash(report, "certificate_sha256")

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_sixj_borromean_hypergraph_screen_certificate@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the first Borromean test must be a hypergraph, not another repair graph",
            "the top-six nonlocal pairwise shadows are inert by the parent certificate",
            "all top-six triple hyperedges are also aperture-inert, so no bounded top-six Borromean class is found",
        ],
    }

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_borromean_hypergraph_screen_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified nonlocal F-symbol screen",
            "construct repair hypergraph vertices, ordinary shadows, and triple hyperedges",
            "verify every singleton and pair shadow is inert",
            "test all top-six nonlocal triple hyperedges against fresh spectral cuts",
            "check hashes, witnesses, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = pair.parent.self_hash(manifest, "manifest_sha256")

    return {
        "hypergraph": hypergraph,
        "hyperedge_csv": pair.csv_text(HYPEREDGE_COLUMNS, rows["hyperedge_rows"]),
        "observables_csv": pair.csv_text(OBSERVABLE_COLUMNS, rows["observable_rows"]),
        "hyperedge_table": hyperedge_table,
        "observable_table": observable_table,
        "certificate": certificate,
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
            "manifest": pair.parent.relpath(OUT_DIR / "manifest.json"),
            "report": pair.parent.relpath(OUT_DIR / "report.json"),
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
    updated["registry_sha256"] = pair.parent.self_hash(updated, "registry_sha256")
    pair.parent.write_json(INDEX_PATH, updated)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pair.parent.write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_borromean_hypergraph_screen.json",
        payloads["hypergraph"],
    )
    (OUT_DIR / "sixj_borromean_hypergraph_hyperedges.csv").write_text(
        payloads["hyperedge_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "sixj_borromean_hypergraph_observables.csv").write_text(
        payloads["observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_borromean_hypergraph_screen_tables.npz",
        hyperedge_table=payloads["hyperedge_table"],
        observable_table=payloads["observable_table"],
    )
    pair.parent.write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_borromean_hypergraph_screen_certificate.json",
        payloads["certificate"],
    )
    pair.parent.write_json(OUT_DIR / "report.json", payloads["report"])
    pair.parent.write_json(OUT_DIR / "manifest.json", payloads["manifest"])
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
                "report": pair.parent.relpath(OUT_DIR / "report.json"),
                "manifest": pair.parent.relpath(OUT_DIR / "manifest.json"),
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
