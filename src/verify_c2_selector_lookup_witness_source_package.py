from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = (
    "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table"
)
PACKAGE_SCHEMA = "d20.selector_finite_subtype.lookup_witness_source_package.v1"
PACKAGE_LOCKED_STATUS = "D20_C2_SELECTOR_LOOKUP_WITNESS_SOURCE_PACKAGE_LOCKED"
PACKAGE_VERIFIED_STATUS = "D20_C2_SELECTOR_LOOKUP_WITNESS_SOURCE_PACKAGE_VERIFIED"
PACKAGE_REGISTRY_ID = "halloween_c2_selector_lookup_witness_source_package"
SOURCE_REGISTRY_STATUS = "D20_SOURCE_REGISTRY_BUILT"
SOURCE_PACKAGE_REGISTERED_STATUS = "D20_SOURCE_PACKAGE_REGISTERED"
DEFAULT_PACKAGE_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID / "source_package"
HALLOWEEN_SOURCE_PACKAGE_THEOREM_IDS = {
    "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lazy63",
    "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_paired_lazy480",
    "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543",
    "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_indexed",
    "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_split",
    "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_lookup",
    "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table",
}

PACKAGE_MANIFEST = DEFAULT_PACKAGE_DIR / "manifest.json"
PACKAGE_TABLE_JSON = DEFAULT_PACKAGE_DIR / "selector_lookup_witness_table.json"
PACKAGE_TABLE_CSV = DEFAULT_PACKAGE_DIR / "selector_lookup_witness_table.csv"
PACKAGE_HALLOWEEN_ORBITS_CSV = (
    DEFAULT_PACKAGE_DIR / "halloween_actual_c2_kernel_orbits_raw543.csv"
)
PACKAGE_CERTIFICATE = DEFAULT_PACKAGE_DIR / "source_package_certificate.json"
THEOREM_REGISTRY_INDEX = D20_INVARIANTS / "theorems" / "index.json"

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

INT_FIELDS = {
    "row_id",
    "selector_index",
    "fiber_count",
    "fiber_index",
    "dynamics_id",
    "index_bound_witness",
}

SELECTOR_CONTRACTS = [
    {
        "selector_name": "raw543",
        "selector_key": "raw_componentwise_absolute_spectral_gap",
        "selector_agda": "rawComponentwiseAbsoluteSpectralGap",
        "selector_index": 0,
        "fiber_count": 543,
        "membership_prefix": "rawGapMember",
        "lookup_module": "C2SelectorFoundationSelectorFiniteSubtypeRaw543IndexedLookup",
        "lookup_prefix": "rawSpectralGapLookup",
        "equivalence_name": "rawSpectralGapLookupFiberEquivFin",
    },
    {
        "selector_name": "lazy63",
        "selector_key": "lazy_componentwise_spectral_gap",
        "selector_agda": "lazyComponentwiseSpectralGap",
        "selector_index": 1,
        "fiber_count": 63,
        "membership_prefix": "lazyGapMember",
        "lookup_module": "C2SelectorFoundationSelectorFiniteSubtypeLazy63IndexedLookup",
        "lookup_prefix": "lazySpectralGapLookup",
        "equivalence_name": "lazySpectralGapLookupFiberEquivFin",
    },
    {
        "selector_name": "paired_lazy480",
        "selector_key": "paired_lazy_componentwise_spectral_gap",
        "selector_agda": "pairedLazyComponentwiseSpectralGap",
        "selector_index": 2,
        "fiber_count": 480,
        "membership_prefix": "pairedLazyGapMember",
        "lookup_module": "C2SelectorFoundationSelectorFiniteSubtypePairedLazy480IndexedLookup",
        "lookup_prefix": "pairedLazySpectralGapLookup",
        "equivalence_name": "pairedLazySpectralGapLookupFiberEquivFin",
    },
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


def normalize_lookup_row(row: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(row)
    for key in INT_FIELDS:
        normalized[key] = int(normalized[key])
    return normalized


def read_lookup_csv(path: Path) -> tuple[list[str], list[dict[str, Any]]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = [normalize_lookup_row(row) for row in reader]
    return fieldnames, rows


def read_halloween_orbits(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rows.append(
                {
                    "orbit_id": int(row["orbit_id"]),
                    "size": int(row["size"]),
                    "representative": int(row["representative"]),
                    "member_a": int(row["member_a"]),
                    "member_b": int(row["member_b"]),
                    "fixed": row["fixed"] == "True",
                    "nonzero": row["nonzero"] == "True",
                }
            )
    return rows


def rows_by_selector(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row["selector_name"]), []).append(row)
    return grouped


def selector_ids(rows: list[dict[str, Any]], selector_name: str) -> list[int]:
    return [int(row["dynamics_id"]) for row in rows if row["selector_name"] == selector_name]


def package_paths(package_dir: Path) -> dict[str, Path]:
    return {
        "manifest": package_dir / "manifest.json",
        "table_json": package_dir / "selector_lookup_witness_table.json",
        "table_csv": package_dir / "selector_lookup_witness_table.csv",
        "halloween_orbits_csv": package_dir / "halloween_actual_c2_kernel_orbits_raw543.csv",
        "certificate": package_dir / "source_package_certificate.json",
    }


def source_registry_binding(
    package_dir: Path = DEFAULT_PACKAGE_DIR,
    certificate_path: Path = PACKAGE_CERTIFICATE,
) -> dict[str, Any]:
    manifest_path = package_dir / "manifest.json"
    certificate = load_json(certificate_path) if certificate_path.exists() else {}
    certificate_payload_sha256 = (
        sha_json(
            {
                key: value
                for key, value in certificate.items()
                if key != "certificate_sha256"
            }
        )
        if certificate
        else None
    )
    manifest = load_json(manifest_path) if manifest_path.exists() else {}
    checks = {
        "registry_id_matches_package_name": certificate.get("package_name")
        == PACKAGE_REGISTRY_ID,
        "manifest_registry_id_matches_package_name": manifest.get("source_registry_id")
        == PACKAGE_REGISTRY_ID,
        "certificate_status_is_verified": certificate.get("status")
        == PACKAGE_VERIFIED_STATUS,
        "certificate_reports_all_package_checks_pass": certificate.get("all_checks_pass")
        is True,
        "certificate_hash_matches_payload": certificate.get("certificate_sha256")
        == certificate_payload_sha256,
        "package_uses_only_halloween_source_and_lookup_artifacts": certificate.get(
            "checks", {}
        ).get("package_uses_only_halloween_source_and_lookup_artifacts")
        is True,
    }
    return {
        "schema": "d20.source_registry.binding.v1",
        "source_registry_status": SOURCE_REGISTRY_STATUS,
        "source_package_registered_status": SOURCE_PACKAGE_REGISTERED_STATUS,
        "registry_id": PACKAGE_REGISTRY_ID,
        "package_name": certificate.get("package_name"),
        "package_dir": rel(package_dir),
        "manifest": {
            "path": rel(manifest_path),
            "sha256": sha_file(manifest_path) if manifest_path.exists() else None,
            "source_registry_id": manifest.get("source_registry_id"),
        },
        "certificate": {
            "path": rel(certificate_path),
            "sha256": sha_file(certificate_path) if certificate_path.exists() else None,
            "embedded_certificate_sha256": certificate.get("certificate_sha256"),
            "payload_sha256": certificate_payload_sha256,
            "status": certificate.get("status"),
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def attach_source_registry_binding_to_theorem_index(index: dict[str, Any]) -> dict[str, Any]:
    binding = source_registry_binding()
    compact_binding = {
        "schema": binding["schema"],
        "registry_id": binding["registry_id"],
        "package_name": binding["package_name"],
        "package_dir": binding["package_dir"],
        "certificate": binding["certificate"],
        "all_checks_pass": binding["all_checks_pass"],
        "bound_theorem_ids": sorted(HALLOWEEN_SOURCE_PACKAGE_THEOREM_IDS),
    }
    compact_binding["binding_sha256"] = sha_json(compact_binding)
    theorems = []
    for entry in index.get("theorems", []):
        updated = dict(entry)
        if updated.get("id") in HALLOWEEN_SOURCE_PACKAGE_THEOREM_IDS:
            updated["source_package_binding"] = {
                "registry_id": PACKAGE_REGISTRY_ID,
                "binding_sha256": compact_binding["binding_sha256"],
            }
        theorems.append(updated)
    out = dict(index)
    out["theorems"] = theorems
    out["theorem_count"] = len(theorems)
    out["source_package_bindings"] = {PACKAGE_REGISTRY_ID: compact_binding}
    out["source_package_binding_count"] = 1
    out["registry_sha256"] = sha_json(
        {key: value for key, value in out.items() if key != "registry_sha256"}
    )
    return out


def validate_theorem_registry_source_package_binding(
    index_path: Path = THEOREM_REGISTRY_INDEX,
) -> dict[str, Any]:
    index = load_json(index_path)
    binding = index.get("source_package_bindings", {}).get(PACKAGE_REGISTRY_ID, {})
    entries = {
        str(entry.get("id")): entry
        for entry in index.get("theorems", [])
        if isinstance(entry, dict)
    }
    bound_ids = sorted(str(item) for item in binding.get("bound_theorem_ids", []))
    embedded_registry_sha256 = index.get("registry_sha256")
    computed_registry_sha256 = sha_json(
        {key: value for key, value in index.items() if key != "registry_sha256"}
    )
    checks = {
        "theorem_registry_file_exists": index_path.exists(),
        "theorem_registry_schema_matches": index.get("schema") == "d20.theorem_registry",
        "theorem_registry_status_built": index.get("status")
        == "D20_THEOREM_REGISTRY_BUILT",
        "theorem_registry_hash_matches_payload": embedded_registry_sha256
        == computed_registry_sha256,
        "source_package_binding_count_is_one": index.get("source_package_binding_count")
        == 1,
        "halloween_binding_present": bool(binding),
        "halloween_binding_checks_pass": binding.get("all_checks_pass") is True,
        "halloween_binding_registry_id_matches": binding.get("registry_id")
        == PACKAGE_REGISTRY_ID,
        "halloween_binding_bound_theorem_ids_match_contract": bound_ids
        == sorted(HALLOWEEN_SOURCE_PACKAGE_THEOREM_IDS),
        "all_bound_theorem_entries_exist": all(
            theorem_id in entries for theorem_id in HALLOWEEN_SOURCE_PACKAGE_THEOREM_IDS
        ),
        "all_bound_entries_reference_binding": all(
            entries.get(theorem_id, {})
            .get("source_package_binding", {})
            .get("registry_id")
            == PACKAGE_REGISTRY_ID
            and entries.get(theorem_id, {})
            .get("source_package_binding", {})
            .get("binding_sha256")
            == binding.get("binding_sha256")
            for theorem_id in HALLOWEEN_SOURCE_PACKAGE_THEOREM_IDS
        ),
        "all_bound_report_hashes_match_report_certificates": all(
            (ROOT / str(entries.get(theorem_id, {}).get("report", ""))).exists()
            and entries.get(theorem_id, {}).get("report_sha256")
            == load_json(ROOT / str(entries.get(theorem_id, {}).get("report", ""))).get(
                "certificate_sha256"
            )
            for theorem_id in HALLOWEEN_SOURCE_PACKAGE_THEOREM_IDS
        ),
        "all_bound_manifest_files_exist": all(
            (ROOT / str(entries.get(theorem_id, {}).get("manifest", ""))).exists()
            for theorem_id in HALLOWEEN_SOURCE_PACKAGE_THEOREM_IDS
        ),
    }
    return {
        "schema": "d20.theorem_registry.source_package_binding_certificate.v1",
        "status": "D20_THEOREM_REGISTRY_HALLOWEEN_SOURCE_PACKAGE_BINDING_CERTIFIED"
        if all(checks.values())
        else "D20_THEOREM_REGISTRY_HALLOWEEN_SOURCE_PACKAGE_BINDING_NEEDS_REVIEW",
        "index_path": rel(index_path),
        "index_file_sha256": sha_file(index_path),
        "registry_sha256": embedded_registry_sha256,
        "computed_registry_sha256": computed_registry_sha256,
        "source_package_registry_id": PACKAGE_REGISTRY_ID,
        "bound_theorem_ids": bound_ids,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def verify_source_package(
    package_dir: Path = DEFAULT_PACKAGE_DIR, out_path: Path | None = None
) -> dict[str, Any]:
    paths = package_paths(package_dir)
    manifest = load_json(paths["manifest"])
    table = load_json(paths["table_json"])
    csv_fieldnames, csv_rows = read_lookup_csv(paths["table_csv"])
    json_rows = [normalize_lookup_row(row) for row in table.get("rows", [])]
    halloween_rows = read_halloween_orbits(paths["halloween_orbits_csv"])

    grouped = rows_by_selector(json_rows)
    orbit_ids = [row["orbit_id"] for row in halloween_rows]
    fixed_ids = [row["orbit_id"] for row in halloween_rows if row["fixed"]]
    paired_ids = [row["orbit_id"] for row in halloween_rows if not row["fixed"]]
    selector_counts = {
        name: len(selector_rows) for name, selector_rows in sorted(grouped.items())
    }
    selector_order = [contract["selector_name"] for contract in SELECTOR_CONTRACTS]
    expected_selector_counts = {"lazy63": 63, "paired_lazy480": 480, "raw543": 543}
    manifest_json = {k: v for k, v in manifest.items() if k != "manifest_sha256"}
    table_json = {k: v for k, v in table.items() if k != "table_sha256"}

    selector_contract_checks: dict[str, bool] = {}
    for contract in SELECTOR_CONTRACTS:
        selector_rows = grouped.get(str(contract["selector_name"]), [])
        selector_contract_checks[str(contract["selector_name"])] = (
            len(selector_rows) == int(contract["fiber_count"])
            and [int(row["fiber_index"]) for row in selector_rows]
            == list(range(int(contract["fiber_count"])))
            and all(
                int(row["selector_index"]) == int(contract["selector_index"])
                and row["selector_key"] == contract["selector_key"]
                and row["selector_agda"] == contract["selector_agda"]
                and int(row["fiber_count"]) == int(contract["fiber_count"])
                and row["dynamics_constructor"] == f"d{int(row['dynamics_id'])}"
                and row["membership_constructor"]
                == f"{contract['membership_prefix']}{int(row['dynamics_id'])}"
                and int(row["index_bound_witness"])
                == int(contract["fiber_count"]) - int(row["fiber_index"]) - 1
                and row["lookup_module"] == contract["lookup_module"]
                and row["lookup_prefix"] == contract["lookup_prefix"]
                and row["equivalence_name"] == contract["equivalence_name"]
                for row in selector_rows
            )
        )

    checks = {
        "manifest_schema_is_lookup_witness_source_package": manifest.get("schema")
        == PACKAGE_SCHEMA,
        "manifest_status_is_locked": manifest.get("status") == PACKAGE_LOCKED_STATUS,
        "manifest_hash_matches_payload": manifest.get("manifest_sha256")
        == sha_json(manifest_json),
        "manifest_names_halloween_source": manifest.get("package_name")
        == PACKAGE_REGISTRY_ID,
        "manifest_source_registry_id_matches_package_name": manifest.get(
            "source_registry_id"
        )
        == PACKAGE_REGISTRY_ID,
        "package_files_exist": all(path.exists() and path.stat().st_size > 0 for path in paths.values() if path.name != "source_package_certificate.json"),
        "manifest_artifact_hashes_match_files": (
            manifest.get("artifacts", {})
            .get("selector_lookup_witness_table_json", {})
            .get("sha256")
            == sha_file(paths["table_json"])
            and manifest.get("artifacts", {})
            .get("selector_lookup_witness_table_csv", {})
            .get("sha256")
            == sha_file(paths["table_csv"])
            and manifest.get("source", {})
            .get("halloween_actual_c2_kernel_orbits_csv", {})
            .get("sha256")
            == sha_file(paths["halloween_orbits_csv"])
        ),
        "table_embedded_hash_matches_payload": table.get("table_sha256")
        == sha_json(table_json),
        "table_json_and_csv_rows_match": json_rows == csv_rows,
        "csv_fieldnames_match_contract": csv_fieldnames == CSV_FIELDNAMES,
        "table_has_1086_rows_and_three_selectors": table.get("row_count") == 1086
        and len(json_rows) == 1086
        and table.get("selector_count") == 3,
        "row_ids_are_contiguous": [int(row["row_id"]) for row in json_rows]
        == list(range(1086)),
        "selector_counts_match_contract": selector_counts == expected_selector_counts,
        "selector_contracts_hold": all(selector_contract_checks.values()),
        "halloween_orbit_ids_are_contiguous": orbit_ids == list(range(543)),
        "halloween_orbit_split_is_63_plus_480": len(fixed_ids) == 63
        and len(paired_ids) == 480
        and all(row["nonzero"] for row in halloween_rows),
        "raw543_rows_match_halloween_orbit_order": selector_ids(json_rows, "raw543")
        == orbit_ids,
        "lazy63_rows_match_halloween_fixed_orbits": selector_ids(json_rows, "lazy63")
        == fixed_ids,
        "paired_lazy480_rows_match_halloween_paired_orbits": selector_ids(
            json_rows, "paired_lazy480"
        )
        == paired_ids,
        "manifest_lock_contract_matches_rows": (
            manifest.get("lock_contract", {}).get("row_count") == 1086
            and manifest.get("lock_contract", {}).get("selector_counts")
            == expected_selector_counts
            and manifest.get("lock_contract", {}).get("selector_order")
            == selector_order
            and manifest.get("lock_contract", {}).get("table_sha256")
            == table.get("table_sha256")
            and manifest.get("lock_contract", {})
            .get("actual_c2_kernel_split", {})
            .get("raw543_orbit_count")
            == 543
            and manifest.get("lock_contract", {})
            .get("actual_c2_kernel_split", {})
            .get("fixed63_orbit_count")
            == 63
            and manifest.get("lock_contract", {})
            .get("actual_c2_kernel_split", {})
            .get("paired480_two_cycle_orbit_count")
            == 480
        ),
        "package_uses_only_halloween_source_and_lookup_artifacts": sorted(
            manifest.get("source", {}).keys()
        )
        == ["halloween_actual_c2_kernel_orbits_csv"]
        and sorted(manifest.get("artifacts", {}).keys())
        == ["selector_lookup_witness_table_csv", "selector_lookup_witness_table_json"],
    }
    all_checks_pass = all(checks.values())
    report = {
        "schema": "d20.selector_finite_subtype.lookup_witness_source_package_certificate.v1",
        "status": PACKAGE_VERIFIED_STATUS
        if all_checks_pass
        else "D20_C2_SELECTOR_LOOKUP_WITNESS_SOURCE_PACKAGE_NEEDS_REVIEW",
        "package_dir": rel(package_dir),
        "package_name": manifest.get("package_name"),
        "source": {
            "halloween_actual_c2_kernel_orbits_csv": {
                "path": rel(paths["halloween_orbits_csv"]),
                "sha256": sha_file(paths["halloween_orbits_csv"]),
                "row_count": len(halloween_rows),
                "fixed63_orbit_count": len(fixed_ids),
                "paired480_two_cycle_orbit_count": len(paired_ids),
            },
        },
        "artifacts": {
            "manifest": {
                "path": rel(paths["manifest"]),
                "sha256": sha_file(paths["manifest"]),
                "embedded_manifest_sha256": manifest.get("manifest_sha256"),
            },
            "selector_lookup_witness_table_json": {
                "path": rel(paths["table_json"]),
                "sha256": sha_file(paths["table_json"]),
                "embedded_table_sha256": table.get("table_sha256"),
            },
            "selector_lookup_witness_table_csv": {
                "path": rel(paths["table_csv"]),
                "sha256": sha_file(paths["table_csv"]),
                "fieldnames": csv_fieldnames,
            },
        },
        "derived": {
            "row_count": len(json_rows),
            "selector_count": len(grouped),
            "selector_counts": selector_counts,
            "selector_contract_checks": selector_contract_checks,
            "selector_order": selector_order,
            "halloween_orbit_split": {
                "raw543_orbit_count": len(orbit_ids),
                "fixed63_orbit_count": len(fixed_ids),
                "paired480_two_cycle_orbit_count": len(paired_ids),
            },
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
    }
    report["certificate_sha256"] = sha_json(
        {k: v for k, v in report.items() if k != "certificate_sha256"}
    )
    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    return report


def main() -> None:
    report = verify_source_package(DEFAULT_PACKAGE_DIR, PACKAGE_CERTIFICATE)
    print(report["status"])
    print(report["certificate_sha256"])


if __name__ == "__main__":
    main()
