from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_obj import (
        COMPARISON_COLUMNS,
        COMPARISON_TEXT_HASH,
        DERIVE_SCRIPT,
        HORIZON_COLUMNS,
        HORIZON_TEXT_HASH,
        INDEX_PATH,
        LONG_CONV_MARGINAL,
        LONG_CONV_REPORT,
        LONG_CONV_TABLES,
        LONG_DEV_DISTRIBUTION,
        LONG_DEV_REPORT,
        LONG_DEV_TABLES,
        LONG_EXT_EXTENSION,
        LONG_EXT_OBJECT,
        LONG_EXT_REPORT,
        LONG_EXT_TABLES,
        LONG_LLN_REPORT,
        LONG_PROF_COMPOSE,
        LONG_PROF_OBJECT,
        LONG_PROF_REPORT,
        LONG_PROF_TABLES,
        LONG_UNIV_ARROW,
        LONG_UNIV_NODE,
        LONG_UNIV_REPORT,
        LONG_UNIV_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OBJECT_COLUMNS,
        OBJECT_TEXT_HASH,
        OUT_DIR,
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
    from derive_long_obj import (
        COMPARISON_COLUMNS,
        COMPARISON_TEXT_HASH,
        DERIVE_SCRIPT,
        HORIZON_COLUMNS,
        HORIZON_TEXT_HASH,
        INDEX_PATH,
        LONG_CONV_MARGINAL,
        LONG_CONV_REPORT,
        LONG_CONV_TABLES,
        LONG_DEV_DISTRIBUTION,
        LONG_DEV_REPORT,
        LONG_DEV_TABLES,
        LONG_EXT_EXTENSION,
        LONG_EXT_OBJECT,
        LONG_EXT_REPORT,
        LONG_EXT_TABLES,
        LONG_LLN_REPORT,
        LONG_PROF_COMPOSE,
        LONG_PROF_OBJECT,
        LONG_PROF_REPORT,
        LONG_PROF_TABLES,
        LONG_UNIV_ARROW,
        LONG_UNIV_NODE,
        LONG_UNIV_REPORT,
        LONG_UNIV_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OBJECT_COLUMNS,
        OBJECT_TEXT_HASH,
        OUT_DIR,
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


def validate_long_obj() -> dict[str, Any]:
    expected = build_payloads()
    obj_payload = load_json(OUT_DIR / "obj.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if obj_payload != expected["obj"]:
        raise AssertionError("long_obj obj JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_obj cert mismatch")
    for filename, key in {
        "object.csv": "object_csv",
        "horizon.csv": "horizon_csv",
        "comparison.csv": "comparison_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_obj {filename} mismatch")

    for key, expected_array in {
        "object_table": expected["object_table"],
        "horizon_table": expected["horizon_table"],
        "comparison_table": expected["comparison_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_obj table mismatch: {key}")

    if report.get("schema") != "long.obj.report@1":
        raise AssertionError("long_obj report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_obj report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_obj all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_obj checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_obj report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_obj report hash mismatch")

    csv_shapes = [
        ("object.csv", OBJECT_COLUMNS, 4),
        ("horizon.csv", HORIZON_COLUMNS, 16),
        ("comparison.csv", COMPARISON_COLUMNS, 288),
    ]
    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_obj {filename} shape mismatch")

    table_shapes = {
        "object_table": (4, len(OBJECT_COLUMNS)),
        "horizon_table": (16, len(HORIZON_COLUMNS)),
        "comparison_table": (288, len(COMPARISON_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_obj {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "object_row_count": 4,
        "horizon_row_count": 16,
        "comparison_row_count": 288,
        "expected_sum_state_total": 288,
        "conv_marginal_row_count": 288,
        "long_dev_distribution_row_count": 80,
        "long_prof_deviation_law_count": 80,
        "long_ext_formal_added_row_count": 208,
        "tensor_lookup_object_row_count": 80,
        "object_gap_row_count": 208,
        "tensor_lookup_object_horizon_count": 8,
        "object_gap_horizon_count": 8,
        "formal_object_count": 2,
        "genuine_tensor_lookup_object_count": 2,
        "convolution_shadow_object_count": 2,
        "source_horizon_gap": 8,
        "target_row_gap": 208,
        "formula_violation_count": 0,
        "comparison_mismatch_count": 0,
        "current_evidence_genuine_extension_flag": 0,
        "current_evidence_object_gap_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_obj observable {key} mismatch")

    if hashlib.sha256(
        digest_text(OBJECT_COLUMNS, csv_rows["object.csv"]).encode("ascii")
    ).hexdigest() != OBJECT_TEXT_HASH:
        raise AssertionError("long_obj object hash mismatch")
    if hashlib.sha256(
        digest_text(HORIZON_COLUMNS, csv_rows["horizon.csv"]).encode("ascii")
    ).hexdigest() != HORIZON_TEXT_HASH:
        raise AssertionError("long_obj horizon hash mismatch")
    if hashlib.sha256(
        digest_text(COMPARISON_COLUMNS, csv_rows["comparison.csv"]).encode("ascii")
    ).hexdigest() != COMPARISON_TEXT_HASH:
        raise AssertionError("long_obj comparison hash mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_lln_report": LONG_LLN_REPORT,
        "long_ext_report": LONG_EXT_REPORT,
        "long_ext_extension": LONG_EXT_EXTENSION,
        "long_ext_object": LONG_EXT_OBJECT,
        "long_ext_tables": LONG_EXT_TABLES,
        "long_conv_report": LONG_CONV_REPORT,
        "long_conv_marginal": LONG_CONV_MARGINAL,
        "long_conv_tables": LONG_CONV_TABLES,
        "long_dev_report": LONG_DEV_REPORT,
        "long_dev_distribution": LONG_DEV_DISTRIBUTION,
        "long_dev_tables": LONG_DEV_TABLES,
        "long_prof_report": LONG_PROF_REPORT,
        "long_prof_object": LONG_PROF_OBJECT,
        "long_prof_compose": LONG_PROF_COMPOSE,
        "long_prof_tables": LONG_PROF_TABLES,
        "long_univ_report": LONG_UNIV_REPORT,
        "long_univ_node": LONG_UNIV_NODE,
        "long_univ_arrow": LONG_UNIV_ARROW,
        "long_univ_tables": LONG_UNIV_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.obj.manifest@1":
        raise AssertionError("long_obj manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_obj manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_obj manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_obj missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_obj proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_obj proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.obj.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "objects": witness.get("objects"),
            "horizons": witness.get("horizons"),
            "comparison": witness.get("comparison"),
            "object_gap": witness.get("object_gap"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_obj(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
