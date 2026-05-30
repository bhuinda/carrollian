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


THEOREM_ID = "long_rtick"
STATUS = "LONG_RTICK_RELATION_VALUED_TICK_COVER_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_GCLK = PROOF_ROOT / "long_gclk" / "report.json"
LONG_GCLK_CLOCK = PROOF_ROOT / "long_gclk" / "clock.csv"
LONG_ABMAP = PROOF_ROOT / "long_abmap" / "report.json"
LONG_ABMAP_EDGE = PROOF_ROOT / "long_abmap" / "edge.csv"
LONG_ABMAP_MATCH = PROOF_ROOT / "long_abmap" / "match.csv"
LONG_TRANSITION_SEM = PROOF_ROOT / "long_transition_sem" / "report.json"
LONG_TRANSITION_CSV = PROOF_ROOT / "long_transition_sem" / "transition.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_rtick.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_rtick.py"

RELATION_ORIENTATION_UNDIRECTED = 1

TICK_COLUMNS = [
    "visible_index",
    "source_atom_id",
    "target_atom_id",
    "relation_match_count",
    "covered_flag",
    "singleton_flag",
    "multivalued_flag",
    "raw_backed_match_count",
    "unit_time_match_count",
    "contact_lift_match_count",
    "semantic_match_count",
    "operation_row_match_count",
]
RELATION_COLUMNS = [
    "relation_id",
    "visible_index",
    "source_atom_id",
    "target_atom_id",
    "left_step_atom_id",
    "right_step_atom_id",
    "left_basis_id",
    "right_basis_id",
    "transition_id",
    "left_raw_row_id",
    "right_raw_row_id",
    "normal_form_delta_t",
    "contact_lift_flag",
    "endpoint_pair_raw_row_flag",
    "operation_row_id",
    "semantic_transition_flag",
]
POLICY_COLUMNS = [
    "policy_id",
    "policy_code",
    "present_flag",
    "certified_flag",
    "required_for_semantic_flag",
    "obstruction_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

POLICY_NAMES = [
    "finite_relation_cover",
    "single_valued_atom_basis_functor",
    "relation_valued_transition_semantic_law",
    "semantic_a985_operation_rows",
    "physical_selector_axiom",
]
POLICY_CODES = {name: index for index, name in enumerate(POLICY_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "affine_tick_count",
    "relation_row_count",
    "covered_tick_count",
    "singleton_tick_count",
    "multivalued_tick_count",
    "max_relation_multiplicity",
    "raw_backed_relation_count",
    "unit_time_relation_count",
    "contact_lift_relation_count",
    "semantic_relation_count",
    "operation_row_materialized_count",
    "relation_cover_certified_flag",
    "single_valued_functor_flag",
    "relation_valued_semantic_law_flag",
    "semantic_transition_operation_flag",
    "physical_selector_axiom_flag",
    "gr_source_ready_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def summary(report: dict[str, Any]) -> dict[str, Any]:
    witness = report.get("witness")
    if not isinstance(witness, dict):
        raise AssertionError("witness missing")
    out = witness.get("summary")
    if not isinstance(out, dict):
        raise AssertionError("summary missing")
    return out


def certified(report: dict[str, Any]) -> bool:
    return report.get("all_checks_pass") is True and "CERTIFIED" in str(
        report.get("status", "")
    )


def build_rows() -> dict[str, Any]:
    gclk = load_json(LONG_GCLK)
    abmap = load_json(LONG_ABMAP)
    transition_sem = load_json(LONG_TRANSITION_SEM)
    clock_rows_raw = read_csv(LONG_GCLK_CLOCK)
    edge_rows_raw = read_csv(LONG_ABMAP_EDGE)
    match_rows_raw = read_csv(LONG_ABMAP_MATCH)
    transition_rows_raw = read_csv(LONG_TRANSITION_CSV)
    abmap_s = summary(abmap)
    transition_s = summary(transition_sem)

    transition_by_id = {
        int(row["transition_id"]): row for row in transition_rows_raw
    }
    undirected_edges = [
        row
        for row in edge_rows_raw
        if int(row["orientation_code"]) == RELATION_ORIENTATION_UNDIRECTED
    ]
    undirected_matches = [
        row
        for row in match_rows_raw
        if int(row["orientation_code"]) == RELATION_ORIENTATION_UNDIRECTED
    ]
    relation_rows = []
    matches_by_tick: dict[int, list[dict[str, int]]] = {
        int(row["visible_index"]): [] for row in clock_rows_raw
    }
    for match in undirected_matches:
        transition = transition_by_id[int(match["transition_id"])]
        relation = {
            "relation_id": len(relation_rows),
            "visible_index": int(match["visible_index"]),
            "source_atom_id": int(match["source_atom_id"]),
            "target_atom_id": int(match["target_atom_id"]),
            "left_step_atom_id": int(match["left_step_atom_id"]),
            "right_step_atom_id": int(match["right_step_atom_id"]),
            "left_basis_id": int(match["left_basis_id"]),
            "right_basis_id": int(match["right_basis_id"]),
            "transition_id": int(match["transition_id"]),
            "left_raw_row_id": int(transition["left_raw_row_id"]),
            "right_raw_row_id": int(transition["right_raw_row_id"]),
            "normal_form_delta_t": int(transition["normal_form_delta_t"]),
            "contact_lift_flag": int(transition["contact_lift_flag"]),
            "endpoint_pair_raw_row_flag": int(transition["endpoint_pair_raw_row_flag"]),
            "operation_row_id": int(transition["operation_row_id"]),
            "semantic_transition_flag": int(transition["semantic_transition_flag"]),
        }
        relation_rows.append(relation)
        matches_by_tick[relation["visible_index"]].append(relation)

    tick_rows = []
    for clock in clock_rows_raw:
        visible_index = int(clock["visible_index"])
        matches = matches_by_tick[visible_index]
        tick_rows.append(
            {
                "visible_index": visible_index,
                "source_atom_id": int(clock["source_atom_id"]),
                "target_atom_id": int(clock["target_atom_id"]),
                "relation_match_count": len(matches),
                "covered_flag": int(bool(matches)),
                "singleton_flag": int(len(matches) == 1),
                "multivalued_flag": int(len(matches) > 1),
                "raw_backed_match_count": sum(
                    int(row["endpoint_pair_raw_row_flag"] == 1) for row in matches
                ),
                "unit_time_match_count": sum(
                    int(row["normal_form_delta_t"] == 1) for row in matches
                ),
                "contact_lift_match_count": sum(
                    int(row["contact_lift_flag"] == 1) for row in matches
                ),
                "semantic_match_count": sum(
                    int(row["semantic_transition_flag"] == 1) for row in matches
                ),
                "operation_row_match_count": sum(
                    int(row["operation_row_id"] >= 0) for row in matches
                ),
            }
        )

    relation_cover = int(all(row["covered_flag"] == 1 for row in tick_rows))
    single_valued_functor = int(abmap_s["atom_to_basis_function_certified_flag"])
    relation_semantic_law = 0
    semantic_operation = int(transition_s["semantic_transition_operation_flag"])
    physical_selector = 0
    policy_rows = [
        {
            "policy_id": POLICY_CODES["finite_relation_cover"],
            "policy_code": POLICY_CODES["finite_relation_cover"],
            "present_flag": relation_cover,
            "certified_flag": relation_cover,
            "required_for_semantic_flag": 1,
            "obstruction_flag": 0,
        },
        {
            "policy_id": POLICY_CODES["single_valued_atom_basis_functor"],
            "policy_code": POLICY_CODES["single_valued_atom_basis_functor"],
            "present_flag": single_valued_functor,
            "certified_flag": single_valued_functor,
            "required_for_semantic_flag": 0,
            "obstruction_flag": int(single_valued_functor == 0),
        },
        {
            "policy_id": POLICY_CODES["relation_valued_transition_semantic_law"],
            "policy_code": POLICY_CODES["relation_valued_transition_semantic_law"],
            "present_flag": relation_semantic_law,
            "certified_flag": relation_semantic_law,
            "required_for_semantic_flag": 1,
            "obstruction_flag": int(relation_semantic_law == 0),
        },
        {
            "policy_id": POLICY_CODES["semantic_a985_operation_rows"],
            "policy_code": POLICY_CODES["semantic_a985_operation_rows"],
            "present_flag": semantic_operation,
            "certified_flag": semantic_operation,
            "required_for_semantic_flag": 1,
            "obstruction_flag": int(semantic_operation == 0),
        },
        {
            "policy_id": POLICY_CODES["physical_selector_axiom"],
            "policy_code": POLICY_CODES["physical_selector_axiom"],
            "present_flag": physical_selector,
            "certified_flag": physical_selector,
            "required_for_semantic_flag": 0,
            "obstruction_flag": int(physical_selector == 0),
        },
    ]
    obs = {
        "input_report_count": 3,
        "input_certified_count": sum(
            certified(report) for report in [gclk, abmap, transition_sem]
        ),
        "affine_tick_count": len(tick_rows),
        "relation_row_count": len(relation_rows),
        "covered_tick_count": sum(row["covered_flag"] for row in tick_rows),
        "singleton_tick_count": sum(row["singleton_flag"] for row in tick_rows),
        "multivalued_tick_count": sum(row["multivalued_flag"] for row in tick_rows),
        "max_relation_multiplicity": max(row["relation_match_count"] for row in tick_rows),
        "raw_backed_relation_count": sum(
            row["endpoint_pair_raw_row_flag"] for row in relation_rows
        ),
        "unit_time_relation_count": sum(
            int(row["normal_form_delta_t"] == 1) for row in relation_rows
        ),
        "contact_lift_relation_count": sum(
            row["contact_lift_flag"] for row in relation_rows
        ),
        "semantic_relation_count": sum(
            row["semantic_transition_flag"] for row in relation_rows
        ),
        "operation_row_materialized_count": sum(
            int(row["operation_row_id"] >= 0) for row in relation_rows
        ),
        "relation_cover_certified_flag": relation_cover,
        "single_valued_functor_flag": single_valued_functor,
        "relation_valued_semantic_law_flag": relation_semantic_law,
        "semantic_transition_operation_flag": semantic_operation,
        "physical_selector_axiom_flag": physical_selector,
        "gr_source_ready_flag": 0,
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": obs[name],
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    return {
        "gclk": gclk,
        "abmap": abmap,
        "transition_sem": transition_sem,
        "undirected_edges": undirected_edges,
        "tick_rows": tick_rows,
        "relation_rows": relation_rows,
        "policy_rows": policy_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    tick_table = table_from_rows(TICK_COLUMNS, rows["tick_rows"])
    relation_table = table_from_rows(RELATION_COLUMNS, rows["relation_rows"])
    policy_table = table_from_rows(POLICY_COLUMNS, rows["policy_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"] == obs["input_certified_count"],
        "relation_cover_is_complete": obs["affine_tick_count"] == 20
        and obs["relation_row_count"] == 59
        and obs["covered_tick_count"] == 20
        and obs["relation_cover_certified_flag"] == 1,
        "relation_cover_is_multivalued": obs["singleton_tick_count"] == 7
        and obs["multivalued_tick_count"] == 13
        and obs["max_relation_multiplicity"] == 6
        and obs["single_valued_functor_flag"] == 0,
        "relation_witnesses_are_guarded_raw_unit_ticks": obs[
            "raw_backed_relation_count"
        ]
        == 59
        and obs["unit_time_relation_count"] == 59
        and obs["contact_lift_relation_count"] == 59,
        "semantic_promotion_is_absent": obs["semantic_relation_count"] == 0
        and obs["operation_row_materialized_count"] == 0
        and obs["relation_valued_semantic_law_flag"] == 0
        and obs["semantic_transition_operation_flag"] == 0
        and obs["physical_selector_axiom_flag"] == 0
        and obs["gr_source_ready_flag"] == 0,
        "table_shapes_match": tick_table.shape == (20, len(TICK_COLUMNS))
        and relation_table.shape == (59, len(RELATION_COLUMNS))
        and policy_table.shape == (len(POLICY_CODES), len(POLICY_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "relation_valued_tick_cover",
        "summary": {
            "affine_tick_count": obs["affine_tick_count"],
            "relation_row_count": obs["relation_row_count"],
            "covered_tick_count": obs["covered_tick_count"],
            "singleton_tick_count": obs["singleton_tick_count"],
            "multivalued_tick_count": obs["multivalued_tick_count"],
            "max_relation_multiplicity": obs["max_relation_multiplicity"],
            "raw_backed_relation_count": obs["raw_backed_relation_count"],
            "unit_time_relation_count": obs["unit_time_relation_count"],
            "relation_cover_certified_flag": obs["relation_cover_certified_flag"],
            "relation_valued_semantic_law_flag": obs[
                "relation_valued_semantic_law_flag"
            ],
            "semantic_transition_operation_flag": obs[
                "semantic_transition_operation_flag"
            ],
            "gr_source_ready_flag": obs["gr_source_ready_flag"],
        },
        "policy_code_map": {str(value): key for key, value in POLICY_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "tick_table_sha256": sha_array(tick_table),
        "relation_table_sha256": sha_array(relation_table),
        "relation_text_sha256": sha_text(
            csv_text(RELATION_COLUMNS, rows["relation_rows"])
        ),
        "policy_table_sha256": sha_array(policy_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    rtick = {
        "schema": "long.rtick@1",
        "object": "relation_valued_tick_cover",
        "status": STATUS if all(checks.values()) else "LONG_RTICK_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.rtick.report@1",
        "status": rtick["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_rtick certifies the relation-valued finite tick cover exposed "
            "by long_abmap. The affine golden C10 clock has 20 visible two-step "
            "ticks, and each tick has at least one undirected raw-backed "
            "contact-lift transition witness with normal-form delta_t=1. The "
            "cover is multivalued, not a single-valued atom-to-basis functor, "
            "and no relation-valued semantic law or A985 operation rows promote "
            "the cover to semantic transition operations."
        ),
        "stage_protocol": {
            "draft": "read long_gclk, long_abmap, long_transition_sem, affine clock rows, relation cover rows, and transition rows",
            "witness": "emit per-tick cover rows, relation witness rows, policy rows, and observables",
            "coherence": "check complete 20-tick relation cover, 59 raw-backed unit-time relation witnesses, multivaluedness, and semantic-operation absence",
            "closure": "certify guarded relation-valued tick coverage while preserving the missing semantic-law boundary",
            "emit": "write long_rtick artifacts and verifier hook",
        },
        "inputs": {
            "long_gclk": input_entry(
                LONG_GCLK,
                {
                    "status": rows["gclk"].get("status"),
                    "certificate_sha256": rows["gclk"].get("certificate_sha256"),
                },
            ),
            "long_gclk_clock": input_entry(LONG_GCLK_CLOCK),
            "long_abmap": input_entry(
                LONG_ABMAP,
                {
                    "status": rows["abmap"].get("status"),
                    "certificate_sha256": rows["abmap"].get("certificate_sha256"),
                },
            ),
            "long_abmap_edge": input_entry(LONG_ABMAP_EDGE),
            "long_abmap_match": input_entry(LONG_ABMAP_MATCH),
            "long_transition_sem": input_entry(
                LONG_TRANSITION_SEM,
                {
                    "status": rows["transition_sem"].get("status"),
                    "certificate_sha256": rows["transition_sem"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_transition_csv": input_entry(LONG_TRANSITION_CSV),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "rtick": relpath(OUT_DIR / "rtick.json"),
            "tick_csv": relpath(OUT_DIR / "tick.csv"),
            "relation_csv": relpath(OUT_DIR / "relation.csv"),
            "policy_csv": relpath(OUT_DIR / "policy.csv"),
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
                "every one of the 20 affine golden visible two-step ticks has at least one undirected transition-relation witness",
                "the relation cover has 59 total transition witnesses",
                "all 59 witnesses are endpoint-raw-backed, contact-lift-backed, and normal-form unit-time transitions",
                "the relation cover is multivalued: 7 singleton ticks, 13 multivalued ticks, maximum multiplicity 6",
                "the relation cover is a guarded finite transition relation, not a single-valued atom-to-basis functor",
                "no relation-valued semantic transition law or semantic A985 operation row is certified for the cover",
            ],
            "does_not_certify_because_out_of_scope": [
                "that relation-valued ticks are acceptable physical transition semantics",
                "a single-valued atom-to-basis functor",
                "semantic A985 transition-operation realization for the affine clock",
                "a physical selector axiom",
                "that the affine golden clock is physical time",
                "a selected 1+3 Lorentzian spacetime boundary",
                "a physical stress-energy tensor or Einstein equation",
                "a derivation of general relativity from A985 alone",
            ],
        },
        "next_highest_yield_item": (
            "Decide the relation-valued semantic law: either certify a law that "
            "allows these 59 guarded relation witnesses to serve as transition "
            "semantics, or keep the golden branch blocked at semantic promotion."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.rtick.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.rtick.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "rtick": rtick,
        "tick_csv": csv_text(TICK_COLUMNS, rows["tick_rows"]),
        "relation_csv": csv_text(RELATION_COLUMNS, rows["relation_rows"]),
        "policy_csv": csv_text(POLICY_COLUMNS, rows["policy_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "tick_table": tick_table,
        "relation_table": relation_table,
        "policy_table": policy_table,
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
    write_json(OUT_DIR / "rtick.json", payloads["rtick"])
    (OUT_DIR / "tick.csv").write_text(payloads["tick_csv"], encoding="utf-8")
    (OUT_DIR / "relation.csv").write_text(payloads["relation_csv"], encoding="utf-8")
    (OUT_DIR / "policy.csv").write_text(payloads["policy_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        tick_table=payloads["tick_table"],
        relation_table=payloads["relation_table"],
        policy_table=payloads["policy_table"],
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
