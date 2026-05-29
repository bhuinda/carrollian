from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_univ import (
        ARROW_COLUMNS,
        ARROW_DIGEST_COLUMNS,
        ARROW_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LAW_COLUMNS,
        LAW_DIGEST_COLUMNS,
        LAW_TEXT_HASH,
        LONG_CLS_MEAN,
        LONG_CLS_MOMENT,
        LONG_CLS_REPORT,
        LONG_CLS_SHRINK,
        LONG_CLS_TABLES,
        LONG_CLS_TAIL,
        LONG_CONV_MARGINAL,
        LONG_CONV_REPORT,
        LONG_CONV_TABLES,
        LONG_LLN_REPORT,
        LONG_MARKOV_REPORT,
        LONG_MARKOV_STATIONARY,
        LONG_MARKOV_TABLES,
        LONG_PROF_COMPOSE,
        LONG_PROF_OBJECT,
        LONG_PROF_PROFUNCTOR,
        LONG_PROF_REPORT,
        LONG_PROF_TABLES,
        NODE_COLUMNS,
        NODE_DIGEST_COLUMNS,
        NODE_TEXT_HASH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        SQUARE_COLUMNS,
        SQUARE_DIGEST_COLUMNS,
        SQUARE_TEXT_HASH,
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
    from derive_long_univ import (
        ARROW_COLUMNS,
        ARROW_DIGEST_COLUMNS,
        ARROW_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LAW_COLUMNS,
        LAW_DIGEST_COLUMNS,
        LAW_TEXT_HASH,
        LONG_CLS_MEAN,
        LONG_CLS_MOMENT,
        LONG_CLS_REPORT,
        LONG_CLS_SHRINK,
        LONG_CLS_TABLES,
        LONG_CLS_TAIL,
        LONG_CONV_MARGINAL,
        LONG_CONV_REPORT,
        LONG_CONV_TABLES,
        LONG_LLN_REPORT,
        LONG_MARKOV_REPORT,
        LONG_MARKOV_STATIONARY,
        LONG_MARKOV_TABLES,
        LONG_PROF_COMPOSE,
        LONG_PROF_OBJECT,
        LONG_PROF_PROFUNCTOR,
        LONG_PROF_REPORT,
        LONG_PROF_TABLES,
        NODE_COLUMNS,
        NODE_DIGEST_COLUMNS,
        NODE_TEXT_HASH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        SQUARE_COLUMNS,
        SQUARE_DIGEST_COLUMNS,
        SQUARE_TEXT_HASH,
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


def validate_long_univ() -> dict[str, Any]:
    expected = build_payloads()
    univ = load_json(OUT_DIR / "univ.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if univ != expected["univ"]:
        raise AssertionError("long_univ univ JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_univ cert mismatch")
    for filename, key in {
        "node.csv": "node_csv",
        "arrow.csv": "arrow_csv",
        "square.csv": "square_csv",
        "law.csv": "law_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_univ {filename} mismatch")

    for key, expected_array in {
        "node_table": expected["node_table"],
        "arrow_table": expected["arrow_table"],
        "square_table": expected["square_table"],
        "law_table": expected["law_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_univ table mismatch: {key}")

    if report.get("schema") != "long.univ.report@1":
        raise AssertionError("long_univ report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_univ report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_univ all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_univ checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_univ report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_univ report hash mismatch")

    csv_shapes = [
        ("node.csv", NODE_COLUMNS, 15),
        ("arrow.csv", ARROW_COLUMNS, 10),
        ("square.csv", SQUARE_COLUMNS, 6),
        ("law.csv", LAW_COLUMNS, 306),
    ]
    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_univ {filename} shape mismatch")

    table_shapes = {
        "node_table": (15, len(NODE_DIGEST_COLUMNS)),
        "arrow_table": (10, len(ARROW_DIGEST_COLUMNS)),
        "square_table": (6, len(SQUARE_DIGEST_COLUMNS)),
        "law_table": (306, len(LAW_DIGEST_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_univ {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "node_count": 15,
        "arrow_count": 10,
        "square_count": 6,
        "law_count": 306,
        "law_equal_count": 306,
        "law_violation_count": 0,
        "node_address_total": 972_056,
        "arrow_positive_entry_total": 971_407,
        "prof_conv_law_count": 80,
        "prof_conv_equal_count": 80,
        "stationary_law_count": 3,
        "stationary_equal_count": 3,
        "mean_law_count": 16,
        "mean_equal_count": 16,
        "moment_law_count": 48,
        "moment_equal_count": 48,
        "tail_law_count": 144,
        "tail_equal_count": 144,
        "shrink_law_count": 15,
        "shrink_equal_count": 15,
        "law_num_digit_max": 3_940,
        "law_den_digit_max": 3_941,
        "long_lln_input_certified": 1,
        "long_prof_input_certified": 1,
        "long_conv_input_certified": 1,
        "long_cls_input_certified": 1,
        "long_markov_input_certified": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_univ observable {key} mismatch")

    if hashlib.sha256(
        digest_text(NODE_COLUMNS, csv_rows["node.csv"]).encode("ascii")
    ).hexdigest() != NODE_TEXT_HASH:
        raise AssertionError("long_univ node hash mismatch")
    if hashlib.sha256(
        digest_text(ARROW_COLUMNS, csv_rows["arrow.csv"]).encode("ascii")
    ).hexdigest() != ARROW_TEXT_HASH:
        raise AssertionError("long_univ arrow hash mismatch")
    if hashlib.sha256(
        digest_text(SQUARE_COLUMNS, csv_rows["square.csv"]).encode("ascii")
    ).hexdigest() != SQUARE_TEXT_HASH:
        raise AssertionError("long_univ square hash mismatch")
    if hashlib.sha256(
        digest_text(LAW_COLUMNS, csv_rows["law.csv"]).encode("ascii")
    ).hexdigest() != LAW_TEXT_HASH:
        raise AssertionError("long_univ law hash mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_lln_report": LONG_LLN_REPORT,
        "long_prof_report": LONG_PROF_REPORT,
        "long_prof_object": LONG_PROF_OBJECT,
        "long_prof_profunctor": LONG_PROF_PROFUNCTOR,
        "long_prof_compose": LONG_PROF_COMPOSE,
        "long_prof_tables": LONG_PROF_TABLES,
        "long_conv_report": LONG_CONV_REPORT,
        "long_conv_marginal": LONG_CONV_MARGINAL,
        "long_conv_tables": LONG_CONV_TABLES,
        "long_cls_report": LONG_CLS_REPORT,
        "long_cls_mean": LONG_CLS_MEAN,
        "long_cls_moment": LONG_CLS_MOMENT,
        "long_cls_tail": LONG_CLS_TAIL,
        "long_cls_shrink": LONG_CLS_SHRINK,
        "long_cls_tables": LONG_CLS_TABLES,
        "long_markov_report": LONG_MARKOV_REPORT,
        "long_markov_stationary": LONG_MARKOV_STATIONARY,
        "long_markov_tables": LONG_MARKOV_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.univ.manifest@1":
        raise AssertionError("long_univ manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_univ manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_univ manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_univ missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_univ index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("long_univ index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.univ.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": {
            "nodes": witness.get("nodes"),
            "arrows": witness.get("arrows"),
            "commuting_squares": witness.get("commuting_squares"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_univ(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
