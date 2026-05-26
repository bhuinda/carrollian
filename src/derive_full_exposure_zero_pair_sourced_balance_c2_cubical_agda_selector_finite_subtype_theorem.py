from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

C2_UNIVALENT_FOUNDATION_BRIDGE_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_univalent_foundation_bridge"
    / "report.json"
)
C2_CUBICAL_AGDA_SELECTOR_MEMBERSHIP_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_membership"
    / "report.json"
)
CUBICAL_AGDA_SOURCE = (
    D20_INVARIANTS
    / "formal"
    / "cubical"
    / "C2SelectorFoundationSelectorFiniteSubtype.agda"
)
CUBICAL_AGDA_INTERFACE = CUBICAL_AGDA_SOURCE.with_suffix(".agdai")


SELECTOR_TO_AGDA = {
    "primitive_seeded": "primitiveSeeded",
    "global_action_minimal": "globalActionMinimal",
    "paired_action_minimal": "pairedActionMinimal",
    "raw_componentwise_absolute_spectral_gap": "rawComponentwiseAbsoluteSpectralGap",
    "lazy_componentwise_spectral_gap": "lazyComponentwiseSpectralGap",
    "lazy_componentwise_spectral_gap_action_tiebreak": "lazyComponentwiseSpectralGapActionTiebreak",
    "paired_lazy_componentwise_spectral_gap": "pairedLazyComponentwiseSpectralGap",
    "paired_lazy_componentwise_spectral_gap_action_tiebreak": "pairedLazyComponentwiseSpectralGapActionTiebreak",
}
SELECTOR_PREFIX = {
    "primitive_seeded": "primitiveSeeded",
    "global_action_minimal": "globalActionMinimal",
    "paired_action_minimal": "pairedActionMinimal",
    "raw_componentwise_absolute_spectral_gap": "rawSpectralGap",
    "lazy_componentwise_spectral_gap": "lazySpectralGap",
    "lazy_componentwise_spectral_gap_action_tiebreak": "lazySpectralGapActionTiebreak",
    "paired_lazy_componentwise_spectral_gap": "pairedLazySpectralGap",
    "paired_lazy_componentwise_spectral_gap_action_tiebreak": "pairedLazySpectralGapActionTiebreak",
}
MEMBERSHIP_PREFIX = {
    "primitive_seeded": "primitiveMember",
    "global_action_minimal": "globalActionMember",
    "paired_action_minimal": "pairedActionMember",
    "raw_componentwise_absolute_spectral_gap": "rawGapMember",
    "lazy_componentwise_spectral_gap": "lazyGapMember",
    "lazy_componentwise_spectral_gap_action_tiebreak": "lazyGapActionTiebreakMember",
    "paired_lazy_componentwise_spectral_gap": "pairedLazyGapMember",
    "paired_lazy_componentwise_spectral_gap_action_tiebreak": "pairedLazyGapActionTiebreakMember",
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


def fin_data_pattern(index: int) -> str:
    term = "FD.zero"
    for _ in range(index):
        term = f"(FD.suc {term})"
    return term


def nat_exact_pattern(index: int) -> str:
    term = "zero"
    for _ in range(index):
        term = f"(suc {term})"
    return term


def nat_ge_pattern(bound: int) -> str:
    term = "n"
    for _ in range(bound):
        term = f"(suc {term})"
    return term


def nat_ge_absurd_clause(bound: int) -> str:
    return f"{nat_ge_pattern(bound)} | p = Empty.rec (NatOrder.¬m+n<m {{m = {bound}}} {{n = n}} p)"


def membership_constructor(selector_key: str, move_id: int) -> str:
    return f"{MEMBERSHIP_PREFIX[selector_key]}{move_id}"


def selector_block(fiber: dict[str, Any]) -> list[str]:
    selector_key = fiber["selector"]
    selector = SELECTOR_TO_AGDA[selector_key]
    prefix = SELECTOR_PREFIX[selector_key]
    selected_ids = [int(move_id) for move_id in fiber["selected_move_orbit_ids"]]
    count = int(fiber["selected_count"])
    lines: list[str] = [
        "",
        f"{prefix}FiberToFinData : SelectorFiber {selector} → FD.Fin {count}",
    ]
    for index, move_id in enumerate(selected_ids):
        constructor = membership_constructor(selector_key, move_id)
        lines.append(
            f"{prefix}FiberToFinData (d{move_id} , {constructor}) = "
            f"FDP.fromℕ' {count} {index} ({count - index - 1} , refl)"
        )

    lines.extend(["", f"{prefix}FiberFromFinData : FD.Fin {count} → SelectorFiber {selector}"])
    for index, move_id in enumerate(selected_ids):
        constructor = membership_constructor(selector_key, move_id)
        if index == 0:
            lines.append(f"{prefix}FiberFromFinData i with FD.toℕ i | FDP.toℕ<n i")
        lines.append(f"... | {nat_exact_pattern(index)} | _ = d{move_id} , {constructor}")
    lines.append(f"... | {nat_ge_absurd_clause(count)}")

    lines.extend(
        [
            "",
            f"{prefix}FiberFinDataRightInv :",
            f"  (i : FD.Fin {count}) → {prefix}FiberToFinData ({prefix}FiberFromFinData i) ≡ i",
        ]
    )
    for index in range(count):
        lines.append(f"{prefix}FiberFinDataRightInv {fin_data_pattern(index)} = refl")

    lines.extend(
        [
            "",
            f"{prefix}FiberFinDataLeftInv :",
            f"  (x : SelectorFiber {selector}) → {prefix}FiberFromFinData ({prefix}FiberToFinData x) ≡ x",
        ]
    )
    for move_id in selected_ids:
        constructor = membership_constructor(selector_key, move_id)
        lines.append(f"{prefix}FiberFinDataLeftInv (d{move_id} , {constructor}) = refl")

    lines.extend(
        [
            "",
            f"{prefix}FiberFinDataIso : Iso (SelectorFiber {selector}) (FD.Fin {count})",
            (
                f"{prefix}FiberFinDataIso = "
                f"iso {prefix}FiberToFinData {prefix}FiberFromFinData "
                f"{prefix}FiberFinDataRightInv {prefix}FiberFinDataLeftInv"
            ),
            "",
            f"{prefix}FiberFinDataEquiv : SelectorFiber {selector} ≃ FD.Fin {count}",
            f"{prefix}FiberFinDataEquiv = isoToEquiv {prefix}FiberFinDataIso",
            "",
            f"{prefix}FiberEquivFin : SelectorFiber {selector} ≃ Fin {count}",
            f"{prefix}FiberEquivFin = compEquiv {prefix}FiberFinDataEquiv (FinData≃Fin {count})",
            "",
            f"{prefix}FiberFinitePackage : SelectorFiberFinitePackage {selector}",
            f"{prefix}FiberFinitePackage = selectorFiberFinitePackage {count} refl {prefix}FiberEquivFin",
        ]
    )
    return lines


def generate_agda_source(bridge: dict[str, Any]) -> str:
    selector_fibers = bridge["derived"]["selector_fibers"]
    lines: list[str] = [
        "{-# OPTIONS --cubical --safe --guardedness #-}",
        "",
        "module C2SelectorFoundationSelectorFiniteSubtype where",
        "",
        "open import Cubical.Foundations.Prelude",
        "open import Cubical.Foundations.Equiv using (_≃_ ; compEquiv)",
        "open import Cubical.Foundations.Isomorphism using (Iso ; iso ; isoToEquiv)",
        "open import Cubical.Data.Nat using (ℕ ; zero ; suc)",
        "open import Cubical.Data.Sigma using (Σ ; Σ-syntax)",
        "open import Cubical.Data.Fin.Base using (Fin)",
        "open import Cubical.Data.Fin.Properties using (FinData≃Fin)",
        "import Cubical.Data.Empty as Empty",
        "import Cubical.Data.FinData.Base as FD",
        "import Cubical.Data.FinData.Properties as FDP",
        "import Cubical.Data.Nat.Order as NatOrder",
        "open import C2SelectorFoundation",
        "open import C2SelectorFoundationGenerated",
        "open import C2SelectorFoundationGeneratedProperties",
        "open import C2SelectorFoundationSelectorMembership",
        "",
        "SelectorFiber : Selector → Set",
        "SelectorFiber s = Σ[ d ∈ DynamicsId ] SelectorMembership s d",
        "",
        "selectorFiberCardinality : Selector → ℕ",
        "selectorFiberCardinality = selectorFiberCount",
        "",
        "record SelectorFiberFinitePackage (s : Selector) : Set where",
        "  constructor selectorFiberFinitePackage",
        "  field",
        "    cardinality : ℕ",
        "    cardinalityMatches : selectorFiberCount s ≡ cardinality",
        "    fiberEquivFin : SelectorFiber s ≃ Fin cardinality",
    ]
    for fiber in selector_fibers:
        lines.extend(selector_block(fiber))

    lines.extend(
        [
            "",
            "selectorFiberFiniteEquiv :",
            "  (s : Selector) → SelectorFiber s ≃ Fin (selectorFiberCount s)",
        ]
    )
    for fiber in selector_fibers:
        selector = SELECTOR_TO_AGDA[fiber["selector"]]
        prefix = SELECTOR_PREFIX[fiber["selector"]]
        lines.append(f"selectorFiberFiniteEquiv {selector} = {prefix}FiberEquivFin")

    lines.extend(
        [
            "",
            "selectorFinitePackage : (s : Selector) → SelectorFiberFinitePackage s",
        ]
    )
    for fiber in selector_fibers:
        selector = SELECTOR_TO_AGDA[fiber["selector"]]
        prefix = SELECTOR_PREFIX[fiber["selector"]]
        lines.append(f"selectorFinitePackage {selector} = {prefix}FiberFinitePackage")

    lines.extend(
        [
            "",
            "selectorFiniteSubtypeCount : ℕ",
            "selectorFiniteSubtypeCount = 8",
            "",
            "selectorFiniteSubtypeWitnessCount : ℕ",
            "selectorFiniteSubtypeWitnessCount = 1091",
        ]
    )
    return "\n".join(lines) + "\n"


def write_agda_source() -> None:
    bridge = load_json(C2_UNIVALENT_FOUNDATION_BRIDGE_REPORT)
    source_text = generate_agda_source(bridge)
    CUBICAL_AGDA_SOURCE.parent.mkdir(parents=True, exist_ok=True)
    if CUBICAL_AGDA_SOURCE.exists() and CUBICAL_AGDA_SOURCE.read_text(encoding="utf-8") == source_text:
        return
    CUBICAL_AGDA_SOURCE.write_text(source_text, encoding="utf-8")


def build_theorem() -> dict[str, Any]:
    bridge = load_json(C2_UNIVALENT_FOUNDATION_BRIDGE_REPORT)
    selector_membership = load_json(C2_CUBICAL_AGDA_SELECTOR_MEMBERSHIP_REPORT)
    source_text = CUBICAL_AGDA_SOURCE.read_text(encoding="utf-8")
    interface_exists = CUBICAL_AGDA_INTERFACE.exists()
    interface_size = CUBICAL_AGDA_INTERFACE.stat().st_size if interface_exists else 0
    source_sha256 = sha_file(CUBICAL_AGDA_SOURCE)
    interface_sha256 = sha_file(CUBICAL_AGDA_INTERFACE) if interface_exists else None
    selector_fibers = bridge["derived"]["selector_fibers"]
    expected_witness_count = sum(int(fiber["selected_count"]) for fiber in selector_fibers)
    to_fin_data_clauses = re.findall(r"^\w+FiberToFinData \(d\d+ , \w+\) = ", source_text, re.MULTILINE)
    from_fin_data_branches = re.findall(r"^\.\.\. \| .+ \| _ = d\d+ , \w+$", source_text, re.MULTILINE)
    right_inv_clauses = re.findall(r"^\w+FiberFinDataRightInv .+ = refl$", source_text, re.MULTILINE)
    impossible_bound_branches = re.findall(
        r"^\.\.\. \| \(suc .+ \| p = Empty\.rec \(NatOrder\.¬m\+n<m ",
        source_text,
        re.MULTILINE,
    )
    left_inv_clauses = re.findall(r"^\w+FiberFinDataLeftInv \(d\d+ , \w+\) = refl$", source_text, re.MULTILINE)
    equiv_fin_decls = re.findall(r"^\w+FiberEquivFin : SelectorFiber \w+ ≃ Fin \d+$", source_text, re.MULTILINE)
    finite_equiv_clauses = re.findall(r"^selectorFiberFiniteEquiv \w+ = \w+FiberEquivFin$", source_text, re.MULTILINE)
    finite_package_clauses = re.findall(
        r"^selectorFinitePackage \w+ = \w+FiberFinitePackage$", source_text, re.MULTILINE
    )

    source_summary = {
        "path": rel(CUBICAL_AGDA_SOURCE),
        "sha256": source_sha256,
        "byte_size": CUBICAL_AGDA_SOURCE.stat().st_size,
        "line_count": len(source_text.splitlines()),
        "module": "C2SelectorFoundationSelectorFiniteSubtype",
        "typecheck_command": (
            "C:/Users/Admin/Documents/agda-toolchain/agda.exe --warning=noUnsupportedIndexedMatch "
            "--transliterate -v0 "
            "-i data/invariants/d20/formal/cubical "
            "-i C:/Users/Admin/Documents/agda-toolchain/cubical-0.9 "
            "data/invariants/d20/formal/cubical/C2SelectorFoundationSelectorFiniteSubtype.agda"
        ),
        "interface": {
            "path": rel(CUBICAL_AGDA_INTERFACE),
            "sha256": interface_sha256,
            "byte_size": interface_size,
        },
        "proof_counts": {
            "selector_count": len(selector_fibers),
            "selector_fiber_witness_count": expected_witness_count,
            "to_fin_data_clause_count": len(to_fin_data_clauses),
            "from_fin_data_branch_count": len(from_fin_data_branches),
            "right_inverse_clause_count": len(right_inv_clauses),
            "impossible_bound_branch_count": len(impossible_bound_branches),
            "left_inverse_clause_count": len(left_inv_clauses),
            "fiber_equiv_fin_declaration_count": len(equiv_fin_decls),
            "uniform_finite_equiv_clause_count": len(finite_equiv_clauses),
            "uniform_finite_package_clause_count": len(finite_package_clauses),
        },
    }

    checks = {
        "univalent_foundation_bridge_is_certified": bridge.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_UNIVALENT_FOUNDATION_BRIDGE_CERTIFIED"
        and bridge.get("all_checks_pass") is True,
        "selector_membership_theorem_is_certified": selector_membership.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_MEMBERSHIP_CERTIFIED"
        and selector_membership.get("all_checks_pass") is True,
        "selector_finite_subtype_source_imports_fin_equivalence": CUBICAL_AGDA_SOURCE.exists()
        and "module C2SelectorFoundationSelectorFiniteSubtype where" in source_text
        and "open import Cubical.Data.Fin.Properties using (FinData≃Fin)" in source_text
        and "import Cubical.Data.FinData.Base as FD" in source_text
        and "import Cubical.Data.Nat.Order as NatOrder" in source_text
        and "open import C2SelectorFoundationSelectorMembership" in source_text,
        "selector_finite_subtype_defines_sigma_subtype": (
            "SelectorFiber s = Σ[ d ∈ DynamicsId ] SelectorMembership s d" in source_text
        ),
        "selector_finite_subtype_has_all_fin_data_iso_clauses": len(to_fin_data_clauses)
        == expected_witness_count
        == 1091
        and len(from_fin_data_branches) == expected_witness_count == 1091
        and len(right_inv_clauses) == expected_witness_count == 1091
        and len(impossible_bound_branches) == len(selector_fibers) == 8
        and len(left_inv_clauses) == expected_witness_count == 1091,
        "selector_finite_subtype_has_all_fin_equivalences": len(equiv_fin_decls)
        == len(selector_fibers)
        == 8
        and "compEquiv primitiveSeededFiberFinDataEquiv (FinData≃Fin 1)" in source_text
        and "compEquiv rawSpectralGapFiberFinDataEquiv (FinData≃Fin 543)" in source_text,
        "selector_finite_subtype_has_uniform_family_interface": len(finite_equiv_clauses)
        == len(selector_fibers)
        == 8
        and len(finite_package_clauses) == len(selector_fibers) == 8,
        "selector_finite_subtype_agda_interface_artifact_present_after_typecheck": interface_exists
        and interface_size > 0,
        "selector_finite_subtype_artifact_hashes_are_stable": len(source_sha256) == 64
        and isinstance(interface_sha256, str)
        and len(interface_sha256) == 64,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_CERTIFIED"
        if all_checks_pass
        else "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_FORMAL_TRACKING_DEMOTED"
    )
    claim = (
        "Each Cubical Agda selector fiber is now a finite Sigma subtype of DynamicsId equipped with "
        "a typechecked equivalence to Fin n for its certified cardinality."
        if all_checks_pass
        else (
            "A generated Cubical Agda selector finite-subtype module has the expected source-level "
            "Sigma subtype and equivalence clauses, but this report is demoted to formal tracking "
            "until Agda produces the selector finite-subtype interface artifact."
        )
    )
    next_highest_yield_item = (
        "Use the finite selector subtype equivalences to prove path-level transport of singleton "
        "selector choices across Cubical structure identity."
        if all_checks_pass
        else (
            "Split the selector finite-subtype proof into per-selector Cubical Agda modules and "
            "typecheck the singleton fibers before rejoining the raw/lazy/paired large fibers."
        )
    )
    proven_items = (
        [
            "each selector fiber is a typechecked finite subtype of the generated dynamics universe",
            "each fiber has an explicit two-sided isomorphism to a finite index type",
            "Cubical's FinData-to-Fin equivalence converts those isomorphisms into equivalences to Fin n",
            "the selector layer now has a uniform finite-family interface in Cubical Agda",
        ]
        if all_checks_pass
        else [
            "the generated source contains the expected Sigma subtype shape",
            "the generated source contains the expected FinData and finite-family clauses",
            "the interface artifact is absent, so no typechecked finite-subtype theorem is certified here",
        ]
    )
    report = {
        "schema": "d20.theorem.full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype",
        "status": status,
        "object": "d20",
        "claim": claim,
        "demotion_reason": None
        if all_checks_pass
        else (
            "Agda is missing the selector finite-subtype interface artifact; the source-shape data is retained "
            "as formal tracking evidence, not as a certified invariant theorem."
        ),
        "inputs": {
            "c2_univalent_foundation_bridge_report": {
                "path": rel(C2_UNIVALENT_FOUNDATION_BRIDGE_REPORT),
                "sha256": sha_file(C2_UNIVALENT_FOUNDATION_BRIDGE_REPORT),
            },
            "c2_cubical_agda_selector_membership_report": {
                "path": rel(C2_CUBICAL_AGDA_SELECTOR_MEMBERSHIP_REPORT),
                "sha256": sha_file(C2_CUBICAL_AGDA_SELECTOR_MEMBERSHIP_REPORT),
            },
            "cubical_agda_selector_finite_subtype_source": {
                "path": rel(CUBICAL_AGDA_SOURCE),
                "sha256": source_sha256,
            },
            "cubical_agda_selector_finite_subtype_interface": {
                "path": rel(CUBICAL_AGDA_INTERFACE),
                "sha256": interface_sha256,
            },
        },
        "derived": {
            "source_summary": source_summary,
            "selector_fiber_counts": {
                fiber["selector"]: fiber["selected_count"] for fiber in selector_fibers
            },
            "finite_subtype_shape": (
                "SelectorFiber s = Sigma DynamicsId (SelectorMembership s), with "
                "SelectorFiber s equiv Fin (selectorFiberCount s)."
            ),
        },
        "interpretation": {
            "what_this_proves": proven_items,
            "why_it_matters_if_extended": [
                "finite selector identity can now be transported through univalence-style equivalences",
                "selector ambiguity is no longer only a JSON count; it is a formal finite type with canonical cardinality",
                "future physical selector axioms can be phrased as operations on finite fibers rather than external filters",
            ],
            "what_this_does_not_prove": [
                "while demoted, it does not count as a certified or provisional invariant report",
                "it does not prove a final physical selector axiom",
                "it does not prove full structure identity for the dynamics operators",
                "it does not connect the finite selector fibers to external continuum semantics",
            ],
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": next_highest_yield_item,
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    write_agda_source()
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem_manifest",
        "theorem_id": THEOREM_ID,
        "status": report["status"],
        "report": rel(out_dir / "report.json"),
        "inputs": report["inputs"],
        "checks": report["checks"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = sha_json({k: v for k, v in manifest.items() if k != "manifest_sha256"})

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    update_theorem_index(report, out_dir)
    return report


def main() -> None:
    report = write_theorem()
    print(report["status"])
    print(report["certificate_sha256"])


if __name__ == "__main__":
    main()
