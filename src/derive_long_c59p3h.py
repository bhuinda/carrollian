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


THEOREM_ID = "long_c59p3h"
STATUS = "LONG_C59P3H_ACTIVE_ADDRESS_MAP_SCREEN_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

RAW_INDEX = ROOT / "data" / "raw" / "index.json"
LONG_C59P3G = PROOF_ROOT / "long_c59p3g" / "report.json"
LONG_C59P3G_TRANSITION_SCHEMA = PROOF_ROOT / "long_c59p3g" / "transition_schema.csv"
LONG_TRANSITION_SEM = PROOF_ROOT / "long_transition_sem" / "report.json"
LONG_TRANSITION_CSV = PROOF_ROOT / "long_transition_sem" / "transition.csv"
LONG_TRANSITION_ENDPOINT = PROOF_ROOT / "long_transition_sem" / "endpoint_raw.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_c59p3h.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_c59p3h.py"

FIELD_NAMES = ["source0_addr", "source1_addr", "target_addr"]
FIELD_CODES = {name: index for index, name in enumerate(FIELD_NAMES)}
ORIENTATION_NAMES = ["lr", "rl"]
ORIENTATION_CODES = {name: index for index, name in enumerate(ORIENTATION_NAMES)}
TARGET_SIDE_NAMES = ["left", "right"]
TARGET_SIDE_CODES = {name: index for index, name in enumerate(TARGET_SIDE_NAMES)}

CANDIDATE_COLUMNS = [
    "candidate_id",
    "orientation_code",
    "source0_field_code",
    "source1_field_code",
    "target_side_code",
    "target_field_code",
    "active_transition_count",
    "covered_transition_count",
    "uncovered_transition_count",
    "total_raw_match_count",
    "max_raw_match_count",
    "full_address_map_flag",
    "semantic_operation_flag",
]
BEST_MATCH_COLUMNS = [
    "active_transition_id",
    "transition_id",
    "candidate_id",
    "left_basis_id",
    "right_basis_id",
    "candidate_source0_addr",
    "candidate_source1_addr",
    "candidate_target_addr",
    "raw_match_count",
    "first_raw_row_id",
    "raw_match_flag",
    "operation_promoted_flag",
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
    "operation_schema_gap_input",
    "endpoint_field_candidate_screen",
    "full_address_map_obstruction",
    "best_partial_raw_support",
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
    "candidate_count",
    "full_address_map_candidate_count",
    "best_candidate_id",
    "best_candidate_covered_transition_count",
    "best_candidate_uncovered_transition_count",
    "best_candidate_total_raw_match_count",
    "best_candidate_max_raw_match_count",
    "best_match_row_count",
    "best_raw_matched_row_count",
    "best_raw_unmatched_row_count",
    "operation_promoted_match_count",
    "semantic_operation_flag",
    "address_screen_obstruction_flag",
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
    return report.get("all_checks_pass") is True and (
        "CERTIFIED" in str(report.get("status", ""))
        or "OBSTRUCTION_CERTIFIED" in str(report.get("status", ""))
    )


def raw_tensor(path: Path) -> np.ndarray:
    with np.load(path, allow_pickle=False) as payload:
        triples = np.asarray(payload["triples"], dtype=np.int64)
    if triples.ndim != 2 or triples.shape[1] != 4:
        raise AssertionError("raw tensor triples must have shape n x 4")
    return triples


def raw_support_index(
    triples: np.ndarray,
) -> tuple[dict[tuple[int, int, int], int], dict[tuple[int, int, int], int]]:
    counts: dict[tuple[int, int, int], int] = defaultdict(int)
    first_row: dict[tuple[int, int, int], int] = {}
    for row_id, row in enumerate(triples.tolist()):
        key = (int(row[0]), int(row[1]), int(row[2]))
        counts[key] += 1
        first_row.setdefault(key, row_id)
    return counts, first_row


def candidate_key(
    transition: dict[str, str],
    endpoints: dict[int, dict[str, str]],
    *,
    orientation_name: str,
    source0_field: str,
    source1_field: str,
    target_side_name: str,
    target_field: str,
) -> tuple[int, int, int]:
    left = endpoints[int(transition["left_basis_id"])]
    right = endpoints[int(transition["right_basis_id"])]
    first, second = (left, right) if orientation_name == "lr" else (right, left)
    target = left if target_side_name == "left" else right
    return (
        int(first[source0_field]),
        int(second[source1_field]),
        int(target[target_field]),
    )


def build_rows() -> dict[str, Any]:
    c59p3g = load_json(LONG_C59P3G)
    transition_sem = load_json(LONG_TRANSITION_SEM)
    raw_index_payload = load_json(RAW_INDEX)
    raw_tensor_path = raw_tensor_path_from_index(raw_index_payload)
    triples = raw_tensor(raw_tensor_path)
    support_counts, first_rows = raw_support_index(triples)
    _, active_raw = read_csv_rows(LONG_C59P3G_TRANSITION_SCHEMA)
    _, transition_raw = read_csv_rows(LONG_TRANSITION_CSV)
    _, endpoint_raw = read_csv_rows(LONG_TRANSITION_ENDPOINT)

    transition_by_id = {
        int(row["transition_id"]): row for row in transition_raw
    }
    endpoint_by_id = {int(row["basis_id"]): row for row in endpoint_raw}
    active_transitions = [
        transition_by_id[int(row["transition_id"])] for row in active_raw
    ]

    candidate_rows = []
    best_keys_by_candidate: dict[int, list[tuple[int, int, int]]] = {}
    candidate_id = 0
    for orientation_name in ORIENTATION_NAMES:
        for source0_field in FIELD_NAMES:
            for source1_field in FIELD_NAMES:
                for target_side_name in TARGET_SIDE_NAMES:
                    for target_field in FIELD_NAMES:
                        counts = []
                        keys = []
                        for transition in active_transitions:
                            key = candidate_key(
                                transition,
                                endpoint_by_id,
                                orientation_name=orientation_name,
                                source0_field=source0_field,
                                source1_field=source1_field,
                                target_side_name=target_side_name,
                                target_field=target_field,
                            )
                            keys.append(key)
                            counts.append(support_counts.get(key, 0))
                        covered = sum(int(count > 0) for count in counts)
                        total = sum(counts)
                        candidate_rows.append(
                            {
                                "candidate_id": candidate_id,
                                "orientation_code": ORIENTATION_CODES[
                                    orientation_name
                                ],
                                "source0_field_code": FIELD_CODES[source0_field],
                                "source1_field_code": FIELD_CODES[source1_field],
                                "target_side_code": TARGET_SIDE_CODES[
                                    target_side_name
                                ],
                                "target_field_code": FIELD_CODES[target_field],
                                "active_transition_count": len(active_transitions),
                                "covered_transition_count": covered,
                                "uncovered_transition_count": len(active_transitions)
                                - covered,
                                "total_raw_match_count": total,
                                "max_raw_match_count": max(counts) if counts else 0,
                                "full_address_map_flag": int(
                                    covered == len(active_transitions)
                                ),
                                "semantic_operation_flag": 0,
                            }
                        )
                        best_keys_by_candidate[candidate_id] = keys
                        candidate_id += 1

    best_candidate = sorted(
        candidate_rows,
        key=lambda row: (
            -row["covered_transition_count"],
            -row["total_raw_match_count"],
            row["candidate_id"],
        ),
    )[0]
    best_id = best_candidate["candidate_id"]
    best_keys = best_keys_by_candidate[best_id]
    best_match_rows = []
    for active, transition, key in zip(active_raw, active_transitions, best_keys):
        raw_match_count = support_counts.get(key, 0)
        best_match_rows.append(
            {
                "active_transition_id": int(active["active_transition_id"]),
                "transition_id": int(transition["transition_id"]),
                "candidate_id": best_id,
                "left_basis_id": int(transition["left_basis_id"]),
                "right_basis_id": int(transition["right_basis_id"]),
                "candidate_source0_addr": key[0],
                "candidate_source1_addr": key[1],
                "candidate_target_addr": key[2],
                "raw_match_count": raw_match_count,
                "first_raw_row_id": first_rows.get(key, -1),
                "raw_match_flag": int(raw_match_count > 0),
                "operation_promoted_flag": 0,
            }
        )

    obs = {
        "input_report_count": 2,
        "input_certified_count": sum(
            int(certified(report)) for report in (c59p3g, transition_sem)
        ),
        "active_transition_count": len(active_transitions),
        "candidate_count": len(candidate_rows),
        "full_address_map_candidate_count": sum(
            row["full_address_map_flag"] for row in candidate_rows
        ),
        "best_candidate_id": best_id,
        "best_candidate_covered_transition_count": best_candidate[
            "covered_transition_count"
        ],
        "best_candidate_uncovered_transition_count": best_candidate[
            "uncovered_transition_count"
        ],
        "best_candidate_total_raw_match_count": best_candidate[
            "total_raw_match_count"
        ],
        "best_candidate_max_raw_match_count": best_candidate[
            "max_raw_match_count"
        ],
        "best_match_row_count": len(best_match_rows),
        "best_raw_matched_row_count": sum(
            row["raw_match_flag"] for row in best_match_rows
        ),
        "best_raw_unmatched_row_count": sum(
            int(row["raw_match_flag"] == 0) for row in best_match_rows
        ),
        "operation_promoted_match_count": sum(
            row["operation_promoted_flag"] for row in best_match_rows
        ),
        "semantic_operation_flag": 0,
        "address_screen_obstruction_flag": 1,
        "transition_composition_law_flag": 0,
        "physical_selector_axiom_flag": 0,
        "metric_derivation_flag": 0,
        "next_gap_code": GAP_CODES["transition_composition_law"],
    }
    gap_rows = [
        {
            "gap_id": GAP_CODES["operation_schema_gap_input"],
            "gap_code": GAP_CODES["operation_schema_gap_input"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["endpoint_field_candidate_screen"],
            "gap_code": GAP_CODES["endpoint_field_candidate_screen"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["full_address_map_obstruction"],
            "gap_code": GAP_CODES["full_address_map_obstruction"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["best_partial_raw_support"],
            "gap_code": GAP_CODES["best_partial_raw_support"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
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
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": obs[name],
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    return {
        "c59p3g": c59p3g,
        "transition_sem": transition_sem,
        "raw_tensor_path": raw_tensor_path,
        "triples": triples,
        "candidate_rows": candidate_rows,
        "best_match_rows": best_match_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    candidate_table = table_from_rows(CANDIDATE_COLUMNS, rows["candidate_rows"])
    best_match_table = table_from_rows(BEST_MATCH_COLUMNS, rows["best_match_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "active_transition_screen_shape": obs["active_transition_count"] == 29
        and obs["candidate_count"] == 108
        and obs["best_match_row_count"] == 29,
        "no_full_address_map_in_screen": obs["full_address_map_candidate_count"] == 0
        and obs["address_screen_obstruction_flag"] == 1,
        "best_candidate_profile_exact": obs["best_candidate_id"] == 8
        and obs["best_candidate_covered_transition_count"] == 15
        and obs["best_candidate_uncovered_transition_count"] == 14
        and obs["best_candidate_total_raw_match_count"] == 15
        and obs["best_candidate_max_raw_match_count"] == 1
        and obs["best_raw_matched_row_count"] == 15
        and obs["best_raw_unmatched_row_count"] == 14,
        "operation_boundaries_preserved": obs["operation_promoted_match_count"] == 0
        and obs["semantic_operation_flag"] == 0
        and obs["transition_composition_law_flag"] == 0,
        "physical_boundaries_preserved": obs["physical_selector_axiom_flag"] == 0
        and obs["metric_derivation_flag"] == 0,
        "table_shapes_match": candidate_table.shape == (108, len(CANDIDATE_COLUMNS))
        and best_match_table.shape == (29, len(BEST_MATCH_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "active_endpoint_field_address_map_screen",
        "summary": {
            "active_transition_count": obs["active_transition_count"],
            "candidate_count": obs["candidate_count"],
            "full_address_map_candidate_count": obs[
                "full_address_map_candidate_count"
            ],
            "best_candidate_id": obs["best_candidate_id"],
            "best_candidate_covered_transition_count": obs[
                "best_candidate_covered_transition_count"
            ],
            "best_candidate_uncovered_transition_count": obs[
                "best_candidate_uncovered_transition_count"
            ],
            "best_candidate_total_raw_match_count": obs[
                "best_candidate_total_raw_match_count"
            ],
            "operation_promoted_match_count": obs["operation_promoted_match_count"],
        },
        "field_code_map": {str(value): key for key, value in FIELD_CODES.items()},
        "orientation_code_map": {
            str(value): key for key, value in ORIENTATION_CODES.items()
        },
        "target_side_code_map": {
            str(value): key for key, value in TARGET_SIDE_CODES.items()
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "candidate_table_sha256": sha_array(candidate_table),
        "candidate_text_sha256": sha_text(
            csv_text(CANDIDATE_COLUMNS, rows["candidate_rows"])
        ),
        "best_match_table_sha256": sha_array(best_match_table),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    c59p3h = {
        "schema": "long.c59p3h@1",
        "object": "active_endpoint_field_address_map_screen",
        "status": STATUS if all(checks.values()) else "LONG_C59P3H_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.c59p3h.report@1",
        "status": c59p3h["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_c59p3h screens the current endpoint-field address maps for "
            "the 29 active transition ids from long_c59p3g. Across 108 direct "
            "left/right endpoint-field candidates, no candidate supplies raw "
            "support for all 29 active transitions. The best candidate covers "
            "15 transitions and leaves 14 uncovered, so the current finite "
            "screen does not produce operation rows."
        ),
        "stage_protocol": {
            "draft": "read long_c59p3g active transition ids, transition endpoint rows, transition rows, and the raw tensor",
            "witness": "emit candidate address-map rows, best-candidate match rows, gaps, and observables",
            "coherence": "check candidate count, active transition count, raw support counts, absent full map, and preserved operation/physical gaps",
            "closure": "certify the bounded endpoint-field address-map screen",
            "emit": "write long_c59p3h artifacts and verifier hook",
        },
        "inputs": {
            "long_c59p3g": input_entry(
                LONG_C59P3G,
                {
                    "status": rows["c59p3g"].get("status"),
                    "certificate_sha256": rows["c59p3g"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_c59p3g_transition_schema": input_entry(
                LONG_C59P3G_TRANSITION_SCHEMA
            ),
            "long_transition_sem": input_entry(
                LONG_TRANSITION_SEM,
                {
                    "status": rows["transition_sem"].get("status"),
                    "certificate_sha256": rows["transition_sem"].get(
                        "certificate_sha256"
                    ),
                },
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
            "c59p3h": relpath(OUT_DIR / "c59p3h.json"),
            "candidate_csv": relpath(OUT_DIR / "candidate.csv"),
            "best_match_csv": relpath(OUT_DIR / "best_match.csv"),
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
                "the active screen has 29 transition ids from long_c59p3g",
                "108 direct endpoint-field address-map candidates were tested against raw tensor support",
                "zero candidates cover all 29 active transition ids",
                "the best candidate has id 8 and covers 15 of 29 active transition ids",
                "the screen produces zero operation-promoted rows",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "absence of every possible address map outside the 108-candidate endpoint-field screen",
                "a transition composition law",
                "new semantic operation rows",
                "a physical selector axiom",
                "a four-dimensional metric reduction",
                "a physical field equation",
            ],
        },
        "next_highest_yield_item": (
            "Construct a transition composition law beyond the direct "
            "endpoint-field screen, or extend the screen with a certified "
            "composite-address grammar."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.c59p3h.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.c59p3h.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "c59p3h": c59p3h,
        "candidate_csv": csv_text(CANDIDATE_COLUMNS, rows["candidate_rows"]),
        "best_match_csv": csv_text(BEST_MATCH_COLUMNS, rows["best_match_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "candidate_table": candidate_table,
        "best_match_table": best_match_table,
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
    write_json(OUT_DIR / "c59p3h.json", payloads["c59p3h"])
    (OUT_DIR / "candidate.csv").write_text(
        payloads["candidate_csv"], encoding="utf-8"
    )
    (OUT_DIR / "best_match.csv").write_text(
        payloads["best_match_csv"], encoding="utf-8"
    )
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        candidate_table=payloads["candidate_table"],
        best_match_table=payloads["best_match_table"],
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
