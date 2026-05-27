from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_d20_geon_phase_entropy_audit import (
        AUDIT_FRAMES,
        D20LiftSimulator,
        D20_WARMUP_STEPS,
        load_visualization_data,
    )
    from .derive_d20_tesla_coil_astar_flux_probe import (
        PATH_PAIR_COUNT,
        cost_from_features,
        invariant_features,
        path_suite,
        shell_geometry,
        transport_field,
    )
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_d20_geon_phase_entropy_audit import (
        AUDIT_FRAMES,
        D20LiftSimulator,
        D20_WARMUP_STEPS,
        load_visualization_data,
    )
    from derive_d20_tesla_coil_astar_flux_probe import (
        PATH_PAIR_COUNT,
        cost_from_features,
        invariant_features,
        path_suite,
        shell_geometry,
        transport_field,
    )
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_horizon_flux_astar_probe"
ARTIFACT_PATH = GENERATED / f"{THEOREM_ID}.json"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

TESLA_COIL_REPORT = (
    D20_INVARIANTS / "proof_obligations" / "d20_tesla_coil_astar_flux_probe" / "report.json"
)
PHASE_AUDIT_REPORT = (
    D20_INVARIANTS / "proof_obligations" / "d20_geon_phase_entropy_audit" / "report.json"
)
DERIVE_SCRIPT = ROOT / "src" / "derive_d20_horizon_flux_astar_probe.py"
VALIDATOR = ROOT / "src" / "certify_d20_horizon_flux_astar_probe.py"

FRAME_COUNT = AUDIT_FRAMES + 1
ASTAR_FRAME_STRIDE = 12
FLUX_NULL_SAMPLES = 32
ASTAR_NULL_SAMPLES = 8


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


def invariant_weight(features: dict[str, np.ndarray]) -> np.ndarray:
    return (
        1.0
        + 0.72 * features["order"]
        + 0.30 * features["mixed"]
        + 0.18 * features["grade_negative"]
    )


def horizon_flux_frame(
    frame: int,
    sim: D20LiftSimulator,
    rng: np.random.Generator,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    tensor = sim.state.reshape(sim.size, sim.size, sim.fibers)
    _categories, sums = sim.state_arrays()
    geometry = shell_geometry(sums)
    vx, vy = transport_field(sim.data, tensor)
    features = invariant_features(sim, geometry["shell"])
    weights = invariant_weight(features)
    radius = geometry["radius"]
    shell = geometry["shell"]
    inner = geometry["inner_band"]
    outer = geometry["outer_band"]
    bulk = shell & ~inner & ~outer
    ys, xs = np.indices(sums.shape)
    cx = float(geometry["center_x"])
    cy = float(geometry["center_y"])
    safe_r = np.where(radius > 0, radius, 1.0)
    radial_out = (vx * (xs - cx) + vy * (ys - cy)) / safe_r
    inward = np.maximum(0.0, -radial_out)
    outward = np.maximum(0.0, radial_out)
    observed = float((inward * weights)[inner].sum()) if np.any(inner) else 0.0
    raw_inward = float(inward[inner].sum()) if np.any(inner) else 0.0
    raw_outward = float(outward[inner].sum()) if np.any(inner) else 0.0
    bulk_inward_mean = float(inward[bulk].mean()) if np.any(bulk) else 0.0
    inner_inward_mean = float(inward[inner].mean()) if np.any(inner) else 0.0

    null_values = []
    if np.any(inner):
        base = inward[inner]
        values = weights[inner].copy()
        for _ in range(FLUX_NULL_SAMPLES):
            shuffled = values.copy()
            rng.shuffle(shuffled)
            null_values.append(float((base * shuffled).sum()))
    null_arr = np.asarray(null_values, dtype=float)
    null_mean = float(null_arr.mean()) if len(null_arr) else 0.0
    null_std = float(null_arr.std(ddof=1)) if len(null_arr) > 1 else 0.0
    z = (observed - null_mean) / null_std if null_std > 0 else 0.0
    above_null = bool(observed > null_mean)

    flux_row = {
        "frame": frame,
        "inner_radius": float(geometry["inner_radius"]),
        "outer_radius": float(geometry["outer_radius"]),
        "shell_coverage_ratio": float(geometry["shell_coverage_ratio"]),
        "hole_cell_count": int(geometry["hole_cell_count"]),
        "inner_band_cell_count": int(inner.sum()),
        "raw_inward_flux": raw_inward,
        "raw_outward_flux": raw_outward,
        "net_inward_flux": raw_inward - raw_outward,
        "invariant_weighted_inward_flux": observed,
        "null_weighted_inward_flux_mean": null_mean,
        "null_weighted_inward_flux_std": null_std,
        "weighted_flux_delta_vs_null": observed - null_mean,
        "weighted_flux_z_vs_null": z,
        "weighted_flux_above_null_mean": above_null,
        "inner_to_bulk_inward_flux_ratio": inner_inward_mean / (bulk_inward_mean + 1e-12),
        "live_grains": int(sums.sum()),
        "topples": int(sim.topples),
        "boundary_loss": int(sim.boundary_loss),
    }

    astar_row = None
    if frame % ASTAR_FRAME_STRIDE == 0 or frame == AUDIT_FRAMES:
        cost = cost_from_features(geometry, features)
        mag = np.sqrt(vx * vx + vy * vy)
        _paths, aggregate = path_suite(geometry, cost, vx, vy, mag)
        null_inner = []
        null_sweep = []
        shell_coords = np.argwhere(shell)
        shell_index = (shell_coords[:, 0], shell_coords[:, 1])
        for _ in range(ASTAR_NULL_SAMPLES):
            shuffled = {
                key: value.copy()
                for key, value in features.items()
                if key in {"order", "grade_negative", "mixed"}
            }
            for key in shuffled:
                values = shuffled[key][shell_index].copy()
                rng.shuffle(values)
                shuffled[key][shell_index] = values
            null_cost = cost_from_features(geometry, shuffled)
            _null_paths, null_aggregate = path_suite(geometry, null_cost, vx, vy, mag)
            null_inner.append(float(null_aggregate["inner_band_fraction_mean"]))
            null_sweep.append(float(null_aggregate["angular_sweep_turns_mean"]))
        inner_arr = np.asarray(null_inner, dtype=float)
        sweep_arr = np.asarray(null_sweep, dtype=float)
        inner_mean = float(inner_arr.mean()) if len(inner_arr) else 0.0
        sweep_mean = float(sweep_arr.mean()) if len(sweep_arr) else 0.0
        inner_std = float(inner_arr.std(ddof=1)) if len(inner_arr) > 1 else 0.0
        sweep_std = float(sweep_arr.std(ddof=1)) if len(sweep_arr) > 1 else 0.0
        astar_row = {
            "frame": frame,
            "paths_found": float(aggregate["paths_found"]),
            "axis_alignment_mean": float(aggregate["axis_alignment_mean"]),
            "high_flux_overlap_fraction_mean": float(
                aggregate["high_flux_overlap_fraction_mean"]
            ),
            "inner_band_fraction_mean": float(aggregate["inner_band_fraction_mean"]),
            "angular_sweep_turns_mean": float(aggregate["angular_sweep_turns_mean"]),
            "null_inner_band_fraction_mean": inner_mean,
            "null_inner_band_fraction_std": inner_std,
            "inner_band_fraction_delta_vs_null": float(aggregate["inner_band_fraction_mean"])
            - inner_mean,
            "inner_band_fraction_z_vs_null": (
                (float(aggregate["inner_band_fraction_mean"]) - inner_mean) / inner_std
                if inner_std > 0
                else 0.0
            ),
            "null_angular_sweep_turns_mean": sweep_mean,
            "null_angular_sweep_turns_std": sweep_std,
            "angular_sweep_turns_delta_vs_null": float(aggregate["angular_sweep_turns_mean"])
            - sweep_mean,
            "angular_sweep_turns_z_vs_null": (
                (float(aggregate["angular_sweep_turns_mean"]) - sweep_mean) / sweep_std
                if sweep_std > 0
                else 0.0
            ),
        }
    return flux_row, astar_row


def horizon_timeseries() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    data, _ = load_visualization_data()
    sim = D20LiftSimulator(data)
    sim.seed()
    for _ in range(D20_WARMUP_STEPS):
        sim.step(9000)
    rng = np.random.default_rng(20260528)
    flux_rows = []
    astar_rows = []
    for frame in range(FRAME_COUNT):
        if frame > 0:
            sim.step()
        flux_row, astar_row = horizon_flux_frame(frame, sim, rng)
        flux_rows.append(flux_row)
        if astar_row is not None:
            astar_rows.append(astar_row)
    return flux_rows, astar_rows


def summarize_flux(rows: list[dict[str, Any]]) -> dict[str, Any]:
    deltas = np.asarray([row["weighted_flux_delta_vs_null"] for row in rows], dtype=float)
    z_values = np.asarray([row["weighted_flux_z_vs_null"] for row in rows], dtype=float)
    inner_bulk = np.asarray([row["inner_to_bulk_inward_flux_ratio"] for row in rows], dtype=float)
    net = np.asarray([row["net_inward_flux"] for row in rows], dtype=float)
    return {
        "frame_count": len(rows),
        "weighted_flux_delta_vs_null_mean": float(deltas.mean()),
        "weighted_flux_delta_vs_null_min": float(deltas.min()),
        "weighted_flux_delta_vs_null_max": float(deltas.max()),
        "weighted_flux_z_vs_null_mean": float(z_values.mean()),
        "weighted_flux_above_null_frame_count": int(
            sum(1 for row in rows if row["weighted_flux_above_null_mean"])
        ),
        "weighted_flux_above_null_fraction": float(
            sum(1 for row in rows if row["weighted_flux_above_null_mean"]) / len(rows)
        ),
        "inner_to_bulk_inward_flux_ratio_mean": float(inner_bulk.mean()),
        "inner_to_bulk_inward_flux_ratio_max": float(inner_bulk.max()),
        "net_inward_flux_positive_frame_count": int((net > 0.0).sum()),
        "cumulative_raw_inward_flux": float(sum(row["raw_inward_flux"] for row in rows)),
        "cumulative_raw_outward_flux": float(sum(row["raw_outward_flux"] for row in rows)),
        "cumulative_invariant_weighted_inward_flux": float(
            sum(row["invariant_weighted_inward_flux"] for row in rows)
        ),
    }


def summarize_astar(rows: list[dict[str, Any]]) -> dict[str, Any]:
    inner_delta = np.asarray([row["inner_band_fraction_delta_vs_null"] for row in rows], dtype=float)
    sweep_delta = np.asarray([row["angular_sweep_turns_delta_vs_null"] for row in rows], dtype=float)
    return {
        "sampled_frame_count": len(rows),
        "path_pair_count": PATH_PAIR_COUNT,
        "all_sampled_paths_found": all(row["paths_found"] == float(PATH_PAIR_COUNT) for row in rows),
        "inner_band_fraction_delta_vs_null_mean": float(inner_delta.mean()),
        "inner_band_fraction_delta_positive_frame_count": int((inner_delta > 0.0).sum()),
        "angular_sweep_turns_delta_vs_null_mean": float(sweep_delta.mean()),
        "angular_sweep_turns_delta_positive_frame_count": int((sweep_delta > 0.0).sum()),
        "axis_alignment_mean": float(np.mean([row["axis_alignment_mean"] for row in rows])),
        "high_flux_overlap_fraction_mean": float(
            np.mean([row["high_flux_overlap_fraction_mean"] for row in rows])
        ),
    }


def artifact_hash(payload: dict[str, Any]) -> str:
    return self_hash(payload, "artifact_sha256_excluding_this_field")


def build_artifact() -> dict[str, Any]:
    phase = load_json(PHASE_AUDIT_REPORT)
    tesla = load_json(TESLA_COIL_REPORT)
    flux_rows, astar_rows = horizon_timeseries()
    flux_summary = summarize_flux(flux_rows)
    astar_summary = summarize_astar(astar_rows)
    checks = {
        "phase_entropy_audit_certified": phase.get("status") == "D20_GEON_PHASE_ENTROPY_AUDIT_CERTIFIED",
        "tesla_coil_probe_is_recorded": tesla.get("status")
        in {
            "D20_TESLA_COIL_ASTAR_FLUX_PROBE_CERTIFIED",
            "D20_TESLA_COIL_ASTAR_FLUX_PROBE_PROVISIONAL",
        },
        "timeseries_frame_count_is_97": flux_summary["frame_count"] == FRAME_COUNT,
        "horizon_has_inward_flux": flux_summary["cumulative_raw_inward_flux"] > 0.0,
        "horizon_weighted_flux_beats_shuffle_mean": flux_summary[
            "weighted_flux_delta_vs_null_mean"
        ]
        > 0.0,
        "horizon_weighted_flux_beats_shuffle_on_majority_frames": flux_summary[
            "weighted_flux_above_null_fraction"
        ]
        > 0.5,
        "inner_band_inward_flux_exceeds_bulk_mean": flux_summary[
            "inner_to_bulk_inward_flux_ratio_mean"
        ]
        > 1.0,
        "astar_sampled_paths_all_found": astar_summary["all_sampled_paths_found"] is True,
        "astar_paths_bend_toward_horizon_more_than_shuffle": astar_summary[
            "inner_band_fraction_delta_vs_null_mean"
        ]
        > 0.0,
        "astar_paths_sweep_more_than_shuffle": astar_summary[
            "angular_sweep_turns_delta_vs_null_mean"
        ]
        > 0.0,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_HORIZON_FLUX_ASTAR_PROBE_CERTIFIED"
        if all_checks_pass
        else "D20_HORIZON_FLUX_ASTAR_PROBE_PROVISIONAL"
    )
    payload: dict[str, Any] = {
        "schema": "d20.proof_obligation.horizon_flux_astar_probe.artifact@1",
        "status": status,
        "source": {
            "phase_entropy_audit_report": input_entry(
                PHASE_AUDIT_REPORT,
                {"status": phase.get("status"), "certificate_sha256": phase.get("certificate_sha256")},
            ),
            "tesla_coil_astar_flux_probe_report": input_entry(
                TESLA_COIL_REPORT,
                {"status": tesla.get("status"), "certificate_sha256": tesla.get("certificate_sha256")},
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
        },
        "definition": {
            "object": "time-resolved D20 lifted sandpile after certified warmup",
            "operational_horizon": (
                "the inner band of the mass-weighted annular shell; inward radial transport "
                "across this band is counted as horizon-crossing flux"
            ),
            "absorption_reading": (
                "absorbing horizon is measured, not back-reacted: chips are not removed from "
                "the simulator in this probe"
            ),
            "invariant_flux_weight": (
                "1 + 0.72*class_order/30 + 0.30*mixed_fiber + 0.18*negative_tube_grade"
            ),
            "lensing_path_reading": (
                "sampled invariant-weighted A* paths are tested for increased inner-band "
                "fraction and angular sweep relative to shuffled invariant labels"
            ),
        },
        "witness": {
            "flux_summary": flux_summary,
            "astar_lensing_summary": astar_summary,
            "flux_rows_sha256": sha_json(flux_rows),
            "astar_rows_sha256": sha_json(astar_rows),
            "flux_rows_first_16": flux_rows[:16],
            "astar_rows": astar_rows,
        },
        "checks": checks,
    }
    payload["artifact_sha256_excluding_this_field"] = artifact_hash(payload)
    return payload


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    all_checks_pass = all(artifact["checks"].values())
    if all_checks_pass:
        claim = (
            "The D20 lifted sandpile shows a certified horizon-flux signal: invariant-weighted "
            "inward flux beats label shuffles over the time series, inner-band inward flux "
            "exceeds shell bulk, and sampled A* paths bend/sweep toward the horizon more than "
            "invariant shuffles."
        )
    else:
        claim = (
            "The D20 lifted sandpile now has a time-resolved operational horizon probe, but the "
            "measured horizon/black-hole signal remains provisional. The report records inward "
            "invariant flux, shuffle controls, and A* lensing metrics without claiming a physical "
            "black-hole model."
        )
    report: dict[str, Any] = {
        "schema": "d20.proof_obligation.horizon_flux_astar_probe@1",
        "status": artifact["status"],
        "all_checks_pass": all_checks_pass,
        "claim": claim,
        "stage_protocol": {
            "draft": "promote the topological hole to an operational absorbing horizon",
            "witness": "measure inward invariant flux across the horizon over every audited frame",
            "coherence": "compare horizon flux and A* lensing against invariant-label shuffles",
            "closure": "validate frame count, flux existence, shuffle deltas, and sampled A* paths",
            "emit": "emit horizon-flux/lensing metrics plus a boundary against physical black-hole claims",
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
        "witness": artifact["witness"],
        "checks": artifact["checks"],
        "closure_boundary": {
            "certifies": [
                "a deterministic operational horizon over the D20 lifted sandpile shell",
                "time-resolved inward flux measurements with invariant-label shuffle controls",
                "sampled A* path-bending/lensing metrics against shuffle controls",
            ],
            "does_not_certify": [
                "a back-reacting absorbing horizon",
                "a continuum event horizon",
                "Einstein-equation curvature or stress-energy semantics",
                "Hawking radiation or thermodynamic black-hole laws",
            ],
        },
        "next_highest_yield_item": (
            "Add back-reaction: remove horizon-crossing chips into a conserved sink ledger, then "
            "measure whether A* path bending and coil winding strengthen as horizon mass grows."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": "d20.proof_obligation.horizon_flux_astar_probe_manifest@1",
        "name": THEOREM_ID,
        "certification_tests": [
            "replay 97 audited D20 lift frames after warmup",
            "derive a per-frame operational annular shell and inner horizon band",
            "measure inward horizon-crossing transport weighted by RGBA atom invariants",
            "compare invariant-weighted horizon flux against shuffled invariant labels",
            "sample A* path bending and angular sweep against invariant-label shuffles",
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
                "all_checks_pass": report["all_checks_pass"],
                "weighted_flux_delta_vs_null_mean": report["witness"]["flux_summary"][
                    "weighted_flux_delta_vs_null_mean"
                ],
                "inner_to_bulk_inward_flux_ratio_mean": report["witness"]["flux_summary"][
                    "inner_to_bulk_inward_flux_ratio_mean"
                ],
                "astar_inner_band_delta_vs_null_mean": report["witness"][
                    "astar_lensing_summary"
                ]["inner_band_fraction_delta_vs_null_mean"],
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
