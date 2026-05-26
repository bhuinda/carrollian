from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT_FOR_IMPORT = Path(__file__).resolve().parents[1]
if str(ROOT_FOR_IMPORT) not in sys.path:
    sys.path.insert(0, str(ROOT_FOR_IMPORT))

from src.derive_d20_tiny_pointer_a985_block_matrix_units import FIELD_PRIME, array_digest  # noqa: E402
from src.derive_d20_tiny_pointer_a985_sector5_normalization_solver_selftest import (  # noqa: E402
    coordinate_columns,
    formula_coords,
    inv_matrix_mod,
    load_sector_units,
    solve_gl2,
    verify_raw_matrix_unit_law,
)
from src.paths import D20_INVARIANTS, ROOT  # noqa: E402


STATUS = "D20_TINY_POINTER_A985_SECTOR5_NORMALIZATION_SOLVER_NONTRIVIAL_FIXTURE_CERTIFIED"
THEOREM_ID = "tiny_pointer_a985_sector5_normalization_solver_nontrivial_fixture"
OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

PILOT_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_sector5_normalization_pilot"
SELFTEST_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_sector5_normalization_solver_selftest"


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


def source_gl2() -> tuple[np.ndarray, np.ndarray]:
    g = np.array([[2, 3], [5, 7]], dtype=np.int64) % FIELD_PRIME
    ginv = inv_matrix_mod(g)
    return g, ginv


def candidate_rows_from_vectors(vectors: np.ndarray) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for col in range(4):
        target_i, target_j = divmod(col, 2)
        support = np.nonzero(vectors[:, col] % FIELD_PRIME)[0]
        for relation in support:
            rows.append(
                {
                    "candidate_unit_label": f"v_sector[5;{target_i},{target_j}]",
                    "local_unit_column": col,
                    "relation_alpha": int(relation),
                    "coefficient_mod_1000003": int(vectors[int(relation), col] % FIELD_PRIME),
                    "candidate_source": "NONTRIVIAL_GL2_FIXTURE_FROM_CERTIFIED_SECTOR5_RAW_UNITS",
                }
            )
    return rows


def coordinate_rows(coords: np.ndarray) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for target_col in range(4):
        target_i, target_j = divmod(target_col, 2)
        for source_col in range(4):
            value = int(coords[source_col, target_col] % FIELD_PRIME)
            if value == 0:
                continue
            source_i, source_j = divmod(source_col, 2)
            rows.append(
                {
                    "candidate_unit_label": f"v_sector[5;{target_i},{target_j}]",
                    "target_i": target_i,
                    "target_j": target_j,
                    "source_i": source_i,
                    "source_j": source_j,
                    "coefficient_mod_1000003": value,
                }
            )
    return rows


def gl2_rows(name: str, g: np.ndarray, ginv: np.ndarray) -> list[dict[str, Any]]:
    det = int((g[0, 0] * g[1, 1] - g[0, 1] * g[1, 0]) % FIELD_PRIME)
    rows = [
        {"solution_name": name, "variable": f"g[{i},{j}]", "value_mod_1000003": int(g[i, j])}
        for i in range(2)
        for j in range(2)
    ]
    rows += [
        {"solution_name": name, "variable": f"ginv[{i},{j}]", "value_mod_1000003": int(ginv[i, j])}
        for i in range(2)
        for j in range(2)
    ]
    rows.append({"solution_name": name, "variable": "det_g", "value_mod_1000003": det})
    return rows


def residual_rows(candidates: np.ndarray, reconstructed: np.ndarray) -> list[dict[str, Any]]:
    residual = (candidates - reconstructed) % FIELD_PRIME
    rows: list[dict[str, Any]] = []
    for col in range(4):
        target_i, target_j = divmod(col, 2)
        col_residual = residual[:, col]
        rows.append(
            {
                "candidate_unit_label": f"v_sector[5;{target_i},{target_j}]",
                "target_i": target_i,
                "target_j": target_j,
                "max_residual_mod_1000003": int(np.max(col_residual)),
                "nonzero_residual_count": int(np.count_nonzero(col_residual)),
            }
        )
    return rows


def write_outputs(
    candidate_rows: list[dict[str, Any]],
    coords: np.ndarray,
    source_g: np.ndarray,
    source_ginv: np.ndarray,
    solved_g: np.ndarray,
    solved_ginv: np.ndarray,
    residuals: list[dict[str, Any]],
    chart_rows: list[int],
) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(
        OUT_DIR / "sector5_nontrivial_candidate_units.csv",
        [
            "candidate_unit_label",
            "local_unit_column",
            "relation_alpha",
            "coefficient_mod_1000003",
            "candidate_source",
        ],
        candidate_rows,
    )
    write_csv_rows(
        OUT_DIR / "sector5_nontrivial_candidate_coordinates.csv",
        [
            "candidate_unit_label",
            "target_i",
            "target_j",
            "source_i",
            "source_j",
            "coefficient_mod_1000003",
        ],
        coordinate_rows(coords),
    )
    write_csv_rows(
        OUT_DIR / "sector5_nontrivial_gl2_source_and_solution.csv",
        ["solution_name", "variable", "value_mod_1000003"],
        gl2_rows("source_fixture", source_g, source_ginv) + gl2_rows("solved_from_candidate", solved_g, solved_ginv),
    )
    write_csv_rows(
        OUT_DIR / "sector5_nontrivial_solver_residuals.csv",
        [
            "candidate_unit_label",
            "target_i",
            "target_j",
            "max_residual_mod_1000003",
            "nonzero_residual_count",
        ],
        residuals,
    )
    write_json(
        OUT_DIR / "sector5_nontrivial_row_chart.json",
        {
            "schema": "d20.tiny_pointer.a985.sector5_nontrivial_solver_row_chart@1",
            "field_prime": FIELD_PRIME,
            "selected_relation_rows": chart_rows,
        },
    )


def markdown_report(report: dict[str, Any]) -> str:
    checks = "\n".join(f"- `{key}`: `{value}`" for key, value in report["checks"].items())
    return (
        "# Sector 5 Nontrivial Normalization Fixture\n\n"
        f"Status: `{report['status']}`\n\n"
        "This verifies the sector-5 GL2 solver on a non-identity fixture generated from the "
        "certified raw matrix-unit chart. It proves the solver handles nontrivial basis changes, "
        "but remains a fixture rather than an independent source-sector basis.\n\n"
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


def build_nontrivial_fixture() -> dict[str, Any]:
    pilot_report = load_json(PILOT_DIR / "report.json")
    selftest_report = load_json(SELFTEST_DIR / "report.json")
    _manifest, units = load_sector_units()
    source_g, source_ginv = source_gl2()
    source_coords = formula_coords(source_g, source_ginv)
    candidates = (units @ source_coords) % FIELD_PRIME
    rows = candidate_rows_from_vectors(candidates)
    chart_rows, coords = coordinate_columns(units, candidates)
    solved_g, solved_ginv, solve_meta = solve_gl2(coords)
    solved_coords = formula_coords(solved_g, solved_ginv)
    reconstructed = (units @ solved_coords) % FIELD_PRIME
    residuals = residual_rows(candidates, reconstructed)
    product_check = verify_raw_matrix_unit_law(candidates)
    write_outputs(rows, coords, source_g, source_ginv, solved_g, solved_ginv, residuals, chart_rows)

    identity = np.eye(2, dtype=np.int64)
    source_det = int((source_g[0, 0] * source_g[1, 1] - source_g[0, 1] * source_g[1, 0]) % FIELD_PRIME)
    solved_det = int((solved_g[0, 0] * solved_g[1, 1] - solved_g[0, 1] * solved_g[1, 0]) % FIELD_PRIME)
    checks = {
        "pilot_certified": pilot_report.get("status") == "D20_TINY_POINTER_A985_SECTOR5_NORMALIZATION_PILOT_CERTIFIED"
        and pilot_report.get("all_checks_pass") is True,
        "selftest_certified": selftest_report.get("status")
        == "D20_TINY_POINTER_A985_SECTOR5_NORMALIZATION_SOLVER_SELFTEST_CERTIFIED"
        and selftest_report.get("all_checks_pass") is True,
        "source_gl2_is_nonidentity": not np.array_equal(source_g, identity),
        "source_gl2_det_nonzero": source_det != 0,
        "candidate_coo_rows_match_nonzeros": len(rows) == int(np.count_nonzero(candidates)),
        "candidate_has_four_nonzero_units": all(np.count_nonzero(candidates[:, col]) > 0 for col in range(4)),
        "row_chart_has_4_rows": len(chart_rows) == 4,
        "coordinate_matrix_matches_source_formula": bool(np.array_equal(coords % FIELD_PRIME, source_coords % FIELD_PRIME)),
        "solved_gl2_det_nonzero": solved_det != 0,
        "solved_gl2_is_nonidentity": not np.array_equal(solved_g % FIELD_PRIME, identity),
        "solved_left_inverse_holds": bool(np.array_equal((solved_ginv @ solved_g) % FIELD_PRIME, identity)),
        "solved_right_inverse_holds": bool(np.array_equal((solved_g @ solved_ginv) % FIELD_PRIME, identity)),
        "solved_formula_reconstructs_candidate": bool(np.array_equal(reconstructed, candidates)),
        "solver_residuals_zero": all(row["nonzero_residual_count"] == 0 for row in residuals),
        "candidate_raw_matrix_unit_law_exhaustive": product_check["checked"] == 16
        and product_check["failure_count"] == 0,
    }
    report = {
        "schema": "d20.theorem.tiny_pointer_a985_sector5_normalization_solver_nontrivial_fixture.source_drop",
        "status": STATUS
        if all(checks.values())
        else "D20_TINY_POINTER_A985_SECTOR5_NORMALIZATION_SOLVER_NONTRIVIAL_FIXTURE_NEEDS_REVIEW",
        "object": "d20",
        "field_prime": FIELD_PRIME,
        "claim": (
            "The sector-5 GL2 normalization solver verifies an explicitly non-identity fixture. "
            "The candidate is generated from the certified raw chart by a known invertible GL2 "
            "change of basis, and the solver reconstructs an equivalent non-identity transform "
            "with zero raw-coordinate residuals."
        ),
        "boundary": (
            "This remains a generated fixture, not an independent source-sector off-diagonal matrix-unit source."
        ),
        "inputs": {
            "sector5_normalization_pilot": {
                "path": rel(PILOT_DIR / "report.json"),
                "sha256": sha_file(PILOT_DIR / "report.json"),
            },
            "sector5_solver_selftest": {
                "path": rel(SELFTEST_DIR / "report.json"),
                "sha256": sha_file(SELFTEST_DIR / "report.json"),
            },
        },
        "checks": checks,
        "derived": {
            "candidate_source": "NONTRIVIAL_GL2_FIXTURE_FROM_CERTIFIED_SECTOR5_RAW_UNITS",
            "candidate_coo_rows": len(rows),
            "selected_relation_rows": chart_rows,
            "source_gl2": {
                "g": source_g.astype(int).tolist(),
                "ginv": source_ginv.astype(int).tolist(),
                "det_g": source_det,
            },
            "solved_gl2": {
                "g": solved_g.astype(int).tolist(),
                "ginv": solved_ginv.astype(int).tolist(),
                "det_g": solved_det,
                **solve_meta,
            },
            "source_coordinate_matrix_sha256": array_digest(source_coords),
            "solved_coordinate_matrix_sha256": array_digest(solved_coords),
            "candidate_units_sha256": array_digest(candidates),
            "reconstructed_units_sha256": array_digest(reconstructed),
            "raw_product_check": product_check,
            "tables": {
                "candidate": rel(OUT_DIR / "sector5_nontrivial_candidate_units.csv"),
                "coordinates": rel(OUT_DIR / "sector5_nontrivial_candidate_coordinates.csv"),
                "gl2_source_and_solution": rel(OUT_DIR / "sector5_nontrivial_gl2_source_and_solution.csv"),
                "residuals": rel(OUT_DIR / "sector5_nontrivial_solver_residuals.csv"),
                "row_chart": rel(OUT_DIR / "sector5_nontrivial_row_chart.json"),
            },
        },
        "next_highest_yield_item": (
            "Use the same verifier on an external sector-5 candidate file, because the solver has now "
            "been checked on both identity and non-identity controlled candidates."
        ),
        "all_checks_pass": all(checks.values()),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    manifest = {
        "schema": "d20.theorem.tiny_pointer_a985_sector5_normalization_solver_nontrivial_fixture_manifest.source_drop",
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
    (OUT_DIR / "sector5_normalization_solver_nontrivial_fixture_report.md").write_text(
        markdown_report(report),
        encoding="utf-8",
    )
    update_theorem_index(report)
    return report


def verify_nontrivial_fixture() -> dict[str, Any]:
    report = load_json(OUT_DIR / "report.json")
    candidate_rows = read_csv_rows(OUT_DIR / "sector5_nontrivial_candidate_units.csv")
    coord_rows = read_csv_rows(OUT_DIR / "sector5_nontrivial_candidate_coordinates.csv")
    solution_rows = read_csv_rows(OUT_DIR / "sector5_nontrivial_gl2_source_and_solution.csv")
    residual_rows = read_csv_rows(OUT_DIR / "sector5_nontrivial_solver_residuals.csv")
    chart = load_json(OUT_DIR / "sector5_nontrivial_row_chart.json")
    checks = {
        "report_status_certified": report.get("status") == STATUS,
        "report_checks_pass": report.get("all_checks_pass") is True,
        "candidate_rows_match_report": len(candidate_rows) == report.get("derived", {}).get("candidate_coo_rows"),
        "coordinate_rows_are_nonempty": len(coord_rows) > 4,
        "source_and_solution_have_18_rows": len(solution_rows) == 18,
        "residuals_have_4_rows": len(residual_rows) == 4,
        "all_residuals_zero": all(int(row["nonzero_residual_count"]) == 0 for row in residual_rows),
        "row_chart_has_4_rows": len(chart.get("selected_relation_rows", [])) == 4,
    }
    return {
        "status": "D20_TINY_POINTER_A985_SECTOR5_NORMALIZATION_SOLVER_NONTRIVIAL_FIXTURE_VERIFIED"
        if all(checks.values())
        else "D20_TINY_POINTER_A985_SECTOR5_NORMALIZATION_SOLVER_NONTRIVIAL_FIXTURE_VERIFY_FAILED",
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if not args.verify_only:
        build_nontrivial_fixture()
    verification = verify_nontrivial_fixture()
    print(json.dumps(verification, indent=2, sort_keys=True))
    if not verification["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

