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


STATUS = "D20_TINY_POINTER_A985_SECTOR5_NORMALIZATION_PILOT_CERTIFIED"
THEOREM_ID = "tiny_pointer_a985_sector5_normalization_pilot"
OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

TARGET_LEGACY_SECTOR = 5
FULL_COO_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_full_matrix_unit_orbital_coo"
NORMALIZATION_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_sector_normalization_obligations"
CENTRAL_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_orbital_central_idempotents"
FULL_A985_LIFT = ROOT / "layers" / "drinfeld" / "full_a985_lift.json"
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


def load_target_obligation() -> dict[str, str]:
    rows = read_csv_rows(NORMALIZATION_DIR / "sector_local_normalization_obligations.csv")
    for row in rows:
        if int(row["legacy_sector"]) == TARGET_LEGACY_SECTOR:
            return row
    raise RuntimeError(f"missing sector {TARGET_LEGACY_SECTOR} normalization row")


def legacy_lift_has_matrix_unit_basis() -> bool:
    text = FULL_A985_LIFT.read_text(encoding="utf-8").lower()
    return "matrix_unit" in text or "matrix-unit" in text


def extract_sector_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]], np.ndarray]:
    manifest = read_csv_rows(FULL_COO_DIR / "legacy_matrix_units_orbital_manifest.csv")
    coo = read_csv_rows(FULL_COO_DIR / "legacy_matrix_units_orbital_coo.csv")
    sector_manifest = [
        row for row in manifest if int(row["legacy_sector"]) == TARGET_LEGACY_SECTOR
    ]
    sector_manifest.sort(key=lambda row: (int(row["i"]), int(row["j"])))
    unit_columns = {int(row["unit_column"]) for row in sector_manifest}
    sector_coo = [row for row in coo if int(row["unit_column"]) in unit_columns]

    arrays = np.load(FULL_COO_DIR / "legacy_matrix_units_raw_orbital_arrays.npz")
    matrix_units = np.asarray(arrays["matrix_units"], dtype=np.int64) % FIELD_PRIME
    sector_matrix_units = matrix_units[:, [int(row["unit_column"]) for row in sector_manifest]]
    manifest_rows: list[dict[str, Any]] = []
    for local_column, row in enumerate(sector_manifest):
        manifest_rows.append(
            {
                "local_unit_column": local_column,
                "full_unit_column": int(row["unit_column"]),
                "legacy_sector": int(row["legacy_sector"]),
                "raw_sector": int(row["raw_sector"]),
                "block_dimension": int(row["block_dimension"]),
                "i": int(row["i"]),
                "j": int(row["j"]),
                "legacy_matrix_unit_label": row["legacy_matrix_unit_label"],
                "raw_matrix_unit_label": row["raw_matrix_unit_label"],
                "coefficient_source": row["coefficient_source"],
                "nonzero_coefficients": int(row["nonzero_coefficients"]),
            }
        )
    coo_rows: list[dict[str, Any]] = []
    full_to_local = {row["full_unit_column"]: row["local_unit_column"] for row in manifest_rows}
    for row in sector_coo:
        coo_rows.append(
            {
                "local_unit_column": full_to_local[int(row["unit_column"])],
                "full_unit_column": int(row["unit_column"]),
                "legacy_sector": int(row["legacy_sector"]),
                "raw_sector": int(row["raw_sector"]),
                "i": int(row["i"]),
                "j": int(row["j"]),
                "relation_alpha": int(row["relation_alpha"]),
                "coefficient_mod_1000003": int(row["coefficient_mod_1000003"]),
                "coefficient_source": row["coefficient_source"],
            }
        )
    coo_rows.sort(key=lambda row: (row["local_unit_column"], row["relation_alpha"]))
    return manifest_rows, coo_rows, sector_matrix_units


def verify_matrix_unit_law(sector_units: np.ndarray) -> dict[str, Any]:
    triples = np.asarray(np.load(TENSOR_NPZ)["triples"], dtype=np.int64)
    oracle = MultiplicationOracle(triples)
    zero = np.zeros(RELATION_COUNT, dtype=np.int64)
    failures: list[dict[str, int]] = []
    checked = 0
    dimension = 2
    for i in range(dimension):
        for j in range(dimension):
            left_col = i * dimension + j
            for k in range(dimension):
                for ell in range(dimension):
                    right_col = k * dimension + ell
                    product = oracle.product(sector_units[:, left_col], sector_units[:, right_col])
                    target = sector_units[:, i * dimension + ell] if j == k else zero
                    checked += 1
                    if not np.array_equal(product % FIELD_PRIME, target % FIELD_PRIME):
                        failures.append(
                            {
                                "left_i": i,
                                "left_j": j,
                                "right_i": k,
                                "right_j": ell,
                            }
                        )
    return {"checked": checked, "failure_count": len(failures), "failures": failures}


def verify_diagonal_sum(sector_units: np.ndarray, raw_sector: int) -> bool:
    z = np.load(CENTRAL_DIR / "a985_center_and_primitive_central_idempotents.npz")
    central_pages = np.asarray(z["idempotents"], dtype=np.int64) % FIELD_PRIME
    diagonal_sum = (sector_units[:, 0] + sector_units[:, 3]) % FIELD_PRIME
    return bool(np.array_equal(diagonal_sum, central_pages[raw_sector] % FIELD_PRIME))


def gl2_terms() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for target_i in range(2):
        for target_j in range(2):
            for source_a in range(2):
                for source_b in range(2):
                    rows.append(
                        {
                            "legacy_sector": TARGET_LEGACY_SECTOR,
                            "target_i": target_i,
                            "target_j": target_j,
                            "source_a": source_a,
                            "source_b": source_b,
                            "coefficient_symbol": f"g[{source_a},{target_i}]*ginv[{target_j},{source_b}]",
                            "source_matrix_unit_label": f"u_legacy[{TARGET_LEGACY_SECTOR};{source_a},{source_b}]",
                            "target_matrix_unit_label": f"v_legacy[{TARGET_LEGACY_SECTOR};{target_i},{target_j}]",
                        }
                    )
    return rows


def gl2_constraints() -> list[dict[str, Any]]:
    constraints = [
        ("left_inverse_00", "ginv[0,0]*g[0,0] + ginv[0,1]*g[1,0] - 1 = 0"),
        ("left_inverse_01", "ginv[0,0]*g[0,1] + ginv[0,1]*g[1,1] = 0"),
        ("left_inverse_10", "ginv[1,0]*g[0,0] + ginv[1,1]*g[1,0] = 0"),
        ("left_inverse_11", "ginv[1,0]*g[0,1] + ginv[1,1]*g[1,1] - 1 = 0"),
        ("right_inverse_00", "g[0,0]*ginv[0,0] + g[0,1]*ginv[1,0] - 1 = 0"),
        ("right_inverse_01", "g[0,0]*ginv[0,1] + g[0,1]*ginv[1,1] = 0"),
        ("right_inverse_10", "g[1,0]*ginv[0,0] + g[1,1]*ginv[1,0] = 0"),
        ("right_inverse_11", "g[1,0]*ginv[0,1] + g[1,1]*ginv[1,1] - 1 = 0"),
        ("determinant_nonzero", "det_g = g[0,0]*g[1,1] - g[0,1]*g[1,0] != 0"),
    ]
    return [
        {
            "legacy_sector": TARGET_LEGACY_SECTOR,
            "constraint_name": name,
            "constraint": formula,
        }
        for name, formula in constraints
    ]


def candidate_schema() -> dict[str, Any]:
    return {
        "schema": "d20.tiny_pointer.a985.sector5_legacy_matrix_unit_candidate@1",
        "required_field_prime": FIELD_PRIME,
        "legacy_sector": TARGET_LEGACY_SECTOR,
        "block_dimension": 2,
        "required_candidate_units": [
            "v_legacy[5;0,0]",
            "v_legacy[5;0,1]",
            "v_legacy[5;1,0]",
            "v_legacy[5;1,1]",
        ],
        "accepted_format": (
            "CSV rows with columns candidate_unit_label, relation_alpha, coefficient_mod_1000003"
        ),
        "normalization_equation": (
            "candidate v[i,j] must equal sum_{a,b} g[a,i] * ginv[j,b] * u[a,b] "
            "for an invertible 2x2 matrix g over F_1000003"
        ),
        "current_raw_unit_source": rel(FULL_COO_DIR / "legacy_matrix_units_orbital_coo.csv"),
    }


def write_outputs(
    manifest_rows: list[dict[str, Any]],
    coo_rows: list[dict[str, Any]],
    terms: list[dict[str, Any]],
    constraints: list[dict[str, Any]],
    schema: dict[str, Any],
) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(
        OUT_DIR / "sector5_current_matrix_unit_manifest.csv",
        [
            "local_unit_column",
            "full_unit_column",
            "legacy_sector",
            "raw_sector",
            "block_dimension",
            "i",
            "j",
            "legacy_matrix_unit_label",
            "raw_matrix_unit_label",
            "coefficient_source",
            "nonzero_coefficients",
        ],
        manifest_rows,
    )
    write_csv_rows(
        OUT_DIR / "sector5_current_matrix_unit_coo.csv",
        [
            "local_unit_column",
            "full_unit_column",
            "legacy_sector",
            "raw_sector",
            "i",
            "j",
            "relation_alpha",
            "coefficient_mod_1000003",
            "coefficient_source",
        ],
        coo_rows,
    )
    write_csv_rows(
        OUT_DIR / "sector5_gl2_change_of_basis_terms.csv",
        [
            "legacy_sector",
            "target_i",
            "target_j",
            "source_a",
            "source_b",
            "coefficient_symbol",
            "source_matrix_unit_label",
            "target_matrix_unit_label",
        ],
        terms,
    )
    write_csv_rows(
        OUT_DIR / "sector5_gl2_constraints.csv",
        ["legacy_sector", "constraint_name", "constraint"],
        constraints,
    )
    write_json(OUT_DIR / "sector5_candidate_input_schema.json", schema)


def markdown_report(report: dict[str, Any]) -> str:
    checks = "\n".join(f"- `{key}`: `{value}`" for key, value in report["checks"].items())
    return (
        "# Sector 5 Normalization Pilot\n\n"
        f"Status: `{report['status']}`\n\n"
        "This isolates the first minimum-dimension open sector. It certifies the current raw-orbital "
        "matrix units and emits the GL2 normalization equation needed to compare a genuine legacy "
        "off-diagonal basis when one is supplied.\n\n"
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


def build_sector5_pilot() -> dict[str, Any]:
    normalization_report = load_json(NORMALIZATION_DIR / "report.json")
    full_coo_report = load_json(FULL_COO_DIR / "report.json")
    obligation = load_target_obligation()
    manifest_rows, coo_rows, sector_units = extract_sector_rows()
    raw_sector = int(obligation["raw_sector"])
    product_check = verify_matrix_unit_law(sector_units)
    diagonal_sum_ok = verify_diagonal_sum(sector_units, raw_sector)
    terms = gl2_terms()
    constraints = gl2_constraints()
    schema = candidate_schema()
    write_outputs(manifest_rows, coo_rows, terms, constraints, schema)

    checks = {
        "normalization_obligations_certified": normalization_report.get("status")
        == "D20_TINY_POINTER_A985_SECTOR_NORMALIZATION_OBLIGATIONS_CERTIFIED"
        and normalization_report.get("all_checks_pass") is True,
        "full_matrix_unit_coo_certified": full_coo_report.get("status")
        == "D20_TINY_POINTER_A985_FULL_MATRIX_UNIT_ORBITAL_COO_CERTIFIED"
        and full_coo_report.get("all_checks_pass") is True,
        "target_sector_is_5": int(obligation["legacy_sector"]) == TARGET_LEGACY_SECTOR,
        "target_sector_is_open": obligation["normalization_status"] == "OPEN_GL_BLOCK_NORMALIZATION",
        "target_sector_has_min_open_dimension_two": int(obligation["block_dimension"]) == 2,
        "legacy_lift_has_no_matrix_unit_basis": not legacy_lift_has_matrix_unit_basis(),
        "current_manifest_has_4_units": len(manifest_rows) == 4,
        "current_coo_rows_match_manifest_nonzeros": len(coo_rows)
        == sum(int(row["nonzero_coefficients"]) for row in manifest_rows),
        "sector_units_array_shape_is_985_by_4": list(sector_units.shape) == [RELATION_COUNT, 4],
        "sector5_matrix_unit_law_exhaustive": product_check["checked"] == 16
        and product_check["failure_count"] == 0,
        "sector5_diagonal_sum_equals_central_page": diagonal_sum_ok,
        "gl2_change_of_basis_has_16_terms": len(terms) == 16,
        "gl2_constraints_have_9_rows": len(constraints) == 9,
    }
    report = {
        "schema": "d20.theorem.tiny_pointer_a985_sector5_normalization_pilot.source_drop",
        "status": STATUS if all(checks.values()) else "D20_TINY_POINTER_A985_SECTOR5_NORMALIZATION_PILOT_NEEDS_REVIEW",
        "object": "d20",
        "field_prime": FIELD_PRIME,
        "claim": (
            "Legacy sector 5 is isolated as the first minimum-dimension open block. Its current "
            "raw-orbital matrix units are exhaustively certified, and the exact GL2/scalar "
            "normalization interface is emitted. This does not claim a legacy off-diagonal basis "
            "has been supplied; it defines the verifier-ready equation for one."
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
            "central_idempotents": {
                "path": rel(CENTRAL_DIR / "a985_center_and_primitive_central_idempotents.npz"),
                "sha256": sha_file(CENTRAL_DIR / "a985_center_and_primitive_central_idempotents.npz"),
            },
            "full_a985_lift": {
                "path": rel(FULL_A985_LIFT),
                "sha256": sha_file(FULL_A985_LIFT),
            },
            "t985_tensor": {"path": rel(TENSOR_NPZ), "sha256": sha_file(TENSOR_NPZ)},
        },
        "checks": checks,
        "derived": {
            "target_legacy_sector": TARGET_LEGACY_SECTOR,
            "target_raw_sector": raw_sector,
            "block_dimension": int(obligation["block_dimension"]),
            "current_matrix_unit_rows": len(manifest_rows),
            "current_matrix_unit_coo_rows": len(coo_rows),
            "current_matrix_units_sha256": array_digest(sector_units),
            "raw_product_check": product_check,
            "remaining_projective_gauge_dimension": int(obligation["remaining_projective_gauge_dimension"]),
            "gl2_change_of_basis_terms": len(terms),
            "gl2_constraints": len(constraints),
            "candidate_schema": rel(OUT_DIR / "sector5_candidate_input_schema.json"),
            "tables": {
                "current_manifest": rel(OUT_DIR / "sector5_current_matrix_unit_manifest.csv"),
                "current_coo": rel(OUT_DIR / "sector5_current_matrix_unit_coo.csv"),
                "gl2_terms": rel(OUT_DIR / "sector5_gl2_change_of_basis_terms.csv"),
                "gl2_constraints": rel(OUT_DIR / "sector5_gl2_constraints.csv"),
            },
        },
        "next_highest_yield_item": (
            "Supply four candidate legacy sector-5 matrix units in the candidate schema, then solve "
            "for the GL2 variables and verify equality in raw-orbital coordinates."
        ),
        "all_checks_pass": all(checks.values()),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    manifest = {
        "schema": "d20.theorem.tiny_pointer_a985_sector5_normalization_pilot_manifest.source_drop",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(OUT_DIR / "manifest.json"),
            "report": rel(OUT_DIR / "report.json"),
            "candidate_schema": rel(OUT_DIR / "sector5_candidate_input_schema.json"),
            **report["derived"]["tables"],
        },
        "validation_tests": list(checks),
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = sha_json({k: v for k, v in manifest.items() if k != "manifest_sha256"})
    write_json(OUT_DIR / "report.json", report)
    write_json(OUT_DIR / "manifest.json", manifest)
    (OUT_DIR / "sector5_normalization_pilot_report.md").write_text(markdown_report(report), encoding="utf-8")
    update_theorem_index(report)
    return report


def verify_sector5_pilot() -> dict[str, Any]:
    report = load_json(OUT_DIR / "report.json")
    manifest_rows = read_csv_rows(OUT_DIR / "sector5_current_matrix_unit_manifest.csv")
    coo_rows = read_csv_rows(OUT_DIR / "sector5_current_matrix_unit_coo.csv")
    terms = read_csv_rows(OUT_DIR / "sector5_gl2_change_of_basis_terms.csv")
    constraints = read_csv_rows(OUT_DIR / "sector5_gl2_constraints.csv")
    schema = load_json(OUT_DIR / "sector5_candidate_input_schema.json")
    checks = {
        "report_status_certified": report.get("status") == STATUS,
        "report_checks_pass": report.get("all_checks_pass") is True,
        "manifest_has_4_rows": len(manifest_rows) == 4,
        "coo_rows_match_report": len(coo_rows) == report.get("derived", {}).get("current_matrix_unit_coo_rows"),
        "gl2_terms_have_16_rows": len(terms) == 16,
        "gl2_constraints_have_9_rows": len(constraints) == 9,
        "candidate_schema_targets_sector5": schema.get("legacy_sector") == TARGET_LEGACY_SECTOR,
        "candidate_schema_requires_4_units": len(schema.get("required_candidate_units", [])) == 4,
    }
    return {
        "status": "D20_TINY_POINTER_A985_SECTOR5_NORMALIZATION_PILOT_VERIFIED"
        if all(checks.values())
        else "D20_TINY_POINTER_A985_SECTOR5_NORMALIZATION_PILOT_VERIFY_FAILED",
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if not args.verify_only:
        build_sector5_pilot()
    verification = verify_sector5_pilot()
    print(json.dumps(verification, indent=2, sort_keys=True))
    if not verification["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
