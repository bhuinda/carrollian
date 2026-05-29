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
    from .derive_long_domind import (
        BRIDGE_COLUMNS as LONG_DOMIND_BRIDGE_COLUMNS,
        COVER_COLUMNS as LONG_DOMIND_COVER_COLUMNS,
        FORMULA_COLUMNS as LONG_DOMIND_FORMULA_COLUMNS,
        OUT_DIR as LONG_DOMIND_DIR,
        STATUS as LONG_DOMIND_STATUS,
    )
    from .derive_long_formind import (
        BRIDGE_COLUMNS as LONG_FORMIND_BRIDGE_COLUMNS,
        CHECK_COLUMNS as LONG_FORMIND_CHECK_COLUMNS,
        CLASS_COLUMNS as LONG_FORMIND_CLASS_COLUMNS,
        OUT_DIR as LONG_FORMIND_DIR,
        STATUS as LONG_FORMIND_STATUS,
        TERM_COLUMNS as LONG_FORMIND_TERM_COLUMNS,
    )
    from .derive_long_raw import (
        csv_text,
        digest_text,
        int_rows,
        read_csv_rows,
        table_from_rows,
    )
    from .derive_long_recind import (
        BRIDGE_COLUMNS as LONG_RECIND_BRIDGE_COLUMNS,
        OUT_DIR as LONG_RECIND_DIR,
        SEED_COLUMNS as LONG_RECIND_SEED_COLUMNS,
        STATUS as LONG_RECIND_STATUS,
        TRANSITION_COLUMNS as LONG_RECIND_TRANSITION_COLUMNS,
        TYPE_SUMMARY_COLUMNS as LONG_RECIND_TYPE_SUMMARY_COLUMNS,
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
    from derive_long_domind import (
        BRIDGE_COLUMNS as LONG_DOMIND_BRIDGE_COLUMNS,
        COVER_COLUMNS as LONG_DOMIND_COVER_COLUMNS,
        FORMULA_COLUMNS as LONG_DOMIND_FORMULA_COLUMNS,
        OUT_DIR as LONG_DOMIND_DIR,
        STATUS as LONG_DOMIND_STATUS,
    )
    from derive_long_formind import (
        BRIDGE_COLUMNS as LONG_FORMIND_BRIDGE_COLUMNS,
        CHECK_COLUMNS as LONG_FORMIND_CHECK_COLUMNS,
        CLASS_COLUMNS as LONG_FORMIND_CLASS_COLUMNS,
        OUT_DIR as LONG_FORMIND_DIR,
        STATUS as LONG_FORMIND_STATUS,
        TERM_COLUMNS as LONG_FORMIND_TERM_COLUMNS,
    )
    from derive_long_raw import (
        csv_text,
        digest_text,
        int_rows,
        read_csv_rows,
        table_from_rows,
    )
    from derive_long_recind import (
        BRIDGE_COLUMNS as LONG_RECIND_BRIDGE_COLUMNS,
        OUT_DIR as LONG_RECIND_DIR,
        SEED_COLUMNS as LONG_RECIND_SEED_COLUMNS,
        STATUS as LONG_RECIND_STATUS,
        TRANSITION_COLUMNS as LONG_RECIND_TRANSITION_COLUMNS,
        TYPE_SUMMARY_COLUMNS as LONG_RECIND_TYPE_SUMMARY_COLUMNS,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_gapind"
STATUS = "LONG_GAPIND_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

LONG_RECIND_REPORT = LONG_RECIND_DIR / "report.json"
LONG_RECIND_SEED = LONG_RECIND_DIR / "seed.csv"
LONG_RECIND_TRANSITION = LONG_RECIND_DIR / "transition.csv"
LONG_RECIND_TYPE_SUMMARY = LONG_RECIND_DIR / "type_summary.csv"
LONG_RECIND_BRIDGE = LONG_RECIND_DIR / "bridge.csv"
LONG_RECIND_TABLES = LONG_RECIND_DIR / "tables.npz"

LONG_FORMIND_REPORT = LONG_FORMIND_DIR / "report.json"
LONG_FORMIND_CLASS = LONG_FORMIND_DIR / "class.csv"
LONG_FORMIND_TERM = LONG_FORMIND_DIR / "term.csv"
LONG_FORMIND_CHECK = LONG_FORMIND_DIR / "check.csv"
LONG_FORMIND_BRIDGE = LONG_FORMIND_DIR / "bridge.csv"
LONG_FORMIND_TABLES = LONG_FORMIND_DIR / "tables.npz"

LONG_DOMIND_REPORT = LONG_DOMIND_DIR / "report.json"
LONG_DOMIND_FORMULA = LONG_DOMIND_DIR / "formula.csv"
LONG_DOMIND_COVER = LONG_DOMIND_DIR / "cover.csv"
LONG_DOMIND_BRIDGE = LONG_DOMIND_DIR / "bridge.csv"
LONG_DOMIND_TABLES = LONG_DOMIND_DIR / "tables.npz"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_gapind.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_gapind.py"

INDUCTION_START = 16
FINITE_START = 17
FINITE_END = 127
PROBE_START = 128
PROBE_END = 256
TAIL_START = 257
RECURRENCE_FACTOR = 12

REGIME_TEXT_HASH = "de5fedcabec4b22ebaadd62f60319bb3cbdc9f67f5876b14f2faea176528b389"
BRIDGE_TEXT_HASH = "0fc3d55d1817466fd20fda84fa2238fef3b06af27c97dc24141c08dbd741dd67"

REGIME_COLUMNS = [
    "regime_id",
    "regime_code",
    "start_sample_count",
    "end_sample_count",
    "state_count",
    "gap_check_count",
    "nonnegative_count",
    "zero_count",
    "source_certificate_code",
    "regime_certificate_flag",
]
BRIDGE_COLUMNS = [
    "bridge_id",
    "regime_count",
    "induction_start",
    "finite_start_sample_count",
    "finite_end_sample_count",
    "probe_start_sample_count",
    "probe_end_sample_count",
    "tail_start_sample_count",
    "recurrence_factor",
    "seed_state_count",
    "finite_transition_count",
    "formula_class_count",
    "formula_count",
    "probe_state_count",
    "tail_formula_count",
    "finite_gap_check_count",
    "finite_gap_nonnegative_count",
    "recind_certified_flag",
    "formind_certified_flag",
    "domind_certified_flag",
    "seed_to_finite_seam_flag",
    "finite_to_probe_seam_flag",
    "probe_to_tail_seam_flag",
    "formula_tail_match_flag",
    "global_gapind_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "regime_count",
    "induction_start",
    "finite_start_sample_count",
    "finite_end_sample_count",
    "probe_start_sample_count",
    "probe_end_sample_count",
    "tail_start_sample_count",
    "recurrence_factor",
    "seed_state_count",
    "seed_gap_nonnegative_count",
    "finite_transition_count",
    "finite_delta_nonnegative_count",
    "finite_delta_zero_count",
    "formula_class_count",
    "formula_count",
    "probe_state_count",
    "probe_formula_eval_count",
    "probe_formula_nonnegative_count",
    "probe_formula_zero_count",
    "tail_formula_nonnegative_count",
    "cover_assignment_count",
    "finite_gap_check_count",
    "finite_gap_nonnegative_count",
    "recind_certified_flag",
    "formind_certified_flag",
    "domind_certified_flag",
    "seed_to_finite_seam_flag",
    "finite_to_probe_seam_flag",
    "probe_to_tail_seam_flag",
    "formula_tail_match_flag",
    "current_gapind_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def read_int_csv(path: Any) -> list[dict[str, int]]:
    return int_rows(read_csv_rows(path))


def build_rows() -> dict[str, Any]:
    recind_report = load_json(LONG_RECIND_REPORT)
    formind_report = load_json(LONG_FORMIND_REPORT)
    domind_report = load_json(LONG_DOMIND_REPORT)
    seed_rows = read_int_csv(LONG_RECIND_SEED)
    transition_rows = read_int_csv(LONG_RECIND_TRANSITION)
    type_rows = read_int_csv(LONG_RECIND_TYPE_SUMMARY)
    formind_class_rows = read_int_csv(LONG_FORMIND_CLASS)
    formind_check_rows = read_int_csv(LONG_FORMIND_CHECK)
    formind_bridge_rows = read_int_csv(LONG_FORMIND_BRIDGE)
    domind_formula_rows = read_int_csv(LONG_DOMIND_FORMULA)
    domind_cover_rows = read_int_csv(LONG_DOMIND_COVER)
    domind_bridge_rows = read_int_csv(LONG_DOMIND_BRIDGE)

    seed_state_count = len(seed_rows)
    seed_gap_nonnegative_count = sum(
        int(row["lower_gap_sign"] >= 0) + int(row["upper_gap_sign"] >= 0)
        for row in seed_rows
    )
    seed_zero_count = sum(
        row["lower_gap_zero_flag"] + row["upper_gap_zero_flag"]
        for row in seed_rows
    )
    seed_certified = int(
        seed_state_count == 33
        and seed_gap_nonnegative_count == 2 * seed_state_count
        and sum(row["seed_certificate_flag"] for row in seed_rows) == seed_state_count
    )

    finite_transition_count = len(transition_rows)
    finite_delta_nonnegative_count = sum(
        int(row["lower_delta_sign"] >= 0) + int(row["upper_delta_sign"] >= 0)
        for row in transition_rows
    )
    finite_delta_zero_count = sum(
        row["lower_delta_zero_flag"] + row["upper_delta_zero_flag"]
        for row in transition_rows
    )
    finite_certified = int(
        finite_transition_count == 16_095
        and finite_delta_nonnegative_count == 2 * finite_transition_count
        and sum(row["transition_certificate_flag"] for row in transition_rows)
        == finite_transition_count
        and min(row["successor_sample_count"] for row in transition_rows)
        == FINITE_START
        and max(row["successor_sample_count"] for row in transition_rows)
        == FINITE_END
        and {row["recurrence_factor"] for row in transition_rows}
        == {RECURRENCE_FACTOR}
    )

    formind_bridge = formind_bridge_rows[0]
    probe_state_count = formind_bridge["probe_state_count"]
    probe_formula_eval_count = sum(row["probe_state_count"] for row in formind_check_rows)
    probe_formula_nonnegative_count = sum(
        row["probe_nonnegative_count"] for row in formind_check_rows
    )
    probe_formula_zero_count = sum(row["probe_zero_count"] for row in formind_check_rows)
    probe_certified = int(
        formind_bridge["probe_start_sample_count"] == PROBE_START
        and formind_bridge["probe_end_sample_count"] == PROBE_END
        and probe_state_count == 49_665
        and probe_formula_eval_count == 99_330
        and probe_formula_nonnegative_count == probe_formula_eval_count
        and sum(row["formula_certificate_flag"] for row in formind_check_rows)
        == len(formind_check_rows)
    )

    domind_bridge = domind_bridge_rows[0]
    tail_formula_nonnegative_count = domind_bridge["formula_tail_nonnegative_count"]
    cover_assignment_count = len(domind_cover_rows)
    tail_certified = int(
        domind_bridge["tail_start_sample_count"] == TAIL_START
        and tail_formula_nonnegative_count == len(domind_formula_rows)
        and domind_bridge["covered_negative_term_count"]
        == domind_bridge["negative_term_count"]
        and domind_bridge["lower_ray_certificate_count"] == cover_assignment_count
        and domind_bridge["upper_ray_certificate_count"] == cover_assignment_count
        and sum(row["tail_nonnegative_flag"] for row in domind_formula_rows)
        == len(domind_formula_rows)
    )

    formula_class_count = len(formind_class_rows)
    formula_count = len(formind_check_rows)
    tail_formula_count = len(domind_formula_rows)
    finite_gap_check_count = (
        2 * seed_state_count + 2 * finite_transition_count + probe_formula_eval_count
    )
    finite_gap_nonnegative_count = (
        seed_gap_nonnegative_count
        + finite_delta_nonnegative_count
        + probe_formula_nonnegative_count
    )
    recind_certified = int(recind_report.get("status") == LONG_RECIND_STATUS)
    formind_certified = int(formind_report.get("status") == LONG_FORMIND_STATUS)
    domind_certified = int(domind_report.get("status") == LONG_DOMIND_STATUS)
    seed_to_finite_seam = int(FINITE_START == INDUCTION_START + 1)
    finite_to_probe_seam = int(PROBE_START == FINITE_END + 1)
    probe_to_tail_seam = int(TAIL_START == PROBE_END + 1)
    formula_tail_match = int(
        formula_count == tail_formula_count
        and formind_bridge["formula_count"] == domind_bridge["formula_count"]
    )
    current_gapind = int(
        recind_certified
        and formind_certified
        and domind_certified
        and seed_certified
        and finite_certified
        and probe_certified
        and tail_certified
        and len(type_rows) == 10
        and formula_class_count == 13
        and formula_tail_match
        and seed_to_finite_seam
        and finite_to_probe_seam
        and probe_to_tail_seam
    )

    regime_rows = [
        {
            "regime_id": 0,
            "regime_code": 0,
            "start_sample_count": INDUCTION_START,
            "end_sample_count": INDUCTION_START,
            "state_count": seed_state_count,
            "gap_check_count": 2 * seed_state_count,
            "nonnegative_count": seed_gap_nonnegative_count,
            "zero_count": seed_zero_count,
            "source_certificate_code": 0,
            "regime_certificate_flag": seed_certified,
        },
        {
            "regime_id": 1,
            "regime_code": 1,
            "start_sample_count": FINITE_START,
            "end_sample_count": FINITE_END,
            "state_count": finite_transition_count,
            "gap_check_count": 2 * finite_transition_count,
            "nonnegative_count": finite_delta_nonnegative_count,
            "zero_count": finite_delta_zero_count,
            "source_certificate_code": 0,
            "regime_certificate_flag": finite_certified,
        },
        {
            "regime_id": 2,
            "regime_code": 2,
            "start_sample_count": PROBE_START,
            "end_sample_count": PROBE_END,
            "state_count": probe_state_count,
            "gap_check_count": probe_formula_eval_count,
            "nonnegative_count": probe_formula_nonnegative_count,
            "zero_count": probe_formula_zero_count,
            "source_certificate_code": 1,
            "regime_certificate_flag": probe_certified,
        },
        {
            "regime_id": 3,
            "regime_code": 3,
            "start_sample_count": TAIL_START,
            "end_sample_count": -1,
            "state_count": -1,
            "gap_check_count": tail_formula_count,
            "nonnegative_count": tail_formula_nonnegative_count,
            "zero_count": -1,
            "source_certificate_code": 2,
            "regime_certificate_flag": tail_certified,
        },
    ]
    bridge_rows = [
        {
            "bridge_id": 0,
            "regime_count": len(regime_rows),
            "induction_start": INDUCTION_START,
            "finite_start_sample_count": FINITE_START,
            "finite_end_sample_count": FINITE_END,
            "probe_start_sample_count": PROBE_START,
            "probe_end_sample_count": PROBE_END,
            "tail_start_sample_count": TAIL_START,
            "recurrence_factor": RECURRENCE_FACTOR,
            "seed_state_count": seed_state_count,
            "finite_transition_count": finite_transition_count,
            "formula_class_count": formula_class_count,
            "formula_count": formula_count,
            "probe_state_count": probe_state_count,
            "tail_formula_count": tail_formula_count,
            "finite_gap_check_count": finite_gap_check_count,
            "finite_gap_nonnegative_count": finite_gap_nonnegative_count,
            "recind_certified_flag": recind_certified,
            "formind_certified_flag": formind_certified,
            "domind_certified_flag": domind_certified,
            "seed_to_finite_seam_flag": seed_to_finite_seam,
            "finite_to_probe_seam_flag": finite_to_probe_seam,
            "probe_to_tail_seam_flag": probe_to_tail_seam,
            "formula_tail_match_flag": formula_tail_match,
            "global_gapind_flag": current_gapind,
        }
    ]
    obs = {
        "regime_count": len(regime_rows),
        "induction_start": INDUCTION_START,
        "finite_start_sample_count": FINITE_START,
        "finite_end_sample_count": FINITE_END,
        "probe_start_sample_count": PROBE_START,
        "probe_end_sample_count": PROBE_END,
        "tail_start_sample_count": TAIL_START,
        "recurrence_factor": RECURRENCE_FACTOR,
        "seed_state_count": seed_state_count,
        "seed_gap_nonnegative_count": seed_gap_nonnegative_count,
        "finite_transition_count": finite_transition_count,
        "finite_delta_nonnegative_count": finite_delta_nonnegative_count,
        "finite_delta_zero_count": finite_delta_zero_count,
        "formula_class_count": formula_class_count,
        "formula_count": formula_count,
        "probe_state_count": probe_state_count,
        "probe_formula_eval_count": probe_formula_eval_count,
        "probe_formula_nonnegative_count": probe_formula_nonnegative_count,
        "probe_formula_zero_count": probe_formula_zero_count,
        "tail_formula_nonnegative_count": tail_formula_nonnegative_count,
        "cover_assignment_count": cover_assignment_count,
        "finite_gap_check_count": finite_gap_check_count,
        "finite_gap_nonnegative_count": finite_gap_nonnegative_count,
        "recind_certified_flag": recind_certified,
        "formind_certified_flag": formind_certified,
        "domind_certified_flag": domind_certified,
        "seed_to_finite_seam_flag": seed_to_finite_seam,
        "finite_to_probe_seam_flag": finite_to_probe_seam,
        "probe_to_tail_seam_flag": probe_to_tail_seam,
        "formula_tail_match_flag": formula_tail_match,
        "current_gapind_flag": current_gapind,
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    regime_hash = hashlib.sha256(
        digest_text(REGIME_COLUMNS, regime_rows).encode("ascii")
    ).hexdigest()
    bridge_hash = hashlib.sha256(
        digest_text(BRIDGE_COLUMNS, bridge_rows).encode("ascii")
    ).hexdigest()
    return {
        "regime_rows": regime_rows,
        "bridge_rows": bridge_rows,
        "obs_rows": obs_rows,
        "regime_table": table_from_rows(REGIME_COLUMNS, regime_rows),
        "bridge_table": table_from_rows(BRIDGE_COLUMNS, bridge_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "regime_hash": regime_hash,
        "bridge_hash": bridge_hash,
        "obs": obs,
        "input_reports": {
            "long_recind": recind_report,
            "long_formind": formind_report,
            "long_domind": domind_report,
        },
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_certified": (
            obs["recind_certified_flag"],
            obs["formind_certified_flag"],
            obs["domind_certified_flag"],
        )
        == (1, 1, 1),
        "regime_surface_exact": (
            obs["regime_count"],
            obs["induction_start"],
            obs["finite_start_sample_count"],
            obs["finite_end_sample_count"],
            obs["probe_start_sample_count"],
            obs["probe_end_sample_count"],
            obs["tail_start_sample_count"],
            rows["regime_hash"],
        )
        == (4, 16, 17, 127, 128, 256, 257, REGIME_TEXT_HASH),
        "gap_counts_exact": (
            obs["seed_state_count"],
            obs["seed_gap_nonnegative_count"],
            obs["finite_transition_count"],
            obs["finite_delta_nonnegative_count"],
            obs["probe_state_count"],
            obs["probe_formula_eval_count"],
            obs["probe_formula_nonnegative_count"],
            obs["tail_formula_nonnegative_count"],
            obs["cover_assignment_count"],
            rows["bridge_hash"],
        )
        == (
            33,
            66,
            16_095,
            32_190,
            49_665,
            99_330,
            99_330,
            26,
            306,
            BRIDGE_TEXT_HASH,
        ),
        "seams_exact": (
            obs["seed_to_finite_seam_flag"],
            obs["finite_to_probe_seam_flag"],
            obs["probe_to_tail_seam_flag"],
            obs["formula_tail_match_flag"],
        )
        == (1, 1, 1, 1),
        "current_gapind_exact": obs["current_gapind_flag"] == 1,
        "table_shapes_match": (
            tuple(rows["regime_table"].shape),
            tuple(rows["bridge_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (4, len(REGIME_COLUMNS)),
            (1, len(BRIDGE_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "global_support_gap_induction_assembly",
        "regimes": {
            "induction_start": INDUCTION_START,
            "finite_transition_range": [FINITE_START, FINITE_END],
            "formula_probe_range": [PROBE_START, PROBE_END],
            "tail_start": TAIL_START,
            "regime_text_sha256": rows["regime_hash"],
            "regime_table_sha256": sha_array(rows["regime_table"]),
        },
        "gap_induction": {
            "recurrence_factor": RECURRENCE_FACTOR,
            "seed_state_count": obs["seed_state_count"],
            "finite_transition_count": obs["finite_transition_count"],
            "formula_class_count": obs["formula_class_count"],
            "formula_count": obs["formula_count"],
            "probe_state_count": obs["probe_state_count"],
            "tail_formula_nonnegative_count": obs[
                "tail_formula_nonnegative_count"
            ],
            "finite_gap_check_count": obs["finite_gap_check_count"],
            "finite_gap_nonnegative_count": obs[
                "finite_gap_nonnegative_count"
            ],
            "bridge_text_sha256": rows["bridge_hash"],
            "bridge_table_sha256": sha_array(rows["bridge_table"]),
        },
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    gapind_payload = {
        "schema": "long.gapind@1",
        "object": "global_support_gap_induction_assembly",
        "status": STATUS if all(checks.values()) else "LONG_GAPIND_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.gapind.report@1",
        "status": gapind_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_gapind assembles the certified support-gap induction into one "
            "four-regime certificate: nonnegative n=16 seeds, finite recurrence "
            "deltas through n=127, formula-probe recurrence deltas through n=256, "
            "and tail dominance for every remaining formula class from n=257 on."
        ),
        "stage_protocol": {
            "draft": "read recind, formind, and domind certificate regimes",
            "witness": "align seed, finite recurrence, formula probe, and infinite tail seams",
            "coherence": "check statuses, counts, nonnegative regimes, seam continuity, hashes, and shapes",
            "closure": "emit the global support-gap induction assembly while preserving remaining theorem boundaries",
            "emit": "write long_gapind artifacts and verifier hook",
        },
        "inputs": {
            "long_recind_report": input_entry(
                LONG_RECIND_REPORT,
                {"status": rows["input_reports"]["long_recind"].get("status")},
            ),
            "long_recind_seed": input_entry(
                LONG_RECIND_SEED,
                {"columns": LONG_RECIND_SEED_COLUMNS},
            ),
            "long_recind_transition": input_entry(
                LONG_RECIND_TRANSITION,
                {"columns": LONG_RECIND_TRANSITION_COLUMNS},
            ),
            "long_recind_type_summary": input_entry(
                LONG_RECIND_TYPE_SUMMARY,
                {"columns": LONG_RECIND_TYPE_SUMMARY_COLUMNS},
            ),
            "long_recind_bridge": input_entry(
                LONG_RECIND_BRIDGE,
                {"columns": LONG_RECIND_BRIDGE_COLUMNS},
            ),
            "long_recind_tables": input_entry(LONG_RECIND_TABLES),
            "long_formind_report": input_entry(
                LONG_FORMIND_REPORT,
                {"status": rows["input_reports"]["long_formind"].get("status")},
            ),
            "long_formind_class": input_entry(
                LONG_FORMIND_CLASS,
                {"columns": LONG_FORMIND_CLASS_COLUMNS},
            ),
            "long_formind_term": input_entry(
                LONG_FORMIND_TERM,
                {"columns": LONG_FORMIND_TERM_COLUMNS},
            ),
            "long_formind_check": input_entry(
                LONG_FORMIND_CHECK,
                {"columns": LONG_FORMIND_CHECK_COLUMNS},
            ),
            "long_formind_bridge": input_entry(
                LONG_FORMIND_BRIDGE,
                {"columns": LONG_FORMIND_BRIDGE_COLUMNS},
            ),
            "long_formind_tables": input_entry(LONG_FORMIND_TABLES),
            "long_domind_report": input_entry(
                LONG_DOMIND_REPORT,
                {"status": rows["input_reports"]["long_domind"].get("status")},
            ),
            "long_domind_formula": input_entry(
                LONG_DOMIND_FORMULA,
                {"columns": LONG_DOMIND_FORMULA_COLUMNS},
            ),
            "long_domind_cover": input_entry(
                LONG_DOMIND_COVER,
                {"columns": LONG_DOMIND_COVER_COLUMNS},
            ),
            "long_domind_bridge": input_entry(
                LONG_DOMIND_BRIDGE,
                {"columns": LONG_DOMIND_BRIDGE_COLUMNS},
            ),
            "long_domind_tables": input_entry(LONG_DOMIND_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "gapind": relpath(OUT_DIR / "gapind.json"),
            "regime_csv": relpath(OUT_DIR / "regime.csv"),
            "bridge_csv": relpath(OUT_DIR / "bridge.csv"),
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
                "global symbolic support-gap induction across all encoded recurrence regimes",
                "nonnegative n=16 seed lower/upper support gaps",
                "nonnegative recurrence deltas through the finite recind range n=17..127",
                "nonnegative formula-probe deltas across n=128..256",
                "tail nonnegativity of every recurrence formula class for n>=257",
            ],
            "does_not_certify_because_out_of_scope": [
                "semantic associator composition",
                "the full component-word measure",
                "a raw tensor table materialized in the infinite tail",
                "the final tensor-lookup LLN theorem without the remaining global assembly layer",
            ],
        },
        "next_highest_yield_item": (
            "Build long_llnind: connect the global support-gap induction back to "
            "the finite profunctor tensor-lookup LLN objects as a single theorem-level "
            "certificate."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.gapind.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.gapind.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "gapind": gapind_payload,
        "regime_csv": csv_text(REGIME_COLUMNS, rows["regime_rows"]),
        "bridge_csv": csv_text(BRIDGE_COLUMNS, rows["bridge_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "regime_table": rows["regime_table"],
        "bridge_table": rows["bridge_table"],
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
    write_json(OUT_DIR / "gapind.json", payloads["gapind"])
    (OUT_DIR / "regime.csv").write_text(payloads["regime_csv"], encoding="utf-8")
    (OUT_DIR / "bridge.csv").write_text(payloads["bridge_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        regime_table=payloads["regime_table"],
        bridge_table=payloads["bridge_table"],
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
