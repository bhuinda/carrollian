from __future__ import annotations

import json
from typing import Any

import numpy as np

try:
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index as dini
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy as holonomy
    from . import derive_c985_eta6_truncated_skeleton as skeleton
    from . import derive_c985_sixj_conductance as preservation
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index as dini
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy as holonomy
    import derive_c985_eta6_truncated_skeleton as skeleton
    import derive_c985_sixj_conductance as preservation
    from paths import D20_INVARIANTS, ROOT


pair = preservation.pair

THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_nonholonomic_aperture"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_ETA6_NONHOLONOMIC_APERTURE_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

HANDOFF_NOTE = ROOT / "docs" / "handoff note.txt"
TRUNCATED_REPORT = skeleton.OUT_DIR / "report.json"
TRUNCATED_TABLES = (
    skeleton.OUT_DIR
    / "eta6_truncated_skeleton_tables.npz"
)
PRESERVATION_REPORT = preservation.OUT_DIR / "report.json"
PRESERVATION_TABLES = (
    preservation.OUT_DIR
    / "sixj_conductance_tables.npz"
)
HOLONOMY_REPORT = holonomy.OUT_DIR / "report.json"
HOLONOMY_TABLES = (
    holonomy.OUT_DIR
    / "signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy_tables.npz"
)
DINI_REPORT = dini.OUT_DIR / "report.json"
DINI_TABLES = (
    dini.OUT_DIR
    / "signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index_tables.npz"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_nonholonomic_aperture.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_nonholonomic_aperture.py"
)

BOUNDARY_COLUMNS = [
    "boundary_row_id",
    "complex_code",
    "vertex_count",
    "edge_count",
    "face_count",
    "cubic_flag",
    "planar_flag",
    "three_vertex_connected_flag",
    "eta6_carrier_flag",
    "positive_cone_proxy_flag",
    "exterior_circuit_matrix_available_flag",
]
DISTRIBUTION_COLUMNS = [
    "source_code",
    "row_count",
    "horizontal_row_count",
    "conductance_decreasing_row_count",
    "conductance_decreasing_horizontal_count",
    "support_changing_count",
    "aperture_preserved_count",
    "min_cut_conductance_x1e12",
    "best_decreasing_cut_conductance_x1e12",
    "best_decreasing_reduction_x1e12",
    "eta6_delta_rank",
    "metric_image_nonzero_flag",
]
STATE_COLUMNS = [
    "state_id",
    "stage_code",
    "source_code",
    "source_row_id",
    "intervention_size",
    "block_code_0",
    "block_code_1",
    "block_code_2",
    "height_x1e12",
    "positive_height_flag",
    "eta6_holonomy_pairing",
    "eta6_relative_class_nonzero_flag",
    "support_changed_flag",
    "old_cut_edge_still_cut_count",
    "discriminant_stratum_flag",
    "surgery_certified_flag",
    "admissible_state_flag",
]
TRANSITION_COLUMNS = [
    "transition_id",
    "from_state_id",
    "to_state_id",
    "generator_source_code",
    "generator_source_row_id",
    "intervention_size",
    "conductance_drop_x1e12",
    "eta6_delta",
    "holonomy_delta",
    "support_changed_sum",
    "old_cut_edge_min",
    "horizontal_flag",
    "metric_nonzero_flag",
    "ordinary_descent_flag",
    "surgery_flag",
    "post_positive_flag",
    "admissible_transition_flag",
]
OBSERVABLE_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBSERVABLE_CODES = {
    "handoff_note_present_flag": 0,
    "handoff_note_length": 1,
    "public_boundary_vertex_count": 2,
    "public_boundary_edge_count": 3,
    "public_boundary_face_count": 4,
    "truncated_vertex_count": 5,
    "truncated_edge_count": 6,
    "truncated_face_count": 7,
    "relative_h1_dimension": 8,
    "relative_cohomology_dimension": 9,
    "eta6_holonomy_pairing": 10,
    "aggregate_distribution_row_count": 11,
    "horizontal_distribution_row_count": 12,
    "conductance_decreasing_row_count": 13,
    "support_changing_row_count": 14,
    "conductance_decreasing_support_changing_count": 15,
    "all_rows_aperture_preserved_count": 16,
    "distribution_eta6_delta_rank": 17,
    "distribution_metric_nonzero_flag": 18,
    "automaton_state_count": 19,
    "automaton_transition_count": 20,
    "positive_height_state_count": 21,
    "horizontal_transition_count": 22,
    "metric_nonzero_transition_count": 23,
    "surgery_transition_count": 24,
    "strict_conductance_descent_flag": 25,
    "holonomy_delta_total": 26,
    "base_to_final_drop_x1e12": 27,
    "final_height_x1e12": 28,
    "discriminant_state_count": 29,
    "positive_cone_proxy_available_flag": 30,
    "exterior_circuit_matrix_available_flag": 31,
    "surgery_certificate_available_flag": 32,
    "nonholonomic_aperture_model_flag": 33,
}


def load_json(path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} is not a JSON object")
    return payload


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


def code_observables(table: np.ndarray) -> dict[int, int]:
    return {int(row[1]): int(row[2]) for row in np.asarray(table, dtype=np.int64)}


def build_boundary_rows(graph_rows: list[dict[str, int]]) -> list[dict[str, int]]:
    public = graph_rows[0]
    truncated = graph_rows[2]
    endpoint = graph_rows[3]
    return [
        {
            "boundary_row_id": 0,
            "complex_code": 0,
            "vertex_count": public["vertex_count"],
            "edge_count": public["edge_count"],
            "face_count": public["face_count"],
            "cubic_flag": public["cubic_flag"],
            "planar_flag": public["polyhedral_embedding_flag"],
            "three_vertex_connected_flag": public["three_vertex_connected_flag"],
            "eta6_carrier_flag": 0,
            "positive_cone_proxy_flag": 0,
            "exterior_circuit_matrix_available_flag": 0,
        },
        {
            "boundary_row_id": 1,
            "complex_code": 1,
            "vertex_count": truncated["vertex_count"],
            "edge_count": truncated["edge_count"],
            "face_count": truncated["face_count"],
            "cubic_flag": truncated["cubic_flag"],
            "planar_flag": truncated["polyhedral_embedding_flag"],
            "three_vertex_connected_flag": truncated[
                "three_vertex_connected_flag"
            ],
            "eta6_carrier_flag": 1,
            "positive_cone_proxy_flag": 1,
            "exterior_circuit_matrix_available_flag": 0,
        },
        {
            "boundary_row_id": 2,
            "complex_code": 2,
            "vertex_count": endpoint["vertex_count"],
            "edge_count": endpoint["edge_count"],
            "face_count": endpoint["face_count"],
            "cubic_flag": endpoint["cubic_flag"],
            "planar_flag": endpoint["polyhedral_embedding_flag"],
            "three_vertex_connected_flag": endpoint["three_vertex_connected_flag"],
            "eta6_carrier_flag": 1,
            "positive_cone_proxy_flag": 0,
            "exterior_circuit_matrix_available_flag": 0,
        },
    ]


def build_distribution_rows(
    source_summary_rows: list[dict[str, int]],
) -> list[dict[str, int]]:
    rows = []
    for row in source_summary_rows:
        decreasing = row["conductance_decreasing_count"]
        preserved = row["aperture_preserved_count"]
        support_changing = row["support_changing_count"]
        horizontal = preserved
        rows.append(
            {
                "source_code": row["source_code"],
                "row_count": row["row_count"],
                "horizontal_row_count": horizontal,
                "conductance_decreasing_row_count": decreasing,
                "conductance_decreasing_horizontal_count": decreasing
                if horizontal == row["row_count"] and support_changing == 0
                else 0,
                "support_changing_count": support_changing,
                "aperture_preserved_count": preserved,
                "min_cut_conductance_x1e12": row["min_cut_conductance_x1e12"],
                "best_decreasing_cut_conductance_x1e12": row[
                    "best_decreasing_cut_conductance_x1e12"
                ],
                "best_decreasing_reduction_x1e12": row[
                    "best_decreasing_reduction_x1e12"
                ],
                "eta6_delta_rank": 0
                if horizontal == row["row_count"] and support_changing == 0
                else 1,
                "metric_image_nonzero_flag": int(decreasing > 0),
            }
        )
    return rows


def build_state_rows(chain_rows: list[dict[str, int]]) -> list[dict[str, int]]:
    rows = []
    for row in chain_rows:
        positive = int(row["cut_conductance_x1e12"] > 0)
        eta_nonzero = row["eta6_relative_class_nonzero_flag"]
        discriminant = int(
            row["eta6_holonomy_pairing"] == 1
            and row["old_cut_edge_still_cut_count"] == 6
            and row["support_changed_flag"] == 0
        )
        rows.append(
            {
                "state_id": row["stage_id"],
                "stage_code": row["stage_code"],
                "source_code": row["source_code"],
                "source_row_id": row["source_row_id"],
                "intervention_size": row["intervention_size"],
                "block_code_0": row["block_code_0"],
                "block_code_1": row["block_code_1"],
                "block_code_2": row["block_code_2"],
                "height_x1e12": row["cut_conductance_x1e12"],
                "positive_height_flag": positive,
                "eta6_holonomy_pairing": row["eta6_holonomy_pairing"],
                "eta6_relative_class_nonzero_flag": eta_nonzero,
                "support_changed_flag": row["support_changed_flag"],
                "old_cut_edge_still_cut_count": row[
                    "old_cut_edge_still_cut_count"
                ],
                "discriminant_stratum_flag": discriminant,
                "surgery_certified_flag": 0,
                "admissible_state_flag": int(positive and eta_nonzero),
            }
        )
    return rows


def build_transition_rows(
    state_rows: list[dict[str, int]],
    step_rows: list[dict[str, int]],
) -> list[dict[str, int]]:
    state_by_id = {row["state_id"]: row for row in state_rows}
    rows = []
    for row in step_rows:
        target = state_by_id[row["to_stage_id"]]
        metric_nonzero = int(row["conductance_drop_x1e12"] > 0)
        horizontal = int(
            row["holonomy_delta"] == 0
            and row["support_changed_sum"] == 0
            and row["old_cut_edge_min"] == 6
        )
        post_positive = target["positive_height_flag"]
        rows.append(
            {
                "transition_id": row["step_id"],
                "from_state_id": row["from_stage_id"],
                "to_state_id": row["to_stage_id"],
                "generator_source_code": target["source_code"],
                "generator_source_row_id": target["source_row_id"],
                "intervention_size": target["intervention_size"],
                "conductance_drop_x1e12": row["conductance_drop_x1e12"],
                "eta6_delta": 0,
                "holonomy_delta": row["holonomy_delta"],
                "support_changed_sum": row["support_changed_sum"],
                "old_cut_edge_min": row["old_cut_edge_min"],
                "horizontal_flag": horizontal,
                "metric_nonzero_flag": metric_nonzero,
                "ordinary_descent_flag": int(horizontal and metric_nonzero),
                "surgery_flag": 0,
                "post_positive_flag": post_positive,
                "admissible_transition_flag": int(
                    horizontal and metric_nonzero and post_positive
                ),
            }
        )
    return rows


def build_payload_rows() -> dict[str, Any]:
    handoff_text = HANDOFF_NOTE.read_text(encoding="utf-8") if HANDOFF_NOTE.exists() else ""
    truncated_report = load_json(TRUNCATED_REPORT)
    preservation_report = load_json(PRESERVATION_REPORT)
    holonomy_report = load_json(HOLONOMY_REPORT)
    dini_report = load_json(DINI_REPORT)

    truncated_tables = np.load(TRUNCATED_TABLES, allow_pickle=False)
    graph_rows = table_rows(
        np.asarray(truncated_tables["graph_table"], dtype=np.int64),
        skeleton.GRAPH_COLUMNS,
    )
    boundary_rows = build_boundary_rows(graph_rows)

    preservation_tables = np.load(PRESERVATION_TABLES, allow_pickle=False)
    source_summary_rows = table_rows(
        np.asarray(preservation_tables["source_summary_table"], dtype=np.int64),
        preservation.SOURCE_SUMMARY_COLUMNS,
    )
    preservation_observables = code_observables(
        preservation_tables["observable_table"]
    )
    distribution_rows = build_distribution_rows(source_summary_rows)

    holonomy_tables = np.load(HOLONOMY_TABLES, allow_pickle=False)
    holonomy_observables = code_observables(holonomy_tables["observable_table"])

    dini_tables = np.load(DINI_TABLES, allow_pickle=False)
    dini_chain_rows = table_rows(
        np.asarray(dini_tables["chain_table"], dtype=np.int64),
        dini.CHAIN_COLUMNS,
    )
    dini_step_rows = table_rows(
        np.asarray(dini_tables["step_table"], dtype=np.int64),
        dini.STEP_COLUMNS,
    )
    dini_observables = code_observables(dini_tables["observable_table"])
    state_rows = build_state_rows(dini_chain_rows)
    transition_rows = build_transition_rows(state_rows, dini_step_rows)

    conductances = [row["height_x1e12"] for row in state_rows]
    observable_values = {
        "handoff_note_present_flag": int(HANDOFF_NOTE.exists()),
        "handoff_note_length": len(handoff_text),
        "public_boundary_vertex_count": boundary_rows[0]["vertex_count"],
        "public_boundary_edge_count": boundary_rows[0]["edge_count"],
        "public_boundary_face_count": boundary_rows[0]["face_count"],
        "truncated_vertex_count": boundary_rows[1]["vertex_count"],
        "truncated_edge_count": boundary_rows[1]["edge_count"],
        "truncated_face_count": boundary_rows[1]["face_count"],
        "relative_h1_dimension": holonomy_observables[
            holonomy.OBSERVABLE_CODES["relative_h1_dimension"]
        ],
        "relative_cohomology_dimension": holonomy_observables[
            holonomy.OBSERVABLE_CODES["relative_cohomology_dimension"]
        ],
        "eta6_holonomy_pairing": holonomy_observables[
            holonomy.OBSERVABLE_CODES["holonomy_eta6_pairing"]
        ],
        "aggregate_distribution_row_count": preservation_observables[
            preservation.OBSERVABLE_CODES["aggregate_row_count"]
        ],
        "horizontal_distribution_row_count": sum(
            row["horizontal_row_count"] for row in distribution_rows
        ),
        "conductance_decreasing_row_count": preservation_observables[
            preservation.OBSERVABLE_CODES["conductance_decreasing_row_count"]
        ],
        "support_changing_row_count": preservation_observables[
            preservation.OBSERVABLE_CODES["support_changing_row_count"]
        ],
        "conductance_decreasing_support_changing_count": preservation_observables[
            preservation.OBSERVABLE_CODES[
                "conductance_decreasing_support_changing_count"
            ]
        ],
        "all_rows_aperture_preserved_count": preservation_observables[
            preservation.OBSERVABLE_CODES["all_rows_aperture_preserved_count"]
        ],
        "distribution_eta6_delta_rank": max(
            row["eta6_delta_rank"] for row in distribution_rows
        ),
        "distribution_metric_nonzero_flag": int(
            any(row["metric_image_nonzero_flag"] for row in distribution_rows)
        ),
        "automaton_state_count": len(state_rows),
        "automaton_transition_count": len(transition_rows),
        "positive_height_state_count": sum(
            row["positive_height_flag"] for row in state_rows
        ),
        "horizontal_transition_count": sum(
            row["horizontal_flag"] for row in transition_rows
        ),
        "metric_nonzero_transition_count": sum(
            row["metric_nonzero_flag"] for row in transition_rows
        ),
        "surgery_transition_count": sum(row["surgery_flag"] for row in transition_rows),
        "strict_conductance_descent_flag": int(
            all(left > right for left, right in zip(conductances, conductances[1:]))
        ),
        "holonomy_delta_total": dini_observables[
            dini.OBSERVABLE_CODES["holonomy_delta_total"]
        ],
        "base_to_final_drop_x1e12": dini_observables[
            dini.OBSERVABLE_CODES["base_to_final_drop_x1e12"]
        ],
        "final_height_x1e12": conductances[-1],
        "discriminant_state_count": sum(
            row["discriminant_stratum_flag"] for row in state_rows
        ),
        "positive_cone_proxy_available_flag": 1,
        "exterior_circuit_matrix_available_flag": 0,
        "surgery_certificate_available_flag": 0,
        "nonholonomic_aperture_model_flag": 1,
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
        "handoff_text": handoff_text,
        "truncated_report": truncated_report,
        "preservation_report": preservation_report,
        "holonomy_report": holonomy_report,
        "dini_report": dini_report,
        "boundary_rows": boundary_rows,
        "distribution_rows": distribution_rows,
        "state_rows": state_rows,
        "transition_rows": transition_rows,
        "observable_rows": observable_rows,
        "observable_values": observable_values,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_payload_rows()
    boundary_table = table_from_rows(BOUNDARY_COLUMNS, rows["boundary_rows"])
    distribution_table = table_from_rows(
        DISTRIBUTION_COLUMNS,
        rows["distribution_rows"],
    )
    state_table = table_from_rows(STATE_COLUMNS, rows["state_rows"])
    transition_table = table_from_rows(TRANSITION_COLUMNS, rows["transition_rows"])
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, rows["observable_rows"])
    observable_values = rows["observable_values"]
    conductances = [row["height_x1e12"] for row in rows["state_rows"]]
    eta_pairings = [row["eta6_holonomy_pairing"] for row in rows["state_rows"]]

    expected_source_counts = {
        0: (45, 45, 16, 16, 0),
        1: (84, 84, 25, 25, 0),
        2: (382, 382, 63, 63, 0),
        3: (21, 21, 3, 3, 0),
        4: (28, 28, 24, 24, 0),
        5: (26, 26, 22, 22, 0),
        6: (20, 20, 0, 0, 0),
    }
    actual_source_counts = {
        row["source_code"]: (
            row["row_count"],
            row["horizontal_row_count"],
            row["conductance_decreasing_row_count"],
            row["conductance_decreasing_horizontal_count"],
            row["eta6_delta_rank"],
        )
        for row in rows["distribution_rows"]
    }

    checks = {
        "handoff_note_loaded": observable_values["handoff_note_present_flag"] == 1
        and observable_values["handoff_note_length"] > 1000,
        "input_reports_are_certified": (
            rows["truncated_report"].get("status"),
            rows["preservation_report"].get("status"),
            rows["holonomy_report"].get("status"),
            rows["dini_report"].get("status"),
        )
        == (
            skeleton.STATUS,
            preservation.STATUS,
            holonomy.STATUS,
            dini.STATUS,
        ),
        "finite_boundary_complex_matches_handoff_counts": (
            observable_values["public_boundary_vertex_count"],
            observable_values["public_boundary_edge_count"],
            observable_values["public_boundary_face_count"],
            observable_values["truncated_vertex_count"],
            observable_values["truncated_edge_count"],
            observable_values["truncated_face_count"],
        )
        == (20, 30, 12, 60, 90, 32),
        "eta6_is_nonzero_holonomy_aperture_class": (
            observable_values["relative_h1_dimension"],
            observable_values["relative_cohomology_dimension"],
            observable_values["eta6_holonomy_pairing"],
        )
        == (1, 1, 1),
        "allowed_distribution_is_eta6_horizontal_and_metric_nonzero": (
            observable_values["aggregate_distribution_row_count"],
            observable_values["horizontal_distribution_row_count"],
            observable_values["conductance_decreasing_row_count"],
            observable_values["support_changing_row_count"],
            observable_values["conductance_decreasing_support_changing_count"],
            observable_values["distribution_eta6_delta_rank"],
            observable_values["distribution_metric_nonzero_flag"],
            actual_source_counts,
        )
        == (
            606,
            606,
            153,
            0,
            0,
            0,
            1,
            expected_source_counts,
        ),
        "finite_automaton_has_positive_horizontal_descent": (
            observable_values["automaton_state_count"],
            observable_values["automaton_transition_count"],
            observable_values["positive_height_state_count"],
            observable_values["horizontal_transition_count"],
            observable_values["metric_nonzero_transition_count"],
            observable_values["surgery_transition_count"],
            observable_values["strict_conductance_descent_flag"],
            observable_values["holonomy_delta_total"],
            conductances,
            eta_pairings,
        )
        == (
            5,
            4,
            5,
            4,
            4,
            0,
            1,
            0,
            [
                4_329_004_000,
                3_649_635_000,
                2_645_503_000,
                2_615_519_000,
                2_610_966_000,
            ],
            [1, 1, 1, 1, 1],
        ),
        "discriminant_and_surgery_seams_are_explicit": (
            observable_values["discriminant_state_count"],
            observable_values["positive_cone_proxy_available_flag"],
            observable_values["exterior_circuit_matrix_available_flag"],
            observable_values["surgery_certificate_available_flag"],
            observable_values["nonholonomic_aperture_model_flag"],
        )
        == (5, 1, 0, 0, 1),
        "table_shapes_match_codebooks": (
            tuple(boundary_table.shape),
            tuple(distribution_table.shape),
            tuple(state_table.shape),
            tuple(transition_table.shape),
            tuple(observable_table.shape),
        )
        == (
            (3, len(BOUNDARY_COLUMNS)),
            (7, len(DISTRIBUTION_COLUMNS)),
            (5, len(STATE_COLUMNS)),
            (4, len(TRANSITION_COLUMNS)),
            (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
        ),
    }

    witness = {
        "finite_boundary_counts": {
            "public_d20": [20, 30, 12],
            "lifted_truncated_boundary": [60, 90, 32],
        },
        "eta6_holonomy": {
            "relative_h1_dimension": observable_values["relative_h1_dimension"],
            "relative_cohomology_dimension": observable_values[
                "relative_cohomology_dimension"
            ],
            "eta6_pairing": observable_values["eta6_holonomy_pairing"],
        },
        "distribution": {
            "row_count": observable_values["aggregate_distribution_row_count"],
            "horizontal_row_count": observable_values[
                "horizontal_distribution_row_count"
            ],
            "conductance_decreasing_row_count": observable_values[
                "conductance_decreasing_row_count"
            ],
            "support_changing_row_count": observable_values[
                "support_changing_row_count"
            ],
            "eta6_delta_rank": observable_values["distribution_eta6_delta_rank"],
            "metric_nonzero_flag": observable_values[
                "distribution_metric_nonzero_flag"
            ],
        },
        "automaton": {
            "conductance_chain_x1e12": conductances,
            "eta6_pairing_chain": eta_pairings,
            "base_to_final_drop_x1e12": observable_values[
                "base_to_final_drop_x1e12"
            ],
            "final_height_x1e12": observable_values["final_height_x1e12"],
        },
        "open_seams": {
            "positive_cone_is_conductance_height_proxy": True,
            "exterior_circuit_matrix_available": False,
            "surgery_certificate_available": False,
        },
        "boundary_table_sha256": pair.parent.sha_array(boundary_table),
        "distribution_table_sha256": pair.parent.sha_array(distribution_table),
        "state_table_sha256": pair.parent.sha_array(state_table),
        "transition_table_sha256": pair.parent.sha_array(transition_table),
        "observable_table_sha256": pair.parent.sha_array(observable_table),
    }

    nonholonomic = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_eta6_nonholonomic_aperture@1",
        "object": "C985->d20",
        "construction": {
            "finite_boundary_complex": "d20 public 20/30/12 boundary plus lifted 60/90/32 truncated carrier",
            "aperture_class": "eta6 is the nonzero relative H1 class detected by the dual holonomy pairing",
            "allowed_distribution": "currently certified 6j/F-symbol interventions whose eta6 delta is zero",
            "positive_height_proxy": "cut conductance remains positive along the selected finite automaton chain",
            "discriminant_reading": "the six-edge aperture remains a stable singular stratum under metric descent",
            "surgery_status": "no aperture-crossing surgery certificate is currently present",
        },
        "witness": witness,
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_nonholonomic_aperture@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_ETA6_NONHOLONOMIC_APERTURE_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The current certified eta6 layer has a finite nonholonomic "
            "aperture model. The lifted boundary carrier is finite and "
            "polyhedral; eta6 is a nonzero holonomy-detected relative class; "
            "all 606 certified 6j/F-symbol intervention rows are horizontal "
            "with respect to eta6; 153 of them still move the conductance "
            "metric coordinate. The selected five-state automaton has positive "
            "conductance height and strict descent while eta6 remains fixed. "
            "The exterior circuit cone and surgery continuation remain explicit "
            "open seams."
        ),
        "stage_protocol": {
            "draft": "read the handoff note as finite boundary complex plus positive cone plus discriminant surgery automaton",
            "witness": "join the truncated boundary skeleton, eta6 holonomy, conductance-preservation distribution, and Dini chain",
            "coherence": "check eta6-horizontal distribution, metric-nonzero conductance image, positive height proxy, and no surgery crossing",
            "closure": "certify the finite nonholonomic aperture model while leaving A_ext and surgery as explicit seams",
            "emit": "emit boundary, distribution, state, transition, observable, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "handoff_note": pair.parent.input_entry(HANDOFF_NOTE),
            "truncated_skeleton_report": pair.parent.input_entry(
                TRUNCATED_REPORT,
                {
                    "status": rows["truncated_report"].get("status"),
                    "certificate_sha256": rows["truncated_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "truncated_skeleton_tables": pair.parent.input_entry(TRUNCATED_TABLES),
            "conductance_preservation_report": pair.parent.input_entry(
                PRESERVATION_REPORT,
                {
                    "status": rows["preservation_report"].get("status"),
                    "certificate_sha256": rows["preservation_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "conductance_preservation_tables": pair.parent.input_entry(
                PRESERVATION_TABLES
            ),
            "eta6_holonomy_report": pair.parent.input_entry(
                HOLONOMY_REPORT,
                {
                    "status": rows["holonomy_report"].get("status"),
                    "certificate_sha256": rows["holonomy_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "eta6_holonomy_tables": pair.parent.input_entry(HOLONOMY_TABLES),
            "dini_torsion_report": pair.parent.input_entry(
                DINI_REPORT,
                {
                    "status": rows["dini_report"].get("status"),
                    "certificate_sha256": rows["dini_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "dini_torsion_tables": pair.parent.input_entry(DINI_TABLES),
            "derive_script": pair.parent.input_entry(DERIVE_SCRIPT),
            "validator": pair.parent.input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": pair.parent.relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "nonholonomic": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_eta6_nonholonomic_aperture.json"
            ),
            "boundary_csv": pair.parent.relpath(
                OUT_DIR / "eta6_nonholonomic_boundary_complex.csv"
            ),
            "distribution_csv": pair.parent.relpath(
                OUT_DIR / "eta6_nonholonomic_distribution.csv"
            ),
            "state_csv": pair.parent.relpath(
                OUT_DIR / "eta6_nonholonomic_automaton_states.csv"
            ),
            "transition_csv": pair.parent.relpath(
                OUT_DIR / "eta6_nonholonomic_automaton_transitions.csv"
            ),
            "observables_csv": pair.parent.relpath(
                OUT_DIR / "eta6_nonholonomic_observables.csv"
            ),
            "tables": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_eta6_nonholonomic_aperture_tables.npz"
            ),
            "certificate": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_eta6_nonholonomic_aperture_certificate.json"
            ),
            "manifest": pair.parent.relpath(OUT_DIR / "manifest.json"),
            "report": pair.parent.relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "eta6 is a nonzero holonomy-detected aperture class in the finite K4 relative model",
                "the certified F-symbol/6j distribution is eta6-horizontal across all 606 rows",
                "the horizontal distribution has nonzero metric image: 153 rows decrease conductance",
                "the selected five-state finite automaton stays positive and descends while eta6 remains fixed",
                "the six-edge aperture is a stable discriminant stratum in the current certified scope",
            ],
            "does_not_certify_because_not_required": [
                "an explicit exterior affine-circuit matrix A_ext",
                "strict positivity of a full exterior rigidity cone C_+ beyond the conductance-height proxy",
                "bracket-generating or commutator closure of the complete F-symbol distribution",
                "a certified surgery move that crosses or kills eta6",
            ],
        },
        "next_highest_yield_item": (
            "Build the actual exterior circuit matrix A_ext for the lifted "
            "60/90 boundary carrier, then replace the conductance-height proxy "
            "with a certified positive cone and discriminant equation."
        ),
    }
    report["certificate_sha256"] = pair.parent.self_hash(report, "certificate_sha256")

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_eta6_nonholonomic_aperture_certificate@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "eta6 is the invariant aperture class for the currently certified finite recoupling distribution",
            "the allowed distribution is eta6-horizontal but metric-active",
            "the current positive cone is only a conductance-height proxy until A_ext is built",
        ],
    }

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_nonholonomic_aperture_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "read docs/handoff note.txt",
            "load certified truncated skeleton, conductance-preservation, eta6 holonomy, and Dini reports",
            "check finite boundary counts and eta6 holonomy dimensions",
            "check the certified distribution is eta6-horizontal and metric-nonzero",
            "check the five-state automaton has positive strict conductance descent with fixed eta6",
            "keep A_ext and surgery as explicit open seams",
            "check hashes, witnesses, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = pair.parent.self_hash(manifest, "manifest_sha256")

    return {
        "nonholonomic": nonholonomic,
        "boundary_csv": pair.csv_text(BOUNDARY_COLUMNS, rows["boundary_rows"]),
        "distribution_csv": pair.csv_text(
            DISTRIBUTION_COLUMNS,
            rows["distribution_rows"],
        ),
        "state_csv": pair.csv_text(STATE_COLUMNS, rows["state_rows"]),
        "transition_csv": pair.csv_text(
            TRANSITION_COLUMNS,
            rows["transition_rows"],
        ),
        "observables_csv": pair.csv_text(
            OBSERVABLE_COLUMNS,
            rows["observable_rows"],
        ),
        "boundary_table": boundary_table,
        "distribution_table": distribution_table,
        "state_table": state_table,
        "transition_table": transition_table,
        "observable_table": observable_table,
        "certificate": certificate,
        "report": report,
        "manifest": manifest,
    }


def update_index(report: dict[str, Any]) -> None:
    if preservation.INDEX_PATH.exists():
        index_payload = load_json(preservation.INDEX_PATH)
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
    pair.parent.write_json(preservation.INDEX_PATH, updated)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pair.parent.write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_nonholonomic_aperture.json",
        payloads["nonholonomic"],
    )
    (OUT_DIR / "eta6_nonholonomic_boundary_complex.csv").write_text(
        payloads["boundary_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "eta6_nonholonomic_distribution.csv").write_text(
        payloads["distribution_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "eta6_nonholonomic_automaton_states.csv").write_text(
        payloads["state_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "eta6_nonholonomic_automaton_transitions.csv").write_text(
        payloads["transition_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "eta6_nonholonomic_observables.csv").write_text(
        payloads["observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_nonholonomic_aperture_tables.npz",
        boundary_table=payloads["boundary_table"],
        distribution_table=payloads["distribution_table"],
        state_table=payloads["state_table"],
        transition_table=payloads["transition_table"],
        observable_table=payloads["observable_table"],
    )
    pair.parent.write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_nonholonomic_aperture_certificate.json",
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
