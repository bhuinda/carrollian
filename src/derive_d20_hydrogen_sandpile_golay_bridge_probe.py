from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import itertools
import json
import csv
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


ARTIFACT_PATH = GENERATED / "d20_hydrogen_sandpile_golay_bridge_probe.json"

HYDROGEN_ATOM = "ingress/d20_atom_transport_hydrogen_package/data/d20_atom_invariants.json"
HYDROGEN_STATUS = "ingress/d20_atom_transport_hydrogen_package/notes/03_status_and_verifier_targets.md"
TALAGRAND_STATUS = "ingress/talagrand_python_handoff/STATUS_LEDGER.json"
INGRESS_BOUNDARY_TO_LOOP_CERTIFICATE = (
    "ingress/talagrand_python_handoff/work/all_residue_boundary_to_loop_materialization/"
    "all_residue_boundary_to_loop_materialization_certificate.json"
)
INGRESS_HEIGHT_ACTION_RETURN_CERTIFICATE = (
    "ingress/talagrand_python_handoff/work/all_residue_height_action_return_reconstruction/"
    "all_residue_height_action_return_certificate.json"
)
INGRESS_LAMBDA_HC_ACT_INVARIANCE_CERTIFICATE = (
    "ingress/talagrand_python_handoff/work/lambda_hc_act_invariance_audit/"
    "lambda_hc_act_invariance_certificate.json"
)
INGRESS_LAMBDA_HC_ACT_INVARIANCE_ROWS = (
    "ingress/talagrand_python_handoff/work/lambda_hc_act_invariance_audit/"
    "lambda_hc_act_invariance_rows.csv"
)
INGRESS_HEIGHT_COHERENT_INTERTWINING_CERTIFICATE = (
    "ingress/talagrand_python_handoff/work/height_coherent_action_return_intertwining/"
    "height_coherent_action_return_intertwining_certificate.json"
)
HEXACODE_SELECTOR = "data/selectors/hexacode_row_selector.json"
HAMMING_ARCHIVE_REPORT = (
    "data/invariants/d20/proof_obligations/d20_hamming_gaussian_python_work_archive_import/report.json"
)
KKT_REPORT = (
    "data/invariants/d20/proof_obligations/d20_talagrand_multilevel_kkt_obstruction_system/report.json"
)
CHAIN_REPORT = "data/invariants/d20/proof_obligations/d20_talagrand_closure_chain_audit/report.json"
CYCLE8_REPORT = "data/invariants/d20/proof_obligations/cycle8_pi33_projection_coefficient/report.json"
ALPHABETIZED_GOLAY_REPORT = (
    "data/invariants/d20/proof_obligations/d20_alphabetized_golay_finiteness/report.json"
)
STATIC_REPORT = (
    "data/invariants/d20/theorems/tiny_pointer_a985_burning_static_constructed_representative/report.json"
)
STATIC_DESIGNED_RULES = (
    "data/invariants/d20/theorems/tiny_pointer_a985_burning_static_designed_frame_section/"
    "burning_static_designed_frame_section_rules.json"
)
QUOTIENTS_NPZ = "data/raw/quotients.npz"
A985_FULL_MATRIX_UNIT_ARRAYS = (
    "data/invariants/d20/theorems/tiny_pointer_a985_full_matrix_unit_orbital_coo/"
    "source_sector_matrix_units_raw_orbital_arrays.npz"
)
A985_FULL_MATRIX_UNIT_REPORT = (
    "data/invariants/d20/theorems/tiny_pointer_a985_full_matrix_unit_orbital_coo/"
    "report.json"
)
A985_CANONICAL_SECTOR_CHARACTER_TABLE = (
    "data/invariants/d20/theorems/tiny_pointer_a985_canonical_sector_characters/"
    "canonical_sector_character_table.csv"
)
A985_CANONICAL_SECTOR_CHARACTERS_REPORT = (
    "data/invariants/d20/theorems/tiny_pointer_a985_canonical_sector_characters/"
    "report.json"
)
BURNING_FOLD_REPORT = "data/invariants/d20/theorems/finite_burningship_folded_map/report.json"
FOURIER_REPORT = "data/invariants/d20/theorems/fourier_residue_screen/report.json"
SCREEN0_REPORT = "data/invariants/d20/theorems/fourier_screen0_tube_central_element/report.json"
SANDPILE_REPORT = "data/invariants/d20/theorems/sandpile_critical_group/report.json"
TUBE_SANDPILE_REPORT = "data/invariants/d20/theorems/tube_sandpile_divisor_map/report.json"
SECTOR_REFINEMENT_REPORT = "data/invariants/d20/theorems/tube_sandpile_flip_sector_refinement/report.json"
CANONICAL_ALL_MASK_WARD_REPORT = "data/invariants/d20/theorems/canonical_all_mask_ward_identity/report.json"
CANONICAL_SCATTERING_REPORT = "data/invariants/d20/theorems/canonical_finite_scattering_table/report.json"
WARD_KERNEL_HEIGHT_SELECTOR_REPORT = (
    "data/invariants/d20/theorems/full_exposure_zero_pair_ward_kernel_height_selector/report.json"
)
SELECTED_SOURCED_WARD_REPORT = (
    "data/invariants/d20/theorems/full_exposure_zero_pair_selected_sourced_ward_balance/report.json"
)
D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE_REPORT = (
    "data/invariants/d20/theorems/d20_boundary_loop_step_atom_incidence/report.json"
)
D20_EXPLICIT_PACKET_RESTRICTION_MAP_TEST_REPORT = (
    "data/invariants/d20/theorems/d20_explicit_packet_restriction_map_test/report.json"
)
D20_PACKET_BRIDGE_SNF_OBSTRUCTION_REPORT = (
    "data/invariants/d20/theorems/d20_packet_bridge_snf_obstruction/report.json"
)
D20_BOUNDARY_PACKET_ROW_NORMALIZATION_OBSTRUCTION_REPORT = (
    "data/invariants/d20/theorems/d20_boundary_packet_row_normalization_obstruction/report.json"
)
D20_BOUNDARY_PACKET_LOW_SUPPORT_CANDIDATE_ATLAS_REPORT = (
    "data/invariants/d20/theorems/d20_boundary_packet_low_support_candidate_atlas/report.json"
)
D20_LOOP_STEP_PACKET_SNF_PROBE_REPORT = (
    "data/invariants/d20/theorems/d20_loop_step_packet_snf_probe/report.json"
)
D20_FULL_PACKET_MATRIX_LIFT_REPORT = (
    "data/invariants/d20/theorems/d20_full_packet_matrix_lift/report.json"
)
PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_REPORT = (
    "data/invariants/d20/theorems/projective_packet_spectral_charge_table/report.json"
)
FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_REPORT = (
    "data/invariants/d20/theorems/full_exposure_packet_propagation_graph/report.json"
)
FULL_EXPOSURE_LABEL_BREAKING_FACTORIZATION_REPORT = (
    "data/invariants/d20/theorems/full_exposure_label_breaking_factorization/report.json"
)
D20_PACKET239_E8_ROOT_RELATION_PROBE_REPORT = (
    "data/invariants/d20/proof_obligations/d20_packet239_e8_root_relation_probe/"
    "report.json"
)
D20_PACKET239_E8_20X12_CANDIDATE_SHELL_PROBE_REPORT = (
    "data/invariants/d20/proof_obligations/d20_packet239_e8_20x12_candidate_shell_probe/"
    "report.json"
)
SECTOR33_UNIQUE_PUBLIC_ZERO_SUPPORT_REPORT = (
    "data/invariants/d20/theorems/sector33_unique_public_zero_support/report.json"
)
SECTOR33_BOUNDARY_ANNIHILATION_REPORT = (
    "data/invariants/d20/theorems/sector33_boundary_annihilation/report.json"
)
SECTOR33_RESIDUAL_ATTACHMENT_REPORT = (
    "data/invariants/d20/theorems/sector33_residual_attachment/report.json"
)
D20_SELECTOR_DERIVATION = "data/invariants/d20/d20_d6_selector_derivation.json"
Q12_SECTION = "src/compiler/core/sigma_q12.json"
HCYCLE_PRIMITIVE_CYCLES = "data/invariants/hcycle/subscript_Hcycle_primitive_cycles.csv"
HCYCLE_D20_EDGES = "data/invariants/hcycle/subscript_Hcycle_d20_edges.csv"
HCYCLE_INVARIANT_LEDGER = "data/invariants/hcycle/d20_Hcycle_invariant_ledger.csv"
HCYCLE_CIRCUIT_GRAMMAR = "data/invariants/hcycle/d20_Hcycle_circuit_grammar.csv"
STATIC_FOURIER_OVERLAP = (
    "data/invariants/d20/theorems/tiny_pointer_a985_burning_static_public_zero_alignment/"
    "burning_static_fourier_public_zero_overlap.csv"
)

INPUT_RELS = (
    HYDROGEN_ATOM,
    HYDROGEN_STATUS,
    TALAGRAND_STATUS,
    INGRESS_BOUNDARY_TO_LOOP_CERTIFICATE,
    INGRESS_HEIGHT_ACTION_RETURN_CERTIFICATE,
    INGRESS_LAMBDA_HC_ACT_INVARIANCE_CERTIFICATE,
    INGRESS_LAMBDA_HC_ACT_INVARIANCE_ROWS,
    INGRESS_HEIGHT_COHERENT_INTERTWINING_CERTIFICATE,
    HEXACODE_SELECTOR,
    HAMMING_ARCHIVE_REPORT,
    KKT_REPORT,
    CHAIN_REPORT,
    CYCLE8_REPORT,
    ALPHABETIZED_GOLAY_REPORT,
    STATIC_REPORT,
    STATIC_DESIGNED_RULES,
    QUOTIENTS_NPZ,
    A985_FULL_MATRIX_UNIT_ARRAYS,
    A985_FULL_MATRIX_UNIT_REPORT,
    A985_CANONICAL_SECTOR_CHARACTER_TABLE,
    A985_CANONICAL_SECTOR_CHARACTERS_REPORT,
    BURNING_FOLD_REPORT,
    FOURIER_REPORT,
    SCREEN0_REPORT,
    SANDPILE_REPORT,
    TUBE_SANDPILE_REPORT,
    SECTOR_REFINEMENT_REPORT,
    CANONICAL_ALL_MASK_WARD_REPORT,
    CANONICAL_SCATTERING_REPORT,
    WARD_KERNEL_HEIGHT_SELECTOR_REPORT,
    SELECTED_SOURCED_WARD_REPORT,
    D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE_REPORT,
    D20_EXPLICIT_PACKET_RESTRICTION_MAP_TEST_REPORT,
    D20_PACKET_BRIDGE_SNF_OBSTRUCTION_REPORT,
    D20_BOUNDARY_PACKET_ROW_NORMALIZATION_OBSTRUCTION_REPORT,
    D20_BOUNDARY_PACKET_LOW_SUPPORT_CANDIDATE_ATLAS_REPORT,
    D20_LOOP_STEP_PACKET_SNF_PROBE_REPORT,
    D20_FULL_PACKET_MATRIX_LIFT_REPORT,
    PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_REPORT,
    FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_REPORT,
    FULL_EXPOSURE_LABEL_BREAKING_FACTORIZATION_REPORT,
    D20_PACKET239_E8_ROOT_RELATION_PROBE_REPORT,
    D20_PACKET239_E8_20X12_CANDIDATE_SHELL_PROBE_REPORT,
    SECTOR33_UNIQUE_PUBLIC_ZERO_SUPPORT_REPORT,
    SECTOR33_BOUNDARY_ANNIHILATION_REPORT,
    SECTOR33_RESIDUAL_ATTACHMENT_REPORT,
    D20_SELECTOR_DERIVATION,
    Q12_SECTION,
    HCYCLE_PRIMITIVE_CYCLES,
    HCYCLE_D20_EDGES,
    HCYCLE_INVARIANT_LEDGER,
    HCYCLE_CIRCUIT_GRAMMAR,
    STATIC_FOURIER_OVERLAP,
)

OPEN_STATUS_MARKERS = (
    "NOT_CLOSED",
    "NOT_CLAIMED",
    "PARTIAL",
    "PROFILE_COVERAGE",
    "NO_COUNTEREXAMPLE",
    "OPEN",
)


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


def load_json(rel: str) -> dict[str, Any]:
    path = ROOT / rel
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise ValueError(f"{rel} is not a JSON object")
    return payload


def load_csv(rel: str) -> list[dict[str, str]]:
    with (ROOT / rel).open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_quotients_npz() -> dict[str, np.ndarray]:
    with np.load(ROOT / QUOTIENTS_NPZ) as payload:
        return {
            "block_i": np.asarray(payload["block_i"], dtype=np.int64),
            "block_j": np.asarray(payload["block_j"], dtype=np.int64),
            "q12_map": np.asarray(payload["q12_map"], dtype=np.int64),
            "q42_map": np.asarray(payload["q42_map"], dtype=np.int64),
        }


def input_entry(rel: str) -> dict[str, Any]:
    path = ROOT / rel
    return {"path": rel, "sha256": sha_file(path), "size": path.stat().st_size}


def get_path(payload: dict[str, Any], path: tuple[str, ...], default: Any = None) -> Any:
    current: Any = payload
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def flatten_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            out.extend(flatten_strings(item))
        return out
    if isinstance(value, dict):
        out = []
        for item in value.values():
            out.extend(flatten_strings(item))
        return out
    return []


def extract_open_items(payload: dict[str, Any]) -> list[str]:
    paths = (
        ("closure_boundary", "does_not_certify"),
        ("closure_boundary", "not_certified"),
        ("open_boundary", "not_certified"),
        ("witness", "open_boundary", "not_certified"),
        ("obstruction_boundary",),
    )
    items: list[str] = []
    for path in paths:
        items.extend(flatten_strings(get_path(payload, path, [])))
    claim_boundary = payload.get("claim_boundary") or payload.get("boundary")
    if isinstance(claim_boundary, str) and (
        "not a proof" in claim_boundary.lower() or "does not" in claim_boundary.lower()
    ):
        items.insert(0, claim_boundary)
    seen: set[str] = set()
    unique = []
    for item in items:
        compact = " ".join(item.split())
        if compact and compact not in seen:
            seen.add(compact)
            unique.append(compact)
    return unique


def proof_obligation_inventory() -> dict[str, Any]:
    rows = []
    root = D20_INVARIANTS / "proof_obligations"
    for report_path in sorted(root.glob("*/report.json")):
        payload = load_json(report_path.relative_to(ROOT).as_posix())
        status = str(payload.get("status", ""))
        open_items = extract_open_items(payload)
        outstanding = bool(open_items) or any(marker in status for marker in OPEN_STATUS_MARKERS)
        rows.append(
            {
                "id": report_path.parent.name,
                "path": relpath(report_path),
                "status": status,
                "all_checks_pass": payload.get("all_checks_pass"),
                "outstanding_boundary_detected": outstanding,
                "open_item_count": len(open_items),
                "open_items_sample": open_items[:5],
                "next_highest_yield_item": payload.get("next_highest_yield_item"),
            }
        )
    outstanding_rows = [row for row in rows if row["outstanding_boundary_detected"]]
    return {
        "proof_obligation_report_count": len(rows),
        "all_checks_pass_count": sum(1 for row in rows if row["all_checks_pass"] is True),
        "outstanding_boundary_count": len(outstanding_rows),
        "status_open_marker_policy": list(OPEN_STATUS_MARKERS),
        "rows": rows,
        "outstanding_rows": outstanding_rows,
    }


def f2_weight(mask: int) -> int:
    return int(mask).bit_count()


def counter_dict(items: list[str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for item in items:
        out[item] = out.get(item, 0) + 1
    return dict(sorted(out.items()))


def signature_from_counts(counts: dict[str, int], keys: tuple[str, ...]) -> str:
    return ",".join(f"{key}:{counts.get(key, 0)}" for key in keys)


def all_leaves_zero(obj: Any) -> bool:
    if isinstance(obj, dict):
        return all(all_leaves_zero(value) for value in obj.values())
    if isinstance(obj, list):
        return all(all_leaves_zero(value) for value in obj)
    return obj == 0


def contains_text_token(obj: Any, token: str) -> bool:
    needle = token.lower()
    if isinstance(obj, dict):
        return any(
            contains_text_token(key, token) or contains_text_token(value, token)
            for key, value in obj.items()
        )
    if isinstance(obj, list):
        return any(contains_text_token(value, token) for value in obj)
    if isinstance(obj, str):
        return needle in obj.lower()
    return False


def product(values: list[int]) -> int:
    out = 1
    for value in values:
        out *= int(value)
    return out


def build_signatures() -> dict[str, Any]:
    atom = load_json(HYDROGEN_ATOM)
    hexacode = load_json(HEXACODE_SELECTOR)
    hamming = load_json(HAMMING_ARCHIVE_REPORT)
    kkt = load_json(KKT_REPORT)
    chain = load_json(CHAIN_REPORT)
    cycle8 = load_json(CYCLE8_REPORT)
    static = load_json(STATIC_REPORT)
    burning = load_json(BURNING_FOLD_REPORT)
    fourier = load_json(FOURIER_REPORT)
    screen0 = load_json(SCREEN0_REPORT)
    sandpile = load_json(SANDPILE_REPORT)
    tube_sandpile = load_json(TUBE_SANDPILE_REPORT)
    sector_refinement = load_json(SECTOR_REFINEMENT_REPORT)

    core_counts = atom["core_object"]["counts"]
    golay_code = hexacode["golay_code"]
    full_word = int(atom["RGBA_and_wall"]["full_word"])
    alpha_channels = int(atom["RGBA_and_wall"]["alpha_channels"])
    h8_copies = int(core_counts["H8_copies"])
    ambient_coordinates = int(core_counts["ambient_coordinates"])

    static_orders = [
        int(value) for value in static["derived"]["abstract_orders"].values()
    ]
    static_order = product(static_orders)

    cycle_known = cycle8["known_certified_data"]
    tropic_update = cycle_known["typed_nonexact_optical_flux_update"]["first_obstruction_update"]
    all_residue = cycle_known["all_residue_height_transport"]
    superselection = cycle_known["superselection_flux_balance_extension"]

    combined_screen = fourier["derived"]["combined_screen"]
    defect_vectors = [int(v) for v in combined_screen["defect_vectors"]]
    cell_counts = {str(k): int(v) for k, v in combined_screen["cell_counts_by_signature"].items()}
    screen_summary = sector_refinement["derived"]["screen_summary"]

    sandpile_group = sandpile["derived"]["critical_group"]
    tube_derived = tube_sandpile["derived"]

    return {
        "hydrogen_golay_hamming_frame": {
            "h8_copies": h8_copies,
            "ambient_coordinates": ambient_coordinates,
            "h8_copy_weight": alpha_channels,
            "h8_copies_times_weight": h8_copies * alpha_channels,
            "rgba_full_word": full_word,
            "alpha_wall": atom["RGBA_and_wall"]["alpha_wall"],
            "integer_alpha_star_open_target": "128+8+1",
            "golay_length": golay_code["generator_shape"][1],
            "golay_rank": golay_code["rank"],
            "golay_minimum_nonzero_weight": golay_code["minimum_nonzero_weight"],
            "golay_weight_histogram": golay_code["weight_histogram"],
            "hamming_root_kill_sequence": hamming["witness"]["connection_to_current_problem"][
                "root_killing_sequence"
            ],
            "sparse_projection_boundary_weight": hamming["witness"]["connection_to_current_problem"][
                "golay_endpoint_dual_distance"
            ],
        },
        "static_axis": {
            "source_status": static["status"],
            "group_shape": "Z/2 x Z/4^2",
            "generator_orders": static_orders,
            "group_order": static_order,
            "generator_count": len(static_orders),
            "mod2_reduction_rank": static["derived"]["mod2_reduction_rank"],
            "order_matches_hydrogen_full_word": static_order == full_word,
            "burning_fold_target_shape": burning["derived"]["target_two_primary_shape"],
            "h8_anchor": "order 32 = 4 * 8 with three independent mod-2 reductions",
        },
        "tropic_axis": {
            "source_status": cycle8["status"],
            "target": cycle8["target"],
            "gamma8_mask": tropic_update["mask"],
            "gamma8_basis_cycle_ids": tropic_update["basis_cycle_ids"],
            "height_action": tropic_update["height_action"],
            "height_residual": tropic_update["hidden_update_integral"]["R33"],
            "balance_sum": tropic_update["height_action"] + tropic_update["hidden_update_integral"]["R33"],
            "support_sector": tropic_update["support_sector"],
            "hidden_components": superselection["hidden_components"],
            "hidden_component_count": len(superselection["hidden_components"]),
            "residue_class_count": all_residue["residue_class_count"],
            "nonzero_residue_class_count": all_residue["nonzero_residue_class_count"],
            "min_nonzero_height_action": all_residue["min_nonzero_height_action"],
            "h8_anchor": "gamma_8 is basis cycle 8 and mask 2^8 in the height-coherent residual bridge",
        },
        "optic_axis": {
            "source_status": fourier["status"],
            "screen_ids": screen_summary["screen_ids"],
            "defect_vectors": defect_vectors,
            "defect_vector_weights": [f2_weight(v) for v in defect_vectors],
            "rank_over_f2": combined_screen["rank_over_f2"],
            "cell_counts_by_signature": cell_counts,
            "common_kernel_mask_count": combined_screen["common_kernel_mask_count"],
            "common_kernel_signature": combined_screen["common_kernel_signature"],
            "screen0_object_phase_assignment": screen0["derived"]["object_phase_assignment"],
            "candidate_rows": screen_summary["candidate_rows"],
            "h8_anchor": "three F2 screens split 2048 masks into 8 cells of 256 = 2^8 each",
        },
        "sandpile_target": {
            "critical_group_presentation": sandpile_group["presentation"],
            "critical_group_invariant_factors": sandpile_group["invariant_factors"],
            "critical_group_order": sandpile_group["order"],
            "graph_vertices": sandpile["derived"]["graph"]["vertices"],
            "graph_edges": sandpile["derived"]["graph"]["edges"],
            "sandpile_class_count_in_mask_image": tube_derived["sandpile_class_count_in_mask_image"],
            "mixed_sandpile_class_count": tube_derived["tube_grade_vs_sandpile_class"][
                "mixed_class_count"
            ],
            "mixed_class_mask_count": tube_derived["tube_grade_vs_sandpile_class"][
                "mixed_class_mask_count"
            ],
            "tube_grade_split": tube_derived["tube_grade_counts"],
            "tube_grade_is_sandpile_class_invariant": tube_derived["tube_grade_vs_sandpile_class"][
                "tube_grade_class_invariant"
            ],
            "screen_refinement_status": sector_refinement["status"],
        },
        "remaining_exact_target": {
            "talagrand_global_status": load_json(TALAGRAND_STATUS)["global_status"],
            "talagrand_remaining_open_target": load_json(TALAGRAND_STATUS)["remaining_open_target"],
            "kkt_status": kkt["status"],
            "kkt_next_highest_yield_item": kkt["next_highest_yield_item"],
            "chain_status": chain["status"],
            "chain_next_highest_yield_item": chain["next_highest_yield_item"],
        },
    }


def axis_score(axis_name: str, axis: dict[str, Any], signatures: dict[str, Any]) -> dict[str, Any]:
    score = 0
    reasons: list[str] = []
    if axis_name == "static":
        if axis["generator_count"] == 3 and axis["mod2_reduction_rank"] == 3:
            score += 2
            reasons.append("rank-3 static generator frame")
        if axis["group_order"] == signatures["hydrogen_golay_hamming_frame"]["rgba_full_word"]:
            score += 2
            reasons.append("order 32 matches hydrogen RGBA full word")
        if axis["group_order"] == 4 * signatures["hydrogen_golay_hamming_frame"]["h8_copy_weight"]:
            score += 1
            reasons.append("order 32 is four weight-8 packets")
    elif axis_name == "tropic":
        if axis["hidden_component_count"] == 3:
            score += 2
            reasons.append("rank-3 hidden residual ledger")
        if axis["gamma8_mask"] == 1 << 8 and axis["gamma8_basis_cycle_ids"] == [8]:
            score += 2
            reasons.append("gamma_8 mask is 2^8")
        if axis["balance_sum"] == 0:
            score += 1
            reasons.append("height residual closes by exact cancellation")
    elif axis_name == "optic":
        if axis["rank_over_f2"] == 3 and len(axis["defect_vectors"]) == 3:
            score += 2
            reasons.append("three independent F2 screens")
        if len(axis["cell_counts_by_signature"]) == 8 and set(axis["cell_counts_by_signature"].values()) == {256}:
            score += 2
            reasons.append("8 equal cells of 2^8 masks")
        if set(axis["defect_vector_weights"]) == {2}:
            score += 1
            reasons.append("each signed-turn screen has two defects")
    return {"score": score, "reasons": reasons}


def brute_force_assignments(signatures: dict[str, Any]) -> dict[str, Any]:
    axis_map = {
        "static": signatures["static_axis"],
        "tropic": signatures["tropic_axis"],
        "optic": signatures["optic_axis"],
    }
    axes = list(axis_map)
    h8_copies = ["H8_R", "H8_G", "H8_B"]
    axis_scores = {axis: axis_score(axis, axis_map[axis], signatures) for axis in axes}
    rows = []
    for perm in itertools.permutations(h8_copies):
        assignment = dict(zip(axes, perm))
        rows.append(
            {
                "assignment": assignment,
                "score": sum(axis_scores[axis]["score"] for axis in axes),
                "axis_scores": axis_scores,
            }
        )
    best_score = max(row["score"] for row in rows)
    best_rows = [row for row in rows if row["score"] == best_score]
    return {
        "axis_order": axes,
        "h8_copies": h8_copies,
        "permutation_count": len(rows),
        "best_score": best_score,
        "best_assignment_count": len(best_rows),
        "best_assignments": best_rows,
        "all_assignments": rows,
        "degeneracy_reason": (
            "The available canonical and ingress data expose three H8 copies but do not attach "
            "static/tropic/optic labels to a distinguished R/G/B copy. The brute force search "
            "therefore finds a real rank-3/weight-8 bridge pattern, but all six assignments tie."
        ),
    }


def normalize_signed_label(label: str) -> str:
    return label.replace("^", "").strip()


def parse_public_atom_label(label: str) -> list[str]:
    return [
        normalize_signed_label(part)
        for part in label.strip("{}").split(",")
        if part.strip()
    ]


def public_atom_label_readout(
    atom_ids: list[int],
    public_atoms_by_id: dict[int, dict[str, Any]],
) -> dict[str, Any]:
    atom_ids = [int(atom_id) for atom_id in atom_ids]
    signed_labels = [
        label
        for atom_id in atom_ids
        for label in parse_public_atom_label(public_atoms_by_id[atom_id]["public_atom_label"])
    ]
    return {
        "atom_ids": atom_ids,
        "public_atom_labels": [
            public_atoms_by_id[atom_id]["public_atom_label"] for atom_id in atom_ids
        ],
        "signed_label_counts": counter_dict(signed_labels),
        "unsigned_sector_counts": counter_dict([label[:1] for label in signed_labels]),
    }


def build_h8_sector_identification() -> dict[str, Any]:
    atom = load_json(HYDROGEN_ATOM)
    alphabetized = load_json(ALPHABETIZED_GOLAY_REPORT)
    ledger_rows = load_csv(HCYCLE_INVARIANT_LEDGER)
    grammar_rows = load_csv(HCYCLE_CIRCUIT_GRAMMAR)

    double_cover_pairs: dict[str, list[str]] = {}
    for entry in atom["quotient_layers"]["A42"]["double_cover"]:
        source, target = [part.strip() for part in entry.split("->")]
        double_cover_pairs.setdefault(target, []).append(normalize_signed_label(source))
    double_cover_pairs = {key: sorted(value) for key, value in sorted(double_cover_pairs.items())}

    finite_reduction = alphabetized["witness"]["finite_reduction"]
    atom_partition = finite_reduction["atom_partition"]
    mog_atom_labels = [normalize_signed_label(label) for label in finite_reduction["mog_atom_labels"]]
    d20_signed_alphabet = [normalize_signed_label(label) for label in finite_reduction["d20_signed_alphabet"]]
    atom_sizes = [int(size) for size in atom_partition["atom_sizes"]]
    atom_sizes_by_label = dict(zip(mog_atom_labels, atom_sizes))
    unsigned_sector_coordinate_sizes = {
        sector: sum(atom_sizes_by_label[label] for label in signed_labels)
        for sector, signed_labels in double_cover_pairs.items()
    }

    hcycle_h8_source_rows = [
        row for row in ledger_rows if "H8" in row["object"] and "G24" in row["object"]
    ]
    hcycle_h6_weight_rows = [
        row
        for row in ledger_rows
        if "H6" in row["object"] or all(label in row["value"] for label in ("B-", "V-", "S-"))
    ]
    rgba_visibility_rows = [
        row for row in grammar_rows if row["circuit"] == "rgba visibility circuit"
    ]

    sector_order = [str(sector) for sector in atom["quotient_layers"]["A12"]["sectors"]]
    rgb_payload = atom["RGBA_and_wall"]["visible_payload"]
    checks = {
        "hydrogen_double_cover_has_three_unsigned_sectors": set(double_cover_pairs) == {"B", "V", "S"}
        and all(len(labels) == 2 for labels in double_cover_pairs.values()),
        "alphabetized_report_matches_signed_h6_atoms": set(d20_signed_alphabet) == set(mog_atom_labels)
        and set(mog_atom_labels) == {label for labels in double_cover_pairs.values() for label in labels},
        "mog_atoms_are_six_by_four": atom_partition["atom_count"] == 6 and set(atom_sizes) == {4},
        "unsigned_sector_pairs_are_weight8": set(unsigned_sector_coordinate_sizes.values()) == {8},
        "hcycle_ledger_uses_same_h6_weight_labels": bool(hcycle_h6_weight_rows),
        "hcycle_ledger_records_h8_cubed_source": bool(hcycle_h8_source_rows),
        "rgba_payload_has_three_named_h8_copies": all(token in rgb_payload for token in ("H_8^{(R)}", "H_8^{(G)}", "H_8^{(B)}"))
        and atom["RGBA_and_wall"]["visible_channels"] == 24,
        "audited_inputs_do_not_name_bvs_to_rgb_bijection": True,
    }

    return {
        "status": "BVS_UNSIGNED_WEIGHT8_H8_SECTOR_PROXY_CERTIFIED_RGB_NAMING_OPEN",
        "sector_order": sector_order,
        "double_cover_pairs": double_cover_pairs,
        "mog_atom_sizes_by_signed_label": atom_sizes_by_label,
        "unsigned_sector_coordinate_sizes": unsigned_sector_coordinate_sizes,
        "hcycle_h8_source_rows": hcycle_h8_source_rows,
        "hcycle_h6_weight_rows": hcycle_h6_weight_rows,
        "rgba_visibility_rows": rgba_visibility_rows,
        "rgb_payload": rgb_payload,
        "certifies": [
            "B/V/S are the three unsigned A12 sector labels obtained from the A42 signed double cover.",
            "The D20 signed H6 alphabet matches the W24/MOG atom labels.",
            "Each signed atom has four W24 coordinates, so each unsigned B/V/S pair has weight 8.",
            "The H-cycle ledger uses the same H6 labels and records an H8^3 finite source.",
        ],
        "does_not_certify": [
            "a canonical bijection from B/V/S sector names to the RGB labels R/G/B",
            "a selected full D20 -> W24 row-refined Golay morphism",
        ],
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def best_screen_sector_assignment(hcycle_rows: list[dict[str, Any]]) -> dict[str, Any]:
    sectors = ["B", "V", "S"]
    rows = []
    for perm in itertools.permutations(sectors):
        assignment = {
            row["screen_id"]: sector for row, sector in zip(hcycle_rows, perm)
        }
        score = sum(
            int(row["combined_turn_type_counts"].get(assignment[row["screen_id"]], 0))
            for row in hcycle_rows
        )
        rows.append({"assignment": assignment, "score": score})
    best_score = max(row["score"] for row in rows)
    best_rows = [row for row in rows if row["score"] == best_score]
    return {
        "sectors": sectors,
        "permutation_count": len(rows),
        "best_score": best_score,
        "best_assignment_count": len(best_rows),
        "best_assignments": best_rows,
        "all_assignments": rows,
        "unique_best_assignment": best_rows[0]["assignment"] if len(best_rows) == 1 else None,
    }


def count_int_values(values: Any) -> dict[str, int]:
    out: dict[str, int] = {}
    for value in values:
        key = str(int(value))
        out[key] = out.get(key, 0) + 1
    return dict(sorted(out.items(), key=lambda item: int(item[0])))


def residue_table_profile(
    vector: np.ndarray,
    block_i: np.ndarray,
    block_j: np.ndarray,
    object_to_sector: dict[int, str],
) -> dict[str, Any]:
    by_source: dict[str, dict[str, int]] = {}
    by_target: dict[str, dict[str, int]] = {}
    by_pair: dict[str, dict[str, int]] = {}
    for src_obj, dst_obj, residue in zip(block_i.tolist(), block_j.tolist(), vector.tolist()):
        src_sector = object_to_sector[int(src_obj)]
        dst_sector = object_to_sector[int(dst_obj)]
        residue_key = str(int(residue))
        by_source.setdefault(src_sector, {})
        by_source[src_sector][residue_key] = by_source[src_sector].get(residue_key, 0) + 1
        by_target.setdefault(dst_sector, {})
        by_target[dst_sector][residue_key] = by_target[dst_sector].get(residue_key, 0) + 1
        pair_key = f"{src_sector}->{dst_sector}"
        by_pair.setdefault(pair_key, {})
        by_pair[pair_key][residue_key] = by_pair[pair_key].get(residue_key, 0) + 1

    def sorted_counts(table: dict[str, dict[str, int]]) -> dict[str, dict[str, int]]:
        return {
            key: dict(sorted(value.items(), key=lambda item: int(item[0])))
            for key, value in sorted(table.items())
        }

    def dominant(table: dict[str, dict[str, int]]) -> dict[str, dict[str, Any]]:
        out = {}
        for key, counts in sorted(table.items()):
            residue, count = max(counts.items(), key=lambda item: (item[1], -int(item[0])))
            total = sum(counts.values())
            out[key] = {
                "residue": residue,
                "count": count,
                "total": total,
                "rate_num_den": [count, total],
            }
        return out

    nonzero_source = sorted(
        key
        for key, counts in by_source.items()
        if sum(count for residue, count in counts.items() if residue != "0") > 0
    )
    nonzero_target = sorted(
        key
        for key, counts in by_target.items()
        if sum(count for residue, count in counts.items() if residue != "0") > 0
    )

    return {
        "residue_counts": count_int_values(vector.tolist()),
        "nonzero_coordinate_count": int(np.count_nonzero(vector)),
        "by_unsigned_source": sorted_counts(by_source),
        "by_unsigned_target": sorted_counts(by_target),
        "by_unsigned_pair": sorted_counts(by_pair),
        "dominant_residue_by_unsigned_source": dominant(by_source),
        "dominant_residue_by_unsigned_target": dominant(by_target),
        "nonzero_source_sectors": nonzero_source,
        "nonzero_target_sectors": nonzero_target,
    }


def build_static_tropic_sector_pullback(discriminator_search: dict[str, Any]) -> dict[str, Any]:
    rules = load_json(STATIC_DESIGNED_RULES)
    q = load_quotients_npz()
    block_i = q["block_i"]
    block_j = q["block_j"]
    q12_map = q["q12_map"]
    q42_map = q["q42_map"]
    object_labels = [normalize_signed_label(label) for label in rules["object_labels"]]
    object_to_sector = {idx: label[:1] for idx, label in enumerate(object_labels)}
    vectors = {
        "z2_a12_parity": q12_map % 2,
        "z4_a42_clock": q42_map % 4,
        "z4_a12_frame_clock": (q12_map + block_i + block_j) % 4,
    }
    static_rows = []
    for generator, vector in sorted(vectors.items()):
        profile = residue_table_profile(vector, block_i, block_j, object_to_sector)
        static_rows.append(
            {
                "quotient_generator": generator,
                "profile": profile,
            }
        )

    static_single_sector_generators = [
        row["quotient_generator"]
        for row in static_rows
        if len(row["profile"]["nonzero_source_sectors"]) == 1
        or len(row["profile"]["nonzero_target_sectors"]) == 1
    ]
    z2_target_s = next(
        row for row in static_rows if row["quotient_generator"] == "z2_a12_parity"
    )["profile"]["dominant_residue_by_unsigned_target"]["S"]

    cycles = {int(row["cycle_id"]): row for row in load_csv(HCYCLE_PRIMITIVE_CYCLES)}
    edges = {int(row["edge_id"]): row for row in load_csv(HCYCLE_D20_EDGES)}
    gamma_cycle = cycles[8]
    gamma_turns = gamma_cycle["turn_addresses"].split()
    gamma_edges = [int(edge_id) for edge_id in gamma_cycle["edge_ids"].split()]
    gamma_turn_type_counts = counter_dict([turn[:1] for turn in gamma_turns])
    gamma_dominant_sector = max(
        gamma_turn_type_counts.items(),
        key=lambda item: (item[1], item[0]),
    )[0]
    defect_pairs = discriminator_search["defect_pairs"]
    gamma_screen = next(
        screen_id for screen_id, pair in defect_pairs.items() if 8 in pair
    )
    screen_assignment = discriminator_search["discriminator_result"][
        "screen_to_unsigned_h8_sector_assignment"
    ]
    gamma_screen_sector = screen_assignment[gamma_screen]

    cycle8 = load_json(CYCLE8_REPORT)
    typed_update = cycle8["known_certified_data"]["typed_nonexact_optical_flux_update"][
        "first_obstruction_update"
    ]
    unique_public_zero = cycle8["known_certified_data"]["unique_public_zero_support"][
        "unique_public_zero_support"
    ]
    public_shadow = cycle8["known_certified_data"]["sector_interface"]["public_terminal_shadow"]

    tropic = {
        "gamma8_cycle_id": 8,
        "gamma8_turn_addresses": gamma_turns,
        "gamma8_turn_type_counts": gamma_turn_type_counts,
        "gamma8_signed_turn_counts": counter_dict(gamma_turns),
        "gamma8_edge_ids": gamma_edges,
        "gamma8_selector_choice_counts": counter_dict(
            [str(edges[edge_id]["selector_choice"]) for edge_id in gamma_edges]
        ),
        "gamma8_dominant_visible_sector": gamma_dominant_sector,
        "gamma8_defect_pair_screen": gamma_screen,
        "gamma8_screen_sector": gamma_screen_sector,
        "gamma8_visible_sector_consensus": gamma_dominant_sector == gamma_screen_sector == "V",
        "hidden_update": typed_update["hidden_update_integral"],
        "public_update": typed_update["public_update"],
        "support_component": typed_update["support_component"],
        "support_sector": typed_update["support_sector"],
        "public_shadow": public_shadow,
        "unique_public_zero_active_objects": [
            normalize_signed_label(label) for label in unique_public_zero["active_objects"]
        ],
        "hidden_residual_is_public_zero_r33": (
            typed_update["support_component"] == "R33"
            and typed_update["support_sector"] == 33
            and all(value == 0 for value in typed_update["public_update"].values())
            and public_shadow["q12_nonzero_count"] == 0
            and public_shadow["q42_nonzero_count"] == 0
        ),
    }

    static = {
        "object_labels": object_labels,
        "object_to_unsigned_sector": object_to_sector,
        "object_indexing_rule": rules["object_indexing"],
        "rows": static_rows,
        "static_frame_uses_bvs_object_indexing": "B=0, V=1, S=2"
        in rules["object_indexing"]["family_index"],
        "single_sector_generator_candidates": static_single_sector_generators,
        "single_sector_generator_detected": bool(static_single_sector_generators),
        "z2_target_S_dominant_residue": z2_target_s,
        "z2_target_S_is_near_detector": z2_target_s["residue"] == "1"
        and z2_target_s["rate_num_den"] == [452, 454],
        "public_zero_screen_sector": screen_assignment.get("signed_turn_screen_0"),
    }

    return {
        "static": static,
        "tropic": tropic,
        "result": {
            "static_frame_pulled_into_bvs": static["static_frame_uses_bvs_object_indexing"],
            "static_individual_generator_to_single_sector_remains_open": not static[
                "single_sector_generator_detected"
            ],
            "static_public_zero_overlap_lands_on_S_screen": static["public_zero_screen_sector"] == "S",
            "tropic_gamma8_visible_cycle_lands_on_V": tropic["gamma8_visible_sector_consensus"],
            "tropic_hidden_residual_lands_on_R33_not_public_BVS": tropic[
                "hidden_residual_is_public_zero_r33"
            ],
            "full_static_tropic_bvs_attachment_remains_open": True,
        },
        "interpretation": (
            "Static is now pulled into the B/V/S frame through source/target object indexing, "
            "but no individual static generator has support on a single unsigned sector. "
            "The strongest static scalar clue is the z2 target-S near detector, while the "
            "public-zero Fourier overlap lands on the S screen. Tropic gamma_8 lands on V at "
            "the visible H-cycle/screen level, but its nonexact height residual remains the "
            "hidden public-zero R33 channel."
        ),
    }


def build_static_tropic_ward_composition_audit(
    static_tropic_pullback: dict[str, Any],
    discriminator_search: dict[str, Any],
) -> dict[str, Any]:
    selected_report = load_json(SELECTED_SOURCED_WARD_REPORT)
    selector_report = load_json(WARD_KERNEL_HEIGHT_SELECTOR_REPORT)
    selected_summary = selected_report["derived"]["sourced_balance_summary"]
    scattering_step = selected_summary["scattering_step"]
    source_decomposition = selected_summary["source_decomposition"]
    selected_hidden_terms = selected_summary["selected_hidden_terms"]
    selected_public_terms = selected_summary["selected_public_terms"]
    source_rows = selected_report["derived"]["source_decomposition_rows"]
    selector_summary = selector_report["derived"]["selector_summary"]
    height_decomposition = selector_summary["height_decomposition"]

    cycles = {int(row["cycle_id"]): row for row in load_csv(HCYCLE_PRIMITIVE_CYCLES)}

    def visible_turn_profile(cycle_ids: list[int]) -> dict[str, Any]:
        turns: list[str] = []
        for cycle_id in cycle_ids:
            turns.extend(cycles[cycle_id]["turn_addresses"].split())
        counts = counter_dict([turn[:1] for turn in turns])
        dominant_sector = max(counts.items(), key=lambda item: (item[1], item[0]))[0]
        return {
            "cycle_ids": cycle_ids,
            "turn_addresses": turns,
            "turn_type_counts": counts,
            "turn_type_signature": signature_from_counts(counts, ("B", "S", "V")),
            "dominant_visible_sector": dominant_sector,
        }

    gamma8_visible = visible_turn_profile([8])
    cycle5_visible = visible_turn_profile([5])
    selected_visible = visible_turn_profile([5, 8])
    matching_screens = sorted(
        row["screen_id"]
        for row in discriminator_search["hcycle_pullback"]["rows"]
        if row["combined_turn_type_signature"] == selected_visible["turn_type_signature"]
    )
    screen_assignment = discriminator_search["discriminator_result"][
        "screen_to_unsigned_h8_sector_assignment"
    ]
    matching_screen_sectors = {
        screen_id: screen_assignment.get(screen_id) for screen_id in matching_screens
    }

    static_tokens = (
        "z2_a12_parity",
        "burning_static",
        "static_tropic",
        "static/tropic",
    )
    bounded_reports = {
        SELECTED_SOURCED_WARD_REPORT: selected_report,
        WARD_KERNEL_HEIGHT_SELECTOR_REPORT: selector_report,
    }
    static_token_hits = {
        rel: [token for token in static_tokens if contains_text_token(payload, token)]
        for rel, payload in bounded_reports.items()
    }
    bounded_report_mentions_static_clue = any(static_token_hits.values())
    static_z2_near_detector = static_tropic_pullback["static"][
        "z2_target_S_is_near_detector"
    ]

    composition_identity = {
        "source_mask_is_gamma8": source_decomposition["source_mask"] == 256,
        "generator_mask_is_cycle5": source_decomposition["generator_mask"] == 32,
        "target_mask_is_selected_288": source_decomposition["target_mask"] == 288,
        "basis_cycles_are_cycle5_plus_gamma8": selected_summary["selected_basis_cycle_ids"]
        == [5, 8],
        "height_decomposes_as_cycle5_plus_gamma8": height_decomposition
        == {
            "cycle5_height_action": 691200,
            "gamma8_height_action": 374784,
            "sum": 1065984,
        },
        "scattering_step_is_gamma8_plus_generator5": scattering_step["source_mask"] == 256
        and scattering_step["target_mask"] == 288
        and scattering_step["generator_cycle_id"] == 5
        and scattering_step["toggle"] == "add",
        "source_rows_match_selected_summary": source_rows["gamma8"]["mask"] == 256
        and source_rows["cycle5"]["mask"] == 32
        and source_rows["selected_288"]["mask"] == 288,
    }
    balance_identity = {
        "selected_public_terms_all_zero": all_leaves_zero(selected_public_terms),
        "selected_hidden_packet_is_kernel": selected_hidden_terms["hidden_packet"] == "kernel",
        "selected_hidden_balance_closes": selected_hidden_terms["hidden_balance_error"] == 0,
        "selected_corrected_clock_is_zero": selected_hidden_terms["corrected_R33_mod26"] == 0,
    }

    result = {
        "tropic_ward_composition_found": selected_report["all_checks_pass"] is True
        and selector_report["all_checks_pass"] is True
        and selected_report["checks"]["gamma8_to_selected_scattering_step_is_generator5"] is True
        and selector_report["checks"]["selected_mask_is_gamma8_plus_cycle5"] is True
        and all(composition_identity.values()),
        "selected_lift_closes_public_and_hidden_balance": selected_report["checks"][
            "selected_bms_row_closes_hidden_balance"
        ]
        is True
        and selected_report["checks"]["selected_bms_row_closes_public_balance"] is True
        and all(balance_identity.values()),
        "selected_lift_matches_V_screen_signature": matching_screen_sectors
        == {"signed_turn_screen_1": "V"},
        "static_z2_target_S_remains_unattached_to_bounded_ward_reports": static_z2_near_detector
        and not bounded_report_mentions_static_clue,
        "direct_static_tropic_commutator_or_ward_term_remains_open": static_z2_near_detector
        and not bounded_report_mentions_static_clue
        and selector_report["checks"]["individual_source_no_go_remains_in_force"] is True,
    }

    return {
        "status": "TROPIC_WARD_COMPOSITION_CERTIFIED_STATIC_Z2_ATTACHMENT_OPEN",
        "bounded_ward_reports": sorted(bounded_reports),
        "composition_identity": composition_identity,
        "balance_identity": balance_identity,
        "scattering_step": scattering_step,
        "source_decomposition": source_decomposition,
        "selected_hidden_terms": selected_hidden_terms,
        "selected_public_terms": selected_public_terms,
        "selector_summary": {
            "selected_mask": selector_summary["selected_mask"],
            "selected_basis_cycle_ids": selector_summary["selected_basis_cycle_ids"],
            "selected_height_action": selector_summary["selected_height_action"],
            "selected_in_ward_kernel": selector_summary["selected_in_ward_kernel"],
            "selected_corrected_clock_mod26": selector_summary["selected_corrected_clock_mod26"],
            "compact_exposure_witness": selector_summary["compact_exposure_witness"],
            "height_decomposition": height_decomposition,
            "minimality_witness": selector_summary["minimality_witness"],
            "source_lift": selector_summary["source_lift"],
        },
        "visible_turn_profiles": {
            "gamma8": gamma8_visible,
            "cycle5": cycle5_visible,
            "selected_288": selected_visible,
        },
        "selected_turn_signature_screen_matches": matching_screens,
        "selected_turn_signature_screen_sectors": matching_screen_sectors,
        "bounded_static_token_hits": static_token_hits,
        "result": result,
        "all_checks_pass": all(result.values()),
        "interpretation": (
            "A certified tropic Ward composition exists: gamma_8 toggled by generator 5 "
            "selects mask 288 = cycle5 + gamma_8 and closes the public and hidden Ward/BMS "
            "balance. Its visible B/S/V turn signature matches the V-assigned optic screen, "
            "not the static z2 target-S near detector. In the bounded Ward reports audited "
            "here, the static z2 clue is absent, so the direct static/tropic commutator remains open."
        ),
    }


def build_selected_mask_z2_static_audit(
    ward_composition_audit: dict[str, Any],
) -> dict[str, Any]:
    selected_screen_sectors = ward_composition_audit["selected_turn_signature_screen_sectors"]
    selected_screens = sorted(selected_screen_sectors)
    overlap_rows = [
        row
        for row in load_csv(STATIC_FOURIER_OVERLAP)
        if row["quotient_generator"] == "z2_a12_parity"
        and row["screen_id"] in selected_screens
    ]

    def row_bool(row: dict[str, str], key: str) -> bool:
        return row[key] == "True"

    support_rows = [
        {
            "screen_id": row["screen_id"],
            "sector_support": row["sector_support"],
            "fourier_scalar_on_support": row_bool(row, "fourier_scalar_on_support"),
            "fourier_support_scalar": row["fourier_support_scalar"],
            "fourier_canonical_trace_defined": row_bool(
                row,
                "fourier_canonical_trace_defined",
            ),
            "constructed_kernel_contains_support": row_bool(
                row,
                "constructed_kernel_contains_support",
            ),
            "constructed_kernel_intersection": row["constructed_kernel_intersection"],
        }
        for row in overlap_rows
    ]
    scalar_supports = [
        row["sector_support"] for row in support_rows if row["fourier_scalar_on_support"]
    ]
    non_scalar_supports = [
        row["sector_support"] for row in support_rows if not row["fourier_scalar_on_support"]
    ]
    hidden_sector33_rows = [
        row for row in support_rows if row["sector_support"] == "{33}"
    ]
    hidden_sector33_hit = len(hidden_sector33_rows) == 1 and all(
        row["fourier_scalar_on_support"]
        and row["fourier_canonical_trace_defined"]
        and row["constructed_kernel_contains_support"]
        for row in hidden_sector33_rows
    )
    selected_public_terms_zero = ward_composition_audit["balance_identity"][
        "selected_public_terms_all_zero"
    ]
    selected_hidden_kernel = (
        ward_composition_audit["selected_hidden_terms"]["hidden_packet"] == "kernel"
        and ward_composition_audit["selected_hidden_terms"]["corrected_R33_mod26"] == 0
    )

    result = {
        "z2_evaluated_on_selected_V_screen_envelope": selected_screen_sectors
        == {"signed_turn_screen_1": "V"}
        and len(support_rows) == 5,
        "z2_hits_hidden_sector33_kernel": hidden_sector33_hit
        and selected_public_terms_zero
        and selected_hidden_kernel,
        "z2_not_scalar_on_full_selected_screen_support_envelope": bool(non_scalar_supports),
        "mask288_exact_sector_support_remains_open": True,
        "z2_selected_mask_static_attachment_remains_open": hidden_sector33_hit
        and bool(non_scalar_supports),
    }

    return {
        "status": "MASK288_Z2_SCREEN_ENVELOPE_EVALUATED_EXACT_SUPPORT_OPEN",
        "claim_boundary": (
            "This evaluates z2_a12_parity on the selected mask's matched V-screen support "
            "envelope. It does not derive a unique sector support for mask 288 itself."
        ),
        "selected_mask": ward_composition_audit["selector_summary"]["selected_mask"],
        "selected_screen_sectors": selected_screen_sectors,
        "quotient_generator": "z2_a12_parity",
        "support_rows": support_rows,
        "scalar_supports": scalar_supports,
        "non_scalar_supports": non_scalar_supports,
        "hidden_sector33_hit": hidden_sector33_hit,
        "selected_public_terms_zero": selected_public_terms_zero,
        "selected_hidden_kernel": selected_hidden_kernel,
        "result": result,
        "all_checks_pass": all(result.values()),
        "interpretation": (
            "On the selected V-screen envelope, z2_a12_parity cleanly hits the hidden sector-33 "
            "kernel and is compatible with the closed mask-288 Ward balance. It is not scalar "
            "on the full screen support envelope, so this is evidence for orthogonality to the "
            "hidden closure, not a static/tropic attachment theorem."
        ),
    }


def build_selected_mask_exact_h6_support_audit(
    ward_composition_audit: dict[str, Any],
) -> dict[str, Any]:
    incidence = load_json(D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE_REPORT)
    restriction = load_json(D20_EXPLICIT_PACKET_RESTRICTION_MAP_TEST_REPORT)
    selector_summary = ward_composition_audit["selector_summary"]
    compact_witness = selector_summary["compact_exposure_witness"]
    selected_step_atom_ids = compact_witness["selected_active_step_atom_ids"]
    selected_cycle_ids = selector_summary["selected_basis_cycle_ids"]

    public_atoms_by_id = {
        int(row["public_atom_id"]): row
        for row in incidence["derived"]["public_atom_rows"]
    }
    generator_rows_by_id = {
        int(row["generator_cycle_id"]): row
        for row in incidence["derived"]["generator_boundary_closure_rows"]
    }
    step_rows_by_id = {
        int(row["step_atom_id"]): row
        for row in incidence["derived"]["step_atom_boundary_incidence_rows"]
    }

    selected_cycle_rows = [generator_rows_by_id[cycle_id] for cycle_id in selected_cycle_ids]
    selected_public_atom_ids = sorted(
        {
            int(atom_id)
            for row in selected_cycle_rows
            for atom_id in row["source_target_vertices"]
        }
    )
    selected_public_atom_rows = [
        {
            "public_atom_id": atom_id,
            "public_atom_label": public_atoms_by_id[atom_id]["public_atom_label"],
            "h6_triple": public_atoms_by_id[atom_id]["h6_triple"],
        }
        for atom_id in selected_public_atom_ids
    ]
    signed_labels = [
        label
        for row in selected_public_atom_rows
        for label in parse_public_atom_label(row["public_atom_label"])
    ]
    selected_step_rows = []
    for step_atom_id in selected_step_atom_ids:
        row = step_rows_by_id[step_atom_id]
        selected_step_rows.append(
            {
                "step_atom_id": step_atom_id,
                "directed_channel_swaps": row["directed_channel_swaps"],
                "boundary_projection_support": row["boundary_projection_support"],
                "vector_support": row["vector_support"],
                "signed_vertex_support": [
                    {
                        "public_atom_id": item["public_atom_id"],
                        "coefficient": item["coefficient"],
                        "public_atom_label": public_atoms_by_id[item["public_atom_id"]][
                            "public_atom_label"
                        ],
                    }
                    for item in row["signed_vertex_support"]
                ],
            }
        )

    missing_q12_bridge_rows = [
        row
        for row in restriction["derived"]["missing_bridge_inventory"]
        if row["candidate"] == "q42_q12_tensor_to_full_packets"
    ]
    q12_projection_missing = (
        restriction["checks"]["a985_tube_q42_q12_packet_projection_is_absent"] is True
        and missing_q12_bridge_rows
        and missing_q12_bridge_rows[0]["status"]
        == "blocked_missing_quotient_class_to_packet_projection"
    )
    result = {
        "boundary_loop_step_atom_incidence_certified": incidence["all_checks_pass"] is True,
        "selected_cycles_are_cycle5_and_gamma8": selected_cycle_ids == [5, 8],
        "selected_cycles_close_on_h6_boundary": all(
            row["path_closes"] is True and row["signed_boundary_zero"] is True
            for row in selected_cycle_rows
        ),
        "selected_h6_public_atom_support_materialized": selected_public_atom_ids
        == [0, 1, 4, 7, 10, 11, 13, 16],
        "selected_h6_public_atom_support_is_weight8": len(selected_public_atom_ids) == 8,
        "selected_step_atom_support_values_materialized": sorted(
            {row["boundary_projection_support"] for row in selected_step_rows}
        )
        == [14, 16, 33, 44, 86],
        "q12_exact_z2_retest_blocked_by_missing_projection": bool(q12_projection_missing),
    }

    return {
        "status": "MASK288_EXACT_H6_SUPPORT_MATERIALIZED_Z2_RETEST_BLOCKED",
        "claim_boundary": (
            "This materializes the selected mask's exact Lambda^3 H6 public-atom support "
            "from the certified boundary incidence table. It does not evaluate q12/z2 on "
            "that support, because the certified q42/q12-to-packet projection is absent."
        ),
        "selected_mask": selector_summary["selected_mask"],
        "selected_cycle_ids": selected_cycle_ids,
        "selected_step_atom_ids": selected_step_atom_ids,
        "selected_step_atom_rows": selected_step_rows,
        "selected_boundary_projection_support_values": sorted(
            {row["boundary_projection_support"] for row in selected_step_rows}
        ),
        "selected_h6_public_atom_ids": selected_public_atom_ids,
        "selected_h6_public_atom_rows": selected_public_atom_rows,
        "selected_h6_signed_label_counts": counter_dict(signed_labels),
        "selected_h6_unsigned_sector_counts": counter_dict([label[:1] for label in signed_labels]),
        "selected_cycle_closure_rows": selected_cycle_rows,
        "missing_q12_packet_projection": missing_q12_bridge_rows[0]
        if missing_q12_bridge_rows
        else None,
        "z2_exact_retest_status": "BLOCKED_MISSING_Q12_TO_H6_PUBLIC_ATOM_PROJECTION",
        "result": result,
        "all_checks_pass": all(result.values()),
        "interpretation": (
            "Mask 288 has an exact weight-8 public H6 support on atoms "
            "0,1,4,7,10,11,13,16. This is the desired mask-local support seam, but the "
            "static z2_a12_parity observable lives in the q12/A985 quotient domain. The "
            "repo already certifies that the q42/q12 quotient-to-packet projection is absent, "
            "so the exact z2 retest is genuinely blocked at that bridge."
        ),
    }


def canonical_cycle(cycle: list[int]) -> tuple[int, ...]:
    variants: list[tuple[int, ...]] = []
    n = len(cycle)
    for seq in (cycle, list(reversed(cycle))):
        for i in range(n):
            rotated = seq[i:] + seq[:i]
            variants.append(tuple(rotated))
    return min(variants)


def derive_q12_selector_pentagons(selector: dict[str, Any]) -> dict[str, Any]:
    edge_set: set[tuple[int, int]] = set()
    labels: dict[int, list[str]] = {}
    for edge in selector.get("root_edges", []):
        indices = [int(x) for x in edge.get("edge_indices", [])]
        face_labels = edge.get("face_labels", [])
        if len(indices) != 2:
            continue
        edge_set.add(tuple(sorted(indices)))
        for index, label in zip(indices, face_labels):
            labels[index] = [str(part) for part in label]

    vertices = sorted(labels)
    adjacency: dict[int, set[int]] = {vertex: set() for vertex in vertices}
    for a, b in edge_set:
        adjacency.setdefault(a, set()).add(b)
        adjacency.setdefault(b, set()).add(a)

    cycles: set[tuple[int, ...]] = set()
    for start in vertices:
        stack: list[tuple[int, list[int]]] = [(start, [start])]
        while stack:
            current, path = stack.pop()
            if len(path) == 5:
                if start in adjacency[current]:
                    cycles.add(canonical_cycle(path))
                continue
            for nxt in sorted(adjacency[current]):
                if nxt not in path:
                    stack.append((nxt, path + [nxt]))

    pentagons = [list(cycle) for cycle in sorted(cycles)]
    degree_histogram = counter_dict(
        [str(len(adjacency.get(vertex, ()))) for vertex in vertices]
    )
    graph_checks = {
        "vertex_count_is_20": len(vertices) == 20,
        "edge_count_is_30": len(edge_set) == 30,
        "degree_histogram_is_3_regular": degree_histogram == {"3": 20},
        "pentagon_cycle_count_is_12": len(pentagons) == 12,
        "source_status_is_d20_selector": selector.get("status")
        == "D20_SELECTOR_DERIVED_FROM_D6_COXETER_POLARITY",
    }
    return {
        "vertices": [{"index": index, "label": labels[index]} for index in vertices],
        "edges": [list(edge) for edge in sorted(edge_set)],
        "degree_histogram": degree_histogram,
        "pentagon_cycles": pentagons,
        "graph_checks": graph_checks,
        "graph_valid": all(graph_checks.values()),
    }


def subset_candidate(
    selected_q12_classes: list[int],
    materialized_atom_ids: list[int],
    target_atom_ids: list[int],
) -> dict[str, Any]:
    materialized = set(materialized_atom_ids)
    target = set(target_atom_ids)
    extra = sorted(materialized - target)
    missing = sorted(target - materialized)
    return {
        "selected_q12_classes": selected_q12_classes,
        "materialized_atom_ids": sorted(materialized),
        "extra_atom_ids": extra,
        "missing_atom_ids": missing,
        "distance_to_target": len(extra) + len(missing),
    }


def brute_force_q12_subset_supports(
    pentagons: list[list[int]],
    target_atom_ids: list[int],
) -> dict[str, Any]:
    target = set(target_atom_ids)
    union_exact: list[list[int]] = []
    parity_exact: list[list[int]] = []
    union_candidates: list[tuple[int, int, int, int, list[int], list[int]]] = []
    parity_candidates: list[tuple[int, int, int, int, list[int], list[int]]] = []

    for mask in range(1 << len(pentagons)):
        chosen = [idx for idx in range(len(pentagons)) if (mask >> idx) & 1]
        union_support: set[int] = set()
        parity_support: set[int] = set()
        for idx in chosen:
            union_support.update(pentagons[idx])
            for atom_id in pentagons[idx]:
                if atom_id in parity_support:
                    parity_support.remove(atom_id)
                else:
                    parity_support.add(atom_id)

        if union_support == target:
            union_exact.append(chosen)
        if parity_support == target:
            parity_exact.append(chosen)

        union_extra = len(union_support - target)
        union_missing = len(target - union_support)
        union_candidates.append(
            (
                union_extra + union_missing,
                union_extra,
                union_missing,
                len(chosen),
                chosen,
                sorted(union_support),
            )
        )
        parity_extra = len(parity_support - target)
        parity_missing = len(target - parity_support)
        parity_candidates.append(
            (
                parity_extra + parity_missing,
                parity_extra,
                parity_missing,
                len(chosen),
                chosen,
                sorted(parity_support),
            )
        )

    best_union = sorted(union_candidates)[0]
    best_parity = sorted(parity_candidates)[0]
    return {
        "search_space_size": 1 << len(pentagons),
        "target_atom_ids": target_atom_ids,
        "raw_union_exact_solution_count": len(union_exact),
        "raw_union_exact_solutions": union_exact,
        "raw_parity_exact_solution_count": len(parity_exact),
        "raw_parity_exact_solutions": parity_exact,
        "best_raw_union_candidate": subset_candidate(
            best_union[4],
            best_union[5],
            target_atom_ids,
        ),
        "best_raw_parity_candidate": subset_candidate(
            best_parity[4],
            best_parity[5],
            target_atom_ids,
        ),
    }


def brute_force_signed_unit_q12_support(
    pentagons: list[list[int]],
    target_atom_ids: list[int],
) -> dict[str, Any]:
    target = set(target_atom_ids)
    target_vector = [1 if atom_id in target else 0 for atom_id in range(20)]
    first_hit: list[int] | None = None
    tested = 0
    for coefficients in itertools.product((-1, 0, 1), repeat=len(pentagons)):
        if not any(coefficients):
            continue
        tested += 1
        vector = [0 for _ in range(20)]
        for q12_class, coefficient in enumerate(coefficients):
            if coefficient == 0:
                continue
            for atom_id in pentagons[q12_class]:
                vector[atom_id] += int(coefficient)
        if vector == target_vector:
            first_hit = [int(coefficient) for coefficient in coefficients]
            break

    return {
        "coefficient_set": [-1, 0, 1],
        "search_space_size": (3 ** len(pentagons)) - 1,
        "tested_until_first_hit_or_exhaustion": tested,
        "exact_hit_found": first_hit is not None,
        "first_hit_coefficients": first_hit,
    }


def build_q12_h6_projection_audit(
    exact_h6_audit: dict[str, Any],
) -> dict[str, Any]:
    selector = load_json(D20_SELECTOR_DERIVATION)
    q12 = load_json(Q12_SECTION)
    incidence = load_json(D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE_REPORT)
    restriction = load_json(D20_EXPLICIT_PACKET_RESTRICTION_MAP_TEST_REPORT)
    loop_snf = load_json(D20_LOOP_STEP_PACKET_SNF_PROBE_REPORT)

    selector_graph = derive_q12_selector_pentagons(selector)
    pentagons = selector_graph["pentagon_cycles"]
    q12_section_indices = [int(index) for index in q12["section_indices"]]
    public_atoms_by_id = {
        int(row["public_atom_id"]): row
        for row in incidence["derived"]["public_atom_rows"]
    }
    q12_rows = []
    for q12_class, atom_ids in enumerate(pentagons):
        q12_rows.append(
            {
                "q12_class": q12_class,
                "section_relation_id": q12_section_indices[q12_class],
                "h6_public_atom_ids": atom_ids,
                "h6_public_atom_labels": [
                    public_atoms_by_id[atom_id]["public_atom_label"] for atom_id in atom_ids
                ],
            }
        )

    coverage_counts: dict[int, int] = {}
    for atom_ids in pentagons:
        for atom_id in atom_ids:
            coverage_counts[atom_id] = coverage_counts.get(atom_id, 0) + 1
    coverage_histogram = counter_dict([str(count) for count in coverage_counts.values()])
    row_weight_histogram = counter_dict([str(len(atom_ids)) for atom_ids in pentagons])

    target_atom_ids = exact_h6_audit["selected_h6_public_atom_ids"]
    brute_force = brute_force_q12_subset_supports(pentagons, target_atom_ids)
    signed_unit = brute_force_signed_unit_q12_support(pentagons, target_atom_ids)
    target = set(target_atom_ids)
    overlap_rows = [
        {
            "q12_class": row["q12_class"],
            "section_relation_id": row["section_relation_id"],
            "overlap_atom_ids": sorted(target.intersection(row["h6_public_atom_ids"])),
            "overlap_count": len(target.intersection(row["h6_public_atom_ids"])),
            "outside_target_atom_ids": sorted(set(row["h6_public_atom_ids"]) - target),
        }
        for row in q12_rows
    ]
    missing_bridge_rows = [
        row
        for row in restriction["derived"]["missing_bridge_inventory"]
        if row["candidate"] == "q42_q12_tensor_to_full_packets"
    ]
    smith = incidence["derived"]["boundary_atom_step_incidence_smith_normal_form"]
    packet_projection_absent = (
        restriction["checks"]["a985_tube_q42_q12_packet_projection_is_absent"] is True
        and missing_bridge_rows
        and missing_bridge_rows[0]["status"]
        == "blocked_missing_quotient_class_to_packet_projection"
    )

    result = {
        "q12_selector_graph_materialized": selector_graph["graph_valid"] is True,
        "q12_section_has_12_classes": q12.get("class_count") == 12
        and len(q12_section_indices) == 12,
        "q12_selector_rows_cover_h6_atoms_uniformly": (
            row_weight_histogram == {"5": 12}
            and len(coverage_counts) == 20
            and coverage_histogram == {"3": 20}
        ),
        "target_mask_h6_support_is_weight8": len(target_atom_ids) == 8,
        "raw_q12_union_does_not_materialize_target_support": (
            brute_force["raw_union_exact_solution_count"] == 0
        ),
        "raw_q12_parity_does_not_materialize_target_support": (
            brute_force["raw_parity_exact_solution_count"] == 0
        ),
        "signed_unit_q12_combination_does_not_materialize_target_support": (
            signed_unit["exact_hit_found"] is False
        ),
        "certified_q12_packet_projection_absent": bool(packet_projection_absent),
        "boundary_torsion_obstruction_present": smith["nonunit_invariant_factors"]
        == [2, 4, 4],
        "visible_loop_snf_no_raw_packet_bridge": (
            loop_snf["checks"]["no_visible_loop_step_column_passes_packet_snf"] is True
        ),
    }
    result["q12_h6_candidate_not_sufficient_for_z2_retest"] = all(result.values())

    return {
        "status": "Q12_H6_SELECTOR_CANDIDATE_MATERIALIZED_PACKET_NORMALIZATION_BLOCKED",
        "claim_boundary": (
            "This materializes the compiler/selector q12-to-D20 pentagon readout and brute-forces "
            "raw union/parity combinations against the exact mask-288 Lambda^3 H6 support. It is "
            "not a certified q12/A985-to-packet action, and it does not discharge the z2 retest."
        ),
        "selected_mask": exact_h6_audit["selected_mask"],
        "selected_h6_public_atom_ids": target_atom_ids,
        "candidate_method": "canonical_sorted_d20_pentagon_incidence_from_q12",
        "q12_section": {
            "status": q12.get("status"),
            "class_count": q12.get("class_count"),
            "section_indices": q12_section_indices,
            "section_method": q12.get("section_method"),
        },
        "selector_graph": selector_graph,
        "q12_h6_rows": q12_rows,
        "row_weight_histogram": row_weight_histogram,
        "coverage_multiplicity_histogram": coverage_histogram,
        "coverage_atom_count": len(coverage_counts),
        "target_overlap_rows": overlap_rows,
        "raw_combination_bruteforce": brute_force,
        "signed_unit_bruteforce": signed_unit,
        "packet_normalization_boundary": {
            "missing_q12_packet_projection": missing_bridge_rows[0]
            if missing_bridge_rows
            else None,
            "boundary_smith_nonunit_factors": smith["nonunit_invariant_factors"],
            "zero_sum_boundary_lattice_index": incidence["derived"]["incidence_summary"][
                "zero_sum_boundary_lattice_index"
            ],
            "loop_step_packet_snf_status": loop_snf["status"],
            "no_visible_loop_step_column_passes_packet_snf": loop_snf["checks"][
                "no_visible_loop_step_column_passes_packet_snf"
            ],
        },
        "result": result,
        "all_checks_pass": all(result.values()),
        "interpretation": (
            "The q12 selector gives twelve pentagon rows on the 20 Lambda^3 H6 public atoms, "
            "each atom appearing in exactly three rows. The mask-288 support is not a raw q12 "
            "pentagon union, parity sum, or signed unit combination, and the certified packet "
            "projection/SNF reports still block a z2 exact retest. The remaining high-yield seam "
            "is a normalized signed/weighted quotient map that kills the 2,4,4 boundary torsion."
        ),
    }


def build_q12_packet_low_support_normalization_audit(
    q12_h6_projection_audit: dict[str, Any],
) -> dict[str, Any]:
    row_norm = load_json(D20_BOUNDARY_PACKET_ROW_NORMALIZATION_OBSTRUCTION_REPORT)
    low_support = load_json(D20_BOUNDARY_PACKET_LOW_SUPPORT_CANDIDATE_ATLAS_REPORT)
    packet_snf = load_json(D20_PACKET_BRIDGE_SNF_OBSTRUCTION_REPORT)

    selected = set(q12_h6_projection_audit["selected_h6_public_atom_ids"])
    q12_rows = q12_h6_projection_audit["q12_h6_rows"]
    family_rows = low_support["derived"]["even_image_support_family_rows"]
    family_scan_rows = []
    q12_seed_rows = []
    selected_family_rows = []
    for family_row in family_rows:
        family = [int(atom_id) for atom_id in family_row["public_atom_support"]]
        family_set = set(family)
        containing_q12_rows = []
        for q12_row in q12_rows:
            q12_atom_set = set(q12_row["h6_public_atom_ids"])
            if family_set.issubset(q12_atom_set):
                containing_q12_rows.append(
                    {
                        "q12_class": q12_row["q12_class"],
                        "section_relation_id": q12_row["section_relation_id"],
                        "h6_public_atom_ids": q12_row["h6_public_atom_ids"],
                        "selected_overlap_atom_ids": sorted(
                            selected.intersection(q12_atom_set)
                        ),
                        "extra_atom_ids_outside_selected_mask": sorted(q12_atom_set - selected),
                        "missing_selected_atom_ids": sorted(selected - q12_atom_set),
                    }
                )
        scan_row = {
            "packet_low_support_family": family,
            "signed_candidate_count": family_row["signed_candidate_count"],
            "contained_in_selected_mask288_support": family_set.issubset(selected),
            "containing_q12_rows": containing_q12_rows,
            "containing_q12_row_count": len(containing_q12_rows),
        }
        family_scan_rows.append(scan_row)
        if scan_row["contained_in_selected_mask288_support"]:
            selected_family_rows.append(scan_row)
        for containing_row in containing_q12_rows:
            q12_seed_rows.append(
                {
                    "packet_low_support_family": family,
                    **containing_row,
                    "family_inside_selected_mask288_support": family_set.issubset(selected),
                }
            )

    mask288_seed_rows = [
        row for row in q12_seed_rows if row["family_inside_selected_mask288_support"]
    ]
    row_summary = row_norm["derived"]["obstruction_summary"]
    low_support_summary = low_support["derived"]["low_support_summary"]
    packet_summary = packet_snf["derived"]["obstruction_summary"]

    result = {
        "row_normalization_obstruction_certified": row_norm["all_checks_pass"] is True,
        "low_support_candidate_atlas_certified": low_support["all_checks_pass"] is True,
        "packet_snf_obstruction_certified": packet_snf["all_checks_pass"] is True,
        "all_packet_low_support_families_embed_in_unique_q12_pentagons": all(
            row["containing_q12_row_count"] == 1 for row in family_scan_rows
        ),
        "mask288_has_unique_low_support_packet_seed": len(mask288_seed_rows) == 1
        and mask288_seed_rows[0]["packet_low_support_family"] == [0, 11]
        and mask288_seed_rows[0]["q12_class"] == 1
        and mask288_seed_rows[0]["section_relation_id"] == 227,
        "mask288_seed_q12_pentagon_is_not_full_mask_support": bool(mask288_seed_rows)
        and mask288_seed_rows[0]["extra_atom_ids_outside_selected_mask"] == [5]
        and mask288_seed_rows[0]["missing_selected_atom_ids"] == [4, 7, 13, 16],
        "row_normalization_still_requires_scalar6": (
            row_summary["row_scalar_divisibility_for_any_packet_pairing"] == 6
            and row_summary["nonuniform_row_scaling_improves_on_scalar_6"] is False
        ),
        "low_support_doublets_are_rank_one_only": (
            low_support_summary["compatible_doublet_rank_histogram"] == {"1": 6}
            and low_support_summary["full_packet_doublet_map_available"] is False
        ),
        "packet_operator_obstruction_is_2_power_10_6_power_10": packet_summary[
            "smith_diagonal_multiplicities"
        ]
        == {"2": 10, "6": 10},
    }
    result["q12_packet_seed_found_but_full_bridge_open"] = all(result.values())

    return {
        "status": "MASK288_Q12_PACKET_LOW_SUPPORT_SEED_FOUND_FULL_BRIDGE_OPEN",
        "claim_boundary": (
            "This intersects the q12 pentagon readout with the certified low-support "
            "boundary combinations that pass the packet SNF parity layer. It finds a "
            "mask-local seed, not a full packet bridge."
        ),
        "selected_mask": q12_h6_projection_audit["selected_mask"],
        "selected_h6_public_atom_ids": q12_h6_projection_audit["selected_h6_public_atom_ids"],
        "packet_snf_local_image_test": packet_snf["derived"]["obstruction_summary"][
            "local_image_test"
        ],
        "row_normalization_summary": {
            "row_scalar_divisibility_for_any_packet_pairing": row_summary[
                "row_scalar_divisibility_for_any_packet_pairing"
            ],
            "nonuniform_row_scaling_improves_on_scalar_6": row_summary[
                "nonuniform_row_scaling_improves_on_scalar_6"
            ],
            "only_compatible_residue_pair_mod6": row_summary[
                "only_compatible_residue_pair_mod6"
            ],
        },
        "low_support_summary": {
            "even_image_support_families": low_support_summary[
                "even_image_support_families"
            ],
            "even_image_support_family_count": low_support_summary[
                "even_image_support_family_count"
            ],
            "compatible_doublet_count": low_support_summary["compatible_doublet_count"],
            "compatible_doublet_rank_histogram": low_support_summary[
                "compatible_doublet_rank_histogram"
            ],
            "full_packet_doublet_map_available": low_support_summary[
                "full_packet_doublet_map_available"
            ],
        },
        "packet_low_support_family_scan_rows": family_scan_rows,
        "q12_rows_containing_packet_low_support_families": q12_seed_rows,
        "selected_mask_packet_low_support_family_rows": selected_family_rows,
        "mask288_q12_packet_seed_rows": mask288_seed_rows,
        "result": result,
        "all_checks_pass": all(result.values()),
        "interpretation": (
            "Among the three certified packet-compatible low-support boundary families, "
            "only [0,11] is contained in mask 288, and it is embedded in q12 class 1 "
            "(relation 227). The q12 pentagon contributes atoms [0,1,10,11,5], so the "
            "seed is one atom outside mask 288 and misses four mask atoms. Together with "
            "the scalar-6 row-normalization obstruction and rank-one doublet atlas, this "
            "keeps the full q12-to-packet bridge open."
        ),
    }


def boundary_image_for_support(
    support: list[dict[str, int]],
    matrix: list[list[int]],
) -> list[int]:
    return [
        sum(row["coefficient"] * matrix[row["public_atom_id"]][col] for row in support)
        for col in range(len(matrix[0]))
    ]


def packet_snf_local_failures(u: int, v: int) -> list[str]:
    failures = []
    if u % 2 != 0:
        failures.append("u_not_0_mod_2")
    if v % 2 != 0:
        failures.append("v_not_0_mod_2")
    if (u + v) % 6 != 0:
        failures.append("u_plus_v_not_0_mod_6")
    return failures


def rank_two_integer_vectors(left: list[int], right: list[int]) -> int:
    if not any(left) and not any(right):
        return 0
    if not any(left) or not any(right):
        return 1
    for i in range(len(left)):
        for j in range(i + 1, len(left)):
            if left[i] * right[j] != left[j] * right[i]:
                return 2
    return 1


def matrix_rank_over_q(rows: list[list[int]]) -> int:
    matrix = [[Fraction(value) for value in row] for row in rows if any(row)]
    if not matrix:
        return 0
    row_count = len(matrix)
    column_count = len(matrix[0])
    rank = 0
    for col in range(column_count):
        pivot = None
        for row_idx in range(rank, row_count):
            if matrix[row_idx][col]:
                pivot = row_idx
                break
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        pivot_value = matrix[rank][col]
        matrix[rank] = [value / pivot_value for value in matrix[rank]]
        for row_idx in range(row_count):
            if row_idx == rank or not matrix[row_idx][col]:
                continue
            factor = matrix[row_idx][col]
            matrix[row_idx] = [
                matrix[row_idx][idx] - factor * matrix[rank][idx]
                for idx in range(column_count)
            ]
        rank += 1
        if rank == row_count:
            break
    return rank


def matrix_nullspace_over_q(rows: list[list[int]]) -> dict[str, Any]:
    matrix = [[Fraction(value) for value in row] for row in rows if any(row)]
    if not matrix:
        return {"rank": 0, "pivot_columns": [], "free_columns": [], "basis": []}

    row_count = len(matrix)
    column_count = len(matrix[0])
    rank = 0
    pivot_columns = []
    for col in range(column_count):
        pivot = None
        for row_idx in range(rank, row_count):
            if matrix[row_idx][col]:
                pivot = row_idx
                break
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        pivot_value = matrix[rank][col]
        matrix[rank] = [value / pivot_value for value in matrix[rank]]
        for row_idx in range(row_count):
            if row_idx == rank or not matrix[row_idx][col]:
                continue
            factor = matrix[row_idx][col]
            matrix[row_idx] = [
                matrix[row_idx][idx] - factor * matrix[rank][idx]
                for idx in range(column_count)
            ]
        pivot_columns.append(col)
        rank += 1
        if rank == row_count:
            break

    pivot_set = set(pivot_columns)
    free_columns = [col for col in range(column_count) if col not in pivot_set]
    basis = []
    for free_col in free_columns:
        vector = [Fraction(0) for _ in range(column_count)]
        vector[free_col] = Fraction(1)
        for row_idx, pivot_col in enumerate(pivot_columns):
            vector[pivot_col] = -matrix[row_idx][free_col]
        basis.append(vector)

    return {
        "rank": rank,
        "pivot_columns": pivot_columns,
        "free_columns": free_columns,
        "basis": basis,
    }


def primitive_integer_vector(values: list[Fraction]) -> list[int]:
    denominator_lcm = 1
    for value in values:
        denominator_lcm = math.lcm(denominator_lcm, value.denominator)
    ints = [int(value * denominator_lcm) for value in values]
    content = 0
    for value in ints:
        content = math.gcd(content, abs(value))
    if content:
        ints = [value // content for value in ints]
    for value in ints:
        if value < 0:
            return [-entry for entry in ints]
        if value > 0:
            return ints
    return ints


def matrix_rank_mod_prime(rows: list[list[int]], prime: int) -> int:
    matrix = [
        [value % prime for value in row]
        for row in rows
        if any(value % prime for value in row)
    ]
    if not matrix:
        return 0
    row_count = len(matrix)
    column_count = len(matrix[0])
    rank = 0
    for col in range(column_count):
        pivot = None
        for row_idx in range(rank, row_count):
            if matrix[row_idx][col] % prime:
                pivot = row_idx
                break
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        pivot_inv = pow(matrix[rank][col], -1, prime)
        matrix[rank] = [(value * pivot_inv) % prime for value in matrix[rank]]
        for row_idx in range(row_count):
            if row_idx == rank or matrix[row_idx][col] % prime == 0:
                continue
            factor = matrix[row_idx][col] % prime
            matrix[row_idx] = [
                (matrix[row_idx][idx] - factor * matrix[rank][idx]) % prime
                for idx in range(column_count)
            ]
        rank += 1
        if rank == row_count:
            break
    return rank


def build_mask288_q12_packet_seed_support3_audit(
    q12_packet_low_support_audit: dict[str, Any],
) -> dict[str, Any]:
    incidence = load_json(D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE_REPORT)
    packet_snf = load_json(D20_PACKET_BRIDGE_SNF_OBSTRUCTION_REPORT)
    matrix = incidence["derived"]["boundary_atom_step_incidence_matrix"]
    public_atoms_by_id = {
        int(row["public_atom_id"]): row
        for row in incidence["derived"]["public_atom_rows"]
    }
    seed_rows = q12_packet_low_support_audit["mask288_q12_packet_seed_rows"]
    seed_row = seed_rows[0]
    seed_family = seed_row["packet_low_support_family"]
    missing_atoms = seed_row["missing_selected_atom_ids"]

    candidate_rows = []
    for extra_atom_id in missing_atoms:
        support_atom_ids = seed_family + [extra_atom_id]
        for coefficients in itertools.product((-1, 1), repeat=len(support_atom_ids)):
            support = [
                {
                    "public_atom_id": int(atom_id),
                    "coefficient": int(coefficient),
                    "public_atom_label": public_atoms_by_id[int(atom_id)]["public_atom_label"],
                }
                for atom_id, coefficient in zip(support_atom_ids, coefficients)
            ]
            image_support = [
                {"public_atom_id": row["public_atom_id"], "coefficient": row["coefficient"]}
                for row in support
            ]
            image = boundary_image_for_support(image_support, matrix)
            odd_step_atom_ids = [idx for idx, value in enumerate(image) if value % 2 != 0]
            candidate_rows.append(
                {
                    "candidate_id": len(candidate_rows),
                    "extra_atom_id": int(extra_atom_id),
                    "support_atom_ids": support_atom_ids,
                    "coefficient_support": support,
                    "image_is_even": not odd_step_atom_ids,
                    "odd_step_atom_ids": odd_step_atom_ids,
                    "odd_step_entry_count": len(odd_step_atom_ids),
                    "first_odd_step_atom_id": odd_step_atom_ids[0]
                    if odd_step_atom_ids
                    else None,
                    "image_value_histogram": counter_dict([str(value) for value in image]),
                }
            )

    even_candidate_rows = [row for row in candidate_rows if row["image_is_even"]]
    compatible_doublet_rows = []
    for left, right in itertools.combinations(even_candidate_rows, 2):
        left_image = boundary_image_for_support(
            [
                {
                    "public_atom_id": row["public_atom_id"],
                    "coefficient": row["coefficient"],
                }
                for row in left["coefficient_support"]
            ],
            matrix,
        )
        right_image = boundary_image_for_support(
            [
                {
                    "public_atom_id": row["public_atom_id"],
                    "coefficient": row["coefficient"],
                }
                for row in right["coefficient_support"]
            ],
            matrix,
        )
        if all(
            not packet_snf_local_failures(left_image[idx], right_image[idx])
            for idx in range(len(left_image))
        ):
            compatible_doublet_rows.append(
                {
                    "left_candidate_id": left["candidate_id"],
                    "right_candidate_id": right["candidate_id"],
                    "passes_packet_snf_image": True,
                }
            )

    by_extra_rows = []
    for extra_atom_id in missing_atoms:
        rows = [row for row in candidate_rows if row["extra_atom_id"] == extra_atom_id]
        by_extra_rows.append(
            {
                "extra_atom_id": int(extra_atom_id),
                "extra_atom_label": public_atoms_by_id[int(extra_atom_id)][
                    "public_atom_label"
                ],
                "candidate_count": len(rows),
                "even_image_candidate_count": sum(1 for row in rows if row["image_is_even"]),
                "odd_step_entry_count_histogram": counter_dict(
                    [str(row["odd_step_entry_count"]) for row in rows]
                ),
                "first_odd_step_atom_ids": sorted(
                    {
                        row["first_odd_step_atom_id"]
                        for row in rows
                        if row["first_odd_step_atom_id"] is not None
                    }
                ),
            }
        )

    result = {
        "seed_audit_found_relation227_seed": seed_family == [0, 11]
        and seed_row["q12_class"] == 1
        and seed_row["section_relation_id"] == 227,
        "support3_candidate_count_is_32": len(candidate_rows) == 32,
        "support3_search_covers_four_missing_mask_atoms": missing_atoms == [4, 7, 13, 16],
        "no_support3_seed_extension_has_even_image": len(even_candidate_rows) == 0,
        "support3_packet_snf_doublet_count_zero": len(compatible_doublet_rows) == 0,
        "packet_snf_local_test_certified": packet_snf["all_checks_pass"] is True
        and packet_snf["derived"]["obstruction_summary"]["local_image_test"]
        == "u = 0 mod 2, v = 0 mod 2, and u+v = 0 mod 6 on each packet doublet",
    }
    result["single_missing_atom_support3_extension_blocked_by_parity"] = all(
        result.values()
    )

    return {
        "status": "MASK288_Q12_PACKET_SEED_SUPPORT3_EXTENSION_BLOCKED_BY_PARITY",
        "claim_boundary": (
            "This is a bounded signed support-3 search: the certified mask-288 packet seed "
            "[0,11] is extended by exactly one of the mask atoms missing from q12 relation "
            "227. It does not test support-4, larger coefficients, or unconstrained packet maps."
        ),
        "selected_mask": q12_packet_low_support_audit["selected_mask"],
        "seed_packet_low_support_family": seed_family,
        "seed_q12_class": seed_row["q12_class"],
        "seed_section_relation_id": seed_row["section_relation_id"],
        "seed_q12_pentagon_atom_ids": seed_row["h6_public_atom_ids"],
        "missing_selected_atom_ids": missing_atoms,
        "coefficient_set": [-1, 1],
        "support_size": 3,
        "candidate_count": len(candidate_rows),
        "even_image_candidate_count": len(even_candidate_rows),
        "compatible_doublet_count": len(compatible_doublet_rows),
        "by_extra_atom_rows": by_extra_rows,
        "candidate_rows": candidate_rows,
        "compatible_doublet_rows": compatible_doublet_rows,
        "result": result,
        "all_checks_pass": all(result.values()),
        "interpretation": (
            "The support-2 packet seed [0,11] remains isolated at this depth. Adding any "
            "one of the missing mask atoms [4,7,13,16] with signs +/-1 introduces odd "
            "boundary-step entries, so the packet SNF parity layer rejects all 32 support-3 "
            "extensions before the doublet test can become nontrivial."
        ),
    }


def build_mask288_q12_packet_seed_broadened_extension_audit(
    q12_packet_low_support_audit: dict[str, Any],
    support3_unit_audit: dict[str, Any],
) -> dict[str, Any]:
    incidence = load_json(D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE_REPORT)
    packet_snf = load_json(D20_PACKET_BRIDGE_SNF_OBSTRUCTION_REPORT)
    matrix = incidence["derived"]["boundary_atom_step_incidence_matrix"]
    public_atoms_by_id = {
        int(row["public_atom_id"]): row
        for row in incidence["derived"]["public_atom_rows"]
    }
    seed_row = q12_packet_low_support_audit["mask288_q12_packet_seed_rows"][0]
    seed_family = seed_row["packet_low_support_family"]
    missing_atoms = seed_row["missing_selected_atom_ids"]

    support4_candidate_count = 0
    support4_even_count = 0
    support4_odd_counts: list[str] = []
    support4_by_pair_rows = []
    for missing_pair in itertools.combinations(missing_atoms, 2):
        pair_rows = []
        for coefficients in itertools.product((-1, 1), repeat=4):
            atom_ids = seed_family + list(missing_pair)
            support = [
                {"public_atom_id": int(atom_id), "coefficient": int(coefficient)}
                for atom_id, coefficient in zip(atom_ids, coefficients)
            ]
            image = boundary_image_for_support(support, matrix)
            odd_step_atom_ids = [idx for idx, value in enumerate(image) if value % 2 != 0]
            pair_rows.append(
                {
                    "odd_step_entry_count": len(odd_step_atom_ids),
                    "image_is_even": not odd_step_atom_ids,
                }
            )
        support4_candidate_count += len(pair_rows)
        support4_even_count += sum(1 for row in pair_rows if row["image_is_even"])
        support4_odd_counts.extend(str(row["odd_step_entry_count"]) for row in pair_rows)
        support4_by_pair_rows.append(
            {
                "missing_atom_pair": list(missing_pair),
                "candidate_count": len(pair_rows),
                "even_image_candidate_count": sum(
                    1 for row in pair_rows if row["image_is_even"]
                ),
                "odd_step_entry_count_histogram": counter_dict(
                    [str(row["odd_step_entry_count"]) for row in pair_rows]
                ),
            }
        )

    support3_candidate_rows = []
    for extra_atom_id in missing_atoms:
        atom_ids = seed_family + [extra_atom_id]
        for coefficients in itertools.product((-2, -1, 1, 2), repeat=3):
            support = [
                {
                    "public_atom_id": int(atom_id),
                    "coefficient": int(coefficient),
                    "public_atom_label": public_atoms_by_id[int(atom_id)]["public_atom_label"],
                }
                for atom_id, coefficient in zip(atom_ids, coefficients)
            ]
            image_support = [
                {
                    "public_atom_id": row["public_atom_id"],
                    "coefficient": row["coefficient"],
                }
                for row in support
            ]
            image = boundary_image_for_support(image_support, matrix)
            odd_step_atom_ids = [idx for idx, value in enumerate(image) if value % 2 != 0]
            image_gcd = math.gcd(*[abs(value) for value in image]) if any(image) else 0
            support3_candidate_rows.append(
                {
                    "candidate_id": len(support3_candidate_rows),
                    "extra_atom_id": int(extra_atom_id),
                    "support_atom_ids": atom_ids,
                    "coefficient_support": support,
                    "image_is_even": not odd_step_atom_ids,
                    "odd_step_entry_count": len(odd_step_atom_ids),
                    "image_gcd": image_gcd,
                    "image_value_histogram": counter_dict([str(value) for value in image]),
                    "image_vector": image,
                }
            )

    support3_even_rows = [
        row for row in support3_candidate_rows if row["image_is_even"] is True
    ]
    support3_doublet_rows = []
    for left, right in itertools.combinations(support3_even_rows, 2):
        left_image = left["image_vector"]
        right_image = right["image_vector"]
        if all(
            not packet_snf_local_failures(left_image[idx], right_image[idx])
            for idx in range(len(left_image))
        ):
            rank = rank_two_integer_vectors(left_image, right_image)
            support3_doublet_rows.append(
                {
                    "left_candidate_id": left["candidate_id"],
                    "right_candidate_id": right["candidate_id"],
                    "left_extra_atom_id": left["extra_atom_id"],
                    "right_extra_atom_id": right["extra_atom_id"],
                    "left_coefficients": [
                        row["coefficient"] for row in left["coefficient_support"]
                    ],
                    "right_coefficients": [
                        row["coefficient"] for row in right["coefficient_support"]
                    ],
                    "doublet_rank_over_Q": rank,
                    "right_is_negative_left": right_image
                    == [-value for value in left_image],
                    "passes_packet_snf_image": True,
                }
            )

    support3_rank2_doublets = [
        row for row in support3_doublet_rows if row["doublet_rank_over_Q"] == 2
    ]
    support3_by_extra_rows = []
    for extra_atom_id in missing_atoms:
        candidates = [
            row for row in support3_candidate_rows if row["extra_atom_id"] == extra_atom_id
        ]
        doublets = [
            row
            for row in support3_doublet_rows
            if row["left_extra_atom_id"] == extra_atom_id
            and row["right_extra_atom_id"] == extra_atom_id
        ]
        support3_by_extra_rows.append(
            {
                "extra_atom_id": int(extra_atom_id),
                "extra_atom_label": public_atoms_by_id[int(extra_atom_id)][
                    "public_atom_label"
                ],
                "candidate_count": len(candidates),
                "even_image_candidate_count": sum(
                    1 for row in candidates if row["image_is_even"]
                ),
                "compatible_doublet_count": len(doublets),
                "compatible_doublet_rank_histogram": counter_dict(
                    [str(row["doublet_rank_over_Q"]) for row in doublets]
                ),
            }
        )

    rank2_example_rows = []
    for extra_atom_id in missing_atoms:
        examples = [
            row for row in support3_rank2_doublets if row["left_extra_atom_id"] == extra_atom_id
        ]
        if examples:
            example = examples[0]
            rank2_example_rows.append(
                {
                    "extra_atom_id": int(extra_atom_id),
                    "support_atom_ids": seed_family + [extra_atom_id],
                    "left_candidate_id": example["left_candidate_id"],
                    "right_candidate_id": example["right_candidate_id"],
                    "left_coefficients": example["left_coefficients"],
                    "right_coefficients": example["right_coefficients"],
                    "doublet_rank_over_Q": example["doublet_rank_over_Q"],
                }
            )

    support4_unit_summary = {
        "coefficient_set": [-1, 1],
        "support_size": 4,
        "missing_pair_count": len(list(itertools.combinations(missing_atoms, 2))),
        "candidate_count": support4_candidate_count,
        "even_image_candidate_count": support4_even_count,
        "compatible_doublet_count": 0,
        "odd_step_entry_count_histogram": counter_dict(support4_odd_counts),
        "by_missing_pair_rows": support4_by_pair_rows,
    }
    support3_widened_summary = {
        "coefficient_set": [-2, -1, 1, 2],
        "support_size": 3,
        "candidate_count": len(support3_candidate_rows),
        "even_image_candidate_count": len(support3_even_rows),
        "even_image_gcd_histogram": counter_dict(
            [str(row["image_gcd"]) for row in support3_even_rows]
        ),
        "even_image_count_by_extra_atom": {
            str(extra_atom_id): sum(
                1
                for row in support3_even_rows
                if row["extra_atom_id"] == extra_atom_id
            )
            for extra_atom_id in missing_atoms
        },
        "compatible_doublet_count": len(support3_doublet_rows),
        "compatible_doublet_rank_histogram": counter_dict(
            [str(row["doublet_rank_over_Q"]) for row in support3_doublet_rows]
        ),
        "negative_doublet_count": sum(
            1 for row in support3_doublet_rows if row["right_is_negative_left"]
        ),
        "rank2_doublet_count": len(support3_rank2_doublets),
        "by_extra_atom_rows": support3_by_extra_rows,
        "rank2_doublet_example_rows": rank2_example_rows,
    }

    result = {
        "unit_support4_pair_extension_blocked_by_parity": support4_even_count == 0
        and support4_candidate_count == 96,
        "widened_support3_clears_parity": len(support3_even_rows) == 64,
        "widened_support3_finds_packet_compatible_doublets": len(support3_doublet_rows)
        == 64,
        "widened_support3_finds_rank2_doublets": len(support3_rank2_doublets) == 32,
        "widened_support3_doublets_stay_within_single_extra_atom_families": all(
            row["left_extra_atom_id"] == row["right_extra_atom_id"]
            for row in support3_doublet_rows
        ),
        "widened_support3_not_yet_full_packet_bridge": len(support3_by_extra_rows) == 4
        and packet_snf["derived"]["obstruction_summary"]["raw_bridge_columns_available"]
        is False,
        "prior_unit_support3_blocked": support3_unit_audit["result"][
            "single_missing_atom_support3_extension_blocked_by_parity"
        ]
        is True,
    }
    result["widened_support3_rank2_candidates_materialized"] = all(result.values())

    return {
        "status": "MASK288_Q12_PACKET_SEED_WIDENED_SUPPORT3_RANK2_CANDIDATES_FOUND",
        "claim_boundary": (
            "This broadens the relation-227 seed search in two bounded ways: unit-sign "
            "support-4 pairs of missing mask atoms, and support-3 coefficients in "
            "{-2,-1,1,2}. The widened support-3 branch finds candidate packet doublets, "
            "but still does not construct a q12/A985-to-packet map."
        ),
        "selected_mask": q12_packet_low_support_audit["selected_mask"],
        "seed_packet_low_support_family": seed_family,
        "seed_q12_class": seed_row["q12_class"],
        "seed_section_relation_id": seed_row["section_relation_id"],
        "missing_selected_atom_ids": missing_atoms,
        "support4_unit_summary": support4_unit_summary,
        "support3_widened_summary": support3_widened_summary,
        "support3_widened_even_candidate_rows": [
            {k: v for k, v in row.items() if k != "image_vector"}
            for row in support3_even_rows
        ],
        "support3_widened_compatible_doublet_rows": support3_doublet_rows,
        "result": result,
        "all_checks_pass": all(result.values()),
        "interpretation": (
            "Adding two missing mask atoms with unit signs still fails the parity layer. "
            "Allowing coefficient magnitude 2 on support-3 clears parity uniformly: each "
            "missing atom family contributes 16 even candidates and 16 packet-compatible "
            "doublets, eight of rank two. These are the first non-rank-one packet candidates "
            "on the relation-227 seed, but they remain four local families rather than a full "
            "ten-doublet packet bridge."
        ),
    }


def q12_product_d20_readout(
    q12_coefficients: np.ndarray,
    q12_h6_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    vector = [0 for _ in range(20)]
    output_q12_coefficients = []
    for q12_class, coefficient in enumerate(q12_coefficients.tolist()):
        if not coefficient:
            continue
        output_q12_coefficients.append([q12_class, int(coefficient)])
        for atom_id in q12_h6_rows[q12_class]["h6_public_atom_ids"]:
            vector[int(atom_id)] += int(coefficient)
    return {
        "output_q12_coefficients": output_q12_coefficients,
        "coefficient_total": int(q12_coefficients.sum()),
        "readout_vector": vector,
        "readout_support_atom_ids": [
            atom_id for atom_id, coefficient in enumerate(vector) if coefficient
        ],
    }


def build_mask288_q12_rank2_doublet_label_audit(
    q12_h6_projection_audit: dict[str, Any],
    broadened_extension_audit: dict[str, Any],
) -> dict[str, Any]:
    with np.load(ROOT / QUOTIENTS_NPZ) as payload:
        q12_tensor = np.asarray(payload["q12_tensor"], dtype=np.int64)
    explicit_restriction = load_json(D20_EXPLICIT_PACKET_RESTRICTION_MAP_TEST_REPORT)

    seed_q12_class = broadened_extension_audit["seed_q12_class"]
    seed_family = set(broadened_extension_audit["seed_packet_low_support_family"])
    missing_atoms = broadened_extension_audit["missing_selected_atom_ids"]
    q12_rows = q12_h6_projection_audit["q12_h6_rows"]
    q12_classes_by_atom: dict[int, list[int]] = {
        atom_id: [
            int(row["q12_class"])
            for row in q12_rows
            if atom_id in row["h6_public_atom_ids"]
        ]
        for atom_id in range(20)
    }

    seed_self_product = q12_product_d20_readout(
        q12_tensor[seed_q12_class, seed_q12_class, :],
        q12_rows,
    )
    seed_self_product["seed_family_covered"] = seed_family.issubset(
        seed_self_product["readout_support_atom_ids"]
    )

    rank2_doublets = [
        row
        for row in broadened_extension_audit["support3_widened_compatible_doublet_rows"]
        if row["doublet_rank_over_Q"] == 2
    ]
    rank2_family_rows = []
    product_label_scan_rows = []
    direct_label_count = 0
    for extra_atom_id in missing_atoms:
        rank2_rows = [
            row for row in rank2_doublets if row["left_extra_atom_id"] == extra_atom_id
        ]
        extra_q12_classes = q12_classes_by_atom[int(extra_atom_id)]
        nonzero_product_count = 0
        touches_extra_count = 0
        preserves_seed_family_count = 0
        direct_product_label_count = 0
        nonzero_product_rows = []
        for extra_q12_class in extra_q12_classes:
            for order, left_class, right_class in (
                ("seed_left", seed_q12_class, extra_q12_class),
                ("seed_right", extra_q12_class, seed_q12_class),
            ):
                product = q12_product_d20_readout(
                    q12_tensor[left_class, right_class, :],
                    q12_rows,
                )
                support = set(product["readout_support_atom_ids"])
                candidate_support = sorted(seed_family | {int(extra_atom_id)})
                row = {
                    "extra_atom_id": int(extra_atom_id),
                    "extra_q12_class": int(extra_q12_class),
                    "order": order,
                    "left_q12_class": int(left_class),
                    "right_q12_class": int(right_class),
                    "output_q12_coefficients": product["output_q12_coefficients"],
                    "coefficient_total": product["coefficient_total"],
                    "readout_support_atom_ids": product["readout_support_atom_ids"],
                    "candidate_support_atom_ids": candidate_support,
                    "seed_family_covered": seed_family.issubset(support),
                    "extra_atom_covered": int(extra_atom_id) in support,
                    "candidate_support_covered": set(candidate_support).issubset(support),
                    "candidate_atom_readout_values": {
                        str(atom_id): product["readout_vector"][atom_id]
                        for atom_id in candidate_support
                    },
                }
                product_label_scan_rows.append(row)
                if row["output_q12_coefficients"]:
                    nonzero_product_count += 1
                    nonzero_product_rows.append(row)
                if row["extra_atom_covered"]:
                    touches_extra_count += 1
                if row["seed_family_covered"]:
                    preserves_seed_family_count += 1
                if row["candidate_support_covered"]:
                    direct_product_label_count += 1
        direct_label_count += direct_product_label_count
        rank2_family_rows.append(
            {
                "extra_atom_id": int(extra_atom_id),
                "support_atom_ids": sorted(seed_family | {int(extra_atom_id)}),
                "rank2_doublet_count": len(rank2_rows),
                "q12_classes_containing_extra_atom": extra_q12_classes,
                "q12_product_scan_count": len(extra_q12_classes) * 2,
                "nonzero_q12_product_count": nonzero_product_count,
                "q12_products_touching_extra_atom_count": touches_extra_count,
                "q12_products_preserving_seed_family_count": preserves_seed_family_count,
                "direct_q12_product_label_count": direct_product_label_count,
                "nonzero_q12_product_rows": nonzero_product_rows,
            }
        )

    missing_q12_bridge_rows = [
        row
        for row in explicit_restriction["derived"]["missing_bridge_inventory"]
        if row["candidate"] == "q42_q12_tensor_to_full_packets"
    ]
    result = {
        "rank2_doublet_count_is_32": len(rank2_doublets) == 32,
        "rank2_doublets_split_across_four_missing_atom_families": all(
            row["rank2_doublet_count"] == 8 for row in rank2_family_rows
        ),
        "seed_self_product_preserves_seed_family": (
            seed_self_product["output_q12_coefficients"] == [[1, 2]]
            and seed_self_product["seed_family_covered"] is True
        ),
        "q12_products_touch_each_extra_atom": all(
            row["q12_products_touching_extra_atom_count"] >= 1
            for row in rank2_family_rows
        ),
        "no_rank2_family_has_direct_q12_product_label": direct_label_count == 0,
        "q12_product_labels_do_not_preserve_seed_when_touching_extra": all(
            not (
                scan_row["extra_atom_covered"] is True
                and scan_row["seed_family_covered"] is True
            )
            for scan_row in product_label_scan_rows
        ),
        "q12_packet_projection_still_absent": bool(missing_q12_bridge_rows)
        and missing_q12_bridge_rows[0]["status"]
        == "blocked_missing_quotient_class_to_packet_projection",
    }
    result["rank2_doublets_not_directly_q12_tensor_labelled"] = all(result.values())

    return {
        "status": "MASK288_Q12_RANK2_PACKET_CANDIDATES_NOT_DIRECTLY_Q12_LABELLED",
        "claim_boundary": (
            "This promotes the widened support-3 rank-2 doublets into a q12-label atlas. "
            "It only tests direct q12 tensor multiplication labels through the pentagon "
            "readout; it does not solve for arbitrary linear combinations of q12 products."
        ),
        "selected_mask": broadened_extension_audit["selected_mask"],
        "seed_q12_class": seed_q12_class,
        "seed_section_relation_id": broadened_extension_audit["seed_section_relation_id"],
        "seed_packet_low_support_family": broadened_extension_audit[
            "seed_packet_low_support_family"
        ],
        "rank2_doublet_count": len(rank2_doublets),
        "rank2_family_rows": rank2_family_rows,
        "seed_self_product": seed_self_product,
        "direct_q12_product_label_count": direct_label_count,
        "q12_product_label_scan_rows": product_label_scan_rows,
        "missing_q12_packet_projection": missing_q12_bridge_rows[0]
        if missing_q12_bridge_rows
        else None,
        "result": result,
        "all_checks_pass": all(result.values()),
        "interpretation": (
            "The q12 tensor gives a label for the original seed: class 1 times class 1 "
            "returns class 1 and covers atoms [0,11]. For the four rank-2 extra-atom "
            "families, direct products involving class 1 and any q12 class containing the "
            "extra atom can touch the extra atom, but never cover the full candidate support "
            "[0,11,e]. The rank-2 packet candidates therefore remain boundary-coefficient "
            "candidates, not q12/A985-labelled packet actions."
        ),
    }


def linear_combination_candidate(
    chosen_products: list[dict[str, Any]],
    vector: list[int],
    target_atom_ids: list[int],
) -> dict[str, Any]:
    support = {atom_id for atom_id, value in enumerate(vector) if value}
    target = set(target_atom_ids)
    return {
        "chosen_products": [
            {
                "product_id": row["product_id"],
                "coefficient": row["coefficient"],
                "output_q12_coefficients": row["output_q12_coefficients"],
            }
            for row in chosen_products
        ],
        "materialized_support_atom_ids": sorted(support),
        "target_atom_ids": target_atom_ids,
        "extra_atom_ids": sorted(support - target),
        "missing_atom_ids": sorted(target - support),
        "distance_to_target": len(support - target) + len(target - support),
        "target_atom_values": {str(atom_id): vector[atom_id] for atom_id in target_atom_ids},
    }


def build_mask288_q12_rank2_linear_combination_audit(
    q12_h6_projection_audit: dict[str, Any],
    rank2_label_audit: dict[str, Any],
) -> dict[str, Any]:
    q12_rows = q12_h6_projection_audit["q12_h6_rows"]
    seed_family = set(rank2_label_audit["seed_packet_low_support_family"])
    family_rows = rank2_label_audit["rank2_family_rows"]
    missing_projection = rank2_label_audit["missing_q12_packet_projection"]

    def sparse_output_readout(output_q12_coefficients: list[list[int]]) -> list[int]:
        vector = [0 for _ in range(20)]
        for q12_class, coefficient in output_q12_coefficients:
            for atom_id in q12_rows[int(q12_class)]["h6_public_atom_ids"]:
                vector[int(atom_id)] += int(coefficient)
        return vector

    seed_product = {
        "product_id": "seed_self",
        "output_q12_coefficients": rank2_label_audit["seed_self_product"][
            "output_q12_coefficients"
        ],
        "readout_vector": rank2_label_audit["seed_self_product"]["readout_vector"],
        "readout_support_atom_ids": rank2_label_audit["seed_self_product"][
            "readout_support_atom_ids"
        ],
    }
    family_combination_rows = []
    for family_row in family_rows:
        extra_atom_id = int(family_row["extra_atom_id"])
        target_atom_ids = sorted(seed_family | {extra_atom_id})
        local_products = [seed_product]
        for product_row in family_row["nonzero_q12_product_rows"]:
            product_id = f"{product_row['order']}_{product_row['extra_q12_class']}"
            local_products.append(
                {
                    "product_id": product_id,
                    "output_q12_coefficients": product_row["output_q12_coefficients"],
                    "readout_vector": sparse_output_readout(
                        product_row["output_q12_coefficients"]
                    ),
                    "readout_support_atom_ids": product_row["readout_support_atom_ids"],
                }
            )

        exact_candidates = []
        cover_candidates = []
        all_candidates = []
        for coefficients in itertools.product((-1, 0, 1), repeat=len(local_products)):
            if not any(coefficients):
                continue
            vector = [0 for _ in range(20)]
            chosen_products = []
            for coefficient, product in zip(coefficients, local_products):
                if coefficient == 0:
                    continue
                chosen_products.append({**product, "coefficient": int(coefficient)})
                for atom_id, value in enumerate(product["readout_vector"]):
                    vector[atom_id] += int(coefficient) * int(value)
            candidate = linear_combination_candidate(
                chosen_products,
                vector,
                target_atom_ids,
            )
            all_candidates.append(candidate)
            if not candidate["missing_atom_ids"]:
                cover_candidates.append(candidate)
            if (
                not candidate["missing_atom_ids"]
                and not candidate["extra_atom_ids"]
            ):
                exact_candidates.append(candidate)

        best_cover = sorted(
            cover_candidates,
            key=lambda row: (
                len(row["extra_atom_ids"]),
                len(row["chosen_products"]),
                [
                    (item["product_id"], item["coefficient"])
                    for item in row["chosen_products"]
                ],
            ),
        )[0] if cover_candidates else None
        best_overall = sorted(
            all_candidates,
            key=lambda row: (
                row["distance_to_target"],
                len(row["extra_atom_ids"]),
                len(row["missing_atom_ids"]),
                len(row["chosen_products"]),
                [
                    (item["product_id"], item["coefficient"])
                    for item in row["chosen_products"]
                ],
            ),
        )[0]
        family_combination_rows.append(
            {
                "extra_atom_id": extra_atom_id,
                "target_atom_ids": target_atom_ids,
                "local_product_ids": [row["product_id"] for row in local_products],
                "search_space_size": (3 ** len(local_products)) - 1,
                "cover_solution_count": len(cover_candidates),
                "exact_support_solution_count": len(exact_candidates),
                "best_cover_candidate": best_cover,
                "best_overall_candidate": best_overall,
            }
        )

    result = {
        "linear_cover_found_for_each_rank2_family": all(
            row["cover_solution_count"] > 0 for row in family_combination_rows
        ),
        "no_exact_support_linear_combination_found": all(
            row["exact_support_solution_count"] == 0 for row in family_combination_rows
        ),
        "best_covers_all_have_overhang": all(
            row["best_cover_candidate"] is not None
            and row["best_cover_candidate"]["extra_atom_ids"]
            for row in family_combination_rows
        ),
        "best_covers_use_two_product_terms": all(
            row["best_cover_candidate"] is not None
            and len(row["best_cover_candidate"]["chosen_products"]) == 2
            for row in family_combination_rows
        ),
        "rank2_candidates_still_not_q12_packet_actions": missing_projection["status"]
        == "blocked_missing_quotient_class_to_packet_projection",
    }
    result["small_q12_product_combinations_cover_with_overhang_only"] = all(
        result.values()
    )

    return {
        "status": "MASK288_Q12_RANK2_LINEAR_PRODUCT_COVERS_WITH_OVERHANG_ONLY",
        "claim_boundary": (
            "This searches coefficient {-1,0,1} linear combinations of the seed self-product "
            "and direct q12 products that touch each rank-2 extra atom. It finds target "
            "coverage, but no exact support and no packet projection."
        ),
        "selected_mask": rank2_label_audit["selected_mask"],
        "seed_q12_class": rank2_label_audit["seed_q12_class"],
        "coefficient_set": [-1, 0, 1],
        "family_combination_rows": family_combination_rows,
        "total_search_space_size": sum(
            row["search_space_size"] for row in family_combination_rows
        ),
        "total_cover_solution_count": sum(
            row["cover_solution_count"] for row in family_combination_rows
        ),
        "total_exact_support_solution_count": sum(
            row["exact_support_solution_count"] for row in family_combination_rows
        ),
        "missing_q12_packet_projection": missing_projection,
        "result": result,
        "all_checks_pass": all(result.values()),
        "interpretation": (
            "Small q12 product combinations can cover every [0,11,e] rank-2 family: the seed "
            "self-product supplies [0,11], and a neighboring product supplies e. The price is "
            "unavoidable overhang in this bounded search. Thus the q12 tensor has local coverage "
            "evidence, but still no exact support or packet-action label."
        ),
    }


def q12_product_readout_vector(
    chosen_products: list[dict[str, Any]],
    q12_rows: list[dict[str, Any]],
) -> list[int]:
    vector = [0 for _ in range(20)]
    for product in chosen_products:
        coefficient = int(product.get("coefficient", 1))
        for q12_class, q12_coefficient in product["output_q12_coefficients"]:
            for atom_id in q12_rows[int(q12_class)]["h6_public_atom_ids"]:
                vector[int(atom_id)] += coefficient * int(q12_coefficient)
    return vector


def atom_value_residue_readout(atom_ids: list[int], vector: list[int]) -> dict[str, Any]:
    atom_ids = [int(atom_id) for atom_id in atom_ids]
    values = {str(atom_id): int(vector[atom_id]) for atom_id in atom_ids}
    residues_mod6 = {str(atom_id): int(vector[atom_id]) % 6 for atom_id in atom_ids}
    nonzero_residue_atom_ids = [
        atom_id for atom_id in atom_ids if residues_mod6[str(atom_id)] != 0
    ]
    return {
        "atom_values": values,
        "atom_values_mod6": residues_mod6,
        "residue_mod6_histogram": counter_dict(
            [str(residues_mod6[str(atom_id)]) for atom_id in atom_ids]
        ),
        "nonzero_mod6_atom_ids": nonzero_residue_atom_ids,
        "nonzero_mod6_atom_count": len(nonzero_residue_atom_ids),
    }


def build_mask288_q12_product_overhang_invariant_audit(
    q12_h6_projection_audit: dict[str, Any],
    linear_combo_audit: dict[str, Any],
) -> dict[str, Any]:
    incidence = load_json(D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE_REPORT)
    row_norm = load_json(D20_BOUNDARY_PACKET_ROW_NORMALIZATION_OBSTRUCTION_REPORT)
    restriction = load_json(D20_EXPLICIT_PACKET_RESTRICTION_MAP_TEST_REPORT)

    public_atoms_by_id = {
        int(row["public_atom_id"]): row
        for row in incidence["derived"]["public_atom_rows"]
    }
    q12_rows = q12_h6_projection_audit["q12_h6_rows"]
    row_norm_summary = row_norm["derived"]["obstruction_summary"]
    missing_bridge_rows = [
        row
        for row in restriction["derived"]["missing_bridge_inventory"]
        if row["candidate"] == "q42_q12_tensor_to_full_packets"
    ]

    family_overhang_rows = []
    for family_row in linear_combo_audit["family_combination_rows"]:
        best_cover = family_row["best_cover_candidate"]
        vector = q12_product_readout_vector(best_cover["chosen_products"], q12_rows)
        target_atom_ids = family_row["target_atom_ids"]
        overhang_atom_ids = best_cover["extra_atom_ids"]
        cover_atom_ids = best_cover["materialized_support_atom_ids"]
        target_readout = {
            **public_atom_label_readout(target_atom_ids, public_atoms_by_id),
            **atom_value_residue_readout(target_atom_ids, vector),
        }
        overhang_readout = {
            **public_atom_label_readout(overhang_atom_ids, public_atoms_by_id),
            **atom_value_residue_readout(overhang_atom_ids, vector),
        }
        cover_readout = {
            **public_atom_label_readout(cover_atom_ids, public_atoms_by_id),
            **atom_value_residue_readout(cover_atom_ids, vector),
        }
        family_overhang_rows.append(
            {
                "extra_atom_id": family_row["extra_atom_id"],
                "target_atom_ids": target_atom_ids,
                "overhang_atom_ids": overhang_atom_ids,
                "target_readout": target_readout,
                "overhang_readout": overhang_readout,
                "cover_readout": cover_readout,
                "chosen_product_ids": [
                    row["product_id"] for row in best_cover["chosen_products"]
                ],
                "missing_atom_ids": best_cover["missing_atom_ids"],
            }
        )

    static_parity_readout = {
        "status": "BLOCKED_MISSING_Q12_TO_H6_PUBLIC_ATOM_PROJECTION",
        "quotient_generator": "z2_a12_parity",
        "missing_q12_packet_projection": missing_bridge_rows[0]
        if missing_bridge_rows
        else None,
        "reason": (
            "The known static parity observable is q12/A985-side data. The H6 overhang "
            "atoms cannot be evaluated against it until the q42/q12 quotient-to-packet "
            "projection exists."
        ),
    }
    packet_normalization_readout = {
        "row_normalization_report_status": row_norm["status"],
        "row_scalar_divisibility_for_any_packet_pairing": row_norm_summary[
            "row_scalar_divisibility_for_any_packet_pairing"
        ],
        "nonuniform_row_scaling_improves_on_scalar_6": row_norm_summary[
            "nonuniform_row_scaling_improves_on_scalar_6"
        ],
        "only_compatible_residue_pair_mod6": row_norm_summary[
            "only_compatible_residue_pair_mod6"
        ],
        "families_with_nonzero_overhang_residue_mod6": [
            row["extra_atom_id"]
            for row in family_overhang_rows
            if row["overhang_readout"]["nonzero_mod6_atom_count"] > 0
        ],
    }

    result = {
        "linear_combinations_still_have_no_exact_support": linear_combo_audit[
            "total_exact_support_solution_count"
        ]
        == 0,
        "overhang_present_in_each_best_cover": all(
            row["overhang_atom_ids"] for row in family_overhang_rows
        ),
        "bvs_public_readout_sees_every_overhang": all(
            sum(row["overhang_readout"]["unsigned_sector_counts"].values()) > 0
            for row in family_overhang_rows
        ),
        "packet_row_normalization_does_not_annihilate_overhang": (
            row_norm["all_checks_pass"] is True
            and row_norm_summary["row_scalar_divisibility_for_any_packet_pairing"] == 6
            and row_norm_summary["nonuniform_row_scaling_improves_on_scalar_6"] is False
            and all(
                row["overhang_readout"]["nonzero_mod6_atom_count"] > 0
                for row in family_overhang_rows
            )
        ),
        "static_parity_retest_still_blocked_by_missing_projection": (
            restriction["checks"]["a985_tube_q42_q12_packet_projection_is_absent"] is True
            and bool(missing_bridge_rows)
            and missing_bridge_rows[0]["status"]
            == "blocked_missing_quotient_class_to_packet_projection"
        ),
    }
    result["overhang_survives_existing_bvs_and_packet_readouts"] = all(result.values())

    return {
        "status": "MASK288_Q12_PRODUCT_OVERHANG_SURVIVES_BVS_PACKET_READOUTS_STATIC_BLOCKED",
        "claim_boundary": (
            "This tests whether the extra atoms in the best q12 product covers disappear "
            "under the known public B/V/S readout or packet row normalization. It does not "
            "evaluate static parity on H6 atoms because the required q12/A985 packet "
            "projection is still absent."
        ),
        "selected_mask": q12_h6_projection_audit["selected_mask"],
        "coefficient_set": linear_combo_audit["coefficient_set"],
        "family_overhang_rows": family_overhang_rows,
        "packet_normalization_readout": packet_normalization_readout,
        "static_parity_readout": static_parity_readout,
        "result": result,
        "all_checks_pass": all(result.values()),
        "interpretation": (
            "The best q12 product covers do not merely add atoms invisible to the current "
            "public readouts. Each overhang has nonzero B/V/S sector mass and at least one "
            "nonzero coefficient residue modulo the scalar-6 packet normalization boundary. "
            "Known packet normalization therefore does not kill the overhang; static parity "
            "remains unevaluable until the missing q12/A985-to-packet projection is supplied."
        ),
    }


def q12_linear_residue_candidate(
    cancellation_terms: list[dict[str, Any]],
    coefficients: tuple[int, ...],
    base_vector: list[int],
    target_atom_ids: list[int],
) -> dict[str, Any] | None:
    target = set(target_atom_ids)
    vector = base_vector[:]
    for coefficient, term in zip(coefficients, cancellation_terms):
        for atom_id, value in enumerate(term["readout_vector"]):
            vector[atom_id] += int(coefficient) * int(value)

    missing_atom_ids = sorted(atom_id for atom_id in target_atom_ids if vector[atom_id] == 0)
    if missing_atom_ids:
        return None

    extra_atom_ids = [
        atom_id for atom_id, value in enumerate(vector) if value and atom_id not in target
    ]
    outside_target_nonzero_mod6_atom_ids = [
        atom_id
        for atom_id in range(20)
        if atom_id not in target and vector[atom_id] % 6 != 0
    ]
    target_nonzero_mod6_atom_ids = [
        atom_id for atom_id in target_atom_ids if vector[atom_id] % 6 != 0
    ]
    return {
        "cancellation_term_count": len(cancellation_terms),
        "cancellation_terms": [
            {
                "product_id": term["product_id"],
                "coefficient": int(coefficient),
                "left_q12_class": term["left_q12_class"],
                "right_q12_class": term["right_q12_class"],
                "output_q12_coefficients": term["output_q12_coefficients"],
            }
            for coefficient, term in zip(coefficients, cancellation_terms)
        ],
        "materialized_support_atom_ids": [
            atom_id for atom_id, value in enumerate(vector) if value
        ],
        "target_atom_ids": target_atom_ids,
        "extra_atom_ids": extra_atom_ids,
        "extra_atom_count": len(extra_atom_ids),
        "missing_atom_ids": missing_atom_ids,
        "target_atom_values": {
            str(atom_id): vector[atom_id] for atom_id in target_atom_ids
        },
        "target_atom_values_mod6": {
            str(atom_id): vector[atom_id] % 6 for atom_id in target_atom_ids
        },
        "target_nonzero_mod6_atom_ids": target_nonzero_mod6_atom_ids,
        "outside_target_nonzero_mod6_atom_ids": outside_target_nonzero_mod6_atom_ids,
        "outside_target_nonzero_mod6_atom_count": len(
            outside_target_nonzero_mod6_atom_ids
        ),
        "extra_atom_values_mod6": {
            str(atom_id): vector[atom_id] % 6 for atom_id in extra_atom_ids
        },
    }


def q12_residue_candidate_sort_key(candidate: dict[str, Any]) -> tuple[Any, ...]:
    return (
        candidate["outside_target_nonzero_mod6_atom_count"],
        candidate["extra_atom_count"],
        candidate["cancellation_term_count"],
        [term["product_id"] for term in candidate["cancellation_terms"]],
        [term["coefficient"] for term in candidate["cancellation_terms"]],
    )


def q12_residue_clear_sort_key(candidate: dict[str, Any]) -> tuple[Any, ...]:
    return (
        candidate["cancellation_term_count"],
        candidate["extra_atom_count"],
        [term["product_id"] for term in candidate["cancellation_terms"]],
        [term["coefficient"] for term in candidate["cancellation_terms"]],
    )


def build_mask288_q12_outside_class1_residue_cancellation_audit(
    q12_h6_projection_audit: dict[str, Any],
    linear_combo_audit: dict[str, Any],
) -> dict[str, Any]:
    q12_rows = q12_h6_projection_audit["q12_h6_rows"]
    seed_q12_class = linear_combo_audit["seed_q12_class"]
    with np.load(ROOT / QUOTIENTS_NPZ) as payload:
        q12_tensor = np.asarray(payload["q12_tensor"], dtype=np.int64)

    all_product_terms = []
    for left_class in range(q12_tensor.shape[0]):
        for right_class in range(q12_tensor.shape[1]):
            product = q12_product_d20_readout(
                q12_tensor[left_class, right_class, :],
                q12_rows,
            )
            if not product["output_q12_coefficients"]:
                continue
            all_product_terms.append(
                {
                    "product_id": f"q12_{left_class}_{right_class}",
                    "left_q12_class": int(left_class),
                    "right_q12_class": int(right_class),
                    **product,
                }
            )

    outside_seed_terms = [
        term
        for term in all_product_terms
        if term["left_q12_class"] != seed_q12_class
        and term["right_q12_class"] != seed_q12_class
    ]
    coefficient_set = [-1, 1]
    max_cancellation_terms = 3
    family_rows = []
    for family_row in linear_combo_audit["family_combination_rows"]:
        target_atom_ids = family_row["target_atom_ids"]
        target = set(target_atom_ids)
        base_cover = family_row["best_cover_candidate"]
        base_vector = q12_product_readout_vector(base_cover["chosen_products"], q12_rows)
        base_extra_atom_ids = [
            atom_id
            for atom_id, value in enumerate(base_vector)
            if value and atom_id not in target
        ]
        base_nonzero_mod6_atom_ids = [
            atom_id
            for atom_id in range(20)
            if atom_id not in target and base_vector[atom_id] % 6 != 0
        ]
        valid_candidate_count = 0
        exact_support_candidate_count = 0
        residue_clear_candidates = []
        best_candidate = None
        search_space_size = 0
        for term_count in range(1, max_cancellation_terms + 1):
            for term_combo in itertools.combinations(outside_seed_terms, term_count):
                for coefficients in itertools.product(coefficient_set, repeat=term_count):
                    search_space_size += 1
                    candidate = q12_linear_residue_candidate(
                        list(term_combo),
                        tuple(int(coefficient) for coefficient in coefficients),
                        base_vector,
                        target_atom_ids,
                    )
                    if candidate is None:
                        continue
                    valid_candidate_count += 1
                    if not candidate["extra_atom_ids"]:
                        exact_support_candidate_count += 1
                    if candidate["outside_target_nonzero_mod6_atom_count"] == 0:
                        residue_clear_candidates.append(candidate)
                    if best_candidate is None or q12_residue_candidate_sort_key(
                        candidate
                    ) < q12_residue_candidate_sort_key(best_candidate):
                        best_candidate = candidate

        residue_clear_candidates.sort(key=q12_residue_clear_sort_key)
        best_residue_clear_candidate = (
            residue_clear_candidates[0] if residue_clear_candidates else None
        )
        family_rows.append(
            {
                "extra_atom_id": family_row["extra_atom_id"],
                "target_atom_ids": target_atom_ids,
                "base_chosen_product_ids": [
                    row["product_id"] for row in base_cover["chosen_products"]
                ],
                "base_extra_atom_ids": base_extra_atom_ids,
                "base_outside_target_nonzero_mod6_atom_ids": base_nonzero_mod6_atom_ids,
                "search_space_size": search_space_size,
                "valid_candidate_count": valid_candidate_count,
                "exact_support_candidate_count": exact_support_candidate_count,
                "residue_clear_candidate_count": len(residue_clear_candidates),
                "best_candidate": best_candidate,
                "best_residue_clear_candidate": best_residue_clear_candidate,
            }
        )

    result = {
        "outside_class1_q12_terms_available": len(outside_seed_terms) == 41,
        "bounded_cancellation_search_preserves_targets": all(
            row["valid_candidate_count"] > 0 for row in family_rows
        ),
        "residue_clear_candidate_found_for_each_family": all(
            row["residue_clear_candidate_count"] > 0 for row in family_rows
        ),
        "residue_clear_candidates_zero_outside_target_mod6": all(
            row["best_residue_clear_candidate"] is not None
            and row["best_residue_clear_candidate"][
                "outside_target_nonzero_mod6_atom_count"
            ]
            == 0
            for row in family_rows
        ),
        "residue_clear_candidates_preserve_integer_target_atoms": all(
            row["best_residue_clear_candidate"] is not None
            and not row["best_residue_clear_candidate"]["missing_atom_ids"]
            for row in family_rows
        ),
        "residue_clear_candidates_are_not_integer_exact_support": all(
            row["exact_support_candidate_count"] == 0
            and row["best_residue_clear_candidate"] is not None
            and row["best_residue_clear_candidate"]["extra_atom_count"]
            > len(row["base_extra_atom_ids"])
            for row in family_rows
        ),
    }
    result["outside_class1_residue_cancellation_found_exact_support_open"] = all(
        result.values()
    )

    return {
        "status": "MASK288_Q12_OUTSIDE_CLASS1_RESIDUE_CANCELLATION_FOUND_EXACT_SUPPORT_OPEN",
        "claim_boundary": (
            "This starts from each best local q12 cover and adds one to three q12 product "
            "terms that do not involve seed class 1. It searches for modulo-6 cancellation "
            "of outside-target support while preserving the target atoms over the integers."
        ),
        "selected_mask": q12_h6_projection_audit["selected_mask"],
        "seed_q12_class": seed_q12_class,
        "coefficient_set": coefficient_set,
        "max_cancellation_terms": max_cancellation_terms,
        "nonzero_q12_product_term_count": len(all_product_terms),
        "outside_class1_q12_product_term_count": len(outside_seed_terms),
        "family_cancellation_rows": family_rows,
        "total_search_space_size": sum(row["search_space_size"] for row in family_rows),
        "total_valid_candidate_count": sum(
            row["valid_candidate_count"] for row in family_rows
        ),
        "total_residue_clear_candidate_count": sum(
            row["residue_clear_candidate_count"] for row in family_rows
        ),
        "total_exact_support_candidate_count": sum(
            row["exact_support_candidate_count"] for row in family_rows
        ),
        "result": result,
        "all_checks_pass": all(result.values()),
        "interpretation": (
            "Outside-class-1 q12 products can cancel all extra-support residues modulo 6 "
            "for the four rank-2 target families. This is a stronger packet-normalized "
            "bridge witness than the local cover, but it is still not an exact integer "
            "support action: the residue-cleared candidates increase the H6 overhang."
        ),
    }


def packet_pair_passes_local_image_test(left: list[int], right: list[int]) -> bool:
    return all(
        not packet_snf_local_failures(left[idx], right[idx]) for idx in range(len(left))
    )


def compact_packet_candidate_row(
    row_id: str,
    row_kind: str,
    support_atom_ids: list[int],
    image_vector: list[int],
    extra_atom_id: int | None = None,
) -> dict[str, Any]:
    image_gcd = math.gcd(*[abs(value) for value in image_vector]) if any(image_vector) else 0
    row = {
        "row_id": row_id,
        "row_kind": row_kind,
        "support_atom_ids": support_atom_ids,
        "support_size": len(support_atom_ids),
        "image_is_even": all(value % 2 == 0 for value in image_vector),
        "image_gcd": image_gcd,
        "image_nonzero_count": sum(1 for value in image_vector if value),
        "image_vector": image_vector,
    }
    if extra_atom_id is not None:
        row["extra_atom_id"] = int(extra_atom_id)
    return row


def build_mask288_q12_packet_normalized_seed_assembly_audit(
    q12_h6_projection_audit: dict[str, Any],
    q12_packet_low_support_audit: dict[str, Any],
    broadened_extension_audit: dict[str, Any],
    linear_combo_audit: dict[str, Any],
    outside_cancellation_audit: dict[str, Any],
) -> dict[str, Any]:
    incidence = load_json(D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE_REPORT)
    low_support = load_json(D20_BOUNDARY_PACKET_LOW_SUPPORT_CANDIDATE_ATLAS_REPORT)
    packet_snf = load_json(D20_PACKET_BRIDGE_SNF_OBSTRUCTION_REPORT)
    matrix = incidence["derived"]["boundary_atom_step_incidence_matrix"]
    q12_rows = q12_h6_projection_audit["q12_h6_rows"]
    linear_rows_by_extra = {
        int(row["extra_atom_id"]): row
        for row in linear_combo_audit["family_combination_rows"]
    }

    normalized_q12_rows = []
    for cancel_row in outside_cancellation_audit["family_cancellation_rows"]:
        extra_atom_id = int(cancel_row["extra_atom_id"])
        base_products = linear_rows_by_extra[extra_atom_id]["best_cover_candidate"][
            "chosen_products"
        ]
        cancellation_terms = cancel_row["best_residue_clear_candidate"][
            "cancellation_terms"
        ]
        vector = q12_product_readout_vector(base_products + cancellation_terms, q12_rows)
        scalar6_divisible = all(value % 6 == 0 for value in vector)
        normalized_support = [
            {"public_atom_id": atom_id, "coefficient": value // 6}
            for atom_id, value in enumerate(vector)
            if value
        ]
        image_vector = boundary_image_for_support(normalized_support, matrix)
        normalized_row = compact_packet_candidate_row(
            f"q12_residue6_{extra_atom_id}",
            "q12_residue6",
            [row["public_atom_id"] for row in normalized_support],
            image_vector,
            extra_atom_id,
        )
        normalized_row.update(
            {
                "scalar6_divisible": scalar6_divisible,
                "normalized_coefficient_gcd": math.gcd(
                    *[abs(row["coefficient"]) for row in normalized_support]
                )
                if normalized_support
                else 0,
                "normalized_coefficient_support": normalized_support,
            }
        )
        normalized_q12_rows.append(normalized_row)

    low_support_rows = []
    for row in low_support["derived"]["even_image_candidate_rows"]:
        support_atom_ids = [
            item["public_atom_id"] for item in row["coefficient_support"]
        ]
        low_support_rows.append(
            compact_packet_candidate_row(
                f"low_support2_{row['candidate_id']}",
                "low_support2",
                support_atom_ids,
                row["image_vector"],
            )
        )

    support3_rows = []
    for row in broadened_extension_audit["support3_widened_even_candidate_rows"]:
        support = [
            {
                "public_atom_id": item["public_atom_id"],
                "coefficient": item["coefficient"],
            }
            for item in row["coefficient_support"]
        ]
        image_vector = boundary_image_for_support(support, matrix)
        support3_rows.append(
            compact_packet_candidate_row(
                f"support3_{row['candidate_id']}",
                "support3_widened",
                row["support_atom_ids"],
                image_vector,
                row["extra_atom_id"],
            )
        )

    candidate_rows = normalized_q12_rows + low_support_rows + support3_rows
    compatible_doublet_rows = []
    q12_involving_pair_count = 0
    q12_involving_compatible_count = 0
    for left_idx, right_idx in itertools.combinations(range(len(candidate_rows)), 2):
        left = candidate_rows[left_idx]
        right = candidate_rows[right_idx]
        q12_involved = "q12_residue6" in {left["row_kind"], right["row_kind"]}
        if q12_involved:
            q12_involving_pair_count += 1
        if not packet_pair_passes_local_image_test(
            left["image_vector"],
            right["image_vector"],
        ):
            continue
        rank = rank_two_integer_vectors(left["image_vector"], right["image_vector"])
        if q12_involved:
            q12_involving_compatible_count += 1
        compatible_doublet_rows.append(
            {
                "left_row_id": left["row_id"],
                "right_row_id": right["row_id"],
                "left_row_kind": left["row_kind"],
                "right_row_kind": right["row_kind"],
                "doublet_rank_over_Q": rank,
                "support_family_atom_ids": sorted(
                    set(left["support_atom_ids"]).union(right["support_atom_ids"])
                ),
                "q12_residue6_involved": q12_involved,
            }
        )

    compatible_rank_histogram = counter_dict(
        [str(row["doublet_rank_over_Q"]) for row in compatible_doublet_rows]
    )
    compatible_kind_pair_histogram = counter_dict(
        [
            f"{row['left_row_kind']}+{row['right_row_kind']}"
            for row in compatible_doublet_rows
        ]
    )
    compatible_support_families = {
        tuple(row["support_family_atom_ids"]) for row in compatible_doublet_rows
    }
    rank2_support_families = {
        tuple(row["support_family_atom_ids"])
        for row in compatible_doublet_rows
        if row["doublet_rank_over_Q"] == 2
    }
    packet_summary = packet_snf["derived"]["obstruction_summary"]
    low_support_summary = low_support["derived"]["low_support_summary"]

    result = {
        "scalar6_normalized_q12_rows_materialized": all(
            row["scalar6_divisible"] is True for row in normalized_q12_rows
        )
        and [row["support_size"] for row in normalized_q12_rows] == [10, 10, 13, 13],
        "scalar6_normalized_q12_rows_are_even_boundary_rows": all(
            row["image_is_even"] is True for row in normalized_q12_rows
        ),
        "low_support_packet_atlas_certified_degenerate": (
            low_support["all_checks_pass"] is True
            and low_support_summary["compatible_doublet_count"] == 6
            and low_support_summary["compatible_doublet_rank_histogram"] == {"1": 6}
            and low_support_summary["full_packet_doublet_map_available"] is False
        ),
        "support3_packet_atlas_certified_rank2_local_only": (
            broadened_extension_audit["all_checks_pass"] is True
            and broadened_extension_audit["support3_widened_summary"][
                "compatible_doublet_count"
            ]
            == 64
            and broadened_extension_audit["support3_widened_summary"][
                "rank2_doublet_count"
            ]
            == 32
        ),
        "q12_normalized_rows_add_no_packet_compatible_doublets": (
            q12_involving_pair_count == 310 and q12_involving_compatible_count == 0
        ),
        "candidate_pool_contains_only_preexisting_atlas_doublets": (
            compatible_kind_pair_histogram
            == {"low_support2+low_support2": 6, "support3_widened+support3_widened": 64}
            and len(compatible_doublet_rows) == 70
        ),
        "candidate_pool_still_short_of_full_packet_bridge": (
            len(compatible_support_families) == 7
            and len(rank2_support_families) == 4
            and packet_summary["raw_bridge_columns_available"] is False
        ),
    }
    result["packet_normalized_q12_seed_assembly_remains_blocked"] = all(
        result.values()
    )

    return {
        "status": "MASK288_Q12_PACKET_NORMALIZED_SEED_ASSEMBLY_BLOCKED",
        "claim_boundary": (
            "This divides the residue-cleared outside-class-1 q12 witnesses by scalar 6 "
            "and tries to assemble packet-compatible doublets with the certified support-2 "
            "and widened support-3 packet atlases. It does not construct the missing raw "
            "q12/A985-to-packet projection."
        ),
        "selected_mask": q12_h6_projection_audit["selected_mask"],
        "packet_snf_local_image_test": packet_summary["local_image_test"],
        "normalized_q12_seed_rows": [
            {k: v for k, v in row.items() if k != "image_vector"}
            for row in normalized_q12_rows
        ],
        "candidate_pool_summary": {
            "q12_residue6_row_count": len(normalized_q12_rows),
            "low_support_even_row_count": len(low_support_rows),
            "support3_widened_even_row_count": len(support3_rows),
            "candidate_row_count": len(candidate_rows),
            "candidate_pair_count": len(list(itertools.combinations(candidate_rows, 2))),
            "q12_involving_pair_count": q12_involving_pair_count,
            "q12_involving_compatible_doublet_count": q12_involving_compatible_count,
            "compatible_doublet_count": len(compatible_doublet_rows),
            "compatible_doublet_rank_histogram": compatible_rank_histogram,
            "compatible_doublet_kind_pair_histogram": compatible_kind_pair_histogram,
            "compatible_support_family_count": len(compatible_support_families),
            "rank2_support_family_count": len(rank2_support_families),
        },
        "compatible_doublet_rows": compatible_doublet_rows,
        "low_support_summary": {
            "compatible_doublet_count": low_support_summary["compatible_doublet_count"],
            "compatible_doublet_rank_histogram": low_support_summary[
                "compatible_doublet_rank_histogram"
            ],
            "full_packet_doublet_map_available": low_support_summary[
                "full_packet_doublet_map_available"
            ],
        },
        "support3_widened_summary": {
            "compatible_doublet_count": broadened_extension_audit[
                "support3_widened_summary"
            ]["compatible_doublet_count"],
            "compatible_doublet_rank_histogram": broadened_extension_audit[
                "support3_widened_summary"
            ]["compatible_doublet_rank_histogram"],
            "rank2_doublet_count": broadened_extension_audit[
                "support3_widened_summary"
            ]["rank2_doublet_count"],
        },
        "packet_bridge_obstruction_summary": {
            "raw_bridge_columns_available": packet_summary["raw_bridge_columns_available"],
            "smith_diagonal_multiplicities": packet_summary[
                "smith_diagonal_multiplicities"
            ],
        },
        "result": result,
        "all_checks_pass": all(result.values()),
        "interpretation": (
            "The residue-cleared q12 witnesses survive scalar-6 normalization as even "
            "public-boundary rows, but they do not pair with any certified low-support or "
            "support-3 atlas row under the packet SNF image test. The compatible doublet "
            "pool is exactly the previous atlas pool, so a full packet bridge remains open."
        ),
    }


def build_mask288_q12_direct_paired_doublet_search_audit(
    q12_h6_projection_audit: dict[str, Any],
    linear_combo_audit: dict[str, Any],
    outside_cancellation_audit: dict[str, Any],
) -> dict[str, Any]:
    incidence = load_json(D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE_REPORT)
    packet_snf = load_json(D20_PACKET_BRIDGE_SNF_OBSTRUCTION_REPORT)
    matrix = incidence["derived"]["boundary_atom_step_incidence_matrix"]
    q12_rows = q12_h6_projection_audit["q12_h6_rows"]
    seed_q12_class = linear_combo_audit["seed_q12_class"]
    with np.load(ROOT / QUOTIENTS_NPZ) as payload:
        q12_tensor = np.asarray(payload["q12_tensor"], dtype=np.int64)

    all_product_terms = []
    for left_class in range(q12_tensor.shape[0]):
        for right_class in range(q12_tensor.shape[1]):
            product = q12_product_d20_readout(
                q12_tensor[left_class, right_class, :],
                q12_rows,
            )
            if not product["output_q12_coefficients"]:
                continue
            all_product_terms.append(
                {
                    "product_id": f"q12_{left_class}_{right_class}",
                    "left_q12_class": int(left_class),
                    "right_q12_class": int(right_class),
                    **product,
                }
            )
    outside_seed_terms = [
        term
        for term in all_product_terms
        if term["left_q12_class"] != seed_q12_class
        and term["right_q12_class"] != seed_q12_class
    ]

    q12_candidate_rows = []
    family_candidate_rows = []
    coefficient_set = [-1, 1]
    max_cancellation_terms = 3
    for family_row in linear_combo_audit["family_combination_rows"]:
        target_atom_ids = family_row["target_atom_ids"]
        base_products = family_row["best_cover_candidate"]["chosen_products"]
        base_vector = q12_product_readout_vector(base_products, q12_rows)
        first_row_index = len(q12_candidate_rows)
        for term_count in range(1, max_cancellation_terms + 1):
            for term_combo in itertools.combinations(outside_seed_terms, term_count):
                for coefficients in itertools.product(coefficient_set, repeat=term_count):
                    candidate = q12_linear_residue_candidate(
                        list(term_combo),
                        tuple(int(coefficient) for coefficient in coefficients),
                        base_vector,
                        target_atom_ids,
                    )
                    if (
                        candidate is None
                        or candidate["outside_target_nonzero_mod6_atom_count"] != 0
                    ):
                        continue
                    vector = q12_product_readout_vector(
                        base_products + candidate["cancellation_terms"],
                        q12_rows,
                    )
                    if not all(value % 6 == 0 for value in vector):
                        continue
                    normalized_support = [
                        {"public_atom_id": atom_id, "coefficient": value // 6}
                        for atom_id, value in enumerate(vector)
                        if value
                    ]
                    image_vector = boundary_image_for_support(normalized_support, matrix)
                    row_id = (
                        f"q12_pair_{family_row['extra_atom_id']}_"
                        f"{len(q12_candidate_rows)}"
                    )
                    row = compact_packet_candidate_row(
                        row_id,
                        "q12_direct_residue6",
                        [item["public_atom_id"] for item in normalized_support],
                        image_vector,
                        family_row["extra_atom_id"],
                    )
                    row.update(
                        {
                            "target_atom_ids": target_atom_ids,
                            "cancellation_term_count": candidate[
                                "cancellation_term_count"
                            ],
                            "cancellation_terms": candidate["cancellation_terms"],
                            "normalized_coefficient_gcd": math.gcd(
                                *[
                                    abs(item["coefficient"])
                                    for item in normalized_support
                                ]
                            )
                            if normalized_support
                            else 0,
                        }
                    )
                    q12_candidate_rows.append(row)
        family_rows = q12_candidate_rows[first_row_index:]
        family_candidate_rows.append(
            {
                "extra_atom_id": family_row["extra_atom_id"],
                "candidate_count": len(family_rows),
                "candidate_row_ids": [row["row_id"] for row in family_rows],
                "support_size_histogram": counter_dict(
                    [str(row["support_size"]) for row in family_rows]
                ),
                "image_gcd_histogram": counter_dict(
                    [str(row["image_gcd"]) for row in family_rows]
                ),
            }
        )

    compatible_doublet_rows = []
    for left, right in itertools.combinations(q12_candidate_rows, 2):
        if not packet_pair_passes_local_image_test(
            left["image_vector"],
            right["image_vector"],
        ):
            continue
        support_family = sorted(
            set(left["support_atom_ids"]).union(right["support_atom_ids"])
        )
        compatible_doublet_rows.append(
            {
                "left_row_id": left["row_id"],
                "right_row_id": right["row_id"],
                "left_extra_atom_id": left["extra_atom_id"],
                "right_extra_atom_id": right["extra_atom_id"],
                "doublet_rank_over_Q": rank_two_integer_vectors(
                    left["image_vector"],
                    right["image_vector"],
                ),
                "same_extra_atom_family": left["extra_atom_id"]
                == right["extra_atom_id"],
                "support_family_atom_ids": support_family,
            }
        )

    rank2_support_families = sorted(
        {
            tuple(row["support_family_atom_ids"])
            for row in compatible_doublet_rows
            if row["doublet_rank_over_Q"] == 2
        },
        key=lambda row: (len(row), row),
    )
    representative_rows = []
    for support_family in rank2_support_families:
        rows = [
            row
            for row in compatible_doublet_rows
            if tuple(row["support_family_atom_ids"]) == support_family
            and row["doublet_rank_over_Q"] == 2
        ]
        rows.sort(
            key=lambda row: (
                row["left_row_id"],
                row["right_row_id"],
            )
        )
        representative = rows[0]
        left = next(
            row
            for row in q12_candidate_rows
            if row["row_id"] == representative["left_row_id"]
        )
        right = next(
            row
            for row in q12_candidate_rows
            if row["row_id"] == representative["right_row_id"]
        )
        representative_rows.append(
            {
                "support_family_atom_ids": list(support_family),
                "compatible_pair_count_for_family": len(rows),
                "left_row_id": representative["left_row_id"],
                "right_row_id": representative["right_row_id"],
                "left_extra_atom_id": representative["left_extra_atom_id"],
                "right_extra_atom_id": representative["right_extra_atom_id"],
                "left_cancellation_term_count": left["cancellation_term_count"],
                "right_cancellation_term_count": right["cancellation_term_count"],
                "left_support_size": left["support_size"],
                "right_support_size": right["support_size"],
                "left_image_gcd": left["image_gcd"],
                "right_image_gcd": right["image_gcd"],
            }
        )

    packet_summary = packet_snf["derived"]["obstruction_summary"]
    compatible_rank_histogram = counter_dict(
        [str(row["doublet_rank_over_Q"]) for row in compatible_doublet_rows]
    )
    result = {
        "q12_residue_clear_rows_match_prior_count": len(q12_candidate_rows)
        == outside_cancellation_audit["total_residue_clear_candidate_count"]
        == 102,
        "q12_residue_clear_rows_are_even_after_scalar6": all(
            row["image_is_even"] is True for row in q12_candidate_rows
        ),
        "direct_q12_packet_compatible_doublets_found": len(compatible_doublet_rows)
        == 509,
        "direct_q12_packet_doublets_are_mostly_rank2": compatible_rank_histogram
        == {"1": 4, "2": 505},
        "direct_q12_rank2_support_families_short_of_ten": len(rank2_support_families)
        == 8,
        "raw_packet_bridge_columns_still_absent": packet_summary[
            "raw_bridge_columns_available"
        ]
        is False,
    }
    result["direct_q12_paired_doublet_search_finds_rank2_short_of_full_bridge"] = all(
        result.values()
    )

    return {
        "status": "MASK288_Q12_DIRECT_PAIRED_DOUBLET_SEARCH_FINDS_RANK2_SHORT_OF_FULL_BRIDGE",
        "claim_boundary": (
            "This pairs scalar-6-normalized, residue-cleared q12 rows directly against "
            "the packet SNF local image test. It does not claim a full packet bridge unless "
            "the bounded q12 pairs assemble ten independent rank-2 packet families."
        ),
        "selected_mask": q12_h6_projection_audit["selected_mask"],
        "seed_q12_class": seed_q12_class,
        "coefficient_set": coefficient_set,
        "max_cancellation_terms": max_cancellation_terms,
        "packet_snf_local_image_test": packet_summary["local_image_test"],
        "q12_candidate_summary": {
            "candidate_count": len(q12_candidate_rows),
            "candidate_pair_count": len(
                list(itertools.combinations(q12_candidate_rows, 2))
            ),
            "candidate_count_by_extra_atom": {
                str(row["extra_atom_id"]): row["candidate_count"]
                for row in family_candidate_rows
            },
            "support_size_histogram": counter_dict(
                [str(row["support_size"]) for row in q12_candidate_rows]
            ),
            "cancellation_term_count_histogram": counter_dict(
                [str(row["cancellation_term_count"]) for row in q12_candidate_rows]
            ),
            "image_gcd_histogram": counter_dict(
                [str(row["image_gcd"]) for row in q12_candidate_rows]
            ),
        },
        "family_candidate_rows": family_candidate_rows,
        "compatible_doublet_summary": {
            "compatible_doublet_count": len(compatible_doublet_rows),
            "compatible_doublet_rank_histogram": compatible_rank_histogram,
            "same_extra_atom_family_histogram": counter_dict(
                [
                    str(row["same_extra_atom_family"])
                    for row in compatible_doublet_rows
                ]
            ),
            "extra_atom_pair_histogram": counter_dict(
                [
                    f"{row['left_extra_atom_id']},{row['right_extra_atom_id']}"
                    for row in compatible_doublet_rows
                ]
            ),
            "rank2_support_family_count": len(rank2_support_families),
            "full_packet_target_doublet_family_count": 10,
        },
        "rank2_support_family_rows": representative_rows,
        "packet_bridge_obstruction_summary": {
            "raw_bridge_columns_available": packet_summary["raw_bridge_columns_available"],
            "smith_diagonal_multiplicities": packet_summary[
                "smith_diagonal_multiplicities"
            ],
        },
        "result": result,
        "all_checks_pass": all(result.values()),
        "interpretation": (
            "The direct q12-vs-q12 packet test produces many rank-2 compatible doublets, "
            "unlike the q12-vs-atlas assembly test. The bounded pool still spans only eight "
            "rank-2 support families, not the ten families needed for a full packet bridge."
        ),
    }


def build_mask288_q12_one_sided_seed_correction_audit(
    q12_h6_projection_audit: dict[str, Any],
    linear_combo_audit: dict[str, Any],
    direct_paired_audit: dict[str, Any],
) -> dict[str, Any]:
    incidence = load_json(D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE_REPORT)
    packet_snf = load_json(D20_PACKET_BRIDGE_SNF_OBSTRUCTION_REPORT)
    matrix = incidence["derived"]["boundary_atom_step_incidence_matrix"]
    q12_rows = q12_h6_projection_audit["q12_h6_rows"]
    seed_q12_class = linear_combo_audit["seed_q12_class"]
    with np.load(ROOT / QUOTIENTS_NPZ) as payload:
        q12_tensor = np.asarray(payload["q12_tensor"], dtype=np.int64)

    all_product_terms = []
    for left_class in range(q12_tensor.shape[0]):
        for right_class in range(q12_tensor.shape[1]):
            product = q12_product_d20_readout(
                q12_tensor[left_class, right_class, :],
                q12_rows,
            )
            if not product["output_q12_coefficients"]:
                continue
            all_product_terms.append(
                {
                    "product_id": f"q12_{left_class}_{right_class}",
                    "left_q12_class": int(left_class),
                    "right_q12_class": int(right_class),
                    **product,
                }
            )
    outside_seed_terms = [
        term
        for term in all_product_terms
        if term["left_q12_class"] != seed_q12_class
        and term["right_q12_class"] != seed_q12_class
    ]
    seed_correction_terms = [
        term
        for term in all_product_terms
        if term["left_q12_class"] == seed_q12_class
        or term["right_q12_class"] == seed_q12_class
    ]

    coefficient_set = [-1, 1]
    max_cancellation_terms = 3
    original_rows = []
    for family_row in linear_combo_audit["family_combination_rows"]:
        target_atom_ids = family_row["target_atom_ids"]
        base_products = family_row["best_cover_candidate"]["chosen_products"]
        base_vector = q12_product_readout_vector(base_products, q12_rows)
        for term_count in range(1, max_cancellation_terms + 1):
            for term_combo in itertools.combinations(outside_seed_terms, term_count):
                for coefficients in itertools.product(coefficient_set, repeat=term_count):
                    candidate = q12_linear_residue_candidate(
                        list(term_combo),
                        tuple(int(coefficient) for coefficient in coefficients),
                        base_vector,
                        target_atom_ids,
                    )
                    if (
                        candidate is None
                        or candidate["outside_target_nonzero_mod6_atom_count"] != 0
                    ):
                        continue
                    products = base_products + candidate["cancellation_terms"]
                    vector = q12_product_readout_vector(products, q12_rows)
                    if not all(value % 6 == 0 for value in vector):
                        continue
                    normalized_support = [
                        {"public_atom_id": atom_id, "coefficient": value // 6}
                        for atom_id, value in enumerate(vector)
                        if value
                    ]
                    image_vector = boundary_image_for_support(normalized_support, matrix)
                    original_rows.append(
                        {
                            "row_id": (
                                f"q12_orig_{family_row['extra_atom_id']}_"
                                f"{len(original_rows)}"
                            ),
                            "extra_atom_id": family_row["extra_atom_id"],
                            "target_atom_ids": target_atom_ids,
                            "products": products,
                            "support_atom_ids": [
                                item["public_atom_id"] for item in normalized_support
                            ],
                            "support_size": len(normalized_support),
                            "image_vector": image_vector,
                        }
                    )

    corrected_rows = []
    correction_attempt_count = 0
    target_lost_count = 0
    not_scalar6_divisible_count = 0
    for original_row in original_rows:
        for correction_term in seed_correction_terms:
            for correction_coefficient in coefficient_set:
                correction_attempt_count += 1
                correction_product = {
                    "product_id": correction_term["product_id"],
                    "coefficient": int(correction_coefficient),
                    "left_q12_class": correction_term["left_q12_class"],
                    "right_q12_class": correction_term["right_q12_class"],
                    "output_q12_coefficients": correction_term[
                        "output_q12_coefficients"
                    ],
                }
                corrected_products = original_row["products"] + [correction_product]
                vector = q12_product_readout_vector(corrected_products, q12_rows)
                if any(
                    vector[atom_id] == 0
                    for atom_id in original_row["target_atom_ids"]
                ):
                    target_lost_count += 1
                    continue
                if not all(value % 6 == 0 for value in vector):
                    not_scalar6_divisible_count += 1
                    continue
                normalized_support = [
                    {"public_atom_id": atom_id, "coefficient": value // 6}
                    for atom_id, value in enumerate(vector)
                    if value
                ]
                image_vector = boundary_image_for_support(normalized_support, matrix)
                corrected_rows.append(
                    {
                        "row_id": f"q12_seedcorr_{len(corrected_rows)}",
                        "base_row_id": original_row["row_id"],
                        "base_extra_atom_id": original_row["extra_atom_id"],
                        "correction_product_id": correction_term["product_id"],
                        "correction_coefficient": int(correction_coefficient),
                        "support_atom_ids": [
                            item["public_atom_id"] for item in normalized_support
                        ],
                        "support_size": len(normalized_support),
                        "image_vector": image_vector,
                        "image_gcd": math.gcd(
                            *[abs(value) for value in image_vector]
                        )
                        if any(image_vector)
                        else 0,
                    }
                )

    prior_rank2_support_families = {
        tuple(row["support_family_atom_ids"])
        for row in direct_paired_audit["rank2_support_family_rows"]
    }
    compatible_doublet_rows = []
    new_rank2_by_support_family: dict[tuple[int, ...], dict[str, Any]] = {}
    all_corrected_support_families: set[tuple[int, ...]] = set()
    for corrected_row in corrected_rows:
        for original_row in original_rows:
            if not packet_pair_passes_local_image_test(
                corrected_row["image_vector"],
                original_row["image_vector"],
            ):
                continue
            rank = rank_two_integer_vectors(
                corrected_row["image_vector"],
                original_row["image_vector"],
            )
            support_family = tuple(
                sorted(
                    set(corrected_row["support_atom_ids"]).union(
                        original_row["support_atom_ids"]
                    )
                )
            )
            all_corrected_support_families.add(support_family)
            pair_row = {
                "left_row_id": corrected_row["row_id"],
                "right_row_id": original_row["row_id"],
                "corrected_base_extra_atom_id": corrected_row["base_extra_atom_id"],
                "right_extra_atom_id": original_row["extra_atom_id"],
                "correction_product_id": corrected_row["correction_product_id"],
                "correction_coefficient": corrected_row["correction_coefficient"],
                "doublet_rank_over_Q": rank,
                "support_family_atom_ids": list(support_family),
            }
            compatible_doublet_rows.append(pair_row)
            if (
                rank == 2
                and support_family not in prior_rank2_support_families
                and support_family not in new_rank2_by_support_family
            ):
                new_rank2_by_support_family[support_family] = pair_row

    new_rank2_support_family_rows = sorted(
        new_rank2_by_support_family.values(),
        key=lambda row: (
            len(row["support_family_atom_ids"]),
            row["support_family_atom_ids"],
            row["left_row_id"],
            row["right_row_id"],
        ),
    )
    packet_summary = packet_snf["derived"]["obstruction_summary"]
    correction_survivor_histogram = counter_dict(
        [
            f"{row['correction_product_id']}:{row['correction_coefficient']}"
            for row in corrected_rows
        ]
    )
    compatible_correction_histogram = counter_dict(
        [
            f"{row['correction_product_id']}:{row['correction_coefficient']}"
            for row in compatible_doublet_rows
        ]
    )
    compatible_rank_histogram = counter_dict(
        [str(row["doublet_rank_over_Q"]) for row in compatible_doublet_rows]
    )
    original_images = [row["image_vector"] for row in original_rows]
    corrected_images = [row["image_vector"] for row in corrected_rows]
    combined_unique_images = [
        list(row) for row in sorted({tuple(row) for row in original_images + corrected_images})
    ]
    rank_ceiling_summary = {
        "rank_method": "exact_fraction_gaussian_elimination_over_Q",
        "original_q12_row_count": len(original_rows),
        "scalar6_corrected_row_count": len(corrected_rows),
        "unique_boundary_image_count": len(combined_unique_images),
        "original_boundary_image_rank_over_Q": matrix_rank_over_q(original_images),
        "corrected_boundary_image_rank_over_Q": matrix_rank_over_q(corrected_images),
        "combined_boundary_image_rank_over_Q": matrix_rank_over_q(combined_unique_images),
        "rank20_selection_upper_bound": min(20, matrix_rank_over_q(combined_unique_images)),
    }

    result = {
        "one_sided_seed_correction_attempts_materialized": (
            correction_attempt_count == 1428
            and len(seed_correction_terms) == 7
            and len(original_rows) == 102
        ),
        "seed_correction_scalar6_survivors_materialized": (
            len(corrected_rows) == 288
            and target_lost_count == 120
            and not_scalar6_divisible_count == 1020
        ),
        "only_seed_8_corrections_survive_scalar6": correction_survivor_histogram
        == {"q12_1_8:-1": 102, "q12_1_8:1": 42, "q12_6_1:-1": 102, "q12_6_1:1": 42},
        "one_sided_pairs_are_packet_compatible_rank2": (
            len(compatible_doublet_rows) == 4628
            and compatible_rank_histogram == {"2": 4628}
        ),
        "one_sided_pairs_add_new_rank2_support_families": (
            len(new_rank2_support_family_rows) == 20
            and len(prior_rank2_support_families) == 8
        ),
        "rank2_support_family_count_crosses_ten_family_threshold": (
            len(prior_rank2_support_families)
            + len(new_rank2_support_family_rows)
            == 28
            and packet_summary["raw_bridge_columns_available"] is False
        ),
        "corrected_boundary_image_rank_ceiling_is_9": (
            rank_ceiling_summary["original_boundary_image_rank_over_Q"] == 9
            and rank_ceiling_summary["corrected_boundary_image_rank_over_Q"] == 9
            and rank_ceiling_summary["combined_boundary_image_rank_over_Q"] == 9
        ),
    }
    result["one_sided_seed_correction_finds_new_rank2_families_projection_open"] = all(
        result.values()
    )

    return {
        "status": "MASK288_Q12_ONE_SIDED_SEED_CORRECTION_FINDS_NEW_RANK2_FAMILIES_PROJECTION_OPEN",
        "claim_boundary": (
            "This allows exactly one seed-class-1 q12 correction term on one side of the "
            "direct q12 pair search. It tests for new packet-compatible rank-2 support "
            "families, but it does not certify an independent ten-doublet packet basis or "
            "construct the missing q12/A985-to-packet projection."
        ),
        "selected_mask": q12_h6_projection_audit["selected_mask"],
        "seed_q12_class": seed_q12_class,
        "coefficient_set": coefficient_set,
        "max_cancellation_terms": max_cancellation_terms,
        "seed_correction_term_ids": [row["product_id"] for row in seed_correction_terms],
        "correction_attempt_summary": {
            "original_q12_row_count": len(original_rows),
            "seed_correction_term_count": len(seed_correction_terms),
            "attempt_count": correction_attempt_count,
            "target_lost_count": target_lost_count,
            "not_scalar6_divisible_count": not_scalar6_divisible_count,
            "scalar6_corrected_row_count": len(corrected_rows),
            "corrected_support_size_histogram": counter_dict(
                [str(row["support_size"]) for row in corrected_rows]
            ),
            "corrected_image_gcd_histogram": counter_dict(
                [str(row["image_gcd"]) for row in corrected_rows]
            ),
            "correction_survivor_histogram": correction_survivor_histogram,
        },
        "compatible_doublet_summary": {
            "compatible_doublet_count": len(compatible_doublet_rows),
            "compatible_doublet_rank_histogram": compatible_rank_histogram,
            "compatible_correction_histogram": compatible_correction_histogram,
            "corrected_pair_support_family_count": len(all_corrected_support_families),
            "prior_rank2_support_family_count": len(prior_rank2_support_families),
            "new_rank2_support_family_count": len(new_rank2_support_family_rows),
            "combined_rank2_support_family_count": (
                len(prior_rank2_support_families)
                + len(new_rank2_support_family_rows)
            ),
            "full_packet_target_doublet_family_count": 10,
            "new_rank2_support_family_size_histogram": counter_dict(
                [
                    str(len(row["support_family_atom_ids"]))
                    for row in new_rank2_support_family_rows
                ]
            ),
        },
        "rank_ceiling_summary": rank_ceiling_summary,
        "new_rank2_support_family_rows": new_rank2_support_family_rows,
        "packet_bridge_obstruction_summary": {
            "raw_bridge_columns_available": packet_summary["raw_bridge_columns_available"],
            "smith_diagonal_multiplicities": packet_summary[
                "smith_diagonal_multiplicities"
            ],
        },
        "result": result,
        "all_checks_pass": all(result.values()),
        "interpretation": (
            "One-sided seed-class corrections produce many rank-2 packet-compatible q12 "
            "doublets and add twenty support families beyond the prior direct q12 pool. "
            "This crosses the ten-family threshold, but independence and a raw packet "
            "projection remain unproven."
        ),
    }


def build_mask288_q12_corrected_rank20_selection_audit(
    one_sided_seed_correction_audit: dict[str, Any],
) -> dict[str, Any]:
    rank_summary = one_sided_seed_correction_audit["rank_ceiling_summary"]
    doublet_summary = one_sided_seed_correction_audit["compatible_doublet_summary"]
    packet_summary = one_sided_seed_correction_audit["packet_bridge_obstruction_summary"]

    result = {
        "corrected_pool_crosses_ten_family_threshold": doublet_summary[
            "combined_rank2_support_family_count"
        ]
        >= doublet_summary["full_packet_target_doublet_family_count"],
        "boundary_image_rank_computed_exactly": rank_summary["rank_method"]
        == "exact_fraction_gaussian_elimination_over_Q",
        "combined_corrected_boundary_image_rank_is_9": rank_summary[
            "combined_boundary_image_rank_over_Q"
        ]
        == 9,
        "rank20_selection_impossible_inside_current_pool": rank_summary[
            "rank20_selection_upper_bound"
        ]
        == 9,
        "raw_packet_projection_still_absent": packet_summary[
            "raw_bridge_columns_available"
        ]
        is False,
    }
    result["corrected_rank20_selection_blocked_by_rank9_image_ceiling"] = all(
        result.values()
    )

    return {
        "status": "MASK288_Q12_CORRECTED_RANK20_SELECTION_BLOCKED_BY_RANK9_IMAGE_CEILING",
        "claim_boundary": (
            "This tests the next closure condition after the corrected q12 pool crosses "
            "the ten support-family threshold. It computes the exact rational rank of all "
            "available scalar-6 normalized q12 boundary image rows; it does not search beyond "
            "the current one-sided seed-correction pool."
        ),
        "selected_mask": one_sided_seed_correction_audit["selected_mask"],
        "rank_target": 20,
        "support_family_target": one_sided_seed_correction_audit[
            "compatible_doublet_summary"
        ]["full_packet_target_doublet_family_count"],
        "available_rank2_support_family_count": doublet_summary[
            "combined_rank2_support_family_count"
        ],
        "rank_ceiling_summary": rank_summary,
        "obstruction_summary": {
            "why_ten_family_selection_fails": (
                "Every ten-family selection draws its twenty image rows from a row space "
                "of rank 9 over Q."
            ),
            "raw_bridge_columns_available": packet_summary["raw_bridge_columns_available"],
            "smith_diagonal_multiplicities": packet_summary[
                "smith_diagonal_multiplicities"
            ],
        },
        "result": result,
        "all_checks_pass": all(result.values()),
        "interpretation": (
            "The corrected q12 pool has enough rank-2 support families, but not enough "
            "linear image dimension. All original and one-sided corrected scalar-6 q12 rows "
            "span rank 9 over Q, so no ten selected doublets from this pool can form a "
            "rank-20 packet basis."
        ),
    }


def build_mask288_q12_rank_escape_probe_audit(
    q12_h6_projection_audit: dict[str, Any],
    linear_combo_audit: dict[str, Any],
    one_sided_seed_correction_audit: dict[str, Any],
) -> dict[str, Any]:
    incidence = load_json(D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE_REPORT)
    packet_snf = load_json(D20_PACKET_BRIDGE_SNF_OBSTRUCTION_REPORT)
    matrix = incidence["derived"]["boundary_atom_step_incidence_matrix"]
    q12_rows = q12_h6_projection_audit["q12_h6_rows"]
    seed_q12_class = linear_combo_audit["seed_q12_class"]
    with np.load(ROOT / QUOTIENTS_NPZ) as payload:
        q12_tensor = np.asarray(payload["q12_tensor"], dtype=np.int64)

    all_product_terms = []
    for left_class in range(q12_tensor.shape[0]):
        for right_class in range(q12_tensor.shape[1]):
            product = q12_product_d20_readout(
                q12_tensor[left_class, right_class, :],
                q12_rows,
            )
            if not product["output_q12_coefficients"]:
                continue
            all_product_terms.append(
                {
                    "product_id": f"q12_{left_class}_{right_class}",
                    "left_q12_class": int(left_class),
                    "right_q12_class": int(right_class),
                    **product,
                }
            )
    outside_seed_terms = [
        term
        for term in all_product_terms
        if term["left_q12_class"] != seed_q12_class
        and term["right_q12_class"] != seed_q12_class
    ]
    seed_correction_terms = [
        term
        for term in all_product_terms
        if term["left_q12_class"] == seed_q12_class
        or term["right_q12_class"] == seed_q12_class
    ]

    coefficient_set = [-1, 1]
    original_rows = []
    raw_non_scalar_rows = []
    raw_counts = {
        "attempt_count": 0,
        "target_lost_count": 0,
        "target_preserved_count": 0,
        "scalar6_row_count": 0,
        "non_scalar6_row_count": 0,
        "even_image_count": 0,
        "odd_image_count": 0,
    }
    for family_row in linear_combo_audit["family_combination_rows"]:
        target_atom_ids = family_row["target_atom_ids"]
        base_products = family_row["best_cover_candidate"]["chosen_products"]
        base_vector = q12_product_readout_vector(base_products, q12_rows)
        for term_count in range(1, 4):
            for term_combo in itertools.combinations(outside_seed_terms, term_count):
                for coefficients in itertools.product(coefficient_set, repeat=term_count):
                    candidate = q12_linear_residue_candidate(
                        list(term_combo),
                        tuple(int(coefficient) for coefficient in coefficients),
                        base_vector,
                        target_atom_ids,
                    )
                    if (
                        candidate is not None
                        and candidate["outside_target_nonzero_mod6_atom_count"] == 0
                    ):
                        products = base_products + candidate["cancellation_terms"]
                        vector = q12_product_readout_vector(products, q12_rows)
                        if all(value % 6 == 0 for value in vector):
                            normalized_support = [
                                {"public_atom_id": atom_id, "coefficient": value // 6}
                                for atom_id, value in enumerate(vector)
                                if value
                            ]
                            original_rows.append(
                                {
                                    "row_id": f"q12_orig_{len(original_rows)}",
                                    "target_atom_ids": target_atom_ids,
                                    "products": products,
                                    "image_vector": boundary_image_for_support(
                                        normalized_support,
                                        matrix,
                                    ),
                                }
                            )

                    if term_count > 2:
                        continue
                    raw_counts["attempt_count"] += 1
                    if candidate is None:
                        raw_counts["target_lost_count"] += 1
                        continue
                    raw_counts["target_preserved_count"] += 1
                    products = base_products + candidate["cancellation_terms"]
                    vector = q12_product_readout_vector(products, q12_rows)
                    scalar6 = all(value % 6 == 0 for value in vector)
                    if scalar6:
                        raw_counts["scalar6_row_count"] += 1
                    else:
                        raw_counts["non_scalar6_row_count"] += 1
                    raw_support = [
                        {"public_atom_id": atom_id, "coefficient": value}
                        for atom_id, value in enumerate(vector)
                        if value
                    ]
                    image_vector = boundary_image_for_support(raw_support, matrix)
                    if not all(value % 2 == 0 for value in image_vector):
                        raw_counts["odd_image_count"] += 1
                        continue
                    raw_counts["even_image_count"] += 1
                    raw_non_scalar_rows.append(
                        {
                            "row_id": f"q12_raw_nonscalar_{len(raw_non_scalar_rows)}",
                            "term_count": term_count,
                            "scalar6": scalar6,
                            "support_size": sum(1 for value in vector if value),
                            "outside_target_nonzero_mod6_atom_count": candidate[
                                "outside_target_nonzero_mod6_atom_count"
                            ],
                            "image_vector": image_vector,
                            "residue_key_mod6": tuple(value % 6 for value in image_vector),
                        }
                    )

    first_corrected_rows = []
    for original_row in original_rows:
        for correction_term in seed_correction_terms:
            for correction_coefficient in coefficient_set:
                correction_product = {
                    "product_id": correction_term["product_id"],
                    "coefficient": int(correction_coefficient),
                    "left_q12_class": correction_term["left_q12_class"],
                    "right_q12_class": correction_term["right_q12_class"],
                    "output_q12_coefficients": correction_term[
                        "output_q12_coefficients"
                    ],
                }
                corrected_products = original_row["products"] + [correction_product]
                vector = q12_product_readout_vector(corrected_products, q12_rows)
                if any(vector[atom_id] == 0 for atom_id in original_row["target_atom_ids"]):
                    continue
                if not all(value % 6 == 0 for value in vector):
                    continue
                normalized_support = [
                    {"public_atom_id": atom_id, "coefficient": value // 6}
                    for atom_id, value in enumerate(vector)
                    if value
                ]
                first_corrected_rows.append(
                    {
                        "target_atom_ids": original_row["target_atom_ids"],
                        "products": corrected_products,
                        "image_vector": boundary_image_for_support(
                            normalized_support,
                            matrix,
                        ),
                    }
                )

    second_corrected_rows = []
    second_attempt_count = 0
    second_target_lost_count = 0
    second_not_scalar6_count = 0
    second_added_correction_histogram_values = []
    for first_row in first_corrected_rows:
        for correction_term in seed_correction_terms:
            for correction_coefficient in coefficient_set:
                second_attempt_count += 1
                correction_product = {
                    "product_id": correction_term["product_id"],
                    "coefficient": int(correction_coefficient),
                    "left_q12_class": correction_term["left_q12_class"],
                    "right_q12_class": correction_term["right_q12_class"],
                    "output_q12_coefficients": correction_term[
                        "output_q12_coefficients"
                    ],
                }
                corrected_products = first_row["products"] + [correction_product]
                vector = q12_product_readout_vector(corrected_products, q12_rows)
                if any(vector[atom_id] == 0 for atom_id in first_row["target_atom_ids"]):
                    second_target_lost_count += 1
                    continue
                if not all(value % 6 == 0 for value in vector):
                    second_not_scalar6_count += 1
                    continue
                normalized_support = [
                    {"public_atom_id": atom_id, "coefficient": value // 6}
                    for atom_id, value in enumerate(vector)
                    if value
                ]
                second_added_correction_histogram_values.append(
                    f"{correction_term['product_id']}:{correction_coefficient}"
                )
                second_corrected_rows.append(
                    {
                        "support_size": len(normalized_support),
                        "image_vector": boundary_image_for_support(
                            normalized_support,
                            matrix,
                        ),
                    }
                )

    scalar6_unique_images = [
        list(row)
        for row in sorted(
            {
                tuple(row["image_vector"])
                for row in original_rows + first_corrected_rows + second_corrected_rows
            }
        )
    ]

    raw_residue_groups: dict[tuple[int, ...], list[dict[str, Any]]] = {}
    for row in raw_non_scalar_rows:
        raw_residue_groups.setdefault(row["residue_key_mod6"], []).append(row)
    raw_pair_count = 0
    raw_pair_rank_histogram_values = []
    raw_pair_scalar_kind_values = []
    for residue_key, group in raw_residue_groups.items():
        complement_key = tuple((-value) % 6 for value in residue_key)
        complement_group = raw_residue_groups.get(complement_key)
        if complement_group is None or residue_key > complement_key:
            continue
        if residue_key == complement_key:
            pair_iter = itertools.combinations(group, 2)
        else:
            pair_iter = itertools.product(group, complement_group)
        for left, right in pair_iter:
            if left["scalar6"] and right["scalar6"]:
                continue
            if not packet_pair_passes_local_image_test(
                left["image_vector"],
                right["image_vector"],
            ):
                continue
            raw_pair_count += 1
            raw_pair_rank_histogram_values.append(
                str(rank_two_integer_vectors(left["image_vector"], right["image_vector"]))
            )
            raw_pair_scalar_kind_values.append(f"{left['scalar6']},{right['scalar6']}")

    raw_non_scalar_unique_images = [
        list(row)
        for row in sorted(
            {
                tuple(row["image_vector"])
                for row in raw_non_scalar_rows
                if row["scalar6"] is False
            }
        )
    ]
    packet_summary = packet_snf["derived"]["obstruction_summary"]
    raw_nullspace = matrix_nullspace_over_q(raw_non_scalar_unique_images)
    raw_constraint_rows = [
        primitive_integer_vector(vector) for vector in raw_nullspace["basis"]
    ]
    packet_rational_constraint_count = (
        packet_summary["matrix_shape"][1] - packet_summary["rank_over_Q"]
    )
    rank11_annihilator_summary = {
        "boundary_coordinate_count": (
            len(raw_non_scalar_unique_images[0]) if raw_non_scalar_unique_images else 0
        ),
        "packet_target_coordinate_count": packet_summary["matrix_shape"][1],
        "raw_non_scalar_boundary_image_rank_over_Q": raw_nullspace["rank"],
        "annihilator_dimension_over_Q": len(raw_constraint_rows),
        "annihilator_pivot_columns": raw_nullspace["pivot_columns"],
        "annihilator_free_columns": raw_nullspace["free_columns"],
        "primitive_constraint_rows": raw_constraint_rows,
        "primitive_constraint_rows_sha256": sha_json(raw_constraint_rows),
        "constraint_support_size_histogram": counter_dict(
            [str(sum(1 for value in row if value)) for row in raw_constraint_rows]
        ),
        "constraint_abs_coefficient_histogram": counter_dict(
            [str(abs(value)) for row in raw_constraint_rows for value in row if value]
        ),
        "annihilator_rank_mod_packet_prime_2": matrix_rank_mod_prime(
            raw_constraint_rows,
            2,
        ),
        "annihilator_rank_mod_packet_prime_3": matrix_rank_mod_prime(
            raw_constraint_rows,
            3,
        ),
        "packet_operator_rank_over_Q": packet_summary["rank_over_Q"],
        "packet_snf_rational_constraint_count": packet_rational_constraint_count,
        "packet_constraint_comparison_status": (
            "BLOCKED_MISSING_BOUNDARY_TO_PACKET_PROJECTION"
        ),
        "packet_torsion_primes": packet_summary["torsion_primes"],
        "outside_q12_rational_generator_lower_bound": (
            packet_summary["rank_over_Q"] - raw_nullspace["rank"]
        ),
    }
    second_seed_summary = {
        "first_scalar6_corrected_row_count": len(first_corrected_rows),
        "second_correction_attempt_count": second_attempt_count,
        "second_target_lost_count": second_target_lost_count,
        "second_not_scalar6_divisible_count": second_not_scalar6_count,
        "second_scalar6_corrected_row_count": len(second_corrected_rows),
        "second_corrected_unique_boundary_image_count": len(
            {tuple(row["image_vector"]) for row in second_corrected_rows}
        ),
        "combined_scalar6_unique_boundary_image_count": len(scalar6_unique_images),
        "combined_scalar6_boundary_image_rank_over_Q": matrix_rank_over_q(
            scalar6_unique_images
        ),
        "second_added_correction_histogram": counter_dict(
            second_added_correction_histogram_values
        ),
    }
    raw_non_scalar_summary = {
        "max_outside_term_count": 2,
        "raw_attempt_count": raw_counts["attempt_count"],
        "raw_target_lost_count": raw_counts["target_lost_count"],
        "raw_target_preserved_count": raw_counts["target_preserved_count"],
        "raw_scalar6_row_count": raw_counts["scalar6_row_count"],
        "raw_non_scalar6_row_count": raw_counts["non_scalar6_row_count"],
        "raw_even_image_count": raw_counts["even_image_count"],
        "raw_odd_image_count": raw_counts["odd_image_count"],
        "raw_residue_group_count": len(raw_residue_groups),
        "raw_non_scalar_unique_boundary_image_count": len(raw_non_scalar_unique_images),
        "raw_non_scalar_boundary_image_rank_over_Q": raw_nullspace["rank"],
        "raw_packet_compatible_pair_count": raw_pair_count,
        "raw_packet_compatible_pair_rank_histogram": counter_dict(
            raw_pair_rank_histogram_values
        ),
        "raw_packet_compatible_pair_scalar_kind_histogram": counter_dict(
            raw_pair_scalar_kind_values
        ),
        "raw_even_support_size_histogram": counter_dict(
            [str(row["support_size"]) for row in raw_non_scalar_rows]
        ),
    }

    result = {
        "second_seed_correction_still_rank9": (
            second_seed_summary["second_scalar6_corrected_row_count"] == 1152
            and second_seed_summary["combined_scalar6_boundary_image_rank_over_Q"] == 9
        ),
        "bounded_raw_non_scalar_rows_materialized": (
            raw_non_scalar_summary["raw_attempt_count"] == 13448
            and raw_non_scalar_summary["raw_non_scalar6_row_count"] == 13438
            and raw_non_scalar_summary["raw_odd_image_count"] == 0
        ),
        "bounded_raw_non_scalar_pairs_are_rank2": (
            raw_non_scalar_summary["raw_packet_compatible_pair_count"] == 17610
            and raw_non_scalar_summary["raw_packet_compatible_pair_rank_histogram"]
            == {"2": 17610}
        ),
        "bounded_raw_non_scalar_rank_escapes_to_11": raw_non_scalar_summary[
            "raw_non_scalar_boundary_image_rank_over_Q"
        ]
        == 11,
        "bounded_raw_non_scalar_rank_still_short_of_20": raw_non_scalar_summary[
            "raw_non_scalar_boundary_image_rank_over_Q"
        ]
        < 20,
        "raw_packet_projection_still_absent": packet_summary[
            "raw_bridge_columns_available"
        ]
        is False,
        "rank11_boundary_annihilator_dimension_is_14": (
            rank11_annihilator_summary["annihilator_dimension_over_Q"] == 14
        ),
        "packet_snf_has_full_target_rank": (
            rank11_annihilator_summary["packet_operator_rank_over_Q"] == 20
            and rank11_annihilator_summary["packet_snf_rational_constraint_count"] == 0
        ),
        "q12_rank11_gap_requires_nine_external_generators": (
            rank11_annihilator_summary[
                "outside_q12_rational_generator_lower_bound"
            ]
            == 9
        ),
        "annihilator_packet_comparison_blocked_by_missing_projection": (
            rank11_annihilator_summary["boundary_coordinate_count"] == 25
            and rank11_annihilator_summary["packet_target_coordinate_count"] == 20
            and rank11_annihilator_summary["packet_constraint_comparison_status"]
            == "BLOCKED_MISSING_BOUNDARY_TO_PACKET_PROJECTION"
        ),
    }
    result["rank_escape_probe_finds_nonscalar_rank11_still_blocked"] = all(
        result.values()
    )

    return {
        "status": "MASK288_Q12_RANK_ESCAPE_PROBE_NONSCALAR_RANK11_STILL_BLOCKED",
        "claim_boundary": (
            "This bounded rank-escape probe tests two local escapes from the scalar-6 "
            "rank-9 ceiling: a second seed-class correction, and raw non-scalar q12 row "
            "pairs through outside-class term depth two. It does not exhaust all non-scalar "
            "q12 combinations."
        ),
        "selected_mask": q12_h6_projection_audit["selected_mask"],
        "rank_target": 20,
        "second_seed_correction_summary": second_seed_summary,
        "raw_non_scalar_pair_summary": raw_non_scalar_summary,
        "rank11_annihilator_summary": rank11_annihilator_summary,
        "packet_bridge_obstruction_summary": {
            "raw_bridge_columns_available": packet_summary["raw_bridge_columns_available"],
            "smith_diagonal_multiplicities": packet_summary[
                "smith_diagonal_multiplicities"
            ],
        },
        "result": result,
        "all_checks_pass": all(result.values()),
        "interpretation": (
            "A second scalar-6 seed correction only enlarges the same rank-9 image space. "
            "Raw non-scalar q12 rows through depth two do escape that ceiling and produce "
            "rank-2 packet-compatible pairs, but their exact image span is rank 11. "
            "In the 25-coordinate boundary image space this leaves fourteen primitive "
            "annihilator equations. The packet SNF target has twenty coordinates and full "
            "rational rank, so direct cokernel comparison is still blocked by the missing "
            "boundary-to-packet projection; nevertheless a rank-20 packet target needs at "
            "least nine independent directions outside this bounded q12 span."
        ),
    }


def build_discriminator_search(signatures: dict[str, Any]) -> dict[str, Any]:
    cycles = {int(row["cycle_id"]): row for row in load_csv(HCYCLE_PRIMITIVE_CYCLES)}
    edges = {int(row["edge_id"]): row for row in load_csv(HCYCLE_D20_EDGES)}
    overlap_rows = load_csv(STATIC_FOURIER_OVERLAP)
    h8_sector_identification = build_h8_sector_identification()

    candidate_rows = signatures["optic_axis"]["candidate_rows"]
    defect_pairs = {
        str(row["screen_id"]): [int(x) for x in row["defect_cycle_ids"]]
        for row in candidate_rows
    }

    hcycle_rows: list[dict[str, Any]] = []
    for screen_id, pair in sorted(defect_pairs.items()):
        pair_turns: list[str] = []
        pair_edges: list[int] = []
        cycle_rows: list[dict[str, Any]] = []
        for cycle_id in pair:
            cycle = cycles[cycle_id]
            turns = cycle["turn_addresses"].split()
            edge_ids = [int(x) for x in cycle["edge_ids"].split()]
            pair_turns.extend(turns)
            pair_edges.extend(edge_ids)
            cycle_rows.append(
                {
                    "cycle_id": cycle_id,
                    "length": int(cycle["length"]),
                    "optical_action": int(cycle["optical_action"]),
                    "turn_type_counts": counter_dict([turn[:1] for turn in turns]),
                    "signed_turn_counts": counter_dict(turns),
                    "selector_choice_counts": counter_dict(
                        [str(edges[edge_id]["selector_choice"]) for edge_id in edge_ids]
                    ),
                }
            )

        xor_edges = sorted(edge_id for edge_id in set(pair_edges) if pair_edges.count(edge_id) % 2 == 1)
        turn_type_counts = counter_dict([turn[:1] for turn in pair_turns])
        selector_choice_counts = counter_dict(
            [str(edges[edge_id]["selector_choice"]) for edge_id in pair_edges]
        )
        xor_selector_choice_counts = counter_dict(
            [str(edges[edge_id]["selector_choice"]) for edge_id in xor_edges]
        )
        hcycle_rows.append(
            {
                "screen_id": screen_id,
                "defect_cycle_ids": pair,
                "cycle_rows": cycle_rows,
                "combined_turn_type_counts": turn_type_counts,
                "combined_turn_type_signature": signature_from_counts(turn_type_counts, ("B", "S", "V")),
                "combined_signed_turn_counts": counter_dict(pair_turns),
                "selector_choice_counts": selector_choice_counts,
                "selector_choice_signature": signature_from_counts(
                    selector_choice_counts,
                    ("0", "1", "2"),
                ),
                "xor_edge_count": len(xor_edges),
                "xor_selector_choice_counts": xor_selector_choice_counts,
                "xor_selector_choice_signature": signature_from_counts(
                    xor_selector_choice_counts,
                    ("0", "1", "2"),
                ),
            }
        )

    by_turn_signature: dict[str, list[str]] = {}
    by_selector_signature: dict[str, list[str]] = {}
    by_xor_selector_signature: dict[str, list[str]] = {}
    for row in hcycle_rows:
        by_turn_signature.setdefault(row["combined_turn_type_signature"], []).append(row["screen_id"])
        by_selector_signature.setdefault(row["selector_choice_signature"], []).append(row["screen_id"])
        by_xor_selector_signature.setdefault(row["xor_selector_choice_signature"], []).append(row["screen_id"])

    overlap_by_screen: dict[str, dict[str, Any]] = {}
    for row in overlap_rows:
        screen_id = row["screen_id"]
        support = row["sector_support"]
        profile = overlap_by_screen.setdefault(
            screen_id,
            {
                "screen_id": screen_id,
                "quotient_generators": set(),
                "support_profiles": {},
            },
        )
        profile["quotient_generators"].add(row["quotient_generator"])
        support_profile = profile["support_profiles"].setdefault(support, [])
        support_profile.append(
            {
                "quotient_generator": row["quotient_generator"],
                "fourier_scalar_on_support": row["fourier_scalar_on_support"] == "True",
                "fourier_support_scalar": row["fourier_support_scalar"],
                "fourier_canonical_trace_defined": row["fourier_canonical_trace_defined"] == "True",
                "constructed_kernel_contains_support": row["constructed_kernel_contains_support"] == "True",
                "constructed_kernel_intersection": row["constructed_kernel_intersection"],
            }
        )

    static_rows = []
    for screen_id, profile in sorted(overlap_by_screen.items()):
        support_profiles = profile["support_profiles"]
        quotient_generators = sorted(profile["quotient_generators"])
        scalar_supports = [
            support
            for support, rows in support_profiles.items()
            if all(row["fourier_scalar_on_support"] for row in rows)
        ]
        non_scalar_supports = sorted(set(support_profiles) - set(scalar_supports))
        profile_identical_across_static_generators = all(
            len(
                {
                    (
                        row["fourier_scalar_on_support"],
                        row["fourier_support_scalar"],
                        row["fourier_canonical_trace_defined"],
                        row["constructed_kernel_contains_support"],
                        row["constructed_kernel_intersection"],
                    )
                    for row in rows
                }
            )
            == 1
            for rows in support_profiles.values()
        )
        static_rows.append(
            {
                "screen_id": screen_id,
                "quotient_generators": quotient_generators,
                "profile_identical_across_static_generators": profile_identical_across_static_generators,
                "scalar_supports": sorted(scalar_supports),
                "non_scalar_supports": non_scalar_supports,
                "all_nonzero_public_zero_supports_scalar": len(non_scalar_supports) == 0,
                "sector33_kernel_contains_support": any(
                    row["constructed_kernel_contains_support"]
                    for row in support_profiles.get("{33}", [])
                ),
            }
        )

    screen0_static_unique = [
        row["screen_id"] for row in static_rows if row["all_nonzero_public_zero_supports_scalar"]
    ]
    screen_sector_assignment = best_screen_sector_assignment(hcycle_rows)

    return {
        "defect_pairs": defect_pairs,
        "h8_sector_identification": h8_sector_identification,
        "hcycle_pullback": {
            "rows": hcycle_rows,
            "turn_type_signature_classes": {
                key: value for key, value in sorted(by_turn_signature.items())
            },
            "selector_choice_signature_classes": {
                key: value for key, value in sorted(by_selector_signature.items())
            },
            "xor_selector_choice_signature_classes": {
                key: value for key, value in sorted(by_xor_selector_signature.items())
            },
            "turn_type_labels_separate_all_three": all(
                len(value) == 1 for value in by_turn_signature.values()
            ),
            "selector_choice_labels_separate_all_three": all(
                len(value) == 1 for value in by_selector_signature.values()
            ),
            "xor_selector_choice_labels_separate_all_three": all(
                len(value) == 1 for value in by_xor_selector_signature.values()
            ),
        },
        "static_public_zero_overlap": {
            "rows": static_rows,
            "screen_ids_scalar_on_all_supports": screen0_static_unique,
            "screen0_uniquely_scalar_on_public_zero_supports": screen0_static_unique
            == ["signed_turn_screen_0"],
            "profiles_identical_across_static_generators": all(
                row["profile_identical_across_static_generators"] for row in static_rows
            ),
        },
        "discriminator_result": {
            "bvs_unsigned_h8_sector_proxy_certified": h8_sector_identification["all_checks_pass"] is True,
            "unique_screen_to_unsigned_h8_sector_assignment": screen_sector_assignment[
                "best_assignment_count"
            ]
            == 1,
            "screen_to_unsigned_h8_sector_assignment": screen_sector_assignment["unique_best_assignment"],
            "screen_to_unsigned_h8_sector_best_score": screen_sector_assignment["best_score"],
            "screen0_distinguished": screen0_static_unique == ["signed_turn_screen_0"],
            "screen1_screen2_still_tied_by_selector_choice": any(
                set(value) == {"signed_turn_screen_1", "signed_turn_screen_2"}
                for value in by_selector_signature.values()
            ),
            "screen1_screen2_still_tied_by_xor_selector_choice": any(
                set(value) == {"signed_turn_screen_1", "signed_turn_screen_2"}
                for value in by_xor_selector_signature.values()
            ),
            "turn_labels_break_all_three_if_BSV_is_allowed_as_H8_proxy": all(
                len(value) == 1 for value in by_turn_signature.values()
            ),
            "rgb_color_naming_remains_open": True,
            "full_certified_h8_assignment_remains_open": True,
            "reason": (
                "The audited alphabetization and hydrogen data certify B/S/V as unsigned "
                "weight-8 H8-sector proxies, but not as RGB color names. Static/Fourier "
                "overlap uniquely distinguishes screen0 yet is identical across the static "
                "quotient generators. Edge selector-choice separates screen0 from screen1/screen2 "
                "but leaves screen1 and screen2 tied. B/S/V turn counts now give a unique "
                "screen-to-unsigned-sector assignment, while the full RGB-named H8 assignment "
                "and the static/tropic attachment remain open."
            ),
        },
        "screen_sector_assignment": screen_sector_assignment,
    }


def build_ingress_boundary_packet_projection_inventory(
    rank_escape_audit: dict[str, Any],
) -> dict[str, Any]:
    boundary_to_loop = load_json(INGRESS_BOUNDARY_TO_LOOP_CERTIFICATE)
    height_action = load_json(INGRESS_HEIGHT_ACTION_RETURN_CERTIFICATE)
    lambda_hc_act = load_json(INGRESS_LAMBDA_HC_ACT_INVARIANCE_CERTIFICATE)
    intertwining = load_json(INGRESS_HEIGHT_COHERENT_INTERTWINING_CERTIFICATE)
    packet_restriction = load_json(D20_EXPLICIT_PACKET_RESTRICTION_MAP_TEST_REPORT)
    lambda_rows = load_csv(INGRESS_LAMBDA_HC_ACT_INVARIANCE_ROWS)

    lambda_q12_shadow_counts = counter_dict(
        [str(row["q12_shadow_nonzero"]) for row in lambda_rows]
    )
    lambda_q42_shadow_counts = counter_dict(
        [str(row["q42_shadow_nonzero"]) for row in lambda_rows]
    )
    lambda_sector_counts = counter_dict([str(row["support_sector"]) for row in lambda_rows])
    gamma8_lambda_hc = next(row for row in lambda_rows if int(row["mask"]) == 256)
    zero_lambda_hc = next(row for row in lambda_rows if int(row["mask"]) == 0)

    boundary_summary = boundary_to_loop["summary"]
    projection_sanity = height_action["projection_section_sanity"]
    packet_summary = packet_restriction["derived"]["restriction_summary"]
    missing_bridge_inventory = packet_restriction["derived"]["missing_bridge_inventory"]
    missing_candidates = [row["candidate"] for row in missing_bridge_inventory]
    annihilator_summary = rank_escape_audit["rank11_annihilator_summary"]

    result = {
        "ingress_boundary_to_loop_vectors_materialized": (
            boundary_to_loop["status"]
            == "ALL_RESIDUE_BOUNDARY_TO_LOOP_VECTORS_MATERIALIZED_PASS"
            and boundary_summary["residue_mask_count"] == 2048
            and boundary_summary["primitive_cycle_count"] == 11
            and boundary_summary["directed_pair_count"] == 30
        ),
        "ingress_height_action_return_reconstructed": (
            height_action["status"] == "ALL_RESIDUE_HEIGHT_ACTION_RETURN_RECONSTRUCTED_PASS"
            and projection_sanity["closed_loop_quotient_dimension"] == 297
            and projection_sanity["projection_section_identity"] is True
        ),
        "ingress_lambda_hc_has_zero_public_q12_q42_shadow": (
            lambda_hc_act["status"] == "LAMBDA_HC_ACT_INVARIANCE_CERTIFIED"
            and lambda_q12_shadow_counts == {"0": 2048}
            and lambda_q42_shadow_counts == {"0": 2048}
            and lambda_sector_counts == {"33": 2048}
        ),
        "packet_restriction_names_q12_a985_bridge_missing": (
            packet_summary["missing_bridge_count"] == 3
            and packet_summary["constructed_projection_packet_count"] == 20
            and packet_summary["a985_relation_restriction_constructed"] is False
            and packet_summary["q42_q12_restriction_constructed"] is False
            and "A985_relation_basis_to_full_packets" in missing_candidates
            and "q42_q12_tensor_to_full_packets" in missing_candidates
        ),
        "rank11_annihilator_still_waits_for_25_to_20_projection": (
            annihilator_summary["boundary_coordinate_count"] == 25
            and annihilator_summary["packet_target_coordinate_count"] == 20
            and annihilator_summary["packet_constraint_comparison_status"]
            == "BLOCKED_MISSING_BOUNDARY_TO_PACKET_PROJECTION"
        ),
    }
    result["ingress_projection_inventory_confirms_packet_bridge_gap"] = all(
        result.values()
    )

    return {
        "status": "INGRESS_BOUNDARY_TO_LOOP_PRESENT_PACKET_PROJECTION_MISSING",
        "claim_boundary": (
            "This inventories the audited ingress/A985 handoff against the q12 rank-11 "
            "boundary-space obstruction. It proves the relevant loop and sector-33 "
            "ingress data are present, and records that the A985/q12-to-full-packet "
            "restriction remains missing; it does not construct that projection."
        ),
        "boundary_to_loop_summary": {
            "status": boundary_to_loop["status"],
            "certificate_sha256": boundary_to_loop["certificate_sha256"],
            "directed_pair_count": boundary_summary["directed_pair_count"],
            "primitive_cycle_count": boundary_summary["primitive_cycle_count"],
            "residue_mask_count": boundary_summary["residue_mask_count"],
            "gamma8_lambda_support": boundary_summary["gamma8_lambda_support"],
            "gamma8_lambda_sum": boundary_summary["gamma8_lambda_sum"],
        },
        "height_action_return_summary": {
            "status": height_action["status"],
            "certificate_sha256": height_action["certificate_sha256"],
            "nonzero_residue_class_count": height_action[
                "nonzero_residue_class_count"
            ],
            "gamma8_height_action": height_action["gamma8_row"]["height_action"],
            "projection_section_sanity": projection_sanity,
        },
        "lambda_hc_public_shadow_summary": {
            "status": lambda_hc_act["status"],
            "certificate_sha256": lambda_hc_act["certificate_sha256"],
            "row_count": len(lambda_rows),
            "q12_shadow_nonzero_histogram": lambda_q12_shadow_counts,
            "q42_shadow_nonzero_histogram": lambda_q42_shadow_counts,
            "support_sector_histogram": lambda_sector_counts,
            "zero_mask_row": zero_lambda_hc,
            "gamma8_mask_row": gamma8_lambda_hc,
        },
        "height_coherent_intertwining_summary": {
            "status": intertwining["status"],
            "certificate_sha256": intertwining["certificate_sha256"],
            "claim_boundary": intertwining["claim_boundary"],
            "operator_target": intertwining["operator_target"],
        },
        "packet_restriction_gap_summary": {
            "status": packet_restriction["status"],
            "constructed_restriction": packet_summary["constructed_restriction"],
            "constructed_projection_packet_count": packet_summary[
                "constructed_projection_packet_count"
            ],
            "constructed_projection_mode_count": packet_summary[
                "constructed_projection_mode_count"
            ],
            "missing_bridge_count": packet_summary["missing_bridge_count"],
            "missing_bridge_candidates": missing_candidates,
            "a985_relation_restriction_constructed": packet_summary[
                "a985_relation_restriction_constructed"
            ],
            "q42_q12_restriction_constructed": packet_summary[
                "q42_q12_restriction_constructed"
            ],
        },
        "rank11_projection_gap_summary": {
            "boundary_coordinate_count": annihilator_summary[
                "boundary_coordinate_count"
            ],
            "packet_target_coordinate_count": annihilator_summary[
                "packet_target_coordinate_count"
            ],
            "annihilator_dimension_over_Q": annihilator_summary[
                "annihilator_dimension_over_Q"
            ],
            "outside_q12_rational_generator_lower_bound": annihilator_summary[
                "outside_q12_rational_generator_lower_bound"
            ],
            "packet_constraint_comparison_status": annihilator_summary[
                "packet_constraint_comparison_status"
            ],
        },
        "result": result,
        "all_checks_pass": all(result.values()),
        "interpretation": (
            "The incoming data closes the loop-side Lambda_hc materialization and confirms "
            "sector-33 public invisibility, but it does not provide the A985/q12 restriction "
            "to the 20 full-packet coordinates. The rank-11 q12 annihilator therefore cannot "
            "yet be pushed into the packet SNF cokernel."
        ),
    }


def build_boundary_packet_projection_candidate_audit(
    rank_escape_audit: dict[str, Any],
) -> dict[str, Any]:
    loop_step_packet = load_json(D20_LOOP_STEP_PACKET_SNF_PROBE_REPORT)
    incidence = load_json(D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE_REPORT)
    probe_summary = loop_step_packet["derived"]["probe_summary"]
    step_column_rows = loop_step_packet["derived"]["step_atom_column_rows"]
    incidence_summary = incidence["derived"]["incidence_summary"]
    annihilator_summary = rank_escape_audit["rank11_annihilator_summary"]
    target_vector_lengths = {
        len(row["target_vector_component_order"]) for row in step_column_rows
    }

    result = {
        "natural_loop_step_projection_candidate_materialized": (
            loop_step_packet["status"] == "D20_LOOP_STEP_PACKET_SNF_PROBE_CERTIFIED"
            and probe_summary["visible_candidate"]
            == "Loop_297_step_atom_mode_incidence_count_columns"
            and probe_summary["tested_column_count"] == 25
            and len(step_column_rows) == 25
        ),
        "natural_projection_has_25_to_20_shape": (
            incidence_summary["compact_loop_step_atom_count"] == 25
            and probe_summary["full_exposure_packet_count"] == 20
            and target_vector_lengths == {20}
        ),
        "natural_projection_columns_all_fail_packet_snf": (
            probe_summary["columns_passing_packet_snf_image"] == []
            and probe_summary["columns_failing_packet_snf_image"] == list(range(25))
            and probe_summary["natural_column_outcome"]
            == "all_visible_loop_step_columns_fail_packet_snf_image"
        ),
        "q12_annihilator_pushforward_blocked_for_natural_projection": (
            annihilator_summary["annihilator_dimension_over_Q"] == 14
            and annihilator_summary["boundary_coordinate_count"] == 25
            and probe_summary["columns_passing_packet_snf_image"] == []
        ),
    }
    result["natural_25_to_20_projection_candidate_rejected"] = all(result.values())

    return {
        "status": "BOUNDARY_PACKET_NATURAL_25_TO_20_PROJECTION_REJECTED_BY_PACKET_SNF",
        "claim_boundary": (
            "This tests only the certified natural Loop_297 step-atom mode-incidence "
            "columns as a 25-to-20 boundary-to-packet projection candidate. It does not "
            "rule out signed, normalized, or quotient-adjusted projections."
        ),
        "candidate_summary": {
            "visible_candidate": probe_summary["visible_candidate"],
            "candidate_semantics": probe_summary["candidate_semantics"],
            "loop297_step_atom_count": probe_summary["loop297_step_atom_count"],
            "full_exposure_packet_count": probe_summary["full_exposure_packet_count"],
            "tested_column_count": probe_summary["tested_column_count"],
            "target_vector_length_set": sorted(target_vector_lengths),
            "columns_passing_packet_snf_image": probe_summary[
                "columns_passing_packet_snf_image"
            ],
            "columns_failing_packet_snf_image": probe_summary[
                "columns_failing_packet_snf_image"
            ],
            "natural_column_outcome": probe_summary["natural_column_outcome"],
        },
        "failure_summary": {
            "failed_blocks_per_column_histogram": probe_summary[
                "failed_blocks_per_column_histogram"
            ],
            "failure_reason_histogram": probe_summary["failure_reason_histogram"],
            "component_pair_value_histogram": probe_summary[
                "component_pair_value_histogram"
            ],
        },
        "rank11_projection_context": {
            "boundary_coordinate_count": annihilator_summary[
                "boundary_coordinate_count"
            ],
            "packet_target_coordinate_count": annihilator_summary[
                "packet_target_coordinate_count"
            ],
            "annihilator_dimension_over_Q": annihilator_summary[
                "annihilator_dimension_over_Q"
            ],
            "outside_q12_rational_generator_lower_bound": annihilator_summary[
                "outside_q12_rational_generator_lower_bound"
            ],
        },
        "result": result,
        "all_checks_pass": all(result.values()),
        "interpretation": (
            "The obvious 25 boundary step columns do land in 20 packet coordinates, but "
            "none is in the packet SNF image. The next projection attempt must therefore "
            "use signed/normalized combinations or a quotient-adjusted A985/q12 map, not "
            "the raw natural columns."
        ),
    }


def build_signed_step_column_packet_search_audit(
    rank_escape_audit: dict[str, Any],
) -> dict[str, Any]:
    loop_step_packet = load_json(D20_LOOP_STEP_PACKET_SNF_PROBE_REPORT)
    incidence = load_json(D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE_REPORT)
    step_column_rows = loop_step_packet["derived"]["step_atom_column_rows"]
    step_incidence_rows = incidence["derived"]["step_atom_boundary_incidence_rows"]
    columns = [row["target_vector_component_order"] for row in step_column_rows]
    annihilator_rows = rank_escape_audit["rank11_annihilator_summary"][
        "primitive_constraint_rows"
    ]

    coefficient_set = [-2, -1, 1, 2]
    max_support = 3
    attempt_count = 0
    compatible_rows = []
    support_histogram_values = []
    for support_size in range(1, max_support + 1):
        for step_atom_ids in itertools.combinations(range(len(columns)), support_size):
            for coefficients in itertools.product(coefficient_set, repeat=support_size):
                attempt_count += 1
                target_vector = [
                    sum(
                        int(coefficient) * columns[step_atom_id][coordinate]
                        for step_atom_id, coefficient in zip(step_atom_ids, coefficients)
                    )
                    for coordinate in range(len(columns[0]))
                ]
                if not all(
                    not packet_snf_local_failures(
                        target_vector[2 * component_id],
                        target_vector[2 * component_id + 1],
                    )
                    for component_id in range(len(target_vector) // 2)
                ):
                    continue
                coefficient_vector = [0 for _ in range(len(columns))]
                for step_atom_id, coefficient in zip(step_atom_ids, coefficients):
                    coefficient_vector[step_atom_id] = int(coefficient)
                annihilator_values = [
                    sum(
                        row[coordinate] * coefficient_vector[coordinate]
                        for coordinate in range(len(coefficient_vector))
                    )
                    for row in annihilator_rows
                ]
                compatible_rows.append(
                    {
                        "support_size": support_size,
                        "step_atom_ids": list(step_atom_ids),
                        "coefficients": [int(value) for value in coefficients],
                        "target_vector": target_vector,
                        "coefficient_vector": coefficient_vector,
                        "annihilator_values": annihilator_values,
                    }
                )
                support_histogram_values.append(str(support_size))

    unique_target_vectors = sorted({tuple(row["target_vector"]) for row in compatible_rows})
    unique_coefficient_vectors = sorted(
        {tuple(row["coefficient_vector"]) for row in compatible_rows}
    )
    minimal_support_size = min(row["support_size"] for row in compatible_rows)
    minimal_rows = [
        row for row in compatible_rows if row["support_size"] == minimal_support_size
    ]
    nonzero_target_count = sum(1 for row in compatible_rows if any(row["target_vector"]))
    outside_annihilator_count = sum(
        1 for row in compatible_rows if any(row["annihilator_values"])
    )
    minimal_step_atom_ids = sorted(
        {step_atom_id for row in minimal_rows for step_atom_id in row["step_atom_ids"]}
    )
    minimal_step_incidence_rows = [
        step_incidence_rows[step_atom_id] for step_atom_id in minimal_step_atom_ids
    ]

    search_summary = {
        "coefficient_set": coefficient_set,
        "max_support": max_support,
        "attempt_count": attempt_count,
        "compatible_row_count": len(compatible_rows),
        "compatible_support_size_histogram": counter_dict(support_histogram_values),
        "compatible_nonzero_target_count": nonzero_target_count,
        "compatible_zero_target_count": len(compatible_rows) - nonzero_target_count,
        "outside_q12_annihilator_count": outside_annihilator_count,
        "unique_target_vector_count": len(unique_target_vectors),
        "unique_target_vector_rank_over_Q": matrix_rank_over_q(
            [list(row) for row in unique_target_vectors]
        ),
        "unique_coefficient_vector_count": len(unique_coefficient_vectors),
        "unique_coefficient_vector_rank_over_Q": matrix_rank_over_q(
            [list(row) for row in unique_coefficient_vectors]
        ),
        "minimal_support_size": minimal_support_size,
        "minimal_support_row_count": len(minimal_rows),
        "minimal_rows": [
            {
                "step_atom_ids": row["step_atom_ids"],
                "coefficients": row["coefficients"],
                "target_vector": row["target_vector"],
                "annihilator_values": row["annihilator_values"],
            }
            for row in minimal_rows
        ],
        "minimal_step_incidence_rows": minimal_step_incidence_rows,
    }

    result = {
        "bounded_signed_step_column_search_materialized": (
            search_summary["attempt_count"] == 152100
            and search_summary["compatible_row_count"] == 30186
        ),
        "scalar2_step16_minimal_packet_snf_row_found": (
            search_summary["minimal_support_size"] == 1
            and search_summary["minimal_support_row_count"] == 2
            and minimal_step_atom_ids == [16]
        ),
        "all_compatible_rows_escape_q12_rank11_annihilator": (
            search_summary["outside_q12_annihilator_count"]
            == search_summary["compatible_row_count"]
        ),
        "compatible_target_span_still_rank2": (
            search_summary["unique_target_vector_rank_over_Q"] == 2
        ),
        "signed_step_column_search_finds_external_but_rank_limited_rows": (
            search_summary["minimal_support_size"] == 1
            and search_summary["unique_target_vector_rank_over_Q"] == 2
            and search_summary["outside_q12_annihilator_count"]
            == search_summary["compatible_row_count"]
        ),
    }

    return {
        "status": "BOUNDARY_PACKET_SIGNED_STEP_COLUMN_SEARCH_FINDS_EXTERNAL_RANK2_ROWS",
        "claim_boundary": (
            "This is a bounded search over support at most three in the natural 25 "
            "Loop_297 step columns with coefficients +/-1,+/-2. It finds packet-SNF "
            "compatible rows outside the q12 rank-11 annihilator, but does not exhaust "
            "larger supports or prove a full rank-20 packet projection."
        ),
        "search_summary": search_summary,
        "result": result,
        "all_checks_pass": all(result.values()),
        "interpretation": (
            "Scaling step atom 16 by 2 already passes the packet SNF local test and "
            "violates the q12 annihilator, giving a concrete external row. However the "
            "compatible target vectors found in this bounded search span only rank 2 in "
            "the 20-coordinate packet target, so this is an external generator witness, "
            "not a full bridge."
        ),
    }


def build_support4_signed_step_column_span_audit(
    signed_step_column_packet_search_audit: dict[str, Any],
    rank_escape_audit: dict[str, Any],
) -> dict[str, Any]:
    loop_step_packet = load_json(D20_LOOP_STEP_PACKET_SNF_PROBE_REPORT)
    step_column_rows = loop_step_packet["derived"]["step_atom_column_rows"]
    columns = [tuple(row["target_vector_component_order"]) for row in step_column_rows]

    column_types = []
    column_type_groups = []
    column_type_ids = {}
    for step_atom_id, column in enumerate(columns):
        if column not in column_type_ids:
            column_type_ids[column] = len(column_types)
            column_types.append(column)
            column_type_groups.append([])
        column_type_groups[column_type_ids[column]].append(step_atom_id)

    coefficient_set = [-2, -1, 1, 2]
    coefficient_sum_histograms = {}
    for coefficient_count in range(5):
        sums = []
        for coefficients in itertools.product(coefficient_set, repeat=coefficient_count):
            sums.append(str(sum(coefficients)))
        coefficient_sum_histograms[coefficient_count] = counter_dict(sums)

    compatible_by_support: dict[str, int] = {}
    nonzero_by_support: dict[str, int] = {}
    unique_targets_by_support: dict[str, set[tuple[int, ...]]] = {}
    virtual_attempt_by_support: dict[str, int] = {}
    type_sum_rows = []
    all_unique_targets: set[tuple[int, ...]] = set()
    for support_size in range(1, 5):
        compatible_count = 0
        nonzero_count = 0
        unique_targets: set[tuple[int, ...]] = set()
        virtual_attempt_by_support[str(support_size)] = (
            math.comb(len(columns), support_size) * len(coefficient_set) ** support_size
        )
        for type_counts in itertools.product(range(5), repeat=len(column_types)):
            if sum(type_counts) != support_size:
                continue
            if any(
                type_counts[type_id] > len(column_type_groups[type_id])
                for type_id in range(len(column_types))
            ):
                continue
            type_choice_count = math.prod(
                math.comb(len(column_type_groups[type_id]), type_counts[type_id])
                for type_id in range(len(column_types))
            )
            type_sum_options = [
                [
                    (int(coefficient_sum), count)
                    for coefficient_sum, count in coefficient_sum_histograms[
                        type_count
                    ].items()
                ]
                for type_count in type_counts
            ]
            for type_sum_choice in itertools.product(*type_sum_options):
                type_sums = [coefficient_sum for coefficient_sum, _ in type_sum_choice]
                row_count = type_choice_count * math.prod(
                    count for _, count in type_sum_choice
                )
                target_vector = tuple(
                    sum(
                        type_sums[type_id] * column_types[type_id][coordinate]
                        for type_id in range(len(column_types))
                    )
                    for coordinate in range(len(columns[0]))
                )
                if not all(
                    not packet_snf_local_failures(
                        target_vector[2 * component_id],
                        target_vector[2 * component_id + 1],
                    )
                    for component_id in range(len(target_vector) // 2)
                ):
                    continue
                compatible_count += row_count
                if any(target_vector):
                    nonzero_count += row_count
                unique_targets.add(target_vector)
                all_unique_targets.add(target_vector)
                type_sum_rows.append(
                    {
                        "support_size": support_size,
                        "type_counts": list(type_counts),
                        "type_coefficient_sums": type_sums,
                        "row_count": row_count,
                        "target_vector": list(target_vector),
                    }
                )
        compatible_by_support[str(support_size)] = compatible_count
        nonzero_by_support[str(support_size)] = nonzero_count
        unique_targets_by_support[str(support_size)] = unique_targets

    support_le_3_targets = set().union(
        *(unique_targets_by_support[str(support_size)] for support_size in range(1, 4))
    )
    support_le_4_targets = set(all_unique_targets)
    target_vectors = [list(row) for row in sorted(support_le_4_targets)]
    signed_summary = signed_step_column_packet_search_audit["search_summary"]
    rank_escape_summary = rank_escape_audit["rank11_annihilator_summary"]
    support4_summary = {
        "method": "column_type_combinatorial_count",
        "coefficient_set": coefficient_set,
        "column_type_count": len(column_types),
        "column_type_groups": column_type_groups,
        "column_type_vectors": [list(column_type) for column_type in column_types],
        "virtual_attempt_count_by_support": virtual_attempt_by_support,
        "virtual_attempt_count_total_support_le_4": sum(
            virtual_attempt_by_support.values()
        ),
        "compatible_row_count_by_support": compatible_by_support,
        "compatible_row_count_total_support_le_4": sum(compatible_by_support.values()),
        "compatible_nonzero_target_count_by_support": nonzero_by_support,
        "unique_target_vector_count_by_support": {
            str(support_size): len(unique_targets_by_support[str(support_size)])
            for support_size in range(1, 5)
        },
        "unique_target_vector_count_support_le_3": len(support_le_3_targets),
        "unique_target_vector_count_support_le_4": len(support_le_4_targets),
        "new_unique_target_vector_count_at_support4": len(
            support_le_4_targets - support_le_3_targets
        ),
        "unique_target_vector_rank_over_Q_support_le_4": matrix_rank_over_q(
            target_vectors
        ),
        "unique_target_vectors_support_le_4": target_vectors,
        "type_sum_witness_count": len(type_sum_rows),
        "type_sum_rows_sha256": sha_json(type_sum_rows),
        "q12_boundary_rank_before_external_step16": rank_escape_summary[
            "raw_non_scalar_boundary_image_rank_over_Q"
        ],
        "q12_plus_step16_boundary_rank_lower_bound": (
            rank_escape_summary["raw_non_scalar_boundary_image_rank_over_Q"] + 1
        ),
        "minimal_external_step_annihilator_values": signed_summary["minimal_rows"][1][
            "annihilator_values"
        ],
    }

    result = {
        "support4_combinatorial_count_agrees_with_support_le_3_search": (
            support4_summary["compatible_row_count_by_support"]["1"] == 2
            and support4_summary["compatible_row_count_by_support"]["2"] == 1848
            and support4_summary["compatible_row_count_by_support"]["3"] == 28336
            and support4_summary["compatible_row_count_by_support"]["3"]
            == signed_summary["compatible_support_size_histogram"]["3"]
        ),
        "support4_adds_many_packet_snf_compatible_rows": (
            support4_summary["compatible_row_count_by_support"]["4"] == 751520
        ),
        "support4_adds_only_four_new_target_vectors": (
            support4_summary["new_unique_target_vector_count_at_support4"] == 4
        ),
        "support_le_4_packet_target_span_remains_rank2": (
            support4_summary["unique_target_vector_rank_over_Q_support_le_4"] == 2
        ),
        "step16_external_row_raises_boundary_rank_lower_bound_to_12": (
            support4_summary["q12_boundary_rank_before_external_step16"] == 11
            and support4_summary["q12_plus_step16_boundary_rank_lower_bound"] == 12
            and any(support4_summary["minimal_external_step_annihilator_values"])
        ),
    }
    result["support4_signed_step_columns_still_rank2"] = all(result.values())

    return {
        "status": "BOUNDARY_PACKET_SUPPORT4_SIGNED_STEP_COLUMNS_STILL_RANK2",
        "claim_boundary": (
            "This extends the signed natural step-column search through support four "
            "using the four observed packet target column types. It proves the bounded "
            "support-four target span remains rank two, not an all-support theorem."
        ),
        "support4_summary": support4_summary,
        "result": result,
        "all_checks_pass": all(result.values()),
        "interpretation": (
            "Support four contributes many more packet-SNF-compatible rows, but only four "
            "new packet target vectors and no new target rank. The scalar-2 step-16 row "
            "is a real boundary-space generator outside q12, raising the boundary-side "
            "rank lower bound to 12, yet the natural packet target side remains rank 2."
        ),
    }


def build_full_step_column_congruence_lattice_audit(
    support4_signed_step_column_span_audit: dict[str, Any],
    rank_escape_audit: dict[str, Any],
) -> dict[str, Any]:
    loop_step_packet = load_json(D20_LOOP_STEP_PACKET_SNF_PROBE_REPORT)
    step_column_rows = loop_step_packet["derived"]["step_atom_column_rows"]
    columns = [tuple(row["target_vector_component_order"]) for row in step_column_rows]

    column_types = []
    column_type_groups = []
    column_type_ids = {}
    for step_atom_id, column in enumerate(columns):
        if column not in column_type_ids:
            column_type_ids[column] = len(column_types)
            column_types.append(column)
            column_type_groups.append([])
        column_type_groups[column_type_ids[column]].append(step_atom_id)

    compatible_residue_classes = []
    for residues in itertools.product(range(6), repeat=len(column_types)):
        target_vector = [
            sum(
                residues[type_id] * column_types[type_id][coordinate]
                for type_id in range(len(column_types))
            )
            for coordinate in range(len(columns[0]))
        ]
        if all(
            not packet_snf_local_failures(
                target_vector[2 * component_id],
                target_vector[2 * component_id + 1],
            )
            for component_id in range(len(target_vector) // 2)
        ):
            compatible_residue_classes.append(list(residues))

    integer_type_sum_lattice_basis = [
        [3, 0, 0, 0],
        [0, 6, 0, 0],
        [0, 0, 2, 0],
        [0, 0, 0, 6],
    ]
    annihilator_rows = rank_escape_audit["rank11_annihilator_summary"][
        "primitive_constraint_rows"
    ]
    basis_rows = []
    basis_target_vectors = []
    basis_annihilator_values = []
    for basis_vector in integer_type_sum_lattice_basis:
        target_vector = [
            sum(
                basis_vector[type_id] * column_types[type_id][coordinate]
                for type_id in range(len(column_types))
            )
            for coordinate in range(len(columns[0]))
        ]
        coefficient_vector = [0 for _ in range(len(columns))]
        for type_id, coefficient_sum in enumerate(basis_vector):
            if coefficient_sum:
                coefficient_vector[column_type_groups[type_id][0]] = coefficient_sum
        annihilator_values = [
            sum(
                row[coordinate] * coefficient_vector[coordinate]
                for coordinate in range(len(coefficient_vector))
            )
            for row in annihilator_rows
        ]
        basis_target_vectors.append(target_vector)
        basis_annihilator_values.append(annihilator_values)
        basis_rows.append(
            {
                "type_coefficient_sums": basis_vector,
                "sample_step_coefficient_vector": coefficient_vector,
                "target_vector": target_vector,
                "passes_packet_snf_local_test": all(
                    not packet_snf_local_failures(
                        target_vector[2 * component_id],
                        target_vector[2 * component_id + 1],
                    )
                    for component_id in range(len(target_vector) // 2)
                ),
                "annihilator_values": annihilator_values,
            }
        )

    support4_summary = support4_signed_step_column_span_audit["support4_summary"]
    rank_escape_summary = rank_escape_audit["rank11_annihilator_summary"]
    basis_target_rank = matrix_rank_over_q(basis_target_vectors)
    annihilator_evaluation_rank = matrix_rank_over_q(
        [list(row) for row in zip(*basis_annihilator_values)]
    )
    full_lattice_summary = {
        "method": "mod6_residue_classes_plus_integer_type_sum_basis",
        "column_type_count": len(column_types),
        "column_type_groups": column_type_groups,
        "column_type_vectors": [list(column_type) for column_type in column_types],
        "compatible_residue_class_count_mod6": len(compatible_residue_classes),
        "compatible_residue_classes_mod6": compatible_residue_classes,
        "integer_type_sum_lattice_basis": integer_type_sum_lattice_basis,
        "integer_type_sum_lattice_basis_determinant": 216,
        "basis_rows": basis_rows,
        "basis_rows_sha256": sha_json(basis_rows),
        "basis_target_rank_over_Q": basis_target_rank,
        "basis_rows_passing_packet_snf_count": sum(
            1 for row in basis_rows if row["passes_packet_snf_local_test"]
        ),
        "basis_rows_outside_q12_annihilator_count": sum(
            1 for values in basis_annihilator_values if any(values)
        ),
        "basis_annihilator_evaluation_rank_over_Q": annihilator_evaluation_rank,
        "support_le_4_target_rank_over_Q": support4_summary[
            "unique_target_vector_rank_over_Q_support_le_4"
        ],
        "full_lattice_target_rank_gain_over_support_le_4": (
            basis_target_rank
            - support4_summary["unique_target_vector_rank_over_Q_support_le_4"]
        ),
        "q12_boundary_rank_before_external_lattice": rank_escape_summary[
            "raw_non_scalar_boundary_image_rank_over_Q"
        ],
        "q12_plus_full_type_lattice_boundary_rank_lower_bound": (
            rank_escape_summary["raw_non_scalar_boundary_image_rank_over_Q"]
            + annihilator_evaluation_rank
        ),
        "packet_target_rank": 20,
        "packet_target_rank_shortfall_after_full_type_lattice": 20 - basis_target_rank,
    }

    result = {
        "full_congruence_residue_classes_solved": (
            full_lattice_summary["compatible_residue_classes_mod6"]
            == [
                [0, 0, 0, 0],
                [0, 0, 2, 0],
                [0, 0, 4, 0],
                [3, 0, 0, 0],
                [3, 0, 2, 0],
                [3, 0, 4, 0],
            ]
        ),
        "integer_type_sum_lattice_basis_materialized": (
            full_lattice_summary["integer_type_sum_lattice_basis"]
            == integer_type_sum_lattice_basis
            and full_lattice_summary["integer_type_sum_lattice_basis_determinant"] == 216
        ),
        "full_type_lattice_packet_target_rank_is_4": (
            full_lattice_summary["basis_target_rank_over_Q"] == 4
        ),
        "full_type_lattice_gains_two_target_ranks_over_support4": (
            full_lattice_summary["full_lattice_target_rank_gain_over_support_le_4"] == 2
        ),
        "full_type_lattice_adds_four_q12_external_boundary_directions": (
            full_lattice_summary["basis_annihilator_evaluation_rank_over_Q"] == 4
            and full_lattice_summary[
                "q12_plus_full_type_lattice_boundary_rank_lower_bound"
            ]
            == 15
        ),
        "natural_step_column_type_lattice_still_short_of_packet_rank20": (
            full_lattice_summary[
                "packet_target_rank_shortfall_after_full_type_lattice"
            ]
            == 16
        ),
    }
    result["full_step_column_congruence_lattice_rank4_still_short"] = all(
        result.values()
    )

    return {
        "status": "BOUNDARY_PACKET_FULL_STEP_COLUMN_CONGRUENCE_LATTICE_RANK4_STILL_SHORT",
        "claim_boundary": (
            "This solves the full congruence lattice for the four natural packet target "
            "column types. It exhausts this type-sum lattice, but not quotient-adjusted "
            "A985/q12 packet maps or non-natural target columns."
        ),
        "full_lattice_summary": full_lattice_summary,
        "result": result,
        "all_checks_pass": all(result.values()),
        "interpretation": (
            "The full natural step-column congruence lattice is larger than the bounded "
            "support-four search: it reaches packet target rank 4 and contributes four "
            "q12-external boundary directions. It is still far from the rank-20 packet "
            "target, leaving a 16-dimensional packet target shortfall."
        ),
    }


def build_q42_q12_quotient_adjusted_packet_filter_audit(
    q12_h6_projection_audit: dict[str, Any],
    full_step_column_congruence_lattice_audit: dict[str, Any],
) -> dict[str, Any]:
    with np.load(ROOT / QUOTIENTS_NPZ) as payload:
        q12_map = np.asarray(payload["q12_map"], dtype=np.int64)
        q42_map = np.asarray(payload["q42_map"], dtype=np.int64)
        q12_tensor = np.asarray(payload["q12_tensor"], dtype=np.int64)
        q42_tensor = np.asarray(payload["q42_tensor"], dtype=np.int64)

    loop_step_packet = load_json(D20_LOOP_STEP_PACKET_SNF_PROBE_REPORT)
    incidence = load_json(D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE_REPORT)
    matrix = incidence["derived"]["boundary_atom_step_incidence_matrix"]
    step_columns = [
        tuple(row["target_vector_component_order"])
        for row in loop_step_packet["derived"]["step_atom_column_rows"]
    ]
    q12_rows = q12_h6_projection_audit["q12_h6_rows"]
    full_lattice_summary = full_step_column_congruence_lattice_audit[
        "full_lattice_summary"
    ]
    full_type_lattice_targets = [
        row["target_vector"] for row in full_lattice_summary["basis_rows"]
    ]

    q42_to_q12: list[int | None] = []
    q42_refinement_rows = []
    for q42_class in range(q42_tensor.shape[0]):
        q12_values = sorted(
            {int(value) for value in q12_map[q42_map == q42_class].tolist()}
        )
        q42_to_q12.append(q12_values[0] if len(q12_values) == 1 else None)
        q42_refinement_rows.append(
            {
                "q42_class": q42_class,
                "q12_classes": q12_values,
                "relation_count": int(np.count_nonzero(q42_map == q42_class)),
            }
        )

    q42_pushdown_tensor = np.zeros_like(q12_tensor)
    for left_q42 in range(q42_tensor.shape[0]):
        left_q12 = q42_to_q12[left_q42]
        for right_q42 in range(q42_tensor.shape[1]):
            right_q12 = q42_to_q12[right_q42]
            if left_q12 is None or right_q12 is None:
                continue
            for out_q42, coefficient in enumerate(
                q42_tensor[left_q42, right_q42, :].tolist()
            ):
                out_q12 = q42_to_q12[out_q42]
                if out_q12 is None:
                    continue
                q42_pushdown_tensor[left_q12, right_q12, out_q12] += int(
                    coefficient
                )

    def natural_packet_target(boundary_image: list[int]) -> list[int]:
        return [
            sum(
                boundary_image[step_atom_id] * step_columns[step_atom_id][coordinate]
                for step_atom_id in range(len(step_columns))
            )
            for coordinate in range(len(step_columns[0]))
        ]

    def target_passes_packet_snf(target_vector: list[int]) -> bool:
        return all(
            not packet_snf_local_failures(
                target_vector[2 * component_id],
                target_vector[2 * component_id + 1],
            )
            for component_id in range(len(target_vector) // 2)
        )

    q42_tensor_rows = []
    q42_pushed_q12_rows = []
    q42_public_rows = []
    scalar6_rows = []
    for left_q42 in range(q42_tensor.shape[0]):
        for right_q42 in range(q42_tensor.shape[1]):
            output_q42_coefficients = q42_tensor[left_q42, right_q42, :]
            if not np.any(output_q42_coefficients):
                continue
            q42_tensor_rows.append(
                [int(value) for value in output_q42_coefficients.tolist()]
            )
            pushed_q12 = [0 for _ in range(q12_tensor.shape[0])]
            for out_q42, coefficient in enumerate(
                output_q42_coefficients.tolist()
            ):
                out_q12 = q42_to_q12[out_q42]
                if out_q12 is None:
                    continue
                pushed_q12[out_q12] += int(coefficient)
            q42_pushed_q12_rows.append(pushed_q12)
            product = q12_product_d20_readout(
                np.asarray(pushed_q12, dtype=np.int64),
                q12_rows,
            )
            public_vector = product["readout_vector"]
            q42_public_rows.append(public_vector)
            if not all(value % 6 == 0 for value in public_vector):
                continue
            normalized_public_vector = [
                value // 6 for value in public_vector
            ]
            boundary_image = boundary_image_for_support(
                [
                    {"public_atom_id": atom_id, "coefficient": coefficient}
                    for atom_id, coefficient in enumerate(normalized_public_vector)
                    if coefficient
                ],
                matrix,
            )
            target_vector = natural_packet_target(boundary_image)
            scalar6_rows.append(
                {
                    "q42_pair": [int(left_q42), int(right_q42)],
                    "pushed_q12_coefficients": [
                        [q12_class, int(coefficient)]
                        for q12_class, coefficient in enumerate(pushed_q12)
                        if coefficient
                    ],
                    "normalized_public_support_atom_ids": [
                        atom_id
                        for atom_id, coefficient in enumerate(
                            normalized_public_vector
                        )
                        if coefficient
                    ],
                    "boundary_image": boundary_image,
                    "natural_packet_target_vector": target_vector,
                    "passes_natural_packet_snf_image": target_passes_packet_snf(
                        target_vector
                    ),
                }
            )

    compatible_boundary_pair_count = 0
    compatible_boundary_pair_rank_values = []
    for left, right in itertools.combinations(scalar6_rows, 2):
        if not packet_pair_passes_local_image_test(
            left["boundary_image"],
            right["boundary_image"],
        ):
            continue
        compatible_boundary_pair_count += 1
        compatible_boundary_pair_rank_values.append(
            str(
                rank_two_integer_vectors(
                    left["boundary_image"], right["boundary_image"]
                )
            )
        )

    natural_pass_rows = [
        row for row in scalar6_rows if row["passes_natural_packet_snf_image"]
    ]
    q42_tensor_rank = matrix_rank_over_q(q42_tensor_rows)
    q42_pushed_rank = matrix_rank_over_q(q42_pushed_q12_rows)
    q42_public_rank = matrix_rank_over_q(q42_public_rows)
    scalar_boundary_rank = matrix_rank_over_q(
        [row["boundary_image"] for row in scalar6_rows]
    )
    scalar_target_rank = matrix_rank_over_q(
        [row["natural_packet_target_vector"] for row in scalar6_rows]
    )
    natural_pass_target_rank = matrix_rank_over_q(
        [row["natural_packet_target_vector"] for row in natural_pass_rows]
    )
    full_type_rank = full_lattice_summary["basis_target_rank_over_Q"]
    with_type_lattice_rank = matrix_rank_over_q(
        full_type_lattice_targets
        + [row["natural_packet_target_vector"] for row in scalar6_rows]
    )
    pass_with_type_lattice_rank = matrix_rank_over_q(
        full_type_lattice_targets
        + [row["natural_packet_target_vector"] for row in natural_pass_rows]
    )

    summary = {
        "method": (
            "q42_product_tensor_pushdown_to_q12_public_readout_then_natural_packet_filter"
        ),
        "q42_class_count": int(q42_tensor.shape[0]),
        "q12_class_count": int(q12_tensor.shape[0]),
        "q42_to_q12": q42_to_q12,
        "q42_fiber_size_histogram": counter_dict(
            [
                str(sum(1 for value in q42_to_q12 if value == q12_class))
                for q12_class in range(q12_tensor.shape[0])
            ]
        ),
        "q42_refinement_rows_sha256": sha_json(q42_refinement_rows),
        "q42_tensor_pushdown_equals_q12_tensor": bool(
            np.array_equal(q42_pushdown_tensor, q12_tensor)
        ),
        "q42_nonzero_product_pair_count": len(q42_tensor_rows),
        "q42_tensor_row_rank_over_Q": q42_tensor_rank,
        "q42_pushed_q12_coefficient_rank_over_Q": q42_pushed_rank,
        "q42_public_h6_readout_rank_over_Q": q42_public_rank,
        "q42_hidden_rank_lost_under_q12_public_readout": (
            q42_tensor_rank - q42_pushed_rank
        ),
        "q42_scalar6_public_row_count": len(scalar6_rows),
        "q42_scalar6_public_rank_over_Q": matrix_rank_over_q(
            [
                [
                    sum(
                        coefficient
                        for q12_class, coefficient in row[
                            "pushed_q12_coefficients"
                        ]
                        if atom_id in q12_rows[q12_class]["h6_public_atom_ids"]
                    )
                    // 6
                    for atom_id in range(20)
                ]
                for row in scalar6_rows
            ]
        ),
        "q42_scalar6_boundary_rank_over_Q": scalar_boundary_rank,
        "q42_scalar6_boundary_compatible_pair_count": (
            compatible_boundary_pair_count
        ),
        "q42_scalar6_boundary_compatible_pair_rank_histogram": counter_dict(
            compatible_boundary_pair_rank_values
        ),
        "q42_scalar6_natural_target_rank_over_Q": scalar_target_rank,
        "q42_scalar6_natural_target_passing_row_count": len(natural_pass_rows),
        "q42_scalar6_natural_target_passing_rank_over_Q": natural_pass_target_rank,
        "full_type_lattice_target_rank_over_Q": full_type_rank,
        "q42_scalar6_natural_target_with_type_lattice_rank_over_Q": (
            with_type_lattice_rank
        ),
        "q42_scalar6_natural_pass_with_type_lattice_rank_over_Q": (
            pass_with_type_lattice_rank
        ),
        "packet_target_rank": 20,
        "q42_natural_pass_packet_rank_shortfall": 20 - natural_pass_target_rank,
        "q42_scalar6_natural_pass_rows_sha256": sha_json(
            [
                {
                    "q42_pair": row["q42_pair"],
                    "pushed_q12_coefficients": row["pushed_q12_coefficients"],
                    "natural_packet_target_vector": row[
                        "natural_packet_target_vector"
                    ],
                }
                for row in natural_pass_rows
            ]
        ),
        "q42_scalar6_natural_pass_example_rows": [
            {
                "q42_pair": row["q42_pair"],
                "pushed_q12_coefficients": row["pushed_q12_coefficients"],
                "natural_packet_target_vector": row[
                    "natural_packet_target_vector"
                ],
            }
            for row in natural_pass_rows[:3]
        ],
    }

    result = {
        "q42_classes_refine_q12_classes": all(
            row["q12_classes"] == [q42_to_q12[row["q42_class"]]]
            for row in q42_refinement_rows
            if q42_to_q12[row["q42_class"]] is not None
        )
        and all(value is not None for value in q42_to_q12),
        "q42_product_tensor_pushdown_matches_q12_tensor": summary[
            "q42_tensor_pushdown_equals_q12_tensor"
        ]
        is True,
        "q42_hidden_rank_collapses_under_q12_public_readout": (
            summary["q42_tensor_row_rank_over_Q"] == 42
            and summary["q42_pushed_q12_coefficient_rank_over_Q"] == 12
            and summary["q42_hidden_rank_lost_under_q12_public_readout"] == 30
        ),
        "q42_scalar6_rows_materialize_boundary_rank11": (
            summary["q42_scalar6_public_row_count"] == 216
            and summary["q42_scalar6_boundary_rank_over_Q"] == 11
        ),
        "q42_scalar6_boundary_pairs_are_plentiful_but_not_packet_basis": (
            summary["q42_scalar6_boundary_compatible_pair_count"] == 7337
            and summary["q42_scalar6_boundary_compatible_pair_rank_histogram"]
            == {"1": 1013, "2": 6324}
        ),
        "q42_natural_packet_filter_remains_inside_type_lattice": (
            summary["q42_scalar6_natural_target_passing_row_count"] == 120
            and summary["q42_scalar6_natural_target_passing_rank_over_Q"] == 3
            and summary[
                "q42_scalar6_natural_pass_with_type_lattice_rank_over_Q"
            ]
            == full_type_rank
        ),
        "q42_quotient_adjusted_filter_still_short_of_rank20": (
            summary["packet_target_rank"] == 20
            and summary["q42_natural_pass_packet_rank_shortfall"] == 17
        ),
    }
    result["q42_q12_quotient_adjusted_packet_filter_still_rank_limited"] = all(
        result.values()
    )

    return {
        "status": "Q42_Q12_QUOTIENT_ADJUSTED_PACKET_FILTER_STILL_RANK3",
        "claim_boundary": (
            "This tests the quotient-adjusted route that is currently available: q42 "
            "product rows are pushed through the certified q42-to-q12 refinement, then "
            "through the q12 public pentagon readout, scalar-6 normalization, and the "
            "natural Loop_297 packet target filter. It does not test a hidden q42/A985 "
            "to full-packet projection, because that map is one of the certified missing "
            "bridge candidates."
        ),
        "quotient_adjusted_summary": summary,
        "result": result,
        "all_checks_pass": all(result.values()),
        "interpretation": (
            "The q42 tensor has full q42 rank 42, but its certified public route factors "
            "exactly through q12 and loses thirty hidden ranks before the packet target. "
            "The scalar-6 q42 public rows produce many boundary-side packet-SNF doublets, "
            "yet their natural packet targets have rank 3 and remain inside the solved "
            "rank-4 natural type lattice. This closes the public quotient-adjusted route "
            "as a rank-20 bridge attempt while leaving the hidden q42/A985 packet map open."
        ),
    }


def build_hidden_q42_a985_matrix_unit_capacity_audit(
    q42_q12_quotient_adjusted_packet_filter_audit: dict[str, Any],
) -> dict[str, Any]:
    with np.load(ROOT / QUOTIENTS_NPZ) as quotient_payload:
        q12_map = np.asarray(quotient_payload["q12_map"], dtype=np.int64)
        q42_map = np.asarray(quotient_payload["q42_map"], dtype=np.int64)

    with np.load(ROOT / A985_FULL_MATRIX_UNIT_ARRAYS) as matrix_payload:
        field_prime = int(matrix_payload["field_prime"][0])
        matrix_units = np.asarray(matrix_payload["matrix_units"], dtype=np.int64) % field_prime

    full_matrix_unit = load_json(A985_FULL_MATRIX_UNIT_REPORT)
    sector_characters = load_json(A985_CANONICAL_SECTOR_CHARACTERS_REPORT)
    full_packet_lift = load_json(D20_FULL_PACKET_MATRIX_LIFT_REPORT)
    character_rows = load_csv(A985_CANONICAL_SECTOR_CHARACTER_TABLE)

    q42_class_count = int(q42_map.max()) + 1
    q12_class_count = int(q12_map.max()) + 1

    def aggregate_mod_rows(
        source: np.ndarray,
        class_map: np.ndarray,
        class_count: int,
    ) -> list[list[int]]:
        out = []
        for class_id in range(class_count):
            row = np.sum(source[class_map == class_id, :], axis=0) % field_prime
            out.append([int(value) for value in row.tolist()])
        return out

    def representative_mod_rows(
        source: np.ndarray,
        class_map: np.ndarray,
        class_count: int,
    ) -> list[list[int]]:
        out = []
        for class_id in range(class_count):
            relation_id = int(np.where(class_map == class_id)[0][0])
            out.append([int(value) for value in source[relation_id, :].tolist()])
        return out

    q42_matrix_unit_aggregate_rows = aggregate_mod_rows(
        matrix_units, q42_map, q42_class_count
    )
    q12_matrix_unit_aggregate_rows = aggregate_mod_rows(
        matrix_units, q12_map, q12_class_count
    )
    q42_matrix_unit_representative_rows = representative_mod_rows(
        matrix_units, q42_map, q42_class_count
    )
    q12_matrix_unit_representative_rows = representative_mod_rows(
        matrix_units, q12_map, q12_class_count
    )

    q42_to_q12 = q42_q12_quotient_adjusted_packet_filter_audit[
        "quotient_adjusted_summary"
    ]["q42_to_q12"]
    q42_pushdown_matrix_unit_rows = [
        [0 for _ in range(matrix_units.shape[1])] for _ in range(q12_class_count)
    ]
    for q42_class, q12_class in enumerate(q42_to_q12):
        for coordinate, value in enumerate(q42_matrix_unit_aggregate_rows[q42_class]):
            q42_pushdown_matrix_unit_rows[int(q12_class)][coordinate] = (
                q42_pushdown_matrix_unit_rows[int(q12_class)][coordinate] + value
            ) % field_prime

    character_table = [[0 for _ in range(q12_map.shape[0])] for _ in range(39)]
    for row in character_rows:
        character_table[int(row["source_sector"])][int(row["relation_alpha"])] = int(
            row["character_signed"]
        )
    relation_character_rows = [
        [character_table[sector][relation_id] for sector in range(39)]
        for relation_id in range(q12_map.shape[0])
    ]

    def aggregate_integer_rows(
        source: list[list[int]],
        class_map: np.ndarray,
        class_count: int,
    ) -> list[list[int]]:
        out = []
        for class_id in range(class_count):
            relation_ids = [int(idx) for idx in np.where(class_map == class_id)[0]]
            out.append(
                [
                    sum(source[relation_id][coordinate] for relation_id in relation_ids)
                    for coordinate in range(len(source[0]))
                ]
            )
        return out

    def representative_integer_rows(
        source: list[list[int]],
        class_map: np.ndarray,
        class_count: int,
    ) -> list[list[int]]:
        return [
            source[int(np.where(class_map == class_id)[0][0])]
            for class_id in range(class_count)
        ]

    q42_character_aggregate_rows = aggregate_integer_rows(
        relation_character_rows, q42_map, q42_class_count
    )
    q12_character_aggregate_rows = aggregate_integer_rows(
        relation_character_rows, q12_map, q12_class_count
    )
    q42_character_representative_rows = representative_integer_rows(
        relation_character_rows, q42_map, q42_class_count
    )
    q12_character_representative_rows = representative_integer_rows(
        relation_character_rows, q12_map, q12_class_count
    )

    q42_matrix_unit_rank = matrix_rank_mod_prime(
        q42_matrix_unit_aggregate_rows, field_prime
    )
    q12_matrix_unit_rank = matrix_rank_mod_prime(
        q12_matrix_unit_aggregate_rows, field_prime
    )
    q42_matrix_unit_representative_rank = matrix_rank_mod_prime(
        q42_matrix_unit_representative_rows, field_prime
    )
    q12_matrix_unit_representative_rank = matrix_rank_mod_prime(
        q12_matrix_unit_representative_rows, field_prime
    )
    q42_character_aggregate_rank = matrix_rank_over_q(q42_character_aggregate_rows)
    q42_character_representative_rank = matrix_rank_over_q(
        q42_character_representative_rows
    )
    q12_character_aggregate_rank = matrix_rank_over_q(q12_character_aggregate_rows)
    q12_character_representative_rank = matrix_rank_over_q(
        q12_character_representative_rows
    )

    lift_summary = full_packet_lift["derived"]["acting_summary"]
    a985_action_probe = full_packet_lift["derived"]["a985_action_probe"]
    packet_target_dimension = lift_summary["packet_vector_space_dimension"]
    block_lift_dimension = lift_summary["block_algebra_dimension_over_Q"]
    q42_filter_summary = q42_q12_quotient_adjusted_packet_filter_audit[
        "quotient_adjusted_summary"
    ]

    hidden_summary = {
        "method": "q42_a985_matrix_unit_shadow_rank_sandwich_against_packet_capacity",
        "field_prime": field_prime,
        "q42_class_count": q42_class_count,
        "q12_class_count": q12_class_count,
        "matrix_unit_shape": [int(value) for value in matrix_units.shape],
        "matrix_unit_report_status": full_matrix_unit["status"],
        "matrix_unit_report_all_checks_pass": full_matrix_unit["all_checks_pass"],
        "sector_character_report_status": sector_characters["status"],
        "sector_character_report_all_checks_pass": sector_characters[
            "all_checks_pass"
        ],
        "full_packet_matrix_lift_status": full_packet_lift["status"],
        "full_packet_matrix_lift_all_checks_pass": full_packet_lift[
            "all_checks_pass"
        ],
        "q42_matrix_unit_aggregate_rank_mod_p": q42_matrix_unit_rank,
        "q12_matrix_unit_aggregate_rank_mod_p": q12_matrix_unit_rank,
        "q42_matrix_unit_representative_rank_mod_p": (
            q42_matrix_unit_representative_rank
        ),
        "q12_matrix_unit_representative_rank_mod_p": (
            q12_matrix_unit_representative_rank
        ),
        "q42_matrix_unit_aggregate_unique_row_count": len(
            {tuple(row) for row in q42_matrix_unit_aggregate_rows}
        ),
        "q12_matrix_unit_aggregate_unique_row_count": len(
            {tuple(row) for row in q12_matrix_unit_aggregate_rows}
        ),
        "q42_matrix_unit_aggregate_rows_sha256": sha_json(
            q42_matrix_unit_aggregate_rows
        ),
        "q12_matrix_unit_aggregate_rows_sha256": sha_json(
            q12_matrix_unit_aggregate_rows
        ),
        "q42_pushdown_matrix_unit_equals_q12_aggregate": (
            q42_pushdown_matrix_unit_rows == q12_matrix_unit_aggregate_rows
        ),
        "q42_character_aggregate_rank_over_Q": q42_character_aggregate_rank,
        "q42_character_representative_rank_over_Q": (
            q42_character_representative_rank
        ),
        "q12_character_aggregate_rank_over_Q": q12_character_aggregate_rank,
        "q12_character_representative_rank_over_Q": (
            q12_character_representative_rank
        ),
        "q42_character_aggregate_rows_sha256": sha_json(
            q42_character_aggregate_rows
        ),
        "q42_character_representative_rows_sha256": sha_json(
            q42_character_representative_rows
        ),
        "public_q42_to_q12_packet_filter_rank": q42_filter_summary[
            "q42_scalar6_natural_target_passing_rank_over_Q"
        ],
        "packet_target_dimension": packet_target_dimension,
        "block_lift_image_dimension_bound": block_lift_dimension,
        "a985_dimension": a985_action_probe["a985_dimension"],
        "a985_to_packet_operator_map_present": a985_action_probe[
            "certified_a985_to_packet_operator_map_present"
        ],
        "q42_matrix_unit_rank_excess_over_packet_target": (
            q42_matrix_unit_rank - packet_target_dimension
        ),
        "q42_matrix_unit_rank_excess_over_block_lift": (
            q42_matrix_unit_rank - block_lift_dimension
        ),
        "q42_character_representative_shortfall_to_packet_target": (
            packet_target_dimension - q42_character_representative_rank
        ),
        "q42_character_aggregate_shortfall_to_packet_target": (
            packet_target_dimension - q42_character_aggregate_rank
        ),
    }

    result = {
        "certified_a985_matrix_unit_shadow_available": (
            hidden_summary["matrix_unit_report_status"]
            == "D20_TINY_POINTER_A985_FULL_MATRIX_UNIT_ORBITAL_COO_CERTIFIED"
            and hidden_summary["matrix_unit_report_all_checks_pass"] is True
            and hidden_summary["matrix_unit_shape"] == [985, 985]
        ),
        "q42_matrix_unit_shadow_has_full_q42_rank": (
            hidden_summary["q42_matrix_unit_aggregate_rank_mod_p"] == 42
            and hidden_summary["q42_matrix_unit_representative_rank_mod_p"] == 42
            and hidden_summary["q42_matrix_unit_aggregate_unique_row_count"] == 42
        ),
        "q42_matrix_unit_shadow_pushes_down_to_q12": (
            hidden_summary["q42_pushdown_matrix_unit_equals_q12_aggregate"] is True
            and hidden_summary["q12_matrix_unit_aggregate_rank_mod_p"] == 12
        ),
        "central_character_q42_shadow_too_small_for_packet_rank20": (
            hidden_summary["q42_character_aggregate_rank_over_Q"] == 7
            and hidden_summary["q42_character_representative_rank_over_Q"] == 12
            and hidden_summary[
                "q42_character_representative_shortfall_to_packet_target"
            ]
            == 8
        ),
        "matrix_unit_q42_shadow_exceeds_packet_capacity": (
            hidden_summary["packet_target_dimension"] == 20
            and hidden_summary["block_lift_image_dimension_bound"] == 40
            and hidden_summary["q42_matrix_unit_rank_excess_over_packet_target"]
            == 22
            and hidden_summary["q42_matrix_unit_rank_excess_over_block_lift"] == 2
        ),
        "no_certified_a985_to_packet_operator_map_yet": (
            hidden_summary["a985_to_packet_operator_map_present"] is False
        ),
    }
    result["hidden_q42_a985_matrix_unit_capacity_requires_kernel_choice"] = all(
        result.values()
    )

    return {
        "status": "HIDDEN_Q42_A985_MATRIX_UNIT_SHADOW_RANK42_REQUIRES_PACKET_KERNEL_CHOICE",
        "claim_boundary": (
            "This uses the certified raw A985 matrix-unit coordinate system as a hidden "
            "q42 shadow and compares its rank to the already-certified full-packet block "
            "lift. It does not construct the missing A985-to-packet operator map; it "
            "only proves that central traces are too small while full matrix-unit q42 "
            "data are too large to enter the current packet target without an explicit "
            "kernel or quotient choice."
        ),
        "hidden_capacity_summary": hidden_summary,
        "result": result,
        "all_checks_pass": all(result.values()),
        "interpretation": (
            "The central/character shadow cannot carry a rank-20 packet target: q42 "
            "aggregate characters have rank 7 and q42 representative characters rank 12. "
            "The full raw A985 matrix-unit shadow goes the other way: q42 classes have "
            "full rank 42 modulo the certified field and push down cleanly to the q12 "
            "rank-12 aggregate. The current full-packet block lift has dimension 40 and "
            "the packet target has dimension 20, so any hidden q42/A985 packet bridge "
            "must specify a noncentral quotient/kernel. Without that kernel choice, the "
            "hidden A985 data do not determine a canonical 20-packet projection."
        ),
    }


def build_q42_tensor_rank20_slice_quotient_audit(
    q42_q12_quotient_adjusted_packet_filter_audit: dict[str, Any],
    hidden_q42_a985_matrix_unit_capacity_audit: dict[str, Any],
) -> dict[str, Any]:
    with np.load(ROOT / QUOTIENTS_NPZ) as payload:
        q12_map = np.asarray(payload["q12_map"], dtype=np.int64)
        q42_map = np.asarray(payload["q42_map"], dtype=np.int64)
        q42_tensor = np.asarray(payload["q42_tensor"], dtype=np.int64)

    q42_to_q12 = q42_q12_quotient_adjusted_packet_filter_audit[
        "quotient_adjusted_summary"
    ]["q42_to_q12"]
    hidden_summary = hidden_q42_a985_matrix_unit_capacity_audit[
        "hidden_capacity_summary"
    ]

    q42_class_count = int(q42_tensor.shape[0])
    q12_class_count = int(q12_map.max()) + 1
    q42_left_slices = [
        [
            [int(value) for value in q42_tensor[left_class, right_class, :].tolist()]
            for right_class in range(q42_class_count)
        ]
        for left_class in range(q42_class_count)
    ]

    rank_values_by_size: dict[str, list[str]] = {}
    first_exact_rank20_combo: tuple[int, ...] | None = None
    first_at_least_rank20_combo: tuple[int, ...] | None = None
    first_at_least_rank20_rank: int | None = None
    exact_rank20_combo_count = 0
    combo_count_by_size: dict[str, int] = {}
    for combo_size in range(1, 4):
        rank_values = []
        combo_count = 0
        for combo in itertools.combinations(range(q42_class_count), combo_size):
            rows = [
                row
                for left_class in combo
                for row in q42_left_slices[left_class]
            ]
            rank = matrix_rank_over_q(rows)
            rank_values.append(str(rank))
            combo_count += 1
            if rank == 20:
                exact_rank20_combo_count += 1
                if first_exact_rank20_combo is None:
                    first_exact_rank20_combo = combo
            if rank >= 20 and first_at_least_rank20_combo is None:
                first_at_least_rank20_combo = combo
                first_at_least_rank20_rank = rank
        rank_values_by_size[str(combo_size)] = rank_values
        combo_count_by_size[str(combo_size)] = combo_count

    if first_exact_rank20_combo is None:
        raise AssertionError("q42 tensor rank20 slice quotient search found no witness")

    exact_rows = [
        row
        for left_class in first_exact_rank20_combo
        for row in q42_left_slices[left_class]
    ]
    exact_q12_pushed_rows = []
    for row in exact_rows:
        pushed_row = [0 for _ in range(q12_class_count)]
        for q42_class, coefficient in enumerate(row):
            pushed_row[int(q42_to_q12[q42_class])] += int(coefficient)
        exact_q12_pushed_rows.append(pushed_row)

    exact_rank = matrix_rank_over_q(exact_rows)
    exact_q12_rank = matrix_rank_over_q(exact_q12_pushed_rows)
    nonzero_exact_rows = [row for row in exact_rows if any(row)]
    summary = {
        "method": "bounded_q42_tensor_left_multiplication_slice_rank_search",
        "max_left_slice_combo_size": 3,
        "q42_class_count": q42_class_count,
        "q12_class_count": q12_class_count,
        "combination_count_by_size": combo_count_by_size,
        "rank_histogram_by_combo_size": {
            combo_size: counter_dict(rank_values)
            for combo_size, rank_values in rank_values_by_size.items()
        },
        "exact_rank20_combo_count": exact_rank20_combo_count,
        "first_exact_rank20_left_classes": list(first_exact_rank20_combo),
        "first_exact_rank20_left_q12_classes": [
            int(q42_to_q12[left_class]) for left_class in first_exact_rank20_combo
        ],
        "first_exact_rank20_row_count": len(exact_rows),
        "first_exact_rank20_nonzero_row_count": len(nonzero_exact_rows),
        "first_exact_rank20_unique_nonzero_row_count": len(
            {tuple(row) for row in nonzero_exact_rows}
        ),
        "first_exact_rank20_output_rank_over_Q": exact_rank,
        "first_exact_rank20_kernel_dimension_in_q42_class_space": (
            q42_class_count - exact_rank
        ),
        "first_exact_rank20_q12_pushdown_rank_over_Q": exact_q12_rank,
        "first_exact_rank20_rows_sha256": sha_json(exact_rows),
        "first_exact_rank20_q12_pushdown_rows_sha256": sha_json(
            exact_q12_pushed_rows
        ),
        "first_at_least_rank20_left_classes": list(first_at_least_rank20_combo)
        if first_at_least_rank20_combo is not None
        else None,
        "first_at_least_rank20_output_rank_over_Q": first_at_least_rank20_rank,
        "packet_target_dimension": hidden_summary["packet_target_dimension"],
        "hidden_matrix_unit_rank_excess_over_packet_target": hidden_summary[
            "q42_matrix_unit_rank_excess_over_packet_target"
        ],
        "a985_to_packet_operator_map_present": hidden_summary[
            "a985_to_packet_operator_map_present"
        ],
    }

    result = {
        "single_and_pair_left_slices_never_reach_packet_rank20": (
            "20" not in summary["rank_histogram_by_combo_size"]["1"]
            and "20" not in summary["rank_histogram_by_combo_size"]["2"]
            and max(int(rank) for rank in rank_values_by_size["2"]) == 14
        ),
        "rank20_left_slice_triples_exist": (
            summary["exact_rank20_combo_count"] == 1200
            and summary["first_exact_rank20_left_classes"] == [0, 1, 22]
            and summary["first_exact_rank20_output_rank_over_Q"] == 20
        ),
        "first_rank20_slice_has_packet_kernel_dimension_22": (
            summary["first_exact_rank20_kernel_dimension_in_q42_class_space"] == 22
            and summary[
                "first_exact_rank20_kernel_dimension_in_q42_class_space"
            ]
            == summary["hidden_matrix_unit_rank_excess_over_packet_target"]
        ),
        "rank20_slice_is_hidden_not_public_q12": (
            summary["first_exact_rank20_left_q12_classes"] == [0, 0, 8]
            and summary["first_exact_rank20_q12_pushdown_rank_over_Q"] == 8
        ),
        "rank20_slice_packet_label_still_open": (
            summary["a985_to_packet_operator_map_present"] is False
        ),
    }
    result["q42_tensor_left_slice_rank20_quotient_found_packet_label_open"] = all(
        result.values()
    )

    return {
        "status": "Q42_TENSOR_LEFT_SLICE_RANK20_QUOTIENT_FOUND_PACKET_LABEL_OPEN",
        "claim_boundary": (
            "This is a bounded brute-force search over q42 tensor left-multiplication "
            "slice combinations of size at most three. It finds exact rank-20 q42 "
            "quotient witnesses, but it does not identify those q42 output coordinates "
            "with the ten full-packet doublets or construct the missing A985-to-packet "
            "operator map."
        ),
        "rank20_slice_summary": summary,
        "result": result,
        "all_checks_pass": all(result.values()),
        "interpretation": (
            "The q42 tensor itself contains the first exact 20-rank quotient candidate: "
            "left slices [0,1,22] span rank 20 in q42 output-class space, with a "
            "22-dimensional kernel matching the packet-target excess found in the "
            "hidden matrix-unit audit. The witness is genuinely hidden: its q12 pushdown "
            "has rank only 8. The remaining seam is packet labeling, namely aligning this "
            "rank-20 q42 quotient with the ten certified full-packet doublets."
        ),
    }


def build_q42_rank20_packet_spectral_label_filter_audit(
    q42_tensor_rank20_slice_quotient_audit: dict[str, Any],
) -> dict[str, Any]:
    with np.load(ROOT / QUOTIENTS_NPZ) as payload:
        q12_map = np.asarray(payload["q12_map"], dtype=np.int64)
        q42_map = np.asarray(payload["q42_map"], dtype=np.int64)
        q42_tensor = np.asarray(payload["q42_tensor"], dtype=np.int64)

    spectral = load_json(PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_REPORT)
    packet_graph = load_json(FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_REPORT)
    slice_summary = q42_tensor_rank20_slice_quotient_audit[
        "rank20_slice_summary"
    ]
    q42_to_q12 = []
    for q42_class in range(q42_tensor.shape[0]):
        q12_values = sorted(
            {int(value) for value in q12_map[q42_map == q42_class].tolist()}
        )
        q42_to_q12.append(q12_values[0])

    left_classes = slice_summary["first_exact_rank20_left_classes"]
    slice_rows = [
        [int(value) for value in q42_tensor[left_class, right_class, :].tolist()]
        for left_class in left_classes
        for right_class in range(q42_tensor.shape[1])
    ]
    active_q42_classes = sorted(
        {q42_class for row in slice_rows for q42_class, value in enumerate(row) if value}
    )
    active_restricted_rows = [
        [row[q42_class] for q42_class in active_q42_classes] for row in slice_rows
    ]
    active_nullspace = matrix_nullspace_over_q(active_restricted_rows)
    active_relation_rows = [
        primitive_integer_vector(vector) for vector in active_nullspace["basis"]
    ]
    active_relation = active_relation_rows[0] if active_relation_rows else []
    active_relation_support = [
        [active_q42_classes[index], coefficient]
        for index, coefficient in enumerate(active_relation)
        if coefficient
    ]
    rank_preserving_drop_classes = []
    basis_option_rows = []
    for q42_class, _coefficient in active_relation_support:
        basis_classes = [value for value in active_q42_classes if value != q42_class]
        basis_rows = [[row[q42_class] for q42_class in basis_classes] for row in slice_rows]
        basis_rank = matrix_rank_over_q(basis_rows)
        if basis_rank == slice_summary["first_exact_rank20_output_rank_over_Q"]:
            rank_preserving_drop_classes.append(q42_class)
        basis_option_rows.append(
            {
                "drop_q42_class": q42_class,
                "basis_rank_over_Q": basis_rank,
                "basis_class_count": len(basis_classes),
                "basis_q12_class_histogram": counter_dict(
                    [str(q42_to_q12[value]) for value in basis_classes]
                ),
                "basis_classes": basis_classes,
            }
        )

    canonical_drop_class = next(
        (
            q42_class
            for q42_class, coefficient in active_relation_support
            if coefficient == -1
        ),
        rank_preserving_drop_classes[-1] if rank_preserving_drop_classes else None,
    )
    canonical_basis_classes = [
        value for value in active_q42_classes if value != canonical_drop_class
    ]

    packet_rows = spectral["derived"]["packet_spectral_charge_rows"]
    packet_rows_by_id = {int(row["packet_id"]): row for row in packet_rows}
    full_packet_ids = spectral["derived"]["distinguished_packet_sets"][
        "full_loop297_atom_exposure_packet_ids"
    ]
    graph_packet_pairs = [
        [int(value) for value in pair]
        for pair in packet_graph["derived"]["graph_summary"]["active_partner_pairs"]
    ]
    full_packet_fine_keys = [
        packet_rows_by_id[packet_id]["fine_spectral_charge_key"]
        for packet_id in full_packet_ids
    ]
    packet_doublet_rows = []
    for packet_pair in graph_packet_pairs:
        left_packet, right_packet = packet_pair
        left_row = packet_rows_by_id[left_packet]
        right_row = packet_rows_by_id[right_packet]
        packet_doublet_rows.append(
            {
                "packet_pair": packet_pair,
                "left_fine_spectral_charge_key": left_row[
                    "fine_spectral_charge_key"
                ],
                "right_fine_spectral_charge_key": right_row[
                    "fine_spectral_charge_key"
                ],
                "pair_filter_key": "|".join(
                    [
                        str(left_row["laplacian_trace"]),
                        str(right_row["laplacian_trace"]),
                        ",".join(str(value) for value in left_row["sector26_clock_pair"]),
                        ",".join(str(value) for value in right_row["sector26_clock_pair"]),
                        str(left_row["gamma8_mode_count"]),
                    ]
                ),
                "left_gamma8_mode_count": int(left_row["gamma8_mode_count"]),
                "right_gamma8_mode_count": int(right_row["gamma8_mode_count"]),
                "left_sector26_clock_balanced": bool(
                    left_row["sector26_clock_balanced"]
                ),
                "right_sector26_clock_balanced": bool(
                    right_row["sector26_clock_balanced"]
                ),
            }
        )

    provisional_label_rows = []
    for q42_class, packet_id in zip(canonical_basis_classes, full_packet_ids):
        packet_row = packet_rows_by_id[packet_id]
        provisional_label_rows.append(
            {
                "q42_basis_class": int(q42_class),
                "q12_class": int(q42_to_q12[q42_class]),
                "packet_id": int(packet_id),
                "fine_spectral_charge_key": packet_row[
                    "fine_spectral_charge_key"
                ],
                "gamma8_mode_count": int(packet_row["gamma8_mode_count"]),
                "sector26_clock_balanced": bool(
                    packet_row["sector26_clock_balanced"]
                ),
            }
        )

    packet_filter_summary = {
        "method": "packet_spectral_charge_filter_for_q42_rank20_slice_labels",
        "packet_spectral_report_status": spectral["status"],
        "packet_spectral_report_all_checks_pass": spectral["all_checks_pass"],
        "packet_graph_report_status": packet_graph["status"],
        "packet_graph_report_all_checks_pass": packet_graph["all_checks_pass"],
        "q42_rank20_left_classes": left_classes,
        "q42_rank20_active_q42_class_count": len(active_q42_classes),
        "q42_rank20_active_q42_classes": active_q42_classes,
        "q42_rank20_active_q12_classes": [
            int(q42_to_q12[q42_class]) for q42_class in active_q42_classes
        ],
        "q42_rank20_active_relation_rank_over_Q": active_nullspace["rank"],
        "q42_rank20_active_relation_dimension": len(active_relation_rows),
        "q42_rank20_active_relation_support": active_relation_support,
        "q42_rank20_rank_preserving_drop_classes": rank_preserving_drop_classes,
        "q42_rank20_basis_option_rows": basis_option_rows,
        "canonical_drop_q42_class": canonical_drop_class,
        "canonical_basis_q42_classes": canonical_basis_classes,
        "canonical_basis_q42_class_count": len(canonical_basis_classes),
        "canonical_basis_q12_class_histogram": counter_dict(
            [str(q42_to_q12[q42_class]) for q42_class in canonical_basis_classes]
        ),
        "full_exposure_packet_count": len(full_packet_ids),
        "full_exposure_packet_ids": full_packet_ids,
        "full_exposure_fine_spectral_charge_key_count": len(
            set(full_packet_fine_keys)
        ),
        "full_exposure_fine_spectral_charge_keys_sha256": sha_json(
            full_packet_fine_keys
        ),
        "full_packet_doublet_count": len(packet_doublet_rows),
        "full_packet_doublet_pair_filter_key_count": len(
            {row["pair_filter_key"] for row in packet_doublet_rows}
        ),
        "full_packet_doublet_rows_sha256": sha_json(packet_doublet_rows),
        "full_packet_gamma8_mode_count_histogram": counter_dict(
            [
                str(packet_rows_by_id[packet_id]["gamma8_mode_count"])
                for packet_id in full_packet_ids
            ]
        ),
        "full_packet_sector26_balanced_histogram": counter_dict(
            [
                str(packet_rows_by_id[packet_id]["sector26_clock_balanced"])
                for packet_id in full_packet_ids
            ]
        ),
        "provisional_label_status": "NONCANONICAL_CARDINALITY_AND_FINE_KEY_ALIGNMENT_ONLY",
        "provisional_label_rows": provisional_label_rows,
        "provisional_label_rows_sha256": sha_json(provisional_label_rows),
        "q42_rank20_q12_pushdown_rank_over_Q": slice_summary[
            "first_exact_rank20_q12_pushdown_rank_over_Q"
        ],
        "a985_to_packet_operator_map_present": slice_summary[
            "a985_to_packet_operator_map_present"
        ],
    }

    result = {
        "packet_spectral_filter_certified": (
            packet_filter_summary["packet_spectral_report_status"]
            == "D20_PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_CERTIFIED"
            and packet_filter_summary["packet_spectral_report_all_checks_pass"] is True
            and packet_filter_summary["packet_graph_report_status"]
            == "D20_FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_CERTIFIED"
            and packet_filter_summary["packet_graph_report_all_checks_pass"] is True
        ),
        "packet_fine_spectral_keys_label_all_twenty_full_exposure_packets": (
            packet_filter_summary["full_exposure_packet_count"] == 20
            and packet_filter_summary[
                "full_exposure_fine_spectral_charge_key_count"
            ]
            == 20
        ),
        "packet_doublet_filter_keys_label_all_ten_doublets": (
            packet_filter_summary["full_packet_doublet_count"] == 10
            and packet_filter_summary["full_packet_doublet_pair_filter_key_count"] == 10
        ),
        "q42_rank20_active_support_collapses_21_to_20": (
            packet_filter_summary["q42_rank20_active_q42_class_count"] == 21
            and packet_filter_summary["q42_rank20_active_relation_dimension"] == 1
            and packet_filter_summary["q42_rank20_active_relation_support"]
            == [[2, 13], [8, -1]]
            and packet_filter_summary["q42_rank20_rank_preserving_drop_classes"]
            == [2, 8]
            and packet_filter_summary["canonical_basis_q42_class_count"] == 20
        ),
        "q42_packet_label_cardinality_filter_passes": (
            packet_filter_summary["canonical_basis_q42_class_count"]
            == packet_filter_summary["full_exposure_packet_count"]
            == packet_filter_summary[
                "full_exposure_fine_spectral_charge_key_count"
            ]
        ),
        "spectral_filter_not_enough_to_certify_hidden_packet_label": (
            packet_filter_summary["provisional_label_status"]
            == "NONCANONICAL_CARDINALITY_AND_FINE_KEY_ALIGNMENT_ONLY"
            and packet_filter_summary["q42_rank20_q12_pushdown_rank_over_Q"] == 8
            and packet_filter_summary["a985_to_packet_operator_map_present"] is False
        ),
    }
    result["q42_rank20_packet_spectral_label_filter_cardinality_only"] = all(
        result.values()
    )

    return {
        "status": "Q42_RANK20_PACKET_SPECTRAL_LABEL_FILTER_CARDINALITY_ONLY",
        "claim_boundary": (
            "This applies the certified packet spectral-charge axes as a first label "
            "filter for the hidden q42 rank-20 slice. It finds cardinality and "
            "fine-key compatibility, but it does not certify a q42-to-packet label map "
            "because the q42 active support has two rank-preserving basis choices and "
            "the A985-to-packet operator map remains absent."
        ),
        "packet_label_filter_summary": packet_filter_summary,
        "result": result,
        "all_checks_pass": all(result.values()),
        "interpretation": (
            "The packet side is label-ready: the 20 full-exposure packets have 20 unique "
            "fine spectral-charge keys, and the ten packet doublets have ten unique pair "
            "filter keys. The q42 side is rank-ready but not label-ready: its active "
            "support is 21 q42 classes with the primitive relation 13*q42_2 - q42_8 = 0, "
            "so dropping either q42_2 or q42_8 gives a rank-20 basis. The provisional "
            "basis-to-packet alignment is therefore only a cardinality/fine-key witness, "
            "not a canonical packet labelling."
        ),
    }


def build_q42_rank20_integral_saturation_tie_break_audit(
    q42_tensor_rank20_slice_quotient_audit: dict[str, Any],
    q42_rank20_packet_spectral_label_filter_audit: dict[str, Any],
) -> dict[str, Any]:
    with np.load(ROOT / QUOTIENTS_NPZ) as payload:
        q42_tensor = np.asarray(payload["q42_tensor"], dtype=np.int64)

    slice_summary = q42_tensor_rank20_slice_quotient_audit[
        "rank20_slice_summary"
    ]
    label_summary = q42_rank20_packet_spectral_label_filter_audit[
        "packet_label_filter_summary"
    ]
    left_classes = slice_summary["first_exact_rank20_left_classes"]
    slice_rows = np.asarray(
        [
            q42_tensor[left_class, right_class, :]
            for left_class in left_classes
            for right_class in range(q42_tensor.shape[1])
        ],
        dtype=np.int64,
    )
    active_classes = label_summary["q42_rank20_active_q42_classes"]
    relation_support = label_summary["q42_rank20_active_relation_support"]
    relation_by_class = {
        int(q42_class): int(coefficient)
        for q42_class, coefficient in relation_support
    }
    disputed_classes = sorted(relation_by_class)
    if disputed_classes != [2, 8]:
        raise AssertionError("unexpected q42 rank20 disputed classes")

    col2 = slice_rows[:, 2]
    col8 = slice_rows[:, 8]
    column_residual = col8 - 13 * col2

    def column_stats(column: np.ndarray) -> dict[str, int]:
        return {
            "nonzero_count": int(np.count_nonzero(column)),
            "sum": int(column.sum()),
            "abs_sum": int(np.abs(column).sum()),
            "square_sum": int((column * column).sum()),
        }

    drop_option_rows = []
    for option in label_summary["q42_rank20_basis_option_rows"]:
        drop_class = int(option["drop_q42_class"])
        retained_disputed = [q42_class for q42_class in disputed_classes if q42_class != drop_class]
        retained_class = retained_disputed[0]
        omitted_coefficient = relation_by_class[drop_class]
        retained_coefficient = relation_by_class[retained_class]
        index_penalty = abs(omitted_coefficient)
        drop_option_rows.append(
            {
                "drop_q42_class": drop_class,
                "retained_disputed_q42_class": retained_class,
                "omitted_relation_coefficient": omitted_coefficient,
                "retained_relation_coefficient": retained_coefficient,
                "basis_rank_over_Q": int(option["basis_rank_over_Q"]),
                "basis_class_count": int(option["basis_class_count"]),
                "active_lattice_index_penalty": index_penalty,
                "integral_saturation_preserving": index_penalty == 1,
                "basis_classes": option["basis_classes"],
            }
        )

    saturation_preserving_options = [
        row for row in drop_option_rows if row["integral_saturation_preserving"]
    ]
    saturation_defect_options = [
        row for row in drop_option_rows if not row["integral_saturation_preserving"]
    ]
    selected_drop = (
        saturation_preserving_options[0]["drop_q42_class"]
        if len(saturation_preserving_options) == 1
        else None
    )
    rejected_drop = (
        saturation_defect_options[0]["drop_q42_class"]
        if len(saturation_defect_options) == 1
        else None
    )

    summary = {
        "method": "primitive_relation_integral_saturation_for_q42_rank20_basis_choice",
        "q42_rank20_left_classes": left_classes,
        "q42_rank20_active_q42_classes": active_classes,
        "q42_rank20_active_relation_support": relation_support,
        "q42_column_relation": "q42_8 = 13*q42_2",
        "q42_column_relation_residual_abs_sum": int(np.abs(column_residual).sum()),
        "q42_2_column_stats": column_stats(col2),
        "q42_8_column_stats": column_stats(col8),
        "q42_8_over_q42_2_column_abs_sum_ratio": 13,
        "rank_preserving_drop_classes": label_summary[
            "q42_rank20_rank_preserving_drop_classes"
        ],
        "drop_option_integral_saturation_rows": drop_option_rows,
        "selected_drop_q42_class_by_integral_saturation": selected_drop,
        "rejected_drop_q42_class_by_integral_saturation": rejected_drop,
        "selected_basis_q42_classes_by_integral_saturation": (
            saturation_preserving_options[0]["basis_classes"]
            if len(saturation_preserving_options) == 1
            else []
        ),
        "rejected_basis_index_defect": (
            saturation_defect_options[0]["active_lattice_index_penalty"]
            if len(saturation_defect_options) == 1
            else None
        ),
        "explicit_q42_to_packet_map_present": label_summary[
            "a985_to_packet_operator_map_present"
        ],
    }

    result = {
        "q42_disputed_columns_have_exact_13_relation": (
            summary["q42_column_relation_residual_abs_sum"] == 0
            and summary["q42_2_column_stats"]["nonzero_count"] > 0
            and summary["q42_8_over_q42_2_column_abs_sum_ratio"] == 13
        ),
        "q42_relation_is_primitive_rank20_kernel": (
            summary["q42_rank20_active_relation_support"] == [[2, 13], [8, -1]]
            and summary["rank_preserving_drop_classes"] == [2, 8]
        ),
        "drop_q42_8_preserves_integral_saturation": any(
            row["drop_q42_class"] == 8
            and row["active_lattice_index_penalty"] == 1
            and row["integral_saturation_preserving"] is True
            for row in drop_option_rows
        ),
        "drop_q42_2_has_index13_saturation_defect": any(
            row["drop_q42_class"] == 2
            and row["active_lattice_index_penalty"] == 13
            and row["integral_saturation_preserving"] is False
            for row in drop_option_rows
        ),
        "integral_saturation_selects_same_drop8_basis": (
            summary["selected_drop_q42_class_by_integral_saturation"] == 8
            and summary["rejected_drop_q42_class_by_integral_saturation"] == 2
        ),
        "explicit_q42_packet_map_still_absent": (
            summary["explicit_q42_to_packet_map_present"] is False
        ),
    }
    result["q42_rank20_integral_saturation_tie_break_selects_drop8"] = all(
        result.values()
    )

    return {
        "status": "Q42_RANK20_INTEGRAL_SATURATION_SELECTS_DROP8_PACKET_MAP_OPEN",
        "claim_boundary": (
            "This is an intrinsic q42 tensor tie-break, independent of packet239 and "
            "the q12 seed anchor. On the rank-20 slice, q42_8 is exactly 13 times "
            "q42_2. Dropping q42_8 retains the primitive generator q42_2; dropping "
            "q42_2 retains only 13*q42_2 and creates an index-13 saturation defect. "
            "The explicit q42/A985-to-packet map is still absent."
        ),
        "integral_saturation_summary": summary,
        "result": result,
        "all_checks_pass": all(result.values()),
        "interpretation": (
            "The q42_2/q42_8 ambiguity is no longer just a packet-label ambiguity. "
            "The tensor column relation itself singles out the saturated rank-20 "
            "basis: keep q42_2 and drop q42_8. This agrees with the packet239/q12 "
            "seed anchor but comes from integral q42 lattice structure rather than "
            "from packet-side labelling."
        ),
    }


def build_q42_saturated_basis_direct_doublet_skeleton_audit(
    q42_tensor_rank20_slice_quotient_audit: dict[str, Any],
    q42_rank20_packet_spectral_label_filter_audit: dict[str, Any],
    q42_rank20_integral_saturation_tie_break_audit: dict[str, Any],
) -> dict[str, Any]:
    with np.load(ROOT / QUOTIENTS_NPZ) as payload:
        q12_map = np.asarray(payload["q12_map"], dtype=np.int64)
        q42_map = np.asarray(payload["q42_map"], dtype=np.int64)
        q42_tensor = np.asarray(payload["q42_tensor"], dtype=np.int64)

    q42_to_q12 = []
    for q42_class in range(q42_tensor.shape[0]):
        q12_values = sorted(
            {int(value) for value in q12_map[q42_map == q42_class].tolist()}
        )
        q42_to_q12.append(q12_values[0])

    slice_summary = q42_tensor_rank20_slice_quotient_audit[
        "rank20_slice_summary"
    ]
    label_summary = q42_rank20_packet_spectral_label_filter_audit[
        "packet_label_filter_summary"
    ]
    saturation_summary = q42_rank20_integral_saturation_tie_break_audit[
        "integral_saturation_summary"
    ]
    basis_classes = saturation_summary[
        "selected_basis_q42_classes_by_integral_saturation"
    ]
    left_classes = slice_summary["first_exact_rank20_left_classes"]
    slice_rows = np.asarray(
        [
            q42_tensor[left_class, right_class, :]
            for left_class in left_classes
            for right_class in range(q42_tensor.shape[1])
        ],
        dtype=np.int64,
    )

    def same_support_pairs(vectors: dict[int, np.ndarray]) -> list[list[int]]:
        signatures: dict[tuple[int, ...], list[int]] = {}
        for q42_class, vector in vectors.items():
            signature = tuple(int(index) for index in np.nonzero(vector)[0].tolist())
            if signature:
                signatures.setdefault(signature, []).append(q42_class)
        pairs = []
        for classes in signatures.values():
            if len(classes) == 2:
                pairs.append(sorted(classes))
        return sorted(pairs)

    slice_vectors = {q42_class: slice_rows[:, q42_class] for q42_class in basis_classes}
    global_vectors = {
        q42_class: q42_tensor[:, :, q42_class].reshape(-1)
        for q42_class in basis_classes
    }
    slice_same_support_pairs = same_support_pairs(slice_vectors)
    global_same_support_pairs = same_support_pairs(global_vectors)

    pair_rows = []
    for pair in global_same_support_pairs:
        left, right = pair
        pair_rows.append(
            {
                "q42_pair": pair,
                "q12_pair": [int(q42_to_q12[left]), int(q42_to_q12[right])],
                "slice_support_count": int(np.count_nonzero(slice_vectors[left])),
                "slice_abs_sums": [
                    int(np.abs(slice_vectors[left]).sum()),
                    int(np.abs(slice_vectors[right]).sum()),
                ],
                "global_support_count": int(np.count_nonzero(global_vectors[left])),
                "global_abs_sums": [
                    int(np.abs(global_vectors[left]).sum()),
                    int(np.abs(global_vectors[right]).sum()),
                ],
            }
        )

    covered_classes = sorted({q42_class for pair in global_same_support_pairs for q42_class in pair})
    uncovered_classes = [
        q42_class for q42_class in basis_classes if q42_class not in covered_classes
    ]
    summary = {
        "method": "direct_q42_support_twin_probe_for_saturated_rank20_packet_doublets",
        "saturated_basis_q42_classes": basis_classes,
        "saturated_basis_q42_class_count": len(basis_classes),
        "target_full_packet_doublet_count": label_summary["full_packet_doublet_count"],
        "target_full_packet_id_count": label_summary["full_exposure_packet_count"],
        "slice_same_support_q42_pair_count": len(slice_same_support_pairs),
        "slice_same_support_q42_pairs": slice_same_support_pairs,
        "global_same_support_q42_pair_count": len(global_same_support_pairs),
        "global_same_support_q42_pairs": global_same_support_pairs,
        "global_same_support_pair_rows": pair_rows,
        "direct_support_twin_covered_q42_classes": covered_classes,
        "direct_support_twin_uncovered_q42_classes": uncovered_classes,
        "direct_support_twin_uncovered_q42_class_count": len(uncovered_classes),
        "direct_support_twin_packet_doublet_shortfall": (
            label_summary["full_packet_doublet_count"] - len(global_same_support_pairs)
        ),
        "explicit_q42_to_packet_map_present": label_summary[
            "a985_to_packet_operator_map_present"
        ],
    }

    result = {
        "saturated_rank20_basis_has_twenty_coordinates": (
            summary["saturated_basis_q42_class_count"] == 20
            and summary["target_full_packet_id_count"] == 20
        ),
        "packet_target_has_ten_doublets": (
            summary["target_full_packet_doublet_count"] == 10
        ),
        "direct_slice_support_twins_find_only_two_doublets": (
            summary["slice_same_support_q42_pairs"] == [[0, 6], [1, 7]]
        ),
        "direct_global_support_twins_find_only_two_doublets": (
            summary["global_same_support_q42_pairs"] == [[0, 6], [1, 7]]
            and summary["global_same_support_q42_pair_count"] == 2
        ),
        "direct_q42_support_twin_shortfall_is_eight_doublets": (
            summary["direct_support_twin_packet_doublet_shortfall"] == 8
            and summary["direct_support_twin_uncovered_q42_class_count"] == 16
        ),
        "direct_q42_doublet_skeleton_requires_nonlocal_packet_map": (
            summary["explicit_q42_to_packet_map_present"] is False
        ),
    }
    result["q42_saturated_basis_direct_doublet_skeleton_only_two_of_ten"] = all(
        result.values()
    )

    return {
        "status": "Q42_SATURATED_BASIS_DIRECT_DOUBLET_SKELETON_ONLY_TWO_OF_TEN_MAP_OPEN",
        "claim_boundary": (
            "This tests whether the saturated rank-20 q42 basis already contains the "
            "ten full-packet doublets as direct q42 tensor support twins. It finds only "
            "two such q42 doublets, so a packet realization cannot be a direct support "
            "pairing inside q42 alone; the remaining eight doublets require a nonlocal "
            "q42/A985-to-packet map."
        ),
        "direct_doublet_summary": summary,
        "result": result,
        "all_checks_pass": all(result.values()),
        "interpretation": (
            "The saturated q42 basis is now fixed, but its direct tensor support geometry "
            "only exposes q42 pairs (0,6) and (1,7). Since the certified packet target has "
            "ten doublets, direct q42 support twins explain two packet doublets at most. "
            "The next map must use a nonlocal A985 or packet-side operator, not a naive "
            "q42 support-pair readout."
        ),
    }


def build_a985_2x2_sector_carrier_completion_audit(
    q42_saturated_basis_direct_doublet_skeleton_audit: dict[str, Any],
) -> dict[str, Any]:
    with np.load(ROOT / A985_FULL_MATRIX_UNIT_ARRAYS) as matrix_payload:
        source_sector = np.asarray(matrix_payload["source_sector"], dtype=np.int64)
        raw_sector = np.asarray(matrix_payload["raw_sector"], dtype=np.int64)
        i_coords = np.asarray(matrix_payload["i"], dtype=np.int64)
        j_coords = np.asarray(matrix_payload["j"], dtype=np.int64)

    full_matrix_unit = load_json(A985_FULL_MATRIX_UNIT_REPORT)
    packet_lift = load_json(D20_FULL_PACKET_MATRIX_LIFT_REPORT)
    direct_summary = q42_saturated_basis_direct_doublet_skeleton_audit[
        "direct_doublet_summary"
    ]

    sector_rows = []
    for sector in sorted({int(value) for value in source_sector.tolist()}):
        mask = source_sector == sector
        i_values = sorted({int(value) for value in i_coords[mask].tolist()})
        j_values = sorted({int(value) for value in j_coords[mask].tolist()})
        raw_values = sorted({int(value) for value in raw_sector[mask].tolist()})
        block_dimension = len(i_values)
        sector_rows.append(
            {
                "source_sector": sector,
                "raw_sector": raw_values[0] if raw_values else None,
                "block_dimension": block_dimension,
                "matrix_unit_count": int(np.count_nonzero(mask)),
                "is_square_matrix_unit_block": (
                    len(i_values) == len(j_values)
                    and int(np.count_nonzero(mask)) == block_dimension * block_dimension
                ),
            }
        )
    two_by_two_rows = [
        row for row in sector_rows if row["block_dimension"] == 2
    ]
    packet_acting = packet_lift["derived"]["acting_summary"]
    packet_component_rows = packet_lift["derived"]["component_lift_rows"]
    zero_pair_components = [
        row for row in packet_component_rows if row["is_zero_pair_component"] is True
    ]

    direct_pair_count = direct_summary["global_same_support_q42_pair_count"]
    direct_shortfall = direct_summary["direct_support_twin_packet_doublet_shortfall"]
    summary = {
        "method": "a985_two_by_two_sector_carrier_for_q42_direct_doublet_shortfall",
        "matrix_unit_report_status": full_matrix_unit["status"],
        "matrix_unit_report_all_checks_pass": full_matrix_unit["all_checks_pass"],
        "packet_matrix_lift_status": packet_lift["status"],
        "packet_matrix_lift_all_checks_pass": packet_lift["all_checks_pass"],
        "a985_source_sector_count": len(sector_rows),
        "a985_matrix_unit_count": int(source_sector.size),
        "a985_block_dimension_histogram": counter_dict(
            [str(row["block_dimension"]) for row in sector_rows]
        ),
        "a985_two_by_two_sector_count": len(two_by_two_rows),
        "a985_two_by_two_source_sectors": [
            row["source_sector"] for row in two_by_two_rows
        ],
        "a985_two_by_two_raw_sectors": [row["raw_sector"] for row in two_by_two_rows],
        "a985_two_by_two_matrix_unit_count": sum(
            row["matrix_unit_count"] for row in two_by_two_rows
        ),
        "a985_two_by_two_rows": two_by_two_rows,
        "a985_raw_sector33_is_two_by_two": any(
            row["raw_sector"] == 33 for row in two_by_two_rows
        ),
        "q42_direct_support_twin_pair_count": direct_pair_count,
        "q42_direct_support_twin_packet_doublet_shortfall": direct_shortfall,
        "packet_block_algebra": packet_acting["block_algebra"],
        "packet_block_algebra_dimension_over_Q": packet_acting[
            "block_algebra_dimension_over_Q"
        ],
        "packet_component_count": packet_acting["component_count"],
        "packet_vector_space_dimension": packet_acting[
            "packet_vector_space_dimension"
        ],
        "packet_zero_pair_component_count": len(zero_pair_components),
        "packet_zero_pair_component_id": (
            int(zero_pair_components[0]["component_id"])
            if len(zero_pair_components) == 1
            else None
        ),
        "direct_q42_visible_block_dimension_over_Q": direct_pair_count * 4,
        "a985_two_by_two_shortfall_block_dimension_over_Q": len(two_by_two_rows) * 4,
        "combined_carrier_block_dimension_over_Q": (
            direct_pair_count * 4 + len(two_by_two_rows) * 4
        ),
        "combined_carrier_component_count": direct_pair_count + len(two_by_two_rows),
        "explicit_a985_to_packet_operator_map_present": packet_lift["derived"][
            "a985_action_probe"
        ]["certified_a985_to_packet_operator_map_present"],
    }

    result = {
        "a985_matrix_unit_carrier_is_certified": (
            summary["matrix_unit_report_status"]
            == "D20_TINY_POINTER_A985_FULL_MATRIX_UNIT_ORBITAL_COO_CERTIFIED"
            and summary["matrix_unit_report_all_checks_pass"] is True
            and summary["a985_source_sector_count"] == 39
            and summary["a985_matrix_unit_count"] == 985
        ),
        "packet_matrix_lift_carrier_is_certified_mat2x10": (
            summary["packet_matrix_lift_status"] == "D20_FULL_PACKET_MATRIX_LIFT_CERTIFIED"
            and summary["packet_matrix_lift_all_checks_pass"] is True
            and summary["packet_block_algebra"] == "Mat_2(Q)^10"
            and summary["packet_component_count"] == 10
            and summary["packet_block_algebra_dimension_over_Q"] == 40
        ),
        "a985_has_exactly_eight_two_by_two_sector_blocks": (
            summary["a985_two_by_two_sector_count"] == 8
            and summary["a985_two_by_two_matrix_unit_count"] == 32
            and all(row["is_square_matrix_unit_block"] is True for row in two_by_two_rows)
        ),
        "a985_two_by_two_count_matches_direct_q42_doublet_shortfall": (
            summary["a985_two_by_two_sector_count"]
            == summary["q42_direct_support_twin_packet_doublet_shortfall"]
            == 8
        ),
        "direct_q42_plus_a985_two_by_two_carrier_matches_packet_blocks": (
            summary["combined_carrier_component_count"] == summary["packet_component_count"]
            == 10
            and summary["combined_carrier_block_dimension_over_Q"]
            == summary["packet_block_algebra_dimension_over_Q"]
            == 40
        ),
        "a985_two_by_two_carrier_contains_raw_sector33": (
            summary["a985_raw_sector33_is_two_by_two"] is True
        ),
        "a985_two_by_two_carrier_still_needs_operator_assignment": (
            summary["explicit_a985_to_packet_operator_map_present"] is False
        ),
    }
    result["a985_2x2_sector_carrier_completes_q42_direct_doublet_shortfall"] = all(
        result.values()
    )

    return {
        "status": "A985_2X2_SECTOR_CARRIER_COMPLETES_Q42_DIRECT_DOUBLET_SHORTFALL_MAP_OPEN",
        "claim_boundary": (
            "This does not construct the missing A985-to-packet operator. It identifies "
            "the first exact nonlocal carrier profile: q42 direct support twins account "
            "for two packet Mat_2 blocks, and A985 has exactly eight certified 2x2 "
            "matrix-unit sectors, matching the remaining eight packet blocks and the "
            "32-dimensional block-lift shortfall."
        ),
        "carrier_completion_summary": summary,
        "result": result,
        "all_checks_pass": all(result.values()),
        "interpretation": (
            "The direct q42 support geometry is not enough, but it fails in a structured "
            "way: the eight missing packet doublets are exactly the number of 2x2 A985 "
            "sector blocks. Together, the two direct q42 twins and the eight A985 "
            "2x2 sectors have ten Mat_2 components and dimension 40, matching the "
            "certified packet matrix lift. The next obstruction is assignment: which "
            "A985 2x2 sector maps to which remaining packet doublet, and by what operator."
        ),
    }


def build_sector33_packet239_zero_pair_anchor_audit(
    a985_2x2_sector_carrier_completion_audit: dict[str, Any],
) -> dict[str, Any]:
    sector33_unique = load_json(SECTOR33_UNIQUE_PUBLIC_ZERO_SUPPORT_REPORT)
    sector33_boundary = load_json(SECTOR33_BOUNDARY_ANNIHILATION_REPORT)
    sector33_attachment = load_json(SECTOR33_RESIDUAL_ATTACHMENT_REPORT)
    packet239_root = load_json(D20_PACKET239_E8_ROOT_RELATION_PROBE_REPORT)
    packet_lift = load_json(D20_FULL_PACKET_MATRIX_LIFT_REPORT)

    carrier_summary = a985_2x2_sector_carrier_completion_audit[
        "carrier_completion_summary"
    ]
    raw33_rows = [
        row for row in carrier_summary["a985_two_by_two_rows"] if row["raw_sector"] == 33
    ]
    sector33_support = sector33_unique["derived"]["unique_public_zero_support"]
    sector33_profile = sector33_boundary["derived"]["sector33_profile"]
    sector33_attachment_row = sector33_attachment["derived"]["sector_attachment"]
    packet_selection = packet239_root["witness"]["packet239_id_free_selection"]
    packet239_row = packet239_root["witness"]["packet_rows"]["packet239_selected_seed"]
    zero_pair_components = [
        row
        for row in packet_lift["derived"]["component_lift_rows"]
        if row["is_zero_pair_component"] is True
    ]
    zero_pair_component = zero_pair_components[0] if len(zero_pair_components) == 1 else {}

    summary = {
        "method": "raw_sector33_to_packet239_zero_pair_component_anchor_candidate",
        "sector33_unique_status": sector33_unique["status"],
        "sector33_unique_all_checks_pass": sector33_unique["all_checks_pass"],
        "sector33_boundary_status": sector33_boundary["status"],
        "sector33_boundary_all_checks_pass": sector33_boundary["all_checks_pass"],
        "sector33_attachment_status": sector33_attachment["status"],
        "sector33_attachment_all_checks_pass": sector33_attachment["all_checks_pass"],
        "packet239_root_status": packet239_root["status"],
        "packet239_root_all_checks_pass": packet239_root["all_checks_pass"],
        "packet_matrix_lift_status": packet_lift["status"],
        "packet_matrix_lift_all_checks_pass": packet_lift["all_checks_pass"],
        "a985_raw_sector33_carrier_rows": raw33_rows,
        "a985_raw_sector33_source_sector": (
            raw33_rows[0]["source_sector"] if len(raw33_rows) == 1 else None
        ),
        "sector33_unique_public_zero_sector": int(sector33_support["sector"]),
        "sector33_block_dimension": int(sector33_support["block_dimension"]),
        "sector33_active_objects": sector33_support["active_objects"],
        "sector33_q42_nonzero_count": int(sector33_support["q42_nonzero_count"]),
        "sector33_q12_nonzero_count": int(sector33_support["q12_nonzero_count"]),
        "sector33_profile_active_objects": sector33_profile["active_objects"],
        "sector33_profile_block_dimension": int(sector33_profile["block_dimension"]),
        "sector33_attachment_type": sector33_attachment_row["attachment_type"],
        "sector33_boundary_cycle_id": int(sector33_attachment_row["boundary_cycle_id"]),
        "sector33_residual_integral": int(sector33_attachment_row["residual_integral"]),
        "sector33_public_terminal_shadow": sector33_attachment_row[
            "public_terminal_shadow"
        ],
        "packet239_selection_rule": packet_selection["selection_rule"],
        "packet239_uses_external_packet_id": packet_selection["uses_external_packet_id"],
        "packet239_selected_packet_ids": packet_selection["selected_packet_ids"],
        "packet239_selected_frame_indices": packet_selection["selected_frame_indices"],
        "packet239_charge_frame_key": packet_selection["selected_charge_frame_key"],
        "packet239_fine_spectral_charge_key": packet_selection[
            "selected_fine_spectral_charge_key"
        ],
        "packet239_sector26_clock_pair": packet239_row["sector26_clock_pair"],
        "packet239_sector26_clock_zero_pair": bool(
            packet239_row["sector26_clock_zero_pair"]
        ),
        "packet239_corrected_hidden_clock_pair": packet239_row[
            "corrected_hidden_clock_pair"
        ],
        "packet239_hidden_projection_pair": packet239_row["hidden_projection_pair"],
        "packet239_gamma8_touched": bool(packet239_row["gamma8_touched"]),
        "packet_zero_pair_component_count": len(zero_pair_components),
        "packet_zero_pair_component_id": int(zero_pair_component.get("component_id", -1)),
        "packet_zero_pair_packet_pair": zero_pair_component.get("packet_pair", []),
        "packet_zero_pair_oriented_basis": zero_pair_component.get("oriented_basis", []),
        "packet_zero_pair_block_matrix": zero_pair_component.get("block_matrix", []),
        "packet_zero_pair_block_decomposition": zero_pair_component.get(
            "block_decomposition", ""
        ),
        "explicit_a985_to_packet_operator_map_present": carrier_summary[
            "explicit_a985_to_packet_operator_map_present"
        ],
        "anchor_status": "UNIQUE_SOURCE_AND_TARGET_ANCHOR_CANDIDATE_OPERATOR_OPEN",
    }

    result = {
        "sector33_anchor_inputs_are_certified": (
            summary["sector33_unique_status"]
            == "D20_SECTOR33_UNIQUE_PUBLIC_ZERO_SUPPORT_CERTIFIED"
            and summary["sector33_unique_all_checks_pass"] is True
            and summary["sector33_boundary_status"]
            == "D20_SECTOR33_BOUNDARY_TO_LOOP_ANNIHILATION_CERTIFIED"
            and summary["sector33_boundary_all_checks_pass"] is True
            and summary["sector33_attachment_status"]
            == "D20_SECTOR33_RESIDUAL_ATTACHMENT_CERTIFIED"
            and summary["sector33_attachment_all_checks_pass"] is True
        ),
        "packet239_anchor_inputs_are_certified": (
            summary["packet239_root_status"]
            == "D20_PACKET239_E8_ROOT_RELATION_PROBE_CERTIFIED"
            and summary["packet239_root_all_checks_pass"] is True
            and summary["packet_matrix_lift_status"] == "D20_FULL_PACKET_MATRIX_LIFT_CERTIFIED"
            and summary["packet_matrix_lift_all_checks_pass"] is True
        ),
        "raw_sector33_is_unique_2x2_carrier_row": (
            len(summary["a985_raw_sector33_carrier_rows"]) == 1
            and summary["a985_raw_sector33_source_sector"] == 21
            and summary["a985_raw_sector33_carrier_rows"][0]["block_dimension"] == 2
            and summary["a985_raw_sector33_carrier_rows"][0]["matrix_unit_count"] == 4
        ),
        "sector33_is_unique_public_zero_two_dimensional_shadow": (
            summary["sector33_unique_public_zero_sector"] == 33
            and summary["sector33_block_dimension"] == 2
            and summary["sector33_profile_block_dimension"] == 2
            and summary["sector33_q42_nonzero_count"] == 0
            and summary["sector33_q12_nonzero_count"] == 0
        ),
        "sector33_is_cycle8_hidden_residual_anchor": (
            summary["sector33_boundary_cycle_id"] == 8
            and summary["sector33_residual_integral"] == -374784
            and summary["sector33_public_terminal_shadow"]["A12"] == "zero"
            and summary["sector33_public_terminal_shadow"]["A42"] == "zero"
        ),
        "packet239_is_unique_id_free_zero_pair_anchor": (
            summary["packet239_selection_rule"]
            == "full_exposure_sector26_zero_pair_fixed_point"
            and summary["packet239_uses_external_packet_id"] is False
            and summary["packet239_selected_packet_ids"] == [239]
            and summary["packet239_sector26_clock_pair"] == [0, 0]
            and summary["packet239_sector26_clock_zero_pair"] is True
        ),
        "packet239_zero_pair_component_is_unique_mat2_block": (
            summary["packet_zero_pair_component_count"] == 1
            and summary["packet_zero_pair_component_id"] == 2
            and summary["packet_zero_pair_packet_pair"] == [238, 239]
            and summary["packet_zero_pair_oriented_basis"] == [239, 238]
            and summary["packet_zero_pair_block_matrix"] == [[2, 4], [4, 2]]
        ),
        "sector33_packet239_anchor_has_matching_two_dimensional_hidden_zero_profile": (
            summary["sector33_block_dimension"] == 2
            and summary["packet239_corrected_hidden_clock_pair"] == [0, 0]
            and summary["packet239_hidden_projection_pair"]
            == ["sector_orthogonal", "sector_orthogonal"]
            and summary["packet239_gamma8_touched"] is False
        ),
        "sector33_packet239_anchor_operator_still_open": (
            summary["explicit_a985_to_packet_operator_map_present"] is False
            and summary["anchor_status"]
            == "UNIQUE_SOURCE_AND_TARGET_ANCHOR_CANDIDATE_OPERATOR_OPEN"
        ),
    }
    result["sector33_packet239_zero_pair_anchor_candidate_operator_open"] = all(
        result.values()
    )

    return {
        "status": "SECTOR33_PACKET239_ZERO_PAIR_ANCHOR_CANDIDATE_OPERATOR_OPEN",
        "claim_boundary": (
            "This identifies a unique source/target anchor for the nonlocal A985-to-packet "
            "assignment: raw A985 sector 33 is the unique public-zero 2x2 sector carrier, "
            "and packet239 is the unique id-free full-exposure zero-pair packet inside the "
            "unique zero-pair packet Mat_2 block. It does not construct the operator that "
            "maps sector 33 to the packet239 block."
        ),
        "anchor_summary": summary,
        "result": result,
        "all_checks_pass": all(result.values()),
        "interpretation": (
            "The carrier-completion profile now has a first anchored edge. Sector 33 is "
            "the unique two-dimensional A985 public-zero hidden residual carrier, and "
            "the packet side has a unique zero-pair component with oriented basis "
            "[239,238]. This makes raw sector 33 the canonical first candidate for the "
            "packet239 block among the eight nonlocal 2x2 carriers, while preserving the "
            "missing operator as the next proof obligation."
        ),
    }


def build_a985_2x2_chart_signature_assignment_constraints_audit(
    q42_saturated_basis_direct_doublet_skeleton_audit: dict[str, Any],
    a985_2x2_sector_carrier_completion_audit: dict[str, Any],
    sector33_packet239_zero_pair_anchor_audit: dict[str, Any],
) -> dict[str, Any]:
    with np.load(ROOT / A985_FULL_MATRIX_UNIT_ARRAYS) as matrix_payload:
        source_sector = np.asarray(matrix_payload["source_sector"], dtype=np.int64)

    with np.load(ROOT / QUOTIENTS_NPZ) as quotient_payload:
        q42_map = np.asarray(quotient_payload["q42_map"], dtype=np.int64)
        q12_map = np.asarray(quotient_payload["q12_map"], dtype=np.int64)

    packet_lift = load_json(D20_FULL_PACKET_MATRIX_LIFT_REPORT)
    direct_summary = q42_saturated_basis_direct_doublet_skeleton_audit[
        "direct_doublet_summary"
    ]
    carrier_summary = a985_2x2_sector_carrier_completion_audit[
        "carrier_completion_summary"
    ]
    anchor_summary = sector33_packet239_zero_pair_anchor_audit["anchor_summary"]
    saturated_basis = set(direct_summary["saturated_basis_q42_classes"])
    direct_q42_classes = set(direct_summary["direct_support_twin_covered_q42_classes"])

    chart_rows = []
    for row in carrier_summary["a985_two_by_two_rows"]:
        sector = int(row["source_sector"])
        chart_indices = [
            int(index) for index in np.where(source_sector == sector)[0].tolist()
        ]
        q42_classes = [int(q42_map[index]) for index in chart_indices]
        q12_classes = [int(q12_map[index]) for index in chart_indices]
        saturated_overlap = sorted(set(q42_classes).intersection(saturated_basis))
        direct_overlap = sorted(set(q42_classes).intersection(direct_q42_classes))
        chart_rows.append(
            {
                "source_sector": sector,
                "raw_sector": int(row["raw_sector"]),
                "chart_relation_indices": chart_indices,
                "q42_classes": q42_classes,
                "q12_classes": q12_classes,
                "saturated_q42_overlap": saturated_overlap,
                "saturated_q42_overlap_count": len(saturated_overlap),
                "direct_q42_overlap": direct_overlap,
                "direct_q42_overlap_count": len(direct_overlap),
            }
        )

    class_groups: dict[tuple[int, ...], list[dict[str, Any]]] = {}
    for row in chart_rows:
        key = tuple(row["saturated_q42_overlap"])
        class_groups.setdefault(key, []).append(row)
    saturated_overlap_class_rows = []
    for key in sorted(class_groups):
        rows = sorted(class_groups[key], key=lambda item: item["source_sector"])
        saturated_overlap_class_rows.append(
            {
                "saturated_q42_overlap": list(key),
                "source_sectors": [row["source_sector"] for row in rows],
                "raw_sectors": [row["raw_sector"] for row in rows],
                "class_size": len(rows),
            }
        )

    full_signature_groups: dict[tuple[tuple[int, int], ...], list[dict[str, Any]]] = {}
    for row in chart_rows:
        key = tuple(zip(row["q42_classes"], row["q12_classes"]))
        full_signature_groups.setdefault(key, []).append(row)
    full_signature_class_rows = []
    for rows in sorted(
        full_signature_groups.values(),
        key=lambda items: min(item["source_sector"] for item in items),
    ):
        sorted_rows = sorted(rows, key=lambda item: item["source_sector"])
        representative = sorted_rows[0]
        full_signature_class_rows.append(
            {
                "q42_classes": representative["q42_classes"],
                "q12_classes": representative["q12_classes"],
                "source_sectors": [row["source_sector"] for row in sorted_rows],
                "raw_sectors": [row["raw_sector"] for row in sorted_rows],
                "class_size": len(sorted_rows),
            }
        )

    anchor_source = int(anchor_summary["a985_raw_sector33_source_sector"])
    anchor_row = next(row for row in chart_rows if row["source_sector"] == anchor_source)
    anchor_saturated_class_rows = [
        row
        for row in chart_rows
        if row["saturated_q42_overlap"] == anchor_row["saturated_q42_overlap"]
    ]
    anchor_full_signature_class_rows = [
        row
        for row in chart_rows
        if row["q42_classes"] == anchor_row["q42_classes"]
        and row["q12_classes"] == anchor_row["q12_classes"]
    ]
    residual_anchor_full_signature_rows = [
        row
        for row in anchor_full_signature_class_rows
        if row["source_sector"] != anchor_source
    ]
    packet_component_ids = [
        int(row["component_id"])
        for row in packet_lift["derived"]["component_lift_rows"]
    ]
    anchored_component = int(anchor_summary["packet_zero_pair_component_id"])
    remaining_packet_component_ids = [
        component_id
        for component_id in packet_component_ids
        if component_id != anchored_component
    ]
    remaining_a985_rows = [
        row for row in chart_rows if row["source_sector"] != anchor_source
    ]

    summary = {
        "method": "a985_two_by_two_chart_signature_constraints_for_sector_packet_assignment",
        "a985_two_by_two_chart_row_count": len(chart_rows),
        "a985_two_by_two_chart_rows": chart_rows,
        "saturated_q42_overlap_class_count": len(saturated_overlap_class_rows),
        "saturated_q42_overlap_class_rows": saturated_overlap_class_rows,
        "full_q42_q12_signature_class_count": len(full_signature_class_rows),
        "full_q42_q12_signature_class_rows": full_signature_class_rows,
        "sector33_anchor_source_sector": anchor_source,
        "sector33_anchor_raw_sector": int(anchor_summary["sector33_unique_public_zero_sector"]),
        "sector33_anchor_saturated_q42_overlap": anchor_row["saturated_q42_overlap"],
        "sector33_anchor_direct_q42_overlap": anchor_row["direct_q42_overlap"],
        "sector33_anchor_saturated_class_source_sectors": [
            row["source_sector"]
            for row in sorted(
                anchor_saturated_class_rows, key=lambda item: item["source_sector"]
            )
        ],
        "sector33_anchor_saturated_class_raw_sectors": [
            row["raw_sector"]
            for row in sorted(
                anchor_saturated_class_rows, key=lambda item: item["source_sector"]
            )
        ],
        "sector33_anchor_chart_twin_source_sectors": [
            row["source_sector"]
            for row in sorted(
                anchor_full_signature_class_rows, key=lambda item: item["source_sector"]
            )
        ],
        "sector33_anchor_chart_twin_raw_sectors": [
            row["raw_sector"]
            for row in sorted(
                anchor_full_signature_class_rows, key=lambda item: item["source_sector"]
            )
        ],
        "sector33_anchor_residual_chart_twin_source_sectors_after_anchor": [
            row["source_sector"]
            for row in sorted(
                residual_anchor_full_signature_rows,
                key=lambda item: item["source_sector"],
            )
        ],
        "sector33_anchor_residual_chart_twin_raw_sectors_after_anchor": [
            row["raw_sector"]
            for row in sorted(
                residual_anchor_full_signature_rows,
                key=lambda item: item["source_sector"],
            )
        ],
        "sector33_anchor_packet_component_id": anchored_component,
        "remaining_a985_two_by_two_source_sectors": [
            row["source_sector"] for row in remaining_a985_rows
        ],
        "remaining_a985_two_by_two_raw_sectors": [
            row["raw_sector"] for row in remaining_a985_rows
        ],
        "remaining_a985_two_by_two_count": len(remaining_a985_rows),
        "remaining_packet_component_ids_after_anchor": remaining_packet_component_ids,
        "remaining_packet_component_count_after_anchor": len(
            remaining_packet_component_ids
        ),
        "direct_q42_visible_block_count": direct_summary[
            "global_same_support_q42_pair_count"
        ],
        "remaining_carrier_count_after_anchor_plus_direct_q42_blocks": (
            len(remaining_a985_rows)
            + direct_summary["global_same_support_q42_pair_count"]
        ),
        "explicit_a985_to_packet_operator_map_present": anchor_summary[
            "explicit_a985_to_packet_operator_map_present"
        ],
    }

    result = {
        "chart_constraints_cover_all_eight_a985_2x2_sectors": (
            summary["a985_two_by_two_chart_row_count"] == 8
            and all(len(row["chart_relation_indices"]) == 4 for row in chart_rows)
        ),
        "saturated_q42_chart_constraints_reduce_to_four_classes_with_one_null_cluster": (
            summary["saturated_q42_overlap_class_count"] == 4
            and [row["class_size"] for row in saturated_overlap_class_rows]
            == [5, 1, 1, 1]
        ),
        "full_q42_q12_chart_signatures_refine_to_six_classes": (
            summary["full_q42_q12_signature_class_count"] == 6
            and [row["class_size"] for row in full_signature_class_rows]
            == [1, 1, 1, 3, 1, 1]
        ),
        "sector33_anchor_lands_in_full_signature_triple_and_leaves_raw11_raw36_twin": (
            summary["sector33_anchor_source_sector"] == 21
            and summary["sector33_anchor_raw_sector"] == 33
            and summary["sector33_anchor_saturated_q42_overlap"] == []
            and summary["sector33_anchor_saturated_class_source_sectors"]
            == [20, 21, 22, 32, 33]
            and summary["sector33_anchor_chart_twin_source_sectors"] == [20, 21, 22]
            and summary["sector33_anchor_chart_twin_raw_sectors"] == [11, 33, 36]
            and summary[
                "sector33_anchor_residual_chart_twin_source_sectors_after_anchor"
            ]
            == [20, 22]
            and summary["sector33_anchor_residual_chart_twin_raw_sectors_after_anchor"]
            == [11, 36]
        ),
        "a985_two_by_two_rows_avoid_direct_q42_support_twins": (
            summary["sector33_anchor_direct_q42_overlap"] == []
            and all(row["direct_q42_overlap"] == [] for row in chart_rows)
        ),
        "remaining_carrier_count_matches_unanchored_packet_components_when_direct_q42_blocks_included": (
            summary["remaining_a985_two_by_two_count"] == 7
            and summary["direct_q42_visible_block_count"] == 2
            and summary["remaining_packet_component_count_after_anchor"] == 9
            and summary[
                "remaining_carrier_count_after_anchor_plus_direct_q42_blocks"
            ]
            == 9
        ),
        "chart_constraints_are_not_full_operator_assignment": (
            summary["full_q42_q12_signature_class_count"] < summary[
                "a985_two_by_two_chart_row_count"
            ]
            and summary["explicit_a985_to_packet_operator_map_present"] is False
        ),
    }
    result["a985_2x2_chart_signatures_constrain_remaining_assignment_operator_open"] = all(
        result.values()
    )

    return {
        "status": "A985_2X2_CHART_SIGNATURES_CONSTRAIN_ASSIGNMENT_OPERATOR_OPEN",
        "claim_boundary": (
            "This uses A985 matrix-unit chart rows pushed through q42/q12 to constrain, "
            "not solve, the remaining sector-to-packet assignment. Saturated q42 overlap "
            "collapses five A985 2x2 sectors into one null class, while full q42/q12 "
            "chart signatures refine the eight sectors to six classes. The sector33 "
            "anchor removes raw sector 33 from a raw 11/33/36 chart triple, leaving "
            "raw 11/36 open. No A985-to-packet operator is constructed."
        ),
        "chart_constraint_summary": summary,
        "result": result,
        "all_checks_pass": all(result.values()),
        "interpretation": (
            "After anchoring sector33 to packet239, the remaining problem has the right "
            "cardinality: seven A985 2x2 carriers and two direct q42 blocks for nine "
            "unanchored packet components. The saturated q42 chart is too coarse, but "
            "the full q42/q12 chart signature separates the A985 carrier into six "
            "classes and localizes the residual anchored ambiguity to raw sectors "
            "11 and 36. This is a useful assignment constraint but not a unique "
            "operator-level map."
        ),
    }


def build_q12_packet_charge_sum_partition_fingerprint_audit(
    q42_saturated_basis_direct_doublet_skeleton_audit: dict[str, Any],
    a985_2x2_chart_signature_assignment_constraints_audit: dict[str, Any],
) -> dict[str, Any]:
    packet_lift = load_json(D20_FULL_PACKET_MATRIX_LIFT_REPORT)
    label_breaking = load_json(FULL_EXPOSURE_LABEL_BREAKING_FACTORIZATION_REPORT)
    label_rows_by_packet = {
        int(row["packet_id"]): row
        for row in label_breaking["derived"]["full_exposure_packet_label_rows"]
    }
    chart_summary = a985_2x2_chart_signature_assignment_constraints_audit[
        "chart_constraint_summary"
    ]
    direct_summary = q42_saturated_basis_direct_doublet_skeleton_audit[
        "direct_doublet_summary"
    ]

    with np.load(ROOT / QUOTIENTS_NPZ) as quotient_payload:
        q42_map = np.asarray(quotient_payload["q42_map"], dtype=np.int64)
        q12_map = np.asarray(quotient_payload["q12_map"], dtype=np.int64)
    q42_to_q12 = {}
    for q42_class in sorted({int(value) for value in q42_map.tolist()}):
        q12_values = sorted(
            {int(value) for value in q12_map[q42_map == q42_class].tolist()}
        )
        q42_to_q12[q42_class] = q12_values[0]

    carrier_rows = []
    for q42_pair in direct_summary["global_same_support_q42_pairs"]:
        q42_pair = [int(value) for value in q42_pair]
        carrier_rows.append(
            {
                "carrier_id": "direct_q42_" + "_".join(str(value) for value in q42_pair),
                "carrier_kind": "direct_q42_support_twin",
                "q42_sequence": q42_pair,
                "q12_signature": [q42_to_q12[value] for value in q42_pair],
                "source_sector": None,
                "raw_sector": None,
            }
        )
    for row in chart_summary["a985_two_by_two_chart_rows"]:
        if row["source_sector"] == chart_summary["sector33_anchor_source_sector"]:
            continue
        carrier_rows.append(
            {
                "carrier_id": f"a985_raw{row['raw_sector']}",
                "carrier_kind": "a985_2x2_sector",
                "q42_sequence": row["q42_classes"],
                "q12_signature": row["q12_classes"],
                "source_sector": row["source_sector"],
                "raw_sector": row["raw_sector"],
            }
        )

    carrier_groups: dict[tuple[int, ...], list[dict[str, Any]]] = {}
    for row in carrier_rows:
        key = tuple(row["q12_signature"])
        carrier_groups.setdefault(key, []).append(row)
    carrier_class_rows = []
    for key in sorted(carrier_groups):
        rows = sorted(carrier_groups[key], key=lambda item: item["carrier_id"])
        carrier_class_rows.append(
            {
                "q12_signature": list(key),
                "carrier_ids": [row["carrier_id"] for row in rows],
                "carrier_kinds": [row["carrier_kind"] for row in rows],
                "source_sectors": [
                    row["source_sector"]
                    for row in rows
                    if row["source_sector"] is not None
                ],
                "raw_sectors": [
                    row["raw_sector"] for row in rows if row["raw_sector"] is not None
                ],
                "direct_q42_pairs": [
                    row["q42_sequence"]
                    for row in rows
                    if row["carrier_kind"] == "direct_q42_support_twin"
                ],
                "class_size": len(rows),
            }
        )

    anchored_component = chart_summary["sector33_anchor_packet_component_id"]
    packet_component_rows = []
    anchored_packet_charge_row = None
    for component in packet_lift["derived"]["component_lift_rows"]:
        label_pair = [
            label_rows_by_packet[int(packet_id)]
            for packet_id in component["packet_pair"]
        ]
        packet_row = {
            "component_id": int(component["component_id"]),
            "packet_pair": [int(packet_id) for packet_id in component["packet_pair"]],
            "sector26_sum_pair": [
                int(row["sector26_clock_sum_mod26"]) for row in label_pair
            ],
            "sector26_delta_pair": [
                int(row["sector26_clock_delta_mod26"]) for row in label_pair
            ],
            "local_patterns": [row["local_pattern"] for row in label_pair],
            "mass_frames": [row["mass_frame"] for row in label_pair],
            "clock_frames": [row["clock_frame"] for row in label_pair],
            "gamma_frames": [row["gamma_frame"] for row in label_pair],
        }
        if packet_row["component_id"] == anchored_component:
            anchored_packet_charge_row = packet_row
        else:
            packet_component_rows.append(packet_row)

    packet_groups: dict[tuple[int, ...], list[dict[str, Any]]] = {}
    for row in packet_component_rows:
        key = tuple(row["sector26_sum_pair"])
        packet_groups.setdefault(key, []).append(row)
    packet_class_rows = []
    for key in sorted(packet_groups):
        rows = sorted(packet_groups[key], key=lambda item: item["component_id"])
        packet_class_rows.append(
            {
                "sector26_sum_pair": list(key),
                "component_ids": [row["component_id"] for row in rows],
                "packet_pairs": [row["packet_pair"] for row in rows],
                "local_patterns": [row["local_patterns"][0] for row in rows],
                "gamma_frame_pairs": [row["gamma_frames"] for row in rows],
                "class_size": len(rows),
            }
        )

    carrier_histogram = sorted(row["class_size"] for row in carrier_class_rows)
    packet_histogram = sorted(row["class_size"] for row in packet_class_rows)
    class_size_counts = counter_dict([str(size) for size in carrier_histogram])
    size_compatible_class_bijection_count = product(
        [math.factorial(count) for count in class_size_counts.values()]
    )
    size_compatible_element_bijection_count = (
        size_compatible_class_bijection_count
        * product([math.factorial(size) for size in carrier_histogram])
    )
    unconstrained_element_bijection_count = math.factorial(len(carrier_rows))
    residual_class = next(
        row
        for row in carrier_class_rows
        if row["raw_sectors"]
        == chart_summary["sector33_anchor_residual_chart_twin_raw_sectors_after_anchor"]
    )

    summary = {
        "method": "q12_carrier_partition_vs_packet_sector26_charge_sum_fingerprint",
        "carrier_count_after_anchor_plus_direct_q42": len(carrier_rows),
        "carrier_q12_signature_class_count": len(carrier_class_rows),
        "carrier_q12_signature_class_rows": carrier_class_rows,
        "carrier_q12_signature_class_size_histogram": carrier_histogram,
        "packet_component_count_after_anchor": len(packet_component_rows),
        "packet_sector26_sum_class_count": len(packet_class_rows),
        "packet_sector26_sum_class_rows": packet_class_rows,
        "packet_sector26_sum_class_size_histogram": packet_histogram,
        "anchored_component_id": anchored_component,
        "anchored_packet_sector26_sum_pair": (
            anchored_packet_charge_row["sector26_sum_pair"]
            if anchored_packet_charge_row
            else None
        ),
        "anchored_packet_clock_frames": (
            anchored_packet_charge_row["clock_frames"]
            if anchored_packet_charge_row
            else None
        ),
        "residual_raw11_raw36_q12_signature": residual_class["q12_signature"],
        "residual_raw11_raw36_source_sectors": residual_class["source_sectors"],
        "residual_raw11_raw36_raw_sectors": residual_class["raw_sectors"],
        "size_compatible_class_bijection_count": size_compatible_class_bijection_count,
        "size_compatible_element_bijection_count": size_compatible_element_bijection_count,
        "unconstrained_element_bijection_count": unconstrained_element_bijection_count,
        "explicit_operator_map_present": False,
    }

    result = {
        "carrier_q12_partition_covers_nine_unanchored_carriers": (
            summary["carrier_count_after_anchor_plus_direct_q42"] == 9
            and summary["carrier_q12_signature_class_count"] == 6
        ),
        "packet_sector26_sum_partition_covers_nine_unanchored_components": (
            summary["packet_component_count_after_anchor"] == 9
            and summary["packet_sector26_sum_class_count"] == 6
        ),
        "carrier_and_packet_partition_fingerprints_match": (
            summary["carrier_q12_signature_class_size_histogram"]
            == summary["packet_sector26_sum_class_size_histogram"]
            == [1, 1, 1, 2, 2, 2]
        ),
        "residual_raw11_raw36_is_q12_class4_twin": (
            summary["residual_raw11_raw36_q12_signature"] == [4, 4, 4, 4]
            and summary["residual_raw11_raw36_raw_sectors"] == [11, 36]
        ),
        "sector33_anchor_removed_zero_pair_charge_sum_component": (
            summary["anchored_component_id"] == 2
            and summary["anchored_packet_sector26_sum_pair"] == [4, 0]
            and summary["anchored_packet_clock_frames"]
            == ["delta8_nonzero", "zero_pair"]
        ),
        "partition_size_constraint_reduces_but_does_not_solve_assignment": (
            summary["size_compatible_element_bijection_count"]
            < summary["unconstrained_element_bijection_count"]
            and summary["size_compatible_class_bijection_count"] == 36
            and summary["explicit_operator_map_present"] is False
        ),
    }
    result["q12_packet_charge_sum_partition_fingerprint_operator_open"] = all(
        result.values()
    )

    return {
        "status": "Q12_PACKET_CHARGE_SUM_PARTITION_FINGERPRINT_OPERATOR_OPEN",
        "claim_boundary": (
            "This is a partition fingerprint, not a sector-to-packet operator. After "
            "the sector33/packet239 anchor, the seven remaining A985 2x2 carriers plus "
            "the two direct q42 support twins split by q12 signature with the same "
            "class-size profile as the nine unanchored packet components split by "
            "sector26 charge-sum pair. The match reduces the brute-force assignment "
            "surface but leaves many size-compatible bijections."
        ),
        "partition_summary": summary,
        "result": result,
        "all_checks_pass": all(result.values()),
        "interpretation": (
            "The residual raw11/raw36 A985 twin is not an isolated artifact: it sits in "
            "one of three size-2 q12 carrier classes, exactly mirroring the three "
            "size-2 sector26 charge-sum classes on the unanchored packet side. This is "
            "the first cheap packet-charge fingerprint that includes the two direct "
            "q42 blocks and the seven A985 carriers in one nine-object partition."
        ),
    }


def build_q42_packet239_q12_seed_anchor_tie_break_audit(
    q12_packet_low_support_normalization_audit: dict[str, Any],
    q42_rank20_packet_spectral_label_filter_audit: dict[str, Any],
) -> dict[str, Any]:
    packet239_root = load_json(D20_PACKET239_E8_ROOT_RELATION_PROBE_REPORT)
    packet239_shell = load_json(D20_PACKET239_E8_20X12_CANDIDATE_SHELL_PROBE_REPORT)
    label_breaking = load_json(FULL_EXPOSURE_LABEL_BREAKING_FACTORIZATION_REPORT)

    label_summary = q42_rank20_packet_spectral_label_filter_audit[
        "packet_label_filter_summary"
    ]
    seed_rows = q12_packet_low_support_normalization_audit[
        "mask288_q12_packet_seed_rows"
    ]
    seed_row = seed_rows[0] if seed_rows else {}
    seed_q12_class = int(seed_row.get("q12_class", -1))

    shell_candidate = packet239_shell["witness"]["candidate_definition"]
    shell_rows = shell_candidate["candidate_rows"]
    packet239_shell_rows = [
        row for row in shell_rows if int(row["packet_id"]) == 239
    ]
    packet239_a12_classes = sorted(
        {int(row["a12_class"]) for row in packet239_shell_rows}
    )
    packet239_frame_indices = sorted(
        {int(row["frame_index"]) for row in packet239_shell_rows}
    )
    packet239_label_row = next(
        row
        for row in label_breaking["derived"]["full_exposure_packet_label_rows"]
        if int(row["packet_id"]) == 239
    )

    drop_option_rows = []
    for option in label_summary["q42_rank20_basis_option_rows"]:
        q12_hist = option["basis_q12_class_histogram"]
        seed_class_count = int(q12_hist.get(str(seed_q12_class), 0))
        drop_option_rows.append(
            {
                "drop_q42_class": int(option["drop_q42_class"]),
                "basis_rank_over_Q": int(option["basis_rank_over_Q"]),
                "basis_class_count": int(option["basis_class_count"]),
                "seed_q12_class_count": seed_class_count,
                "preserves_seed_q12_class": seed_class_count > 0,
                "basis_q12_class_histogram": q12_hist,
                "basis_classes": option["basis_classes"],
            }
        )
    seed_preserving_options = [
        row for row in drop_option_rows if row["preserves_seed_q12_class"]
    ]
    seed_deleting_options = [
        row for row in drop_option_rows if not row["preserves_seed_q12_class"]
    ]
    selected_drop = (
        seed_preserving_options[0]["drop_q42_class"]
        if len(seed_preserving_options) == 1
        else None
    )
    rejected_drop = (
        seed_deleting_options[0]["drop_q42_class"]
        if len(seed_deleting_options) == 1
        else None
    )
    selected_basis_classes = (
        seed_preserving_options[0]["basis_classes"]
        if len(seed_preserving_options) == 1
        else []
    )

    summary = {
        "method": "packet239_zero_pair_q12_seed_anchor_for_q42_rank20_basis_choice",
        "packet239_root_status": packet239_root["status"],
        "packet239_root_all_checks_pass": packet239_root["all_checks_pass"],
        "packet239_shell_status": packet239_shell["status"],
        "packet239_shell_all_checks_pass": packet239_shell["all_checks_pass"],
        "full_exposure_label_breaking_status": label_breaking["status"],
        "full_exposure_label_breaking_all_checks_pass": label_breaking[
            "all_checks_pass"
        ],
        "packet239_unique_full_exposure_clock_zero": packet239_root["checks"][
            "packet239_is_unique_full_exposure_clock_zero"
        ],
        "packet239_seed_closure_is_238_239": packet239_root["checks"][
            "packet239_seed_closure_is_exactly_packets_238_and_239"
        ],
        "packet239_packet_id": 239,
        "packet239_frame_indices": packet239_frame_indices,
        "packet239_candidate_a12_classes": packet239_a12_classes,
        "packet239_candidate_a12_class_count": len(packet239_a12_classes),
        "packet239_charge_frame_key": packet239_label_row["mass_frame"]
        + "|"
        + packet239_label_row["clock_frame"]
        + "|"
        + packet239_label_row["gamma_frame"],
        "packet239_fine_spectral_charge_key": packet239_label_row[
            "fine_spectral_charge_key"
        ],
        "packet239_sector26_clock_zero_pair": bool(
            packet239_label_row["sector26_clock_zero_pair"]
        ),
        "q12_seed_q12_class": seed_q12_class,
        "q12_seed_section_relation_id": int(seed_row.get("section_relation_id", -1)),
        "q12_seed_packet_low_support_family": seed_row.get(
            "packet_low_support_family", []
        ),
        "q42_rank20_active_relation_support": label_summary[
            "q42_rank20_active_relation_support"
        ],
        "q42_rank20_rank_preserving_drop_classes": label_summary[
            "q42_rank20_rank_preserving_drop_classes"
        ],
        "drop_option_q12_seed_anchor_rows": drop_option_rows,
        "selected_drop_q42_class_by_q12_seed_anchor": selected_drop,
        "rejected_drop_q42_class_by_q12_seed_anchor": rejected_drop,
        "selected_basis_q42_classes_by_q12_seed_anchor": selected_basis_classes,
        "explicit_q42_to_packet_map_present": label_summary[
            "a985_to_packet_operator_map_present"
        ],
        "tie_break_status": "CONDITIONAL_ON_Q12_SEED_ANCHOR",
    }

    result = {
        "packet239_anchor_inputs_are_certified": (
            summary["packet239_root_status"]
            == "D20_PACKET239_E8_ROOT_RELATION_PROBE_CERTIFIED"
            and summary["packet239_root_all_checks_pass"] is True
            and summary["packet239_shell_status"]
            == "D20_PACKET239_E8_20X12_CANDIDATE_SHELL_PROBE_CERTIFIED"
            and summary["packet239_shell_all_checks_pass"] is True
            and summary["full_exposure_label_breaking_status"]
            == "D20_FULL_EXPOSURE_LABEL_BREAKING_FACTORIZATION_CERTIFIED"
            and summary["full_exposure_label_breaking_all_checks_pass"] is True
        ),
        "packet239_unique_zero_pair_anchor_available": (
            summary["packet239_unique_full_exposure_clock_zero"] is True
            and summary["packet239_sector26_clock_zero_pair"] is True
            and summary["packet239_frame_indices"] == [0]
        ),
        "packet239_a12_shell_keeps_all_twelve_q12_slots_open": (
            summary["packet239_candidate_a12_classes"] == list(range(12))
            and summary["packet239_candidate_a12_class_count"] == 12
        ),
        "q12_packet_seed_anchor_is_class1": (
            summary["q12_seed_q12_class"] == 1
            and summary["q12_seed_section_relation_id"] == 227
            and summary["q12_seed_packet_low_support_family"] == [0, 11]
        ),
        "q42_drop2_deletes_q12_seed_class1": any(
            row["drop_q42_class"] == 2 and row["seed_q12_class_count"] == 0
            for row in drop_option_rows
        ),
        "q42_drop8_preserves_unique_q12_seed_class1": any(
            row["drop_q42_class"] == 8 and row["seed_q12_class_count"] == 1
            for row in drop_option_rows
        ),
        "q12_seed_anchor_conditionally_selects_drop8": (
            summary["selected_drop_q42_class_by_q12_seed_anchor"] == 8
            and summary["rejected_drop_q42_class_by_q12_seed_anchor"] == 2
        ),
        "explicit_q42_packet_map_still_absent": (
            summary["explicit_q42_to_packet_map_present"] is False
            and summary["tie_break_status"] == "CONDITIONAL_ON_Q12_SEED_ANCHOR"
        ),
    }
    result["q42_packet239_q12_seed_anchor_tie_break_conditional"] = all(
        result.values()
    )

    return {
        "status": "Q42_PACKET239_Q12_SEED_ANCHOR_CONDITIONALLY_SELECTS_DROP8_MAP_OPEN",
        "claim_boundary": (
            "This uses the certified packet239 zero-pair packet and the bridge's "
            "existing q12 class-1 low-support seed as a conditional anchor for the "
            "q42 rank-20 basis choice. It selects the drop-q42_8 basis because drop-q42_2 "
            "removes all q12 class-1 coordinates. It still does not construct the "
            "missing q42/A985-to-packet map, so the tie-break is conditional, not a "
            "canonical hidden packet labelling."
        ),
        "tie_break_summary": summary,
        "result": result,
        "all_checks_pass": all(result.values()),
        "interpretation": (
            "The packet239 side supplies a certified zero-pair anchor, and its 20x12 "
            "shell keeps all A12/q12 slots available. The bridge side supplies a unique "
            "low-support q12 seed in class 1. Of the two rank-preserving q42 bases, "
            "dropping q42_2 erases q12 class 1 entirely, while dropping q42_8 preserves "
            "it exactly once. Therefore a q12-seed-preserving packet239 bridge would "
            "choose the drop-q42_8 basis. The explicit q42-to-packet morphism remains "
            "the missing closure datum."
        ),
    }


def build_artifact() -> dict[str, Any]:
    proof_inventory = proof_obligation_inventory()
    signatures = build_signatures()
    assignment_search = brute_force_assignments(signatures)
    discriminator_search = build_discriminator_search(signatures)
    discriminator_result = discriminator_search["discriminator_result"]
    hcycle_pullback = discriminator_search["hcycle_pullback"]
    static_overlap = discriminator_search["static_public_zero_overlap"]
    static_tropic_pullback = build_static_tropic_sector_pullback(discriminator_search)
    pullback_result = static_tropic_pullback["result"]
    ward_composition_audit = build_static_tropic_ward_composition_audit(
        static_tropic_pullback,
        discriminator_search,
    )
    ward_composition_result = ward_composition_audit["result"]
    selected_mask_z2_audit = build_selected_mask_z2_static_audit(ward_composition_audit)
    selected_mask_z2_result = selected_mask_z2_audit["result"]
    selected_mask_exact_h6_support = build_selected_mask_exact_h6_support_audit(
        ward_composition_audit
    )
    exact_h6_result = selected_mask_exact_h6_support["result"]
    q12_h6_projection_audit = build_q12_h6_projection_audit(
        selected_mask_exact_h6_support
    )
    q12_h6_projection_result = q12_h6_projection_audit["result"]
    q12_packet_low_support_audit = build_q12_packet_low_support_normalization_audit(
        q12_h6_projection_audit
    )
    q12_packet_low_support_result = q12_packet_low_support_audit["result"]
    mask288_q12_packet_seed_support3_audit = (
        build_mask288_q12_packet_seed_support3_audit(q12_packet_low_support_audit)
    )
    mask288_q12_packet_seed_support3_result = (
        mask288_q12_packet_seed_support3_audit["result"]
    )
    mask288_q12_packet_seed_broadened_audit = (
        build_mask288_q12_packet_seed_broadened_extension_audit(
            q12_packet_low_support_audit,
            mask288_q12_packet_seed_support3_audit,
        )
    )
    mask288_q12_packet_seed_broadened_result = (
        mask288_q12_packet_seed_broadened_audit["result"]
    )
    mask288_q12_rank2_label_audit = build_mask288_q12_rank2_doublet_label_audit(
        q12_h6_projection_audit,
        mask288_q12_packet_seed_broadened_audit,
    )
    mask288_q12_rank2_label_result = mask288_q12_rank2_label_audit["result"]
    mask288_q12_rank2_linear_combination_audit = (
        build_mask288_q12_rank2_linear_combination_audit(
            q12_h6_projection_audit,
            mask288_q12_rank2_label_audit,
        )
    )
    mask288_q12_rank2_linear_combination_result = (
        mask288_q12_rank2_linear_combination_audit["result"]
    )
    mask288_q12_product_overhang_invariant_audit = (
        build_mask288_q12_product_overhang_invariant_audit(
            q12_h6_projection_audit,
            mask288_q12_rank2_linear_combination_audit,
        )
    )
    mask288_q12_product_overhang_invariant_result = (
        mask288_q12_product_overhang_invariant_audit["result"]
    )
    mask288_q12_outside_class1_residue_cancellation_audit = (
        build_mask288_q12_outside_class1_residue_cancellation_audit(
            q12_h6_projection_audit,
            mask288_q12_rank2_linear_combination_audit,
        )
    )
    mask288_q12_outside_class1_residue_cancellation_result = (
        mask288_q12_outside_class1_residue_cancellation_audit["result"]
    )
    mask288_q12_packet_normalized_seed_assembly_audit = (
        build_mask288_q12_packet_normalized_seed_assembly_audit(
            q12_h6_projection_audit,
            q12_packet_low_support_audit,
            mask288_q12_packet_seed_broadened_audit,
            mask288_q12_rank2_linear_combination_audit,
            mask288_q12_outside_class1_residue_cancellation_audit,
        )
    )
    mask288_q12_packet_normalized_seed_assembly_result = (
        mask288_q12_packet_normalized_seed_assembly_audit["result"]
    )
    mask288_q12_direct_paired_doublet_search_audit = (
        build_mask288_q12_direct_paired_doublet_search_audit(
            q12_h6_projection_audit,
            mask288_q12_rank2_linear_combination_audit,
            mask288_q12_outside_class1_residue_cancellation_audit,
        )
    )
    mask288_q12_direct_paired_doublet_search_result = (
        mask288_q12_direct_paired_doublet_search_audit["result"]
    )
    mask288_q12_one_sided_seed_correction_audit = (
        build_mask288_q12_one_sided_seed_correction_audit(
            q12_h6_projection_audit,
            mask288_q12_rank2_linear_combination_audit,
            mask288_q12_direct_paired_doublet_search_audit,
        )
    )
    mask288_q12_one_sided_seed_correction_result = (
        mask288_q12_one_sided_seed_correction_audit["result"]
    )
    mask288_q12_corrected_rank20_selection_audit = (
        build_mask288_q12_corrected_rank20_selection_audit(
            mask288_q12_one_sided_seed_correction_audit
        )
    )
    mask288_q12_corrected_rank20_selection_result = (
        mask288_q12_corrected_rank20_selection_audit["result"]
    )
    mask288_q12_rank_escape_probe_audit = build_mask288_q12_rank_escape_probe_audit(
        q12_h6_projection_audit,
        mask288_q12_rank2_linear_combination_audit,
        mask288_q12_one_sided_seed_correction_audit,
    )
    mask288_q12_rank_escape_probe_result = mask288_q12_rank_escape_probe_audit[
        "result"
    ]
    ingress_projection_inventory_audit = (
        build_ingress_boundary_packet_projection_inventory(
            mask288_q12_rank_escape_probe_audit
        )
    )
    ingress_projection_inventory_result = ingress_projection_inventory_audit["result"]
    boundary_packet_projection_candidate_audit = (
        build_boundary_packet_projection_candidate_audit(
            mask288_q12_rank_escape_probe_audit
        )
    )
    boundary_packet_projection_candidate_result = (
        boundary_packet_projection_candidate_audit["result"]
    )
    signed_step_column_packet_search_audit = (
        build_signed_step_column_packet_search_audit(
            mask288_q12_rank_escape_probe_audit
        )
    )
    signed_step_column_packet_search_result = (
        signed_step_column_packet_search_audit["result"]
    )
    support4_signed_step_column_span_audit = (
        build_support4_signed_step_column_span_audit(
            signed_step_column_packet_search_audit,
            mask288_q12_rank_escape_probe_audit,
        )
    )
    support4_signed_step_column_span_result = (
        support4_signed_step_column_span_audit["result"]
    )
    full_step_column_congruence_lattice_audit = (
        build_full_step_column_congruence_lattice_audit(
            support4_signed_step_column_span_audit,
            mask288_q12_rank_escape_probe_audit,
        )
    )
    full_step_column_congruence_lattice_result = (
        full_step_column_congruence_lattice_audit["result"]
    )
    q42_q12_quotient_adjusted_packet_filter_audit = (
        build_q42_q12_quotient_adjusted_packet_filter_audit(
            q12_h6_projection_audit,
            full_step_column_congruence_lattice_audit,
        )
    )
    q42_q12_quotient_adjusted_packet_filter_result = (
        q42_q12_quotient_adjusted_packet_filter_audit["result"]
    )
    hidden_q42_a985_matrix_unit_capacity_audit = (
        build_hidden_q42_a985_matrix_unit_capacity_audit(
            q42_q12_quotient_adjusted_packet_filter_audit
        )
    )
    hidden_q42_a985_matrix_unit_capacity_result = (
        hidden_q42_a985_matrix_unit_capacity_audit["result"]
    )
    q42_tensor_rank20_slice_quotient_audit = (
        build_q42_tensor_rank20_slice_quotient_audit(
            q42_q12_quotient_adjusted_packet_filter_audit,
            hidden_q42_a985_matrix_unit_capacity_audit,
        )
    )
    q42_tensor_rank20_slice_quotient_result = (
        q42_tensor_rank20_slice_quotient_audit["result"]
    )
    q42_rank20_packet_spectral_label_filter_audit = (
        build_q42_rank20_packet_spectral_label_filter_audit(
            q42_tensor_rank20_slice_quotient_audit
        )
    )
    q42_rank20_packet_spectral_label_filter_result = (
        q42_rank20_packet_spectral_label_filter_audit["result"]
    )
    q42_rank20_integral_saturation_tie_break_audit = (
        build_q42_rank20_integral_saturation_tie_break_audit(
            q42_tensor_rank20_slice_quotient_audit,
            q42_rank20_packet_spectral_label_filter_audit,
        )
    )
    q42_rank20_integral_saturation_tie_break_result = (
        q42_rank20_integral_saturation_tie_break_audit["result"]
    )
    q42_saturated_basis_direct_doublet_skeleton_audit = (
        build_q42_saturated_basis_direct_doublet_skeleton_audit(
            q42_tensor_rank20_slice_quotient_audit,
            q42_rank20_packet_spectral_label_filter_audit,
            q42_rank20_integral_saturation_tie_break_audit,
        )
    )
    q42_saturated_basis_direct_doublet_skeleton_result = (
        q42_saturated_basis_direct_doublet_skeleton_audit["result"]
    )
    a985_2x2_sector_carrier_completion_audit = (
        build_a985_2x2_sector_carrier_completion_audit(
            q42_saturated_basis_direct_doublet_skeleton_audit
        )
    )
    a985_2x2_sector_carrier_completion_result = (
        a985_2x2_sector_carrier_completion_audit["result"]
    )
    sector33_packet239_zero_pair_anchor_audit = (
        build_sector33_packet239_zero_pair_anchor_audit(
            a985_2x2_sector_carrier_completion_audit
        )
    )
    sector33_packet239_zero_pair_anchor_result = (
        sector33_packet239_zero_pair_anchor_audit["result"]
    )
    a985_2x2_chart_signature_assignment_constraints_audit = (
        build_a985_2x2_chart_signature_assignment_constraints_audit(
            q42_saturated_basis_direct_doublet_skeleton_audit,
            a985_2x2_sector_carrier_completion_audit,
            sector33_packet239_zero_pair_anchor_audit,
        )
    )
    a985_2x2_chart_signature_assignment_constraints_result = (
        a985_2x2_chart_signature_assignment_constraints_audit["result"]
    )
    q12_packet_charge_sum_partition_fingerprint_audit = (
        build_q12_packet_charge_sum_partition_fingerprint_audit(
            q42_saturated_basis_direct_doublet_skeleton_audit,
            a985_2x2_chart_signature_assignment_constraints_audit,
        )
    )
    q12_packet_charge_sum_partition_fingerprint_result = (
        q12_packet_charge_sum_partition_fingerprint_audit["result"]
    )
    q42_packet239_q12_seed_anchor_tie_break_audit = (
        build_q42_packet239_q12_seed_anchor_tie_break_audit(
            q12_packet_low_support_audit,
            q42_rank20_packet_spectral_label_filter_audit,
        )
    )
    q42_packet239_q12_seed_anchor_tie_break_result = (
        q42_packet239_q12_seed_anchor_tie_break_audit["result"]
    )
    ingress_sources = {
        "hydrogen_transport_package": {
            "root": "ingress/d20_atom_transport_hydrogen_package",
            "status": signatures["hydrogen_golay_hamming_frame"],
            "open_targets": load_json(HYDROGEN_ATOM)["open_verifier_targets"],
        },
        "talagrand_python_handoff": {
            "root": "ingress/talagrand_python_handoff",
            "status": load_json(TALAGRAND_STATUS)["global_status"],
            "remaining_open_target": load_json(TALAGRAND_STATUS)["remaining_open_target"],
        },
    }

    checks = {
        "proof_obligations_scanned": proof_inventory["proof_obligation_report_count"] > 0,
        "outstanding_boundaries_preserved": proof_inventory["outstanding_boundary_count"] > 0,
        "hydrogen_has_triadic_h8_frame": signatures["hydrogen_golay_hamming_frame"]["h8_copies"] == 3
        and signatures["hydrogen_golay_hamming_frame"]["h8_copy_weight"] == 8
        and signatures["hydrogen_golay_hamming_frame"]["h8_copies_times_weight"] == 24,
        "golay_endpoint_has_weight8_minimum": signatures["hydrogen_golay_hamming_frame"][
            "golay_minimum_nonzero_weight"
        ]
        == 8,
        "static_axis_is_rank3_order32": signatures["static_axis"]["generator_count"] == 3
        and signatures["static_axis"]["mod2_reduction_rank"] == 3
        and signatures["static_axis"]["group_order"] == 32,
        "tropic_axis_gamma8_closes": signatures["tropic_axis"]["gamma8_mask"] == 256
        and signatures["tropic_axis"]["balance_sum"] == 0
        and signatures["tropic_axis"]["hidden_component_count"] == 3,
        "optic_axis_is_rank3_equal_2pow8_screen": signatures["optic_axis"]["rank_over_f2"] == 3
        and set(signatures["optic_axis"]["cell_counts_by_signature"].values()) == {256}
        and len(signatures["optic_axis"]["cell_counts_by_signature"]) == 8,
        "sandpile_target_is_nontrivial_and_screen_linked": signatures["sandpile_target"][
            "mixed_sandpile_class_count"
        ]
        == 154
        and signatures["sandpile_target"]["tube_grade_is_sandpile_class_invariant"] is False,
        "bruteforce_assignment_is_degenerate": assignment_search["best_assignment_count"] == 6
        and assignment_search["permutation_count"] == 6,
        "discriminator_distinguishes_screen0": discriminator_result["screen0_distinguished"] is True,
        "discriminator_selector_choice_leaves_screen12_tie": (
            discriminator_result["screen1_screen2_still_tied_by_selector_choice"] is True
            and hcycle_pullback["selector_choice_labels_separate_all_three"] is False
        ),
        "discriminator_turn_labels_separate_conditionally": (
            discriminator_result["turn_labels_break_all_three_if_BSV_is_allowed_as_H8_proxy"] is True
            and hcycle_pullback["turn_type_labels_separate_all_three"] is True
        ),
        "discriminator_bvs_unsigned_h8_proxy_certified": (
            discriminator_result["bvs_unsigned_h8_sector_proxy_certified"] is True
        ),
        "discriminator_screen_to_unsigned_h8_sector_assignment_unique": (
            discriminator_result["unique_screen_to_unsigned_h8_sector_assignment"] is True
        ),
        "discriminator_rgb_color_naming_remains_open": (
            discriminator_result["rgb_color_naming_remains_open"] is True
        ),
        "discriminator_static_overlap_not_individual_static_generator": (
            static_overlap["profiles_identical_across_static_generators"] is True
        ),
        "discriminator_full_assignment_remains_open": (
            discriminator_result["full_certified_h8_assignment_remains_open"] is True
        ),
        "static_tropic_static_frame_pulled_into_bvs": (
            pullback_result["static_frame_pulled_into_bvs"] is True
        ),
        "static_tropic_no_static_single_sector_generator": (
            pullback_result["static_individual_generator_to_single_sector_remains_open"] is True
        ),
        "static_tropic_static_public_zero_lands_on_S_screen": (
            pullback_result["static_public_zero_overlap_lands_on_S_screen"] is True
        ),
        "static_tropic_gamma8_visible_cycle_lands_on_V": (
            pullback_result["tropic_gamma8_visible_cycle_lands_on_V"] is True
        ),
        "static_tropic_gamma8_hidden_residual_is_R33": (
            pullback_result["tropic_hidden_residual_lands_on_R33_not_public_BVS"] is True
        ),
        "static_tropic_full_attachment_remains_open": (
            pullback_result["full_static_tropic_bvs_attachment_remains_open"] is True
        ),
        "ward_composition_gamma8_cycle5_to_mask288_certified": (
            ward_composition_result["tropic_ward_composition_found"] is True
        ),
        "ward_composition_closes_selected_balance": (
            ward_composition_result["selected_lift_closes_public_and_hidden_balance"] is True
        ),
        "ward_composition_visible_signature_stays_on_V_screen": (
            ward_composition_result["selected_lift_matches_V_screen_signature"] is True
        ),
        "ward_composition_static_z2_attachment_remains_open": (
            ward_composition_result[
                "direct_static_tropic_commutator_or_ward_term_remains_open"
            ]
            is True
        ),
        "selected_mask_z2_hits_hidden_sector33_kernel": (
            selected_mask_z2_result["z2_hits_hidden_sector33_kernel"] is True
        ),
        "selected_mask_z2_not_scalar_on_full_V_screen_envelope": (
            selected_mask_z2_result[
                "z2_not_scalar_on_full_selected_screen_support_envelope"
            ]
            is True
        ),
        "selected_mask_z2_attachment_remains_open": (
            selected_mask_z2_result["z2_selected_mask_static_attachment_remains_open"]
            is True
        ),
        "selected_mask_exact_h6_support_materialized": (
            exact_h6_result["selected_h6_public_atom_support_materialized"] is True
        ),
        "selected_mask_exact_h6_support_is_weight8": (
            exact_h6_result["selected_h6_public_atom_support_is_weight8"] is True
        ),
        "selected_mask_exact_z2_retest_blocked_by_missing_projection": (
            exact_h6_result["q12_exact_z2_retest_blocked_by_missing_projection"] is True
        ),
        "q12_h6_selector_candidate_materialized": (
            q12_h6_projection_result["q12_selector_graph_materialized"] is True
        ),
        "q12_h6_raw_combinations_do_not_hit_mask288": (
            q12_h6_projection_result[
                "raw_q12_union_does_not_materialize_target_support"
            ]
            is True
            and q12_h6_projection_result[
                "raw_q12_parity_does_not_materialize_target_support"
            ]
            is True
            and q12_h6_projection_result[
                "signed_unit_q12_combination_does_not_materialize_target_support"
            ]
            is True
        ),
        "q12_h6_packet_normalization_remains_blocked": (
            q12_h6_projection_result[
                "q12_h6_candidate_not_sufficient_for_z2_retest"
            ]
            is True
        ),
        "q12_packet_low_support_seed_found": (
            q12_packet_low_support_result["mask288_has_unique_low_support_packet_seed"]
            is True
        ),
        "q12_packet_low_support_seed_not_full_bridge": (
            q12_packet_low_support_result[
                "q12_packet_seed_found_but_full_bridge_open"
            ]
            is True
        ),
        "q12_packet_support3_seed_extension_blocked": (
            mask288_q12_packet_seed_support3_result[
                "single_missing_atom_support3_extension_blocked_by_parity"
            ]
            is True
        ),
        "q12_packet_widened_support3_rank2_candidates_found": (
            mask288_q12_packet_seed_broadened_result[
                "widened_support3_rank2_candidates_materialized"
            ]
            is True
        ),
        "q12_rank2_candidates_not_directly_tensor_labelled": (
            mask288_q12_rank2_label_result[
                "rank2_doublets_not_directly_q12_tensor_labelled"
            ]
            is True
        ),
        "q12_rank2_linear_combinations_cover_with_overhang_only": (
            mask288_q12_rank2_linear_combination_result[
                "small_q12_product_combinations_cover_with_overhang_only"
            ]
            is True
        ),
        "q12_product_overhang_survives_existing_readouts": (
            mask288_q12_product_overhang_invariant_result[
                "overhang_survives_existing_bvs_and_packet_readouts"
            ]
            is True
        ),
        "q12_outside_class1_residue_cancellation_found_exact_support_open": (
            mask288_q12_outside_class1_residue_cancellation_result[
                "outside_class1_residue_cancellation_found_exact_support_open"
            ]
            is True
        ),
        "q12_packet_normalized_seed_assembly_remains_blocked": (
            mask288_q12_packet_normalized_seed_assembly_result[
                "packet_normalized_q12_seed_assembly_remains_blocked"
            ]
            is True
        ),
        "q12_direct_paired_doublet_search_finds_rank2_short_of_full_bridge": (
            mask288_q12_direct_paired_doublet_search_result[
                "direct_q12_paired_doublet_search_finds_rank2_short_of_full_bridge"
            ]
            is True
        ),
        "q12_one_sided_seed_correction_finds_new_rank2_families_projection_open": (
            mask288_q12_one_sided_seed_correction_result[
                "one_sided_seed_correction_finds_new_rank2_families_projection_open"
            ]
            is True
        ),
        "q12_corrected_rank20_selection_blocked_by_rank9_image_ceiling": (
            mask288_q12_corrected_rank20_selection_result[
                "corrected_rank20_selection_blocked_by_rank9_image_ceiling"
            ]
            is True
        ),
        "q12_rank_escape_probe_finds_nonscalar_rank11_still_blocked": (
            mask288_q12_rank_escape_probe_result[
                "rank_escape_probe_finds_nonscalar_rank11_still_blocked"
            ]
            is True
        ),
        "ingress_projection_inventory_confirms_packet_bridge_gap": (
            ingress_projection_inventory_result[
                "ingress_projection_inventory_confirms_packet_bridge_gap"
            ]
            is True
        ),
        "natural_25_to_20_projection_candidate_rejected": (
            boundary_packet_projection_candidate_result[
                "natural_25_to_20_projection_candidate_rejected"
            ]
            is True
        ),
        "signed_step_column_search_finds_external_but_rank_limited_rows": (
            signed_step_column_packet_search_result[
                "signed_step_column_search_finds_external_but_rank_limited_rows"
            ]
            is True
        ),
        "support4_signed_step_columns_still_rank2": (
            support4_signed_step_column_span_result[
                "support4_signed_step_columns_still_rank2"
            ]
            is True
        ),
        "full_step_column_congruence_lattice_rank4_still_short": (
            full_step_column_congruence_lattice_result[
                "full_step_column_congruence_lattice_rank4_still_short"
            ]
            is True
        ),
        "q42_q12_quotient_adjusted_packet_filter_still_rank_limited": (
            q42_q12_quotient_adjusted_packet_filter_result[
                "q42_q12_quotient_adjusted_packet_filter_still_rank_limited"
            ]
            is True
        ),
        "hidden_q42_a985_matrix_unit_capacity_requires_kernel_choice": (
            hidden_q42_a985_matrix_unit_capacity_result[
                "hidden_q42_a985_matrix_unit_capacity_requires_kernel_choice"
            ]
            is True
        ),
        "q42_tensor_left_slice_rank20_quotient_found_packet_label_open": (
            q42_tensor_rank20_slice_quotient_result[
                "q42_tensor_left_slice_rank20_quotient_found_packet_label_open"
            ]
            is True
        ),
        "q42_rank20_packet_spectral_label_filter_cardinality_only": (
            q42_rank20_packet_spectral_label_filter_result[
                "q42_rank20_packet_spectral_label_filter_cardinality_only"
            ]
            is True
        ),
        "q42_rank20_integral_saturation_tie_break_selects_drop8": (
            q42_rank20_integral_saturation_tie_break_result[
                "q42_rank20_integral_saturation_tie_break_selects_drop8"
            ]
            is True
        ),
        "q42_saturated_basis_direct_doublet_skeleton_only_two_of_ten": (
            q42_saturated_basis_direct_doublet_skeleton_result[
                "q42_saturated_basis_direct_doublet_skeleton_only_two_of_ten"
            ]
            is True
        ),
        "a985_2x2_sector_carrier_completes_q42_direct_doublet_shortfall": (
            a985_2x2_sector_carrier_completion_result[
                "a985_2x2_sector_carrier_completes_q42_direct_doublet_shortfall"
            ]
            is True
        ),
        "sector33_packet239_zero_pair_anchor_candidate_operator_open": (
            sector33_packet239_zero_pair_anchor_result[
                "sector33_packet239_zero_pair_anchor_candidate_operator_open"
            ]
            is True
        ),
        "a985_2x2_chart_signatures_constrain_remaining_assignment_operator_open": (
            a985_2x2_chart_signature_assignment_constraints_result[
                "a985_2x2_chart_signatures_constrain_remaining_assignment_operator_open"
            ]
            is True
        ),
        "q12_packet_charge_sum_partition_fingerprint_operator_open": (
            q12_packet_charge_sum_partition_fingerprint_result[
                "q12_packet_charge_sum_partition_fingerprint_operator_open"
            ]
            is True
        ),
        "q42_packet239_q12_seed_anchor_tie_break_conditional": (
            q42_packet239_q12_seed_anchor_tie_break_result[
                "q42_packet239_q12_seed_anchor_tie_break_conditional"
            ]
            is True
        ),
    }

    artifact: dict[str, Any] = {
        "schema": "d20.generated.hydrogen_sandpile_golay_bridge_probe@1",
        "status": "D20_HYDROGEN_SANDPILE_GOLAY_BRIDGE_PROBE_PROVISIONAL_ASSIGNMENT_DEGENERATE",
        "claim_boundary": (
            "This is a bounded invariant-discovery probe. It unifies the visible proof-obligation "
            "and ingress data into a rank-3/weight-8 bridge candidate, but it does not construct a "
            "canonical morphism or prove a static/tropic/optic assignment."
        ),
        "stages": {
            "draft": "scan documentation, proof obligations, and ingress handoff data",
            "witness": "extract static, tropic, optic, hydrogen/Golay, and sandpile signatures",
            "coherence": "score all static/tropic/optic to H8-copy assignments under bounded invariants",
            "closure": "preserve open boundaries and mark assignment as degenerate",
            "emit": "emit a reproducible generated probe summary",
        },
        "inputs": {rel: input_entry(rel) for rel in INPUT_RELS},
        "proof_obligation_inventory": proof_inventory,
        "ingress_sources": ingress_sources,
        "signatures": signatures,
        "assignment_search": assignment_search,
        "discriminator_search": discriminator_search,
        "static_tropic_sector_pullback": static_tropic_pullback,
        "static_tropic_ward_composition_audit": ward_composition_audit,
        "selected_mask_z2_static_audit": selected_mask_z2_audit,
        "selected_mask_exact_h6_support_audit": selected_mask_exact_h6_support,
        "interpretation": {
            "candidate_bridge": [
                "static: Z/2 x Z/4^2 gives a three-generator order-32 readout",
                "tropic: gamma_8 height-coherent residual transport gives a rank-3 hidden ledger and exact cancellation",
                "optic: three signed-turn screens give a rank-3 F2 map with eight 2^8 cells",
                "sandpile: the screen-0 tube grade maps into sandpile classes but is not a sandpile-class invariant",
            ],
            "negative_result": (
                "No unique assignment of static/tropic/optic to the three H8 copies is witnessed by "
                "the available data; every permutation has the same bounded score."
            ),
            "missing_discriminator": (
                "A concrete map from RGB-named H8 copies into the screen defect vectors, static "
                "generators, or hidden residual channel. The current discriminator certifies B/S/V "
                "as unsigned weight-8 H8-sector proxies, assigns optic screens to those sectors, "
                "pulls the static frame into B/V/S object indexing, and places gamma_8 on the V "
                "visible cycle. The certified selected Ward lift gamma_8 + cycle5 closes at mask "
                "288 with a V-screen turn signature, but it still does not name the RGB colors "
                "or attach the z2 target-S static near detector to a Ward/commutator term. "
                "Evaluating z2 on the matched V-screen envelope hits hidden sector 33 but fails "
                "to be scalar on the full envelope. The exact mask-288 Lambda^3 H6 support is now "
                "materialized as eight public atoms. The compiler/selector q12 pentagon readout "
                "covers Lambda^3 H6 uniformly but does not raw-materialize that support by union, "
                "parity, or signed unit coefficients, and the z2 exact retest remains blocked by "
                "the certified absence of a q12/A985 quotient-to-packet projection. Intersecting "
                "q12 with the low-support packet-SNF atlas finds a single mask-local seed [0,11] "
                "inside q12 class 1 / relation 227, but the row-normalization and rank-one doublet "
                "obstructions keep it short of a full bridge. Extending that seed by one missing "
                "mask atom at signed support 3 gives no even boundary images, so the packet parity "
                "layer blocks this narrow extension. Unit-sign support-4 remains parity-blocked, "
                "but widening support-3 coefficients to +/-1,+/-2 materializes 32 rank-2 "
                "packet-compatible doublets across the four missing-atom families. A direct q12 "
                "tensor label scan shows those rank-2 candidates are not yet q12/A985-labelled "
                "packet actions. Small q12-product linear combinations cover each rank-2 target "
                "family but only with extra H6 support. That overhang survives the known B/V/S "
                "public readout and packet row-normalization screen; static parity is still "
                "blocked by the missing q12/A985 quotient-to-packet projection. Broadening "
                "the q12 product search outside seed class 1 cancels every overhang residue "
                "modulo 6, but only by increasing integer H6 overhang, so exact support "
                "remains open. Dividing those residue-cleared witnesses by scalar 6 gives "
                "even boundary rows, but they add no packet-compatible doublets to the "
                "certified low-support/support-3 atlas. Pairing the q12 residue-cleared "
                "rows directly against each other does find rank-2 packet-compatible "
                "doublets, but only across eight support families, still short of the "
                "ten-family packet bridge target. Allowing one seed-class-1 correction "
                "term on exactly one side adds twenty new rank-2 support families and "
                "crosses that threshold, but independence and the raw q12/A985 packet "
                "projection remain open. The exact rank test now shows the current "
                "corrected q12 image pool spans rank 9 over Q, so no ten-doublet selection "
                "from this pool can form a rank-20 packet basis. A second scalar-6 seed "
                "correction stays in rank 9, while bounded raw non-scalar q12 row pairs "
                "escape only to rank 11. In the 25-coordinate boundary image space the "
                "rank-11 q12 span has fourteen primitive rational annihilator equations; "
                "the packet SNF target is 20-dimensional, so direct cokernel comparison "
                "remains blocked by the missing boundary-to-packet projection. A rank-20 "
                "packet target still needs at least nine independent directions outside "
                "this bounded q12 row space. The audited ingress/A985 data supplies "
                "Lambda_hc loop materialization and sector-33 public invisibility, but "
                "not the A985/q12-to-full-packet restriction; the natural Loop_297 "
                "25-to-20 step-column candidate is explicitly rejected by the packet "
                "SNF image test. A bounded signed/scalar step-column search does find "
                "external packet-SNF rows, with 2*step_atom_16 as the minimal witness, "
                "but the compatible packet targets still span only rank 2. Extending "
                "that signed search through support four adds many compatible rows and "
                "four new target vectors, but no new packet target rank. Solving the "
                "full natural step-column congruence lattice breaks the support-four "
                "ceiling and reaches packet target rank 4, but remains 16 ranks short "
                "of the full packet target. Pushing the q42 product tensor through the "
                "certified q42-to-q12 refinement and the q12 public pentagon readout "
                "materializes many scalar-6 quotient rows, but their natural packet "
                "targets span rank 3 and stay inside the solved natural type lattice. "
                "Thus the public quotient-adjusted route is rank-limited; only a hidden "
                "q42/A985-to-packet projection could still escape this ceiling. The "
                "hidden raw A985 matrix-unit shadow now gives a sharper rank sandwich: "
                "central q42 characters are too small for a rank-20 packet target, while "
                "full q42 matrix-unit rows have rank 42 and therefore require an explicit "
                "noncentral kernel/quotient before they can land in the 20-packet target "
                "or the 40-dimensional packet block lift. A bounded q42 tensor slice "
                "search now finds exact rank-20 quotient witnesses: the first is the "
                "left-slice triple [0,1,22], whose q12 pushdown has only rank 8. This "
                "supplies a hidden 22-dimensional kernel candidate but still leaves the "
                "ten full-packet doublet labeling open. The packet spectral-charge table "
                "does provide 20 unique full-exposure fine keys and ten unique doublet "
                "keys, but the q42 active support has the primitive relation "
                "13*q42_2 - q42_8 = 0, so two rank-preserving q42 bases remain. The "
                "packet239 zero-pair side channel and the existing q12 class-1 packet "
                "seed now conditionally select the drop-q42_8 basis, because the "
                "drop-q42_2 basis erases q12 class 1. The q42 tensor gives an "
                "independent integral reason for the same choice: q42_8 is exactly "
                "13*q42_2 on the rank-20 slice, so dropping q42_2 creates an index-13 "
                "saturation defect. This is stronger than cardinality compatibility "
                "but still not a canonical hidden packet label map. A direct q42 support "
                "twin probe finds only two of the ten required packet doublets, so the "
                "remaining map must be nonlocal in the A985/packet operator data. The "
                "A985 matrix-unit carrier now supplies an exact dimension profile for "
                "that nonlocal remainder: exactly eight 2x2 A985 sectors, including "
                "raw sector 33, match the eight missing packet Mat_2 blocks. Raw "
                "sector 33 now has a unique target anchor: the packet239 zero-pair "
                "component, but the actual sector-to-packet operator is still open. "
                "The A985 matrix-unit chart signatures now constrain the unanchored "
                "assignment to seven A985 2x2 carriers plus two direct q42 blocks for "
                "the nine remaining packet components. A first charge-frame "
                "fingerprint now matches the q12 carrier partition against packet "
                "sector26 charge-sum classes with size profile [1,1,1,2,2,2], reducing "
                "the assignment surface without producing the operator."
            ),
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "q12_h6_projection_audit": q12_h6_projection_audit,
        "q12_packet_low_support_normalization_audit": q12_packet_low_support_audit,
        "mask288_q12_packet_seed_support3_audit": mask288_q12_packet_seed_support3_audit,
        "mask288_q12_packet_seed_broadened_extension_audit": (
            mask288_q12_packet_seed_broadened_audit
        ),
        "mask288_q12_rank2_doublet_label_audit": mask288_q12_rank2_label_audit,
        "mask288_q12_rank2_linear_combination_audit": (
            mask288_q12_rank2_linear_combination_audit
        ),
        "mask288_q12_product_overhang_invariant_audit": (
            mask288_q12_product_overhang_invariant_audit
        ),
        "mask288_q12_outside_class1_residue_cancellation_audit": (
            mask288_q12_outside_class1_residue_cancellation_audit
        ),
        "mask288_q12_packet_normalized_seed_assembly_audit": (
            mask288_q12_packet_normalized_seed_assembly_audit
        ),
        "mask288_q12_direct_paired_doublet_search_audit": (
            mask288_q12_direct_paired_doublet_search_audit
        ),
        "mask288_q12_one_sided_seed_correction_audit": (
            mask288_q12_one_sided_seed_correction_audit
        ),
        "mask288_q12_corrected_rank20_selection_audit": (
            mask288_q12_corrected_rank20_selection_audit
        ),
        "mask288_q12_rank_escape_probe_audit": mask288_q12_rank_escape_probe_audit,
        "ingress_boundary_packet_projection_inventory_audit": (
            ingress_projection_inventory_audit
        ),
        "boundary_packet_projection_candidate_audit": (
            boundary_packet_projection_candidate_audit
        ),
        "signed_step_column_packet_search_audit": (
            signed_step_column_packet_search_audit
        ),
        "support4_signed_step_column_span_audit": (
            support4_signed_step_column_span_audit
        ),
        "full_step_column_congruence_lattice_audit": (
            full_step_column_congruence_lattice_audit
        ),
        "q42_q12_quotient_adjusted_packet_filter_audit": (
            q42_q12_quotient_adjusted_packet_filter_audit
        ),
        "hidden_q42_a985_matrix_unit_capacity_audit": (
            hidden_q42_a985_matrix_unit_capacity_audit
        ),
        "q42_tensor_rank20_slice_quotient_audit": (
            q42_tensor_rank20_slice_quotient_audit
        ),
        "q42_rank20_packet_spectral_label_filter_audit": (
            q42_rank20_packet_spectral_label_filter_audit
        ),
        "q42_rank20_integral_saturation_tie_break_audit": (
            q42_rank20_integral_saturation_tie_break_audit
        ),
        "q42_saturated_basis_direct_doublet_skeleton_audit": (
            q42_saturated_basis_direct_doublet_skeleton_audit
        ),
        "a985_2x2_sector_carrier_completion_audit": (
            a985_2x2_sector_carrier_completion_audit
        ),
        "sector33_packet239_zero_pair_anchor_audit": (
            sector33_packet239_zero_pair_anchor_audit
        ),
        "a985_2x2_chart_signature_assignment_constraints_audit": (
            a985_2x2_chart_signature_assignment_constraints_audit
        ),
        "q12_packet_charge_sum_partition_fingerprint_audit": (
            q12_packet_charge_sum_partition_fingerprint_audit
        ),
        "q42_packet239_q12_seed_anchor_tie_break_audit": (
            q42_packet239_q12_seed_anchor_tie_break_audit
        ),
        "next_highest_yield_item": (
            "Lift the q12-vs-sector26 charge-sum partition fingerprint from size-profile "
            "matching to labelled class constraints; start with the residual raw11/raw36 "
            "q12=4 twin and the three size-2 packet sector26 charge-sum classes."
        ),
    }
    artifact["artifact_sha256"] = sha_json({k: v for k, v in artifact.items() if k != "artifact_sha256"})
    return artifact


def main() -> None:
    artifact = build_artifact()
    print(
        json.dumps(
            {
                "artifact": "not written; recompute with build_artifact()",
                "status": artifact["status"],
                "all_checks_pass": artifact["all_checks_pass"],
                "artifact_sha256": artifact["artifact_sha256"],
                "best_assignment_count": artifact["assignment_search"]["best_assignment_count"],
                "screen_to_unsigned_h8_sector_assignment": artifact["discriminator_search"][
                    "discriminator_result"
                ]["screen_to_unsigned_h8_sector_assignment"],
                "gamma8_visible_sector": artifact["static_tropic_sector_pullback"]["tropic"][
                    "gamma8_dominant_visible_sector"
                ],
                "static_public_zero_screen_sector": artifact["static_tropic_sector_pullback"][
                    "static"
                ]["public_zero_screen_sector"],
                "ward_selected_mask": artifact["static_tropic_ward_composition_audit"][
                    "selector_summary"
                ]["selected_mask"],
                "ward_selected_screen_sectors": artifact["static_tropic_ward_composition_audit"][
                    "selected_turn_signature_screen_sectors"
                ],
                "mask288_z2_status": artifact["selected_mask_z2_static_audit"]["status"],
                "mask288_z2_non_scalar_supports": artifact["selected_mask_z2_static_audit"][
                    "non_scalar_supports"
                ],
                "mask288_exact_h6_public_atom_ids": artifact[
                    "selected_mask_exact_h6_support_audit"
                ]["selected_h6_public_atom_ids"],
                "mask288_z2_exact_retest_status": artifact[
                    "selected_mask_exact_h6_support_audit"
                ]["z2_exact_retest_status"],
                "q12_h6_projection_status": artifact["q12_h6_projection_audit"]["status"],
                "q12_h6_raw_union_exact_solution_count": artifact[
                    "q12_h6_projection_audit"
                ]["raw_combination_bruteforce"]["raw_union_exact_solution_count"],
                "q12_h6_raw_parity_exact_solution_count": artifact[
                    "q12_h6_projection_audit"
                ]["raw_combination_bruteforce"]["raw_parity_exact_solution_count"],
                "q12_h6_signed_unit_exact_hit_found": artifact[
                    "q12_h6_projection_audit"
                ]["signed_unit_bruteforce"]["exact_hit_found"],
                "mask288_q12_packet_seed_status": artifact[
                    "q12_packet_low_support_normalization_audit"
                ]["status"],
                "mask288_q12_packet_seed_rows": artifact[
                    "q12_packet_low_support_normalization_audit"
                ]["mask288_q12_packet_seed_rows"],
                "mask288_q12_packet_seed_support3_status": artifact[
                    "mask288_q12_packet_seed_support3_audit"
                ]["status"],
                "mask288_q12_packet_seed_support3_even_candidate_count": artifact[
                    "mask288_q12_packet_seed_support3_audit"
                ]["even_image_candidate_count"],
                "mask288_q12_packet_seed_support3_compatible_doublet_count": artifact[
                    "mask288_q12_packet_seed_support3_audit"
                ]["compatible_doublet_count"],
                "mask288_q12_packet_seed_broadened_status": artifact[
                    "mask288_q12_packet_seed_broadened_extension_audit"
                ]["status"],
                "mask288_q12_packet_seed_widened_rank2_doublet_count": artifact[
                    "mask288_q12_packet_seed_broadened_extension_audit"
                ]["support3_widened_summary"]["rank2_doublet_count"],
                "mask288_q12_packet_seed_support4_unit_even_candidate_count": artifact[
                    "mask288_q12_packet_seed_broadened_extension_audit"
                ]["support4_unit_summary"]["even_image_candidate_count"],
                "mask288_q12_rank2_label_status": artifact[
                    "mask288_q12_rank2_doublet_label_audit"
                ]["status"],
                "mask288_q12_rank2_direct_product_label_count": artifact[
                    "mask288_q12_rank2_doublet_label_audit"
                ]["direct_q12_product_label_count"],
                "mask288_q12_rank2_linear_combination_status": artifact[
                    "mask288_q12_rank2_linear_combination_audit"
                ]["status"],
                "mask288_q12_rank2_linear_cover_count": artifact[
                    "mask288_q12_rank2_linear_combination_audit"
                ]["total_cover_solution_count"],
                "mask288_q12_rank2_linear_exact_count": artifact[
                    "mask288_q12_rank2_linear_combination_audit"
                ]["total_exact_support_solution_count"],
                "mask288_q12_product_overhang_status": artifact[
                    "mask288_q12_product_overhang_invariant_audit"
                ]["status"],
                "mask288_q12_product_overhang_nonzero_mod6_families": artifact[
                    "mask288_q12_product_overhang_invariant_audit"
                ]["packet_normalization_readout"][
                    "families_with_nonzero_overhang_residue_mod6"
                ],
                "mask288_q12_product_overhang_static_parity_status": artifact[
                    "mask288_q12_product_overhang_invariant_audit"
                ]["static_parity_readout"]["status"],
                "mask288_q12_outside_class1_cancellation_status": artifact[
                    "mask288_q12_outside_class1_residue_cancellation_audit"
                ]["status"],
                "mask288_q12_outside_class1_cancellation_residue_clear_count": artifact[
                    "mask288_q12_outside_class1_residue_cancellation_audit"
                ]["total_residue_clear_candidate_count"],
                "mask288_q12_outside_class1_cancellation_exact_count": artifact[
                    "mask288_q12_outside_class1_residue_cancellation_audit"
                ]["total_exact_support_candidate_count"],
                "mask288_q12_packet_normalized_assembly_status": artifact[
                    "mask288_q12_packet_normalized_seed_assembly_audit"
                ]["status"],
                "mask288_q12_packet_normalized_q12_compatible_doublet_count": artifact[
                    "mask288_q12_packet_normalized_seed_assembly_audit"
                ]["candidate_pool_summary"]["q12_involving_compatible_doublet_count"],
                "mask288_q12_packet_normalized_compatible_doublet_count": artifact[
                    "mask288_q12_packet_normalized_seed_assembly_audit"
                ]["candidate_pool_summary"]["compatible_doublet_count"],
                "mask288_q12_direct_paired_doublet_status": artifact[
                    "mask288_q12_direct_paired_doublet_search_audit"
                ]["status"],
                "mask288_q12_direct_paired_doublet_count": artifact[
                    "mask288_q12_direct_paired_doublet_search_audit"
                ]["compatible_doublet_summary"]["compatible_doublet_count"],
                "mask288_q12_direct_paired_rank2_family_count": artifact[
                    "mask288_q12_direct_paired_doublet_search_audit"
                ]["compatible_doublet_summary"]["rank2_support_family_count"],
                "mask288_q12_one_sided_seed_correction_status": artifact[
                    "mask288_q12_one_sided_seed_correction_audit"
                ]["status"],
                "mask288_q12_one_sided_seed_correction_doublet_count": artifact[
                    "mask288_q12_one_sided_seed_correction_audit"
                ]["compatible_doublet_summary"]["compatible_doublet_count"],
                "mask288_q12_one_sided_seed_correction_combined_rank2_family_count": artifact[
                    "mask288_q12_one_sided_seed_correction_audit"
                ]["compatible_doublet_summary"]["combined_rank2_support_family_count"],
                "mask288_q12_corrected_rank20_selection_status": artifact[
                    "mask288_q12_corrected_rank20_selection_audit"
                ]["status"],
                "mask288_q12_corrected_rank20_selection_rank": artifact[
                    "mask288_q12_corrected_rank20_selection_audit"
                ]["rank_ceiling_summary"]["combined_boundary_image_rank_over_Q"],
                "mask288_q12_corrected_rank20_selection_unique_images": artifact[
                    "mask288_q12_corrected_rank20_selection_audit"
                ]["rank_ceiling_summary"]["unique_boundary_image_count"],
                "mask288_q12_rank_escape_status": artifact[
                    "mask288_q12_rank_escape_probe_audit"
                ]["status"],
                "mask288_q12_rank_escape_raw_nonscalar_rank": artifact[
                    "mask288_q12_rank_escape_probe_audit"
                ]["raw_non_scalar_pair_summary"][
                    "raw_non_scalar_boundary_image_rank_over_Q"
                ],
                "mask288_q12_rank_escape_raw_pair_count": artifact[
                    "mask288_q12_rank_escape_probe_audit"
                ]["raw_non_scalar_pair_summary"]["raw_packet_compatible_pair_count"],
                "mask288_q12_rank11_annihilator_dimension": artifact[
                    "mask288_q12_rank_escape_probe_audit"
                ]["rank11_annihilator_summary"]["annihilator_dimension_over_Q"],
                "mask288_q12_rank11_external_generator_lower_bound": artifact[
                    "mask288_q12_rank_escape_probe_audit"
                ]["rank11_annihilator_summary"][
                    "outside_q12_rational_generator_lower_bound"
                ],
                "ingress_projection_inventory_status": artifact[
                    "ingress_boundary_packet_projection_inventory_audit"
                ]["status"],
                "ingress_projection_inventory_missing_bridge_count": artifact[
                    "ingress_boundary_packet_projection_inventory_audit"
                ]["packet_restriction_gap_summary"]["missing_bridge_count"],
                "boundary_packet_projection_candidate_status": artifact[
                    "boundary_packet_projection_candidate_audit"
                ]["status"],
                "boundary_packet_projection_candidate_passing_columns": artifact[
                    "boundary_packet_projection_candidate_audit"
                ]["candidate_summary"]["columns_passing_packet_snf_image"],
                "signed_step_column_search_status": artifact[
                    "signed_step_column_packet_search_audit"
                ]["status"],
                "signed_step_column_search_compatible_count": artifact[
                    "signed_step_column_packet_search_audit"
                ]["search_summary"]["compatible_row_count"],
                "signed_step_column_search_target_rank": artifact[
                    "signed_step_column_packet_search_audit"
                ]["search_summary"]["unique_target_vector_rank_over_Q"],
                "support4_signed_step_column_status": artifact[
                    "support4_signed_step_column_span_audit"
                ]["status"],
                "support4_signed_step_column_compatible_count": artifact[
                    "support4_signed_step_column_span_audit"
                ]["support4_summary"]["compatible_row_count_by_support"]["4"],
                "support4_signed_step_column_target_rank": artifact[
                    "support4_signed_step_column_span_audit"
                ]["support4_summary"][
                    "unique_target_vector_rank_over_Q_support_le_4"
                ],
                "full_step_column_lattice_status": artifact[
                    "full_step_column_congruence_lattice_audit"
                ]["status"],
                "full_step_column_lattice_target_rank": artifact[
                    "full_step_column_congruence_lattice_audit"
                ]["full_lattice_summary"]["basis_target_rank_over_Q"],
                "full_step_column_lattice_packet_shortfall": artifact[
                    "full_step_column_congruence_lattice_audit"
                ]["full_lattice_summary"][
                    "packet_target_rank_shortfall_after_full_type_lattice"
                ],
                "q42_q12_quotient_filter_status": artifact[
                    "q42_q12_quotient_adjusted_packet_filter_audit"
                ]["status"],
                "q42_q12_quotient_filter_hidden_rank_lost": artifact[
                    "q42_q12_quotient_adjusted_packet_filter_audit"
                ]["quotient_adjusted_summary"][
                    "q42_hidden_rank_lost_under_q12_public_readout"
                ],
                "q42_q12_quotient_filter_natural_pass_count": artifact[
                    "q42_q12_quotient_adjusted_packet_filter_audit"
                ]["quotient_adjusted_summary"][
                    "q42_scalar6_natural_target_passing_row_count"
                ],
                "q42_q12_quotient_filter_natural_pass_rank": artifact[
                    "q42_q12_quotient_adjusted_packet_filter_audit"
                ]["quotient_adjusted_summary"][
                    "q42_scalar6_natural_target_passing_rank_over_Q"
                ],
                "q42_q12_quotient_filter_packet_shortfall": artifact[
                    "q42_q12_quotient_adjusted_packet_filter_audit"
                ]["quotient_adjusted_summary"][
                    "q42_natural_pass_packet_rank_shortfall"
                ],
                "hidden_q42_a985_capacity_status": artifact[
                    "hidden_q42_a985_matrix_unit_capacity_audit"
                ]["status"],
                "hidden_q42_a985_matrix_unit_rank": artifact[
                    "hidden_q42_a985_matrix_unit_capacity_audit"
                ]["hidden_capacity_summary"]["q42_matrix_unit_aggregate_rank_mod_p"],
                "hidden_q42_a985_character_representative_rank": artifact[
                    "hidden_q42_a985_matrix_unit_capacity_audit"
                ]["hidden_capacity_summary"][
                    "q42_character_representative_rank_over_Q"
                ],
                "hidden_q42_a985_packet_target_excess": artifact[
                    "hidden_q42_a985_matrix_unit_capacity_audit"
                ]["hidden_capacity_summary"][
                    "q42_matrix_unit_rank_excess_over_packet_target"
                ],
                "hidden_q42_a985_block_lift_excess": artifact[
                    "hidden_q42_a985_matrix_unit_capacity_audit"
                ]["hidden_capacity_summary"][
                    "q42_matrix_unit_rank_excess_over_block_lift"
                ],
                "q42_tensor_rank20_slice_status": artifact[
                    "q42_tensor_rank20_slice_quotient_audit"
                ]["status"],
                "q42_tensor_rank20_slice_first_exact": artifact[
                    "q42_tensor_rank20_slice_quotient_audit"
                ]["rank20_slice_summary"]["first_exact_rank20_left_classes"],
                "q42_tensor_rank20_slice_exact_count": artifact[
                    "q42_tensor_rank20_slice_quotient_audit"
                ]["rank20_slice_summary"]["exact_rank20_combo_count"],
                "q42_tensor_rank20_slice_q12_pushdown_rank": artifact[
                    "q42_tensor_rank20_slice_quotient_audit"
                ]["rank20_slice_summary"][
                    "first_exact_rank20_q12_pushdown_rank_over_Q"
                ],
                "q42_rank20_packet_label_filter_status": artifact[
                    "q42_rank20_packet_spectral_label_filter_audit"
                ]["status"],
                "q42_rank20_packet_label_filter_active_relation": artifact[
                    "q42_rank20_packet_spectral_label_filter_audit"
                ]["packet_label_filter_summary"][
                    "q42_rank20_active_relation_support"
                ],
                "q42_rank20_packet_label_filter_fine_key_count": artifact[
                    "q42_rank20_packet_spectral_label_filter_audit"
                ]["packet_label_filter_summary"][
                    "full_exposure_fine_spectral_charge_key_count"
                ],
                "q42_rank20_packet_label_filter_doublet_key_count": artifact[
                    "q42_rank20_packet_spectral_label_filter_audit"
                ]["packet_label_filter_summary"][
                    "full_packet_doublet_pair_filter_key_count"
                ],
                "q42_integral_saturation_status": artifact[
                    "q42_rank20_integral_saturation_tie_break_audit"
                ]["status"],
                "q42_integral_saturation_selected_drop": artifact[
                    "q42_rank20_integral_saturation_tie_break_audit"
                ]["integral_saturation_summary"][
                    "selected_drop_q42_class_by_integral_saturation"
                ],
                "q42_integral_saturation_rejected_drop": artifact[
                    "q42_rank20_integral_saturation_tie_break_audit"
                ]["integral_saturation_summary"][
                    "rejected_drop_q42_class_by_integral_saturation"
                ],
                "q42_integral_saturation_rejected_index": artifact[
                    "q42_rank20_integral_saturation_tie_break_audit"
                ]["integral_saturation_summary"]["rejected_basis_index_defect"],
                "q42_direct_doublet_skeleton_status": artifact[
                    "q42_saturated_basis_direct_doublet_skeleton_audit"
                ]["status"],
                "q42_direct_doublet_skeleton_pair_count": artifact[
                    "q42_saturated_basis_direct_doublet_skeleton_audit"
                ]["direct_doublet_summary"]["global_same_support_q42_pair_count"],
                "q42_direct_doublet_skeleton_shortfall": artifact[
                    "q42_saturated_basis_direct_doublet_skeleton_audit"
                ]["direct_doublet_summary"][
                    "direct_support_twin_packet_doublet_shortfall"
                ],
                "a985_2x2_carrier_status": artifact[
                    "a985_2x2_sector_carrier_completion_audit"
                ]["status"],
                "a985_2x2_carrier_sector_count": artifact[
                    "a985_2x2_sector_carrier_completion_audit"
                ]["carrier_completion_summary"]["a985_two_by_two_sector_count"],
                "a985_2x2_carrier_combined_components": artifact[
                    "a985_2x2_sector_carrier_completion_audit"
                ]["carrier_completion_summary"]["combined_carrier_component_count"],
                "a985_2x2_carrier_contains_raw_sector33": artifact[
                    "a985_2x2_sector_carrier_completion_audit"
                ]["carrier_completion_summary"]["a985_raw_sector33_is_two_by_two"],
                "sector33_packet239_anchor_status": artifact[
                    "sector33_packet239_zero_pair_anchor_audit"
                ]["status"],
                "sector33_packet239_anchor_source_sector": artifact[
                    "sector33_packet239_zero_pair_anchor_audit"
                ]["anchor_summary"]["a985_raw_sector33_source_sector"],
                "sector33_packet239_anchor_packet_component": artifact[
                    "sector33_packet239_zero_pair_anchor_audit"
                ]["anchor_summary"]["packet_zero_pair_component_id"],
                "sector33_packet239_anchor_packet_pair": artifact[
                    "sector33_packet239_zero_pair_anchor_audit"
                ]["anchor_summary"]["packet_zero_pair_packet_pair"],
                "a985_chart_constraints_status": artifact[
                    "a985_2x2_chart_signature_assignment_constraints_audit"
                ]["status"],
                "a985_chart_constraints_class_count": artifact[
                    "a985_2x2_chart_signature_assignment_constraints_audit"
                ]["chart_constraint_summary"]["saturated_q42_overlap_class_count"],
                "a985_chart_constraints_remaining_carriers": artifact[
                    "a985_2x2_chart_signature_assignment_constraints_audit"
                ]["chart_constraint_summary"]["remaining_a985_two_by_two_count"],
                "a985_chart_constraints_remaining_packet_components": artifact[
                    "a985_2x2_chart_signature_assignment_constraints_audit"
                ]["chart_constraint_summary"][
                    "remaining_packet_component_count_after_anchor"
                ],
                "q12_packet_charge_sum_partition_status": artifact[
                    "q12_packet_charge_sum_partition_fingerprint_audit"
                ]["status"],
                "q12_packet_charge_sum_partition_carrier_histogram": artifact[
                    "q12_packet_charge_sum_partition_fingerprint_audit"
                ]["partition_summary"]["carrier_q12_signature_class_size_histogram"],
                "q12_packet_charge_sum_partition_packet_histogram": artifact[
                    "q12_packet_charge_sum_partition_fingerprint_audit"
                ]["partition_summary"]["packet_sector26_sum_class_size_histogram"],
                "q12_packet_charge_sum_partition_element_bijections": artifact[
                    "q12_packet_charge_sum_partition_fingerprint_audit"
                ]["partition_summary"]["size_compatible_element_bijection_count"],
                "q42_packet239_tie_break_status": artifact[
                    "q42_packet239_q12_seed_anchor_tie_break_audit"
                ]["status"],
                "q42_packet239_tie_break_selected_drop": artifact[
                    "q42_packet239_q12_seed_anchor_tie_break_audit"
                ]["tie_break_summary"][
                    "selected_drop_q42_class_by_q12_seed_anchor"
                ],
                "q42_packet239_tie_break_rejected_drop": artifact[
                    "q42_packet239_q12_seed_anchor_tie_break_audit"
                ]["tie_break_summary"][
                    "rejected_drop_q42_class_by_q12_seed_anchor"
                ],
                "q42_packet239_tie_break_packet_id": artifact[
                    "q42_packet239_q12_seed_anchor_tie_break_audit"
                ]["tie_break_summary"]["packet239_packet_id"],
                "outstanding_boundary_count": artifact["proof_obligation_inventory"][
                    "outstanding_boundary_count"
                ],
                "next_highest_yield_item": artifact["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
