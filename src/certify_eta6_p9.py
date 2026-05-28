from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_eta6_p9 import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        P5_REPORT,
        P5_TABLES,
        P6_REPORT,
        P7_REPORT,
        P7_TABLES,
        P8_REPORT,
        P8_TABLES,
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
    from derive_eta6_p9 import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        P5_REPORT,
        P5_TABLES,
        P6_REPORT,
        P7_REPORT,
        P7_TABLES,
        P8_REPORT,
        P8_TABLES,
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


def validate_eta6_p9() -> dict[str, Any]:
    expected = build_payloads()
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    p9 = load_json(OUT_DIR / "p9.json")
    cert = load_json(OUT_DIR / "cert.json")
    top_csv = (OUT_DIR / "top.csv").read_text(encoding="utf-8")
    obs_csv = (OUT_DIR / "obs.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    index = load_json(INDEX_PATH)

    if p9 != expected["p9"]:
        raise AssertionError("eta6_p9 JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("eta6_p9 cert mismatch")
    if top_csv != expected["top_csv"]:
        raise AssertionError("eta6_p9 top CSV mismatch")
    if obs_csv != expected["obs_csv"]:
        raise AssertionError("eta6_p9 obs CSV mismatch")
    if not np.array_equal(np.asarray(tables["top_table"]), expected["top_table"]):
        raise AssertionError("eta6_p9 top table mismatch")
    if not np.array_equal(
        np.asarray(tables["observable_table"]),
        expected["obs_table"],
    ):
        raise AssertionError("eta6_p9 observable table mismatch")

    if report.get("schema") != "eta6.p9.report@1":
        raise AssertionError("eta6_p9 report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6_p9 report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6_p9 all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6_p9 checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p9 report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6_p9 report hash mismatch")

    top_table = np.asarray(tables["top_table"], dtype=np.int64)
    obs_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(top_table.shape) != (TOP_N, len(TOP_COLUMNS)):
        raise AssertionError("eta6_p9 top table shape mismatch")
    if tuple(obs_table.shape) != (len(OBS_CODES), len(OBS_COLUMNS)):
        raise AssertionError("eta6_p9 obs table shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(obs_table, OBS_COLUMNS)
    }
    required = {
        "p5_extension_count": 144,
        "p7_top_count": 32,
        "p8_top_count": 32,
        "candidate_count": 316068,
        "p5_single_floor": 11213312,
        "p6_pair_floor": 10515968,
        "p7_triple_floor": 2601984,
        "p8_quad_floor": 2447744,
        "bounded_min_spread": 5601664,
        "bounded_min_below_p8_flag": 0,
        "below_p8_candidate_count": 0,
        "below_p7_candidate_count": 0,
        "below_p6_candidate_count": 88,
        "below_p5_candidate_count": 128,
        "support_equal_candidate_count": 0,
        "best_p9_id": 10321,
        "best_p5_a": 2,
        "best_p5_b": 8,
        "best_p5_c": 12,
        "best_p5_d": 30,
        "best_p5_e": 128,
        "best_face_a": 12,
        "best_face_b": 12,
        "best_face_c": 12,
        "best_face_d": 12,
        "best_face_e": 26,
        "best_same_face_spread": 5959680,
        "best_same_face_p9_id": 120075,
        "best_same_mask_spread": 5959680,
        "best_same_mask_p9_id": 120075,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"eta6_p9 observable {key} mismatch")

    witness = report.get("witness", {})
    if witness.get("classification") != "bounded_five_move_frontier_stall":
        raise AssertionError("eta6_p9 classification mismatch")
    if witness.get("p8_quad_floor") != 2447744:
        raise AssertionError("eta6_p9 p8 floor mismatch")
    if witness.get("bounded_min_spread") != 5601664:
        raise AssertionError("eta6_p9 bounded min spread mismatch")
    if witness.get("below_p8_candidate_count") != 0:
        raise AssertionError("eta6_p9 below-p8 count mismatch")
    if witness.get("support_equal_candidate_count") != 0:
        raise AssertionError("eta6_p9 support equal count mismatch")
    best = witness.get("best_candidates", [])
    if not best or best[0].get("p9_id") != 10321:
        raise AssertionError("eta6_p9 best candidate mismatch")
    if best[0].get("p5_ids") != [2, 8, 12, 30, 128]:
        raise AssertionError("eta6_p9 best p5 ids mismatch")
    if best[0].get("spread") != 5601664:
        raise AssertionError("eta6_p9 best spread mismatch")
    if top_csv.splitlines()[0].split(",") != TOP_COLUMNS:
        raise AssertionError("eta6_p9 top header mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("p5_report", {}), P5_REPORT, "p5 report")
    assert_file_hash(inputs.get("p5_tables", {}), P5_TABLES, "p5 tables")
    assert_file_hash(inputs.get("p6_report", {}), P6_REPORT, "p6 report")
    assert_file_hash(inputs.get("p7_report", {}), P7_REPORT, "p7 report")
    assert_file_hash(inputs.get("p7_tables", {}), P7_TABLES, "p7 tables")
    assert_file_hash(inputs.get("p8_report", {}), P8_REPORT, "p8 report")
    assert_file_hash(inputs.get("p8_tables", {}), P8_TABLES, "p8 tables")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "eta6.p9.manifest@1":
        raise AssertionError("eta6_p9 manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p9 manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("eta6_p9 manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6_p9 missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p9 index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6_p9 index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "eta6.p9.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_eta6_p9(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
