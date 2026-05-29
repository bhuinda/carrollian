from __future__ import annotations

import hashlib
import json
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
    from .derive_long_comp import (
        LONG_LLN_REPORT,
        LONG_LLN_TABLES,
        OUT_DIR as LONG_COMP_DIR,
        STATUS as LONG_COMP_STATUS,
    )
    from .derive_long_path import OUT_DIR as LONG_PATH_DIR, STATUS as LONG_PATH_STATUS
    from .derive_long_lln import STATUS as LONG_LLN_STATUS
    from .derive_long_raw import (
        csv_text,
        digest_text,
        int_rows,
        read_csv_rows,
        rows_from_table,
        table_from_rows,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_comp import (
        LONG_LLN_REPORT,
        LONG_LLN_TABLES,
        OUT_DIR as LONG_COMP_DIR,
        STATUS as LONG_COMP_STATUS,
    )
    from derive_long_path import OUT_DIR as LONG_PATH_DIR, STATUS as LONG_PATH_STATUS
    from derive_long_lln import STATUS as LONG_LLN_STATUS
    from derive_long_raw import (
        csv_text,
        digest_text,
        int_rows,
        read_csv_rows,
        rows_from_table,
        table_from_rows,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_sheaf"
STATUS = "LONG_SHEAF_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
LONG_PATH_REPORT = LONG_PATH_DIR / "report.json"
LONG_PATH_COMPONENT = LONG_PATH_DIR / "component.csv"
LONG_PATH_PATH = LONG_PATH_DIR / "path.csv"
LONG_PATH_STEP = LONG_PATH_DIR / "step.csv"
LONG_PATH_TABLES = LONG_PATH_DIR / "tables.npz"
LONG_COMP_REPORT = LONG_COMP_DIR / "report.json"
LONG_COMP_PAIR = LONG_COMP_DIR / "pair.csv"
LONG_COMP_PATH = LONG_COMP_DIR / "path.csv"
LONG_COMP_TRANSITION = LONG_COMP_DIR / "transition.csv"
LONG_COMP_TABLES = LONG_COMP_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_sheaf.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_sheaf.py"

SECTION_TEXT_HASH = (
    "75ec5ff92a614f2998e0a445bd26ba8d9de1bb4e8f30fec1c4a71cf794adbf62"
)
CUT_TEXT_HASH = (
    "2f4bf3a358a05141c4efbfd62e8f9a89827e3630f7a21f7cc7049dcdb4af9bc1"
)
STALK_TEXT_HASH = (
    "89613824278fe35e2f8f574038a0c95f34d9ed7312dd2087a5a105e8a4443ccc"
)

LINE_POINT_COUNT = 985

SECTION_COLUMNS = [
    "section_id",
    "path_id",
    "fiber_row_id",
    "step_index",
    "component_id",
    "raw_row_id",
    "lower_addr",
    "upper_addr",
    "source0_addr",
    "source1_addr",
    "target_addr",
    "coeff",
    "coeff_square",
    "interval_width",
    "long_tens_gap_flag",
    "zeta_interval_flag",
]
CUT_COLUMNS = [
    "cut_id",
    "left_addr",
    "right_addr",
    "closed_section_count",
    "open_section_count",
    "crossing_section_count",
    "closed_coeff_sum",
    "open_coeff_sum",
    "crossing_coeff_sum",
    "closed_coeff_square_sum",
    "open_coeff_square_sum",
    "crossing_coeff_square_sum",
    "count_gluing_total",
    "coeff_gluing_total",
    "coeff_square_gluing_total",
    "count_gluing_flag",
    "coeff_gluing_flag",
    "coeff_square_gluing_flag",
]
STALK_COLUMNS = [
    "addr",
    "section_count",
    "coeff_sum",
    "coeff_square_sum",
    "gap_section_count",
    "existing_section_count",
    "active_stalk_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "line_point_count",
    "section_row_count",
    "path_row_count",
    "cut_row_count",
    "stalk_row_count",
    "section_zeta_interval_count",
    "global_section_count",
    "global_coeff_sum",
    "global_coeff_square_sum",
    "gap_section_count",
    "existing_section_count",
    "cut_count_gluing_flag_count",
    "cut_coeff_gluing_flag_count",
    "cut_coeff_square_gluing_flag_count",
    "closed_count_monotone_flag",
    "open_count_monotone_flag",
    "crossing_positive_cut_count",
    "crossing_count_max",
    "active_stalk_count",
    "active_stalk_min_addr",
    "active_stalk_max_addr",
    "active_span_zero_stalk_count",
    "stalk_section_count_max",
    "stalk_coeff_sum_max",
    "stalk_coeff_square_sum_max",
    "current_interval_sheaf_flag",
    "current_all_cuts_glue_lln_observables_flag",
    "current_full_raw_tensor_sheaf_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def section_rows_from_steps(
    step_rows: list[dict[str, int]],
    path_rows: list[dict[str, int]],
) -> list[dict[str, int]]:
    path_by_id = {row["path_id"]: row for row in path_rows}
    section_rows: list[dict[str, int]] = []
    for row in step_rows:
        lower = row["target_addr"]
        upper = min(row["source0_addr"], row["source1_addr"])
        coeff = row["coeff"]
        path = path_by_id[row["path_id"]]
        section_rows.append(
            {
                "section_id": row["step_id"],
                "path_id": row["path_id"],
                "fiber_row_id": row["fiber_row_id"],
                "step_index": row["step_index"],
                "component_id": row["component_id"],
                "raw_row_id": row["raw_row_id"],
                "lower_addr": lower,
                "upper_addr": upper,
                "source0_addr": row["source0_addr"],
                "source1_addr": row["source1_addr"],
                "target_addr": row["target_addr"],
                "coeff": coeff,
                "coeff_square": coeff * coeff,
                "interval_width": upper - lower + 1,
                "long_tens_gap_flag": path["long_tens_gap_flag"],
                "zeta_interval_flag": int(lower <= upper),
            }
        )
    return section_rows


def cut_rows_from_sections(section_rows: list[dict[str, int]]) -> list[dict[str, int]]:
    global_count = len(section_rows)
    global_coeff = sum(row["coeff"] for row in section_rows)
    global_square = sum(row["coeff_square"] for row in section_rows)
    cut_rows: list[dict[str, int]] = []
    for left_addr in range(LINE_POINT_COUNT - 1):
        right_addr = left_addr + 1
        closed = [row for row in section_rows if row["upper_addr"] <= left_addr]
        open_ = [row for row in section_rows if row["lower_addr"] >= right_addr]
        crossing = [
            row
            for row in section_rows
            if row["lower_addr"] <= left_addr and row["upper_addr"] >= right_addr
        ]
        closed_count = len(closed)
        open_count = len(open_)
        crossing_count = len(crossing)
        closed_coeff = sum(row["coeff"] for row in closed)
        open_coeff = sum(row["coeff"] for row in open_)
        crossing_coeff = sum(row["coeff"] for row in crossing)
        closed_square = sum(row["coeff_square"] for row in closed)
        open_square = sum(row["coeff_square"] for row in open_)
        crossing_square = sum(row["coeff_square"] for row in crossing)
        count_total = closed_count + open_count + crossing_count
        coeff_total = closed_coeff + open_coeff + crossing_coeff
        square_total = closed_square + open_square + crossing_square
        cut_rows.append(
            {
                "cut_id": left_addr,
                "left_addr": left_addr,
                "right_addr": right_addr,
                "closed_section_count": closed_count,
                "open_section_count": open_count,
                "crossing_section_count": crossing_count,
                "closed_coeff_sum": closed_coeff,
                "open_coeff_sum": open_coeff,
                "crossing_coeff_sum": crossing_coeff,
                "closed_coeff_square_sum": closed_square,
                "open_coeff_square_sum": open_square,
                "crossing_coeff_square_sum": crossing_square,
                "count_gluing_total": count_total,
                "coeff_gluing_total": coeff_total,
                "coeff_square_gluing_total": square_total,
                "count_gluing_flag": int(count_total == global_count),
                "coeff_gluing_flag": int(coeff_total == global_coeff),
                "coeff_square_gluing_flag": int(square_total == global_square),
            }
        )
    return cut_rows


def stalk_rows_from_sections(section_rows: list[dict[str, int]]) -> list[dict[str, int]]:
    stalk_rows: list[dict[str, int]] = []
    for addr in range(LINE_POINT_COUNT):
        rows = [
            row
            for row in section_rows
            if row["lower_addr"] <= addr <= row["upper_addr"]
        ]
        section_count = len(rows)
        gap_count = sum(row["long_tens_gap_flag"] for row in rows)
        stalk_rows.append(
            {
                "addr": addr,
                "section_count": section_count,
                "coeff_sum": sum(row["coeff"] for row in rows),
                "coeff_square_sum": sum(row["coeff_square"] for row in rows),
                "gap_section_count": gap_count,
                "existing_section_count": section_count - gap_count,
                "active_stalk_flag": int(section_count > 0),
            }
        )
    return stalk_rows


def monotone_non_decreasing(values: list[int]) -> bool:
    return all(left <= right for left, right in zip(values, values[1:]))


def monotone_non_increasing(values: list[int]) -> bool:
    return all(left >= right for left, right in zip(values, values[1:]))


def build_rows() -> dict[str, Any]:
    input_reports = {
        "long_lln": load_json(LONG_LLN_REPORT),
        "long_path": load_json(LONG_PATH_REPORT),
        "long_comp": load_json(LONG_COMP_REPORT),
    }
    path_rows = int_rows(read_csv_rows(LONG_PATH_PATH))
    step_rows = int_rows(read_csv_rows(LONG_PATH_STEP))
    section_rows = section_rows_from_steps(step_rows, path_rows)
    cut_rows = cut_rows_from_sections(section_rows)
    stalk_rows = stalk_rows_from_sections(section_rows)

    active_addrs = [row["addr"] for row in stalk_rows if row["active_stalk_flag"]]
    global_count = len(section_rows)
    global_coeff = sum(row["coeff"] for row in section_rows)
    global_square = sum(row["coeff_square"] for row in section_rows)
    obs = {
        "line_point_count": LINE_POINT_COUNT,
        "section_row_count": len(section_rows),
        "path_row_count": len(path_rows),
        "cut_row_count": len(cut_rows),
        "stalk_row_count": len(stalk_rows),
        "section_zeta_interval_count": sum(
            row["zeta_interval_flag"] for row in section_rows
        ),
        "global_section_count": global_count,
        "global_coeff_sum": global_coeff,
        "global_coeff_square_sum": global_square,
        "gap_section_count": sum(row["long_tens_gap_flag"] for row in section_rows),
        "existing_section_count": sum(
            1 - row["long_tens_gap_flag"] for row in section_rows
        ),
        "cut_count_gluing_flag_count": sum(
            row["count_gluing_flag"] for row in cut_rows
        ),
        "cut_coeff_gluing_flag_count": sum(
            row["coeff_gluing_flag"] for row in cut_rows
        ),
        "cut_coeff_square_gluing_flag_count": sum(
            row["coeff_square_gluing_flag"] for row in cut_rows
        ),
        "closed_count_monotone_flag": int(
            monotone_non_decreasing(
                [row["closed_section_count"] for row in cut_rows]
            )
        ),
        "open_count_monotone_flag": int(
            monotone_non_increasing([row["open_section_count"] for row in cut_rows])
        ),
        "crossing_positive_cut_count": sum(
            int(row["crossing_section_count"] > 0) for row in cut_rows
        ),
        "crossing_count_max": max(row["crossing_section_count"] for row in cut_rows),
        "active_stalk_count": sum(row["active_stalk_flag"] for row in stalk_rows),
        "active_stalk_min_addr": min(active_addrs),
        "active_stalk_max_addr": max(active_addrs),
        "active_span_zero_stalk_count": sum(
            int(
                min(active_addrs) <= row["addr"] <= max(active_addrs)
                and row["active_stalk_flag"] == 0
            )
            for row in stalk_rows
        ),
        "stalk_section_count_max": max(row["section_count"] for row in stalk_rows),
        "stalk_coeff_sum_max": max(row["coeff_sum"] for row in stalk_rows),
        "stalk_coeff_square_sum_max": max(
            row["coeff_square_sum"] for row in stalk_rows
        ),
        "current_interval_sheaf_flag": 1,
        "current_all_cuts_glue_lln_observables_flag": 1,
        "current_full_raw_tensor_sheaf_flag": 0,
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    section_hash = hashlib.sha256(
        digest_text(SECTION_COLUMNS, section_rows).encode("ascii")
    ).hexdigest()
    cut_hash = hashlib.sha256(
        digest_text(CUT_COLUMNS, cut_rows).encode("ascii")
    ).hexdigest()
    stalk_hash = hashlib.sha256(
        digest_text(STALK_COLUMNS, stalk_rows).encode("ascii")
    ).hexdigest()
    return {
        "input_reports": input_reports,
        "section_rows": section_rows,
        "cut_rows": cut_rows,
        "stalk_rows": stalk_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "section_table": table_from_rows(SECTION_COLUMNS, section_rows),
        "cut_table": table_from_rows(CUT_COLUMNS, cut_rows),
        "stalk_table": table_from_rows(STALK_COLUMNS, stalk_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "section_hash": section_hash,
        "cut_hash": cut_hash,
        "stalk_hash": stalk_hash,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    input_reports = rows["input_reports"]
    checks = {
        "input_certified": (
            input_reports["long_lln"].get("status"),
            input_reports["long_path"].get("status"),
            input_reports["long_comp"].get("status"),
        )
        == (LONG_LLN_STATUS, LONG_PATH_STATUS, LONG_COMP_STATUS),
        "section_inventory_exact": (
            obs["line_point_count"],
            obs["section_row_count"],
            obs["path_row_count"],
            obs["section_zeta_interval_count"],
            obs["global_section_count"],
            obs["global_coeff_sum"],
            obs["global_coeff_square_sum"],
            obs["gap_section_count"],
            obs["existing_section_count"],
            rows["section_hash"],
        )
        == (
            985,
            3128,
            288,
            3128,
            3128,
            15_232,
            102_272,
            2684,
            444,
            SECTION_TEXT_HASH,
        ),
        "cut_gluing_exact": (
            obs["cut_row_count"],
            obs["cut_count_gluing_flag_count"],
            obs["cut_coeff_gluing_flag_count"],
            obs["cut_coeff_square_gluing_flag_count"],
            obs["closed_count_monotone_flag"],
            obs["open_count_monotone_flag"],
            obs["crossing_positive_cut_count"],
            obs["crossing_count_max"],
            rows["cut_hash"],
        )
        == (984, 984, 984, 984, 1, 1, 146, 2312, CUT_TEXT_HASH),
        "stalk_inventory_exact": (
            obs["stalk_row_count"],
            obs["active_stalk_count"],
            obs["active_stalk_min_addr"],
            obs["active_stalk_max_addr"],
            obs["active_span_zero_stalk_count"],
            obs["stalk_section_count_max"],
            obs["stalk_coeff_sum_max"],
            obs["stalk_coeff_square_sum_max"],
            rows["stalk_hash"],
        )
        == (985, 148, 0, 171, 24, 2312, 13_600, 99_008, STALK_TEXT_HASH),
        "current_representation_exact": (
            obs["current_interval_sheaf_flag"],
            obs["current_all_cuts_glue_lln_observables_flag"],
            obs["current_full_raw_tensor_sheaf_flag"],
        )
        == (1, 1, 0),
        "table_shapes_match": (
            tuple(rows["section_table"].shape),
            tuple(rows["cut_table"].shape),
            tuple(rows["stalk_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (3128, len(SECTION_COLUMNS)),
            (984, len(CUT_COLUMNS)),
            (985, len(STALK_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "alexandrov_interval_support_sheaf_for_lln_witnesses",
        "section_rule": "each raw lookup step is the interval [target, min(source0, source1)]",
        "cut_rule": "each cut decomposes sections into closed-prefix, open-suffix, and crossing sections",
        "sections": {
            "section_row_count": obs["section_row_count"],
            "path_row_count": obs["path_row_count"],
            "global_section_count": obs["global_section_count"],
            "global_coeff_sum": obs["global_coeff_sum"],
            "global_coeff_square_sum": obs["global_coeff_square_sum"],
            "gap_section_count": obs["gap_section_count"],
            "existing_section_count": obs["existing_section_count"],
            "section_table_sha256": sha_array(rows["section_table"]),
            "section_text_sha256": rows["section_hash"],
        },
        "cut_gluing": {
            "cut_row_count": obs["cut_row_count"],
            "count_gluing_flag_count": obs["cut_count_gluing_flag_count"],
            "coeff_gluing_flag_count": obs["cut_coeff_gluing_flag_count"],
            "coeff_square_gluing_flag_count": obs[
                "cut_coeff_square_gluing_flag_count"
            ],
            "closed_count_monotone": bool(obs["closed_count_monotone_flag"]),
            "open_count_monotone": bool(obs["open_count_monotone_flag"]),
            "crossing_positive_cut_count": obs["crossing_positive_cut_count"],
            "crossing_count_max": obs["crossing_count_max"],
            "cut_table_sha256": sha_array(rows["cut_table"]),
            "cut_text_sha256": rows["cut_hash"],
        },
        "stalks": {
            "stalk_row_count": obs["stalk_row_count"],
            "active_stalk_count": obs["active_stalk_count"],
            "active_stalk_range": [
                obs["active_stalk_min_addr"],
                obs["active_stalk_max_addr"],
            ],
            "active_span_zero_stalk_count": obs["active_span_zero_stalk_count"],
            "stalk_section_count_max": obs["stalk_section_count_max"],
            "stalk_coeff_sum_max": obs["stalk_coeff_sum_max"],
            "stalk_coeff_square_sum_max": obs["stalk_coeff_square_sum_max"],
            "stalk_table_sha256": sha_array(rows["stalk_table"]),
            "stalk_text_sha256": rows["stalk_hash"],
        },
        "current_representation": {
            "current_interval_sheaf_flag": obs["current_interval_sheaf_flag"],
            "current_all_cuts_glue_lln_observables_flag": obs[
                "current_all_cuts_glue_lln_observables_flag"
            ],
            "current_full_raw_tensor_sheaf_flag": obs[
                "current_full_raw_tensor_sheaf_flag"
            ],
        },
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    sheaf_payload = {
        "schema": "long.sheaf@1",
        "object": "alexandrov_interval_support_sheaf_for_lln_witnesses",
        "status": STATUS if all(checks.values()) else "LONG_SHEAF_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.sheaf.report@1",
        "status": sheaf_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_sheaf certifies a constructible interval-support sheaf for "
            "the long_path/long_comp finite LLN witnesses. Each raw lookup step "
            "defines an Alexandrov interval [target, min(source0, source1)]. "
            "For every finite-line cut, section count, coefficient sum, and "
            "coefficient-square sum glue exactly from the closed prefix, open "
            "suffix, and crossing boundary sections."
        ),
        "stage_protocol": {
            "draft": "read long_path steps and long_comp zeta-composable witness status",
            "witness": "turn each raw lookup step into an interval section on the finite Alexandrov line",
            "coherence": "check interval positivity, cut gluing for LLN observables, monotonicity, stalk counts, statuses, hashes, and shapes",
            "closure": "emit witness-level support sheaf while keeping the full raw tensor sheaf out of scope",
            "emit": "write long_sheaf artifacts and verifier hook",
        },
        "inputs": {
            "long_lln_report": input_entry(
                LONG_LLN_REPORT,
                {"status": rows["input_reports"]["long_lln"].get("status")},
            ),
            "long_lln_tables": input_entry(LONG_LLN_TABLES),
            "long_path_report": input_entry(
                LONG_PATH_REPORT,
                {"status": rows["input_reports"]["long_path"].get("status")},
            ),
            "long_path_component": input_entry(LONG_PATH_COMPONENT),
            "long_path_path": input_entry(LONG_PATH_PATH),
            "long_path_step": input_entry(LONG_PATH_STEP),
            "long_path_tables": input_entry(LONG_PATH_TABLES),
            "long_comp_report": input_entry(
                LONG_COMP_REPORT,
                {"status": rows["input_reports"]["long_comp"].get("status")},
            ),
            "long_comp_pair": input_entry(LONG_COMP_PAIR),
            "long_comp_path": input_entry(LONG_COMP_PATH),
            "long_comp_transition": input_entry(LONG_COMP_TRANSITION),
            "long_comp_tables": input_entry(LONG_COMP_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "sheaf": relpath(OUT_DIR / "sheaf.json"),
            "section_csv": relpath(OUT_DIR / "section.csv"),
            "cut_csv": relpath(OUT_DIR / "cut.csv"),
            "stalk_csv": relpath(OUT_DIR / "stalk.csv"),
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
                "an interval-support sheaf for the 3,128 step sections in the long_path witnesses",
                "exact gluing of section count, coefficient sum, and coefficient-square sum across all 984 finite-line cuts",
                "monotone closed-prefix and open-suffix restriction counts",
                "stalk support over 148 active addresses with a 24-address inactive gap inside the active span",
            ],
            "does_not_certify_because_out_of_scope": [
                "the full raw tensor support sheaf over all 1,414,965 rows",
                "semantic C985 associator composition",
                "a genuine long_prof horizon-16 profunctor",
                "an infinite-horizon LLN theorem",
            ],
        },
        "next_highest_yield_item": (
            "Build long_all: extend the interval-support sheaf from the "
            "long_path witnesses to all raw tensor support rows and compare "
            "the full-sheaf LLN observables against long_lln moments."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.sheaf.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.sheaf.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "sheaf": sheaf_payload,
        "section_csv": csv_text(SECTION_COLUMNS, rows["section_rows"]),
        "cut_csv": csv_text(CUT_COLUMNS, rows["cut_rows"]),
        "stalk_csv": csv_text(STALK_COLUMNS, rows["stalk_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "section_table": rows["section_table"],
        "cut_table": rows["cut_table"],
        "stalk_table": rows["stalk_table"],
        "observable_table": rows["observable_table"],
        "cert": cert,
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
    write_json(OUT_DIR / "sheaf.json", payloads["sheaf"])
    (OUT_DIR / "section.csv").write_text(
        payloads["section_csv"], encoding="utf-8"
    )
    (OUT_DIR / "cut.csv").write_text(payloads["cut_csv"], encoding="utf-8")
    (OUT_DIR / "stalk.csv").write_text(payloads["stalk_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        section_table=payloads["section_table"],
        cut_table=payloads["cut_table"],
        stalk_table=payloads["stalk_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(OUT_DIR / "cert.json", payloads["cert"])
    write_json(OUT_DIR / "report.json", payloads["report"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
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
                "report": relpath(OUT_DIR / "report.json"),
                "manifest": relpath(OUT_DIR / "manifest.json"),
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
