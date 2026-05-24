from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT_FOR_IMPORT = Path(__file__).resolve().parents[1]
if str(ROOT_FOR_IMPORT) not in sys.path:
    sys.path.insert(0, str(ROOT_FOR_IMPORT))

from src.paths import D20_INVARIANTS, ROOT


STATUS = "D20_TINY_POINTER_A985_LEGACY_MATRIX_UNIT_TRANSPORT_CERTIFIED"
THEOREM_ID = "tiny_pointer_a985_legacy_matrix_unit_transport"
OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FULL_MATCH_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_full_legacy_sector_match"
REGISTERED_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_registered_support_matrix_units"
FULL_A985_LIFT = ROOT / "layers" / "drinfeld" / "full_a985_lift.json"


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


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv_rows(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def parse_set(text: str) -> set[int]:
    text = text.strip()
    if text in {"", "{}"}:
        return set()
    if not (text.startswith("{") and text.endswith("}")):
        raise ValueError(f"not a set literal: {text}")
    body = text[1:-1].strip()
    if not body:
        return set()
    return {int(part.strip()) for part in body.split(",")}


def set_literal(values: set[int] | list[int]) -> str:
    vals = sorted(int(value) for value in values)
    return "{" + ",".join(str(value) for value in vals) + "}"


def load_maps() -> tuple[dict[int, int], dict[int, int], dict[int, int]]:
    rows = read_csv_rows(FULL_MATCH_DIR / "legacy_to_raw_sector_full_match.csv")
    legacy_to_raw = {int(row["legacy_sector"]): int(row["raw_sector"]) for row in rows}
    raw_to_legacy = {raw: legacy for legacy, raw in legacy_to_raw.items()}
    dimensions = {int(row["legacy_sector"]): int(row["block_dimension"]) for row in rows}
    return legacy_to_raw, raw_to_legacy, dimensions


def transported_manifest(raw_to_legacy: dict[int, int], dimensions: dict[int, int]) -> list[dict[str, Any]]:
    source_rows = read_csv_rows(REGISTERED_DIR / "registered_support_matrix_unit_manifest.csv")
    out: list[dict[str, Any]] = []
    for source_index, row in enumerate(source_rows):
        raw_sector = int(row["raw_sector"])
        legacy_sector = raw_to_legacy[raw_sector]
        original_legacy = row["legacy_sector"].strip()
        original_legacy_status = (
            "FILLED_FROM_FULL_MATCH"
            if original_legacy == ""
            else "PRESERVED_AND_CONFIRMED"
            if int(original_legacy) == legacy_sector
            else "MISMATCH"
        )
        i = int(row["i"])
        j = int(row["j"])
        transported = {
            "source_row": source_index,
            "support_name": row["support_name"],
            "legacy_support": row["legacy_support"],
            "raw_support": row["raw_support"],
            "legacy_sector": legacy_sector,
            "raw_sector": raw_sector,
            "block_dimension": int(row["block_dimension"]),
            "i": i,
            "j": j,
            "object_i": int(row["object_i"]),
            "object_j": int(row["object_j"]),
            "nonzero_coefficients": int(row["nonzero_coefficients"]),
            "legacy_matrix_unit_label": f"u_legacy[{legacy_sector};{i},{j}]",
            "raw_matrix_unit_label": row["matrix_unit_label"],
            "legacy_sector_source": original_legacy_status,
        }
        if transported["block_dimension"] != dimensions[legacy_sector]:
            transported["legacy_sector_source"] = "DIMENSION_MISMATCH"
        out.append(transported)
    return out


def sector_profiles(
    legacy_to_raw: dict[int, int],
    dimensions: dict[int, int],
    transported_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    full = load_json(FULL_A985_LIFT)
    by_legacy = {
        int(profile["sector"]): profile
        for profile in full["gluing_and_sector_profiles"]["sector_profiles"]
    }
    unit_rows_by_legacy: dict[int, list[dict[str, Any]]] = {}
    for row in transported_rows:
        if row["support_name"] == "unit_top_all_39":
            unit_rows_by_legacy.setdefault(int(row["legacy_sector"]), []).append(row)

    out: list[dict[str, Any]] = []
    for legacy_sector in sorted(legacy_to_raw):
        raw_sector = legacy_to_raw[legacy_sector]
        dimension = dimensions[legacy_sector]
        rows = sorted(unit_rows_by_legacy.get(legacy_sector, []), key=lambda item: (int(item["i"]), int(item["j"])))
        profile = by_legacy[legacy_sector]
        out.append(
            {
                "legacy_sector": legacy_sector,
                "raw_sector": raw_sector,
                "block_dimension": dimension,
                "matrix_unit_count": len(rows),
                "expected_matrix_unit_count": dimension * dimension,
                "first_legacy_matrix_unit_label": rows[0]["legacy_matrix_unit_label"] if rows else "",
                "last_legacy_matrix_unit_label": rows[-1]["legacy_matrix_unit_label"] if rows else "",
                "first_raw_matrix_unit_label": rows[0]["raw_matrix_unit_label"] if rows else "",
                "last_raw_matrix_unit_label": rows[-1]["raw_matrix_unit_label"] if rows else "",
                "active_objects": ",".join(profile.get("active_objects", [])),
                "permutation_rank": int(profile["permutation_rank"]),
                "permutation_multiplicity": int(profile["permutation_multiplicity"]),
                "regular_trace_block_square": int(profile["regular_trace_block_square"]),
                "q42_nonzero_count": int(profile["q42_nonzero_count"]),
                "q12_nonzero_count": int(profile["q12_nonzero_count"]),
                "legacy_identity_fingerprint": json.dumps(profile["identity_coefficients_signed"]),
            }
        )
    return out


def support_transport_rows(
    transported_rows: list[dict[str, Any]],
    raw_to_legacy: dict[int, int],
) -> list[dict[str, Any]]:
    resolution = read_csv_rows(REGISTERED_DIR / "registered_support_raw_resolution.csv")
    out: list[dict[str, Any]] = []
    for row in resolution:
        raw_support = parse_set(row["raw_support"])
        transported_legacy = {raw_to_legacy[raw] for raw in raw_support}
        rows = [item for item in transported_rows if item["support_name"] == row["name"]]
        out.append(
            {
                "support_name": row["name"],
                "legacy_support": row["legacy_support"],
                "raw_support": row["raw_support"],
                "transported_legacy_support": set_literal(transported_legacy),
                "raw_rank": int(row["raw_rank"]),
                "matrix_unit_rows": len(rows),
                "resolution_status": row["resolution_status"],
                "transport_status": "LEGACY_LABELS_TRANSPORTED",
            }
        )
    return out


def markdown_report(report: dict[str, Any]) -> str:
    checks = "\n".join(f"- `{key}`: `{value}`" for key, value in report["checks"].items())
    return (
        "# Legacy Matrix-Unit Transport\n\n"
        f"Status: `{report['status']}`\n\n"
        "The full legacy-sector map is now applied to the registered raw matrix-unit manifest. "
        "Rows with blank legacy-sector labels in the top support are filled from the certified all-39 match, "
        "while previously registered support rows are preserved and checked.\n\n"
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


def build_transport() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    full_match = load_json(FULL_MATCH_DIR / "report.json")
    registered = load_json(REGISTERED_DIR / "report.json")
    legacy_to_raw, raw_to_legacy, dimensions = load_maps()
    rows = transported_manifest(raw_to_legacy, dimensions)
    profiles = sector_profiles(legacy_to_raw, dimensions, rows)
    supports = support_transport_rows(rows, raw_to_legacy)

    manifest_fields = [
        "source_row",
        "support_name",
        "legacy_support",
        "raw_support",
        "legacy_sector",
        "raw_sector",
        "block_dimension",
        "i",
        "j",
        "object_i",
        "object_j",
        "nonzero_coefficients",
        "legacy_matrix_unit_label",
        "raw_matrix_unit_label",
        "legacy_sector_source",
    ]
    profile_fields = [
        "legacy_sector",
        "raw_sector",
        "block_dimension",
        "matrix_unit_count",
        "expected_matrix_unit_count",
        "first_legacy_matrix_unit_label",
        "last_legacy_matrix_unit_label",
        "first_raw_matrix_unit_label",
        "last_raw_matrix_unit_label",
        "active_objects",
        "permutation_rank",
        "permutation_multiplicity",
        "regular_trace_block_square",
        "q42_nonzero_count",
        "q12_nonzero_count",
        "legacy_identity_fingerprint",
    ]
    support_fields = [
        "support_name",
        "legacy_support",
        "raw_support",
        "transported_legacy_support",
        "raw_rank",
        "matrix_unit_rows",
        "resolution_status",
        "transport_status",
    ]
    write_csv_rows(OUT_DIR / "legacy_labeled_matrix_unit_manifest.csv", manifest_fields, rows)
    write_csv_rows(OUT_DIR / "legacy_sector_matrix_unit_profiles.csv", profile_fields, profiles)
    write_csv_rows(OUT_DIR / "registered_support_legacy_transport.csv", support_fields, supports)

    top_rows = [row for row in rows if row["support_name"] == "unit_top_all_39"]
    top_counts = Counter(int(row["legacy_sector"]) for row in top_rows)
    mismatch_rows = [
        row for row in rows
        if row["legacy_sector_source"] in {"MISMATCH", "DIMENSION_MISMATCH"}
    ]
    filled_rows = sum(1 for row in rows if row["legacy_sector_source"] == "FILLED_FROM_FULL_MATCH")
    preserved_rows = sum(1 for row in rows if row["legacy_sector_source"] == "PRESERVED_AND_CONFIRMED")
    profile_mismatches = [
        row for row in profiles
        if int(row["matrix_unit_count"]) != int(row["expected_matrix_unit_count"])
    ]
    support_mismatches = [
        row for row in supports
        if parse_set(row["legacy_support"]) != parse_set(row["transported_legacy_support"])
        and row["support_name"] not in {"unit_top_all_39", "zero"}
    ]

    checks = {
        "full_match_is_certified": full_match.get("status") == "D20_TINY_POINTER_A985_FULL_LEGACY_SECTOR_MATCH_CERTIFIED"
        and full_match.get("all_checks_pass") is True,
        "registered_stage_is_certified": registered.get("status")
        == "D20_TINY_POINTER_A985_REGISTERED_SUPPORT_MATRIX_UNITS_CERTIFIED"
        and registered.get("all_checks_pass") is True,
        "transported_manifest_row_count_is_1011": len(rows) == 1011,
        "all_rows_have_legacy_sector": all(str(row["legacy_sector"]) != "" for row in rows),
        "no_transport_mismatch_rows": not mismatch_rows,
        "top_support_has_985_rows": len(top_rows) == 985,
        "top_support_covers_all_39_legacy_sectors": len(top_counts) == 39,
        "top_support_counts_are_d_squared": all(
            top_counts[legacy] == dimensions[legacy] * dimensions[legacy]
            for legacy in dimensions
        ),
        "sector_profile_count_is_39": len(profiles) == 39,
        "sector_profile_matrix_unit_counts_match_d_squared": not profile_mismatches,
        "registered_support_legacy_transport_matches_source": not support_mismatches,
    }
    report = {
        "schema": "d20.theorem.tiny_pointer_a985_legacy_matrix_unit_transport.source_drop",
        "status": STATUS if all(checks.values()) else "D20_TINY_POINTER_A985_LEGACY_MATRIX_UNIT_TRANSPORT_NEEDS_REVIEW",
        "object": "d20",
        "claim": (
            "The certified full legacy-to-raw sector match transports legacy sector labels and sector-local "
            "Wedderburn profile data onto the registered raw A985 matrix-unit manifest."
        ),
        "inputs": {
            "full_legacy_sector_match": {
                "path": rel(FULL_MATCH_DIR / "report.json"),
                "sha256": sha_file(FULL_MATCH_DIR / "report.json"),
            },
            "registered_support_matrix_units": {
                "path": rel(REGISTERED_DIR / "report.json"),
                "sha256": sha_file(REGISTERED_DIR / "report.json"),
            },
            "registered_raw_manifest": {
                "path": rel(REGISTERED_DIR / "registered_support_matrix_unit_manifest.csv"),
                "sha256": sha_file(REGISTERED_DIR / "registered_support_matrix_unit_manifest.csv"),
            },
            "full_a985_lift": {
                "path": rel(FULL_A985_LIFT),
                "sha256": sha_file(FULL_A985_LIFT),
            },
        },
        "checks": checks,
        "derived": {
            "transported_manifest_rows": len(rows),
            "legacy_sector_rows_filled_from_full_match": filled_rows,
            "legacy_sector_rows_preserved_and_confirmed": preserved_rows,
            "unit_top_all_39_rows": len(top_rows),
            "block_dimension_histogram": {
                str(key): int(value)
                for key, value in sorted(Counter(dimensions.values()).items())
            },
            "tables": {
                "legacy_labeled_matrix_unit_manifest": rel(OUT_DIR / "legacy_labeled_matrix_unit_manifest.csv"),
                "legacy_sector_matrix_unit_profiles": rel(OUT_DIR / "legacy_sector_matrix_unit_profiles.csv"),
                "registered_support_legacy_transport": rel(OUT_DIR / "registered_support_legacy_transport.csv"),
            },
        },
        "next_highest_yield_item": (
            "Attach raw orbital COO coefficients to the all-39 legacy-labeled matrix-unit manifest, not only "
            "to the registered public-zero support subset."
        ),
        "all_checks_pass": all(checks.values()),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    manifest = {
        "schema": "d20.theorem.tiny_pointer_a985_legacy_matrix_unit_transport_manifest.source_drop",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(OUT_DIR / "manifest.json"),
            "report": rel(OUT_DIR / "report.json"),
            **report["derived"]["tables"],
        },
        "validation_tests": list(checks),
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = sha_json({k: v for k, v in manifest.items() if k != "manifest_sha256"})
    write_json(OUT_DIR / "report.json", report)
    write_json(OUT_DIR / "manifest.json", manifest)
    (OUT_DIR / "legacy_matrix_unit_transport_report.md").write_text(markdown_report(report), encoding="utf-8")
    update_theorem_index(report)
    return report


def verify_transport() -> dict[str, Any]:
    report = load_json(OUT_DIR / "report.json")
    manifest_rows = read_csv_rows(OUT_DIR / "legacy_labeled_matrix_unit_manifest.csv")
    profile_rows = read_csv_rows(OUT_DIR / "legacy_sector_matrix_unit_profiles.csv")
    support_rows = read_csv_rows(OUT_DIR / "registered_support_legacy_transport.csv")
    checks = {
        "report_status_certified": report.get("status") == STATUS,
        "report_checks_pass": report.get("all_checks_pass") is True,
        "manifest_has_1011_rows": len(manifest_rows) == 1011,
        "profiles_have_39_rows": len(profile_rows) == 39,
        "support_transport_has_7_rows": len(support_rows) == 7,
        "no_blank_legacy_sector": all(row["legacy_sector"] != "" for row in manifest_rows),
        "top_rows_have_all_39_legacy_sectors": len(
            {row["legacy_sector"] for row in manifest_rows if row["support_name"] == "unit_top_all_39"}
        )
        == 39,
    }
    return {
        "status": "D20_TINY_POINTER_A985_LEGACY_MATRIX_UNIT_TRANSPORT_VERIFIED"
        if all(checks.values())
        else "D20_TINY_POINTER_A985_LEGACY_MATRIX_UNIT_TRANSPORT_VERIFY_FAILED",
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if not args.verify_only:
        build_transport()
    verification = verify_transport()
    print(json.dumps(verification, indent=2, sort_keys=True))
    if not verification["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
