from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_eta6_p16 import (
        DERIVE_SCRIPT,
        GAP_REPORT,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        P5_REPORT,
        P5_TABLES,
        P15_REPORT,
        P15_TABLES,
        ROW_COLUMNS,
        STATUS,
        THEOREM_ID,
        TOP_N,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_eta6_p16 import (
        DERIVE_SCRIPT,
        GAP_REPORT,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        P5_REPORT,
        P5_TABLES,
        P15_REPORT,
        P15_TABLES,
        ROW_COLUMNS,
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


def validate_eta6_p16() -> dict[str, Any]:
    expected = build_payloads()
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    p16 = load_json(OUT_DIR / "p16.json")
    cert = load_json(OUT_DIR / "cert.json")
    rows_csv = (OUT_DIR / "rows.csv").read_text(encoding="utf-8")
    obs_csv = (OUT_DIR / "obs.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    index = load_json(INDEX_PATH)

    if p16 != expected["p16"]:
        raise AssertionError("eta6_p16 JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("eta6_p16 cert mismatch")
    if rows_csv != expected["rows_csv"]:
        raise AssertionError("eta6_p16 rows CSV mismatch")
    if obs_csv != expected["obs_csv"]:
        raise AssertionError("eta6_p16 obs CSV mismatch")
    if not np.array_equal(np.asarray(tables["row_table"]), expected["row_table"]):
        raise AssertionError("eta6_p16 row table mismatch")
    if not np.array_equal(
        np.asarray(tables["observable_table"]),
        expected["obs_table"],
    ):
        raise AssertionError("eta6_p16 observable table mismatch")

    if report.get("schema") != "eta6.p16.report@1":
        raise AssertionError("eta6_p16 report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6_p16 report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6_p16 all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6_p16 checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p16 report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6_p16 report hash mismatch")

    row_table = np.asarray(tables["row_table"], dtype=np.int64)
    obs_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(row_table.shape) != (TOP_N, len(ROW_COLUMNS)):
        raise AssertionError("eta6_p16 row table shape mismatch")
    if tuple(obs_table.shape) != (len(OBS_CODES), len(OBS_COLUMNS)):
        raise AssertionError("eta6_p16 obs table shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(obs_table, OBS_COLUMNS)
    }
    required = {
        "top_row_count": 16,
        "component_move_count": 96,
        "mirror_closed_row_count": 16,
        "self_mirror_row_count": 2,
        "mirror_pair_count": 7,
        "eta6_preserved_row_count": 16,
        "eta6_preserved_move_count": 96,
        "global_delta_zero_row_count": 2,
        "per_face_delta_zero_row_count": 2,
        "carrier_neutral_row_count": 2,
        "balanced_222_row_count": 1,
        "winner_rank": 0,
        "winner_p15_id": 58834,
        "winner_spread": 492736,
        "winner_balanced_222_flag": 1,
        "winner_carrier_neutral_flag": 1,
        "winner_hpol_min_margin": 1,
        "winner_repl_min_margin": 146,
        "winner_margin_positive_flag": 1,
        "p15_screen_min_spread": 492736,
        "p15_unique_candidate_count": 434839,
        "support_equal_top_row_count": 0,
        "imported_hpol_min_margin": 1,
        "imported_repl_min_margin": 146,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"eta6_p16 observable {key} mismatch")

    rows = table_rows(row_table, ROW_COLUMNS)
    winner = rows[0]
    if winner["p15_id"] != 58834:
        raise AssertionError("eta6_p16 winner p15 id mismatch")
    if [winner[f"p5_{letter}"] for letter in "abcdef"] != [1, 47, 57, 79, 110, 128]:
        raise AssertionError("eta6_p16 winner p5 ids mismatch")
    if winner["carrier_margin_positive_flag"] != 1:
        raise AssertionError("eta6_p16 winner margin flag mismatch")
    if rows_csv.splitlines()[0].split(",") != ROW_COLUMNS:
        raise AssertionError("eta6_p16 rows header mismatch")

    witness = report.get("witness", {})
    if witness.get("classification") != "p15_top16_carrier_margin_packet":
        raise AssertionError("eta6_p16 classification mismatch")
    if witness.get("p15_winner", {}).get("p5_ids") != [1, 47, 57, 79, 110, 128]:
        raise AssertionError("eta6_p16 witness winner ids mismatch")
    if witness.get("carrier_neutrality", {}).get("balanced_222_row_count") != 1:
        raise AssertionError("eta6_p16 balanced count mismatch")
    if witness.get("mirror_packet", {}).get("mirror_pair_count") != 7:
        raise AssertionError("eta6_p16 mirror count mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("p5_report", {}), P5_REPORT, "p5 report")
    assert_file_hash(inputs.get("p5_tables", {}), P5_TABLES, "p5 tables")
    assert_file_hash(inputs.get("p15_report", {}), P15_REPORT, "p15 report")
    assert_file_hash(inputs.get("p15_tables", {}), P15_TABLES, "p15 tables")
    assert_file_hash(inputs.get("gap_report", {}), GAP_REPORT, "gap report")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "eta6.p16.manifest@1":
        raise AssertionError("eta6_p16 manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p16 manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("eta6_p16 manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6_p16 missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p16 index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6_p16 index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "eta6.p16.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_eta6_p16(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
