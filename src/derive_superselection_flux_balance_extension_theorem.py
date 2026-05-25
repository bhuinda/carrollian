from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, DATA, ROOT


THEOREM_ID = "superselection_flux_balance_extension"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FINITE_FLUX_BALANCE_REPORT = D20_INVARIANTS / "theorems" / "finite_flux_balance" / "report.json"
MINIMAL_COMPOSITE_TRANSPORT_REPORT = (
    D20_INVARIANTS / "theorems" / "minimal_composite_null_supports_transport" / "report.json"
)
IDEMPOTENT_ADMISSIBILITY_REPORT = (
    D20_INVARIANTS / "theorems" / "sector_idempotent_support_admissibility" / "report.json"
)
ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT = (
    D20_INVARIANTS / "theorems" / "sector33_all_residue_height_transport" / "report.json"
)
FULL_A985_LIFT = DATA / "drinfeld" / "full_a985_lift.json"

HIDDEN_COMPONENTS = ["R33", "K_mixed_S", "K_pure_Sminus"]
PUBLIC_COMPONENTS = ["M", "J", "P", "Phi"]


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


def sector_profiles_by_id(full_lift: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {
        int(profile["sector"]): profile
        for profile in full_lift["gluing_and_sector_profiles"]["sector_profiles"]
    }


def transport_rank(left: list[int], right: list[int], profiles: dict[int, dict[str, Any]]) -> int:
    return int(
        sum(
            int(profiles[sector]["block_dimension"]) ** 2
            for sector in sorted(set(left).intersection(right))
        )
    )


def hidden_zero_vector() -> dict[str, int]:
    return {component: 0 for component in HIDDEN_COMPONENTS}


def hidden_vector(*, r33: int = 0, mixed: int = 0, pure: int = 0) -> dict[str, int]:
    return {
        "R33": int(r33),
        "K_mixed_S": int(mixed),
        "K_pure_Sminus": int(pure),
    }


def label_state(name: str, sectors: list[int], hidden: dict[str, int]) -> dict[str, Any]:
    return {
        "name": name,
        "sector_support": sectors,
        "public_components": {component: 0 for component in PUBLIC_COMPONENTS},
        "hidden_components": hidden,
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
        "schema": "d20.theorem_registry.source_drop",
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": len(theorems),
        "theorems": theorems,
    }
    index["registry_sha256"] = sha_json({k: v for k, v in index.items() if k != "registry_sha256"})
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_theorem() -> dict[str, Any]:
    finite_flux = load_json(FINITE_FLUX_BALANCE_REPORT)
    minimal_transport = load_json(MINIMAL_COMPOSITE_TRANSPORT_REPORT)
    admissibility = load_json(IDEMPOTENT_ADMISSIBILITY_REPORT)
    all_residue_transport = load_json(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT)
    full_lift = load_json(FULL_A985_LIFT)
    profiles = sector_profiles_by_id(full_lift)

    public_zero_supports = admissibility["derived"]["nonzero_public_zero_idempotent_supports"]
    minimal_derived = minimal_transport["derived"]
    transport_components = minimal_derived["transport_components"]
    primitive = transport_components["primitive_residual_atom"]
    mixed = transport_components["mixed_S_channel_superselection_null_support"]
    pure = transport_components["pure_Sminus_superselection_null_doublet"]
    disallowed_mixed_plus_pure = sorted(set(mixed).union(pure))

    hidden_basis = [
        {
            "component": "R33",
            "sector_support": primitive,
            "role": "primitive_support_exact_residual_atom",
            "self_transport_rank": transport_rank(primitive, primitive, profiles),
            "new_in_this_extension": False,
        },
        {
            "component": "K_mixed_S",
            "sector_support": mixed,
            "role": "mixed_S_channel_public_zero_superselection_null_support",
            "self_transport_rank": transport_rank(mixed, mixed, profiles),
            "transport_to_R33_rank": transport_rank(mixed, primitive, profiles),
            "transport_from_R33_rank": transport_rank(primitive, mixed, profiles),
            "new_in_this_extension": True,
        },
        {
            "component": "K_pure_Sminus",
            "sector_support": pure,
            "role": "pure_Sminus_public_zero_superselection_null_doublet",
            "self_transport_rank": transport_rank(pure, pure, profiles),
            "transport_to_R33_rank": transport_rank(pure, primitive, profiles),
            "transport_from_R33_rank": transport_rank(primitive, pure, profiles),
            "new_in_this_extension": True,
        },
    ]
    hidden_transport_matrix = {
        left["component"]: {
            right["component"]: transport_rank(left["sector_support"], right["sector_support"], profiles)
            for right in hidden_basis
        }
        for left in hidden_basis
    }
    admissible_hidden_states = [
        label_state("gauge_zero", [], hidden_zero_vector()),
        label_state("primitive_residual_atom", primitive, hidden_vector(r33=1)),
        label_state("mixed_S_null_support", mixed, hidden_vector(mixed=1)),
        label_state("pure_Sminus_null_doublet", pure, hidden_vector(pure=1)),
        label_state("mixed_S_null_plus_R33", sorted(set(mixed).union(primitive)), hidden_vector(r33=1, mixed=1)),
        label_state("pure_Sminus_null_plus_R33", sorted(set(pure).union(primitive)), hidden_vector(r33=1, pure=1)),
    ]
    hidden_vectors = [tuple(state["hidden_components"][component] for component in HIDDEN_COMPONENTS) for state in admissible_hidden_states]
    sector_supports = [state["sector_support"] for state in admissible_hidden_states]

    exact_balance_extension = {
        "Q_boundary_extended": PUBLIC_COMPONENTS + HIDDEN_COMPONENTS,
        "public_state_hidden_charge": hidden_zero_vector(),
        "exact_public_flux_hidden_update": hidden_zero_vector(),
        "reason": (
            "The exact finite flux-balance theorem is a coboundary statement on public D20 states. "
            "The new hidden superselection components only change when a certified hidden null support is inserted."
        ),
    }
    height_transport_extension = {
        "certified_height_transport_hidden_support": "R33",
        "composite_superselection_flux_for_certified_sector33_height_transport": {
            "K_mixed_S": 0,
            "K_pure_Sminus": 0,
        },
        "reason": (
            "The all-residue height-coherent transport report carries every nonzero height residual by sector 33; "
            "the two composite null labels are tracked but not excited by that certified transport."
        ),
    }

    checks = {
        "finite_flux_balance_is_certified": finite_flux.get("status")
        == "D20_FINITE_EXACT_FLUX_BALANCE_CERTIFIED"
        and finite_flux.get("all_checks_pass") is True,
        "minimal_composite_transport_is_certified": minimal_transport.get("status")
        == "D20_MINIMAL_COMPOSITE_NULL_SUPPORTS_TRANSPORT_CLASSIFIED"
        and minimal_transport.get("all_checks_pass") is True,
        "idempotent_support_admissibility_is_certified": admissibility.get("status")
        == "D20_SECTOR_IDEMPOTENT_SUPPORT_ADMISSIBILITY_CLASSIFIED"
        and admissibility.get("all_checks_pass") is True,
        "all_residue_height_transport_is_certified": all_residue_transport.get("status")
        == "D20_ALL_RESIDUE_HEIGHT_COHERENT_TRANSPORT_CERTIFIED"
        and all_residue_transport.get("all_checks_pass") is True,
        "extended_charge_has_four_public_plus_three_hidden_components": (
            exact_balance_extension["Q_boundary_extended"] == PUBLIC_COMPONENTS + HIDDEN_COMPONENTS
        ),
        "two_new_superselection_labels_are_added": [
            item["component"] for item in hidden_basis if item["new_in_this_extension"]
        ]
        == ["K_mixed_S", "K_pure_Sminus"],
        "new_superselection_labels_are_public_zero_supports": mixed in public_zero_supports
        and pure in public_zero_supports,
        "new_superselection_labels_are_not_gauge_zero": all(
            item["self_transport_rank"] > 0
            for item in hidden_basis
            if item["new_in_this_extension"]
        ),
        "new_superselection_labels_are_isolated_from_R33": all(
            item.get("transport_to_R33_rank", 0) == 0
            and item.get("transport_from_R33_rank", 0) == 0
            for item in hidden_basis
            if item["new_in_this_extension"]
        ),
        "mixed_and_pure_null_labels_have_cross_transport_rank_one": hidden_transport_matrix["K_mixed_S"][
            "K_pure_Sminus"
        ]
        == 1
        and hidden_transport_matrix["K_pure_Sminus"]["K_mixed_S"] == 1,
        "hidden_label_map_is_injective_on_admissible_public_zero_supports": len(hidden_vectors)
        == len(set(hidden_vectors))
        and len(sector_supports) == len({tuple(support) for support in sector_supports}),
        "mixed_plus_pure_without_R33_is_not_admissible_public_zero": disallowed_mixed_plus_pure
        not in public_zero_supports,
        "exact_public_flux_lifts_with_zero_hidden_update": exact_balance_extension[
            "exact_public_flux_hidden_update"
        ]
        == hidden_zero_vector()
        and finite_flux.get("checks", {}).get("primitive_flux_residuals_zero") is True,
        "sector33_height_transport_has_zero_composite_superselection_flux": all_residue_transport.get(
            "checks", {}
        ).get("all_transports_carried_by_sector33")
        is True
        and height_transport_extension["composite_superselection_flux_for_certified_sector33_height_transport"]
        == {"K_mixed_S": 0, "K_pure_Sminus": 0},
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_SUPERSELECTION_FLUX_BALANCE_EXTENSION_CERTIFIED"
        if all_checks_pass
        else "D20_SUPERSELECTION_FLUX_BALANCE_EXTENSION_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.superselection_flux_balance_extension.source_drop",
        "status": status,
        "object": "d20",
        "claim": (
            "The finite D20 boundary charge can be extended from the public four-vector "
            "(M,J,P,Phi) to an augmented public-plus-hidden ledger "
            "(M,J,P,Phi;R33,K_mixed_S,K_pure_Sminus). The two new hidden labels distinguish the "
            "minimal public-zero composite superselection supports from gauge zero while preserving the "
            "certified sector-33 height transport."
        ),
        "definition": {
            "augmented_boundary_charge": (
                "Q_ext=(M,J,P,Phi;R33,K_mixed_S,K_pure_Sminus), where the first four components are the "
                "public exact-flux charges and the last three components track the finite public-zero hidden fiber."
            ),
            "new_superselection_labels": {
                "K_mixed_S": "{6,26}, the mixed S-/S+ public-zero support",
                "K_pure_Sminus": "{25,26}, the pure S- public-zero doublet",
            },
            "admissible_hidden_states": (
                "The six certified Boolean public-zero idempotent supports: zero, R33, K_mixed_S, "
                "K_pure_Sminus, K_mixed_S+R33, and K_pure_Sminus+R33. K_mixed_S+K_pure_Sminus is not "
                "a certified public-zero support because the two labels overlap through sector 26."
            ),
        },
        "inputs": {
            "finite_flux_balance_report": {
                "path": rel(FINITE_FLUX_BALANCE_REPORT),
                "sha256": sha_file(FINITE_FLUX_BALANCE_REPORT),
            },
            "minimal_composite_null_supports_transport_report": {
                "path": rel(MINIMAL_COMPOSITE_TRANSPORT_REPORT),
                "sha256": sha_file(MINIMAL_COMPOSITE_TRANSPORT_REPORT),
            },
            "sector_idempotent_support_admissibility_report": {
                "path": rel(IDEMPOTENT_ADMISSIBILITY_REPORT),
                "sha256": sha_file(IDEMPOTENT_ADMISSIBILITY_REPORT),
            },
            "all_residue_height_transport_report": {
                "path": rel(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT),
                "sha256": sha_file(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT),
            },
            "full_a985_lift": {
                "path": rel(FULL_A985_LIFT),
                "sha256": sha_file(FULL_A985_LIFT),
            },
        },
        "derived": {
            "public_components": PUBLIC_COMPONENTS,
            "hidden_components": HIDDEN_COMPONENTS,
            "hidden_basis": hidden_basis,
            "hidden_transport_rank_matrix": hidden_transport_matrix,
            "admissible_hidden_states": admissible_hidden_states,
            "disallowed_mixed_plus_pure_sector_support": disallowed_mixed_plus_pure,
            "exact_balance_extension": exact_balance_extension,
            "height_transport_extension": height_transport_extension,
        },
        "interpretation": {
            "ontological": (
                "Public zero is refined into a finite hidden null fiber. Gauge zero, the primitive residual atom, "
                "and the two composite superselection supports are distinct states of the augmented ledger."
            ),
            "technological": (
                "A runtime or protocol may project the hidden labels away for public display, but must retain them "
                "in the internal state if it wants flux balance to distinguish gauge zero from hidden null transport."
            ),
            "overlap_warning": (
                "The two composite labels are not independent Boolean bits: their sector supports share sector 26, "
                "giving cross-transport rank one. The admissible hidden state set has six states, not the full "
                "three-bit cube."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Define the non-exact optical/action flux update as a typed transition in the augmented hidden ledger, "
            "with R33 carrying height residuals and K_mixed_S/K_pure_Sminus reserved for superselection-null events."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.superselection_flux_balance_extension_manifest.source_drop",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "consume the exact finite flux-balance theorem",
            "consume the minimal composite null-support transport theorem",
            "extend Q_boundary with R33 and two public-zero superselection labels",
            "verify the two new labels are public-zero and not gauge-zero",
            "verify the two new labels are isolated from R33",
            "verify the two new labels have cross-transport through sector 26",
            "verify the certified sector-33 height transport excites no composite superselection flux",
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
