from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_eta6_xfer import (
        CYCLE_COLUMNS,
        DERIVE_SCRIPT,
        EDGE_COLUMNS,
        HOL_REPORT,
        LABEL_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PATCH_COLUMNS,
        REPL_FACES,
        REPL_REPORT,
        REPL_VERTS,
        STATUS,
        THEOREM_ID,
        TRUNCATED_TABLES,
        VALIDATOR_SCRIPT,
        build_payloads,
        pair,
        repl,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_eta6_xfer import (
        CYCLE_COLUMNS,
        DERIVE_SCRIPT,
        EDGE_COLUMNS,
        HOL_REPORT,
        LABEL_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PATCH_COLUMNS,
        REPL_FACES,
        REPL_REPORT,
        REPL_VERTS,
        STATUS,
        THEOREM_ID,
        TRUNCATED_TABLES,
        VALIDATOR_SCRIPT,
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


def validate_eta6_xfer() -> dict[str, Any]:
    expected = build_payloads()
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    xfer = load_json(OUT_DIR / "xfer.json")
    cert = load_json(OUT_DIR / "cert.json")
    edges_csv = (OUT_DIR / "edges.csv").read_text(encoding="utf-8")
    labels_csv = (OUT_DIR / "labels.csv").read_text(encoding="utf-8")
    patch_csv = (OUT_DIR / "patch.csv").read_text(encoding="utf-8")
    cycles_csv = (OUT_DIR / "cycles.csv").read_text(encoding="utf-8")
    obs_csv = (OUT_DIR / "obs.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    index = load_json(repl.ext.nonholonomic.preservation.INDEX_PATH)

    if xfer != expected["xfer"]:
        raise AssertionError("eta6_xfer JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("eta6_xfer cert mismatch")
    if edges_csv != expected["edges_csv"]:
        raise AssertionError("eta6_xfer edges CSV mismatch")
    if labels_csv != expected["labels_csv"]:
        raise AssertionError("eta6_xfer labels CSV mismatch")
    if patch_csv != expected["patch_csv"]:
        raise AssertionError("eta6_xfer patch CSV mismatch")
    if cycles_csv != expected["cycles_csv"]:
        raise AssertionError("eta6_xfer cycles CSV mismatch")
    if obs_csv != expected["obs_csv"]:
        raise AssertionError("eta6_xfer obs CSV mismatch")

    table_expectations = {
        "edge_table": expected["edge_table"],
        "label_table": expected["label_table"],
        "patch_table": expected["patch_table"],
        "cycle_table": expected["cycle_table"],
        "observable_table": expected["obs_table"],
    }
    for name, value in table_expectations.items():
        if not np.array_equal(np.asarray(tables[name]), value):
            raise AssertionError(f"eta6_xfer {name} mismatch")

    if report.get("schema") != "eta6.xfer.report@1":
        raise AssertionError("eta6_xfer report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6_xfer report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6_xfer all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6_xfer checks mismatch")
    if pair.parent.self_hash(report, "certificate_sha256") != report.get(
        "certificate_sha256"
    ):
        raise AssertionError("eta6_xfer report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6_xfer report hash mismatch")

    edge_table = np.asarray(tables["edge_table"], dtype=np.int64)
    label_table = np.asarray(tables["label_table"], dtype=np.int64)
    patch_table = np.asarray(tables["patch_table"], dtype=np.int64)
    cycle_table = np.asarray(tables["cycle_table"], dtype=np.int64)
    obs_table = np.asarray(tables["observable_table"], dtype=np.int64)
    required_shapes = {
        "edge": (6, len(EDGE_COLUMNS), edge_table),
        "label": (6, len(LABEL_COLUMNS), label_table),
        "patch": (7, len(PATCH_COLUMNS), patch_table),
        "cycle": (2, len(CYCLE_COLUMNS), cycle_table),
        "observable": (len(OBS_CODES), len(OBS_COLUMNS), obs_table),
    }
    for label, (rows, cols, table) in required_shapes.items():
        if tuple(table.shape) != (rows, cols):
            raise AssertionError(f"eta6_xfer {label} table shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(obs_table, OBS_COLUMNS)
    }
    required = {
        "edge_count": 6,
        "transfer_rank": 6,
        "eta_before_weight": 6,
        "eta_after_weight": 6,
        "eta_transfer_equal_flag": 1,
        "holonomy_before_weight": 3,
        "holonomy_after_weight": 3,
        "holonomy_transfer_equal_flag": 1,
        "holonomy_eta_pairing_before": 1,
        "holonomy_eta_pairing_after": 1,
        "label_count_preserved_flag": 1,
        "source_face_count_before": 32,
        "source_face_count_after": 32,
        "source_id_preserved_count": 32,
        "affected_face_count": 7,
        "old_cycle_length": 6,
        "cap_cycle_length": 6,
        "cap_uses_first_hit_vertices_flag": 1,
        "removed_cycle_disjoint_cap_flag": 1,
        "geometric_carrier_changed_flag": 1,
        "eta6_killed_flag": 0,
        "eta6_preserved_flag": 1,
        "eta6_transformed_geometrically_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"eta6_xfer observable {key} mismatch")

    witness = report.get("witness", {})
    if witness.get("classification") != "preserved_class_transformed_carrier":
        raise AssertionError("eta6_xfer classification mismatch")
    if witness.get("eta6_after") != [1, 1, 1, 1, 1, 1]:
        raise AssertionError("eta6_xfer eta6 vector mismatch")
    if witness.get("holonomy_after") != [0, 0, 1, 0, 1, 1]:
        raise AssertionError("eta6_xfer holonomy vector mismatch")
    if witness.get("holonomy_eta_pairing_after") != 1:
        raise AssertionError("eta6_xfer pairing mismatch")
    if witness.get("old_face31_cycle", {}).get("v0") != 43:
        raise AssertionError("eta6_xfer old cycle mismatch")
    if witness.get("new_cap_cycle", {}).get("v0") != 42:
        raise AssertionError("eta6_xfer cap cycle mismatch")
    if edges_csv.splitlines()[0].split(",") != EDGE_COLUMNS:
        raise AssertionError("eta6_xfer edge header mismatch")
    if labels_csv.splitlines()[0].split(",") != LABEL_COLUMNS:
        raise AssertionError("eta6_xfer label header mismatch")
    if patch_csv.splitlines()[0].split(",") != PATCH_COLUMNS:
        raise AssertionError("eta6_xfer patch header mismatch")
    if cycles_csv.splitlines()[0].split(",") != CYCLE_COLUMNS:
        raise AssertionError("eta6_xfer cycle header mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("holonomy_report", {}), HOL_REPORT, "holonomy report")
    assert_file_hash(inputs.get("repl_report", {}), REPL_REPORT, "repl report")
    assert_file_hash(inputs.get("repl_faces", {}), REPL_FACES, "repl faces")
    assert_file_hash(inputs.get("repl_verts", {}), REPL_VERTS, "repl verts")
    assert_file_hash(
        inputs.get("truncated_tables", {}),
        TRUNCATED_TABLES,
        "truncated tables",
    )
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "eta6.xfer.manifest@1":
        raise AssertionError("eta6_xfer manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_xfer manifest report hash mismatch")
    if pair.parent.self_hash(manifest, "manifest_sha256") != manifest.get(
        "manifest_sha256"
    ):
        raise AssertionError("eta6_xfer manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6_xfer missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_xfer index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6_xfer index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "eta6.xfer.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_eta6_xfer(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
