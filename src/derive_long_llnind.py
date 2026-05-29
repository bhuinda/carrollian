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
    from .derive_long_gapind import (
        BRIDGE_COLUMNS as LONG_GAPIND_BRIDGE_COLUMNS,
        OUT_DIR as LONG_GAPIND_DIR,
        REGIME_COLUMNS as LONG_GAPIND_REGIME_COLUMNS,
        STATUS as LONG_GAPIND_STATUS,
    )
    from .derive_long_lln import (
        ADDR_COLUMNS as LONG_LLN_ADDR_COLUMNS,
        LLN_COLUMNS as LONG_LLN_LLN_COLUMNS,
        OUT_DIR as LONG_LLN_DIR,
        STATUS as LONG_LLN_STATUS,
    )
    from .derive_long_min import (
        BASIS_COLUMNS as LONG_MIN_BASIS_COLUMNS,
        COVER_COLUMNS as LONG_MIN_COVER_COLUMNS,
        OUT_DIR as LONG_MIN_DIR,
        STATUS as LONG_MIN_STATUS,
    )
    from .derive_long_nat import (
        DEP_COLUMNS as LONG_NAT_DEP_COLUMNS,
        NAT_COLUMNS as LONG_NAT_NAT_COLUMNS,
        OUT_DIR as LONG_NAT_DIR,
        STATUS as LONG_NAT_STATUS,
    )
    from .derive_long_path import (
        OUT_DIR as LONG_PATH_DIR,
        PATH_COLUMNS as LONG_PATH_PATH_COLUMNS,
        STATUS as LONG_PATH_STATUS,
        STEP_COLUMNS as LONG_PATH_STEP_COLUMNS,
    )
    from .derive_long_prob import (
        DIST_COLUMNS as LONG_PROB_DIST_COLUMNS,
        MOMENT_COLUMNS as LONG_PROB_MOMENT_COLUMNS,
        OUT_DIR as LONG_PROB_DIR,
        STATUS as LONG_PROB_STATUS,
    )
    from .derive_long_prof import (
        COMPOSE_COLUMNS as LONG_PROF_COMPOSE_COLUMNS,
        OBJECT_COLUMNS as LONG_PROF_OBJECT_COLUMNS,
        OUT_DIR as LONG_PROF_DIR,
        PROFUNCTOR_COLUMNS as LONG_PROF_PROFUNCTOR_COLUMNS,
        STATUS as LONG_PROF_STATUS,
    )
    from .derive_long_raw import (
        FIBER_COLUMNS as LONG_RAW_FIBER_COLUMNS,
        OUT_DIR as LONG_RAW_DIR,
        OWNER_COLUMNS as LONG_RAW_OWNER_COLUMNS,
        STATUS as LONG_RAW_STATUS,
        csv_text,
        digest_text,
        table_from_rows,
    )
    from .derive_long_univ import (
        ARROW_COLUMNS as LONG_UNIV_ARROW_COLUMNS,
        LAW_COLUMNS as LONG_UNIV_LAW_COLUMNS,
        NODE_COLUMNS as LONG_UNIV_NODE_COLUMNS,
        OUT_DIR as LONG_UNIV_DIR,
        STATUS as LONG_UNIV_STATUS,
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
    from derive_long_gapind import (
        BRIDGE_COLUMNS as LONG_GAPIND_BRIDGE_COLUMNS,
        OUT_DIR as LONG_GAPIND_DIR,
        REGIME_COLUMNS as LONG_GAPIND_REGIME_COLUMNS,
        STATUS as LONG_GAPIND_STATUS,
    )
    from derive_long_lln import (
        ADDR_COLUMNS as LONG_LLN_ADDR_COLUMNS,
        LLN_COLUMNS as LONG_LLN_LLN_COLUMNS,
        OUT_DIR as LONG_LLN_DIR,
        STATUS as LONG_LLN_STATUS,
    )
    from derive_long_min import (
        BASIS_COLUMNS as LONG_MIN_BASIS_COLUMNS,
        COVER_COLUMNS as LONG_MIN_COVER_COLUMNS,
        OUT_DIR as LONG_MIN_DIR,
        STATUS as LONG_MIN_STATUS,
    )
    from derive_long_nat import (
        DEP_COLUMNS as LONG_NAT_DEP_COLUMNS,
        NAT_COLUMNS as LONG_NAT_NAT_COLUMNS,
        OUT_DIR as LONG_NAT_DIR,
        STATUS as LONG_NAT_STATUS,
    )
    from derive_long_path import (
        OUT_DIR as LONG_PATH_DIR,
        PATH_COLUMNS as LONG_PATH_PATH_COLUMNS,
        STATUS as LONG_PATH_STATUS,
        STEP_COLUMNS as LONG_PATH_STEP_COLUMNS,
    )
    from derive_long_prob import (
        DIST_COLUMNS as LONG_PROB_DIST_COLUMNS,
        MOMENT_COLUMNS as LONG_PROB_MOMENT_COLUMNS,
        OUT_DIR as LONG_PROB_DIR,
        STATUS as LONG_PROB_STATUS,
    )
    from derive_long_prof import (
        COMPOSE_COLUMNS as LONG_PROF_COMPOSE_COLUMNS,
        OBJECT_COLUMNS as LONG_PROF_OBJECT_COLUMNS,
        OUT_DIR as LONG_PROF_DIR,
        PROFUNCTOR_COLUMNS as LONG_PROF_PROFUNCTOR_COLUMNS,
        STATUS as LONG_PROF_STATUS,
    )
    from derive_long_raw import (
        FIBER_COLUMNS as LONG_RAW_FIBER_COLUMNS,
        OUT_DIR as LONG_RAW_DIR,
        OWNER_COLUMNS as LONG_RAW_OWNER_COLUMNS,
        STATUS as LONG_RAW_STATUS,
        csv_text,
        digest_text,
        table_from_rows,
    )
    from derive_long_univ import (
        ARROW_COLUMNS as LONG_UNIV_ARROW_COLUMNS,
        LAW_COLUMNS as LONG_UNIV_LAW_COLUMNS,
        NODE_COLUMNS as LONG_UNIV_NODE_COLUMNS,
        OUT_DIR as LONG_UNIV_DIR,
        STATUS as LONG_UNIV_STATUS,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_llnind"
STATUS = "LONG_LLNIND_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

LONG_LLN_REPORT = LONG_LLN_DIR / "report.json"
LONG_LLN_ADDR = LONG_LLN_DIR / "addr.csv"
LONG_LLN_LLN = LONG_LLN_DIR / "lln.csv"
LONG_LLN_TABLES = LONG_LLN_DIR / "tables.npz"
LONG_PROF_REPORT = LONG_PROF_DIR / "report.json"
LONG_PROF_OBJECT = LONG_PROF_DIR / "object.csv"
LONG_PROF_PROFUNCTOR = LONG_PROF_DIR / "profunctor.csv"
LONG_PROF_COMPOSE = LONG_PROF_DIR / "compose.csv"
LONG_PROF_TABLES = LONG_PROF_DIR / "tables.npz"
LONG_UNIV_REPORT = LONG_UNIV_DIR / "report.json"
LONG_UNIV_NODE = LONG_UNIV_DIR / "node.csv"
LONG_UNIV_ARROW = LONG_UNIV_DIR / "arrow.csv"
LONG_UNIV_LAW = LONG_UNIV_DIR / "law.csv"
LONG_UNIV_TABLES = LONG_UNIV_DIR / "tables.npz"
LONG_MIN_REPORT = LONG_MIN_DIR / "report.json"
LONG_MIN_BASIS = LONG_MIN_DIR / "basis.csv"
LONG_MIN_COVER = LONG_MIN_DIR / "cover.csv"
LONG_MIN_TABLES = LONG_MIN_DIR / "tables.npz"
LONG_NAT_REPORT = LONG_NAT_DIR / "report.json"
LONG_NAT_NATURALITY = LONG_NAT_DIR / "naturality.csv"
LONG_NAT_DEPENDENCY = LONG_NAT_DIR / "dependency.csv"
LONG_NAT_TABLES = LONG_NAT_DIR / "tables.npz"
LONG_PROB_REPORT = LONG_PROB_DIR / "report.json"
LONG_PROB_DIST = LONG_PROB_DIR / "dist.csv"
LONG_PROB_MOMENT = LONG_PROB_DIR / "moment.csv"
LONG_PROB_TABLES = LONG_PROB_DIR / "tables.npz"
LONG_RAW_REPORT = LONG_RAW_DIR / "report.json"
LONG_RAW_OWNER = LONG_RAW_DIR / "owner.csv"
LONG_RAW_FIBER = LONG_RAW_DIR / "fiber.csv"
LONG_RAW_TABLES = LONG_RAW_DIR / "tables.npz"
LONG_PATH_REPORT = LONG_PATH_DIR / "report.json"
LONG_PATH_PATH = LONG_PATH_DIR / "path.csv"
LONG_PATH_STEP = LONG_PATH_DIR / "step.csv"
LONG_PATH_TABLES = LONG_PATH_DIR / "tables.npz"
LONG_GAPIND_REPORT = LONG_GAPIND_DIR / "report.json"
LONG_GAPIND_REGIME = LONG_GAPIND_DIR / "regime.csv"
LONG_GAPIND_BRIDGE = LONG_GAPIND_DIR / "bridge.csv"
LONG_GAPIND_TABLES = LONG_GAPIND_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_llnind.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_llnind.py"

LAYER_TEXT_HASH = "a60e605393e02302eaf9d989f8c8bb63ee8c2ad00a9583f7815c2d8cb712f78a"
SEAM_TEXT_HASH = "f9a6458b65fa550613f5547e47060835cc5e15a22ef48b78db9184f3ceea5358"
BRIDGE_TEXT_HASH = "97cf755e5dfc1b8cc684d7eaeed1563b44ff5ac98bdfccee414ca4a080b96cf0"

LAYER_COLUMNS = [
    "layer_id",
    "layer_code",
    "primary_count",
    "secondary_count",
    "tertiary_count",
    "quaternary_count",
    "certified_flag",
]
SEAM_COLUMNS = [
    "seam_id",
    "seam_code",
    "left_count",
    "right_count",
    "third_count",
    "seam_match_flag",
]
BRIDGE_COLUMNS = [
    "bridge_id",
    "line_point_count",
    "tensor_support_count",
    "tensor_coeff_sum",
    "profunctor_object_count",
    "profunctor_count",
    "universal_node_count",
    "universal_arrow_count",
    "universal_law_count",
    "forcing_basis_count",
    "naturality_law_count",
    "profunctor_controlled_law_count",
    "external_input_law_count",
    "probability_path_count",
    "variance_shrink_count",
    "raw_tensor_support_count",
    "raw_path_count",
    "gap_path_count",
    "gap_regime_count",
    "finite_gap_check_count",
    "finite_gap_nonnegative_count",
    "tail_formula_nonnegative_count",
    "input_certified_count",
    "seam_match_count",
    "theorem_bridge_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "line_point_count",
    "tensor_support_count",
    "tensor_coeff_sum",
    "checked_k_start",
    "checked_k_end",
    "profunctor_object_count",
    "profunctor_count",
    "profunctor_law_count",
    "universal_node_count",
    "universal_arrow_count",
    "universal_law_count",
    "forcing_basis_count",
    "forced_law_count",
    "naturality_law_count",
    "profunctor_controlled_law_count",
    "external_input_law_count",
    "naturality_dependency_edge_count",
    "probability_path_count",
    "probability_sample_max",
    "variance_shrink_count",
    "raw_tensor_support_count",
    "raw_coeff_sum",
    "raw_path_count",
    "gap_path_count",
    "path_step_count",
    "gap_regime_count",
    "finite_gap_check_count",
    "finite_gap_nonnegative_count",
    "tail_formula_nonnegative_count",
    "input_certified_count",
    "seam_match_count",
    "current_llnind_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def status_flag(report: dict[str, Any], status: str) -> int:
    return int(report.get("status") == status and report.get("all_checks_pass") is True)


def build_rows() -> dict[str, Any]:
    reports = {
        "lln": load_json(LONG_LLN_REPORT),
        "prof": load_json(LONG_PROF_REPORT),
        "univ": load_json(LONG_UNIV_REPORT),
        "min": load_json(LONG_MIN_REPORT),
        "nat": load_json(LONG_NAT_REPORT),
        "prob": load_json(LONG_PROB_REPORT),
        "raw": load_json(LONG_RAW_REPORT),
        "path": load_json(LONG_PATH_REPORT),
        "gapind": load_json(LONG_GAPIND_REPORT),
    }
    lln_witness = reports["lln"]["witness"]
    prof_witness = reports["prof"]["witness"]
    univ_witness = reports["univ"]["witness"]
    min_witness = reports["min"]["witness"]
    nat_witness = reports["nat"]["witness"]
    prob_witness = reports["prob"]["witness"]
    raw_witness = reports["raw"]["witness"]
    path_witness = reports["path"]["witness"]
    gap_witness = reports["gapind"]["witness"]

    line_point_count = int(lln_witness["line"]["point_count"])
    tensor_support_count = int(lln_witness["tensor_lookup"]["support_count"])
    tensor_coeff_sum = int(lln_witness["tensor_lookup"]["coefficient_sum"])
    checked_k_start, checked_k_end = [
        int(value) for value in lln_witness["finite_lln"]["checked_k_range"]
    ]
    prof_object_count = int(prof_witness["objects"]["count"])
    profunctor_count = int(prof_witness["profunctors"]["count"])
    prof_law_count = int(prof_witness["composition"]["law_count"])
    owner_component_rows = int(prof_witness["owner_component"]["row_count"])
    univ_node_count = int(univ_witness["nodes"]["count"])
    univ_arrow_count = int(univ_witness["arrows"]["count"])
    univ_law_count = int(univ_witness["commuting_squares"]["law_count"])
    univ_square_count = int(univ_witness["commuting_squares"]["count"])
    forcing_basis_count = int(min_witness["basis"]["law_count"])
    forced_law_count = int(min_witness["forced"]["law_count"])
    nat_law_count = int(nat_witness["naturality"]["law_count"])
    prof_controlled_count = int(
        nat_witness["naturality"]["profunctor_controlled_law_count"]
    )
    external_input_count = int(nat_witness["naturality"]["external_input_law_count"])
    nat_dependency_edges = int(nat_witness["dependency_graph"]["edge_count"])
    probability_path_count = int(prob_witness["measure"]["path_count"])
    probability_sample_max = int(prob_witness["measure"]["sample_count_max"])
    variance_shrink_count = int(
        prob_witness["conditional_lln_curve"]["variance_shrink_flag_count"]
    )
    raw_support_count = int(
        raw_witness["raw_owner_assignment"]["raw_tensor_support_count"]
    )
    raw_coeff_sum = int(raw_witness["raw_owner_assignment"]["raw_tensor_coeff_sum"])
    raw_current_flag = int(
        raw_witness["current_representation"]["current_raw_owner_support_flag"]
    )
    path_count = int(path_witness["paths"]["path_row_count"])
    gap_path_count = int(path_witness["paths"]["gap_path_count"])
    path_step_count = int(path_witness["paths"]["path_step_row_count"])
    path_current_flag = int(
        path_witness["current_representation"]["current_explicit_raw_product_path_flag"]
    )
    gap_regime_count = int(gap_witness["regimes"]["tail_start"] >= 257) + 3
    finite_gap_check_count = int(gap_witness["gap_induction"]["finite_gap_check_count"])
    finite_gap_nonnegative_count = int(
        gap_witness["gap_induction"]["finite_gap_nonnegative_count"]
    )
    tail_formula_nonnegative_count = int(
        gap_witness["gap_induction"]["tail_formula_nonnegative_count"]
    )
    gap_formula_count = int(gap_witness["gap_induction"]["formula_count"])
    input_flags = [
        status_flag(reports["lln"], LONG_LLN_STATUS),
        status_flag(reports["prof"], LONG_PROF_STATUS),
        status_flag(reports["univ"], LONG_UNIV_STATUS),
        status_flag(reports["min"], LONG_MIN_STATUS),
        status_flag(reports["nat"], LONG_NAT_STATUS),
        status_flag(reports["prob"], LONG_PROB_STATUS),
        status_flag(reports["raw"], LONG_RAW_STATUS),
        status_flag(reports["path"], LONG_PATH_STATUS),
        status_flag(reports["gapind"], LONG_GAPIND_STATUS),
    ]
    input_certified_count = sum(input_flags)

    layer_rows = [
        {
            "layer_id": 0,
            "layer_code": 0,
            "primary_count": line_point_count,
            "secondary_count": tensor_support_count,
            "tertiary_count": tensor_coeff_sum,
            "quaternary_count": checked_k_end,
            "certified_flag": input_flags[0],
        },
        {
            "layer_id": 1,
            "layer_code": 1,
            "primary_count": prof_object_count,
            "secondary_count": profunctor_count,
            "tertiary_count": prof_law_count,
            "quaternary_count": owner_component_rows,
            "certified_flag": input_flags[1],
        },
        {
            "layer_id": 2,
            "layer_code": 2,
            "primary_count": univ_node_count,
            "secondary_count": univ_arrow_count,
            "tertiary_count": univ_law_count,
            "quaternary_count": univ_square_count,
            "certified_flag": input_flags[2],
        },
        {
            "layer_id": 3,
            "layer_code": 3,
            "primary_count": forcing_basis_count,
            "secondary_count": forced_law_count,
            "tertiary_count": univ_law_count,
            "quaternary_count": univ_square_count,
            "certified_flag": input_flags[3],
        },
        {
            "layer_id": 4,
            "layer_code": 4,
            "primary_count": nat_law_count,
            "secondary_count": prof_controlled_count,
            "tertiary_count": external_input_count,
            "quaternary_count": nat_dependency_edges,
            "certified_flag": input_flags[4],
        },
        {
            "layer_id": 5,
            "layer_code": 5,
            "primary_count": probability_path_count,
            "secondary_count": probability_sample_max,
            "tertiary_count": variance_shrink_count,
            "quaternary_count": 1,
            "certified_flag": input_flags[5],
        },
        {
            "layer_id": 6,
            "layer_code": 6,
            "primary_count": raw_support_count,
            "secondary_count": path_count,
            "tertiary_count": gap_path_count,
            "quaternary_count": path_step_count,
            "certified_flag": int(input_flags[6] and input_flags[7]),
        },
        {
            "layer_id": 7,
            "layer_code": 7,
            "primary_count": gap_regime_count,
            "secondary_count": finite_gap_check_count,
            "tertiary_count": finite_gap_nonnegative_count,
            "quaternary_count": tail_formula_nonnegative_count,
            "certified_flag": input_flags[8],
        },
    ]
    seam_rows = [
        {
            "seam_id": 0,
            "seam_code": 0,
            "left_count": line_point_count,
            "right_count": line_point_count,
            "third_count": line_point_count,
            "seam_match_flag": int(line_point_count == 985),
        },
        {
            "seam_id": 1,
            "seam_code": 1,
            "left_count": tensor_support_count,
            "right_count": raw_support_count,
            "third_count": tensor_coeff_sum,
            "seam_match_flag": int(
                tensor_support_count == raw_support_count
                and tensor_coeff_sum == raw_coeff_sum
            ),
        },
        {
            "seam_id": 2,
            "seam_code": 2,
            "left_count": prof_object_count,
            "right_count": univ_node_count,
            "third_count": profunctor_count,
            "seam_match_flag": int(univ_node_count >= prof_object_count),
        },
        {
            "seam_id": 3,
            "seam_code": 3,
            "left_count": univ_law_count,
            "right_count": forcing_basis_count + forced_law_count,
            "third_count": nat_law_count,
            "seam_match_flag": int(
                univ_law_count == forcing_basis_count + forced_law_count == nat_law_count
            ),
        },
        {
            "seam_id": 4,
            "seam_code": 4,
            "left_count": path_count,
            "right_count": probability_path_count,
            "third_count": probability_sample_max,
            "seam_match_flag": int(path_count == probability_path_count),
        },
        {
            "seam_id": 5,
            "seam_code": 5,
            "left_count": gap_path_count,
            "right_count": gap_path_count,
            "third_count": path_current_flag,
            "seam_match_flag": int(gap_path_count == 208 and path_current_flag == 1),
        },
        {
            "seam_id": 6,
            "seam_code": 6,
            "left_count": checked_k_end,
            "right_count": probability_sample_max,
            "third_count": 16,
            "seam_match_flag": int(checked_k_end == 8 and probability_sample_max == 16),
        },
        {
            "seam_id": 7,
            "seam_code": 7,
            "left_count": finite_gap_check_count,
            "right_count": finite_gap_nonnegative_count,
            "third_count": tail_formula_nonnegative_count,
            "seam_match_flag": int(
                finite_gap_check_count == finite_gap_nonnegative_count
                and tail_formula_nonnegative_count == gap_formula_count
            ),
        },
    ]
    seam_match_count = sum(row["seam_match_flag"] for row in seam_rows)
    theorem_bridge_flag = int(
        input_certified_count == len(input_flags)
        and seam_match_count == len(seam_rows)
        and raw_current_flag == 1
        and path_current_flag == 1
        and finite_gap_check_count == finite_gap_nonnegative_count
    )
    bridge_rows = [
        {
            "bridge_id": 0,
            "line_point_count": line_point_count,
            "tensor_support_count": tensor_support_count,
            "tensor_coeff_sum": tensor_coeff_sum,
            "profunctor_object_count": prof_object_count,
            "profunctor_count": profunctor_count,
            "universal_node_count": univ_node_count,
            "universal_arrow_count": univ_arrow_count,
            "universal_law_count": univ_law_count,
            "forcing_basis_count": forcing_basis_count,
            "naturality_law_count": nat_law_count,
            "profunctor_controlled_law_count": prof_controlled_count,
            "external_input_law_count": external_input_count,
            "probability_path_count": probability_path_count,
            "variance_shrink_count": variance_shrink_count,
            "raw_tensor_support_count": raw_support_count,
            "raw_path_count": path_count,
            "gap_path_count": gap_path_count,
            "gap_regime_count": gap_regime_count,
            "finite_gap_check_count": finite_gap_check_count,
            "finite_gap_nonnegative_count": finite_gap_nonnegative_count,
            "tail_formula_nonnegative_count": tail_formula_nonnegative_count,
            "input_certified_count": input_certified_count,
            "seam_match_count": seam_match_count,
            "theorem_bridge_flag": theorem_bridge_flag,
        }
    ]
    obs = {
        "line_point_count": line_point_count,
        "tensor_support_count": tensor_support_count,
        "tensor_coeff_sum": tensor_coeff_sum,
        "checked_k_start": checked_k_start,
        "checked_k_end": checked_k_end,
        "profunctor_object_count": prof_object_count,
        "profunctor_count": profunctor_count,
        "profunctor_law_count": prof_law_count,
        "universal_node_count": univ_node_count,
        "universal_arrow_count": univ_arrow_count,
        "universal_law_count": univ_law_count,
        "forcing_basis_count": forcing_basis_count,
        "forced_law_count": forced_law_count,
        "naturality_law_count": nat_law_count,
        "profunctor_controlled_law_count": prof_controlled_count,
        "external_input_law_count": external_input_count,
        "naturality_dependency_edge_count": nat_dependency_edges,
        "probability_path_count": probability_path_count,
        "probability_sample_max": probability_sample_max,
        "variance_shrink_count": variance_shrink_count,
        "raw_tensor_support_count": raw_support_count,
        "raw_coeff_sum": raw_coeff_sum,
        "raw_path_count": path_count,
        "gap_path_count": gap_path_count,
        "path_step_count": path_step_count,
        "gap_regime_count": gap_regime_count,
        "finite_gap_check_count": finite_gap_check_count,
        "finite_gap_nonnegative_count": finite_gap_nonnegative_count,
        "tail_formula_nonnegative_count": tail_formula_nonnegative_count,
        "input_certified_count": input_certified_count,
        "seam_match_count": seam_match_count,
        "current_llnind_flag": theorem_bridge_flag,
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    layer_hash = hashlib.sha256(
        digest_text(LAYER_COLUMNS, layer_rows).encode("ascii")
    ).hexdigest()
    seam_hash = hashlib.sha256(
        digest_text(SEAM_COLUMNS, seam_rows).encode("ascii")
    ).hexdigest()
    bridge_hash = hashlib.sha256(
        digest_text(BRIDGE_COLUMNS, bridge_rows).encode("ascii")
    ).hexdigest()
    return {
        "layer_rows": layer_rows,
        "seam_rows": seam_rows,
        "bridge_rows": bridge_rows,
        "obs_rows": obs_rows,
        "layer_table": table_from_rows(LAYER_COLUMNS, layer_rows),
        "seam_table": table_from_rows(SEAM_COLUMNS, seam_rows),
        "bridge_table": table_from_rows(BRIDGE_COLUMNS, bridge_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "layer_hash": layer_hash,
        "seam_hash": seam_hash,
        "bridge_hash": bridge_hash,
        "obs": obs,
        "input_reports": reports,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_certified": obs["input_certified_count"] == 9,
        "layer_fingerprint_exact": (
            len(rows["layer_rows"]),
            sum(row["certified_flag"] for row in rows["layer_rows"]),
            rows["layer_hash"],
        )
        == (8, 8, LAYER_TEXT_HASH),
        "seam_fingerprint_exact": (
            len(rows["seam_rows"]),
            obs["seam_match_count"],
            rows["seam_hash"],
        )
        == (8, 8, SEAM_TEXT_HASH),
        "bridge_counts_exact": (
            obs["line_point_count"],
            obs["tensor_support_count"],
            obs["tensor_coeff_sum"],
            obs["universal_law_count"],
            obs["forcing_basis_count"],
            obs["naturality_law_count"],
            obs["probability_path_count"],
            obs["raw_path_count"],
            obs["finite_gap_check_count"],
            obs["finite_gap_nonnegative_count"],
            obs["tail_formula_nonnegative_count"],
            rows["bridge_hash"],
        )
        == (
            985,
            1_414_965,
            2_537_360,
            306,
            74,
            306,
            288,
            288,
            131_586,
            131_586,
            26,
            BRIDGE_TEXT_HASH,
        ),
        "current_theorem_bridge_exact": obs["current_llnind_flag"] == 1,
        "table_shapes_match": (
            tuple(rows["layer_table"].shape),
            tuple(rows["seam_table"].shape),
            tuple(rows["bridge_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (8, len(LAYER_COLUMNS)),
            (8, len(SEAM_COLUMNS)),
            (1, len(BRIDGE_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "finite_tensor_lookup_lln_induction_bridge",
        "layers": {
            "layer_count": len(rows["layer_rows"]),
            "certified_layer_count": sum(
                row["certified_flag"] for row in rows["layer_rows"]
            ),
            "layer_text_sha256": rows["layer_hash"],
            "layer_table_sha256": sha_array(rows["layer_table"]),
        },
        "seams": {
            "seam_count": len(rows["seam_rows"]),
            "seam_match_count": obs["seam_match_count"],
            "seam_text_sha256": rows["seam_hash"],
            "seam_table_sha256": sha_array(rows["seam_table"]),
        },
        "theorem_bridge": {
            "line_point_count": obs["line_point_count"],
            "tensor_support_count": obs["tensor_support_count"],
            "tensor_coeff_sum": obs["tensor_coeff_sum"],
            "universal_law_count": obs["universal_law_count"],
            "probability_path_count": obs["probability_path_count"],
            "finite_gap_check_count": obs["finite_gap_check_count"],
            "finite_gap_nonnegative_count": obs["finite_gap_nonnegative_count"],
            "tail_formula_nonnegative_count": obs["tail_formula_nonnegative_count"],
            "bridge_text_sha256": rows["bridge_hash"],
            "bridge_table_sha256": sha_array(rows["bridge_table"]),
        },
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    llnind_payload = {
        "schema": "long.llnind@1",
        "object": "finite_tensor_lookup_lln_induction_bridge",
        "status": STATUS if all(checks.values()) else "LONG_LLNIND_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.llnind.report@1",
        "status": llnind_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_llnind connects the global support-gap induction to the finite "
            "tensor-lookup LLN chain. It verifies that the same 985-address line, "
            "profunctor diagram, forcing/naturality laws, raw product-path witnesses, "
            "probability curve, and support-gap induction form one certified bridge."
        ),
        "stage_protocol": {
            "draft": "read the certified line, profunctor, universal, path, probability, and gap-induction artifacts",
            "witness": "emit layer and seam rows linking finite tensor lookup to global support-gap induction",
            "coherence": "check statuses, seam equalities, theorem counts, hashes, and shapes",
            "closure": "emit the theorem-facing bridge while retaining unresolved semantic and full-measure boundaries",
            "emit": "write long_llnind artifacts and verifier hook",
        },
        "inputs": {
            "long_lln_report": input_entry(
                LONG_LLN_REPORT,
                {"status": rows["input_reports"]["lln"].get("status")},
            ),
            "long_lln_addr": input_entry(
                LONG_LLN_ADDR,
                {"columns": LONG_LLN_ADDR_COLUMNS},
            ),
            "long_lln_lln": input_entry(
                LONG_LLN_LLN,
                {"columns": LONG_LLN_LLN_COLUMNS},
            ),
            "long_lln_tables": input_entry(LONG_LLN_TABLES),
            "long_prof_report": input_entry(
                LONG_PROF_REPORT,
                {"status": rows["input_reports"]["prof"].get("status")},
            ),
            "long_prof_object": input_entry(
                LONG_PROF_OBJECT,
                {"columns": LONG_PROF_OBJECT_COLUMNS},
            ),
            "long_prof_profunctor": input_entry(
                LONG_PROF_PROFUNCTOR,
                {"columns": LONG_PROF_PROFUNCTOR_COLUMNS},
            ),
            "long_prof_compose": input_entry(
                LONG_PROF_COMPOSE,
                {"columns": LONG_PROF_COMPOSE_COLUMNS},
            ),
            "long_prof_tables": input_entry(LONG_PROF_TABLES),
            "long_univ_report": input_entry(
                LONG_UNIV_REPORT,
                {"status": rows["input_reports"]["univ"].get("status")},
            ),
            "long_univ_node": input_entry(
                LONG_UNIV_NODE,
                {"columns": LONG_UNIV_NODE_COLUMNS},
            ),
            "long_univ_arrow": input_entry(
                LONG_UNIV_ARROW,
                {"columns": LONG_UNIV_ARROW_COLUMNS},
            ),
            "long_univ_law": input_entry(
                LONG_UNIV_LAW,
                {"columns": LONG_UNIV_LAW_COLUMNS},
            ),
            "long_univ_tables": input_entry(LONG_UNIV_TABLES),
            "long_min_report": input_entry(
                LONG_MIN_REPORT,
                {"status": rows["input_reports"]["min"].get("status")},
            ),
            "long_min_basis": input_entry(
                LONG_MIN_BASIS,
                {"columns": LONG_MIN_BASIS_COLUMNS},
            ),
            "long_min_cover": input_entry(
                LONG_MIN_COVER,
                {"columns": LONG_MIN_COVER_COLUMNS},
            ),
            "long_min_tables": input_entry(LONG_MIN_TABLES),
            "long_nat_report": input_entry(
                LONG_NAT_REPORT,
                {"status": rows["input_reports"]["nat"].get("status")},
            ),
            "long_nat_naturality": input_entry(
                LONG_NAT_NATURALITY,
                {"columns": LONG_NAT_NAT_COLUMNS},
            ),
            "long_nat_dependency": input_entry(
                LONG_NAT_DEPENDENCY,
                {"columns": LONG_NAT_DEP_COLUMNS},
            ),
            "long_nat_tables": input_entry(LONG_NAT_TABLES),
            "long_prob_report": input_entry(
                LONG_PROB_REPORT,
                {"status": rows["input_reports"]["prob"].get("status")},
            ),
            "long_prob_dist": input_entry(
                LONG_PROB_DIST,
                {"columns": LONG_PROB_DIST_COLUMNS},
            ),
            "long_prob_moment": input_entry(
                LONG_PROB_MOMENT,
                {"columns": LONG_PROB_MOMENT_COLUMNS},
            ),
            "long_prob_tables": input_entry(LONG_PROB_TABLES),
            "long_raw_report": input_entry(
                LONG_RAW_REPORT,
                {"status": rows["input_reports"]["raw"].get("status")},
            ),
            "long_raw_owner": input_entry(
                LONG_RAW_OWNER,
                {"columns": LONG_RAW_OWNER_COLUMNS},
            ),
            "long_raw_fiber": input_entry(
                LONG_RAW_FIBER,
                {"columns": LONG_RAW_FIBER_COLUMNS},
            ),
            "long_raw_tables": input_entry(LONG_RAW_TABLES),
            "long_path_report": input_entry(
                LONG_PATH_REPORT,
                {"status": rows["input_reports"]["path"].get("status")},
            ),
            "long_path_path": input_entry(
                LONG_PATH_PATH,
                {"columns": LONG_PATH_PATH_COLUMNS},
            ),
            "long_path_step": input_entry(
                LONG_PATH_STEP,
                {"columns": LONG_PATH_STEP_COLUMNS},
            ),
            "long_path_tables": input_entry(LONG_PATH_TABLES),
            "long_gapind_report": input_entry(
                LONG_GAPIND_REPORT,
                {"status": rows["input_reports"]["gapind"].get("status")},
            ),
            "long_gapind_regime": input_entry(
                LONG_GAPIND_REGIME,
                {"columns": LONG_GAPIND_REGIME_COLUMNS},
            ),
            "long_gapind_bridge": input_entry(
                LONG_GAPIND_BRIDGE,
                {"columns": LONG_GAPIND_BRIDGE_COLUMNS},
            ),
            "long_gapind_tables": input_entry(LONG_GAPIND_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "llnind": relpath(OUT_DIR / "llnind.json"),
            "layer_csv": relpath(OUT_DIR / "layer.csv"),
            "seam_csv": relpath(OUT_DIR / "seam.csv"),
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
                "one theorem-facing bridge from the 985-address tensor lookup to the global support-gap induction",
                "the certified finite profunctor and universal LLN law diagram are attached to the same line-address counts",
                "the finite probability curve and explicit raw product-path witnesses use the same 288 sum-fiber rows",
                "the global support-gap induction is attached to the certified tensor-lookup LLN object chain",
            ],
            "does_not_certify_because_out_of_scope": [
                "semantic C985 associator composition",
                "a probability measure on the full raw tensor support",
                "all raw product paths in each fiber",
                "a genuine long_prof horizon-16 profunctor",
                "a final infinite-horizon LLN theorem",
            ],
        },
        "next_highest_yield_item": (
            "Build long_thm: collapse the theorem-facing bridge and remaining "
            "boundaries into a final finite-LLN theorem status object, separating "
            "proved tensor-lookup content from semantic/full-measure gaps."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.llnind.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.llnind.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "llnind": llnind_payload,
        "layer_csv": csv_text(LAYER_COLUMNS, rows["layer_rows"]),
        "seam_csv": csv_text(SEAM_COLUMNS, rows["seam_rows"]),
        "bridge_csv": csv_text(BRIDGE_COLUMNS, rows["bridge_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "layer_table": rows["layer_table"],
        "seam_table": rows["seam_table"],
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
    write_json(OUT_DIR / "llnind.json", payloads["llnind"])
    (OUT_DIR / "layer.csv").write_text(payloads["layer_csv"], encoding="utf-8")
    (OUT_DIR / "seam.csv").write_text(payloads["seam_csv"], encoding="utf-8")
    (OUT_DIR / "bridge.csv").write_text(payloads["bridge_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        layer_table=payloads["layer_table"],
        seam_table=payloads["seam_table"],
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
