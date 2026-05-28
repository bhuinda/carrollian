from __future__ import annotations

import json
from itertools import combinations
from typing import Any

import numpy as np

try:
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction as pair
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction as pair
    from derive_c985_typed_simple_object_registry import INDEX_PATH
    from paths import D20_INVARIANTS, ROOT


THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_SIXJ_RECOUPLING_TRIPLE_FACE_OBSTRUCTION_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

PAIR_OBSTRUCTION_REPORT = pair.OUT_DIR / "report.json"
PAIR_OBSTRUCTION_CERTIFICATE = (
    pair.OUT_DIR
    / "signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction_certificate.json"
)
PAIR_OBSTRUCTION_TABLES = (
    pair.OUT_DIR
    / "signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction_tables.npz"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction.py"
)

K4_FACE_FRAME_EDGES = {
    12: (0, 2, 5),   # vertices 0,1,2 -> edges 01,02,12
    13: (0, 4, 3),   # vertices 0,1,3 -> edges 01,03,13
    23: (2, 4, 1),   # vertices 0,2,3 -> edges 02,03,23
    123: (5, 3, 1),  # vertices 1,2,3 -> edges 12,13,23
}

TRIPLE_COLUMNS = [
    "triple_id",
    "block_code_a",
    "block_code_b",
    "block_code_c",
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
]
FACE_COLUMNS = [
    "face_id",
    "edge_frame_id_0",
    "edge_frame_id_1",
    "edge_frame_id_2",
    "edge_id_0",
    "edge_id_1",
    "edge_id_2",
    "covered_triple_count",
    "best_triple_id",
    "best_triple_cut_conductance_x1e12",
    "best_triple_old_cut_edge_still_cut_count",
]
OBSERVABLE_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBSERVABLE_CODES = {
    "base_state_count": 0,
    "base_edge_count": 1,
    "base_cut_edge_count": 2,
    "base_cut_conductance_x1e12": 3,
    "candidate_block_count": 4,
    "triple_intervention_count": 5,
    "face_count": 6,
    "face_covered_count": 7,
    "support_changing_triple_count": 8,
    "best_block_code_a": 9,
    "best_block_code_b": 10,
    "best_block_code_c": 11,
    "best_state_count": 12,
    "best_edge_count": 13,
    "best_cut_edge_count": 14,
    "best_old_cut_edge_still_cut_count": 15,
    "best_lambda_2_x1e12": 16,
    "best_cut_conductance_x1e12": 17,
    "best_conductance_reduction_x1e12": 18,
    "best_full_face_count": 19,
    "closed_metric_word_count": 20,
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


def face_edge_ids(geometry: dict[str, Any]) -> dict[int, tuple[int, int, int]]:
    sorted_cut_edge_ids = tuple(sorted(geometry["cut_blocks_by_edge"]))
    return {
        face_code: tuple(sorted_cut_edge_ids[frame_id] for frame_id in frame_edges)
        for face_code, frame_edges in K4_FACE_FRAME_EDGES.items()
    }


def triple_touch_edges(
    blocks: tuple[tuple[int, int, int, int], ...],
    geometry: dict[str, Any],
) -> set[int]:
    return {
        edge_id
        for edge_id, per_edge in geometry["cut_blocks_by_edge"].items()
        if any(block in per_edge for block in blocks)
    }


def full_face_count(
    touched_edges: set[int],
    faces: dict[int, tuple[int, int, int]],
) -> int:
    return sum(int(set(edge_ids).issubset(touched_edges)) for edge_ids in faces.values())


def max_face_edge_touch_count(
    touched_edges: set[int],
    faces: dict[int, tuple[int, int, int]],
) -> int:
    return max(len(set(edge_ids) & touched_edges) for edge_ids in faces.values())


def evaluate_triple(
    triple_id: int,
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
    touched_edges = triple_touch_edges(blocks, geometry)
    return {
        "triple_id": triple_id,
        "block_code_a": pair.block_code(blocks[0]),
        "block_code_b": pair.block_code(blocks[1]),
        "block_code_c": pair.block_code(blocks[2]),
        "candidate_touch_count": sum(geometry["touch_counts"][block] for block in blocks),
        "cut_edge_touch_count": len(touched_edges),
        "full_face_count": full_face_count(touched_edges, faces),
        "max_face_edge_touch_count": max_face_edge_touch_count(touched_edges, faces),
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
    }


def build_payload_rows() -> dict[str, Any]:
    pair_report = load_json(PAIR_OBSTRUCTION_REPORT)
    candidate_blocks = [
        tuple(int(part) for part in block_text.split("."))
        for block_text in pair_report["witness"]["candidate_block_codes_as_words"]
    ] if "candidate_block_codes_as_words" in pair_report.get("witness", {}) else []
    if not candidate_blocks:
        code_to_block = {
            pair.block_code(block): block
            for block in pair.load_second_window_geometry()["touch_counts"]
        }
        candidate_blocks = [
            code_to_block[code] for code in pair_report["witness"]["candidate_block_codes"]
        ]

    geometry = pair.load_second_window_geometry()
    records = pair.precompute_closed_metric_records()
    faces = face_edge_ids(geometry)
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

    triple_rows = [
        evaluate_triple(
            triple_id,
            tuple(blocks),
            records,
            geometry,
            faces,
            base_conductance,
        )
        for triple_id, blocks in enumerate(combinations(candidate_blocks, 3))
    ]
    best = min(
        triple_rows,
        key=lambda row: (
            row["support_changed_flag"],
            row["cut_conductance_x1e12"],
            -row["lambda_2_x1e12"],
            row["block_code_a"],
            row["block_code_b"],
            row["block_code_c"],
        ),
    )
    best["selected_best_flag"] = 1

    face_rows = []
    for face_id, (face_code, edge_ids) in enumerate(faces.items()):
        covered = [
            row
            for row in triple_rows
            if set(edge_ids).issubset(
                triple_touch_edges(
                    tuple(
                        tuple(int(digit) for digit in f"{row[key]:04d}")
                        for key in [
                            "block_code_a",
                            "block_code_b",
                            "block_code_c",
                        ]
                    ),
                    geometry,
                )
            )
        ]
        best_face = min(
            covered,
            key=lambda row: (
                row["support_changed_flag"],
                row["cut_conductance_x1e12"],
                -row["lambda_2_x1e12"],
            ),
        )
        frame_edges = K4_FACE_FRAME_EDGES[face_code]
        face_rows.append(
            {
                "face_id": face_code,
                "edge_frame_id_0": frame_edges[0],
                "edge_frame_id_1": frame_edges[1],
                "edge_frame_id_2": frame_edges[2],
                "edge_id_0": edge_ids[0],
                "edge_id_1": edge_ids[1],
                "edge_id_2": edge_ids[2],
                "covered_triple_count": len(covered),
                "best_triple_id": best_face["triple_id"],
                "best_triple_cut_conductance_x1e12": best_face[
                    "cut_conductance_x1e12"
                ],
                "best_triple_old_cut_edge_still_cut_count": best_face[
                    "old_cut_edge_still_cut_count"
                ],
            }
        )

    observable_values = {
        "base_state_count": geometry["state_count"],
        "base_edge_count": geometry["edge_count"],
        "base_cut_edge_count": base_spectral["cut_edge_count"],
        "base_cut_conductance_x1e12": base_conductance,
        "candidate_block_count": len(candidate_blocks),
        "triple_intervention_count": len(triple_rows),
        "face_count": len(face_rows),
        "face_covered_count": sum(int(row["covered_triple_count"] > 0) for row in face_rows),
        "support_changing_triple_count": sum(row["support_changed_flag"] for row in triple_rows),
        "best_block_code_a": best["block_code_a"],
        "best_block_code_b": best["block_code_b"],
        "best_block_code_c": best["block_code_c"],
        "best_state_count": best["state_count"],
        "best_edge_count": best["edge_count"],
        "best_cut_edge_count": best["cut_edge_count"],
        "best_old_cut_edge_still_cut_count": best["old_cut_edge_still_cut_count"],
        "best_lambda_2_x1e12": best["lambda_2_x1e12"],
        "best_cut_conductance_x1e12": best["cut_conductance_x1e12"],
        "best_conductance_reduction_x1e12": best["conductance_reduction_x1e12"],
        "best_full_face_count": best["full_face_count"],
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
        "candidate_blocks": candidate_blocks,
        "triple_rows": triple_rows,
        "face_rows": face_rows,
        "observable_rows": observable_rows,
        "observable_values": observable_values,
        "record_count": len(records),
    }


def build_payloads() -> dict[str, Any]:
    pair_report = load_json(PAIR_OBSTRUCTION_REPORT)
    pair_certificate = load_json(PAIR_OBSTRUCTION_CERTIFICATE)
    rows = build_payload_rows()

    triple_table = table_from_rows(TRIPLE_COLUMNS, rows["triple_rows"])
    face_table = table_from_rows(FACE_COLUMNS, rows["face_rows"])
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, rows["observable_rows"])
    observable_values = rows["observable_values"]
    best = next(row for row in rows["triple_rows"] if row["selected_best_flag"])

    checks = {
        "pair_obstruction_report_certified": pair_report.get("status")
        == pair.STATUS,
        "pair_obstruction_certificate_certified": pair_certificate.get("status")
        == pair.STATUS,
        "base_cut_is_six_edges": (
            observable_values["base_state_count"],
            observable_values["base_edge_count"],
            observable_values["base_cut_edge_count"],
            observable_values["base_cut_conductance_x1e12"],
        )
        == (860, 2_571, 6, 4_329_004_000),
        "triple_scope_is_all_candidate_three_subsets": (
            observable_values["candidate_block_count"],
            observable_values["triple_intervention_count"],
            observable_values["face_count"],
            observable_values["face_covered_count"],
        )
        == (9, 84, 4, 4),
        "closed_metric_record_count_is_expected": observable_values[
            "closed_metric_word_count"
        ]
        == 984,
        "no_triple_changes_old_cut_support": observable_values[
            "support_changing_triple_count"
        ]
        == 0,
        "best_triple_improves_conductance_but_keeps_six_edges": (
            observable_values["best_block_code_a"],
            observable_values["best_block_code_b"],
            observable_values["best_block_code_c"],
            observable_values["best_state_count"],
            observable_values["best_edge_count"],
            observable_values["best_cut_edge_count"],
            observable_values["best_old_cut_edge_still_cut_count"],
            observable_values["best_cut_conductance_x1e12"],
            observable_values["best_conductance_reduction_x1e12"],
            observable_values["best_full_face_count"],
        )
        == (5_255, 1_252, 5_252, 900, 2_711, 6, 6, 3_649_635_000, 679_369_000, 2),
        "all_triple_rows_keep_old_cut_edges": all(
            row["old_cut_edge_still_cut_count"] == 6
            and row["old_cut_edge_same_side_count"] == 0
            for row in rows["triple_rows"]
        ),
        "every_face_best_keeps_six_old_edges": all(
            row["best_triple_old_cut_edge_still_cut_count"] == 6
            for row in rows["face_rows"]
        ),
        "table_shapes_match_codebooks": (
            tuple(triple_table.shape),
            tuple(face_table.shape),
            tuple(observable_table.shape),
        )
        == (
            (84, len(TRIPLE_COLUMNS)),
            (4, len(FACE_COLUMNS)),
            (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
        ),
    }

    witness = {
        "candidate_block_codes": [
            pair.block_code(block) for block in rows["candidate_blocks"]
        ],
        "triple_intervention_count": observable_values["triple_intervention_count"],
        "support_changing_triple_count": observable_values[
            "support_changing_triple_count"
        ],
        "best_triple": best,
        "face_rows": rows["face_rows"],
        "triple_table_sha256": pair.parent.sha_array(triple_table),
        "face_table_sha256": pair.parent.sha_array(face_table),
        "observable_table_sha256": pair.parent.sha_array(observable_table),
    }

    obstruction = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction@1",
        "object": "C985->d20",
        "parent": PAIR_OBSTRUCTION_REPORT.relative_to(ROOT).as_posix(),
        "search_scope": {
            "candidate_block_codes": [
                pair.block_code(block) for block in rows["candidate_blocks"]
            ],
            "interventions": "all three-block subsets of the nine K4-local touch blocks",
            "k4_faces": {
                str(face_code): list(edges)
                for face_code, edges in K4_FACE_FRAME_EDGES.items()
            },
        },
        "summary": {
            "triple_intervention_count": observable_values["triple_intervention_count"],
            "support_changing_triple_count": observable_values[
                "support_changing_triple_count"
            ],
            "best_block_codes": [
                observable_values["best_block_code_a"],
                observable_values["best_block_code_b"],
                observable_values["best_block_code_c"],
            ],
            "best_cut_conductance_x1e12": observable_values[
                "best_cut_conductance_x1e12"
            ],
            "best_old_cut_edge_still_cut_count": observable_values[
                "best_old_cut_edge_still_cut_count"
            ],
        },
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_SIXJ_RECOUPLING_TRIPLE_FACE_OBSTRUCTION_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "All 84 three-block interventions over the nine certified K4-local "
            "touch blocks preserve the old six-edge aperture. The best triple, "
            "5,2,5,5 with 1,2,5,2 and 5,2,5,2, lowers conductance to "
            "3649635000/1e12 but still keeps all six old cut edges on the "
            "fresh spectral cut."
        ),
        "stage_protocol": {
            "draft": "use the certified K4-local pair obstruction as the rank-two boundary",
            "witness": "enumerate all three-block K4-local interventions and K4 face cover rows",
            "coherence": "rebuild the promoted grammar and fresh spectral cut for each triple",
            "closure": "certify the rank-three/face obstruction inside the current touch-block alphabet",
            "emit": "emit triple, face, observable, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "pair_obstruction_report": pair.parent.input_entry(
                PAIR_OBSTRUCTION_REPORT,
                {
                    "status": pair_report.get("status"),
                    "certificate_sha256": pair_report.get("certificate_sha256"),
                },
            ),
            "pair_obstruction_certificate": pair.parent.input_entry(
                PAIR_OBSTRUCTION_CERTIFICATE
            ),
            "pair_obstruction_tables": pair.parent.input_entry(
                PAIR_OBSTRUCTION_TABLES
            ),
            "derive_script": pair.parent.input_entry(DERIVE_SCRIPT),
            "validator": pair.parent.input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": pair.parent.relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "triple_face_obstruction": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction.json"
            ),
            "triple_interventions_csv": pair.parent.relpath(
                OUT_DIR / "sixj_recoupling_triple_interventions.csv"
            ),
            "face_cover_csv": pair.parent.relpath(
                OUT_DIR / "sixj_recoupling_face_cover.csv"
            ),
            "observables_csv": pair.parent.relpath(
                OUT_DIR / "sixj_recoupling_triple_face_observables.csv"
            ),
            "tables": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction_tables.npz"
            ),
            "certificate": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction_certificate.json"
            ),
            "manifest": pair.parent.relpath(OUT_DIR / "manifest.json"),
            "report": pair.parent.relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "exhaustive three-block search over the nine declared K4-local touch blocks",
                "fresh spectral-cut comparison for every tested triple intervention",
                "absence of old-six-edge support change at recoupling rank three in the current touch-block alphabet",
                "the best conductance-improving triple still leaves the six old cut edges intact",
            ],
            "does_not_certify_because_not_required": [
                "four-block or all-face recoupling interventions",
                "new blocks outside the current six-edge touch alphabet",
                "a full C985 numerical F-symbol table",
                "compiler integration of the tested recoupling rules",
            ],
        },
        "next_highest_yield_item": (
            "Escalate from face/triple recoupling to full tetrahedral closure: "
            "test four-block interventions and the all-nine touch alphabet, "
            "because singleton, pair, and triple K4-local moves preserve the "
            "old six-edge aperture."
        ),
    }
    report["certificate_sha256"] = pair.parent.self_hash(report, "certificate_sha256")

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction_certificate@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "three-block K4-local recoupling is still below the aperture-opening threshold",
            "the best triple improves conductance but not cut support",
            "the next test is full tetrahedral closure over four or more touch blocks",
        ],
    }

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified recoupling-pair obstruction",
            "enumerate all three-block subsets of the nine K4-local touch blocks",
            "rebuild grammar, graph, automaton, and fresh spectral cut for every triple",
            "check old cut support, face coverage, conductance ranking, hashes, and registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = pair.parent.self_hash(manifest, "manifest_sha256")

    return {
        "triple_face_obstruction": obstruction,
        "triple_interventions_csv": pair.csv_text(
            TRIPLE_COLUMNS,
            rows["triple_rows"],
        ),
        "face_cover_csv": pair.csv_text(FACE_COLUMNS, rows["face_rows"]),
        "observables_csv": pair.csv_text(OBSERVABLE_COLUMNS, rows["observable_rows"]),
        "triple_table": triple_table,
        "face_table": face_table,
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
        / "signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction.json",
        payloads["triple_face_obstruction"],
    )
    (OUT_DIR / "sixj_recoupling_triple_interventions.csv").write_text(
        payloads["triple_interventions_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "sixj_recoupling_face_cover.csv").write_text(
        payloads["face_cover_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "sixj_recoupling_triple_face_observables.csv").write_text(
        payloads["observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction_tables.npz",
        triple_table=payloads["triple_table"],
        face_table=payloads["face_table"],
        observable_table=payloads["observable_table"],
    )
    pair.parent.write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction_certificate.json",
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
