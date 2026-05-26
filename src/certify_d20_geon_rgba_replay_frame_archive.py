from __future__ import annotations

import base64
import hashlib
import json
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_geon_rgba_replay_frame_archive import (
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
    from derive_d20_geon_rgba_replay_frame_archive import (
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
    "source_visualization_hash_recorded",
    "phase_audit_certified",
    "frame_count_is_18",
    "sample_frames_match_phase_audit",
    "all_three_canvases_present",
    "every_frame_byte_length_matches_rgba_shape",
    "every_frame_hash_matches_base64_payload",
    "all_alpha_channels_constant_opaque",
    "some_non_alpha_state_entropy_present",
    "browser_capture_blocked_not_claimed",
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


def _validate_frame(row: dict[str, Any]) -> None:
    width = int(row["width"])
    height = int(row["height"])
    raw = base64.b64decode(row["rgba_base64"])
    if len(raw) != width * height * 4:
        raise AssertionError(f"{row['canvas_id']} frame {row['frame']} byte length mismatch")
    if len(raw) != int(row["byte_length"]):
        raise AssertionError(f"{row['canvas_id']} frame {row['frame']} stored byte length mismatch")
    if hashlib.sha256(raw).hexdigest() != row["rgba_sha256"]:
        raise AssertionError(f"{row['canvas_id']} frame {row['frame']} hash mismatch")
    alpha = raw[3::4]
    if any(value != 255 for value in alpha):
        raise AssertionError(f"{row['canvas_id']} frame {row['frame']} alpha is not opaque")
    if row.get("channel_summary", {}).get("entropy_bits", {}).get("alpha") != 0.0:
        raise AssertionError(f"{row['canvas_id']} frame {row['frame']} alpha entropy is not zero")


def validate_d20_geon_rgba_replay_frame_archive() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != "d20.proof_obligation.geon_rgba_replay_frame_archive.artifact@1":
        raise AssertionError("RGBA replay archive artifact schema mismatch")
    if artifact.get("status") != "D20_GEON_RGBA_REPLAY_FRAME_ARCHIVE_DERIVED":
        raise AssertionError("RGBA replay archive artifact status mismatch")
    if _self_hash(artifact, "artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("RGBA replay archive artifact self hash mismatch")
    rebuilt_artifact = build_artifact()
    if rebuilt_artifact.get("artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("RGBA replay archive artifact is not reproducible")

    checks = artifact.get("checks", {})
    if set(checks) != EXPECTED_CHECKS or any(checks.get(key) is not True for key in EXPECTED_CHECKS):
        raise AssertionError("RGBA replay archive checks mismatch")

    frames = artifact.get("frames", [])
    if len(frames) != 18:
        raise AssertionError("RGBA replay archive expected 18 frames")
    for row in frames:
        _validate_frame(row)
    if artifact.get("browser_capture_status", {}).get("status") != "BLOCKED_IN_CURRENT_ENVIRONMENT":
        raise AssertionError("browser-capture blocked boundary missing")
    if "not a live-browser" not in artifact.get("browser_capture_status", {}).get("boundary", ""):
        raise AssertionError("browser-capture nonclaim boundary missing")

    if report.get("schema") != "d20.proof_obligation.geon_rgba_replay_frame_archive@1":
        raise AssertionError("RGBA replay archive report schema mismatch")
    if report.get("status") != "D20_GEON_RGBA_REPLAY_FRAME_ARCHIVE_CERTIFIED_BROWSER_CAPTURE_BLOCKED":
        raise AssertionError("RGBA replay archive report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("RGBA replay archive report checks did not pass")
    if report.get("checks") != checks:
        raise AssertionError("RGBA replay archive report checks differ from artifact")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("RGBA replay archive report self hash mismatch")
    expected_report = build_report(artifact)
    if expected_report.get("certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("RGBA replay archive report is not reproducible")

    _check_input_file(report.get("inputs", {}).get("artifact", {}), ARTIFACT_REL, "artifact input")
    _check_input_file(
        report.get("inputs", {}).get("visualization", {}),
        "generated/d20_sandpile_visualization.html",
        "visualization input",
    )
    _check_input_file(
        report.get("inputs", {}).get("phase_entropy_audit_report", {}),
        "data/invariants/d20/proof_obligations/d20_geon_phase_entropy_audit/report.json",
        "phase audit input",
    )
    _check_input_file(
        report.get("inputs", {}).get("validator", {}),
        "src/certify_d20_geon_rgba_replay_frame_archive.py",
        "validator input",
    )

    if manifest.get("schema") != "d20.proof_obligation.geon_rgba_replay_frame_archive_manifest@1":
        raise AssertionError("RGBA replay archive manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("RGBA replay archive manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("RGBA replay archive manifest artifact hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("RGBA replay archive manifest self hash mismatch")
    expected_manifest = build_manifest(report, artifact)
    if expected_manifest.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("RGBA replay archive manifest is not reproducible")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("RGBA replay archive registry entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("RGBA replay archive registry report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("RGBA replay archive registry status mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_geon_rgba_replay_frame_archive()
    print("D20 geon RGBA replay frame archive validated")
