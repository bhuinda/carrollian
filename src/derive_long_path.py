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
    from .derive_long_lap import STATUS as LONG_LAP_STATUS
    from .derive_long_raw import (
        LONG_LAP_COMPONENT,
        LONG_LAP_NODE,
        LONG_LAP_REPORT,
        LONG_LAP_TABLES,
        LONG_LIFT_REPORT,
        LONG_LIFT_TABLES,
        LONG_LLN_REPORT,
        LONG_LLN_TABLES,
        LONG_REC_OWNER,
        LONG_REC_REPORT,
        LONG_REC_TABLES,
        LONG_TENS_FIBER,
        LONG_TENS_HORIZON,
        LONG_TENS_REPORT,
        LONG_TENS_TABLES,
        OUT_DIR as LONG_RAW_DIR,
        RAW_TENSOR,
        STATUS as LONG_RAW_STATUS,
        active_component_maps,
        csv_text,
        digest_text,
        int_rows,
        load_raw_triples,
        load_rec_tables,
        raw_owner_profiles,
        read_csv_rows,
        rows_from_table,
        table_from_rows,
    )
    from .derive_long_lift import STATUS as LONG_LIFT_STATUS
    from .derive_long_lln import STATUS as LONG_LLN_STATUS
    from .derive_long_rec import STATUS as LONG_REC_STATUS
    from .derive_long_tens import STATUS as LONG_TENS_STATUS
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_lap import STATUS as LONG_LAP_STATUS
    from derive_long_raw import (
        LONG_LAP_COMPONENT,
        LONG_LAP_NODE,
        LONG_LAP_REPORT,
        LONG_LAP_TABLES,
        LONG_LIFT_REPORT,
        LONG_LIFT_TABLES,
        LONG_LLN_REPORT,
        LONG_LLN_TABLES,
        LONG_REC_OWNER,
        LONG_REC_REPORT,
        LONG_REC_TABLES,
        LONG_TENS_FIBER,
        LONG_TENS_HORIZON,
        LONG_TENS_REPORT,
        LONG_TENS_TABLES,
        OUT_DIR as LONG_RAW_DIR,
        RAW_TENSOR,
        STATUS as LONG_RAW_STATUS,
        active_component_maps,
        csv_text,
        digest_text,
        int_rows,
        load_raw_triples,
        load_rec_tables,
        raw_owner_profiles,
        read_csv_rows,
        rows_from_table,
        table_from_rows,
    )
    from derive_long_lift import STATUS as LONG_LIFT_STATUS
    from derive_long_lln import STATUS as LONG_LLN_STATUS
    from derive_long_rec import STATUS as LONG_REC_STATUS
    from derive_long_tens import STATUS as LONG_TENS_STATUS
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_path"
STATUS = "LONG_PATH_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
LONG_RAW_REPORT = LONG_RAW_DIR / "report.json"
LONG_RAW_TABLES = LONG_RAW_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_path.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_path.py"

COMPONENT_TEXT_HASH = (
    "582a89541591128cdf0e957a7fb9c314da269c3078501d2426875a2a6cb943e3"
)
PATH_TEXT_HASH = (
    "d85f1344fe06e44c76f80ee7fa3d0754e12095f8ffdd5fe162c07815a6a220a4"
)
STEP_TEXT_HASH = (
    "4d91021a42de050572bf461176e5933076eb368aa2513e29f732c62282b1d6b5"
)

MOD_PRIMES = (1_000_000_007, 1_000_000_009)

COMPONENT_COLUMNS = [
    "component_id",
    "representative_raw_row_id",
    "representative_basis_id",
    "representative_source0_addr",
    "representative_source1_addr",
    "representative_target_addr",
    "representative_coeff",
    "active_owner_count",
    "raw_support_count",
    "raw_coeff_sum",
    "representative_owner_active_flag",
]
PATH_COLUMNS = [
    "path_id",
    "fiber_row_id",
    "sample_count",
    "sum_value",
    "count_component0",
    "count_component1",
    "count_component2",
    "step_count",
    "path_component_sum",
    "component_sum_check_flag",
    "raw_row_word_exists_flag",
    "long_tens_gap_flag",
    "existing_prof_flag",
    "gap_witness_flag",
    "support_product_digits",
    "support_product_mod_1000000007",
    "support_product_mod_1000000009",
    "representative_coeff_product_digits",
    "representative_coeff_product_mod_1000000007",
    "representative_coeff_product_mod_1000000009",
]
STEP_COLUMNS = [
    "step_id",
    "path_id",
    "fiber_row_id",
    "step_index",
    "component_id",
    "raw_row_id",
    "basis_id",
    "source0_addr",
    "source1_addr",
    "target_addr",
    "coeff",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "component_row_count",
    "path_row_count",
    "fiber_row_count",
    "path_step_row_count",
    "gap_path_count",
    "existing_path_count",
    "max_sample_count",
    "component_sum_check_count",
    "raw_row_word_exists_count",
    "gap_witness_count",
    "representative_component_count",
    "representative_active_owner_count",
    "support_product_positive_count",
    "representative_coeff_product_positive_count",
    "current_explicit_raw_product_path_flag",
    "current_single_witness_per_fiber_flag",
    "current_all_raw_paths_materialized_flag",
    "current_composable_raw_address_path_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def composition_counts(sample_count: int, sum_value: int) -> tuple[int, int, int]:
    count2 = max(0, sum_value - sample_count)
    count1 = sum_value - 2 * count2
    count0 = sample_count - count1 - count2
    if min(count0, count1, count2) < 0:
        raise ValueError(f"invalid fiber composition: k={sample_count}, s={sum_value}")
    if count0 + count1 + count2 != sample_count:
        raise ValueError("component counts do not match sample count")
    if count1 + 2 * count2 != sum_value:
        raise ValueError("component counts do not match sum value")
    return count0, count1, count2


def representative_rows(
    triples: np.ndarray,
    row_owners: np.ndarray,
    active_component: np.ndarray,
    component_ids: list[int],
    raw_component_support: dict[int, int],
    raw_component_coeff: dict[int, int],
    component_owner_counts: dict[int, int],
) -> list[dict[str, int]]:
    row_components = active_component[row_owners]
    rows: list[dict[str, int]] = []
    for component_id in component_ids:
        matches = np.flatnonzero(row_components == component_id)
        if matches.size == 0:
            raise ValueError(f"component {component_id} has no raw row witness")
        raw_row_id = int(matches[0])
        basis_id = int(row_owners[raw_row_id])
        source0, source1, target, coeff = (int(value) for value in triples[raw_row_id])
        rows.append(
            {
                "component_id": component_id,
                "representative_raw_row_id": raw_row_id,
                "representative_basis_id": basis_id,
                "representative_source0_addr": source0,
                "representative_source1_addr": source1,
                "representative_target_addr": target,
                "representative_coeff": coeff,
                "active_owner_count": int(component_owner_counts[component_id]),
                "raw_support_count": int(raw_component_support[component_id]),
                "raw_coeff_sum": int(raw_component_coeff[component_id]),
                "representative_owner_active_flag": int(active_component[basis_id] == component_id),
            }
        )
    return rows


def product_mod(values: list[int], counts: list[int], modulus: int) -> int:
    total = 1
    for value, count in zip(values, counts):
        total = (total * pow(value % modulus, count, modulus)) % modulus
    return total


def product_digits(values: list[int], counts: list[int]) -> int:
    total = 1
    for value, count in zip(values, counts):
        total *= value**count
    return len(str(total))


def build_rows() -> dict[str, Any]:
    input_reports = {
        "long_lln": load_json(LONG_LLN_REPORT),
        "long_rec": load_json(LONG_REC_REPORT),
        "long_lap": load_json(LONG_LAP_REPORT),
        "long_tens": load_json(LONG_TENS_REPORT),
        "long_lift": load_json(LONG_LIFT_REPORT),
        "long_raw": load_json(LONG_RAW_REPORT),
    }
    triples = load_raw_triples()
    owner_grid, owner_table = load_rec_tables()
    raw = raw_owner_profiles(triples, owner_grid, owner_table)
    active_component, _, component_to_basis, component_ids, _ = active_component_maps(
        owner_table
    )
    row_owners = raw["owners"]
    raw_component_support = {
        component_id: int(raw["owner_support"][basis_ids].sum())
        for component_id, basis_ids in component_to_basis.items()
    }
    raw_component_coeff = {
        component_id: int(raw["owner_coeff"][basis_ids].sum())
        for component_id, basis_ids in component_to_basis.items()
    }
    component_owner_counts = {
        component_id: len(basis_ids)
        for component_id, basis_ids in component_to_basis.items()
    }
    component_rows = representative_rows(
        triples,
        row_owners,
        active_component,
        component_ids,
        raw_component_support,
        raw_component_coeff,
        component_owner_counts,
    )
    component_by_id = {row["component_id"]: row for row in component_rows}
    support_weights = [
        component_by_id[component_id]["raw_support_count"]
        for component_id in component_ids
    ]
    representative_coeffs = [
        component_by_id[component_id]["representative_coeff"]
        for component_id in component_ids
    ]
    representative_raw_rows = [
        component_by_id[component_id]["representative_raw_row_id"]
        for component_id in component_ids
    ]
    representative_basis_ids = [
        component_by_id[component_id]["representative_basis_id"]
        for component_id in component_ids
    ]

    tens_fiber_rows = int_rows(read_csv_rows(LONG_TENS_FIBER))
    path_rows: list[dict[str, int]] = []
    step_rows: list[dict[str, int]] = []
    step_id = 0
    for path_id, fiber in enumerate(tens_fiber_rows):
        sample_count = fiber["sample_count"]
        sum_value = fiber["sum_value"]
        counts = list(composition_counts(sample_count, sum_value))
        support_digits = product_digits(support_weights, counts)
        coeff_digits = product_digits(representative_coeffs, counts)
        path_component_sum = counts[1] + 2 * counts[2]
        component_sum_check = int(
            sum(counts) == sample_count and path_component_sum == sum_value
        )
        raw_row_word_exists = int(
            all(count == 0 or representative_raw_rows[index] >= 0 for index, count in enumerate(counts))
        )
        gap_flag = fiber["long_obj_object_gap_flag"]
        path_rows.append(
            {
                "path_id": path_id,
                "fiber_row_id": fiber["fiber_row_id"],
                "sample_count": sample_count,
                "sum_value": sum_value,
                "count_component0": counts[0],
                "count_component1": counts[1],
                "count_component2": counts[2],
                "step_count": sample_count,
                "path_component_sum": path_component_sum,
                "component_sum_check_flag": component_sum_check,
                "raw_row_word_exists_flag": raw_row_word_exists,
                "long_tens_gap_flag": gap_flag,
                "existing_prof_flag": fiber["existing_prof_flag"],
                "gap_witness_flag": int(gap_flag == 1 and raw_row_word_exists == 1),
                "support_product_digits": support_digits,
                "support_product_mod_1000000007": product_mod(
                    support_weights, counts, MOD_PRIMES[0]
                ),
                "support_product_mod_1000000009": product_mod(
                    support_weights, counts, MOD_PRIMES[1]
                ),
                "representative_coeff_product_digits": coeff_digits,
                "representative_coeff_product_mod_1000000007": product_mod(
                    representative_coeffs, counts, MOD_PRIMES[0]
                ),
                "representative_coeff_product_mod_1000000009": product_mod(
                    representative_coeffs, counts, MOD_PRIMES[1]
                ),
            }
        )
        for component_index, count in enumerate(counts):
            component_id = component_ids[component_index]
            raw_row_id = representative_raw_rows[component_index]
            basis_id = representative_basis_ids[component_index]
            source0, source1, target, coeff = (
                int(value) for value in triples[raw_row_id]
            )
            for _ in range(count):
                step_rows.append(
                    {
                        "step_id": step_id,
                        "path_id": path_id,
                        "fiber_row_id": fiber["fiber_row_id"],
                        "step_index": step_id
                        - sum(row["step_count"] for row in path_rows[:-1]),
                        "component_id": component_id,
                        "raw_row_id": raw_row_id,
                        "basis_id": basis_id,
                        "source0_addr": source0,
                        "source1_addr": source1,
                        "target_addr": target,
                        "coeff": coeff,
                    }
                )
                step_id += 1

    obs = {
        "component_row_count": len(component_rows),
        "path_row_count": len(path_rows),
        "fiber_row_count": len(tens_fiber_rows),
        "path_step_row_count": len(step_rows),
        "gap_path_count": sum(row["long_tens_gap_flag"] for row in path_rows),
        "existing_path_count": sum(row["existing_prof_flag"] for row in path_rows),
        "max_sample_count": max(row["sample_count"] for row in path_rows),
        "component_sum_check_count": sum(
            row["component_sum_check_flag"] for row in path_rows
        ),
        "raw_row_word_exists_count": sum(
            row["raw_row_word_exists_flag"] for row in path_rows
        ),
        "gap_witness_count": sum(row["gap_witness_flag"] for row in path_rows),
        "representative_component_count": len(component_rows),
        "representative_active_owner_count": sum(
            row["representative_owner_active_flag"] for row in component_rows
        ),
        "support_product_positive_count": sum(
            int(row["support_product_digits"] > 0) for row in path_rows
        ),
        "representative_coeff_product_positive_count": sum(
            int(row["representative_coeff_product_digits"] > 0) for row in path_rows
        ),
        "current_explicit_raw_product_path_flag": 1,
        "current_single_witness_per_fiber_flag": 1,
        "current_all_raw_paths_materialized_flag": 0,
        "current_composable_raw_address_path_flag": 0,
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
    step_hash = hashlib.sha256(
        digest_text(STEP_COLUMNS, step_rows).encode("ascii")
    ).hexdigest()
    return {
        "input_reports": input_reports,
        "component_rows": component_rows,
        "path_rows": path_rows,
        "step_rows": step_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "component_table": table_from_rows(COMPONENT_COLUMNS, component_rows),
        "path_table": table_from_rows(PATH_COLUMNS, path_rows),
        "step_table": table_from_rows(STEP_COLUMNS, step_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "component_hash": component_hash,
        "path_hash": path_hash,
        "step_hash": step_hash,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    input_reports = rows["input_reports"]
    checks = {
        "input_certified": (
            input_reports["long_lln"].get("status"),
            input_reports["long_rec"].get("status"),
            input_reports["long_lap"].get("status"),
            input_reports["long_tens"].get("status"),
            input_reports["long_lift"].get("status"),
            input_reports["long_raw"].get("status"),
        )
        == (
            LONG_LLN_STATUS,
            LONG_REC_STATUS,
            LONG_LAP_STATUS,
            LONG_TENS_STATUS,
            LONG_LIFT_STATUS,
            LONG_RAW_STATUS,
        ),
        "representative_components_exact": (
            obs["component_row_count"],
            obs["representative_component_count"],
            obs["representative_active_owner_count"],
            rows["component_hash"],
        )
        == (3, 3, 3, COMPONENT_TEXT_HASH),
        "path_witness_exact": (
            obs["path_row_count"],
            obs["fiber_row_count"],
            obs["gap_path_count"],
            obs["existing_path_count"],
            obs["max_sample_count"],
            obs["component_sum_check_count"],
            obs["raw_row_word_exists_count"],
            obs["gap_witness_count"],
            obs["support_product_positive_count"],
            obs["representative_coeff_product_positive_count"],
            rows["path_hash"],
        )
        == (288, 288, 208, 80, 16, 288, 288, 208, 288, 288, PATH_TEXT_HASH),
        "step_witness_exact": (
            obs["path_step_row_count"],
            rows["step_hash"],
        )
        == (3128, STEP_TEXT_HASH),
        "current_representation_exact": (
            obs["current_explicit_raw_product_path_flag"],
            obs["current_single_witness_per_fiber_flag"],
            obs["current_all_raw_paths_materialized_flag"],
            obs["current_composable_raw_address_path_flag"],
        )
        == (1, 1, 0, 0),
        "table_shapes_match": (
            tuple(rows["component_table"].shape),
            tuple(rows["path_table"].shape),
            tuple(rows["step_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (3, len(COMPONENT_COLUMNS)),
            (288, len(PATH_COLUMNS)),
            (3128, len(STEP_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "explicit_single_raw_product_path_per_sum_fiber",
        "components": {
            "component_row_count": obs["component_row_count"],
            "representative_component_count": obs["representative_component_count"],
            "representative_active_owner_count": obs[
                "representative_active_owner_count"
            ],
            "component_table_sha256": sha_array(rows["component_table"]),
            "component_text_sha256": rows["component_hash"],
        },
        "paths": {
            "path_row_count": obs["path_row_count"],
            "fiber_row_count": obs["fiber_row_count"],
            "path_step_row_count": obs["path_step_row_count"],
            "gap_path_count": obs["gap_path_count"],
            "existing_path_count": obs["existing_path_count"],
            "max_sample_count": obs["max_sample_count"],
            "component_sum_check_count": obs["component_sum_check_count"],
            "raw_row_word_exists_count": obs["raw_row_word_exists_count"],
            "gap_witness_count": obs["gap_witness_count"],
            "path_table_sha256": sha_array(rows["path_table"]),
            "path_text_sha256": rows["path_hash"],
            "step_table_sha256": sha_array(rows["step_table"]),
            "step_text_sha256": rows["step_hash"],
        },
        "current_representation": {
            "current_explicit_raw_product_path_flag": obs[
                "current_explicit_raw_product_path_flag"
            ],
            "current_single_witness_per_fiber_flag": obs[
                "current_single_witness_per_fiber_flag"
            ],
            "current_all_raw_paths_materialized_flag": obs[
                "current_all_raw_paths_materialized_flag"
            ],
            "current_composable_raw_address_path_flag": obs[
                "current_composable_raw_address_path_flag"
            ],
        },
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    path_payload = {
        "schema": "long.path@1",
        "object": "explicit_single_raw_product_path_per_sum_fiber",
        "status": STATUS if all(checks.values()) else "LONG_PATH_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.path.report@1",
        "status": path_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_path certifies a concrete finite raw tensor lookup path "
            "witness for every long_tens sum-state fiber. The path object is "
            "single-witness and product-sample based: it chooses one raw row "
            "representative for each active component and expands each fiber "
            "into a step table whose component values sum to the requested "
            "fiber value. This proves finite raw sample-path nonemptiness for "
            "all 208 horizon-9..16 gap fibers without claiming all paths or "
            "inter-step C985/profunctor composability."
        ),
        "stage_protocol": {
            "draft": "read long_raw, long_tens, long_lap, long_rec, and raw tensor artifacts",
            "witness": "choose one raw tensor row per active component and expand one product path per sum-state fiber",
            "coherence": "check component representatives, fiber sums, gap coverage, step table shape, flags, hashes, and input statuses",
            "closure": "emit a finite sample-path witness while keeping composable-address paths out of scope",
            "emit": "write long_path artifacts and verifier hook",
        },
        "inputs": {
            "raw_tensor": input_entry(RAW_TENSOR),
            "long_lln_report": input_entry(
                LONG_LLN_REPORT,
                {"status": rows["input_reports"]["long_lln"].get("status")},
            ),
            "long_lln_tables": input_entry(LONG_LLN_TABLES),
            "long_rec_report": input_entry(
                LONG_REC_REPORT,
                {"status": rows["input_reports"]["long_rec"].get("status")},
            ),
            "long_rec_owner": input_entry(LONG_REC_OWNER),
            "long_rec_tables": input_entry(LONG_REC_TABLES),
            "long_lap_report": input_entry(
                LONG_LAP_REPORT,
                {"status": rows["input_reports"]["long_lap"].get("status")},
            ),
            "long_lap_node": input_entry(LONG_LAP_NODE),
            "long_lap_component": input_entry(LONG_LAP_COMPONENT),
            "long_lap_tables": input_entry(LONG_LAP_TABLES),
            "long_tens_report": input_entry(
                LONG_TENS_REPORT,
                {"status": rows["input_reports"]["long_tens"].get("status")},
            ),
            "long_tens_fiber": input_entry(LONG_TENS_FIBER),
            "long_tens_horizon": input_entry(LONG_TENS_HORIZON),
            "long_tens_tables": input_entry(LONG_TENS_TABLES),
            "long_lift_report": input_entry(
                LONG_LIFT_REPORT,
                {"status": rows["input_reports"]["long_lift"].get("status")},
            ),
            "long_lift_tables": input_entry(LONG_LIFT_TABLES),
            "long_raw_report": input_entry(
                LONG_RAW_REPORT,
                {"status": rows["input_reports"]["long_raw"].get("status")},
            ),
            "long_raw_tables": input_entry(LONG_RAW_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "path": relpath(OUT_DIR / "path.json"),
            "component_csv": relpath(OUT_DIR / "component.csv"),
            "path_csv": relpath(OUT_DIR / "path.csv"),
            "step_csv": relpath(OUT_DIR / "step.csv"),
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
                "one explicit raw tensor row representative for each active long_lap component",
                "one finite raw product path for every one of the 288 long_tens sum-state fibers",
                "one finite raw product path for every one of the 208 horizon-9..16 gap fibers",
                "the step-expanded product paths have component sums equal to their fiber sums",
            ],
            "does_not_certify_because_out_of_scope": [
                "all raw product paths in each fiber",
                "inter-step C985 source/target composability",
                "a genuine long_prof horizon-16 profunctor",
                "an infinite-horizon LLN theorem",
            ],
        },
        "next_highest_yield_item": (
            "Build long_comp: add inter-step source/target compatibility tests "
            "for the long_path witnesses, or certify that LLN sample paths do not "
            "require C985 composability."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.path.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.path.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "path": path_payload,
        "component_csv": csv_text(COMPONENT_COLUMNS, rows["component_rows"]),
        "path_csv": csv_text(PATH_COLUMNS, rows["path_rows"]),
        "step_csv": csv_text(STEP_COLUMNS, rows["step_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "component_table": rows["component_table"],
        "path_table": rows["path_table"],
        "step_table": rows["step_table"],
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
    write_json(OUT_DIR / "path.json", payloads["path"])
    (OUT_DIR / "component.csv").write_text(
        payloads["component_csv"], encoding="utf-8"
    )
    (OUT_DIR / "path.csv").write_text(payloads["path_csv"], encoding="utf-8")
    (OUT_DIR / "step.csv").write_text(payloads["step_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        component_table=payloads["component_table"],
        path_table=payloads["path_table"],
        step_table=payloads["step_table"],
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
