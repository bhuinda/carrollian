from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_cls import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_CONV_MARGINAL,
        LONG_CONV_REPORT,
        LONG_CONV_TABLES,
        LONG_MARKOV_MEAN_VARIANCE,
        LONG_MARKOV_REPORT,
        LONG_MARKOV_TABLES,
        MEAN_COLUMNS,
        MEAN_DIGEST_COLUMNS,
        MEAN_TEXT_HASH,
        MOMENT_COLUMNS,
        MOMENT_DIGEST_COLUMNS,
        MOMENT_TEXT_HASH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        SHRINK_COLUMNS,
        SHRINK_DIGEST_COLUMNS,
        SHRINK_TEXT_HASH,
        STATUS,
        TAIL_COLUMNS,
        TAIL_DIGEST_COLUMNS,
        TAIL_TEXT_HASH,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        mean_text,
        moment_text,
        rows_from_table,
        self_hash,
        shrink_text,
        tail_text,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_cls import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_CONV_MARGINAL,
        LONG_CONV_REPORT,
        LONG_CONV_TABLES,
        LONG_MARKOV_MEAN_VARIANCE,
        LONG_MARKOV_REPORT,
        LONG_MARKOV_TABLES,
        MEAN_COLUMNS,
        MEAN_DIGEST_COLUMNS,
        MEAN_TEXT_HASH,
        MOMENT_COLUMNS,
        MOMENT_DIGEST_COLUMNS,
        MOMENT_TEXT_HASH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        SHRINK_COLUMNS,
        SHRINK_DIGEST_COLUMNS,
        SHRINK_TEXT_HASH,
        STATUS,
        TAIL_COLUMNS,
        TAIL_DIGEST_COLUMNS,
        TAIL_TEXT_HASH,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        mean_text,
        moment_text,
        rows_from_table,
        self_hash,
        shrink_text,
        tail_text,
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


def validate_long_cls() -> dict[str, Any]:
    expected = build_payloads()
    cls = load_json(OUT_DIR / "cls.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if cls != expected["cls"]:
        raise AssertionError("long_cls cls JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_cls cert mismatch")
    for filename, key in {
        "mean.csv": "mean_csv",
        "moment.csv": "moment_csv",
        "tail.csv": "tail_csv",
        "shrink.csv": "shrink_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_cls {filename} mismatch")

    for key, expected_array in {
        "mean_table": expected["mean_table"],
        "moment_table": expected["moment_table"],
        "tail_table": expected["tail_table"],
        "shrink_table": expected["shrink_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_cls table mismatch: {key}")

    if report.get("schema") != "long.cls.report@1":
        raise AssertionError("long_cls report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_cls report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_cls all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_cls checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_cls report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_cls report hash mismatch")

    csv_shapes = [
        ("mean.csv", MEAN_COLUMNS, 16),
        ("moment.csv", MOMENT_COLUMNS, 48),
        ("tail.csv", TAIL_COLUMNS, 48),
        ("shrink.csv", SHRINK_COLUMNS, 15),
    ]
    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_cls {filename} shape mismatch")

    table_shapes = {
        "mean_table": (16, len(MEAN_DIGEST_COLUMNS)),
        "moment_table": (48, len(MOMENT_DIGEST_COLUMNS)),
        "tail_table": (48, len(TAIL_DIGEST_COLUMNS)),
        "shrink_table": (15, len(SHRINK_DIGEST_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_cls {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "horizon": 16,
        "epsilon_count": 3,
        "mean_row_count": 16,
        "mean_match_count": 16,
        "mean_num_digit_max": 4,
        "mean_den_digit_max": 4,
        "centered_moment_row_count": 48,
        "variance_markov_match_count": 8,
        "order2_nonnegative_count": 16,
        "order4_nonnegative_count": 16,
        "moment_num_digit_max": 3_940,
        "moment_den_digit_max": 3_941,
        "tail_row_count": 48,
        "tail_gap_nonnegative_count": 48,
        "tail_num_digit_max": 3_934,
        "tail_den_digit_max": 3_934,
        "shrink_row_count": 15,
        "shrink_nonnegative_count": 15,
        "shrink_num_digit_max": 3_933,
        "shrink_den_digit_max": 3_933,
        "long_conv_input_certified": 1,
        "long_markov_input_certified": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_cls observable {key} mismatch")

    if hashlib.sha256(
        mean_text(csv_rows["mean.csv"]).encode("ascii")
    ).hexdigest() != MEAN_TEXT_HASH:
        raise AssertionError("long_cls mean hash mismatch")
    if hashlib.sha256(
        moment_text(csv_rows["moment.csv"]).encode("ascii")
    ).hexdigest() != MOMENT_TEXT_HASH:
        raise AssertionError("long_cls moment hash mismatch")
    if hashlib.sha256(
        tail_text(csv_rows["tail.csv"]).encode("ascii")
    ).hexdigest() != TAIL_TEXT_HASH:
        raise AssertionError("long_cls tail hash mismatch")
    if hashlib.sha256(
        shrink_text(csv_rows["shrink.csv"]).encode("ascii")
    ).hexdigest() != SHRINK_TEXT_HASH:
        raise AssertionError("long_cls shrink hash mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_conv_report": LONG_CONV_REPORT,
        "long_conv_marginal": LONG_CONV_MARGINAL,
        "long_conv_tables": LONG_CONV_TABLES,
        "long_markov_report": LONG_MARKOV_REPORT,
        "long_markov_mean_variance": LONG_MARKOV_MEAN_VARIANCE,
        "long_markov_tables": LONG_MARKOV_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.cls.manifest@1":
        raise AssertionError("long_cls manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_cls manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_cls manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_cls missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_cls index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("long_cls index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.cls.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": {
            "means": witness.get("means"),
            "centered_moments": witness.get("centered_moments"),
            "chebyshev_tails": witness.get("chebyshev_tails"),
            "variance_shrink": witness.get("variance_shrink"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_cls(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
