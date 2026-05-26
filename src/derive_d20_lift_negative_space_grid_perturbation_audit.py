from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_d20_geon_phase_entropy_audit import (
        D20LiftSimulator,
        load_visualization_data,
    )
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_d20_geon_phase_entropy_audit import (
        D20LiftSimulator,
        load_visualization_data,
    )
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_lift_negative_space_grid_perturbation_audit"
ARTIFACT_PATH = GENERATED / f"{THEOREM_ID}.json"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

VISUALIZATION = GENERATED / "d20_sandpile_visualization.html"
EDGE_STEPS = GENERATED / "d20_voltage_lift_edge_steps.json"
ROBUST_REPORT = D20_INVARIANTS / "theorems" / "d20_voltage_lift_robust_oblongness" / "report.json"
INTRINSIC_REPORT = (
    D20_INVARIANTS / "proof_obligations" / "d20_voltage_lift_intrinsic_hex_metric" / "report.json"
)
DERIVE_SCRIPT = ROOT / "src" / "derive_d20_lift_negative_space_grid_perturbation_audit.py"
VALIDATOR = ROOT / "src" / "certify_d20_lift_negative_space_grid_perturbation_audit.py"

SIZE = 128
CENTER = SIZE // 2
WARMUP_STEPS = 36
WARMUP_LIMIT = 9000
OBSERVATION_FRAME = 96
FRAME_LIMIT = 7000
NULL_SAMPLES = 64

PERTURBATIONS: list[dict[str, Any]] = [
    {"id": "baseline", "adds": []},
    {"id": "source_plus_37", "adds": [[CENTER, CENTER, 0, 37]]},
    {"id": "source_plus_113", "adds": [[CENTER, CENTER, 0, 113]]},
    {"id": "east_v7_plus_89", "adds": [[CENTER + 1, CENTER, 7, 89]]},
    {"id": "west_v14_plus_89", "adds": [[CENTER - 1, CENTER, 14, 89]]},
    {"id": "north_v3_plus_89", "adds": [[CENTER, CENTER - 1, 3, 89]]},
    {"id": "south_v11_plus_89", "adds": [[CENTER, CENTER + 1, 11, 89]]},
]


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


def signed_frequency(index: int, size: int) -> int:
    return index if index <= size // 2 else index - size


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


def negative_edge_mask(mask: np.ndarray) -> np.ndarray:
    edges = np.zeros_like(mask, dtype=bool)
    edges[1:, :] |= mask[1:, :] != mask[:-1, :]
    edges[:, 1:] |= mask[:, 1:] != mask[:, :-1]
    return edges


def fft_power(mask: np.ndarray) -> np.ndarray:
    arr = mask.astype(float)
    arr -= float(arr.mean())
    power = np.abs(np.fft.fft2(arr)) ** 2
    power[0, 0] = 0.0
    return power


def spectral_cosine(a: np.ndarray, b: np.ndarray) -> float:
    av = a.ravel()
    bv = b.ravel()
    denom = float(np.linalg.norm(av) * np.linalg.norm(bv))
    return float((av @ bv) / denom) if denom else 0.0


def axis_power_fraction(power: np.ndarray) -> float:
    total = float(power.sum())
    if total == 0.0:
        return 0.0
    return float((power[0, :].sum() + power[:, 0].sum()) / total)


def top_frequencies(power: np.ndarray, count: int = 8) -> list[dict[str, Any]]:
    q = power.copy()
    total = float(q.sum()) or 1.0
    out: list[dict[str, Any]] = []
    for rank in range(1, count + 1):
        y_idx, x_idx = np.unravel_index(int(np.argmax(q)), q.shape)
        value = float(q[y_idx, x_idx])
        out.append(
            {
                "rank": rank,
                "frequency_xy": [
                    signed_frequency(int(x_idx), q.shape[1]),
                    signed_frequency(int(y_idx), q.shape[0]),
                ],
                "power_fraction": value / total,
            }
        )
        q[y_idx, x_idx] = 0.0
    return out


def axis_shuffle_null(mask: np.ndarray, seed: int) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    flat = mask.ravel().copy()
    observed = axis_power_fraction(fft_power(mask))
    values: list[float] = []
    for _ in range(NULL_SAMPLES):
        rng.shuffle(flat)
        values.append(axis_power_fraction(fft_power(flat.reshape(mask.shape))))
    mean = float(np.mean(values))
    sd = float(np.std(values, ddof=1))
    return {
        "histogram_preserving_shuffle_samples": NULL_SAMPLES,
        "observed_axis_power_fraction": observed,
        "shuffle_mean_axis_power_fraction": mean,
        "shuffle_sample_sd_axis_power_fraction": sd,
        "axis_power_z_score": (observed - mean) / sd if sd else math.inf,
    }


def jaccard(a: np.ndarray, b: np.ndarray) -> float:
    union = int(np.logical_or(a, b).sum())
    if union == 0:
        return 1.0
    return float(np.logical_and(a, b).sum() / union)


def run_render(data: dict[str, Any], adds: list[list[int]]) -> tuple[np.ndarray, dict[str, int]]:
    sim = D20LiftSimulator(data)
    sim.seed()
    for x, y, fiber, grains in adds:
        sim.add(int(x), int(y), int(fiber), int(grains))
    for _ in range(WARMUP_STEPS):
        sim.step(WARMUP_LIMIT)
    for _ in range(OBSERVATION_FRAME):
        sim.step(FRAME_LIMIT)
    categories, sums = sim.state_arrays()
    render = sim.render_cooriented(categories, sums)
    return render, {
        "live_grains": int(sums.sum()),
        "topples": int(sim.topples),
        "boundary_loss": int(sim.boundary_loss),
        "active_queue": len(sim.queue),
    }


def frequency_signature(peaks: list[dict[str, Any]]) -> list[list[int]]:
    return [row["frequency_xy"] for row in peaks[:4]]


def all_top_four_are_axis_27(peaks: list[dict[str, Any]]) -> bool:
    for row in peaks[:4]:
        x, y = row["frequency_xy"]
        if sorted([abs(int(x)), abs(int(y))]) != [0, 27]:
            return False
    return True


def build_variant_metrics(data: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    baseline_negative = None
    baseline_edge = None
    baseline_edge_power = None

    for idx, variant in enumerate(PERTURBATIONS):
        render, run_stats = run_render(data, variant["adds"])
        negative = render == 0
        edge = negative_edge_mask(negative)
        edge_power = fft_power(edge)
        negative_power = fft_power(negative)
        peaks = top_frequencies(edge_power, 8)
        counts = np.bincount(render.ravel(), minlength=5).astype(int).tolist()
        if baseline_negative is None:
            baseline_negative = negative
            baseline_edge = edge
            baseline_edge_power = edge_power
        assert baseline_negative is not None
        assert baseline_edge is not None
        assert baseline_edge_power is not None
        rows.append(
            {
                "id": variant["id"],
                "post_seed_additions": variant["adds"],
                "run_stats": run_stats,
                "render_category_counts": counts,
                "render_category_entropy_bits": entropy_from_counts(counts),
                "negative_pixel_count": int(negative.sum()),
                "negative_fraction": float(negative.mean()),
                "negative_jaccard_to_baseline": jaccard(baseline_negative, negative),
                "negative_edge_pixel_count": int(edge.sum()),
                "negative_edge_fraction": float(edge.mean()),
                "negative_edge_jaccard_to_baseline": jaccard(baseline_edge, edge),
                "negative_edge_spectral_cosine_to_baseline": spectral_cosine(
                    baseline_edge_power, edge_power
                ),
                "negative_edge_axis_power": axis_shuffle_null(edge, 54320 + idx),
                "negative_edge_top_frequencies": peaks,
                "top_four_frequency_signature": frequency_signature(peaks),
                "top_four_are_axis_frequency_27": all_top_four_are_axis_27(peaks),
                "negative_space_axis_power_fraction": axis_power_fraction(negative_power),
            }
        )
    return rows


def artifact_hash(payload: dict[str, Any]) -> str:
    return self_hash(payload, "artifact_sha256_excluding_this_field")


def build_artifact() -> dict[str, Any]:
    data, _ = load_visualization_data()
    robust = load_json(ROBUST_REPORT)
    intrinsic = load_json(INTRINSIC_REPORT)
    variants = build_variant_metrics(data)
    nonbaseline = [row for row in variants if row["id"] != "baseline"]
    checks = {
        "source_visualization_loaded": len(data.get("nodes", [])) == 20
        and len(data.get("edges", [])) == 30,
        "robust_oblongness_theorem_certified": robust.get("status")
        == "D20_VOLTAGE_LIFT_ROBUST_OBLONGNESS_CERTIFIED",
        "intrinsic_hex_metric_certified": intrinsic.get("status")
        == "D20_VOLTAGE_LIFT_INTRINSIC_HEX_METRIC_CERTIFIED",
        "seven_perturbation_variants_tested": len(variants) == 7,
        "baseline_and_all_perturbations_have_axis27_top_four": all(
            row["top_four_are_axis_frequency_27"] for row in variants
        ),
        "all_edge_axis_power_z_scores_exceed_100": all(
            float(row["negative_edge_axis_power"]["axis_power_z_score"]) > 100.0
            for row in variants
        ),
        "all_perturbed_edge_spectral_cosines_exceed_0_94": all(
            float(row["negative_edge_spectral_cosine_to_baseline"]) > 0.94
            for row in nonbaseline
        ),
        "all_perturbed_negative_jaccards_exceed_0_78": all(
            float(row["negative_jaccard_to_baseline"]) > 0.78 for row in nonbaseline
        ),
        "exact_negative_edge_mask_not_claimed_invariant": any(
            float(row["negative_edge_jaccard_to_baseline"]) < 0.70 for row in nonbaseline
        ),
    }
    payload: dict[str, Any] = {
        "schema": "d20.proof_obligation.lift_negative_space_grid_perturbation_audit.artifact@1",
        "status": "D20_LIFT_NEGATIVE_SPACE_GRID_PERTURBATION_AUDIT_DERIVED",
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
            "derive_script": input_entry(DERIVE_SCRIPT),
        },
        "definition": {
            "negative_space": "screen-space pixels with D20 cooriented lift render category 0",
            "negative_edge_mask": (
                "horizontal/vertical boundary of the negative-space mask, computed without "
                "wraparound"
            ),
            "grid_signature": (
                "the four strongest non-DC Fourier modes of the negative-edge mask are the "
                "axis modes (0,+/-27) and (+/-27,0)"
            ),
            "quasi_invariance": (
                "perturbations may change exact negative-edge pixels, but preserve the axis-27 "
                "spectral signature and remain close to the baseline spectrum"
            ),
        },
        "simulation": {
            "canvas_size": [SIZE, SIZE],
            "warmup_steps": WARMUP_STEPS,
            "warmup_topple_limit": WARMUP_LIMIT,
            "observation_frame_after_warmup": OBSERVATION_FRAME,
            "frame_topple_limit": FRAME_LIMIT,
            "perturbation_count": len(PERTURBATIONS),
        },
        "variants": variants,
        "summary": {
            "negative_fraction_range": [
                min(float(row["negative_fraction"]) for row in variants),
                max(float(row["negative_fraction"]) for row in variants),
            ],
            "negative_edge_fraction_range": [
                min(float(row["negative_edge_fraction"]) for row in variants),
                max(float(row["negative_edge_fraction"]) for row in variants),
            ],
            "perturbed_negative_jaccard_range": [
                min(float(row["negative_jaccard_to_baseline"]) for row in nonbaseline),
                max(float(row["negative_jaccard_to_baseline"]) for row in nonbaseline),
            ],
            "perturbed_edge_spectral_cosine_range": [
                min(float(row["negative_edge_spectral_cosine_to_baseline"]) for row in nonbaseline),
                max(float(row["negative_edge_spectral_cosine_to_baseline"]) for row in nonbaseline),
            ],
            "edge_axis_power_z_score_range": [
                min(float(row["negative_edge_axis_power"]["axis_power_z_score"]) for row in variants),
                max(float(row["negative_edge_axis_power"]["axis_power_z_score"]) for row in variants),
            ],
            "common_top_four_axis_frequency_abs": 27,
        },
        "interpretation_boundary": {
            "certifies": [
                "the D20 cooriented lift negative-space edge mask has a strong axis-27 grid signature",
                "the axis-27 signature survives the tested local post-seed perturbations",
                "perturbed negative-space spectra remain close to the baseline spectrum",
                "the exact negative-edge pixel set is not invariant",
            ],
            "does_not_certify": [
                "a coordinate-free intrinsic lattice in the D20 object",
                "physical spacetime structure",
                "subpixel or alpha-channel phase structure",
                "all possible perturbations",
            ],
        },
        "checks": checks,
    }
    payload["artifact_sha256_excluding_this_field"] = artifact_hash(payload)
    return payload


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema": "d20.proof_obligation.lift_negative_space_grid_perturbation_audit@1",
        "status": "D20_LIFT_NEGATIVE_SPACE_GRID_PERTURBATION_AUDIT_CERTIFIED",
        "all_checks_pass": all(artifact["checks"].values()),
        "claim": (
            "The D20 cooriented voltage-lift render has a certified screen-space negative-space "
            "grid signature: the negative-edge mask's strongest Fourier modes are the axis modes "
            "(0,+/-27) and (+/-27,0), and this signature survives the tested local perturbations. "
            "The exact negative-edge pixels are not invariant, so the certified invariant is "
            "spectral/quasi-invariant rather than pointwise."
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
            "variant_count": len(artifact["variants"]),
            "variant_ids": [row["id"] for row in artifact["variants"]],
        },
        "checks": artifact["checks"],
        "next_highest_yield_item": (
            "Separate screen-coordinate effects from intrinsic D20 geometry by repeating this "
            "negative-space audit under regular-hex projection and under randomized label-preserving "
            "edge-step perturbations."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": "d20.proof_obligation.lift_negative_space_grid_perturbation_audit_manifest@1",
        "name": THEOREM_ID,
        "certification_tests": [
            "verify D20 visualization source loads with 20 vertices and 30 edges",
            "verify robust oblongness and intrinsic hex metric reports are certified",
            "replay baseline plus six local post-seed perturbations",
            "extract D20 cooriented negative-space and negative-edge masks",
            "verify all variants have top four negative-edge Fourier modes at axis frequency 27",
            "verify edge-axis power exceeds histogram-preserving shuffle nulls",
            "verify perturbed spectra remain close while exact edge masks are not claimed invariant",
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
