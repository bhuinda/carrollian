from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_eta6_p5 import (
        DERIVE_SCRIPT,
        EXT_COLUMNS,
        F4_REPORT,
        F4_TABLES,
        FACE_COLUMNS,
        FUSION_REPORT,
        FUSION_TENSOR,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PENTAGON_REPORT,
        REGISTRY_REPORT,
        SOURCE_TARGET,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_eta6_p5 import (
        DERIVE_SCRIPT,
        EXT_COLUMNS,
        F4_REPORT,
        F4_TABLES,
        FACE_COLUMNS,
        FUSION_REPORT,
        FUSION_TENSOR,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PENTAGON_REPORT,
        REGISTRY_REPORT,
        SOURCE_TARGET,
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


def validate_eta6_p5() -> dict[str, Any]:
    expected = build_payloads()
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    p5 = load_json(OUT_DIR / "p5.json")
    cert = load_json(OUT_DIR / "cert.json")
    ext_csv = (OUT_DIR / "ext.csv").read_text(encoding="utf-8")
    face_csv = (OUT_DIR / "face.csv").read_text(encoding="utf-8")
    obs_csv = (OUT_DIR / "obs.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    index = load_json(INDEX_PATH)

    if p5 != expected["p5"]:
        raise AssertionError("eta6_p5 JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("eta6_p5 cert mismatch")
    if ext_csv != expected["ext_csv"]:
        raise AssertionError("eta6_p5 ext CSV mismatch")
    if face_csv != expected["face_csv"]:
        raise AssertionError("eta6_p5 face CSV mismatch")
    if obs_csv != expected["obs_csv"]:
        raise AssertionError("eta6_p5 obs CSV mismatch")
    if not np.array_equal(np.asarray(tables["ext_table"]), expected["ext_table"]):
        raise AssertionError("eta6_p5 ext table mismatch")
    if not np.array_equal(np.asarray(tables["face_table"]), expected["face_table"]):
        raise AssertionError("eta6_p5 face table mismatch")
    if not np.array_equal(
        np.asarray(tables["observable_table"]),
        expected["obs_table"],
    ):
        raise AssertionError("eta6_p5 observable table mismatch")

    if report.get("schema") != "eta6.p5.report@1":
        raise AssertionError("eta6_p5 report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6_p5 report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6_p5 all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6_p5 checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p5 report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6_p5 report hash mismatch")

    ext_table = np.asarray(tables["ext_table"], dtype=np.int64)
    face_table = np.asarray(tables["face_table"], dtype=np.int64)
    obs_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(ext_table.shape) != (144, len(EXT_COLUMNS)):
        raise AssertionError("eta6_p5 ext table shape mismatch")
    if tuple(face_table.shape) != (3, len(FACE_COLUMNS)):
        raise AssertionError("eta6_p5 face table shape mismatch")
    if tuple(obs_table.shape) != (len(OBS_CODES), len(OBS_COLUMNS)):
        raise AssertionError("eta6_p5 obs table shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(obs_table, OBS_COLUMNS)
    }
    required = {
        "fused_face_count": 3,
        "f4_order_count": 72,
        "p5_extension_count": 144,
        "complement_extensions_per_order": 2,
        "mult_equal_extension_count": 144,
        "support_equal_extension_count": 0,
        "support_unique_five_count": 144,
        "eta6_preserved_extension_count": 144,
        "min_support_spread": 11213312,
        "max_support_spread": 633114624,
        "min_spread_count": 2,
        "max_spread_count": 2,
        "total_mult_p0": 145542610944,
        "total_mult_p1": 145542610944,
        "total_mult_p2": 145542610944,
        "total_mult_p3": 145542610944,
        "total_mult_p4": 145542610944,
        "total_support_p0": 23211650672,
        "total_support_p1": 23211650672,
        "total_support_p2": 26519023584,
        "total_support_p3": 26519023584,
        "total_support_p4": 29718149184,
        "p5_multiplicity_flag": 1,
        "p5_raw_support_obstruction_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"eta6_p5 observable {key} mismatch")

    witness = report.get("witness", {})
    if witness.get("classification") != "pentagon_multiplicity_pass_support_obstruction":
        raise AssertionError("eta6_p5 classification mismatch")
    if witness.get("p5_extension_count") != 144:
        raise AssertionError("eta6_p5 extension count mismatch")
    if witness.get("total_multiplicity_by_parenthesization") != [145542610944] * 5:
        raise AssertionError("eta6_p5 total multiplicity mismatch")
    if witness.get("total_support_by_parenthesization") != [
        23211650672,
        23211650672,
        26519023584,
        26519023584,
        29718149184,
    ]:
        raise AssertionError("eta6_p5 total support mismatch")
    if witness.get("min_support_spread") != 11213312:
        raise AssertionError("eta6_p5 min support spread mismatch")
    if witness.get("max_support_spread") != 633114624:
        raise AssertionError("eta6_p5 max support spread mismatch")
    best = witness.get("best_extensions", [])
    if not best or best[0].get("p5_id") != 14:
        raise AssertionError("eta6_p5 best extension mismatch")
    if best[0].get("support_spread") != 11213312:
        raise AssertionError("eta6_p5 best spread mismatch")
    if ext_csv.splitlines()[0].split(",") != EXT_COLUMNS:
        raise AssertionError("eta6_p5 ext header mismatch")
    if face_csv.splitlines()[0].split(",") != FACE_COLUMNS:
        raise AssertionError("eta6_p5 face header mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("f4_report", {}), F4_REPORT, "f4 report")
    assert_file_hash(inputs.get("f4_tables", {}), F4_TABLES, "f4 tables")
    assert_file_hash(
        inputs.get("typed_registry_report", {}),
        REGISTRY_REPORT,
        "registry report",
    )
    assert_file_hash(inputs.get("source_target", {}), SOURCE_TARGET, "source target")
    assert_file_hash(inputs.get("fusion_report", {}), FUSION_REPORT, "fusion report")
    assert_file_hash(inputs.get("fusion_tensor", {}), FUSION_TENSOR, "fusion tensor")
    assert_file_hash(
        inputs.get("pentagon_report", {}),
        PENTAGON_REPORT,
        "pentagon report",
    )
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "eta6.p5.manifest@1":
        raise AssertionError("eta6_p5 manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p5 manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("eta6_p5 manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6_p5 missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p5 index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6_p5 index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "eta6.p5.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_eta6_p5(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
