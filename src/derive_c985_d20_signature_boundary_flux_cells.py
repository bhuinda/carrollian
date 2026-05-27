from __future__ import annotations

import csv
import json
from collections import defaultdict
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_residual_cell_complex import (
        EDGE_CENTRAL_NEGATIVE,
        EDGE_HIGH_NEGATIVE,
        OUT_DIR as CELL_COMPLEX_DIR,
    )
    from .derive_c985_d20_signature_transfer_spectral_cut import (
        OUT_DIR as SPECTRAL_CUT_DIR,
    )
    from .derive_c985_d20_symbolic_rewrite_rules import csv_text
    from .derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_d20_signature_residual_cell_complex import (
        EDGE_CENTRAL_NEGATIVE,
        EDGE_HIGH_NEGATIVE,
        OUT_DIR as CELL_COMPLEX_DIR,
    )
    from derive_c985_d20_signature_transfer_spectral_cut import (
        OUT_DIR as SPECTRAL_CUT_DIR,
    )
    from derive_c985_d20_symbolic_rewrite_rules import csv_text
    from derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "c985_d20_signature_boundary_flux_cells"
STATUS = "C985_D20_SIGNATURE_BOUNDARY_FLUX_CELLS_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

CELL_COMPLEX_REPORT = CELL_COMPLEX_DIR / "report.json"
CELL_COMPLEX_JSON = CELL_COMPLEX_DIR / "signature_residual_cell_complex.json"
CELL_COMPLEX_TABLES = CELL_COMPLEX_DIR / "signature_residual_cell_complex_tables.npz"
CELL_COMPLEX_CERTIFICATE = CELL_COMPLEX_DIR / "signature_residual_cell_complex_certificate.json"
CELL_COMPLEX_VERTICES = CELL_COMPLEX_DIR / "carrier_region_vertices.csv"
CELL_COMPLEX_EDGES = CELL_COMPLEX_DIR / "carrier_region_edges.csv"

SPECTRAL_CUT_REPORT = SPECTRAL_CUT_DIR / "report.json"
SPECTRAL_CUT_JSON = SPECTRAL_CUT_DIR / "signature_transfer_spectral_cut.json"
SPECTRAL_CUT_TABLES = SPECTRAL_CUT_DIR / "signature_transfer_spectral_cut_tables.npz"
SPECTRAL_CUT_CERTIFICATE = SPECTRAL_CUT_DIR / "signature_transfer_spectral_cut_certificate.json"
SPECTRAL_CUT_EDGES = SPECTRAL_CUT_DIR / "signature_eigenmode_cut_edges.csv"
SPECTRAL_MASK_SUMMARY = SPECTRAL_CUT_DIR / "carrier_mask_eigenmode_summary.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_c985_d20_signature_boundary_flux_cells.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_d20_signature_boundary_flux_cells.py"

PROBABILITY_SCALE = 1_000_000_000_000

BOUNDARY_SIGNATURE_EDGE_COLUMNS = [
    "cut_edge_id",
    "transfer_edge_id",
    "source_signature_class_id",
    "target_signature_class_id",
    "source_carrier_mask_class_id",
    "target_carrier_mask_class_id",
    "boundary_partition_code",
    "source_region_code",
    "target_region_code",
    "shared_active_atom_count",
    "undirected_stationary_flux_x1e12",
    "source_carrier_atom_mask",
    "target_carrier_atom_mask",
]

BOUNDARY_MASK_EDGE_COLUMNS = [
    "boundary_mask_edge_id",
    "source_carrier_mask_class_id",
    "target_carrier_mask_class_id",
    "boundary_partition_code",
    "source_region_code",
    "target_region_code",
    "signature_cut_edge_count",
    "undirected_stationary_flux_x1e12",
    "flux_fraction_of_total_cut_x1e12",
    "shared_active_atom_sum",
    "source_carrier_atom_mask",
    "target_carrier_atom_mask",
]

BOUNDARY_PARTITION_COLUMNS = [
    "boundary_partition_code",
    "mask_edge_count",
    "signature_cut_edge_count",
    "undirected_stationary_flux_x1e12",
    "flux_fraction_of_total_cut_x1e12",
    "shared_active_atom_sum",
    "top_boundary_source_mask_class_id",
    "top_boundary_target_mask_class_id",
    "top_boundary_flux_x1e12",
]

BOUNDARY_FLUX_OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "signature_cut_edge_count": 0,
    "carrier_boundary_edge_count": 1,
    "total_undirected_cut_flux": 2,
    "high_negative_mask_edge_count": 3,
    "high_negative_signature_edge_count": 4,
    "high_negative_undirected_cut_flux": 5,
    "high_negative_flux_fraction": 6,
    "central_negative_mask_edge_count": 7,
    "central_negative_signature_edge_count": 8,
    "central_negative_undirected_cut_flux": 9,
    "central_negative_flux_fraction": 10,
    "top_boundary_pair_source": 11,
    "top_boundary_pair_target": 12,
    "top_boundary_pair_flux": 13,
    "top_boundary_pair_flux_fraction": 14,
    "shared_active_atom_sum": 15,
    "unexpected_boundary_partition_count": 16,
}


def scaled_ratio(numerator: int, denominator: int) -> int:
    scaled = int(numerator) * PROBABILITY_SCALE
    quotient, remainder = divmod(scaled, int(denominator))
    if 2 * remainder >= int(denominator):
        quotient += 1
    return int(quotient)


def table_from_rows(columns: list[str], rows: list[dict[str, int]]) -> np.ndarray:
    return np.asarray(
        [[int(row[column]) for column in columns] for row in rows],
        dtype=np.int64,
    )


def read_int_csv(path: Any) -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows.append({key: int(value) for key, value in row.items()})
    return rows


def boundary_partition_code(left_region: int, right_region: int) -> int:
    pair = {int(left_region), int(right_region)}
    if pair == {2, -1}:
        return EDGE_HIGH_NEGATIVE
    if pair == {1, -1}:
        return EDGE_CENTRAL_NEGATIVE
    raise ValueError(f"unexpected boundary regions: {left_region}, {right_region}")


def build_payloads() -> dict[str, Any]:
    cell_report = load_json(CELL_COMPLEX_REPORT)
    cell_complex = load_json(CELL_COMPLEX_JSON)
    cell_certificate = load_json(CELL_COMPLEX_CERTIFICATE)
    spectral_report = load_json(SPECTRAL_CUT_REPORT)
    spectral_cut = load_json(SPECTRAL_CUT_JSON)
    spectral_certificate = load_json(SPECTRAL_CUT_CERTIFICATE)
    cell_tables = np.load(CELL_COMPLEX_TABLES, allow_pickle=False)
    spectral_tables = np.load(SPECTRAL_CUT_TABLES, allow_pickle=False)

    carrier_rows = read_int_csv(CELL_COMPLEX_VERTICES)
    cell_edge_rows = read_int_csv(CELL_COMPLEX_EDGES)
    cut_edge_source_rows = read_int_csv(SPECTRAL_CUT_EDGES)
    spectral_mask_rows = read_int_csv(SPECTRAL_MASK_SUMMARY)

    mask_to_carrier = {
        int(row["carrier_atom_mask"]): int(row["carrier_mask_class_id"])
        for row in carrier_rows
    }
    carrier_region = {
        int(row["carrier_mask_class_id"]): int(row["elbow_region_code"])
        for row in carrier_rows
    }
    carrier_mask = {
        int(row["carrier_mask_class_id"]): int(row["carrier_atom_mask"])
        for row in carrier_rows
    }
    boundary_cell_pairs = {
        tuple(sorted((int(row["source_carrier_mask_class_id"]), int(row["target_carrier_mask_class_id"]))))
        for row in cell_edge_rows
        if int(row["is_positive_negative_boundary"]) == 1
    }
    spectral_boundary_degree = {
        int(row["carrier_mask_class_id"]): int(row["cut_boundary_mask_edge_count"])
        for row in spectral_mask_rows
    }

    signature_edge_rows: list[dict[str, int]] = []
    pair_accumulator: dict[tuple[int, int], dict[str, int]] = defaultdict(
        lambda: {
            "signature_cut_edge_count": 0,
            "undirected_stationary_flux_x1e12": 0,
            "shared_active_atom_sum": 0,
        }
    )
    partition_accumulator: dict[int, dict[str, int]] = defaultdict(
        lambda: {
            "mask_edge_count": 0,
            "signature_cut_edge_count": 0,
            "undirected_stationary_flux_x1e12": 0,
            "shared_active_atom_sum": 0,
            "top_boundary_source_mask_class_id": -1,
            "top_boundary_target_mask_class_id": -1,
            "top_boundary_flux_x1e12": -1,
        }
    )

    unexpected_partition_count = 0
    for row in cut_edge_source_rows:
        source_mask_class = mask_to_carrier[int(row["source_carrier_atom_mask"])]
        target_mask_class = mask_to_carrier[int(row["target_carrier_atom_mask"])]
        source_region = carrier_region[source_mask_class]
        target_region = carrier_region[target_mask_class]
        try:
            partition_code = boundary_partition_code(source_region, target_region)
        except ValueError:
            unexpected_partition_count += 1
            partition_code = -999
        key = tuple(sorted((source_mask_class, target_mask_class)))
        signature_edge_rows.append(
            {
                "cut_edge_id": int(row["cut_edge_id"]),
                "transfer_edge_id": int(row["transfer_edge_id"]),
                "source_signature_class_id": int(row["source_signature_class_id"]),
                "target_signature_class_id": int(row["target_signature_class_id"]),
                "source_carrier_mask_class_id": source_mask_class,
                "target_carrier_mask_class_id": target_mask_class,
                "boundary_partition_code": partition_code,
                "source_region_code": source_region,
                "target_region_code": target_region,
                "shared_active_atom_count": int(row["shared_active_atom_count"]),
                "undirected_stationary_flux_x1e12": int(row["undirected_stationary_flux_x1e12"]),
                "source_carrier_atom_mask": int(row["source_carrier_atom_mask"]),
                "target_carrier_atom_mask": int(row["target_carrier_atom_mask"]),
            }
        )
        pair_accumulator[key]["signature_cut_edge_count"] += 1
        pair_accumulator[key]["undirected_stationary_flux_x1e12"] += int(
            row["undirected_stationary_flux_x1e12"]
        )
        pair_accumulator[key]["shared_active_atom_sum"] += int(
            row["shared_active_atom_count"]
        )

    mask_edge_rows: list[dict[str, int]] = []
    for edge_id, key in enumerate(sorted(pair_accumulator)):
        left, right = key
        left_region = carrier_region[left]
        right_region = carrier_region[right]
        partition_code = boundary_partition_code(left_region, right_region)
        data = pair_accumulator[key]
        mask_edge_rows.append(
            {
                "boundary_mask_edge_id": edge_id,
                "source_carrier_mask_class_id": left,
                "target_carrier_mask_class_id": right,
                "boundary_partition_code": partition_code,
                "source_region_code": left_region,
                "target_region_code": right_region,
                "signature_cut_edge_count": int(data["signature_cut_edge_count"]),
                "undirected_stationary_flux_x1e12": int(
                    data["undirected_stationary_flux_x1e12"]
                ),
                "flux_fraction_of_total_cut_x1e12": 0,
                "shared_active_atom_sum": int(data["shared_active_atom_sum"]),
                "source_carrier_atom_mask": carrier_mask[left],
                "target_carrier_atom_mask": carrier_mask[right],
            }
        )

    total_cut_flux = int(
        sum(int(row["undirected_stationary_flux_x1e12"]) for row in signature_edge_rows)
    )
    for row in mask_edge_rows:
        row["flux_fraction_of_total_cut_x1e12"] = scaled_ratio(
            int(row["undirected_stationary_flux_x1e12"]),
            total_cut_flux,
        )
        partition = partition_accumulator[int(row["boundary_partition_code"])]
        partition["mask_edge_count"] += 1
        partition["signature_cut_edge_count"] += int(row["signature_cut_edge_count"])
        partition["undirected_stationary_flux_x1e12"] += int(
            row["undirected_stationary_flux_x1e12"]
        )
        partition["shared_active_atom_sum"] += int(row["shared_active_atom_sum"])
        if int(row["undirected_stationary_flux_x1e12"]) > int(
            partition["top_boundary_flux_x1e12"]
        ):
            partition["top_boundary_source_mask_class_id"] = int(
                row["source_carrier_mask_class_id"]
            )
            partition["top_boundary_target_mask_class_id"] = int(
                row["target_carrier_mask_class_id"]
            )
            partition["top_boundary_flux_x1e12"] = int(
                row["undirected_stationary_flux_x1e12"]
            )

    partition_rows: list[dict[str, int]] = []
    for partition_code in (EDGE_HIGH_NEGATIVE, EDGE_CENTRAL_NEGATIVE):
        data = partition_accumulator[partition_code]
        partition_rows.append(
            {
                "boundary_partition_code": partition_code,
                "mask_edge_count": int(data["mask_edge_count"]),
                "signature_cut_edge_count": int(data["signature_cut_edge_count"]),
                "undirected_stationary_flux_x1e12": int(
                    data["undirected_stationary_flux_x1e12"]
                ),
                "flux_fraction_of_total_cut_x1e12": scaled_ratio(
                    int(data["undirected_stationary_flux_x1e12"]),
                    total_cut_flux,
                ),
                "shared_active_atom_sum": int(data["shared_active_atom_sum"]),
                "top_boundary_source_mask_class_id": int(
                    data["top_boundary_source_mask_class_id"]
                ),
                "top_boundary_target_mask_class_id": int(
                    data["top_boundary_target_mask_class_id"]
                ),
                "top_boundary_flux_x1e12": int(data["top_boundary_flux_x1e12"]),
            }
        )

    top_boundary_row = max(
        mask_edge_rows,
        key=lambda row: (
            int(row["undirected_stationary_flux_x1e12"]),
            -int(row["source_carrier_mask_class_id"]),
            -int(row["target_carrier_mask_class_id"]),
        ),
    )
    high_partition = next(
        row for row in partition_rows if int(row["boundary_partition_code"]) == EDGE_HIGH_NEGATIVE
    )
    central_partition = next(
        row for row in partition_rows if int(row["boundary_partition_code"]) == EDGE_CENTRAL_NEGATIVE
    )

    observable_values = {
        "signature_cut_edge_count": len(signature_edge_rows),
        "carrier_boundary_edge_count": len(mask_edge_rows),
        "total_undirected_cut_flux": total_cut_flux,
        "high_negative_mask_edge_count": int(high_partition["mask_edge_count"]),
        "high_negative_signature_edge_count": int(high_partition["signature_cut_edge_count"]),
        "high_negative_undirected_cut_flux": int(
            high_partition["undirected_stationary_flux_x1e12"]
        ),
        "high_negative_flux_fraction": int(
            high_partition["flux_fraction_of_total_cut_x1e12"]
        ),
        "central_negative_mask_edge_count": int(central_partition["mask_edge_count"]),
        "central_negative_signature_edge_count": int(
            central_partition["signature_cut_edge_count"]
        ),
        "central_negative_undirected_cut_flux": int(
            central_partition["undirected_stationary_flux_x1e12"]
        ),
        "central_negative_flux_fraction": int(
            central_partition["flux_fraction_of_total_cut_x1e12"]
        ),
        "top_boundary_pair_source": int(top_boundary_row["source_carrier_mask_class_id"]),
        "top_boundary_pair_target": int(top_boundary_row["target_carrier_mask_class_id"]),
        "top_boundary_pair_flux": int(top_boundary_row["undirected_stationary_flux_x1e12"]),
        "top_boundary_pair_flux_fraction": scaled_ratio(
            int(top_boundary_row["undirected_stationary_flux_x1e12"]),
            total_cut_flux,
        ),
        "shared_active_atom_sum": int(
            sum(int(row["shared_active_atom_count"]) for row in signature_edge_rows)
        ),
        "unexpected_boundary_partition_count": unexpected_partition_count,
    }
    observable_rows = [
        {
            "observable_id": index,
            "observable_code": int(code),
            "value_x1e12": int(observable_values[name]),
            "aux_id": -1,
        }
        for index, (name, code) in enumerate(
            sorted(OBSERVABLE_CODES.items(), key=lambda item: item[1])
        )
    ]

    signature_edge_table = table_from_rows(
        BOUNDARY_SIGNATURE_EDGE_COLUMNS,
        signature_edge_rows,
    )
    mask_edge_table = table_from_rows(BOUNDARY_MASK_EDGE_COLUMNS, mask_edge_rows)
    partition_table = table_from_rows(BOUNDARY_PARTITION_COLUMNS, partition_rows)
    observable_table = table_from_rows(
        BOUNDARY_FLUX_OBSERVABLE_COLUMNS,
        observable_rows,
    )

    boundary_pair_set = {
        tuple(sorted((int(row["source_carrier_mask_class_id"]), int(row["target_carrier_mask_class_id"]))))
        for row in mask_edge_rows
    }
    spectral_boundary_degree_from_flux = defaultdict(int)
    for pair in boundary_pair_set:
        left, right = pair
        spectral_boundary_degree_from_flux[left] += 1
        spectral_boundary_degree_from_flux[right] += 1
    degree_l1_delta = sum(
        abs(spectral_boundary_degree_from_flux[index] - spectral_boundary_degree[index])
        for index in range(14)
    )

    boundary_flux = {
        "schema": "c985.d20_signature_boundary_flux_cells@1",
        "object": "d20",
        "flux_rule": {
            "source": "certified spectral-cut signature crossing edges",
            "boundary_cells": "certified residual cell-complex carrier-mask positive-negative boundary",
            "partition": "high-negative versus central-negative carrier boundary contact",
            "flux": "undirected stationary flux at exact scale 1e12 from the signature spectral cut",
        },
        "partition_summary": [
            {key: int(value) for key, value in row.items()} for row in partition_rows
        ],
        "top_boundary_pair": {
            "source_carrier_mask_class_id": int(
                top_boundary_row["source_carrier_mask_class_id"]
            ),
            "target_carrier_mask_class_id": int(
                top_boundary_row["target_carrier_mask_class_id"]
            ),
            "boundary_partition_code": int(top_boundary_row["boundary_partition_code"]),
            "signature_cut_edge_count": int(top_boundary_row["signature_cut_edge_count"]),
            "undirected_stationary_flux_x1e12": int(
                top_boundary_row["undirected_stationary_flux_x1e12"]
            ),
            "flux_fraction_of_total_cut_x1e12": observable_values[
                "top_boundary_pair_flux_fraction"
            ],
        },
        "boundary_mask_edges": [
            {key: int(value) for key, value in row.items()} for row in mask_edge_rows
        ],
    }

    expected_pair_rows = [
        (EDGE_HIGH_NEGATIVE, 0, 7, 100, 1787572600),
        (EDGE_HIGH_NEGATIVE, 1, 8, 98, 1924482056),
        (EDGE_CENTRAL_NEGATIVE, 3, 7, 290, 23966124030),
        (EDGE_CENTRAL_NEGATIVE, 3, 8, 203, 16978273445),
        (EDGE_CENTRAL_NEGATIVE, 4, 12, 216, 2823477696),
        (EDGE_CENTRAL_NEGATIVE, 6, 12, 108, 8492755176),
        (EDGE_CENTRAL_NEGATIVE, 7, 11, 200, 22135706800),
        (EDGE_CENTRAL_NEGATIVE, 7, 12, 180, 16474783260),
        (EDGE_CENTRAL_NEGATIVE, 8, 11, 140, 15681554700),
        (EDGE_CENTRAL_NEGATIVE, 8, 12, 126, 11671197804),
        (EDGE_CENTRAL_NEGATIVE, 9, 10, 240, 3891062880),
        (EDGE_CENTRAL_NEGATIVE, 9, 11, 600, 14668386000),
        (EDGE_CENTRAL_NEGATIVE, 9, 12, 540, 10917134100),
        (EDGE_CENTRAL_NEGATIVE, 10, 13, 168, 11557048944),
        (EDGE_CENTRAL_NEGATIVE, 11, 13, 420, 43567340880),
        (EDGE_CENTRAL_NEGATIVE, 12, 13, 378, 32425551018),
    ]
    observed_pair_rows = [
        (
            int(row["boundary_partition_code"]),
            int(row["source_carrier_mask_class_id"]),
            int(row["target_carrier_mask_class_id"]),
            int(row["signature_cut_edge_count"]),
            int(row["undirected_stationary_flux_x1e12"]),
        )
        for row in mask_edge_rows
    ]

    checks = {
        "cell_complex_report_certified": cell_report.get("status")
        == "C985_D20_SIGNATURE_RESIDUAL_CELL_COMPLEX_CERTIFIED",
        "cell_complex_certificate_certified": cell_certificate.get("status")
        == "C985_D20_SIGNATURE_RESIDUAL_CELL_COMPLEX_CERTIFIED",
        "spectral_cut_report_certified": spectral_report.get("status")
        == "C985_D20_SIGNATURE_TRANSFER_SPECTRAL_CUT_CERTIFIED",
        "spectral_cut_certificate_certified": spectral_certificate.get("status")
        == "C985_D20_SIGNATURE_TRANSFER_SPECTRAL_CUT_CERTIFIED",
        "signature_cut_edge_count_is_4007": len(signature_edge_rows) == 4007,
        "carrier_boundary_edge_count_is_16": len(mask_edge_rows) == 16,
        "total_cut_flux_matches_spectral_cut": total_cut_flux
        == int(spectral_report["witness"]["undirected_cut_flux_x1e12"])
        == 238962451389,
        "all_signature_cut_edges_have_shared_active_atom_one": all(
            int(row["shared_active_atom_count"]) == 1 for row in signature_edge_rows
        ),
        "shared_active_atom_sum_matches_cut_edge_count": observable_values[
            "shared_active_atom_sum"
        ]
        == 4007,
        "boundary_pair_set_matches_cell_complex": boundary_pair_set
        == boundary_cell_pairs,
        "boundary_degrees_match_spectral_mask_summary": degree_l1_delta == 0,
        "unexpected_boundary_partition_count_is_zero": unexpected_partition_count == 0,
        "high_negative_partition_matches_expected": (
            int(high_partition["mask_edge_count"]),
            int(high_partition["signature_cut_edge_count"]),
            int(high_partition["undirected_stationary_flux_x1e12"]),
            int(high_partition["flux_fraction_of_total_cut_x1e12"]),
        )
        == (2, 198, 3712054656, 15534049950),
        "central_negative_partition_matches_expected": (
            int(central_partition["mask_edge_count"]),
            int(central_partition["signature_cut_edge_count"]),
            int(central_partition["undirected_stationary_flux_x1e12"]),
            int(central_partition["flux_fraction_of_total_cut_x1e12"]),
        )
        == (14, 3809, 235250396733, 984465950050),
        "central_negative_carries_flux_majority": int(
            central_partition["undirected_stationary_flux_x1e12"]
        )
        > int(high_partition["undirected_stationary_flux_x1e12"]),
        "top_boundary_pair_matches_expected": (
            int(top_boundary_row["source_carrier_mask_class_id"]),
            int(top_boundary_row["target_carrier_mask_class_id"]),
            int(top_boundary_row["signature_cut_edge_count"]),
            int(top_boundary_row["undirected_stationary_flux_x1e12"]),
            observable_values["top_boundary_pair_flux_fraction"],
        )
        == (11, 13, 420, 43567340880, 182318772789),
        "boundary_pair_flux_rows_match_expected": observed_pair_rows
        == expected_pair_rows,
        "signature_edge_table_shape_is_4007_by_13": tuple(signature_edge_table.shape)
        == (4007, len(BOUNDARY_SIGNATURE_EDGE_COLUMNS)),
        "mask_edge_table_shape_is_16_by_12": tuple(mask_edge_table.shape)
        == (16, len(BOUNDARY_MASK_EDGE_COLUMNS)),
        "partition_table_shape_is_2_by_9": tuple(partition_table.shape)
        == (2, len(BOUNDARY_PARTITION_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(BOUNDARY_FLUX_OBSERVABLE_COLUMNS)),
        "cell_complex_tables_available": "carrier_region_edge_table"
        in cell_tables.files,
        "spectral_cut_tables_available": "eigenmode_cut_edge_table"
        in spectral_tables.files,
        "cell_complex_json_schema_available": cell_complex.get("schema")
        == "c985.d20_signature_residual_cell_complex@1",
        "spectral_cut_json_schema_available": spectral_cut.get("schema")
        == "c985.d20_signature_transfer_spectral_cut@1",
    }

    witness = {
        "signature_cut_edge_count": len(signature_edge_rows),
        "carrier_boundary_edge_count": len(mask_edge_rows),
        "total_undirected_cut_flux_x1e12": total_cut_flux,
        "high_negative": {
            "mask_edge_count": int(high_partition["mask_edge_count"]),
            "signature_cut_edge_count": int(high_partition["signature_cut_edge_count"]),
            "undirected_cut_flux_x1e12": int(
                high_partition["undirected_stationary_flux_x1e12"]
            ),
            "flux_fraction_x1e12": int(
                high_partition["flux_fraction_of_total_cut_x1e12"]
            ),
        },
        "central_negative": {
            "mask_edge_count": int(central_partition["mask_edge_count"]),
            "signature_cut_edge_count": int(
                central_partition["signature_cut_edge_count"]
            ),
            "undirected_cut_flux_x1e12": int(
                central_partition["undirected_stationary_flux_x1e12"]
            ),
            "flux_fraction_x1e12": int(
                central_partition["flux_fraction_of_total_cut_x1e12"]
            ),
        },
        "top_boundary_pair": boundary_flux["top_boundary_pair"],
        "shared_active_atom_sum": observable_values["shared_active_atom_sum"],
        "boundary_degree_l1_delta": degree_l1_delta,
        "boundary_signature_edge_table_sha256": sha_array(signature_edge_table),
        "boundary_mask_edge_table_sha256": sha_array(mask_edge_table),
        "boundary_partition_table_sha256": sha_array(partition_table),
        "boundary_flux_observable_table_sha256": sha_array(observable_table),
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_flux_cells_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_FLUX_CELLS_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "all 4,007 spectral crossing signature edges lie over the 16 residual cell-complex boundary mask edges",
            "high-negative boundary contacts carry 198 crossing edges and 0.015534049950 of cut flux",
            "central-negative boundary contacts carry 3,809 crossing edges and 0.984465950050 of cut flux",
            "the strongest boundary pair is central-negative mask edge 11-13 with flux 0.043567340880",
            "every crossing signature edge has exactly one shared active carrier atom",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_flux_cells@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The residual cell-complex boundary lifts exactly to the 4,007 "
            "spectral crossing signature edges, and almost all cut conductance "
            "is carried by central-negative rather than high-negative boundary cells."
        ),
        "stage_protocol": {
            "draft": "map spectral crossing signature edges to residual carrier boundary cells",
            "witness": "aggregate signature-edge counts, shared-carrier counts, and undirected stationary flux by boundary cell",
            "coherence": "check totals against the spectral cut and boundary pairs against the residual cell complex",
            "closure": "certify finite boundary-cell flux without claiming a continuum conductance law",
            "emit": "emit boundary-flux JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "cell_complex_report": input_entry(
                CELL_COMPLEX_REPORT,
                {
                    "status": cell_report.get("status"),
                    "certificate_sha256": cell_report.get("certificate_sha256"),
                },
            ),
            "cell_complex": input_entry(CELL_COMPLEX_JSON),
            "cell_complex_tables": input_entry(CELL_COMPLEX_TABLES),
            "cell_complex_certificate": input_entry(CELL_COMPLEX_CERTIFICATE),
            "cell_complex_vertices": input_entry(CELL_COMPLEX_VERTICES),
            "cell_complex_edges": input_entry(CELL_COMPLEX_EDGES),
            "spectral_cut_report": input_entry(
                SPECTRAL_CUT_REPORT,
                {
                    "status": spectral_report.get("status"),
                    "certificate_sha256": spectral_report.get("certificate_sha256"),
                },
            ),
            "spectral_cut": input_entry(SPECTRAL_CUT_JSON),
            "spectral_cut_tables": input_entry(SPECTRAL_CUT_TABLES),
            "spectral_cut_certificate": input_entry(SPECTRAL_CUT_CERTIFICATE),
            "spectral_cut_edges": input_entry(SPECTRAL_CUT_EDGES),
            "spectral_mask_summary": input_entry(SPECTRAL_MASK_SUMMARY),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_flux_cells": relpath(
                OUT_DIR / "signature_boundary_flux_cells.json"
            ),
            "boundary_signature_edges_csv": relpath(
                OUT_DIR / "boundary_signature_edges.csv"
            ),
            "boundary_mask_edges_csv": relpath(OUT_DIR / "boundary_mask_edges.csv"),
            "boundary_partition_summary_csv": relpath(
                OUT_DIR / "boundary_partition_summary.csv"
            ),
            "boundary_flux_observables_csv": relpath(
                OUT_DIR / "boundary_flux_observables.csv"
            ),
            "signature_boundary_flux_cells_tables": relpath(
                OUT_DIR / "signature_boundary_flux_cells_tables.npz"
            ),
            "signature_boundary_flux_cells_certificate": relpath(
                OUT_DIR / "signature_boundary_flux_cells_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "assignment of every spectral crossing signature edge to a residual boundary cell",
                "flux and count aggregation by high-negative and central-negative boundary partitions",
                "exact equality between flux boundary pairs and residual cell-complex positive-negative boundary pairs",
                "the dominant central-negative carrier of spectral cut conductance",
            ],
            "does_not_certify_because_not_required": [
                "mixing-time bounds or continuum conductance estimates",
                "a physical law selecting the declared transfer conductance",
                "higher-eigenmode boundary flux",
                "new associator, pentagon, pivotal, spherical, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Push the boundary flux through the two-state quotient dynamics: "
            "certify how the central-negative conductance accounts for the "
            "positive-to-negative and negative-to-positive transition rates, then "
            "compare it with the quotient entropy rate."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_flux_cells_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified residual cell-complex and spectral-cut artifacts",
            "map all spectral crossing signature edges to residual boundary-cell carrier pairs",
            "aggregate signature cut-edge counts and undirected stationary flux by high-negative and central-negative contact",
            "verify flux totals, boundary pairs, and boundary degrees against upstream certificates",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_flux_cells": boundary_flux,
        "boundary_signature_edges_csv": csv_text(
            BOUNDARY_SIGNATURE_EDGE_COLUMNS,
            signature_edge_rows,
        ),
        "boundary_mask_edges_csv": csv_text(BOUNDARY_MASK_EDGE_COLUMNS, mask_edge_rows),
        "boundary_partition_summary_csv": csv_text(
            BOUNDARY_PARTITION_COLUMNS,
            partition_rows,
        ),
        "boundary_flux_observables_csv": csv_text(
            BOUNDARY_FLUX_OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "boundary_signature_edge_table": signature_edge_table,
        "boundary_mask_edge_table": mask_edge_table,
        "boundary_partition_table": partition_table,
        "boundary_flux_observable_table": observable_table,
        "signature_boundary_flux_cells_certificate": certificate,
        "report": report,
        "manifest": manifest,
    }


def update_index(report: dict[str, Any]) -> None:
    if INDEX_PATH.exists():
        index_payload = load_json(INDEX_PATH)
        obligations = [
            row
            for row in index_payload.get("obligations", [])
            if isinstance(row, dict) and row.get("id") != THEOREM_ID
        ]
        schema = index_payload.get("schema", "d20.proof_obligation_registry.source_drop")
    else:
        obligations = []
        schema = "d20.proof_obligation_registry.source_drop"
    obligations.append(
        {
            "id": THEOREM_ID,
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
            "report_sha256": report["certificate_sha256"],
            "status": report["status"],
        }
    )
    updated = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": sorted(obligations, key=lambda row: row["id"]),
    }
    updated["registry_sha256"] = self_hash(updated, "registry_sha256")
    write_json(INDEX_PATH, updated)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(
        OUT_DIR / "signature_boundary_flux_cells.json",
        payloads["signature_boundary_flux_cells"],
    )
    (OUT_DIR / "boundary_signature_edges.csv").write_text(
        payloads["boundary_signature_edges_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "boundary_mask_edges.csv").write_text(
        payloads["boundary_mask_edges_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "boundary_partition_summary.csv").write_text(
        payloads["boundary_partition_summary_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "boundary_flux_observables.csv").write_text(
        payloads["boundary_flux_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_boundary_flux_cells_tables.npz",
        boundary_signature_edge_table=payloads["boundary_signature_edge_table"],
        boundary_mask_edge_table=payloads["boundary_mask_edge_table"],
        boundary_partition_table=payloads["boundary_partition_table"],
        boundary_flux_observable_table=payloads["boundary_flux_observable_table"],
    )
    write_json(
        OUT_DIR / "signature_boundary_flux_cells_certificate.json",
        payloads["signature_boundary_flux_cells_certificate"],
    )
    write_json(OUT_DIR / "report.json", payloads["report"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    update_index(payloads["report"])


def main() -> None:
    payloads = build_payloads()
    write_payloads(payloads)
    witness = payloads["report"]["witness"]
    print(
        json.dumps(
            {
                "status": payloads["report"]["status"],
                "all_checks_pass": payloads["report"]["all_checks_pass"],
                "report": relpath(OUT_DIR / "report.json"),
                "manifest": relpath(OUT_DIR / "manifest.json"),
                "certificate_sha256": payloads["report"]["certificate_sha256"],
                "signature_cut_edge_count": witness["signature_cut_edge_count"],
                "total_undirected_cut_flux_x1e12": witness[
                    "total_undirected_cut_flux_x1e12"
                ],
                "high_negative": witness["high_negative"],
                "central_negative": witness["central_negative"],
                "next_highest_yield_item": payloads["report"][
                    "next_highest_yield_item"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
