from __future__ import annotations

import csv
import hashlib
import json
import math
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


THEOREM_ID = "long_c59p3n"
STATUS = "LONG_C59P3N_CLOCK_PACKET_DENOMINATOR_NORMALIZATION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_C59P3E = PROOF_ROOT / "long_c59p3e" / "report.json"
LONG_C59P3E_WEIGHT = PROOF_ROOT / "long_c59p3e" / "weight.csv"
LONG_GCLK = PROOF_ROOT / "long_gclk" / "report.json"
LONG_BINC = PROOF_ROOT / "long_binc" / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_c59p3n.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_c59p3n.py"

NORMALIZATION_COLUMNS = [
    "normalization_id",
    "normalization_code",
    "scale_value",
    "common_denominator",
    "gcd_value",
    "lcm_value",
    "clears_common_denominator_flag",
    "residual_denominator",
    "cleared_row_count",
    "uncleared_row_count",
]
WEIGHT_CLEAR_COLUMNS = [
    "carrier_id",
    "atom_id",
    "weight_num",
    "weight_den",
    "visible20_cleared_num",
    "visible20_cleared_flag",
    "hidden10_cleared_num",
    "hidden10_cleared_flag",
    "packet32_cleared_num",
    "packet32_cleared_flag",
    "lcm160_cleared_num",
    "lcm160_cleared_flag",
    "packet_residual_denominator",
]
PROFILE_COLUMNS = [
    "profile_id",
    "weight_den",
    "row_count",
    "atom_count",
    "visible20_cleared_flag",
    "hidden10_cleared_flag",
    "packet32_cleared_flag",
    "lcm160_cleared_flag",
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

NORMALIZATION_NAMES = [
    "selector_common_denominator_20",
    "hidden_affine_c10_clock",
    "visible_c20_cycle",
    "packet_lattice_index_32",
    "joint_visible_packet_lcm_160",
]
NORMALIZATION_CODES = {name: index for index, name in enumerate(NORMALIZATION_NAMES)}

GAP_NAMES = [
    "rational_selector_distribution",
    "visible_c20_clearance",
    "hidden_c10_clearance_obstruction",
    "packet32_clearance_obstruction",
    "joint_clock_packet_lcm_clearance",
    "operation_backed_normalized_counterterm",
    "physical_selector_axiom",
    "metric_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "carrier_row_count",
    "common_denominator",
    "visible_cycle_scale",
    "hidden_clock_scale",
    "packet_scale",
    "joint_lcm_scale",
    "visible_cleared_row_count",
    "hidden_cleared_row_count",
    "hidden_uncleared_row_count",
    "packet_cleared_row_count",
    "packet_uncleared_row_count",
    "lcm_cleared_row_count",
    "denominator1_row_count",
    "denominator2_row_count",
    "denominator4_row_count",
    "denominator5_row_count",
    "denominator5_atom_count",
    "hidden_den4_uncleared_row_count",
    "visible_denominator_clearance_flag",
    "hidden_clock_clearance_flag",
    "packet_index_clearance_flag",
    "joint_lcm_clearance_flag",
    "operation_backed_flag",
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


def lcm_pair(left: int, right: int) -> int:
    return left * right // math.gcd(left, right)


def row_clears(scale: int, weight_den: int) -> bool:
    return scale % weight_den == 0


def cleared_num(scale: int, weight_num: int, weight_den: int) -> int:
    if not row_clears(scale, weight_den):
        return 0
    return weight_num * (scale // weight_den)


def scale_summary(
    *,
    normalization_id: int,
    name: str,
    scale: int,
    common_denominator: int,
    weight_rows: list[dict[str, int]],
) -> dict[str, int]:
    gcd_value = math.gcd(scale, common_denominator)
    cleared = sum(int(row_clears(scale, row["weight_den"])) for row in weight_rows)
    return {
        "normalization_id": normalization_id,
        "normalization_code": NORMALIZATION_CODES[name],
        "scale_value": scale,
        "common_denominator": common_denominator,
        "gcd_value": gcd_value,
        "lcm_value": lcm_pair(scale, common_denominator),
        "clears_common_denominator_flag": int(scale % common_denominator == 0),
        "residual_denominator": common_denominator // gcd_value,
        "cleared_row_count": cleared,
        "uncleared_row_count": len(weight_rows) - cleared,
    }


def build_rows() -> dict[str, Any]:
    c59p3e = load_json(LONG_C59P3E)
    gclk = load_json(LONG_GCLK)
    binc = load_json(LONG_BINC)
    _, raw_weight_rows = read_csv_rows(LONG_C59P3E_WEIGHT)

    common_denominator = int(c59p3e["witness"]["summary"]["common_denominator"])
    visible_scale = int(gclk["witness"]["summary"]["d20_as_grade_three_f2_6_count"])
    hidden_scale = int(gclk["witness"]["summary"]["affine_clock_order"])
    packet_scale = int(binc["witness"]["summary"]["zero_sum_boundary_lattice_index"])
    joint_lcm_scale = lcm_pair(visible_scale, packet_scale)

    source_weight_rows = [
        {
            "carrier_id": int(row["carrier_id"]),
            "atom_id": int(row["atom_id"]),
            "weight_num": int(row["weight_num"]),
            "weight_den": int(row["weight_den"]),
        }
        for row in raw_weight_rows
    ]
    weight_clear_rows = []
    atoms_by_den: dict[int, set[int]] = defaultdict(set)
    rows_by_den: dict[int, int] = defaultdict(int)
    for row in source_weight_rows:
        weight_den = row["weight_den"]
        atoms_by_den[weight_den].add(row["atom_id"])
        rows_by_den[weight_den] += 1
        weight_clear_rows.append(
            {
                "carrier_id": row["carrier_id"],
                "atom_id": row["atom_id"],
                "weight_num": row["weight_num"],
                "weight_den": weight_den,
                "visible20_cleared_num": cleared_num(
                    visible_scale, row["weight_num"], weight_den
                ),
                "visible20_cleared_flag": int(row_clears(visible_scale, weight_den)),
                "hidden10_cleared_num": cleared_num(
                    hidden_scale, row["weight_num"], weight_den
                ),
                "hidden10_cleared_flag": int(row_clears(hidden_scale, weight_den)),
                "packet32_cleared_num": cleared_num(
                    packet_scale, row["weight_num"], weight_den
                ),
                "packet32_cleared_flag": int(row_clears(packet_scale, weight_den)),
                "lcm160_cleared_num": cleared_num(
                    joint_lcm_scale, row["weight_num"], weight_den
                ),
                "lcm160_cleared_flag": int(row_clears(joint_lcm_scale, weight_den)),
                "packet_residual_denominator": weight_den
                // math.gcd(packet_scale, weight_den),
            }
        )

    profile_rows = []
    for profile_id, weight_den in enumerate(sorted(rows_by_den)):
        profile_rows.append(
            {
                "profile_id": profile_id,
                "weight_den": weight_den,
                "row_count": rows_by_den[weight_den],
                "atom_count": len(atoms_by_den[weight_den]),
                "visible20_cleared_flag": int(row_clears(visible_scale, weight_den)),
                "hidden10_cleared_flag": int(row_clears(hidden_scale, weight_den)),
                "packet32_cleared_flag": int(row_clears(packet_scale, weight_den)),
                "lcm160_cleared_flag": int(row_clears(joint_lcm_scale, weight_den)),
            }
        )

    normalization_specs = [
        ("selector_common_denominator_20", common_denominator),
        ("hidden_affine_c10_clock", hidden_scale),
        ("visible_c20_cycle", visible_scale),
        ("packet_lattice_index_32", packet_scale),
        ("joint_visible_packet_lcm_160", joint_lcm_scale),
    ]
    normalization_rows = [
        scale_summary(
            normalization_id=normalization_id,
            name=name,
            scale=scale,
            common_denominator=common_denominator,
            weight_rows=source_weight_rows,
        )
        for normalization_id, (name, scale) in enumerate(normalization_specs)
    ]

    visible_cleared = sum(row["visible20_cleared_flag"] for row in weight_clear_rows)
    hidden_cleared = sum(row["hidden10_cleared_flag"] for row in weight_clear_rows)
    packet_cleared = sum(row["packet32_cleared_flag"] for row in weight_clear_rows)
    lcm_cleared = sum(row["lcm160_cleared_flag"] for row in weight_clear_rows)
    obs = {
        "input_report_count": 3,
        "input_certified_count": sum(
            int(certified(report)) for report in (c59p3e, gclk, binc)
        ),
        "carrier_row_count": len(weight_clear_rows),
        "common_denominator": common_denominator,
        "visible_cycle_scale": visible_scale,
        "hidden_clock_scale": hidden_scale,
        "packet_scale": packet_scale,
        "joint_lcm_scale": joint_lcm_scale,
        "visible_cleared_row_count": visible_cleared,
        "hidden_cleared_row_count": hidden_cleared,
        "hidden_uncleared_row_count": len(weight_clear_rows) - hidden_cleared,
        "packet_cleared_row_count": packet_cleared,
        "packet_uncleared_row_count": len(weight_clear_rows) - packet_cleared,
        "lcm_cleared_row_count": lcm_cleared,
        "denominator1_row_count": rows_by_den[1],
        "denominator2_row_count": rows_by_den[2],
        "denominator4_row_count": rows_by_den[4],
        "denominator5_row_count": rows_by_den[5],
        "denominator5_atom_count": len(atoms_by_den[5]),
        "hidden_den4_uncleared_row_count": sum(
            int(row["weight_den"] == 4 and row["hidden10_cleared_flag"] == 0)
            for row in weight_clear_rows
        ),
        "visible_denominator_clearance_flag": int(
            visible_cleared == len(weight_clear_rows)
        ),
        "hidden_clock_clearance_flag": int(hidden_cleared == len(weight_clear_rows)),
        "packet_index_clearance_flag": int(packet_cleared == len(weight_clear_rows)),
        "joint_lcm_clearance_flag": int(lcm_cleared == len(weight_clear_rows)),
        "operation_backed_flag": 0,
        "physical_selector_axiom_flag": 0,
        "metric_derivation_flag": 0,
        "next_gap_code": GAP_CODES["operation_backed_normalized_counterterm"],
    }
    gap_rows = [
        {
            "gap_id": GAP_CODES["rational_selector_distribution"],
            "gap_code": GAP_CODES["rational_selector_distribution"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["visible_c20_clearance"],
            "gap_code": GAP_CODES["visible_c20_clearance"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["hidden_c10_clearance_obstruction"],
            "gap_code": GAP_CODES["hidden_c10_clearance_obstruction"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["packet32_clearance_obstruction"],
            "gap_code": GAP_CODES["packet32_clearance_obstruction"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["joint_clock_packet_lcm_clearance"],
            "gap_code": GAP_CODES["joint_clock_packet_lcm_clearance"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["operation_backed_normalized_counterterm"],
            "gap_code": GAP_CODES["operation_backed_normalized_counterterm"],
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
        "c59p3e": c59p3e,
        "gclk": gclk,
        "binc": binc,
        "normalization_rows": normalization_rows,
        "weight_clear_rows": weight_clear_rows,
        "profile_rows": profile_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    normalization_table = table_from_rows(
        NORMALIZATION_COLUMNS, rows["normalization_rows"]
    )
    weight_clear_table = table_from_rows(
        WEIGHT_CLEAR_COLUMNS, rows["weight_clear_rows"]
    )
    profile_table = table_from_rows(PROFILE_COLUMNS, rows["profile_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "normalization_scales_certified": (
            obs["common_denominator"],
            obs["visible_cycle_scale"],
            obs["hidden_clock_scale"],
            obs["packet_scale"],
            obs["joint_lcm_scale"],
        )
        == (20, 20, 10, 32, 160),
        "visible_cycle_clears_denominator": obs[
            "visible_denominator_clearance_flag"
        ]
        == 1
        and obs["visible_cleared_row_count"] == 77,
        "hidden_c10_clearance_obstructed": obs["hidden_clock_clearance_flag"] == 0
        and obs["hidden_cleared_row_count"] == 65
        and obs["hidden_uncleared_row_count"] == 12
        and obs["hidden_den4_uncleared_row_count"] == 12,
        "packet32_clearance_obstructed": obs["packet_index_clearance_flag"] == 0
        and obs["packet_cleared_row_count"] == 52
        and obs["packet_uncleared_row_count"] == 25
        and obs["denominator5_row_count"] == 25
        and obs["denominator5_atom_count"] == 5,
        "joint_lcm_clears_denominator": obs["joint_lcm_clearance_flag"] == 1
        and obs["lcm_cleared_row_count"] == 77,
        "denominator_profile_exact": (
            obs["denominator1_row_count"],
            obs["denominator2_row_count"],
            obs["denominator4_row_count"],
            obs["denominator5_row_count"],
        )
        == (30, 10, 12, 25),
        "operation_and_physical_boundaries_preserved": obs["operation_backed_flag"]
        == 0
        and obs["physical_selector_axiom_flag"] == 0
        and obs["metric_derivation_flag"] == 0,
        "table_shapes_match": normalization_table.shape
        == (len(NORMALIZATION_CODES), len(NORMALIZATION_COLUMNS))
        and weight_clear_table.shape == (77, len(WEIGHT_CLEAR_COLUMNS))
        and profile_table.shape == (4, len(PROFILE_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "clock_packet_denominator_normalization",
        "summary": {
            "carrier_row_count": obs["carrier_row_count"],
            "common_denominator": obs["common_denominator"],
            "visible_cycle_scale": obs["visible_cycle_scale"],
            "hidden_clock_scale": obs["hidden_clock_scale"],
            "packet_scale": obs["packet_scale"],
            "joint_lcm_scale": obs["joint_lcm_scale"],
            "visible_cleared_row_count": obs["visible_cleared_row_count"],
            "hidden_cleared_row_count": obs["hidden_cleared_row_count"],
            "hidden_uncleared_row_count": obs["hidden_uncleared_row_count"],
            "packet_cleared_row_count": obs["packet_cleared_row_count"],
            "packet_uncleared_row_count": obs["packet_uncleared_row_count"],
            "lcm_cleared_row_count": obs["lcm_cleared_row_count"],
            "denominator5_row_count": obs["denominator5_row_count"],
            "operation_backed_flag": obs["operation_backed_flag"],
        },
        "normalization_code_map": {
            str(value): key for key, value in NORMALIZATION_CODES.items()
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "normalization_table_sha256": sha_array(normalization_table),
        "normalization_text_sha256": sha_text(
            csv_text(NORMALIZATION_COLUMNS, rows["normalization_rows"])
        ),
        "weight_clear_table_sha256": sha_array(weight_clear_table),
        "weight_clear_text_sha256": sha_text(
            csv_text(WEIGHT_CLEAR_COLUMNS, rows["weight_clear_rows"])
        ),
        "profile_table_sha256": sha_array(profile_table),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    c59p3n = {
        "schema": "long.c59p3n@1",
        "object": "clock_packet_denominator_normalization",
        "status": STATUS if all(checks.values()) else "LONG_C59P3N_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.c59p3n.report@1",
        "status": c59p3n["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_c59p3n certifies that the denominator-20 selector weights "
            "from long_c59p3e clear on the visible 20-state boundary scale. "
            "The hidden C10 clock alone leaves 12 denominator-four rows "
            "uncleared, and the packet index 32 alone leaves 25 "
            "denominator-five rows uncleared. The joint visible/packet lcm "
            "160 clears all 77 carrier rows."
        ),
        "stage_protocol": {
            "draft": "read long_c59p3e, long_gclk, long_binc, and the c59p3e weight rows",
            "witness": "emit normalization rows, per-carrier clearing rows, denominator profiles, gaps, and observables",
            "coherence": "check scale arithmetic, denominator profiles, row clearance counts, packet obstruction, and preserved operation/physical gaps",
            "closure": "certify clock/packet denominator normalization without promoting the rows to operations",
            "emit": "write long_c59p3n artifacts and verifier hook",
        },
        "inputs": {
            "long_c59p3e": input_entry(
                LONG_C59P3E,
                {
                    "status": rows["c59p3e"].get("status"),
                    "certificate_sha256": rows["c59p3e"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_c59p3e_weight": input_entry(LONG_C59P3E_WEIGHT),
            "long_gclk": input_entry(
                LONG_GCLK,
                {
                    "status": rows["gclk"].get("status"),
                    "certificate_sha256": rows["gclk"].get("certificate_sha256"),
                },
            ),
            "long_binc": input_entry(
                LONG_BINC,
                {
                    "status": rows["binc"].get("status"),
                    "certificate_sha256": rows["binc"].get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "c59p3n": relpath(OUT_DIR / "c59p3n.json"),
            "normalization_csv": relpath(OUT_DIR / "normalization.csv"),
            "weight_clear_csv": relpath(OUT_DIR / "weight_clear.csv"),
            "profile_csv": relpath(OUT_DIR / "profile.csv"),
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
                "the 20-state visible boundary scale clears every reduced selector denominator from long_c59p3e",
                "the hidden C10 clock alone fails to clear the 12 denominator-four carrier rows",
                "the packet lattice index 32 alone fails to clear the 25 denominator-five carrier rows",
                "the joint visible/packet lcm 160 clears all 77 carrier rows",
                "the exact denominator profile is 30 rows at 1, 10 rows at 2, 12 rows at 4, and 25 rows at 5",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "operation-backed normalized counterterm rows",
                "a physical selector axiom",
                "a four-dimensional metric reduction",
                "a physical field equation",
            ],
        },
        "next_highest_yield_item": (
            "Use the visible-clock-cleared integer rows to attempt an "
            "operation-backed normalized counterterm witness, or certify the "
            "first operation-promotion failure."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.c59p3n.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.c59p3n.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "c59p3n": c59p3n,
        "normalization_csv": csv_text(
            NORMALIZATION_COLUMNS, rows["normalization_rows"]
        ),
        "weight_clear_csv": csv_text(
            WEIGHT_CLEAR_COLUMNS, rows["weight_clear_rows"]
        ),
        "profile_csv": csv_text(PROFILE_COLUMNS, rows["profile_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "normalization_table": normalization_table,
        "weight_clear_table": weight_clear_table,
        "profile_table": profile_table,
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
    write_json(OUT_DIR / "c59p3n.json", payloads["c59p3n"])
    (OUT_DIR / "normalization.csv").write_text(
        payloads["normalization_csv"], encoding="utf-8"
    )
    (OUT_DIR / "weight_clear.csv").write_text(
        payloads["weight_clear_csv"], encoding="utf-8"
    )
    (OUT_DIR / "profile.csv").write_text(payloads["profile_csv"], encoding="utf-8")
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        normalization_table=payloads["normalization_table"],
        weight_clear_table=payloads["weight_clear_table"],
        profile_table=payloads["profile_table"],
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
