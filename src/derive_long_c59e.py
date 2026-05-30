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


THEOREM_ID = "long_c59e"
STATUS = "LONG_C59E_SIGNED_EDGE_ANSATZ_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_C59X = PROOF_ROOT / "long_c59x" / "report.json"
LONG_C59X_ROUTE = PROOF_ROOT / "long_c59x" / "route.csv"
LONG_C59X_SENTINEL = PROOF_ROOT / "long_c59x" / "sentinel.csv"
LONG_STRESS_GATE = PROOF_ROOT / "long_stress_gate" / "report.json"
LONG_STRESS_EDGE = PROOF_ROOT / "long_stress_gate" / "stress_edge.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_c59e.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_c59e.py"

ROUTE_FLUX_COLUMNS = [
    "route_id",
    "relation_id",
    "sentinel_mode_id",
    "sentinel_sign",
    "stress_edge_id",
    "source_atom",
    "target_atom",
    "route_weight_scaled",
    "route_flux_scaled",
    "tension_abs_scaled",
    "formal_ansatz_flag",
]
EDGE_FLUX_COLUMNS = [
    "edge_flux_id",
    "stress_edge_id",
    "source_atom",
    "target_atom",
    "positive_route_count",
    "negative_route_count",
    "route_count",
    "positive_flux_scaled",
    "negative_flux_scaled",
    "net_flux_scaled",
    "abs_net_flux_scaled",
]
NODE_BALANCE_COLUMNS = [
    "atom_id",
    "outgoing_flux_scaled",
    "incoming_flux_scaled",
    "divergence_scaled",
    "abs_divergence_scaled",
    "local_conserved_flag",
]
MODE_COLUMNS = [
    "sentinel_mode_id",
    "sentinel_sign",
    "route_count",
    "used_edge_count",
    "source_node_count",
    "total_weight_scaled",
    "total_flux_scaled",
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
    "signed_edge_ansatz",
    "global_conservation",
    "local_conservation",
    "controlled_local_defect",
    "physical_stress_energy_tensor",
    "smooth_lorentzian_metric",
    "thermal_gravity_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "route_row_count",
    "edge_flux_row_count",
    "node_balance_row_count",
    "sentinel_mode_count",
    "positive_route_count",
    "negative_route_count",
    "used_edge_count",
    "positive_total_weight_scaled",
    "negative_total_weight_scaled",
    "positive_total_flux_scaled",
    "negative_total_flux_scaled",
    "net_route_flux_scaled",
    "node_outgoing_total_scaled",
    "node_incoming_total_scaled",
    "global_divergence_scaled",
    "global_conservation_flag",
    "local_conserved_node_count",
    "defect_node_count",
    "total_abs_defect_scaled",
    "max_abs_defect_scaled",
    "controlled_defect_flag",
    "formal_edge_ansatz_flag",
    "physical_stress_energy_flag",
    "smooth_metric_flag",
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
    return report.get("all_checks_pass") is True and "CERTIFIED" in str(
        report.get("status", "")
    )


def build_rows() -> dict[str, Any]:
    c59x = load_json(LONG_C59X)
    stress_gate = load_json(LONG_STRESS_GATE)
    route_rows_source = read_csv_int(LONG_C59X_ROUTE)
    sentinel_rows_source = read_csv_int(LONG_C59X_SENTINEL)
    stress_edges = read_csv_int(LONG_STRESS_EDGE)

    route_flux_rows = []
    for row in route_rows_source:
        flux = row["sentinel_sign"] * row["weight_scaled"]
        route_flux_rows.append(
            {
                "route_id": row["route_id"],
                "relation_id": row["relation_id"],
                "sentinel_mode_id": row["sentinel_mode_id"],
                "sentinel_sign": row["sentinel_sign"],
                "stress_edge_id": row["stress_edge_id"],
                "source_atom": row["edge_source_atom"],
                "target_atom": row["edge_target_atom"],
                "route_weight_scaled": row["weight_scaled"],
                "route_flux_scaled": flux,
                "tension_abs_scaled": abs(row["signed_tension_scaled"]),
                "formal_ansatz_flag": 1,
            }
        )

    edge_ids = sorted({row["stress_edge_id"] for row in route_flux_rows})
    edge_by_id = {row["stress_edge_id"]: row for row in stress_edges}
    edge_flux_rows = []
    for edge_flux_id, stress_edge_id in enumerate(edge_ids):
        rows_for_edge = [
            row for row in route_flux_rows if row["stress_edge_id"] == stress_edge_id
        ]
        positive_flux = sum(
            row["route_flux_scaled"] for row in rows_for_edge if row["sentinel_sign"] > 0
        )
        negative_flux = sum(
            row["route_flux_scaled"] for row in rows_for_edge if row["sentinel_sign"] < 0
        )
        net_flux = positive_flux + negative_flux
        edge = edge_by_id[stress_edge_id]
        edge_flux_rows.append(
            {
                "edge_flux_id": edge_flux_id,
                "stress_edge_id": stress_edge_id,
                "source_atom": edge["source_atom"],
                "target_atom": edge["target_atom"],
                "positive_route_count": sum(
                    row["sentinel_sign"] > 0 for row in rows_for_edge
                ),
                "negative_route_count": sum(
                    row["sentinel_sign"] < 0 for row in rows_for_edge
                ),
                "route_count": len(rows_for_edge),
                "positive_flux_scaled": positive_flux,
                "negative_flux_scaled": negative_flux,
                "net_flux_scaled": net_flux,
                "abs_net_flux_scaled": abs(net_flux),
            }
        )

    node_balance_rows = []
    for atom_id in range(20):
        outgoing = sum(
            row["route_flux_scaled"]
            for row in route_flux_rows
            if row["source_atom"] == atom_id
        )
        incoming = sum(
            row["route_flux_scaled"]
            for row in route_flux_rows
            if row["target_atom"] == atom_id
        )
        divergence = outgoing - incoming
        node_balance_rows.append(
            {
                "atom_id": atom_id,
                "outgoing_flux_scaled": outgoing,
                "incoming_flux_scaled": incoming,
                "divergence_scaled": divergence,
                "abs_divergence_scaled": abs(divergence),
                "local_conserved_flag": int(divergence == 0),
            }
        )

    mode_rows = []
    for sentinel in sentinel_rows_source:
        mode_id = sentinel["sentinel_mode_id"]
        rows_for_mode = [
            row for row in route_flux_rows if row["sentinel_mode_id"] == mode_id
        ]
        mode_rows.append(
            {
                "sentinel_mode_id": mode_id,
                "sentinel_sign": sentinel["sentinel_sign"],
                "route_count": len(rows_for_mode),
                "used_edge_count": len({row["stress_edge_id"] for row in rows_for_mode}),
                "source_node_count": len({row["source_atom"] for row in rows_for_mode}),
                "total_weight_scaled": sum(
                    row["route_weight_scaled"] for row in rows_for_mode
                ),
                "total_flux_scaled": sum(
                    row["route_flux_scaled"] for row in rows_for_mode
                ),
            }
        )

    positive_route_count = sum(row["sentinel_sign"] > 0 for row in route_flux_rows)
    negative_route_count = sum(row["sentinel_sign"] < 0 for row in route_flux_rows)
    positive_total_weight = sum(
        row["route_weight_scaled"] for row in route_flux_rows if row["sentinel_sign"] > 0
    )
    negative_total_weight = sum(
        row["route_weight_scaled"] for row in route_flux_rows if row["sentinel_sign"] < 0
    )
    positive_total_flux = sum(
        row["route_flux_scaled"] for row in route_flux_rows if row["sentinel_sign"] > 0
    )
    negative_total_flux = sum(
        row["route_flux_scaled"] for row in route_flux_rows if row["sentinel_sign"] < 0
    )
    node_outgoing_total = sum(row["outgoing_flux_scaled"] for row in node_balance_rows)
    node_incoming_total = sum(row["incoming_flux_scaled"] for row in node_balance_rows)
    global_divergence = sum(row["divergence_scaled"] for row in node_balance_rows)
    local_conserved = sum(row["local_conserved_flag"] for row in node_balance_rows)
    total_abs_defect = sum(row["abs_divergence_scaled"] for row in node_balance_rows)
    max_abs_defect = max(row["abs_divergence_scaled"] for row in node_balance_rows)
    obs = {
        "input_report_count": 2,
        "input_certified_count": sum(certified(report) for report in [c59x, stress_gate]),
        "route_row_count": len(route_flux_rows),
        "edge_flux_row_count": len(edge_flux_rows),
        "node_balance_row_count": len(node_balance_rows),
        "sentinel_mode_count": len(mode_rows),
        "positive_route_count": positive_route_count,
        "negative_route_count": negative_route_count,
        "used_edge_count": len(edge_flux_rows),
        "positive_total_weight_scaled": positive_total_weight,
        "negative_total_weight_scaled": negative_total_weight,
        "positive_total_flux_scaled": positive_total_flux,
        "negative_total_flux_scaled": negative_total_flux,
        "net_route_flux_scaled": positive_total_flux + negative_total_flux,
        "node_outgoing_total_scaled": node_outgoing_total,
        "node_incoming_total_scaled": node_incoming_total,
        "global_divergence_scaled": global_divergence,
        "global_conservation_flag": int(global_divergence == 0),
        "local_conserved_node_count": local_conserved,
        "defect_node_count": len(node_balance_rows) - local_conserved,
        "total_abs_defect_scaled": total_abs_defect,
        "max_abs_defect_scaled": max_abs_defect,
        "controlled_defect_flag": int(global_divergence == 0 and total_abs_defect > 0),
        "formal_edge_ansatz_flag": 1,
        "physical_stress_energy_flag": 0,
        "smooth_metric_flag": 0,
        "thermal_gravity_flag": 0,
        "next_gap_code": GAP_CODES["local_conservation"],
    }
    gap_rows = [
        {
            "gap_id": GAP_CODES["signed_edge_ansatz"],
            "gap_code": GAP_CODES["signed_edge_ansatz"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["global_conservation"],
            "gap_code": GAP_CODES["global_conservation"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["local_conservation"],
            "gap_code": GAP_CODES["local_conservation"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": int(obs["defect_node_count"] > 0),
            "next_flag": 1,
        },
        {
            "gap_id": GAP_CODES["controlled_local_defect"],
            "gap_code": GAP_CODES["controlled_local_defect"],
            "certified_flag": obs["controlled_defect_flag"],
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["physical_stress_energy_tensor"],
            "gap_code": GAP_CODES["physical_stress_energy_tensor"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["smooth_lorentzian_metric"],
            "gap_code": GAP_CODES["smooth_lorentzian_metric"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["thermal_gravity_derivation"],
            "gap_code": GAP_CODES["thermal_gravity_derivation"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 0,
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
        "c59x": c59x,
        "stress_gate": stress_gate,
        "route_flux_rows": route_flux_rows,
        "edge_flux_rows": edge_flux_rows,
        "node_balance_rows": node_balance_rows,
        "mode_rows": mode_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    route_flux_table = table_from_rows(ROUTE_FLUX_COLUMNS, rows["route_flux_rows"])
    edge_flux_table = table_from_rows(EDGE_FLUX_COLUMNS, rows["edge_flux_rows"])
    node_balance_table = table_from_rows(NODE_BALANCE_COLUMNS, rows["node_balance_rows"])
    mode_table = table_from_rows(MODE_COLUMNS, rows["mode_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "signed_edge_ansatz_materialized": obs["route_row_count"] == 118
        and obs["edge_flux_row_count"] == obs["used_edge_count"]
        and obs["used_edge_count"] > 0
        and obs["sentinel_mode_count"] == 2,
        "mode_fluxes_match_signed_weights": obs["positive_route_count"] == 59
        and obs["negative_route_count"] == 59
        and obs["positive_total_flux_scaled"] == obs["positive_total_weight_scaled"]
        and obs["negative_total_flux_scaled"] == -obs["negative_total_weight_scaled"],
        "global_conservation_exact": obs["global_divergence_scaled"] == 0
        and obs["node_outgoing_total_scaled"] == obs["node_incoming_total_scaled"],
        "controlled_local_defect_explicit": obs["controlled_defect_flag"] == 1
        and obs["defect_node_count"] > 0
        and obs["total_abs_defect_scaled"] > 0
        and obs["max_abs_defect_scaled"] > 0,
        "physical_metric_boundaries_preserved": obs["formal_edge_ansatz_flag"] == 1
        and obs["physical_stress_energy_flag"] == 0
        and obs["smooth_metric_flag"] == 0
        and obs["thermal_gravity_flag"] == 0,
        "table_shapes_match": route_flux_table.shape
        == (118, len(ROUTE_FLUX_COLUMNS))
        and edge_flux_table.shape[1] == len(EDGE_FLUX_COLUMNS)
        and edge_flux_table.shape[0] == obs["edge_flux_row_count"]
        and node_balance_table.shape == (20, len(NODE_BALANCE_COLUMNS))
        and mode_table.shape == (2, len(MODE_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "c59x_signed_edge_ansatz",
        "summary": {
            "route_row_count": obs["route_row_count"],
            "edge_flux_row_count": obs["edge_flux_row_count"],
            "node_balance_row_count": obs["node_balance_row_count"],
            "positive_route_count": obs["positive_route_count"],
            "negative_route_count": obs["negative_route_count"],
            "used_edge_count": obs["used_edge_count"],
            "net_route_flux_scaled": obs["net_route_flux_scaled"],
            "global_divergence_scaled": obs["global_divergence_scaled"],
            "global_conservation_flag": obs["global_conservation_flag"],
            "local_conserved_node_count": obs["local_conserved_node_count"],
            "defect_node_count": obs["defect_node_count"],
            "total_abs_defect_scaled": obs["total_abs_defect_scaled"],
            "max_abs_defect_scaled": obs["max_abs_defect_scaled"],
            "controlled_defect_flag": obs["controlled_defect_flag"],
            "physical_stress_energy_flag": obs["physical_stress_energy_flag"],
            "smooth_metric_flag": obs["smooth_metric_flag"],
            "thermal_gravity_flag": obs["thermal_gravity_flag"],
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "route_flux_table_sha256": sha_array(route_flux_table),
        "route_flux_text_sha256": sha_text(
            csv_text(ROUTE_FLUX_COLUMNS, rows["route_flux_rows"])
        ),
        "edge_flux_table_sha256": sha_array(edge_flux_table),
        "node_balance_table_sha256": sha_array(node_balance_table),
        "mode_table_sha256": sha_array(mode_table),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    c59e = {
        "schema": "long.c59e@1",
        "object": "c59x_signed_edge_ansatz",
        "status": STATUS if all(checks.values()) else "LONG_C59E_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.c59e.report@1",
        "status": c59e["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_c59e aggregates the signed C59X route rows into a finite "
            "directed-edge ansatz. The ansatz has exact global conservation "
            "and an explicit controlled local defect table. It does not certify "
            "a physical stress-energy tensor, a smooth metric, or a "
            "thermal-gravity derivation."
        ),
        "stage_protocol": {
            "draft": "read long_c59x routes and directed stress edges",
            "witness": "emit signed route flux rows, edge aggregates, node balances, mode totals, gaps, and observables",
            "coherence": "check signed route counts, mode totals, global divergence, controlled local defect, and physical exclusions",
            "closure": "certify finite signed edge ansatz with global conservation and explicit local defect",
            "emit": "write long_c59e artifacts and verifier hook",
        },
        "inputs": {
            "long_c59x": input_entry(
                LONG_C59X,
                {
                    "status": rows["c59x"].get("status"),
                    "certificate_sha256": rows["c59x"].get("certificate_sha256"),
                },
            ),
            "long_c59x_route": input_entry(LONG_C59X_ROUTE),
            "long_c59x_sentinel": input_entry(LONG_C59X_SENTINEL),
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
            "c59e": relpath(OUT_DIR / "c59e.json"),
            "route_flux_csv": relpath(OUT_DIR / "route_flux.csv"),
            "edge_flux_csv": relpath(OUT_DIR / "edge_flux.csv"),
            "node_balance_csv": relpath(OUT_DIR / "node_balance.csv"),
            "mode_csv": relpath(OUT_DIR / "mode.csv"),
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
                "a finite signed directed-edge ansatz from the 118 C59X route rows",
                "edge-level aggregation over the materialized routed stress edges",
                "exact global divergence zero across the 20-node balance table",
                "a controlled explicit local defect table where local conservation is not closed",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "local conservation at every node",
                "a physical stress-energy tensor",
                "a smooth Lorentzian metric",
                "curvature, Einstein tensor, or field equations",
                "a thermal-gravity derivation",
            ],
        },
        "next_highest_yield_item": (
            "Try to cancel the local defect by adding the minimal counterflow "
            "on existing directed stress edges, or certify the residual defect "
            "as the finite source obstruction."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.c59e.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.c59e.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "c59e": c59e,
        "route_flux_csv": csv_text(ROUTE_FLUX_COLUMNS, rows["route_flux_rows"]),
        "edge_flux_csv": csv_text(EDGE_FLUX_COLUMNS, rows["edge_flux_rows"]),
        "node_balance_csv": csv_text(NODE_BALANCE_COLUMNS, rows["node_balance_rows"]),
        "mode_csv": csv_text(MODE_COLUMNS, rows["mode_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "route_flux_table": route_flux_table,
        "edge_flux_table": edge_flux_table,
        "node_balance_table": node_balance_table,
        "mode_table": mode_table,
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
    write_json(OUT_DIR / "c59e.json", payloads["c59e"])
    (OUT_DIR / "route_flux.csv").write_text(
        payloads["route_flux_csv"], encoding="utf-8"
    )
    (OUT_DIR / "edge_flux.csv").write_text(
        payloads["edge_flux_csv"], encoding="utf-8"
    )
    (OUT_DIR / "node_balance.csv").write_text(
        payloads["node_balance_csv"], encoding="utf-8"
    )
    (OUT_DIR / "mode.csv").write_text(payloads["mode_csv"], encoding="utf-8")
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        route_flux_table=payloads["route_flux_table"],
        edge_flux_table=payloads["edge_flux_table"],
        node_balance_table=payloads["node_balance_table"],
        mode_table=payloads["mode_table"],
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
