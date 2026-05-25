from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
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
    "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_split"
)
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

RAW543_ACTUAL_C2_KERNEL_ORBITS_CSV = PACKAGE_HALLOWEEN_ORBITS_CSV
C2_CUBICAL_AGDA_SELECTOR_MEMBERSHIP_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_membership"
    / "report.json"
)
C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LAZY63_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lazy63"
    / "report.json"
)
C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_PAIRED_LAZY480_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_paired_lazy480"
    / "report.json"
)
C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_INDEXED_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_indexed"
    / "report.json"
)
C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_EMITTER_FACTORIZATION_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_emitter_factorization"
    / "report.json"
)


@dataclass(frozen=True)
class IndexedSelectorTheoremSpec:
    name: str
    selector_key: str
    selector_agda: str
    prefix: str
    membership_prefix: str
    fiber_count: int
    index_type_name: str
    module_name: str
    agda_source: Path
    direct_report: Path
    direct_status: str
    selector_summary_key: str

    @property
    def agda_interface(self) -> Path:
        return self.agda_source.with_suffix(".agdai")

    def emitter_spec(self) -> SelectorFiniteSubtypeSpec:
        return SelectorFiniteSubtypeSpec(
            module_name=self.module_name,
            selector_key=self.selector_key,
            selector_agda=self.selector_agda,
            prefix=self.prefix,
            membership_prefix=self.membership_prefix,
            fiber_count=self.fiber_count,
            index_type_name=self.index_type_name,
            use_from_nat_to_fin=True,
            use_nat_with_from=True,
            use_nat_with_right_inv=True,
        )


INDEXED_SELECTOR_SPECS = [
    IndexedSelectorTheoremSpec(
        name="lazy63",
        selector_key="lazy_componentwise_spectral_gap",
        selector_agda="lazyComponentwiseSpectralGap",
        prefix="lazySpectralGapIndexed",
        membership_prefix="lazyGapMember",
        fiber_count=63,
        index_type_name="LazySpectralGapIndexedSelectorIndex",
        module_name="C2SelectorFoundationSelectorFiniteSubtypeLazy63Indexed",
        agda_source=(
            D20_INVARIANTS
            / "formal"
            / "cubical"
            / "C2SelectorFoundationSelectorFiniteSubtypeLazy63Indexed.agda"
        ),
        direct_report=C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LAZY63_REPORT,
        direct_status=(
            "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LAZY63_CERTIFIED"
        ),
        selector_summary_key="lazy_selector",
    ),
    IndexedSelectorTheoremSpec(
        name="paired_lazy480",
        selector_key="paired_lazy_componentwise_spectral_gap",
        selector_agda="pairedLazyComponentwiseSpectralGap",
        prefix="pairedLazySpectralGapIndexed",
        membership_prefix="pairedLazyGapMember",
        fiber_count=480,
        index_type_name="PairedLazySpectralGapIndexedSelectorIndex",
        module_name="C2SelectorFoundationSelectorFiniteSubtypePairedLazy480Indexed",
        agda_source=(
            D20_INVARIANTS
            / "formal"
            / "cubical"
            / "C2SelectorFoundationSelectorFiniteSubtypePairedLazy480Indexed.agda"
        ),
        direct_report=C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_PAIRED_LAZY480_REPORT,
        direct_status=(
            "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_PAIRED_LAZY480_CERTIFIED"
        ),
        selector_summary_key="paired_lazy_selector",
    ),
]


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


def generate_agda_source(bridge: dict[str, Any], spec: IndexedSelectorTheoremSpec) -> str:
    return generate_selector_finite_subtype_agda(bridge, spec.emitter_spec())


def actual_selector_payload() -> dict[str, Any]:
    return selector_payload_from_actual_c2_kernel_orbits(
        RAW543_ACTUAL_C2_KERNEL_ORBITS_CSV
    )


def write_agda_sources() -> None:
    bridge = actual_selector_payload()
    for spec in INDEXED_SELECTOR_SPECS:
        source_text = generate_agda_source(bridge, spec)
        spec.agda_source.parent.mkdir(parents=True, exist_ok=True)
        if spec.agda_source.exists() and spec.agda_source.read_text(encoding="utf-8") == source_text:
            continue
        spec.agda_source.write_text(source_text, encoding="utf-8")


def count_regex(source_text: str, pattern: str) -> int:
    return len(re.findall(pattern, source_text, re.MULTILINE))


def build_selector_row(bridge: dict[str, Any], spec: IndexedSelectorTheoremSpec) -> dict[str, Any]:
    direct_report = load_json(spec.direct_report)
    source_text = spec.agda_source.read_text(encoding="utf-8")
    interface_exists = spec.agda_interface.exists()
    interface_size = spec.agda_interface.stat().st_size if interface_exists else 0
    interface_is_fresh = (
        interface_exists
        and interface_size > 0
        and spec.agda_interface.stat().st_mtime >= spec.agda_source.stat().st_mtime
    )
    fiber = selected_fiber(bridge, spec.selector_key, spec.fiber_count)
    selected_ids = [int(move_id) for move_id in fiber["selected_move_orbit_ids"]]
    dynamics_count = int(bridge["derived"]["bridge_summary"]["dynamics_count"])
    nonselected_count = dynamics_count - len(selected_ids)
    direct_source_size = int(
        direct_report.get("derived", {}).get("source_summary", {}).get("byte_size", 0)
    )
    prefix = spec.prefix
    member = spec.membership_prefix
    selector = spec.selector_agda
    fiber_count = spec.fiber_count
    source_summary = {
        "path": rel(spec.agda_source),
        "sha256": sha_file(spec.agda_source),
        "byte_size": spec.agda_source.stat().st_size,
        "line_count": len(source_text.splitlines()),
        "module": spec.module_name,
        "typecheck_command": (
            "C:/Users/Admin/Documents/agda-toolchain/agda.exe --warning=noUnsupportedIndexedMatch "
            "--transliterate -v0 -i data/invariants/d20/formal/cubical "
            "-i C:/Users/Admin/Documents/agda-toolchain/cubical-0.9 "
            f"{rel(spec.agda_source)}"
        ),
        "interface": {
            "path": rel(spec.agda_interface),
            "sha256": sha_file(spec.agda_interface) if interface_exists else None,
            "byte_size": interface_size,
            "fresh_for_source": interface_is_fresh,
        },
        "compactness": {
            "direct_source_byte_size": direct_source_size,
            "indexed_source_byte_size": spec.agda_source.stat().st_size,
            "byte_delta_against_direct": spec.agda_source.stat().st_size - direct_source_size,
            "fd_suc_occurrence_count": source_text.count("FD.suc"),
            "to_fin_data_from_nat_prime_clause_count": count_regex(
                source_text,
                rf"^{prefix}FiberToFinData \(d\d+ , {member}\d+\) = FDP.fromℕ' {fiber_count} ",
            ),
            "to_from_id_occurrence_count": source_text.count(f"FDP.toFromId' {fiber_count}"),
        },
        "proof_counts": {
            "selected_count": len(selected_ids),
            "nonselected_count": nonselected_count,
            "to_fin_data_selected_clause_count": count_regex(
                source_text,
                rf"^{prefix}FiberToFinData \(d\d+ , {member}\d+\) = FDP.fromℕ' {fiber_count} ",
            ),
            "to_fin_data_impossible_clause_count": count_regex(
                source_text,
                rf"^{prefix}FiberToFinData \(d\d+ , \(\)\)$",
            ),
            "from_fin_data_nat_with_clause_count": count_regex(
                source_text,
                rf"^\.\.\. \| .* \| _ = d\d+ , {member}\d+$",
            ),
            "right_inverse_nat_with_clause_count": count_regex(
                source_text,
                rf"^\.\.\. \| .* \| \[ eq \]ᵢ \| _ = FDP.inj-toℕ \{{k = FDP.fromℕ' {fiber_count} \d+ ",
            ),
            "nat_bound_absurd_clause_count": count_regex(
                source_text,
                r"^\.\.\. \| .* \| .*p = Empty.rec \(NatOrder.¬m\+n<m ",
            ),
            "left_inverse_selected_clause_count": count_regex(
                source_text,
                rf"^{prefix}FiberFinDataLeftInv \(d\d+ , {member}\d+\) = refl$",
            ),
            "left_inverse_impossible_clause_count": count_regex(
                source_text,
                rf"^{prefix}FiberFinDataLeftInv \(d\d+ , \(\)\)$",
            ),
            "fin_equivalence_count": count_regex(
                source_text,
                rf"^{prefix}FiberEquivFin : SelectorFiber {selector} ≃ Fin {fiber_count}$",
            ),
        },
    }
    counts = source_summary["proof_counts"]
    compactness = source_summary["compactness"]
    checks = {
        "direct_finite_subtype_theorem_is_certified": direct_report.get("status")
        == spec.direct_status
        and direct_report.get("all_checks_pass") is True,
        "indexed_source_defines_sigma_subtype": (
            "SelectorFiber s = Σ[ d ∈ DynamicsId ] SelectorMembership s d" in source_text
        ),
        "indexed_source_has_exact_fiber_witnesses": counts["selected_count"]
        == counts["to_fin_data_selected_clause_count"]
        == counts["from_fin_data_nat_with_clause_count"]
        == counts["right_inverse_nat_with_clause_count"]
        == counts["left_inverse_selected_clause_count"]
        == fiber_count,
        "indexed_source_has_expected_impossible_rows": counts[
            "to_fin_data_impossible_clause_count"
        ]
        == counts["left_inverse_impossible_clause_count"]
        == nonselected_count,
        "indexed_source_has_two_nat_bound_absurd_rows": counts[
            "nat_bound_absurd_clause_count"
        ]
        == 2,
        "indexed_source_has_fin_equivalence": counts["fin_equivalence_count"] == 1
        and f"{prefix}FiberEquivFin = compEquiv {prefix}FiberFinDataEquiv (FinData≃Fin {fiber_count})"
        in source_text,
        "indexed_source_has_no_fd_suc_constructor_normal_forms": compactness[
            "fd_suc_occurrence_count"
        ]
        == 0,
        "indexed_source_uses_from_nat_and_to_from_id_for_all_witnesses": compactness[
            "to_fin_data_from_nat_prime_clause_count"
        ]
        == compactness["to_from_id_occurrence_count"]
        == fiber_count,
        "indexed_agda_interface_artifact_present_after_typecheck": interface_is_fresh,
        "indexed_artifact_hashes_are_stable": (
            len(sha_file(spec.agda_source)) == 64
            and interface_exists
            and len(sha_file(spec.agda_interface)) == 64
        ),
    }
    return {
        "name": spec.name,
        "selector": {
            "selector": fiber["selector"],
            "selected_count": fiber["selected_count"],
            "selected_move_orbit_ids": fiber["selected_move_orbit_ids"],
            "unselected_count": nonselected_count,
        },
        "source_summary": source_summary,
        "direct_report": {
            "path": rel(spec.direct_report),
            "sha256": sha_file(spec.direct_report),
            "status": direct_report.get("status"),
            "all_checks_pass": direct_report.get("all_checks_pass"),
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def build_theorem() -> dict[str, Any]:
    source_package = load_json(PACKAGE_CERTIFICATE)
    source_registry = source_registry_binding()
    selector_payload = actual_selector_payload()
    membership = load_json(C2_CUBICAL_AGDA_SELECTOR_MEMBERSHIP_REPORT)
    raw543_indexed = load_json(C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_INDEXED_REPORT)
    emitter_factorization = load_json(
        C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_EMITTER_FACTORIZATION_REPORT
    )
    actual_source = selector_payload["derived"]["actual_c2_kernel_orbit_source"]
    rows = [build_selector_row(selector_payload, spec) for spec in INDEXED_SELECTOR_SPECS]
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
        "raw543_indexed_finite_subtype_theorem_is_certified": raw543_indexed.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_INDEXED_CERTIFIED"
        and raw543_indexed.get("all_checks_pass") is True,
        "shared_emitter_factorization_is_certified": emitter_factorization.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_EMITTER_FACTORIZATION_CERTIFIED"
        and emitter_factorization.get("all_checks_pass") is True,
        "all_indexed_split_rows_certified": all(row["all_checks_pass"] for row in rows),
        "actual_c2_kernel_orbits_drive_indexed_split_rows": actual_source[
            "raw543_orbit_count"
        ]
        == 543
        and actual_source["fixed63_orbit_count"] == 63
        and actual_source["paired480_two_cycle_orbit_count"] == 480
        and [row["selector"]["selected_count"] for row in rows] == [63, 480],
        "all_indexed_split_sources_have_no_fd_suc_constructor_normal_forms": all(
            row["source_summary"]["compactness"]["fd_suc_occurrence_count"] == 0
            for row in rows
        ),
        "indexed_split_covers_lazy63_and_paired_lazy480": [row["name"] for row in rows]
        == ["lazy63", "paired_lazy480"],
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_SPLIT_CERTIFIED"
        if all_checks_pass
        else "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_SPLIT_NEEDS_REVIEW"
    )
    report = {
        "schema": "d20.theorem.full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_split",
        "status": status,
        "object": "d20",
        "claim": (
            "The lazy63 and paired-lazy480 selector fibers have compact indexed Cubical Agda "
            "equivalences to their certified Fin cardinalities with no generated FD.suc constructor normal forms."
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
            "c2_cubical_agda_selector_finite_subtype_raw543_indexed_report": {
                "path": rel(C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_INDEXED_REPORT),
                "sha256": sha_file(C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_INDEXED_REPORT),
            },
            "c2_cubical_agda_selector_finite_subtype_emitter_factorization_report": {
                "path": rel(C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_EMITTER_FACTORIZATION_REPORT),
                "sha256": sha_file(
                    C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_EMITTER_FACTORIZATION_REPORT
                ),
            },
            "indexed_selector_sources": [
                {
                    "name": row["name"],
                    "path": row["source_summary"]["path"],
                    "sha256": row["source_summary"]["sha256"],
                }
                for row in rows
            ],
        },
        "derived": {
            "actual_c2_kernel_orbit_source": actual_source,
            "indexed_selector_rows": rows,
            "indexed_selector_count": len(rows),
        },
        "interpretation": {
            "what_this_proves": [
                "lazy63 is packaged as an indexed Sigma subtype equivalent to Fin 63",
                "paired-lazy480 is packaged as an indexed Sigma subtype equivalent to Fin 480",
                "both indexed modules avoid explicit FD.suc constructor-normal-form towers",
            ],
            "what_remains": [
                "switch downstream proof-obligation references to the indexed finite-subtype spine",
                "consider a second-stage vector lookup layer if Agda source size, not only constructor-normal-form shape, must be minimized",
            ],
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Switch the cycle-8 proof-obligation spine to the indexed finite-subtype trio and "
            "then factor the indexed proof rows into a second-stage vector lookup layer."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    write_agda_sources()
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
