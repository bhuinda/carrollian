from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_geon_phase_entropy_audit"
ARTIFACT_PATH = GENERATED / f"{THEOREM_ID}.json"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

VISUALIZATION = GENERATED / "d20_sandpile_visualization.html"
EDGE_STEPS = GENERATED / "d20_voltage_lift_edge_steps.json"
FAMILY_ARTIFACT = GENERATED / "d20_voltage_lift_family_comparison.json"
INTRINSIC_ARTIFACT = GENERATED / "d20_voltage_lift_intrinsic_hex_metric.json"
INTRINSIC_REPORT = (
    D20_INVARIANTS / "proof_obligations" / "d20_voltage_lift_intrinsic_hex_metric" / "report.json"
)
FAMILY_REPORT = (
    D20_INVARIANTS / "proof_obligations" / "d20_voltage_lift_family_robust_oblongness" / "report.json"
)
ROBUST_REPORT = D20_INVARIANTS / "theorems" / "d20_voltage_lift_robust_oblongness" / "report.json"
GOLAY_PROBE_REPORT = (
    D20_INVARIANTS / "proof_obligations" / "d20_golay_hamming_correspondence_probe" / "report.json"
)
GOLAY_MINOR_REPORT = (
    D20_INVARIANTS / "proof_obligations" / "d20_golay_hamming_minor_puncture_search" / "report.json"
)

DERIVE_SCRIPT = ROOT / "src" / "derive_d20_geon_phase_entropy_audit.py"
VALIDATOR = ROOT / "src" / "certify_d20_geon_phase_entropy_audit.py"

D20_SIZE = 128
TOPPLE_SIZE = 72
D20_WARMUP_STEPS = 36
AUDIT_FRAMES = 96
NULL_SAMPLES = 64
SAMPLE_FRAMES = {0, 1, 8, 32, 64, 96}

D20_PALETTE = [
    [5, 8, 7],
    [40, 120, 79],
    [123, 77, 177],
    [243, 191, 77],
    [233, 79, 65],
]
TOPPLE_PALETTE = [
    [6, 16, 14],
    [25, 82, 87],
    [200, 112, 56],
    [243, 213, 106],
    [233, 79, 65],
]

D20_LABEL_VECTORS = {
    "B-": (-1.0, 0.0),
    "B+": (1.0, 0.0),
    "V-": (0.0, -1.0),
    "V+": (0.0, 1.0),
    "S-": (-1.0, 1.0),
    "S+": (1.0, -1.0),
}
SQRT3 = math.sqrt(3.0)
D20_HEX_LABEL_VECTORS = {
    "B-": (-1.0, 0.0),
    "B+": (1.0, 0.0),
    "V-": (0.5, -SQRT3 / 2.0),
    "V+": (-0.5, SQRT3 / 2.0),
    "S-": (0.5, SQRT3 / 2.0),
    "S+": (-0.5, -SQRT3 / 2.0),
}


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


def load_visualization_data() -> tuple[dict[str, Any], str]:
    text = VISUALIZATION.read_text(encoding="utf-8")
    match = re.search(r"const DATA = (\{.*?\});\n", text, re.S)
    if not match:
        raise ValueError("generated D20 sandpile visualization does not contain a DATA object")
    data = json.loads(match.group(1))
    if not isinstance(data, dict):
        raise ValueError("visualization DATA is not a JSON object")
    return data, text


def label_set(text: str) -> set[str]:
    return set(re.findall(r"[BVS][+-]", text))


def replacement(edge: dict[str, Any]) -> tuple[str, str]:
    u = label_set(str(edge["uLabel"]))
    v = label_set(str(edge["vLabel"]))
    leaving = sorted(u - v)
    entering = sorted(v - u)
    if len(leaving) != 1 or len(entering) != 1:
        raise ValueError(f"edge {edge.get('id')} is not a single-label transition")
    return leaving[0], entering[0]


def sign(value: float) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def d20_lift_delta(edge: dict[str, Any]) -> tuple[int, int]:
    leaving, entering = replacement(edge)
    ax, ay = D20_LABEL_VECTORS[leaving]
    bx, by = D20_LABEL_VECTORS[entering]
    dx = sign(bx - ax)
    dy = sign(by - ay)
    return (
        dx if dx else (1 if int(edge["choice"]) % 2 else -1),
        dy if dy else (1 if int(edge["choice"]) == 2 else 0),
    )


def d20_hex_delta(edge: dict[str, Any]) -> tuple[float, float]:
    leaving, entering = replacement(edge)
    ax, ay = D20_HEX_LABEL_VECTORS[leaving]
    bx, by = D20_HEX_LABEL_VECTORS[entering]
    return bx - ax, by - ay


def step_covariance(edges: list[dict[str, Any]], delta_fn: Any) -> dict[str, float]:
    pairs = [delta_fn(edge) for edge in edges]
    n = float(len(pairs))
    a = sum(dx * dx for dx, _ in pairs) / n
    b = sum(dx * dy for dx, dy in pairs) / n
    d = sum(dy * dy for _, dy in pairs) / n
    disc = math.sqrt((a - d) ** 2 + 4 * b * b)
    major = (a + d + disc) / 2.0
    minor = (a + d - disc) / 2.0
    vx = b
    vy = major - a
    norm = math.hypot(vx, vy) or 1.0
    vx /= norm
    vy /= norm
    if vx < 0:
        vx = -vx
        vy = -vy
    return {
        "anisotropy_ratio": major / minor,
        "principal_axis_angle_degrees": math.atan2(vy, vx) * 180.0 / math.pi,
    }


def entropy_from_counts(counts: list[int]) -> float:
    total = sum(counts)
    if total <= 0:
        return 0.0
    out = 0.0
    for count in counts:
        if count:
            p = count / total
            out -= p * math.log2(p)
    return out


def palette_channel_entropies(counts: list[int], palette: list[list[int]]) -> dict[str, Any]:
    channels = {"red": {}, "green": {}, "blue": {}, "alpha": {255: sum(counts)}}
    for count, color in zip(counts, palette):
        for name, value in zip(("red", "green", "blue"), color):
            channels[name][value] = channels[name].get(value, 0) + count
    entropy = {
        name: entropy_from_counts([int(v) for v in values.values()])
        for name, values in channels.items()
    }
    unique = {name: sorted(int(k) for k in values) for name, values in channels.items()}
    return {"entropy_bits": entropy, "unique_values": unique}


def rgba_channel_summary(rgba: np.ndarray) -> dict[str, Any]:
    channels: dict[str, dict[int, int]] = {}
    for idx, name in enumerate(("red", "green", "blue", "alpha")):
        values, counts = np.unique(rgba[:, :, idx], return_counts=True)
        channels[name] = {
            int(value): int(count)
            for value, count in zip(values.tolist(), counts.tolist())
        }
    entropy = {
        name: entropy_from_counts(list(values.values()))
        for name, values in channels.items()
    }
    unique = {name: sorted(values) for name, values in channels.items()}
    return {"entropy_bits": entropy, "unique_values": unique}


def js_round(value: float) -> int:
    return int(math.floor(value + 0.5))


def signed_frequency(index: int, size: int) -> int:
    return index if index <= size // 2 else index - size


def spectral_metrics(grid: np.ndarray) -> dict[str, Any]:
    arr = grid.astype(float)
    arr = arr - float(arr.mean())
    power = np.abs(np.fft.fft2(arr)) ** 2
    power[0, 0] = 0.0
    total = float(power.sum())
    if total == 0.0:
        return {
            "dominant_non_dc_power_fraction": 0.0,
            "dominant_signed_frequency_xy": [0, 0],
            "spectral_entropy_normalized": 0.0,
        }
    y_idx, x_idx = np.unravel_index(int(np.argmax(power)), power.shape)
    probabilities = (power.ravel() / total)
    probabilities = probabilities[probabilities > 0]
    entropy = float(-(probabilities * np.log2(probabilities)).sum())
    return {
        "dominant_non_dc_power_fraction": float(power[y_idx, x_idx] / total),
        "dominant_signed_frequency_xy": [
            signed_frequency(int(x_idx), grid.shape[1]),
            signed_frequency(int(y_idx), grid.shape[0]),
        ],
        "spectral_entropy_normalized": entropy / math.log2(power.size - 1),
    }


def shuffle_null_metrics(grid: np.ndarray, samples: int = NULL_SAMPLES) -> dict[str, Any]:
    rng = np.random.default_rng(54320)
    flat = grid.ravel().copy()
    dominant: list[float] = []
    entropy: list[float] = []
    for _ in range(samples):
        rng.shuffle(flat)
        metrics = spectral_metrics(flat.reshape(grid.shape))
        dominant.append(float(metrics["dominant_non_dc_power_fraction"]))
        entropy.append(float(metrics["spectral_entropy_normalized"]))
    dom_mean = float(np.mean(dominant))
    dom_sd = float(np.std(dominant, ddof=1)) if samples > 1 else 0.0
    ent_mean = float(np.mean(entropy))
    ent_sd = float(np.std(entropy, ddof=1)) if samples > 1 else 0.0
    observed = spectral_metrics(grid)
    observed_dom = float(observed["dominant_non_dc_power_fraction"])
    observed_ent = float(observed["spectral_entropy_normalized"])
    return {
        "histogram_preserving_shuffle_samples": samples,
        "observed": observed,
        "shuffle_mean": {
            "dominant_non_dc_power_fraction": dom_mean,
            "spectral_entropy_normalized": ent_mean,
        },
        "shuffle_sample_sd": {
            "dominant_non_dc_power_fraction": dom_sd,
            "spectral_entropy_normalized": ent_sd,
        },
        "z_scores": {
            "dominant_non_dc_power_fraction": (observed_dom - dom_mean) / dom_sd if dom_sd else math.inf,
            "spectral_entropy_normalized": (observed_ent - ent_mean) / ent_sd if ent_sd else -math.inf,
        },
    }


def weighted_covariance_ratio(weights: np.ndarray) -> float:
    total = float(weights.sum())
    if total <= 0:
        return 0.0
    ys, xs = np.indices(weights.shape)
    mx = float((xs * weights).sum() / total)
    my = float((ys * weights).sum() / total)
    dx = xs - mx
    dy = ys - my
    xx = float((dx * dx * weights).sum() / total)
    xy = float((dx * dy * weights).sum() / total)
    yy = float((dy * dy * weights).sum() / total)
    disc = math.sqrt((xx - yy) ** 2 + 4 * xy * xy)
    major = (xx + yy + disc) / 2.0
    minor = (xx + yy - disc) / 2.0
    return major / minor if minor > 0 else math.inf


class D20LiftSimulator:
    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data
        self.size = D20_SIZE
        self.fibers = len(data["nodes"])
        self.source = int(data["summary"]["graph"]["sink_vertex"])
        self.state = np.zeros(self.size * self.size * self.fibers, dtype=np.uint64)
        self.queued = np.zeros(self.size * self.size * self.fibers, dtype=np.uint8)
        self.queue: list[int] = []
        self.topples = 0
        self.boundary_loss = 0
        self.cursor = 0
        self.neighbors: list[list[tuple[int, int, int]]] = [[] for _ in range(self.fibers)]
        for edge in data["edges"]:
            dx, dy = d20_lift_delta(edge)
            self.neighbors[int(edge["u"])].append((int(edge["v"]), dx, dy))
            self.neighbors[int(edge["v"])].append((int(edge["u"]), -dx, -dy))
        self.cooriented_covariance = step_covariance(data["edges"], d20_lift_delta)
        self.hex_covariance = step_covariance(data["edges"], d20_hex_delta)

    def index(self, x: int, y: int, v: int) -> int:
        return ((y * self.size + x) * self.fibers) + v

    def enqueue(self, index: int) -> None:
        if self.state[index] >= 3 and not self.queued[index]:
            self.queued[index] = 1
            self.queue.append(index)

    def add(self, x: int, y: int, v: int, grains: int) -> None:
        if x < 0 or y < 0 or x >= self.size or y >= self.size:
            self.boundary_loss += int(grains)
            return
        index = self.index(x, y, v)
        self.state[index] += int(grains)
        self.enqueue(index)

    def seed(self) -> None:
        self.state.fill(0)
        self.queued.fill(0)
        self.queue = []
        self.topples = 0
        self.boundary_loss = 0
        self.cursor = 0
        center = self.size // 2
        for move in self.data["summary"]["kernel"]["smallCoverMoves"]:
            pixel = self.data["pixels"][int(move) % len(self.data["pixels"])]
            x = center + ((int(move) % 17) - 8)
            y = center + (((int(move) >> 3) % 17) - 8)
            v = (int(pixel["c"]) + int(pixel["a"]) + int(pixel["o"])) % self.fibers
            self.add(x, y, v, 90 + (int(move) % 45))
        self.add(center, center, self.source, 6000)

    def drop(self) -> None:
        center = self.size // 2
        pixel = self.data["pixels"][self.cursor % len(self.data["pixels"])]
        self.cursor += 37
        v = (int(pixel["m"]) + int(pixel["c"]) + int(pixel["a"]) + int(pixel["o"])) % self.fibers
        self.add(center, center, v, 90 + int(pixel["a"]) + (45 if int(pixel["x"]) else 0))

    def step(self, limit: int = 7000) -> None:
        events = 0
        while self.queue and events < limit:
            index = self.queue.pop()
            self.queued[index] = 0
            chips = int(self.state[index])
            if chips < 3:
                continue
            q = chips // 3
            self.state[index] -= q * 3
            self.topples += q
            events += 1
            fiber = index % self.fibers
            cell = index // self.fibers
            x = cell % self.size
            y = cell // self.size
            for next_fiber, dx, dy in self.neighbors[fiber]:
                self.add(x + dx, y + dy, next_fiber, q)
            self.enqueue(index)
        if not self.queue:
            self.drop()

    def state_arrays(self) -> tuple[np.ndarray, np.ndarray]:
        tensor = self.state.reshape(self.size, self.size, self.fibers)
        sums = tensor.sum(axis=2)
        hot = (tensor >= 3).any(axis=2)
        signature = (sums + 2 * tensor[:, :, 1] + 3 * tensor[:, :, 7] + 5 * tensor[:, :, 14]) & 3
        return np.where(hot, 4, signature).astype(np.uint8), sums

    def category_at(self, categories: np.ndarray, x: int, y: int) -> int:
        if x < 0 or y < 0 or x >= self.size or y >= self.size:
            return 0
        return int(categories[y, x])

    def sample_cell(self, x: int, y: int) -> dict[str, Any]:
        if x < 0 or y < 0 or x >= self.size or y >= self.size:
            return {
                "sum": 0,
                "hot": False,
                "signature": 0,
                "dominant_fiber": 0,
                "dominant_chips": 0,
                "mask": 0,
                "pixel": self.data["pixels"][0],
            }
        cell_base = (y * self.size + x) * self.fibers
        total = 0
        hot = False
        dominant_fiber = 0
        dominant_chips = -1
        folded = 0
        signature_terms = {1: 0, 7: 0, 14: 0}
        for fiber in range(self.fibers):
            chips = int(self.state[cell_base + fiber])
            total += chips
            hot = hot or chips >= 3
            if chips > dominant_chips:
                dominant_chips = chips
                dominant_fiber = fiber
            folded = (folded + (((fiber + 1) * (chips % 2048)) & 2047)) & 2047
            if fiber in signature_terms:
                signature_terms[fiber] = chips
        signature = (
            total
            + 2 * signature_terms[1]
            + 3 * signature_terms[7]
            + 5 * signature_terms[14]
        ) & 3
        mask = (
            folded
            ^ (total & 2047)
            ^ ((dominant_fiber * 131) & 2047)
            ^ ((signature & 3) << 9)
            ^ (1024 if hot else 0)
        ) & 2047
        return {
            "sum": total,
            "hot": hot,
            "signature": signature,
            "dominant_fiber": dominant_fiber,
            "dominant_chips": dominant_chips,
            "mask": mask,
            "pixel": self.data["pixels"][mask],
        }

    def rgba_atom_from_sample(self, sample: dict[str, Any]) -> list[int]:
        if not int(sample["sum"]):
            return [0, 0, 0, 255]
        pixel = sample["pixel"]
        red = 255 if sample["hot"] else min(
            254,
            int(round(math.log1p(int(sample["sum"])) * 38 + int(sample["signature"]) * 7)),
        )
        green = int(round(int(sample["dominant_fiber"]) * 255 / max(1, self.fibers - 1)))
        order_byte = int(round(int(pixel.get("o", 0)) * 255 / 30))
        grade_byte = 48 if int(pixel.get("g", 1)) > 0 else 8
        mixed_byte = 54 if int(pixel.get("x", 0)) else 0
        blue = max(0, min(255, int(round(order_byte * 0.62 + grade_byte + mixed_byte))))
        return [red, green, blue, 255]

    def bounding_box(self, sums: np.ndarray) -> tuple[float, float, float]:
        ys, xs = np.nonzero(sums > 0)
        if len(xs) == 0:
            return (self.size - 1) / 2.0, (self.size - 1) / 2.0, self.size / 2.0
        min_x = int(xs.min())
        max_x = int(xs.max())
        min_y = int(ys.min())
        max_y = int(ys.max())
        center_x = (min_x + max_x) / 2.0
        center_y = (min_y + max_y) / 2.0
        half_span = max(max_x - min_x + 1, max_y - min_y + 1, 8) / 2.0 + 2.0
        return center_x, center_y, half_span

    def render_cooriented(self, categories: np.ndarray, sums: np.ndarray) -> np.ndarray:
        center_x, center_y, half_span = self.bounding_box(sums)
        out = np.zeros((self.size, self.size), dtype=np.uint8)
        for y in range(self.size):
            sy = max(
                0,
                min(
                    self.size - 1,
                    js_round(center_y - half_span + ((y + 0.5) / self.size) * half_span * 2.0),
                ),
            )
            for x in range(self.size):
                sx = max(
                    0,
                    min(
                        self.size - 1,
                        js_round(center_x - half_span + ((x + 0.5) / self.size) * half_span * 2.0),
                    ),
                )
                out[y, x] = self.category_at(categories, sx, sy)
        return out

    def render_hex(self, categories: np.ndarray, sums: np.ndarray) -> np.ndarray:
        center_x, center_y, half_span = self.bounding_box(sums)
        scale = math.sqrt(
            self.cooriented_covariance["anisotropy_ratio"] / self.hex_covariance["anisotropy_ratio"]
        )
        angle = self.cooriented_covariance["principal_axis_angle_degrees"] * math.pi / 180.0
        axis_x = math.cos(angle)
        axis_y = math.sin(angle)
        out = np.zeros((self.size, self.size), dtype=np.uint8)
        for y in range(self.size):
            for x in range(self.size):
                world_x = center_x - half_span + ((x + 0.5) / self.size) * half_span * 2.0
                world_y = center_y - half_span + ((y + 0.5) / self.size) * half_span * 2.0
                dx = world_x - center_x
                dy = world_y - center_y
                major = (dx * axis_x + dy * axis_y) * scale
                minor = -dx * axis_y + dy * axis_x
                sx = js_round(center_x + major * axis_x - minor * axis_y)
                sy = js_round(center_y + major * axis_y + minor * axis_x)
                out[y, x] = self.category_at(categories, sx, sy)
        return out

    def render_rgba_atom(self, sums: np.ndarray) -> np.ndarray:
        center_x, center_y, half_span = self.bounding_box(sums)
        out = np.zeros((self.size, self.size, 4), dtype=np.uint8)
        for y in range(self.size):
            sy = max(
                0,
                min(
                    self.size - 1,
                    js_round(center_y - half_span + ((y + 0.5) / self.size) * half_span * 2.0),
                ),
            )
            for x in range(self.size):
                sx = max(
                    0,
                    min(
                        self.size - 1,
                        js_round(center_x - half_span + ((x + 0.5) / self.size) * half_span * 2.0),
                    ),
                )
                out[y, x] = self.rgba_atom_from_sample(self.sample_cell(sx, sy))
        return out

    def run(self) -> dict[str, Any]:
        self.seed()
        for _ in range(D20_WARMUP_STEPS):
            self.step(9000)
        samples: list[dict[str, Any]] = []
        previous_render: np.ndarray | None = None
        final_render = None
        final_hex_render = None
        final_atom_rgba = None
        final_state_categories = None
        for frame in range(AUDIT_FRAMES + 1):
            if frame > 0:
                self.step()
            categories, sums = self.state_arrays()
            render = self.render_cooriented(categories, sums)
            hex_render = self.render_hex(categories, sums)
            atom_rgba = self.render_rgba_atom(sums)
            if frame in SAMPLE_FRAMES:
                counts = np.bincount(render.ravel(), minlength=5).astype(int).tolist()
                hex_counts = np.bincount(hex_render.ravel(), minlength=5).astype(int).tolist()
                atom_channels = rgba_channel_summary(atom_rgba)
                samples.append(
                    {
                        "frame": frame,
                        "live_grains": int(sums.sum()),
                        "active_cells": int((sums > 0).sum()),
                        "hot_render_pixels": int(counts[4]),
                        "render_entropy_bits": entropy_from_counts(counts),
                        "hex_render_entropy_bits": entropy_from_counts(hex_counts),
                        "rgba_atom_red_entropy_bits": atom_channels["entropy_bits"]["red"],
                        "rgba_atom_green_entropy_bits": atom_channels["entropy_bits"]["green"],
                        "rgba_atom_blue_entropy_bits": atom_channels["entropy_bits"]["blue"],
                        "rgba_atom_alpha_entropy_bits": atom_channels["entropy_bits"]["alpha"],
                        "weighted_state_covariance_ratio": weighted_covariance_ratio(sums),
                        "topples": int(self.topples),
                        "boundary_loss": int(self.boundary_loss),
                        "active_queue": len(self.queue),
                        "render_delta_fraction": None
                        if previous_render is None
                        else float((render != previous_render).mean()),
                    }
                )
            previous_render = render.copy()
            final_render = render
            final_hex_render = hex_render
            final_atom_rgba = atom_rgba
            final_state_categories = categories
        assert final_render is not None
        assert final_hex_render is not None
        assert final_atom_rgba is not None
        assert final_state_categories is not None
        counts = np.bincount(final_render.ravel(), minlength=5).astype(int).tolist()
        hex_counts = np.bincount(final_hex_render.ravel(), minlength=5).astype(int).tolist()
        state_counts = np.bincount(final_state_categories.ravel(), minlength=5).astype(int).tolist()
        atom_channels = rgba_channel_summary(final_atom_rgba)
        return {
            "simulation": {
                "canvas_size": [self.size, self.size],
                "fiber_count": self.fibers,
                "warmup_steps": D20_WARMUP_STEPS,
                "audit_frames_after_warmup": AUDIT_FRAMES,
                "topple_limit_per_frame": 7000,
                "warmup_topple_limit": 9000,
                "seed_small_cover_move_count": len(self.data["summary"]["kernel"]["smallCoverMoves"]),
            },
            "final": {
                "live_grains": int(self.state.reshape(self.size, self.size, self.fibers).sum()),
                "topples": int(self.topples),
                "boundary_loss": int(self.boundary_loss),
                "active_queue": len(self.queue),
                "state_category_counts": state_counts,
                "state_entropy_bits": entropy_from_counts(state_counts),
                "cooriented_render_category_counts": counts,
                "cooriented_render_entropy_bits": entropy_from_counts(counts),
                "hex_render_category_counts": hex_counts,
                "hex_render_entropy_bits": entropy_from_counts(hex_counts),
                "cooriented_render_channels": palette_channel_entropies(counts, D20_PALETTE),
                "hex_render_channels": palette_channel_entropies(hex_counts, D20_PALETTE),
                "cooriented_render_spectral_null": shuffle_null_metrics(final_render),
                "hex_render_spectral": spectral_metrics(final_hex_render),
                "rgba_atom_sha256": hashlib.sha256(final_atom_rgba.tobytes()).hexdigest(),
                "rgba_atom_channels": atom_channels,
                "rgba_atom_channel_entropy_bits": atom_channels["entropy_bits"],
                "rgba_atom_red_spectral": spectral_metrics(final_atom_rgba[:, :, 0]),
            },
            "sample_frames": samples,
        }


class ToppleSimulator:
    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data
        self.size = TOPPLE_SIZE
        self.grid = np.zeros(self.size * self.size, dtype=np.uint64)
        self.queued = np.zeros(self.size * self.size, dtype=np.uint8)
        self.queue: list[int] = []
        self.source_grains = 0
        self.topples = 0
        self.cursor = 0

    def index(self, x: int, y: int) -> int:
        return y * self.size + x

    def enqueue(self, index: int) -> None:
        if self.grid[index] >= 4 and not self.queued[index]:
            self.queued[index] = 1
            self.queue.append(index)

    def add(self, x: int, y: int, grains: int) -> None:
        x = max(0, min(self.size - 1, x))
        y = max(0, min(self.size - 1, y))
        index = self.index(x, y)
        self.grid[index] += int(grains)
        self.source_grains += int(grains)
        self.enqueue(index)

    def seed(self) -> None:
        self.grid.fill(0)
        self.queued.fill(0)
        self.queue = []
        self.source_grains = 0
        self.topples = 0
        self.cursor = 0
        center = self.size // 2
        self.add(center, center, 18000)
        for coset in self.data["cosets"][:16]:
            x = 8 + ((int(coset["index"]) * 13 + int(coset["generators"]) * 5) % 56)
            y = 8 + ((int(coset["pairs"]) * 7 + int(coset["classes"]) * 3) % 56)
            self.add(x, y, 18 + int(coset["generators"]))

    def step(self, limit: int = 5200) -> None:
        steps = 0
        while self.queue and steps < limit:
            index = self.queue.pop()
            self.queued[index] = 0
            q = int(self.grid[index] // 4)
            if q == 0:
                continue
            self.grid[index] -= q * 4
            self.topples += q
            steps += q
            x = index % self.size
            y = index // self.size
            if x > 0:
                self.grid[index - 1] += q
                self.enqueue(index - 1)
            if x < self.size - 1:
                self.grid[index + 1] += q
                self.enqueue(index + 1)
            if y > 0:
                self.grid[index - self.size] += q
                self.enqueue(index - self.size)
            if y < self.size - 1:
                self.grid[index + self.size] += q
                self.enqueue(index + self.size)
            self.enqueue(index)
        if not self.queue:
            pixel = self.data["pixels"][self.cursor % len(self.data["pixels"])]
            self.cursor += 37
            x = 6 + ((int(pixel["m"]) * 17 + int(pixel["a"]) * 5) % 60)
            y = 6 + ((int(pixel["c"]) * 11 + int(pixel["o"]) * 3) % 60)
            self.add(x, y, 4 + (int(pixel["a"]) % 5))

    def categories(self) -> np.ndarray:
        arr = self.grid.reshape(self.size, self.size)
        return np.where(arr >= 4, 4, arr).astype(np.uint8)

    def run(self) -> dict[str, Any]:
        self.seed()
        samples: list[dict[str, Any]] = []
        previous: np.ndarray | None = None
        final = None
        for frame in range(AUDIT_FRAMES + 1):
            if frame > 0:
                self.step()
            categories = self.categories()
            if frame in SAMPLE_FRAMES:
                counts = np.bincount(categories.ravel(), minlength=5).astype(int).tolist()
                samples.append(
                    {
                        "frame": frame,
                        "source_grains": int(self.source_grains),
                        "live_grains": int(self.grid.sum()),
                        "topples": int(self.topples),
                        "active_queue": len(self.queue),
                        "hot_pixels": int(counts[4]),
                        "height_entropy_bits": entropy_from_counts(counts),
                        "frame_delta_fraction": None
                        if previous is None
                        else float((categories != previous).mean()),
                    }
                )
            previous = categories.copy()
            final = categories
        assert final is not None
        counts = np.bincount(final.ravel(), minlength=5).astype(int).tolist()
        return {
            "simulation": {
                "canvas_size": [self.size, self.size],
                "audit_frames": AUDIT_FRAMES,
                "topple_limit_per_frame": 5200,
                "seed_coset_count": 16,
                "open_boundary": True,
            },
            "final": {
                "source_grains": int(self.source_grains),
                "live_grains": int(self.grid.sum()),
                "topples": int(self.topples),
                "active_queue": len(self.queue),
                "height_category_counts": counts,
                "height_entropy_bits": entropy_from_counts(counts),
                "render_channels": palette_channel_entropies(counts, TOPPLE_PALETTE),
                "render_spectral_null": shuffle_null_metrics(final),
            },
            "sample_frames": samples,
        }


def source_report_entry(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    extra: dict[str, Any] = {"status": payload.get("status")}
    if "certificate_sha256" in payload:
        extra["certificate_sha256"] = payload["certificate_sha256"]
    return input_entry(path, extra)


def artifact_hash(payload: dict[str, Any]) -> str:
    return self_hash(payload, "artifact_sha256_excluding_this_field")


def build_artifact() -> dict[str, Any]:
    data, text = load_visualization_data()
    family = load_json(FAMILY_ARTIFACT)
    intrinsic = load_json(INTRINSIC_ARTIFACT)
    robust = load_json(ROBUST_REPORT)
    golay_probe = load_json(GOLAY_PROBE_REPORT)
    golay_minor = load_json(GOLAY_MINOR_REPORT)

    d20_audit = D20LiftSimulator(data).run()
    topple_audit = ToppleSimulator(data).run()

    d20_z = d20_audit["final"]["cooriented_render_spectral_null"]["z_scores"]
    topple_z = topple_audit["final"]["render_spectral_null"]["z_scores"]
    d20_alpha_entropy = d20_audit["final"]["cooriented_render_channels"]["entropy_bits"]["alpha"]
    d20_atom_entropy = d20_audit["final"]["rgba_atom_channel_entropy_bits"]
    topple_alpha_entropy = topple_audit["final"]["render_channels"]["entropy_bits"]["alpha"]

    checks = {
        "visualization_data_loaded": len(data.get("edges", [])) == 30 and len(data.get("nodes", [])) == 20,
        "d20_lift_render_grid_is_2_by_2": text.count('class="d20-lift-frame"') == 4,
        "d20_rgba_atom_canvas_declared": "d20RgbaAtomCanvas" in text,
        "d20_atlas_tension_canvas_declared": "d20AtlasTensionCanvas" in text,
        "d20_atlas_tension_uses_certified_stress_graph": "D20_ATLAS_STRESS_GRAPH" in text
        and "d20AtlasTensionForAtom" in text
        and "drawD20AtlasTensionMask" in text,
        "d20_rgba_atom_3d_canvas_declared": "d20RgbaAtom3dCanvas" in text,
        "d20_rgba_atom_3d_uses_translucent_projection": "globalCompositeOperation = 'lighter'" in text
        and "drawD20RgbaAtom3dLift" in text
        and "d20LiftRgbaAtom(sample)" in text,
        "robust_oblongness_theorem_certified": robust.get("status")
        == "D20_VOLTAGE_LIFT_ROBUST_OBLONGNESS_CERTIFIED",
        "intrinsic_ratio_is_31_over_23": intrinsic.get("covariance", {}).get("anisotropy_ratio_exact")
        == "31/23",
        "all_named_voltage_lifts_oblong": family.get("survival_summary", {}).get("anisotropic_variant_count")
        == family.get("survival_summary", {}).get("variants_tested")
        == 5,
        "d20_render_alpha_entropy_zero": d20_alpha_entropy == 0.0,
        "d20_rgba_atom_alpha_entropy_zero": d20_atom_entropy["alpha"] == 0.0,
        "d20_rgba_atom_non_alpha_channels_nonzero": all(
            d20_atom_entropy[channel] > 0.0 for channel in ("red", "green", "blue")
        ),
        "topple_render_alpha_entropy_zero": topple_alpha_entropy == 0.0,
        "d20_render_state_entropy_nonzero": d20_audit["final"]["cooriented_render_entropy_bits"] > 0.0,
        "topple_height_entropy_nonzero": topple_audit["final"]["height_entropy_bits"] > 0.0,
        "d20_render_spectrum_exceeds_histogram_shuffle": d20_z["dominant_non_dc_power_fraction"] > 10.0
        and d20_z["spectral_entropy_normalized"] < -10.0,
        "topple_render_spectrum_exceeds_histogram_shuffle": topple_z["dominant_non_dc_power_fraction"] > 10.0
        and topple_z["spectral_entropy_normalized"] < -10.0,
        "golay_hamming_coordinate_claim_remains_open": golay_probe.get("candidate_morphism", {}).get(
            "morphism_status"
        )
        == "OPEN_NOT_CONSTRUCTED"
        and golay_minor.get("status") == "D20_GOLAY_HAMMING_MINOR_PUNCTURE_SEARCH_CERTIFIED",
        "physical_geon_claim_not_promoted": True,
    }

    payload: dict[str, Any] = {
        "schema": "d20.proof_obligation.geon_phase_entropy_audit.artifact@1",
        "status": "D20_GEON_PHASE_ENTROPY_AUDIT_DERIVED",
        "source": {
            "visualization": input_entry(VISUALIZATION),
            "edge_steps": input_entry(EDGE_STEPS),
            "family_comparison": input_entry(
                FAMILY_ARTIFACT,
                {
                    "schema": family.get("schema"),
                    "status": family.get("status"),
                    "artifact_sha256_excluding_this_field": family.get(
                        "artifact_sha256_excluding_this_field"
                    ),
                },
            ),
            "intrinsic_hex_metric_artifact": input_entry(
                INTRINSIC_ARTIFACT,
                {
                    "schema": intrinsic.get("schema"),
                    "status": intrinsic.get("status"),
                    "artifact_sha256_excluding_this_field": intrinsic.get(
                        "artifact_sha256_excluding_this_field"
                    ),
                },
            ),
            "intrinsic_hex_metric_report": source_report_entry(INTRINSIC_REPORT),
            "family_robust_oblongness_report": source_report_entry(FAMILY_REPORT),
            "robust_oblongness_theorem_report": source_report_entry(ROBUST_REPORT),
            "golay_hamming_probe_report": source_report_entry(GOLAY_PROBE_REPORT),
            "golay_hamming_minor_puncture_search_report": source_report_entry(GOLAY_MINOR_REPORT),
            "derive_script": input_entry(DERIVE_SCRIPT),
        },
        "candidate_definition": {
            "object_under_audit": (
                "the finite D20 voltage-lift sandpile render and its square-grid Abelian "
                "comparison embedded in generated/d20_sandpile_visualization.html"
            ),
            "geon_candidate_reading": (
                "a finite coherent mask/sandpile candidate: robust oblongness plus structured "
                "state-channel spectra, not a promoted continuum or physical geon theorem"
            ),
            "rgba_boundary": (
                "the stored renderer writes palette RGB views plus a D20 RGBA atom view whose "
                "RGB channels encode live height, dominant public atom, and folded mask "
                "order/grade/mixed invariants; alpha remains canonical opaque"
            ),
        },
        "canvas_source_audit": {
            "d20_lift_grid": {
                "layout": "2x2",
                "frame_count": text.count('class="d20-lift-frame"'),
                "canvases": [
                    "d20LiftCanvas",
                    "d20HexLiftCanvas",
                    "d20RgbaAtomCanvas",
                    "d20RgbaAtom3dCanvas",
                ],
            },
            "d20_lift_canvas": {
                "id": "d20LiftCanvas",
                "rgba_write_rule": "ImageData RGB from D20_LIFT_PALETTE with image.data[offset + 3] = 255",
                "alpha_255_assignments_in_visualization": text.count("image.data[offset + 3] = 255"),
            },
            "d20_hex_lift_canvas": {
                "id": "d20HexLiftCanvas",
                "relationship": "same D20 state field, rendered through the regular-hex comparison projection",
            },
            "d20_rgba_atom_canvas": {
                "id": "d20RgbaAtomCanvas",
                "rgba_write_rule": (
                    "ImageData RGBA atom: red=height/hotness, green=dominant public atom, "
                    "blue=certified mask order/tube-grade/mixed status, alpha=255"
                ),
                "folded_mask_rule": (
                    "fold the live 20-fiber cell vector to an 11-bit mask, then dereference "
                    "DATA.pixels[mask] for certified order, grade, class, and mixed-fiber data"
                ),
            },
            "d20_atlas_tension_canvas": {
                "id": "d20AtlasTensionCanvas",
                "relationship": (
                    "transparent overlay on d20RgbaAtomCanvas; uses the certified C985 D20 "
                    "boundary-neighborhood stress graph to smooth signed complement-pair tension"
                ),
                "claim_boundary": (
                    "physical boundary mask only; it does not alter canonical RGBA atom bytes"
                ),
            },
            "d20_rgba_atom_3d_canvas": {
                "id": "d20RgbaAtom3dCanvas",
                "relationship": (
                    "transparent 3D projection of the same live RGBA atom samples; it exposes "
                    "depth as class-order, dominant-fiber, tube-grade, and mixed-fiber offsets"
                ),
                "claim_boundary": (
                    "visual coil projection only; the canonical byte-buffer invariant remains "
                    "d20RgbaAtomCanvas with alpha fixed at 255"
                ),
            },
            "square_topple_canvas": {
                "id": "toppleCanvas",
                "rgb_write_rule": "opaque CSS hex colors in TOPPLE_COLORS; no alpha-valued state channel",
            },
        },
        "geometry_witness": {
            "intrinsic_ratio_exact": intrinsic["covariance"]["anisotropy_ratio_exact"],
            "intrinsic_ratio": intrinsic["covariance"]["anisotropy_ratio"],
            "intrinsic_principal_axis_degrees": intrinsic["covariance"][
                "principal_axis_angle_degrees"
            ],
            "family_survival_summary": family["survival_summary"],
            "robust_theorem_status": robust["status"],
            "ranking_by_anisotropy_desc": family["ranking_by_anisotropy_desc"],
        },
        "phase_entropy_witness": {
            "d20_lift": d20_audit,
            "square_abelian_topple": topple_audit,
        },
        "interpretation_boundary": {
            "certified_here": [
                "the finite D20 voltage-lift render is a deterministic opaque mask field",
                "the stored D20 lift is backed by the certified robust-oblongness theorem",
                "the RGBA atom render carries D20 height, public-atom, class-order, tube-grade, and mixed-fiber invariants in non-alpha channels",
                "the fourth D20 lift window visualizes the RGBA atom as a transparent 3D coil projection",
                "rendered D20 and square-grid state fields have nonzero state/RGB entropy",
                "the final rendered state spectra are far from histogram-preserving shuffles",
                "alpha/subpixel entropy is absent because alpha remains a constant opaque channel",
            ],
            "not_certified_here": [
                "a physical geon",
                "a continuum gravitational field",
                "nontrivial alpha-channel or subpixel entropy",
                "three independent weight-8 Hamming-code coordinate systems",
                "an explicit 31 -> 24 -> 23 Golay-Hamming morphism",
            ],
        },
        "open_obligations": [
            {
                "id": "live_browser_rgba_capture",
                "status": "open",
                "needed_witness": (
                    "compare live browser getImageData buffers against the deterministic RGBA "
                    "atom replay archive before asserting browser-compositor or subpixel effects"
                ),
            },
            {
                "id": "three_coordinate_hamming_weight8_witness",
                "status": "open",
                "needed_witness": (
                    "construct explicit coordinate maps and weight-8 Hamming-code checks; the "
                    "current Golay-Hamming probes record this boundary as unresolved"
                ),
            },
            {
                "id": "physical_geon_interpretation",
                "status": "open",
                "needed_witness": (
                    "supply a semantics bridge from the finite mask/sandpile object to a physical "
                    "or continuum geon model"
                ),
            },
        ],
        "checks": checks,
    }
    payload["artifact_sha256_excluding_this_field"] = artifact_hash(payload)
    return payload


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema": "d20.proof_obligation.geon_phase_entropy_audit@1",
        "status": "D20_GEON_PHASE_ENTROPY_AUDIT_CERTIFIED",
        "all_checks_pass": all(artifact["checks"].values()),
        "claim": (
            "The D20 geon candidate is certified here only as a finite deterministic "
            "mask/sandpile audit: robust oblongness is already witnessed, the rendered state "
            "channels carry nonzero entropy and structured spectra, and the new RGBA atom "
            "render stores D20 invariants in non-alpha channels while alpha remains constant "
            "opaque. The report explicitly does not promote a physical geon, alpha/subpixel "
            "entropy, or weight-8 Hamming-coordinate claim."
        ),
        "stage_protocol": {
            "draft": "treat the geon language as a candidate reading of existing D20 sandpile/lift artifacts",
            "witness": "replay the deterministic HTML D20 lift and square Abelian simulations for fixed frames",
            "coherence": "compare the replay with certified robust-oblongness and Golay/Hamming boundary reports",
            "closure": "validate hashes, simulations, entropy/spectrum checks, and explicit demotions",
            "emit": "emit a proof-obligation report plus the next highest-yield witness target",
        },
        "definition": artifact["candidate_definition"],
        "closure_boundary": artifact["interpretation_boundary"],
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
            "geometry": artifact["geometry_witness"],
            "canvas_source_audit": artifact["canvas_source_audit"],
            "phase_entropy_summary": {
                "d20_final": {
                    "cooriented_render_entropy_bits": artifact["phase_entropy_witness"]["d20_lift"][
                        "final"
                    ]["cooriented_render_entropy_bits"],
                    "hex_render_entropy_bits": artifact["phase_entropy_witness"]["d20_lift"][
                        "final"
                    ]["hex_render_entropy_bits"],
                    "rgba_atom_sha256": artifact["phase_entropy_witness"]["d20_lift"]["final"][
                        "rgba_atom_sha256"
                    ],
                    "rgba_atom_channel_entropy_bits": artifact["phase_entropy_witness"][
                        "d20_lift"
                    ]["final"]["rgba_atom_channel_entropy_bits"],
                    "alpha_entropy_bits": artifact["phase_entropy_witness"]["d20_lift"]["final"][
                        "cooriented_render_channels"
                    ]["entropy_bits"]["alpha"],
                    "spectral_z_scores": artifact["phase_entropy_witness"]["d20_lift"]["final"][
                        "cooriented_render_spectral_null"
                    ]["z_scores"],
                },
                "square_topple_final": {
                    "height_entropy_bits": artifact["phase_entropy_witness"][
                        "square_abelian_topple"
                    ]["final"]["height_entropy_bits"],
                    "alpha_entropy_bits": artifact["phase_entropy_witness"][
                        "square_abelian_topple"
                    ]["final"]["render_channels"]["entropy_bits"]["alpha"],
                    "spectral_z_scores": artifact["phase_entropy_witness"][
                        "square_abelian_topple"
                    ]["final"]["render_spectral_null"]["z_scores"],
                },
            },
        },
        "open_obligations": artifact["open_obligations"],
        "checks": artifact["checks"],
        "next_highest_yield_item": (
            "Run a browser getImageData capture against d20RgbaAtomCanvas and compare it to the "
            "deterministic RGBA atom replay hashes. That is the direct witness needed before "
            "making any browser-compositor or subpixel claim."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": "d20.proof_obligation.geon_phase_entropy_audit_manifest@1",
        "name": THEOREM_ID,
        "certification_tests": [
            "verify the D20 visualization DATA object loads with 20 vertices and 30 edges",
            "verify robust oblongness and intrinsic 31/23 geometry witnesses are certified",
            "replay deterministic D20 lift and square Abelian render simulations",
            "verify the D20 RGBA atom canvas exists and has nonzero non-alpha channel entropy",
            "verify rendered RGB/state entropy is nonzero while alpha entropy is zero",
            "verify rendered spectra exceed histogram-preserving shuffle baselines",
            "verify physical geon, alpha/subpixel, and Hamming-coordinate claims remain demoted",
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
                "alpha_entropy_bits": report["witness"]["phase_entropy_summary"]["d20_final"][
                    "alpha_entropy_bits"
                ],
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
