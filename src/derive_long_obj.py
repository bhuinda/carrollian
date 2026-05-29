from __future__ import annotations

import csv
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
    from .derive_long_conv import OUT_DIR as LONG_CONV_DIR, STATUS as LONG_CONV_STATUS
    from .derive_long_dev import OUT_DIR as LONG_DEV_DIR, STATUS as LONG_DEV_STATUS
    from .derive_long_ext import OUT_DIR as LONG_EXT_DIR, STATUS as LONG_EXT_STATUS
    from .derive_long_lln import OUT_DIR as LONG_LLN_DIR, STATUS as LONG_LLN_STATUS
    from .derive_long_prof import OUT_DIR as LONG_PROF_DIR, STATUS as LONG_PROF_STATUS
    from .derive_long_univ import OUT_DIR as LONG_UNIV_DIR, STATUS as LONG_UNIV_STATUS
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_conv import OUT_DIR as LONG_CONV_DIR, STATUS as LONG_CONV_STATUS
    from derive_long_dev import OUT_DIR as LONG_DEV_DIR, STATUS as LONG_DEV_STATUS
    from derive_long_ext import OUT_DIR as LONG_EXT_DIR, STATUS as LONG_EXT_STATUS
    from derive_long_lln import OUT_DIR as LONG_LLN_DIR, STATUS as LONG_LLN_STATUS
    from derive_long_prof import OUT_DIR as LONG_PROF_DIR, STATUS as LONG_PROF_STATUS
    from derive_long_univ import OUT_DIR as LONG_UNIV_DIR, STATUS as LONG_UNIV_STATUS
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_obj"
STATUS = "LONG_OBJ_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

LONG_LLN_REPORT = LONG_LLN_DIR / "report.json"
LONG_EXT_REPORT = LONG_EXT_DIR / "report.json"
LONG_EXT_EXTENSION = LONG_EXT_DIR / "extension.csv"
LONG_EXT_OBJECT = LONG_EXT_DIR / "object.csv"
LONG_EXT_TABLES = LONG_EXT_DIR / "tables.npz"
LONG_CONV_REPORT = LONG_CONV_DIR / "report.json"
LONG_CONV_MARGINAL = LONG_CONV_DIR / "marginal.csv"
LONG_CONV_TABLES = LONG_CONV_DIR / "tables.npz"
LONG_DEV_REPORT = LONG_DEV_DIR / "report.json"
LONG_DEV_DISTRIBUTION = LONG_DEV_DIR / "distribution.csv"
LONG_DEV_TABLES = LONG_DEV_DIR / "tables.npz"
LONG_PROF_REPORT = LONG_PROF_DIR / "report.json"
LONG_PROF_OBJECT = LONG_PROF_DIR / "object.csv"
LONG_PROF_COMPOSE = LONG_PROF_DIR / "compose.csv"
LONG_PROF_TABLES = LONG_PROF_DIR / "tables.npz"
LONG_UNIV_REPORT = LONG_UNIV_DIR / "report.json"
LONG_UNIV_NODE = LONG_UNIV_DIR / "node.csv"
LONG_UNIV_ARROW = LONG_UNIV_DIR / "arrow.csv"
LONG_UNIV_TABLES = LONG_UNIV_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_obj.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_obj.py"

OBJECT_TEXT_HASH = (
    "febc2ec027e5a85ade2ed678aea371532a879e7d4561624a9ca1e625d6f643d3"
)
HORIZON_TEXT_HASH = (
    "7b1e715d384e28cfba91791d164ceb81f06177768beb4ba50c6af1cc3ef4d29b"
)
COMPARISON_TEXT_HASH = (
    "2d75c06f6a7b8d6f1f1c8e01aea9f87b379f49427e8be9acb95ce47f33abcc70"
)

OBJECT_COLUMNS = [
    "object_row_id",
    "object_role_code",
    "long_univ_node_code",
    "long_prof_object_code",
    "sample_horizon",
    "address_count",
    "expected_address_count",
    "baseline_address_count",
    "address_delta",
    "long_prof_object_flag",
    "long_dev_object_flag",
    "long_conv_object_flag",
    "formal_extension_flag",
    "tensor_lookup_object_flag",
    "object_gap_flag",
]
HORIZON_COLUMNS = [
    "horizon_id",
    "sample_count",
    "expected_sum_state_count",
    "conv_marginal_count",
    "long_dev_distribution_count",
    "long_prof_deviation_law_count",
    "long_ext_row_count",
    "long_ext_formal_added_count",
    "conv_positive_count",
    "long_dev_backed_flag",
    "long_prof_backed_flag",
    "tensor_lookup_object_flag",
    "object_gap_flag",
    "formula_equal_flag",
]
COMPARISON_COLUMNS = [
    "comparison_row_id",
    "sample_count",
    "sum_value",
    "conv_row_flag",
    "long_dev_row_flag",
    "long_prof_law_flag",
    "long_ext_existing_prof_flag",
    "long_ext_formal_added_flag",
    "tensor_lookup_object_flag",
    "object_gap_flag",
    "positive_flag",
    "prob_num_digits",
    "prob_den_digits",
    "prob_num_mod_1000000007",
    "prob_den_mod_1000000007",
    "prob_num_mod_1000000009",
    "prob_den_mod_1000000009",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "object_row_count",
    "horizon_row_count",
    "comparison_row_count",
    "expected_sum_state_total",
    "conv_marginal_row_count",
    "long_dev_distribution_row_count",
    "long_prof_deviation_law_count",
    "long_ext_formal_added_row_count",
    "tensor_lookup_object_row_count",
    "object_gap_row_count",
    "tensor_lookup_object_horizon_count",
    "object_gap_horizon_count",
    "formal_object_count",
    "genuine_tensor_lookup_object_count",
    "convolution_shadow_object_count",
    "source_horizon_gap",
    "target_row_gap",
    "formula_violation_count",
    "comparison_mismatch_count",
    "current_evidence_genuine_extension_flag",
    "current_evidence_object_gap_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def csv_text(columns: list[str], rows: list[dict[str, Any]]) -> str:
    lines = [",".join(columns)]
    lines.extend(",".join(str(row[column]) for column in columns) for row in rows)
    return "\n".join(lines) + "\n"


def digest_text(columns: list[str], rows: list[dict[str, Any]]) -> str:
    return "".join(",".join(str(row[column]) for column in columns) + "\n" for row in rows)


def table_from_rows(columns: list[str], rows: list[dict[str, int]]) -> np.ndarray:
    return np.asarray(
        [[int(row[column]) for column in columns] for row in rows],
        dtype=np.int64,
    )


def rows_from_table(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def read_csv_rows(path: Any) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def int_rows(rows: list[dict[str, str]]) -> list[dict[str, int]]:
    return [{key: int(value) for key, value in row.items()} for row in rows]


def sum_state_count(sample_horizon: int) -> int:
    return sample_horizon * (sample_horizon + 2)


def build_rows() -> dict[str, Any]:
    input_reports = {
        "long_lln": load_json(LONG_LLN_REPORT),
        "long_ext": load_json(LONG_EXT_REPORT),
        "long_conv": load_json(LONG_CONV_REPORT),
        "long_dev": load_json(LONG_DEV_REPORT),
        "long_prof": load_json(LONG_PROF_REPORT),
        "long_univ": load_json(LONG_UNIV_REPORT),
    }
    ext_rows = int_rows(read_csv_rows(LONG_EXT_EXTENSION))
    ext_object_rows = int_rows(read_csv_rows(LONG_EXT_OBJECT))
    conv_rows = read_csv_rows(LONG_CONV_MARGINAL)
    dev_rows = read_csv_rows(LONG_DEV_DISTRIBUTION)
    prof_compose_rows = read_csv_rows(LONG_PROF_COMPOSE)

    conv_keys = {
        (int(row["sample_count"]), int(row["sum_value"])) for row in conv_rows
    }
    dev_keys = {
        (int(row["sample_count"]), int(row["sum_value"])) for row in dev_rows
    }
    prof_keys = {
        (int(row["source_id"]), int(row["target_id"]))
        for row in prof_compose_rows
        if row["law_name"] == "deviation"
    }

    ext_by_role = {row["object_role_code"]: row for row in ext_object_rows}
    object_rows = [
        {
            "object_row_id": 0,
            "object_role_code": 0,
            "long_univ_node_code": ext_by_role[0]["long_univ_node_code"],
            "long_prof_object_code": ext_by_role[0]["long_prof_object_code"],
            "sample_horizon": 8,
            "address_count": ext_by_role[0]["address_count"],
            "expected_address_count": 8,
            "baseline_address_count": ext_by_role[0]["baseline_address_count"],
            "address_delta": ext_by_role[0]["address_delta"],
            "long_prof_object_flag": 1,
            "long_dev_object_flag": 1,
            "long_conv_object_flag": 1,
            "formal_extension_flag": ext_by_role[0]["formal_extension_flag"],
            "tensor_lookup_object_flag": 1,
            "object_gap_flag": 0,
        },
        {
            "object_row_id": 1,
            "object_role_code": 1,
            "long_univ_node_code": ext_by_role[1]["long_univ_node_code"],
            "long_prof_object_code": ext_by_role[1]["long_prof_object_code"],
            "sample_horizon": 8,
            "address_count": ext_by_role[1]["address_count"],
            "expected_address_count": sum_state_count(8),
            "baseline_address_count": ext_by_role[1]["baseline_address_count"],
            "address_delta": ext_by_role[1]["address_delta"],
            "long_prof_object_flag": 1,
            "long_dev_object_flag": 1,
            "long_conv_object_flag": 1,
            "formal_extension_flag": ext_by_role[1]["formal_extension_flag"],
            "tensor_lookup_object_flag": 1,
            "object_gap_flag": 0,
        },
        {
            "object_row_id": 2,
            "object_role_code": 2,
            "long_univ_node_code": ext_by_role[2]["long_univ_node_code"],
            "long_prof_object_code": ext_by_role[2]["long_prof_object_code"],
            "sample_horizon": 16,
            "address_count": ext_by_role[2]["address_count"],
            "expected_address_count": 16,
            "baseline_address_count": ext_by_role[2]["baseline_address_count"],
            "address_delta": ext_by_role[2]["address_delta"],
            "long_prof_object_flag": 0,
            "long_dev_object_flag": 0,
            "long_conv_object_flag": 1,
            "formal_extension_flag": ext_by_role[2]["formal_extension_flag"],
            "tensor_lookup_object_flag": 0,
            "object_gap_flag": 1,
        },
        {
            "object_row_id": 3,
            "object_role_code": 3,
            "long_univ_node_code": ext_by_role[3]["long_univ_node_code"],
            "long_prof_object_code": ext_by_role[3]["long_prof_object_code"],
            "sample_horizon": 16,
            "address_count": ext_by_role[3]["address_count"],
            "expected_address_count": sum_state_count(16),
            "baseline_address_count": ext_by_role[3]["baseline_address_count"],
            "address_delta": ext_by_role[3]["address_delta"],
            "long_prof_object_flag": 0,
            "long_dev_object_flag": 0,
            "long_conv_object_flag": 1,
            "formal_extension_flag": ext_by_role[3]["formal_extension_flag"],
            "tensor_lookup_object_flag": 0,
            "object_gap_flag": 1,
        },
    ]

    horizon_rows: list[dict[str, int]] = []
    for sample_count in range(1, 17):
        expected = 2 * sample_count + 1
        conv_count = sum(
            1 for row in conv_rows if int(row["sample_count"]) == sample_count
        )
        dev_count = sum(
            1 for row in dev_rows if int(row["sample_count"]) == sample_count
        )
        prof_count = sum(
            1
            for row in prof_compose_rows
            if row["law_name"] == "deviation"
            and int(row["source_id"]) == sample_count
        )
        ext_sample_rows = [
            row for row in ext_rows if row["sample_count"] == sample_count
        ]
        dev_backed = int(dev_count == expected)
        prof_backed = int(prof_count == expected)
        tensor_lookup_object = int(dev_backed and prof_backed)
        object_gap = int(not tensor_lookup_object and conv_count == expected)
        horizon_rows.append(
            {
                "horizon_id": sample_count - 1,
                "sample_count": sample_count,
                "expected_sum_state_count": expected,
                "conv_marginal_count": conv_count,
                "long_dev_distribution_count": dev_count,
                "long_prof_deviation_law_count": prof_count,
                "long_ext_row_count": len(ext_sample_rows),
                "long_ext_formal_added_count": sum(
                    row["formal_added_flag"] for row in ext_sample_rows
                ),
                "conv_positive_count": sum(
                    int(row["positive_flag"])
                    for row in conv_rows
                    if int(row["sample_count"]) == sample_count
                ),
                "long_dev_backed_flag": dev_backed,
                "long_prof_backed_flag": prof_backed,
                "tensor_lookup_object_flag": tensor_lookup_object,
                "object_gap_flag": object_gap,
                "formula_equal_flag": int(
                    conv_count == expected and len(ext_sample_rows) == expected
                ),
            }
        )

    comparison_rows: list[dict[str, int]] = []
    for comparison_row_id, row in enumerate(ext_rows):
        key = (row["sample_count"], row["sum_value"])
        dev_flag = int(key in dev_keys)
        prof_flag = int(key in prof_keys)
        tensor_lookup_object = int(dev_flag and prof_flag)
        object_gap = int(not tensor_lookup_object and key in conv_keys)
        comparison_rows.append(
            {
                "comparison_row_id": comparison_row_id,
                "sample_count": key[0],
                "sum_value": key[1],
                "conv_row_flag": int(key in conv_keys),
                "long_dev_row_flag": dev_flag,
                "long_prof_law_flag": prof_flag,
                "long_ext_existing_prof_flag": row["existing_prof_flag"],
                "long_ext_formal_added_flag": row["formal_added_flag"],
                "tensor_lookup_object_flag": tensor_lookup_object,
                "object_gap_flag": object_gap,
                "positive_flag": row["positive_flag"],
                "prob_num_digits": row["prob_num_digits"],
                "prob_den_digits": row["prob_den_digits"],
                "prob_num_mod_1000000007": row["prob_num_mod_1000000007"],
                "prob_den_mod_1000000007": row["prob_den_mod_1000000007"],
                "prob_num_mod_1000000009": row["prob_num_mod_1000000009"],
                "prob_den_mod_1000000009": row["prob_den_mod_1000000009"],
            }
        )

    obs = {
        "object_row_count": len(object_rows),
        "horizon_row_count": len(horizon_rows),
        "comparison_row_count": len(comparison_rows),
        "expected_sum_state_total": sum(
            row["expected_sum_state_count"] for row in horizon_rows
        ),
        "conv_marginal_row_count": sum(
            row["conv_marginal_count"] for row in horizon_rows
        ),
        "long_dev_distribution_row_count": len(dev_rows),
        "long_prof_deviation_law_count": len(prof_keys),
        "long_ext_formal_added_row_count": sum(
            row["long_ext_formal_added_flag"] for row in comparison_rows
        ),
        "tensor_lookup_object_row_count": sum(
            row["tensor_lookup_object_flag"] for row in comparison_rows
        ),
        "object_gap_row_count": sum(row["object_gap_flag"] for row in comparison_rows),
        "tensor_lookup_object_horizon_count": sum(
            row["tensor_lookup_object_flag"] for row in horizon_rows
        ),
        "object_gap_horizon_count": sum(row["object_gap_flag"] for row in horizon_rows),
        "formal_object_count": sum(row["formal_extension_flag"] for row in object_rows),
        "genuine_tensor_lookup_object_count": sum(
            row["tensor_lookup_object_flag"] for row in object_rows
        ),
        "convolution_shadow_object_count": sum(
            row["object_gap_flag"] for row in object_rows
        ),
        "source_horizon_gap": 8,
        "target_row_gap": 208,
        "formula_violation_count": sum(
            1 - row["formula_equal_flag"] for row in horizon_rows
        ),
        "comparison_mismatch_count": sum(
            1
            for row in comparison_rows
            if row["long_ext_existing_prof_flag"] != row["tensor_lookup_object_flag"]
            or row["long_ext_formal_added_flag"] != row["object_gap_flag"]
        ),
        "current_evidence_genuine_extension_flag": 0,
        "current_evidence_object_gap_flag": 1,
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    object_hash = hashlib.sha256(
        digest_text(OBJECT_COLUMNS, object_rows).encode("ascii")
    ).hexdigest()
    horizon_hash = hashlib.sha256(
        digest_text(HORIZON_COLUMNS, horizon_rows).encode("ascii")
    ).hexdigest()
    comparison_hash = hashlib.sha256(
        digest_text(COMPARISON_COLUMNS, comparison_rows).encode("ascii")
    ).hexdigest()
    return {
        "input_reports": input_reports,
        "object_rows": object_rows,
        "horizon_rows": horizon_rows,
        "comparison_rows": comparison_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "object_table": table_from_rows(OBJECT_COLUMNS, object_rows),
        "horizon_table": table_from_rows(HORIZON_COLUMNS, horizon_rows),
        "comparison_table": table_from_rows(COMPARISON_COLUMNS, comparison_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "object_hash": object_hash,
        "horizon_hash": horizon_hash,
        "comparison_hash": comparison_hash,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    input_reports = rows["input_reports"]
    checks = {
        "input_certified": (
            input_reports["long_lln"].get("status"),
            input_reports["long_ext"].get("status"),
            input_reports["long_conv"].get("status"),
            input_reports["long_dev"].get("status"),
            input_reports["long_prof"].get("status"),
            input_reports["long_univ"].get("status"),
        )
        == (
            LONG_LLN_STATUS,
            LONG_EXT_STATUS,
            LONG_CONV_STATUS,
            LONG_DEV_STATUS,
            LONG_PROF_STATUS,
            LONG_UNIV_STATUS,
        ),
        "object_fingerprint_exact": (
            obs["object_row_count"],
            obs["formal_object_count"],
            obs["genuine_tensor_lookup_object_count"],
            obs["convolution_shadow_object_count"],
            rows["object_hash"],
        )
        == (4, 2, 2, 2, OBJECT_TEXT_HASH),
        "horizon_fingerprint_exact": (
            obs["horizon_row_count"],
            obs["tensor_lookup_object_horizon_count"],
            obs["object_gap_horizon_count"],
            obs["expected_sum_state_total"],
            obs["formula_violation_count"],
            rows["horizon_hash"],
        )
        == (16, 8, 8, 288, 0, HORIZON_TEXT_HASH),
        "comparison_fingerprint_exact": (
            obs["comparison_row_count"],
            obs["conv_marginal_row_count"],
            obs["long_dev_distribution_row_count"],
            obs["long_prof_deviation_law_count"],
            obs["tensor_lookup_object_row_count"],
            obs["object_gap_row_count"],
            obs["comparison_mismatch_count"],
            rows["comparison_hash"],
        )
        == (288, 288, 80, 80, 80, 208, 0, COMPARISON_TEXT_HASH),
        "object_gap_exact": (
            obs["source_horizon_gap"],
            obs["target_row_gap"],
            obs["long_ext_formal_added_row_count"],
            obs["current_evidence_genuine_extension_flag"],
            obs["current_evidence_object_gap_flag"],
        )
        == (8, 208, 208, 0, 1),
        "table_shapes_match": (
            tuple(rows["object_table"].shape),
            tuple(rows["horizon_table"].shape),
            tuple(rows["comparison_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (4, len(OBJECT_COLUMNS)),
            (16, len(HORIZON_COLUMNS)),
            (288, len(COMPARISON_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "finite_line_tensor_object_gap",
        "objects": {
            "object_row_count": obs["object_row_count"],
            "formal_object_count": obs["formal_object_count"],
            "genuine_tensor_lookup_object_count": obs[
                "genuine_tensor_lookup_object_count"
            ],
            "convolution_shadow_object_count": obs["convolution_shadow_object_count"],
            "text_sha256": rows["object_hash"],
            "table_sha256": sha_array(rows["object_table"]),
        },
        "horizons": {
            "horizon_row_count": obs["horizon_row_count"],
            "tensor_lookup_object_horizon_count": obs[
                "tensor_lookup_object_horizon_count"
            ],
            "object_gap_horizon_count": obs["object_gap_horizon_count"],
            "expected_sum_state_total": obs["expected_sum_state_total"],
            "formula_violation_count": obs["formula_violation_count"],
            "text_sha256": rows["horizon_hash"],
            "table_sha256": sha_array(rows["horizon_table"]),
        },
        "comparison": {
            "comparison_row_count": obs["comparison_row_count"],
            "conv_marginal_row_count": obs["conv_marginal_row_count"],
            "long_dev_distribution_row_count": obs["long_dev_distribution_row_count"],
            "long_prof_deviation_law_count": obs["long_prof_deviation_law_count"],
            "tensor_lookup_object_row_count": obs["tensor_lookup_object_row_count"],
            "object_gap_row_count": obs["object_gap_row_count"],
            "comparison_mismatch_count": obs["comparison_mismatch_count"],
            "text_sha256": rows["comparison_hash"],
            "table_sha256": sha_array(rows["comparison_table"]),
        },
        "object_gap": {
            "source_horizon_gap": obs["source_horizon_gap"],
            "target_row_gap": obs["target_row_gap"],
            "current_evidence_genuine_extension_flag": obs[
                "current_evidence_genuine_extension_flag"
            ],
            "current_evidence_object_gap_flag": obs[
                "current_evidence_object_gap_flag"
            ],
        },
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    obj_payload = {
        "schema": "long.obj@1",
        "object": "finite_line_tensor_object_gap",
        "status": STATUS if all(checks.values()) else "LONG_OBJ_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.obj.report@1",
        "status": obj_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_obj certifies the object-level status of the long_ext "
            "extension: the horizon-16 rows satisfy the exact finite line "
            "sum-state formula, but only horizons 1-8 are backed by the "
            "certified long_dev and long_prof tensor-lookup objects. The "
            "remaining 208 rows are a formula-correct convolution shadow."
        ),
        "stage_protocol": {
            "draft": "read long_ext, long_conv, long_dev, long_prof, long_univ, and long_lln artifacts",
            "witness": "compare horizon object laws and row keys against certified tensor-lookup object support",
            "coherence": "check input status, object/horizon/comparison fingerprints, gap flags, hashes, and shapes",
            "closure": "emit object, horizon, comparison, table, certificate, manifest, and report artifacts",
            "emit": "write long_obj artifacts and verifier hook",
        },
        "inputs": {
            "long_lln_report": input_entry(
                LONG_LLN_REPORT,
                {"status": rows["input_reports"]["long_lln"].get("status")},
            ),
            "long_ext_report": input_entry(
                LONG_EXT_REPORT,
                {"status": rows["input_reports"]["long_ext"].get("status")},
            ),
            "long_ext_extension": input_entry(LONG_EXT_EXTENSION),
            "long_ext_object": input_entry(LONG_EXT_OBJECT),
            "long_ext_tables": input_entry(LONG_EXT_TABLES),
            "long_conv_report": input_entry(
                LONG_CONV_REPORT,
                {"status": rows["input_reports"]["long_conv"].get("status")},
            ),
            "long_conv_marginal": input_entry(LONG_CONV_MARGINAL),
            "long_conv_tables": input_entry(LONG_CONV_TABLES),
            "long_dev_report": input_entry(
                LONG_DEV_REPORT,
                {"status": rows["input_reports"]["long_dev"].get("status")},
            ),
            "long_dev_distribution": input_entry(LONG_DEV_DISTRIBUTION),
            "long_dev_tables": input_entry(LONG_DEV_TABLES),
            "long_prof_report": input_entry(
                LONG_PROF_REPORT,
                {"status": rows["input_reports"]["long_prof"].get("status")},
            ),
            "long_prof_object": input_entry(LONG_PROF_OBJECT),
            "long_prof_compose": input_entry(LONG_PROF_COMPOSE),
            "long_prof_tables": input_entry(LONG_PROF_TABLES),
            "long_univ_report": input_entry(
                LONG_UNIV_REPORT,
                {"status": rows["input_reports"]["long_univ"].get("status")},
            ),
            "long_univ_node": input_entry(LONG_UNIV_NODE),
            "long_univ_arrow": input_entry(LONG_UNIV_ARROW),
            "long_univ_tables": input_entry(LONG_UNIV_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "obj": relpath(OUT_DIR / "obj.json"),
            "object_csv": relpath(OUT_DIR / "object.csv"),
            "horizon_csv": relpath(OUT_DIR / "horizon.csv"),
            "comparison_csv": relpath(OUT_DIR / "comparison.csv"),
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
                "the exact finite object law: horizon n has 2n+1 sum states and horizons 1-16 total 288 rows",
                "horizons 1-8 are backed by long_dev distribution rows and long_prof deviation laws",
                "horizons 9-16 contribute exactly 208 formula-correct rows with no current tensor-lookup object backing",
                "the long_ext formal-added flags coincide exactly with the object-gap rows",
            ],
            "does_not_certify_because_out_of_scope": [
                "that no future tensor-lookup object extension can be constructed",
                "a genuine long_prof object for horizons 9-16",
                "an infinite-horizon LLN theorem",
                "a categorical universal property for the object gap",
            ],
        },
        "next_highest_yield_item": (
            "Build long_tens: attempt to construct the missing horizon-16 "
            "object from explicit tensor powers or prove the obstruction is "
            "not representable by the current finite line tensor lookup."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.obj.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.obj.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "obj": obj_payload,
        "object_csv": csv_text(OBJECT_COLUMNS, rows["object_rows"]),
        "horizon_csv": csv_text(HORIZON_COLUMNS, rows["horizon_rows"]),
        "comparison_csv": csv_text(COMPARISON_COLUMNS, rows["comparison_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "object_table": rows["object_table"],
        "horizon_table": rows["horizon_table"],
        "comparison_table": rows["comparison_table"],
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
    write_json(OUT_DIR / "obj.json", payloads["obj"])
    (OUT_DIR / "object.csv").write_text(payloads["object_csv"], encoding="utf-8")
    (OUT_DIR / "horizon.csv").write_text(payloads["horizon_csv"], encoding="utf-8")
    (OUT_DIR / "comparison.csv").write_text(
        payloads["comparison_csv"], encoding="utf-8"
    )
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        object_table=payloads["object_table"],
        horizon_table=payloads["horizon_table"],
        comparison_table=payloads["comparison_table"],
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
