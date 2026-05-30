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


THEOREM_ID = "long_c59x"
STATUS = "LONG_C59X_SIGNED_SENTINEL_EDGE_ROUTING_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_SEMSTRESS = PROOF_ROOT / "long_semstress" / "report.json"
LONG_SEMSTRESS_SOURCE = PROOF_ROOT / "long_semstress" / "source.csv"
LONG_RSEM = PROOF_ROOT / "long_rsem" / "report.json"
LONG_RSEM_RELATION = PROOF_ROOT / "long_rsem" / "relation.csv"
LONG_STRESS_GATE = PROOF_ROOT / "long_stress_gate" / "report.json"
LONG_STRESS_EDGE = PROOF_ROOT / "long_stress_gate" / "stress_edge.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_c59x.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_c59x.py"

SENTINEL_COLUMNS = [
    "sentinel_mode_id",
    "sentinel_code",
    "sentinel_sign",
    "carrier_count",
    "sentinel_count",
    "closure_total",
    "signed_route_count",
    "formal_route_flag",
    "physical_validation_flag",
]
ROUTE_COLUMNS = [
    "route_id",
    "relation_id",
    "visible_index",
    "sentinel_mode_id",
    "sentinel_sign",
    "source_atom",
    "stress_edge_id",
    "edge_source_atom",
    "edge_target_atom",
    "signed_tension_scaled",
    "weight_scaled",
    "sign_match_flag",
    "outgoing_source_flag",
    "formal_route_flag",
    "physical_stress_energy_flag",
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

SENTINEL_NAMES = [
    "C59N_PLUS_SIGNED_SENTINEL",
    "C59B_MINUS_SIGNED_SENTINEL",
]
SENTINEL_CODES = {name: index for index, name in enumerate(SENTINEL_NAMES)}
SENTINEL_SIGNS = {
    SENTINEL_CODES["C59N_PLUS_SIGNED_SENTINEL"]: 1,
    SENTINEL_CODES["C59B_MINUS_SIGNED_SENTINEL"]: -1,
}

GAP_NAMES = [
    "c59x_signed_sentinel_rule",
    "semantic_row_to_directed_stress_edge_route",
    "physical_stress_energy_tensor",
    "smooth_lorentzian_metric",
    "thermal_gravity_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "semantic_carrier_count",
    "sentinel_count",
    "closure_total",
    "sentinel_mode_count",
    "signed_route_row_count",
    "expected_signed_route_row_count",
    "positive_route_row_count",
    "negative_route_row_count",
    "materialized_stress_edge_count",
    "source_node_count",
    "positive_source_node_count",
    "negative_source_node_count",
    "all_routes_materialized_flag",
    "all_routes_outgoing_flag",
    "all_routes_sign_matched_flag",
    "formal_edge_routing_flag",
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


def pick_edge(edge_rows: list[dict[str, int]], source_atom: int, sign: int) -> dict[str, int]:
    candidates = [
        row
        for row in edge_rows
        if row["source_atom"] == source_atom
        and row["signed_tension_scaled"] * sign > 0
    ]
    if not candidates:
        raise AssertionError(f"no signed stress edge for atom {source_atom}, sign {sign}")
    candidates.sort(
        key=lambda row: (
            -abs(row["signed_tension_scaled"]),
            -row["weight_scaled"],
            row["stress_edge_id"],
        )
    )
    return candidates[0]


def build_rows() -> dict[str, Any]:
    semstress = load_json(LONG_SEMSTRESS)
    rsem = load_json(LONG_RSEM)
    stress_gate = load_json(LONG_STRESS_GATE)
    source_rows = read_csv_int(LONG_SEMSTRESS_SOURCE)
    relation_rows = read_csv_int(LONG_RSEM_RELATION)
    edge_rows = read_csv_int(LONG_STRESS_EDGE)

    sentinel_rows = []
    for mode_id, sign in SENTINEL_SIGNS.items():
        sentinel_rows.append(
            {
                "sentinel_mode_id": mode_id,
                "sentinel_code": mode_id,
                "sentinel_sign": sign,
                "carrier_count": len(relation_rows),
                "sentinel_count": 1,
                "closure_total": len(relation_rows) + 1,
                "signed_route_count": len(relation_rows),
                "formal_route_flag": 1,
                "physical_validation_flag": 0,
            }
        )

    route_rows = []
    route_id = 0
    for mode_id, sign in SENTINEL_SIGNS.items():
        for relation in relation_rows:
            source_atom = relation["visible_index"]
            edge = pick_edge(edge_rows, source_atom, sign)
            route_rows.append(
                {
                    "route_id": route_id,
                    "relation_id": relation["relation_id"],
                    "visible_index": relation["visible_index"],
                    "sentinel_mode_id": mode_id,
                    "sentinel_sign": sign,
                    "source_atom": source_atom,
                    "stress_edge_id": edge["stress_edge_id"],
                    "edge_source_atom": edge["source_atom"],
                    "edge_target_atom": edge["target_atom"],
                    "signed_tension_scaled": edge["signed_tension_scaled"],
                    "weight_scaled": edge["weight_scaled"],
                    "sign_match_flag": int(edge["signed_tension_scaled"] * sign > 0),
                    "outgoing_source_flag": int(edge["source_atom"] == source_atom),
                    "formal_route_flag": 1,
                    "physical_stress_energy_flag": 0,
                }
            )
            route_id += 1

    positive_rows = [
        row for row in route_rows if row["sentinel_sign"] > 0
    ]
    negative_rows = [
        row for row in route_rows if row["sentinel_sign"] < 0
    ]
    obs = {
        "input_report_count": 3,
        "input_certified_count": sum(
            certified(report) for report in [semstress, rsem, stress_gate]
        ),
        "semantic_carrier_count": len(relation_rows),
        "sentinel_count": 1,
        "closure_total": len(relation_rows) + 1,
        "sentinel_mode_count": len(sentinel_rows),
        "signed_route_row_count": len(route_rows),
        "expected_signed_route_row_count": len(relation_rows) * len(sentinel_rows),
        "positive_route_row_count": len(positive_rows),
        "negative_route_row_count": len(negative_rows),
        "materialized_stress_edge_count": len(
            {row["stress_edge_id"] for row in route_rows}
        ),
        "source_node_count": len(source_rows),
        "positive_source_node_count": len(
            {row["source_atom"] for row in positive_rows}
        ),
        "negative_source_node_count": len(
            {row["source_atom"] for row in negative_rows}
        ),
        "all_routes_materialized_flag": int(
            all(row["stress_edge_id"] >= 0 for row in route_rows)
        ),
        "all_routes_outgoing_flag": int(
            all(row["outgoing_source_flag"] == 1 for row in route_rows)
        ),
        "all_routes_sign_matched_flag": int(
            all(row["sign_match_flag"] == 1 for row in route_rows)
        ),
        "formal_edge_routing_flag": 1,
        "physical_stress_energy_flag": 0,
        "smooth_metric_flag": 0,
        "thermal_gravity_flag": 0,
        "next_gap_code": GAP_CODES["physical_stress_energy_tensor"],
    }
    gap_rows = [
        {
            "gap_id": GAP_CODES["c59x_signed_sentinel_rule"],
            "gap_code": GAP_CODES["c59x_signed_sentinel_rule"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["semantic_row_to_directed_stress_edge_route"],
            "gap_code": GAP_CODES["semantic_row_to_directed_stress_edge_route"],
            "certified_flag": 1,
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
            "next_flag": 1,
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
        "semstress": semstress,
        "rsem": rsem,
        "stress_gate": stress_gate,
        "source_rows": source_rows,
        "relation_rows": relation_rows,
        "edge_rows": edge_rows,
        "sentinel_rows": sentinel_rows,
        "route_rows": route_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    sentinel_table = table_from_rows(SENTINEL_COLUMNS, rows["sentinel_rows"])
    route_table = table_from_rows(ROUTE_COLUMNS, rows["route_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    semstress_s = summary(rows["semstress"])
    checks = {
        "input_reports_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "semstress_node_source_available": semstress_s["node_source_bridge_flag"] == 1
        and semstress_s["normalized_source_measure_flag"] == 1,
        "c59x_split_exact": obs["semantic_carrier_count"] == 59
        and obs["sentinel_count"] == 1
        and obs["closure_total"] == 60
        and obs["sentinel_mode_count"] == 2,
        "signed_routes_materialized": obs["signed_route_row_count"]
        == obs["expected_signed_route_row_count"]
        == 118
        and obs["positive_route_row_count"] == 59
        and obs["negative_route_row_count"] == 59
        and obs["all_routes_materialized_flag"] == 1
        and obs["all_routes_outgoing_flag"] == 1
        and obs["all_routes_sign_matched_flag"] == 1,
        "source_nodes_covered_in_both_modes": obs["source_node_count"] == 20
        and obs["positive_source_node_count"] == 20
        and obs["negative_source_node_count"] == 20,
        "physical_metric_boundaries_preserved": obs["formal_edge_routing_flag"] == 1
        and obs["physical_stress_energy_flag"] == 0
        and obs["smooth_metric_flag"] == 0
        and obs["thermal_gravity_flag"] == 0,
        "table_shapes_match": sentinel_table.shape
        == (2, len(SENTINEL_COLUMNS))
        and route_table.shape == (118, len(ROUTE_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "c59x_signed_sentinel_edge_routing",
        "summary": {
            "semantic_carrier_count": obs["semantic_carrier_count"],
            "sentinel_count": obs["sentinel_count"],
            "closure_total": obs["closure_total"],
            "sentinel_mode_count": obs["sentinel_mode_count"],
            "signed_route_row_count": obs["signed_route_row_count"],
            "positive_route_row_count": obs["positive_route_row_count"],
            "negative_route_row_count": obs["negative_route_row_count"],
            "materialized_stress_edge_count": obs["materialized_stress_edge_count"],
            "positive_source_node_count": obs["positive_source_node_count"],
            "negative_source_node_count": obs["negative_source_node_count"],
            "formal_edge_routing_flag": obs["formal_edge_routing_flag"],
            "physical_stress_energy_flag": obs["physical_stress_energy_flag"],
            "smooth_metric_flag": obs["smooth_metric_flag"],
            "thermal_gravity_flag": obs["thermal_gravity_flag"],
        },
        "sentinel_code_map": {
            str(value): key for key, value in SENTINEL_CODES.items()
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "sentinel_table_sha256": sha_array(sentinel_table),
        "sentinel_text_sha256": sha_text(
            csv_text(SENTINEL_COLUMNS, rows["sentinel_rows"])
        ),
        "route_table_sha256": sha_array(route_table),
        "route_text_sha256": sha_text(csv_text(ROUTE_COLUMNS, rows["route_rows"])),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    c59x = {
        "schema": "long.c59x@1",
        "object": "c59x_signed_sentinel_edge_routing",
        "status": STATUS if all(checks.values()) else "LONG_C59X_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.c59x.report@1",
        "status": c59x["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_c59x certifies a formal C59X signed-sentinel rule on top of "
            "long_semstress: 59 semantic carrier rows plus one sentinel close "
            "to a 60-site split, and the positive/negative sentinel modes route "
            "every carrier row to materialized outgoing directed stress edges "
            "with matching signed tension. The result is a formal edge-routing "
            "law, not a physical stress-energy tensor or thermal-gravity claim."
        ),
        "stage_protocol": {
            "draft": "read long_semstress, long_rsem relation rows, and directed stress edges",
            "witness": "emit sentinel modes, signed route rows, gap rows, and observables",
            "coherence": "check 59+1 split, two signed modes, 118 materialized signed routes, source-node coverage, and physical exclusions",
            "closure": "certify formal C59X signed sentinel routing from semantic rows to directed stress edges",
            "emit": "write long_c59x artifacts and verifier hook",
        },
        "inputs": {
            "long_semstress": input_entry(
                LONG_SEMSTRESS,
                {
                    "status": rows["semstress"].get("status"),
                    "certificate_sha256": rows["semstress"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_semstress_source": input_entry(LONG_SEMSTRESS_SOURCE),
            "long_rsem": input_entry(
                LONG_RSEM,
                {
                    "status": rows["rsem"].get("status"),
                    "certificate_sha256": rows["rsem"].get("certificate_sha256"),
                },
            ),
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
            "c59x": relpath(OUT_DIR / "c59x.json"),
            "sentinel_csv": relpath(OUT_DIR / "sentinel.csv"),
            "route_csv": relpath(OUT_DIR / "route.csv"),
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
                "a formal C59X 59+1 carrier/sentinel split over the 59 semantic rows",
                "two signed sentinel modes: C59N_PLUS and C59B_MINUS",
                "118 signed semantic-row routes to materialized outgoing directed stress edges",
                "positive and negative routes cover all 20 semantic source nodes",
                "each route matches the selected sentinel sign against directed-edge tension",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "a physical stress-energy tensor",
                "a smooth Lorentzian metric",
                "curvature, Einstein tensor, or field equations",
                "a thermal-gravity derivation",
                "chemical stability, synthesis, or transport measurement",
            ],
        },
        "next_highest_yield_item": (
            "Feed the signed C59X route rows into a finite stress-energy ansatz: "
            "aggregate signed route weights by source/target edge and test "
            "whether conservation or a controlled defect survives."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.c59x.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.c59x.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "c59x": c59x,
        "sentinel_csv": csv_text(SENTINEL_COLUMNS, rows["sentinel_rows"]),
        "route_csv": csv_text(ROUTE_COLUMNS, rows["route_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "sentinel_table": sentinel_table,
        "route_table": route_table,
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
    write_json(OUT_DIR / "c59x.json", payloads["c59x"])
    (OUT_DIR / "sentinel.csv").write_text(
        payloads["sentinel_csv"], encoding="utf-8"
    )
    (OUT_DIR / "route.csv").write_text(payloads["route_csv"], encoding="utf-8")
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        sentinel_table=payloads["sentinel_table"],
        route_table=payloads["route_table"],
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
