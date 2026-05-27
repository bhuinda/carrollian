from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401

import hashlib
import json
import math
from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
    from .derive_d20_collider_ab_batch_report import (
        BATCH_SHOTS,
        BATCH_STEPS,
        CANVAS_H,
        CANVAS_W,
        D20_FIBERS,
        DAMPING,
        FIELD_H,
        FIELD_W,
        GUN_SPEED,
        PARTICLE_COUNT,
        SHUFFLE_MULTIPLIER,
        SHUFFLE_OFFSET,
        Particle,
        clamp_unit,
        collider_tension,
        graph_rows,
        input_entry,
        load_json,
        self_hash,
        sha_file,
        sha_json,
        shuffled_index,
        write_json,
    )
except ImportError:  # Supports direct script execution.
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath
    from derive_d20_collider_ab_batch_report import (
        BATCH_SHOTS,
        BATCH_STEPS,
        CANVAS_H,
        CANVAS_W,
        D20_FIBERS,
        DAMPING,
        FIELD_H,
        FIELD_W,
        GUN_SPEED,
        PARTICLE_COUNT,
        SHUFFLE_MULTIPLIER,
        SHUFFLE_OFFSET,
        Particle,
        clamp_unit,
        collider_tension,
        graph_rows,
        input_entry,
        load_json,
        self_hash,
        sha_file,
        sha_json,
        shuffled_index,
        write_json,
    )


THEOREM_ID = "d20_alphabetic_collider_contact_report"
ARTIFACT_PATH = GENERATED / f"{THEOREM_ID}.json"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

STRESS_GRAPH_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_boundary_neighborhood_stress_graph"
STRESS_GRAPH_ARTIFACT = STRESS_GRAPH_DIR / "artifact.json"
STRESS_GRAPH_REPORT = STRESS_GRAPH_DIR / "report.json"
GATE_AUTOMATON_DIR = (
    D20_INVARIANTS / "proof_obligations" / "c985_d20_signature_boundary_spine_gate_automaton"
)
GATE_AUTOMATON_REPORT = GATE_AUTOMATON_DIR / "report.json"
VISUALIZATION = GENERATED / "d20_sandpile_visualization.html"
DERIVE_SCRIPT = ROOT / "src" / "derive_d20_alphabetic_collider_contact_report.py"
VALIDATOR = ROOT / "src" / "certify_d20_alphabetic_collider_contact_report.py"
BASE_COLLIDER_DERIVE_SCRIPT = ROOT / "src" / "derive_d20_collider_ab_batch_report.py"

H6_SECTORS = ["B-", "B+", "V-", "V+", "S-", "S+"]
D20_H6_TRIPLES = [tuple(row) for row in combinations(range(len(H6_SECTORS)), 3)]


def contact_letter(a: Particle, b: Particle) -> tuple[int | None, str]:
    left = a if a.side <= b.side else b
    right = b if left is a else a
    left_triple = set(D20_H6_TRIPLES[left.atom_id % D20_FIBERS])
    right_triple = set(D20_H6_TRIPLES[right.atom_id % D20_FIBERS])
    common = left_triple & right_triple
    if len(common) != 2:
        return None, "coarse_overlap"
    entered = sorted(right_triple - left_triple)
    if len(entered) != 1:
        return None, "degenerate_exchange"
    return entered[0], "kiss_exchange"


def normalized_entropy(counts: list[int]) -> float:
    total = sum(counts)
    if total <= 0:
        return 0.0
    entropy = 0.0
    for count in counts:
        if count:
            p = count / total
            entropy -= p * math.log(p)
    return clamp_unit(entropy / math.log(len(counts)))


@dataclass
class AlphabetStats:
    gate_sequence: list[int]
    accepting_states: set[int]
    certified_trigrams: set[tuple[int, int, int]]
    missing_symbols: set[int]
    counts: list[int] = field(default_factory=lambda: [0, 0, 0, 0, 0, 0])
    state: int = 0
    tail: list[int] = field(default_factory=list)
    raw_contacts: int = 0
    kiss_contacts: int = 0
    coarse_contacts: int = 0
    matched_letters: int = 0
    rejected_letters: int = 0
    branch_accepts: int = 0
    completed_words: int = 0
    certified_trigram_hits: int = 0
    uncertified_trigram_hits: int = 0
    missing_aperture_hits: int = 0

    def reset(self) -> None:
        self.counts = [0, 0, 0, 0, 0, 0]
        self.state = 0
        self.tail = []
        self.raw_contacts = 0
        self.kiss_contacts = 0
        self.coarse_contacts = 0
        self.matched_letters = 0
        self.rejected_letters = 0
        self.branch_accepts = 0
        self.completed_words = 0
        self.certified_trigram_hits = 0
        self.uncertified_trigram_hits = 0
        self.missing_aperture_hits = 0

    def next_state(self, letter: int) -> int:
        candidate = self.gate_sequence[: self.state] + [letter]
        max_size = min(len(self.gate_sequence), len(candidate))
        for size in range(max_size, 0, -1):
            if candidate[-size:] == self.gate_sequence[:size]:
                return size
        return 0

    def observe(self, a: Particle, b: Particle) -> dict[str, Any]:
        self.raw_contacts += 1
        letter, kind = contact_letter(a, b)
        if letter is None:
            self.coarse_contacts += 1
            return {
                "kiss": False,
                "accepted": False,
                "matched": False,
                "branch_accepted": False,
                "certified_trigram": False,
                "missing": False,
                "letter": None,
            }
        self.kiss_contacts += 1
        self.counts[letter] += 1
        self.tail.append(letter)
        if len(self.tail) > 3:
            self.tail.pop(0)
        certified_trigram = False
        if len(self.tail) == 3:
            triple = tuple(self.tail)
            certified_trigram = triple in self.certified_trigrams
            if certified_trigram:
                self.certified_trigram_hits += 1
            else:
                self.uncertified_trigram_hits += 1
        missing = letter in self.missing_symbols
        if missing:
            self.missing_aperture_hits += 1
        expected = self.gate_sequence[self.state] if self.state < len(self.gate_sequence) else None
        matched = letter == expected
        if matched:
            self.matched_letters += 1
        else:
            self.rejected_letters += 1
        self.state = self.next_state(letter)
        branch_accepted = self.state in self.accepting_states
        if branch_accepted:
            self.branch_accepts += 1
        completed = False
        if self.state == len(self.gate_sequence):
            self.completed_words += 1
            self.state = 0
            completed = True
        return {
            "kiss": True,
            "accepted": matched,
            "matched": matched,
            "branch_accepted": branch_accepted,
            "completed": completed,
            "certified_trigram": certified_trigram,
            "missing": missing,
            "letter": letter,
        }

    def snapshot(self) -> dict[str, Any]:
        letter_total = sum(self.counts)
        return {
            "raw_contacts": self.raw_contacts,
            "kiss_contacts": self.kiss_contacts,
            "coarse_contacts": self.coarse_contacts,
            "matched_letters": self.matched_letters,
            "rejected_letters": self.rejected_letters,
            "branch_accepts": self.branch_accepts,
            "completed_words": self.completed_words,
            "certified_trigram_hits": self.certified_trigram_hits,
            "uncertified_trigram_hits": self.uncertified_trigram_hits,
            "missing_aperture_hits": self.missing_aperture_hits,
            "letter_counts": list(self.counts),
            "final_prefix_state": self.state,
            "letter_entropy": normalized_entropy(self.counts),
            "kiss_rate": self.kiss_contacts / self.raw_contacts if self.raw_contacts else 0.0,
            "match_rate": self.matched_letters / self.kiss_contacts if self.kiss_contacts else 0.0,
            "accept_rate": self.branch_accepts / self.kiss_contacts if self.kiss_contacts else 0.0,
            "certified_trigram_rate": self.certified_trigram_hits
            / max(1, self.certified_trigram_hits + self.uncertified_trigram_hits),
            "missing_aperture_rate": self.missing_aperture_hits / letter_total if letter_total else 0.0,
        }


@dataclass
class AlphabeticColliderState:
    rows: list[dict[str, Any]]
    gate_sequence: list[int]
    accepting_states: set[int]
    certified_trigrams: set[tuple[int, int, int]]
    missing_symbols: set[int]
    null_model: bool
    seed: int = 0
    tick: int = 0
    particles: list[Particle] | None = None
    field: np.ndarray | None = None
    scratch: np.ndarray | None = None
    contacts: int = 0
    captures: int = 0
    escapes: int = 0
    alphabet: AlphabetStats | None = None

    def __post_init__(self) -> None:
        if self.particles is None:
            self.particles = []
        if self.field is None:
            self.field = np.zeros((FIELD_H, FIELD_W), dtype=float)
        if self.scratch is None:
            self.scratch = np.zeros((FIELD_H, FIELD_W), dtype=float)
        if self.alphabet is None:
            self.alphabet = AlphabetStats(
                self.gate_sequence,
                self.accepting_states,
                self.certified_trigrams,
                self.missing_symbols,
            )

    def clear_field(self) -> None:
        self.field.fill(0.0)
        self.scratch.fill(0.0)

    def reset_stats(self) -> None:
        self.contacts = 0
        self.captures = 0
        self.escapes = 0
        assert self.alphabet is not None
        self.alphabet.reset()

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
        assert self.alphabet is not None
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
                alphabet_event: dict[str, Any] | None = None
                if contact_depth > 0.0:
                    self.contacts += 1
                    alphabet_event = self.alphabet.observe(a, b)
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
                        elastic_boost = (
                            0.42
                            if alphabet_event
                            and alphabet_event["kiss"]
                            and not alphabet_event["accepted"]
                            else 0.0
                        )
                        accepted_softening = (
                            0.18 if alphabet_event and alphabet_event["accepted"] else 0.0
                        )
                        impulse = (
                            max(0.0, -closing)
                            * (1.35 + stress * 0.35 + elastic_boost - accepted_softening)
                            + contact_depth * (0.050 + elastic_boost * 0.018)
                        ) / inv_mass
                        a.vx -= nx * impulse / a.mass
                        a.vy -= ny * impulse / a.mass
                        b.vx += nx * impulse / b.mass
                        b.vy += ny * impulse / b.mass
                        scatter += contact_depth * stress * (0.040 + elastic_boost * 0.016)
                    else:
                        gate_capture = (
                            0.20
                            + (0.10 if alphabet_event and alphabet_event["branch_accepted"] else 0.0)
                            + (0.06 if alphabet_event and alphabet_event["certified_trigram"] else 0.0)
                            if alphabet_event and alphabet_event["accepted"]
                            else 0.0
                        )
                        rejection_loss = (
                            0.12
                            if alphabet_event
                            and alphabet_event["kiss"]
                            and not alphabet_event["accepted"]
                            else 0.0
                        )
                        capture = clamp_unit(0.10 + close * stress * 0.72 + gate_capture - rejection_loss)
                        cm_vx = (a.vx * a.mass + b.vx * b.mass) / total_mass
                        cm_vy = (a.vy * a.mass + b.vy * b.mass) / total_mass
                        a.vx = a.vx * (1.0 - capture) + cm_vx * capture
                        a.vy = a.vy * (1.0 - capture) + cm_vy * capture
                        b.vx = b.vx * (1.0 - capture) + cm_vx * capture
                        b.vy = b.vy * (1.0 - capture) + cm_vy * capture
                        if capture > 0.18:
                            self.captures += 1
                        fusion += contact_depth * stress * (0.055 + gate_capture * 0.050)
                field_value = reach * stress * 0.070 / max(0.45, dist2 / 620.0)
                if product >= 0.0:
                    repulse = field_value * (0.45 + product)
                    a.ax -= nx * repulse / a.mass
                    a.ay -= ny * repulse / a.mass
                    b.ax += nx * repulse / b.mass
                    b.ay += ny * repulse / b.mass
                    scatter += repulse * close * 18.0
                else:
                    attract = field_value * (0.70 + abs(product) * 1.35)
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
                    gate_residue = (
                        close
                        * (0.10 + (0.05 if alphabet_event and alphabet_event["branch_accepted"] else 0.0))
                        if alphabet_event and alphabet_event["accepted"]
                        else 0.0
                    )
                    rejected_residue = (
                        -close * 0.045
                        if alphabet_event
                        and alphabet_event["kiss"]
                        and not alphabet_event["accepted"]
                        else 0.0
                    )
                    aperture_residue = (
                        close * 0.13 if alphabet_event and alphabet_event["missing"] else 0.0
                    )
                    amount = (
                        deposit_sign * close * stress * 0.18
                        + shear_bias * close * 0.04
                        + gate_residue
                        + rejected_residue
                        + aperture_residue
                    )
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


def gate_witness(gate_report: dict[str, Any]) -> dict[str, Any]:
    witness = gate_report.get("witness", {})
    required = [
        "gate_symbol_sequence",
        "accepting_state_ids",
        "source_to_branch_trigram_windows",
        "missing_gate_symbol_ids",
    ]
    for key in required:
        if key not in witness:
            raise ValueError(f"gate automaton witness missing {key}")
    return witness


def run_batch(rows: list[dict[str, Any]], gate: dict[str, Any], null_model: bool) -> dict[str, Any]:
    gate_sequence = [int(value) for value in gate["gate_symbol_sequence"]]
    accepting_states = {int(value) for value in gate["accepting_state_ids"]}
    certified_trigrams = {tuple(int(x) for x in row) for row in gate["source_to_branch_trigram_windows"]}
    missing_symbols = {int(value) for value in gate["missing_gate_symbol_ids"]}
    state = AlphabeticColliderState(
        rows=rows,
        gate_sequence=gate_sequence,
        accepting_states=accepting_states,
        certified_trigrams=certified_trigrams,
        missing_symbols=missing_symbols,
        null_model=null_model,
    )
    per_shot: list[dict[str, Any]] = []
    totals = {
        "contacts": 0.0,
        "captures": 0.0,
        "escapes": 0.0,
        "residue": 0.0,
        "clump": 0.0,
        "kiss_contacts": 0.0,
        "coarse_contacts": 0.0,
        "kiss_rate": 0.0,
        "match_rate": 0.0,
        "accept_rate": 0.0,
        "certified_trigram_rate": 0.0,
        "missing_aperture_rate": 0.0,
        "letter_entropy": 0.0,
    }
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
        alphabet = state.alphabet.snapshot() if state.alphabet else {}
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
            "alphabet": alphabet,
        }
        per_shot.append(row)
        totals["contacts"] += state.contacts
        totals["captures"] += state.captures
        totals["escapes"] += state.escapes
        totals["residue"] += residue
        totals["clump"] += clump
        for key in (
            "kiss_contacts",
            "coarse_contacts",
            "kiss_rate",
            "match_rate",
            "accept_rate",
            "certified_trigram_rate",
            "missing_aperture_rate",
            "letter_entropy",
        ):
            totals[key] += float(alphabet[key])
    averages = {key: value / BATCH_SHOTS for key, value in totals.items()}
    return {"averages": averages, "shots": per_shot}


def verdict_from_deltas(deltas: dict[str, float]) -> str:
    if deltas["accept_rate"] > 0.015 and deltas["certified_trigram_rate"] > 0.015:
        return "REAL_LANGUAGE_ADVANTAGE"
    if deltas["accept_rate"] < -0.015 or deltas["certified_trigram_rate"] < -0.015:
        return "NULL_LANGUAGE_ADVANTAGE"
    if deltas["missing_aperture_rate"] > 0.015:
        return "REAL_APERTURE_HIT"
    if deltas["kiss_rate"] > 0.025 and deltas["match_rate"] > 0.0:
        return "REAL_KISS_BIAS"
    return "NULL_LIKE_LANGUAGE"


def all_finite(values: list[Any]) -> bool:
    return all(math.isfinite(float(value)) for value in values)


def build_artifact() -> dict[str, Any]:
    stress_artifact = load_json(STRESS_GRAPH_ARTIFACT)
    stress_report = load_json(STRESS_GRAPH_REPORT)
    gate_report = load_json(GATE_AUTOMATON_REPORT)
    visualization_text = VISUALIZATION.read_text(encoding="utf-8")
    rows = graph_rows(stress_artifact)
    gate = gate_witness(gate_report)
    real = run_batch(rows, gate, False)
    null = run_batch(rows, gate, True)
    delta_keys = (
        "kiss_rate",
        "match_rate",
        "accept_rate",
        "certified_trigram_rate",
        "missing_aperture_rate",
        "letter_entropy",
    )
    deltas = {
        key: float(real["averages"][key] - null["averages"][key])
        for key in delta_keys
    }
    verdict = verdict_from_deltas(deltas)
    null_permutation = [shuffled_index(i) for i in range(D20_FIBERS)]
    gate_sequence = [int(value) for value in gate["gate_symbol_sequence"]]
    missing_symbols = [int(value) for value in gate["missing_gate_symbol_ids"]]
    checks = {
        "stress_graph_certified": stress_artifact.get("status")
        == "C985_D20_BOUNDARY_NEIGHBORHOOD_STRESS_GRAPH_CERTIFIED"
        and stress_report.get("status") == "C985_D20_BOUNDARY_NEIGHBORHOOD_STRESS_GRAPH_CERTIFIED",
        "gate_automaton_certified": gate_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_GATE_AUTOMATON_CERTIFIED"
        and gate_report.get("all_checks_pass") is True,
        "lambda3_h6_boundary_has_20_atoms": len(D20_H6_TRIPLES) == D20_FIBERS
        and len(set(D20_H6_TRIPLES)) == D20_FIBERS,
        "gate_sequence_has_16_symbols": len(gate_sequence) == 16
        and all(0 <= value < len(H6_SECTORS) for value in gate_sequence),
        "accepting_states_match_six_branches": len(gate["accepting_state_ids"]) == 6,
        "missing_apertures_are_x2_x4": missing_symbols == [2, 4],
        "renderer_embeds_alphabetic_contact_harness": "D20_GATE_SEQUENCE" in visualization_text
        and "observeD20ColliderAlphabetContact" in visualization_text,
        "renderer_embeds_alphabetic_interaction_mask": "gateCapture" in visualization_text
        and "elasticBoost" in visualization_text
        and "gateResidue" in visualization_text,
        "null_assignment_is_permutation": sorted(null_permutation) == list(range(D20_FIBERS)),
        "shot_count_matches_collider_batch": len(real["shots"]) == len(null["shots"]) == BATCH_SHOTS,
        "kiss_activity_observed": real["averages"]["kiss_contacts"] > 0.0
        and null["averages"]["kiss_contacts"] > 0.0,
        "finite_alphabetic_values": all_finite(
            [*real["averages"].values(), *null["averages"].values(), *deltas.values()]
        ),
        "rates_in_unit_interval": all(
            0.0 <= float(side["averages"][key]) <= 1.0
            for side in (real, null)
            for key in (
                "kiss_rate",
                "match_rate",
                "accept_rate",
                "certified_trigram_rate",
                "missing_aperture_rate",
                "letter_entropy",
            )
        ),
    }
    payload: dict[str, Any] = {
        "schema": "d20.alphabetic_collider_contact_report.artifact@1",
        "status": "D20_ALPHABETIC_COLLIDER_CONTACT_REPORT_DERIVED",
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
            "gate_automaton_report": input_entry(
                GATE_AUTOMATON_REPORT,
                {
                    "status": gate_report.get("status"),
                    "certificate_sha256": gate_report.get("certificate_sha256"),
                },
            ),
            "visualization": input_entry(VISUALIZATION),
            "base_collider_derive_script": input_entry(BASE_COLLIDER_DERIVE_SCRIPT),
            "derive_script": input_entry(DERIVE_SCRIPT),
        },
        "definition": {
            "object": "alphabetic D20 RGBA-horizon collider contact replay",
            "finite_boundary": "d20 atoms are modeled as lexicographic Lambda^3 H6 triples over six sectors",
            "h6_sectors": H6_SECTORS,
            "kiss_point_rule": (
                "a hard contact is a typed kiss-point only when two d20 triples share exactly "
                "two H6 sectors; the directed exchanged sector becomes the gate letter"
            ),
            "interaction_mask": (
                "accepted gate-prefix letters add capture and positive residue; rejected kiss-points "
                "increase elastic impulse and subtract residue; missing x2/x4 aperture hits add anomaly residue"
            ),
            "certified_gate_word": gate_sequence,
            "accepting_state_ids": gate["accepting_state_ids"],
            "missing_gate_symbol_ids": missing_symbols,
            "claim_boundary": (
                "certifies finite alphabetic contact statistics for this deterministic collider replay; "
                "it does not certify electromagnetism, real particle scattering, gravity, or black-hole behavior"
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
        "schema": "d20.alphabetic_collider_contact_report@1",
        "status": "D20_ALPHABETIC_COLLIDER_CONTACT_REPORT_CERTIFIED",
        "all_checks_pass": all(artifact["checks"].values()),
        "claim": (
            "The D20 collider can be replayed with a finite alphabetic contact layer: hard contacts "
            "become Lambda^3 H6 kiss-point exchanges when they differ by one H6 sector, and those "
            "letters are scored against the certified gate automaton while accepted/rejected letters "
            "also mask capture, elasticity, and residue."
        ),
        "stage_protocol": {
            "draft": "replace unconstrained collision metaphors with finite typed contact words",
            "witness": "run matched real/null collider batches and letterize every clean kiss-point contact",
            "coherence": "verify certified stress graph, certified gate automaton, Lambda^3 H6 shape, finite rates, and null permutation",
            "closure": "emit real-minus-null alphabetic contact deltas and masked-interaction behavior without promoting physical-particle claims",
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
            "kiss_rate_delta": deltas["kiss_rate"],
            "match_rate_delta": deltas["match_rate"],
            "accept_rate_delta": deltas["accept_rate"],
            "certified_trigram_rate_delta": deltas["certified_trigram_rate"],
            "missing_aperture_rate_delta": deltas["missing_aperture_rate"],
            "support_status": witness["verdict"],
        },
        "closure_boundary": {
            "certifies": [
                "finite Lambda^3 H6 letterization of collider contacts",
                "matched real-vs-null alphabetic contact replay",
                "gate-word acceptance, trigram certification, missing-aperture, and entropy deltas",
            ],
            "does_not_certify": [
                "literal electron paths",
                "magnetic fields",
                "micro black holes",
                "general relativistic horizons",
                "arbitrary-word confluence beyond the certified gate automaton",
            ],
        },
        "next_highest_yield_item": (
            "Sweep gate-mask strengths and compare real/null acceptance deltas against the previous observer-only "
            "baseline to separate alphabetic structure from tuned force gains."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest = {
        "schema": "d20.alphabetic_collider_contact_report_manifest@1",
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
                "accept_rate_delta": deltas["accept_rate"],
                "certified_trigram_rate_delta": deltas["certified_trigram_rate"],
                "missing_aperture_rate_delta": deltas["missing_aperture_rate"],
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
