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

from src.a985_perennial_ids import (  # noqa: E402
    load_perennial_sector_maps_if_available,
    write_a985_sector_csv_rows_if_available,
)
from src.paths import D20_INVARIANTS, ROOT


STATUS = "D20_TINY_POINTER_A985_SECTOR_NORMALIZATION_OBLIGATIONS_CERTIFIED"
THEOREM_ID = "tiny_pointer_a985_sector_normalization_obligations"
OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FULL_MATCH_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_full_sector_match"
FULL_COO_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_full_matrix_unit_orbital_coo"
SUPPORT_MULT_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_support_restricted_multiplication_tables"
FULL_A985_LIFT = ROOT / "data" / "drinfeld" / "full_a985_lift.json"


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


def load_registered_anchor_sectors() -> set[int]:
    rows = read_csv_rows(FULL_COO_DIR / "sector_matrix_unit_source_summary.csv")
    return {
        int(row["source_sector"])
        for row in rows
        if row["coefficient_source"] == "REGISTERED_SUPPORT_COO"
    }


def load_source_profiles() -> dict[int, dict[str, Any]]:
    full = load_json(FULL_A985_LIFT)
    profiles = full["gluing_and_sector_profiles"]["sector_profiles"]
    return {int(profile["sector"]): profile for profile in profiles}


def normalization_status(source_sector: int, dimension: int, coefficient_source: str, registered: set[int]) -> tuple[str, str, int]:
    if dimension == 1:
        return ("CANONICAL_DIMENSION_ONE", "central idempotent is the only matrix unit", 0)
    if source_sector in registered and coefficient_source == "REGISTERED_SUPPORT_COO":
        return ("REGISTERED_SUPPORT_ANCHORED", "promoted registered support matrix-unit source fixes this basis", 0)
    return ("OPEN_GL_BLOCK_NORMALIZATION", "no source-sector off-diagonal matrix-unit basis is present in the certified lift", dimension * dimension - 1)


def build_obligations() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    registered = load_registered_anchor_sectors()
    profiles = load_source_profiles()
    sector_rows = read_csv_rows(FULL_COO_DIR / "sector_matrix_unit_source_summary.csv")
    product_summary = {
        row["support_name"]: row
        for row in read_csv_rows(SUPPORT_MULT_DIR / "support_restricted_table_summary.csv")
    }
    top_product_count = int(product_summary["unit_top_all_39"]["nonzero_products"])

    obligations: list[dict[str, Any]] = []
    term_rows: list[dict[str, Any]] = []
    for row in sector_rows:
        source_sector = int(row["source_sector"])
        raw_sector = int(row["raw_sector"])
        dimension = int(row["block_dimension"])
        source = row["coefficient_source"]
        status, anchor, projective_dim = normalization_status(source_sector, dimension, source, registered)
        template_terms = dimension**4 if status == "OPEN_GL_BLOCK_NORMALIZATION" else 0
        profile = profiles[source_sector]
        obligations.append(
            {
                "source_sector": source_sector,
                "raw_sector": raw_sector,
                "block_dimension": dimension,
                "matrix_unit_count": int(row["matrix_unit_count"]),
                "expected_matrix_unit_count": dimension * dimension,
                "matrix_unit_product_count": dimension**3,
                "coefficient_source": source,
                "normalization_status": status,
                "normalization_anchor": anchor,
                "remaining_projective_gauge_dimension": projective_dim,
                "change_of_basis_template_terms": template_terms,
                "change_of_basis_formula": "v_s[i,j] = sum_{a,b} g_s[a,i] * ginv_s[j,b] * u_s[a,b]",
                "identity_fingerprint": json.dumps(profile["identity_coefficients_signed"], separators=(",", ":")),
                "matrix_unit_block_sha256": row["matrix_unit_block_sha256"],
            }
        )
        if status != "OPEN_GL_BLOCK_NORMALIZATION":
            continue
        for i in range(dimension):
            for j in range(dimension):
                for a in range(dimension):
                    for b in range(dimension):
                        term_rows.append(
                            {
                                "source_sector": source_sector,
                                "raw_sector": raw_sector,
                                "block_dimension": dimension,
                                "target_i": i,
                                "target_j": j,
                                "source_a": a,
                                "source_b": b,
                                "coefficient_symbol": f"g_{source_sector}[{a},{i}]*ginv_{source_sector}[{j},{b}]",
                                "source_matrix_unit_label": f"u_sector[{source_sector};{a},{b}]",
                                "target_matrix_unit_label": f"v_sector[{source_sector};{i},{j}]",
                            }
                        )

    status_counts = Counter(row["normalization_status"] for row in obligations)
    source_counts = Counter(row["coefficient_source"] for row in obligations)
    summary = [
        {
            "summary_key": "sector_count",
            "summary_value": len(obligations),
            "detail": "all source sectors",
        },
        {
            "summary_key": "canonical_dimension_one_sectors",
            "summary_value": status_counts["CANONICAL_DIMENSION_ONE"],
            "detail": "dimension-one blocks have no matrix-unit basis ambiguity",
        },
        {
            "summary_key": "registered_support_anchored_sectors",
            "summary_value": status_counts["REGISTERED_SUPPORT_ANCHORED"],
            "detail": "nontrivial blocks fixed by promoted registered support COO",
        },
        {
            "summary_key": "open_gl_block_normalization_sectors",
            "summary_value": status_counts["OPEN_GL_BLOCK_NORMALIZATION"],
            "detail": "blocks requiring an external source-sector matrix-unit basis or normalization convention",
        },
        {
            "summary_key": "remaining_projective_gauge_dimension",
            "summary_value": sum(int(row["remaining_projective_gauge_dimension"]) for row in obligations),
            "detail": "sum of d^2 - 1 over open sectors",
        },
        {
            "summary_key": "change_of_basis_template_terms",
            "summary_value": len(term_rows),
            "detail": "expanded symbolic terms for all open sectors",
        },
        {
            "summary_key": "top_support_nonzero_matrix_unit_products",
            "summary_value": top_product_count,
            "detail": "sum of d^3 over all sectors from support-restricted multiplication",
        },
        {
            "summary_key": "registered_support_source_sectors",
            "summary_value": source_counts["REGISTERED_SUPPORT_COO"],
            "detail": "sectors whose current matrix-unit COO came from registered support source",
        },
    ]
    return obligations, term_rows, summary


def source_lift_has_matrix_unit_basis() -> bool:
    text = FULL_A985_LIFT.read_text(encoding="utf-8").lower()
    return "matrix_unit" in text or "matrix-unit" in text


def write_outputs(
    obligations: list[dict[str, Any]],
    terms: list[dict[str, Any]],
    summary: list[dict[str, Any]],
    perennial_maps: dict[str, dict[int | str, dict[str, Any]]] | None,
) -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    obligation_stats = write_a985_sector_csv_rows_if_available(
        OUT_DIR / "sector_local_normalization_obligations.csv",
        [
            "source_sector",
            "raw_sector",
            "block_dimension",
            "matrix_unit_count",
            "expected_matrix_unit_count",
            "matrix_unit_product_count",
            "coefficient_source",
            "normalization_status",
            "normalization_anchor",
            "remaining_projective_gauge_dimension",
            "change_of_basis_template_terms",
            "change_of_basis_formula",
            "identity_fingerprint",
            "matrix_unit_block_sha256",
        ],
        obligations,
        perennial_maps,
    )
    term_stats = write_a985_sector_csv_rows_if_available(
        OUT_DIR / "sector_local_change_of_basis_terms.csv",
        [
            "source_sector",
            "raw_sector",
            "block_dimension",
            "target_i",
            "target_j",
            "source_a",
            "source_b",
            "coefficient_symbol",
            "source_matrix_unit_label",
            "target_matrix_unit_label",
        ],
        terms,
        perennial_maps,
    )
    write_csv_rows(
        OUT_DIR / "sector_local_normalization_summary.csv",
        ["summary_key", "summary_value", "detail"],
        summary,
    )
    return {"obligations": obligation_stats, "terms": term_stats}


def markdown_report(report: dict[str, Any]) -> str:
    checks = "\n".join(f"- `{key}`: `{value}`" for key, value in report["checks"].items())
    derived = report["derived"]
    return (
        "# Sector-Local Matrix-Unit Normalization Obligations\n\n"
        f"Status: `{report['status']}`\n\n"
        f"Open sectors: `{derived['open_sector_count']}`\n\n"
        f"Remaining projective gauge dimension: `{derived['remaining_projective_gauge_dimension']}`\n\n"
        f"Change-of-basis template terms: `{derived['change_of_basis_template_terms']}`\n\n"
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


def build_normalization_obligations() -> dict[str, Any]:
    full_match_report = load_json(FULL_MATCH_DIR / "report.json")
    full_coo_report = load_json(FULL_COO_DIR / "report.json")
    support_mult_report = load_json(SUPPORT_MULT_DIR / "report.json")
    perennial_maps = load_perennial_sector_maps_if_available()
    obligations, terms, summary = build_obligations()
    perennial_stats = write_outputs(obligations, terms, summary, perennial_maps)
    support_summary_rows = read_csv_rows(SUPPORT_MULT_DIR / "support_restricted_table_summary.csv")
    top_support_products = next(
        int(row["nonzero_products"])
        for row in support_summary_rows
        if row["support_name"] == "unit_top_all_39"
    )

    status_counts = Counter(row["normalization_status"] for row in obligations)
    source_counts = Counter(row["coefficient_source"] for row in obligations)
    matrix_units_total = sum(int(row["matrix_unit_count"]) for row in obligations)
    product_total = sum(int(row["matrix_unit_product_count"]) for row in obligations)
    gauge_total = sum(int(row["remaining_projective_gauge_dimension"]) for row in obligations)
    template_total = sum(int(row["change_of_basis_template_terms"]) for row in obligations)
    checks = {
        "full_source_sector_match_certified": full_match_report.get("status")
        == "D20_TINY_POINTER_A985_FULL_SECTOR_MATCH_CERTIFIED"
        and full_match_report.get("all_checks_pass") is True,
        "full_matrix_unit_coo_certified": full_coo_report.get("status")
        == "D20_TINY_POINTER_A985_FULL_MATRIX_UNIT_ORBITAL_COO_CERTIFIED"
        and full_coo_report.get("all_checks_pass") is True,
        "support_restricted_multiplication_certified": support_mult_report.get("status")
        == "D20_TINY_POINTER_A985_SUPPORT_RESTRICTED_MULTIPLICATION_TABLES_CERTIFIED"
        and support_mult_report.get("all_checks_pass") is True,
        "source_lift_has_no_matrix_unit_basis": not source_lift_has_matrix_unit_basis(),
        "obligation_rows_cover_39_sectors": len(obligations) == 39,
        "matrix_unit_counts_sum_to_985": matrix_units_total == 985,
        "matrix_unit_products_sum_to_top_support_products": product_total == top_support_products,
        "dimension_one_fixed_sector_count_is_7": status_counts["CANONICAL_DIMENSION_ONE"] == 7,
        "registered_support_anchored_nontrivial_sector_count_is_2": status_counts["REGISTERED_SUPPORT_ANCHORED"] == 2,
        "open_sector_count_is_30": status_counts["OPEN_GL_BLOCK_NORMALIZATION"] == 30,
        "registered_source_sector_count_is_4": source_counts["REGISTERED_SUPPORT_COO"] == 4,
        "change_of_basis_terms_match_sector_templates": len(terms) == template_total,
        "remaining_projective_gauge_dimension_positive": gauge_total > 0,
        "perennial_join_key_emitted_when_available": perennial_maps is None
        or (
            perennial_stats["obligations"]["rows_with_perennial_id"]
            == perennial_stats["obligations"]["rows_with_direct_sector"]
            == len(obligations)
            and perennial_stats["terms"]["rows_with_perennial_id"]
            == perennial_stats["terms"]["rows_with_direct_sector"]
            == len(terms)
            and perennial_stats["obligations"]["sector_mismatch_count"] == 0
            and perennial_stats["terms"]["sector_mismatch_count"] == 0
        ),
    }
    report = {
        "schema": "d20.theorem.tiny_pointer_a985_sector_normalization_obligations.source_drop",
        "status": STATUS if all(checks.values()) else "D20_TINY_POINTER_A985_SECTOR_NORMALIZATION_OBLIGATIONS_NEEDS_REVIEW",
        "object": "d20",
        "claim": (
            "The all-39 source-sector-labeled matrix units are certified as algebraic matrix-unit systems, "
            "but the certified source lift does not contain an off-diagonal matrix-unit basis. "
            "The remaining sector-local normalization is therefore exactly the listed GL_d/scalar "
            "change-of-basis obligation for the open primitive blocks."
        ),
        "inputs": {
            "full_source_sector_match": {
                "path": rel(FULL_MATCH_DIR / "report.json"),
                "sha256": sha_file(FULL_MATCH_DIR / "report.json"),
            },
            "full_matrix_unit_orbital_coo": {
                "path": rel(FULL_COO_DIR / "report.json"),
                "sha256": sha_file(FULL_COO_DIR / "report.json"),
            },
            "support_restricted_multiplication": {
                "path": rel(SUPPORT_MULT_DIR / "report.json"),
                "sha256": sha_file(SUPPORT_MULT_DIR / "report.json"),
            },
            "registered_support_sector_source": {
                "path": rel(FULL_COO_DIR / "sector_matrix_unit_source_summary.csv"),
                "sha256": sha_file(FULL_COO_DIR / "sector_matrix_unit_source_summary.csv"),
            },
            "full_a985_lift": {
                "path": rel(FULL_A985_LIFT),
                "sha256": sha_file(FULL_A985_LIFT),
            },
        },
        "checks": checks,
        "derived": {
            "sector_count": len(obligations),
            "matrix_unit_count": matrix_units_total,
            "top_support_matrix_unit_product_count": product_total,
            "dimension_one_fixed_sector_count": status_counts["CANONICAL_DIMENSION_ONE"],
            "registered_support_anchored_sector_count": status_counts["REGISTERED_SUPPORT_ANCHORED"],
            "open_sector_count": status_counts["OPEN_GL_BLOCK_NORMALIZATION"],
            "registered_support_source_sector_count": source_counts["REGISTERED_SUPPORT_COO"],
            "remaining_projective_gauge_dimension": gauge_total,
            "change_of_basis_template_terms": len(terms),
            "perennial_join_key": {
                "map_available": perennial_maps is not None,
                "obligation_rows_resolved": int(perennial_stats["obligations"]["rows_with_perennial_id"]),
                "term_rows_resolved": int(perennial_stats["terms"]["rows_with_perennial_id"]),
            },
            "tables": {
                "obligations": rel(OUT_DIR / "sector_local_normalization_obligations.csv"),
                "change_of_basis_terms": rel(OUT_DIR / "sector_local_change_of_basis_terms.csv"),
                "summary": rel(OUT_DIR / "sector_local_normalization_summary.csv"),
            },
        },
        "next_highest_yield_item": (
            "Supply or derive a genuine source-sector off-diagonal matrix-unit basis for one open sector, "
            "then solve its GL_d/scalar normalization equation against the raw-orbital matrix units."
        ),
        "all_checks_pass": all(checks.values()),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    manifest = {
        "schema": "d20.theorem.tiny_pointer_a985_sector_normalization_obligations_manifest.source_drop",
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
    (OUT_DIR / "sector_local_normalization_obligations_report.md").write_text(markdown_report(report), encoding="utf-8")
    update_theorem_index(report)
    return report


def verify_normalization_obligations() -> dict[str, Any]:
    report = load_json(OUT_DIR / "report.json")
    obligations = read_csv_rows(OUT_DIR / "sector_local_normalization_obligations.csv")
    terms = read_csv_rows(OUT_DIR / "sector_local_change_of_basis_terms.csv")
    summary = read_csv_rows(OUT_DIR / "sector_local_normalization_summary.csv")
    status_counts = Counter(row["normalization_status"] for row in obligations)
    template_total = sum(int(row["change_of_basis_template_terms"]) for row in obligations)
    perennial_available = bool(report.get("derived", {}).get("perennial_join_key", {}).get("map_available"))
    checks = {
        "report_status_certified": report.get("status") == STATUS,
        "report_checks_pass": report.get("all_checks_pass") is True,
        "obligation_rows_cover_39_sectors": len(obligations) == 39,
        "summary_has_8_rows": len(summary) == 8,
        "dimension_one_fixed_sector_count_is_7": status_counts["CANONICAL_DIMENSION_ONE"] == 7,
        "registered_support_anchored_sector_count_is_2": status_counts["REGISTERED_SUPPORT_ANCHORED"] == 2,
        "open_sector_count_is_30": status_counts["OPEN_GL_BLOCK_NORMALIZATION"] == 30,
        "term_rows_match_report": len(terms) == report.get("derived", {}).get("change_of_basis_template_terms"),
        "term_rows_match_obligation_templates": len(terms) == template_total,
        "perennial_join_key_present_when_available": not perennial_available
        or (
            all(row.get("perennial_id", "").startswith("a985pf.") for row in obligations)
            and all(row.get("coordinate_fingerprint_id", "").startswith("a985coord.") for row in obligations)
            and all(row.get("perennial_id", "").startswith("a985pf.") for row in terms)
            and all(row.get("coordinate_fingerprint_id", "").startswith("a985coord.") for row in terms)
        ),
    }
    return {
        "status": "D20_TINY_POINTER_A985_SECTOR_NORMALIZATION_OBLIGATIONS_VERIFIED"
        if all(checks.values())
        else "D20_TINY_POINTER_A985_SECTOR_NORMALIZATION_OBLIGATIONS_VERIFY_FAILED",
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if not args.verify_only:
        build_normalization_obligations()
    verification = verify_normalization_obligations()
    print(json.dumps(verification, indent=2, sort_keys=True))
    if not verification["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

