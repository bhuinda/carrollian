from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401

import json
import math
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_boundary_neighborhood_stress_graph import (
        ARTIFACT_PATH,
        ATLAS_NPZ,
        ATLAS_REPORT,
        INDEX_PATH,
        OUT_DIR,
        THEOREM_ID,
        build_artifact,
        build_manifest,
        build_report,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_boundary_neighborhood_stress_graph import (
        ARTIFACT_PATH,
        ATLAS_NPZ,
        ATLAS_REPORT,
        INDEX_PATH,
        OUT_DIR,
        THEOREM_ID,
        build_artifact,
        build_manifest,
        build_report,
    )


ARTIFACT_REL = ARTIFACT_PATH.relative_to(ROOT).as_posix()
REPORT_REL = (OUT_DIR / "report.json").relative_to(ROOT).as_posix()
MANIFEST_REL = (OUT_DIR / "manifest.json").relative_to(ROOT).as_posix()
INDEX_REL = INDEX_PATH.relative_to(ROOT).as_posix()
ATLAS_NPZ_REL = ATLAS_NPZ.relative_to(ROOT).as_posix()
ATLAS_REPORT_REL = ATLAS_REPORT.relative_to(ROOT).as_posix()

EXPECTED_CHECKS = {
    "atlas_report_passed",
    "atom_table_shape_is_20_by_15",
    "complement_map_is_involutive",
    "graph_rows_are_stochastic",
    "all_nodes_have_five_neighbors",
    "signed_tension_has_two_polarities",
}


def _load_json(rel_path: str) -> dict[str, Any]:
    with (ROOT / rel_path).open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise AssertionError(f"{rel_path} is not a JSON object")
    return payload


def _self_hash(payload: dict[str, Any], field: str) -> str:
    tmp = dict(payload)
    tmp.pop(field, None)
    return h_json(tmp)


def _check_input_file(entry: dict[str, Any], rel_path: str, label: str) -> None:
    if entry.get("path") != rel_path:
        raise AssertionError(f"{label} path mismatch")
    if h_file(ROOT / rel_path) != entry.get("sha256"):
        raise AssertionError(f"{label} hash mismatch")


def _assert_finite(value: Any, label: str) -> None:
    if not math.isfinite(float(value)):
        raise AssertionError(f"{label} is not finite")


def validate_c985_d20_boundary_neighborhood_stress_graph() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != "c985.d20_boundary_neighborhood_stress_graph.artifact@1":
        raise AssertionError("stress graph artifact schema mismatch")
    if artifact.get("status") != "C985_D20_BOUNDARY_NEIGHBORHOOD_STRESS_GRAPH_CERTIFIED":
        raise AssertionError("stress graph artifact status mismatch")
    if _self_hash(artifact, "artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("stress graph artifact self hash mismatch")
    expected_artifact = build_artifact()
    if expected_artifact.get("artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("stress graph artifact is not reproducible")

    checks = artifact.get("checks", {})
    if set(checks) != EXPECTED_CHECKS or not all(checks.values()):
        raise AssertionError("stress graph checks mismatch")
    summary = artifact.get("witness", {}).get("summary", {})
    rows = artifact.get("witness", {}).get("graph_rows", [])
    if int(summary.get("node_count", 0)) != 20 or len(rows) != 20:
        raise AssertionError("stress graph node count mismatch")
    if int(summary.get("neighbor_count_per_node", 0)) != 5:
        raise AssertionError("stress graph neighbor count mismatch")
    if abs(float(summary.get("row_sum_min", 0.0)) - 1.0) > 1e-10:
        raise AssertionError("stress graph row sum min mismatch")
    if abs(float(summary.get("row_sum_max", 0.0)) - 1.0) > 1e-10:
        raise AssertionError("stress graph row sum max mismatch")
    for key in (
        "signed_tension_min",
        "signed_tension_max",
        "mean_abs_signed_tension",
    ):
        _assert_finite(summary.get(key), key)
    if float(summary.get("signed_tension_min", 0.0)) >= 0.0:
        raise AssertionError("stress graph signed tension min is not negative")
    if float(summary.get("signed_tension_max", 0.0)) <= 0.0:
        raise AssertionError("stress graph signed tension max is not positive")
    for row in rows:
        if len(row.get("neighbors", [])) != 5:
            raise AssertionError("stress graph row does not have five neighbors")
        total = sum(float(neighbor.get("weight", 0.0)) for neighbor in row.get("neighbors", []))
        if total <= 0.0:
            raise AssertionError("stress graph top-neighbor weights are empty")
        for key in ("atom_id", "complement_atom_id", "tension", "signed_tension"):
            _assert_finite(row.get(key), f"graph row {key}")

    if report.get("schema") != "c985.d20_boundary_neighborhood_stress_graph@1":
        raise AssertionError("stress graph report schema mismatch")
    if report.get("status") != artifact.get("status"):
        raise AssertionError("stress graph report status mismatch")
    if report.get("checks") != checks:
        raise AssertionError("stress graph report checks mismatch")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("stress graph report self hash mismatch")
    expected_report = build_report(artifact)
    if expected_report.get("certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("stress graph report is not reproducible")
    inputs = report.get("inputs", {})
    _check_input_file(inputs.get("artifact", {}), ARTIFACT_REL, "artifact input")
    _check_input_file(inputs.get("validator", {}), "src/certify_c985_d20_boundary_neighborhood_stress_graph.py", "validator input")
    _check_input_file(inputs.get("atlas_npz", {}), ATLAS_NPZ_REL, "atlas NPZ input")
    _check_input_file(inputs.get("atlas_report", {}), ATLAS_REPORT_REL, "atlas report input")

    if manifest.get("schema") != "c985.d20_boundary_neighborhood_stress_graph_manifest@1":
        raise AssertionError("stress graph manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("stress graph manifest report hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("stress graph manifest self hash mismatch")
    expected_manifest = build_manifest(report, artifact)
    if expected_manifest.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("stress graph manifest is not reproducible")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("stress graph registry entry missing")
    if entry.get("status") != report.get("status"):
        raise AssertionError("stress graph registry status mismatch")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("stress graph registry report hash mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_c985_d20_boundary_neighborhood_stress_graph()
    print("C985 D20 boundary neighborhood stress graph validated")
