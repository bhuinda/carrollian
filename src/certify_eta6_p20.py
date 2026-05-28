from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_eta6_p20 import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        P17_REPORT,
        P19_OBS,
        P19_REPORT,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_eta6_p20 import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        P17_REPORT,
        P19_OBS,
        P19_REPORT,
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


def validate_eta6_p20() -> dict[str, Any]:
    expected = build_payloads()
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    p20 = load_json(OUT_DIR / "p20.json")
    cert = load_json(OUT_DIR / "cert.json")
    obs_csv = (OUT_DIR / "obs.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    index = load_json(INDEX_PATH)

    if p20 != expected["p20"]:
        raise AssertionError("eta6_p20 JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("eta6_p20 cert mismatch")
    if obs_csv != expected["obs_csv"]:
        raise AssertionError("eta6_p20 obs CSV mismatch")
    if not np.array_equal(
        np.asarray(tables["observable_table"]),
        expected["obs_table"],
    ):
        raise AssertionError("eta6_p20 observable table mismatch")

    if report.get("schema") != "eta6.p20.report@1":
        raise AssertionError("eta6_p20 report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6_p20 report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6_p20 all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6_p20 checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p20 report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6_p20 report hash mismatch")

    obs_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(obs_table.shape) != (len(OBS_CODES), len(OBS_COLUMNS)):
        raise AssertionError("eta6_p20 obs table shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(obs_table, OBS_COLUMNS)
    }
    required = {
        "full_six_count": 11143364232,
        "exact_222_count": 1435249152,
        "outside_count": 9708115080,
        "p5_floor": 11213312,
        "p14_floor": 1164096,
        "p15_floor": 492736,
        "p19_cell_width": 33554432,
        "capture_margin": 22341120,
        "capture_applies_flag": 1,
        "inside_min_spread": 492736,
        "outside_min_spread": 1164096,
        "global_min_spread": 492736,
        "inside_below_p15_count": 0,
        "inside_at_p15_count": 1,
        "outside_below_p15_count": 0,
        "outside_below_p14_count": 0,
        "global_below_min_count": 0,
        "global_at_min_count": 1,
        "global_support_equal_count": 0,
        "best_p5_a": 1,
        "best_p5_b": 47,
        "best_p5_c": 57,
        "best_p5_d": 79,
        "best_p5_e": 110,
        "best_p5_f": 128,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"eta6_p20 observable {key} mismatch")

    witness = report.get("witness", {})
    if witness.get("classification") != "global_six_move_floor_by_cell_capture":
        raise AssertionError("eta6_p20 classification mismatch")
    if witness.get("global_min_spread") != 492736:
        raise AssertionError("eta6_p20 global min mismatch")
    if witness.get("best_p5_ids") != [1, 47, 57, 79, 110, 128]:
        raise AssertionError("eta6_p20 best p5 ids mismatch")
    if witness.get("global_support_equal_count") != 0:
        raise AssertionError("eta6_p20 equalizer count mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("p17_report", {}), P17_REPORT, "p17 report")
    assert_file_hash(inputs.get("p19_report", {}), P19_REPORT, "p19 report")
    assert_file_hash(inputs.get("p19_obs", {}), P19_OBS, "p19 obs")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "eta6.p20.manifest@1":
        raise AssertionError("eta6_p20 manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p20 manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("eta6_p20 manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6_p20 missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p20 index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6_p20 index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "eta6.p20.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_eta6_p20(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
