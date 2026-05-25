from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

ROOT_FOR_IMPORT = Path(__file__).resolve().parents[1]
if str(ROOT_FOR_IMPORT) not in sys.path:
    sys.path.insert(0, str(ROOT_FOR_IMPORT))

from src.derive_d20_tiny_pointer_a985_block_matrix_units import (  # noqa: E402
    FIELD_PRIME,
    RELATION_COUNT,
    MultiplicationOracle,
    array_digest,
)
from src.derive_d20_tiny_pointer_a985_sector5_normalization_solver_selftest import (  # noqa: E402
    inv_matrix_mod,
    inv_scalar,
    select_row_chart,
)
from src.paths import D20_INVARIANTS, ROOT  # noqa: E402


STATUS = "D20_TINY_POINTER_A985_ALL_OPEN_SECTOR_NORMALIZATION_FIXTURE_ATLAS_CERTIFIED"
THEOREM_ID = "tiny_pointer_a985_all_open_sector_normalization_fixture_atlas"
OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FULL_COO_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_full_matrix_unit_orbital_coo"
OBLIGATIONS_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_sector_normalization_obligations"
NONTRIVIAL_FIXTURE_DIR = (
    D20_INVARIANTS / "theorems" / "tiny_pointer_a985_sector5_normalization_solver_nontrivial_fixture"
)
TENSOR_NPZ = ROOT / "data" / "raw" / "T_985.npz"


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


def det_mod(matrix: np.ndarray) -> int:
    mat = np.asarray(matrix, dtype=np.int64).copy() % FIELD_PRIME
    n, m = mat.shape
    if n != m:
        raise ValueError("determinant requires a square matrix")
    det = 1
    for col in range(n):
        pivot = None
        for row in range(col, n):
            if int(mat[row, col]) % FIELD_PRIME:
                pivot = row
                break
        if pivot is None:
            return 0
        if pivot != col:
            mat[[col, pivot]] = mat[[pivot, col]]
            det = (-det) % FIELD_PRIME
        pivot_value = int(mat[col, col]) % FIELD_PRIME
        det = (det * pivot_value) % FIELD_PRIME
        inv = inv_scalar(pivot_value)
        for row in range(col + 1, n):
            factor = int(mat[row, col]) * inv % FIELD_PRIME
            if factor:
                mat[row] = (mat[row] - factor * mat[col]) % FIELD_PRIME
    return int(det % FIELD_PRIME)


def fixture_gl(source_sector: int, dimension: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(20_260_524 + source_sector * 101 + dimension)
    for _ in range(256):
        g = rng.integers(0, 37, size=(dimension, dimension), dtype=np.int64) % FIELD_PRIME
        for idx in range(dimension):
            g[idx, idx] = (g[idx, idx] + idx + source_sector + 1) % FIELD_PRIME
            if int(g[idx, idx]) == 0:
                g[idx, idx] = 1
        try:
            ginv = inv_matrix_mod(g)
        except ValueError:
            continue
        if det_mod(g) and not np.array_equal(g % FIELD_PRIME, np.eye(dimension, dtype=np.int64)):
            return g % FIELD_PRIME, ginv % FIELD_PRIME
    raise RuntimeError(f"failed to find invertible fixture GL matrix for sector {source_sector}")


def formula_coords(g: np.ndarray, ginv: np.ndarray) -> np.ndarray:
    dimension = int(g.shape[0])
    coords = np.zeros((dimension * dimension, dimension * dimension), dtype=np.int64)
    for target_i in range(dimension):
        for target_j in range(dimension):
            col = target_i * dimension + target_j
            for source_a in range(dimension):
                for source_b in range(dimension):
                    row = source_a * dimension + source_b
                    coords[row, col] = (
                        int(g[source_a, target_i]) * int(ginv[target_j, source_b])
                    ) % FIELD_PRIME
    return coords


def coordinate_columns(units: np.ndarray, vectors: np.ndarray) -> tuple[list[int], np.ndarray]:
    chart_rows = select_row_chart(units)
    chart = units[chart_rows, :]
    inv_chart = inv_matrix_mod(chart)
    coords = (inv_chart @ vectors[chart_rows, :]) % FIELD_PRIME
    return chart_rows, coords


def coord_matrix(coords: np.ndarray, dimension: int, target_i: int, target_j: int) -> np.ndarray:
    col = coords[:, target_i * dimension + target_j] % FIELD_PRIME
    return col.reshape((dimension, dimension))


def solve_gl(coords: np.ndarray, dimension: int) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    m00 = coord_matrix(coords, dimension, 0, 0)
    pivot = None
    for row in range(dimension):
        for col in range(dimension):
            if int(m00[row, col]) % FIELD_PRIME:
                pivot = (row, col)
                break
        if pivot is not None:
            break
    if pivot is None:
        raise ValueError("candidate v[0,0] has no nonzero pivot")

    pivot_row, pivot_col = pivot
    pivot_value = int(m00[pivot_row, pivot_col]) % FIELD_PRIME
    inv_pivot = inv_scalar(pivot_value)
    g = np.zeros((dimension, dimension), dtype=np.int64)
    ginv = np.zeros((dimension, dimension), dtype=np.int64)
    for target_i in range(dimension):
        g[:, target_i] = coord_matrix(coords, dimension, target_i, 0)[:, pivot_col]
    for target_j in range(dimension):
        ginv[target_j, :] = (
            coord_matrix(coords, dimension, 0, target_j)[pivot_row, :] * inv_pivot
        ) % FIELD_PRIME
    meta = {
        "pivot_row": int(pivot_row),
        "pivot_col": int(pivot_col),
        "pivot_value": int(pivot_value),
    }
    return g % FIELD_PRIME, ginv % FIELD_PRIME, meta


def load_open_obligations() -> list[dict[str, Any]]:
    rows = read_csv_rows(OBLIGATIONS_DIR / "sector_local_normalization_obligations.csv")
    open_rows = [
        {
            "source_sector": int(row["source_sector"]),
            "raw_sector": int(row["raw_sector"]),
            "block_dimension": int(row["block_dimension"]),
            "matrix_unit_count": int(row["matrix_unit_count"]),
            "normalization_status": row["normalization_status"],
            "matrix_unit_block_sha256": row["matrix_unit_block_sha256"],
        }
        for row in rows
        if row["normalization_status"] == "OPEN_GL_BLOCK_NORMALIZATION"
    ]
    return sorted(open_rows, key=lambda row: row["source_sector"])


def load_sector_block(arrays: np.lib.npyio.NpzFile, source_sector: int, dimension: int) -> np.ndarray:
    matrix_units = np.asarray(arrays["matrix_units"], dtype=np.int64) % FIELD_PRIME
    sectors = np.asarray(arrays["source_sector"], dtype=np.int64)
    local_i = np.asarray(arrays["i"], dtype=np.int64)
    local_j = np.asarray(arrays["j"], dtype=np.int64)
    block = np.zeros((RELATION_COUNT, dimension * dimension), dtype=np.int64)
    found = 0
    for idx in np.where(sectors == source_sector)[0]:
        i = int(local_i[idx])
        j = int(local_j[idx])
        block[:, i * dimension + j] = matrix_units[:, int(idx)]
        found += 1
    if found != dimension * dimension:
        raise ValueError(f"sector {source_sector} has {found} matrix-unit columns, expected {dimension * dimension}")
    return block % FIELD_PRIME


def coordinate_rows(source_sector: int, raw_sector: int, dimension: int, coords: np.ndarray) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for target_i in range(dimension):
        for target_j in range(dimension):
            target_col = target_i * dimension + target_j
            for source_a in range(dimension):
                for source_b in range(dimension):
                    source_row = source_a * dimension + source_b
                    value = int(coords[source_row, target_col]) % FIELD_PRIME
                    if value == 0:
                        continue
                    rows.append(
                        {
                            "source_sector": source_sector,
                            "raw_sector": raw_sector,
                            "block_dimension": dimension,
                            "target_i": target_i,
                            "target_j": target_j,
                            "source_a": source_a,
                            "source_b": source_b,
                            "coefficient_mod_1000003": value,
                        }
                    )
    return rows


def gl_rows(
    source_sector: int,
    raw_sector: int,
    dimension: int,
    name: str,
    g: np.ndarray,
    ginv: np.ndarray,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for i in range(dimension):
        for j in range(dimension):
            rows.append(
                {
                    "source_sector": source_sector,
                    "raw_sector": raw_sector,
                    "block_dimension": dimension,
                    "solution_name": name,
                    "variable": f"g[{i},{j}]",
                    "value_mod_1000003": int(g[i, j]) % FIELD_PRIME,
                }
            )
    for i in range(dimension):
        for j in range(dimension):
            rows.append(
                {
                    "source_sector": source_sector,
                    "raw_sector": raw_sector,
                    "block_dimension": dimension,
                    "solution_name": name,
                    "variable": f"ginv[{i},{j}]",
                    "value_mod_1000003": int(ginv[i, j]) % FIELD_PRIME,
                }
            )
    rows.append(
        {
            "source_sector": source_sector,
            "raw_sector": raw_sector,
            "block_dimension": dimension,
            "solution_name": name,
            "variable": "det_g",
            "value_mod_1000003": det_mod(g),
        }
    )
    return rows


def residual_rows(source_sector: int, raw_sector: int, dimension: int, residual: np.ndarray) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for target_i in range(dimension):
        for target_j in range(dimension):
            col = target_i * dimension + target_j
            col_residual = residual[:, col] % FIELD_PRIME
            rows.append(
                {
                    "source_sector": source_sector,
                    "raw_sector": raw_sector,
                    "block_dimension": dimension,
                    "target_i": target_i,
                    "target_j": target_j,
                    "max_residual_mod_1000003": int(np.max(col_residual)),
                    "nonzero_residual_count": int(np.count_nonzero(col_residual)),
                }
            )
    return rows


def raw_product_samples(
    candidate_blocks: dict[int, np.ndarray],
    dimensions: dict[int, int],
    sample_size: int,
    seed: int,
) -> dict[str, Any]:
    if sample_size <= 0:
        return {"checked": 0, "failure_count": 0, "failures": []}
    triples = np.asarray(np.load(TENSOR_NPZ)["triples"], dtype=np.int64)
    oracle = MultiplicationOracle(triples)
    rng = np.random.default_rng(seed)
    sectors = sorted(candidate_blocks)
    zero = np.zeros(RELATION_COUNT, dtype=np.int64)
    failures: list[dict[str, int]] = []
    for _ in range(sample_size):
        source_sector = int(sectors[int(rng.integers(0, len(sectors)))])
        d = dimensions[source_sector]
        i = int(rng.integers(0, d))
        j = int(rng.integers(0, d))
        k = int(rng.integers(0, d))
        ell = int(rng.integers(0, d))
        block = candidate_blocks[source_sector]
        product = oracle.product(block[:, i * d + j], block[:, k * d + ell])
        target = block[:, i * d + ell] if j == k else zero
        if not np.array_equal(product % FIELD_PRIME, target % FIELD_PRIME):
            failures.append(
                {
                    "source_sector": source_sector,
                    "left_i": i,
                    "left_j": j,
                    "right_i": k,
                    "right_j": ell,
                }
            )
            if len(failures) >= 8:
                break
    return {"checked": int(sample_size), "failure_count": len(failures), "failures": failures}


def write_outputs(
    summary_rows: list[dict[str, Any]],
    coordinate_nonzeros: list[dict[str, Any]],
    gl_table: list[dict[str, Any]],
    residual_table: list[dict[str, Any]],
) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(
        OUT_DIR / "open_sector_fixture_summary.csv",
        [
            "source_sector",
            "raw_sector",
            "block_dimension",
            "matrix_unit_count",
            "selected_relation_chart_rows",
            "source_gl_sha256",
            "solved_gl_sha256",
            "coordinate_matrix_sha256",
            "candidate_matrix_units_sha256",
            "candidate_raw_nonzeros",
            "coordinate_nonzeros",
            "source_det_g",
            "solved_det_g",
            "source_nonidentity",
            "solved_nonidentity",
            "solved_left_inverse_holds",
            "solved_right_inverse_holds",
            "formula_residual_nonzeros",
            "diagonal_sum_preserved",
            "pivot_row",
            "pivot_col",
            "pivot_value",
        ],
        summary_rows,
    )
    write_csv_rows(
        OUT_DIR / "open_sector_fixture_coordinate_nonzeros.csv",
        [
            "source_sector",
            "raw_sector",
            "block_dimension",
            "target_i",
            "target_j",
            "source_a",
            "source_b",
            "coefficient_mod_1000003",
        ],
        coordinate_nonzeros,
    )
    write_csv_rows(
        OUT_DIR / "open_sector_fixture_gl_source_and_solution.csv",
        [
            "source_sector",
            "raw_sector",
            "block_dimension",
            "solution_name",
            "variable",
            "value_mod_1000003",
        ],
        gl_table,
    )
    write_csv_rows(
        OUT_DIR / "open_sector_fixture_solver_residuals.csv",
        [
            "source_sector",
            "raw_sector",
            "block_dimension",
            "target_i",
            "target_j",
            "max_residual_mod_1000003",
            "nonzero_residual_count",
        ],
        residual_table,
    )


def build_atlas(raw_product_sample_size: int, seed: int) -> dict[str, Any]:
    full_coo_report = load_json(FULL_COO_DIR / "report.json")
    obligations_report = load_json(OBLIGATIONS_DIR / "report.json")
    sector5_fixture_report = load_json(NONTRIVIAL_FIXTURE_DIR / "report.json")
    open_obligations = load_open_obligations()
    arrays = np.load(FULL_COO_DIR / "source_sector_matrix_units_raw_orbital_arrays.npz")

    summary_rows: list[dict[str, Any]] = []
    coordinate_nonzeros: list[dict[str, Any]] = []
    gl_table: list[dict[str, Any]] = []
    residual_table: list[dict[str, Any]] = []
    candidate_blocks: dict[int, np.ndarray] = {}
    dimensions: dict[int, int] = {}

    for obligation in open_obligations:
        source_sector = int(obligation["source_sector"])
        raw_sector = int(obligation["raw_sector"])
        d = int(obligation["block_dimension"])
        source_block = load_sector_block(arrays, source_sector, d)
        chart_rows = coordinate_columns(source_block, source_block)[0]

        source_g, source_ginv = fixture_gl(source_sector, d)
        source_coords = formula_coords(source_g, source_ginv)
        candidate = (source_block @ source_coords) % FIELD_PRIME
        solved_chart_rows, candidate_coords = coordinate_columns(source_block, candidate)
        solved_g, solved_ginv, meta = solve_gl(candidate_coords, d)
        solved_coords = formula_coords(solved_g, solved_ginv)
        reconstructed = (source_block @ solved_coords) % FIELD_PRIME
        residual = (candidate - reconstructed) % FIELD_PRIME

        source_diag = np.sum(source_block[:, [i * d + i for i in range(d)]], axis=1) % FIELD_PRIME
        candidate_diag = np.sum(candidate[:, [i * d + i for i in range(d)]], axis=1) % FIELD_PRIME
        left_identity = (solved_g @ solved_ginv) % FIELD_PRIME
        right_identity = (solved_ginv @ solved_g) % FIELD_PRIME
        identity = np.eye(d, dtype=np.int64) % FIELD_PRIME

        if chart_rows != solved_chart_rows:
            raise RuntimeError(f"sector {source_sector} selected inconsistent coordinate charts")

        candidate_blocks[source_sector] = candidate
        dimensions[source_sector] = d
        coord_nonzero_count = int(np.count_nonzero(candidate_coords))
        residual_nonzeros = int(np.count_nonzero(residual))
        coordinate_nonzeros.extend(coordinate_rows(source_sector, raw_sector, d, candidate_coords))
        gl_table.extend(gl_rows(source_sector, raw_sector, d, "source_fixture", source_g, source_ginv))
        gl_table.extend(gl_rows(source_sector, raw_sector, d, "solved_from_candidate", solved_g, solved_ginv))
        residual_table.extend(residual_rows(source_sector, raw_sector, d, residual))
        summary_rows.append(
            {
                "source_sector": source_sector,
                "raw_sector": raw_sector,
                "block_dimension": d,
                "matrix_unit_count": d * d,
                "selected_relation_chart_rows": json.dumps([int(row) for row in chart_rows], separators=(",", ":")),
                "source_gl_sha256": array_digest(source_g),
                "solved_gl_sha256": array_digest(solved_g),
                "coordinate_matrix_sha256": array_digest(candidate_coords),
                "candidate_matrix_units_sha256": array_digest(candidate),
                "candidate_raw_nonzeros": int(np.count_nonzero(candidate)),
                "coordinate_nonzeros": coord_nonzero_count,
                "source_det_g": det_mod(source_g),
                "solved_det_g": det_mod(solved_g),
                "source_nonidentity": not np.array_equal(source_g % FIELD_PRIME, identity),
                "solved_nonidentity": not np.array_equal(solved_g % FIELD_PRIME, identity),
                "solved_left_inverse_holds": bool(np.array_equal(left_identity, identity)),
                "solved_right_inverse_holds": bool(np.array_equal(right_identity, identity)),
                "formula_residual_nonzeros": residual_nonzeros,
                "diagonal_sum_preserved": bool(np.array_equal(source_diag, candidate_diag)),
                "pivot_row": int(meta["pivot_row"]),
                "pivot_col": int(meta["pivot_col"]),
                "pivot_value": int(meta["pivot_value"]),
            }
        )

    sample = raw_product_samples(candidate_blocks, dimensions, raw_product_sample_size, seed + 39)
    dimension_histogram = Counter(row["block_dimension"] for row in summary_rows)
    checks = {
        "full_matrix_unit_coo_certified": full_coo_report.get("status")
        == "D20_TINY_POINTER_A985_FULL_MATRIX_UNIT_ORBITAL_COO_CERTIFIED"
        and full_coo_report.get("all_checks_pass") is True,
        "normalization_obligations_certified": obligations_report.get("status")
        == "D20_TINY_POINTER_A985_SECTOR_NORMALIZATION_OBLIGATIONS_CERTIFIED"
        and obligations_report.get("all_checks_pass") is True,
        "sector5_nontrivial_fixture_certified": sector5_fixture_report.get("status")
        == "D20_TINY_POINTER_A985_SECTOR5_NORMALIZATION_SOLVER_NONTRIVIAL_FIXTURE_CERTIFIED"
        and sector5_fixture_report.get("all_checks_pass") is True,
        "open_sector_count_is_30": len(summary_rows) == 30,
        "open_matrix_unit_count_is_970": sum(int(row["matrix_unit_count"]) for row in summary_rows) == 970,
        "coordinate_rows_match_summary": len(coordinate_nonzeros)
        == sum(int(row["coordinate_nonzeros"]) for row in summary_rows),
        "all_source_gl_nonidentity": all(row["source_nonidentity"] for row in summary_rows),
        "all_solved_gl_nonidentity": all(row["solved_nonidentity"] for row in summary_rows),
        "all_solved_left_inverses_hold": all(row["solved_left_inverse_holds"] for row in summary_rows),
        "all_solved_right_inverses_hold": all(row["solved_right_inverse_holds"] for row in summary_rows),
        "all_formula_residuals_zero": all(int(row["formula_residual_nonzeros"]) == 0 for row in summary_rows),
        "all_diagonal_sums_preserved": all(row["diagonal_sum_preserved"] for row in summary_rows),
        "sampled_raw_candidate_products_pass": sample["failure_count"] == 0,
    }
    write_outputs(summary_rows, coordinate_nonzeros, gl_table, residual_table)

    report = {
        "schema": "d20.theorem.tiny_pointer_a985_all_open_sector_normalization_fixture_atlas.source_drop",
        "status": STATUS if all(checks.values()) else "D20_TINY_POINTER_A985_ALL_OPEN_SECTOR_NORMALIZATION_FIXTURE_ATLAS_NEEDS_REVIEW",
        "object": "d20",
        "field_prime": FIELD_PRIME,
        "claim": (
            "Every open A985 source sector now has a verifier fixture for the sector-local GL_d "
            "normalization equation. The fixtures are generated from the certified raw-orbital matrix "
            "units by non-identity invertible GL_d changes, solved back from raw coordinates, and "
            "checked with zero reconstruction residuals. This is a verifier atlas, not an independent "
            "source-sector off-diagonal source."
        ),
        "boundary": "No independent source-sector off-diagonal matrix-unit basis is supplied by this fixture atlas.",
        "inputs": {
            "full_matrix_unit_orbital_coo": {
                "path": rel(FULL_COO_DIR / "report.json"),
                "sha256": sha_file(FULL_COO_DIR / "report.json"),
            },
            "matrix_unit_arrays": {
                "path": rel(FULL_COO_DIR / "source_sector_matrix_units_raw_orbital_arrays.npz"),
                "sha256": sha_file(FULL_COO_DIR / "source_sector_matrix_units_raw_orbital_arrays.npz"),
            },
            "sector_normalization_obligations": {
                "path": rel(OBLIGATIONS_DIR / "report.json"),
                "sha256": sha_file(OBLIGATIONS_DIR / "report.json"),
            },
            "sector5_nontrivial_fixture": {
                "path": rel(NONTRIVIAL_FIXTURE_DIR / "report.json"),
                "sha256": sha_file(NONTRIVIAL_FIXTURE_DIR / "report.json"),
            },
            "t985_tensor": {"path": rel(TENSOR_NPZ), "sha256": sha_file(TENSOR_NPZ)},
        },
        "checks": checks,
        "derived": {
            "open_sector_count": len(summary_rows),
            "open_matrix_unit_count": sum(int(row["matrix_unit_count"]) for row in summary_rows),
            "dimension_histogram": {str(key): int(value) for key, value in sorted(dimension_histogram.items())},
            "fixture_coordinate_nonzeros": len(coordinate_nonzeros),
            "fixture_raw_nonzeros": sum(int(row["candidate_raw_nonzeros"]) for row in summary_rows),
            "raw_product_samples": sample,
            "tables": {
                "summary": rel(OUT_DIR / "open_sector_fixture_summary.csv"),
                "coordinates": rel(OUT_DIR / "open_sector_fixture_coordinate_nonzeros.csv"),
                "gl_source_and_solution": rel(OUT_DIR / "open_sector_fixture_gl_source_and_solution.csv"),
                "residuals": rel(OUT_DIR / "open_sector_fixture_solver_residuals.csv"),
            },
        },
        "next_highest_yield_item": (
            "Wire the same all-sector verifier to accept an external source-sector candidate COO file, then "
            "run it as soon as a genuine source-sector off-diagonal source exists."
        ),
        "all_checks_pass": all(checks.values()),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    manifest = {
        "schema": "d20.theorem.tiny_pointer_a985_all_open_sector_normalization_fixture_atlas_manifest.source_drop",
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
    (OUT_DIR / "all_open_sector_normalization_fixture_atlas_report.md").write_text(
        markdown_report(report),
        encoding="utf-8",
    )
    update_theorem_index(report)
    return report


def markdown_report(report: dict[str, Any]) -> str:
    checks = "\n".join(f"- `{key}`: `{value}`" for key, value in report["checks"].items())
    derived = report["derived"]
    return (
        "# All Open-Sector Normalization Fixture Atlas\n\n"
        f"Status: `{report['status']}`\n\n"
        f"Open sectors: `{derived['open_sector_count']}`\n\n"
        f"Open matrix units: `{derived['open_matrix_unit_count']}`\n\n"
        f"Coordinate nonzeros: `{derived['fixture_coordinate_nonzeros']}`\n\n"
        "## Checks\n\n"
        f"{checks}\n\n"
        f"Boundary: {report['boundary']}\n\n"
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


def verify_atlas() -> dict[str, Any]:
    report = load_json(OUT_DIR / "report.json")
    summary_rows = read_csv_rows(OUT_DIR / "open_sector_fixture_summary.csv")
    coordinate_rows = read_csv_rows(OUT_DIR / "open_sector_fixture_coordinate_nonzeros.csv")
    gl_rows_read = read_csv_rows(OUT_DIR / "open_sector_fixture_gl_source_and_solution.csv")
    residual_rows_read = read_csv_rows(OUT_DIR / "open_sector_fixture_solver_residuals.csv")
    coordinate_nonzeros = sum(int(row["coordinate_nonzeros"]) for row in summary_rows)
    checks = {
        "report_status_certified": report.get("status") == STATUS,
        "report_checks_pass": report.get("all_checks_pass") is True,
        "summary_has_30_open_sectors": len(summary_rows) == 30,
        "summary_matrix_units_sum_to_970": sum(int(row["matrix_unit_count"]) for row in summary_rows) == 970,
        "coordinate_rows_match_summary": len(coordinate_rows) == coordinate_nonzeros,
        "gl_table_nonempty": len(gl_rows_read) > 0,
        "residual_rows_match_matrix_units": len(residual_rows_read)
        == sum(int(row["matrix_unit_count"]) for row in summary_rows),
        "all_summary_residuals_zero": all(int(row["formula_residual_nonzeros"]) == 0 for row in summary_rows),
        "all_summary_diagonal_sums_preserved": all(row["diagonal_sum_preserved"] == "True" for row in summary_rows),
        "raw_product_samples_passed": report.get("derived", {}).get("raw_product_samples", {}).get("failure_count") == 0,
    }
    return {
        "status": "D20_TINY_POINTER_A985_ALL_OPEN_SECTOR_NORMALIZATION_FIXTURE_ATLAS_VERIFIED"
        if all(checks.values())
        else "D20_TINY_POINTER_A985_ALL_OPEN_SECTOR_NORMALIZATION_FIXTURE_ATLAS_VERIFY_FAILED",
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--raw-product-samples", type=int, default=512)
    parser.add_argument("--seed", type=int, default=20_260_524)
    args = parser.parse_args()
    if not args.verify_only:
        build_atlas(args.raw_product_samples, args.seed)
    verification = verify_atlas()
    print(json.dumps(verification, indent=2, sort_keys=True))
    if not verification["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

