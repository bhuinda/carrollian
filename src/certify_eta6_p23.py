from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_eta6_p23 import (
        DERIVE_SCRIPT,
        FACE_COLUMNS,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        P22_REPORT,
        P2_FACES,
        P2_REPORT,
        P2_SUPP,
        P2_VERTS,
        STATUS,
        T2_FUSE,
        T2_REPORT,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_eta6_p23 import (
        DERIVE_SCRIPT,
        FACE_COLUMNS,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        P22_REPORT,
        P2_FACES,
        P2_REPORT,
        P2_SUPP,
        P2_VERTS,
        STATUS,
        T2_FUSE,
        T2_REPORT,
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


def validate_eta6_p23() -> dict[str, Any]:
    expected = build_payloads()
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    p23 = load_json(OUT_DIR / "p23.json")
    cert = load_json(OUT_DIR / "cert.json")
    faces_csv = (OUT_DIR / "faces.csv").read_text(encoding="utf-8")
    obs_csv = (OUT_DIR / "obs.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    index = load_json(INDEX_PATH)

    if p23 != expected["p23"]:
        raise AssertionError("eta6_p23 JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("eta6_p23 cert mismatch")
    if faces_csv != expected["faces_csv"]:
        raise AssertionError("eta6_p23 faces CSV mismatch")
    if obs_csv != expected["obs_csv"]:
        raise AssertionError("eta6_p23 obs CSV mismatch")
    if not np.array_equal(np.asarray(tables["face_table"]), expected["face_table"]):
        raise AssertionError("eta6_p23 face table mismatch")
    if not np.array_equal(
        np.asarray(tables["observable_table"]),
        expected["obs_table"],
    ):
        raise AssertionError("eta6_p23 observable table mismatch")

    if report.get("schema") != "eta6.p23.report@1":
        raise AssertionError("eta6_p23 report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6_p23 report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6_p23 all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6_p23 checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p23 report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6_p23 report hash mismatch")

    face_table = np.asarray(tables["face_table"], dtype=np.int64)
    obs_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(face_table.shape) != (3, len(FACE_COLUMNS)):
        raise AssertionError("eta6_p23 face table shape mismatch")
    if tuple(obs_table.shape) != (len(OBS_CODES), len(OBS_COLUMNS)):
        raise AssertionError("eta6_p23 obs table shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(obs_table, OBS_COLUMNS)
    }
    required = {
        "lift_face_count": 3,
        "quadrilateral_face_count": 3,
        "fused_kind_count": 3,
        "unique_vertex_count": 9,
        "hit_vertex_count": 3,
        "support_row_count": 132,
        "support_positive_count": 132,
        "support_zero_count": 0,
        "min_slack_x1e12": 363262450397,
        "max_slack_x1e12": 2602092146127,
        "p2_positive_support_flag": 1,
        "p22_symbolic_carrier_flag": 1,
        "geometric_lift_flag": 1,
        "new_c985_recompute_flag": 0,
        "face12_label_mask": 30,
        "face22_label_mask": 45,
        "face26_label_mask": 51,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"eta6_p23 observable {key} mismatch")

    face_rows = table_rows(face_table, FACE_COLUMNS)
    expected_faces = [
        (12, 30, [13, 14, 47, 46], [13, 14, 55, 52]),
        (22, 45, [28, 29, 46, 40], [28, 29, 52, 41]),
        (26, 51, [40, 44, 45, 47], [41, 48, 49, 55]),
    ]
    actual_faces = [
        (
            row["face_id"],
            row["label_mask"],
            [row["cycle_v0"], row["cycle_v1"], row["cycle_v2"], row["cycle_v3"]],
            [row["orig_v0"], row["orig_v1"], row["orig_v2"], row["orig_v3"]],
        )
        for row in face_rows
    ]
    if actual_faces != expected_faces:
        raise AssertionError("eta6_p23 lifted face mismatch")
    if any(row["kind_code"] != 2 or row["face_size"] != 4 for row in face_rows):
        raise AssertionError("eta6_p23 face kind mismatch")

    witness = report.get("witness", {})
    if witness.get("classification") != "symbolic_to_geometric_face_lift":
        raise AssertionError("eta6_p23 classification mismatch")
    if witness.get("claim_boundary", {}).get("new_c985_recompute") != 0:
        raise AssertionError("eta6_p23 C985 boundary mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("p2_report", {}), P2_REPORT, "p2 report")
    assert_file_hash(inputs.get("p2_faces", {}), P2_FACES, "p2 faces")
    assert_file_hash(inputs.get("p2_verts", {}), P2_VERTS, "p2 verts")
    assert_file_hash(inputs.get("p2_supp", {}), P2_SUPP, "p2 supp")
    assert_file_hash(inputs.get("t2_report", {}), T2_REPORT, "t2 report")
    assert_file_hash(inputs.get("t2_fuse", {}), T2_FUSE, "t2 fuse")
    assert_file_hash(inputs.get("p22_report", {}), P22_REPORT, "p22 report")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "eta6.p23.manifest@1":
        raise AssertionError("eta6_p23 manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p23 manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("eta6_p23 manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6_p23 missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p23 index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6_p23 index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "eta6.p23.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_eta6_p23(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
