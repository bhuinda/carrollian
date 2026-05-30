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


THEOREM_ID = "long_c59p3f"
STATUS = "LONG_C59P3F_FORMAL_SELECTOR_STRESS_PUSHFORWARD_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_C59P3I = PROOF_ROOT / "long_c59p3i" / "report.json"
LONG_C59P3R = PROOF_ROOT / "long_c59p3r" / "report.json"
LONG_RSEM = PROOF_ROOT / "long_rsem" / "report.json"
LONG_RSEM_TICK = PROOF_ROOT / "long_rsem" / "tick.csv"
LONG_RSEM_RELATION = PROOF_ROOT / "long_rsem" / "relation.csv"
LONG_STRESS_GATE = PROOF_ROOT / "long_stress_gate" / "report.json"
LONG_STRESS_EDGE = PROOF_ROOT / "long_stress_gate" / "stress_edge.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_c59p3f.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_c59p3f.py"

ASSIGNMENT_COLUMNS = [
    "relation_id",
    "visible_index",
    "transition_id",
    "source_atom_id",
    "target_atom_id",
    "rule_code",
    "stress_edge_id",
    "stress_source_atom",
    "stress_target_atom",
    "signed_tension_scaled",
    "abs_tension_scaled",
    "formal_pushforward_flag",
    "operation_row_present_flag",
    "physical_selector_axiom_flag",
]
RULE_COLUMNS = [
    "rule_code",
    "rule_name_code",
    "assignment_count",
    "formal_rule_flag",
    "physical_selector_axiom_flag",
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

RULE_NAMES = [
    "direct_stress_edge",
    "reverse_stress_edge",
    "max_abs_incident_stress_edge",
]
RULE_CODES = {name: index for index, name in enumerate(RULE_NAMES)}

GAP_NAMES = [
    "formal_selector_stress_pushforward",
    "operation_row_promotion",
    "semantic_transition_flags",
    "physical_selector_axiom",
    "four_dimensional_metric_reduction",
    "thermal_gravity_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "relation_row_count",
    "stress_edge_row_count",
    "assigned_relation_count",
    "direct_assignment_count",
    "reverse_assignment_count",
    "fallback_assignment_count",
    "unique_stress_edge_count",
    "max_assignment_multiplicity",
    "formal_pushforward_flag",
    "operation_row_match_count",
    "semantic_transition_match_count",
    "physical_selector_axiom_flag",
    "four_dimensional_metric_flag",
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


def choose_fallback_edge(
    source: int, target: int, stress_rows: list[dict[str, str]]
) -> dict[str, str]:
    candidates = [
        row
        for row in stress_rows
        if int(row["source_atom"]) in {source, target}
        or int(row["target_atom"]) in {source, target}
    ]
    if not candidates:
        raise AssertionError("no incident stress candidate")
    return sorted(
        candidates,
        key=lambda row: (
            -abs(int(row["signed_tension_scaled"])),
            int(row["stress_edge_id"]),
        ),
    )[0]


def build_rows() -> dict[str, Any]:
    c59p3i = load_json(LONG_C59P3I)
    c59p3r = load_json(LONG_C59P3R)
    rsem = load_json(LONG_RSEM)
    stress_gate = load_json(LONG_STRESS_GATE)
    _, tick_rows_raw = read_csv_rows(LONG_RSEM_TICK)
    _, relation_rows_raw = read_csv_rows(LONG_RSEM_RELATION)
    _, stress_rows_raw = read_csv_rows(LONG_STRESS_EDGE)
    c59p3r_summary = summary(c59p3r)

    tick_by_visible = {int(row["visible_index"]): row for row in tick_rows_raw}
    stress_by_pair: dict[tuple[int, int], dict[str, str]] = {}
    for row in stress_rows_raw:
        stress_by_pair[(int(row["source_atom"]), int(row["target_atom"]))] = row

    assignment_rows = []
    for row in relation_rows_raw:
        visible_index = int(row["visible_index"])
        tick = tick_by_visible[visible_index]
        source = int(tick["source_atom_id"])
        target = int(tick["target_atom_id"])
        direct = stress_by_pair.get((source, target))
        reverse = stress_by_pair.get((target, source))
        if direct is not None:
            stress_edge = direct
            rule_code = RULE_CODES["direct_stress_edge"]
        elif reverse is not None:
            stress_edge = reverse
            rule_code = RULE_CODES["reverse_stress_edge"]
        else:
            stress_edge = choose_fallback_edge(source, target, stress_rows_raw)
            rule_code = RULE_CODES["max_abs_incident_stress_edge"]
        signed_tension = int(stress_edge["signed_tension_scaled"])
        assignment_rows.append(
            {
                "relation_id": int(row["relation_id"]),
                "visible_index": visible_index,
                "transition_id": int(row["transition_id"]),
                "source_atom_id": source,
                "target_atom_id": target,
                "rule_code": rule_code,
                "stress_edge_id": int(stress_edge["stress_edge_id"]),
                "stress_source_atom": int(stress_edge["source_atom"]),
                "stress_target_atom": int(stress_edge["target_atom"]),
                "signed_tension_scaled": signed_tension,
                "abs_tension_scaled": abs(signed_tension),
                "formal_pushforward_flag": 1,
                "operation_row_present_flag": 0,
                "physical_selector_axiom_flag": 0,
            }
        )

    rule_rows = []
    for name, code in RULE_CODES.items():
        rule_rows.append(
            {
                "rule_code": code,
                "rule_name_code": code,
                "assignment_count": sum(
                    int(row["rule_code"] == code) for row in assignment_rows
                ),
                "formal_rule_flag": 1,
                "physical_selector_axiom_flag": 0,
            }
        )

    counts_by_edge: dict[int, int] = {}
    for row in assignment_rows:
        edge_id = int(row["stress_edge_id"])
        counts_by_edge[edge_id] = counts_by_edge.get(edge_id, 0) + 1
    obs = {
        "input_report_count": 4,
        "input_certified_count": int(certified(c59p3i))
        + int(certified(c59p3r))
        + int(certified(rsem))
        + int(certified(stress_gate)),
        "relation_row_count": len(relation_rows_raw),
        "stress_edge_row_count": len(stress_rows_raw),
        "assigned_relation_count": len(assignment_rows),
        "direct_assignment_count": sum(
            int(row["rule_code"] == RULE_CODES["direct_stress_edge"])
            for row in assignment_rows
        ),
        "reverse_assignment_count": sum(
            int(row["rule_code"] == RULE_CODES["reverse_stress_edge"])
            for row in assignment_rows
        ),
        "fallback_assignment_count": sum(
            int(row["rule_code"] == RULE_CODES["max_abs_incident_stress_edge"])
            for row in assignment_rows
        ),
        "unique_stress_edge_count": len(counts_by_edge),
        "max_assignment_multiplicity": max(counts_by_edge.values()),
        "formal_pushforward_flag": int(
            all(row["formal_pushforward_flag"] == 1 for row in assignment_rows)
        ),
        "operation_row_match_count": int(c59p3r_summary["operation_row_match_count"]),
        "semantic_transition_match_count": int(
            c59p3r_summary["semantic_transition_match_count"]
        ),
        "physical_selector_axiom_flag": 0,
        "four_dimensional_metric_flag": 0,
        "thermal_gravity_flag": 0,
        "next_gap_code": GAP_CODES["operation_row_promotion"],
    }
    gap_rows = [
        {
            "gap_id": GAP_CODES["formal_selector_stress_pushforward"],
            "gap_code": GAP_CODES["formal_selector_stress_pushforward"],
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
            "gap_id": GAP_CODES["semantic_transition_flags"],
            "gap_code": GAP_CODES["semantic_transition_flags"],
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
        "c59p3i": c59p3i,
        "c59p3r": c59p3r,
        "rsem": rsem,
        "stress_gate": stress_gate,
        "assignment_rows": assignment_rows,
        "rule_rows": rule_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    assignment_table = table_from_rows(ASSIGNMENT_COLUMNS, rows["assignment_rows"])
    rule_table = table_from_rows(RULE_COLUMNS, rows["rule_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "source_counts_match": obs["relation_row_count"] == 59
        and obs["stress_edge_row_count"] == 100,
        "formal_pushforward_is_total": obs["assigned_relation_count"] == 59
        and obs["formal_pushforward_flag"] == 1,
        "rule_counts_match": obs["direct_assignment_count"] == 8
        and obs["reverse_assignment_count"] == 7
        and obs["fallback_assignment_count"] == 44
        and obs["unique_stress_edge_count"] == 14
        and obs["max_assignment_multiplicity"] == 10,
        "operation_and_physical_boundaries_preserved": obs[
            "operation_row_match_count"
        ]
        == 0
        and obs["semantic_transition_match_count"] == 0
        and obs["physical_selector_axiom_flag"] == 0
        and obs["four_dimensional_metric_flag"] == 0
        and obs["thermal_gravity_flag"] == 0,
        "table_shapes_match": assignment_table.shape == (59, len(ASSIGNMENT_COLUMNS))
        and rule_table.shape == (len(RULE_CODES), len(RULE_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "formal_selector_stress_pushforward",
        "summary": {
            "relation_row_count": obs["relation_row_count"],
            "assigned_relation_count": obs["assigned_relation_count"],
            "direct_assignment_count": obs["direct_assignment_count"],
            "reverse_assignment_count": obs["reverse_assignment_count"],
            "fallback_assignment_count": obs["fallback_assignment_count"],
            "unique_stress_edge_count": obs["unique_stress_edge_count"],
            "max_assignment_multiplicity": obs["max_assignment_multiplicity"],
            "formal_pushforward_flag": obs["formal_pushforward_flag"],
            "operation_row_match_count": obs["operation_row_match_count"],
            "physical_selector_axiom_flag": obs["physical_selector_axiom_flag"],
        },
        "rule_code_map": {str(value): key for key, value in RULE_CODES.items()},
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "assignment_table_sha256": sha_array(assignment_table),
        "assignment_text_sha256": sha_text(
            csv_text(ASSIGNMENT_COLUMNS, rows["assignment_rows"])
        ),
        "rule_table_sha256": sha_array(rule_table),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    c59p3f = {
        "schema": "long.c59p3f@1",
        "object": "formal_selector_stress_pushforward",
        "status": STATUS if all(checks.values()) else "LONG_C59P3F_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.c59p3f.report@1",
        "status": c59p3f["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_c59p3f supplies a total formal stress pushforward for the 59 "
            "guarded relation witnesses. The rule uses a directed stress edge "
            "when present, otherwise a reversed edge, otherwise the strongest "
            "incident stress edge at either visible endpoint. This is a formal "
            "selector rule only: operation rows, semantic transition flags, and "
            "the physical selector axiom remain absent."
        ),
        "stage_protocol": {
            "draft": "read long_c59p3i, long_c59p3r, long_rsem, and long_stress_gate",
            "witness": "emit per-relation stress assignments, rule rows, gaps, and observables",
            "coherence": "check total assignment, direct/reverse/fallback counts, unique stress-edge count, and preserved boundaries",
            "closure": "certify the formal selector stress-pushforward candidate",
            "emit": "write long_c59p3f artifacts and verifier hook",
        },
        "inputs": {
            "long_c59p3i": input_entry(
                LONG_C59P3I,
                {
                    "status": rows["c59p3i"].get("status"),
                    "certificate_sha256": rows["c59p3i"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_c59p3r": input_entry(
                LONG_C59P3R,
                {
                    "status": rows["c59p3r"].get("status"),
                    "certificate_sha256": rows["c59p3r"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_rsem": input_entry(
                LONG_RSEM,
                {
                    "status": rows["rsem"].get("status"),
                    "certificate_sha256": rows["rsem"].get("certificate_sha256"),
                },
            ),
            "long_rsem_tick": input_entry(LONG_RSEM_TICK),
            "long_rsem_relation": input_entry(LONG_RSEM_RELATION),
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
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "c59p3f": relpath(OUT_DIR / "c59p3f.json"),
            "assignment_csv": relpath(OUT_DIR / "assignment.csv"),
            "rule_csv": relpath(OUT_DIR / "rule.csv"),
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
                "a total formal stress assignment exists for all 59 guarded relation witnesses",
                "8 relation witnesses use a directed visible stress edge",
                "7 relation witnesses use a reversed visible stress edge",
                "44 relation witnesses use the strongest incident stress-edge fallback",
                "the formal pushforward uses 14 distinct stress edges",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "semantic operation rows for the assigned witnesses",
                "semantic transition flags for the assigned witnesses",
                "a physical selector axiom for the fallback rule",
                "a four-dimensional metric reduction or thermal-gravity derivation",
            ],
        },
        "next_highest_yield_item": (
            "Test the formal pushforward against operation-row promotion: decide "
            "whether the 59 assigned relation witnesses can be represented as "
            "semantic A985 operations, or keep the construction formal only."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.c59p3f.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.c59p3f.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "c59p3f": c59p3f,
        "assignment_csv": csv_text(ASSIGNMENT_COLUMNS, rows["assignment_rows"]),
        "rule_csv": csv_text(RULE_COLUMNS, rows["rule_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "assignment_table": assignment_table,
        "rule_table": rule_table,
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
    write_json(OUT_DIR / "c59p3f.json", payloads["c59p3f"])
    (OUT_DIR / "assignment.csv").write_text(
        payloads["assignment_csv"], encoding="utf-8"
    )
    (OUT_DIR / "rule.csv").write_text(payloads["rule_csv"], encoding="utf-8")
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        assignment_table=payloads["assignment_table"],
        rule_table=payloads["rule_table"],
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
