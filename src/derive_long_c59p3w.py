from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
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


THEOREM_ID = "long_c59p3w"
STATUS = "LONG_C59P3W_FORMAL_STRESS_SOURCE_BALANCE_GATE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_C59P3U = PROOF_ROOT / "long_c59p3u" / "report.json"
LONG_C59P3U_SOURCE = PROOF_ROOT / "long_c59p3u" / "source.csv"
LONG_C59P3F = PROOF_ROOT / "long_c59p3f" / "report.json"
LONG_C59P3F_ASSIGNMENT = PROOF_ROOT / "long_c59p3f" / "assignment.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_c59p3w.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_c59p3w.py"

BALANCE_COLUMNS = [
    "atom_id",
    "outgoing_signed_tension_scaled",
    "incoming_signed_tension_scaled",
    "net_divergence_scaled",
    "incident_abs_tension_scaled",
    "local_balance_flag",
]
EDGE_COLUMNS = [
    "stress_edge_id",
    "stress_source_atom",
    "stress_target_atom",
    "assignment_count",
    "signed_tension_sum_scaled",
    "abs_tension_sum_scaled",
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
    "formal_stress_source_ledger",
    "global_divergence_balance",
    "local_node_balance",
    "counterterm_or_selector_correction",
    "physical_selector_axiom",
    "thermal_gravity_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "source_row_count",
    "assignment_row_count",
    "stress_edge_count",
    "atom_count",
    "source_assignment_total",
    "source_signed_tension_total_scaled",
    "source_abs_tension_total_scaled",
    "global_divergence_sum_scaled",
    "local_balanced_atom_count",
    "local_unbalanced_atom_count",
    "max_abs_divergence_scaled",
    "incident_abs_tension_total_scaled",
    "global_balance_flag",
    "local_balance_flag",
    "operation_backed_source_count",
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
    c59p3u = load_json(LONG_C59P3U)
    c59p3f = load_json(LONG_C59P3F)
    c59p3u_summary = summary(c59p3u)
    _, source_rows_raw = read_csv_rows(LONG_C59P3U_SOURCE)
    _, assignment_rows_raw = read_csv_rows(LONG_C59P3F_ASSIGNMENT)

    edge_info: dict[int, dict[str, int]] = {}
    for row in assignment_rows_raw:
        stress_edge_id = int(row["stress_edge_id"])
        if stress_edge_id not in edge_info:
            edge_info[stress_edge_id] = {
                "stress_source_atom": int(row["stress_source_atom"]),
                "stress_target_atom": int(row["stress_target_atom"]),
                "assignment_count": 0,
                "signed_tension_sum_scaled": 0,
                "abs_tension_sum_scaled": 0,
            }
        edge_info[stress_edge_id]["assignment_count"] += 1
        edge_info[stress_edge_id]["signed_tension_sum_scaled"] += int(
            row["signed_tension_scaled"]
        )
        edge_info[stress_edge_id]["abs_tension_sum_scaled"] += int(
            row["abs_tension_scaled"]
        )

    edge_rows = [
        {
            "stress_edge_id": edge_id,
            **edge_info[edge_id],
        }
        for edge_id in sorted(edge_info)
    ]

    outgoing: dict[int, int] = defaultdict(int)
    incoming: dict[int, int] = defaultdict(int)
    incident_abs: dict[int, int] = defaultdict(int)
    for row in edge_rows:
        source = row["stress_source_atom"]
        target = row["stress_target_atom"]
        signed = row["signed_tension_sum_scaled"]
        abs_value = row["abs_tension_sum_scaled"]
        outgoing[source] += signed
        incoming[target] += signed
        incident_abs[source] += abs_value
        incident_abs[target] += abs_value

    atom_ids = list(range(20))
    balance_rows = []
    for atom_id in atom_ids:
        net = outgoing[atom_id] - incoming[atom_id]
        balance_rows.append(
            {
                "atom_id": atom_id,
                "outgoing_signed_tension_scaled": outgoing[atom_id],
                "incoming_signed_tension_scaled": incoming[atom_id],
                "net_divergence_scaled": net,
                "incident_abs_tension_scaled": incident_abs[atom_id],
                "local_balance_flag": int(net == 0),
            }
        )

    source_assignment_total = sum(row["assignment_count"] for row in edge_rows)
    source_signed_total = sum(row["signed_tension_sum_scaled"] for row in edge_rows)
    source_abs_total = sum(row["abs_tension_sum_scaled"] for row in edge_rows)
    global_divergence_sum = sum(row["net_divergence_scaled"] for row in balance_rows)
    local_balanced_count = sum(row["local_balance_flag"] for row in balance_rows)
    obs = {
        "input_report_count": 2,
        "input_certified_count": int(certified(c59p3u)) + int(certified(c59p3f)),
        "source_row_count": len(source_rows_raw),
        "assignment_row_count": len(assignment_rows_raw),
        "stress_edge_count": len(edge_rows),
        "atom_count": len(balance_rows),
        "source_assignment_total": source_assignment_total,
        "source_signed_tension_total_scaled": source_signed_total,
        "source_abs_tension_total_scaled": source_abs_total,
        "global_divergence_sum_scaled": global_divergence_sum,
        "local_balanced_atom_count": local_balanced_count,
        "local_unbalanced_atom_count": len(balance_rows) - local_balanced_count,
        "max_abs_divergence_scaled": max(
            abs(row["net_divergence_scaled"]) for row in balance_rows
        ),
        "incident_abs_tension_total_scaled": sum(
            row["incident_abs_tension_scaled"] for row in balance_rows
        ),
        "global_balance_flag": int(global_divergence_sum == 0),
        "local_balance_flag": int(local_balanced_count == len(balance_rows)),
        "operation_backed_source_count": int(
            c59p3u_summary["operation_backed_source_count"]
        ),
        "physical_selector_axiom_flag": 0,
        "thermal_gravity_flag": 0,
        "next_gap_code": GAP_CODES["counterterm_or_selector_correction"],
    }
    gap_rows = [
        {
            "gap_id": GAP_CODES["formal_stress_source_ledger"],
            "gap_code": GAP_CODES["formal_stress_source_ledger"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["global_divergence_balance"],
            "gap_code": GAP_CODES["global_divergence_balance"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["local_node_balance"],
            "gap_code": GAP_CODES["local_node_balance"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["counterterm_or_selector_correction"],
            "gap_code": GAP_CODES["counterterm_or_selector_correction"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 0,
            "next_flag": 1,
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
        "c59p3u": c59p3u,
        "c59p3f": c59p3f,
        "edge_rows": edge_rows,
        "balance_rows": balance_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    edge_table = table_from_rows(EDGE_COLUMNS, rows["edge_rows"])
    balance_table = table_from_rows(BALANCE_COLUMNS, rows["balance_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "source_counts_match": obs["source_row_count"] == 14
        and obs["assignment_row_count"] == 59
        and obs["stress_edge_count"] == 14
        and obs["atom_count"] == 20
        and obs["source_assignment_total"] == 59,
        "source_sums_match": obs["source_signed_tension_total_scaled"]
        == -197809407552
        and obs["source_abs_tension_total_scaled"] == 354128490312
        and obs["incident_abs_tension_total_scaled"] == 708256980624,
        "global_balance_holds": obs["global_divergence_sum_scaled"] == 0
        and obs["global_balance_flag"] == 1,
        "local_balance_obstructed": obs["local_balanced_atom_count"] == 3
        and obs["local_unbalanced_atom_count"] == 17
        and obs["max_abs_divergence_scaled"] == 180000000000
        and obs["local_balance_flag"] == 0,
        "operation_and_physical_boundaries_preserved": obs[
            "operation_backed_source_count"
        ]
        == 0
        and obs["physical_selector_axiom_flag"] == 0
        and obs["thermal_gravity_flag"] == 0,
        "table_shapes_match": edge_table.shape == (14, len(EDGE_COLUMNS))
        and balance_table.shape == (20, len(BALANCE_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "formal_stress_source_balance_gate",
        "summary": {
            "source_row_count": obs["source_row_count"],
            "atom_count": obs["atom_count"],
            "source_signed_tension_total_scaled": obs[
                "source_signed_tension_total_scaled"
            ],
            "global_divergence_sum_scaled": obs["global_divergence_sum_scaled"],
            "local_balanced_atom_count": obs["local_balanced_atom_count"],
            "local_unbalanced_atom_count": obs["local_unbalanced_atom_count"],
            "max_abs_divergence_scaled": obs["max_abs_divergence_scaled"],
            "global_balance_flag": obs["global_balance_flag"],
            "local_balance_flag": obs["local_balance_flag"],
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "edge_table_sha256": sha_array(edge_table),
        "edge_text_sha256": sha_text(csv_text(EDGE_COLUMNS, rows["edge_rows"])),
        "balance_table_sha256": sha_array(balance_table),
        "balance_text_sha256": sha_text(
            csv_text(BALANCE_COLUMNS, rows["balance_rows"])
        ),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    c59p3w = {
        "schema": "long.c59p3w@1",
        "object": "formal_stress_source_balance_gate",
        "status": STATUS if all(checks.values()) else "LONG_C59P3W_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.c59p3w.report@1",
        "status": c59p3w["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_c59p3w tests conservation for the 14-edge formal stress-source "
            "ledger. The directed incidence has zero total divergence, but it "
            "is not locally balanced: only 3 of 20 atoms have zero net "
            "divergence, while 17 atoms retain a local source/sink residue."
        ),
        "stage_protocol": {
            "draft": "read long_c59p3u source rows and long_c59p3f stress assignments",
            "witness": "emit stress-edge source rows, atom balance rows, gaps, and observables",
            "coherence": "check source sums, global divergence, local imbalance, and preserved boundaries",
            "closure": "certify the formal stress-source balance gate",
            "emit": "write long_c59p3w artifacts and verifier hook",
        },
        "inputs": {
            "long_c59p3u": input_entry(
                LONG_C59P3U,
                {
                    "status": rows["c59p3u"].get("status"),
                    "certificate_sha256": rows["c59p3u"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_c59p3u_source": input_entry(LONG_C59P3U_SOURCE),
            "long_c59p3f": input_entry(
                LONG_C59P3F,
                {
                    "status": rows["c59p3f"].get("status"),
                    "certificate_sha256": rows["c59p3f"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_c59p3f_assignment": input_entry(LONG_C59P3F_ASSIGNMENT),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "c59p3w": relpath(OUT_DIR / "c59p3w.json"),
            "edge_csv": relpath(OUT_DIR / "edge.csv"),
            "balance_csv": relpath(OUT_DIR / "balance.csv"),
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
                "the 14-edge formal stress-source ledger has zero global divergence",
                "the ledger has 20 atom-balance rows",
                "only 3 atoms are locally balanced",
                "17 atoms retain nonzero local divergence",
                "the largest absolute local divergence is 180000000000",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "local stress-source conservation",
                "a counterterm or selector correction that cancels the 17 residues",
                "a physical selector axiom",
                "a four-dimensional metric reduction or thermal-gravity derivation",
            ],
        },
        "next_highest_yield_item": (
            "Construct the minimal finite counterterm or selector correction that "
            "cancels the 17 nonzero atom divergences while preserving the "
            "global zero-divergence ledger."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.c59p3w.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.c59p3w.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "c59p3w": c59p3w,
        "edge_csv": csv_text(EDGE_COLUMNS, rows["edge_rows"]),
        "balance_csv": csv_text(BALANCE_COLUMNS, rows["balance_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "edge_table": edge_table,
        "balance_table": balance_table,
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
    write_json(OUT_DIR / "c59p3w.json", payloads["c59p3w"])
    (OUT_DIR / "edge.csv").write_text(payloads["edge_csv"], encoding="utf-8")
    (OUT_DIR / "balance.csv").write_text(payloads["balance_csv"], encoding="utf-8")
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        edge_table=payloads["edge_table"],
        balance_table=payloads["balance_table"],
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
