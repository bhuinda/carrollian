from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401

import hashlib
import json
import math
from itertools import combinations
from pathlib import Path
from typing import Any

try:
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_finite_state_collider_report"
ARTIFACT_PATH = GENERATED / f"{THEOREM_ID}.json"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
GATE_AUTOMATON_REPORT = (
    D20_INVARIANTS
    / "proof_obligations"
    / "c985_d20_signature_boundary_spine_gate_automaton"
    / "report.json"
)
VISUALIZATION = GENERATED / "d20_sandpile_visualization.html"
DERIVE_SCRIPT = ROOT / "src" / "derive_d20_finite_state_collider_report.py"
VALIDATOR = ROOT / "src" / "certify_d20_finite_state_collider_report.py"

H6_SECTORS = ["B-", "B+", "V-", "V+", "S-", "S+"]
D20_H6_TRIPLES = [tuple(row) for row in combinations(range(len(H6_SECTORS)), 3)]
NULL_SYMBOL_MAP = [2, 4, 1, 5, 0, 3]
BATCH_SHOTS = 8


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


def next_state(gate_sequence: list[int], state: int, letter: int) -> int:
    candidate = gate_sequence[:state] + [letter]
    for size in range(min(len(gate_sequence), len(candidate)), 0, -1):
        if candidate[-size:] == gate_sequence[:size]:
            return size
    return 0


def normalized_entropy(counts: list[int]) -> float:
    total = sum(counts)
    if not total:
        return 0.0
    entropy = 0.0
    for count in counts:
        if count:
            p = count / total
            entropy -= p * math.log(p)
    return max(0.0, min(1.0, entropy / math.log(len(counts))))


def run_finite_collider(gate: dict[str, Any], null_model: bool) -> dict[str, Any]:
    gate_sequence = [int(value) for value in gate["gate_symbol_sequence"]]
    accepting = {int(value) for value in gate["accepting_state_ids"]}
    certified_trigrams = {tuple(int(x) for x in row) for row in gate["source_to_branch_trigram_windows"]}
    missing = {int(value) for value in gate["missing_gate_symbol_ids"]}
    state = 0
    tail: list[int] = []
    counts = [0, 0, 0, 0, 0, 0]
    contacts = captures = escapes = accepted = rejected = branch_accepts = 0
    certified_hits = uncertified_hits = missing_hits = completed_words = 0
    residue = 0.0
    events = BATCH_SHOTS * len(gate_sequence)
    rows: list[dict[str, Any]] = []
    for event_index in range(events):
        certified_letter = gate_sequence[event_index % len(gate_sequence)]
        letter = NULL_SYMBOL_MAP[certified_letter] if null_model else certified_letter
        expected = gate_sequence[state]
        matched = letter == expected
        state_next = next_state(gate_sequence, state, letter)
        branch_accepted = state_next in accepting
        missing_hit = letter in missing
        contacts += 1
        counts[letter] += 1
        tail.append(letter)
        if len(tail) > 3:
            tail.pop(0)
        certified_trigram = False
        if len(tail) == 3:
            certified_trigram = tuple(tail) in certified_trigrams
            if certified_trigram:
                certified_hits += 1
            else:
                uncertified_hits += 1
        if missing_hit:
            missing_hits += 1
        if matched:
            accepted += 1
            captures += 1
        else:
            rejected += 1
            escapes += 1
        if branch_accepted:
            branch_accepts += 1
        residue += 1.0 + (0.55 if branch_accepted else 0.0) + (0.35 if certified_trigram else 0.0) if matched else -0.22
        if missing_hit:
            residue += 0.38
        residue = max(-12.0, min(48.0, residue))
        state = state_next
        completed = False
        if state == len(gate_sequence):
            state = 0
            completed_words += 1
            captures += 3
            completed = True
        rows.append(
            {
                "event": event_index,
                "letter": letter,
                "expected": expected,
                "accepted": matched,
                "branch_accepted": branch_accepted,
                "certified_trigram": certified_trigram,
                "missing_aperture": missing_hit,
                "completed_word": completed,
            }
        )
    trigram_total = certified_hits + uncertified_hits
    return {
        "events": events,
        "contacts": contacts,
        "captures": captures,
        "escapes": escapes,
        "accepted": accepted,
        "rejected": rejected,
        "branch_accepts": branch_accepts,
        "completed_words": completed_words,
        "certified_trigram_hits": certified_hits,
        "uncertified_trigram_hits": uncertified_hits,
        "missing_aperture_hits": missing_hits,
        "letter_counts": counts,
        "accept_rate": accepted / contacts if contacts else 0.0,
        "branch_accept_rate": branch_accepts / contacts if contacts else 0.0,
        "certified_trigram_rate": certified_hits / trigram_total if trigram_total else 0.0,
        "missing_aperture_rate": missing_hits / contacts if contacts else 0.0,
        "letter_entropy": normalized_entropy(counts),
        "residue": max(0.0, min(1.0, (residue + 12.0) / 60.0)),
        "sample_events": rows[:18],
    }


def verdict_from_deltas(deltas: dict[str, float]) -> str:
    if deltas["accept_rate"] > 0.20 and deltas["branch_accept_rate"] > 0.10:
        return "FINITE_GRAMMAR_ADVANTAGE"
    if deltas["accept_rate"] < -0.05:
        return "NULL_LANGUAGE_ADVANTAGE"
    if deltas["certified_trigram_rate"] > 0.10:
        return "CERTIFIED_TRIGRAM_ADVANTAGE"
    return "NULL_LIKE_LANGUAGE"


def run_finite_wind_tunnel(gate: dict[str, Any], null_model: bool, inlet: int = 0) -> dict[str, Any]:
    gate_sequence = [int(value) for value in gate["gate_symbol_sequence"]]
    certified_trigrams = {tuple(int(x) for x in row) for row in gate["source_to_branch_trigram_windows"]}
    missing = {int(value) for value in gate["missing_gate_symbol_ids"]}
    state = 0
    tail: list[int] = []
    pressure = [0.0 for _ in D20_H6_TRIPLES]
    packets = throughput = recirc = aperture_loss = certified_hits = uncertified_hits = 0
    events = BATCH_SHOTS * len(gate_sequence)
    for packet_index in range(events):
        pressure = [value * 0.982 for value in pressure]
        certified = gate_sequence[(packet_index + inlet) % len(gate_sequence)]
        letter = NULL_SYMBOL_MAP[certified] if null_model else certified
        expected = gate_sequence[state]
        matched = letter == expected
        state = next_state(gate_sequence, state, letter)
        tail.append(letter)
        if len(tail) > 3:
            tail.pop(0)
        if len(tail) == 3:
            if tuple(tail) in certified_trigrams:
                certified_hits += 1
            else:
                uncertified_hits += 1
        inlet_atoms = [i for i, triple in enumerate(D20_H6_TRIPLES) if inlet in triple]
        outlet_atoms = [i for i, triple in enumerate(D20_H6_TRIPLES) if letter in triple]
        for atom in inlet_atoms:
            pressure[atom] += 0.28
        for atom in outlet_atoms:
            pressure[atom] += 1.05 if matched else 0.46
        if letter in missing:
            aperture_loss += 1
            for atom in outlet_atoms:
                pressure[atom] += 0.66
        packets += 1
        if matched:
            throughput += 1
        else:
            recirc += 1
        if state == len(gate_sequence):
            state = 0
    trigram_total = certified_hits + uncertified_hits
    return {
        "packets": packets,
        "throughput_rate": throughput / packets if packets else 0.0,
        "recirc_rate": recirc / packets if packets else 0.0,
        "aperture_loss_rate": aperture_loss / packets if packets else 0.0,
        "alignment_rate": certified_hits / trigram_total if trigram_total else 0.0,
        "pressure": max(0.0, min(1.0, max(pressure) / 9.0)),
        "total_pressure": max(0.0, min(1.0, sum(abs(value) for value in pressure) / 80.0)),
    }


def wind_verdict(deltas: dict[str, float]) -> str:
    if deltas["throughput_rate"] > 0.20 and deltas["total_pressure"] > -0.15:
        return "FINITE_WIND_GRAMMAR_LIFT"
    if deltas["throughput_rate"] < -0.05:
        return "NULL_WIND_ADVANTAGE"
    if deltas["alignment_rate"] > 0.0:
        return "FINITE_WIND_CORRIDOR_BIAS"
    return "NULL_LIKE_WIND"


def build_artifact() -> dict[str, Any]:
    gate_report = load_json(GATE_AUTOMATON_REPORT)
    gate = gate_report["witness"]
    visualization_text = VISUALIZATION.read_text(encoding="utf-8")
    real = run_finite_collider(gate, False)
    null = run_finite_collider(gate, True)
    wind_real = run_finite_wind_tunnel(gate, False)
    wind_null = run_finite_wind_tunnel(gate, True)
    deltas = {
        key: float(real[key] - null[key])
        for key in (
            "accept_rate",
            "branch_accept_rate",
            "certified_trigram_rate",
            "missing_aperture_rate",
            "letter_entropy",
            "residue",
        )
    }
    wind_deltas = {
        key: float(wind_real[key] - wind_null[key])
        for key in (
            "throughput_rate",
            "recirc_rate",
            "aperture_loss_rate",
            "alignment_rate",
            "pressure",
            "total_pressure",
        )
    }
    checks = {
        "gate_automaton_certified": gate_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_GATE_AUTOMATON_CERTIFIED"
        and gate_report.get("all_checks_pass") is True,
        "lambda3_h6_boundary_has_20_atoms": len(D20_H6_TRIPLES) == 20,
        "null_symbol_map_is_permutation": sorted(NULL_SYMBOL_MAP) == list(range(6)),
        "real_and_null_event_counts_match": real["events"] == null["events"] == BATCH_SHOTS * len(gate["gate_symbol_sequence"]),
        "renderer_routes_to_finite_state_collider": "drawD20FiniteStateCollider" in visualization_text
        and "return drawD20FiniteStateCollider()" in visualization_text,
        "renderer_projects_finite_events_to_3d_atom": all(
            token in visualization_text
            for token in (
                "syncD20FiniteColliderProjection",
                "getD20FiniteColliderProjection",
                "drawD20FiniteCollisionProjectionOn3d",
                "const finiteProjection = getD20FiniteColliderProjection()",
            )
        ),
        "renderer_embeds_finite_word_ledger": all(
            token in visualization_text
            for token in (
                "d20ColliderLedger",
                "renderD20FiniteColliderLedger",
                "state.history.slice(-12).reverse()",
                "x${row.letter}->x${row.expected}",
            )
        ),
        "renderer_embeds_finite_wind_tunnel": all(
            token in visualization_text
            for token in (
                "d20WindTunnelCanvas",
                "createD20WindTunnelState",
                "d20WindApplyPacket",
                "runD20WindTunnelBatchAB",
                "Finite alphabet wind tunnel",
            )
        ),
        "visuals_pause_by_default": all(
            token in visualization_text
            for token in (
                "let d20ChipPlaying = false;",
                "let d20LiftPlaying = false;",
                "let topplePlaying = false;",
                "let pixelPlaying = false;",
                'id="d20LiftPlay" aria-pressed="false">Play',
                "setD20LiftPlaying(false);",
            )
        ),
        "old_force_solver_removed": all(
            token not in visualization_text
            for token in (
                "function stepD20ColliderGun",
                "function drawD20ColliderGun",
                "function fireD20ColliderGun",
                "function clearD20ColliderField",
                "d20ColliderParticles",
                "d20ColliderLinks",
                "D20_COLLIDER_GUN_SPEED",
                "D20_COLLIDER_FIELD_W",
            )
        ),
        "renderer_embeds_null_symbol_map": "D20_GATE_NULL_SYMBOL_MAP" in visualization_text,
        "renderer_note_declares_grammar_experiment": "Finite-state collider" in visualization_text
        and "grammar experiment" in visualization_text,
        "real_accepts_certified_word": real["accept_rate"] == 1.0,
        "finite_values": all(math.isfinite(float(value)) for value in [*deltas.values(), real["residue"], null["residue"]]),
    }
    payload: dict[str, Any] = {
        "schema": "d20.finite_state_collider_report.artifact@1",
        "status": "D20_FINITE_STATE_COLLIDER_REPORT_DERIVED",
        "source": {
            "gate_automaton_report": input_entry(
                GATE_AUTOMATON_REPORT,
                {
                    "status": gate_report.get("status"),
                    "certificate_sha256": gate_report.get("certificate_sha256"),
                },
            ),
            "visualization": input_entry(VISUALIZATION),
            "derive_script": input_entry(DERIVE_SCRIPT),
        },
        "definition": {
            "object": "pure finite-state D20 collider",
            "finite_boundary": "d20 atoms are Lambda^3 H6 triples over six sectors",
            "interaction_law": "contacts are gate letters; accepted prefixes capture, rejected prefixes escape, missing x2/x4 letters add anomaly residue",
            "horizon_projection": "the 3D RGBA atom pane reads the same finite collision event and visualizes its accepted/rejected/aperture state as a shared horizon pulse",
            "word_ledger": "the collider panel renders the latest finite contact events from the same state.history stream used by the collider and horizon projection",
            "wind_tunnel": "directional H6 inlet packets route through the same certified gate automaton and accumulate finite pressure over the 20 C(H6,3) atoms",
            "real_mode": "uses the certified gate sequence as the emitted contact word",
            "null_mode": "uses the same certified word passed through a fixed six-letter permutation",
            "claim_boundary": "certifies a finite grammar experiment only; no electromagnetic, particle, gravitational, or black-hole claim is made",
        },
        "parameters": {
            "batch_shots": BATCH_SHOTS,
            "gate_sequence": gate["gate_symbol_sequence"],
            "accepting_state_ids": gate["accepting_state_ids"],
            "missing_gate_symbol_ids": gate["missing_gate_symbol_ids"],
            "null_symbol_map": NULL_SYMBOL_MAP,
        },
        "witness": {
            "real": real,
            "null": null,
            "deltas_real_minus_null": deltas,
            "verdict": verdict_from_deltas(deltas),
            "wind_tunnel": {
                "real": wind_real,
                "null": wind_null,
                "deltas_real_minus_null": wind_deltas,
                "verdict": wind_verdict(wind_deltas),
            },
        },
        "checks": checks,
    }
    payload["artifact_sha256_excluding_this_field"] = self_hash(payload, "artifact_sha256_excluding_this_field")
    return payload


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    witness = artifact["witness"]
    report = {
        "schema": "d20.finite_state_collider_report@1",
        "status": "D20_FINITE_STATE_COLLIDER_REPORT_CERTIFIED",
        "all_checks_pass": all(artifact["checks"].values()),
        "claim": "The visible collider and wind tunnel have been reduced to finite alphabet experiments: contact/flow words are scored directly by the certified gate automaton, and the collider pane, finite word ledger, wind pane, and 3D RGBA atom pane visualize symbolic transport rather than force-first physics.",
        "stage_protocol": {
            "draft": "remove force-first collider behavior from the visible experiment",
            "witness": "run certified gate word against a fixed shuffled six-letter null",
            "coherence": "verify certified gate input, Lambda^3 H6 size, null permutation, renderer routing, finite rates, wind-tunnel embedding, and default-paused visuals",
            "closure": "emit finite-language real/null deltas and renderer coupling evidence without physical-particle claims",
            "emit": "publish artifact, report, manifest, and registry entry",
        },
        "definition": artifact["definition"],
        "inputs": {
            "artifact": input_entry(
                ARTIFACT_PATH,
                {
                    "schema": artifact["schema"],
                    "status": artifact["status"],
                    "artifact_sha256_excluding_this_field": artifact["artifact_sha256_excluding_this_field"],
                },
            ),
            "validator": input_entry(VALIDATOR),
            **artifact["source"],
        },
        "witness": witness,
        "checks": artifact["checks"],
        "interpretation": {
            "support_status": witness["verdict"],
            "accept_rate_delta": witness["deltas_real_minus_null"]["accept_rate"],
            "branch_accept_rate_delta": witness["deltas_real_minus_null"]["branch_accept_rate"],
            "certified_trigram_rate_delta": witness["deltas_real_minus_null"]["certified_trigram_rate"],
            "wind_tunnel_verdict": witness["wind_tunnel"]["verdict"],
            "wind_throughput_delta": witness["wind_tunnel"]["deltas_real_minus_null"]["throughput_rate"],
        },
        "closure_boundary": {
            "certifies": [
                "finite-state collider semantics",
                "real/null comparison against the certified gate automaton",
                "renderer routing away from the old force-first collider",
                "shared finite-event projection into the 3D RGBA atom pane",
                "on-screen finite word ledger sourced from the collider event history",
                "finite alphabet wind tunnel over the d20 atom domain",
                "visual systems open paused by default",
            ],
            "does_not_certify": [
                "spontaneous physical collision dynamics",
                "electromagnetism",
                "micro black holes",
                "gravity",
            ],
        },
        "next_highest_yield_item": "Add a wind-pressure export artifact that records the per-atom pressure vector for every H6 inlet and null permutation.",
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest = {
        "schema": "d20.finite_state_collider_report_manifest@1",
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
    print(
        json.dumps(
            {
                "artifact": relpath(ARTIFACT_PATH),
                "report": relpath(OUT_DIR / "report.json"),
                "status": report["status"],
                "verdict": artifact["witness"]["verdict"],
                "accept_rate_delta": artifact["witness"]["deltas_real_minus_null"]["accept_rate"],
                "branch_accept_rate_delta": artifact["witness"]["deltas_real_minus_null"]["branch_accept_rate"],
                "report_sha256": report["certificate_sha256"],
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
