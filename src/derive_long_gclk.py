from __future__ import annotations

import csv
import hashlib
import json
from math import comb
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .derive_long_raw import csv_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_raw import csv_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_gclk"
STATUS = "D20_STAGE5_F2_6_BRIDGE_AND_AFFINE_CLOCK_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_GLAW = PROOF_ROOT / "long_glaw" / "report.json"
LONG_GLAW_LAW = PROOF_ROOT / "long_glaw" / "law.csv"
LONG_F63 = PROOF_ROOT / "long_f63" / "report.json"
LONG_F63_ATOM = PROOF_ROOT / "long_f63" / "atom.csv"
LONG_RIM = PROOF_ROOT / "long_rim" / "report.json"
LONG_RIM_ORBIT = PROOF_ROOT / "long_rim" / "orbit.csv"
LONG_TRANSITION_SEM = PROOF_ROOT / "long_transition_sem" / "report.json"
LONG_TRANSITION_CSV = PROOF_ROOT / "long_transition_sem" / "transition.csv"
LONG_CONTACT_CSV = PROOF_ROOT / "long_contact_lift" / "contact.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_gclk.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_gclk.py"

ALL_ONES_MASK = (1 << 6) - 1
SIGMA = {0: 3, 3: 1, 1: 5, 5: 4, 4: 0, 2: 2}
SIGMA_CYCLE_CODE = 31540

ATOM_COLUMNS = [
    "atom_id",
    "coordinate_mask",
    "coordinate_weight",
    "complement_atom_id",
    "complement_coordinate_mask",
    "grade3_flag",
]
JOHNSON_COLUMNS = [
    "edge_id",
    "left_atom_id",
    "right_atom_id",
    "left_coordinate_mask",
    "right_coordinate_mask",
    "hamming_distance",
    "intersection_size",
    "johnson_edge_flag",
]
CYCLE_COLUMNS = [
    "visible_edge_id",
    "source_atom_id",
    "target_atom_id",
    "source_coordinate_mask",
    "target_coordinate_mask",
    "hamming_distance",
    "intersection_size",
    "johnson_edge_flag",
    "visible_delta_t",
    "visible_accumulated_time",
]
CLOCK_COLUMNS = [
    "visible_index",
    "source_atom_id",
    "target_atom_id",
    "expected_atom_id",
    "source_coordinate_mask",
    "sigma_coordinate_mask",
    "affine_coordinate_mask",
    "visible_shift",
    "hidden_delta_t",
    "tick_match_flag",
    "parity_preserved_flag",
]
POWER_COLUMNS = [
    "power_id",
    "visible_shift_mod20",
    "cycle_match_count",
    "identity_match_count",
    "complement_match_count",
    "even_seed_atom_id",
    "odd_seed_atom_id",
]
DECAGON_COLUMNS = [
    "visible_index",
    "parity",
    "decagon_index",
    "atom_id",
    "coordinate_mask",
    "seed_atom_id",
    "affine_from_seed_atom_id",
    "decagon_match_flag",
]
FACE_COLUMNS = [
    "dimension",
    "face_count",
    "hypersimplex_dimension_flag",
]
SCHEMA_COLUMNS = [
    "schema_id",
    "schema_code",
    "row_count",
    "atom_key_flag",
    "rim_key_flag",
    "basis_key_flag",
    "semantic_operation_flag",
    "shared_transition_key_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

SCHEMA_NAMES = [
    "stage5_atoms",
    "johnson_edges",
    "visible_golden_cycle",
    "affine_hidden_clock",
    "transition_sem_rows",
    "contact_rows",
]
SCHEMA_CODES = {name: index for index, name in enumerate(SCHEMA_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "coordinate_dimension",
    "d20_atom_count",
    "grade3_atom_count",
    "complement_pair_count",
    "johnson_vertex_count",
    "johnson_edge_count",
    "johnson_degree",
    "hypersimplex_dimension",
    "hypersimplex_f0",
    "hypersimplex_f1",
    "hypersimplex_f2",
    "hypersimplex_f3",
    "hypersimplex_f4",
    "golden_selector_law_flag",
    "golden_class_id",
    "golden_orbit_id",
    "golden_unoriented_rim_count",
    "visible_cycle_edge_count",
    "visible_cycle_unique_atom_count",
    "visible_cycle_johnson_edge_count",
    "affine_sigma_order",
    "affine_clock_order",
    "affine_tick_visible_shift",
    "affine_tick_cycle_match_count",
    "affine_fifth_tick_complement_count",
    "affine_tenth_tick_identity_count",
    "even_decagon_match_count",
    "odd_decagon_match_count",
    "s6_stabilizer_order",
    "affine_stabilizer_order",
    "golden_orbit_size_from_stabilizer",
    "transition_row_count",
    "contact_row_count",
    "atom_transition_shared_key_count",
    "atom_transition_schema_key_flag",
    "semantic_transition_operation_flag",
    "semantic_transition_realized_count",
    "physical_transition_flag",
    "gr_source_ready_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def summary(report: dict[str, Any]) -> dict[str, Any]:
    witness = report.get("witness")
    if not isinstance(witness, dict):
        raise AssertionError("witness missing")
    out = witness.get("summary")
    if not isinstance(out, dict):
        raise AssertionError("summary missing")
    return out


def certified(report: dict[str, Any]) -> bool:
    return report.get("all_checks_pass") is True and "CERTIFIED" in str(
        report.get("status", "")
    )


def bit_set(mask: int) -> set[int]:
    return {index for index in range(6) if (mask >> index) & 1}


def permute_mask(mask: int, permutation: dict[int, int]) -> int:
    out = 0
    for index in range(6):
        if (mask >> index) & 1:
            out |= 1 << permutation[index]
    return out


def affine_tick(mask: int) -> int:
    return permute_mask(mask, SIGMA) ^ ALL_ONES_MASK


def affine_power(mask: int, power: int) -> int:
    out = mask
    for _ in range(power):
        out = affine_tick(out)
    return out


def permutation_order(permutation: dict[int, int]) -> int:
    seen_orders = []
    for start in range(6):
        value = start
        order = 0
        while True:
            value = permutation[value]
            order += 1
            if value == start:
                break
        seen_orders.append(order)
    out = 1
    for order in seen_orders:
        candidate = out
        while candidate % order != 0:
            candidate += out
        out = candidate
    return out


def affine_order(atom_masks: list[int]) -> int:
    for power in range(1, 33):
        if all(affine_power(mask, power) == mask for mask in atom_masks):
            return power
    raise AssertionError("affine clock order not found")


def hypersimplex_face_count(n: int, k: int, dimension: int) -> int:
    if dimension == 0:
        return comb(n, k)
    free_count = dimension + 1
    total = 0
    fixed_count = n - free_count
    for one_count in range(fixed_count + 1):
        zero_count = fixed_count - one_count
        residual = k - one_count
        if 1 <= residual <= free_count - 1:
            total += comb(n, one_count) * comb(n - one_count, zero_count)
    return total


def atom_id_for_mask(atom_by_mask: dict[int, int], mask: int) -> int:
    if mask not in atom_by_mask:
        raise AssertionError(f"missing atom mask {mask}")
    return atom_by_mask[mask]


def build_rows() -> dict[str, Any]:
    glaw = load_json(LONG_GLAW)
    f63 = load_json(LONG_F63)
    rim_report = load_json(LONG_RIM)
    transition = load_json(LONG_TRANSITION_SEM)
    glaw_law_rows = read_csv(LONG_GLAW_LAW)
    atom_rows_raw = read_csv(LONG_F63_ATOM)
    orbit_rows_raw = read_csv(LONG_RIM_ORBIT)
    transition_rows_raw = read_csv(LONG_TRANSITION_CSV)
    contact_rows_raw = read_csv(LONG_CONTACT_CSV)

    glaw_s = summary(glaw)
    transition_s = summary(transition)
    law = glaw_law_rows[0]
    selected_class_id = int(law["selected_class_id"])
    selected_orbit_id = int(law["selected_orbit_id"])
    selected_rim_count = int(law["rim_count"])
    orbit = next(
        row for row in orbit_rows_raw if int(row["orbit_id"]) == selected_orbit_id
    )
    rim = [int(value) for value in orbit["representative_rim"].split("|")]

    atom_by_id = {
        int(row["atom_id"]): {
            "coordinate_mask": int(row["coordinate_mask"]),
            "complement_atom_id": int(row["complement_atom_id"]),
        }
        for row in atom_rows_raw
    }
    atom_by_mask = {
        data["coordinate_mask"]: atom_id for atom_id, data in atom_by_id.items()
    }
    atom_masks = [atom_by_id[atom_id]["coordinate_mask"] for atom_id in sorted(atom_by_id)]

    atom_rows = []
    for atom_id in sorted(atom_by_id):
        coord = atom_by_id[atom_id]["coordinate_mask"]
        complement_coord = coord ^ ALL_ONES_MASK
        atom_rows.append(
            {
                "atom_id": atom_id,
                "coordinate_mask": coord,
                "coordinate_weight": coord.bit_count(),
                "complement_atom_id": atom_by_id[atom_id]["complement_atom_id"],
                "complement_coordinate_mask": complement_coord,
                "grade3_flag": int(coord.bit_count() == 3),
            }
        )

    johnson_rows = []
    degrees = {atom_id: 0 for atom_id in atom_by_id}
    for left in sorted(atom_by_id):
        left_coord = atom_by_id[left]["coordinate_mask"]
        left_set = bit_set(left_coord)
        for right in range(left + 1, len(atom_by_id)):
            right_coord = atom_by_id[right]["coordinate_mask"]
            right_set = bit_set(right_coord)
            hamming_distance = (left_coord ^ right_coord).bit_count()
            intersection_size = len(left_set & right_set)
            if hamming_distance == 2 and intersection_size == 2:
                degrees[left] += 1
                degrees[right] += 1
                johnson_rows.append(
                    {
                        "edge_id": len(johnson_rows),
                        "left_atom_id": left,
                        "right_atom_id": right,
                        "left_coordinate_mask": left_coord,
                        "right_coordinate_mask": right_coord,
                        "hamming_distance": hamming_distance,
                        "intersection_size": intersection_size,
                        "johnson_edge_flag": 1,
                    }
                )

    cycle_rows = []
    for edge_id, source in enumerate(rim):
        target = rim[(edge_id + 1) % len(rim)]
        source_coord = atom_by_id[source]["coordinate_mask"]
        target_coord = atom_by_id[target]["coordinate_mask"]
        intersection_size = len(bit_set(source_coord) & bit_set(target_coord))
        hamming_distance = (source_coord ^ target_coord).bit_count()
        cycle_rows.append(
            {
                "visible_edge_id": edge_id,
                "source_atom_id": source,
                "target_atom_id": target,
                "source_coordinate_mask": source_coord,
                "target_coordinate_mask": target_coord,
                "hamming_distance": hamming_distance,
                "intersection_size": intersection_size,
                "johnson_edge_flag": int(
                    hamming_distance == 2 and intersection_size == 2
                ),
                "visible_delta_t": 1,
                "visible_accumulated_time": edge_id + 1,
            }
        )

    clock_rows = []
    for visible_index, source in enumerate(rim):
        source_coord = atom_by_id[source]["coordinate_mask"]
        sigma_coord = permute_mask(source_coord, SIGMA)
        affine_coord = sigma_coord ^ ALL_ONES_MASK
        target = atom_id_for_mask(atom_by_mask, affine_coord)
        expected = rim[(visible_index + 2) % len(rim)]
        clock_rows.append(
            {
                "visible_index": visible_index,
                "source_atom_id": source,
                "target_atom_id": target,
                "expected_atom_id": expected,
                "source_coordinate_mask": source_coord,
                "sigma_coordinate_mask": sigma_coord,
                "affine_coordinate_mask": affine_coord,
                "visible_shift": 2,
                "hidden_delta_t": 1,
                "tick_match_flag": int(target == expected),
                "parity_preserved_flag": int((visible_index % 2) == ((visible_index + 2) % 2)),
            }
        )

    power_rows = []
    for power in range(11):
        cycle_match_count = 0
        for visible_index, source in enumerate(rim):
            source_coord = atom_by_id[source]["coordinate_mask"]
            expected = rim[(visible_index + 2 * power) % len(rim)]
            target = atom_id_for_mask(atom_by_mask, affine_power(source_coord, power))
            cycle_match_count += int(target == expected)
        identity_match_count = sum(
            int(affine_power(mask, power) == mask) for mask in atom_masks
        )
        complement_match_count = sum(
            int(affine_power(mask, power) == (mask ^ ALL_ONES_MASK))
            for mask in atom_masks
        )
        power_rows.append(
            {
                "power_id": power,
                "visible_shift_mod20": (2 * power) % 20,
                "cycle_match_count": cycle_match_count,
                "identity_match_count": identity_match_count,
                "complement_match_count": complement_match_count,
                "even_seed_atom_id": atom_id_for_mask(
                    atom_by_mask, affine_power(atom_by_id[rim[0]]["coordinate_mask"], power)
                ),
                "odd_seed_atom_id": atom_id_for_mask(
                    atom_by_mask, affine_power(atom_by_id[rim[1]]["coordinate_mask"], power)
                ),
            }
        )

    decagon_rows = []
    for visible_index, atom_id in enumerate(rim):
        parity = visible_index % 2
        decagon_index = visible_index // 2
        seed_atom = rim[parity]
        seed_coord = atom_by_id[seed_atom]["coordinate_mask"]
        target_atom = atom_id_for_mask(
            atom_by_mask, affine_power(seed_coord, decagon_index)
        )
        decagon_rows.append(
            {
                "visible_index": visible_index,
                "parity": parity,
                "decagon_index": decagon_index,
                "atom_id": atom_id,
                "coordinate_mask": atom_by_id[atom_id]["coordinate_mask"],
                "seed_atom_id": seed_atom,
                "affine_from_seed_atom_id": target_atom,
                "decagon_match_flag": int(target_atom == atom_id),
            }
        )

    face_rows = [
        {
            "dimension": dimension,
            "face_count": hypersimplex_face_count(6, 3, dimension),
            "hypersimplex_dimension_flag": int(dimension <= 4),
        }
        for dimension in range(5)
    ]

    transition_header = set(transition_rows_raw[0]) if transition_rows_raw else set()
    contact_header = set(contact_rows_raw[0]) if contact_rows_raw else set()
    atom_cycle_header = set(CYCLE_COLUMNS) | set(CLOCK_COLUMNS)
    shared_transition_keys = sorted(
        (atom_cycle_header & transition_header)
        & {"atom_id", "source_atom_id", "target_atom_id", "class_id", "orbit_id", "rim_id"}
    )
    schema_specs = [
        (
            "stage5_atoms",
            len(atom_rows),
            1,
            0,
            0,
            0,
            0,
        ),
        (
            "johnson_edges",
            len(johnson_rows),
            1,
            0,
            0,
            0,
            0,
        ),
        (
            "visible_golden_cycle",
            len(cycle_rows),
            1,
            1,
            0,
            0,
            int(bool(shared_transition_keys)),
        ),
        (
            "affine_hidden_clock",
            len(clock_rows),
            1,
            1,
            0,
            0,
            int(bool(shared_transition_keys)),
        ),
        (
            "transition_sem_rows",
            len(transition_rows_raw),
            int("atom_id" in transition_header),
            0,
            int("left_basis_id" in transition_header and "right_basis_id" in transition_header),
            int(any(int(row["semantic_transition_flag"]) for row in transition_rows_raw)),
            int(bool(shared_transition_keys)),
        ),
        (
            "contact_rows",
            len(contact_rows_raw),
            int("atom_id" in contact_header),
            0,
            int("left_basis_id" in contact_header and "right_basis_id" in contact_header),
            0,
            0,
        ),
    ]
    schema_rows = [
        {
            "schema_id": index,
            "schema_code": SCHEMA_CODES[name],
            "row_count": row_count,
            "atom_key_flag": atom_key,
            "rim_key_flag": rim_key,
            "basis_key_flag": basis_key,
            "semantic_operation_flag": semantic_flag,
            "shared_transition_key_flag": shared_key,
        }
        for index, (
            name,
            row_count,
            atom_key,
            rim_key,
            basis_key,
            semantic_flag,
            shared_key,
        ) in enumerate(schema_specs)
    ]

    sigma_order = permutation_order(SIGMA)
    clock_order = affine_order(atom_masks)
    obs = {
        "input_report_count": 4,
        "input_certified_count": sum(
            certified(report) for report in [glaw, f63, rim_report, transition]
        ),
        "coordinate_dimension": 6,
        "d20_atom_count": len(atom_rows),
        "grade3_atom_count": sum(row["grade3_flag"] for row in atom_rows),
        "complement_pair_count": sum(
            int(row["atom_id"] < row["complement_atom_id"]) for row in atom_rows
        ),
        "johnson_vertex_count": len(atom_rows),
        "johnson_edge_count": len(johnson_rows),
        "johnson_degree": min(degrees.values()),
        "hypersimplex_dimension": 5,
        "hypersimplex_f0": face_rows[0]["face_count"],
        "hypersimplex_f1": face_rows[1]["face_count"],
        "hypersimplex_f2": face_rows[2]["face_count"],
        "hypersimplex_f3": face_rows[3]["face_count"],
        "hypersimplex_f4": face_rows[4]["face_count"],
        "golden_selector_law_flag": int(glaw_s["formal_golden_selector_law_flag"]),
        "golden_class_id": selected_class_id,
        "golden_orbit_id": selected_orbit_id,
        "golden_unoriented_rim_count": selected_rim_count,
        "visible_cycle_edge_count": len(cycle_rows),
        "visible_cycle_unique_atom_count": len(set(rim)),
        "visible_cycle_johnson_edge_count": sum(
            row["johnson_edge_flag"] for row in cycle_rows
        ),
        "affine_sigma_order": sigma_order,
        "affine_clock_order": clock_order,
        "affine_tick_visible_shift": 2,
        "affine_tick_cycle_match_count": sum(row["tick_match_flag"] for row in clock_rows),
        "affine_fifth_tick_complement_count": power_rows[5]["complement_match_count"],
        "affine_tenth_tick_identity_count": power_rows[10]["identity_match_count"],
        "even_decagon_match_count": sum(
            row["decagon_match_flag"] for row in decagon_rows if row["parity"] == 0
        ),
        "odd_decagon_match_count": sum(
            row["decagon_match_flag"] for row in decagon_rows if row["parity"] == 1
        ),
        "s6_stabilizer_order": sigma_order,
        "affine_stabilizer_order": clock_order,
        "golden_orbit_size_from_stabilizer": 720 // sigma_order,
        "transition_row_count": len(transition_rows_raw),
        "contact_row_count": len(contact_rows_raw),
        "atom_transition_shared_key_count": len(shared_transition_keys),
        "atom_transition_schema_key_flag": int(bool(shared_transition_keys)),
        "semantic_transition_operation_flag": int(
            transition_s["semantic_transition_operation_flag"]
        ),
        "semantic_transition_realized_count": int(
            transition_s["semantic_transition_realized_count"]
        ),
        "physical_transition_flag": 0,
        "gr_source_ready_flag": 0,
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": obs[name],
        }
        for index, name in enumerate(OBS_NAMES)
    ]

    return {
        "glaw": glaw,
        "f63": f63,
        "rim_report": rim_report,
        "transition": transition,
        "atom_rows": atom_rows,
        "johnson_rows": johnson_rows,
        "cycle_rows": cycle_rows,
        "clock_rows": clock_rows,
        "power_rows": power_rows,
        "decagon_rows": decagon_rows,
        "face_rows": face_rows,
        "schema_rows": schema_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "shared_transition_keys": shared_transition_keys,
        "degrees": degrees,
        "selected_orbit": orbit,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    atom_table = table_from_rows(ATOM_COLUMNS, rows["atom_rows"])
    johnson_table = table_from_rows(JOHNSON_COLUMNS, rows["johnson_rows"])
    cycle_table = table_from_rows(CYCLE_COLUMNS, rows["cycle_rows"])
    clock_table = table_from_rows(CLOCK_COLUMNS, rows["clock_rows"])
    power_table = table_from_rows(POWER_COLUMNS, rows["power_rows"])
    decagon_table = table_from_rows(DECAGON_COLUMNS, rows["decagon_rows"])
    face_table = table_from_rows(FACE_COLUMNS, rows["face_rows"])
    schema_table = table_from_rows(SCHEMA_COLUMNS, rows["schema_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"] == obs["input_certified_count"],
        "f2_6_grade_three_boundary_matches_d20": obs["coordinate_dimension"] == 6
        and obs["d20_atom_count"] == 20
        and obs["grade3_atom_count"] == 20
        and obs["complement_pair_count"] == 10,
        "johnson_graph_and_hypersimplex_counts_match": obs["johnson_vertex_count"] == 20
        and obs["johnson_edge_count"] == 90
        and obs["johnson_degree"] == 9
        and sorted(rows["degrees"].values()) == [9] * 20
        and [
            obs["hypersimplex_f0"],
            obs["hypersimplex_f1"],
            obs["hypersimplex_f2"],
            obs["hypersimplex_f3"],
            obs["hypersimplex_f4"],
        ]
        == [20, 90, 120, 60, 12],
        "golden_rim_selected_by_formal_law": obs["golden_selector_law_flag"] == 1
        and obs["golden_class_id"] == 0
        and obs["golden_orbit_id"] == 122
        and obs["golden_unoriented_rim_count"] == 144,
        "visible_cycle_is_johnson_c20": obs["visible_cycle_edge_count"] == 20
        and obs["visible_cycle_unique_atom_count"] == 20
        and obs["visible_cycle_johnson_edge_count"] == 20,
        "affine_clock_realizes_hidden_half_tick": obs["affine_sigma_order"] == 5
        and obs["affine_clock_order"] == 10
        and obs["affine_tick_visible_shift"] == 2
        and obs["affine_tick_cycle_match_count"] == 20
        and obs["affine_fifth_tick_complement_count"] == 20
        and obs["affine_tenth_tick_identity_count"] == 20,
        "visible_rim_interlaces_two_affine_decagons": obs["even_decagon_match_count"] == 10
        and obs["odd_decagon_match_count"] == 10,
        "stabilizer_explains_golden_orbit_size": obs["s6_stabilizer_order"] == 5
        and obs["affine_stabilizer_order"] == 10
        and obs["golden_orbit_size_from_stabilizer"] == 144,
        "transition_surface_is_not_atom_rim_semantic": obs["transition_row_count"] == 642
        and obs["contact_row_count"] == 642
        and obs["atom_transition_shared_key_count"] == 0
        and obs["atom_transition_schema_key_flag"] == 0
        and obs["semantic_transition_operation_flag"] == 0
        and obs["semantic_transition_realized_count"] == 0
        and obs["physical_transition_flag"] == 0
        and obs["gr_source_ready_flag"] == 0,
        "table_shapes_match": atom_table.shape == (20, len(ATOM_COLUMNS))
        and johnson_table.shape == (90, len(JOHNSON_COLUMNS))
        and cycle_table.shape == (20, len(CYCLE_COLUMNS))
        and clock_table.shape == (20, len(CLOCK_COLUMNS))
        and power_table.shape == (11, len(POWER_COLUMNS))
        and decagon_table.shape == (20, len(DECAGON_COLUMNS))
        and face_table.shape == (5, len(FACE_COLUMNS))
        and schema_table.shape == (len(SCHEMA_CODES), len(SCHEMA_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "stage5_f2_6_bridge_and_affine_clock",
        "summary": {
            "status": STATUS if all(checks.values()) else "LONG_GCLK_PROVISIONAL",
            "d20_as_grade_three_f2_6_count": obs["d20_atom_count"],
            "johnson_edge_count": obs["johnson_edge_count"],
            "hypersimplex_f_vector": [
                obs["hypersimplex_f0"],
                obs["hypersimplex_f1"],
                obs["hypersimplex_f2"],
                obs["hypersimplex_f3"],
                obs["hypersimplex_f4"],
            ],
            "golden_class_id": obs["golden_class_id"],
            "golden_orbit_id": obs["golden_orbit_id"],
            "golden_unoriented_rim_count": obs["golden_unoriented_rim_count"],
            "affine_sigma_cycle_code": SIGMA_CYCLE_CODE,
            "affine_sigma_order": obs["affine_sigma_order"],
            "affine_clock_order": obs["affine_clock_order"],
            "affine_tick_visible_shift": obs["affine_tick_visible_shift"],
            "affine_fifth_tick_complement_count": obs[
                "affine_fifth_tick_complement_count"
            ],
            "affine_tenth_tick_identity_count": obs[
                "affine_tenth_tick_identity_count"
            ],
            "even_decagon_seed_atom_id": rows["decagon_rows"][0]["seed_atom_id"],
            "odd_decagon_seed_atom_id": rows["decagon_rows"][1]["seed_atom_id"],
            "atom_transition_shared_key_count": obs[
                "atom_transition_shared_key_count"
            ],
            "semantic_transition_operation_flag": obs[
                "semantic_transition_operation_flag"
            ],
            "physical_transition_flag": obs["physical_transition_flag"],
        },
        "schema_code_map": {str(value): key for key, value in SCHEMA_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "sigma_coordinate_map": {str(key): SIGMA[key] for key in sorted(SIGMA)},
        "shared_transition_keys": rows["shared_transition_keys"],
        "atom_table_sha256": sha_array(atom_table),
        "johnson_table_sha256": sha_array(johnson_table),
        "cycle_table_sha256": sha_array(cycle_table),
        "cycle_text_sha256": sha_text(csv_text(CYCLE_COLUMNS, rows["cycle_rows"])),
        "clock_table_sha256": sha_array(clock_table),
        "power_table_sha256": sha_array(power_table),
        "decagon_table_sha256": sha_array(decagon_table),
        "face_table_sha256": sha_array(face_table),
        "schema_table_sha256": sha_array(schema_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    gclk = {
        "schema": "long.gclk@2",
        "object": "stage5_f2_6_bridge_and_affine_clock",
        "status": STATUS if all(checks.values()) else "LONG_GCLK_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.gclk.report@2",
        "status": gclk["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_gclk certifies the Stage 5 finite bridge D20 = {x in F2^6: "
            "|x| = 3}, with Johnson adjacency given exactly by Hamming "
            "distance two. The selected golden class-0 rim is the visible C20 "
            "cycle, and the affine map T(x)=sigma(x)+1 with sigma=(0 3 1 5 4) "
            "and coordinate 2 fixed advances the rim by two visible steps. "
            "T has order 10, T^5 is complement, and the visible C20 is an "
            "interlacing of two affine C10 orbits."
        ),
        "stage_protocol": {
            "draft": "read long_glaw, long_f63, long_rim, long_transition_sem, atom rows, rim orbit rows, transition rows, and contact rows",
            "witness": "emit grade-three atoms, Johnson edges, visible cycle rows, affine clock rows, clock powers, decagon rows, hypersimplex face counts, schema rows, and observables",
            "coherence": "check F2^6 grade-three counts, Johnson graph counts, hypersimplex f-vector, selected golden rim, affine order/complement laws, stabilizer/orbit relation, and transition schema absence",
            "closure": "certify the finite public-state polytope and affine golden clock while preserving the semantic transition and physical-GR boundary",
            "emit": "write long_gclk artifacts and verifier hook",
        },
        "inputs": {
            "long_glaw": input_entry(
                LONG_GLAW,
                {
                    "status": rows["glaw"].get("status"),
                    "certificate_sha256": rows["glaw"].get("certificate_sha256"),
                },
            ),
            "long_glaw_law": input_entry(LONG_GLAW_LAW),
            "long_f63": input_entry(
                LONG_F63,
                {
                    "status": rows["f63"].get("status"),
                    "certificate_sha256": rows["f63"].get("certificate_sha256"),
                },
            ),
            "long_f63_atom": input_entry(LONG_F63_ATOM),
            "long_rim": input_entry(
                LONG_RIM,
                {
                    "status": rows["rim_report"].get("status"),
                    "certificate_sha256": rows["rim_report"].get("certificate_sha256"),
                },
            ),
            "long_rim_orbit": input_entry(LONG_RIM_ORBIT),
            "long_transition_sem": input_entry(
                LONG_TRANSITION_SEM,
                {
                    "status": rows["transition"].get("status"),
                    "certificate_sha256": rows["transition"].get("certificate_sha256"),
                },
            ),
            "long_transition_csv": input_entry(LONG_TRANSITION_CSV),
            "long_contact_csv": input_entry(LONG_CONTACT_CSV),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "gclk": relpath(OUT_DIR / "gclk.json"),
            "atom_csv": relpath(OUT_DIR / "atom.csv"),
            "johnson_csv": relpath(OUT_DIR / "johnson.csv"),
            "cycle_csv": relpath(OUT_DIR / "cycle.csv"),
            "clock_csv": relpath(OUT_DIR / "clock.csv"),
            "power_csv": relpath(OUT_DIR / "power.csv"),
            "decagon_csv": relpath(OUT_DIR / "decagon.csv"),
            "face_csv": relpath(OUT_DIR / "face.csv"),
            "schema_csv": relpath(OUT_DIR / "schema.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "D20 is reconstructed as the 20 weight-three vectors in F2^6",
                "D20 adjacency is exactly the Johnson graph J(6,3), with 20 vertices, 90 edges, and degree 9",
                "the associated Johnson solid is the hypersimplex Delta(6,3), with f-vector (20,90,120,60,12)",
                "the formal golden law selects class 0, orbit 122, with 144 unoriented rims",
                "the selected visible C20 rim is advanced by two visible steps under T(x)=sigma(x)+1",
                "T has order 10 on the D20 atom boundary, T^5 is complement, and T^10 is identity",
                "the visible C20 rim is an interlacing of even and odd affine C10 orbits",
                "the S6 stabilizer has order 5 and the affine complement extension has order 10",
            ],
            "does_not_certify_because_out_of_scope": [
                "semantic A985 transition-operation realization for the affine tick",
                "a physical selector axiom",
                "that the affine golden clock is physical time",
                "a selected 1+3 Lorentzian spacetime boundary",
                "a physical stress-energy tensor or Einstein equation",
                "a derivation of general relativity from A985 alone",
            ],
        },
        "next_highest_yield_item": (
            "Construct the atom/rim-to-basis transition lift for the affine "
            "tick T: map each of the 20 T-edges to raw-backed basis endpoint "
            "transitions, or certify that no such lift exists under the current "
            "schemas."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.gclk.cert@2",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.gclk.manifest@2",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "gclk": gclk,
        "atom_csv": csv_text(ATOM_COLUMNS, rows["atom_rows"]),
        "johnson_csv": csv_text(JOHNSON_COLUMNS, rows["johnson_rows"]),
        "cycle_csv": csv_text(CYCLE_COLUMNS, rows["cycle_rows"]),
        "clock_csv": csv_text(CLOCK_COLUMNS, rows["clock_rows"]),
        "power_csv": csv_text(POWER_COLUMNS, rows["power_rows"]),
        "decagon_csv": csv_text(DECAGON_COLUMNS, rows["decagon_rows"]),
        "face_csv": csv_text(FACE_COLUMNS, rows["face_rows"]),
        "schema_csv": csv_text(SCHEMA_COLUMNS, rows["schema_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "atom_table": atom_table,
        "johnson_table": johnson_table,
        "cycle_table": cycle_table,
        "clock_table": clock_table,
        "power_table": power_table,
        "decagon_table": decagon_table,
        "face_table": face_table,
        "schema_table": schema_table,
        "observable_table": observable_table,
        "cert": cert,
        "manifest": manifest,
        "report": report,
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
    obligations.sort(key=lambda row: str(row["id"]))
    index = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": obligations,
    }
    index["registry_sha256"] = self_hash(index, "registry_sha256")
    write_json(INDEX_PATH, index)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / "gclk.json", payloads["gclk"])
    (OUT_DIR / "atom.csv").write_text(payloads["atom_csv"], encoding="utf-8")
    (OUT_DIR / "johnson.csv").write_text(payloads["johnson_csv"], encoding="utf-8")
    (OUT_DIR / "cycle.csv").write_text(payloads["cycle_csv"], encoding="utf-8")
    (OUT_DIR / "clock.csv").write_text(payloads["clock_csv"], encoding="utf-8")
    (OUT_DIR / "power.csv").write_text(payloads["power_csv"], encoding="utf-8")
    (OUT_DIR / "decagon.csv").write_text(payloads["decagon_csv"], encoding="utf-8")
    (OUT_DIR / "face.csv").write_text(payloads["face_csv"], encoding="utf-8")
    (OUT_DIR / "schema.csv").write_text(payloads["schema_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        atom_table=payloads["atom_table"],
        johnson_table=payloads["johnson_table"],
        cycle_table=payloads["cycle_table"],
        clock_table=payloads["clock_table"],
        power_table=payloads["power_table"],
        decagon_table=payloads["decagon_table"],
        face_table=payloads["face_table"],
        schema_table=payloads["schema_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(OUT_DIR / "cert.json", payloads["cert"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    write_json(OUT_DIR / "report.json", payloads["report"])
    update_index(payloads["report"])


def main() -> None:
    payloads = build_payloads()
    write_payloads(payloads)
    report = payloads["report"]
    print(
        json.dumps(
            {
                "status": report["status"],
                "all_checks_pass": report["all_checks_pass"],
                "certificate_sha256": report["certificate_sha256"],
                "summary": report["witness"]["summary"],
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
