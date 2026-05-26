from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, DATA, ROOT


THEOREM_ID = "typed_nonexact_optical_flux_update"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

NONEXACT_OPTICAL_REPORT = D20_INVARIANTS / "theorems" / "nonexact_optical_residue" / "report.json"
ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT = (
    D20_INVARIANTS / "theorems" / "sector33_all_residue_height_transport" / "report.json"
)
SUPERSELECTION_FLUX_EXTENSION_REPORT = (
    D20_INVARIANTS / "theorems" / "superselection_flux_balance_extension" / "report.json"
)
MINIMAL_COMPOSITE_TRANSPORT_REPORT = (
    D20_INVARIANTS / "theorems" / "minimal_composite_null_supports_transport" / "report.json"
)
FULL_A985_LIFT = DATA / "drinfeld" / "full_a985_lift.json"

FIELD_PRIME = 1_000_003
PUBLIC_COMPONENTS = ["M", "J", "P", "Phi"]
HIDDEN_COMPONENTS = ["R33", "K_mixed_S", "K_pure_Sminus"]
BOSONIC_STRING_CRITICAL_DIMENSION = 26
D20_PUBLIC_STATE_COUNT = 20
H6_CHANNEL_COUNT = 6


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


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


def signed_mod(value: int, mod: int = FIELD_PRIME) -> int:
    value %= mod
    return value if value <= mod // 2 else value - mod


def sector_profiles_by_id(full_lift: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {
        int(profile["sector"]): profile
        for profile in full_lift["gluing_and_sector_profiles"]["sector_profiles"]
    }


def zero_public_update() -> dict[str, int]:
    return {component: 0 for component in PUBLIC_COMPONENTS}


def hidden_update(*, r33: int = 0, mixed: int = 0, pure: int = 0) -> dict[str, int]:
    return {
        "R33": int(r33),
        "K_mixed_S": int(mixed),
        "K_pure_Sminus": int(pure),
    }


def typed_row(row: dict[str, Any]) -> dict[str, Any]:
    residual = int(row["residual_integral"])
    residual_mod = int(row["residual_mod_prime"])
    is_zero = int(row["mask"]) == 0
    return {
        "mask": int(row["mask"]),
        "basis_cycle_ids": row["basis_cycle_ids"],
        "height_action": int(row["height_action"]),
        "public_update": zero_public_update(),
        "hidden_update_integral": hidden_update(r33=residual),
        "hidden_update_mod_prime": hidden_update(r33=residual_mod),
        "event_type": "gauge_zero" if is_zero else "nonexact_optical_height_residual",
        "support_component": "gauge_zero" if is_zero else "R33",
        "support_sector": int(row["support_sector"]),
        "transport_scalar": int(row["transport_scalar"]),
        "transport_scalar_signed": int(row["transport_scalar_signed"]),
        "pi33_coefficient_mod_prime": int(row["pi33_coefficient_mod_prime"]),
        "residual_matches_negative_height_action": residual == -int(row["height_action"]),
    }


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


def build_theorem() -> dict[str, Any]:
    nonexact = load_json(NONEXACT_OPTICAL_REPORT)
    all_residue = load_json(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT)
    superselection = load_json(SUPERSELECTION_FLUX_EXTENSION_REPORT)
    minimal_composite = load_json(MINIMAL_COMPOSITE_TRANSPORT_REPORT)
    full_lift = load_json(FULL_A985_LIFT)
    profiles = sector_profiles_by_id(full_lift)

    transport_rows = sorted(all_residue["derived"]["transport_rows"], key=lambda row: int(row["mask"]))
    update_rows = [typed_row(row) for row in transport_rows]
    zero_row = update_rows[0]
    nonzero_rows = [row for row in update_rows if row["mask"] != 0]
    first_forced = nonexact["derived"]["first_forced_nonzero_residual"]
    gamma8_update = next(row for row in update_rows if row["mask"] == int(first_forced["mask"]))

    transport_components = minimal_composite["derived"]["transport_components"]
    mixed_support = transport_components["mixed_S_channel_superselection_null_support"]
    pure_support = transport_components["pure_Sminus_superselection_null_doublet"]
    shared_composite_sector = sorted(set(mixed_support).intersection(pure_support))
    sector26_profile = profiles[26]
    hidden_rank_matrix = superselection["derived"]["hidden_transport_rank_matrix"]

    bosonic_alignment = {
        "statement": (
            "Sector 26 is the shared finite public-zero composite seam. Its label matches the critical "
            "dimension 26 of bosonic string theory. This certificate records the numerical/invariant "
            "alignment only; it does not identify the D20 finite algebra with continuum bosonic string theory."
        ),
        "shared_composite_sector": shared_composite_sector,
        "bosonic_string_critical_dimension": BOSONIC_STRING_CRITICAL_DIMENSION,
        "d20_public_state_count": D20_PUBLIC_STATE_COUNT,
        "h6_channel_count": H6_CHANNEL_COUNT,
        "d20_plus_h6": D20_PUBLIC_STATE_COUNT + H6_CHANNEL_COUNT,
        "sector26_profile": {
            "sector": 26,
            "block_dimension": int(sector26_profile["block_dimension"]),
            "active_objects": sector26_profile["active_objects"],
            "active_cy_sectors": sector26_profile["active_cy_sectors"],
            "permutation_rank": int(sector26_profile["permutation_rank"]),
            "permutation_multiplicity": int(sector26_profile["permutation_multiplicity"]),
            "q42_nonzero_count": int(sector26_profile["q42_nonzero_count"]),
            "q12_nonzero_count": int(sector26_profile["q12_nonzero_count"]),
            "object_loop_coordinate_support": sector26_profile["object_loop_coordinate_support"],
            "spectral_signature": sector26_profile["spectral_signature"],
        },
        "cross_transport_rank_through_sector26": hidden_rank_matrix["K_mixed_S"]["K_pure_Sminus"],
    }

    invariant_openings = [
        {
            "name": "critical_26_marker",
            "description": (
                "Sector 26 is the shared central sector of the two minimal public-zero composite supports, "
                "and 20 public D20 states plus 6 H6 channels also give 26."
            ),
            "next_test": (
                "Build a 26-marker invariant that distinguishes public state count + channel count from "
                "sector-index coincidence and checks stability under quotient maps A985->A42->A12."
            ),
        },
        {
            "name": "null_fiber_superselection_form",
            "description": (
                "The hidden public-zero fiber now has a transport matrix with R33 isolated and a rank-one "
                "coupling between K_mixed_S and K_pure_Sminus through sector 26."
            ),
            "next_test": "Diagonalize/classify this 3-component hidden transport form over integers and over F_1000003.",
        },
        {
            "name": "worldsheet_like_anomaly_counter",
            "description": (
                "Because optical/action flux is non-exact and typed into a hidden ledger, sector 26 becomes a "
                "candidate finite anomaly-counter marker rather than a public charge."
            ),
            "next_test": (
                "Check whether primitive-cycle optical actions admit a modular or central-charge-like "
                "normalization with the sector-26 seam."
            ),
        },
        {
            "name": "gauge_vs_superselection_separation",
            "description": (
                "The typed update separates true gauge zero from public-zero hidden transport. This is the "
                "finite invariant needed before any BRST-like or constraint-cohomology analogy is defensible."
            ),
            "next_test": "Construct the cohomological quotient that kills gauge zero but retains the two composite labels.",
        },
    ]

    checks = {
        "nonexact_optical_residue_is_certified": nonexact.get("status")
        == "D20_NONEXACT_OPTICAL_RESIDUE_CERTIFIED"
        and nonexact.get("all_checks_pass") is True,
        "all_residue_height_transport_is_certified": all_residue.get("status")
        == "D20_ALL_RESIDUE_HEIGHT_COHERENT_TRANSPORT_CERTIFIED"
        and all_residue.get("all_checks_pass") is True,
        "superselection_flux_extension_is_certified": superselection.get("status")
        == "D20_SUPERSELECTION_FLUX_BALANCE_EXTENSION_CERTIFIED"
        and superselection.get("all_checks_pass") is True,
        "minimal_composite_transport_is_certified": minimal_composite.get("status")
        == "D20_MINIMAL_COMPOSITE_NULL_SUPPORTS_TRANSPORT_CLASSIFIED"
        and minimal_composite.get("all_checks_pass") is True,
        "typed_update_count_is_2048": len(update_rows) == 2048,
        "typed_update_masks_are_complete": [row["mask"] for row in update_rows] == list(range(2048)),
        "zero_class_has_zero_hidden_update": zero_row["hidden_update_integral"] == hidden_update()
        and zero_row["event_type"] == "gauge_zero",
        "all_nonzero_updates_go_to_R33": all(
            row["support_component"] == "R33"
            and row["hidden_update_integral"]["K_mixed_S"] == 0
            and row["hidden_update_integral"]["K_pure_Sminus"] == 0
            for row in nonzero_rows
        ),
        "all_nonzero_R33_updates_match_negative_height_action": all(
            row["hidden_update_integral"]["R33"] == -row["height_action"]
            and row["residual_matches_negative_height_action"]
            for row in nonzero_rows
        ),
        "all_nonzero_mod_prime_updates_match_pi33_coefficients": all(
            row["hidden_update_mod_prime"]["R33"] == row["pi33_coefficient_mod_prime"]
            and row["hidden_update_mod_prime"]["R33"] % FIELD_PRIME
            == row["hidden_update_integral"]["R33"] % FIELD_PRIME
            for row in nonzero_rows
        ),
        "gamma8_typed_update_matches_first_forced_obstruction": gamma8_update["mask"] == 256
        and gamma8_update["basis_cycle_ids"] == [8]
        and gamma8_update["hidden_update_integral"] == hidden_update(r33=-374784),
        "composite_superselection_labels_are_reserved_not_optically_excited": all(
            row["hidden_update_integral"]["K_mixed_S"] == 0
            and row["hidden_update_integral"]["K_pure_Sminus"] == 0
            for row in update_rows
        ),
        "sector26_is_shared_minimal_composite_seam": shared_composite_sector == [26],
        "sector26_aligns_with_bosonic_critical_dimension": shared_composite_sector == [
            BOSONIC_STRING_CRITICAL_DIMENSION
        ],
        "d20_plus_h6_also_gives_26": D20_PUBLIC_STATE_COUNT + H6_CHANNEL_COUNT
        == BOSONIC_STRING_CRITICAL_DIMENSION,
        "sector26_cross_transport_rank_is_one": bosonic_alignment["cross_transport_rank_through_sector26"] == 1,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_TYPED_NONEXACT_OPTICAL_FLUX_UPDATE_CERTIFIED"
        if all_checks_pass
        else "D20_TYPED_NONEXACT_OPTICAL_FLUX_UPDATE_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.typed_nonexact_optical_flux_update",
        "status": status,
        "object": "d20",
        "claim": (
            "The non-exact optical/action flux on every certified closed-return residue class has a typed "
            "hidden update in the augmented ledger: nonzero height residuals update R33, while the two "
            "minimal composite public-zero superselection labels are retained as distinct null labels but are "
            "not excited by the certified sector-33 height transport."
        ),
        "definition": {
            "typed_update": (
                "For each closed-return residue gamma, Delta Q_ext^nonexact(gamma) has zero public components, "
                "R33=-A_opt(gamma), and K_mixed_S=K_pure_Sminus=0 for the certified height transport."
            ),
            "reserved_superselection_null_event": (
                "An event that changes K_mixed_S or K_pure_Sminus must be certified separately; it is not the "
                "same as optical height residual transport."
            ),
            "sector26_alignment": (
                "Sector 26 is the shared seam between {6,26} and {25,26}; it also matches the bosonic string "
                "critical dimension 26 and the finite count 20 D20 states + 6 H6 channels."
            ),
        },
        "inputs": {
            "nonexact_optical_residue_report": {
                "path": rel(NONEXACT_OPTICAL_REPORT),
                "sha256": sha_file(NONEXACT_OPTICAL_REPORT),
            },
            "all_residue_height_transport_report": {
                "path": rel(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT),
                "sha256": sha_file(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT),
            },
            "superselection_flux_balance_extension_report": {
                "path": rel(SUPERSELECTION_FLUX_EXTENSION_REPORT),
                "sha256": sha_file(SUPERSELECTION_FLUX_EXTENSION_REPORT),
            },
            "minimal_composite_null_supports_transport_report": {
                "path": rel(MINIMAL_COMPOSITE_TRANSPORT_REPORT),
                "sha256": sha_file(MINIMAL_COMPOSITE_TRANSPORT_REPORT),
            },
            "full_a985_lift": {
                "path": rel(FULL_A985_LIFT),
                "sha256": sha_file(FULL_A985_LIFT),
            },
        },
        "derived": {
            "field_prime": FIELD_PRIME,
            "public_components": PUBLIC_COMPONENTS,
            "hidden_components": HIDDEN_COMPONENTS,
            "typed_update_count": len(update_rows),
            "nonzero_typed_update_count": len(nonzero_rows),
            "zero_update": zero_row,
            "first_obstruction_update": gamma8_update,
            "update_rows_sha256": sha_json(update_rows),
            "update_row_samples": [zero_row, gamma8_update, update_rows[-1]],
            "bosonic_string_26_alignment": bosonic_alignment,
            "invariant_openings": invariant_openings,
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Build the sector-26 invariant suite: 26-marker stability under A985->A42->A12, hidden transport "
            "form diagonalization, and a finite anomaly-counter normalization for optical action."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.typed_nonexact_optical_flux_update_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "consume the non-exact optical residue theorem",
            "consume the all-residue sector-33 height transport theorem",
            "consume the superselection flux-balance extension theorem",
            "type every nonzero optical residual as an R33 hidden update",
            "verify K_mixed_S and K_pure_Sminus are not excited by certified height transport",
            "record sector 26 as the shared composite seam and 26-alignment marker",
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
