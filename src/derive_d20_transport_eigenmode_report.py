from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_d20_geon_phase_entropy_audit import D20LiftSimulator, js_round, load_visualization_data
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_d20_geon_phase_entropy_audit import D20LiftSimulator, js_round, load_visualization_data
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_transport_eigenmode_report"
ARTIFACT_PATH = GENERATED / f"{THEOREM_ID}.json"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

STRESS_GRAPH_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_boundary_neighborhood_stress_graph"
STRESS_GRAPH_ARTIFACT = STRESS_GRAPH_DIR / "artifact.json"
STRESS_GRAPH_REPORT = STRESS_GRAPH_DIR / "report.json"
VISUALIZATION = GENERATED / "d20_sandpile_visualization.html"
DERIVE_SCRIPT = ROOT / "src" / "derive_d20_transport_eigenmode_report.py"
VALIDATOR = ROOT / "src" / "certify_d20_transport_eigenmode_report.py"

D20_LIFT_SIZE = 128
D20_LIFT_FIBERS = 20
WARMUP_STEPS = 36
REPLAY_FRAMES = 96
STEP_LIMIT = 9000
SHUFFLE_MULTIPLIER = 7
SHUFFLE_OFFSET = 11


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


def normalize_signed_vector(values: np.ndarray) -> np.ndarray:
    vector = np.asarray(values, dtype=float).copy()
    vector -= float(vector.mean()) if vector.size else 0.0
    norm = float(np.linalg.norm(vector))
    if norm == 0.0:
        return np.zeros_like(vector)
    return vector / norm


def stress_graph_rows(stress_artifact: dict[str, Any]) -> list[dict[str, Any]]:
    rows = stress_artifact.get("witness", {}).get("graph_rows", [])
    if not isinstance(rows, list) or len(rows) != D20_LIFT_FIBERS:
        raise ValueError("stress graph artifact does not contain 20 graph rows")
    return rows


def signed_tension(rows: list[dict[str, Any]]) -> np.ndarray:
    return np.asarray([float(row["signed_tension"]) for row in rows], dtype=float)


def shuffled_index(index: int) -> int:
    return (index * SHUFFLE_MULTIPLIER + SHUFFLE_OFFSET) % D20_LIFT_FIBERS


def smoothed_tension(atom_id: int, rows: list[dict[str, Any]]) -> float:
    atom = max(0, min(D20_LIFT_FIBERS - 1, int(atom_id)))
    base = float(rows[atom]["signed_tension"])
    signed = base * 0.45
    norm = 0.45
    for neighbor in rows[atom].get("neighbors", []):
        weight = float(neighbor["weight"])
        signed += weight * float(neighbor["signed_tension"])
        norm += weight
    return signed / norm if norm else base


def compute_transport_mode(rows: list[dict[str, Any]], null_model: bool) -> np.ndarray:
    base = signed_tension(rows)

    def source_at(index: int) -> float:
        return float(base[shuffled_index(index) if null_model else index])

    mode = normalize_signed_vector(np.asarray([source_at(i) for i in range(D20_LIFT_FIBERS)], dtype=float))
    for _ in range(72):
        next_mode = np.zeros(D20_LIFT_FIBERS, dtype=float)
        for atom_id in range(D20_LIFT_FIBERS):
            value = source_at(atom_id) * 0.52 + mode[atom_id] * 0.14
            norm = 0.66
            for neighbor in rows[atom_id].get("neighbors", []):
                j = int(neighbor["atom_id"])
                weight = float(neighbor["weight"])
                value += weight * mode[j]
                norm += weight
            next_mode[atom_id] = value / norm if norm else value
        mode = normalize_signed_vector(next_mode)
    anchor = normalize_signed_vector(np.asarray([source_at(i) for i in range(D20_LIFT_FIBERS)], dtype=float))
    if float(np.dot(mode, anchor)) < 0.0:
        mode = -mode
    return mode


def mode_alignment(signal: np.ndarray, mode: np.ndarray) -> float:
    normalized = normalize_signed_vector(signal)
    if float(np.linalg.norm(normalized)) == 0.0:
        return 0.0
    return max(0.0, min(1.0, abs(float(np.dot(normalized, mode)))))


def collect_live_mode_signal(sim: D20LiftSimulator, rows: list[dict[str, Any]]) -> tuple[np.ndarray, int]:
    _categories, sums = sim.state_arrays()
    center_x, center_y, half_span = sim.bounding_box(sums)
    signal = np.zeros(D20_LIFT_FIBERS, dtype=float)
    active = 0
    for y in range(D20_LIFT_SIZE):
        sy = max(
            0,
            min(
                D20_LIFT_SIZE - 1,
                js_round(center_y - half_span + ((y + 0.5) / D20_LIFT_SIZE) * half_span * 2.0),
            ),
        )
        for x in range(D20_LIFT_SIZE):
            sx = max(
                0,
                min(
                    D20_LIFT_SIZE - 1,
                    js_round(center_x - half_span + ((x + 0.5) / D20_LIFT_SIZE) * half_span * 2.0),
                ),
            )
            sample = sim.sample_cell(sx, sy)
            total = int(sample["sum"])
            if total <= 0:
                continue
            dominant = int(sample["dominant_fiber"])
            load = max(0.0, min(1.0, math.log1p(total) / 9.0))
            signal[dominant] += smoothed_tension(dominant, rows) * load
            active += 1
    return signal, active


def summarize_frames(samples: list[dict[str, Any]]) -> dict[str, Any]:
    real = np.asarray([float(sample["real_alignment"]) for sample in samples], dtype=float)
    null = np.asarray([float(sample["null_alignment"]) for sample in samples], dtype=float)
    gap = real - null
    positive = gap > 0.0
    return {
        "frame_count": len(samples),
        "real_alignment_mean": float(real.mean()),
        "real_alignment_min": float(real.min()),
        "real_alignment_max": float(real.max()),
        "null_alignment_mean": float(null.mean()),
        "null_alignment_min": float(null.min()),
        "null_alignment_max": float(null.max()),
        "real_minus_null_gap_mean": float(gap.mean()),
        "real_minus_null_gap_min": float(gap.min()),
        "real_minus_null_gap_max": float(gap.max()),
        "positive_gap_frame_count": int(positive.sum()),
        "positive_gap_fraction": float(positive.mean()),
        "active_cells_mean": float(np.mean([int(sample["active_cells"]) for sample in samples])),
    }


def support_status(summary: dict[str, Any]) -> str:
    if summary["real_minus_null_gap_mean"] > 0.08 and summary["positive_gap_fraction"] >= 0.72:
        return "REAL_MODE_ADVANTAGE"
    if abs(summary["real_minus_null_gap_mean"]) <= 0.03:
        return "NULL_COMPETITIVE"
    if summary["real_minus_null_gap_mean"] < 0.0:
        return "NULL_MODE_ADVANTAGE"
    return "WEAK_REAL_MODE_ADVANTAGE"


def build_artifact() -> dict[str, Any]:
    stress_artifact = load_json(STRESS_GRAPH_ARTIFACT)
    stress_report = load_json(STRESS_GRAPH_REPORT)
    data, visualization_text = load_visualization_data()
    rows = stress_graph_rows(stress_artifact)
    real_mode = compute_transport_mode(rows, False)
    null_mode = compute_transport_mode(rows, True)
    null_permutation = [shuffled_index(i) for i in range(D20_LIFT_FIBERS)]

    sim = D20LiftSimulator(data)
    sim.seed()
    for _ in range(WARMUP_STEPS):
        sim.step(STEP_LIMIT)

    frame_samples: list[dict[str, Any]] = []
    for frame in range(REPLAY_FRAMES):
        signal, active = collect_live_mode_signal(sim, rows)
        frame_samples.append(
            {
                "frame": frame,
                "active_cells": active,
                "real_alignment": float(mode_alignment(signal, real_mode)),
                "null_alignment": float(mode_alignment(signal, null_mode)),
                "signal_l2_norm": float(np.linalg.norm(normalize_signed_vector(signal))),
            }
        )
        sim.step(STEP_LIMIT)

    summary = summarize_frames(frame_samples)
    conclusion = support_status(summary)
    mode_overlap = float(np.dot(real_mode, null_mode))
    checks = {
        "stress_graph_certified": stress_artifact.get("status")
        == "C985_D20_BOUNDARY_NEIGHBORHOOD_STRESS_GRAPH_CERTIFIED"
        and stress_report.get("status") == "C985_D20_BOUNDARY_NEIGHBORHOOD_STRESS_GRAPH_CERTIFIED",
        "renderer_embeds_eigenmode_witness": "d20AtlasModeAlignment" in visualization_text
        and "computeD20AtlasTransportMode" in visualization_text,
        "real_mode_unit_norm": abs(float(np.linalg.norm(real_mode)) - 1.0) < 1e-12,
        "null_mode_unit_norm": abs(float(np.linalg.norm(null_mode)) - 1.0) < 1e-12,
        "null_assignment_is_permutation": sorted(null_permutation) == list(range(D20_LIFT_FIBERS)),
        "replay_frames_present": len(frame_samples) == REPLAY_FRAMES,
        "alignment_values_finite": all(
            math.isfinite(float(sample["real_alignment"]))
            and math.isfinite(float(sample["null_alignment"]))
            for sample in frame_samples
        ),
        "active_cells_nonzero": summary["active_cells_mean"] > 0.0,
    }
    payload: dict[str, Any] = {
        "schema": "d20.transport_eigenmode_report.artifact@1",
        "status": "D20_TRANSPORT_EIGENMODE_REPORT_DERIVED",
        "source": {
            "stress_graph_artifact": input_entry(
                STRESS_GRAPH_ARTIFACT,
                {
                    "schema": stress_artifact.get("schema"),
                    "status": stress_artifact.get("status"),
                    "artifact_sha256_excluding_this_field": stress_artifact.get(
                        "artifact_sha256_excluding_this_field"
                    ),
                },
            ),
            "stress_graph_report": input_entry(
                STRESS_GRAPH_REPORT,
                {
                    "status": stress_report.get("status"),
                    "certificate_sha256": stress_report.get("certificate_sha256"),
                },
            ),
            "visualization": input_entry(VISUALIZATION),
            "derive_script": input_entry(DERIVE_SCRIPT),
        },
        "definition": {
            "object": "fixed-seed D20 lifted sandpile transport eigenmode witness",
            "real_mode": "dominant smoothed transport vector from the certified C985 D20 stress graph",
            "null_mode": "same graph update with deterministic atom-to-tension shuffle i -> (7*i + 11) mod 20",
            "live_signal": (
                "per-frame histogram of live dominant D20 fibers weighted by graph-smoothed "
                "signed atlas tension and log local load"
            ),
            "claim_boundary": (
                "certifies reproducible real-vs-null alignment measurements only; it does not "
                "certify a continuum electron eigenpath, Maxwell field, or gravitational model"
            ),
        },
        "parameters": {
            "warmup_steps": WARMUP_STEPS,
            "replay_frames": REPLAY_FRAMES,
            "step_limit": STEP_LIMIT,
            "null_shuffle": {"multiplier": SHUFFLE_MULTIPLIER, "offset": SHUFFLE_OFFSET},
        },
        "witness": {
            "real_mode": [round(float(value), 12) for value in real_mode.tolist()],
            "null_mode": [round(float(value), 12) for value in null_mode.tolist()],
            "real_null_mode_dot": mode_overlap,
            "summary": summary,
            "conclusion": conclusion,
            "frame_samples": frame_samples,
        },
        "checks": checks,
    }
    payload["artifact_sha256_excluding_this_field"] = self_hash(
        payload, "artifact_sha256_excluding_this_field"
    )
    return payload


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    summary = artifact["witness"]["summary"]
    report = {
        "schema": "d20.transport_eigenmode_report@1",
        "status": "D20_TRANSPORT_EIGENMODE_REPORT_CERTIFIED",
        "all_checks_pass": all(artifact["checks"].values()),
        "claim": (
            "A deterministic D20 lift replay can be compared against a certified stress-graph "
            "transport mode and a shuffled null mode. The report records whether the live "
            "coil-like atlas signal aligns more strongly with the real atlas mode than with "
            "the null assignment."
        ),
        "stage_protocol": {
            "draft": "treat the Tesla-coil reading as a graph-transport eigenmode hypothesis",
            "witness": "replay the D20 lift with fixed warmup and compare live signals to real/null modes",
            "coherence": "verify stress graph certification, unit modes, finite alignments, and null permutation",
            "closure": "emit a reproducible alignment gap without promoting a physical EM/GR claim",
            "emit": "publish artifact, report, manifest, and registry entry",
        },
        "definition": artifact["definition"],
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
            "summary": summary,
            "conclusion": artifact["witness"]["conclusion"],
            "real_null_mode_dot": artifact["witness"]["real_null_mode_dot"],
            "real_mode_head": artifact["witness"]["real_mode"][:8],
            "null_mode_head": artifact["witness"]["null_mode"][:8],
            "sample_frames": artifact["witness"]["frame_samples"][:6],
        },
        "checks": artifact["checks"],
        "interpretation": {
            "real_mode_alignment_mean": summary["real_alignment_mean"],
            "null_mode_alignment_mean": summary["null_alignment_mean"],
            "mean_gap": summary["real_minus_null_gap_mean"],
            "positive_gap_fraction": summary["positive_gap_fraction"],
            "support_status": artifact["witness"]["conclusion"],
        },
        "closure_boundary": {
            "certifies": [
                "fixed-seed real-vs-null transport-eigenmode measurements",
                "deterministic replay parameters and graph-mode construction",
                "finite alignment values against certified atlas-derived inputs",
            ],
            "does_not_certify": [
                "literal electron-path eigenmodes",
                "magnetic-field control",
                "black-hole or gravitational dynamics",
                "browser compositor pixels",
            ],
        },
        "next_highest_yield_item": (
            "Add a batch A/B harness over many collider shots and compare capture/residue "
            "statistics for real atlas assignment versus shuffled null assignment."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest = {
        "schema": "d20.transport_eigenmode_report_manifest@1",
        "name": THEOREM_ID,
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
    summary = artifact["witness"]["summary"]
    print(
        json.dumps(
            {
                "artifact": relpath(ARTIFACT_PATH),
                "report": relpath(OUT_DIR / "report.json"),
                "report_sha256": report["certificate_sha256"],
                "status": report["status"],
                "conclusion": artifact["witness"]["conclusion"],
                "real_alignment_mean": summary["real_alignment_mean"],
                "null_alignment_mean": summary["null_alignment_mean"],
                "mean_gap": summary["real_minus_null_gap_mean"],
                "positive_gap_fraction": summary["positive_gap_fraction"],
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
