from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_conv import (
        CONTINUATION_COLUMNS,
        CONTINUATION_TEXT_HASH,
        CONV_COLUMNS,
        CONV_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_MARKOV_KERNEL,
        LONG_MARKOV_REPORT,
        LONG_MARKOV_STATIONARY,
        LONG_PROF_COMPOSE,
        LONG_PROF_REPORT,
        LONG_PROF_TABLES,
        LONG_RATE_REPORT,
        LONG_RATE_TABLES,
        MARGINAL_COLUMNS,
        MARGINAL_DIGEST_COLUMNS,
        MARGINAL_TEXT_HASH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATE_COLUMNS,
        STATE_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        continuation_text,
        conv_text,
        marginal_text,
        rows_from_table,
        self_hash,
        state_text,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_conv import (
        CONTINUATION_COLUMNS,
        CONTINUATION_TEXT_HASH,
        CONV_COLUMNS,
        CONV_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_MARKOV_KERNEL,
        LONG_MARKOV_REPORT,
        LONG_MARKOV_STATIONARY,
        LONG_PROF_COMPOSE,
        LONG_PROF_REPORT,
        LONG_PROF_TABLES,
        LONG_RATE_REPORT,
        LONG_RATE_TABLES,
        MARGINAL_COLUMNS,
        MARGINAL_DIGEST_COLUMNS,
        MARGINAL_TEXT_HASH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATE_COLUMNS,
        STATE_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        continuation_text,
        conv_text,
        marginal_text,
        rows_from_table,
        self_hash,
        state_text,
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


def validate_long_conv() -> dict[str, Any]:
    expected = build_payloads()
    conv = load_json(OUT_DIR / "conv.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if conv != expected["conv"]:
        raise AssertionError("long_conv conv JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_conv cert mismatch")
    for filename, key in {
        "state.csv": "state_csv",
        "continuation.csv": "continuation_csv",
        "marginal.csv": "marginal_csv",
        "convolution.csv": "convolution_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_conv {filename} mismatch")

    for key, expected_array in {
        "state_table": expected["state_table"],
        "continuation_table": expected["continuation_table"],
        "marginal_table": expected["marginal_table"],
        "convolution_table": expected["convolution_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_conv table mismatch: {key}")

    if report.get("schema") != "long.conv.report@1":
        raise AssertionError("long_conv report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_conv report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_conv all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_conv checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_conv report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_conv report hash mismatch")

    csv_shapes = [
        ("state.csv", STATE_COLUMNS, 864),
        ("continuation.csv", CONTINUATION_COLUMNS, 729),
        ("marginal.csv", MARGINAL_COLUMNS, 288),
        ("convolution.csv", CONV_COLUMNS, 3_648),
    ]
    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_conv {filename} shape mismatch")

    table_shapes = {
        "state_table": (864, len(STATE_COLUMNS)),
        "continuation_table": (729, len(CONTINUATION_COLUMNS)),
        "marginal_table": (288, len(MARGINAL_DIGEST_COLUMNS)),
        "convolution_table": (3_648, len(CONV_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_conv {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "state_horizon": 16,
        "split_horizon": 8,
        "state_row_count": 864,
        "state_positive_count": 768,
        "state_mass_one_count": 16,
        "state_num_digit_max": 3_890,
        "state_den_digit_max": 3_892,
        "continuation_row_count": 729,
        "continuation_positive_count": 579,
        "continuation_row_sum_one_count": 27,
        "continuation_num_digit_max": 2_070,
        "continuation_den_digit_max": 2_071,
        "marginal_row_count": 288,
        "marginal_positive_count": 288,
        "marginal_sum_one_count": 16,
        "marginal_prof_match_count": 80,
        "marginal_num_digit_max": 3_893,
        "marginal_den_digit_max": 3_895,
        "convolution_row_count": 3_648,
        "convolution_equal_count": 3_648,
        "convolution_violation_count": 0,
        "convolution_num_digit_max": 3_890,
        "convolution_den_digit_max": 3_892,
        "long_markov_input_certified": 1,
        "long_prof_input_certified": 1,
        "long_rate_input_certified": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_conv observable {key} mismatch")

    if hashlib.sha256(state_text(csv_rows["state.csv"]).encode("ascii")).hexdigest() != STATE_TEXT_HASH:
        raise AssertionError("long_conv state hash mismatch")
    if hashlib.sha256(
        continuation_text(csv_rows["continuation.csv"]).encode("ascii")
    ).hexdigest() != CONTINUATION_TEXT_HASH:
        raise AssertionError("long_conv continuation hash mismatch")
    if hashlib.sha256(
        marginal_text(csv_rows["marginal.csv"]).encode("ascii")
    ).hexdigest() != MARGINAL_TEXT_HASH:
        raise AssertionError("long_conv marginal hash mismatch")
    if hashlib.sha256(
        conv_text(csv_rows["convolution.csv"]).encode("ascii")
    ).hexdigest() != CONV_TEXT_HASH:
        raise AssertionError("long_conv convolution hash mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_markov_report": LONG_MARKOV_REPORT,
        "long_markov_kernel": LONG_MARKOV_KERNEL,
        "long_markov_stationary": LONG_MARKOV_STATIONARY,
        "long_prof_report": LONG_PROF_REPORT,
        "long_prof_compose": LONG_PROF_COMPOSE,
        "long_prof_tables": LONG_PROF_TABLES,
        "long_rate_report": LONG_RATE_REPORT,
        "long_rate_tables": LONG_RATE_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.conv.manifest@1":
        raise AssertionError("long_conv manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_conv manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_conv manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_conv missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_conv index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("long_conv index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.conv.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": {
            "state_laws": witness.get("state_laws"),
            "continuation_laws": witness.get("continuation_laws"),
            "marginals": witness.get("marginals"),
            "convolution": witness.get("convolution"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_conv(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
