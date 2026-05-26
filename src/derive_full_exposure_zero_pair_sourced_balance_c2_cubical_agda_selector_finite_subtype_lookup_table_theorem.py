from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.c2_selector_finite_subtype_emitter import (
    membership_constructor,
    nat_exact_pattern,
    selected_fiber,
    selector_payload_from_actual_c2_kernel_orbits,
)
from src.paths import D20_INVARIANTS, ROOT
from src.verify_c2_selector_lookup_witness_source_package import (
    PACKAGE_LOCKED_STATUS,
    PACKAGE_REGISTRY_ID,
    PACKAGE_SCHEMA,
    PACKAGE_VERIFIED_STATUS,
    attach_source_registry_binding_to_theorem_index,
    source_registry_binding,
    verify_source_package,
)


THEOREM_ID = (
    "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table"
)
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

TABLE_JSON = DEFAULT_OUT_DIR / "selector_lookup_witness_table.json"
TABLE_CSV = DEFAULT_OUT_DIR / "selector_lookup_witness_table.csv"
SOURCE_PACKAGE_DIR = DEFAULT_OUT_DIR / "source_package"
SOURCE_PACKAGE_TABLE_JSON = SOURCE_PACKAGE_DIR / "selector_lookup_witness_table.json"
SOURCE_PACKAGE_TABLE_CSV = SOURCE_PACKAGE_DIR / "selector_lookup_witness_table.csv"
SOURCE_PACKAGE_HALLOWEEN_ORBITS_CSV = (
    SOURCE_PACKAGE_DIR / "halloween_actual_c2_kernel_orbits_raw543.csv"
)
SOURCE_PACKAGE_MANIFEST = SOURCE_PACKAGE_DIR / "manifest.json"
SOURCE_PACKAGE_CERTIFICATE = SOURCE_PACKAGE_DIR / "source_package_certificate.json"
SOUNDNESS_SOURCE = (
    D20_INVARIANTS
    / "formal"
    / "cubical"
    / "C2SelectorFoundationSelectorFiniteSubtypeLookupTableSoundness.agda"
)

RAW543_ACTUAL_C2_KERNEL_ORBITS_CSV = (
    D20_INVARIANTS
    / "theorems"
    / "raw543_repo_c2_kernel_action"
    / "actual_c2_kernel_orbits_raw543.csv"
)
C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_LOOKUP_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_lookup"
    / "report.json"
)


@dataclass(frozen=True)
class LookupTableSelectorSpec:
    name: str
    selector_key: str
    selector_agda: str
    prefix: str
    membership_prefix: str
    fiber_count: int
    module_name: str
    agda_source: Path

    @property
    def equiv_name(self) -> str:
        return f"{self.prefix}FiberEquivFin"


LOOKUP_TABLE_SELECTOR_SPECS = [
    LookupTableSelectorSpec(
        name="raw543",
        selector_key="raw_componentwise_absolute_spectral_gap",
        selector_agda="rawComponentwiseAbsoluteSpectralGap",
        prefix="rawSpectralGapLookup",
        membership_prefix="rawGapMember",
        fiber_count=543,
        module_name="C2SelectorFoundationSelectorFiniteSubtypeRaw543IndexedLookup",
        agda_source=(
            D20_INVARIANTS
            / "formal"
            / "cubical"
            / "C2SelectorFoundationSelectorFiniteSubtypeRaw543IndexedLookup.agda"
        ),
    ),
    LookupTableSelectorSpec(
        name="lazy63",
        selector_key="lazy_componentwise_spectral_gap",
        selector_agda="lazyComponentwiseSpectralGap",
        prefix="lazySpectralGapLookup",
        membership_prefix="lazyGapMember",
        fiber_count=63,
        module_name="C2SelectorFoundationSelectorFiniteSubtypeLazy63IndexedLookup",
        agda_source=(
            D20_INVARIANTS
            / "formal"
            / "cubical"
            / "C2SelectorFoundationSelectorFiniteSubtypeLazy63IndexedLookup.agda"
        ),
    ),
    LookupTableSelectorSpec(
        name="paired_lazy480",
        selector_key="paired_lazy_componentwise_spectral_gap",
        selector_agda="pairedLazyComponentwiseSpectralGap",
        prefix="pairedLazySpectralGapLookup",
        membership_prefix="pairedLazyGapMember",
        fiber_count=480,
        module_name="C2SelectorFoundationSelectorFiniteSubtypePairedLazy480IndexedLookup",
        agda_source=(
            D20_INVARIANTS
            / "formal"
            / "cubical"
            / "C2SelectorFoundationSelectorFiniteSubtypePairedLazy480IndexedLookup.agda"
        ),
    ),
]

CSV_FIELDNAMES = [
    "row_id",
    "selector_index",
    "selector_name",
    "selector_key",
    "selector_agda",
    "fiber_count",
    "fiber_index",
    "dynamics_id",
    "dynamics_constructor",
    "membership_constructor",
    "index_bound_witness",
    "lookup_module",
    "lookup_prefix",
    "equivalence_name",
    "to_fin_data_clause",
    "from_nat_clause",
    "from_nat_to_fin_data_clause",
    "left_inverse_clause",
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


def build_table_rows(selector_payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    row_id = 0
    for selector_index, spec in enumerate(LOOKUP_TABLE_SELECTOR_SPECS):
        fiber = selected_fiber(selector_payload, spec.selector_key, spec.fiber_count)
        selected_ids = [int(move_id) for move_id in fiber["selected_move_orbit_ids"]]
        for fiber_index, dynamics_id in enumerate(selected_ids):
            member = membership_constructor(spec.membership_prefix, dynamics_id)
            index_bound = spec.fiber_count - fiber_index - 1
            rows.append(
                {
                    "row_id": row_id,
                    "selector_index": selector_index,
                    "selector_name": spec.name,
                    "selector_key": spec.selector_key,
                    "selector_agda": spec.selector_agda,
                    "fiber_count": spec.fiber_count,
                    "fiber_index": fiber_index,
                    "dynamics_id": dynamics_id,
                    "dynamics_constructor": f"d{dynamics_id}",
                    "membership_constructor": member,
                    "index_bound_witness": index_bound,
                    "lookup_module": spec.module_name,
                    "lookup_prefix": spec.prefix,
                    "equivalence_name": spec.equiv_name,
                    "to_fin_data_clause": (
                        f"{spec.prefix}FiberToFinData (d{dynamics_id} , {member}) = "
                        f"FDP.fromℕ' {spec.fiber_count} {fiber_index} "
                        f"({index_bound} , refl)"
                    ),
                    "from_nat_clause": (
                        f"{spec.prefix}FiberFromNat {nat_exact_pattern(fiber_index)} _ = "
                        f"d{dynamics_id} , {member}"
                    ),
                    "from_nat_to_fin_data_clause": (
                        f"{spec.prefix}FiberFromNatToFinData {nat_exact_pattern(fiber_index)} "
                        "_ = refl"
                    ),
                    "left_inverse_clause": (
                        f"{spec.prefix}FiberFinDataLeftInv (d{dynamics_id} , {member}) = refl"
                    ),
                }
            )
            row_id += 1
    return rows


def build_table_artifact(rows: list[dict[str, Any]]) -> dict[str, Any]:
    selector_summaries = []
    for spec in LOOKUP_TABLE_SELECTOR_SPECS:
        selector_rows = [row for row in rows if row["selector_name"] == spec.name]
        selector_summaries.append(
            {
                "selector_name": spec.name,
                "selector_key": spec.selector_key,
                "selector_agda": spec.selector_agda,
                "fiber_count": spec.fiber_count,
                "row_count": len(selector_rows),
                "first_row_id": selector_rows[0]["row_id"] if selector_rows else None,
                "last_row_id": selector_rows[-1]["row_id"] if selector_rows else None,
                "selected_move_orbit_ids_sha256": sha_json(
                    [row["dynamics_id"] for row in selector_rows]
                ),
                "lookup_module": spec.module_name,
                "equivalence_name": spec.equiv_name,
            }
        )
    table = {
        "schema": "d20.selector_finite_subtype.lookup_witness_table.v1",
        "theorem_id": THEOREM_ID,
        "row_count": len(rows),
        "selector_count": len(LOOKUP_TABLE_SELECTOR_SPECS),
        "selectors": selector_summaries,
        "rows": rows,
    }
    table["table_sha256"] = sha_json({k: v for k, v in table.items() if k != "table_sha256"})
    return table


def write_table_artifacts(rows: list[dict[str, Any]]) -> dict[str, Any]:
    DEFAULT_OUT_DIR.mkdir(parents=True, exist_ok=True)
    table = build_table_artifact(rows)
    TABLE_JSON.write_text(json.dumps(table, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with TABLE_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    return table


def selector_count_by_name(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        counts[str(row["selector_name"])] = counts.get(str(row["selector_name"]), 0) + 1
    return dict(sorted(counts.items()))


def write_source_package(table: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    SOURCE_PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
    SOURCE_PACKAGE_TABLE_JSON.write_text(
        json.dumps(table, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    with SOURCE_PACKAGE_TABLE_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    SOURCE_PACKAGE_HALLOWEEN_ORBITS_CSV.write_bytes(
        RAW543_ACTUAL_C2_KERNEL_ORBITS_CSV.read_bytes()
    )

    counts = selector_count_by_name(rows)
    package_files = [
        SOURCE_PACKAGE_MANIFEST,
        SOURCE_PACKAGE_TABLE_JSON,
        SOURCE_PACKAGE_TABLE_CSV,
        SOURCE_PACKAGE_HALLOWEEN_ORBITS_CSV,
    ]
    manifest = {
        "schema": PACKAGE_SCHEMA,
        "status": PACKAGE_LOCKED_STATUS,
        "theorem_id": THEOREM_ID,
        "package_name": PACKAGE_REGISTRY_ID,
        "source_registry_id": PACKAGE_REGISTRY_ID,
        "source": {
            "halloween_actual_c2_kernel_orbits_csv": {
                "path": rel(SOURCE_PACKAGE_HALLOWEEN_ORBITS_CSV),
                "sha256": sha_file(SOURCE_PACKAGE_HALLOWEEN_ORBITS_CSV),
                "row_count": 543,
            },
        },
        "artifacts": {
            "selector_lookup_witness_table_json": {
                "path": rel(SOURCE_PACKAGE_TABLE_JSON),
                "sha256": sha_file(SOURCE_PACKAGE_TABLE_JSON),
                "embedded_table_sha256": table["table_sha256"],
            },
            "selector_lookup_witness_table_csv": {
                "path": rel(SOURCE_PACKAGE_TABLE_CSV),
                "sha256": sha_file(SOURCE_PACKAGE_TABLE_CSV),
                "fieldnames": CSV_FIELDNAMES,
            },
        },
        "lock_contract": {
            "row_count": len(rows),
            "selector_counts": counts,
            "selector_order": [spec.name for spec in LOOKUP_TABLE_SELECTOR_SPECS],
            "csv_fieldnames": CSV_FIELDNAMES,
            "table_sha256": table["table_sha256"],
            "actual_c2_kernel_split": {
                "raw543_orbit_count": 543,
                "fixed63_orbit_count": 63,
                "paired480_two_cycle_orbit_count": 480,
            },
            "standalone_source_dependency": True,
        },
        "package_files": [rel(path) for path in package_files],
    }
    manifest["manifest_sha256"] = sha_json(
        {k: v for k, v in manifest.items() if k != "manifest_sha256"}
    )
    SOURCE_PACKAGE_MANIFEST.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return verify_source_package(SOURCE_PACKAGE_DIR, SOURCE_PACKAGE_CERTIFICATE)


def agda_soundness_source() -> str:
    return """{-# OPTIONS --cubical --safe --guardedness #-}

module C2SelectorFoundationSelectorFiniteSubtypeLookupTableSoundness where

open import Cubical.Foundations.Prelude using (_≡_ ; refl)
open import Cubical.Foundations.Equiv using (_≃_)
open import Cubical.Data.Nat using (ℕ ; _+_)
open import Cubical.Data.Fin.Base using (Fin)
open import C2SelectorFoundation
import C2SelectorFoundationSelectorFiniteSubtypeRaw543IndexedLookup as RawLookup
import C2SelectorFoundationSelectorFiniteSubtypeLazy63IndexedLookup as LazyLookup
import C2SelectorFoundationSelectorFiniteSubtypePairedLazy480IndexedLookup as PairedLookup

raw543LookupTableRowCount : ℕ
raw543LookupTableRowCount = 543

lazy63LookupTableRowCount : ℕ
lazy63LookupTableRowCount = 63

pairedLazy480LookupTableRowCount : ℕ
pairedLazy480LookupTableRowCount = 480

lookupTableSelectorCount : ℕ
lookupTableSelectorCount = 3

lookupTableTotalRowCount : ℕ
lookupTableTotalRowCount =
  raw543LookupTableRowCount + lazy63LookupTableRowCount + pairedLazy480LookupTableRowCount

lookupTableTotalRowCountIs1086 : lookupTableTotalRowCount ≡ 1086
lookupTableTotalRowCountIs1086 = refl

raw543LookupTableSoundness :
  RawLookup.SelectorFiber rawComponentwiseAbsoluteSpectralGap ≃ Fin raw543LookupTableRowCount
raw543LookupTableSoundness = RawLookup.rawSpectralGapLookupFiberEquivFin

lazy63LookupTableSoundness :
  LazyLookup.SelectorFiber lazyComponentwiseSpectralGap ≃ Fin lazy63LookupTableRowCount
lazy63LookupTableSoundness = LazyLookup.lazySpectralGapLookupFiberEquivFin

pairedLazy480LookupTableSoundness :
  PairedLookup.SelectorFiber pairedLazyComponentwiseSpectralGap ≃
  Fin pairedLazy480LookupTableRowCount
pairedLazy480LookupTableSoundness = PairedLookup.pairedLazySpectralGapLookupFiberEquivFin
"""


def write_agda_soundness_source() -> None:
    source_text = agda_soundness_source()
    SOUNDNESS_SOURCE.parent.mkdir(parents=True, exist_ok=True)
    if SOUNDNESS_SOURCE.exists() and SOUNDNESS_SOURCE.read_text(encoding="utf-8") == source_text:
        return
    SOUNDNESS_SOURCE.write_text(source_text, encoding="utf-8")


def selector_summary_from_rows(
    selector_payload: dict[str, Any], rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    summary = []
    for spec in LOOKUP_TABLE_SELECTOR_SPECS:
        fiber = selected_fiber(selector_payload, spec.selector_key, spec.fiber_count)
        selected_ids = [int(move_id) for move_id in fiber["selected_move_orbit_ids"]]
        selector_rows = [row for row in rows if row["selector_name"] == spec.name]
        source_text = spec.agda_source.read_text(encoding="utf-8")
        exact_clause_checks = {
            "to_fin_data_clauses_in_source": all(
                row["to_fin_data_clause"] in source_text for row in selector_rows
            ),
            "from_nat_clauses_in_source": all(
                row["from_nat_clause"] in source_text for row in selector_rows
            ),
            "from_nat_to_fin_data_clauses_in_source": all(
                row["from_nat_to_fin_data_clause"] in source_text for row in selector_rows
            ),
            "left_inverse_clauses_in_source": all(
                row["left_inverse_clause"] in source_text for row in selector_rows
            ),
        }
        indices = [int(row["fiber_index"]) for row in selector_rows]
        row_ids = [int(row["row_id"]) for row in selector_rows]
        dynamics_ids = [int(row["dynamics_id"]) for row in selector_rows]
        summary.append(
            {
                "selector_name": spec.name,
                "selector_key": spec.selector_key,
                "selector_agda": spec.selector_agda,
                "fiber_count": spec.fiber_count,
                "table_row_count": len(selector_rows),
                "row_id_span": [min(row_ids), max(row_ids)] if row_ids else [],
                "indices_are_contiguous": indices == list(range(spec.fiber_count)),
                "selected_ids_match_actual_c2_kernel_order": dynamics_ids == selected_ids,
                "membership_constructors_match_dynamics_ids": all(
                    row["membership_constructor"]
                    == membership_constructor(spec.membership_prefix, int(row["dynamics_id"]))
                    for row in selector_rows
                ),
                "index_bound_witnesses_are_exact": all(
                    int(row["index_bound_witness"])
                    == spec.fiber_count - int(row["fiber_index"]) - 1
                    for row in selector_rows
                ),
                "lookup_source": {
                    "path": rel(spec.agda_source),
                    "sha256": sha_file(spec.agda_source),
                    "byte_size": spec.agda_source.stat().st_size,
                    "module": spec.module_name,
                    "equivalence_name": spec.equiv_name,
                },
                "exact_clause_checks": exact_clause_checks,
                "all_exact_clauses_in_source": all(exact_clause_checks.values()),
            }
        )
    return summary


def soundness_source_summary() -> dict[str, Any]:
    interface = SOUNDNESS_SOURCE.with_suffix(".agdai")
    source_text = SOUNDNESS_SOURCE.read_text(encoding="utf-8") if SOUNDNESS_SOURCE.exists() else ""
    interface_exists = interface.exists()
    interface_size = interface.stat().st_size if interface_exists else 0
    interface_is_fresh = (
        interface_exists
        and interface_size > 0
        and interface.stat().st_mtime >= SOUNDNESS_SOURCE.stat().st_mtime
    )
    return {
        "path": rel(SOUNDNESS_SOURCE),
        "sha256": sha_file(SOUNDNESS_SOURCE) if SOUNDNESS_SOURCE.exists() else None,
        "byte_size": SOUNDNESS_SOURCE.stat().st_size if SOUNDNESS_SOURCE.exists() else 0,
        "line_count": len(source_text.splitlines()),
        "typecheck_command": (
            "C:/Users/Admin/Documents/agda-toolchain/agda.exe --warning=noUnsupportedIndexedMatch "
            "--transliterate -v0 -i data/invariants/d20/formal/cubical "
            "-i C:/Users/Admin/Documents/agda-toolchain/cubical-0.9 "
            f"{rel(SOUNDNESS_SOURCE)}"
        ),
        "interface": {
            "path": rel(interface),
            "sha256": sha_file(interface) if interface_exists else None,
            "byte_size": interface_size,
            "fresh_for_source": interface_is_fresh,
        },
        "proof_counts": {
            "lookup_table_soundness_equivalence_count": source_text.count(
                "LookupTableSoundness"
            ),
            "selector_count_definition_count": source_text.count(
                "lookupTableSelectorCount"
            ),
            "total_row_count_1086_proof_count": source_text.count(
                "lookupTableTotalRowCountIs1086"
            ),
        },
        "imports": {
            "raw_lookup_module": (
                "import C2SelectorFoundationSelectorFiniteSubtypeRaw543IndexedLookup as RawLookup"
                in source_text
            ),
            "lazy_lookup_module": (
                "import C2SelectorFoundationSelectorFiniteSubtypeLazy63IndexedLookup as LazyLookup"
                in source_text
            ),
            "paired_lookup_module": (
                "import C2SelectorFoundationSelectorFiniteSubtypePairedLazy480IndexedLookup as PairedLookup"
                in source_text
            ),
        },
        "equivalence_exports": {
            "raw543": "raw543LookupTableSoundness = RawLookup.rawSpectralGapLookupFiberEquivFin"
            in source_text,
            "lazy63": "lazy63LookupTableSoundness = LazyLookup.lazySpectralGapLookupFiberEquivFin"
            in source_text,
            "paired_lazy480": (
                "pairedLazy480LookupTableSoundness = "
                "PairedLookup.pairedLazySpectralGapLookupFiberEquivFin"
            )
            in source_text,
        },
    }


def table_artifact_summary(table: dict[str, Any]) -> dict[str, Any]:
    return {
        "json": {
            "path": rel(TABLE_JSON),
            "sha256": sha_file(TABLE_JSON),
            "byte_size": TABLE_JSON.stat().st_size,
            "embedded_table_sha256": table["table_sha256"],
            "embedded_table_sha256_matches_payload": table["table_sha256"]
            == sha_json({k: v for k, v in table.items() if k != "table_sha256"}),
        },
        "csv": {
            "path": rel(TABLE_CSV),
            "sha256": sha_file(TABLE_CSV),
            "byte_size": TABLE_CSV.stat().st_size,
            "fieldnames": CSV_FIELDNAMES,
        },
    }


def source_package_summary() -> dict[str, Any]:
    manifest = load_json(SOURCE_PACKAGE_MANIFEST)
    certificate = load_json(SOURCE_PACKAGE_CERTIFICATE)
    registry_binding = source_registry_binding(
        SOURCE_PACKAGE_DIR, SOURCE_PACKAGE_CERTIFICATE
    )
    return {
        "package_dir": rel(SOURCE_PACKAGE_DIR),
        "source_registry_binding": registry_binding,
        "manifest": {
            "path": rel(SOURCE_PACKAGE_MANIFEST),
            "sha256": sha_file(SOURCE_PACKAGE_MANIFEST),
            "embedded_manifest_sha256": manifest.get("manifest_sha256"),
            "schema": manifest.get("schema"),
            "status": manifest.get("status"),
            "source_registry_id": manifest.get("source_registry_id"),
            "lock_contract": manifest.get("lock_contract", {}),
        },
        "certificate": {
            "path": rel(SOURCE_PACKAGE_CERTIFICATE),
            "sha256": sha_file(SOURCE_PACKAGE_CERTIFICATE),
            "status": certificate.get("status"),
            "certificate_sha256": certificate.get("certificate_sha256"),
            "all_checks_pass": certificate.get("all_checks_pass"),
            "checks": certificate.get("checks", {}),
        },
        "table_json": {
            "path": rel(SOURCE_PACKAGE_TABLE_JSON),
            "sha256": sha_file(SOURCE_PACKAGE_TABLE_JSON),
        },
        "table_csv": {
            "path": rel(SOURCE_PACKAGE_TABLE_CSV),
            "sha256": sha_file(SOURCE_PACKAGE_TABLE_CSV),
        },
        "halloween_actual_c2_kernel_orbits_csv": {
            "path": rel(SOURCE_PACKAGE_HALLOWEEN_ORBITS_CSV),
            "sha256": sha_file(SOURCE_PACKAGE_HALLOWEEN_ORBITS_CSV),
        },
    }


def build_theorem() -> dict[str, Any]:
    selector_payload = actual_selector_payload()
    actual_source = selector_payload["derived"]["actual_c2_kernel_orbit_source"]
    indexed_lookup = load_json(C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_LOOKUP_REPORT)
    table = load_json(TABLE_JSON)
    rows = table["rows"]
    selector_summaries = selector_summary_from_rows(selector_payload, rows)
    soundness = soundness_source_summary()
    artifacts = table_artifact_summary(table)
    source_package = source_package_summary()

    row_ids = [int(row["row_id"]) for row in rows]
    csv_row_count = 0
    with TABLE_CSV.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        csv_fieldnames = list(reader.fieldnames or [])
        csv_row_count = sum(1 for _ in reader)

    checks = {
        "indexed_lookup_theorem_is_certified": indexed_lookup.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_LOOKUP_CERTIFIED"
        and indexed_lookup.get("all_checks_pass") is True,
        "indexed_lookup_emitter_consumes_lookup_table": indexed_lookup.get(
            "checks", {}
        ).get("lookup_witness_table_drives_indexed_lookup_rows")
        is True
        and all(
            row.get("checks", {}).get("lookup_source_selected_witnesses_are_table_driven")
            is True
            for row in indexed_lookup.get("derived", {}).get("lookup_selector_rows", [])
        ),
        "indexed_lookup_emitter_consumes_source_package": indexed_lookup.get(
            "derived", {}
        )
        .get("lookup_witness_table_source", {})
        .get("path")
        == str(SOURCE_PACKAGE_TABLE_JSON),
        "lookup_table_json_has_1086_rows": table.get("row_count") == len(rows) == 1086,
        "lookup_table_csv_has_1086_rows": csv_row_count == 1086
        and csv_fieldnames == CSV_FIELDNAMES,
        "lookup_table_has_three_selectors": table.get("selector_count") == 3
        and [summary["selector_name"] for summary in selector_summaries]
        == ["raw543", "lazy63", "paired_lazy480"],
        "lookup_table_row_ids_are_contiguous": row_ids == list(range(1086)),
        "lookup_table_counts_match_actual_c2_kernel_fibers": all(
            summary["table_row_count"] == summary["fiber_count"] for summary in selector_summaries
        ),
        "lookup_table_indices_are_contiguous": all(
            summary["indices_are_contiguous"] for summary in selector_summaries
        ),
        "lookup_table_selected_ids_match_actual_c2_kernel_order": all(
            summary["selected_ids_match_actual_c2_kernel_order"]
            for summary in selector_summaries
        ),
        "actual_c2_kernel_orbits_drive_lookup_table": actual_source[
            "raw543_orbit_count"
        ]
        == 543
        and actual_source["fixed63_orbit_count"] == 63
        and actual_source["paired480_two_cycle_orbit_count"] == 480
        and {
            summary["selector_name"]: summary["table_row_count"]
            for summary in selector_summaries
        }
        == {"raw543": 543, "lazy63": 63, "paired_lazy480": 480},
        "lookup_table_membership_constructors_are_exact": all(
            summary["membership_constructors_match_dynamics_ids"]
            and summary["index_bound_witnesses_are_exact"]
            for summary in selector_summaries
        ),
        "lookup_table_rows_match_lookup_agda_sources": all(
            summary["all_exact_clauses_in_source"] for summary in selector_summaries
        ),
        "lookup_table_artifact_hashes_are_stable": (
            artifacts["json"]["embedded_table_sha256_matches_payload"]
            and len(artifacts["json"]["sha256"]) == 64
            and len(artifacts["csv"]["sha256"]) == 64
        ),
        "lookup_source_package_standalone_verifier_passes": source_package[
            "certificate"
        ]["status"]
        == PACKAGE_VERIFIED_STATUS
        and source_package["certificate"]["all_checks_pass"] is True,
        "lookup_source_package_registry_id_is_threaded": source_package[
            "source_registry_binding"
        ]["all_checks_pass"]
        is True,
        "lookup_source_package_has_immutable_hash_contract": (
            source_package["manifest"]["schema"] == PACKAGE_SCHEMA
            and source_package["manifest"]["status"] == PACKAGE_LOCKED_STATUS
            and source_package["manifest"]["source_registry_id"] == PACKAGE_REGISTRY_ID
            and source_package["manifest"]["lock_contract"].get("row_count") == 1086
            and source_package["manifest"]["lock_contract"].get("selector_counts")
            == {"lazy63": 63, "paired_lazy480": 480, "raw543": 543}
            and source_package["manifest"]["lock_contract"].get("table_sha256")
            == table["table_sha256"]
        ),
        "lookup_source_package_uses_only_halloween_source_and_lookup_artifacts": source_package[
            "certificate"
        ]["checks"].get("package_uses_only_halloween_source_and_lookup_artifacts")
        is True,
        "lookup_table_soundness_source_imports_lookup_modules": all(
            soundness["imports"].values()
        ),
        "lookup_table_soundness_exports_three_fin_equivalences": all(
            soundness["equivalence_exports"].values()
        )
        and soundness["proof_counts"]["total_row_count_1086_proof_count"] >= 2,
        "lookup_table_soundness_agda_interface_artifact_present_after_typecheck": soundness[
            "interface"
        ]["fresh_for_source"],
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LOOKUP_TABLE_CERTIFIED"
        if all_checks_pass
        else "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LOOKUP_TABLE_NEEDS_REVIEW"
    )
    report = {
        "schema": "d20.theorem.full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table",
        "status": status,
        "object": "d20",
        "claim": (
            "The raw543, lazy63, and paired-lazy480 lookup-collapsed selector witnesses are "
            "externalized as a 1086-row JSON/CSV table, and a Cubical Agda soundness module "
            "ties the table row counts back to the certified Fin 543, Fin 63, and Fin 480 "
            "lookup equivalences."
        ),
        "inputs": {
            "raw543_actual_c2_kernel_orbits_csv": {
                "path": rel(RAW543_ACTUAL_C2_KERNEL_ORBITS_CSV),
                "sha256": sha_file(RAW543_ACTUAL_C2_KERNEL_ORBITS_CSV),
            },
            "c2_cubical_agda_selector_finite_subtype_indexed_lookup_report": {
                "path": rel(C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_LOOKUP_REPORT),
                "sha256": sha_file(C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_LOOKUP_REPORT),
            },
            "lookup_selector_sources": [
                {
                    "selector_name": spec.name,
                    "path": rel(spec.agda_source),
                    "sha256": sha_file(spec.agda_source),
                }
                for spec in LOOKUP_TABLE_SELECTOR_SPECS
            ],
        },
        "outputs": {
            "lookup_witness_table_json": artifacts["json"],
            "lookup_witness_table_csv": artifacts["csv"],
            "lookup_witness_source_package": source_package,
            "lookup_table_soundness_agda": soundness,
        },
        "derived": {
            "actual_c2_kernel_orbit_source": actual_source,
            "lookup_table_selector_summaries": selector_summaries,
            "lookup_table_row_count": len(rows),
            "lookup_table_selector_count": len(selector_summaries),
            "lookup_table_row_count_by_selector": {
                summary["selector_name"]: summary["table_row_count"]
                for summary in selector_summaries
            },
            "lookup_table_artifact_summary": artifacts,
            "lookup_witness_source_package": source_package,
            "lookup_table_soundness_summary": soundness,
        },
        "interpretation": {
            "what_this_proves": [
                "the selected witness rows for the three non-singleton spectral selectors are materialized as an audited table",
                "the table rows are exact source clauses in the lookup-collapsed Agda modules",
                "the table row counts are tied to certified Cubical equivalences to Fin 543, Fin 63, and Fin 480",
                "the Halloween lookup rows are locked as a standalone source package with its own verifier",
            ],
            "explicit_seam": (
                "The indexed lookup emitter consumes the standalone Halloween source package for "
                "selected witness clauses; the package is the only selected-witness source input."
            ),
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
    selector_payload = actual_selector_payload()
    rows = build_table_rows(selector_payload)
    table = write_table_artifacts(rows)
    write_source_package(table, rows)
    write_agda_soundness_source()
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem_manifest",
        "theorem_id": THEOREM_ID,
        "status": report["status"],
        "report": rel(out_dir / "report.json"),
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "checks": report["checks"],
        "report_sha256": report["certificate_sha256"],
        "table_sha256": table["table_sha256"],
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
