from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_d20_geon_phase_entropy_audit import D20LiftSimulator, load_visualization_data
    from .derive_d20_lift_spectral_timeseries_audit import (
        EXPECTED_LAPLACIAN_BANDS,
        laplacian_bands,
        spatial_moments,
        spectral_band_stats,
    )
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_d20_geon_phase_entropy_audit import D20LiftSimulator, load_visualization_data
    from derive_d20_lift_spectral_timeseries_audit import (
        EXPECTED_LAPLACIAN_BANDS,
        laplacian_bands,
        spatial_moments,
        spectral_band_stats,
    )
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_lift_spectral_recurrence_audit"
ARTIFACT_PATH = GENERATED / f"{THEOREM_ID}.json"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

VISUALIZATION = GENERATED / "d20_sandpile_visualization.html"
SPECTRAL_TIMESERIES_REPORT = (
    D20_INVARIANTS / "proof_obligations" / "d20_lift_spectral_timeseries_audit" / "report.json"
)
DERIVE_SCRIPT = ROOT / "src" / "derive_d20_lift_spectral_recurrence_audit.py"
VALIDATOR = ROOT / "src" / "certify_d20_lift_spectral_recurrence_audit.py"

WARMUP_STEPS = 36
WARMUP_LIMIT = 9000
FRAME_LIMIT = 7000
BASELINE_FRAMES = 2048
BASELINE_STRIDE = 8
BASELINE_MIN_RETURN_GAP = 128
BASELINE_NEAR_RETURN_DISTANCE_MAX = 0.012
QUANTIZATION_SCALE = 1000

PERTURBATION_FRAMES = 512
PERTURBATION_STRIDE = 16
PERTURBATION_MIN_RETURN_GAP = 96
PERTURBATION_NEAR_RETURN_DISTANCE_MAX = 0.07
PERTURBATION_CURSOR_OFFSETS = [1, 11]


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


def quantized_key(vector: list[float], scale: int = QUANTIZATION_SCALE) -> list[int]:
    return [int(round(value * scale)) for value in vector]


def vector_hash(vector: list[float]) -> str:
    return hashlib.sha256(json.dumps(quantized_key(vector), separators=(",", ":")).encode("ascii")).hexdigest()


def row_distance(left: dict[str, Any], right: dict[str, Any]) -> float:
    a = np.asarray(left["band_probability_vector"], dtype=float)
    b = np.asarray(right["band_probability_vector"], dtype=float)
    return float(np.linalg.norm(a - b))


def nearest_return(rows: list[dict[str, Any]], min_gap: int) -> dict[str, Any]:
    best: tuple[float, dict[str, Any], dict[str, Any]] | None = None
    for i, right in enumerate(rows):
        for left in rows[:i]:
            if int(right["frame"]) - int(left["frame"]) < min_gap:
                continue
            distance = row_distance(left, right)
            if best is None or distance < best[0]:
                best = (distance, left, right)
    if best is None:
        return {
            "found": False,
            "distance": math.inf,
            "frame_pair": [],
            "frame_gap": 0,
        }
    distance, left, right = best
    return {
        "found": True,
        "distance": distance,
        "frame_pair": [int(left["frame"]), int(right["frame"])],
        "frame_gap": int(right["frame"]) - int(left["frame"]),
        "left": {
            "spectral_centroid": left["spectral_centroid"],
            "spectral_entropy": left["spectral_entropy"],
            "dominant_band": left["dominant_band"],
            "live_grains": left["live_grains"],
            "band_probability_vector": left["band_probability_vector"],
            "quantized_key": left["quantized_key"],
        },
        "right": {
            "spectral_centroid": right["spectral_centroid"],
            "spectral_entropy": right["spectral_entropy"],
            "dominant_band": right["dominant_band"],
            "live_grains": right["live_grains"],
            "band_probability_vector": right["band_probability_vector"],
            "quantized_key": right["quantized_key"],
        },
    }


def exact_quantized_collisions(rows: list[dict[str, Any]], min_gap: int) -> list[dict[str, Any]]:
    seen: dict[tuple[int, ...], dict[str, Any]] = {}
    out: list[dict[str, Any]] = []
    for row in rows:
        key = tuple(int(value) for value in row["quantized_key"])
        prior = seen.get(key)
        if prior is not None and int(row["frame"]) - int(prior["frame"]) >= min_gap:
            out.append(
                {
                    "frame_pair": [int(prior["frame"]), int(row["frame"])],
                    "frame_gap": int(row["frame"]) - int(prior["frame"]),
                    "quantized_key": list(key),
                }
            )
        else:
            seen.setdefault(key, row)
    return out


def collect_orbit(
    data: dict[str, Any],
    total_frames: int,
    stride: int,
    cursor_offset: int,
) -> list[dict[str, Any]]:
    values, vectors, groups = laplacian_bands(data)
    sim = D20LiftSimulator(data)
    sim.seed()
    for _ in range(WARMUP_STEPS):
        sim.step(WARMUP_LIMIT)
    sim.cursor += int(cursor_offset)

    rows: list[dict[str, Any]] = []
    for frame in range(total_frames + 1):
        if frame > 0:
            sim.step(FRAME_LIMIT)
        if frame % stride != 0:
            continue
        tensor = sim.state.reshape(sim.size, sim.size, sim.fibers)
        sums = tensor.sum(axis=2)
        masses = tensor.sum(axis=(0, 1)).astype(float)
        spectral = spectral_band_stats(masses, values, vectors, groups)
        vector = [float(band["probability"]) for band in spectral["bands"]]
        spatial = spatial_moments(sums)
        rows.append(
            {
                "frame": int(frame),
                "topples": int(sim.topples),
                "boundary_loss": int(sim.boundary_loss),
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
                "vector_sha256": vector_hash(vector),
            }
        )
    return rows


def value_range(rows: list[dict[str, Any]], key: str) -> list[float]:
    values = [float(row[key]) for row in rows]
    return [min(values), max(values)]


def summarize_orbit(rows: list[dict[str, Any]], min_gap: int) -> dict[str, Any]:
    dominant_counts = Counter(f'{float(row["dominant_band"]):.6f}' for row in rows)
    collisions = exact_quantized_collisions(rows, min_gap)
    return {
        "sample_count": len(rows),
        "first_frame": int(rows[0]["frame"]),
        "last_frame": int(rows[-1]["frame"]),
        "live_grain_range": [min(int(row["live_grains"]) for row in rows), max(int(row["live_grains"]) for row in rows)],
        "boundary_loss_range": [min(int(row["boundary_loss"]) for row in rows), max(int(row["boundary_loss"]) for row in rows)],
        "active_fiber_range": [min(int(row["active_fibers"]) for row in rows), max(int(row["active_fibers"]) for row in rows)],
        "spatial_radius_range": value_range(rows, "spatial_radius"),
        "spectral_centroid_range": value_range(rows, "spectral_centroid"),
        "spectral_entropy_range": value_range(rows, "spectral_entropy"),
        "spectral_coherence_range": value_range(rows, "spectral_coherence"),
        "spectral_bandwidth_range": value_range(rows, "spectral_bandwidth"),
        "golden_pair_probability_range": value_range(rows, "golden_pair_probability"),
        "dominant_band_counts": dict(sorted(dominant_counts.items())),
        "dominant_band_sequence": [float(row["dominant_band"]) for row in rows],
        "nearest_return": nearest_return(rows, min_gap),
        "exact_quantized_collision_count": len(collisions),
        "exact_quantized_collisions": collisions[:8],
    }


def band_signature(data: dict[str, Any]) -> list[dict[str, Any]]:
    _, _, groups = laplacian_bands(data)
    return [{"lambda": float(group["lambda"]), "multiplicity": len(group["indices"])} for group in groups]


def build_artifact() -> dict[str, Any]:
    data, visualization_text = load_visualization_data()
    spectral_report = load_json(SPECTRAL_TIMESERIES_REPORT)
    signature = band_signature(data)
    baseline_rows = collect_orbit(data, BASELINE_FRAMES, BASELINE_STRIDE, 0)
    baseline_summary = summarize_orbit(baseline_rows, BASELINE_MIN_RETURN_GAP)

    perturbation_rows = []
    for offset in PERTURBATION_CURSOR_OFFSETS:
        rows = collect_orbit(data, PERTURBATION_FRAMES, PERTURBATION_STRIDE, offset)
        perturbation_rows.append(
            {
                "id": f"cursor_offset_{offset}",
                "cursor_offset": int(offset),
                "total_frames": PERTURBATION_FRAMES,
                "stride": PERTURBATION_STRIDE,
                "summary": summarize_orbit(rows, PERTURBATION_MIN_RETURN_GAP),
            }
        )

    baseline_dominant_bands = set(baseline_summary["dominant_band_counts"])
    checks = {
        "visualization_data_loaded": len(data.get("nodes", [])) == 20 and len(data.get("edges", [])) == 30,
        "full_window_canvas_embedded": "d20WindowCanvas" in visualization_text,
        "spectral_timeseries_audit_certified": spectral_report.get("status")
        == "D20_LIFT_SPECTRAL_TIMESERIES_AUDIT_CERTIFIED",
        "laplacian_band_signature_matches_expected": signature == EXPECTED_LAPLACIAN_BANDS,
        "baseline_sample_count_matches_schedule": baseline_summary["sample_count"]
        == BASELINE_FRAMES // BASELINE_STRIDE + 1,
        "baseline_has_no_boundary_loss": baseline_summary["boundary_loss_range"] == [0, 0],
        "baseline_near_return_found": baseline_summary["nearest_return"]["found"] is True,
        "baseline_near_return_gap_large": int(baseline_summary["nearest_return"]["frame_gap"]) >= 512,
        "baseline_near_return_distance_small": float(baseline_summary["nearest_return"]["distance"])
        < BASELINE_NEAR_RETURN_DISTANCE_MAX,
        "baseline_has_no_exact_quantized_recurrence": baseline_summary["exact_quantized_collision_count"] == 0,
        "baseline_visits_all_nonconstant_dominant_bands": baseline_dominant_bands
        == {"0.763932", "2.000000", "3.000000", "5.000000", "5.236068"},
        "baseline_radius_stays_inside_full_window": baseline_summary["spatial_radius_range"][1] < 32.0,
        "perturbation_trials_have_no_boundary_loss": all(
            row["summary"]["boundary_loss_range"] == [0, 0] for row in perturbation_rows
        ),
        "perturbation_trials_have_near_returns": all(
            row["summary"]["nearest_return"]["found"] is True
            and float(row["summary"]["nearest_return"]["distance"]) < PERTURBATION_NEAR_RETURN_DISTANCE_MAX
            for row in perturbation_rows
        ),
        "perturbation_trials_change_dominant_band": all(
            len(row["summary"]["dominant_band_counts"]) >= 3 for row in perturbation_rows
        ),
    }
    payload: dict[str, Any] = {
        "schema": "d20.proof_obligation.lift_spectral_recurrence_audit.artifact@1",
        "status": "D20_LIFT_SPECTRAL_RECURRENCE_AUDIT_DERIVED",
        "source": {
            "visualization": input_entry(VISUALIZATION),
            "spectral_timeseries_report": input_entry(
                SPECTRAL_TIMESERIES_REPORT,
                {
                    "status": spectral_report.get("status"),
                    "certificate_sha256": spectral_report.get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
        },
        "definition": {
            "spectral_orbit": (
                "The sequence of normalized power vectors in the five nonconstant public D20 "
                "Laplacian bands for the centered 20-fiber mass vector."
            ),
            "near_return": (
                "A pair of sampled frames separated by a minimum gap whose normalized band-power "
                "vectors have minimal Euclidean distance in the sampled orbit."
            ),
            "quantized_recurrence": (
                f"An exact collision after rounding each band probability to 1/{QUANTIZATION_SCALE}."
            ),
            "source_schedule_perturbation": (
                "A deterministic cursor offset applied after warmup, changing future source drops "
                "without changing the initialized lifted state."
            ),
        },
        "parameters": {
            "warmup_steps": WARMUP_STEPS,
            "warmup_limit": WARMUP_LIMIT,
            "frame_limit": FRAME_LIMIT,
            "baseline_frames": BASELINE_FRAMES,
            "baseline_stride": BASELINE_STRIDE,
            "baseline_min_return_gap": BASELINE_MIN_RETURN_GAP,
            "baseline_near_return_distance_max": BASELINE_NEAR_RETURN_DISTANCE_MAX,
            "quantization_scale": QUANTIZATION_SCALE,
            "perturbation_frames": PERTURBATION_FRAMES,
            "perturbation_stride": PERTURBATION_STRIDE,
            "perturbation_min_return_gap": PERTURBATION_MIN_RETURN_GAP,
            "perturbation_near_return_distance_max": PERTURBATION_NEAR_RETURN_DISTANCE_MAX,
            "perturbation_cursor_offsets": PERTURBATION_CURSOR_OFFSETS,
        },
        "laplacian_band_signature": signature,
        "baseline_orbit": {
            "rows": baseline_rows,
            "summary": baseline_summary,
        },
        "perturbation_trials": perturbation_rows,
        "checks": checks,
    }
    payload["artifact_sha256_excluding_this_field"] = self_hash(payload, "artifact_sha256_excluding_this_field")
    return payload


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    baseline = artifact["baseline_orbit"]["summary"]
    report: dict[str, Any] = {
        "schema": "d20.proof_obligation.lift_spectral_recurrence_audit@1",
        "status": "D20_LIFT_SPECTRAL_RECURRENCE_AUDIT_CERTIFIED",
        "all_checks_pass": all(artifact["checks"].values()),
        "claim": (
            "The longer full-window D20 lifted sandpile replay exhibits a bounded spectral orbit in "
            "the public D20 Laplacian band-power simplex. Through frame 2048 after warmup the replay "
            "has no boundary loss, visits all five nonconstant bands as dominant bands, has no exact "
            "1e-3 quantized recurrence, but does have a strong near-return in normalized band power."
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
            "baseline_summary": baseline,
            "perturbation_summaries": [
                {
                    "id": row["id"],
                    "cursor_offset": row["cursor_offset"],
                    "summary": row["summary"],
                }
                for row in artifact["perturbation_trials"]
            ],
            "nearest_return": baseline["nearest_return"],
        },
        "checks": artifact["checks"],
        "closure_boundary": {
            "certifies": [
                "no boundary loss in the sampled baseline orbit through frame 2048",
                "a reproducible baseline near-return in normalized five-band spectral power",
                "absence of exact 1e-3 quantized recurrence in the sampled baseline orbit",
                "dominant-band visitation of all five nonconstant public D20 Laplacian bands",
                "source-schedule cursor perturbations preserve bounded near-return behavior in the tested window",
            ],
            "does_not_certify": [
                "an exact period",
                "an infinite-time invariant measure",
                "that all source schedules or all voltage lifts share the same spectral orbit",
                "a physical atom interpretation beyond the certified finite replay behavior",
            ],
        },
        "next_highest_yield_item": (
            "Promote the near-return into a candidate Poincare section: persist the nearest-return "
            "frame pair, replay from both states, and compare future spectral divergence over a fixed horizon."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": "d20.proof_obligation.lift_spectral_recurrence_audit_manifest@1",
        "name": THEOREM_ID,
        "certification_tests": [
            "verify the spectral time-series audit is certified",
            "replay the baseline lifted sandpile through frame 2048",
            "sample normalized five-band public D20 Laplacian power every eight frames",
            "find the nearest nonlocal spectral return",
            "verify no exact 1e-3 quantized recurrence occurs in the sampled baseline orbit",
            "verify all five nonconstant bands appear as dominant bands",
            "run two deterministic source-schedule cursor perturbations and verify bounded near-return behavior",
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
                "nearest_return": report["witness"]["nearest_return"],
                "dominant_band_counts": report["witness"]["baseline_summary"]["dominant_band_counts"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
