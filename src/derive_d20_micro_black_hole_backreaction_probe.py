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
    from .derive_d20_geon_phase_entropy_audit import (
        AUDIT_FRAMES,
        D20LiftSimulator,
        D20_WARMUP_STEPS,
        d20_lift_delta,
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
        d20_lift_delta,
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


THEOREM_ID = "d20_micro_black_hole_backreaction_probe"
ARTIFACT_PATH = GENERATED / f"{THEOREM_ID}.json"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

HORIZON_FLUX_REPORT = (
    D20_INVARIANTS / "proof_obligations" / "d20_horizon_flux_astar_probe" / "report.json"
)
TESLA_COIL_REPORT = (
    D20_INVARIANTS / "proof_obligations" / "d20_tesla_coil_astar_flux_probe" / "report.json"
)
DERIVE_SCRIPT = ROOT / "src" / "derive_d20_micro_black_hole_backreaction_probe.py"
VALIDATOR = ROOT / "src" / "certify_d20_micro_black_hole_backreaction_probe.py"

FRAME_COUNT = AUDIT_FRAMES + 1
ASTAR_FRAME_STRIDE = 12
ABSORPTION_MAX_FRACTION = 0.34
HORIZON_LENS_STRENGTH = 0.95
HORIZON_LENS_MASS_SCALE = 12000.0
HORIZON_LENS_WIDTH = 3.25
RAW_COST_REMOVAL_WEIGHT = 4.5
RAW_COST_TARGET_WEIGHT = 1.6
RAW_COST_LOW_TARGET = 0.29
ANTI_TANGENT_WEIGHT = 0.58
ANTI_GLOBAL_WEIGHT = 0.75
OUTWARD_LEAK_WEIGHT = 0.34
USE_GREEDY_RAW_COST_REMOVAL = False


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


def radial_transport(
    vx: np.ndarray,
    vy: np.ndarray,
    geometry: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    radius = geometry["radius"]
    ys, xs = np.indices(vx.shape)
    cx = float(geometry["center_x"])
    cy = float(geometry["center_y"])
    safe_r = np.where(radius > 0, radius, 1.0)
    radial_out = (vx * (xs - cx) + vy * (ys - cy)) / safe_r
    inward = np.maximum(0.0, -radial_out)
    outward = np.maximum(0.0, radial_out)
    magnitude = np.sqrt(vx * vx + vy * vy)
    return inward, outward, magnitude


def polarization_and_coil(
    vx: np.ndarray,
    vy: np.ndarray,
    geometry: dict[str, Any],
) -> dict[str, float]:
    shell = geometry["shell"]
    radius = geometry["radius"]
    mag = np.sqrt(vx * vx + vy * vy)
    support = shell & (mag > 0.0)
    if not np.any(support):
        return {
            "polarization_order": 0.0,
            "coil_phase_coherence": 0.0,
            "mean_signed_tangential_flow": 0.0,
        }
    total_mag = float(mag[support].sum())
    polarization = float(
        math.hypot(float(vx[support].sum()), float(vy[support].sum())) / (total_mag + 1e-12)
    )
    ys, xs = np.indices(vx.shape)
    theta = np.arctan2(ys - float(geometry["center_y"]), xs - float(geometry["center_x"]))
    vector_angle = np.arctan2(vy, vx)
    phase = vector_angle - theta
    complex_phase = np.exp(1j * phase[support])
    coherence = float(abs(np.mean(complex_phase)))
    safe_r = np.where(radius > 0, radius, 1.0)
    tangent_x = -(ys - float(geometry["center_y"])) / safe_r
    tangent_y = (xs - float(geometry["center_x"])) / safe_r
    tangential = (vx * tangent_x + vy * tangent_y) / (mag + 1e-12)
    return {
        "polarization_order": polarization,
        "coil_phase_coherence": coherence,
        "mean_signed_tangential_flow": float(tangential[support].mean()),
    }


def horizon_flux_metrics(
    vx: np.ndarray,
    vy: np.ndarray,
    geometry: dict[str, Any],
) -> dict[str, float]:
    inward, outward, _mag = radial_transport(vx, vy, geometry)
    inner = geometry["inner_band"]
    bulk = geometry["shell"] & ~geometry["inner_band"] & ~geometry["outer_band"]
    inner_mean = float(inward[inner].mean()) if np.any(inner) else 0.0
    bulk_mean = float(inward[bulk].mean()) if np.any(bulk) else 0.0
    return {
        "raw_inward_flux": float(inward[inner].sum()) if np.any(inner) else 0.0,
        "raw_outward_flux": float(outward[inner].sum()) if np.any(inner) else 0.0,
        "net_inward_flux": float((inward[inner] - outward[inner]).sum()) if np.any(inner) else 0.0,
        "inner_to_bulk_inward_flux_ratio": inner_mean / (bulk_mean + 1e-12),
    }


def horizon_lens_factor(horizon_mass: int) -> float:
    if horizon_mass <= 0:
        return 0.0
    return min(1.0, math.log1p(float(horizon_mass)) / math.log1p(HORIZON_LENS_MASS_SCALE))


def horizon_lensed_cost(
    geometry: dict[str, Any],
    features: dict[str, np.ndarray],
    horizon_mass: int,
) -> tuple[np.ndarray, float, float]:
    base_cost = cost_from_features(geometry, features)
    lens_factor = horizon_lens_factor(horizon_mass)
    if lens_factor <= 0.0:
        return base_cost, 0.0, 0.0
    radius = geometry["radius"]
    inner_radius = float(geometry["inner_radius"])
    shell = geometry["shell"]
    inner_band = geometry["inner_band"]
    gaussian = np.exp(-((radius - inner_radius) / HORIZON_LENS_WIDTH) ** 2)
    profile = np.where(inner_band, 1.0, 0.35 * gaussian)
    potential = HORIZON_LENS_STRENGTH * lens_factor * profile
    cost = np.where(shell, np.maximum(0.06, base_cost - potential), np.inf)
    potential_mean = float(potential[shell].mean()) if np.any(shell) else 0.0
    return cost, lens_factor, potential_mean


def invariant_raw_cost(pixel: dict[str, Any]) -> float:
    return (
        0.55 * (float(pixel.get("o", 0)) / 30.0)
        + 0.16 * (1.0 if int(pixel.get("g", 1)) < 0 else 0.0)
        - 0.24 * (1.0 if int(pixel.get("x", 0)) else 0.0)
    )


def sample_from_chips(chips: np.ndarray, pixels: list[dict[str, Any]]) -> dict[str, Any]:
    total = int(chips.sum())
    hot = bool(np.any(chips >= 3))
    dominant_fiber = int(np.argmax(chips)) if len(chips) else 0
    folded = 0
    for fiber, chip_count in enumerate(chips.tolist()):
        folded = (folded + (((fiber + 1) * (int(chip_count) % 2048)) & 2047)) & 2047
    signature = (
        total
        + 2 * int(chips[1])
        + 3 * int(chips[7])
        + 5 * int(chips[14])
    ) & 3
    mask = (
        folded
        ^ (total & 2047)
        ^ ((dominant_fiber * 131) & 2047)
        ^ ((signature & 3) << 9)
        ^ (1024 if hot else 0)
    ) & 2047
    pixel = pixels[mask] if 0 <= mask < len(pixels) else pixels[0]
    return {
        "sum": total,
        "hot": hot,
        "signature": int(signature),
        "dominantFiber": dominant_fiber,
        "mask": int(mask),
        "pixel": pixel,
    }


def removal_allocation(chips: np.ndarray, target: int) -> np.ndarray:
    total = int(chips.sum())
    if target <= 0 or total <= 0:
        return np.zeros_like(chips, dtype=np.uint64)
    target = min(target, total)
    raw = chips.astype(float) * (target / total)
    base = np.floor(raw).astype(np.uint64)
    remaining = target - int(base.sum())
    if remaining > 0:
        fractions = raw - base.astype(float)
        order = sorted(
            range(len(chips)),
            key=lambda idx: (fractions[idx], int(chips[idx]), -idx),
            reverse=True,
        )
        for idx in order:
            if remaining <= 0:
                break
            if base[idx] < chips[idx]:
                base[idx] += 1
                remaining -= 1
    return base


def weighted_removal_allocation(
    chips: np.ndarray,
    scores: np.ndarray,
    target: int,
) -> np.ndarray:
    total = int(chips.sum())
    if target <= 0 or total <= 0:
        return np.zeros_like(chips, dtype=np.uint64)
    target = min(target, total)
    weights = chips.astype(float) * np.maximum(scores.astype(float), 0.0)
    if float(weights.sum()) <= 0.0:
        return removal_allocation(chips, target)
    raw = weights * (target / float(weights.sum()))
    base = np.minimum(np.floor(raw).astype(np.uint64), chips)
    remaining = target - int(base.sum())
    if remaining > 0:
        fractions = raw - base.astype(float)
        order = sorted(
            range(len(chips)),
            key=lambda idx: (fractions[idx], float(scores[idx]), int(chips[idx]), -idx),
            reverse=True,
        )
        for idx in order:
            if remaining <= 0:
                break
            if base[idx] < chips[idx]:
                base[idx] += 1
                remaining -= 1
    return base


def raw_cost_guided_removal_allocation(
    chips: np.ndarray,
    base_scores: np.ndarray,
    target: int,
    pixels: list[dict[str, Any]],
) -> np.ndarray:
    total = int(chips.sum())
    if target <= 0 or total <= 0:
        return np.zeros_like(chips, dtype=np.uint64)
    target = min(target, total)
    current = chips.copy()
    removal = np.zeros_like(chips, dtype=np.uint64)
    for _ in range(target):
        sample = sample_from_chips(current, pixels)
        current_cost = invariant_raw_cost(sample["pixel"])
        best_fiber = -1
        best_score = -math.inf
        for fiber in range(len(chips)):
            if int(current[fiber]) <= 0:
                continue
            trial = current.copy()
            trial[fiber] -= 1
            trial_cost = invariant_raw_cost(sample_from_chips(trial, pixels)["pixel"])
            improvement = max(0.0, current_cost - trial_cost)
            low_target = max(0.0, RAW_COST_LOW_TARGET - trial_cost)
            score = (
                float(base_scores[fiber])
                + RAW_COST_REMOVAL_WEIGHT * improvement
                + RAW_COST_TARGET_WEIGHT * low_target
                - 0.08 * max(0.0, trial_cost - current_cost)
            )
            if score > best_score:
                best_score = score
                best_fiber = fiber
        if best_fiber < 0:
            break
        current[best_fiber] -= 1
        removal[best_fiber] += 1
    return removal


def fiber_transport_vectors(data: dict[str, Any], fibers: int) -> np.ndarray:
    vectors = np.zeros((fibers, 2), dtype=float)
    for edge in data["edges"]:
        dx, dy = d20_lift_delta(edge)
        vectors[int(edge["u"]), 0] += dx
        vectors[int(edge["u"]), 1] += dy
        vectors[int(edge["v"]), 0] -= dx
        vectors[int(edge["v"]), 1] -= dy
    return vectors


def absorb_horizon(
    sim: D20LiftSimulator,
    vx: np.ndarray,
    vy: np.ndarray,
    geometry: dict[str, Any],
    fiber_vectors: np.ndarray,
    data: dict[str, Any],
) -> dict[str, Any]:
    tensor = sim.state.reshape(sim.size, sim.size, sim.fibers)
    pixels = data["pixels"]
    inward, _outward, mag = radial_transport(vx, vy, geometry)
    shell = geometry["shell"]
    shell_vx = float(vx[shell].sum())
    shell_vy = float(vy[shell].sum())
    shell_norm = math.hypot(shell_vx, shell_vy) or 1.0
    global_unit = np.asarray([shell_vx / shell_norm, shell_vy / shell_norm], dtype=float)
    ys, xs = np.indices(vx.shape)
    radius = geometry["radius"]
    safe_r = np.where(radius > 0, radius, 1.0)
    tangent_x = -(ys - float(geometry["center_y"])) / safe_r
    tangent_y = (xs - float(geometry["center_x"])) / safe_r
    tangent_flow = vx * tangent_x + vy * tangent_y
    orientation = 1.0 if float(tangent_flow[shell].sum()) >= 0.0 else -1.0
    ledger = {
        "absorbed_mass": 0,
        "by_fiber": Counter(),
        "by_order": Counter(),
        "by_grade": Counter(),
        "by_mixed": Counter(),
        "cell_count": 0,
    }
    for y, x in np.argwhere(geometry["inner_band"]):
        local_inward = float(inward[y, x])
        if local_inward <= 0.0:
            continue
        chips = tensor[y, x, :].copy()
        total = int(chips.sum())
        if total <= 0:
            continue
        ratio = local_inward / (float(mag[y, x]) + 1e-12)
        fraction = min(ABSORPTION_MAX_FRACTION, 0.025 + 0.145 * ratio)
        target = max(1, int(round(total * fraction)))
        sample = sim.sample_cell(int(x), int(y))
        pixel = sample["pixel"]
        base_raw_cost = invariant_raw_cost(pixel)
        radial_unit = np.asarray(
            [
                (float(x) - float(geometry["center_x"])) / float(safe_r[y, x]),
                (float(y) - float(geometry["center_y"])) / float(safe_r[y, x]),
            ],
            dtype=float,
        )
        tangent_unit = orientation * np.asarray(
            [float(tangent_x[y, x]), float(tangent_y[y, x])],
            dtype=float,
        )
        inv_weight = (
            1.0
            + 0.32 * (float(pixel.get("o", 0)) / 30.0)
            + 0.22 * (1.0 if int(pixel.get("x", 0)) else 0.0)
            + 0.12 * (1.0 if int(pixel.get("g", 1)) < 0 else 0.0)
        )
        scores = np.zeros(sim.fibers, dtype=float)
        for fiber in range(sim.fibers):
            if int(chips[fiber]) <= 0:
                scores[fiber] = 0.0
                continue
            fx = float(fiber_vectors[fiber, 0])
            fy = float(fiber_vectors[fiber, 1])
            norm = math.hypot(fx, fy)
            trial = chips.copy()
            trial[fiber] -= 1
            trial_cost = invariant_raw_cost(sample_from_chips(trial, pixels)["pixel"])
            raw_cost_improvement = max(0.0, base_raw_cost - trial_cost)
            raw_low_target = max(0.0, RAW_COST_LOW_TARGET - trial_cost)
            if norm <= 0.0:
                transport_score = 0.05
                scores[fiber] = inv_weight * (
                    transport_score
                    + RAW_COST_REMOVAL_WEIGHT * raw_cost_improvement
                    + RAW_COST_TARGET_WEIGHT * raw_low_target
                )
                continue
            unit = np.asarray([fx / norm, fy / norm], dtype=float)
            anti_tangent = max(0.0, -float(np.dot(unit, tangent_unit)))
            anti_global = max(0.0, -float(np.dot(unit, global_unit)))
            outward_leak = max(0.0, float(np.dot(unit, radial_unit)))
            scores[fiber] = inv_weight * (
                0.04
                + ANTI_TANGENT_WEIGHT * anti_tangent
                + ANTI_GLOBAL_WEIGHT * anti_global
                + OUTWARD_LEAK_WEIGHT * outward_leak
                + RAW_COST_REMOVAL_WEIGHT * raw_cost_improvement
                + RAW_COST_TARGET_WEIGHT * raw_low_target
            )
        if USE_GREEDY_RAW_COST_REMOVAL:
            removal = raw_cost_guided_removal_allocation(chips, scores, target, pixels)
        else:
            removal = weighted_removal_allocation(chips, scores, target)
        removed = int(removal.sum())
        if removed <= 0:
            continue
        cell_base = (int(y) * sim.size + int(x)) * sim.fibers
        for fiber, amount in enumerate(removal.tolist()):
            amount = int(amount)
            if amount <= 0:
                continue
            sim.state[cell_base + fiber] -= amount
            ledger["by_fiber"][fiber] += amount
        ledger["absorbed_mass"] += removed
        ledger["by_order"][int(pixel.get("o", 0))] += removed
        ledger["by_grade"][int(pixel.get("g", 0))] += removed
        ledger["by_mixed"][int(pixel.get("x", 0))] += removed
        ledger["cell_count"] += 1
    return {
        "absorbed_mass": int(ledger["absorbed_mass"]),
        "cell_count": int(ledger["cell_count"]),
        "by_fiber": {str(k): int(v) for k, v in sorted(ledger["by_fiber"].items())},
        "by_order": {str(k): int(v) for k, v in sorted(ledger["by_order"].items())},
        "by_grade": {str(k): int(v) for k, v in sorted(ledger["by_grade"].items())},
        "by_mixed": {str(k): int(v) for k, v in sorted(ledger["by_mixed"].items())},
    }


def merge_counter_dict(target: Counter[int], source: dict[str, int]) -> None:
    for key, value in source.items():
        target[int(key)] += int(value)


def run_micro_hole(backreaction: bool) -> dict[str, Any]:
    data, _ = load_visualization_data()
    sim = D20LiftSimulator(data)
    fiber_vectors = fiber_transport_vectors(data, sim.fibers)
    sim.seed()
    for _ in range(D20_WARMUP_STEPS):
        sim.step(9000)

    rows = []
    astar_rows = []
    cumulative_mass = 0
    ledger_fiber: Counter[int] = Counter()
    ledger_order: Counter[int] = Counter()
    ledger_grade: Counter[int] = Counter()
    ledger_mixed: Counter[int] = Counter()

    for frame in range(FRAME_COUNT):
        if frame > 0:
            sim.step()
        tensor = sim.state.reshape(sim.size, sim.size, sim.fibers)
        _categories, sums = sim.state_arrays()
        geometry = shell_geometry(sums)
        vx, vy = transport_field(data, tensor)
        pre_flux = horizon_flux_metrics(vx, vy, geometry)
        absorption = {
            "absorbed_mass": 0,
            "cell_count": 0,
            "by_fiber": {},
            "by_order": {},
            "by_grade": {},
            "by_mixed": {},
        }
        if backreaction:
            absorption = absorb_horizon(sim, vx, vy, geometry, fiber_vectors, data)
            cumulative_mass += int(absorption["absorbed_mass"])
            merge_counter_dict(ledger_fiber, absorption["by_fiber"])
            merge_counter_dict(ledger_order, absorption["by_order"])
            merge_counter_dict(ledger_grade, absorption["by_grade"])
            merge_counter_dict(ledger_mixed, absorption["by_mixed"])

        tensor = sim.state.reshape(sim.size, sim.size, sim.fibers)
        _categories, sums = sim.state_arrays()
        geometry = shell_geometry(sums)
        vx, vy = transport_field(data, tensor)
        post_flux = horizon_flux_metrics(vx, vy, geometry)
        field = polarization_and_coil(vx, vy, geometry)
        rows.append(
            {
                "frame": frame,
                "backreaction": backreaction,
                "horizon_mass": cumulative_mass,
                "absorbed_this_frame": int(absorption["absorbed_mass"]),
                "absorbing_cell_count": int(absorption["cell_count"]),
                "live_grains": int(sums.sum()),
                "topples": int(sim.topples),
                "boundary_loss": int(sim.boundary_loss),
                "shell_coverage_ratio": float(geometry["shell_coverage_ratio"]),
                "pre_absorption_inner_to_bulk_inward_flux_ratio": pre_flux[
                    "inner_to_bulk_inward_flux_ratio"
                ],
                "post_absorption_inner_to_bulk_inward_flux_ratio": post_flux[
                    "inner_to_bulk_inward_flux_ratio"
                ],
                "post_absorption_net_inward_flux": post_flux["net_inward_flux"],
                **field,
            }
        )

        if frame % ASTAR_FRAME_STRIDE == 0 or frame == AUDIT_FRAMES:
            features = invariant_features(sim, geometry["shell"])
            raw_cost = cost_from_features(geometry, features)
            mag = np.sqrt(vx * vx + vy * vy)
            _raw_paths, raw_aggregate = path_suite(geometry, raw_cost, vx, vy, mag)
            if backreaction:
                cost, lens_factor, lens_potential_mean = horizon_lensed_cost(
                    geometry, features, cumulative_mass
                )
            else:
                cost = raw_cost
                lens_factor = 0.0
                lens_potential_mean = 0.0
            _paths, aggregate = path_suite(geometry, cost, vx, vy, mag)
            astar_rows.append(
                {
                    "frame": frame,
                    "horizon_mass": cumulative_mass,
                    "horizon_lens_factor": float(lens_factor),
                    "horizon_lens_potential_shell_mean": float(lens_potential_mean),
                    "paths_found": float(aggregate["paths_found"]),
                    "axis_alignment_mean": float(aggregate["axis_alignment_mean"]),
                    "high_flux_overlap_fraction_mean": float(
                        aggregate["high_flux_overlap_fraction_mean"]
                    ),
                    "inner_band_fraction_mean": float(aggregate["inner_band_fraction_mean"]),
                    "angular_sweep_turns_mean": float(aggregate["angular_sweep_turns_mean"]),
                    "raw_axis_alignment_mean": float(raw_aggregate["axis_alignment_mean"]),
                    "raw_high_flux_overlap_fraction_mean": float(
                        raw_aggregate["high_flux_overlap_fraction_mean"]
                    ),
                    "raw_inner_band_fraction_mean": float(
                        raw_aggregate["inner_band_fraction_mean"]
                    ),
                    "raw_angular_sweep_turns_mean": float(
                        raw_aggregate["angular_sweep_turns_mean"]
                    ),
                }
            )

    ledger = {
        "horizon_mass": cumulative_mass,
        "by_fiber": {str(k): int(v) for k, v in sorted(ledger_fiber.items())},
        "by_order": {str(k): int(v) for k, v in sorted(ledger_order.items())},
        "by_grade": {str(k): int(v) for k, v in sorted(ledger_grade.items())},
        "by_mixed": {str(k): int(v) for k, v in sorted(ledger_mixed.items())},
    }
    return {
        "rows": rows,
        "astar_rows": astar_rows,
        "ledger": ledger,
        "rows_sha256": sha_json(rows),
        "astar_rows_sha256": sha_json(astar_rows),
        "ledger_sha256": sha_json(ledger),
    }


def mean_delta(
    back_rows: list[dict[str, Any]],
    base_rows: list[dict[str, Any]],
    field: str,
) -> float:
    return float(
        np.mean(
            [
                float(left[field]) - float(right[field])
                for left, right in zip(back_rows, base_rows)
            ]
        )
    )


def mean_astar_delta(
    back_rows: list[dict[str, Any]],
    base_rows: list[dict[str, Any]],
    field: str,
) -> float:
    return float(
        np.mean(
            [
                float(left[field]) - float(right[field])
                for left, right in zip(back_rows, base_rows)
            ]
        )
    )


def summarize(backreaction: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    back_rows = backreaction["rows"]
    base_rows = baseline["rows"]
    back_astar = backreaction["astar_rows"]
    base_astar = baseline["astar_rows"]
    horizon_mass = [int(row["horizon_mass"]) for row in back_rows]
    absorbed = [int(row["absorbed_this_frame"]) for row in back_rows]
    return {
        "frame_count": len(back_rows),
        "astar_sample_count": len(back_astar),
        "final_horizon_mass": int(horizon_mass[-1]),
        "horizon_mass_monotone": all(
            right >= left for left, right in zip(horizon_mass, horizon_mass[1:])
        ),
        "absorbing_frame_count": int(sum(1 for value in absorbed if value > 0)),
        "polarization_delta_vs_baseline_mean": mean_delta(
            back_rows, base_rows, "polarization_order"
        ),
        "coil_coherence_delta_vs_baseline_mean": mean_delta(
            back_rows, base_rows, "coil_phase_coherence"
        ),
        "tangential_flow_delta_vs_baseline_mean": mean_delta(
            back_rows, base_rows, "mean_signed_tangential_flow"
        ),
        "post_flux_localization_delta_vs_baseline_mean": mean_delta(
            back_rows, base_rows, "post_absorption_inner_to_bulk_inward_flux_ratio"
        ),
        "astar_inner_band_delta_vs_baseline_mean": mean_astar_delta(
            back_astar, base_astar, "inner_band_fraction_mean"
        ),
        "raw_astar_inner_band_delta_vs_baseline_mean": mean_astar_delta(
            back_astar, base_astar, "raw_inner_band_fraction_mean"
        ),
        "astar_angular_sweep_delta_vs_baseline_mean": mean_astar_delta(
            back_astar, base_astar, "angular_sweep_turns_mean"
        ),
        "raw_astar_angular_sweep_delta_vs_baseline_mean": mean_astar_delta(
            back_astar, base_astar, "raw_angular_sweep_turns_mean"
        ),
        "astar_high_flux_overlap_delta_vs_baseline_mean": mean_astar_delta(
            back_astar, base_astar, "high_flux_overlap_fraction_mean"
        ),
        "raw_astar_high_flux_overlap_delta_vs_baseline_mean": mean_astar_delta(
            back_astar, base_astar, "raw_high_flux_overlap_fraction_mean"
        ),
        "horizon_lens_factor_mean": float(
            np.mean([float(row["horizon_lens_factor"]) for row in back_astar])
        ),
        "horizon_lens_potential_shell_mean": float(
            np.mean([float(row["horizon_lens_potential_shell_mean"]) for row in back_astar])
        ),
        "baseline_final_live_grains": int(base_rows[-1]["live_grains"]),
        "backreaction_final_live_grains": int(back_rows[-1]["live_grains"]),
    }


def compact_backreaction_replay(backreaction: dict[str, Any]) -> list[dict[str, Any]]:
    astar_by_frame = {int(row["frame"]): row for row in backreaction["astar_rows"]}
    last_astar: dict[str, Any] | None = None
    compact = []
    for row in backreaction["rows"]:
        frame = int(row["frame"])
        if frame in astar_by_frame:
            last_astar = astar_by_frame[frame]
        if last_astar is None:
            raise ValueError("backreaction replay is missing frame-0 A* witness")
        horizon_mass = int(row["horizon_mass"])
        compact.append(
            {
                "frame": frame,
                "horizon_mass": horizon_mass,
                "absorbed_this_frame": int(row["absorbed_this_frame"]),
                "live_grains": int(row["live_grains"]),
                "polarization_order": float(row["polarization_order"]),
                "coil_phase_coherence": float(row["coil_phase_coherence"]),
                "post_flux_localization": float(
                    row["post_absorption_inner_to_bulk_inward_flux_ratio"]
                ),
                "horizon_lens_factor": horizon_lens_factor(horizon_mass),
                "astar_inner_band_fraction_mean": float(
                    last_astar["inner_band_fraction_mean"]
                ),
                "raw_astar_inner_band_fraction_mean": float(
                    last_astar["raw_inner_band_fraction_mean"]
                ),
            }
        )
    return compact


def artifact_hash(payload: dict[str, Any]) -> str:
    return self_hash(payload, "artifact_sha256_excluding_this_field")


def build_artifact() -> dict[str, Any]:
    horizon = load_json(HORIZON_FLUX_REPORT)
    tesla = load_json(TESLA_COIL_REPORT)
    backreaction = run_micro_hole(True)
    baseline = run_micro_hole(False)
    summary = summarize(backreaction, baseline)
    checks = {
        "horizon_flux_probe_is_recorded": horizon.get("status")
        in {
            "D20_HORIZON_FLUX_ASTAR_PROBE_CERTIFIED",
            "D20_HORIZON_FLUX_ASTAR_PROBE_PROVISIONAL",
        },
        "tesla_coil_probe_is_recorded": tesla.get("status")
        in {
            "D20_TESLA_COIL_ASTAR_FLUX_PROBE_CERTIFIED",
            "D20_TESLA_COIL_ASTAR_FLUX_PROBE_PROVISIONAL",
        },
        "backreaction_frame_count_is_97": summary["frame_count"] == FRAME_COUNT,
        "sink_ledger_mass_is_positive": summary["final_horizon_mass"] > 0,
        "sink_ledger_mass_is_monotone": summary["horizon_mass_monotone"] is True,
        "sink_ledger_has_invariant_charge_breakdown": bool(backreaction["ledger"]["by_fiber"])
        and bool(backreaction["ledger"]["by_order"])
        and bool(backreaction["ledger"]["by_grade"])
        and bool(backreaction["ledger"]["by_mixed"]),
        "backreaction_reduces_live_grains_vs_baseline": summary[
            "backreaction_final_live_grains"
        ]
        < summary["baseline_final_live_grains"],
        "polarization_increases_vs_baseline": summary[
            "polarization_delta_vs_baseline_mean"
        ]
        > 0.0,
        "coil_coherence_increases_vs_baseline": summary[
            "coil_coherence_delta_vs_baseline_mean"
        ]
        > 0.0,
        "astar_bends_toward_horizon_vs_baseline": summary[
            "astar_inner_band_delta_vs_baseline_mean"
        ]
        > 0.0,
        "flux_localization_improves_vs_baseline": summary[
            "post_flux_localization_delta_vs_baseline_mean"
        ]
        > 0.0,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_MICRO_BLACK_HOLE_BACKREACTION_PROBE_CERTIFIED"
        if all_checks_pass
        else "D20_MICRO_BLACK_HOLE_BACKREACTION_PROBE_PROVISIONAL"
    )
    payload: dict[str, Any] = {
        "schema": "d20.proof_obligation.micro_black_hole_backreaction_probe.artifact@1",
        "status": status,
        "source": {
            "horizon_flux_astar_probe_report": input_entry(
                HORIZON_FLUX_REPORT,
                {"status": horizon.get("status"), "certificate_sha256": horizon.get("certificate_sha256")},
            ),
            "tesla_coil_astar_flux_probe_report": input_entry(
                TESLA_COIL_REPORT,
                {"status": tesla.get("status"), "certificate_sha256": tesla.get("certificate_sha256")},
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
        },
        "definition": {
            "object": "back-reacting D20 lifted sandpile micro-black-hole analog",
            "horizon_crossing": (
                "live chips in the inner shell band with inward radial transport activate a "
                "phase-selective sink; counter-winding, globally depolarizing, and outward-leaking "
                "fiber modes are preferentially removed after pre-absorption flux is measured"
            ),
            "astar_lensing_seam": (
                "A* pathing records both the raw invariant-cost field and a backreaction-only "
                "test-particle lens that lowers traversal cost near the inner shell band as the "
                "monotone horizon-mass ledger grows"
            ),
            "sink_ledger": (
                "absorbed chips are conserved in a ledger by frame, D20 fiber, sandpile class "
                "order, tube grade, and mixed-fiber flag"
            ),
            "micro_black_hole_signature": (
                "monotone horizon mass plus increased polarization, coil coherence, lensed A* "
                "horizon bending, and flux localization versus the no-backreaction replay"
            ),
            "physical_boundary": (
                "finite lifted-sandpile analog only; no continuum event horizon, curvature, or "
                "stress-energy semantics are claimed"
            ),
        },
        "witness": {
            "summary": summary,
            "baseline": {
                "rows_sha256": baseline["rows_sha256"],
                "astar_rows_sha256": baseline["astar_rows_sha256"],
                "rows_first_12": baseline["rows"][:12],
                "astar_rows": baseline["astar_rows"],
            },
            "backreaction": {
                "rows_sha256": backreaction["rows_sha256"],
                "astar_rows_sha256": backreaction["astar_rows_sha256"],
                "ledger_sha256": backreaction["ledger_sha256"],
                "ledger": backreaction["ledger"],
                "rows_first_12": backreaction["rows"][:12],
                "rows_compact": compact_backreaction_replay(backreaction),
                "astar_rows": backreaction["astar_rows"],
            },
        },
        "checks": checks,
    }
    payload["artifact_sha256_excluding_this_field"] = artifact_hash(payload)
    return payload


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    all_checks_pass = all(artifact["checks"].values())
    if all_checks_pass:
        claim = (
            "The D20 lifted sandpile satisfies the repo-local micro-black-hole backreaction "
            "signature: a conserved horizon ledger grows monotonically while polarization, "
            "coil coherence, A* horizon bending, and flux localization improve against the "
            "no-backreaction baseline."
        )
    else:
        claim = (
            "The D20 lifted sandpile now has a back-reacting micro-black-hole analog with a "
            "conserved invariant sink ledger, but one or more polarization/lensing/localization "
            "signatures remain provisional. The report records the measured deltas rather than "
            "promoting the physical interpretation."
        )
    report: dict[str, Any] = {
        "schema": "d20.proof_obligation.micro_black_hole_backreaction_probe@1",
        "status": artifact["status"],
        "all_checks_pass": all_checks_pass,
        "claim": claim,
        "stage_protocol": {
            "draft": "define micro black hole behavior as finite lifted-sandpile absorption with backreaction",
            "witness": "remove horizon-crossing chips and conserve their invariant charges in a sink ledger",
            "coherence": "compare back-reacting dynamics against no-backreaction replay",
            "closure": "validate mass growth, ledger conservation, polarization, coil coherence, A* bending, and flux localization",
            "emit": "emit measured signatures plus physical-claim boundary",
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
                "a deterministic back-reacting lifted-sandpile horizon",
                "a monotone conserved sink ledger by D20 invariant type when checks pass",
                "measured polarization, coil-coherence, raw and lensed A* bending, and flux-localization deltas against baseline",
            ],
            "does_not_certify": [
                "a physical micro black hole",
                "a continuum event horizon",
                "Einstein-equation curvature or stress-energy semantics",
                "Hawking radiation or thermodynamic black-hole laws",
            ],
        },
        "next_highest_yield_item": (
            "If the signature is provisional, tune only the explicit absorption law and re-run "
            "the same baseline-controlled probe; if certified, expose the horizon-mass ledger "
            "in the 3D renderer as a visible back-reacting core."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": "d20.proof_obligation.micro_black_hole_backreaction_probe_manifest@1",
        "name": THEOREM_ID,
        "certification_tests": [
            "run matched D20 lift replays with and without horizon backreaction",
            "remove inward horizon-crossing chips from the back-reacting state",
            "record absorbed chips in a conserved invariant sink ledger",
            "verify horizon mass monotonicity and live-grain reduction",
            "compare polarization, coil coherence, A* horizon bending, and flux localization against baseline",
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
    summary = report["witness"]["summary"]
    print(
        json.dumps(
            {
                "artifact": relpath(ARTIFACT_PATH),
                "report": relpath(OUT_DIR / "report.json"),
                "report_sha256": report["certificate_sha256"],
                "status": report["status"],
                "all_checks_pass": report["all_checks_pass"],
                "final_horizon_mass": summary["final_horizon_mass"],
                "polarization_delta_vs_baseline_mean": summary[
                    "polarization_delta_vs_baseline_mean"
                ],
                "coil_coherence_delta_vs_baseline_mean": summary[
                    "coil_coherence_delta_vs_baseline_mean"
                ],
                "astar_inner_band_delta_vs_baseline_mean": summary[
                    "astar_inner_band_delta_vs_baseline_mean"
                ],
                "flux_localization_delta_vs_baseline_mean": summary[
                    "post_flux_localization_delta_vs_baseline_mean"
                ],
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
