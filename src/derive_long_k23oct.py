from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import input_entry, load_json, self_hash, write_json
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_k23oct"
STATUS = "SECTOR33_K23_TYPED_W24_OCTAD_PLACEMENT_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_k23oct.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_k23oct.py"
D20_JSON = ROOT / "d20.json"
LONG_K23_REPORT = D20_INVARIANTS / "proof_obligations" / "long_k23" / "report.json"
W24_REPORT = D20_INVARIANTS / "proof_obligations" / "d20_w24_hexacode_row_alphabetization" / "report.json"
DELETE_CONTRACT_REPORT = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_sector33_w24_marked_delete_contract_shadow_probe"
    / "report.json"
)

PLACEMENT_TEXT_HASH = "c224af094ba30409a08786dc6e6acf7c7e9fb9f07711c76e1e58d5f9e133016d"
OCTAD_TEXT_HASH = "8fc42151e31d807d3092ac28784b881bc0c4dbd4dcc0802fb45351f6a26e151f"
OBS_TEXT_HASH = "fa60799f707093ab1d82d645f5415644b4c16d842841d2b0eba181487e2263bb"
MATRIX_SHA256 = "5e74d246a3165de08ffc2bfc1002e90fb782625a694e2f1330a994bc7e1e20ff"

H6_LABELS = ["B-", "B+", "V-", "V+", "S-", "S+"]
PAIR_FAMILY_CODES = {"shared_duad": 0, "swapped_pair": 1, "missing_pair": 2}
SELECTED_PAIR_FAMILY = "shared_duad"
TARGET_SUPPORT = [0, 3, 12, 13, 14, 16, 20, 24]
TARGET_COLUMN_VECTOR = [4, 0, 4, 0, 0, 0]

PLACEMENT_COLUMNS = [
    "row_id",
    "source_edge_id",
    "h6_column_id",
    "w24_coordinate",
    "mog_row",
    "f4_value",
    "support_flag",
    "target_octad_flag",
    "pair_family_code",
    "pair_choice_position",
    "compatible_record_id",
]
OCTAD_COLUMNS = [
    "octad_row_id",
    "source_edge_id",
    "w24_coordinate",
    "h6_column_id",
    "mog_row",
    "f4_value",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "long_k23_certified_flag",
    "w24_code_certified_flag",
    "delete_contract_input_certified_flag",
    "compatible_record_count",
    "nontrivial_compatible_record_count",
    "unique_nonzero_support_count",
    "selected_record_id",
    "selected_extra_removed",
    "selected_effective_contract_count",
    "remaining_column_count",
    "pair_family_code",
    "assignment_edge_count",
    "support_edge_count",
    "h6_balance_flag",
    "mapped_coordinate_count",
    "mapped_coordinate_bijection_flag",
    "target_octad_weight",
    "target_octad_in_w24_code_flag",
    "mapped_support_matches_target_octad_flag",
    "rowspace_equality_certified_flag",
    "full_morphism_certified_flag",
    "m23_module_proven_flag",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sha_array(array: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def matrix_payload_hash(payload: dict[str, np.ndarray]) -> str:
    return hashlib.sha256(
        b"".join(
            np.ascontiguousarray(payload[key]).tobytes()
            for key in ["placement_matrix", "target_octad_vector", "support_edge_vector"]
        )
    ).hexdigest()


def span_masks(gens: list[int]) -> set[int]:
    out = {0}
    for gen in gens:
        out |= {word ^ gen for word in list(out)}
    return out


def parse_pair(text: str) -> list[str]:
    return [part.strip() for part in text.strip("{}").split(",") if part.strip()]


def edge_pair_data(row: dict[str, Any], h6_labels: list[str]) -> dict[str, list[str]]:
    shared = parse_pair(str(row["shared_duad"]))
    swapped = parse_pair(str(row["swapped_pair"]))
    present = set(shared) | set(swapped)
    missing = [label for label in h6_labels if label not in present]
    if len(shared) != 2 or len(swapped) != 2 or len(missing) != 2:
        raise ValueError(f"edge {row['edge_id']} does not define three H6 pairs")
    return {
        "shared_duad": shared,
        "swapped_pair": swapped,
        "missing_pair": missing,
    }


def edge_table(d20: dict[str, Any]) -> list[dict[str, Any]]:
    rows = d20["game_theory"]["tables"]["subscript_Hcycle_d20_edges.csv"]["rows"]
    return sorted(rows, key=lambda row: int(row["edge_id"]))


def coordinate_profile(w24: dict[str, Any]) -> dict[int, dict[str, int]]:
    out: dict[int, dict[str, int]] = {}
    for row in w24["witness"]["row_alphabetization"]["coordinate_labels"]:
        coord = int(row["coordinate"])
        out[coord] = {
            "h6_column_id": int(row["mog_column"]),
            "mog_row": int(row["mog_row"]),
            "f4_value": int(row["row_f4_value"]),
        }
    return out


def columns_to_coordinates(profile: dict[int, dict[str, int]]) -> dict[int, list[int]]:
    by_column: dict[int, list[int]] = {index: [] for index in range(len(H6_LABELS))}
    for coord, row in profile.items():
        by_column[int(row["h6_column_id"])].append(coord)
    for coords in by_column.values():
        coords.sort(key=lambda coord: profile[coord]["mog_row"])
    return by_column


def selected_record(records: list[dict[str, Any]]) -> tuple[int, dict[str, Any]]:
    support_tuple = tuple(TARGET_SUPPORT)
    for record_id, record in enumerate(records):
        supports = [tuple(int(value) for value in support) for support in record.get("nonzero_shadow_supports", [])]
        if support_tuple in supports:
            return record_id, record
    raise AssertionError("no compatible record carries the target rank-one support")


def solve_assignment(
    edge_rows: list[dict[str, Any]],
    record: dict[str, Any],
) -> dict[int, int]:
    row_by_edge = {int(row["edge_id"]): row for row in edge_rows}
    label_to_id = {label: index for index, label in enumerate(H6_LABELS)}
    remaining = [int(edge_id) for edge_id in record["remaining_columns"]]
    support = list(TARGET_SUPPORT)
    assignment: dict[int, int] = {}
    counts = Counter({column: 0 for column in range(len(H6_LABELS))})

    support_options = {
        edge_id: [
            label_to_id[label]
            for label in edge_pair_data(row_by_edge[edge_id], H6_LABELS)[SELECTED_PAIR_FAMILY]
            if label_to_id[label] in (0, 2)
        ]
        for edge_id in support
    }
    target_support_need = Counter({column: TARGET_COLUMN_VECTOR[column] for column in range(len(H6_LABELS))})

    def support_rec(position: int) -> bool:
        if position == len(support):
            return all(target_support_need[column] == 0 for column in range(len(H6_LABELS)))
        edge_id = support[position]
        for column_id in support_options[edge_id]:
            if target_support_need[column_id] <= 0:
                continue
            target_support_need[column_id] -= 1
            assignment[edge_id] = column_id
            if support_rec(position + 1):
                return True
            target_support_need[column_id] += 1
            assignment.pop(edge_id, None)
        return False

    if not support_rec(0):
        raise AssertionError("support edges cannot be placed in the target octad columns")
    for column_id in assignment.values():
        counts[column_id] += 1
    if [counts[index] for index in range(len(H6_LABELS))] != TARGET_COLUMN_VECTOR:
        raise AssertionError("support assignment did not hit the target octad column vector")

    need = Counter({column: 4 - counts[column] for column in range(len(H6_LABELS))})
    non_support = [edge_id for edge_id in remaining if edge_id not in assignment]
    options = {
        edge_id: [
            label_to_id[label]
            for label in edge_pair_data(row_by_edge[edge_id], H6_LABELS)[SELECTED_PAIR_FAMILY]
        ]
        for edge_id in non_support
    }
    order = sorted(non_support, key=lambda edge_id: tuple(options[edge_id]))

    def rec(position: int) -> bool:
        if position == len(order):
            return all(need[column] == 0 for column in range(len(H6_LABELS)))
        edge_id = order[position]
        for column_id in options[edge_id]:
            if need[column_id] <= 0:
                continue
            need[column_id] -= 1
            assignment[edge_id] = column_id
            if rec(position + 1):
                return True
            need[column_id] += 1
            assignment.pop(edge_id, None)
        return False

    if not rec(0):
        raise AssertionError("could not extend target octad placement to H6-balanced 24-coordinate assignment")
    if sorted(assignment) != sorted(remaining):
        raise AssertionError("assignment does not cover the selected remaining columns")
    if [sum(1 for value in assignment.values() if value == column) for column in range(len(H6_LABELS))] != [4] * 6:
        raise AssertionError("assignment is not H6-balanced")
    return assignment


def coordinate_assignment(
    assignment: dict[int, int],
    profile: dict[int, dict[str, int]],
) -> tuple[dict[int, int], int]:
    by_column = columns_to_coordinates(profile)
    target_coords = {
        coord
        for coord, row in profile.items()
        if int(row["h6_column_id"]) in (0, 2)
    }
    coord_assignment: dict[int, int] = {}
    for column_id in range(len(H6_LABELS)):
        support_edges = [
            edge_id
            for edge_id, assigned_column in sorted(assignment.items())
            if assigned_column == column_id and edge_id in TARGET_SUPPORT
        ]
        other_edges = [
            edge_id
            for edge_id, assigned_column in sorted(assignment.items())
            if assigned_column == column_id and edge_id not in TARGET_SUPPORT
        ]
        support_coords = [coord for coord in by_column[column_id] if coord in target_coords]
        other_coords = [coord for coord in by_column[column_id] if coord not in target_coords]
        if len(support_edges) != len(support_coords):
            raise AssertionError("support coordinate count mismatch in selected column")
        if len(other_edges) != len(other_coords):
            raise AssertionError("non-support coordinate count mismatch in selected column")
        for edge_id, coord in zip(support_edges, support_coords):
            coord_assignment[edge_id] = coord
        for edge_id, coord in zip(other_edges, other_coords):
            coord_assignment[edge_id] = coord
    if len(set(coord_assignment.values())) != len(coord_assignment):
        raise AssertionError("coordinate assignment is not injective")
    target_mask = sum(1 << coord for coord in target_coords)
    return coord_assignment, target_mask


def build_rows() -> dict[str, Any]:
    d20 = load_json(D20_JSON)
    long_k23 = load_json(LONG_K23_REPORT)
    w24 = load_json(W24_REPORT)
    delete_contract = load_json(DELETE_CONTRACT_REPORT)
    edge_rows = edge_table(d20)
    profile = coordinate_profile(w24)
    target_span = span_masks([int(mask) for mask in w24["witness"]["golay_code"]["generator_basis_masks"]])
    records = delete_contract["witness"]["delete_contract_shadow_analysis"]["shadow_summaries"]["dual_rowspace_shadow"]["compatible_records"]
    nontrivial = [record for record in records if record.get("nonzero_shadow_supports")]
    unique_supports = {
        tuple(int(value) for value in support)
        for record in records
        for support in record.get("nonzero_shadow_supports", [])
    }
    record_id, record = selected_record(records)
    assignment = solve_assignment(edge_rows, record)
    coord_assignment, target_mask = coordinate_assignment(assignment, profile)

    placement_rows: list[dict[str, int]] = []
    row_by_edge = {int(row["edge_id"]): row for row in edge_rows}
    for row_id, edge_id in enumerate(sorted(record["remaining_columns"])):
        coord = coord_assignment[int(edge_id)]
        h6_column_id = assignment[int(edge_id)]
        pair_options = [
            H6_LABELS.index(label)
            for label in edge_pair_data(row_by_edge[int(edge_id)], H6_LABELS)[SELECTED_PAIR_FAMILY]
        ]
        placement_rows.append(
            {
                "row_id": row_id,
                "source_edge_id": int(edge_id),
                "h6_column_id": h6_column_id,
                "w24_coordinate": coord,
                "mog_row": profile[coord]["mog_row"],
                "f4_value": profile[coord]["f4_value"],
                "support_flag": int(int(edge_id) in TARGET_SUPPORT),
                "target_octad_flag": int((target_mask >> coord) & 1),
                "pair_family_code": PAIR_FAMILY_CODES[SELECTED_PAIR_FAMILY],
                "pair_choice_position": pair_options.index(h6_column_id),
                "compatible_record_id": record_id,
            }
        )
    octad_rows = [
        {
            "octad_row_id": index,
            "source_edge_id": row["source_edge_id"],
            "w24_coordinate": row["w24_coordinate"],
            "h6_column_id": row["h6_column_id"],
            "mog_row": row["mog_row"],
            "f4_value": row["f4_value"],
        }
        for index, row in enumerate(row for row in placement_rows if row["support_flag"] == 1)
    ]
    mapped_support_mask = sum(1 << row["w24_coordinate"] for row in placement_rows if row["support_flag"] == 1)
    h6_counts = [sum(1 for row in placement_rows if row["h6_column_id"] == column) for column in range(len(H6_LABELS))]
    support_h6_counts = [sum(1 for row in octad_rows if row["h6_column_id"] == column) for column in range(len(H6_LABELS))]
    obs = {
        "long_k23_certified_flag": int(long_k23.get("status") == "SECTOR33_K23_PUNCTURED_MOG_SYZYGY_APERTURE_TARGET_CERTIFIED" and long_k23.get("all_checks_pass") is True),
        "w24_code_certified_flag": int(w24.get("status") == "D20_W24_HEXACODE_ROW_ALPHABETIZATION_CERTIFIED" and w24.get("all_checks_pass") is True),
        "delete_contract_input_certified_flag": int(delete_contract.get("status") == "D20_SECTOR33_W24_MARKED_DELETE_CONTRACT_SHADOW_PROBE_CERTIFIED" and delete_contract.get("all_checks_pass") is True),
        "compatible_record_count": len(records),
        "nontrivial_compatible_record_count": len(nontrivial),
        "unique_nonzero_support_count": len(unique_supports),
        "selected_record_id": record_id,
        "selected_extra_removed": int(record["extra_removed"]),
        "selected_effective_contract_count": int(record["effective_contract_count"]),
        "remaining_column_count": len(record["remaining_columns"]),
        "pair_family_code": PAIR_FAMILY_CODES[SELECTED_PAIR_FAMILY],
        "assignment_edge_count": len(placement_rows),
        "support_edge_count": len(octad_rows),
        "h6_balance_flag": int(h6_counts == [4] * 6 and support_h6_counts == TARGET_COLUMN_VECTOR),
        "mapped_coordinate_count": len({row["w24_coordinate"] for row in placement_rows}),
        "mapped_coordinate_bijection_flag": int(len({row["w24_coordinate"] for row in placement_rows}) == 24),
        "target_octad_weight": int(target_mask.bit_count()),
        "target_octad_in_w24_code_flag": int(target_mask in target_span),
        "mapped_support_matches_target_octad_flag": int(mapped_support_mask == target_mask),
        "rowspace_equality_certified_flag": 0,
        "full_morphism_certified_flag": 0,
        "m23_module_proven_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {"observable_id": OBS_CODES[name], "observable_code": OBS_CODES[name], "value": int(obs[name])}
        for name in OBS_NAMES
    ]
    placement_matrix = np.asarray(
        [[row[column] for column in PLACEMENT_COLUMNS] for row in placement_rows],
        dtype=np.int64,
    )
    target_vector = np.asarray([(target_mask >> coord) & 1 for coord in range(24)], dtype=np.int64)
    support_vector = np.asarray([row["source_edge_id"] for row in octad_rows], dtype=np.int64)
    matrix_payload = {
        "placement_matrix": placement_matrix,
        "target_octad_vector": target_vector,
        "support_edge_vector": support_vector,
    }
    return {
        "long_k23": long_k23,
        "w24": w24,
        "delete_contract": delete_contract,
        "placement_rows": placement_rows,
        "octad_rows": octad_rows,
        "obs_rows": obs_rows,
        "placement_table": table_from_rows(PLACEMENT_COLUMNS, placement_rows),
        "octad_table": table_from_rows(OCTAD_COLUMNS, octad_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "matrix_payload": matrix_payload,
        "matrix_sha256": matrix_payload_hash(matrix_payload),
        "obs": obs,
        "target_mask": target_mask,
        "mapped_support_mask": mapped_support_mask,
        "h6_counts": h6_counts,
        "support_h6_counts": support_h6_counts,
        "placement_text_hash": hashlib.sha256(digest_text(PLACEMENT_COLUMNS, placement_rows).encode("ascii")).hexdigest(),
        "octad_text_hash": hashlib.sha256(digest_text(OCTAD_COLUMNS, octad_rows).encode("ascii")).hexdigest(),
        "obs_text_hash": hashlib.sha256(digest_text(OBS_COLUMNS, obs_rows).encode("ascii")).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "long_k23_input_passes": obs["long_k23_certified_flag"] == 1,
        "w24_code_input_passes": obs["w24_code_certified_flag"] == 1,
        "delete_contract_input_passes": obs["delete_contract_input_certified_flag"] == 1,
        "unique_sector33_octad_support_selected": (
            obs["compatible_record_count"],
            obs["nontrivial_compatible_record_count"],
            obs["unique_nonzero_support_count"],
            obs["support_edge_count"],
        )
        == (70, 15, 1, 8),
        "selected_record_has_24_remaining_columns": obs["remaining_column_count"] == 24,
        "placement_is_h6_balanced": obs["h6_balance_flag"] == 1,
        "placement_is_w24_coordinate_bijection": (
            obs["assignment_edge_count"],
            obs["mapped_coordinate_count"],
            obs["mapped_coordinate_bijection_flag"],
        )
        == (24, 24, 1),
        "mapped_support_is_certified_w24_octad": (
            obs["target_octad_weight"],
            obs["target_octad_in_w24_code_flag"],
            obs["mapped_support_matches_target_octad_flag"],
        )
        == (8, 1, 1),
        "higher_binding_claims_remain_open": (
            obs["rowspace_equality_certified_flag"],
            obs["full_morphism_certified_flag"],
            obs["m23_module_proven_flag"],
            obs["complete_goal_claim_flag"],
        )
        == (0, 0, 0, 0),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sector33_k23_typed_w24_octad_placement",
        "summary": obs,
        "target_w24_octad_mask": rows["target_mask"],
        "mapped_support_mask": rows["mapped_support_mask"],
        "h6_counts": rows["h6_counts"],
        "support_h6_counts": rows["support_h6_counts"],
        "matrix_sha256": rows["matrix_sha256"],
        "boundary": "This places the unique sector33 rank-one support into a certified W24 octad and a full H6-balanced coordinate bijection, but it is not yet a rowspace or K23 equality proof.",
    }
    seam_payload = {
        "schema": "long.k23oct.seam@1",
        "status": STATUS,
        "claim": "The unique rank-one sector33 delete/contract octad support admits a typed placement into a certified W24 octad, extending to a 24-coordinate H6-balanced bijection for the selected shadow record.",
        "witness": witness,
        "checks": checks,
    }
    inputs = {
        "long_k23": input_entry(
            LONG_K23_REPORT,
            {
                "status": rows["long_k23"].get("status"),
                "certificate_sha256": rows["long_k23"].get("certificate_sha256"),
            },
        ),
        "w24_hexacode_row_alphabetization": input_entry(
            W24_REPORT,
            {
                "status": rows["w24"].get("status"),
                "certificate_sha256": rows["w24"].get("certificate_sha256"),
            },
        ),
        "sector33_w24_marked_delete_contract_shadow_probe": input_entry(
            DELETE_CONTRACT_REPORT,
            {
                "status": rows["delete_contract"].get("status"),
                "certificate_sha256": rows["delete_contract"].get("certificate_sha256"),
            },
        ),
        "d20_json": input_entry(D20_JSON),
        "derive_script": input_entry(DERIVE_SCRIPT),
        "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
    }
    report = {
        "schema": "long.k23oct.report@1",
        "status": STATUS,
        "all_checks_pass": all(checks.values()),
        "claim": "long_k23oct certifies a typed W24 octad placement witness for the unique sector33 rank-one delete/contract support, while keeping the full rowspace and K23 equality claims open.",
        "stage_protocol": {
            "draft": "read long_k23, W24 row alphabetization, d20 edge labels, and the marked delete/contract shadow probe",
            "witness": "emit the 24-coordinate placement rows, the eight support-octad rows, observables, and matrix payloads",
            "coherence": "check H6 balance, coordinate bijection, W24 code membership, and open higher-binding flags",
            "closure": "certify typed octad placement without claiming a full sector33-to-W24 morphism",
            "emit": "write long_k23oct artifacts and verifier hook",
        },
        "inputs": inputs,
        "outputs": {
            "seam": relpath(OUT_DIR / "seam.json"),
            "placement_rows_csv": relpath(OUT_DIR / "placement_rows.csv"),
            "octad_rows_csv": relpath(OUT_DIR / "octad_rows.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "matrices": relpath(OUT_DIR / "k23oct_matrices.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the selected delete/contract shadow record has 24 remaining sector33 columns",
                "the unique nonzero rank-one sector33 support has eight edge ids",
                "the eight support ids are placed into a certified W24 weight-eight codeword",
                "the placement extends to a 24-coordinate H6-balanced bijection using the shared-duad typed rule",
                "the mapped support mask is exactly the target W24 octad mask",
            ],
            "does_not_certify": [
                "a full sector33-to-W24 rowspace morphism",
                "rowspan(K23) equals the W24/Euler-punctured syzygy rowspace",
                "the complete 56-to-W24 syzygy basis-binding map",
                "an M23 module action on K23",
                "a rebuild of d20.json or broad bundle closure",
            ],
        },
        "next_highest_yield_item": "Promote this octad placement from a rank-one support witness to a full 24-column rowspace test for the selected shadow record.",
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {"schema": "long.k23oct.cert@1", "status": STATUS, "checks": checks, "witness": witness}
    manifest = {
        "schema": "long.k23oct.manifest@1",
        "name": THEOREM_ID,
        "status": STATUS,
        "inputs": inputs,
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "seam": seam_payload,
        "placement_csv": csv_text(PLACEMENT_COLUMNS, rows["placement_rows"]),
        "octad_csv": csv_text(OCTAD_COLUMNS, rows["octad_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "placement_table": rows["placement_table"],
        "octad_table": rows["octad_table"],
        "observable_table": rows["observable_table"],
        "matrix_payload": rows["matrix_payload"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "placement_text_sha256": rows["placement_text_hash"],
            "octad_text_sha256": rows["octad_text_hash"],
            "obs_text_sha256": rows["obs_text_hash"],
            "matrix_sha256": rows["matrix_sha256"],
        },
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
    (OUT_DIR / "placement_rows.csv").write_text(payloads["placement_csv"], encoding="utf-8")
    (OUT_DIR / "octad_rows.csv").write_text(payloads["octad_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    write_json(OUT_DIR / "seam.json", payloads["seam"])
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        placement_table=payloads["placement_table"],
        octad_table=payloads["octad_table"],
        observable_table=payloads["observable_table"],
    )
    np.savez_compressed(OUT_DIR / "k23oct_matrices.npz", **payloads["matrix_payload"])
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
                "computed_hashes": payloads["computed_hashes"],
                "summary": report["witness"]["summary"],
                "report": relpath(OUT_DIR / "report.json"),
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
