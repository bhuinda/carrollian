from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

ROOT_FOR_IMPORT = Path(__file__).resolve().parents[1]
if str(ROOT_FOR_IMPORT) not in sys.path:
    sys.path.insert(0, str(ROOT_FOR_IMPORT))

from src.derive_d20_nested_pointer_a985_block_matrix_units import (
    FIELD_PRIME,
    RELATION_COUNT,
    MultiplicationOracle,
    array_digest,
    build_block_units,
)
from src.paths import D20_INVARIANTS, ROOT


STATUS = "D20_NESTED_POINTER_A985_FULL_MATRIX_UNIT_ORBITAL_COO_CERTIFIED"
THEOREM_ID = "nested_pointer_a985_full_matrix_unit_orbital_coo"
OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

CENTRAL_DIR = D20_INVARIANTS / "theorems" / "nested_pointer_a985_orbital_central_idempotents"
FULL_MATCH_DIR = D20_INVARIANTS / "theorems" / "nested_pointer_a985_full_legacy_sector_match"
REGISTERED_DIR = D20_INVARIANTS / "theorems" / "nested_pointer_a985_registered_support_matrix_units"
LEGACY_TRANSPORT_DIR = D20_INVARIANTS / "theorems" / "nested_pointer_a985_legacy_matrix_unit_transport"
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


def load_maps() -> tuple[dict[int, int], dict[int, int], dict[int, int]]:
    rows = read_csv_rows(FULL_MATCH_DIR / "legacy_to_raw_sector_full_match.csv")
    legacy_to_raw = {int(row["legacy_sector"]): int(row["raw_sector"]) for row in rows}
    raw_to_legacy = {raw: legacy for legacy, raw in legacy_to_raw.items()}
    dimensions = {int(row["raw_sector"]): int(row["block_dimension"]) for row in rows}
    return legacy_to_raw, raw_to_legacy, dimensions


def load_central_pages() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    z = np.load(CENTRAL_DIR / "a985_center_and_primitive_central_idempotents.npz")
    pages = np.asarray(z["idempotents"], dtype=np.int64) % FIELD_PRIME
    trace_coeff = np.asarray(z["trace_coeff"], dtype=np.int64) % FIELD_PRIME
    identity_indices = np.asarray(z["identity_indices"], dtype=np.int64)
    return pages, trace_coeff, identity_indices


def registered_unit_blocks(dimensions: dict[int, int]) -> tuple[dict[int, np.ndarray], dict[str, Any]]:
    rows = read_csv_rows(REGISTERED_DIR / "registered_null_support_matrix_units_orbital_coo.csv")
    entries: dict[tuple[int, int, int], dict[int, int]] = defaultdict(dict)
    conflicts: list[dict[str, int]] = []
    for row in rows:
        raw_sector = int(row["raw_sector"])
        i = int(row["i"])
        j = int(row["j"])
        relation = int(row["relation_alpha"])
        coefficient = int(row["coefficient_mod_1000003"]) % FIELD_PRIME
        key = (raw_sector, i, j)
        prior = entries[key].get(relation)
        if prior is not None and prior != coefficient:
            conflicts.append(
                {
                    "raw_sector": raw_sector,
                    "i": i,
                    "j": j,
                    "relation_alpha": relation,
                    "prior": prior,
                    "new": coefficient,
                }
            )
        entries[key][relation] = coefficient

    by_sector: dict[int, np.ndarray] = {}
    incomplete: list[int] = []
    for raw_sector in sorted({key[0] for key in entries}):
        d = dimensions[raw_sector]
        present = [key for key in entries if key[0] == raw_sector]
        if len(present) != d * d:
            incomplete.append(raw_sector)
            continue
        block = np.zeros((RELATION_COUNT, d * d), dtype=np.int64)
        for i in range(d):
            for j in range(d):
                key = (raw_sector, i, j)
                col = i * d + j
                for relation, coefficient in entries[key].items():
                    block[relation, col] = coefficient
        by_sector[raw_sector] = block % FIELD_PRIME
    summary = {
        "registered_coo_rows_read": len(rows),
        "registered_raw_sectors_available": sorted(int(value) for value in by_sector),
        "registered_duplicate_conflicts": conflicts[:8],
        "registered_incomplete_raw_sectors": incomplete,
    }
    return by_sector, summary


def verify_registered_block(
    oracle: MultiplicationOracle,
    central_page: np.ndarray,
    raw_sector: int,
    block: np.ndarray,
    dimension: int,
) -> dict[str, Any]:
    failures = 0
    zero = np.zeros(RELATION_COUNT, dtype=np.int64)
    for i in range(dimension):
        for j in range(dimension):
            left = block[:, i * dimension + j]
            for k in range(dimension):
                for ell in range(dimension):
                    right = block[:, k * dimension + ell]
                    product = oracle.product(left, right)
                    target = block[:, i * dimension + ell] if j == k else zero
                    if not np.array_equal(product % FIELD_PRIME, target % FIELD_PRIME):
                        failures += 1
    diagonal_sum = np.sum(block[:, [i * dimension + i for i in range(dimension)]], axis=1) % FIELD_PRIME
    return {
        "raw_sector": int(raw_sector),
        "source": "REGISTERED_SUPPORT_COO",
        "block_dimension": int(dimension),
        "matrix_unit_count": int(block.shape[1]),
        "direct_matrix_unit_product_failures": int(failures),
        "diagonal_sum_equals_central_page": bool(np.array_equal(diagonal_sum, central_page % FIELD_PRIME)),
        "matrix_unit_block_sha256": array_digest(block),
    }


def write_outputs(
    matrix_units: np.ndarray,
    manifest_rows: list[dict[str, Any]],
    coo_rows: list[dict[str, Any]],
    sector_rows: list[dict[str, Any]],
) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        OUT_DIR / "legacy_matrix_units_raw_orbital_arrays.npz",
        field_prime=np.array([FIELD_PRIME], dtype=np.int64),
        matrix_units=matrix_units.astype(np.int64),
        unit_column=np.asarray([row["unit_column"] for row in manifest_rows], dtype=np.int64),
        legacy_sector=np.asarray([row["legacy_sector"] for row in manifest_rows], dtype=np.int64),
        raw_sector=np.asarray([row["raw_sector"] for row in manifest_rows], dtype=np.int64),
        i=np.asarray([row["i"] for row in manifest_rows], dtype=np.int64),
        j=np.asarray([row["j"] for row in manifest_rows], dtype=np.int64),
    )
    write_csv_rows(
        OUT_DIR / "legacy_matrix_units_orbital_manifest.csv",
        [
            "unit_column",
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
        OUT_DIR / "legacy_matrix_units_orbital_coo.csv",
        [
            "unit_column",
            "legacy_sector",
            "raw_sector",
            "block_dimension",
            "i",
            "j",
            "relation_alpha",
            "coefficient_mod_1000003",
            "coefficient_source",
        ],
        coo_rows,
    )
    write_csv_rows(
        OUT_DIR / "sector_matrix_unit_source_summary.csv",
        [
            "legacy_sector",
            "raw_sector",
            "block_dimension",
            "matrix_unit_count",
            "coefficient_source",
            "diagonal_sum_equals_central_page",
            "bridge_delta_failures",
            "direct_matrix_unit_product_failures",
            "matrix_unit_block_sha256",
        ],
        sector_rows,
    )


def build_full_coo(seed: int, max_trials: int, sample_products: int) -> dict[str, Any]:
    full_match = load_json(FULL_MATCH_DIR / "report.json")
    legacy_transport = load_json(LEGACY_TRANSPORT_DIR / "report.json")
    legacy_to_raw, raw_to_legacy, dimensions = load_maps()
    central_pages, _trace_coeff, identity_indices = load_central_pages()
    triples = np.asarray(np.load(TENSOR_NPZ)["triples"], dtype=np.int64)
    oracle = MultiplicationOracle(triples)
    registered_blocks, registered_summary = registered_unit_blocks(dimensions)
    rng = np.random.default_rng(seed)

    matrix_blocks_by_legacy: list[np.ndarray] = []
    manifest_rows: list[dict[str, Any]] = []
    coo_rows: list[dict[str, Any]] = []
    sector_rows: list[dict[str, Any]] = []
    constructed_count = 0
    registered_count = 0
    unit_column = 0
    for legacy_sector in sorted(legacy_to_raw):
        raw_sector = legacy_to_raw[legacy_sector]
        dimension = dimensions[raw_sector]
        central_page = central_pages[raw_sector]
        if raw_sector in registered_blocks:
            block = registered_blocks[raw_sector]
            info = verify_registered_block(oracle, central_page, raw_sector, block, dimension)
            source = "REGISTERED_SUPPORT_COO"
            registered_count += 1
        else:
            block, _corner, _left_basis, _right_dual_basis, info = build_block_units(
                oracle,
                raw_sector,
                central_page,
                dimension,
                rng,
                max_trials,
            )
            source = "CONSTRUCTED_FROM_PROMOTED_CENTRAL_PAGE"
            constructed_count += 1
            info["source"] = source
            info.setdefault("direct_matrix_unit_product_failures", "")
        matrix_blocks_by_legacy.append(block)

        for i in range(dimension):
            for j in range(dimension):
                local_col = i * dimension + j
                vec = block[:, local_col] % FIELD_PRIME
                support = np.nonzero(vec)[0]
                manifest_rows.append(
                    {
                        "unit_column": unit_column,
                        "legacy_sector": legacy_sector,
                        "raw_sector": raw_sector,
                        "block_dimension": dimension,
                        "i": i,
                        "j": j,
                        "legacy_matrix_unit_label": f"u_legacy[{legacy_sector};{i},{j}]",
                        "raw_matrix_unit_label": f"u_raw[{raw_sector};{i},{j}]",
                        "coefficient_source": source,
                        "nonzero_coefficients": int(support.size),
                    }
                )
                for relation in support:
                    coo_rows.append(
                        {
                            "unit_column": unit_column,
                            "legacy_sector": legacy_sector,
                            "raw_sector": raw_sector,
                            "block_dimension": dimension,
                            "i": i,
                            "j": j,
                            "relation_alpha": int(relation),
                            "coefficient_mod_1000003": int(vec[int(relation)]),
                            "coefficient_source": source,
                        }
                    )
                unit_column += 1
        sector_rows.append(
            {
                "legacy_sector": legacy_sector,
                "raw_sector": raw_sector,
                "block_dimension": dimension,
                "matrix_unit_count": int(dimension * dimension),
                "coefficient_source": source,
                "diagonal_sum_equals_central_page": bool(info["diagonal_sum_equals_central_page"]),
                "bridge_delta_failures": int(info.get("bridge_delta_failures", 0) or 0),
                "direct_matrix_unit_product_failures": int(info.get("direct_matrix_unit_product_failures", 0) or 0),
                "matrix_unit_block_sha256": info["matrix_unit_block_sha256"],
            }
        )

    matrix_units = np.concatenate(matrix_blocks_by_legacy, axis=1) % FIELD_PRIME
    write_outputs(matrix_units, manifest_rows, coo_rows, sector_rows)

    sample = sample_matrix_products(oracle, matrix_units, manifest_rows, sample_products, seed + 31)
    source_counts = Counter(row["coefficient_source"] for row in manifest_rows)
    coo_source_counts = Counter(row["coefficient_source"] for row in coo_rows)
    diag_failures = [row for row in sector_rows if not row["diagonal_sum_equals_central_page"]]
    bridge_failures = sum(int(row["bridge_delta_failures"]) for row in sector_rows)
    direct_failures = sum(int(row["direct_matrix_unit_product_failures"]) for row in sector_rows)
    checks = {
        "full_legacy_sector_match_certified": full_match.get("status")
        == "D20_NESTED_POINTER_A985_FULL_LEGACY_SECTOR_MATCH_CERTIFIED"
        and full_match.get("all_checks_pass") is True,
        "legacy_transport_certified": legacy_transport.get("status")
        == "D20_NESTED_POINTER_A985_LEGACY_MATRIX_UNIT_TRANSPORT_CERTIFIED"
        and legacy_transport.get("all_checks_pass") is True,
        "central_page_count_is_39": central_pages.shape == (39, RELATION_COUNT),
        "matrix_unit_count_is_985": matrix_units.shape == (RELATION_COUNT, RELATION_COUNT),
        "manifest_row_count_is_985": len(manifest_rows) == RELATION_COUNT,
        "coo_rows_match_nonzero_count": len(coo_rows) == int(np.count_nonzero(matrix_units)),
        "sector_summary_count_is_39": len(sector_rows) == 39,
        "registered_blocks_preserved": registered_summary["registered_raw_sectors_available"] == [9, 19, 29, 30],
        "registered_duplicate_conflicts_zero": registered_summary["registered_duplicate_conflicts"] == [],
        "all_diagonal_sums_equal_central_pages": not diag_failures,
        "constructed_bridge_failures_zero": bridge_failures == 0,
        "registered_direct_product_failures_zero": direct_failures == 0,
        "sampled_matrix_unit_products_pass": sample["failure_count"] == 0,
    }
    report = {
        "schema": "d20.theorem.nested_pointer_a985_full_matrix_unit_orbital_coo.source_drop",
        "status": STATUS if all(checks.values()) else "D20_NESTED_POINTER_A985_FULL_MATRIX_UNIT_ORBITAL_COO_NEEDS_REVIEW",
        "object": "d20",
        "field_prime": FIELD_PRIME,
        "claim": (
            "All 985 legacy-labeled A985 block matrix units now have raw-orbital COO coefficient rows. "
            "Registered public-zero support blocks preserve the promoted registered COO coordinates; the "
            "remaining blocks are constructed from the promoted central pages inside the raw T985 algebra."
        ),
        "inputs": {
            "t985_tensor": {"path": rel(TENSOR_NPZ), "sha256": sha_file(TENSOR_NPZ)},
            "central_idempotents": {
                "path": rel(CENTRAL_DIR / "a985_center_and_primitive_central_idempotents.npz"),
                "sha256": sha_file(CENTRAL_DIR / "a985_center_and_primitive_central_idempotents.npz"),
            },
            "full_legacy_sector_match": {
                "path": rel(FULL_MATCH_DIR / "report.json"),
                "sha256": sha_file(FULL_MATCH_DIR / "report.json"),
            },
            "legacy_matrix_unit_transport": {
                "path": rel(LEGACY_TRANSPORT_DIR / "report.json"),
                "sha256": sha_file(LEGACY_TRANSPORT_DIR / "report.json"),
            },
            "registered_subset_coo": {
                "path": rel(REGISTERED_DIR / "registered_null_support_matrix_units_orbital_coo.csv"),
                "sha256": sha_file(REGISTERED_DIR / "registered_null_support_matrix_units_orbital_coo.csv"),
            },
        },
        "checks": checks,
        "derived": {
            "matrix_units_shape": list(matrix_units.shape),
            "matrix_units_sha256": array_digest(matrix_units),
            "legacy_matrix_unit_count": len(manifest_rows),
            "orbital_coo_rows": len(coo_rows),
            "identity_indices": [int(value) for value in identity_indices.tolist()],
            "sector_source_counts": {
                "registered_blocks": int(registered_count),
                "constructed_blocks": int(constructed_count),
            },
            "matrix_unit_source_counts": {key: int(value) for key, value in sorted(source_counts.items())},
            "coo_source_counts": {key: int(value) for key, value in sorted(coo_source_counts.items())},
            "registered_summary": registered_summary,
            "sampled_products": sample,
            "tables": {
                "arrays": rel(OUT_DIR / "legacy_matrix_units_raw_orbital_arrays.npz"),
                "manifest": rel(OUT_DIR / "legacy_matrix_units_orbital_manifest.csv"),
                "coo": rel(OUT_DIR / "legacy_matrix_units_orbital_coo.csv"),
                "sector_summary": rel(OUT_DIR / "sector_matrix_unit_source_summary.csv"),
            },
        },
        "next_highest_yield_item": (
            "Replace the registered support manifest's top-support rows with this all-39 COO-backed "
            "legacy matrix-unit table, or derive support-level projectors directly from the full COO table."
        ),
        "all_checks_pass": all(checks.values()),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    manifest = {
        "schema": "d20.theorem.nested_pointer_a985_full_matrix_unit_orbital_coo_manifest.source_drop",
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
    (OUT_DIR / "full_matrix_unit_orbital_coo_report.md").write_text(markdown_report(report), encoding="utf-8")
    update_theorem_index(report)
    return report


def sample_matrix_products(
    oracle: MultiplicationOracle,
    matrix_units: np.ndarray,
    manifest_rows: list[dict[str, Any]],
    sample_size: int,
    seed: int,
) -> dict[str, Any]:
    if sample_size <= 0:
        return {"checked": 0, "failure_count": 0, "failures": []}
    rng = np.random.default_rng(seed)
    by_key = {
        (int(row["legacy_sector"]), int(row["i"]), int(row["j"])): int(row["unit_column"])
        for row in manifest_rows
    }
    zero = np.zeros(RELATION_COUNT, dtype=np.int64)
    failures: list[dict[str, int]] = []
    for _ in range(sample_size):
        left = int(rng.integers(0, len(manifest_rows)))
        right = int(rng.integers(0, len(manifest_rows)))
        left_row = manifest_rows[left]
        right_row = manifest_rows[right]
        product = oracle.product(matrix_units[:, left], matrix_units[:, right])
        target = zero
        if left_row["legacy_sector"] == right_row["legacy_sector"] and left_row["j"] == right_row["i"]:
            target = matrix_units[:, by_key[(left_row["legacy_sector"], left_row["i"], right_row["j"])]]
        if not np.array_equal(product % FIELD_PRIME, target % FIELD_PRIME):
            failures.append({"left_column": left, "right_column": right})
            if len(failures) >= 8:
                break
    return {"checked": int(sample_size), "failure_count": len(failures), "failures": failures}


def markdown_report(report: dict[str, Any]) -> str:
    checks = "\n".join(f"- `{key}`: `{value}`" for key, value in report["checks"].items())
    derived = report["derived"]
    return (
        "# Full Matrix-Unit Orbital COO\n\n"
        f"Status: `{report['status']}`\n\n"
        f"Matrix units: `{derived['legacy_matrix_unit_count']}`\n\n"
        f"COO coefficient rows: `{derived['orbital_coo_rows']}`\n\n"
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


def verify_full_coo() -> dict[str, Any]:
    report = load_json(OUT_DIR / "report.json")
    manifest_rows = read_csv_rows(OUT_DIR / "legacy_matrix_units_orbital_manifest.csv")
    coo_rows = read_csv_rows(OUT_DIR / "legacy_matrix_units_orbital_coo.csv")
    sector_rows = read_csv_rows(OUT_DIR / "sector_matrix_unit_source_summary.csv")
    arrays = np.load(OUT_DIR / "legacy_matrix_units_raw_orbital_arrays.npz")
    checks = {
        "report_status_certified": report.get("status") == STATUS,
        "report_checks_pass": report.get("all_checks_pass") is True,
        "array_shape_is_985_by_985": list(arrays["matrix_units"].shape) == [RELATION_COUNT, RELATION_COUNT],
        "manifest_has_985_rows": len(manifest_rows) == RELATION_COUNT,
        "coo_rows_match_report": len(coo_rows) == report.get("derived", {}).get("orbital_coo_rows"),
        "sector_summary_has_39_rows": len(sector_rows) == 39,
        "coo_rows_match_array_nonzeros": len(coo_rows) == int(np.count_nonzero(arrays["matrix_units"] % FIELD_PRIME)),
    }
    return {
        "status": "D20_NESTED_POINTER_A985_FULL_MATRIX_UNIT_ORBITAL_COO_VERIFIED"
        if all(checks.values())
        else "D20_NESTED_POINTER_A985_FULL_MATRIX_UNIT_ORBITAL_COO_VERIFY_FAILED",
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--seed", type=int, default=20_260_524)
    parser.add_argument("--max-trials", type=int, default=100)
    parser.add_argument("--sample-products", type=int, default=256)
    args = parser.parse_args()
    if not args.verify_only:
        build_full_coo(args.seed, args.max_trials, args.sample_products)
    verification = verify_full_coo()
    print(json.dumps(verification, indent=2, sort_keys=True))
    if not verification["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
