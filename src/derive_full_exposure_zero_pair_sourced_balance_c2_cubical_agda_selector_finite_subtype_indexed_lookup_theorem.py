from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.c2_selector_finite_subtype_emitter import (
    SelectorFiniteSubtypeSpec,
    generate_selector_finite_subtype_agda,
    selected_fiber,
    selector_payload_from_actual_c2_kernel_orbits,
    selector_payload_with_lookup_witness_table,
)
from src.paths import D20_INVARIANTS, ROOT
from src.verify_c2_selector_lookup_witness_source_package import (
    PACKAGE_VERIFIED_STATUS,
    attach_source_registry_binding_to_theorem_index,
    source_registry_binding,
)


THEOREM_ID = (
    "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_lookup"
)
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

RAW543_ACTUAL_C2_KERNEL_ORBITS_CSV = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table"
    / "source_package"
    / "halloween_actual_c2_kernel_orbits_raw543.csv"
)
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
C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_SPLIT_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_split"
    / "report.json"
)
C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LOOKUP_TABLE_JSON = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table"
    / "source_package"
    / "selector_lookup_witness_table.json"
)
C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LOOKUP_SOURCE_PACKAGE_CERTIFICATE = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table"
    / "source_package"
    / "source_package_certificate.json"
)
C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_EMITTER_FACTORIZATION_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_emitter_factorization"
    / "report.json"
)


@dataclass(frozen=True)
class LookupSelectorTheoremSpec:
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
    previous_indexed_report: Path
    previous_indexed_status: str
    previous_indexed_row_name: str | None = None
    require_full_selector: bool = False

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
            use_nat_lookup_right_inv=True,
            require_full_selector=self.require_full_selector,
        )


LOOKUP_SELECTOR_SPECS = [
    LookupSelectorTheoremSpec(
        name="raw543",
        selector_key="raw_componentwise_absolute_spectral_gap",
        selector_agda="rawComponentwiseAbsoluteSpectralGap",
        prefix="rawSpectralGapLookup",
        membership_prefix="rawGapMember",
        fiber_count=543,
        index_type_name="RawSpectralGapLookupSelectorIndex",
        module_name="C2SelectorFoundationSelectorFiniteSubtypeRaw543IndexedLookup",
        agda_source=(
            D20_INVARIANTS
            / "formal"
            / "cubical"
            / "C2SelectorFoundationSelectorFiniteSubtypeRaw543IndexedLookup.agda"
        ),
        direct_report=C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_REPORT,
        direct_status=(
            "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_CERTIFIED"
        ),
        previous_indexed_report=C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_INDEXED_REPORT,
        previous_indexed_status=(
            "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_INDEXED_CERTIFIED"
        ),
        require_full_selector=True,
    ),
    LookupSelectorTheoremSpec(
        name="lazy63",
        selector_key="lazy_componentwise_spectral_gap",
        selector_agda="lazyComponentwiseSpectralGap",
        prefix="lazySpectralGapLookup",
        membership_prefix="lazyGapMember",
        fiber_count=63,
        index_type_name="LazySpectralGapLookupSelectorIndex",
        module_name="C2SelectorFoundationSelectorFiniteSubtypeLazy63IndexedLookup",
        agda_source=(
            D20_INVARIANTS
            / "formal"
            / "cubical"
            / "C2SelectorFoundationSelectorFiniteSubtypeLazy63IndexedLookup.agda"
        ),
        direct_report=C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LAZY63_REPORT,
        direct_status=(
            "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LAZY63_CERTIFIED"
        ),
        previous_indexed_report=C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_SPLIT_REPORT,
        previous_indexed_status=(
            "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_SPLIT_CERTIFIED"
        ),
        previous_indexed_row_name="lazy63",
    ),
    LookupSelectorTheoremSpec(
        name="paired_lazy480",
        selector_key="paired_lazy_componentwise_spectral_gap",
        selector_agda="pairedLazyComponentwiseSpectralGap",
        prefix="pairedLazySpectralGapLookup",
        membership_prefix="pairedLazyGapMember",
        fiber_count=480,
        index_type_name="PairedLazySpectralGapLookupSelectorIndex",
        module_name="C2SelectorFoundationSelectorFiniteSubtypePairedLazy480IndexedLookup",
        agda_source=(
            D20_INVARIANTS
            / "formal"
            / "cubical"
            / "C2SelectorFoundationSelectorFiniteSubtypePairedLazy480IndexedLookup.agda"
        ),
        direct_report=C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_PAIRED_LAZY480_REPORT,
        direct_status=(
            "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_PAIRED_LAZY480_CERTIFIED"
        ),
        previous_indexed_report=C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_SPLIT_REPORT,
        previous_indexed_status=(
            "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_SPLIT_CERTIFIED"
        ),
        previous_indexed_row_name="paired_lazy480",
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


def actual_selector_payload() -> dict[str, Any]:
    return selector_payload_from_actual_c2_kernel_orbits(
        RAW543_ACTUAL_C2_KERNEL_ORBITS_CSV
    )


def lookup_table_selector_payload() -> dict[str, Any]:
    return selector_payload_with_lookup_witness_table(
        actual_selector_payload(),
        C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LOOKUP_TABLE_JSON,
    )


def write_agda_sources() -> None:
    bridge = lookup_table_selector_payload()
    for spec in LOOKUP_SELECTOR_SPECS:
        source_text = generate_selector_finite_subtype_agda(bridge, spec.emitter_spec())
        spec.agda_source.parent.mkdir(parents=True, exist_ok=True)
        if spec.agda_source.exists() and spec.agda_source.read_text(encoding="utf-8") == source_text:
            continue
        spec.agda_source.write_text(source_text, encoding="utf-8")


def previous_indexed_source_size(spec: LookupSelectorTheoremSpec) -> int:
    report = load_json(spec.previous_indexed_report)
    if spec.previous_indexed_row_name is None:
        return int(report.get("derived", {}).get("source_summary", {}).get("byte_size", 0))
    for row in report.get("derived", {}).get("indexed_selector_rows", []):
        if row.get("name") == spec.previous_indexed_row_name:
            return int(row.get("source_summary", {}).get("byte_size", 0))
    raise ValueError(f"missing previous indexed row {spec.previous_indexed_row_name}")


def line_count(lines: list[str], *, prefix: str, contains: str | None = None) -> int:
    return sum(
        1
        for line in lines
        if line.startswith(prefix) and (contains is None or contains in line)
    )


def build_selector_row(bridge: dict[str, Any], spec: LookupSelectorTheoremSpec) -> dict[str, Any]:
    direct_report = load_json(spec.direct_report)
    previous_indexed_report = load_json(spec.previous_indexed_report)
    source_text = spec.agda_source.read_text(encoding="utf-8")
    source_lines = source_text.splitlines()
    interface_exists = spec.agda_interface.exists()
    interface_size = spec.agda_interface.stat().st_size if interface_exists else 0
    interface_is_fresh = (
        interface_exists
        and interface_size > 0
        and spec.agda_interface.stat().st_mtime >= spec.agda_source.stat().st_mtime
    )
    fiber = selected_fiber(bridge, spec.selector_key, spec.fiber_count)
    selected_ids = [int(move_id) for move_id in fiber["selected_move_orbit_ids"]]
    table_rows = bridge["derived"].get("selector_lookup_witness_rows", {}).get(
        spec.selector_key, []
    )
    dynamics_count = int(bridge["derived"]["bridge_summary"]["dynamics_count"])
    nonselected_count = dynamics_count - len(selected_ids)
    direct_source_size = int(
        direct_report.get("derived", {}).get("source_summary", {}).get("byte_size", 0)
    )
    previous_indexed_size = previous_indexed_source_size(spec)
    prefix = spec.prefix
    member = spec.membership_prefix
    selected_to_fin_prefix = f"{prefix}FiberToFinData (d"
    left_inv_prefix = f"{prefix}FiberFinDataLeftInv (d"
    source_summary = {
        "path": rel(spec.agda_source),
        "sha256": sha_file(spec.agda_source),
        "byte_size": spec.agda_source.stat().st_size,
        "line_count": len(source_lines),
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
            "previous_indexed_source_byte_size": previous_indexed_size,
            "lookup_source_byte_size": spec.agda_source.stat().st_size,
            "byte_delta_against_direct": spec.agda_source.stat().st_size - direct_source_size,
            "byte_delta_against_previous_indexed": spec.agda_source.stat().st_size
            - previous_indexed_size,
            "fd_suc_occurrence_count": source_text.count("FD.suc"),
            "inspect_occurrence_count": source_text.count("inspect FD.toℕ"),
            "inj_to_nat_occurrence_count": source_text.count("FDP.inj-toℕ"),
            "to_from_id_occurrence_count": source_text.count("FDP.toFromId'"),
            "from_to_id_occurrence_count": source_text.count("FDP.fromToId'"),
        },
        "lookup_witness_table": {
            "row_count": len(table_rows),
            "dynamics_ids_match_selector": [
                int(row["dynamics_id"]) for row in table_rows
            ]
            == selected_ids,
            "to_fin_data_clauses_in_source": all(
                str(row["to_fin_data_clause"]) in source_text for row in table_rows
            ),
            "from_nat_clauses_in_source": all(
                str(row["from_nat_clause"]) in source_text for row in table_rows
            ),
            "from_nat_to_fin_data_clauses_in_source": all(
                str(row["from_nat_to_fin_data_clause"]) in source_text for row in table_rows
            ),
            "left_inverse_clauses_in_source": all(
                str(row["left_inverse_clause"]) in source_text for row in table_rows
            ),
        },
        "proof_counts": {
            "selected_count": len(selected_ids),
            "nonselected_count": nonselected_count,
            "to_fin_data_selected_clause_count": sum(
                1
                for line in source_lines
                if line.startswith(selected_to_fin_prefix)
                and f", {member}" in line
                and "FDP.fromℕ'" in line
            ),
            "to_fin_data_impossible_clause_count": line_count(
                source_lines, prefix=selected_to_fin_prefix, contains=", ())"
            ),
            "from_nat_selected_clause_count": sum(
                1
                for line in source_lines
                if line.startswith(f"{prefix}FiberFromNat ") and " = d" in line
            ),
            "from_nat_absurd_clause_count": line_count(
                source_lines,
                prefix=f"{prefix}FiberFromNat ",
                contains="Empty.rec (NatOrder.¬m+n<m",
            ),
            "from_nat_to_fin_data_selected_clause_count": sum(
                1
                for line in source_lines
                if line.startswith(f"{prefix}FiberFromNatToFinData ")
                and line.endswith(" = refl")
            ),
            "from_nat_to_fin_data_absurd_clause_count": line_count(
                source_lines,
                prefix=f"{prefix}FiberFromNatToFinData ",
                contains="Empty.rec (NatOrder.¬m+n<m",
            ),
            "from_fin_data_lookup_definition_count": source_lines.count(
                f"{prefix}FiberFromFinData i = {prefix}FiberFromNat (FD.toℕ i) (FDP.toℕ<n i)"
            ),
            "right_inverse_from_to_id_definition_count": source_text.count(
                f"FDP.fromToId' {spec.fiber_count} i (FDP.toℕ<n i)"
            ),
            "left_inverse_selected_clause_count": sum(
                1
                for line in source_lines
                if line.startswith(left_inv_prefix)
                and f", {member}" in line
                and line.endswith(" = refl")
            ),
            "left_inverse_impossible_clause_count": line_count(
                source_lines, prefix=left_inv_prefix, contains=", ())"
            ),
            "fin_equivalence_count": source_text.count(
                f"{prefix}FiberEquivFin : SelectorFiber {spec.selector_agda} ≃ Fin {spec.fiber_count}"
            ),
        },
    }
    counts = source_summary["proof_counts"]
    compactness = source_summary["compactness"]
    checks = {
        "direct_finite_subtype_theorem_is_certified": direct_report.get("status")
        == spec.direct_status
        and direct_report.get("all_checks_pass") is True,
        "previous_indexed_theorem_is_certified": previous_indexed_report.get("status")
        == spec.previous_indexed_status
        and previous_indexed_report.get("all_checks_pass") is True,
        "lookup_source_defines_sigma_subtype": (
            "SelectorFiber s = Σ[ d ∈ DynamicsId ] SelectorMembership s d" in source_text
        ),
        "lookup_source_selected_witnesses_are_table_driven": source_summary[
            "lookup_witness_table"
        ]["row_count"]
        == spec.fiber_count
        and source_summary["lookup_witness_table"]["dynamics_ids_match_selector"] is True
        and source_summary["lookup_witness_table"]["to_fin_data_clauses_in_source"] is True
        and source_summary["lookup_witness_table"]["from_nat_clauses_in_source"] is True
        and source_summary["lookup_witness_table"][
            "from_nat_to_fin_data_clauses_in_source"
        ]
        is True
        and source_summary["lookup_witness_table"]["left_inverse_clauses_in_source"] is True,
        "lookup_source_has_exact_fiber_witnesses": counts["selected_count"]
        == counts["to_fin_data_selected_clause_count"]
        == counts["from_nat_selected_clause_count"]
        == counts["from_nat_to_fin_data_selected_clause_count"]
        == counts["left_inverse_selected_clause_count"]
        == spec.fiber_count,
        "lookup_source_has_expected_impossible_rows": counts[
            "to_fin_data_impossible_clause_count"
        ]
        == counts["left_inverse_impossible_clause_count"]
        == nonselected_count,
        "lookup_source_has_one_from_nat_absurd_row_per_helper": counts[
            "from_nat_absurd_clause_count"
        ]
        == counts["from_nat_to_fin_data_absurd_clause_count"]
        == 1,
        "from_fin_data_is_single_lookup_definition": counts[
            "from_fin_data_lookup_definition_count"
        ]
        == 1
        and f"{prefix}FiberFromFinData i with" not in source_text,
        "right_inverse_is_single_from_to_id_definition": counts[
            "right_inverse_from_to_id_definition_count"
        ]
        == 1,
        "lookup_right_inverse_removes_inspect_and_injection_tower": compactness[
            "inspect_occurrence_count"
        ]
        == compactness["inj_to_nat_occurrence_count"]
        == compactness["to_from_id_occurrence_count"]
        == 0
        and compactness["from_to_id_occurrence_count"] == 1,
        "lookup_source_has_fin_equivalence": counts["fin_equivalence_count"] == 1
        and f"{prefix}FiberEquivFin = compEquiv {prefix}FiberFinDataEquiv (FinData≃Fin {spec.fiber_count})"
        in source_text,
        "lookup_source_has_no_fd_suc_constructor_normal_forms": compactness[
            "fd_suc_occurrence_count"
        ]
        == 0,
        "lookup_source_is_smaller_than_previous_indexed_source": compactness[
            "byte_delta_against_previous_indexed"
        ]
        < 0,
        "lookup_agda_interface_artifact_present_after_typecheck": interface_is_fresh,
        "lookup_artifact_hashes_are_stable": (
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
        "previous_indexed_report": {
            "path": rel(spec.previous_indexed_report),
            "sha256": sha_file(spec.previous_indexed_report),
            "status": previous_indexed_report.get("status"),
            "all_checks_pass": previous_indexed_report.get("all_checks_pass"),
            "row_name": spec.previous_indexed_row_name,
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def build_theorem() -> dict[str, Any]:
    selector_payload = lookup_table_selector_payload()
    source_package_certificate = load_json(
        C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LOOKUP_SOURCE_PACKAGE_CERTIFICATE
    )
    source_registry = source_registry_binding()
    membership = load_json(C2_CUBICAL_AGDA_SELECTOR_MEMBERSHIP_REPORT)
    raw543_indexed = load_json(C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_INDEXED_REPORT)
    indexed_split = load_json(C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_SPLIT_REPORT)
    emitter_factorization = load_json(
        C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_EMITTER_FACTORIZATION_REPORT
    )
    actual_source = selector_payload["derived"]["actual_c2_kernel_orbit_source"]
    lookup_table_source = selector_payload["derived"]["lookup_witness_table_source"]
    rows = [build_selector_row(selector_payload, spec) for spec in LOOKUP_SELECTOR_SPECS]
    checks = {
        "lookup_source_package_is_standalone_verified": source_package_certificate.get(
            "status"
        )
        == PACKAGE_VERIFIED_STATUS
        and source_package_certificate.get("all_checks_pass") is True,
        "lookup_source_package_registry_id_is_threaded": source_registry[
            "all_checks_pass"
        ]
        is True,
        "selector_membership_theorem_is_certified": membership.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_MEMBERSHIP_CERTIFIED"
        and membership.get("all_checks_pass") is True,
        "raw543_indexed_finite_subtype_theorem_is_certified": raw543_indexed.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_INDEXED_CERTIFIED"
        and raw543_indexed.get("all_checks_pass") is True,
        "indexed_split_finite_subtype_theorem_is_certified": indexed_split.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_SPLIT_CERTIFIED"
        and indexed_split.get("all_checks_pass") is True,
        "shared_emitter_factorization_is_certified": emitter_factorization.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_EMITTER_FACTORIZATION_CERTIFIED"
        and emitter_factorization.get("all_checks_pass") is True,
        "all_lookup_rows_certified": all(row["all_checks_pass"] for row in rows),
        "lookup_covers_raw543_lazy63_and_paired_lazy480": [row["name"] for row in rows]
        == ["raw543", "lazy63", "paired_lazy480"],
        "actual_c2_kernel_orbits_drive_indexed_lookup_rows": actual_source[
            "raw543_orbit_count"
        ]
        == 543
        and actual_source["fixed63_orbit_count"] == 63
        and actual_source["paired480_two_cycle_orbit_count"] == 480
        and [row["selector"]["selected_count"] for row in rows] == [543, 63, 480],
        "lookup_witness_table_drives_indexed_lookup_rows": lookup_table_source[
            "row_count"
        ]
        == 1086
        and lookup_table_source["row_count_by_selector"]
        == {
            "lazy_componentwise_spectral_gap": 63,
            "paired_lazy_componentwise_spectral_gap": 480,
            "raw_componentwise_absolute_spectral_gap": 543,
        },
        "lookup_witness_table_source_is_halloween_package": lookup_table_source[
            "path"
        ]
        == str(C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LOOKUP_TABLE_JSON)
        and actual_source["path"] == str(RAW543_ACTUAL_C2_KERNEL_ORBITS_CSV),
        "all_lookup_sources_have_no_fd_suc_constructor_normal_forms": all(
            row["source_summary"]["compactness"]["fd_suc_occurrence_count"] == 0
            for row in rows
        ),
        "all_lookup_sources_are_smaller_than_previous_indexed_sources": all(
            row["source_summary"]["compactness"]["byte_delta_against_previous_indexed"] < 0
            for row in rows
        ),
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_LOOKUP_CERTIFIED"
        if all_checks_pass
        else "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_LOOKUP_NEEDS_REVIEW"
    )
    report = {
        "schema": "d20.theorem.full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_lookup",
        "status": status,
        "object": "d20",
        "claim": (
            "The raw543, lazy63, and paired-lazy480 selector fibers have lookup-collapsed "
            "indexed Cubical Agda equivalences to Fin 543, Fin 63, and Fin 480. "
            "The right inverse is discharged by a shared Nat-index helper and FinData fromToId' "
            "instead of generated inspect/injection proof rows, with selected witnesses emitted "
            "from the standalone Halloween source package."
        ),
        "inputs": {
            "halloween_lookup_source_package_orbits_csv": {
                "path": rel(RAW543_ACTUAL_C2_KERNEL_ORBITS_CSV),
                "sha256": sha_file(RAW543_ACTUAL_C2_KERNEL_ORBITS_CSV),
            },
            "selector_lookup_witness_table_json": {
                "path": rel(C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LOOKUP_TABLE_JSON),
                "sha256": sha_file(C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LOOKUP_TABLE_JSON),
            },
            "selector_lookup_witness_source_package_certificate": {
                "path": rel(
                    C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LOOKUP_SOURCE_PACKAGE_CERTIFICATE
                ),
                "sha256": sha_file(
                    C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LOOKUP_SOURCE_PACKAGE_CERTIFICATE
                ),
            },
            "halloween_lookup_source_package_registry_binding": source_registry,
            "c2_cubical_agda_selector_membership_report": {
                "path": rel(C2_CUBICAL_AGDA_SELECTOR_MEMBERSHIP_REPORT),
                "sha256": sha_file(C2_CUBICAL_AGDA_SELECTOR_MEMBERSHIP_REPORT),
            },
            "c2_cubical_agda_selector_finite_subtype_raw543_indexed_report": {
                "path": rel(C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_INDEXED_REPORT),
                "sha256": sha_file(C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_INDEXED_REPORT),
            },
            "c2_cubical_agda_selector_finite_subtype_indexed_split_report": {
                "path": rel(C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_SPLIT_REPORT),
                "sha256": sha_file(C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_SPLIT_REPORT),
            },
            "c2_cubical_agda_selector_finite_subtype_emitter_factorization_report": {
                "path": rel(C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_EMITTER_FACTORIZATION_REPORT),
                "sha256": sha_file(
                    C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_EMITTER_FACTORIZATION_REPORT
                ),
            },
            "lookup_selector_sources": [
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
            "lookup_witness_table_source": lookup_table_source,
            "lookup_selector_rows": rows,
            "lookup_selector_count": len(rows),
        },
        "interpretation": {
            "what_this_proves": [
                "raw543 is packaged as a lookup-collapsed indexed Sigma subtype equivalent to Fin 543",
                "lazy63 is packaged as a lookup-collapsed indexed Sigma subtype equivalent to Fin 63",
                "paired-lazy480 is packaged as a lookup-collapsed indexed Sigma subtype equivalent to Fin 480",
                "selected witness clauses are emitted from the verified lookup-table artifact",
                "the lookup emitter path consumes the standalone Halloween package as its selected-witness source",
                "all three modules avoid explicit FD.suc constructor-normal-form towers and inspect/injection right-inverse rows",
            ],
            "what_remains": [
                "stage the Halloween source-registry, theorem-registry, and Agda replay artifacts for review",
            ],
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Stage the Halloween source-registry, theorem-registry, and Agda replay artifacts for review."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {k: v for k, v in report.items() if k != "certificate_sha256"}
    )
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
    manifest["manifest_sha256"] = sha_json(
        {k: v for k, v in manifest.items() if k != "manifest_sha256"}
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    update_theorem_index(report, out_dir)
    return report


def main() -> None:
    report = write_theorem()
    print(report["status"])
    print(report["certificate_sha256"])


if __name__ == "__main__":
    main()
