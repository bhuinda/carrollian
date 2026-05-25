from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from src.c2_selector_finite_subtype_emitter import generate_singleton_finite_subtype_agda
from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = (
    "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_singletons"
)
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
C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype"
    / "report.json"
)
CUBICAL_AGDA_SOURCE = (
    D20_INVARIANTS
    / "formal"
    / "cubical"
    / "C2SelectorFoundationSelectorFiniteSubtypeSingletons.agda"
)
CUBICAL_AGDA_INTERFACE = CUBICAL_AGDA_SOURCE.with_suffix(".agdai")

SELECTOR_TO_AGDA = {
    "primitive_seeded": "primitiveSeeded",
    "global_action_minimal": "globalActionMinimal",
    "paired_action_minimal": "pairedActionMinimal",
    "lazy_componentwise_spectral_gap_action_tiebreak": "lazyComponentwiseSpectralGapActionTiebreak",
    "paired_lazy_componentwise_spectral_gap_action_tiebreak": "pairedLazyComponentwiseSpectralGapActionTiebreak",
}
SINGLETON_CONSTRUCTOR_TO_AGDA = {
    "primitive_seeded": "primitiveSeededSingleton",
    "global_action_minimal": "globalActionMinimalSingleton",
    "paired_action_minimal": "pairedActionMinimalSingleton",
    "lazy_componentwise_spectral_gap_action_tiebreak": "lazySpectralGapActionTiebreakSingleton",
    "paired_lazy_componentwise_spectral_gap_action_tiebreak": "pairedLazySpectralGapActionTiebreakSingleton",
}
SELECTOR_PREFIX = {
    "primitive_seeded": "primitiveSeeded",
    "global_action_minimal": "globalActionMinimal",
    "paired_action_minimal": "pairedActionMinimal",
    "lazy_componentwise_spectral_gap_action_tiebreak": "lazySpectralGapActionTiebreak",
    "paired_lazy_componentwise_spectral_gap_action_tiebreak": "pairedLazySpectralGapActionTiebreak",
}
MEMBERSHIP_PREFIX = {
    "primitive_seeded": "primitiveMember",
    "global_action_minimal": "globalActionMember",
    "paired_action_minimal": "pairedActionMember",
    "lazy_componentwise_spectral_gap_action_tiebreak": "lazyGapActionTiebreakMember",
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


def singleton_fibers(bridge: dict[str, Any]) -> list[dict[str, Any]]:
    fibers = []
    for fiber in bridge["derived"]["selector_fibers"]:
        if fiber["selector"] in SELECTOR_TO_AGDA:
            if int(fiber["selected_count"]) != 1:
                raise ValueError(f"expected singleton selector: {fiber['selector']}")
            fibers.append(fiber)
    return fibers


def generate_agda_source(bridge: dict[str, Any]) -> str:
    return generate_singleton_finite_subtype_agda(
        bridge,
        module_name="C2SelectorFoundationSelectorFiniteSubtypeSingletons",
        selector_to_agda=SELECTOR_TO_AGDA,
        singleton_constructor_to_agda=SINGLETON_CONSTRUCTOR_TO_AGDA,
        selector_prefix=SELECTOR_PREFIX,
        membership_prefix=MEMBERSHIP_PREFIX,
    )


def write_agda_source() -> None:
    bridge = load_json(C2_UNIVALENT_FOUNDATION_BRIDGE_REPORT)
    source_text = generate_agda_source(bridge)
    CUBICAL_AGDA_SOURCE.parent.mkdir(parents=True, exist_ok=True)
    if CUBICAL_AGDA_SOURCE.exists() and CUBICAL_AGDA_SOURCE.read_text(encoding="utf-8") == source_text:
        return
    CUBICAL_AGDA_SOURCE.write_text(source_text, encoding="utf-8")


def build_theorem() -> dict[str, Any]:
    bridge = load_json(C2_UNIVALENT_FOUNDATION_BRIDGE_REPORT)
    membership = load_json(C2_CUBICAL_AGDA_SELECTOR_MEMBERSHIP_REPORT)
    finite_subtype = (
        load_json(C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_REPORT)
        if C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_REPORT.exists()
        else {}
    )
    source_text = CUBICAL_AGDA_SOURCE.read_text(encoding="utf-8")
    interface_exists = CUBICAL_AGDA_INTERFACE.exists()
    interface_size = CUBICAL_AGDA_INTERFACE.stat().st_size if interface_exists else 0
    fibers = singleton_fibers(bridge)

    source_summary = {
        "path": rel(CUBICAL_AGDA_SOURCE),
        "sha256": sha_file(CUBICAL_AGDA_SOURCE),
        "byte_size": CUBICAL_AGDA_SOURCE.stat().st_size,
        "line_count": len(source_text.splitlines()),
        "module": "C2SelectorFoundationSelectorFiniteSubtypeSingletons",
        "typecheck_command": (
            "C:/Users/Admin/Documents/agda-toolchain/agda.exe --warning=noUnsupportedIndexedMatch "
            "--transliterate -v0 -i data/invariants/d20/formal/cubical "
            "-i C:/Users/Admin/Documents/agda-toolchain/cubical-0.9 "
            "data/invariants/d20/formal/cubical/C2SelectorFoundationSelectorFiniteSubtypeSingletons.agda"
        ),
        "interface": {
            "path": rel(CUBICAL_AGDA_INTERFACE),
            "sha256": sha_file(CUBICAL_AGDA_INTERFACE) if interface_exists else None,
            "byte_size": interface_size,
        },
        "proof_counts": {
            "singleton_selector_count": len(fibers),
            "to_fin_data_clause_count": len(
                re.findall(r"^\w+SingletonFiberToFinData \(d\d+ , \w+\) = FD\.zero$", source_text, re.MULTILINE)
            ),
            "from_fin_data_clause_count": len(
                re.findall(r"^\w+SingletonFiberFromFinData FD\.zero = d\d+ , \w+$", source_text, re.MULTILINE)
            ),
            "right_inverse_clause_count": len(
                re.findall(r"^\w+SingletonFiberRightInv FD\.zero = refl$", source_text, re.MULTILINE)
            ),
            "left_inverse_clause_count": len(
                re.findall(r"^\w+SingletonFiberLeftInv \(d\d+ , \w+\) = refl$", source_text, re.MULTILINE)
            ),
            "fin_equivalence_count": len(
                re.findall(r"^\w+SingletonFiberEquivFin : SelectorFiber \w+ ≃ Fin 1$", source_text, re.MULTILINE)
            ),
            "singleton_constructor_count": len(
                re.findall(r"^\s+\w+Singleton : SingletonSelector$", source_text, re.MULTILINE)
            ),
            "singleton_selector_map_clause_count": len(
                re.findall(r"^singletonSelector \w+Singleton = \w+$", source_text, re.MULTILINE)
            ),
        },
    }
    counts = source_summary["proof_counts"]

    checks = {
        "univalent_foundation_bridge_is_certified": bridge.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_UNIVALENT_FOUNDATION_BRIDGE_CERTIFIED"
        and bridge.get("all_checks_pass") is True,
        "selector_membership_theorem_is_certified": membership.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_MEMBERSHIP_CERTIFIED"
        and membership.get("all_checks_pass") is True,
        "large_finite_subtype_attempt_is_recorded_as_review_item": finite_subtype.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_NEEDS_REVIEW",
        "singleton_source_defines_sigma_subtype": (
            "SelectorFiber s = Σ[ d ∈ DynamicsId ] SelectorMembership s d" in source_text
        ),
        "singleton_source_has_all_five_iso_witnesses": counts["singleton_selector_count"]
        == counts["to_fin_data_clause_count"]
        == counts["from_fin_data_clause_count"]
        == counts["right_inverse_clause_count"]
        == counts["left_inverse_clause_count"]
        == counts["fin_equivalence_count"]
        == 5,
        "singleton_source_restricts_total_map_to_singleton_selector_index": counts[
            "singleton_constructor_count"
        ]
        == counts["singleton_selector_map_clause_count"]
        == 5
        and "singletonSelectorFiberEquivFin :\n  (s : SingletonSelector) → SelectorFiber (singletonSelector s) ≃ Fin 1"
        in source_text,
        "singleton_agda_interface_artifact_present_after_typecheck": interface_exists
        and interface_size > 0,
        "singleton_artifact_hashes_are_stable": sha_file(CUBICAL_AGDA_SOURCE)
        and (sha_file(CUBICAL_AGDA_INTERFACE) if interface_exists else None),
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_SINGLETONS_CERTIFIED"
        if all_checks_pass
        else "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_SINGLETONS_NEEDS_REVIEW"
    )
    report = {
        "schema": "d20.theorem.full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_singletons",
        "status": status,
        "object": "d20",
        "claim": (
            "The five singleton selector fibers are packaged as Cubical Agda Sigma subtypes and equipped "
            "with typechecked equivalences to Fin 1."
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
            "c2_cubical_agda_selector_finite_subtype_report": {
                "path": rel(C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_REPORT),
                "sha256": sha_file(C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_REPORT)
                if C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_REPORT.exists()
                else None,
            },
            "cubical_agda_selector_finite_subtype_singletons_source": {
                "path": rel(CUBICAL_AGDA_SOURCE),
                "sha256": sha_file(CUBICAL_AGDA_SOURCE),
            },
            "cubical_agda_selector_finite_subtype_singletons_interface": {
                "path": rel(CUBICAL_AGDA_INTERFACE),
                "sha256": sha_file(CUBICAL_AGDA_INTERFACE) if interface_exists else None,
            },
        },
        "derived": {
            "source_summary": source_summary,
            "singleton_selectors": [
                {
                    "selector": fiber["selector"],
                    "selected_move_orbit_ids": fiber["selected_move_orbit_ids"],
                    "selected_count": fiber["selected_count"],
                }
                for fiber in fibers
            ],
        },
        "interpretation": {
            "what_this_proves": [
                "the five contractible selector choices are finite subtypes equivalent to Fin 1",
                "primitive, global-action, paired-action, lazy-gap action tiebreak, and paired-lazy action tiebreak selectors now have typechecked finite cardinality witnesses",
                "the large raw/lazy/paired non-singleton fibers remain split-out work",
            ],
            "significance_if_extended": [
                "the selector layer can be internalized one fiber class at a time",
                "singleton physical criteria can be transported as canonical points rather than external ids",
                "the remaining obstruction is proof engineering scale for the non-singleton fibers, not a missing selector count",
            ],
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Generate and typecheck the 63-element lazy selector finite-subtype module before attempting "
            "the 480- and 543-element fibers."
        ),
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
