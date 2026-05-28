from __future__ import annotations

import json
from typing import Any

import numpy as np

try:
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_borromean_hypergraph_screen as borromean
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen as neighborhood
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_triple_screen as triple2114
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen as nonlocal_screen
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction as pair_obstruction
    from . import derive_c985_sixj_tetra_closure as closure
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction as triple_face
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_borromean_hypergraph_screen as borromean
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen as neighborhood
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_triple_screen as triple2114
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen as nonlocal_screen
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction as pair_obstruction
    import derive_c985_sixj_tetra_closure as closure
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction as triple_face
    from derive_c985_typed_simple_object_registry import INDEX_PATH
    from paths import D20_INVARIANTS, ROOT


pair = nonlocal_screen.pair

THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_conductance_decreasing_aperture_preservation"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_SIXJ_CONDUCTANCE_DECREASING_APERTURE_PRESERVATION_CERTIFIED"
)
OUT_DIR_NAME = "c985_sixj_conductance"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / OUT_DIR_NAME

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_sixj_conductance.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_sixj_conductance.py"
)

AGGREGATE_COLUMNS = [
    "aggregate_row_id",
    "source_code",
    "source_row_id",
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
    "conductance_decreasing_flag",
    "support_changed_flag",
    "aperture_preserved_flag",
    "selected_best_flag",
]
SOURCE_SUMMARY_COLUMNS = [
    "source_code",
    "row_count",
    "conductance_decreasing_count",
    "support_changing_count",
    "aperture_preserved_count",
    "min_cut_conductance_x1e12",
    "best_decreasing_source_row_id",
    "best_decreasing_cut_conductance_x1e12",
    "best_decreasing_reduction_x1e12",
    "best_decreasing_old_cut_edge_still_cut_count",
]
OBSERVABLE_COLUMNS = ["observable_id", "observable_code", "value", "scale_code"]
OBSERVABLE_CODES = {
    "source_count": 0,
    "aggregate_row_count": 1,
    "conductance_decreasing_row_count": 2,
    "nonconductance_decreasing_row_count": 3,
    "support_changing_row_count": 4,
    "conductance_decreasing_support_changing_count": 5,
    "all_rows_aperture_preserved_count": 6,
    "min_decreasing_old_cut_edge_still_cut_count": 7,
    "max_decreasing_old_cut_edge_same_side_count": 8,
    "best_source_code": 9,
    "best_source_row_id": 10,
    "best_intervention_size": 11,
    "best_block_code_0": 12,
    "best_block_code_1": 13,
    "best_block_code_2": 14,
    "best_state_count": 15,
    "best_edge_count": 16,
    "best_cut_edge_count": 17,
    "best_old_cut_edge_still_cut_count": 18,
    "best_lambda_2_x1e12": 19,
    "best_cut_conductance_x1e12": 20,
    "best_conductance_reduction_x1e12": 21,
    "borromean_hyperedge_count": 22,
    "borromean_conductance_decreasing_count": 23,
}


SOURCE_DEFS = [
    {
        "source_code": 0,
        "name": "k4_pair_recoupling",
        "module": pair_obstruction,
        "report": pair_obstruction.OUT_DIR / "report.json",
        "tables": pair_obstruction.OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction_tables.npz",
        "table_key": "intervention_table",
        "columns": pair_obstruction.INTERVENTION_COLUMNS,
        "status": pair_obstruction.STATUS,
    },
    {
        "source_code": 1,
        "name": "k4_triple_face_recoupling",
        "module": triple_face,
        "report": triple_face.OUT_DIR / "report.json",
        "tables": triple_face.OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction_tables.npz",
        "table_key": "triple_table",
        "columns": triple_face.TRIPLE_COLUMNS,
        "status": triple_face.STATUS,
    },
    {
        "source_code": 2,
        "name": "k4_tetrahedral_closure",
        "module": closure,
        "report": closure.OUT_DIR / "report.json",
        "tables": closure.OUT_DIR
        / "sixj_tetra_closure_tables.npz",
        "table_key": "intervention_table",
        "columns": closure.INTERVENTION_COLUMNS,
        "status": closure.STATUS,
    },
    {
        "source_code": 3,
        "name": "nonlocal_top_six_fsymbol_screen",
        "module": nonlocal_screen,
        "report": nonlocal_screen.OUT_DIR / "report.json",
        "tables": nonlocal_screen.OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen_tables.npz",
        "table_key": "intervention_table",
        "columns": nonlocal_screen.INTERVENTION_COLUMNS,
        "status": nonlocal_screen.STATUS,
    },
    {
        "source_code": 4,
        "name": "nonlocal_2114_neighborhood",
        "module": neighborhood,
        "report": neighborhood.OUT_DIR / "report.json",
        "tables": neighborhood.OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen_tables.npz",
        "table_key": "intervention_table",
        "columns": neighborhood.INTERVENTION_COLUMNS,
        "status": neighborhood.STATUS,
    },
    {
        "source_code": 5,
        "name": "nonlocal_2114_triple_screen",
        "module": triple2114,
        "report": triple2114.OUT_DIR / "report.json",
        "tables": triple2114.OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_triple_screen_tables.npz",
        "table_key": "triple_table",
        "columns": triple2114.TRIPLE_COLUMNS,
        "status": triple2114.STATUS,
    },
    {
        "source_code": 6,
        "name": "borromean_top_six_hypergraph",
        "module": borromean,
        "report": borromean.OUT_DIR / "report.json",
        "tables": borromean.OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_borromean_hypergraph_screen_tables.npz",
        "table_key": "hyperedge_table",
        "columns": borromean.HYPEREDGE_COLUMNS,
        "status": borromean.STATUS,
    },
]


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


def source_row_id(row: dict[str, int]) -> int:
    for key in ("intervention_id", "triple_id", "hyperedge_id"):
        if key in row:
            return row[key]
    raise ValueError(f"row has no source id: {row}")


def source_intervention_size(row: dict[str, int]) -> int:
    if "intervention_size" in row:
        return row["intervention_size"]
    if "block_code_c" in row:
        return 3
    if row.get("block_code_b", -1) == -1:
        return 1
    return 2


def source_block_codes(row: dict[str, int]) -> list[int]:
    if "block_code_0" in row:
        return [row.get(f"block_code_{index}", -1) for index in range(9)]
    codes = [row.get("block_code_a", -1), row.get("block_code_b", -1)]
    if "block_code_c" in row:
        codes.append(row["block_code_c"])
    return codes + [-1] * (9 - len(codes))


def normalize_row(
    aggregate_row_id: int,
    source_code: int,
    row: dict[str, int],
) -> dict[str, int]:
    block_codes = source_block_codes(row)
    conductance_decreasing = int(row["conductance_reduction_x1e12"] > 0)
    aperture_preserved = int(
        row["old_cut_edge_still_cut_count"] == 6
        and row["old_cut_edge_same_side_count"] == 0
        and row["support_changed_flag"] == 0
    )
    return {
        "aggregate_row_id": aggregate_row_id,
        "source_code": source_code,
        "source_row_id": source_row_id(row),
        "intervention_size": source_intervention_size(row),
        **{f"block_code_{index}": block_codes[index] for index in range(9)},
        "state_count": row["state_count"],
        "new_state_count": row["new_state_count"],
        "edge_count": row["edge_count"],
        "new_edge_count": row["new_edge_count"],
        "cut_edge_count": row["cut_edge_count"],
        "old_cut_edge_still_cut_count": row["old_cut_edge_still_cut_count"],
        "old_cut_edge_same_side_count": row["old_cut_edge_same_side_count"],
        "promoted_cut_edge_count": row["promoted_cut_edge_count"],
        "promoted_only_cut_edge_count": row["promoted_only_cut_edge_count"],
        "lambda_2_x1e12": row["lambda_2_x1e12"],
        "cut_conductance_x1e12": row["cut_conductance_x1e12"],
        "conductance_reduction_x1e12": row["conductance_reduction_x1e12"],
        "conductance_decreasing_flag": conductance_decreasing,
        "support_changed_flag": row["support_changed_flag"],
        "aperture_preserved_flag": aperture_preserved,
        "selected_best_flag": row.get("selected_best_flag", 0),
    }


def source_summary_row(source_code: int, rows: list[dict[str, int]]) -> dict[str, int]:
    decreasing = [row for row in rows if row["conductance_decreasing_flag"] == 1]
    best = (
        min(
            decreasing,
            key=lambda row: (
                row["cut_conductance_x1e12"],
                -row["lambda_2_x1e12"],
                row["source_row_id"],
            ),
        )
        if decreasing
        else None
    )
    return {
        "source_code": source_code,
        "row_count": len(rows),
        "conductance_decreasing_count": len(decreasing),
        "support_changing_count": sum(row["support_changed_flag"] for row in rows),
        "aperture_preserved_count": sum(
            row["aperture_preserved_flag"] for row in rows
        ),
        "min_cut_conductance_x1e12": min(
            row["cut_conductance_x1e12"] for row in rows
        ),
        "best_decreasing_source_row_id": best["source_row_id"] if best else -1,
        "best_decreasing_cut_conductance_x1e12": best[
            "cut_conductance_x1e12"
        ]
        if best
        else -1,
        "best_decreasing_reduction_x1e12": best["conductance_reduction_x1e12"]
        if best
        else -1,
        "best_decreasing_old_cut_edge_still_cut_count": best[
            "old_cut_edge_still_cut_count"
        ]
        if best
        else -1,
    }


def build_payload_rows() -> dict[str, Any]:
    source_reports: dict[int, dict[str, Any]] = {}
    aggregate_rows: list[dict[str, int]] = []
    source_summaries: list[dict[str, int]] = []

    for source in SOURCE_DEFS:
        source_code = source["source_code"]
        report = load_json(source["report"])
        source_reports[source_code] = report
        table = np.asarray(
            np.load(source["tables"], allow_pickle=False)[source["table_key"]],
            dtype=np.int64,
        )
        source_rows = table_rows(table, source["columns"])
        normalized = [
            normalize_row(len(aggregate_rows) + offset, source_code, row)
            for offset, row in enumerate(source_rows)
        ]
        aggregate_rows.extend(normalized)
        source_summaries.append(source_summary_row(source_code, normalized))

    decreasing_rows = [
        row for row in aggregate_rows if row["conductance_decreasing_flag"] == 1
    ]
    best = min(
        decreasing_rows,
        key=lambda row: (
            row["cut_conductance_x1e12"],
            -row["lambda_2_x1e12"],
            row["source_code"],
            row["source_row_id"],
        ),
    )
    borromean_rows = [
        row for row in aggregate_rows if row["source_code"] == 6
    ]
    observable_values = {
        "source_count": len(SOURCE_DEFS),
        "aggregate_row_count": len(aggregate_rows),
        "conductance_decreasing_row_count": len(decreasing_rows),
        "nonconductance_decreasing_row_count": len(aggregate_rows)
        - len(decreasing_rows),
        "support_changing_row_count": sum(
            row["support_changed_flag"] for row in aggregate_rows
        ),
        "conductance_decreasing_support_changing_count": sum(
            row["support_changed_flag"] for row in decreasing_rows
        ),
        "all_rows_aperture_preserved_count": sum(
            row["aperture_preserved_flag"] for row in aggregate_rows
        ),
        "min_decreasing_old_cut_edge_still_cut_count": min(
            row["old_cut_edge_still_cut_count"] for row in decreasing_rows
        ),
        "max_decreasing_old_cut_edge_same_side_count": max(
            row["old_cut_edge_same_side_count"] for row in decreasing_rows
        ),
        "best_source_code": best["source_code"],
        "best_source_row_id": best["source_row_id"],
        "best_intervention_size": best["intervention_size"],
        "best_block_code_0": best["block_code_0"],
        "best_block_code_1": best["block_code_1"],
        "best_block_code_2": best["block_code_2"],
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
        "borromean_hyperedge_count": len(borromean_rows),
        "borromean_conductance_decreasing_count": sum(
            row["conductance_decreasing_flag"] for row in borromean_rows
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
        "source_reports": source_reports,
        "aggregate_rows": aggregate_rows,
        "source_summaries": source_summaries,
        "observable_rows": observable_rows,
        "observable_values": observable_values,
        "best": best,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_payload_rows()
    aggregate_table = table_from_rows(AGGREGATE_COLUMNS, rows["aggregate_rows"])
    source_summary_table = table_from_rows(
        SOURCE_SUMMARY_COLUMNS,
        rows["source_summaries"],
    )
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, rows["observable_rows"])
    observable_values = rows["observable_values"]
    best = rows["best"]

    source_counts = {
        summary["source_code"]: (
            summary["row_count"],
            summary["conductance_decreasing_count"],
            summary["support_changing_count"],
        )
        for summary in rows["source_summaries"]
    }
    source_statuses = {
        source["source_code"]: rows["source_reports"][source["source_code"]].get(
            "status"
        )
        for source in SOURCE_DEFS
    }

    checks = {
        "all_source_reports_certified": all(
            source_statuses[source["source_code"]] == source["status"]
            for source in SOURCE_DEFS
        ),
        "aggregate_scope_matches_certified_fsymbol_rows": (
            observable_values["source_count"],
            observable_values["aggregate_row_count"],
            source_counts,
        )
        == (
            7,
            606,
            {
                0: (45, 16, 0),
                1: (84, 25, 0),
                2: (382, 63, 0),
                3: (21, 3, 0),
                4: (28, 24, 0),
                5: (26, 22, 0),
                6: (20, 0, 0),
            },
        ),
        "all_certified_fsymbol_rows_preserve_six_edge_aperture": (
            observable_values["support_changing_row_count"],
            observable_values["all_rows_aperture_preserved_count"],
        )
        == (0, 606),
        "all_conductance_decreasing_rows_preserve_six_edge_aperture": (
            observable_values["conductance_decreasing_row_count"],
            observable_values["conductance_decreasing_support_changing_count"],
            observable_values["min_decreasing_old_cut_edge_still_cut_count"],
            observable_values["max_decreasing_old_cut_edge_same_side_count"],
        )
        == (153, 0, 6, 0),
        "best_decreasing_intervention_is_2114_5255_1521": (
            observable_values["best_source_code"],
            observable_values["best_source_row_id"],
            observable_values["best_intervention_size"],
            observable_values["best_block_code_0"],
            observable_values["best_block_code_1"],
            observable_values["best_block_code_2"],
            observable_values["best_state_count"],
            observable_values["best_edge_count"],
            observable_values["best_cut_edge_count"],
            observable_values["best_old_cut_edge_still_cut_count"],
            observable_values["best_cut_conductance_x1e12"],
            observable_values["best_conductance_reduction_x1e12"],
        )
        == (5, 10, 3, 2114, 5255, 1521, 957, 3_063, 6, 6, 2_610_966_000, 1_718_038_000),
        "borromean_top_six_hyperedges_are_not_conductance_decreasing": (
            observable_values["borromean_hyperedge_count"],
            observable_values["borromean_conductance_decreasing_count"],
        )
        == (20, 0),
        "table_shapes_match_codebooks": (
            tuple(aggregate_table.shape),
            tuple(source_summary_table.shape),
            tuple(observable_table.shape),
        )
        == (
            (606, len(AGGREGATE_COLUMNS)),
            (7, len(SOURCE_SUMMARY_COLUMNS)),
            (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
        ),
    }

    witness = {
        "source_counts": {
            str(code): {
                "row_count": count[0],
                "conductance_decreasing_count": count[1],
                "support_changing_count": count[2],
            }
            for code, count in source_counts.items()
        },
        "conductance_decreasing_row_count": observable_values[
            "conductance_decreasing_row_count"
        ],
        "conductance_decreasing_support_changing_count": observable_values[
            "conductance_decreasing_support_changing_count"
        ],
        "best_decreasing_intervention": best,
        "aggregate_table_sha256": pair.parent.sha_array(aggregate_table),
        "source_summary_table_sha256": pair.parent.sha_array(source_summary_table),
        "observable_table_sha256": pair.parent.sha_array(observable_table),
    }

    preservation = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_sixj_conductance_decreasing_aperture_preservation@1",
        "object": "C985->d20",
        "source_codes": {
            str(source["source_code"]): source["name"] for source in SOURCE_DEFS
        },
        "claim_scope": (
            "all currently certified F-symbol/6j intervention rows in the "
            "K4-local, nonlocal top-six, focused 2114, and top-six Borromean "
            "screens"
        ),
        "summary": {
            "aggregate_row_count": observable_values["aggregate_row_count"],
            "conductance_decreasing_row_count": observable_values[
                "conductance_decreasing_row_count"
            ],
            "support_changing_row_count": observable_values[
                "support_changing_row_count"
            ],
            "best_decreasing_codes": [
                best["block_code_0"],
                best["block_code_1"],
                best["block_code_2"],
            ],
            "best_decreasing_cut_conductance_x1e12": best[
                "cut_conductance_x1e12"
            ],
            "borromean_conductance_decreasing_count": observable_values[
                "borromean_conductance_decreasing_count"
            ],
        },
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_conductance_decreasing_aperture_preservation@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_SIXJ_CONDUCTANCE_DECREASING_APERTURE_PRESERVATION_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "Across the 606 currently certified F-symbol/6j intervention rows, "
            "153 interventions decrease conductance. Every conductance-decreasing "
            "row preserves the six-edge aperture: old_cut_edge_still_cut_count "
            "is 6, old_cut_edge_same_side_count is 0, and support_changed_flag "
            "is 0. The best decreasing row is 2114+5255+1521."
        ),
        "stage_protocol": {
            "draft": "start from all certified 6j/F-symbol intervention tables",
            "witness": "aggregate rows and mark conductance-decreasing interventions",
            "coherence": "check every source report status and normalize aperture-support fields",
            "closure": "certify the current-scope preservation law for every conductance-decreasing row",
            "emit": "emit aggregate table, source summary, observables, certificate, report, verifier command, and next target",
        },
        "inputs": {
            source["name"]: {
                "report": pair.parent.input_entry(
                    source["report"],
                    {
                        "status": rows["source_reports"][
                            source["source_code"]
                        ].get("status"),
                        "certificate_sha256": rows["source_reports"][
                            source["source_code"]
                        ].get("certificate_sha256"),
                    },
                ),
                "tables": pair.parent.input_entry(source["tables"]),
            }
            for source in SOURCE_DEFS
        }
        | {
            "derive_script": pair.parent.input_entry(DERIVE_SCRIPT),
            "validator": pair.parent.input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": pair.parent.relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "preservation": pair.parent.relpath(
                OUT_DIR
                / "sixj_conductance.json"
            ),
            "aggregate_csv": pair.parent.relpath(
                OUT_DIR
                / "sixj_conductance_decreasing_aperture_preservation_rows.csv"
            ),
            "source_summary_csv": pair.parent.relpath(
                OUT_DIR
                / "sixj_conductance_decreasing_aperture_preservation_source_summary.csv"
            ),
            "observables_csv": pair.parent.relpath(
                OUT_DIR
                / "sixj_conductance_decreasing_aperture_preservation_observables.csv"
            ),
            "tables": pair.parent.relpath(
                OUT_DIR
                / "sixj_conductance_tables.npz"
            ),
            "certificate": pair.parent.relpath(
                OUT_DIR
                / "sixj_conductance_certificate.json"
            ),
            "manifest": pair.parent.relpath(OUT_DIR / "manifest.json"),
            "report": pair.parent.relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "all currently certified F-symbol/6j rows preserve the old six-edge support",
                "every currently certified conductance-decreasing F-symbol/6j row preserves the six-edge aperture",
                "2114+5255+1521 is the current best conductance-decreasing intervention in the aggregate",
                "top-six Borromean hyperedges are not conductance-decreasing and do not open the aperture",
            ],
            "does_not_certify_because_not_required": [
                "uncertified F-symbol interventions outside the listed source tables",
                "all triples over the 145 mobile nonlocal F-addresses",
                "quadruple or higher nonlocal Borromean hyperedges",
                "full rigidity under the complete associator geometry",
            ],
        },
        "next_highest_yield_item": (
            "Widen the Borromean search beyond the top-six nonlocal F-addresses, "
            "prioritizing pairwise-inert triples that include 2114 or that have "
            "high unrepaired-word coverage."
        ),
    }
    report["certificate_sha256"] = pair.parent.self_hash(report, "certificate_sha256")

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_sixj_conductance_decreasing_aperture_preservation_certificate@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "every current conductance-decreasing F-symbol/6j intervention is aperture-preserving",
            "the best current decreasing row is the focused triple 2114+5255+1521",
            "the top-six Borromean hyperedges do not belong to the conductance-decreasing family",
        ],
    }

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_conductance_decreasing_aperture_preservation_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load all certified current F-symbol/6j intervention tables",
            "normalize intervention rows into one aggregate table",
            "filter conductance-decreasing rows",
            "check six-edge aperture preservation on every decreasing row",
            "check hashes, witnesses, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = pair.parent.self_hash(manifest, "manifest_sha256")

    return {
        "preservation": preservation,
        "aggregate_csv": pair.csv_text(AGGREGATE_COLUMNS, rows["aggregate_rows"]),
        "source_summary_csv": pair.csv_text(
            SOURCE_SUMMARY_COLUMNS,
            rows["source_summaries"],
        ),
        "observables_csv": pair.csv_text(OBSERVABLE_COLUMNS, rows["observable_rows"]),
        "aggregate_table": aggregate_table,
        "source_summary_table": source_summary_table,
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
        / "sixj_conductance.json",
        payloads["preservation"],
    )
    (
        OUT_DIR / "sixj_conductance_decreasing_aperture_preservation_rows.csv"
    ).write_text(payloads["aggregate_csv"], encoding="utf-8")
    (
        OUT_DIR
        / "sixj_conductance_decreasing_aperture_preservation_source_summary.csv"
    ).write_text(payloads["source_summary_csv"], encoding="utf-8")
    (
        OUT_DIR
        / "sixj_conductance_decreasing_aperture_preservation_observables.csv"
    ).write_text(payloads["observables_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR
        / "sixj_conductance_tables.npz",
        aggregate_table=payloads["aggregate_table"],
        source_summary_table=payloads["source_summary_table"],
        observable_table=payloads["observable_table"],
    )
    pair.parent.write_json(
        OUT_DIR
        / "sixj_conductance_certificate.json",
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
