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


THEOREM_ID = "long_semstress"
STATUS = "LONG_SEMSTRESS_NODE_SOURCE_MEASURE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_RSEM = PROOF_ROOT / "long_rsem" / "report.json"
LONG_RSEM_RELATION = PROOF_ROOT / "long_rsem" / "relation.csv"
LONG_STRESS20 = PROOF_ROOT / "long_stress20" / "report.json"
LONG_STRESS20_NODE = PROOF_ROOT / "long_stress20" / "node.csv"
LONG_STRESS_GATE = PROOF_ROOT / "long_stress_gate" / "report.json"
LONG_STRESS_EDGE = PROOF_ROOT / "long_stress_gate" / "stress_edge.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_semstress.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_semstress.py"

SOURCE_COLUMNS = [
    "atom_id",
    "semantic_row_count",
    "stress_node_present_flag",
    "source_present_flag",
    "thermal_weight_num",
    "thermal_weight_den",
    "stress_neighbor_count",
    "stress_complement",
    "signed_tension_scaled",
    "complement_source_count",
    "complement_imbalance",
]
COMPLEMENT_COLUMNS = [
    "pair_id",
    "atom_id",
    "complement_atom",
    "source_count",
    "complement_source_count",
    "pair_source_count",
    "imbalance_abs",
    "signed_tension_sum_scaled",
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
    "semantic_to_stress_node_source",
    "normalized_finite_source_measure",
    "stress_edge_coupling_map",
    "physical_stress_energy_tensor",
    "smooth_lorentzian_metric",
    "thermal_gravity_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "semantic_relation_row_count",
    "stress_node_count",
    "stress_edge_row_count",
    "semantic_source_node_count",
    "relation_to_node_map_count",
    "relation_to_edge_map_count",
    "source_total_mass",
    "normalized_source_measure_flag",
    "all_semantic_rows_node_mapped_flag",
    "all_stress_nodes_hit_flag",
    "complement_pair_count",
    "complement_tension_zero_pair_count",
    "complement_source_imbalanced_pair_count",
    "node_source_bridge_flag",
    "edge_coupling_flag",
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


def build_rows() -> dict[str, Any]:
    rsem = load_json(LONG_RSEM)
    stress20 = load_json(LONG_STRESS20)
    stress_gate = load_json(LONG_STRESS_GATE)
    relation_rows = read_csv_int(LONG_RSEM_RELATION)
    node_rows_source = read_csv_int(LONG_STRESS20_NODE)
    edge_rows = read_csv_int(LONG_STRESS_EDGE)
    node_by_atom = {row["atom_id"]: row for row in node_rows_source}

    counts = {atom_id: 0 for atom_id in range(20)}
    for row in relation_rows:
        counts[row["visible_index"]] += 1

    source_rows = []
    total_mass = len(relation_rows)
    for atom_id in range(20):
        node = node_by_atom[atom_id]
        complement = node["stress_complement"]
        count = counts[atom_id]
        source_rows.append(
            {
                "atom_id": atom_id,
                "semantic_row_count": count,
                "stress_node_present_flag": 1,
                "source_present_flag": int(count > 0),
                "thermal_weight_num": count,
                "thermal_weight_den": total_mass,
                "stress_neighbor_count": node["stress_neighbor_count"],
                "stress_complement": complement,
                "signed_tension_scaled": node["signed_tension_scaled"],
                "complement_source_count": counts[complement],
                "complement_imbalance": count - counts[complement],
            }
        )

    pair_rows = []
    seen = set()
    for atom_id in range(20):
        complement = node_by_atom[atom_id]["stress_complement"]
        key = tuple(sorted((atom_id, complement)))
        if key in seen:
            continue
        seen.add(key)
        tension_sum = (
            node_by_atom[atom_id]["signed_tension_scaled"]
            + node_by_atom[complement]["signed_tension_scaled"]
        )
        imbalance = abs(counts[atom_id] - counts[complement])
        pair_rows.append(
            {
                "pair_id": len(pair_rows),
                "atom_id": key[0],
                "complement_atom": key[1],
                "source_count": counts[key[0]],
                "complement_source_count": counts[key[1]],
                "pair_source_count": counts[key[0]] + counts[key[1]],
                "imbalance_abs": imbalance,
                "signed_tension_sum_scaled": tension_sum,
            }
        )

    obs = {
        "input_report_count": 3,
        "input_certified_count": sum(
            certified(report) for report in [rsem, stress20, stress_gate]
        ),
        "semantic_relation_row_count": len(relation_rows),
        "stress_node_count": len(node_rows_source),
        "stress_edge_row_count": len(edge_rows),
        "semantic_source_node_count": sum(
            row["source_present_flag"] for row in source_rows
        ),
        "relation_to_node_map_count": len(relation_rows),
        "relation_to_edge_map_count": 0,
        "source_total_mass": sum(row["semantic_row_count"] for row in source_rows),
        "normalized_source_measure_flag": int(
            total_mass == sum(row["thermal_weight_num"] for row in source_rows)
            and all(row["thermal_weight_den"] == total_mass for row in source_rows)
        ),
        "all_semantic_rows_node_mapped_flag": int(
            len(relation_rows) == sum(row["semantic_row_count"] for row in source_rows)
        ),
        "all_stress_nodes_hit_flag": int(
            all(row["source_present_flag"] == 1 for row in source_rows)
        ),
        "complement_pair_count": len(pair_rows),
        "complement_tension_zero_pair_count": sum(
            row["signed_tension_sum_scaled"] == 0 for row in pair_rows
        ),
        "complement_source_imbalanced_pair_count": sum(
            row["imbalance_abs"] != 0 for row in pair_rows
        ),
        "node_source_bridge_flag": 1,
        "edge_coupling_flag": 0,
        "physical_stress_energy_flag": 0,
        "smooth_metric_flag": 0,
        "thermal_gravity_flag": 0,
        "next_gap_code": GAP_CODES["stress_edge_coupling_map"],
    }
    gap_rows = [
        {
            "gap_id": GAP_CODES["semantic_to_stress_node_source"],
            "gap_code": GAP_CODES["semantic_to_stress_node_source"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["normalized_finite_source_measure"],
            "gap_code": GAP_CODES["normalized_finite_source_measure"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["stress_edge_coupling_map"],
            "gap_code": GAP_CODES["stress_edge_coupling_map"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 1,
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
        "rsem": rsem,
        "stress20": stress20,
        "stress_gate": stress_gate,
        "relation_rows": relation_rows,
        "source_rows": source_rows,
        "pair_rows": pair_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    source_table = table_from_rows(SOURCE_COLUMNS, rows["source_rows"])
    complement_table = table_from_rows(COMPLEMENT_COLUMNS, rows["pair_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "semantic_rows_map_to_all_stress_nodes": obs[
            "semantic_relation_row_count"
        ]
        == 59
        and obs["stress_node_count"] == 20
        and obs["semantic_source_node_count"] == 20
        and obs["relation_to_node_map_count"] == 59
        and obs["all_semantic_rows_node_mapped_flag"] == 1
        and obs["all_stress_nodes_hit_flag"] == 1,
        "finite_source_measure_normalized": obs["source_total_mass"] == 59
        and obs["normalized_source_measure_flag"] == 1,
        "stress_complement_surface_coheres": obs["complement_pair_count"] == 10
        and obs["complement_tension_zero_pair_count"] == 10,
        "edge_tensor_metric_boundaries_preserved": obs["relation_to_edge_map_count"]
        == 0
        and obs["edge_coupling_flag"] == 0
        and obs["physical_stress_energy_flag"] == 0
        and obs["smooth_metric_flag"] == 0
        and obs["thermal_gravity_flag"] == 0,
        "table_shapes_match": source_table.shape == (20, len(SOURCE_COLUMNS))
        and complement_table.shape == (10, len(COMPLEMENT_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "semantic_stress_node_source_measure",
        "summary": {
            "semantic_relation_row_count": obs["semantic_relation_row_count"],
            "stress_node_count": obs["stress_node_count"],
            "stress_edge_row_count": obs["stress_edge_row_count"],
            "semantic_source_node_count": obs["semantic_source_node_count"],
            "source_total_mass": obs["source_total_mass"],
            "normalized_source_measure_flag": obs[
                "normalized_source_measure_flag"
            ],
            "node_source_bridge_flag": obs["node_source_bridge_flag"],
            "relation_to_edge_map_count": obs["relation_to_edge_map_count"],
            "edge_coupling_flag": obs["edge_coupling_flag"],
            "physical_stress_energy_flag": obs["physical_stress_energy_flag"],
            "smooth_metric_flag": obs["smooth_metric_flag"],
            "thermal_gravity_flag": obs["thermal_gravity_flag"],
            "complement_source_imbalanced_pair_count": obs[
                "complement_source_imbalanced_pair_count"
            ],
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "source_table_sha256": sha_array(source_table),
        "source_text_sha256": sha_text(csv_text(SOURCE_COLUMNS, rows["source_rows"])),
        "complement_table_sha256": sha_array(complement_table),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    semstress = {
        "schema": "long.semstress@1",
        "object": "semantic_stress_node_source_measure",
        "status": STATUS if all(checks.values()) else "LONG_SEMSTRESS_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.semstress.report@1",
        "status": semstress["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_semstress certifies the first semantics-to-stress bridge "
            "that survives the current boundary: the 59 guarded semantic rows "
            "map through visible_index to all 20 finite stress nodes and define "
            "a normalized finite source measure of total mass 59. It does not "
            "certify a stress-edge coupling map, physical stress-energy tensor, "
            "smooth metric, or thermal-gravity derivation."
        ),
        "stage_protocol": {
            "draft": "read long_rsem relation rows, long_stress20 node rows, and long_stress_gate stress edges",
            "witness": "emit semantic source-node rows, complement-pair rows, gap rows, and observables",
            "coherence": "check node coverage, normalized source mass, complement tension pairing, and edge/tensor/metric exclusions",
            "closure": "certify the finite node-level semantic stress source while preserving the edge/tensor gap",
            "emit": "write long_semstress artifacts and verifier hook",
        },
        "inputs": {
            "long_rsem": input_entry(
                LONG_RSEM,
                {
                    "status": rows["rsem"].get("status"),
                    "certificate_sha256": rows["rsem"].get("certificate_sha256"),
                },
            ),
            "long_rsem_relation": input_entry(LONG_RSEM_RELATION),
            "long_stress20": input_entry(
                LONG_STRESS20,
                {
                    "status": rows["stress20"].get("status"),
                    "certificate_sha256": rows["stress20"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_stress20_node": input_entry(LONG_STRESS20_NODE),
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
            "semstress": relpath(OUT_DIR / "semstress.json"),
            "source_csv": relpath(OUT_DIR / "source.csv"),
            "complement_csv": relpath(OUT_DIR / "complement.csv"),
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
                "all 59 guarded semantic rows map to finite stress nodes by visible_index",
                "all 20 finite stress nodes receive at least one semantic source row",
                "the induced finite source measure is normalized with total mass 59",
                "the 10 complement pairs have antisymmetric signed-tension sums",
                "the bridge is node-level only, not edge-level or tensor-level",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "a certified semantic-row to stress-edge coupling map",
                "a physical stress-energy tensor",
                "a smooth Lorentzian metric",
                "curvature, Einstein tensor, or field equations",
                "a thermal-gravity derivation",
            ],
        },
        "next_highest_yield_item": (
            "Materialize or obstruct a canonical rule that sends each semantic "
            "source node to directed stress edges. That is the next hard seam "
            "before any stress-energy or thermal metric claim."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.semstress.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.semstress.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "semstress": semstress,
        "source_csv": csv_text(SOURCE_COLUMNS, rows["source_rows"]),
        "complement_csv": csv_text(COMPLEMENT_COLUMNS, rows["pair_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "source_table": source_table,
        "complement_table": complement_table,
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
    write_json(OUT_DIR / "semstress.json", payloads["semstress"])
    (OUT_DIR / "source.csv").write_text(payloads["source_csv"], encoding="utf-8")
    (OUT_DIR / "complement.csv").write_text(
        payloads["complement_csv"], encoding="utf-8"
    )
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        source_table=payloads["source_table"],
        complement_table=payloads["complement_table"],
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
