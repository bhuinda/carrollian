from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "full_exposure_zero_pair_ward_kernel_height_selector"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

ZERO_PAIR_SOURCE_TO_CLOSED_RETURN_COUPLING_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_source_to_closed_return_coupling"
    / "report.json"
)
CANONICAL_ALL_MASK_WARD_IDENTITY_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "canonical_all_mask_ward_identity"
    / "report.json"
)
SECTOR33_ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "sector33_all_residue_height_transport"
    / "report.json"
)
COMPACT_AMPLITUDE_QUOTIENT_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "compact_amplitude_quotient"
    / "report.json"
)
AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "amplitude_quotient_fourier_mode_classifier"
    / "report.json"
)


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


def mask_bits(mask: int, rank: int = 11) -> list[int]:
    return [idx for idx in range(rank) if mask & (1 << idx)]


def sorted_top_candidates(
    kernel_masks: list[int],
    height_by_mask: dict[int, dict[str, Any]],
    mode_by_mask: dict[int, dict[str, Any]],
    limit: int = 12,
) -> list[dict[str, Any]]:
    def key(mask: int) -> tuple[int, int, int, int, int]:
        height_row = height_by_mask[mask]
        mode_row = mode_by_mask[mask]
        return (
            int(height_row["height_action"]),
            int(mode_row["active_step_atom_count"]),
            int(height_row["active_edge_count"]),
            int(mode_row["support_weight"]),
            mask,
        )

    rows = []
    for mask in sorted(kernel_masks, key=key)[:limit]:
        height_row = height_by_mask[mask]
        mode_row = mode_by_mask[mask]
        rows.append(
            {
                "mask": mask,
                "basis_cycle_ids": height_row["basis_cycle_ids"],
                "height_action": height_row["height_action"],
                "active_edge_count": height_row["active_edge_count"],
                "active_step_atom_count": mode_row["active_step_atom_count"],
                "support_weight": mode_row["support_weight"],
                "gamma8_support": mode_row["gamma8_support"],
                "sector26_optical_clock_mod26": mode_row["sector26_optical_clock_mod26"],
            }
        )
    return rows


def histogram(values: list[int]) -> dict[str, int]:
    out: dict[str, int] = {}
    for value in values:
        key = str(value)
        out[key] = out.get(key, 0) + 1
    return dict(sorted(out.items(), key=lambda item: int(item[0])))


def build_theorem() -> dict[str, Any]:
    source_coupling = load_json(ZERO_PAIR_SOURCE_TO_CLOSED_RETURN_COUPLING_REPORT)
    ward = load_json(CANONICAL_ALL_MASK_WARD_IDENTITY_REPORT)
    height = load_json(SECTOR33_ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT)
    compact = load_json(COMPACT_AMPLITUDE_QUOTIENT_REPORT)
    fourier = load_json(AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER_REPORT)

    ward_rows = ward.get("derived", {}).get("ward_rows", [])
    transport_rows = height.get("derived", {}).get("transport_rows", [])
    mode_rows = fourier.get("derived", {}).get("mode_rows", [])
    generator_rows = compact.get("derived", {}).get("generator_quotient_rows", [])

    height_by_mask = {int(row["mask"]): row for row in transport_rows}
    mode_by_mask = {int(row["mode_mask"]): row for row in mode_rows}
    generator_by_id = {int(row["generator_cycle_id"]): row for row in generator_rows}
    ward_by_mask = {int(row["mask"]): row for row in ward_rows}

    kernel_masks = sorted(
        int(row["mask"]) for row in ward_rows if row.get("in_global_corrected_kernel") is True
    )
    nonzero_kernel_masks = [mask for mask in kernel_masks if mask != 0]
    min_positive_height = min(int(height_by_mask[mask]["height_action"]) for mask in nonzero_kernel_masks)
    min_positive_masks = [
        mask
        for mask in nonzero_kernel_masks
        if int(height_by_mask[mask]["height_action"]) == min_positive_height
    ]
    selected_mask = min_positive_masks[0] if len(min_positive_masks) == 1 else None

    gamma8_bit = 1 << 8
    gamma8_supported_kernel_masks = [mask for mask in nonzero_kernel_masks if mask & gamma8_bit]
    gamma8_supported_min_height = min(
        int(height_by_mask[mask]["height_action"]) for mask in gamma8_supported_kernel_masks
    )
    gamma8_supported_min_masks = [
        mask
        for mask in gamma8_supported_kernel_masks
        if int(height_by_mask[mask]["height_action"]) == gamma8_supported_min_height
    ]
    gamma8_free_kernel_masks = [mask for mask in nonzero_kernel_masks if not (mask & gamma8_bit)]
    gamma8_free_min_height = min(
        int(height_by_mask[mask]["height_action"]) for mask in gamma8_free_kernel_masks
    )
    gamma8_free_min_masks = [
        mask
        for mask in gamma8_free_kernel_masks
        if int(height_by_mask[mask]["height_action"]) == gamma8_free_min_height
    ]

    selected_height_row = height_by_mask.get(selected_mask, {})
    selected_mode_row = mode_by_mask.get(selected_mask, {})
    cycle5_row = generator_by_id.get(5, {})
    gamma8_row = compact.get("derived", {}).get("gamma8_quotient_row", {})
    cycle5_atoms = set(cycle5_row.get("step_atom_ids_ordered", []))
    gamma8_atoms = set(gamma8_row.get("step_atom_ids_ordered", []))
    shared_atoms = sorted(cycle5_atoms & gamma8_atoms)
    selected_atom_union = sorted(cycle5_atoms | gamma8_atoms)
    basis_heights = height.get("derived", {}).get("basis_cycle_height_vector", [])
    basis_clocks = ward.get("derived", {}).get("global_corrected_character", {}).get(
        "basis_clock_mod26", []
    )
    source_coupling_summary = source_coupling.get("derived", {}).get("coupling_summary", {})

    selector_summary = {
        "selector_rule": (
            "choose the unique nonzero all-mask Ward-kernel mask with minimal certified positive "
            "height_action"
        ),
        "selected_mask": selected_mask,
        "selected_basis_cycle_ids": selected_height_row.get("basis_cycle_ids"),
        "selected_height_action": selected_height_row.get("height_action"),
        "selected_is_nontrivial": selected_mask not in (None, 0),
        "selected_in_ward_kernel": ward_by_mask.get(selected_mask, {}).get(
            "in_global_corrected_kernel"
        ),
        "selected_corrected_clock_mod26": ward_by_mask.get(selected_mask, {}).get(
            "corrected_clock_mod26"
        ),
        "height_decomposition": {
            "cycle5_height_action": basis_heights[5] if len(basis_heights) > 5 else None,
            "gamma8_height_action": basis_heights[8] if len(basis_heights) > 8 else None,
            "sum": (basis_heights[5] + basis_heights[8]) if len(basis_heights) > 8 else None,
        },
        "ward_clock_decomposition_mod26": {
            "cycle5_corrected_clock": basis_clocks[5] if len(basis_clocks) > 5 else None,
            "gamma8_corrected_clock": basis_clocks[8] if len(basis_clocks) > 8 else None,
            "sum_mod26": (
                (int(basis_clocks[5]) + int(basis_clocks[8])) % 26
                if len(basis_clocks) > 8
                else None
            ),
        },
        "minimality_witness": {
            "nonzero_kernel_mask_count": len(nonzero_kernel_masks),
            "min_positive_height": min_positive_height,
            "min_positive_masks": min_positive_masks,
            "gamma8_supported_kernel_mask_count": len(gamma8_supported_kernel_masks),
            "gamma8_supported_min_height": gamma8_supported_min_height,
            "gamma8_supported_min_masks": gamma8_supported_min_masks,
            "gamma8_free_min_height": gamma8_free_min_height,
            "gamma8_free_min_masks": gamma8_free_min_masks,
        },
        "compact_exposure_witness": {
            "selected_active_step_atom_ids": selected_mode_row.get("active_step_atom_ids"),
            "selected_active_step_atom_count": selected_mode_row.get("active_step_atom_count"),
            "selected_support_weight": selected_mode_row.get("support_weight"),
            "selected_sector26_optical_clock_mod26": selected_mode_row.get(
                "sector26_optical_clock_mod26"
            ),
            "selected_adjacency_eigenvalue": selected_mode_row.get("adjacency_eigenvalue"),
            "selected_laplacian_eigenvalue": selected_mode_row.get("laplacian_eigenvalue"),
            "cycle5_step_atom_ids": cycle5_row.get("step_atom_ids_ordered"),
            "gamma8_step_atom_ids": gamma8_row.get("step_atom_ids_ordered"),
            "shared_step_atom_ids": shared_atoms,
            "union_step_atom_ids": selected_atom_union,
        },
        "source_lift": {
            "source_id": "paired_plus_minus_neutral_source",
            "previous_canonical_minimal_mask": source_coupling_summary.get(
                "canonical_trivial_coupling", {}
            ).get("closed_return_mask"),
            "height_selected_nontrivial_mask": selected_mask,
            "individual_plus_minus_sources_remain_no_go": source_coupling.get("checks", {}).get(
                "individual_plus_minus_couplings_are_impossible"
            ),
        },
    }

    selector_candidates = sorted_top_candidates(
        nonzero_kernel_masks,
        height_by_mask,
        mode_by_mask,
    )
    height_histogram_head = histogram(
        sorted({int(height_by_mask[mask]["height_action"]) for mask in nonzero_kernel_masks})[:16]
    )

    checks = {
        "source_to_closed_return_coupling_is_certified": source_coupling.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCE_TO_CLOSED_RETURN_COUPLING_CERTIFIED"
        and source_coupling.get("all_checks_pass") is True,
        "canonical_all_mask_ward_identity_is_certified": ward.get("status")
        == "D20_CANONICAL_ALL_MASK_WARD_IDENTITY_CERTIFIED"
        and ward.get("all_checks_pass") is True,
        "all_residue_height_transport_is_certified": height.get("status")
        == "D20_ALL_RESIDUE_HEIGHT_COHERENT_TRANSPORT_CERTIFIED"
        and height.get("all_checks_pass") is True,
        "compact_amplitude_quotient_is_certified": compact.get("status")
        == "D20_COMPACT_AMPLITUDE_QUOTIENT_CERTIFIED"
        and compact.get("all_checks_pass") is True,
        "amplitude_quotient_fourier_classifier_is_certified": fourier.get("status")
        == "D20_AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER_CERTIFIED"
        and fourier.get("all_checks_pass") is True,
        "ward_kernel_mask_set_has_expected_size": len(kernel_masks) == 1024
        and len(nonzero_kernel_masks) == 1023
        and 0 in kernel_masks,
        "selector_has_unique_minimum_positive_kernel_action": min_positive_masks == [288]
        and min_positive_height == 1065984,
        "selected_mask_is_nonzero_ward_kernel_mask": selected_mask == 288
        and ward_by_mask.get(288, {}).get("in_global_corrected_kernel") is True
        and ward_by_mask.get(288, {}).get("corrected_clock_mod26") == 0,
        "selected_mask_is_gamma8_plus_cycle5": selected_height_row.get("basis_cycle_ids")
        == [5, 8]
        and selected_mask == (1 << 5) + (1 << 8)
        and gamma8_supported_min_masks == [288],
        "selected_height_decomposes_as_cycle5_plus_gamma8": basis_heights[5] == 691200
        and basis_heights[8] == 374784
        and basis_heights[5] + basis_heights[8] == selected_height_row.get("height_action"),
        "selected_clock_is_pairwise_ward_neutral": basis_clocks[5] == 13
        and basis_clocks[8] == 13
        and (basis_clocks[5] + basis_clocks[8]) % 26 == 0,
        "compact_exposure_matches_cycle5_gamma8_union": selected_mode_row.get(
            "active_step_atom_ids"
        )
        == selected_atom_union
        and selected_mode_row.get("active_step_atom_count") == 9
        and selected_mode_row.get("support_weight") == 2
        and shared_atoms == [11],
        "selected_mask_is_nontrivial_sourced_ward_lift": source_coupling_summary.get(
            "canonical_trivial_coupling", {}
        ).get("closed_return_mask")
        == 0
        and selected_mask == 288
        and selected_mask != 0
        and selected_height_row.get("height_action", 0) > 0,
        "individual_source_no_go_remains_in_force": source_coupling.get("checks", {}).get(
            "individual_plus_minus_couplings_are_impossible"
        )
        is True,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FULL_EXPOSURE_ZERO_PAIR_WARD_KERNEL_HEIGHT_SELECTOR_CERTIFIED"
        if all_checks_pass
        else "D20_FULL_EXPOSURE_ZERO_PAIR_WARD_KERNEL_HEIGHT_SELECTOR_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.full_exposure_zero_pair_ward_kernel_height_selector",
        "status": status,
        "object": "d20",
        "claim": (
            "The paired neutral zero-pair source has a canonical nontrivial closed-return lift once the "
            "certified action-height selector is admitted. Among all 1023 nonzero all-mask Ward-kernel "
            "masks, the unique minimum positive height is mask 288 = cycle5 + gamma8, with height "
            "691200 + 374784 = 1065984 and corrected Ward clock 0."
        ),
        "definition": {
            "ward_kernel_height_selector": (
                "Sel_h(K) is the unique nonzero mask in the all-mask Ward kernel minimizing the certified "
                "height_action from all-residue height-coherent transport."
            ),
            "nontrivial_sourced_ward_lift": (
                "A lift of the paired neutral packet-source residue to a nonzero closed-return Ward-kernel "
                "mask selected by an invariant rule."
            ),
            "compact_exposure_witness": (
                "The amplitude-quotient Fourier exposure of the selected mask, checked against the compact "
                "generator step atoms for cycle 5 and gamma8."
            ),
        },
        "inputs": {
            "zero_pair_source_to_closed_return_coupling_report": {
                "path": rel(ZERO_PAIR_SOURCE_TO_CLOSED_RETURN_COUPLING_REPORT),
                "sha256": sha_file(ZERO_PAIR_SOURCE_TO_CLOSED_RETURN_COUPLING_REPORT),
            },
            "canonical_all_mask_ward_identity_report": {
                "path": rel(CANONICAL_ALL_MASK_WARD_IDENTITY_REPORT),
                "sha256": sha_file(CANONICAL_ALL_MASK_WARD_IDENTITY_REPORT),
            },
            "sector33_all_residue_height_transport_report": {
                "path": rel(SECTOR33_ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT),
                "sha256": sha_file(SECTOR33_ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT),
            },
            "compact_amplitude_quotient_report": {
                "path": rel(COMPACT_AMPLITUDE_QUOTIENT_REPORT),
                "sha256": sha_file(COMPACT_AMPLITUDE_QUOTIENT_REPORT),
            },
            "amplitude_quotient_fourier_mode_classifier_report": {
                "path": rel(AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER_REPORT),
                "sha256": sha_file(AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER_REPORT),
            },
        },
        "derived": {
            "selector_summary": selector_summary,
            "selector_candidates_by_height": selector_candidates,
            "height_action_unique_value_head_histogram": height_histogram_head,
        },
        "interpretation": {
            "what_this_proves": [
                "the neutral paired source can be lifted nontrivially after adding the certified action-height selector",
                "the selected nonzero Ward-kernel mask is unique and equals cycle5 plus gamma8",
                "the selection is not a bare source-residue fact; it depends on the height/action structure",
                "individual plus and minus source residues still cannot be lifted as Ward characters",
            ],
            "what_this_does_not_prove": (
                "This does not yet prove a full sourced Ward balance law with charge update. It selects the "
                "closed-return mask that such a sourced law should test next."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Propagate the selected mask 288 through the finite BMS/Carrollian charge ledger and scattering "
            "automaton to certify the first nontrivial sourced Ward balance."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {k: v for k, v in report.items() if k != "certificate_sha256"}
    )
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.full_exposure_zero_pair_ward_kernel_height_selector_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify source-coupling, all-mask Ward, all-residue height, compact quotient, and Fourier inputs",
            "enumerate the all-mask Ward kernel and remove the zero mask",
            "find the unique minimum positive height_action on the nonzero Ward kernel",
            "verify the selected mask is 288 = cycle5 + gamma8",
            "verify the selected height decomposes as 691200 + 374784",
            "verify the selected Ward clock is neutral because 13 + 13 = 0 mod 26",
            "verify compact amplitude exposure matches the cycle5/gamma8 step-atom union",
            "verify individual source residues remain no-go while the paired source has a nontrivial selected lift",
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
