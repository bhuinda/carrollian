from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_eta6_p39 import (
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
    from derive_eta6_p39 import (
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


def validate_eta6_p39() -> dict[str, Any]:
    expected = build_payloads()
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    p39 = load_json(OUT_DIR / "p39.json")
    cert = load_json(OUT_DIR / "cert.json")
    top_csv = (OUT_DIR / "top.csv").read_text(encoding="utf-8")
    obs_csv = (OUT_DIR / "obs.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    index = load_json(INDEX_PATH)

    if p39 != expected["p39"]:
        raise AssertionError("eta6_p39 JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("eta6_p39 cert mismatch")
    if top_csv != expected["top_csv"]:
        raise AssertionError("eta6_p39 top CSV mismatch")
    if obs_csv != expected["obs_csv"]:
        raise AssertionError("eta6_p39 obs CSV mismatch")
    if not np.array_equal(np.asarray(tables["top_table"]), expected["top_table"]):
        raise AssertionError("eta6_p39 top table mismatch")
    if not np.array_equal(
        np.asarray(tables["observable_table"]),
        expected["obs_table"],
    ):
        raise AssertionError("eta6_p39 observable table mismatch")

    if report.get("schema") != "eta6.p39.report@1":
        raise AssertionError("eta6_p39 report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6_p39 report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6_p39 all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6_p39 checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p39 report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6_p39 report hash mismatch")

    top_table = np.asarray(tables["top_table"], dtype=np.int64)
    obs_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(top_table.shape) != (TOP_N, len(TOP_COLUMNS)):
        raise AssertionError("eta6_p39 top table shape mismatch")
    if tuple(obs_table.shape) != (len(OBS_CODES), len(OBS_COLUMNS)):
        raise AssertionError("eta6_p39 obs table shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(obs_table, OBS_COLUMNS)
    }
    required = {
        "p31_top_seed_count": 32768,
        "p31_top32768_worst_spread": 19618592,
        "p31_top32768_worst_p31_id": 274598157,
        "raw_extension_count": 4554752,
        "candidate_count": 4482624,
        "duplicate_candidate_count": 72128,
        "multi_source_candidate_count": 67402,
        "max_source_multiplicity": 6,
        "p37_basin_floor": 492736,
        "p38_branch_floor": 492736,
        "p39_basin_min_spread": 492736,
        "below_p38_candidate_count": 0,
        "below_p37_candidate_count": 0,
        "below_p36_candidate_count": 15,
        "below_p35_candidate_count": 632,
        "below_p31_candidate_count": 20,
        "support_equal_candidate_count": 0,
        "best_p39_id": 2335598,
        "best_p25_a": 1,
        "best_p25_b": 47,
        "best_p25_c": 57,
        "best_p25_d": 79,
        "best_p25_e": 110,
        "best_p25_f": 128,
        "best_source_count": 2,
        "best_source_min_rank": 4756,
        "best_source_max_rank": 4757,
        "best_same_face_spread": 2644672,
        "best_same_face_p39_id": 30854,
        "best_source_rank0_spread": 10529536,
        "best_source_rank0_p39_id": 75514,
        "best_low8192_spread": 492736,
        "best_low8192_p39_id": 2335598,
        "compound_horizon_margin": 1,
        "p26_margin_preserved_flag": 1,
        "packed_candidate_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"eta6_p39 observable {key} mismatch")

    witness = report.get("witness", {})
    if witness.get("classification") != "p39_packed_widen":
        raise AssertionError("eta6_p39 classification mismatch")
    if witness.get("p39_basin_min_spread") != 492736:
        raise AssertionError("eta6_p39 min spread mismatch")
    if witness.get("below_p38_candidate_count") != 0:
        raise AssertionError("eta6_p39 below-p38 count mismatch")
    if witness.get("below_p37_candidate_count") != 0:
        raise AssertionError("eta6_p39 below-p37 count mismatch")
    if witness.get("support_equal_candidate_count") != 0:
        raise AssertionError("eta6_p39 equalizer count mismatch")
    if witness.get("compound_horizon_margin") != 1:
        raise AssertionError("eta6_p39 horizon margin mismatch")
    if witness.get("candidate_count") != 4482624:
        raise AssertionError("eta6_p39 candidate count mismatch")
    if witness.get("seed_count") != 32768:
        raise AssertionError("eta6_p39 seed count mismatch")
    if witness.get("claim_boundary", {}).get("p31_top32768_packed_screen") != 1:
        raise AssertionError("eta6_p39 screen boundary mismatch")
    if witness.get("claim_boundary", {}).get("candidate_below_p38_found") != 0:
        raise AssertionError("eta6_p39 below-p38 boundary mismatch")
    if witness.get("claim_boundary", {}).get("raw_support_equalizer_found") != 0:
        raise AssertionError("eta6_p39 equalizer boundary mismatch")
    best = witness.get("best_candidates", [])
    if not best or best[0].get("p39_id") != 2335598:
        raise AssertionError("eta6_p39 best candidate mismatch")
    if best[0].get("p25_ids") != [1, 47, 57, 79, 110, 128]:
        raise AssertionError("eta6_p39 best p25 ids mismatch")
    if best[0].get("spread") != 492736:
        raise AssertionError("eta6_p39 best spread mismatch")
    if top_csv.splitlines()[0].split(",") != TOP_COLUMNS:
        raise AssertionError("eta6_p39 top header mismatch")

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
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "eta6.p39.manifest@1":
        raise AssertionError("eta6_p39 manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p39 manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("eta6_p39 manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6_p39 missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p39 index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6_p39 index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "eta6.p39.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_eta6_p39(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
