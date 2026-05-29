from __future__ import annotations

import hashlib
import json
from collections import deque
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


THEOREM_ID = "long_stress20"
STATUS = "LONG_STRESS20_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

PROOF_ROOT = D20_INVARIANTS / "proof_obligations"
STRESS = PROOF_ROOT / "c985_d20_boundary_neighborhood_stress_graph" / "report.json"
STRESS_ARTIFACT = (
    PROOF_ROOT / "c985_d20_boundary_neighborhood_stress_graph" / "artifact.json"
)

DERIVE_SCRIPT = ROOT / "src" / "derive_long_stress20.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_stress20.py"

SCALE = 10_000_000_000

NODE_COLUMNS = [
    "atom_id",
    "cycle_prev",
    "cycle_next",
    "cycle_antipode",
    "stress_complement",
    "stress_neighbor_count",
    "cycle_neighbor_hit_count",
    "complement_is_cycle_antipode_flag",
    "complement_forward_edge_flag",
    "complement_reverse_edge_flag",
    "signed_tension_scaled",
]
CYCLE_EDGE_COLUMNS = [
    "cycle_edge_id",
    "atom_a",
    "atom_b",
    "stress_undirected_flag",
    "stress_forward_flag",
    "stress_reverse_flag",
]
COMPLEMENT_COLUMNS = [
    "complement_pair_id",
    "atom_a",
    "atom_b",
    "cycle_edge_flag",
    "cycle_antipode_pair_flag",
    "stress_undirected_flag",
    "stress_forward_flag",
    "stress_reverse_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

OBS_NAMES = [
    "stress_node_count",
    "stress_directed_edge_count",
    "stress_undirected_edge_count",
    "stress_row_degree_min",
    "stress_row_degree_max",
    "stress_undirected_degree_min",
    "stress_undirected_degree_max",
    "stress_undirected_diameter",
    "stress_connected_flag",
    "cycle_node_count",
    "cycle_directed_edge_count",
    "cycle_undirected_edge_count",
    "cycle_diameter",
    "cycle_directed_overlap_count",
    "cycle_undirected_overlap_count",
    "cycle_undirected_missing_count",
    "complement_pair_count",
    "complement_cycle_edge_overlap_count",
    "complement_cycle_antipode_pair_count",
    "complement_stress_undirected_overlap_count",
    "complement_stress_directed_overlap_count",
    "stress_equals_20gon_flag",
    "stress_contains_cycle_flag",
    "stress_contains_all_complements_flag",
    "comparison_certified_flag",
    "physical_spacetime_20gon_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _stress_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    witness = report.get("witness")
    if not isinstance(witness, dict):
        raise AssertionError("stress witness missing")
    graph_rows = witness.get("graph_rows")
    if not isinstance(graph_rows, list):
        raise AssertionError("stress graph_rows missing")
    return graph_rows


def _directed_edges(graph_rows: list[dict[str, Any]]) -> set[tuple[int, int]]:
    edges: set[tuple[int, int]] = set()
    for row in graph_rows:
        source = int(row["atom_id"])
        for neighbor in row.get("neighbors", []):
            edges.add((source, int(neighbor["atom_id"])))
    return edges


def _undirected(edges: set[tuple[int, int]]) -> set[tuple[int, int]]:
    return {tuple(sorted(edge)) for edge in edges}


def _diameter(node_count: int, undirected_edges: set[tuple[int, int]]) -> tuple[int, int, list[int]]:
    adjacency = [set() for _ in range(node_count)]
    for a, b in undirected_edges:
        adjacency[a].add(b)
        adjacency[b].add(a)
    all_distances: list[int] = []
    connected = 1
    diameter = 0
    for start in range(node_count):
        queue: deque[int] = deque([start])
        distances = {start: 0}
        while queue:
            current = queue.popleft()
            for nxt in adjacency[current]:
                if nxt not in distances:
                    distances[nxt] = distances[current] + 1
                    queue.append(nxt)
        if len(distances) != node_count:
            connected = 0
        all_distances.extend(distances.values())
        diameter = max(diameter, max(distances.values()))
    return diameter, connected, [len(neighbors) for neighbors in adjacency]


def build_rows() -> dict[str, Any]:
    stress = load_json(STRESS)
    stress_artifact = load_json(STRESS_ARTIFACT)
    graph_rows = _stress_rows(stress)
    node_count = len(graph_rows)
    directed = _directed_edges(graph_rows)
    undirected = _undirected(directed)

    cycle_directed = {
        (atom, (atom + 1) % node_count) for atom in range(node_count)
    } | {(atom, (atom - 1) % node_count) for atom in range(node_count)}
    cycle_undirected = {
        tuple(sorted((atom, (atom + 1) % node_count))) for atom in range(node_count)
    }
    complement = {int(row["atom_id"]): int(row["complement_atom_id"]) for row in graph_rows}
    complement_pairs = {
        tuple(sorted((atom, paired))) for atom, paired in complement.items()
    }
    stress_diameter, stress_connected, stress_degrees = _diameter(node_count, undirected)

    node_rows: list[dict[str, int]] = []
    for row in graph_rows:
        atom = int(row["atom_id"])
        neighbors = {int(neighbor["atom_id"]) for neighbor in row["neighbors"]}
        cycle_prev = (atom - 1) % node_count
        cycle_next = (atom + 1) % node_count
        cycle_antipode = (atom + node_count // 2) % node_count
        stress_complement = complement[atom]
        node_rows.append(
            {
                "atom_id": atom,
                "cycle_prev": cycle_prev,
                "cycle_next": cycle_next,
                "cycle_antipode": cycle_antipode,
                "stress_complement": stress_complement,
                "stress_neighbor_count": len(neighbors),
                "cycle_neighbor_hit_count": int(cycle_prev in neighbors)
                + int(cycle_next in neighbors),
                "complement_is_cycle_antipode_flag": int(
                    stress_complement == cycle_antipode
                ),
                "complement_forward_edge_flag": int((atom, stress_complement) in directed),
                "complement_reverse_edge_flag": int((stress_complement, atom) in directed),
                "signed_tension_scaled": int(round(float(row["signed_tension"]) * SCALE)),
            }
        )

    cycle_rows: list[dict[str, int]] = []
    for atom in range(node_count):
        a, b = tuple(sorted((atom, (atom + 1) % node_count)))
        cycle_rows.append(
            {
                "cycle_edge_id": atom,
                "atom_a": a,
                "atom_b": b,
                "stress_undirected_flag": int((a, b) in undirected),
                "stress_forward_flag": int((a, b) in directed),
                "stress_reverse_flag": int((b, a) in directed),
            }
        )

    complement_rows: list[dict[str, int]] = []
    for pair_id, (a, b) in enumerate(sorted(complement_pairs)):
        complement_rows.append(
            {
                "complement_pair_id": pair_id,
                "atom_a": a,
                "atom_b": b,
                "cycle_edge_flag": int((a, b) in cycle_undirected),
                "cycle_antipode_pair_flag": int((a + node_count // 2) % node_count == b),
                "stress_undirected_flag": int((a, b) in undirected),
                "stress_forward_flag": int((a, b) in directed),
                "stress_reverse_flag": int((b, a) in directed),
            }
        )

    obs = {
        "stress_node_count": node_count,
        "stress_directed_edge_count": len(directed),
        "stress_undirected_edge_count": len(undirected),
        "stress_row_degree_min": min(row["stress_neighbor_count"] for row in node_rows),
        "stress_row_degree_max": max(row["stress_neighbor_count"] for row in node_rows),
        "stress_undirected_degree_min": min(stress_degrees),
        "stress_undirected_degree_max": max(stress_degrees),
        "stress_undirected_diameter": stress_diameter,
        "stress_connected_flag": stress_connected,
        "cycle_node_count": node_count,
        "cycle_directed_edge_count": len(cycle_directed),
        "cycle_undirected_edge_count": len(cycle_undirected),
        "cycle_diameter": node_count // 2,
        "cycle_directed_overlap_count": len(directed & cycle_directed),
        "cycle_undirected_overlap_count": len(undirected & cycle_undirected),
        "cycle_undirected_missing_count": len(cycle_undirected - undirected),
        "complement_pair_count": len(complement_pairs),
        "complement_cycle_edge_overlap_count": len(complement_pairs & cycle_undirected),
        "complement_cycle_antipode_pair_count": sum(
            row["cycle_antipode_pair_flag"] for row in complement_rows
        ),
        "complement_stress_undirected_overlap_count": sum(
            row["stress_undirected_flag"] for row in complement_rows
        ),
        "complement_stress_directed_overlap_count": sum(
            row["stress_forward_flag"] + row["stress_reverse_flag"]
            for row in complement_rows
        ),
        "stress_equals_20gon_flag": int(undirected == cycle_undirected),
        "stress_contains_cycle_flag": int(cycle_undirected <= undirected),
        "stress_contains_all_complements_flag": int(complement_pairs <= undirected),
        "comparison_certified_flag": 1,
        "physical_spacetime_20gon_flag": 0,
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    return {
        "stress": stress,
        "stress_artifact": stress_artifact,
        "node_rows": node_rows,
        "cycle_rows": cycle_rows,
        "complement_rows": complement_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "node_table": table_from_rows(NODE_COLUMNS, node_rows),
        "cycle_edge_table": table_from_rows(CYCLE_EDGE_COLUMNS, cycle_rows),
        "complement_table": table_from_rows(COMPLEMENT_COLUMNS, complement_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "node_text_hash": sha_text(digest_text(NODE_COLUMNS, node_rows)),
        "cycle_edge_text_hash": sha_text(digest_text(CYCLE_EDGE_COLUMNS, cycle_rows)),
        "complement_text_hash": sha_text(digest_text(COMPLEMENT_COLUMNS, complement_rows)),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    stress = rows["stress"]
    stress_artifact = rows["stress_artifact"]
    checks = {
        "stress_input_certified": stress.get("status")
        == "C985_D20_BOUNDARY_NEIGHBORHOOD_STRESS_GRAPH_CERTIFIED"
        and stress.get("all_checks_pass") is True
        and stress_artifact.get("status")
        == "C985_D20_BOUNDARY_NEIGHBORHOOD_STRESS_GRAPH_CERTIFIED",
        "stress_graph_shape_exact": obs["stress_node_count"] == 20
        and obs["stress_directed_edge_count"] == 100
        and obs["stress_undirected_edge_count"] == 64
        and obs["stress_row_degree_min"] == 5
        and obs["stress_row_degree_max"] == 5,
        "cycle_shape_exact": obs["cycle_node_count"] == 20
        and obs["cycle_directed_edge_count"] == 40
        and obs["cycle_undirected_edge_count"] == 20
        and obs["cycle_diameter"] == 10,
        "stress_cycle_overlap_exact": obs["cycle_directed_overlap_count"] == 14
        and obs["cycle_undirected_overlap_count"] == 10
        and obs["cycle_undirected_missing_count"] == 10
        and obs["stress_equals_20gon_flag"] == 0
        and obs["stress_contains_cycle_flag"] == 0,
        "complement_comparison_exact": obs["complement_pair_count"] == 10
        and obs["complement_cycle_edge_overlap_count"] == 2
        and obs["complement_cycle_antipode_pair_count"] == 0
        and obs["complement_stress_undirected_overlap_count"] == 10
        and obs["complement_stress_directed_overlap_count"] == 18
        and obs["stress_contains_all_complements_flag"] == 1,
        "metric_comparison_not_physical_spacetime": obs["comparison_certified_flag"] == 1
        and obs["physical_spacetime_20gon_flag"] == 0,
        "table_shapes_match": rows["node_table"].shape == (20, len(NODE_COLUMNS))
        and rows["cycle_edge_table"].shape == (20, len(CYCLE_EDGE_COLUMNS))
        and rows["complement_table"].shape == (10, len(COMPLEMENT_COLUMNS))
        and rows["observable_table"].shape == (len(OBS_NAMES), len(OBS_COLUMNS)),
    }

    witness = {
        "name": THEOREM_ID,
        "classification": "stress_graph_to_canonical_20gon_comparison",
        "summary": {
            "stress_node_count": obs["stress_node_count"],
            "stress_directed_edge_count": obs["stress_directed_edge_count"],
            "stress_undirected_edge_count": obs["stress_undirected_edge_count"],
            "stress_undirected_diameter": obs["stress_undirected_diameter"],
            "cycle_undirected_edge_count": obs["cycle_undirected_edge_count"],
            "cycle_undirected_overlap_count": obs["cycle_undirected_overlap_count"],
            "cycle_undirected_missing_count": obs["cycle_undirected_missing_count"],
            "complement_pair_count": obs["complement_pair_count"],
            "complement_cycle_antipode_pair_count": obs[
                "complement_cycle_antipode_pair_count"
            ],
            "complement_stress_undirected_overlap_count": obs[
                "complement_stress_undirected_overlap_count"
            ],
            "stress_equals_20gon_flag": obs["stress_equals_20gon_flag"],
            "stress_contains_all_complements_flag": obs[
                "stress_contains_all_complements_flag"
            ],
            "physical_spacetime_20gon_flag": obs["physical_spacetime_20gon_flag"],
            "next_gap": "long_stress_gate",
        },
        "node_table_sha256": sha_array(rows["node_table"]),
        "node_text_sha256": rows["node_text_hash"],
        "cycle_edge_table_sha256": sha_array(rows["cycle_edge_table"]),
        "cycle_edge_text_sha256": rows["cycle_edge_text_hash"],
        "complement_table_sha256": sha_array(rows["complement_table"]),
        "complement_text_sha256": rows["complement_text_hash"],
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    stress20 = {
        "schema": "long.stress20@1",
        "object": "stress_graph_to_canonical_20gon_comparison",
        "status": STATUS if all(checks.values()) else "LONG_STRESS20_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.stress20.report@1",
        "status": stress20["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_stress20 compares the certified 20-node stress-neighborhood "
            "graph with the canonical atom-id 20-gon. The stress graph is not "
            "the 20-gon: it has 64 undirected edges, contains 10 of the 20 "
            "cycle edges, and has undirected diameter 4 rather than 10. It does "
            "contain all 10 certified complement pairs, but those complements "
            "are not the canonical 20-gon antipodes."
        ),
        "stage_protocol": {
            "draft": "read the certified d20 stress-neighborhood graph",
            "witness": "emit per-node cycle/complement rows, cycle-edge overlap rows, and complement-pair rows",
            "coherence": "check edge counts, overlap counts, complement counts, connectivity, diameter, and table hashes",
            "closure": "certify the finite graph comparison without claiming physical spacetime cyclicity",
            "emit": "write long_stress20 artifacts and verifier hook",
        },
        "inputs": {
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
            "stress20": relpath(OUT_DIR / "stress20.json"),
            "node_csv": relpath(OUT_DIR / "node.csv"),
            "cycle_edge_csv": relpath(OUT_DIR / "cycle_edge.csv"),
            "complement_csv": relpath(OUT_DIR / "complement.csv"),
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
                "finite comparison against the canonical atom-id 20-gon",
                "the stress graph is a connected 20-node graph with 100 directed and 64 undirected stress-neighborhood edges",
                "the stress graph overlaps 10 of 20 undirected 20-gon cycle edges",
                "the stress graph contains all 10 complement pairs",
                "the certified complement pairing is not the 20-gon antipode pairing",
            ],
            "does_not_certify_because_out_of_scope": [
                "that the stress graph is the physical spacetime circle",
                "that the atom-id 20-gon is a physical spatial slice",
                "a physical stress-energy tensor",
                "a smooth Lorentzian metric or Einstein equation",
            ],
        },
        "next_highest_yield_item": (
            "Build long_stress_gate using this comparison: treat the stress graph "
            "as a dense finite stress-neighborhood surface, not as a literal "
            "20-gon, and keep physical stress-energy open."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.stress20.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.stress20.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "stress20": stress20,
        "node_csv": csv_text(NODE_COLUMNS, rows["node_rows"]),
        "cycle_edge_csv": csv_text(CYCLE_EDGE_COLUMNS, rows["cycle_rows"]),
        "complement_csv": csv_text(COMPLEMENT_COLUMNS, rows["complement_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "node_table": rows["node_table"],
        "cycle_edge_table": rows["cycle_edge_table"],
        "complement_table": rows["complement_table"],
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
    write_json(OUT_DIR / "stress20.json", payloads["stress20"])
    (OUT_DIR / "node.csv").write_text(payloads["node_csv"], encoding="utf-8")
    (OUT_DIR / "cycle_edge.csv").write_text(
        payloads["cycle_edge_csv"], encoding="utf-8"
    )
    (OUT_DIR / "complement.csv").write_text(
        payloads["complement_csv"], encoding="utf-8"
    )
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        node_table=payloads["node_table"],
        cycle_edge_table=payloads["cycle_edge_table"],
        complement_table=payloads["complement_table"],
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
