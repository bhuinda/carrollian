from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_eta6_f4 import (
        ASSOC_REPORT,
        DERIVE_SCRIPT,
        FACE_COLUMNS,
        FUSION_REPORT,
        FUSION_TENSOR,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        ORDER_COLUMNS,
        OUT_DIR,
        REGISTRY_REPORT,
        SAMPLE_COLUMNS,
        SOURCE_TARGET,
        STATUS,
        T2_REPORT,
        T2_TABLES,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_eta6_f4 import (
        ASSOC_REPORT,
        DERIVE_SCRIPT,
        FACE_COLUMNS,
        FUSION_REPORT,
        FUSION_TENSOR,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        ORDER_COLUMNS,
        OUT_DIR,
        REGISTRY_REPORT,
        SAMPLE_COLUMNS,
        SOURCE_TARGET,
        STATUS,
        T2_REPORT,
        T2_TABLES,
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


def validate_eta6_f4() -> dict[str, Any]:
    expected = build_payloads()
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    f4 = load_json(OUT_DIR / "f4.json")
    cert = load_json(OUT_DIR / "cert.json")
    ord_csv = (OUT_DIR / "ord.csv").read_text(encoding="utf-8")
    face_csv = (OUT_DIR / "face.csv").read_text(encoding="utf-8")
    samp_csv = (OUT_DIR / "samp.csv").read_text(encoding="utf-8")
    obs_csv = (OUT_DIR / "obs.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    index = load_json(INDEX_PATH)

    if f4 != expected["f4"]:
        raise AssertionError("eta6_f4 JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("eta6_f4 cert mismatch")
    if ord_csv != expected["ord_csv"]:
        raise AssertionError("eta6_f4 ord CSV mismatch")
    if face_csv != expected["face_csv"]:
        raise AssertionError("eta6_f4 face CSV mismatch")
    if samp_csv != expected["samp_csv"]:
        raise AssertionError("eta6_f4 samp CSV mismatch")
    if obs_csv != expected["obs_csv"]:
        raise AssertionError("eta6_f4 obs CSV mismatch")
    if not np.array_equal(np.asarray(tables["order_table"]), expected["order_table"]):
        raise AssertionError("eta6_f4 order table mismatch")
    if not np.array_equal(np.asarray(tables["face_table"]), expected["face_table"]):
        raise AssertionError("eta6_f4 face table mismatch")
    if not np.array_equal(np.asarray(tables["sample_table"]), expected["sample_table"]):
        raise AssertionError("eta6_f4 sample table mismatch")
    if not np.array_equal(
        np.asarray(tables["observable_table"]),
        expected["obs_table"],
    ):
        raise AssertionError("eta6_f4 observable table mismatch")

    if report.get("schema") != "eta6.f4.report@1":
        raise AssertionError("eta6_f4 report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6_f4 report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6_f4 all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6_f4 checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_f4 report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6_f4 report hash mismatch")

    order_table = np.asarray(tables["order_table"], dtype=np.int64)
    face_table = np.asarray(tables["face_table"], dtype=np.int64)
    sample_table = np.asarray(tables["sample_table"], dtype=np.int64)
    obs_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(order_table.shape) != (72, len(ORDER_COLUMNS)):
        raise AssertionError("eta6_f4 order table shape mismatch")
    if tuple(face_table.shape) != (3, len(FACE_COLUMNS)):
        raise AssertionError("eta6_f4 face table shape mismatch")
    if tuple(sample_table.shape) != (72, len(SAMPLE_COLUMNS)):
        raise AssertionError("eta6_f4 sample table shape mismatch")
    if tuple(obs_table.shape) != (len(OBS_CODES), len(OBS_COLUMNS)):
        raise AssertionError("eta6_f4 obs table shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(obs_table, OBS_COLUMNS)
    }
    required = {
        "fused_face_count": 3,
        "ordered_quad_count": 72,
        "positive_order_count": 72,
        "ordered_mult_match_count": 72,
        "ordered_support_match_count": 0,
        "face_support_sum_match_count": 3,
        "face_mult_sum_match_count": 3,
        "left_support_total": 56729616,
        "right_support_total": 56729616,
        "left_mult_total": 213172224,
        "right_mult_total": 213172224,
        "min_order_support": 59904,
        "min_order_mult": 884736,
        "raw_support_pointwise_obstruction_flag": 1,
        "multiplicity_f_address_flag": 1,
        "sym_support_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"eta6_f4 observable {key} mismatch")

    witness = report.get("witness", {})
    if witness.get("classification") != "multiplicity_balanced_sym_support":
        raise AssertionError("eta6_f4 classification mismatch")
    if witness.get("fused_face_masks") != [30, 45, 51]:
        raise AssertionError("eta6_f4 fused masks mismatch")
    if witness.get("fused_face_ids") != [12, 22, 26]:
        raise AssertionError("eta6_f4 fused face ids mismatch")
    if witness.get("ordered_quadruples") != 72:
        raise AssertionError("eta6_f4 ordered quadruple count mismatch")
    if witness.get("ordered_support_match_count") != 0:
        raise AssertionError("eta6_f4 ordered support match count mismatch")
    if witness.get("ordered_mult_match_count") != 72:
        raise AssertionError("eta6_f4 ordered multiplicity match count mismatch")
    if witness.get("face_support_sums") != [
        {"face_id": 12, "label_mask": 30, "left": 3360512, "right": 3360512},
        {"face_id": 22, "label_mask": 45, "left": 28257280, "right": 28257280},
        {"face_id": 26, "label_mask": 51, "left": 25111824, "right": 25111824},
    ]:
        raise AssertionError("eta6_f4 face support sums mismatch")
    if witness.get("face_mult_sums") != [
        {"face_id": 12, "label_mask": 30, "left": 27967488, "right": 27967488},
        {"face_id": 22, "label_mask": 45, "left": 93192192, "right": 93192192},
        {"face_id": 26, "label_mask": 51, "left": 92012544, "right": 92012544},
    ]:
        raise AssertionError("eta6_f4 face multiplicity sums mismatch")
    if ord_csv.splitlines()[0].split(",") != ORDER_COLUMNS:
        raise AssertionError("eta6_f4 ord header mismatch")
    if face_csv.splitlines()[0].split(",") != FACE_COLUMNS:
        raise AssertionError("eta6_f4 face header mismatch")
    if samp_csv.splitlines()[0].split(",") != SAMPLE_COLUMNS:
        raise AssertionError("eta6_f4 samp header mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("t2_report", {}), T2_REPORT, "t2 report")
    assert_file_hash(inputs.get("t2_tables", {}), T2_TABLES, "t2 tables")
    assert_file_hash(
        inputs.get("typed_registry_report", {}),
        REGISTRY_REPORT,
        "registry report",
    )
    assert_file_hash(inputs.get("source_target", {}), SOURCE_TARGET, "source target")
    assert_file_hash(inputs.get("fusion_report", {}), FUSION_REPORT, "fusion report")
    assert_file_hash(inputs.get("fusion_tensor", {}), FUSION_TENSOR, "fusion tensor")
    assert_file_hash(
        inputs.get("associator_report", {}),
        ASSOC_REPORT,
        "associator report",
    )
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "eta6.f4.manifest@1":
        raise AssertionError("eta6_f4 manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_f4 manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("eta6_f4 manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6_f4 missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_f4 index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6_f4 index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "eta6.f4.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_eta6_f4(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
