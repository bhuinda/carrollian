from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_eta6_repl import (
        C4_COLUMNS,
        DERIVE_SCRIPT,
        EDGE_COLUMNS,
        FACE_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        SAMPLE_COLUMNS,
        SAMPLE_LIMIT,
        STATUS,
        SUPP_COLUMNS,
        SURG_REPORT,
        THEOREM_ID,
        TRUNCATED_REPORT,
        TRUNCATED_TABLES,
        VALIDATOR_SCRIPT,
        VERTEX_COLUMNS,
        build_payloads,
        ext,
        pair,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_eta6_repl import (
        C4_COLUMNS,
        DERIVE_SCRIPT,
        EDGE_COLUMNS,
        FACE_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        SAMPLE_COLUMNS,
        SAMPLE_LIMIT,
        STATUS,
        SUPP_COLUMNS,
        SURG_REPORT,
        THEOREM_ID,
        TRUNCATED_REPORT,
        TRUNCATED_TABLES,
        VALIDATOR_SCRIPT,
        VERTEX_COLUMNS,
        build_payloads,
        ext,
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


def validate_eta6_repl() -> dict[str, Any]:
    expected = build_payloads()
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    repl = load_json(OUT_DIR / "repl.json")
    cert = load_json(OUT_DIR / "cert.json")
    verts_csv = (OUT_DIR / "verts.csv").read_text(encoding="utf-8")
    edges_csv = (OUT_DIR / "edges.csv").read_text(encoding="utf-8")
    faces_csv = (OUT_DIR / "faces.csv").read_text(encoding="utf-8")
    supp_csv = (OUT_DIR / "supp.csv").read_text(encoding="utf-8")
    c4_csv = (OUT_DIR / "c4.csv").read_text(encoding="utf-8")
    samp_csv = (OUT_DIR / "samp.csv").read_text(encoding="utf-8")
    obs_csv = (OUT_DIR / "obs.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    index = load_json(ext.nonholonomic.preservation.INDEX_PATH)

    if repl != expected["repl"]:
        raise AssertionError("eta6_repl JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("eta6_repl cert mismatch")
    if verts_csv != expected["verts_csv"]:
        raise AssertionError("eta6_repl vertices CSV mismatch")
    if edges_csv != expected["edges_csv"]:
        raise AssertionError("eta6_repl edges CSV mismatch")
    if faces_csv != expected["faces_csv"]:
        raise AssertionError("eta6_repl faces CSV mismatch")
    if supp_csv != expected["supp_csv"]:
        raise AssertionError("eta6_repl support CSV mismatch")
    if c4_csv != expected["c4_csv"]:
        raise AssertionError("eta6_repl c4 CSV mismatch")
    if samp_csv != expected["samp_csv"]:
        raise AssertionError("eta6_repl sample CSV mismatch")
    if obs_csv != expected["obs_csv"]:
        raise AssertionError("eta6_repl obs CSV mismatch")

    table_expectations = {
        "vertex_table": expected["vertex_table"],
        "edge_table": expected["edge_table"],
        "face_table": expected["face_table"],
        "support_table": expected["support_table"],
        "c4_table": expected["c4_table"],
        "sample_table": expected["sample_table"],
        "observable_table": expected["obs_table"],
    }
    for name, value in table_expectations.items():
        if not np.array_equal(np.asarray(tables[name]), value):
            raise AssertionError(f"eta6_repl {name} mismatch")

    if report.get("schema") != "eta6.repl.report@1":
        raise AssertionError("eta6_repl report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6_repl report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6_repl all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6_repl checks mismatch")
    if pair.parent.self_hash(report, "certificate_sha256") != report.get(
        "certificate_sha256"
    ):
        raise AssertionError("eta6_repl report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6_repl report hash mismatch")

    obs_table = np.asarray(tables["observable_table"], dtype=np.int64)
    vertex_table = np.asarray(tables["vertex_table"], dtype=np.int64)
    edge_table = np.asarray(tables["edge_table"], dtype=np.int64)
    face_table = np.asarray(tables["face_table"], dtype=np.int64)
    support_table = np.asarray(tables["support_table"], dtype=np.int64)
    c4_table = np.asarray(tables["c4_table"], dtype=np.int64)
    sample_table = np.asarray(tables["sample_table"], dtype=np.int64)
    required_shapes = {
        "vertex": (54, len(VERTEX_COLUMNS), vertex_table),
        "edge": (84, len(EDGE_COLUMNS), edge_table),
        "face": (32, len(FACE_COLUMNS), face_table),
        "support": (1_560, len(SUPP_COLUMNS), support_table),
        "c4": (7_095, len(C4_COLUMNS), c4_table),
        "sample": (SAMPLE_LIMIT, len(SAMPLE_COLUMNS), sample_table),
        "observable": (len(OBS_CODES), len(OBS_COLUMNS), obs_table),
    }
    for label, (rows, cols, table) in required_shapes.items():
        if tuple(table.shape) != (rows, cols):
            raise AssertionError(f"eta6_repl {label} table shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(obs_table, OBS_COLUMNS)
    }
    required = {
        "vertex_count": 54,
        "removed_vertex_count": 6,
        "edge_count": 84,
        "face_count": 32,
        "triangle_face_count": 3,
        "quadrilateral_face_count": 3,
        "pentagon_face_count": 9,
        "hexagon_face_count": 17,
        "euler_characteristic": 2,
        "connected_flag": 1,
        "three_vertex_connected_flag": 1,
        "edge_two_face_incidence_flag": 1,
        "support_row_count": 1_560,
        "support_positive_row_count": 1_560,
        "support_zero_row_count": 0,
        "min_support_slack_x1e12": 237_881_393_182,
        "max_support_slack_x1e12": 3_103_251_249_022,
        "positive_support_cone_flag": 1,
        "collinear_triple_count": 0,
        "minimal_c4_count": 7_095,
        "minimal_c5_count": 2_824_272,
        "minimal_affine_circuit_count": 2_831_367,
        "max_c4_det_abs_x1e15": 5_705,
        "min_non_c4_det_abs_x1e12": 34_973_033_701,
        "circuit_census_gap_flag": 1,
        "signed_row_count": 2_831_367,
        "zero_pairing_count": 0,
        "positive_pairing_count": 2_831_367,
        "min_positive_pairing": 146,
        "max_positive_pairing_bit_length": 141,
        "strict_height_orientation_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"eta6_repl observable {key} mismatch")

    witness = report.get("witness", {})
    if witness.get("removed_original_vertices") != [43, 53, 54, 59, 57, 44]:
        raise AssertionError("eta6_repl removed vertices mismatch")
    if witness.get("cap_original_vertices") != [42, 40, 51, 50, 56, 58]:
        raise AssertionError("eta6_repl cap vertices mismatch")
    if witness.get("circuits", {}).get("row_stream_sha256") != (
        "58a495540af510f0ef52e8d730ffbf58d42c07725971dff463364f67d79e118c"
    ):
        raise AssertionError("eta6_repl row stream hash mismatch")
    if witness.get("circuits", {}).get("support_stream_sha256") != (
        "99e478f0cc956ef367eca0ddf24d9b2ea22612ccc0a9ef1b4c4e250a4a5c9477"
    ):
        raise AssertionError("eta6_repl support stream hash mismatch")
    if verts_csv.splitlines()[0].split(",") != VERTEX_COLUMNS:
        raise AssertionError("eta6_repl vertex header mismatch")
    if edges_csv.splitlines()[0].split(",") != EDGE_COLUMNS:
        raise AssertionError("eta6_repl edge header mismatch")
    if faces_csv.splitlines()[0].split(",") != FACE_COLUMNS:
        raise AssertionError("eta6_repl face header mismatch")
    if supp_csv.splitlines()[0].split(",") != SUPP_COLUMNS:
        raise AssertionError("eta6_repl support header mismatch")
    if c4_csv.splitlines()[0].split(",") != C4_COLUMNS:
        raise AssertionError("eta6_repl c4 header mismatch")
    if samp_csv.splitlines()[0].split(",") != SAMPLE_COLUMNS:
        raise AssertionError("eta6_repl sample header mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("surg_report", {}), SURG_REPORT, "surg report")
    assert_file_hash(
        inputs.get("truncated_report", {}),
        TRUNCATED_REPORT,
        "truncated report",
    )
    assert_file_hash(
        inputs.get("truncated_tables", {}),
        TRUNCATED_TABLES,
        "truncated tables",
    )
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "eta6.repl.manifest@1":
        raise AssertionError("eta6_repl manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_repl manifest report hash mismatch")
    if pair.parent.self_hash(manifest, "manifest_sha256") != manifest.get(
        "manifest_sha256"
    ):
        raise AssertionError("eta6_repl manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6_repl missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_repl index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6_repl index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "eta6.repl.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_eta6_repl(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
