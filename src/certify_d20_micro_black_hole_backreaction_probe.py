from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
import math
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_micro_black_hole_backreaction_probe import (
        ARTIFACT_PATH,
        ASTAR_FRAME_STRIDE,
        FRAME_COUNT,
        INDEX_PATH,
        OUT_DIR,
        PATH_PAIR_COUNT,
        THEOREM_ID,
        build_artifact,
        build_manifest,
        build_report,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_d20_micro_black_hole_backreaction_probe import (
        ARTIFACT_PATH,
        ASTAR_FRAME_STRIDE,
        FRAME_COUNT,
        INDEX_PATH,
        OUT_DIR,
        PATH_PAIR_COUNT,
        THEOREM_ID,
        build_artifact,
        build_manifest,
        build_report,
    )


ARTIFACT_REL = ARTIFACT_PATH.relative_to(ROOT).as_posix()
REPORT_REL = (OUT_DIR / "report.json").relative_to(ROOT).as_posix()
MANIFEST_REL = (OUT_DIR / "manifest.json").relative_to(ROOT).as_posix()
INDEX_REL = INDEX_PATH.relative_to(ROOT).as_posix()

EXPECTED_CHECKS = {
    "horizon_flux_probe_is_recorded",
    "tesla_coil_probe_is_recorded",
    "backreaction_frame_count_is_97",
    "sink_ledger_mass_is_positive",
    "sink_ledger_mass_is_monotone",
    "sink_ledger_has_invariant_charge_breakdown",
    "backreaction_reduces_live_grains_vs_baseline",
    "polarization_increases_vs_baseline",
    "coil_coherence_increases_vs_baseline",
    "astar_bends_toward_horizon_vs_baseline",
    "flux_localization_improves_vs_baseline",
}

EXPECTED_STATUSES = {
    "D20_MICRO_BLACK_HOLE_BACKREACTION_PROBE_CERTIFIED",
    "D20_MICRO_BLACK_HOLE_BACKREACTION_PROBE_PROVISIONAL",
}


def _load_json(rel_path: str) -> dict[str, Any]:
    with (ROOT / rel_path).open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise AssertionError(f"{rel_path} is not a JSON object")
    return payload


def _self_hash(payload: dict[str, Any], field: str) -> str:
    tmp = dict(payload)
    tmp.pop(field, None)
    return h_json(tmp)


def _check_input_file(entry: dict[str, Any], rel_path: str, label: str) -> None:
    if entry.get("path") != rel_path:
        raise AssertionError(f"{label} path mismatch")
    if h_file(ROOT / rel_path) != entry.get("sha256"):
        raise AssertionError(f"{label} file hash mismatch")


def _assert_finite(value: Any, label: str) -> None:
    if not math.isfinite(float(value)):
        raise AssertionError(f"{label} is not finite")


def _assert_ledger_sums(ledger: dict[str, Any]) -> None:
    mass = int(ledger.get("horizon_mass", -1))
    if mass <= 0:
        raise AssertionError("micro black hole ledger mass is not positive")
    for key in ("by_fiber", "by_order", "by_grade", "by_mixed"):
        total = sum(int(value) for value in ledger.get(key, {}).values())
        if total != mass:
            raise AssertionError(f"micro black hole ledger {key} does not sum to mass")


def validate_d20_micro_black_hole_backreaction_probe() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != "d20.proof_obligation.micro_black_hole_backreaction_probe.artifact@1":
        raise AssertionError("micro black hole artifact schema mismatch")
    if artifact.get("status") not in EXPECTED_STATUSES:
        raise AssertionError("micro black hole artifact status mismatch")
    if _self_hash(artifact, "artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("micro black hole artifact self hash mismatch")
    rebuilt_artifact = build_artifact()
    if rebuilt_artifact.get("artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("micro black hole artifact is not reproducible")

    checks = artifact.get("checks", {})
    if set(checks) != EXPECTED_CHECKS:
        raise AssertionError("micro black hole checks mismatch")
    if artifact.get("status") == "D20_MICRO_BLACK_HOLE_BACKREACTION_PROBE_CERTIFIED" and not all(
        checks.values()
    ):
        raise AssertionError("certified micro black hole artifact has failing checks")
    if artifact.get("status") == "D20_MICRO_BLACK_HOLE_BACKREACTION_PROBE_PROVISIONAL" and all(
        checks.values()
    ):
        raise AssertionError("provisional micro black hole artifact has no failing checks")

    witness = artifact.get("witness", {})
    summary = witness.get("summary", {})
    baseline = witness.get("baseline", {})
    backreaction = witness.get("backreaction", {})
    ledger = backreaction.get("ledger", {})
    _assert_ledger_sums(ledger)

    if int(summary.get("frame_count", 0)) != FRAME_COUNT:
        raise AssertionError("micro black hole frame count mismatch")
    expected_astar_samples = (FRAME_COUNT - 1) // ASTAR_FRAME_STRIDE + 1
    if int(summary.get("astar_sample_count", 0)) != expected_astar_samples:
        raise AssertionError("micro black hole A* sample count mismatch")
    if len(baseline.get("astar_rows", [])) != expected_astar_samples:
        raise AssertionError("baseline A* row count mismatch")
    if len(backreaction.get("astar_rows", [])) != expected_astar_samples:
        raise AssertionError("backreaction A* row count mismatch")
    if len(baseline.get("rows_first_12", [])) != 12:
        raise AssertionError("baseline first rows witness mismatch")
    if len(backreaction.get("rows_first_12", [])) != 12:
        raise AssertionError("backreaction first rows witness mismatch")
    compact_rows = backreaction.get("rows_compact", [])
    if len(compact_rows) != FRAME_COUNT:
        raise AssertionError("backreaction compact replay row count mismatch")

    masses = [int(row.get("horizon_mass", 0)) for row in backreaction.get("rows_first_12", [])]
    if any(right < left for left, right in zip(masses, masses[1:])):
        raise AssertionError("micro black hole first-row horizon mass decreases")
    compact_masses = [int(row.get("horizon_mass", 0)) for row in compact_rows]
    if any(right < left for left, right in zip(compact_masses, compact_masses[1:])):
        raise AssertionError("micro black hole compact replay horizon mass decreases")
    if compact_masses[-1] != int(summary.get("final_horizon_mass", -1)):
        raise AssertionError("micro black hole compact replay final mass mismatch")
    if compact_masses[-1] != int(ledger.get("horizon_mass", -2)):
        raise AssertionError("micro black hole compact replay ledger mass mismatch")
    for idx, row in enumerate(compact_rows):
        if int(row.get("frame", -1)) != idx:
            raise AssertionError("micro black hole compact replay frame sequence mismatch")
        lens = float(row.get("horizon_lens_factor", -1.0))
        if lens < 0.0 or lens > 1.0:
            raise AssertionError("micro black hole compact replay lens factor out of range")
        for key in (
            "horizon_mass",
            "absorbed_this_frame",
            "live_grains",
            "polarization_order",
            "coil_phase_coherence",
            "post_flux_localization",
            "horizon_lens_factor",
            "astar_inner_band_fraction_mean",
            "raw_astar_inner_band_fraction_mean",
        ):
            _assert_finite(row.get(key), f"compact replay {key}")
    for row in baseline.get("astar_rows", []) + backreaction.get("astar_rows", []):
        if float(row.get("paths_found", 0.0)) != float(PATH_PAIR_COUNT):
            raise AssertionError("micro black hole sampled A* row did not find all paths")
        for key in (
            "horizon_mass",
            "horizon_lens_factor",
            "horizon_lens_potential_shell_mean",
            "raw_axis_alignment_mean",
            "raw_high_flux_overlap_fraction_mean",
            "raw_inner_band_fraction_mean",
            "raw_angular_sweep_turns_mean",
        ):
            _assert_finite(row.get(key), f"sampled A* row {key}")

    for label, value in {
        "final_horizon_mass": summary.get("final_horizon_mass"),
        "polarization_delta_vs_baseline_mean": summary.get("polarization_delta_vs_baseline_mean"),
        "coil_coherence_delta_vs_baseline_mean": summary.get("coil_coherence_delta_vs_baseline_mean"),
        "tangential_flow_delta_vs_baseline_mean": summary.get("tangential_flow_delta_vs_baseline_mean"),
        "post_flux_localization_delta_vs_baseline_mean": summary.get(
            "post_flux_localization_delta_vs_baseline_mean"
        ),
        "astar_inner_band_delta_vs_baseline_mean": summary.get(
            "astar_inner_band_delta_vs_baseline_mean"
        ),
        "raw_astar_inner_band_delta_vs_baseline_mean": summary.get(
            "raw_astar_inner_band_delta_vs_baseline_mean"
        ),
        "astar_angular_sweep_delta_vs_baseline_mean": summary.get(
            "astar_angular_sweep_delta_vs_baseline_mean"
        ),
        "raw_astar_angular_sweep_delta_vs_baseline_mean": summary.get(
            "raw_astar_angular_sweep_delta_vs_baseline_mean"
        ),
        "astar_high_flux_overlap_delta_vs_baseline_mean": summary.get(
            "astar_high_flux_overlap_delta_vs_baseline_mean"
        ),
        "raw_astar_high_flux_overlap_delta_vs_baseline_mean": summary.get(
            "raw_astar_high_flux_overlap_delta_vs_baseline_mean"
        ),
        "horizon_lens_factor_mean": summary.get("horizon_lens_factor_mean"),
        "horizon_lens_potential_shell_mean": summary.get(
            "horizon_lens_potential_shell_mean"
        ),
    }.items():
        _assert_finite(value, label)

    if report.get("schema") != "d20.proof_obligation.micro_black_hole_backreaction_probe@1":
        raise AssertionError("micro black hole report schema mismatch")
    if report.get("status") != artifact.get("status"):
        raise AssertionError("micro black hole report status mismatch")
    if report.get("all_checks_pass") != all(checks.values()):
        raise AssertionError("micro black hole report all_checks_pass mismatch")
    if report.get("checks") != checks:
        raise AssertionError("micro black hole report checks differ from artifact")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("micro black hole report self hash mismatch")
    expected_report = build_report(artifact)
    if expected_report.get("certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("micro black hole report is not reproducible")

    _check_input_file(report.get("inputs", {}).get("artifact", {}), ARTIFACT_REL, "artifact input")
    _check_input_file(
        report.get("inputs", {}).get("horizon_flux_astar_probe_report", {}),
        "data/invariants/d20/proof_obligations/d20_horizon_flux_astar_probe/report.json",
        "horizon flux input",
    )
    _check_input_file(
        report.get("inputs", {}).get("tesla_coil_astar_flux_probe_report", {}),
        "data/invariants/d20/proof_obligations/d20_tesla_coil_astar_flux_probe/report.json",
        "Tesla coil input",
    )
    _check_input_file(
        report.get("inputs", {}).get("validator", {}),
        "src/certify_d20_micro_black_hole_backreaction_probe.py",
        "validator input",
    )

    if manifest.get("schema") != "d20.proof_obligation.micro_black_hole_backreaction_probe_manifest@1":
        raise AssertionError("micro black hole manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("micro black hole manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("micro black hole manifest artifact hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("micro black hole manifest self hash mismatch")
    expected_manifest = build_manifest(report, artifact)
    if expected_manifest.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("micro black hole manifest is not reproducible")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("micro black hole registry entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("micro black hole registry report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("micro black hole registry status mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_micro_black_hole_backreaction_probe()
    print("D20 micro black hole backreaction probe validated")
