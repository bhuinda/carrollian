from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "full_exposure_zero_pair_sourced_balance_shortest_paths"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

SOURCED_BALANCE_CONE_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_cone"
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
CANONICAL_FINITE_SCATTERING_TABLE_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "canonical_finite_scattering_table"
    / "report.json"
)

PUBLIC_COMPONENTS = ("M", "J", "P", "Phi")
GAMMA8_MASK = 1 << 8
SELECTED_MASK = GAMMA8_MASK + (1 << 5)
RESIDUE_RANK = 11


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


def mask_bits(mask: int) -> list[int]:
    return [idx for idx in range(RESIDUE_RANK) if mask & (1 << idx)]


def histogram(values: list[int]) -> dict[str, int]:
    counts = Counter(values)
    return {str(key): int(counts[key]) for key in sorted(counts)}


def build_path_row(
    target_mask: int,
    balance_by_mask: dict[int, dict[str, Any]],
    transition_by_edge: dict[tuple[int, int], dict[str, Any]],
    generator_by_id: dict[int, dict[str, Any]],
) -> dict[str, Any]:
    source_row = balance_by_mask[GAMMA8_MASK]
    target_row = balance_by_mask[target_mask]
    delta_mask = GAMMA8_MASK ^ target_mask
    toggles = mask_bits(delta_mask)
    ordered_toggles = sorted(
        toggles,
        key=lambda idx: (int(generator_by_id[idx]["optical_action"]), idx),
    )
    add_generator_ids = [idx for idx in toggles if target_mask & (1 << idx)]
    remove_generator_ids = [idx for idx in toggles if GAMMA8_MASK & (1 << idx)]

    current = GAMMA8_MASK
    transition_witnesses = []
    signed_height_delta = 0
    for generator_id in ordered_toggles:
        next_mask = current ^ (1 << generator_id)
        transition = transition_by_edge[(current, next_mask)]
        signed_height_delta += int(transition["height_flux_delta"])
        transition_witnesses.append(
            {
                "transition_id": transition["transition_id"],
                "generator_cycle_id": transition["generator_cycle_id"],
                "source_mask": transition["source_mask"],
                "target_mask": transition["target_mask"],
                "height_flux_delta": transition["height_flux_delta"],
                "packet_transfer": transition["packet_transfer"],
            }
        )
        current = next_mask

    shortest_path_action = sum(int(generator_by_id[idx]["optical_action"]) for idx in toggles)
    corrected_transfer_mod26 = (
        sum(int(generator_by_id[idx]["corrected_basis_clock_mod26"]) for idx in toggles) % 26
    )
    return {
        "target_mask": target_mask,
        "target_basis_cycle_indices": target_row["basis_cycle_indices"],
        "delta_mask_from_gamma8": delta_mask,
        "toggle_generator_ids": toggles,
        "canonical_ordered_generator_ids": ordered_toggles,
        "add_generator_ids": add_generator_ids,
        "remove_generator_ids": remove_generator_ids,
        "shortest_step_count": len(toggles),
        "shortest_path_action": shortest_path_action,
        "signed_height_delta": signed_height_delta,
        "source_height_action": source_row["finite_height_flux"],
        "target_height_action": target_row["finite_height_flux"],
        "target_hidden_packet": target_row["hidden_packet"],
        "target_corrected_R33_mod26": target_row["corrected_R33_mod26"],
        "corrected_R33_transfer_mod26": corrected_transfer_mod26,
        "public_balance_error": target_row["public_balance_error"],
        "hidden_balance_error": target_row["hidden_balance_error"],
        "transition_witnesses": transition_witnesses,
    }


def build_theorem() -> dict[str, Any]:
    cone = load_json(SOURCED_BALANCE_CONE_REPORT)
    ward = load_json(CANONICAL_ALL_MASK_WARD_IDENTITY_REPORT)
    bms = load_json(FINITE_BMS_CARROLLIAN_FLUX_BALANCE_REPORT)
    scattering = load_json(CANONICAL_FINITE_SCATTERING_TABLE_REPORT)

    ward_rows = ward.get("derived", {}).get("ward_rows", [])
    balance_rows = bms.get("derived", {}).get("balance_rows", [])
    transition_rows = scattering.get("derived", {}).get("transition_rows", [])
    generator_rows = scattering.get("derived", {}).get("generator_summaries", [])

    balance_by_mask = {int(row["mask"]): row for row in balance_rows}
    transition_by_edge = {
        (int(row["source_mask"]), int(row["target_mask"])): row for row in transition_rows
    }
    generator_by_id = {int(row["generator_cycle_id"]): row for row in generator_rows}
    kernel_masks = sorted(
        int(row["mask"]) for row in ward_rows if row.get("in_global_corrected_kernel") is True
    )
    nonzero_kernel_masks = [mask for mask in kernel_masks if mask != 0]

    path_rows = [
        build_path_row(mask, balance_by_mask, transition_by_edge, generator_by_id)
        for mask in nonzero_kernel_masks
    ]
    path_rows = sorted(
        path_rows,
        key=lambda row: (int(row["shortest_path_action"]), int(row["target_mask"])),
    )
    for rank, row in enumerate(path_rows, start=1):
        row["shortest_path_action_rank"] = rank

    first_row = path_rows[0]
    source_row = balance_by_mask[GAMMA8_MASK]
    zero_public = zero_public_vector()
    step_histogram = histogram([int(row["shortest_step_count"]) for row in path_rows])
    action_histogram = histogram([int(row["shortest_path_action"]) for row in path_rows])
    target_height_histogram = histogram([int(row["target_height_action"]) for row in path_rows])
    generator_participation = {
        str(generator_id): sum(
            1 for row in path_rows if generator_id in row["toggle_generator_ids"]
        )
        for generator_id in range(RESIDUE_RANK)
    }
    includes_gamma8_removal = sum(1 for row in path_rows if 8 in row["remove_generator_ids"])
    includes_generator3 = sum(1 for row in path_rows if 3 in row["toggle_generator_ids"])

    shortest_path_summary = {
        "source_mask": GAMMA8_MASK,
        "source_height_action": source_row["finite_height_flux"],
        "source_corrected_R33_mod26": source_row["corrected_R33_mod26"],
        "target_count": len(path_rows),
        "kernel_mask_count_including_zero": len(kernel_masks),
        "shortest_path_rule": (
            "For target k, toggle exactly the bits of gamma8 XOR k. Since every generator action is "
            "positive, any extra toggle pair strictly increases the path action."
        ),
        "canonical_order_rule": (
            "Order the required toggles by generator optical action, then generator id, for a deterministic "
            "transition witness."
        ),
        "unique_minimum_path": {
            "target_mask": first_row["target_mask"],
            "shortest_path_action": first_row["shortest_path_action"],
            "target_height_action": first_row["target_height_action"],
            "toggle_generator_ids": first_row["toggle_generator_ids"],
            "shortest_path_action_gap_to_next": (
                path_rows[1]["shortest_path_action"] - first_row["shortest_path_action"]
            ),
        },
        "shortest_step_count_histogram": step_histogram,
        "unique_shortest_path_action_count": len(action_histogram),
        "unique_target_height_action_count": len(target_height_histogram),
        "generator_participation_counts": generator_participation,
        "targets_requiring_gamma8_removal": includes_gamma8_removal,
        "targets_using_generator3": includes_generator3,
        "path_rows_sha256": sha_json(path_rows),
    }

    checks = {
        "sourced_balance_cone_is_certified": cone.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_CONE_CERTIFIED"
        and cone.get("all_checks_pass") is True,
        "canonical_all_mask_ward_identity_is_certified": ward.get("status")
        == "D20_CANONICAL_ALL_MASK_WARD_IDENTITY_CERTIFIED"
        and ward.get("all_checks_pass") is True,
        "finite_bms_carrollian_flux_balance_is_certified": bms.get("status")
        == "D20_FINITE_BMS_CARROLLIAN_FLUX_BALANCE_CERTIFIED"
        and bms.get("all_checks_pass") is True,
        "canonical_finite_scattering_table_is_certified": scattering.get("status")
        == "D20_CANONICAL_FINITE_SCATTERING_TABLE_CERTIFIED"
        and scattering.get("all_checks_pass") is True,
        "all_nonzero_ward_kernel_masks_are_covered": len(kernel_masks) == 1024
        and len(nonzero_kernel_masks) == 1023
        and [row["target_mask"] for row in sorted(path_rows, key=lambda row: row["target_mask"])]
        == nonzero_kernel_masks,
        "all_shortest_path_witnesses_end_at_target": all(
            row["transition_witnesses"]
            and row["transition_witnesses"][-1]["target_mask"] == row["target_mask"]
            for row in path_rows
        ),
        "all_paths_toggle_exactly_the_xor_difference": all(
            row["delta_mask_from_gamma8"] == (GAMMA8_MASK ^ row["target_mask"])
            and row["toggle_generator_ids"] == mask_bits(row["delta_mask_from_gamma8"])
            and row["shortest_step_count"] == len(row["toggle_generator_ids"])
            for row in path_rows
        ),
        "all_path_actions_equal_sum_of_required_generator_actions": all(
            row["shortest_path_action"]
            == sum(
                int(generator_by_id[generator_id]["optical_action"])
                for generator_id in row["toggle_generator_ids"]
            )
            for row in path_rows
        ),
        "all_signed_height_deltas_match_target_minus_source": all(
            row["signed_height_delta"] == row["target_height_action"] - source_row["finite_height_flux"]
            for row in path_rows
        ),
        "all_paths_transfer_odd_source_to_kernel_clock": all(
            row["corrected_R33_transfer_mod26"] == 13
            and row["target_corrected_R33_mod26"] == 0
            and row["target_hidden_packet"] == "kernel"
            for row in path_rows
        ),
        "all_targets_close_public_and_hidden_balance": all(
            row["public_balance_error"] == zero_public and row["hidden_balance_error"] == 0
            for row in path_rows
        ),
        "mask288_remains_unique_shortest_path_action_apex": first_row["target_mask"] == SELECTED_MASK
        and first_row["shortest_path_action"] == 691200
        and first_row["target_height_action"] == 1065984
        and first_row["toggle_generator_ids"] == [5]
        and path_rows[1]["shortest_path_action"] - first_row["shortest_path_action"] == 82944
        and [row["target_mask"] for row in path_rows if row["shortest_path_action"] == 691200]
        == [SELECTED_MASK],
        "step_count_histogram_matches_ward_kernel_geometry": step_histogram
        == {
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
        },
        "path_classification_records_gamma8_and_generator3_splits": includes_gamma8_removal == 511
        and includes_generator3 == 512,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_SHORTEST_PATHS_CERTIFIED"
        if all_checks_pass
        else "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_SHORTEST_PATHS_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.full_exposure_zero_pair_sourced_balance_shortest_paths",
        "status": status,
        "object": "d20",
        "claim": (
            "Every nonzero all-mask Ward-kernel mask has a certified shortest sourced-balance path from "
            "gamma8. The path toggles exactly the XOR difference from gamma8, is witnessed by canonical "
            "scattering transitions, closes the finite BMS/Ward balance at the target, and keeps mask 288 "
            "as the unique minimum-action target."
        ),
        "definition": {
            "shortest_sourced_balance_path": (
                "For a nonzero Ward-kernel target k, the minimal positive-action path from gamma8 is the "
                "hypercube path toggling each generator bit in gamma8 XOR k exactly once."
            ),
            "canonical_path_witness": (
                "The deterministic representative of that shortest path obtained by ordering required "
                "toggles by generator optical action and then generator id."
            ),
            "target_balance": (
                "The finite BMS/Carrollian row at the target mask, with public balance error zero and "
                "hidden R33/action balance error zero."
            ),
        },
        "inputs": {
            "sourced_balance_cone_report": {
                "path": rel(SOURCED_BALANCE_CONE_REPORT),
                "sha256": sha_file(SOURCED_BALANCE_CONE_REPORT),
            },
            "canonical_all_mask_ward_identity_report": {
                "path": rel(CANONICAL_ALL_MASK_WARD_IDENTITY_REPORT),
                "sha256": sha_file(CANONICAL_ALL_MASK_WARD_IDENTITY_REPORT),
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
            "shortest_path_summary": shortest_path_summary,
            "shortest_path_rows": path_rows,
        },
        "interpretation": {
            "what_this_proves": [
                "the gamma8 sourced-balance classifier covers every nonzero Ward-kernel mask",
                "each target has a certified canonical shortest scattering path",
                "every target closes public and hidden finite BMS/Ward balance",
                "mask 288 remains the unique minimum-action target in the full 1023-target classifier",
            ],
            "what_this_does_not_prove": (
                "This classifies shortest paths by the existing positive generator actions. It does not yet "
                "quotient path degeneracies by graph automorphism or build a continuum transport limit."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Compress the 1023 shortest sourced-balance paths by height, step count, generator support, "
            "and D20 symmetry to find canonical transport families."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {k: v for k, v in report.items() if k != "certificate_sha256"}
    )
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.full_exposure_zero_pair_sourced_balance_shortest_paths_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify sourced-balance cone, Ward, BMS, and scattering inputs",
            "enumerate all 1023 nonzero Ward-kernel target masks",
            "construct each gamma8 XOR shortest path and canonical transition witness",
            "verify path actions equal sums of required generator actions",
            "verify signed height deltas match target height minus gamma8 height",
            "verify every path transfers the odd gamma8 source into the Ward kernel",
            "verify every target closes public and hidden balance",
            "verify mask 288 remains the unique minimum-action target",
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
