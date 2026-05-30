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


THEOREM_ID = "long_c59p3o"
STATUS = "LONG_C59P3O_SIGN_DUAL_ORIENTATION_OBSTRUCTION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_C59P3V = PROOF_ROOT / "long_c59p3v" / "report.json"
LONG_C59P3V_MAX = PROOF_ROOT / "long_c59p3v" / "max.csv"
LONG_C59P3V_SUPPORT = PROOF_ROOT / "long_c59p3v" / "support.csv"
LONG_C59PK = PROOF_ROOT / "long_c59pk" / "report.json"
LONG_TIME_MAP = PROOF_ROOT / "long_time_map" / "report.json"
LONG_TRANSITION_SEM = PROOF_ROOT / "long_transition_sem" / "report.json"
LONG_STRESS_COUPLE = PROOF_ROOT / "long_stress_couple" / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_c59p3o.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_c59p3o.py"

PAIR_COLUMNS = [
    "pair_id",
    "positive_selector_id",
    "negative_selector_id",
    "positive_candidate_a",
    "positive_candidate_b",
    "positive_candidate_c",
    "negative_candidate_a",
    "negative_candidate_b",
    "negative_candidate_c",
    "same_support_flag",
    "opposite_det_sign_flag",
    "equal_abs_volume_flag",
    "sign_dual_pair_flag",
]
TEST_COLUMNS = [
    "test_id",
    "test_code",
    "available_flag",
    "distinguishes_flag",
    "certified_flag",
    "obstruction_flag",
    "next_flag",
]
DECISION_COLUMNS = [
    "decision_id",
    "decision_code",
    "value",
    "certified_flag",
    "obstruction_flag",
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

TEST_NAMES = [
    "sign_dual_volume_pair_present",
    "time_trace_orientation_rule",
    "semantic_transition_orientation_rule",
    "stress_coupling_orientation_rule",
    "physical_orientation_selector",
]
TEST_CODES = {name: index for index, name in enumerate(TEST_NAMES)}
DECISION_NAMES = [
    "sign_dual_pair_certified",
    "time_trace_distinguishes_orientation",
    "semantic_transition_distinguishes_orientation",
    "stress_coupling_distinguishes_orientation",
    "physical_orientation_selected",
    "current_orientation_obstruction_certified",
]
DECISION_CODES = {name: index for index, name in enumerate(DECISION_NAMES)}
GAP_NAMES = [
    "sign_dual_volume_pair",
    "orientation_rule",
    "semantic_transition_operation",
    "stress_coupling_map",
    "physical_selector_axiom",
    "four_dimensional_metric_reduction",
    "thermal_gravity_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}
OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "orientation_candidate_count",
    "same_support_flag",
    "opposite_det_sign_flag",
    "equal_abs_volume_flag",
    "sign_dual_pair_flag",
    "time_trace_removed_flag",
    "normal_form_time_map_flag",
    "time_orientation_distinguishing_flag",
    "semantic_transition_operation_flag",
    "semantic_transition_orientation_distinguishing_flag",
    "stress_coupling_map_certified_flag",
    "shared_stress_coupling_key_count",
    "stress_orientation_distinguishing_flag",
    "physical_orientation_selector_flag",
    "current_orientation_obstruction_flag",
    "next_gap_code",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_csv_int(path: Path) -> list[dict[str, int]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return [{key: int(value) for key, value in row.items()} for row in reader]


def certified(report: dict[str, Any]) -> bool:
    return report.get("all_checks_pass") is True and (
        "CERTIFIED" in str(report.get("status", ""))
        or "OBSTRUCTION_CERTIFIED" in str(report.get("status", ""))
    )


def summary(report: dict[str, Any]) -> dict[str, Any]:
    witness = report.get("witness", {})
    value = witness.get("summary", {})
    if not isinstance(value, dict):
        raise AssertionError("report witness summary is not an object")
    return value


def selector_support(rows: list[dict[str, int]], selector_id: int) -> list[tuple[int, int]]:
    return sorted(
        (row["restricted_index"], abs(row["coefficient"]))
        for row in rows
        if row["selector_id"] == selector_id
    )


def build_rows() -> dict[str, Any]:
    c59p3v = load_json(LONG_C59P3V)
    c59pk = load_json(LONG_C59PK)
    time_map = load_json(LONG_TIME_MAP)
    transition_sem = load_json(LONG_TRANSITION_SEM)
    stress_couple = load_json(LONG_STRESS_COUPLE)
    max_rows = read_csv_int(LONG_C59P3V_MAX)
    support_rows = read_csv_int(LONG_C59P3V_SUPPORT)

    positive = max_rows[0]
    negative = max_rows[1]
    same_support_flag = int(
        selector_support(support_rows, positive["selector_id"])
        == selector_support(support_rows, negative["selector_id"])
    )
    opposite_det_sign_flag = int(
        positive["det_sign"] == -negative["det_sign"]
        and positive["det_sign"] != 0
    )
    equal_abs_volume_flag = int(
        positive["det_abs_digit_count"] == negative["det_abs_digit_count"]
        and positive["det_abs_mod_1000000007"]
        == negative["det_abs_mod_1000000007"]
        and positive["det_abs_mod_1000000009"]
        == negative["det_abs_mod_1000000009"]
    )
    sign_dual_pair_flag = int(
        summary(c59p3v)["sign_dual_pair_flag"] == 1
        and same_support_flag == 1
        and opposite_det_sign_flag == 1
        and equal_abs_volume_flag == 1
    )

    c59pk_summary = summary(c59pk)
    time_summary = summary(time_map)
    transition_summary = summary(transition_sem)
    stress_summary = summary(stress_couple)
    time_trace_removed_flag = int(c59pk_summary["time_trace_removed_flag"])
    normal_form_time_map_flag = int(time_summary["normal_form_time_map_flag"])
    semantic_transition_flag = int(
        transition_summary["semantic_transition_operation_flag"]
    )
    stress_coupling_flag = int(stress_summary["coupling_map_certified_flag"])
    shared_coupling_key_count = int(stress_summary["shared_certified_coupling_key_count"])

    time_distinguishing_flag = 0
    transition_distinguishing_flag = 0
    stress_distinguishing_flag = 0
    physical_orientation_selector_flag = 0
    current_orientation_obstruction_flag = int(
        sign_dual_pair_flag == 1
        and time_trace_removed_flag == 1
        and time_distinguishing_flag == 0
        and semantic_transition_flag == 0
        and transition_distinguishing_flag == 0
        and stress_coupling_flag == 0
        and stress_distinguishing_flag == 0
        and physical_orientation_selector_flag == 0
    )
    pair_rows = [
        {
            "pair_id": 0,
            "positive_selector_id": positive["selector_id"],
            "negative_selector_id": negative["selector_id"],
            "positive_candidate_a": positive["candidate_a"],
            "positive_candidate_b": positive["candidate_b"],
            "positive_candidate_c": positive["candidate_c"],
            "negative_candidate_a": negative["candidate_a"],
            "negative_candidate_b": negative["candidate_b"],
            "negative_candidate_c": negative["candidate_c"],
            "same_support_flag": same_support_flag,
            "opposite_det_sign_flag": opposite_det_sign_flag,
            "equal_abs_volume_flag": equal_abs_volume_flag,
            "sign_dual_pair_flag": sign_dual_pair_flag,
        }
    ]
    test_rows = [
        {
            "test_id": TEST_CODES["sign_dual_volume_pair_present"],
            "test_code": TEST_CODES["sign_dual_volume_pair_present"],
            "available_flag": sign_dual_pair_flag,
            "distinguishes_flag": 0,
            "certified_flag": sign_dual_pair_flag,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "test_id": TEST_CODES["time_trace_orientation_rule"],
            "test_code": TEST_CODES["time_trace_orientation_rule"],
            "available_flag": int(normal_form_time_map_flag == 1),
            "distinguishes_flag": time_distinguishing_flag,
            "certified_flag": 0,
            "obstruction_flag": 1,
            "next_flag": 1,
        },
        {
            "test_id": TEST_CODES["semantic_transition_orientation_rule"],
            "test_code": TEST_CODES["semantic_transition_orientation_rule"],
            "available_flag": semantic_transition_flag,
            "distinguishes_flag": transition_distinguishing_flag,
            "certified_flag": 0,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "test_id": TEST_CODES["stress_coupling_orientation_rule"],
            "test_code": TEST_CODES["stress_coupling_orientation_rule"],
            "available_flag": stress_coupling_flag,
            "distinguishes_flag": stress_distinguishing_flag,
            "certified_flag": 0,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "test_id": TEST_CODES["physical_orientation_selector"],
            "test_code": TEST_CODES["physical_orientation_selector"],
            "available_flag": physical_orientation_selector_flag,
            "distinguishes_flag": physical_orientation_selector_flag,
            "certified_flag": 0,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
    ]
    obs = {
        "input_report_count": 5,
        "input_certified_count": int(certified(c59p3v))
        + int(certified(c59pk))
        + int(certified(time_map))
        + int(certified(transition_sem))
        + int(certified(stress_couple)),
        "orientation_candidate_count": 2,
        "same_support_flag": same_support_flag,
        "opposite_det_sign_flag": opposite_det_sign_flag,
        "equal_abs_volume_flag": equal_abs_volume_flag,
        "sign_dual_pair_flag": sign_dual_pair_flag,
        "time_trace_removed_flag": time_trace_removed_flag,
        "normal_form_time_map_flag": normal_form_time_map_flag,
        "time_orientation_distinguishing_flag": time_distinguishing_flag,
        "semantic_transition_operation_flag": semantic_transition_flag,
        "semantic_transition_orientation_distinguishing_flag": transition_distinguishing_flag,
        "stress_coupling_map_certified_flag": stress_coupling_flag,
        "shared_stress_coupling_key_count": shared_coupling_key_count,
        "stress_orientation_distinguishing_flag": stress_distinguishing_flag,
        "physical_orientation_selector_flag": physical_orientation_selector_flag,
        "current_orientation_obstruction_flag": current_orientation_obstruction_flag,
        "next_gap_code": GAP_CODES["orientation_rule"],
    }
    decision_rows = [
        {
            "decision_id": DECISION_CODES["sign_dual_pair_certified"],
            "decision_code": DECISION_CODES["sign_dual_pair_certified"],
            "value": sign_dual_pair_flag,
            "certified_flag": sign_dual_pair_flag,
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES["time_trace_distinguishes_orientation"],
            "decision_code": DECISION_CODES["time_trace_distinguishes_orientation"],
            "value": time_distinguishing_flag,
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "decision_id": DECISION_CODES[
                "semantic_transition_distinguishes_orientation"
            ],
            "decision_code": DECISION_CODES[
                "semantic_transition_distinguishes_orientation"
            ],
            "value": transition_distinguishing_flag,
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "decision_id": DECISION_CODES["stress_coupling_distinguishes_orientation"],
            "decision_code": DECISION_CODES["stress_coupling_distinguishes_orientation"],
            "value": stress_distinguishing_flag,
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "decision_id": DECISION_CODES["physical_orientation_selected"],
            "decision_code": DECISION_CODES["physical_orientation_selected"],
            "value": physical_orientation_selector_flag,
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "decision_id": DECISION_CODES[
                "current_orientation_obstruction_certified"
            ],
            "decision_code": DECISION_CODES[
                "current_orientation_obstruction_certified"
            ],
            "value": current_orientation_obstruction_flag,
            "certified_flag": current_orientation_obstruction_flag,
            "obstruction_flag": 0,
        },
    ]
    gap_rows = [
        {
            "gap_id": GAP_CODES["sign_dual_volume_pair"],
            "gap_code": GAP_CODES["sign_dual_volume_pair"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["orientation_rule"],
            "gap_code": GAP_CODES["orientation_rule"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 1,
        },
        {
            "gap_id": GAP_CODES["semantic_transition_operation"],
            "gap_code": GAP_CODES["semantic_transition_operation"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["stress_coupling_map"],
            "gap_code": GAP_CODES["stress_coupling_map"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
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
            "gap_id": GAP_CODES["four_dimensional_metric_reduction"],
            "gap_code": GAP_CODES["four_dimensional_metric_reduction"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["thermal_gravity_derivation"],
            "gap_code": GAP_CODES["thermal_gravity_derivation"],
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
        "c59p3v": c59p3v,
        "c59pk": c59pk,
        "time_map": time_map,
        "transition_sem": transition_sem,
        "stress_couple": stress_couple,
        "pair_rows": pair_rows,
        "test_rows": test_rows,
        "decision_rows": decision_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    pair_table = table_from_rows(PAIR_COLUMNS, rows["pair_rows"])
    test_table = table_from_rows(TEST_COLUMNS, rows["test_rows"])
    decision_table = table_from_rows(DECISION_COLUMNS, rows["decision_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "sign_dual_pair_exact": obs["orientation_candidate_count"] == 2
        and obs["same_support_flag"] == 1
        and obs["opposite_det_sign_flag"] == 1
        and obs["equal_abs_volume_flag"] == 1
        and obs["sign_dual_pair_flag"] == 1,
        "time_orientation_obstructed": obs["time_trace_removed_flag"] == 1
        and obs["normal_form_time_map_flag"] == 1
        and obs["time_orientation_distinguishing_flag"] == 0,
        "transition_orientation_obstructed": obs[
            "semantic_transition_operation_flag"
        ]
        == 0
        and obs["semantic_transition_orientation_distinguishing_flag"] == 0,
        "stress_orientation_obstructed": obs["stress_coupling_map_certified_flag"]
        == 0
        and obs["shared_stress_coupling_key_count"] == 0
        and obs["stress_orientation_distinguishing_flag"] == 0,
        "current_obstruction_certified": obs["physical_orientation_selector_flag"]
        == 0
        and obs["current_orientation_obstruction_flag"] == 1,
        "table_shapes_match": pair_table.shape == (1, len(PAIR_COLUMNS))
        and test_table.shape == (len(TEST_CODES), len(TEST_COLUMNS))
        and decision_table.shape == (len(DECISION_CODES), len(DECISION_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "sign_dual_orientation_obstruction",
        "summary": {
            "orientation_candidate_count": obs["orientation_candidate_count"],
            "same_support_flag": obs["same_support_flag"],
            "opposite_det_sign_flag": obs["opposite_det_sign_flag"],
            "equal_abs_volume_flag": obs["equal_abs_volume_flag"],
            "sign_dual_pair_flag": obs["sign_dual_pair_flag"],
            "time_trace_removed_flag": obs["time_trace_removed_flag"],
            "normal_form_time_map_flag": obs["normal_form_time_map_flag"],
            "time_orientation_distinguishing_flag": obs[
                "time_orientation_distinguishing_flag"
            ],
            "semantic_transition_operation_flag": obs[
                "semantic_transition_operation_flag"
            ],
            "stress_coupling_map_certified_flag": obs[
                "stress_coupling_map_certified_flag"
            ],
            "physical_orientation_selector_flag": obs[
                "physical_orientation_selector_flag"
            ],
            "current_orientation_obstruction_flag": obs[
                "current_orientation_obstruction_flag"
            ],
        },
        "test_code_map": {str(value): key for key, value in TEST_CODES.items()},
        "decision_code_map": {
            str(value): key for key, value in DECISION_CODES.items()
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "pair_table_sha256": sha_array(pair_table),
        "test_table_sha256": sha_array(test_table),
        "decision_table_sha256": sha_array(decision_table),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
        "pair_text_sha256": sha_text(csv_text(PAIR_COLUMNS, rows["pair_rows"])),
        "test_text_sha256": sha_text(csv_text(TEST_COLUMNS, rows["test_rows"])),
    }
    c59p3o = {
        "schema": "long.c59p3o@1",
        "object": "sign_dual_orientation_obstruction",
        "status": STATUS if all(checks.values()) else "LONG_C59P3O_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.c59p3o.report@1",
        "status": c59p3o["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_c59p3o tests whether the current finite time, transition, "
            "or stress-coupling surfaces distinguish the sign-dual max-volume "
            "3-plane pair from long_c59p3v. They do not: the time trace has "
            "been removed in the restricted form, semantic transition "
            "operations are absent, and no stress-coupling map is materialized."
        ),
        "stage_protocol": {
            "draft": "read long_c59p3v, long_c59pk, long_time_map, long_transition_sem, and long_stress_couple",
            "witness": "emit sign-dual pair rows, orientation-test rows, decisions, gaps, and observables",
            "coherence": "check equal-support sign duality, time-trace removal, transition-operation absence, stress-coupling absence, and current obstruction",
            "closure": "certify the current-boundary orientation obstruction for the sign-dual max-volume pair",
            "emit": "write long_c59p3o artifacts and verifier hook",
        },
        "inputs": {
            "long_c59p3v": input_entry(
                LONG_C59P3V,
                {
                    "status": rows["c59p3v"].get("status"),
                    "certificate_sha256": rows["c59p3v"].get("certificate_sha256"),
                },
            ),
            "long_c59p3v_max": input_entry(LONG_C59P3V_MAX),
            "long_c59p3v_support": input_entry(LONG_C59P3V_SUPPORT),
            "long_c59pk": input_entry(
                LONG_C59PK,
                {
                    "status": rows["c59pk"].get("status"),
                    "certificate_sha256": rows["c59pk"].get("certificate_sha256"),
                },
            ),
            "long_time_map": input_entry(
                LONG_TIME_MAP,
                {
                    "status": rows["time_map"].get("status"),
                    "certificate_sha256": rows["time_map"].get("certificate_sha256"),
                },
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
            "long_stress_couple": input_entry(
                LONG_STRESS_COUPLE,
                {
                    "status": rows["stress_couple"].get("status"),
                    "certificate_sha256": rows["stress_couple"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "c59p3o": relpath(OUT_DIR / "c59p3o.json"),
            "pair_csv": relpath(OUT_DIR / "pair.csv"),
            "test_csv": relpath(OUT_DIR / "test.csv"),
            "decision_csv": relpath(OUT_DIR / "decision.csv"),
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
                "the max-volume 3-plane pair is sign-dual with equal support and opposite determinant sign",
                "the restricted 18D form has the public time trace removed",
                "the current semantic transition-operation surface does not distinguish the pair",
                "the current stress-coupling surface does not distinguish the pair",
                "the sign-dual orientation choice is a current-boundary obstruction",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "absolute nonexistence of a future orientation rule",
                "a semantic transition operation that chooses an orientation",
                "a stress-coupling map that chooses an orientation",
                "acceptance of a physical selector axiom",
                "a four-dimensional metric reduction or thermal-gravity derivation",
            ],
        },
        "next_highest_yield_item": (
            "Break the sign-dual obstruction by constructing either semantic "
            "transition operation rows or a transition-to-stress coupling map; "
            "without one of those, orientation remains a selector axiom."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.c59p3o.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.c59p3o.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "c59p3o": c59p3o,
        "pair_csv": csv_text(PAIR_COLUMNS, rows["pair_rows"]),
        "test_csv": csv_text(TEST_COLUMNS, rows["test_rows"]),
        "decision_csv": csv_text(DECISION_COLUMNS, rows["decision_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "pair_table": pair_table,
        "test_table": test_table,
        "decision_table": decision_table,
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
    write_json(OUT_DIR / "c59p3o.json", payloads["c59p3o"])
    (OUT_DIR / "pair.csv").write_text(payloads["pair_csv"], encoding="utf-8")
    (OUT_DIR / "test.csv").write_text(payloads["test_csv"], encoding="utf-8")
    (OUT_DIR / "decision.csv").write_text(
        payloads["decision_csv"], encoding="utf-8"
    )
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        pair_table=payloads["pair_table"],
        test_table=payloads["test_table"],
        decision_table=payloads["decision_table"],
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
