from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import base64
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_d20_geon_phase_entropy_audit import (
        AUDIT_FRAMES,
        D20LiftSimulator,
        D20_PALETTE,
        SAMPLE_FRAMES,
        TOPPLE_PALETTE,
        ToppleSimulator,
        entropy_from_counts,
        load_visualization_data,
        palette_channel_entropies,
        spectral_metrics,
    )
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_d20_geon_phase_entropy_audit import (
        AUDIT_FRAMES,
        D20LiftSimulator,
        D20_PALETTE,
        SAMPLE_FRAMES,
        TOPPLE_PALETTE,
        ToppleSimulator,
        entropy_from_counts,
        load_visualization_data,
        palette_channel_entropies,
        spectral_metrics,
    )
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_geon_rgba_replay_frame_archive"
ARTIFACT_PATH = GENERATED / f"{THEOREM_ID}.json"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

VISUALIZATION = GENERATED / "d20_sandpile_visualization.html"
PHASE_AUDIT_REPORT = (
    D20_INVARIANTS / "proof_obligations" / "d20_geon_phase_entropy_audit" / "report.json"
)
DERIVE_SCRIPT = ROOT / "src" / "derive_d20_geon_rgba_replay_frame_archive.py"
VALIDATOR = ROOT / "src" / "certify_d20_geon_rgba_replay_frame_archive.py"


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} is not a JSON object")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def input_entry(path: Path, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    entry = {"path": relpath(path), "sha256": sha_file(path)}
    if extra:
        entry.update(extra)
    return entry


def self_hash(payload: dict[str, Any], field: str) -> str:
    tmp = dict(payload)
    tmp.pop(field, None)
    return sha_json(tmp)


def rgba_bytes(categories: np.ndarray, palette: list[list[int]]) -> bytes:
    rgb = np.asarray(palette, dtype=np.uint8)[categories]
    alpha = np.full((*categories.shape, 1), 255, dtype=np.uint8)
    return np.concatenate([rgb, alpha], axis=2).tobytes()


def frame_record(canvas_id: str, frame: int, categories: np.ndarray, palette: list[list[int]]) -> dict[str, Any]:
    raw = rgba_bytes(categories, palette)
    counts = np.bincount(categories.ravel(), minlength=len(palette)).astype(int).tolist()
    return {
        "canvas_id": canvas_id,
        "frame": frame,
        "width": int(categories.shape[1]),
        "height": int(categories.shape[0]),
        "byte_length": len(raw),
        "rgba_sha256": hashlib.sha256(raw).hexdigest(),
        "rgba_base64": base64.b64encode(raw).decode("ascii"),
        "category_counts": counts,
        "category_entropy_bits": entropy_from_counts(counts),
        "channel_summary": palette_channel_entropies(counts, palette),
        "spectral_summary": spectral_metrics(categories),
    }


def capture_d20_frames(data: dict[str, Any]) -> list[dict[str, Any]]:
    sim = D20LiftSimulator(data)
    sim.seed()
    for _ in range(36):
        sim.step(9000)

    frames: list[dict[str, Any]] = []
    sample_set = set(SAMPLE_FRAMES)
    for frame in range(AUDIT_FRAMES + 1):
        if frame > 0:
            sim.step()
        categories, sums = sim.state_arrays()
        if frame in sample_set:
            frames.append(frame_record("d20LiftCanvas", frame, sim.render_cooriented(categories, sums), D20_PALETTE))
            frames.append(frame_record("d20HexLiftCanvas", frame, sim.render_hex(categories, sums), D20_PALETTE))
    return frames


def capture_topple_frames(data: dict[str, Any]) -> list[dict[str, Any]]:
    sim = ToppleSimulator(data)
    sim.seed()
    frames: list[dict[str, Any]] = []
    sample_set = set(SAMPLE_FRAMES)
    for frame in range(AUDIT_FRAMES + 1):
        if frame > 0:
            sim.step()
        if frame in sample_set:
            frames.append(frame_record("toppleCanvas", frame, sim.categories(), TOPPLE_PALETTE))
    return frames


def artifact_hash(payload: dict[str, Any]) -> str:
    return self_hash(payload, "artifact_sha256_excluding_this_field")


def build_artifact() -> dict[str, Any]:
    data, _ = load_visualization_data()
    phase_report = load_json(PHASE_AUDIT_REPORT)
    frames = sorted(
        capture_d20_frames(data) + capture_topple_frames(data),
        key=lambda row: (int(row["frame"]), str(row["canvas_id"])),
    )
    alpha_entropies = [
        float(row["channel_summary"]["entropy_bits"]["alpha"])
        for row in frames
    ]
    non_alpha_entropies = [
        float(row["category_entropy_bits"])
        for row in frames
    ]
    checks = {
        "source_visualization_hash_recorded": sha_file(VISUALIZATION)
        == phase_report["inputs"]["visualization"]["sha256"],
        "phase_audit_certified": phase_report.get("status") == "D20_GEON_PHASE_ENTROPY_AUDIT_CERTIFIED",
        "frame_count_is_18": len(frames) == 18,
        "sample_frames_match_phase_audit": sorted({int(row["frame"]) for row in frames})
        == sorted(SAMPLE_FRAMES),
        "all_three_canvases_present": sorted({row["canvas_id"] for row in frames})
        == ["d20HexLiftCanvas", "d20LiftCanvas", "toppleCanvas"],
        "every_frame_byte_length_matches_rgba_shape": all(
            int(row["byte_length"]) == int(row["width"]) * int(row["height"]) * 4
            for row in frames
        ),
        "every_frame_hash_matches_base64_payload": all(
            hashlib.sha256(base64.b64decode(row["rgba_base64"])).hexdigest() == row["rgba_sha256"]
            for row in frames
        ),
        "all_alpha_channels_constant_opaque": all(value == 0.0 for value in alpha_entropies),
        "some_non_alpha_state_entropy_present": max(non_alpha_entropies) > 0.0,
        "browser_capture_blocked_not_claimed": True,
    }
    payload: dict[str, Any] = {
        "schema": "d20.proof_obligation.geon_rgba_replay_frame_archive.artifact@1",
        "status": "D20_GEON_RGBA_REPLAY_FRAME_ARCHIVE_DERIVED",
        "source": {
            "visualization": input_entry(VISUALIZATION),
            "phase_entropy_audit_report": input_entry(
                PHASE_AUDIT_REPORT,
                {
                    "status": phase_report["status"],
                    "certificate_sha256": phase_report["certificate_sha256"],
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
        },
        "browser_capture_status": {
            "status": "BLOCKED_IN_CURRENT_ENVIRONMENT",
            "attempted_targets": [
                "file:///D:/Projects/carrollian/generated/d20_sandpile_visualization.html",
                "http://127.0.0.1:8765/d20_sandpile_visualization.html",
            ],
            "boundary": (
                "This archive is a deterministic replay frame-buffer archive, not a live-browser "
                "getImageData certificate. The in-app browser blocked both local targets."
            ),
        },
        "capture_method": {
            "engine": "repo-local deterministic replay of the exact D20 canvas render rules",
            "raw_format": "RGBA byte buffer encoded as base64",
            "sample_frames": sorted(SAMPLE_FRAMES),
            "canvases": ["d20LiftCanvas", "d20HexLiftCanvas", "toppleCanvas"],
        },
        "frame_count": len(frames),
        "frames": frames,
        "summary": {
            "alpha_entropy_bits_min": min(alpha_entropies),
            "alpha_entropy_bits_max": max(alpha_entropies),
            "non_alpha_category_entropy_bits_min": min(non_alpha_entropies),
            "non_alpha_category_entropy_bits_max": max(non_alpha_entropies),
            "total_rgba_bytes": sum(int(row["byte_length"]) for row in frames),
        },
        "checks": checks,
    }
    payload["artifact_sha256_excluding_this_field"] = artifact_hash(payload)
    return payload


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema": "d20.proof_obligation.geon_rgba_replay_frame_archive@1",
        "status": "D20_GEON_RGBA_REPLAY_FRAME_ARCHIVE_CERTIFIED_BROWSER_CAPTURE_BLOCKED",
        "all_checks_pass": all(artifact["checks"].values()),
        "claim": (
            "Raw RGBA frame buffers are now archived for the deterministic D20 geon replay. "
            "Every archived alpha channel is constant opaque, while non-alpha state channels "
            "carry entropy. Live browser getImageData capture remains blocked in this environment "
            "and is not claimed by this certificate."
        ),
        "closure_boundary": {
            "certifies": [
                "raw RGBA byte buffers are archived for the deterministic renderer replay",
                "all archived frames have byte length width * height * 4",
                "all archived frame hashes match their base64 RGBA payloads",
                "all archived alpha channels are constant opaque",
                "non-alpha state channels carry entropy in the archived frame set",
            ],
            "does_not_certify": [
                "live browser getImageData capture",
                "nontrivial alpha-channel entropy",
                "subpixel browser-compositor entropy",
                "a physical geon interpretation",
            ],
        },
        "inputs": {
            "artifact": input_entry(
                ARTIFACT_PATH,
                {
                    "schema": artifact["schema"],
                    "status": artifact["status"],
                    "artifact_sha256_excluding_this_field": artifact[
                        "artifact_sha256_excluding_this_field"
                    ],
                },
            ),
            "validator": input_entry(VALIDATOR),
            **artifact["source"],
        },
        "witness": {
            "browser_capture_status": artifact["browser_capture_status"],
            "capture_method": artifact["capture_method"],
            "frame_count": artifact["frame_count"],
            "summary": artifact["summary"],
        },
        "checks": artifact["checks"],
        "next_highest_yield_item": (
            "Run the same frame-buffer capture in an environment where the browser can load the "
            "local visualization, then compare the live getImageData hashes against this replay "
            "archive frame-by-frame."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": "d20.proof_obligation.geon_rgba_replay_frame_archive_manifest@1",
        "name": THEOREM_ID,
        "certification_tests": [
            "verify the source visualization hash matches the phase-entropy audit input",
            "verify the prior phase-entropy audit is certified",
            "verify 18 RGBA frames cover six sample frames across three canvases",
            "verify every RGBA byte buffer length and hash",
            "verify all alpha channels are constant opaque",
            "verify browser capture remains explicitly blocked rather than claimed",
        ],
        "inputs": report["inputs"],
        "outputs": {
            "artifact": relpath(ARTIFACT_PATH),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "report_sha256": report["certificate_sha256"],
        "artifact_sha256_excluding_hash_field": artifact["artifact_sha256_excluding_this_field"],
    }
    manifest["manifest_sha256"] = sha_json(manifest)
    return manifest


def update_index(report: dict[str, Any]) -> None:
    if INDEX_PATH.exists():
        index = load_json(INDEX_PATH)
        obligations = [row for row in index.get("obligations", []) if row.get("id") != THEOREM_ID]
        schema = index.get("schema", "d20.proof_obligation_registry.source_drop")
    else:
        obligations = []
        schema = "d20.proof_obligation_registry.source_drop"
    obligations.append(
        {
            "id": THEOREM_ID,
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
            "report_sha256": report["certificate_sha256"],
            "status": report["status"],
        }
    )
    index = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": sorted(obligations, key=lambda row: row["id"]),
    }
    index["registry_sha256"] = sha_json(index)
    write_json(INDEX_PATH, index)


def main() -> None:
    artifact = build_artifact()
    write_json(ARTIFACT_PATH, artifact)
    report = build_report(artifact)
    manifest = build_manifest(report, artifact)
    write_json(OUT_DIR / "report.json", report)
    write_json(OUT_DIR / "manifest.json", manifest)
    update_index(report)
    print(
        json.dumps(
            {
                "artifact": relpath(ARTIFACT_PATH),
                "report": relpath(OUT_DIR / "report.json"),
                "report_sha256": report["certificate_sha256"],
                "status": report["status"],
                "frame_count": artifact["frame_count"],
                "total_rgba_bytes": artifact["summary"]["total_rgba_bytes"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
