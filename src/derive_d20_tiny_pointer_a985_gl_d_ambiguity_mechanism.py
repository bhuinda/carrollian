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
THEOREM_ID = "tiny_pointer_a985_gl_d_ambiguity_mechanism"
STATUS = "D20_TINY_POINTER_A985_GL_D_AMBIGUITY_MECHANISM_CERTIFIED"
VERIFY_STATUS = "D20_TINY_POINTER_A985_GL_D_AMBIGUITY_MECHANISM_VERIFIED"
VERIFY_FAILED_STATUS = "D20_TINY_POINTER_A985_GL_D_AMBIGUITY_MECHANISM_VERIFY_FAILED"

OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
NORMALIZATION_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_sector_normalization_obligations"
FIXTURE_ATLAS_DIR = (
    D20_INVARIANTS / "theorems" / "tiny_pointer_a985_all_open_sector_normalization_fixture_atlas"
)
FOLD_FRAME_DIR = (
    D20_INVARIANTS / "theorems" / "tiny_pointer_a985_burning_ship_fold_frame_normalization_anchors"
)
FULL_COO_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_full_matrix_unit_orbital_coo"


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


def bool_text(value: str) -> bool:
    return value == "True"


def ambiguity_group(dimension: int) -> str:
    if dimension <= 1:
        return "trivial"
    return f"PGL_{dimension}(F_{FIELD_PRIME})"


def load_fixture_by_sector() -> dict[int, dict[str, str]]:
    rows = read_csv_rows(FIXTURE_ATLAS_DIR / "open_sector_fixture_summary.csv")
    return {int(row["source_sector"]): row for row in rows}


def mechanism_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    obligations = read_csv_rows(NORMALIZATION_DIR / "sector_local_normalization_obligations.csv")
    fixtures = load_fixture_by_sector()
    rows: list[dict[str, Any]] = []
    witness_rows: list[dict[str, Any]] = []
    for row in obligations:
        source_sector = int(row["source_sector"])
        raw_sector = int(row["raw_sector"])
        dimension = int(row["block_dimension"])
        status = row["normalization_status"]
        intrinsic_dim = dimension * dimension - 1 if dimension > 1 else 0
        residual_dim = intrinsic_dim if status == "OPEN_GL_BLOCK_NORMALIZATION" else 0
        fixture = fixtures.get(source_sector)
        witness_present = fixture is not None
        witness_zero_residual = witness_present and int(fixture["formula_residual_nonzeros"]) == 0
        witness_preserves_central_page = witness_present and bool_text(fixture["diagonal_sum_preserved"])
        rows.append(
            {
                "source_sector": source_sector,
                "raw_sector": raw_sector,
                "block_dimension": dimension,
                "normalization_status": status,
                "coefficient_source": row["coefficient_source"],
                "intrinsic_ambiguity_group": ambiguity_group(dimension),
                "intrinsic_projective_gauge_dimension": intrinsic_dim,
                "residual_unanchored_projective_gauge_dimension": residual_dim,
                "why_ambiguous": (
                    "changing the simple-module basis conjugates the matrix-unit system while preserving multiplication"
                    if dimension > 1
                    else "dimension-one block has no off-diagonal basis choice"
                ),
                "current_anchor": row["normalization_anchor"],
                "nontrivial_gl_witness_present": witness_present,
                "witness_formula_residual_zero": witness_zero_residual,
                "witness_preserves_central_page": witness_preserves_central_page,
            }
        )
        if fixture is not None:
            witness_rows.append(
                {
                    "source_sector": source_sector,
                    "raw_sector": raw_sector,
                    "block_dimension": dimension,
                    "source_gl_sha256": fixture["source_gl_sha256"],
                    "solved_gl_sha256": fixture["solved_gl_sha256"],
                    "source_det_g": int(fixture["source_det_g"]),
                    "solved_det_g": int(fixture["solved_det_g"]),
                    "source_nonidentity": bool_text(fixture["source_nonidentity"]),
                    "solved_nonidentity": bool_text(fixture["solved_nonidentity"]),
                    "solved_left_inverse_holds": bool_text(fixture["solved_left_inverse_holds"]),
                    "solved_right_inverse_holds": bool_text(fixture["solved_right_inverse_holds"]),
                    "formula_residual_nonzeros": int(fixture["formula_residual_nonzeros"]),
                    "diagonal_sum_preserved": bool_text(fixture["diagonal_sum_preserved"]),
                    "candidate_matrix_units_sha256": fixture["candidate_matrix_units_sha256"],
                }
            )
    return rows, witness_rows


def explanation_payload() -> dict[str, Any]:
    return {
        "schema": "d20.tiny_pointer_a985.gl_d_ambiguity_explanation@1",
        "formula": "v_s[i,j] = sum_{a,b} g_s[a,i] * ginv_s[j,b] * u_s[a,b]",
        "condition": "g_s is invertible and ginv_s is its inverse over F_1000003",
        "reason": (
            "A primitive central page e_s cuts out a simple matrix algebra M_d(F). Choosing matrix "
            "units inside that block is the same as choosing a basis of the d-dimensional simple "
            "module. Any invertible basis change gives another valid matrix-unit system."
        ),
        "scalar_quotient": (
            "Multiplying g_s by a nonzero scalar does not change v_s, because the scalar cancels "
            "against g_s^{-1}. The effective ambiguity is therefore PGL_d, with dimension d^2 - 1."
        ),
        "what_current_certificates_fix": [
            "the primitive central idempotent e_s",
            "the raw A985 multiplication law",
            "one constructed matrix-unit system per source sector",
            "Burning Ship fold-frame anchors for the static Z/2 x Z/4^2 quotient",
        ],
        "what_they_do_not_fix": (
            "For open d>1 blocks they do not supply an independent ordered basis of the simple "
            "module, a preferred rank-one idempotent flag, or an external off-diagonal source."
        ),
    }


def build_theorem() -> dict[str, Any]:
    normalization_report = load_json(NORMALIZATION_DIR / "report.json")
    fixture_report = load_json(FIXTURE_ATLAS_DIR / "report.json")
    fold_frame_report = load_json(FOLD_FRAME_DIR / "report.json")
    full_coo_report = load_json(FULL_COO_DIR / "report.json")
    perennial_maps = load_perennial_sector_maps_if_available()
    rows, witness_rows = mechanism_rows()
    explanation = explanation_payload()
    status_counts = Counter(row["normalization_status"] for row in rows)
    dimension_hist = Counter(int(row["block_dimension"]) for row in rows)
    intrinsic_total = sum(int(row["intrinsic_projective_gauge_dimension"]) for row in rows)
    residual_total = sum(int(row["residual_unanchored_projective_gauge_dimension"]) for row in rows)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    mechanism_perennial_stats = write_a985_sector_csv_rows_if_available(
        OUT_DIR / "gl_d_ambiguity_mechanism_by_sector.csv",
        [
            "source_sector",
            "raw_sector",
            "block_dimension",
            "normalization_status",
            "coefficient_source",
            "intrinsic_ambiguity_group",
            "intrinsic_projective_gauge_dimension",
            "residual_unanchored_projective_gauge_dimension",
            "why_ambiguous",
            "current_anchor",
            "nontrivial_gl_witness_present",
            "witness_formula_residual_zero",
            "witness_preserves_central_page",
        ],
        rows,
        perennial_maps,
    )
    witness_perennial_stats = write_a985_sector_csv_rows_if_available(
        OUT_DIR / "gl_d_nontrivial_conjugate_witnesses.csv",
        [
            "source_sector",
            "raw_sector",
            "block_dimension",
            "source_gl_sha256",
            "solved_gl_sha256",
            "source_det_g",
            "solved_det_g",
            "source_nonidentity",
            "solved_nonidentity",
            "solved_left_inverse_holds",
            "solved_right_inverse_holds",
            "formula_residual_nonzeros",
            "diagonal_sum_preserved",
            "candidate_matrix_units_sha256",
        ],
        witness_rows,
        perennial_maps,
    )
    write_json(OUT_DIR / "gl_d_ambiguity_explanation.json", explanation)

    open_rows = [row for row in rows if row["normalization_status"] == "OPEN_GL_BLOCK_NORMALIZATION"]
    nontrivial_rows = [row for row in rows if int(row["block_dimension"]) > 1]
    checks = {
        "normalization_obligations_certified": normalization_report.get("status")
        == "D20_TINY_POINTER_A985_SECTOR_NORMALIZATION_OBLIGATIONS_CERTIFIED"
        and normalization_report.get("all_checks_pass") is True,
        "all_open_fixture_atlas_certified": fixture_report.get("status")
        == "D20_TINY_POINTER_A985_ALL_OPEN_SECTOR_NORMALIZATION_FIXTURE_ATLAS_CERTIFIED"
        and fixture_report.get("all_checks_pass") is True,
        "fold_frame_anchors_certified": fold_frame_report.get("status")
        == "D20_TINY_POINTER_A985_BURNING_SHIP_FOLD_FRAME_NORMALIZATION_ANCHORS_CERTIFIED"
        and fold_frame_report.get("all_checks_pass") is True,
        "full_matrix_unit_coo_certified": full_coo_report.get("status")
        == "D20_TINY_POINTER_A985_FULL_MATRIX_UNIT_ORBITAL_COO_CERTIFIED"
        and full_coo_report.get("all_checks_pass") is True,
        "sector_rows_cover_39": len(rows) == 39,
        "dimension_histogram_matches_wedderburn_profile": dict(sorted(dimension_hist.items()))
        == {1: 7, 2: 8, 3: 4, 4: 8, 5: 4, 6: 2, 8: 1, 9: 1, 10: 2, 11: 1, 12: 1},
        "intrinsic_pgl_dimension_is_946": intrinsic_total == 946,
        "residual_unanchored_pgl_dimension_is_940": residual_total == 940,
        "open_sector_count_is_30": status_counts["OPEN_GL_BLOCK_NORMALIZATION"] == 30,
        "dimension_one_sector_count_is_7": status_counts["CANONICAL_DIMENSION_ONE"] == 7,
        "registered_support_anchored_nontrivial_count_is_2": status_counts["REGISTERED_SUPPORT_ANCHORED"] == 2,
        "every_open_sector_has_nontrivial_witness": all(
            row["nontrivial_gl_witness_present"] is True for row in open_rows
        ),
        "every_open_witness_has_zero_residual": all(
            row["witness_formula_residual_zero"] is True for row in open_rows
        ),
        "every_open_witness_preserves_central_page": all(
            row["witness_preserves_central_page"] is True for row in open_rows
        ),
        "nontrivial_sectors_have_pgl_group": all(
            str(row["intrinsic_ambiguity_group"]).startswith("PGL_") for row in nontrivial_rows
        ),
        "perennial_join_key_emitted_when_available": perennial_maps is None
        or (
            mechanism_perennial_stats["rows_with_perennial_id"]
            == mechanism_perennial_stats["rows_with_direct_sector"]
            == len(rows)
            and witness_perennial_stats["rows_with_perennial_id"]
            == witness_perennial_stats["rows_with_direct_sector"]
            == len(witness_rows)
            and mechanism_perennial_stats["sector_mismatch_count"] == 0
            and witness_perennial_stats["sector_mismatch_count"] == 0
        ),
    }
    report = {
        "schema": "d20.theorem.tiny_pointer_a985_gl_d_ambiguity_mechanism.source_drop",
        "status": STATUS,
        "object": "d20",
        "field_prime": FIELD_PRIME,
        "claim": (
            "The sector-local GL_d ambiguity is the ordinary basis-change symmetry of each "
            "matrix block e_s A985 e_s. Central idempotents and matrix-unit laws determine the "
            "block algebra but not an ordered simple-module basis; non-identity GL_d conjugates "
            "give equally valid raw-orbital matrix units."
        ),
        "boundary": (
            "This explains and witnesses the ambiguity. It does not choose the missing external "
            "basis for the 30 open sectors."
        ),
        "inputs": {
            "sector_normalization_obligations": {
                "path": rel(NORMALIZATION_DIR / "report.json"),
                "sha256": sha_file(NORMALIZATION_DIR / "report.json"),
            },
            "all_open_fixture_atlas": {
                "path": rel(FIXTURE_ATLAS_DIR / "report.json"),
                "sha256": sha_file(FIXTURE_ATLAS_DIR / "report.json"),
            },
            "fold_frame_anchors": {
                "path": rel(FOLD_FRAME_DIR / "report.json"),
                "sha256": sha_file(FOLD_FRAME_DIR / "report.json"),
            },
            "full_matrix_unit_orbital_coo": {
                "path": rel(FULL_COO_DIR / "report.json"),
                "sha256": sha_file(FULL_COO_DIR / "report.json"),
            },
        },
        "checks": checks,
        "derived": {
            "intrinsic_pgl_dimension": intrinsic_total,
            "residual_unanchored_pgl_dimension": residual_total,
            "status_counts": dict(status_counts),
            "dimension_histogram": {str(key): value for key, value in sorted(dimension_hist.items())},
            "nontrivial_sector_count": len(nontrivial_rows),
            "open_sector_count": len(open_rows),
            "witness_count": len(witness_rows),
            "formula": explanation["formula"],
            "perennial_join_key": {
                "map_available": perennial_maps is not None,
                "mechanism_rows_resolved": int(mechanism_perennial_stats["rows_with_perennial_id"]),
                "witness_rows_resolved": int(witness_perennial_stats["rows_with_perennial_id"]),
            },
            "tables": {
                "mechanism_by_sector": rel(OUT_DIR / "gl_d_ambiguity_mechanism_by_sector.csv"),
                "nontrivial_conjugate_witnesses": rel(OUT_DIR / "gl_d_nontrivial_conjugate_witnesses.csv"),
                "explanation": rel(OUT_DIR / "gl_d_ambiguity_explanation.json"),
            },
        },
        "next_highest_yield_item": (
            "Either accept the current constructed basis as the repo convention for open sectors, "
            "or add an external criterion that selects a rank-one idempotent flag in each open block."
        ),
        "all_checks_pass": all(checks.values()),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    manifest = {
        "schema": "d20.theorem.tiny_pointer_a985_gl_d_ambiguity_mechanism_manifest.source_drop",
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
    (OUT_DIR / "gl_d_ambiguity_mechanism_report.md").write_text(markdown_report(report), encoding="utf-8")
    update_theorem_index(report)
    return report


def markdown_report(report: dict[str, Any]) -> str:
    checks = "\n".join(f"- `{name}`: `{value}`" for name, value in report["checks"].items())
    derived = report["derived"]
    return (
        "# GL_d ambiguity mechanism\n\n"
        f"Status: `{report['status']}`\n\n"
        f"{report['claim']}\n\n"
        f"Boundary: {report['boundary']}\n\n"
        f"Intrinsic PGL dimension: `{derived['intrinsic_pgl_dimension']}`\n\n"
        f"Residual unanchored PGL dimension: `{derived['residual_unanchored_pgl_dimension']}`\n\n"
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
    rows = read_csv_rows(OUT_DIR / "gl_d_ambiguity_mechanism_by_sector.csv")
    witnesses = read_csv_rows(OUT_DIR / "gl_d_nontrivial_conjugate_witnesses.csv")
    explanation = load_json(OUT_DIR / "gl_d_ambiguity_explanation.json")
    perennial_available = bool(report.get("derived", {}).get("perennial_join_key", {}).get("map_available"))
    checks = {
        "report_status_certified": report.get("status") == STATUS,
        "report_checks_pass": report.get("all_checks_pass") is True,
        "mechanism_rows_cover_39": len(rows) == 39,
        "witness_rows_cover_30_open_sectors": len(witnesses) == 30,
        "intrinsic_pgl_dimension_is_946": sum(
            int(row["intrinsic_projective_gauge_dimension"]) for row in rows
        )
        == 946,
        "residual_unanchored_pgl_dimension_is_940": sum(
            int(row["residual_unanchored_projective_gauge_dimension"]) for row in rows
        )
        == 940,
        "all_witnesses_nonidentity": all(
            row["source_nonidentity"] == "True" and row["solved_nonidentity"] == "True" for row in witnesses
        ),
        "all_witnesses_zero_residual": all(int(row["formula_residual_nonzeros"]) == 0 for row in witnesses),
        "all_witnesses_preserve_central_page": all(row["diagonal_sum_preserved"] == "True" for row in witnesses),
        "explanation_has_formula": "g_s" in explanation.get("formula", ""),
        "perennial_join_key_present_when_available": not perennial_available
        or (
            all(row.get("perennial_id", "").startswith("a985pf.") for row in rows)
            and all(row.get("coordinate_fingerprint_id", "").startswith("a985coord.") for row in rows)
            and all(row.get("perennial_id", "").startswith("a985pf.") for row in witnesses)
            and all(row.get("coordinate_fingerprint_id", "").startswith("a985coord.") for row in witnesses)
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
