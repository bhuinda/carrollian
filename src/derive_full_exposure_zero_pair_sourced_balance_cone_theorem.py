from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "full_exposure_zero_pair_sourced_balance_cone"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

SELECTED_SOURCED_WARD_BALANCE_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_selected_sourced_ward_balance"
    / "report.json"
)
ZERO_PAIR_WARD_KERNEL_HEIGHT_SELECTOR_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_ward_kernel_height_selector"
    / "report.json"
)
FINITE_BMS_CARROLLIAN_FLUX_BALANCE_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "finite_bms_carrollian_flux_balance"
    / "report.json"
)
CANONICAL_FINITE_SCATTERING_TABLE_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "canonical_finite_scattering_table"
    / "report.json"
)

PUBLIC_COMPONENTS = ("M", "J", "P", "Phi")
GAMMA8_MASK = 1 << 8
SELECTED_MASK = GAMMA8_MASK + (1 << 5)
GENERATOR3_ID = 3


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


def zero_public_vector() -> dict[str, int]:
    return {component: 0 for component in PUBLIC_COMPONENTS}


def row_by_mask(rows: list[dict[str, Any]], mask: int) -> dict[str, Any]:
    return next(row for row in rows if int(row["mask"]) == mask)


def sourced_target_row(
    scattering_row: dict[str, Any],
    balance_by_mask: dict[int, dict[str, Any]],
) -> dict[str, Any]:
    mask = int(scattering_row["target_mask"])
    balance = balance_by_mask[mask]
    return {
        "height_rank": None,
        "generator_cycle_id": scattering_row["generator_cycle_id"],
        "target_mask": mask,
        "target_basis_cycle_indices": balance["basis_cycle_indices"],
        "target_height_action": balance["finite_height_flux"],
        "height_flux_delta": scattering_row["height_flux_delta"],
        "target_corrected_R33_mod26": balance["corrected_R33_mod26"],
        "target_hidden_packet": balance["hidden_packet"],
        "packet_transfer": scattering_row["packet_transfer"],
        "transition_id": scattering_row["transition_id"],
        "public_balance_error": balance["public_balance_error"],
        "hidden_balance_error": balance["hidden_balance_error"],
    }


def build_theorem() -> dict[str, Any]:
    selected_balance = load_json(SELECTED_SOURCED_WARD_BALANCE_REPORT)
    selector = load_json(ZERO_PAIR_WARD_KERNEL_HEIGHT_SELECTOR_REPORT)
    bms = load_json(FINITE_BMS_CARROLLIAN_FLUX_BALANCE_REPORT)
    scattering = load_json(CANONICAL_FINITE_SCATTERING_TABLE_REPORT)

    balance_rows = bms.get("derived", {}).get("balance_rows", [])
    balance_by_mask = {int(row["mask"]): row for row in balance_rows}
    transition_rows = scattering.get("derived", {}).get("transition_rows", [])
    gamma8_star = scattering.get("derived", {}).get("gamma8_scattering_star", [])
    zero_public = zero_public_vector()

    kernel_targets = [
        row for row in gamma8_star if row.get("target_hidden_packet") == "kernel"
    ]
    nonzero_kernel_targets = [
        row for row in kernel_targets if int(row["target_mask"]) != 0
    ]
    odd_targets = [row for row in gamma8_star if row.get("target_hidden_packet") == "odd"]

    height_ordered_targets = sorted(
        [sourced_target_row(row, balance_by_mask) for row in nonzero_kernel_targets],
        key=lambda row: (int(row["target_height_action"]), int(row["target_mask"])),
    )
    for rank, row in enumerate(height_ordered_targets, start=1):
        row["height_rank"] = rank

    selected_row = row_by_mask(balance_rows, SELECTED_MASK)
    selected_transition = next(
        row
        for row in gamma8_star
        if int(row["target_mask"]) == SELECTED_MASK
    )
    trivial_transition = next(row for row in gamma8_star if int(row["target_mask"]) == 0)
    odd_self_transition = next(
        row for row in gamma8_star if row.get("target_hidden_packet") == "odd"
    )
    apex_outgoing_kernel = [
        row
        for row in transition_rows
        if int(row["source_mask"]) == SELECTED_MASK and row.get("target_hidden_packet") == "kernel"
    ]
    apex_span = sorted({0, SELECTED_MASK})
    target_masks = [int(row["target_mask"]) for row in height_ordered_targets]
    missing_from_apex_span = sorted(mask for mask in target_masks if mask not in apex_span)

    height_gap_to_next = (
        int(height_ordered_targets[1]["target_height_action"])
        - int(height_ordered_targets[0]["target_height_action"])
        if len(height_ordered_targets) > 1
        else None
    )
    cone_summary = {
        "source_mask": GAMMA8_MASK,
        "target_definition": (
            "one-step scattering targets from gamma8 that land in the all-mask Ward kernel"
        ),
        "kernel_target_count_including_zero": len(kernel_targets),
        "nonzero_kernel_target_count": len(nonzero_kernel_targets),
        "odd_target_count": len(odd_targets),
        "trivial_zero_target": {
            "generator_cycle_id": trivial_transition["generator_cycle_id"],
            "target_mask": trivial_transition["target_mask"],
            "height_flux_delta": trivial_transition["height_flux_delta"],
        },
        "odd_self_target": {
            "generator_cycle_id": odd_self_transition["generator_cycle_id"],
            "target_mask": odd_self_transition["target_mask"],
            "target_hidden_packet": odd_self_transition["target_hidden_packet"],
            "height_flux_delta": odd_self_transition["height_flux_delta"],
        },
        "height_apex": {
            "mask": SELECTED_MASK,
            "height_action": selected_row["finite_height_flux"],
            "generator_cycle_id": selected_transition["generator_cycle_id"],
            "height_gap_to_next": height_gap_to_next,
        },
        "height_cone_statement": (
            "mask 288 is the unique nonzero height-minimal apex of the gamma8 one-step Ward-kernel "
            "sourced-balance cone"
        ),
        "algebraic_generation_statement": (
            "mask 288 does not generate the whole one-step target set as an F2 subspace or by one-step "
            "kernel-preserving scattering"
        ),
        "apex_f2_span": apex_span,
        "target_masks_missing_from_apex_f2_span": missing_from_apex_span,
        "apex_one_step_kernel_preserving_targets": [
            {
                "generator_cycle_id": row["generator_cycle_id"],
                "target_mask": row["target_mask"],
                "target_height_action": row["target_height_action"],
                "height_flux_delta": row["height_flux_delta"],
            }
            for row in apex_outgoing_kernel
        ],
    }

    checks = {
        "selected_sourced_ward_balance_is_certified": selected_balance.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SELECTED_SOURCED_WARD_BALANCE_CERTIFIED"
        and selected_balance.get("all_checks_pass") is True,
        "ward_kernel_height_selector_is_certified": selector.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_WARD_KERNEL_HEIGHT_SELECTOR_CERTIFIED"
        and selector.get("all_checks_pass") is True,
        "finite_bms_carrollian_flux_balance_is_certified": bms.get("status")
        == "D20_FINITE_BMS_CARROLLIAN_FLUX_BALANCE_CERTIFIED"
        and bms.get("all_checks_pass") is True,
        "canonical_finite_scattering_table_is_certified": scattering.get("status")
        == "D20_CANONICAL_FINITE_SCATTERING_TABLE_CERTIFIED"
        and scattering.get("all_checks_pass") is True,
        "gamma8_star_has_expected_kernel_and_odd_targets": len(gamma8_star) == 11
        and len(kernel_targets) == 10
        and len(nonzero_kernel_targets) == 9
        and len(odd_targets) == 1
        and odd_self_transition["generator_cycle_id"] == GENERATOR3_ID,
        "height_ordered_kernel_targets_are_all_balanced": all(
            row["public_balance_error"] == zero_public
            and row["hidden_balance_error"] == 0
            and row["target_corrected_R33_mod26"] == 0
            and row["target_hidden_packet"] == "kernel"
            for row in height_ordered_targets
        ),
        "mask288_is_unique_nonzero_height_apex": height_ordered_targets[0][
            "target_mask"
        ]
        == SELECTED_MASK
        and height_ordered_targets[0]["target_height_action"] == 1065984
        and height_ordered_targets[0]["generator_cycle_id"] == 5
        and height_gap_to_next == 82944
        and [row["target_mask"] for row in height_ordered_targets].count(SELECTED_MASK) == 1,
        "height_order_matches_certified_gamma8_star": [
            row["target_mask"] for row in height_ordered_targets
        ]
        == [288, 260, 320, 768, 384, 257, 272, 1280, 258],
        "mask288_does_not_generate_target_set_as_f2_span": apex_span == [0, 288]
        and missing_from_apex_span == [257, 258, 260, 272, 320, 384, 768, 1280],
        "mask288_has_only_generator3_one_step_kernel_preserving_exit": len(apex_outgoing_kernel)
        == 1
        and apex_outgoing_kernel[0]["generator_cycle_id"] == GENERATOR3_ID
        and apex_outgoing_kernel[0]["target_mask"] == 296
        and apex_outgoing_kernel[0]["target_height_action"] == 2257920,
        "selected_balance_remains_first_nontrivial_sourced_balance": selected_balance.get(
            "checks", {}
        ).get("selected_balance_is_first_nontrivial_sourced_target")
        is True
        and selector.get("checks", {}).get("selector_has_unique_minimum_positive_kernel_action")
        is True,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_CONE_CERTIFIED"
        if all_checks_pass
        else "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_CONE_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.full_exposure_zero_pair_sourced_balance_cone",
        "status": status,
        "object": "d20",
        "claim": (
            "The gamma8 one-step sourced Ward-kernel target cone has nine nonzero balanced targets. "
            "Mask 288 is the unique nonzero height-minimal apex, separated from the next target by height "
            "gap 82944. It is a height-cone apex, not an algebraic generator of the full target set: its "
            "F2 span is only {0,288}, and its only one-step kernel-preserving exit is generator 3 to mask 296."
        ),
        "definition": {
            "gamma8_sourced_balance_cone": (
                "The one-step scattering targets from gamma8 that land in the all-mask Ward kernel, ordered "
                "by finite height action and filtered to nonzero targets when testing nontriviality."
            ),
            "height_apex": (
                "The unique nonzero target in that set with minimum positive finite height action."
            ),
            "algebraic_generation_test": (
                "Whether the apex alone generates every nonzero one-step target as an F2 subspace element "
                "or by one-step kernel-preserving scattering."
            ),
        },
        "inputs": {
            "selected_sourced_ward_balance_report": {
                "path": rel(SELECTED_SOURCED_WARD_BALANCE_REPORT),
                "sha256": sha_file(SELECTED_SOURCED_WARD_BALANCE_REPORT),
            },
            "zero_pair_ward_kernel_height_selector_report": {
                "path": rel(ZERO_PAIR_WARD_KERNEL_HEIGHT_SELECTOR_REPORT),
                "sha256": sha_file(ZERO_PAIR_WARD_KERNEL_HEIGHT_SELECTOR_REPORT),
            },
            "finite_bms_carrollian_flux_balance_report": {
                "path": rel(FINITE_BMS_CARROLLIAN_FLUX_BALANCE_REPORT),
                "sha256": sha_file(FINITE_BMS_CARROLLIAN_FLUX_BALANCE_REPORT),
            },
            "canonical_finite_scattering_table_report": {
                "path": rel(CANONICAL_FINITE_SCATTERING_TABLE_REPORT),
                "sha256": sha_file(CANONICAL_FINITE_SCATTERING_TABLE_REPORT),
            },
        },
        "derived": {
            "cone_summary": cone_summary,
            "height_ordered_nonzero_kernel_targets": height_ordered_targets,
            "gamma8_star_kernel_target_rows": kernel_targets,
            "gamma8_star_odd_target_rows": odd_targets,
        },
        "interpretation": {
            "what_this_proves": [
                "all nonzero one-step Ward-kernel targets from gamma8 are balanced sourced Ward rows",
                "mask 288 is the unique height-minimal nonzero target",
                "mask 288 is the apex of the height-ordered sourced-balance cone",
                "mask 288 does not algebraically generate the whole one-step target set by itself",
            ],
            "what_this_does_not_prove": (
                "This is a one-step cone classification. It does not yet classify all higher-depth paths "
                "through the 1024-mask Ward kernel."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Extend the sourced-balance cone from the one-step gamma8 star to shortest height paths through "
            "all 1023 nonzero Ward-kernel masks."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {k: v for k, v in report.items() if k != "certificate_sha256"}
    )
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.full_exposure_zero_pair_sourced_balance_cone_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify selected sourced balance, height selector, finite BMS, and scattering inputs",
            "extract the one-step gamma8 scattering star",
            "classify kernel, nonzero kernel, and odd targets",
            "verify all nonzero kernel targets close public and hidden balance",
            "verify mask 288 is the unique nonzero height-minimal apex",
            "verify the height order of all nonzero kernel targets",
            "verify mask 288 does not span all targets as an F2 generator",
            "verify mask 288 has only the generator-3 one-step kernel-preserving exit",
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
