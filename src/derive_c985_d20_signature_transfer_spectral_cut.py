from __future__ import annotations

import csv
import json
import math
from fractions import Fraction
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_recurrent_signature_subboundary import (
        OUT_DIR as SIGNATURE_SUBBOUNDARY_DIR,
        atom_ids_from_mask,
        padded_atom_ids,
    )
    from .derive_c985_d20_signature_subboundary_transfer_operator import (
        OUT_DIR as SIGNATURE_TRANSFER_DIR,
    )
    from .derive_c985_d20_stationary_atom_flow_lift import (
        OUT_DIR as ATOM_FLOW_DIR,
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
    from derive_c985_d20_recurrent_signature_subboundary import (
        OUT_DIR as SIGNATURE_SUBBOUNDARY_DIR,
        atom_ids_from_mask,
        padded_atom_ids,
    )
    from derive_c985_d20_signature_subboundary_transfer_operator import (
        OUT_DIR as SIGNATURE_TRANSFER_DIR,
    )
    from derive_c985_d20_stationary_atom_flow_lift import (
        OUT_DIR as ATOM_FLOW_DIR,
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


THEOREM_ID = "c985_d20_signature_transfer_spectral_cut"
STATUS = "C985_D20_SIGNATURE_TRANSFER_SPECTRAL_CUT_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

SIGNATURE_TRANSFER_REPORT = SIGNATURE_TRANSFER_DIR / "report.json"
SIGNATURE_TRANSFER_JSON = SIGNATURE_TRANSFER_DIR / "signature_transfer_operator.json"
SIGNATURE_TRANSFER_TABLES = SIGNATURE_TRANSFER_DIR / "signature_transfer_tables.npz"
SIGNATURE_TRANSFER_CERTIFICATE = SIGNATURE_TRANSFER_DIR / "signature_transfer_certificate.json"

SIGNATURE_SUBBOUNDARY_REPORT = SIGNATURE_SUBBOUNDARY_DIR / "report.json"
SIGNATURE_SUBBOUNDARY_JSON = SIGNATURE_SUBBOUNDARY_DIR / "recurrent_signature_subboundary.json"
SIGNATURE_SUBBOUNDARY_TABLES = (
    SIGNATURE_SUBBOUNDARY_DIR / "recurrent_signature_subboundary_tables.npz"
)
SIGNATURE_SUBBOUNDARY_CERTIFICATE = (
    SIGNATURE_SUBBOUNDARY_DIR / "recurrent_signature_subboundary_certificate.json"
)

ATOM_FLOW_REPORT = ATOM_FLOW_DIR / "report.json"
ATOM_FLOW_JSON = ATOM_FLOW_DIR / "stationary_atom_flow_lift.json"
ATOM_FLOW_TABLES = ATOM_FLOW_DIR / "stationary_atom_flow_tables.npz"
ATOM_FLOW_CERTIFICATE = ATOM_FLOW_DIR / "stationary_atom_flow_certificate.json"
ATOM_FLOW_NODE_CONTRIBUTIONS = ATOM_FLOW_DIR / "node_atom_contributions.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_c985_d20_signature_transfer_spectral_cut.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_d20_signature_transfer_spectral_cut.py"

PROBABILITY_SCALE = 1_000_000_000_000

EIGENMODE_VERTEX_COLUMNS = [
    "signature_vertex_id",
    "signature_class_id",
    "nodal_sign",
    "second_eigenfunction_x1e12",
    "stationary_mass_x1e12",
    "carrier_atom_mask",
    "carrier_mask_class_id",
    "degree",
    "signature_flow_rank",
    "stationary_rank",
]

EIGENMODE_CUT_EDGE_COLUMNS = [
    "cut_edge_id",
    "transfer_edge_id",
    "source_signature_class_id",
    "target_signature_class_id",
    "shared_active_atom_count",
    "source_nodal_sign",
    "target_nodal_sign",
    "source_eigenfunction_x1e12",
    "target_eigenfunction_x1e12",
    "undirected_stationary_flux_x1e12",
    "source_carrier_atom_mask",
    "target_carrier_atom_mask",
]

MASK_EIGENMODE_COLUMNS = [
    "carrier_mask_class_id",
    "carrier_atom_mask",
    "nodal_sign",
    "signature_class_count",
    "positive_signature_count",
    "negative_signature_count",
    "stationary_mass_x1e12",
    "positive_stationary_mass_x1e12",
    "negative_stationary_mass_x1e12",
    "mode_mean_x1e12",
    "mask_graph_degree",
    "cut_boundary_mask_edge_count",
    "carrier_atom_id_0",
    "carrier_atom_id_1",
    "carrier_atom_id_2",
    "carrier_atom_id_3",
]

ATOM_EIGENMODE_COLUMNS = [
    "atom_id",
    "stationary_participation_mass_x1e12",
    "positive_side_mass_x1e12",
    "negative_side_mass_x1e12",
    "positive_fraction_x1e12",
    "mode_mean_x1e12",
    "carrier_signature_count",
]

BASIN_EIGENMODE_COLUMNS = [
    "basin_code",
    "total_participation_mass_x1e12",
    "positive_side_mass_x1e12",
    "negative_side_mass_x1e12",
    "positive_fraction_x1e12",
    "positive_side_composition_x1e12",
    "negative_side_composition_x1e12",
]

EIGENMODE_OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "lambda_2": 0,
    "lambda_3": 1,
    "lambda_2_minus_lambda_3": 2,
    "spectral_gap": 3,
    "lambda_min": 4,
    "positive_vertex_count": 5,
    "negative_vertex_count": 6,
    "positive_stationary_mass": 7,
    "negative_stationary_mass": 8,
    "cut_edge_count": 9,
    "within_positive_edge_count": 10,
    "within_negative_edge_count": 11,
    "undirected_cut_flux": 12,
    "one_way_cut_flux": 13,
    "cut_conductance": 14,
    "positive_mask_class_count": 15,
    "negative_mask_class_count": 16,
    "mask_cut_edge_count": 17,
    "top_positive_atom": 18,
    "top_negative_atom": 19,
    "basin_10_positive_fraction": 20,
    "basin_43_positive_fraction": 21,
    "basin_boundary_positive_fraction": 22,
}


def scaled_float(value: float) -> int:
    return int(round(float(value) * PROBABILITY_SCALE))


def scaled_fraction(value: Fraction, *, scale: int = PROBABILITY_SCALE) -> int:
    numerator = value.numerator * scale
    quotient, remainder = divmod(numerator, value.denominator)
    if 2 * remainder >= value.denominator:
        quotient += 1
    return int(quotient)


def scale_fraction_masses(values: list[Fraction]) -> list[int]:
    total = sum(values, Fraction(0))
    target = int(total) if total.denominator == 1 else int(round(float(total)))
    floors = [value.numerator // value.denominator for value in values]
    remainder = target - sum(floors)
    residues = [
        Fraction(value.numerator % value.denominator, value.denominator)
        for value in values
    ]
    order = sorted(range(len(values)), key=lambda index: (-residues[index], index))
    scaled = floors[:]
    for index in order[:remainder]:
        scaled[index] += 1
    return [int(value) for value in scaled]


def table_from_rows(columns: list[str], rows: list[dict[str, int]]) -> np.ndarray:
    return np.asarray([[int(row[column]) for column in columns] for row in rows], dtype=np.int64)


def ranks_descending(values: dict[int, int]) -> dict[int, int]:
    return {
        key: rank
        for rank, key in enumerate(
            sorted(values, key=lambda item: (-int(values[item]), int(item))),
            start=1,
        )
    }


def atom_basin_masses() -> dict[int, dict[int, int]]:
    masses = {atom_id: {10: 0, 43: 0, 0: 0} for atom_id in range(20)}
    with ATOM_FLOW_NODE_CONTRIBUTIONS.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            atom_id = int(row["atom_id"])
            basin_code = int(row["node_basin_code"])
            masses[atom_id][basin_code] += int(row["atom_slot_mass_x1e12"])
    return masses


def eigenmode_from_conductance(
    stationary_table: np.ndarray,
    transfer_edge_table: np.ndarray,
) -> dict[str, Any]:
    vertex_count = int(stationary_table.shape[0])
    class_to_index = {
        int(row[1]): index for index, row in enumerate(stationary_table)
    }
    masses = np.asarray(stationary_table[:, 3], dtype=np.float64) / PROBABILITY_SCALE
    conductance = np.zeros((vertex_count, vertex_count), dtype=np.float64)
    for row in transfer_edge_table:
        source = class_to_index[int(row[1])]
        target = class_to_index[int(row[2])]
        value = int(row[3]) * masses[source] * masses[target]
        conductance[source, target] = value
        conductance[target, source] = value
    degree = conductance.sum(axis=1)
    stationary = degree / degree.sum()
    similarity = conductance / np.sqrt(degree[:, None] * degree[None, :])
    eigenvalues, eigenvectors = np.linalg.eigh(similarity)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]

    eigenfunction = eigenvectors[:, 1] / np.sqrt(stationary)
    mean = float(np.dot(stationary, eigenfunction))
    eigenfunction = eigenfunction - mean
    eigenfunction = eigenfunction / math.sqrt(float(np.dot(stationary, eigenfunction * eigenfunction)))

    stored_stationary = np.asarray(stationary_table[:, 2], dtype=np.int64)
    positive_mass = int(stored_stationary[eigenfunction > 0].sum())
    negative_mass = int(stored_stationary[eigenfunction < 0].sum())
    if positive_mass < negative_mass:
        eigenfunction = -eigenfunction
        positive_mass, negative_mass = negative_mass, positive_mass

    signs = np.where(eigenfunction > 0, 1, -1).astype(np.int64)
    transition = np.zeros_like(conductance)
    transition[degree > 0] = conductance[degree > 0] / degree[degree > 0, None]
    residual = float(np.max(np.abs(transition @ eigenfunction - eigenvalues[1] * eigenfunction)))
    orthogonality = float(abs(np.dot(stationary, eigenfunction)))
    norm_residual = float(abs(np.dot(stationary, eigenfunction * eigenfunction) - 1.0))

    return {
        "eigenvalues": eigenvalues,
        "eigenfunction": eigenfunction,
        "eigenfunction_x1e12": np.asarray(
            [scaled_float(value) for value in eigenfunction],
            dtype=np.int64,
        ),
        "nodal_signs": signs,
        "positive_mass_x1e12": positive_mass,
        "negative_mass_x1e12": negative_mass,
        "eigen_residual_max_x1e12": scaled_float(residual),
        "stationary_orthogonality_abs_x1e12": scaled_float(orthogonality),
        "stationary_norm_residual_abs_x1e12": scaled_float(norm_residual),
        "transition": transition,
    }


def build_payloads() -> dict[str, Any]:
    transfer_report = load_json(SIGNATURE_TRANSFER_REPORT)
    transfer = load_json(SIGNATURE_TRANSFER_JSON)
    transfer_certificate = load_json(SIGNATURE_TRANSFER_CERTIFICATE)
    subboundary_report = load_json(SIGNATURE_SUBBOUNDARY_REPORT)
    subboundary = load_json(SIGNATURE_SUBBOUNDARY_JSON)
    subboundary_certificate = load_json(SIGNATURE_SUBBOUNDARY_CERTIFICATE)
    atom_flow_report = load_json(ATOM_FLOW_REPORT)
    atom_flow = load_json(ATOM_FLOW_JSON)
    atom_flow_certificate = load_json(ATOM_FLOW_CERTIFICATE)
    transfer_tables = np.load(SIGNATURE_TRANSFER_TABLES, allow_pickle=False)
    subboundary_tables = np.load(SIGNATURE_SUBBOUNDARY_TABLES, allow_pickle=False)
    atom_flow_tables = np.load(ATOM_FLOW_TABLES, allow_pickle=False)

    stationary_table_source = np.asarray(
        transfer_tables["signature_stationary_table"],
        dtype=np.int64,
    )
    transfer_edge_table_source = np.asarray(
        transfer_tables["signature_transfer_edge_table"],
        dtype=np.int64,
    )
    source_mask_table = np.asarray(
        transfer_tables["signature_mask_stationary_table"],
        dtype=np.int64,
    )
    source_stationary_vector = np.asarray(
        transfer_tables["signature_stationary_distribution_x1e12"],
        dtype=np.int64,
    )
    mask_adjacency = np.asarray(subboundary_tables["mask_class_adjacency"], dtype=np.int8)

    eigenmode = eigenmode_from_conductance(
        stationary_table_source,
        transfer_edge_table_source,
    )
    eigenvalues = np.asarray(eigenmode["eigenvalues"], dtype=np.float64)
    eigenfunction = np.asarray(eigenmode["eigenfunction"], dtype=np.float64)
    eigenfunction_x1e12 = np.asarray(eigenmode["eigenfunction_x1e12"], dtype=np.int64)
    signs = np.asarray(eigenmode["nodal_signs"], dtype=np.int64)

    vertex_rows: list[dict[str, int]] = []
    for index, row in enumerate(stationary_table_source):
        vertex_rows.append(
            {
                "signature_vertex_id": int(row[0]),
                "signature_class_id": int(row[1]),
                "nodal_sign": int(signs[index]),
                "second_eigenfunction_x1e12": int(eigenfunction_x1e12[index]),
                "stationary_mass_x1e12": int(row[2]),
                "carrier_atom_mask": int(row[5]),
                "carrier_mask_class_id": int(row[8]),
                "degree": int(row[7]),
                "signature_flow_rank": int(row[10]),
                "stationary_rank": int(row[9]),
            }
        )

    class_to_index = {int(row[1]): index for index, row in enumerate(stationary_table_source)}
    cut_rows: list[dict[str, int]] = []
    within_positive_edge_count = 0
    within_negative_edge_count = 0
    within_positive_flux = 0
    within_negative_flux = 0
    cut_flux = 0
    for row in transfer_edge_table_source:
        source = class_to_index[int(row[1])]
        target = class_to_index[int(row[2])]
        source_sign = int(signs[source])
        target_sign = int(signs[target])
        flux = int(row[10])
        if source_sign == target_sign == 1:
            within_positive_edge_count += 1
            within_positive_flux += flux
            continue
        if source_sign == target_sign == -1:
            within_negative_edge_count += 1
            within_negative_flux += flux
            continue
        cut_flux += flux
        cut_rows.append(
            {
                "cut_edge_id": len(cut_rows),
                "transfer_edge_id": int(row[0]),
                "source_signature_class_id": int(row[1]),
                "target_signature_class_id": int(row[2]),
                "shared_active_atom_count": int(row[3]),
                "source_nodal_sign": source_sign,
                "target_nodal_sign": target_sign,
                "source_eigenfunction_x1e12": int(eigenfunction_x1e12[source]),
                "target_eigenfunction_x1e12": int(eigenfunction_x1e12[target]),
                "undirected_stationary_flux_x1e12": flux,
                "source_carrier_atom_mask": int(row[4]),
                "target_carrier_atom_mask": int(row[5]),
            }
        )

    mask_rows: list[dict[str, int]] = []
    mask_signs: dict[int, int] = {}
    for mask_row in source_mask_table:
        mask_class = int(mask_row[0])
        indices = [
            index
            for index, row in enumerate(stationary_table_source)
            if int(row[8]) == mask_class
        ]
        positive_indices = [index for index in indices if int(signs[index]) == 1]
        negative_indices = [index for index in indices if int(signs[index]) == -1]
        mask_sign = 1 if positive_indices and not negative_indices else -1 if negative_indices and not positive_indices else 0
        mask_signs[mask_class] = mask_sign
        stationary_mass = int(sum(int(source_stationary_vector[index]) for index in indices))
        positive_mass = int(sum(int(source_stationary_vector[index]) for index in positive_indices))
        negative_mass = int(sum(int(source_stationary_vector[index]) for index in negative_indices))
        weighted_mode = (
            sum(float(source_stationary_vector[index]) * float(eigenfunction[index]) for index in indices)
            / stationary_mass
            if stationary_mass
            else 0.0
        )
        cut_boundary = 0
        for other in range(mask_adjacency.shape[0]):
            if int(mask_adjacency[mask_class, other]) and mask_signs.get(other, mask_sign) != mask_sign:
                cut_boundary += 1
        carrier_ids = atom_ids_from_mask(int(mask_row[1]))
        padded = padded_atom_ids(carrier_ids)
        mask_rows.append(
            {
                "carrier_mask_class_id": mask_class,
                "carrier_atom_mask": int(mask_row[1]),
                "nodal_sign": mask_sign,
                "signature_class_count": len(indices),
                "positive_signature_count": len(positive_indices),
                "negative_signature_count": len(negative_indices),
                "stationary_mass_x1e12": stationary_mass,
                "positive_stationary_mass_x1e12": positive_mass,
                "negative_stationary_mass_x1e12": negative_mass,
                "mode_mean_x1e12": scaled_float(weighted_mode),
                "mask_graph_degree": int(mask_row[8]),
                "cut_boundary_mask_edge_count": cut_boundary,
                "carrier_atom_id_0": padded[0],
                "carrier_atom_id_1": padded[1],
                "carrier_atom_id_2": padded[2],
                "carrier_atom_id_3": padded[3],
            }
        )

    for row in mask_rows:
        cut_boundary = 0
        mask_class = int(row["carrier_mask_class_id"])
        for other in range(mask_adjacency.shape[0]):
            if int(mask_adjacency[mask_class, other]) and mask_signs[other] != mask_signs[mask_class]:
                cut_boundary += 1
        row["cut_boundary_mask_edge_count"] = cut_boundary

    mask_cut_edge_count = sum(
        1
        for left in range(mask_adjacency.shape[0])
        for right in range(left + 1, mask_adjacency.shape[1])
        if int(mask_adjacency[left, right]) and mask_signs[left] != mask_signs[right]
    )
    mask_within_positive_edge_count = sum(
        1
        for left in range(mask_adjacency.shape[0])
        for right in range(left + 1, mask_adjacency.shape[1])
        if int(mask_adjacency[left, right]) and mask_signs[left] == mask_signs[right] == 1
    )
    mask_within_negative_edge_count = sum(
        1
        for left in range(mask_adjacency.shape[0])
        for right in range(left + 1, mask_adjacency.shape[1])
        if int(mask_adjacency[left, right]) and mask_signs[left] == mask_signs[right] == -1
    )

    atom_total = [Fraction(0) for _ in range(20)]
    atom_positive = [Fraction(0) for _ in range(20)]
    atom_negative = [Fraction(0) for _ in range(20)]
    atom_mode_numerator = [0.0 for _ in range(20)]
    atom_counts = [0 for _ in range(20)]
    for index, row in enumerate(stationary_table_source):
        carrier_ids = atom_ids_from_mask(int(row[5]))
        for atom_id in carrier_ids:
            share = Fraction(int(source_stationary_vector[index]), len(carrier_ids))
            atom_total[atom_id] += share
            atom_mode_numerator[atom_id] += float(share) * float(eigenfunction[index])
            atom_counts[atom_id] += 1
            if int(signs[index]) == 1:
                atom_positive[atom_id] += share
            else:
                atom_negative[atom_id] += share

    active_atom_ids = [atom_id for atom_id in range(20) if atom_total[atom_id] != 0]
    atom_total_scaled = {
        atom_id: value
        for atom_id, value in zip(
            active_atom_ids,
            scale_fraction_masses([atom_total[atom_id] for atom_id in active_atom_ids]),
        )
    }
    atom_positive_scaled = {
        atom_id: value
        for atom_id, value in zip(
            active_atom_ids,
            scale_fraction_masses([atom_positive[atom_id] for atom_id in active_atom_ids]),
        )
    }
    atom_negative_scaled = {
        atom_id: value
        for atom_id, value in zip(
            active_atom_ids,
            scale_fraction_masses([atom_negative[atom_id] for atom_id in active_atom_ids]),
        )
    }

    atom_rows: list[dict[str, int]] = []
    for atom_id in active_atom_ids:
        total_mass = atom_total_scaled[atom_id]
        positive_mass = atom_positive_scaled[atom_id]
        negative_mass = atom_negative_scaled[atom_id]
        positive_fraction = (
            scaled_fraction(atom_positive[atom_id] / atom_total[atom_id])
            if atom_total[atom_id]
            else 0
        )
        mode_mean = atom_mode_numerator[atom_id] / float(atom_total[atom_id])
        atom_rows.append(
            {
                "atom_id": atom_id,
                "stationary_participation_mass_x1e12": total_mass,
                "positive_side_mass_x1e12": positive_mass,
                "negative_side_mass_x1e12": negative_mass,
                "positive_fraction_x1e12": positive_fraction,
                "mode_mean_x1e12": scaled_float(mode_mean),
                "carrier_signature_count": atom_counts[atom_id],
            }
        )

    basin_atom_masses = atom_basin_masses()
    basin_total = {10: Fraction(0), 43: Fraction(0), 0: Fraction(0)}
    basin_positive = {10: Fraction(0), 43: Fraction(0), 0: Fraction(0)}
    basin_negative = {10: Fraction(0), 43: Fraction(0), 0: Fraction(0)}
    for index, row in enumerate(stationary_table_source):
        carrier_ids = atom_ids_from_mask(int(row[5]))
        for atom_id in carrier_ids:
            atom_total_mass = sum(basin_atom_masses[atom_id].values())
            for basin_code, basin_atom_mass in basin_atom_masses[atom_id].items():
                share = Fraction(
                    int(source_stationary_vector[index]),
                    len(carrier_ids),
                ) * Fraction(basin_atom_mass, atom_total_mass)
                basin_total[basin_code] += share
                if int(signs[index]) == 1:
                    basin_positive[basin_code] += share
                else:
                    basin_negative[basin_code] += share

    basin_total_scaled = {
        basin_code: value
        for basin_code, value in zip(
            [10, 43, 0],
            scale_fraction_masses([basin_total[10], basin_total[43], basin_total[0]]),
        )
    }
    basin_positive_scaled = {
        basin_code: value
        for basin_code, value in zip(
            [10, 43, 0],
            scale_fraction_masses([basin_positive[10], basin_positive[43], basin_positive[0]]),
        )
    }
    basin_negative_scaled = {
        basin_code: value
        for basin_code, value in zip(
            [10, 43, 0],
            scale_fraction_masses([basin_negative[10], basin_negative[43], basin_negative[0]]),
        )
    }
    positive_total = sum(basin_positive.values(), Fraction(0))
    negative_total = sum(basin_negative.values(), Fraction(0))
    basin_rows: list[dict[str, int]] = []
    for basin_code in [10, 43, 0]:
        basin_rows.append(
            {
                "basin_code": basin_code,
                "total_participation_mass_x1e12": int(basin_total_scaled[basin_code]),
                "positive_side_mass_x1e12": int(basin_positive_scaled[basin_code]),
                "negative_side_mass_x1e12": int(basin_negative_scaled[basin_code]),
                "positive_fraction_x1e12": scaled_fraction(
                    basin_positive[basin_code] / basin_total[basin_code]
                ),
                "positive_side_composition_x1e12": scaled_fraction(
                    basin_positive[basin_code] / positive_total
                ),
                "negative_side_composition_x1e12": scaled_fraction(
                    basin_negative[basin_code] / negative_total
                ),
            }
        )

    positive_count = int(np.count_nonzero(signs == 1))
    negative_count = int(np.count_nonzero(signs == -1))
    positive_mass = int(source_stationary_vector[signs == 1].sum())
    negative_mass = int(source_stationary_vector[signs == -1].sum())
    one_way_cut_flux = cut_flux // 2
    cut_conductance = scaled_float((cut_flux / 2) / min(positive_mass, negative_mass))
    positive_mask_classes = [
        int(mask_class) for mask_class, sign in sorted(mask_signs.items()) if sign == 1
    ]
    negative_mask_classes = [
        int(mask_class) for mask_class, sign in sorted(mask_signs.items()) if sign == -1
    ]
    top_positive_atom = max(atom_rows, key=lambda row: int(row["mode_mean_x1e12"]))
    top_negative_atom = min(atom_rows, key=lambda row: int(row["mode_mean_x1e12"]))

    vertex_table = table_from_rows(EIGENMODE_VERTEX_COLUMNS, vertex_rows)
    cut_edge_table = table_from_rows(EIGENMODE_CUT_EDGE_COLUMNS, cut_rows)
    mask_table = table_from_rows(MASK_EIGENMODE_COLUMNS, mask_rows)
    atom_table = table_from_rows(ATOM_EIGENMODE_COLUMNS, atom_rows)
    basin_table = table_from_rows(BASIN_EIGENMODE_COLUMNS, basin_rows)
    observable_values = {
        "lambda_2": scaled_float(float(eigenvalues[1])),
        "lambda_3": scaled_float(float(eigenvalues[2])),
        "lambda_2_minus_lambda_3": scaled_float(float(eigenvalues[1] - eigenvalues[2])),
        "spectral_gap": scaled_float(float(1.0 - eigenvalues[1])),
        "lambda_min": scaled_float(float(eigenvalues[-1])),
        "positive_vertex_count": positive_count,
        "negative_vertex_count": negative_count,
        "positive_stationary_mass": positive_mass,
        "negative_stationary_mass": negative_mass,
        "cut_edge_count": len(cut_rows),
        "within_positive_edge_count": within_positive_edge_count,
        "within_negative_edge_count": within_negative_edge_count,
        "undirected_cut_flux": cut_flux,
        "one_way_cut_flux": one_way_cut_flux,
        "cut_conductance": cut_conductance,
        "positive_mask_class_count": len(positive_mask_classes),
        "negative_mask_class_count": len(negative_mask_classes),
        "mask_cut_edge_count": mask_cut_edge_count,
        "top_positive_atom": int(top_positive_atom["atom_id"]),
        "top_negative_atom": int(top_negative_atom["atom_id"]),
        "basin_10_positive_fraction": int(basin_rows[0]["positive_fraction_x1e12"]),
        "basin_43_positive_fraction": int(basin_rows[1]["positive_fraction_x1e12"]),
        "basin_boundary_positive_fraction": int(basin_rows[2]["positive_fraction_x1e12"]),
    }
    observable_rows: list[dict[str, int]] = []
    for name, code in sorted(OBSERVABLE_CODES.items(), key=lambda item: item[1]):
        observable_rows.append(
            {
                "observable_id": len(observable_rows),
                "observable_code": int(code),
                "value_x1e12": int(observable_values[name]),
                "aux_id": -1,
            }
        )
    observable_table = table_from_rows(EIGENMODE_OBSERVABLE_COLUMNS, observable_rows)

    spectral_cut = {
        "schema": "c985.d20_signature_transfer_spectral_cut@1",
        "object": "d20",
        "spectral_rule": {
            "operator": "the certified reversible 221-state signature-subboundary transfer operator",
            "eigenmode": "the second right Markov eigenfunction, computed through the symmetric reversible similarity",
            "orientation": "the sign is chosen so the positive side has larger stationary mass",
            "nodal_cut": "vertices are split by the sign of the second eigenfunction",
        },
        "eigen_summary": {
            "lambda_2_x1e12": observable_values["lambda_2"],
            "lambda_3_x1e12": observable_values["lambda_3"],
            "lambda_2_minus_lambda_3_x1e12": observable_values["lambda_2_minus_lambda_3"],
            "spectral_gap_x1e12": observable_values["spectral_gap"],
            "lambda_min_x1e12": observable_values["lambda_min"],
            "eigen_residual_max_x1e12": int(eigenmode["eigen_residual_max_x1e12"]),
            "stationary_orthogonality_abs_x1e12": int(
                eigenmode["stationary_orthogonality_abs_x1e12"]
            ),
            "stationary_norm_residual_abs_x1e12": int(
                eigenmode["stationary_norm_residual_abs_x1e12"]
            ),
        },
        "nodal_cut_summary": {
            "positive_vertex_count": positive_count,
            "negative_vertex_count": negative_count,
            "positive_stationary_mass_x1e12": positive_mass,
            "negative_stationary_mass_x1e12": negative_mass,
            "cut_edge_count": len(cut_rows),
            "within_positive_edge_count": within_positive_edge_count,
            "within_negative_edge_count": within_negative_edge_count,
            "undirected_cut_flux_x1e12": cut_flux,
            "one_way_cut_flux_x1e12": one_way_cut_flux,
            "cut_conductance_x1e12": cut_conductance,
        },
        "carrier_mask_comparison": {
            "positive_mask_class_ids": positive_mask_classes,
            "negative_mask_class_ids": negative_mask_classes,
            "all_mask_classes_are_pure_sign": all(int(row["nodal_sign"]) != 0 for row in mask_rows),
            "mask_cut_edge_count": mask_cut_edge_count,
            "mask_within_positive_edge_count": mask_within_positive_edge_count,
            "mask_within_negative_edge_count": mask_within_negative_edge_count,
        },
        "atom_comparison": {
            "top_positive_atom_id": int(top_positive_atom["atom_id"]),
            "top_negative_atom_id": int(top_negative_atom["atom_id"]),
            "atom_7_positive_fraction_x1e12": next(
                int(row["positive_fraction_x1e12"]) for row in atom_rows if int(row["atom_id"]) == 7
            ),
            "atom_12_positive_fraction_x1e12": next(
                int(row["positive_fraction_x1e12"]) for row in atom_rows if int(row["atom_id"]) == 12
            ),
        },
        "core_basin_comparison": {
            "basin_rows": basin_rows,
            "reading": (
                "the eigenmode is a clean carrier-mask cut, not a pure recovery "
                "of the original core source lobes: every core basin sends a "
                "majority of its induced participation to the positive side"
            ),
        },
        "top_positive_vertices": [
            {
                "signature_class_id": int(row["signature_class_id"]),
                "second_eigenfunction_x1e12": int(row["second_eigenfunction_x1e12"]),
                "stationary_mass_x1e12": int(row["stationary_mass_x1e12"]),
                "carrier_atom_mask": int(row["carrier_atom_mask"]),
            }
            for row in sorted(vertex_rows, key=lambda item: -int(item["second_eigenfunction_x1e12"]))[:16]
        ],
        "top_negative_vertices": [
            {
                "signature_class_id": int(row["signature_class_id"]),
                "second_eigenfunction_x1e12": int(row["second_eigenfunction_x1e12"]),
                "stationary_mass_x1e12": int(row["stationary_mass_x1e12"]),
                "carrier_atom_mask": int(row["carrier_atom_mask"]),
            }
            for row in sorted(vertex_rows, key=lambda item: int(item["second_eigenfunction_x1e12"]))[:16]
        ],
    }

    checks = {
        "signature_transfer_report_certified": transfer_report.get("status")
        == "C985_D20_SIGNATURE_SUBBOUNDARY_TRANSFER_OPERATOR_CERTIFIED",
        "signature_transfer_certificate_certified": transfer_certificate.get("status")
        == "C985_D20_SIGNATURE_SUBBOUNDARY_TRANSFER_OPERATOR_CERTIFIED",
        "signature_subboundary_report_certified": subboundary_report.get("status")
        == "C985_D20_RECURRENT_SIGNATURE_SUBBOUNDARY_CERTIFIED",
        "signature_subboundary_certificate_certified": subboundary_certificate.get("status")
        == "C985_D20_RECURRENT_SIGNATURE_SUBBOUNDARY_CERTIFIED",
        "atom_flow_report_certified": atom_flow_report.get("status")
        == "C985_D20_STATIONARY_ATOM_FLOW_LIFT_CERTIFIED",
        "atom_flow_certificate_certified": atom_flow_certificate.get("status")
        == "C985_D20_STATIONARY_ATOM_FLOW_LIFT_CERTIFIED",
        "lambda_2_matches_transfer_second_modulus": observable_values["lambda_2"]
        == int(transfer_report["witness"]["spectral_second_modulus_x1e12"]),
        "lambda_2_matches_expected": observable_values["lambda_2"] == 587252536214,
        "lambda_3_matches_expected": observable_values["lambda_3"] == 348829795192,
        "lambda_2_minus_lambda_3_matches_expected": observable_values[
            "lambda_2_minus_lambda_3"
        ]
        == 238422741021,
        "spectral_gap_matches_transfer": observable_values["spectral_gap"]
        == int(transfer_report["witness"]["spectral_gap_x1e12"]),
        "lambda_min_matches_expected": observable_values["lambda_min"] == -23107307402,
        "eigen_residual_is_zero_at_x1e12": int(eigenmode["eigen_residual_max_x1e12"])
        == 0,
        "stationary_orthogonality_is_zero_at_x1e12": int(
            eigenmode["stationary_orthogonality_abs_x1e12"]
        )
        == 0,
        "stationary_norm_residual_is_zero_at_x1e12": int(
            eigenmode["stationary_norm_residual_abs_x1e12"]
        )
        == 0,
        "positive_vertex_count_is_121": positive_count == 121,
        "negative_vertex_count_is_100": negative_count == 100,
        "positive_stationary_mass_matches_expected": positive_mass == 626107108209,
        "negative_stationary_mass_matches_expected": negative_mass == 373892891791,
        "cut_edge_count_is_4007": len(cut_rows) == 4007,
        "within_edge_counts_match_expected": within_positive_edge_count == 5968
        and within_negative_edge_count == 3060,
        "cut_flux_matches_expected": cut_flux == 238962451389,
        "one_way_cut_flux_matches_expected": one_way_cut_flux == 119481225694,
        "cut_conductance_matches_expected": cut_conductance == 319560035288,
        "all_mask_classes_are_pure_sign": all(int(row["nodal_sign"]) != 0 for row in mask_rows),
        "positive_mask_classes_match_expected": positive_mask_classes
        == [0, 1, 2, 3, 10, 11, 12],
        "negative_mask_classes_match_expected": negative_mask_classes
        == [4, 5, 6, 7, 8, 9, 13],
        "mask_cut_edges_match_expected": mask_cut_edge_count == 16,
        "mask_within_edges_match_expected": mask_within_positive_edge_count == 14
        and mask_within_negative_edge_count == 14,
        "top_positive_atom_is_7": int(top_positive_atom["atom_id"]) == 7,
        "top_negative_atom_is_12": int(top_negative_atom["atom_id"]) == 12,
        "atom_7_is_pure_positive": spectral_cut["atom_comparison"][
            "atom_7_positive_fraction_x1e12"
        ]
        == PROBABILITY_SCALE,
        "atom_12_is_pure_negative": spectral_cut["atom_comparison"][
            "atom_12_positive_fraction_x1e12"
        ]
        == 0,
        "basin_positive_fractions_match_expected": [
            int(row["positive_fraction_x1e12"]) for row in basin_rows
        ]
        == [684970520566, 624064619314, 598273462377],
        "vertex_table_shape_is_221_by_10": tuple(vertex_table.shape)
        == (221, len(EIGENMODE_VERTEX_COLUMNS)),
        "cut_edge_table_shape_is_4007_by_12": tuple(cut_edge_table.shape)
        == (4007, len(EIGENMODE_CUT_EDGE_COLUMNS)),
        "mask_table_shape_is_14_by_16": tuple(mask_table.shape)
        == (14, len(MASK_EIGENMODE_COLUMNS)),
        "atom_table_shape_is_6_by_7": tuple(atom_table.shape)
        == (6, len(ATOM_EIGENMODE_COLUMNS)),
        "basin_table_shape_is_3_by_7": tuple(basin_table.shape)
        == (3, len(BASIN_EIGENMODE_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(EIGENMODE_OBSERVABLE_COLUMNS)),
        "second_eigenfunction_shape_is_221": tuple(eigenfunction_x1e12.shape) == (221,),
        "nodal_sign_shape_is_221": tuple(signs.shape) == (221,),
        "transfer_json_schema_available": transfer.get("schema")
        == "c985.d20_signature_subboundary_transfer_operator@1",
        "subboundary_json_schema_available": subboundary.get("schema")
        == "c985.d20_recurrent_signature_subboundary@1",
        "atom_flow_json_schema_available": atom_flow.get("schema")
        == "c985.d20_stationary_atom_flow_lift@1",
        "atom_flow_signature_table_available": "signature_flow_table"
        in atom_flow_tables.files,
    }

    witness = {
        "lambda_2_x1e12": observable_values["lambda_2"],
        "lambda_3_x1e12": observable_values["lambda_3"],
        "lambda_2_minus_lambda_3_x1e12": observable_values["lambda_2_minus_lambda_3"],
        "spectral_gap_x1e12": observable_values["spectral_gap"],
        "lambda_min_x1e12": observable_values["lambda_min"],
        "positive_vertex_count": positive_count,
        "negative_vertex_count": negative_count,
        "positive_stationary_mass_x1e12": positive_mass,
        "negative_stationary_mass_x1e12": negative_mass,
        "cut_edge_count": len(cut_rows),
        "within_positive_edge_count": within_positive_edge_count,
        "within_negative_edge_count": within_negative_edge_count,
        "undirected_cut_flux_x1e12": cut_flux,
        "one_way_cut_flux_x1e12": one_way_cut_flux,
        "cut_conductance_x1e12": cut_conductance,
        "positive_mask_class_ids": positive_mask_classes,
        "negative_mask_class_ids": negative_mask_classes,
        "mask_cut_edge_count": mask_cut_edge_count,
        "mask_within_positive_edge_count": mask_within_positive_edge_count,
        "mask_within_negative_edge_count": mask_within_negative_edge_count,
        "top_positive_atom_id": int(top_positive_atom["atom_id"]),
        "top_negative_atom_id": int(top_negative_atom["atom_id"]),
        "basin_positive_fraction_x1e12": {
            str(row["basin_code"]): int(row["positive_fraction_x1e12"])
            for row in basin_rows
        },
        "basin_positive_composition_x1e12": {
            str(row["basin_code"]): int(row["positive_side_composition_x1e12"])
            for row in basin_rows
        },
        "basin_negative_composition_x1e12": {
            str(row["basin_code"]): int(row["negative_side_composition_x1e12"])
            for row in basin_rows
        },
        "eigenmode_vertex_table_sha256": sha_array(vertex_table),
        "eigenmode_cut_edge_table_sha256": sha_array(cut_edge_table),
        "mask_eigenmode_table_sha256": sha_array(mask_table),
        "atom_eigenmode_table_sha256": sha_array(atom_table),
        "basin_eigenmode_table_sha256": sha_array(basin_table),
        "eigenmode_observable_table_sha256": sha_array(observable_table),
        "second_eigenfunction_x1e12_sha256": sha_array(eigenfunction_x1e12),
        "nodal_signs_sha256": sha_array(signs),
    }

    certificate = {
        "schema": "c985.d20_signature_transfer_spectral_cut_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_TRANSFER_SPECTRAL_CUT_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the second transfer eigenmode has a reproducible eigengap below lambda_2",
            "the nodal cut splits the 221 recurrent signatures into 121 positive and 100 negative vertices",
            "the cut is exactly pure on the 14 carrier-mask quotient classes",
            "the cut separates atom 7 as purely positive and atom 12 as purely negative, with atom 19 acting as a mixed bridge",
            "the nodal cut is not a direct core-source-lobe recovery: all three core basin labels have positive-side majority participation",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_transfer_spectral_cut@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The certified signature-subboundary transfer operator has a "
            "verified second eigenmode whose nodal cut is a clean carrier-mask "
            "quotient split, with 121 positive and 100 negative signature "
            "classes, 4,007 crossing signature edges, and a documented "
            "comparison to the original core basin labels."
        ),
        "stage_protocol": {
            "draft": "compute the second eigenfunction of the reversible signature transfer similarity",
            "witness": "materialize eigenmode values, nodal signs, crossing edges, carrier-mask signs, atom participation, and core-basin comparison",
            "coherence": "check eigen residuals, eigengap, cut masses, cut flux, pure mask-class split, and basin comparison",
            "closure": "certify the spectral cut without claiming a continuum boundary or a unique physical transition law",
            "emit": "emit spectral-cut JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "signature_transfer_report": input_entry(
                SIGNATURE_TRANSFER_REPORT,
                {
                    "status": transfer_report.get("status"),
                    "certificate_sha256": transfer_report.get("certificate_sha256"),
                },
            ),
            "signature_transfer": input_entry(SIGNATURE_TRANSFER_JSON),
            "signature_transfer_tables": input_entry(SIGNATURE_TRANSFER_TABLES),
            "signature_transfer_certificate": input_entry(SIGNATURE_TRANSFER_CERTIFICATE),
            "signature_subboundary_report": input_entry(
                SIGNATURE_SUBBOUNDARY_REPORT,
                {
                    "status": subboundary_report.get("status"),
                    "certificate_sha256": subboundary_report.get("certificate_sha256"),
                },
            ),
            "signature_subboundary": input_entry(SIGNATURE_SUBBOUNDARY_JSON),
            "signature_subboundary_tables": input_entry(SIGNATURE_SUBBOUNDARY_TABLES),
            "signature_subboundary_certificate": input_entry(
                SIGNATURE_SUBBOUNDARY_CERTIFICATE
            ),
            "atom_flow_report": input_entry(
                ATOM_FLOW_REPORT,
                {
                    "status": atom_flow_report.get("status"),
                    "certificate_sha256": atom_flow_report.get("certificate_sha256"),
                },
            ),
            "atom_flow": input_entry(ATOM_FLOW_JSON),
            "atom_flow_tables": input_entry(ATOM_FLOW_TABLES),
            "atom_flow_certificate": input_entry(ATOM_FLOW_CERTIFICATE),
            "atom_flow_node_contributions": input_entry(ATOM_FLOW_NODE_CONTRIBUTIONS),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_transfer_spectral_cut": relpath(
                OUT_DIR / "signature_transfer_spectral_cut.json"
            ),
            "signature_eigenmode_vertices_csv": relpath(
                OUT_DIR / "signature_eigenmode_vertices.csv"
            ),
            "signature_eigenmode_cut_edges_csv": relpath(
                OUT_DIR / "signature_eigenmode_cut_edges.csv"
            ),
            "carrier_mask_eigenmode_summary_csv": relpath(
                OUT_DIR / "carrier_mask_eigenmode_summary.csv"
            ),
            "atom_eigenmode_summary_csv": relpath(OUT_DIR / "atom_eigenmode_summary.csv"),
            "core_basin_eigenmode_summary_csv": relpath(
                OUT_DIR / "core_basin_eigenmode_summary.csv"
            ),
            "signature_transfer_spectral_observables_csv": relpath(
                OUT_DIR / "signature_transfer_spectral_observables.csv"
            ),
            "signature_transfer_spectral_cut_tables": relpath(
                OUT_DIR / "signature_transfer_spectral_cut_tables.npz"
            ),
            "signature_transfer_spectral_cut_certificate": relpath(
                OUT_DIR / "signature_transfer_spectral_cut_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the second eigenfunction and nodal sign split of the signature transfer operator",
                "crossing-edge, cut-flux, and conductance observables for the nodal cut",
                "the pure-sign carrier-mask quotient split induced by the eigenmode",
                "atom-level participation of the eigenmode split",
                "comparison of the split to the original core basin labels through atom-flow contributions",
            ],
            "does_not_certify_because_not_required": [
                "a continuum Laplacian or geometric limit",
                "a physically canonical choice among other possible transfer laws",
                "higher eigenmode clustering beyond the second eigenmode",
                "new associator, pentagon, pivotal, spherical, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Promote the pure carrier-mask spectral split to a two-state quotient "
            "dynamics: collapse the 221-node transfer operator along the nodal cut, "
            "certify the exact two-state flux/return law, and compare it to the "
            "10/43/boundary core basin masses."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_transfer_spectral_cut_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified signature transfer, recurrent subboundary, and atom-flow artifacts",
            "reconstruct the reversible similarity and second Markov eigenfunction",
            "orient the eigenfunction by larger positive stationary mass",
            "materialize nodal signs, crossing edges, carrier-mask summaries, atom summaries, and core-basin comparison",
            "verify eigen residuals, eigengap, cut masses, cut flux, mask purity, and artifact reproducibility",
            "check source hashes and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_transfer_spectral_cut": spectral_cut,
        "signature_eigenmode_vertices_csv": csv_text(EIGENMODE_VERTEX_COLUMNS, vertex_rows),
        "signature_eigenmode_cut_edges_csv": csv_text(EIGENMODE_CUT_EDGE_COLUMNS, cut_rows),
        "carrier_mask_eigenmode_summary_csv": csv_text(MASK_EIGENMODE_COLUMNS, mask_rows),
        "atom_eigenmode_summary_csv": csv_text(ATOM_EIGENMODE_COLUMNS, atom_rows),
        "core_basin_eigenmode_summary_csv": csv_text(BASIN_EIGENMODE_COLUMNS, basin_rows),
        "signature_transfer_spectral_observables_csv": csv_text(
            EIGENMODE_OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "eigenmode_vertex_table": vertex_table,
        "eigenmode_cut_edge_table": cut_edge_table,
        "mask_eigenmode_table": mask_table,
        "atom_eigenmode_table": atom_table,
        "basin_eigenmode_table": basin_table,
        "eigenmode_observable_table": observable_table,
        "second_eigenfunction_x1e12": eigenfunction_x1e12,
        "nodal_signs": signs,
        "signature_transfer_spectral_cut_certificate": certificate,
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
        OUT_DIR / "signature_transfer_spectral_cut.json",
        payloads["signature_transfer_spectral_cut"],
    )
    (OUT_DIR / "signature_eigenmode_vertices.csv").write_text(
        payloads["signature_eigenmode_vertices_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "signature_eigenmode_cut_edges.csv").write_text(
        payloads["signature_eigenmode_cut_edges_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "carrier_mask_eigenmode_summary.csv").write_text(
        payloads["carrier_mask_eigenmode_summary_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "atom_eigenmode_summary.csv").write_text(
        payloads["atom_eigenmode_summary_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "core_basin_eigenmode_summary.csv").write_text(
        payloads["core_basin_eigenmode_summary_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "signature_transfer_spectral_observables.csv").write_text(
        payloads["signature_transfer_spectral_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_transfer_spectral_cut_tables.npz",
        eigenmode_vertex_table=payloads["eigenmode_vertex_table"],
        eigenmode_cut_edge_table=payloads["eigenmode_cut_edge_table"],
        mask_eigenmode_table=payloads["mask_eigenmode_table"],
        atom_eigenmode_table=payloads["atom_eigenmode_table"],
        basin_eigenmode_table=payloads["basin_eigenmode_table"],
        eigenmode_observable_table=payloads["eigenmode_observable_table"],
        second_eigenfunction_x1e12=payloads["second_eigenfunction_x1e12"],
        nodal_signs=payloads["nodal_signs"],
    )
    write_json(
        OUT_DIR / "signature_transfer_spectral_cut_certificate.json",
        payloads["signature_transfer_spectral_cut_certificate"],
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
                "lambda_2_x1e12": witness["lambda_2_x1e12"],
                "positive_vertex_count": witness["positive_vertex_count"],
                "negative_vertex_count": witness["negative_vertex_count"],
                "cut_edge_count": witness["cut_edge_count"],
                "positive_mask_class_ids": witness["positive_mask_class_ids"],
                "negative_mask_class_ids": witness["negative_mask_class_ids"],
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
