from __future__ import annotations

import json
from typing import Any

import numpy as np

try:
    from . import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_promoted_transfer_operator as flow
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_promotion import (
        OUT_DIR as SECOND_WINDOW_PROMOTION_DIR,
        STATUS as SECOND_WINDOW_PROMOTION_STATUS,
    )
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    import derive_c985_d20_signature_boundary_spine_aperture_closure_tail_promoted_transfer_operator as flow
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_promotion import (
        OUT_DIR as SECOND_WINDOW_PROMOTION_DIR,
        STATUS as SECOND_WINDOW_PROMOTION_STATUS,
    )
    from paths import D20_INVARIANTS, ROOT


THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_SECOND_WINDOW_TRANSFER_OPERATOR_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

SECOND_WINDOW_PROMOTION_REPORT = SECOND_WINDOW_PROMOTION_DIR / "report.json"
SECOND_WINDOW_PROMOTION_CERTIFICATE = (
    SECOND_WINDOW_PROMOTION_DIR
    / "signature_boundary_spine_aperture_closure_tail_second_window_promotion_certificate.json"
)
SECOND_WINDOW_PROMOTION_TABLES = (
    SECOND_WINDOW_PROMOTION_DIR
    / "signature_boundary_spine_aperture_closure_tail_second_window_promotion_tables.npz"
)
SECOND_WINDOW_PROMOTION_STATES = (
    SECOND_WINDOW_PROMOTION_DIR
    / "aperture_closure_tail_second_window_promotion_states.csv"
)
SECOND_WINDOW_PROMOTION_EDGES = (
    SECOND_WINDOW_PROMOTION_DIR
    / "aperture_closure_tail_second_window_promotion_edges.csv"
)
SECOND_WINDOW_PROMOTION_POINCARE = (
    SECOND_WINDOW_PROMOTION_DIR
    / "aperture_closure_tail_second_window_promotion_poincare.csv"
)
SECOND_WINDOW_PROMOTION_SPECTRAL_CUT = (
    SECOND_WINDOW_PROMOTION_DIR
    / "aperture_closure_tail_second_window_promotion_spectral_cut.csv"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator.py"
)

TRANSFER_STATE_COLUMNS = flow.TRANSFER_STATE_COLUMNS
TRANSFER_EDGE_COLUMNS = flow.TRANSFER_EDGE_COLUMNS
SIDE_FLOW_COLUMNS = flow.SIDE_FLOW_COLUMNS
CENTER_COLUMNS = flow.CENTER_COLUMNS
TRANSFER_OBSERVABLE_CODES = flow.TRANSFER_OBSERVABLE_CODES
FLOAT_OBSERVABLES = flow.FLOAT_OBSERVABLES
OBSERVABLE_COLUMNS = flow.OBSERVABLE_COLUMNS
NATIVE_EDGE_WEIGHT = flow.NATIVE_EDGE_WEIGHT
DERIVED_EDGE_WEIGHT = flow.DERIVED_EDGE_WEIGHT
SCALE = flow.SCALE
INDEX_PATH = flow.INDEX_PATH

csv_text = flow.csv_text
input_entry = flow.input_entry
load_json = flow.load_json
relpath = flow.relpath
self_hash = flow.self_hash
sha_array = flow.sha_array
scaled_float = flow.scaled_float
table_from_rows = flow.table_from_rows
write_json = flow.write_json


def build_payload_rows() -> dict[str, Any]:
    original_tables = flow.PROMOTED_WINDOW_TABLES
    flow.PROMOTED_WINDOW_TABLES = SECOND_WINDOW_PROMOTION_TABLES
    try:
        return flow.build_payload_rows()
    finally:
        flow.PROMOTED_WINDOW_TABLES = original_tables


def build_payloads() -> dict[str, Any]:
    promotion_report = load_json(SECOND_WINDOW_PROMOTION_REPORT)
    promotion_certificate = load_json(SECOND_WINDOW_PROMOTION_CERTIFICATE)
    rows = build_payload_rows()

    state_table = table_from_rows(TRANSFER_STATE_COLUMNS, rows["state_rows"])
    edge_table = table_from_rows(TRANSFER_EDGE_COLUMNS, rows["edge_rows"])
    side_table = table_from_rows(SIDE_FLOW_COLUMNS, rows["side_rows"])
    center_table = table_from_rows(CENTER_COLUMNS, rows["center_rows"])
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, rows["observable_rows"])

    observable_values = rows["observable_values"]
    checks = {
        "second_window_promotion_report_certified": promotion_report.get("status")
        == SECOND_WINDOW_PROMOTION_STATUS,
        "second_window_promotion_certificate_certified": promotion_certificate.get(
            "status"
        )
        == SECOND_WINDOW_PROMOTION_STATUS,
        "transfer_counts_are_expected": (
            observable_values["transfer_state_count"],
            observable_values["transfer_edge_count"],
            observable_values["total_edge_weight"],
            observable_values["total_weighted_degree"],
        )
        == (798, 2_523, 5_859, 11_718),
        "transition_weight_profile_is_expected": (
            observable_values["native_edge_count"],
            observable_values["derived_edge_count"],
            observable_values["promoted_edge_count"],
            observable_values["promoted_only_edge_count"],
            observable_values["native_edge_weight"],
            observable_values["derived_edge_weight"],
            observable_values["promoted_edge_weight"],
        )
        == (1_668, 855, 481, 22, 5_004, 855, 1_095),
        "surviving_cut_flux_is_expected": (
            observable_values["spectral_cut_edge_count"],
            observable_values["spectral_cut_weight"],
            rows["cut_flux_x1e12"],
            observable_values["old_cut_edge_count"],
            rows["old_cut_flux_x1e12"],
            observable_values["promoted_cut_edge_count"],
            rows["promoted_cut_flux_x1e12"],
        )
        == (6, 6, 1_024_065_540, 6, 1_024_065_540, 6, 1_024_065_540),
        "stationary_mass_sums_to_one": int(np.sum(state_table[:, 3])) == SCALE,
        "edge_flux_sums_to_one": int(np.sum(edge_table[:, 11])) == SCALE,
        "side_masses_are_expected": (
            next(
                row["stationary_mass_x1e12"]
                for row in rows["side_rows"]
                if row["spectral_side_code"] == 1
            ),
            next(
                row["stationary_mass_x1e12"]
                for row in rows["side_rows"]
                if row["spectral_side_code"] == -1
            ),
        )
        == (881_720_430_124, 118_279_569_876),
        "boundary_masses_are_expected": (
            int(
                next(
                    row["stationary_mass_x1e12"]
                    for row in rows["state_rows"]
                    if row["left_boundary_flag"] == 1
                )
            ),
            int(
                next(
                    row["stationary_mass_x1e12"]
                    for row in rows["state_rows"]
                    if row["gate_word_flag"] == 1
                )
            ),
            int(
                next(
                    row["stationary_mass_x1e12"]
                    for row in rows["state_rows"]
                    if row["right_boundary_flag"] == 1
                )
            ),
        )
        == (2_133_469_876, 768_049_155, 1_621_437_105),
        "flow_center_is_expected": (
            next(
                row["center_x_x1e12"]
                for row in rows["center_rows"]
                if row["center_code"] == 0
            ),
            next(
                row["center_y_x1e12"]
                for row in rows["center_rows"]
                if row["center_code"] == 0
            ),
            next(
                row["center_radius_x1e12"]
                for row in rows["center_rows"]
                if row["center_code"] == 0
            ),
            scaled_float(observable_values["flow_to_cut_center_distance"]),
            scaled_float(observable_values["flow_to_right_boundary_distance"]),
        )
        == (
            67_572_661_820,
            4_522_140_858,
            67_723_810_000,
            224_107_159_000,
            119_531_550_000,
        ),
        "promoted_cut_center_equals_full_cut_center": (
            next(
                row["center_x_x1e12"]
                for row in rows["center_rows"]
                if row["center_code"] == 2
            ),
            next(
                row["center_y_x1e12"]
                for row in rows["center_rows"]
                if row["center_code"] == 2
            ),
            next(
                row["center_radius_x1e12"]
                for row in rows["center_rows"]
                if row["center_code"] == 2
            ),
            next(
                row["center_x_x1e12"]
                for row in rows["center_rows"]
                if row["center_code"] == 4
            ),
            next(
                row["center_y_x1e12"]
                for row in rows["center_rows"]
                if row["center_code"] == 4
            ),
            next(
                row["center_radius_x1e12"]
                for row in rows["center_rows"]
                if row["center_code"] == 4
            ),
        )
        == (
            -38_651_644_583,
            39_576_416_917,
            55_319_458_000,
            -38_651_644_583,
            39_576_416_917,
            55_319_458_000,
        ),
        "flow_center_is_closer_to_right_than_gate": (
            observable_values["flow_to_right_boundary_distance"]
            < observable_values["flow_to_gate_distance"]
        ),
        "flow_center_sees_promoted_cut_as_full_cut": (
            observable_values["flow_to_promoted_cut_center_distance"]
            == observable_values["flow_to_cut_center_distance"]
        ),
        "state_table_shape_matches_codebook": tuple(state_table.shape)
        == (798, len(TRANSFER_STATE_COLUMNS)),
        "edge_table_shape_matches_codebook": tuple(edge_table.shape)
        == (2_523, len(TRANSFER_EDGE_COLUMNS)),
        "side_table_shape_matches_codebook": tuple(side_table.shape)
        == (2, len(SIDE_FLOW_COLUMNS)),
        "center_table_shape_matches_codebook": tuple(center_table.shape)
        == (6, len(CENTER_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(TRANSFER_OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    witness = {
        "transfer_state_count": observable_values["transfer_state_count"],
        "transfer_edge_count": observable_values["transfer_edge_count"],
        "total_edge_weight": observable_values["total_edge_weight"],
        "total_weighted_degree": observable_values["total_weighted_degree"],
        "weight_rule": {
            "native_edge_weight": NATIVE_EDGE_WEIGHT,
            "derived_edge_weight": DERIVED_EDGE_WEIGHT,
        },
        "edge_profile": {
            "native_edge_count": observable_values["native_edge_count"],
            "derived_edge_count": observable_values["derived_edge_count"],
            "promoted_edge_count": observable_values["promoted_edge_count"],
            "promoted_only_edge_count": observable_values[
                "promoted_only_edge_count"
            ],
            "native_edge_weight": observable_values["native_edge_weight"],
            "derived_edge_weight": observable_values["derived_edge_weight"],
            "promoted_edge_weight": observable_values["promoted_edge_weight"],
        },
        "surviving_cut_flow": {
            "cut_edge_count": observable_values["spectral_cut_edge_count"],
            "cut_weight": observable_values["spectral_cut_weight"],
            "cut_flux_x1e12": rows["cut_flux_x1e12"],
            "old_cut_edge_count": observable_values["old_cut_edge_count"],
            "old_cut_flux_x1e12": rows["old_cut_flux_x1e12"],
            "promoted_cut_edge_count": observable_values[
                "promoted_cut_edge_count"
            ],
            "promoted_cut_flux_x1e12": rows["promoted_cut_flux_x1e12"],
            "weighted_cut_conductance_x1e12": scaled_float(
                observable_values["weighted_cut_conductance"]
            ),
        },
        "side_masses": {
            str(row["spectral_side_code"]): row["stationary_mass_x1e12"]
            for row in rows["side_rows"]
        },
        "boundary_masses": {
            "left_state_id": rows["left_id"],
            "left_mass_x1e12": next(
                row["stationary_mass_x1e12"]
                for row in rows["state_rows"]
                if row["left_boundary_flag"] == 1
            ),
            "gate_state_id": rows["gate_id"],
            "gate_mass_x1e12": next(
                row["stationary_mass_x1e12"]
                for row in rows["state_rows"]
                if row["gate_word_flag"] == 1
            ),
            "right_state_id": rows["right_id"],
            "right_mass_x1e12": next(
                row["stationary_mass_x1e12"]
                for row in rows["state_rows"]
                if row["right_boundary_flag"] == 1
            ),
        },
        "mass_center": next(
            row for row in rows["center_rows"] if row["center_code"] == 0
        ),
        "cut_center": next(
            row for row in rows["center_rows"] if row["center_code"] == 2
        ),
        "promoted_cut_center": next(
            row for row in rows["center_rows"] if row["center_code"] == 4
        ),
        "top_stationary_state_id": rows["top_state_id"],
        "top_stationary_mass_x1e12": next(
            row["stationary_mass_x1e12"]
            for row in rows["state_rows"]
            if row["automaton_state_id"] == rows["top_state_id"]
        ),
        "state_table_sha256": sha_array(state_table),
        "edge_table_sha256": sha_array(edge_table),
        "side_table_sha256": sha_array(side_table),
        "center_table_sha256": sha_array(center_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    transfer_operator = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator@1",
        "object": "d20",
        "parent": SECOND_WINDOW_PROMOTION_REPORT.relative_to(ROOT).as_posix(),
        "weight_rule": {
            "native_transition_edge_weight": NATIVE_EDGE_WEIGHT,
            "derived_involving_transition_edge_weight": DERIVED_EDGE_WEIGHT,
            "rationale": "reuse the conservative native-biased kernel after the 1,4,5,5 second-window promotion",
        },
        "stationary_rule": [
            "restrict to the certified 798-state dominant second-window promoted recurrent class",
            "make the one-edit transition graph reversible with the declared edge weights",
            "stationary mass is proportional to weighted degree",
            "undirected edge flux is proportional to edge weight",
            "compare full cut, parent cut, and promoted-support cut flow centers in the second-window Poincare chart",
        ],
        "summary": {
            "state_count": observable_values["transfer_state_count"],
            "edge_count": observable_values["transfer_edge_count"],
            "cut_flux_x1e12": rows["cut_flux_x1e12"],
            "promoted_cut_flux_x1e12": rows["promoted_cut_flux_x1e12"],
            "positive_side_mass_x1e12": next(
                row["stationary_mass_x1e12"]
                for row in rows["side_rows"]
                if row["spectral_side_code"] == 1
            ),
            "negative_side_mass_x1e12": next(
                row["stationary_mass_x1e12"]
                for row in rows["side_rows"]
                if row["spectral_side_code"] == -1
            ),
        },
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_SECOND_WINDOW_TRANSFER_OPERATOR_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The second-window promoted automaton carries the native-biased "
            "reversible transfer operator on its 798-state dominant recurrent "
            "class. Native edges retain weight 3 and derived-involving edges "
            "weight 1, giving 2,523 transfer edges, total edge weight 5,859, "
            "and total weighted degree 11,718. The surviving six-edge cut "
            "carries stationary flux 1024065540/1e12, and all six cut edges "
            "now carry promoted-window support. Positive-side stationary mass "
            "is 881720430124/1e12, while the negative side carries "
            "118279569876/1e12. The full cut, parent cut, and promoted-support "
            "cut centers coincide, so the second promotion closes the support "
            "gap but still loads the same six-edge aperture."
        ),
        "stage_protocol": {
            "draft": "weight native and derived transitions on the second-window promoted automaton",
            "witness": "emit second-window transfer-state, transfer-edge, side-flow, center, and observable tables",
            "coherence": "check stationary mass, flux, side mass, boundary landmarks, and promoted cut lineage",
            "closure": "certify the native-biased second-window stationary flow and its Poincare relation to the surviving cut",
            "emit": "emit transfer artifacts, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "second_window_promotion_report": input_entry(
                SECOND_WINDOW_PROMOTION_REPORT,
                {
                    "status": promotion_report.get("status"),
                    "certificate_sha256": promotion_report.get("certificate_sha256"),
                },
            ),
            "second_window_promotion_certificate": input_entry(
                SECOND_WINDOW_PROMOTION_CERTIFICATE
            ),
            "second_window_promotion_states": input_entry(
                SECOND_WINDOW_PROMOTION_STATES
            ),
            "second_window_promotion_edges": input_entry(
                SECOND_WINDOW_PROMOTION_EDGES
            ),
            "second_window_promotion_poincare": input_entry(
                SECOND_WINDOW_PROMOTION_POINCARE
            ),
            "second_window_promotion_spectral_cut": input_entry(
                SECOND_WINDOW_PROMOTION_SPECTRAL_CUT
            ),
            "second_window_promotion_tables": input_entry(
                SECOND_WINDOW_PROMOTION_TABLES
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "second_window_transfer_operator": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator.json"
            ),
            "second_window_transfer_states_csv": relpath(
                OUT_DIR / "aperture_closure_tail_second_window_transfer_states.csv"
            ),
            "second_window_transfer_edges_csv": relpath(
                OUT_DIR / "aperture_closure_tail_second_window_transfer_edges.csv"
            ),
            "second_window_transfer_side_flow_csv": relpath(
                OUT_DIR
                / "aperture_closure_tail_second_window_transfer_side_flow.csv"
            ),
            "second_window_transfer_centers_csv": relpath(
                OUT_DIR / "aperture_closure_tail_second_window_transfer_centers.csv"
            ),
            "second_window_transfer_observables_csv": relpath(
                OUT_DIR
                / "aperture_closure_tail_second_window_transfer_observables.csv"
            ),
            "second_window_transfer_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator_tables.npz"
            ),
            "second_window_transfer_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the native-biased reversible transfer operator on the dominant second-window promoted recurrent class",
                "the exact integer-scaled stationary distribution and undirected edge fluxes",
                "the spectral-side stationary mass split and surviving cut flux",
                "parent-cut and promoted-cut flow lineage inside the fresh second-window Poincare chart",
            ],
            "does_not_certify_because_not_required": [
                "alternative edge-weight schedules",
                "stationary flow on smaller recurrent classes",
                "promotion closure beyond the two certified window blocks",
                "compiler integration of promoted transfer weights",
            ],
        },
        "next_highest_yield_item": (
            "Rank the six second-window transfer cut edges by stationary flux "
            "and search for a third intervention that changes cut support "
            "rather than merely adding promoted-window support to the same "
            "six-edge aperture."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator_certificate@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the dominant second-window promoted recurrent class supports a reversible native-biased transfer operator",
            "the stationary distribution is exactly reproducible from weighted degrees",
            "the surviving six-edge cut still carries bottleneck flux",
            "all six cut edges now touch promoted support and carry all of the cut flux",
            "the promoted-support cut center coincides with the full cut center",
        ],
    }

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified second-window promoted automaton artifacts",
            "build the native-biased reversible transfer operator",
            "check stationary mass, edge flux, side masses, boundary masses, and promoted cut lineage",
            "compare the stationary Poincare center against full-cut, parent-cut, promoted-cut, and boundary landmarks",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "second_window_transfer_operator": transfer_operator,
        "second_window_transfer_states_csv": csv_text(
            TRANSFER_STATE_COLUMNS,
            rows["state_rows"],
        ),
        "second_window_transfer_edges_csv": csv_text(
            TRANSFER_EDGE_COLUMNS,
            rows["edge_rows"],
        ),
        "second_window_transfer_side_flow_csv": csv_text(
            SIDE_FLOW_COLUMNS,
            rows["side_rows"],
        ),
        "second_window_transfer_centers_csv": csv_text(
            CENTER_COLUMNS,
            rows["center_rows"],
        ),
        "second_window_transfer_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            rows["observable_rows"],
        ),
        "state_table": state_table,
        "edge_table": edge_table,
        "side_table": side_table,
        "center_table": center_table,
        "observable_table": observable_table,
        "second_window_transfer_certificate": certificate,
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
        / "signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator.json",
        payloads["second_window_transfer_operator"],
    )
    (OUT_DIR / "aperture_closure_tail_second_window_transfer_states.csv").write_text(
        payloads["second_window_transfer_states_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_second_window_transfer_edges.csv").write_text(
        payloads["second_window_transfer_edges_csv"],
        encoding="utf-8",
    )
    (
        OUT_DIR / "aperture_closure_tail_second_window_transfer_side_flow.csv"
    ).write_text(
        payloads["second_window_transfer_side_flow_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_second_window_transfer_centers.csv").write_text(
        payloads["second_window_transfer_centers_csv"],
        encoding="utf-8",
    )
    (
        OUT_DIR / "aperture_closure_tail_second_window_transfer_observables.csv"
    ).write_text(
        payloads["second_window_transfer_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator_tables.npz",
        state_table=payloads["state_table"],
        edge_table=payloads["edge_table"],
        side_table=payloads["side_table"],
        center_table=payloads["center_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator_certificate.json",
        payloads["second_window_transfer_certificate"],
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
