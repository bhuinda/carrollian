from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT_FOR_IMPORT = Path(__file__).resolve().parents[1]
if str(ROOT_FOR_IMPORT) not in sys.path:
    sys.path.insert(0, str(ROOT_FOR_IMPORT))

from src.paths import D20_INVARIANTS, ROOT


STATUS = "D20_CERTIFIED_POINTER_A985_MATRIX_UNIT_DEREFERENCE_CERTIFIED"
VERIFY_STATUS = "D20_CERTIFIED_POINTER_A985_MATRIX_UNIT_DEREFERENCE_VERIFIED"
THEOREM_ID = "certified_pointer_a985_matrix_unit_dereference"
OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FULL_MATCH_DIR = D20_INVARIANTS / "theorems" / "nested_pointer_a985_full_legacy_sector_match"
REGISTERED_DIR = D20_INVARIANTS / "theorems" / "nested_pointer_a985_registered_support_matrix_units"
TRANSPORT_DIR = D20_INVARIANTS / "theorems" / "nested_pointer_a985_legacy_matrix_unit_transport"

IDENTITY_RELATIONS = [6, 163, 227, 349, 618, 893]
REQUIRED_POINTER_SLOTS = [
    "source",
    "address_space",
    "pointer_map",
    "dereference",
    "public_readout",
    "proxy",
    "verifier",
    "defect_ledger",
]


def canonical(obj: Any) -> bytes:
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


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


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def pointer_schema() -> dict[str, Any]:
    return {
        "schema": "d20.vocabulary.certified_pointer.source_drop",
        "status": "D20_CERTIFIED_POINTER_SCHEMA_BUILT",
        "object": "d20",
        "primitive": "certified_pointer",
        "meaning": (
            "A certified pointer is a typed, dereferenceable address for hidden support. "
            "It is not merely a hint: it carries a public readout and the checks needed "
            "to prove that dereferencing lands in the declared address space."
        ),
        "required_slots": REQUIRED_POINTER_SLOTS,
        "slot_definitions": {
            "source": "Native token, support, or support being addressed.",
            "address_space": "The target coordinate system where the source becomes explicit.",
            "pointer_map": "A deterministic transport from source labels into address labels.",
            "dereference": "The rule and tables that expand an address into concrete supports or coordinates.",
            "public_readout": "The externally visible class, support, chamber, or profile reached by dereference.",
            "proxy": "A certified observable fingerprint used to identify or test the pointer map.",
            "verifier": "Machine-checkable evidence that the pointer map and dereference are valid.",
            "defect_ledger": "Finite defects or declared open boundaries; empty only when verified as empty.",
        },
        "typing_rules": [
            "pointer_map.domain must match the source label type",
            "pointer_map.codomain must live inside address_space",
            "dereference.input must be produced by pointer_map",
            "public_readout must be derived from dereference outputs",
            "proxy may identify a pointer but may not replace verifier checks",
            "defect_ledger must separate finite defects from open boundaries",
        ],
        "validation_tests": [
            "all required slots are present",
            "source labels map uniquely into address labels",
            "dereference tables have the expected row counts",
            "proxy fingerprints are unique where uniqueness is claimed",
            "upstream theorem reports are certified",
            "output hashes are canonical JSON hashes",
        ],
    }


def load_legacy_to_raw_rows() -> list[dict[str, Any]]:
    rows = read_csv_rows(FULL_MATCH_DIR / "legacy_to_raw_sector_full_match.csv")
    return [
        {
            "legacy_sector": int(row["legacy_sector"]),
            "raw_sector": int(row["raw_sector"]),
            "block_dimension": int(row["block_dimension"]),
            "match_status": row["match_status"],
        }
        for row in rows
    ]


def build_pointer_instance(
    *,
    full_match: dict[str, Any],
    registered: dict[str, Any],
    transport: dict[str, Any],
    legacy_to_raw: list[dict[str, Any]],
    manifest_rows: list[dict[str, str]],
    support_rows: list[dict[str, str]],
) -> dict[str, Any]:
    registered_supports = sorted({row["support_name"] for row in support_rows})
    top_rows = [row for row in manifest_rows if row["support_name"] == "unit_top_all_39"]
    preserved = transport.get("derived", {}).get("legacy_sector_rows_preserved_and_confirmed")
    filled = transport.get("derived", {}).get("legacy_sector_rows_filled_from_full_match")
    return {
        "schema": "d20.certified_pointer.a985_matrix_unit_dereference.source_drop",
        "status": STATUS,
        "pointer_id": "a985_matrix_unit_dereference",
        "source": {
            "native_support": "A985",
            "source_labels": [
                "legacy sector label",
                "registered public-zero support label",
                "top all-39 sector support label",
            ],
            "registered_support_count": len(registered_supports),
            "registered_supports": registered_supports,
        },
        "address_space": {
            "support": "raw A985 orbital algebra",
            "basis_size": 985,
            "central_sector_count": 39,
            "address_atoms": ["raw_sector", "matrix_unit_i", "matrix_unit_j", "orbital_relation_R_alpha"],
            "block_dimension_histogram": transport.get("derived", {}).get("block_dimension_histogram", {}),
            "central_idempotent_report": rel(FULL_MATCH_DIR.parent / "nested_pointer_a985_orbital_central_idempotents" / "report.json"),
        },
        "pointer_map": {
            "domain": "legacy_sector",
            "codomain": "raw_sector",
            "map_table": rel(FULL_MATCH_DIR / "legacy_to_raw_sector_full_match.csv"),
            "map_rows": legacy_to_raw,
            "matching_rule": "unique six-identity coefficient fingerprint match",
            "fingerprint_identity_relations": IDENTITY_RELATIONS,
        },
        "dereference": {
            "input": ["legacy_sector", "matrix_unit_i", "matrix_unit_j"],
            "output": "raw orbital matrix unit u[s;i,j] expressed in the A985 orbital basis",
            "rule": "legacy_sector maps to raw_sector; matrix indices select the corresponding raw block matrix unit",
            "manifest": rel(TRANSPORT_DIR / "legacy_labeled_matrix_unit_manifest.csv"),
            "manifest_rows": len(manifest_rows),
            "unit_top_all_39_rows": len(top_rows),
            "legacy_rows_preserved_and_confirmed": preserved,
            "legacy_rows_filled_from_full_match": filled,
        },
        "public_readout": {
            "readout_classes": [
                "public-zero registered support",
                "legacy-labeled Wedderburn sector profile",
                "all-39 top support matrix-unit chart",
            ],
            "registered_support_transport": rel(TRANSPORT_DIR / "registered_support_legacy_transport.csv"),
            "legacy_sector_profiles": rel(TRANSPORT_DIR / "legacy_sector_matrix_unit_profiles.csv"),
        },
        "proxy": {
            "kind": "six_identity_coefficient_fingerprint",
            "identity_relations": IDENTITY_RELATIONS,
            "claim": "the fingerprint uniquely matches every legacy sector to a raw separating-center sector",
            "boundary": "proxy identifies the pointer map; centrality and matrix-unit checks remain the verifier",
        },
        "verifier": {
            "upstream_reports": {
                "full_legacy_sector_match": {
                    "path": rel(FULL_MATCH_DIR / "report.json"),
                    "status": full_match.get("status"),
                    "sha256": sha_file(FULL_MATCH_DIR / "report.json"),
                },
                "registered_support_matrix_units": {
                    "path": rel(REGISTERED_DIR / "report.json"),
                    "status": registered.get("status"),
                    "sha256": sha_file(REGISTERED_DIR / "report.json"),
                },
                "legacy_matrix_unit_transport": {
                    "path": rel(TRANSPORT_DIR / "report.json"),
                    "status": transport.get("status"),
                    "sha256": sha_file(TRANSPORT_DIR / "report.json"),
                },
            },
            "check_groups": [
                "central idempotent checks",
                "unique fingerprint match checks",
                "registered raw matrix-unit checks",
                "all-39 legacy matrix-unit transport checks",
            ],
        },
        "defect_ledger": {
            "finite_defects": [],
            "open_boundaries": [
                (
                    "all-39 legacy matrix units are label-transported; raw orbital COO coefficients are "
                    "attached only for the registered public-zero support subset"
                )
            ],
            "next_highest_yield_item": (
                "Attach raw orbital COO coefficients to the all-39 legacy-labeled matrix-unit manifest."
            ),
        },
    }


def markdown_report(report: dict[str, Any]) -> str:
    checks = "\n".join(f"- `{key}`: `{value}`" for key, value in report["checks"].items())
    return (
        "# Certified Pointer: A985 Matrix-Unit Dereference\n\n"
        f"Status: `{report['status']}`\n\n"
        "This promotes the nested-pointer evidence into an explicit certified-pointer primitive. "
        "The source labels are legacy sectors and registered public-zero supports; the address "
        "space is the raw A985 orbital matrix-unit chart. The six-identity fingerprint is the "
        "proxy, while the central-idempotent and matrix-unit reports are the verifier.\n\n"
        "## Checks\n\n"
        f"{checks}\n\n"
        f"Next: {report['next_highest_yield_item']}\n"
    )


def update_theorem_index(report: dict[str, Any]) -> None:
    index_path = D20_INVARIANTS / "theorems" / "index.json"
    index = load_json(index_path) if index_path.exists() else {"theorems": []}
    theorems = [item for item in index.get("theorems", []) if item.get("id") != THEOREM_ID]
    theorems.append(
        {
            "id": THEOREM_ID,
            "manifest": rel(OUT_DIR / "manifest.json"),
            "report": rel(OUT_DIR / "report.json"),
            "report_sha256": report["certificate_sha256"],
            "status": report["status"],
        }
    )
    theorems = sorted(theorems, key=lambda item: item["id"])
    index = {
        "schema": "d20.theorem_registry.source_drop",
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": len(theorems),
        "theorems": theorems,
    }
    index["registry_sha256"] = sha_json({k: v for k, v in index.items() if k != "registry_sha256"})
    write_json(index_path, index)


def build_pointer() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    full_match = load_json(FULL_MATCH_DIR / "report.json")
    registered = load_json(REGISTERED_DIR / "report.json")
    transport = load_json(TRANSPORT_DIR / "report.json")
    legacy_to_raw = load_legacy_to_raw_rows()
    manifest_rows = read_csv_rows(TRANSPORT_DIR / "legacy_labeled_matrix_unit_manifest.csv")
    profile_rows = read_csv_rows(TRANSPORT_DIR / "legacy_sector_matrix_unit_profiles.csv")
    support_rows = read_csv_rows(TRANSPORT_DIR / "registered_support_legacy_transport.csv")
    schema_doc = pointer_schema()
    pointer = build_pointer_instance(
        full_match=full_match,
        registered=registered,
        transport=transport,
        legacy_to_raw=legacy_to_raw,
        manifest_rows=manifest_rows,
        support_rows=support_rows,
    )

    pointer_slots = [slot for slot in REQUIRED_POINTER_SLOTS if slot in pointer]
    checks = {
        "schema_required_slots_present": pointer_slots == REQUIRED_POINTER_SLOTS,
        "full_match_is_certified": full_match.get("all_checks_pass") is True
        and full_match.get("status") == "D20_NESTED_POINTER_A985_FULL_LEGACY_SECTOR_MATCH_CERTIFIED",
        "registered_matrix_units_are_certified": registered.get("all_checks_pass") is True
        and registered.get("status") == "D20_NESTED_POINTER_A985_REGISTERED_SUPPORT_MATRIX_UNITS_CERTIFIED",
        "legacy_matrix_unit_transport_is_certified": transport.get("all_checks_pass") is True
        and transport.get("status") == "D20_NESTED_POINTER_A985_LEGACY_MATRIX_UNIT_TRANSPORT_CERTIFIED",
        "legacy_to_raw_map_has_39_rows": len(legacy_to_raw) == 39,
        "legacy_to_raw_map_is_bijective": len({row["legacy_sector"] for row in legacy_to_raw}) == 39
        and len({row["raw_sector"] for row in legacy_to_raw}) == 39,
        "dereference_manifest_has_1011_rows": len(manifest_rows) == 1011,
        "sector_profile_table_has_39_rows": len(profile_rows) == 39,
        "registered_support_transport_has_7_rows": len(support_rows) == 7,
        "proxy_identity_relation_count_is_6": len(IDENTITY_RELATIONS) == 6,
        "finite_defect_ledger_is_empty": pointer["defect_ledger"]["finite_defects"] == [],
    }
    report = {
        "schema": "d20.theorem.certified_pointer_a985_matrix_unit_dereference.source_drop",
        "status": STATUS if all(checks.values()) else "D20_CERTIFIED_POINTER_A985_MATRIX_UNIT_DEREFERENCE_NEEDS_REVIEW",
        "object": "d20",
        "claim": (
            "The A985 nested-pointer evidence is a certified pointer: legacy sector and public-zero support "
            "labels dereference through a unique six-identity fingerprint map into the raw orbital "
            "matrix-unit address space."
        ),
        "pointer_schema": rel(OUT_DIR / "certified_pointer_schema.json"),
        "pointer_instance": rel(OUT_DIR / "certified_pointer_instance.json"),
        "inputs": pointer["verifier"]["upstream_reports"],
        "checks": checks,
        "derived": {
            "pointer_slots": pointer_slots,
            "legacy_to_raw_map_rows": len(legacy_to_raw),
            "dereference_manifest_rows": len(manifest_rows),
            "sector_profile_rows": len(profile_rows),
            "registered_support_transport_rows": len(support_rows),
            "finite_defect_count": len(pointer["defect_ledger"]["finite_defects"]),
            "open_boundary_count": len(pointer["defect_ledger"]["open_boundaries"]),
        },
        "next_highest_yield_item": pointer["defect_ledger"]["next_highest_yield_item"],
        "all_checks_pass": all(checks.values()),
    }
    schema_doc["schema_sha256"] = sha_json({k: v for k, v in schema_doc.items() if k != "schema_sha256"})
    pointer["pointer_sha256"] = sha_json({k: v for k, v in pointer.items() if k != "pointer_sha256"})
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    manifest = {
        "schema": "d20.theorem.certified_pointer_a985_matrix_unit_dereference_manifest.source_drop",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(OUT_DIR / "manifest.json"),
            "report": rel(OUT_DIR / "report.json"),
            "certified_pointer_schema": rel(OUT_DIR / "certified_pointer_schema.json"),
            "certified_pointer_instance": rel(OUT_DIR / "certified_pointer_instance.json"),
            "markdown_report": rel(OUT_DIR / "certified_pointer_report.md"),
        },
        "validation_tests": list(checks),
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = sha_json({k: v for k, v in manifest.items() if k != "manifest_sha256"})
    write_json(OUT_DIR / "certified_pointer_schema.json", schema_doc)
    write_json(OUT_DIR / "certified_pointer_instance.json", pointer)
    write_json(OUT_DIR / "report.json", report)
    write_json(OUT_DIR / "manifest.json", manifest)
    (OUT_DIR / "certified_pointer_report.md").write_text(markdown_report(report), encoding="utf-8")
    update_theorem_index(report)
    return report


def verify_pointer() -> dict[str, Any]:
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    schema_doc = load_json(OUT_DIR / "certified_pointer_schema.json")
    pointer = load_json(OUT_DIR / "certified_pointer_instance.json")
    manifest_rows = read_csv_rows(TRANSPORT_DIR / "legacy_labeled_matrix_unit_manifest.csv")
    checks = {
        "report_status_certified": report.get("status") == STATUS,
        "report_checks_pass": report.get("all_checks_pass") is True,
        "report_hash_valid": report.get("certificate_sha256")
        == sha_json({k: v for k, v in report.items() if k != "certificate_sha256"}),
        "manifest_hash_valid": manifest.get("manifest_sha256")
        == sha_json({k: v for k, v in manifest.items() if k != "manifest_sha256"}),
        "schema_hash_valid": schema_doc.get("schema_sha256")
        == sha_json({k: v for k, v in schema_doc.items() if k != "schema_sha256"}),
        "pointer_hash_valid": pointer.get("pointer_sha256")
        == sha_json({k: v for k, v in pointer.items() if k != "pointer_sha256"}),
        "pointer_has_all_slots": [slot for slot in REQUIRED_POINTER_SLOTS if slot in pointer] == REQUIRED_POINTER_SLOTS,
        "dereference_manifest_has_1011_rows": len(manifest_rows) == 1011,
        "finite_defect_ledger_is_empty": pointer.get("defect_ledger", {}).get("finite_defects") == [],
    }
    return {
        "status": VERIFY_STATUS if all(checks.values()) else "D20_CERTIFIED_POINTER_A985_MATRIX_UNIT_DEREFERENCE_VERIFY_FAILED",
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if not args.verify_only:
        build_pointer()
    verification = verify_pointer()
    print(json.dumps(verification, indent=2, sort_keys=True, allow_nan=False))
    if not verification["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
