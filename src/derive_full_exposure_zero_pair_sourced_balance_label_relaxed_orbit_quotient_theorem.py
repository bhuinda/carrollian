from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable

from src.derive_global_corrected_hidden_split_symmetry_theorem import (
    edge_permutation,
    enumerate_automorphisms,
    graph_matrices,
    hidden_parity,
    induced_basis_images,
    load_edges,
    load_residue_maps,
    preserves_hidden_split,
)
from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

SOURCED_BALANCE_SHORTEST_PATHS_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_shortest_paths"
    / "report.json"
)
SOURCED_BALANCE_TRANSPORT_FAMILIES_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_transport_families"
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
RESIDUE_RANK = 11
NONZERO_MASKS = set(range(1, 1 << RESIDUE_RANK))


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


def apply_linear_image(mask: int, basis_image_masks: list[int]) -> int:
    image = 0
    for idx in range(RESIDUE_RANK):
        if mask & (1 << idx):
            image ^= int(basis_image_masks[idx])
    return image


def reconstruct_public_automorphism_records(coefficients: list[int]) -> list[dict[str, Any]]:
    edges, edge_ids = load_edges()
    adjacency, _neighbors, distances = graph_matrices(edges)
    mask_to_incidence, incidence_to_mask = load_residue_maps()
    records = []
    for idx, vertex_perm in enumerate(enumerate_automorphisms(adjacency, distances)):
        edge_perm = edge_permutation(vertex_perm, edges, edge_ids)
        basis_images = induced_basis_images(edge_perm, mask_to_incidence, incidence_to_mask)
        basis_image_hidden_values = [hidden_parity(mask, coefficients) for mask in basis_images]
        records.append(
            {
                "automorphism_id": idx,
                "vertex_permutation": list(vertex_perm),
                "edge_permutation": edge_perm,
                "basis_image_masks": basis_images,
                "basis_image_hidden_z2": basis_image_hidden_values,
                "preserves_hidden_split": preserves_hidden_split(basis_images, coefficients),
            }
        )
    return records


def closure(seed: set[int], group_records: list[dict[str, Any]]) -> set[int]:
    seen = set(seed)
    frontier = list(seed)
    while frontier:
        mask = frontier.pop()
        for record in group_records:
            image = apply_linear_image(mask, record["basis_image_masks"])
            if image not in seen:
                seen.add(image)
                frontier.append(image)
    return seen


def orbit_rows(domain: set[int], group_records: list[dict[str, Any]]) -> list[list[int]]:
    seen: set[int] = set()
    orbits: list[list[int]] = []
    for mask in sorted(domain):
        if mask in seen:
            continue
        orbit = {mask}
        frontier = [mask]
        while frontier:
            cursor = frontier.pop()
            for record in group_records:
                image = apply_linear_image(cursor, record["basis_image_masks"])
                if image in domain and image not in orbit:
                    orbit.add(image)
                    frontier.append(image)
        seen.update(orbit)
        orbits.append(sorted(orbit))
    return orbits


def size_histogram(orbits: list[list[int]]) -> dict[str, int]:
    counts = Counter(len(orbit) for orbit in orbits)
    return {str(size): int(counts[size]) for size in sorted(counts)}


def label_coherence(
    orbits: list[list[int]],
    value_by_mask: dict[int, dict[str, Any]],
    label_specs: list[tuple[str, Callable[[dict[str, Any]], Any]]],
) -> list[dict[str, Any]]:
    rows = []
    for name, value_fn in label_specs:
        coherent = 0
        breaking_examples = []
        for orbit in orbits:
            values = [value_fn(value_by_mask[mask]) for mask in orbit]
            canonical_values = {canonical(value) for value in values}
            if len(canonical_values) == 1:
                coherent += 1
            elif len(breaking_examples) < 8:
                breaking_examples.append({"target_masks": orbit, "values": values})
        breaking = len(orbits) - coherent
        rows.append(
            {
                "label": name,
                "coherent_orbit_count": coherent,
                "breaking_orbit_count": breaking,
                "verdict": (
                    "retained_by_full_c2_quotient"
                    if breaking == 0
                    else "must_be_forgotten_or_restricted_for_full_c2_quotient"
                ),
                "first_breaking_examples": breaking_examples,
            }
        )
    return rows


def build_value_by_mask(
    path_rows: list[dict[str, Any]],
    mode_by_mask: dict[int, dict[str, Any]],
) -> dict[int, dict[str, Any]]:
    values = {}
    for row in path_rows:
        mask = int(row["target_mask"])
        mode = mode_by_mask[mask]
        fourier_signature = [
            mode["support_weight"],
            mode["active_step_atom_count"],
            mode["sector26_optical_clock_mod26"],
            mode["adjacency_eigenvalue"],
            mode["laplacian_eigenvalue"],
            mode["gamma8_support"],
            mode["gamma8_translation_eigenvalue"],
            mode["hidden_projection_type"],
        ]
        values[mask] = {
            "target_identity": mask,
            "exact_generator_support": row["toggle_generator_ids"],
            "shortest_step_count": row["shortest_step_count"],
            "shortest_path_action": row["shortest_path_action"],
            "target_height_action": row["target_height_action"],
            "target_hidden_packet": row["target_hidden_packet"],
            "target_corrected_R33_mod26": row["target_corrected_R33_mod26"],
            "public_balance_error": row["public_balance_error"],
            "hidden_balance_error": row["hidden_balance_error"],
            "support_weight": mode["support_weight"],
            "active_step_atom_count": mode["active_step_atom_count"],
            "active_step_atom_ids": mode["active_step_atom_ids"],
            "support_generator_ids": mode["support_generator_ids"],
            "negative_ordered_step_chain_class_ids": mode[
                "negative_ordered_step_chain_class_ids"
            ],
            "sector26_optical_clock_mod26": mode["sector26_optical_clock_mod26"],
            "corrected_hidden_clock_mod26": mode["corrected_hidden_clock_mod26"],
            "adjacency_eigenvalue": mode["adjacency_eigenvalue"],
            "laplacian_eigenvalue": mode["laplacian_eigenvalue"],
            "gamma8_support": mode["gamma8_support"],
            "gamma8_translation_eigenvalue": mode["gamma8_translation_eigenvalue"],
            "hidden_projection_type": mode["hidden_projection_type"],
            "fourier_signature": fourier_signature,
        }
    return values


def build_theorem() -> dict[str, Any]:
    shortest_paths = load_json(SOURCED_BALANCE_SHORTEST_PATHS_REPORT)
    transport_families = load_json(SOURCED_BALANCE_TRANSPORT_FAMILIES_REPORT)
    fourier_classifier = load_json(AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER_REPORT)
    hidden_split_symmetry = load_json(GLOBAL_CORRECTED_HIDDEN_SPLIT_SYMMETRY_REPORT)
    augmented_stabilizer = load_json(HIDDEN_SPLIT_AUGMENTED_LEDGER_STABILIZER_REPORT)

    path_rows = shortest_paths.get("derived", {}).get("shortest_path_rows", [])
    kernel_masks = {int(row["target_mask"]) for row in path_rows}
    mode_rows = fourier_classifier.get("derived", {}).get("mode_rows", [])
    mode_by_mask = {int(row["mode_mask"]): row for row in mode_rows}
    value_by_mask = build_value_by_mask(path_rows, mode_by_mask)

    hidden_split = hidden_split_symmetry.get("derived", {}).get("hidden_split", {})
    coefficients = [int(value) for value in hidden_split.get("coefficient_vector_over_f2", [])]
    public_records = reconstruct_public_automorphism_records(coefficients)
    hidden_preservers = [record for record in public_records if record["preserves_hidden_split"]]
    source_stabilizer = [
        record
        for record in public_records
        if apply_linear_image(GAMMA8_MASK, record["basis_image_masks"]) == GAMMA8_MASK
    ]
    source_kernel_preservers = [
        record
        for record in source_stabilizer
        if {apply_linear_image(mask, record["basis_image_masks"]) for mask in kernel_masks}
        == kernel_masks
    ]

    c2_orbits = orbit_rows(kernel_masks, hidden_preservers)
    source_public_closure = closure(kernel_masks, source_stabilizer)
    source_public_orbits = orbit_rows(source_public_closure, source_stabilizer)
    public_closure = closure(kernel_masks, public_records)
    public_orbits = orbit_rows(public_closure, public_records)

    label_specs: list[tuple[str, Callable[[dict[str, Any]], Any]]] = [
        ("target_identity", lambda row: row["target_identity"]),
        ("exact_generator_support", lambda row: row["exact_generator_support"]),
        ("shortest_step_count", lambda row: row["shortest_step_count"]),
        ("support_weight", lambda row: row["support_weight"]),
        ("adjacency_eigenvalue", lambda row: row["adjacency_eigenvalue"]),
        ("laplacian_eigenvalue", lambda row: row["laplacian_eigenvalue"]),
        ("shortest_path_action", lambda row: row["shortest_path_action"]),
        ("target_height_action", lambda row: row["target_height_action"]),
        ("active_step_atom_count", lambda row: row["active_step_atom_count"]),
        ("sector26_optical_clock_mod26", lambda row: row["sector26_optical_clock_mod26"]),
        ("support_generator_ids", lambda row: row["support_generator_ids"]),
        ("active_step_atom_ids", lambda row: row["active_step_atom_ids"]),
        (
            "negative_ordered_step_chain_class_ids",
            lambda row: row["negative_ordered_step_chain_class_ids"],
        ),
        ("fourier_signature", lambda row: row["fourier_signature"]),
        ("target_hidden_packet", lambda row: row["target_hidden_packet"]),
        ("target_corrected_R33_mod26", lambda row: row["target_corrected_R33_mod26"]),
        ("corrected_hidden_clock_mod26", lambda row: row["corrected_hidden_clock_mod26"]),
        ("gamma8_support", lambda row: row["gamma8_support"]),
        ("gamma8_translation_eigenvalue", lambda row: row["gamma8_translation_eigenvalue"]),
        ("hidden_projection_type", lambda row: row["hidden_projection_type"]),
        ("public_balance_error", lambda row: row["public_balance_error"]),
        ("hidden_balance_error", lambda row: row["hidden_balance_error"]),
    ]
    c2_label_coherence = label_coherence(c2_orbits, value_by_mask, label_specs)
    coherence_by_label = {row["label"]: row for row in c2_label_coherence}

    nonidentity_ledger = next(
        (
            record
            for record in augmented_stabilizer.get("derived", {}).get("candidate_records", [])
            if record.get("is_identity") is False
        ),
        {},
    )
    ledger_failures = nonidentity_ledger.get("failures", {})
    ledger_must_forget = sorted(label for label, witness in ledger_failures.items() if witness)
    ledger_retained = sorted(label for label, witness in ledger_failures.items() if not witness)
    retained_c2_labels = sorted(
        row["label"] for row in c2_label_coherence if row["breaking_orbit_count"] == 0
    )
    forgotten_c2_labels = sorted(
        row["label"] for row in c2_label_coherence if row["breaking_orbit_count"] > 0
    )

    quotient_ladder = [
        {
            "level": "full_augmented_ledger",
            "group_order": 1,
            "domain": "nonzero Ward-kernel gamma8 targets",
            "domain_size": len(kernel_masks),
            "orbit_count": len(kernel_masks),
            "nontrivial": False,
            "retained_labels": "all certified action/charge/counterterm/transport labels",
            "must_forget": [],
        },
        {
            "level": "hidden_split_c2_transport_topology",
            "group_order": len(hidden_preservers),
            "domain": "nonzero Ward-kernel gamma8 targets",
            "domain_size": len(kernel_masks),
            "orbit_count": len(c2_orbits),
            "orbit_size_histogram": size_histogram(c2_orbits),
            "nontrivial": True,
            "retained_labels": retained_c2_labels,
            "must_forget": forgotten_c2_labels + ledger_must_forget,
        },
        {
            "level": "source_fixed_public_mask_closure",
            "group_order": len(source_stabilizer),
            "domain": "public source-fixed closure of the nonzero Ward-kernel targets",
            "domain_size": len(source_public_closure),
            "orbit_count": len(source_public_orbits),
            "orbit_size_histogram": size_histogram(source_public_orbits),
            "nontrivial": True,
            "retained_labels": ["gamma8 source anchor", "public residue-mask action"],
            "must_forget": [
                "Ward-kernel target-domain restriction",
                "hidden packet split",
                "corrected R33 kernel clock",
                "sourced-balance action-height labels on the original kernel atlas",
            ],
        },
        {
            "level": "full_public_residue_mask_action",
            "group_order": len(public_records),
            "domain": "all nonzero closed-return residue masks",
            "domain_size": len(public_closure),
            "orbit_count": len(public_orbits),
            "orbit_size_histogram": size_histogram(public_orbits),
            "nontrivial": True,
            "retained_labels": ["public graph/residue-mask action"],
            "must_forget": [
                "gamma8 source anchor",
                "Ward-kernel target-domain restriction",
                "hidden packet split",
                "corrected R33 kernel clock",
                "full action/charge/counterterm ledger",
            ],
        },
    ]

    public_level_summary = {
        "public_automorphism_count": len(public_records),
        "source_stabilizer_count": len(source_stabilizer),
        "kernel_target_preserving_public_count": sum(
            1
            for record in public_records
            if {apply_linear_image(mask, record["basis_image_masks"]) for mask in kernel_masks}
            == kernel_masks
        ),
        "source_and_kernel_target_preserving_count": len(source_kernel_preservers),
        "source_stabilizer_automorphism_ids": [
            record["automorphism_id"] for record in source_stabilizer
        ],
        "source_kernel_preserving_automorphism_ids": [
            record["automorphism_id"] for record in source_kernel_preservers
        ],
        "source_fixed_public_closure_size": len(source_public_closure),
        "source_fixed_public_closure_missing_nonzero_mask_count": len(
            NONZERO_MASKS - source_public_closure
        ),
        "source_fixed_public_orbit_count": len(source_public_orbits),
        "source_fixed_public_orbit_size_histogram": size_histogram(source_public_orbits),
        "full_public_closure_size": len(public_closure),
        "full_public_orbit_count": len(public_orbits),
        "full_public_orbit_size_histogram": size_histogram(public_orbits),
    }
    label_relaxation_summary = {
        "nonzero_kernel_target_count": len(kernel_masks),
        "hidden_split_c2_orbit_count": len(c2_orbits),
        "hidden_split_c2_orbit_size_histogram": size_histogram(c2_orbits),
        "retained_by_full_c2_quotient": retained_c2_labels,
        "must_forget_for_full_c2_quotient": forgotten_c2_labels,
        "ledger_retained_by_nonidentity_c2": ledger_retained,
        "ledger_must_forget_for_nonidentity_c2": ledger_must_forget,
        "minimal_nontrivial_transport_quotient": (
            "Keep gamma8 source anchoring plus the corrected hidden split/R33 packet labels, and forget "
            "target identity, exact support, step/action/height, Fourier/sector-26 clock refinements, "
            "public charge/flux labels, counterterms, and interface/action weights."
        ),
    }

    expected_public_sha = hidden_split_symmetry.get("derived", {}).get(
        "all_automorphism_records_sha256"
    )
    checks = {
        "shortest_paths_is_certified": shortest_paths.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_SHORTEST_PATHS_CERTIFIED"
        and shortest_paths.get("all_checks_pass") is True,
        "transport_families_is_certified": transport_families.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_TRANSPORT_FAMILIES_CERTIFIED"
        and transport_families.get("all_checks_pass") is True,
        "fourier_mode_classifier_is_certified": fourier_classifier.get("status")
        == "D20_AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER_CERTIFIED"
        and fourier_classifier.get("all_checks_pass") is True,
        "global_hidden_split_symmetry_is_certified": hidden_split_symmetry.get("status")
        == "D20_GLOBAL_CORRECTED_HIDDEN_SPLIT_SYMMETRY_CERTIFIED"
        and hidden_split_symmetry.get("all_checks_pass") is True,
        "augmented_ledger_stabilizer_is_certified": augmented_stabilizer.get("status")
        == "D20_HIDDEN_SPLIT_AUGMENTED_LEDGER_STABILIZER_CERTIFIED"
        and augmented_stabilizer.get("all_checks_pass") is True,
        "reconstructed_public_automorphism_records_match_hidden_split_report": len(public_records)
        == 120
        and sha_json(public_records) == expected_public_sha,
        "source_and_kernel_target_preserving_group_is_hidden_split_c2": len(source_stabilizer)
        == 10
        and len(hidden_preservers) == 2
        and len(source_kernel_preservers) == 2
        and [record["automorphism_id"] for record in source_kernel_preservers] == [0, 1],
        "hidden_split_c2_quotient_has_543_kernel_target_orbits": len(c2_orbits) == 543
        and size_histogram(c2_orbits) == {"1": 63, "2": 480},
        "hidden_split_c2_retains_hidden_packet_and_corrected_clock_labels": all(
            coherence_by_label[label]["breaking_orbit_count"] == 0
            for label in (
                "target_hidden_packet",
                "target_corrected_R33_mod26",
                "corrected_hidden_clock_mod26",
                "gamma8_support",
                "gamma8_translation_eigenvalue",
                "hidden_projection_type",
            )
        ),
        "hidden_split_c2_forgets_target_support_step_action_height_and_fourier_refinements": (
            coherence_by_label["target_identity"]["breaking_orbit_count"] == 480
            and coherence_by_label["exact_generator_support"]["breaking_orbit_count"] == 480
            and coherence_by_label["shortest_step_count"]["breaking_orbit_count"] == 128
            and coherence_by_label["shortest_path_action"]["breaking_orbit_count"] == 472
            and coherence_by_label["target_height_action"]["breaking_orbit_count"] == 472
            and coherence_by_label["sector26_optical_clock_mod26"]["breaking_orbit_count"] == 468
            and coherence_by_label["fourier_signature"]["breaking_orbit_count"] == 479
        ),
        "nonidentity_c2_requires_forgetting_six_augmented_ledger_axes": ledger_must_forget
        == [
            "edge_interface_weights",
            "normalized_optical_clock_mod26",
            "primitive_optical_action_weights",
            "public_oriented_edge_flux_components",
            "public_state_charge_components",
            "sector26_counterterm_vector_mod26",
        ]
        and ledger_retained == ["corrected_clock_mod26"],
        "source_fixed_public_quotient_requires_enlarged_domain": len(source_public_closure)
        == 1983
        and len(source_public_orbits) == 255
        and size_histogram(source_public_orbits) == {"1": 3, "5": 108, "10": 144},
        "full_public_quotient_requires_forgetting_source_anchor": len(public_closure) == 2047
        and len(public_orbits) == 45
        and size_histogram(public_orbits)
        == {"6": 3, "10": 3, "12": 2, "15": 1, "20": 2, "30": 8, "60": 24, "120": 2},
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_LABEL_RELAXED_ORBIT_QUOTIENT_CERTIFIED"
        if all_checks_pass
        else "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_LABEL_RELAXED_ORBIT_QUOTIENT_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient",
        "status": status,
        "object": "d20",
        "claim": (
            "A nontrivial gamma8-sourced transport quotient exists exactly at the label-relaxed "
            "hidden-split C2 level. It keeps the corrected hidden packet/R33 split and gamma8 source "
            "anchor, but must forget target identity, exact generator support, step/action/height data, "
            "Fourier and sector-26 clock refinements, and the full public action/charge/counterterm ledger. "
            "Larger public quotients exist only after enlarging the target domain and eventually forgetting "
            "the gamma8 source anchor itself."
        ),
        "definition": {
            "label_relaxed_transport_quotient": (
                "An orbit quotient of the gamma8-sourced nonzero Ward-kernel target atlas by a certified "
                "D20 automorphism subgroup after retaining only labels that are constant on every orbit."
            ),
            "must_forget_label": (
                "A label that takes at least two values on some orbit of the proposed nontrivial quotient."
            ),
            "source_fixed_public_closure": (
                "The closure of the nonzero Ward-kernel target set under public graph automorphisms that "
                "fix gamma8 in the 11-bit closed-return residue action."
            ),
        },
        "inputs": {
            "sourced_balance_shortest_paths_report": {
                "path": rel(SOURCED_BALANCE_SHORTEST_PATHS_REPORT),
                "sha256": sha_file(SOURCED_BALANCE_SHORTEST_PATHS_REPORT),
            },
            "sourced_balance_transport_families_report": {
                "path": rel(SOURCED_BALANCE_TRANSPORT_FAMILIES_REPORT),
                "sha256": sha_file(SOURCED_BALANCE_TRANSPORT_FAMILIES_REPORT),
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
            "label_relaxation_summary": label_relaxation_summary,
            "public_level_summary": public_level_summary,
            "quotient_ladder": quotient_ladder,
            "hidden_split_c2_label_coherence": c2_label_coherence,
            "hidden_split_c2_orbits_sha256": sha_json(c2_orbits),
            "source_fixed_public_orbits_sha256": sha_json(source_public_orbits),
            "full_public_orbits_sha256": sha_json(public_orbits),
        },
        "interpretation": {
            "what_this_proves": [
                "the full action/charge ledger has no nontrivial quotient symmetry",
                "the smallest nontrivial gamma8-sourced transport quotient is the hidden-split C2 quotient",
                "that C2 quotient is not action-, height-, step-, support-, or Fourier-coherent on the full target set",
                "public source-fixed symmetry is larger only after dropping the Ward-kernel target-domain restriction",
                "the full public 120-action is recovered only after dropping the gamma8 source anchor too",
            ],
            "what_this_does_not_prove": (
                "This does not make action or height descend to the C2 quotient. Their failures are now "
                "classified as label-breaking data; turning them into a quotient cocycle is a separate theorem."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Promote the C2 action/height label-breaking table to a quotient anomaly or cocycle and test "
            "whether sourced Ward/BMS balance descends after adding that cocycle."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {k: v for k, v in report.items() if k != "certificate_sha256"}
    )
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": (
            "d20.theorem.full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient_manifest"
        ),
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify shortest-path, transport-family, Fourier, hidden-split, and augmented-ledger inputs",
            "reconstruct the 120 public automorphisms and verify their hash against the hidden-split theorem",
            "identify the gamma8 source stabilizer and its kernel-target preserving subgroup",
            "compute hidden-split C2 orbits on the 1023 nonzero Ward-kernel targets",
            "classify which transport/Fourier labels are constant on every C2 orbit",
            "verify the six augmented-ledger axes broken by the nonidentity C2 automorphism",
            "compute source-fixed public and full-public residue-mask quotient levels",
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
