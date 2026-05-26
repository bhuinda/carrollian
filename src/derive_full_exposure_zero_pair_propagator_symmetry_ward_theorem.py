from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "full_exposure_zero_pair_propagator_symmetry_ward"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

ZERO_PAIR_PROPAGATOR_CHARGE_KERNEL_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_propagator_charge_kernel"
    / "report.json"
)
FULL_EXPOSURE_RADICAL_GATE_STABILIZER_LIFT_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_radical_gate_stabilizer_lift"
    / "report.json"
)
FULL_EXPOSURE_LABEL_BREAKING_FACTORIZATION_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_label_breaking_factorization"
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


def build_theorem() -> dict[str, Any]:
    kernel = load_json(ZERO_PAIR_PROPAGATOR_CHARGE_KERNEL_REPORT)
    lift = load_json(FULL_EXPOSURE_RADICAL_GATE_STABILIZER_LIFT_REPORT)
    breaking = load_json(FULL_EXPOSURE_LABEL_BREAKING_FACTORIZATION_REPORT)
    ward = load_json(CANONICAL_ALL_MASK_WARD_IDENTITY_REPORT)
    flux = load_json(FINITE_BMS_CARROLLIAN_FLUX_BALANCE_REPORT)

    kernel_summary = kernel.get("derived", {}).get("propagator_charge_kernel_summary", {})
    plus_image = kernel_summary.get("plus_denominator_cleared_sector26_image", {})
    minus_image = kernel_summary.get("minus_denominator_cleared_sector26_image", {})
    pair_sum = mod26_add(plus_image, minus_image)
    ward_character_histogram = ward.get("derived", {}).get("global_corrected_character", {}).get(
        "histogram", {}
    )
    ward_character_image = sorted(int(value) for value in ward_character_histogram)
    breaker_summary = breaking.get("derived", {}).get("breaker_summary", {})
    lift_summary = lift.get("derived", {}).get("graph_action_lift_summary", {})
    public_frame = flux.get("derived", {}).get("public_charge_frame", {})
    balance_summary = flux.get("derived", {}).get("balance_summary", {})

    symmetry_summary = {
        "unlabelled_graph_action_lift_order": lift_summary.get("graph_action_lift_order"),
        "canonical_affine_lift_count": breaker_summary.get("canonical_affine_lift_count"),
        "nonidentity_affine_lift_count": breaker_summary.get("nonidentity_affine_lift_count"),
        "identity_affine_id": breaker_summary.get("identity_affine_id"),
        "sector26_axis_survivor_count": breaker_summary.get("axis_family_survivor_counts", {}).get(
            "sector26"
        ),
        "fine_spectral_atomic_survivor_count": breaker_summary.get(
            "atomic_label_survivor_counts", {}
        ).get("fine_spectral"),
        "surviving_label_preserving_symmetry_order": 1,
        "kernel_fixed_reason": (
            "The full label-preserving symmetry is already reduced to the identity, so the "
            "denominator-cleared propagator charge kernel is fixed without quotienting."
        ),
    }

    ward_flux_summary = {
        "public_charge_components": public_frame.get("components"),
        "public_closed_return_rank_over_f2": balance_summary.get(
            "public_closed_return_rank_over_f2"
        ),
        "hidden_corrected_rank_over_f2": balance_summary.get("hidden_corrected_rank_over_f2"),
        "ward_corrected_r33_character_image": ward_character_image,
        "ward_corrected_r33_histogram": ward_character_histogram,
        "plus_sector26_sum_mod26": plus_image.get("sector26_clock_sum_mod26"),
        "minus_sector26_sum_mod26": minus_image.get("sector26_clock_sum_mod26"),
        "plus_minus_sum_mod26": pair_sum,
        "individual_residues_are_not_closed_return_ward_characters": (
            plus_image.get("sector26_clock_sum_mod26") not in ward_character_image
            and minus_image.get("sector26_clock_sum_mod26") not in ward_character_image
        ),
        "paired_residue_is_sector26_neutral": pair_sum
        == {
            "sector26_clock_delta_mod26": 0,
            "sector26_clock_pair_mod26": [0, 0],
            "sector26_clock_sum_mod26": 0,
        },
        "compatibility_status": (
            "Compatible as a denominator-cleared packet-source kernel: the individual plus/minus "
            "sector-26 residues are not closed-return Ward characters, while the paired source/dipole "
            "class is sector-26 neutral and the public closed-return flux rank remains zero."
        ),
    }

    checks = {
        "propagator_charge_kernel_is_certified": kernel.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_PROPAGATOR_CHARGE_KERNEL_CERTIFIED"
        and kernel.get("all_checks_pass") is True,
        "stabilizer_lift_is_certified": lift.get("status")
        == "D20_FULL_EXPOSURE_RADICAL_GATE_STABILIZER_LIFT_CERTIFIED"
        and lift.get("all_checks_pass") is True,
        "label_breaking_factorization_is_certified": breaking.get("status")
        == "D20_FULL_EXPOSURE_LABEL_BREAKING_FACTORIZATION_CERTIFIED"
        and breaking.get("all_checks_pass") is True,
        "canonical_all_mask_ward_identity_is_certified": ward.get("status")
        == "D20_CANONICAL_ALL_MASK_WARD_IDENTITY_CERTIFIED"
        and ward.get("all_checks_pass") is True,
        "finite_bms_carrollian_flux_balance_is_certified": flux.get("status")
        == "D20_FINITE_BMS_CARROLLIAN_FLUX_BALANCE_CERTIFIED"
        and flux.get("all_checks_pass") is True,
        "surviving_label_preserving_symmetry_is_identity": lift.get("checks", {}).get(
            "charge_frame_and_fine_spectral_labels_reduce_to_identity"
        )
        is True
        and breaking.get("checks", {}).get("every_nonidentity_lift_is_killed_by_some_atomic_label")
        is True
        and breaker_summary.get("identity_affine_id") == 0
        and breaker_summary.get("nonidentity_affine_lift_count") == 383
        and breaker_summary.get("axis_family_survivor_counts", {}).get("sector26") == 1
        and breaker_summary.get("atomic_label_survivor_counts", {}).get("fine_spectral") == 1,
        "kernel_is_fixed_by_surviving_label_symmetry": symmetry_summary[
            "surviving_label_preserving_symmetry_order"
        ]
        == 1
        and kernel_summary.get("support_packet_ids") == [239, 238],
        "public_flux_balance_context_is_rank_zero": flux.get("checks", {}).get(
            "public_flux_balance_holds_for_all_masks"
        )
        is True
        and balance_summary.get("public_closed_return_rank_over_f2") == 0
        and public_frame.get("components") == ["M", "J", "P", "Phi"],
        "ward_character_image_is_order_two": ward.get("checks", {}).get(
            "global_corrected_character_has_order_two_image"
        )
        is True
        and ward_character_histogram == {"0": 1024, "13": 1024}
        and ward_character_image == [0, 13],
        "individual_kernel_residues_are_not_closed_return_ward_characters": plus_image.get(
            "sector26_clock_sum_mod26"
        )
        == 4
        and minus_image.get("sector26_clock_sum_mod26") == 22
        and plus_image.get("sector26_clock_sum_mod26") not in ward_character_image
        and minus_image.get("sector26_clock_sum_mod26") not in ward_character_image,
        "paired_kernel_residue_is_sector26_neutral": pair_sum
        == {
            "sector26_clock_delta_mod26": 0,
            "sector26_clock_pair_mod26": [0, 0],
            "sector26_clock_sum_mod26": 0,
        },
        "kernel_support_does_not_activate_gamma_or_hidden_ward_channels": kernel_summary.get(
            "shared_support_axes", {}
        ).get("gamma_frame")
        == "gamma8_silent"
        and kernel_summary.get("shared_support_axes", {}).get("hidden_frame")
        == "hidden_cancelled"
        and kernel_summary.get("shared_support_axes", {}).get("central_frame")
        == "central_negative",
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FULL_EXPOSURE_ZERO_PAIR_PROPAGATOR_SYMMETRY_WARD_CERTIFIED"
        if all_checks_pass
        else "D20_FULL_EXPOSURE_ZERO_PAIR_PROPAGATOR_SYMMETRY_WARD_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.full_exposure_zero_pair_propagator_symmetry_ward",
        "status": status,
        "object": "d20",
        "claim": (
            "The denominator-cleared zero-pair propagator charge kernel is invariant under the surviving "
            "label-preserving symmetry because that symmetry is trivial. It is compatible with the finite "
            "Ward/flux-balance ledger as a packet-source kernel: the individual plus/minus sector-26 "
            "images are not closed-return Ward characters, but the paired residue is sector-26 neutral and "
            "does not disturb the rank-zero public flux balance."
        ),
        "definition": {
            "surviving_label_preserving_symmetry": (
                "The full-exposure radical-gate lift after imposing the certified charge-frame, sector-26, "
                "and fine spectral labels."
            ),
            "ward_native_closed_return_character": (
                "The all-mask corrected R33 character with image {0,13} in Z/26."
            ),
            "packet_source_ward_compatibility": (
                "A packet-source kernel is compatible when it is fixed by surviving labels, has no public "
                "closed-return flux contradiction, and its paired plus/minus cleared residue is neutral in "
                "the sector-26 ledger."
            ),
        },
        "inputs": {
            "zero_pair_propagator_charge_kernel_report": {
                "path": rel(ZERO_PAIR_PROPAGATOR_CHARGE_KERNEL_REPORT),
                "sha256": sha_file(ZERO_PAIR_PROPAGATOR_CHARGE_KERNEL_REPORT),
            },
            "full_exposure_radical_gate_stabilizer_lift_report": {
                "path": rel(FULL_EXPOSURE_RADICAL_GATE_STABILIZER_LIFT_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_RADICAL_GATE_STABILIZER_LIFT_REPORT),
            },
            "full_exposure_label_breaking_factorization_report": {
                "path": rel(FULL_EXPOSURE_LABEL_BREAKING_FACTORIZATION_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_LABEL_BREAKING_FACTORIZATION_REPORT),
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
            "symmetry_summary": symmetry_summary,
            "ward_flux_summary": ward_flux_summary,
            "kernel_summary": kernel_summary,
            "compatibility_matrix": {
                "symmetry_invariant": True,
                "ward_native_as_individual_closed_return_character": False,
                "ward_compatible_as_packet_source_pair": True,
                "needs_source_to_closed_return_coupling_for_stronger_claim": True,
            },
        },
        "interpretation": {
            "what_this_proves": [
                "the denominator-cleared kernel is fixed by the full surviving label-preserving symmetry",
                "that invariance is identity-level, not protection by a nontrivial residual group",
                "the individual plus/minus sector-26 residues are not native all-mask Ward characters",
                "the paired cleared residue is sector-26 neutral and public-flux compatible",
            ],
            "what_this_does_not_prove": (
                "This does not yet build a sourced Ward identity. A stronger theorem needs a coupling map "
                "from packet-source residues into closed-return masks or a new sourced finite Ward law."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Construct the source-to-closed-return coupling map, or prove no such map exists, from the "
            "denominator-cleared propagator kernel into the all-mask Ward residue group."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {k: v for k, v in report.items() if k != "certificate_sha256"}
    )
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.full_exposure_zero_pair_propagator_symmetry_ward_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify propagator charge-kernel, stabilizer, label-breaking, Ward, and flux inputs",
            "verify the surviving label-preserving symmetry is identity",
            "verify the zero-pair kernel is fixed by that surviving symmetry",
            "verify public closed-return flux rank is zero",
            "verify all-mask Ward character image is {0,13}",
            "verify individual propagator residues are not closed-return Ward characters",
            "verify the paired plus/minus residue is sector-26 neutral",
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
