from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_realization import (
        EXACT_WITNESS_COLUMNS,
        OBSERVABLE_COLUMNS as PARENT_OBSERVABLE_COLUMNS,
        OUT_DIR as CARRIER_SPLICE_DIR,
        SELECTED_SIX_TEMPLATE_TRACE,
        SELECTED_SIX_TEMPLATE_WORD,
        SELECTED_TEMPLATE_COLUMNS,
        STATUS as CARRIER_SPLICE_STATUS,
        TRACE_NODE_COLUMNS,
        WORD_COLUMNS,
        input_entry,
        relpath,
        self_hash,
        sha_array,
        table_from_rows,
        write_json,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_rewrite_node_lift import (
        csv_text,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_realization import (
        EXACT_WITNESS_COLUMNS,
        OBSERVABLE_COLUMNS as PARENT_OBSERVABLE_COLUMNS,
        OUT_DIR as CARRIER_SPLICE_DIR,
        SELECTED_SIX_TEMPLATE_TRACE,
        SELECTED_SIX_TEMPLATE_WORD,
        SELECTED_TEMPLATE_COLUMNS,
        STATUS as CARRIER_SPLICE_STATUS,
        TRACE_NODE_COLUMNS,
        WORD_COLUMNS,
        input_entry,
        relpath,
        self_hash,
        sha_array,
        table_from_rows,
        write_json,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_rewrite_node_lift import (
        csv_text,
    )
    from derive_c985_typed_simple_object_registry import INDEX_PATH
    from paths import D20_INVARIANTS, ROOT


THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_CARRIER_SPLICE_OPTIMALITY_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

CARRIER_SPLICE_REPORT = CARRIER_SPLICE_DIR / "report.json"
CARRIER_SPLICE_JSON = (
    CARRIER_SPLICE_DIR
    / "signature_boundary_spine_aperture_closure_tail_carrier_splice_realization.json"
)
CARRIER_SPLICE_EXACT_WITNESSES = (
    CARRIER_SPLICE_DIR / "aperture_closure_tail_carrier_splice_exact_witnesses.csv"
)
CARRIER_SPLICE_SELECTED_TEMPLATES = (
    CARRIER_SPLICE_DIR / "aperture_closure_tail_carrier_splice_selected_templates.csv"
)
CARRIER_SPLICE_OBSERVABLES = (
    CARRIER_SPLICE_DIR / "aperture_closure_tail_carrier_splice_observables.csv"
)
CARRIER_SPLICE_TABLES = (
    CARRIER_SPLICE_DIR
    / "signature_boundary_spine_aperture_closure_tail_carrier_splice_realization_tables.npz"
)
CARRIER_SPLICE_CERTIFICATE = (
    CARRIER_SPLICE_DIR
    / "signature_boundary_spine_aperture_closure_tail_carrier_splice_realization_certificate.json"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality.py"
)

SELECTED_SPLICE_WITNESS_ID = 2
SELECTED_VARIATION = 223
ALL_EXACT_MIN_VARIATION = 197
ALL_EXACT_MIN_VARIATION_WITNESS_ID = 0

FRONTIER_COLUMNS = [
    "splice_witness_id",
    "word_length",
    "pre_tail_symbol_count",
    "inserted_symbol_count_over_rank104",
    "metric_gromov_delta_twice",
    "trace_signature_total_variation",
    "first_return_closed_path_count",
    "full_carrier_path_count",
    "normalized_tail_template_count",
    "template_lift_count_min",
    "template_lift_count_max",
    "tail_entry_9_path_count",
    "tail_entry_10_path_count",
    "tail_entry_11_path_count",
    "has_chord_31_28_flag",
    "has_chord_50_34_flag",
    "rank104_prefix_27_31_50_flag",
    "shared_rewrite_tail_suffix_flag",
    "six_template_retention_flag",
    "selected_min_variation_flag",
    "selected_six_template_retention_flag",
]

CLASS_COLUMNS = [
    "class_id",
    "class_code",
    "witness_count",
    "min_variation",
    "max_variation",
    "min_variation_witness_id",
    "selected_witness_member_flag",
    "six_template_member_count",
    "lower_than_selected_count",
    "lower_than_selected_six_template_count",
]

OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

CLASS_CODES = {
    "all_exact_24_delta2_splices": 0,
    "rank104_prefix_exact_splices": 1,
    "shared_rewrite_tail_exact_splices": 2,
    "six_template_retention_exact_splices": 3,
    "lower_variation_than_selected_exact_splices": 4,
    "both_repair_chords_exact_splices": 5,
}

OBSERVABLE_CODES = {
    "exact_24_delta2_splice_count": 0,
    "selected_splice_witness_id": 1,
    "selected_variation": 2,
    "six_template_retention_exact_count": 3,
    "six_template_min_variation": 4,
    "six_template_lower_than_selected_count": 5,
    "lower_than_selected_exact_count": 6,
    "lower_than_selected_six_template_count": 7,
    "rank104_prefix_exact_count": 8,
    "shared_rewrite_tail_exact_count": 9,
    "both_repair_chords_exact_count": 10,
    "all_exact_min_variation": 11,
    "all_exact_min_variation_witness_id": 12,
    "selected_endpoint_9_count": 13,
    "selected_endpoint_10_count": 14,
    "selected_endpoint_11_count": 15,
    "selected_template_lift_count": 16,
}


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} is not a JSON object")
    return payload


def read_int_dict_csv(path: Path) -> list[dict[str, int]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            {key: int(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def selected_word(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(row[column] for column in WORD_COLUMNS[: row["word_length"]])


def selected_trace(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(row[column] for column in TRACE_NODE_COLUMNS[: row["trace_node_count"]])


def class_row(
    class_id: int,
    class_name: str,
    rows: list[dict[str, int]],
) -> dict[str, int]:
    variations = [row["trace_signature_total_variation"] for row in rows]
    min_variation = min(variations)
    min_witness = min(
        row["splice_witness_id"]
        for row in rows
        if row["trace_signature_total_variation"] == min_variation
    )
    return {
        "class_id": class_id,
        "class_code": CLASS_CODES[class_name],
        "witness_count": len(rows),
        "min_variation": min_variation,
        "max_variation": max(variations),
        "min_variation_witness_id": min_witness,
        "selected_witness_member_flag": int(
            any(row["splice_witness_id"] == SELECTED_SPLICE_WITNESS_ID for row in rows)
        ),
        "six_template_member_count": sum(
            row["six_template_retention_flag"] for row in rows
        ),
        "lower_than_selected_count": sum(
            row["trace_signature_total_variation"] < SELECTED_VARIATION
            for row in rows
        ),
        "lower_than_selected_six_template_count": sum(
            row["trace_signature_total_variation"] < SELECTED_VARIATION
            and row["six_template_retention_flag"] == 1
            for row in rows
        ),
    }


def build_payloads() -> dict[str, Any]:
    carrier_report = load_json(CARRIER_SPLICE_REPORT)
    carrier_json = load_json(CARRIER_SPLICE_JSON)
    carrier_certificate = load_json(CARRIER_SPLICE_CERTIFICATE)
    exact_rows_parent = read_int_dict_csv(CARRIER_SPLICE_EXACT_WITNESSES)
    template_rows_parent = read_int_dict_csv(CARRIER_SPLICE_SELECTED_TEMPLATES)

    exact_rows = [
        {column: row[column] for column in FRONTIER_COLUMNS}
        for row in exact_rows_parent
    ]
    selected_rows = [
        row
        for row in exact_rows_parent
        if row["selected_six_template_retention_flag"] == 1
    ]
    if len(selected_rows) != 1:
        raise AssertionError("expected exactly one selected six-template splice")
    selected = selected_rows[0]
    six_template_rows = [
        row for row in exact_rows_parent if row["six_template_retention_flag"] == 1
    ]
    lower_than_selected_rows = [
        row
        for row in exact_rows_parent
        if row["trace_signature_total_variation"] < SELECTED_VARIATION
    ]
    rank104_prefix_rows = [
        row for row in exact_rows_parent if row["rank104_prefix_27_31_50_flag"] == 1
    ]
    shared_tail_rows = [
        row for row in exact_rows_parent if row["shared_rewrite_tail_suffix_flag"] == 1
    ]
    both_chord_rows = [
        row
        for row in exact_rows_parent
        if row["has_chord_31_28_flag"] == 1 and row["has_chord_50_34_flag"] == 1
    ]

    class_rows = [
        class_row(0, "all_exact_24_delta2_splices", exact_rows_parent),
        class_row(1, "rank104_prefix_exact_splices", rank104_prefix_rows),
        class_row(2, "shared_rewrite_tail_exact_splices", shared_tail_rows),
        class_row(3, "six_template_retention_exact_splices", six_template_rows),
        class_row(4, "lower_variation_than_selected_exact_splices", lower_than_selected_rows),
        class_row(5, "both_repair_chords_exact_splices", both_chord_rows),
    ]

    selected_template_lift_count = min(
        row["selected_splice_path_count"] for row in template_rows_parent
    )
    observable_values = {
        "exact_24_delta2_splice_count": len(exact_rows_parent),
        "selected_splice_witness_id": selected["splice_witness_id"],
        "selected_variation": selected["trace_signature_total_variation"],
        "six_template_retention_exact_count": len(six_template_rows),
        "six_template_min_variation": min(
            row["trace_signature_total_variation"] for row in six_template_rows
        ),
        "six_template_lower_than_selected_count": sum(
            row["trace_signature_total_variation"] < SELECTED_VARIATION
            for row in six_template_rows
        ),
        "lower_than_selected_exact_count": len(lower_than_selected_rows),
        "lower_than_selected_six_template_count": sum(
            row["six_template_retention_flag"] for row in lower_than_selected_rows
        ),
        "rank104_prefix_exact_count": len(rank104_prefix_rows),
        "shared_rewrite_tail_exact_count": len(shared_tail_rows),
        "both_repair_chords_exact_count": len(both_chord_rows),
        "all_exact_min_variation": min(
            row["trace_signature_total_variation"] for row in exact_rows_parent
        ),
        "all_exact_min_variation_witness_id": min(
            row["splice_witness_id"]
            for row in exact_rows_parent
            if row["trace_signature_total_variation"] == ALL_EXACT_MIN_VARIATION
        ),
        "selected_endpoint_9_count": selected["tail_entry_9_path_count"],
        "selected_endpoint_10_count": selected["tail_entry_10_path_count"],
        "selected_endpoint_11_count": selected["tail_entry_11_path_count"],
        "selected_template_lift_count": selected_template_lift_count,
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

    frontier_table = table_from_rows(FRONTIER_COLUMNS, exact_rows)
    class_table = table_from_rows(CLASS_COLUMNS, class_rows)
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    checks = {
        "carrier_splice_report_certified": carrier_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_CARRIER_SPLICE_REALIZATION_CERTIFIED",
        "carrier_splice_certificate_certified": carrier_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_CARRIER_SPLICE_REALIZATION_CERTIFIED",
        "carrier_splice_schema_available": carrier_json.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_realization@1",
        "parent_carrier_splice_boundary_declares_bounded_exhaustive_search": carrier_report.get(
            "checks", {}
        ).get("bounded_search_space_is_19500")
        is True
        and carrier_report.get("checks", {}).get(
            "eleven_exact_24_path_delta2_splices_exist"
        )
        is True,
        "all_frontier_rows_are_24_path_delta2": all(
            row["metric_gromov_delta_twice"] == 2
            and row["first_return_closed_path_count"] == 24
            for row in exact_rows_parent
        ),
        "selected_six_template_splice_is_witness_2": selected[
            "splice_witness_id"
        ]
        == SELECTED_SPLICE_WITNESS_ID,
        "selected_word_and_trace_match_parent": selected_word(selected)
        == SELECTED_SIX_TEMPLATE_WORD
        and selected_trace(selected) == SELECTED_SIX_TEMPLATE_TRACE,
        "six_template_retention_is_unique": len(six_template_rows) == 1
        and six_template_rows[0]["splice_witness_id"] == SELECTED_SPLICE_WITNESS_ID,
        "six_template_minimum_variation_is_223": observable_values[
            "six_template_min_variation"
        ]
        == SELECTED_VARIATION,
        "no_lower_variation_row_retains_six_templates": observable_values[
            "lower_than_selected_six_template_count"
        ]
        == 0
        and observable_values["six_template_lower_than_selected_count"] == 0,
        "lower_variation_rows_are_not_tail_retaining": [
            row["splice_witness_id"] for row in lower_than_selected_rows
        ]
        == [0, 1]
        and all(row["six_template_retention_flag"] == 0 for row in lower_than_selected_rows),
        "selected_endpoint_distribution_is_12_4_8": (
            selected["tail_entry_9_path_count"],
            selected["tail_entry_10_path_count"],
            selected["tail_entry_11_path_count"],
        )
        == (12, 4, 8),
        "selected_template_lifts_are_uniform_four": [
            row["selected_splice_path_count"] for row in template_rows_parent
        ]
        == [4, 4, 4, 4, 4, 4],
        "frontier_table_shape_matches_codebook": tuple(frontier_table.shape)
        == (11, len(FRONTIER_COLUMNS)),
        "class_table_shape_matches_codebook": tuple(class_table.shape)
        == (6, len(CLASS_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    witness = {
        "selected_splice_witness_id": SELECTED_SPLICE_WITNESS_ID,
        "selected_word": list(SELECTED_SIX_TEMPLATE_WORD),
        "selected_trace": list(SELECTED_SIX_TEMPLATE_TRACE),
        "selected_variation": selected["trace_signature_total_variation"],
        "selected_closed_path_count": selected["first_return_closed_path_count"],
        "selected_delta_twice": selected["metric_gromov_delta_twice"],
        "six_template_retention_exact_count": len(six_template_rows),
        "lower_variation_exact_witness_ids": [
            row["splice_witness_id"] for row in lower_than_selected_rows
        ],
        "lower_variation_six_template_count": observable_values[
            "lower_than_selected_six_template_count"
        ],
        "bounded_minimum_statement": (
            "witness 2 is the unique six-template-retaining exact splice, "
            "therefore variation 223 is the bounded minimum under the declared "
            "tail-retention constraints"
        ),
        "frontier_table_sha256": sha_array(frontier_table),
        "class_table_sha256": sha_array(class_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    optimality = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality@1",
        "object": "d20",
        "comparison_rule": {
            "parent": CARRIER_SPLICE_REPORT.relative_to(ROOT).as_posix(),
            "bounded_search_space": "fixed prefix x2,x1; pre-tail lengths 5..8; fixed tail x5,x2,x1,x4,x5",
            "required_constraints": [
                "first_return_closed_path_count = 24",
                "metric_gromov_delta_twice = 2",
                "six normalized rank104 tail templates retained",
                "four lifts per retained template",
            ],
        },
        "summary": {
            "exact_24_delta2_splice_count": len(exact_rows_parent),
            "six_template_retention_exact_count": len(six_template_rows),
            "selected_splice_witness_id": SELECTED_SPLICE_WITNESS_ID,
            "bounded_minimum_variation": SELECTED_VARIATION,
            "lower_variation_exact_count": len(lower_than_selected_rows),
            "lower_variation_six_template_count": 0,
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_CARRIER_SPLICE_OPTIMALITY_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the parent carrier-splice layer exhausts the bounded pre-tail search and emits all 11 exact 24-path delta2 splices",
            "only witness 2 retains all six rank104 tail templates with four lifts each",
            "the two exact splices with lower variation than 223 do not retain the six-template tail distribution",
            "therefore 223 is the bounded variation minimum under the declared six-template tail-retention constraints",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "Within the certified bounded carrier-splice frontier, the "
            "six-template-retaining splice is already variation-optimal. The "
            "parent layer emits all 11 bounded words with 24 first-return "
            "closures and delta_twice 2. Only witness 2 retains all six "
            "rank104 tail templates at four lifts each; its variation is 223. "
            "The lower-variation exact splices, witnesses 0 and 1 at variation "
            "197 and 199, collapse the tail-template distribution and therefore "
            "do not satisfy the retained-tail constraint."
        ),
        "stage_protocol": {
            "draft": "reuse the certified carrier-splice frontier instead of re-running the 19,500-word search",
            "witness": "project all exact 24-path delta2 splices and their tail-retention flags",
            "coherence": "compare variation minima by all-exact, rank104-prefix, shared-tail, six-template, and both-chord classes",
            "closure": "certify that no lower-variation exact splice retains the six rank104 tail templates",
            "emit": "emit frontier rows, class rows, observables, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "carrier_splice_report": input_entry(
                CARRIER_SPLICE_REPORT,
                {
                    "status": carrier_report.get("status"),
                    "certificate_sha256": carrier_report.get("certificate_sha256"),
                },
            ),
            "carrier_splice_json": input_entry(CARRIER_SPLICE_JSON),
            "carrier_splice_exact_witnesses": input_entry(
                CARRIER_SPLICE_EXACT_WITNESSES
            ),
            "carrier_splice_selected_templates": input_entry(
                CARRIER_SPLICE_SELECTED_TEMPLATES
            ),
            "carrier_splice_observables": input_entry(CARRIER_SPLICE_OBSERVABLES),
            "carrier_splice_tables": input_entry(CARRIER_SPLICE_TABLES),
            "carrier_splice_certificate": input_entry(CARRIER_SPLICE_CERTIFICATE),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality.json"
            ),
            "aperture_closure_tail_carrier_splice_frontier_csv": relpath(
                OUT_DIR / "aperture_closure_tail_carrier_splice_frontier.csv"
            ),
            "aperture_closure_tail_carrier_splice_optimality_classes_csv": relpath(
                OUT_DIR
                / "aperture_closure_tail_carrier_splice_optimality_classes.csv"
            ),
            "aperture_closure_tail_carrier_splice_optimality_observables_csv": relpath(
                OUT_DIR
                / "aperture_closure_tail_carrier_splice_optimality_observables.csv"
            ),
            "signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality_tables.npz"
            ),
            "signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "bounded variation optimality of the six-template-retaining carrier splice",
                "that witnesses 0 and 1 are the only lower-variation exact splices and both fail six-template retention",
                "that witness 2 is the unique exact splice retaining six rank104 tail templates at four lifts each",
                "that variation 223 is the bounded minimum under the declared tail-retention constraints",
            ],
            "does_not_certify_because_not_required": [
                "global optimality outside the parent bounded pre-tail search",
                "carrier splices that abandon the six-template rank104 tail distribution",
                "edit costs above the parent three-insertion bound",
                "categorical pivotal, spherical, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Relax the tail-retention constraint one notch: characterize the "
            "lower-variation exact splices at variation 197 and 199, then test "
            "whether their collapsed tail distributions can be lifted back to "
            "six templates without reintroducing delta_twice 4."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified carrier-splice realization artifacts",
            "project exact 24-path delta2 frontier rows",
            "group frontier by tail-retention and repair-chord classes",
            "check unique six-template retention and no lower-variation retained-tail row",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality": optimality,
        "aperture_closure_tail_carrier_splice_frontier_csv": csv_text(
            FRONTIER_COLUMNS,
            exact_rows,
        ),
        "aperture_closure_tail_carrier_splice_optimality_classes_csv": csv_text(
            CLASS_COLUMNS,
            class_rows,
        ),
        "aperture_closure_tail_carrier_splice_optimality_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "frontier_table": frontier_table,
        "class_table": class_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality_certificate": certificate,
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
        / "signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality.json",
        payloads[
            "signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality"
        ],
    )
    (OUT_DIR / "aperture_closure_tail_carrier_splice_frontier.csv").write_text(
        payloads["aperture_closure_tail_carrier_splice_frontier_csv"],
        encoding="utf-8",
    )
    (
        OUT_DIR / "aperture_closure_tail_carrier_splice_optimality_classes.csv"
    ).write_text(
        payloads["aperture_closure_tail_carrier_splice_optimality_classes_csv"],
        encoding="utf-8",
    )
    (
        OUT_DIR / "aperture_closure_tail_carrier_splice_optimality_observables.csv"
    ).write_text(
        payloads["aperture_closure_tail_carrier_splice_optimality_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality_tables.npz",
        frontier_table=payloads["frontier_table"],
        class_table=payloads["class_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality_certificate"
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
