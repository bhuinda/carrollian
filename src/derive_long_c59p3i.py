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


THEOREM_ID = "long_c59p3i"
STATUS = "LONG_C59P3I_VISIBLE_TICK_STRESS_INCIDENCE_OBSTRUCTION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_C59P3R = PROOF_ROOT / "long_c59p3r" / "report.json"
LONG_RSEM = PROOF_ROOT / "long_rsem" / "report.json"
LONG_RSEM_TICK = PROOF_ROOT / "long_rsem" / "tick.csv"
LONG_RSEM_RELATION = PROOF_ROOT / "long_rsem" / "relation.csv"
LONG_STRESS_GATE = PROOF_ROOT / "long_stress_gate" / "report.json"
LONG_STRESS_EDGE = PROOF_ROOT / "long_stress_gate" / "stress_edge.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_c59p3i.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_c59p3i.py"

TICK_STRESS_COLUMNS = [
    "visible_index",
    "source_atom_id",
    "target_atom_id",
    "relation_match_count",
    "direct_stress_edge_id",
    "reverse_stress_edge_id",
    "direct_stress_flag",
    "reverse_stress_flag",
    "undirected_stress_flag",
    "missing_stress_flag",
]
RELATION_STRESS_COLUMNS = [
    "relation_id",
    "visible_index",
    "transition_id",
    "direct_stress_edge_id",
    "reverse_stress_edge_id",
    "direct_stress_flag",
    "reverse_stress_flag",
    "undirected_stress_flag",
    "stress_incidence_flag",
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

GAP_NAMES = [
    "guarded_relation_tick_law",
    "directed_visible_tick_stress_map",
    "undirected_visible_tick_stress_map",
    "total_relation_stress_incidence",
    "operation_row_promotion",
    "selector_pushforward_rule",
    "thermal_gravity_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "tick_row_count",
    "relation_row_count",
    "stress_edge_row_count",
    "direct_tick_stress_count",
    "reverse_tick_stress_count",
    "undirected_tick_stress_count",
    "missing_tick_stress_count",
    "direct_relation_stress_count",
    "undirected_relation_stress_count",
    "missing_relation_stress_count",
    "total_visible_tick_stress_map_flag",
    "total_relation_stress_incidence_flag",
    "relation_stress_extension_flag",
    "operation_row_match_count",
    "semantic_transition_match_count",
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
    c59p3r = load_json(LONG_C59P3R)
    rsem = load_json(LONG_RSEM)
    stress_gate = load_json(LONG_STRESS_GATE)
    _, tick_rows_raw = read_csv_rows(LONG_RSEM_TICK)
    _, relation_rows_raw = read_csv_rows(LONG_RSEM_RELATION)
    _, stress_rows_raw = read_csv_rows(LONG_STRESS_EDGE)
    c_summary = summary(c59p3r)

    stress_by_pair: dict[tuple[int, int], int] = {}
    for row in stress_rows_raw:
        pair = (int(row["source_atom"]), int(row["target_atom"]))
        stress_by_pair[pair] = int(row["stress_edge_id"])

    tick_by_visible: dict[int, dict[str, int]] = {}
    tick_stress_rows = []
    for row in tick_rows_raw:
        visible_index = int(row["visible_index"])
        source = int(row["source_atom_id"])
        target = int(row["target_atom_id"])
        direct_id = stress_by_pair.get((source, target), -1)
        reverse_id = stress_by_pair.get((target, source), -1)
        direct_flag = int(direct_id >= 0)
        reverse_flag = int(reverse_id >= 0)
        undirected_flag = int(direct_flag == 1 or reverse_flag == 1)
        entry = {
            "visible_index": visible_index,
            "source_atom_id": source,
            "target_atom_id": target,
            "relation_match_count": int(row["relation_match_count"]),
            "direct_stress_edge_id": direct_id,
            "reverse_stress_edge_id": reverse_id,
            "direct_stress_flag": direct_flag,
            "reverse_stress_flag": reverse_flag,
            "undirected_stress_flag": undirected_flag,
            "missing_stress_flag": int(undirected_flag == 0),
        }
        tick_by_visible[visible_index] = entry
        tick_stress_rows.append(entry)

    relation_stress_rows = []
    for row in relation_rows_raw:
        visible_index = int(row["visible_index"])
        tick = tick_by_visible[visible_index]
        relation_stress_rows.append(
            {
                "relation_id": int(row["relation_id"]),
                "visible_index": visible_index,
                "transition_id": int(row["transition_id"]),
                "direct_stress_edge_id": tick["direct_stress_edge_id"],
                "reverse_stress_edge_id": tick["reverse_stress_edge_id"],
                "direct_stress_flag": tick["direct_stress_flag"],
                "reverse_stress_flag": tick["reverse_stress_flag"],
                "undirected_stress_flag": tick["undirected_stress_flag"],
                "stress_incidence_flag": tick["undirected_stress_flag"],
            }
        )

    direct_tick_count = sum(row["direct_stress_flag"] for row in tick_stress_rows)
    reverse_tick_count = sum(row["reverse_stress_flag"] for row in tick_stress_rows)
    undirected_tick_count = sum(
        row["undirected_stress_flag"] for row in tick_stress_rows
    )
    missing_tick_count = sum(row["missing_stress_flag"] for row in tick_stress_rows)
    direct_relation_count = sum(
        row["direct_stress_flag"] for row in relation_stress_rows
    )
    undirected_relation_count = sum(
        row["undirected_stress_flag"] for row in relation_stress_rows
    )
    missing_relation_count = len(relation_stress_rows) - undirected_relation_count
    obs = {
        "input_report_count": 3,
        "input_certified_count": int(certified(c59p3r))
        + int(certified(rsem))
        + int(certified(stress_gate)),
        "tick_row_count": len(tick_rows_raw),
        "relation_row_count": len(relation_rows_raw),
        "stress_edge_row_count": len(stress_rows_raw),
        "direct_tick_stress_count": direct_tick_count,
        "reverse_tick_stress_count": reverse_tick_count,
        "undirected_tick_stress_count": undirected_tick_count,
        "missing_tick_stress_count": missing_tick_count,
        "direct_relation_stress_count": direct_relation_count,
        "undirected_relation_stress_count": undirected_relation_count,
        "missing_relation_stress_count": missing_relation_count,
        "total_visible_tick_stress_map_flag": int(undirected_tick_count == len(tick_rows_raw)),
        "total_relation_stress_incidence_flag": int(
            undirected_relation_count == len(relation_rows_raw)
        ),
        "relation_stress_extension_flag": int(
            c_summary["relation_stress_extension_flag"]
        ),
        "operation_row_match_count": int(c_summary["operation_row_match_count"]),
        "semantic_transition_match_count": int(
            c_summary["semantic_transition_match_count"]
        ),
        "physical_selector_axiom_flag": 0,
        "thermal_gravity_flag": 0,
        "next_gap_code": GAP_CODES["selector_pushforward_rule"],
    }
    gap_rows = [
        {
            "gap_id": GAP_CODES["guarded_relation_tick_law"],
            "gap_code": GAP_CODES["guarded_relation_tick_law"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["directed_visible_tick_stress_map"],
            "gap_code": GAP_CODES["directed_visible_tick_stress_map"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["undirected_visible_tick_stress_map"],
            "gap_code": GAP_CODES["undirected_visible_tick_stress_map"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["total_relation_stress_incidence"],
            "gap_code": GAP_CODES["total_relation_stress_incidence"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["operation_row_promotion"],
            "gap_code": GAP_CODES["operation_row_promotion"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["selector_pushforward_rule"],
            "gap_code": GAP_CODES["selector_pushforward_rule"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 1,
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
        "c59p3r": c59p3r,
        "rsem": rsem,
        "stress_gate": stress_gate,
        "tick_stress_rows": tick_stress_rows,
        "relation_stress_rows": relation_stress_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    tick_stress_table = table_from_rows(TICK_STRESS_COLUMNS, rows["tick_stress_rows"])
    relation_stress_table = table_from_rows(
        RELATION_STRESS_COLUMNS, rows["relation_stress_rows"]
    )
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "source_counts_match": obs["tick_row_count"] == 20
        and obs["relation_row_count"] == 59
        and obs["stress_edge_row_count"] == 100,
        "visible_tick_stress_incidence_incomplete": obs["direct_tick_stress_count"] == 3
        and obs["reverse_tick_stress_count"] == 5
        and obs["undirected_tick_stress_count"] == 6
        and obs["missing_tick_stress_count"] == 14
        and obs["total_visible_tick_stress_map_flag"] == 0,
        "relation_stress_incidence_incomplete": obs["direct_relation_stress_count"] == 8
        and obs["undirected_relation_stress_count"] == 15
        and obs["missing_relation_stress_count"] == 44
        and obs["total_relation_stress_incidence_flag"] == 0,
        "upstream_extension_still_blocked": obs["relation_stress_extension_flag"] == 0
        and obs["operation_row_match_count"] == 0
        and obs["semantic_transition_match_count"] == 0,
        "physical_boundaries_preserved": obs["physical_selector_axiom_flag"] == 0
        and obs["thermal_gravity_flag"] == 0,
        "table_shapes_match": tick_stress_table.shape
        == (20, len(TICK_STRESS_COLUMNS))
        and relation_stress_table.shape == (59, len(RELATION_STRESS_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "visible_tick_stress_incidence_obstruction",
        "summary": {
            "tick_row_count": obs["tick_row_count"],
            "relation_row_count": obs["relation_row_count"],
            "stress_edge_row_count": obs["stress_edge_row_count"],
            "direct_tick_stress_count": obs["direct_tick_stress_count"],
            "undirected_tick_stress_count": obs["undirected_tick_stress_count"],
            "missing_tick_stress_count": obs["missing_tick_stress_count"],
            "direct_relation_stress_count": obs["direct_relation_stress_count"],
            "undirected_relation_stress_count": obs[
                "undirected_relation_stress_count"
            ],
            "missing_relation_stress_count": obs["missing_relation_stress_count"],
            "total_relation_stress_incidence_flag": obs[
                "total_relation_stress_incidence_flag"
            ],
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "tick_stress_table_sha256": sha_array(tick_stress_table),
        "tick_stress_text_sha256": sha_text(
            csv_text(TICK_STRESS_COLUMNS, rows["tick_stress_rows"])
        ),
        "relation_stress_table_sha256": sha_array(relation_stress_table),
        "relation_stress_text_sha256": sha_text(
            csv_text(RELATION_STRESS_COLUMNS, rows["relation_stress_rows"])
        ),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    c59p3i = {
        "schema": "long.c59p3i@1",
        "object": "visible_tick_stress_incidence_obstruction",
        "status": STATUS if all(checks.values()) else "LONG_C59P3I_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.c59p3i.report@1",
        "status": c59p3i["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_c59p3i tests the direct visible-endpoint pushforward from "
            "relation-valued ticks into the stress graph. The 20 guarded ticks "
            "supply atom endpoints, but only 3 are directed stress edges and "
            "only 6 are stress edges after allowing reversal. Thus only 15 of "
            "the 59 relation witnesses receive any visible-endpoint stress "
            "incidence, so this pushforward is not a total stress-transition law."
        ),
        "stage_protocol": {
            "draft": "read long_c59p3r, long_rsem tick/relation rows, and long_stress_gate stress edges",
            "witness": "emit per-tick and per-relation stress-incidence rows",
            "coherence": "check directed, reversed, undirected, and missing stress incidence counts",
            "closure": "certify the visible-endpoint stress-incidence obstruction",
            "emit": "write long_c59p3i artifacts and verifier hook",
        },
        "inputs": {
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
            "c59p3i": relpath(OUT_DIR / "c59p3i.json"),
            "tick_stress_csv": relpath(OUT_DIR / "tick_stress.csv"),
            "relation_stress_csv": relpath(OUT_DIR / "relation_stress.csv"),
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
                "the visible relation-tick endpoints can be checked against the directed stress graph",
                "only 3 of 20 visible ticks are directed stress edges",
                "only 6 of 20 visible ticks are stress edges after allowing reversal",
                "only 15 of 59 relation witnesses inherit any visible-endpoint stress incidence",
                "the visible-endpoint pushforward is not a total stress-transition law",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "a selector pushforward rule that sends missing tick endpoints into stress atoms by another key",
                "operation-row promotion for the relation witnesses",
                "a physical selector axiom",
                "a four-dimensional metric reduction or thermal-gravity derivation",
            ],
        },
        "next_highest_yield_item": (
            "Search for a selector pushforward rule from the 44 missing relation "
            "witnesses into stress atoms, because visible tick endpoints alone "
            "cover only 15 of 59 witnesses."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.c59p3i.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.c59p3i.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "c59p3i": c59p3i,
        "tick_stress_csv": csv_text(TICK_STRESS_COLUMNS, rows["tick_stress_rows"]),
        "relation_stress_csv": csv_text(
            RELATION_STRESS_COLUMNS, rows["relation_stress_rows"]
        ),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "tick_stress_table": tick_stress_table,
        "relation_stress_table": relation_stress_table,
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
    write_json(OUT_DIR / "c59p3i.json", payloads["c59p3i"])
    (OUT_DIR / "tick_stress.csv").write_text(
        payloads["tick_stress_csv"], encoding="utf-8"
    )
    (OUT_DIR / "relation_stress.csv").write_text(
        payloads["relation_stress_csv"], encoding="utf-8"
    )
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        tick_stress_table=payloads["tick_stress_table"],
        relation_stress_table=payloads["relation_stress_table"],
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
