from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_tens import (
        DERIVE_SCRIPT,
        FIBER_COLUMNS,
        FIBER_TEXT_HASH,
        HORIZON_COLUMNS,
        HORIZON_TEXT_HASH,
        INDEX_PATH,
        INVENTORY_COLUMNS,
        INVENTORY_TEXT_HASH,
        LONG_LLN_LINE,
        LONG_LLN_REPORT,
        LONG_LLN_TABLES,
        LONG_MARKOV_KERNEL,
        LONG_MARKOV_REPORT,
        LONG_MARKOV_STATIONARY,
        LONG_MARKOV_TABLES,
        LONG_OBJ_COMPARISON,
        LONG_OBJ_HORIZON,
        LONG_OBJ_REPORT,
        LONG_OBJ_TABLES,
        LONG_PROF_OBJECT,
        LONG_PROF_REPORT,
        LONG_PROF_TABLES,
        LONG_UNIV_NODE,
        LONG_UNIV_REPORT,
        LONG_UNIV_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
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
    from derive_long_tens import (
        DERIVE_SCRIPT,
        FIBER_COLUMNS,
        FIBER_TEXT_HASH,
        HORIZON_COLUMNS,
        HORIZON_TEXT_HASH,
        INDEX_PATH,
        INVENTORY_COLUMNS,
        INVENTORY_TEXT_HASH,
        LONG_LLN_LINE,
        LONG_LLN_REPORT,
        LONG_LLN_TABLES,
        LONG_MARKOV_KERNEL,
        LONG_MARKOV_REPORT,
        LONG_MARKOV_STATIONARY,
        LONG_MARKOV_TABLES,
        LONG_OBJ_COMPARISON,
        LONG_OBJ_HORIZON,
        LONG_OBJ_REPORT,
        LONG_OBJ_TABLES,
        LONG_PROF_OBJECT,
        LONG_PROF_REPORT,
        LONG_PROF_TABLES,
        LONG_UNIV_NODE,
        LONG_UNIV_REPORT,
        LONG_UNIV_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
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


def validate_long_tens() -> dict[str, Any]:
    expected = build_payloads()
    tens_payload = load_json(OUT_DIR / "tens.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if tens_payload != expected["tens"]:
        raise AssertionError("long_tens tens JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_tens cert mismatch")
    for filename, key in {
        "inventory.csv": "inventory_csv",
        "horizon.csv": "horizon_csv",
        "fiber.csv": "fiber_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_tens {filename} mismatch")

    for key, expected_array in {
        "inventory_table": expected["inventory_table"],
        "horizon_table": expected["horizon_table"],
        "fiber_table": expected["fiber_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_tens table mismatch: {key}")

    if report.get("schema") != "long.tens.report@1":
        raise AssertionError("long_tens report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_tens report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_tens all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_tens checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_tens report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_tens report hash mismatch")

    csv_shapes = [
        ("inventory.csv", INVENTORY_COLUMNS, 8),
        ("horizon.csv", HORIZON_COLUMNS, 16),
        ("fiber.csv", FIBER_COLUMNS, 288),
    ]
    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_tens {filename} shape mismatch")

    table_shapes = {
        "inventory_table": (8, len(INVENTORY_COLUMNS)),
        "horizon_table": (16, len(HORIZON_COLUMNS)),
        "fiber_table": (288, len(FIBER_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_tens {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "inventory_row_count": 8,
        "fiber_row_count": 288,
        "horizon_row_count": 16,
        "component_count": 3,
        "component_support_full_flag": 1,
        "total_sum_state_count": 288,
        "total_component_path_count": 64570080,
        "backed_sum_state_count": 80,
        "gap_sum_state_count": 208,
        "backed_component_path_count": 9840,
        "gap_component_path_count": 64560240,
        "materialized_component_path_object_count": 0,
        "current_sum_quotient_object_count": 2,
        "profunctor_backed_sum_object_count": 1,
        "formal_shadow_sum_object_count": 1,
        "finite_line_tensor_inventory_count": 4,
        "component_path_required_count": 2,
        "current_horizon16_component_path_flag": 0,
        "current_horizon16_sum_profunctor_flag": 0,
        "current_horizon16_sum_shadow_flag": 1,
        "fiber_total_matches_paths_flag": 1,
        "object_gap_matches_long_obj_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_tens observable {key} mismatch")

    if hashlib.sha256(
        digest_text(INVENTORY_COLUMNS, csv_rows["inventory.csv"]).encode("ascii")
    ).hexdigest() != INVENTORY_TEXT_HASH:
        raise AssertionError("long_tens inventory hash mismatch")
    if hashlib.sha256(
        digest_text(HORIZON_COLUMNS, csv_rows["horizon.csv"]).encode("ascii")
    ).hexdigest() != HORIZON_TEXT_HASH:
        raise AssertionError("long_tens horizon hash mismatch")
    if hashlib.sha256(
        digest_text(FIBER_COLUMNS, csv_rows["fiber.csv"]).encode("ascii")
    ).hexdigest() != FIBER_TEXT_HASH:
        raise AssertionError("long_tens fiber hash mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_obj_report": LONG_OBJ_REPORT,
        "long_obj_comparison": LONG_OBJ_COMPARISON,
        "long_obj_horizon": LONG_OBJ_HORIZON,
        "long_obj_tables": LONG_OBJ_TABLES,
        "long_lln_report": LONG_LLN_REPORT,
        "long_lln_line": LONG_LLN_LINE,
        "long_lln_tables": LONG_LLN_TABLES,
        "long_markov_report": LONG_MARKOV_REPORT,
        "long_markov_kernel": LONG_MARKOV_KERNEL,
        "long_markov_stationary": LONG_MARKOV_STATIONARY,
        "long_markov_tables": LONG_MARKOV_TABLES,
        "long_prof_report": LONG_PROF_REPORT,
        "long_prof_object": LONG_PROF_OBJECT,
        "long_prof_tables": LONG_PROF_TABLES,
        "long_univ_report": LONG_UNIV_REPORT,
        "long_univ_node": LONG_UNIV_NODE,
        "long_univ_tables": LONG_UNIV_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.tens.manifest@1":
        raise AssertionError("long_tens manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_tens manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_tens manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_tens missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_tens proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_tens proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.tens.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "inventory": witness.get("inventory"),
            "horizons": witness.get("horizons"),
            "fibers": witness.get("fibers"),
            "current_representation": witness.get("current_representation"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_tens(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
