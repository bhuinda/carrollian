from __future__ import annotations

import csv
import json
import math
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
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
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "c985_d20_poincare_embedding"
STATUS = "C985_D20_POINCARE_EMBEDDING_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

GRAPH_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_hyperbolic_boundary_graph"
ATLAS_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_boundary_invariant_atlas"

GRAPH_REPORT = GRAPH_DIR / "report.json"
GRAPH_JSON = GRAPH_DIR / "boundary_hyperbolic_graph.json"
GRAPH_METRICS = GRAPH_DIR / "boundary_hyperbolic_metrics.npz"
ATLAS_REPORT = ATLAS_DIR / "report.json"
ATLAS_JSON = ATLAS_DIR / "d20_boundary_invariant_atlas.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_c985_d20_poincare_embedding.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_d20_poincare_embedding.py"

COORDINATE_COLUMNS = [
    "atom_id",
    "x",
    "y",
    "radius",
    "angle_radians",
    "tensor_path_coefficient_mass",
    "internal_signature_class_count",
    "central_rank",
    "mass_rank",
    "signature_rank",
]
JSON_FLOAT_DIGITS = 10
FLOAT_HASH_SCALE = 10**JSON_FLOAT_DIGITS


def q(value: float) -> float:
    return round(float(value), JSON_FLOAT_DIGITS)


def sha_quantized_float_array(array: np.ndarray) -> str:
    stable = np.rint(np.asarray(array, dtype=np.float64) * FLOAT_HASH_SCALE).astype(np.int64)
    return sha_array(stable)


def upper_triangle_values(matrix: np.ndarray) -> np.ndarray:
    return matrix[np.triu_indices(int(matrix.shape[0]), k=1)]


def classical_mds(metric: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    node_count = int(metric.shape[0])
    center = np.eye(node_count) - np.ones((node_count, node_count), dtype=np.float64) / node_count
    gram = -0.5 * center @ (metric.astype(np.float64) ** 2) @ center
    eigenvalues, eigenvectors = np.linalg.eigh(gram)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]
    coords = eigenvectors[:, :2] * np.sqrt(np.maximum(eigenvalues[:2], 0.0))
    return coords.astype(np.float64), eigenvalues.astype(np.float64)


def canonicalize_axes(coords: np.ndarray, masses: np.ndarray) -> np.ndarray:
    oriented = np.array(coords, dtype=np.float64, copy=True)
    lightest_atom = int(np.argmin(masses))
    heaviest_atom = int(np.argmax(masses))
    if oriented[lightest_atom, 0] > 0:
        oriented[:, 0] *= -1.0
    if oriented[heaviest_atom, 1] < 0:
        oriented[:, 1] *= -1.0
    return oriented


def poincare_distances(coords: np.ndarray) -> np.ndarray:
    node_count = int(coords.shape[0])
    distances = np.zeros((node_count, node_count), dtype=np.float64)
    norms = np.sum(coords * coords, axis=1)
    for i in range(node_count):
        for j in range(i + 1, node_count):
            numerator = 2.0 * float(np.sum((coords[i] - coords[j]) ** 2))
            denominator = float((1.0 - norms[i]) * (1.0 - norms[j]))
            argument = 1.0 + numerator / denominator
            value = math.acosh(max(1.0, argument))
            distances[i, j] = value
            distances[j, i] = value
    return distances


def stress_and_correlation(poincare_metric: np.ndarray, target_metric: np.ndarray) -> tuple[float, float]:
    observed = upper_triangle_values(poincare_metric)
    target = upper_triangle_values(target_metric)
    stress = float(np.sqrt(np.mean((observed - target) ** 2)))
    correlation = float(np.corrcoef(observed, target)[0, 1])
    return stress, correlation


def choose_disk_scale(unit_coords: np.ndarray, graph_metric: np.ndarray) -> dict[str, Any]:
    target = graph_metric.astype(np.float64) * (4.0 / float(graph_metric.max()))
    best: dict[str, Any] | None = None
    for radius_step in range(10, 191):
        radius = radius_step / 200.0
        coords = unit_coords * radius
        metric = poincare_distances(coords)
        stress, correlation = stress_and_correlation(metric, target)
        candidate = {
            "radius_step": radius_step,
            "radius": radius,
            "stress": stress,
            "correlation": correlation,
            "coords": coords,
            "metric": metric,
        }
        if best is None:
            best = candidate
            continue
        key = (round(stress, 15), -round(correlation, 15), radius_step)
        best_key = (round(best["stress"], 15), -round(best["correlation"], 15), best["radius_step"])
        if key < best_key:
            best = candidate
    if best is None:
        raise ValueError("empty Poincare scale search")
    best["target_metric"] = target
    return best


def ranks_desc(values: np.ndarray) -> np.ndarray:
    order = sorted(range(int(values.size)), key=lambda idx: (-float(values[idx]), idx))
    ranks = np.empty(int(values.size), dtype=np.int64)
    for rank, idx in enumerate(order, start=1):
        ranks[idx] = rank
    return ranks


def ranks_asc(values: np.ndarray) -> np.ndarray:
    order = sorted(range(int(values.size)), key=lambda idx: (float(values[idx]), idx))
    ranks = np.empty(int(values.size), dtype=np.int64)
    for rank, idx in enumerate(order, start=1):
        ranks[idx] = rank
    return ranks


def atom_label(atom: dict[str, Any]) -> str:
    return "{" + ",".join(atom["h6_triple"]) + "}"


def nearest_neighbors(
    atom_id: int,
    distances: np.ndarray,
    atlas: dict[str, Any],
    *,
    limit: int = 5,
) -> list[dict[str, Any]]:
    order = sorted(
        (idx for idx in range(int(distances.shape[0])) if idx != atom_id),
        key=lambda idx: (float(distances[atom_id, idx]), idx),
    )
    out: list[dict[str, Any]] = []
    for idx in order[:limit]:
        row = atlas["atom_rows"][idx]
        out.append(
            {
                "atom_id": idx,
                "atom_label": atom_label(row),
                "poincare_distance": q(float(distances[atom_id, idx])),
                "tensor_path_coefficient_mass": int(row["tensor_path_coefficient_mass"]),
                "internal_signature_class_count": int(row["internal_signature_class_count"]),
            }
        )
    return out


def coordinate_rows(
    coords: np.ndarray,
    atlas: dict[str, Any],
) -> tuple[list[dict[str, Any]], np.ndarray]:
    masses = np.asarray([row["tensor_path_coefficient_mass"] for row in atlas["atom_rows"]], dtype=np.float64)
    signatures = np.asarray(
        [row["internal_signature_class_count"] for row in atlas["atom_rows"]],
        dtype=np.float64,
    )
    radii = np.linalg.norm(coords, axis=1)
    central_ranks = ranks_asc(radii)
    mass_ranks = ranks_desc(masses)
    signature_ranks = ranks_desc(signatures)
    rows: list[dict[str, Any]] = []
    numeric = np.zeros((coords.shape[0], len(COORDINATE_COLUMNS)), dtype=np.float64)
    for atom_id, atom in enumerate(atlas["atom_rows"]):
        x = float(coords[atom_id, 0])
        y = float(coords[atom_id, 1])
        radius = float(radii[atom_id])
        angle = float(math.atan2(y, x))
        row = {
            "atom_id": atom_id,
            "atom_label": atom_label(atom),
            "x": q(x),
            "y": q(y),
            "radius": q(radius),
            "angle_radians": q(angle),
            "tensor_path_coefficient_mass": int(masses[atom_id]),
            "internal_signature_class_count": int(signatures[atom_id]),
            "central_rank": int(central_ranks[atom_id]),
            "mass_rank": int(mass_ranks[atom_id]),
            "signature_rank": int(signature_ranks[atom_id]),
        }
        rows.append(row)
        numeric[atom_id] = np.asarray(
            [
                atom_id,
                x,
                y,
                radius,
                angle,
                masses[atom_id],
                signatures[atom_id],
                central_ranks[atom_id],
                mass_ranks[atom_id],
                signature_ranks[atom_id],
            ],
            dtype=np.float64,
        )
    return rows, numeric


def coordinate_csv(rows: list[dict[str, Any]]) -> str:
    output = [",".join(COORDINATE_COLUMNS)]
    for row in rows:
        output.append(",".join(str(row[column]) for column in COORDINATE_COLUMNS))
    return "\n".join(output) + "\n"


def svg_payload(rows: list[dict[str, Any]], atlas: dict[str, Any]) -> str:
    size = 720
    center = size / 2
    scale = 320
    max_mass = max(int(row["tensor_path_coefficient_mass"]) for row in atlas["atom_rows"])
    min_mass = min(int(row["tensor_path_coefficient_mass"]) for row in atlas["atom_rows"])
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="720" height="720" viewBox="0 0 720 720">',
        '<rect width="720" height="720" fill="#f7f4ed"/>',
        '<circle cx="360" cy="360" r="320" fill="#ffffff" stroke="#202020" stroke-width="2"/>',
        '<circle cx="360" cy="360" r="160" fill="none" stroke="#d0d0d0" stroke-width="1"/>',
        '<line x1="40" y1="360" x2="680" y2="360" stroke="#d0d0d0" stroke-width="1"/>',
        '<line x1="360" y1="40" x2="360" y2="680" stroke="#d0d0d0" stroke-width="1"/>',
    ]
    for row in rows:
        x = center + scale * float(row["x"])
        y = center - scale * float(row["y"])
        mass = int(row["tensor_path_coefficient_mass"])
        t = (mass - min_mass) / (max_mass - min_mass)
        radius = 5.0 + 10.0 * math.sqrt(t)
        color = f"rgb({int(70 + 150 * t)},{int(75 + 60 * (1 - t))},{int(145 - 90 * t)})"
        label = row["atom_label"].replace("{", "").replace("}", "")
        parts.append(
            f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{radius:.3f}" fill="{color}" '
            'stroke="#111111" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{x + 8:.3f}" y="{y - 8:.3f}" font-size="11" '
            f'font-family="Arial, sans-serif" fill="#111111">{row["atom_id"]}: {label}</text>'
        )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def spearman_overlap(top_a: set[int], top_b: set[int]) -> int:
    return len(top_a & top_b)


def build_payloads() -> dict[str, Any]:
    graph_report = load_json(GRAPH_REPORT)
    graph = load_json(GRAPH_JSON)
    atlas_report = load_json(ATLAS_REPORT)
    atlas = load_json(ATLAS_JSON)
    metrics = np.load(GRAPH_METRICS, allow_pickle=False)
    affinity_distances = np.asarray(metrics["affinity_distances"], dtype=np.float64)

    masses = np.asarray([row["tensor_path_coefficient_mass"] for row in atlas["atom_rows"]], dtype=np.float64)
    signatures = np.asarray(
        [row["internal_signature_class_count"] for row in atlas["atom_rows"]],
        dtype=np.float64,
    )
    raw_coords, eigenvalues = classical_mds(affinity_distances)
    oriented = canonicalize_axes(raw_coords, masses)
    norm_max = float(np.linalg.norm(oriented, axis=1).max())
    unit_coords = oriented / norm_max
    scale = choose_disk_scale(unit_coords, affinity_distances)
    coords = np.asarray(scale["coords"], dtype=np.float64)
    poincare_metric = np.asarray(scale["metric"], dtype=np.float64)
    target_metric = np.asarray(scale["target_metric"], dtype=np.float64)
    coordinate_table, coordinate_numeric = coordinate_rows(coords, atlas)

    radii = coordinate_numeric[:, 3]
    central_ranks = coordinate_numeric[:, 7].astype(np.int64)
    mass_ranks = coordinate_numeric[:, 8].astype(np.int64)
    signature_ranks = coordinate_numeric[:, 9].astype(np.int64)
    central_top5 = set(int(idx) for idx in np.argsort(radii)[:5])
    mass_top5 = set(int(idx) for idx in np.argsort(-masses)[:5])
    signature_top5 = set(int(idx) for idx in np.argsort(-signatures)[:5])
    lightest_atom = int(np.argmin(masses))
    heaviest_atom = int(np.argmax(masses))
    richest_signature_atom = int(np.argmax(signatures))
    outermost_atom = int(np.argmax(radii))

    landmark_ids = sorted(mass_top5 | {lightest_atom, heaviest_atom, richest_signature_atom})
    geodesic_neighborhoods = [
        {
            "atom_id": atom_id,
            "atom_label": atom_label(atlas["atom_rows"][atom_id]),
            "central_rank": int(central_ranks[atom_id]),
            "mass_rank": int(mass_ranks[atom_id]),
            "signature_rank": int(signature_ranks[atom_id]),
            "nearest_atoms": nearest_neighbors(atom_id, poincare_metric, atlas),
        }
        for atom_id in landmark_ids
    ]

    stress = float(scale["stress"])
    correlation = float(scale["correlation"])
    radius_mass_correlation = float(np.corrcoef(radii, masses)[0, 1])
    radius_signature_correlation = float(np.corrcoef(radii, signatures)[0, 1])

    embedding = {
        "schema": "c985.d20_poincare_embedding@1",
        "object": "d20",
        "embedding_rule": {
            "source_metric": "signature_affinity_boundary shortest-path matrix",
            "chart": "two-dimensional classical metric MDS, axis signs fixed by lightest and heaviest tensor-mass atoms",
            "disk_scale": "fixed grid search over radii 0.05..0.95 step 0.005 minimizing RMS stress against the source metric scaled to diameter 4",
            "distance_model": "Poincare disk geodesic distance",
        },
        "source_graph_certificate": graph_report.get("certificate_sha256"),
        "source_metric_delta_fraction": graph.get("metric_summaries", [])[2]["gromov_hyperbolicity"][
            "delta_fraction"
        ],
        "coordinate_columns": COORDINATE_COLUMNS,
        "coordinates": coordinate_table,
        "stress_summary": {
            "selected_radius": q(float(scale["radius"])),
            "selected_radius_step": int(scale["radius_step"]),
            "target_metric_diameter": q(float(target_metric.max())),
            "poincare_metric_diameter": q(float(poincare_metric.max())),
            "rms_stress": q(stress),
            "distance_correlation": q(correlation),
            "leading_mds_eigenvalues": [q(float(x)) for x in eigenvalues[:6]],
        },
        "landmark_summary": {
            "lightest_atom": {
                "atom_id": lightest_atom,
                "atom_label": atom_label(atlas["atom_rows"][lightest_atom]),
                "radius": q(float(radii[lightest_atom])),
            },
            "heaviest_atom": {
                "atom_id": heaviest_atom,
                "atom_label": atom_label(atlas["atom_rows"][heaviest_atom]),
                "radius": q(float(radii[heaviest_atom])),
            },
            "richest_signature_atom": {
                "atom_id": richest_signature_atom,
                "atom_label": atom_label(atlas["atom_rows"][richest_signature_atom]),
                "radius": q(float(radii[richest_signature_atom])),
            },
            "outermost_atom": {
                "atom_id": outermost_atom,
                "atom_label": atom_label(atlas["atom_rows"][outermost_atom]),
                "radius": q(float(radii[outermost_atom])),
            },
            "top5_mass_atom_ids": sorted(mass_top5),
            "top5_central_atom_ids": sorted(central_top5),
            "top5_signature_atom_ids": sorted(signature_top5),
            "top5_mass_central_overlap": spearman_overlap(mass_top5, central_top5),
            "top5_signature_central_overlap": spearman_overlap(signature_top5, central_top5),
            "radius_mass_correlation": q(radius_mass_correlation),
            "radius_signature_correlation": q(radius_signature_correlation),
        },
        "geodesic_neighborhoods": geodesic_neighborhoods,
    }

    checks = {
        "hyperbolic_graph_report_certified": graph_report.get("status")
        == "C985_D20_HYPERBOLIC_BOUNDARY_GRAPH_CERTIFIED",
        "boundary_atlas_report_certified": atlas_report.get("status")
        == "C985_D20_BOUNDARY_INVARIANT_ATLAS_CERTIFIED",
        "affinity_distance_matrix_shape_is_20_by_20": tuple(affinity_distances.shape) == (20, 20),
        "leading_two_mds_eigenvalues_are_positive": bool(np.all(eigenvalues[:2] > 0)),
        "selected_radius_step_is_182": int(scale["radius_step"]) == 182,
        "selected_radius_is_0_91": math.isclose(float(scale["radius"]), 0.91, abs_tol=1e-12),
        "all_points_inside_open_poincare_disk": bool(np.all(radii < 1.0)),
        "max_embedding_radius_is_0_91": math.isclose(float(radii.max()), 0.91, abs_tol=1e-12),
        "poincare_distance_matrix_is_20_by_20": tuple(poincare_metric.shape) == (20, 20),
        "poincare_distance_correlation_above_0_71": correlation > 0.71,
        "poincare_rms_stress_below_1_02": stress < 1.02,
        "top5_mass_top5_central_overlap_is_4": spearman_overlap(mass_top5, central_top5) == 4,
        "top5_signature_top5_central_overlap_is_4": spearman_overlap(signature_top5, central_top5) == 4,
        "lightest_atom_is_outermost": lightest_atom == outermost_atom,
        "heaviest_atom_is_in_top5_central": heaviest_atom in central_top5,
        "richest_signature_atom_is_in_top5_central": richest_signature_atom in central_top5,
        "radius_mass_correlation_is_negative": radius_mass_correlation < 0,
        "radius_signature_correlation_is_negative": radius_signature_correlation < 0,
    }

    witness = {
        "atom_count": 20,
        "source_metric": "signature_affinity_boundary",
        "source_metric_diameter": int(affinity_distances.max()),
        "selected_radius": q(float(scale["radius"])),
        "selected_radius_step": int(scale["radius_step"]),
        "poincare_metric_diameter": q(float(poincare_metric.max())),
        "rms_stress": q(stress),
        "distance_correlation": q(correlation),
        "radius_min": q(float(radii.min())),
        "radius_max": q(float(radii.max())),
        "lightest_atom": lightest_atom,
        "heaviest_atom": heaviest_atom,
        "richest_signature_atom": richest_signature_atom,
        "outermost_atom": outermost_atom,
        "top5_mass_central_overlap": spearman_overlap(mass_top5, central_top5),
        "top5_signature_central_overlap": spearman_overlap(signature_top5, central_top5),
        "radius_mass_correlation": q(radius_mass_correlation),
        "radius_signature_correlation": q(radius_signature_correlation),
        "coordinate_table_sha256": sha_quantized_float_array(coordinate_numeric),
        "poincare_distance_sha256": sha_quantized_float_array(poincare_metric),
        "target_metric_sha256": sha_quantized_float_array(target_metric),
    }

    certificate = {
        "schema": "c985.d20_poincare_embedding_certificate@1",
        "status": STATUS if all(checks.values()) else "C985_D20_POINCARE_EMBEDDING_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the signature-affinity boundary metric has a deterministic 2D Poincare disk chart",
            "the stress-selected disk radius is 0.91",
            "Poincare geodesic distances retain positive correlation with the certified graph metric",
            "high tensor-mass and high signature-diversity atoms concentrate toward the disk center",
            "the lightest atom is the outermost point in the chart",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_poincare_embedding@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The certified d20 hyperbolic boundary graph admits a reproducible 2D "
            "Poincare disk chart whose central region captures the dominant C985 "
            "tensor-mass and relation-signature landmarks."
        ),
        "stage_protocol": {
            "draft": "use the certified hyperbolic boundary graph and d20 atlas",
            "witness": "materialize deterministic MDS coordinates, stress-selected Poincare coordinates, and geodesic neighborhoods",
            "coherence": "check disk containment, stress/correlation thresholds, and tensor landmark centrality",
            "closure": "certify a concrete hyperbolic embedding readout while recording that it is not a packet bridge",
            "emit": "emit embedding JSON/CSV/NPZ/SVG and next geometric deepening target",
        },
        "inputs": {
            "hyperbolic_graph_report": input_entry(
                GRAPH_REPORT,
                {
                    "status": graph_report.get("status"),
                    "certificate_sha256": graph_report.get("certificate_sha256"),
                },
            ),
            "hyperbolic_graph": input_entry(GRAPH_JSON),
            "hyperbolic_metrics": input_entry(GRAPH_METRICS),
            "boundary_atlas_report": input_entry(
                ATLAS_REPORT,
                {
                    "status": atlas_report.get("status"),
                    "certificate_sha256": atlas_report.get("certificate_sha256"),
                },
            ),
            "boundary_atlas": input_entry(ATLAS_JSON),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "poincare_embedding": relpath(OUT_DIR / "poincare_embedding.json"),
            "poincare_coordinates_csv": relpath(OUT_DIR / "poincare_coordinates.csv"),
            "poincare_embedding_npz": relpath(OUT_DIR / "poincare_embedding.npz"),
            "poincare_embedding_svg": relpath(OUT_DIR / "poincare_embedding.svg"),
            "embedding_certificate": relpath(OUT_DIR / "embedding_certificate.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "deterministic 2D Poincare disk coordinates for the 20 d20 boundary atoms",
                "stress-selected scale against the certified signature-affinity graph metric",
                "Poincare geodesic neighborhood records for tensor-mass landmarks",
                "centrality comparison between tensor mass, signature diversity, and disk radius",
                "static SVG readout of the certified chart",
            ],
            "does_not_certify_because_not_required": [
                "optimality among all possible hyperbolic embeddings",
                "a packet bridge from d20 atoms to A985/tube coordinates",
                "a packet normalization killing known boundary torsion",
                "pivotal, spherical, unitary, braiding, ribbon, or Drinfeld-center data",
            ],
        },
        "next_highest_yield_item": (
            "Use the Poincare geodesic neighborhoods to grow a landmark-centered "
            "filtration and compare its shells with C985 relation-signature classes."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_poincare_embedding_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load the certified d20 hyperbolic boundary graph and atlas",
            "derive a deterministic two-dimensional MDS chart from the signature-affinity metric",
            "choose Poincare disk scale by fixed stress grid search",
            "verify disk containment, stress, correlation, and landmark centrality",
            "emit geodesic neighborhoods and SVG visualization",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "poincare_embedding": embedding,
        "poincare_coordinates_csv": coordinate_csv(coordinate_table),
        "coordinate_table": coordinate_numeric,
        "poincare_distances": poincare_metric,
        "target_metric": target_metric,
        "embedding_certificate": certificate,
        "poincare_embedding_svg": svg_payload(coordinate_table, atlas),
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
    write_json(OUT_DIR / "poincare_embedding.json", payloads["poincare_embedding"])
    (OUT_DIR / "poincare_coordinates.csv").write_text(
        payloads["poincare_coordinates_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "poincare_embedding.npz",
        coordinate_table=payloads["coordinate_table"],
        poincare_distances=payloads["poincare_distances"],
        target_metric=payloads["target_metric"],
    )
    (OUT_DIR / "poincare_embedding.svg").write_text(
        payloads["poincare_embedding_svg"],
        encoding="utf-8",
    )
    write_json(OUT_DIR / "embedding_certificate.json", payloads["embedding_certificate"])
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
                "selected_radius": witness["selected_radius"],
                "rms_stress": witness["rms_stress"],
                "distance_correlation": witness["distance_correlation"],
                "top5_mass_central_overlap": witness["top5_mass_central_overlap"],
                "top5_signature_central_overlap": witness["top5_signature_central_overlap"],
                "next_highest_yield_item": payloads["report"]["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
