from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import heapq
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
        d20_lift_delta,
        load_visualization_data,
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
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_tesla_coil_astar_flux_probe"
ARTIFACT_PATH = GENERATED / f"{THEOREM_ID}.json"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

PHASE_AUDIT_REPORT = (
    D20_INVARIANTS / "proof_obligations" / "d20_geon_phase_entropy_audit" / "report.json"
)
RGBA_REPLAY_REPORT = (
    D20_INVARIANTS / "proof_obligations" / "d20_geon_rgba_replay_frame_archive" / "report.json"
)
DERIVE_SCRIPT = ROOT / "src" / "derive_d20_tesla_coil_astar_flux_probe.py"
VALIDATOR = ROOT / "src" / "certify_d20_tesla_coil_astar_flux_probe.py"

PATH_PAIR_COUNT = 8
NULL_SAMPLES = 32


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


def wrap_angle(delta: float) -> float:
    while delta <= -math.pi:
        delta += 2.0 * math.pi
    while delta > math.pi:
        delta -= 2.0 * math.pi
    return delta


def replay_lift() -> tuple[dict[str, Any], D20LiftSimulator, np.ndarray, np.ndarray, np.ndarray]:
    data, _ = load_visualization_data()
    sim = D20LiftSimulator(data)
    sim.seed()
    for _ in range(D20_WARMUP_STEPS):
        sim.step(9000)
    for _ in range(AUDIT_FRAMES):
        sim.step()
    categories, sums = sim.state_arrays()
    tensor = sim.state.reshape(sim.size, sim.size, sim.fibers)
    return data, sim, tensor, categories, sums


def transport_field(data: dict[str, Any], tensor: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    size = tensor.shape[0]
    fibers = tensor.shape[2]
    vx = np.zeros((size, size), dtype=float)
    vy = np.zeros((size, size), dtype=float)
    outgoing: list[list[tuple[int, int]]] = [[] for _ in range(fibers)]
    for edge in data["edges"]:
        dx, dy = d20_lift_delta(edge)
        outgoing[int(edge["u"])].append((dx, dy))
        outgoing[int(edge["v"])].append((-dx, -dy))
    for fiber in range(fibers):
        chips = tensor[:, :, fiber].astype(float)
        for dx, dy in outgoing[fiber]:
            vx += chips * dx
            vy += chips * dy
    return vx, vy


def shell_geometry(sums: np.ndarray) -> dict[str, Any]:
    size = sums.shape[0]
    ys, xs = np.indices(sums.shape)
    active = sums > 0
    if not np.any(active):
        raise ValueError("D20 lift replay has no active cells")
    total = float(sums.sum())
    center_x = float((xs * sums).sum() / total)
    center_y = float((ys * sums).sum() / total)
    radius = np.sqrt((xs - center_x) ** 2 + (ys - center_y) ** 2)
    active_radius = radius[active]
    inner = float(np.percentile(active_radius, 32))
    outer = float(np.percentile(active_radius, 88))
    if outer - inner < 8.0:
        midpoint = (inner + outer) / 2.0
        inner = max(2.0, midpoint - 4.0)
        outer = min(size / 2.0, midpoint + 4.0)
    shell = (radius >= inner) & (radius <= outer)
    hole = radius < inner
    inner_band = shell & (np.abs(radius - inner) <= 2.5)
    outer_band = shell & (np.abs(radius - outer) <= 2.5)
    shell_active = shell & active
    return {
        "center_x": center_x,
        "center_y": center_y,
        "inner_radius": inner,
        "outer_radius": outer,
        "shell": shell,
        "hole": hole,
        "inner_band": inner_band,
        "outer_band": outer_band,
        "radius": radius,
        "shell_cell_count": int(shell.sum()),
        "hole_cell_count": int(hole.sum()),
        "shell_active_cell_count": int(shell_active.sum()),
        "shell_coverage_ratio": float(shell_active.sum() / max(1, int(shell.sum()))),
    }


def vector_diagnostics(
    vx: np.ndarray,
    vy: np.ndarray,
    geometry: dict[str, Any],
) -> dict[str, Any]:
    radius = geometry["radius"]
    shell = geometry["shell"]
    inner_band = geometry["inner_band"]
    bulk = shell & ~inner_band & ~geometry["outer_band"]
    mag = np.sqrt(vx * vx + vy * vy)
    div = np.zeros_like(vx)
    curl = np.zeros_like(vx)
    div[1:-1, 1:-1] = (
        (vx[1:-1, 2:] - vx[1:-1, :-2]) * 0.5
        + (vy[2:, 1:-1] - vy[:-2, 1:-1]) * 0.5
    )
    curl[1:-1, 1:-1] = (
        (vy[1:-1, 2:] - vy[1:-1, :-2]) * 0.5
        - (vx[2:, 1:-1] - vx[:-2, 1:-1]) * 0.5
    )
    residual = np.sqrt(div * div + curl * curl)
    cx = float(geometry["center_x"])
    cy = float(geometry["center_y"])
    ys, xs = np.indices(vx.shape)
    safe_r = np.where(radius > 0, radius, 1.0)
    radial_out = (vx * (xs - cx) + vy * (ys - cy)) / safe_r
    hole_mean = float(residual[inner_band].mean()) if np.any(inner_band) else 0.0
    bulk_mean = float(residual[bulk].mean()) if np.any(bulk) else 0.0
    return {
        "transport_magnitude": mag,
        "divergence": div,
        "curl": curl,
        "residual": residual,
        "shell_transport_mean": float(mag[shell].mean()) if np.any(shell) else 0.0,
        "shell_transport_max": float(mag[shell].max()) if np.any(shell) else 0.0,
        "inner_band_residual_mean": hole_mean,
        "shell_bulk_residual_mean": bulk_mean,
        "hole_flux_anomaly_ratio": hole_mean / (bulk_mean + 1e-12),
        "inner_band_radial_flux_signed_mean": float(radial_out[inner_band].mean())
        if np.any(inner_band)
        else 0.0,
    }


def invariant_features(sim: D20LiftSimulator, shell: np.ndarray) -> dict[str, np.ndarray]:
    order = np.zeros(shell.shape, dtype=float)
    grade_negative = np.zeros(shell.shape, dtype=float)
    mixed = np.zeros(shell.shape, dtype=float)
    mask = np.zeros(shell.shape, dtype=int)
    for y, x in np.argwhere(shell):
        sample = sim.sample_cell(int(x), int(y))
        pixel = sample["pixel"]
        order[y, x] = float(pixel.get("o", 0)) / 30.0
        grade_negative[y, x] = 1.0 if int(pixel.get("g", 1)) < 0 else 0.0
        mixed[y, x] = 1.0 if int(pixel.get("x", 0)) else 0.0
        mask[y, x] = int(sample["mask"])
    return {
        "order": order,
        "grade_negative": grade_negative,
        "mixed": mixed,
        "mask": mask,
    }


def cost_from_features(
    geometry: dict[str, Any],
    features: dict[str, np.ndarray],
) -> np.ndarray:
    shell = geometry["shell"]
    radius = geometry["radius"]
    mid = (float(geometry["inner_radius"]) + float(geometry["outer_radius"])) / 2.0
    half_width = max(1.0, (float(geometry["outer_radius"]) - float(geometry["inner_radius"])) / 2.0)
    radial = np.abs(radius - mid) / half_width
    cost = (
        1.0
        + 0.78 * radial
        + 0.55 * features["order"]
        + 0.16 * features["grade_negative"]
        - 0.24 * features["mixed"]
    )
    cost = np.where(shell, np.maximum(0.12, cost), np.inf)
    return cost


def nearest_shell_point(
    geometry: dict[str, Any],
    angle: float,
) -> tuple[int, int]:
    shell = geometry["shell"]
    coords = np.argwhere(shell)
    cx = float(geometry["center_x"])
    cy = float(geometry["center_y"])
    radius = (float(geometry["inner_radius"]) + float(geometry["outer_radius"])) / 2.0
    tx = cx + radius * math.cos(angle)
    ty = cy + radius * math.sin(angle)
    dist = (coords[:, 1] - tx) ** 2 + (coords[:, 0] - ty) ** 2
    y, x = coords[int(np.argmin(dist))]
    return int(x), int(y)


def astar_path(
    start: tuple[int, int],
    goal: tuple[int, int],
    allowed: np.ndarray,
    cost: np.ndarray,
) -> list[tuple[int, int]]:
    size_y, size_x = allowed.shape
    moves = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1),
        (-1, -1),
        (-1, 1),
        (1, -1),
        (1, 1),
    ]
    open_heap: list[tuple[float, int, tuple[int, int]]] = []
    serial = 0
    heapq.heappush(open_heap, (0.0, serial, start))
    came_from: dict[tuple[int, int], tuple[int, int]] = {}
    g_score = {start: 0.0}

    def heuristic(node: tuple[int, int]) -> float:
        return math.hypot(goal[0] - node[0], goal[1] - node[1])

    while open_heap:
        _, _, current = heapq.heappop(open_heap)
        if current == goal:
            out = [current]
            while current in came_from:
                current = came_from[current]
                out.append(current)
            return list(reversed(out))
        cx, cy = current
        current_g = g_score[current]
        for dx, dy in moves:
            nx = cx + dx
            ny = cy + dy
            if nx < 0 or ny < 0 or nx >= size_x or ny >= size_y or not allowed[ny, nx]:
                continue
            step = math.hypot(dx, dy)
            local = step * (float(cost[cy, cx]) + float(cost[ny, nx])) * 0.5
            tentative = current_g + local
            node = (nx, ny)
            if tentative >= g_score.get(node, math.inf):
                continue
            came_from[node] = current
            g_score[node] = tentative
            serial += 1
            heapq.heappush(open_heap, (tentative + heuristic(node), serial, node))
    return []


def path_metrics(
    path: list[tuple[int, int]],
    vx: np.ndarray,
    vy: np.ndarray,
    mag: np.ndarray,
    high_flux_threshold: float,
    geometry: dict[str, Any],
) -> dict[str, Any]:
    if len(path) < 2:
        return {
            "path_length": len(path),
            "axis_alignment_mean": 0.0,
            "signed_alignment_mean": 0.0,
            "high_flux_overlap_fraction": 0.0,
            "angular_sweep_turns": 0.0,
            "inner_band_fraction": 0.0,
        }
    alignments = []
    signed = []
    high_flux = 0
    inner_band = 0
    angles = []
    cx = float(geometry["center_x"])
    cy = float(geometry["center_y"])
    for idx, (x, y) in enumerate(path):
        if mag[y, x] >= high_flux_threshold:
            high_flux += 1
        if geometry["inner_band"][y, x]:
            inner_band += 1
        angles.append(math.atan2(y - cy, x - cx))
        if idx + 1 >= len(path):
            continue
        nx, ny = path[idx + 1]
        dx = nx - x
        dy = ny - y
        step = math.hypot(dx, dy)
        local_mag = float(mag[y, x])
        if step and local_mag:
            cos = (float(vx[y, x]) * dx + float(vy[y, x]) * dy) / (local_mag * step)
            signed.append(cos)
            alignments.append(abs(cos))
    sweep = 0.0
    for left, right in zip(angles, angles[1:]):
        sweep += abs(wrap_angle(right - left))
    return {
        "path_length": len(path),
        "axis_alignment_mean": float(np.mean(alignments)) if alignments else 0.0,
        "signed_alignment_mean": float(np.mean(signed)) if signed else 0.0,
        "high_flux_overlap_fraction": float(high_flux / len(path)),
        "angular_sweep_turns": float(sweep / (2.0 * math.pi)),
        "inner_band_fraction": float(inner_band / len(path)),
    }


def path_suite(
    geometry: dict[str, Any],
    cost: np.ndarray,
    vx: np.ndarray,
    vy: np.ndarray,
    mag: np.ndarray,
) -> tuple[list[dict[str, Any]], dict[str, float]]:
    threshold = float(np.percentile(mag[geometry["shell"]], 75))
    rows = []
    for idx in range(PATH_PAIR_COUNT):
        angle = 2.0 * math.pi * idx / PATH_PAIR_COUNT
        start = nearest_shell_point(geometry, angle)
        goal = nearest_shell_point(geometry, angle + math.pi)
        path = astar_path(start, goal, geometry["shell"], cost)
        metrics = path_metrics(path, vx, vy, mag, threshold, geometry)
        rows.append(
            {
                "pair_index": idx,
                "start": list(start),
                "goal": list(goal),
                "found": bool(path),
                "path_sha256": sha_json(path),
                "path_first_16": [list(point) for point in path[:16]],
                **metrics,
            }
        )
    aggregate = {
        "path_count": float(len(rows)),
        "paths_found": float(sum(1 for row in rows if row["found"])),
        "axis_alignment_mean": float(np.mean([row["axis_alignment_mean"] for row in rows])),
        "high_flux_overlap_fraction_mean": float(
            np.mean([row["high_flux_overlap_fraction"] for row in rows])
        ),
        "angular_sweep_turns_mean": float(np.mean([row["angular_sweep_turns"] for row in rows])),
        "inner_band_fraction_mean": float(np.mean([row["inner_band_fraction"] for row in rows])),
    }
    return rows, aggregate


def null_suite(
    geometry: dict[str, Any],
    features: dict[str, np.ndarray],
    vx: np.ndarray,
    vy: np.ndarray,
    mag: np.ndarray,
) -> dict[str, Any]:
    rng = np.random.default_rng(20260527)
    shell_coords = np.argwhere(geometry["shell"])
    shell_index = (shell_coords[:, 0], shell_coords[:, 1])
    rows = []
    for sample in range(NULL_SAMPLES):
        shuffled = {
            key: value.copy()
            for key, value in features.items()
            if key in {"order", "grade_negative", "mixed"}
        }
        for key in shuffled:
            values = shuffled[key][shell_index].copy()
            rng.shuffle(values)
            shuffled[key][shell_index] = values
        cost = cost_from_features(geometry, shuffled)
        _, aggregate = path_suite(geometry, cost, vx, vy, mag)
        rows.append(
            {
                "sample": sample,
                "axis_alignment_mean": aggregate["axis_alignment_mean"],
                "high_flux_overlap_fraction_mean": aggregate["high_flux_overlap_fraction_mean"],
                "angular_sweep_turns_mean": aggregate["angular_sweep_turns_mean"],
                "paths_found": aggregate["paths_found"],
            }
        )
    def stats(name: str) -> dict[str, float]:
        values = np.asarray([row[name] for row in rows], dtype=float)
        return {
            "mean": float(values.mean()),
            "std": float(values.std(ddof=1)) if len(values) > 1 else 0.0,
            "min": float(values.min()),
            "max": float(values.max()),
        }
    return {
        "sample_count": NULL_SAMPLES,
        "shuffle_model": "permute order, tube-grade sign, and mixed-fiber flags over fixed shell cells",
        "summary": {
            "axis_alignment_mean": stats("axis_alignment_mean"),
            "high_flux_overlap_fraction_mean": stats("high_flux_overlap_fraction_mean"),
            "angular_sweep_turns_mean": stats("angular_sweep_turns_mean"),
        },
        "rows_sha256": sha_json(rows),
        "rows_first_8": rows[:8],
    }


def vector_field_index(
    vx: np.ndarray,
    vy: np.ndarray,
    geometry: dict[str, Any],
    sample_count: int = 192,
) -> dict[str, Any]:
    cx = float(geometry["center_x"])
    cy = float(geometry["center_y"])
    radius = float(geometry["inner_radius"]) + 2.0
    angles = []
    used = 0
    for idx in range(sample_count):
        theta = 2.0 * math.pi * idx / sample_count
        x = int(round(cx + radius * math.cos(theta)))
        y = int(round(cy + radius * math.sin(theta)))
        if x < 0 or y < 0 or x >= vx.shape[1] or y >= vx.shape[0]:
            continue
        mag = math.hypot(float(vx[y, x]), float(vy[y, x]))
        if mag <= 0:
            continue
        angles.append(math.atan2(float(vy[y, x]), float(vx[y, x])))
        used += 1
    winding = 0.0
    if len(angles) > 1:
        closed = angles + [angles[0]]
        winding = sum(wrap_angle(right - left) for left, right in zip(closed, closed[1:]))
    return {
        "loop_radius": radius,
        "sample_count": sample_count,
        "nonzero_vector_samples": used,
        "index_turns": float(winding / (2.0 * math.pi)),
        "index_abs_turns": float(abs(winding) / (2.0 * math.pi)),
    }


def artifact_hash(payload: dict[str, Any]) -> str:
    return self_hash(payload, "artifact_sha256_excluding_this_field")


def build_artifact() -> dict[str, Any]:
    data, sim, tensor, _categories, sums = replay_lift()
    phase = load_json(PHASE_AUDIT_REPORT)
    rgba = load_json(RGBA_REPLAY_REPORT)
    vx, vy = transport_field(data, tensor)
    geometry = shell_geometry(sums)
    diagnostics = vector_diagnostics(vx, vy, geometry)
    features = invariant_features(sim, geometry["shell"])
    cost = cost_from_features(geometry, features)
    mag = diagnostics["transport_magnitude"]
    paths, aggregate = path_suite(geometry, cost, vx, vy, mag)
    null = null_suite(geometry, features, vx, vy, mag)
    index = vector_field_index(vx, vy, geometry)

    observed_alignment = aggregate["axis_alignment_mean"]
    null_alignment = null["summary"]["axis_alignment_mean"]["mean"]
    null_alignment_std = null["summary"]["axis_alignment_mean"]["std"]
    observed_overlap = aggregate["high_flux_overlap_fraction_mean"]
    null_overlap = null["summary"]["high_flux_overlap_fraction_mean"]["mean"]
    null_overlap_std = null["summary"]["high_flux_overlap_fraction_mean"]["std"]

    alignment_z = (
        (observed_alignment - null_alignment) / null_alignment_std
        if null_alignment_std > 0
        else math.inf
    )
    overlap_z = (
        (observed_overlap - null_overlap) / null_overlap_std
        if null_overlap_std > 0
        else math.inf
    )

    serial_geometry = {
        key: value
        for key, value in geometry.items()
        if key
        not in {
            "shell",
            "hole",
            "inner_band",
            "outer_band",
            "radius",
        }
    }
    checks = {
        "phase_entropy_audit_certified": phase.get("status") == "D20_GEON_PHASE_ENTROPY_AUDIT_CERTIFIED",
        "rgba_replay_archive_certified": rgba.get("status")
        == "D20_GEON_RGBA_REPLAY_FRAME_ARCHIVE_CERTIFIED_BROWSER_CAPTURE_BLOCKED",
        "shell_has_nonempty_hole": serial_geometry["hole_cell_count"] > 0,
        "shell_has_nonempty_transport": diagnostics["shell_transport_max"] > 0.0,
        "astar_found_all_path_pairs": aggregate["paths_found"] == float(PATH_PAIR_COUNT),
        "vector_field_index_measurable": index["nonzero_vector_samples"] >= 64,
        "hole_flux_anomaly_ratio_exceeds_bulk": diagnostics["hole_flux_anomaly_ratio"] > 1.0,
        "astar_alignment_exceeds_invariant_shuffle_mean": observed_alignment > null_alignment,
        "astar_high_flux_overlap_exceeds_invariant_shuffle_mean": observed_overlap > null_overlap,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_TESLA_COIL_ASTAR_FLUX_PROBE_CERTIFIED"
        if all_checks_pass
        else "D20_TESLA_COIL_ASTAR_FLUX_PROBE_PROVISIONAL"
    )
    payload: dict[str, Any] = {
        "schema": "d20.proof_obligation.tesla_coil_astar_flux_probe.artifact@1",
        "status": status,
        "source": {
            "phase_entropy_audit_report": input_entry(
                PHASE_AUDIT_REPORT,
                {"status": phase.get("status"), "certificate_sha256": phase.get("certificate_sha256")},
            ),
            "rgba_replay_archive_report": input_entry(
                RGBA_REPLAY_REPORT,
                {"status": rgba.get("status"), "certificate_sha256": rgba.get("certificate_sha256")},
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
        },
        "definition": {
            "object": "D20 lifted sandpile final replay state",
            "hole_model": (
                "mass-weighted annular public shell; the inner disk is the operational topological hole"
            ),
            "transport_field": (
                "per-cell outgoing D20 lift vector obtained by summing live chips over certified "
                "cooriented graph edge deltas"
            ),
            "astar_model": (
                "eight opposite shell point pairs solved by A* over the annulus with local cost from "
                "radial shell position plus RGBA atom order, tube-grade sign, and mixed-fiber flag"
            ),
            "null_model": "shuffle invariant labels over the fixed shell, preserving geometry and transport",
        },
        "witness": {
            "shell": serial_geometry,
            "flux": {
                key: value
                for key, value in diagnostics.items()
                if key
                not in {
                    "transport_magnitude",
                    "divergence",
                    "curl",
                    "residual",
                }
            },
            "vector_field_index": index,
            "astar_paths": {
                "pair_count": PATH_PAIR_COUNT,
                "aggregate": aggregate,
                "paths": paths,
            },
            "null_shuffle": null,
            "effect_sizes": {
                "axis_alignment_delta_vs_null": observed_alignment - null_alignment,
                "axis_alignment_z_vs_null": alignment_z,
                "high_flux_overlap_delta_vs_null": observed_overlap - null_overlap,
                "high_flux_overlap_z_vs_null": overlap_z,
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
            "The D20 lifted sandpile coil has a certified nontrivial pathing signal: "
            "invariant-weighted A* routes on the annular shell align with measured transport and "
            "high-flux cells better than invariant-label shuffles, while flux residual localizes "
            "near the operational hole."
        )
    else:
        claim = (
            "The D20 lifted sandpile coil is measured as a serious topological-pathing candidate, "
            "but one or more signal checks remain provisional. The report records the A* paths, "
            "flux anomaly, vector-field index, and null-shuffle controls without promoting a "
            "black-hole or physical-geon claim."
        )
    report: dict[str, Any] = {
        "schema": "d20.proof_obligation.tesla_coil_astar_flux_probe@1",
        "status": artifact["status"],
        "all_checks_pass": all_checks_pass,
        "claim": claim,
        "stage_protocol": {
            "draft": "treat the visible coil as a discrete vector-field/pathing hypothesis",
            "witness": "derive annular shell, hole, transport field, A* paths, flux residuals, and null shuffles",
            "coherence": "compare invariant-weighted A* routes against actual D20 lift transport",
            "closure": "validate reproducibility, path existence, flux anomaly, vector index, and null deltas",
            "emit": "emit measured effect sizes plus explicit black-hole boundary conditions not yet certified",
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
                "a deterministic D20 lift transport field over an operational annular shell",
                "explicit invariant-weighted A* paths around the hole",
                "flux residual, vector-field index, and invariant-shuffle controls",
            ],
            "does_not_certify": [
                "a continuum black-hole spacetime",
                "Einstein-equation curvature or stress-energy semantics",
                "a physical Tesla coil",
                "browser compositor/subpixel behavior",
            ],
        },
        "next_highest_yield_item": (
            "Promote the operational hole to an absorbing horizon: measure invariant flux crossing "
            "the horizon shell per frame and compare lensing/path-bending against the A* baseline."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": "d20.proof_obligation.tesla_coil_astar_flux_probe_manifest@1",
        "name": THEOREM_ID,
        "certification_tests": [
            "replay the deterministic D20 lifted sandpile to the audited final frame",
            "derive the mass-weighted annular shell and operational hole",
            "compute the outgoing D20 lift transport vector field",
            "solve eight invariant-weighted A* path pairs around the hole",
            "compare path alignment and high-flux overlap against invariant-label shuffles",
            "compute flux residual localization and vector-field index around the hole",
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
                "hole_flux_anomaly_ratio": report["witness"]["flux"]["hole_flux_anomaly_ratio"],
                "axis_alignment_delta_vs_null": report["witness"]["effect_sizes"][
                    "axis_alignment_delta_vs_null"
                ],
                "high_flux_overlap_delta_vs_null": report["witness"]["effect_sizes"][
                    "high_flux_overlap_delta_vs_null"
                ],
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
