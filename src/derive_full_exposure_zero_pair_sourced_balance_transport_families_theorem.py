from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "full_exposure_zero_pair_sourced_balance_transport_families"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

SOURCED_BALANCE_SHORTEST_PATHS_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_shortest_paths"
    / "report.json"
)
AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "amplitude_quotient_fourier_mode_classifier"
    / "report.json"
)
GLOBAL_CORRECTED_HIDDEN_SPLIT_SYMMETRY_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "global_corrected_hidden_split_symmetry"
    / "report.json"
)
HIDDEN_SPLIT_AUGMENTED_LEDGER_STABILIZER_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "hidden_split_augmented_ledger_stabilizer"
    / "report.json"
)

GAMMA8_MASK = 1 << 8
SELECTED_MASK = GAMMA8_MASK + (1 << 5)
RESIDUE_RANK = 11
EXPECTED_STEP_HISTOGRAM = {
    "1": 9,
    "2": 10,
    "3": 120,
    "4": 120,
    "5": 252,
    "6": 252,
    "7": 120,
    "8": 120,
    "9": 10,
    "10": 10,
}


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


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
        theorems = [item for item in index.get("theorems", []) if item.get("id") != THEOREM_ID]
    else:
        theorems = []
    theorems.append(entry)
    theorems = sorted(theorems, key=lambda item: item["id"])
    index = {
        "schema": "d20.theorem_registry",
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": len(theorems),
        "theorems": theorems,
    }
    index["registry_sha256"] = sha_json({k: v for k, v in index.items() if k != "registry_sha256"})
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def histogram(values: list[int]) -> dict[str, int]:
    counts = Counter(values)
    return {str(key): int(counts[key]) for key in sorted(counts)}


def size_histogram(groups: dict[str, list[dict[str, Any]]]) -> dict[str, int]:
    counts = Counter(len(rows) for rows in groups.values())
    return {str(key): int(counts[key]) for key in sorted(counts)}


def make_groups(
    rows: list[dict[str, Any]], key_fn: Callable[[dict[str, Any]], Any]
) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[json.dumps(key_fn(row), sort_keys=True, separators=(",", ":"))].append(row)
    return dict(groups)


def scalar_family_summary(rows: list[dict[str, Any]], field: str) -> dict[str, Any]:
    groups: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[int(row[field])].append(row)
    collision_examples = []
    for value in sorted(groups):
        family_rows = groups[value]
        if len(family_rows) > 1:
            collision_examples.append(
                {
                    "value": value,
                    "count": len(family_rows),
                    "target_masks": sorted(int(row["target_mask"]) for row in family_rows)[:12],
                }
            )
        if len(collision_examples) == 12:
            break
    size_counts = Counter(len(family_rows) for family_rows in groups.values())
    return {
        "field": field,
        "family_count": len(groups),
        "collision_family_count": sum(1 for family_rows in groups.values() if len(family_rows) > 1),
        "max_family_size": max(len(family_rows) for family_rows in groups.values()),
        "size_histogram": {str(size): int(size_counts[size]) for size in sorted(size_counts)},
        "first_collision_examples": collision_examples,
    }


def group_summary(
    rows: list[dict[str, Any]],
    key_fn: Callable[[dict[str, Any]], Any],
    key_name: str,
) -> dict[str, Any]:
    groups = make_groups(rows, key_fn)
    collisions = []
    for key in sorted(groups):
        family_rows = groups[key]
        if len(family_rows) > 1:
            collisions.append(
                {
                    key_name: json.loads(key),
                    "count": len(family_rows),
                    "target_masks": sorted(int(row["target_mask"]) for row in family_rows)[:12],
                }
            )
        if len(collisions) == 12:
            break
    return {
        "family_count": len(groups),
        "collision_family_count": sum(1 for family_rows in groups.values() if len(family_rows) > 1),
        "max_family_size": max(len(family_rows) for family_rows in groups.values()),
        "size_histogram": size_histogram(groups),
        "first_collision_examples": collisions,
        "families_sha256": sha_json(
            [
                {
                    key_name: json.loads(key),
                    "target_masks": sorted(int(row["target_mask"]) for row in family_rows),
                }
                for key, family_rows in sorted(groups.items())
            ]
        ),
    }


def target_fourier_signature(row: dict[str, Any]) -> list[Any]:
    mode = row["fourier_mode"]
    return [
        mode["support_weight"],
        mode["active_step_atom_count"],
        mode["sector26_optical_clock_mod26"],
        mode["adjacency_eigenvalue"],
        mode["laplacian_eigenvalue"],
        mode["gamma8_support"],
        mode["gamma8_translation_eigenvalue"],
        mode["hidden_projection_type"],
    ]


def transport_signature(row: dict[str, Any]) -> list[Any]:
    return [
        row["shortest_step_count"],
        row["shortest_path_action"],
        row["target_height_action"],
        *target_fourier_signature(row),
    ]


def step_family_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_step: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_step[int(row["shortest_step_count"])].append(row)
    families = []
    for step in sorted(by_step):
        family_rows = by_step[step]
        families.append(
            {
                "shortest_step_count": step,
                "target_count": len(family_rows),
                "min_shortest_path_action": min(int(row["shortest_path_action"]) for row in family_rows),
                "max_shortest_path_action": max(int(row["shortest_path_action"]) for row in family_rows),
                "min_target_height_action": min(int(row["target_height_action"]) for row in family_rows),
                "max_target_height_action": max(int(row["target_height_action"]) for row in family_rows),
                "targets_requiring_gamma8_removal": sum(
                    1 for row in family_rows if 8 in row["remove_generator_ids"]
                ),
                "targets_using_generator3": sum(
                    1 for row in family_rows if 3 in row["toggle_generator_ids"]
                ),
            }
        )
    return families


def coarse_transport_family_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[int, bool, bool], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = (
            int(row["shortest_step_count"]),
            8 in row["remove_generator_ids"],
            3 in row["toggle_generator_ids"],
        )
        groups[key].append(row)
    families = []
    for key in sorted(groups):
        step, removes_gamma8, uses_generator3 = key
        family_rows = groups[key]
        families.append(
            {
                "shortest_step_count": step,
                "removes_gamma8": removes_gamma8,
                "uses_generator3": uses_generator3,
                "target_count": len(family_rows),
                "min_shortest_path_action": min(int(row["shortest_path_action"]) for row in family_rows),
                "max_shortest_path_action": max(int(row["shortest_path_action"]) for row in family_rows),
                "min_target_height_action": min(int(row["target_height_action"]) for row in family_rows),
                "max_target_height_action": max(int(row["target_height_action"]) for row in family_rows),
            }
        )
    return families


def apply_linear_image(mask: int, basis_image_masks: list[int]) -> int:
    image = 0
    for idx in range(RESIDUE_RANK):
        if mask & (1 << idx):
            image ^= int(basis_image_masks[idx])
    return image


def hidden_split_c2_orbits(
    rows: list[dict[str, Any]], basis_image_masks: list[int]
) -> list[dict[str, Any]]:
    by_mask = {int(row["target_mask"]): row for row in rows}
    target_masks = set(by_mask)
    seen: set[int] = set()
    orbit_rows = []
    for mask in sorted(target_masks):
        if mask in seen:
            continue
        orbit = sorted({mask, apply_linear_image(mask, basis_image_masks)})
        seen.update(orbit)
        members = [by_mask[item] for item in orbit]
        path_actions = [int(row["shortest_path_action"]) for row in members]
        target_heights = [int(row["target_height_action"]) for row in members]
        step_counts = [int(row["shortest_step_count"]) for row in members]
        r33_values = [int(row["target_corrected_R33_mod26"]) for row in members]
        hidden_packets = [row["target_hidden_packet"] for row in members]
        orbit_rows.append(
            {
                "target_masks": orbit,
                "size": len(orbit),
                "shortest_step_counts": step_counts,
                "shortest_path_actions": path_actions,
                "target_height_actions": target_heights,
                "target_corrected_R33_mod26_values": r33_values,
                "target_hidden_packets": hidden_packets,
                "step_coherent": len(set(step_counts)) == 1,
                "path_action_coherent": len(set(path_actions)) == 1,
                "target_height_coherent": len(set(target_heights)) == 1,
                "r33_coherent": len(set(r33_values)) == 1,
                "hidden_packet_coherent": len(set(hidden_packets)) == 1,
            }
        )
    return orbit_rows


def first_breaking_examples(orbit_rows: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    coherent_field = {
        "shortest_path_actions": "path_action_coherent",
        "target_height_actions": "target_height_coherent",
        "shortest_step_counts": "step_coherent",
    }[field]
    examples = []
    for row in orbit_rows:
        if not row[coherent_field]:
            examples.append(
                {
                    "target_masks": row["target_masks"],
                    field: row[field],
                    "shortest_step_counts": row["shortest_step_counts"],
                }
            )
        if len(examples) == 8:
            break
    return examples


def build_theorem() -> dict[str, Any]:
    shortest_paths = load_json(SOURCED_BALANCE_SHORTEST_PATHS_REPORT)
    fourier_classifier = load_json(AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER_REPORT)
    hidden_split_symmetry = load_json(GLOBAL_CORRECTED_HIDDEN_SPLIT_SYMMETRY_REPORT)
    augmented_stabilizer = load_json(HIDDEN_SPLIT_AUGMENTED_LEDGER_STABILIZER_REPORT)

    path_rows = shortest_paths.get("derived", {}).get("shortest_path_rows", [])
    mode_rows = fourier_classifier.get("derived", {}).get("mode_rows", [])
    mode_by_mask = {int(row["mode_mask"]): row for row in mode_rows}
    enriched_rows = []
    for row in path_rows:
        target_mask = int(row["target_mask"])
        enriched = dict(row)
        enriched["fourier_mode"] = mode_by_mask[target_mask]
        enriched_rows.append(enriched)

    step_histogram = histogram([int(row["shortest_step_count"]) for row in enriched_rows])
    action_summary = scalar_family_summary(enriched_rows, "shortest_path_action")
    target_height_summary = scalar_family_summary(enriched_rows, "target_height_action")
    step_summary_rows = step_family_rows(enriched_rows)
    coarse_rows = coarse_transport_family_rows(enriched_rows)
    generator_support_summary = group_summary(
        enriched_rows,
        lambda row: row["toggle_generator_ids"],
        "toggle_generator_ids",
    )
    fourier_signature_summary = group_summary(
        enriched_rows,
        target_fourier_signature,
        "fourier_signature",
    )
    transport_signature_summary = group_summary(
        enriched_rows,
        transport_signature,
        "transport_signature",
    )

    hidden_split_classification = hidden_split_symmetry.get("derived", {}).get(
        "symmetry_classification", {}
    )
    preserving_automorphisms = hidden_split_classification.get("preserving_automorphisms", [])
    hidden_split_nonidentity = next(
        (
            record
            for record in preserving_automorphisms
            if record.get("automorphism_id") != 0 or record.get("vertex_cycle_notation")
        ),
        None,
    )
    c2_basis_image_masks = (
        [int(mask) for mask in hidden_split_nonidentity.get("basis_image_masks", [])]
        if hidden_split_nonidentity
        else []
    )
    c2_orbit_rows = hidden_split_c2_orbits(enriched_rows, c2_basis_image_masks)
    c2_orbit_summary = {
        "target_orbit_count": len(c2_orbit_rows),
        "fixed_target_count": sum(1 for row in c2_orbit_rows if row["size"] == 1),
        "two_target_orbit_count": sum(1 for row in c2_orbit_rows if row["size"] == 2),
        "step_coherent_orbit_count": sum(1 for row in c2_orbit_rows if row["step_coherent"]),
        "path_action_coherent_orbit_count": sum(
            1 for row in c2_orbit_rows if row["path_action_coherent"]
        ),
        "target_height_coherent_orbit_count": sum(
            1 for row in c2_orbit_rows if row["target_height_coherent"]
        ),
        "r33_coherent_orbit_count": sum(1 for row in c2_orbit_rows if row["r33_coherent"]),
        "hidden_packet_coherent_orbit_count": sum(
            1 for row in c2_orbit_rows if row["hidden_packet_coherent"]
        ),
        "path_action_breaking_orbit_count": sum(
            1 for row in c2_orbit_rows if not row["path_action_coherent"]
        ),
        "target_height_breaking_orbit_count": sum(
            1 for row in c2_orbit_rows if not row["target_height_coherent"]
        ),
        "step_breaking_orbit_count": sum(1 for row in c2_orbit_rows if not row["step_coherent"]),
        "c2_target_orbits_sha256": sha_json(c2_orbit_rows),
        "first_path_action_breaking_examples": first_breaking_examples(
            c2_orbit_rows, "shortest_path_actions"
        ),
        "first_target_height_breaking_examples": first_breaking_examples(
            c2_orbit_rows, "target_height_actions"
        ),
        "first_step_breaking_examples": first_breaking_examples(
            c2_orbit_rows, "shortest_step_counts"
        ),
    }

    target_masks = {int(row["target_mask"]) for row in enriched_rows}
    c2_images = {apply_linear_image(mask, c2_basis_image_masks) for mask in target_masks}
    augmented_summary = augmented_stabilizer.get("derived", {}).get("summary", {})
    augmented_candidate_group = augmented_stabilizer.get("derived", {}).get("candidate_group", {})
    graph_summary = hidden_split_symmetry.get("derived", {}).get("graph", {})
    minimum_row = min(
        enriched_rows,
        key=lambda row: (int(row["shortest_path_action"]), int(row["target_mask"])),
    )
    transport_family_summary = {
        "target_count": len(enriched_rows),
        "step_family_count": len(step_summary_rows),
        "shortest_step_count_histogram": step_histogram,
        "coarse_gamma8_generator3_family_count": len(coarse_rows),
        "shortest_path_action_family_count": action_summary["family_count"],
        "target_height_action_family_count": target_height_summary["family_count"],
        "exact_generator_support_family_count": generator_support_summary["family_count"],
        "fourier_signature_family_count": fourier_signature_summary["family_count"],
        "transport_signature_family_count": transport_signature_summary["family_count"],
        "public_graph_automorphism_count": graph_summary.get("public_automorphism_count"),
        "corrected_hidden_split_stabilizer_order": hidden_split_classification.get(
            "preserving_automorphism_count"
        ),
        "full_augmented_ledger_stabilizer_order": augmented_candidate_group.get(
            "full_augmented_ledger_stabilizer_order"
        ),
        "minimum_transport_family": {
            "target_mask": int(minimum_row["target_mask"]),
            "shortest_path_action": int(minimum_row["shortest_path_action"]),
            "target_height_action": int(minimum_row["target_height_action"]),
            "toggle_generator_ids": minimum_row["toggle_generator_ids"],
            "fourier_signature": target_fourier_signature(minimum_row),
        },
        "compression_reading": (
            "Scalar transport data compresses the 1023 targets, the hidden-split C2 gives a topological "
            "543-orbit quotient, but the full action/charge/counterterm ledger admits only the identity "
            "as a coherent symmetry."
        ),
    }

    checks = {
        "shortest_paths_is_certified": shortest_paths.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_SHORTEST_PATHS_CERTIFIED"
        and shortest_paths.get("all_checks_pass") is True,
        "fourier_mode_classifier_is_certified": fourier_classifier.get("status")
        == "D20_AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER_CERTIFIED"
        and fourier_classifier.get("all_checks_pass") is True,
        "global_corrected_hidden_split_symmetry_is_certified": hidden_split_symmetry.get("status")
        == "D20_GLOBAL_CORRECTED_HIDDEN_SPLIT_SYMMETRY_CERTIFIED"
        and hidden_split_symmetry.get("all_checks_pass") is True,
        "hidden_split_augmented_ledger_stabilizer_is_certified": augmented_stabilizer.get("status")
        == "D20_HIDDEN_SPLIT_AUGMENTED_LEDGER_STABILIZER_CERTIFIED"
        and augmented_stabilizer.get("all_checks_pass") is True,
        "all_targets_join_to_fourier_modes": len(enriched_rows) == 1023
        and len(mode_rows) == 2048
        and all(int(row["target_mask"]) in mode_by_mask for row in path_rows),
        "step_family_count_and_histogram_match_kernel_geometry": len(step_summary_rows) == 10
        and step_histogram == EXPECTED_STEP_HISTOGRAM,
        "path_and_height_scalar_families_have_805_values": action_summary["family_count"] == 805
        and target_height_summary["family_count"] == 805
        and action_summary["size_histogram"] == {"1": 597, "2": 198, "3": 10}
        and target_height_summary["size_histogram"] == {"1": 597, "2": 198, "3": 10},
        "coarse_gamma8_generator3_partition_has_19_families": len(coarse_rows) == 19,
        "exact_generator_support_has_no_nontrivial_compression": generator_support_summary[
            "family_count"
        ]
        == 1023
        and generator_support_summary["size_histogram"] == {"1": 1023},
        "fourier_signature_compresses_to_690_families": fourier_signature_summary[
            "family_count"
        ]
        == 690
        and fourier_signature_summary["max_family_size"] == 7,
        "full_transport_signature_compresses_to_991_families": transport_signature_summary[
            "family_count"
        ]
        == 991
        and transport_signature_summary["collision_family_count"] == 32
        and transport_signature_summary["max_family_size"] == 2,
        "hidden_split_c2_maps_kernel_targets_to_kernel_targets_and_fixes_gamma8": c2_basis_image_masks
        and c2_images == target_masks
        and apply_linear_image(GAMMA8_MASK, c2_basis_image_masks) == GAMMA8_MASK,
        "hidden_split_c2_compresses_targets_but_breaks_action_height_labels": c2_orbit_summary[
            "target_orbit_count"
        ]
        == 543
        and c2_orbit_summary["fixed_target_count"] == 63
        and c2_orbit_summary["two_target_orbit_count"] == 480
        and c2_orbit_summary["path_action_coherent_orbit_count"] == 71
        and c2_orbit_summary["target_height_coherent_orbit_count"] == 71
        and c2_orbit_summary["path_action_breaking_orbit_count"] == 472,
        "hidden_split_c2_preserves_kernel_packet_and_r33_labels": c2_orbit_summary[
            "r33_coherent_orbit_count"
        ]
        == 543
        and c2_orbit_summary["hidden_packet_coherent_orbit_count"] == 543,
        "full_augmented_ledger_symmetry_compression_is_identity": augmented_candidate_group.get(
            "full_augmented_ledger_stabilizer_order"
        )
        == 1
        and augmented_summary.get("identity_preserves_everything") is True
        and augmented_summary.get("nonidentity_preserves_only_corrected_hidden_layer") is True,
        "mask288_remains_unique_minimum_transport_family": minimum_row["target_mask"]
        == SELECTED_MASK
        and minimum_row["shortest_path_action"] == 691200
        and minimum_row["target_height_action"] == 1065984
        and minimum_row["toggle_generator_ids"] == [5],
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_TRANSPORT_FAMILIES_CERTIFIED"
        if all_checks_pass
        else "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_TRANSPORT_FAMILIES_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.full_exposure_zero_pair_sourced_balance_transport_families",
        "status": status,
        "object": "d20",
        "claim": (
            "The 1023 certified gamma8-to-Ward-kernel shortest paths admit scalar, Fourier, and "
            "topological transport-family compressions, while the full action/charge/counterterm ledger "
            "permits no nontrivial D20 symmetry quotient. The only fully ledger-coherent symmetry "
            "compression is the identity."
        ),
        "definition": {
            "transport_family": (
                "A class of shortest sourced-balance paths grouped by selected invariants such as step "
                "count, positive path action, target height action, Fourier mode labels, and generator "
                "support."
            ),
            "hidden_split_c2_topological_orbit": (
                "The orbit of a nonzero Ward-kernel target under the certified nonidentity automorphism "
                "that preserves the corrected hidden split and fixes gamma8."
            ),
            "full_ledger_coherent_symmetry": (
                "A D20 graph automorphism preserving the corrected hidden split together with primitive "
                "action weights, public charges, public edge fluxes, sector-26 counterterms, normalized "
                "clock, and edge interface weights."
            ),
        },
        "inputs": {
            "sourced_balance_shortest_paths_report": {
                "path": rel(SOURCED_BALANCE_SHORTEST_PATHS_REPORT),
                "sha256": sha_file(SOURCED_BALANCE_SHORTEST_PATHS_REPORT),
            },
            "amplitude_quotient_fourier_mode_classifier_report": {
                "path": rel(AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER_REPORT),
                "sha256": sha_file(AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER_REPORT),
            },
            "global_corrected_hidden_split_symmetry_report": {
                "path": rel(GLOBAL_CORRECTED_HIDDEN_SPLIT_SYMMETRY_REPORT),
                "sha256": sha_file(GLOBAL_CORRECTED_HIDDEN_SPLIT_SYMMETRY_REPORT),
            },
            "hidden_split_augmented_ledger_stabilizer_report": {
                "path": rel(HIDDEN_SPLIT_AUGMENTED_LEDGER_STABILIZER_REPORT),
                "sha256": sha_file(HIDDEN_SPLIT_AUGMENTED_LEDGER_STABILIZER_REPORT),
            },
        },
        "derived": {
            "transport_family_summary": transport_family_summary,
            "step_families": step_summary_rows,
            "coarse_gamma8_generator3_families": coarse_rows,
            "shortest_path_action_family_summary": action_summary,
            "target_height_action_family_summary": target_height_summary,
            "exact_generator_support_family_summary": generator_support_summary,
            "fourier_signature_family_summary": fourier_signature_summary,
            "transport_signature_family_summary": transport_signature_summary,
            "hidden_split_c2_orbit_summary": c2_orbit_summary,
            "hidden_split_c2_orbit_rows": c2_orbit_rows,
            "symmetry_levels": {
                "public_graph": {
                    "automorphism_count": graph_summary.get("public_automorphism_count"),
                    "source": rel(GLOBAL_CORRECTED_HIDDEN_SPLIT_SYMMETRY_REPORT),
                },
                "corrected_hidden_split": {
                    "stabilizer_order": hidden_split_classification.get(
                        "preserving_automorphism_count"
                    ),
                    "target_orbit_count_on_nonzero_kernel": c2_orbit_summary["target_orbit_count"],
                    "action_height_coherent_orbit_count": c2_orbit_summary[
                        "path_action_coherent_orbit_count"
                    ],
                },
                "full_augmented_ledger": {
                    "stabilizer_order": augmented_candidate_group.get(
                        "full_augmented_ledger_stabilizer_order"
                    ),
                    "preserving_automorphism_ids": augmented_candidate_group.get(
                        "full_augmented_ledger_preserving_automorphism_ids"
                    ),
                    "nonidentity_first_failures": augmented_summary.get(
                        "nonidentity_first_failures"
                    ),
                },
            },
        },
        "interpretation": {
            "what_this_proves": [
                "the full 1023 shortest-path atlas has a certified scalar family structure",
                "path action and target height each collapse to 805 values with the same collision profile",
                "exact generator support remains singleton-level, so support labels identify every target",
                "Fourier mode labels compress the target set more strongly than action-height labels alone",
                "the corrected hidden-split C2 gives a 543-orbit topological quotient but breaks most action-height labels",
                "the full physical ledger has identity stabilizer, so no nontrivial D20 symmetry quotient is currently coherent",
            ],
            "what_this_does_not_prove": (
                "This does not prove a continuum transport limit or a nontrivial full-ledger symmetry. It also "
                "does not assert that the full public 120-automorphism graph action is a label-preserving "
                "closed-return action on the sourced-balance atlas."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Build the label-relaxed public/hidden-split orbit quotient and prove exactly which labels must "
            "be forgotten to recover a nontrivial D20 transport symmetry."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {k: v for k, v in report.items() if k != "certificate_sha256"}
    )
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.full_exposure_zero_pair_sourced_balance_transport_families_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify shortest-path, Fourier classifier, hidden-split symmetry, and augmented ledger inputs",
            "join all 1023 shortest-path targets to Fourier mode rows",
            "compute step-count, path-action, target-height, Fourier, transport, and generator-support families",
            "verify the hidden-split C2 maps nonzero Ward-kernel targets to nonzero Ward-kernel targets",
            "verify the hidden-split C2 quotient breaks most path-action and target-height labels",
            "verify the full augmented ledger stabilizer has order one",
            "verify mask 288 remains the unique minimum transport family",
        ],
    }
    manifest["report_sha256"] = report["certificate_sha256"]
    manifest["manifest_sha256"] = sha_json(
        {k: v for k, v in manifest.items() if k != "manifest_sha256"}
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    update_theorem_index(report, out_dir)
    return report


def main() -> None:
    report = write_theorem()
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report.get("all_checks_pass"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
