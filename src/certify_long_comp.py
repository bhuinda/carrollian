from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_comp import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_LLN_REPORT,
        LONG_LLN_TABLES,
        LONG_PATH_COMPONENT,
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_STEP,
        LONG_PATH_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PAIR_COLUMNS,
        PAIR_TEXT_HASH,
        PATH_COLUMNS,
        PATH_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        TRANSITION_COLUMNS,
        TRANSITION_TEXT_HASH,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        rows_from_table,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_comp import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_LLN_REPORT,
        LONG_LLN_TABLES,
        LONG_PATH_COMPONENT,
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_STEP,
        LONG_PATH_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PAIR_COLUMNS,
        PAIR_TEXT_HASH,
        PATH_COLUMNS,
        PATH_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        TRANSITION_COLUMNS,
        TRANSITION_TEXT_HASH,
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


def validate_long_comp() -> dict[str, Any]:
    expected = build_payloads()
    comp_payload = load_json(OUT_DIR / "comp.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if comp_payload != expected["comp"]:
        raise AssertionError("long_comp comp JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_comp cert mismatch")
    for filename, key in {
        "pair.csv": "pair_csv",
        "path.csv": "path_csv",
        "transition.csv": "transition_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_comp {filename} mismatch")

    for key, expected_array in {
        "pair_table": expected["pair_table"],
        "path_table": expected["path_table"],
        "transition_table": expected["transition_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_comp table mismatch: {key}")

    if report.get("schema") != "long.comp.report@1":
        raise AssertionError("long_comp report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_comp report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_comp all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_comp checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_comp report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_comp report hash mismatch")

    csv_shapes = [
        ("pair.csv", PAIR_COLUMNS, 5),
        ("path.csv", PATH_COLUMNS, 288),
        ("transition.csv", TRANSITION_COLUMNS, 2840),
    ]
    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_comp {filename} shape mismatch")

    table_shapes = {
        "pair_table": (5, len(PAIR_COLUMNS)),
        "path_table": (288, len(PATH_COLUMNS)),
        "transition_table": (2840, len(TRANSITION_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_comp {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "pair_row_count": 5,
        "path_row_count": 288,
        "step_row_count": 3128,
        "transition_row_count": 2840,
        "one_step_path_count": 3,
        "gap_path_count": 208,
        "existing_path_count": 80,
        "gap_transition_count": 2476,
        "existing_transition_count": 364,
        "zeta_left_transition_count": 2840,
        "zeta_right_transition_count": 2840,
        "zeta_both_transition_count": 2840,
        "zeta_path_count": 288,
        "gap_zeta_path_count": 208,
        "existing_zeta_path_count": 80,
        "exact_left_transition_count": 0,
        "exact_right_transition_count": 0,
        "exact_path_count": 0,
        "left_margin_min": 8,
        "left_margin_max": 171,
        "right_margin_min": 152,
        "right_margin_max": 708,
        "current_alexandrov_zeta_composable_path_flag": 1,
        "current_exact_source_target_composable_path_flag": 0,
        "current_c985_semantic_composable_path_flag": 0,
        "current_lln_product_sample_independence_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_comp observable {key} mismatch")

    if hashlib.sha256(
        digest_text(PAIR_COLUMNS, csv_rows["pair.csv"]).encode("ascii")
    ).hexdigest() != PAIR_TEXT_HASH:
        raise AssertionError("long_comp pair hash mismatch")
    if hashlib.sha256(
        digest_text(PATH_COLUMNS, csv_rows["path.csv"]).encode("ascii")
    ).hexdigest() != PATH_TEXT_HASH:
        raise AssertionError("long_comp path hash mismatch")
    if hashlib.sha256(
        digest_text(TRANSITION_COLUMNS, csv_rows["transition.csv"]).encode("ascii")
    ).hexdigest() != TRANSITION_TEXT_HASH:
        raise AssertionError("long_comp transition hash mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_lln_report": LONG_LLN_REPORT,
        "long_lln_tables": LONG_LLN_TABLES,
        "long_path_report": LONG_PATH_REPORT,
        "long_path_component": LONG_PATH_COMPONENT,
        "long_path_path": LONG_PATH_PATH,
        "long_path_step": LONG_PATH_STEP,
        "long_path_tables": LONG_PATH_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.comp.manifest@1":
        raise AssertionError("long_comp manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_comp manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_comp manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_comp missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_comp proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_comp proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.comp.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "inventory": witness.get("inventory"),
            "zeta_composability": witness.get("zeta_composability"),
            "exact_composability": witness.get("exact_composability"),
            "current_representation": witness.get("current_representation"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_comp(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
