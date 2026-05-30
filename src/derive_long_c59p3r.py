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


THEOREM_ID = "long_c59p3r"
STATUS = "LONG_C59P3R_RELATION_STRESS_EXTENSION_GATE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_C59P3B = PROOF_ROOT / "long_c59p3b" / "report.json"
LONG_C59P3B_BRIDGE = PROOF_ROOT / "long_c59p3b" / "bridge.csv"
LONG_C59P3B_OBS = PROOF_ROOT / "long_c59p3b" / "obs.csv"
LONG_RSEM = PROOF_ROOT / "long_rsem" / "report.json"
LONG_RSEM_RELATION = PROOF_ROOT / "long_rsem" / "relation.csv"
LONG_RSEM_TICK = PROOF_ROOT / "long_rsem" / "tick.csv"
LONG_RSEM_OBS = PROOF_ROOT / "long_rsem" / "obs.csv"
LONG_OPROM = PROOF_ROOT / "long_oprom" / "report.json"
LONG_OPROM_PROMOTION = PROOF_ROOT / "long_oprom" / "promotion.csv"
LONG_OPROM_OBS = PROOF_ROOT / "long_oprom" / "obs.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_c59p3r.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_c59p3r.py"

RELATION_STRESS_COLUMNS = [
    "relation_id",
    "visible_index",
    "transition_id",
    "guarded_relation_semantic_flag",
    "transition_row_present_flag",
    "operation_row_present_flag",
    "semantic_transition_flag",
    "operation_promotion_flag",
    "endpoint_atom_key_flag",
    "stress_atom_bridge_flag",
    "stress_score_consumed_flag",
    "relation_stress_extension_flag",
    "obstruction_code",
]
GATE_COLUMNS = [
    "gate_id",
    "gate_code",
    "present_flag",
    "required_flag",
    "row_count",
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

GATE_NAMES = [
    "guarded_relation_semantics",
    "operation_row_promotion",
    "semantic_transition_flags",
    "endpoint_atom_key",
    "stress_atom_bridge",
    "stress_score_consumption",
    "relation_stress_extension",
]
GATE_CODES = {name: index for index, name in enumerate(GATE_NAMES)}

GAP_NAMES = [
    "guarded_relation_semantic_law",
    "operation_row_promotion",
    "endpoint_atom_key",
    "stress_atom_bridge",
    "stress_score_consumption",
    "physical_selector_axiom",
    "thermal_gravity_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "relation_row_count",
    "guarded_relation_row_count",
    "guarded_semantic_tick_count",
    "multivalued_tick_count",
    "matched_transition_row_count",
    "operation_row_match_count",
    "semantic_transition_match_count",
    "promotion_success_count",
    "promotion_blocked_count",
    "operation_promotion_flag",
    "semantic_a985_operation_flag",
    "endpoint_atom_column_count",
    "raw_endpoint_stress_atom_bridge_flag",
    "current_schema_consumes_atom_score_flag",
    "relation_stress_extension_success_count",
    "relation_stress_extension_blocked_count",
    "relation_stress_extension_flag",
    "physical_selector_axiom_flag",
    "thermal_gravity_flag",
    "next_gap_code",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


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


def build_rows() -> dict[str, Any]:
    c59p3b = load_json(LONG_C59P3B)
    rsem = load_json(LONG_RSEM)
    oprom = load_json(LONG_OPROM)
    _, c59p3b_bridge_rows = read_csv_rows(LONG_C59P3B_BRIDGE)
    _, c59p3b_obs_rows = read_csv_rows(LONG_C59P3B_OBS)
    _, rsem_relation_rows = read_csv_rows(LONG_RSEM_RELATION)
    _, rsem_tick_rows = read_csv_rows(LONG_RSEM_TICK)
    _, rsem_obs_rows = read_csv_rows(LONG_RSEM_OBS)
    _, oprom_promotion_rows = read_csv_rows(LONG_OPROM_PROMOTION)
    _, oprom_obs_rows = read_csv_rows(LONG_OPROM_OBS)

    c_summary = summary(c59p3b)
    r_summary = summary(rsem)
    o_summary = summary(oprom)
    promotion_by_relation = {
        int(row["relation_id"]): row for row in oprom_promotion_rows
    }
    endpoint_atom_key_flag = int(c_summary["endpoint_atom_column_count"] > 0)
    stress_atom_bridge_flag = int(c_summary["raw_endpoint_stress_atom_bridge_flag"])
    stress_score_consumed_flag = int(
        c_summary["current_schema_consumes_atom_score_flag"]
    )
    relation_stress_rows = []
    for row in rsem_relation_rows:
        relation_id = int(row["relation_id"])
        promotion = promotion_by_relation[relation_id]
        operation_row_present = int(promotion["operation_row_present_flag"])
        semantic_transition = int(promotion["semantic_transition_flag"])
        operation_promotion = int(promotion["operation_promotion_flag"])
        extension_flag = int(
            operation_promotion == 1
            and endpoint_atom_key_flag == 1
            and stress_atom_bridge_flag == 1
            and stress_score_consumed_flag == 1
        )
        relation_stress_rows.append(
            {
                "relation_id": relation_id,
                "visible_index": int(row["visible_index"]),
                "transition_id": int(row["transition_id"]),
                "guarded_relation_semantic_flag": int(
                    row["guarded_relation_semantic_flag"]
                ),
                "transition_row_present_flag": int(
                    promotion["transition_row_present_flag"]
                ),
                "operation_row_present_flag": operation_row_present,
                "semantic_transition_flag": semantic_transition,
                "operation_promotion_flag": operation_promotion,
                "endpoint_atom_key_flag": endpoint_atom_key_flag,
                "stress_atom_bridge_flag": stress_atom_bridge_flag,
                "stress_score_consumed_flag": stress_score_consumed_flag,
                "relation_stress_extension_flag": extension_flag,
                "obstruction_code": int(extension_flag == 0),
            }
        )

    extension_success_count = sum(
        row["relation_stress_extension_flag"] for row in relation_stress_rows
    )
    extension_blocked_count = len(relation_stress_rows) - extension_success_count
    relation_stress_extension_flag = int(extension_success_count == len(relation_stress_rows))
    obs = {
        "input_report_count": 3,
        "input_certified_count": int(certified(c59p3b))
        + int(certified(rsem))
        + int(certified(oprom)),
        "relation_row_count": int(r_summary["relation_row_count"]),
        "guarded_relation_row_count": int(
            o_summary["guarded_relation_row_count"]
        ),
        "guarded_semantic_tick_count": int(r_summary["guarded_semantic_tick_count"]),
        "multivalued_tick_count": int(r_summary["multivalued_tick_count"]),
        "matched_transition_row_count": int(o_summary["matched_transition_row_count"]),
        "operation_row_match_count": int(o_summary["operation_row_match_count"]),
        "semantic_transition_match_count": int(
            o_summary["semantic_transition_match_count"]
        ),
        "promotion_success_count": int(o_summary["promotion_success_count"]),
        "promotion_blocked_count": int(o_summary["promotion_blocked_count"]),
        "operation_promotion_flag": int(o_summary["operation_promotion_flag"]),
        "semantic_a985_operation_flag": int(o_summary["semantic_a985_operation_flag"]),
        "endpoint_atom_column_count": int(c_summary["endpoint_atom_column_count"]),
        "raw_endpoint_stress_atom_bridge_flag": stress_atom_bridge_flag,
        "current_schema_consumes_atom_score_flag": stress_score_consumed_flag,
        "relation_stress_extension_success_count": extension_success_count,
        "relation_stress_extension_blocked_count": extension_blocked_count,
        "relation_stress_extension_flag": relation_stress_extension_flag,
        "physical_selector_axiom_flag": int(o_summary["physical_selector_axiom_flag"]),
        "thermal_gravity_flag": 0,
        "next_gap_code": GAP_CODES["operation_row_promotion"],
    }
    gate_rows = [
        {
            "gate_id": GATE_CODES["guarded_relation_semantics"],
            "gate_code": GATE_CODES["guarded_relation_semantics"],
            "present_flag": int(r_summary["relation_semantic_law_flag"]),
            "required_flag": 1,
            "row_count": obs["guarded_relation_row_count"],
            "certified_flag": 1,
            "obstruction_flag": 0,
        },
        {
            "gate_id": GATE_CODES["operation_row_promotion"],
            "gate_code": GATE_CODES["operation_row_promotion"],
            "present_flag": obs["operation_promotion_flag"],
            "required_flag": 1,
            "row_count": obs["operation_row_match_count"],
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "gate_id": GATE_CODES["semantic_transition_flags"],
            "gate_code": GATE_CODES["semantic_transition_flags"],
            "present_flag": int(obs["semantic_transition_match_count"] > 0),
            "required_flag": 1,
            "row_count": obs["semantic_transition_match_count"],
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "gate_id": GATE_CODES["endpoint_atom_key"],
            "gate_code": GATE_CODES["endpoint_atom_key"],
            "present_flag": endpoint_atom_key_flag,
            "required_flag": 1,
            "row_count": obs["endpoint_atom_column_count"],
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "gate_id": GATE_CODES["stress_atom_bridge"],
            "gate_code": GATE_CODES["stress_atom_bridge"],
            "present_flag": stress_atom_bridge_flag,
            "required_flag": 1,
            "row_count": stress_atom_bridge_flag,
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "gate_id": GATE_CODES["stress_score_consumption"],
            "gate_code": GATE_CODES["stress_score_consumption"],
            "present_flag": stress_score_consumed_flag,
            "required_flag": 1,
            "row_count": stress_score_consumed_flag,
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "gate_id": GATE_CODES["relation_stress_extension"],
            "gate_code": GATE_CODES["relation_stress_extension"],
            "present_flag": relation_stress_extension_flag,
            "required_flag": 1,
            "row_count": extension_success_count,
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
    ]
    gap_rows = [
        {
            "gap_id": GAP_CODES["guarded_relation_semantic_law"],
            "gap_code": GAP_CODES["guarded_relation_semantic_law"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["operation_row_promotion"],
            "gap_code": GAP_CODES["operation_row_promotion"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 1,
        },
        {
            "gap_id": GAP_CODES["endpoint_atom_key"],
            "gap_code": GAP_CODES["endpoint_atom_key"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["stress_atom_bridge"],
            "gap_code": GAP_CODES["stress_atom_bridge"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["stress_score_consumption"],
            "gap_code": GAP_CODES["stress_score_consumption"],
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
        "c59p3b": c59p3b,
        "rsem": rsem,
        "oprom": oprom,
        "c59p3b_bridge_rows": c59p3b_bridge_rows,
        "c59p3b_obs_rows": c59p3b_obs_rows,
        "rsem_tick_rows": rsem_tick_rows,
        "rsem_obs_rows": rsem_obs_rows,
        "oprom_obs_rows": oprom_obs_rows,
        "relation_stress_rows": relation_stress_rows,
        "gate_rows": gate_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    relation_stress_table = table_from_rows(
        RELATION_STRESS_COLUMNS, rows["relation_stress_rows"]
    )
    gate_table = table_from_rows(GATE_COLUMNS, rows["gate_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "relation_semantics_present": obs["relation_row_count"] == 59
        and obs["guarded_relation_row_count"] == 59
        and obs["guarded_semantic_tick_count"] == 20
        and obs["multivalued_tick_count"] == 13
        and obs["matched_transition_row_count"] == 59,
        "operation_promotion_absent": obs["operation_row_match_count"] == 0
        and obs["semantic_transition_match_count"] == 0
        and obs["promotion_success_count"] == 0
        and obs["promotion_blocked_count"] == 59
        and obs["operation_promotion_flag"] == 0
        and obs["semantic_a985_operation_flag"] == 0,
        "stress_bridge_absent": obs["endpoint_atom_column_count"] == 0
        and obs["raw_endpoint_stress_atom_bridge_flag"] == 0
        and obs["current_schema_consumes_atom_score_flag"] == 0,
        "relation_stress_extension_blocked": obs[
            "relation_stress_extension_success_count"
        ]
        == 0
        and obs["relation_stress_extension_blocked_count"] == 59
        and obs["relation_stress_extension_flag"] == 0,
        "physical_boundaries_preserved": obs["physical_selector_axiom_flag"] == 0
        and obs["thermal_gravity_flag"] == 0,
        "table_shapes_match": relation_stress_table.shape
        == (59, len(RELATION_STRESS_COLUMNS))
        and gate_table.shape == (len(GATE_CODES), len(GATE_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "relation_valued_stress_extension_gate",
        "summary": {
            "relation_row_count": obs["relation_row_count"],
            "guarded_semantic_tick_count": obs["guarded_semantic_tick_count"],
            "operation_row_match_count": obs["operation_row_match_count"],
            "semantic_transition_match_count": obs["semantic_transition_match_count"],
            "endpoint_atom_column_count": obs["endpoint_atom_column_count"],
            "raw_endpoint_stress_atom_bridge_flag": obs[
                "raw_endpoint_stress_atom_bridge_flag"
            ],
            "current_schema_consumes_atom_score_flag": obs[
                "current_schema_consumes_atom_score_flag"
            ],
            "relation_stress_extension_success_count": obs[
                "relation_stress_extension_success_count"
            ],
            "relation_stress_extension_blocked_count": obs[
                "relation_stress_extension_blocked_count"
            ],
            "relation_stress_extension_flag": obs["relation_stress_extension_flag"],
        },
        "gate_code_map": {str(value): key for key, value in GATE_CODES.items()},
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "relation_stress_table_sha256": sha_array(relation_stress_table),
        "relation_stress_text_sha256": sha_text(
            csv_text(RELATION_STRESS_COLUMNS, rows["relation_stress_rows"])
        ),
        "gate_table_sha256": sha_array(gate_table),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    c59p3r = {
        "schema": "long.c59p3r@1",
        "object": "relation_valued_stress_extension_gate",
        "status": STATUS if all(checks.values()) else "LONG_C59P3R_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.c59p3r.report@1",
        "status": c59p3r["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_c59p3r tests whether the guarded relation-valued tick law can "
            "be extended to stress scoring. All 59 relation witnesses are "
            "present and matched to guarded transitions, but zero have operation "
            "rows, zero have semantic transition flags, and the current boundary "
            "still has no endpoint atom key or stress-atom bridge. The relation "
            "law therefore remains a guarded transition law, not a stress-scored "
            "operation law."
        ),
        "stage_protocol": {
            "draft": "read long_c59p3b, long_rsem, and long_oprom",
            "witness": "emit per-relation stress-extension rows, gate rows, gap rows, and observables",
            "coherence": "check relation semantics, operation-promotion absence, stress-bridge absence, and physical exclusions",
            "closure": "certify the current relation-valued stress-extension gate",
            "emit": "write long_c59p3r artifacts and verifier hook",
        },
        "inputs": {
            "long_c59p3b": input_entry(
                LONG_C59P3B,
                {
                    "status": rows["c59p3b"].get("status"),
                    "certificate_sha256": rows["c59p3b"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_c59p3b_bridge": input_entry(LONG_C59P3B_BRIDGE),
            "long_c59p3b_obs": input_entry(LONG_C59P3B_OBS),
            "long_rsem": input_entry(
                LONG_RSEM,
                {
                    "status": rows["rsem"].get("status"),
                    "certificate_sha256": rows["rsem"].get("certificate_sha256"),
                },
            ),
            "long_rsem_relation": input_entry(LONG_RSEM_RELATION),
            "long_rsem_tick": input_entry(LONG_RSEM_TICK),
            "long_rsem_obs": input_entry(LONG_RSEM_OBS),
            "long_oprom": input_entry(
                LONG_OPROM,
                {
                    "status": rows["oprom"].get("status"),
                    "certificate_sha256": rows["oprom"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_oprom_promotion": input_entry(LONG_OPROM_PROMOTION),
            "long_oprom_obs": input_entry(LONG_OPROM_OBS),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "c59p3r": relpath(OUT_DIR / "c59p3r.json"),
            "relation_stress_csv": relpath(OUT_DIR / "relation_stress.csv"),
            "gate_csv": relpath(OUT_DIR / "gate.csv"),
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
                "the guarded relation-valued tick law supplies 59 matched transition witnesses",
                "zero of the 59 relation witnesses is promoted to an operation row",
                "zero of the 59 relation witnesses has a semantic transition flag",
                "the current boundary has no endpoint atom key or stress-atom bridge for the relation law",
                "zero relation witnesses are extended to stress scoring under the current boundary",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "operation rows for the 59 guarded relation witnesses",
                "a relation-valued stress-transition law that bypasses operation rows by explicit rule",
                "a physical selector axiom",
                "a four-dimensional metric reduction or thermal-gravity derivation",
            ],
        },
        "next_highest_yield_item": (
            "Construct operation rows for the 59 guarded relation witnesses, or "
            "emit an explicit relation-valued stress-transition law that names "
            "how multivalued witnesses push forward into stress atoms."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.c59p3r.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.c59p3r.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "c59p3r": c59p3r,
        "relation_stress_csv": csv_text(
            RELATION_STRESS_COLUMNS, rows["relation_stress_rows"]
        ),
        "gate_csv": csv_text(GATE_COLUMNS, rows["gate_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "relation_stress_table": relation_stress_table,
        "gate_table": gate_table,
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
    write_json(OUT_DIR / "c59p3r.json", payloads["c59p3r"])
    (OUT_DIR / "relation_stress.csv").write_text(
        payloads["relation_stress_csv"], encoding="utf-8"
    )
    (OUT_DIR / "gate.csv").write_text(payloads["gate_csv"], encoding="utf-8")
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        relation_stress_table=payloads["relation_stress_table"],
        gate_table=payloads["gate_table"],
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
