from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS


PERENNIAL_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_perennial_sector_fingerprints"
PERENNIAL_TABLE = PERENNIAL_DIR / "perennial_sector_fingerprints.csv"
SOURCE_SET_COLUMNS = (
    "transported_source_support",
    "trace_support_source_sectors",
    "sector_support",
    "zero_sectors",
    "zero_member_sectors",
    "nonzero_member_sectors",
    "constructed_kernel_intersection",
)
RAW_SET_COLUMNS = ("raw_support", "trace_support_raw_sectors")


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


def load_perennial_sector_maps(path: Path = PERENNIAL_TABLE) -> dict[str, dict[int | str, dict[str, Any]]]:
    rows = read_csv_rows(path)
    by_source: dict[int, dict[str, Any]] = {}
    by_raw: dict[int, dict[str, Any]] = {}
    by_perennial: dict[str, dict[str, Any]] = {}
    for row in rows:
        record = {
            "source_sector": int(row["source_sector"]),
            "raw_sector": int(row["raw_sector"]),
            "perennial_id": row["perennial_id"],
            "coordinate_fingerprint_id": row["coordinate_fingerprint_id"],
            "block_dimension": int(row["block_dimension"]),
            "matrix_unit_count": int(row["matrix_unit_count"]),
        }
        by_source[record["source_sector"]] = record
        by_raw[record["raw_sector"]] = record
        by_perennial[record["perennial_id"]] = record
    return {"by_source": by_source, "by_raw": by_raw, "by_perennial": by_perennial}


def load_perennial_sector_maps_if_available(
    path: Path = PERENNIAL_TABLE,
) -> dict[str, dict[int | str, dict[str, Any]]] | None:
    if not path.exists():
        return None
    return load_perennial_sector_maps(path)


def parse_int_collection(value: str) -> list[int]:
    text = str(value).strip()
    if not text or text == "{}" or text == "[]":
        return []
    if text[0] in "[{" and text[-1] in "]}":
        text = text[1:-1].strip()
    if not text:
        return []
    return [int(part.strip()) for part in text.split(",") if part.strip()]


def ids_for_source_collection(value: str, by_source: dict[int, dict[str, Any]]) -> list[str]:
    return [by_source[item]["perennial_id"] for item in parse_int_collection(value) if item in by_source]


def ids_for_raw_collection(value: str, by_raw: dict[int, dict[str, Any]]) -> list[str]:
    return [by_raw[item]["perennial_id"] for item in parse_int_collection(value) if item in by_raw]


def maybe_int(value: Any) -> int | None:
    text = str(value).strip()
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def append_unique(fieldnames: list[str], *new_fields: str) -> list[str]:
    out = list(fieldnames)
    for field in new_fields:
        if field not in out:
            out.append(field)
    return out


def needs_a985_perennial_id_augmentation(fieldnames: list[str]) -> bool:
    fields = set(fieldnames)
    return bool(
        {"source_sector", "raw_sector"} & fields
        or any(column in fields for column in SOURCE_SET_COLUMNS)
        or any(column in fields for column in RAW_SET_COLUMNS)
    )


def infer_fieldnames(rows: list[dict[str, Any]], fieldnames: list[str] | None) -> list[str]:
    if fieldnames is not None:
        return list(fieldnames)
    if not rows:
        return []
    return list(rows[0].keys())


def augment_a985_sector_rows(
    rows: list[dict[str, Any]],
    fieldnames: list[str] | None = None,
    maps: dict[str, dict[int | str, dict[str, Any]]] | None = None,
) -> tuple[list[str], list[dict[str, Any]], dict[str, Any]]:
    input_fields = infer_fieldnames(rows, fieldnames)
    maps = maps or load_perennial_sector_maps()
    by_source = maps["by_source"]
    by_raw = maps["by_raw"]
    needs_augmentation = needs_a985_perennial_id_augmentation(input_fields)

    output_fields = list(input_fields)
    added_columns: list[str] = []
    if "source_sector" in input_fields or "raw_sector" in input_fields:
        before = set(output_fields)
        output_fields = append_unique(output_fields, "perennial_id", "coordinate_fingerprint_id")
        added_columns.extend(field for field in ("perennial_id", "coordinate_fingerprint_id") if field not in before)
    for column in SOURCE_SET_COLUMNS:
        if column in input_fields:
            out_col = f"{column}_perennial_ids"
            if out_col not in output_fields:
                output_fields.append(out_col)
                added_columns.append(out_col)
    for column in RAW_SET_COLUMNS:
        if column in input_fields:
            out_col = f"{column}_perennial_ids"
            if out_col not in output_fields:
                output_fields.append(out_col)
                added_columns.append(out_col)

    augmented_rows: list[dict[str, Any]] = []
    rows_with_direct_sector = 0
    rows_with_perennial_id = 0
    sector_mismatch_count = 0
    unresolved_direct_rows = 0
    for row in rows:
        out = dict(row)
        source_record = None
        raw_record = None
        source = maybe_int(row.get("source_sector", "")) if "source_sector" in input_fields else None
        raw = maybe_int(row.get("raw_sector", "")) if "raw_sector" in input_fields else None
        if source is not None:
            source_record = by_source.get(source)
        if raw is not None:
            raw_record = by_raw.get(raw)
        if source is not None or raw is not None:
            rows_with_direct_sector += 1
        if source_record and raw_record and source_record["perennial_id"] != raw_record["perennial_id"]:
            sector_mismatch_count += 1
        record = source_record or raw_record
        if record:
            out["perennial_id"] = record["perennial_id"]
            out["coordinate_fingerprint_id"] = record["coordinate_fingerprint_id"]
            rows_with_perennial_id += 1
        elif "source_sector" in input_fields or "raw_sector" in input_fields:
            out["perennial_id"] = out.get("perennial_id", "")
            out["coordinate_fingerprint_id"] = out.get("coordinate_fingerprint_id", "")
            if source is not None or raw is not None:
                unresolved_direct_rows += 1
        for column in SOURCE_SET_COLUMNS:
            if column in input_fields:
                out[f"{column}_perennial_ids"] = "|".join(
                    ids_for_source_collection(row.get(column, ""), by_source)
                )
        for column in RAW_SET_COLUMNS:
            if column in input_fields:
                out[f"{column}_perennial_ids"] = "|".join(ids_for_raw_collection(row.get(column, ""), by_raw))
        augmented_rows.append(out)

    stats = {
        "needs_augmentation": needs_augmentation,
        "row_count": len(rows),
        "added_columns": added_columns,
        "has_source_sector": "source_sector" in input_fields,
        "has_raw_sector": "raw_sector" in input_fields,
        "has_source_set_column": any(column in input_fields for column in SOURCE_SET_COLUMNS),
        "has_raw_set_column": any(column in input_fields for column in RAW_SET_COLUMNS),
        "rows_with_direct_sector": rows_with_direct_sector,
        "rows_with_perennial_id": rows_with_perennial_id,
        "unresolved_direct_rows": unresolved_direct_rows,
        "sector_mismatch_count": sector_mismatch_count,
    }
    return output_fields, augmented_rows, stats


def write_a985_sector_csv_rows(
    path: Path,
    fieldnames: list[str],
    rows: list[dict[str, Any]],
    maps: dict[str, dict[int | str, dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    output_fields, output_rows, stats = augment_a985_sector_rows(rows, fieldnames, maps)
    write_csv_rows(path, output_fields, output_rows)
    return stats


def write_a985_sector_csv_rows_if_available(
    path: Path,
    fieldnames: list[str],
    rows: list[dict[str, Any]],
    maps: dict[str, dict[int | str, dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    maps = maps or load_perennial_sector_maps_if_available()
    if maps is None:
        write_csv_rows(path, fieldnames, rows)
        return {
            "needs_augmentation": needs_a985_perennial_id_augmentation(fieldnames),
            "row_count": len(rows),
            "added_columns": [],
            "has_source_sector": "source_sector" in fieldnames,
            "has_raw_sector": "raw_sector" in fieldnames,
            "has_source_set_column": any(column in fieldnames for column in SOURCE_SET_COLUMNS),
            "has_raw_set_column": any(column in fieldnames for column in RAW_SET_COLUMNS),
            "rows_with_direct_sector": 0,
            "rows_with_perennial_id": 0,
            "unresolved_direct_rows": 0,
            "sector_mismatch_count": 0,
            "perennial_map_available": False,
        }
    stats = write_a985_sector_csv_rows(path, fieldnames, rows, maps)
    stats["perennial_map_available"] = True
    return stats

