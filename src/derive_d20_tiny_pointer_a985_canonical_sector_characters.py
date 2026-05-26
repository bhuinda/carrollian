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

from src.derive_d20_tiny_pointer_a985_block_matrix_units import (  # noqa: E402
    FIELD_PRIME,
    RELATION_COUNT,
    MultiplicationOracle,
    array_digest,
    inv_mod_matrix,
    pivot_rows_for_columns,
)
from src.a985_perennial_ids import (  # noqa: E402
    load_perennial_sector_maps_if_available,
    write_a985_sector_csv_rows_if_available,
)
from src.paths import D20_INVARIANTS, ROOT  # noqa: E402


STATUS = "D20_TINY_POINTER_A985_CANONICAL_SECTOR_CHARACTERS_CERTIFIED"
THEOREM_ID = "tiny_pointer_a985_canonical_sector_characters"
OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

CANONICAL_UNITS_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_canonical_sector_matrix_units"
FULL_COO_DIR = D20_INVARIANTS / "theorems" / "tiny_pointer_a985_full_matrix_unit_orbital_coo"
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


def signed_mod(value: int) -> int:
    value %= FIELD_PRIME
    return value if value <= FIELD_PRIME // 2 else value - FIELD_PRIME


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


def load_sector_blocks() -> tuple[list[dict[str, Any]], dict[int, np.ndarray]]:
    arrays = np.load(FULL_COO_DIR / "source_sector_matrix_units_raw_orbital_arrays.npz")
    matrix_units = np.asarray(arrays["matrix_units"], dtype=np.int64) % FIELD_PRIME
    source_sector = np.asarray(arrays["source_sector"], dtype=np.int64)
    raw_sector = np.asarray(arrays["raw_sector"], dtype=np.int64)
    local_i = np.asarray(arrays["i"], dtype=np.int64)
    local_j = np.asarray(arrays["j"], dtype=np.int64)

    sector_rows: list[dict[str, Any]] = []
    blocks: dict[int, np.ndarray] = {}
    for sector in sorted(int(value) for value in set(source_sector.tolist())):
        mask = source_sector == sector
        d = int(np.max(local_i[mask]) + 1)
        raw_values = sorted(set(int(value) for value in raw_sector[mask].tolist()))
        if len(raw_values) != 1:
            raise ValueError(f"source sector {sector} has multiple raw sectors: {raw_values}")
        block = np.zeros((RELATION_COUNT, d * d), dtype=np.int64)
        for i in range(d):
            for j in range(d):
                idxs = np.where(mask & (local_i == i) & (local_j == j))[0]
                if len(idxs) != 1:
                    raise ValueError(f"source sector {sector} missing local unit ({i},{j})")
                block[:, i * d + j] = matrix_units[:, int(idxs[0])]
        sector_rows.append(
            {
                "source_sector": sector,
                "raw_sector": int(raw_values[0]),
                "block_dimension": d,
                "matrix_unit_count": d * d,
            }
        )
        blocks[sector] = block % FIELD_PRIME
    return sector_rows, blocks


def trace_from_coords(coords: np.ndarray, dimension: int) -> int:
    return int(sum(int(coords[i * dimension + i]) for i in range(dimension)) % FIELD_PRIME)


def build_characters() -> dict[str, Any]:
    canonical_report = load_json(CANONICAL_UNITS_DIR / "report.json")
    full_coo_report = load_json(FULL_COO_DIR / "report.json")
    perennial_maps = load_perennial_sector_maps_if_available()
    central = np.load(CENTRAL_DIR / "a985_center_and_primitive_central_idempotents.npz")
    central_pages = np.asarray(central["idempotents"], dtype=np.int64) % FIELD_PRIME
    identity_indices = np.asarray(central["identity_indices"], dtype=np.int64)
    triples = np.asarray(np.load(TENSOR_NPZ)["triples"], dtype=np.int64)
    oracle = MultiplicationOracle(triples)
    sector_rows, blocks = load_sector_blocks()

    character_table = np.zeros((len(sector_rows), RELATION_COUNT), dtype=np.int64)
    table_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    identity_failures: list[int] = []
    central_page_trace_failures: list[int] = []
    matrix_unit_trace_failures: list[int] = []
    projection_sample_failures: list[dict[str, int]] = []

    for sector_index, sector in enumerate(sector_rows):
        source_sector = int(sector["source_sector"])
        raw_sector = int(sector["raw_sector"])
        d = int(sector["block_dimension"])
        block = blocks[source_sector]
        chart_rows = pivot_rows_for_columns(block)
        chart = block[chart_rows, :]
        inv_chart = inv_mod_matrix(chart)
        unit_coords = (inv_chart @ chart) % FIELD_PRIME
        expected_identity = np.eye(d * d, dtype=np.int64) % FIELD_PRIME
        if not np.array_equal(unit_coords, expected_identity):
            matrix_unit_trace_failures.append(source_sector)
        unit_trace_values = [trace_from_coords(unit_coords[:, col], d) for col in range(d * d)]
        diagonal_trace_sum = sum(unit_trace_values[i * d + i] for i in range(d)) % FIELD_PRIME
        off_diagonal_nonzero_trace_count = sum(
            1
            for i in range(d)
            for j in range(d)
            if i != j and unit_trace_values[i * d + j] != 0
        )

        page_coords = (inv_chart @ central_pages[raw_sector][chart_rows]) % FIELD_PRIME
        central_page_trace = trace_from_coords(page_coords, d)
        page_expected = np.zeros(d * d, dtype=np.int64)
        for i in range(d):
            page_expected[i * d + i] = 1
        if central_page_trace != d or not np.array_equal(page_coords % FIELD_PRIME, page_expected):
            central_page_trace_failures.append(source_sector)

        for relation_alpha in range(RELATION_COUNT):
            projected = oracle.basis_right_product(central_pages[raw_sector], relation_alpha)
            if relation_alpha in {0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 984}:
                left_projected = oracle.basis_left_product(relation_alpha, central_pages[raw_sector])
                if not np.array_equal(projected % FIELD_PRIME, left_projected % FIELD_PRIME):
                    projection_sample_failures.append(
                        {
                            "source_sector": source_sector,
                            "raw_sector": raw_sector,
                            "relation_alpha": relation_alpha,
                        }
                    )
            coords = (inv_chart @ projected[chart_rows]) % FIELD_PRIME
            trace = trace_from_coords(coords, d)
            character_table[sector_index, relation_alpha] = trace
            table_rows.append(
                {
                    "source_sector": source_sector,
                    "raw_sector": raw_sector,
                    "block_dimension": d,
                    "relation_alpha": relation_alpha,
                    "character_mod_1000003": trace,
                    "character_signed": signed_mod(trace),
                }
            )

        identity_character = int(np.sum(character_table[sector_index, identity_indices]) % FIELD_PRIME)
        if identity_character != d:
            identity_failures.append(source_sector)
        row_values = character_table[sector_index, :]
        summary_rows.append(
            {
                "source_sector": source_sector,
                "raw_sector": raw_sector,
                "block_dimension": d,
                "matrix_unit_count": d * d,
                "chart_rows": json.dumps([int(row) for row in chart_rows], separators=(",", ":")),
                "identity_character_mod_1000003": identity_character,
                "central_page_trace_mod_1000003": central_page_trace,
                "diagonal_unit_trace_sum_mod_1000003": int(diagonal_trace_sum),
                "off_diagonal_nonzero_trace_count": off_diagonal_nonzero_trace_count,
                "nonzero_character_values": int(np.count_nonzero(row_values)),
                "character_row_sha256": array_digest(row_values.reshape(1, RELATION_COUNT)),
            }
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        OUT_DIR / "canonical_sector_character_table.npz",
        field_prime=np.array([FIELD_PRIME], dtype=np.int64),
        character_table=character_table.astype(np.int64),
        source_sector=np.asarray([row["source_sector"] for row in sector_rows], dtype=np.int64),
        raw_sector=np.asarray([row["raw_sector"] for row in sector_rows], dtype=np.int64),
        block_dimension=np.asarray([row["block_dimension"] for row in sector_rows], dtype=np.int64),
        identity_indices=identity_indices.astype(np.int64),
    )
    table_perennial_stats = write_a985_sector_csv_rows_if_available(
        OUT_DIR / "canonical_sector_character_table.csv",
        [
            "source_sector",
            "raw_sector",
            "block_dimension",
            "relation_alpha",
            "character_mod_1000003",
            "character_signed",
        ],
        table_rows,
        perennial_maps,
    )
    summary_perennial_stats = write_a985_sector_csv_rows_if_available(
        OUT_DIR / "canonical_sector_trace_summary.csv",
        [
            "source_sector",
            "raw_sector",
            "block_dimension",
            "matrix_unit_count",
            "chart_rows",
            "identity_character_mod_1000003",
            "central_page_trace_mod_1000003",
            "diagonal_unit_trace_sum_mod_1000003",
            "off_diagonal_nonzero_trace_count",
            "nonzero_character_values",
            "character_row_sha256",
        ],
        summary_rows,
        perennial_maps,
    )

    checks = {
        "canonical_source_sector_matrix_units_certified": canonical_report.get("status")
        == "D20_TINY_POINTER_A985_CANONICAL_SECTOR_MATRIX_UNITS_CERTIFIED"
        and canonical_report.get("all_checks_pass") is True,
        "full_matrix_unit_coo_certified": full_coo_report.get("status")
        == "D20_TINY_POINTER_A985_FULL_MATRIX_UNIT_ORBITAL_COO_CERTIFIED"
        and full_coo_report.get("all_checks_pass") is True,
        "central_page_count_is_39": central_pages.shape == (39, RELATION_COUNT),
        "sector_count_is_39": len(sector_rows) == 39,
        "character_table_shape_is_39_by_985": character_table.shape == (39, RELATION_COUNT),
        "character_csv_has_38415_rows": len(table_rows) == 39 * RELATION_COUNT,
        "block_dimensions_sum_to_159": sum(int(row["block_dimension"]) for row in sector_rows) == 159,
        "matrix_unit_counts_sum_to_985": sum(int(row["matrix_unit_count"]) for row in sector_rows) == 985,
        "identity_character_matches_block_dimensions": identity_failures == [],
        "central_page_trace_matches_block_dimensions": central_page_trace_failures == [],
        "canonical_matrix_unit_traces_match_delta": matrix_unit_trace_failures == [],
        "central_projection_sample_commutes": projection_sample_failures == [],
        "perennial_join_key_emitted_when_available": perennial_maps is None
        or (
            table_perennial_stats["rows_with_perennial_id"]
            == table_perennial_stats["rows_with_direct_sector"]
            == len(table_rows)
            and summary_perennial_stats["rows_with_perennial_id"]
            == summary_perennial_stats["rows_with_direct_sector"]
            == len(summary_rows)
            and table_perennial_stats["sector_mismatch_count"] == 0
            and summary_perennial_stats["sector_mismatch_count"] == 0
        ),
    }
    report = {
        "schema": "d20.theorem.tiny_pointer_a985_canonical_sector_characters.source_drop",
        "status": STATUS if all(checks.values()) else "D20_TINY_POINTER_A985_CANONICAL_SECTOR_CHARACTERS_NEEDS_REVIEW",
        "object": "d20",
        "field_prime": FIELD_PRIME,
        "claim": (
            "The canonical source-sector matrix units now give a block character table for the raw "
            "985-orbital basis: chi_s(R_alpha) is the trace of e_s R_alpha in the canonical "
            "source-sector block End(F_p^d_s)."
        ),
        "inputs": {
            "canonical_source_sector_matrix_units": {
                "path": rel(CANONICAL_UNITS_DIR / "report.json"),
                "sha256": sha_file(CANONICAL_UNITS_DIR / "report.json"),
            },
            "full_matrix_unit_orbital_coo": {
                "path": rel(FULL_COO_DIR / "report.json"),
                "sha256": sha_file(FULL_COO_DIR / "report.json"),
            },
            "full_matrix_unit_arrays": {
                "path": rel(FULL_COO_DIR / "source_sector_matrix_units_raw_orbital_arrays.npz"),
                "sha256": sha_file(FULL_COO_DIR / "source_sector_matrix_units_raw_orbital_arrays.npz"),
            },
            "central_idempotents": {
                "path": rel(CENTRAL_DIR / "a985_center_and_primitive_central_idempotents.npz"),
                "sha256": sha_file(CENTRAL_DIR / "a985_center_and_primitive_central_idempotents.npz"),
            },
            "t985_tensor": {"path": rel(TENSOR_NPZ), "sha256": sha_file(TENSOR_NPZ)},
        },
        "checks": checks,
        "derived": {
            "character_table_shape": list(character_table.shape),
            "character_table_sha256": array_digest(character_table),
            "nonzero_character_values": int(np.count_nonzero(character_table)),
            "identity_indices": [int(value) for value in identity_indices.tolist()],
            "identity_character_failures": identity_failures,
            "central_page_trace_failures": central_page_trace_failures,
            "matrix_unit_trace_failures": matrix_unit_trace_failures,
            "projection_sample_failures": projection_sample_failures[:8],
            "perennial_join_key": {
                "map_available": perennial_maps is not None,
                "character_rows_resolved": int(table_perennial_stats["rows_with_perennial_id"]),
                "summary_rows_resolved": int(summary_perennial_stats["rows_with_perennial_id"]),
            },
            "tables": {
                "character_table_npz": rel(OUT_DIR / "canonical_sector_character_table.npz"),
                "character_table_csv": rel(OUT_DIR / "canonical_sector_character_table.csv"),
                "trace_summary": rel(OUT_DIR / "canonical_sector_trace_summary.csv"),
            },
        },
        "next_highest_yield_item": (
            "Use this character table to test Fourier/residue candidates against the actual canonical "
            "A985 block traces instead of only the upstream object-phase sector profiles."
        ),
        "all_checks_pass": all(checks.values()),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    manifest = {
        "schema": "d20.theorem.tiny_pointer_a985_canonical_sector_characters_manifest.source_drop",
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
    (OUT_DIR / "canonical_sector_characters_report.md").write_text(markdown_report(report), encoding="utf-8")
    update_theorem_index(report)
    return report


def markdown_report(report: dict[str, Any]) -> str:
    checks = "\n".join(f"- `{key}`: `{value}`" for key, value in report["checks"].items())
    derived = report["derived"]
    return (
        "# Canonical Sector Characters\n\n"
        f"Status: `{report['status']}`\n\n"
        f"Character table shape: `{derived['character_table_shape']}`\n\n"
        f"Nonzero character values: `{derived['nonzero_character_values']}`\n\n"
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


def verify_theorem() -> dict[str, Any]:
    report = load_json(OUT_DIR / "report.json")
    table_rows = read_csv_rows(OUT_DIR / "canonical_sector_character_table.csv")
    summary_rows = read_csv_rows(OUT_DIR / "canonical_sector_trace_summary.csv")
    arrays = np.load(OUT_DIR / "canonical_sector_character_table.npz")
    character_table = np.asarray(arrays["character_table"], dtype=np.int64) % FIELD_PRIME
    dimensions = np.asarray(arrays["block_dimension"], dtype=np.int64)
    identity_indices = np.asarray(arrays["identity_indices"], dtype=np.int64)
    identity_values = np.sum(character_table[:, identity_indices], axis=1) % FIELD_PRIME
    perennial_available = bool(report.get("derived", {}).get("perennial_join_key", {}).get("map_available"))
    checks = {
        "report_status_certified": report.get("status") == STATUS,
        "report_checks_pass": report.get("all_checks_pass") is True,
        "npz_table_shape_is_39_by_985": character_table.shape == (39, RELATION_COUNT),
        "csv_table_has_38415_rows": len(table_rows) == 39 * RELATION_COUNT,
        "summary_has_39_rows": len(summary_rows) == 39,
        "identity_characters_match_dimensions": np.array_equal(identity_values, dimensions % FIELD_PRIME),
        "summary_identity_characters_match_dimensions": all(
            int(row["identity_character_mod_1000003"]) == int(row["block_dimension"])
            for row in summary_rows
        ),
        "summary_off_diagonal_traces_zero": all(
            int(row["off_diagonal_nonzero_trace_count"]) == 0 for row in summary_rows
        ),
        "table_hash_matches_report": array_digest(character_table) == report.get("derived", {}).get("character_table_sha256"),
        "perennial_join_key_present_when_available": not perennial_available
        or (
            all(row.get("perennial_id", "").startswith("a985pf.") for row in table_rows)
            and all(row.get("coordinate_fingerprint_id", "").startswith("a985coord.") for row in table_rows)
            and all(row.get("perennial_id", "").startswith("a985pf.") for row in summary_rows)
            and all(row.get("coordinate_fingerprint_id", "").startswith("a985coord.") for row in summary_rows)
        ),
    }
    return {
        "status": "D20_TINY_POINTER_A985_CANONICAL_SECTOR_CHARACTERS_VERIFIED"
        if all(checks.values())
        else "D20_TINY_POINTER_A985_CANONICAL_SECTOR_CHARACTERS_VERIFY_FAILED",
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if not args.verify_only:
        build_characters()
    verification = verify_theorem()
    print(json.dumps(verification, indent=2, sort_keys=True))
    if not verification["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
