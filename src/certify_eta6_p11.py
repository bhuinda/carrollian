from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_eta6_p11 import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        P5_REPORT,
        P5_TABLES,
        P6_REPORT,
        P7_REPORT,
        P8_REPORT,
        P9_REPORT,
        P10_REPORT,
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
    from derive_eta6_p11 import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        P5_REPORT,
        P5_TABLES,
        P6_REPORT,
        P7_REPORT,
        P8_REPORT,
        P9_REPORT,
        P10_REPORT,
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


def validate_eta6_p11() -> dict[str, Any]:
    expected = build_payloads()
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    p11 = load_json(OUT_DIR / "p11.json")
    cert = load_json(OUT_DIR / "cert.json")
    top_csv = (OUT_DIR / "top.csv").read_text(encoding="utf-8")
    obs_csv = (OUT_DIR / "obs.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    index = load_json(INDEX_PATH)

    if p11 != expected["p11"]:
        raise AssertionError("eta6_p11 JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("eta6_p11 cert mismatch")
    if top_csv != expected["top_csv"]:
        raise AssertionError("eta6_p11 top CSV mismatch")
    if obs_csv != expected["obs_csv"]:
        raise AssertionError("eta6_p11 obs CSV mismatch")
    if not np.array_equal(np.asarray(tables["top_table"]), expected["top_table"]):
        raise AssertionError("eta6_p11 top table mismatch")
    if not np.array_equal(
        np.asarray(tables["observable_table"]),
        expected["obs_table"],
    ):
        raise AssertionError("eta6_p11 observable table mismatch")

    if report.get("schema") != "eta6.p11.report@1":
        raise AssertionError("eta6_p11 report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6_p11 report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6_p11 all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6_p11 checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p11 report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6_p11 report hash mismatch")

    top_table = np.asarray(tables["top_table"], dtype=np.int64)
    obs_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(top_table.shape) != (TOP_N, len(TOP_COLUMNS)):
        raise AssertionError("eta6_p11 top table shape mismatch")
    if tuple(obs_table.shape) != (len(OBS_CODES), len(OBS_COLUMNS)):
        raise AssertionError("eta6_p11 obs table shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(obs_table, OBS_COLUMNS)
    }
    required = {
        "p5_extension_count": 144,
        "pair_count": 10296,
        "triple_count": 487344,
        "quint_count": 481008528,
        "p5_single_floor": 11213312,
        "p6_pair_floor": 10515968,
        "p7_triple_floor": 2601984,
        "p8_quad_floor": 2447744,
        "p9_bounded_floor": 5601664,
        "p10_shadow_floor": 4213120,
        "quint_min_spread": 1815040,
        "quint_min_below_p10_flag": 1,
        "quint_min_below_p9_flag": 1,
        "quint_min_below_p8_flag": 1,
        "below_p10_candidate_count": 60,
        "below_p9_candidate_count": 226,
        "below_p8_candidate_count": 2,
        "below_p7_candidate_count": 4,
        "below_p6_candidate_count": 2734,
        "below_p5_candidate_count": 3526,
        "support_equal_candidate_count": 0,
        "best_p11_id": 67415100,
        "best_p5_a": 1,
        "best_p5_b": 8,
        "best_p5_c": 41,
        "best_p5_d": 52,
        "best_p5_e": 54,
        "best_face_a": 12,
        "best_face_b": 12,
        "best_face_c": 12,
        "best_face_d": 22,
        "best_face_e": 22,
        "best_same_face_spread": 3384704,
        "best_same_face_p11_id": 15777042,
        "best_same_mask_spread": 3384704,
        "best_same_mask_p11_id": 15777042,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"eta6_p11 observable {key} mismatch")

    witness = report.get("witness", {})
    if witness.get("classification") != "complete_five_move_support_spread_descent":
        raise AssertionError("eta6_p11 classification mismatch")
    if witness.get("quint_min_spread") != 1815040:
        raise AssertionError("eta6_p11 quint min spread mismatch")
    if witness.get("below_p8_candidate_count") != 2:
        raise AssertionError("eta6_p11 below-p8 count mismatch")
    if witness.get("support_equal_candidate_count") != 0:
        raise AssertionError("eta6_p11 support equal count mismatch")
    best = witness.get("best_candidates", [])
    if not best or best[0].get("p11_id") != 67415100:
        raise AssertionError("eta6_p11 best candidate mismatch")
    if best[0].get("p5_ids") != [1, 8, 41, 52, 54]:
        raise AssertionError("eta6_p11 best p5 ids mismatch")
    if best[0].get("spread") != 1815040:
        raise AssertionError("eta6_p11 best spread mismatch")
    if top_csv.splitlines()[0].split(",") != TOP_COLUMNS:
        raise AssertionError("eta6_p11 top header mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("p5_report", {}), P5_REPORT, "p5 report")
    assert_file_hash(inputs.get("p5_tables", {}), P5_TABLES, "p5 tables")
    assert_file_hash(inputs.get("p6_report", {}), P6_REPORT, "p6 report")
    assert_file_hash(inputs.get("p7_report", {}), P7_REPORT, "p7 report")
    assert_file_hash(inputs.get("p8_report", {}), P8_REPORT, "p8 report")
    assert_file_hash(inputs.get("p9_report", {}), P9_REPORT, "p9 report")
    assert_file_hash(inputs.get("p10_report", {}), P10_REPORT, "p10 report")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "eta6.p11.manifest@1":
        raise AssertionError("eta6_p11 manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p11 manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("eta6_p11 manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6_p11 missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p11 index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6_p11 index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "eta6.p11.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_eta6_p11(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
