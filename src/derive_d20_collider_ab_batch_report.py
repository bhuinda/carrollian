from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_collider_ab_batch_report"
ARTIFACT_PATH = GENERATED / f"{THEOREM_ID}.json"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

STRESS_GRAPH_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_boundary_neighborhood_stress_graph"
STRESS_GRAPH_ARTIFACT = STRESS_GRAPH_DIR / "artifact.json"
STRESS_GRAPH_REPORT = STRESS_GRAPH_DIR / "report.json"
VISUALIZATION = GENERATED / "d20_sandpile_visualization.html"
DERIVE_SCRIPT = ROOT / "src" / "derive_d20_collider_ab_batch_report.py"
VALIDATOR = ROOT / "src" / "certify_d20_collider_ab_batch_report.py"

D20_FIBERS = 20
CANVAS_W = 360.0
CANVAS_H = 160.0
PARTICLE_COUNT = 20
BATCH_SHOTS = 8
BATCH_STEPS = 160
GUN_SPEED = 2.05
DAMPING = 0.993
FIELD_W = 90
FIELD_H = 40
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


def clamp_unit(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def shuffled_index(index: int) -> int:
    return (index * SHUFFLE_MULTIPLIER + SHUFFLE_OFFSET) % D20_FIBERS


def graph_rows(stress_artifact: dict[str, Any]) -> list[dict[str, Any]]:
    rows = stress_artifact.get("witness", {}).get("graph_rows", [])
    if not isinstance(rows, list) or len(rows) != D20_FIBERS:
        raise ValueError("stress graph artifact does not contain 20 graph rows")
    return rows


def smoothed_tension(atom_id: int, rows: list[dict[str, Any]]) -> float:
    atom = max(0, min(D20_FIBERS - 1, int(atom_id)))
    base = float(rows[atom]["signed_tension"])
    signed = base * 0.45
    norm = 0.45
    for neighbor in rows[atom].get("neighbors", []):
        weight = float(neighbor["weight"])
        signed += weight * float(neighbor["signed_tension"])
        norm += weight
    return signed / norm if norm else base


def collider_tension(atom_id: int, rows: list[dict[str, Any]], null_model: bool) -> tuple[float, float]:
    source = shuffled_index(atom_id) if null_model else atom_id
    signed = smoothed_tension(source, rows)
    return signed, clamp_unit(abs(signed))


@dataclass
class Particle:
    side: int
    atom_id: int
    signed: float
    stress: float
    charge: float
    mass: float
    radius: float
    x: float
    y: float
    vx: float
    vy: float
    ax: float = 0.0
    ay: float = 0.0
    escaped: bool = False


@dataclass
class ColliderState:
    rows: list[dict[str, Any]]
    null_model: bool
    seed: int = 0
    tick: int = 0
    particles: list[Particle] | None = None
    field: np.ndarray | None = None
    scratch: np.ndarray | None = None
    contacts: int = 0
    captures: int = 0
    escapes: int = 0

    def __post_init__(self) -> None:
        if self.particles is None:
            self.particles = []
        if self.field is None:
            self.field = np.zeros((FIELD_H, FIELD_W), dtype=float)
        if self.scratch is None:
            self.scratch = np.zeros((FIELD_H, FIELD_W), dtype=float)

    def clear_field(self) -> None:
        self.field.fill(0.0)
        self.scratch.fill(0.0)

    def reset_stats(self) -> None:
        self.contacts = 0
        self.captures = 0
        self.escapes = 0

    def fire(self) -> None:
        self.tick = 0
        self.particles = []
        self.reset_stats()
        for i in range(PARTICLE_COUNT):
            row = (i - (PARTICLE_COUNT - 1) / 2.0) / PARTICLE_COUNT
            spread = row * CANVAS_H * 0.72
            wobble = math.sin((i + self.seed) * 1.91) * 5.0
            atom_a = (i + self.seed) % D20_FIBERS
            atom_b = (D20_FIBERS - 1 - i + self.seed * 3) % D20_FIBERS
            specs = [
                {
                    "side": -1,
                    "atom": atom_a,
                    "x": 26.0 + (i % 4) * 3.0,
                    "y": CANVAS_H / 2.0 + spread + wobble,
                    "angle": row * 0.28 + math.sin(i * 1.3) * 0.035,
                },
                {
                    "side": 1,
                    "atom": atom_b,
                    "x": CANVAS_W - 26.0 - (i % 4) * 3.0,
                    "y": CANVAS_H / 2.0 - spread - wobble,
                    "angle": math.pi - row * 0.28 + math.cos(i * 1.1) * 0.035,
                },
            ]
            for spec in specs:
                signed, stress = collider_tension(int(spec["atom"]), self.rows, self.null_model)
                polarity = 1.0 if signed >= 0.0 else -1.0
                charge = polarity * (0.22 + 0.78 * stress)
                speed = GUN_SPEED * (0.88 + stress * 0.24)
                angle = float(spec["angle"])
                self.particles.append(
                    Particle(
                        side=int(spec["side"]),
                        atom_id=int(spec["atom"]),
                        signed=signed,
                        stress=stress,
                        charge=charge,
                        mass=1.0 + stress * 1.8,
                        radius=8.0 + stress * 7.5,
                        x=float(spec["x"]),
                        y=max(16.0, min(CANVAS_H - 16.0, float(spec["y"]))),
                        vx=math.cos(angle) * speed,
                        vy=math.sin(angle) * speed,
                    )
                )

    def deposit_field(self, x: float, y: float, amount: float, radius: float) -> None:
        gx = round(x / CANVAS_W * (FIELD_W - 1))
        gy = round(y / CANVAS_H * (FIELD_H - 1))
        gr = max(1, round(radius))
        for yy in range(-gr, gr + 1):
            for xx in range(-gr, gr + 1):
                px = gx + xx
                py = gy + yy
                if px < 0 or py < 0 or px >= FIELD_W or py >= FIELD_H:
                    continue
                falloff = max(0.0, 1.0 - math.hypot(xx, yy) / (gr + 0.5))
                self.field[py, px] = max(-1.5, min(1.5, self.field[py, px] + amount * falloff))

    def sample_field(self, x: float, y: float) -> tuple[float, float, float]:
        gx = max(1, min(FIELD_W - 2, round(x / CANVAS_W * (FIELD_W - 1))))
        gy = max(1, min(FIELD_H - 2, round(y / CANVAS_H * (FIELD_H - 1))))
        value = float(self.field[gy, gx])
        dx = float(self.field[gy, gx + 1] - self.field[gy, gx - 1])
        dy = float(self.field[gy + 1, gx] - self.field[gy - 1, gx])
        return value, dx, dy

    def step_field(self) -> float:
        total = 0.0
        for y in range(FIELD_H):
            for x in range(FIELD_W):
                center = float(self.field[y, x])
                left = float(self.field[y, x - 1]) if x > 0 else center
                right = float(self.field[y, x + 1]) if x < FIELD_W - 1 else center
                up = float(self.field[y - 1, x]) if y > 0 else center
                down = float(self.field[y + 1, x]) if y < FIELD_H - 1 else center
                diffuse = center * 0.78 + (left + right + up + down) * 0.055
                next_value = diffuse * 0.992
                self.scratch[y, x] = 0.0 if abs(next_value) < 0.0004 else next_value
                total += abs(float(self.scratch[y, x]))
        self.field, self.scratch = self.scratch, self.field
        return clamp_unit(total / (FIELD_W * FIELD_H * 0.18))

    def field_memory(self) -> float:
        return clamp_unit(float(np.abs(self.field).sum()) / (FIELD_W * FIELD_H * 0.18))

    def clump_score(self) -> float:
        if not self.particles:
            return 0.0
        weights = [1.0 + p.stress for p in self.particles]
        mass = sum(weights) or 1.0
        cx = sum(p.x * w for p, w in zip(self.particles, weights)) / mass
        cy = sum(p.y * w for p, w in zip(self.particles, weights)) / mass
        radius = sum(math.hypot(p.x - cx, p.y - cy) * w for p, w in zip(self.particles, weights)) / mass
        return clamp_unit(1.0 - radius / (min(CANVAS_W, CANVAS_H) * 0.52))

    def step_gun(self) -> dict[str, float]:
        self.tick += 1
        overlap = 0.0
        scatter = 0.0
        fusion = 0.0
        coupling = 0.0
        norm = 0.0
        for p in self.particles:
            p.ax = 0.0
            p.ay = (CANVAS_H / 2.0 - p.y) * 0.00018
            _value, dx, dy = self.sample_field(p.x, p.y)
            p.ax += -dx * p.charge * 0.018 - dy * p.stress * 0.006
            p.ay += -dy * p.charge * 0.018 + dx * p.stress * 0.006
        for i, a in enumerate(self.particles):
            for b in self.particles[i + 1 :]:
                dx = b.x - a.x
                dy = b.y - a.y
                dist2 = dx * dx + dy * dy + 36.0
                dist = math.sqrt(dist2)
                nx = dx / dist
                ny = dy / dist
                product = a.charge * b.charge
                stress = 0.20 + (a.stress + b.stress) * 0.55
                reach = math.exp(-max(0.0, dist - 14.0) / 58.0)
                close = clamp_unit(1.0 - max(0.0, dist - (a.radius + b.radius)) / 38.0)
                contact_depth = a.radius + b.radius - dist
                if contact_depth > 0.0:
                    self.contacts += 1
                    total_mass = a.mass + b.mass
                    a_share = b.mass / total_mass
                    b_share = a.mass / total_mass
                    correction = contact_depth * 0.58
                    a.x -= nx * correction * a_share
                    a.y -= ny * correction * a_share
                    b.x += nx * correction * b_share
                    b.y += ny * correction * b_share
                    rel_vx = b.vx - a.vx
                    rel_vy = b.vy - a.vy
                    closing = rel_vx * nx + rel_vy * ny
                    inv_mass = 1.0 / a.mass + 1.0 / b.mass
                    if product >= 0.0:
                        impulse = (
                            max(0.0, -closing) * (1.35 + stress * 0.35) + contact_depth * 0.050
                        ) / inv_mass
                        a.vx -= nx * impulse / a.mass
                        a.vy -= ny * impulse / a.mass
                        b.vx += nx * impulse / b.mass
                        b.vy += ny * impulse / b.mass
                        scatter += contact_depth * stress * 0.040
                    else:
                        capture = clamp_unit(0.10 + close * stress * 0.72)
                        cm_vx = (a.vx * a.mass + b.vx * b.mass) / total_mass
                        cm_vy = (a.vy * a.mass + b.vy * b.mass) / total_mass
                        a.vx = a.vx * (1.0 - capture) + cm_vx * capture
                        a.vy = a.vy * (1.0 - capture) + cm_vy * capture
                        b.vx = b.vx * (1.0 - capture) + cm_vx * capture
                        b.vy = b.vy * (1.0 - capture) + cm_vy * capture
                        if capture > 0.18:
                            self.captures += 1
                        fusion += contact_depth * stress * 0.055
                field = reach * stress * 0.070 / max(0.45, dist2 / 620.0)
                if product >= 0.0:
                    repulse = field * (0.45 + product)
                    a.ax -= nx * repulse / a.mass
                    a.ay -= ny * repulse / a.mass
                    b.ax += nx * repulse / b.mass
                    b.ay += ny * repulse / b.mass
                    scatter += repulse * close * 18.0
                else:
                    attract = field * (0.70 + abs(product) * 1.35)
                    a.ax += nx * attract / a.mass
                    a.ay += ny * attract / a.mass
                    b.ax -= nx * attract / b.mass
                    b.ay -= ny * attract / b.mass
                    fusion += attract * close * 18.0
                bend = (a.charge - b.charge) * reach * stress * 0.018
                a.ax += -ny * bend / a.mass
                a.ay += nx * bend / a.mass
                b.ax += -ny * bend / b.mass
                b.ay += nx * bend / b.mass
                coupling += abs(a.charge - b.charge) * close * stress
                norm += close * stress + 0.0001
                overlap = max(overlap, close)
                if close > 0.018:
                    deposit_sign = 1.0 if product < 0.0 else -1.0
                    shear_bias = max(-0.35, min(0.35, a.charge - b.charge))
                    amount = deposit_sign * close * stress * 0.18 + shear_bias * close * 0.04
                    self.deposit_field((a.x + b.x) * 0.5, (a.y + b.y) * 0.5, amount, 2.0 + close * 7.0)
        kinetic = 0.0
        for p in self.particles:
            p.vx = (p.vx + p.ax) * DAMPING
            p.vy = (p.vy + p.ay) * DAMPING
            p.x += p.vx
            p.y += p.vy
            if p.x < p.radius + 3.0:
                p.x = p.radius + 3.0
                p.vx = abs(p.vx) * 0.74
            if p.x > CANVAS_W - p.radius - 3.0:
                p.x = CANVAS_W - p.radius - 3.0
                p.vx = -abs(p.vx) * 0.74
            if p.y < p.radius + 3.0:
                p.y = p.radius + 3.0
                p.vy = abs(p.vy) * 0.74
            if p.y > CANVAS_H - p.radius - 3.0:
                p.y = CANVAS_H - p.radius - 3.0
                p.vy = -abs(p.vy) * 0.74
            if not p.escaped and self.tick > 48 and (
                (p.side < 0 and p.x > CANVAS_W * 0.66) or (p.side > 0 and p.x < CANVAS_W * 0.34)
            ):
                p.escaped = True
                self.escapes += 1
            kinetic += math.hypot(p.vx, p.vy)
        return {
            "overlap": overlap,
            "scatter": clamp_unit(scatter / (norm * 2.4)) if norm else 0.0,
            "fusion": clamp_unit(fusion / (norm * 2.4)) if norm else 0.0,
            "coupling": clamp_unit(coupling / (norm * 2.8)) if norm else 0.0,
            "kinetic": kinetic,
        }


def run_batch(rows: list[dict[str, Any]], null_model: bool) -> dict[str, Any]:
    state = ColliderState(rows=rows, null_model=null_model)
    per_shot: list[dict[str, Any]] = []
    totals = {"contacts": 0.0, "captures": 0.0, "escapes": 0.0, "residue": 0.0, "clump": 0.0}
    for shot in range(BATCH_SHOTS):
        state.seed = (shot * 7 + 3) % D20_FIBERS
        state.clear_field()
        state.fire()
        last_sample = {"overlap": 0.0, "scatter": 0.0, "fusion": 0.0, "coupling": 0.0, "kinetic": 0.0}
        for _ in range(BATCH_STEPS):
            last_sample = state.step_gun()
            state.step_field()
        residue = state.field_memory()
        clump = state.clump_score()
        row = {
            "shot": shot,
            "seed": state.seed,
            "contacts": state.contacts,
            "captures": state.captures,
            "escapes": state.escapes,
            "residue": residue,
            "clump": clump,
            "final_overlap": last_sample["overlap"],
            "final_scatter": last_sample["scatter"],
            "final_fusion": last_sample["fusion"],
            "final_coupling": last_sample["coupling"],
        }
        per_shot.append(row)
        totals["contacts"] += state.contacts
        totals["captures"] += state.captures
        totals["escapes"] += state.escapes
        totals["residue"] += residue
        totals["clump"] += clump
    averages = {key: value / BATCH_SHOTS for key, value in totals.items()}
    return {"averages": averages, "shots": per_shot}


def verdict_from_deltas(deltas: dict[str, float]) -> str:
    if deltas["captures"] > 10.0 and deltas["clump"] > 0.04:
        return "REAL_CLUMPS"
    if deltas["captures"] > 0.0 and deltas["residue"] > 0.03:
        return "REAL_BIAS"
    if deltas["captures"] < -10.0 or deltas["clump"] < -0.04:
        return "NULL_WINS"
    return "NULL_LIKE"


def build_artifact() -> dict[str, Any]:
    stress_artifact = load_json(STRESS_GRAPH_ARTIFACT)
    stress_report = load_json(STRESS_GRAPH_REPORT)
    visualization_text = VISUALIZATION.read_text(encoding="utf-8")
    rows = graph_rows(stress_artifact)
    real = run_batch(rows, False)
    null = run_batch(rows, True)
    deltas = {
        key: float(real["averages"][key] - null["averages"][key])
        for key in ("contacts", "captures", "escapes", "residue", "clump")
    }
    verdict = verdict_from_deltas(deltas)
    null_permutation = [shuffled_index(i) for i in range(D20_FIBERS)]
    checks = {
        "stress_graph_certified": stress_artifact.get("status")
        == "C985_D20_BOUNDARY_NEIGHBORHOOD_STRESS_GRAPH_CERTIFIED"
        and stress_report.get("status") == "C985_D20_BOUNDARY_NEIGHBORHOOD_STRESS_GRAPH_CERTIFIED",
        "renderer_embeds_collider_batch_harness": "runD20ColliderBatchAB" in visualization_text
        and "d20ColliderBatch" in visualization_text,
        "null_assignment_is_permutation": sorted(null_permutation) == list(range(D20_FIBERS)),
        "shot_count_matches_renderer": len(real["shots"]) == len(null["shots"]) == BATCH_SHOTS,
        "contact_activity_observed": real["averages"]["contacts"] > 0.0 and null["averages"]["contacts"] > 0.0,
        "capture_activity_observed": real["averages"]["captures"] > 0.0 or null["averages"]["captures"] > 0.0,
        "finite_batch_values": all(
            math.isfinite(float(value))
            for group in (real["averages"], null["averages"], deltas)
            for value in group.values()
        ),
        "residue_values_in_unit_interval": 0.0 <= real["averages"]["residue"] <= 1.0
        and 0.0 <= null["averages"]["residue"] <= 1.0,
        "clump_values_in_unit_interval": 0.0 <= real["averages"]["clump"] <= 1.0
        and 0.0 <= null["averages"]["clump"] <= 1.0,
    }
    payload: dict[str, Any] = {
        "schema": "d20.collider_ab_batch_report.artifact@1",
        "status": "D20_COLLIDER_AB_BATCH_REPORT_DERIVED",
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
            "object": "fixed-seed D20 RGBA-horizon collider A/B batch",
            "real_mode": "projectiles use each atom's certified graph-smoothed atlas tension",
            "null_mode": "same simulator with deterministic atom-to-tension shuffle i -> (7*i + 11) mod 20",
            "measured_quantities": [
                "hard contacts",
                "capture contacts",
                "escapes",
                "signed residue memory",
                "final clump compactness",
            ],
            "claim_boundary": (
                "certifies this finite collider simulator's real-vs-null statistics only; "
                "it does not certify literal electromagnetic, particle, or gravitational physics"
            ),
        },
        "parameters": {
            "batch_shots": BATCH_SHOTS,
            "batch_steps": BATCH_STEPS,
            "particle_count_per_side": PARTICLE_COUNT,
            "gun_speed": GUN_SPEED,
            "damping": DAMPING,
            "field_shape": [FIELD_H, FIELD_W],
            "null_shuffle": {"multiplier": SHUFFLE_MULTIPLIER, "offset": SHUFFLE_OFFSET},
        },
        "witness": {
            "real": real,
            "null": null,
            "deltas_real_minus_null": deltas,
            "verdict": verdict,
        },
        "checks": checks,
    }
    payload["artifact_sha256_excluding_this_field"] = self_hash(
        payload, "artifact_sha256_excluding_this_field"
    )
    return payload


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    witness = artifact["witness"]
    deltas = witness["deltas_real_minus_null"]
    report = {
        "schema": "d20.collider_ab_batch_report@1",
        "status": "D20_COLLIDER_AB_BATCH_REPORT_CERTIFIED",
        "all_checks_pass": all(artifact["checks"].values()),
        "claim": (
            "The renderer's D20 RGBA-horizon collider can be replayed as a deterministic A/B "
            "batch comparing certified atlas polarity assignment against a shuffled null. "
            "The report records whether contact, capture, residue, and clump metrics differ."
        ),
        "stage_protocol": {
            "draft": "treat collider clumping as a real-vs-null finite-simulator question",
            "witness": "run matched fixed-seed real and null collider batches",
            "coherence": "verify certified stress graph input, null permutation, finite values, and active contacts",
            "closure": "emit real-minus-null deltas without promoting physical-particle claims",
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
            "real_averages": witness["real"]["averages"],
            "null_averages": witness["null"]["averages"],
            "deltas_real_minus_null": deltas,
            "verdict": witness["verdict"],
            "sample_real_shots": witness["real"]["shots"][:3],
            "sample_null_shots": witness["null"]["shots"][:3],
        },
        "checks": artifact["checks"],
        "interpretation": {
            "captures_delta": deltas["captures"],
            "residue_delta": deltas["residue"],
            "clump_delta": deltas["clump"],
            "support_status": witness["verdict"],
        },
        "closure_boundary": {
            "certifies": [
                "matched fixed-seed collider A/B replay",
                "real-vs-null capture, contact, escape, residue, and clump metrics",
                "deterministic null-shuffle comparison against certified atlas stress input",
            ],
            "does_not_certify": [
                "literal particle collisions",
                "magnetic control",
                "physical black-hole or gravitational dynamics",
                "browser compositor pixel output",
            ],
        },
        "next_highest_yield_item": (
            "Run a parameter sweep over damping, attraction strength, and residue feedback to "
            "separate robust atlas effects from simulator-tuned clumping."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest = {
        "schema": "d20.collider_ab_batch_report_manifest@1",
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
    deltas = artifact["witness"]["deltas_real_minus_null"]
    print(
        json.dumps(
            {
                "artifact": relpath(ARTIFACT_PATH),
                "report": relpath(OUT_DIR / "report.json"),
                "report_sha256": report["certificate_sha256"],
                "status": report["status"],
                "verdict": artifact["witness"]["verdict"],
                "captures_delta": deltas["captures"],
                "residue_delta": deltas["residue"],
                "clump_delta": deltas["clump"],
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
