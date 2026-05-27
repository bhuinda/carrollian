from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_geon_phase_entropy_audit import (
        ARTIFACT_PATH,
        INDEX_PATH,
        OUT_DIR,
        THEOREM_ID,
        build_artifact,
        build_manifest,
        build_report,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_d20_geon_phase_entropy_audit import (
        ARTIFACT_PATH,
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

EXPECTED_CHECKS = {
    "visualization_data_loaded",
    "d20_lift_render_grid_is_2_by_2",
    "d20_rgba_atom_canvas_declared",
    "d20_atlas_tension_canvas_declared",
    "d20_atlas_tension_uses_certified_stress_graph",
    "d20_rgba_atom_3d_canvas_declared",
    "d20_rgba_atom_3d_uses_translucent_projection",
    "robust_oblongness_theorem_certified",
    "intrinsic_ratio_is_31_over_23",
    "all_named_voltage_lifts_oblong",
    "d20_render_alpha_entropy_zero",
    "d20_rgba_atom_alpha_entropy_zero",
    "d20_rgba_atom_non_alpha_channels_nonzero",
    "topple_render_alpha_entropy_zero",
    "d20_render_state_entropy_nonzero",
    "topple_height_entropy_nonzero",
    "d20_render_spectrum_exceeds_histogram_shuffle",
    "topple_render_spectrum_exceeds_histogram_shuffle",
    "golay_hamming_coordinate_claim_remains_open",
    "physical_geon_claim_not_promoted",
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
        raise AssertionError(f"{label} file hash mismatch")


def _assert_spectral_witness(row: dict[str, Any], label: str) -> None:
    z_scores = row.get("z_scores", {})
    if float(z_scores.get("dominant_non_dc_power_fraction", 0.0)) <= 10.0:
        raise AssertionError(f"{label} dominant spectral z-score too small")
    if float(z_scores.get("spectral_entropy_normalized", 0.0)) >= -10.0:
        raise AssertionError(f"{label} spectral entropy z-score too small")


def validate_d20_geon_phase_entropy_audit() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != "d20.proof_obligation.geon_phase_entropy_audit.artifact@1":
        raise AssertionError("geon phase entropy artifact schema mismatch")
    if artifact.get("status") != "D20_GEON_PHASE_ENTROPY_AUDIT_DERIVED":
        raise AssertionError("geon phase entropy artifact status mismatch")
    if _self_hash(artifact, "artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("geon phase entropy artifact self hash mismatch")

    rebuilt_artifact = build_artifact()
    if rebuilt_artifact.get("artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("geon phase entropy artifact is not reproducible")

    checks = artifact.get("checks", {})
    if set(checks) != EXPECTED_CHECKS or any(checks.get(key) is not True for key in EXPECTED_CHECKS):
        raise AssertionError("geon phase entropy artifact checks mismatch")

    d20_final = artifact.get("phase_entropy_witness", {}).get("d20_lift", {}).get("final", {})
    topple_final = artifact.get("phase_entropy_witness", {}).get("square_abelian_topple", {}).get(
        "final", {}
    )
    canvas_audit = artifact.get("canvas_source_audit", {})
    if canvas_audit.get("d20_lift_grid", {}).get("frame_count") != 4:
        raise AssertionError("D20 lift grid is not recorded as four frames")
    if canvas_audit.get("d20_rgba_atom_3d_canvas", {}).get("id") != "d20RgbaAtom3dCanvas":
        raise AssertionError("D20 RGBA atom 3D canvas audit is missing")
    if canvas_audit.get("d20_atlas_tension_canvas", {}).get("id") != "d20AtlasTensionCanvas":
        raise AssertionError("D20 atlas tension canvas audit is missing")
    if d20_final.get("cooriented_render_channels", {}).get("unique_values", {}).get("alpha") != [255]:
        raise AssertionError("D20 alpha channel is not constant opaque")
    if d20_final.get("rgba_atom_channels", {}).get("unique_values", {}).get("alpha") != [255]:
        raise AssertionError("D20 RGBA atom alpha channel is not constant opaque")
    if topple_final.get("render_channels", {}).get("unique_values", {}).get("alpha") != [255]:
        raise AssertionError("topple alpha channel is not constant opaque")
    if float(d20_final.get("cooriented_render_entropy_bits", 0.0)) <= 0.0:
        raise AssertionError("D20 render entropy is zero")
    atom_entropy = d20_final.get("rgba_atom_channel_entropy_bits", {})
    if any(float(atom_entropy.get(channel, 0.0)) <= 0.0 for channel in ("red", "green", "blue")):
        raise AssertionError("D20 RGBA atom non-alpha channel entropy is zero")
    if float(topple_final.get("height_entropy_bits", 0.0)) <= 0.0:
        raise AssertionError("topple height entropy is zero")
    _assert_spectral_witness(d20_final.get("cooriented_render_spectral_null", {}), "D20 render")
    _assert_spectral_witness(topple_final.get("render_spectral_null", {}), "topple render")

    open_ids = [row.get("id") for row in artifact.get("open_obligations", [])]
    if open_ids != [
        "live_browser_rgba_capture",
        "three_coordinate_hamming_weight8_witness",
        "physical_geon_interpretation",
    ]:
        raise AssertionError("geon phase entropy open-obligation boundary mismatch")

    if report.get("schema") != "d20.proof_obligation.geon_phase_entropy_audit@1":
        raise AssertionError("geon phase entropy report schema mismatch")
    if report.get("status") != "D20_GEON_PHASE_ENTROPY_AUDIT_CERTIFIED":
        raise AssertionError("geon phase entropy report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("geon phase entropy report checks did not pass")
    if report.get("checks") != checks:
        raise AssertionError("geon phase entropy report checks differ from artifact")
    if report.get("open_obligations") != artifact.get("open_obligations"):
        raise AssertionError("geon phase entropy report open obligations differ from artifact")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("geon phase entropy report self hash mismatch")

    artifact_input = report.get("inputs", {}).get("artifact", {})
    _check_input_file(artifact_input, ARTIFACT_REL, "report artifact input")
    if artifact_input.get("artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("report artifact internal hash mismatch")
    _check_input_file(report.get("inputs", {}).get("validator", {}), "src/certify_d20_geon_phase_entropy_audit.py", "validator input")
    _check_input_file(report.get("inputs", {}).get("visualization", {}), "generated/d20_sandpile_visualization.html", "visualization input")

    expected_report = build_report(artifact)
    if expected_report.get("certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("geon phase entropy report is not reproducible")

    if manifest.get("schema") != "d20.proof_obligation.geon_phase_entropy_audit_manifest@1":
        raise AssertionError("geon phase entropy manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("geon phase entropy manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("geon phase entropy manifest artifact hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("geon phase entropy manifest self hash mismatch")
    expected_manifest = build_manifest(report, artifact)
    if expected_manifest.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("geon phase entropy manifest is not reproducible")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("geon phase entropy registry entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("geon phase entropy registry report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("geon phase entropy registry status mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_geon_phase_entropy_audit()
    print("D20 geon phase entropy audit validated")
