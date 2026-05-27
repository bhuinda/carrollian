from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401

import hashlib
import itertools
import json
import math
from itertools import combinations
from pathlib import Path
from typing import Any

try:
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_wind_pressure_export_report"
ARTIFACT_PATH = GENERATED / f"{THEOREM_ID}.json"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
GATE_AUTOMATON_REPORT = (
    D20_INVARIANTS
    / "proof_obligations"
    / "c985_d20_signature_boundary_spine_gate_automaton"
    / "report.json"
)
FINITE_STATE_REPORT = (
    D20_INVARIANTS / "proof_obligations" / "d20_finite_state_collider_report" / "report.json"
)
VISUALIZATION = GENERATED / "d20_sandpile_visualization.html"
DERIVE_SCRIPT = ROOT / "src" / "derive_d20_wind_pressure_export_report.py"
VALIDATOR = ROOT / "src" / "certify_d20_wind_pressure_export_report.py"

H6_SECTORS = ["B-", "B+", "V-", "V+", "S-", "S+"]
D20_H6_TRIPLES = [tuple(row) for row in combinations(range(len(H6_SECTORS)), 3)]
IDENTITY_SYMBOL_MAP = tuple(range(len(H6_SECTORS)))
BATCH_SHOTS = 8
ROUND_DIGITS = 9


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


def rounded(value: float) -> float:
    return round(float(value), ROUND_DIGITS)


def next_state(gate_sequence: list[int], state: int, letter: int) -> int:
    candidate = gate_sequence[:state] + [letter]
    for size in range(min(len(gate_sequence), len(candidate)), 0, -1):
        if candidate[-size:] == gate_sequence[:size]:
            return size
    return 0


def atom_label(atom_id: int) -> dict[str, Any]:
    triple = D20_H6_TRIPLES[atom_id]
    return {
        "atom": atom_id,
        "triple": list(triple),
        "sectors": [H6_SECTORS[index] for index in triple],
    }


def run_wind_tunnel(
    gate_sequence: list[int],
    certified_trigrams: set[tuple[int, int, int]],
    missing_symbols: set[int],
    inlet: int,
    symbol_map: tuple[int, ...],
) -> dict[str, Any]:
    state = 0
    tail: list[int] = []
    pressure = [0.0 for _ in D20_H6_TRIPLES]
    packets = throughput = recirc = aperture_loss = certified_hits = uncertified_hits = branch_accepts = 0
    events = BATCH_SHOTS * len(gate_sequence)
    accepting_states = {1, 3, 5, 8, 12, 14}
    for packet_index in range(events):
        pressure = [value * 0.982 for value in pressure]
        certified = gate_sequence[(packet_index + inlet) % len(gate_sequence)]
        letter = symbol_map[certified]
        expected = gate_sequence[state]
        matched = letter == expected
        state = next_state(gate_sequence, state, letter)
        if state in accepting_states:
            branch_accepts += 1
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
        if letter in missing_symbols:
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
    pressure_vector = [rounded(value) for value in pressure]
    ranked = sorted(range(len(pressure_vector)), key=lambda atom: (-pressure_vector[atom], atom))
    return {
        "packets": packets,
        "throughput_rate": rounded(throughput / packets if packets else 0.0),
        "recirc_rate": rounded(recirc / packets if packets else 0.0),
        "aperture_loss_rate": rounded(aperture_loss / packets if packets else 0.0),
        "branch_accept_rate": rounded(branch_accepts / packets if packets else 0.0),
        "alignment_rate": rounded(certified_hits / trigram_total if trigram_total else 0.0),
        "pressure": rounded(max(0.0, min(1.0, max(pressure_vector) / 9.0 if pressure_vector else 0.0))),
        "total_pressure": rounded(max(0.0, min(1.0, sum(abs(value) for value in pressure_vector) / 80.0))),
        "pressure_vector": pressure_vector,
        "top_atoms": [
            {**atom_label(atom), "pressure": pressure_vector[atom]}
            for atom in ranked[:5]
        ],
    }


def average_vectors(vectors: list[list[float]]) -> list[float]:
    if not vectors:
        return [0.0 for _ in D20_H6_TRIPLES]
    return [
        rounded(sum(vector[index] for vector in vectors) / len(vectors))
        for index in range(len(vectors[0]))
    ]


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {}
    keys = (
        "throughput_rate",
        "recirc_rate",
        "aperture_loss_rate",
        "branch_accept_rate",
        "alignment_rate",
        "pressure",
        "total_pressure",
    )
    summary = {
        key: rounded(sum(float(row[key]) for row in rows) / len(rows))
        for key in keys
    }
    vector = average_vectors([row["pressure_vector"] for row in rows])
    ranked = sorted(range(len(vector)), key=lambda atom: (-vector[atom], atom))
    summary["mean_pressure_vector"] = vector
    summary["top_mean_pressure_atoms"] = [
        {**atom_label(atom), "pressure": vector[atom]}
        for atom in ranked[:8]
    ]
    return summary


def build_artifact() -> dict[str, Any]:
    gate_report = load_json(GATE_AUTOMATON_REPORT)
    finite_state_report = load_json(FINITE_STATE_REPORT)
    visualization_text = VISUALIZATION.read_text(encoding="utf-8")
    gate = gate_report["witness"]
    gate_sequence = [int(value) for value in gate["gate_symbol_sequence"]]
    certified_trigrams = {tuple(int(x) for x in row) for row in gate["source_to_branch_trigram_windows"]}
    missing_symbols = {int(value) for value in gate["missing_gate_symbol_ids"]}
    permutations = list(itertools.permutations(range(len(H6_SECTORS))))
    null_permutations = [perm for perm in permutations if perm != IDENTITY_SYMBOL_MAP]

    identity_rows: list[dict[str, Any]] = []
    null_rows: list[dict[str, Any]] = []
    inlet_summaries: list[dict[str, Any]] = []

    for inlet in range(len(H6_SECTORS)):
        identity_run = run_wind_tunnel(
            gate_sequence, certified_trigrams, missing_symbols, inlet, IDENTITY_SYMBOL_MAP
        )
        identity_row = {
            "inlet": inlet,
            "inlet_sector": H6_SECTORS[inlet],
            "symbol_map": list(IDENTITY_SYMBOL_MAP),
            **identity_run,
        }
        identity_rows.append(identity_row)
        inlet_null_rows: list[dict[str, Any]] = []
        for permutation_index, perm in enumerate(null_permutations):
            run = run_wind_tunnel(gate_sequence, certified_trigrams, missing_symbols, inlet, perm)
            row = {
                "inlet": inlet,
                "inlet_sector": H6_SECTORS[inlet],
                "permutation_index": permutation_index,
                "symbol_map": list(perm),
                **run,
            }
            null_rows.append(row)
            inlet_null_rows.append(row)
        null_summary = summarize_rows(inlet_null_rows)
        inlet_summaries.append(
            {
                "inlet": inlet,
                "inlet_sector": H6_SECTORS[inlet],
                "identity": identity_row,
                "null_mean": null_summary,
                "identity_minus_null_mean": {
                    key: rounded(identity_row[key] - null_summary[key])
                    for key in (
                        "throughput_rate",
                        "recirc_rate",
                        "aperture_loss_rate",
                        "branch_accept_rate",
                        "alignment_rate",
                        "pressure",
                        "total_pressure",
                    )
                },
                "pressure_l1_gap_to_null_mean": rounded(
                    sum(
                        abs(identity_row["pressure_vector"][index] - null_summary["mean_pressure_vector"][index])
                        for index in range(len(D20_H6_TRIPLES))
                    )
                ),
            }
        )

    identity_summary = summarize_rows(identity_rows)
    null_summary = summarize_rows(null_rows)
    deltas = {
        key: rounded(identity_summary[key] - null_summary[key])
        for key in (
            "throughput_rate",
            "recirc_rate",
            "aperture_loss_rate",
            "branch_accept_rate",
            "alignment_rate",
            "pressure",
            "total_pressure",
        )
    }
    checks = {
        "gate_automaton_certified": gate_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_GATE_AUTOMATON_CERTIFIED"
        and gate_report.get("all_checks_pass") is True,
        "finite_state_wind_tunnel_certified": finite_state_report.get("status")
        == "D20_FINITE_STATE_COLLIDER_REPORT_CERTIFIED"
        and finite_state_report.get("all_checks_pass") is True,
        "all_six_inlets_exported": sorted(row["inlet"] for row in identity_rows) == list(range(6))
        and sorted({row["inlet"] for row in null_rows}) == list(range(6)),
        "all_nonidentity_null_permutations_exported": len(null_permutations) == 719
        and len(null_rows) == 6 * 719,
        "identity_rows_exported": len(identity_rows) == 6,
        "pressure_vectors_are_d20_atoms": all(
            len(row["pressure_vector"]) == len(D20_H6_TRIPLES)
            for row in identity_rows + null_rows
        ),
        "finite_values": all(
            math.isfinite(float(value))
            for row in identity_rows + null_rows
            for value in (
                row["throughput_rate"],
                row["recirc_rate"],
                row["aperture_loss_rate"],
                row["branch_accept_rate"],
                row["alignment_rate"],
                row["pressure"],
                row["total_pressure"],
                *row["pressure_vector"],
            )
        ),
        "renderer_embeds_wind_tunnel": "d20WindTunnelCanvas" in visualization_text
        and "runD20WindTunnelBatchAB" in visualization_text,
    }
    payload: dict[str, Any] = {
        "schema": "d20.wind_pressure_export_report.artifact@1",
        "status": "D20_WIND_PRESSURE_EXPORT_REPORT_DERIVED",
        "source": {
            "gate_automaton_report": input_entry(
                GATE_AUTOMATON_REPORT,
                {
                    "status": gate_report.get("status"),
                    "certificate_sha256": gate_report.get("certificate_sha256"),
                },
            ),
            "finite_state_report": input_entry(
                FINITE_STATE_REPORT,
                {
                    "status": finite_state_report.get("status"),
                    "certificate_sha256": finite_state_report.get("certificate_sha256"),
                },
            ),
            "visualization": input_entry(VISUALIZATION),
            "derive_script": input_entry(DERIVE_SCRIPT),
        },
        "definition": {
            "object": "exhaustive finite D20 wind-pressure export",
            "finite_boundary": "20 d20 atoms are C(H6,3) triples over six H6 sectors",
            "real_mode": "identity six-letter alphabet map",
            "null_mode": "all 719 non-identity permutations of the six-letter alphabet",
            "pressure_rule": "inlet atoms receive base pressure; outlet atoms receive accepted/rejected/aperture pressure under the certified gate automaton",
            "claim_boundary": "exports finite symbolic pressure vectors only; does not claim continuum fluid dynamics",
        },
        "parameters": {
            "batch_shots": BATCH_SHOTS,
            "events_per_run": BATCH_SHOTS * len(gate_sequence),
            "gate_sequence": gate_sequence,
            "missing_gate_symbol_ids": sorted(missing_symbols),
            "h6_sectors": H6_SECTORS,
            "identity_symbol_map": list(IDENTITY_SYMBOL_MAP),
            "null_permutation_count": len(null_permutations),
        },
        "witness": {
            "identity_rows": identity_rows,
            "null_rows": null_rows,
            "inlet_summaries": inlet_summaries,
            "identity_summary": identity_summary,
            "null_summary": null_summary,
            "identity_minus_null_mean": deltas,
            "verdict": (
                "FINITE_WIND_PRESSURE_ADVANTAGE"
                if deltas["throughput_rate"] > 0.05 and deltas["alignment_rate"] >= 0.0
                else "NULL_LIKE_WIND_PRESSURE"
            ),
        },
        "checks": checks,
    }
    payload["artifact_sha256_excluding_this_field"] = self_hash(
        payload, "artifact_sha256_excluding_this_field"
    )
    return payload


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    witness = artifact["witness"]
    report = {
        "schema": "d20.wind_pressure_export_report@1",
        "status": "D20_WIND_PRESSURE_EXPORT_REPORT_CERTIFIED",
        "all_checks_pass": all(artifact["checks"].values()),
        "claim": (
            "The D20 wind tunnel exports a deterministic per-atom pressure vector for every H6 inlet "
            "under the certified identity alphabet and every non-identity six-letter null permutation."
        ),
        "stage_protocol": {
            "draft": "treat wind as finite symbolic transport over C(H6,3) atoms",
            "witness": "simulate all six inlets under identity and all non-identity alphabet permutations",
            "coherence": "verify certified gate input, finite-state renderer support, complete permutation coverage, and finite 20-atom pressure vectors",
            "closure": "emit pressure vectors and summaries without continuum-fluid claims",
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
        "witness_summary": {
            "identity_summary": witness["identity_summary"],
            "null_summary": witness["null_summary"],
            "identity_minus_null_mean": witness["identity_minus_null_mean"],
            "verdict": witness["verdict"],
            "inlet_summaries": [
                {
                    "inlet": row["inlet"],
                    "inlet_sector": row["inlet_sector"],
                    "identity_minus_null_mean": row["identity_minus_null_mean"],
                    "pressure_l1_gap_to_null_mean": row["pressure_l1_gap_to_null_mean"],
                }
                for row in witness["inlet_summaries"]
            ],
        },
        "checks": artifact["checks"],
        "closure_boundary": {
            "certifies": [
                "complete six-inlet identity pressure export",
                "complete six-inlet export across all 719 non-identity six-symbol null permutations",
                "20-atom pressure vector shape for every run",
                "deterministic finite wind-pressure summaries",
            ],
            "does_not_certify": [
                "continuum fluid dynamics",
                "Navier-Stokes behavior",
                "physical aerodynamics",
                "literal mass or force fields",
            ],
        },
        "next_highest_yield_item": (
            "Render the exported six-inlet pressure atlas as a small multiples panel so high-pressure "
            "d20 atoms can be inspected without opening the JSON artifact."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest = {
        "schema": "d20.wind_pressure_export_report_manifest@1",
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
    deltas = artifact["witness"]["identity_minus_null_mean"]
    print(
        json.dumps(
            {
                "artifact": relpath(ARTIFACT_PATH),
                "report": relpath(OUT_DIR / "report.json"),
                "status": report["status"],
                "verdict": artifact["witness"]["verdict"],
                "throughput_delta": deltas["throughput_rate"],
                "alignment_delta": deltas["alignment_rate"],
                "null_rows": len(artifact["witness"]["null_rows"]),
                "report_sha256": report["certificate_sha256"],
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
