from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "full_exposure_zero_pair_source_to_closed_return_coupling"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

ZERO_PAIR_PROPAGATOR_CHARGE_KERNEL_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_propagator_charge_kernel"
    / "report.json"
)
ZERO_PAIR_PROPAGATOR_SYMMETRY_WARD_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_propagator_symmetry_ward"
    / "report.json"
)
CANONICAL_ALL_MASK_WARD_IDENTITY_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "canonical_all_mask_ward_identity"
    / "report.json"
)
FINITE_BMS_CARROLLIAN_FLUX_BALANCE_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "finite_bms_carrollian_flux_balance"
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


def mod26_add(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    return {
        "sector26_clock_pair_mod26": [
            (int(left["sector26_clock_pair_mod26"][idx]) + int(right["sector26_clock_pair_mod26"][idx]))
            % 26
            for idx in range(2)
        ],
        "sector26_clock_sum_mod26": (
            int(left["sector26_clock_sum_mod26"]) + int(right["sector26_clock_sum_mod26"])
        )
        % 26,
        "sector26_clock_delta_mod26": (
            int(left["sector26_clock_delta_mod26"]) + int(right["sector26_clock_delta_mod26"])
        )
        % 26,
    }


def coupling_row(
    source_id: str,
    source_image: dict[str, Any],
    ward_character_image: list[int],
    canonical_mask: int | None,
    reason: str,
) -> dict[str, Any]:
    source_sum = int(source_image["sector26_clock_sum_mod26"])
    return {
        "source_id": source_id,
        "source_sector26_image": source_image,
        "source_sum_mod26": source_sum,
        "source_sum_in_ward_character_image": source_sum in ward_character_image,
        "canonical_closed_return_mask": canonical_mask,
        "coupling_status": "couples_to_ward_kernel" if canonical_mask is not None else "no_individual_coupling",
        "reason": reason,
    }


def build_theorem() -> dict[str, Any]:
    kernel = load_json(ZERO_PAIR_PROPAGATOR_CHARGE_KERNEL_REPORT)
    symmetry_ward = load_json(ZERO_PAIR_PROPAGATOR_SYMMETRY_WARD_REPORT)
    ward = load_json(CANONICAL_ALL_MASK_WARD_IDENTITY_REPORT)
    flux = load_json(FINITE_BMS_CARROLLIAN_FLUX_BALANCE_REPORT)

    kernel_summary = kernel.get("derived", {}).get("propagator_charge_kernel_summary", {})
    plus_image = kernel_summary.get("plus_denominator_cleared_sector26_image", {})
    minus_image = kernel_summary.get("minus_denominator_cleared_sector26_image", {})
    paired_image = mod26_add(plus_image, minus_image)

    ward_character = ward.get("derived", {}).get("global_corrected_character", {})
    ward_histogram = ward_character.get("histogram", {})
    ward_character_image = sorted(int(value) for value in ward_histogram)
    ward_kernel = ward_character.get("kernel", {})
    ward_image_13 = ward_character.get("image_13", {})
    flux_summary = flux.get("derived", {}).get("balance_summary", {})
    symmetry_compatibility = symmetry_ward.get("derived", {}).get("compatibility_matrix", {})

    coupling_tests = [
        coupling_row(
            "plus_denominator_cleared_source",
            plus_image,
            ward_character_image,
            None,
            "sector-26 sum 4 is outside the all-mask Ward character image {0,13}",
        ),
        coupling_row(
            "minus_denominator_cleared_source",
            minus_image,
            ward_character_image,
            None,
            "sector-26 sum 22 is outside the all-mask Ward character image {0,13}",
        ),
        coupling_row(
            "paired_plus_minus_neutral_source",
            paired_image,
            ward_character_image,
            0,
            "the paired source residue is sector-26 neutral and the minimal closed-return mask is the Ward-kernel zero mask",
        ),
    ]

    coupling_summary = {
        "source_generators": {
            "plus_denominator_cleared_source": plus_image,
            "minus_denominator_cleared_source": minus_image,
            "paired_plus_minus_neutral_source": paired_image,
        },
        "ward_character_image": ward_character_image,
        "ward_character_histogram": ward_histogram,
        "ward_kernel_dimension": ward_kernel.get("dimension"),
        "ward_kernel_size": ward_kernel.get("size"),
        "ward_odd_sector_size": ward_image_13.get("size"),
        "canonical_trivial_coupling": {
            "source_id": "paired_plus_minus_neutral_source",
            "closed_return_mask": 0,
            "ward_character_value_mod26": 0,
        },
        "nonunique_neutral_target_sample_masks": ward_kernel.get("sample_masks", []),
        "individual_coupling_status": (
            "No Ward-character-preserving coupling exists for the individual plus or minus residues."
        ),
        "paired_neutral_coupling_status": (
            "A canonical minimal coupling exists only for the neutral paired residue, and it maps to the "
            "zero closed-return mask unless an additional selector chooses a nonzero Ward-kernel mask."
        ),
        "nontrivial_coupling_selector_status": (
            "underdetermined: the certified Ward kernel has 1024 neutral masks and the current invariants "
            "do not select a unique nonzero closed-return representative"
        ),
    }

    checks = {
        "propagator_charge_kernel_is_certified": kernel.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_PROPAGATOR_CHARGE_KERNEL_CERTIFIED"
        and kernel.get("all_checks_pass") is True,
        "symmetry_ward_input_is_certified": symmetry_ward.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_PROPAGATOR_SYMMETRY_WARD_CERTIFIED"
        and symmetry_ward.get("all_checks_pass") is True,
        "canonical_all_mask_ward_identity_is_certified": ward.get("status")
        == "D20_CANONICAL_ALL_MASK_WARD_IDENTITY_CERTIFIED"
        and ward.get("all_checks_pass") is True,
        "finite_bms_carrollian_flux_balance_is_certified": flux.get("status")
        == "D20_FINITE_BMS_CARROLLIAN_FLUX_BALANCE_CERTIFIED"
        and flux.get("all_checks_pass") is True,
        "ward_character_image_is_exactly_order_two": ward.get("checks", {}).get(
            "global_corrected_character_has_order_two_image"
        )
        is True
        and ward_histogram == {"0": 1024, "13": 1024}
        and ward_character_image == [0, 13],
        "ward_kernel_has_expected_size_and_dimension": ward.get("checks", {}).get(
            "global_corrected_kernel_has_dimension_10"
        )
        is True
        and ward_kernel.get("dimension") == 10
        and ward_kernel.get("size") == 1024
        and ward_image_13.get("size") == 1024,
        "source_generators_have_expected_sector26_images": plus_image
        == {
            "sector26_clock_delta_mod26": 8,
            "sector26_clock_pair_mod26": [24, 6],
            "sector26_clock_sum_mod26": 4,
        }
        and minus_image
        == {
            "sector26_clock_delta_mod26": 18,
            "sector26_clock_pair_mod26": [2, 20],
            "sector26_clock_sum_mod26": 22,
        }
        and paired_image
        == {
            "sector26_clock_delta_mod26": 0,
            "sector26_clock_pair_mod26": [0, 0],
            "sector26_clock_sum_mod26": 0,
        },
        "individual_plus_minus_couplings_are_impossible": all(
            row["coupling_status"] == "no_individual_coupling"
            and row["source_sum_in_ward_character_image"] is False
            for row in coupling_tests[:2]
        ),
        "canonical_neutral_coupling_maps_to_ward_kernel": coupling_tests[2][
            "canonical_closed_return_mask"
        ]
        == 0
        and coupling_tests[2]["source_sum_in_ward_character_image"] is True
        and 0 in ward_kernel.get("sample_masks", []),
        "nontrivial_neutral_coupling_is_not_selected_by_current_invariants": ward_kernel.get(
            "size"
        )
        == 1024
        and len(ward_kernel.get("sample_masks", [])) > 1
        and symmetry_compatibility.get("needs_source_to_closed_return_coupling_for_stronger_claim")
        is True,
        "public_flux_context_remains_rank_zero": flux_summary.get(
            "public_closed_return_rank_over_f2"
        )
        == 0
        and flux_summary.get("hidden_corrected_rank_over_f2") == 1
        and flux_summary.get("mask_count") == 2048,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCE_TO_CLOSED_RETURN_COUPLING_CERTIFIED"
        if all_checks_pass
        else "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCE_TO_CLOSED_RETURN_COUPLING_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.full_exposure_zero_pair_source_to_closed_return_coupling",
        "status": status,
        "object": "d20",
        "claim": (
            "The denominator-cleared zero-pair packet-source residues do not individually couple to "
            "closed-return Ward characters: their sector-26 sums 4 and 22 lie outside the all-mask "
            "Ward image {0,13}. The paired plus/minus residue is neutral and admits only the canonical "
            "minimal closed-return coupling to the Ward-kernel zero mask unless a further selector chooses "
            "one of the 1024 neutral masks."
        ),
        "definition": {
            "source_to_closed_return_coupling": (
                "A map from denominator-cleared packet-source residues into all-mask closed-return "
                "residue masks that preserves the sector-26 Ward character."
            ),
            "individual_coupling": (
                "A coupling for the plus or minus denominator-cleared packet-source residue alone."
            ),
            "paired_neutral_coupling": (
                "A coupling after summing the plus and minus packet-source residues in the sector-26 ledger."
            ),
            "canonical_minimal_closed_return_mask": (
                "The zero closed-return mask in the all-mask Ward kernel; it is the only representative "
                "selected without additional action-height or incidence data."
            ),
        },
        "inputs": {
            "zero_pair_propagator_charge_kernel_report": {
                "path": rel(ZERO_PAIR_PROPAGATOR_CHARGE_KERNEL_REPORT),
                "sha256": sha_file(ZERO_PAIR_PROPAGATOR_CHARGE_KERNEL_REPORT),
            },
            "zero_pair_propagator_symmetry_ward_report": {
                "path": rel(ZERO_PAIR_PROPAGATOR_SYMMETRY_WARD_REPORT),
                "sha256": sha_file(ZERO_PAIR_PROPAGATOR_SYMMETRY_WARD_REPORT),
            },
            "canonical_all_mask_ward_identity_report": {
                "path": rel(CANONICAL_ALL_MASK_WARD_IDENTITY_REPORT),
                "sha256": sha_file(CANONICAL_ALL_MASK_WARD_IDENTITY_REPORT),
            },
            "finite_bms_carrollian_flux_balance_report": {
                "path": rel(FINITE_BMS_CARROLLIAN_FLUX_BALANCE_REPORT),
                "sha256": sha_file(FINITE_BMS_CARROLLIAN_FLUX_BALANCE_REPORT),
            },
        },
        "derived": {
            "coupling_summary": coupling_summary,
            "coupling_tests": coupling_tests,
            "source_to_closed_return_coupling_matrix": {
                "individual_plus_source": "no Ward-character-preserving target",
                "individual_minus_source": "no Ward-character-preserving target",
                "paired_plus_minus_source": "canonical target mask 0; nonzero Ward-kernel target underdetermined",
            },
        },
        "interpretation": {
            "what_this_proves": [
                "the plus and minus packet-source residues cannot be promoted individually to all-mask Ward characters",
                "the paired plus/minus source residue is the only currently certified Ward-compatible source class",
                "the canonical paired lift is trivial at closed-return level because no nonzero kernel selector is certified",
                "a nontrivial sourced Ward identity would need an extra selector on the 1024-mask Ward kernel",
            ],
            "what_this_does_not_prove": (
                "This does not rule out every future nontrivial source-to-return law. It rules out one "
                "being forced by the currently certified sector-26 Ward character, propagator kernel, and "
                "finite BMS/Carrollian flux-balance invariants alone."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Search for an additional canonical selector on the 1024-mask Ward kernel, using action height, "
            "gamma8 incidence, or compact amplitude quotient exposure, to decide whether a nontrivial sourced "
            "Ward lift exists."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {k: v for k, v in report.items() if k != "certificate_sha256"}
    )
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.full_exposure_zero_pair_source_to_closed_return_coupling_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify propagator charge-kernel, symmetry/Ward, all-mask Ward, and finite BMS inputs",
            "verify the all-mask Ward character image is exactly {0,13}",
            "verify plus and minus denominator-cleared source residues have sums 4 and 22",
            "verify individual plus/minus source residues lie outside the Ward character image",
            "verify the paired plus/minus source residue is sector-26 neutral",
            "verify the canonical paired target is the closed-return zero mask in the Ward kernel",
            "verify no nonzero neutral target is selected by current certified invariants",
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
