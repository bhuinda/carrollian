from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT_FOR_IMPORT = Path(__file__).resolve().parents[1]
if str(ROOT_FOR_IMPORT) not in sys.path:
    sys.path.insert(0, str(ROOT_FOR_IMPORT))

from src.a985_perennial_ids import (  # noqa: E402
    augment_a985_sector_rows,
    load_perennial_sector_maps,
    read_csv_rows,
)
from src.paths import D20_INVARIANTS, ROOT  # noqa: E402


THEOREM_ID = "tiny_pointer_a985_perennial_sector_report_coverage"
STATUS = "D20_TINY_POINTER_A985_PERENNIAL_SECTOR_REPORT_COVERAGE_CERTIFIED"
VERIFY_STATUS = "D20_TINY_POINTER_A985_PERENNIAL_SECTOR_REPORT_COVERAGE_VERIFIED"
VERIFY_FAILED_STATUS = "D20_TINY_POINTER_A985_PERENNIAL_SECTOR_REPORT_COVERAGE_VERIFY_FAILED"

OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
AUGMENTED_DIR = OUT_DIR / "augmented"
PERENNIAL_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_perennial_sector_fingerprints"

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


def write_csv_rows(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def csv_candidates() -> list[Path]:
    theorem_root = D20_INVARIANTS / "theorems"
    candidates: list[Path] = []
    for path in theorem_root.glob("tiny_pointer_a985*/*.csv"):
        if OUT_DIR in path.parents or PERENNIAL_DIR in path.parents:
            continue
        candidates.append(path)
    return sorted(candidates, key=lambda p: rel(p))


def destination_for(source: Path) -> Path:
    return AUGMENTED_DIR / source.relative_to(D20_INVARIANTS / "theorems")


def augment_csv(path: Path, maps: dict[str, dict[int | str, dict[str, Any]]]) -> dict[str, Any] | None:
    rows = read_csv_rows(path)
    if not rows:
        return None
    fieldnames = list(rows[0].keys())
    output_fields, augmented_rows, stats = augment_a985_sector_rows(rows, fieldnames, maps)
    if not stats["needs_augmentation"]:
        return None

    destination = destination_for(path)
    write_csv_rows(destination, output_fields, augmented_rows)
    return {
        "source_path": rel(path),
        "augmented_path": rel(destination),
        "row_count": len(rows),
        "added_columns": "|".join(stats["added_columns"]),
        "has_source_sector": stats["has_source_sector"],
        "has_raw_sector": stats["has_raw_sector"],
        "has_source_set_column": stats["has_source_set_column"],
        "has_raw_set_column": stats["has_raw_set_column"],
        "rows_with_direct_sector": stats["rows_with_direct_sector"],
        "rows_with_perennial_id": stats["rows_with_perennial_id"],
        "unresolved_direct_rows": stats["unresolved_direct_rows"],
        "sector_mismatch_count": stats["sector_mismatch_count"],
        "source_sha256": sha_file(path),
        "augmented_sha256": sha_file(destination),
    }


def copy_alias_table() -> None:
    source = PERENNIAL_DIR / "perennial_sector_fingerprints.csv"
    destination = OUT_DIR / "perennial_sector_alias_table.csv"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def build_theorem() -> dict[str, Any]:
    perennial_report = load_json(PERENNIAL_DIR / "report.json")
    maps = load_perennial_sector_maps()
    sample_fields, sample_rows, sample_stats = augment_a985_sector_rows(
        [{"source_sector": 0, "raw_sector": 32, "value": "sample"}],
        ["source_sector", "raw_sector", "value"],
        maps,
    )
    automatic_augmenter_selftest_passes = (
        "perennial_id" in sample_fields
        and "coordinate_fingerprint_id" in sample_fields
        and sample_stats["rows_with_direct_sector"] == 1
        and sample_stats["rows_with_perennial_id"] == 1
        and sample_stats["sector_mismatch_count"] == 0
        and sample_rows[0]["perennial_id"] == maps["by_source"][0]["perennial_id"]
        and sample_rows[0]["coordinate_fingerprint_id"] == maps["by_source"][0]["coordinate_fingerprint_id"]
    )
    if AUGMENTED_DIR.exists():
        shutil.rmtree(AUGMENTED_DIR)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    copy_alias_table()

    coverage_rows: list[dict[str, Any]] = []
    for path in csv_candidates():
        row = augment_csv(path, maps)
        if row is not None:
            coverage_rows.append(row)

    write_csv_rows(
        OUT_DIR / "perennial_sector_report_coverage.csv",
        [
            "source_path",
            "augmented_path",
            "row_count",
            "added_columns",
            "has_source_sector",
            "has_raw_sector",
            "has_source_set_column",
            "has_raw_set_column",
            "rows_with_direct_sector",
            "rows_with_perennial_id",
            "unresolved_direct_rows",
            "sector_mismatch_count",
            "source_sha256",
            "augmented_sha256",
        ],
        coverage_rows,
    )

    direct_tables = [row for row in coverage_rows if int(row["rows_with_direct_sector"]) > 0]
    total_rows = sum(int(row["row_count"]) for row in coverage_rows)
    direct_rows = sum(int(row["rows_with_direct_sector"]) for row in coverage_rows)
    resolved_rows = sum(int(row["rows_with_perennial_id"]) for row in coverage_rows)
    unresolved_rows = sum(int(row["unresolved_direct_rows"]) for row in coverage_rows)
    mismatch_count = sum(int(row["sector_mismatch_count"]) for row in coverage_rows)

    checks = {
        "perennial_fingerprints_certified": perennial_report.get("status")
        == "D20_TINY_POINTER_A985_PERENNIAL_SECTOR_FINGERPRINTS_CERTIFIED"
        and perennial_report.get("all_checks_pass") is True,
        "perennial_map_has_39_source_aliases": len(maps["by_source"]) == 39,
        "perennial_map_has_39_raw_aliases": len(maps["by_raw"]) == 39,
        "automatic_augmenter_selftest_passes": automatic_augmenter_selftest_passes,
        "sector_facing_tables_covered": len(coverage_rows) >= 30,
        "direct_sector_tables_covered": len(direct_tables) >= 20,
        "all_direct_sector_rows_resolved": direct_rows == resolved_rows and unresolved_rows == 0,
        "source_raw_sector_aliases_are_coherent": mismatch_count == 0,
        "coverage_table_emitted": (OUT_DIR / "perennial_sector_report_coverage.csv").exists(),
        "alias_table_emitted": (OUT_DIR / "perennial_sector_alias_table.csv").exists(),
    }
    report = {
        "schema": "d20.theorem.tiny_pointer_a985_perennial_sector_report_coverage",
        "status": STATUS,
        "object": "d20",
        "claim": (
            "Sector-facing A985 CSV report tables now have perennial-id-covered views emitted "
            "through the shared automatic A985 perennial-id augmenter. The augmented copies add "
            "perennial_id and coordinate_fingerprint_id for direct "
            "source/raw sector rows, and add perennial-id set columns for transported source, raw, "
            "and zero-sector support fields. Original witness tables remain unchanged."
        ),
        "boundary": (
            "This is a report-coverage overlay, not a recomputation of the underlying matrix units "
            "or sector characters. Older numeric columns are retained as aliases for traceability."
        ),
        "inputs": {
            "perennial_sector_fingerprints": {
                "path": rel(PERENNIAL_DIR / "report.json"),
                "sha256": sha_file(PERENNIAL_DIR / "report.json"),
            }
        },
        "checks": checks,
        "derived": {
            "covered_csv_tables": len(coverage_rows),
            "covered_direct_sector_tables": len(direct_tables),
            "covered_rows_total": total_rows,
            "direct_sector_rows": direct_rows,
            "direct_sector_rows_resolved_to_perennial_id": resolved_rows,
            "unresolved_direct_sector_rows": unresolved_rows,
            "sector_mismatch_count": mismatch_count,
            "automatic_augmenter": "src/a985_perennial_ids.py::augment_a985_sector_rows",
            "tables": {
                "coverage": rel(OUT_DIR / "perennial_sector_report_coverage.csv"),
                "alias_table": rel(OUT_DIR / "perennial_sector_alias_table.csv"),
                "augmented_root": rel(AUGMENTED_DIR),
            },
        },
        "next_highest_yield_item": (
            "For new sector-facing theorems, write CSV tables through the automatic A985 perennial-id "
            "augmenter so perennial_id appears without hand-maintained joins."
        ),
        "all_checks_pass": all(checks.values()),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    manifest = {
        "schema": "d20.theorem.tiny_pointer_a985_perennial_sector_report_coverage_manifest",
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
    (OUT_DIR / "perennial_sector_report_coverage.md").write_text(markdown_report(report), encoding="utf-8")
    update_theorem_index(report)
    return report


def markdown_report(report: dict[str, Any]) -> str:
    checks = "\n".join(f"- `{name}`: `{value}`" for name, value in report["checks"].items())
    derived = report["derived"]
    return (
        "# A985 perennial sector report coverage\n\n"
        f"Status: `{report['status']}`\n\n"
        f"{report['claim']}\n\n"
        f"Boundary: {report['boundary']}\n\n"
        f"Covered CSV tables: `{derived['covered_csv_tables']}`\n\n"
        f"Direct sector rows resolved: `{derived['direct_sector_rows_resolved_to_perennial_id']}`\n\n"
        "## Checks\n\n"
        f"{checks}\n\n"
        f"Next: {report['next_highest_yield_item']}\n"
    )


def update_theorem_index(report: dict[str, Any]) -> None:
    index_path = D20_INVARIANTS / "theorems" / "index.json"
    existing = load_json(index_path) if index_path.exists() else {"theorems": []}
    theorems = [item for item in existing.get("theorems", []) if item.get("id") != THEOREM_ID]
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


def verify_outputs() -> dict[str, Any]:
    report = load_json(OUT_DIR / "report.json")
    coverage = read_csv_rows(OUT_DIR / "perennial_sector_report_coverage.csv")
    alias_rows = read_csv_rows(OUT_DIR / "perennial_sector_alias_table.csv")
    direct_rows = sum(int(row["rows_with_direct_sector"]) for row in coverage)
    resolved_rows = sum(int(row["rows_with_perennial_id"]) for row in coverage)
    unresolved_rows = sum(int(row["unresolved_direct_rows"]) for row in coverage)
    mismatch_count = sum(int(row["sector_mismatch_count"]) for row in coverage)
    checks = {
        "report_status_certified": report.get("status") == STATUS,
        "report_checks_pass": report.get("all_checks_pass") is True,
        "coverage_rows_match_report": len(coverage) == report.get("derived", {}).get("covered_csv_tables"),
        "alias_table_has_39_rows": len(alias_rows) == 39,
        "all_direct_sector_rows_resolved": direct_rows == resolved_rows and unresolved_rows == 0,
        "no_source_raw_mismatches": mismatch_count == 0,
        "augmented_files_exist": all((ROOT / row["augmented_path"]).exists() for row in coverage),
        "augmented_files_hash_match": all(
            sha_file(ROOT / row["augmented_path"]) == row["augmented_sha256"] for row in coverage
        ),
        "report_checks_all_true": all(report.get("checks", {}).values()),
    }
    return {
        "status": VERIFY_STATUS if all(checks.values()) else VERIFY_FAILED_STATUS,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if not args.verify_only:
        build_theorem()
    verification = verify_outputs()
    print(json.dumps(verification, indent=2, sort_keys=True))
    if not verification["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

