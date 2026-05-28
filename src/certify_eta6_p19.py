from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_eta6_p19 import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        P5_REPORT,
        P5_TABLES,
        P15_REPORT,
        P17_REPORT,
        STATUS,
        THEOREM_ID,
        TOP_COLUMNS,
        TOP_N,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_eta6_p19 import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        P5_REPORT,
        P5_TABLES,
        P15_REPORT,
        P17_REPORT,
        STATUS,
        THEOREM_ID,
        TOP_COLUMNS,
        TOP_N,
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


def table_rows(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def validate_eta6_p19() -> dict[str, Any]:
    expected = build_payloads()
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    p19 = load_json(OUT_DIR / "p19.json")
    cert = load_json(OUT_DIR / "cert.json")
    top_csv = (OUT_DIR / "top.csv").read_text(encoding="utf-8")
    obs_csv = (OUT_DIR / "obs.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    index = load_json(INDEX_PATH)

    if p19 != expected["p19"]:
        raise AssertionError("eta6_p19 JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("eta6_p19 cert mismatch")
    if top_csv != expected["top_csv"]:
        raise AssertionError("eta6_p19 top CSV mismatch")
    if obs_csv != expected["obs_csv"]:
        raise AssertionError("eta6_p19 obs CSV mismatch")
    if not np.array_equal(np.asarray(tables["top_table"]), expected["top_table"]):
        raise AssertionError("eta6_p19 top table mismatch")
    if not np.array_equal(
        np.asarray(tables["observable_table"]),
        expected["obs_table"],
    ):
        raise AssertionError("eta6_p19 observable table mismatch")

    if report.get("schema") != "eta6.p19.report@1":
        raise AssertionError("eta6_p19 report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6_p19 report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6_p19 all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6_p19 checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p19 report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6_p19 report hash mismatch")

    top_table = np.asarray(tables["top_table"], dtype=np.int64)
    obs_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(top_table.shape) != (TOP_N, len(TOP_COLUMNS)):
        raise AssertionError("eta6_p19 top table shape mismatch")
    if tuple(obs_table.shape) != (len(OBS_CODES), len(OBS_COLUMNS)):
        raise AssertionError("eta6_p19 obs table shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(obs_table, OBS_COLUMNS)
    }
    required = {
        "p5_extension_count": 144,
        "triple_count": 487344,
        "full_six_count": 11143364232,
        "cell_width": 33554432,
        "neighbor_cell_count": 81,
        "grid_cell_count": 114454,
        "raw_lookup_count": 722138260,
        "raw_pair_count": 337311229,
        "outside_raw_pair_count": 307586410,
        "inside_222_raw_pair_count": 29724819,
        "outside_unique_low_count": 36308,
        "p5_single_floor": 11213312,
        "p6_pair_floor": 10515968,
        "p7_triple_floor": 2601984,
        "p8_quad_floor": 2447744,
        "p11_quint_floor": 1815040,
        "p14_basin_six_floor": 1164096,
        "p15_grid_floor": 492736,
        "outside_min_spread": 1164096,
        "outside_min_below_p15_flag": 0,
        "outside_min_below_p14_flag": 0,
        "outside_below_p15_raw_count": 0,
        "outside_below_p14_raw_count": 0,
        "outside_below_p11_raw_count": 240,
        "outside_below_p8_raw_count": 980,
        "outside_below_p7_raw_count": 1160,
        "outside_below_p6_raw_count": 283070,
        "outside_below_p5_raw_count": 363080,
        "outside_support_equal_raw_count": 0,
        "outside_below_p15_unique_count": 0,
        "outside_below_p14_unique_count": 0,
        "outside_below_p11_unique_count": 24,
        "outside_below_p8_unique_count": 98,
        "outside_below_p7_unique_count": 116,
        "outside_below_p6_unique_count": 28307,
        "outside_below_p5_unique_count": 36308,
        "outside_support_equal_unique_count": 0,
        "best_p5_a": 6,
        "best_p5_b": 12,
        "best_p5_c": 19,
        "best_p5_d": 29,
        "best_p5_e": 94,
        "best_p5_f": 96,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"eta6_p19 observable {key} mismatch")

    best = table_rows(top_table, TOP_COLUMNS)[0]
    if [best[f"p5_{letter}"] for letter in "abcdef"] != [6, 12, 19, 29, 94, 96]:
        raise AssertionError("eta6_p19 best p5 ids mismatch")
    if best["joint_support_spread"] != 1164096:
        raise AssertionError("eta6_p19 best spread mismatch")
    if top_csv.splitlines()[0].split(",") != TOP_COLUMNS:
        raise AssertionError("eta6_p19 top header mismatch")

    witness = report.get("witness", {})
    if witness.get("classification") != "expanded_grid_outside_222_screen":
        raise AssertionError("eta6_p19 classification mismatch")
    if witness.get("outside_min_spread") != 1164096:
        raise AssertionError("eta6_p19 min spread mismatch")
    if witness.get("outside_below_p15_unique_count") != 0:
        raise AssertionError("eta6_p19 below-p15 count mismatch")
    if witness.get("outside_support_equal_unique_count") != 0:
        raise AssertionError("eta6_p19 support equal count mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("p5_report", {}), P5_REPORT, "p5 report")
    assert_file_hash(inputs.get("p5_tables", {}), P5_TABLES, "p5 tables")
    assert_file_hash(inputs.get("p15_report", {}), P15_REPORT, "p15 report")
    assert_file_hash(inputs.get("p17_report", {}), P17_REPORT, "p17 report")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "eta6.p19.manifest@1":
        raise AssertionError("eta6_p19 manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p19 manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("eta6_p19 manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6_p19 missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p19 index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6_p19 index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "eta6.p19.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_eta6_p19(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
