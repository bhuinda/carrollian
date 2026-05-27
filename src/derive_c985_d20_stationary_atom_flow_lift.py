from __future__ import annotations

import json
from collections import Counter, defaultdict
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_boundary_transfer_operator import (
        OUT_DIR as BOUNDARY_TRANSFER_DIR,
    )
    from .derive_c985_d20_symbolic_rewrite_rules import csv_text, histogram
    from .derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        OBJECT_LABELS,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_d20_boundary_transfer_operator import (
        OUT_DIR as BOUNDARY_TRANSFER_DIR,
    )
    from derive_c985_d20_symbolic_rewrite_rules import csv_text, histogram
    from derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        OBJECT_LABELS,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "c985_d20_stationary_atom_flow_lift"
STATUS = "C985_D20_STATIONARY_ATOM_FLOW_LIFT_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

REWRITE_COMPLEX_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_rewrite_complex_hyperbolicity"
ATLAS_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_boundary_invariant_atlas"
POINCARE_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_poincare_embedding"
SYMBOLIC_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_symbolic_rewrite_rules"

REWRITE_COMPLEX_REPORT = REWRITE_COMPLEX_DIR / "report.json"
REWRITE_COMPLEX_JSON = REWRITE_COMPLEX_DIR / "rewrite_complex.json"
REWRITE_COMPLEX_CERTIFICATE = REWRITE_COMPLEX_DIR / "rewrite_complex_certificate.json"
ATLAS_REPORT = ATLAS_DIR / "report.json"
ATLAS_JSON = ATLAS_DIR / "d20_boundary_invariant_atlas.json"
ATLAS_TABLES = ATLAS_DIR / "d20_boundary_invariant_atlas.npz"
ATLAS_CERTIFICATE = ATLAS_DIR / "projection_certificate.json"
POINCARE_REPORT = POINCARE_DIR / "report.json"
POINCARE_JSON = POINCARE_DIR / "poincare_embedding.json"
POINCARE_TABLES = POINCARE_DIR / "poincare_embedding.npz"
POINCARE_CERTIFICATE = POINCARE_DIR / "embedding_certificate.json"
SYMBOLIC_REPORT = SYMBOLIC_DIR / "report.json"
SYMBOLIC_JSON = SYMBOLIC_DIR / "symbolic_alphabet.json"
SYMBOLIC_TABLES = SYMBOLIC_DIR / "symbolic_rewrite_tables.npz"
SYMBOLIC_CERTIFICATE = SYMBOLIC_DIR / "symbolic_rewrite_certificate.json"
BOUNDARY_TRANSFER_REPORT = BOUNDARY_TRANSFER_DIR / "report.json"
BOUNDARY_TRANSFER_JSON = BOUNDARY_TRANSFER_DIR / "boundary_transfer_operator.json"
BOUNDARY_TRANSFER_TABLES = BOUNDARY_TRANSFER_DIR / "boundary_transfer_tables.npz"
BOUNDARY_TRANSFER_CERTIFICATE = BOUNDARY_TRANSFER_DIR / "boundary_transfer_certificate.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_c985_d20_stationary_atom_flow_lift.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_d20_stationary_atom_flow_lift.py"

PROBABILITY_SCALE = 1_000_000_000_000
ATOM_COUNT = 20
SIGNATURE_CLASS_COUNT = 233
MAX_NODE_ATOM_SLOTS = 3

NODE_ATOM_CONTRIBUTION_COLUMNS = [
    "contribution_id",
    "node_id",
    "atom_slot_index",
    "atom_id",
    "symbol_id",
    "node_stationary_mass_x1e12",
    "atom_slot_mass_x1e12",
    "node_basin_code",
]

ATOM_FLOW_COLUMNS = [
    "atom_id",
    "atom_flow_mass_x1e12",
    "active_flow",
    "atom_slot_count",
    "source_node_count",
    "sector_mask",
    "signature_class_count",
    "tensor_path_coefficient_mass",
    "poincare_x_x1e12",
    "poincare_y_x1e12",
    "poincare_radius_x1e12",
    "atom_flow_rank",
    "complement_atom_id",
    "complement_flow_mass_x1e12",
]

SECTOR_FLOW_COLUMNS = [
    "sector_id",
    "sector_label_code",
    "sector_flow_mass_x1e12",
    "active_atom_count",
    "sector_flow_rank",
]

SIGNATURE_FLOW_COLUMNS = [
    "signature_class_id",
    "signature_flow_mass_x1e12",
    "active_flow",
    "active_atom_count",
    "carrier_atom_mask",
    "signature_flow_rank",
]

ATOM_FLOW_OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "active_atom_count": 0,
    "inactive_atom_count": 1,
    "active_sector_count": 2,
    "active_signature_class_count": 3,
    "inactive_signature_class_count": 4,
    "top_atom_mass": 5,
    "top_sector_mass": 6,
    "top_signature_class_mass": 7,
    "atom_flow_center_x": 8,
    "atom_flow_center_y": 9,
    "atom_flow_center_radius": 10,
    "atom_flow_mean_poincare_radius": 11,
    "core_center_delta_radius_abs": 12,
}


def sector_mask(labels: list[str]) -> int:
    mask = 0
    for label in labels:
        mask |= 1 << OBJECT_LABELS.index(label)
    return mask


def scaled(value: float) -> int:
    return int(round(float(value) * PROBABILITY_SCALE))


def fair_split(total: int, count: int) -> list[int]:
    quotient, remainder = divmod(int(total), int(count))
    return [quotient + (1 if index < remainder else 0) for index in range(count)]


def ranks_descending(values: dict[int, int]) -> dict[int, int]:
    return {
        key: rank
        for rank, key in enumerate(
            sorted(values, key=lambda item: (-int(values[item]), int(item))),
            start=1,
        )
    }


def load_stationary_rows(transfer_tables: np.lib.npyio.NpzFile) -> list[dict[str, int]]:
    table = np.asarray(transfer_tables["stationary_distribution_table"], dtype=np.int64)
    return [
        {
            "node_id": int(row[0]),
            "stationary_mass_x1e12": int(row[1]),
            "basin_code": int(row[2]),
        }
        for row in table
    ]


def symbolic_signature_sets(symbolic: dict[str, Any]) -> dict[int, list[int]]:
    return {
        int(row["atom_id"]): [int(value) for value in row["signature_class_ids"]]
        for row in symbolic["alphabet"]
    }


def build_node_atom_contributions(
    stationary_rows: list[dict[str, int]],
    node_by_id: dict[int, dict[str, Any]],
) -> tuple[list[dict[str, int]], np.ndarray]:
    rows: list[dict[str, int]] = []
    table_rows: list[list[int]] = []
    for stationary_row in stationary_rows:
        node_id = int(stationary_row["node_id"])
        node = node_by_id[node_id]
        atom_ids = [int(value) for value in node["canonical_atom_ids"]]
        symbol_ids = [int(value) for value in node["canonical_symbol_ids"]]
        splits = fair_split(int(stationary_row["stationary_mass_x1e12"]), len(atom_ids))
        for slot_index, (atom_id, symbol_id, slot_mass) in enumerate(
            zip(atom_ids, symbol_ids, splits)
        ):
            row = {
                "contribution_id": len(rows),
                "node_id": node_id,
                "atom_slot_index": slot_index,
                "atom_id": atom_id,
                "symbol_id": symbol_id,
                "node_stationary_mass_x1e12": int(stationary_row["stationary_mass_x1e12"]),
                "atom_slot_mass_x1e12": int(slot_mass),
                "node_basin_code": int(stationary_row["basin_code"]),
            }
            rows.append(row)
            table_rows.append([int(row[column]) for column in NODE_ATOM_CONTRIBUTION_COLUMNS])
    return rows, np.asarray(table_rows, dtype=np.int64)


def atom_label_from_poincare(poincare: dict[str, Any], atom_id: int) -> str:
    return str(poincare["coordinates"][atom_id]["atom_label"])


def build_atom_flow_rows(
    contribution_rows: list[dict[str, int]],
    atlas: dict[str, Any],
    poincare: dict[str, Any],
    signature_sets: dict[int, list[int]],
) -> tuple[list[dict[str, Any]], np.ndarray, dict[int, int]]:
    atom_masses = {atom_id: 0 for atom_id in range(ATOM_COUNT)}
    atom_slots: Counter[int] = Counter()
    atom_nodes: dict[int, set[int]] = {atom_id: set() for atom_id in range(ATOM_COUNT)}
    for row in contribution_rows:
        atom_id = int(row["atom_id"])
        atom_masses[atom_id] += int(row["atom_slot_mass_x1e12"])
        atom_slots[atom_id] += 1
        atom_nodes[atom_id].add(int(row["node_id"]))

    flow_ranks = ranks_descending(atom_masses)
    rows: list[dict[str, Any]] = []
    table_rows: list[list[int]] = []
    for atom_id in range(ATOM_COUNT):
        atlas_row = atlas["atom_rows"][atom_id]
        coordinate = poincare["coordinates"][atom_id]
        complement_id = int(atlas_row["complement_atom_id"])
        row = {
            "atom_id": atom_id,
            "atom_label": atom_label_from_poincare(poincare, atom_id),
            "atom_flow_mass_x1e12": int(atom_masses[atom_id]),
            "active_flow": int(atom_masses[atom_id] > 0),
            "atom_slot_count": int(atom_slots[atom_id]),
            "source_node_count": len(atom_nodes[atom_id]),
            "source_node_ids": sorted(atom_nodes[atom_id]),
            "h6_triple": atlas_row["h6_triple"],
            "sector_mask": sector_mask(atlas_row["h6_triple"]),
            "signature_class_count": int(atlas_row["internal_signature_class_count"]),
            "active_signature_class_count": len(signature_sets.get(atom_id, []))
            if atom_masses[atom_id] > 0
            else 0,
            "tensor_path_coefficient_mass": int(atlas_row["tensor_path_coefficient_mass"]),
            "poincare_x_x1e12": scaled(float(coordinate["x"])),
            "poincare_y_x1e12": scaled(float(coordinate["y"])),
            "poincare_radius_x1e12": scaled(float(coordinate["radius"])),
            "atom_flow_rank": flow_ranks[atom_id],
            "complement_atom_id": complement_id,
            "complement_flow_mass_x1e12": int(atom_masses[complement_id]),
        }
        rows.append(row)
        table_rows.append([int(row[column]) for column in ATOM_FLOW_COLUMNS])
    return rows, np.asarray(table_rows, dtype=np.int64), atom_masses


def build_sector_flow_rows(
    atom_masses: dict[int, int],
    atlas: dict[str, Any],
) -> tuple[list[dict[str, Any]], np.ndarray, dict[str, int]]:
    sector_masses = {label: 0 for label in OBJECT_LABELS}
    sector_atoms = {label: set() for label in OBJECT_LABELS}
    for atom_id, atom_mass in atom_masses.items():
        if atom_mass <= 0:
            continue
        triple = [str(label) for label in atlas["atom_rows"][atom_id]["h6_triple"]]
        for label, share in zip(triple, fair_split(atom_mass, len(triple))):
            sector_masses[label] += share
            sector_atoms[label].add(atom_id)

    ranks = {
        label: rank
        for rank, label in enumerate(
            sorted(OBJECT_LABELS, key=lambda item: (-sector_masses[item], OBJECT_LABELS.index(item))),
            start=1,
        )
    }
    rows: list[dict[str, Any]] = []
    table_rows: list[list[int]] = []
    for sector_id, label in enumerate(OBJECT_LABELS):
        row = {
            "sector_id": sector_id,
            "sector_label": label,
            "sector_label_code": sector_id,
            "sector_flow_mass_x1e12": int(sector_masses[label]),
            "active_atom_count": len(sector_atoms[label]),
            "active_atom_ids": sorted(sector_atoms[label]),
            "sector_flow_rank": ranks[label],
        }
        rows.append(row)
        table_rows.append([int(row[column]) for column in SECTOR_FLOW_COLUMNS])
    return rows, np.asarray(table_rows, dtype=np.int64), sector_masses


def build_signature_flow_rows(
    atom_masses: dict[int, int],
    signature_sets: dict[int, list[int]],
) -> tuple[list[dict[str, Any]], np.ndarray, np.ndarray]:
    signature_masses = {signature_id: 0 for signature_id in range(SIGNATURE_CLASS_COUNT)}
    signature_atoms = {signature_id: set() for signature_id in range(SIGNATURE_CLASS_COUNT)}
    membership = np.zeros((ATOM_COUNT, SIGNATURE_CLASS_COUNT), dtype=np.int8)
    for atom_id, signatures in signature_sets.items():
        for signature_id in signatures:
            membership[atom_id, signature_id] = 1
        atom_mass = atom_masses.get(atom_id, 0)
        if atom_mass <= 0:
            continue
        for signature_id, share in zip(signatures, fair_split(atom_mass, len(signatures))):
            signature_masses[signature_id] += share
            signature_atoms[signature_id].add(atom_id)

    ranks = ranks_descending(signature_masses)
    rows: list[dict[str, Any]] = []
    table_rows: list[list[int]] = []
    for signature_id in range(SIGNATURE_CLASS_COUNT):
        carrier_mask = sum(1 << atom_id for atom_id in sorted(signature_atoms[signature_id]))
        row = {
            "signature_class_id": signature_id,
            "signature_flow_mass_x1e12": int(signature_masses[signature_id]),
            "active_flow": int(signature_masses[signature_id] > 0),
            "active_atom_count": len(signature_atoms[signature_id]),
            "carrier_atom_ids": sorted(signature_atoms[signature_id]),
            "carrier_atom_mask": int(carrier_mask),
            "signature_flow_rank": ranks[signature_id],
        }
        rows.append(row)
        table_rows.append([int(row[column]) for column in SIGNATURE_FLOW_COLUMNS])
    return rows, np.asarray(table_rows, dtype=np.int64), membership


def flow_center_observables(
    atom_masses: dict[int, int],
    poincare: dict[str, Any],
    transfer_report: dict[str, Any],
) -> dict[str, int]:
    center_x = 0.0
    center_y = 0.0
    mean_radius = 0.0
    for atom_id, atom_mass in atom_masses.items():
        weight = atom_mass / PROBABILITY_SCALE
        coordinate = poincare["coordinates"][atom_id]
        center_x += weight * float(coordinate["x"])
        center_y += weight * float(coordinate["y"])
        mean_radius += weight * float(coordinate["radius"])
    center_radius = float((center_x * center_x + center_y * center_y) ** 0.5)
    core_center = transfer_report["witness"]["geometric_observables"]["weighted_poincare_center"]
    return {
        "atom_flow_center_x_x1e12": scaled(center_x),
        "atom_flow_center_y_x1e12": scaled(center_y),
        "atom_flow_center_radius_x1e12": scaled(center_radius),
        "atom_flow_mean_poincare_radius_x1e12": scaled(mean_radius),
        "core_center_x_delta_abs_x1e12": abs(scaled(center_x) - int(core_center["x_x1e12"])),
        "core_center_y_delta_abs_x1e12": abs(scaled(center_y) - int(core_center["y_x1e12"])),
        "core_center_radius_delta_abs_x1e12": abs(
            scaled(center_radius) - int(core_center["radius_x1e12"])
        ),
    }


def build_observable_rows(summary: dict[str, Any]) -> tuple[list[dict[str, int]], np.ndarray]:
    values = {
        "active_atom_count": int(summary["active_atom_count"]),
        "inactive_atom_count": int(summary["inactive_atom_count"]),
        "active_sector_count": int(summary["active_sector_count"]),
        "active_signature_class_count": int(summary["active_signature_class_count"]),
        "inactive_signature_class_count": int(summary["inactive_signature_class_count"]),
        "top_atom_mass": int(summary["top_atom_mass_x1e12"]),
        "top_sector_mass": int(summary["top_sector_mass_x1e12"]),
        "top_signature_class_mass": int(summary["top_signature_class_mass_x1e12"]),
        "atom_flow_center_x": int(summary["geometric_observables"]["atom_flow_center_x_x1e12"]),
        "atom_flow_center_y": int(summary["geometric_observables"]["atom_flow_center_y_x1e12"]),
        "atom_flow_center_radius": int(
            summary["geometric_observables"]["atom_flow_center_radius_x1e12"]
        ),
        "atom_flow_mean_poincare_radius": int(
            summary["geometric_observables"]["atom_flow_mean_poincare_radius_x1e12"]
        ),
        "core_center_delta_radius_abs": int(
            summary["geometric_observables"]["core_center_radius_delta_abs_x1e12"]
        ),
    }
    rows: list[dict[str, int]] = []
    table_rows: list[list[int]] = []
    for name, code in sorted(OBSERVABLE_CODES.items(), key=lambda item: item[1]):
        row = {
            "observable_id": len(rows),
            "observable_code": int(code),
            "value_x1e12": int(values[name]),
            "aux_id": -1,
        }
        rows.append(row)
        table_rows.append([int(row[column]) for column in ATOM_FLOW_OBSERVABLE_COLUMNS])
    return rows, np.asarray(table_rows, dtype=np.int64)


def build_payloads() -> dict[str, Any]:
    rewrite_report = load_json(REWRITE_COMPLEX_REPORT)
    rewrite_complex = load_json(REWRITE_COMPLEX_JSON)
    rewrite_certificate = load_json(REWRITE_COMPLEX_CERTIFICATE)
    atlas_report = load_json(ATLAS_REPORT)
    atlas = load_json(ATLAS_JSON)
    atlas_certificate = load_json(ATLAS_CERTIFICATE)
    poincare_report = load_json(POINCARE_REPORT)
    poincare = load_json(POINCARE_JSON)
    poincare_certificate = load_json(POINCARE_CERTIFICATE)
    symbolic_report = load_json(SYMBOLIC_REPORT)
    symbolic = load_json(SYMBOLIC_JSON)
    symbolic_certificate = load_json(SYMBOLIC_CERTIFICATE)
    transfer_report = load_json(BOUNDARY_TRANSFER_REPORT)
    boundary_transfer = load_json(BOUNDARY_TRANSFER_JSON)
    transfer_certificate = load_json(BOUNDARY_TRANSFER_CERTIFICATE)
    transfer_tables = np.load(BOUNDARY_TRANSFER_TABLES, allow_pickle=False)
    symbolic_tables = np.load(SYMBOLIC_TABLES, allow_pickle=False)
    atlas_tables = np.load(ATLAS_TABLES, allow_pickle=False)
    poincare_tables = np.load(POINCARE_TABLES, allow_pickle=False)

    node_by_id = {int(node["node_id"]): node for node in rewrite_complex["nodes"]}
    stationary_rows = load_stationary_rows(transfer_tables)
    signature_sets = symbolic_signature_sets(symbolic)
    contribution_rows, contribution_table = build_node_atom_contributions(
        stationary_rows,
        node_by_id,
    )
    atom_rows, atom_table, atom_masses = build_atom_flow_rows(
        contribution_rows,
        atlas,
        poincare,
        signature_sets,
    )
    sector_rows, sector_table, sector_masses = build_sector_flow_rows(atom_masses, atlas)
    signature_rows, signature_table, atom_signature_membership = build_signature_flow_rows(
        atom_masses,
        signature_sets,
    )

    active_atom_ids = [atom_id for atom_id, mass in atom_masses.items() if mass > 0]
    inactive_atom_ids = [atom_id for atom_id, mass in atom_masses.items() if mass == 0]
    active_signature_ids = [
        int(row["signature_class_id"])
        for row in signature_rows
        if int(row["signature_flow_mass_x1e12"]) > 0
    ]
    inactive_signature_ids = [
        int(row["signature_class_id"])
        for row in signature_rows
        if int(row["signature_flow_mass_x1e12"]) == 0
    ]
    top_atom_mass = max(atom_masses.values())
    top_atom_ids = [atom_id for atom_id, mass in atom_masses.items() if mass == top_atom_mass]
    top_sector_mass = max(sector_masses.values())
    top_sector_labels = [
        label for label, mass in sector_masses.items() if mass == top_sector_mass
    ]
    top_signature_mass = max(
        int(row["signature_flow_mass_x1e12"]) for row in signature_rows
    )
    top_signature_ids = [
        int(row["signature_class_id"])
        for row in signature_rows
        if int(row["signature_flow_mass_x1e12"]) == top_signature_mass
    ]
    geometry = flow_center_observables(atom_masses, poincare, transfer_report)

    summary = {
        "core_node_count": len(stationary_rows),
        "node_atom_contribution_count": len(contribution_rows),
        "active_atom_count": len(active_atom_ids),
        "inactive_atom_count": len(inactive_atom_ids),
        "active_atom_ids": active_atom_ids,
        "inactive_atom_ids": inactive_atom_ids,
        "atom_flow_mass_x1e12": {
            str(atom_id): int(atom_masses[atom_id]) for atom_id in range(ATOM_COUNT)
        },
        "atom_flow_mass_sum_x1e12": int(sum(atom_masses.values())),
        "top_atom_ids": top_atom_ids,
        "top_atom_mass_x1e12": int(top_atom_mass),
        "active_sector_count": sum(1 for value in sector_masses.values() if value > 0),
        "sector_flow_mass_x1e12": {
            label: int(sector_masses[label]) for label in OBJECT_LABELS
        },
        "sector_flow_mass_sum_x1e12": int(sum(sector_masses.values())),
        "top_sector_labels": top_sector_labels,
        "top_sector_mass_x1e12": int(top_sector_mass),
        "active_signature_class_count": len(active_signature_ids),
        "inactive_signature_class_count": len(inactive_signature_ids),
        "inactive_signature_class_ids": inactive_signature_ids,
        "signature_flow_mass_sum_x1e12": int(
            sum(int(row["signature_flow_mass_x1e12"]) for row in signature_rows)
        ),
        "top_signature_class_ids": top_signature_ids,
        "top_signature_class_mass_x1e12": int(top_signature_mass),
        "signature_active_atom_count_histogram": histogram(
            [int(row["active_atom_count"]) for row in signature_rows if int(row["active_flow"]) == 1]
        ),
        "atom_slot_count_histogram": histogram(
            [int(row["atom_slot_count"]) for row in atom_rows if int(row["active_flow"]) == 1]
        ),
        "geometric_observables": geometry,
    }
    observable_rows, observable_table = build_observable_rows(summary)

    atom_flow_lift = {
        "schema": "c985.d20_stationary_atom_flow_lift@1",
        "object": "d20",
        "source_boundary_transfer_certificate": transfer_report.get("certificate_sha256"),
        "lift_rule": {
            "node_to_atom": "split each core-node stationary mass across its three canonical atom slots, preserving repeated atom slots",
            "integer_split": "use exact x1e12 integer mass; divide fairly left-to-right so each output layer sums exactly to 1e12",
            "atom_to_sector": "split active atom mass across the three H6 sectors in its d20 atom",
            "atom_to_signature_class": "split active atom mass uniformly across its certified symbolic signature-class set",
            "probability_scale": PROBABILITY_SCALE,
        },
        "node_atom_contributions": contribution_rows,
        "atom_flow_rows": atom_rows,
        "sector_flow_rows": sector_rows,
        "signature_flow_rows": signature_rows,
        "observable_codebook": OBSERVABLE_CODES,
        "flow_observables": observable_rows,
        "summary": summary,
    }

    expected_atom_masses = {
        "1": 77350993273,
        "4": 85180709940,
        "7": 275942307799,
        "11": 60252076861,
        "12": 330723741064,
        "19": 170550171063,
    }
    expected_sector_masses = {
        "B-": 146158003672,
        "B+": 156108937067,
        "V-": 158718842621,
        "V+": 203008060691,
        "S-": 168914851907,
        "S+": 167091304042,
    }

    checks = {
        "rewrite_complex_report_certified": rewrite_report.get("status")
        == "C985_D20_REWRITE_COMPLEX_HYPERBOLICITY_CERTIFIED",
        "rewrite_complex_certificate_certified": rewrite_certificate.get("status")
        == "C985_D20_REWRITE_COMPLEX_HYPERBOLICITY_CERTIFIED",
        "boundary_atlas_report_certified": atlas_report.get("status")
        == "C985_D20_BOUNDARY_INVARIANT_ATLAS_CERTIFIED",
        "boundary_atlas_certificate_certified": atlas_certificate.get("status")
        == "C985_D20_BOUNDARY_INVARIANT_ATLAS_CERTIFIED",
        "poincare_report_certified": poincare_report.get("status")
        == "C985_D20_POINCARE_EMBEDDING_CERTIFIED",
        "poincare_certificate_certified": poincare_certificate.get("status")
        == "C985_D20_POINCARE_EMBEDDING_CERTIFIED",
        "symbolic_report_certified": symbolic_report.get("status")
        == "C985_D20_SYMBOLIC_REWRITE_RULES_CERTIFIED",
        "symbolic_certificate_certified": symbolic_certificate.get("status")
        == "C985_D20_SYMBOLIC_REWRITE_RULES_CERTIFIED",
        "boundary_transfer_report_certified": transfer_report.get("status")
        == "C985_D20_BOUNDARY_TRANSFER_OPERATOR_CERTIFIED",
        "boundary_transfer_certificate_certified": transfer_certificate.get("status")
        == "C985_D20_BOUNDARY_TRANSFER_OPERATOR_CERTIFIED",
        "core_node_count_is_12": len(stationary_rows) == 12,
        "node_atom_contribution_count_is_36": len(contribution_rows) == 36,
        "node_atom_contribution_table_shape_is_36_by_8": tuple(contribution_table.shape)
        == (36, len(NODE_ATOM_CONTRIBUTION_COLUMNS)),
        "active_atom_ids_are_symbolic_alphabet": active_atom_ids == [1, 4, 7, 11, 12, 19],
        "active_atom_count_is_6": summary["active_atom_count"] == 6,
        "inactive_atom_count_is_14": summary["inactive_atom_count"] == 14,
        "atom_flow_mass_sums_to_one": summary["atom_flow_mass_sum_x1e12"]
        == PROBABILITY_SCALE,
        "active_atom_masses_match_expected": {
            key: summary["atom_flow_mass_x1e12"][key] for key in expected_atom_masses
        }
        == expected_atom_masses,
        "top_atom_is_12": summary["top_atom_ids"] == [12],
        "top_atom_mass_matches_expected": summary["top_atom_mass_x1e12"]
        == 330723741064,
        "all_six_sectors_active": summary["active_sector_count"] == 6,
        "sector_flow_mass_sums_to_one": summary["sector_flow_mass_sum_x1e12"]
        == PROBABILITY_SCALE,
        "sector_masses_match_expected": summary["sector_flow_mass_x1e12"]
        == expected_sector_masses,
        "top_sector_is_vplus": summary["top_sector_labels"] == ["V+"],
        "signature_support_count_is_221": summary["active_signature_class_count"] == 221,
        "inactive_signature_count_is_12": summary["inactive_signature_class_count"] == 12,
        "inactive_signature_ids_are_expected": summary["inactive_signature_class_ids"]
        == [39, 40, 41, 42, 43, 44, 184, 185, 186, 187, 188, 189],
        "signature_flow_mass_sums_to_one": summary["signature_flow_mass_sum_x1e12"]
        == PROBABILITY_SCALE,
        "top_signature_classes_are_78_to_84": summary["top_signature_class_ids"]
        == [78, 79, 80, 81, 82, 83, 84],
        "top_signature_mass_matches_expected": summary["top_signature_class_mass_x1e12"]
        == 8055832391,
        "atom_flow_center_matches_core_with_integer_tolerance": geometry[
            "core_center_x_delta_abs_x1e12"
        ]
        <= 16
        and geometry["core_center_y_delta_abs_x1e12"] <= 16
        and geometry["core_center_radius_delta_abs_x1e12"] <= 16,
        "atom_flow_center_radius_matches_expected": geometry[
            "atom_flow_center_radius_x1e12"
        ]
        == 50308637906,
        "atom_flow_mean_radius_is_0_144485801805": geometry[
            "atom_flow_mean_poincare_radius_x1e12"
        ]
        == 144485801805,
        "atom_flow_table_shape_is_20_by_14": tuple(atom_table.shape)
        == (20, len(ATOM_FLOW_COLUMNS)),
        "sector_flow_table_shape_is_6_by_5": tuple(sector_table.shape)
        == (6, len(SECTOR_FLOW_COLUMNS)),
        "signature_flow_table_shape_is_233_by_6": tuple(signature_table.shape)
        == (233, len(SIGNATURE_FLOW_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(ATOM_FLOW_OBSERVABLE_COLUMNS)),
        "symbolic_membership_shape_is_6_by_233": tuple(
            np.asarray(symbolic_tables["alphabet_signature_membership"]).shape
        )
        == (6, 233),
        "atlas_atom_table_shape_is_20_rows": int(np.asarray(atlas_tables["atom_table"]).shape[0])
        == 20,
        "poincare_coordinate_table_shape_is_20_rows": int(
            np.asarray(poincare_tables["coordinate_table"]).shape[0]
        )
        == 20,
        "boundary_transfer_stationary_table_available": "stationary_distribution_table"
        in transfer_tables.files,
    }

    witness = {
        "core_node_count": len(stationary_rows),
        "node_atom_contribution_count": len(contribution_rows),
        "active_atom_count": summary["active_atom_count"],
        "active_atom_ids": active_atom_ids,
        "inactive_atom_count": summary["inactive_atom_count"],
        "atom_flow_mass_x1e12": summary["atom_flow_mass_x1e12"],
        "atom_flow_mass_sum_x1e12": summary["atom_flow_mass_sum_x1e12"],
        "top_atom_ids": summary["top_atom_ids"],
        "top_atom_mass_x1e12": summary["top_atom_mass_x1e12"],
        "active_sector_count": summary["active_sector_count"],
        "sector_flow_mass_x1e12": summary["sector_flow_mass_x1e12"],
        "sector_flow_mass_sum_x1e12": summary["sector_flow_mass_sum_x1e12"],
        "top_sector_labels": summary["top_sector_labels"],
        "active_signature_class_count": summary["active_signature_class_count"],
        "inactive_signature_class_count": summary["inactive_signature_class_count"],
        "inactive_signature_class_ids": summary["inactive_signature_class_ids"],
        "signature_flow_mass_sum_x1e12": summary["signature_flow_mass_sum_x1e12"],
        "top_signature_class_ids": summary["top_signature_class_ids"],
        "top_signature_class_mass_x1e12": summary["top_signature_class_mass_x1e12"],
        "signature_active_atom_count_histogram": summary[
            "signature_active_atom_count_histogram"
        ],
        "atom_slot_count_histogram": summary["atom_slot_count_histogram"],
        "geometric_observables": summary["geometric_observables"],
        "node_atom_contribution_table_sha256": sha_array(contribution_table),
        "atom_flow_table_sha256": sha_array(atom_table),
        "sector_flow_table_sha256": sha_array(sector_table),
        "signature_flow_table_sha256": sha_array(signature_table),
        "atom_signature_membership_sha256": sha_array(atom_signature_membership),
        "atom_flow_observable_table_sha256": sha_array(observable_table),
    }

    certificate = {
        "schema": "c985.d20_stationary_atom_flow_lift_certificate@1",
        "status": STATUS if all(checks.values()) else "C985_D20_STATIONARY_ATOM_FLOW_LIFT_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the stationary 12-node core transfer measure lifts through canonical normal-word atom slots",
            "exact integer mass transport gives six active d20 atoms and preserves total probability at every layer",
            "all six H6 sectors receive recurrent flow, with V+ carrying the largest sector mass",
            "221 of 233 relation-signature classes receive recurrent flow from the active atom support",
            "the atom-flow Poincare center matches the core stationary center up to the declared integer split tolerance",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_stationary_atom_flow_lift@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The stationary measure of the certified d20 boundary transfer operator "
            "lifts through the 12 core normal words to a 20-atom Poincare-boundary "
            "flow, identifying the recurrent atoms, sectors, and relation-signature "
            "classes carried by the hyperbolic transfer dynamics."
        ),
        "stage_protocol": {
            "draft": "push stationary core mass through each normal word's three canonical atom slots",
            "witness": "materialize node-atom contributions, atom flow, sector flow, and signature-class flow tables",
            "coherence": "check exact mass conservation, active supports, top carriers, signature coverage, and Poincare-center compatibility",
            "closure": "certify the stationary atom-flow lift from the core transfer operator",
            "emit": "emit atom-flow JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "rewrite_complex_report": input_entry(
                REWRITE_COMPLEX_REPORT,
                {
                    "status": rewrite_report.get("status"),
                    "certificate_sha256": rewrite_report.get("certificate_sha256"),
                },
            ),
            "rewrite_complex": input_entry(REWRITE_COMPLEX_JSON),
            "rewrite_complex_certificate": input_entry(REWRITE_COMPLEX_CERTIFICATE),
            "boundary_atlas_report": input_entry(
                ATLAS_REPORT,
                {
                    "status": atlas_report.get("status"),
                    "certificate_sha256": atlas_report.get("certificate_sha256"),
                },
            ),
            "boundary_atlas": input_entry(ATLAS_JSON),
            "boundary_atlas_tables": input_entry(ATLAS_TABLES),
            "boundary_atlas_certificate": input_entry(ATLAS_CERTIFICATE),
            "poincare_report": input_entry(
                POINCARE_REPORT,
                {
                    "status": poincare_report.get("status"),
                    "certificate_sha256": poincare_report.get("certificate_sha256"),
                },
            ),
            "poincare_embedding": input_entry(POINCARE_JSON),
            "poincare_tables": input_entry(POINCARE_TABLES),
            "poincare_certificate": input_entry(POINCARE_CERTIFICATE),
            "symbolic_report": input_entry(
                SYMBOLIC_REPORT,
                {
                    "status": symbolic_report.get("status"),
                    "certificate_sha256": symbolic_report.get("certificate_sha256"),
                },
            ),
            "symbolic_alphabet": input_entry(SYMBOLIC_JSON),
            "symbolic_tables": input_entry(SYMBOLIC_TABLES),
            "symbolic_certificate": input_entry(SYMBOLIC_CERTIFICATE),
            "boundary_transfer_report": input_entry(
                BOUNDARY_TRANSFER_REPORT,
                {
                    "status": transfer_report.get("status"),
                    "certificate_sha256": transfer_report.get("certificate_sha256"),
                },
            ),
            "boundary_transfer": input_entry(BOUNDARY_TRANSFER_JSON),
            "boundary_transfer_tables": input_entry(BOUNDARY_TRANSFER_TABLES),
            "boundary_transfer_certificate": input_entry(BOUNDARY_TRANSFER_CERTIFICATE),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "stationary_atom_flow_lift": relpath(OUT_DIR / "stationary_atom_flow_lift.json"),
            "node_atom_contributions_csv": relpath(OUT_DIR / "node_atom_contributions.csv"),
            "atom_flow_csv": relpath(OUT_DIR / "atom_flow.csv"),
            "sector_flow_csv": relpath(OUT_DIR / "sector_flow.csv"),
            "signature_flow_csv": relpath(OUT_DIR / "signature_flow.csv"),
            "atom_flow_observables_csv": relpath(OUT_DIR / "atom_flow_observables.csv"),
            "stationary_atom_flow_tables": relpath(OUT_DIR / "stationary_atom_flow_tables.npz"),
            "stationary_atom_flow_certificate": relpath(
                OUT_DIR / "stationary_atom_flow_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the exact atom-slot lift of the 12-node stationary transfer measure",
                "which six d20 atoms carry recurrent flow and their mass ordering",
                "sector-level recurrent flow across all six H6 sectors",
                "relation-signature flow support over 221 of 233 signature classes",
                "Poincare-center compatibility between the core stationary measure and atom-flow lift",
            ],
            "does_not_certify_because_not_required": [
                "nonzero recurrent flow on all 20 d20 atoms",
                "a canonical physical probability law beyond the declared slot-splitting lift",
                "a continuum boundary measure",
                "signature-class transition dynamics between individual relations",
                "new C985 associator or pentagon data beyond the existing certificate",
            ],
        },
        "next_highest_yield_item": (
            "Turn the 221 active signature classes into a recurrent signature "
            "subboundary: build the induced signature-intersection graph, compare "
            "its hyperbolicity with the 20-atom Johnson boundary, and locate the "
            "12 signature classes excluded by the transfer flow."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_stationary_atom_flow_lift_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified rewrite-complex, atlas, Poincare, symbolic, and boundary-transfer artifacts",
            "split stationary core mass through canonical normal-word atom slots",
            "aggregate atom, sector, and signature-class recurrent flow tables",
            "check exact mass conservation and active-support invariants at every layer",
            "check Poincare-center compatibility with the core transfer stationary measure",
            "check source hashes and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "stationary_atom_flow_lift": atom_flow_lift,
        "node_atom_contributions_csv": csv_text(
            NODE_ATOM_CONTRIBUTION_COLUMNS,
            contribution_rows,
        ),
        "atom_flow_csv": csv_text(ATOM_FLOW_COLUMNS, atom_rows),
        "sector_flow_csv": csv_text(SECTOR_FLOW_COLUMNS, sector_rows),
        "signature_flow_csv": csv_text(SIGNATURE_FLOW_COLUMNS, signature_rows),
        "atom_flow_observables_csv": csv_text(
            ATOM_FLOW_OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "node_atom_contribution_table": contribution_table,
        "atom_flow_table": atom_table,
        "sector_flow_table": sector_table,
        "signature_flow_table": signature_table,
        "atom_signature_membership": atom_signature_membership,
        "atom_flow_observable_table": observable_table,
        "stationary_atom_flow_certificate": certificate,
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
    write_json(OUT_DIR / "stationary_atom_flow_lift.json", payloads["stationary_atom_flow_lift"])
    (OUT_DIR / "node_atom_contributions.csv").write_text(
        payloads["node_atom_contributions_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "atom_flow.csv").write_text(payloads["atom_flow_csv"], encoding="utf-8")
    (OUT_DIR / "sector_flow.csv").write_text(payloads["sector_flow_csv"], encoding="utf-8")
    (OUT_DIR / "signature_flow.csv").write_text(
        payloads["signature_flow_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "atom_flow_observables.csv").write_text(
        payloads["atom_flow_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "stationary_atom_flow_tables.npz",
        node_atom_contribution_table=payloads["node_atom_contribution_table"],
        atom_flow_table=payloads["atom_flow_table"],
        sector_flow_table=payloads["sector_flow_table"],
        signature_flow_table=payloads["signature_flow_table"],
        atom_signature_membership=payloads["atom_signature_membership"],
        atom_flow_observable_table=payloads["atom_flow_observable_table"],
    )
    write_json(
        OUT_DIR / "stationary_atom_flow_certificate.json",
        payloads["stationary_atom_flow_certificate"],
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
                "active_atom_ids": witness["active_atom_ids"],
                "active_signature_class_count": witness["active_signature_class_count"],
                "inactive_signature_class_count": witness["inactive_signature_class_count"],
                "top_atom_ids": witness["top_atom_ids"],
                "top_sector_labels": witness["top_sector_labels"],
                "next_highest_yield_item": payloads["report"]["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
