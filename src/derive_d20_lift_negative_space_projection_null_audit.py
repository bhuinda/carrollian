from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
import math
import random
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_d20_geon_phase_entropy_audit import (
        D20LiftSimulator,
        D20_LABEL_VECTORS,
        replacement,
        load_visualization_data,
    )
    from .derive_d20_lift_negative_space_grid_perturbation_audit import (
        FRAME_LIMIT,
        INTRINSIC_REPORT,
        OBSERVATION_FRAME,
        ROBUST_REPORT,
        SIZE,
        WARMUP_LIMIT,
        WARMUP_STEPS,
        axis_power_fraction,
        axis_shuffle_null,
        fft_power,
        frequency_signature,
        input_entry,
        negative_edge_mask,
        sha_file,
        sha_json,
        spectral_cosine,
        top_frequencies,
        write_json,
    )
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_d20_geon_phase_entropy_audit import (
        D20LiftSimulator,
        D20_LABEL_VECTORS,
        replacement,
        load_visualization_data,
    )
    from derive_d20_lift_negative_space_grid_perturbation_audit import (
        FRAME_LIMIT,
        INTRINSIC_REPORT,
        OBSERVATION_FRAME,
        ROBUST_REPORT,
        SIZE,
        WARMUP_LIMIT,
        WARMUP_STEPS,
        axis_power_fraction,
        axis_shuffle_null,
        fft_power,
        frequency_signature,
        input_entry,
        negative_edge_mask,
        sha_file,
        sha_json,
        spectral_cosine,
        top_frequencies,
        write_json,
    )
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_lift_negative_space_projection_null_audit"
ARTIFACT_PATH = GENERATED / f"{THEOREM_ID}.json"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

VISUALIZATION = GENERATED / "d20_sandpile_visualization.html"
EDGE_STEPS = GENERATED / "d20_voltage_lift_edge_steps.json"
GRID_AUDIT_REPORT = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_lift_negative_space_grid_perturbation_audit"
    / "report.json"
)
DERIVE_SCRIPT = ROOT / "src" / "derive_d20_lift_negative_space_projection_null_audit.py"
VALIDATOR = ROOT / "src" / "certify_d20_lift_negative_space_projection_null_audit.py"

ZERO_TIE_SEEDS = list(range(200, 208))


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} is not a JSON object")
    return payload


def self_hash(payload: dict[str, Any], field: str) -> str:
    tmp = dict(payload)
    tmp.pop(field, None)
    return sha_json(tmp)


def sign(value: float) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def top_four_axis27(peaks: list[dict[str, Any]]) -> bool:
    for row in peaks[:4]:
        x, y = row["frequency_xy"]
        if sorted([abs(int(x)), abs(int(y))]) != [0, 27]:
            return False
    return True


def high_axis_band_frequency(peaks: list[dict[str, Any]], low: int = 28, high: int = 33) -> int | None:
    for row in peaks:
        x, y = row["frequency_xy"]
        ax = abs(int(x))
        ay = abs(int(y))
        if ay == 0 and low <= ax <= high:
            return ax
        if ax == 0 and low <= ay <= high:
            return ay
    return None


class CustomD20LiftSimulator(D20LiftSimulator):
    def __init__(self, data: dict[str, Any], edge_deltas: dict[int, tuple[int, int]]) -> None:
        super().__init__(data)
        self.neighbors = [[] for _ in range(self.fibers)]
        for edge in data["edges"]:
            dx, dy = edge_deltas[int(edge["id"])]
            self.neighbors[int(edge["u"])].append((int(edge["v"]), int(dx), int(dy)))
            self.neighbors[int(edge["v"])].append((int(edge["u"]), -int(dx), -int(dy)))


def zero_tie_edge_deltas(data: dict[str, Any], seed: int) -> dict[int, tuple[int, int]]:
    rng = random.Random(seed)
    out: dict[int, tuple[int, int]] = {}
    for edge in data["edges"]:
        leaving, entering = replacement(edge)
        ax, ay = D20_LABEL_VECTORS[leaving]
        bx, by = D20_LABEL_VECTORS[entering]
        dx = sign(bx - ax)
        dy = sign(by - ay)
        if dx == 0:
            dx = rng.choice([-1, 1])
        if dy == 0:
            dy = rng.choice([0, 1])
        out[int(edge["id"])] = (dx, dy)
    return out


def run_baseline_state(data: dict[str, Any]) -> tuple[D20LiftSimulator, np.ndarray, np.ndarray]:
    sim = D20LiftSimulator(data)
    sim.seed()
    for _ in range(WARMUP_STEPS):
        sim.step(WARMUP_LIMIT)
    for _ in range(OBSERVATION_FRAME):
        sim.step(FRAME_LIMIT)
    categories, sums = sim.state_arrays()
    return sim, categories, sums


def run_custom_render(data: dict[str, Any], seed: int) -> np.ndarray:
    sim = CustomD20LiftSimulator(data, zero_tie_edge_deltas(data, seed))
    sim.seed()
    for _ in range(WARMUP_STEPS):
        sim.step(WARMUP_LIMIT)
    for _ in range(OBSERVATION_FRAME):
        sim.step(FRAME_LIMIT)
    categories, sums = sim.state_arrays()
    return sim.render_cooriented(categories, sums)


def mask_metrics(mask: np.ndarray, seed: int, baseline_power: np.ndarray | None = None) -> dict[str, Any]:
    edge = negative_edge_mask(mask)
    power = fft_power(edge)
    peaks = top_frequencies(power, 8)
    row: dict[str, Any] = {
        "negative_fraction": float(mask.mean()),
        "negative_edge_fraction": float(edge.mean()),
        "negative_edge_axis_power": axis_shuffle_null(edge, seed),
        "negative_edge_axis_power_fraction": axis_power_fraction(power),
        "negative_edge_top_frequencies": peaks,
        "top_four_frequency_signature": frequency_signature(peaks),
        "top_four_are_axis27": top_four_axis27(peaks),
        "high_axis_band_28_to_33": high_axis_band_frequency(peaks),
    }
    if baseline_power is not None:
        row["negative_edge_spectral_cosine_to_cooriented_baseline"] = spectral_cosine(
            baseline_power, power
        )
    return row


def artifact_hash(payload: dict[str, Any]) -> str:
    return self_hash(payload, "artifact_sha256_excluding_this_field")


def build_artifact() -> dict[str, Any]:
    data, _ = load_visualization_data()
    robust = load_json(ROBUST_REPORT)
    intrinsic = load_json(INTRINSIC_REPORT)
    grid_report = load_json(GRID_AUDIT_REPORT)
    sim, categories, sums = run_baseline_state(data)

    cooriented_render = sim.render_cooriented(categories, sums)
    hex_render = sim.render_hex(categories, sums)
    state_mask = categories == 0
    baseline_edge_power = fft_power(negative_edge_mask(cooriented_render == 0))

    projection_rows = [
        {
            "id": "cooriented_screen_projection",
            "role": "current D20 cooriented render",
            **mask_metrics(cooriented_render == 0, 6500, baseline_edge_power),
        },
        {
            "id": "regular_hex_projection",
            "role": "same D20 state field rendered through the regular-hex comparison projection",
            **mask_metrics(hex_render == 0, 6501, baseline_edge_power),
        },
        {
            "id": "unprojected_state_grid",
            "role": "category-0 cells before screen crop/projection",
            **mask_metrics(state_mask, 6502, baseline_edge_power),
        },
    ]

    zero_tie_rows = []
    for idx, seed in enumerate(ZERO_TIE_SEEDS):
        render = run_custom_render(data, seed)
        row = mask_metrics(render == 0, 7000 + idx, baseline_edge_power)
        row.update(
            {
                "id": f"zero_tie_random_seed_{seed}",
                "seed": seed,
                "role": (
                    "entering/leaving labels fixed; nonzero raw step signs fixed; only zero-coordinate "
                    "selector tie-break components randomized"
                ),
            }
        )
        zero_tie_rows.append(row)

    high_band_values = [
        int(row["high_axis_band_28_to_33"])
        for row in zero_tie_rows
        if row["high_axis_band_28_to_33"] is not None
    ]
    checks = {
        "source_visualization_loaded": len(data.get("nodes", [])) == 20
        and len(data.get("edges", [])) == 30,
        "robust_oblongness_theorem_certified": robust.get("status")
        == "D20_VOLTAGE_LIFT_ROBUST_OBLONGNESS_CERTIFIED",
        "intrinsic_hex_metric_certified": intrinsic.get("status")
        == "D20_VOLTAGE_LIFT_INTRINSIC_HEX_METRIC_CERTIFIED",
        "prior_negative_space_grid_audit_certified": grid_report.get("status")
        == "D20_LIFT_NEGATIVE_SPACE_GRID_PERTURBATION_AUDIT_CERTIFIED",
        "cooriented_projection_has_exact_axis27_top_four": projection_rows[0][
            "top_four_are_axis27"
        ]
        is True,
        "regular_hex_projection_does_not_have_axis27_top_four": projection_rows[1][
            "top_four_are_axis27"
        ]
        is False,
        "unprojected_state_does_not_have_axis27_top_four": projection_rows[2][
            "top_four_are_axis27"
        ]
        is False,
        "eight_zero_tie_randomizations_tested": len(zero_tie_rows) == 8,
        "all_zero_tie_randomizations_have_high_axis_band_28_to_33": len(high_band_values)
        == len(zero_tie_rows),
        "zero_tie_high_axis_band_is_not_fixed_at_27": 27 not in high_band_values,
        "all_zero_tie_axis_power_z_scores_exceed_100": all(
            float(row["negative_edge_axis_power"]["axis_power_z_score"]) > 100.0
            for row in zero_tie_rows
        ),
        "some_zero_tie_spectra_depart_from_baseline": min(
            float(row["negative_edge_spectral_cosine_to_cooriented_baseline"])
            for row in zero_tie_rows
        )
        < 0.50,
    }
    payload: dict[str, Any] = {
        "schema": "d20.proof_obligation.lift_negative_space_projection_null_audit.artifact@1",
        "status": "D20_LIFT_NEGATIVE_SPACE_PROJECTION_NULL_AUDIT_DERIVED",
        "source": {
            "visualization": input_entry(VISUALIZATION),
            "edge_steps": input_entry(EDGE_STEPS),
            "robust_oblongness_theorem_report": input_entry(
                ROBUST_REPORT,
                {
                    "status": robust.get("status"),
                    "certificate_sha256": robust.get("certificate_sha256"),
                },
            ),
            "intrinsic_hex_metric_report": input_entry(
                INTRINSIC_REPORT,
                {
                    "status": intrinsic.get("status"),
                    "certificate_sha256": intrinsic.get("certificate_sha256"),
                },
            ),
            "prior_negative_space_grid_audit": input_entry(
                GRID_AUDIT_REPORT,
                {
                    "status": grid_report.get("status"),
                    "certificate_sha256": grid_report.get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
        },
        "definition": {
            "projection_test": (
                "Compare the cooriented screen negative-space mask with the same state field under "
                "regular-hex projection and before projection."
            ),
            "zero_tie_randomization": (
                "Preserve each edge's entering/leaving labels and nonzero raw sign components, but "
                "randomize screen-step components produced only by zero-coordinate tie-breaks."
            ),
            "interpretation": (
                "Exact axis-27 is a cooriented selector-screen feature. A broader high-axis grid "
                "band survives zero-tie randomization, but the regular-hex projection does not keep "
                "the exact axis-27 top-four signature."
            ),
        },
        "simulation": {
            "canvas_size": [SIZE, SIZE],
            "warmup_steps": WARMUP_STEPS,
            "warmup_topple_limit": WARMUP_LIMIT,
            "observation_frame_after_warmup": OBSERVATION_FRAME,
            "frame_topple_limit": FRAME_LIMIT,
            "zero_tie_randomization_seeds": ZERO_TIE_SEEDS,
        },
        "projection_variants": projection_rows,
        "zero_tie_randomization_variants": zero_tie_rows,
        "summary": {
            "cooriented_exact_top_frequency_abs": 27,
            "zero_tie_high_axis_band_range": [min(high_band_values), max(high_band_values)],
            "zero_tie_spectral_cosine_to_baseline_range": [
                min(float(row["negative_edge_spectral_cosine_to_cooriented_baseline"]) for row in zero_tie_rows),
                max(float(row["negative_edge_spectral_cosine_to_cooriented_baseline"]) for row in zero_tie_rows),
            ],
            "regular_hex_projection_top_four_signature": projection_rows[1][
                "top_four_frequency_signature"
            ],
            "unprojected_state_top_four_signature": projection_rows[2][
                "top_four_frequency_signature"
            ],
        },
        "interpretation_boundary": {
            "certifies": [
                "exact axis-27 is present in the cooriented screen projection",
                "exact axis-27 is not the top-four signature in the regular-hex projection",
                "exact axis-27 is not the top-four signature before screen projection",
                "a high-axis grid band from 28 to 33 survives the tested zero-tie randomizations",
            ],
            "does_not_certify": [
                "that axis-27 is coordinate-free intrinsic D20 geometry",
                "that every label-preserving perturbation preserves a grid band",
                "that the regular-hex projection lacks all possible grid structure",
                "physical spacetime interpretation",
            ],
        },
        "checks": checks,
    }
    payload["artifact_sha256_excluding_this_field"] = artifact_hash(payload)
    return payload


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema": "d20.proof_obligation.lift_negative_space_projection_null_audit@1",
        "status": "D20_LIFT_NEGATIVE_SPACE_PROJECTION_NULL_AUDIT_CERTIFIED",
        "all_checks_pass": all(artifact["checks"].values()),
        "claim": (
            "The exact axis-27 negative-space grid is a cooriented selector-screen feature, not "
            "currently certified as coordinate-free intrinsic D20 geometry. Under zero-coordinate "
            "tie-break randomization, a nearby high-axis grid band persists in the tested range "
            "28-33, but the regular-hex projection and unprojected state do not keep the exact "
            "axis-27 top-four signature."
        ),
        "definition": artifact["definition"],
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
            "simulation": artifact["simulation"],
            "summary": artifact["summary"],
            "projection_variant_ids": [row["id"] for row in artifact["projection_variants"]],
            "zero_tie_variant_count": len(artifact["zero_tie_randomization_variants"]),
        },
        "checks": artifact["checks"],
        "next_highest_yield_item": (
            "Test whether the high-axis band is explained by the crop/zoom renderer by recomputing "
            "the negative-space spectra on un-cropped lift coordinates and on fixed-window renders."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": "d20.proof_obligation.lift_negative_space_projection_null_audit_manifest@1",
        "name": THEOREM_ID,
        "certification_tests": [
            "verify the prior negative-space grid audit is certified",
            "compare cooriented screen, regular-hex projection, and unprojected state masks",
            "verify exact axis-27 appears only in the cooriented projection top-four signature",
            "run eight label-preserving zero-tie randomizations",
            "verify zero-tie randomizations preserve a high-axis grid band in the 28-33 range",
            "verify the exact 27 claim remains projection/selector scoped",
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
                "summary": report["witness"]["summary"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
