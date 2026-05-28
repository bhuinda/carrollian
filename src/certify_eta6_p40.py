from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_eta6_p40 import (
        BRANCH_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        P25_REPORT,
        P25_TABLES,
        P26_REPORT,
        P27_REPORT,
        P28_REPORT,
        P29_REPORT,
        P30_REPORT,
        P31_REPORT,
        P32_REPORT,
        P33_REPORT,
        P34_REPORT,
        P35_REPORT,
        P36_REPORT,
        P37_REPORT,
        P38_REPORT,
        P39_REPORT,
        STATUS,
        THEOREM_ID,
        TOP_N,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_eta6_p40 import (
        BRANCH_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        P25_REPORT,
        P25_TABLES,
        P26_REPORT,
        P27_REPORT,
        P28_REPORT,
        P29_REPORT,
        P30_REPORT,
        P31_REPORT,
        P32_REPORT,
        P33_REPORT,
        P34_REPORT,
        P35_REPORT,
        P36_REPORT,
        P37_REPORT,
        P38_REPORT,
        P39_REPORT,
        STATUS,
        THEOREM_ID,
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


def validate_eta6_p40() -> dict[str, Any]:
    expected = build_payloads()
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    p40 = load_json(OUT_DIR / "p40.json")
    cert = load_json(OUT_DIR / "cert.json")
    branch_csv = (OUT_DIR / "branch.csv").read_text(encoding="utf-8")
    obs_csv = (OUT_DIR / "obs.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    index = load_json(INDEX_PATH)

    if p40 != expected["p40"]:
        raise AssertionError("eta6_p40 JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("eta6_p40 cert mismatch")
    if branch_csv != expected["branch_csv"]:
        raise AssertionError("eta6_p40 branch CSV mismatch")
    if obs_csv != expected["obs_csv"]:
        raise AssertionError("eta6_p40 obs CSV mismatch")
    if not np.array_equal(
        np.asarray(tables["branch_table"]),
        expected["branch_table"],
    ):
        raise AssertionError("eta6_p40 branch table mismatch")
    if not np.array_equal(
        np.asarray(tables["observable_table"]),
        expected["obs_table"],
    ):
        raise AssertionError("eta6_p40 observable table mismatch")

    if report.get("schema") != "eta6.p40.report@1":
        raise AssertionError("eta6_p40 report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6_p40 report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6_p40 all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6_p40 checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p40 report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6_p40 report hash mismatch")

    branch_table = np.asarray(tables["branch_table"], dtype=np.int64)
    obs_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(branch_table.shape) != (TOP_N, len(BRANCH_COLUMNS)):
        raise AssertionError("eta6_p40 branch table shape mismatch")
    if tuple(obs_table.shape) != (len(OBS_CODES), len(OBS_COLUMNS)):
        raise AssertionError("eta6_p40 obs table shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(obs_table, OBS_COLUMNS)
    }
    required = {
        "p25_extension_count": 144,
        "p31_top_seed_count": 131072,
        "p31_top131072_worst_spread": 28075840,
        "p31_top131072_worst_p31_id": 308298973,
        "raw_extension_count": 18219008,
        "p39_basin_floor": 492736,
        "p38_branch_floor": 492736,
        "p37_basin_floor": 492736,
        "branch_min_floor": 492736,
        "branch_min_below_p39_count": 0,
        "branch_min_equal_p39_count": 2,
        "branch_min_below_p38_count": 0,
        "branch_min_below_p37_count": 0,
        "branch_support_equal_count": 0,
        "branch_min_below_p36_count": 26,
        "branch_min_below_p35_count": 1046,
        "branch_min_below_p34_count": 4674,
        "branch_min_below_p33_count": 8050,
        "branch_min_below_p32_count": 6652,
        "branch_min_below_p31_count": 40,
        "branch_min_below_p30_count": 792,
        "branch_min_below_p29_count": 118,
        "branch_min_below_p28_count": 140,
        "branch_min_below_p27_count": 20354,
        "branch_min_below_p25_count": 24720,
        "branch_min_max": 33327776,
        "branch_min_sum": 2100868571648,
        "best_seed_rank": 4756,
        "best_p31_id": 29509840,
        "best_ext_p25_id": 128,
        "best_seed_spread": 12025920,
        "compound_horizon_margin": 1,
        "p26_margin_preserved_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"eta6_p40 observable {key} mismatch")

    witness = report.get("witness", {})
    if witness.get("classification") != "p40_branch_env":
        raise AssertionError("eta6_p40 classification mismatch")
    if witness.get("branch_min_floor") != 492736:
        raise AssertionError("eta6_p40 branch floor mismatch")
    if witness.get("branch_min_below_p39_count") != 0:
        raise AssertionError("eta6_p40 below-p39 count mismatch")
    if witness.get("branch_min_equal_p39_count") != 2:
        raise AssertionError("eta6_p40 equal-p39 count mismatch")
    if witness.get("branch_min_below_p38_count") != 0:
        raise AssertionError("eta6_p40 below-p38 count mismatch")
    if witness.get("branch_min_below_p37_count") != 0:
        raise AssertionError("eta6_p40 below-p37 count mismatch")
    if witness.get("branch_support_equal_count") != 0:
        raise AssertionError("eta6_p40 equalizer count mismatch")
    if witness.get("compound_horizon_margin") != 1:
        raise AssertionError("eta6_p40 horizon margin mismatch")
    if witness.get("raw_extension_count") != 18219008:
        raise AssertionError("eta6_p40 raw count mismatch")
    if witness.get("claim_boundary", {}).get("p31_top131072_branch_env") != 1:
        raise AssertionError("eta6_p40 screen boundary mismatch")
    if witness.get("claim_boundary", {}).get("branch_below_p39_found") != 0:
        raise AssertionError("eta6_p40 below-p39 boundary mismatch")
    if witness.get("claim_boundary", {}).get("raw_support_equalizer_found") != 0:
        raise AssertionError("eta6_p40 equalizer boundary mismatch")
    if witness.get("claim_boundary", {}).get("p26_margin_preserved") != 1:
        raise AssertionError("eta6_p40 p26 boundary mismatch")
    best = witness.get("best_branches", [])
    if not best or best[0].get("seed_rank") != 4756:
        raise AssertionError("eta6_p40 best branch mismatch")
    if best[0].get("p25_ids") != [1, 47, 57, 79, 110, 128]:
        raise AssertionError("eta6_p40 best p25 ids mismatch")
    if best[0].get("spread") != 492736:
        raise AssertionError("eta6_p40 best spread mismatch")
    if branch_csv.splitlines()[0].split(",") != BRANCH_COLUMNS:
        raise AssertionError("eta6_p40 branch header mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "p25_report": P25_REPORT,
        "p25_tables": P25_TABLES,
        "p26_report": P26_REPORT,
        "p27_report": P27_REPORT,
        "p28_report": P28_REPORT,
        "p29_report": P29_REPORT,
        "p30_report": P30_REPORT,
        "p31_report": P31_REPORT,
        "p32_report": P32_REPORT,
        "p33_report": P33_REPORT,
        "p34_report": P34_REPORT,
        "p35_report": P35_REPORT,
        "p36_report": P36_REPORT,
        "p37_report": P37_REPORT,
        "p38_report": P38_REPORT,
        "p39_report": P39_REPORT,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "eta6.p40.manifest@1":
        raise AssertionError("eta6_p40 manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p40 manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("eta6_p40 manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6_p40 missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p40 index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6_p40 index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "eta6.p40.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_eta6_p40(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
