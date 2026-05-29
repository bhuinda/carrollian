from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_dual import (
        COMPONENT_COLUMNS,
        COMPONENT_TEXT_HASH,
        DERIVE_SCRIPT,
        EDGE_COLUMNS,
        EDGE_TEXT_HASH,
        INDEX_PATH,
        LONG_COMP_REPORT,
        LONG_COMP_TABLES,
        LONG_COMP_TRANSITION,
        LONG_ORIENT_PAIR,
        LONG_ORIENT_REPORT,
        LONG_ORIENT_TABLES,
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_TABLES,
        LONG_SHEAF_REPORT,
        LONG_SHEAF_SECTION,
        LONG_SHEAF_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PATH_COLUMNS,
        PATH_TEXT_HASH,
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
    from derive_long_dual import (
        COMPONENT_COLUMNS,
        COMPONENT_TEXT_HASH,
        DERIVE_SCRIPT,
        EDGE_COLUMNS,
        EDGE_TEXT_HASH,
        INDEX_PATH,
        LONG_COMP_REPORT,
        LONG_COMP_TABLES,
        LONG_COMP_TRANSITION,
        LONG_ORIENT_PAIR,
        LONG_ORIENT_REPORT,
        LONG_ORIENT_TABLES,
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_TABLES,
        LONG_SHEAF_REPORT,
        LONG_SHEAF_SECTION,
        LONG_SHEAF_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PATH_COLUMNS,
        PATH_TEXT_HASH,
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


def validate_long_dual() -> dict[str, Any]:
    expected = build_payloads()
    dual_payload = load_json(OUT_DIR / "dual.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if dual_payload != expected["dual"]:
        raise AssertionError("long_dual dual JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_dual cert mismatch")
    for filename, key in {
        "component.csv": "component_csv",
        "path.csv": "path_csv",
        "edge.csv": "edge_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_dual {filename} mismatch")

    for key, expected_array in {
        "component_table": expected["component_table"],
        "path_table": expected["path_table"],
        "edge_table": expected["edge_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_dual table mismatch: {key}")

    if report.get("schema") != "long.dual.report@1":
        raise AssertionError("long_dual report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_dual report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_dual all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_dual checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_dual report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_dual report hash mismatch")

    csv_shapes = [
        ("component.csv", COMPONENT_COLUMNS, 3),
        ("path.csv", PATH_COLUMNS, 288),
        ("edge.csv", EDGE_COLUMNS, 5),
    ]
    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_dual {filename} shape mismatch")

    table_shapes = {
        "component_table": (3, len(COMPONENT_COLUMNS)),
        "path_table": (288, len(PATH_COLUMNS)),
        "edge_table": (5, len(EDGE_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_dual {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "component_row_count": 3,
        "witness_path_count": 288,
        "witness_step_count": 3128,
        "transition_count": 2840,
        "coeff_kernel_nonzero_component_count": 3,
        "count_kernel_nonzero_component_count": 1,
        "coeff_kernel_nonzero_step_count": 3128,
        "count_kernel_nonzero_step_count": 816,
        "dual_path_coeff_nonzero_count": 288,
        "dual_path_count_nonzero_count": 16,
        "dual_path_positive_count": 288,
        "dual_coeff_product_digit_max": 27,
        "dual_coeff_path_sum_min": 12,
        "dual_coeff_path_sum_max": 768,
        "dual_coeff_product_mod_sum_1000000007": 497_101_086,
        "dual_coeff_product_mod_sum_1000000009": 118_327_119,
        "edge_row_count": 5,
        "edge_chain_flag_count": 5,
        "edge_backward_count": 0,
        "edge_skip_count": 0,
        "dual_transition_compose_count": 2840,
        "dual_edge_product_sum": 2_196_000,
        "component_signed_coeff_gcd": 6,
        "component_signed_coeff_min": 12,
        "component_signed_coeff_max": 48,
        "current_coeff_dual_kernel_flag": 1,
        "current_count_dual_kernel_flag": 0,
        "current_witness_composition_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_dual observable {key} mismatch")

    if hashlib.sha256(
        digest_text(COMPONENT_COLUMNS, csv_rows["component.csv"]).encode("ascii")
    ).hexdigest() != COMPONENT_TEXT_HASH:
        raise AssertionError("long_dual component hash mismatch")
    if hashlib.sha256(
        digest_text(PATH_COLUMNS, csv_rows["path.csv"]).encode("ascii")
    ).hexdigest() != PATH_TEXT_HASH:
        raise AssertionError("long_dual path hash mismatch")
    if hashlib.sha256(
        digest_text(EDGE_COLUMNS, csv_rows["edge.csv"]).encode("ascii")
    ).hexdigest() != EDGE_TEXT_HASH:
        raise AssertionError("long_dual edge hash mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_orient_report": LONG_ORIENT_REPORT,
        "long_orient_pair": LONG_ORIENT_PAIR,
        "long_orient_tables": LONG_ORIENT_TABLES,
        "long_sheaf_report": LONG_SHEAF_REPORT,
        "long_sheaf_section": LONG_SHEAF_SECTION,
        "long_sheaf_tables": LONG_SHEAF_TABLES,
        "long_path_report": LONG_PATH_REPORT,
        "long_path_path": LONG_PATH_PATH,
        "long_path_tables": LONG_PATH_TABLES,
        "long_comp_report": LONG_COMP_REPORT,
        "long_comp_transition": LONG_COMP_TRANSITION,
        "long_comp_tables": LONG_COMP_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.dual.manifest@1":
        raise AssertionError("long_dual manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_dual manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_dual manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_dual missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_dual proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_dual proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.dual.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "kernel": witness.get("kernel"),
            "path_composition": witness.get("path_composition"),
            "transition_composition": witness.get("transition_composition"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_dual(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
