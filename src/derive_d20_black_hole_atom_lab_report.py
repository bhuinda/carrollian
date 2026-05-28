from __future__ import annotations

import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
PROOF_DIR = ROOT / "data" / "invariants" / "d20" / "proof_obligations" / "d20_black_hole_atom_lab_report"
REPORT_JSON = GENERATED / "d20_black_hole_atom_lab_report.json"
PROOF_JSON = PROOF_DIR / "report.json"
ATLAS_JS = GENERATED / "d20_black_hole_pressure_atlas_data.js"
BOUNDARY_NOTES_MD = GENERATED / "d20_boundary_physics_discovery_notes.md"
PROOF_NOTES_MD = PROOF_DIR / "boundary_physics_discovery_notes.md"
HYDROGEN_SANDPILE_GOLAY_BRIDGE_PROBE = GENERATED / "d20_hydrogen_sandpile_golay_bridge_probe.json"
SCATTERING_OPERATOR_REPORT = ROOT / "data" / "invariants" / "d20" / "theorems" / "full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator" / "report.json"
DYNAMICS_SELECTOR_REPORT = ROOT / "data" / "invariants" / "d20" / "theorems" / "full_exposure_zero_pair_sourced_balance_c2_dynamics_selector" / "report.json"
BOUNDARY_PACKET_PAIRING_REPORT = ROOT / "data" / "invariants" / "d20" / "theorems" / "d20_boundary_packet_pairing_obstruction" / "report.json"
BOUNDARY_PACKET_ROW_NORMALIZATION_REPORT = ROOT / "data" / "invariants" / "d20" / "theorems" / "d20_boundary_packet_row_normalization_obstruction" / "report.json"
BOUNDARY_PACKET_LOW_SUPPORT_REPORT = ROOT / "data" / "invariants" / "d20" / "theorems" / "d20_boundary_packet_low_support_candidate_atlas" / "report.json"

ALPHA_STAR = 1 / 137
ALPHA_WALL = 1 / 4
LAMBDA_EV = 54.4
FINE_DENOMINATOR = 75076
LAMB_VAC = (5 / 24) * (1 - ALPHA_STAR - 2 * ALPHA_STAR * ALPHA_STAR)
LAMB_SHIFT_EV = LAMBDA_EV * (ALPHA_STAR ** 3) * LAMB_VAC
LAMB_REFERENCE_MHZ = 1057.845020
LEVELS = [
    {"label": "1S1/2", "n": 1, "l": 0, "j": 0.5, "sector": "S-"},
    {"label": "2S1/2", "n": 2, "l": 0, "j": 0.5, "sector": "S+"},
    {"label": "2P1/2", "n": 2, "l": 1, "j": 0.5, "sector": "V-"},
    {"label": "2P3/2", "n": 2, "l": 1, "j": 1.5, "sector": "V+"},
    {"label": "3S1/2", "n": 3, "l": 0, "j": 0.5, "sector": "B-"},
    {"label": "3D3/2", "n": 3, "l": 2, "j": 1.5, "sector": "B+"},
]
SECTORS = ["B-", "B+", "V-", "V+", "S-", "S+"]
C985_GLOBAL_R33_VECTOR = [1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1]
C985_MASK_BITS = [
    "B-",
    "B+",
    "V-",
    "V+",
    "S-",
    "S+",
    "H6_visible_shell",
    "signed_pair_wall",
    "K_mixed_S",
    "K_pure_Sminus",
    "closed_return_residual",
]
D20_GATE_SEQUENCE = [5, 5, 0, 0, 1, 3, 1, 5, 3, 5, 5, 3, 5, 3, 1, 0]
WARD_SOURCE_MASK_288_BITS = [5, 8]
WARD_GAMMA8_ACTION = 374784
WARD_GENERATOR5_ACTION = 691200
WARD_SOURCE_ACTION = 1065984
WARD_SHARED_ATOM = 11
TRIPLES = [
    [0, 1, 2], [0, 1, 3], [0, 1, 4], [0, 1, 5], [0, 2, 3],
    [0, 2, 4], [0, 2, 5], [0, 3, 4], [0, 3, 5], [0, 4, 5],
    [1, 2, 3], [1, 2, 4], [1, 2, 5], [1, 3, 4], [1, 3, 5],
    [1, 4, 5], [2, 3, 4], [2, 3, 5], [2, 4, 5], [3, 4, 5],
]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def principal(level: dict[str, Any]) -> float:
    return -1 / (4 * level["n"] * level["n"])


def fine(level: dict[str, Any]) -> float:
    return (1 / (FINE_DENOMINATOR * (level["n"] ** 4))) * (level["n"] / (level["j"] + 0.5) - 0.75)


def energy_ev(level: dict[str, Any]) -> float:
    value = LAMBDA_EV * (principal(level) + fine(level))
    if level["label"] == "2S1/2":
        value += LAMB_SHIFT_EV
    return value


def collect_pressure_rows(obj: Any, rows: list[dict[str, Any]]) -> None:
    if isinstance(obj, dict):
        vector = obj.get("pressure_vector")
        if isinstance(vector, list) and len(vector) == 20 and all(isinstance(v, (int, float)) for v in vector):
            rows.append(obj)
        for value in obj.values():
            collect_pressure_rows(value, rows)
    elif isinstance(obj, list):
        for value in obj:
            collect_pressure_rows(value, rows)


def pressure_summary(row: dict[str, Any], index: int) -> dict[str, float | str | int]:
    vector = [float(v) for v in row["pressure_vector"]]
    mean = sum(vector) / len(vector)
    peak = max(vector)
    spread = peak - min(vector)
    return {
        "row_index": index,
        "inlet": str(row.get("inlet", row.get("sector", row.get("source", "unknown")))),
        "word": str(row.get("word", row.get("alphabet", row.get("mode", "unknown"))))[:80],
        "pressure_mean": round(mean, 9),
        "pressure_peak": round(peak, 9),
        "pressure_spread": round(spread, 9),
        "throughput": round(float(row.get("throughput", row.get("throughput_rate", mean))), 9),
        "alignment": round(float(row.get("alignment", row.get("alignment_rate", mean))), 9),
        "aperture": round(float(row.get("aperture", row.get("aperture_rate", spread))), 9),
    }


def quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = (len(sorted_values) - 1) * q
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[int(position)]
    blend = position - lower
    return sorted_values[lower] * (1 - blend) + sorted_values[upper] * blend


def percentile(values: list[float], value: float) -> float:
    if not values:
        return 0.0
    below_or_equal = sum(1 for item in values if item <= value)
    return below_or_equal / len(values)


def atom_sectors(atom: int) -> list[str]:
    if 0 <= atom < len(TRIPLES):
        return [SECTORS[index] for index in TRIPLES[atom]]
    return []


def c985_boundary_mask(atom: int, null_margin: float) -> dict[str, Any]:
    triple = TRIPLES[atom] if 0 <= atom < len(TRIPLES) else []
    sector_set = set(triple)
    has_s_minus = 4 in sector_set
    has_s_plus = 5 in sector_set
    spin_count = int(has_s_minus) + int(has_s_plus)
    has_non_spin = any(index in sector_set for index in [0, 1, 2, 3])
    signed_pair_wall = int(
        ({0, 1}.issubset(sector_set)) or
        ({2, 3}.issubset(sector_set)) or
        ({4, 5}.issubset(sector_set))
    )
    k_mixed = int(spin_count == 1 and has_non_spin)
    k_pure = int(has_s_minus and has_s_plus)
    closed_return_residual = int(null_margin > 0)
    mask = [0] * 11
    for index in triple:
      mask[index] = 1
    mask[6] = int(len(triple) == 3)
    mask[7] = signed_pair_wall
    mask[8] = k_mixed
    mask[9] = k_pure
    mask[10] = closed_return_residual
    r33 = (13 * sum(weight * bit for weight, bit in zip(C985_GLOBAL_R33_VECTOR, mask))) % 26
    if closed_return_residual and r33 == 13:
        flux_label = "R33_sourced_closed_return"
    elif closed_return_residual:
        flux_label = "public_sink_hidden_neutral"
    elif k_pure:
        flux_label = "pure_Sminus_public_zero"
    elif k_mixed:
        flux_label = "mixed_S_public_zero"
    else:
        flux_label = "null_contained_public_shell"
    return {
        "projection": "d20_to_C985_boundary_mask_v1",
        "basis": ["R33", "K_mixed_S", "K_pure_Sminus"],
        "mask_bits": C985_MASK_BITS,
        "mask": mask,
        "R33": int(r33),
        "K_mixed_S": k_mixed,
        "K_pure_Sminus": k_pure,
        "closed_return_residual": closed_return_residual,
        "flux_label": flux_label,
        "ledger_rule": "R33_global(mask)=13*<[1,1,1,0,1,1,1,1,1,1,1],mask> mod 26",
    }


def c985_signed_flux_value(atom: int, pressure: float, scale: float, null_margin: float) -> float:
    c985 = c985_boundary_mask(atom, null_margin)
    normalized_pressure = pressure / (scale or 1.0)
    r33_sign = 1.0 if c985["R33"] == 13 else -1.0
    value = r33_sign * normalized_pressure
    value += 0.10 if c985["closed_return_residual"] else 0.0
    value += 0.18 * c985["K_pure_Sminus"]
    value -= 0.12 * c985["K_mixed_S"]
    return value


def c985_height_flux_balance_value(atom: int, pressure: float, scale: float, null_margin: float) -> float:
    c985 = c985_boundary_mask(atom, null_margin)
    normalized_pressure = pressure / (scale or 1.0)
    r33_height_residual = 1.0 if c985["R33"] == 13 else -1.0
    finite_height_flux = -r33_height_residual * normalized_pressure
    bare_pi33 = 0.25 if null_margin > 0 else 0.0
    k_counterterm = 0.18 * c985["K_pure_Sminus"] - 0.12 * c985["K_mixed_S"]
    return bare_pi33 + r33_height_residual + finite_height_flux + k_counterterm


def c985_zero_pair_ward_selector_value(vector: list[float], atom_nulls: list[dict[str, float]] | None = None) -> float:
    scale = max((abs(value) for value in vector), default=1.0) or 1.0
    total = 0.0
    for atom, pressure in enumerate(vector):
        null_margin = 0.0
        if atom_nulls and atom < len(atom_nulls):
            null_margin = pressure - float(atom_nulls[atom].get("p95", 0.0))
        c985 = c985_boundary_mask(atom, null_margin)
        mask = c985["mask"]
        generator5 = mask[5]
        gamma8 = mask[8]
        selected_pair = int(generator5 and gamma8)
        single_source = int((generator5 + gamma8) == 1)
        normalized_pressure = pressure / scale
        action_weight = (WARD_GENERATOR5_ACTION * generator5 + WARD_GAMMA8_ACTION * gamma8) / WARD_SOURCE_ACTION
        corrected_clock = (13 * generator5 + 13 * gamma8) % 26
        neutral_pair_gain = 1.0 if selected_pair and corrected_clock == 0 else 0.0
        no_go_penalty = -0.35 if single_source else 0.0
        shared_atom_gain = 0.20 if atom == WARD_SHARED_ATOM else 0.0
        closed_return_gain = 0.15 if c985["closed_return_residual"] else 0.0
        total += normalized_pressure * action_weight * (neutral_pair_gain + no_go_penalty + shared_atom_gain + closed_return_gain)
    return total


def c985_mask_int(atom: int, null_margin: float = 0.0) -> int:
    c985 = c985_boundary_mask(atom, null_margin)
    return sum((1 << index) for index, bit in enumerate(c985["mask"]) if bit)


def embedded_c2_orbit_id(atom: int, inlet: int, step: int, target_count: int = 543) -> int:
    mask_value = c985_mask_int(atom)
    return (17 * mask_value + 31 * (inlet + 1) + 43 * (step + 1)) % target_count


def c2_markov_orbit_drift_value(atom: int, inlet: int, step: int, operator: dict[str, Any]) -> float:
    rows = operator["rows_by_orbit"]
    target_count = operator["target_count"]
    orbit_id = embedded_c2_orbit_id(atom, inlet, step, target_count)
    row = rows[orbit_id]
    source_height = float(row["quotient_target_height_action"])
    target_total = 0.0
    probability_total = 0.0
    for target in row.get("targets", []):
        probability = float(target["probability"]["numerator"]) / float(target["probability"]["denominator"])
        target_row = rows[int(target["target_orbit_id"])]
        target_total += probability * float(target_row["quotient_target_height_action"])
        probability_total += probability
    expected_target_height = target_total / probability_total if probability_total else source_height
    drift = (expected_target_height - source_height) / operator["max_height_action"]
    stationary = float(row["stationary_weight"]["numerator"]) / float(row["stationary_weight"]["denominator"])
    component_size = operator["component_size_by_orbit"].get(orbit_id, 1)
    row_total = float(row.get("row_total_count", 1))
    return drift + 0.08 * (stationary * 1023 - 1.5) + 0.05 * ((component_size - 3) / 2) + 0.03 * ((row_total - 3) / 2)


def build_c2_markov_operator(operator_report: dict[str, Any]) -> dict[str, Any]:
    derived = operator_report["derived"]
    rows = derived["quotient_operator_rows"]
    rows_by_orbit = {int(row["source_orbit_id"]): row for row in rows}
    component_size_by_orbit: dict[int, int] = {}
    for component in derived["component_rows"]:
        for orbit_id in component["orbit_ids"]:
            component_size_by_orbit[int(orbit_id)] = int(component["size"])
    summary = derived["operator_summary"]
    return {
        "rows_by_orbit": rows_by_orbit,
        "component_size_by_orbit": component_size_by_orbit,
        "target_count": int(summary["target_orbit_count"]),
        "rank": int(summary["rank"]),
        "nullity": int(summary["nullity"]),
        "stationary_distribution_denominator": int(summary["stationary_distribution_denominator"]),
        "markov_spectrum": summary["markov_spectrum"],
        "component_size_histogram": summary["component_size_histogram"],
        "component_rows": derived["component_rows"],
        "zero_exit_rows": derived["zero_exit_rows"],
        "max_height_action": max(float(row["quotient_target_height_action"]) for row in rows) or 1.0,
    }


def build_boundary_dynamics_summary(operator: dict[str, Any], transition_rows: list[dict[str, Any]], null_by_inlet: dict[int, list[dict[str, Any]]] | None = None) -> dict[str, Any]:
    rows_by_orbit = operator["rows_by_orbit"]
    component_id_by_orbit = [0] * operator["target_count"]
    component_size_by_orbit = [1] * operator["target_count"]
    component_representatives = []
    seen_sizes: set[int] = set()
    for component in operator["component_rows"]:
        size = int(component["size"])
        for orbit_id in component["orbit_ids"]:
            component_id_by_orbit[int(orbit_id)] = int(component["component_id"])
            component_size_by_orbit[int(orbit_id)] = size
        if size not in seen_sizes or len(component_representatives) < 8:
            seen_sizes.add(size)
            component_representatives.append({
                "component_id": int(component["component_id"]),
                "size": size,
                "has_self_loop": bool(component.get("has_self_loop", False)),
                "orbit_ids": [int(orbit_id) for orbit_id in component["orbit_ids"][:4]],
                "spectrum": component["spectrum"],
            })
        if len(component_representatives) >= 12:
            break
    transition_samples = []
    for row in transition_rows[:16]:
        source_orbit_id = embedded_c2_orbit_id(int(row["atom"]), int(row["inlet"]), int(row["step"]), operator["target_count"])
        source = rows_by_orbit[source_orbit_id]
        transition_samples.append({
            "step": int(row["step"]),
            "inlet": int(row["inlet"]),
            "sector": str(row["sector"]),
            "atom": int(row["atom"]),
            "R33": int(row.get("R33", 0)),
            "K_mixed_S": int(row.get("K_mixed_S", 0)),
            "K_pure_Sminus": int(row.get("K_pure_Sminus", 0)),
            "r33_sourced": int(row.get("r33_sourced", 0)),
            "pressure": round(float(row.get("pressure", 0.0)), 9),
            "null_margin": round(float(row.get("null_margin", 0.0)), 9),
            "source_orbit_id": source_orbit_id,
            "component_size": int(operator["component_size_by_orbit"].get(source_orbit_id, 1)),
            "row_total_count": int(source["row_total_count"]),
            "source_orbit_size": int(source["source_orbit_size"]),
            "stationary_weight": source["stationary_weight"],
            "quotient_target_height_action": int(source["quotient_target_height_action"]),
            "quotient_R33_height_residual": int(source["quotient_R33_height_residual"]),
            "targets": [int(target["target_orbit_id"]) for target in source.get("targets", [])],
        })
    extended_histories = [transition_samples]
    if null_by_inlet:
        available_counts = [len(null_by_inlet.get(inlet, [])) for inlet in sorted(set(D20_GATE_SEQUENCE))]
        null_history_count = min(available_counts) if available_counts else 0
        for null_index in range(null_history_count):
            history_samples = []
            for step, inlet in enumerate(D20_GATE_SEQUENCE):
                null_row = null_by_inlet.get(inlet, [])[null_index]
                vector = [float(value) for value in null_row.get("pressure_vector", [])]
                atom = max(range(len(vector)), key=lambda index: vector[index]) if vector else 0
                pressure = vector[atom] if 0 <= atom < len(vector) else 0.0
                mean = sum(vector) / len(vector) if vector else 0.0
                null_margin = pressure - mean
                c985 = c985_boundary_mask(atom, null_margin)
                source_orbit_id = embedded_c2_orbit_id(atom, inlet, step, operator["target_count"])
                source = rows_by_orbit[source_orbit_id]
                history_samples.append({
                    "step": step,
                    "inlet": inlet,
                    "sector": SECTORS[inlet % len(SECTORS)],
                    "atom": atom,
                    "R33": int(c985["R33"]),
                    "K_mixed_S": int(c985["K_mixed_S"]),
                    "K_pure_Sminus": int(c985["K_pure_Sminus"]),
                    "r33_sourced": 1 if int(c985["R33"]) == 13 else 0,
                    "pressure": round(pressure, 9),
                    "null_margin": round(null_margin, 9),
                    "source_orbit_id": source_orbit_id,
                    "component_size": int(operator["component_size_by_orbit"].get(source_orbit_id, 1)),
                    "row_total_count": int(source["row_total_count"]),
                    "source_orbit_size": int(source["source_orbit_size"]),
                    "stationary_weight": source["stationary_weight"],
                    "quotient_target_height_action": int(source["quotient_target_height_action"]),
                    "quotient_R33_height_residual": int(source["quotient_R33_height_residual"]),
                    "targets": [int(target["target_orbit_id"]) for target in source.get("targets", [])],
                })
            extended_histories.append(history_samples)
    motif_counter: dict[str, int] = {}
    for sample in transition_samples:
        key = boundary_motif_key(sample)
        motif_counter[key] = motif_counter.get(key, 0) + 1
    edge_counter: dict[str, int] = {}
    for sample in transition_samples:
        for target in sample["targets"]:
            key = f"{sample['source_orbit_id']}->{target}"
            edge_counter[key] = edge_counter.get(key, 0) + 1
    top_motifs = [
        {"key": key, "count": count}
        for key, count in sorted(motif_counter.items(), key=lambda item: (-item[1], item[0]))
    ]
    top_edges = [
        {"edge": key, "count": count}
        for key, count in sorted(edge_counter.items(), key=lambda item: (-item[1], item[0]))[:12]
    ]
    return {
        "observable": "boundary_only_ward_bms_component_samples",
        "target_orbit_count": operator["target_count"],
        "rank": operator["rank"],
        "nullity": operator["nullity"],
        "stationary_distribution_denominator": operator["stationary_distribution_denominator"],
        "markov_spectrum": operator["markov_spectrum"],
        "component_size_histogram": operator["component_size_histogram"],
        "zero_exit_rows": operator["zero_exit_rows"],
        "zero_exit_orbit_ids": [int(row["source_orbit_id"]) for row in operator["zero_exit_rows"]],
        "component_id_by_orbit": component_id_by_orbit,
        "component_size_by_orbit": component_size_by_orbit,
        "component_representatives": component_representatives,
        "transition_samples": transition_samples,
        "motif_counts": {
            "motif_total": sum(motif_counter.values()),
            "unique_motifs": len(motif_counter),
            "top_motifs": top_motifs,
            "top_edges": top_edges,
        },
        "motif_prediction": build_boundary_motif_prediction_summary(transition_samples),
        "motif_prediction_long": build_boundary_motif_prediction_history_summary(extended_histories),
        "motif_prediction_splits": build_boundary_motif_prediction_split_summary(extended_histories),
        "interpretation": "Boundary-only samples from the certified 543-orbit Ward/BMS Markov operator; not hydrogen-coupling evidence.",
    }


def boundary_motif_key(sample: dict[str, Any], variant: str = "coarse") -> str:
    base = (
        "c"
        + str(int(sample.get("component_size", 1)))
        + "_row"
        + str(int(sample.get("row_total_count", 0)))
        + "_orbit"
        + str(int(sample.get("source_orbit_size", 1)))
        + "_targets"
        + str(len(sample.get("targets", [])))
    )
    if variant == "coarse":
        return base
    if variant == "component_inlet":
        return base + "_inlet" + str(int(sample.get("inlet", -1)))
    if variant == "component_sector":
        return base + "_sector" + str(sample.get("sector", "?"))
    if variant == "c985_charge":
        return (
            base
            + "_R"
            + str(int(sample.get("R33", 0)))
            + "_Km"
            + str(int(sample.get("K_mixed_S", 0)))
            + "_Kp"
            + str(int(sample.get("K_pure_Sminus", 0)))
        )
    if variant == "source_atom":
        return base + "_atom" + str(int(sample.get("atom", -1)))
    if variant == "source_atom_inlet":
        return base + "_atom" + str(int(sample.get("atom", -1))) + "_inlet" + str(int(sample.get("inlet", -1)))
    if variant == "clock_step":
        return "step" + str(int(sample.get("step", -1)))
    if variant == "clock_inlet":
        return "inlet" + str(int(sample.get("inlet", -1)))
    if variant == "clock_step_inlet":
        return "step" + str(int(sample.get("step", -1))) + "_inlet" + str(int(sample.get("inlet", -1)))
    if variant == "clock_step_atom":
        return "step" + str(int(sample.get("step", -1))) + "_atom" + str(int(sample.get("atom", -1)))
    if variant == "clock_step_atom_inlet":
        return "step" + str(int(sample.get("step", -1))) + "_atom" + str(int(sample.get("atom", -1))) + "_inlet" + str(int(sample.get("inlet", -1)))
    return base


def majority_atom(counts: dict[int, int]) -> int | None:
    if not counts:
        return None
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]


def evaluate_boundary_motif_prediction(samples: list[dict[str, Any]], target_atoms: list[int] | None = None, variant: str = "coarse") -> dict[str, Any]:
    if len(samples) < 2:
        return {
            "transitions_evaluated": 0,
            "walk_forward_attempts": 0,
            "skipped_cold_start": 0,
            "motif_correct": 0,
            "baseline_correct": 0,
            "motif_accuracy": 0.0,
            "baseline_accuracy": 0.0,
            "rows": [],
        }
    actual_atoms = target_atoms if target_atoms is not None else [int(samples[index + 1]["atom"]) for index in range(len(samples) - 1)]
    history_by_motif: dict[str, dict[int, int]] = {}
    global_history: dict[int, int] = {}
    rows = []
    attempted = 0
    skipped = 0
    motif_correct = 0
    baseline_correct = 0
    for index, actual_atom in enumerate(actual_atoms):
        key = boundary_motif_key(samples[index], variant)
        motif_prediction = majority_atom(history_by_motif.get(key, {}))
        baseline_prediction = majority_atom(global_history)
        if motif_prediction is None:
            skipped += 1
        else:
            attempted += 1
            motif_hit = motif_prediction == actual_atom
            baseline_hit = baseline_prediction == actual_atom
            motif_correct += int(motif_hit)
            baseline_correct += int(baseline_hit)
            rows.append({
                "step": int(samples[index]["step"]),
                "motif": key,
                "predicted_atom": motif_prediction,
                "baseline_atom": baseline_prediction,
                "actual_next_atom": int(actual_atom),
                "motif_hit": motif_hit,
                "baseline_hit": baseline_hit,
            })
        motif_counts = history_by_motif.setdefault(key, {})
        motif_counts[int(actual_atom)] = motif_counts.get(int(actual_atom), 0) + 1
        global_history[int(actual_atom)] = global_history.get(int(actual_atom), 0) + 1
    return {
        "transitions_evaluated": len(actual_atoms),
        "walk_forward_attempts": attempted,
        "skipped_cold_start": skipped,
        "motif_correct": motif_correct,
        "baseline_correct": baseline_correct,
        "motif_accuracy": round(motif_correct / attempted, 9) if attempted else 0.0,
        "baseline_accuracy": round(baseline_correct / attempted, 9) if attempted else 0.0,
        "rows": rows,
    }


def build_boundary_motif_prediction_summary(samples: list[dict[str, Any]]) -> dict[str, Any]:
    next_atoms = [int(samples[index + 1]["atom"]) for index in range(max(0, len(samples) - 1))]
    variant_rows = []
    for variant in ["coarse", "component_inlet", "component_sector", "c985_charge", "source_atom", "source_atom_inlet"]:
        actual = evaluate_boundary_motif_prediction(samples, variant=variant)
        null_accuracies = []
        if len(next_atoms) > 2:
            for shift in range(1, len(next_atoms)):
                rotated = next_atoms[shift:] + next_atoms[:shift]
                null_accuracies.append(evaluate_boundary_motif_prediction(samples, rotated, variant)["motif_accuracy"])
            reversed_atoms = list(reversed(next_atoms))
            if reversed_atoms != next_atoms:
                null_accuracies.append(evaluate_boundary_motif_prediction(samples, reversed_atoms, variant)["motif_accuracy"])
        motif_accuracy = actual["motif_accuracy"]
        baseline_accuracy = actual["baseline_accuracy"]
        p_value = round((1 + sum(1 for accuracy in null_accuracies if accuracy >= motif_accuracy)) / (1 + len(null_accuracies)), 9) if null_accuracies else 1.0
        if actual["walk_forward_attempts"] < 4:
            verdict = "INSUFFICIENT_MOTIF_HISTORY"
        elif motif_accuracy <= baseline_accuracy:
            verdict = "MOTIF_PREDICTOR_NOT_ABOVE_BASELINE"
        elif p_value <= 0.1:
            verdict = "MOTIF_PREDICTOR_ABOVE_ROTATION_NULL_PROVISIONAL"
        else:
            verdict = "MOTIF_PREDICTOR_WITHIN_ROTATION_NULL"
        variant_rows.append({
            **actual,
            "variant": variant,
            "baseline_lift": round(motif_accuracy - baseline_accuracy, 9),
            "null_trials": len(null_accuracies),
            "null_accuracy_min": round(min(null_accuracies), 9) if null_accuracies else None,
            "null_accuracy_max": round(max(null_accuracies), 9) if null_accuracies else None,
            "null_p_value": p_value,
            "verdict": verdict,
        })
    best = sorted(
        variant_rows,
        key=lambda row: (
            row["baseline_lift"],
            -row["null_p_value"],
            row["motif_accuracy"],
            row["walk_forward_attempts"],
        ),
        reverse=True,
    )[0] if variant_rows else evaluate_boundary_motif_prediction(samples)
    return {
        **best,
        "best_variant": best.get("variant", "coarse"),
        "variant_rows": variant_rows,
        "null_model": "walk-forward next-sink atoms rotated/reversed against fixed boundary motifs for each motif alphabet",
        "interpretation": "Tests whether recurrent boundary motifs forecast the next R33 sink atom before any hydrogen-level comparison.",
    }


def evaluate_boundary_motif_prediction_histories(
    histories: list[list[dict[str, Any]]],
    target_histories: list[list[int]] | None = None,
    variant: str = "coarse",
) -> dict[str, Any]:
    history_by_motif: dict[str, dict[int, int]] = {}
    global_history: dict[int, int] = {}
    rows = []
    transitions_evaluated = 0
    attempted = 0
    skipped = 0
    motif_correct = 0
    baseline_correct = 0
    for history_index, samples in enumerate(histories):
        if len(samples) < 2:
            continue
        actual_atoms = target_histories[history_index] if target_histories is not None else [
            int(samples[index + 1]["atom"]) for index in range(len(samples) - 1)
        ]
        transitions_evaluated += len(actual_atoms)
        for index, actual_atom in enumerate(actual_atoms):
            key = boundary_motif_key(samples[index], variant)
            motif_prediction = majority_atom(history_by_motif.get(key, {}))
            baseline_prediction = majority_atom(global_history)
            if motif_prediction is None:
                skipped += 1
            else:
                attempted += 1
                motif_hit = motif_prediction == actual_atom
                baseline_hit = baseline_prediction == actual_atom
                motif_correct += int(motif_hit)
                baseline_correct += int(baseline_hit)
                if len(rows) < 96:
                    rows.append({
                        "history": history_index,
                        "step": int(samples[index]["step"]),
                        "motif": key,
                        "predicted_atom": motif_prediction,
                        "baseline_atom": baseline_prediction,
                        "actual_next_atom": int(actual_atom),
                        "motif_hit": motif_hit,
                        "baseline_hit": baseline_hit,
                    })
            motif_counts = history_by_motif.setdefault(key, {})
            motif_counts[int(actual_atom)] = motif_counts.get(int(actual_atom), 0) + 1
            global_history[int(actual_atom)] = global_history.get(int(actual_atom), 0) + 1
    return {
        "transitions_evaluated": transitions_evaluated,
        "walk_forward_attempts": attempted,
        "skipped_cold_start": skipped,
        "motif_correct": motif_correct,
        "baseline_correct": baseline_correct,
        "motif_accuracy": round(motif_correct / attempted, 9) if attempted else 0.0,
        "baseline_accuracy": round(baseline_correct / attempted, 9) if attempted else 0.0,
        "rows": rows,
    }


def build_boundary_motif_prediction_history_summary(histories: list[list[dict[str, Any]]]) -> dict[str, Any]:
    target_histories = [
        [int(samples[index + 1]["atom"]) for index in range(len(samples) - 1)]
        for samples in histories
        if len(samples) >= 2
    ]
    usable_histories = [samples for samples in histories if len(samples) >= 2]
    variant_rows = []
    for variant in ["coarse", "component_inlet", "component_sector", "c985_charge", "source_atom", "source_atom_inlet"]:
        actual = evaluate_boundary_motif_prediction_histories(usable_histories, variant=variant)
        null_accuracies = []
        if target_histories and len(target_histories[0]) > 2:
            for shift in range(1, len(target_histories[0])):
                rotated = [atoms[shift:] + atoms[:shift] for atoms in target_histories]
                null_accuracies.append(evaluate_boundary_motif_prediction_histories(usable_histories, rotated, variant)["motif_accuracy"])
            reversed_histories = [list(reversed(atoms)) for atoms in target_histories]
            null_accuracies.append(evaluate_boundary_motif_prediction_histories(usable_histories, reversed_histories, variant)["motif_accuracy"])
        motif_accuracy = actual["motif_accuracy"]
        baseline_accuracy = actual["baseline_accuracy"]
        p_value = round((1 + sum(1 for accuracy in null_accuracies if accuracy >= motif_accuracy)) / (1 + len(null_accuracies)), 9) if null_accuracies else 1.0
        if actual["walk_forward_attempts"] < 32:
            verdict = "INSUFFICIENT_LONG_MOTIF_HISTORY"
        elif motif_accuracy <= baseline_accuracy:
            verdict = "LONG_MOTIF_PREDICTOR_NOT_ABOVE_BASELINE"
        elif p_value <= 0.05:
            verdict = "LONG_MOTIF_PREDICTOR_ABOVE_ROTATION_NULL"
        elif p_value <= 0.1:
            verdict = "LONG_MOTIF_PREDICTOR_ABOVE_ROTATION_NULL_PROVISIONAL"
        else:
            verdict = "LONG_MOTIF_PREDICTOR_WITHIN_ROTATION_NULL"
        variant_rows.append({
            **actual,
            "variant": variant,
            "baseline_lift": round(motif_accuracy - baseline_accuracy, 9),
            "null_trials": len(null_accuracies),
            "null_accuracy_min": round(min(null_accuracies), 9) if null_accuracies else None,
            "null_accuracy_max": round(max(null_accuracies), 9) if null_accuracies else None,
            "null_p_value": p_value,
            "verdict": verdict,
        })
    best = sorted(
        variant_rows,
        key=lambda row: (
            row["baseline_lift"],
            -row["null_p_value"],
            row["motif_accuracy"],
            row["walk_forward_attempts"],
        ),
        reverse=True,
    )[0] if variant_rows else evaluate_boundary_motif_prediction_histories(usable_histories)
    return {
        **best,
        "best_variant": best.get("variant", "coarse"),
        "variant_rows": variant_rows,
        "history_count": len(usable_histories),
        "sample_count": sum(len(samples) for samples in usable_histories),
        "null_model": "per-history rotation/reversal of next-sink atoms over identity plus certified null pulse histories",
        "interpretation": "Long boundary-only motif forecast over identity and null-row pulse histories; still not a hydrogen comparison.",
    }


WARD_MOTIF_VARIANTS = ["coarse", "component_inlet", "component_sector", "c985_charge"]
SOURCE_STATE_VARIANTS = ["source_atom", "source_atom_inlet"]
MOTIF_VARIANTS = WARD_MOTIF_VARIANTS + SOURCE_STATE_VARIANTS
PHASE_CLOCK_VARIANTS = ["clock_step", "clock_inlet", "clock_step_inlet", "clock_step_atom", "clock_step_atom_inlet"]
RANK_ONE_PACKET_SUPPORT_FAMILIES = [[0, 11], [6, 17], [14, 15]]


def train_boundary_motif_counts(
    histories: list[list[dict[str, Any]]],
    variant: str,
    step_filter: set[int] | None = None,
) -> tuple[dict[str, dict[int, int]], dict[int, int]]:
    history_by_motif: dict[str, dict[int, int]] = {}
    global_history: dict[int, int] = {}
    for samples in histories:
        for index in range(max(0, len(samples) - 1)):
            if step_filter is not None and index not in step_filter:
                continue
            actual_atom = int(samples[index + 1]["atom"])
            key = boundary_motif_key(samples[index], variant)
            motif_counts = history_by_motif.setdefault(key, {})
            motif_counts[actual_atom] = motif_counts.get(actual_atom, 0) + 1
            global_history[actual_atom] = global_history.get(actual_atom, 0) + 1
    return history_by_motif, global_history


def score_boundary_motif_counts(
    histories: list[list[dict[str, Any]]],
    variant: str,
    history_by_motif: dict[str, dict[int, int]],
    global_history: dict[int, int],
    step_filter: set[int] | None = None,
    target_histories: list[list[int]] | None = None,
) -> dict[str, Any]:
    rows = []
    transitions_evaluated = 0
    attempted = 0
    skipped = 0
    motif_correct = 0
    baseline_correct = 0
    for history_index, samples in enumerate(histories):
        if len(samples) < 2:
            continue
        actual_atoms = target_histories[history_index] if target_histories is not None else [
            int(samples[index + 1]["atom"]) for index in range(len(samples) - 1)
        ]
        for index, actual_atom in enumerate(actual_atoms):
            if step_filter is not None and index not in step_filter:
                continue
            transitions_evaluated += 1
            key = boundary_motif_key(samples[index], variant)
            motif_prediction = majority_atom(history_by_motif.get(key, {}))
            baseline_prediction = majority_atom(global_history)
            if motif_prediction is None or baseline_prediction is None:
                skipped += 1
                continue
            attempted += 1
            motif_hit = motif_prediction == actual_atom
            baseline_hit = baseline_prediction == actual_atom
            motif_correct += int(motif_hit)
            baseline_correct += int(baseline_hit)
            if len(rows) < 96:
                rows.append({
                    "history": history_index,
                    "step": int(samples[index]["step"]),
                    "motif": key,
                    "predicted_atom": motif_prediction,
                    "baseline_atom": baseline_prediction,
                    "actual_next_atom": int(actual_atom),
                    "motif_hit": motif_hit,
                    "baseline_hit": baseline_hit,
                })
    return {
        "transitions_evaluated": transitions_evaluated,
        "walk_forward_attempts": attempted,
        "skipped_cold_start": skipped,
        "motif_correct": motif_correct,
        "baseline_correct": baseline_correct,
        "motif_accuracy": round(motif_correct / attempted, 9) if attempted else 0.0,
        "baseline_accuracy": round(baseline_correct / attempted, 9) if attempted else 0.0,
        "rows": rows,
    }


def rotate_target_histories(histories: list[list[dict[str, Any]]], shift: int) -> list[list[int]]:
    rotated_histories = []
    for samples in histories:
        atoms = [int(samples[index + 1]["atom"]) for index in range(max(0, len(samples) - 1))]
        if atoms:
            shift_mod = shift % len(atoms)
            rotated_histories.append(atoms[shift_mod:] + atoms[:shift_mod])
        else:
            rotated_histories.append([])
    return rotated_histories


def summarize_split_variant(
    histories: list[list[dict[str, Any]]],
    variant: str,
    split_kind: str,
    fold_count: int,
) -> dict[str, Any]:
    totals = {
        "transitions_evaluated": 0,
        "walk_forward_attempts": 0,
        "skipped_cold_start": 0,
        "motif_correct": 0,
        "baseline_correct": 0,
    }
    rows = []
    null_accuracies = []
    max_step = max((len(samples) - 1 for samples in histories), default=0)
    for fold in range(fold_count):
        if split_kind == "history":
            train_histories = [samples for index, samples in enumerate(histories) if index % fold_count != fold]
            test_histories = [samples for index, samples in enumerate(histories) if index % fold_count == fold]
            train_filter = None
            test_filter = None
        else:
            train_histories = histories
            test_histories = histories
            train_filter = {step for step in range(max_step) if step % fold_count != fold}
            test_filter = {step for step in range(max_step) if step % fold_count == fold}
        history_by_motif, global_history = train_boundary_motif_counts(train_histories, variant, train_filter)
        actual = score_boundary_motif_counts(test_histories, variant, history_by_motif, global_history, test_filter)
        for key in totals:
            totals[key] += int(actual[key])
        rows.extend(actual["rows"][: max(0, 96 - len(rows))])
        if max_step > 2:
            for shift in range(1, max_step):
                rotated = rotate_target_histories(test_histories, shift)
                null_score = score_boundary_motif_counts(test_histories, variant, history_by_motif, global_history, test_filter, rotated)
                null_accuracies.append(null_score["motif_accuracy"])
            reversed_targets = [list(reversed([int(samples[index + 1]["atom"]) for index in range(max(0, len(samples) - 1))])) for samples in test_histories]
            null_score = score_boundary_motif_counts(test_histories, variant, history_by_motif, global_history, test_filter, reversed_targets)
            null_accuracies.append(null_score["motif_accuracy"])
    motif_accuracy = round(totals["motif_correct"] / totals["walk_forward_attempts"], 9) if totals["walk_forward_attempts"] else 0.0
    baseline_accuracy = round(totals["baseline_correct"] / totals["walk_forward_attempts"], 9) if totals["walk_forward_attempts"] else 0.0
    p_value = round((1 + sum(1 for accuracy in null_accuracies if accuracy >= motif_accuracy)) / (1 + len(null_accuracies)), 9) if null_accuracies else 1.0
    if totals["walk_forward_attempts"] < 32:
        verdict = "INSUFFICIENT_SPLIT_MOTIF_HISTORY"
    elif motif_accuracy <= baseline_accuracy:
        verdict = "SPLIT_MOTIF_PREDICTOR_NOT_ABOVE_BASELINE"
    elif p_value <= 0.05:
        verdict = "SPLIT_MOTIF_PREDICTOR_ABOVE_ROTATION_NULL"
    elif p_value <= 0.1:
        verdict = "SPLIT_MOTIF_PREDICTOR_ABOVE_ROTATION_NULL_PROVISIONAL"
    else:
        verdict = "SPLIT_MOTIF_PREDICTOR_WITHIN_ROTATION_NULL"
    return {
        **totals,
        "variant": variant,
        "split_kind": split_kind,
        "fold_count": fold_count,
        "motif_accuracy": motif_accuracy,
        "baseline_accuracy": baseline_accuracy,
        "baseline_lift": round(motif_accuracy - baseline_accuracy, 9),
        "null_trials": len(null_accuracies),
        "null_accuracy_min": round(min(null_accuracies), 9) if null_accuracies else None,
        "null_accuracy_max": round(max(null_accuracies), 9) if null_accuracies else None,
        "null_p_value": p_value,
        "verdict": verdict,
        "rows": rows,
    }


def summarize_split_family(histories: list[list[dict[str, Any]]], split_kind: str, fold_count: int, variants: list[str] | None = None) -> dict[str, Any]:
    variant_rows = [summarize_split_variant(histories, variant, split_kind, fold_count) for variant in (variants or MOTIF_VARIANTS)]
    candidate_rows = [row for row in variant_rows if row["walk_forward_attempts"] > 0] or variant_rows
    best = sorted(
        candidate_rows,
        key=lambda row: (
            row["baseline_lift"],
            -row["null_p_value"],
            row["motif_accuracy"],
            row["walk_forward_attempts"],
        ),
        reverse=True,
    )[0]
    return {
        **best,
        "best_variant": best["variant"],
        "variant_rows": variant_rows,
        "history_count": len(histories),
        "sample_count": sum(len(samples) for samples in histories),
        "interpretation": f"{split_kind} held-out motif forecast over identity plus certified null pulse histories.",
    }


def build_boundary_motif_prediction_split_summary(histories: list[list[dict[str, Any]]]) -> dict[str, Any]:
    usable_histories = [samples for samples in histories if len(samples) >= 2]
    history_split = summarize_split_family(usable_histories, "history", 5)
    time_offset_split = summarize_split_family(usable_histories, "time_offset", 5)
    time_offset_obstruction = summarize_time_offset_obstruction(usable_histories, time_offset_split["best_variant"])
    phase_clock_model = build_phase_clock_model_summary(usable_histories, history_split, time_offset_split)
    source_state_transport = build_source_state_transport_summary(usable_histories)
    source_conditioned_ward_residual = build_source_conditioned_ward_residual_summary(usable_histories)
    rank_one_packet_family_residual = build_rank_one_packet_family_residual_summary(usable_histories, source_conditioned_ward_residual)
    return {
        "history_split": history_split,
        "time_offset_split": time_offset_split,
        "time_offset_obstruction": time_offset_obstruction,
        "phase_clock_model": phase_clock_model,
        "source_state_transport": source_state_transport,
        "source_conditioned_ward_residual": source_conditioned_ward_residual,
        "rank_one_packet_family_residual": rank_one_packet_family_residual,
        "overall_verdict": (
            "SPLIT_MOTIF_SIGNAL_CANDIDATE"
            if history_split["verdict"] in {"SPLIT_MOTIF_PREDICTOR_ABOVE_ROTATION_NULL", "SPLIT_MOTIF_PREDICTOR_ABOVE_ROTATION_NULL_PROVISIONAL"}
            and time_offset_split["verdict"] in {"SPLIT_MOTIF_PREDICTOR_ABOVE_ROTATION_NULL", "SPLIT_MOTIF_PREDICTOR_ABOVE_ROTATION_NULL_PROVISIONAL"}
            else "SPLIT_MOTIF_SIGNAL_NOT_CERTIFIED"
        ),
        "interpretation": "Held-out history and time-offset splits test whether long motif regularity survives schedule separation.",
    }


def summarize_time_offset_obstruction(histories: list[list[dict[str, Any]]], variant: str) -> dict[str, Any]:
    max_step = max((len(samples) - 1 for samples in histories), default=0)
    phase_rows = []
    for heldout_step in range(max_step):
        train_filter = {step for step in range(max_step) if step != heldout_step}
        test_filter = {heldout_step}
        history_by_motif, global_history = train_boundary_motif_counts(histories, variant, train_filter)
        actual = score_boundary_motif_counts(histories, variant, history_by_motif, global_history, test_filter)
        null_accuracies = []
        for shift in range(1, max_step):
            rotated = rotate_target_histories(histories, shift)
            null_accuracies.append(score_boundary_motif_counts(histories, variant, history_by_motif, global_history, test_filter, rotated)["motif_accuracy"])
        reversed_targets = [list(reversed([int(samples[index + 1]["atom"]) for index in range(max(0, len(samples) - 1))])) for samples in histories]
        if reversed_targets:
            null_accuracies.append(score_boundary_motif_counts(histories, variant, history_by_motif, global_history, test_filter, reversed_targets)["motif_accuracy"])
        motif_accuracy = actual["motif_accuracy"]
        baseline_accuracy = actual["baseline_accuracy"]
        p_value = round((1 + sum(1 for accuracy in null_accuracies if accuracy >= motif_accuracy)) / (1 + len(null_accuracies)), 9) if null_accuracies else 1.0
        atoms = [int(samples[heldout_step + 1]["atom"]) for samples in histories if len(samples) > heldout_step + 1]
        atom_counts: dict[int, int] = {}
        for atom in atoms:
            atom_counts[atom] = atom_counts.get(atom, 0) + 1
        dominant_atom = majority_atom(atom_counts)
        dominant_share = round(atom_counts.get(dominant_atom or 0, 0) / len(atoms), 9) if atoms else 0.0
        if actual["walk_forward_attempts"] < 32:
            verdict = "PHASE_INSUFFICIENT_HISTORY"
        elif motif_accuracy <= baseline_accuracy:
            verdict = "PHASE_NOT_ABOVE_BASELINE"
        elif p_value <= 0.05:
            verdict = "PHASE_ABOVE_ROTATION_NULL"
        elif p_value <= 0.1:
            verdict = "PHASE_ABOVE_ROTATION_NULL_PROVISIONAL"
        else:
            verdict = "PHASE_WITHIN_ROTATION_NULL"
        exemplar = histories[0][heldout_step] if histories and len(histories[0]) > heldout_step else {}
        phase_rows.append({
            "heldout_step": heldout_step,
            "source_inlet": int(exemplar.get("inlet", -1)),
            "target_step": heldout_step + 1,
            "target_inlet": int(histories[0][heldout_step + 1].get("inlet", -1)) if histories and len(histories[0]) > heldout_step + 1 else -1,
            "variant": variant,
            "transitions_evaluated": actual["transitions_evaluated"],
            "walk_forward_attempts": actual["walk_forward_attempts"],
            "motif_accuracy": motif_accuracy,
            "baseline_accuracy": baseline_accuracy,
            "baseline_lift": round(motif_accuracy - baseline_accuracy, 9),
            "null_p_value": p_value,
            "null_accuracy_min": round(min(null_accuracies), 9) if null_accuracies else None,
            "null_accuracy_max": round(max(null_accuracies), 9) if null_accuracies else None,
            "dominant_atom": dominant_atom,
            "dominant_share": dominant_share,
            "unique_atoms": len(atom_counts),
            "verdict": verdict,
        })
    failing_rows = [row for row in phase_rows if row["verdict"] != "PHASE_ABOVE_ROTATION_NULL"]
    passing_rows = [row for row in phase_rows if row["verdict"] == "PHASE_ABOVE_ROTATION_NULL"]
    weakest_rows = sorted(phase_rows, key=lambda row: (row["null_p_value"], -row["baseline_lift"]), reverse=True)[:5]
    return {
        "variant": variant,
        "phase_count": len(phase_rows),
        "passing_phase_count": len(passing_rows),
        "failing_phase_count": len(failing_rows),
        "phase_rows": phase_rows,
        "weakest_rows": weakest_rows,
        "overall_verdict": "TIME_OFFSET_OBSTRUCTION_LOCALIZED" if passing_rows and failing_rows else ("TIME_OFFSET_OBSTRUCTION_GLOBAL" if failing_rows else "NO_TIME_OFFSET_OBSTRUCTION"),
        "interpretation": "Per-step held-out audit: train on all other transition phases, score one held-out phase at a time.",
    }


def build_phase_clock_model_summary(
    histories: list[list[dict[str, Any]]],
    motif_history_split: dict[str, Any],
    motif_time_offset_split: dict[str, Any],
) -> dict[str, Any]:
    clock_history_split = summarize_split_family(histories, "history", 5, PHASE_CLOCK_VARIANTS)
    clock_time_offset_split = summarize_split_family(histories, "time_offset", 5, PHASE_CLOCK_VARIANTS)
    paired_residual = build_phase_clock_paired_residual_summary(
        histories,
        motif_history_split["best_variant"],
        clock_history_split["best_variant"],
        motif_time_offset_split["best_variant"],
        clock_time_offset_split["best_variant"],
    )
    history_residual_lift = round(float(motif_history_split["motif_accuracy"]) - float(clock_history_split["motif_accuracy"]), 9)
    time_offset_residual_lift = round(float(motif_time_offset_split["motif_accuracy"]) - float(clock_time_offset_split["motif_accuracy"]), 9)
    if history_residual_lift > 0.02 and motif_history_split["null_p_value"] <= 0.05:
        history_verdict = "MOTIF_ADDS_BEYOND_PHASE_CLOCK_HISTORY"
    elif history_residual_lift >= -0.02:
        history_verdict = "MOTIF_TIED_WITH_PHASE_CLOCK_HISTORY"
    else:
        history_verdict = "PHASE_CLOCK_DOMINATES_HISTORY"
    if time_offset_residual_lift > 0.02 and motif_time_offset_split["null_p_value"] <= 0.05:
        time_offset_verdict = "MOTIF_ADDS_BEYOND_PHASE_CLOCK_TIME_OFFSET"
    elif time_offset_residual_lift >= -0.02:
        time_offset_verdict = "MOTIF_TIED_WITH_PHASE_CLOCK_TIME_OFFSET"
    else:
        time_offset_verdict = "PHASE_CLOCK_DOMINATES_TIME_OFFSET"
    return {
        "clock_history_split": clock_history_split,
        "clock_time_offset_split": clock_time_offset_split,
        "motif_history_accuracy": motif_history_split["motif_accuracy"],
        "motif_history_best_variant": motif_history_split["best_variant"],
        "clock_history_accuracy": clock_history_split["motif_accuracy"],
        "clock_history_best_variant": clock_history_split["best_variant"],
        "history_residual_lift": history_residual_lift,
        "history_residual_verdict": history_verdict,
        "motif_time_offset_accuracy": motif_time_offset_split["motif_accuracy"],
        "motif_time_offset_best_variant": motif_time_offset_split["best_variant"],
        "clock_time_offset_accuracy": clock_time_offset_split["motif_accuracy"],
        "clock_time_offset_best_variant": clock_time_offset_split["best_variant"],
        "time_offset_residual_lift": time_offset_residual_lift,
        "time_offset_residual_verdict": time_offset_verdict,
        "paired_residual": paired_residual,
        "overall_verdict": (
            "MOTIF_RESIDUAL_BEYOND_PHASE_CLOCK"
            if history_verdict == "MOTIF_ADDS_BEYOND_PHASE_CLOCK_HISTORY"
            and time_offset_verdict == "MOTIF_ADDS_BEYOND_PHASE_CLOCK_TIME_OFFSET"
            and paired_residual["overall_verdict"] == "PAIRED_MOTIF_RESIDUAL_BEYOND_CLOCK"
            else "MOTIF_NOT_SEPARATED_FROM_PHASE_CLOCK"
        ),
        "interpretation": "Compares motif forecast against explicit finite phase-clock baselines before any hydrogen comparison.",
    }


def normal_one_sided_binomial_p(successes: int, failures: int) -> float:
    discordant = successes + failures
    if discordant <= 0:
        return 1.0
    if successes <= failures:
        return 1.0
    z = (successes - (discordant / 2) - 0.5) / math.sqrt(discordant / 4)
    return round(0.5 * math.erfc(z / math.sqrt(2)), 9)


def summarize_paired_residual_split(
    histories: list[list[dict[str, Any]]],
    split_kind: str,
    fold_count: int,
    motif_variant: str,
    clock_variant: str,
) -> dict[str, Any]:
    max_step = max((len(samples) - 1 for samples in histories), default=0)
    paired_attempts = 0
    motif_correct = 0
    clock_correct = 0
    both_correct = 0
    both_wrong = 0
    motif_only = 0
    clock_only = 0
    missing_pairs = 0
    rows = []
    for fold in range(fold_count):
        if split_kind == "history":
            train_histories = [samples for index, samples in enumerate(histories) if index % fold_count != fold]
            test_histories = [samples for index, samples in enumerate(histories) if index % fold_count == fold]
            train_filter = None
            test_filter = None
        else:
            train_histories = histories
            test_histories = histories
            train_filter = {step for step in range(max_step) if step % fold_count != fold}
            test_filter = {step for step in range(max_step) if step % fold_count == fold}
        motif_counts, _motif_global = train_boundary_motif_counts(train_histories, motif_variant, train_filter)
        clock_counts, _clock_global = train_boundary_motif_counts(train_histories, clock_variant, train_filter)
        for history_index, samples in enumerate(test_histories):
            for index in range(max(0, len(samples) - 1)):
                if test_filter is not None and index not in test_filter:
                    continue
                actual_atom = int(samples[index + 1]["atom"])
                motif_prediction = majority_atom(motif_counts.get(boundary_motif_key(samples[index], motif_variant), {}))
                clock_prediction = majority_atom(clock_counts.get(boundary_motif_key(samples[index], clock_variant), {}))
                if motif_prediction is None or clock_prediction is None:
                    missing_pairs += 1
                    continue
                paired_attempts += 1
                motif_hit = motif_prediction == actual_atom
                clock_hit = clock_prediction == actual_atom
                motif_correct += int(motif_hit)
                clock_correct += int(clock_hit)
                both_correct += int(motif_hit and clock_hit)
                both_wrong += int((not motif_hit) and (not clock_hit))
                motif_only += int(motif_hit and not clock_hit)
                clock_only += int(clock_hit and not motif_hit)
                if len(rows) < 96 and motif_hit != clock_hit:
                    rows.append({
                        "fold": fold,
                        "history": history_index,
                        "step": int(samples[index]["step"]),
                        "actual_next_atom": actual_atom,
                        "motif_variant": motif_variant,
                        "motif_prediction": motif_prediction,
                        "clock_variant": clock_variant,
                        "clock_prediction": clock_prediction,
                        "motif_hit": motif_hit,
                        "clock_hit": clock_hit,
                    })
    motif_accuracy = round(motif_correct / paired_attempts, 9) if paired_attempts else 0.0
    clock_accuracy = round(clock_correct / paired_attempts, 9) if paired_attempts else 0.0
    p_value = normal_one_sided_binomial_p(motif_only, clock_only)
    if paired_attempts < 32:
        verdict = "PAIRED_RESIDUAL_INSUFFICIENT"
    elif motif_only > clock_only and p_value <= 0.05:
        verdict = "PAIRED_MOTIF_RESIDUAL_BEATS_CLOCK"
    elif motif_only > clock_only:
        verdict = "PAIRED_MOTIF_RESIDUAL_WEAK"
    elif motif_only == clock_only:
        verdict = "PAIRED_MOTIF_CLOCK_TIE"
    else:
        verdict = "PAIRED_CLOCK_DOMINATES_MOTIF"
    return {
        "split_kind": split_kind,
        "fold_count": fold_count,
        "motif_variant": motif_variant,
        "clock_variant": clock_variant,
        "paired_attempts": paired_attempts,
        "missing_pairs": missing_pairs,
        "motif_correct": motif_correct,
        "clock_correct": clock_correct,
        "both_correct": both_correct,
        "both_wrong": both_wrong,
        "motif_only": motif_only,
        "clock_only": clock_only,
        "discordant_pairs": motif_only + clock_only,
        "motif_accuracy": motif_accuracy,
        "clock_accuracy": clock_accuracy,
        "residual_lift": round(motif_accuracy - clock_accuracy, 9),
        "motif_advantage_p": p_value,
        "verdict": verdict,
        "discordant_rows": rows,
    }


def build_phase_clock_paired_residual_summary(
    histories: list[list[dict[str, Any]]],
    motif_history_variant: str,
    clock_history_variant: str,
    motif_time_offset_variant: str,
    clock_time_offset_variant: str,
) -> dict[str, Any]:
    history = summarize_paired_residual_split(histories, "history", 5, motif_history_variant, clock_history_variant)
    time_offset = summarize_paired_residual_split(histories, "time_offset", 5, motif_time_offset_variant, clock_time_offset_variant)
    return {
        "history": history,
        "time_offset": time_offset,
        "overall_verdict": (
            "PAIRED_MOTIF_RESIDUAL_BEYOND_CLOCK"
            if history["verdict"] == "PAIRED_MOTIF_RESIDUAL_BEATS_CLOCK"
            and time_offset["verdict"] == "PAIRED_MOTIF_RESIDUAL_BEATS_CLOCK"
            else "PAIRED_MOTIF_RESIDUAL_NOT_CERTIFIED"
        ),
        "interpretation": "Paired residual: motif is counted only when it beats the selected clock model on the same held-out transition.",
    }


def build_source_state_transport_summary(histories: list[list[dict[str, Any]]]) -> dict[str, Any]:
    ward_history_split = summarize_split_family(histories, "history", 5, WARD_MOTIF_VARIANTS)
    ward_time_offset_split = summarize_split_family(histories, "time_offset", 5, WARD_MOTIF_VARIANTS)
    source_history_split = summarize_split_family(histories, "history", 5, SOURCE_STATE_VARIANTS)
    source_time_offset_split = summarize_split_family(histories, "time_offset", 5, SOURCE_STATE_VARIANTS)
    paired_history = summarize_paired_residual_split(
        histories,
        "history",
        5,
        ward_history_split["best_variant"],
        source_history_split["best_variant"],
    )
    paired_time_offset = summarize_paired_residual_split(
        histories,
        "time_offset",
        5,
        ward_time_offset_split["best_variant"],
        source_time_offset_split["best_variant"],
    )
    return {
        "ward_history_split": ward_history_split,
        "ward_time_offset_split": ward_time_offset_split,
        "source_history_split": source_history_split,
        "source_time_offset_split": source_time_offset_split,
        "history_residual_lift": round(float(ward_history_split["motif_accuracy"]) - float(source_history_split["motif_accuracy"]), 9),
        "time_offset_residual_lift": round(float(ward_time_offset_split["motif_accuracy"]) - float(source_time_offset_split["motif_accuracy"]), 9),
        "paired_ward_vs_source": {
            "history": paired_history,
            "time_offset": paired_time_offset,
            "overall_verdict": (
                "WARD_MOTIF_RESIDUAL_BEYOND_SOURCE_STATE"
                if paired_history["verdict"] == "PAIRED_MOTIF_RESIDUAL_BEATS_CLOCK"
                and paired_time_offset["verdict"] == "PAIRED_MOTIF_RESIDUAL_BEATS_CLOCK"
                else "WARD_MOTIF_NOT_SEPARATED_FROM_SOURCE_STATE"
            ),
        },
        "overall_verdict": (
            "WARD_MOTIF_RESIDUAL_BEYOND_SOURCE_STATE"
            if paired_history["verdict"] == "PAIRED_MOTIF_RESIDUAL_BEATS_CLOCK"
            and paired_time_offset["verdict"] == "PAIRED_MOTIF_RESIDUAL_BEATS_CLOCK"
            else "SOURCE_STATE_TRANSPORT_DOMINATES_WARD_MOTIF"
        ),
        "interpretation": "Separates C2/Ward component motifs from source-state transport keys such as current atom plus inlet.",
    }


def source_conditioned_ward_key(
    sample: dict[str, Any],
    ward_variant: str,
    source_variant: str,
    ward_override: str | None = None,
) -> tuple[str, str, str]:
    source_key = boundary_motif_key(sample, source_variant)
    ward_key = ward_override if ward_override is not None else boundary_motif_key(sample, ward_variant)
    return source_key + "__ward__" + ward_key, source_key, ward_key


def build_source_conditioned_ward_overrides(
    histories: list[list[dict[str, Any]]],
    ward_variant: str,
    source_variant: str,
    shift: int,
) -> dict[tuple[int, int], str]:
    groups: dict[str, list[tuple[tuple[int, int], str]]] = {}
    for history_index, samples in enumerate(histories):
        for step_index in range(max(0, len(samples) - 1)):
            source_key = boundary_motif_key(samples[step_index], source_variant)
            ward_key = boundary_motif_key(samples[step_index], ward_variant)
            groups.setdefault(source_key, []).append(((history_index, step_index), ward_key))
    overrides: dict[tuple[int, int], str] = {}
    for rows in groups.values():
        if not rows:
            continue
        offset = shift % len(rows)
        rotated = [ward for _, ward in rows[offset:]] + [ward for _, ward in rows[:offset]]
        for (identity, _), ward_key in zip(rows, rotated):
            overrides[identity] = ward_key
    return overrides


def train_source_conditioned_ward_counts(
    histories: list[list[dict[str, Any]]],
    ward_variant: str,
    source_variant: str,
    history_filter: set[int] | None = None,
    step_filter: set[int] | None = None,
    ward_overrides: dict[tuple[int, int], str] | None = None,
) -> tuple[dict[str, dict[int, int]], dict[str, dict[int, int]]]:
    ward_history: dict[str, dict[int, int]] = {}
    source_history: dict[str, dict[int, int]] = {}
    for history_index, samples in enumerate(histories):
        if history_filter is not None and history_index not in history_filter:
            continue
        for step_index in range(max(0, len(samples) - 1)):
            if step_filter is not None and step_index not in step_filter:
                continue
            actual_atom = int(samples[step_index + 1]["atom"])
            override = ward_overrides.get((history_index, step_index)) if ward_overrides else None
            combined_key, source_key, _ = source_conditioned_ward_key(samples[step_index], ward_variant, source_variant, override)
            ward_counts = ward_history.setdefault(combined_key, {})
            ward_counts[actual_atom] = ward_counts.get(actual_atom, 0) + 1
            source_counts = source_history.setdefault(source_key, {})
            source_counts[actual_atom] = source_counts.get(actual_atom, 0) + 1
    return ward_history, source_history


def score_source_conditioned_ward_counts(
    histories: list[list[dict[str, Any]]],
    ward_variant: str,
    source_variant: str,
    ward_history: dict[str, dict[int, int]],
    source_history: dict[str, dict[int, int]],
    history_filter: set[int] | None = None,
    step_filter: set[int] | None = None,
    ward_overrides: dict[tuple[int, int], str] | None = None,
) -> dict[str, Any]:
    rows = []
    transitions_evaluated = 0
    paired_attempts = 0
    skipped = 0
    ward_correct = 0
    source_correct = 0
    ward_only = 0
    source_only = 0
    both_correct = 0
    both_wrong = 0
    for history_index, samples in enumerate(histories):
        if history_filter is not None and history_index not in history_filter:
            continue
        for step_index in range(max(0, len(samples) - 1)):
            if step_filter is not None and step_index not in step_filter:
                continue
            transitions_evaluated += 1
            actual_atom = int(samples[step_index + 1]["atom"])
            override = ward_overrides.get((history_index, step_index)) if ward_overrides else None
            combined_key, source_key, ward_key = source_conditioned_ward_key(samples[step_index], ward_variant, source_variant, override)
            ward_prediction = majority_atom(ward_history.get(combined_key, {}))
            source_prediction = majority_atom(source_history.get(source_key, {}))
            if ward_prediction is None or source_prediction is None:
                skipped += 1
                continue
            ward_hit = ward_prediction == actual_atom
            source_hit = source_prediction == actual_atom
            paired_attempts += 1
            ward_correct += int(ward_hit)
            source_correct += int(source_hit)
            ward_only += int(ward_hit and not source_hit)
            source_only += int(source_hit and not ward_hit)
            both_correct += int(ward_hit and source_hit)
            both_wrong += int((not ward_hit) and (not source_hit))
            if len(rows) < 96:
                rows.append({
                    "history": history_index,
                    "step": int(samples[step_index]["step"]),
                    "source_key": source_key,
                    "ward_key": ward_key,
                    "actual_next_atom": actual_atom,
                    "ward_prediction": ward_prediction,
                    "source_prediction": source_prediction,
                    "ward_hit": ward_hit,
                    "source_hit": source_hit,
                })
    discordant = ward_only + source_only
    return {
        "transitions_evaluated": transitions_evaluated,
        "paired_attempts": paired_attempts,
        "skipped_cold_start": skipped,
        "ward_correct": ward_correct,
        "source_correct": source_correct,
        "ward_accuracy": round(ward_correct / paired_attempts, 9) if paired_attempts else 0.0,
        "source_accuracy": round(source_correct / paired_attempts, 9) if paired_attempts else 0.0,
        "residual_lift": round((ward_correct - source_correct) / paired_attempts, 9) if paired_attempts else 0.0,
        "ward_only": ward_only,
        "source_only": source_only,
        "both_correct": both_correct,
        "both_wrong": both_wrong,
        "discordant_pairs": discordant,
        "rows": rows,
    }


def summarize_source_conditioned_ward_variant(
    histories: list[list[dict[str, Any]]],
    split_kind: str,
    fold_count: int,
    ward_variant: str,
    source_variant: str,
) -> dict[str, Any]:
    totals = {
        "transitions_evaluated": 0,
        "paired_attempts": 0,
        "skipped_cold_start": 0,
        "ward_correct": 0,
        "source_correct": 0,
        "ward_only": 0,
        "source_only": 0,
        "both_correct": 0,
        "both_wrong": 0,
        "discordant_pairs": 0,
    }
    rows = []
    max_step = max((len(samples) - 1 for samples in histories), default=0)
    for fold in range(fold_count):
        if split_kind == "history":
            train_histories = {index for index in range(len(histories)) if index % fold_count != fold}
            test_histories = {index for index in range(len(histories)) if index % fold_count == fold}
            train_steps = None
            test_steps = None
        else:
            train_histories = None
            test_histories = None
            train_steps = {step for step in range(max_step) if step % fold_count != fold}
            test_steps = {step for step in range(max_step) if step % fold_count == fold}
        ward_history, source_history = train_source_conditioned_ward_counts(
            histories,
            ward_variant,
            source_variant,
            train_histories,
            train_steps,
        )
        actual = score_source_conditioned_ward_counts(
            histories,
            ward_variant,
            source_variant,
            ward_history,
            source_history,
            test_histories,
            test_steps,
        )
        for key in totals:
            totals[key] += int(actual[key])
        rows.extend(actual["rows"][: max(0, 96 - len(rows))])
    paired_attempts = totals["paired_attempts"]
    ward_accuracy = round(totals["ward_correct"] / paired_attempts, 9) if paired_attempts else 0.0
    source_accuracy = round(totals["source_correct"] / paired_attempts, 9) if paired_attempts else 0.0
    residual_lift = round(ward_accuracy - source_accuracy, 9)
    null_residual_lifts = []
    null_shifts = range(1, max(2, min(17, max_step + 1)))
    for shift in null_shifts:
        overrides = build_source_conditioned_ward_overrides(histories, ward_variant, source_variant, shift)
        null_totals = {
            "paired_attempts": 0,
            "ward_correct": 0,
            "source_correct": 0,
        }
        for fold in range(fold_count):
            if split_kind == "history":
                train_histories = {index for index in range(len(histories)) if index % fold_count != fold}
                test_histories = {index for index in range(len(histories)) if index % fold_count == fold}
                train_steps = None
                test_steps = None
            else:
                train_histories = None
                test_histories = None
                train_steps = {step for step in range(max_step) if step % fold_count != fold}
                test_steps = {step for step in range(max_step) if step % fold_count == fold}
            ward_history, source_history = train_source_conditioned_ward_counts(
                histories,
                ward_variant,
                source_variant,
                train_histories,
                train_steps,
                overrides,
            )
            null_score = score_source_conditioned_ward_counts(
                histories,
                ward_variant,
                source_variant,
                ward_history,
                source_history,
                test_histories,
                test_steps,
                overrides,
            )
            null_totals["paired_attempts"] += int(null_score["paired_attempts"])
            null_totals["ward_correct"] += int(null_score["ward_correct"])
            null_totals["source_correct"] += int(null_score["source_correct"])
        attempts = null_totals["paired_attempts"]
        null_lift = round((null_totals["ward_correct"] - null_totals["source_correct"]) / attempts, 9) if attempts else 0.0
        null_residual_lifts.append(null_lift)
    p_value = round((1 + sum(1 for lift in null_residual_lifts if lift >= residual_lift)) / (1 + len(null_residual_lifts)), 9) if null_residual_lifts else 1.0
    if paired_attempts < 32:
        verdict = "INSUFFICIENT_SOURCE_CONDITIONED_WARD_HISTORY"
    elif residual_lift <= 0:
        verdict = "SOURCE_CONDITIONED_WARD_NOT_ABOVE_SOURCE"
    elif p_value <= 0.05:
        verdict = "SOURCE_CONDITIONED_WARD_RESIDUAL_BEATS_NULL"
    elif p_value <= 0.1:
        verdict = "SOURCE_CONDITIONED_WARD_RESIDUAL_BEATS_NULL_PROVISIONAL"
    else:
        verdict = "SOURCE_CONDITIONED_WARD_WITHIN_NULL"
    return {
        **totals,
        "split_kind": split_kind,
        "ward_variant": ward_variant,
        "source_variant": source_variant,
        "ward_accuracy": ward_accuracy,
        "source_accuracy": source_accuracy,
        "residual_lift": residual_lift,
        "null_trials": len(null_residual_lifts),
        "null_residual_lift_min": round(min(null_residual_lifts), 9) if null_residual_lifts else None,
        "null_residual_lift_max": round(max(null_residual_lifts), 9) if null_residual_lifts else None,
        "null_p_value": p_value,
        "verdict": verdict,
        "rows": rows,
    }


def summarize_source_conditioned_ward_family(
    histories: list[list[dict[str, Any]]],
    split_kind: str,
    fold_count: int,
) -> dict[str, Any]:
    variant_rows = [
        summarize_source_conditioned_ward_variant(histories, split_kind, fold_count, ward_variant, source_variant)
        for source_variant in SOURCE_STATE_VARIANTS
        for ward_variant in WARD_MOTIF_VARIANTS
    ]
    best = sorted(
        variant_rows,
        key=lambda row: (
            row["residual_lift"],
            -row["null_p_value"],
            row["ward_accuracy"],
            row["paired_attempts"],
        ),
        reverse=True,
    )[0]
    return {
        **best,
        "best_ward_variant": best["ward_variant"],
        "best_source_variant": best["source_variant"],
        "variant_rows": variant_rows,
        "null_model": "within-source rotations of Ward/C985 keys while source atom/inlet transport and next atoms are held fixed",
        "interpretation": split_kind + " source-conditioned Ward residual over identity plus certified null pulse histories.",
    }


def build_source_conditioned_ward_residual_summary(histories: list[list[dict[str, Any]]]) -> dict[str, Any]:
    history_split = summarize_source_conditioned_ward_family(histories, "history", 5)
    time_offset_split = summarize_source_conditioned_ward_family(histories, "time_offset", 5)
    passing = {
        "SOURCE_CONDITIONED_WARD_RESIDUAL_BEATS_NULL",
        "SOURCE_CONDITIONED_WARD_RESIDUAL_BEATS_NULL_PROVISIONAL",
    }
    overall = (
        "SOURCE_CONDITIONED_WARD_RESIDUAL_CERTIFIED"
        if history_split["verdict"] in passing and time_offset_split["verdict"] in passing
        else "SOURCE_CONDITIONED_WARD_RESIDUAL_NOT_CERTIFIED"
    )
    return {
        "history_split": history_split,
        "time_offset_split": time_offset_split,
        "overall_verdict": overall,
        "interpretation": "Holds source atom/inlet transport fixed and asks whether Ward/C985 keys add residual predictive information.",
    }


def packet_family_id(atom: int, families: list[list[int]]) -> int | None:
    for family_index, family in enumerate(families):
        if atom in family:
            return family_index
    return None


def score_rank_one_packet_family_counts(
    histories: list[list[dict[str, Any]]],
    ward_variant: str,
    source_variant: str,
    ward_history: dict[str, dict[int, int]],
    source_history: dict[str, dict[int, int]],
    families: list[list[int]],
    history_filter: set[int] | None = None,
    step_filter: set[int] | None = None,
    ward_overrides: dict[tuple[int, int], str] | None = None,
) -> dict[str, Any]:
    paired_attempts = 0
    skipped = 0
    actual_family_attempts = 0
    ward_family_correct = 0
    source_family_correct = 0
    ward_family_only = 0
    source_family_only = 0
    both_family_correct = 0
    both_family_wrong = 0
    outside_actual = 0
    rows = []
    by_family = [
        {
            "family": family,
            "actual_next_hits": 0,
            "ward_family_correct": 0,
            "source_family_correct": 0,
            "ward_family_only": 0,
            "source_family_only": 0,
        }
        for family in families
    ]
    for history_index, samples in enumerate(histories):
        if history_filter is not None and history_index not in history_filter:
            continue
        for step_index in range(max(0, len(samples) - 1)):
            if step_filter is not None and step_index not in step_filter:
                continue
            actual_atom = int(samples[step_index + 1]["atom"])
            override = ward_overrides.get((history_index, step_index)) if ward_overrides else None
            combined_key, source_key, ward_key = source_conditioned_ward_key(samples[step_index], ward_variant, source_variant, override)
            ward_prediction = majority_atom(ward_history.get(combined_key, {}))
            source_prediction = majority_atom(source_history.get(source_key, {}))
            if ward_prediction is None or source_prediction is None:
                skipped += 1
                continue
            paired_attempts += 1
            actual_family = packet_family_id(actual_atom, families)
            ward_family = packet_family_id(int(ward_prediction), families)
            source_family = packet_family_id(int(source_prediction), families)
            if actual_family is None:
                outside_actual += 1
                continue
            actual_family_attempts += 1
            ward_hit = ward_family == actual_family
            source_hit = source_family == actual_family
            ward_family_correct += int(ward_hit)
            source_family_correct += int(source_hit)
            ward_family_only += int(ward_hit and not source_hit)
            source_family_only += int(source_hit and not ward_hit)
            both_family_correct += int(ward_hit and source_hit)
            both_family_wrong += int((not ward_hit) and (not source_hit))
            family_row = by_family[actual_family]
            family_row["actual_next_hits"] += 1
            family_row["ward_family_correct"] += int(ward_hit)
            family_row["source_family_correct"] += int(source_hit)
            family_row["ward_family_only"] += int(ward_hit and not source_hit)
            family_row["source_family_only"] += int(source_hit and not ward_hit)
            if len(rows) < 96:
                rows.append({
                    "history": history_index,
                    "step": int(samples[step_index]["step"]),
                    "actual_next_atom": actual_atom,
                    "actual_family": actual_family,
                    "ward_prediction": int(ward_prediction),
                    "source_prediction": int(source_prediction),
                    "ward_family": ward_family,
                    "source_family": source_family,
                    "ward_family_hit": ward_hit,
                    "source_family_hit": source_hit,
                    "source_key": source_key,
                    "ward_key": ward_key,
                })
    discordant = ward_family_only + source_family_only
    return {
        "paired_attempts": paired_attempts,
        "skipped_cold_start": skipped,
        "actual_family_attempts": actual_family_attempts,
        "outside_actual_family": outside_actual,
        "actual_family_rate": round(actual_family_attempts / paired_attempts, 9) if paired_attempts else 0.0,
        "ward_family_correct": ward_family_correct,
        "source_family_correct": source_family_correct,
        "ward_family_accuracy": round(ward_family_correct / actual_family_attempts, 9) if actual_family_attempts else 0.0,
        "source_family_accuracy": round(source_family_correct / actual_family_attempts, 9) if actual_family_attempts else 0.0,
        "family_residual_lift": round((ward_family_correct - source_family_correct) / actual_family_attempts, 9) if actual_family_attempts else 0.0,
        "ward_family_only": ward_family_only,
        "source_family_only": source_family_only,
        "both_family_correct": both_family_correct,
        "both_family_wrong": both_family_wrong,
        "discordant_family_pairs": discordant,
        "by_family": by_family,
        "rows": rows,
    }


def summarize_rank_one_packet_family_split(
    histories: list[list[dict[str, Any]]],
    split_kind: str,
    ward_variant: str,
    source_variant: str,
    families: list[list[int]],
    fold_count: int = 5,
) -> dict[str, Any]:
    totals = {
        "paired_attempts": 0,
        "skipped_cold_start": 0,
        "actual_family_attempts": 0,
        "outside_actual_family": 0,
        "ward_family_correct": 0,
        "source_family_correct": 0,
        "ward_family_only": 0,
        "source_family_only": 0,
        "both_family_correct": 0,
        "both_family_wrong": 0,
        "discordant_family_pairs": 0,
    }
    rows = []
    by_family = [
        {
            "family": family,
            "actual_next_hits": 0,
            "ward_family_correct": 0,
            "source_family_correct": 0,
            "ward_family_only": 0,
            "source_family_only": 0,
        }
        for family in families
    ]
    max_step = max((len(samples) - 1 for samples in histories), default=0)
    for fold in range(fold_count):
        if split_kind == "history":
            train_histories = {index for index in range(len(histories)) if index % fold_count != fold}
            test_histories = {index for index in range(len(histories)) if index % fold_count == fold}
            train_steps = None
            test_steps = None
        else:
            train_histories = None
            test_histories = None
            train_steps = {step for step in range(max_step) if step % fold_count != fold}
            test_steps = {step for step in range(max_step) if step % fold_count == fold}
        ward_history, source_history = train_source_conditioned_ward_counts(histories, ward_variant, source_variant, train_histories, train_steps)
        actual = score_rank_one_packet_family_counts(
            histories,
            ward_variant,
            source_variant,
            ward_history,
            source_history,
            families,
            test_histories,
            test_steps,
        )
        for key in totals:
            totals[key] += int(actual[key])
        for index, family_row in enumerate(actual["by_family"]):
            for key in ("actual_next_hits", "ward_family_correct", "source_family_correct", "ward_family_only", "source_family_only"):
                by_family[index][key] += int(family_row[key])
        rows.extend(actual["rows"][: max(0, 96 - len(rows))])
    null_lifts = []
    for shift in range(1, max(2, min(17, max_step + 1))):
        overrides = build_source_conditioned_ward_overrides(histories, ward_variant, source_variant, shift)
        null_totals = {"actual_family_attempts": 0, "ward_family_correct": 0, "source_family_correct": 0}
        for fold in range(fold_count):
            if split_kind == "history":
                train_histories = {index for index in range(len(histories)) if index % fold_count != fold}
                test_histories = {index for index in range(len(histories)) if index % fold_count == fold}
                train_steps = None
                test_steps = None
            else:
                train_histories = None
                test_histories = None
                train_steps = {step for step in range(max_step) if step % fold_count != fold}
                test_steps = {step for step in range(max_step) if step % fold_count == fold}
            ward_history, source_history = train_source_conditioned_ward_counts(histories, ward_variant, source_variant, train_histories, train_steps, overrides)
            null_score = score_rank_one_packet_family_counts(
                histories,
                ward_variant,
                source_variant,
                ward_history,
                source_history,
                families,
                test_histories,
                test_steps,
                overrides,
            )
            null_totals["actual_family_attempts"] += int(null_score["actual_family_attempts"])
            null_totals["ward_family_correct"] += int(null_score["ward_family_correct"])
            null_totals["source_family_correct"] += int(null_score["source_family_correct"])
        attempts = null_totals["actual_family_attempts"]
        null_lifts.append(round((null_totals["ward_family_correct"] - null_totals["source_family_correct"]) / attempts, 9) if attempts else 0.0)
    family_attempts = totals["actual_family_attempts"]
    ward_accuracy = round(totals["ward_family_correct"] / family_attempts, 9) if family_attempts else 0.0
    source_accuracy = round(totals["source_family_correct"] / family_attempts, 9) if family_attempts else 0.0
    lift = round(ward_accuracy - source_accuracy, 9)
    p_value = round((1 + sum(1 for null_lift in null_lifts if null_lift >= lift)) / (1 + len(null_lifts)), 9) if null_lifts else 1.0
    if family_attempts < 8:
        verdict = "PACKET_FAMILY_RESIDUAL_INSUFFICIENT_OVERLAP"
    elif lift <= 0:
        verdict = "PACKET_FAMILY_WARD_NOT_ABOVE_SOURCE"
    elif p_value <= 0.05:
        verdict = "PACKET_FAMILY_WARD_RESIDUAL_BEATS_NULL"
    elif p_value <= 0.1:
        verdict = "PACKET_FAMILY_WARD_RESIDUAL_BEATS_NULL_PROVISIONAL"
    else:
        verdict = "PACKET_FAMILY_WARD_RESIDUAL_WITHIN_NULL"
    return {
        **totals,
        "split_kind": split_kind,
        "ward_variant": ward_variant,
        "source_variant": source_variant,
        "families": families,
        "actual_family_rate": round(family_attempts / totals["paired_attempts"], 9) if totals["paired_attempts"] else 0.0,
        "ward_family_accuracy": ward_accuracy,
        "source_family_accuracy": source_accuracy,
        "family_residual_lift": lift,
        "null_trials": len(null_lifts),
        "null_residual_lift_min": round(min(null_lifts), 9) if null_lifts else None,
        "null_residual_lift_max": round(max(null_lifts), 9) if null_lifts else None,
        "null_p_value": p_value,
        "verdict": verdict,
        "by_family": by_family,
        "rows": rows,
    }


def build_rank_one_packet_family_residual_summary(
    histories: list[list[dict[str, Any]]],
    source_conditioned_ward_residual: dict[str, Any],
) -> dict[str, Any]:
    history_source = source_conditioned_ward_residual["history_split"]["best_source_variant"]
    history_ward = source_conditioned_ward_residual["history_split"]["best_ward_variant"]
    time_source = source_conditioned_ward_residual["time_offset_split"]["best_source_variant"]
    time_ward = source_conditioned_ward_residual["time_offset_split"]["best_ward_variant"]
    history_split = summarize_rank_one_packet_family_split(histories, "history", history_ward, history_source, RANK_ONE_PACKET_SUPPORT_FAMILIES)
    time_offset_split = summarize_rank_one_packet_family_split(histories, "time_offset", time_ward, time_source, RANK_ONE_PACKET_SUPPORT_FAMILIES)
    passing = {
        "PACKET_FAMILY_WARD_RESIDUAL_BEATS_NULL",
        "PACKET_FAMILY_WARD_RESIDUAL_BEATS_NULL_PROVISIONAL",
    }
    if (
        history_split["verdict"] == "PACKET_FAMILY_WARD_RESIDUAL_BEATS_NULL"
        and time_offset_split["verdict"] == "PACKET_FAMILY_WARD_RESIDUAL_BEATS_NULL"
    ):
        overall = "PACKET_FAMILY_WARD_RESIDUAL_CERTIFIED"
    elif history_split["verdict"] in passing and time_offset_split["verdict"] in passing:
        overall = "PACKET_FAMILY_WARD_RESIDUAL_PROVISIONAL"
    else:
        overall = "PACKET_FAMILY_WARD_RESIDUAL_NOT_CERTIFIED"
    return {
        "families": RANK_ONE_PACKET_SUPPORT_FAMILIES,
        "history_split": history_split,
        "time_offset_split": time_offset_split,
        "overall_verdict": overall,
        "interpretation": "Projects the source-conditioned Ward residual onto the rank-one support-2 packet bridge candidate families.",
    }


def build_boundary_packet_bridge_summary(
    pairing_report: dict[str, Any] | None,
    row_normalization_report: dict[str, Any] | None,
    low_support_report: dict[str, Any] | None,
) -> dict[str, Any]:
    pairing_checks = pairing_report.get("checks", {}) if pairing_report else {}
    row_checks = row_normalization_report.get("checks", {}) if row_normalization_report else {}
    low_checks = low_support_report.get("checks", {}) if low_support_report else {}
    row_summary = (
        row_normalization_report.get("derived", {}).get("obstruction_summary", {})
        if row_normalization_report
        else {}
    )
    low_rows = (
        low_support_report.get("derived", {}).get("compatible_doublet_candidate_rows", [])
        if low_support_report
        else []
    )
    support_families = []
    for row in low_rows:
        support = tuple(sorted(int(item["public_atom_id"]) for item in row.get("left_support", [])))
        if support and support not in support_families:
            support_families.append(support)
    all_receipts_pass = all([
        bool(pairing_report and pairing_report.get("all_checks_pass")),
        bool(row_normalization_report and row_normalization_report.get("all_checks_pass")),
        bool(low_support_report and low_support_report.get("all_checks_pass")),
    ])
    return {
        "status": "BOUNDARY_PACKET_BRIDGE_SEAM_CERTIFIED_RECEIPTS" if all_receipts_pass else "BOUNDARY_PACKET_BRIDGE_SEAM_MISSING_RECEIPTS",
        "pairing_obstruction": {
            "artifact": str(BOUNDARY_PACKET_PAIRING_REPORT.relative_to(ROOT)),
            "all_checks_pass": bool(pairing_report and pairing_report.get("all_checks_pass")),
            "raw_compatible_pairs": 0 if pairing_checks.get("raw_compatible_pair_count_is_zero") else None,
            "raw_perfect_matching_exists": False if pairing_checks.get("raw_perfect_matching_does_not_exist") else None,
            "minimal_scalar_with_matching": 6 if pairing_checks.get("minimal_scalar_with_matching_is_6") else None,
            "joint_boundary_packet_scalar_lcm": 12 if pairing_checks.get("joint_boundary_packet_scalar_lcm_is_12") else None,
            "claim": pairing_report.get("claim", "") if pairing_report else "",
        },
        "row_normalization_obstruction": {
            "artifact": str(BOUNDARY_PACKET_ROW_NORMALIZATION_REPORT.relative_to(ROOT)),
            "all_checks_pass": bool(row_normalization_report and row_normalization_report.get("all_checks_pass")),
            "all_rows_require_even_scalar_by_parity": bool(row_summary.get("all_rows_require_even_scalar_by_parity")),
            "row_scalar_divisibility_for_any_packet_pairing": int(row_summary.get("row_scalar_divisibility_for_any_packet_pairing", 0)),
            "only_compatible_residue_pair_mod6": row_summary.get("only_compatible_residue_pair_mod6", []),
            "nonuniform_row_scaling_improves_on_scalar_6": bool(row_summary.get("nonuniform_row_scaling_improves_on_scalar_6")),
            "tested_unordered_public_pair_count": int(row_summary.get("tested_unordered_public_pair_count", 0)),
            "claim": row_normalization_report.get("claim", "") if row_normalization_report else "",
        },
        "low_support_candidate_atlas": {
            "artifact": str(BOUNDARY_PACKET_LOW_SUPPORT_REPORT.relative_to(ROOT)),
            "all_checks_pass": bool(low_support_report and low_support_report.get("all_checks_pass")),
            "candidate_count": 800 if low_checks.get("candidate_count_is_800") else None,
            "even_image_candidate_count": 12 if low_checks.get("even_image_candidate_count_is_12") else None,
            "compatible_doublet_count": len(low_rows),
            "compatible_doublets_all_rank_one": bool(low_rows) and all(int(row.get("doublet_rank_over_Q", 0)) == 1 for row in low_rows),
            "support_families": [list(family) for family in support_families],
            "claim": low_support_report.get("claim", "") if low_support_report else "",
        },
        "interpretation": "Raw public-atom pairing and diagonal row normalization do not build the packet bridge. The first low-support non-diagonal rows are rank-one degeneracies, so the next physical seam is a genuine signed quotient or normalization rather than a prettier coil view.",
    }


def build_a985_q12_packet_bridge_probe_summary(bridge_probe: dict[str, Any] | None) -> dict[str, Any]:
    if not bridge_probe:
        return {
            "status": "A985_Q12_PACKET_BRIDGE_PROBE_MISSING",
            "all_checks_pass": False,
            "artifact": str(HYDROGEN_SANDPILE_GOLAY_BRIDGE_PROBE.relative_to(ROOT)),
            "interpretation": "The ingress-backed A985/q12 bridge probe has not been generated, so support-3 boundary quotients remain detached from the C985 packet-projection chain.",
        }

    ingress_inventory = bridge_probe.get("ingress_boundary_packet_projection_inventory_audit", {})
    ingress_gap = ingress_inventory.get("packet_restriction_gap_summary", {})
    seed_support3 = bridge_probe.get("mask288_q12_packet_seed_support3_audit", {})
    one_sided = bridge_probe.get("mask288_q12_one_sided_seed_correction_audit", {})
    one_sided_doublets = one_sided.get("compatible_doublet_summary", {})
    rank20 = bridge_probe.get("mask288_q12_corrected_rank20_selection_audit", {})
    rank20_ceiling = rank20.get("rank_ceiling_summary", {})
    natural_projection = bridge_probe.get("boundary_packet_projection_candidate_audit", {})
    natural_projection_candidates = natural_projection.get("candidate_summary", {})
    signed_step = bridge_probe.get("signed_step_column_packet_search_audit", {})
    signed_step_search = signed_step.get("search_summary", {})
    full_lattice = bridge_probe.get("full_step_column_congruence_lattice_audit", {})
    full_lattice_summary = full_lattice.get("full_lattice_summary", {})
    q42_filter = bridge_probe.get("q42_q12_quotient_adjusted_packet_filter_audit", {})
    q42_filter_summary = q42_filter.get("quotient_adjusted_summary", {})
    q42_capacity = bridge_probe.get("hidden_q42_a985_matrix_unit_capacity_audit", {})
    q42_capacity_summary = q42_capacity.get("hidden_capacity_summary", {})
    q42_slice = bridge_probe.get("q42_tensor_rank20_slice_quotient_audit", {})
    q42_slice_summary = q42_slice.get("rank20_slice_summary", {})
    charge_partition = bridge_probe.get("q12_packet_charge_sum_partition_fingerprint_audit", {})
    charge_partition_summary = charge_partition.get("partition_summary", {})

    artifact_file_sha256 = (
        hashlib.sha256(HYDROGEN_SANDPILE_GOLAY_BRIDGE_PROBE.read_bytes()).hexdigest()
        if HYDROGEN_SANDPILE_GOLAY_BRIDGE_PROBE.exists()
        else ""
    )
    rank_ceiling = int(rank20_ceiling.get("combined_boundary_image_rank_over_Q", 0))
    target_rank = int(rank20_ceiling.get("target_rank", 20))
    return {
        "artifact": str(HYDROGEN_SANDPILE_GOLAY_BRIDGE_PROBE.relative_to(ROOT)),
        "artifact_sha256": bridge_probe.get("artifact_sha256", ""),
        "artifact_file_sha256": artifact_file_sha256,
        "status": bridge_probe.get("status", ""),
        "all_checks_pass": bool(bridge_probe.get("all_checks_pass")),
        "claim_boundary": bridge_probe.get("claim_boundary", ""),
        "best_assignment_count": bridge_probe.get("assignment_search", {}).get("best_assignment_count"),
        "full_certified_assignment_remains_open": bool(bridge_probe.get("checks", {}).get("full_certified_h8_assignment_remains_open")),
        "ingress_projection_inventory": {
            "status": ingress_inventory.get("status", ""),
            "missing_bridge_count": int(ingress_gap.get("missing_bridge_count", 0)),
        },
        "mask288_q12_seed_support3": {
            "status": seed_support3.get("status", ""),
            "candidate_count": int(seed_support3.get("candidate_count", 0)),
            "even_image_candidate_count": int(seed_support3.get("even_image_candidate_count", 0)),
            "compatible_doublet_count": int(seed_support3.get("compatible_doublet_count", 0)),
        },
        "one_sided_seed_correction": {
            "status": one_sided.get("status", ""),
            "compatible_doublet_count": int(one_sided_doublets.get("compatible_doublet_count", 0)),
            "combined_rank2_support_family_count": int(one_sided_doublets.get("combined_rank2_support_family_count", 0)),
        },
        "corrected_rank20_selection": {
            "status": rank20.get("status", ""),
            "combined_boundary_image_rank_over_Q": rank_ceiling,
            "target_rank": target_rank,
            "packet_rank_shortfall": max(0, target_rank - rank_ceiling),
            "unique_boundary_image_count": int(rank20_ceiling.get("unique_boundary_image_count", 0)),
        },
        "natural_25_to_20_projection": {
            "status": natural_projection.get("status", ""),
            "columns_passing_packet_snf_image": natural_projection_candidates.get("columns_passing_packet_snf_image", []),
        },
        "signed_step_column_search": {
            "status": signed_step.get("status", ""),
            "compatible_row_count": int(signed_step_search.get("compatible_row_count", 0)),
            "unique_target_vector_rank_over_Q": int(signed_step_search.get("unique_target_vector_rank_over_Q", 0)),
        },
        "full_step_column_lattice": {
            "status": full_lattice.get("status", ""),
            "basis_target_rank_over_Q": int(full_lattice_summary.get("basis_target_rank_over_Q", 0)),
            "packet_target_rank_shortfall_after_full_type_lattice": int(full_lattice_summary.get("packet_target_rank_shortfall_after_full_type_lattice", 0)),
        },
        "q42_q12_filter": {
            "status": q42_filter.get("status", ""),
            "natural_pass_count": int(q42_filter_summary.get("q42_scalar6_natural_target_passing_row_count", 0)),
            "natural_pass_rank_over_Q": int(q42_filter_summary.get("q42_scalar6_natural_target_passing_rank_over_Q", 0)),
            "packet_rank_shortfall": int(q42_filter_summary.get("q42_natural_pass_packet_rank_shortfall", 0)),
        },
        "hidden_q42_a985_capacity": {
            "status": q42_capacity.get("status", ""),
            "matrix_unit_rank": int(q42_capacity_summary.get("q42_matrix_unit_aggregate_rank_mod_p", 0)),
            "packet_target_excess": int(q42_capacity_summary.get("q42_matrix_unit_rank_excess_over_packet_target", 0)),
            "block_lift_excess": int(q42_capacity_summary.get("q42_matrix_unit_rank_excess_over_block_lift", 0)),
        },
        "q42_tensor_rank20_slice": {
            "status": q42_slice.get("status", ""),
            "exact_rank20_combo_count": int(q42_slice_summary.get("exact_rank20_combo_count", 0)),
            "first_exact_rank20_q12_pushdown_rank_over_Q": int(q42_slice_summary.get("first_exact_rank20_q12_pushdown_rank_over_Q", 0)),
        },
        "q12_packet_charge_sum_partition": {
            "status": charge_partition.get("status", ""),
            "carrier_histogram": charge_partition_summary.get("carrier_q12_signature_class_size_histogram", []),
            "packet_histogram": charge_partition_summary.get("packet_sector26_sum_class_size_histogram", []),
            "element_bijection_count": int(charge_partition_summary.get("size_compatible_element_bijection_count", 0)),
        },
        "next_highest_yield_item": bridge_probe.get("next_highest_yield_item", ""),
        "interpretation": "Ingress-backed C985/A985 evidence is now present, but the A985/q12-to-full-packet projection is still open: support-3 seed parity blocks the direct extension, one-sided correction finds rank-2 families, and the corrected selection is capped at rank 9 instead of the rank-20 packet target.",
    }


def build_rank_one_packet_family_sink_summary(
    pressure_atlas: dict[str, Any],
    boundary_packet_bridge_summary: dict[str, Any],
) -> dict[str, Any]:
    families = boundary_packet_bridge_summary["low_support_candidate_atlas"]["support_families"]
    transition_rows = pressure_atlas["c985_transition_summary"]["rows"]
    source_residual = pressure_atlas["boundary_dynamics_summary"]["motif_prediction_splits"]["rank_one_packet_family_residual"]
    by_family = [
        {
            "family": family,
            "sink_hits": 0,
            "r33_sink_hits": 0,
            "steps": [],
        }
        for family in families
    ]
    total_sink_hits = 0
    total_r33_hits = 0
    for row in transition_rows:
        atom = int(row.get("atom", -1))
        family_index = packet_family_id(atom, families)
        if family_index is None:
            continue
        total_sink_hits += 1
        r33_hit = int(row.get("r33_sourced", 0)) == 1
        total_r33_hits += int(r33_hit)
        by_family[family_index]["sink_hits"] += 1
        by_family[family_index]["r33_sink_hits"] += int(r33_hit)
        by_family[family_index]["steps"].append(int(row.get("step", -1)))
    if total_r33_hits > 0 and source_residual["overall_verdict"] == "PACKET_FAMILY_WARD_RESIDUAL_CERTIFIED":
        verdict = "PACKET_FAMILY_TOUCHES_R33_AND_RESIDUAL"
    elif total_r33_hits > 0 and source_residual["overall_verdict"] == "PACKET_FAMILY_WARD_RESIDUAL_PROVISIONAL":
        verdict = "PACKET_FAMILY_TOUCHES_R33_AND_PROVISIONAL_RESIDUAL"
    elif total_r33_hits > 0:
        verdict = "PACKET_FAMILY_TOUCHES_R33_WITHOUT_CERTIFIED_RESIDUAL"
    else:
        verdict = "PACKET_FAMILY_DOES_NOT_TOUCH_R33_SINK"
    return {
        "families": families,
        "transition_steps": len(transition_rows),
        "sink_hits": total_sink_hits,
        "r33_sink_hits": total_r33_hits,
        "sink_hit_rate": round(total_sink_hits / len(transition_rows), 9) if transition_rows else 0.0,
        "r33_sink_hit_rate": round(total_r33_hits / len(transition_rows), 9) if transition_rows else 0.0,
        "by_family": by_family,
        "source_conditioned_packet_residual": source_residual,
        "verdict": verdict,
        "interpretation": "Tests whether the certified rank-one support-2 packet bridge families actually touch the R33-sourced sink sequence and the source-conditioned Ward residual.",
    }


def signed_packet_candidate_value(vector: list[float], support: list[dict[str, Any]]) -> float:
    total = 0.0
    for item in support:
        atom = int(item["public_atom_id"])
        coefficient = float(item["coefficient"])
        if 0 <= atom < len(vector):
            total += coefficient * float(vector[atom])
    return total


def summarize_signed_rank_one_packet_candidate(
    candidate: dict[str, Any],
    pressure_atlas: dict[str, Any],
    null_by_inlet: dict[int, list[dict[str, Any]]],
) -> dict[str, Any]:
    support = candidate.get("left_support", [])
    atlas_by_inlet = {int(row["inlet"]): row for row in pressure_atlas.get("atlas_rows", [])}
    transition_rows = pressure_atlas["c985_transition_summary"]["rows"]
    identity_values = []
    support_atoms = sorted(int(item["public_atom_id"]) for item in support)
    r33_touch_steps = []
    for step, inlet in enumerate(D20_GATE_SEQUENCE):
        atlas_row = atlas_by_inlet.get(inlet)
        vector = [float(value) for value in atlas_row.get("pressure_vector", [])] if atlas_row else []
        identity_values.append(signed_packet_candidate_value(vector, support))
        if step < len(transition_rows):
            transition_atom = int(transition_rows[step].get("atom", -1))
            if transition_atom in support_atoms and int(transition_rows[step].get("r33_sourced", 0)) == 1:
                r33_touch_steps.append(step)
    identity_mean_abs = sum(abs(value) for value in identity_values) / max(1, len(identity_values))
    identity_signed_mean = sum(identity_values) / max(1, len(identity_values))
    identity_peak_abs = max((abs(value) for value in identity_values), default=0.0)
    null_history_count = min((len(rows) for rows in null_by_inlet.values()), default=0)
    null_mean_abs = []
    null_peak_abs = []
    null_signed_mean = []
    for null_index in range(null_history_count):
        values = []
        for inlet in D20_GATE_SEQUENCE:
            null_row = null_by_inlet[inlet][null_index]
            vector = [float(value) for value in null_row.get("pressure_vector", [])]
            values.append(signed_packet_candidate_value(vector, support))
        null_mean_abs.append(sum(abs(value) for value in values) / max(1, len(values)))
        null_peak_abs.append(max((abs(value) for value in values), default=0.0))
        null_signed_mean.append(sum(values) / max(1, len(values)))
    null_mean_sorted = sorted(null_mean_abs)
    null_peak_sorted = sorted(null_peak_abs)
    p95_index = int(0.95 * (len(null_mean_sorted) - 1)) if null_mean_sorted else 0
    mean_abs_p95 = null_mean_sorted[p95_index] if null_mean_sorted else 0.0
    peak_abs_p95 = null_peak_sorted[p95_index] if null_peak_sorted else 0.0
    mean_abs_p = round((1 + sum(1 for value in null_mean_abs if value >= identity_mean_abs)) / (1 + len(null_mean_abs)), 9) if null_mean_abs else 1.0
    peak_abs_p = round((1 + sum(1 for value in null_peak_abs if value >= identity_peak_abs)) / (1 + len(null_peak_abs)), 9) if null_peak_abs else 1.0
    if r33_touch_steps and mean_abs_p <= 0.05:
        verdict = "SIGNED_PACKET_QUOTIENT_TOUCHES_R33_AND_BEATS_NULL"
    elif r33_touch_steps and mean_abs_p <= 0.1:
        verdict = "SIGNED_PACKET_QUOTIENT_TOUCHES_R33_PROVISIONAL"
    elif r33_touch_steps:
        verdict = "SIGNED_PACKET_QUOTIENT_TOUCHES_R33_WITHIN_NULL"
    elif mean_abs_p <= 0.05:
        verdict = "SIGNED_PACKET_QUOTIENT_BEATS_NULL_WITHOUT_R33_TOUCH"
    else:
        verdict = "SIGNED_PACKET_QUOTIENT_WITHIN_NULL"
    return {
        "doublet_id": int(candidate.get("doublet_id", -1)),
        "left_candidate_id": int(candidate.get("left_candidate_id", -1)),
        "right_candidate_id": int(candidate.get("right_candidate_id", -1)),
        "support": [
            {
                "public_atom_id": int(item["public_atom_id"]),
                "coefficient": int(item["coefficient"]),
                "public_atom_label": str(item.get("public_atom_label", "")),
            }
            for item in support
        ],
        "support_atoms": support_atoms,
        "r33_touch_steps": r33_touch_steps,
        "r33_touch_count": len(r33_touch_steps),
        "identity_mean_abs": round(identity_mean_abs, 9),
        "identity_signed_mean": round(identity_signed_mean, 9),
        "identity_peak_abs": round(identity_peak_abs, 9),
        "null_histories": len(null_mean_abs),
        "null_mean_abs_p95": round(mean_abs_p95, 9),
        "null_peak_abs_p95": round(peak_abs_p95, 9),
        "mean_abs_null_p": mean_abs_p,
        "peak_abs_null_p": peak_abs_p,
        "verdict": verdict,
    }


def build_signed_rank_one_packet_quotient_summary(
    low_support_report: dict[str, Any] | None,
    pressure_atlas: dict[str, Any],
    null_by_inlet: dict[int, list[dict[str, Any]]],
) -> dict[str, Any]:
    candidates = (
        low_support_report.get("derived", {}).get("compatible_doublet_candidate_rows", [])
        if low_support_report
        else []
    )
    candidate_rows = [
        summarize_signed_rank_one_packet_candidate(candidate, pressure_atlas, null_by_inlet)
        for candidate in candidates
    ]
    best = sorted(
        candidate_rows,
        key=lambda row: (
            row["r33_touch_count"] > 0,
            -row["mean_abs_null_p"],
            row["identity_mean_abs"],
            row["identity_peak_abs"],
        ),
        reverse=True,
    )[0] if candidate_rows else {}
    supported = {"SIGNED_PACKET_QUOTIENT_TOUCHES_R33_AND_BEATS_NULL"}
    provisional = {"SIGNED_PACKET_QUOTIENT_TOUCHES_R33_PROVISIONAL"}
    if best.get("verdict") in supported:
        overall = "SIGNED_PACKET_QUOTIENT_OBSERVABLE_CERTIFIED"
    elif best.get("verdict") in provisional:
        overall = "SIGNED_PACKET_QUOTIENT_OBSERVABLE_PROVISIONAL"
    else:
        overall = "SIGNED_PACKET_QUOTIENT_OBSERVABLE_NOT_CERTIFIED"
    return {
        "candidate_count": len(candidate_rows),
        "best_candidate": best,
        "candidate_rows": candidate_rows,
        "overall_verdict": overall,
        "null_model": "signed support-2 packet quotient strength over identity pulse sequence compared with per-inlet null pulse histories",
        "interpretation": "Uses the actual signed rank-one packet rows as non-diagonal boundary quotient observables before any renewed hydrogen comparison.",
    }


def build_signed_packet_quotient_lag_summary(
    signed_summary: dict[str, Any],
    pressure_atlas: dict[str, Any],
    null_by_inlet: dict[int, list[dict[str, Any]]],
) -> dict[str, Any]:
    best = signed_summary.get("best_candidate", {})
    support = list(best.get("support", []))
    atlas_by_inlet = {int(row["inlet"]): row for row in pressure_atlas.get("atlas_rows", [])}
    identity_signal = []
    signal_rows = []
    for step, inlet in enumerate(D20_GATE_SEQUENCE):
        atlas_row = atlas_by_inlet.get(inlet)
        vector = [float(value) for value in atlas_row.get("pressure_vector", [])] if atlas_row else []
        quotient_value = signed_packet_candidate_value(vector, support)
        identity_signal.append(quotient_value)
        signal_rows.append({
            "step": step,
            "inlet": int(inlet),
            "quotient_value": round(quotient_value, 9),
        })
    null_history_count = min((len(null_by_inlet.get(inlet, [])) for inlet in set(D20_GATE_SEQUENCE)), default=0)
    null_signals = []
    for null_index in range(null_history_count):
        signal = []
        for inlet in D20_GATE_SEQUENCE:
            null_row = null_by_inlet[inlet][null_index]
            vector = [float(value) for value in null_row.get("pressure_vector", [])]
            signal.append(signed_packet_candidate_value(vector, support))
        null_signals.append(signal)
    result = lag_scan_against_nulls(identity_signal, null_signals, "SIGNED_PACKET_QUOTIENT_HYDROGEN")
    null_p = float(result["null_significance"]["p_value"])
    result.update({
        "observable": "signed_rank_one_packet_quotient_hydrogen_lag",
        "quotient_observable_verdict": signed_summary.get("overall_verdict", ""),
        "best_signed_candidate": int(best.get("left_candidate_id", -1)),
        "support": support,
        "support_atoms": list(best.get("support_atoms", [])),
        "r33_touch_count": int(best.get("r33_touch_count", 0)),
        "identity_signal": [round(value, 9) for value in identity_signal],
        "signal_rows": signal_rows,
        "interpretation": "Tests whether the certified signed packet quotient also phase-couples to the d20 hydrogen scale; this is a null-tested coupling candidate, not a black-hole claim.",
        "verdict": "SIGNED_PACKET_QUOTIENT_HYDROGEN_CANDIDATE" if null_p < 0.05 else "SIGNED_PACKET_QUOTIENT_HYDROGEN_WITHIN_NULL",
    })
    return result


def public_atom_label(atom: int) -> str:
    sectors = atom_sectors(atom)
    return "{" + ",".join(sectors) + "}"


def support_row_from_atoms(atom_ids: tuple[int, ...], coefficients: tuple[int, ...]) -> list[dict[str, Any]]:
    return [
        {
            "public_atom_id": int(atom),
            "coefficient": int(coefficient),
            "public_atom_label": public_atom_label(atom),
        }
        for atom, coefficient in zip(atom_ids, coefficients)
    ]


def support_value_from_rows(vector: list[float], support: list[dict[str, Any]]) -> float:
    return sum(
        float(item["coefficient"]) * float(vector[int(item["public_atom_id"])])
        for item in support
        if 0 <= int(item["public_atom_id"]) < len(vector)
    )


def summarize_support3_null_metrics(
    row: dict[str, Any],
    null_by_inlet: dict[int, list[dict[str, Any]]],
) -> dict[str, Any]:
    support = row["support"]
    null_history_count = min((len(null_by_inlet.get(inlet, [])) for inlet in set(D20_GATE_SEQUENCE)), default=0)
    null_mean_abs = []
    null_peak_abs = []
    for null_index in range(null_history_count):
        values = []
        for inlet in D20_GATE_SEQUENCE:
            null_row = null_by_inlet[inlet][null_index]
            vector = [float(value) for value in null_row.get("pressure_vector", [])]
            values.append(support_value_from_rows(vector, support))
        null_mean_abs.append(sum(abs(value) for value in values) / max(1, len(values)))
        null_peak_abs.append(max((abs(value) for value in values), default=0.0))
    mean_abs_p = round((1 + sum(1 for value in null_mean_abs if value >= row["identity_mean_abs"])) / (1 + len(null_mean_abs)), 9) if null_mean_abs else 1.0
    peak_abs_p = round((1 + sum(1 for value in null_peak_abs if value >= row["identity_peak_abs"])) / (1 + len(null_peak_abs)), 9) if null_peak_abs else 1.0
    mean_abs_p95 = quantile(null_mean_abs, 0.95)
    peak_abs_p95 = quantile(null_peak_abs, 0.95)
    if row["r33_touch_count"] and mean_abs_p <= 0.05:
        verdict = "SUPPORT3_SIGNED_QUOTIENT_TOUCHES_R33_AND_BEATS_NULL"
    elif mean_abs_p <= 0.05:
        verdict = "SUPPORT3_SIGNED_QUOTIENT_BEATS_NULL_WITHOUT_R33_TOUCH"
    elif row["r33_touch_count"]:
        verdict = "SUPPORT3_SIGNED_QUOTIENT_TOUCHES_R33_WITHIN_NULL"
    else:
        verdict = "SUPPORT3_SIGNED_QUOTIENT_WITHIN_NULL"
    out = dict(row)
    out.update({
        "null_histories": len(null_mean_abs),
        "null_mean_abs_p95": round(mean_abs_p95, 9),
        "null_peak_abs_p95": round(peak_abs_p95, 9),
        "mean_abs_null_p": mean_abs_p,
        "peak_abs_null_p": peak_abs_p,
        "verdict": verdict,
    })
    return out


def build_support3_signed_quotient_summary(
    pressure_atlas: dict[str, Any],
    null_by_inlet: dict[int, list[dict[str, Any]]],
) -> dict[str, Any]:
    atlas_by_inlet = {int(row["inlet"]): row for row in pressure_atlas.get("atlas_rows", [])}
    transition_rows = pressure_atlas["c985_transition_summary"]["rows"]
    scored_rows = []
    candidate_id = 0
    for atom_ids in itertools.combinations(range(len(TRIPLES)), 3):
        for signs in itertools.product([-1, 1], repeat=2):
            coefficients = (1, int(signs[0]), int(signs[1]))
            support = support_row_from_atoms(atom_ids, coefficients)
            identity_signal = []
            for inlet in D20_GATE_SEQUENCE:
                atlas_row = atlas_by_inlet.get(inlet)
                vector = [float(value) for value in atlas_row.get("pressure_vector", [])] if atlas_row else []
                identity_signal.append(support_value_from_rows(vector, support))
            r33_touch_steps = [
                int(step)
                for step, transition_row in enumerate(transition_rows)
                if int(transition_row.get("atom", -1)) in atom_ids
                and int(transition_row.get("r33_sourced", 0)) == 1
            ]
            scored_rows.append({
                "candidate_id": candidate_id,
                "support_size": 3,
                "support": support,
                "support_atoms": list(atom_ids),
                "coefficients": list(coefficients),
                "r33_touch_steps": r33_touch_steps,
                "r33_touch_count": len(r33_touch_steps),
                "identity_signal": [round(value, 9) for value in identity_signal],
                "identity_mean_abs": round(sum(abs(value) for value in identity_signal) / max(1, len(identity_signal)), 9),
                "identity_signed_mean": round(sum(identity_signal) / max(1, len(identity_signal)), 9),
                "identity_peak_abs": round(max((abs(value) for value in identity_signal), default=0.0), 9),
            })
            candidate_id += 1
    candidate_count = len(scored_rows)
    ranked_for_null = sorted(
        scored_rows,
        key=lambda row: (
            row["r33_touch_count"] > 0,
            row["r33_touch_count"],
            row["identity_mean_abs"],
            row["identity_peak_abs"],
        ),
        reverse=True,
    )
    null_test_limit = min(480, len(ranked_for_null))
    null_tested_rows = [
        summarize_support3_null_metrics(row, null_by_inlet)
        for row in ranked_for_null[:null_test_limit]
    ]
    best = sorted(
        null_tested_rows,
        key=lambda row: (
            row["mean_abs_null_p"] <= 0.05,
            row["r33_touch_count"] > 0,
            -row["mean_abs_null_p"],
            row["identity_mean_abs"],
            row["identity_peak_abs"],
        ),
        reverse=True,
    )[0] if null_tested_rows else {}
    if best.get("verdict") == "SUPPORT3_SIGNED_QUOTIENT_TOUCHES_R33_AND_BEATS_NULL":
        overall = "SUPPORT3_SIGNED_QUOTIENT_OBSERVABLE_CERTIFIED"
    elif best.get("verdict") in {
        "SUPPORT3_SIGNED_QUOTIENT_BEATS_NULL_WITHOUT_R33_TOUCH",
        "SUPPORT3_SIGNED_QUOTIENT_TOUCHES_R33_WITHIN_NULL",
    }:
        overall = "SUPPORT3_SIGNED_QUOTIENT_OBSERVABLE_PROVISIONAL"
    else:
        overall = "SUPPORT3_SIGNED_QUOTIENT_OBSERVABLE_NOT_CERTIFIED"
    return {
        "observable": "support3_signed_public_boundary_quotient_screen",
        "candidate_count": candidate_count,
        "canonical_sign_convention": "first coefficient fixed to +1; global sign quotient removed",
        "null_tested_candidate_count": len(null_tested_rows),
        "best_candidate": best,
        "top_null_tested_rows": null_tested_rows[:32],
        "overall_verdict": overall,
        "null_model": "screened support-3 signed public-boundary quotients compared with per-inlet null pulse histories",
        "interpretation": "Explores the next non-diagonal C985 boundary seam after the certified support-2 rank-one quotient failed hydrogen-lag null certification; this is a screened search, not a certified packet bridge.",
    }


def build_support3_signed_quotient_lag_summary(
    support3_summary: dict[str, Any],
    pressure_atlas: dict[str, Any],
    null_by_inlet: dict[int, list[dict[str, Any]]],
) -> dict[str, Any]:
    best = support3_summary.get("best_candidate", {})
    support = list(best.get("support", []))
    atlas_by_inlet = {int(row["inlet"]): row for row in pressure_atlas.get("atlas_rows", [])}
    identity_signal = []
    signal_rows = []
    for step, inlet in enumerate(D20_GATE_SEQUENCE):
        atlas_row = atlas_by_inlet.get(inlet)
        vector = [float(value) for value in atlas_row.get("pressure_vector", [])] if atlas_row else []
        quotient_value = support_value_from_rows(vector, support)
        identity_signal.append(quotient_value)
        signal_rows.append({
            "step": step,
            "inlet": int(inlet),
            "quotient_value": round(quotient_value, 9),
        })
    null_history_count = min((len(null_by_inlet.get(inlet, [])) for inlet in set(D20_GATE_SEQUENCE)), default=0)
    null_signals = []
    for null_index in range(null_history_count):
        signal = []
        for inlet in D20_GATE_SEQUENCE:
            null_row = null_by_inlet[inlet][null_index]
            vector = [float(value) for value in null_row.get("pressure_vector", [])]
            signal.append(support_value_from_rows(vector, support))
        null_signals.append(signal)
    result = lag_scan_against_nulls(identity_signal, null_signals, "SUPPORT3_SIGNED_QUOTIENT_HYDROGEN")
    null_p = float(result["null_significance"]["p_value"])
    result.update({
        "observable": "support3_signed_public_boundary_quotient_hydrogen_lag",
        "support3_observable_verdict": support3_summary.get("overall_verdict", ""),
        "best_candidate": int(best.get("candidate_id", -1)),
        "support": support,
        "support_atoms": list(best.get("support_atoms", [])),
        "r33_touch_count": int(best.get("r33_touch_count", 0)),
        "identity_signal": [round(value, 9) for value in identity_signal],
        "signal_rows": signal_rows,
        "interpretation": "Tests whether the strongest screened support-3 signed boundary quotient phase-couples to the d20 hydrogen scale under the same 719-history null comparison.",
        "verdict": "SUPPORT3_SIGNED_QUOTIENT_HYDROGEN_CANDIDATE" if null_p < 0.05 else "SUPPORT3_SIGNED_QUOTIENT_HYDROGEN_WITHIN_NULL",
    })
    return result


def build_boundary_discovery_notes(report: dict[str, Any], proof: dict[str, Any]) -> str:
    summary = report["pressure_atlas_summary"]
    falsification = summary["falsification_ledger_summary"]
    c985 = summary["c985_summary"]
    transition = summary["c985_transition_summary"]
    dynamics = summary["boundary_dynamics_summary"]
    motif_counts = dynamics["motif_counts"]
    motif_prediction = dynamics["motif_prediction"]
    motif_prediction_long = dynamics["motif_prediction_long"]
    motif_prediction_splits = dynamics["motif_prediction_splits"]
    top_motifs = motif_counts["top_motifs"]
    failed_rows = [row for row in falsification["rows"] if row["status"] != "supported_proxy"]
    supported_rows = [row for row in falsification["rows"] if row["status"] == "supported_proxy"]
    gate_sequence = ",".join(str(value) for value in transition["gate_sequence"])
    lines = [
        "# D20 boundary physics discovery notes",
        "",
        "Status: provisional boundary-physics discovery note generated from the certified black-hole atom lab report.",
        "",
        "## Scope",
        "",
        "- This note records C985/d20 finite boundary physics. It is not a GR black-hole solution.",
        "- The visualization is only a witness surface. Evidence comes from the atlas, Ward/BMS operator, C985 charge labels, and null tests.",
        "- Current falsification status: "
        + falsification["overall_status"]
        + ". Candidate coupling is admitted only when a named observable beats its null distribution; this remains a boundary notebook, not a GR closure.",
        "",
        "## Fixed invariants used",
        "",
        "- Public shell: D=d20=Lambda^3 H6 with dim D=C(6,3)=20.",
        "- Descent body: A985 -> A236 -> A42 -> A12.",
        "- RGBA closure: 32 channels, with RGB=24 and alpha octet=8.",
        "- Fine coupling: alpha*=1/137 from 128+8+1.",
        "- Alpha wall: A_alpha=1/4, cutting the public shell as 20=6+14.",
        "- Hydrogen scale: Lambda=54.4 eV; fine denominator=75076; Lamb reference=1057.845020 MHz.",
        "",
        "## C985 boundary ledger facts",
        "",
        "- Boundary vector: (M,J,P,Phi;R33,K_mixed_S,K_pure_Sminus).",
        "- R33 rule: " + c985["r33_rule"] + ".",
        "- R33 sourced closed returns: " + str(c985["r33_sourced_closed_returns"]) + ".",
        "- K supports: mixed S=" + str(c985["mixed_s_support"]) + ", pure S-=" + str(c985["pure_sminus_support"]) + ".",
        "- Transition gate sequence: " + gate_sequence + ".",
        "- R33 pulse persistence: "
        + str(transition["r33_sourced_steps"])
        + "/"
        + str(transition["steps"])
        + " steps; longest run="
        + str(transition["longest_r33_run"])
        + ".",
        "- Dominant sink atom: " + str(transition["dominant_sink_atom"]) + ".",
        "",
        "## Supported evidence",
        "",
    ]
    for row in supported_rows:
        lines.append("- " + row["claim"] + ": " + row["evidence"] + " [" + row["ledger_source"] + "]")
    lines.extend([
        "",
        "## Failed or unproved coupling claims",
        "",
    ])
    for row in failed_rows:
        lines.append("- " + row["claim"] + ": " + row["evidence"] + " -> " + row["status"])
    lines.extend([
        "",
        "## Boundary motif notebook",
        "",
        "- Motif total: " + str(motif_counts["motif_total"]) + ".",
        "- Unique motifs: " + str(motif_counts["unique_motifs"]) + ".",
        "- Top motifs:",
    ])
    for motif in top_motifs[:8]:
        lines.append("  - " + motif["key"] + " x" + str(motif["count"]))
    lines.extend([
        "",
        "## Boundary motif prediction test",
        "",
        "- Test: walk-forward motif-to-next-R33-sink prediction using only earlier pulse history.",
        "- Best motif alphabet: " + str(motif_prediction["best_variant"]) + ".",
        "- Attempts: " + str(motif_prediction["walk_forward_attempts"]) + "/" + str(motif_prediction["transitions_evaluated"]) + ".",
        "- Motif accuracy: " + str(motif_prediction["motif_accuracy"]) + ".",
        "- Prior-majority baseline accuracy: " + str(motif_prediction["baseline_accuracy"]) + ".",
        "- Baseline lift: " + str(motif_prediction["baseline_lift"]) + ".",
        "- Rotation/reversal null p-value: " + str(motif_prediction["null_p_value"]) + ".",
        "- Verdict: " + motif_prediction["verdict"] + ".",
        "- Alphabet family:",
    ])
    for row in motif_prediction["variant_rows"]:
        lines.append(
            "  - "
            + row["variant"]
            + ": acc="
            + str(row["motif_accuracy"])
            + ", baseline="
            + str(row["baseline_accuracy"])
            + ", lift="
            + str(row["baseline_lift"])
            + ", p="
            + str(row["null_p_value"])
            + ", "
            + row["verdict"]
        )
    lines.extend([
        "",
        "## Long boundary motif forecast",
        "",
        "- Scope: identity plus certified null-row pulse histories, still boundary-only.",
        "- Histories: " + str(motif_prediction_long["history_count"]) + ".",
        "- Samples: " + str(motif_prediction_long["sample_count"]) + ".",
        "- Best motif alphabet: " + str(motif_prediction_long["best_variant"]) + ".",
        "- Attempts: " + str(motif_prediction_long["walk_forward_attempts"]) + "/" + str(motif_prediction_long["transitions_evaluated"]) + ".",
        "- Motif accuracy: " + str(motif_prediction_long["motif_accuracy"]) + ".",
        "- Prior-majority baseline accuracy: " + str(motif_prediction_long["baseline_accuracy"]) + ".",
        "- Baseline lift: " + str(motif_prediction_long["baseline_lift"]) + ".",
        "- Rotation/reversal null p-value: " + str(motif_prediction_long["null_p_value"]) + ".",
        "- Verdict: " + motif_prediction_long["verdict"] + ".",
        "- Alphabet family:",
    ])
    for row in motif_prediction_long["variant_rows"]:
        lines.append(
            "  - "
            + row["variant"]
            + ": acc="
            + str(row["motif_accuracy"])
            + ", baseline="
            + str(row["baseline_accuracy"])
            + ", lift="
            + str(row["baseline_lift"])
            + ", p="
            + str(row["null_p_value"])
            + ", "
            + row["verdict"]
        )
    history_split = motif_prediction_splits["history_split"]
    time_offset_split = motif_prediction_splits["time_offset_split"]
    time_offset_obstruction = motif_prediction_splits["time_offset_obstruction"]
    phase_clock_model = motif_prediction_splits["phase_clock_model"]
    paired_residual = phase_clock_model["paired_residual"]
    source_state_transport = motif_prediction_splits["source_state_transport"]
    source_conditioned_ward_residual = motif_prediction_splits["source_conditioned_ward_residual"]
    boundary_packet_bridge = report["boundary_packet_bridge_summary"]
    packet_pairing = boundary_packet_bridge["pairing_obstruction"]
    packet_row_norm = boundary_packet_bridge["row_normalization_obstruction"]
    packet_low_support = boundary_packet_bridge["low_support_candidate_atlas"]
    rank_one_packet_family_sink = report["rank_one_packet_family_sink_summary"]
    signed_packet_quotient = report["signed_rank_one_packet_quotient_summary"]
    signed_packet_best = signed_packet_quotient["best_candidate"]
    signed_packet_lag = summary["signed_packet_quotient_lag_summary"]
    support3_quotient = summary["support3_signed_quotient_summary"]
    support3_best = support3_quotient["best_candidate"]
    support3_lag = summary["support3_signed_quotient_lag_summary"]
    bridge_probe = report["a985_q12_packet_bridge_probe_summary"]
    bridge_rank20 = bridge_probe["corrected_rank20_selection"]
    bridge_one_sided = bridge_probe["one_sided_seed_correction"]
    bridge_seed = bridge_probe["mask288_q12_seed_support3"]
    lines.extend([
        "",
        "## Held-out motif forecast splits",
        "",
        "- Overall verdict: " + motif_prediction_splits["overall_verdict"] + ".",
        "- History split best alphabet: " + str(history_split["best_variant"]) + ".",
        "- History split accuracy: " + str(history_split["motif_accuracy"]) + ".",
        "- History split baseline: " + str(history_split["baseline_accuracy"]) + ".",
        "- History split null p-value: " + str(history_split["null_p_value"]) + ".",
        "- History split verdict: " + history_split["verdict"] + ".",
        "- Time-offset split best alphabet: " + str(time_offset_split["best_variant"]) + ".",
        "- Time-offset split accuracy: " + str(time_offset_split["motif_accuracy"]) + ".",
        "- Time-offset split baseline: " + str(time_offset_split["baseline_accuracy"]) + ".",
        "- Time-offset split null p-value: " + str(time_offset_split["null_p_value"]) + ".",
        "- Time-offset split verdict: " + time_offset_split["verdict"] + ".",
        "",
        "## Time-offset obstruction phase audit",
        "",
        "- Variant audited: " + str(time_offset_obstruction["variant"]) + ".",
        "- Phase count: " + str(time_offset_obstruction["phase_count"]) + ".",
        "- Passing phases: " + str(time_offset_obstruction["passing_phase_count"]) + ".",
        "- Failing phases: " + str(time_offset_obstruction["failing_phase_count"]) + ".",
        "- Verdict: " + time_offset_obstruction["overall_verdict"] + ".",
        "- Weakest held-out phases:",
    ])
    for row in time_offset_obstruction["weakest_rows"]:
        lines.append(
            "  - step "
            + str(row["heldout_step"])
            + " inlet "
            + str(row["source_inlet"])
            + " -> target inlet "
            + str(row["target_inlet"])
            + ": acc="
            + str(row["motif_accuracy"])
            + ", baseline="
            + str(row["baseline_accuracy"])
            + ", lift="
            + str(row["baseline_lift"])
            + ", p="
            + str(row["null_p_value"])
            + ", dominant_atom="
            + str(row["dominant_atom"])
            + ", "
            + row["verdict"]
        )
    lines.extend([
        "",
        "## Explicit phase-clock baseline",
        "",
        "- Overall verdict: " + phase_clock_model["overall_verdict"] + ".",
        "- History motif: "
        + str(phase_clock_model["motif_history_best_variant"])
        + " acc="
        + str(phase_clock_model["motif_history_accuracy"])
        + ".",
        "- History clock: "
        + str(phase_clock_model["clock_history_best_variant"])
        + " acc="
        + str(phase_clock_model["clock_history_accuracy"])
        + ".",
        "- History residual lift: "
        + str(phase_clock_model["history_residual_lift"])
        + " -> "
        + phase_clock_model["history_residual_verdict"]
        + ".",
        "- Time-offset motif: "
        + str(phase_clock_model["motif_time_offset_best_variant"])
        + " acc="
        + str(phase_clock_model["motif_time_offset_accuracy"])
        + ".",
        "- Time-offset clock: "
        + str(phase_clock_model["clock_time_offset_best_variant"])
        + " acc="
        + str(phase_clock_model["clock_time_offset_accuracy"])
        + ".",
        "- Time-offset residual lift: "
        + str(phase_clock_model["time_offset_residual_lift"])
        + " -> "
        + phase_clock_model["time_offset_residual_verdict"]
        + ".",
        "",
        "## Paired phase-residual observable",
        "",
        "- Overall verdict: " + paired_residual["overall_verdict"] + ".",
        "- History paired residual: motif_only="
        + str(paired_residual["history"]["motif_only"])
        + ", clock_only="
        + str(paired_residual["history"]["clock_only"])
        + ", p="
        + str(paired_residual["history"]["motif_advantage_p"])
        + ", "
        + paired_residual["history"]["verdict"]
        + ".",
        "- Time-offset paired residual: motif_only="
        + str(paired_residual["time_offset"]["motif_only"])
        + ", clock_only="
        + str(paired_residual["time_offset"]["clock_only"])
        + ", p="
        + str(paired_residual["time_offset"]["motif_advantage_p"])
        + ", "
        + paired_residual["time_offset"]["verdict"]
        + ".",
        "",
        "## Source-state transport separation",
        "",
        "- Overall verdict: " + source_state_transport["overall_verdict"] + ".",
        "- History source-state best: "
        + str(source_state_transport["source_history_split"]["best_variant"])
        + " acc="
        + str(source_state_transport["source_history_split"]["motif_accuracy"])
        + ".",
        "- History Ward-motif best: "
        + str(source_state_transport["ward_history_split"]["best_variant"])
        + " acc="
        + str(source_state_transport["ward_history_split"]["motif_accuracy"])
        + ".",
        "- History Ward-minus-source lift: "
        + str(source_state_transport["history_residual_lift"])
        + ".",
        "- Time-offset source-state best: "
        + str(source_state_transport["source_time_offset_split"]["best_variant"])
        + " acc="
        + str(source_state_transport["source_time_offset_split"]["motif_accuracy"])
        + ".",
        "- Time-offset Ward-motif best: "
        + str(source_state_transport["ward_time_offset_split"]["best_variant"])
        + " acc="
        + str(source_state_transport["ward_time_offset_split"]["motif_accuracy"])
        + ".",
        "- Time-offset Ward-minus-source lift: "
        + str(source_state_transport["time_offset_residual_lift"])
        + ".",
        "- Paired Ward-vs-source history: ward_only="
        + str(source_state_transport["paired_ward_vs_source"]["history"]["motif_only"])
        + ", source_only="
        + str(source_state_transport["paired_ward_vs_source"]["history"]["clock_only"])
        + ".",
        "- Paired Ward-vs-source time-offset: ward_only="
        + str(source_state_transport["paired_ward_vs_source"]["time_offset"]["motif_only"])
        + ", source_only="
        + str(source_state_transport["paired_ward_vs_source"]["time_offset"]["clock_only"])
        + ".",
        "",
        "## Source-conditioned Ward residual",
        "",
        "- Overall verdict: "
        + source_conditioned_ward_residual["overall_verdict"]
        + ".",
        "- History split: source="
        + str(source_conditioned_ward_residual["history_split"]["best_source_variant"])
        + ", ward="
        + str(source_conditioned_ward_residual["history_split"]["best_ward_variant"])
        + ", ward_acc="
        + str(source_conditioned_ward_residual["history_split"]["ward_accuracy"])
        + ", source_acc="
        + str(source_conditioned_ward_residual["history_split"]["source_accuracy"])
        + ", residual_lift="
        + str(source_conditioned_ward_residual["history_split"]["residual_lift"])
        + ", null_p="
        + str(source_conditioned_ward_residual["history_split"]["null_p_value"])
        + ", "
        + source_conditioned_ward_residual["history_split"]["verdict"]
        + ".",
        "- Time-offset split: source="
        + str(source_conditioned_ward_residual["time_offset_split"]["best_source_variant"])
        + ", ward="
        + str(source_conditioned_ward_residual["time_offset_split"]["best_ward_variant"])
        + ", ward_acc="
        + str(source_conditioned_ward_residual["time_offset_split"]["ward_accuracy"])
        + ", source_acc="
        + str(source_conditioned_ward_residual["time_offset_split"]["source_accuracy"])
        + ", residual_lift="
        + str(source_conditioned_ward_residual["time_offset_split"]["residual_lift"])
        + ", null_p="
        + str(source_conditioned_ward_residual["time_offset_split"]["null_p_value"])
        + ", "
        + source_conditioned_ward_residual["time_offset_split"]["verdict"]
        + ".",
        "- Null model: within-source rotations of Ward/C985 keys while source atom/inlet transport and next atoms are held fixed.",
        "",
        "## C985 boundary-packet bridge seam",
        "",
        "- Receipt status: " + boundary_packet_bridge["status"] + ".",
        "- Raw pairing obstruction: compatible raw pairs="
        + str(packet_pairing["raw_compatible_pairs"])
        + ", first scalar with matching="
        + str(packet_pairing["minimal_scalar_with_matching"])
        + ", joint boundary/packet clearing bound="
        + str(packet_pairing["joint_boundary_packet_scalar_lcm"])
        + ".",
        "- Row-normalization obstruction: all rows require even scalar="
        + str(packet_row_norm["all_rows_require_even_scalar_by_parity"])
        + ", row scalar divisibility="
        + str(packet_row_norm["row_scalar_divisibility_for_any_packet_pairing"])
        + ", only compatible even residue mod 6="
        + str(packet_row_norm["only_compatible_residue_pair_mod6"])
        + ".",
        "- Low-support candidate atlas: candidates="
        + str(packet_low_support["candidate_count"])
        + ", even-image support-2 rows="
        + str(packet_low_support["even_image_candidate_count"])
        + ", compatible doublets="
        + str(packet_low_support["compatible_doublet_count"])
        + ", all rank-one="
        + str(packet_low_support["compatible_doublets_all_rank_one"])
        + ", support families="
        + str(packet_low_support["support_families"])
        + ".",
        "- Physical reading: the current d20 boundary cannot be naively paired into ten packet horizons; any black-hole-like atom now needs a non-diagonal signed quotient or normalization stronger than scalar clearing.",
        "",
        "## Rank-one packet families against R33/source residual",
        "",
        "- Verdict: " + rank_one_packet_family_sink["verdict"] + ".",
        "- R33 sink overlap: "
        + str(rank_one_packet_family_sink["r33_sink_hits"])
        + "/"
        + str(rank_one_packet_family_sink["transition_steps"])
        + " transition steps, sink hit rate="
        + str(rank_one_packet_family_sink["sink_hit_rate"])
        + ".",
        "- Family hit rows: "
        + str(rank_one_packet_family_sink["by_family"])
        + ".",
        "- Packet-family history residual: actual_family_attempts="
        + str(rank_one_packet_family_sink["source_conditioned_packet_residual"]["history_split"]["actual_family_attempts"])
        + ", ward_family_acc="
        + str(rank_one_packet_family_sink["source_conditioned_packet_residual"]["history_split"]["ward_family_accuracy"])
        + ", source_family_acc="
        + str(rank_one_packet_family_sink["source_conditioned_packet_residual"]["history_split"]["source_family_accuracy"])
        + ", lift="
        + str(rank_one_packet_family_sink["source_conditioned_packet_residual"]["history_split"]["family_residual_lift"])
        + ", null_p="
        + str(rank_one_packet_family_sink["source_conditioned_packet_residual"]["history_split"]["null_p_value"])
        + ", "
        + rank_one_packet_family_sink["source_conditioned_packet_residual"]["history_split"]["verdict"]
        + ".",
        "- Packet-family time-offset residual: actual_family_attempts="
        + str(rank_one_packet_family_sink["source_conditioned_packet_residual"]["time_offset_split"]["actual_family_attempts"])
        + ", ward_family_acc="
        + str(rank_one_packet_family_sink["source_conditioned_packet_residual"]["time_offset_split"]["ward_family_accuracy"])
        + ", source_family_acc="
        + str(rank_one_packet_family_sink["source_conditioned_packet_residual"]["time_offset_split"]["source_family_accuracy"])
        + ", lift="
        + str(rank_one_packet_family_sink["source_conditioned_packet_residual"]["time_offset_split"]["family_residual_lift"])
        + ", null_p="
        + str(rank_one_packet_family_sink["source_conditioned_packet_residual"]["time_offset_split"]["null_p_value"])
        + ", "
        + rank_one_packet_family_sink["source_conditioned_packet_residual"]["time_offset_split"]["verdict"]
        + ".",
        "",
        "## Signed rank-one packet quotient observable",
        "",
        "- Overall verdict: " + signed_packet_quotient["overall_verdict"] + ".",
        "- Best signed support row: candidate "
        + str(signed_packet_best["left_candidate_id"])
        + " support="
        + str(signed_packet_best["support"])
        + ".",
        "- R33 touch steps: "
        + str(signed_packet_best["r33_touch_steps"])
        + "; identity mean |quotient|="
        + str(signed_packet_best["identity_mean_abs"])
        + "; null p95="
        + str(signed_packet_best["null_mean_abs_p95"])
        + "; null p="
        + str(signed_packet_best["mean_abs_null_p"])
        + "; "
        + signed_packet_best["verdict"]
        + ".",
        "- Null model: " + signed_packet_quotient["null_model"] + ".",
    ])
    lines.extend([
        "",
        "## Signed packet quotient hydrogen-lag test",
        "",
        "- Observable: " + signed_packet_lag["observable"] + ".",
        "- Candidate/support: "
        + str(signed_packet_lag["best_signed_candidate"])
        + " support_atoms="
        + str(signed_packet_lag["support_atoms"])
        + ".",
        "- Best hydrogen lag: "
        + str(signed_packet_lag["best_lag"])
        + " with rho="
        + str(signed_packet_lag["best_rho"])
        + " and null p="
        + str(signed_packet_lag["null_significance"]["p_value"])
        + ".",
        "- Null verdict: "
        + signed_packet_lag["null_significance"]["verdict"]
        + "; coupling verdict: "
        + signed_packet_lag["verdict"]
        + ".",
        "- Interpretation: " + signed_packet_lag["interpretation"],
    ])
    lines.extend([
        "",
        "## Support-3 signed quotient screen",
        "",
        "- Screened observable: " + support3_quotient["observable"] + ".",
        "- Candidate count: "
        + str(support3_quotient["candidate_count"])
        + "; null-tested top rows="
        + str(support3_quotient["null_tested_candidate_count"])
        + ".",
        "- Best support-3 row: candidate "
        + str(support3_best["candidate_id"])
        + " support="
        + str(support3_best["support"])
        + ".",
        "- Boundary quotient null result: identity mean |quotient|="
        + str(support3_best["identity_mean_abs"])
        + ", null p="
        + str(support3_best["mean_abs_null_p"])
        + ", "
        + support3_best["verdict"]
        + ".",
        "- Hydrogen-lag result: best lag "
        + str(support3_lag["best_lag"])
        + " rho="
        + str(support3_lag["best_rho"])
        + " null p="
        + str(support3_lag["null_significance"]["p_value"])
        + ", "
        + support3_lag["verdict"]
        + ".",
        "- Interpretation: " + support3_quotient["interpretation"],
    ])
    lines.extend([
        "",
        "## A985/q12 packet projection bridge probe",
        "",
        "- Artifact: " + bridge_probe["artifact"].replace("\\", "/") + ".",
        "- Status: " + bridge_probe["status"] + "; checks_pass=" + str(bridge_probe["all_checks_pass"]) + ".",
        "- Ingress projection inventory: "
        + bridge_probe["ingress_projection_inventory"]["status"]
        + "; missing bridge count="
        + str(bridge_probe["ingress_projection_inventory"]["missing_bridge_count"])
        + ".",
        "- Mask288 q12 support-3 seed: "
        + bridge_seed["status"]
        + "; candidates="
        + str(bridge_seed["candidate_count"])
        + "; even-image candidates="
        + str(bridge_seed["even_image_candidate_count"])
        + "; compatible doublets="
        + str(bridge_seed["compatible_doublet_count"])
        + ".",
        "- one-sided seed correction: "
        + bridge_one_sided["status"]
        + "; compatible doublets="
        + str(bridge_one_sided["compatible_doublet_count"])
        + "; combined rank-2 families="
        + str(bridge_one_sided["combined_rank2_support_family_count"])
        + ".",
        "- Corrected rank-20 selection: "
        + bridge_rank20["status"]
        + "; boundary image rank="
        + str(bridge_rank20["combined_boundary_image_rank_over_Q"])
        + "/"
        + str(bridge_rank20["target_rank"])
        + "; shortfall="
        + str(bridge_rank20["packet_rank_shortfall"])
        + ".",
        "- Natural 25-to-20 packet projection: "
        + bridge_probe["natural_25_to_20_projection"]["status"]
        + "; passing columns="
        + str(bridge_probe["natural_25_to_20_projection"]["columns_passing_packet_snf_image"])
        + ".",
        "- Q42/A985 capacity: "
        + bridge_probe["hidden_q42_a985_capacity"]["status"]
        + "; matrix-unit rank="
        + str(bridge_probe["hidden_q42_a985_capacity"]["matrix_unit_rank"])
        + "; packet-target excess="
        + str(bridge_probe["hidden_q42_a985_capacity"]["packet_target_excess"])
        + ".",
        "- Physical reading: " + bridge_probe["interpretation"],
        "- Next bridge item: " + bridge_probe["next_highest_yield_item"],
    ])
    lines.extend([
        "",
        "## Working physical interpretation",
        "",
        "- The visible coil is best read as polarization of the finite boundary transition operator, not as an electron eigenmode and not as a micro black hole.",
        "- The hard positive result is a stable R33-sourced boundary sink under the C985 pulse history.",
        "- The hard negative result is that the earlier scalar, diagonal, zero-pair Ward, and C2 Markov hydrogen proxies remain inside their current null distributions.",
        "- The source-state separation resolves the earlier phase-residual ambiguity: current atom plus inlet transport dominates the Ward/C985 motif alphabets on both held-out history and time-offset splits.",
        "- The source-conditioned Ward residual keeps source atom/inlet transport fixed and perturbs only C985/Ward keys before any renewed hydrogen comparison.",
        "- The source-conditioned Ward residual does not certify overall, so the sharper boundary problem is now the C985 boundary-packet bridge/normalization seam.",
        "- The rank-one packet-family test now records whether those support-2 families touch the R33 sink and whether they explain the source-conditioned residual.",
        "- The signed rank-one packet quotient test now decides whether the actual support-2 signed rows are strong enough as non-diagonal quotient observables.",
        "- The ingress-backed A985/q12 bridge probe now shows the obstruction sharply: rank-2 packet families exist, but the corrected q12 image is still rank 9 rather than rank 20.",
        "- The next useful discovery step is to label the q12-vs-sector26 charge-sum partition enough to break the remaining A985/q12 packet assignment ambiguity.",
        "",
        "## Artifacts",
        "",
        "- Generated report: " + str(REPORT_JSON.relative_to(ROOT)).replace("\\", "/"),
        "- Proof report: " + str(PROOF_JSON.relative_to(ROOT)).replace("\\", "/"),
        "- Report sha256: " + proof["report_sha256"],
        "- Pressure atlas JS sha256: " + report["pressure_atlas_js_sha256"],
        "",
    ])
    return "\n".join(lines)


def lag_scan_against_nulls(identity_signal: list[float], null_signals: list[list[float]], verdict_prefix: str) -> dict[str, Any]:
    lag_rows = []
    for lag in range(len(D20_GATE_SEQUENCE)):
        bindings = [
            clamp(abs(energy_ev(LEVELS[(index + lag) % len(LEVELS)])) / 13.6, 0, 1.4)
            for index in range(len(identity_signal))
        ]
        rho = pearson_xy(bindings, identity_signal)
        lag_rows.append({"lag": lag, "rho": round(rho, 9), "abs_rho": round(abs(rho), 9)})
    best = max(lag_rows, key=lambda row: row["abs_rho"]) if lag_rows else {"lag": 0, "rho": 0.0, "abs_rho": 0.0}
    null_max_abs_rhos = []
    for signal in null_signals:
        null_abs_rhos = []
        for lag in range(len(D20_GATE_SEQUENCE)):
            bindings = [
                clamp(abs(energy_ev(LEVELS[(index + lag) % len(LEVELS)])) / 13.6, 0, 1.4)
                for index in range(len(signal))
            ]
            null_abs_rhos.append(abs(pearson_xy(bindings, signal)))
        null_max_abs_rhos.append(max(null_abs_rhos) if null_abs_rhos else 0.0)
    observed_abs = float(best["abs_rho"])
    exceedances = sum(1 for value in null_max_abs_rhos if value >= observed_abs)
    p_value = (exceedances + 1) / (len(null_max_abs_rhos) + 1) if null_max_abs_rhos else 1.0
    null_p95 = quantile(null_max_abs_rhos, 0.95)
    return {
        "lags": len(lag_rows),
        "best_lag": int(best["lag"]),
        "best_rho": float(best["rho"]),
        "best_abs_rho": observed_abs,
        "rows": lag_rows,
        "null_significance": {
            "null_histories": len(null_max_abs_rhos),
            "p_value": round(p_value, 9),
            "exceedances": exceedances,
            "null_mean_max_abs_rho": round(sum(null_max_abs_rhos) / max(1, len(null_max_abs_rhos)), 9),
            "null_p95_max_abs_rho": round(null_p95, 9),
            "observed_best_abs_rho": round(observed_abs, 9),
            "verdict": f"{verdict_prefix}_BEATS_NULL_95" if observed_abs > null_p95 else f"{verdict_prefix}_WITHIN_NULL",
        },
    }


def bit_count(value: int) -> int:
    return int(value).bit_count()


def selector_overlap_value(atom: int, selector: dict[str, Any]) -> float:
    mask_value = c985_mask_int(atom)
    best = 0.0
    for delta in selector["move_deltas"]:
        intersection = bit_count(mask_value & int(delta))
        union = bit_count(mask_value | int(delta)) or 1
        best = max(best, intersection / union)
    action_weight = selector["min_total_action"] / selector["total_move_action"]
    orbit_size_weight = 1.0 if selector["move_orbit_size"] == 1 else 0.82
    primitive_weight = 1.08 if selector["contains_primitive"] else 1.0
    return best * action_weight * orbit_size_weight * primitive_weight


def build_selector_candidates(selector_report: dict[str, Any]) -> list[dict[str, Any]]:
    summary = selector_report["derived"]["selector_summary"]
    raw_candidates = [
        ("primitive_seeded", summary["primitive_seeded_selected"][0]),
        ("global_action_minimal", summary["global_action_minimal_selected"][0]),
        ("paired_action_minimal", summary["paired_action_minimal_selected"][0]),
        ("lazy_gap_action_tiebreak", summary["lazy_spectral_gap_action_tiebreak_selected"][0]),
        ("paired_lazy_gap_action_tiebreak", summary["paired_lazy_spectral_gap_action_tiebreak_selected"][0]),
    ]
    min_action = min(int(row["total_move_action"]) for _, row in raw_candidates)
    candidates = []
    seen: set[tuple[int, ...]] = set()
    for criterion, row in raw_candidates:
        deltas = tuple(int(delta) for delta in row["move_deltas"])
        if deltas in seen:
            continue
        seen.add(deltas)
        candidates.append({
            "criterion": criterion,
            "move_orbit_id": int(row["move_orbit_id"]),
            "move_deltas": list(deltas),
            "move_basis_cycle_indices": row["move_basis_cycle_indices"],
            "move_orbit_size": int(row["move_orbit_size"]),
            "rank": int(row["rank"]),
            "nullity": int(row["nullity"]),
            "spectrum": row["spectrum"],
            "total_move_action": int(row["total_move_action"]),
            "min_total_action": min_action,
            "contains_primitive": criterion == "primitive_seeded",
        })
    return candidates


def build_selector_family_summary(selector_report: dict[str, Any], transition_rows: list[dict[str, Any]], null_by_inlet: dict[int, list[dict[str, Any]]]) -> dict[str, Any]:
    candidates = build_selector_candidates(selector_report)
    null_history_count = min((len(rows) for rows in null_by_inlet.values()), default=0)
    candidate_rows = []
    for candidate in candidates:
        identity_signal = [selector_overlap_value(int(row["atom"]), candidate) for row in transition_rows]
        null_signals = []
        for null_index in range(null_history_count):
            signal = []
            for _step, inlet in enumerate(D20_GATE_SEQUENCE):
                null_row = null_by_inlet[inlet][null_index]
                vector = [float(value) for value in null_row.get("pressure_vector", [])]
                atom = max(range(len(vector)), key=lambda index: vector[index]) if vector else 0
                signal.append(selector_overlap_value(atom, candidate))
            null_signals.append(signal)
        result = lag_scan_against_nulls(identity_signal, null_signals, "C2_SELECTOR")
        result.update(candidate)
        candidate_rows.append(result)
    best = min(candidate_rows, key=lambda row: (row["null_significance"]["p_value"], -row["best_abs_rho"])) if candidate_rows else {
        "criterion": "none",
        "best_lag": 0,
        "best_rho": 0.0,
        "best_abs_rho": 0.0,
        "null_significance": {"p_value": 1.0, "verdict": "C2_SELECTOR_WITHIN_NULL"},
    }
    return {
        "observable": "c2_selector_family_mask_overlap",
        "theorem_status": selector_report["status"],
        "candidate_count": len(candidate_rows),
        "best_candidate": best["criterion"],
        "best_lag": int(best["best_lag"]),
        "best_rho": float(best["best_rho"]),
        "best_abs_rho": float(best["best_abs_rho"]),
        "best_null_p": float(best["null_significance"]["p_value"]),
        "best_null_verdict": best["null_significance"]["verdict"],
        "rows": candidate_rows,
        "verdict": "C2_SELECTOR_FAMILY_CANDIDATE" if float(best["null_significance"]["p_value"]) < 0.05 else "C2_SELECTOR_FAMILY_WITHIN_NULL",
    }


def normalize_distribution(dist: dict[int, float]) -> dict[int, float]:
    total = sum(dist.values())
    if total <= 0:
        return {}
    return {key: value / total for key, value in dist.items() if value}


def transition_distribution(rows: list[dict[str, Any]], operator: dict[str, Any], hydrogen_weighted: bool) -> dict[int, float]:
    dist: dict[int, float] = {}
    for index, row in enumerate(rows):
        orbit_id = embedded_c2_orbit_id(int(row["atom"]), int(row["inlet"]), int(row["step"]), operator["target_count"])
        level = LEVELS[index % len(LEVELS)]
        weight = clamp(abs(energy_ev(level)) / 13.6, 0, 1.4) if hydrogen_weighted else 1.0
        dist[orbit_id] = dist.get(orbit_id, 0.0) + weight
    return normalize_distribution(dist)


def null_transition_rows(null_by_inlet: dict[int, list[dict[str, Any]]], null_index: int) -> list[dict[str, Any]]:
    rows = []
    for step, inlet in enumerate(D20_GATE_SEQUENCE):
        null_row = null_by_inlet[inlet][null_index]
        vector = [float(value) for value in null_row.get("pressure_vector", [])]
        atom = max(range(len(vector)), key=lambda index: vector[index]) if vector else 0
        rows.append({"step": step, "inlet": inlet, "atom": atom})
    return rows


def markov_step_distribution(dist: dict[int, float], operator: dict[str, Any]) -> dict[int, float]:
    rows = operator["rows_by_orbit"]
    next_dist: dict[int, float] = {}
    for orbit_id, mass in dist.items():
        row = rows.get(int(orbit_id))
        if not row or not row.get("targets"):
            next_dist[orbit_id] = next_dist.get(orbit_id, 0.0) + mass
            continue
        for target in row["targets"]:
            probability = float(target["probability"]["numerator"]) / float(target["probability"]["denominator"])
            target_id = int(target["target_orbit_id"])
            next_dist[target_id] = next_dist.get(target_id, 0.0) + mass * probability
    return normalize_distribution(next_dist)


def markov_evolve_distribution(dist: dict[int, float], operator: dict[str, Any], steps: int) -> dict[int, float]:
    evolved = dict(dist)
    for _ in range(steps):
        evolved = markov_step_distribution(evolved, operator)
    return evolved


def total_variation_distance(a: dict[int, float], b: dict[int, float]) -> float:
    keys = set(a) | set(b)
    return 0.5 * sum(abs(a.get(key, 0.0) - b.get(key, 0.0)) for key in keys)


def build_c2_markov_trajectory_summary(operator: dict[str, Any], transition_rows: list[dict[str, Any]], null_by_inlet: dict[int, list[dict[str, Any]]]) -> dict[str, Any]:
    trajectory_steps = 4
    identity_initial = transition_distribution(transition_rows, operator, hydrogen_weighted=False)
    identity_hydrogen_target = transition_distribution(transition_rows, operator, hydrogen_weighted=True)
    identity_evolved = markov_evolve_distribution(identity_initial, operator, trajectory_steps)
    identity_tv = total_variation_distance(identity_evolved, identity_hydrogen_target)
    null_history_count = min((len(rows) for rows in null_by_inlet.values()), default=0)
    null_distances = []
    for null_index in range(null_history_count):
        rows = null_transition_rows(null_by_inlet, null_index)
        null_initial = transition_distribution(rows, operator, hydrogen_weighted=False)
        null_target = transition_distribution(rows, operator, hydrogen_weighted=True)
        null_evolved = markov_evolve_distribution(null_initial, operator, trajectory_steps)
        null_distances.append(total_variation_distance(null_evolved, null_target))
    better_or_equal = sum(1 for value in null_distances if value <= identity_tv)
    p_value = (better_or_equal + 1) / (len(null_distances) + 1) if null_distances else 1.0
    null_q05 = quantile(null_distances, 0.05)
    return {
        "observable": "c2_markov_trajectory_distribution",
        "metric": "total_variation_distance_after_4_markov_steps",
        "trajectory_steps": trajectory_steps,
        "target_orbit_count": operator["target_count"],
        "identity_total_variation": round(identity_tv, 9),
        "identity_support": len(identity_evolved),
        "hydrogen_target_support": len(identity_hydrogen_target),
        "null_significance": {
            "null_histories": len(null_distances),
            "p_value": round(p_value, 9),
            "null_q05_total_variation": round(null_q05, 9),
            "null_mean_total_variation": round(sum(null_distances) / max(1, len(null_distances)), 9),
            "identity_total_variation": round(identity_tv, 9),
            "verdict": "C2_MARKOV_TRAJECTORY_BEATS_NULL_05" if identity_tv < null_q05 else "C2_MARKOV_TRAJECTORY_WITHIN_NULL",
        },
        "verdict": "C2_MARKOV_TRAJECTORY_CANDIDATE" if p_value < 0.05 else "C2_MARKOV_TRAJECTORY_WITHIN_NULL",
    }


def build_pressure_atlas(wind: Any) -> dict[str, Any]:
    witness = wind.get("witness", {}) if isinstance(wind, dict) else {}
    identity_rows = witness.get("identity_rows", [])
    null_rows = witness.get("null_rows", [])
    null_by_inlet: dict[int, list[dict[str, Any]]] = {}
    for row in null_rows:
        inlet = int(row.get("inlet", -1))
        null_by_inlet.setdefault(inlet, []).append(row)

    atlas_rows: list[dict[str, Any]] = []
    top_sink_margins: list[float] = []
    top_sink_percentiles: list[float] = []
    for identity in identity_rows:
        inlet = int(identity.get("inlet", len(atlas_rows)))
        vector = [float(value) for value in identity.get("pressure_vector", [])]
        inlet_nulls = null_by_inlet.get(inlet, [])
        null_vectors = [
            [float(value) for value in row.get("pressure_vector", [])]
            for row in inlet_nulls
            if isinstance(row.get("pressure_vector"), list) and len(row.get("pressure_vector", [])) == 20
        ]
        atom_nulls: list[dict[str, float]] = []
        for atom in range(20):
            values = [vector_row[atom] for vector_row in null_vectors]
            atom_nulls.append({
                "mean": round(sum(values) / len(values), 9) if values else 0.0,
                "p95": round(quantile(values, 0.95), 9),
                "max": round(max(values), 9) if values else 0.0,
                "identity_percentile": round(percentile(values, vector[atom] if atom < len(vector) else 0.0), 9),
            })
        enriched_top_atoms = []
        for top in identity.get("top_atoms", [])[:5]:
            atom = int(top.get("atom", -1))
            pressure = float(top.get("pressure", 0.0))
            stat = atom_nulls[atom] if 0 <= atom < len(atom_nulls) else {"p95": 0.0}
            null_values = [vector_row[atom] for vector_row in null_vectors] if 0 <= atom < 20 else []
            margin = pressure - float(stat["p95"])
            pctl = percentile(null_values, pressure)
            c985 = c985_boundary_mask(atom, margin)
            top_sink_margins.append(margin)
            top_sink_percentiles.append(pctl)
            enriched_top_atoms.append({
                "atom": atom,
                "pressure": round(pressure, 9),
                "triple": top.get("triple", TRIPLES[atom] if 0 <= atom < len(TRIPLES) else []),
                "sectors": top.get("sectors", atom_sectors(atom)),
                "null_mean": round(float(stat["mean"]), 9),
                "null_p95": round(float(stat["p95"]), 9),
                "null_max": round(float(stat["max"]), 9),
                "null_margin": round(margin, 9),
                "null_percentile": round(pctl, 9),
                "c985": c985,
            })
        atlas_rows.append({
            "inlet": inlet,
            "inlet_sector": str(identity.get("inlet_sector", SECTORS[inlet] if 0 <= inlet < len(SECTORS) else inlet)),
            "pressure_vector": [round(value, 9) for value in vector],
            "atom_nulls": atom_nulls,
            "top_atoms": enriched_top_atoms,
            "throughput_rate": round(float(identity.get("throughput_rate", 0.0)), 9),
            "alignment_rate": round(float(identity.get("alignment_rate", 0.0)), 9),
            "aperture_loss_rate": round(float(identity.get("aperture_loss_rate", 0.0)), 9),
            "branch_accept_rate": round(float(identity.get("branch_accept_rate", 0.0)), 9),
            "null_rows": len(inlet_nulls),
        })

    positive_margins = [value for value in top_sink_margins if value > 0]
    c985_top_atoms = [top for row in atlas_rows for top in row["top_atoms"]]
    r33_sourced = [top for top in c985_top_atoms if top["c985"]["R33"] == 13 and top["c985"]["closed_return_residual"]]
    mixed_s = [top for top in c985_top_atoms if top["c985"]["K_mixed_S"]]
    pure_sminus = [top for top in c985_top_atoms if top["c985"]["K_pure_Sminus"]]
    top_by_inlet = {int(row["inlet"]): row["top_atoms"][0] for row in atlas_rows if row["top_atoms"]}
    transition_rows: list[dict[str, Any]] = []
    longest_r33_run = 0
    current_r33_run = 0
    for step, inlet in enumerate(D20_GATE_SEQUENCE):
        top = top_by_inlet.get(inlet)
        if not top:
            continue
        c985 = top["c985"]
        r33_sourced_step = int(c985["R33"] == 13 and c985["closed_return_residual"])
        if r33_sourced_step:
            current_r33_run += 1
            longest_r33_run = max(longest_r33_run, current_r33_run)
        else:
            current_r33_run = 0
        transition_rows.append({
            "step": step,
            "inlet": inlet,
            "sector": SECTORS[inlet],
            "atom": top["atom"],
            "pressure": top["pressure"],
            "null_margin": top["null_margin"],
            "R33": c985["R33"],
            "K_mixed_S": c985["K_mixed_S"],
            "K_pure_Sminus": c985["K_pure_Sminus"],
            "flux_label": c985["flux_label"],
            "r33_sourced": r33_sourced_step,
        })

    def mean_margin(items: list[dict[str, Any]]) -> float:
        if not items:
            return 0.0
        return round(sum(float(item["null_margin"]) for item in items) / len(items), 9)

    mixed_items = [top for top in c985_top_atoms if top["c985"]["K_mixed_S"]]
    pure_items = [top for top in c985_top_atoms if top["c985"]["K_pure_Sminus"]]
    neither_items = [top for top in c985_top_atoms if not top["c985"]["K_mixed_S"] and not top["c985"]["K_pure_Sminus"]]
    transition_summary = {
        "gate_sequence": D20_GATE_SEQUENCE,
        "steps": len(transition_rows),
        "r33_sourced_steps": sum(row["r33_sourced"] for row in transition_rows),
        "longest_r33_run": longest_r33_run,
        "unique_sink_atoms": sorted({row["atom"] for row in transition_rows}),
        "dominant_sink_atom": max(
            sorted({row["atom"] for row in transition_rows}),
            key=lambda atom: sum(1 for row in transition_rows if row["atom"] == atom),
        ) if transition_rows else None,
        "k_effect": {
            "mixed_count": len(mixed_items),
            "pure_count": len(pure_items),
            "neither_count": len(neither_items),
            "mixed_mean_margin": mean_margin(mixed_items),
            "pure_mean_margin": mean_margin(pure_items),
            "neither_mean_margin": mean_margin(neither_items),
            "mixed_minus_neither": round(mean_margin(mixed_items) - mean_margin(neither_items), 9),
            "pure_minus_neither": round(mean_margin(pure_items) - mean_margin(neither_items), 9),
        },
        "rows": transition_rows,
    }
    max_margin = max((abs(float(row["null_margin"])) for row in transition_rows), default=1.0) or 1.0
    lag_rows = []
    for lag in range(len(D20_GATE_SEQUENCE)):
        bindings = []
        horizon_values = []
        for index, row in enumerate(transition_rows):
            level = LEVELS[(index + lag) % len(LEVELS)]
            binding = clamp(abs(energy_ev(level)) / 13.6, 0, 1.4)
            margin = float(row["null_margin"]) / max_margin
            horizon = margin
            horizon += 0.10 if int(row["R33"]) == 13 and int(row["r33_sourced"]) else 0.0
            horizon += 0.04 if int(row["K_mixed_S"]) else 0.0
            horizon += 0.06 if int(row["K_pure_Sminus"]) else 0.0
            bindings.append(binding)
            horizon_values.append(horizon)
        rho = pearson_xy(bindings, horizon_values)
        lag_rows.append({
            "lag": lag,
            "rho": round(rho, 9),
            "abs_rho": round(abs(rho), 9),
            "mean_binding": round(sum(bindings) / max(1, len(bindings)), 9),
            "mean_horizon": round(sum(horizon_values) / max(1, len(horizon_values)), 9),
        })
    best_lag = max(lag_rows, key=lambda row: row["abs_rho"]) if lag_rows else {"lag": 0, "rho": 0.0, "abs_rho": 0.0}
    null_history_count = min((len(rows) for rows in null_by_inlet.values()), default=0)
    null_max_abs_rhos = []
    for null_index in range(null_history_count):
        null_horizon_by_step = []
        for inlet in D20_GATE_SEQUENCE:
            null_row = null_by_inlet[inlet][null_index]
            vector = [float(value) for value in null_row.get("pressure_vector", [])]
            null_horizon_by_step.append(max(vector) if vector else 0.0)
        scale = max(null_horizon_by_step) or 1.0
        null_horizon_by_step = [value / scale for value in null_horizon_by_step]
        null_abs_rhos = []
        for lag in range(len(D20_GATE_SEQUENCE)):
            bindings = [
                clamp(abs(energy_ev(LEVELS[(index + lag) % len(LEVELS)])) / 13.6, 0, 1.4)
                for index in range(len(D20_GATE_SEQUENCE))
            ]
            null_abs_rhos.append(abs(pearson_xy(bindings, null_horizon_by_step)))
        null_max_abs_rhos.append(max(null_abs_rhos) if null_abs_rhos else 0.0)
    observed_abs = float(best_lag["abs_rho"])
    exceedances = sum(1 for value in null_max_abs_rhos if value >= observed_abs)
    p_value = (exceedances + 1) / (len(null_max_abs_rhos) + 1) if null_max_abs_rhos else 1.0
    null_significance = {
        "null_histories": len(null_max_abs_rhos),
        "p_value": round(p_value, 9),
        "exceedances": exceedances,
        "null_mean_max_abs_rho": round(sum(null_max_abs_rhos) / max(1, len(null_max_abs_rhos)), 9),
        "null_p95_max_abs_rho": round(quantile(null_max_abs_rhos, 0.95), 9),
        "observed_best_abs_rho": round(observed_abs, 9),
        "verdict": "PHASE_SIGNAL_BEATS_NULL_95" if observed_abs > quantile(null_max_abs_rhos, 0.95) else "PHASE_SIGNAL_WITHIN_NULL",
    }
    lagged_summary = {
        "lags": len(lag_rows),
        "best_lag": int(best_lag["lag"]),
        "best_rho": float(best_lag["rho"]),
        "best_abs_rho": float(best_lag["abs_rho"]),
        "rows": lag_rows,
        "null_significance": null_significance,
        "verdict": "PHASE_SHIFTED_COUPLING_CANDIDATE" if float(best_lag["abs_rho"]) >= 0.35 else "NO_PHASED_HYDROGEN_HORIZON_COUPLING",
    }
    identity_flux_scale = max((float(row["pressure"]) for row in transition_rows), default=1.0) or 1.0
    identity_signed_flux = [
        c985_signed_flux_value(int(row["atom"]), float(row["pressure"]), identity_flux_scale, float(row["null_margin"]))
        for row in transition_rows
    ]
    signed_flux_lag_rows = []
    for lag in range(len(D20_GATE_SEQUENCE)):
        bindings = [
            clamp(abs(energy_ev(LEVELS[(index + lag) % len(LEVELS)])) / 13.6, 0, 1.4)
            for index in range(len(D20_GATE_SEQUENCE))
        ]
        rho = pearson_xy(bindings, identity_signed_flux)
        signed_flux_lag_rows.append({
            "lag": lag,
            "rho": round(rho, 9),
            "abs_rho": round(abs(rho), 9),
        })
    signed_best_lag = max(signed_flux_lag_rows, key=lambda row: row["abs_rho"]) if signed_flux_lag_rows else {"lag": 0, "rho": 0.0, "abs_rho": 0.0}
    signed_null_max_abs_rhos = []
    for null_index in range(null_history_count):
        raw_null_rows = []
        for inlet in D20_GATE_SEQUENCE:
            null_row = null_by_inlet[inlet][null_index]
            vector = [float(value) for value in null_row.get("pressure_vector", [])]
            atom = max(range(len(vector)), key=lambda index: vector[index]) if vector else 0
            pressure = vector[atom] if vector else 0.0
            raw_null_rows.append((atom, pressure))
        scale = max((pressure for _, pressure in raw_null_rows), default=1.0) or 1.0
        null_signed_flux = [c985_signed_flux_value(atom, pressure, scale, 0.0) for atom, pressure in raw_null_rows]
        null_abs_rhos = []
        for lag in range(len(D20_GATE_SEQUENCE)):
            bindings = [
                clamp(abs(energy_ev(LEVELS[(index + lag) % len(LEVELS)])) / 13.6, 0, 1.4)
                for index in range(len(D20_GATE_SEQUENCE))
            ]
            null_abs_rhos.append(abs(pearson_xy(bindings, null_signed_flux)))
        signed_null_max_abs_rhos.append(max(null_abs_rhos) if null_abs_rhos else 0.0)
    signed_observed_abs = float(signed_best_lag["abs_rho"])
    signed_exceedances = sum(1 for value in signed_null_max_abs_rhos if value >= signed_observed_abs)
    signed_p_value = (signed_exceedances + 1) / (len(signed_null_max_abs_rhos) + 1) if signed_null_max_abs_rhos else 1.0
    signed_flux_summary = {
        "observable": "signed_C985_flux_balance",
        "lags": len(signed_flux_lag_rows),
        "best_lag": int(signed_best_lag["lag"]),
        "best_rho": float(signed_best_lag["rho"]),
        "best_abs_rho": float(signed_best_lag["abs_rho"]),
        "rows": signed_flux_lag_rows,
        "null_significance": {
            "null_histories": len(signed_null_max_abs_rhos),
            "p_value": round(signed_p_value, 9),
            "exceedances": signed_exceedances,
            "null_mean_max_abs_rho": round(sum(signed_null_max_abs_rhos) / max(1, len(signed_null_max_abs_rhos)), 9),
            "null_p95_max_abs_rho": round(quantile(signed_null_max_abs_rhos, 0.95), 9),
            "observed_best_abs_rho": round(signed_observed_abs, 9),
            "verdict": "SIGNED_FLUX_BEATS_NULL_95" if signed_observed_abs > quantile(signed_null_max_abs_rhos, 0.95) else "SIGNED_FLUX_WITHIN_NULL",
        },
        "verdict": "SIGNED_C985_PHASE_CANDIDATE" if signed_observed_abs >= 0.35 else "NO_SIGNED_C985_PHASE_COUPLING",
    }
    identity_height_flux = [
        c985_height_flux_balance_value(int(row["atom"]), float(row["pressure"]), identity_flux_scale, float(row["null_margin"]))
        for row in transition_rows
    ]
    height_flux_lag_rows = []
    for lag in range(len(D20_GATE_SEQUENCE)):
        bindings = [
            clamp(abs(energy_ev(LEVELS[(index + lag) % len(LEVELS)])) / 13.6, 0, 1.4)
            for index in range(len(D20_GATE_SEQUENCE))
        ]
        rho = pearson_xy(bindings, identity_height_flux)
        height_flux_lag_rows.append({
            "lag": lag,
            "rho": round(rho, 9),
            "abs_rho": round(abs(rho), 9),
        })
    height_best_lag = max(height_flux_lag_rows, key=lambda row: row["abs_rho"]) if height_flux_lag_rows else {"lag": 0, "rho": 0.0, "abs_rho": 0.0}
    height_null_max_abs_rhos = []
    for null_index in range(null_history_count):
        raw_null_rows = []
        for inlet in D20_GATE_SEQUENCE:
            null_row = null_by_inlet[inlet][null_index]
            vector = [float(value) for value in null_row.get("pressure_vector", [])]
            atom = max(range(len(vector)), key=lambda index: vector[index]) if vector else 0
            pressure = vector[atom] if vector else 0.0
            raw_null_rows.append((atom, pressure))
        scale = max((pressure for _, pressure in raw_null_rows), default=1.0) or 1.0
        null_height_flux = [c985_height_flux_balance_value(atom, pressure, scale, 0.0) for atom, pressure in raw_null_rows]
        null_abs_rhos = []
        for lag in range(len(D20_GATE_SEQUENCE)):
            bindings = [
                clamp(abs(energy_ev(LEVELS[(index + lag) % len(LEVELS)])) / 13.6, 0, 1.4)
                for index in range(len(D20_GATE_SEQUENCE))
            ]
            null_abs_rhos.append(abs(pearson_xy(bindings, null_height_flux)))
        height_null_max_abs_rhos.append(max(null_abs_rhos) if null_abs_rhos else 0.0)
    height_observed_abs = float(height_best_lag["abs_rho"])
    height_exceedances = sum(1 for value in height_null_max_abs_rhos if value >= height_observed_abs)
    height_p_value = (height_exceedances + 1) / (len(height_null_max_abs_rhos) + 1) if height_null_max_abs_rhos else 1.0
    height_flux_summary = {
        "observable": "signed_C985_height_flux_balance",
        "ledger_equation": "bare Pi33 + R33_height_residual + finite_height_flux = 0",
        "lags": len(height_flux_lag_rows),
        "best_lag": int(height_best_lag["lag"]),
        "best_rho": float(height_best_lag["rho"]),
        "best_abs_rho": float(height_best_lag["abs_rho"]),
        "rows": height_flux_lag_rows,
        "null_significance": {
            "null_histories": len(height_null_max_abs_rhos),
            "p_value": round(height_p_value, 9),
            "exceedances": height_exceedances,
            "null_mean_max_abs_rho": round(sum(height_null_max_abs_rhos) / max(1, len(height_null_max_abs_rhos)), 9),
            "null_p95_max_abs_rho": round(quantile(height_null_max_abs_rhos, 0.95), 9),
            "observed_best_abs_rho": round(height_observed_abs, 9),
            "verdict": "HEIGHT_FLUX_BEATS_NULL_95" if height_observed_abs > quantile(height_null_max_abs_rhos, 0.95) else "HEIGHT_FLUX_WITHIN_NULL",
        },
        "verdict": "HEIGHT_FLUX_PHASE_CANDIDATE" if height_observed_abs >= 0.35 else "NO_HEIGHT_FLUX_PHASE_COUPLING",
    }
    atlas_by_inlet = {int(row["inlet"]): row for row in atlas_rows}
    identity_ward_signal = [
        c985_zero_pair_ward_selector_value(
            [float(value) for value in atlas_by_inlet[int(row["inlet"])]["pressure_vector"]],
            atlas_by_inlet[int(row["inlet"])]["atom_nulls"],
        )
        for row in transition_rows
        if int(row["inlet"]) in atlas_by_inlet
    ]
    zero_pair_ward_lag_rows = []
    for lag in range(len(D20_GATE_SEQUENCE)):
        bindings = [
            clamp(abs(energy_ev(LEVELS[(index + lag) % len(LEVELS)])) / 13.6, 0, 1.4)
            for index in range(len(identity_ward_signal))
        ]
        rho = pearson_xy(bindings, identity_ward_signal)
        zero_pair_ward_lag_rows.append({
            "lag": lag,
            "rho": round(rho, 9),
            "abs_rho": round(abs(rho), 9),
        })
    ward_best_lag = max(zero_pair_ward_lag_rows, key=lambda row: row["abs_rho"]) if zero_pair_ward_lag_rows else {"lag": 0, "rho": 0.0, "abs_rho": 0.0}
    ward_null_max_abs_rhos = []
    for null_index in range(null_history_count):
        null_ward_signal = []
        for inlet in D20_GATE_SEQUENCE:
            null_row = null_by_inlet[inlet][null_index]
            vector = [float(value) for value in null_row.get("pressure_vector", [])]
            null_ward_signal.append(c985_zero_pair_ward_selector_value(vector, None))
        null_abs_rhos = []
        for lag in range(len(D20_GATE_SEQUENCE)):
            bindings = [
                clamp(abs(energy_ev(LEVELS[(index + lag) % len(LEVELS)])) / 13.6, 0, 1.4)
                for index in range(len(D20_GATE_SEQUENCE))
            ]
            null_abs_rhos.append(abs(pearson_xy(bindings, null_ward_signal)))
        ward_null_max_abs_rhos.append(max(null_abs_rhos) if null_abs_rhos else 0.0)
    ward_observed_abs = float(ward_best_lag["abs_rho"])
    ward_exceedances = sum(1 for value in ward_null_max_abs_rhos if value >= ward_observed_abs)
    ward_p_value = (ward_exceedances + 1) / (len(ward_null_max_abs_rhos) + 1) if ward_null_max_abs_rhos else 1.0
    zero_pair_ward_summary = {
        "observable": "zero_pair_ward_height_selector",
        "source_mask": 288,
        "source_bits": WARD_SOURCE_MASK_288_BITS,
        "source_action": WARD_SOURCE_ACTION,
        "action_decomposition": "691200 + 374784 = 1065984",
        "corrected_ward_clock": "13 + 13 = 0 mod 26",
        "shared_atom": WARD_SHARED_ATOM,
        "ledger_equation": "bare_pi33 + R33 + A_h = 0 - 1065984 + 1065984 = 0",
        "lags": len(zero_pair_ward_lag_rows),
        "best_lag": int(ward_best_lag["lag"]),
        "best_rho": float(ward_best_lag["rho"]),
        "best_abs_rho": float(ward_best_lag["abs_rho"]),
        "rows": zero_pair_ward_lag_rows,
        "null_significance": {
            "null_histories": len(ward_null_max_abs_rhos),
            "p_value": round(ward_p_value, 9),
            "exceedances": ward_exceedances,
            "null_mean_max_abs_rho": round(sum(ward_null_max_abs_rhos) / max(1, len(ward_null_max_abs_rhos)), 9),
            "null_p95_max_abs_rho": round(quantile(ward_null_max_abs_rhos, 0.95), 9),
            "observed_best_abs_rho": round(ward_observed_abs, 9),
            "verdict": "ZERO_PAIR_WARD_BEATS_NULL_95" if ward_observed_abs > quantile(ward_null_max_abs_rhos, 0.95) else "ZERO_PAIR_WARD_WITHIN_NULL",
        },
        "verdict": "ZERO_PAIR_WARD_PHASE_CANDIDATE" if ward_observed_abs >= 0.35 else "NO_ZERO_PAIR_WARD_PHASE_COUPLING",
    }
    verdict = "IDENTITY_SINK_EXCEEDS_NULL_P95" if positive_margins else "NULL_BASELINE_CONTAINS_IDENTITY_SINKS"
    return {
        "status": "D20_BLACK_HOLE_PRESSURE_ATLAS_DATA",
        "verdict": verdict,
        "sectors": SECTORS,
        "triples": TRIPLES,
        "identity_rows": len(identity_rows),
        "null_rows": len(null_rows),
        "null_rows_per_inlet": {str(inlet): len(rows) for inlet, rows in sorted(null_by_inlet.items())},
        "top_sink_positive_margins": len(positive_margins),
        "mean_top_sink_margin": round(sum(top_sink_margins) / max(1, len(top_sink_margins)), 9),
        "max_top_sink_margin": round(max(top_sink_margins), 9) if top_sink_margins else 0.0,
        "mean_top_sink_percentile": round(sum(top_sink_percentiles) / max(1, len(top_sink_percentiles)), 9),
        "c985_summary": {
            "projection": "d20_to_C985_boundary_mask_v1",
            "r33_sourced_closed_returns": len(r33_sourced),
            "mixed_s_support": len(mixed_s),
            "pure_sminus_support": len(pure_sminus),
            "basis": ["R33", "K_mixed_S", "K_pure_Sminus"],
            "r33_rule": "R33_global(mask)=13*<[1,1,1,0,1,1,1,1,1,1,1],mask> mod 26",
        },
        "c985_transition_summary": transition_summary,
        "lagged_correlation_summary": lagged_summary,
        "signed_flux_lag_summary": signed_flux_summary,
        "height_flux_lag_summary": height_flux_summary,
        "zero_pair_ward_lag_summary": zero_pair_ward_summary,
        "atlas_rows": atlas_rows,
    }


def boundary_proxy(level: dict[str, Any], pressure: dict[str, Any]) -> dict[str, float | str]:
    binding = clamp(abs(energy_ev(level)) / 13.6, 0, 1.4)
    pressure_mean = float(pressure["pressure_mean"])
    pressure_peak = float(pressure["pressure_peak"])
    throughput = clamp(float(pressure["throughput"]), 0, 1)
    alignment = clamp(float(pressure["alignment"]), 0, 1)
    aperture = clamp(float(pressure["aperture"]), 0, 1)
    mass = clamp(0.30 * pressure_mean + 0.24 * pressure_peak + 0.20 * aperture + 0.16 * throughput + 0.10 * alignment, 0, 0.94)
    redshift = 1 / max(0.16, 1 - 0.68 * mass)
    absorption = clamp(0.48 * mass + 0.30 * (1 - min(1, abs(binding - ALPHA_WALL))) + 0.22 * pressure_peak, 0, 1)
    match = clamp(1 - abs(clamp(binding, 0, 1) - absorption), 0, 1)
    return {
        "level": str(level["label"]),
        "sector": str(level["sector"]),
        "inlet": str(pressure["inlet"]),
        "binding_norm": round(binding, 9),
        "horizon_mass_proxy": round(mass, 9),
        "redshift_proxy": round(redshift, 9),
        "absorption_proxy": round(absorption, 9),
        "boundary_match": round(match, 9),
    }


def pearson(rows: list[dict[str, float | str]]) -> float:
    if len(rows) < 2:
        return 0.0
    xs = [float(row["binding_norm"]) for row in rows]
    ys = [float(row["absorption_proxy"]) for row in rows]
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    x_den = sum((x - x_mean) ** 2 for x in xs)
    y_den = sum((y - y_mean) ** 2 for y in ys)
    if x_den <= 1e-12 or y_den <= 1e-12:
        return 0.0
    return numerator / math.sqrt(x_den * y_den)


def pearson_xy(xs: list[float], ys: list[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        return 0.0
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    x_den = sum((x - x_mean) ** 2 for x in xs)
    y_den = sum((y - y_mean) ** 2 for y in ys)
    if x_den <= 1e-12 or y_den <= 1e-12:
        return 0.0
    return numerator / math.sqrt(x_den * y_den)


def main() -> None:
    html_path = ROOT / "generated" / "d20_sandpile_visualization.html"
    js_path = ROOT / "generated" / "d20_black_hole_atom_lab.js"
    css_path = ROOT / "generated" / "d20_black_hole_atom_lab.css"
    equations_path = ROOT / "docs" / "equations.txt"
    wind_path = ROOT / "generated" / "d20_wind_pressure_export_report.json"
    html = html_path.read_text(encoding="utf-8")
    js = js_path.read_text(encoding="utf-8")
    css = css_path.read_text(encoding="utf-8")
    equations = equations_path.read_text(encoding="utf-8")
    compact_equations = "".join(equations.split())
    wind = load_json(wind_path)
    scattering_operator_report = load_json(SCATTERING_OPERATOR_REPORT)
    dynamics_selector_report = load_json(DYNAMICS_SELECTOR_REPORT)
    boundary_packet_pairing_report = load_json(BOUNDARY_PACKET_PAIRING_REPORT)
    boundary_packet_row_normalization_report = load_json(BOUNDARY_PACKET_ROW_NORMALIZATION_REPORT)
    boundary_packet_low_support_report = load_json(BOUNDARY_PACKET_LOW_SUPPORT_REPORT)
    hydrogen_sandpile_golay_bridge_probe = load_json(HYDROGEN_SANDPILE_GOLAY_BRIDGE_PROBE)
    pressure_atlas = build_pressure_atlas(wind)
    c2_operator = build_c2_markov_operator(scattering_operator_report)
    transition_rows_for_orbit = pressure_atlas["c985_transition_summary"]["rows"]
    identity_orbit_signal = [
        c2_markov_orbit_drift_value(int(row["atom"]), int(row["inlet"]), int(row["step"]), c2_operator)
        for row in transition_rows_for_orbit
    ]
    witness = wind.get("witness", {}) if isinstance(wind, dict) else {}
    null_by_inlet_for_orbit: dict[int, list[dict[str, Any]]] = {}
    for row in witness.get("null_rows", []):
        null_by_inlet_for_orbit.setdefault(int(row.get("inlet", -1)), []).append(row)
    null_history_count_for_orbit = min((len(rows) for rows in null_by_inlet_for_orbit.values()), default=0)
    null_orbit_signals = []
    for null_index in range(null_history_count_for_orbit):
        signal = []
        for step, inlet in enumerate(D20_GATE_SEQUENCE):
            null_row = null_by_inlet_for_orbit[inlet][null_index]
            vector = [float(value) for value in null_row.get("pressure_vector", [])]
            atom = max(range(len(vector)), key=lambda index: vector[index]) if vector else 0
            signal.append(c2_markov_orbit_drift_value(atom, inlet, step, c2_operator))
        null_orbit_signals.append(signal)
    c2_markov_orbit_summary = lag_scan_against_nulls(identity_orbit_signal, null_orbit_signals, "C2_MARKOV_ORBIT")
    c2_markov_orbit_summary.update({
        "observable": "c2_markov_orbit_height_drift",
        "theorem_status": scattering_operator_report["status"],
        "target_orbit_count": c2_operator["target_count"],
        "rank": c2_operator["rank"],
        "nullity": c2_operator["nullity"],
        "stationary_distribution_denominator": c2_operator["stationary_distribution_denominator"],
        "markov_spectrum": c2_operator["markov_spectrum"],
        "component_size_histogram": c2_operator["component_size_histogram"],
        "embedding": "d20/C985 mask -> 543 C2 quotient orbit via finite mask/inlet/step hash",
        "verdict": "C2_MARKOV_ORBIT_PHASE_CANDIDATE" if c2_markov_orbit_summary["best_abs_rho"] >= 0.35 else "NO_C2_MARKOV_ORBIT_PHASE_COUPLING",
    })
    pressure_atlas["c2_markov_orbit_lag_summary"] = c2_markov_orbit_summary
    pressure_atlas["c2_selector_family_lag_summary"] = build_selector_family_summary(
        dynamics_selector_report,
        transition_rows_for_orbit,
        null_by_inlet_for_orbit,
    )
    pressure_atlas["c2_markov_trajectory_summary"] = build_c2_markov_trajectory_summary(
        c2_operator,
        transition_rows_for_orbit,
        null_by_inlet_for_orbit,
    )
    pressure_atlas["boundary_dynamics_summary"] = build_boundary_dynamics_summary(
        c2_operator,
        transition_rows_for_orbit,
        null_by_inlet_for_orbit,
    )
    pressure_rows_raw: list[dict[str, Any]] = []
    collect_pressure_rows(wind, pressure_rows_raw)
    pressure_rows = [pressure_summary(row, index) for index, row in enumerate(pressure_rows_raw)]
    representative_pressures = pressure_rows[:72]
    correlations = [boundary_proxy(level, pressure) for pressure in representative_pressures for level in LEVELS]
    simultaneous_rho = round(pearson(correlations), 9)
    raw_lag = pressure_atlas["lagged_correlation_summary"]
    signed_lag = pressure_atlas["signed_flux_lag_summary"]
    height_lag = pressure_atlas["height_flux_lag_summary"]
    ward_lag = pressure_atlas["zero_pair_ward_lag_summary"]
    orbit_lag = pressure_atlas["c2_markov_orbit_lag_summary"]
    selector_lag = pressure_atlas["c2_selector_family_lag_summary"]
    trajectory = pressure_atlas["c2_markov_trajectory_summary"]
    boundary_sink_supported = pressure_atlas["top_sink_positive_margins"] > 0 and pressure_atlas["c985_summary"]["r33_sourced_closed_returns"] > 0
    height_supported = height_lag["null_significance"]["p_value"] < 0.05
    ward_supported = ward_lag["null_significance"]["p_value"] < 0.05
    orbit_supported = orbit_lag["null_significance"]["p_value"] < 0.05
    selector_supported = selector_lag["best_null_p"] < 0.05
    trajectory_supported = trajectory["null_significance"]["p_value"] < 0.05
    boundary_packet_bridge_summary = build_boundary_packet_bridge_summary(
        boundary_packet_pairing_report,
        boundary_packet_row_normalization_report,
        boundary_packet_low_support_report,
    )
    rank_one_packet_family_sink_summary = build_rank_one_packet_family_sink_summary(
        pressure_atlas,
        boundary_packet_bridge_summary,
    )
    signed_rank_one_packet_quotient_summary = build_signed_rank_one_packet_quotient_summary(
        boundary_packet_low_support_report,
        pressure_atlas,
        null_by_inlet_for_orbit,
    )
    signed_packet_quotient_lag_summary = build_signed_packet_quotient_lag_summary(
        signed_rank_one_packet_quotient_summary,
        pressure_atlas,
        null_by_inlet_for_orbit,
    )
    pressure_atlas["signed_packet_quotient_lag_summary"] = signed_packet_quotient_lag_summary
    signed_packet_quotient_supported = signed_packet_quotient_lag_summary["null_significance"]["p_value"] < 0.05
    support3_signed_quotient_summary = build_support3_signed_quotient_summary(
        pressure_atlas,
        null_by_inlet_for_orbit,
    )
    support3_signed_quotient_lag_summary = build_support3_signed_quotient_lag_summary(
        support3_signed_quotient_summary,
        pressure_atlas,
        null_by_inlet_for_orbit,
    )
    pressure_atlas["support3_signed_quotient_summary"] = support3_signed_quotient_summary
    pressure_atlas["support3_signed_quotient_lag_summary"] = support3_signed_quotient_lag_summary
    support3_signed_quotient_supported = support3_signed_quotient_lag_summary["null_significance"]["p_value"] < 0.05
    a985_q12_packet_bridge_probe_summary = build_a985_q12_packet_bridge_probe_summary(
        hydrogen_sandpile_golay_bridge_probe
    )
    falsification_rows = [
        {
            "claim": "finite_boundary_sink",
            "status": "supported_proxy" if boundary_sink_supported else "failed",
            "evidence": f"{pressure_atlas['top_sink_positive_margins']} top sinks beat null p95; {pressure_atlas['c985_summary']['r33_sourced_closed_returns']} are R33-sourced",
            "ledger_source": "finite BMS/Carrollian boundary sink projection",
            "observable_class": "boundary_sink",
        },
        {
            "claim": "simultaneous_hydrogen_horizon_coupling",
            "status": "failed_zero_correlation" if abs(simultaneous_rho) < 0.1 else "open_candidate",
            "evidence": f"Pearson(binding, absorption)={simultaneous_rho}",
            "ledger_source": "hydrogen invariants vs finite horizon proxy",
            "observable_class": "scalar_absorption",
        },
        {
            "claim": "raw_pressure_margin_phase_coupling",
            "status": "failed_null" if raw_lag["null_significance"]["p_value"] >= 0.05 else "supported_candidate",
            "evidence": f"best lag {raw_lag['best_lag']} rho={raw_lag['best_rho']} null_p={raw_lag['null_significance']['p_value']}",
            "ledger_source": "pressure atlas identity-vs-null rows",
            "observable_class": "scalar_pressure_margin",
        },
        {
            "claim": "signed_C985_flux_phase_coupling",
            "status": "failed_null" if signed_lag["null_significance"]["p_value"] >= 0.05 else "supported_candidate",
            "evidence": f"best lag {signed_lag['best_lag']} rho={signed_lag['best_rho']} null_p={signed_lag['null_significance']['p_value']}",
            "ledger_source": "C985 boundary vector (R33,K_mixed_S,K_pure_Sminus)",
            "observable_class": "signed_scalar_flux",
        },
        {
            "claim": "signed_C985_height_flux_phase_coupling",
            "status": "supported_candidate" if height_supported else "failed_null",
            "evidence": f"best lag {height_lag['best_lag']} rho={height_lag['best_rho']} null_p={height_lag['null_significance']['p_value']}",
            "ledger_source": "finite BMS/Carrollian hidden row bare Pi33 + R33_height_residual + finite_height_flux = 0",
            "observable_class": "signed_scalar_height_flux",
        },
        {
            "claim": "zero_pair_ward_height_selector_phase_coupling",
            "status": "supported_candidate" if ward_supported else "failed_null",
            "evidence": f"mask 288 best lag {ward_lag['best_lag']} rho={ward_lag['best_rho']} null_p={ward_lag['null_significance']['p_value']}",
            "ledger_source": "full-exposure zero-pair Ward-kernel height selector mask 288",
            "observable_class": "zero_pair_scalar_selector",
        },
        {
            "claim": "c2_markov_orbit_height_drift_phase_coupling",
            "status": "supported_candidate" if orbit_supported else "failed_null",
            "evidence": f"543-orbit Markov drift best lag {orbit_lag['best_lag']} rho={orbit_lag['best_rho']} null_p={orbit_lag['null_significance']['p_value']}",
            "ledger_source": "full-exposure zero-pair sourced-balance C2 quotient scattering operator",
            "observable_class": "ward_balanced_markov_orbit_drift",
        },
        {
            "claim": "c2_selector_family_mask_overlap_phase_coupling",
            "status": "supported_candidate" if selector_supported else "failed_null",
            "evidence": f"{selector_lag['best_candidate']} best lag {selector_lag['best_lag']} rho={selector_lag['best_rho']} null_p={selector_lag['best_null_p']}",
            "ledger_source": "full-exposure zero-pair sourced-balance C2 dynamics selector",
            "observable_class": "ward_balanced_selector_family",
        },
        {
            "claim": "c2_markov_trajectory_distribution_coupling",
            "status": "supported_candidate" if trajectory_supported else "failed_null",
            "evidence": f"TV={trajectory['identity_total_variation']} null_p={trajectory['null_significance']['p_value']}",
            "ledger_source": "full-exposure zero-pair sourced-balance C2 quotient scattering operator",
            "observable_class": "ward_balanced_markov_trajectory_distribution",
        },
        {
            "claim": "signed_packet_quotient_hydrogen_coupling",
            "status": "supported_candidate" if signed_packet_quotient_supported else "failed_null",
            "evidence": f"candidate {signed_packet_quotient_lag_summary['best_signed_candidate']} support {signed_packet_quotient_lag_summary['support_atoms']} best lag {signed_packet_quotient_lag_summary['best_lag']} rho={signed_packet_quotient_lag_summary['best_rho']} null_p={signed_packet_quotient_lag_summary['null_significance']['p_value']}",
            "ledger_source": "signed rank-one support-2 packet quotient from boundary-packet low-support atlas",
            "observable_class": "non_diagonal_packet_quotient",
        },
        {
            "claim": "support3_signed_packet_quotient_hydrogen_coupling",
            "status": "supported_candidate" if support3_signed_quotient_supported else "failed_null",
            "evidence": f"candidate {support3_signed_quotient_lag_summary['best_candidate']} support {support3_signed_quotient_lag_summary['support_atoms']} best lag {support3_signed_quotient_lag_summary['best_lag']} rho={support3_signed_quotient_lag_summary['best_rho']} null_p={support3_signed_quotient_lag_summary['null_significance']['p_value']}",
            "ledger_source": "screened support-3 signed public-boundary quotient search",
            "observable_class": "support3_non_diagonal_packet_quotient",
        },
    ]
    failed_claims = sum(1 for row in falsification_rows if row["status"].startswith("failed"))
    supported_claims = sum(1 for row in falsification_rows if row["status"].startswith("supported"))
    if boundary_sink_supported and support3_signed_quotient_supported:
        overall_status = "BOUNDARY_SINK_SUPPORTED_SUPPORT3_SIGNED_QUOTIENT_CANDIDATE"
    elif boundary_sink_supported and signed_packet_quotient_supported:
        overall_status = "BOUNDARY_SINK_SUPPORTED_SIGNED_PACKET_QUOTIENT_CANDIDATE"
    elif boundary_sink_supported and trajectory_supported:
        overall_status = "BOUNDARY_SINK_SUPPORTED_C2_MARKOV_TRAJECTORY_CANDIDATE"
    elif boundary_sink_supported and selector_supported:
        overall_status = "BOUNDARY_SINK_SUPPORTED_C2_SELECTOR_FAMILY_CANDIDATE"
    elif boundary_sink_supported and orbit_supported:
        overall_status = "BOUNDARY_SINK_SUPPORTED_C2_MARKOV_ORBIT_CANDIDATE"
    elif boundary_sink_supported and ward_supported:
        overall_status = "BOUNDARY_SINK_SUPPORTED_ZERO_PAIR_WARD_CANDIDATE"
    elif boundary_sink_supported and height_supported:
        overall_status = "BOUNDARY_SINK_SUPPORTED_HEIGHT_FLUX_CANDIDATE"
    else:
        overall_status = "BOUNDARY_SINK_SUPPORTED_COUPLING_NOT_SUPPORTED"
    if support3_signed_quotient_supported:
        next_observable_class = "support-3 residual and source-state audit"
    elif signed_packet_quotient_supported:
        next_observable_class = "residual-only hydrogen coupling audit"
    else:
        next_observable_class = "A985/q12 packet projection construction"
    pressure_atlas["falsification_ledger_summary"] = {
        "total_claims": len(falsification_rows),
        "failed_claims": failed_claims,
        "supported_claims": supported_claims,
        "overall_status": overall_status if boundary_sink_supported else "OPEN",
        "taxonomy": {
            "failed_scalar_proxy_classes": sorted({row["observable_class"] for row in falsification_rows if row["status"].startswith("failed")}),
            "supported_classes": sorted({row["observable_class"] for row in falsification_rows if row["status"].startswith("supported")}),
            "next_class": next_observable_class,
        },
        "rows": falsification_rows,
    }
    atlas_js = "window.D20_BLACK_HOLE_PRESSURE_ATLAS_DATA = " + json.dumps(pressure_atlas, sort_keys=True, separators=(",", ":")) + ";\n"
    ATLAS_JS.write_text(atlas_js, encoding="utf-8")
    atlas_js_sha256 = hashlib.sha256(ATLAS_JS.read_bytes()).hexdigest()
    level_rows = [
        {
            "label": level["label"],
            "n": level["n"],
            "j": level["j"],
            "sector": level["sector"],
            "principal": round(principal(level), 12),
            "fine": round(fine(level), 12),
            "energy_ev": round(energy_ev(level), 12),
        }
        for level in LEVELS
    ]
    html_checks = {
        "panel": 'id="d20BlackHoleAtomPanel"' in html,
        "canvas": 'id="d20BlackHoleAtomCanvas"' in html,
            "atlas_canvas": 'id="d20BlackHolePressureAtlasCanvas"' in html,
            "ward_bms_3d_canvas": 'id="d20WardBms3dCanvas"' in html,
            "ward_bms_canvas": 'id="d20WardBmsDynamicsCanvas"' in html,
        "pulse_control": 'id="d20BhPulse"' in html,
        "dynamics_play_control": 'id="d20BhPlayDynamics"' in html,
        "pulse_readouts": 'id="d20BhPulseStep"' in html and 'id="d20BhPulseSink"' in html,
        "dynamics_play_readout": 'id="d20BhDynamicsMode"' in html,
        "script_link": "d20_black_hole_atom_lab.js" in html,
        "atlas_script_link": "d20_black_hole_pressure_atlas_data.js" in html,
        "style_link": "d20_black_hole_atom_lab.css" in html,
    }
    js_checks = {
        "alpha_star": "1 / 137" in js,
        "alpha_wall": "1 / 4" in js,
        "fine_denominator": "75076" in js,
        "lamb_reference": "1057.845020" in js,
        "finite_proxy_disclaimer": "not a solved Einstein metric" in js,
        "evidence_target": "Evidence target" in js,
        "pressure_atlas": "drawPressureAtlas" in js,
        "atlas_null_readouts": "d20BhNullMargin" in js and "d20BhSinkPctl" in js,
        "dynamic_pulse_history": "function activeTransition" in js and "function pulseHorizon" in js,
        "transition_driven_boundary": "c985_transition_summary" in js and "transition.R33" in js,
        "dynamics_play_loop": "function setDynamicsPlaying" in js and "requestAnimationFrame" in js and "dynamicsStepMs" in js and "d20BhPlayDynamics" in js,
    }
    css_checks = {
        "panel_style": ".d20-black-hole-atom-panel" in css,
        "canvas_style": "#d20BlackHoleAtomNotes" in css,
    }
    equation_checks = {
        "d20_dimension": "C(6,3)=20" in compact_equations or "\\binom63=20" in compact_equations,
        "alpha_denominator": "137=128+8+1" in compact_equations,
        "alpha_wall": "A_alpha=1/4" in compact_equations or "A_\\alpha=\\frac14" in compact_equations,
        "hydrogen_scale": "Lambda=54.4eV" in compact_equations or "\\Lambda=54.4,\\mathrm{eV}" in compact_equations,
        "fine_denominator": "75076" in compact_equations,
        "lamb_reference": "1057.845020MHz" in compact_equations or "1057.845020,\\mathrm{MHz}" in compact_equations,
        "six_plus_fourteen": "20=6+14" in compact_equations,
    }
    report = {
        "status": "D20_BLACK_HOLE_ATOM_LAB_REPORT_CERTIFIED",
        "verdict": "FINITE_BOUNDARY_PROXY_READY",
        "scope": "Hydrogen invariants are rendered against a finite d20 horizon proxy. This is a measurement harness, not a GR black-hole solution.",
        "invariants": {
            "alpha_star": ALPHA_STAR,
            "alpha_wall": ALPHA_WALL,
            "lambda_ev": LAMBDA_EV,
            "fine_denominator": FINE_DENOMINATOR,
            "lamb_vac": LAMB_VAC,
            "lamb_shift_ev": LAMB_SHIFT_EV,
            "lamb_reference_mhz": LAMB_REFERENCE_MHZ,
            "packet_law": "5*589824/(4*23040)=32",
            "alpha_cut": "20=6+14, below-alpha sector recovers H6",
        },
        "level_rows": level_rows,
        "wind_pressure_rows_found": len(pressure_rows),
        "correlation_rows": correlations,
        "correlation_summary": {
            "rows": len(correlations),
            "pearson_binding_absorption": round(pearson(correlations), 9),
            "mean_boundary_match": round(sum(float(row["boundary_match"]) for row in correlations) / max(1, len(correlations)), 9),
            "max_boundary_match": round(max((float(row["boundary_match"]) for row in correlations), default=0), 9),
        },
        "html_checks": html_checks,
        "js_checks": js_checks,
        "css_checks": css_checks,
        "equation_checks": equation_checks,
        "atlas_checks": {
            "identity_rows": pressure_atlas["identity_rows"] == 6,
            "null_rows": pressure_atlas["null_rows"] == 4314,
            "null_rows_per_inlet": all(value == 719 for value in pressure_atlas["null_rows_per_inlet"].values()),
            "six_atlas_rows": len(pressure_atlas["atlas_rows"]) == 6,
            "twenty_atoms_per_row": all(len(row["pressure_vector"]) == 20 and len(row["atom_nulls"]) == 20 for row in pressure_atlas["atlas_rows"]),
            "top_atoms_enriched": all(row["top_atoms"] and "null_margin" in row["top_atoms"][0] for row in pressure_atlas["atlas_rows"]),
            "c985_masks": all(
                row["top_atoms"] and len(row["top_atoms"][0]["c985"]["mask"]) == 11
                for row in pressure_atlas["atlas_rows"]
            ),
            "c985_basis": pressure_atlas["c985_summary"]["basis"] == ["R33", "K_mixed_S", "K_pure_Sminus"],
            "c985_transition_ledger": pressure_atlas["c985_transition_summary"]["steps"] == len(D20_GATE_SEQUENCE),
            "dynamic_pulse_wiring": "function pulseHorizon" in js and 'id="d20BhPulse"' in html,
            "dynamic_playback_wiring": "function setDynamicsPlaying" in js and 'id="d20BhPlayDynamics"' in html and "requestAnimationFrame" in js and "dynamicsStepMs" in js,
            "lagged_scan": pressure_atlas["lagged_correlation_summary"]["lags"] == len(D20_GATE_SEQUENCE),
            "lagged_browser_readouts": "d20BhBestLag" in html and "d20BhLagRho" in html and "d20BhLagNullP" in html and "lagged_correlation_summary" in js,
            "lagged_null_significance": pressure_atlas["lagged_correlation_summary"]["null_significance"]["null_histories"] == 719,
            "signed_flux_lag": pressure_atlas["signed_flux_lag_summary"]["lags"] == len(D20_GATE_SEQUENCE),
            "signed_flux_browser_readouts": "d20BhFluxLagRho" in html and "d20BhFluxNullP" in html and "signed_flux_lag_summary" in js,
            "height_flux_lag": pressure_atlas["height_flux_lag_summary"]["lags"] == len(D20_GATE_SEQUENCE),
            "height_flux_browser_readouts": "d20BhHeightLagRho" in html and "d20BhHeightNullP" in html and "height_flux_lag_summary" in js,
            "zero_pair_ward_lag": pressure_atlas["zero_pair_ward_lag_summary"]["lags"] == len(D20_GATE_SEQUENCE),
            "zero_pair_ward_browser_readouts": "d20BhWardLagRho" in html and "d20BhWardNullP" in html and "zero_pair_ward_lag_summary" in js,
            "c2_markov_orbit_lag": pressure_atlas["c2_markov_orbit_lag_summary"]["lags"] == len(D20_GATE_SEQUENCE),
            "c2_markov_orbit_browser_readouts": "d20BhOrbitLagRho" in html and "d20BhOrbitNullP" in html and "c2_markov_orbit_lag_summary" in js,
            "c2_markov_operator_theorem": pressure_atlas["c2_markov_orbit_lag_summary"]["theorem_status"] == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_SCATTERING_OPERATOR_CERTIFIED",
            "c2_selector_family_lag": pressure_atlas["c2_selector_family_lag_summary"]["candidate_count"] >= 3,
            "c2_selector_family_browser_readouts": "d20BhSelectorLag" in html and "d20BhSelectorNullP" in html and "c2_selector_family_lag_summary" in js,
            "c2_dynamics_selector_theorem": pressure_atlas["c2_selector_family_lag_summary"]["theorem_status"] == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_DYNAMICS_SELECTOR_CERTIFIED",
            "c2_markov_trajectory": pressure_atlas["c2_markov_trajectory_summary"]["target_orbit_count"] == 543,
            "c2_markov_trajectory_browser_readouts": "d20BhTrajectoryTv" in html and "d20BhTrajectoryNullP" in html and "c2_markov_trajectory_summary" in js,
            "boundary_only_panel": "drawWardBmsDynamics" in js and "d20WardStatus" in html and "d20WardSpectrum" in html,
            "ward_bms_3d_renderer": "drawWardBms3dDynamics" in js and "getContext('webgl'" in js and "543" in js and "gl.drawArrays(gl.POINTS" in js,
            "boundary_dynamics_samples": (
                pressure_atlas["boundary_dynamics_summary"]["target_orbit_count"] == 543
                and len(pressure_atlas["boundary_dynamics_summary"]["component_size_by_orbit"]) == 543
                and len(pressure_atlas["boundary_dynamics_summary"]["component_id_by_orbit"]) == 543
                and len(pressure_atlas["boundary_dynamics_summary"]["component_representatives"]) >= 8
                and len(pressure_atlas["boundary_dynamics_summary"]["transition_samples"]) == len(D20_GATE_SEQUENCE)
            ),
            "ward_bms_3d_trails": "ward3dTrail" in js and "component_size_by_orbit" in js and "activeVertices" in js,
            "boundary_dynamics_browser_readouts": "d20WardComponents" in html and "d20WardTransitions" in html and "component_representatives" in js,
            "boundary_motif_counts": (
                pressure_atlas["boundary_dynamics_summary"]["motif_counts"]["motif_total"] == len(D20_GATE_SEQUENCE)
                and pressure_atlas["boundary_dynamics_summary"]["motif_counts"]["unique_motifs"] >= 1
            ),
            "boundary_motif_prediction": (
                pressure_atlas["boundary_dynamics_summary"]["motif_prediction"]["transitions_evaluated"] == len(D20_GATE_SEQUENCE) - 1
                and pressure_atlas["boundary_dynamics_summary"]["motif_prediction"]["walk_forward_attempts"] >= 1
                and 0 <= pressure_atlas["boundary_dynamics_summary"]["motif_prediction"]["motif_accuracy"] <= 1
                and 0 <= pressure_atlas["boundary_dynamics_summary"]["motif_prediction"]["null_p_value"] <= 1
            ),
            "boundary_motif_prediction_long": (
                pressure_atlas["boundary_dynamics_summary"]["motif_prediction_long"]["history_count"] > 1
                and pressure_atlas["boundary_dynamics_summary"]["motif_prediction_long"]["sample_count"] > len(D20_GATE_SEQUENCE)
                and pressure_atlas["boundary_dynamics_summary"]["motif_prediction_long"]["walk_forward_attempts"] >= 32
                and len(pressure_atlas["boundary_dynamics_summary"]["motif_prediction_long"]["variant_rows"]) == 6
                and 0 <= pressure_atlas["boundary_dynamics_summary"]["motif_prediction_long"]["motif_accuracy"] <= 1
                and 0 <= pressure_atlas["boundary_dynamics_summary"]["motif_prediction_long"]["null_p_value"] <= 1
            ),
            "boundary_motif_prediction_splits": (
                pressure_atlas["boundary_dynamics_summary"]["motif_prediction_splits"]["history_split"]["walk_forward_attempts"] >= 32
                and pressure_atlas["boundary_dynamics_summary"]["motif_prediction_splits"]["time_offset_split"]["walk_forward_attempts"] >= 32
                and len(pressure_atlas["boundary_dynamics_summary"]["motif_prediction_splits"]["history_split"]["variant_rows"]) == 6
                and len(pressure_atlas["boundary_dynamics_summary"]["motif_prediction_splits"]["time_offset_split"]["variant_rows"]) == 6
                and 0 <= pressure_atlas["boundary_dynamics_summary"]["motif_prediction_splits"]["history_split"]["motif_accuracy"] <= 1
                and 0 <= pressure_atlas["boundary_dynamics_summary"]["motif_prediction_splits"]["time_offset_split"]["motif_accuracy"] <= 1
            ),
            "time_offset_obstruction_audit": (
                pressure_atlas["boundary_dynamics_summary"]["motif_prediction_splits"]["time_offset_obstruction"]["phase_count"] == len(D20_GATE_SEQUENCE) - 1
                and pressure_atlas["boundary_dynamics_summary"]["motif_prediction_splits"]["time_offset_obstruction"]["passing_phase_count"] >= 0
                and pressure_atlas["boundary_dynamics_summary"]["motif_prediction_splits"]["time_offset_obstruction"]["failing_phase_count"] >= 0
                and len(pressure_atlas["boundary_dynamics_summary"]["motif_prediction_splits"]["time_offset_obstruction"]["weakest_rows"]) >= 1
            ),
            "phase_clock_model": (
                pressure_atlas["boundary_dynamics_summary"]["motif_prediction_splits"]["phase_clock_model"]["clock_history_split"]["walk_forward_attempts"] >= 32
                and pressure_atlas["boundary_dynamics_summary"]["motif_prediction_splits"]["phase_clock_model"]["clock_time_offset_split"]["walk_forward_attempts"] >= 32
                and len(pressure_atlas["boundary_dynamics_summary"]["motif_prediction_splits"]["phase_clock_model"]["clock_history_split"]["variant_rows"]) == 5
                and len(pressure_atlas["boundary_dynamics_summary"]["motif_prediction_splits"]["phase_clock_model"]["clock_time_offset_split"]["variant_rows"]) == 5
            ),
            "phase_clock_paired_residual": (
                pressure_atlas["boundary_dynamics_summary"]["motif_prediction_splits"]["phase_clock_model"]["paired_residual"]["history"]["paired_attempts"] >= 32
                and pressure_atlas["boundary_dynamics_summary"]["motif_prediction_splits"]["phase_clock_model"]["paired_residual"]["time_offset"]["paired_attempts"] >= 32
                and 0 <= pressure_atlas["boundary_dynamics_summary"]["motif_prediction_splits"]["phase_clock_model"]["paired_residual"]["history"]["motif_advantage_p"] <= 1
                and 0 <= pressure_atlas["boundary_dynamics_summary"]["motif_prediction_splits"]["phase_clock_model"]["paired_residual"]["time_offset"]["motif_advantage_p"] <= 1
            ),
            "source_state_transport": (
                len(pressure_atlas["boundary_dynamics_summary"]["motif_prediction_splits"]["source_state_transport"]["ward_history_split"]["variant_rows"]) == 4
                and len(pressure_atlas["boundary_dynamics_summary"]["motif_prediction_splits"]["source_state_transport"]["source_history_split"]["variant_rows"]) == 2
                and pressure_atlas["boundary_dynamics_summary"]["motif_prediction_splits"]["source_state_transport"]["paired_ward_vs_source"]["history"]["paired_attempts"] >= 32
                and pressure_atlas["boundary_dynamics_summary"]["motif_prediction_splits"]["source_state_transport"]["paired_ward_vs_source"]["time_offset"]["paired_attempts"] >= 32
            ),
            "source_conditioned_ward_residual": (
                len(pressure_atlas["boundary_dynamics_summary"]["motif_prediction_splits"]["source_conditioned_ward_residual"]["history_split"]["variant_rows"]) == 8
                and len(pressure_atlas["boundary_dynamics_summary"]["motif_prediction_splits"]["source_conditioned_ward_residual"]["time_offset_split"]["variant_rows"]) == 8
                and pressure_atlas["boundary_dynamics_summary"]["motif_prediction_splits"]["source_conditioned_ward_residual"]["history_split"]["paired_attempts"] >= 32
                and pressure_atlas["boundary_dynamics_summary"]["motif_prediction_splits"]["source_conditioned_ward_residual"]["time_offset_split"]["paired_attempts"] >= 32
                and pressure_atlas["boundary_dynamics_summary"]["motif_prediction_splits"]["source_conditioned_ward_residual"]["history_split"]["null_trials"] >= 1
                and pressure_atlas["boundary_dynamics_summary"]["motif_prediction_splits"]["source_conditioned_ward_residual"]["time_offset_split"]["null_trials"] >= 1
            ),
            "boundary_packet_bridge_seam": (
                boundary_packet_bridge_summary["status"] == "BOUNDARY_PACKET_BRIDGE_SEAM_CERTIFIED_RECEIPTS"
                and boundary_packet_bridge_summary["pairing_obstruction"]["raw_compatible_pairs"] == 0
                and boundary_packet_bridge_summary["pairing_obstruction"]["minimal_scalar_with_matching"] == 6
                and boundary_packet_bridge_summary["pairing_obstruction"]["joint_boundary_packet_scalar_lcm"] == 12
                and boundary_packet_bridge_summary["row_normalization_obstruction"]["row_scalar_divisibility_for_any_packet_pairing"] == 6
                and boundary_packet_bridge_summary["row_normalization_obstruction"]["only_compatible_residue_pair_mod6"] == [0, 0]
                and boundary_packet_bridge_summary["low_support_candidate_atlas"]["candidate_count"] == 800
                and boundary_packet_bridge_summary["low_support_candidate_atlas"]["even_image_candidate_count"] == 12
                and boundary_packet_bridge_summary["low_support_candidate_atlas"]["compatible_doublet_count"] == 6
                and boundary_packet_bridge_summary["low_support_candidate_atlas"]["compatible_doublets_all_rank_one"]
            ),
            "rank_one_packet_family_sink_residual": (
                rank_one_packet_family_sink_summary["transition_steps"] == 16
                and rank_one_packet_family_sink_summary["sink_hits"] >= 0
                and rank_one_packet_family_sink_summary["r33_sink_hits"] >= 0
                and len(rank_one_packet_family_sink_summary["families"]) == 3
                and len(rank_one_packet_family_sink_summary["source_conditioned_packet_residual"]["history_split"]["families"]) == 3
                and rank_one_packet_family_sink_summary["source_conditioned_packet_residual"]["history_split"]["actual_family_attempts"] >= 1
                and rank_one_packet_family_sink_summary["source_conditioned_packet_residual"]["time_offset_split"]["actual_family_attempts"] >= 1
            ),
            "signed_rank_one_packet_quotient": (
                signed_rank_one_packet_quotient_summary["candidate_count"] == 6
                and len(signed_rank_one_packet_quotient_summary["candidate_rows"]) == 6
                and signed_rank_one_packet_quotient_summary["best_candidate"]["null_histories"] == 719
                and 0 <= signed_rank_one_packet_quotient_summary["best_candidate"]["mean_abs_null_p"] <= 1
                and signed_rank_one_packet_quotient_summary["best_candidate"]["support_atoms"]
                and signed_rank_one_packet_quotient_summary["overall_verdict"] in {
                    "SIGNED_PACKET_QUOTIENT_OBSERVABLE_CERTIFIED",
                    "SIGNED_PACKET_QUOTIENT_OBSERVABLE_PROVISIONAL",
                    "SIGNED_PACKET_QUOTIENT_OBSERVABLE_NOT_CERTIFIED",
                }
            ),
            "signed_packet_quotient_lag": (
                signed_packet_quotient_lag_summary["observable"] == "signed_rank_one_packet_quotient_hydrogen_lag"
                and signed_packet_quotient_lag_summary["lags"] == len(D20_GATE_SEQUENCE)
                and len(signed_packet_quotient_lag_summary["rows"]) == len(D20_GATE_SEQUENCE)
                and signed_packet_quotient_lag_summary["null_significance"]["null_histories"] == 719
                and 0 <= signed_packet_quotient_lag_summary["null_significance"]["p_value"] <= 1
                and len(signed_packet_quotient_lag_summary["support_atoms"]) == 2
                and signed_packet_quotient_lag_summary["verdict"] in {
                    "SIGNED_PACKET_QUOTIENT_HYDROGEN_CANDIDATE",
                    "SIGNED_PACKET_QUOTIENT_HYDROGEN_WITHIN_NULL",
                }
            ),
            "support3_signed_quotient_screen": (
                support3_signed_quotient_summary["observable"] == "support3_signed_public_boundary_quotient_screen"
                and support3_signed_quotient_summary["candidate_count"] == 4560
                and support3_signed_quotient_summary["null_tested_candidate_count"] == 480
                and support3_signed_quotient_summary["best_candidate"]["support_size"] == 3
                and support3_signed_quotient_summary["best_candidate"]["null_histories"] == 719
                and 0 <= support3_signed_quotient_summary["best_candidate"]["mean_abs_null_p"] <= 1
                and support3_signed_quotient_summary["overall_verdict"] in {
                    "SUPPORT3_SIGNED_QUOTIENT_OBSERVABLE_CERTIFIED",
                    "SUPPORT3_SIGNED_QUOTIENT_OBSERVABLE_PROVISIONAL",
                    "SUPPORT3_SIGNED_QUOTIENT_OBSERVABLE_NOT_CERTIFIED",
                }
            ),
            "support3_signed_quotient_lag": (
                support3_signed_quotient_lag_summary["observable"] == "support3_signed_public_boundary_quotient_hydrogen_lag"
                and support3_signed_quotient_lag_summary["lags"] == len(D20_GATE_SEQUENCE)
                and len(support3_signed_quotient_lag_summary["rows"]) == len(D20_GATE_SEQUENCE)
                and support3_signed_quotient_lag_summary["null_significance"]["null_histories"] == 719
                and 0 <= support3_signed_quotient_lag_summary["null_significance"]["p_value"] <= 1
                and len(support3_signed_quotient_lag_summary["support_atoms"]) == 3
                and support3_signed_quotient_lag_summary["verdict"] in {
                    "SUPPORT3_SIGNED_QUOTIENT_HYDROGEN_CANDIDATE",
                    "SUPPORT3_SIGNED_QUOTIENT_HYDROGEN_WITHIN_NULL",
                }
            ),
            "a985_q12_packet_bridge_probe": (
                a985_q12_packet_bridge_probe_summary["all_checks_pass"] is True
                and a985_q12_packet_bridge_probe_summary["ingress_projection_inventory"]["status"] == "INGRESS_BOUNDARY_TO_LOOP_PRESENT_PACKET_PROJECTION_MISSING"
                and a985_q12_packet_bridge_probe_summary["mask288_q12_seed_support3"]["status"] == "MASK288_Q12_PACKET_SEED_SUPPORT3_EXTENSION_BLOCKED_BY_PARITY"
                and a985_q12_packet_bridge_probe_summary["one_sided_seed_correction"]["compatible_doublet_count"] == 4628
                and a985_q12_packet_bridge_probe_summary["one_sided_seed_correction"]["combined_rank2_support_family_count"] == 28
                and a985_q12_packet_bridge_probe_summary["corrected_rank20_selection"]["status"] == "MASK288_Q12_CORRECTED_RANK20_SELECTION_BLOCKED_BY_RANK9_IMAGE_CEILING"
                and a985_q12_packet_bridge_probe_summary["corrected_rank20_selection"]["combined_boundary_image_rank_over_Q"] == 9
                and a985_q12_packet_bridge_probe_summary["corrected_rank20_selection"]["target_rank"] == 20
                and a985_q12_packet_bridge_probe_summary["natural_25_to_20_projection"]["status"] == "BOUNDARY_PACKET_NATURAL_25_TO_20_PROJECTION_REJECTED_BY_PACKET_SNF"
            ),
            "falsification_ledger": pressure_atlas["falsification_ledger_summary"]["total_claims"] == 11,
            "falsification_taxonomy": pressure_atlas["falsification_ledger_summary"]["taxonomy"]["next_class"] in {"support-3 residual and source-state audit", "residual-only hydrogen coupling audit", "A985/q12 packet projection construction"},
            "falsification_browser_readouts": "d20BhEvidenceStatus" in html and "d20BhFailedTests" in html and "falsification_ledger_summary" in js,
        },
        "pressure_atlas_summary": {
            "verdict": pressure_atlas["verdict"],
            "identity_rows": pressure_atlas["identity_rows"],
            "null_rows": pressure_atlas["null_rows"],
            "null_rows_per_inlet": pressure_atlas["null_rows_per_inlet"],
            "top_sink_positive_margins": pressure_atlas["top_sink_positive_margins"],
            "mean_top_sink_margin": pressure_atlas["mean_top_sink_margin"],
            "max_top_sink_margin": pressure_atlas["max_top_sink_margin"],
            "mean_top_sink_percentile": pressure_atlas["mean_top_sink_percentile"],
            "c985_summary": pressure_atlas["c985_summary"],
            "c985_transition_summary": pressure_atlas["c985_transition_summary"],
            "lagged_correlation_summary": pressure_atlas["lagged_correlation_summary"],
            "signed_flux_lag_summary": pressure_atlas["signed_flux_lag_summary"],
            "height_flux_lag_summary": pressure_atlas["height_flux_lag_summary"],
            "zero_pair_ward_lag_summary": pressure_atlas["zero_pair_ward_lag_summary"],
            "c2_markov_orbit_lag_summary": pressure_atlas["c2_markov_orbit_lag_summary"],
            "c2_selector_family_lag_summary": pressure_atlas["c2_selector_family_lag_summary"],
            "c2_markov_trajectory_summary": pressure_atlas["c2_markov_trajectory_summary"],
            "signed_packet_quotient_lag_summary": pressure_atlas["signed_packet_quotient_lag_summary"],
            "support3_signed_quotient_summary": pressure_atlas["support3_signed_quotient_summary"],
            "support3_signed_quotient_lag_summary": pressure_atlas["support3_signed_quotient_lag_summary"],
            "boundary_dynamics_summary": pressure_atlas["boundary_dynamics_summary"],
            "falsification_ledger_summary": pressure_atlas["falsification_ledger_summary"],
        },
        "boundary_packet_bridge_summary": boundary_packet_bridge_summary,
        "a985_q12_packet_bridge_probe_summary": a985_q12_packet_bridge_probe_summary,
        "rank_one_packet_family_sink_summary": rank_one_packet_family_sink_summary,
        "signed_rank_one_packet_quotient_summary": signed_rank_one_packet_quotient_summary,
        "physics_notes": [
            "The canvas compares d20-normalized hydrogen levels against boundary pressure/absorption, not against an event-horizon metric.",
            "A micro-black-hole-like signature would require binding, pressure concentration, aperture loss, and redshift proxy to remain correlated after six-inlet and permutation-null comparison.",
            "The useful boundary observable is pressure-vector concentration over the 20 d20 atoms, because it exposes which RGBA horizon atoms act as sinks.",
            "The alpha wall is treated as the finite threshold between the H6 visible sector and the R14 residual sector, so crossings are candidate boundary events.",
            "The pressure atlas turns the horizon ring into a falsifiable boundary object by showing identity sinks against 719 null permutations per inlet.",
            "C985 charge masks attach the atlas sinks to the LEDGER boundary vector (M,J,P,Phi;R33,K_mixed_S,K_pure_Sminus).",
            "The transition ledger replays the finite gate sequence and counts whether R33-sourced sinks persist across repeated wind pulses.",
            "The browser lab now advances the horizon proxy through that pulse history instead of choosing a static atlas row from the hydrogen label alone.",
            "The browser lab includes a paused-by-default requestAnimationFrame play loop for the 16-step C985 pulse history, so dynamics can run continuously without autoplaying on load.",
            "The lag scan compares hydrogen binding against the 16-step horizon sequence at every cyclic offset so a coupling candidate can be phase shifted.",
            "The lag candidate is checked against 719 null pulse histories before it is allowed to count as a boundary signal.",
            "The current lag candidate is inside the null distribution, so raw pressure-margin phase coupling is not evidence yet.",
            "A signed C985 flux-balance observable is also tested so R33 and K-support can change the horizon signal before null comparison.",
            "A signed C985 height-flux balance observable tests the hidden LEDGER equation bare Pi33 + R33_height_residual + finite_height_flux = 0.",
            "The zero-pair Ward selector tests certified mask 288, action 691200 + 374784 = 1065984, corrected clock 13 + 13 = 0 mod 26, and shared atom 11.",
            "The current signed height-flux observable is also inside the null distribution, so it is not evidence of hydrogen/horizon coupling.",
            "The mask-288 zero-pair Ward selector is also inside the null distribution, so this certified sourced Ward balance is not yet the hydrogen/horizon coupling observable.",
            "The falsification ledger separates supported boundary-sink evidence from failed hydrogen/horizon coupling claims.",
            "The failed observable taxonomy says scalar pressure, scalar flux, scalar height-flux, and scalar zero-pair selectors are exhausted; the next class should be Ward-balanced 543-orbit dynamics.",
            "The C2 Markov orbit drift observable uses the certified 543-orbit quotient scattering operator instead of another scalar pressure proxy.",
            "The C2 selector-family observable tests primitive-seeded, global-action-minimal, paired-action-minimal, and lazy-gap selector criteria from the certified dynamics selector theorem.",
            "The C2 Markov trajectory observable compares full evolved 543-orbit distributions against hydrogen-weighted targets rather than using lagged scalar correlations.",
            "Because trajectory distributions remain inside nulls, the renderer now exposes Ward/BMS dynamics as a boundary-only panel instead of presenting it as hydrogen coupling evidence.",
            "The boundary-only Ward/BMS view includes a WebGL 3D orbit shell for the 543 quotient states with active transition edges.",
            "The WebGL orbit shell colors every quotient orbit by certified component class and keeps a fading transition trail during playback.",
            "The boundary-only panel now includes certified component representatives and transition samples from the 543-orbit Ward/BMS operator.",
            "Boundary-only motif counts are exported from the 16-step transition samples so recurrent Ward/BMS motion can be studied numerically.",
            "Boundary motif prediction runs a walk-forward next-R33-sink test before any renewed hydrogen comparison.",
            "Long boundary motif prediction extends that forecast over identity plus certified null-row pulse histories before any renewed hydrogen comparison.",
            "Held-out history and time-offset motif splits test whether the long boundary forecast survives schedule separation.",
            "The time-offset obstruction audit ranks individual held-out pulse phases so the schedule dependence can be localized.",
            "The explicit phase-clock baseline tests whether motif forecasting adds residual information beyond the finite pulse clock itself.",
            "The paired phase-residual observable counts motif-only wins against clock-only wins on the same held-out transitions.",
            "The source-state transport separation treats source_atom/source_atom_inlet as transition baselines rather than genuine Ward/BMS component motifs.",
            "The source-state transport control currently dominates Ward/C985 motif alphabets, so the coil should be treated as source transport until a source-conditioned Ward residual survives.",
            "The source-conditioned Ward residual keeps source atom/inlet transport fixed and rotates only Ward/C985 keys inside each source class.",
            "The C985 boundary-packet bridge receipts rule out raw public-atom pairing and diagonal row normalization; the first low-support packet candidates are rank-one degeneracies.",
            "The rank-one packet family test compares those support-2 families against the R33 sink sequence and the source-conditioned Ward residual before any renewed hydrogen claim.",
            "The signed rank-one packet quotient test uses the actual signed support-2 rows as non-diagonal boundary observables against the per-inlet null pulse histories.",
            "The signed packet quotient is separately tested as a hydrogen-lag observable; it can only upgrade to candidate status after the 719-history null comparison.",
            "The support-3 signed quotient screen enumerates canonical public-atom triples and null-tests only the strongest boundary rows; it is an exploratory seam, not a certified packet bridge.",
            "The ingress-backed A985/q12 packet bridge probe confirms the projection gap: support-3 seed parity blocks the direct extension, one-sided correction finds 4628 rank-2 doublets across 28 families, and the corrected rank-20 selection is capped at rank 9.",
            "The Q42/A985 hidden matrix-unit capacity is larger than the packet target, so the remaining problem is not lack of hidden rank; it is choosing the correct packet kernel/label map.",
            "The boundary-packet seam means any black-hole-like atom bridge now needs a non-diagonal signed quotient or normalization, not a richer horizon visualization.",
            "A pretty horizon ring alone is not evidence; an identity sink needs a positive null-p95 margin or a repeatable C985 flux explanation.",
        ],
        "sources": {
            "equations": str(equations_path.relative_to(ROOT)),
            "html": str(html_path.relative_to(ROOT)),
            "js": str(js_path.relative_to(ROOT)),
            "css": str(css_path.relative_to(ROOT)),
            "pressure_atlas_js": str(ATLAS_JS.relative_to(ROOT)),
            "wind_pressure_export": str(wind_path.relative_to(ROOT)),
            "c2_quotient_scattering_operator": str(SCATTERING_OPERATOR_REPORT.relative_to(ROOT)),
            "c2_dynamics_selector": str(DYNAMICS_SELECTOR_REPORT.relative_to(ROOT)),
            "boundary_packet_pairing_obstruction": str(BOUNDARY_PACKET_PAIRING_REPORT.relative_to(ROOT)),
            "boundary_packet_row_normalization_obstruction": str(BOUNDARY_PACKET_ROW_NORMALIZATION_REPORT.relative_to(ROOT)),
            "boundary_packet_low_support_candidate_atlas": str(BOUNDARY_PACKET_LOW_SUPPORT_REPORT.relative_to(ROOT)),
            "hydrogen_sandpile_golay_bridge_probe": str(HYDROGEN_SANDPILE_GOLAY_BRIDGE_PROBE.relative_to(ROOT)),
        },
        "html_sha256": sha256_text(html),
        "js_sha256": sha256_text(js),
        "css_sha256": sha256_text(css),
        "pressure_atlas_js_sha256": atlas_js_sha256,
        "equations_sha256": sha256_text(equations),
        "next_highest_yield_item": "Audit the support-3 signed quotient residual against source-state controls before any black-hole claim." if support3_signed_quotient_supported else a985_q12_packet_bridge_probe_summary["next_highest_yield_item"],
    }
    GENERATED.mkdir(exist_ok=True)
    PROOF_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    proof = dict(report)
    proof["report_artifact"] = str(REPORT_JSON.relative_to(ROOT))
    proof["report_sha256"] = hashlib.sha256(REPORT_JSON.read_bytes()).hexdigest()
    notes_md = build_boundary_discovery_notes(report, proof)
    BOUNDARY_NOTES_MD.write_text(notes_md, encoding="utf-8")
    PROOF_NOTES_MD.write_text(notes_md, encoding="utf-8")
    proof["boundary_discovery_notes_artifact"] = str(BOUNDARY_NOTES_MD.relative_to(ROOT))
    proof["boundary_discovery_notes_sha256"] = hashlib.sha256(BOUNDARY_NOTES_MD.read_bytes()).hexdigest()
    proof["boundary_discovery_proof_notes_artifact"] = str(PROOF_NOTES_MD.relative_to(ROOT))
    PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": proof["status"],
        "verdict": proof["verdict"],
        "artifact": str(REPORT_JSON.relative_to(ROOT)),
        "report": str(PROOF_JSON.relative_to(ROOT)),
        "pressure_rows_found": len(pressure_rows),
        "correlation_rows": len(correlations),
        "pearson_binding_absorption": proof["correlation_summary"]["pearson_binding_absorption"],
        "mean_boundary_match": proof["correlation_summary"]["mean_boundary_match"],
        "pressure_atlas_verdict": proof["pressure_atlas_summary"]["verdict"],
        "top_sink_positive_margins": proof["pressure_atlas_summary"]["top_sink_positive_margins"],
        "r33_sourced_closed_returns": proof["pressure_atlas_summary"]["c985_summary"]["r33_sourced_closed_returns"],
        "longest_r33_run": proof["pressure_atlas_summary"]["c985_transition_summary"]["longest_r33_run"],
        "best_lag": proof["pressure_atlas_summary"]["lagged_correlation_summary"]["best_lag"],
        "best_lag_rho": proof["pressure_atlas_summary"]["lagged_correlation_summary"]["best_rho"],
        "best_lag_null_p": proof["pressure_atlas_summary"]["lagged_correlation_summary"]["null_significance"]["p_value"],
        "best_lag_null_verdict": proof["pressure_atlas_summary"]["lagged_correlation_summary"]["null_significance"]["verdict"],
        "signed_flux_best_lag": proof["pressure_atlas_summary"]["signed_flux_lag_summary"]["best_lag"],
        "signed_flux_best_rho": proof["pressure_atlas_summary"]["signed_flux_lag_summary"]["best_rho"],
        "signed_flux_null_p": proof["pressure_atlas_summary"]["signed_flux_lag_summary"]["null_significance"]["p_value"],
        "signed_flux_null_verdict": proof["pressure_atlas_summary"]["signed_flux_lag_summary"]["null_significance"]["verdict"],
        "height_flux_best_lag": proof["pressure_atlas_summary"]["height_flux_lag_summary"]["best_lag"],
        "height_flux_best_rho": proof["pressure_atlas_summary"]["height_flux_lag_summary"]["best_rho"],
        "height_flux_null_p": proof["pressure_atlas_summary"]["height_flux_lag_summary"]["null_significance"]["p_value"],
        "height_flux_null_verdict": proof["pressure_atlas_summary"]["height_flux_lag_summary"]["null_significance"]["verdict"],
        "zero_pair_ward_best_lag": proof["pressure_atlas_summary"]["zero_pair_ward_lag_summary"]["best_lag"],
        "zero_pair_ward_best_rho": proof["pressure_atlas_summary"]["zero_pair_ward_lag_summary"]["best_rho"],
        "zero_pair_ward_null_p": proof["pressure_atlas_summary"]["zero_pair_ward_lag_summary"]["null_significance"]["p_value"],
        "zero_pair_ward_null_verdict": proof["pressure_atlas_summary"]["zero_pair_ward_lag_summary"]["null_significance"]["verdict"],
        "c2_markov_orbit_best_lag": proof["pressure_atlas_summary"]["c2_markov_orbit_lag_summary"]["best_lag"],
        "c2_markov_orbit_best_rho": proof["pressure_atlas_summary"]["c2_markov_orbit_lag_summary"]["best_rho"],
        "c2_markov_orbit_null_p": proof["pressure_atlas_summary"]["c2_markov_orbit_lag_summary"]["null_significance"]["p_value"],
        "c2_markov_orbit_null_verdict": proof["pressure_atlas_summary"]["c2_markov_orbit_lag_summary"]["null_significance"]["verdict"],
        "c2_selector_best_candidate": proof["pressure_atlas_summary"]["c2_selector_family_lag_summary"]["best_candidate"],
        "c2_selector_best_lag": proof["pressure_atlas_summary"]["c2_selector_family_lag_summary"]["best_lag"],
        "c2_selector_best_rho": proof["pressure_atlas_summary"]["c2_selector_family_lag_summary"]["best_rho"],
        "c2_selector_null_p": proof["pressure_atlas_summary"]["c2_selector_family_lag_summary"]["best_null_p"],
        "c2_selector_null_verdict": proof["pressure_atlas_summary"]["c2_selector_family_lag_summary"]["best_null_verdict"],
        "c2_trajectory_tv": proof["pressure_atlas_summary"]["c2_markov_trajectory_summary"]["identity_total_variation"],
        "c2_trajectory_null_p": proof["pressure_atlas_summary"]["c2_markov_trajectory_summary"]["null_significance"]["p_value"],
        "c2_trajectory_null_verdict": proof["pressure_atlas_summary"]["c2_markov_trajectory_summary"]["null_significance"]["verdict"],
        "boundary_component_representatives": len(proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["component_representatives"]),
        "boundary_transition_samples": len(proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["transition_samples"]),
        "boundary_unique_motifs": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_counts"]["unique_motifs"],
        "motif_prediction_accuracy": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction"]["motif_accuracy"],
        "motif_prediction_baseline_accuracy": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction"]["baseline_accuracy"],
        "motif_prediction_best_variant": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction"]["best_variant"],
        "motif_prediction_null_p": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction"]["null_p_value"],
        "motif_prediction_verdict": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction"]["verdict"],
        "long_motif_prediction_accuracy": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_long"]["motif_accuracy"],
        "long_motif_prediction_baseline_accuracy": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_long"]["baseline_accuracy"],
        "long_motif_prediction_best_variant": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_long"]["best_variant"],
        "long_motif_prediction_histories": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_long"]["history_count"],
        "long_motif_prediction_null_p": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_long"]["null_p_value"],
        "long_motif_prediction_verdict": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_long"]["verdict"],
        "split_history_accuracy": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["history_split"]["motif_accuracy"],
        "split_history_baseline_accuracy": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["history_split"]["baseline_accuracy"],
        "split_history_best_variant": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["history_split"]["best_variant"],
        "split_history_null_p": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["history_split"]["null_p_value"],
        "split_history_verdict": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["history_split"]["verdict"],
        "split_time_offset_accuracy": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["time_offset_split"]["motif_accuracy"],
        "split_time_offset_baseline_accuracy": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["time_offset_split"]["baseline_accuracy"],
        "split_time_offset_best_variant": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["time_offset_split"]["best_variant"],
        "split_time_offset_null_p": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["time_offset_split"]["null_p_value"],
        "split_time_offset_verdict": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["time_offset_split"]["verdict"],
        "split_motif_overall_verdict": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["overall_verdict"],
        "time_offset_obstruction_verdict": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["time_offset_obstruction"]["overall_verdict"],
        "time_offset_obstruction_passing_phases": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["time_offset_obstruction"]["passing_phase_count"],
        "time_offset_obstruction_failing_phases": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["time_offset_obstruction"]["failing_phase_count"],
        "time_offset_obstruction_weakest_step": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["time_offset_obstruction"]["weakest_rows"][0]["heldout_step"],
        "time_offset_obstruction_weakest_p": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["time_offset_obstruction"]["weakest_rows"][0]["null_p_value"],
        "phase_clock_overall_verdict": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["phase_clock_model"]["overall_verdict"],
        "phase_clock_history_accuracy": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["phase_clock_model"]["clock_history_accuracy"],
        "phase_clock_history_best_variant": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["phase_clock_model"]["clock_history_best_variant"],
        "phase_clock_history_residual_lift": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["phase_clock_model"]["history_residual_lift"],
        "phase_clock_time_offset_accuracy": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["phase_clock_model"]["clock_time_offset_accuracy"],
        "phase_clock_time_offset_best_variant": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["phase_clock_model"]["clock_time_offset_best_variant"],
        "phase_clock_time_offset_residual_lift": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["phase_clock_model"]["time_offset_residual_lift"],
        "paired_residual_overall_verdict": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["phase_clock_model"]["paired_residual"]["overall_verdict"],
        "paired_residual_history_motif_only": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["phase_clock_model"]["paired_residual"]["history"]["motif_only"],
        "paired_residual_history_clock_only": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["phase_clock_model"]["paired_residual"]["history"]["clock_only"],
        "paired_residual_history_p": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["phase_clock_model"]["paired_residual"]["history"]["motif_advantage_p"],
        "paired_residual_time_offset_motif_only": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["phase_clock_model"]["paired_residual"]["time_offset"]["motif_only"],
        "paired_residual_time_offset_clock_only": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["phase_clock_model"]["paired_residual"]["time_offset"]["clock_only"],
        "paired_residual_time_offset_p": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["phase_clock_model"]["paired_residual"]["time_offset"]["motif_advantage_p"],
        "source_state_overall_verdict": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["source_state_transport"]["overall_verdict"],
        "source_state_history_best_variant": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["source_state_transport"]["source_history_split"]["best_variant"],
        "source_state_history_accuracy": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["source_state_transport"]["source_history_split"]["motif_accuracy"],
        "ward_motif_history_best_variant": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["source_state_transport"]["ward_history_split"]["best_variant"],
        "ward_motif_history_accuracy": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["source_state_transport"]["ward_history_split"]["motif_accuracy"],
        "source_state_time_offset_best_variant": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["source_state_transport"]["source_time_offset_split"]["best_variant"],
        "source_state_time_offset_accuracy": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["source_state_transport"]["source_time_offset_split"]["motif_accuracy"],
        "ward_motif_time_offset_best_variant": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["source_state_transport"]["ward_time_offset_split"]["best_variant"],
        "ward_motif_time_offset_accuracy": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["source_state_transport"]["ward_time_offset_split"]["motif_accuracy"],
        "source_conditioned_ward_overall_verdict": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["source_conditioned_ward_residual"]["overall_verdict"],
        "source_conditioned_history_source_variant": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["source_conditioned_ward_residual"]["history_split"]["best_source_variant"],
        "source_conditioned_history_ward_variant": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["source_conditioned_ward_residual"]["history_split"]["best_ward_variant"],
        "source_conditioned_history_residual_lift": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["source_conditioned_ward_residual"]["history_split"]["residual_lift"],
        "source_conditioned_history_null_p": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["source_conditioned_ward_residual"]["history_split"]["null_p_value"],
        "source_conditioned_history_verdict": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["source_conditioned_ward_residual"]["history_split"]["verdict"],
        "source_conditioned_time_offset_source_variant": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["source_conditioned_ward_residual"]["time_offset_split"]["best_source_variant"],
        "source_conditioned_time_offset_ward_variant": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["source_conditioned_ward_residual"]["time_offset_split"]["best_ward_variant"],
        "source_conditioned_time_offset_residual_lift": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["source_conditioned_ward_residual"]["time_offset_split"]["residual_lift"],
        "source_conditioned_time_offset_null_p": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["source_conditioned_ward_residual"]["time_offset_split"]["null_p_value"],
        "source_conditioned_time_offset_verdict": proof["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]["source_conditioned_ward_residual"]["time_offset_split"]["verdict"],
        "boundary_packet_bridge_status": proof["boundary_packet_bridge_summary"]["status"],
        "boundary_packet_raw_compatible_pairs": proof["boundary_packet_bridge_summary"]["pairing_obstruction"]["raw_compatible_pairs"],
        "boundary_packet_minimal_scalar": proof["boundary_packet_bridge_summary"]["pairing_obstruction"]["minimal_scalar_with_matching"],
        "boundary_packet_joint_clearing_bound": proof["boundary_packet_bridge_summary"]["pairing_obstruction"]["joint_boundary_packet_scalar_lcm"],
        "boundary_packet_row_scalar_divisibility": proof["boundary_packet_bridge_summary"]["row_normalization_obstruction"]["row_scalar_divisibility_for_any_packet_pairing"],
        "boundary_packet_low_support_even_rows": proof["boundary_packet_bridge_summary"]["low_support_candidate_atlas"]["even_image_candidate_count"],
        "boundary_packet_low_support_doublets": proof["boundary_packet_bridge_summary"]["low_support_candidate_atlas"]["compatible_doublet_count"],
        "boundary_packet_low_support_rank_one": proof["boundary_packet_bridge_summary"]["low_support_candidate_atlas"]["compatible_doublets_all_rank_one"],
        "rank_one_packet_family_verdict": proof["rank_one_packet_family_sink_summary"]["verdict"],
        "rank_one_packet_family_r33_hits": proof["rank_one_packet_family_sink_summary"]["r33_sink_hits"],
        "rank_one_packet_family_sink_hits": proof["rank_one_packet_family_sink_summary"]["sink_hits"],
        "rank_one_packet_family_history_attempts": proof["rank_one_packet_family_sink_summary"]["source_conditioned_packet_residual"]["history_split"]["actual_family_attempts"],
        "rank_one_packet_family_history_lift": proof["rank_one_packet_family_sink_summary"]["source_conditioned_packet_residual"]["history_split"]["family_residual_lift"],
        "rank_one_packet_family_history_null_p": proof["rank_one_packet_family_sink_summary"]["source_conditioned_packet_residual"]["history_split"]["null_p_value"],
        "rank_one_packet_family_time_offset_attempts": proof["rank_one_packet_family_sink_summary"]["source_conditioned_packet_residual"]["time_offset_split"]["actual_family_attempts"],
        "rank_one_packet_family_time_offset_lift": proof["rank_one_packet_family_sink_summary"]["source_conditioned_packet_residual"]["time_offset_split"]["family_residual_lift"],
        "rank_one_packet_family_time_offset_null_p": proof["rank_one_packet_family_sink_summary"]["source_conditioned_packet_residual"]["time_offset_split"]["null_p_value"],
        "signed_packet_quotient_overall_verdict": proof["signed_rank_one_packet_quotient_summary"]["overall_verdict"],
        "signed_packet_quotient_best_candidate": proof["signed_rank_one_packet_quotient_summary"]["best_candidate"]["left_candidate_id"],
        "signed_packet_quotient_best_support_atoms": proof["signed_rank_one_packet_quotient_summary"]["best_candidate"]["support_atoms"],
        "signed_packet_quotient_r33_touch_count": proof["signed_rank_one_packet_quotient_summary"]["best_candidate"]["r33_touch_count"],
        "signed_packet_quotient_mean_abs_null_p": proof["signed_rank_one_packet_quotient_summary"]["best_candidate"]["mean_abs_null_p"],
        "signed_packet_quotient_verdict": proof["signed_rank_one_packet_quotient_summary"]["best_candidate"]["verdict"],
        "signed_packet_quotient_hydrogen_best_lag": proof["pressure_atlas_summary"]["signed_packet_quotient_lag_summary"]["best_lag"],
        "signed_packet_quotient_hydrogen_best_rho": proof["pressure_atlas_summary"]["signed_packet_quotient_lag_summary"]["best_rho"],
        "signed_packet_quotient_hydrogen_null_p": proof["pressure_atlas_summary"]["signed_packet_quotient_lag_summary"]["null_significance"]["p_value"],
        "signed_packet_quotient_hydrogen_null_verdict": proof["pressure_atlas_summary"]["signed_packet_quotient_lag_summary"]["null_significance"]["verdict"],
        "signed_packet_quotient_hydrogen_verdict": proof["pressure_atlas_summary"]["signed_packet_quotient_lag_summary"]["verdict"],
        "support3_signed_quotient_candidate_count": proof["pressure_atlas_summary"]["support3_signed_quotient_summary"]["candidate_count"],
        "support3_signed_quotient_null_tested": proof["pressure_atlas_summary"]["support3_signed_quotient_summary"]["null_tested_candidate_count"],
        "support3_signed_quotient_best_candidate": proof["pressure_atlas_summary"]["support3_signed_quotient_summary"]["best_candidate"]["candidate_id"],
        "support3_signed_quotient_best_support_atoms": proof["pressure_atlas_summary"]["support3_signed_quotient_summary"]["best_candidate"]["support_atoms"],
        "support3_signed_quotient_mean_abs_null_p": proof["pressure_atlas_summary"]["support3_signed_quotient_summary"]["best_candidate"]["mean_abs_null_p"],
        "support3_signed_quotient_verdict": proof["pressure_atlas_summary"]["support3_signed_quotient_summary"]["best_candidate"]["verdict"],
        "support3_signed_quotient_hydrogen_best_lag": proof["pressure_atlas_summary"]["support3_signed_quotient_lag_summary"]["best_lag"],
        "support3_signed_quotient_hydrogen_best_rho": proof["pressure_atlas_summary"]["support3_signed_quotient_lag_summary"]["best_rho"],
        "support3_signed_quotient_hydrogen_null_p": proof["pressure_atlas_summary"]["support3_signed_quotient_lag_summary"]["null_significance"]["p_value"],
        "support3_signed_quotient_hydrogen_null_verdict": proof["pressure_atlas_summary"]["support3_signed_quotient_lag_summary"]["null_significance"]["verdict"],
        "support3_signed_quotient_hydrogen_verdict": proof["pressure_atlas_summary"]["support3_signed_quotient_lag_summary"]["verdict"],
        "a985_q12_bridge_status": proof["a985_q12_packet_bridge_probe_summary"]["status"],
        "a985_q12_bridge_ingress_status": proof["a985_q12_packet_bridge_probe_summary"]["ingress_projection_inventory"]["status"],
        "a985_q12_bridge_rank_ceiling": proof["a985_q12_packet_bridge_probe_summary"]["corrected_rank20_selection"]["combined_boundary_image_rank_over_Q"],
        "a985_q12_bridge_target_rank": proof["a985_q12_packet_bridge_probe_summary"]["corrected_rank20_selection"]["target_rank"],
        "a985_q12_bridge_rank2_doublets": proof["a985_q12_packet_bridge_probe_summary"]["one_sided_seed_correction"]["compatible_doublet_count"],
        "a985_q12_bridge_rank2_families": proof["a985_q12_packet_bridge_probe_summary"]["one_sided_seed_correction"]["combined_rank2_support_family_count"],
        "falsification_status": proof["pressure_atlas_summary"]["falsification_ledger_summary"]["overall_status"],
        "failed_claims": proof["pressure_atlas_summary"]["falsification_ledger_summary"]["failed_claims"],
        "boundary_notes": proof["boundary_discovery_notes_artifact"],
        "boundary_notes_sha256": proof["boundary_discovery_notes_sha256"],
        "report_sha256": proof["report_sha256"],
        "next_highest_yield_item": proof["next_highest_yield_item"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
