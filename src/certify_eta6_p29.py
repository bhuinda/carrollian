from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_eta6_p29 import (
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
    from derive_eta6_p29 import (
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


def validate_eta6_p29() -> dict[str, Any]:
    expected = build_payloads()
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    p29 = load_json(OUT_DIR / "p29.json")
    cert = load_json(OUT_DIR / "cert.json")
    top_csv = (OUT_DIR / "top.csv").read_text(encoding="utf-8")
    obs_csv = (OUT_DIR / "obs.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    index = load_json(INDEX_PATH)

    if p29 != expected["p29"]:
        raise AssertionError("eta6_p29 JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("eta6_p29 cert mismatch")
    if top_csv != expected["top_csv"]:
        raise AssertionError("eta6_p29 top CSV mismatch")
    if obs_csv != expected["obs_csv"]:
        raise AssertionError("eta6_p29 obs CSV mismatch")
    if not np.array_equal(np.asarray(tables["top_table"]), expected["top_table"]):
        raise AssertionError("eta6_p29 top table mismatch")
    if not np.array_equal(
        np.asarray(tables["observable_table"]),
        expected["obs_table"],
    ):
        raise AssertionError("eta6_p29 observable table mismatch")

    if report.get("schema") != "eta6.p29.report@1":
        raise AssertionError("eta6_p29 report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6_p29 report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6_p29 all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6_p29 checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p29 report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6_p29 report hash mismatch")

    top_table = np.asarray(tables["top_table"], dtype=np.int64)
    obs_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(top_table.shape) != (TOP_N, len(TOP_COLUMNS)):
        raise AssertionError("eta6_p29 top table shape mismatch")
    if tuple(obs_table.shape) != (len(OBS_CODES), len(OBS_COLUMNS)):
        raise AssertionError("eta6_p29 obs table shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(obs_table, OBS_COLUMNS)
    }
    required = {
        "p25_extension_count": 144,
        "quad_count": 17178876,
        "p25_single_floor": 11213312,
        "p27_pair_floor": 10515968,
        "p28_triple_floor": 2601984,
        "quad_min_spread": 2447744,
        "quad_min_below_p28_flag": 1,
        "below_p28_quad_count": 1,
        "below_p27_quad_count": 247,
        "below_p25_quad_count": 311,
        "support_equal_quad_count": 0,
        "best_p29_id": 10063403,
        "best_p25_a": 28,
        "best_p25_b": 36,
        "best_p25_c": 58,
        "best_p25_d": 66,
        "best_face_a": 12,
        "best_face_b": 12,
        "best_face_c": 22,
        "best_face_d": 22,
        "best_same_face_spread": 2643328,
        "best_same_face_p29_id": 3573468,
        "best_same_mask_spread": 2643328,
        "best_same_mask_p29_id": 3573468,
        "p26_horizon_component_count": 4,
        "p26_checked_positive_row_total": 7735158,
        "p26_min_component_margin": 1,
        "compound_horizon_margin": 1,
        "compound_horizon_strict_flag": 1,
        "p26_margin_preserved_flag": 1,
        "mitm_pair_sum_count": 10296,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"eta6_p29 observable {key} mismatch")

    witness = report.get("witness", {})
    if witness.get("classification") != "lifted_four_move_support_spread_descent":
        raise AssertionError("eta6_p29 classification mismatch")
    if witness.get("p28_triple_floor") != 2601984:
        raise AssertionError("eta6_p29 p28 floor mismatch")
    if witness.get("quad_min_spread") != 2447744:
        raise AssertionError("eta6_p29 quad min spread mismatch")
    if witness.get("below_p28_quad_count") != 1:
        raise AssertionError("eta6_p29 below-p28 count mismatch")
    if witness.get("support_equal_quad_count") != 0:
        raise AssertionError("eta6_p29 support equal count mismatch")
    if witness.get("compound_horizon_margin") != 1:
        raise AssertionError("eta6_p29 horizon margin mismatch")
    if witness.get("claim_boundary", {}).get("complete_quad_screen") != 1:
        raise AssertionError("eta6_p29 quad screen boundary mismatch")
    if witness.get("claim_boundary", {}).get("raw_support_equalizer_found") != 0:
        raise AssertionError("eta6_p29 equalizer boundary mismatch")
    if witness.get("claim_boundary", {}).get("p26_margin_preserved") != 1:
        raise AssertionError("eta6_p29 p26 boundary mismatch")
    best = witness.get("best_quads", [])
    if not best or best[0].get("p29_id") != 10063403:
        raise AssertionError("eta6_p29 best quad mismatch")
    if best[0].get("p25_ids") != [28, 36, 58, 66]:
        raise AssertionError("eta6_p29 best p25 ids mismatch")
    if best[0].get("spread") != 2447744:
        raise AssertionError("eta6_p29 best spread mismatch")
    if top_csv.splitlines()[0].split(",") != TOP_COLUMNS:
        raise AssertionError("eta6_p29 top header mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("p25_report", {}), P25_REPORT, "p25 report")
    assert_file_hash(inputs.get("p25_tables", {}), P25_TABLES, "p25 tables")
    assert_file_hash(inputs.get("p26_report", {}), P26_REPORT, "p26 report")
    assert_file_hash(inputs.get("p27_report", {}), P27_REPORT, "p27 report")
    assert_file_hash(inputs.get("p28_report", {}), P28_REPORT, "p28 report")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "eta6.p29.manifest@1":
        raise AssertionError("eta6_p29 manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p29 manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("eta6_p29 manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6_p29 missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p29 index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6_p29 index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "eta6.p29.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_eta6_p29(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
