from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
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
    from derive_long_raw import csv_text, table_from_rows
    from derive_long_time_sem import raw_tensor_path_from_index
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_c59p3k"
STATUS = "LONG_C59P3K_MIXED_CONTACT_ADDRESS_SCREEN_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

RAW_INDEX = ROOT / "data" / "raw" / "index.json"
LONG_C59P3H = PROOF_ROOT / "long_c59p3h" / "report.json"
LONG_C59P3J = PROOF_ROOT / "long_c59p3j" / "report.json"
LONG_C59P3G_TRANSITION_SCHEMA = PROOF_ROOT / "long_c59p3g" / "transition_schema.csv"
LONG_CONTACT_LIFT = PROOF_ROOT / "long_contact_lift" / "report.json"
LONG_CONTACT_CONTACT = PROOF_ROOT / "long_contact_lift" / "contact.csv"
LONG_TRANSITION_SEM = PROOF_ROOT / "long_transition_sem" / "report.json"
LONG_TRANSITION_CSV = PROOF_ROOT / "long_transition_sem" / "transition.csv"
LONG_TRANSITION_ENDPOINT = PROOF_ROOT / "long_transition_sem" / "endpoint_raw.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_c59p3k.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_c59p3k.py"

LIBRARY_NAMES = ["direct_endpoint_field", "contact_sample_slot"]
LIBRARY_CODES = {name: index for index, name in enumerate(LIBRARY_NAMES)}
CONTACT_AXIS_NAMES = ["source0", "source1"]
CONTACT_AXIS_CODES = {name: index for index, name in enumerate(CONTACT_AXIS_NAMES)}
ORIENTATION_NAMES = ["lr", "rl", "xy", "yx"]
ORIENTATION_CODES = {name: index for index, name in enumerate(ORIENTATION_NAMES)}
FIELD_NAMES = ["source0_addr", "source1_addr", "target_addr", "coeff"]
FIELD_CODES = {name: index for index, name in enumerate(FIELD_NAMES)}
TARGET_SELECTOR_NAMES = [
    "sample_owner_a",
    "sample_owner_b",
    "left_endpoint",
    "right_endpoint",
]
TARGET_SELECTOR_CODES = {
    name: index for index, name in enumerate(TARGET_SELECTOR_NAMES)
}

CANDIDATE_COLUMNS = [
    "candidate_id",
    "library_code",
    "local_candidate_id",
    "contact_axis_code",
    "orientation_code",
    "source0_field_code",
    "source1_field_code",
    "target_selector_code",
    "target_field_code",
    "active_transition_count",
    "covered_transition_count",
    "uncovered_transition_count",
    "total_raw_match_count",
    "max_raw_match_count",
    "full_candidate_flag",
    "semantic_operation_flag",
]
COVER_COLUMNS = [
    "active_transition_id",
    "transition_id",
    "direct_covered_flag",
    "contact_covered_flag",
    "mixed_covered_flag",
    "direct_best_candidate_id",
    "direct_best_raw_match_count",
    "contact_best_candidate_id",
    "contact_best_raw_match_count",
    "mixed_obstruction_flag",
]
GAP_COLUMNS = [
    "gap_id",
    "gap_code",
    "certified_flag",
    "open_flag",
    "obstruction_flag",
    "next_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

GAP_NAMES = [
    "direct_address_screen_input",
    "endpoint_projector_input",
    "contact_sample_slot_screen",
    "full_mixed_candidate_obstruction",
    "mixed_union_partial_cover",
    "semantic_operation_rows_absent",
    "transition_composition_law",
    "physical_selector_axiom",
    "metric_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "active_transition_count",
    "direct_candidate_count",
    "contact_candidate_count",
    "mixed_candidate_count",
    "full_candidate_count",
    "best_candidate_id",
    "best_candidate_library_code",
    "best_candidate_covered_transition_count",
    "best_direct_candidate_id",
    "best_direct_covered_transition_count",
    "best_contact_candidate_id",
    "best_contact_covered_transition_count",
    "direct_union_covered_transition_count",
    "contact_union_covered_transition_count",
    "mixed_union_covered_transition_count",
    "mixed_union_uncovered_transition_count",
    "missing_transition_id_count",
    "operation_promoted_row_count",
    "semantic_operation_flag",
    "transition_composition_law_flag",
    "physical_selector_axiom_flag",
    "metric_derivation_flag",
    "next_gap_code",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def certified(report: dict[str, Any]) -> bool:
    return report.get("all_checks_pass") is True and "CERTIFIED" in str(
        report.get("status", "")
    )


def raw_tensor(path: Path) -> np.ndarray:
    with np.load(path, allow_pickle=False) as payload:
        triples = np.asarray(payload["triples"], dtype=np.int64)
    if triples.ndim != 2 or triples.shape[1] != 4:
        raise AssertionError("raw tensor triples must have shape n x 4")
    return triples


def raw_support_index(triples: np.ndarray) -> dict[tuple[int, int, int], int]:
    counts: dict[tuple[int, int, int], int] = defaultdict(int)
    for row in triples.tolist():
        counts[(int(row[0]), int(row[1]), int(row[2]))] += 1
    return counts


def direct_key(
    transition: dict[str, str],
    endpoints: dict[int, dict[str, str]],
    *,
    orientation_name: str,
    source0_field: str,
    source1_field: str,
    target_selector_name: str,
    target_field: str,
) -> tuple[int, int, int]:
    left = endpoints[int(transition["left_basis_id"])]
    right = endpoints[int(transition["right_basis_id"])]
    first, second = (left, right) if orientation_name == "lr" else (right, left)
    target = left if target_selector_name == "left_endpoint" else right
    return (
        int(first[source0_field]),
        int(second[source1_field]),
        int(target[target_field]),
    )


def contact_key(
    transition: dict[str, str],
    contact: dict[str, str],
    endpoints: dict[int, dict[str, str]],
    *,
    contact_axis_name: str,
    orientation_name: str,
    target_selector_name: str,
    target_field: str,
) -> tuple[int, int, int]:
    x = int(contact[f"{contact_axis_name}_sample_x"])
    y = int(contact[f"{contact_axis_name}_sample_y"])
    if target_selector_name == "sample_owner_a":
        basis_id = int(contact[f"{contact_axis_name}_sample_owner_a"])
    elif target_selector_name == "sample_owner_b":
        basis_id = int(contact[f"{contact_axis_name}_sample_owner_b"])
    elif target_selector_name == "left_endpoint":
        basis_id = int(transition["left_basis_id"])
    else:
        basis_id = int(transition["right_basis_id"])
    if basis_id < 0:
        target = -1
    else:
        target = int(endpoints[basis_id][target_field])
    return (x, y, target) if orientation_name == "xy" else (y, x, target)


def candidate_profile(
    *,
    candidate_id: int,
    library_name: str,
    local_candidate_id: int,
    contact_axis_code: int,
    orientation_code: int,
    source0_field_code: int,
    source1_field_code: int,
    target_selector_code: int,
    target_field_code: int,
    keys: list[tuple[int, int, int]],
    support_counts: dict[tuple[int, int, int], int],
) -> tuple[dict[str, int], list[int]]:
    counts = [
        0 if min(key) < 0 else int(support_counts.get(key, 0)) for key in keys
    ]
    covered_ids = [index for index, count in enumerate(counts) if count > 0]
    row = {
        "candidate_id": candidate_id,
        "library_code": LIBRARY_CODES[library_name],
        "local_candidate_id": local_candidate_id,
        "contact_axis_code": contact_axis_code,
        "orientation_code": orientation_code,
        "source0_field_code": source0_field_code,
        "source1_field_code": source1_field_code,
        "target_selector_code": target_selector_code,
        "target_field_code": target_field_code,
        "active_transition_count": len(keys),
        "covered_transition_count": len(covered_ids),
        "uncovered_transition_count": len(keys) - len(covered_ids),
        "total_raw_match_count": sum(counts),
        "max_raw_match_count": max(counts) if counts else 0,
        "full_candidate_flag": int(len(covered_ids) == len(keys)),
        "semantic_operation_flag": 0,
    }
    return row, counts


def best_count_for_transition(
    candidate_rows: list[dict[str, int]],
    counts_by_candidate: dict[int, list[int]],
    active_transition_id: int,
) -> tuple[int, int]:
    best = sorted(
        (
            (
                counts_by_candidate[row["candidate_id"]][active_transition_id],
                row["candidate_id"],
            )
            for row in candidate_rows
        ),
        key=lambda item: (-item[0], item[1]),
    )[0]
    return best[1], best[0]


def build_rows() -> dict[str, Any]:
    c59p3h = load_json(LONG_C59P3H)
    c59p3j = load_json(LONG_C59P3J)
    contact_lift = load_json(LONG_CONTACT_LIFT)
    transition_sem = load_json(LONG_TRANSITION_SEM)
    raw_index_payload = load_json(RAW_INDEX)
    raw_tensor_path = raw_tensor_path_from_index(raw_index_payload)
    triples = raw_tensor(raw_tensor_path)
    support_counts = raw_support_index(triples)

    _, active_raw = read_csv_rows(LONG_C59P3G_TRANSITION_SCHEMA)
    _, transition_raw = read_csv_rows(LONG_TRANSITION_CSV)
    _, endpoint_raw = read_csv_rows(LONG_TRANSITION_ENDPOINT)
    _, contact_raw = read_csv_rows(LONG_CONTACT_CONTACT)

    transition_by_id = {int(row["transition_id"]): row for row in transition_raw}
    endpoint_by_id = {int(row["basis_id"]): row for row in endpoint_raw}
    contact_by_edge_id = {int(row["edge_id"]): row for row in contact_raw}
    active_transitions = [
        transition_by_id[int(row["transition_id"])] for row in active_raw
    ]

    candidate_rows = []
    counts_by_candidate: dict[int, list[int]] = {}
    direct_candidate_ids: list[int] = []
    contact_candidate_ids: list[int] = []

    candidate_id = 0
    local_candidate_id = 0
    for orientation_name in ("lr", "rl"):
        for source0_field in FIELD_NAMES[:3]:
            for source1_field in FIELD_NAMES[:3]:
                for target_selector_name in ("left_endpoint", "right_endpoint"):
                    for target_field in FIELD_NAMES[:3]:
                        keys = [
                            direct_key(
                                transition,
                                endpoint_by_id,
                                orientation_name=orientation_name,
                                source0_field=source0_field,
                                source1_field=source1_field,
                                target_selector_name=target_selector_name,
                                target_field=target_field,
                            )
                            for transition in active_transitions
                        ]
                        row, counts = candidate_profile(
                            candidate_id=candidate_id,
                            library_name="direct_endpoint_field",
                            local_candidate_id=local_candidate_id,
                            contact_axis_code=-1,
                            orientation_code=ORIENTATION_CODES[orientation_name],
                            source0_field_code=FIELD_CODES[source0_field],
                            source1_field_code=FIELD_CODES[source1_field],
                            target_selector_code=TARGET_SELECTOR_CODES[
                                target_selector_name
                            ],
                            target_field_code=FIELD_CODES[target_field],
                            keys=keys,
                            support_counts=support_counts,
                        )
                        candidate_rows.append(row)
                        counts_by_candidate[candidate_id] = counts
                        direct_candidate_ids.append(candidate_id)
                        candidate_id += 1
                        local_candidate_id += 1

    local_candidate_id = 0
    for contact_axis_name in CONTACT_AXIS_NAMES:
        for orientation_name in ("xy", "yx"):
            for target_selector_name in TARGET_SELECTOR_NAMES:
                for target_field in FIELD_NAMES:
                    keys = [
                        contact_key(
                            transition,
                            contact_by_edge_id[int(transition["edge_id"])],
                            endpoint_by_id,
                            contact_axis_name=contact_axis_name,
                            orientation_name=orientation_name,
                            target_selector_name=target_selector_name,
                            target_field=target_field,
                        )
                        for transition in active_transitions
                    ]
                    source0_field = "source0_addr" if orientation_name == "xy" else "target_addr"
                    source1_field = "target_addr" if orientation_name == "xy" else "source0_addr"
                    row, counts = candidate_profile(
                        candidate_id=candidate_id,
                        library_name="contact_sample_slot",
                        local_candidate_id=local_candidate_id,
                        contact_axis_code=CONTACT_AXIS_CODES[contact_axis_name],
                        orientation_code=ORIENTATION_CODES[orientation_name],
                        source0_field_code=FIELD_CODES[source0_field],
                        source1_field_code=FIELD_CODES[source1_field],
                        target_selector_code=TARGET_SELECTOR_CODES[
                            target_selector_name
                        ],
                        target_field_code=FIELD_CODES[target_field],
                        keys=keys,
                        support_counts=support_counts,
                    )
                    candidate_rows.append(row)
                    counts_by_candidate[candidate_id] = counts
                    contact_candidate_ids.append(candidate_id)
                    candidate_id += 1
                    local_candidate_id += 1

    direct_rows = [
        row for row in candidate_rows if row["candidate_id"] in direct_candidate_ids
    ]
    contact_rows = [
        row for row in candidate_rows if row["candidate_id"] in contact_candidate_ids
    ]
    best_candidate = sorted(
        candidate_rows,
        key=lambda row: (
            -row["covered_transition_count"],
            -row["total_raw_match_count"],
            row["candidate_id"],
        ),
    )[0]
    best_direct = sorted(
        direct_rows,
        key=lambda row: (
            -row["covered_transition_count"],
            -row["total_raw_match_count"],
            row["candidate_id"],
        ),
    )[0]
    best_contact = sorted(
        contact_rows,
        key=lambda row: (
            -row["covered_transition_count"],
            -row["total_raw_match_count"],
            row["candidate_id"],
        ),
    )[0]

    direct_union = {
        active_id
        for row in direct_rows
        for active_id, count in enumerate(counts_by_candidate[row["candidate_id"]])
        if count > 0
    }
    contact_union = {
        active_id
        for row in contact_rows
        for active_id, count in enumerate(counts_by_candidate[row["candidate_id"]])
        if count > 0
    }
    mixed_union = direct_union | contact_union
    missing_transition_ids = [
        int(active_raw[index]["transition_id"])
        for index in range(len(active_raw))
        if index not in mixed_union
    ]

    cover_rows = []
    for active_index, active_row in enumerate(active_raw):
        direct_best_id, direct_best_count = best_count_for_transition(
            direct_rows, counts_by_candidate, active_index
        )
        contact_best_id, contact_best_count = best_count_for_transition(
            contact_rows, counts_by_candidate, active_index
        )
        mixed_flag = int(active_index in mixed_union)
        cover_rows.append(
            {
                "active_transition_id": int(active_row["active_transition_id"]),
                "transition_id": int(active_row["transition_id"]),
                "direct_covered_flag": int(active_index in direct_union),
                "contact_covered_flag": int(active_index in contact_union),
                "mixed_covered_flag": mixed_flag,
                "direct_best_candidate_id": direct_best_id,
                "direct_best_raw_match_count": direct_best_count,
                "contact_best_candidate_id": contact_best_id,
                "contact_best_raw_match_count": contact_best_count,
                "mixed_obstruction_flag": int(mixed_flag == 0),
            }
        )

    obs = {
        "input_report_count": 4,
        "input_certified_count": sum(
            int(certified(report))
            for report in (c59p3h, c59p3j, contact_lift, transition_sem)
        ),
        "active_transition_count": len(active_transitions),
        "direct_candidate_count": len(direct_rows),
        "contact_candidate_count": len(contact_rows),
        "mixed_candidate_count": len(candidate_rows),
        "full_candidate_count": sum(
            row["full_candidate_flag"] for row in candidate_rows
        ),
        "best_candidate_id": best_candidate["candidate_id"],
        "best_candidate_library_code": best_candidate["library_code"],
        "best_candidate_covered_transition_count": best_candidate[
            "covered_transition_count"
        ],
        "best_direct_candidate_id": best_direct["candidate_id"],
        "best_direct_covered_transition_count": best_direct[
            "covered_transition_count"
        ],
        "best_contact_candidate_id": best_contact["candidate_id"],
        "best_contact_covered_transition_count": best_contact[
            "covered_transition_count"
        ],
        "direct_union_covered_transition_count": len(direct_union),
        "contact_union_covered_transition_count": len(contact_union),
        "mixed_union_covered_transition_count": len(mixed_union),
        "mixed_union_uncovered_transition_count": len(active_transitions)
        - len(mixed_union),
        "missing_transition_id_count": len(missing_transition_ids),
        "operation_promoted_row_count": 0,
        "semantic_operation_flag": 0,
        "transition_composition_law_flag": 0,
        "physical_selector_axiom_flag": 0,
        "metric_derivation_flag": 0,
        "next_gap_code": GAP_CODES["transition_composition_law"],
    }
    gap_rows = [
        {
            "gap_id": GAP_CODES["direct_address_screen_input"],
            "gap_code": GAP_CODES["direct_address_screen_input"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["endpoint_projector_input"],
            "gap_code": GAP_CODES["endpoint_projector_input"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["contact_sample_slot_screen"],
            "gap_code": GAP_CODES["contact_sample_slot_screen"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["full_mixed_candidate_obstruction"],
            "gap_code": GAP_CODES["full_mixed_candidate_obstruction"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["mixed_union_partial_cover"],
            "gap_code": GAP_CODES["mixed_union_partial_cover"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["semantic_operation_rows_absent"],
            "gap_code": GAP_CODES["semantic_operation_rows_absent"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["transition_composition_law"],
            "gap_code": GAP_CODES["transition_composition_law"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 1,
        },
        {
            "gap_id": GAP_CODES["physical_selector_axiom"],
            "gap_code": GAP_CODES["physical_selector_axiom"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["metric_derivation"],
            "gap_code": GAP_CODES["metric_derivation"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
    ]
    obs_rows = [
        {"observable_id": index, "observable_code": OBS_CODES[name], "value": obs[name]}
        for index, name in enumerate(OBS_NAMES)
    ]
    return {
        "c59p3h": c59p3h,
        "c59p3j": c59p3j,
        "contact_lift": contact_lift,
        "transition_sem": transition_sem,
        "raw_tensor_path": raw_tensor_path,
        "triples": triples,
        "candidate_rows": candidate_rows,
        "cover_rows": cover_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "missing_transition_ids": missing_transition_ids,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    candidate_table = table_from_rows(CANDIDATE_COLUMNS, rows["candidate_rows"])
    cover_table = table_from_rows(COVER_COLUMNS, rows["cover_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "mixed_screen_shape_exact": obs["active_transition_count"] == 29
        and obs["direct_candidate_count"] == 108
        and obs["contact_candidate_count"] == 64
        and obs["mixed_candidate_count"] == 172,
        "no_full_candidate_in_mixed_screen": obs["full_candidate_count"] == 0,
        "best_candidate_profile_exact": obs["best_candidate_id"] == 8
        and obs["best_candidate_library_code"]
        == LIBRARY_CODES["direct_endpoint_field"]
        and obs["best_candidate_covered_transition_count"] == 15
        and obs["best_direct_candidate_id"] == 8
        and obs["best_direct_covered_transition_count"] == 15
        and obs["best_contact_candidate_id"] == 110
        and obs["best_contact_covered_transition_count"] == 11,
        "union_cover_profile_exact": obs["direct_union_covered_transition_count"]
        == 25
        and obs["contact_union_covered_transition_count"] == 18
        and obs["mixed_union_covered_transition_count"] == 26
        and obs["mixed_union_uncovered_transition_count"] == 3
        and rows["missing_transition_ids"] == [24, 38, 40],
        "operation_boundaries_preserved": obs["operation_promoted_row_count"] == 0
        and obs["semantic_operation_flag"] == 0
        and obs["transition_composition_law_flag"] == 0,
        "physical_boundaries_preserved": obs["physical_selector_axiom_flag"] == 0
        and obs["metric_derivation_flag"] == 0,
        "table_shapes_match": candidate_table.shape == (172, len(CANDIDATE_COLUMNS))
        and cover_table.shape == (29, len(COVER_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "mixed_contact_address_screen",
        "summary": {
            "active_transition_count": obs["active_transition_count"],
            "direct_candidate_count": obs["direct_candidate_count"],
            "contact_candidate_count": obs["contact_candidate_count"],
            "mixed_candidate_count": obs["mixed_candidate_count"],
            "full_candidate_count": obs["full_candidate_count"],
            "best_candidate_id": obs["best_candidate_id"],
            "best_candidate_covered_transition_count": obs[
                "best_candidate_covered_transition_count"
            ],
            "best_contact_candidate_id": obs["best_contact_candidate_id"],
            "best_contact_covered_transition_count": obs[
                "best_contact_covered_transition_count"
            ],
            "mixed_union_covered_transition_count": obs[
                "mixed_union_covered_transition_count"
            ],
            "mixed_union_uncovered_transition_count": obs[
                "mixed_union_uncovered_transition_count"
            ],
            "missing_transition_ids": rows["missing_transition_ids"],
            "operation_promoted_row_count": obs["operation_promoted_row_count"],
        },
        "library_code_map": {str(value): key for key, value in LIBRARY_CODES.items()},
        "contact_axis_code_map": {
            str(value): key for key, value in CONTACT_AXIS_CODES.items()
        },
        "orientation_code_map": {
            str(value): key for key, value in ORIENTATION_CODES.items()
        },
        "field_code_map": {str(value): key for key, value in FIELD_CODES.items()},
        "target_selector_code_map": {
            str(value): key for key, value in TARGET_SELECTOR_CODES.items()
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "candidate_table_sha256": sha_array(candidate_table),
        "candidate_text_sha256": sha_text(
            csv_text(CANDIDATE_COLUMNS, rows["candidate_rows"])
        ),
        "cover_table_sha256": sha_array(cover_table),
        "cover_text_sha256": sha_text(csv_text(COVER_COLUMNS, rows["cover_rows"])),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    c59p3k = {
        "schema": "long.c59p3k@1",
        "object": "mixed_contact_address_screen",
        "status": STATUS if all(checks.values()) else "LONG_C59P3K_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.c59p3k.report@1",
        "status": c59p3k["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_c59p3k widens the active address-map screen beyond "
            "long_c59p3h by adding a 64-row contact-sample endpoint-slot "
            "family to the 108 direct endpoint-field candidates. The widened "
            "172-candidate finite grammar still has zero candidates covering "
            "all 29 active transition ids. Its union covers 26 transitions and "
            "leaves transition ids 24, 38, and 40 uncovered, so it does not "
            "produce semantic operation rows."
        ),
        "stage_protocol": {
            "draft": "read long_c59p3h, long_c59p3j, long_contact_lift, long_transition_sem, active transition rows, transition rows, endpoint rows, contact rows, and the raw tensor",
            "witness": "emit mixed candidate rows, per-transition union cover rows, gaps, and observables",
            "coherence": "check candidate counts, best direct/contact profiles, union coverage, missing transition ids, and preserved operation/physical gaps",
            "closure": "certify the bounded mixed direct/contact address screen as still insufficient for a transition composition law",
            "emit": "write long_c59p3k artifacts and verifier hook",
        },
        "inputs": {
            "long_c59p3h": input_entry(
                LONG_C59P3H,
                {
                    "status": rows["c59p3h"].get("status"),
                    "certificate_sha256": rows["c59p3h"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_c59p3j": input_entry(
                LONG_C59P3J,
                {
                    "status": rows["c59p3j"].get("status"),
                    "certificate_sha256": rows["c59p3j"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_contact_lift": input_entry(
                LONG_CONTACT_LIFT,
                {
                    "status": rows["contact_lift"].get("status"),
                    "certificate_sha256": rows["contact_lift"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_contact_contact": input_entry(LONG_CONTACT_CONTACT),
            "long_transition_sem": input_entry(
                LONG_TRANSITION_SEM,
                {
                    "status": rows["transition_sem"].get("status"),
                    "certificate_sha256": rows["transition_sem"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_c59p3g_transition_schema": input_entry(
                LONG_C59P3G_TRANSITION_SCHEMA
            ),
            "long_transition_csv": input_entry(LONG_TRANSITION_CSV),
            "long_transition_endpoint": input_entry(LONG_TRANSITION_ENDPOINT),
            "raw_index": input_entry(RAW_INDEX),
            "raw_tensor": input_entry(
                rows["raw_tensor_path"],
                {
                    "row_count": int(rows["triples"].shape[0]),
                    "column_count": int(rows["triples"].shape[1]),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "c59p3k": relpath(OUT_DIR / "c59p3k.json"),
            "candidate_csv": relpath(OUT_DIR / "candidate.csv"),
            "cover_csv": relpath(OUT_DIR / "cover.csv"),
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
                "the widened mixed screen has 172 candidates: 108 direct endpoint-field candidates and 64 contact-sample endpoint-slot candidates",
                "zero mixed-screen candidates cover all 29 active transition ids",
                "the best direct candidate remains id 8 and covers 15 active transitions",
                "the best contact candidate is id 110 and covers 11 active transitions",
                "the mixed union covers 26 active transitions and leaves transition ids 24, 38, and 40 uncovered",
                "the widened screen produces zero operation-promoted rows",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "absence of every possible address grammar outside this bounded 172-candidate screen",
                "a transition composition law",
                "new semantic operation rows",
                "a physical selector axiom",
                "a four-dimensional metric reduction",
                "a physical field equation",
            ],
        },
        "next_highest_yield_item": (
            "Use the three uncovered transition ids 24, 38, and 40 as the next "
            "bounded obstruction target: either find the missing composite "
            "address grammar for those transitions or certify a transition-local "
            "schema gap."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.c59p3k.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.c59p3k.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "c59p3k": c59p3k,
        "candidate_csv": csv_text(CANDIDATE_COLUMNS, rows["candidate_rows"]),
        "cover_csv": csv_text(COVER_COLUMNS, rows["cover_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "candidate_table": candidate_table,
        "cover_table": cover_table,
        "gap_table": gap_table,
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
    write_json(OUT_DIR / "c59p3k.json", payloads["c59p3k"])
    (OUT_DIR / "candidate.csv").write_text(
        payloads["candidate_csv"], encoding="utf-8"
    )
    (OUT_DIR / "cover.csv").write_text(payloads["cover_csv"], encoding="utf-8")
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        candidate_table=payloads["candidate_table"],
        cover_table=payloads["cover_table"],
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
                "summary": report["witness"]["summary"],
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
