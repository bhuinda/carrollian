from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_micro_black_hole_raw_transport_probe"
ARTIFACT_PATH = GENERATED / f"{THEOREM_ID}.json"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

MICRO_THEOREM_ID = "d20_micro_black_hole_backreaction_probe"
MICRO_ARTIFACT = GENERATED / f"{MICRO_THEOREM_ID}.json"
MICRO_REPORT = D20_INVARIANTS / "proof_obligations" / MICRO_THEOREM_ID / "report.json"
DERIVE_SCRIPT = ROOT / "src" / "derive_d20_micro_black_hole_raw_transport_probe.py"
VALIDATOR = ROOT / "src" / "certify_d20_micro_black_hole_raw_transport_probe.py"


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


def artifact_hash(payload: dict[str, Any]) -> str:
    return self_hash(payload, "artifact_sha256_excluding_this_field")


def close_enough(left: float, right: float) -> bool:
    return math.isclose(float(left), float(right), rel_tol=0.0, abs_tol=1e-12)


def frame_delta_rows(micro: dict[str, Any]) -> list[dict[str, Any]]:
    baseline = micro["witness"]["baseline"]["astar_rows"]
    backreaction = micro["witness"]["backreaction"]["astar_rows"]
    rows = []
    for base, back in zip(baseline, backreaction):
        frame = int(back["frame"])
        raw_back = float(back["raw_inner_band_fraction_mean"])
        raw_base = float(base["raw_inner_band_fraction_mean"])
        lensed_back = float(back["inner_band_fraction_mean"])
        lensed_base = float(base["inner_band_fraction_mean"])
        rows.append(
            {
                "frame": frame,
                "raw_backreaction_inner_band_fraction": raw_back,
                "raw_baseline_inner_band_fraction": raw_base,
                "raw_delta": raw_back - raw_base,
                "lensed_backreaction_inner_band_fraction": lensed_back,
                "lensed_baseline_inner_band_fraction": lensed_base,
                "lensed_delta": lensed_back - lensed_base,
                "lens_factor": float(back["horizon_lens_factor"]),
                "horizon_mass": int(back["horizon_mass"]),
            }
        )
    return rows


def build_artifact() -> dict[str, Any]:
    micro = load_json(MICRO_ARTIFACT)
    micro_report = load_json(MICRO_REPORT)
    summary = micro["witness"]["summary"]
    rows = frame_delta_rows(micro)
    raw_mean = float(np.mean([row["raw_delta"] for row in rows]))
    lensed_mean = float(np.mean([row["lensed_delta"] for row in rows]))
    raw_positive_count = int(sum(1 for row in rows if float(row["raw_delta"]) > 0.0))
    lensed_positive_count = int(sum(1 for row in rows if float(row["lensed_delta"]) > 0.0))
    checks = {
        "micro_backreaction_probe_is_certified": micro.get("status")
        == "D20_MICRO_BLACK_HOLE_BACKREACTION_PROBE_CERTIFIED"
        and micro_report.get("status") == micro.get("status"),
        "raw_astar_shadow_fields_are_present": all(
            "raw_inner_band_fraction_mean" in row
            and "inner_band_fraction_mean" in row
            and "horizon_lens_factor" in row
            for row in micro["witness"]["backreaction"]["astar_rows"]
        ),
        "raw_transport_delta_matches_source_summary": close_enough(
            raw_mean, summary["raw_astar_inner_band_delta_vs_baseline_mean"]
        ),
        "lensed_transport_delta_matches_source_summary": close_enough(
            lensed_mean, summary["astar_inner_band_delta_vs_baseline_mean"]
        ),
        "lensed_reference_bends_toward_horizon": lensed_mean > 0.0,
        "raw_and_lensed_measurements_are_distinct": abs(lensed_mean - raw_mean) > 0.03,
        "raw_transport_bends_toward_horizon_without_lens": raw_mean > 0.0,
    }
    status = (
        "D20_MICRO_BLACK_HOLE_RAW_TRANSPORT_PROBE_CERTIFIED_RAW_POSITIVE"
        if checks["micro_backreaction_probe_is_certified"]
        and checks["raw_transport_bends_toward_horizon_without_lens"]
        else "D20_MICRO_BLACK_HOLE_RAW_TRANSPORT_PROBE_NEGATIVE"
    )
    payload: dict[str, Any] = {
        "schema": "d20.proof_obligation.micro_black_hole_raw_transport_probe.artifact@1",
        "status": status,
        "source": {
            "micro_black_hole_backreaction_artifact": input_entry(
                MICRO_ARTIFACT,
                {
                    "status": micro.get("status"),
                    "artifact_sha256_excluding_this_field": micro.get(
                        "artifact_sha256_excluding_this_field"
                    ),
                },
            ),
            "micro_black_hole_backreaction_report": input_entry(
                MICRO_REPORT,
                {
                    "status": micro_report.get("status"),
                    "certificate_sha256": micro_report.get("certificate_sha256"),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
        },
        "definition": {
            "object": "no-lens raw A* transport test for the D20 micro-horizon analog",
            "no_lens_constraint": (
                "uses the raw_astar_* shadow measurements recorded before horizon_lensed_cost "
                "is applied; the engineered horizon-mass lens is used only as a reference column"
            ),
            "positive_signature": (
                "raw backreacting A* paths spend more of their route in the inner shell band "
                "than the no-backreaction baseline"
            ),
            "physical_boundary": (
                "finite sandpile transport witness only; a negative result means the current "
                "absorption law does not produce unaided path bending"
            ),
        },
        "witness": {
            "summary": {
                "astar_sample_count": len(rows),
                "raw_astar_inner_band_delta_vs_baseline_mean": raw_mean,
                "lensed_astar_inner_band_delta_vs_baseline_mean": lensed_mean,
                "raw_positive_frame_count": raw_positive_count,
                "lensed_positive_frame_count": lensed_positive_count,
                "final_horizon_mass": int(summary["final_horizon_mass"]),
                "horizon_lens_factor_mean": float(summary["horizon_lens_factor_mean"]),
                "source_micro_status": micro.get("status"),
            },
            "frame_deltas": rows,
        },
        "checks": checks,
    }
    payload["artifact_sha256_excluding_this_field"] = artifact_hash(payload)
    return payload


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    raw_positive = artifact["checks"]["raw_transport_bends_toward_horizon_without_lens"]
    if raw_positive:
        claim = (
            "The current D20 micro-horizon backreaction also bends raw, no-lens A* transport "
            "toward the inner shell band."
        )
    else:
        claim = (
            "The current D20 micro-horizon backreaction is not raw-A* positive without the "
            "explicit horizon-mass lens; the black-hole-like lensing claim remains a "
            "test-particle lens seam, not an unaided transport emergence."
        )
    report = {
        "schema": "d20.proof_obligation.micro_black_hole_raw_transport_probe@1",
        "status": artifact["status"],
        "claim": claim,
        "stages": {
            "draft": "define no-lens raw A* horizon-bending test",
            "witness": "read certified backreaction artifact raw_astar shadow fields",
            "coherence": "compare raw and lensed deltas against source summary",
            "closure": "emit negative or raw-positive status without changing the source simulation",
            "emit": "publish frame deltas and explicit claim boundary",
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
        "all_checks_pass": all(artifact["checks"].values()),
        "closure_boundary": {
            "certifies": [
                "the current raw no-lens A* shadow metric against the certified micro-horizon artifact",
                "whether raw transport is positive independently of the engineered horizon lens",
            ],
            "does_not_certify": [
                "physical black-hole behavior",
                "raw unaided lensing when status is NEGATIVE",
                "any absorption-law variant not present in the source micro-horizon artifact",
            ],
        },
        "next_highest_yield_item": (
            "If raw transport remains negative, tune only the explicit absorption law and keep "
            "horizon_lensed_cost disabled for the primary A* pass until raw inner-band delta is positive."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest = {
        "schema": "d20.proof_obligation.micro_black_hole_raw_transport_probe_manifest@1",
        "name": THEOREM_ID,
        "certification_tests": [
            "load the certified micro black-hole backreaction artifact",
            "extract raw no-lens A* shadow fields",
            "compare raw and lensed inner-band deltas",
            "classify the current law as raw-positive or negative",
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
    summary = report["witness"]["summary"]
    print(
        json.dumps(
            {
                "artifact": relpath(ARTIFACT_PATH),
                "report": relpath(OUT_DIR / "report.json"),
                "report_sha256": report["certificate_sha256"],
                "status": report["status"],
                "raw_astar_inner_band_delta_vs_baseline_mean": summary[
                    "raw_astar_inner_band_delta_vs_baseline_mean"
                ],
                "lensed_astar_inner_band_delta_vs_baseline_mean": summary[
                    "lensed_astar_inner_band_delta_vs_baseline_mean"
                ],
                "raw_positive_frame_count": summary["raw_positive_frame_count"],
                "lensed_positive_frame_count": summary["lensed_positive_frame_count"],
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
