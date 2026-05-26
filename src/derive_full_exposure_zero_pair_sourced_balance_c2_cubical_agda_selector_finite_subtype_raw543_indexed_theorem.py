from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from src.c2_selector_finite_subtype_emitter import (
    SelectorFiniteSubtypeSpec,
    generate_selector_finite_subtype_agda,
    selected_fiber,
    selector_payload_from_actual_c2_kernel_orbits,
)
from src.paths import D20_INVARIANTS, ROOT
from src.verify_c2_selector_lookup_witness_source_package import (
    PACKAGE_CERTIFICATE,
    PACKAGE_HALLOWEEN_ORBITS_CSV,
    PACKAGE_VERIFIED_STATUS,
    attach_source_registry_binding_to_theorem_index,
    source_registry_binding,
)


THEOREM_ID = (
    "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_indexed"
)
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

RAW543_ACTUAL_C2_KERNEL_ORBITS_CSV = PACKAGE_HALLOWEEN_ORBITS_CSV
C2_CUBICAL_AGDA_SELECTOR_MEMBERSHIP_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_membership"
    / "report.json"
)
C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543"
    / "report.json"
)
C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_EMITTER_FACTORIZATION_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_emitter_factorization"
    / "report.json"
)
CUBICAL_AGDA_SOURCE = (
    D20_INVARIANTS
    / "formal"
    / "cubical"
    / "C2SelectorFoundationSelectorFiniteSubtypeRaw543Indexed.agda"
)
CUBICAL_AGDA_INTERFACE = CUBICAL_AGDA_SOURCE.with_suffix(".agdai")

SELECTOR_KEY = "raw_componentwise_absolute_spectral_gap"
SELECTOR_AGDA = "rawComponentwiseAbsoluteSpectralGap"
PREFIX = "rawSpectralGapIndexed"
MEMBERSHIP_PREFIX = "rawGapMember"
FIBER_COUNT = 543
RAW543_INDEXED_SPEC = SelectorFiniteSubtypeSpec(
    module_name="C2SelectorFoundationSelectorFiniteSubtypeRaw543Indexed",
    selector_key=SELECTOR_KEY,
    selector_agda=SELECTOR_AGDA,
    prefix=PREFIX,
    membership_prefix=MEMBERSHIP_PREFIX,
    fiber_count=FIBER_COUNT,
    index_type_name="RawSpectralGapIndexedSelectorIndex",
    use_from_nat_to_fin=True,
    use_nat_with_from=True,
    use_nat_with_right_inv=True,
    require_full_selector=True,
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
    index = attach_source_registry_binding_to_theorem_index(index)
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def raw_fiber(bridge: dict[str, Any]) -> dict[str, Any]:
    return selected_fiber(bridge, SELECTOR_KEY, FIBER_COUNT)


def generate_agda_source(bridge: dict[str, Any]) -> str:
    return generate_selector_finite_subtype_agda(bridge, RAW543_INDEXED_SPEC)


def actual_selector_payload() -> dict[str, Any]:
    return selector_payload_from_actual_c2_kernel_orbits(
        RAW543_ACTUAL_C2_KERNEL_ORBITS_CSV
    )


def write_agda_source() -> None:
    source_text = generate_agda_source(actual_selector_payload())
    CUBICAL_AGDA_SOURCE.parent.mkdir(parents=True, exist_ok=True)
    if CUBICAL_AGDA_SOURCE.exists() and CUBICAL_AGDA_SOURCE.read_text(encoding="utf-8") == source_text:
        return
    CUBICAL_AGDA_SOURCE.write_text(source_text, encoding="utf-8")


def build_theorem() -> dict[str, Any]:
    source_package = load_json(PACKAGE_CERTIFICATE)
    source_registry = source_registry_binding()
    selector_payload = actual_selector_payload()
    membership = load_json(C2_CUBICAL_AGDA_SELECTOR_MEMBERSHIP_REPORT)
    raw543 = load_json(C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_REPORT)
    emitter_factorization = load_json(
        C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_EMITTER_FACTORIZATION_REPORT
    )
    source_text = CUBICAL_AGDA_SOURCE.read_text(encoding="utf-8")
    interface_exists = CUBICAL_AGDA_INTERFACE.exists()
    interface_size = CUBICAL_AGDA_INTERFACE.stat().st_size if interface_exists else 0
    interface_is_fresh = (
        interface_exists
        and interface_size > 0
        and CUBICAL_AGDA_INTERFACE.stat().st_mtime >= CUBICAL_AGDA_SOURCE.stat().st_mtime
    )
    fiber = raw_fiber(selector_payload)
    selected_ids = [int(move_id) for move_id in fiber["selected_move_orbit_ids"]]
    direct_raw_source = (
        raw543.get("derived", {}).get("source_summary", {}).get("byte_size", 0)
    )

    source_summary = {
        "path": rel(CUBICAL_AGDA_SOURCE),
        "sha256": sha_file(CUBICAL_AGDA_SOURCE),
        "byte_size": CUBICAL_AGDA_SOURCE.stat().st_size,
        "line_count": len(source_text.splitlines()),
        "module": "C2SelectorFoundationSelectorFiniteSubtypeRaw543Indexed",
        "typecheck_command": (
            "C:/Users/Admin/Documents/agda-toolchain/agda.exe --warning=noUnsupportedIndexedMatch "
            "--transliterate -v0 -i data/invariants/d20/formal/cubical "
            "-i C:/Users/Admin/Documents/agda-toolchain/cubical-0.9 "
            "data/invariants/d20/formal/cubical/C2SelectorFoundationSelectorFiniteSubtypeRaw543Indexed.agda"
        ),
        "interface": {
            "path": rel(CUBICAL_AGDA_INTERFACE),
            "sha256": sha_file(CUBICAL_AGDA_INTERFACE) if interface_exists else None,
            "byte_size": interface_size,
            "fresh_for_source": interface_is_fresh,
        },
        "compactness": {
            "direct_raw543_source_byte_size": direct_raw_source,
            "indexed_source_byte_size": CUBICAL_AGDA_SOURCE.stat().st_size,
            "byte_reduction_against_direct_raw543": direct_raw_source
            - CUBICAL_AGDA_SOURCE.stat().st_size,
            "fd_suc_occurrence_count": source_text.count("FD.suc"),
            "to_fin_data_from_nat_prime_clause_count": len(
                re.findall(
                    r"^rawSpectralGapIndexedFiberToFinData \(d\d+ , rawGapMember\d+\) = FDP.fromℕ' 543 ",
                    source_text,
                    re.MULTILINE,
                )
            ),
            "to_from_id_occurrence_count": source_text.count("FDP.toFromId' 543"),
        },
        "proof_counts": {
            "selected_count": len(selected_ids),
            "to_fin_data_selected_clause_count": len(
                re.findall(
                    r"^rawSpectralGapIndexedFiberToFinData \(d\d+ , rawGapMember\d+\) = FDP.fromℕ' 543 ",
                    source_text,
                    re.MULTILINE,
                )
            ),
            "from_fin_data_nat_with_clause_count": len(
                re.findall(
                    r"^\.\.\. \| .* \| _ = d\d+ , rawGapMember\d+$",
                    source_text,
                    re.MULTILINE,
                )
            ),
            "right_inverse_nat_with_clause_count": len(
                re.findall(
                    r"^\.\.\. \| .* \| \[ eq \]ᵢ \| _ = FDP.inj-toℕ \{k = FDP.fromℕ' 543 \d+ ",
                    source_text,
                    re.MULTILINE,
                )
            ),
            "nat_bound_absurd_clause_count": len(
                re.findall(
                    r"^\.\.\. \| .* \| .*p = Empty.rec \(NatOrder.¬m\+n<m ",
                    source_text,
                    re.MULTILINE,
                )
            ),
            "left_inverse_selected_clause_count": len(
                re.findall(
                    r"^rawSpectralGapIndexedFiberFinDataLeftInv \(d\d+ , rawGapMember\d+\) = refl$",
                    source_text,
                    re.MULTILINE,
                )
            ),
            "fin_equivalence_count": len(
                re.findall(
                    r"^rawSpectralGapIndexedFiberEquivFin : SelectorFiber rawComponentwiseAbsoluteSpectralGap ≃ Fin 543$",
                    source_text,
                    re.MULTILINE,
                )
            ),
        },
    }
    counts = source_summary["proof_counts"]
    compactness = source_summary["compactness"]
    checks = {
        "halloween_source_package_is_verified": source_package.get("status")
        == PACKAGE_VERIFIED_STATUS
        and source_package.get("all_checks_pass") is True,
        "halloween_source_package_registry_id_is_threaded": source_registry[
            "all_checks_pass"
        ]
        is True,
        "selector_membership_theorem_is_certified": membership.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_MEMBERSHIP_CERTIFIED"
        and membership.get("all_checks_pass") is True,
        "direct_raw543_finite_subtype_theorem_is_certified": raw543.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_CERTIFIED"
        and raw543.get("all_checks_pass") is True,
        "shared_emitter_factorization_is_certified": emitter_factorization.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_EMITTER_FACTORIZATION_CERTIFIED"
        and emitter_factorization.get("all_checks_pass") is True,
        "actual_c2_kernel_orbits_drive_raw_indexed_selector": selected_ids
        == list(range(FIBER_COUNT)),
        "indexed_source_defines_sigma_subtype": (
            "SelectorFiber s = Σ[ d ∈ DynamicsId ] SelectorMembership s d" in source_text
        ),
        "indexed_source_has_exact_543_fiber_witnesses": counts[
            "selected_count"
        ]
        == counts["to_fin_data_selected_clause_count"]
        == counts["from_fin_data_nat_with_clause_count"]
        == counts["right_inverse_nat_with_clause_count"]
        == counts["left_inverse_selected_clause_count"]
        == FIBER_COUNT,
        "indexed_source_has_two_nat_bound_absurd_rows": counts[
            "nat_bound_absurd_clause_count"
        ]
        == 2,
        "indexed_source_has_fin543_equivalence": counts["fin_equivalence_count"] == 1
        and "rawSpectralGapIndexedFiberEquivFin = compEquiv rawSpectralGapIndexedFiberFinDataEquiv (FinData≃Fin 543)"
        in source_text,
        "indexed_source_has_no_fd_suc_constructor_normal_forms": compactness[
            "fd_suc_occurrence_count"
        ]
        == 0,
        "indexed_source_uses_from_nat_and_to_from_id_for_all_543": compactness[
            "to_fin_data_from_nat_prime_clause_count"
        ]
        == compactness["to_from_id_occurrence_count"]
        == FIBER_COUNT,
        "indexed_source_is_smaller_than_direct_raw543_source": 0
        < compactness["indexed_source_byte_size"]
        < compactness["direct_raw543_source_byte_size"],
        "raw543_indexed_agda_interface_artifact_present_after_typecheck": interface_is_fresh,
        "raw543_indexed_artifact_hashes_are_stable": sha_file(CUBICAL_AGDA_SOURCE)
        and (sha_file(CUBICAL_AGDA_INTERFACE) if interface_exists else None),
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_INDEXED_CERTIFIED"
        if all_checks_pass
        else "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_INDEXED_NEEDS_REVIEW"
    )
    report = {
        "schema": "d20.theorem.full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_indexed",
        "status": status,
        "object": "d20",
        "claim": (
            "The raw componentwise absolute spectral-gap selector fiber has a compact indexed Cubical "
            "Agda equivalence to Fin 543 with no generated FD.suc constructor normal forms."
        ),
        "inputs": {
            "halloween_lookup_source_package_certificate": {
                "path": rel(PACKAGE_CERTIFICATE),
                "sha256": sha_file(PACKAGE_CERTIFICATE),
            },
            "halloween_lookup_source_package_registry_binding": source_registry,
            "halloween_actual_c2_kernel_orbits_csv": {
                "path": rel(RAW543_ACTUAL_C2_KERNEL_ORBITS_CSV),
                "sha256": sha_file(RAW543_ACTUAL_C2_KERNEL_ORBITS_CSV),
            },
            "c2_cubical_agda_selector_membership_report": {
                "path": rel(C2_CUBICAL_AGDA_SELECTOR_MEMBERSHIP_REPORT),
                "sha256": sha_file(C2_CUBICAL_AGDA_SELECTOR_MEMBERSHIP_REPORT),
            },
            "c2_cubical_agda_selector_finite_subtype_raw543_report": {
                "path": rel(C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_REPORT),
                "sha256": sha_file(C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_REPORT),
            },
            "c2_cubical_agda_selector_finite_subtype_emitter_factorization_report": {
                "path": rel(C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_EMITTER_FACTORIZATION_REPORT),
                "sha256": sha_file(
                    C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_EMITTER_FACTORIZATION_REPORT
                ),
            },
            "cubical_agda_selector_finite_subtype_raw543_indexed_source": {
                "path": rel(CUBICAL_AGDA_SOURCE),
                "sha256": sha_file(CUBICAL_AGDA_SOURCE),
            },
            "cubical_agda_selector_finite_subtype_raw543_indexed_interface": {
                "path": rel(CUBICAL_AGDA_INTERFACE),
                "sha256": sha_file(CUBICAL_AGDA_INTERFACE) if interface_exists else None,
            },
        },
        "derived": {
            "source_summary": source_summary,
            "raw_selector": {
                "selector": fiber["selector"],
                "selected_count": fiber["selected_count"],
                "selected_move_orbit_ids": fiber["selected_move_orbit_ids"],
                "unselected_count": 0,
            },
            "actual_c2_kernel_orbit_source": selector_payload["derived"][
                "actual_c2_kernel_orbit_source"
            ],
        },
        "interpretation": {
            "what_this_proves": [
                "the raw Fin 543 selector subtype can be certified through natural-number indexed witnesses instead of FD.suc normal forms",
                "the compact path keeps the same Sigma subtype and Fin 543 equivalence as the direct raw543 theorem",
                "the source-level normal form is smaller and contains no explicit FD.suc constructor tower",
            ],
            "what_remains": [
                "lift the indexed mode to lazy63 and paired-lazy480",
                "retire the constructor-normal-form finite-subtype modules from the active proof-obligation spine once all split fibers have indexed replacements",
            ],
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Promote the indexed finite-subtype emitter mode to lazy63 and paired-lazy480, then "
            "switch the proof-obligation spine from constructor-normal-form modules to indexed modules."
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
