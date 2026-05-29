from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_cluster import (
        CLUSTER_COLUMNS,
        CLUSTER_TEXT_HASH,
        DERIVE_SCRIPT,
        FOCUSED_MANIFESTS,
        FOCUSED_REPORTS,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        SEAM_COLUMNS,
        SEAM_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_cluster import (
        CLUSTER_COLUMNS,
        CLUSTER_TEXT_HASH,
        DERIVE_SCRIPT,
        FOCUSED_MANIFESTS,
        FOCUSED_REPORTS,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        SEAM_COLUMNS,
        SEAM_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        self_hash,
    )
    from derive_long_raw import rows_from_table


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} is not a JSON object")
    return payload


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def assert_file_hash(entry: dict[str, Any], expected_path: Path, label: str) -> None:
    expected_rel = expected_path.relative_to(ROOT).as_posix()
    if entry.get("path") != expected_rel:
        raise AssertionError(f"{label} path mismatch: {entry.get('path')}")
    if entry.get("sha256") != h_file(expected_path):
        raise AssertionError(f"{label} sha256 mismatch")


def validate_long_cluster() -> dict[str, Any]:
    expected = build_payloads()
    cluster_payload = load_json(OUT_DIR / "cluster.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if cluster_payload != expected["cluster"]:
        raise AssertionError("long_cluster JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_cluster cert mismatch")
    for filename, key in {
        "cluster.csv": "cluster_csv",
        "seam.csv": "seam_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_cluster {filename} mismatch")
    for key, expected_array in {
        "cluster_table": expected["cluster_table"],
        "seam_table": expected["seam_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_cluster table mismatch: {key}")

    if report.get("schema") != "long.cluster.report@1":
        raise AssertionError("long_cluster report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_cluster report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_cluster all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_cluster checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_cluster report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_cluster report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("cluster.csv", CLUSTER_COLUMNS, len(expected["cluster_table"])),
        ("seam.csv", SEAM_COLUMNS, len(expected["seam_table"])),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_cluster {filename} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    for key in [
        "theorem_report_count",
        "certified_report_count",
        "focused_consumed_report_count",
        "unconsumed_certified_report_count",
        "cluster_count",
        "reopened_cluster_count",
        "seam_candidate_count",
        "multi_theme_unconsumed_count",
    ]:
        if obs.get(OBS_CODES[key], 0) <= 0:
            raise AssertionError(f"long_cluster observable {key} is not positive")
    if obs.get(OBS_CODES["complete_goal_claim_flag"]) != 0:
        raise AssertionError("long_cluster overclaimed goal completion")

    if hashlib.sha256(
        digest_text(CLUSTER_COLUMNS, csv_rows["cluster.csv"]).encode("ascii")
    ).hexdigest() != CLUSTER_TEXT_HASH:
        raise AssertionError("long_cluster cluster hash mismatch")
    if hashlib.sha256(
        digest_text(SEAM_COLUMNS, csv_rows["seam.csv"]).encode("ascii")
    ).hexdigest() != SEAM_TEXT_HASH:
        raise AssertionError("long_cluster seam hash mismatch")
    if hashlib.sha256(
        digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")
    ).hexdigest() != OBS_TEXT_HASH:
        raise AssertionError("long_cluster observable hash mismatch")

    inputs = report.get("inputs", {})
    for name, path in FOCUSED_MANIFESTS.items():
        if path.exists():
            assert_file_hash(inputs.get(f"focused_manifest_{name}", {}), path, name)
    for name, path in FOCUSED_REPORTS.items():
        if path.exists():
            assert_file_hash(inputs.get(f"focused_report_{name}", {}), path, name)
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")
    for key, entry in inputs.items():
        if key.startswith("top_seam_"):
            path_value = entry.get("path")
            if not isinstance(path_value, str):
                raise AssertionError(f"{key} missing path")
            assert_file_hash(entry, ROOT / path_value, key)

    if manifest.get("schema") != "long.cluster.manifest@1":
        raise AssertionError("long_cluster manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_cluster manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_cluster manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_cluster missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_cluster proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_cluster proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.cluster.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "summary": witness.get("summary"),
            "cluster_code_map": witness.get("cluster_code_map"),
            "top_candidates": witness.get("top_candidates"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_cluster(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
