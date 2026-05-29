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
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_stress_gate"
STATUS = "LONG_STRESS_GATE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

PROOF_ROOT = D20_INVARIANTS / "proof_obligations"
LONG_TRANSITION_SEM = PROOF_ROOT / "long_transition_sem" / "report.json"
LONG_TRANSITION_CSV = PROOF_ROOT / "long_transition_sem" / "transition.csv"
LONG_STRESS20 = PROOF_ROOT / "long_stress20" / "report.json"
STRESS = PROOF_ROOT / "c985_d20_boundary_neighborhood_stress_graph" / "report.json"
STRESS_ARTIFACT = (
    PROOF_ROOT / "c985_d20_boundary_neighborhood_stress_graph" / "artifact.json"
)

DERIVE_SCRIPT = ROOT / "src" / "derive_long_stress_gate.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_stress_gate.py"

SCALE = 10_000_000_000

STRESS_EDGE_COLUMNS = [
    "stress_edge_id",
    "source_atom",
    "target_atom",
    "weight_scaled",
    "signed_tension_scaled",
    "complement_edge_flag",
    "cycle_edge_flag",
    "cycle_antipode_edge_flag",
]
SURFACE_COLUMNS = [
    "surface_id",
    "surface_code",
    "certified_input_flag",
    "finite_readout_flag",
    "transition_backed_flag",
    "stress_backed_flag",
    "obstruction_flag",
    "count_value",
]
GAP_COLUMNS = ["gap_id", "gap_code", "open_flag", "obstruction_flag", "next_flag"]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

SURFACE_NAMES = [
    "guarded_unit_time_transition_surface",
    "finite_stress_neighborhood_surface",
    "stress_complement_surface",
    "stress_20gon_comparison_surface",
    "transition_to_stress_coupling_law",
    "physical_stress_energy_tensor",
    "smooth_metric_einstein_source",
]
SURFACE_CODES = {name: index for index, name in enumerate(SURFACE_NAMES)}

GAP_NAMES = [
    "finite_stress_readout",
    "stress_transition_coupling_map",
    "physical_stress_energy_tensor",
    "nondegenerate_smooth_lorentzian_metric",
    "curvature_and_einstein_tensor",
    "gr_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "transition_row_count",
    "transition_delta_sum",
    "semantic_transition_realized_count",
    "stress_node_count",
    "stress_directed_edge_count",
    "stress_undirected_edge_count",
    "stress_row_degree_min",
    "stress_row_degree_max",
    "stress_complement_pair_count",
    "stress_complement_directed_edge_count",
    "stress_cycle_directed_overlap_count",
    "stress_cycle_undirected_overlap_count",
    "stress_equals_20gon_flag",
    "finite_stress_readout_flag",
    "transition_stress_edge_map_count",
    "transition_stress_coupling_flag",
    "physical_stress_energy_flag",
    "smooth_lorentzian_metric_flag",
    "curvature_einstein_tensor_flag",
    "gr_derivation_flag",
    "open_gap_count",
    "next_gap_code",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _stress_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    witness = report.get("witness")
    if not isinstance(witness, dict):
        raise AssertionError("stress witness missing")
    graph_rows = witness.get("graph_rows")
    if not isinstance(graph_rows, list):
        raise AssertionError("stress graph_rows missing")
    return graph_rows


def build_rows() -> dict[str, Any]:
    transition_sem = load_json(LONG_TRANSITION_SEM)
    transition_rows = read_csv_rows(LONG_TRANSITION_CSV)
    stress20 = load_json(LONG_STRESS20)
    stress = load_json(STRESS)
    stress_artifact = load_json(STRESS_ARTIFACT)
    graph_rows = _stress_rows(stress)

    node_count = len(graph_rows)
    cycle_undirected = {
        tuple(sorted((atom, (atom + 1) % node_count))) for atom in range(node_count)
    }
    complement = {int(row["atom_id"]): int(row["complement_atom_id"]) for row in graph_rows}
    stress_edge_rows: list[dict[str, int]] = []
    for row in graph_rows:
        source = int(row["atom_id"])
        for neighbor in row["neighbors"]:
            target = int(neighbor["atom_id"])
            stress_edge_rows.append(
                {
                    "stress_edge_id": len(stress_edge_rows),
                    "source_atom": source,
                    "target_atom": target,
                    "weight_scaled": int(round(float(neighbor["weight"]) * SCALE)),
                    "signed_tension_scaled": int(
                        round(float(neighbor["signed_tension"]) * SCALE)
                    ),
                    "complement_edge_flag": int(target == complement[source]),
                    "cycle_edge_flag": int(tuple(sorted((source, target))) in cycle_undirected),
                    "cycle_antipode_edge_flag": int(
                        target == (source + node_count // 2) % node_count
                    ),
                }
            )

    transition_count = len(transition_rows)
    transition_delta_sum = sum(int(row["normal_form_delta_t"]) for row in transition_rows)
    semantic_transition_count = sum(
        int(row["semantic_transition_flag"]) for row in transition_rows
    )
    stress20_summary = stress20["witness"]["summary"]
    obs = {
        "input_report_count": 3,
        "input_certified_count": 3,
        "transition_row_count": transition_count,
        "transition_delta_sum": transition_delta_sum,
        "semantic_transition_realized_count": semantic_transition_count,
        "stress_node_count": int(stress20_summary["stress_node_count"]),
        "stress_directed_edge_count": int(stress20_summary["stress_directed_edge_count"]),
        "stress_undirected_edge_count": int(
            stress20_summary["stress_undirected_edge_count"]
        ),
        "stress_row_degree_min": min(
            sum(1 for edge in stress_edge_rows if edge["source_atom"] == atom)
            for atom in range(node_count)
        ),
        "stress_row_degree_max": max(
            sum(1 for edge in stress_edge_rows if edge["source_atom"] == atom)
            for atom in range(node_count)
        ),
        "stress_complement_pair_count": int(stress20_summary["complement_pair_count"]),
        "stress_complement_directed_edge_count": sum(
            row["complement_edge_flag"] for row in stress_edge_rows
        ),
        "stress_cycle_directed_overlap_count": sum(
            row["cycle_edge_flag"] for row in stress_edge_rows
        ),
        "stress_cycle_undirected_overlap_count": int(
            stress20_summary["cycle_undirected_overlap_count"]
        ),
        "stress_equals_20gon_flag": int(stress20_summary["stress_equals_20gon_flag"]),
        "finite_stress_readout_flag": 1,
        "transition_stress_edge_map_count": 0,
        "transition_stress_coupling_flag": 0,
        "physical_stress_energy_flag": 0,
        "smooth_lorentzian_metric_flag": 0,
        "curvature_einstein_tensor_flag": 0,
        "gr_derivation_flag": 0,
        "open_gap_count": 5,
        "next_gap_code": GAP_CODES["stress_transition_coupling_map"],
    }
    surface_rows = [
        {
            "surface_id": SURFACE_CODES["guarded_unit_time_transition_surface"],
            "surface_code": SURFACE_CODES["guarded_unit_time_transition_surface"],
            "certified_input_flag": 1,
            "finite_readout_flag": 1,
            "transition_backed_flag": 1,
            "stress_backed_flag": 0,
            "obstruction_flag": 0,
            "count_value": obs["transition_row_count"],
        },
        {
            "surface_id": SURFACE_CODES["finite_stress_neighborhood_surface"],
            "surface_code": SURFACE_CODES["finite_stress_neighborhood_surface"],
            "certified_input_flag": 1,
            "finite_readout_flag": 1,
            "transition_backed_flag": 0,
            "stress_backed_flag": 1,
            "obstruction_flag": 0,
            "count_value": obs["stress_directed_edge_count"],
        },
        {
            "surface_id": SURFACE_CODES["stress_complement_surface"],
            "surface_code": SURFACE_CODES["stress_complement_surface"],
            "certified_input_flag": 1,
            "finite_readout_flag": 1,
            "transition_backed_flag": 0,
            "stress_backed_flag": 1,
            "obstruction_flag": 0,
            "count_value": obs["stress_complement_pair_count"],
        },
        {
            "surface_id": SURFACE_CODES["stress_20gon_comparison_surface"],
            "surface_code": SURFACE_CODES["stress_20gon_comparison_surface"],
            "certified_input_flag": 1,
            "finite_readout_flag": 1,
            "transition_backed_flag": 0,
            "stress_backed_flag": 1,
            "obstruction_flag": 1,
            "count_value": obs["stress_equals_20gon_flag"],
        },
        {
            "surface_id": SURFACE_CODES["transition_to_stress_coupling_law"],
            "surface_code": SURFACE_CODES["transition_to_stress_coupling_law"],
            "certified_input_flag": 0,
            "finite_readout_flag": 0,
            "transition_backed_flag": 1,
            "stress_backed_flag": 1,
            "obstruction_flag": 1,
            "count_value": obs["transition_stress_edge_map_count"],
        },
        {
            "surface_id": SURFACE_CODES["physical_stress_energy_tensor"],
            "surface_code": SURFACE_CODES["physical_stress_energy_tensor"],
            "certified_input_flag": 0,
            "finite_readout_flag": 0,
            "transition_backed_flag": 0,
            "stress_backed_flag": 1,
            "obstruction_flag": 1,
            "count_value": obs["physical_stress_energy_flag"],
        },
        {
            "surface_id": SURFACE_CODES["smooth_metric_einstein_source"],
            "surface_code": SURFACE_CODES["smooth_metric_einstein_source"],
            "certified_input_flag": 0,
            "finite_readout_flag": 0,
            "transition_backed_flag": 0,
            "stress_backed_flag": 0,
            "obstruction_flag": 1,
            "count_value": obs["curvature_einstein_tensor_flag"],
        },
    ]
    gap_rows = [
        {
            "gap_id": code,
            "gap_code": code,
            "open_flag": int(name != "finite_stress_readout"),
            "obstruction_flag": int(name != "finite_stress_readout"),
            "next_flag": int(name == "stress_transition_coupling_map"),
        }
        for name, code in GAP_CODES.items()
    ]
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    return {
        "transition_sem": transition_sem,
        "transition_rows": transition_rows,
        "stress20": stress20,
        "stress": stress,
        "stress_artifact": stress_artifact,
        "stress_edge_rows": stress_edge_rows,
        "surface_rows": surface_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "stress_edge_table": table_from_rows(STRESS_EDGE_COLUMNS, stress_edge_rows),
        "surface_table": table_from_rows(SURFACE_COLUMNS, surface_rows),
        "gap_table": table_from_rows(GAP_COLUMNS, gap_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "stress_edge_text_hash": sha_text(
            digest_text(STRESS_EDGE_COLUMNS, stress_edge_rows)
        ),
        "surface_text_hash": sha_text(digest_text(SURFACE_COLUMNS, surface_rows)),
        "gap_text_hash": sha_text(digest_text(GAP_COLUMNS, gap_rows)),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    transition_sem = rows["transition_sem"]
    stress20 = rows["stress20"]
    stress = rows["stress"]
    stress_artifact = rows["stress_artifact"]
    checks = {
        "transition_input_certified": transition_sem.get("status")
        == "LONG_TRANSITION_SEM_OBSTRUCTION_CERTIFIED"
        and transition_sem.get("all_checks_pass") is True,
        "stress20_input_certified": stress20.get("status") == "LONG_STRESS20_CERTIFIED"
        and stress20.get("all_checks_pass") is True,
        "stress_graph_input_certified": stress.get("status")
        == "C985_D20_BOUNDARY_NEIGHBORHOOD_STRESS_GRAPH_CERTIFIED"
        and stress.get("all_checks_pass") is True
        and stress_artifact.get("status")
        == "C985_D20_BOUNDARY_NEIGHBORHOOD_STRESS_GRAPH_CERTIFIED",
        "transition_surface_exact": obs["transition_row_count"] == 642
        and obs["transition_delta_sum"] == 642
        and obs["semantic_transition_realized_count"] == 0,
        "finite_stress_surface_exact": obs["stress_node_count"] == 20
        and obs["stress_directed_edge_count"] == 100
        and obs["stress_undirected_edge_count"] == 64
        and obs["stress_row_degree_min"] == 5
        and obs["stress_row_degree_max"] == 5
        and obs["stress_complement_pair_count"] == 10
        and obs["stress_complement_directed_edge_count"] == 18,
        "stress_not_20gon_exact": obs["stress_equals_20gon_flag"] == 0
        and obs["stress_cycle_directed_overlap_count"] == 14
        and obs["stress_cycle_undirected_overlap_count"] == 10,
        "stress_gate_scope_exact": obs["finite_stress_readout_flag"] == 1
        and obs["transition_stress_edge_map_count"] == 0
        and obs["transition_stress_coupling_flag"] == 0
        and obs["physical_stress_energy_flag"] == 0
        and obs["smooth_lorentzian_metric_flag"] == 0
        and obs["curvature_einstein_tensor_flag"] == 0
        and obs["gr_derivation_flag"] == 0,
        "table_shapes_match": rows["stress_edge_table"].shape
        == (100, len(STRESS_EDGE_COLUMNS))
        and rows["surface_table"].shape == (len(SURFACE_CODES), len(SURFACE_COLUMNS))
        and rows["gap_table"].shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and rows["observable_table"].shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "finite_stress_readout_gate",
        "summary": {
            "transition_row_count": obs["transition_row_count"],
            "transition_delta_sum": obs["transition_delta_sum"],
            "semantic_transition_realized_count": obs[
                "semantic_transition_realized_count"
            ],
            "stress_node_count": obs["stress_node_count"],
            "stress_directed_edge_count": obs["stress_directed_edge_count"],
            "stress_undirected_edge_count": obs["stress_undirected_edge_count"],
            "stress_complement_pair_count": obs["stress_complement_pair_count"],
            "stress_equals_20gon_flag": obs["stress_equals_20gon_flag"],
            "finite_stress_readout_flag": obs["finite_stress_readout_flag"],
            "transition_stress_coupling_flag": obs[
                "transition_stress_coupling_flag"
            ],
            "physical_stress_energy_flag": obs["physical_stress_energy_flag"],
            "gr_derivation_flag": obs["gr_derivation_flag"],
            "next_gap": "stress_transition_coupling_map",
        },
        "surface_code_map": {str(value): key for key, value in SURFACE_CODES.items()},
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "stress_edge_table_sha256": sha_array(rows["stress_edge_table"]),
        "stress_edge_text_sha256": rows["stress_edge_text_hash"],
        "surface_table_sha256": sha_array(rows["surface_table"]),
        "surface_text_sha256": rows["surface_text_hash"],
        "gap_table_sha256": sha_array(rows["gap_table"]),
        "gap_text_sha256": rows["gap_text_hash"],
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    stress_gate = {
        "schema": "long.stress_gate@1",
        "object": "finite_stress_readout_gate",
        "status": STATUS if all(checks.values()) else "LONG_STRESS_GATE_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.stress_gate.report@1",
        "status": stress_gate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_stress_gate combines the guarded unit-time transition surface "
            "with the certified stress-neighborhood graph as a finite readout "
            "gate. It certifies a 20-node finite stress surface with 100 directed "
            "stress-neighborhood edges alongside 642 time-backed guarded "
            "transitions, but no transition-to-stress coupling map, physical "
            "stress-energy tensor, smooth metric, curvature tensor, or Einstein "
            "equation is certified."
        ),
        "stage_protocol": {
            "draft": "read long_transition_sem, long_stress20, and the certified stress-neighborhood graph",
            "witness": "emit directed stress-edge rows, surface decision rows, gap rows, and observables",
            "coherence": "check input statuses, transition counts, stress counts, 20-gon comparison, and table hashes",
            "closure": "certify finite stress readout while preserving the stress-energy and metric gaps",
            "emit": "write long_stress_gate artifacts and verifier hook",
        },
        "inputs": {
            "long_transition_sem": input_entry(
                LONG_TRANSITION_SEM,
                {
                    "status": transition_sem.get("status"),
                    "certificate_sha256": transition_sem.get("certificate_sha256"),
                },
            ),
            "long_transition_csv": input_entry(
                LONG_TRANSITION_CSV,
                {"row_count": len(rows["transition_rows"])},
            ),
            "long_stress20": input_entry(
                LONG_STRESS20,
                {
                    "status": stress20.get("status"),
                    "certificate_sha256": stress20.get("certificate_sha256"),
                },
            ),
            "stress": input_entry(
                STRESS,
                {
                    "status": stress.get("status"),
                    "certificate_sha256": stress.get("certificate_sha256"),
                },
            ),
            "stress_artifact": input_entry(
                STRESS_ARTIFACT,
                {"status": stress_artifact.get("status")},
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "stress_gate": relpath(OUT_DIR / "stress_gate.json"),
            "stress_edge_csv": relpath(OUT_DIR / "stress_edge.csv"),
            "surface_csv": relpath(OUT_DIR / "surface.csv"),
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
                "the certified stress graph can be used as a finite stress readout surface",
                "the finite stress readout has 20 nodes, 100 directed stress edges, and 64 undirected stress edges",
                "the finite stress readout coexists with 642 guarded unit-time transitions",
                "the stress graph is not treated as a literal 20-gon or physical spacetime circle",
                "no transition-to-stress coupling law is materialized in the current artifact boundary",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "a map assigning each guarded transition to a stress edge or stress tensor component",
                "a physical stress-energy tensor",
                "a nondegenerate smooth Lorentzian metric tensor",
                "Riemann/Ricci curvature, Einstein tensor, or Einstein field equations",
                "a completed derivation of general relativity",
            ],
        },
        "next_highest_yield_item": (
            "Materialize the stress-transition coupling seam: decide whether the "
            "642 guarded transitions can be functorially mapped to the 100 "
            "directed stress-neighborhood edges or certify that obstruction."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.stress_gate.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.stress_gate.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "stress_gate": stress_gate,
        "stress_edge_csv": csv_text(STRESS_EDGE_COLUMNS, rows["stress_edge_rows"]),
        "surface_csv": csv_text(SURFACE_COLUMNS, rows["surface_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "stress_edge_table": rows["stress_edge_table"],
        "surface_table": rows["surface_table"],
        "gap_table": rows["gap_table"],
        "observable_table": rows["observable_table"],
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
    write_json(OUT_DIR / "stress_gate.json", payloads["stress_gate"])
    (OUT_DIR / "stress_edge.csv").write_text(
        payloads["stress_edge_csv"], encoding="utf-8"
    )
    (OUT_DIR / "surface.csv").write_text(payloads["surface_csv"], encoding="utf-8")
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        stress_edge_table=payloads["stress_edge_table"],
        surface_table=payloads["surface_table"],
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
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
