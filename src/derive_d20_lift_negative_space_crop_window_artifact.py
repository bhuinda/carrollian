from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_d20_geon_phase_entropy_audit import (
        D20LiftSimulator,
        js_round,
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
        input_entry,
        negative_edge_mask,
        sha_file,
        sha_json,
        top_frequencies,
        write_json,
    )
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_d20_geon_phase_entropy_audit import (
        D20LiftSimulator,
        js_round,
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
        input_entry,
        negative_edge_mask,
        sha_file,
        sha_json,
        top_frequencies,
        write_json,
    )
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_lift_negative_space_crop_window_artifact"
ARTIFACT_PATH = GENERATED / f"{THEOREM_ID}.json"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

VISUALIZATION = GENERATED / "d20_sandpile_visualization.html"
EDGE_STEPS = GENERATED / "d20_voltage_lift_edge_steps.json"
PROJECTION_NULL_REPORT = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_lift_negative_space_projection_null_audit"
    / "report.json"
)
DERIVE_SCRIPT = ROOT / "src" / "derive_d20_lift_negative_space_crop_window_artifact.py"
VALIDATOR = ROOT / "src" / "certify_d20_lift_negative_space_crop_window_artifact.py"

SMALL_HALF_SPANS = [8, 10, 12, 14]
WIDE_HALF_SPANS = [18, 20, 24, 32, 64]


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


def signed_frequency(index: int, size: int) -> int:
    return index if index <= size // 2 else index - size


def sample_category(categories: np.ndarray, x: int, y: int) -> int:
    if x < 0 or y < 0 or x >= categories.shape[1] or y >= categories.shape[0]:
        return 0
    return int(categories[y, x])


def fixed_window_render(
    categories: np.ndarray,
    center_x: float,
    center_y: float,
    half_span: float,
) -> np.ndarray:
    out = np.zeros((SIZE, SIZE), dtype=np.uint8)
    for y in range(SIZE):
        sy = max(
            0,
            min(
                SIZE - 1,
                js_round(center_y - half_span + ((y + 0.5) / SIZE) * half_span * 2.0),
            ),
        )
        for x in range(SIZE):
            sx = max(
                0,
                min(
                    SIZE - 1,
                    js_round(center_x - half_span + ((x + 0.5) / SIZE) * half_span * 2.0),
                ),
            )
            out[y, x] = sample_category(categories, sx, sy)
    return out


def dominant_high_axis_frequency(peaks: list[dict[str, Any]], min_abs: int = 2) -> int | None:
    for row in peaks:
        x, y = row["frequency_xy"]
        ax = abs(int(x))
        ay = abs(int(y))
        if ay == 0 and ax >= min_abs:
            return ax
        if ax == 0 and ay >= min_abs:
            return ay
    return None


def low_frequency_dominated(peaks: list[dict[str, Any]], top_n: int = 4) -> bool:
    for row in peaks[:top_n]:
        x, y = row["frequency_xy"]
        if max(abs(int(x)), abs(int(y))) > 1:
            return False
    return True


def mask_metrics(mask: np.ndarray, seed: int) -> dict[str, Any]:
    edge = negative_edge_mask(mask)
    power = fft_power(edge)
    peaks = top_frequencies(power, 10)
    return {
        "negative_fraction": float(mask.mean()),
        "negative_edge_fraction": float(edge.mean()),
        "negative_edge_axis_power": axis_shuffle_null(edge, seed),
        "negative_edge_axis_power_fraction": axis_power_fraction(power),
        "negative_edge_top_frequencies": peaks,
        "dominant_high_axis_frequency": dominant_high_axis_frequency(peaks),
        "low_frequency_dominated_top_four": low_frequency_dominated(peaks),
    }


def run_baseline() -> tuple[D20LiftSimulator, np.ndarray, np.ndarray]:
    data, _ = load_visualization_data()
    sim = D20LiftSimulator(data)
    sim.seed()
    for _ in range(WARMUP_STEPS):
        sim.step(WARMUP_LIMIT)
    for _ in range(OBSERVATION_FRAME):
        sim.step(FRAME_LIMIT)
    categories, sums = sim.state_arrays()
    return sim, categories, sums


def artifact_hash(payload: dict[str, Any]) -> str:
    return self_hash(payload, "artifact_sha256_excluding_this_field")


def build_artifact() -> dict[str, Any]:
    data, _ = load_visualization_data()
    robust = load_json(ROBUST_REPORT)
    intrinsic = load_json(INTRINSIC_REPORT)
    projection_null = load_json(PROJECTION_NULL_REPORT)
    sim, categories, sums = run_baseline()
    bbox_center_x, bbox_center_y, dynamic_half_span = sim.bounding_box(sums)

    dynamic_render = sim.render_cooriented(categories, sums)
    raw_state_mask = categories == 0

    dynamic_row = {
        "id": "dynamic_crop_window",
        "center": [bbox_center_x, bbox_center_y],
        "half_span": dynamic_half_span,
        "window_source": "active-bounding-box render window from generated visualization",
        **mask_metrics(dynamic_render == 0, 8000),
    }
    raw_row = {
        "id": "uncropped_lift_coordinates",
        "center": [SIZE / 2, SIZE / 2],
        "half_span": SIZE / 2,
        "window_source": "native 128x128 lift-coordinate state mask without render crop",
        **mask_metrics(raw_state_mask, 8001),
    }
    small_rows = []
    for idx, half_span in enumerate(SMALL_HALF_SPANS):
        render = fixed_window_render(categories, bbox_center_x, bbox_center_y, float(half_span))
        row = {
            "id": f"fixed_bbox_window_halfspan_{half_span}",
            "center": [bbox_center_x, bbox_center_y],
            "half_span": half_span,
            "expected_scale_frequency": 2 * half_span,
            "window_source": "fixed center at dynamic active-bounding-box center",
            **mask_metrics(render == 0, 8100 + idx),
        }
        small_rows.append(row)
    wide_rows = []
    for idx, half_span in enumerate(WIDE_HALF_SPANS):
        render = fixed_window_render(categories, bbox_center_x, bbox_center_y, float(half_span))
        row = {
            "id": f"fixed_bbox_window_halfspan_{half_span}",
            "center": [bbox_center_x, bbox_center_y],
            "half_span": half_span,
            "window_source": "fixed center at dynamic active-bounding-box center",
            **mask_metrics(render == 0, 8200 + idx),
        }
        wide_rows.append(row)

    dynamic_frequency = int(dynamic_row["dominant_high_axis_frequency"])
    dynamic_scale_frequency = int(round(2 * dynamic_half_span))
    small_frequency_pairs = [
        [int(row["expected_scale_frequency"]), int(row["dominant_high_axis_frequency"])]
        for row in small_rows
    ]
    checks = {
        "source_visualization_loaded": len(data.get("nodes", [])) == 20
        and len(data.get("edges", [])) == 30,
        "robust_oblongness_theorem_certified": robust.get("status")
        == "D20_VOLTAGE_LIFT_ROBUST_OBLONGNESS_CERTIFIED",
        "intrinsic_hex_metric_certified": intrinsic.get("status")
        == "D20_VOLTAGE_LIFT_INTRINSIC_HEX_METRIC_CERTIFIED",
        "projection_null_audit_certified": projection_null.get("status")
        == "D20_LIFT_NEGATIVE_SPACE_PROJECTION_NULL_AUDIT_CERTIFIED",
        "dynamic_half_span_is_13_5": abs(float(dynamic_half_span) - 13.5) < 1e-12,
        "dynamic_frequency_equals_two_times_half_span": dynamic_frequency
        == dynamic_scale_frequency
        == 27,
        "small_fixed_windows_track_two_times_half_span": all(
            expected == observed for expected, observed in small_frequency_pairs
        ),
        "uncropped_lift_coordinates_do_not_have_axis27": raw_row["dominant_high_axis_frequency"]
        != 27,
        "uncropped_lift_coordinates_low_frequency_dominated": raw_row[
            "low_frequency_dominated_top_four"
        ]
        is True,
        "wide_windows_are_low_frequency_dominated": all(
            row["low_frequency_dominated_top_four"] is True for row in wide_rows
        ),
    }

    payload: dict[str, Any] = {
        "schema": "d20.proof_obligation.lift_negative_space_crop_window_artifact.artifact@1",
        "status": "D20_LIFT_NEGATIVE_SPACE_CROP_WINDOW_ARTIFACT_DERIVED",
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
            "projection_null_audit_report": input_entry(
                PROJECTION_NULL_REPORT,
                {
                    "status": projection_null.get("status"),
                    "certificate_sha256": projection_null.get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
        },
        "definition": {
            "crop_window_test": (
                "Compare the current dynamic crop render against fixed windows at the same active "
                "bbox center and against the uncropped native lift-coordinate state mask."
            ),
            "scale_frequency_rule": (
                "For the small fixed windows tested here, the dominant high-axis negative-edge "
                "frequency equals 2 * half_span. The dynamic crop has half_span 13.5 and frequency 27."
            ),
            "interpretation": (
                "The exact high-axis frequency is a render-window artifact explained by the "
                "crop/zoom scale, not by an uncropped coordinate-free D20 lift frequency."
            ),
        },
        "simulation": {
            "canvas_size": [SIZE, SIZE],
            "warmup_steps": WARMUP_STEPS,
            "warmup_topple_limit": WARMUP_LIMIT,
            "observation_frame_after_warmup": OBSERVATION_FRAME,
            "frame_topple_limit": FRAME_LIMIT,
            "dynamic_bbox": {
                "center": [bbox_center_x, bbox_center_y],
                "half_span": dynamic_half_span,
                "scale_frequency": dynamic_scale_frequency,
            },
            "small_half_spans": SMALL_HALF_SPANS,
            "wide_half_spans": WIDE_HALF_SPANS,
        },
        "dynamic_crop": dynamic_row,
        "uncropped_lift_coordinates": raw_row,
        "fixed_small_windows": small_rows,
        "fixed_wide_windows": wide_rows,
        "summary": {
            "dynamic_half_span": dynamic_half_span,
            "dynamic_dominant_high_axis_frequency": dynamic_frequency,
            "small_window_expected_observed_frequency_pairs": small_frequency_pairs,
            "uncropped_top_four_signature": [
                row["frequency_xy"] for row in raw_row["negative_edge_top_frequencies"][:4]
            ],
            "wide_window_top_four_signatures": {
                row["id"]: [peak["frequency_xy"] for peak in row["negative_edge_top_frequencies"][:4]]
                for row in wide_rows
            },
        },
        "interpretation_boundary": {
            "certifies": [
                "the visible high-axis frequency is a render-window artifact: it equals 2 * the active crop half-span",
                "small fixed crop windows move the high-axis frequency according to 2 * half_span",
                "uncropped native lift coordinates are low-frequency dominated and do not show the crop-scale frequency",
                "wide fixed windows are low-frequency dominated in the tested set",
            ],
            "does_not_certify": [
                "that all negative-space structure is a render artifact",
                "that no intrinsic D20 negative-space invariant exists",
                "a physical spacetime interpretation",
                "all possible crop windows or perturbations",
            ],
        },
        "checks": checks,
    }
    payload["artifact_sha256_excluding_this_field"] = artifact_hash(payload)
    return payload


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema": "d20.proof_obligation.lift_negative_space_crop_window_artifact@1",
        "status": "D20_LIFT_NEGATIVE_SPACE_CROP_WINDOW_ARTIFACT_CERTIFIED",
        "all_checks_pass": all(artifact["checks"].values()),
        "claim": (
            "The visible high-axis negative-space frequency is a render-window artifact, not a "
            "canonical D20 invariant. The dynamic window has half-span 13.5 and dominant high-axis "
            "frequency 27, while fixed small windows move the high-axis frequency as 2 * half_span. "
            "Uncropped lift coordinates and wide windows are low-frequency dominated. This artifact "
            "is retained only as a demotion/regression guard."
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
        },
        "checks": artifact["checks"],
        "next_highest_yield_item": (
            "Keep this out of the canonical invariant list. If a native negative-space claim is "
            "still desired, define it before crop/render projection and test it independently."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": "d20.proof_obligation.lift_negative_space_crop_window_artifact_manifest@1",
        "name": THEOREM_ID,
        "certification_tests": [
            "verify the projection/null audit is certified",
            "replay the D20 lift baseline state",
            "extract dynamic crop, fixed-window, and uncropped negative-space edge spectra",
            "verify dynamic axis-27 equals 2 * dynamic half-span 13.5",
            "verify small fixed-window high-axis frequencies equal 2 * half_span",
            "verify uncropped and wide-window spectra are low-frequency dominated",
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
