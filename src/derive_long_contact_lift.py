from __future__ import annotations

import csv
import hashlib
import json
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
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .derive_long_time_sem import raw_tensor_path_from_index
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from derive_long_time_sem import raw_tensor_path_from_index
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_contact_lift"
STATUS = "LONG_CONTACT_LIFT_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

PROOF_ROOT = D20_INVARIANTS / "proof_obligations"
RAW_INDEX = ROOT / "data" / "raw" / "index.json"
LONG_METRIC_GATE = PROOF_ROOT / "long_metric_gate" / "report.json"
LONG_TIME_SEM = PROOF_ROOT / "long_time_sem" / "report.json"
LONG_REC = PROOF_ROOT / "long_rec" / "report.json"
LONG_REC_TABLES = PROOF_ROOT / "long_rec" / "tables.npz"
LONG_REC_OWNER = PROOF_ROOT / "long_rec" / "owner.csv"
LONG_REC_EDGE = PROOF_ROOT / "long_rec" / "edge.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_contact_lift.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_contact_lift.py"

ENDPOINT_COLUMNS = [
    "basis_id",
    "source0_addr",
    "source1_addr",
    "target_addr",
    "coeff",
    "raw_tensor_flag",
    "owner_cell_count",
    "graph_degree",
    "weighted_degree",
]
CONTACT_COLUMNS = [
    "contact_id",
    "edge_id",
    "left_basis_id",
    "right_basis_id",
    "source0_boundary_count",
    "source1_boundary_count",
    "boundary_count",
    "source0_sample_x",
    "source0_sample_y",
    "source0_sample_owner_a",
    "source0_sample_owner_b",
    "source1_sample_x",
    "source1_sample_y",
    "source1_sample_owner_a",
    "source1_sample_owner_b",
    "left_endpoint_raw_flag",
    "right_endpoint_raw_flag",
    "source0_count_verified_flag",
    "source1_count_verified_flag",
    "boundary_count_verified_flag",
    "contact_lift_flag",
]
GAP_COLUMNS = [
    "gap_id",
    "obligation_code",
    "required_for_gr_flag",
    "certified_flag",
    "obstruction_flag",
    "next_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

GAP_NAMES = [
    "owner_boundary_contact_lift",
    "semantic_operation_from_contact_lift",
    "physical_stress_energy_tensor",
    "nondegenerate_smooth_lorentzian_metric",
    "four_dimensional_spacetime_reduction",
    "curvature_and_einstein_tensor",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "raw_tensor_row_count",
    "raw_tensor_coeff_mass",
    "owner_grid_row_count",
    "owner_grid_col_count",
    "owner_grid_min",
    "owner_grid_max",
    "owner_row_count",
    "endpoint_raw_count",
    "recurrence_edge_count",
    "contact_edge_count",
    "source0_contact_sum",
    "source1_contact_sum",
    "boundary_contact_sum",
    "source0_verified_edge_count",
    "source1_verified_edge_count",
    "boundary_verified_edge_count",
    "contact_lift_edge_count",
    "contact_lift_certified_flag",
    "semantic_edge_operation_flag",
    "semantic_operation_certified_flag",
    "smooth_lorentzian_metric_flag",
    "gr_derivation_flag",
    "open_gap_count",
    "next_gap_code",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _read_csv_int(path: Path) -> list[dict[str, int]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return [{key: int(value) for key, value in row.items()} for row in reader]


def _raw_tensor(path: Path) -> np.ndarray:
    with np.load(path, allow_pickle=False) as payload:
        triples = np.asarray(payload["triples"], dtype=np.int64)
    if triples.ndim != 2 or triples.shape[1] != 4:
        raise AssertionError("raw tensor triples must have shape n x 4")
    return triples


def _raw_tuple_set(triples: np.ndarray) -> set[tuple[int, int, int, int]]:
    return {tuple(int(value) for value in row) for row in triples.tolist()}


def _pair_key(left: int, right: int) -> tuple[int, int]:
    return (left, right) if left <= right else (right, left)


def _blank_stat() -> dict[str, Any]:
    return {
        "source0_count": 0,
        "source1_count": 0,
        "source0_sample": (-1, -1, -1, -1),
        "source1_sample": (-1, -1, -1, -1),
    }


def contact_stats(owner_grid: np.ndarray) -> dict[tuple[int, int], dict[str, Any]]:
    stats: dict[tuple[int, int], dict[str, Any]] = {}
    for axis, (left, right) in enumerate(
        (
            (owner_grid[:-1, :], owner_grid[1:, :]),
            (owner_grid[:, :-1], owner_grid[:, 1:]),
        )
    ):
        differs = left != right
        xs, ys = np.nonzero(differs)
        for x, y in zip(xs.tolist(), ys.tolist()):
            owner_a = int(left[x, y])
            owner_b = int(right[x, y])
            key = _pair_key(owner_a, owner_b)
            stat = stats.setdefault(key, _blank_stat())
            if axis == 0:
                stat["source0_count"] += 1
                if stat["source0_sample"][0] < 0:
                    stat["source0_sample"] = (int(x), int(y), owner_a, owner_b)
            else:
                stat["source1_count"] += 1
                if stat["source1_sample"][0] < 0:
                    stat["source1_sample"] = (int(x), int(y), owner_a, owner_b)
    return stats


def endpoint_rows(
    owner_rows: list[dict[str, int]],
    raw_tuples: set[tuple[int, int, int, int]],
) -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    for owner in owner_rows:
        endpoint = (
            owner["source0_addr"],
            owner["source1_addr"],
            owner["target_addr"],
            owner["coeff"],
        )
        rows.append(
            {
                "basis_id": owner["basis_id"],
                "source0_addr": owner["source0_addr"],
                "source1_addr": owner["source1_addr"],
                "target_addr": owner["target_addr"],
                "coeff": owner["coeff"],
                "raw_tensor_flag": int(endpoint in raw_tuples),
                "owner_cell_count": owner["owner_cell_count"],
                "graph_degree": owner["graph_degree"],
                "weighted_degree": owner["weighted_degree"],
            }
        )
    return rows


def contact_rows(
    edge_rows: list[dict[str, int]],
    endpoints: dict[int, dict[str, int]],
    stats: dict[tuple[int, int], dict[str, Any]],
) -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    for contact_id, edge in enumerate(edge_rows):
        left = edge["left_basis_id"]
        right = edge["right_basis_id"]
        stat = stats.get(_pair_key(left, right), _blank_stat())
        s0_sample = stat["source0_sample"]
        s1_sample = stat["source1_sample"]
        s0_count = int(stat["source0_count"])
        s1_count = int(stat["source1_count"])
        boundary_count = s0_count + s1_count
        s0_verified = int(s0_count == edge["source0_boundary_count"])
        s1_verified = int(s1_count == edge["source1_boundary_count"])
        boundary_verified = int(boundary_count == edge["boundary_count"])
        left_raw = endpoints[left]["raw_tensor_flag"]
        right_raw = endpoints[right]["raw_tensor_flag"]
        rows.append(
            {
                "contact_id": contact_id,
                "edge_id": edge["edge_id"],
                "left_basis_id": left,
                "right_basis_id": right,
                "source0_boundary_count": s0_count,
                "source1_boundary_count": s1_count,
                "boundary_count": boundary_count,
                "source0_sample_x": int(s0_sample[0]),
                "source0_sample_y": int(s0_sample[1]),
                "source0_sample_owner_a": int(s0_sample[2]),
                "source0_sample_owner_b": int(s0_sample[3]),
                "source1_sample_x": int(s1_sample[0]),
                "source1_sample_y": int(s1_sample[1]),
                "source1_sample_owner_a": int(s1_sample[2]),
                "source1_sample_owner_b": int(s1_sample[3]),
                "left_endpoint_raw_flag": left_raw,
                "right_endpoint_raw_flag": right_raw,
                "source0_count_verified_flag": s0_verified,
                "source1_count_verified_flag": s1_verified,
                "boundary_count_verified_flag": boundary_verified,
                "contact_lift_flag": int(
                    left_raw
                    and right_raw
                    and s0_verified
                    and s1_verified
                    and boundary_verified
                    and boundary_count > 0
                ),
            }
        )
    return rows


def build_rows() -> dict[str, Any]:
    raw_index = load_json(RAW_INDEX)
    raw_tensor_path = raw_tensor_path_from_index(raw_index)
    raw_tensor = _raw_tensor(raw_tensor_path)
    raw_tuples = _raw_tuple_set(raw_tensor)
    long_metric_gate = load_json(LONG_METRIC_GATE)
    long_time_sem = load_json(LONG_TIME_SEM)
    long_rec = load_json(LONG_REC)
    owner_rows_source = _read_csv_int(LONG_REC_OWNER)
    edge_rows_source = _read_csv_int(LONG_REC_EDGE)
    with np.load(LONG_REC_TABLES, allow_pickle=False) as payload:
        owner_grid = np.asarray(payload["owner_grid"], dtype=np.int64)
    endpoints = endpoint_rows(owner_rows_source, raw_tuples)
    endpoint_by_id = {row["basis_id"]: row for row in endpoints}
    stats = contact_stats(owner_grid)
    contacts = contact_rows(edge_rows_source, endpoint_by_id, stats)

    source0_contact_sum = sum(row["source0_boundary_count"] for row in contacts)
    source1_contact_sum = sum(row["source1_boundary_count"] for row in contacts)
    boundary_contact_sum = sum(row["boundary_count"] for row in contacts)
    source0_verified_edge_count = sum(
        row["source0_count_verified_flag"] for row in contacts
    )
    source1_verified_edge_count = sum(
        row["source1_count_verified_flag"] for row in contacts
    )
    boundary_verified_edge_count = sum(
        row["boundary_count_verified_flag"] for row in contacts
    )
    contact_lift_edge_count = sum(row["contact_lift_flag"] for row in contacts)

    gap_rows = [
        {
            "gap_id": 0,
            "obligation_code": GAP_CODES["owner_boundary_contact_lift"],
            "required_for_gr_flag": 1,
            "certified_flag": 1,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": 1,
            "obligation_code": GAP_CODES["semantic_operation_from_contact_lift"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 1,
        },
        {
            "gap_id": 2,
            "obligation_code": GAP_CODES["physical_stress_energy_tensor"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": 3,
            "obligation_code": GAP_CODES["nondegenerate_smooth_lorentzian_metric"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": 4,
            "obligation_code": GAP_CODES["four_dimensional_spacetime_reduction"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": 5,
            "obligation_code": GAP_CODES["curvature_and_einstein_tensor"],
            "required_for_gr_flag": 1,
            "certified_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
    ]

    obs = {
        "raw_tensor_row_count": int(raw_tensor.shape[0]),
        "raw_tensor_coeff_mass": int(raw_tensor[:, 3].sum()),
        "owner_grid_row_count": int(owner_grid.shape[0]),
        "owner_grid_col_count": int(owner_grid.shape[1]),
        "owner_grid_min": int(owner_grid.min()),
        "owner_grid_max": int(owner_grid.max()),
        "owner_row_count": len(endpoints),
        "endpoint_raw_count": sum(row["raw_tensor_flag"] for row in endpoints),
        "recurrence_edge_count": len(edge_rows_source),
        "contact_edge_count": len(contacts),
        "source0_contact_sum": source0_contact_sum,
        "source1_contact_sum": source1_contact_sum,
        "boundary_contact_sum": boundary_contact_sum,
        "source0_verified_edge_count": source0_verified_edge_count,
        "source1_verified_edge_count": source1_verified_edge_count,
        "boundary_verified_edge_count": boundary_verified_edge_count,
        "contact_lift_edge_count": contact_lift_edge_count,
        "contact_lift_certified_flag": int(contact_lift_edge_count == len(contacts)),
        "semantic_edge_operation_flag": 0,
        "semantic_operation_certified_flag": 0,
        "smooth_lorentzian_metric_flag": 0,
        "gr_derivation_flag": 0,
        "open_gap_count": sum(1 - row["certified_flag"] for row in gap_rows),
        "next_gap_code": GAP_CODES["semantic_operation_from_contact_lift"],
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]

    return {
        "raw_index": raw_index,
        "raw_tensor_path": raw_tensor_path,
        "raw_tensor": raw_tensor,
        "long_metric_gate": long_metric_gate,
        "long_time_sem": long_time_sem,
        "long_rec": long_rec,
        "owner_grid": owner_grid,
        "endpoint_rows": endpoints,
        "contact_rows": contacts,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "endpoint_table": table_from_rows(ENDPOINT_COLUMNS, endpoints),
        "contact_table": table_from_rows(CONTACT_COLUMNS, contacts),
        "gap_table": table_from_rows(GAP_COLUMNS, gap_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "endpoint_text_hash": sha_text(digest_text(ENDPOINT_COLUMNS, endpoints)),
        "contact_text_hash": sha_text(digest_text(CONTACT_COLUMNS, contacts)),
        "gap_text_hash": sha_text(digest_text(GAP_COLUMNS, gap_rows)),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    long_metric_gate = rows["long_metric_gate"]
    long_time_sem = rows["long_time_sem"]
    long_rec = rows["long_rec"]
    contacts = rows["contact_rows"]
    checks = {
        "metric_gate_input_certified": long_metric_gate.get("status")
        == "LONG_METRIC_GATE_CERTIFIED"
        and long_metric_gate.get("all_checks_pass") is True,
        "time_sem_guard_preserved": long_time_sem.get("status")
        == "LONG_TIME_SEM_OBSTRUCTION_CERTIFIED"
        and long_time_sem.get("all_checks_pass") is True
        and obs["semantic_edge_operation_flag"] == 0,
        "long_rec_input_certified": long_rec.get("status") == "LONG_REC_CERTIFIED"
        and long_rec.get("all_checks_pass") is True,
        "raw_endpoint_support_exact": obs["raw_tensor_row_count"] == 1_414_965
        and obs["raw_tensor_coeff_mass"] == 2_537_360
        and obs["owner_row_count"] == 259
        and obs["endpoint_raw_count"] == 259,
        "owner_grid_shape_exact": obs["owner_grid_row_count"] == 985
        and obs["owner_grid_col_count"] == 985
        and obs["owner_grid_min"] == 0
        and obs["owner_grid_max"] == 258,
        "contact_counts_exact": obs["recurrence_edge_count"] == 642
        and obs["contact_edge_count"] == 642
        and obs["source0_contact_sum"] == 12_707
        and obs["source1_contact_sum"] == 5_410
        and obs["boundary_contact_sum"] == 18_117,
        "all_edge_counts_verified": obs["source0_verified_edge_count"] == 642
        and obs["source1_verified_edge_count"] == 642
        and obs["boundary_verified_edge_count"] == 642
        and obs["contact_lift_edge_count"] == 642
        and all(row["contact_lift_flag"] == 1 for row in contacts),
        "sample_contacts_match_nonzero_axes": all(
            (row["source0_boundary_count"] == 0 and row["source0_sample_x"] == -1)
            or (
                row["source0_boundary_count"] > 0
                and row["source0_sample_x"] >= 0
                and _pair_key(
                    row["source0_sample_owner_a"], row["source0_sample_owner_b"]
                )
                == _pair_key(row["left_basis_id"], row["right_basis_id"])
            )
            for row in contacts
        )
        and all(
            (row["source1_boundary_count"] == 0 and row["source1_sample_x"] == -1)
            or (
                row["source1_boundary_count"] > 0
                and row["source1_sample_x"] >= 0
                and _pair_key(
                    row["source1_sample_owner_a"], row["source1_sample_owner_b"]
                )
                == _pair_key(row["left_basis_id"], row["right_basis_id"])
            )
            for row in contacts
        ),
        "contact_lift_not_semantic_operation": obs["contact_lift_certified_flag"] == 1
        and obs["semantic_operation_certified_flag"] == 0
        and obs["smooth_lorentzian_metric_flag"] == 0
        and obs["gr_derivation_flag"] == 0,
        "table_shapes_match": rows["endpoint_table"].shape
        == (259, len(ENDPOINT_COLUMNS))
        and rows["contact_table"].shape == (642, len(CONTACT_COLUMNS))
        and rows["gap_table"].shape == (len(GAP_NAMES), len(GAP_COLUMNS))
        and rows["observable_table"].shape == (len(OBS_NAMES), len(OBS_COLUMNS)),
    }

    witness = {
        "name": THEOREM_ID,
        "classification": "owner_boundary_contact_lift",
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "summary": {
            "owner_grid_shape": [
                obs["owner_grid_row_count"],
                obs["owner_grid_col_count"],
            ],
            "owner_row_count": obs["owner_row_count"],
            "endpoint_raw_count": obs["endpoint_raw_count"],
            "recurrence_edge_count": obs["recurrence_edge_count"],
            "contact_edge_count": obs["contact_edge_count"],
            "source0_contact_sum": obs["source0_contact_sum"],
            "source1_contact_sum": obs["source1_contact_sum"],
            "boundary_contact_sum": obs["boundary_contact_sum"],
            "contact_lift_edge_count": obs["contact_lift_edge_count"],
            "contact_lift_certified_flag": obs["contact_lift_certified_flag"],
            "semantic_operation_certified_flag": obs[
                "semantic_operation_certified_flag"
            ],
            "next_gap": "semantic_operation_from_contact_lift",
        },
        "raw_tensor_sha256": sha_array(rows["raw_tensor"]),
        "owner_grid_sha256": sha_array(rows["owner_grid"]),
        "endpoint_table_sha256": sha_array(rows["endpoint_table"]),
        "endpoint_text_sha256": rows["endpoint_text_hash"],
        "contact_table_sha256": sha_array(rows["contact_table"]),
        "contact_text_sha256": rows["contact_text_hash"],
        "gap_table_sha256": sha_array(rows["gap_table"]),
        "gap_text_sha256": rows["gap_text_hash"],
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    contact_lift = {
        "schema": "long.contact_lift@1",
        "object": "owner_boundary_contact_lift",
        "status": STATUS if all(checks.values()) else "LONG_CONTACT_LIFT_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.contact_lift.report@1",
        "status": contact_lift["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_contact_lift materializes the owner-boundary contact layer "
            "behind the long_rec recurrence graph: every one of the 642 graph "
            "edges has exact source0/source1 boundary-contact counts "
            "recomputed from the 985x985 owner grid, a representative contact "
            "coordinate on every nonzero contact axis, and A985 raw-backed "
            "endpoint triples on both sides. This closes the owner-boundary "
            "contact lift required by long_metric_gate, while preserving that "
            "contacts are not yet semantic A985 transition operations."
        ),
        "stage_protocol": {
            "draft": "read long_metric_gate, long_time_sem, long_rec owner/edge rows, owner_grid, and raw tensor",
            "witness": "emit raw-backed endpoint rows and per-edge owner-boundary contact rows",
            "coherence": "check endpoint raw support, owner-grid shape, exact axis contact counts, sample coordinates, and table hashes",
            "closure": "certify owner-boundary contact lift without claiming semantic transition operations or GR",
            "emit": "write long_contact_lift artifacts and verifier hook",
        },
        "inputs": {
            "raw_index": input_entry(RAW_INDEX),
            "raw_tensor": input_entry(
                rows["raw_tensor_path"],
                {
                    "row_count": int(rows["raw_tensor"].shape[0]),
                    "column_count": int(rows["raw_tensor"].shape[1]),
                },
            ),
            "long_metric_gate": input_entry(
                LONG_METRIC_GATE,
                {
                    "status": long_metric_gate.get("status"),
                    "certificate_sha256": long_metric_gate.get("certificate_sha256"),
                },
            ),
            "long_time_sem": input_entry(
                LONG_TIME_SEM,
                {
                    "status": long_time_sem.get("status"),
                    "certificate_sha256": long_time_sem.get("certificate_sha256"),
                },
            ),
            "long_rec": input_entry(
                LONG_REC,
                {
                    "status": long_rec.get("status"),
                    "certificate_sha256": long_rec.get("certificate_sha256"),
                },
            ),
            "long_rec_tables": input_entry(LONG_REC_TABLES),
            "long_rec_owner": input_entry(
                LONG_REC_OWNER,
                {"row_count": len(rows["endpoint_rows"])},
            ),
            "long_rec_edge": input_entry(
                LONG_REC_EDGE,
                {"row_count": len(rows["contact_rows"])},
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "contact_lift": relpath(OUT_DIR / "contact_lift.json"),
            "endpoint_csv": relpath(OUT_DIR / "endpoint.csv"),
            "contact_csv": relpath(OUT_DIR / "contact.csv"),
            "gap_csv": relpath(OUT_DIR / "gap.csv"),
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
                "all 259 owner endpoints are A985 raw tensor triples",
                "all 642 recurrence graph edges have exact owner-grid contact counts",
                "source0/source1 contact totals are 12,707 and 5,410, summing to 18,117 boundary contacts",
                "each nonzero contact axis has a representative owner-grid coordinate witness",
                "the owner-boundary contact lift required by long_metric_gate is closed",
            ],
            "does_not_certify_because_open": [
                "a semantic A985 transition operation for each contact-lifted recurrence edge",
                "a physical stress-energy tensor",
                "a nondegenerate smooth Lorentzian metric tensor",
                "a 3+1 spacetime reduction from the 1+19 public split",
                "Riemann/Ricci curvature, Einstein tensor, or Einstein field equations",
            ],
        },
        "next_highest_yield_item": (
            "Build long_transition_sem: decide whether owner-boundary contacts "
            "can be promoted to semantic A985 transition operations, or certify "
            "the remaining obstruction as a distinct operation-realization gap."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.contact_lift.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.contact_lift.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "contact_lift": contact_lift,
        "endpoint_csv": csv_text(ENDPOINT_COLUMNS, rows["endpoint_rows"]),
        "contact_csv": csv_text(CONTACT_COLUMNS, rows["contact_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "raw_tensor": rows["raw_tensor"],
        "owner_grid": rows["owner_grid"],
        "endpoint_table": rows["endpoint_table"],
        "contact_table": rows["contact_table"],
        "gap_table": rows["gap_table"],
        "observable_table": rows["observable_table"],
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
    write_json(OUT_DIR / "contact_lift.json", payloads["contact_lift"])
    (OUT_DIR / "endpoint.csv").write_text(payloads["endpoint_csv"], encoding="utf-8")
    (OUT_DIR / "contact.csv").write_text(payloads["contact_csv"], encoding="utf-8")
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        raw_tensor=payloads["raw_tensor"],
        owner_grid=payloads["owner_grid"],
        endpoint_table=payloads["endpoint_table"],
        contact_table=payloads["contact_table"],
        gap_table=payloads["gap_table"],
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
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
