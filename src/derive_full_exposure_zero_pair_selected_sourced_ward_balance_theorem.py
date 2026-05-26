from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "full_exposure_zero_pair_selected_sourced_ward_balance"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

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
CYCLE5_MASK = 1 << 5
SELECTED_MASK = GAMMA8_MASK + CYCLE5_MASK


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


def transition_between(
    rows: list[dict[str, Any]], source_mask: int, target_mask: int
) -> dict[str, Any]:
    return next(
        row
        for row in rows
        if int(row["source_mask"]) == source_mask and int(row["target_mask"]) == target_mask
    )


def build_theorem() -> dict[str, Any]:
    selector = load_json(ZERO_PAIR_WARD_KERNEL_HEIGHT_SELECTOR_REPORT)
    bms = load_json(FINITE_BMS_CARROLLIAN_FLUX_BALANCE_REPORT)
    scattering = load_json(CANONICAL_FINITE_SCATTERING_TABLE_REPORT)

    selector_summary = selector.get("derived", {}).get("selector_summary", {})
    balance_rows = bms.get("derived", {}).get("balance_rows", [])
    transition_rows = scattering.get("derived", {}).get("transition_rows", [])

    zero_row = row_by_mask(balance_rows, 0)
    gamma8_row = row_by_mask(balance_rows, GAMMA8_MASK)
    cycle5_row = row_by_mask(balance_rows, CYCLE5_MASK)
    selected_row = row_by_mask(balance_rows, SELECTED_MASK)
    gamma8_to_selected = transition_between(transition_rows, GAMMA8_MASK, SELECTED_MASK)
    selected_to_gamma8 = transition_between(transition_rows, SELECTED_MASK, GAMMA8_MASK)
    cycle5_to_selected = transition_between(transition_rows, CYCLE5_MASK, SELECTED_MASK)
    selected_to_cycle5 = transition_between(transition_rows, SELECTED_MASK, CYCLE5_MASK)
    zero_public = zero_public_vector()

    selected_public_terms = {
        "delta_Q_public": selected_row["delta_Q_public"],
        "Flux_D20_public_exact": selected_row["Flux_D20_public_exact"],
        "Res_A985_public": selected_row["Res_A985_public"],
        "public_balance_error": selected_row["public_balance_error"],
    }
    selected_hidden_terms = {
        "bare_pi33": selected_row["bare_pi33"],
        "R33_height_residual": selected_row["R33_height_residual"],
        "finite_height_flux": selected_row["finite_height_flux"],
        "hidden_balance_error": selected_row["hidden_balance_error"],
        "corrected_R33_mod26": selected_row["corrected_R33_mod26"],
        "hidden_packet": selected_row["hidden_packet"],
    }
    source_decomposition = {
        "zero_mask": zero_row,
        "gamma8_source_row": gamma8_row,
        "cycle5_generator_row": cycle5_row,
        "selected_target_row": selected_row,
        "height_sum": gamma8_row["finite_height_flux"] + cycle5_row["finite_height_flux"],
        "corrected_R33_sum_mod26": (
            gamma8_row["corrected_R33_mod26"] + cycle5_row["corrected_R33_mod26"]
        )
        % 26,
    }
    scattering_witness = {
        "gamma8_to_selected": gamma8_to_selected,
        "selected_to_gamma8": selected_to_gamma8,
        "cycle5_to_selected": cycle5_to_selected,
        "selected_to_cycle5": selected_to_cycle5,
    }
    sourced_balance_summary = {
        "selected_mask": SELECTED_MASK,
        "selected_basis_cycle_ids": selected_row["basis_cycle_indices"],
        "selected_public_terms": selected_public_terms,
        "selected_hidden_terms": selected_hidden_terms,
        "source_decomposition": {
            "source_mask": GAMMA8_MASK,
            "generator_mask": CYCLE5_MASK,
            "target_mask": SELECTED_MASK,
            "source_height": gamma8_row["finite_height_flux"],
            "generator_height": cycle5_row["finite_height_flux"],
            "target_height": selected_row["finite_height_flux"],
            "height_sum": source_decomposition["height_sum"],
            "source_corrected_R33_mod26": gamma8_row["corrected_R33_mod26"],
            "generator_corrected_R33_mod26": cycle5_row["corrected_R33_mod26"],
            "target_corrected_R33_mod26": selected_row["corrected_R33_mod26"],
            "corrected_R33_sum_mod26": source_decomposition["corrected_R33_sum_mod26"],
        },
        "scattering_step": {
            "transition_id": gamma8_to_selected["transition_id"],
            "source_mask": gamma8_to_selected["source_mask"],
            "generator_cycle_id": gamma8_to_selected["generator_cycle_id"],
            "target_mask": gamma8_to_selected["target_mask"],
            "toggle": gamma8_to_selected["toggle"],
            "height_flux_delta": gamma8_to_selected["height_flux_delta"],
            "hidden_R33_transfer_mod26": gamma8_to_selected["hidden_R33_transfer_mod26"],
            "packet_transfer": gamma8_to_selected["packet_transfer"],
        },
        "balance_identity": (
            "Delta Q_public(288)=0=Flux_public(288)+Res_public(288), and "
            "bare_pi33(288)+R33(288)+A_h(288)=0-1065984+1065984=0."
        ),
    }

    checks = {
        "ward_kernel_height_selector_is_certified": selector.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_WARD_KERNEL_HEIGHT_SELECTOR_CERTIFIED"
        and selector.get("all_checks_pass") is True,
        "finite_bms_carrollian_flux_balance_is_certified": bms.get("status")
        == "D20_FINITE_BMS_CARROLLIAN_FLUX_BALANCE_CERTIFIED"
        and bms.get("all_checks_pass") is True,
        "canonical_finite_scattering_table_is_certified": scattering.get("status")
        == "D20_CANONICAL_FINITE_SCATTERING_TABLE_CERTIFIED"
        and scattering.get("all_checks_pass") is True,
        "selector_selects_mask288": selector_summary.get("selected_mask") == SELECTED_MASK
        and selector_summary.get("selected_basis_cycle_ids") == [5, 8]
        and selector_summary.get("selected_height_action") == 1065984
        and selector_summary.get("selected_corrected_clock_mod26") == 0,
        "selected_bms_row_closes_public_balance": selected_row["mask"] == SELECTED_MASK
        and selected_row["delta_Q_public"] == zero_public
        and selected_row["Flux_D20_public_exact"] == zero_public
        and selected_row["Res_A985_public"] == zero_public
        and selected_row["public_balance_error"] == zero_public,
        "selected_bms_row_closes_hidden_balance": selected_row["bare_pi33"] == 0
        and selected_row["R33_height_residual"] == -1065984
        and selected_row["finite_height_flux"] == 1065984
        and selected_row["hidden_balance_error"] == 0
        and selected_row["corrected_R33_mod26"] == 0
        and selected_row["hidden_packet"] == "kernel",
        "selected_balance_decomposes_as_gamma8_plus_cycle5": gamma8_row["mask"] == GAMMA8_MASK
        and gamma8_row["finite_height_flux"] == 374784
        and gamma8_row["corrected_R33_mod26"] == 13
        and gamma8_row["hidden_packet"] == "odd"
        and cycle5_row["mask"] == CYCLE5_MASK
        and cycle5_row["finite_height_flux"] == 691200
        and cycle5_row["corrected_R33_mod26"] == 13
        and cycle5_row["hidden_packet"] == "odd"
        and source_decomposition["height_sum"] == selected_row["finite_height_flux"]
        and source_decomposition["corrected_R33_sum_mod26"] == 0,
        "gamma8_to_selected_scattering_step_is_generator5": gamma8_to_selected[
            "source_mask"
        ]
        == GAMMA8_MASK
        and gamma8_to_selected["target_mask"] == SELECTED_MASK
        and gamma8_to_selected["generator_cycle_id"] == 5
        and gamma8_to_selected["toggle"] == "add"
        and gamma8_to_selected["height_flux_delta"] == 691200
        and gamma8_to_selected["hidden_R33_transfer_mod26"] == 13
        and gamma8_to_selected["packet_transfer"] == "odd_to_kernel",
        "selected_to_gamma8_reverse_scattering_step_is_generator5": selected_to_gamma8[
            "source_mask"
        ]
        == SELECTED_MASK
        and selected_to_gamma8["target_mask"] == GAMMA8_MASK
        and selected_to_gamma8["generator_cycle_id"] == 5
        and selected_to_gamma8["toggle"] == "remove"
        and selected_to_gamma8["height_flux_delta"] == -691200
        and selected_to_gamma8["packet_transfer"] == "kernel_to_odd",
        "cycle5_and_gamma8_both_reach_selected_by_the_other_generator": cycle5_to_selected[
            "generator_cycle_id"
        ]
        == 8
        and cycle5_to_selected["height_flux_delta"] == 374784
        and cycle5_to_selected["packet_transfer"] == "odd_to_kernel"
        and selected_to_cycle5["generator_cycle_id"] == 8
        and selected_to_cycle5["height_flux_delta"] == -374784
        and selected_to_cycle5["packet_transfer"] == "kernel_to_odd",
        "selected_balance_is_first_nontrivial_sourced_target": selector.get("checks", {}).get(
            "selector_has_unique_minimum_positive_kernel_action"
        )
        is True
        and selector.get("checks", {}).get("selected_mask_is_nontrivial_sourced_ward_lift")
        is True
        and selected_row["mask"] != 0
        and selected_row["finite_height_flux"] > 0,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FULL_EXPOSURE_ZERO_PAIR_SELECTED_SOURCED_WARD_BALANCE_CERTIFIED"
        if all_checks_pass
        else "D20_FULL_EXPOSURE_ZERO_PAIR_SELECTED_SOURCED_WARD_BALANCE_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.full_exposure_zero_pair_selected_sourced_ward_balance",
        "status": status,
        "object": "d20",
        "claim": (
            "The height-selected nontrivial zero-pair source lift mask 288 satisfies the first selected "
            "sourced finite Ward/BMS balance. It is reached from gamma8 by the generator-5 scattering step, "
            "has zero public charge update, zero public flux, zero public A985 residual, and closes the "
            "hidden balance 0 - 1065984 + 1065984 = 0."
        ),
        "definition": {
            "selected_sourced_ward_balance": (
                "The finite BMS/Carrollian balance evaluated on the nonzero Ward-kernel mask selected by "
                "the zero-pair height selector."
            ),
            "source_scattering_witness": (
                "The canonical scattering transition from gamma8 to the selected mask by toggling generator 5."
            ),
            "first_nontrivial": (
                "First by the certified height selector: mask 288 is the unique nonzero Ward-kernel mask "
                "with minimum positive height action."
            ),
        },
        "inputs": {
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
            "sourced_balance_summary": sourced_balance_summary,
            "scattering_witness": scattering_witness,
            "source_decomposition_rows": {
                "zero": zero_row,
                "gamma8": gamma8_row,
                "cycle5": cycle5_row,
                "selected_288": selected_row,
            },
        },
        "interpretation": {
            "what_this_proves": [
                "the selected nonzero source lift is an actual finite BMS/Ward balance row",
                "the public charge balance is completely closed on mask 288",
                "the hidden R33/action balance closes exactly on mask 288",
                "the scattering automaton realizes the source lift as gamma8 plus generator 5",
            ],
            "what_this_does_not_prove": (
                "This is the first selected sourced balance, not yet a classification of every nontrivial "
                "sourced Ward lift in the Ward kernel."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Classify all Ward-kernel sourced balance targets reachable from gamma8 by height order and "
            "identify whether mask 288 generates a minimal sourced-balance cone."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {k: v for k, v in report.items() if k != "certificate_sha256"}
    )
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.full_exposure_zero_pair_selected_sourced_ward_balance_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify height selector, finite BMS/Carrollian balance, and scattering table inputs",
            "verify selector chooses mask 288 with basis cycles [5,8]",
            "verify mask 288 closes public charge/flux/residual balance",
            "verify mask 288 closes hidden R33/action balance",
            "verify mask 288 decomposes as gamma8 plus cycle 5",
            "verify gamma8 reaches mask 288 by the canonical generator-5 scattering step",
            "verify the reverse generator-5 scattering step returns to gamma8",
            "verify the selected balance is nonzero and first by certified height order",
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
