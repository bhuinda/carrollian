from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_eta6_hit2 import (
        COLLAPSE_COLUMNS,
        DERIVE_SCRIPT,
        HIT_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        REPL_FACES,
        REPL_REPORT,
        REPL_SUPP,
        REPL_VERTS,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        XFER_REPORT,
        build_payloads,
        pair,
        repl,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_eta6_hit2 import (
        COLLAPSE_COLUMNS,
        DERIVE_SCRIPT,
        HIT_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        REPL_FACES,
        REPL_REPORT,
        REPL_SUPP,
        REPL_VERTS,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        XFER_REPORT,
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


def validate_eta6_hit2() -> dict[str, Any]:
    expected = build_payloads()
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    hit2 = load_json(OUT_DIR / "hit2.json")
    cert = load_json(OUT_DIR / "cert.json")
    hits_csv = (OUT_DIR / "hits.csv").read_text(encoding="utf-8")
    collapse_csv = (OUT_DIR / "collapse.csv").read_text(encoding="utf-8")
    obs_csv = (OUT_DIR / "obs.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    index = load_json(repl.ext.nonholonomic.preservation.INDEX_PATH)

    if hit2 != expected["hit2"]:
        raise AssertionError("eta6_hit2 JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("eta6_hit2 cert mismatch")
    if hits_csv != expected["hits_csv"]:
        raise AssertionError("eta6_hit2 hits CSV mismatch")
    if collapse_csv != expected["collapse_csv"]:
        raise AssertionError("eta6_hit2 collapse CSV mismatch")
    if obs_csv != expected["obs_csv"]:
        raise AssertionError("eta6_hit2 obs CSV mismatch")
    if not np.array_equal(np.asarray(tables["hit_table"]), expected["hit_table"]):
        raise AssertionError("eta6_hit2 hit table mismatch")
    if not np.array_equal(
        np.asarray(tables["collapse_table"]),
        expected["collapse_table"],
    ):
        raise AssertionError("eta6_hit2 collapse table mismatch")
    if not np.array_equal(
        np.asarray(tables["observable_table"]),
        expected["obs_table"],
    ):
        raise AssertionError("eta6_hit2 observable table mismatch")

    if report.get("schema") != "eta6.hit2.report@1":
        raise AssertionError("eta6_hit2 report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6_hit2 report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6_hit2 all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6_hit2 checks mismatch")
    if pair.parent.self_hash(report, "certificate_sha256") != report.get(
        "certificate_sha256"
    ):
        raise AssertionError("eta6_hit2 report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6_hit2 report hash mismatch")

    hit_table = np.asarray(tables["hit_table"], dtype=np.int64)
    collapse_table = np.asarray(tables["collapse_table"], dtype=np.int64)
    obs_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(hit_table.shape) != (3, len(HIT_COLUMNS)):
        raise AssertionError("eta6_hit2 hit table shape mismatch")
    if tuple(collapse_table.shape) != (6, len(COLLAPSE_COLUMNS)):
        raise AssertionError("eta6_hit2 collapse table shape mismatch")
    if tuple(obs_table.shape) != (len(OBS_CODES), len(OBS_COLUMNS)):
        raise AssertionError("eta6_hit2 obs table shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(obs_table, OBS_COLUMNS)
    }
    required = {
        "support_row_count": 1_560,
        "negative_ray_row_count": 782,
        "first_hit_row_count": 3,
        "first_hit_face_id": 31,
        "first_tau_numerator": 118_940_696_591,
        "first_tau_denominator": 512,
        "next_tau_numerator": 96_225_044_865,
        "next_tau_denominator": 256,
        "post_tau_numerator": 311_390_786_321,
        "post_tau_denominator": 1_024,
        "survivor_row_count": 1_557,
        "positive_survivor_count": 1_557,
        "nonpositive_survivor_count": 0,
        "min_survivor_slack_numerator": 73_509_393_139,
        "min_survivor_slack_denominator": 1,
        "removed_negative_post_count": 3,
        "support_cone_positive_after_hit_cut_flag": 1,
        "naive_removed_vertex_count": 6,
        "naive_cap_vertex_count": 3,
        "collapsed_face_count": 6,
        "collapsed_to_vertex_count": 3,
        "collapsed_to_edge_count": 3,
        "min_naive_face_size": 1,
        "edge_incidence_bad_edge_count": 15,
        "simple_replacement_valid_flag": 0,
        "three_edge_collapse_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"eta6_hit2 observable {key} mismatch")

    witness = report.get("witness", {})
    if witness.get("classification") != "three_edge_collapse_obstruction":
        raise AssertionError("eta6_hit2 classification mismatch")
    if witness.get("hit_original_vertices") != [41, 52, 55]:
        raise AssertionError("eta6_hit2 original hit vertices mismatch")
    if witness.get("hit_local_vertices") != [41, 50, 51]:
        raise AssertionError("eta6_hit2 local hit vertices mismatch")
    if witness.get("collapsed_neighbor_faces") != [8, 10, 11, 25, 29, 30]:
        raise AssertionError("eta6_hit2 collapsed faces mismatch")
    if hits_csv.splitlines()[0].split(",") != HIT_COLUMNS:
        raise AssertionError("eta6_hit2 hit header mismatch")
    if collapse_csv.splitlines()[0].split(",") != COLLAPSE_COLUMNS:
        raise AssertionError("eta6_hit2 collapse header mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("repl_report", {}), REPL_REPORT, "repl report")
    assert_file_hash(inputs.get("xfer_report", {}), XFER_REPORT, "xfer report")
    assert_file_hash(inputs.get("repl_faces", {}), REPL_FACES, "repl faces")
    assert_file_hash(inputs.get("repl_verts", {}), REPL_VERTS, "repl verts")
    assert_file_hash(inputs.get("repl_supp", {}), REPL_SUPP, "repl supp")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "eta6.hit2.manifest@1":
        raise AssertionError("eta6_hit2 manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_hit2 manifest report hash mismatch")
    if pair.parent.self_hash(manifest, "manifest_sha256") != manifest.get(
        "manifest_sha256"
    ):
        raise AssertionError("eta6_hit2 manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6_hit2 missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_hit2 index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6_hit2 index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "eta6.hit2.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_eta6_hit2(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
