from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .derive_long_raw import csv_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_raw import csv_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_c59p3a"
STATUS = "LONG_C59P3A_ATOM_STRESS_ORIENTATION_CANDIDATE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_C59P3O = PROOF_ROOT / "long_c59p3o" / "report.json"
LONG_C59P3V = PROOF_ROOT / "long_c59p3v" / "report.json"
LONG_C59P3V_SUPPORT = PROOF_ROOT / "long_c59p3v" / "support.csv"
LONG_STRESS_GATE = PROOF_ROOT / "long_stress_gate" / "report.json"
LONG_STRESS_EDGE = PROOF_ROOT / "long_stress_gate" / "stress_edge.csv"
LONG_STRESS_COUPLE = PROOF_ROOT / "long_stress_couple" / "report.json"
LONG_TRANSITION_SEM = PROOF_ROOT / "long_transition_sem" / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_c59p3a.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_c59p3a.py"

COEFF_COLUMNS = ["selector_id", "source_atom", "coefficient"]
OVERLAP_COLUMNS = [
    "selector_id",
    "stress_edge_id",
    "source_atom",
    "target_atom",
    "source_coefficient",
    "target_coefficient",
    "coefficient_product",
    "weight_scaled",
    "signed_tension_scaled",
    "signed_tension_contribution_scaled",
    "weight_contribution_scaled",
    "abs_tension_contribution_scaled",
]
SCORE_COLUMNS = [
    "selector_id",
    "selector_code",
    "induced_edge_count",
    "signed_tension_score_scaled",
    "weight_score_scaled",
    "abs_tension_score_scaled",
    "selected_by_signed_tension_flag",
    "physical_selector_axiom_flag",
    "transition_stress_map_flag",
]
DECISION_COLUMNS = [
    "decision_id",
    "decision_code",
    "value",
    "certified_flag",
    "obstruction_flag",
]
GAP_COLUMNS = [
    "gap_id",
    "gap_code",
    "certified_flag",
    "open_flag",
    "obstruction_flag",
    "next_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

SELECTOR_NAMES = ["positive_volume_max", "negative_volume_max"]
SELECTOR_CODES = {name: index for index, name in enumerate(SELECTOR_NAMES)}
DECISION_NAMES = [
    "atom_overlap_stress_score_materialized",
    "signed_tension_score_distinguishes_pair",
    "formal_positive_orientation_candidate_selected",
    "transition_stress_map_available",
    "semantic_transition_operation_available",
    "physical_selector_axiom_available",
]
DECISION_CODES = {name: index for index, name in enumerate(DECISION_NAMES)}
GAP_NAMES = [
    "atom_overlap_stress_orientation_candidate",
    "transition_to_stress_coupling_map",
    "semantic_transition_operation",
    "physical_selector_axiom",
    "four_dimensional_metric_reduction",
    "thermal_gravity_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}
OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "selector_count",
    "support_row_count",
    "shared_support_atom_count",
    "overlap_row_count",
    "positive_overlap_edge_count",
    "negative_overlap_edge_count",
    "positive_signed_tension_score_scaled",
    "negative_signed_tension_score_scaled",
    "signed_tension_score_difference_scaled",
    "positive_weight_score_scaled",
    "negative_weight_score_scaled",
    "positive_abs_tension_score_scaled",
    "negative_abs_tension_score_scaled",
    "selected_selector_id",
    "selected_selector_code",
    "atom_overlap_orientation_candidate_flag",
    "transition_stress_map_certified_flag",
    "semantic_transition_operation_flag",
    "physical_selector_axiom_flag",
    "four_dimensional_metric_flag",
    "thermal_gravity_flag",
    "next_gap_code",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_csv_int(path: Path) -> list[dict[str, int]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return [{key: int(value) for key, value in row.items()} for row in reader]


def certified(report: dict[str, Any]) -> bool:
    return report.get("all_checks_pass") is True and (
        "CERTIFIED" in str(report.get("status", ""))
        or "OBSTRUCTION_CERTIFIED" in str(report.get("status", ""))
    )


def summary(report: dict[str, Any]) -> dict[str, Any]:
    witness = report.get("witness", {})
    value = witness.get("summary", {})
    if not isinstance(value, dict):
        raise AssertionError("report witness summary is not an object")
    return value


def build_coeff_rows(support_rows: list[dict[str, int]]) -> list[dict[str, int]]:
    coeff_rows = []
    for selector_id in [0, 1]:
        by_atom: dict[int, int] = {}
        for row in support_rows:
            if row["selector_id"] != selector_id:
                continue
            by_atom[row["source_atom"]] = by_atom.get(row["source_atom"], 0) + row[
                "coefficient"
            ]
        for atom in sorted(by_atom):
            coeff_rows.append(
                {
                    "selector_id": selector_id,
                    "source_atom": atom,
                    "coefficient": by_atom[atom],
                }
            )
    return coeff_rows


def build_overlap_rows(
    coeff_rows: list[dict[str, int]],
    stress_edges: list[dict[str, int]],
) -> list[dict[str, int]]:
    coeff_by_selector: dict[int, dict[int, int]] = {0: {}, 1: {}}
    for row in coeff_rows:
        coeff_by_selector[row["selector_id"]][row["source_atom"]] = row[
            "coefficient"
        ]
    overlap_rows = []
    for selector_id in [0, 1]:
        coeff = coeff_by_selector[selector_id]
        for edge in stress_edges:
            source_atom = edge["source_atom"]
            target_atom = edge["target_atom"]
            if source_atom not in coeff or target_atom not in coeff:
                continue
            product = coeff[source_atom] * coeff[target_atom]
            signed_tension = edge["signed_tension_scaled"]
            weight = edge["weight_scaled"]
            overlap_rows.append(
                {
                    "selector_id": selector_id,
                    "stress_edge_id": edge["stress_edge_id"],
                    "source_atom": source_atom,
                    "target_atom": target_atom,
                    "source_coefficient": coeff[source_atom],
                    "target_coefficient": coeff[target_atom],
                    "coefficient_product": product,
                    "weight_scaled": weight,
                    "signed_tension_scaled": signed_tension,
                    "signed_tension_contribution_scaled": product * signed_tension,
                    "weight_contribution_scaled": product * weight,
                    "abs_tension_contribution_scaled": product * abs(signed_tension),
                }
            )
    return overlap_rows


def build_rows() -> dict[str, Any]:
    c59p3o = load_json(LONG_C59P3O)
    c59p3v = load_json(LONG_C59P3V)
    stress_gate = load_json(LONG_STRESS_GATE)
    stress_couple = load_json(LONG_STRESS_COUPLE)
    transition_sem = load_json(LONG_TRANSITION_SEM)
    support_rows = read_csv_int(LONG_C59P3V_SUPPORT)
    stress_edges = read_csv_int(LONG_STRESS_EDGE)
    coeff_rows = build_coeff_rows(support_rows)
    overlap_rows = build_overlap_rows(coeff_rows, stress_edges)

    stress_couple_summary = summary(stress_couple)
    transition_summary = summary(transition_sem)
    transition_stress_map_flag = int(stress_couple_summary["coupling_map_certified_flag"])
    semantic_transition_flag = int(transition_summary["semantic_transition_operation_flag"])
    physical_selector_flag = int(summary(c59p3o)["physical_orientation_selector_flag"])

    score_rows = []
    for selector_id in [0, 1]:
        rows = [row for row in overlap_rows if row["selector_id"] == selector_id]
        signed_score = sum(row["signed_tension_contribution_scaled"] for row in rows)
        weight_score = sum(row["weight_contribution_scaled"] for row in rows)
        abs_tension_score = sum(row["abs_tension_contribution_scaled"] for row in rows)
        score_rows.append(
            {
                "selector_id": selector_id,
                "selector_code": selector_id,
                "induced_edge_count": len(rows),
                "signed_tension_score_scaled": signed_score,
                "weight_score_scaled": weight_score,
                "abs_tension_score_scaled": abs_tension_score,
                "selected_by_signed_tension_flag": 0,
                "physical_selector_axiom_flag": physical_selector_flag,
                "transition_stress_map_flag": transition_stress_map_flag,
            }
        )
    selected = max(score_rows, key=lambda row: row["signed_tension_score_scaled"])
    selected["selected_by_signed_tension_flag"] = 1
    positive = score_rows[0]
    negative = score_rows[1]
    shared_support_atom_count = len(
        {
            row["source_atom"]
            for row in coeff_rows
            if row["selector_id"] == 0
        }
        & {
            row["source_atom"]
            for row in coeff_rows
            if row["selector_id"] == 1
        }
    )
    obs = {
        "input_report_count": 5,
        "input_certified_count": int(certified(c59p3o))
        + int(certified(c59p3v))
        + int(certified(stress_gate))
        + int(certified(stress_couple))
        + int(certified(transition_sem)),
        "selector_count": 2,
        "support_row_count": len(coeff_rows),
        "shared_support_atom_count": shared_support_atom_count,
        "overlap_row_count": len(overlap_rows),
        "positive_overlap_edge_count": positive["induced_edge_count"],
        "negative_overlap_edge_count": negative["induced_edge_count"],
        "positive_signed_tension_score_scaled": positive[
            "signed_tension_score_scaled"
        ],
        "negative_signed_tension_score_scaled": negative[
            "signed_tension_score_scaled"
        ],
        "signed_tension_score_difference_scaled": positive[
            "signed_tension_score_scaled"
        ]
        - negative["signed_tension_score_scaled"],
        "positive_weight_score_scaled": positive["weight_score_scaled"],
        "negative_weight_score_scaled": negative["weight_score_scaled"],
        "positive_abs_tension_score_scaled": positive["abs_tension_score_scaled"],
        "negative_abs_tension_score_scaled": negative["abs_tension_score_scaled"],
        "selected_selector_id": selected["selector_id"],
        "selected_selector_code": selected["selector_code"],
        "atom_overlap_orientation_candidate_flag": 1,
        "transition_stress_map_certified_flag": transition_stress_map_flag,
        "semantic_transition_operation_flag": semantic_transition_flag,
        "physical_selector_axiom_flag": physical_selector_flag,
        "four_dimensional_metric_flag": 0,
        "thermal_gravity_flag": 0,
        "next_gap_code": GAP_CODES["transition_to_stress_coupling_map"],
    }
    decision_rows = [
        {
            "decision_id": DECISION_CODES["atom_overlap_stress_score_materialized"],
            "decision_code": DECISION_CODES["atom_overlap_stress_score_materialized"],
            "value": obs["overlap_row_count"],
            "certified_flag": 1,
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES["signed_tension_score_distinguishes_pair"],
            "decision_code": DECISION_CODES["signed_tension_score_distinguishes_pair"],
            "value": obs["signed_tension_score_difference_scaled"],
            "certified_flag": 1,
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES[
                "formal_positive_orientation_candidate_selected"
            ],
            "decision_code": DECISION_CODES[
                "formal_positive_orientation_candidate_selected"
            ],
            "value": obs["selected_selector_id"],
            "certified_flag": int(obs["selected_selector_id"] == 0),
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES["transition_stress_map_available"],
            "decision_code": DECISION_CODES["transition_stress_map_available"],
            "value": transition_stress_map_flag,
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "decision_id": DECISION_CODES["semantic_transition_operation_available"],
            "decision_code": DECISION_CODES["semantic_transition_operation_available"],
            "value": semantic_transition_flag,
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "decision_id": DECISION_CODES["physical_selector_axiom_available"],
            "decision_code": DECISION_CODES["physical_selector_axiom_available"],
            "value": physical_selector_flag,
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
    ]
    gap_rows = [
        {
            "gap_id": GAP_CODES["atom_overlap_stress_orientation_candidate"],
            "gap_code": GAP_CODES["atom_overlap_stress_orientation_candidate"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["transition_to_stress_coupling_map"],
            "gap_code": GAP_CODES["transition_to_stress_coupling_map"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 1,
        },
        {
            "gap_id": GAP_CODES["semantic_transition_operation"],
            "gap_code": GAP_CODES["semantic_transition_operation"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["physical_selector_axiom"],
            "gap_code": GAP_CODES["physical_selector_axiom"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["four_dimensional_metric_reduction"],
            "gap_code": GAP_CODES["four_dimensional_metric_reduction"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["thermal_gravity_derivation"],
            "gap_code": GAP_CODES["thermal_gravity_derivation"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
    ]
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": obs[name],
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    return {
        "c59p3o": c59p3o,
        "c59p3v": c59p3v,
        "stress_gate": stress_gate,
        "stress_couple": stress_couple,
        "transition_sem": transition_sem,
        "coeff_rows": coeff_rows,
        "overlap_rows": overlap_rows,
        "score_rows": score_rows,
        "decision_rows": decision_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    coeff_table = table_from_rows(COEFF_COLUMNS, rows["coeff_rows"])
    overlap_table = table_from_rows(OVERLAP_COLUMNS, rows["overlap_rows"])
    score_table = table_from_rows(SCORE_COLUMNS, rows["score_rows"])
    decision_table = table_from_rows(DECISION_COLUMNS, rows["decision_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "atom_overlap_rows_exact": obs["selector_count"] == 2
        and obs["support_row_count"] == 12
        and obs["shared_support_atom_count"] == 6
        and obs["overlap_row_count"] == 14
        and obs["positive_overlap_edge_count"] == 7
        and obs["negative_overlap_edge_count"] == 7,
        "signed_tension_scores_exact": obs[
            "positive_signed_tension_score_scaled"
        ]
        == 13_946_765_269
        and obs["negative_signed_tension_score_scaled"] == -15_571_590_835
        and obs["signed_tension_score_difference_scaled"] == 29_518_356_104,
        "formal_orientation_candidate_selected": obs["selected_selector_id"] == 0
        and obs["selected_selector_code"] == SELECTOR_CODES["positive_volume_max"]
        and obs["atom_overlap_orientation_candidate_flag"] == 1,
        "physical_boundaries_preserved": obs["transition_stress_map_certified_flag"]
        == 0
        and obs["semantic_transition_operation_flag"] == 0
        and obs["physical_selector_axiom_flag"] == 0
        and obs["four_dimensional_metric_flag"] == 0
        and obs["thermal_gravity_flag"] == 0,
        "table_shapes_match": coeff_table.shape == (12, len(COEFF_COLUMNS))
        and overlap_table.shape == (14, len(OVERLAP_COLUMNS))
        and score_table.shape == (2, len(SCORE_COLUMNS))
        and decision_table.shape == (len(DECISION_CODES), len(DECISION_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "atom_overlap_stress_orientation_candidate",
        "summary": {
            "selector_count": obs["selector_count"],
            "shared_support_atom_count": obs["shared_support_atom_count"],
            "overlap_row_count": obs["overlap_row_count"],
            "positive_signed_tension_score_scaled": obs[
                "positive_signed_tension_score_scaled"
            ],
            "negative_signed_tension_score_scaled": obs[
                "negative_signed_tension_score_scaled"
            ],
            "signed_tension_score_difference_scaled": obs[
                "signed_tension_score_difference_scaled"
            ],
            "selected_selector_id": obs["selected_selector_id"],
            "selected_selector_code": obs["selected_selector_code"],
            "atom_overlap_orientation_candidate_flag": obs[
                "atom_overlap_orientation_candidate_flag"
            ],
            "transition_stress_map_certified_flag": obs[
                "transition_stress_map_certified_flag"
            ],
            "semantic_transition_operation_flag": obs[
                "semantic_transition_operation_flag"
            ],
            "physical_selector_axiom_flag": obs["physical_selector_axiom_flag"],
            "four_dimensional_metric_flag": obs["four_dimensional_metric_flag"],
            "thermal_gravity_flag": obs["thermal_gravity_flag"],
        },
        "selector_code_map": {
            str(value): key for key, value in SELECTOR_CODES.items()
        },
        "decision_code_map": {
            str(value): key for key, value in DECISION_CODES.items()
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "coeff_table_sha256": sha_array(coeff_table),
        "overlap_table_sha256": sha_array(overlap_table),
        "score_table_sha256": sha_array(score_table),
        "decision_table_sha256": sha_array(decision_table),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
        "overlap_text_sha256": sha_text(
            csv_text(OVERLAP_COLUMNS, rows["overlap_rows"])
        ),
    }
    c59p3a = {
        "schema": "long.c59p3a@1",
        "object": "atom_overlap_stress_orientation_candidate",
        "status": STATUS if all(checks.values()) else "LONG_C59P3A_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.c59p3a.report@1",
        "status": c59p3a["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_c59p3a joins the sign-dual plane support atoms to the "
            "atom-keyed finite stress graph and evaluates an exact signed-tension "
            "overlap score. The formal atom-overlap score selects the positive "
            "max-volume plane, but this is not yet a transition-to-stress map, "
            "semantic transition operation, or physical selector axiom."
        ),
        "stage_protocol": {
            "draft": "read long_c59p3o, long_c59p3v support, long_stress_gate, long_stress_couple, and long_transition_sem",
            "witness": "emit selector atom coefficients, induced stress-edge overlaps, scores, decisions, gaps, and observables",
            "coherence": "check overlap row counts, exact signed-tension scores, positive selection, and preserved transition/physical gaps",
            "closure": "certify the atom-overlap stress orientation candidate without promoting physical selector status",
            "emit": "write long_c59p3a artifacts and verifier hook",
        },
        "inputs": {
            "long_c59p3o": input_entry(
                LONG_C59P3O,
                {
                    "status": rows["c59p3o"].get("status"),
                    "certificate_sha256": rows["c59p3o"].get("certificate_sha256"),
                },
            ),
            "long_c59p3v": input_entry(
                LONG_C59P3V,
                {
                    "status": rows["c59p3v"].get("status"),
                    "certificate_sha256": rows["c59p3v"].get("certificate_sha256"),
                },
            ),
            "long_c59p3v_support": input_entry(LONG_C59P3V_SUPPORT),
            "long_stress_gate": input_entry(
                LONG_STRESS_GATE,
                {
                    "status": rows["stress_gate"].get("status"),
                    "certificate_sha256": rows["stress_gate"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_stress_edge": input_entry(LONG_STRESS_EDGE),
            "long_stress_couple": input_entry(
                LONG_STRESS_COUPLE,
                {
                    "status": rows["stress_couple"].get("status"),
                    "certificate_sha256": rows["stress_couple"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_transition_sem": input_entry(
                LONG_TRANSITION_SEM,
                {
                    "status": rows["transition_sem"].get("status"),
                    "certificate_sha256": rows["transition_sem"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "c59p3a": relpath(OUT_DIR / "c59p3a.json"),
            "coeff_csv": relpath(OUT_DIR / "coeff.csv"),
            "overlap_csv": relpath(OUT_DIR / "overlap.csv"),
            "score_csv": relpath(OUT_DIR / "score.csv"),
            "decision_csv": relpath(OUT_DIR / "decision.csv"),
            "gap_csv": relpath(OUT_DIR / "gap.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the sign-dual plane support atoms have a finite atom-overlap stress score",
                "the induced support subgraph has seven directed stress edges for each selector",
                "the signed-tension overlap score distinguishes the sign-dual pair",
                "the formal atom-overlap score selects the positive max-volume plane",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "a transition-to-stress coupling map",
                "semantic transition-operation realization",
                "acceptance of a physical selector axiom",
                "a four-dimensional metric reduction",
                "a physical source tensor or thermal-gravity derivation",
            ],
        },
        "next_highest_yield_item": (
            "Lift the atom-overlap orientation candidate into a true "
            "transition-to-stress coupling map, or certify why the transition "
            "schema still cannot consume the atom-keyed score."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.c59p3a.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.c59p3a.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "c59p3a": c59p3a,
        "coeff_csv": csv_text(COEFF_COLUMNS, rows["coeff_rows"]),
        "overlap_csv": csv_text(OVERLAP_COLUMNS, rows["overlap_rows"]),
        "score_csv": csv_text(SCORE_COLUMNS, rows["score_rows"]),
        "decision_csv": csv_text(DECISION_COLUMNS, rows["decision_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "coeff_table": coeff_table,
        "overlap_table": overlap_table,
        "score_table": score_table,
        "decision_table": decision_table,
        "gap_table": gap_table,
        "observable_table": observable_table,
        "cert": cert,
        "manifest": manifest,
        "report": report,
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
    obligations.sort(key=lambda row: str(row["id"]))
    index = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": obligations,
    }
    index["registry_sha256"] = self_hash(index, "registry_sha256")
    write_json(INDEX_PATH, index)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / "c59p3a.json", payloads["c59p3a"])
    (OUT_DIR / "coeff.csv").write_text(payloads["coeff_csv"], encoding="utf-8")
    (OUT_DIR / "overlap.csv").write_text(payloads["overlap_csv"], encoding="utf-8")
    (OUT_DIR / "score.csv").write_text(payloads["score_csv"], encoding="utf-8")
    (OUT_DIR / "decision.csv").write_text(
        payloads["decision_csv"], encoding="utf-8"
    )
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        coeff_table=payloads["coeff_table"],
        overlap_table=payloads["overlap_table"],
        score_table=payloads["score_table"],
        decision_table=payloads["decision_table"],
        gap_table=payloads["gap_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(OUT_DIR / "cert.json", payloads["cert"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    write_json(OUT_DIR / "report.json", payloads["report"])
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
                "certificate_sha256": report["certificate_sha256"],
                "summary": report["witness"]["summary"],
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
