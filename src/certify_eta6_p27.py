from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_eta6_p27 import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        P25_REPORT,
        P25_TABLES,
        P26_REPORT,
        PAIR_COLUMNS,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_eta6_p27 import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        P25_REPORT,
        P25_TABLES,
        P26_REPORT,
        PAIR_COLUMNS,
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


def table_rows(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def validate_eta6_p27() -> dict[str, Any]:
    expected = build_payloads()
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    p27 = load_json(OUT_DIR / "p27.json")
    cert = load_json(OUT_DIR / "cert.json")
    pair_csv = (OUT_DIR / "pair.csv").read_text(encoding="utf-8")
    obs_csv = (OUT_DIR / "obs.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    index = load_json(INDEX_PATH)

    if p27 != expected["p27"]:
        raise AssertionError("eta6_p27 JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("eta6_p27 cert mismatch")
    if pair_csv != expected["pair_csv"]:
        raise AssertionError("eta6_p27 pair CSV mismatch")
    if obs_csv != expected["obs_csv"]:
        raise AssertionError("eta6_p27 obs CSV mismatch")
    if not np.array_equal(np.asarray(tables["pair_table"]), expected["pair_table"]):
        raise AssertionError("eta6_p27 pair table mismatch")
    if not np.array_equal(
        np.asarray(tables["observable_table"]),
        expected["obs_table"],
    ):
        raise AssertionError("eta6_p27 observable table mismatch")

    if report.get("schema") != "eta6.p27.report@1":
        raise AssertionError("eta6_p27 report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6_p27 report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6_p27 all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6_p27 checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p27 report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6_p27 report hash mismatch")

    pair_table = np.asarray(tables["pair_table"], dtype=np.int64)
    obs_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(pair_table.shape) != (10296, len(PAIR_COLUMNS)):
        raise AssertionError("eta6_p27 pair table shape mismatch")
    if tuple(obs_table.shape) != (len(OBS_CODES), len(OBS_COLUMNS)):
        raise AssertionError("eta6_p27 obs table shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(obs_table, OBS_COLUMNS)
    }
    required = {
        "p25_extension_count": 144,
        "pair_count": 10296,
        "p25_single_floor": 11213312,
        "pair_min_spread": 10515968,
        "pair_min_below_single_flag": 1,
        "below_single_pair_count": 4,
        "support_equal_pair_count": 0,
        "best_pair_id": 410,
        "best_pair_p25_a": 2,
        "best_pair_p25_b": 128,
        "best_pair_face_a": 12,
        "best_pair_face_b": 26,
        "best_same_face_spread": 10533376,
        "best_same_face_pair_id": 1936,
        "best_same_mask_spread": 10533376,
        "best_same_mask_pair_id": 1936,
        "p26_horizon_component_count": 4,
        "p26_checked_positive_row_total": 7735158,
        "p26_min_component_margin": 1,
        "compound_horizon_margin": 1,
        "compound_horizon_strict_flag": 1,
        "p26_margin_preserved_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"eta6_p27 observable {key} mismatch")

    witness = report.get("witness", {})
    if witness.get("classification") != "lifted_two_move_support_spread_descent":
        raise AssertionError("eta6_p27 classification mismatch")
    if witness.get("p25_single_floor") != 11213312:
        raise AssertionError("eta6_p27 single floor mismatch")
    if witness.get("pair_min_spread") != 10515968:
        raise AssertionError("eta6_p27 pair floor mismatch")
    if witness.get("below_single_pair_count") != 4:
        raise AssertionError("eta6_p27 below floor count mismatch")
    if witness.get("support_equal_pair_count") != 0:
        raise AssertionError("eta6_p27 support equalizer mismatch")
    if witness.get("compound_horizon_margin") != 1:
        raise AssertionError("eta6_p27 horizon margin mismatch")
    if witness.get("claim_boundary", {}).get("complete_pair_screen") != 1:
        raise AssertionError("eta6_p27 pair screen boundary mismatch")
    if witness.get("claim_boundary", {}).get("raw_support_equalizer_found") != 0:
        raise AssertionError("eta6_p27 equalizer boundary mismatch")
    if witness.get("claim_boundary", {}).get("p26_margin_preserved") != 1:
        raise AssertionError("eta6_p27 p26 boundary mismatch")
    best = witness.get("best_pairs", [])
    if not best or best[0].get("pair_id") != 410:
        raise AssertionError("eta6_p27 best pair mismatch")
    if best[0].get("p25_ids") != [2, 128]:
        raise AssertionError("eta6_p27 best pair ids mismatch")
    if best[0].get("spread") != 10515968:
        raise AssertionError("eta6_p27 best spread mismatch")
    if pair_csv.splitlines()[0].split(",") != PAIR_COLUMNS:
        raise AssertionError("eta6_p27 pair header mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("p25_report", {}), P25_REPORT, "p25 report")
    assert_file_hash(inputs.get("p25_tables", {}), P25_TABLES, "p25 tables")
    assert_file_hash(inputs.get("p26_report", {}), P26_REPORT, "p26 report")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "eta6.p27.manifest@1":
        raise AssertionError("eta6_p27 manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p27 manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("eta6_p27 manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6_p27 missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p27 index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6_p27 index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "eta6.p27.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_eta6_p27(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
