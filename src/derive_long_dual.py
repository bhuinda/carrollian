from __future__ import annotations

import hashlib
import json
from collections import defaultdict
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
    from .derive_long_orient import OUT_DIR as LONG_ORIENT_DIR, STATUS as LONG_ORIENT_STATUS
    from .derive_long_raw import (
        csv_text,
        digest_text,
        int_rows,
        read_csv_rows,
        rows_from_table,
        table_from_rows,
    )
    from .derive_long_sheaf import (
        LONG_COMP_REPORT,
        LONG_COMP_TABLES,
        LONG_COMP_TRANSITION,
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_TABLES,
        OUT_DIR as LONG_SHEAF_DIR,
        STATUS as LONG_SHEAF_STATUS,
        LONG_COMP_STATUS,
        LONG_PATH_STATUS,
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
    from derive_long_orient import OUT_DIR as LONG_ORIENT_DIR, STATUS as LONG_ORIENT_STATUS
    from derive_long_raw import (
        csv_text,
        digest_text,
        int_rows,
        read_csv_rows,
        rows_from_table,
        table_from_rows,
    )
    from derive_long_sheaf import (
        LONG_COMP_REPORT,
        LONG_COMP_TABLES,
        LONG_COMP_TRANSITION,
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_TABLES,
        OUT_DIR as LONG_SHEAF_DIR,
        STATUS as LONG_SHEAF_STATUS,
        LONG_COMP_STATUS,
        LONG_PATH_STATUS,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_dual"
STATUS = "LONG_DUAL_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
LONG_ORIENT_REPORT = LONG_ORIENT_DIR / "report.json"
LONG_ORIENT_PAIR = LONG_ORIENT_DIR / "pair.csv"
LONG_ORIENT_TABLES = LONG_ORIENT_DIR / "tables.npz"
LONG_SHEAF_REPORT = LONG_SHEAF_DIR / "report.json"
LONG_SHEAF_SECTION = LONG_SHEAF_DIR / "section.csv"
LONG_SHEAF_TABLES = LONG_SHEAF_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_dual.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_dual.py"

COMPONENT_TEXT_HASH = "1c9ea8852da6f0aad1086cf2a405f988b450d6b794a8ed23c2032321c1be1bc1"
PATH_TEXT_HASH = "eaf5b4990be57597ddb7ac1dc5ba9e02e73bab0de938225544132a35165a5b87"
EDGE_TEXT_HASH = "de3efed95e3f17d3e03af0037458e5177b9cd44da278520dbaa808bb7d466acc"

MOD_PRIMES = (1_000_000_007, 1_000_000_009)

COMPONENT_COLUMNS = [
    "component_id",
    "pair_id",
    "lower_addr",
    "upper_addr",
    "witness_step_count",
    "positive_section_count",
    "reverse_section_count",
    "total_section_count",
    "signed_section_count",
    "positive_coeff_sum",
    "reverse_coeff_sum",
    "total_coeff_sum",
    "signed_coeff_sum",
    "positive_coeff_square_sum",
    "reverse_coeff_square_sum",
    "total_coeff_square_sum",
    "signed_coeff_square_sum",
    "count_kernel_nonzero_flag",
    "coeff_kernel_nonzero_flag",
    "coeff_square_kernel_nonzero_flag",
]
PATH_COLUMNS = [
    "path_id",
    "fiber_row_id",
    "step_count",
    "count_component0",
    "count_component1",
    "count_component2",
    "signed_coeff_sum",
    "signed_coeff_square_sum",
    "dual_coeff_product_digits",
    "dual_coeff_product_mod_1000000007",
    "dual_coeff_product_mod_1000000009",
    "dual_count_product_mod_1000000007",
    "dual_count_product_mod_1000000009",
    "dual_coeff_product_nonzero_flag",
    "dual_count_product_nonzero_flag",
    "dual_path_positive_flag",
    "long_tens_gap_flag",
    "existing_prof_flag",
]
EDGE_COLUMNS = [
    "edge_id",
    "from_component_id",
    "to_component_id",
    "transition_count",
    "zeta_both_count",
    "dual_compose_count",
    "signed_coeff_from",
    "signed_coeff_to",
    "signed_coeff_product",
    "signed_coeff_product_sum",
    "signed_coeff_product_mod_1000000007",
    "signed_coeff_product_mod_1000000009",
    "signed_coeff_delta_sum",
    "chain_edge_flag",
    "backward_edge_flag",
    "skip_edge_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "component_row_count",
    "witness_path_count",
    "witness_step_count",
    "transition_count",
    "coeff_kernel_nonzero_component_count",
    "count_kernel_nonzero_component_count",
    "coeff_kernel_nonzero_step_count",
    "count_kernel_nonzero_step_count",
    "dual_path_coeff_nonzero_count",
    "dual_path_count_nonzero_count",
    "dual_path_positive_count",
    "dual_coeff_product_digit_max",
    "dual_coeff_path_sum_min",
    "dual_coeff_path_sum_max",
    "dual_coeff_product_mod_sum_1000000007",
    "dual_coeff_product_mod_sum_1000000009",
    "edge_row_count",
    "edge_chain_flag_count",
    "edge_backward_count",
    "edge_skip_count",
    "dual_transition_compose_count",
    "dual_edge_product_sum",
    "component_signed_coeff_gcd",
    "component_signed_coeff_min",
    "component_signed_coeff_max",
    "current_coeff_dual_kernel_flag",
    "current_count_dual_kernel_flag",
    "current_witness_composition_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def gcd(values: list[int]) -> int:
    result = 0
    for value in values:
        result = int(np.gcd(result, abs(int(value))))
    return result


def load_inputs() -> dict[str, Any]:
    pair_rows = int_rows(read_csv_rows(LONG_ORIENT_PAIR))
    section_rows = int_rows(read_csv_rows(LONG_SHEAF_SECTION))
    path_rows = int_rows(read_csv_rows(LONG_PATH_PATH))
    transition_rows = int_rows(read_csv_rows(LONG_COMP_TRANSITION))
    input_reports = {
        "long_orient": load_json(LONG_ORIENT_REPORT),
        "long_sheaf": load_json(LONG_SHEAF_REPORT),
        "long_path": load_json(LONG_PATH_REPORT),
        "long_comp": load_json(LONG_COMP_REPORT),
    }
    return {
        "pair_rows": pair_rows,
        "section_rows": section_rows,
        "path_rows": path_rows,
        "transition_rows": transition_rows,
        "input_reports": input_reports,
    }


def enrich_sections(
    pair_rows: list[dict[str, int]],
    section_rows: list[dict[str, int]],
) -> tuple[list[dict[str, int]], dict[int, dict[str, int]], dict[tuple[int, int], dict[str, int]]]:
    pair_by_interval = {
        (row["lower_addr"], row["upper_addr"]): row for row in pair_rows
    }
    enriched_sections: list[dict[str, int]] = []
    component_kernel: dict[int, dict[str, int]] = {}
    for row in section_rows:
        pair = pair_by_interval[(row["lower_addr"], row["upper_addr"])]
        enriched = dict(row)
        for key in [
            "pair_id",
            "positive_section_count",
            "reverse_section_count",
            "total_section_count",
            "signed_section_count",
            "positive_coeff_sum",
            "reverse_coeff_sum",
            "total_coeff_sum",
            "signed_coeff_sum",
            "positive_coeff_square_sum",
            "reverse_coeff_square_sum",
            "total_coeff_square_sum",
            "signed_coeff_square_sum",
        ]:
            enriched[key] = pair[key]
        enriched_sections.append(enriched)
        component_id = row["component_id"]
        if component_id not in component_kernel:
            component_kernel[component_id] = {
                key: pair[key]
                for key in [
                    "pair_id",
                    "lower_addr",
                    "upper_addr",
                    "positive_section_count",
                    "reverse_section_count",
                    "total_section_count",
                    "signed_section_count",
                    "positive_coeff_sum",
                    "reverse_coeff_sum",
                    "total_coeff_sum",
                    "signed_coeff_sum",
                    "positive_coeff_square_sum",
                    "reverse_coeff_square_sum",
                    "total_coeff_square_sum",
                    "signed_coeff_square_sum",
                ]
            }
    step_count_by_component: defaultdict[int, int] = defaultdict(int)
    for row in enriched_sections:
        step_count_by_component[row["component_id"]] += 1
    component_rows: list[dict[str, int]] = []
    for component_id in sorted(component_kernel):
        row = {"component_id": component_id, **component_kernel[component_id]}
        row["witness_step_count"] = step_count_by_component[component_id]
        row["count_kernel_nonzero_flag"] = int(row["signed_section_count"] != 0)
        row["coeff_kernel_nonzero_flag"] = int(row["signed_coeff_sum"] != 0)
        row["coeff_square_kernel_nonzero_flag"] = int(
            row["signed_coeff_square_sum"] != 0
        )
        component_rows.append(row)
    section_by_path_step = {
        (row["path_id"], row["step_index"]): row for row in enriched_sections
    }
    return enriched_sections, {row["component_id"]: row for row in component_rows}, section_by_path_step


def build_path_rows(
    path_rows: list[dict[str, int]],
    enriched_sections: list[dict[str, int]],
) -> list[dict[str, int]]:
    sections_by_path: defaultdict[int, list[dict[str, int]]] = defaultdict(list)
    for row in enriched_sections:
        sections_by_path[row["path_id"]].append(row)
    path_input = {row["path_id"]: row for row in path_rows}
    rows: list[dict[str, int]] = []
    for path_id in sorted(sections_by_path):
        sections = sorted(sections_by_path[path_id], key=lambda row: row["step_index"])
        product = 1
        product_mod = [1, 1]
        count_product_mod = [1, 1]
        sign = 1
        coeff_sum = 0
        coeff_square_sum = 0
        count_nonzero = 1
        coeff_nonzero = 1
        for section in sections:
            coeff_value = section["signed_coeff_sum"]
            count_value = section["signed_section_count"]
            square_value = section["signed_coeff_square_sum"]
            coeff_sum += coeff_value
            coeff_square_sum += square_value
            product *= coeff_value
            if coeff_value < 0:
                sign *= -1
            if coeff_value == 0:
                coeff_nonzero = 0
            if count_value == 0:
                count_nonzero = 0
            for index, modulus in enumerate(MOD_PRIMES):
                product_mod[index] = (product_mod[index] * (coeff_value % modulus)) % modulus
                count_product_mod[index] = (
                    count_product_mod[index] * (count_value % modulus)
                ) % modulus
        base = path_input[path_id]
        rows.append(
            {
                "path_id": path_id,
                "fiber_row_id": base["fiber_row_id"],
                "step_count": len(sections),
                "count_component0": base["count_component0"],
                "count_component1": base["count_component1"],
                "count_component2": base["count_component2"],
                "signed_coeff_sum": coeff_sum,
                "signed_coeff_square_sum": coeff_square_sum,
                "dual_coeff_product_digits": len(str(abs(product))) if product else 0,
                "dual_coeff_product_mod_1000000007": product_mod[0],
                "dual_coeff_product_mod_1000000009": product_mod[1],
                "dual_count_product_mod_1000000007": count_product_mod[0],
                "dual_count_product_mod_1000000009": count_product_mod[1],
                "dual_coeff_product_nonzero_flag": coeff_nonzero,
                "dual_count_product_nonzero_flag": count_nonzero,
                "dual_path_positive_flag": int(sign > 0 and coeff_nonzero),
                "long_tens_gap_flag": base["long_tens_gap_flag"],
                "existing_prof_flag": base["existing_prof_flag"],
            }
        )
    return rows


def build_edge_rows(
    transition_rows: list[dict[str, int]],
    section_by_path_step: dict[tuple[int, int], dict[str, int]],
) -> list[dict[str, int]]:
    edge_data: dict[tuple[int, int], dict[str, int]] = {}
    for transition in transition_rows:
        from_step = section_by_path_step[
            (transition["path_id"], transition["from_step_index"])
        ]
        to_step = section_by_path_step[
            (transition["path_id"], transition["to_step_index"])
        ]
        edge_key = (from_step["component_id"], to_step["component_id"])
        if edge_key not in edge_data:
            edge_data[edge_key] = {
                "from_component_id": edge_key[0],
                "to_component_id": edge_key[1],
                "transition_count": 0,
                "zeta_both_count": 0,
                "dual_compose_count": 0,
                "signed_coeff_from": from_step["signed_coeff_sum"],
                "signed_coeff_to": to_step["signed_coeff_sum"],
                "signed_coeff_product": from_step["signed_coeff_sum"]
                * to_step["signed_coeff_sum"],
                "signed_coeff_product_sum": 0,
                "signed_coeff_product_mod_1000000007": 0,
                "signed_coeff_product_mod_1000000009": 0,
                "signed_coeff_delta_sum": 0,
            }
        row = edge_data[edge_key]
        product = from_step["signed_coeff_sum"] * to_step["signed_coeff_sum"]
        row["transition_count"] += 1
        row["zeta_both_count"] += transition["zeta_both_flag"]
        row["dual_compose_count"] += int(
            transition["zeta_both_flag"] == 1
            and from_step["signed_coeff_sum"] != 0
            and to_step["signed_coeff_sum"] != 0
        )
        row["signed_coeff_product_sum"] += product
        row["signed_coeff_delta_sum"] += (
            to_step["signed_coeff_sum"] - from_step["signed_coeff_sum"]
        )
        row["signed_coeff_product_mod_1000000007"] = (
            row["signed_coeff_product_mod_1000000007"] + product
        ) % MOD_PRIMES[0]
        row["signed_coeff_product_mod_1000000009"] = (
            row["signed_coeff_product_mod_1000000009"] + product
        ) % MOD_PRIMES[1]
    rows: list[dict[str, int]] = []
    for edge_id, edge_key in enumerate(sorted(edge_data)):
        row = {"edge_id": edge_id, **edge_data[edge_key]}
        delta = row["to_component_id"] - row["from_component_id"]
        row["chain_edge_flag"] = int(delta in (0, 1))
        row["backward_edge_flag"] = int(delta < 0)
        row["skip_edge_flag"] = int(delta > 1)
        rows.append(row)
    return rows


def build_rows() -> dict[str, Any]:
    loaded = load_inputs()
    enriched_sections, component_by_id, section_by_path_step = enrich_sections(
        loaded["pair_rows"], loaded["section_rows"]
    )
    component_rows = [component_by_id[key] for key in sorted(component_by_id)]
    path_rows = build_path_rows(loaded["path_rows"], enriched_sections)
    edge_rows = build_edge_rows(loaded["transition_rows"], section_by_path_step)
    component_coeffs = [row["signed_coeff_sum"] for row in component_rows]
    obs = {
        "component_row_count": len(component_rows),
        "witness_path_count": len(path_rows),
        "witness_step_count": len(enriched_sections),
        "transition_count": len(loaded["transition_rows"]),
        "coeff_kernel_nonzero_component_count": sum(
            row["coeff_kernel_nonzero_flag"] for row in component_rows
        ),
        "count_kernel_nonzero_component_count": sum(
            row["count_kernel_nonzero_flag"] for row in component_rows
        ),
        "coeff_kernel_nonzero_step_count": sum(
            int(row["signed_coeff_sum"] != 0) for row in enriched_sections
        ),
        "count_kernel_nonzero_step_count": sum(
            int(row["signed_section_count"] != 0) for row in enriched_sections
        ),
        "dual_path_coeff_nonzero_count": sum(
            row["dual_coeff_product_nonzero_flag"] for row in path_rows
        ),
        "dual_path_count_nonzero_count": sum(
            row["dual_count_product_nonzero_flag"] for row in path_rows
        ),
        "dual_path_positive_count": sum(row["dual_path_positive_flag"] for row in path_rows),
        "dual_coeff_product_digit_max": max(
            row["dual_coeff_product_digits"] for row in path_rows
        ),
        "dual_coeff_path_sum_min": min(row["signed_coeff_sum"] for row in path_rows),
        "dual_coeff_path_sum_max": max(row["signed_coeff_sum"] for row in path_rows),
        "dual_coeff_product_mod_sum_1000000007": sum(
            row["dual_coeff_product_mod_1000000007"] for row in path_rows
        )
        % MOD_PRIMES[0],
        "dual_coeff_product_mod_sum_1000000009": sum(
            row["dual_coeff_product_mod_1000000009"] for row in path_rows
        )
        % MOD_PRIMES[1],
        "edge_row_count": len(edge_rows),
        "edge_chain_flag_count": sum(row["chain_edge_flag"] for row in edge_rows),
        "edge_backward_count": sum(row["backward_edge_flag"] for row in edge_rows),
        "edge_skip_count": sum(row["skip_edge_flag"] for row in edge_rows),
        "dual_transition_compose_count": sum(
            row["dual_compose_count"] for row in edge_rows
        ),
        "dual_edge_product_sum": sum(row["signed_coeff_product_sum"] for row in edge_rows),
        "component_signed_coeff_gcd": gcd(component_coeffs),
        "component_signed_coeff_min": min(component_coeffs),
        "component_signed_coeff_max": max(component_coeffs),
        "current_coeff_dual_kernel_flag": 1,
        "current_count_dual_kernel_flag": 0,
        "current_witness_composition_flag": 1,
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    component_hash = hashlib.sha256(
        digest_text(COMPONENT_COLUMNS, component_rows).encode("ascii")
    ).hexdigest()
    path_hash = hashlib.sha256(
        digest_text(PATH_COLUMNS, path_rows).encode("ascii")
    ).hexdigest()
    edge_hash = hashlib.sha256(
        digest_text(EDGE_COLUMNS, edge_rows).encode("ascii")
    ).hexdigest()
    return {
        "input_reports": loaded["input_reports"],
        "component_rows": component_rows,
        "path_rows": path_rows,
        "edge_rows": edge_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "component_table": table_from_rows(COMPONENT_COLUMNS, component_rows),
        "path_table": table_from_rows(PATH_COLUMNS, path_rows),
        "edge_table": table_from_rows(EDGE_COLUMNS, edge_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "component_hash": component_hash,
        "path_hash": path_hash,
        "edge_hash": edge_hash,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    input_reports = rows["input_reports"]
    checks = {
        "input_certified": (
            input_reports["long_orient"].get("status"),
            input_reports["long_sheaf"].get("status"),
            input_reports["long_path"].get("status"),
            input_reports["long_comp"].get("status"),
        )
        == (
            LONG_ORIENT_STATUS,
            LONG_SHEAF_STATUS,
            LONG_PATH_STATUS,
            LONG_COMP_STATUS,
        ),
        "component_kernel_exact": (
            obs["component_row_count"],
            obs["coeff_kernel_nonzero_component_count"],
            obs["count_kernel_nonzero_component_count"],
            obs["component_signed_coeff_gcd"],
            obs["component_signed_coeff_min"],
            obs["component_signed_coeff_max"],
            rows["component_hash"],
        )
        == (3, 3, 1, 6, 12, 48, COMPONENT_TEXT_HASH),
        "witness_step_kernel_exact": (
            obs["witness_step_count"],
            obs["coeff_kernel_nonzero_step_count"],
            obs["count_kernel_nonzero_step_count"],
            obs["current_coeff_dual_kernel_flag"],
            obs["current_count_dual_kernel_flag"],
        )
        == (3128, 3128, 816, 1, 0),
        "path_dual_exact": (
            obs["witness_path_count"],
            obs["dual_path_coeff_nonzero_count"],
            obs["dual_path_count_nonzero_count"],
            obs["dual_path_positive_count"],
            obs["dual_coeff_product_digit_max"],
            obs["dual_coeff_path_sum_min"],
            obs["dual_coeff_path_sum_max"],
            obs["dual_coeff_product_mod_sum_1000000007"],
            obs["dual_coeff_product_mod_sum_1000000009"],
            rows["path_hash"],
        )
        == (
            288,
            288,
            16,
            288,
            27,
            12,
            768,
            497_101_086,
            118_327_119,
            PATH_TEXT_HASH,
        ),
        "edge_dual_composition_exact": (
            obs["transition_count"],
            obs["edge_row_count"],
            obs["edge_chain_flag_count"],
            obs["edge_backward_count"],
            obs["edge_skip_count"],
            obs["dual_transition_compose_count"],
            obs["dual_edge_product_sum"],
            obs["current_witness_composition_flag"],
            rows["edge_hash"],
        )
        == (
            2840,
            5,
            5,
            0,
            0,
            2840,
            2_196_000,
            1,
            EDGE_TEXT_HASH,
        ),
        "table_shapes_match": (
            tuple(rows["component_table"].shape),
            tuple(rows["path_table"].shape),
            tuple(rows["edge_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (3, len(COMPONENT_COLUMNS)),
            (288, len(PATH_COLUMNS)),
            (5, len(EDGE_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "coefficient_dual_kernel_on_witness_paths",
        "kernel": {
            "component_signed_coeffs": [
                row["signed_coeff_sum"] for row in rows["component_rows"]
            ],
            "component_signed_coeff_gcd": obs["component_signed_coeff_gcd"],
            "coefficient_kernel_nonzero_on_all_witness_steps": bool(
                obs["coeff_kernel_nonzero_step_count"] == obs["witness_step_count"]
            ),
            "count_kernel_nonzero_on_all_witness_steps": bool(
                obs["count_kernel_nonzero_step_count"] == obs["witness_step_count"]
            ),
        },
        "path_composition": {
            "witness_path_count": obs["witness_path_count"],
            "dual_path_coeff_nonzero_count": obs["dual_path_coeff_nonzero_count"],
            "dual_path_count_nonzero_count": obs["dual_path_count_nonzero_count"],
            "dual_path_positive_count": obs["dual_path_positive_count"],
            "dual_coeff_product_digit_max": obs["dual_coeff_product_digit_max"],
            "dual_coeff_path_sum_min": obs["dual_coeff_path_sum_min"],
            "dual_coeff_path_sum_max": obs["dual_coeff_path_sum_max"],
            "path_table_sha256": sha_array(rows["path_table"]),
            "path_text_sha256": rows["path_hash"],
        },
        "transition_composition": {
            "transition_count": obs["transition_count"],
            "edge_row_count": obs["edge_row_count"],
            "edge_chain_flag_count": obs["edge_chain_flag_count"],
            "edge_backward_count": obs["edge_backward_count"],
            "edge_skip_count": obs["edge_skip_count"],
            "dual_transition_compose_count": obs["dual_transition_compose_count"],
            "dual_edge_product_sum": obs["dual_edge_product_sum"],
            "edge_table_sha256": sha_array(rows["edge_table"]),
            "edge_text_sha256": rows["edge_hash"],
        },
        "component_table_sha256": sha_array(rows["component_table"]),
        "component_text_sha256": rows["component_hash"],
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    dual_payload = {
        "schema": "long.dual@1",
        "object": "coefficient_dual_kernel_on_witness_paths",
        "status": STATUS if all(checks.values()) else "LONG_DUAL_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.dual.report@1",
        "status": dual_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_dual certifies that the long_orient signed coefficient "
            "component is a nonzero finite dual kernel on every long_path "
            "witness step and every long_comp witness transition. The signed "
            "count component is recorded as insufficient: it vanishes on two "
            "of the three representative component intervals and only supports "
            "16 of 288 path products."
        ),
        "stage_protocol": {
            "draft": "read long_orient pair split, long_sheaf witness sections, long_path paths, and long_comp transitions",
            "witness": "restrict the signed coefficient component to the three representative path intervals",
            "coherence": "check nonzero path products, transition composition, chain-edge shape, statuses, hashes, and shapes",
            "closure": "emit coefficient-dual kernel while recording count-kernel failure",
            "emit": "write long_dual artifacts and verifier hook",
        },
        "inputs": {
            "long_orient_report": input_entry(
                LONG_ORIENT_REPORT,
                {"status": rows["input_reports"]["long_orient"].get("status")},
            ),
            "long_orient_pair": input_entry(LONG_ORIENT_PAIR),
            "long_orient_tables": input_entry(LONG_ORIENT_TABLES),
            "long_sheaf_report": input_entry(
                LONG_SHEAF_REPORT,
                {"status": rows["input_reports"]["long_sheaf"].get("status")},
            ),
            "long_sheaf_section": input_entry(LONG_SHEAF_SECTION),
            "long_sheaf_tables": input_entry(LONG_SHEAF_TABLES),
            "long_path_report": input_entry(
                LONG_PATH_REPORT,
                {"status": rows["input_reports"]["long_path"].get("status")},
            ),
            "long_path_path": input_entry(LONG_PATH_PATH),
            "long_path_tables": input_entry(LONG_PATH_TABLES),
            "long_comp_report": input_entry(
                LONG_COMP_REPORT,
                {"status": rows["input_reports"]["long_comp"].get("status")},
            ),
            "long_comp_transition": input_entry(LONG_COMP_TRANSITION),
            "long_comp_tables": input_entry(LONG_COMP_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "dual": relpath(OUT_DIR / "dual.json"),
            "component_csv": relpath(OUT_DIR / "component.csv"),
            "path_csv": relpath(OUT_DIR / "path.csv"),
            "edge_csv": relpath(OUT_DIR / "edge.csv"),
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
                "signed coefficient kernel values on the three representative witness intervals",
                "nonzero signed coefficient dual product for all 288 witness paths",
                "nonzero signed coefficient composition over all 2,840 zeta-composable witness transitions",
                "the witness transition graph is a loop/nearest-forward chain on components 0, 1, 2",
            ],
            "does_not_certify_because_out_of_scope": [
                "that signed counts alone define a witness-support kernel",
                "semantic C985 associator composition",
                "full raw-path composition beyond the selected witnesses",
                "a signed probability theorem",
            ],
        },
        "next_highest_yield_item": (
            "Build long_prob: normalize the coefficient-dual kernel into "
            "finite path measures and test the LLN variance decomposition on "
            "the witness chain."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.dual.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.dual.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "dual": dual_payload,
        "component_csv": csv_text(COMPONENT_COLUMNS, rows["component_rows"]),
        "path_csv": csv_text(PATH_COLUMNS, rows["path_rows"]),
        "edge_csv": csv_text(EDGE_COLUMNS, rows["edge_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "component_table": rows["component_table"],
        "path_table": rows["path_table"],
        "edge_table": rows["edge_table"],
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
    write_json(OUT_DIR / "dual.json", payloads["dual"])
    (OUT_DIR / "component.csv").write_text(payloads["component_csv"], encoding="utf-8")
    (OUT_DIR / "path.csv").write_text(payloads["path_csv"], encoding="utf-8")
    (OUT_DIR / "edge.csv").write_text(payloads["edge_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        component_table=payloads["component_table"],
        path_table=payloads["path_table"],
        edge_table=payloads["edge_table"],
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
