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
    from .derive_long_hlim import OUT_DIR as LONG_HLIM_DIR, STATUS as LONG_HLIM_STATUS
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
    from derive_long_hlim import OUT_DIR as LONG_HLIM_DIR, STATUS as LONG_HLIM_STATUS
    from derive_long_prof import OUT_DIR as LONG_PROF_DIR, STATUS as LONG_PROF_STATUS
    from derive_long_univ import OUT_DIR as LONG_UNIV_DIR, STATUS as LONG_UNIV_STATUS
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_ext"
STATUS = "LONG_EXT_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

LONG_HLIM_REPORT = LONG_HLIM_DIR / "report.json"
LONG_HLIM_OBSTRUCTION = LONG_HLIM_DIR / "obstruction.csv"
LONG_HLIM_HORIZON = LONG_HLIM_DIR / "horizon.csv"
LONG_HLIM_TABLES = LONG_HLIM_DIR / "tables.npz"
LONG_CONV_REPORT = LONG_CONV_DIR / "report.json"
LONG_CONV_MARGINAL = LONG_CONV_DIR / "marginal.csv"
LONG_CONV_TABLES = LONG_CONV_DIR / "tables.npz"
LONG_PROF_REPORT = LONG_PROF_DIR / "report.json"
LONG_PROF_OBJECT = LONG_PROF_DIR / "object.csv"
LONG_PROF_PROFUNCTOR = LONG_PROF_DIR / "profunctor.csv"
LONG_PROF_TABLES = LONG_PROF_DIR / "tables.npz"
LONG_UNIV_REPORT = LONG_UNIV_DIR / "report.json"
LONG_UNIV_NODE = LONG_UNIV_DIR / "node.csv"
LONG_UNIV_ARROW = LONG_UNIV_DIR / "arrow.csv"
LONG_UNIV_TABLES = LONG_UNIV_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_ext.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_ext.py"

EXTENSION_TEXT_HASH = (
    "e8b3e9900d795b9389a76a99f7a01198a8dba5bbbf9dd71ce9c8bf8782303ddd"
)
OBJECT_TEXT_HASH = (
    "2178ec67c3c1982b06ffbc0f451ef640ad340604e944bff3880b2e39db64734e"
)
ARROW_TEXT_HASH = (
    "1d3b1b457ca2a75a8aeb0196ee5530f475a5c58885c561e57cb7caa694ef5fba"
)

EXTENSION_COLUMNS = [
    "extension_row_id",
    "sample_count",
    "sum_value",
    "marginal_row_id",
    "source_node_code",
    "target_node_code",
    "univ_arrow_code",
    "prof_source_object_code",
    "prof_target_object_code",
    "existing_prof_flag",
    "missing_prof_flag",
    "formal_added_flag",
    "conv_shadow_flag",
    "positive_flag",
    "prob_num_digits",
    "prob_den_digits",
    "prob_num_mod_1000000007",
    "prob_den_mod_1000000007",
    "prob_num_mod_1000000009",
    "prob_den_mod_1000000009",
]
OBJECT_COLUMNS = [
    "extension_object_id",
    "object_role_code",
    "long_prof_object_code",
    "long_univ_node_code",
    "address_count",
    "baseline_address_count",
    "address_delta",
    "existing_prof_flag",
    "long_univ_flag",
    "formal_extension_flag",
]
ARROW_COLUMNS = [
    "extension_arrow_id",
    "arrow_role_code",
    "profunctor_code",
    "long_univ_arrow_code",
    "source_code",
    "target_code",
    "source_count",
    "target_count",
    "support_entry_count",
    "positive_entry_count",
    "row_sum_one_count",
    "existing_prof_flag",
    "long_univ_flag",
    "formal_extension_flag",
    "conv_shadow_flag",
    "anchor_row_count",
    "added_row_count",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "extension_row_count",
    "existing_prof_row_count",
    "missing_prof_row_count",
    "formal_added_row_count",
    "conv_shadow_row_count",
    "positive_row_count",
    "object_row_count",
    "formal_extension_object_count",
    "address_delta_total",
    "arrow_row_count",
    "formal_extension_arrow_count",
    "long_prof_backed_arrow_count",
    "long_univ_backed_arrow_count",
    "conv_shadow_arrow_count",
    "source_horizon_delta",
    "target_row_delta",
    "minimal_added_row_count",
    "hlim_obstruction_row_count",
    "hlim_extension_horizon_count",
    "current_evidence_genuine_tensor_lookup_flag",
    "current_evidence_convolution_shadow_flag",
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


def row_by_name(rows: list[dict[str, str]], name_column: str, name: str) -> dict[str, str]:
    for row in rows:
        if row[name_column] == name:
            return row
    raise AssertionError(f"missing row {name!r} in {name_column}")


def row_by_code(rows: list[dict[str, str]], code_column: str, code: int) -> dict[str, str]:
    for row in rows:
        if int(row[code_column]) == code:
            return row
    raise AssertionError(f"missing code {code} in {code_column}")


def build_rows() -> dict[str, Any]:
    long_hlim = load_json(LONG_HLIM_REPORT)
    long_conv = load_json(LONG_CONV_REPORT)
    long_prof = load_json(LONG_PROF_REPORT)
    long_univ = load_json(LONG_UNIV_REPORT)
    marginal_rows = read_csv_rows(LONG_CONV_MARGINAL)
    hlim_horizon_rows = int_rows(read_csv_rows(LONG_HLIM_HORIZON))
    hlim_obstruction_rows = int_rows(read_csv_rows(LONG_HLIM_OBSTRUCTION))
    prof_object_rows = read_csv_rows(LONG_PROF_OBJECT)
    profunctor_rows = read_csv_rows(LONG_PROF_PROFUNCTOR)
    univ_node_rows = read_csv_rows(LONG_UNIV_NODE)
    univ_arrow_rows = read_csv_rows(LONG_UNIV_ARROW)

    path_sum = row_by_name(
        profunctor_rows, "profunctor_name", "path_sum_distribution"
    )
    conv_path_sum = row_by_name(univ_arrow_rows, "arrow_name", "conv_path_sum16")
    path_sum_arrow = row_by_name(univ_arrow_rows, "arrow_name", "path_sum_distribution")
    sample_horizon = row_by_name(prof_object_rows, "object_name", "sample_horizon")
    deviation_state = row_by_name(prof_object_rows, "object_name", "deviation_state")
    sample_horizon16 = row_by_name(univ_node_rows, "node_name", "sample_horizon16")
    sum_state16 = row_by_name(univ_node_rows, "node_name", "sum_state16")
    hlim_extension_horizon_count = sum(row["extension_flag"] for row in hlim_horizon_rows)

    extension_rows: list[dict[str, int]] = []
    for marginal_row_id, row in enumerate(marginal_rows):
        prof_match_flag = int(row["prof_match_flag"])
        existing_flag = int(prof_match_flag == 1)
        missing_flag = int(prof_match_flag == -1)
        extension_rows.append(
            {
                "extension_row_id": marginal_row_id,
                "sample_count": int(row["sample_count"]),
                "sum_value": int(row["sum_value"]),
                "marginal_row_id": marginal_row_id,
                "source_node_code": int(conv_path_sum["source_node_code"]),
                "target_node_code": int(conv_path_sum["target_node_code"]),
                "univ_arrow_code": int(conv_path_sum["arrow_code"]),
                "prof_source_object_code": int(path_sum["source_object_code"])
                if existing_flag
                else -1,
                "prof_target_object_code": int(path_sum["target_object_code"])
                if existing_flag
                else -1,
                "existing_prof_flag": existing_flag,
                "missing_prof_flag": missing_flag,
                "formal_added_flag": missing_flag,
                "conv_shadow_flag": missing_flag,
                "positive_flag": int(row["positive_flag"]),
                "prob_num_digits": int(row["prob_num_digits"]),
                "prob_den_digits": int(row["prob_den_digits"]),
                "prob_num_mod_1000000007": int(row["prob_num_mod_1000000007"]),
                "prob_den_mod_1000000007": int(row["prob_den_mod_1000000007"]),
                "prob_num_mod_1000000009": int(row["prob_num_mod_1000000009"]),
                "prob_den_mod_1000000009": int(row["prob_den_mod_1000000009"]),
            }
        )

    baseline_source_count = int(path_sum["source_count"])
    baseline_target_count = int(path_sum["target_count"])
    extension_source_count = int(conv_path_sum["source_count"])
    extension_target_count = int(conv_path_sum["target_count"])
    object_rows = [
        {
            "extension_object_id": 0,
            "object_role_code": 0,
            "long_prof_object_code": int(sample_horizon["object_code"]),
            "long_univ_node_code": int(row_by_code(univ_node_rows, "node_code", 7)["node_code"]),
            "address_count": int(sample_horizon["address_count"]),
            "baseline_address_count": baseline_source_count,
            "address_delta": 0,
            "existing_prof_flag": 1,
            "long_univ_flag": 1,
            "formal_extension_flag": 0,
        },
        {
            "extension_object_id": 1,
            "object_role_code": 1,
            "long_prof_object_code": int(deviation_state["object_code"]),
            "long_univ_node_code": int(row_by_code(univ_node_rows, "node_code", 8)["node_code"]),
            "address_count": int(deviation_state["address_count"]),
            "baseline_address_count": baseline_target_count,
            "address_delta": 0,
            "existing_prof_flag": 1,
            "long_univ_flag": 1,
            "formal_extension_flag": 0,
        },
        {
            "extension_object_id": 2,
            "object_role_code": 2,
            "long_prof_object_code": -1,
            "long_univ_node_code": int(sample_horizon16["node_code"]),
            "address_count": int(sample_horizon16["address_count"]),
            "baseline_address_count": baseline_source_count,
            "address_delta": int(sample_horizon16["address_count"]) - baseline_source_count,
            "existing_prof_flag": 0,
            "long_univ_flag": 1,
            "formal_extension_flag": 1,
        },
        {
            "extension_object_id": 3,
            "object_role_code": 3,
            "long_prof_object_code": -1,
            "long_univ_node_code": int(sum_state16["node_code"]),
            "address_count": int(sum_state16["address_count"]),
            "baseline_address_count": baseline_target_count,
            "address_delta": int(sum_state16["address_count"]) - baseline_target_count,
            "existing_prof_flag": 0,
            "long_univ_flag": 1,
            "formal_extension_flag": 1,
        },
    ]
    arrow_rows = [
        {
            "extension_arrow_id": 0,
            "arrow_role_code": 0,
            "profunctor_code": int(path_sum["profunctor_code"]),
            "long_univ_arrow_code": int(path_sum_arrow["arrow_code"]),
            "source_code": int(path_sum["source_object_code"]),
            "target_code": int(path_sum["target_object_code"]),
            "source_count": baseline_source_count,
            "target_count": baseline_target_count,
            "support_entry_count": int(path_sum["support_entry_count"]),
            "positive_entry_count": int(path_sum["positive_entry_count"]),
            "row_sum_one_count": int(path_sum_arrow["row_sum_one_count"]),
            "existing_prof_flag": 1,
            "long_univ_flag": 1,
            "formal_extension_flag": 0,
            "conv_shadow_flag": 0,
            "anchor_row_count": baseline_target_count,
            "added_row_count": 0,
        },
        {
            "extension_arrow_id": 1,
            "arrow_role_code": 1,
            "profunctor_code": -1,
            "long_univ_arrow_code": int(conv_path_sum["arrow_code"]),
            "source_code": int(conv_path_sum["source_node_code"]),
            "target_code": int(conv_path_sum["target_node_code"]),
            "source_count": extension_source_count,
            "target_count": extension_target_count,
            "support_entry_count": int(conv_path_sum["support_entry_count"]),
            "positive_entry_count": int(conv_path_sum["positive_entry_count"]),
            "row_sum_one_count": int(conv_path_sum["row_sum_one_count"]),
            "existing_prof_flag": 0,
            "long_univ_flag": 1,
            "formal_extension_flag": 1,
            "conv_shadow_flag": 1,
            "anchor_row_count": baseline_target_count,
            "added_row_count": extension_target_count - baseline_target_count,
        },
    ]
    obs = {
        "extension_row_count": len(extension_rows),
        "existing_prof_row_count": sum(row["existing_prof_flag"] for row in extension_rows),
        "missing_prof_row_count": sum(row["missing_prof_flag"] for row in extension_rows),
        "formal_added_row_count": sum(row["formal_added_flag"] for row in extension_rows),
        "conv_shadow_row_count": sum(row["conv_shadow_flag"] for row in extension_rows),
        "positive_row_count": sum(row["positive_flag"] for row in extension_rows),
        "object_row_count": len(object_rows),
        "formal_extension_object_count": sum(
            row["formal_extension_flag"] for row in object_rows
        ),
        "address_delta_total": sum(row["address_delta"] for row in object_rows),
        "arrow_row_count": len(arrow_rows),
        "formal_extension_arrow_count": sum(
            row["formal_extension_flag"] for row in arrow_rows
        ),
        "long_prof_backed_arrow_count": sum(
            row["existing_prof_flag"] for row in arrow_rows
        ),
        "long_univ_backed_arrow_count": sum(row["long_univ_flag"] for row in arrow_rows),
        "conv_shadow_arrow_count": sum(row["conv_shadow_flag"] for row in arrow_rows),
        "source_horizon_delta": extension_source_count - baseline_source_count,
        "target_row_delta": extension_target_count - baseline_target_count,
        "minimal_added_row_count": len(hlim_obstruction_rows),
        "hlim_obstruction_row_count": len(hlim_obstruction_rows),
        "hlim_extension_horizon_count": hlim_extension_horizon_count,
        "current_evidence_genuine_tensor_lookup_flag": 0,
        "current_evidence_convolution_shadow_flag": 1,
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    extension_hash = hashlib.sha256(
        digest_text(EXTENSION_COLUMNS, extension_rows).encode("ascii")
    ).hexdigest()
    object_hash = hashlib.sha256(
        digest_text(OBJECT_COLUMNS, object_rows).encode("ascii")
    ).hexdigest()
    arrow_hash = hashlib.sha256(
        digest_text(ARROW_COLUMNS, arrow_rows).encode("ascii")
    ).hexdigest()
    return {
        "input_reports": {
            "long_hlim": long_hlim,
            "long_conv": long_conv,
            "long_prof": long_prof,
            "long_univ": long_univ,
        },
        "extension_rows": extension_rows,
        "object_rows": object_rows,
        "arrow_rows": arrow_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "extension_table": table_from_rows(EXTENSION_COLUMNS, extension_rows),
        "object_table": table_from_rows(OBJECT_COLUMNS, object_rows),
        "arrow_table": table_from_rows(ARROW_COLUMNS, arrow_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "extension_hash": extension_hash,
        "object_hash": object_hash,
        "arrow_hash": arrow_hash,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    input_reports = rows["input_reports"]
    checks = {
        "input_certified": (
            input_reports["long_hlim"].get("status"),
            input_reports["long_conv"].get("status"),
            input_reports["long_prof"].get("status"),
            input_reports["long_univ"].get("status"),
        )
        == (
            LONG_HLIM_STATUS,
            LONG_CONV_STATUS,
            LONG_PROF_STATUS,
            LONG_UNIV_STATUS,
        ),
        "extension_fingerprint_exact": (
            obs["extension_row_count"],
            obs["existing_prof_row_count"],
            obs["missing_prof_row_count"],
            obs["formal_added_row_count"],
            obs["conv_shadow_row_count"],
            obs["positive_row_count"],
            rows["extension_hash"],
        )
        == (288, 80, 208, 208, 208, 288, EXTENSION_TEXT_HASH),
        "object_fingerprint_exact": (
            obs["object_row_count"],
            obs["formal_extension_object_count"],
            obs["address_delta_total"],
            rows["object_hash"],
        )
        == (4, 2, 216, OBJECT_TEXT_HASH),
        "arrow_fingerprint_exact": (
            obs["arrow_row_count"],
            obs["formal_extension_arrow_count"],
            obs["long_prof_backed_arrow_count"],
            obs["long_univ_backed_arrow_count"],
            obs["conv_shadow_arrow_count"],
            rows["arrow_hash"],
        )
        == (2, 1, 1, 2, 1, ARROW_TEXT_HASH),
        "classification_exact": (
            obs["current_evidence_genuine_tensor_lookup_flag"],
            obs["current_evidence_convolution_shadow_flag"],
            obs["minimal_added_row_count"],
            obs["hlim_obstruction_row_count"],
            obs["hlim_extension_horizon_count"],
            obs["target_row_delta"],
        )
        == (0, 1, 208, 208, 8, 208),
        "table_shapes_match": (
            tuple(rows["extension_table"].shape),
            tuple(rows["object_table"].shape),
            tuple(rows["arrow_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (288, len(EXTENSION_COLUMNS)),
            (4, len(OBJECT_COLUMNS)),
            (2, len(ARROW_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "minimal_formal_profunctor_extension_shadow",
        "extension": {
            "extension_row_count": obs["extension_row_count"],
            "existing_prof_row_count": obs["existing_prof_row_count"],
            "missing_prof_row_count": obs["missing_prof_row_count"],
            "formal_added_row_count": obs["formal_added_row_count"],
            "conv_shadow_row_count": obs["conv_shadow_row_count"],
            "positive_row_count": obs["positive_row_count"],
            "text_sha256": rows["extension_hash"],
            "table_sha256": sha_array(rows["extension_table"]),
        },
        "objects": {
            "object_row_count": obs["object_row_count"],
            "formal_extension_object_count": obs["formal_extension_object_count"],
            "address_delta_total": obs["address_delta_total"],
            "text_sha256": rows["object_hash"],
            "table_sha256": sha_array(rows["object_table"]),
        },
        "arrows": {
            "arrow_row_count": obs["arrow_row_count"],
            "formal_extension_arrow_count": obs["formal_extension_arrow_count"],
            "long_prof_backed_arrow_count": obs["long_prof_backed_arrow_count"],
            "long_univ_backed_arrow_count": obs["long_univ_backed_arrow_count"],
            "conv_shadow_arrow_count": obs["conv_shadow_arrow_count"],
            "text_sha256": rows["arrow_hash"],
            "table_sha256": sha_array(rows["arrow_table"]),
        },
        "classification_flags": {
            "current_evidence_genuine_tensor_lookup_flag": obs[
                "current_evidence_genuine_tensor_lookup_flag"
            ],
            "current_evidence_convolution_shadow_flag": obs[
                "current_evidence_convolution_shadow_flag"
            ],
            "minimal_added_row_count": obs["minimal_added_row_count"],
            "hlim_obstruction_row_count": obs["hlim_obstruction_row_count"],
        },
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    ext_payload = {
        "schema": "long.ext@1",
        "object": "minimal_formal_profunctor_extension",
        "status": STATUS if all(checks.values()) else "LONG_EXT_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.ext.report@1",
        "status": ext_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_ext certifies the minimal formal extension that fills the "
            "208 long_hlim missing comparison rows. The extension is backed "
            "by long_univ and long_conv, but the current certified evidence "
            "classifies it as a convolution shadow rather than a genuine "
            "long_prof tensor-lookup profunctor object."
        ),
        "stage_protocol": {
            "draft": "read long_hlim, long_conv, long_prof, and long_univ artifacts",
            "witness": "mark the 80 profunctor-backed rows and the 208 formal added rows",
            "coherence": "check input status, extension/object/arrow fingerprints, classification flags, hashes, and shapes",
            "closure": "emit extension, object, arrow, table, certificate, manifest, and report artifacts",
            "emit": "write long_ext artifacts and verifier hook",
        },
        "inputs": {
            "long_hlim_report": input_entry(
                LONG_HLIM_REPORT,
                {"status": rows["input_reports"]["long_hlim"].get("status")},
            ),
            "long_hlim_obstruction": input_entry(LONG_HLIM_OBSTRUCTION),
            "long_hlim_horizon": input_entry(LONG_HLIM_HORIZON),
            "long_hlim_tables": input_entry(LONG_HLIM_TABLES),
            "long_conv_report": input_entry(
                LONG_CONV_REPORT,
                {"status": rows["input_reports"]["long_conv"].get("status")},
            ),
            "long_conv_marginal": input_entry(LONG_CONV_MARGINAL),
            "long_conv_tables": input_entry(LONG_CONV_TABLES),
            "long_prof_report": input_entry(
                LONG_PROF_REPORT,
                {"status": rows["input_reports"]["long_prof"].get("status")},
            ),
            "long_prof_object": input_entry(LONG_PROF_OBJECT),
            "long_prof_profunctor": input_entry(LONG_PROF_PROFUNCTOR),
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
            "ext": relpath(OUT_DIR / "ext.json"),
            "extension_csv": relpath(OUT_DIR / "extension.csv"),
            "object_csv": relpath(OUT_DIR / "object.csv"),
            "arrow_csv": relpath(OUT_DIR / "arrow.csv"),
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
                "the formal extension has exactly 288 rows: 80 existing profunctor rows plus 208 added rows",
                "the 208 added rows match the long_hlim obstruction count and target-row delta",
                "the added rows are present as the long_univ conv_path_sum16 arrow and long_conv marginal table",
                "the current certified evidence marks the formal extension as a convolution shadow",
            ],
            "does_not_certify_because_out_of_scope": [
                "a genuine long_prof tensor-lookup object for the 208 added rows",
                "a proof that no future tensor-lookup profunctor extension exists",
                "an infinite-horizon LLN theorem",
                "a categorical universal property for the formal extension",
            ],
        },
        "next_highest_yield_item": (
            "Build long_obj: test whether the formal long_ext rows close under "
            "actual tensor-lookup object laws, instead of only appearing as a "
            "long_conv path-sum shadow."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.ext.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.ext.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "ext": ext_payload,
        "extension_csv": csv_text(EXTENSION_COLUMNS, rows["extension_rows"]),
        "object_csv": csv_text(OBJECT_COLUMNS, rows["object_rows"]),
        "arrow_csv": csv_text(ARROW_COLUMNS, rows["arrow_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "extension_table": rows["extension_table"],
        "object_table": rows["object_table"],
        "arrow_table": rows["arrow_table"],
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
    write_json(OUT_DIR / "ext.json", payloads["ext"])
    (OUT_DIR / "extension.csv").write_text(payloads["extension_csv"], encoding="utf-8")
    (OUT_DIR / "object.csv").write_text(payloads["object_csv"], encoding="utf-8")
    (OUT_DIR / "arrow.csv").write_text(payloads["arrow_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        extension_table=payloads["extension_table"],
        object_table=payloads["object_table"],
        arrow_table=payloads["arrow_table"],
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
