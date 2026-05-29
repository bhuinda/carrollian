from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_eta6_core import (
        DERIVE_SCRIPT,
        GAP_REPORT,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        P20_REPORT,
        P21_REPORT,
        P26_REPORT,
        REPORT_CODES,
        SPINE_COLUMNS,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_eta6_core import (
        DERIVE_SCRIPT,
        GAP_REPORT,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        P20_REPORT,
        P21_REPORT,
        P26_REPORT,
        REPORT_CODES,
        SPINE_COLUMNS,
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


def validate_eta6_core() -> dict[str, Any]:
    expected = build_payloads()
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    core = load_json(OUT_DIR / "core.json")
    cert = load_json(OUT_DIR / "cert.json")
    spine_csv = (OUT_DIR / "spine.csv").read_text(encoding="utf-8")
    obs_csv = (OUT_DIR / "obs.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    index = load_json(INDEX_PATH)

    if core != expected["core"]:
        raise AssertionError("eta6_core JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("eta6_core cert mismatch")
    if spine_csv != expected["spine_csv"]:
        raise AssertionError("eta6_core spine CSV mismatch")
    if obs_csv != expected["obs_csv"]:
        raise AssertionError("eta6_core obs CSV mismatch")
    if not np.array_equal(np.asarray(tables["spine_table"]), expected["spine_table"]):
        raise AssertionError("eta6_core spine table mismatch")
    if not np.array_equal(np.asarray(tables["observable_table"]), expected["obs_table"]):
        raise AssertionError("eta6_core observable table mismatch")

    if report.get("schema") != "eta6.core.report@1":
        raise AssertionError("eta6_core report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6_core report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6_core all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6_core checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_core report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6_core report hash mismatch")

    spine_table = np.asarray(tables["spine_table"], dtype=np.int64)
    obs_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(spine_table.shape) != (len(REPORT_CODES), len(SPINE_COLUMNS)):
        raise AssertionError("eta6_core spine table shape mismatch")
    if tuple(obs_table.shape) != (len(OBS_CODES), len(OBS_COLUMNS)):
        raise AssertionError("eta6_core obs table shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(obs_table, OBS_COLUMNS)
    }
    required = {
        "spine_report_count": 4,
        "certified_spine_count": 4,
        "input_certificates_ok": 1,
        "hpol_margin": 1,
        "hpol_row_count": 4_903_515,
        "hpol_min_count": 2,
        "hpol_zero_count": 0,
        "gordan_no_positive_annihilator_flag": 1,
        "replacement_margin": 146,
        "replacement_row_count": 2_831_367,
        "global_six_floor": 492_736,
        "global_six_count": 11_143_364_232,
        "global_at_floor_count": 1,
        "global_below_floor_count": 0,
        "global_support_equal_count": 0,
        "gate_floor": 492_736,
        "gate_carrier_neutral": 1,
        "gate_eta6_preserved_count": 6,
        "gate_rebuilt_claim": 0,
        "packet_component_count": 4,
        "packet_positive_row_total": 7_735_158,
        "packet_min_margin": 1,
        "packet_support_equalizer_absent": 1,
        "best_ids_agree_flag": 1,
        "bounded_horizon_flag": 1,
        "universal_completion_claim": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"eta6_core observable {key} mismatch")

    witness = report.get("witness", {})
    if witness.get("classification") != "eta6_core":
        raise AssertionError("eta6_core classification mismatch")
    if witness.get("core_claim") != "bounded_horizon":
        raise AssertionError("eta6_core claim mismatch")
    if witness.get("best_p5_ids") != [1, 47, 57, 79, 110, 128]:
        raise AssertionError("eta6_core best ids mismatch")
    if witness.get("gordan_gap", {}).get("hpol_margin") != 1:
        raise AssertionError("eta6_core hpol margin mismatch")
    if witness.get("six_floor", {}).get("floor") != 492_736:
        raise AssertionError("eta6_core six floor mismatch")
    if witness.get("gate", {}).get("carrier_neutral") != 1:
        raise AssertionError("eta6_core gate mismatch")
    if witness.get("margin_packet", {}).get("min_margin") != 1:
        raise AssertionError("eta6_core packet margin mismatch")
    boundary = witness.get("claim_boundary", {})
    if boundary.get("bounded_horizon_flag") != 1:
        raise AssertionError("eta6_core bounded flag mismatch")
    if boundary.get("universal_completion_claim") != 0:
        raise AssertionError("eta6_core universal boundary mismatch")
    if spine_csv.splitlines()[0].split(",") != SPINE_COLUMNS:
        raise AssertionError("eta6_core spine header mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "gap_report": GAP_REPORT,
        "p20_report": P20_REPORT,
        "p21_report": P21_REPORT,
        "p26_report": P26_REPORT,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "eta6.core.manifest@1":
        raise AssertionError("eta6_core manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_core manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("eta6_core manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6_core missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_core index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6_core index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "eta6.core.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_eta6_core(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
