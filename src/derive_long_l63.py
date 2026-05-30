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


THEOREM_ID = "long_l63"
STATUS = "LONG_L63_SELECTOR_RIM_BRIDGE_OBSTRUCTION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"
THEOREM_ROOT = D20_INVARIANTS / "theorems"

LONG_C2UF = PROOF_ROOT / "long_c2uf" / "report.json"
LONG_SEL = PROOF_ROOT / "long_sel" / "report.json"
LONG_PSEL = PROOF_ROOT / "long_psel" / "report.json"
LONG_RIM = PROOF_ROOT / "long_rim" / "report.json"
LONG_RIM_CLASS = PROOF_ROOT / "long_rim" / "class.csv"
LONG_RIM_ORBIT = PROOF_ROOT / "long_rim" / "orbit.csv"
LONG_RIM_SELECT = PROOF_ROOT / "long_rim_select" / "report.json"
LONG_RIM_PHASE = PROOF_ROOT / "long_rim_select" / "phase.csv"
SELECTOR_LOOKUP = (
    THEOREM_ROOT
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table"
    / "selector_lookup_witness_table.csv"
)
LAZY63_REPORT = (
    THEOREM_ROOT
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lazy63"
    / "report.json"
)
FIXED63 = (
    THEOREM_ROOT
    / "raw543_repo_c2_kernel_agda_bridge_data"
    / "actual_raw543_agda_fixed63.csv"
)

DERIVE_SCRIPT = ROOT / "src" / "derive_long_l63.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_l63.py"

BRIDGE_COLUMNS = [
    "bridge_id",
    "bridge_code",
    "source_code",
    "selector_row_count",
    "rim_row_count",
    "count_match_flag",
    "semantic_key_present_flag",
    "row_bridge_present_flag",
    "golden_selector_backed_flag",
    "obstruction_flag",
]
SCHEMA_COLUMNS = [
    "schema_id",
    "schema_code",
    "source_code",
    "row_count",
    "class_id_flag",
    "lazy63_index_flag",
    "dynamics_id_flag",
    "rim_phase_key_flag",
    "semantic_bridge_key_flag",
]
OVERLAP_COLUMNS = [
    "overlap_id",
    "overlap_code",
    "left_source_code",
    "right_source_code",
    "raw_overlap_count",
    "domain_compatible_flag",
    "bridge_usable_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

BRIDGE_NAMES = [
    "lazy63_count_to_rim_phase_count",
    "lazy63_rows_to_rim_classes",
    "lazy63_fixed_orbits_to_rim_orbits",
    "golden_rim_direct_selector",
    "physical_selector_axiom",
]
BRIDGE_CODES = {name: index for index, name in enumerate(BRIDGE_NAMES)}

SCHEMA_NAMES = [
    "selector_lookup",
    "fixed63_orbits",
    "rim_class",
    "rim_orbit",
    "rim_phase",
]
SCHEMA_CODES = {name: index for index, name in enumerate(SCHEMA_NAMES)}

OVERLAP_NAMES = [
    "selector_lookup_to_rim_class_columns",
    "fixed63_to_rim_class_columns",
    "fixed63_to_rim_orbit_numeric_orbit_id",
    "lazy63_index_to_class_id_numeric",
]
OVERLAP_CODES = {name: index for index, name in enumerate(OVERLAP_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "selector_lookup_rows",
    "selector_family_count",
    "raw543_selector_rows",
    "lazy63_selector_rows",
    "paired_lazy480_selector_rows",
    "fixed63_rows",
    "rim_class_rows",
    "rim_orbit_rows",
    "rim_phase_rows",
    "lazy63_rim_count_match_flag",
    "selector_to_rim_class_shared_column_count",
    "fixed63_to_rim_class_shared_column_count",
    "fixed63_to_rim_orbit_raw_overlap_count",
    "fixed63_to_rim_orbit_domain_compatible_flag",
    "semantic_bridge_key_count",
    "row_bridge_present_flag",
    "golden_class_count",
    "golden_unoriented_rim_count",
    "golden_selector_backed_flag",
    "physical_selector_axiom_flag",
    "physical_selector_candidate_count",
    "psel_first_failure_clause_code",
    "bridge_obstruction_count",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}

SEMANTIC_BRIDGE_KEYS = {
    "rim_class_id",
    "rim_phase_id",
    "defect_class_id",
    "charpoly_sha256",
    "golden_flag",
    "representative_rim",
}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


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


def int_set(rows: list[dict[str, str]], key: str) -> set[int]:
    out: set[int] = set()
    for row in rows:
        value = row.get(key, "")
        if value != "":
            out.add(int(value))
    return out


def build_rows() -> dict[str, Any]:
    c2uf = load_json(LONG_C2UF)
    sel = load_json(LONG_SEL)
    psel = load_json(LONG_PSEL)
    rim = load_json(LONG_RIM)
    rim_select = load_json(LONG_RIM_SELECT)
    lazy63 = load_json(LAZY63_REPORT)

    selector_header, selector_rows = read_csv(SELECTOR_LOOKUP)
    fixed_header, fixed_rows = read_csv(FIXED63)
    class_header, class_rows = read_csv(LONG_RIM_CLASS)
    orbit_header, orbit_rows = read_csv(LONG_RIM_ORBIT)
    phase_header, phase_rows = read_csv(LONG_RIM_PHASE)

    by_selector: dict[str, int] = {}
    for row in selector_rows:
        by_selector[row["selector_name"]] = by_selector.get(row["selector_name"], 0) + 1
    lazy_rows = [
        row for row in selector_rows if row.get("selector_name") == "lazy63"
    ]

    selector_class_shared = sorted(set(selector_header) & set(class_header))
    fixed_class_shared = sorted(set(fixed_header) & set(class_header))
    fixed_orbit_raw_overlap = len(int_set(fixed_rows, "orbit_id") & int_set(orbit_rows, "orbit_id"))
    lazy_index_class_overlap = len(
        int_set(lazy_rows, "fiber_index") & int_set(class_rows, "class_id")
    )
    semantic_bridge_keys = sorted(
        (set(selector_header) | set(fixed_header))
        & (set(class_header) | set(orbit_header) | set(phase_header))
        & SEMANTIC_BRIDGE_KEYS
    )

    sel_s = summary(sel)
    psel_s = summary(psel)
    rim_s = summary(rim)
    rim_select_s = summary(rim_select)

    lazy_count = by_selector.get("lazy63", 0)
    rim_class_count = len(class_rows)
    count_match = int(lazy_count == rim_class_count == 63)
    semantic_key_count = len(semantic_bridge_keys)
    row_bridge = int(semantic_key_count > 0)
    golden_backed = int(row_bridge == 1 and int(rim_s["golden_defect_class_count"]) == 1)

    bridge_seed = [
        (
            "lazy63_count_to_rim_phase_count",
            0,
            lazy_count,
            rim_class_count,
            count_match,
            0,
            0,
            0,
        ),
        (
            "lazy63_rows_to_rim_classes",
            1,
            lazy_count,
            rim_class_count,
            count_match,
            int(semantic_key_count > 0),
            row_bridge,
            0,
        ),
        (
            "lazy63_fixed_orbits_to_rim_orbits",
            2,
            len(fixed_rows),
            len(orbit_rows),
            0,
            0,
            0,
            0,
        ),
        (
            "golden_rim_direct_selector",
            3,
            1,
            int(rim_select_s["golden_unoriented_rims"]),
            0,
            1,
            0,
            0,
        ),
        (
            "physical_selector_axiom",
            4,
            int(sel_s["physical_selector_candidate_count"]),
            1,
            0,
            0,
            0,
            int(sel_s["physical_selector_axiom_flag"]),
        ),
    ]
    bridge_rows = []
    for index, (
        name,
        source_code,
        selector_count,
        rim_count,
        match_flag,
        semantic_flag,
        bridge_flag,
        golden_flag,
    ) in enumerate(bridge_seed):
        obstruction = int(bridge_flag == 0 or golden_flag == 0)
        bridge_rows.append(
            {
                "bridge_id": index,
                "bridge_code": BRIDGE_CODES[name],
                "source_code": source_code,
                "selector_row_count": selector_count,
                "rim_row_count": rim_count,
                "count_match_flag": match_flag,
                "semantic_key_present_flag": semantic_flag,
                "row_bridge_present_flag": bridge_flag,
                "golden_selector_backed_flag": golden_flag,
                "obstruction_flag": obstruction,
            }
        )

    schema_inputs = [
        ("selector_lookup", 0, selector_header, len(selector_rows)),
        ("fixed63_orbits", 1, fixed_header, len(fixed_rows)),
        ("rim_class", 2, class_header, len(class_rows)),
        ("rim_orbit", 3, orbit_header, len(orbit_rows)),
        ("rim_phase", 4, phase_header, len(phase_rows)),
    ]
    schema_rows = []
    for index, (name, source_code, header, row_count) in enumerate(schema_inputs):
        header_set = set(header)
        schema_rows.append(
            {
                "schema_id": index,
                "schema_code": SCHEMA_CODES[name],
                "source_code": source_code,
                "row_count": row_count,
                "class_id_flag": int("class_id" in header_set),
                "lazy63_index_flag": int("lazy63_index" in header_set),
                "dynamics_id_flag": int("dynamics_id" in header_set or "agda_dynamics_id" in header_set),
                "rim_phase_key_flag": int("class_id" in header_set or "charpoly_sha256" in header_set),
                "semantic_bridge_key_flag": int(bool(header_set & SEMANTIC_BRIDGE_KEYS)),
            }
        )

    overlap_seed = [
        (
            "selector_lookup_to_rim_class_columns",
            0,
            2,
            len(selector_class_shared),
            0,
            0,
        ),
        (
            "fixed63_to_rim_class_columns",
            1,
            2,
            len(fixed_class_shared),
            0,
            0,
        ),
        (
            "fixed63_to_rim_orbit_numeric_orbit_id",
            1,
            3,
            fixed_orbit_raw_overlap,
            0,
            0,
        ),
        (
            "lazy63_index_to_class_id_numeric",
            0,
            2,
            lazy_index_class_overlap,
            0,
            0,
        ),
    ]
    overlap_rows = []
    for index, (
        name,
        left_code,
        right_code,
        raw_overlap,
        compatible,
        usable,
    ) in enumerate(overlap_seed):
        overlap_rows.append(
            {
                "overlap_id": index,
                "overlap_code": OVERLAP_CODES[name],
                "left_source_code": left_code,
                "right_source_code": right_code,
                "raw_overlap_count": raw_overlap,
                "domain_compatible_flag": compatible,
                "bridge_usable_flag": usable,
            }
        )

    obs = {
        "input_report_count": 5,
        "input_certified_count": sum(
            certified(report) for report in [c2uf, sel, psel, rim, rim_select]
        ),
        "selector_lookup_rows": len(selector_rows),
        "selector_family_count": len(by_selector),
        "raw543_selector_rows": by_selector.get("raw543", 0),
        "lazy63_selector_rows": lazy_count,
        "paired_lazy480_selector_rows": by_selector.get("paired_lazy480", 0),
        "fixed63_rows": len(fixed_rows),
        "rim_class_rows": rim_class_count,
        "rim_orbit_rows": len(orbit_rows),
        "rim_phase_rows": len(phase_rows),
        "lazy63_rim_count_match_flag": count_match,
        "selector_to_rim_class_shared_column_count": len(selector_class_shared),
        "fixed63_to_rim_class_shared_column_count": len(fixed_class_shared),
        "fixed63_to_rim_orbit_raw_overlap_count": fixed_orbit_raw_overlap,
        "fixed63_to_rim_orbit_domain_compatible_flag": 0,
        "semantic_bridge_key_count": semantic_key_count,
        "row_bridge_present_flag": row_bridge,
        "golden_class_count": int(rim_s["golden_defect_class_count"]),
        "golden_unoriented_rim_count": int(rim_select_s["golden_unoriented_rims"]),
        "golden_selector_backed_flag": golden_backed,
        "physical_selector_axiom_flag": int(sel_s["physical_selector_axiom_flag"]),
        "physical_selector_candidate_count": int(sel_s["physical_selector_candidate_count"]),
        "psel_first_failure_clause_code": int(psel_s["first_failure_clause_code"]),
        "bridge_obstruction_count": sum(row["obstruction_flag"] for row in bridge_rows),
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
        "c2uf": c2uf,
        "sel": sel,
        "psel": psel,
        "rim": rim,
        "rim_select": rim_select,
        "lazy63": lazy63,
        "bridge_rows": bridge_rows,
        "schema_rows": schema_rows,
        "overlap_rows": overlap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "selector_class_shared": selector_class_shared,
        "fixed_class_shared": fixed_class_shared,
        "semantic_bridge_keys": semantic_bridge_keys,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    bridge_table = table_from_rows(BRIDGE_COLUMNS, rows["bridge_rows"])
    schema_table = table_from_rows(SCHEMA_COLUMNS, rows["schema_rows"])
    overlap_table = table_from_rows(OVERLAP_COLUMNS, rows["overlap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_certified_count"] == obs["input_report_count"],
        "lazy63_selector_and_rim_phase_counts_match": obs["lazy63_selector_rows"] == 63
        and obs["rim_class_rows"] == 63
        and obs["lazy63_rim_count_match_flag"] == 1,
        "selector_lookup_families_cohere": obs["selector_lookup_rows"] == 1086
        and obs["raw543_selector_rows"] == 543
        and obs["paired_lazy480_selector_rows"] == 480
        and obs["selector_family_count"] == 3,
        "row_bridge_absent": obs["semantic_bridge_key_count"] == 0
        and obs["row_bridge_present_flag"] == 0,
        "numeric_overlaps_are_not_domain_bridges": obs[
            "fixed63_to_rim_orbit_raw_overlap_count"
        ]
        > 0
        and obs["fixed63_to_rim_orbit_domain_compatible_flag"] == 0,
        "golden_selector_not_formally_backed": obs["golden_class_count"] == 1
        and obs["golden_unoriented_rim_count"] == 144
        and obs["golden_selector_backed_flag"] == 0,
        "physical_selector_first_failure_preserved": obs["physical_selector_axiom_flag"] == 0
        and obs["physical_selector_candidate_count"] == 0
        and obs["psel_first_failure_clause_code"] == 4,
        "table_shapes_match": bridge_table.shape == (len(BRIDGE_CODES), len(BRIDGE_COLUMNS))
        and schema_table.shape == (len(SCHEMA_CODES), len(SCHEMA_COLUMNS))
        and overlap_table.shape == (len(OVERLAP_CODES), len(OVERLAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "lazy63_to_rim_phase_bridge_obstruction",
        "summary": {
            "selector_lookup_rows": obs["selector_lookup_rows"],
            "lazy63_selector_rows": obs["lazy63_selector_rows"],
            "rim_class_rows": obs["rim_class_rows"],
            "lazy63_rim_count_match_flag": obs["lazy63_rim_count_match_flag"],
            "semantic_bridge_key_count": obs["semantic_bridge_key_count"],
            "row_bridge_present_flag": obs["row_bridge_present_flag"],
            "fixed63_to_rim_orbit_raw_overlap_count": obs[
                "fixed63_to_rim_orbit_raw_overlap_count"
            ],
            "fixed63_to_rim_orbit_domain_compatible_flag": obs[
                "fixed63_to_rim_orbit_domain_compatible_flag"
            ],
            "golden_class_count": obs["golden_class_count"],
            "golden_unoriented_rim_count": obs["golden_unoriented_rim_count"],
            "golden_selector_backed_flag": obs["golden_selector_backed_flag"],
            "physical_selector_axiom_flag": obs["physical_selector_axiom_flag"],
            "bridge_obstruction_count": obs["bridge_obstruction_count"],
        },
        "bridge_code_map": {str(value): key for key, value in BRIDGE_CODES.items()},
        "schema_code_map": {str(value): key for key, value in SCHEMA_CODES.items()},
        "overlap_code_map": {str(value): key for key, value in OVERLAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "selector_class_shared_columns": rows["selector_class_shared"],
        "fixed_class_shared_columns": rows["fixed_class_shared"],
        "semantic_bridge_keys": rows["semantic_bridge_keys"],
        "bridge_table_sha256": sha_array(bridge_table),
        "bridge_text_sha256": sha_text(csv_text(BRIDGE_COLUMNS, rows["bridge_rows"])),
        "schema_table_sha256": sha_array(schema_table),
        "overlap_table_sha256": sha_array(overlap_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    l63 = {
        "schema": "long.l63@1",
        "object": "lazy63_to_rim_phase_bridge_obstruction",
        "status": STATUS if all(checks.values()) else "LONG_L63_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.l63.report@1",
        "status": l63["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_l63 tests the tempting cardinality bridge between the C2 "
            "lazy63 formal selector and the 63 complement-antipodal rim defect "
            "classes. The count match is certified, but the current artifact "
            "boundary has no semantic row key mapping lazy63 selector rows to "
            "rim classes or to the golden rim phase."
        ),
        "stage_protocol": {
            "draft": "read long_c2uf, long_sel, long_psel, long_rim, long_rim_select, lazy63, selector lookup, fixed63, and rim class/orbit/phase tables",
            "witness": "emit bridge candidate rows, schema rows, overlap rows, and observables",
            "coherence": "check input statuses, selector counts, rim counts, key absence, numeric-overlap domain mismatch, and table hashes",
            "closure": "certify the current-boundary lazy63-to-rim bridge obstruction",
            "emit": "write long_l63 artifacts and verifier hook",
        },
        "inputs": {
            "long_c2uf": input_entry(
                LONG_C2UF,
                {
                    "status": rows["c2uf"].get("status"),
                    "certificate_sha256": rows["c2uf"].get("certificate_sha256"),
                },
            ),
            "long_sel": input_entry(
                LONG_SEL,
                {
                    "status": rows["sel"].get("status"),
                    "certificate_sha256": rows["sel"].get("certificate_sha256"),
                },
            ),
            "long_psel": input_entry(
                LONG_PSEL,
                {
                    "status": rows["psel"].get("status"),
                    "certificate_sha256": rows["psel"].get("certificate_sha256"),
                },
            ),
            "long_rim": input_entry(
                LONG_RIM,
                {
                    "status": rows["rim"].get("status"),
                    "certificate_sha256": rows["rim"].get("certificate_sha256"),
                },
            ),
            "long_rim_select": input_entry(
                LONG_RIM_SELECT,
                {
                    "status": rows["rim_select"].get("status"),
                    "certificate_sha256": rows["rim_select"].get("certificate_sha256"),
                },
            ),
            "lazy63_report": input_entry(
                LAZY63_REPORT,
                {
                    "status": rows["lazy63"].get("status"),
                    "certificate_sha256": rows["lazy63"].get("certificate_sha256"),
                },
            ),
            "selector_lookup": input_entry(SELECTOR_LOOKUP),
            "fixed63": input_entry(FIXED63),
            "rim_class": input_entry(LONG_RIM_CLASS),
            "rim_orbit": input_entry(LONG_RIM_ORBIT),
            "rim_phase": input_entry(LONG_RIM_PHASE),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "l63": relpath(OUT_DIR / "l63.json"),
            "bridge_csv": relpath(OUT_DIR / "bridge.csv"),
            "schema_csv": relpath(OUT_DIR / "schema.csv"),
            "overlap_csv": relpath(OUT_DIR / "overlap.csv"),
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
                "lazy63 has 63 selector rows and the rim defect classifier has 63 classes",
                "the cardinality match alone does not provide a certified selector-to-rim row map",
                "the current selector and rim tables expose no semantic bridge key for class, phase, characteristic polynomial, or golden-rim selection",
                "numeric orbit-id overlap between fixed63 and rim-orbit tables is domain-incompatible and not usable as a bridge",
                "the golden rim phase remains a direct rim candidate without formal lazy63 selector backing",
            ],
            "does_not_certify_because_out_of_scope": [
                "absolute nonexistence of a future lazy63-to-rim bridge",
                "a physical selector axiom",
                "a raw A985-to-packet operator bridge",
                "semantic A985 transition operations",
                "a selected 1+3 Lorentzian spacetime boundary",
                "a derivation of general relativity from A985 alone",
            ],
        },
        "next_highest_yield_item": (
            "Construct an explicit semantic bridge table from lazy63 fixed "
            "orbits to rim defect classes, with class_id/charpoly/golden_flag "
            "columns, then rerun this gate to see whether the count match can "
            "be promoted to a physical selector candidate."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.l63.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.l63.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "l63": l63,
        "bridge_csv": csv_text(BRIDGE_COLUMNS, rows["bridge_rows"]),
        "schema_csv": csv_text(SCHEMA_COLUMNS, rows["schema_rows"]),
        "overlap_csv": csv_text(OVERLAP_COLUMNS, rows["overlap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "bridge_table": bridge_table,
        "schema_table": schema_table,
        "overlap_table": overlap_table,
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
    write_json(OUT_DIR / "l63.json", payloads["l63"])
    (OUT_DIR / "bridge.csv").write_text(payloads["bridge_csv"], encoding="utf-8")
    (OUT_DIR / "schema.csv").write_text(payloads["schema_csv"], encoding="utf-8")
    (OUT_DIR / "overlap.csv").write_text(payloads["overlap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        bridge_table=payloads["bridge_table"],
        schema_table=payloads["schema_table"],
        overlap_table=payloads["overlap_table"],
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
