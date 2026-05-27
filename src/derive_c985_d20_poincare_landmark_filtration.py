from __future__ import annotations

import csv
import json
import math
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_hyperbolic_boundary_graph import (
        atom_signature_sets,
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


THEOREM_ID = "c985_d20_poincare_landmark_filtration"
STATUS = "C985_D20_POINCARE_LANDMARK_FILTRATION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

POINCARE_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_poincare_embedding"
ATLAS_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_boundary_invariant_atlas"
GEOMETRY_DIR = D20_INVARIANTS / "proof_obligations" / "c985_tensor_geometry_invariants"

POINCARE_REPORT = POINCARE_DIR / "report.json"
POINCARE_JSON = POINCARE_DIR / "poincare_embedding.json"
POINCARE_NPZ = POINCARE_DIR / "poincare_embedding.npz"
ATLAS_REPORT = ATLAS_DIR / "report.json"
ATLAS_JSON = ATLAS_DIR / "d20_boundary_invariant_atlas.json"
ATLAS_NPZ = ATLAS_DIR / "d20_boundary_invariant_atlas.npz"
GEOMETRY_REPORT = GEOMETRY_DIR / "report.json"
RELATION_GEOMETRY_SIGNATURES = GEOMETRY_DIR / "relation_geometry_signatures.npz"

DERIVE_SCRIPT = ROOT / "src" / "derive_c985_d20_poincare_landmark_filtration.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_d20_poincare_landmark_filtration.py"

JSON_FLOAT_DIGITS = 10
FLOAT_HASH_SCALE = 10**JSON_FLOAT_DIGITS

FILTRATION_COLUMNS = [
    "seed_atom_id",
    "rank",
    "entering_atom_id",
    "poincare_threshold",
    "new_signature_class_count",
    "cumulative_signature_class_count",
    "cumulative_tensor_path_coefficient_mass",
    "cumulative_internal_signature_count",
    "full_coverage",
]

FILTRATION_INT_COLUMNS = [
    "seed_atom_id",
    "rank",
    "entering_atom_id",
    "new_signature_class_count",
    "cumulative_signature_class_count",
    "cumulative_tensor_path_coefficient_mass",
    "cumulative_internal_signature_count",
    "full_coverage",
]


def q(value: float) -> float:
    return round(float(value), JSON_FLOAT_DIGITS)


def sha_quantized_float_array(array: np.ndarray) -> str:
    stable = np.rint(np.asarray(array, dtype=np.float64) * FLOAT_HASH_SCALE).astype(np.int64)
    return sha_array(stable)


def atom_label(atlas: dict[str, Any], atom_id: int) -> str:
    return "{" + ",".join(atlas["atom_rows"][atom_id]["h6_triple"]) + "}"


def csv_text(headers: list[str], rows: list[dict[str, Any]]) -> str:
    out = [",".join(headers)]
    for row in rows:
        out.append(",".join(str(row[column]) for column in headers))
    return "\n".join(out) + "\n"


def signature_incidence(signature_sets: list[set[int]], class_count: int) -> np.ndarray:
    incidence = np.zeros((len(signature_sets), class_count), dtype=np.int8)
    for atom_id, class_set in enumerate(signature_sets):
        incidence[atom_id, sorted(class_set)] = 1
    return incidence


def ball_order(seed_atom_id: int, distances: np.ndarray) -> list[int]:
    return sorted(
        range(int(distances.shape[0])),
        key=lambda atom_id: (float(distances[seed_atom_id, atom_id]), atom_id),
    )


def build_filtration(
    atlas: dict[str, Any],
    distances: np.ndarray,
    signature_sets: list[set[int]],
) -> dict[str, Any]:
    atom_count = int(distances.shape[0])
    masses = np.asarray(
        [row["tensor_path_coefficient_mass"] for row in atlas["atom_rows"]],
        dtype=np.int64,
    )
    signature_counts = np.asarray(
        [row["internal_signature_class_count"] for row in atlas["atom_rows"]],
        dtype=np.int64,
    )
    all_signature_classes = set().union(*signature_sets)
    class_count = len(all_signature_classes)

    records: list[dict[str, Any]] = []
    int_rows: list[list[int]] = []
    entry_order = np.zeros((atom_count, atom_count), dtype=np.int64)
    thresholds = np.zeros((atom_count, atom_count), dtype=np.float64)
    novelty = np.zeros((atom_count, atom_count), dtype=np.int64)
    coverage = np.zeros((atom_count, atom_count), dtype=np.int64)
    mass = np.zeros((atom_count, atom_count), dtype=np.int64)
    signature_count_sum = np.zeros((atom_count, atom_count), dtype=np.int64)
    full_coverage_by_seed: list[dict[str, Any]] = []

    for seed_atom_id in range(atom_count):
        order = ball_order(seed_atom_id, distances)
        seen: set[int] = set()
        cumulative_mass = 0
        cumulative_signature_count = 0
        first_full: dict[str, Any] | None = None
        for rank, entering_atom_id in enumerate(order, start=1):
            new_classes = signature_sets[entering_atom_id].difference(seen)
            seen.update(signature_sets[entering_atom_id])
            cumulative_mass += int(masses[entering_atom_id])
            cumulative_signature_count += int(signature_counts[entering_atom_id])
            threshold = float(distances[seed_atom_id, entering_atom_id])
            is_full = len(seen) == class_count

            entry_order[seed_atom_id, rank - 1] = entering_atom_id
            thresholds[seed_atom_id, rank - 1] = threshold
            novelty[seed_atom_id, rank - 1] = len(new_classes)
            coverage[seed_atom_id, rank - 1] = len(seen)
            mass[seed_atom_id, rank - 1] = cumulative_mass
            signature_count_sum[seed_atom_id, rank - 1] = cumulative_signature_count

            record = {
                "seed_atom_id": seed_atom_id,
                "seed_atom_label": atom_label(atlas, seed_atom_id),
                "rank": rank,
                "entering_atom_id": entering_atom_id,
                "entering_atom_label": atom_label(atlas, entering_atom_id),
                "poincare_threshold": q(threshold),
                "new_signature_class_count": len(new_classes),
                "cumulative_signature_class_count": len(seen),
                "cumulative_tensor_path_coefficient_mass": cumulative_mass,
                "cumulative_internal_signature_count": cumulative_signature_count,
                "full_coverage": int(is_full),
            }
            records.append(record)
            int_rows.append([int(record[column]) for column in FILTRATION_INT_COLUMNS])

            if is_full and first_full is None:
                first_full = {
                    "seed_atom_id": seed_atom_id,
                    "seed_atom_label": atom_label(atlas, seed_atom_id),
                    "ball_size": rank,
                    "poincare_threshold": q(threshold),
                    "cumulative_tensor_path_coefficient_mass": cumulative_mass,
                    "atom_ids": order[:rank],
                    "atom_labels": [atom_label(atlas, atom_id) for atom_id in order[:rank]],
                    "signature_class_count": len(seen),
                }

        if first_full is None:
            raise ValueError(f"seed {seed_atom_id} never reaches full signature coverage")
        full_coverage_by_seed.append(first_full)

    coverage_frontier = []
    for rank in range(1, atom_count + 1):
        candidates = []
        for seed_atom_id in range(atom_count):
            atom_ids = entry_order[seed_atom_id, :rank].astype(np.int64).tolist()
            candidates.append(
                {
                    "ball_size": rank,
                    "seed_atom_id": seed_atom_id,
                    "seed_atom_label": atom_label(atlas, seed_atom_id),
                    "poincare_threshold": q(float(thresholds[seed_atom_id, rank - 1])),
                    "signature_class_count": int(coverage[seed_atom_id, rank - 1]),
                    "cumulative_tensor_path_coefficient_mass": int(mass[seed_atom_id, rank - 1]),
                    "atom_ids": atom_ids,
                    "atom_labels": [atom_label(atlas, atom_id) for atom_id in atom_ids],
                }
            )
        best = sorted(
            candidates,
            key=lambda row: (
                -int(row["signature_class_count"]),
                float(row["poincare_threshold"]),
                -int(row["cumulative_tensor_path_coefficient_mass"]),
                int(row["seed_atom_id"]),
            ),
        )[0]
        coverage_frontier.append(best)

    minimal_full = sorted(
        full_coverage_by_seed,
        key=lambda row: (
            int(row["ball_size"]),
            float(row["poincare_threshold"]),
            int(row["cumulative_tensor_path_coefficient_mass"]),
            int(row["seed_atom_id"]),
        ),
    )[0]
    minimum_size = int(minimal_full["ball_size"])
    smaller_max_coverage = max(
        int(coverage[seed_atom_id, rank - 1])
        for seed_atom_id in range(atom_count)
        for rank in range(1, minimum_size)
    )
    same_size_full_count = sum(
        1
        for row in full_coverage_by_seed
        if int(row["ball_size"]) == minimum_size
    )

    return {
        "filtration_records": records,
        "filtration_int_table": np.asarray(int_rows, dtype=np.int64),
        "entry_order": entry_order,
        "thresholds": thresholds,
        "novelty_matrix": novelty,
        "coverage_matrix": coverage,
        "mass_matrix": mass,
        "signature_count_sum_matrix": signature_count_sum,
        "full_coverage_by_seed": full_coverage_by_seed,
        "coverage_frontier": coverage_frontier,
        "minimal_full_coverage": minimal_full,
        "smaller_ball_max_signature_coverage": smaller_max_coverage,
        "minimum_size_full_coverage_ball_count": same_size_full_count,
        "total_tensor_path_coefficient_mass": int(masses.sum()),
    }


def landmark_ids_from_embedding(embedding: dict[str, Any]) -> list[int]:
    summary = embedding["landmark_summary"]
    landmark_ids = set(summary["top5_central_atom_ids"])
    landmark_ids.update(summary["top5_mass_atom_ids"])
    landmark_ids.update(summary["top5_signature_atom_ids"])
    landmark_ids.add(int(summary["lightest_atom"]["atom_id"]))
    landmark_ids.add(int(summary["heaviest_atom"]["atom_id"]))
    landmark_ids.add(int(summary["richest_signature_atom"]["atom_id"]))
    return sorted(int(atom_id) for atom_id in landmark_ids)


def build_payloads() -> dict[str, Any]:
    poincare_report = load_json(POINCARE_REPORT)
    poincare_embedding = load_json(POINCARE_JSON)
    atlas_report = load_json(ATLAS_REPORT)
    atlas = load_json(ATLAS_JSON)
    geometry_report = load_json(GEOMETRY_REPORT)
    atlas_npz = np.load(ATLAS_NPZ, allow_pickle=False)
    stored_class_ids = np.asarray(atlas_npz["relation_signature_class_ids"], dtype=np.int64)
    relation_npz = np.load(RELATION_GEOMETRY_SIGNATURES, allow_pickle=False)
    relation_records = np.asarray(relation_npz["relation_records"], dtype=np.int64)
    class_ids = signature_class_ids(relation_records)
    signature_sets = atom_signature_sets(atlas, relation_records, class_ids)
    class_count = len(set().union(*signature_sets))
    incidence = signature_incidence(signature_sets, class_count)

    poincare_npz = np.load(POINCARE_NPZ, allow_pickle=False)
    distances = np.asarray(poincare_npz["poincare_distances"], dtype=np.float64)
    filtration = build_filtration(atlas, distances, signature_sets)
    landmark_ids = landmark_ids_from_embedding(poincare_embedding)
    minimal_full = filtration["minimal_full_coverage"]
    full_by_seed = {
        int(row["seed_atom_id"]): row
        for row in filtration["full_coverage_by_seed"]
    }

    landmark_filtrations = [
        {
            "seed_atom_id": atom_id,
            "seed_atom_label": atom_label(atlas, atom_id),
            "full_coverage": full_by_seed[atom_id],
            "first_six_shells": [
                record
                for record in filtration["filtration_records"]
                if int(record["seed_atom_id"]) == atom_id and int(record["rank"]) <= 6
            ],
        }
        for atom_id in landmark_ids
    ]

    filtration_json = {
        "schema": "c985.d20_poincare_landmark_filtration@1",
        "object": "d20",
        "filtration_rule": {
            "metric": "Poincare geodesic distance from the certified d20 disk chart",
            "shell_order": "for each seed atom, add atoms by increasing Poincare distance with atom-id tie break",
            "signature_comparison": "each cumulative ball is compared with the 233 C985 relation-signature classes visible on d20 atom interiors",
        },
        "source_poincare_certificate": poincare_report.get("certificate_sha256"),
        "signature_class_count": class_count,
        "landmark_atom_ids": landmark_ids,
        "coverage_frontier_by_ball_size": filtration["coverage_frontier"],
        "minimal_full_coverage_ball": minimal_full,
        "minimum_size_full_coverage_ball_count": filtration["minimum_size_full_coverage_ball_count"],
        "smaller_ball_max_signature_coverage": filtration["smaller_ball_max_signature_coverage"],
        "landmark_filtrations": landmark_filtrations,
    }

    total_mass = int(filtration["total_tensor_path_coefficient_mass"])
    heaviest_atom = int(poincare_embedding["landmark_summary"]["heaviest_atom"]["atom_id"])
    richest_signature_atom = int(poincare_embedding["landmark_summary"]["richest_signature_atom"]["atom_id"])
    most_central_atom = int(poincare_embedding["landmark_summary"]["top5_central_atom_ids"][0])
    checks = {
        "poincare_report_certified": poincare_report.get("status")
        == "C985_D20_POINCARE_EMBEDDING_CERTIFIED",
        "boundary_atlas_report_certified": atlas_report.get("status")
        == "C985_D20_BOUNDARY_INVARIANT_ATLAS_CERTIFIED",
        "tensor_geometry_report_certified": geometry_report.get("status")
        == "C985_TENSOR_GEOMETRY_INVARIANTS_CERTIFIED",
        "atom_count_is_20": len(atlas["atom_rows"]) == 20,
        "poincare_distance_matrix_is_20_by_20": tuple(distances.shape) == (20, 20),
        "relation_signature_class_domain_is_233": class_count == 233,
        "stored_relation_signature_classes_match_recomputed": bool(np.array_equal(stored_class_ids, class_ids)),
        "atom_signature_counts_match_atlas": bool(
            all(
                len(signature_sets[atom_id])
                == int(atlas["atom_rows"][atom_id]["internal_signature_class_count"])
                for atom_id in range(20)
            )
        ),
        "signature_incidence_shape_is_20_by_233": tuple(incidence.shape) == (20, 233),
        "filtration_record_count_is_400": len(filtration["filtration_records"]) == 400,
        "coverage_matrix_shape_is_20_by_20": tuple(filtration["coverage_matrix"].shape) == (20, 20),
        "every_seed_reaches_full_signature_coverage": all(
            int(row["signature_class_count"]) == 233
            for row in filtration["full_coverage_by_seed"]
        ),
        "minimum_full_coverage_ball_size_is_7": int(minimal_full["ball_size"]) == 7,
        "no_ball_smaller_than_7_has_full_coverage": int(
            filtration["smaller_ball_max_signature_coverage"]
        )
        < 233,
        "minimum_full_coverage_seed_is_11": int(minimal_full["seed_atom_id"]) == 11,
        "minimum_full_coverage_radius_is_0_557922089": math.isclose(
            float(minimal_full["poincare_threshold"]),
            0.557922089,
            abs_tol=1e-10,
        ),
        "minimum_full_coverage_ball_count_at_size_7_is_2": int(
            filtration["minimum_size_full_coverage_ball_count"]
        )
        == 2,
        "minimum_full_coverage_ball_mass_is_below_half_total": int(
            minimal_full["cumulative_tensor_path_coefficient_mass"]
        )
        * 2
        < total_mass,
        "minimum_full_coverage_ball_contains_heaviest_atom": heaviest_atom
        in set(int(x) for x in minimal_full["atom_ids"]),
        "minimum_full_coverage_ball_contains_most_central_atom": most_central_atom
        in set(int(x) for x in minimal_full["atom_ids"]),
        "heaviest_seed_full_coverage_size_is_11": int(full_by_seed[heaviest_atom]["ball_size"]) == 11,
        "heaviest_seed_full_coverage_radius_is_0_5561031147": math.isclose(
            float(full_by_seed[heaviest_atom]["poincare_threshold"]),
            0.5561031147,
            abs_tol=1e-10,
        ),
        "richest_signature_seed_full_coverage_size_is_12": int(
            full_by_seed[richest_signature_atom]["ball_size"]
        )
        == 12,
        "heaviest_seed_first_five_covers_203_signature_classes": int(
            filtration["coverage_matrix"][heaviest_atom, 4]
        )
        == 203,
        "gateway_seed_first_seven_novelty_sums_to_233": int(
            filtration["novelty_matrix"][11, :7].sum()
        )
        == 233,
    }

    witness = {
        "atom_count": 20,
        "signature_class_count": class_count,
        "filtration_record_count": len(filtration["filtration_records"]),
        "landmark_atom_ids": landmark_ids,
        "minimum_full_coverage_seed": int(minimal_full["seed_atom_id"]),
        "minimum_full_coverage_seed_label": minimal_full["seed_atom_label"],
        "minimum_full_coverage_ball_size": int(minimal_full["ball_size"]),
        "minimum_full_coverage_threshold": q(float(minimal_full["poincare_threshold"])),
        "minimum_full_coverage_atom_ids": [int(x) for x in minimal_full["atom_ids"]],
        "minimum_full_coverage_mass": int(minimal_full["cumulative_tensor_path_coefficient_mass"]),
        "total_tensor_path_coefficient_mass": total_mass,
        "smaller_ball_max_signature_coverage": int(
            filtration["smaller_ball_max_signature_coverage"]
        ),
        "minimum_size_full_coverage_ball_count": int(
            filtration["minimum_size_full_coverage_ball_count"]
        ),
        "heaviest_seed": heaviest_atom,
        "heaviest_seed_full_coverage_ball_size": int(full_by_seed[heaviest_atom]["ball_size"]),
        "heaviest_seed_full_coverage_threshold": q(
            float(full_by_seed[heaviest_atom]["poincare_threshold"])
        ),
        "heaviest_seed_first_five_signature_coverage": int(
            filtration["coverage_matrix"][heaviest_atom, 4]
        ),
        "richest_signature_seed": richest_signature_atom,
        "richest_signature_seed_full_coverage_ball_size": int(
            full_by_seed[richest_signature_atom]["ball_size"]
        ),
        "signature_incidence_sha256": sha_array(incidence),
        "filtration_int_table_sha256": sha_array(filtration["filtration_int_table"]),
        "entry_order_sha256": sha_array(filtration["entry_order"]),
        "threshold_matrix_sha256": sha_quantized_float_array(filtration["thresholds"]),
        "coverage_matrix_sha256": sha_array(filtration["coverage_matrix"]),
        "novelty_matrix_sha256": sha_array(filtration["novelty_matrix"]),
        "mass_matrix_sha256": sha_array(filtration["mass_matrix"]),
    }

    certificate = {
        "schema": "c985.d20_poincare_landmark_filtration_certificate@1",
        "status": STATUS if all(checks.values()) else "C985_D20_POINCARE_LANDMARK_FILTRATION_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "Poincare geodesic balls give a deterministic filtration of the 20 d20 atoms",
            "the relation-signature domain visible through d20 has 233 classes",
            "no six-atom Poincare ball covers all relation-signature classes",
            "a seven-atom ball centered at atom 11 covers all 233 relation-signature classes",
            "the heaviest tensor-mass landmark reaches full relation-signature coverage in eleven atoms",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_poincare_landmark_filtration@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The certified d20 Poincare chart induces a landmark-centered geodesic "
            "filtration whose cumulative balls can be compared directly with the "
            "233 C985 relation-signature classes; the first full-coverage ball has "
            "seven atoms."
        ),
        "stage_protocol": {
            "draft": "start from the certified Poincare disk chart and relation-signature atlas",
            "witness": "materialize every seed atom's geodesic shell order and cumulative signature-class coverage",
            "coherence": "check signature incidence against atlas counts and prove the minimal full-coverage ball",
            "closure": "certify a filtration readout without claiming embedding optimality or packet normalization",
            "emit": "emit filtration JSON/CSV/NPZ, certificate, report, and next hyperbolic invariant target",
        },
        "inputs": {
            "poincare_report": input_entry(
                POINCARE_REPORT,
                {
                    "status": poincare_report.get("status"),
                    "certificate_sha256": poincare_report.get("certificate_sha256"),
                },
            ),
            "poincare_embedding": input_entry(POINCARE_JSON),
            "poincare_npz": input_entry(POINCARE_NPZ),
            "boundary_atlas_report": input_entry(
                ATLAS_REPORT,
                {
                    "status": atlas_report.get("status"),
                    "certificate_sha256": atlas_report.get("certificate_sha256"),
                },
            ),
            "boundary_atlas": input_entry(ATLAS_JSON),
            "boundary_atlas_npz": input_entry(ATLAS_NPZ),
            "tensor_geometry_report": input_entry(
                GEOMETRY_REPORT,
                {
                    "status": geometry_report.get("status"),
                    "certificate_sha256": geometry_report.get("certificate_sha256"),
                },
            ),
            "relation_geometry_signatures": input_entry(RELATION_GEOMETRY_SIGNATURES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "landmark_filtration": relpath(OUT_DIR / "landmark_filtration.json"),
            "filtration_records_csv": relpath(OUT_DIR / "filtration_records.csv"),
            "filtration_tables_npz": relpath(OUT_DIR / "filtration_tables.npz"),
            "filtration_certificate": relpath(OUT_DIR / "filtration_certificate.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "all 400 seed/rank Poincare geodesic filtration records",
                "20-by-233 atom-to-relation-signature incidence matrix",
                "coverage, novelty, mass, threshold, and entry-order matrices",
                "minimal full relation-signature coverage ball and its seed",
                "landmark full-coverage thresholds for central, mass, and signature seeds",
            ],
            "does_not_certify_because_not_required": [
                "optimality among non-Poincare embeddings",
                "a packet bridge from d20 atoms to A985/tube coordinates",
                "a packet normalization killing known boundary torsion",
                "pivotal, spherical, unitary, braiding, ribbon, or Drinfeld-center data",
            ],
        },
        "next_highest_yield_item": (
            "Use the full-coverage filtration balls as charts for a signature-class "
            "nerve, then measure whether its intersections recover the hyperbolic "
            "four-point witnesses."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_poincare_landmark_filtration_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load the certified Poincare embedding and relation-signature arrays",
            "reconstruct the 20-by-233 atom signature-incidence matrix",
            "sort every seed atom's Poincare geodesic shells deterministically",
            "verify cumulative relation-signature coverage and novelty matrices",
            "prove the minimal full-coverage ball size and seed",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "landmark_filtration": filtration_json,
        "filtration_records_csv": csv_text(FILTRATION_COLUMNS, filtration["filtration_records"]),
        "filtration_int_table": filtration["filtration_int_table"],
        "entry_order": filtration["entry_order"],
        "thresholds": filtration["thresholds"],
        "novelty_matrix": filtration["novelty_matrix"],
        "coverage_matrix": filtration["coverage_matrix"],
        "mass_matrix": filtration["mass_matrix"],
        "signature_count_sum_matrix": filtration["signature_count_sum_matrix"],
        "signature_incidence": incidence,
        "filtration_certificate": certificate,
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
    write_json(OUT_DIR / "landmark_filtration.json", payloads["landmark_filtration"])
    (OUT_DIR / "filtration_records.csv").write_text(
        payloads["filtration_records_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "filtration_tables.npz",
        filtration_int_table=payloads["filtration_int_table"],
        entry_order=payloads["entry_order"],
        thresholds=payloads["thresholds"],
        novelty_matrix=payloads["novelty_matrix"],
        coverage_matrix=payloads["coverage_matrix"],
        mass_matrix=payloads["mass_matrix"],
        signature_count_sum_matrix=payloads["signature_count_sum_matrix"],
        signature_incidence=payloads["signature_incidence"],
    )
    write_json(OUT_DIR / "filtration_certificate.json", payloads["filtration_certificate"])
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
                "minimum_full_coverage_seed": witness["minimum_full_coverage_seed"],
                "minimum_full_coverage_ball_size": witness["minimum_full_coverage_ball_size"],
                "minimum_full_coverage_threshold": witness["minimum_full_coverage_threshold"],
                "heaviest_seed_full_coverage_ball_size": witness[
                    "heaviest_seed_full_coverage_ball_size"
                ],
                "next_highest_yield_item": payloads["report"]["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
