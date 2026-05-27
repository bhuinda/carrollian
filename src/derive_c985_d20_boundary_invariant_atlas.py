from __future__ import annotations

import csv
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


THEOREM_ID = "c985_d20_boundary_invariant_atlas"
STATUS = "C985_D20_BOUNDARY_INVARIANT_ATLAS_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

GEOMETRY_DIR = D20_INVARIANTS / "proof_obligations" / "c985_tensor_geometry_invariants"
GEOMETRY_REPORT = GEOMETRY_DIR / "report.json"
OBJECT_SECTOR_CUBES = GEOMETRY_DIR / "object_sector_cubes.npz"
RELATION_GEOMETRY_SIGNATURES = GEOMETRY_DIR / "relation_geometry_signatures.npz"
TENSOR_GEOMETRY_SUMMARY = GEOMETRY_DIR / "tensor_geometry_summary.json"

TINY_POINTER_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_sector_label_alias_registry"
TINY_POINTER_REPORT = TINY_POINTER_DIR / "report.json"
D20_ATOM_DOMAIN_CSV = TINY_POINTER_DIR / "d20_atom_domain.csv"
TINY_POINTER_SCHEMA = TINY_POINTER_DIR / "tiny_pointer_d20_atom_primitive_schema.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_c985_d20_boundary_invariant_atlas.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_d20_boundary_invariant_atlas.py"


ATLAS_COLUMNS = [
    "atom_id",
    "atom_label",
    "h6_triple",
    "complement_atom_id",
    "ordered_distinct_path_count",
    "tensor_path_support",
    "tensor_path_coefficient_mass",
    "internal_relation_count",
    "internal_signature_class_count",
    "self_transpose_relation_count",
    "relation_size_total",
    "left_support_degree_total",
    "right_support_degree_total",
    "output_support_degree_total",
    "left_coefficient_mass_total",
    "right_coefficient_mass_total",
    "output_coefficient_mass_total",
]


def load_atom_domain() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with D20_ATOM_DOMAIN_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            triple_labels = row["h6_triple"].split("|")
            triple_ids = [OBJECT_LABELS.index(label) for label in triple_labels]
            rows.append(
                {
                    "atom_id": int(row["atom_id"]),
                    "atom_label": row["atom_label"],
                    "h6_triple": triple_labels,
                    "h6_triple_ids": triple_ids,
                    "native_domain": row["native_domain"],
                }
            )
    return rows


def atom_domain_csv_text(rows: list[dict[str, Any]]) -> str:
    out = [",".join(["atom_id", "atom_label", "h6_triple", "native_domain"])]
    for row in rows:
        out.append(
            ",".join(
                [
                    str(row["atom_id"]),
                    row["atom_label"],
                    "|".join(row["h6_triple"]),
                    row["native_domain"],
                ]
            )
        )
    return "\n".join(out) + "\n"


def atlas_csv_text(rows: list[dict[str, Any]]) -> str:
    out = [",".join(ATLAS_COLUMNS)]
    for row in rows:
        out.append(
            ",".join(
                [
                    str(row[column]) if column != "h6_triple" else "|".join(row[column])
                    for column in ATLAS_COLUMNS
                ]
            )
        )
    return "\n".join(out) + "\n"


def relation_signature_class_ids(records: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    signature = records[:, [1, 2, 4, 5, 6, 7, 8, 9, 10, 11]].astype(np.int64)
    unique, inverse = np.unique(signature, axis=0, return_inverse=True)
    return unique.astype(np.int64), inverse.astype(np.int64)


def complement_map(atom_rows: list[dict[str, Any]]) -> dict[int, int]:
    by_set = {frozenset(row["h6_triple_ids"]): int(row["atom_id"]) for row in atom_rows}
    all_ids = frozenset(range(len(OBJECT_LABELS)))
    return {
        int(row["atom_id"]): by_set[all_ids.difference(row["h6_triple_ids"])]
        for row in atom_rows
    }


def atom_relation_mask(records: np.ndarray, triple_ids: list[int]) -> np.ndarray:
    members = np.zeros(len(OBJECT_LABELS), dtype=bool)
    members[np.asarray(triple_ids, dtype=np.int64)] = True
    return members[records[:, 1]] & members[records[:, 2]]


def path_indices(triple_ids: list[int]) -> list[tuple[int, int, int]]:
    return list(itertools.permutations(triple_ids, 3))


def top_relation_samples(
    records: np.ndarray,
    class_ids: np.ndarray,
    mask: np.ndarray,
    *,
    limit: int = 8,
) -> list[dict[str, Any]]:
    subset = records[mask]
    subset_classes = class_ids[mask]
    order = sorted(
        range(subset.shape[0]),
        key=lambda idx: (-int(subset[idx, 8]), -int(subset[idx, 11]), int(subset[idx, 0])),
    )
    samples: list[dict[str, Any]] = []
    for idx in order[:limit]:
        row = subset[idx]
        samples.append(
            {
                "relation_id": int(row[0]),
                "source": OBJECT_LABELS[int(row[1])],
                "target": OBJECT_LABELS[int(row[2])],
                "signature_class_id": int(subset_classes[idx]),
                "self_transpose": bool(row[4]),
                "relation_size": int(row[5]),
                "output_support_degree": int(row[8]),
                "output_coefficient_mass": int(row[11]),
            }
        )
    return samples


def build_atom_rows(
    atom_domain: list[dict[str, Any]],
    support_cube: np.ndarray,
    coefficient_cube: np.ndarray,
    relation_records: np.ndarray,
    class_ids: np.ndarray,
) -> tuple[list[dict[str, Any]], np.ndarray]:
    complements = complement_map(atom_domain)
    numeric = np.zeros((len(atom_domain), len(ATLAS_COLUMNS) - 2), dtype=np.int64)
    rows: list[dict[str, Any]] = []
    for atom in atom_domain:
        atom_id = int(atom["atom_id"])
        paths = path_indices(atom["h6_triple_ids"])
        tensor_support = int(sum(int(support_cube[path]) for path in paths))
        tensor_mass = int(sum(int(coefficient_cube[path]) for path in paths))
        mask = atom_relation_mask(relation_records, atom["h6_triple_ids"])
        atom_records = relation_records[mask]
        signature_classes = np.unique(class_ids[mask])
        row = {
            "atom_id": atom_id,
            "atom_label": atom["atom_label"],
            "h6_triple": atom["h6_triple"],
            "complement_atom_id": complements[atom_id],
            "ordered_distinct_path_count": len(paths),
            "tensor_path_support": tensor_support,
            "tensor_path_coefficient_mass": tensor_mass,
            "internal_relation_count": int(mask.sum()),
            "internal_signature_class_count": int(signature_classes.size),
            "self_transpose_relation_count": int(atom_records[:, 4].sum()) if atom_records.size else 0,
            "relation_size_total": int(atom_records[:, 5].sum()) if atom_records.size else 0,
            "left_support_degree_total": int(atom_records[:, 6].sum()) if atom_records.size else 0,
            "right_support_degree_total": int(atom_records[:, 7].sum()) if atom_records.size else 0,
            "output_support_degree_total": int(atom_records[:, 8].sum()) if atom_records.size else 0,
            "left_coefficient_mass_total": int(atom_records[:, 9].sum()) if atom_records.size else 0,
            "right_coefficient_mass_total": int(atom_records[:, 10].sum()) if atom_records.size else 0,
            "output_coefficient_mass_total": int(atom_records[:, 11].sum()) if atom_records.size else 0,
            "top_internal_relation_landmarks": top_relation_samples(relation_records, class_ids, mask),
        }
        rows.append(row)
        numeric[atom_id] = np.asarray(
            [
                row["atom_id"],
                row["complement_atom_id"],
                row["ordered_distinct_path_count"],
                row["tensor_path_support"],
                row["tensor_path_coefficient_mass"],
                row["internal_relation_count"],
                row["internal_signature_class_count"],
                row["self_transpose_relation_count"],
                row["relation_size_total"],
                row["left_support_degree_total"],
                row["right_support_degree_total"],
                row["output_support_degree_total"],
                row["left_coefficient_mass_total"],
                row["right_coefficient_mass_total"],
                row["output_coefficient_mass_total"],
            ],
            dtype=np.int64,
        )
    return rows, numeric


def distinct_path_totals(support_cube: np.ndarray, coefficient_cube: np.ndarray) -> dict[str, int]:
    distinct_support = 0
    distinct_mass = 0
    degenerate_support = 0
    degenerate_mass = 0
    for path in itertools.product(range(len(OBJECT_LABELS)), repeat=3):
        if len(set(path)) == 3:
            distinct_support += int(support_cube[path])
            distinct_mass += int(coefficient_cube[path])
        else:
            degenerate_support += int(support_cube[path])
            degenerate_mass += int(coefficient_cube[path])
    return {
        "distinct_object_path_support": distinct_support,
        "distinct_object_path_coefficient_mass": distinct_mass,
        "degenerate_object_path_support": degenerate_support,
        "degenerate_object_path_coefficient_mass": degenerate_mass,
    }


def relation_atom_incidence_expected(records: np.ndarray) -> int:
    source = records[:, 1]
    target = records[:, 2]
    return int(np.where(source == target, 10, 4).sum())


def complement_pair_rows(atom_rows: list[dict[str, Any]]) -> list[dict[str, int]]:
    by_id = {int(row["atom_id"]): row for row in atom_rows}
    pairs: list[dict[str, int]] = []
    seen: set[int] = set()
    for atom_id, row in by_id.items():
        complement_id = int(row["complement_atom_id"])
        if atom_id in seen or complement_id in seen:
            continue
        other = by_id[complement_id]
        pairs.append(
            {
                "atom_id": atom_id,
                "complement_atom_id": complement_id,
                "tensor_path_support_sum": int(row["tensor_path_support"])
                + int(other["tensor_path_support"]),
                "tensor_path_coefficient_mass_sum": int(row["tensor_path_coefficient_mass"])
                + int(other["tensor_path_coefficient_mass"]),
                "support_delta_abs": abs(int(row["tensor_path_support"]) - int(other["tensor_path_support"])),
                "mass_delta_abs": abs(
                    int(row["tensor_path_coefficient_mass"])
                    - int(other["tensor_path_coefficient_mass"])
                ),
            }
        )
        seen.add(atom_id)
        seen.add(complement_id)
    return sorted(pairs, key=lambda row: (row["atom_id"], row["complement_atom_id"]))


def build_payloads() -> dict[str, Any]:
    geometry_report = load_json(GEOMETRY_REPORT)
    tiny_pointer_report = load_json(TINY_POINTER_REPORT)
    tensor_summary = load_json(TENSOR_GEOMETRY_SUMMARY)
    atom_domain = load_atom_domain()

    cubes = np.load(OBJECT_SECTOR_CUBES, allow_pickle=False)
    support_cube = np.asarray(cubes["support_cube"], dtype=np.int64)
    coefficient_cube = np.asarray(cubes["coefficient_cube"], dtype=np.int64)
    signatures = np.load(RELATION_GEOMETRY_SIGNATURES, allow_pickle=False)
    relation_records = np.asarray(signatures["relation_records"], dtype=np.int64)
    signature_matrix = np.asarray(signatures["signature_matrix"], dtype=np.int64)
    recomputed_signature_matrix, class_ids = relation_signature_class_ids(relation_records)

    atom_rows, atom_numeric = build_atom_rows(
        atom_domain,
        support_cube,
        coefficient_cube,
        relation_records,
        class_ids,
    )
    path_totals = distinct_path_totals(support_cube, coefficient_cube)
    complement_pairs = complement_pair_rows(atom_rows)
    atom_support_total = int(sum(row["tensor_path_support"] for row in atom_rows))
    atom_mass_total = int(sum(row["tensor_path_coefficient_mass"] for row in atom_rows))
    atom_relation_incidence_total = int(sum(row["internal_relation_count"] for row in atom_rows))
    all_signature_classes_seen = sorted(
        {
            int(class_id)
            for row in atom_domain
            for class_id in np.unique(class_ids[atom_relation_mask(relation_records, row["h6_triple_ids"])])
        }
    )

    atom_domain_sets = {tuple(row["h6_triple_ids"]) for row in atom_domain}
    expected_sets = set(itertools.combinations(range(len(OBJECT_LABELS)), 3))
    checks = {
        "tensor_geometry_report_certified": geometry_report.get("status")
        == "C985_TENSOR_GEOMETRY_INVARIANTS_CERTIFIED",
        "tiny_pointer_atom_domain_certified": tiny_pointer_report.get("status")
        == "D20_TINY_POINTER_A985_SECTOR_LABEL_ALIAS_REGISTRY_CERTIFIED",
        "atom_domain_has_20_rows": len(atom_domain) == 20,
        "atom_domain_is_c_h6_3": atom_domain_sets == expected_sets,
        "atom_ids_are_contiguous": [row["atom_id"] for row in atom_domain] == list(range(20)),
        "object_sector_cube_shape_is_6_by_6_by_6": tuple(support_cube.shape) == (6, 6, 6)
        and tuple(coefficient_cube.shape) == (6, 6, 6),
        "relation_records_shape_is_985_by_12": tuple(relation_records.shape) == (985, 12),
        "signature_matrix_reproducible": bool(np.array_equal(signature_matrix, recomputed_signature_matrix)),
        "ordered_distinct_path_count_is_6_per_atom": all(
            row["ordered_distinct_path_count"] == 6 for row in atom_rows
        ),
        "atom_distinct_path_support_sums_match_cube": atom_support_total
        == path_totals["distinct_object_path_support"],
        "atom_distinct_path_mass_sums_match_cube": atom_mass_total
        == path_totals["distinct_object_path_coefficient_mass"],
        "degenerate_and_distinct_support_partition_tensor": (
            path_totals["distinct_object_path_support"]
            + path_totals["degenerate_object_path_support"]
            == int(support_cube.sum())
        ),
        "degenerate_and_distinct_mass_partition_tensor": (
            path_totals["distinct_object_path_coefficient_mass"]
            + path_totals["degenerate_object_path_coefficient_mass"]
            == int(coefficient_cube.sum())
        ),
        "relation_atom_incidence_total_matches_source_target_formula": atom_relation_incidence_total
        == relation_atom_incidence_expected(relation_records),
        "all_relation_signature_classes_seen_by_atoms": len(all_signature_classes_seen)
        == int(signature_matrix.shape[0]),
        "all_atoms_have_positive_tensor_support": all(row["tensor_path_support"] > 0 for row in atom_rows),
        "all_atoms_have_positive_internal_relation_count": all(
            row["internal_relation_count"] > 0 for row in atom_rows
        ),
        "complement_pair_count_is_10": len(complement_pairs) == 10,
    }

    top_atoms_by_mass = sorted(
        atom_rows,
        key=lambda row: (-int(row["tensor_path_coefficient_mass"]), -int(row["tensor_path_support"]), int(row["atom_id"])),
    )[:8]
    top_atoms_by_signature_classes = sorted(
        atom_rows,
        key=lambda row: (-int(row["internal_signature_class_count"]), -int(row["internal_relation_count"]), int(row["atom_id"])),
    )[:8]

    atlas = {
        "schema": "c985.d20_boundary_invariant_atlas@1",
        "object": "d20",
        "projection_rule": {
            "atom_domain": "C(H6,3)",
            "tensor_path_rule": (
                "For each d20 atom {a,b,c}, aggregate the six ordered C985 object-sector "
                "paths that are permutations of a -> b -> c."
            ),
            "relation_signature_rule": (
                "Attach every C985 relation signature whose source and target sectors both "
                "lie in the d20 atom triple."
            ),
            "degenerate_paths": (
                "Object paths with repeated sectors are recorded as tensor mass outside the "
                "Lambda^3 H6 boundary projection."
            ),
        },
        "object_labels": OBJECT_LABELS,
        "atom_rows": atom_rows,
        "complement_pairs": complement_pairs,
        "summary": {
            "atom_count": len(atom_rows),
            "ordered_distinct_paths_per_atom": 6,
            "distinct_object_path_support": path_totals["distinct_object_path_support"],
            "distinct_object_path_coefficient_mass": path_totals[
                "distinct_object_path_coefficient_mass"
            ],
            "degenerate_object_path_support": path_totals["degenerate_object_path_support"],
            "degenerate_object_path_coefficient_mass": path_totals[
                "degenerate_object_path_coefficient_mass"
            ],
            "relation_atom_incidence_total": atom_relation_incidence_total,
            "unique_signature_classes_seen": len(all_signature_classes_seen),
            "top_atoms_by_tensor_mass": [
                {
                    "atom_id": int(row["atom_id"]),
                    "h6_triple": row["h6_triple"],
                    "tensor_path_support": int(row["tensor_path_support"]),
                    "tensor_path_coefficient_mass": int(row["tensor_path_coefficient_mass"]),
                    "internal_signature_class_count": int(row["internal_signature_class_count"]),
                }
                for row in top_atoms_by_mass
            ],
            "top_atoms_by_signature_classes": [
                {
                    "atom_id": int(row["atom_id"]),
                    "h6_triple": row["h6_triple"],
                    "internal_relation_count": int(row["internal_relation_count"]),
                    "internal_signature_class_count": int(row["internal_signature_class_count"]),
                    "tensor_path_coefficient_mass": int(row["tensor_path_coefficient_mass"]),
                }
                for row in top_atoms_by_signature_classes
            ],
        },
    }

    witness = {
        "atom_count": len(atom_rows),
        "relation_count": int(relation_records.shape[0]),
        "signature_class_count": int(signature_matrix.shape[0]),
        "distinct_object_path_support": path_totals["distinct_object_path_support"],
        "distinct_object_path_coefficient_mass": path_totals[
            "distinct_object_path_coefficient_mass"
        ],
        "degenerate_object_path_support": path_totals["degenerate_object_path_support"],
        "degenerate_object_path_coefficient_mass": path_totals[
            "degenerate_object_path_coefficient_mass"
        ],
        "atom_tensor_support_min": int(min(row["tensor_path_support"] for row in atom_rows)),
        "atom_tensor_support_max": int(max(row["tensor_path_support"] for row in atom_rows)),
        "atom_tensor_mass_min": int(min(row["tensor_path_coefficient_mass"] for row in atom_rows)),
        "atom_tensor_mass_max": int(max(row["tensor_path_coefficient_mass"] for row in atom_rows)),
        "atom_internal_relation_count_min": int(min(row["internal_relation_count"] for row in atom_rows)),
        "atom_internal_relation_count_max": int(max(row["internal_relation_count"] for row in atom_rows)),
        "atom_internal_signature_class_count_min": int(
            min(row["internal_signature_class_count"] for row in atom_rows)
        ),
        "atom_internal_signature_class_count_max": int(
            max(row["internal_signature_class_count"] for row in atom_rows)
        ),
        "relation_atom_incidence_total": atom_relation_incidence_total,
        "complement_pair_count": len(complement_pairs),
        "atlas_table_sha256": sha_array(atom_numeric),
        "relation_signature_class_ids_sha256": sha_array(class_ids),
    }

    certificate = {
        "schema": "c985.d20_boundary_invariant_atlas_certificate@1",
        "status": STATUS if all(checks.values()) else "C985_D20_BOUNDARY_INVARIANT_ATLAS_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the visible d20 atom domain is the certified C(H6,3) table",
            "C985 tensor object paths with three distinct sectors project to exactly one d20 atom",
            "object paths with repeated sectors are explicitly kept outside the Lambda^3 H6 projection",
            "all 233 C985 relation-signature classes are visible through atom-internal source/target incidence",
            "the atlas ranks d20 atoms by tensor mass and internal relation-signature diversity",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_boundary_invariant_atlas@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The certified C985 tensor geometry projects to a reproducible d20 boundary "
            "atlas over the 20 C(H6,3) atoms by aggregating distinct three-sector tensor "
            "paths and atom-internal relation signatures."
        ),
        "stage_protocol": {
            "draft": "use the certified tensor geometry readout and tiny-pointer d20 atom domain",
            "witness": "materialize the 20-row d20 atom atlas plus machine numeric table",
            "coherence": "check C(H6,3), tensor path partitioning, relation incidence totals, and signature coverage",
            "closure": "certify a boundary invariant atlas without claiming optional categorical enrichment",
            "emit": "emit atlas CSV/JSON/NPZ and the next invariant-discovery target",
        },
        "inputs": {
            "tensor_geometry_report": input_entry(
                GEOMETRY_REPORT,
                {
                    "status": geometry_report.get("status"),
                    "certificate_sha256": geometry_report.get("certificate_sha256"),
                },
            ),
            "object_sector_cubes": input_entry(OBJECT_SECTOR_CUBES),
            "relation_geometry_signatures": input_entry(RELATION_GEOMETRY_SIGNATURES),
            "tensor_geometry_summary": input_entry(TENSOR_GEOMETRY_SUMMARY),
            "tiny_pointer_report": input_entry(
                TINY_POINTER_REPORT,
                {"status": tiny_pointer_report.get("status")},
            ),
            "d20_atom_domain": input_entry(D20_ATOM_DOMAIN_CSV),
            "tiny_pointer_schema": input_entry(TINY_POINTER_SCHEMA),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "d20_boundary_invariant_atlas": relpath(OUT_DIR / "d20_boundary_invariant_atlas.json"),
            "d20_boundary_invariant_atlas_csv": relpath(OUT_DIR / "d20_boundary_invariant_atlas.csv"),
            "d20_boundary_invariant_atlas_npz": relpath(OUT_DIR / "d20_boundary_invariant_atlas.npz"),
            "projection_certificate": relpath(OUT_DIR / "projection_certificate.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "projection of distinct C985 object-sector tensor paths onto the 20 d20 atoms",
                "explicit accounting of repeated-sector tensor paths outside Lambda^3 H6",
                "atom-internal aggregation of C985 relation-signature classes",
                "complement-pair atlas over the 20 d20 atoms",
                "machine-readable atlas table for invariant search and visualization",
            ],
            "does_not_certify_because_not_required": [
                "a full packet bridge from d20 atoms to A985/tube coordinates",
                "a packet normalization killing known boundary torsion",
                "pivotal or spherical normalization",
                "unitarity, braiding, ribbon, or Drinfeld-center modular data",
            ],
        },
        "next_highest_yield_item": (
            "Use d20_boundary_invariant_atlas.npz to choose landmark atoms and build "
            "a boundary-neighborhood graph weighted by tensor mass, signature overlap, "
            "and complement-pair contrast."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_boundary_invariant_atlas_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load the certified C985 tensor-geometry readout",
            "load the certified d20 C(H6,3) atom domain",
            "aggregate six ordered distinct object-sector paths per d20 atom",
            "attach relation signatures whose source and target lie inside each atom",
            "verify distinct/repeated object-path partition totals",
            "verify all relation-signature classes are visible through atom incidence",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "atlas": atlas,
        "atlas_csv": atlas_csv_text(atom_rows),
        "atom_numeric": atom_numeric,
        "relation_signature_class_ids": class_ids,
        "projection_certificate": certificate,
        "report": report,
        "manifest": manifest,
        "debug": {
            "atom_domain_csv": atom_domain_csv_text(atom_domain),
            "tensor_summary_status": tensor_summary.get("schema"),
        },
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
    write_json(OUT_DIR / "d20_boundary_invariant_atlas.json", payloads["atlas"])
    (OUT_DIR / "d20_boundary_invariant_atlas.csv").write_text(
        payloads["atlas_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "d20_boundary_invariant_atlas.npz",
        atom_table=payloads["atom_numeric"],
        relation_signature_class_ids=payloads["relation_signature_class_ids"],
    )
    write_json(OUT_DIR / "projection_certificate.json", payloads["projection_certificate"])
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
                "atom_count": payloads["report"]["witness"]["atom_count"],
                "distinct_object_path_support": payloads["report"]["witness"][
                    "distinct_object_path_support"
                ],
                "distinct_object_path_coefficient_mass": payloads["report"]["witness"][
                    "distinct_object_path_coefficient_mass"
                ],
                "signature_class_count": payloads["report"]["witness"]["signature_class_count"],
                "next_highest_yield_item": payloads["report"]["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
