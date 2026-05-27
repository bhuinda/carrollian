from __future__ import annotations

import csv
import itertools
import json
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_hyperbolic_boundary_graph import (
        atom_signature_sets,
        gromov_hyperbolicity,
        signature_class_ids,
    )
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
    from derive_c985_d20_hyperbolic_boundary_graph import (
        atom_signature_sets,
        gromov_hyperbolicity,
        signature_class_ids,
    )
    from derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "c985_d20_signature_class_nerve"
STATUS = "C985_D20_SIGNATURE_CLASS_NERVE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

FILTRATION_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_poincare_landmark_filtration"
GRAPH_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_hyperbolic_boundary_graph"
ATLAS_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_boundary_invariant_atlas"
GEOMETRY_DIR = D20_INVARIANTS / "proof_obligations" / "c985_tensor_geometry_invariants"

FILTRATION_REPORT = FILTRATION_DIR / "report.json"
LANDMARK_FILTRATION_JSON = FILTRATION_DIR / "landmark_filtration.json"
FILTRATION_TABLES = FILTRATION_DIR / "filtration_tables.npz"
GRAPH_REPORT = GRAPH_DIR / "report.json"
GRAPH_JSON = GRAPH_DIR / "boundary_hyperbolic_graph.json"
GRAPH_METRICS = GRAPH_DIR / "boundary_hyperbolic_metrics.npz"
ATLAS_JSON = ATLAS_DIR / "d20_boundary_invariant_atlas.json"
RELATION_GEOMETRY_SIGNATURES = GEOMETRY_DIR / "relation_geometry_signatures.npz"

DERIVE_SCRIPT = ROOT / "src" / "derive_c985_d20_signature_class_nerve.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_d20_signature_class_nerve.py"

NERVE_PAIR_COLUMNS = [
    "seed_i",
    "seed_j",
    "chart_i_size",
    "chart_j_size",
    "intersection_atom_count",
    "intersection_signature_class_count",
    "signature_deficit",
    "intersection_tensor_path_coefficient_mass",
    "atom_deficit_distance",
]


def atom_label(atlas: dict[str, Any], atom_id: int) -> str:
    return "{" + ",".join(atlas["atom_rows"][atom_id]["h6_triple"]) + "}"


def csv_text(headers: list[str], rows: list[dict[str, Any]]) -> str:
    out = [",".join(headers)]
    for row in rows:
        out.append(",".join(str(row[column]) for column in headers))
    return "\n".join(out) + "\n"


def histogram(values: list[int]) -> list[dict[str, int]]:
    counts: dict[int, int] = {}
    for value in values:
        counts[int(value)] = counts.get(int(value), 0) + 1
    return [
        {"value": int(value), "count": int(count)}
        for value, count in sorted(counts.items())
    ]


def full_coverage_charts(
    entry_order: np.ndarray,
    coverage_matrix: np.ndarray,
    thresholds: np.ndarray,
) -> tuple[list[list[int]], np.ndarray]:
    atom_count = int(entry_order.shape[0])
    chart_rows = np.zeros((atom_count, 4), dtype=np.int64)
    charts: list[list[int]] = []
    for seed_atom_id in range(atom_count):
        full_ranks = np.flatnonzero(coverage_matrix[seed_atom_id] == 233)
        if full_ranks.size == 0:
            raise ValueError(f"seed {seed_atom_id} never reaches full relation-signature coverage")
        rank_index = int(full_ranks[0])
        atoms = [int(x) for x in entry_order[seed_atom_id, : rank_index + 1]]
        charts.append(atoms)
        chart_rows[seed_atom_id] = np.asarray(
            [
                seed_atom_id,
                rank_index + 1,
                int(coverage_matrix[seed_atom_id, rank_index]),
                int(round(float(thresholds[seed_atom_id, rank_index]) * 10**10)),
            ],
            dtype=np.int64,
        )
    return charts, chart_rows


def signature_union_count(atom_ids: set[int], signature_sets: list[set[int]]) -> int:
    if not atom_ids:
        return 0
    return len(set().union(*(signature_sets[atom_id] for atom_id in sorted(atom_ids))))


def chart_incidence(charts: list[list[int]]) -> np.ndarray:
    incidence = np.zeros((len(charts), len(charts)), dtype=np.int8)
    for seed_atom_id, chart in enumerate(charts):
        incidence[seed_atom_id, chart] = 1
    return incidence


def triangle_violation_count(distances: np.ndarray) -> int:
    count = 0
    node_count = int(distances.shape[0])
    for i, j, k in itertools.product(range(node_count), repeat=3):
        if int(distances[i, j]) > int(distances[i, k] + distances[k, j]):
            count += 1
    return count


def enrich_gromov(summary: dict[str, Any], atlas: dict[str, Any]) -> dict[str, Any]:
    ids = [int(x) for x in summary["witness_atom_ids"]]
    return {
        **summary,
        "witness_atom_labels": [atom_label(atlas, atom_id) for atom_id in ids],
    }


def metric_summary(name: str, distances: np.ndarray, atlas: dict[str, Any]) -> dict[str, Any]:
    positive = distances[distances > 0]
    hyperbolicity = enrich_gromov(gromov_hyperbolicity(distances), atlas)
    return {
        "name": name,
        "diameter": int(distances.max()),
        "positive_distance_min": int(positive.min()) if positive.size else 0,
        "positive_distance_max": int(positive.max()) if positive.size else 0,
        "triangle_violation_count": triangle_violation_count(distances),
        "gromov_hyperbolicity": hyperbolicity,
    }


def witness_overlay(
    graph_summary: dict[str, Any],
    charts: list[list[int]],
    chart_atom_incidence: np.ndarray,
    signature_sets: list[set[int]],
    masses: np.ndarray,
    atlas: dict[str, Any],
) -> dict[str, Any]:
    witness = graph_summary["gromov_hyperbolicity"]
    witness_atom_ids = [int(x) for x in witness["witness_atom_ids"]]
    membership_sets = [
        set(int(seed) for seed in np.flatnonzero(chart_atom_incidence[:, atom_id]))
        for atom_id in witness_atom_ids
    ]
    common_chart_ids = sorted(set.intersection(*membership_sets))
    centered_intersection = set.intersection(*(set(charts[atom_id]) for atom_id in witness_atom_ids))
    pair_common_counts = [
        {
            "atom_i": i,
            "atom_j": j,
            "common_chart_count": len(membership_sets[pos_i] & membership_sets[pos_j]),
        }
        for pos_i, i in enumerate(witness_atom_ids)
        for pos_j, j in enumerate(witness_atom_ids)
        if pos_i < pos_j
    ]
    return {
        "source_metric": graph_summary["name"],
        "source_delta_fraction": witness["delta_fraction"],
        "witness_atom_ids": witness_atom_ids,
        "witness_atom_labels": [atom_label(atlas, atom_id) for atom_id in witness_atom_ids],
        "common_full_coverage_chart_count": len(common_chart_ids),
        "common_full_coverage_chart_ids": common_chart_ids,
        "common_full_coverage_chart_labels": [atom_label(atlas, atom_id) for atom_id in common_chart_ids],
        "witness_centered_chart_intersection_atom_count": len(centered_intersection),
        "witness_centered_chart_intersection_atom_ids": sorted(centered_intersection),
        "witness_centered_chart_intersection_atom_labels": [
            atom_label(atlas, atom_id) for atom_id in sorted(centered_intersection)
        ],
        "witness_centered_chart_intersection_signature_class_count": signature_union_count(
            centered_intersection,
            signature_sets,
        ),
        "witness_centered_chart_intersection_tensor_mass": int(
            sum(int(masses[atom_id]) for atom_id in centered_intersection)
        ),
        "pair_common_chart_counts": pair_common_counts,
    }


def build_nerve_payload(
    atlas: dict[str, Any],
    graph: dict[str, Any],
    charts: list[list[int]],
    chart_rows: np.ndarray,
    signature_sets: list[set[int]],
) -> dict[str, Any]:
    atom_count = len(charts)
    masses = np.asarray(
        [row["tensor_path_coefficient_mass"] for row in atlas["atom_rows"]],
        dtype=np.int64,
    )
    chart_atom_matrix = chart_incidence(charts)
    atom_chart_membership_matrix = chart_atom_matrix.T.astype(np.int8)
    chart_sizes = chart_atom_matrix.sum(axis=1).astype(np.int64)

    pair_rows: list[dict[str, Any]] = []
    pair_array_rows: list[list[int]] = []
    intersection_atoms = np.zeros((atom_count, atom_count), dtype=np.int64)
    intersection_signatures = np.zeros((atom_count, atom_count), dtype=np.int64)
    intersection_mass = np.zeros((atom_count, atom_count), dtype=np.int64)

    for seed_i, seed_j in itertools.combinations(range(atom_count), 2):
        common_atoms = set(charts[seed_i]) & set(charts[seed_j])
        signature_count = signature_union_count(common_atoms, signature_sets)
        mass = int(sum(int(masses[atom_id]) for atom_id in common_atoms))
        intersection_atoms[seed_i, seed_j] = intersection_atoms[seed_j, seed_i] = len(common_atoms)
        intersection_signatures[seed_i, seed_j] = intersection_signatures[seed_j, seed_i] = signature_count
        intersection_mass[seed_i, seed_j] = intersection_mass[seed_j, seed_i] = mass
        row = {
            "seed_i": seed_i,
            "seed_j": seed_j,
            "seed_i_label": atom_label(atlas, seed_i),
            "seed_j_label": atom_label(atlas, seed_j),
            "chart_i_size": int(chart_sizes[seed_i]),
            "chart_j_size": int(chart_sizes[seed_j]),
            "intersection_atom_count": len(common_atoms),
            "intersection_atom_ids": sorted(common_atoms),
            "intersection_atom_labels": [atom_label(atlas, atom_id) for atom_id in sorted(common_atoms)],
            "intersection_signature_class_count": signature_count,
            "signature_deficit": 233 - signature_count,
            "intersection_tensor_path_coefficient_mass": mass,
            "atom_deficit_distance": atom_count - len(common_atoms),
        }
        pair_rows.append(row)
        pair_array_rows.append([int(row[column]) for column in NERVE_PAIR_COLUMNS])

    np.fill_diagonal(intersection_atoms, chart_sizes)
    for seed_atom_id, chart in enumerate(charts):
        chart_set = set(chart)
        intersection_signatures[seed_atom_id, seed_atom_id] = signature_union_count(
            chart_set,
            signature_sets,
        )
        intersection_mass[seed_atom_id, seed_atom_id] = int(
            sum(int(masses[atom_id]) for atom_id in chart_set)
        )

    signature_deficit_contrast = 233 - intersection_signatures
    np.fill_diagonal(signature_deficit_contrast, 0)
    atom_deficit_distances = atom_count - intersection_atoms
    np.fill_diagonal(atom_deficit_distances, 0)

    membership_hamming_distances = np.zeros((atom_count, atom_count), dtype=np.int64)
    for atom_i, atom_j in itertools.combinations(range(atom_count), 2):
        distance = int(
            np.count_nonzero(
                atom_chart_membership_matrix[atom_i] != atom_chart_membership_matrix[atom_j]
            )
        )
        membership_hamming_distances[atom_i, atom_j] = distance
        membership_hamming_distances[atom_j, atom_i] = distance

    atom_deficit_summary = metric_summary(
        "full_coverage_chart_atom_deficit",
        atom_deficit_distances,
        atlas,
    )
    membership_hamming_summary = metric_summary(
        "atom_chart_membership_hamming",
        membership_hamming_distances,
        atlas,
    )
    overlays = [
        witness_overlay(summary, charts, chart_atom_matrix, signature_sets, masses, atlas)
        for summary in graph["metric_summaries"]
    ]

    min_signature_count = int(min(int(row["intersection_signature_class_count"]) for row in pair_rows))
    min_signature_pairs = [
        row for row in pair_rows if int(row["intersection_signature_class_count"]) == min_signature_count
    ]
    affinity_overlay = next(
        row for row in overlays if row["source_metric"] == "signature_affinity_boundary"
    )
    affinity_witness_atoms = set(int(x) for x in affinity_overlay["witness_atom_ids"])
    atom_deficit_witness_atoms = set(
        int(x)
        for x in atom_deficit_summary["gromov_hyperbolicity"]["witness_atom_ids"]
    )

    nerve = {
        "schema": "c985.d20_signature_class_nerve@1",
        "object": "d20",
        "nerve_rule": {
            "charts": "for each atom seed, take the first Poincare geodesic ball whose atom signatures cover all 233 relation-signature classes",
            "chart_intersection": "intersect charts as atom sets, then measure the union of relation-signature classes visible on the common atoms",
            "atom_deficit_metric": "20 minus chart-intersection atom count, with diagonal zero",
            "dual_membership_metric": "Hamming distance between atom membership codes across the 20 full-coverage charts",
        },
        "chart_vertices": [
            {
                "seed_atom_id": seed_atom_id,
                "seed_atom_label": atom_label(atlas, seed_atom_id),
                "full_coverage_ball_size": int(chart_rows[seed_atom_id, 1]),
                "full_coverage_signature_class_count": int(chart_rows[seed_atom_id, 2]),
                "threshold_times_1e10": int(chart_rows[seed_atom_id, 3]),
                "atom_ids": charts[seed_atom_id],
                "atom_labels": [atom_label(atlas, atom_id) for atom_id in charts[seed_atom_id]],
            }
            for seed_atom_id in range(atom_count)
        ],
        "pair_intersection_summary": {
            "pair_count": len(pair_rows),
            "chart_size_histogram": histogram([int(x) for x in chart_sizes.tolist()]),
            "atom_intersection_histogram": histogram(
                [int(row["intersection_atom_count"]) for row in pair_rows]
            ),
            "signature_intersection_histogram": histogram(
                [int(row["intersection_signature_class_count"]) for row in pair_rows]
            ),
            "minimum_signature_intersection_pairs": min_signature_pairs,
        },
        "metric_summaries": [atom_deficit_summary, membership_hamming_summary],
        "hyperbolic_witness_overlays": overlays,
        "affinity_overlap_with_atom_deficit_witness": {
            "affinity_witness_atom_ids": sorted(affinity_witness_atoms),
            "atom_deficit_witness_atom_ids": sorted(atom_deficit_witness_atoms),
            "overlap_atom_ids": sorted(affinity_witness_atoms & atom_deficit_witness_atoms),
            "overlap_count": len(affinity_witness_atoms & atom_deficit_witness_atoms),
        },
    }

    return {
        "nerve": nerve,
        "nerve_pair_records_csv": csv_text(NERVE_PAIR_COLUMNS, pair_rows),
        "pair_records": np.asarray(pair_array_rows, dtype=np.int64),
        "chart_rows": chart_rows,
        "chart_atom_incidence": chart_atom_matrix,
        "atom_chart_membership": atom_chart_membership_matrix,
        "chart_intersection_atom_counts": intersection_atoms,
        "chart_intersection_signature_counts": intersection_signatures,
        "chart_intersection_tensor_mass": intersection_mass,
        "signature_deficit_contrast": signature_deficit_contrast,
        "atom_deficit_distances": atom_deficit_distances,
        "membership_hamming_distances": membership_hamming_distances,
        "atom_deficit_summary": atom_deficit_summary,
        "membership_hamming_summary": membership_hamming_summary,
        "hyperbolic_witness_overlays": overlays,
        "min_signature_pairs": min_signature_pairs,
    }


def build_payloads() -> dict[str, Any]:
    filtration_report = load_json(FILTRATION_REPORT)
    landmark_filtration = load_json(LANDMARK_FILTRATION_JSON)
    graph_report = load_json(GRAPH_REPORT)
    graph = load_json(GRAPH_JSON)
    atlas = load_json(ATLAS_JSON)
    relation_npz = np.load(RELATION_GEOMETRY_SIGNATURES, allow_pickle=False)
    relation_records = np.asarray(relation_npz["relation_records"], dtype=np.int64)
    signature_sets = atom_signature_sets(atlas, relation_records, signature_class_ids(relation_records))
    filtration_tables = np.load(FILTRATION_TABLES, allow_pickle=False)
    entry_order = np.asarray(filtration_tables["entry_order"], dtype=np.int64)
    coverage_matrix = np.asarray(filtration_tables["coverage_matrix"], dtype=np.int64)
    thresholds = np.asarray(filtration_tables["thresholds"], dtype=np.float64)
    charts, chart_rows = full_coverage_charts(entry_order, coverage_matrix, thresholds)
    nerve_payload = build_nerve_payload(atlas, graph, charts, chart_rows, signature_sets)

    pair_records = nerve_payload["pair_records"]
    chart_atom_incidence = nerve_payload["chart_atom_incidence"]
    atom_deficit_distances = nerve_payload["atom_deficit_distances"]
    membership_hamming_distances = nerve_payload["membership_hamming_distances"]
    atom_deficit_summary = nerve_payload["atom_deficit_summary"]
    membership_hamming_summary = nerve_payload["membership_hamming_summary"]
    overlays = nerve_payload["hyperbolic_witness_overlays"]
    overlay_by_name = {row["source_metric"]: row for row in overlays}
    min_signature_pairs = nerve_payload["min_signature_pairs"]
    affinity_overlap = nerve_payload["nerve"]["affinity_overlap_with_atom_deficit_witness"]

    checks = {
        "filtration_report_certified": filtration_report.get("status")
        == "C985_D20_POINCARE_LANDMARK_FILTRATION_CERTIFIED",
        "hyperbolic_graph_report_certified": graph_report.get("status")
        == "C985_D20_HYPERBOLIC_BOUNDARY_GRAPH_CERTIFIED",
        "landmark_filtration_signature_class_count_is_233": int(
            landmark_filtration.get("signature_class_count", 0)
        )
        == 233,
        "atom_count_is_20": len(atlas["atom_rows"]) == 20,
        "chart_count_is_20": len(charts) == 20,
        "every_chart_has_full_signature_coverage": bool(np.all(chart_rows[:, 2] == 233)),
        "chart_size_min_is_7": int(chart_rows[:, 1].min()) == 7,
        "chart_size_max_is_14": int(chart_rows[:, 1].max()) == 14,
        "chart_size_sum_is_240": int(chart_rows[:, 1].sum()) == 240,
        "chart_atom_incidence_shape_is_20_by_20": tuple(chart_atom_incidence.shape) == (20, 20),
        "nerve_pair_record_count_is_190": int(pair_records.shape[0]) == 190,
        "chart_pair_atom_intersection_min_is_4": int(pair_records[:, 4].min()) == 4,
        "chart_pair_signature_intersection_min_is_197": int(pair_records[:, 5].min()) == 197,
        "chart_pair_signature_intersection_max_is_233": int(pair_records[:, 5].max()) == 233,
        "minimum_signature_intersection_pair_count_is_4": len(min_signature_pairs) == 4,
        "atom_deficit_metric_triangle_holds": atom_deficit_summary["triangle_violation_count"] == 0,
        "atom_deficit_delta_numerator_is_4": atom_deficit_summary["gromov_hyperbolicity"][
            "delta_numerator_over_2"
        ]
        == 4,
        "atom_deficit_witness_is_0_4_10_14": atom_deficit_summary["gromov_hyperbolicity"][
            "witness_atom_ids"
        ]
        == [0, 4, 10, 14],
        "atom_deficit_witness_overlaps_affinity_witness_in_3_atoms": affinity_overlap[
            "overlap_count"
        ]
        == 3,
        "membership_hamming_metric_triangle_holds": membership_hamming_summary[
            "triangle_violation_count"
        ]
        == 0,
        "membership_hamming_delta_numerator_is_16": membership_hamming_summary[
            "gromov_hyperbolicity"
        ]["delta_numerator_over_2"]
        == 16,
        "membership_hamming_witness_is_1_7_10_14": membership_hamming_summary[
            "gromov_hyperbolicity"
        ]["witness_atom_ids"]
        == [1, 7, 10, 14],
        "johnson_witness_common_chart_count_is_1": overlay_by_name[
            "unweighted_johnson_boundary"
        ]["common_full_coverage_chart_count"]
        == 1,
        "signature_distance_witness_common_chart_count_is_1": overlay_by_name[
            "signature_distance_boundary"
        ]["common_full_coverage_chart_count"]
        == 1,
        "affinity_witness_common_chart_count_is_0": overlay_by_name[
            "signature_affinity_boundary"
        ]["common_full_coverage_chart_count"]
        == 0,
        "johnson_witness_centered_intersection_signature_coverage_is_207": overlay_by_name[
            "unweighted_johnson_boundary"
        ]["witness_centered_chart_intersection_signature_class_count"]
        == 207,
        "signature_witness_centered_intersection_signature_coverage_is_203": overlay_by_name[
            "signature_distance_boundary"
        ]["witness_centered_chart_intersection_signature_class_count"]
        == 203,
        "affinity_witness_centered_intersection_signature_coverage_is_197": overlay_by_name[
            "signature_affinity_boundary"
        ]["witness_centered_chart_intersection_signature_class_count"]
        == 197,
        "affinity_witness_centered_signature_coverage_hits_pairwise_floor": overlay_by_name[
            "signature_affinity_boundary"
        ]["witness_centered_chart_intersection_signature_class_count"]
        == int(pair_records[:, 5].min()),
    }

    witness = {
        "atom_count": 20,
        "chart_count": len(charts),
        "signature_class_count": 233,
        "chart_size_min": int(chart_rows[:, 1].min()),
        "chart_size_max": int(chart_rows[:, 1].max()),
        "chart_size_sum": int(chart_rows[:, 1].sum()),
        "nerve_pair_count": int(pair_records.shape[0]),
        "pair_signature_intersection_min": int(pair_records[:, 5].min()),
        "pair_signature_intersection_max": int(pair_records[:, 5].max()),
        "minimum_signature_intersection_pair_count": len(min_signature_pairs),
        "atom_deficit_diameter": atom_deficit_summary["diameter"],
        "atom_deficit_delta_fraction": atom_deficit_summary["gromov_hyperbolicity"][
            "delta_fraction"
        ],
        "atom_deficit_witness_atom_ids": atom_deficit_summary["gromov_hyperbolicity"][
            "witness_atom_ids"
        ],
        "membership_hamming_diameter": membership_hamming_summary["diameter"],
        "membership_hamming_delta_fraction": membership_hamming_summary["gromov_hyperbolicity"][
            "delta_fraction"
        ],
        "membership_hamming_witness_atom_ids": membership_hamming_summary["gromov_hyperbolicity"][
            "witness_atom_ids"
        ],
        "affinity_witness_common_chart_count": overlay_by_name["signature_affinity_boundary"][
            "common_full_coverage_chart_count"
        ],
        "affinity_witness_centered_intersection_signature_coverage": overlay_by_name[
            "signature_affinity_boundary"
        ]["witness_centered_chart_intersection_signature_class_count"],
        "affinity_overlap_with_atom_deficit_witness_count": affinity_overlap["overlap_count"],
        "chart_rows_sha256": sha_array(chart_rows),
        "nerve_pair_records_sha256": sha_array(pair_records),
        "chart_atom_incidence_sha256": sha_array(chart_atom_incidence),
        "chart_intersection_atom_counts_sha256": sha_array(
            nerve_payload["chart_intersection_atom_counts"]
        ),
        "chart_intersection_signature_counts_sha256": sha_array(
            nerve_payload["chart_intersection_signature_counts"]
        ),
        "atom_deficit_distances_sha256": sha_array(atom_deficit_distances),
        "membership_hamming_distances_sha256": sha_array(membership_hamming_distances),
    }

    certificate = {
        "schema": "c985.d20_signature_class_nerve_certificate@1",
        "status": STATUS if all(checks.values()) else "C985_D20_SIGNATURE_CLASS_NERVE_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the 20 first-full-coverage Poincare balls form a deterministic chart nerve",
            "chart intersections never drop below four atoms or 197 relation-signature classes",
            "the chart atom-deficit metric is hyperbolic with four-point witness [0,4,10,14]",
            "that nerve witness shares three atoms with the certified signature-affinity graph witness",
            "the signature-affinity witness is the unique certified graph witness whose four atoms share no full-coverage chart",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_class_nerve@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The full-coverage Poincare filtration balls form a reproducible "
            "signature-class nerve whose chart-overlap metrics retain hyperbolic "
            "four-point structure and expose the signature-affinity witness at the "
            "pairwise signature-coverage floor."
        ),
        "stage_protocol": {
            "draft": "use the certified full-coverage filtration balls as chart vertices",
            "witness": "materialize chart incidence, chart intersections, atom-deficit and membership-code metrics",
            "coherence": "check nerve pair counts, intersection floors, metric triangle laws, and four-point witnesses",
            "closure": "certify a signature-class nerve readout without claiming a packet bridge or optional categorical enrichment",
            "emit": "emit nerve JSON/CSV/NPZ, certificate, report, and next nerve-deepening target",
        },
        "inputs": {
            "filtration_report": input_entry(
                FILTRATION_REPORT,
                {
                    "status": filtration_report.get("status"),
                    "certificate_sha256": filtration_report.get("certificate_sha256"),
                },
            ),
            "landmark_filtration": input_entry(LANDMARK_FILTRATION_JSON),
            "filtration_tables": input_entry(FILTRATION_TABLES),
            "hyperbolic_graph_report": input_entry(
                GRAPH_REPORT,
                {
                    "status": graph_report.get("status"),
                    "certificate_sha256": graph_report.get("certificate_sha256"),
                },
            ),
            "hyperbolic_graph": input_entry(GRAPH_JSON),
            "hyperbolic_metrics": input_entry(GRAPH_METRICS),
            "boundary_atlas": input_entry(ATLAS_JSON),
            "relation_geometry_signatures": input_entry(RELATION_GEOMETRY_SIGNATURES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_class_nerve": relpath(OUT_DIR / "signature_class_nerve.json"),
            "nerve_pair_records_csv": relpath(OUT_DIR / "nerve_pair_records.csv"),
            "signature_class_nerve_tables": relpath(OUT_DIR / "signature_class_nerve_tables.npz"),
            "nerve_certificate": relpath(OUT_DIR / "nerve_certificate.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "20 full-coverage Poincare filtration charts",
                "all 190 chart-pair atom/signature/mass intersection records",
                "chart atom-incidence and atom chart-membership matrices",
                "chart atom-deficit and membership-code Hamming metrics",
                "overlay of certified hyperbolic graph witnesses with the chart nerve",
            ],
            "does_not_certify_because_not_required": [
                "optimality among all possible nerves or covers",
                "a packet bridge from d20 atoms to A985/tube coordinates",
                "a packet normalization killing known boundary torsion",
                "pivotal, spherical, unitary, braiding, ribbon, or Drinfeld-center data",
            ],
        },
        "next_highest_yield_item": (
            "Use the signature-class nerve to choose a small hyperbolic atlas of "
            "charts, then compute transition maps between overlapping full-coverage balls."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_class_nerve_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load the certified Poincare landmark filtration and hyperbolic graph",
            "reconstruct first-full-coverage charts from filtration tables",
            "materialize chart-pair intersections and signature coverage",
            "verify atom-deficit and membership-code metric four-point witnesses",
            "overlay the certified graph hyperbolicity witnesses with the chart nerve",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_class_nerve": nerve_payload["nerve"],
        "nerve_pair_records_csv": nerve_payload["nerve_pair_records_csv"],
        "nerve_pair_records": pair_records,
        "chart_rows": nerve_payload["chart_rows"],
        "chart_atom_incidence": chart_atom_incidence,
        "atom_chart_membership": nerve_payload["atom_chart_membership"],
        "chart_intersection_atom_counts": nerve_payload["chart_intersection_atom_counts"],
        "chart_intersection_signature_counts": nerve_payload["chart_intersection_signature_counts"],
        "chart_intersection_tensor_mass": nerve_payload["chart_intersection_tensor_mass"],
        "signature_deficit_contrast": nerve_payload["signature_deficit_contrast"],
        "atom_deficit_distances": atom_deficit_distances,
        "membership_hamming_distances": membership_hamming_distances,
        "nerve_certificate": certificate,
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
    write_json(OUT_DIR / "signature_class_nerve.json", payloads["signature_class_nerve"])
    (OUT_DIR / "nerve_pair_records.csv").write_text(
        payloads["nerve_pair_records_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_class_nerve_tables.npz",
        nerve_pair_records=payloads["nerve_pair_records"],
        chart_rows=payloads["chart_rows"],
        chart_atom_incidence=payloads["chart_atom_incidence"],
        atom_chart_membership=payloads["atom_chart_membership"],
        chart_intersection_atom_counts=payloads["chart_intersection_atom_counts"],
        chart_intersection_signature_counts=payloads["chart_intersection_signature_counts"],
        chart_intersection_tensor_mass=payloads["chart_intersection_tensor_mass"],
        signature_deficit_contrast=payloads["signature_deficit_contrast"],
        atom_deficit_distances=payloads["atom_deficit_distances"],
        membership_hamming_distances=payloads["membership_hamming_distances"],
    )
    write_json(OUT_DIR / "nerve_certificate.json", payloads["nerve_certificate"])
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
                "pair_signature_intersection_min": witness["pair_signature_intersection_min"],
                "atom_deficit_delta_fraction": witness["atom_deficit_delta_fraction"],
                "atom_deficit_witness_atom_ids": witness["atom_deficit_witness_atom_ids"],
                "affinity_overlap_with_atom_deficit_witness_count": witness[
                    "affinity_overlap_with_atom_deficit_witness_count"
                ],
                "next_highest_yield_item": payloads["report"]["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
