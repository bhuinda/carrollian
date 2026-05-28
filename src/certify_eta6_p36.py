from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_eta6_p36 import (
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
    from derive_eta6_p36 import (
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


def validate_eta6_p36() -> dict[str, Any]:
    expected = build_payloads()
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    p36 = load_json(OUT_DIR / "p36.json")
    cert = load_json(OUT_DIR / "cert.json")
    top_csv = (OUT_DIR / "top.csv").read_text(encoding="utf-8")
    obs_csv = (OUT_DIR / "obs.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    index = load_json(INDEX_PATH)

    if p36 != expected["p36"]:
        raise AssertionError("eta6_p36 JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("eta6_p36 cert mismatch")
    if top_csv != expected["top_csv"]:
        raise AssertionError("eta6_p36 top CSV mismatch")
    if obs_csv != expected["obs_csv"]:
        raise AssertionError("eta6_p36 obs CSV mismatch")
    if not np.array_equal(np.asarray(tables["top_table"]), expected["top_table"]):
        raise AssertionError("eta6_p36 top table mismatch")
    if not np.array_equal(
        np.asarray(tables["observable_table"]),
        expected["obs_table"],
    ):
        raise AssertionError("eta6_p36 observable table mismatch")

    if report.get("schema") != "eta6.p36.report@1":
        raise AssertionError("eta6_p36 report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6_p36 report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6_p36 all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6_p36 checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p36 report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6_p36 report hash mismatch")

    top_table = np.asarray(tables["top_table"], dtype=np.int64)
    obs_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(top_table.shape) != (TOP_N, len(TOP_COLUMNS)):
        raise AssertionError("eta6_p36 top table shape mismatch")
    if tuple(obs_table.shape) != (len(OBS_CODES), len(OBS_COLUMNS)):
        raise AssertionError("eta6_p36 obs table shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(obs_table, OBS_COLUMNS)
    }
    required = {
        "p25_extension_count": 144,
        "p31_top_seed_count": 2048,
        "p31_top2048_worst_spread": 9747264,
        "p31_top2048_worst_p31_id": 73407855,
        "raw_extension_count": 284672,
        "candidate_count": 283830,
        "duplicate_candidate_count": 842,
        "multi_source_candidate_count": 818,
        "max_source_multiplicity": 3,
        "p25_single_floor": 11213312,
        "p27_pair_floor": 10515968,
        "p28_triple_floor": 2601984,
        "p29_quad_floor": 2447744,
        "p30_bounded_floor": 4213120,
        "p31_quint_floor": 1815040,
        "p32_seeded_floor": 7541600,
        "p33_basin_floor": 7982592,
        "p34_basin_floor": 6796608,
        "p35_basin_floor": 4589696,
        "p36_basin_min_spread": 1667584,
        "basin_min_below_p35_flag": 1,
        "basin_min_below_p34_flag": 1,
        "basin_min_below_p33_flag": 1,
        "basin_min_below_p32_flag": 1,
        "basin_min_below_p31_flag": 1,
        "basin_min_below_p30_flag": 1,
        "basin_min_below_p29_flag": 1,
        "basin_min_below_p28_flag": 1,
        "below_p35_candidate_count": 89,
        "below_p34_candidate_count": 523,
        "below_p33_candidate_count": 998,
        "below_p32_candidate_count": 790,
        "below_p31_candidate_count": 1,
        "below_p30_candidate_count": 66,
        "below_p29_candidate_count": 5,
        "below_p28_candidate_count": 7,
        "below_p27_candidate_count": 2874,
        "below_p25_candidate_count": 3630,
        "support_equal_candidate_count": 0,
        "best_p36_id": 26360,
        "best_p25_a": 1,
        "best_p25_b": 14,
        "best_p25_c": 32,
        "best_p25_d": 47,
        "best_p25_e": 57,
        "best_p25_f": 79,
        "best_source_count": 2,
        "best_source_min_rank": 1902,
        "best_source_max_rank": 1903,
        "best_face_a": 12,
        "best_face_b": 12,
        "best_face_c": 12,
        "best_face_d": 12,
        "best_face_e": 22,
        "best_face_f": 22,
        "best_same_face_spread": 3416832,
        "best_same_face_p36_id": 39461,
        "best_same_mask_spread": 3416832,
        "best_same_mask_p36_id": 39461,
        "best_source_rank0_spread": 10529536,
        "best_source_rank0_p36_id": 24398,
        "best_low512_spread": 4589696,
        "best_low512_p36_id": 161406,
        "p26_horizon_component_count": 4,
        "p26_checked_positive_row_total": 7735158,
        "p26_min_component_margin": 1,
        "compound_horizon_margin": 1,
        "compound_horizon_strict_flag": 1,
        "p26_margin_preserved_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"eta6_p36 observable {key} mismatch")

    witness = report.get("witness", {})
    if witness.get("classification") != "p36_descent":
        raise AssertionError("eta6_p36 classification mismatch")
    if witness.get("p36_basin_min_spread") != 1667584:
        raise AssertionError("eta6_p36 min spread mismatch")
    if witness.get("p35_basin_floor") != 4589696:
        raise AssertionError("eta6_p36 p35 floor mismatch")
    if witness.get("p31_quint_floor") != 1815040:
        raise AssertionError("eta6_p36 p31 floor mismatch")
    if witness.get("below_p31_candidate_count") != 1:
        raise AssertionError("eta6_p36 below-p31 count mismatch")
    if witness.get("support_equal_candidate_count") != 0:
        raise AssertionError("eta6_p36 support equal count mismatch")
    if witness.get("compound_horizon_margin") != 1:
        raise AssertionError("eta6_p36 horizon margin mismatch")
    if witness.get("candidate_count") != 283830:
        raise AssertionError("eta6_p36 candidate count mismatch")
    if witness.get("seed_count") != 2048:
        raise AssertionError("eta6_p36 seed count mismatch")
    if witness.get("seed_worst_spread") != 9747264:
        raise AssertionError("eta6_p36 seed worst mismatch")
    if witness.get("claim_boundary", {}).get("p31_top2048_basin_screen") != 1:
        raise AssertionError("eta6_p36 screen boundary mismatch")
    if witness.get("claim_boundary", {}).get("raw_support_equalizer_found") != 0:
        raise AssertionError("eta6_p36 equalizer boundary mismatch")
    if witness.get("claim_boundary", {}).get("p26_margin_preserved") != 1:
        raise AssertionError("eta6_p36 p26 boundary mismatch")
    best = witness.get("best_candidates", [])
    if not best or best[0].get("p36_id") != 26360:
        raise AssertionError("eta6_p36 best candidate mismatch")
    if best[0].get("p25_ids") != [1, 14, 32, 47, 57, 79]:
        raise AssertionError("eta6_p36 best p25 ids mismatch")
    if best[0].get("spread") != 1667584:
        raise AssertionError("eta6_p36 best spread mismatch")
    if best[0].get("source_min_rank") != 1902:
        raise AssertionError("eta6_p36 best source rank mismatch")
    if top_csv.splitlines()[0].split(",") != TOP_COLUMNS:
        raise AssertionError("eta6_p36 top header mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("p25_report", {}), P25_REPORT, "p25 report")
    assert_file_hash(inputs.get("p25_tables", {}), P25_TABLES, "p25 tables")
    assert_file_hash(inputs.get("p26_report", {}), P26_REPORT, "p26 report")
    assert_file_hash(inputs.get("p27_report", {}), P27_REPORT, "p27 report")
    assert_file_hash(inputs.get("p28_report", {}), P28_REPORT, "p28 report")
    assert_file_hash(inputs.get("p29_report", {}), P29_REPORT, "p29 report")
    assert_file_hash(inputs.get("p30_report", {}), P30_REPORT, "p30 report")
    assert_file_hash(inputs.get("p31_report", {}), P31_REPORT, "p31 report")
    assert_file_hash(inputs.get("p32_report", {}), P32_REPORT, "p32 report")
    assert_file_hash(inputs.get("p33_report", {}), P33_REPORT, "p33 report")
    assert_file_hash(inputs.get("p34_report", {}), P34_REPORT, "p34 report")
    assert_file_hash(inputs.get("p35_report", {}), P35_REPORT, "p35 report")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "eta6.p36.manifest@1":
        raise AssertionError("eta6_p36 manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p36 manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("eta6_p36 manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6_p36 missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p36 index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6_p36 index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "eta6.p36.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_eta6_p36(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
