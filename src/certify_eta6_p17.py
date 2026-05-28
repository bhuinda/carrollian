from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_eta6_p17 import (
        CLASS_COLUMNS,
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
        P11_REPORT,
        P15_REPORT,
        P16_REPORT,
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
    from derive_eta6_p17 import (
        CLASS_COLUMNS,
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
        P11_REPORT,
        P15_REPORT,
        P16_REPORT,
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


def validate_eta6_p17() -> dict[str, Any]:
    expected = build_payloads()
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    p17 = load_json(OUT_DIR / "p17.json")
    cert = load_json(OUT_DIR / "cert.json")
    top_csv = (OUT_DIR / "top.csv").read_text(encoding="utf-8")
    class_csv = (OUT_DIR / "class.csv").read_text(encoding="utf-8")
    obs_csv = (OUT_DIR / "obs.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    index = load_json(INDEX_PATH)

    if p17 != expected["p17"]:
        raise AssertionError("eta6_p17 JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("eta6_p17 cert mismatch")
    if top_csv != expected["top_csv"]:
        raise AssertionError("eta6_p17 top CSV mismatch")
    if class_csv != expected["class_csv"]:
        raise AssertionError("eta6_p17 class CSV mismatch")
    if obs_csv != expected["obs_csv"]:
        raise AssertionError("eta6_p17 obs CSV mismatch")
    if not np.array_equal(np.asarray(tables["top_table"]), expected["top_table"]):
        raise AssertionError("eta6_p17 top table mismatch")
    if not np.array_equal(np.asarray(tables["class_table"]), expected["class_table"]):
        raise AssertionError("eta6_p17 class table mismatch")
    if not np.array_equal(
        np.asarray(tables["observable_table"]),
        expected["obs_table"],
    ):
        raise AssertionError("eta6_p17 observable table mismatch")

    if report.get("schema") != "eta6.p17.report@1":
        raise AssertionError("eta6_p17 report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6_p17 report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6_p17 all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6_p17 checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p17 report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6_p17 report hash mismatch")

    top_table = np.asarray(tables["top_table"], dtype=np.int64)
    class_table = np.asarray(tables["class_table"], dtype=np.int64)
    obs_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(top_table.shape) != (TOP_N, len(TOP_COLUMNS)):
        raise AssertionError("eta6_p17 top table shape mismatch")
    if tuple(class_table.shape) != (3, len(CLASS_COLUMNS)):
        raise AssertionError("eta6_p17 class table shape mismatch")
    if tuple(obs_table.shape) != (len(OBS_CODES), len(OBS_COLUMNS)):
        raise AssertionError("eta6_p17 obs table shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(obs_table, OBS_COLUMNS)
    }
    required = {
        "class_count": 3,
        "moves_per_class": 48,
        "pairs_per_class": 1128,
        "balance_candidate_count": 1435249152,
        "p5_single_floor": 11213312,
        "p6_pair_floor": 10515968,
        "p7_triple_floor": 2601984,
        "p8_quad_floor": 2447744,
        "p11_quint_floor": 1815040,
        "p14_basin_six_floor": 1164096,
        "p15_grid_floor": 492736,
        "balance_min_spread": 492736,
        "balance_min_equal_p15_flag": 1,
        "below_p15_candidate_count": 0,
        "at_p15_floor_candidate_count": 1,
        "below_p14_candidate_count": 1,
        "below_p11_candidate_count": 1,
        "below_p8_candidate_count": 3,
        "below_p7_candidate_count": 3,
        "below_p6_candidate_count": 2240,
        "below_p5_candidate_count": 2929,
        "support_equal_candidate_count": 0,
        "total_delta_zero_candidate_count": 7077888,
        "per_face_delta_zero_candidate_count": 7077888,
        "best_p17_id": 117520136,
        "best_p5_a": 1,
        "best_p5_b": 47,
        "best_p5_c": 57,
        "best_p5_d": 79,
        "best_p5_e": 110,
        "best_p5_f": 128,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"eta6_p17 observable {key} mismatch")

    best = table_rows(top_table, TOP_COLUMNS)[0]
    if best["p17_id"] != 117520136:
        raise AssertionError("eta6_p17 best id mismatch")
    if [best[f"p5_{letter}"] for letter in "abcdef"] != [1, 47, 57, 79, 110, 128]:
        raise AssertionError("eta6_p17 best p5 ids mismatch")
    if best["joint_support_spread"] != 492736:
        raise AssertionError("eta6_p17 best spread mismatch")
    if best["per_face_delta_zero_flag"] != 1:
        raise AssertionError("eta6_p17 best per-face delta flag mismatch")
    if top_csv.splitlines()[0].split(",") != TOP_COLUMNS:
        raise AssertionError("eta6_p17 top header mismatch")
    if class_csv.splitlines()[0].split(",") != CLASS_COLUMNS:
        raise AssertionError("eta6_p17 class header mismatch")

    witness = report.get("witness", {})
    if witness.get("classification") != "exact_222_face_mask_balance_class":
        raise AssertionError("eta6_p17 classification mismatch")
    if witness.get("balance_min_spread") != 492736:
        raise AssertionError("eta6_p17 min spread mismatch")
    if witness.get("below_p15_candidate_count") != 0:
        raise AssertionError("eta6_p17 below-p15 count mismatch")
    if witness.get("support_equal_candidate_count") != 0:
        raise AssertionError("eta6_p17 support equal count mismatch")
    if witness.get("best_candidates", [{}])[0].get("p5_ids") != [1, 47, 57, 79, 110, 128]:
        raise AssertionError("eta6_p17 witness best ids mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("p5_report", {}), P5_REPORT, "p5 report")
    assert_file_hash(inputs.get("p5_tables", {}), P5_TABLES, "p5 tables")
    assert_file_hash(inputs.get("p6_report", {}), P6_REPORT, "p6 report")
    assert_file_hash(inputs.get("p7_report", {}), P7_REPORT, "p7 report")
    assert_file_hash(inputs.get("p8_report", {}), P8_REPORT, "p8 report")
    assert_file_hash(inputs.get("p11_report", {}), P11_REPORT, "p11 report")
    assert_file_hash(inputs.get("p15_report", {}), P15_REPORT, "p15 report")
    assert_file_hash(inputs.get("p16_report", {}), P16_REPORT, "p16 report")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "eta6.p17.manifest@1":
        raise AssertionError("eta6_p17 manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p17 manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("eta6_p17 manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6_p17 missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p17 index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6_p17 index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "eta6.p17.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_eta6_p17(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
