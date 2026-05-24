from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT_FOR_IMPORT = Path(__file__).resolve().parents[1]
if str(ROOT_FOR_IMPORT) not in sys.path:
    sys.path.insert(0, str(ROOT_FOR_IMPORT))

from src.paths import D20_INVARIANTS, ROOT  # noqa: E402


STATUS = "D20_TINY_POINTER_A985_CANONICAL_LEGACY_MATRIX_UNITS_CERTIFIED"
THEOREM_ID = "tiny_pointer_a985_canonical_legacy_matrix_units"
OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FULL_MATCH_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_full_legacy_sector_match"
FULL_COO_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_full_matrix_unit_orbital_coo"
SUPPORT_MULT_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_support_restricted_multiplication_tables"


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


def load_dimension_map() -> dict[int, int]:
    rows = read_csv_rows(FULL_MATCH_DIR / "legacy_to_raw_sector_full_match.csv")
    return {int(row["legacy_sector"]): int(row["block_dimension"]) for row in rows}


def canonical_gauge_status(source: str) -> str:
    if source == "REGISTERED_SUPPORT_COO":
        return "REGISTERED_SUPPORT_CANONICAL_GAUGE"
    return "CONSTRUCTED_RAW_BLOCK_CANONICAL_GAUGE"


def build_canonical_tables() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    dimensions = load_dimension_map()
    manifest_rows = read_csv_rows(FULL_COO_DIR / "legacy_matrix_units_orbital_manifest.csv")
    coo_rows = read_csv_rows(FULL_COO_DIR / "legacy_matrix_units_orbital_coo.csv")
    sector_source_rows = read_csv_rows(FULL_COO_DIR / "sector_matrix_unit_source_summary.csv")
    product_summary_rows = read_csv_rows(SUPPORT_MULT_DIR / "support_restricted_table_summary.csv")
    top_product_summary = {
        row["support_name"]: row for row in product_summary_rows
    }["unit_top_all_39"]

    coo_counts: dict[int, int] = defaultdict(int)
    for row in coo_rows:
        coo_counts[int(row["unit_column"])] += 1

    canonical_rows: list[dict[str, Any]] = []
    sector_counts: dict[int, Counter[str]] = defaultdict(Counter)
    row_keys: set[tuple[int, int, int]] = set()
    missing_coo_units: list[int] = []
    nonzero_count_mismatches: list[int] = []
    source_by_sector = {int(row["legacy_sector"]): row["coefficient_source"] for row in sector_source_rows}

    for row in manifest_rows:
        unit_column = int(row["unit_column"])
        legacy_sector = int(row["legacy_sector"])
        raw_sector = int(row["raw_sector"])
        d = int(row["block_dimension"])
        i = int(row["i"])
        j = int(row["j"])
        source = row["coefficient_source"]
        is_diagonal = i == j
        key = (legacy_sector, i, j)
        row_keys.add(key)
        sector_counts[legacy_sector]["matrix_units"] += 1
        sector_counts[legacy_sector]["diagonal_units" if is_diagonal else "off_diagonal_units"] += 1
        sector_counts[legacy_sector][source] += 1
        if coo_counts[unit_column] == 0:
            missing_coo_units.append(unit_column)
        if coo_counts[unit_column] != int(row["nonzero_coefficients"]):
            nonzero_count_mismatches.append(unit_column)
        canonical_rows.append(
            {
                "unit_column": unit_column,
                "legacy_sector": legacy_sector,
                "raw_sector": raw_sector,
                "block_dimension": d,
                "i": i,
                "j": j,
                "is_off_diagonal": not is_diagonal,
                "legacy_matrix_unit_label": row["legacy_matrix_unit_label"],
                "raw_matrix_unit_label": row["raw_matrix_unit_label"],
                "coefficient_source": source,
                "canonical_gauge_status": canonical_gauge_status(source),
                "raw_orbital_coo_rows": coo_counts[unit_column],
                "nonzero_coefficients": int(row["nonzero_coefficients"]),
            }
        )

    sector_rows: list[dict[str, Any]] = []
    missing_local_units: list[dict[str, int]] = []
    for legacy_sector in sorted(dimensions):
        d = dimensions[legacy_sector]
        expected_keys = {(legacy_sector, i, j) for i in range(d) for j in range(d)}
        missing = sorted(expected_keys - row_keys)
        for _, i, j in missing:
            missing_local_units.append({"legacy_sector": legacy_sector, "i": i, "j": j})
        counts = sector_counts[legacy_sector]
        source = source_by_sector[legacy_sector]
        sector_rows.append(
            {
                "legacy_sector": legacy_sector,
                "block_dimension": d,
                "matrix_units": counts["matrix_units"],
                "expected_matrix_units": d * d,
                "diagonal_units": counts["diagonal_units"],
                "expected_diagonal_units": d,
                "off_diagonal_units": counts["off_diagonal_units"],
                "expected_off_diagonal_units": d * (d - 1),
                "coefficient_source": source,
                "canonical_gauge_status": canonical_gauge_status(source),
            }
        )

    derived = {
        "legacy_sector_count": len(dimensions),
        "matrix_unit_count": len(canonical_rows),
        "diagonal_matrix_unit_count": sum(row["diagonal_units"] for row in sector_rows),
        "off_diagonal_matrix_unit_count": sum(row["off_diagonal_units"] for row in sector_rows),
        "raw_orbital_coo_rows": len(coo_rows),
        "expected_nonzero_products": sum(dimension**3 for dimension in dimensions.values()),
        "top_support_nonzero_products": int(top_product_summary["nonzero_products"]),
        "top_support_zero_products": int(top_product_summary["zero_products"]),
        "top_support_symbolic_complete": top_product_summary["symbolic_table_complete"] == "True",
        "source_counts": dict(sorted(Counter(row["coefficient_source"] for row in canonical_rows).items())),
        "gauge_counts": dict(sorted(Counter(row["canonical_gauge_status"] for row in canonical_rows).items())),
        "missing_coo_units": missing_coo_units[:8],
        "nonzero_count_mismatches": nonzero_count_mismatches[:8],
        "missing_local_units": missing_local_units[:8],
    }
    return canonical_rows, sector_rows, derived


def write_outputs(canonical_rows: list[dict[str, Any]], sector_rows: list[dict[str, Any]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(
        OUT_DIR / "canonical_legacy_matrix_units_manifest.csv",
        [
            "unit_column",
            "legacy_sector",
            "raw_sector",
            "block_dimension",
            "i",
            "j",
            "is_off_diagonal",
            "legacy_matrix_unit_label",
            "raw_matrix_unit_label",
            "coefficient_source",
            "canonical_gauge_status",
            "raw_orbital_coo_rows",
            "nonzero_coefficients",
        ],
        canonical_rows,
    )
    write_csv_rows(
        OUT_DIR / "canonical_legacy_sector_matrix_unit_summary.csv",
        [
            "legacy_sector",
            "block_dimension",
            "matrix_units",
            "expected_matrix_units",
            "diagonal_units",
            "expected_diagonal_units",
            "off_diagonal_units",
            "expected_off_diagonal_units",
            "coefficient_source",
            "canonical_gauge_status",
        ],
        sector_rows,
    )


def build_theorem() -> dict[str, Any]:
    full_match = load_json(FULL_MATCH_DIR / "report.json")
    full_coo = load_json(FULL_COO_DIR / "report.json")
    support_mult = load_json(SUPPORT_MULT_DIR / "report.json")
    canonical_rows, sector_rows, derived = build_canonical_tables()
    checks = {
        "full_legacy_sector_match_certified": full_match.get("status")
        == "D20_TINY_POINTER_A985_FULL_LEGACY_SECTOR_MATCH_CERTIFIED"
        and full_match.get("all_checks_pass") is True,
        "full_matrix_unit_coo_certified": full_coo.get("status")
        == "D20_TINY_POINTER_A985_FULL_MATRIX_UNIT_ORBITAL_COO_CERTIFIED"
        and full_coo.get("all_checks_pass") is True,
        "support_restricted_multiplication_certified": support_mult.get("status")
        == "D20_TINY_POINTER_A985_SUPPORT_RESTRICTED_MULTIPLICATION_TABLES_CERTIFIED"
        and support_mult.get("all_checks_pass") is True,
        "all_39_legacy_sectors_present": derived["legacy_sector_count"] == 39,
        "all_985_matrix_units_present": derived["matrix_unit_count"] == 985,
        "diagonal_count_is_159": derived["diagonal_matrix_unit_count"] == 159,
        "off_diagonal_count_is_826": derived["off_diagonal_matrix_unit_count"] == 826,
        "all_sector_unit_grids_complete": all(
            row["matrix_units"] == row["expected_matrix_units"]
            and row["diagonal_units"] == row["expected_diagonal_units"]
            and row["off_diagonal_units"] == row["expected_off_diagonal_units"]
            for row in sector_rows
        ),
        "all_units_have_raw_orbital_coo": derived["missing_coo_units"] == [],
        "manifest_nonzero_counts_match_coo": derived["nonzero_count_mismatches"] == [],
        "no_missing_local_matrix_unit_labels": derived["missing_local_units"] == [],
        "top_support_symbolic_matrix_unit_table_complete": derived["top_support_symbolic_complete"],
        "top_support_nonzero_products_match_sum_d_cubed": derived["top_support_nonzero_products"]
        == derived["expected_nonzero_products"]
        == 7923,
    }
    write_outputs(canonical_rows, sector_rows)
    report = {
        "schema": "d20.theorem.tiny_pointer_a985_canonical_legacy_matrix_units.source_drop",
        "status": STATUS if all(checks.values()) else "D20_TINY_POINTER_A985_CANONICAL_LEGACY_MATRIX_UNITS_NEEDS_REVIEW",
        "object": "d20",
        "claim": (
            "The off-diagonal matrix units are constructed, not deferred. For every one of the 39 legacy "
            "sector labels, the repo now designates the certified raw-orbital block matrix units as the "
            "canonical legacy-sector matrix-unit gauge."
        ),
        "gauge_note": (
            "A later external legacy convention may still differ by sector-local GL_d conjugacy, but that "
            "is a comparison problem. It is not a construction blocker for u_legacy[s;i,j]."
        ),
        "inputs": {
            "full_legacy_sector_match": {
                "path": rel(FULL_MATCH_DIR / "report.json"),
                "sha256": sha_file(FULL_MATCH_DIR / "report.json"),
            },
            "full_matrix_unit_orbital_coo": {
                "path": rel(FULL_COO_DIR / "report.json"),
                "sha256": sha_file(FULL_COO_DIR / "report.json"),
            },
            "full_matrix_unit_manifest": {
                "path": rel(FULL_COO_DIR / "legacy_matrix_units_orbital_manifest.csv"),
                "sha256": sha_file(FULL_COO_DIR / "legacy_matrix_units_orbital_manifest.csv"),
            },
            "full_matrix_unit_coo": {
                "path": rel(FULL_COO_DIR / "legacy_matrix_units_orbital_coo.csv"),
                "sha256": sha_file(FULL_COO_DIR / "legacy_matrix_units_orbital_coo.csv"),
            },
            "support_restricted_multiplication": {
                "path": rel(SUPPORT_MULT_DIR / "report.json"),
                "sha256": sha_file(SUPPORT_MULT_DIR / "report.json"),
            },
        },
        "checks": checks,
        "derived": {
            **{key: value for key, value in derived.items() if not isinstance(value, list)},
            "tables": {
                "canonical_manifest": rel(OUT_DIR / "canonical_legacy_matrix_units_manifest.csv"),
                "sector_summary": rel(OUT_DIR / "canonical_legacy_sector_matrix_unit_summary.csv"),
            },
        },
        "next_highest_yield_item": (
            "Use the canonical legacy-sector matrix units as the default input for sector-local character, "
            "Fourier, or block trace calculations; only introduce GL_d comparison data if a separate "
            "legacy convention needs to be matched."
        ),
        "all_checks_pass": all(checks.values()),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    manifest = {
        "schema": "d20.theorem.tiny_pointer_a985_canonical_legacy_matrix_units_manifest.source_drop",
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
    (OUT_DIR / "canonical_legacy_matrix_units_report.md").write_text(markdown_report(report), encoding="utf-8")
    update_theorem_index(report)
    return report


def markdown_report(report: dict[str, Any]) -> str:
    checks = "\n".join(f"- `{key}`: `{value}`" for key, value in report["checks"].items())
    derived = report["derived"]
    return (
        "# Canonical Legacy Matrix Units\n\n"
        f"Status: `{report['status']}`\n\n"
        f"Matrix units: `{derived['matrix_unit_count']}`\n\n"
        f"Diagonal units: `{derived['diagonal_matrix_unit_count']}`\n\n"
        f"Off-diagonal units: `{derived['off_diagonal_matrix_unit_count']}`\n\n"
        "## Checks\n\n"
        f"{checks}\n\n"
        f"Gauge note: {report['gauge_note']}\n\n"
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


def verify_theorem() -> dict[str, Any]:
    report = load_json(OUT_DIR / "report.json")
    canonical_rows = read_csv_rows(OUT_DIR / "canonical_legacy_matrix_units_manifest.csv")
    sector_rows = read_csv_rows(OUT_DIR / "canonical_legacy_sector_matrix_unit_summary.csv")
    checks = {
        "report_status_certified": report.get("status") == STATUS,
        "report_checks_pass": report.get("all_checks_pass") is True,
        "canonical_manifest_has_985_rows": len(canonical_rows) == 985,
        "sector_summary_has_39_rows": len(sector_rows) == 39,
        "off_diagonal_manifest_count_is_826": sum(row["is_off_diagonal"] == "True" for row in canonical_rows) == 826,
        "sector_summaries_are_complete": all(
            int(row["matrix_units"]) == int(row["expected_matrix_units"])
            and int(row["diagonal_units"]) == int(row["expected_diagonal_units"])
            and int(row["off_diagonal_units"]) == int(row["expected_off_diagonal_units"])
            for row in sector_rows
        ),
    }
    return {
        "status": "D20_TINY_POINTER_A985_CANONICAL_LEGACY_MATRIX_UNITS_VERIFIED"
        if all(checks.values())
        else "D20_TINY_POINTER_A985_CANONICAL_LEGACY_MATRIX_UNITS_VERIFY_FAILED",
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if not args.verify_only:
        build_theorem()
    verification = verify_theorem()
    print(json.dumps(verification, indent=2, sort_keys=True))
    if not verification["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
