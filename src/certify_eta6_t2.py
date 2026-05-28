from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_eta6_t2 import (
        DERIVE_SCRIPT,
        FUSE_COLUMNS,
        HOL_REPORT,
        LABEL_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        P2_FACES,
        P2_REPORT,
        P2_VERTS,
        STATUS,
        THEOREM_ID,
        TRUNCATED_TABLES,
        VALIDATOR_SCRIPT,
        XFER_REPORT,
        build_payloads,
        p2,
        pair,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_eta6_t2 import (
        DERIVE_SCRIPT,
        FUSE_COLUMNS,
        HOL_REPORT,
        LABEL_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        P2_FACES,
        P2_REPORT,
        P2_VERTS,
        STATUS,
        THEOREM_ID,
        TRUNCATED_TABLES,
        VALIDATOR_SCRIPT,
        XFER_REPORT,
        build_payloads,
        p2,
        pair,
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


def validate_eta6_t2() -> dict[str, Any]:
    expected = build_payloads()
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    t2 = load_json(OUT_DIR / "t2.json")
    cert = load_json(OUT_DIR / "cert.json")
    fuse_csv = (OUT_DIR / "fuse.csv").read_text(encoding="utf-8")
    labels_csv = (OUT_DIR / "labels.csv").read_text(encoding="utf-8")
    obs_csv = (OUT_DIR / "obs.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    index = load_json(p2.repl.ext.nonholonomic.preservation.INDEX_PATH)

    if t2 != expected["t2"]:
        raise AssertionError("eta6_t2 JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("eta6_t2 cert mismatch")
    if fuse_csv != expected["fuse_csv"]:
        raise AssertionError("eta6_t2 fuse CSV mismatch")
    if labels_csv != expected["labels_csv"]:
        raise AssertionError("eta6_t2 labels CSV mismatch")
    if obs_csv != expected["obs_csv"]:
        raise AssertionError("eta6_t2 obs CSV mismatch")
    if not np.array_equal(np.asarray(tables["fuse_table"]), expected["fuse_table"]):
        raise AssertionError("eta6_t2 fuse table mismatch")
    if not np.array_equal(np.asarray(tables["label_table"]), expected["label_table"]):
        raise AssertionError("eta6_t2 label table mismatch")
    if not np.array_equal(
        np.asarray(tables["observable_table"]),
        expected["obs_table"],
    ):
        raise AssertionError("eta6_t2 observable table mismatch")

    if report.get("schema") != "eta6.t2.report@1":
        raise AssertionError("eta6_t2 report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6_t2 report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6_t2 all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6_t2 checks mismatch")
    if pair.parent.self_hash(report, "certificate_sha256") != report.get(
        "certificate_sha256"
    ):
        raise AssertionError("eta6_t2 report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6_t2 report hash mismatch")

    fuse_table = np.asarray(tables["fuse_table"], dtype=np.int64)
    label_table = np.asarray(tables["label_table"], dtype=np.int64)
    obs_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(fuse_table.shape) != (3, len(FUSE_COLUMNS)):
        raise AssertionError("eta6_t2 fuse table shape mismatch")
    if tuple(label_table.shape) != (6, len(LABEL_COLUMNS)):
        raise AssertionError("eta6_t2 label table shape mismatch")
    if tuple(obs_table.shape) != (len(OBS_CODES), len(OBS_COLUMNS)):
        raise AssertionError("eta6_t2 obs table shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(obs_table, OBS_COLUMNS)
    }
    required = {
        "face_count": 29,
        "known_face_count": 26,
        "fused_face_count": 3,
        "known_label_count_min": 10,
        "known_label_count_max": 10,
        "target_label_count": 12,
        "fused_label_size": 4,
        "candidate_assignment_count": 90,
        "best_assignment_count": 1,
        "best_score": 57,
        "total_label_count_min": 12,
        "total_label_count_max": 12,
        "label_counts_preserved_flag": 1,
        "eta_weight": 6,
        "holonomy_weight": 3,
        "holonomy_eta_pairing": 1,
        "noncubic_transfer_flag": 1,
        "transfer_obstruction_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"eta6_t2 observable {key} mismatch")

    witness = report.get("witness", {})
    if witness.get("classification") != "noncubic_transfer_exists":
        raise AssertionError("eta6_t2 classification mismatch")
    if witness.get("fused_face_masks") != [30, 45, 51]:
        raise AssertionError("eta6_t2 fused masks mismatch")
    if witness.get("fused_face_ids") != [12, 22, 26]:
        raise AssertionError("eta6_t2 fused face ids mismatch")
    if witness.get("label_counts") != [12, 12, 12, 12, 12, 12]:
        raise AssertionError("eta6_t2 label counts mismatch")
    if witness.get("holonomy_eta_pairing_after") != 1:
        raise AssertionError("eta6_t2 pairing mismatch")
    if fuse_csv.splitlines()[0].split(",") != FUSE_COLUMNS:
        raise AssertionError("eta6_t2 fuse header mismatch")
    if labels_csv.splitlines()[0].split(",") != LABEL_COLUMNS:
        raise AssertionError("eta6_t2 label header mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("p2_report", {}), P2_REPORT, "p2 report")
    assert_file_hash(inputs.get("xfer_report", {}), XFER_REPORT, "xfer report")
    assert_file_hash(inputs.get("holonomy_report", {}), HOL_REPORT, "holonomy report")
    assert_file_hash(inputs.get("p2_faces", {}), P2_FACES, "p2 faces")
    assert_file_hash(inputs.get("p2_verts", {}), P2_VERTS, "p2 verts")
    assert_file_hash(
        inputs.get("truncated_tables", {}),
        TRUNCATED_TABLES,
        "truncated tables",
    )
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "eta6.t2.manifest@1":
        raise AssertionError("eta6_t2 manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_t2 manifest report hash mismatch")
    if pair.parent.self_hash(manifest, "manifest_sha256") != manifest.get(
        "manifest_sha256"
    ):
        raise AssertionError("eta6_t2 manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6_t2 missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_t2 index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6_t2 index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "eta6.t2.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_eta6_t2(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
