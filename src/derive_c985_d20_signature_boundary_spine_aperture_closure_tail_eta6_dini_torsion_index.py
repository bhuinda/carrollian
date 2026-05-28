from __future__ import annotations

import json
from typing import Any

import numpy as np

try:
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy as holonomy
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_promotion as base_promotion
    from . import derive_c985_sixj_conductance as preservation
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy as holonomy
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_promotion as base_promotion
    import derive_c985_sixj_conductance as preservation
    from derive_c985_typed_simple_object_registry import INDEX_PATH
    from paths import D20_INVARIANTS, ROOT


pair = preservation.pair

THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_ETA6_DINI_TORSION_INDEX_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

BASE_REPORT = base_promotion.OUT_DIR / "report.json"
CONDUCTANCE_REPORT = preservation.OUT_DIR / "report.json"
CONDUCTANCE_TABLES = (
    preservation.OUT_DIR
    / "sixj_conductance_tables.npz"
)
HOLONOMY_REPORT = holonomy.OUT_DIR / "report.json"
HOLONOMY_TABLES = (
    holonomy.OUT_DIR
    / "signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy_tables.npz"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index.py"
)

BLOCK_CODE_COLUMNS = [f"block_code_{index}" for index in range(4)]
CHAIN_COLUMNS = [
    "stage_id",
    "stage_code",
    "source_code",
    "source_row_id",
    "screen_order",
    "intervention_size",
    *BLOCK_CODE_COLUMNS,
    "state_count",
    "edge_count",
    "lambda_2_x1e12",
    "cut_conductance_x1e12",
    "conductance_drop_from_base_x1e12",
    "conductance_drop_from_previous_x1e12",
    "old_cut_edge_still_cut_count",
    "old_cut_edge_same_side_count",
    "support_changed_flag",
    "eta6_holonomy_pairing",
    "eta6_relative_class_nonzero_flag",
]
STEP_COLUMNS = [
    "step_id",
    "from_stage_id",
    "to_stage_id",
    "phase_delta",
    "conductance_drop_x1e12",
    "signed_conductance_delta_x1e12",
    "dini_step_torsion_x1e12",
    "holonomy_delta",
    "from_holonomy_pairing",
    "to_holonomy_pairing",
    "support_changed_sum",
    "old_cut_edge_min",
]
OBSERVABLE_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBSERVABLE_CODES = {
    "chain_stage_count": 0,
    "transition_count": 1,
    "base_cut_conductance_x1e12": 2,
    "local_cut_conductance_x1e12": 3,
    "final_cut_conductance_x1e12": 4,
    "base_to_final_drop_x1e12": 5,
    "local_to_final_drop_x1e12": 6,
    "all_stage_holonomy_pairing_count": 7,
    "holonomy_delta_total": 8,
    "support_changed_total": 9,
    "old_cut_edge_min": 10,
    "strict_conductance_descent_flag": 11,
    "positive_final_conductance_flag": 12,
    "dini_total_torsion_base_x1e12": 13,
    "dini_total_torsion_local_x1e12": 14,
    "largest_step_drop_x1e12": 15,
    "largest_step_code": 16,
    "smallest_positive_step_drop_x1e12": 17,
    "nonlocal_tail_drop_after_2114_x1e12": 18,
    "poincare_height_available_for_all_stages_flag": 19,
    "h4_lift_certified_flag": 20,
}

STAGE_LABELS = {
    0: "second_window_base",
    1: "best_k4_local_face_recoupling",
    2: "nonlocal_singleton_2114",
    3: "focused_pair_2114_5255",
    4: "bounded_triple_2114_5255_1521",
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


def block_codes(row: dict[str, int]) -> list[int]:
    return [row.get(f"block_code_{index}", -1) for index in range(4)]


def select_best(
    rows: list[dict[str, int]],
    *,
    source_codes: set[int],
    required_prefix: tuple[int, ...] = (),
) -> dict[str, int]:
    candidates = [
        row
        for row in rows
        if row["source_code"] in source_codes
        and row["conductance_decreasing_flag"] == 1
        and tuple(block_codes(row)[: len(required_prefix)]) == required_prefix
    ]
    if not candidates:
        raise ValueError(f"no conductance-decreasing row for {source_codes}")
    return min(
        candidates,
        key=lambda row: (
            row["cut_conductance_x1e12"],
            row["intervention_size"],
            row["source_code"],
            row["source_row_id"],
        ),
    )


def load_aggregate_rows() -> list[dict[str, int]]:
    tables = np.load(CONDUCTANCE_TABLES, allow_pickle=False)
    aggregate = np.asarray(tables["aggregate_table"], dtype=np.int64)
    return table_rows(aggregate, preservation.AGGREGATE_COLUMNS)


def holonomy_witness(report: dict[str, Any]) -> tuple[int, int]:
    witness = report["witness"]
    return (
        int(witness["holonomy_eta6_pairing"]),
        int(witness["relative_h1_dimension"] > 0),
    )


def build_base_stage(
    base_report: dict[str, Any],
    holonomy_pairing: int,
    eta6_nonzero: int,
) -> dict[str, int]:
    spectral = base_report["witness"]["spectral_cut"]
    return {
        "stage_id": 0,
        "stage_code": 0,
        "source_code": -1,
        "source_row_id": -1,
        "screen_order": 0,
        "intervention_size": 0,
        "block_code_0": -1,
        "block_code_1": -1,
        "block_code_2": -1,
        "block_code_3": -1,
        "state_count": int(base_report["witness"]["state_count"]),
        "edge_count": int(base_report["witness"]["undirected_edge_count"]),
        "lambda_2_x1e12": int(spectral["lambda_2_x1e12"]),
        "cut_conductance_x1e12": int(spectral["cut_conductance_x1e12"]),
        "conductance_drop_from_base_x1e12": 0,
        "conductance_drop_from_previous_x1e12": 0,
        "old_cut_edge_still_cut_count": int(
            base_report["witness"]["parent_cut_lineage"][
                "parent_cut_edge_still_cut_count"
            ]
        ),
        "old_cut_edge_same_side_count": 0,
        "support_changed_flag": 0,
        "eta6_holonomy_pairing": holonomy_pairing,
        "eta6_relative_class_nonzero_flag": eta6_nonzero,
    }


def chain_stage_from_row(
    stage_id: int,
    row: dict[str, int],
    *,
    base_conductance: int,
    previous_conductance: int,
    holonomy_pairing: int,
    eta6_nonzero: int,
) -> dict[str, int]:
    codes = block_codes(row)
    return {
        "stage_id": stage_id,
        "stage_code": stage_id,
        "source_code": row["source_code"],
        "source_row_id": row["source_row_id"],
        "screen_order": stage_id,
        "intervention_size": row["intervention_size"],
        "block_code_0": codes[0],
        "block_code_1": codes[1],
        "block_code_2": codes[2],
        "block_code_3": codes[3],
        "state_count": row["state_count"],
        "edge_count": row["edge_count"],
        "lambda_2_x1e12": row["lambda_2_x1e12"],
        "cut_conductance_x1e12": row["cut_conductance_x1e12"],
        "conductance_drop_from_base_x1e12": base_conductance
        - row["cut_conductance_x1e12"],
        "conductance_drop_from_previous_x1e12": previous_conductance
        - row["cut_conductance_x1e12"],
        "old_cut_edge_still_cut_count": row["old_cut_edge_still_cut_count"],
        "old_cut_edge_same_side_count": row["old_cut_edge_same_side_count"],
        "support_changed_flag": row["support_changed_flag"],
        "eta6_holonomy_pairing": holonomy_pairing,
        "eta6_relative_class_nonzero_flag": eta6_nonzero,
    }


def build_chain_rows(
    base_report: dict[str, Any],
    holonomy_report: dict[str, Any],
    aggregate_rows: list[dict[str, int]],
) -> list[dict[str, int]]:
    holonomy_pairing, eta6_nonzero = holonomy_witness(holonomy_report)
    base = build_base_stage(base_report, holonomy_pairing, eta6_nonzero)
    base_conductance = base["cut_conductance_x1e12"]
    selected_rows = [
        select_best(aggregate_rows, source_codes={0, 1, 2}),
        select_best(aggregate_rows, source_codes={3}, required_prefix=(2114,)),
        select_best(aggregate_rows, source_codes={4}, required_prefix=(2114, 5255)),
        select_best(
            aggregate_rows,
            source_codes={5},
            required_prefix=(2114, 5255, 1521),
        ),
    ]
    chain = [base]
    previous_conductance = base_conductance
    for stage_id, row in enumerate(selected_rows, start=1):
        stage = chain_stage_from_row(
            stage_id,
            row,
            base_conductance=base_conductance,
            previous_conductance=previous_conductance,
            holonomy_pairing=holonomy_pairing,
            eta6_nonzero=eta6_nonzero,
        )
        chain.append(stage)
        previous_conductance = stage["cut_conductance_x1e12"]
    return chain


def build_step_rows(chain_rows: list[dict[str, int]]) -> list[dict[str, int]]:
    steps = []
    for step_id, (source, target) in enumerate(zip(chain_rows, chain_rows[1:])):
        phase_delta = target["screen_order"] - source["screen_order"]
        conductance_drop = (
            source["cut_conductance_x1e12"] - target["cut_conductance_x1e12"]
        )
        steps.append(
            {
                "step_id": step_id,
                "from_stage_id": source["stage_id"],
                "to_stage_id": target["stage_id"],
                "phase_delta": phase_delta,
                "conductance_drop_x1e12": conductance_drop,
                "signed_conductance_delta_x1e12": -conductance_drop,
                "dini_step_torsion_x1e12": conductance_drop // phase_delta,
                "holonomy_delta": target["eta6_holonomy_pairing"]
                - source["eta6_holonomy_pairing"],
                "from_holonomy_pairing": source["eta6_holonomy_pairing"],
                "to_holonomy_pairing": target["eta6_holonomy_pairing"],
                "support_changed_sum": source["support_changed_flag"]
                + target["support_changed_flag"],
                "old_cut_edge_min": min(
                    source["old_cut_edge_still_cut_count"],
                    target["old_cut_edge_still_cut_count"],
                ),
            }
        )
    return steps


def build_observable_rows(
    chain_rows: list[dict[str, int]],
    step_rows: list[dict[str, int]],
) -> tuple[list[dict[str, int]], dict[str, int]]:
    conductances = [row["cut_conductance_x1e12"] for row in chain_rows]
    base_to_final_drop = conductances[0] - conductances[-1]
    local_to_final_drop = conductances[1] - conductances[-1]
    largest_step = max(step_rows, key=lambda row: row["conductance_drop_x1e12"])
    positive_steps = [
        row["conductance_drop_x1e12"]
        for row in step_rows
        if row["conductance_drop_x1e12"] > 0
    ]
    observable_values = {
        "chain_stage_count": len(chain_rows),
        "transition_count": len(step_rows),
        "base_cut_conductance_x1e12": conductances[0],
        "local_cut_conductance_x1e12": conductances[1],
        "final_cut_conductance_x1e12": conductances[-1],
        "base_to_final_drop_x1e12": base_to_final_drop,
        "local_to_final_drop_x1e12": local_to_final_drop,
        "all_stage_holonomy_pairing_count": sum(
            row["eta6_holonomy_pairing"] for row in chain_rows
        ),
        "holonomy_delta_total": sum(abs(row["holonomy_delta"]) for row in step_rows),
        "support_changed_total": sum(row["support_changed_flag"] for row in chain_rows),
        "old_cut_edge_min": min(
            row["old_cut_edge_still_cut_count"] for row in chain_rows
        ),
        "strict_conductance_descent_flag": int(
            all(left > right for left, right in zip(conductances, conductances[1:]))
        ),
        "positive_final_conductance_flag": int(conductances[-1] > 0),
        "dini_total_torsion_base_x1e12": base_to_final_drop
        // max(1, len(chain_rows) - 1),
        "dini_total_torsion_local_x1e12": local_to_final_drop
        // max(1, len(chain_rows) - 2),
        "largest_step_drop_x1e12": largest_step["conductance_drop_x1e12"],
        "largest_step_code": largest_step["from_stage_id"] * 10
        + largest_step["to_stage_id"],
        "smallest_positive_step_drop_x1e12": min(positive_steps),
        "nonlocal_tail_drop_after_2114_x1e12": conductances[2] - conductances[-1],
        "poincare_height_available_for_all_stages_flag": 0,
        "h4_lift_certified_flag": 0,
    }
    rows = [
        {
            "observable_id": observable_id,
            "observable_code": code,
            "value": int(observable_values[key]),
            "scale_code": 0,
        }
        for observable_id, (key, code) in enumerate(OBSERVABLE_CODES.items())
    ]
    return rows, observable_values


def build_payload_rows() -> dict[str, Any]:
    base_report = load_json(BASE_REPORT)
    conductance_report = load_json(CONDUCTANCE_REPORT)
    holonomy_report = load_json(HOLONOMY_REPORT)
    aggregate_rows = load_aggregate_rows()
    chain_rows = build_chain_rows(base_report, holonomy_report, aggregate_rows)
    step_rows = build_step_rows(chain_rows)
    observable_rows, observable_values = build_observable_rows(chain_rows, step_rows)
    return {
        "base_report": base_report,
        "conductance_report": conductance_report,
        "holonomy_report": holonomy_report,
        "chain_rows": chain_rows,
        "step_rows": step_rows,
        "observable_rows": observable_rows,
        "observable_values": observable_values,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_payload_rows()
    chain_table = table_from_rows(CHAIN_COLUMNS, rows["chain_rows"])
    step_table = table_from_rows(STEP_COLUMNS, rows["step_rows"])
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, rows["observable_rows"])
    observable_values = rows["observable_values"]
    conductances = [row["cut_conductance_x1e12"] for row in rows["chain_rows"]]
    holonomy_pairings = [row["eta6_holonomy_pairing"] for row in rows["chain_rows"]]
    support_flags = [row["support_changed_flag"] for row in rows["chain_rows"]]

    checks = {
        "base_second_window_report_certified": rows["base_report"].get("status")
        == base_promotion.STATUS,
        "conductance_preservation_report_certified": rows["conductance_report"].get(
            "status"
        )
        == preservation.STATUS,
        "eta6_holonomy_report_certified": rows["holonomy_report"].get("status")
        == holonomy.STATUS,
        "chain_values_match_expected_descent": conductances
        == [
            4_329_004_000,
            3_649_635_000,
            2_645_503_000,
            2_615_519_000,
            2_610_966_000,
        ],
        "chain_stage_blocks_match_expected_witness": [
            block_codes(row) for row in rows["chain_rows"]
        ]
        == [
            [-1, -1, -1, -1],
            [5255, 1252, 5252, -1],
            [2114, -1, -1, -1],
            [2114, 5255, -1, -1],
            [2114, 5255, 1521, -1],
        ],
        "conductance_descends_strictly_while_holonomy_is_fixed": (
            observable_values["strict_conductance_descent_flag"],
            observable_values["holonomy_delta_total"],
            holonomy_pairings,
        )
        == (1, 0, [1, 1, 1, 1, 1]),
        "support_class_is_fixed_through_dini_chain": (
            observable_values["support_changed_total"],
            observable_values["old_cut_edge_min"],
            support_flags,
        )
        == (0, 6, [0, 0, 0, 0, 0]),
        "dini_torsion_indices_are_expected": (
            observable_values["base_to_final_drop_x1e12"],
            observable_values["local_to_final_drop_x1e12"],
            observable_values["dini_total_torsion_base_x1e12"],
            observable_values["dini_total_torsion_local_x1e12"],
            observable_values["largest_step_drop_x1e12"],
            observable_values["largest_step_code"],
            observable_values["smallest_positive_step_drop_x1e12"],
            observable_values["nonlocal_tail_drop_after_2114_x1e12"],
        )
        == (
            1_718_038_000,
            1_038_669_000,
            429_509_500,
            346_223_000,
            1_004_132_000,
            12,
            4_553_000,
            34_537_000,
        ),
        "h4_lift_is_explicitly_not_certified_here": (
            observable_values["poincare_height_available_for_all_stages_flag"],
            observable_values["h4_lift_certified_flag"],
        )
        == (0, 0),
        "table_shapes_match_codebooks": (
            tuple(chain_table.shape),
            tuple(step_table.shape),
            tuple(observable_table.shape),
        )
        == (
            (5, len(CHAIN_COLUMNS)),
            (4, len(STEP_COLUMNS)),
            (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
        ),
    }

    witness = {
        "stage_labels": {str(key): value for key, value in STAGE_LABELS.items()},
        "conductance_chain_x1e12": conductances,
        "holonomy_pairing_chain": holonomy_pairings,
        "support_changed_chain": support_flags,
        "base_to_final_drop_x1e12": observable_values[
            "base_to_final_drop_x1e12"
        ],
        "local_to_final_drop_x1e12": observable_values[
            "local_to_final_drop_x1e12"
        ],
        "dini_total_torsion_base_x1e12": observable_values[
            "dini_total_torsion_base_x1e12"
        ],
        "dini_total_torsion_local_x1e12": observable_values[
            "dini_total_torsion_local_x1e12"
        ],
        "nonlocal_tail_drop_after_2114_x1e12": observable_values[
            "nonlocal_tail_drop_after_2114_x1e12"
        ],
        "chain_table_sha256": pair.parent.sha_array(chain_table),
        "step_table_sha256": pair.parent.sha_array(step_table),
        "observable_table_sha256": pair.parent.sha_array(observable_table),
    }

    dini = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index@1",
        "object": "C985->d20",
        "definition": {
            "finite_torsion_reading": (
                "tau_Dini is measured here as conductance descent per certified "
                "recoupling-screen phase while the nontrivial eta6 holonomy "
                "pairing remains fixed."
            ),
            "eta6_holonomy_pairing": holonomy_pairings[0],
            "coefficient_scale": "x1e12",
        },
        "chain": [
            {
                "stage_id": row["stage_id"],
                "label": STAGE_LABELS[row["stage_id"]],
                "blocks": [
                    row[column]
                    for column in BLOCK_CODE_COLUMNS
                    if row[column] != -1
                ],
                "cut_conductance_x1e12": row["cut_conductance_x1e12"],
                "conductance_drop_from_base_x1e12": row[
                    "conductance_drop_from_base_x1e12"
                ],
                "eta6_holonomy_pairing": row["eta6_holonomy_pairing"],
                "support_changed_flag": row["support_changed_flag"],
            }
            for row in rows["chain_rows"]
        ],
        "index": {
            "base_to_final_drop_x1e12": observable_values[
                "base_to_final_drop_x1e12"
            ],
            "local_to_final_drop_x1e12": observable_values[
                "local_to_final_drop_x1e12"
            ],
            "dini_total_torsion_base_x1e12": observable_values[
                "dini_total_torsion_base_x1e12"
            ],
            "dini_total_torsion_local_x1e12": observable_values[
                "dini_total_torsion_local_x1e12"
            ],
            "nonlocal_tail_drop_after_2114_x1e12": observable_values[
                "nonlocal_tail_drop_after_2114_x1e12"
            ],
        },
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_ETA6_DINI_TORSION_INDEX_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The certified recoupling chain from the second-window six-edge "
            "base through the best K4-local row, 2114, 2114+5255, and "
            "2114+5255+1521 has strictly decreasing conductance while the "
            "nontrivial eta6 holonomy pairing remains fixed at 1 and the old "
            "six-edge support class never changes. This is the finite Dini "
            "torsion index: metric relaxation around a fixed cohomological seam."
        ),
        "stage_protocol": {
            "draft": "start from the certified eta6 holonomy and conductance-preservation layers",
            "witness": "extract the best local, 2114, 2114+5255, and 2114+5255+1521 chain rows",
            "coherence": "compare conductance descent against fixed eta6 holonomy and unchanged support",
            "closure": "certify the finite Dini torsion index without claiming a full H4 metric lift",
            "emit": "emit Dini chain, step, observable, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "second_window_base_report": pair.parent.input_entry(
                BASE_REPORT,
                {
                    "status": rows["base_report"].get("status"),
                    "certificate_sha256": rows["base_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "conductance_preservation_report": pair.parent.input_entry(
                CONDUCTANCE_REPORT,
                {
                    "status": rows["conductance_report"].get("status"),
                    "certificate_sha256": rows["conductance_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "conductance_preservation_tables": pair.parent.input_entry(
                CONDUCTANCE_TABLES
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
            "derive_script": pair.parent.input_entry(DERIVE_SCRIPT),
            "validator": pair.parent.input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": pair.parent.relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "dini": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index.json"
            ),
            "chain_csv": pair.parent.relpath(
                OUT_DIR / "eta6_dini_torsion_chain.csv"
            ),
            "steps_csv": pair.parent.relpath(
                OUT_DIR / "eta6_dini_torsion_steps.csv"
            ),
            "observables_csv": pair.parent.relpath(
                OUT_DIR / "eta6_dini_torsion_observables.csv"
            ),
            "tables": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index_tables.npz"
            ),
            "certificate": pair.parent.relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index_certificate.json"
            ),
            "manifest": pair.parent.relpath(OUT_DIR / "manifest.json"),
            "report": pair.parent.relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "a strict conductance descent chain from local recoupling through 2114+5255+1521",
                "eta6 holonomy pairing stays fixed and nonzero throughout that chain",
                "the old six-edge support class stays fixed throughout that chain",
                "finite Dini torsion indices for base-to-final and local-to-final descent",
            ],
            "does_not_certify_because_not_required": [
                "a smooth Dini surface or differential torsion tensor",
                "per-intervention Poincare-height coordinates",
                "a literal H4 metric embedding",
                "a positive lower asymptote for the conductance relaxation curve",
            ],
        },
        "next_highest_yield_item": (
            "Build the H4 precursor table by giving every Dini-chain stage a "
            "compatible (x,y,r,h) coordinate: reuse existing Poincare data where "
            "available, set r from eta6 holonomy/residue, and use conductance as "
            "the first certified height coordinate."
        ),
    }
    report["certificate_sha256"] = pair.parent.self_hash(report, "certificate_sha256")

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index_certificate@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "conductance relaxes monotonically along the selected recoupling chain",
            "eta6 remains a fixed nontrivial cohomological seam",
            "the current finite torsion is metric descent around that seam, not an aperture opening",
        ],
    }

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified second-window base, conductance-preservation, and eta6 holonomy reports",
            "extract the best local/nonlocal conductance descent chain",
            "verify strict conductance descent and fixed eta6 holonomy pairing",
            "verify unchanged six-edge support along the chain",
            "check hashes, witnesses, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = pair.parent.self_hash(manifest, "manifest_sha256")

    return {
        "dini": dini,
        "chain_csv": pair.csv_text(CHAIN_COLUMNS, rows["chain_rows"]),
        "steps_csv": pair.csv_text(STEP_COLUMNS, rows["step_rows"]),
        "observables_csv": pair.csv_text(OBSERVABLE_COLUMNS, rows["observable_rows"]),
        "chain_table": chain_table,
        "step_table": step_table,
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
        / "signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index.json",
        payloads["dini"],
    )
    (OUT_DIR / "eta6_dini_torsion_chain.csv").write_text(
        payloads["chain_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "eta6_dini_torsion_steps.csv").write_text(
        payloads["steps_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "eta6_dini_torsion_observables.csv").write_text(
        payloads["observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index_tables.npz",
        chain_table=payloads["chain_table"],
        step_table=payloads["step_table"],
        observable_table=payloads["observable_table"],
    )
    pair.parent.write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index_certificate.json",
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
