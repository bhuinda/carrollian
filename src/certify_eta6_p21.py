from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_eta6_p21 import (
        DERIVE_SCRIPT,
        GATE_COLUMNS,
        GAP_REPORT,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        P16_REPORT,
        P20_REPORT,
        P5_TABLES,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_eta6_p21 import (
        DERIVE_SCRIPT,
        GATE_COLUMNS,
        GAP_REPORT,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        P16_REPORT,
        P20_REPORT,
        P5_TABLES,
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


def validate_eta6_p21() -> dict[str, Any]:
    expected = build_payloads()
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    p21 = load_json(OUT_DIR / "p21.json")
    cert = load_json(OUT_DIR / "cert.json")
    gate_csv = (OUT_DIR / "gate.csv").read_text(encoding="utf-8")
    obs_csv = (OUT_DIR / "obs.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    index = load_json(INDEX_PATH)

    if p21 != expected["p21"]:
        raise AssertionError("eta6_p21 JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("eta6_p21 cert mismatch")
    if gate_csv != expected["gate_csv"]:
        raise AssertionError("eta6_p21 gate CSV mismatch")
    if obs_csv != expected["obs_csv"]:
        raise AssertionError("eta6_p21 obs CSV mismatch")
    if not np.array_equal(np.asarray(tables["gate_table"]), expected["gate_table"]):
        raise AssertionError("eta6_p21 gate table mismatch")
    if not np.array_equal(
        np.asarray(tables["observable_table"]),
        expected["obs_table"],
    ):
        raise AssertionError("eta6_p21 observable table mismatch")

    if report.get("schema") != "eta6.p21.report@1":
        raise AssertionError("eta6_p21 report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6_p21 report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6_p21 all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6_p21 checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p21 report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6_p21 report hash mismatch")

    gate_table = np.asarray(tables["gate_table"], dtype=np.int64)
    obs_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(gate_table.shape) != (6, len(GATE_COLUMNS)):
        raise AssertionError("eta6_p21 gate table shape mismatch")
    if tuple(obs_table.shape) != (len(OBS_CODES), len(OBS_COLUMNS)):
        raise AssertionError("eta6_p21 obs table shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(obs_table, OBS_COLUMNS)
    }
    required = {
        "global_floor": 492736,
        "global_at_floor_count": 1,
        "global_below_floor_count": 0,
        "global_equalizer_count": 0,
        "gate_move_count": 6,
        "eta6_preserved_count": 6,
        "balanced_222_flag": 1,
        "total_f4_delta": 0,
        "per_face_abs_delta_sum": 0,
        "carrier_neutral_flag": 1,
        "hpol_min_margin": 1,
        "hpol_min_count": 2,
        "repl_min_margin": 146,
        "checked_margin_positive_flag": 1,
        "rebuilt_carrier_claim_flag": 0,
        "p0_support": 1083830080,
        "p1_support": 1083830080,
        "p2_support": 1084205056,
        "p3_support": 1084205056,
        "p4_support": 1084322816,
        "support_spread": 492736,
        "joint_mult_value": 5877006336,
        "best_p5_a": 1,
        "best_p5_b": 47,
        "best_p5_c": 57,
        "best_p5_d": 79,
        "best_p5_e": 110,
        "best_p5_f": 128,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"eta6_p21 observable {key} mismatch")

    gate_rows = table_rows(gate_table, GATE_COLUMNS)
    if [row["p5_id"] for row in gate_rows] != [1, 47, 57, 79, 110, 128]:
        raise AssertionError("eta6_p21 gate ids mismatch")
    if sum(row["f4_delta"] for row in gate_rows) != 0:
        raise AssertionError("eta6_p21 gate f4 delta mismatch")
    if sum(row["eta6_preserved_flag"] for row in gate_rows) != 6:
        raise AssertionError("eta6_p21 eta6 preservation mismatch")

    witness = report.get("witness", {})
    if witness.get("classification") != "exact_floor_surgery_gate":
        raise AssertionError("eta6_p21 classification mismatch")
    if witness.get("gate_p5_ids") != [1, 47, 57, 79, 110, 128]:
        raise AssertionError("eta6_p21 witness gate ids mismatch")
    if witness.get("checked_margins", {}).get("rebuilt_carrier_claim") != 0:
        raise AssertionError("eta6_p21 rebuilt carrier boundary mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("p5_tables", {}), P5_TABLES, "p5 tables")
    assert_file_hash(inputs.get("p16_report", {}), P16_REPORT, "p16 report")
    assert_file_hash(inputs.get("p20_report", {}), P20_REPORT, "p20 report")
    assert_file_hash(inputs.get("gap_report", {}), GAP_REPORT, "gap report")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "eta6.p21.manifest@1":
        raise AssertionError("eta6_p21 manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p21 manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("eta6_p21 manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6_p21 missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p21 index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6_p21 index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "eta6.p21.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_eta6_p21(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
