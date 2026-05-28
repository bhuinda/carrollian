from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = ROOT / "generated" / "d20_black_hole_atom_lab_report.json"
PROOF_JSON = ROOT / "data" / "invariants" / "d20" / "proof_obligations" / "d20_black_hole_atom_lab_report" / "report.json"
ATLAS_JS = ROOT / "generated" / "d20_black_hole_pressure_atlas_data.js"
BOUNDARY_NOTES_MD = ROOT / "generated" / "d20_boundary_physics_discovery_notes.md"
PROOF_NOTES_MD = ROOT / "data" / "invariants" / "d20" / "proof_obligations" / "d20_black_hole_atom_lab_report" / "boundary_physics_discovery_notes.md"
BRIDGE_PROBE_JSON = ROOT / "generated" / "d20_hydrogen_sandpile_golay_bridge_probe.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def approx(actual: float, expected: float, tolerance: float, message: str) -> None:
    require(abs(actual - expected) <= tolerance, f"{message}: {actual!r} != {expected!r}")


def main() -> None:
    require(REPORT_JSON.exists(), "Missing generated black-hole atom lab report")
    require(PROOF_JSON.exists(), "Missing black-hole atom proof obligation report")
    require(ATLAS_JS.exists(), "Missing generated black-hole pressure atlas data")
    require(BOUNDARY_NOTES_MD.exists(), "Missing generated boundary physics discovery notes")
    require(PROOF_NOTES_MD.exists(), "Missing proof boundary physics discovery notes")
    require(BRIDGE_PROBE_JSON.exists(), "Missing generated A985/q12 bridge probe")
    report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
    proof = json.loads(PROOF_JSON.read_text(encoding="utf-8"))
    boundary_notes = BOUNDARY_NOTES_MD.read_text(encoding="utf-8")
    proof_notes = PROOF_NOTES_MD.read_text(encoding="utf-8")
    require(report["status"] == "D20_BLACK_HOLE_ATOM_LAB_REPORT_CERTIFIED", "Unexpected report status")
    require(proof["status"] == report["status"], "Proof status mismatch")
    require(proof["report_sha256"] == hashlib.sha256(REPORT_JSON.read_bytes()).hexdigest(), "Report sha256 mismatch")
    require(proof_notes == boundary_notes, "Boundary discovery notes proof copy mismatch")
    require(proof["boundary_discovery_notes_sha256"] == hashlib.sha256(BOUNDARY_NOTES_MD.read_bytes()).hexdigest(), "Boundary notes sha256 mismatch")
    require(proof["boundary_discovery_notes_artifact"] in {"generated\\d20_boundary_physics_discovery_notes.md", "generated/d20_boundary_physics_discovery_notes.md"}, "Unexpected boundary notes artifact")
    require(report["verdict"] == "FINITE_BOUNDARY_PROXY_READY", "Unexpected verdict")
    require(all(report["html_checks"].values()), f"HTML checks failed: {report['html_checks']}")
    require(all(report["js_checks"].values()), f"JS checks failed: {report['js_checks']}")
    require(all(report["css_checks"].values()), f"CSS checks failed: {report['css_checks']}")
    require(all(report["equation_checks"].values()), f"Equation checks failed: {report['equation_checks']}")
    require(all(report["atlas_checks"].values()), f"Atlas checks failed: {report['atlas_checks']}")
    invariants = report["invariants"]
    approx(float(invariants["alpha_star"]), 1 / 137, 1e-15, "alpha star")
    approx(float(invariants["alpha_wall"]), 0.25, 1e-15, "alpha wall")
    approx(float(invariants["lambda_ev"]), 54.4, 1e-12, "hydrogen scale")
    require(int(invariants["fine_denominator"]) == 75076, "Fine denominator mismatch")
    approx(float(invariants["lamb_reference_mhz"]), 1057.845020, 1e-9, "Lamb reference")
    rows = {row["label"]: row for row in report["level_rows"]}
    require({"1S1/2", "2S1/2", "2P1/2", "2P3/2"}.issubset(rows), "Missing required hydrogen levels")
    approx(float(rows["1S1/2"]["principal"]), -0.25, 1e-12, "1S principal")
    approx(float(rows["2P1/2"]["principal"]), -0.0625, 1e-12, "2P principal")
    require(float(rows["2S1/2"]["energy_ev"]) > float(rows["2P1/2"]["energy_ev"]), "Lamb shifted 2S should sit above 2P1/2 in this binding convention")
    require(int(report["wind_pressure_rows_found"]) >= 6, "Need at least six wind pressure rows")
    require(int(report["correlation_summary"]["rows"]) >= 36, "Need at least 36 correlation rows")
    atlas = report["pressure_atlas_summary"]
    require(int(atlas["identity_rows"]) == 6, "Atlas must expose six identity inlets")
    require(int(atlas["null_rows"]) == 4314, "Atlas must expose 4314 null rows")
    require(all(int(value) == 719 for value in atlas["null_rows_per_inlet"].values()), "Atlas null rows must be 719 per inlet")
    require(atlas["verdict"] in {"IDENTITY_SINK_EXCEEDS_NULL_P95", "NULL_BASELINE_CONTAINS_IDENTITY_SINKS"}, "Unexpected atlas verdict")
    require(math.isfinite(float(atlas["mean_top_sink_margin"])), "Mean top sink margin must be finite")
    require(0 <= float(atlas["mean_top_sink_percentile"]) <= 1, "Mean top sink percentile out of range")
    c985 = atlas["c985_summary"]
    require(c985["basis"] == ["R33", "K_mixed_S", "K_pure_Sminus"], "C985 basis mismatch")
    require("R33_global(mask)=13*" in c985["r33_rule"], "Missing R33 global rule")
    require(int(c985["r33_sourced_closed_returns"]) >= 0, "Invalid R33 sourced count")
    require(int(c985["mixed_s_support"]) >= 0, "Invalid K_mixed_S count")
    require(int(c985["pure_sminus_support"]) >= 0, "Invalid K_pure_Sminus count")
    transition = atlas["c985_transition_summary"]
    require(int(transition["steps"]) == 16, "Transition ledger must replay 16 finite gate steps")
    require(len(transition["gate_sequence"]) == 16, "Gate sequence length mismatch")
    require(int(transition["r33_sourced_steps"]) >= 0, "Invalid R33 sourced transition count")
    require(int(transition["longest_r33_run"]) >= 0, "Invalid R33 run length")
    require(transition["rows"] and all("flux_label" in row for row in transition["rows"]), "Transition rows must carry flux labels")
    require(report["atlas_checks"]["dynamic_pulse_wiring"], "Missing dynamic pulse-history wiring")
    require(report["atlas_checks"]["dynamic_playback_wiring"], "Missing dynamic playback wiring")
    require(report["atlas_checks"]["lagged_scan"], "Missing lagged correlation scan")
    require(report["atlas_checks"]["lagged_browser_readouts"], "Missing lagged browser readouts")
    require(report["atlas_checks"]["lagged_null_significance"], "Missing lagged null significance")
    require(report["atlas_checks"]["signed_flux_lag"], "Missing signed C985 flux lag scan")
    require(report["atlas_checks"]["signed_flux_browser_readouts"], "Missing signed C985 flux browser readouts")
    require(report["atlas_checks"]["height_flux_lag"], "Missing signed C985 height-flux lag scan")
    require(report["atlas_checks"]["height_flux_browser_readouts"], "Missing signed C985 height-flux browser readouts")
    require(report["atlas_checks"]["zero_pair_ward_lag"], "Missing zero-pair Ward lag scan")
    require(report["atlas_checks"]["zero_pair_ward_browser_readouts"], "Missing zero-pair Ward browser readouts")
    require(report["atlas_checks"]["c2_markov_orbit_lag"], "Missing C2 Markov orbit lag scan")
    require(report["atlas_checks"]["c2_markov_orbit_browser_readouts"], "Missing C2 Markov orbit browser readouts")
    require(report["atlas_checks"]["c2_markov_operator_theorem"], "Missing C2 Markov operator theorem witness")
    require(report["atlas_checks"]["c2_selector_family_lag"], "Missing C2 selector-family lag scan")
    require(report["atlas_checks"]["c2_selector_family_browser_readouts"], "Missing C2 selector-family browser readouts")
    require(report["atlas_checks"]["c2_dynamics_selector_theorem"], "Missing C2 dynamics selector theorem witness")
    require(report["atlas_checks"]["c2_markov_trajectory"], "Missing C2 Markov trajectory distribution test")
    require(report["atlas_checks"]["c2_markov_trajectory_browser_readouts"], "Missing C2 Markov trajectory browser readouts")
    require(report["atlas_checks"]["boundary_only_panel"], "Missing boundary-only Ward/BMS panel")
    require(report["atlas_checks"]["ward_bms_3d_renderer"], "Missing WebGL 3D Ward/BMS renderer")
    require(report["atlas_checks"]["ward_bms_3d_trails"], "Missing WebGL 3D Ward/BMS transition trails")
    require(report["atlas_checks"]["boundary_dynamics_samples"], "Missing boundary dynamics samples")
    require(report["atlas_checks"]["boundary_dynamics_browser_readouts"], "Missing boundary dynamics browser readouts")
    require(report["atlas_checks"]["boundary_motif_counts"], "Missing boundary motif counts")
    require(report["atlas_checks"]["boundary_packet_bridge_seam"], "Missing boundary-packet bridge seam receipts")
    require(report["atlas_checks"]["rank_one_packet_family_sink_residual"], "Missing rank-one packet family sink/residual test")
    require(report["atlas_checks"]["signed_rank_one_packet_quotient"], "Missing signed rank-one packet quotient observable")
    require(report["atlas_checks"]["signed_packet_quotient_lag"], "Missing signed packet quotient hydrogen-lag test")
    require(report["atlas_checks"]["support3_signed_quotient_screen"], "Missing support-3 signed quotient screen")
    require(report["atlas_checks"]["support3_signed_quotient_lag"], "Missing support-3 signed quotient hydrogen-lag test")
    require(report["atlas_checks"]["a985_q12_packet_bridge_probe"], "Missing A985/q12 packet bridge probe integration")
    require(report["atlas_checks"]["falsification_ledger"], "Missing falsification ledger")
    require(report["atlas_checks"]["falsification_taxonomy"], "Missing falsification taxonomy")
    require(report["atlas_checks"]["falsification_browser_readouts"], "Missing falsification browser readouts")
    k_effect = transition["k_effect"]
    require(int(k_effect["mixed_count"]) + int(k_effect["pure_count"]) + int(k_effect["neither_count"]) >= 6, "K-effect sample too small")
    require(math.isfinite(float(k_effect["mixed_mean_margin"])), "Mixed K margin must be finite")
    require(math.isfinite(float(k_effect["pure_mean_margin"])), "Pure K margin must be finite")
    lagged = atlas["lagged_correlation_summary"]
    require(int(lagged["lags"]) == 16, "Lagged scan must cover 16 cyclic offsets")
    require(len(lagged["rows"]) == 16, "Lag rows length mismatch")
    require(0 <= int(lagged["best_lag"]) < 16, "Best lag out of range")
    require(math.isfinite(float(lagged["best_rho"])) and -1 <= float(lagged["best_rho"]) <= 1, "Best lag rho out of range")
    require(lagged["verdict"] in {"PHASE_SHIFTED_COUPLING_CANDIDATE", "NO_PHASED_HYDROGEN_HORIZON_COUPLING"}, "Unexpected lagged verdict")
    null_sig = lagged["null_significance"]
    require(int(null_sig["null_histories"]) == 719, "Lag null test must cover 719 null pulse histories")
    require(0 <= float(null_sig["p_value"]) <= 1, "Lag null p-value out of range")
    require(null_sig["verdict"] in {"PHASE_SIGNAL_BEATS_NULL_95", "PHASE_SIGNAL_WITHIN_NULL"}, "Unexpected lag null verdict")
    require(math.isfinite(float(null_sig["null_p95_max_abs_rho"])), "Lag null p95 must be finite")
    signed_flux = atlas["signed_flux_lag_summary"]
    require(signed_flux["observable"] == "signed_C985_flux_balance", "Unexpected signed flux observable")
    require(int(signed_flux["lags"]) == 16, "Signed flux lag scan must cover 16 cyclic offsets")
    require(0 <= int(signed_flux["best_lag"]) < 16, "Signed flux best lag out of range")
    require(math.isfinite(float(signed_flux["best_rho"])) and -1 <= float(signed_flux["best_rho"]) <= 1, "Signed flux best rho out of range")
    signed_null = signed_flux["null_significance"]
    require(int(signed_null["null_histories"]) == 719, "Signed flux null test must cover 719 null pulse histories")
    require(0 <= float(signed_null["p_value"]) <= 1, "Signed flux null p-value out of range")
    require(signed_null["verdict"] in {"SIGNED_FLUX_BEATS_NULL_95", "SIGNED_FLUX_WITHIN_NULL"}, "Unexpected signed flux null verdict")
    height_flux = atlas["height_flux_lag_summary"]
    require(height_flux["observable"] == "signed_C985_height_flux_balance", "Unexpected height-flux observable")
    require("bare Pi33 + R33_height_residual + finite_height_flux = 0" in height_flux["ledger_equation"], "Missing height-flux ledger equation")
    require(int(height_flux["lags"]) == 16, "Height-flux lag scan must cover 16 cyclic offsets")
    require(0 <= int(height_flux["best_lag"]) < 16, "Height-flux best lag out of range")
    require(math.isfinite(float(height_flux["best_rho"])) and -1 <= float(height_flux["best_rho"]) <= 1, "Height-flux best rho out of range")
    height_null = height_flux["null_significance"]
    require(int(height_null["null_histories"]) == 719, "Height-flux null test must cover 719 null pulse histories")
    require(0 <= float(height_null["p_value"]) <= 1, "Height-flux null p-value out of range")
    require(height_null["verdict"] in {"HEIGHT_FLUX_BEATS_NULL_95", "HEIGHT_FLUX_WITHIN_NULL"}, "Unexpected height-flux null verdict")
    ward = atlas["zero_pair_ward_lag_summary"]
    require(ward["observable"] == "zero_pair_ward_height_selector", "Unexpected zero-pair Ward observable")
    require(int(ward["source_mask"]) == 288, "Zero-pair Ward source mask mismatch")
    require(ward["source_bits"] == [5, 8], "Zero-pair Ward source bits mismatch")
    require(int(ward["source_action"]) == 1065984, "Zero-pair Ward source action mismatch")
    require("13 + 13 = 0 mod 26" in ward["corrected_ward_clock"], "Missing zero-pair Ward corrected clock")
    require(int(ward["shared_atom"]) == 11, "Zero-pair Ward shared atom mismatch")
    require(int(ward["lags"]) == 16, "Zero-pair Ward lag scan must cover 16 cyclic offsets")
    require(0 <= int(ward["best_lag"]) < 16, "Zero-pair Ward best lag out of range")
    require(math.isfinite(float(ward["best_rho"])) and -1 <= float(ward["best_rho"]) <= 1, "Zero-pair Ward best rho out of range")
    ward_null = ward["null_significance"]
    require(int(ward_null["null_histories"]) == 719, "Zero-pair Ward null test must cover 719 null pulse histories")
    require(0 <= float(ward_null["p_value"]) <= 1, "Zero-pair Ward null p-value out of range")
    require(ward_null["verdict"] in {"ZERO_PAIR_WARD_BEATS_NULL_95", "ZERO_PAIR_WARD_WITHIN_NULL"}, "Unexpected zero-pair Ward null verdict")
    orbit = atlas["c2_markov_orbit_lag_summary"]
    require(orbit["observable"] == "c2_markov_orbit_height_drift", "Unexpected C2 Markov orbit observable")
    require(orbit["theorem_status"] == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_SCATTERING_OPERATOR_CERTIFIED", "Unexpected C2 Markov theorem status")
    require(int(orbit["target_orbit_count"]) == 543, "C2 Markov target orbit count mismatch")
    require(int(orbit["rank"]) == 288, "C2 Markov rank mismatch")
    require(int(orbit["nullity"]) == 255, "C2 Markov nullity mismatch")
    require(int(orbit["stationary_distribution_denominator"]) == 2046, "C2 Markov stationary denominator mismatch")
    require(int(orbit["lags"]) == 16, "C2 Markov orbit lag scan must cover 16 cyclic offsets")
    require(0 <= int(orbit["best_lag"]) < 16, "C2 Markov orbit best lag out of range")
    require(math.isfinite(float(orbit["best_rho"])) and -1 <= float(orbit["best_rho"]) <= 1, "C2 Markov orbit best rho out of range")
    orbit_null = orbit["null_significance"]
    require(int(orbit_null["null_histories"]) == 719, "C2 Markov orbit null test must cover 719 null pulse histories")
    require(0 <= float(orbit_null["p_value"]) <= 1, "C2 Markov orbit null p-value out of range")
    require(orbit_null["verdict"] in {"C2_MARKOV_ORBIT_BEATS_NULL_95", "C2_MARKOV_ORBIT_WITHIN_NULL"}, "Unexpected C2 Markov orbit null verdict")
    selector = atlas["c2_selector_family_lag_summary"]
    require(selector["observable"] == "c2_selector_family_mask_overlap", "Unexpected C2 selector-family observable")
    require(selector["theorem_status"] == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_DYNAMICS_SELECTOR_CERTIFIED", "Unexpected C2 selector theorem status")
    require(int(selector["candidate_count"]) >= 3, "C2 selector-family needs at least three candidates")
    require(selector["best_candidate"] in {"primitive_seeded", "global_action_minimal", "paired_action_minimal"}, "Unexpected C2 selector best candidate")
    require(0 <= int(selector["best_lag"]) < 16, "C2 selector best lag out of range")
    require(math.isfinite(float(selector["best_rho"])) and -1 <= float(selector["best_rho"]) <= 1, "C2 selector best rho out of range")
    require(0 <= float(selector["best_null_p"]) <= 1, "C2 selector null p-value out of range")
    require(selector["best_null_verdict"] in {"C2_SELECTOR_BEATS_NULL_95", "C2_SELECTOR_WITHIN_NULL"}, "Unexpected C2 selector null verdict")
    require(all(int(row["null_significance"]["null_histories"]) == 719 for row in selector["rows"]), "Each C2 selector candidate must use 719 null histories")
    trajectory = atlas["c2_markov_trajectory_summary"]
    require(trajectory["observable"] == "c2_markov_trajectory_distribution", "Unexpected C2 trajectory observable")
    require(trajectory["metric"] == "total_variation_distance_after_4_markov_steps", "Unexpected C2 trajectory metric")
    require(int(trajectory["trajectory_steps"]) == 4, "C2 trajectory step count mismatch")
    require(int(trajectory["target_orbit_count"]) == 543, "C2 trajectory orbit count mismatch")
    require(0 <= float(trajectory["identity_total_variation"]) <= 1, "C2 trajectory TV out of range")
    trajectory_null = trajectory["null_significance"]
    require(int(trajectory_null["null_histories"]) == 719, "C2 trajectory null test must cover 719 null pulse histories")
    require(0 <= float(trajectory_null["p_value"]) <= 1, "C2 trajectory null p-value out of range")
    require(trajectory_null["verdict"] in {"C2_MARKOV_TRAJECTORY_BEATS_NULL_05", "C2_MARKOV_TRAJECTORY_WITHIN_NULL"}, "Unexpected C2 trajectory null verdict")
    boundary = atlas["boundary_dynamics_summary"]
    require(boundary["observable"] == "boundary_only_ward_bms_component_samples", "Unexpected boundary dynamics observable")
    require(int(boundary["target_orbit_count"]) == 543, "Boundary dynamics orbit count mismatch")
    require(int(boundary["rank"]) == 288, "Boundary dynamics rank mismatch")
    require(int(boundary["nullity"]) == 255, "Boundary dynamics nullity mismatch")
    require(len(boundary["component_size_by_orbit"]) == 543, "Boundary component-size map mismatch")
    require(len(boundary["component_id_by_orbit"]) == 543, "Boundary component-id map mismatch")
    require(len(boundary["zero_exit_orbit_ids"]) == 2, "Boundary zero-exit orbit count mismatch")
    require(len(boundary["component_representatives"]) >= 8, "Need boundary component representatives")
    require(len(boundary["transition_samples"]) == 16, "Need 16 boundary transition samples")
    require(all(sample["targets"] for sample in boundary["transition_samples"]), "Every boundary transition sample needs targets")
    motifs = boundary["motif_counts"]
    require(int(motifs["motif_total"]) == 16, "Boundary motif count should cover 16 transitions")
    require(int(motifs["unique_motifs"]) >= 1, "Boundary motif count should have at least one motif")
    require(motifs["top_motifs"], "Boundary motif count needs top motifs")
    ledger = atlas["falsification_ledger_summary"]
    require(int(ledger["total_claims"]) == 11, "Falsification ledger must contain eleven claim rows")
    require(int(ledger["failed_claims"]) >= 1, "Falsification ledger must record at least one failed claim")
    require(int(ledger["supported_claims"]) >= 1, "Falsification ledger must preserve supported boundary evidence")
    require(ledger["overall_status"] in {"BOUNDARY_SINK_SUPPORTED_COUPLING_NOT_SUPPORTED", "BOUNDARY_SINK_SUPPORTED_HEIGHT_FLUX_CANDIDATE", "BOUNDARY_SINK_SUPPORTED_ZERO_PAIR_WARD_CANDIDATE", "BOUNDARY_SINK_SUPPORTED_C2_MARKOV_ORBIT_CANDIDATE", "BOUNDARY_SINK_SUPPORTED_C2_SELECTOR_FAMILY_CANDIDATE", "BOUNDARY_SINK_SUPPORTED_C2_MARKOV_TRAJECTORY_CANDIDATE", "BOUNDARY_SINK_SUPPORTED_SIGNED_PACKET_QUOTIENT_CANDIDATE", "BOUNDARY_SINK_SUPPORTED_SUPPORT3_SIGNED_QUOTIENT_CANDIDATE"}, "Unexpected falsification status")
    statuses = {row["claim"]: row["status"] for row in ledger["rows"]}
    require(all("ledger_source" in row and "observable_class" in row for row in ledger["rows"]), "Falsification rows need source taxonomy")
    require(ledger["taxonomy"]["next_class"] in {"support-3 residual and source-state audit", "residual-only hydrogen coupling audit", "A985/q12 packet projection construction"}, "Unexpected next observable class")
    require(statuses["finite_boundary_sink"] == "supported_proxy", "Boundary sink claim should remain supported")
    require(statuses["raw_pressure_margin_phase_coupling"] == "failed_null", "Raw phase coupling should fail null test")
    require(statuses["signed_C985_flux_phase_coupling"] == "failed_null", "Signed C985 flux phase coupling should fail null test")
    require(statuses["signed_C985_height_flux_phase_coupling"] in {"failed_null", "supported_candidate"}, "Unexpected height-flux claim status")
    require(statuses["zero_pair_ward_height_selector_phase_coupling"] in {"failed_null", "supported_candidate"}, "Unexpected zero-pair Ward claim status")
    require(statuses["c2_markov_orbit_height_drift_phase_coupling"] in {"failed_null", "supported_candidate"}, "Unexpected C2 Markov orbit claim status")
    require(statuses["c2_selector_family_mask_overlap_phase_coupling"] in {"failed_null", "supported_candidate"}, "Unexpected C2 selector-family claim status")
    require(statuses["c2_markov_trajectory_distribution_coupling"] in {"failed_null", "supported_candidate"}, "Unexpected C2 trajectory claim status")
    require(statuses["signed_packet_quotient_hydrogen_coupling"] in {"failed_null", "supported_candidate"}, "Unexpected signed packet quotient hydrogen claim status")
    require(statuses["support3_signed_packet_quotient_hydrogen_coupling"] in {"failed_null", "supported_candidate"}, "Unexpected support-3 signed quotient hydrogen claim status")
    bridge = report["a985_q12_packet_bridge_probe_summary"]
    require(bridge["artifact"] in {"generated\\d20_hydrogen_sandpile_golay_bridge_probe.json", "generated/d20_hydrogen_sandpile_golay_bridge_probe.json"}, "Unexpected bridge probe artifact")
    require(bridge["artifact_file_sha256"] == hashlib.sha256(BRIDGE_PROBE_JSON.read_bytes()).hexdigest(), "Bridge probe file sha256 mismatch")
    require(bridge["all_checks_pass"] is True, "Bridge probe checks must pass")
    require(bridge["status"] == "D20_HYDROGEN_SANDPILE_GOLAY_BRIDGE_PROBE_PROVISIONAL_ASSIGNMENT_DEGENERATE", "Unexpected bridge probe status")
    require(bridge["ingress_projection_inventory"]["status"] == "INGRESS_BOUNDARY_TO_LOOP_PRESENT_PACKET_PROJECTION_MISSING", "Unexpected bridge ingress inventory status")
    require(int(bridge["ingress_projection_inventory"]["missing_bridge_count"]) == 3, "Unexpected bridge missing count")
    require(bridge["mask288_q12_seed_support3"]["status"] == "MASK288_Q12_PACKET_SEED_SUPPORT3_EXTENSION_BLOCKED_BY_PARITY", "Unexpected bridge support-3 seed status")
    require(int(bridge["mask288_q12_seed_support3"]["even_image_candidate_count"]) == 0, "Bridge support-3 seed should have zero even-image candidates")
    require(int(bridge["mask288_q12_seed_support3"]["compatible_doublet_count"]) == 0, "Bridge support-3 seed should have zero compatible doublets")
    require(bridge["one_sided_seed_correction"]["status"] == "MASK288_Q12_ONE_SIDED_SEED_CORRECTION_FINDS_NEW_RANK2_FAMILIES_PROJECTION_OPEN", "Unexpected bridge one-sided correction status")
    require(int(bridge["one_sided_seed_correction"]["compatible_doublet_count"]) == 4628, "Unexpected bridge one-sided compatible doublet count")
    require(int(bridge["one_sided_seed_correction"]["combined_rank2_support_family_count"]) == 28, "Unexpected bridge rank-2 family count")
    require(bridge["corrected_rank20_selection"]["status"] == "MASK288_Q12_CORRECTED_RANK20_SELECTION_BLOCKED_BY_RANK9_IMAGE_CEILING", "Unexpected bridge rank20 selection status")
    require(int(bridge["corrected_rank20_selection"]["combined_boundary_image_rank_over_Q"]) == 9, "Bridge rank ceiling should be 9")
    require(int(bridge["corrected_rank20_selection"]["target_rank"]) == 20, "Bridge target rank should be 20")
    require(int(bridge["corrected_rank20_selection"]["packet_rank_shortfall"]) == 11, "Bridge rank shortfall should be 11")
    require(bridge["natural_25_to_20_projection"]["status"] == "BOUNDARY_PACKET_NATURAL_25_TO_20_PROJECTION_REJECTED_BY_PACKET_SNF", "Unexpected natural packet projection status")
    require(bridge["natural_25_to_20_projection"]["columns_passing_packet_snf_image"] == [], "Natural packet projection should have no passing columns")
    require(bridge["hidden_q42_a985_capacity"]["matrix_unit_rank"] == 42, "Q42/A985 matrix-unit capacity rank mismatch")
    require(bridge["hidden_q42_a985_capacity"]["packet_target_excess"] == 22, "Q42/A985 packet target excess mismatch")
    require(report["sources"]["hydrogen_sandpile_golay_bridge_probe"] in {"generated\\d20_hydrogen_sandpile_golay_bridge_probe.json", "generated/d20_hydrogen_sandpile_golay_bridge_probe.json"}, "Missing bridge probe source")
    require(report["sources"]["pressure_atlas_js"] == "generated\\d20_black_hole_pressure_atlas_data.js" or report["sources"]["pressure_atlas_js"] == "generated/d20_black_hole_pressure_atlas_data.js", "Unexpected pressure atlas source")
    require(report["pressure_atlas_js_sha256"] == hashlib.sha256(ATLAS_JS.read_bytes()).hexdigest(), "Pressure atlas sha256 mismatch")
    pearson = float(report["correlation_summary"]["pearson_binding_absorption"])
    require(math.isfinite(pearson) and -1 <= pearson <= 1, "Pearson correlation out of range")
    mean_match = float(report["correlation_summary"]["mean_boundary_match"])
    require(0 <= mean_match <= 1, "Mean boundary match out of range")
    require("not a GR black-hole solution" in report["scope"], "Scope must avoid fake GR closure")
    notes = " ".join(report["physics_notes"])
    require(report["physics_notes"] and "pretty horizon ring alone is not evidence" in notes, "Missing falsification note")
    require("R33,K_mixed_S,K_pure_Sminus" in notes, "Missing C985 boundary-vector note")
    require("transition ledger" in notes, "Missing transition ledger note")
    require("pulse history" in notes, "Missing pulse-history browser note")
    require("paused-by-default requestAnimationFrame play loop" in notes, "Missing paused play-loop note")
    require("lag scan" in notes, "Missing lag scan note")
    require("719 null pulse histories" in notes, "Missing lag null-history note")
    require("inside the null distribution" in notes, "Missing null-failure note")
    require("signed C985 flux-balance" in notes, "Missing signed C985 flux note")
    require("signed C985 height-flux balance" in notes, "Missing signed C985 height-flux note")
    require("zero-pair Ward selector" in notes, "Missing zero-pair Ward note")
    require("height-flux observable is also inside the null distribution" in notes, "Missing height-flux null-failure note")
    require("mask-288 zero-pair Ward selector is also inside the null distribution" in notes, "Missing zero-pair Ward null-failure note")
    require("Ward-balanced 543-orbit dynamics" in notes, "Missing Ward-balanced dynamics note")
    require("C2 Markov orbit drift observable" in notes, "Missing C2 Markov orbit note")
    require("C2 selector-family observable" in notes, "Missing C2 selector-family note")
    require("boundary-only panel" in notes, "Missing boundary-only panel note")
    require("WebGL 3D orbit shell" in notes, "Missing WebGL 3D orbit shell note")
    require("fading transition trail" in notes, "Missing 3D transition trail note")
    require("C2 Markov trajectory observable" in notes, "Missing C2 Markov trajectory note")
    require("certified component representatives and transition samples" in notes, "Missing boundary sample note")
    require("Boundary-only motif counts" in notes, "Missing boundary motif-count note")
    require("Boundary motif prediction" in notes, "Missing boundary motif-prediction note")
    require("falsification ledger" in notes, "Missing falsification ledger note")
    motif_prediction = report["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction"]
    long_motif_prediction = report["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_long"]
    motif_splits = report["pressure_atlas_summary"]["boundary_dynamics_summary"]["motif_prediction_splits"]
    time_obstruction = motif_splits["time_offset_obstruction"]
    phase_clock = motif_splits["phase_clock_model"]
    paired_residual = phase_clock["paired_residual"]
    source_transport = motif_splits["source_state_transport"]
    source_conditioned = motif_splits["source_conditioned_ward_residual"]
    packet_bridge = report["boundary_packet_bridge_summary"]
    packet_family = report["rank_one_packet_family_sink_summary"]
    signed_packet = report["signed_rank_one_packet_quotient_summary"]
    signed_packet_lag = atlas["signed_packet_quotient_lag_summary"]
    support3 = atlas["support3_signed_quotient_summary"]
    support3_lag = atlas["support3_signed_quotient_lag_summary"]
    require(motif_prediction["transitions_evaluated"] == 15, "Unexpected motif-prediction transition count")
    require(motif_prediction["walk_forward_attempts"] >= 1, "Motif-prediction walk-forward test has no attempts")
    require(motif_prediction["best_variant"] in {"coarse", "component_inlet", "component_sector", "c985_charge", "source_atom", "source_atom_inlet"}, "Unexpected motif-prediction best variant")
    require(len(motif_prediction["variant_rows"]) == 6, "Missing motif-prediction alphabet family")
    require(0 <= motif_prediction["motif_accuracy"] <= 1, "Motif-prediction accuracy out of range")
    require(0 <= motif_prediction["baseline_accuracy"] <= 1, "Motif-prediction baseline accuracy out of range")
    require(0 <= motif_prediction["null_p_value"] <= 1, "Motif-prediction null p-value out of range")
    require(motif_prediction["verdict"] in {
        "INSUFFICIENT_MOTIF_HISTORY",
        "MOTIF_PREDICTOR_NOT_ABOVE_BASELINE",
        "MOTIF_PREDICTOR_ABOVE_ROTATION_NULL_PROVISIONAL",
        "MOTIF_PREDICTOR_WITHIN_ROTATION_NULL",
    }, "Unexpected motif-prediction verdict")
    require(long_motif_prediction["history_count"] > 1, "Long motif prediction did not extend beyond one history")
    require(long_motif_prediction["sample_count"] > 16, "Long motif prediction did not extend sample count")
    require(long_motif_prediction["walk_forward_attempts"] >= 32, "Long motif prediction has too few attempts")
    require(long_motif_prediction["best_variant"] in {"coarse", "component_inlet", "component_sector", "c985_charge", "source_atom", "source_atom_inlet"}, "Unexpected long motif best variant")
    require(len(long_motif_prediction["variant_rows"]) == 6, "Missing long motif alphabet family")
    require(0 <= long_motif_prediction["motif_accuracy"] <= 1, "Long motif accuracy out of range")
    require(0 <= long_motif_prediction["baseline_accuracy"] <= 1, "Long motif baseline accuracy out of range")
    require(0 <= long_motif_prediction["null_p_value"] <= 1, "Long motif null p-value out of range")
    require(long_motif_prediction["verdict"] in {
        "INSUFFICIENT_LONG_MOTIF_HISTORY",
        "LONG_MOTIF_PREDICTOR_NOT_ABOVE_BASELINE",
        "LONG_MOTIF_PREDICTOR_ABOVE_ROTATION_NULL",
        "LONG_MOTIF_PREDICTOR_ABOVE_ROTATION_NULL_PROVISIONAL",
        "LONG_MOTIF_PREDICTOR_WITHIN_ROTATION_NULL",
    }, "Unexpected long motif verdict")
    require(motif_splits["overall_verdict"] in {"SPLIT_MOTIF_SIGNAL_CANDIDATE", "SPLIT_MOTIF_SIGNAL_NOT_CERTIFIED"}, "Unexpected motif split overall verdict")
    for split_name in ("history_split", "time_offset_split"):
        split = motif_splits[split_name]
        require(split["walk_forward_attempts"] >= 32, f"{split_name} has too few attempts")
        require(split["best_variant"] in {"coarse", "component_inlet", "component_sector", "c985_charge", "source_atom", "source_atom_inlet"}, f"Unexpected {split_name} best variant")
        require(len(split["variant_rows"]) == 6, f"Missing {split_name} alphabet family")
        require(0 <= split["motif_accuracy"] <= 1, f"{split_name} accuracy out of range")
        require(0 <= split["baseline_accuracy"] <= 1, f"{split_name} baseline accuracy out of range")
        require(0 <= split["null_p_value"] <= 1, f"{split_name} null p-value out of range")
        require(split["verdict"] in {
            "INSUFFICIENT_SPLIT_MOTIF_HISTORY",
            "SPLIT_MOTIF_PREDICTOR_NOT_ABOVE_BASELINE",
            "SPLIT_MOTIF_PREDICTOR_ABOVE_ROTATION_NULL",
            "SPLIT_MOTIF_PREDICTOR_ABOVE_ROTATION_NULL_PROVISIONAL",
            "SPLIT_MOTIF_PREDICTOR_WITHIN_ROTATION_NULL",
        }, f"Unexpected {split_name} verdict")
    require(time_obstruction["phase_count"] == 15, "Unexpected time-offset obstruction phase count")
    require(time_obstruction["passing_phase_count"] + time_obstruction["failing_phase_count"] == time_obstruction["phase_count"], "Time-offset obstruction phase accounting mismatch")
    require(len(time_obstruction["phase_rows"]) == time_obstruction["phase_count"], "Missing time-offset phase rows")
    require(len(time_obstruction["weakest_rows"]) >= 1, "Missing weakest time-offset obstruction rows")
    require(time_obstruction["overall_verdict"] in {"TIME_OFFSET_OBSTRUCTION_LOCALIZED", "TIME_OFFSET_OBSTRUCTION_GLOBAL", "NO_TIME_OFFSET_OBSTRUCTION"}, "Unexpected time-offset obstruction verdict")
    for row in time_obstruction["phase_rows"]:
        require(0 <= row["motif_accuracy"] <= 1, "Phase motif accuracy out of range")
        require(0 <= row["baseline_accuracy"] <= 1, "Phase baseline accuracy out of range")
        require(0 <= row["null_p_value"] <= 1, "Phase null p-value out of range")
        require(row["verdict"] in {
            "PHASE_INSUFFICIENT_HISTORY",
            "PHASE_NOT_ABOVE_BASELINE",
            "PHASE_ABOVE_ROTATION_NULL",
            "PHASE_ABOVE_ROTATION_NULL_PROVISIONAL",
            "PHASE_WITHIN_ROTATION_NULL",
        }, "Unexpected phase obstruction verdict")
    require(phase_clock["overall_verdict"] in {"MOTIF_RESIDUAL_BEYOND_PHASE_CLOCK", "MOTIF_NOT_SEPARATED_FROM_PHASE_CLOCK"}, "Unexpected phase-clock overall verdict")
    require(phase_clock["clock_history_best_variant"] in {"clock_step", "clock_inlet", "clock_step_inlet", "clock_step_atom", "clock_step_atom_inlet"}, "Unexpected history phase-clock variant")
    require(phase_clock["clock_time_offset_best_variant"] in {"clock_step", "clock_inlet", "clock_step_inlet", "clock_step_atom", "clock_step_atom_inlet"}, "Unexpected time-offset phase-clock variant")
    require(len(phase_clock["clock_history_split"]["variant_rows"]) == 5, "Missing history phase-clock alphabet family")
    require(len(phase_clock["clock_time_offset_split"]["variant_rows"]) == 5, "Missing time-offset phase-clock alphabet family")
    require(0 <= phase_clock["clock_history_accuracy"] <= 1, "History phase-clock accuracy out of range")
    require(0 <= phase_clock["clock_time_offset_accuracy"] <= 1, "Time-offset phase-clock accuracy out of range")
    require(phase_clock["history_residual_verdict"] in {"MOTIF_ADDS_BEYOND_PHASE_CLOCK_HISTORY", "MOTIF_TIED_WITH_PHASE_CLOCK_HISTORY", "PHASE_CLOCK_DOMINATES_HISTORY"}, "Unexpected history residual verdict")
    require(phase_clock["time_offset_residual_verdict"] in {"MOTIF_ADDS_BEYOND_PHASE_CLOCK_TIME_OFFSET", "MOTIF_TIED_WITH_PHASE_CLOCK_TIME_OFFSET", "PHASE_CLOCK_DOMINATES_TIME_OFFSET"}, "Unexpected time-offset residual verdict")
    require(paired_residual["overall_verdict"] in {"PAIRED_MOTIF_RESIDUAL_BEYOND_CLOCK", "PAIRED_MOTIF_RESIDUAL_NOT_CERTIFIED"}, "Unexpected paired residual overall verdict")
    for split_name in ("history", "time_offset"):
        paired = paired_residual[split_name]
        require(paired["paired_attempts"] >= 32, f"{split_name} paired residual has too few attempts")
        require(paired["motif_only"] + paired["clock_only"] == paired["discordant_pairs"], f"{split_name} paired residual discordance mismatch")
        require(0 <= paired["motif_accuracy"] <= 1, f"{split_name} paired motif accuracy out of range")
        require(0 <= paired["clock_accuracy"] <= 1, f"{split_name} paired clock accuracy out of range")
        require(0 <= paired["motif_advantage_p"] <= 1, f"{split_name} paired p-value out of range")
        require(paired["verdict"] in {
            "PAIRED_RESIDUAL_INSUFFICIENT",
            "PAIRED_MOTIF_RESIDUAL_BEATS_CLOCK",
            "PAIRED_MOTIF_RESIDUAL_WEAK",
            "PAIRED_MOTIF_CLOCK_TIE",
            "PAIRED_CLOCK_DOMINATES_MOTIF",
        }, f"Unexpected {split_name} paired residual verdict")
    require(source_transport["overall_verdict"] in {"WARD_MOTIF_RESIDUAL_BEYOND_SOURCE_STATE", "SOURCE_STATE_TRANSPORT_DOMINATES_WARD_MOTIF"}, "Unexpected source-state transport verdict")
    require(len(source_transport["ward_history_split"]["variant_rows"]) == 4, "Missing Ward history motif family")
    require(len(source_transport["ward_time_offset_split"]["variant_rows"]) == 4, "Missing Ward time-offset motif family")
    require(len(source_transport["source_history_split"]["variant_rows"]) == 2, "Missing source-state history family")
    require(len(source_transport["source_time_offset_split"]["variant_rows"]) == 2, "Missing source-state time-offset family")
    require(source_transport["paired_ward_vs_source"]["history"]["paired_attempts"] >= 32, "Ward/source history paired residual has too few attempts")
    require(source_transport["paired_ward_vs_source"]["time_offset"]["paired_attempts"] >= 32, "Ward/source time-offset paired residual has too few attempts")
    for key in ("ward_history_split", "ward_time_offset_split", "source_history_split", "source_time_offset_split"):
        row = source_transport[key]
        require(0 <= row["motif_accuracy"] <= 1, f"{key} accuracy out of range")
        require(0 <= row["null_p_value"] <= 1, f"{key} null p-value out of range")
    require(source_conditioned["overall_verdict"] in {
        "SOURCE_CONDITIONED_WARD_RESIDUAL_CERTIFIED",
        "SOURCE_CONDITIONED_WARD_RESIDUAL_NOT_CERTIFIED",
    }, "Unexpected source-conditioned Ward residual verdict")
    for split_name in ("history_split", "time_offset_split"):
        split = source_conditioned[split_name]
        require(split["best_ward_variant"] in {"coarse", "component_inlet", "component_sector", "c985_charge"}, f"Unexpected {split_name} Ward variant")
        require(split["best_source_variant"] in {"source_atom", "source_atom_inlet"}, f"Unexpected {split_name} source variant")
        require(len(split["variant_rows"]) == 8, f"Missing {split_name} source-conditioned variant family")
        require(split["paired_attempts"] >= 32, f"{split_name} source-conditioned residual has too few attempts")
        require(split["ward_only"] + split["source_only"] == split["discordant_pairs"], f"{split_name} source-conditioned discordance mismatch")
        require(split["both_correct"] + split["both_wrong"] + split["discordant_pairs"] == split["paired_attempts"], f"{split_name} source-conditioned pair accounting mismatch")
        require(0 <= split["ward_accuracy"] <= 1, f"{split_name} Ward accuracy out of range")
        require(0 <= split["source_accuracy"] <= 1, f"{split_name} source accuracy out of range")
        require(-1 <= split["residual_lift"] <= 1, f"{split_name} residual lift out of range")
        require(split["null_trials"] >= 1, f"{split_name} missing source-conditioned null trials")
        require(0 <= split["null_p_value"] <= 1, f"{split_name} source-conditioned null p-value out of range")
        require(split["verdict"] in {
            "INSUFFICIENT_SOURCE_CONDITIONED_WARD_HISTORY",
            "SOURCE_CONDITIONED_WARD_NOT_ABOVE_SOURCE",
            "SOURCE_CONDITIONED_WARD_RESIDUAL_BEATS_NULL",
            "SOURCE_CONDITIONED_WARD_RESIDUAL_BEATS_NULL_PROVISIONAL",
            "SOURCE_CONDITIONED_WARD_WITHIN_NULL",
        }, f"Unexpected {split_name} source-conditioned verdict")
    require(packet_bridge["status"] == "BOUNDARY_PACKET_BRIDGE_SEAM_CERTIFIED_RECEIPTS", "Boundary-packet receipts are not certified")
    pairing = packet_bridge["pairing_obstruction"]
    row_norm = packet_bridge["row_normalization_obstruction"]
    low_support = packet_bridge["low_support_candidate_atlas"]
    require(pairing["all_checks_pass"], "Boundary-packet pairing receipt failed")
    require(pairing["raw_compatible_pairs"] == 0, "Raw public-atom pairing should have zero compatible pairs")
    require(pairing["raw_perfect_matching_exists"] is False, "Raw public-atom pairing should not have a perfect matching")
    require(pairing["minimal_scalar_with_matching"] == 6, "Packet bridge first matching scalar should be 6")
    require(pairing["joint_boundary_packet_scalar_lcm"] == 12, "Boundary/packet joint clearing bound should be 12")
    require(row_norm["all_checks_pass"], "Boundary-packet row-normalization receipt failed")
    require(row_norm["all_rows_require_even_scalar_by_parity"] is True, "Rows should require even scalar by parity")
    require(row_norm["row_scalar_divisibility_for_any_packet_pairing"] == 6, "Row normalization should not improve scalar 6")
    require(row_norm["only_compatible_residue_pair_mod6"] == [0, 0], "Only compatible even row residue should be (0,0) mod 6")
    require(row_norm["nonuniform_row_scaling_improves_on_scalar_6"] is False, "Nonuniform row scaling should not improve scalar 6")
    require(row_norm["tested_unordered_public_pair_count"] == 190, "Row-normalization test should cover 190 public pairs")
    require(low_support["all_checks_pass"], "Low-support packet candidate receipt failed")
    require(low_support["candidate_count"] == 800, "Low-support atlas should test 800 candidates")
    require(low_support["even_image_candidate_count"] == 12, "Low-support atlas should find 12 even-image rows")
    require(low_support["compatible_doublet_count"] == 6, "Low-support atlas should find 6 compatible doublets")
    require(low_support["compatible_doublets_all_rank_one"] is True, "Low-support compatible doublets should all be rank one")
    require(sorted(low_support["support_families"]) == [[0, 11], [6, 17], [14, 15]], "Unexpected low-support packet families")
    require(packet_family["families"] == low_support["support_families"], "Packet family test must use certified low-support families")
    require(packet_family["transition_steps"] == 16, "Packet family sink test must cover 16 transition steps")
    require(0 <= packet_family["sink_hit_rate"] <= 1, "Packet family sink hit rate out of range")
    require(0 <= packet_family["r33_sink_hit_rate"] <= 1, "Packet family R33 hit rate out of range")
    require(packet_family["sink_hits"] >= packet_family["r33_sink_hits"], "R33 packet hits cannot exceed packet sink hits")
    require(len(packet_family["by_family"]) == 3, "Packet family sink test must report three families")
    require(packet_family["verdict"] in {
        "PACKET_FAMILY_TOUCHES_R33_AND_RESIDUAL",
        "PACKET_FAMILY_TOUCHES_R33_AND_PROVISIONAL_RESIDUAL",
        "PACKET_FAMILY_TOUCHES_R33_WITHOUT_CERTIFIED_RESIDUAL",
        "PACKET_FAMILY_DOES_NOT_TOUCH_R33_SINK",
    }, "Unexpected packet family sink verdict")
    packet_residual = packet_family["source_conditioned_packet_residual"]
    require(packet_residual["families"] == packet_family["families"], "Packet residual families mismatch")
    require(packet_residual["overall_verdict"] in {
        "PACKET_FAMILY_WARD_RESIDUAL_CERTIFIED",
        "PACKET_FAMILY_WARD_RESIDUAL_PROVISIONAL",
        "PACKET_FAMILY_WARD_RESIDUAL_NOT_CERTIFIED",
    }, "Unexpected packet family residual verdict")
    for split_name in ("history_split", "time_offset_split"):
        split = packet_residual[split_name]
        require(split["actual_family_attempts"] >= 1, f"{split_name} packet family residual has no family overlap")
        require(split["paired_attempts"] >= split["actual_family_attempts"], f"{split_name} packet family attempts mismatch")
        require(split["ward_family_only"] + split["source_family_only"] == split["discordant_family_pairs"], f"{split_name} packet family discordance mismatch")
        require(split["both_family_correct"] + split["both_family_wrong"] + split["discordant_family_pairs"] == split["actual_family_attempts"], f"{split_name} packet family pair accounting mismatch")
        require(0 <= split["actual_family_rate"] <= 1, f"{split_name} packet family rate out of range")
        require(0 <= split["ward_family_accuracy"] <= 1, f"{split_name} packet family Ward accuracy out of range")
        require(0 <= split["source_family_accuracy"] <= 1, f"{split_name} packet family source accuracy out of range")
        require(-1 <= split["family_residual_lift"] <= 1, f"{split_name} packet family lift out of range")
        require(split["null_trials"] >= 1, f"{split_name} packet family null trials missing")
        require(0 <= split["null_p_value"] <= 1, f"{split_name} packet family p-value out of range")
        require(len(split["by_family"]) == 3, f"{split_name} packet family rows missing")
        require(split["verdict"] in {
            "PACKET_FAMILY_RESIDUAL_INSUFFICIENT_OVERLAP",
            "PACKET_FAMILY_WARD_NOT_ABOVE_SOURCE",
            "PACKET_FAMILY_WARD_RESIDUAL_BEATS_NULL",
            "PACKET_FAMILY_WARD_RESIDUAL_BEATS_NULL_PROVISIONAL",
            "PACKET_FAMILY_WARD_RESIDUAL_WITHIN_NULL",
        }, f"Unexpected {split_name} packet family residual verdict")
    require(signed_packet["candidate_count"] == 6, "Signed packet quotient must test six rank-one rows")
    require(len(signed_packet["candidate_rows"]) == 6, "Signed packet quotient rows missing")
    require(signed_packet["overall_verdict"] in {
        "SIGNED_PACKET_QUOTIENT_OBSERVABLE_CERTIFIED",
        "SIGNED_PACKET_QUOTIENT_OBSERVABLE_PROVISIONAL",
        "SIGNED_PACKET_QUOTIENT_OBSERVABLE_NOT_CERTIFIED",
    }, "Unexpected signed packet quotient overall verdict")
    require("per-inlet null pulse histories" in signed_packet["null_model"], "Signed packet quotient must use per-inlet null histories")
    signed_best = signed_packet["best_candidate"]
    require(signed_best["null_histories"] == 719, "Signed packet quotient must test 719 null histories")
    require(len(signed_best["support"]) == 2, "Signed packet quotient best support must have size two")
    require(len(signed_best["support_atoms"]) == 2, "Signed packet quotient best support atoms must have size two")
    require(0 <= signed_best["r33_touch_count"] <= 16, "Signed packet quotient R33 touch count out of range")
    require(0 <= signed_best["mean_abs_null_p"] <= 1, "Signed packet quotient mean p out of range")
    require(0 <= signed_best["peak_abs_null_p"] <= 1, "Signed packet quotient peak p out of range")
    require(signed_best["identity_mean_abs"] >= 0, "Signed packet quotient identity mean abs invalid")
    require(signed_best["identity_peak_abs"] >= 0, "Signed packet quotient identity peak abs invalid")
    require(signed_best["verdict"] in {
        "SIGNED_PACKET_QUOTIENT_TOUCHES_R33_AND_BEATS_NULL",
        "SIGNED_PACKET_QUOTIENT_TOUCHES_R33_PROVISIONAL",
        "SIGNED_PACKET_QUOTIENT_TOUCHES_R33_WITHIN_NULL",
        "SIGNED_PACKET_QUOTIENT_BEATS_NULL_WITHOUT_R33_TOUCH",
        "SIGNED_PACKET_QUOTIENT_WITHIN_NULL",
    }, "Unexpected signed packet quotient best verdict")
    for row in signed_packet["candidate_rows"]:
        require(len(row["support"]) == 2, "Every signed packet quotient row must have support size two")
        require(row["null_histories"] == 719, "Every signed packet quotient row must test 719 null histories")
        require(0 <= row["mean_abs_null_p"] <= 1, "Signed packet quotient row p out of range")
    require(signed_packet_lag["observable"] == "signed_rank_one_packet_quotient_hydrogen_lag", "Unexpected signed packet quotient lag observable")
    require(signed_packet_lag["best_signed_candidate"] == signed_best["left_candidate_id"], "Signed packet lag candidate must match boundary quotient candidate")
    require(signed_packet_lag["support_atoms"] == signed_best["support_atoms"], "Signed packet lag support atoms must match boundary quotient support")
    require(int(signed_packet_lag["lags"]) == 16, "Signed packet quotient lag scan must cover 16 cyclic offsets")
    require(len(signed_packet_lag["rows"]) == 16, "Signed packet quotient lag rows missing")
    require(len(signed_packet_lag["identity_signal"]) == 16, "Signed packet quotient identity signal must cover gate sequence")
    require(len(signed_packet_lag["signal_rows"]) == 16, "Signed packet quotient signal rows must cover gate sequence")
    require(0 <= int(signed_packet_lag["best_lag"]) < 16, "Signed packet quotient best lag out of range")
    require(math.isfinite(float(signed_packet_lag["best_rho"])) and -1 <= float(signed_packet_lag["best_rho"]) <= 1, "Signed packet quotient best rho out of range")
    signed_packet_lag_null = signed_packet_lag["null_significance"]
    require(int(signed_packet_lag_null["null_histories"]) == 719, "Signed packet quotient lag null test must cover 719 histories")
    require(0 <= float(signed_packet_lag_null["p_value"]) <= 1, "Signed packet quotient lag p-value out of range")
    require(signed_packet_lag_null["verdict"] in {"SIGNED_PACKET_QUOTIENT_HYDROGEN_BEATS_NULL_95", "SIGNED_PACKET_QUOTIENT_HYDROGEN_WITHIN_NULL"}, "Unexpected signed packet quotient lag null verdict")
    require(signed_packet_lag["verdict"] in {"SIGNED_PACKET_QUOTIENT_HYDROGEN_CANDIDATE", "SIGNED_PACKET_QUOTIENT_HYDROGEN_WITHIN_NULL"}, "Unexpected signed packet quotient hydrogen verdict")
    require(support3["observable"] == "support3_signed_public_boundary_quotient_screen", "Unexpected support-3 observable")
    require(support3["candidate_count"] == 4560, "Support-3 screen must enumerate canonical signed triples")
    require(support3["canonical_sign_convention"].startswith("first coefficient fixed"), "Support-3 screen must record sign quotient")
    require(support3["null_tested_candidate_count"] == 480, "Support-3 screen null-tested row count mismatch")
    require(support3["overall_verdict"] in {
        "SUPPORT3_SIGNED_QUOTIENT_OBSERVABLE_CERTIFIED",
        "SUPPORT3_SIGNED_QUOTIENT_OBSERVABLE_PROVISIONAL",
        "SUPPORT3_SIGNED_QUOTIENT_OBSERVABLE_NOT_CERTIFIED",
    }, "Unexpected support-3 overall verdict")
    support3_best = support3["best_candidate"]
    require(support3_best["support_size"] == 3, "Support-3 best row must have support size three")
    require(len(support3_best["support"]) == 3, "Support-3 best support rows missing")
    require(len(support3_best["support_atoms"]) == 3, "Support-3 support atoms missing")
    require(support3_best["null_histories"] == 719, "Support-3 best row must test 719 null histories")
    require(0 <= support3_best["r33_touch_count"] <= 16, "Support-3 R33 touch count out of range")
    require(0 <= support3_best["mean_abs_null_p"] <= 1, "Support-3 mean p out of range")
    require(0 <= support3_best["peak_abs_null_p"] <= 1, "Support-3 peak p out of range")
    require(support3_best["verdict"] in {
        "SUPPORT3_SIGNED_QUOTIENT_TOUCHES_R33_AND_BEATS_NULL",
        "SUPPORT3_SIGNED_QUOTIENT_BEATS_NULL_WITHOUT_R33_TOUCH",
        "SUPPORT3_SIGNED_QUOTIENT_TOUCHES_R33_WITHIN_NULL",
        "SUPPORT3_SIGNED_QUOTIENT_WITHIN_NULL",
    }, "Unexpected support-3 best verdict")
    require(len(support3["top_null_tested_rows"]) >= 1, "Support-3 screen needs top rows")
    require(all(row["support_size"] == 3 and row["null_histories"] == 719 for row in support3["top_null_tested_rows"]), "Support-3 top rows must be null-tested support-3 rows")
    require(support3_lag["observable"] == "support3_signed_public_boundary_quotient_hydrogen_lag", "Unexpected support-3 lag observable")
    require(support3_lag["best_candidate"] == support3_best["candidate_id"], "Support-3 lag candidate must match screen best")
    require(support3_lag["support_atoms"] == support3_best["support_atoms"], "Support-3 lag support atoms must match screen best")
    require(int(support3_lag["lags"]) == 16, "Support-3 lag scan must cover 16 cyclic offsets")
    require(len(support3_lag["rows"]) == 16, "Support-3 lag rows missing")
    require(len(support3_lag["identity_signal"]) == 16, "Support-3 identity signal must cover gate sequence")
    require(len(support3_lag["signal_rows"]) == 16, "Support-3 signal rows must cover gate sequence")
    require(0 <= int(support3_lag["best_lag"]) < 16, "Support-3 best lag out of range")
    require(math.isfinite(float(support3_lag["best_rho"])) and -1 <= float(support3_lag["best_rho"]) <= 1, "Support-3 best rho out of range")
    support3_lag_null = support3_lag["null_significance"]
    require(int(support3_lag_null["null_histories"]) == 719, "Support-3 lag null test must cover 719 histories")
    require(0 <= float(support3_lag_null["p_value"]) <= 1, "Support-3 lag p-value out of range")
    require(support3_lag_null["verdict"] in {"SUPPORT3_SIGNED_QUOTIENT_HYDROGEN_BEATS_NULL_95", "SUPPORT3_SIGNED_QUOTIENT_HYDROGEN_WITHIN_NULL"}, "Unexpected support-3 lag null verdict")
    require(support3_lag["verdict"] in {"SUPPORT3_SIGNED_QUOTIENT_HYDROGEN_CANDIDATE", "SUPPORT3_SIGNED_QUOTIENT_HYDROGEN_WITHIN_NULL"}, "Unexpected support-3 hydrogen verdict")
    require("# D20 boundary physics discovery notes" in boundary_notes, "Missing boundary notes title")
    require(ledger["overall_status"] in boundary_notes, "Missing falsification status in boundary notes")
    require("D=d20=Lambda^3 H6" in boundary_notes, "Missing public-shell invariant in boundary notes")
    require("alpha*=1/137" in boundary_notes, "Missing alpha invariant in boundary notes")
    require("R33_global(mask)" in boundary_notes, "Missing C985 R33 rule in boundary notes")
    require("Top motifs" in boundary_notes, "Missing motif notebook in boundary notes")
    require("Boundary motif prediction test" in boundary_notes, "Missing motif prediction test in boundary notes")
    require("walk-forward motif-to-next-R33-sink" in boundary_notes, "Missing walk-forward motif prediction detail")
    require("Best motif alphabet" in boundary_notes and "Alphabet family" in boundary_notes, "Missing motif alphabet family detail")
    require("Long boundary motif forecast" in boundary_notes, "Missing long boundary motif forecast notes")
    require("identity plus certified null-row pulse histories" in boundary_notes, "Missing long motif witness detail")
    require("Held-out motif forecast splits" in boundary_notes, "Missing held-out motif split notes")
    require("History split verdict" in boundary_notes and "Time-offset split verdict" in boundary_notes, "Missing split verdict details")
    require("Time-offset obstruction phase audit" in boundary_notes, "Missing time-offset obstruction phase audit")
    require("Weakest held-out phases" in boundary_notes, "Missing weakest phase details")
    require("Explicit phase-clock baseline" in boundary_notes, "Missing explicit phase-clock notes")
    require("History residual lift" in boundary_notes and "Time-offset residual lift" in boundary_notes, "Missing phase-clock residual details")
    require("Paired phase-residual observable" in boundary_notes, "Missing paired phase-residual notes")
    require("motif_only" in boundary_notes and "clock_only" in boundary_notes, "Missing paired residual win/loss details")
    require("Source-state transport separation" in boundary_notes, "Missing source-state transport notes")
    require("Ward-minus-source" in boundary_notes, "Missing Ward/source residual details")
    require("Source-conditioned Ward residual" in boundary_notes, "Missing source-conditioned Ward residual notes")
    require("within-source rotations of Ward/C985 keys" in boundary_notes, "Missing source-conditioned null model")
    require("C985 boundary-packet bridge seam" in boundary_notes, "Missing boundary-packet bridge seam notes")
    require("compatible raw pairs=0" in boundary_notes, "Missing raw pairing obstruction details")
    require("all rank-one=True" in boundary_notes, "Missing rank-one low-support packet detail")
    require("Rank-one packet families against R33/source residual" in boundary_notes, "Missing rank-one packet family residual notes")
    require("Packet-family history residual" in boundary_notes, "Missing packet family history residual details")
    require("Signed rank-one packet quotient observable" in boundary_notes, "Missing signed packet quotient notes")
    require("identity mean |quotient|" in boundary_notes, "Missing signed packet quotient null details")
    require("Signed packet quotient hydrogen-lag test" in boundary_notes, "Missing signed packet quotient hydrogen-lag notes")
    require("Best hydrogen lag" in boundary_notes, "Missing signed packet quotient hydrogen-lag detail")
    require("Support-3 signed quotient screen" in boundary_notes, "Missing support-3 signed quotient notes")
    require("null-tested top rows" in boundary_notes, "Missing support-3 null-tested row detail")
    require("A985/q12 packet projection bridge probe" in boundary_notes, "Missing A985/q12 bridge probe notes")
    require("boundary image rank=9/20" in boundary_notes, "Missing bridge rank ceiling detail")
    require("one-sided seed correction" in boundary_notes, "Missing bridge one-sided correction detail")
    require("Q42/A985 capacity" in boundary_notes, "Missing Q42/A985 bridge capacity detail")
    require("source-conditioned Ward residual" in boundary_notes, "Missing next source-conditioned Ward residual target")
    require("source-state transport control currently dominates Ward/C985 motif alphabets" in notes, "Missing source-state dominance physics note")
    require("rotates only Ward/C985 keys inside each source class" in notes, "Missing source-conditioned physics note")
    require("rule out raw public-atom pairing and diagonal row normalization" in notes, "Missing boundary-packet obstruction physics note")
    require("rank-one packet family test compares those support-2 families" in notes, "Missing rank-one packet family physics note")
    require("signed rank-one packet quotient test uses the actual signed support-2 rows" in notes, "Missing signed packet quotient physics note")
    require("signed packet quotient is separately tested as a hydrogen-lag observable" in notes, "Missing signed packet quotient hydrogen-lag physics note")
    require("support-3 signed quotient screen enumerates canonical public-atom triples" in notes, "Missing support-3 signed quotient physics note")
    require("A985/q12 packet bridge probe confirms the projection gap" in notes, "Missing A985/q12 bridge physics note")
    require("choosing the correct packet kernel/label map" in notes, "Missing packet kernel/label physics note")
    require("non-diagonal signed quotient or normalization" in notes, "Missing non-diagonal bridge physics note")
    require("not a GR black-hole solution" in boundary_notes, "Boundary notes must avoid fake GR closure")
    print("D20 black-hole atom lab report validated")


if __name__ == "__main__":
    main()
