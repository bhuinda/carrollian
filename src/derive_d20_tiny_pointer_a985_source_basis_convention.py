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
from src.paths import D20_INVARIANTS, ROOT  # noqa: E402


FIELD_PRIME = 1_000_003
THEOREM_ID = "tiny_pointer_a985_source_basis_convention"
STATUS = "D20_TINY_POINTER_A985_SOURCE_BASIS_CONVENTION_CERTIFIED"
VERIFY_STATUS = "D20_TINY_POINTER_A985_SOURCE_BASIS_CONVENTION_VERIFIED"
VERIFY_FAILED_STATUS = "D20_TINY_POINTER_A985_SOURCE_BASIS_CONVENTION_VERIFY_FAILED"

OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
FULL_COO_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_full_matrix_unit_orbital_coo"
NORMALIZATION_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_sector_normalization_obligations"
AMBIGUITY_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_gl_d_ambiguity_mechanism"
FOLD_FRAME_DIR = (
    D20_INVARIANTS / "theorems" / "tiny_pointer_a985_burning_ship_fold_frame_normalization_anchors"
)


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


def convention_status(normalization_status: str, dimension: int) -> tuple[str, str, str]:
    if dimension == 1:
        return (
            "INTRINSIC_CANONICAL_DIMENSION_ONE",
            "central idempotent is the single matrix unit",
            "no basis convention required",
        )
    if normalization_status == "REGISTERED_SUPPORT_ANCHORED":
        return (
            "EXTERNAL_REGISTERED_SUPPORT_CONVENTION",
            "promoted registered support rows fix the stored basis",
            "identity transform relative to registered support basis",
        )
    return (
        "REPO_STORED_BASIS_CONVENTION",
        "deterministic full_matrix_unit_orbital_coo stored basis is accepted as the repo convention",
        "identity transform relative to stored source-sector basis",
    )


def identity_gl_rows(source_sector: int, raw_sector: int, dimension: int, convention: str) -> list[dict[str, Any]]:
    if dimension <= 1:
        return []
    rows: list[dict[str, Any]] = []
    for i in range(dimension):
        for j in range(dimension):
            rows.append(
                {
                    "source_sector": source_sector,
                    "raw_sector": raw_sector,
                    "block_dimension": dimension,
                    "convention_status": convention,
                    "variable": f"g[{i},{j}]",
                    "value_mod_1000003": 1 if i == j else 0,
                }
            )
    for i in range(dimension):
        for j in range(dimension):
            rows.append(
                {
                    "source_sector": source_sector,
                    "raw_sector": raw_sector,
                    "block_dimension": dimension,
                    "convention_status": convention,
                    "variable": f"ginv[{i},{j}]",
                    "value_mod_1000003": 1 if i == j else 0,
                }
            )
    rows.append(
        {
            "source_sector": source_sector,
            "raw_sector": raw_sector,
            "block_dimension": dimension,
            "convention_status": convention,
            "variable": "det_g",
            "value_mod_1000003": 1,
        }
    )
    return rows


def build_convention_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    ambiguity_rows = {
        int(row["source_sector"]): row
        for row in read_csv_rows(AMBIGUITY_DIR / "gl_d_ambiguity_mechanism_by_sector.csv")
    }
    source_summary = {
        int(row["source_sector"]): row
        for row in read_csv_rows(FULL_COO_DIR / "sector_matrix_unit_source_summary.csv")
    }
    rows: list[dict[str, Any]] = []
    gl_rows: list[dict[str, Any]] = []
    for source_sector in sorted(ambiguity_rows):
        ambiguity = ambiguity_rows[source_sector]
        source = source_summary[source_sector]
        raw_sector = int(ambiguity["raw_sector"])
        dimension = int(ambiguity["block_dimension"])
        status, anchor, rule = convention_status(ambiguity["normalization_status"], dimension)
        mathematical_dim = int(ambiguity["intrinsic_projective_gauge_dimension"])
        prior_residual_dim = int(ambiguity["residual_unanchored_projective_gauge_dimension"])
        convention_residual_dim = 0
        rows.append(
            {
                "source_sector": source_sector,
                "raw_sector": raw_sector,
                "block_dimension": dimension,
                "matrix_unit_count": int(source["matrix_unit_count"]),
                "coefficient_source": source["coefficient_source"],
                "previous_normalization_status": ambiguity["normalization_status"],
                "convention_status": status,
                "convention_anchor": anchor,
                "convention_rule": rule,
                "identity_gl_transform": dimension > 1,
                "mathematical_ambiguity_group": ambiguity["intrinsic_ambiguity_group"],
                "mathematical_projective_gauge_dimension": mathematical_dim,
                "prior_unanchored_projective_gauge_dimension": prior_residual_dim,
                "repo_convention_residual_gauge_dimension": convention_residual_dim,
                "mathematical_ambiguity_retained": mathematical_dim > 0,
                "diagonal_sum_equals_central_page": source["diagonal_sum_equals_central_page"],
                "direct_matrix_unit_product_failures": int(source["direct_matrix_unit_product_failures"]),
                "matrix_unit_block_sha256": source["matrix_unit_block_sha256"],
            }
        )
        gl_rows.extend(identity_gl_rows(source_sector, raw_sector, dimension, status))
    return rows, gl_rows


def convention_contract() -> dict[str, Any]:
    return {
        "schema": "d20.tiny_pointer_a985.source_basis_convention.contract@1",
        "field_prime": FIELD_PRIME,
        "convention": (
            "The repository canonical source-sector matrix-unit basis is the stored basis emitted by "
            "tiny_pointer_a985_full_matrix_unit_orbital_coo. For comparison, the convention transform "
            "is g_s = I in every nontrivial block."
        ),
        "meaning": (
            "This closes the engineering normalization ledger by choosing coordinates. It does not "
            "claim the mathematical PGL_d symmetry is absent."
        ),
        "external_candidate_rule": (
            "Given an external candidate basis v_s, solve v_s[i,j] = sum g_s[a,i] ginv_s[j,b] u_s[a,b]. "
            "If the solve verifies, transport the candidate into the repo convention by the inverse basis change."
        ),
        "static_frame_anchor": (
            "The Burning Ship fold-frame anchors fix the static Z/2 x Z/4^2 quotient convention, not the full "
            "rank-one idempotent flag in every Wedderburn block."
        ),
    }


def build_theorem() -> dict[str, Any]:
    full_coo_report = load_json(FULL_COO_DIR / "report.json")
    normalization_report = load_json(NORMALIZATION_DIR / "report.json")
    ambiguity_report = load_json(AMBIGUITY_DIR / "report.json")
    fold_frame_report = load_json(FOLD_FRAME_DIR / "report.json")
    perennial_maps = load_perennial_sector_maps_if_available()
    convention_rows, gl_rows = build_convention_rows()
    contract = convention_contract()
    status_counts = Counter(row["convention_status"] for row in convention_rows)
    matrix_unit_count = sum(int(row["matrix_unit_count"]) for row in convention_rows)
    mathematical_dim = sum(int(row["mathematical_projective_gauge_dimension"]) for row in convention_rows)
    prior_residual_dim = sum(int(row["prior_unanchored_projective_gauge_dimension"]) for row in convention_rows)
    convention_residual_dim = sum(int(row["repo_convention_residual_gauge_dimension"]) for row in convention_rows)
    expected_gl_rows = sum(
        2 * int(row["block_dimension"]) * int(row["block_dimension"]) + 1
        for row in convention_rows
        if int(row["block_dimension"]) > 1
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    convention_stats = write_a985_sector_csv_rows_if_available(
        OUT_DIR / "source_matrix_unit_basis_convention_by_sector.csv",
        [
            "source_sector",
            "raw_sector",
            "block_dimension",
            "matrix_unit_count",
            "coefficient_source",
            "previous_normalization_status",
            "convention_status",
            "convention_anchor",
            "convention_rule",
            "identity_gl_transform",
            "mathematical_ambiguity_group",
            "mathematical_projective_gauge_dimension",
            "prior_unanchored_projective_gauge_dimension",
            "repo_convention_residual_gauge_dimension",
            "mathematical_ambiguity_retained",
            "diagonal_sum_equals_central_page",
            "direct_matrix_unit_product_failures",
            "matrix_unit_block_sha256",
        ],
        convention_rows,
        perennial_maps,
    )
    gl_stats = write_a985_sector_csv_rows_if_available(
        OUT_DIR / "source_matrix_unit_identity_gl_convention.csv",
        [
            "source_sector",
            "raw_sector",
            "block_dimension",
            "convention_status",
            "variable",
            "value_mod_1000003",
        ],
        gl_rows,
        perennial_maps,
    )
    write_json(OUT_DIR / "source_basis_convention_contract.json", contract)

    checks = {
        "full_matrix_unit_coo_certified": full_coo_report.get("status")
        == "D20_TINY_POINTER_A985_FULL_MATRIX_UNIT_ORBITAL_COO_CERTIFIED"
        and full_coo_report.get("all_checks_pass") is True,
        "normalization_obligations_certified": normalization_report.get("status")
        == "D20_TINY_POINTER_A985_SECTOR_NORMALIZATION_OBLIGATIONS_CERTIFIED"
        and normalization_report.get("all_checks_pass") is True,
        "gl_d_ambiguity_mechanism_certified": ambiguity_report.get("status")
        == "D20_TINY_POINTER_A985_GL_D_AMBIGUITY_MECHANISM_CERTIFIED"
        and ambiguity_report.get("all_checks_pass") is True,
        "burning_ship_fold_frame_anchors_certified": fold_frame_report.get("status")
        == "D20_TINY_POINTER_A985_BURNING_SHIP_FOLD_FRAME_NORMALIZATION_ANCHORS_CERTIFIED"
        and fold_frame_report.get("all_checks_pass") is True,
        "convention_rows_cover_39_sectors": len(convention_rows) == 39,
        "matrix_unit_count_is_985": matrix_unit_count == 985,
        "convention_status_counts_match_expected": dict(status_counts)
        == {
            "EXTERNAL_REGISTERED_SUPPORT_CONVENTION": 2,
            "INTRINSIC_CANONICAL_DIMENSION_ONE": 7,
            "REPO_STORED_BASIS_CONVENTION": 30,
        },
        "identity_gl_rows_match_nontrivial_blocks": len(gl_rows) == expected_gl_rows == 1988,
        "mathematical_pgl_dimension_retained_is_946": mathematical_dim == 946,
        "prior_unanchored_pgl_dimension_was_940": prior_residual_dim == 940,
        "repo_convention_residual_gauge_dimension_is_zero": convention_residual_dim == 0,
        "all_direct_products_pass": all(
            int(row["direct_matrix_unit_product_failures"]) == 0 for row in convention_rows
        ),
        "all_diagonal_sums_are_central_pages": all(
            row["diagonal_sum_equals_central_page"] == "True" for row in convention_rows
        ),
        "contract_emitted": (OUT_DIR / "source_basis_convention_contract.json").exists(),
        "perennial_join_key_emitted_when_available": perennial_maps is None
        or (
            convention_stats["rows_with_perennial_id"]
            == convention_stats["rows_with_direct_sector"]
            == len(convention_rows)
            and gl_stats["rows_with_perennial_id"]
            == gl_stats["rows_with_direct_sector"]
            == len(gl_rows)
            and convention_stats["sector_mismatch_count"] == 0
            and gl_stats["sector_mismatch_count"] == 0
        ),
    }
    report = {
        "schema": "d20.theorem.tiny_pointer_a985_source_basis_convention.source_drop",
        "status": STATUS,
        "object": "d20",
        "field_prime": FIELD_PRIME,
        "claim": (
            "The repository now fixes a source-sector matrix-unit basis convention: the stored "
            "raw-orbital matrix units from full_matrix_unit_orbital_coo are the comparison basis, "
            "so the convention transform is g_s = I in every nontrivial block."
        ),
        "boundary": (
            "This is a coordinate convention. The mathematical PGL_d basis-change symmetry remains "
            "recorded by the ambiguity mechanism theorem."
        ),
        "inputs": {
            "full_matrix_unit_orbital_coo": {
                "path": rel(FULL_COO_DIR / "report.json"),
                "sha256": sha_file(FULL_COO_DIR / "report.json"),
            },
            "sector_normalization_obligations": {
                "path": rel(NORMALIZATION_DIR / "report.json"),
                "sha256": sha_file(NORMALIZATION_DIR / "report.json"),
            },
            "gl_d_ambiguity_mechanism": {
                "path": rel(AMBIGUITY_DIR / "report.json"),
                "sha256": sha_file(AMBIGUITY_DIR / "report.json"),
            },
            "burning_ship_fold_frame_anchors": {
                "path": rel(FOLD_FRAME_DIR / "report.json"),
                "sha256": sha_file(FOLD_FRAME_DIR / "report.json"),
            },
        },
        "checks": checks,
        "derived": {
            "sector_count": len(convention_rows),
            "matrix_unit_count": matrix_unit_count,
            "convention_status_counts": dict(status_counts),
            "identity_gl_rows": len(gl_rows),
            "mathematical_pgl_dimension_retained": mathematical_dim,
            "prior_unanchored_pgl_dimension": prior_residual_dim,
            "repo_convention_residual_gauge_dimension": convention_residual_dim,
            "matrix_units_sha256": full_coo_report.get("derived", {}).get("matrix_units_sha256"),
            "perennial_join_key": {
                "map_available": perennial_maps is not None,
                "basis_rows_resolved": int(convention_stats["rows_with_perennial_id"]),
                "identity_gl_rows_resolved": int(gl_stats["rows_with_perennial_id"]),
            },
            "tables": {
                "basis_convention_by_sector": rel(
                    OUT_DIR / "source_matrix_unit_basis_convention_by_sector.csv"
                ),
                "identity_gl_convention": rel(OUT_DIR / "source_matrix_unit_identity_gl_convention.csv"),
                "contract": rel(OUT_DIR / "source_basis_convention_contract.json"),
            },
        },
        "next_highest_yield_item": (
            "Use this convention as the target coordinate system for any future external sector basis "
            "or rank-one idempotent flag."
        ),
        "all_checks_pass": all(checks.values()),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    manifest = {
        "schema": "d20.theorem.tiny_pointer_a985_source_basis_convention_manifest.source_drop",
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
    (OUT_DIR / "source_basis_convention_report.md").write_text(markdown_report(report), encoding="utf-8")
    update_theorem_index(report)
    return report


def markdown_report(report: dict[str, Any]) -> str:
    checks = "\n".join(f"- `{name}`: `{value}`" for name, value in report["checks"].items())
    derived = report["derived"]
    return (
        "# Source-sector basis convention\n\n"
        f"Status: `{report['status']}`\n\n"
        f"{report['claim']}\n\n"
        f"Boundary: {report['boundary']}\n\n"
        f"Convention residual gauge dimension: `{derived['repo_convention_residual_gauge_dimension']}`\n\n"
        f"Mathematical PGL dimension retained: `{derived['mathematical_pgl_dimension_retained']}`\n\n"
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
    rows = read_csv_rows(OUT_DIR / "source_matrix_unit_basis_convention_by_sector.csv")
    gl_rows = read_csv_rows(OUT_DIR / "source_matrix_unit_identity_gl_convention.csv")
    contract = load_json(OUT_DIR / "source_basis_convention_contract.json")
    status_counts = Counter(row["convention_status"] for row in rows)
    perennial_available = bool(report.get("derived", {}).get("perennial_join_key", {}).get("map_available"))
    checks = {
        "report_status_certified": report.get("status") == STATUS,
        "report_checks_pass": report.get("all_checks_pass") is True,
        "basis_convention_rows_cover_39": len(rows) == 39,
        "matrix_unit_count_is_985": sum(int(row["matrix_unit_count"]) for row in rows) == 985,
        "convention_status_counts_match_expected": dict(status_counts)
        == {
            "EXTERNAL_REGISTERED_SUPPORT_CONVENTION": 2,
            "INTRINSIC_CANONICAL_DIMENSION_ONE": 7,
            "REPO_STORED_BASIS_CONVENTION": 30,
        },
        "identity_gl_rows_count_is_1988": len(gl_rows) == 1988,
        "repo_convention_residual_gauge_zero": sum(
            int(row["repo_convention_residual_gauge_dimension"]) for row in rows
        )
        == 0,
        "mathematical_pgl_dimension_retained": sum(
            int(row["mathematical_projective_gauge_dimension"]) for row in rows
        )
        == 946,
        "contract_mentions_identity_convention": "g_s = I" in contract.get("convention", ""),
        "perennial_join_key_present_when_available": not perennial_available
        or (
            all(row.get("perennial_id", "").startswith("a985pf.") for row in rows)
            and all(row.get("coordinate_fingerprint_id", "").startswith("a985coord.") for row in rows)
            and all(row.get("perennial_id", "").startswith("a985pf.") for row in gl_rows)
            and all(row.get("coordinate_fingerprint_id", "").startswith("a985coord.") for row in gl_rows)
        ),
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
