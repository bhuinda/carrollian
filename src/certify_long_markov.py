from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_markov import (
        COVARIANCE_COLUMNS,
        COVARIANCE_DIGEST_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        KERNEL_COLUMNS,
        KERNEL_DIGEST_COLUMNS,
        LONG_ABSORB_MATRIX,
        LONG_SPEC_REPORT,
        LONG_SPEC_TABLES,
        MEAN_VARIANCE_COLUMNS,
        MEAN_VARIANCE_DIGEST_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        POWER_DIGEST_COLUMNS,
        SPECTRAL_COLUMNS,
        SPECTRAL_DIGEST_COLUMNS,
        STATIONARY_COLUMNS,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        covariance_fraction_text,
        detailed_balance_text,
        kernel_fraction_text,
        mean_variance_fraction_text,
        power_digest_text,
        rows_from_table,
        self_hash,
        spectral_fraction_text,
        stationary_fraction_text,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_markov import (
        COVARIANCE_COLUMNS,
        COVARIANCE_DIGEST_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        KERNEL_COLUMNS,
        KERNEL_DIGEST_COLUMNS,
        LONG_ABSORB_MATRIX,
        LONG_SPEC_REPORT,
        LONG_SPEC_TABLES,
        MEAN_VARIANCE_COLUMNS,
        MEAN_VARIANCE_DIGEST_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        POWER_DIGEST_COLUMNS,
        SPECTRAL_COLUMNS,
        SPECTRAL_DIGEST_COLUMNS,
        STATIONARY_COLUMNS,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        covariance_fraction_text,
        detailed_balance_text,
        kernel_fraction_text,
        mean_variance_fraction_text,
        power_digest_text,
        rows_from_table,
        self_hash,
        spectral_fraction_text,
        stationary_fraction_text,
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
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def validate_long_markov() -> dict[str, Any]:
    expected = build_payloads()
    markov = load_json(OUT_DIR / "markov.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if markov != expected["markov"]:
        raise AssertionError("long_markov markov JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_markov cert mismatch")
    for filename, key in {
        "kernel.csv": "kernel_csv",
        "stationary.csv": "stationary_csv",
        "spectral.csv": "spectral_csv",
        "power.csv": "power_csv",
        "covariance.csv": "covariance_csv",
        "mean_variance.csv": "mean_variance_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_markov {filename} mismatch")

    for key, expected_array in {
        "kernel_digest_table": expected["kernel_digest_table"],
        "stationary_digest_table": expected["stationary_digest_table"],
        "spectral_digest_table": expected["spectral_digest_table"],
        "power_digest_table": expected["power_digest_table"],
        "covariance_digest_table": expected["covariance_digest_table"],
        "mean_variance_digest_table": expected["mean_variance_digest_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_markov table mismatch: {key}")

    if report.get("schema") != "long.markov.report@1":
        raise AssertionError("long_markov report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_markov report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_markov all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_markov checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_markov report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_markov report hash mismatch")

    csv_shapes = [
        ("kernel.csv", KERNEL_COLUMNS, 9),
        ("stationary.csv", STATIONARY_COLUMNS, 3),
        ("spectral.csv", SPECTRAL_COLUMNS, 6),
        ("power.csv", POWER_DIGEST_COLUMNS, 81),
        ("covariance.csv", COVARIANCE_COLUMNS, 9),
        ("mean_variance.csv", MEAN_VARIANCE_COLUMNS, 8),
    ]
    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_markov {filename} shape mismatch")

    table_shapes = {
        "kernel_digest_table": (9, len(KERNEL_DIGEST_COLUMNS)),
        "stationary_digest_table": (3, len(STATIONARY_COLUMNS) - 1),
        "spectral_digest_table": (6, len(SPECTRAL_DIGEST_COLUMNS)),
        "power_digest_table": (81, len(POWER_DIGEST_COLUMNS)),
        "covariance_digest_table": (9, len(COVARIANCE_DIGEST_COLUMNS)),
        "mean_variance_digest_table": (8, len(MEAN_VARIANCE_DIGEST_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_markov {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "line_point_count": 985,
        "component_count": 3,
        "boundary0_count": 1_342,
        "boundary1_count": 864,
        "boundary2_count": 2_378,
        "boundary_total_count": 4_584,
        "kernel_entry_count": 9,
        "kernel_positive_entry_count": 9,
        "kernel_row_sum_one_flag": 1,
        "stationary_entry_count": 3,
        "stationary_sum_one_flag": 1,
        "stationary_fixed_flag": 1,
        "detailed_balance_flag": 1,
        "power_horizon": 8,
        "power_digest_entry_count": 81,
        "power_row_sum_violation_count": 0,
        "power_stationary_fixed_violation_count": 0,
        "spectral_invariant_count": 6,
        "nontrivial_discriminant_num_digits": 524,
        "nontrivial_discriminant_den_digits": 525,
        "nontrivial_discriminant_num_mod_1000000007": 848_692_485,
        "nontrivial_discriminant_den_mod_1000000007": 526_418_076,
        "nontrivial_discriminant_positive_flag": 1,
        "nontrivial_discriminant_rational_square_flag": 0,
        "stationary_mean_num_digits": 4,
        "stationary_mean_den_digits": 4,
        "stationary_mean_num_mod_1000000007": 1_405,
        "stationary_mean_den_mod_1000000007": 1_146,
        "stationary_variance_num_digits": 6,
        "stationary_variance_den_digits": 7,
        "stationary_variance_num_mod_1000000007": 998_699,
        "stationary_variance_den_mod_1000000007": 1_313_316,
        "autocovariance_count": 9,
        "mean_variance_count": 8,
        "mean_variance_monotone_decrease_flag": 1,
        "mean_variance_first_matches_stationary_flag": 1,
        "long_spec_input_certified": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_markov observable {key} mismatch")

    if hashlib.sha256(
        kernel_fraction_text(csv_rows["kernel.csv"]).encode("ascii")
    ).hexdigest() != (
        "1de86eb4c03287b20e03ad6d38170e08a3398b721ba281a6f8fa61982e83b552"
    ):
        raise AssertionError("long_markov kernel hash mismatch")
    if hashlib.sha256(
        stationary_fraction_text(csv_rows["stationary.csv"]).encode("ascii")
    ).hexdigest() != (
        "67c0cd6ff0bca3e0575d0136033240098abb705bdeb93812783853f7a20695d2"
    ):
        raise AssertionError("long_markov stationary hash mismatch")
    if report["witness"]["stationary"].get("detailed_balance_text_sha256") != (
        "f2cb23a2c33352d0dc40163ff7a1fd241d6ab10668971a0b20cdd6e4d5974899"
    ):
        raise AssertionError("long_markov detailed balance hash mismatch")
    if hashlib.sha256(
        spectral_fraction_text(csv_rows["spectral.csv"]).encode("ascii")
    ).hexdigest() != (
        "0d0f56de3fa6c48d111c5af6d85589ad17077cc97130028390cdb9fd9848a0f7"
    ):
        raise AssertionError("long_markov spectral hash mismatch")
    if hashlib.sha256(
        power_digest_text(
            [
                {column: int(row[column]) for column in POWER_DIGEST_COLUMNS}
                for row in csv_rows["power.csv"]
            ]
        ).encode("ascii")
    ).hexdigest() != (
        "c3e77932668eb5f83979c6b805f9d456450d02cdceb7a1bd335684633f1aeee6"
    ):
        raise AssertionError("long_markov power hash mismatch")
    if hashlib.sha256(
        covariance_fraction_text(csv_rows["covariance.csv"]).encode("ascii")
    ).hexdigest() != (
        "d9e86f019666d3161c71d69f7c277320bd6782a0771a58bde1922dd5b3ae723a"
    ):
        raise AssertionError("long_markov covariance hash mismatch")
    if hashlib.sha256(
        mean_variance_fraction_text(csv_rows["mean_variance.csv"]).encode("ascii")
    ).hexdigest() != (
        "46d3daf5ecb3caf90f29834f98afe7c7a2e90997e68a56ca936bbc47a0e3be47"
    ):
        raise AssertionError("long_markov mean variance hash mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_spec_report": LONG_SPEC_REPORT,
        "long_spec_tables": LONG_SPEC_TABLES,
        "long_absorb_matrix": LONG_ABSORB_MATRIX,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.markov.manifest@1":
        raise AssertionError("long_markov manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_markov manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_markov manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_markov missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_markov index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("long_markov index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.markov.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": {
            "kernel": witness.get("kernel"),
            "stationary": witness.get("stationary"),
            "spectrum": witness.get("spectrum"),
            "powers": witness.get("powers"),
            "finite_lln": witness.get("finite_lln"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_markov(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
