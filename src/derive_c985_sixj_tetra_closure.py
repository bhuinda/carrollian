from __future__ import annotations

import json
from itertools import combinations
from typing import Any

import numpy as np

try:
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction as triple
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction as triple
    from derive_c985_typed_simple_object_registry import INDEX_PATH
    from paths import D20_INVARIANTS, ROOT


pair = triple.pair

THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_tetrahedral_closure_obstruction"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_SIXJ_RECOUPLING_TETRAHEDRAL_CLOSURE_OBSTRUCTION_CERTIFIED"
)
OUT_DIR_NAME = "c985_sixj_tetra_closure"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / OUT_DIR_NAME

TRIPLE_FACE_REPORT = triple.OUT_DIR / "report.json"
TRIPLE_FACE_CERTIFICATE = (
    triple.OUT_DIR
    / "signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction_certificate.json"
)
TRIPLE_FACE_TABLES = (
    triple.OUT_DIR
    / "signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction_tables.npz"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_sixj_tetra_closure.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_sixj_tetra_closure.py"
)

MIN_INTERVENTION_SIZE = 4
MAX_INTERVENTION_SIZE = 9

INTERVENTION_COLUMNS = [
    "intervention_id",
    "intervention_size",
    "block_code_0",
    "block_code_1",
    "block_code_2",
    "block_code_3",
    "block_code_4",
    "block_code_5",
    "block_code_6",
    "block_code_7",
    "block_code_8",
    "candidate_touch_count",
    "cut_edge_touch_count",
    "full_face_count",
    "max_face_edge_touch_count",
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
    "selected_best_flag",
    "all_nine_flag",
]
SIZE_SUMMARY_COLUMNS = [
    "intervention_size",
    "intervention_count",
    "support_changing_count",
    "best_intervention_id",
    "best_cut_conductance_x1e12",
    "best_lambda_2_x1e12",
    "best_state_count",
    "best_edge_count",
    "best_cut_edge_count",
    "best_old_cut_edge_still_cut_count",
    "best_promoted_only_cut_edge_count",
]
OBSERVABLE_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBSERVABLE_CODES = {
    "base_state_count": 0,
    "base_edge_count": 1,
    "base_cut_edge_count": 2,
    "base_cut_conductance_x1e12": 3,
    "candidate_block_count": 4,
    "min_intervention_size": 5,
    "max_intervention_size": 6,
    "intervention_count": 7,
    "rank4_intervention_count": 8,
    "rank5_intervention_count": 9,
    "rank6_intervention_count": 10,
    "rank7_intervention_count": 11,
    "rank8_intervention_count": 12,
    "rank9_intervention_count": 13,
    "support_changing_intervention_count": 14,
    "best_intervention_size": 15,
    "best_block_code_0": 16,
    "best_block_code_1": 17,
    "best_block_code_2": 18,
    "best_block_code_3": 19,
    "best_state_count": 20,
    "best_edge_count": 21,
    "best_cut_edge_count": 22,
    "best_old_cut_edge_still_cut_count": 23,
    "best_lambda_2_x1e12": 24,
    "best_cut_conductance_x1e12": 25,
    "best_conductance_reduction_x1e12": 26,
    "all_nine_state_count": 27,
    "all_nine_edge_count": 28,
    "all_nine_cut_edge_count": 29,
    "all_nine_old_cut_edge_still_cut_count": 30,
    "all_nine_promoted_only_cut_edge_count": 31,
    "all_nine_cut_conductance_x1e12": 32,
    "closed_metric_word_count": 33,
}


def table_from_rows(columns: list[str], rows: list[dict[str, int]]) -> np.ndarray:
    return np.asarray(
        [[int(row[column]) for column in columns] for row in rows],
        dtype=np.int64,
    )


def load_json(path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} is not a JSON object")
    return payload


def candidate_blocks_from_triple_report(
    geometry: dict[str, Any],
) -> list[tuple[int, int, int, int]]:
    triple_report = load_json(TRIPLE_FACE_REPORT)
    code_to_block = {
        pair.block_code(block): block for block in geometry["touch_counts"]
    }
    return [
        code_to_block[int(code)]
        for code in triple_report["witness"]["candidate_block_codes"]
    ]


def evaluate_intervention(
    intervention_id: int,
    blocks: tuple[tuple[int, int, int, int], ...],
    records: dict[tuple[int, ...], dict[str, Any]],
    geometry: dict[str, Any],
    faces: dict[int, tuple[int, int, int]],
    base_conductance: int,
) -> dict[str, int]:
    promoted_blocks = set(pair.BASE_BLOCKS) | set(blocks)
    rows_by_word = pair.rows_for_blocks(records, promoted_blocks)
    graph = pair.parent.build_graph(rows_by_word)
    automaton = pair.parent.build_automaton_rows(graph, geometry)
    spectral = automaton["spectral_rows"][0]
    touched_edges = triple.triple_touch_edges(blocks, geometry)
    block_codes = [pair.block_code(block) for block in blocks]
    padded_codes = block_codes + [-1] * (MAX_INTERVENTION_SIZE - len(block_codes))

    row = {
        "intervention_id": intervention_id,
        "intervention_size": len(blocks),
        "candidate_touch_count": sum(
            geometry["touch_counts"][block] for block in blocks
        ),
        "cut_edge_touch_count": len(touched_edges),
        "full_face_count": triple.full_face_count(touched_edges, faces),
        "max_face_edge_touch_count": triple.max_face_edge_touch_count(
            touched_edges,
            faces,
        ),
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
        "support_changed_flag": int(
            spectral["old_cut_edge_still_cut_count"] < 6
            or spectral["old_cut_edge_same_side_count"] > 0
        ),
        "selected_best_flag": 0,
        "all_nine_flag": int(len(blocks) == MAX_INTERVENTION_SIZE),
    }
    for index, code in enumerate(padded_codes):
        row[f"block_code_{index}"] = code
    return row


def best_key(row: dict[str, int]) -> tuple[Any, ...]:
    codes = tuple(row[f"block_code_{index}"] for index in range(MAX_INTERVENTION_SIZE))
    return (
        row["support_changed_flag"],
        row["cut_conductance_x1e12"],
        -row["lambda_2_x1e12"],
        row["intervention_size"],
        codes,
    )


def build_payload_rows() -> dict[str, Any]:
    triple_report = load_json(TRIPLE_FACE_REPORT)
    triple_certificate = load_json(TRIPLE_FACE_CERTIFICATE)
    geometry = pair.load_second_window_geometry()
    records = pair.precompute_closed_metric_records()
    faces = triple.face_edge_ids(geometry)
    candidate_blocks = candidate_blocks_from_triple_report(geometry)
    base_spectral = pair.parent.table_rows(
        np.asarray(
            np.load(pair.SECOND_WINDOW_PROMOTION_TABLES, allow_pickle=False)[
                "spectral_cut_table"
            ],
            dtype=np.int64,
        ),
        pair.parent.SPECTRAL_CUT_COLUMNS,
    )[0]
    base_conductance = base_spectral["cut_conductance_x1e12"]

    intervention_rows = []
    intervention_id = 0
    for size in range(MIN_INTERVENTION_SIZE, MAX_INTERVENTION_SIZE + 1):
        for blocks in combinations(candidate_blocks, size):
            intervention_rows.append(
                evaluate_intervention(
                    intervention_id,
                    tuple(blocks),
                    records,
                    geometry,
                    faces,
                    base_conductance,
                )
            )
            intervention_id += 1

    best = min(intervention_rows, key=best_key)
    best["selected_best_flag"] = 1
    all_nine = next(row for row in intervention_rows if row["all_nine_flag"] == 1)

    size_rows = []
    for size in range(MIN_INTERVENTION_SIZE, MAX_INTERVENTION_SIZE + 1):
        per_size = [
            row for row in intervention_rows if row["intervention_size"] == size
        ]
        size_best = min(per_size, key=best_key)
        size_rows.append(
            {
                "intervention_size": size,
                "intervention_count": len(per_size),
                "support_changing_count": sum(
                    row["support_changed_flag"] for row in per_size
                ),
                "best_intervention_id": size_best["intervention_id"],
                "best_cut_conductance_x1e12": size_best[
                    "cut_conductance_x1e12"
                ],
                "best_lambda_2_x1e12": size_best["lambda_2_x1e12"],
                "best_state_count": size_best["state_count"],
                "best_edge_count": size_best["edge_count"],
                "best_cut_edge_count": size_best["cut_edge_count"],
                "best_old_cut_edge_still_cut_count": size_best[
                    "old_cut_edge_still_cut_count"
                ],
                "best_promoted_only_cut_edge_count": size_best[
                    "promoted_only_cut_edge_count"
                ],
            }
        )

    observable_values = {
        "base_state_count": geometry["state_count"],
        "base_edge_count": geometry["edge_count"],
        "base_cut_edge_count": base_spectral["cut_edge_count"],
        "base_cut_conductance_x1e12": base_conductance,
        "candidate_block_count": len(candidate_blocks),
        "min_intervention_size": MIN_INTERVENTION_SIZE,
        "max_intervention_size": MAX_INTERVENTION_SIZE,
        "intervention_count": len(intervention_rows),
        "rank4_intervention_count": sum(
            row["intervention_size"] == 4 for row in intervention_rows
        ),
        "rank5_intervention_count": sum(
            row["intervention_size"] == 5 for row in intervention_rows
        ),
        "rank6_intervention_count": sum(
            row["intervention_size"] == 6 for row in intervention_rows
        ),
        "rank7_intervention_count": sum(
            row["intervention_size"] == 7 for row in intervention_rows
        ),
        "rank8_intervention_count": sum(
            row["intervention_size"] == 8 for row in intervention_rows
        ),
        "rank9_intervention_count": sum(
            row["intervention_size"] == 9 for row in intervention_rows
        ),
        "support_changing_intervention_count": sum(
            row["support_changed_flag"] for row in intervention_rows
        ),
        "best_intervention_size": best["intervention_size"],
        "best_block_code_0": best["block_code_0"],
        "best_block_code_1": best["block_code_1"],
        "best_block_code_2": best["block_code_2"],
        "best_block_code_3": best["block_code_3"],
        "best_state_count": best["state_count"],
        "best_edge_count": best["edge_count"],
        "best_cut_edge_count": best["cut_edge_count"],
        "best_old_cut_edge_still_cut_count": best[
            "old_cut_edge_still_cut_count"
        ],
        "best_lambda_2_x1e12": best["lambda_2_x1e12"],
        "best_cut_conductance_x1e12": best["cut_conductance_x1e12"],
        "best_conductance_reduction_x1e12": best[
            "conductance_reduction_x1e12"
        ],
        "all_nine_state_count": all_nine["state_count"],
        "all_nine_edge_count": all_nine["edge_count"],
        "all_nine_cut_edge_count": all_nine["cut_edge_count"],
        "all_nine_old_cut_edge_still_cut_count": all_nine[
            "old_cut_edge_still_cut_count"
        ],
        "all_nine_promoted_only_cut_edge_count": all_nine[
            "promoted_only_cut_edge_count"
        ],
        "all_nine_cut_conductance_x1e12": all_nine[
            "cut_conductance_x1e12"
        ],
        "closed_metric_word_count": len(records),
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
        "triple_report": triple_report,
        "triple_certificate": triple_certificate,
        "candidate_blocks": candidate_blocks,
        "intervention_rows": intervention_rows,
        "size_rows": size_rows,
        "observable_rows": observable_rows,
        "observable_values": observable_values,
        "record_count": len(records),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_payload_rows()
    intervention_table = table_from_rows(
        INTERVENTION_COLUMNS,
        rows["intervention_rows"],
    )
    size_summary_table = table_from_rows(
        SIZE_SUMMARY_COLUMNS,
        rows["size_rows"],
    )
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, rows["observable_rows"])
    observable_values = rows["observable_values"]
    best = next(
        row for row in rows["intervention_rows"] if row["selected_best_flag"]
    )
    all_nine = next(row for row in rows["intervention_rows"] if row["all_nine_flag"])

    checks = {
        "triple_face_report_certified": rows["triple_report"].get("status")
        == triple.STATUS,
        "triple_face_certificate_certified": rows["triple_certificate"].get(
            "status"
        )
        == triple.STATUS,
        "base_cut_is_six_edges": (
            observable_values["base_state_count"],
            observable_values["base_edge_count"],
            observable_values["base_cut_edge_count"],
            observable_values["base_cut_conductance_x1e12"],
        )
        == (860, 2_571, 6, 4_329_004_000),
        "closure_scope_is_all_candidate_subsets_size_four_through_nine": (
            observable_values["candidate_block_count"],
            observable_values["min_intervention_size"],
            observable_values["max_intervention_size"],
            observable_values["intervention_count"],
            observable_values["rank4_intervention_count"],
            observable_values["rank5_intervention_count"],
            observable_values["rank6_intervention_count"],
            observable_values["rank7_intervention_count"],
            observable_values["rank8_intervention_count"],
            observable_values["rank9_intervention_count"],
        )
        == (9, 4, 9, 382, 126, 126, 84, 36, 9, 1),
        "closed_metric_record_count_is_expected": observable_values[
            "closed_metric_word_count"
        ]
        == 984,
        "no_closure_intervention_changes_old_cut_support": observable_values[
            "support_changing_intervention_count"
        ]
        == 0,
        "best_closure_intervention_improves_conductance_but_keeps_six_edges": (
            observable_values["best_intervention_size"],
            observable_values["best_block_code_0"],
            observable_values["best_block_code_1"],
            observable_values["best_block_code_2"],
            observable_values["best_block_code_3"],
            observable_values["best_state_count"],
            observable_values["best_edge_count"],
            observable_values["best_cut_edge_count"],
            observable_values["best_old_cut_edge_still_cut_count"],
            observable_values["best_cut_conductance_x1e12"],
            observable_values["best_conductance_reduction_x1e12"],
        )
        == (4, 4_552, 5_255, 1_252, 5_252, 900, 2_711, 6, 6, 3_649_635_000, 679_369_000),
        "all_nine_stress_case_keeps_six_old_edges": (
            observable_values["all_nine_state_count"],
            observable_values["all_nine_edge_count"],
            observable_values["all_nine_cut_edge_count"],
            observable_values["all_nine_old_cut_edge_still_cut_count"],
            observable_values["all_nine_promoted_only_cut_edge_count"],
            observable_values["all_nine_cut_conductance_x1e12"],
        )
        == (975, 3_068, 11, 6, 5, 4_934_948_000),
        "all_closure_rows_keep_old_cut_edges": all(
            row["old_cut_edge_still_cut_count"] == 6
            and row["old_cut_edge_same_side_count"] == 0
            for row in rows["intervention_rows"]
        ),
        "table_shapes_match_codebooks": (
            tuple(intervention_table.shape),
            tuple(size_summary_table.shape),
            tuple(observable_table.shape),
        )
        == (
            (382, len(INTERVENTION_COLUMNS)),
            (6, len(SIZE_SUMMARY_COLUMNS)),
            (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
        ),
    }

    witness = {
        "candidate_block_codes": [
            pair.block_code(block) for block in rows["candidate_blocks"]
        ],
        "intervention_count": observable_values["intervention_count"],
        "rank_counts": {
            str(size): next(
                row["intervention_count"]
                for row in rows["size_rows"]
                if row["intervention_size"] == size
            )
            for size in range(MIN_INTERVENTION_SIZE, MAX_INTERVENTION_SIZE + 1)
        },
        "support_changing_intervention_count": observable_values[
            "support_changing_intervention_count"
        ],
        "best_intervention": best,
        "all_nine_intervention": all_nine,
        "size_rows": rows["size_rows"],
        "intervention_table_sha256": pair.parent.sha_array(intervention_table),
        "size_summary_table_sha256": pair.parent.sha_array(size_summary_table),
        "observable_table_sha256": pair.parent.sha_array(observable_table),
    }

    obstruction = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_tetrahedral_closure_obstruction@1",
        "object": "C985->d20",
        "parent": TRIPLE_FACE_REPORT.relative_to(ROOT).as_posix(),
        "search_scope": {
            "candidate_block_codes": witness["candidate_block_codes"],
            "interventions": (
                "all subsets of size four through nine of the nine K4-local "
                "touch blocks, including the all-nine alphabet"
            ),
            "base_promoted_blocks": [
                pair.block_text(block) for block in pair.BASE_BLOCKS
            ],
        },
        "summary": {
            "intervention_count": observable_values["intervention_count"],
            "support_changing_intervention_count": observable_values[
                "support_changing_intervention_count"
            ],
            "best_block_codes": [
                best[f"block_code_{index}"]
                for index in range(best["intervention_size"])
            ],
            "best_cut_conductance_x1e12": best["cut_conductance_x1e12"],
            "best_old_cut_edge_still_cut_count": best[
                "old_cut_edge_still_cut_count"
            ],
            "all_nine_cut_edge_count": all_nine["cut_edge_count"],
            "all_nine_old_cut_edge_still_cut_count": all_nine[
                "old_cut_edge_still_cut_count"
            ],
        },
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_tetrahedral_closure_obstruction@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_SIXJ_RECOUPLING_TETRAHEDRAL_CLOSURE_OBSTRUCTION_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "All 382 rank-four-through-rank-nine interventions over the nine "
            "certified K4-local touch blocks preserve the old six-edge "
            "aperture. The all-nine stress case creates 11 fresh cut edges, "
            "but the old six cut edges all remain on the cut."
        ),
        "stage_protocol": {
            "draft": "use the certified rank-three/face obstruction as the boundary",
            "witness": "enumerate every K4-local subset of size four through nine",
            "coherence": "rebuild the promoted grammar and fresh spectral cut for every intervention",
            "closure": "certify full tetrahedral touch-alphabet obstruction inside the current K4-local scope",
            "emit": "emit intervention, rank-summary, observable, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "triple_face_report": pair.parent.input_entry(
                TRIPLE_FACE_REPORT,
                {
                    "status": rows["triple_report"].get("status"),
                    "certificate_sha256": rows["triple_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "triple_face_certificate": pair.parent.input_entry(
                TRIPLE_FACE_CERTIFICATE
            ),
            "triple_face_tables": pair.parent.input_entry(TRIPLE_FACE_TABLES),
            "derive_script": pair.parent.input_entry(DERIVE_SCRIPT),
            "validator": pair.parent.input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": pair.parent.relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "tetrahedral_closure_obstruction": pair.parent.relpath(
                OUT_DIR
                / "sixj_tetra_closure.json"
            ),
            "interventions_csv": pair.parent.relpath(
                OUT_DIR / "sixj_recoupling_tetrahedral_closure_interventions.csv"
            ),
            "size_summary_csv": pair.parent.relpath(
                OUT_DIR / "sixj_recoupling_tetrahedral_size_summary.csv"
            ),
            "observables_csv": pair.parent.relpath(
                OUT_DIR / "sixj_recoupling_tetrahedral_closure_observables.csv"
            ),
            "tables": pair.parent.relpath(
                OUT_DIR
                / "sixj_tetra_closure_tables.npz"
            ),
            "certificate": pair.parent.relpath(
                OUT_DIR
                / "sixj_tetra_closure_certificate.json"
            ),
            "manifest": pair.parent.relpath(OUT_DIR / "manifest.json"),
            "report": pair.parent.relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "exhaustive K4-local search over every subset size four through nine of the declared touch alphabet",
                "fresh spectral-cut comparison for every tested closure intervention",
                "absence of old-six-edge support change throughout the full current K4-local touch alphabet",
                "the all-nine stress case still leaves the old six cut edges intact",
            ],
            "does_not_certify_because_not_required": [
                "blocks outside the current six-edge touch alphabet",
                "nonlocal F-symbol or pentagon-addressed recouplings not visible as current touch blocks",
                "a full C985 numerical F-symbol table",
                "compiler integration of the tested recoupling rules",
            ],
        },
        "next_highest_yield_item": (
            "Leave the current K4-local touch alphabet and derive a genuinely "
            "new nonlocal F-symbol/pentagon-addressed recoupling candidate, "
            "because every subset of the current nine-block tetrahedral "
            "alphabet preserves the old six-edge aperture."
        ),
    }
    report["certificate_sha256"] = pair.parent.self_hash(report, "certificate_sha256")

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_tetrahedral_closure_obstruction_certificate@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the current K4-local touch alphabet is exhausted through all subset sizes",
            "larger local recouplings add fresh cut edges before they remove old ones",
            "the next aperture-opening candidate must come from outside the current touch alphabet",
        ],
    }

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_tetrahedral_closure_obstruction_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified recoupling-triple/face obstruction",
            "enumerate every candidate subset of size four through nine",
            "rebuild grammar, graph, automaton, and fresh spectral cut for every intervention",
            "check old cut support, rank summaries, all-nine stress case, hashes, and registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = pair.parent.self_hash(manifest, "manifest_sha256")

    return {
        "tetrahedral_closure_obstruction": obstruction,
        "interventions_csv": pair.csv_text(
            INTERVENTION_COLUMNS,
            rows["intervention_rows"],
        ),
        "size_summary_csv": pair.csv_text(SIZE_SUMMARY_COLUMNS, rows["size_rows"]),
        "observables_csv": pair.csv_text(
            OBSERVABLE_COLUMNS,
            rows["observable_rows"],
        ),
        "intervention_table": intervention_table,
        "size_summary_table": size_summary_table,
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
        / "sixj_tetra_closure.json",
        payloads["tetrahedral_closure_obstruction"],
    )
    (OUT_DIR / "sixj_recoupling_tetrahedral_closure_interventions.csv").write_text(
        payloads["interventions_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "sixj_recoupling_tetrahedral_size_summary.csv").write_text(
        payloads["size_summary_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "sixj_recoupling_tetrahedral_closure_observables.csv").write_text(
        payloads["observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "sixj_tetra_closure_tables.npz",
        intervention_table=payloads["intervention_table"],
        size_summary_table=payloads["size_summary_table"],
        observable_table=payloads["observable_table"],
    )
    pair.parent.write_json(
        OUT_DIR
        / "sixj_tetra_closure_certificate.json",
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
