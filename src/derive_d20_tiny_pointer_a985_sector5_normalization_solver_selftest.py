from __future__ import annotations

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

from src.derive_d20_tiny_pointer_a985_block_matrix_units import (  # noqa: E402
    FIELD_PRIME,
    RELATION_COUNT,
    MultiplicationOracle,
    array_digest,
)
from src.paths import D20_INVARIANTS, ROOT  # noqa: E402


STATUS = "D20_TINY_POINTER_A985_SECTOR5_NORMALIZATION_SOLVER_SELFTEST_CERTIFIED"
THEOREM_ID = "tiny_pointer_a985_sector5_normalization_solver_selftest"
OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

PILOT_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_sector5_normalization_pilot"
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


def inv_scalar(value: int) -> int:
    value %= FIELD_PRIME
    if value == 0:
        raise ZeroDivisionError("zero is not invertible")
    return pow(value, FIELD_PRIME - 2, FIELD_PRIME)


def rank_mod(matrix: np.ndarray) -> int:
    mat = np.asarray(matrix, dtype=np.int64).copy() % FIELD_PRIME
    rows, cols = mat.shape
    rank = 0
    for col in range(cols):
        pivot = None
        for row in range(rank, rows):
            if int(mat[row, col]) % FIELD_PRIME:
                pivot = row
                break
        if pivot is None:
            continue
        if pivot != rank:
            mat[[rank, pivot]] = mat[[pivot, rank]]
        inv = inv_scalar(int(mat[rank, col]))
        mat[rank] = (mat[rank] * inv) % FIELD_PRIME
        for row in range(rows):
            if row == rank:
                continue
            factor = int(mat[row, col])
            if factor:
                mat[row] = (mat[row] - factor * mat[rank]) % FIELD_PRIME
        rank += 1
        if rank == rows:
            break
    return rank


def inv_matrix_mod(matrix: np.ndarray) -> np.ndarray:
    mat = np.asarray(matrix, dtype=np.int64).copy() % FIELD_PRIME
    n, m = mat.shape
    if n != m:
        raise ValueError("matrix must be square")
    aug = np.concatenate([mat, np.eye(n, dtype=np.int64)], axis=1) % FIELD_PRIME
    for col in range(n):
        pivot = None
        for row in range(col, n):
            if int(aug[row, col]) % FIELD_PRIME:
                pivot = row
                break
        if pivot is None:
            raise ValueError("matrix is singular")
        if pivot != col:
            aug[[col, pivot]] = aug[[pivot, col]]
        inv = inv_scalar(int(aug[col, col]))
        aug[col] = (aug[col] * inv) % FIELD_PRIME
        for row in range(n):
            if row == col:
                continue
            factor = int(aug[row, col])
            if factor:
                aug[row] = (aug[row] - factor * aug[col]) % FIELD_PRIME
    return aug[:, n:] % FIELD_PRIME


def select_row_chart(units: np.ndarray) -> list[int]:
    rows: list[int] = []
    rank = 0
    for idx in range(units.shape[0]):
        candidate = units[[*rows, idx], :]
        candidate_rank = rank_mod(candidate)
        if candidate_rank > rank:
            rows.append(idx)
            rank = candidate_rank
            if rank == units.shape[1]:
                return rows
    raise RuntimeError("failed to select sector row chart")


def load_sector_units() -> tuple[list[dict[str, str]], np.ndarray]:
    manifest = read_csv_rows(PILOT_DIR / "sector5_current_matrix_unit_manifest.csv")
    coo_rows = read_csv_rows(PILOT_DIR / "sector5_current_matrix_unit_coo.csv")
    units = np.zeros((RELATION_COUNT, 4), dtype=np.int64)
    for row in coo_rows:
        units[int(row["relation_alpha"]), int(row["local_unit_column"])] = int(row["coefficient_mod_1000003"])
    return manifest, units % FIELD_PRIME


def self_candidate_rows(manifest: list[dict[str, str]]) -> list[dict[str, Any]]:
    coo_rows = read_csv_rows(PILOT_DIR / "sector5_current_matrix_unit_coo.csv")
    labels = {
        int(row["local_unit_column"]): f"v_sector[5;{row['i']},{row['j']}]"
        for row in manifest
    }
    out: list[dict[str, Any]] = []
    for row in coo_rows:
        out.append(
            {
                "candidate_unit_label": labels[int(row["local_unit_column"])],
                "local_unit_column": int(row["local_unit_column"]),
                "relation_alpha": int(row["relation_alpha"]),
                "coefficient_mod_1000003": int(row["coefficient_mod_1000003"]),
                "candidate_source": "SELF_CANDIDATE_FROM_CERTIFIED_SECTOR5_RAW_UNITS",
            }
        )
    return out


def candidate_vectors(candidate_rows: list[dict[str, Any]]) -> np.ndarray:
    vectors = np.zeros((RELATION_COUNT, 4), dtype=np.int64)
    for row in candidate_rows:
        vectors[int(row["relation_alpha"]), int(row["local_unit_column"])] = int(row["coefficient_mod_1000003"])
    return vectors % FIELD_PRIME


def coordinate_columns(units: np.ndarray, vectors: np.ndarray) -> tuple[list[int], np.ndarray]:
    chart_rows = select_row_chart(units)
    chart = units[chart_rows, :]
    inv_chart = inv_matrix_mod(chart)
    coords = (inv_chart @ vectors[chart_rows, :]) % FIELD_PRIME
    return chart_rows, coords


def coord_matrix(coords: np.ndarray, target_i: int, target_j: int) -> np.ndarray:
    col = coords[:, target_i * 2 + target_j] % FIELD_PRIME
    return np.array([[col[0], col[1]], [col[2], col[3]]], dtype=np.int64)


def solve_gl2(coords: np.ndarray) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    m00 = coord_matrix(coords, 0, 0)
    m01 = coord_matrix(coords, 0, 1)
    m10 = coord_matrix(coords, 1, 0)
    pivot = None
    for row in range(2):
        for col in range(2):
            if int(m00[row, col]) % FIELD_PRIME:
                pivot = (row, col)
                break
        if pivot is not None:
            break
    if pivot is None:
        raise ValueError("candidate v[0,0] has no nonzero pivot")
    pivot_row, pivot_col = pivot
    pivot_value = int(m00[pivot_row, pivot_col])
    inv_pivot = inv_scalar(pivot_value)
    first_col = m00[:, pivot_col] % FIELD_PRIME
    first_row = (m00[pivot_row, :] * inv_pivot) % FIELD_PRIME
    second_col = m10[:, pivot_col] % FIELD_PRIME
    second_row = (m01[pivot_row, :] * inv_pivot) % FIELD_PRIME
    g = np.stack([first_col, second_col], axis=1) % FIELD_PRIME
    ginv = np.stack([first_row, second_row], axis=0) % FIELD_PRIME
    meta = {
        "pivot_row": int(pivot_row),
        "pivot_col": int(pivot_col),
        "pivot_value": pivot_value,
    }
    return g, ginv, meta


def formula_coords(g: np.ndarray, ginv: np.ndarray) -> np.ndarray:
    out = np.zeros((4, 4), dtype=np.int64)
    for target_i in range(2):
        for target_j in range(2):
            col = target_i * 2 + target_j
            for source_a in range(2):
                for source_b in range(2):
                    row = source_a * 2 + source_b
                    out[row, col] = (int(g[source_a, target_i]) * int(ginv[target_j, source_b])) % FIELD_PRIME
    return out


def verify_raw_matrix_unit_law(vectors: np.ndarray) -> dict[str, Any]:
    triples = np.asarray(np.load(TENSOR_NPZ)["triples"], dtype=np.int64)
    oracle = MultiplicationOracle(triples)
    zero = np.zeros(RELATION_COUNT, dtype=np.int64)
    failures: list[dict[str, int]] = []
    checked = 0
    for i in range(2):
        for j in range(2):
            left_col = i * 2 + j
            for k in range(2):
                for ell in range(2):
                    right_col = k * 2 + ell
                    product = oracle.product(vectors[:, left_col], vectors[:, right_col])
                    target = vectors[:, i * 2 + ell] if j == k else zero
                    checked += 1
                    if not np.array_equal(product % FIELD_PRIME, target % FIELD_PRIME):
                        failures.append({"left_i": i, "left_j": j, "right_i": k, "right_j": ell})
    return {"checked": checked, "failure_count": len(failures), "failures": failures}


def write_outputs(
    candidate_rows: list[dict[str, Any]],
    coords: np.ndarray,
    chart_rows: list[int],
    g: np.ndarray,
    ginv: np.ndarray,
    residuals: list[dict[str, Any]],
) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(
        OUT_DIR / "sector5_self_candidate_units.csv",
        [
            "candidate_unit_label",
            "local_unit_column",
            "relation_alpha",
            "coefficient_mod_1000003",
            "candidate_source",
        ],
        candidate_rows,
    )
    coordinate_rows: list[dict[str, Any]] = []
    for target_col in range(4):
        target_i, target_j = divmod(target_col, 2)
        for source_col in range(4):
            value = int(coords[source_col, target_col])
            if value == 0:
                continue
            source_i, source_j = divmod(source_col, 2)
            coordinate_rows.append(
                {
                    "candidate_unit_label": f"v_sector[5;{target_i},{target_j}]",
                    "target_i": target_i,
                    "target_j": target_j,
                    "source_i": source_i,
                    "source_j": source_j,
                    "coefficient_mod_1000003": value,
                }
            )
    write_csv_rows(
        OUT_DIR / "sector5_self_candidate_coordinates.csv",
        [
            "candidate_unit_label",
            "target_i",
            "target_j",
            "source_i",
            "source_j",
            "coefficient_mod_1000003",
        ],
        coordinate_rows,
    )
    solution_rows = [
        {"variable": f"g[{i},{j}]", "value_mod_1000003": int(g[i, j])}
        for i in range(2)
        for j in range(2)
    ] + [
        {"variable": f"ginv[{i},{j}]", "value_mod_1000003": int(ginv[i, j])}
        for i in range(2)
        for j in range(2)
    ] + [
        {
            "variable": "det_g",
            "value_mod_1000003": int((g[0, 0] * g[1, 1] - g[0, 1] * g[1, 0]) % FIELD_PRIME),
        }
    ]
    write_csv_rows(OUT_DIR / "sector5_gl2_solution.csv", ["variable", "value_mod_1000003"], solution_rows)
    write_csv_rows(
        OUT_DIR / "sector5_solver_residuals.csv",
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
        OUT_DIR / "sector5_row_chart.json",
        {
            "schema": "d20.tiny_pointer.a985.sector5_solver_row_chart@1",
            "field_prime": FIELD_PRIME,
            "selected_relation_rows": chart_rows,
        },
    )


def markdown_report(report: dict[str, Any]) -> str:
    checks = "\n".join(f"- `{key}`: `{value}`" for key, value in report["checks"].items())
    return (
        "# Sector 5 Normalization Solver Self-Test\n\n"
        f"Status: `{report['status']}`\n\n"
        "This proves the GL2 solver and raw-coordinate verifier on a controlled self-candidate. "
        "The candidate is the already certified sector-5 raw matrix-unit chart, so this is an "
        "executable normalization path, not an independent source-sector-basis solution.\n\n"
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


def build_selftest() -> dict[str, Any]:
    pilot_report = load_json(PILOT_DIR / "report.json")
    manifest, units = load_sector_units()
    candidate_rows = self_candidate_rows(manifest)
    candidates = candidate_vectors(candidate_rows)
    chart_rows, coords = coordinate_columns(units, candidates)
    g, ginv, solve_meta = solve_gl2(coords)
    expected_coords = formula_coords(g, ginv)
    reconstructed = (units @ expected_coords) % FIELD_PRIME
    residual = (candidates - reconstructed) % FIELD_PRIME
    residual_rows: list[dict[str, Any]] = []
    for col in range(4):
        target_i, target_j = divmod(col, 2)
        col_residual = residual[:, col]
        residual_rows.append(
            {
                "candidate_unit_label": f"v_sector[5;{target_i},{target_j}]",
                "target_i": target_i,
                "target_j": target_j,
                "max_residual_mod_1000003": int(np.max(col_residual)),
                "nonzero_residual_count": int(np.count_nonzero(col_residual)),
            }
        )
    product_check = verify_raw_matrix_unit_law(candidates)
    write_outputs(candidate_rows, coords, chart_rows, g, ginv, residual_rows)

    identity = np.eye(2, dtype=np.int64)
    checks = {
        "pilot_certified": pilot_report.get("status")
        == "D20_TINY_POINTER_A985_SECTOR5_NORMALIZATION_PILOT_CERTIFIED"
        and pilot_report.get("all_checks_pass") is True,
        "self_candidate_has_144_coo_rows": len(candidate_rows) == 144,
        "row_chart_has_4_rows": len(chart_rows) == 4,
        "coordinate_matrix_is_identity": bool(np.array_equal(coords % FIELD_PRIME, np.eye(4, dtype=np.int64))),
        "gl2_solution_g_is_identity": bool(np.array_equal(g % FIELD_PRIME, identity)),
        "gl2_solution_ginv_is_identity": bool(np.array_equal(ginv % FIELD_PRIME, identity)),
        "gl2_left_inverse_holds": bool(np.array_equal((ginv @ g) % FIELD_PRIME, identity)),
        "gl2_right_inverse_holds": bool(np.array_equal((g @ ginv) % FIELD_PRIME, identity)),
        "formula_reconstructs_candidate": bool(np.array_equal(reconstructed, candidates)),
        "solver_residuals_zero": all(row["nonzero_residual_count"] == 0 for row in residual_rows),
        "candidate_raw_matrix_unit_law_exhaustive": product_check["checked"] == 16
        and product_check["failure_count"] == 0,
    }
    report = {
        "schema": "d20.theorem.tiny_pointer_a985_sector5_normalization_solver_selftest.source_drop",
        "status": STATUS if all(checks.values()) else "D20_TINY_POINTER_A985_SECTOR5_NORMALIZATION_SOLVER_SELFTEST_NEEDS_REVIEW",
        "object": "d20",
        "field_prime": FIELD_PRIME,
        "claim": (
            "The sector-5 GL2 normalization solver path is executable and verified on a controlled "
            "self-candidate. The self-candidate is the current certified raw matrix-unit chart, so "
            "the solved transform is the identity; this is not an independent source-sector off-diagonal "
            "basis certification."
        ),
        "inputs": {
            "sector5_normalization_pilot": {
                "path": rel(PILOT_DIR / "report.json"),
                "sha256": sha_file(PILOT_DIR / "report.json"),
            },
            "sector5_candidate_schema": {
                "path": rel(PILOT_DIR / "sector5_candidate_input_schema.json"),
                "sha256": sha_file(PILOT_DIR / "sector5_candidate_input_schema.json"),
            },
            "t985_tensor": {"path": rel(TENSOR_NPZ), "sha256": sha_file(TENSOR_NPZ)},
        },
        "checks": checks,
        "derived": {
            "candidate_source": "SELF_CANDIDATE_FROM_CERTIFIED_SECTOR5_RAW_UNITS",
            "candidate_coo_rows": len(candidate_rows),
            "selected_relation_rows": chart_rows,
            "coordinate_matrix_sha256": array_digest(coords),
            "gl2_solution": {
                "g": g.astype(int).tolist(),
                "ginv": ginv.astype(int).tolist(),
                "det_g": int((g[0, 0] * g[1, 1] - g[0, 1] * g[1, 0]) % FIELD_PRIME),
                **solve_meta,
            },
            "raw_product_check": product_check,
            "candidate_units_sha256": array_digest(candidates),
            "reconstructed_units_sha256": array_digest(reconstructed),
            "tables": {
                "self_candidate": rel(OUT_DIR / "sector5_self_candidate_units.csv"),
                "coordinates": rel(OUT_DIR / "sector5_self_candidate_coordinates.csv"),
                "gl2_solution": rel(OUT_DIR / "sector5_gl2_solution.csv"),
                "residuals": rel(OUT_DIR / "sector5_solver_residuals.csv"),
                "row_chart": rel(OUT_DIR / "sector5_row_chart.json"),
            },
        },
        "next_highest_yield_item": (
            "Run this solver against a non-self sector-5 candidate source, or derive such a candidate "
            "from an upstream source-sector off-diagonal construction."
        ),
        "all_checks_pass": all(checks.values()),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    manifest_payload = {
        "schema": "d20.theorem.tiny_pointer_a985_sector5_normalization_solver_selftest_manifest.source_drop",
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
    manifest_payload["manifest_sha256"] = sha_json(
        {k: v for k, v in manifest_payload.items() if k != "manifest_sha256"}
    )
    write_json(OUT_DIR / "report.json", report)
    write_json(OUT_DIR / "manifest.json", manifest_payload)
    (OUT_DIR / "sector5_normalization_solver_selftest_report.md").write_text(markdown_report(report), encoding="utf-8")
    update_theorem_index(report)
    return report


def verify_selftest() -> dict[str, Any]:
    report = load_json(OUT_DIR / "report.json")
    candidate_rows = read_csv_rows(OUT_DIR / "sector5_self_candidate_units.csv")
    coord_rows = read_csv_rows(OUT_DIR / "sector5_self_candidate_coordinates.csv")
    solution_rows = read_csv_rows(OUT_DIR / "sector5_gl2_solution.csv")
    residual_rows = read_csv_rows(OUT_DIR / "sector5_solver_residuals.csv")
    chart = load_json(OUT_DIR / "sector5_row_chart.json")
    checks = {
        "report_status_certified": report.get("status") == STATUS,
        "report_checks_pass": report.get("all_checks_pass") is True,
        "self_candidate_has_144_rows": len(candidate_rows) == 144,
        "identity_coordinate_rows_have_4_nonzero_entries": len(coord_rows) == 4,
        "solution_has_9_rows": len(solution_rows) == 9,
        "residuals_have_4_rows": len(residual_rows) == 4,
        "all_residuals_zero": all(int(row["nonzero_residual_count"]) == 0 for row in residual_rows),
        "row_chart_has_4_rows": len(chart.get("selected_relation_rows", [])) == 4,
    }
    return {
        "status": "D20_TINY_POINTER_A985_SECTOR5_NORMALIZATION_SOLVER_SELFTEST_VERIFIED"
        if all(checks.values())
        else "D20_TINY_POINTER_A985_SECTOR5_NORMALIZATION_SOLVER_SELFTEST_VERIFY_FAILED",
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if not args.verify_only:
        build_selftest()
    verification = verify_selftest()
    print(json.dumps(verification, indent=2, sort_keys=True))
    if not verification["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

