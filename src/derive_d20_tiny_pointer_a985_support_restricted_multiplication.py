from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import defaultdict
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
)
from src.paths import D20_INVARIANTS, ROOT  # noqa: E402


STATUS = "D20_TINY_POINTER_A985_SUPPORT_RESTRICTED_MULTIPLICATION_TABLES_CERTIFIED"
THEOREM_ID = "tiny_pointer_a985_support_restricted_multiplication_tables"
OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FULL_MATCH_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_full_sector_match"
SUPPORT_COO_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_support_full_matrix_unit_orbital_coo"
CENTRAL_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_orbital_central_idempotents"
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


def array_digest(array: np.ndarray) -> str:
    arr = np.asarray(array, dtype=np.int64)
    h = hashlib.sha256()
    h.update(str(arr.shape).encode("ascii"))
    h.update(arr.tobytes(order="C"))
    return h.hexdigest()


def load_source_maps() -> tuple[dict[int, int], dict[int, int]]:
    rows = read_csv_rows(FULL_MATCH_DIR / "source_to_raw_sector_full_match.csv")
    source_to_raw = {int(row["source_sector"]): int(row["raw_sector"]) for row in rows}
    dimensions = {int(row["source_sector"]): int(row["block_dimension"]) for row in rows}
    return source_to_raw, dimensions


def load_central_pages() -> tuple[np.ndarray, np.ndarray]:
    z = np.load(CENTRAL_DIR / "a985_center_and_primitive_central_idempotents.npz")
    pages = np.asarray(z["idempotents"], dtype=np.int64) % FIELD_PRIME
    identity_indices = np.asarray(z["identity_indices"], dtype=np.int64)
    return pages, identity_indices


def central_sum(source_set: set[int], central_pages: np.ndarray, source_to_raw: dict[int, int]) -> np.ndarray:
    out = np.zeros(RELATION_COUNT, dtype=np.int64)
    for source_sector in sorted(source_set):
        out += central_pages[source_to_raw[source_sector]]
    return out % FIELD_PRIME


def group_support_rows(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["support_name"]].append(row)
    for support_rows in grouped.values():
        support_rows.sort(key=lambda row: int(row["support_unit_row"]))
    return dict(grouped)


def build_basis_manifest(
    support_rows_by_name: dict[str, list[dict[str, str]]],
    projector_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    projector_by_name = {row["support_name"]: row for row in projector_rows}
    for projector in projector_rows:
        support_name = projector["support_name"]
        for support_basis_index, row in enumerate(support_rows_by_name.get(support_name, [])):
            out.append(
                {
                    "support_name": support_name,
                    "projector_column": int(projector["projector_column"]),
                    "support_basis_index": support_basis_index,
                    "support_unit_row": int(row["support_unit_row"]),
                    "source_support": projector_by_name[support_name]["source_support"],
                    "transported_source_support": projector_by_name[support_name]["transported_source_support"],
                    "source_sector": int(row["source_sector"]),
                    "raw_sector": int(row["raw_sector"]),
                    "block_dimension": int(row["block_dimension"]),
                    "i": int(row["i"]),
                    "j": int(row["j"]),
                    "full_unit_column": int(row["full_unit_column"]),
                    "source_matrix_unit_label": row["source_matrix_unit_label"],
                    "raw_matrix_unit_label": row["raw_matrix_unit_label"],
                    "coefficient_source": row["coefficient_source"],
                }
            )
    return out


def build_matrix_unit_tables(
    support_rows_by_name: dict[str, list[dict[str, str]]],
    projector_rows: list[dict[str, str]],
    dimensions: dict[int, int],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    product_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []

    for projector in projector_rows:
        support_name = projector["support_name"]
        support_rows = support_rows_by_name.get(support_name, [])
        local_by_key = {
            (int(row["source_sector"]), int(row["i"]), int(row["j"])): idx
            for idx, row in enumerate(support_rows)
        }
        rows_by_sector: dict[int, list[dict[str, str]]] = defaultdict(list)
        for row in support_rows:
            rows_by_sector[int(row["source_sector"])].append(row)

        nonzero_start = len(product_rows)
        for source_sector in sorted(rows_by_sector):
            dimension = dimensions[source_sector]
            for i in range(dimension):
                for j in range(dimension):
                    left_idx = local_by_key[(source_sector, i, j)]
                    left_row = support_rows[left_idx]
                    for ell in range(dimension):
                        right_idx = local_by_key[(source_sector, j, ell)]
                        result_idx = local_by_key[(source_sector, i, ell)]
                        right_row = support_rows[right_idx]
                        result_row = support_rows[result_idx]
                        product_rows.append(
                            {
                                "support_name": support_name,
                                "projector_column": int(projector["projector_column"]),
                                "source_sector": source_sector,
                                "raw_sector": int(left_row["raw_sector"]),
                                "left_support_basis_index": left_idx,
                                "right_support_basis_index": right_idx,
                                "result_support_basis_index": result_idx,
                                "left_support_unit_row": int(left_row["support_unit_row"]),
                                "right_support_unit_row": int(right_row["support_unit_row"]),
                                "result_support_unit_row": int(result_row["support_unit_row"]),
                                "left_i": i,
                                "left_j": j,
                                "right_i": j,
                                "right_j": ell,
                                "result_i": i,
                                "result_j": ell,
                                "coefficient_mod_1000003": 1,
                                "left_label": left_row["source_matrix_unit_label"],
                                "right_label": right_row["source_matrix_unit_label"],
                                "result_label": result_row["source_matrix_unit_label"],
                            }
                        )

        source_set = parse_set(projector["transported_source_support"])
        expected_basis = sum(dimensions[sector] ** 2 for sector in source_set)
        expected_products = sum(dimensions[sector] ** 3 for sector in source_set)
        nonzero_count = len(product_rows) - nonzero_start
        summary_rows.append(
            {
                "support_name": support_name,
                "projector_column": int(projector["projector_column"]),
                "transported_source_support": projector["transported_source_support"],
                "basis_rows": len(support_rows),
                "expected_basis_rows": expected_basis,
                "nonzero_products": nonzero_count,
                "expected_nonzero_products": expected_products,
                "zero_products": len(support_rows) * len(support_rows) - nonzero_count,
                "symbolic_table_complete": len(support_rows) == expected_basis and nonzero_count == expected_products,
            }
        )
    return product_rows, summary_rows


def matrix_unit_target(
    left: dict[str, str],
    right: dict[str, str],
    local_by_key: dict[tuple[int, int, int], int],
) -> int | None:
    left_sector = int(left["source_sector"])
    right_sector = int(right["source_sector"])
    if left_sector != right_sector or int(left["j"]) != int(right["i"]):
        return None
    return local_by_key[(left_sector, int(left["i"]), int(right["j"]))]


def verify_direct_products(
    support_rows_by_name: dict[str, list[dict[str, str]]],
    support_names: list[str],
    support_arrays: np.ndarray,
    max_exhaustive_basis: int,
    top_sample_products: int,
    seed: int,
) -> dict[str, Any]:
    triples = np.asarray(np.load(TENSOR_NPZ)["triples"], dtype=np.int64)
    oracle = MultiplicationOracle(triples)
    rng = np.random.default_rng(seed)
    zero = np.zeros(RELATION_COUNT, dtype=np.int64)
    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    checked_total = 0

    for support_name in support_names:
        support_rows = support_rows_by_name.get(support_name, [])
        local_by_key = {
            (int(row["source_sector"]), int(row["i"]), int(row["j"])): idx
            for idx, row in enumerate(support_rows)
        }
        pairs: list[tuple[int, int]] = []
        mode = "SKIPPED_LARGE_SUPPORT"
        if len(support_rows) <= max_exhaustive_basis:
            pairs = [(i, j) for i in range(len(support_rows)) for j in range(len(support_rows))]
            mode = "EXHAUSTIVE"
        elif support_name == "unit_top_all_39" and top_sample_products > 0:
            pairs = [
                (int(rng.integers(0, len(support_rows))), int(rng.integers(0, len(support_rows))))
                for _ in range(top_sample_products)
            ]
            mode = "SAMPLED"

        local_failures = 0
        for left_idx, right_idx in pairs:
            left = support_rows[left_idx]
            right = support_rows[right_idx]
            product = oracle.product(
                support_arrays[:, int(left["support_unit_row"])],
                support_arrays[:, int(right["support_unit_row"])],
            )
            target_idx = matrix_unit_target(left, right, local_by_key)
            if target_idx is None:
                target = zero
            else:
                target = support_arrays[:, int(support_rows[target_idx]["support_unit_row"])]
            if not np.array_equal(product % FIELD_PRIME, target % FIELD_PRIME):
                local_failures += 1
                failures.append(
                    {
                        "support_name": support_name,
                        "left_support_basis_index": left_idx,
                        "right_support_basis_index": right_idx,
                    }
                )
                if len(failures) >= 8:
                    break
        checked_total += len(pairs)
        rows.append(
            {
                "support_name": support_name,
                "basis_rows": len(support_rows),
                "check_mode": mode,
                "raw_products_checked": len(pairs),
                "raw_product_failures": local_failures,
            }
        )
        if len(failures) >= 8:
            break
    return {
        "checked": checked_total,
        "failure_count": len(failures),
        "failures": failures,
        "rows": rows,
    }


def build_projector_multiplication_table(
    projector_rows: list[dict[str, str]],
    projectors: np.ndarray,
    central_pages: np.ndarray,
    source_to_raw: dict[int, int],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    triples = np.asarray(np.load(TENSOR_NPZ)["triples"], dtype=np.int64)
    oracle = MultiplicationOracle(triples)
    sets_by_name = {row["support_name"]: parse_set(row["transported_source_support"]) for row in projector_rows}
    exact_name_by_set = {frozenset(value): name for name, value in sets_by_name.items()}
    rows: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []

    for left_idx, left_row in enumerate(projector_rows):
        left_name = left_row["support_name"]
        for right_idx, right_row in enumerate(projector_rows):
            right_name = right_row["support_name"]
            intersection = sets_by_name[left_name] & sets_by_name[right_name]
            target = central_sum(intersection, central_pages, source_to_raw)
            product = oracle.product(projectors[:, left_idx], projectors[:, right_idx])
            verified = bool(np.array_equal(product % FIELD_PRIME, target % FIELD_PRIME))
            if not verified:
                failures.append({"left": left_name, "right": right_name})
            rows.append(
                {
                    "left_projector_column": left_idx,
                    "right_projector_column": right_idx,
                    "left_support_name": left_name,
                    "right_support_name": right_name,
                    "result_named_support": exact_name_by_set.get(frozenset(intersection), ""),
                    "result_transport_source_support": set_literal(intersection),
                    "result_nonzero_coefficients": int(np.count_nonzero(target)),
                    "raw_product_verified": verified,
                }
            )
    return rows, {"checked": len(rows), "failure_count": len(failures), "failures": failures[:8]}


def write_outputs(
    basis_rows: list[dict[str, Any]],
    product_rows: list[dict[str, Any]],
    summary_rows: list[dict[str, Any]],
    raw_check_rows: list[dict[str, Any]],
    projector_product_rows: list[dict[str, Any]],
) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(
        OUT_DIR / "support_restricted_basis_manifest.csv",
        [
            "support_name",
            "projector_column",
            "support_basis_index",
            "support_unit_row",
            "source_support",
            "transported_source_support",
            "source_sector",
            "raw_sector",
            "block_dimension",
            "i",
            "j",
            "full_unit_column",
            "source_matrix_unit_label",
            "raw_matrix_unit_label",
            "coefficient_source",
        ],
        basis_rows,
    )
    write_csv_rows(
        OUT_DIR / "support_restricted_matrix_unit_products.csv",
        [
            "support_name",
            "projector_column",
            "source_sector",
            "raw_sector",
            "left_support_basis_index",
            "right_support_basis_index",
            "result_support_basis_index",
            "left_support_unit_row",
            "right_support_unit_row",
            "result_support_unit_row",
            "left_i",
            "left_j",
            "right_i",
            "right_j",
            "result_i",
            "result_j",
            "coefficient_mod_1000003",
            "left_label",
            "right_label",
            "result_label",
        ],
        product_rows,
    )
    write_csv_rows(
        OUT_DIR / "support_restricted_table_summary.csv",
        [
            "support_name",
            "projector_column",
            "transported_source_support",
            "basis_rows",
            "expected_basis_rows",
            "nonzero_products",
            "expected_nonzero_products",
            "zero_products",
            "symbolic_table_complete",
        ],
        summary_rows,
    )
    write_csv_rows(
        OUT_DIR / "support_restricted_raw_product_checks.csv",
        [
            "support_name",
            "basis_rows",
            "check_mode",
            "raw_products_checked",
            "raw_product_failures",
        ],
        raw_check_rows,
    )
    write_csv_rows(
        OUT_DIR / "support_projector_multiplication_table.csv",
        [
            "left_projector_column",
            "right_projector_column",
            "left_support_name",
            "right_support_name",
            "result_named_support",
            "result_transport_source_support",
            "result_nonzero_coefficients",
            "raw_product_verified",
        ],
        projector_product_rows,
    )
    table = np.asarray(
        [
            [
                int(row["projector_column"]),
                int(row["left_support_basis_index"]),
                int(row["right_support_basis_index"]),
                int(row["result_support_basis_index"]),
                int(row["coefficient_mod_1000003"]),
            ]
            for row in product_rows
        ],
        dtype=np.int64,
    )
    np.savez_compressed(
        OUT_DIR / "support_restricted_multiplication_arrays.npz",
        field_prime=np.array([FIELD_PRIME], dtype=np.int64),
        multiplication_table=table,
        support_basis_count=np.asarray([int(row["basis_rows"]) for row in summary_rows], dtype=np.int64),
        support_nonzero_product_count=np.asarray([int(row["nonzero_products"]) for row in summary_rows], dtype=np.int64),
    )


def markdown_report(report: dict[str, Any]) -> str:
    checks = "\n".join(f"- `{key}`: `{value}`" for key, value in report["checks"].items())
    derived = report["derived"]
    return (
        "# Support-Restricted Multiplication Tables\n\n"
        f"Status: `{report['status']}`\n\n"
        f"Basis rows: `{derived['basis_rows']}`\n\n"
        f"Sparse nonzero matrix-unit products: `{derived['matrix_unit_product_rows']}`\n\n"
        f"Projector products: `{derived['projector_product_rows']}`\n\n"
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


def build_support_multiplication(max_exhaustive_basis: int, top_sample_products: int, seed: int) -> dict[str, Any]:
    support_report = load_json(SUPPORT_COO_DIR / "report.json")
    source_to_raw, dimensions = load_source_maps()
    central_pages, _identity_indices = load_central_pages()

    support_rows = read_csv_rows(SUPPORT_COO_DIR / "support_matrix_units_orbital_manifest.csv")
    projector_rows = read_csv_rows(SUPPORT_COO_DIR / "support_projector_summary.csv")
    support_rows_by_name = group_support_rows(support_rows)
    arrays = np.load(SUPPORT_COO_DIR / "support_matrix_units_and_projectors_raw_orbital_arrays.npz")
    support_arrays = np.asarray(arrays["support_matrix_units"], dtype=np.int64) % FIELD_PRIME
    projectors = np.asarray(arrays["support_projectors"], dtype=np.int64) % FIELD_PRIME

    basis_rows = build_basis_manifest(support_rows_by_name, projector_rows)
    product_rows, summary_rows = build_matrix_unit_tables(support_rows_by_name, projector_rows, dimensions)
    support_names = [row["support_name"] for row in projector_rows]
    direct = verify_direct_products(
        support_rows_by_name,
        support_names,
        support_arrays,
        max_exhaustive_basis,
        top_sample_products,
        seed,
    )
    projector_product_rows, projector_products = build_projector_multiplication_table(
        projector_rows,
        projectors,
        central_pages,
        source_to_raw,
    )
    write_outputs(basis_rows, product_rows, summary_rows, direct["rows"], projector_product_rows)

    expected_product_rows = sum(int(row["expected_nonzero_products"]) for row in summary_rows)
    checks = {
        "support_full_coo_certified": support_report.get("status")
        == "D20_TINY_POINTER_A985_SUPPORT_FULL_MATRIX_UNIT_ORBITAL_COO_CERTIFIED"
        and support_report.get("all_checks_pass") is True,
        "support_projector_count_is_7": len(projector_rows) == 7,
        "support_basis_manifest_has_1011_rows": len(basis_rows) == 1011,
        "support_arrays_shape_is_985_by_1011": list(support_arrays.shape) == [RELATION_COUNT, 1011],
        "summary_has_7_rows": len(summary_rows) == 7,
        "all_symbolic_tables_complete": all(row["symbolic_table_complete"] for row in summary_rows),
        "product_rows_match_expected_nonzero_products": len(product_rows) == expected_product_rows,
        "zero_support_has_no_basis_or_products": any(
            row["support_name"] == "zero" and row["basis_rows"] == 0 and row["nonzero_products"] == 0
            for row in summary_rows
        ),
        "top_support_has_985_basis_rows": any(
            row["support_name"] == "unit_top_all_39" and row["basis_rows"] == RELATION_COUNT
            for row in summary_rows
        ),
        "direct_raw_product_failures_zero": direct["failure_count"] == 0,
        "direct_raw_products_checked_positive": direct["checked"] > 0,
        "projector_product_table_has_49_rows": len(projector_product_rows) == 49,
        "projector_raw_product_failures_zero": projector_products["failure_count"] == 0,
    }
    report = {
        "schema": "d20.theorem.tiny_pointer_a985_support_restricted_multiplication_tables.source_drop",
        "status": STATUS if all(checks.values()) else "D20_TINY_POINTER_A985_SUPPORT_RESTRICTED_MULTIPLICATION_TABLES_NEEDS_REVIEW",
        "object": "d20",
        "field_prime": FIELD_PRIME,
        "claim": (
            "Each named A985 support now has an explicit sparse multiplication table in its "
            "source-sector-labeled matrix-unit basis, and the seven support projectors have an explicit "
            "projector-intersection multiplication table."
        ),
        "inputs": {
            "support_full_matrix_unit_orbital_coo": {
                "path": rel(SUPPORT_COO_DIR / "report.json"),
                "sha256": sha_file(SUPPORT_COO_DIR / "report.json"),
            },
            "support_arrays": {
                "path": rel(SUPPORT_COO_DIR / "support_matrix_units_and_projectors_raw_orbital_arrays.npz"),
                "sha256": sha_file(SUPPORT_COO_DIR / "support_matrix_units_and_projectors_raw_orbital_arrays.npz"),
            },
            "full_source_sector_match": {
                "path": rel(FULL_MATCH_DIR / "report.json"),
                "sha256": sha_file(FULL_MATCH_DIR / "report.json"),
            },
            "central_idempotents": {
                "path": rel(CENTRAL_DIR / "a985_center_and_primitive_central_idempotents.npz"),
                "sha256": sha_file(CENTRAL_DIR / "a985_center_and_primitive_central_idempotents.npz"),
            },
            "t985_tensor": {"path": rel(TENSOR_NPZ), "sha256": sha_file(TENSOR_NPZ)},
        },
        "checks": checks,
        "derived": {
            "basis_rows": len(basis_rows),
            "matrix_unit_product_rows": len(product_rows),
            "projector_product_rows": len(projector_product_rows),
            "raw_matrix_unit_products": {
                "checked": direct["checked"],
                "failure_count": direct["failure_count"],
                "failures": direct["failures"],
            },
            "projector_products": projector_products,
            "basis_manifest_sha256": sha_file(OUT_DIR / "support_restricted_basis_manifest.csv"),
            "matrix_unit_product_table_sha256": sha_file(OUT_DIR / "support_restricted_matrix_unit_products.csv"),
            "summary_sha256": sha_file(OUT_DIR / "support_restricted_table_summary.csv"),
            "multiplication_arrays_sha256": sha_file(OUT_DIR / "support_restricted_multiplication_arrays.npz"),
            "tables": {
                "arrays": rel(OUT_DIR / "support_restricted_multiplication_arrays.npz"),
                "basis_manifest": rel(OUT_DIR / "support_restricted_basis_manifest.csv"),
                "matrix_unit_products": rel(OUT_DIR / "support_restricted_matrix_unit_products.csv"),
                "projector_products": rel(OUT_DIR / "support_projector_multiplication_table.csv"),
                "raw_product_checks": rel(OUT_DIR / "support_restricted_raw_product_checks.csv"),
                "summary": rel(OUT_DIR / "support_restricted_table_summary.csv"),
            },
        },
        "next_highest_yield_item": (
            "Use these support-restricted tables to isolate the remaining sector-local "
            "change-of-basis problem: source-sector matrix-unit normalization within each primitive block."
        ),
        "all_checks_pass": all(checks.values()),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    manifest = {
        "schema": "d20.theorem.tiny_pointer_a985_support_restricted_multiplication_tables_manifest.source_drop",
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
    (OUT_DIR / "support_restricted_multiplication_report.md").write_text(markdown_report(report), encoding="utf-8")
    update_theorem_index(report)
    return report


def verify_support_multiplication() -> dict[str, Any]:
    report = load_json(OUT_DIR / "report.json")
    basis_rows = read_csv_rows(OUT_DIR / "support_restricted_basis_manifest.csv")
    product_rows = read_csv_rows(OUT_DIR / "support_restricted_matrix_unit_products.csv")
    summary_rows = read_csv_rows(OUT_DIR / "support_restricted_table_summary.csv")
    projector_rows = read_csv_rows(OUT_DIR / "support_projector_multiplication_table.csv")
    raw_check_rows = read_csv_rows(OUT_DIR / "support_restricted_raw_product_checks.csv")
    arrays = np.load(OUT_DIR / "support_restricted_multiplication_arrays.npz")
    checks = {
        "report_status_certified": report.get("status") == STATUS,
        "report_checks_pass": report.get("all_checks_pass") is True,
        "basis_manifest_has_1011_rows": len(basis_rows) == 1011,
        "summary_has_7_rows": len(summary_rows) == 7,
        "projector_table_has_49_rows": len(projector_rows) == 49,
        "raw_check_summary_has_7_rows": len(raw_check_rows) == 7,
        "product_rows_match_report": len(product_rows) == report.get("derived", {}).get("matrix_unit_product_rows"),
        "product_arrays_match_table": list(arrays["multiplication_table"].shape)
        == [len(product_rows), 5],
        "all_raw_check_rows_have_zero_failures": all(int(row["raw_product_failures"]) == 0 for row in raw_check_rows),
        "all_projector_products_verified": all(row["raw_product_verified"] == "True" for row in projector_rows),
    }
    return {
        "status": "D20_TINY_POINTER_A985_SUPPORT_RESTRICTED_MULTIPLICATION_TABLES_VERIFIED"
        if all(checks.values())
        else "D20_TINY_POINTER_A985_SUPPORT_RESTRICTED_MULTIPLICATION_TABLES_VERIFY_FAILED",
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--max-exhaustive-basis", type=int, default=16)
    parser.add_argument("--top-sample-products", type=int, default=64)
    parser.add_argument("--seed", type=int, default=20_260_524)
    args = parser.parse_args()
    if not args.verify_only:
        build_support_multiplication(args.max_exhaustive_basis, args.top_sample_products, args.seed)
    verification = verify_support_multiplication()
    print(json.dumps(verification, indent=2, sort_keys=True))
    if not verification["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

