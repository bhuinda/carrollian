from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_dev import (
        CHERNOFF_COLUMNS,
        CHERNOFF_DIGEST_COLUMNS,
        DERIVE_SCRIPT,
        DISTRIBUTION_COLUMNS,
        DISTRIBUTION_DIGEST_COLUMNS,
        INDEX_PATH,
        LONG_MARKOV_KERNEL,
        LONG_MARKOV_REPORT,
        LONG_MARKOV_STATIONARY,
        LONG_MARKOV_TABLES,
        MOMENT_COLUMNS,
        MOMENT_DIGEST_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        TAIL_COLUMNS,
        TAIL_DIGEST_COLUMNS,
        THEOREM_ID,
        TILT_COLUMNS,
        TILT_DIGEST_COLUMNS,
        VALIDATOR_SCRIPT,
        STATUS,
        build_payloads,
        chernoff_fraction_text,
        distribution_fraction_text,
        moment_fraction_text,
        rows_from_table,
        self_hash,
        tail_fraction_text,
        tilt_fraction_text,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_dev import (
        CHERNOFF_COLUMNS,
        CHERNOFF_DIGEST_COLUMNS,
        DERIVE_SCRIPT,
        DISTRIBUTION_COLUMNS,
        DISTRIBUTION_DIGEST_COLUMNS,
        INDEX_PATH,
        LONG_MARKOV_KERNEL,
        LONG_MARKOV_REPORT,
        LONG_MARKOV_STATIONARY,
        LONG_MARKOV_TABLES,
        MOMENT_COLUMNS,
        MOMENT_DIGEST_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        TAIL_COLUMNS,
        TAIL_DIGEST_COLUMNS,
        THEOREM_ID,
        TILT_COLUMNS,
        TILT_DIGEST_COLUMNS,
        VALIDATOR_SCRIPT,
        STATUS,
        build_payloads,
        chernoff_fraction_text,
        distribution_fraction_text,
        moment_fraction_text,
        rows_from_table,
        self_hash,
        tail_fraction_text,
        tilt_fraction_text,
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


def validate_long_dev() -> dict[str, Any]:
    expected = build_payloads()
    dev = load_json(OUT_DIR / "dev.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if dev != expected["dev"]:
        raise AssertionError("long_dev dev JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_dev cert mismatch")
    for filename, key in {
        "distribution.csv": "distribution_csv",
        "moment.csv": "moment_csv",
        "tilt.csv": "tilt_csv",
        "tail.csv": "tail_csv",
        "chernoff.csv": "chernoff_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_dev {filename} mismatch")

    for key, expected_array in {
        "distribution_digest_table": expected["distribution_digest_table"],
        "moment_digest_table": expected["moment_digest_table"],
        "tilt_digest_table": expected["tilt_digest_table"],
        "tail_digest_table": expected["tail_digest_table"],
        "chernoff_digest_table": expected["chernoff_digest_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_dev table mismatch: {key}")

    if report.get("schema") != "long.dev.report@1":
        raise AssertionError("long_dev report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_dev report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_dev all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_dev checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_dev report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_dev report hash mismatch")

    csv_shapes = [
        ("distribution.csv", DISTRIBUTION_COLUMNS, 80),
        ("moment.csv", MOMENT_COLUMNS, 32),
        ("tilt.csv", TILT_COLUMNS, 24),
        ("tail.csv", TAIL_COLUMNS, 16),
        ("chernoff.csv", CHERNOFF_COLUMNS, 16),
    ]
    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_dev {filename} shape mismatch")

    table_shapes = {
        "distribution_digest_table": (80, len(DISTRIBUTION_DIGEST_COLUMNS)),
        "moment_digest_table": (32, len(MOMENT_DIGEST_COLUMNS)),
        "tilt_digest_table": (24, len(TILT_DIGEST_COLUMNS)),
        "tail_digest_table": (16, len(TAIL_DIGEST_COLUMNS)),
        "chernoff_digest_table": (16, len(CHERNOFF_DIGEST_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_dev {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "line_point_count": 985,
        "component_count": 3,
        "component_value_min": 0,
        "component_value_max": 2,
        "sample_horizon": 8,
        "moment_order_max": 4,
        "distribution_row_count": 80,
        "distribution_sum_one_flag": 1,
        "distribution_full_support_flag": 1,
        "distribution_prob_num_digit_max": 1_819,
        "distribution_prob_den_digit_max": 1_820,
        "moment_row_count": 32,
        "first_moment_linear_flag": 1,
        "moment_num_digit_max": 1_835,
        "moment_den_digit_max": 1_831,
        "tilt_row_count": 24,
        "tilt_count": 3,
        "tilt_num_digit_max": 1_835,
        "tilt_den_digit_max": 1_833,
        "tail_row_count": 16,
        "tail_num_digit_max": 1_814,
        "tail_den_digit_max": 1_814,
        "chernoff_row_count": 16,
        "chernoff_gap_nonnegative_flag": 1,
        "chernoff_bound_num_digit_max": 1_835,
        "chernoff_bound_den_digit_max": 1_834,
        "chernoff_gap_num_digit_max": 1_835,
        "chernoff_gap_den_digit_max": 1_834,
        "long_markov_input_certified": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_dev observable {key} mismatch")

    if hashlib.sha256(
        distribution_fraction_text(csv_rows["distribution.csv"]).encode("ascii")
    ).hexdigest() != (
        "9298c8d0100769d65e0432c21d09c37e48ddb718475d5f532bfc65e81ff5b66e"
    ):
        raise AssertionError("long_dev distribution hash mismatch")
    if hashlib.sha256(
        moment_fraction_text(csv_rows["moment.csv"]).encode("ascii")
    ).hexdigest() != (
        "3a6e0b3831d10559fe27508ca1196a53b72d10d9e2f2e38999eff837a77c0838"
    ):
        raise AssertionError("long_dev moment hash mismatch")
    if hashlib.sha256(
        tilt_fraction_text(csv_rows["tilt.csv"]).encode("ascii")
    ).hexdigest() != (
        "7513e77f2b3601a7d26b3cb3d0dea1131f4836975e811225354b02b8b86639ce"
    ):
        raise AssertionError("long_dev tilt hash mismatch")
    if hashlib.sha256(
        tail_fraction_text(csv_rows["tail.csv"]).encode("ascii")
    ).hexdigest() != (
        "4002870068ef1f0f5989e4765524800e536cdd1b76b55fc6626e4e4bc4487bfb"
    ):
        raise AssertionError("long_dev tail hash mismatch")
    if hashlib.sha256(
        chernoff_fraction_text(csv_rows["chernoff.csv"]).encode("ascii")
    ).hexdigest() != (
        "d74e1e0c3c973175017decb4e79577445b85fec2f745aa4667994ac2328c3550"
    ):
        raise AssertionError("long_dev chernoff hash mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_markov_report": LONG_MARKOV_REPORT,
        "long_markov_kernel": LONG_MARKOV_KERNEL,
        "long_markov_stationary": LONG_MARKOV_STATIONARY,
        "long_markov_tables": LONG_MARKOV_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.dev.manifest@1":
        raise AssertionError("long_dev manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_dev manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_dev manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_dev missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_dev index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("long_dev index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.dev.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": {
            "distribution": witness.get("distribution"),
            "moments": witness.get("moments"),
            "tilts": witness.get("tilts"),
            "tails": witness.get("tails"),
            "chernoff": witness.get("chernoff"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_dev(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
