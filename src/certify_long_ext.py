from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_ext import (
        ARROW_COLUMNS,
        ARROW_TEXT_HASH,
        DERIVE_SCRIPT,
        EXTENSION_COLUMNS,
        EXTENSION_TEXT_HASH,
        INDEX_PATH,
        LONG_CONV_MARGINAL,
        LONG_CONV_REPORT,
        LONG_CONV_TABLES,
        LONG_HLIM_HORIZON,
        LONG_HLIM_OBSTRUCTION,
        LONG_HLIM_REPORT,
        LONG_HLIM_TABLES,
        LONG_PROF_OBJECT,
        LONG_PROF_PROFUNCTOR,
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
    from derive_long_ext import (
        ARROW_COLUMNS,
        ARROW_TEXT_HASH,
        DERIVE_SCRIPT,
        EXTENSION_COLUMNS,
        EXTENSION_TEXT_HASH,
        INDEX_PATH,
        LONG_CONV_MARGINAL,
        LONG_CONV_REPORT,
        LONG_CONV_TABLES,
        LONG_HLIM_HORIZON,
        LONG_HLIM_OBSTRUCTION,
        LONG_HLIM_REPORT,
        LONG_HLIM_TABLES,
        LONG_PROF_OBJECT,
        LONG_PROF_PROFUNCTOR,
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


def validate_long_ext() -> dict[str, Any]:
    expected = build_payloads()
    ext_payload = load_json(OUT_DIR / "ext.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if ext_payload != expected["ext"]:
        raise AssertionError("long_ext ext JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_ext cert mismatch")
    for filename, key in {
        "extension.csv": "extension_csv",
        "object.csv": "object_csv",
        "arrow.csv": "arrow_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_ext {filename} mismatch")

    for key, expected_array in {
        "extension_table": expected["extension_table"],
        "object_table": expected["object_table"],
        "arrow_table": expected["arrow_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_ext table mismatch: {key}")

    if report.get("schema") != "long.ext.report@1":
        raise AssertionError("long_ext report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_ext report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_ext all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_ext checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_ext report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_ext report hash mismatch")

    csv_shapes = [
        ("extension.csv", EXTENSION_COLUMNS, 288),
        ("object.csv", OBJECT_COLUMNS, 4),
        ("arrow.csv", ARROW_COLUMNS, 2),
    ]
    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_ext {filename} shape mismatch")

    table_shapes = {
        "extension_table": (288, len(EXTENSION_COLUMNS)),
        "object_table": (4, len(OBJECT_COLUMNS)),
        "arrow_table": (2, len(ARROW_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_ext {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "extension_row_count": 288,
        "existing_prof_row_count": 80,
        "missing_prof_row_count": 208,
        "formal_added_row_count": 208,
        "conv_shadow_row_count": 208,
        "positive_row_count": 288,
        "object_row_count": 4,
        "formal_extension_object_count": 2,
        "address_delta_total": 216,
        "arrow_row_count": 2,
        "formal_extension_arrow_count": 1,
        "long_prof_backed_arrow_count": 1,
        "long_univ_backed_arrow_count": 2,
        "conv_shadow_arrow_count": 1,
        "source_horizon_delta": 8,
        "target_row_delta": 208,
        "minimal_added_row_count": 208,
        "hlim_obstruction_row_count": 208,
        "hlim_extension_horizon_count": 8,
        "current_evidence_genuine_tensor_lookup_flag": 0,
        "current_evidence_convolution_shadow_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_ext observable {key} mismatch")

    if hashlib.sha256(
        digest_text(EXTENSION_COLUMNS, csv_rows["extension.csv"]).encode("ascii")
    ).hexdigest() != EXTENSION_TEXT_HASH:
        raise AssertionError("long_ext extension hash mismatch")
    if hashlib.sha256(
        digest_text(OBJECT_COLUMNS, csv_rows["object.csv"]).encode("ascii")
    ).hexdigest() != OBJECT_TEXT_HASH:
        raise AssertionError("long_ext object hash mismatch")
    if hashlib.sha256(
        digest_text(ARROW_COLUMNS, csv_rows["arrow.csv"]).encode("ascii")
    ).hexdigest() != ARROW_TEXT_HASH:
        raise AssertionError("long_ext arrow hash mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_hlim_report": LONG_HLIM_REPORT,
        "long_hlim_obstruction": LONG_HLIM_OBSTRUCTION,
        "long_hlim_horizon": LONG_HLIM_HORIZON,
        "long_hlim_tables": LONG_HLIM_TABLES,
        "long_conv_report": LONG_CONV_REPORT,
        "long_conv_marginal": LONG_CONV_MARGINAL,
        "long_conv_tables": LONG_CONV_TABLES,
        "long_prof_report": LONG_PROF_REPORT,
        "long_prof_object": LONG_PROF_OBJECT,
        "long_prof_profunctor": LONG_PROF_PROFUNCTOR,
        "long_prof_tables": LONG_PROF_TABLES,
        "long_univ_report": LONG_UNIV_REPORT,
        "long_univ_node": LONG_UNIV_NODE,
        "long_univ_arrow": LONG_UNIV_ARROW,
        "long_univ_tables": LONG_UNIV_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.ext.manifest@1":
        raise AssertionError("long_ext manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_ext manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_ext manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_ext missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_ext proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_ext proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.ext.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "extension": witness.get("extension"),
            "objects": witness.get("objects"),
            "arrows": witness.get("arrows"),
            "classification_flags": witness.get("classification_flags"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_ext(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
