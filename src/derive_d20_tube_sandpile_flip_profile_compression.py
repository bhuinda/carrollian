from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

try:
    from .derive_d20_sandpile_critical_group_theorem import rel, sha_file, sha_json
    from .derive_global_corrected_hidden_split_symmetry_theorem import (
        AUTOMORPHISM_SUMMARY,
        EDGE_CSV,
        RESIDUE_SPECTRUM_CSV,
        edge_permutation,
        enumerate_automorphisms,
        graph_matrices,
        induced_basis_images,
        load_edges,
        load_residue_maps,
    )
    from .paths import D20_INVARIANTS
except ImportError:  # Supports `python src/derive_d20_tube_sandpile_flip_profile_compression.py`.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.derive_d20_sandpile_critical_group_theorem import rel, sha_file, sha_json
    from src.derive_global_corrected_hidden_split_symmetry_theorem import (
        AUTOMORPHISM_SUMMARY,
        EDGE_CSV,
        RESIDUE_SPECTRUM_CSV,
        edge_permutation,
        enumerate_automorphisms,
        graph_matrices,
        induced_basis_images,
        load_edges,
        load_residue_maps,
    )
    from src.paths import D20_INVARIANTS


THEOREM_ID = "tube_sandpile_flip_profile_compression"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
COSET_CLASSIFIER_REPORT = (
    D20_INVARIANTS / "theorems" / "tube_sandpile_flip_coset_classifier" / "report.json"
)
PUBLIC_BOUNDARY_REPORT = (
    D20_INVARIANTS / "theorems" / "public_boundary_graph_invariants" / "report.json"
)

RESIDUE_RANK = 11
COVER_DELTAS = [1560, 128, 512, 130, 421]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def update_theorem_index(report: dict[str, Any], out_dir: Path) -> None:
    index_path = out_dir.parent / "index.json"
    entry = {
        "id": THEOREM_ID,
        "manifest": rel(out_dir / "manifest.json"),
        "report": rel(out_dir / "report.json"),
        "report_sha256": report["certificate_sha256"],
        "status": report["status"],
    }
    if index_path.exists():
        index = load_json(index_path)
        schema = index.get("schema", "d20.theorem_registry")
        theorems = [item for item in index.get("theorems", []) if item.get("id") != THEOREM_ID]
    else:
        schema = "d20.theorem_registry"
        theorems = []
    theorems.append(entry)
    theorems = sorted(theorems, key=lambda item: item["id"])
    index = {
        "schema": schema,
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": len(theorems),
        "theorems": theorems,
    }
    index["registry_sha256"] = sha_json({k: v for k, v in index.items() if k != "registry_sha256"})
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bit_indices(mask: int, width: int = RESIDUE_RANK) -> list[int]:
    return [idx for idx in range(width) if (mask >> idx) & 1]


def xor_all(values: list[int]) -> int:
    out = 0
    for value in values:
        out ^= value
    return out


def cover_span() -> set[int]:
    out: set[int] = set()
    for selector in range(1 << len(COVER_DELTAS)):
        selected = [COVER_DELTAS[idx] for idx in range(len(COVER_DELTAS)) if (selector >> idx) & 1]
        out.add(xor_all(selected))
    return out


def apply_residue_action(mask: int, basis_images: list[int]) -> int:
    out = 0
    for idx, image in enumerate(basis_images):
        if (mask >> idx) & 1:
            out ^= image
    return out


def histogram(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(value) for key, value in sorted(counter.items())}


def freeze_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): freeze_json(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [freeze_json(item) for item in value]
    return value


def profile_key(row: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    return {field: freeze_json(row[field]) for field in fields}


def profile_classes(rows: list[dict[str, Any]], fields: list[str]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = profile_key(row, fields)
        key_hash = sha_json(key)
        grouped.setdefault(key_hash, {"profile_key": key, "coset_indices": []})
        grouped[key_hash]["coset_indices"].append(int(row["coset_index"]))
    out = []
    for class_index, (key_hash, item) in enumerate(
        sorted(grouped.items(), key=lambda pair: (pair[1]["coset_indices"][0], pair[0]))
    ):
        coset_indices = sorted(item["coset_indices"])
        out.append(
            {
                "profile_class_index": class_index,
                "profile_key_sha256": key_hash,
                "class_size": len(coset_indices),
                "coset_indices": coset_indices,
                "profile_key": item["profile_key"],
                "contains_cover_span_coset": 0 in coset_indices,
            }
        )
    return out


def automorphism_action_summary(coset_rows: list[dict[str, Any]]) -> dict[str, Any]:
    edges, edge_ids = load_edges()
    adjacency, _neighbors, distances = graph_matrices(edges)
    automorphisms = enumerate_automorphisms(adjacency, distances)
    mask_to_incidence, incidence_to_mask = load_residue_maps()

    generator_deltas = sorted(
        int(delta)
        for row in coset_rows
        for delta in row["generator_delta_masks"]
    )
    generator_set = set(generator_deltas)
    span = cover_span()
    cover_set = set(COVER_DELTAS)

    action_rows = []
    flip_preservers = []
    cover_span_preservers = []
    cover_set_preservers = []
    quotient_preservers = []
    first_flip_failure: dict[str, Any] | None = None

    for automorphism_id, vertex_perm in enumerate(automorphisms):
        edge_perm = edge_permutation(vertex_perm, edges, edge_ids)
        basis_images = induced_basis_images(edge_perm, mask_to_incidence, incidence_to_mask)
        image_generator_set = {apply_residue_action(delta, basis_images) for delta in generator_set}
        image_cover_span = {apply_residue_action(delta, basis_images) for delta in span}
        image_cover_set = {apply_residue_action(delta, basis_images) for delta in cover_set}

        flip_preserves = image_generator_set == generator_set
        cover_span_preserves = image_cover_span == span
        cover_set_preserves = image_cover_set == cover_set
        quotient_preserves = flip_preserves and cover_span_preserves
        if flip_preserves:
            flip_preservers.append(automorphism_id)
        elif first_flip_failure is None:
            source_delta = next(
                delta
                for delta in generator_deltas
                if apply_residue_action(delta, basis_images) not in generator_set
            )
            image_delta = apply_residue_action(source_delta, basis_images)
            first_flip_failure = {
                "automorphism_id": automorphism_id,
                "source_delta": source_delta,
                "source_delta_bits": bit_indices(source_delta),
                "image_delta": image_delta,
                "image_delta_bits": bit_indices(image_delta),
                "vertex_permutation": list(vertex_perm),
                "basis_image_masks": basis_images,
            }
        if cover_span_preserves:
            cover_span_preservers.append(automorphism_id)
        if cover_set_preserves:
            cover_set_preservers.append(automorphism_id)
        if quotient_preserves:
            quotient_preservers.append(automorphism_id)

        action_rows.append(
            {
                "automorphism_id": automorphism_id,
                "vertex_permutation": list(vertex_perm),
                "basis_image_masks": basis_images,
                "basis_image_bits": [bit_indices(mask) for mask in basis_images],
                "preserves_flip_generator_set": flip_preserves,
                "preserves_five_cover_span": cover_span_preserves,
                "preserves_five_cover_set": cover_set_preserves,
                "preserves_flip_quotient": quotient_preserves,
            }
        )

    return {
        "automorphism_count": len(automorphisms),
        "flip_generator_preserver_ids": flip_preservers,
        "five_cover_span_preserver_ids": cover_span_preservers,
        "five_cover_set_preserver_ids": cover_set_preservers,
        "flip_quotient_preserver_ids": quotient_preservers,
        "public_automorphism_compression_class_count": 64,
        "public_automorphism_compression_is_trivial": quotient_preservers == [0],
        "first_flip_set_failure": first_flip_failure,
        "action_rows_sha256": sha_json(action_rows),
        "action_rows": action_rows,
    }


def build_theorem() -> dict[str, Any]:
    source = load_json(COSET_CLASSIFIER_REPORT)
    public_boundary = load_json(PUBLIC_BOUNDARY_REPORT)
    coset_rows = source["derived"]["coset_rows"]

    automorphism = automorphism_action_summary(coset_rows)

    pair_order_fields = ["pair_sandpile_class_order_histogram"]
    fiber_order_fields = ["fiber_sandpile_class_order_histogram"]
    combined_order_fields = [
        "grade_flip_pair_count",
        "exact_divisor_fiber_count",
        "pair_sandpile_class_order_histogram",
        "fiber_sandpile_class_order_histogram",
    ]
    measured_profile_fields = [
        "grade_flip_pair_count",
        "exact_divisor_fiber_count",
        "pair_sandpile_class_order_histogram",
        "fiber_sandpile_class_order_histogram",
        "exact_divisor_fiber_size_histogram",
        "mixed_fiber_grade_split_histogram",
        "pair_grade_orientation_histogram",
    ]

    pair_order_rows = profile_classes(coset_rows, pair_order_fields)
    fiber_order_rows = profile_classes(coset_rows, fiber_order_fields)
    combined_order_rows = profile_classes(coset_rows, combined_order_fields)
    measured_profile_rows = profile_classes(coset_rows, measured_profile_fields)

    checks = {
        "source_coset_classifier_is_certified": source.get("status")
        == "D20_TUBE_SANDPILE_FLIP_COSET_CLASSIFIER_CERTIFIED"
        and source.get("all_checks_pass") is True,
        "public_boundary_source_is_certified": public_boundary.get("status")
        == "D20_PUBLIC_BOUNDARY_GRAPH_INVARIANTS_CERTIFIED"
        and public_boundary.get("all_checks_pass") is True,
        "automorphism_count_is_120": automorphism["automorphism_count"] == 120,
        "only_identity_preserves_flip_generator_set": automorphism["flip_generator_preserver_ids"] == [0],
        "only_identity_preserves_five_cover_span": automorphism["five_cover_span_preserver_ids"] == [0],
        "only_identity_preserves_five_cover_set": automorphism["five_cover_set_preserver_ids"] == [0],
        "only_identity_preserves_flip_quotient": automorphism["flip_quotient_preserver_ids"] == [0],
        "public_automorphism_compression_is_trivial": automorphism[
            "public_automorphism_compression_is_trivial"
        ]
        is True,
        "pair_order_profile_class_count_is_30": len(pair_order_rows) == 30,
        "fiber_order_profile_class_count_is_15": len(fiber_order_rows) == 15,
        "combined_order_profile_class_count_is_48": len(combined_order_rows) == 48,
        "measured_profile_class_count_is_58": len(measured_profile_rows) == 58,
        "combined_order_size_histogram_matches": histogram(
            Counter(row["class_size"] for row in combined_order_rows)
        )
        == {"1": 36, "2": 9, "3": 2, "4": 1},
        "cover_span_coset_is_singleton_under_combined_order_profile": any(
            row["coset_indices"] == [0] for row in combined_order_rows
        ),
        "combined_order_partition_covers_64_cosets": sorted(
            idx for row in combined_order_rows for idx in row["coset_indices"]
        )
        == list(range(64)),
        "pair_order_partition_covers_64_cosets": sorted(
            idx for row in pair_order_rows for idx in row["coset_indices"]
        )
        == list(range(64)),
        "fiber_order_partition_covers_64_cosets": sorted(
            idx for row in fiber_order_rows for idx in row["coset_indices"]
        )
        == list(range(64)),
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_TUBE_SANDPILE_FLIP_PROFILE_COMPRESSION_CERTIFIED"
        if all_checks_pass
        else "D20_TUBE_SANDPILE_FLIP_PROFILE_COMPRESSION_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.tube_sandpile_flip_profile_compression",
        "status": status,
        "object": "d20",
        "claim": (
            "The full public automorphism group does not nontrivially compress the 64 "
            "flip-coset quotient: only the identity preserves the flip-generator set and "
            "the five-cover span. Sandpile-order observables give a canonical finite "
            "compression: pair-order profiles give 30 classes, fiber-order profiles give "
            "15 classes, and the combined order profile gives 48 classes."
        ),
        "definition": {
            "public_automorphism_test": (
                "Enumerate the 120 public graph automorphisms, induce each action on the "
                "11-dimensional residue space, and test whether it preserves the 392 flip "
                "generators and the rank-5 five-cover span."
            ),
            "combined_order_profile": (
                "The canonical sandpile-order profile keeps grade-flip pair count, exact "
                "fiber count, pair-level sandpile class-order histogram, and fiber-level "
                "sandpile class-order histogram. It ignores concrete coset, fiber, class, "
                "and delta labels."
            ),
        },
        "inputs": {
            "tube_sandpile_flip_coset_classifier_report": {
                "path": rel(COSET_CLASSIFIER_REPORT),
                "sha256": sha_file(COSET_CLASSIFIER_REPORT),
            },
            "public_boundary_graph_invariants_report": {
                "path": rel(PUBLIC_BOUNDARY_REPORT),
                "sha256": sha_file(PUBLIC_BOUNDARY_REPORT),
            },
            "hcycle_edges_csv": {
                "path": rel(EDGE_CSV),
                "sha256": sha_file(EDGE_CSV),
            },
            "hcycle_residue_spectrum_csv": {
                "path": rel(RESIDUE_SPECTRUM_CSV),
                "sha256": sha_file(RESIDUE_SPECTRUM_CSV),
            },
            "hcycle_automorphism_summary": {
                "path": rel(AUTOMORPHISM_SUMMARY),
                "sha256": sha_file(AUTOMORPHISM_SUMMARY),
            },
        },
        "derived": {
            "automorphism_compression": {
                key: value
                for key, value in automorphism.items()
                if key != "action_rows"
            },
            "pair_order_profile": {
                "fields": pair_order_fields,
                "class_count": len(pair_order_rows),
                "class_size_histogram": histogram(Counter(row["class_size"] for row in pair_order_rows)),
                "class_rows_sha256": sha_json(pair_order_rows),
                "class_rows": pair_order_rows,
            },
            "fiber_order_profile": {
                "fields": fiber_order_fields,
                "class_count": len(fiber_order_rows),
                "class_size_histogram": histogram(Counter(row["class_size"] for row in fiber_order_rows)),
                "class_rows_sha256": sha_json(fiber_order_rows),
                "class_rows": fiber_order_rows,
            },
            "combined_order_profile": {
                "fields": combined_order_fields,
                "class_count": len(combined_order_rows),
                "class_size_histogram": histogram(
                    Counter(row["class_size"] for row in combined_order_rows)
                ),
                "class_rows_sha256": sha_json(combined_order_rows),
                "class_rows": combined_order_rows,
            },
            "measured_profile": {
                "fields": measured_profile_fields,
                "class_count": len(measured_profile_rows),
                "class_size_histogram": histogram(
                    Counter(row["class_size"] for row in measured_profile_rows)
                ),
                "class_rows_sha256": sha_json(measured_profile_rows),
                "class_rows": measured_profile_rows,
            },
        },
        "interpretation": {
            "what_is_certified": (
                "There is no nontrivial public-automorphism quotient compatible with the "
                "current exact flip generators and five-cover span. The certified compression "
                "is therefore a sandpile-order profile quotient."
            ),
            "what_this_does_not_prove": (
                "The 48 combined-order classes are canonical for the stated profile, but this "
                "does not prove they are minimal or complete invariants of the hidden tube data."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Refine the 48 combined-order classes with tube-sector data to test whether the "
            "four non-singleton class sizes 2, 3, and 4 split canonically."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.tube_sandpile_flip_profile_compression_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "load the certified 64-coset classifier",
            "enumerate the 120 public graph automorphisms",
            "induce each automorphism on the 11-dimensional residue space",
            "verify only the identity preserves the flip-generator quotient",
            "compress cosets by pair-order, fiber-order, and combined sandpile-order profiles",
        ],
    }
    manifest["report_sha256"] = report["certificate_sha256"]
    manifest["manifest_sha256"] = sha_json({k: v for k, v in manifest.items() if k != "manifest_sha256"})

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    update_theorem_index(report, out_dir)
    return report


def main() -> None:
    report = write_theorem()
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report.get("all_checks_pass"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
