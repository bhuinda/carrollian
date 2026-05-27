from __future__ import annotations

import heapq
import itertools
import json
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        OBJECT_LABELS,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        OBJECT_LABELS,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "c985_d20_hyperbolic_boundary_graph"
STATUS = "C985_D20_HYPERBOLIC_BOUNDARY_GRAPH_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

ATLAS_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_boundary_invariant_atlas"
GEOMETRY_DIR = D20_INVARIANTS / "proof_obligations" / "c985_tensor_geometry_invariants"

ATLAS_REPORT = ATLAS_DIR / "report.json"
ATLAS_JSON = ATLAS_DIR / "d20_boundary_invariant_atlas.json"
ATLAS_NPZ = ATLAS_DIR / "d20_boundary_invariant_atlas.npz"
RELATION_GEOMETRY_SIGNATURES = GEOMETRY_DIR / "relation_geometry_signatures.npz"

DERIVE_SCRIPT = ROOT / "src" / "derive_c985_d20_hyperbolic_boundary_graph.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_d20_hyperbolic_boundary_graph.py"

PAIR_COLUMNS = [
    "atom_i",
    "atom_j",
    "intersection_size",
    "is_johnson_edge",
    "is_complement_pair",
    "signature_intersection",
    "signature_union",
    "signature_jaccard_distance_numerator",
    "tensor_mass_delta",
    "tensor_mass_sum",
    "tensor_support_delta",
    "complement_mass_contrast",
    "johnson_edge_length",
    "signature_edge_length",
    "affinity_edge_length",
]


def csv_text(headers: list[str], rows: list[dict[str, Any]]) -> str:
    out = [",".join(headers)]
    for row in rows:
        out.append(",".join(str(row[column]) for column in headers))
    return "\n".join(out) + "\n"


def signature_class_ids(records: np.ndarray) -> np.ndarray:
    signature = records[:, [1, 2, 4, 5, 6, 7, 8, 9, 10, 11]].astype(np.int64)
    _, inverse = np.unique(signature, axis=0, return_inverse=True)
    return inverse.astype(np.int64)


def atom_signature_sets(atlas: dict[str, Any], relation_records: np.ndarray, class_ids: np.ndarray) -> list[set[int]]:
    sets: list[set[int]] = []
    for row in atlas["atom_rows"]:
        triple = {OBJECT_LABELS.index(label) for label in row["h6_triple"]}
        members = np.zeros(len(OBJECT_LABELS), dtype=bool)
        members[np.asarray(sorted(triple), dtype=np.int64)] = True
        mask = members[relation_records[:, 1]] & members[relation_records[:, 2]]
        sets.append(set(int(x) for x in np.unique(class_ids[mask])))
    return sets


def build_pair_records(atlas: dict[str, Any], signature_sets: list[set[int]]) -> tuple[np.ndarray, list[dict[str, Any]]]:
    atoms = atlas["atom_rows"]
    preliminary: list[dict[str, Any]] = []
    max_johnson_overlap = 0
    for i, j in itertools.combinations(range(len(atoms)), 2):
        left = atoms[i]
        right = atoms[j]
        left_triple = {OBJECT_LABELS.index(label) for label in left["h6_triple"]}
        right_triple = {OBJECT_LABELS.index(label) for label in right["h6_triple"]}
        intersection_size = len(left_triple & right_triple)
        signature_intersection = len(signature_sets[i] & signature_sets[j])
        signature_union = len(signature_sets[i] | signature_sets[j])
        if intersection_size == 2:
            max_johnson_overlap = max(max_johnson_overlap, signature_intersection)
        preliminary.append(
            {
                "atom_i": i,
                "atom_j": j,
                "intersection_size": intersection_size,
                "is_johnson_edge": int(intersection_size == 2),
                "is_complement_pair": int(intersection_size == 0),
                "signature_intersection": signature_intersection,
                "signature_union": signature_union,
                "signature_jaccard_distance_numerator": signature_union - signature_intersection,
                "tensor_mass_delta": abs(
                    int(left["tensor_path_coefficient_mass"])
                    - int(right["tensor_path_coefficient_mass"])
                ),
                "tensor_mass_sum": int(left["tensor_path_coefficient_mass"])
                + int(right["tensor_path_coefficient_mass"]),
                "tensor_support_delta": abs(
                    int(left["tensor_path_support"]) - int(right["tensor_path_support"])
                ),
            }
        )

    rows: list[dict[str, Any]] = []
    for row in preliminary:
        is_johnson = bool(row["is_johnson_edge"])
        is_complement = bool(row["is_complement_pair"])
        edge_length = int(row["signature_jaccard_distance_numerator"]) if is_johnson else 0
        rows.append(
            {
                **row,
                "complement_mass_contrast": int(row["tensor_mass_delta"]) if is_complement else 0,
                "johnson_edge_length": 1 if is_johnson else 0,
                "signature_edge_length": max(1, edge_length) if is_johnson else 0,
                "affinity_edge_length": 1
                + max_johnson_overlap
                - int(row["signature_intersection"])
                if is_johnson
                else 0,
            }
        )

    pair_array = np.asarray([[int(row[column]) for column in PAIR_COLUMNS] for row in rows], dtype=np.int64)
    return pair_array, rows


def shortest_paths(node_count: int, edges: list[tuple[int, int, int]]) -> np.ndarray:
    infinity = 10**15
    adjacency: list[list[tuple[int, int]]] = [[] for _ in range(node_count)]
    for source, target, length in edges:
        adjacency[source].append((target, length))
        adjacency[target].append((source, length))
    distances = np.full((node_count, node_count), infinity, dtype=np.int64)
    for source in range(node_count):
        distances[source, source] = 0
        queue = [(0, source)]
        while queue:
            distance, node = heapq.heappop(queue)
            if distance != int(distances[source, node]):
                continue
            for neighbor, length in adjacency[node]:
                candidate = distance + length
                if candidate < int(distances[source, neighbor]):
                    distances[source, neighbor] = candidate
                    heapq.heappush(queue, (candidate, neighbor))
    return distances


def metric_edges(pair_rows: list[dict[str, Any]], length_column: str) -> list[tuple[int, int, int]]:
    return [
        (int(row["atom_i"]), int(row["atom_j"]), int(row[length_column]))
        for row in pair_rows
        if int(row["is_johnson_edge"]) == 1
    ]


def gromov_hyperbolicity(distances: np.ndarray) -> dict[str, Any]:
    node_count = int(distances.shape[0])
    histogram: dict[int, int] = {}
    best_gap = -1
    best_quad: tuple[int, int, int, int] | None = None
    best_sums: list[int] = []
    for quad in itertools.combinations(range(node_count), 4):
        a, b, c, d = quad
        sums = [
            int(distances[a, b] + distances[c, d]),
            int(distances[a, c] + distances[b, d]),
            int(distances[a, d] + distances[b, c]),
        ]
        sorted_sums = sorted(sums)
        gap = sorted_sums[2] - sorted_sums[1]
        histogram[gap] = histogram.get(gap, 0) + 1
        if gap > best_gap:
            best_gap = gap
            best_quad = quad
            best_sums = sums
    if best_quad is None:
        raise ValueError("empty graph metric cannot have a four-point witness")
    return {
        "delta_numerator_over_2": best_gap,
        "delta_fraction": [best_gap, 2],
        "witness_atom_ids": list(best_quad),
        "witness_pair_sums": best_sums,
        "gap_histogram": [
            {"gap_numerator_over_2": int(gap), "quadruple_count": int(count)}
            for gap, count in sorted(histogram.items())
        ],
    }


def metric_summary(name: str, distances: np.ndarray) -> dict[str, Any]:
    finite = distances[distances < 10**15]
    if finite.size != distances.size:
        raise ValueError(f"{name} graph is disconnected")
    return {
        "name": name,
        "diameter": int(finite.max()),
        "positive_distance_min": int(finite[finite > 0].min()),
        "positive_distance_max": int(finite[finite > 0].max()),
        "gromov_hyperbolicity": gromov_hyperbolicity(distances),
    }


def row_atom_label(atlas: dict[str, Any], atom_id: int) -> str:
    row = atlas["atom_rows"][atom_id]
    return "{" + ",".join(row["h6_triple"]) + "}"


def enrich_witness(summary: dict[str, Any], atlas: dict[str, Any]) -> dict[str, Any]:
    hyperbolicity = summary["gromov_hyperbolicity"]
    ids = [int(x) for x in hyperbolicity["witness_atom_ids"]]
    return {
        **summary,
        "gromov_hyperbolicity": {
            **hyperbolicity,
            "witness_atom_labels": [row_atom_label(atlas, atom_id) for atom_id in ids],
        },
    }


def build_payloads() -> dict[str, Any]:
    atlas_report = load_json(ATLAS_REPORT)
    atlas = load_json(ATLAS_JSON)
    relation_npz = np.load(RELATION_GEOMETRY_SIGNATURES, allow_pickle=False)
    relation_records = np.asarray(relation_npz["relation_records"], dtype=np.int64)
    class_ids = signature_class_ids(relation_records)
    signature_sets = atom_signature_sets(atlas, relation_records, class_ids)
    pair_array, pair_rows = build_pair_records(atlas, signature_sets)

    johnson_edges = metric_edges(pair_rows, "johnson_edge_length")
    signature_edges = metric_edges(pair_rows, "signature_edge_length")
    affinity_edges = metric_edges(pair_rows, "affinity_edge_length")
    johnson_distances = shortest_paths(20, johnson_edges)
    signature_distances = shortest_paths(20, signature_edges)
    affinity_distances = shortest_paths(20, affinity_edges)

    johnson_summary = enrich_witness(metric_summary("unweighted_johnson_boundary", johnson_distances), atlas)
    signature_summary = enrich_witness(metric_summary("signature_distance_boundary", signature_distances), atlas)
    affinity_summary = enrich_witness(metric_summary("signature_affinity_boundary", affinity_distances), atlas)

    layer_counts = {
        str(layer): int(np.count_nonzero(pair_array[:, 2] == layer))
        for layer in range(3)
    }
    top_signature_edges = sorted(
        (row for row in pair_rows if int(row["is_johnson_edge"]) == 1),
        key=lambda row: (
            -int(row["signature_intersection"]),
            int(row["signature_union"]),
            -int(row["tensor_mass_sum"]),
            int(row["atom_i"]),
            int(row["atom_j"]),
        ),
    )[:16]
    top_complement_contrasts = sorted(
        (row for row in pair_rows if int(row["is_complement_pair"]) == 1),
        key=lambda row: (-int(row["tensor_mass_delta"]), int(row["atom_i"])),
    )

    graph = {
        "schema": "c985.d20_hyperbolic_boundary_graph@1",
        "object": "d20",
        "graph_rule": {
            "vertices": "20 atoms of C(H6,3)",
            "johnson_edges": "two atoms are adjacent when their H6 triples share exactly two sectors",
            "signature_edge_length": "on Johnson edges, length is |S_i union S_j| - |S_i intersect S_j| for atom signature-class sets",
            "affinity_edge_length": "on Johnson edges, length is 1 + max_signature_overlap - signature_overlap",
            "complement_pairs": "disjoint H6 triples are recorded as antipodal contrast pairs, not Johnson edges",
        },
        "pair_columns": PAIR_COLUMNS,
        "vertices": [
            {
                "atom_id": int(row["atom_id"]),
                "h6_triple": row["h6_triple"],
                "complement_atom_id": int(row["complement_atom_id"]),
                "tensor_path_support": int(row["tensor_path_support"]),
                "tensor_path_coefficient_mass": int(row["tensor_path_coefficient_mass"]),
                "internal_signature_class_count": int(row["internal_signature_class_count"]),
            }
            for row in atlas["atom_rows"]
        ],
        "pair_layer_counts": layer_counts,
        "johnson_edge_count": int(sum(int(row["is_johnson_edge"]) for row in pair_rows)),
        "complement_pair_count": int(sum(int(row["is_complement_pair"]) for row in pair_rows)),
        "top_signature_overlap_johnson_edges": [
            {
                **{column: int(row[column]) for column in PAIR_COLUMNS},
                "atom_i_label": row_atom_label(atlas, int(row["atom_i"])),
                "atom_j_label": row_atom_label(atlas, int(row["atom_j"])),
            }
            for row in top_signature_edges
        ],
        "top_complement_mass_contrasts": [
            {
                **{column: int(row[column]) for column in PAIR_COLUMNS},
                "atom_i_label": row_atom_label(atlas, int(row["atom_i"])),
                "atom_j_label": row_atom_label(atlas, int(row["atom_j"])),
            }
            for row in top_complement_contrasts
        ],
        "metric_summaries": [johnson_summary, signature_summary, affinity_summary],
    }

    checks = {
        "atlas_report_certified": atlas_report.get("status") == "C985_D20_BOUNDARY_INVARIANT_ATLAS_CERTIFIED",
        "atom_count_is_20": len(atlas["atom_rows"]) == 20,
        "pair_count_is_190": int(pair_array.shape[0]) == 190,
        "pair_layer_counts_match_c_h6_3": layer_counts == {"0": 10, "1": 90, "2": 90},
        "johnson_edge_count_is_90": graph["johnson_edge_count"] == 90,
        "complement_pair_count_is_10": graph["complement_pair_count"] == 10,
        "signature_class_union_is_233": len(set.union(*signature_sets)) == 233,
        "johnson_graph_is_connected": bool(np.all(johnson_distances < 10**15)),
        "signature_metric_graph_is_connected": bool(np.all(signature_distances < 10**15)),
        "affinity_metric_graph_is_connected": bool(np.all(affinity_distances < 10**15)),
        "johnson_diameter_is_3": johnson_summary["diameter"] == 3,
        "johnson_delta_numerator_is_2": johnson_summary["gromov_hyperbolicity"][
            "delta_numerator_over_2"
        ]
        == 2,
        "signature_delta_numerator_is_146": signature_summary["gromov_hyperbolicity"][
            "delta_numerator_over_2"
        ]
        == 146,
        "affinity_delta_numerator_is_41": affinity_summary["gromov_hyperbolicity"][
            "delta_numerator_over_2"
        ]
        == 41,
        "max_complement_mass_contrast_is_155776": int(pair_array[:, 11].max()) == 155776,
        "pair_records_shape_is_190_by_15": tuple(pair_array.shape) == (190, 15),
    }

    witness = {
        "atom_count": 20,
        "pair_count": int(pair_array.shape[0]),
        "johnson_edge_count": graph["johnson_edge_count"],
        "complement_pair_count": graph["complement_pair_count"],
        "signature_class_count": len(set.union(*signature_sets)),
        "johnson_diameter": johnson_summary["diameter"],
        "johnson_delta_fraction": johnson_summary["gromov_hyperbolicity"]["delta_fraction"],
        "signature_distance_diameter": signature_summary["diameter"],
        "signature_delta_fraction": signature_summary["gromov_hyperbolicity"]["delta_fraction"],
        "affinity_distance_diameter": affinity_summary["diameter"],
        "affinity_delta_fraction": affinity_summary["gromov_hyperbolicity"]["delta_fraction"],
        "max_signature_overlap_on_johnson_edge": int(
            max(int(row["signature_intersection"]) for row in pair_rows if int(row["is_johnson_edge"]) == 1)
        ),
        "max_complement_mass_contrast": int(pair_array[:, 11].max()),
        "pair_records_sha256": sha_array(pair_array),
        "johnson_distance_sha256": sha_array(johnson_distances),
        "signature_distance_sha256": sha_array(signature_distances),
        "affinity_distance_sha256": sha_array(affinity_distances),
    }

    certificate = {
        "schema": "c985.d20_hyperbolic_boundary_graph_certificate@1",
        "status": STATUS if all(checks.values()) else "C985_D20_HYPERBOLIC_BOUNDARY_GRAPH_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the d20 boundary atlas induces the Johnson graph J(6,3) on 20 atoms",
            "the unweighted boundary graph has exact four-point Gromov delta 1",
            "signature-distance weighting exposes a larger exact delta witness of 73",
            "signature-affinity weighting exposes an exact delta witness of 41/2",
            "antipodal complement-pair mass contrast is maximized by atoms 0 and 19",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_hyperbolic_boundary_graph@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The C985-derived d20 boundary atlas carries a verified hyperbolic graph "
            "readout: the C(H6,3) Johnson graph has exact Gromov delta 1, while "
            "signature-weighted metrics expose stronger four-point curvature witnesses."
        ),
        "stage_protocol": {
            "draft": "use the certified C985-to-d20 boundary atlas as the 20-vertex source",
            "witness": "materialize pair records, Johnson edges, complement contrasts, and shortest-path metrics",
            "coherence": "check C(H6,3) layer counts, connectivity, exact hyperbolicity witnesses, and metric reproducibility",
            "closure": "certify a hyperbolic boundary graph readout without claiming a packet bridge or optional categorical enrichment",
            "emit": "emit graph JSON, edge CSV, metric NPZ, certificate, and next graph-deepening target",
        },
        "inputs": {
            "boundary_atlas_report": input_entry(
                ATLAS_REPORT,
                {
                    "status": atlas_report.get("status"),
                    "certificate_sha256": atlas_report.get("certificate_sha256"),
                },
            ),
            "boundary_atlas": input_entry(ATLAS_JSON),
            "boundary_atlas_npz": input_entry(ATLAS_NPZ),
            "relation_geometry_signatures": input_entry(RELATION_GEOMETRY_SIGNATURES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "boundary_hyperbolic_graph": relpath(OUT_DIR / "boundary_hyperbolic_graph.json"),
            "boundary_hyperbolic_edges_csv": relpath(OUT_DIR / "boundary_hyperbolic_edges.csv"),
            "boundary_hyperbolic_metrics": relpath(OUT_DIR / "boundary_hyperbolic_metrics.npz"),
            "hyperbolic_certificate": relpath(OUT_DIR / "hyperbolic_certificate.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "Johnson-neighborhood graph on the 20 d20 boundary atoms",
                "all 190 atom-pair layer records with signature overlap and tensor mass contrast",
                "exact unweighted and signature-weighted shortest-path matrices",
                "exact four-point Gromov hyperbolicity witnesses for the boundary metrics",
                "antipodal complement-pair contrast landmarks",
            ],
            "does_not_certify_because_not_required": [
                "a canonical hyperbolic embedding in the Poincare disk or hyperboloid model",
                "a packet bridge from d20 atoms to A985/tube coordinates",
                "a packet normalization killing known boundary torsion",
                "pivotal, spherical, unitary, braiding, ribbon, or Drinfeld-center data",
            ],
        },
        "next_highest_yield_item": (
            "Build a canonical 2D hyperbolic embedding from the certified graph metrics, "
            "then compare geodesic neighborhoods against the C985 tensor-mass landmarks."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_hyperbolic_boundary_graph_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load the certified C985-to-d20 boundary atlas",
            "reconstruct atom signature-class sets from relation geometry signatures",
            "materialize all 190 atom-pair records",
            "verify Johnson J(6,3) layer counts and connectivity",
            "compute exact shortest-path metrics and four-point Gromov hyperbolicity witnesses",
            "verify complement-pair contrast landmarks and artifact reproducibility",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "boundary_hyperbolic_graph": graph,
        "boundary_hyperbolic_edges_csv": csv_text(PAIR_COLUMNS, pair_rows),
        "pair_records": pair_array,
        "johnson_distances": johnson_distances,
        "signature_distances": signature_distances,
        "affinity_distances": affinity_distances,
        "hyperbolic_certificate": certificate,
        "report": report,
        "manifest": manifest,
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
    updated = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": sorted(obligations, key=lambda row: row["id"]),
    }
    updated["registry_sha256"] = self_hash(updated, "registry_sha256")
    write_json(INDEX_PATH, updated)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / "boundary_hyperbolic_graph.json", payloads["boundary_hyperbolic_graph"])
    (OUT_DIR / "boundary_hyperbolic_edges.csv").write_text(
        payloads["boundary_hyperbolic_edges_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "boundary_hyperbolic_metrics.npz",
        pair_records=payloads["pair_records"],
        johnson_distances=payloads["johnson_distances"],
        signature_distances=payloads["signature_distances"],
        affinity_distances=payloads["affinity_distances"],
    )
    write_json(OUT_DIR / "hyperbolic_certificate.json", payloads["hyperbolic_certificate"])
    write_json(OUT_DIR / "report.json", payloads["report"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    update_index(payloads["report"])


def main() -> None:
    payloads = build_payloads()
    write_payloads(payloads)
    witness = payloads["report"]["witness"]
    print(
        json.dumps(
            {
                "status": payloads["report"]["status"],
                "all_checks_pass": payloads["report"]["all_checks_pass"],
                "report": relpath(OUT_DIR / "report.json"),
                "manifest": relpath(OUT_DIR / "manifest.json"),
                "certificate_sha256": payloads["report"]["certificate_sha256"],
                "johnson_delta_fraction": witness["johnson_delta_fraction"],
                "signature_delta_fraction": witness["signature_delta_fraction"],
                "affinity_delta_fraction": witness["affinity_delta_fraction"],
                "max_complement_mass_contrast": witness["max_complement_mass_contrast"],
                "next_highest_yield_item": payloads["report"]["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
