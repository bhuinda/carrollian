from __future__ import annotations

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


THEOREM_ID = "c985_tensor_geometry_invariants"
STATUS = "C985_TENSOR_GEOMETRY_INVARIANTS_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

REGISTRY_DIR = D20_INVARIANTS / "proof_obligations" / "c985_typed_simple_object_registry"
FUSION_DIR = D20_INVARIANTS / "proof_obligations" / "c985_fusion_multiplicity_typing"
FINAL_DIR = D20_INVARIANTS / "proof_obligations" / "c985_final_multifusion_certificate"

REGISTRY_REPORT = REGISTRY_DIR / "report.json"
FUSION_REPORT = FUSION_DIR / "report.json"
FINAL_REPORT = FINAL_DIR / "report.json"
SOURCE_TARGET = REGISTRY_DIR / "source_target.npy"
TRANSPOSE = REGISTRY_DIR / "transpose.npy"
ORBITALS = REGISTRY_DIR / "orbitals.json"
FUSION_TENSOR = FUSION_DIR / "fusion_tensor_coo.npz"

DERIVE_SCRIPT = ROOT / "src" / "derive_c985_tensor_geometry_invariants.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_tensor_geometry_invariants.py"


def load_fusion_tensor() -> np.ndarray:
    return np.asarray(np.load(FUSION_TENSOR, allow_pickle=False)["triples"], dtype=np.int32)


def relation_sizes_from_orbitals() -> np.ndarray:
    orbitals = load_json(ORBITALS)
    rows = orbitals.get("orbitals", [])
    if not isinstance(rows, list):
        raise ValueError("orbitals.json does not contain an orbital list")
    sizes = np.zeros(len(rows), dtype=np.int64)
    for row in rows:
        relation_id = int(row["relation_id"])
        sizes[relation_id] = int(row["relation_size"])
    return sizes


def object_pair_matrix(source_target: np.ndarray) -> np.ndarray:
    matrix = np.zeros((len(OBJECT_LABELS), len(OBJECT_LABELS)), dtype=np.int64)
    for source, target in source_target:
        matrix[int(source), int(target)] += 1
    return matrix


def object_cubes(triples: np.ndarray, source_target: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    alpha = triples[:, 0]
    beta = triples[:, 1]
    coeff = triples[:, 3].astype(np.int64)
    source = source_target[alpha, 0].astype(np.int64)
    middle = source_target[alpha, 1].astype(np.int64)
    target = source_target[beta, 1].astype(np.int64)
    support = np.zeros((6, 6, 6), dtype=np.int64)
    mass = np.zeros((6, 6, 6), dtype=np.int64)
    np.add.at(support, (source, middle, target), 1)
    np.add.at(mass, (source, middle, target), coeff)
    return support, mass


def degree_records(
    triples: np.ndarray,
    source_target: np.ndarray,
    transpose: np.ndarray,
    relation_sizes: np.ndarray,
) -> np.ndarray:
    relation_count = int(source_target.shape[0])
    alpha = triples[:, 0]
    beta = triples[:, 1]
    gamma = triples[:, 2]
    coeff = triples[:, 3].astype(np.int64)

    left_support = np.bincount(alpha, minlength=relation_count).astype(np.int64)
    right_support = np.bincount(beta, minlength=relation_count).astype(np.int64)
    output_support = np.bincount(gamma, minlength=relation_count).astype(np.int64)
    left_mass = np.zeros(relation_count, dtype=np.int64)
    right_mass = np.zeros(relation_count, dtype=np.int64)
    output_mass = np.zeros(relation_count, dtype=np.int64)
    np.add.at(left_mass, alpha, coeff)
    np.add.at(right_mass, beta, coeff)
    np.add.at(output_mass, gamma, coeff)

    relation_ids = np.arange(relation_count, dtype=np.int64)
    return np.column_stack(
        [
            relation_ids,
            source_target[:, 0].astype(np.int64),
            source_target[:, 1].astype(np.int64),
            transpose.astype(np.int64),
            (transpose == relation_ids).astype(np.int64),
            relation_sizes.astype(np.int64),
            left_support,
            right_support,
            output_support,
            left_mass,
            right_mass,
            output_mass,
        ]
    ).astype(np.int64)


def sorted_rows(rows: np.ndarray) -> np.ndarray:
    order = np.lexsort((rows[:, 2], rows[:, 1], rows[:, 0]))
    return rows[order]


def transpose_symmetry_failures(triples: np.ndarray, transpose: np.ndarray) -> int:
    dual = np.column_stack(
        [
            transpose[triples[:, 1]],
            transpose[triples[:, 0]],
            transpose[triples[:, 2]],
            triples[:, 3],
        ]
    ).astype(np.int32)
    left = sorted_rows(triples)
    right = sorted_rows(dual)
    if left.shape != right.shape:
        return max(int(left.shape[0]), int(right.shape[0]))
    return int(np.count_nonzero(np.any(left != right, axis=1)))


def coefficient_histogram(triples: np.ndarray) -> list[dict[str, int]]:
    values, counts = np.unique(triples[:, 3], return_counts=True)
    return [
        {"coefficient": int(value), "support_rows": int(count)}
        for value, count in zip(values, counts, strict=True)
    ]


def tensor_row_samples(triples: np.ndarray, source_target: np.ndarray, limit: int = 32) -> list[dict[str, Any]]:
    order = np.lexsort((triples[:, 2], triples[:, 1], triples[:, 0], -triples[:, 3]))
    samples: list[dict[str, Any]] = []
    for idx in order[:limit]:
        alpha, beta, gamma, coeff = [int(x) for x in triples[int(idx)]]
        source = int(source_target[alpha, 0])
        middle = int(source_target[alpha, 1])
        target = int(source_target[beta, 1])
        samples.append(
            {
                "alpha": alpha,
                "beta": beta,
                "gamma": gamma,
                "coefficient": coeff,
                "object_path": [OBJECT_LABELS[source], OBJECT_LABELS[middle], OBJECT_LABELS[target]],
            }
        )
    return samples


def relation_samples(records: np.ndarray, metric_column: int, *, reverse: bool, limit: int = 16) -> list[dict[str, Any]]:
    key = (lambda row: (-int(row[metric_column]), int(row[0]))) if reverse else (lambda row: (int(row[metric_column]), int(row[0])))
    ordered = sorted(records.tolist(), key=key)
    samples: list[dict[str, Any]] = []
    for row in ordered[:limit]:
        samples.append(
            {
                "relation_id": int(row[0]),
                "source": OBJECT_LABELS[int(row[1])],
                "target": OBJECT_LABELS[int(row[2])],
                "transpose_relation": int(row[3]),
                "self_transpose": bool(row[4]),
                "relation_size": int(row[5]),
                "left_support_degree": int(row[6]),
                "right_support_degree": int(row[7]),
                "output_support_degree": int(row[8]),
                "left_coefficient_mass": int(row[9]),
                "right_coefficient_mass": int(row[10]),
                "output_coefficient_mass": int(row[11]),
            }
        )
    return samples


def sector_entries(support_cube: np.ndarray, mass_cube: np.ndarray) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for source in range(6):
        for middle in range(6):
            for target in range(6):
                support = int(support_cube[source, middle, target])
                mass = int(mass_cube[source, middle, target])
                entries.append(
                    {
                        "object_path": [
                            OBJECT_LABELS[source],
                            OBJECT_LABELS[middle],
                            OBJECT_LABELS[target],
                        ],
                        "support_rows": support,
                        "coefficient_mass": mass,
                        "mean_coefficient_fraction": [mass, support] if support else [0, 1],
                    }
                )
    return entries


def sector_extrema(support_cube: np.ndarray, mass_cube: np.ndarray, *, metric: str) -> list[dict[str, Any]]:
    entries = sector_entries(support_cube, mass_cube)
    metric_key = "support_rows" if metric == "support" else "coefficient_mass"
    return sorted(entries, key=lambda row: (-int(row[metric_key]), row["object_path"]))[:12]


def signature_classes(records: np.ndarray) -> tuple[np.ndarray, list[dict[str, Any]]]:
    signature = records[:, [1, 2, 4, 5, 6, 7, 8, 9, 10, 11]].astype(np.int64)
    unique, inverse, counts = np.unique(signature, axis=0, return_inverse=True, return_counts=True)
    ordered_class_ids = sorted(range(unique.shape[0]), key=lambda idx: (-int(counts[idx]), unique[idx].tolist()))
    classes: list[dict[str, Any]] = []
    for class_id in ordered_class_ids[:24]:
        relation_ids = np.flatnonzero(inverse == class_id)[:12].astype(int).tolist()
        row = unique[class_id].astype(int).tolist()
        classes.append(
            {
                "class_size": int(counts[class_id]),
                "signature": {
                    "source": OBJECT_LABELS[row[0]],
                    "target": OBJECT_LABELS[row[1]],
                    "self_transpose": bool(row[2]),
                    "relation_size": row[3],
                    "left_support_degree": row[4],
                    "right_support_degree": row[5],
                    "output_support_degree": row[6],
                    "left_coefficient_mass": row[7],
                    "right_coefficient_mass": row[8],
                    "output_coefficient_mass": row[9],
                },
                "sample_relation_ids": relation_ids,
            }
        )
    return unique, classes


def build_payloads() -> dict[str, Any]:
    registry_report = load_json(REGISTRY_REPORT)
    fusion_report = load_json(FUSION_REPORT)
    final_report = load_json(FINAL_REPORT)
    source_target = np.asarray(np.load(SOURCE_TARGET, allow_pickle=False), dtype=np.int16)
    transpose = np.asarray(np.load(TRANSPOSE, allow_pickle=False), dtype=np.int32)
    relation_sizes = relation_sizes_from_orbitals()
    triples = load_fusion_tensor()

    support_cube, mass_cube = object_cubes(triples, source_target)
    records = degree_records(triples, source_target, transpose, relation_sizes)
    signature_matrix, largest_signature_classes = signature_classes(records)
    hist = coefficient_histogram(triples)
    transpose_failures = transpose_symmetry_failures(triples, transpose)
    relation_count_matrix = object_pair_matrix(source_target)
    coefficient_histogram_support_total = sum(row["support_rows"] for row in hist)
    coefficient_histogram_mass_total = sum(row["coefficient"] * row["support_rows"] for row in hist)

    output_mass = records[:, 11]
    checks = {
        "registry_certified": registry_report.get("status") == "C985_TYPED_SIMPLE_OBJECT_REGISTRY_CERTIFIED",
        "fusion_certified": fusion_report.get("status") == "C985_FUSION_MULTIPLICITY_TYPING_CERTIFIED",
        "final_c985_certificate_present": final_report.get("status")
        == "C985_FINITE_SEMISIMPLE_MULTIFUSION_CATEGORY_CERTIFIED",
        "source_target_shape_is_985_by_2": tuple(source_target.shape) == (985, 2),
        "fusion_tensor_shape_is_1414965_by_4": tuple(triples.shape) == (1414965, 4),
        "fusion_coefficient_total_is_2537360": int(triples[:, 3].sum()) == 2537360,
        "object_sector_support_cube_has_all_216_cells": int(np.count_nonzero(support_cube)) == 216,
        "support_cube_sum_matches_tensor_support": int(support_cube.sum()) == int(triples.shape[0]),
        "coefficient_cube_sum_matches_tensor_mass": int(mass_cube.sum()) == int(triples[:, 3].sum()),
        "relation_geometry_records_shape_is_985_by_12": tuple(records.shape) == (985, 12),
        "every_output_relation_has_point_mass_2576": bool(np.all(output_mass == 2576)),
        "transpose_symmetry_failure_count_is_zero": transpose_failures == 0,
        "transpose_preserves_relation_size": bool(np.array_equal(relation_sizes[transpose], relation_sizes)),
        "left_support_matches_right_support_under_transpose": bool(np.array_equal(records[:, 6], records[transpose, 7])),
        "left_mass_matches_right_mass_under_transpose": bool(np.array_equal(records[:, 9], records[transpose, 10])),
        "output_support_matches_transpose_output_support": bool(np.array_equal(records[:, 8], records[transpose, 8])),
        "histogram_support_total_matches_tensor_support": coefficient_histogram_support_total == int(triples.shape[0]),
        "histogram_mass_total_matches_tensor_mass": coefficient_histogram_mass_total == int(triples[:, 3].sum()),
    }

    summary = {
        "schema": "c985.tensor_geometry_summary@1",
        "interpretation": {
            "object_sector_cube": (
                "Rows are aggregated by typed object path source -> middle -> target; "
                "all 216 paths are populated, so the tensor is geometrically live across "
                "the full six-sector cube."
            ),
            "output_mass_balance": (
                "For every output simple gamma, sum_{alpha,beta} p_{alpha,beta}^{gamma} "
                "is exactly 2576, the point count in the relation model."
            ),
            "transpose_symmetry": (
                "The tensor is invariant under (alpha,beta,gamma) -> "
                "(beta^vee, alpha^vee, gamma^vee) with the same coefficient."
            ),
        },
        "object_labels": OBJECT_LABELS,
        "object_pair_relation_matrix": relation_count_matrix.astype(int).tolist(),
        "object_sector_entries": sector_entries(support_cube, mass_cube),
        "top_object_paths_by_support": sector_extrema(support_cube, mass_cube, metric="support"),
        "top_object_paths_by_coefficient_mass": sector_extrema(support_cube, mass_cube, metric="mass"),
        "coefficient_histogram": hist,
        "max_coefficient_rows": tensor_row_samples(triples, source_target),
        "degree_extrema": {
            "top_left_support": relation_samples(records, 6, reverse=True),
            "top_right_support": relation_samples(records, 7, reverse=True),
            "top_output_support": relation_samples(records, 8, reverse=True),
            "bottom_output_support": relation_samples(records, 8, reverse=False),
        },
        "signature_columns": [
            "source_object",
            "target_object",
            "self_transpose",
            "relation_size",
            "left_support_degree",
            "right_support_degree",
            "output_support_degree",
            "left_coefficient_mass",
            "right_coefficient_mass",
            "output_coefficient_mass",
        ],
        "unique_signature_count": int(signature_matrix.shape[0]),
        "largest_signature_classes": largest_signature_classes,
    }

    witness = {
        "relation_count": 985,
        "object_count": 6,
        "tensor_support": int(triples.shape[0]),
        "coefficient_total": int(triples[:, 3].sum()),
        "coefficient_min": int(triples[:, 3].min()),
        "coefficient_max": int(triples[:, 3].max()),
        "coefficient_value_count": len(hist),
        "object_sector_nonzero_cells": int(np.count_nonzero(support_cube)),
        "object_sector_support_min": int(support_cube.min()),
        "object_sector_support_max": int(support_cube.max()),
        "object_sector_mass_min": int(mass_cube.min()),
        "object_sector_mass_max": int(mass_cube.max()),
        "self_transpose_relation_count": int(records[:, 4].sum()),
        "unique_relation_signature_count": int(signature_matrix.shape[0]),
        "output_coefficient_mass_min": int(output_mass.min()),
        "output_coefficient_mass_max": int(output_mass.max()),
        "transpose_symmetry_failure_count": transpose_failures,
        "object_sector_cubes_sha256": sha_array(np.stack([support_cube, mass_cube])),
        "relation_geometry_records_sha256": sha_array(records),
        "relation_signature_matrix_sha256": sha_array(signature_matrix),
    }

    geometry_certificate = {
        "schema": "c985.tensor_geometry_invariants_certificate@1",
        "status": STATUS if all(checks.values()) else "C985_TENSOR_GEOMETRY_INVARIANTS_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the tensor has full six-object sector-cube support",
            "every output simple carries the same total coefficient mass 2576",
            "left and right tensor degrees are paired exactly by transpose duality",
            "the sparse coefficient spectrum and extremal rows are reproducible",
            "985 relation-level geometric signatures are materialized for invariant search",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.tensor_geometry_invariants@1",
        "status": geometry_certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The certified C985 fusion tensor has reproducible geometric readouts: full "
            "six-sector object-cube support, constant output mass 2576, exact transpose "
            "symmetry, coefficient strata, and relation-level degree signatures."
        ),
        "stage_protocol": {
            "draft": "mine the certified C985 sparse fusion tensor for geometry-oriented invariants",
            "witness": "materialize object-sector cubes, relation degree signatures, coefficient strata, and extremal rows",
            "coherence": "check tensor totals, transpose symmetry, output mass balance, and signature reproducibility",
            "closure": "certify the invariant-discovery readout layer without adding optional categorical structure",
            "emit": "emit a compact geometry summary and NPZ tables for downstream visualization/search",
        },
        "inputs": {
            "typed_registry_report": input_entry(
                REGISTRY_REPORT,
                {
                    "status": registry_report.get("status"),
                    "certificate_sha256": registry_report.get("certificate_sha256"),
                },
            ),
            "fusion_report": input_entry(
                FUSION_REPORT,
                {
                    "status": fusion_report.get("status"),
                    "certificate_sha256": fusion_report.get("certificate_sha256"),
                },
            ),
            "final_c985_report": input_entry(
                FINAL_REPORT,
                {
                    "status": final_report.get("status"),
                    "certificate_sha256": final_report.get("certificate_sha256"),
                },
            ),
            "source_target": input_entry(SOURCE_TARGET),
            "transpose": input_entry(TRANSPOSE),
            "orbitals": input_entry(ORBITALS),
            "fusion_tensor": input_entry(FUSION_TENSOR),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "object_sector_cubes": relpath(OUT_DIR / "object_sector_cubes.npz"),
            "relation_geometry_signatures": relpath(OUT_DIR / "relation_geometry_signatures.npz"),
            "tensor_geometry_summary": relpath(OUT_DIR / "tensor_geometry_summary.json"),
            "geometry_certificate": relpath(OUT_DIR / "geometry_certificate.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "object-sector cube aggregation of the C985 fusion tensor",
                "relation-level tensor degree and coefficient-mass signatures",
                "constant output coefficient mass across all 985 simple outputs",
                "exact transpose-dual symmetry of the sparse tensor",
                "coefficient spectrum and extremal tensor-row witnesses for invariant discovery",
            ],
            "does_not_certify_because_not_required": [
                "new categorical coherence beyond the existing C985 final certificate",
                "pivotal or spherical normalization",
                "unitarity",
                "braiding or ribbon data",
                "Drinfeld-center modular data",
            ],
        },
        "next_highest_yield_item": (
            "Use relation_geometry_signatures.npz to choose geometric landmarks and "
            "project them onto the d20 boundary/readout as a navigable invariant atlas."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.tensor_geometry_invariants_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load the certified C985 tensor and typed registry",
            "aggregate tensor support and coefficient mass over the 6x6x6 object-sector cube",
            "materialize relation-level support and coefficient-mass signatures",
            "verify constant output coefficient mass 2576 for every simple output",
            "verify exact transpose-dual tensor symmetry",
            "verify coefficient histogram totals and NPZ/JSON reproducibility",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "object_support_cube": support_cube,
        "object_coefficient_cube": mass_cube,
        "relation_geometry_records": records,
        "relation_signature_matrix": signature_matrix,
        "tensor_geometry_summary": summary,
        "geometry_certificate": geometry_certificate,
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
    np.savez_compressed(
        OUT_DIR / "object_sector_cubes.npz",
        support_cube=payloads["object_support_cube"],
        coefficient_cube=payloads["object_coefficient_cube"],
    )
    np.savez_compressed(
        OUT_DIR / "relation_geometry_signatures.npz",
        relation_records=payloads["relation_geometry_records"],
        signature_matrix=payloads["relation_signature_matrix"],
    )
    write_json(OUT_DIR / "tensor_geometry_summary.json", payloads["tensor_geometry_summary"])
    write_json(OUT_DIR / "geometry_certificate.json", payloads["geometry_certificate"])
    write_json(OUT_DIR / "report.json", payloads["report"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    update_index(payloads["report"])


def main() -> None:
    payloads = build_payloads()
    write_payloads(payloads)
    print(
        json.dumps(
            {
                "status": payloads["report"]["status"],
                "all_checks_pass": payloads["report"]["all_checks_pass"],
                "report": relpath(OUT_DIR / "report.json"),
                "manifest": relpath(OUT_DIR / "manifest.json"),
                "certificate_sha256": payloads["report"]["certificate_sha256"],
                "object_sector_nonzero_cells": payloads["report"]["witness"]["object_sector_nonzero_cells"],
                "output_coefficient_mass": payloads["report"]["witness"]["output_coefficient_mass_min"],
                "transpose_symmetry_failure_count": payloads["report"]["witness"][
                    "transpose_symmetry_failure_count"
                ],
                "unique_relation_signature_count": payloads["report"]["witness"][
                    "unique_relation_signature_count"
                ],
                "next_highest_yield_item": payloads["report"]["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
