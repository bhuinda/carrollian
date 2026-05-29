from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_cut import (
        CUT_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_LAP_REPORT,
        LONG_LAP_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PAIR_COLUMNS,
        PAIR_DIGEST_COLUMNS,
        RES_COMPONENT_COLUMNS,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_cut import (
        CUT_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_LAP_REPORT,
        LONG_LAP_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PAIR_COLUMNS,
        PAIR_DIGEST_COLUMNS,
        RES_COMPONENT_COLUMNS,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
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
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def table_rows(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def validate_long_cut() -> dict[str, Any]:
    expected = build_payloads()
    cut = load_json(OUT_DIR / "cut.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if cut != expected["cut"]:
        raise AssertionError("long_cut cut JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_cut cert mismatch")
    for filename, key in {
        "cut.csv": "cut_csv",
        "res_component.csv": "res_component_csv",
        "pair.csv": "pair_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_cut {filename} mismatch")

    for key, expected_array in {
        "cut_table": expected["cut_table"],
        "res_component_table": expected["res_component_table"],
        "pair_digest_table": expected["pair_digest_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_cut table mismatch: {key}")

    if report.get("schema") != "long.cut.report@1":
        raise AssertionError("long_cut report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_cut report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_cut all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_cut checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_cut report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_cut report hash mismatch")

    cut_header, cut_rows = read_csv(OUT_DIR / "cut.csv")
    res_header, res_rows = read_csv(OUT_DIR / "res_component.csv")
    pair_header, pair_rows = read_csv(OUT_DIR / "pair.csv")
    if cut_header != CUT_COLUMNS or len(cut_rows) != 3:
        raise AssertionError("long_cut cut CSV shape mismatch")
    if res_header != RES_COMPONENT_COLUMNS or len(res_rows) != 3:
        raise AssertionError("long_cut resistance component CSV shape mismatch")
    if pair_header != PAIR_COLUMNS or len(pair_rows) != 664:
        raise AssertionError("long_cut pair CSV shape mismatch")
    if np.asarray(tables["pair_digest_table"]).shape != (664, len(PAIR_DIGEST_COLUMNS)):
        raise AssertionError("long_cut pair digest table shape mismatch")
    pair_text = (OUT_DIR / "pair.csv").read_text(encoding="utf-8")
    if hashlib.sha256(pair_text.encode("utf-8")).hexdigest() != (
        "ca8e79cb1408dbcd1953dd482d29500b66a451d2bfa6b1a0649a4c03aca54bcc"
    ):
        raise AssertionError("long_cut pair CSV sha256 mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "line_point_count": 985,
        "active_owner_count": 51,
        "component_count": 3,
        "active_pair_count": 1275,
        "finite_resistance_pair_count": 664,
        "infinite_resistance_pair_count": 611,
        "active_internal_min_cut": 0,
        "connected_component_min_cut": 2,
        "component_external_positive_count": 3,
        "external_degree_min": 0,
        "external_degree_max": 1003,
        "external_degree_zero_count": 14,
        "external_degree_sum": 4584,
        "finite_resistance_min_num": 1,
        "finite_resistance_min_den": 733,
        "finite_resistance_max_num_digits": 32,
        "finite_resistance_max_den_digits": 32,
        "finite_resistance_sum_num_digits": 57,
        "finite_resistance_sum_den_digits": 54,
        "finite_resistance_sum_num_mod_1000000007": 818_911_361,
        "finite_resistance_sum_den_mod_1000000007": 398_565_772,
        "finite_kirchhoff_num_digits": 57,
        "finite_kirchhoff_den_digits": 53,
        "finite_kirchhoff_num_mod_1000000007": 20_321_197,
        "finite_kirchhoff_den_mod_1000000007": 36_233_252,
        "long_lap_rank": 48,
        "long_lap_nullity": 3,
        "long_lap_input_certified": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_cut observable {key} mismatch")

    cut_table = np.asarray(tables["cut_table"])
    expected_cut_rows = [
        [0, 33, 61, 2, 1, 32, 138, 19_044, 1_342, 3_024, 671, 1_512],
        [1, 1, 0, 0, 1, 0, 7, 49, 864, 864, 1, 1],
        [2, 17, 30, 2, 1, 16, 174, 30_276, 2_378, 11_954, 1_189, 5_977],
    ]
    if cut_table.tolist() != expected_cut_rows:
        raise AssertionError("long_cut cut table fingerprint mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_lap_report": LONG_LAP_REPORT,
        "long_lap_tables": LONG_LAP_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.cut.manifest@1":
        raise AssertionError("long_cut manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_cut manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_cut manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_cut missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_cut index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("long_cut index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.cut.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": {
            "cut": {
                "active_internal_min_cut": witness.get("cut", {}).get(
                    "active_internal_min_cut"
                ),
                "connected_component_min_cut": witness.get("cut", {}).get(
                    "connected_component_min_cut"
                ),
                "component_external_positive_count": witness.get("cut", {}).get(
                    "component_external_positive_count"
                ),
            },
            "resistance": {
                "active_pair_count": witness.get("resistance", {}).get(
                    "active_pair_count"
                ),
                "finite_pair_count": witness.get("resistance", {}).get(
                    "finite_pair_count"
                ),
                "infinite_pair_count": witness.get("resistance", {}).get(
                    "infinite_pair_count"
                ),
                "finite_summary": witness.get("resistance", {}).get(
                    "finite_summary"
                ),
            },
            "external_degree": witness.get("external_degree"),
            "lap_context": witness.get("lap_context"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_cut(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
