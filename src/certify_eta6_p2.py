from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_eta6_p2 import (
        C4_COLUMNS,
        DERIVE_SCRIPT,
        EDGE_COLUMNS,
        FACE_COLUMNS,
        HIT2_REPORT,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        REPL_FACES,
        REPL_REPORT,
        REPL_VERTS,
        SAMPLE_COLUMNS,
        STATUS,
        SUPP_COLUMNS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        VERTEX_COLUMNS,
        build_payloads,
        pair,
        repl,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_eta6_p2 import (
        C4_COLUMNS,
        DERIVE_SCRIPT,
        EDGE_COLUMNS,
        FACE_COLUMNS,
        HIT2_REPORT,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        REPL_FACES,
        REPL_REPORT,
        REPL_VERTS,
        SAMPLE_COLUMNS,
        STATUS,
        SUPP_COLUMNS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        VERTEX_COLUMNS,
        build_payloads,
        pair,
        repl,
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


def validate_eta6_p2() -> dict[str, Any]:
    expected = build_payloads()
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    p2 = load_json(OUT_DIR / "p2.json")
    cert = load_json(OUT_DIR / "cert.json")
    verts_csv = (OUT_DIR / "verts.csv").read_text(encoding="utf-8")
    edges_csv = (OUT_DIR / "edges.csv").read_text(encoding="utf-8")
    faces_csv = (OUT_DIR / "faces.csv").read_text(encoding="utf-8")
    supp_csv = (OUT_DIR / "supp.csv").read_text(encoding="utf-8")
    c4_csv = (OUT_DIR / "c4.csv").read_text(encoding="utf-8")
    sample_csv = (OUT_DIR / "samp.csv").read_text(encoding="utf-8")
    obs_csv = (OUT_DIR / "obs.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    index = load_json(repl.ext.nonholonomic.preservation.INDEX_PATH)

    if p2 != expected["p2"]:
        raise AssertionError("eta6_p2 JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("eta6_p2 cert mismatch")
    if verts_csv != expected["verts_csv"]:
        raise AssertionError("eta6_p2 verts CSV mismatch")
    if edges_csv != expected["edges_csv"]:
        raise AssertionError("eta6_p2 edges CSV mismatch")
    if faces_csv != expected["faces_csv"]:
        raise AssertionError("eta6_p2 faces CSV mismatch")
    if supp_csv != expected["supp_csv"]:
        raise AssertionError("eta6_p2 support CSV mismatch")
    if c4_csv != expected["c4_csv"]:
        raise AssertionError("eta6_p2 c4 CSV mismatch")
    if sample_csv != expected["samp_csv"]:
        raise AssertionError("eta6_p2 sample CSV mismatch")
    if obs_csv != expected["obs_csv"]:
        raise AssertionError("eta6_p2 obs CSV mismatch")
    table_pairs = [
        ("vertex_table", expected["vertex_table"]),
        ("edge_table", expected["edge_table"]),
        ("face_table", expected["face_table"]),
        ("support_table", expected["support_table"]),
        ("c4_table", expected["c4_table"]),
        ("sample_table", expected["sample_table"]),
        ("observable_table", expected["obs_table"]),
    ]
    for name, expected_table in table_pairs:
        if not np.array_equal(np.asarray(tables[name]), expected_table):
            raise AssertionError(f"eta6_p2 {name} mismatch")

    if report.get("schema") != "eta6.p2.report@1":
        raise AssertionError("eta6_p2 report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6_p2 report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6_p2 all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6_p2 checks mismatch")
    if pair.parent.self_hash(report, "certificate_sha256") != report.get(
        "certificate_sha256"
    ):
        raise AssertionError("eta6_p2 report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6_p2 report hash mismatch")

    obs_table = np.asarray(tables["observable_table"], dtype=np.int64)
    required_shapes = {
        "vertex_table": (48, len(VERTEX_COLUMNS)),
        "edge_table": (75, len(EDGE_COLUMNS)),
        "face_table": (29, len(FACE_COLUMNS)),
        "support_table": (1_242, len(SUPP_COLUMNS)),
        "c4_table": (4_626, len(C4_COLUMNS)),
        "sample_table": (repl.SAMPLE_LIMIT, len(SAMPLE_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for name, shape in required_shapes.items():
        if tuple(np.asarray(tables[name]).shape) != shape:
            raise AssertionError(f"eta6_p2 {name} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(obs_table, OBS_COLUMNS)
    }
    required = {
        "vertex_count": 48,
        "removed_vertex_count": 6,
        "edge_count": 75,
        "face_count": 29,
        "triangle_face_count": 1,
        "quadrilateral_face_count": 3,
        "pentagon_face_count": 15,
        "hexagon_face_count": 10,
        "euler_characteristic": 2,
        "connected_flag": 1,
        "three_vertex_connected_flag": 1,
        "edge_two_face_incidence_flag": 1,
        "degree_three_vertex_count": 45,
        "degree_five_vertex_count": 3,
        "cubic_carrier_flag": 0,
        "central_face_id": 27,
        "source_exact_face_count": 19,
        "source_shrunk_face_count": 6,
        "fused_face_count": 3,
        "cap_face_count": 1,
        "support_row_count": 1_242,
        "support_positive_row_count": 1_242,
        "support_zero_row_count": 0,
        "min_support_slack_x1e12": 147_018_786_278,
        "max_support_slack_x1e12": 3_103_251_249_022,
        "positive_support_cone_flag": 1,
        "collinear_triple_count": 0,
        "minimal_c4_count": 4_626,
        "minimal_c5_count": 1_518_732,
        "minimal_affine_circuit_count": 1_523_358,
        "circuit_census_gap_flag": 1,
        "signed_row_count": 1_523_358,
        "zero_pairing_count": 0,
        "positive_pairing_count": 1_523_358,
        "min_positive_pairing": 146,
        "max_positive_pairing_bit_length": 140,
        "strict_height_orientation_flag": 1,
        "eta6_identity_transfer_ready_flag": 0,
        "valence_change_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"eta6_p2 observable {key} mismatch")

    witness = report.get("witness", {})
    if witness.get("high_degree_original_vertices") != [41, 52, 55]:
        raise AssertionError("eta6_p2 high-degree vertices mismatch")
    if witness.get("hull_face_sets_sha256") != (
        "d48c8dc86f78e6e1f7872fcdf48f0f7ed44c4e04d9b02315ae9259c65db4196b"
    ):
        raise AssertionError("eta6_p2 hull hash mismatch")
    if witness.get("circuits", {}).get("row_stream_sha256") != (
        "282b0ae02d1ccd34bca5e8f2f84b9fdc8bfb913108d7a10a2ab6a2e450116f50"
    ):
        raise AssertionError("eta6_p2 row hash mismatch")
    if witness.get("circuits", {}).get("support_stream_sha256") != (
        "ce39fd237012c2a5ef57d0cb33b7aa556064878383b082ae625fdb02ebcbaf8e"
    ):
        raise AssertionError("eta6_p2 support hash mismatch")
    if verts_csv.splitlines()[0].split(",") != VERTEX_COLUMNS:
        raise AssertionError("eta6_p2 vertex header mismatch")
    if edges_csv.splitlines()[0].split(",") != EDGE_COLUMNS:
        raise AssertionError("eta6_p2 edge header mismatch")
    if faces_csv.splitlines()[0].split(",") != FACE_COLUMNS:
        raise AssertionError("eta6_p2 face header mismatch")
    if supp_csv.splitlines()[0].split(",") != SUPP_COLUMNS:
        raise AssertionError("eta6_p2 support header mismatch")
    if c4_csv.splitlines()[0].split(",") != C4_COLUMNS:
        raise AssertionError("eta6_p2 c4 header mismatch")
    if sample_csv.splitlines()[0].split(",") != SAMPLE_COLUMNS:
        raise AssertionError("eta6_p2 sample header mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("repl_report", {}), REPL_REPORT, "repl report")
    assert_file_hash(inputs.get("hit2_report", {}), HIT2_REPORT, "hit2 report")
    assert_file_hash(inputs.get("repl_verts", {}), REPL_VERTS, "repl verts")
    assert_file_hash(inputs.get("repl_faces", {}), REPL_FACES, "repl faces")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "eta6.p2.manifest@1":
        raise AssertionError("eta6_p2 manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p2 manifest report hash mismatch")
    if pair.parent.self_hash(manifest, "manifest_sha256") != manifest.get(
        "manifest_sha256"
    ):
        raise AssertionError("eta6_p2 manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6_p2 missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_p2 index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6_p2 index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "eta6.p2.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_eta6_p2(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
