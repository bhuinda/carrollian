from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_mart import (
        DERIVE_SCRIPT,
        EDGE_COLUMNS,
        EDGE_TEXT_HASH,
        INDEX_PATH,
        LEVEL_COLUMNS,
        LEVEL_TEXT_HASH,
        LONG_DUAL_PATH,
        LONG_DUAL_REPORT,
        LONG_DUAL_TABLES,
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_TABLES,
        LONG_PROB_DIST,
        LONG_PROB_MOMENT,
        LONG_PROB_REPORT,
        LONG_PROB_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATE_COLUMNS,
        STATE_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        rows_from_table,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_mart import (
        DERIVE_SCRIPT,
        EDGE_COLUMNS,
        EDGE_TEXT_HASH,
        INDEX_PATH,
        LEVEL_COLUMNS,
        LEVEL_TEXT_HASH,
        LONG_DUAL_PATH,
        LONG_DUAL_REPORT,
        LONG_DUAL_TABLES,
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_TABLES,
        LONG_PROB_DIST,
        LONG_PROB_MOMENT,
        LONG_PROB_REPORT,
        LONG_PROB_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATE_COLUMNS,
        STATE_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        rows_from_table,
        self_hash,
    )


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} is not a JSON object")
    return payload


def assert_file_hash(entry: dict[str, Any], expected_path: Path, label: str) -> None:
    expected_rel = expected_path.relative_to(ROOT).as_posix()
    if entry.get("path") != expected_rel:
        raise AssertionError(f"{label} path mismatch: {entry.get('path')}")
    if entry.get("sha256") != h_file(expected_path):
        raise AssertionError(f"{label} sha256 mismatch")


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def validate_long_mart() -> dict[str, Any]:
    expected = build_payloads()
    mart_payload = load_json(OUT_DIR / "mart.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if mart_payload != expected["mart"]:
        raise AssertionError("long_mart mart JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_mart cert mismatch")
    for filename, key in {
        "edge.csv": "edge_csv",
        "state.csv": "state_csv",
        "level.csv": "level_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_mart {filename} mismatch")

    for key, expected_array in {
        "edge_table": expected["edge_table"],
        "state_table": expected["state_table"],
        "level_table": expected["level_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_mart table mismatch: {key}")

    if report.get("schema") != "long.mart.report@1":
        raise AssertionError("long_mart report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_mart report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_mart all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_mart checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_mart report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_mart report hash mismatch")

    csv_shapes = [
        ("edge.csv", EDGE_COLUMNS, 525),
        ("state.csv", STATE_COLUMNS, 255),
        ("level.csv", LEVEL_COLUMNS, 15),
    ]
    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_mart {filename} shape mismatch")

    table_shapes = {
        "edge_table": (525, len(EDGE_COLUMNS)),
        "state_table": (255, len(STATE_COLUMNS)),
        "level_table": (15, len(LEVEL_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_mart {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "level_row_count": 15,
        "edge_row_count": 525,
        "state_row_count": 255,
        "source_row_count_sum": 255,
        "target_row_count_sum": 285,
        "row_marginal_flag_count": 255,
        "col_marginal_flag_count": 285,
        "drift_positive_count": 240,
        "drift_negative_count": 1,
        "drift_zero_count": 14,
        "eventual_submartingale_level_count": 14,
        "global_martingale_row_count": 14,
        "variance_shrink_level_count": 15,
        "variance_decomp_level_count": 15,
        "max_outgoing_edge_count": 3,
        "transport_mass_mod_sum_1000000007": 290_450_850,
        "conditional_noise_num_mod_sum_1000000007": 139_149_809,
        "predicted_variance_num_mod_sum_1000000007": 847_852_262,
        "drift_abs_num_mod_sum_1000000007": 236_694_364,
        "first_level_negative_drift_count": 1,
        "last_level_positive_drift_count": 30,
        "current_transport_operator_flag": 1,
        "current_global_martingale_flag": 0,
        "current_eventual_submartingale_flag": 1,
        "current_variance_supermartingale_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_mart observable {key} mismatch")

    if hashlib.sha256(
        digest_text(EDGE_COLUMNS, csv_rows["edge.csv"]).encode("ascii")
    ).hexdigest() != EDGE_TEXT_HASH:
        raise AssertionError("long_mart edge hash mismatch")
    if hashlib.sha256(
        digest_text(STATE_COLUMNS, csv_rows["state.csv"]).encode("ascii")
    ).hexdigest() != STATE_TEXT_HASH:
        raise AssertionError("long_mart state hash mismatch")
    if hashlib.sha256(
        digest_text(LEVEL_COLUMNS, csv_rows["level.csv"]).encode("ascii")
    ).hexdigest() != LEVEL_TEXT_HASH:
        raise AssertionError("long_mart level hash mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_prob_report": LONG_PROB_REPORT,
        "long_prob_dist": LONG_PROB_DIST,
        "long_prob_moment": LONG_PROB_MOMENT,
        "long_prob_tables": LONG_PROB_TABLES,
        "long_dual_report": LONG_DUAL_REPORT,
        "long_dual_path": LONG_DUAL_PATH,
        "long_dual_tables": LONG_DUAL_TABLES,
        "long_path_report": LONG_PATH_REPORT,
        "long_path_path": LONG_PATH_PATH,
        "long_path_tables": LONG_PATH_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.mart.manifest@1":
        raise AssertionError("long_mart manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_mart manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_mart manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_mart missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_mart proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_mart proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.mart.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "transport": witness.get("transport"),
            "drift": witness.get("drift"),
            "variance": witness.get("variance"),
            "current_representation": witness.get("current_representation"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_mart(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
