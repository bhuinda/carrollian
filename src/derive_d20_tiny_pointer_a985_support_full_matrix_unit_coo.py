from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

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

from src.derive_d20_tiny_pointer_a985_block_matrix_units import (  # noqa: E402
    FIELD_PRIME,
    RELATION_COUNT,
    MultiplicationOracle,
    array_digest,
)
from src.a985_perennial_ids import (  # noqa: E402
    load_perennial_sector_maps_if_available,
    write_a985_sector_csv_rows_if_available,
)
from src.paths import D20_INVARIANTS, ROOT  # noqa: E402


STATUS = "D20_TINY_POINTER_A985_SUPPORT_FULL_MATRIX_UNIT_ORBITAL_COO_CERTIFIED"
THEOREM_ID = "tiny_pointer_a985_support_full_matrix_unit_orbital_coo"
OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

CENTRAL_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_orbital_central_idempotents"
FULL_MATCH_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_full_sector_match"
REGISTERED_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_registered_support_matrix_units"
SECTOR_TRANSPORT_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_sector_matrix_unit_transport"
FULL_COO_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_full_matrix_unit_orbital_coo"
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


def support_name(row: dict[str, str]) -> str:
    return row.get("support_name") or row.get("support_name") or ""


def source_support(row: dict[str, str]) -> str:
    return row.get("source_support") or row.get("source_support") or ""


def raw_support(row: dict[str, str]) -> str:
    return row.get("raw_support") or row.get("raw_support") or ""


def transported_source_support(row: dict[str, str]) -> str:
    return row.get("transported_source_support") or row.get("transported_source_support") or ""


def load_source_maps() -> tuple[dict[int, int], dict[int, int], dict[int, int]]:
    rows = read_csv_rows(FULL_MATCH_DIR / "source_to_raw_sector_full_match.csv")
    source_to_raw = {int(row["source_sector"]): int(row["raw_sector"]) for row in rows}
    raw_to_source = {raw: source for source, raw in source_to_raw.items()}
    dimensions = {int(row["source_sector"]): int(row["block_dimension"]) for row in rows}
    return source_to_raw, raw_to_source, dimensions


def load_central_pages() -> tuple[np.ndarray, np.ndarray]:
    z = np.load(CENTRAL_DIR / "a985_center_and_primitive_central_idempotents.npz")
    pages = np.asarray(z["idempotents"], dtype=np.int64) % FIELD_PRIME
    identity_indices = np.asarray(z["identity_indices"], dtype=np.int64)
    return pages, identity_indices


def full_coo_spans() -> dict[int, dict[str, int]]:
    spans: dict[int, dict[str, int]] = {}
    for coo_index, row in enumerate(read_csv_rows(FULL_COO_DIR / "source_sector_matrix_units_orbital_coo.csv")):
        unit_column = int(row["unit_column"])
        if unit_column not in spans:
            spans[unit_column] = {"first_full_coo_row": coo_index, "full_coo_row_count": 0}
        spans[unit_column]["full_coo_row_count"] += 1
    return spans


def build_support_rows(
    full_manifest_rows: list[dict[str, str]],
    transported_rows: list[dict[str, str]],
    spans: dict[int, dict[str, int]],
) -> list[dict[str, Any]]:
    transport_by_key: dict[tuple[int, int, int], dict[str, str]] = {}
    for row in transported_rows:
        if support_name(row) != "unit_top_all_39":
            continue
        key = (int(row["source_sector"]), int(row["i"]), int(row["j"]))
        transport_by_key[key] = row

    full_by_key: dict[tuple[int, int, int], dict[str, str]] = {}
    for row in full_manifest_rows:
        key = (int(row["source_sector"]), int(row["i"]), int(row["j"]))
        full_by_key[key] = row

    out: list[dict[str, Any]] = []
    support_row = 0

    for full_row in full_manifest_rows:
        source_sector = int(full_row["source_sector"])
        i = int(full_row["i"])
        j = int(full_row["j"])
        key = (source_sector, i, j)
        source_row = transport_by_key[key]
        unit_column = int(full_row["unit_column"])
        span = spans[unit_column]
        out.append(
            {
                "support_unit_row": support_row,
                "source_row": int(source_row["source_row"]),
                "support_name": "unit_top_all_39",
                "source_support": transported_source_support(source_row) or set_literal(list(range(39))),
                "raw_support": raw_support(source_row),
                "source_sector": source_sector,
                "raw_sector": int(full_row["raw_sector"]),
                "block_dimension": int(full_row["block_dimension"]),
                "i": i,
                "j": j,
                "object_i": int(source_row["object_i"]),
                "object_j": int(source_row["object_j"]),
                "full_unit_column": unit_column,
                "full_coo_first_row": span["first_full_coo_row"],
                "full_coo_row_count": span["full_coo_row_count"],
                "nonzero_coefficients": int(full_row["nonzero_coefficients"]),
                "source_matrix_unit_label": full_row["source_matrix_unit_label"],
                "raw_matrix_unit_label": full_row["raw_matrix_unit_label"],
                "coefficient_source": full_row["coefficient_source"],
                "support_row_source": "TOP_SUPPORT_REPLACED_FROM_FULL_COO",
            }
        )
        support_row += 1

    for source_row in transported_rows:
        if support_name(source_row) == "unit_top_all_39":
            continue
        source_sector = int(source_row["source_sector"])
        i = int(source_row["i"])
        j = int(source_row["j"])
        full_row = full_by_key[(source_sector, i, j)]
        unit_column = int(full_row["unit_column"])
        span = spans[unit_column]
        out.append(
            {
                "support_unit_row": support_row,
                "source_row": int(source_row["source_row"]),
                "support_name": support_name(source_row),
                "source_support": source_support(source_row),
                "raw_support": raw_support(source_row),
                "source_sector": source_sector,
                "raw_sector": int(full_row["raw_sector"]),
                "block_dimension": int(full_row["block_dimension"]),
                "i": i,
                "j": j,
                "object_i": int(source_row["object_i"]),
                "object_j": int(source_row["object_j"]),
                "full_unit_column": unit_column,
                "full_coo_first_row": span["first_full_coo_row"],
                "full_coo_row_count": span["full_coo_row_count"],
                "nonzero_coefficients": int(full_row["nonzero_coefficients"]),
                "source_matrix_unit_label": full_row["source_matrix_unit_label"],
                "raw_matrix_unit_label": full_row["raw_matrix_unit_label"],
                "coefficient_source": full_row["coefficient_source"],
                "support_row_source": "REGISTERED_SUPPORT_DEREFERENCED_TO_FULL_COO",
            }
        )
        support_row += 1
    return out


def build_support_coo_rows(support_rows: list[dict[str, Any]], matrix_units: np.ndarray) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in support_rows:
        vec = matrix_units[:, int(row["full_unit_column"])] % FIELD_PRIME
        support = np.nonzero(vec)[0]
        for relation in support:
            out.append(
                {
                    "support_unit_row": row["support_unit_row"],
                    "support_name": row["support_name"],
                    "source_sector": row["source_sector"],
                    "raw_sector": row["raw_sector"],
                    "i": row["i"],
                    "j": row["j"],
                    "full_unit_column": row["full_unit_column"],
                    "relation_alpha": int(relation),
                    "coefficient_mod_1000003": int(vec[int(relation)]),
                    "coefficient_source": row["coefficient_source"],
                }
            )
    return out


def central_sum(
    source_sectors: set[int],
    central_pages: np.ndarray,
    source_to_raw: dict[int, int],
) -> np.ndarray:
    out = np.zeros(RELATION_COUNT, dtype=np.int64)
    for source_sector in sorted(source_sectors):
        out += central_pages[source_to_raw[source_sector]]
    return out % FIELD_PRIME


def build_projectors(
    support_transport_rows: list[dict[str, str]],
    full_by_key: dict[tuple[int, int, int], dict[str, str]],
    matrix_units: np.ndarray,
    central_pages: np.ndarray,
    identity_indices: np.ndarray,
    source_to_raw: dict[int, int],
) -> tuple[np.ndarray, list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    projector_columns: list[np.ndarray] = []
    summary_rows: list[dict[str, Any]] = []
    coo_rows: list[dict[str, Any]] = []
    support_sets: dict[str, set[int]] = {}

    for projector_column, row in enumerate(support_transport_rows):
        name = support_name(row)
        source_set = parse_set(transported_source_support(row))
        support_sets[name] = source_set
        diag_columns: list[int] = []
        for source_sector in sorted(source_set):
            dimension = int(next(
                item["block_dimension"]
                for key, item in full_by_key.items()
                if key[0] == source_sector
            ))
            for i in range(dimension):
                diag_columns.append(int(full_by_key[(source_sector, i, i)]["unit_column"]))

        if diag_columns:
            vec = np.sum(matrix_units[:, diag_columns], axis=1) % FIELD_PRIME
        else:
            vec = np.zeros(RELATION_COUNT, dtype=np.int64)
        target = central_sum(source_set, central_pages, source_to_raw)
        support = np.nonzero(vec)[0]
        for relation in support:
            coo_rows.append(
                {
                    "projector_column": projector_column,
                    "support_name": name,
                    "relation_alpha": int(relation),
                    "coefficient_mod_1000003": int(vec[int(relation)]),
                    "projector_source": "SUM_OF_FULL_COO_DIAGONAL_MATRIX_UNITS",
                }
            )
        summary_rows.append(
            {
                "projector_column": projector_column,
                "support_name": name,
                "source_support": source_support(row),
                "raw_support": raw_support(row),
                "transported_source_support": transported_source_support(row),
                "source_sector_count": len(source_set),
                "matrix_unit_rows": int(row["matrix_unit_rows"]),
                "diagonal_terms": len(diag_columns),
                "nonzero_coefficients": int(support.size),
                "equals_central_page_sum": bool(np.array_equal(vec, target)),
                "projector_sha256": array_digest(vec.reshape(-1, 1)),
            }
        )
        projector_columns.append(vec)

    projectors = np.stack(projector_columns, axis=1) if projector_columns else np.zeros((RELATION_COUNT, 0), dtype=np.int64)
    unit = np.zeros(RELATION_COUNT, dtype=np.int64)
    unit[identity_indices] = 1
    top_idx = next(idx for idx, row in enumerate(summary_rows) if row["support_name"] == "unit_top_all_39")
    zero_idx = next(idx for idx, row in enumerate(summary_rows) if row["support_name"] == "zero")
    product_summary = verify_projector_products(projectors, support_transport_rows, support_sets, central_pages, source_to_raw)
    checks = {
        "projector_count_is_7": projectors.shape == (RELATION_COUNT, 7),
        "zero_projector_is_zero": bool(np.array_equal(projectors[:, zero_idx], np.zeros(RELATION_COUNT, dtype=np.int64))),
        "top_projector_is_unit": bool(np.array_equal(projectors[:, top_idx], unit)),
        "all_projectors_equal_central_page_sums": all(row["equals_central_page_sum"] for row in summary_rows),
        "projector_product_failures_zero": product_summary["failure_count"] == 0,
    }
    return projectors, summary_rows, coo_rows, {"checks": checks, "products": product_summary}


def verify_projector_products(
    projectors: np.ndarray,
    support_transport_rows: list[dict[str, str]],
    support_sets: dict[str, set[int]],
    central_pages: np.ndarray,
    source_to_raw: dict[int, int],
) -> dict[str, Any]:
    triples = np.asarray(np.load(TENSOR_NPZ)["triples"], dtype=np.int64)
    oracle = MultiplicationOracle(triples)
    failures: list[dict[str, str]] = []
    for left_index, left_row in enumerate(support_transport_rows):
        left_name = support_name(left_row)
        for right_index, right_row in enumerate(support_transport_rows):
            right_name = support_name(right_row)
            product = oracle.product(projectors[:, left_index], projectors[:, right_index])
            intersection = support_sets[left_name] & support_sets[right_name]
            target = central_sum(intersection, central_pages, source_to_raw)
            if not np.array_equal(product % FIELD_PRIME, target % FIELD_PRIME):
                failures.append({"left": left_name, "right": right_name})
                if len(failures) >= 8:
                    break
        if len(failures) >= 8:
            break
    return {
        "checked": int(len(support_transport_rows) * len(support_transport_rows)),
        "failure_count": len(failures),
        "failures": failures,
    }


def write_outputs(
    support_rows: list[dict[str, Any]],
    support_coo_rows: list[dict[str, Any]],
    projectors: np.ndarray,
    projector_summary_rows: list[dict[str, Any]],
    projector_coo_rows: list[dict[str, Any]],
    matrix_units: np.ndarray,
    perennial_maps: dict[str, dict[int | str, dict[str, Any]]] | None,
) -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    full_columns = np.asarray([row["full_unit_column"] for row in support_rows], dtype=np.int64)
    support_matrix_units = matrix_units[:, full_columns] % FIELD_PRIME
    np.savez_compressed(
        OUT_DIR / "support_matrix_units_and_projectors_raw_orbital_arrays.npz",
        field_prime=np.array([FIELD_PRIME], dtype=np.int64),
        support_matrix_units=support_matrix_units.astype(np.int64),
        support_projectors=projectors.astype(np.int64),
        full_unit_column=full_columns,
        support_unit_row=np.asarray([row["support_unit_row"] for row in support_rows], dtype=np.int64),
        source_sector=np.asarray([row["source_sector"] for row in support_rows], dtype=np.int64),
        raw_sector=np.asarray([row["raw_sector"] for row in support_rows], dtype=np.int64),
        i=np.asarray([row["i"] for row in support_rows], dtype=np.int64),
        j=np.asarray([row["j"] for row in support_rows], dtype=np.int64),
    )
    support_manifest_stats = write_a985_sector_csv_rows_if_available(
        OUT_DIR / "support_matrix_units_orbital_manifest.csv",
        [
            "support_unit_row",
            "source_row",
            "support_name",
            "source_support",
            "raw_support",
            "source_sector",
            "raw_sector",
            "block_dimension",
            "i",
            "j",
            "object_i",
            "object_j",
            "full_unit_column",
            "full_coo_first_row",
            "full_coo_row_count",
            "nonzero_coefficients",
            "source_matrix_unit_label",
            "raw_matrix_unit_label",
            "coefficient_source",
            "support_row_source",
        ],
        support_rows,
        perennial_maps,
    )
    support_coo_stats = write_a985_sector_csv_rows_if_available(
        OUT_DIR / "support_matrix_units_orbital_coo.csv",
        [
            "support_unit_row",
            "support_name",
            "source_sector",
            "raw_sector",
            "i",
            "j",
            "full_unit_column",
            "relation_alpha",
            "coefficient_mod_1000003",
            "coefficient_source",
        ],
        support_coo_rows,
        perennial_maps,
    )
    projector_summary_stats = write_a985_sector_csv_rows_if_available(
        OUT_DIR / "support_projector_summary.csv",
        [
            "projector_column",
            "support_name",
            "source_support",
            "raw_support",
            "transported_source_support",
            "source_sector_count",
            "matrix_unit_rows",
            "diagonal_terms",
            "nonzero_coefficients",
            "equals_central_page_sum",
            "projector_sha256",
        ],
        projector_summary_rows,
        perennial_maps,
    )
    write_csv_rows(
        OUT_DIR / "support_projectors_orbital_coo.csv",
        [
            "projector_column",
            "support_name",
            "relation_alpha",
            "coefficient_mod_1000003",
            "projector_source",
        ],
        projector_coo_rows,
    )
    return {
        "support_manifest": support_manifest_stats,
        "support_coo": support_coo_stats,
        "projector_summary": projector_summary_stats,
    }


def markdown_report(report: dict[str, Any]) -> str:
    checks = "\n".join(f"- `{key}`: `{value}`" for key, value in report["checks"].items())
    derived = report["derived"]
    return (
        "# Support Full Matrix-Unit Orbital COO\n\n"
        f"Status: `{report['status']}`\n\n"
        f"Support matrix-unit rows: `{derived['support_matrix_unit_rows']}`\n\n"
        f"Support COO rows: `{derived['support_orbital_coo_rows']}`\n\n"
        f"Support projectors: `{derived['support_projector_count']}`\n\n"
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


def build_support_full_coo() -> dict[str, Any]:
    registered_report = load_json(REGISTERED_DIR / "report.json")
    transport_report = load_json(SECTOR_TRANSPORT_DIR / "report.json")
    full_coo_report = load_json(FULL_COO_DIR / "report.json")
    perennial_maps = load_perennial_sector_maps_if_available()
    source_to_raw, _raw_to_source, _dimensions = load_source_maps()
    central_pages, identity_indices = load_central_pages()

    full_manifest_rows = read_csv_rows(FULL_COO_DIR / "source_sector_matrix_units_orbital_manifest.csv")
    transported_rows = read_csv_rows(SECTOR_TRANSPORT_DIR / "source_sector_matrix_unit_manifest.csv")
    support_transport = read_csv_rows(SECTOR_TRANSPORT_DIR / "registered_support_source_transport.csv")
    spans = full_coo_spans()
    support_rows = build_support_rows(full_manifest_rows, transported_rows, spans)

    arrays = np.load(FULL_COO_DIR / "source_sector_matrix_units_raw_orbital_arrays.npz")
    matrix_units = np.asarray(arrays["matrix_units"], dtype=np.int64) % FIELD_PRIME
    support_coo_rows = build_support_coo_rows(support_rows, matrix_units)
    full_by_key = {
        (int(row["source_sector"]), int(row["i"]), int(row["j"])): row
        for row in full_manifest_rows
    }
    projectors, projector_summary_rows, projector_coo_rows, projector_checks = build_projectors(
        support_transport,
        full_by_key,
        matrix_units,
        central_pages,
        identity_indices,
        source_to_raw,
    )
    perennial_stats = write_outputs(
        support_rows,
        support_coo_rows,
        projectors,
        projector_summary_rows,
        projector_coo_rows,
        matrix_units,
        perennial_maps,
    )

    top_rows = [row for row in support_rows if row["support_name"] == "unit_top_all_39"]
    subsupport_rows = [row for row in support_rows if row["support_name"] != "unit_top_all_39"]
    row_source_counts = Counter(row["support_row_source"] for row in support_rows)
    coefficient_source_counts = Counter(row["coefficient_source"] for row in support_rows)
    checks = {
        "registered_stage_certified": registered_report.get("status")
        == "D20_TINY_POINTER_A985_REGISTERED_SUPPORT_MATRIX_UNITS_CERTIFIED"
        and registered_report.get("all_checks_pass") is True,
        "sector_transport_certified": transport_report.get("status")
        == "D20_TINY_POINTER_A985_SECTOR_MATRIX_UNIT_TRANSPORT_CERTIFIED"
        and transport_report.get("all_checks_pass") is True,
        "full_matrix_unit_coo_certified": full_coo_report.get("status")
        == "D20_TINY_POINTER_A985_FULL_MATRIX_UNIT_ORBITAL_COO_CERTIFIED"
        and full_coo_report.get("all_checks_pass") is True,
        "support_manifest_has_1011_rows": len(support_rows) == 1011,
        "top_support_replaced_with_full_coo_985_rows": len(top_rows) == RELATION_COUNT,
        "registered_subsupport_rows_preserved": len(subsupport_rows) == 26,
        "all_rows_dereference_full_coo": all(
            int(row["full_coo_row_count"]) == int(row["nonzero_coefficients"]) for row in support_rows
        ),
        "top_rows_follow_full_coo_order": all(
            int(top_rows[idx]["full_unit_column"]) == idx for idx in range(len(top_rows))
        ),
        "support_coo_rows_match_nonzero_count": len(support_coo_rows)
        == sum(int(row["nonzero_coefficients"]) for row in support_rows),
        "registered_subsupport_rows_use_registered_source": all(
            row["coefficient_source"] == "REGISTERED_SUPPORT_COO" for row in subsupport_rows
        ),
        "perennial_join_key_emitted_when_available": perennial_maps is None
        or (
            perennial_stats["support_manifest"]["rows_with_perennial_id"]
            == perennial_stats["support_manifest"]["rows_with_direct_sector"]
            == len(support_rows)
            and perennial_stats["support_coo"]["rows_with_perennial_id"]
            == perennial_stats["support_coo"]["rows_with_direct_sector"]
            == len(support_coo_rows)
            and perennial_stats["support_manifest"]["sector_mismatch_count"] == 0
            and perennial_stats["support_coo"]["sector_mismatch_count"] == 0
            and perennial_stats["projector_summary"]["sector_mismatch_count"] == 0
        ),
        **projector_checks["checks"],
    }
    report = {
        "schema": "d20.theorem.tiny_pointer_a985_support_full_matrix_unit_orbital_coo.source_drop",
        "status": STATUS if all(checks.values()) else "D20_TINY_POINTER_A985_SUPPORT_FULL_MATRIX_UNIT_ORBITAL_COO_NEEDS_REVIEW",
        "object": "d20",
        "field_prime": FIELD_PRIME,
        "claim": (
            "The registered support matrix-unit layer is now dereferenced through the all-39 "
            "source-sector-labeled raw-orbital matrix-unit COO table. The top support is replaced by the "
            "full COO-backed table, registered subsupport rows retain their support labels, and all "
            "support projectors are emitted as sums of full COO diagonal matrix units."
        ),
        "inputs": {
            "registered_support_matrix_units": {
                "path": rel(REGISTERED_DIR / "report.json"),
                "sha256": sha_file(REGISTERED_DIR / "report.json"),
            },
            "sector_matrix_unit_transport": {
                "path": rel(SECTOR_TRANSPORT_DIR / "report.json"),
                "sha256": sha_file(SECTOR_TRANSPORT_DIR / "report.json"),
            },
            "full_matrix_unit_orbital_coo": {
                "path": rel(FULL_COO_DIR / "report.json"),
                "sha256": sha_file(FULL_COO_DIR / "report.json"),
            },
            "central_idempotents": {
                "path": rel(CENTRAL_DIR / "a985_center_and_primitive_central_idempotents.npz"),
                "sha256": sha_file(CENTRAL_DIR / "a985_center_and_primitive_central_idempotents.npz"),
            },
            "t985_tensor": {"path": rel(TENSOR_NPZ), "sha256": sha_file(TENSOR_NPZ)},
        },
        "checks": checks,
        "derived": {
            "support_matrix_unit_rows": len(support_rows),
            "top_support_rows": len(top_rows),
            "registered_subsupport_rows": len(subsupport_rows),
            "support_orbital_coo_rows": len(support_coo_rows),
            "support_projector_count": int(projectors.shape[1]),
            "support_projector_coo_rows": len(projector_coo_rows),
            "support_matrix_units_sha256": array_digest(matrix_units[:, [row["full_unit_column"] for row in support_rows]]),
            "support_projectors_sha256": array_digest(projectors),
            "support_row_source_counts": {key: int(value) for key, value in sorted(row_source_counts.items())},
            "coefficient_source_counts": {key: int(value) for key, value in sorted(coefficient_source_counts.items())},
            "projector_products": projector_checks["products"],
            "perennial_join_key": {
                "map_available": perennial_maps is not None,
                "support_manifest_rows_resolved": int(perennial_stats["support_manifest"]["rows_with_perennial_id"]),
                "support_coo_rows_resolved": int(perennial_stats["support_coo"]["rows_with_perennial_id"]),
                "projector_summary_set_columns_added": perennial_stats["projector_summary"]["added_columns"],
            },
            "tables": {
                "arrays": rel(OUT_DIR / "support_matrix_units_and_projectors_raw_orbital_arrays.npz"),
                "support_manifest": rel(OUT_DIR / "support_matrix_units_orbital_manifest.csv"),
                "support_coo": rel(OUT_DIR / "support_matrix_units_orbital_coo.csv"),
                "projector_summary": rel(OUT_DIR / "support_projector_summary.csv"),
                "projector_coo": rel(OUT_DIR / "support_projectors_orbital_coo.csv"),
            },
        },
        "next_highest_yield_item": (
            "Use the support projectors to build support-restricted multiplication tables and "
            "separate the remaining sector-local matrix-unit change-of-basis obligations from "
            "support-level dereferencing."
        ),
        "all_checks_pass": all(checks.values()),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    manifest = {
        "schema": "d20.theorem.tiny_pointer_a985_support_full_matrix_unit_orbital_coo_manifest.source_drop",
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
    (OUT_DIR / "support_full_matrix_unit_orbital_coo_report.md").write_text(markdown_report(report), encoding="utf-8")
    update_theorem_index(report)
    return report


def verify_support_full_coo() -> dict[str, Any]:
    report = load_json(OUT_DIR / "report.json")
    manifest_rows = read_csv_rows(OUT_DIR / "support_matrix_units_orbital_manifest.csv")
    support_coo_rows = read_csv_rows(OUT_DIR / "support_matrix_units_orbital_coo.csv")
    projector_rows = read_csv_rows(OUT_DIR / "support_projector_summary.csv")
    projector_coo_rows = read_csv_rows(OUT_DIR / "support_projectors_orbital_coo.csv")
    arrays = np.load(OUT_DIR / "support_matrix_units_and_projectors_raw_orbital_arrays.npz")
    perennial_available = bool(report.get("derived", {}).get("perennial_join_key", {}).get("map_available"))
    checks = {
        "report_status_certified": report.get("status") == STATUS,
        "report_checks_pass": report.get("all_checks_pass") is True,
        "support_arrays_shape_is_985_by_1011": list(arrays["support_matrix_units"].shape) == [RELATION_COUNT, 1011],
        "projector_arrays_shape_is_985_by_7": list(arrays["support_projectors"].shape) == [RELATION_COUNT, 7],
        "manifest_has_1011_rows": len(manifest_rows) == 1011,
        "top_support_has_985_rows": sum(row["support_name"] == "unit_top_all_39" for row in manifest_rows) == RELATION_COUNT,
        "projector_summary_has_7_rows": len(projector_rows) == 7,
        "support_coo_rows_match_report": len(support_coo_rows)
        == report.get("derived", {}).get("support_orbital_coo_rows"),
        "projector_coo_rows_match_report": len(projector_coo_rows)
        == report.get("derived", {}).get("support_projector_coo_rows"),
        "support_coo_rows_match_arrays": len(support_coo_rows)
        == int(np.count_nonzero(arrays["support_matrix_units"] % FIELD_PRIME)),
        "projector_coo_rows_match_arrays": len(projector_coo_rows)
        == int(np.count_nonzero(arrays["support_projectors"] % FIELD_PRIME)),
        "perennial_join_key_present_when_available": not perennial_available
        or (
            all(row.get("perennial_id", "").startswith("a985pf.") for row in manifest_rows)
            and all(row.get("coordinate_fingerprint_id", "").startswith("a985coord.") for row in manifest_rows)
            and all(row.get("perennial_id", "").startswith("a985pf.") for row in support_coo_rows)
            and all(row.get("coordinate_fingerprint_id", "").startswith("a985coord.") for row in support_coo_rows)
            and "transported_source_support_perennial_ids" in projector_rows[0]
            and "raw_support_perennial_ids" in projector_rows[0]
        ),
    }
    return {
        "status": "D20_TINY_POINTER_A985_SUPPORT_FULL_MATRIX_UNIT_ORBITAL_COO_VERIFIED"
        if all(checks.values())
        else "D20_TINY_POINTER_A985_SUPPORT_FULL_MATRIX_UNIT_ORBITAL_COO_VERIFY_FAILED",
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if not args.verify_only:
        build_support_full_coo()
    verification = verify_support_full_coo()
    print(json.dumps(verification, indent=2, sort_keys=True))
    if not verification["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

