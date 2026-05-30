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


THEOREM_ID = "long_tlift"
STATUS = "LONG_TLIFT_AFFINE_TICK_TRANSITION_LIFT_OBSTRUCTION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_GCLK = PROOF_ROOT / "long_gclk" / "report.json"
LONG_GCLK_CLOCK = PROOF_ROOT / "long_gclk" / "clock.csv"
LONG_TRANSITION_SEM = PROOF_ROOT / "long_transition_sem" / "report.json"
LONG_TRANSITION_ENDPOINT = PROOF_ROOT / "long_transition_sem" / "endpoint_raw.csv"
LONG_TRANSITION_CSV = PROOF_ROOT / "long_transition_sem" / "transition.csv"
LONG_CONTACT_LIFT = PROOF_ROOT / "long_contact_lift" / "report.json"
LONG_CONTACT_CSV = PROOF_ROOT / "long_contact_lift" / "contact.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_tlift.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_tlift.py"

VALUE_NAMES = ["atom_id", "coordinate_mask"]
VALUE_CODES = {name: index for index, name in enumerate(VALUE_NAMES)}
FIELD_NAMES = [
    "basis_id",
    "source0_addr",
    "source1_addr",
    "target_addr",
    "coeff",
    "raw_row_id",
]
FIELD_CODES = {name: index for index, name in enumerate(FIELD_NAMES)}
ORIENTATION_NAMES = ["directed", "undirected"]
ORIENTATION_CODES = {name: index for index, name in enumerate(ORIENTATION_NAMES)}

CANDIDATE_COLUMNS = [
    "candidate_id",
    "value_code",
    "field_code",
    "orientation_code",
    "tick_covered_count",
    "total_match_count",
    "max_multiplicity",
    "full_lift_flag",
    "semantic_transition_flag",
]
MATCH_COLUMNS = [
    "visible_index",
    "source_atom_id",
    "target_atom_id",
    "source_value",
    "target_value",
    "matched_transition_id",
    "matched_left_basis_id",
    "matched_right_basis_id",
    "matched_left_raw_row_id",
    "matched_right_raw_row_id",
    "matched_flag",
    "semantic_transition_flag",
]
SCHEMA_COLUMNS = [
    "schema_id",
    "schema_code",
    "row_count",
    "atom_key_flag",
    "coordinate_key_flag",
    "basis_key_flag",
    "raw_endpoint_key_flag",
    "semantic_operation_flag",
    "shared_key_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

SCHEMA_NAMES = [
    "affine_clock_ticks",
    "transition_endpoint_rows",
    "transition_rows",
    "contact_rows",
    "candidate_encodings",
]
SCHEMA_CODES = {name: index for index, name in enumerate(SCHEMA_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "affine_tick_count",
    "transition_endpoint_count",
    "transition_row_count",
    "contact_row_count",
    "candidate_encoding_count",
    "full_lift_candidate_count",
    "best_candidate_id",
    "best_candidate_covered_ticks",
    "best_candidate_total_matches",
    "best_candidate_max_multiplicity",
    "atom_basis_directed_covered_ticks",
    "atom_basis_undirected_covered_ticks",
    "coordinate_basis_directed_covered_ticks",
    "coordinate_basis_undirected_covered_ticks",
    "endpoint_address_full_lift_candidate_count",
    "semantic_transition_operation_flag",
    "semantic_transition_realized_count",
    "operation_row_materialized_count",
    "physical_transition_flag",
    "affine_tick_lift_obstruction_flag",
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


def transition_pair_maps(
    transition_rows: list[dict[str, str]],
) -> tuple[dict[tuple[int, int], dict[str, str]], dict[tuple[int, int], dict[str, str]]]:
    directed: dict[tuple[int, int], dict[str, str]] = {}
    undirected: dict[tuple[int, int], dict[str, str]] = {}
    for row in transition_rows:
        left = int(row["left_basis_id"])
        right = int(row["right_basis_id"])
        directed[(left, right)] = row
        undirected[tuple(sorted((left, right)))] = row
    return directed, undirected


def endpoint_value_maps(
    endpoint_rows: list[dict[str, str]],
) -> dict[str, dict[int, set[int]]]:
    maps: dict[str, dict[int, set[int]]] = {}
    for field in FIELD_NAMES:
        by_value: dict[int, set[int]] = {}
        for row in endpoint_rows:
            by_value.setdefault(int(row[field]), set()).add(int(row["basis_id"]))
        maps[field] = by_value
    return maps


def clock_value(row: dict[str, str], value_name: str, source: bool) -> int:
    if value_name == "atom_id":
        return int(row["source_atom_id" if source else "target_atom_id"])
    if value_name == "coordinate_mask":
        return int(row["source_coordinate_mask" if source else "affine_coordinate_mask"])
    raise AssertionError(f"unknown value name {value_name}")


def match_candidate(
    clock_rows: list[dict[str, str]],
    value_maps: dict[str, dict[int, set[int]]],
    transitions: dict[tuple[int, int], dict[str, str]],
    *,
    value_name: str,
    field_name: str,
    orientation_name: str,
) -> tuple[list[list[dict[str, str]]], int, int, int]:
    matches_by_tick: list[list[dict[str, str]]] = []
    covered = 0
    total_matches = 0
    max_multiplicity = 0
    for tick in clock_rows:
        source_value = clock_value(tick, value_name, source=True)
        target_value = clock_value(tick, value_name, source=False)
        lefts = value_maps[field_name].get(source_value, set())
        rights = value_maps[field_name].get(target_value, set())
        matches: list[dict[str, str]] = []
        for left in sorted(lefts):
            for right in sorted(rights):
                key = (left, right)
                if orientation_name == "undirected":
                    key = tuple(sorted(key))
                transition = transitions.get(key)
                if transition is not None:
                    matches.append(transition)
        matches_by_tick.append(matches)
        covered += int(bool(matches))
        total_matches += len(matches)
        max_multiplicity = max(max_multiplicity, len(matches))
    return matches_by_tick, covered, total_matches, max_multiplicity


def build_rows() -> dict[str, Any]:
    gclk = load_json(LONG_GCLK)
    transition_sem = load_json(LONG_TRANSITION_SEM)
    contact_lift = load_json(LONG_CONTACT_LIFT)
    clock_rows_raw = read_csv(LONG_GCLK_CLOCK)
    endpoint_rows_raw = read_csv(LONG_TRANSITION_ENDPOINT)
    transition_rows_raw = read_csv(LONG_TRANSITION_CSV)
    contact_rows_raw = read_csv(LONG_CONTACT_CSV)

    transition_s = summary(transition_sem)
    endpoint_maps = endpoint_value_maps(endpoint_rows_raw)
    directed_transitions, undirected_transitions = transition_pair_maps(transition_rows_raw)

    candidate_rows = []
    matches_by_candidate: dict[int, list[list[dict[str, str]]]] = {}
    candidate_id = 0
    for value_name in VALUE_NAMES:
        for field_name in FIELD_NAMES:
            for orientation_name in ORIENTATION_NAMES:
                transition_map = (
                    directed_transitions
                    if orientation_name == "directed"
                    else undirected_transitions
                )
                matches, covered, total_matches, max_multiplicity = match_candidate(
                    clock_rows_raw,
                    endpoint_maps,
                    transition_map,
                    value_name=value_name,
                    field_name=field_name,
                    orientation_name=orientation_name,
                )
                candidate_rows.append(
                    {
                        "candidate_id": candidate_id,
                        "value_code": VALUE_CODES[value_name],
                        "field_code": FIELD_CODES[field_name],
                        "orientation_code": ORIENTATION_CODES[orientation_name],
                        "tick_covered_count": covered,
                        "total_match_count": total_matches,
                        "max_multiplicity": max_multiplicity,
                        "full_lift_flag": int(covered == len(clock_rows_raw)),
                        "semantic_transition_flag": 0,
                    }
                )
                matches_by_candidate[candidate_id] = matches
                candidate_id += 1

    candidate_rows.sort(
        key=lambda row: (
            -row["tick_covered_count"],
            -row["total_match_count"],
            row["candidate_id"],
        )
    )
    best_candidate = candidate_rows[0]
    best_matches = matches_by_candidate[best_candidate["candidate_id"]]

    match_rows = []
    for tick, matches in zip(clock_rows_raw, best_matches):
        if matches:
            transition = matches[0]
            matched_transition_id = int(transition["transition_id"])
            matched_left = int(transition["left_basis_id"])
            matched_right = int(transition["right_basis_id"])
            matched_left_raw = int(transition["left_raw_row_id"])
            matched_right_raw = int(transition["right_raw_row_id"])
            matched_flag = 1
        else:
            matched_transition_id = -1
            matched_left = -1
            matched_right = -1
            matched_left_raw = -1
            matched_right_raw = -1
            matched_flag = 0
        match_rows.append(
            {
                "visible_index": int(tick["visible_index"]),
                "source_atom_id": int(tick["source_atom_id"]),
                "target_atom_id": int(tick["target_atom_id"]),
                "source_value": clock_value(tick, "atom_id", source=True),
                "target_value": clock_value(tick, "atom_id", source=False),
                "matched_transition_id": matched_transition_id,
                "matched_left_basis_id": matched_left,
                "matched_right_basis_id": matched_right,
                "matched_left_raw_row_id": matched_left_raw,
                "matched_right_raw_row_id": matched_right_raw,
                "matched_flag": matched_flag,
                "semantic_transition_flag": 0,
            }
        )

    schema_rows = [
        {
            "schema_id": SCHEMA_CODES["affine_clock_ticks"],
            "schema_code": SCHEMA_CODES["affine_clock_ticks"],
            "row_count": len(clock_rows_raw),
            "atom_key_flag": 1,
            "coordinate_key_flag": 1,
            "basis_key_flag": 0,
            "raw_endpoint_key_flag": 0,
            "semantic_operation_flag": 0,
            "shared_key_flag": 0,
        },
        {
            "schema_id": SCHEMA_CODES["transition_endpoint_rows"],
            "schema_code": SCHEMA_CODES["transition_endpoint_rows"],
            "row_count": len(endpoint_rows_raw),
            "atom_key_flag": 0,
            "coordinate_key_flag": 0,
            "basis_key_flag": 1,
            "raw_endpoint_key_flag": 1,
            "semantic_operation_flag": 0,
            "shared_key_flag": 0,
        },
        {
            "schema_id": SCHEMA_CODES["transition_rows"],
            "schema_code": SCHEMA_CODES["transition_rows"],
            "row_count": len(transition_rows_raw),
            "atom_key_flag": 0,
            "coordinate_key_flag": 0,
            "basis_key_flag": 1,
            "raw_endpoint_key_flag": 1,
            "semantic_operation_flag": int(
                any(int(row["semantic_transition_flag"]) for row in transition_rows_raw)
            ),
            "shared_key_flag": 0,
        },
        {
            "schema_id": SCHEMA_CODES["contact_rows"],
            "schema_code": SCHEMA_CODES["contact_rows"],
            "row_count": len(contact_rows_raw),
            "atom_key_flag": 0,
            "coordinate_key_flag": 0,
            "basis_key_flag": 1,
            "raw_endpoint_key_flag": 0,
            "semantic_operation_flag": 0,
            "shared_key_flag": 0,
        },
        {
            "schema_id": SCHEMA_CODES["candidate_encodings"],
            "schema_code": SCHEMA_CODES["candidate_encodings"],
            "row_count": len(candidate_rows),
            "atom_key_flag": 1,
            "coordinate_key_flag": 1,
            "basis_key_flag": 1,
            "raw_endpoint_key_flag": 1,
            "semantic_operation_flag": 0,
            "shared_key_flag": int(any(row["full_lift_flag"] for row in candidate_rows)),
        },
    ]

    lookup = {
        (
            VALUE_NAMES[row["value_code"]],
            FIELD_NAMES[row["field_code"]],
            ORIENTATION_NAMES[row["orientation_code"]],
        ): row
        for row in candidate_rows
    }
    endpoint_address_full_lifts = sum(
        row["full_lift_flag"]
        for key, row in lookup.items()
        if key[1] in {"source0_addr", "source1_addr", "target_addr", "coeff", "raw_row_id"}
    )
    obs = {
        "input_report_count": 3,
        "input_certified_count": sum(
            certified(report) for report in [gclk, transition_sem, contact_lift]
        ),
        "affine_tick_count": len(clock_rows_raw),
        "transition_endpoint_count": len(endpoint_rows_raw),
        "transition_row_count": len(transition_rows_raw),
        "contact_row_count": len(contact_rows_raw),
        "candidate_encoding_count": len(candidate_rows),
        "full_lift_candidate_count": sum(row["full_lift_flag"] for row in candidate_rows),
        "best_candidate_id": best_candidate["candidate_id"],
        "best_candidate_covered_ticks": best_candidate["tick_covered_count"],
        "best_candidate_total_matches": best_candidate["total_match_count"],
        "best_candidate_max_multiplicity": best_candidate["max_multiplicity"],
        "atom_basis_directed_covered_ticks": lookup[
            ("atom_id", "basis_id", "directed")
        ]["tick_covered_count"],
        "atom_basis_undirected_covered_ticks": lookup[
            ("atom_id", "basis_id", "undirected")
        ]["tick_covered_count"],
        "coordinate_basis_directed_covered_ticks": lookup[
            ("coordinate_mask", "basis_id", "directed")
        ]["tick_covered_count"],
        "coordinate_basis_undirected_covered_ticks": lookup[
            ("coordinate_mask", "basis_id", "undirected")
        ]["tick_covered_count"],
        "endpoint_address_full_lift_candidate_count": endpoint_address_full_lifts,
        "semantic_transition_operation_flag": int(
            transition_s["semantic_transition_operation_flag"]
        ),
        "semantic_transition_realized_count": int(
            transition_s["semantic_transition_realized_count"]
        ),
        "operation_row_materialized_count": int(
            transition_s["operation_row_materialized_count"]
        ),
        "physical_transition_flag": 0,
        "affine_tick_lift_obstruction_flag": int(
            best_candidate["tick_covered_count"] < len(clock_rows_raw)
        ),
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
        "gclk": gclk,
        "transition_sem": transition_sem,
        "contact_lift": contact_lift,
        "candidate_rows": candidate_rows,
        "match_rows": match_rows,
        "schema_rows": schema_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    candidate_table = table_from_rows(CANDIDATE_COLUMNS, rows["candidate_rows"])
    match_table = table_from_rows(MATCH_COLUMNS, rows["match_rows"])
    schema_table = table_from_rows(SCHEMA_COLUMNS, rows["schema_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"] == obs["input_certified_count"],
        "candidate_surface_complete": obs["affine_tick_count"] == 20
        and obs["transition_endpoint_count"] == 259
        and obs["transition_row_count"] == 642
        and obs["contact_row_count"] == 642
        and obs["candidate_encoding_count"] == 24,
        "no_complete_affine_tick_lift_exists_under_tested_current_schemas": obs[
            "full_lift_candidate_count"
        ]
        == 0
        and obs["best_candidate_covered_ticks"] == 7
        and obs["best_candidate_total_matches"] == 7
        and obs["best_candidate_max_multiplicity"] == 1,
        "expected_direct_encodings_are_incomplete": obs[
            "atom_basis_directed_covered_ticks"
        ]
        == 3
        and obs["atom_basis_undirected_covered_ticks"] == 7
        and obs["coordinate_basis_directed_covered_ticks"] == 0
        and obs["coordinate_basis_undirected_covered_ticks"] == 0
        and obs["endpoint_address_full_lift_candidate_count"] == 0,
        "semantic_transition_still_absent": obs["semantic_transition_operation_flag"] == 0
        and obs["semantic_transition_realized_count"] == 0
        and obs["operation_row_materialized_count"] == 0
        and obs["physical_transition_flag"] == 0
        and obs["gr_source_ready_flag"] == 0
        and obs["affine_tick_lift_obstruction_flag"] == 1,
        "table_shapes_match": candidate_table.shape == (24, len(CANDIDATE_COLUMNS))
        and match_table.shape == (20, len(MATCH_COLUMNS))
        and schema_table.shape == (len(SCHEMA_CODES), len(SCHEMA_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "affine_tick_transition_lift_obstruction",
        "summary": {
            "affine_tick_count": obs["affine_tick_count"],
            "candidate_encoding_count": obs["candidate_encoding_count"],
            "full_lift_candidate_count": obs["full_lift_candidate_count"],
            "best_candidate_id": obs["best_candidate_id"],
            "best_candidate": "atom_id:basis_id:undirected",
            "best_candidate_covered_ticks": obs["best_candidate_covered_ticks"],
            "atom_basis_directed_covered_ticks": obs[
                "atom_basis_directed_covered_ticks"
            ],
            "atom_basis_undirected_covered_ticks": obs[
                "atom_basis_undirected_covered_ticks"
            ],
            "coordinate_basis_undirected_covered_ticks": obs[
                "coordinate_basis_undirected_covered_ticks"
            ],
            "semantic_transition_operation_flag": obs[
                "semantic_transition_operation_flag"
            ],
            "semantic_transition_realized_count": obs[
                "semantic_transition_realized_count"
            ],
            "affine_tick_lift_obstruction_flag": obs[
                "affine_tick_lift_obstruction_flag"
            ],
            "gr_source_ready_flag": obs["gr_source_ready_flag"],
        },
        "value_code_map": {str(value): key for key, value in VALUE_CODES.items()},
        "field_code_map": {str(value): key for key, value in FIELD_CODES.items()},
        "orientation_code_map": {
            str(value): key for key, value in ORIENTATION_CODES.items()
        },
        "schema_code_map": {str(value): key for key, value in SCHEMA_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "candidate_table_sha256": sha_array(candidate_table),
        "candidate_text_sha256": sha_text(
            csv_text(CANDIDATE_COLUMNS, rows["candidate_rows"])
        ),
        "match_table_sha256": sha_array(match_table),
        "schema_table_sha256": sha_array(schema_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    tlift = {
        "schema": "long.tlift@1",
        "object": "affine_tick_transition_lift_obstruction",
        "status": STATUS if all(checks.values()) else "LONG_TLIFT_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.tlift.report@1",
        "status": tlift["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_tlift tests whether the 20 affine golden clock ticks from "
            "long_gclk can be lifted into the current raw-backed transition "
            "surface. Across atom-id and coordinate-mask encodings against "
            "basis ids and endpoint raw fields, no candidate covers all 20 "
            "ticks. The best accidental overlap is atom-id-as-basis-id with "
            "undirected transition edges, covering 7 of 20 ticks, so the "
            "affine clock remains unpromoted to semantic A985 transitions."
        ),
        "stage_protocol": {
            "draft": "read long_gclk, long_transition_sem, long_contact_lift, affine clock rows, endpoint rows, transition rows, and contact rows",
            "witness": "emit candidate encoding rows, best-candidate tick match rows, schema rows, and observables",
            "coherence": "check all 24 finite candidate encodings, best overlap, zero full lifts, and semantic operation absence",
            "closure": "certify the current-schema transition-lift obstruction for the affine golden tick",
            "emit": "write long_tlift artifacts and verifier hook",
        },
        "inputs": {
            "long_gclk": input_entry(
                LONG_GCLK,
                {
                    "status": rows["gclk"].get("status"),
                    "certificate_sha256": rows["gclk"].get("certificate_sha256"),
                },
            ),
            "long_gclk_clock": input_entry(LONG_GCLK_CLOCK),
            "long_transition_sem": input_entry(
                LONG_TRANSITION_SEM,
                {
                    "status": rows["transition_sem"].get("status"),
                    "certificate_sha256": rows["transition_sem"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_transition_endpoint": input_entry(LONG_TRANSITION_ENDPOINT),
            "long_transition_csv": input_entry(LONG_TRANSITION_CSV),
            "long_contact_lift": input_entry(
                LONG_CONTACT_LIFT,
                {
                    "status": rows["contact_lift"].get("status"),
                    "certificate_sha256": rows["contact_lift"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_contact_csv": input_entry(LONG_CONTACT_CSV),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "tlift": relpath(OUT_DIR / "tlift.json"),
            "candidate_csv": relpath(OUT_DIR / "candidate.csv"),
            "match_csv": relpath(OUT_DIR / "match.csv"),
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
                "the current affine golden clock has 20 atom/rim ticks to lift",
                "the current raw-backed transition surface has 259 endpoint rows and 642 transition rows",
                "24 schema-admissible direct encodings were tested across atom ids, coordinate masks, basis ids, endpoint address fields, and directed/undirected transition orientation",
                "no tested current-schema encoding gives a complete 20-tick transition lift",
                "the best overlap is atom-id-as-basis-id with undirected transitions, covering 7 of 20 ticks",
                "coordinate-mask-to-basis encodings cover 0 of 20 ticks",
                "no semantic A985 transition operation rows are materialized for the affine tick",
            ],
            "does_not_certify_because_out_of_scope": [
                "absolute nonexistence of a future lift after adding a new atom-to-basis map",
                "semantic A985 transition-operation realization for the affine clock",
                "a physical selector axiom",
                "that the affine golden clock is physical time",
                "a selected 1+3 Lorentzian spacetime boundary",
                "a physical stress-energy tensor or Einstein equation",
                "a derivation of general relativity from A985 alone",
            ],
        },
        "next_highest_yield_item": (
            "Materialize an explicit atom-to-basis map or prove its absence: "
            "the present transition surface cannot consume the affine clock "
            "until D20 atoms are functorially mapped into the 259 endpoint "
            "basis ids."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.tlift.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.tlift.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "tlift": tlift,
        "candidate_csv": csv_text(CANDIDATE_COLUMNS, rows["candidate_rows"]),
        "match_csv": csv_text(MATCH_COLUMNS, rows["match_rows"]),
        "schema_csv": csv_text(SCHEMA_COLUMNS, rows["schema_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "candidate_table": candidate_table,
        "match_table": match_table,
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
    write_json(OUT_DIR / "tlift.json", payloads["tlift"])
    (OUT_DIR / "candidate.csv").write_text(payloads["candidate_csv"], encoding="utf-8")
    (OUT_DIR / "match.csv").write_text(payloads["match_csv"], encoding="utf-8")
    (OUT_DIR / "schema.csv").write_text(payloads["schema_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        candidate_table=payloads["candidate_table"],
        match_table=payloads["match_table"],
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
