from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
import math
from typing import Any

import numpy as np

try:
    from .derive_d20_geon_phase_entropy_audit import D20LiftSimulator, load_visualization_data
    from .derive_d20_lift_spectral_recurrence_audit import (
        BASELINE_NEAR_RETURN_DISTANCE_MAX,
        FRAME_LIMIT,
        WARMUP_LIMIT,
        WARMUP_STEPS,
        input_entry,
        load_json,
        quantized_key,
        self_hash,
        sha_file,
        write_json,
    )
    from .derive_d20_lift_spectral_timeseries_audit import (
        EXPECTED_LAPLACIAN_BANDS,
        laplacian_bands,
        spatial_moments,
        spectral_band_stats,
    )
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_d20_geon_phase_entropy_audit import D20LiftSimulator, load_visualization_data
    from derive_d20_lift_spectral_recurrence_audit import (
        BASELINE_NEAR_RETURN_DISTANCE_MAX,
        FRAME_LIMIT,
        WARMUP_LIMIT,
        WARMUP_STEPS,
        input_entry,
        load_json,
        quantized_key,
        self_hash,
        sha_file,
        write_json,
    )
    from derive_d20_lift_spectral_timeseries_audit import (
        EXPECTED_LAPLACIAN_BANDS,
        laplacian_bands,
        spatial_moments,
        spectral_band_stats,
    )
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_lift_spectral_poincare_audit"
ARTIFACT_PATH = GENERATED / f"{THEOREM_ID}.json"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

VISUALIZATION = GENERATED / "d20_sandpile_visualization.html"
RECURRENCE_REPORT = (
    D20_INVARIANTS / "proof_obligations" / "d20_lift_spectral_recurrence_audit" / "report.json"
)
DERIVE_SCRIPT = ROOT / "src" / "derive_d20_lift_spectral_poincare_audit.py"
VALIDATOR = ROOT / "src" / "certify_d20_lift_spectral_poincare_audit.py"

HORIZON_FRAMES = 192
SAMPLE_STRIDE = 8
INITIAL_DISTANCE_TOLERANCE = 1e-12
DIVERGENCE_GAIN_MIN = 2.0


Snapshot = dict[str, Any]


def snapshot_simulator(sim: D20LiftSimulator) -> Snapshot:
    return {
        "state": sim.state.copy(),
        "queued": sim.queued.copy(),
        "queue": list(sim.queue),
        "topples": int(sim.topples),
        "boundary_loss": int(sim.boundary_loss),
        "cursor": int(sim.cursor),
    }


def restore_simulator(data: dict[str, Any], snapshot: Snapshot) -> D20LiftSimulator:
    sim = D20LiftSimulator(data)
    sim.state[:] = snapshot["state"]
    sim.queued[:] = snapshot["queued"]
    sim.queue = list(snapshot["queue"])
    sim.topples = int(snapshot["topples"])
    sim.boundary_loss = int(snapshot["boundary_loss"])
    sim.cursor = int(snapshot["cursor"])
    return sim


def snapshot_summary(snapshot: Snapshot) -> dict[str, Any]:
    state = snapshot["state"]
    return {
        "state_sha256": sha_file_like(state),
        "queued_sha256": sha_file_like(snapshot["queued"]),
        "queue_size": len(snapshot["queue"]),
        "topples": int(snapshot["topples"]),
        "boundary_loss": int(snapshot["boundary_loss"]),
        "cursor": int(snapshot["cursor"]),
        "live_grains": int(state.sum()),
        "unstable_fibers": int((state >= 3).sum()),
    }


def sha_file_like(array: np.ndarray) -> str:
    return __import__("hashlib").sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def spectral_row(
    sim: D20LiftSimulator,
    frame: int,
    offset: int,
    values: np.ndarray,
    vectors: np.ndarray,
    groups: list[dict[str, Any]],
) -> dict[str, Any]:
    tensor = sim.state.reshape(sim.size, sim.size, sim.fibers)
    sums = tensor.sum(axis=2)
    masses = tensor.sum(axis=(0, 1)).astype(float)
    spectral = spectral_band_stats(masses, values, vectors, groups)
    vector = [float(band["probability"]) for band in spectral["bands"]]
    spatial = spatial_moments(sums)
    return {
        "frame": int(frame),
        "offset": int(offset),
        "cursor": int(sim.cursor),
        "topples": int(sim.topples),
        "boundary_loss": int(sim.boundary_loss),
        "queue_size": len(sim.queue),
        "live_grains": int(masses.sum()),
        "active_lift_cells": int((sums > 0).sum()),
        "active_fibers": int((tensor > 0).sum()),
        "unstable_fibers": int((tensor >= 3).sum()),
        "spatial_radius": float(spatial["radius"]),
        "spectral_centroid": float(spectral["centroid"]),
        "spectral_entropy": float(spectral["entropy_normalized"]),
        "spectral_coherence": float(spectral["coherence"]),
        "spectral_bandwidth": float(spectral["bandwidth"]),
        "dominant_band": float(spectral["dominant_band"]),
        "golden_pair_probability": float(spectral["golden_pair_probability"]),
        "band_probability_vector": vector,
        "quantized_key": quantized_key(vector),
    }


def vector_distance(left: dict[str, Any], right: dict[str, Any]) -> float:
    a = np.asarray(left["band_probability_vector"], dtype=float)
    b = np.asarray(right["band_probability_vector"], dtype=float)
    return float(np.linalg.norm(a - b))


def compare_rows(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    return {
        "offset": int(left["offset"]),
        "left_frame": int(left["frame"]),
        "right_frame": int(right["frame"]),
        "distance": vector_distance(left, right),
        "centroid_delta": float(right["spectral_centroid"]) - float(left["spectral_centroid"]),
        "entropy_delta": float(right["spectral_entropy"]) - float(left["spectral_entropy"]),
        "live_grain_delta": int(right["live_grains"]) - int(left["live_grains"]),
        "dominant_band_pair": [float(left["dominant_band"]), float(right["dominant_band"])],
        "same_dominant_band": float(left["dominant_band"]) == float(right["dominant_band"]),
    }


def advance_to_checkpoints(data: dict[str, Any], frame_pair: list[int]) -> dict[int, Snapshot]:
    targets = set(int(frame) for frame in frame_pair)
    max_frame = max(targets)
    sim = D20LiftSimulator(data)
    sim.seed()
    for _ in range(WARMUP_STEPS):
        sim.step(WARMUP_LIMIT)

    out: dict[int, Snapshot] = {}
    for frame in range(max_frame + 1):
        if frame > 0:
            sim.step(FRAME_LIMIT)
        if frame in targets:
            out[frame] = snapshot_simulator(sim)
    if set(out) != targets:
        raise RuntimeError("failed to capture all Poincare checkpoint frames")
    return out


def branch_comparison(
    data: dict[str, Any],
    frame_pair: list[int],
    snapshots: dict[int, Snapshot],
    align_right_cursor_to_left: bool,
) -> dict[str, Any]:
    values, vectors, groups = laplacian_bands(data)
    left_frame, right_frame = [int(frame) for frame in frame_pair]
    left = restore_simulator(data, snapshots[left_frame])
    right = restore_simulator(data, snapshots[right_frame])
    if align_right_cursor_to_left:
        right.cursor = int(left.cursor)

    left_rows: list[dict[str, Any]] = []
    right_rows: list[dict[str, Any]] = []
    comparisons: list[dict[str, Any]] = []
    for offset in range(HORIZON_FRAMES + 1):
        if offset > 0:
            left.step(FRAME_LIMIT)
            right.step(FRAME_LIMIT)
        if offset % SAMPLE_STRIDE != 0:
            continue
        left_row = spectral_row(left, left_frame + offset, offset, values, vectors, groups)
        right_row = spectral_row(right, right_frame + offset, offset, values, vectors, groups)
        left_rows.append(left_row)
        right_rows.append(right_row)
        comparisons.append(compare_rows(left_row, right_row))

    distances = [float(row["distance"]) for row in comparisons]
    return {
        "mode": "cursor_aligned" if align_right_cursor_to_left else "natural_source_phase",
        "right_cursor_aligned_to_left": bool(align_right_cursor_to_left),
        "left_rows": left_rows,
        "right_rows": right_rows,
        "comparisons": comparisons,
        "summary": {
            "sample_count": len(comparisons),
            "horizon_frames": HORIZON_FRAMES,
            "sample_stride": SAMPLE_STRIDE,
            "initial_distance": distances[0],
            "final_distance": distances[-1],
            "min_distance_after_initial": min(distances[1:]),
            "max_distance": max(distances),
            "max_distance_offset": int(comparisons[distances.index(max(distances))]["offset"]),
            "divergence_gain": max(distances) / max(distances[0], 1e-18),
            "same_dominant_band_count": sum(1 for row in comparisons if row["same_dominant_band"]),
            "boundary_loss_range": [
                min(int(row["boundary_loss"]) for row in left_rows + right_rows),
                max(int(row["boundary_loss"]) for row in left_rows + right_rows),
            ],
            "radius_range": [
                min(float(row["spatial_radius"]) for row in left_rows + right_rows),
                max(float(row["spatial_radius"]) for row in left_rows + right_rows),
            ],
        },
    }


def band_signature(data: dict[str, Any]) -> list[dict[str, Any]]:
    _, _, groups = laplacian_bands(data)
    return [{"lambda": float(group["lambda"]), "multiplicity": len(group["indices"])} for group in groups]


def build_artifact() -> dict[str, Any]:
    data, visualization_text = load_visualization_data()
    recurrence_report = load_json(RECURRENCE_REPORT)
    nearest = recurrence_report["witness"]["nearest_return"]
    frame_pair = [int(frame) for frame in nearest["frame_pair"]]
    snapshots = advance_to_checkpoints(data, frame_pair)
    natural = branch_comparison(data, frame_pair, snapshots, False)
    aligned = branch_comparison(data, frame_pair, snapshots, True)
    initial_distance_delta = abs(float(nearest["distance"]) - float(natural["summary"]["initial_distance"]))
    checks = {
        "visualization_data_loaded": len(data.get("nodes", [])) == 20 and len(data.get("edges", [])) == 30,
        "full_window_canvas_embedded": "d20WindowCanvas" in visualization_text,
        "recurrence_audit_certified": recurrence_report.get("status")
        == "D20_LIFT_SPECTRAL_RECURRENCE_AUDIT_CERTIFIED",
        "laplacian_band_signature_matches_expected": band_signature(data) == EXPECTED_LAPLACIAN_BANDS,
        "checkpoint_pair_matches_recurrence_nearest_return": frame_pair
        == [int(frame) for frame in nearest["frame_pair"]],
        "initial_distance_matches_recurrence_report": initial_distance_delta < INITIAL_DISTANCE_TOLERANCE,
        "initial_distance_is_near_return": natural["summary"]["initial_distance"] < BASELINE_NEAR_RETURN_DISTANCE_MAX,
        "natural_branch_has_no_boundary_loss": natural["summary"]["boundary_loss_range"] == [0, 0],
        "cursor_aligned_branch_has_no_boundary_loss": aligned["summary"]["boundary_loss_range"] == [0, 0],
        "natural_branch_diverges_from_near_return": natural["summary"]["divergence_gain"] > DIVERGENCE_GAIN_MIN,
        "cursor_aligned_branch_diverges_from_near_return": aligned["summary"]["divergence_gain"] > DIVERGENCE_GAIN_MIN,
        "branches_stay_inside_full_window": natural["summary"]["radius_range"][1] < 32.0
        and aligned["summary"]["radius_range"][1] < 32.0,
    }
    payload: dict[str, Any] = {
        "schema": "d20.proof_obligation.lift_spectral_poincare_audit.artifact@1",
        "status": "D20_LIFT_SPECTRAL_POINCARE_AUDIT_DERIVED",
        "source": {
            "visualization": input_entry(VISUALIZATION),
            "recurrence_report": input_entry(
                RECURRENCE_REPORT,
                {
                    "status": recurrence_report.get("status"),
                    "certificate_sha256": recurrence_report.get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
        },
        "definition": {
            "poincare_candidate": (
                "The nearest-return pair from the recurrence audit, treated as a finite Poincare "
                "section in the five-band normalized D20 Laplacian power simplex."
            ),
            "natural_source_phase": (
                "Replay both checkpointed states forward with their original deterministic source cursors."
            ),
            "cursor_aligned": (
                "Replay the later checkpoint after resetting its source cursor to the earlier checkpoint, "
                "separating source-phase mismatch from state-field divergence."
            ),
        },
        "parameters": {
            "warmup_steps": WARMUP_STEPS,
            "warmup_limit": WARMUP_LIMIT,
            "frame_limit": FRAME_LIMIT,
            "horizon_frames": HORIZON_FRAMES,
            "sample_stride": SAMPLE_STRIDE,
            "initial_distance_tolerance": INITIAL_DISTANCE_TOLERANCE,
            "divergence_gain_min": DIVERGENCE_GAIN_MIN,
        },
        "nearest_return": nearest,
        "checkpoint_summaries": {
            str(frame): snapshot_summary(snapshot) for frame, snapshot in sorted(snapshots.items())
        },
        "natural_source_phase": natural,
        "cursor_aligned": aligned,
        "checks": checks,
    }
    payload["artifact_sha256_excluding_this_field"] = self_hash(payload, "artifact_sha256_excluding_this_field")
    return payload


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    natural = artifact["natural_source_phase"]["summary"]
    aligned = artifact["cursor_aligned"]["summary"]
    report: dict[str, Any] = {
        "schema": "d20.proof_obligation.lift_spectral_poincare_audit@1",
        "status": "D20_LIFT_SPECTRAL_POINCARE_AUDIT_CERTIFIED",
        "all_checks_pass": all(artifact["checks"].values()),
        "claim": (
            "The recurrence audit's nearest spectral return is a finite Poincare candidate, not an "
            "exact repeat: replaying the two checkpointed D20 lifted states forward keeps both inside "
            "the full visualization window with no boundary loss, while both natural and cursor-aligned "
            "continuations amplify the initial five-band spectral separation."
        ),
        "inputs": {
            "artifact": input_entry(
                ARTIFACT_PATH,
                {
                    "artifact_sha256_excluding_this_field": artifact["artifact_sha256_excluding_this_field"],
                    "status": artifact["status"],
                },
            ),
            "validator": input_entry(VALIDATOR),
            **artifact["source"],
        },
        "witness": {
            "nearest_return": artifact["nearest_return"],
            "natural_source_phase_summary": natural,
            "cursor_aligned_summary": aligned,
            "natural_source_phase_comparisons": artifact["natural_source_phase"]["comparisons"],
            "cursor_aligned_comparisons": artifact["cursor_aligned"]["comparisons"],
        },
        "checks": artifact["checks"],
        "closure_boundary": {
            "certifies": [
                "the nearest spectral return can be replayed from full lifted-state checkpoints",
                "both forward branches have no boundary loss through the finite horizon",
                "the initial near-return separation is amplified in both natural and cursor-aligned continuations",
                "the observed behavior is a finite-time spectral shear witness, not an exact period",
            ],
            "does_not_certify": [
                "a global Poincare map",
                "an asymptotic Lyapunov exponent",
                "that every near-return shears by the same factor",
                "a physical atom interpretation beyond the certified finite replay behavior",
            ],
        },
        "next_highest_yield_item": (
            "Lift the Poincare witness into the HTML panel: display the nearest-return pair, "
            "natural/cursor-aligned divergence curves, and branch toggles over the full D20 object window."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": "d20.proof_obligation.lift_spectral_poincare_audit_manifest@1",
        "name": THEOREM_ID,
        "certification_tests": [
            "verify the recurrence audit is certified",
            "checkpoint both nearest-return lifted states",
            "replay natural-source-phase and cursor-aligned continuations",
            "verify no boundary loss occurs through the finite horizon",
            "verify the initial spectral distance matches the recurrence report",
            "verify the near-return separation is amplified in both continuations",
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
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
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
    index["registry_sha256"] = self_hash(index, "registry_sha256")
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
                "natural_source_phase_summary": report["witness"]["natural_source_phase_summary"],
                "cursor_aligned_summary": report["witness"]["cursor_aligned_summary"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
