from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, HCYCLE_INVARIANTS, DATA, ROOT
from src.verify_c2_selector_lookup_witness_source_package import PACKAGE_HALLOWEEN_ORBITS_CSV


OBLIGATION_ID = "cycle8_pi33_projection_coefficient"
DEFAULT_OUT_DIR = D20_INVARIANTS / "proof_obligations" / OBLIGATION_ID

SECTOR_ATTACHMENT_REPORT = (
    D20_INVARIANTS / "theorems" / "sector33_residual_attachment" / "report.json"
)
D20_EDGES_CSV = HCYCLE_INVARIANTS / "subscript_Hcycle_d20_edges.csv"
PRIMITIVE_CYCLES_CSV = HCYCLE_INVARIANTS / "subscript_Hcycle_primitive_cycles.csv"
TUBE_PROJECTION_SECTION = DATA / "tube" / "projection_section.json"
FULL_A985_LIFT = DATA / "drinfeld" / "full_a985_lift.json"
WEDDERBURN_TRACE = DATA / "drinfeld" / "wedderburn_trace.json"
BOUNDARY_TO_LOOP_REPORT = D20_INVARIANTS / "boundary_to_loop" / "report.json"
BOUNDARY_ANNIHILATION_REPORT = (
    D20_INVARIANTS / "theorems" / "sector33_boundary_annihilation" / "report.json"
)
HEIGHT_TRANSPORT_REPORT = (
    D20_INVARIANTS / "theorems" / "sector33_height_coherent_transport" / "report.json"
)
ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT = (
    D20_INVARIANTS / "theorems" / "sector33_all_residue_height_transport" / "report.json"
)
UNIQUE_PUBLIC_ZERO_SUPPORT_REPORT = (
    D20_INVARIANTS / "theorems" / "sector33_unique_public_zero_support" / "report.json"
)
SECTOR_PUBLIC_SHADOW_KERNEL_REPORT = (
    D20_INVARIANTS / "theorems" / "sector_public_shadow_kernel" / "report.json"
)
SECTOR_IDEMPOTENT_SUPPORT_ADMISSIBILITY_REPORT = (
    D20_INVARIANTS / "theorems" / "sector_idempotent_support_admissibility" / "report.json"
)
MINIMAL_COMPOSITE_TRANSPORT_REPORT = (
    D20_INVARIANTS / "theorems" / "minimal_composite_null_supports_transport" / "report.json"
)
SUPERSELECTION_FLUX_EXTENSION_REPORT = (
    D20_INVARIANTS / "theorems" / "superselection_flux_balance_extension" / "report.json"
)
TYPED_NONEXACT_OPTICAL_FLUX_REPORT = (
    D20_INVARIANTS / "theorems" / "typed_nonexact_optical_flux_update" / "report.json"
)
SECTOR26_INVARIANT_SUITE_REPORT = (
    D20_INVARIANTS / "theorems" / "sector26_invariant_suite" / "report.json"
)
FINITE_ANOMALY_COUNTER_REPORT = (
    D20_INVARIANTS / "theorems" / "finite_anomaly_counter" / "report.json"
)
SECTOR26_ANOMALY_CANCELLATION_REPORT = (
    D20_INVARIANTS / "theorems" / "sector26_anomaly_cancellation" / "report.json"
)
ANOMALY_CANCELLED_FLUX_BALANCE_RECOVERY_REPORT = (
    D20_INVARIANTS / "theorems" / "anomaly_cancelled_flux_balance_recovery" / "report.json"
)
GAMMA8_OBSTRUCTION_CORRECTION_REPORT = (
    D20_INVARIANTS / "theorems" / "gamma8_obstruction_correction" / "report.json"
)
GENERAL_OBSTRUCTION_CORRECTION_SUITE_REPORT = (
    D20_INVARIANTS / "theorems" / "general_obstruction_correction_suite" / "report.json"
)
GLOBAL_COUNTERTERM_LATTICE_REPORT = (
    D20_INVARIANTS / "theorems" / "global_counterterm_lattice" / "report.json"
)
GLOBAL_CORRECTED_CHARGE_MAP_REPORT = (
    D20_INVARIANTS / "theorems" / "global_corrected_charge_map" / "report.json"
)
GLOBAL_CORRECTED_HIDDEN_SPLIT_SYMMETRY_REPORT = (
    D20_INVARIANTS / "theorems" / "global_corrected_hidden_split_symmetry" / "report.json"
)
HIDDEN_SPLIT_AUGMENTED_LEDGER_STABILIZER_REPORT = (
    D20_INVARIANTS / "theorems" / "hidden_split_augmented_ledger_stabilizer" / "report.json"
)
CANONICAL_FLUX_BALANCE_GAUGE_REPORT = (
    D20_INVARIANTS / "theorems" / "canonical_flux_balance_gauge" / "report.json"
)
CANONICAL_LOOP_PI33_OBSTRUCTION_REPORT = (
    D20_INVARIANTS / "theorems" / "canonical_loop_pi33_obstruction" / "report.json"
)
CANONICAL_FINITE_WARD_IDENTITY_REPORT = (
    D20_INVARIANTS / "theorems" / "canonical_finite_ward_identity" / "report.json"
)
CANONICAL_ALL_MASK_WARD_IDENTITY_REPORT = (
    D20_INVARIANTS / "theorems" / "canonical_all_mask_ward_identity" / "report.json"
)
FINITE_BMS_CARROLLIAN_FLUX_BALANCE_REPORT = (
    D20_INVARIANTS / "theorems" / "finite_bms_carrollian_flux_balance" / "report.json"
)
HIDDEN_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT = (
    D20_INVARIANTS / "theorems" / "hidden_packet_charge_frame_classifier" / "report.json"
)
CANONICAL_FINITE_SCATTERING_TABLE_REPORT = (
    D20_INVARIANTS / "theorems" / "canonical_finite_scattering_table" / "report.json"
)
LOOP297_SCATTERING_AMPLITUDE_LIFT_REPORT = (
    D20_INVARIANTS / "theorems" / "loop297_scattering_amplitude_lift" / "report.json"
)
COMPACT_AMPLITUDE_QUOTIENT_REPORT = (
    D20_INVARIANTS / "theorems" / "compact_amplitude_quotient" / "report.json"
)
REDUCED_AMPLITUDE_QUOTIENT_SCATTERING_AUTOMATON_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "reduced_amplitude_quotient_scattering_automaton"
    / "report.json"
)
AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "amplitude_quotient_fourier_mode_classifier"
    / "report.json"
)
FINITE_VIRASORO_STRING_KERNEL_CANDIDATE_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "finite_virasoro_string_kernel_candidate"
    / "report.json"
)
FINITE_VIRASORO_GENERATOR_ALGEBRA_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "finite_virasoro_generator_algebra"
    / "report.json"
)
FINITE_CENTRAL_EXTENSION_ANOMALY_COCYCLE_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "finite_central_extension_anomaly_cocycle"
    / "report.json"
)
FINITE_PARITY_CENTRAL_EXTENSION_GROUP_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "finite_parity_central_extension_group"
    / "report.json"
)
PROJECTIVE_KERNEL_PACKET_TENFOLD_WAY_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "projective_kernel_packet_tenfold_way"
    / "report.json"
)
PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "projective_packet_spectral_charge_table"
    / "report.json"
)
PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "projective_packet_charge_frame_classifier"
    / "report.json"
)
PACKET239_STABILIZER_SEED_CANDIDATE_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "packet239_stabilizer_seed_candidate"
    / "report.json"
)
PACKET239_SEED_PROPAGATION_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "packet239_seed_propagation"
    / "report.json"
)
FULL_EXPOSURE_PACKET_PROPAGATION_CELLS_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_packet_propagation_cells"
    / "report.json"
)
FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_packet_propagation_graph"
    / "report.json"
)
FULL_EXPOSURE_RANK10_TENFOLD_ALIGNMENT_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_rank10_tenfold_alignment"
    / "report.json"
)
FULL_EXPOSURE_RADICAL_GATE_STABILIZER_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_radical_gate_stabilizer"
    / "report.json"
)
FULL_EXPOSURE_RADICAL_GATE_STABILIZER_LIFT_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_radical_gate_stabilizer_lift"
    / "report.json"
)
FULL_EXPOSURE_LABEL_BREAKING_FACTORIZATION_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_label_breaking_factorization"
    / "report.json"
)
FULL_EXPOSURE_CANONICAL_LABELLED_FRAME_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_canonical_labelled_frame"
    / "report.json"
)
FULL_EXPOSURE_LABEL_COORDINATE_TRANSITION_OPERATOR_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_label_coordinate_transition_operator"
    / "report.json"
)
FULL_EXPOSURE_LABEL_COORDINATE_SPECTRAL_BOUNDARY_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_label_coordinate_spectral_boundary"
    / "report.json"
)
FULL_EXPOSURE_LABEL_COORDINATE_GREEN_RESPONSE_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_label_coordinate_green_response"
    / "report.json"
)
FULL_EXPOSURE_ZERO_PAIR_PROPAGATOR_CHARGE_KERNEL_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_propagator_charge_kernel"
    / "report.json"
)
FULL_EXPOSURE_ZERO_PAIR_PROPAGATOR_SYMMETRY_WARD_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_propagator_symmetry_ward"
    / "report.json"
)
FULL_EXPOSURE_ZERO_PAIR_SOURCE_TO_CLOSED_RETURN_COUPLING_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_source_to_closed_return_coupling"
    / "report.json"
)
FULL_EXPOSURE_ZERO_PAIR_WARD_KERNEL_HEIGHT_SELECTOR_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_ward_kernel_height_selector"
    / "report.json"
)
FULL_EXPOSURE_ZERO_PAIR_SELECTED_SOURCED_WARD_BALANCE_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_selected_sourced_ward_balance"
    / "report.json"
)
FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_CONE_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_cone"
    / "report.json"
)
FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_SHORTEST_PATHS_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_shortest_paths"
    / "report.json"
)
FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_TRANSPORT_FAMILIES_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_transport_families"
    / "report.json"
)
FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_LABEL_RELAXED_ORBIT_QUOTIENT_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient"
    / "report.json"
)
FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_ANOMALY_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly"
    / "report.json"
)
FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_TRANSPORT_LEDGER_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_quotient_transport_ledger"
    / "report.json"
)
FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_SCATTERING_OPERATOR_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator"
    / "report.json"
)
FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_MOVE_ORBIT_FAMILY_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_move_orbit_family"
    / "report.json"
)
FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_DYNAMICS_SELECTOR_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_dynamics_selector"
    / "report.json"
)
FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SKELETON_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_skeleton"
    / "report.json"
)
FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_ENUMERATION_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration"
    / "report.json"
)
FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_ENUMERATION_PROPERTIES_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_properties"
    / "report.json"
)
FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_MEMBERSHIP_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_membership"
    / "report.json"
)
FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_SINGLETONS_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_singletons"
    / "report.json"
)
FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LAZY63_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lazy63"
    / "report.json"
)
FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_PAIRED_LAZY480_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_paired_lazy480"
    / "report.json"
)
FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543"
    / "report.json"
)
RAW543_ACTUAL_C2_KERNEL_ORBITS_CSV = PACKAGE_HALLOWEEN_ORBITS_CSV
FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_INDEXED_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_indexed"
    / "report.json"
)
FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_SPLIT_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_split"
    / "report.json"
)
FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_LOOKUP_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_lookup"
    / "report.json"
)
FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LOOKUP_TABLE_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table"
    / "report.json"
)
FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_EMITTER_FACTORIZATION_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_emitter_factorization"
    / "report.json"
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


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def vector_summary(vector: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in vector.items() if key != "entries"}


def csv_header(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(next(csv.reader(f)))


def read_cycle8() -> dict[str, Any]:
    with PRIMITIVE_CYCLES_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if int(row["cycle_id"]) == 8:
                return {
                    "cycle_id": 8,
                    "edge_ids": [int(x) for x in row["edge_ids"].split()],
                    "vertices": [int(x) for x in row["vertices"].split()],
                    "vertex_labels": row["vertex_labels"],
                    "optical_action": int(row["optical_action"]),
                }
    raise ValueError("cycle 8 not found")


def edge_rows(edge_ids: list[int]) -> list[dict[str, Any]]:
    wanted = set(edge_ids)
    rows = []
    with D20_EDGES_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if int(row["edge_id"]) in wanted:
                rows.append(row)
    return sorted(rows, key=lambda row: edge_ids.index(int(row["edge_id"])))


def has_any_key(d: dict[str, Any], keys: set[str]) -> bool:
    stack: list[Any] = [d]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            if any(key in item for key in keys):
                return True
            stack.extend(item.values())
        elif isinstance(item, list):
            stack.extend(item)
    return False


def update_obligation_index(report: dict[str, Any], out_dir: Path) -> None:
    index_path = out_dir.parent / "index.json"
    entry = {
        "id": OBLIGATION_ID,
        "manifest": rel(out_dir / "manifest.json"),
        "report": rel(out_dir / "report.json"),
        "report_sha256": report["certificate_sha256"],
        "status": report["status"],
    }
    if index_path.exists():
        index = json.loads(index_path.read_text(encoding="utf-8"))
        obligations = [item for item in index.get("obligations", []) if item.get("id") != OBLIGATION_ID]
    else:
        obligations = []
    obligations.append(entry)
    obligations = sorted(obligations, key=lambda item: item["id"])
    index = {
        "schema": "d20.proof_obligation_registry.source_drop",
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": obligations,
    }
    index["registry_sha256"] = sha_json({k: v for k, v in index.items() if k != "registry_sha256"})
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report() -> dict[str, Any]:
    attachment = load_json(SECTOR_ATTACHMENT_REPORT)
    tube_section = load_json(TUBE_PROJECTION_SECTION)
    full_lift = load_json(FULL_A985_LIFT)
    wedderburn = load_json(WEDDERBURN_TRACE)
    boundary_to_loop = load_json(BOUNDARY_TO_LOOP_REPORT) if BOUNDARY_TO_LOOP_REPORT.exists() else {}
    annihilation = load_json(BOUNDARY_ANNIHILATION_REPORT) if BOUNDARY_ANNIHILATION_REPORT.exists() else {}
    height_transport = load_json(HEIGHT_TRANSPORT_REPORT) if HEIGHT_TRANSPORT_REPORT.exists() else {}
    all_residue_transport = (
        load_json(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT)
        if ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT.exists()
        else {}
    )
    unique_public_zero_support = (
        load_json(UNIQUE_PUBLIC_ZERO_SUPPORT_REPORT)
        if UNIQUE_PUBLIC_ZERO_SUPPORT_REPORT.exists()
        else {}
    )
    sector_public_shadow_kernel = (
        load_json(SECTOR_PUBLIC_SHADOW_KERNEL_REPORT)
        if SECTOR_PUBLIC_SHADOW_KERNEL_REPORT.exists()
        else {}
    )
    sector_idempotent_support_admissibility = (
        load_json(SECTOR_IDEMPOTENT_SUPPORT_ADMISSIBILITY_REPORT)
        if SECTOR_IDEMPOTENT_SUPPORT_ADMISSIBILITY_REPORT.exists()
        else {}
    )
    minimal_composite_transport = (
        load_json(MINIMAL_COMPOSITE_TRANSPORT_REPORT)
        if MINIMAL_COMPOSITE_TRANSPORT_REPORT.exists()
        else {}
    )
    superselection_flux_extension = (
        load_json(SUPERSELECTION_FLUX_EXTENSION_REPORT)
        if SUPERSELECTION_FLUX_EXTENSION_REPORT.exists()
        else {}
    )
    typed_nonexact_optical_flux = (
        load_json(TYPED_NONEXACT_OPTICAL_FLUX_REPORT)
        if TYPED_NONEXACT_OPTICAL_FLUX_REPORT.exists()
        else {}
    )
    sector26_invariant_suite = (
        load_json(SECTOR26_INVARIANT_SUITE_REPORT)
        if SECTOR26_INVARIANT_SUITE_REPORT.exists()
        else {}
    )
    finite_anomaly_counter = (
        load_json(FINITE_ANOMALY_COUNTER_REPORT)
        if FINITE_ANOMALY_COUNTER_REPORT.exists()
        else {}
    )
    sector26_anomaly_cancellation = (
        load_json(SECTOR26_ANOMALY_CANCELLATION_REPORT)
        if SECTOR26_ANOMALY_CANCELLATION_REPORT.exists()
        else {}
    )
    anomaly_cancelled_flux_balance_recovery = (
        load_json(ANOMALY_CANCELLED_FLUX_BALANCE_RECOVERY_REPORT)
        if ANOMALY_CANCELLED_FLUX_BALANCE_RECOVERY_REPORT.exists()
        else {}
    )
    gamma8_obstruction_correction = (
        load_json(GAMMA8_OBSTRUCTION_CORRECTION_REPORT)
        if GAMMA8_OBSTRUCTION_CORRECTION_REPORT.exists()
        else {}
    )
    general_obstruction_correction_suite = (
        load_json(GENERAL_OBSTRUCTION_CORRECTION_SUITE_REPORT)
        if GENERAL_OBSTRUCTION_CORRECTION_SUITE_REPORT.exists()
        else {}
    )
    global_counterterm_lattice = (
        load_json(GLOBAL_COUNTERTERM_LATTICE_REPORT)
        if GLOBAL_COUNTERTERM_LATTICE_REPORT.exists()
        else {}
    )
    global_corrected_charge_map = (
        load_json(GLOBAL_CORRECTED_CHARGE_MAP_REPORT)
        if GLOBAL_CORRECTED_CHARGE_MAP_REPORT.exists()
        else {}
    )
    global_corrected_hidden_split_symmetry = (
        load_json(GLOBAL_CORRECTED_HIDDEN_SPLIT_SYMMETRY_REPORT)
        if GLOBAL_CORRECTED_HIDDEN_SPLIT_SYMMETRY_REPORT.exists()
        else {}
    )
    hidden_split_augmented_ledger_stabilizer = (
        load_json(HIDDEN_SPLIT_AUGMENTED_LEDGER_STABILIZER_REPORT)
        if HIDDEN_SPLIT_AUGMENTED_LEDGER_STABILIZER_REPORT.exists()
        else {}
    )
    canonical_flux_balance_gauge = (
        load_json(CANONICAL_FLUX_BALANCE_GAUGE_REPORT)
        if CANONICAL_FLUX_BALANCE_GAUGE_REPORT.exists()
        else {}
    )
    canonical_loop_pi33_obstruction = (
        load_json(CANONICAL_LOOP_PI33_OBSTRUCTION_REPORT)
        if CANONICAL_LOOP_PI33_OBSTRUCTION_REPORT.exists()
        else {}
    )
    canonical_finite_ward_identity = (
        load_json(CANONICAL_FINITE_WARD_IDENTITY_REPORT)
        if CANONICAL_FINITE_WARD_IDENTITY_REPORT.exists()
        else {}
    )
    canonical_all_mask_ward_identity = (
        load_json(CANONICAL_ALL_MASK_WARD_IDENTITY_REPORT)
        if CANONICAL_ALL_MASK_WARD_IDENTITY_REPORT.exists()
        else {}
    )
    finite_bms_carrollian_flux_balance = (
        load_json(FINITE_BMS_CARROLLIAN_FLUX_BALANCE_REPORT)
        if FINITE_BMS_CARROLLIAN_FLUX_BALANCE_REPORT.exists()
        else {}
    )
    hidden_packet_charge_frame_classifier = (
        load_json(HIDDEN_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT)
        if HIDDEN_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT.exists()
        else {}
    )
    canonical_finite_scattering_table = (
        load_json(CANONICAL_FINITE_SCATTERING_TABLE_REPORT)
        if CANONICAL_FINITE_SCATTERING_TABLE_REPORT.exists()
        else {}
    )
    loop297_scattering_amplitude_lift = (
        load_json(LOOP297_SCATTERING_AMPLITUDE_LIFT_REPORT)
        if LOOP297_SCATTERING_AMPLITUDE_LIFT_REPORT.exists()
        else {}
    )
    compact_amplitude_quotient = (
        load_json(COMPACT_AMPLITUDE_QUOTIENT_REPORT)
        if COMPACT_AMPLITUDE_QUOTIENT_REPORT.exists()
        else {}
    )
    reduced_amplitude_quotient_scattering_automaton = (
        load_json(REDUCED_AMPLITUDE_QUOTIENT_SCATTERING_AUTOMATON_REPORT)
        if REDUCED_AMPLITUDE_QUOTIENT_SCATTERING_AUTOMATON_REPORT.exists()
        else {}
    )
    amplitude_quotient_fourier_mode_classifier = (
        load_json(AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER_REPORT)
        if AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER_REPORT.exists()
        else {}
    )
    finite_virasoro_string_kernel_candidate = (
        load_json(FINITE_VIRASORO_STRING_KERNEL_CANDIDATE_REPORT)
        if FINITE_VIRASORO_STRING_KERNEL_CANDIDATE_REPORT.exists()
        else {}
    )
    finite_virasoro_generator_algebra = (
        load_json(FINITE_VIRASORO_GENERATOR_ALGEBRA_REPORT)
        if FINITE_VIRASORO_GENERATOR_ALGEBRA_REPORT.exists()
        else {}
    )
    finite_central_extension_anomaly_cocycle = (
        load_json(FINITE_CENTRAL_EXTENSION_ANOMALY_COCYCLE_REPORT)
        if FINITE_CENTRAL_EXTENSION_ANOMALY_COCYCLE_REPORT.exists()
        else {}
    )
    finite_parity_central_extension_group = (
        load_json(FINITE_PARITY_CENTRAL_EXTENSION_GROUP_REPORT)
        if FINITE_PARITY_CENTRAL_EXTENSION_GROUP_REPORT.exists()
        else {}
    )
    projective_kernel_packet_tenfold_way = (
        load_json(PROJECTIVE_KERNEL_PACKET_TENFOLD_WAY_REPORT)
        if PROJECTIVE_KERNEL_PACKET_TENFOLD_WAY_REPORT.exists()
        else {}
    )
    projective_packet_spectral_charge_table = (
        load_json(PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_REPORT)
        if PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_REPORT.exists()
        else {}
    )
    projective_packet_charge_frame_classifier = (
        load_json(PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT)
        if PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT.exists()
        else {}
    )
    packet239_stabilizer_seed_candidate = (
        load_json(PACKET239_STABILIZER_SEED_CANDIDATE_REPORT)
        if PACKET239_STABILIZER_SEED_CANDIDATE_REPORT.exists()
        else {}
    )
    packet239_seed_propagation = (
        load_json(PACKET239_SEED_PROPAGATION_REPORT)
        if PACKET239_SEED_PROPAGATION_REPORT.exists()
        else {}
    )
    full_exposure_packet_propagation_cells = (
        load_json(FULL_EXPOSURE_PACKET_PROPAGATION_CELLS_REPORT)
        if FULL_EXPOSURE_PACKET_PROPAGATION_CELLS_REPORT.exists()
        else {}
    )
    full_exposure_packet_propagation_graph = (
        load_json(FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_REPORT)
        if FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_REPORT.exists()
        else {}
    )
    full_exposure_rank10_tenfold_alignment = (
        load_json(FULL_EXPOSURE_RANK10_TENFOLD_ALIGNMENT_REPORT)
        if FULL_EXPOSURE_RANK10_TENFOLD_ALIGNMENT_REPORT.exists()
        else {}
    )
    full_exposure_radical_gate_stabilizer = (
        load_json(FULL_EXPOSURE_RADICAL_GATE_STABILIZER_REPORT)
        if FULL_EXPOSURE_RADICAL_GATE_STABILIZER_REPORT.exists()
        else {}
    )
    full_exposure_radical_gate_stabilizer_lift = (
        load_json(FULL_EXPOSURE_RADICAL_GATE_STABILIZER_LIFT_REPORT)
        if FULL_EXPOSURE_RADICAL_GATE_STABILIZER_LIFT_REPORT.exists()
        else {}
    )
    full_exposure_label_breaking_factorization = (
        load_json(FULL_EXPOSURE_LABEL_BREAKING_FACTORIZATION_REPORT)
        if FULL_EXPOSURE_LABEL_BREAKING_FACTORIZATION_REPORT.exists()
        else {}
    )
    full_exposure_canonical_labelled_frame = (
        load_json(FULL_EXPOSURE_CANONICAL_LABELLED_FRAME_REPORT)
        if FULL_EXPOSURE_CANONICAL_LABELLED_FRAME_REPORT.exists()
        else {}
    )
    full_exposure_label_coordinate_transition_operator = (
        load_json(FULL_EXPOSURE_LABEL_COORDINATE_TRANSITION_OPERATOR_REPORT)
        if FULL_EXPOSURE_LABEL_COORDINATE_TRANSITION_OPERATOR_REPORT.exists()
        else {}
    )
    full_exposure_label_coordinate_spectral_boundary = (
        load_json(FULL_EXPOSURE_LABEL_COORDINATE_SPECTRAL_BOUNDARY_REPORT)
        if FULL_EXPOSURE_LABEL_COORDINATE_SPECTRAL_BOUNDARY_REPORT.exists()
        else {}
    )
    full_exposure_label_coordinate_green_response = (
        load_json(FULL_EXPOSURE_LABEL_COORDINATE_GREEN_RESPONSE_REPORT)
        if FULL_EXPOSURE_LABEL_COORDINATE_GREEN_RESPONSE_REPORT.exists()
        else {}
    )
    full_exposure_zero_pair_propagator_charge_kernel = (
        load_json(FULL_EXPOSURE_ZERO_PAIR_PROPAGATOR_CHARGE_KERNEL_REPORT)
        if FULL_EXPOSURE_ZERO_PAIR_PROPAGATOR_CHARGE_KERNEL_REPORT.exists()
        else {}
    )
    full_exposure_zero_pair_propagator_symmetry_ward = (
        load_json(FULL_EXPOSURE_ZERO_PAIR_PROPAGATOR_SYMMETRY_WARD_REPORT)
        if FULL_EXPOSURE_ZERO_PAIR_PROPAGATOR_SYMMETRY_WARD_REPORT.exists()
        else {}
    )
    full_exposure_zero_pair_source_to_closed_return_coupling = (
        load_json(FULL_EXPOSURE_ZERO_PAIR_SOURCE_TO_CLOSED_RETURN_COUPLING_REPORT)
        if FULL_EXPOSURE_ZERO_PAIR_SOURCE_TO_CLOSED_RETURN_COUPLING_REPORT.exists()
        else {}
    )
    full_exposure_zero_pair_ward_kernel_height_selector = (
        load_json(FULL_EXPOSURE_ZERO_PAIR_WARD_KERNEL_HEIGHT_SELECTOR_REPORT)
        if FULL_EXPOSURE_ZERO_PAIR_WARD_KERNEL_HEIGHT_SELECTOR_REPORT.exists()
        else {}
    )
    full_exposure_zero_pair_selected_sourced_ward_balance = (
        load_json(FULL_EXPOSURE_ZERO_PAIR_SELECTED_SOURCED_WARD_BALANCE_REPORT)
        if FULL_EXPOSURE_ZERO_PAIR_SELECTED_SOURCED_WARD_BALANCE_REPORT.exists()
        else {}
    )
    full_exposure_zero_pair_sourced_balance_cone = (
        load_json(FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_CONE_REPORT)
        if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_CONE_REPORT.exists()
        else {}
    )
    full_exposure_zero_pair_sourced_balance_shortest_paths = (
        load_json(FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_SHORTEST_PATHS_REPORT)
        if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_SHORTEST_PATHS_REPORT.exists()
        else {}
    )
    full_exposure_zero_pair_sourced_balance_transport_families = (
        load_json(FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_TRANSPORT_FAMILIES_REPORT)
        if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_TRANSPORT_FAMILIES_REPORT.exists()
        else {}
    )
    full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient = (
        load_json(FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_LABEL_RELAXED_ORBIT_QUOTIENT_REPORT)
        if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_LABEL_RELAXED_ORBIT_QUOTIENT_REPORT.exists()
        else {}
    )
    full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly = (
        load_json(FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_ANOMALY_REPORT)
        if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_ANOMALY_REPORT.exists()
        else {}
    )
    full_exposure_zero_pair_sourced_balance_c2_quotient_transport_ledger = (
        load_json(FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_TRANSPORT_LEDGER_REPORT)
        if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_TRANSPORT_LEDGER_REPORT.exists()
        else {}
    )
    full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator = (
        load_json(FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_SCATTERING_OPERATOR_REPORT)
        if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_SCATTERING_OPERATOR_REPORT.exists()
        else {}
    )
    full_exposure_zero_pair_sourced_balance_c2_move_orbit_family = (
        load_json(FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_MOVE_ORBIT_FAMILY_REPORT)
        if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_MOVE_ORBIT_FAMILY_REPORT.exists()
        else {}
    )
    full_exposure_zero_pair_sourced_balance_c2_dynamics_selector = (
        load_json(FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_DYNAMICS_SELECTOR_REPORT)
        if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_DYNAMICS_SELECTOR_REPORT.exists()
        else {}
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_skeleton = (
        load_json(
            FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SKELETON_REPORT
        )
        if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SKELETON_REPORT.exists()
        else {}
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration = (
        load_json(
            FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_ENUMERATION_REPORT
        )
        if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_ENUMERATION_REPORT.exists()
        else {}
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_properties = (
        load_json(
            FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_ENUMERATION_PROPERTIES_REPORT
        )
        if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_ENUMERATION_PROPERTIES_REPORT.exists()
        else {}
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_membership = (
        load_json(
            FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_MEMBERSHIP_REPORT
        )
        if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_MEMBERSHIP_REPORT.exists()
        else {}
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_singletons = (
        load_json(
            FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_SINGLETONS_REPORT
        )
        if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_SINGLETONS_REPORT.exists()
        else {}
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lazy63 = (
        load_json(
            FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LAZY63_REPORT
        )
        if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LAZY63_REPORT.exists()
        else {}
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_paired_lazy480 = (
        load_json(
            FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_PAIRED_LAZY480_REPORT
        )
        if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_PAIRED_LAZY480_REPORT.exists()
        else {}
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543 = (
        load_json(
            FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_REPORT
        )
        if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_REPORT.exists()
        else {}
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_indexed = (
        load_json(
            FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_INDEXED_REPORT
        )
        if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_INDEXED_REPORT.exists()
        else {}
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_split = (
        load_json(
            FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_SPLIT_REPORT
        )
        if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_SPLIT_REPORT.exists()
        else {}
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_lookup = (
        load_json(
            FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_LOOKUP_REPORT
        )
        if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_LOOKUP_REPORT.exists()
        else {}
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table = (
        load_json(
            FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LOOKUP_TABLE_REPORT
        )
        if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LOOKUP_TABLE_REPORT.exists()
        else {}
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_emitter_factorization = (
        load_json(
            FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_EMITTER_FACTORIZATION_REPORT
        )
        if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_EMITTER_FACTORIZATION_REPORT.exists()
        else {}
    )

    cycle = read_cycle8()
    cycle_edges = edge_rows(cycle["edge_ids"])
    edge_header = csv_header(D20_EDGES_CSV)
    cycle_header = csv_header(PRIMITIVE_CYCLES_CSV)

    lift_field_tokens = ("loop", "relation", "a985", "tube", "pi33", "sector", "projection")
    edge_lift_columns = [name for name in edge_header if any(token in name.lower() for token in lift_field_tokens)]
    cycle_lift_columns = [name for name in cycle_header if any(token in name.lower() for token in lift_field_tokens)]

    character = full_lift.get("irreducible_character_table", {})
    idempotent_validation = full_lift.get("full_A985_idempotent_validation", {})
    wedderburn_source = wedderburn.get("idempotent_source", {})
    section = tube_section.get("section", {})
    boundary_cycle8 = boundary_to_loop.get("derived", {}).get("cycle8_lift", {})
    boundary_cycle8_vector = boundary_cycle8.get("vector", {})
    boundary_cycle8_cycle = boundary_cycle8.get("cycle", {})
    boundary_cycle8_object_summary = boundary_cycle8.get("object_summary", {})
    annihilation_cycle8 = annihilation.get("derived", {}).get("cycle8", {}).get("variants", {})
    annihilation_e33 = annihilation.get("derived", {}).get("sector33_tube_idempotent", {})
    height_transport_derived = height_transport.get("derived", {})
    height_transport_character = height_transport_derived.get("pi33_tube_character", {})
    all_residue_derived = all_residue_transport.get("derived", {})
    unique_public_zero_derived = unique_public_zero_support.get("derived", {})
    public_shadow_kernel_derived = sector_public_shadow_kernel.get("derived", {})
    idempotent_admissibility_derived = sector_idempotent_support_admissibility.get("derived", {})
    minimal_composite_transport_derived = minimal_composite_transport.get("derived", {})
    superselection_flux_extension_derived = superselection_flux_extension.get("derived", {})
    typed_nonexact_optical_flux_derived = typed_nonexact_optical_flux.get("derived", {})
    sector26_invariant_suite_derived = sector26_invariant_suite.get("derived", {})
    finite_anomaly_counter_derived = finite_anomaly_counter.get("derived", {})
    sector26_anomaly_cancellation_derived = sector26_anomaly_cancellation.get("derived", {})
    anomaly_cancelled_flux_balance_recovery_derived = anomaly_cancelled_flux_balance_recovery.get(
        "derived", {}
    )
    gamma8_obstruction_correction_derived = gamma8_obstruction_correction.get("derived", {})
    general_obstruction_correction_suite_derived = general_obstruction_correction_suite.get(
        "derived", {}
    )
    global_counterterm_lattice_derived = global_counterterm_lattice.get("derived", {})
    global_corrected_charge_map_derived = global_corrected_charge_map.get("derived", {})
    global_corrected_hidden_split_symmetry_derived = global_corrected_hidden_split_symmetry.get(
        "derived", {}
    )
    hidden_split_augmented_ledger_stabilizer_derived = hidden_split_augmented_ledger_stabilizer.get(
        "derived", {}
    )
    canonical_flux_balance_gauge_derived = canonical_flux_balance_gauge.get("derived", {})
    canonical_loop_pi33_obstruction_derived = canonical_loop_pi33_obstruction.get("derived", {})
    canonical_finite_ward_identity_derived = canonical_finite_ward_identity.get("derived", {})
    canonical_all_mask_ward_identity_derived = canonical_all_mask_ward_identity.get("derived", {})
    finite_bms_carrollian_flux_balance_derived = finite_bms_carrollian_flux_balance.get(
        "derived", {}
    )
    hidden_packet_charge_frame_classifier_derived = hidden_packet_charge_frame_classifier.get(
        "derived", {}
    )
    canonical_finite_scattering_table_derived = canonical_finite_scattering_table.get(
        "derived", {}
    )
    loop297_scattering_amplitude_lift_derived = loop297_scattering_amplitude_lift.get(
        "derived", {}
    )
    compact_amplitude_quotient_derived = compact_amplitude_quotient.get("derived", {})
    reduced_amplitude_quotient_scattering_automaton_derived = (
        reduced_amplitude_quotient_scattering_automaton.get("derived", {})
    )
    amplitude_quotient_fourier_mode_classifier_derived = (
        amplitude_quotient_fourier_mode_classifier.get("derived", {})
    )
    finite_virasoro_string_kernel_candidate_derived = (
        finite_virasoro_string_kernel_candidate.get("derived", {})
    )
    finite_virasoro_generator_algebra_derived = (
        finite_virasoro_generator_algebra.get("derived", {})
    )
    finite_central_extension_anomaly_cocycle_derived = (
        finite_central_extension_anomaly_cocycle.get("derived", {})
    )
    finite_parity_central_extension_group_derived = (
        finite_parity_central_extension_group.get("derived", {})
    )
    projective_kernel_packet_tenfold_way_derived = (
        projective_kernel_packet_tenfold_way.get("derived", {})
    )
    projective_packet_spectral_charge_table_derived = (
        projective_packet_spectral_charge_table.get("derived", {})
    )
    projective_packet_charge_frame_classifier_derived = (
        projective_packet_charge_frame_classifier.get("derived", {})
    )
    packet239_stabilizer_seed_candidate_derived = (
        packet239_stabilizer_seed_candidate.get("derived", {})
    )
    packet239_seed_propagation_derived = packet239_seed_propagation.get("derived", {})
    full_exposure_packet_propagation_cells_derived = (
        full_exposure_packet_propagation_cells.get("derived", {})
    )
    full_exposure_packet_propagation_graph_derived = (
        full_exposure_packet_propagation_graph.get("derived", {})
    )
    full_exposure_rank10_tenfold_alignment_derived = (
        full_exposure_rank10_tenfold_alignment.get("derived", {})
    )
    full_exposure_radical_gate_stabilizer_derived = (
        full_exposure_radical_gate_stabilizer.get("derived", {})
    )
    full_exposure_radical_gate_stabilizer_lift_derived = (
        full_exposure_radical_gate_stabilizer_lift.get("derived", {})
    )
    full_exposure_label_breaking_factorization_derived = (
        full_exposure_label_breaking_factorization.get("derived", {})
    )
    full_exposure_canonical_labelled_frame_derived = (
        full_exposure_canonical_labelled_frame.get("derived", {})
    )
    full_exposure_label_coordinate_transition_operator_derived = (
        full_exposure_label_coordinate_transition_operator.get("derived", {})
    )
    full_exposure_label_coordinate_spectral_boundary_derived = (
        full_exposure_label_coordinate_spectral_boundary.get("derived", {})
    )
    full_exposure_label_coordinate_green_response_derived = (
        full_exposure_label_coordinate_green_response.get("derived", {})
    )
    full_exposure_zero_pair_propagator_charge_kernel_derived = (
        full_exposure_zero_pair_propagator_charge_kernel.get("derived", {})
    )
    full_exposure_zero_pair_propagator_symmetry_ward_derived = (
        full_exposure_zero_pair_propagator_symmetry_ward.get("derived", {})
    )
    full_exposure_zero_pair_source_to_closed_return_coupling_derived = (
        full_exposure_zero_pair_source_to_closed_return_coupling.get("derived", {})
    )
    full_exposure_zero_pair_ward_kernel_height_selector_derived = (
        full_exposure_zero_pair_ward_kernel_height_selector.get("derived", {})
    )
    full_exposure_zero_pair_selected_sourced_ward_balance_derived = (
        full_exposure_zero_pair_selected_sourced_ward_balance.get("derived", {})
    )
    full_exposure_zero_pair_sourced_balance_cone_derived = (
        full_exposure_zero_pair_sourced_balance_cone.get("derived", {})
    )
    full_exposure_zero_pair_sourced_balance_shortest_paths_derived = (
        full_exposure_zero_pair_sourced_balance_shortest_paths.get("derived", {})
    )
    full_exposure_zero_pair_sourced_balance_transport_families_derived = (
        full_exposure_zero_pair_sourced_balance_transport_families.get("derived", {})
    )
    full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient_derived = (
        full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient.get("derived", {})
    )
    full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly_derived = (
        full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly.get("derived", {})
    )
    full_exposure_zero_pair_sourced_balance_c2_quotient_transport_ledger_derived = (
        full_exposure_zero_pair_sourced_balance_c2_quotient_transport_ledger.get("derived", {})
    )
    full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator_derived = (
        full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator.get(
            "derived", {}
        )
    )
    full_exposure_zero_pair_sourced_balance_c2_move_orbit_family_derived = (
        full_exposure_zero_pair_sourced_balance_c2_move_orbit_family.get("derived", {})
    )
    full_exposure_zero_pair_sourced_balance_c2_dynamics_selector_derived = (
        full_exposure_zero_pair_sourced_balance_c2_dynamics_selector.get("derived", {})
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_skeleton_derived = (
        full_exposure_zero_pair_sourced_balance_c2_cubical_agda_skeleton.get(
            "derived", {}
        )
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_derived = (
        full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration.get(
            "derived", {}
        )
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_properties_derived = (
        full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_properties.get(
            "derived", {}
        )
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_membership_derived = (
        full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_membership.get(
            "derived", {}
        )
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_singletons_derived = (
        full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_singletons.get(
            "derived", {}
        )
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lazy63_derived = (
        full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lazy63.get(
            "derived", {}
        )
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_paired_lazy480_derived = (
        full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_paired_lazy480.get(
            "derived", {}
        )
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_derived = (
        full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543.get(
            "derived", {}
        )
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_indexed_derived = (
        full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_indexed.get(
            "derived", {}
        )
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_split_derived = (
        full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_split.get(
            "derived", {}
        )
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_lookup_derived = (
        full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_lookup.get(
            "derived", {}
        )
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table_derived = (
        full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table.get(
            "derived", {}
        )
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_emitter_factorization_derived = (
        full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_emitter_factorization.get(
            "derived", {}
        )
    )

    character_values_materialized = has_any_key(
        character,
        {"values", "matrix", "rows", "table", "character_table", "central_character_matrix"},
    )
    idempotent_matrix_materialized = has_any_key(
        idempotent_validation,
        {"values", "matrix", "rows", "embedded_idempotent_matrix", "idempotents"},
    ) or has_any_key(
        wedderburn_source,
        {"values", "matrix", "rows", "embedded_idempotent_matrix", "idempotents"},
    )
    complete_section_materialized = has_any_key(
        section,
        {"entries", "section_entries", "matrix", "coefficients", "complete_section"},
    )

    boundary_lift_map_present = (
        boundary_to_loop.get("status") == "D20_BOUNDARY_TO_LOOP_MAP_CERTIFIED"
        and boundary_to_loop.get("all_checks_pass") is True
    )
    pi33_tube_functional_materialized = (
        annihilation.get("status") == "D20_SECTOR33_BOUNDARY_TO_LOOP_ANNIHILATION_CERTIFIED"
        and annihilation.get("all_checks_pass") is True
    )
    bare_lambda_coefficient_is_zero = (
        pi33_tube_functional_materialized
        and annihilation_cycle8.get("unweighted", {})
        .get("pi33_tube_character", {})
        .get("coefficient_mod_prime")
        == 0
    )
    height_coherent_transport_certified = (
        height_transport.get("status") == "D20_SECTOR33_HEIGHT_COHERENT_TRANSPORT_CERTIFIED"
        and height_transport.get("all_checks_pass") is True
    )
    all_residue_transport_certified = (
        all_residue_transport.get("status") == "D20_ALL_RESIDUE_HEIGHT_COHERENT_TRANSPORT_CERTIFIED"
        and all_residue_transport.get("all_checks_pass") is True
    )
    unique_public_zero_support_certified = (
        unique_public_zero_support.get("status")
        == "D20_SECTOR33_UNIQUE_PUBLIC_ZERO_SUPPORT_CERTIFIED"
        and unique_public_zero_support.get("all_checks_pass") is True
    )
    sector_public_shadow_kernel_certified = (
        sector_public_shadow_kernel.get("status") == "D20_SECTOR_PUBLIC_SHADOW_KERNEL_CERTIFIED"
        and sector_public_shadow_kernel.get("all_checks_pass") is True
    )
    sector_idempotent_support_admissibility_certified = (
        sector_idempotent_support_admissibility.get("status")
        == "D20_SECTOR_IDEMPOTENT_SUPPORT_ADMISSIBILITY_CLASSIFIED"
        and sector_idempotent_support_admissibility.get("all_checks_pass") is True
    )
    minimal_composite_transport_certified = (
        minimal_composite_transport.get("status")
        == "D20_MINIMAL_COMPOSITE_NULL_SUPPORTS_TRANSPORT_CLASSIFIED"
        and minimal_composite_transport.get("all_checks_pass") is True
    )
    superselection_flux_extension_certified = (
        superselection_flux_extension.get("status")
        == "D20_SUPERSELECTION_FLUX_BALANCE_EXTENSION_CERTIFIED"
        and superselection_flux_extension.get("all_checks_pass") is True
    )
    typed_nonexact_optical_flux_certified = (
        typed_nonexact_optical_flux.get("status")
        == "D20_TYPED_NONEXACT_OPTICAL_FLUX_UPDATE_CERTIFIED"
        and typed_nonexact_optical_flux.get("all_checks_pass") is True
    )
    sector26_invariant_suite_certified = (
        sector26_invariant_suite.get("status")
        == "D20_SECTOR26_INVARIANT_SUITE_CERTIFIED"
        and sector26_invariant_suite.get("all_checks_pass") is True
    )
    finite_anomaly_counter_certified = (
        finite_anomaly_counter.get("status") == "D20_FINITE_ANOMALY_COUNTER_CERTIFIED"
        and finite_anomaly_counter.get("all_checks_pass") is True
    )
    sector26_anomaly_cancellation_certified = (
        sector26_anomaly_cancellation.get("status")
        == "D20_SECTOR26_ANOMALY_CANCELLATION_CERTIFIED"
        and sector26_anomaly_cancellation.get("all_checks_pass") is True
    )
    anomaly_cancelled_flux_balance_recovery_certified = (
        anomaly_cancelled_flux_balance_recovery.get("status")
        == "D20_ANOMALY_CANCELLED_FLUX_BALANCE_RECOVERY_CERTIFIED"
        and anomaly_cancelled_flux_balance_recovery.get("all_checks_pass") is True
    )
    gamma8_obstruction_correction_certified = (
        gamma8_obstruction_correction.get("status")
        == "D20_GAMMA8_OBSTRUCTION_CORRECTION_CERTIFIED"
        and gamma8_obstruction_correction.get("all_checks_pass") is True
    )
    general_obstruction_correction_suite_certified = (
        general_obstruction_correction_suite.get("status")
        == "D20_GENERAL_OBSTRUCTION_CORRECTION_SUITE_CERTIFIED"
        and general_obstruction_correction_suite.get("all_checks_pass") is True
    )
    global_counterterm_lattice_certified = (
        global_counterterm_lattice.get("status") == "D20_GLOBAL_COUNTERTERM_LATTICE_CERTIFIED"
        and global_counterterm_lattice.get("all_checks_pass") is True
    )
    global_corrected_charge_map_certified = (
        global_corrected_charge_map.get("status") == "D20_GLOBAL_CORRECTED_CHARGE_MAP_CERTIFIED"
        and global_corrected_charge_map.get("all_checks_pass") is True
    )
    global_corrected_hidden_split_symmetry_certified = (
        global_corrected_hidden_split_symmetry.get("status")
        == "D20_GLOBAL_CORRECTED_HIDDEN_SPLIT_SYMMETRY_CERTIFIED"
        and global_corrected_hidden_split_symmetry.get("all_checks_pass") is True
    )
    hidden_split_augmented_ledger_stabilizer_certified = (
        hidden_split_augmented_ledger_stabilizer.get("status")
        == "D20_HIDDEN_SPLIT_AUGMENTED_LEDGER_STABILIZER_CERTIFIED"
        and hidden_split_augmented_ledger_stabilizer.get("all_checks_pass") is True
    )
    canonical_flux_balance_gauge_certified = (
        canonical_flux_balance_gauge.get("status") == "D20_CANONICAL_FLUX_BALANCE_GAUGE_CERTIFIED"
        and canonical_flux_balance_gauge.get("all_checks_pass") is True
    )
    canonical_loop_pi33_obstruction_certified = (
        canonical_loop_pi33_obstruction.get("status")
        == "D20_CANONICAL_LOOP_PI33_OBSTRUCTION_CERTIFIED"
        and canonical_loop_pi33_obstruction.get("all_checks_pass") is True
    )
    canonical_finite_ward_identity_certified = (
        canonical_finite_ward_identity.get("status")
        == "D20_CANONICAL_FINITE_WARD_IDENTITY_CERTIFIED"
        and canonical_finite_ward_identity.get("all_checks_pass") is True
    )
    canonical_all_mask_ward_identity_certified = (
        canonical_all_mask_ward_identity.get("status")
        == "D20_CANONICAL_ALL_MASK_WARD_IDENTITY_CERTIFIED"
        and canonical_all_mask_ward_identity.get("all_checks_pass") is True
    )
    finite_bms_carrollian_flux_balance_certified = (
        finite_bms_carrollian_flux_balance.get("status")
        == "D20_FINITE_BMS_CARROLLIAN_FLUX_BALANCE_CERTIFIED"
        and finite_bms_carrollian_flux_balance.get("all_checks_pass") is True
    )
    hidden_packet_charge_frame_classifier_certified = (
        hidden_packet_charge_frame_classifier.get("status")
        == "D20_HIDDEN_PACKET_CHARGE_FRAME_CLASSIFIER_CERTIFIED"
        and hidden_packet_charge_frame_classifier.get("all_checks_pass") is True
    )
    canonical_finite_scattering_table_certified = (
        canonical_finite_scattering_table.get("status")
        == "D20_CANONICAL_FINITE_SCATTERING_TABLE_CERTIFIED"
        and canonical_finite_scattering_table.get("all_checks_pass") is True
    )
    loop297_scattering_amplitude_lift_certified = (
        loop297_scattering_amplitude_lift.get("status")
        == "D20_LOOP297_SCATTERING_AMPLITUDE_LIFT_CERTIFIED"
        and loop297_scattering_amplitude_lift.get("all_checks_pass") is True
    )
    compact_amplitude_quotient_certified = (
        compact_amplitude_quotient.get("status")
        == "D20_COMPACT_AMPLITUDE_QUOTIENT_CERTIFIED"
        and compact_amplitude_quotient.get("all_checks_pass") is True
    )
    reduced_amplitude_quotient_scattering_automaton_certified = (
        reduced_amplitude_quotient_scattering_automaton.get("status")
        == "D20_REDUCED_AMPLITUDE_QUOTIENT_SCATTERING_AUTOMATON_CERTIFIED"
        and reduced_amplitude_quotient_scattering_automaton.get("all_checks_pass") is True
    )
    amplitude_quotient_fourier_mode_classifier_certified = (
        amplitude_quotient_fourier_mode_classifier.get("status")
        == "D20_AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER_CERTIFIED"
        and amplitude_quotient_fourier_mode_classifier.get("all_checks_pass") is True
    )
    finite_virasoro_string_kernel_candidate_certified = (
        finite_virasoro_string_kernel_candidate.get("status")
        == "D20_FINITE_VIRASORO_STRING_KERNEL_CANDIDATE_CERTIFIED"
        and finite_virasoro_string_kernel_candidate.get("all_checks_pass") is True
    )
    finite_virasoro_generator_algebra_certified = (
        finite_virasoro_generator_algebra.get("status")
        == "D20_FINITE_VIRASORO_GENERATOR_ALGEBRA_CERTIFIED"
        and finite_virasoro_generator_algebra.get("all_checks_pass") is True
    )
    finite_central_extension_anomaly_cocycle_certified = (
        finite_central_extension_anomaly_cocycle.get("status")
        == "D20_FINITE_CENTRAL_EXTENSION_ANOMALY_COCYCLE_CERTIFIED"
        and finite_central_extension_anomaly_cocycle.get("all_checks_pass") is True
    )
    finite_parity_central_extension_group_certified = (
        finite_parity_central_extension_group.get("status")
        == "D20_FINITE_PARITY_CENTRAL_EXTENSION_GROUP_CERTIFIED"
        and finite_parity_central_extension_group.get("all_checks_pass") is True
    )
    projective_kernel_packet_tenfold_way_certified = (
        projective_kernel_packet_tenfold_way.get("status")
        == "D20_PROJECTIVE_KERNEL_PACKET_TENFOLD_WAY_CERTIFIED"
        and projective_kernel_packet_tenfold_way.get("all_checks_pass") is True
    )
    projective_packet_spectral_charge_table_certified = (
        projective_packet_spectral_charge_table.get("status")
        == "D20_PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_CERTIFIED"
        and projective_packet_spectral_charge_table.get("all_checks_pass") is True
    )
    projective_packet_charge_frame_classifier_certified = (
        projective_packet_charge_frame_classifier.get("status")
        == "D20_PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_CERTIFIED"
        and projective_packet_charge_frame_classifier.get("all_checks_pass") is True
    )
    packet239_stabilizer_seed_candidate_certified = (
        packet239_stabilizer_seed_candidate.get("status")
        == "D20_PACKET239_STABILIZER_SEED_CANDIDATE_CERTIFIED"
        and packet239_stabilizer_seed_candidate.get("all_checks_pass") is True
    )
    packet239_seed_propagation_certified = (
        packet239_seed_propagation.get("status")
        == "D20_PACKET239_SEED_PROPAGATION_CERTIFIED"
        and packet239_seed_propagation.get("all_checks_pass") is True
    )
    full_exposure_packet_propagation_cells_certified = (
        full_exposure_packet_propagation_cells.get("status")
        == "D20_FULL_EXPOSURE_PACKET_PROPAGATION_CELLS_CERTIFIED"
        and full_exposure_packet_propagation_cells.get("all_checks_pass") is True
    )
    full_exposure_packet_propagation_graph_certified = (
        full_exposure_packet_propagation_graph.get("status")
        == "D20_FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_CERTIFIED"
        and full_exposure_packet_propagation_graph.get("all_checks_pass") is True
    )
    full_exposure_rank10_tenfold_alignment_certified = (
        full_exposure_rank10_tenfold_alignment.get("status")
        == "D20_FULL_EXPOSURE_RANK10_TENFOLD_ALIGNMENT_CERTIFIED"
        and full_exposure_rank10_tenfold_alignment.get("all_checks_pass") is True
    )
    full_exposure_radical_gate_stabilizer_certified = (
        full_exposure_radical_gate_stabilizer.get("status")
        == "D20_FULL_EXPOSURE_RADICAL_GATE_STABILIZER_CERTIFIED"
        and full_exposure_radical_gate_stabilizer.get("all_checks_pass") is True
    )
    full_exposure_radical_gate_stabilizer_lift_certified = (
        full_exposure_radical_gate_stabilizer_lift.get("status")
        == "D20_FULL_EXPOSURE_RADICAL_GATE_STABILIZER_LIFT_CERTIFIED"
        and full_exposure_radical_gate_stabilizer_lift.get("all_checks_pass") is True
    )
    full_exposure_label_breaking_factorization_certified = (
        full_exposure_label_breaking_factorization.get("status")
        == "D20_FULL_EXPOSURE_LABEL_BREAKING_FACTORIZATION_CERTIFIED"
        and full_exposure_label_breaking_factorization.get("all_checks_pass") is True
    )
    full_exposure_canonical_labelled_frame_certified = (
        full_exposure_canonical_labelled_frame.get("status")
        == "D20_FULL_EXPOSURE_CANONICAL_LABELLED_FRAME_CERTIFIED"
        and full_exposure_canonical_labelled_frame.get("all_checks_pass") is True
    )
    full_exposure_label_coordinate_transition_operator_certified = (
        full_exposure_label_coordinate_transition_operator.get("status")
        == "D20_FULL_EXPOSURE_LABEL_COORDINATE_TRANSITION_OPERATOR_CERTIFIED"
        and full_exposure_label_coordinate_transition_operator.get("all_checks_pass") is True
    )
    full_exposure_label_coordinate_spectral_boundary_certified = (
        full_exposure_label_coordinate_spectral_boundary.get("status")
        == "D20_FULL_EXPOSURE_LABEL_COORDINATE_SPECTRAL_BOUNDARY_CERTIFIED"
        and full_exposure_label_coordinate_spectral_boundary.get("all_checks_pass") is True
    )
    full_exposure_label_coordinate_green_response_certified = (
        full_exposure_label_coordinate_green_response.get("status")
        == "D20_FULL_EXPOSURE_LABEL_COORDINATE_GREEN_RESPONSE_CERTIFIED"
        and full_exposure_label_coordinate_green_response.get("all_checks_pass") is True
    )
    full_exposure_zero_pair_propagator_charge_kernel_certified = (
        full_exposure_zero_pair_propagator_charge_kernel.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_PROPAGATOR_CHARGE_KERNEL_CERTIFIED"
        and full_exposure_zero_pair_propagator_charge_kernel.get("all_checks_pass") is True
    )
    full_exposure_zero_pair_propagator_symmetry_ward_certified = (
        full_exposure_zero_pair_propagator_symmetry_ward.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_PROPAGATOR_SYMMETRY_WARD_CERTIFIED"
        and full_exposure_zero_pair_propagator_symmetry_ward.get("all_checks_pass") is True
    )
    full_exposure_zero_pair_source_to_closed_return_coupling_certified = (
        full_exposure_zero_pair_source_to_closed_return_coupling.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCE_TO_CLOSED_RETURN_COUPLING_CERTIFIED"
        and full_exposure_zero_pair_source_to_closed_return_coupling.get("all_checks_pass") is True
    )
    full_exposure_zero_pair_ward_kernel_height_selector_certified = (
        full_exposure_zero_pair_ward_kernel_height_selector.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_WARD_KERNEL_HEIGHT_SELECTOR_CERTIFIED"
        and full_exposure_zero_pair_ward_kernel_height_selector.get("all_checks_pass") is True
    )
    full_exposure_zero_pair_selected_sourced_ward_balance_certified = (
        full_exposure_zero_pair_selected_sourced_ward_balance.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SELECTED_SOURCED_WARD_BALANCE_CERTIFIED"
        and full_exposure_zero_pair_selected_sourced_ward_balance.get("all_checks_pass") is True
    )
    full_exposure_zero_pair_sourced_balance_cone_certified = (
        full_exposure_zero_pair_sourced_balance_cone.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_CONE_CERTIFIED"
        and full_exposure_zero_pair_sourced_balance_cone.get("all_checks_pass") is True
    )
    full_exposure_zero_pair_sourced_balance_shortest_paths_certified = (
        full_exposure_zero_pair_sourced_balance_shortest_paths.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_SHORTEST_PATHS_CERTIFIED"
        and full_exposure_zero_pair_sourced_balance_shortest_paths.get("all_checks_pass") is True
    )
    full_exposure_zero_pair_sourced_balance_transport_families_certified = (
        full_exposure_zero_pair_sourced_balance_transport_families.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_TRANSPORT_FAMILIES_CERTIFIED"
        and full_exposure_zero_pair_sourced_balance_transport_families.get("all_checks_pass")
        is True
    )
    full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient_certified = (
        full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_LABEL_RELAXED_ORBIT_QUOTIENT_CERTIFIED"
        and full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient.get(
            "all_checks_pass"
        )
        is True
    )
    full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly_certified = (
        full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_ANOMALY_CERTIFIED"
        and full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly.get("all_checks_pass")
        is True
    )
    full_exposure_zero_pair_sourced_balance_c2_quotient_transport_ledger_certified = (
        full_exposure_zero_pair_sourced_balance_c2_quotient_transport_ledger.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_TRANSPORT_LEDGER_CERTIFIED"
        and full_exposure_zero_pair_sourced_balance_c2_quotient_transport_ledger.get(
            "all_checks_pass"
        )
        is True
    )
    full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator_certified = (
        full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_SCATTERING_OPERATOR_CERTIFIED"
        and full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator.get(
            "all_checks_pass"
        )
        is True
    )
    full_exposure_zero_pair_sourced_balance_c2_move_orbit_family_certified = (
        full_exposure_zero_pair_sourced_balance_c2_move_orbit_family.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_MOVE_ORBIT_FAMILY_CERTIFIED"
        and full_exposure_zero_pair_sourced_balance_c2_move_orbit_family.get(
            "all_checks_pass"
        )
        is True
    )
    full_exposure_zero_pair_sourced_balance_c2_dynamics_selector_certified = (
        full_exposure_zero_pair_sourced_balance_c2_dynamics_selector.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_DYNAMICS_SELECTOR_CERTIFIED"
        and full_exposure_zero_pair_sourced_balance_c2_dynamics_selector.get(
            "all_checks_pass"
        )
        is True
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_skeleton_certified = (
        full_exposure_zero_pair_sourced_balance_c2_cubical_agda_skeleton.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SKELETON_CERTIFIED"
        and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_skeleton.get(
            "all_checks_pass"
        )
        is True
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_certified = (
        full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_ENUMERATION_CERTIFIED"
        and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration.get(
            "all_checks_pass"
        )
        is True
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_properties_certified = (
        full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_properties.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_ENUMERATION_PROPERTIES_CERTIFIED"
        and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_properties.get(
            "all_checks_pass"
        )
        is True
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_membership_certified = (
        full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_membership.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_MEMBERSHIP_CERTIFIED"
        and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_membership.get(
            "all_checks_pass"
        )
        is True
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_singletons_certified = (
        full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_singletons.get(
            "status"
        )
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_SINGLETONS_CERTIFIED"
        and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_singletons.get(
            "all_checks_pass"
        )
        is True
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lazy63_certified = (
        full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lazy63.get(
            "status"
        )
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LAZY63_CERTIFIED"
        and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lazy63.get(
            "all_checks_pass"
        )
        is True
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_paired_lazy480_certified = (
        full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_paired_lazy480.get(
            "status"
        )
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_PAIRED_LAZY480_CERTIFIED"
        and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_paired_lazy480.get(
            "all_checks_pass"
        )
        is True
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_certified = (
        full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543.get(
            "status"
        )
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_CERTIFIED"
        and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543.get(
            "all_checks_pass"
        )
        is True
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_indexed_certified = (
        full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_indexed.get(
            "status"
        )
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_INDEXED_CERTIFIED"
        and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_indexed.get(
            "all_checks_pass"
        )
        is True
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_split_certified = (
        full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_split.get(
            "status"
        )
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_SPLIT_CERTIFIED"
        and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_split.get(
            "all_checks_pass"
        )
        is True
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_lookup_certified = (
        full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_lookup.get(
            "status"
        )
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_LOOKUP_CERTIFIED"
        and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_lookup.get(
            "all_checks_pass"
        )
        is True
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table_certified = (
        full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table.get(
            "status"
        )
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LOOKUP_TABLE_CERTIFIED"
        and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table.get(
            "all_checks_pass"
        )
        is True
    )
    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_emitter_factorization_certified = (
        full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_emitter_factorization.get(
            "status"
        )
        == "D20_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_EMITTER_FACTORIZATION_CERTIFIED"
        and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_emitter_factorization.get(
            "all_checks_pass"
        )
        is True
    )
    indexed_split_rows = (
        full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_split_derived.get(
            "indexed_selector_rows", []
        )
    )
    indexed_split_row_by_name = {row.get("name"): row for row in indexed_split_rows}
    indexed_lookup_rows = (
        full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_lookup_derived.get(
            "lookup_selector_rows", []
        )
    )
    indexed_lookup_row_by_name = {row.get("name"): row for row in indexed_lookup_rows}
    lookup_table_selector_summaries = (
        full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table_derived.get(
            "lookup_table_selector_summaries", []
        )
    )
    lookup_table_row_count_by_selector = (
        full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table_derived.get(
            "lookup_table_row_count_by_selector", {}
        )
    )
    lookup_table_source_package = (
        full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table_derived.get(
            "lookup_witness_source_package", {}
        )
    )
    lookup_table_source_package_certificate = lookup_table_source_package.get("certificate", {})
    actual_c2_kernel_orbit_sources = {
        "lazy63": full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lazy63_derived.get(
            "actual_c2_kernel_orbit_source", {}
        ),
        "paired_lazy480": full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_paired_lazy480_derived.get(
            "actual_c2_kernel_orbit_source", {}
        ),
        "raw543": full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_derived.get(
            "actual_c2_kernel_orbit_source", {}
        ),
        "raw543_indexed": full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_indexed_derived.get(
            "actual_c2_kernel_orbit_source", {}
        ),
        "indexed_split": full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_split_derived.get(
            "actual_c2_kernel_orbit_source", {}
        ),
        "indexed_lookup": full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_lookup_derived.get(
            "actual_c2_kernel_orbit_source", {}
        ),
        "lookup_table": full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table_derived.get(
            "actual_c2_kernel_orbit_source", {}
        ),
    }
    actual_c2_kernel_orbit_source_consumers = {
        name: source
        for name, source in actual_c2_kernel_orbit_sources.items()
        if name != "lookup_table"
    }

    checks = {
        "sector_attachment_is_certified": attachment.get("status")
        == "D20_SECTOR33_RESIDUAL_ATTACHMENT_CERTIFIED"
        and attachment.get("all_checks_pass") is True,
        "cycle8_is_the_target": cycle["cycle_id"] == 8
        and cycle["edge_ids"] == [11, 1, 2, 22, 21]
        and cycle["optical_action"] == 374784,
        "tube_section_is_certified": tube_section.get("projection", {}).get("closed_loop_quotient_dimension") == 297
        and tube_section.get("projection", {}).get("tube_pair_basis_total") == 44521
        and tube_section.get("section", {}).get("projection_section_identity") is True,
        "pi33_sector_interface_is_known": attachment.get("derived", {})
        .get("sector_attachment", {})
        .get("a985_sector")
        == 33,
        "boundary_to_loop_report_exists": BOUNDARY_TO_LOOP_REPORT.exists(),
        "boundary_to_loop_map_is_certified": boundary_lift_map_present,
        "boundary_cycle8_matches_target": boundary_cycle8_cycle.get("edge_ids") == [11, 1, 2, 22, 21]
        and boundary_cycle8_cycle.get("optical_action") == 374784,
        "boundary_cycle8_lift_is_witnessed_in_loop297": boundary_cycle8_vector.get("support") == 193
        and boundary_cycle8_vector.get("coefficient_sum") == 53952
        and boundary_cycle8_vector.get("mod_prime_sum") == 53952,
        "boundary_cycle8_lift_has_sector33_base_overlap": "B+" in boundary_cycle8_object_summary
        or "S+" in boundary_cycle8_object_summary,
        "pi33_tube_functional_is_certified": pi33_tube_functional_materialized,
        "bare_lambda_cycle8_pi33_coefficient_is_zero": bare_lambda_coefficient_is_zero,
        "height_coherent_transport_is_certified": height_coherent_transport_certified,
        "height_transport_recovers_sector33_residual": height_transport_character.get("height_transport", {}).get(
            "coefficient_signed"
        )
        == -374784,
        "height_transport_public_shadows_are_zero": height_transport_derived.get("public_shadows", {})
        .get("height_transport_q42", {})
        .get("nonzero_count")
        == 0
        and height_transport_derived.get("public_shadows", {})
        .get("height_transport_q12", {})
        .get("nonzero_count")
        == 0,
        "all_residue_height_transport_is_certified": all_residue_transport_certified,
        "all_2047_nonzero_residue_classes_are_carried_by_sector33": all_residue_derived.get(
            "nonzero_residue_class_count"
        )
        == 2047
        and all_residue_transport.get("checks", {}).get("all_transports_carried_by_sector33") is True,
        "basis_active_matrix_is_height_coherent": all_residue_transport.get("checks", {}).get(
            "basis_active_circuit_matrix_is_height_coherent"
        )
        is True,
        "edge_mod2_height_caveat_is_witnessed": all_residue_derived.get("edge_mod2_height_incoherence", {}).get(
            "mismatch_count", 0
        )
        > 0,
        "unique_public_zero_support_is_certified": unique_public_zero_support_certified,
        "sector33_is_unique_single_sector_public_zero_support": unique_public_zero_derived.get(
            "public_zero_sectors"
        )
        == [33]
        and unique_public_zero_support.get("checks", {}).get(
            "sector33_is_unique_single_sector_public_zero_support"
        )
        is True,
        "all_nonzero_height_residuals_are_field_nonzero_for_unique_support": unique_public_zero_derived.get(
            "nonzero_height_residual_count"
        )
        == 2047
        and unique_public_zero_derived.get("field_zero_nonzero_residual_count") == 0,
        "sector_public_shadow_kernel_is_certified": sector_public_shadow_kernel_certified,
        "full_sector_public_shadow_kernel_dimension_is_27": public_shadow_kernel_derived.get(
            "kernel_dimension"
        )
        == 27
        and public_shadow_kernel_derived.get("rank_mod_prime") == 12,
        "pi33_uniqueness_is_coordinate_axis_not_linear_span": public_shadow_kernel_derived.get(
            "coordinate_axis_public_zero_sectors"
        )
        == [33]
        and public_shadow_kernel_derived.get("non_axis_kernel_basis_count", 0) > 0,
        "sector_idempotent_support_admissibility_is_certified": (
            sector_idempotent_support_admissibility_certified
        ),
        "public_zero_idempotent_boundary_null_supports_are_classified": idempotent_admissibility_derived.get(
            "nonzero_public_zero_boundary_null_supports"
        )
        == [[6, 26], [25, 26], [33], [6, 26, 33], [25, 26, 33]],
        "pi33_is_unique_primitive_and_height_support_exact_support": idempotent_admissibility_derived.get(
            "primitive_single_sector_public_zero"
        )
        == [33]
        and idempotent_admissibility_derived.get("height_support_exact_supports_for_certified_transport")
        == [[33]],
        "minimal_composite_transport_is_certified": minimal_composite_transport_certified,
        "minimal_composites_are_superselection_not_gauge": minimal_composite_transport.get("checks", {}).get(
            "minimal_composites_classified_as_superselection_not_gauge"
        )
        is True
        and minimal_composite_transport.get("checks", {}).get("minimal_composites_are_not_gauge_zero")
        is True,
        "minimal_composites_are_isolated_from_pi33": minimal_composite_transport_derived.get(
            "transport_to_pi33_ranks"
        )
        == {"6,26": 0, "25,26": 0}
        and minimal_composite_transport_derived.get("transport_from_pi33_ranks")
        == {"6,26": 0, "25,26": 0},
        "superselection_flux_extension_is_certified": superselection_flux_extension_certified,
        "augmented_boundary_charge_tracks_three_hidden_components": superselection_flux_extension_derived.get(
            "hidden_components"
        )
        == ["R33", "K_mixed_S", "K_pure_Sminus"],
        "two_composite_labels_are_non_gauge_and_R33_isolated_in_flux_extension": superselection_flux_extension.get(
            "checks", {}
        ).get("new_superselection_labels_are_not_gauge_zero")
        is True
        and superselection_flux_extension.get("checks", {}).get(
            "new_superselection_labels_are_isolated_from_R33"
        )
        is True,
        "typed_nonexact_optical_flux_update_is_certified": typed_nonexact_optical_flux_certified,
        "typed_nonexact_optical_flux_updates_R33_only": typed_nonexact_optical_flux.get("checks", {}).get(
            "all_nonzero_updates_go_to_R33"
        )
        is True
        and typed_nonexact_optical_flux.get("checks", {}).get(
            "composite_superselection_labels_are_reserved_not_optically_excited"
        )
        is True,
        "sector26_alignment_is_recorded": typed_nonexact_optical_flux.get("checks", {}).get(
            "sector26_is_shared_minimal_composite_seam"
        )
        is True
        and typed_nonexact_optical_flux.get("checks", {}).get(
            "sector26_aligns_with_bosonic_critical_dimension"
        )
        is True,
        "sector26_invariant_suite_is_certified": sector26_invariant_suite_certified,
        "sector26_quotient_cancellation_is_stable": sector26_invariant_suite.get("checks", {}).get(
            "sector26_cancellation_is_stable_in_A42_and_A12_for_both_minimal_composites"
        )
        is True
        and sector26_invariant_suite.get("checks", {}).get("sector26_is_public_visible_alone") is True,
        "sector26_mod26_optical_clock_is_complete": sector26_invariant_suite.get("checks", {}).get(
            "normalized_nonzero_actions_hit_all_26_residues"
        )
        is True,
        "finite_anomaly_counter_is_certified": finite_anomaly_counter_certified,
        "finite_anomaly_counter_detects_nonadditive_mod26_clock": finite_anomaly_counter.get(
            "checks", {}
        ).get("z26_clock_is_not_linear_character")
        is True
        and finite_anomaly_counter.get("checks", {}).get("anomaly_defect_formula_matches_all_pairs")
        is True,
        "finite_anomaly_counter_has_mod2_character_and_mod13_half_counter": finite_anomaly_counter.get(
            "checks", {}
        ).get("z2_parity_shadow_is_linear_character")
        is True
        and finite_anomaly_counter.get("checks", {}).get("half_anomaly_hits_all_mod13_classes")
        is True,
        "sector26_anomaly_cancellation_is_certified": sector26_anomaly_cancellation_certified,
        "sector26_maximal_cancelled_packet_dimension_is_3": sector26_anomaly_cancellation.get(
            "checks", {}
        ).get("maximal_cancelled_packet_dimension_is_3")
        is True
        and sector26_anomaly_cancellation.get("checks", {}).get("no_dimension_4_cancelled_packet_exists")
        is True,
        "gamma8_is_excluded_from_anomaly_cancelled_packets": sector26_anomaly_cancellation.get(
            "checks", {}
        ).get("gamma8_is_excluded_from_all_cancelled_packets")
        is True,
        "anomaly_cancelled_flux_balance_recovery_is_certified": (
            anomaly_cancelled_flux_balance_recovery_certified
        ),
        "recovered_flux_balance_has_additive_R33_mod26": anomaly_cancelled_flux_balance_recovery.get(
            "checks", {}
        ).get("all_packet_clocks_are_additive_mod26")
        is True
        and anomaly_cancelled_flux_balance_recovery.get("checks", {}).get(
            "exact_public_flux_closes_on_certified_cycle_space"
        )
        is True,
        "gamma8_is_not_in_recovered_flux_balance_sector": anomaly_cancelled_flux_balance_recovery.get(
            "checks", {}
        ).get("gamma8_is_not_recovered")
        is True,
        "gamma8_obstruction_correction_is_certified": gamma8_obstruction_correction_certified,
        "gamma8_minimal_counterterm_is_5": gamma8_obstruction_correction.get("checks", {}).get(
            "minimal_signed_mod26_lift_is_5"
        )
        is True
        and gamma8_obstruction_correction.get("checks", {}).get(
            "corrected_gamma8_r33_is_order_two"
        )
        is True,
        "gamma8_corrected_packets_include_gamma8": gamma8_obstruction_correction.get(
            "checks", {}
        ).get("all_corrected_maximal_packets_contain_gamma8")
        is True,
        "general_obstruction_correction_suite_is_certified": (
            general_obstruction_correction_suite_certified
        ),
        "all_basis_coordinates_have_rank_one_corrections": general_obstruction_correction_suite.get(
            "checks", {}
        ).get("all_coordinate_corrections_are_rank_one")
        is True
        and general_obstruction_correction_suite.get("checks", {}).get(
            "all_11_basis_coordinates_are_self_anomalous"
        )
        is True,
        "general_suite_opens_dimension4_for_every_coordinate": general_obstruction_correction_suite.get(
            "checks", {}
        ).get("every_corrected_search_opens_dimension_4")
        is True
        and general_obstruction_correction_suite.get("checks", {}).get(
            "every_corrected_packet_clock_is_additive"
        )
        is True,
        "global_counterterm_lattice_is_certified": global_counterterm_lattice_certified,
        "global_counterterm_lattice_balances_full_residue_group": global_counterterm_lattice.get(
            "checks", {}
        ).get("corrected_clock_is_additive_on_all_2048_masks")
        is True
        and global_counterterm_lattice.get("checks", {}).get(
            "corrected_half_anomaly_vanishes_on_all_pairs"
        )
        is True,
        "global_counterterm_lattice_includes_gamma8": global_counterterm_lattice.get("checks", {}).get(
            "gamma8_is_included_with_order_two_value"
        )
        is True,
        "global_corrected_charge_map_is_certified": global_corrected_charge_map_certified,
        "global_corrected_charge_map_compares_to_public_exact_basis": global_corrected_charge_map.get(
            "checks", {}
        ).get("public_closed_return_rank_is_zero")
        is True
        and global_corrected_charge_map.get("checks", {}).get("corrected_hidden_rank_is_one")
        is True
        and global_corrected_charge_map.get("checks", {}).get(
            "hidden_character_not_in_public_closed_span"
        )
        is True,
        "global_corrected_charge_map_detects_gamma8": global_corrected_charge_map.get(
            "checks", {}
        ).get("gamma8_is_public_exact_zero_but_hidden_nonzero")
        is True,
        "global_corrected_hidden_split_symmetry_is_certified": (
            global_corrected_hidden_split_symmetry_certified
        ),
        "global_corrected_hidden_split_symmetry_reduces_public_symmetry_to_c2": (
            global_corrected_hidden_split_symmetry.get("checks", {}).get(
                "hidden_split_stabilizer_has_order_2"
            )
            is True
            and global_corrected_hidden_split_symmetry.get("checks", {}).get(
                "hidden_split_breaks_118_public_graph_symmetries"
            )
            is True
        ),
        "global_corrected_hidden_split_symmetry_fixes_gamma8": (
            global_corrected_hidden_split_symmetry.get("checks", {}).get(
                "gamma8_mask_is_fixed_by_hidden_split_stabilizer"
            )
            is True
        ),
        "hidden_split_augmented_ledger_stabilizer_is_certified": (
            hidden_split_augmented_ledger_stabilizer_certified
        ),
        "hidden_split_augmented_ledger_stabilizer_is_identity": (
            hidden_split_augmented_ledger_stabilizer.get("checks", {}).get(
                "full_augmented_ledger_stabilizer_is_identity"
            )
            is True
        ),
        "hidden_split_nonidentity_breaks_augmented_ledger_fields": (
            hidden_split_augmented_ledger_stabilizer.get("checks", {}).get(
                "nonidentity_breaks_sector26_counterterm_vector"
            )
            is True
            and hidden_split_augmented_ledger_stabilizer.get("checks", {}).get(
                "nonidentity_breaks_optical_weights"
            )
            is True
            and hidden_split_augmented_ledger_stabilizer.get("checks", {}).get(
                "nonidentity_breaks_public_charge_components"
            )
            is True
        ),
        "canonical_flux_balance_gauge_is_certified": canonical_flux_balance_gauge_certified,
        "canonical_flux_balance_gauge_has_unique_root_and_orientation": (
            canonical_flux_balance_gauge.get("checks", {}).get(
                "public_charges_uniquely_mark_all_vertices"
            )
            is True
            and canonical_flux_balance_gauge.get("checks", {}).get("canonical_root_is_unique")
            is True
            and canonical_flux_balance_gauge.get("checks", {}).get(
                "canonical_edge_orientation_has_no_charge_ties"
            )
            is True
        ),
        "canonical_flux_balance_gauge_is_root_fixed_unique": (
            canonical_flux_balance_gauge.get("checks", {}).get("incidence_rank_is_connected_graph_rank_19")
            is True
            and canonical_flux_balance_gauge.get("checks", {}).get("rooted_incidence_rank_is_full_20")
            is True
            and canonical_flux_balance_gauge.get("checks", {}).get(
                "rooted_four_component_flux_potential_gauge_dimension_is_0"
            )
            is True
        ),
        "canonical_loop_pi33_obstruction_is_certified": canonical_loop_pi33_obstruction_certified,
        "canonical_loop_pi33_obstruction_uses_canonical_root_edge": (
            canonical_loop_pi33_obstruction.get("checks", {}).get(
                "canonical_root_and_root_edge_match_cycle8"
            )
            is True
            and canonical_loop_pi33_obstruction.get("checks", {}).get(
                "cycle8_root_edge_is_traversed_in_canonical_direction"
            )
            is True
        ),
        "canonical_loop_pi33_obstruction_keeps_bare_zero_and_height_residual": (
            canonical_loop_pi33_obstruction.get("checks", {}).get(
                "bare_pi33_coefficients_are_zero_for_all_recorded_variants"
            )
            is True
            and canonical_loop_pi33_obstruction.get("checks", {}).get(
                "height_corrected_pi33_obstruction_is_nonzero_and_canonical"
            )
            is True
            and canonical_loop_pi33_obstruction.get("checks", {}).get(
                "height_corrected_obstruction_has_zero_public_shadow"
            )
            is True
        ),
        "canonical_finite_ward_identity_is_certified": canonical_finite_ward_identity_certified,
        "canonical_finite_ward_identity_has_zero_public_and_bare_terms": (
            canonical_finite_ward_identity.get("checks", {}).get(
                "exact_public_flux_gauge_term_is_zero"
            )
            is True
            and canonical_finite_ward_identity.get("checks", {}).get("bare_pi33_terms_are_zero")
            is True
        ),
        "canonical_finite_ward_identity_balances_height_corrected_r33": (
            canonical_finite_ward_identity.get("checks", {}).get(
                "height_corrected_r33_term_is_negative_height_action"
            )
            is True
            and canonical_finite_ward_identity.get("checks", {}).get("finite_ward_scalar_sum_is_zero")
            is True
        ),
        "canonical_all_mask_ward_identity_is_certified": canonical_all_mask_ward_identity_certified,
        "canonical_all_mask_ward_identity_balances_all_2048_masks": (
            canonical_all_mask_ward_identity.get("checks", {}).get(
                "all_ward_scalar_sums_are_zero"
            )
            is True
            and canonical_all_mask_ward_identity.get("checks", {}).get(
                "residue_masks_are_complete"
            )
            is True
            and canonical_all_mask_ward_identity_derived.get("mask_count") == 2048
        ),
        "canonical_all_mask_ward_identity_extends_gamma8": (
            canonical_all_mask_ward_identity.get("checks", {}).get(
                "gamma8_row_extends_canonical_finite_ward_identity"
            )
            is True
            and canonical_all_mask_ward_identity_derived.get("gamma8_row", {}).get(
                "height_corrected_R33"
            )
            == -374784
            and canonical_all_mask_ward_identity_derived.get("gamma8_row", {}).get(
                "ward_scalar_sum"
            )
            == 0
        ),
        "canonical_all_mask_ward_identity_preserves_global_hidden_split": (
            canonical_all_mask_ward_identity.get("checks", {}).get(
                "global_corrected_character_is_additive"
            )
            is True
            and canonical_all_mask_ward_identity.get("checks", {}).get(
                "global_corrected_kernel_has_dimension_10"
            )
            is True
        ),
        "finite_bms_carrollian_flux_balance_is_certified": (
            finite_bms_carrollian_flux_balance_certified
        ),
        "finite_bms_carrollian_flux_balance_names_all_masks": (
            finite_bms_carrollian_flux_balance.get("checks", {}).get("all_2048_masks_are_named")
            is True
            and finite_bms_carrollian_flux_balance_derived.get("balance_summary", {}).get(
                "mask_count"
            )
            == 2048
        ),
        "finite_bms_carrollian_flux_balance_closes_public_and_hidden_terms": (
            finite_bms_carrollian_flux_balance.get("checks", {}).get(
                "public_flux_balance_holds_for_all_masks"
            )
            is True
            and finite_bms_carrollian_flux_balance.get("checks", {}).get(
                "hidden_r33_action_balance_holds_for_all_masks"
            )
            is True
            and finite_bms_carrollian_flux_balance.get("checks", {}).get(
                "r33_residual_is_negative_height_flux_for_all_masks"
            )
            is True
        ),
        "finite_bms_carrollian_flux_balance_preserves_hidden_packet_split": (
            finite_bms_carrollian_flux_balance.get("checks", {}).get(
                "global_corrected_r33_split_is_preserved"
            )
            is True
            and finite_bms_carrollian_flux_balance_derived.get("balance_summary", {}).get(
                "hidden_packet_histogram"
            )
            == {"kernel": 1024, "odd": 1024}
        ),
        "hidden_packet_charge_frame_classifier_is_certified": (
            hidden_packet_charge_frame_classifier_certified
        ),
        "hidden_packet_charge_frame_classifier_splits_kernel_and_odd": (
            hidden_packet_charge_frame_classifier.get("checks", {}).get(
                "hidden_packets_split_evenly"
            )
            is True
            and hidden_packet_charge_frame_classifier_derived.get("packet_histograms", {}).get(
                "hidden_packet"
            )
            == {"kernel": 1024, "odd": 1024}
        ),
        "hidden_packet_charge_frame_classifier_refines_to_2032_classes": (
            hidden_packet_charge_frame_classifier.get("checks", {}).get(
                "coarse_charge_frame_classifier_has_942_classes"
            )
            is True
            and hidden_packet_charge_frame_classifier.get("checks", {}).get(
                "refined_charge_frame_classifier_has_2032_classes"
            )
            is True
        ),
        "hidden_packet_charge_frame_classifier_action_separates_all_masks": (
            hidden_packet_charge_frame_classifier.get("checks", {}).get(
                "complete_charge_action_classifier_separates_all_masks"
            )
            is True
            and hidden_packet_charge_frame_classifier_derived.get("classifiers", {})
            .get("complete_charge_action", {})
            .get("class_count")
            == 2048
        ),
        "canonical_finite_scattering_table_is_certified": (
            canonical_finite_scattering_table_certified
        ),
        "canonical_finite_scattering_table_names_all_generator_transitions": (
            canonical_finite_scattering_table.get("checks", {}).get(
                "directed_transition_count_is_2048_times_11"
            )
            is True
            and canonical_finite_scattering_table_derived.get("transition_counts", {}).get(
                "directed_transition_count"
            )
            == 22528
        ),
        "canonical_finite_scattering_table_has_involutive_reverse_rows": (
            canonical_finite_scattering_table.get("checks", {}).get(
                "every_transition_has_involutive_reverse"
            )
            is True
            and canonical_finite_scattering_table.get("checks", {}).get(
                "height_flux_delta_histogram_matches_generator_actions"
            )
            is True
        ),
        "canonical_finite_scattering_table_has_expected_packet_transfers": (
            canonical_finite_scattering_table.get("checks", {}).get(
                "packet_transfer_histogram_matches_basis_clock"
            )
            is True
            and canonical_finite_scattering_table_derived.get("hidden_R33_transfer_mod26_histogram")
            == {"0": 2048, "13": 20480}
        ),
        "loop297_scattering_amplitude_lift_is_certified": (
            loop297_scattering_amplitude_lift_certified
        ),
        "loop297_scattering_amplitude_lift_attaches_all_generator_packets": (
            loop297_scattering_amplitude_lift.get("checks", {}).get(
                "primitive_generator_amplitude_packet_count_is_11"
            )
            is True
            and loop297_scattering_amplitude_lift_derived.get("lifted_transition_counts", {}).get(
                "primitive_generator_count"
            )
            == 11
        ),
        "loop297_scattering_amplitude_lift_covers_all_scattering_rows": (
            loop297_scattering_amplitude_lift.get("checks", {}).get(
                "lifted_transition_count_matches_scattering_table"
            )
            is True
            and loop297_scattering_amplitude_lift_derived.get("lifted_transition_counts", {}).get(
                "directed_transition_count"
            )
            == 22528
        ),
        "loop297_scattering_amplitude_lift_balances_pi33_and_height_transfer": (
            loop297_scattering_amplitude_lift.get("checks", {}).get(
                "all_lifted_rows_have_zero_bare_pi33"
            )
            is True
            and loop297_scattering_amplitude_lift.get("checks", {}).get(
                "all_lifted_rows_balance_height_corrected_r33_transfer"
            )
            is True
            and loop297_scattering_amplitude_lift.get("checks", {}).get(
                "gamma8_self_generator_lift_returns_to_zero_with_positive_correction"
            )
            is True
        ),
        "compact_amplitude_quotient_is_certified": compact_amplitude_quotient_certified,
        "compact_amplitude_quotient_collapses_tube_zero_class": (
            compact_amplitude_quotient.get("checks", {}).get(
                "bare_pi33_quotient_collapses_all_generators"
            )
            is True
            and compact_amplitude_quotient_derived.get("quotient_summary", {}).get(
                "bare_pi33_quotient_class_count"
            )
            == 1
        ),
        "compact_amplitude_quotient_uses_25_loop_atoms": (
            compact_amplitude_quotient.get("checks", {}).get("used_step_atom_count_is_25")
            is True
            and compact_amplitude_quotient_derived.get("quotient_summary", {}).get(
                "used_loop_step_atom_count"
            )
            == 25
        ),
        "compact_amplitude_quotient_separates_all_generators": (
            compact_amplitude_quotient.get("checks", {}).get(
                "step_hash_multiset_quotient_separates_generators"
            )
            is True
            and compact_amplitude_quotient.get("checks", {}).get(
                "ordered_step_chain_quotient_separates_generators"
            )
            is True
            and compact_amplitude_quotient_derived.get("quotient_summary", {}).get(
                "ordered_step_chain_quotient_class_count"
            )
            == 11
        ),
        "compact_amplitude_quotient_tracks_gamma8_and_generator3": (
            compact_amplitude_quotient.get("checks", {}).get(
                "gamma8_row_matches_certified_cycle8_packet"
            )
            is True
            and compact_amplitude_quotient.get("checks", {}).get(
                "hidden_packet_preserving_generator_is_exactly_3"
            )
            is True
        ),
        "reduced_amplitude_quotient_scattering_automaton_is_certified": (
            reduced_amplitude_quotient_scattering_automaton_certified
        ),
        "reduced_amplitude_quotient_scattering_automaton_covers_all_states_and_transitions": (
            reduced_amplitude_quotient_scattering_automaton.get("checks", {}).get(
                "state_count_is_2048"
            )
            is True
            and reduced_amplitude_quotient_scattering_automaton.get("checks", {}).get(
                "transition_count_is_2048_times_11"
            )
            is True
            and reduced_amplitude_quotient_scattering_automaton_derived.get(
                "automaton_summary", {}
            ).get("directed_transition_count")
            == 22528
        ),
        "reduced_amplitude_quotient_scattering_automaton_is_regular_reversible_and_connected": (
            reduced_amplitude_quotient_scattering_automaton.get("checks", {}).get(
                "automaton_is_connected"
            )
            is True
            and reduced_amplitude_quotient_scattering_automaton.get("checks", {}).get(
                "outdegree_and_indegree_are_11_regular"
            )
            is True
            and reduced_amplitude_quotient_scattering_automaton.get("checks", {}).get(
                "every_transition_has_reverse_with_same_compact_label"
            )
            is True
        ),
        "reduced_amplitude_quotient_scattering_automaton_certifies_spectrum_and_sector_matrix": (
            reduced_amplitude_quotient_scattering_automaton.get("checks", {}).get(
                "adjacency_spectrum_has_expected_dimension_and_moments"
            )
            is True
            and reduced_amplitude_quotient_scattering_automaton.get("checks", {}).get(
                "hidden_sector_quotient_matrix_is_1_10_10_1"
            )
            is True
            and reduced_amplitude_quotient_scattering_automaton_derived.get(
                "sector_invariants", {}
            )
            .get("per_state_sector_quotient_matrix", {})
            .get("matrix")
            == [[1, 10], [10, 1]]
        ),
        "reduced_amplitude_quotient_scattering_automaton_tracks_gamma8_and_atoms": (
            reduced_amplitude_quotient_scattering_automaton.get("checks", {}).get(
                "gamma8_label_has_2048_transitions_and_expected_action"
            )
            is True
            and reduced_amplitude_quotient_scattering_automaton.get("checks", {}).get(
                "atom_exposure_uses_25_step_atoms"
            )
            is True
        ),
        "amplitude_quotient_fourier_mode_classifier_is_certified": (
            amplitude_quotient_fourier_mode_classifier_certified
        ),
        "amplitude_quotient_fourier_mode_classifier_covers_all_2048_modes": (
            amplitude_quotient_fourier_mode_classifier.get("checks", {}).get(
                "mode_count_matches_automaton_state_count"
            )
            is True
            and amplitude_quotient_fourier_mode_classifier_derived.get(
                "classifier_summary", {}
            ).get("mode_count")
            == 2048
        ),
        "amplitude_quotient_fourier_mode_classifier_matches_hypercube_spectrum": (
            amplitude_quotient_fourier_mode_classifier.get("checks", {}).get(
                "spectral_histogram_matches_hypercube_formula"
            )
            is True
            and amplitude_quotient_fourier_mode_classifier.get("checks", {}).get(
                "spectral_histogram_matches_automaton_report"
            )
            is True
        ),
        "amplitude_quotient_fourier_mode_classifier_matches_sector26_clock": (
            amplitude_quotient_fourier_mode_classifier.get("checks", {}).get(
                "sector26_optical_clock_hits_all_26_residues"
            )
            is True
            and amplitude_quotient_fourier_mode_classifier.get("checks", {}).get(
                "nonzero_sector26_optical_clock_histogram_matches_sector26_suite"
            )
            is True
        ),
        "amplitude_quotient_fourier_mode_classifier_tracks_hidden_and_gamma8_modes": (
            amplitude_quotient_fourier_mode_classifier.get("checks", {}).get(
                "hidden_sign_mode_matches_sector_quotient_eigenvalue"
            )
            is True
            and amplitude_quotient_fourier_mode_classifier.get("checks", {}).get(
                "gamma8_basis_mode_matches_first_obstruction_clock"
            )
            is True
        ),
        "finite_virasoro_string_kernel_candidate_is_certified": (
            finite_virasoro_string_kernel_candidate_certified
        ),
        "finite_virasoro_string_kernel_candidate_identifies_rank10_closure": (
            finite_virasoro_string_kernel_candidate.get("checks", {}).get(
                "minimal_kernel_closure_has_rank_10_and_1024_modes"
            )
            is True
            and finite_virasoro_string_kernel_candidate.get("checks", {}).get(
                "kernel_closure_is_defined_by_5_9_10_parity"
            )
            is True
        ),
        "finite_virasoro_string_kernel_candidate_records_seed_nonclosure": (
            finite_virasoro_string_kernel_candidate.get("checks", {}).get(
                "seed_zero_clock_fiber_has_83_modes"
            )
            is True
            and finite_virasoro_string_kernel_candidate.get("checks", {}).get(
                "seed_zero_clock_fiber_is_not_additively_closed"
            )
            is True
        ),
        "finite_virasoro_string_kernel_candidate_closes_by_cross_return_composites": (
            finite_virasoro_string_kernel_candidate.get("checks", {}).get(
                "primitive_generators_split_as_8_preserving_3_crossing"
            )
            is True
            and finite_virasoro_string_kernel_candidate.get("checks", {}).get(
                "paired_cross_return_composites_connect_kernel"
            )
            is True
        ),
        "finite_virasoro_string_kernel_candidate_tracks_gamma8_and_hidden_sign": (
            finite_virasoro_string_kernel_candidate.get("checks", {}).get(
                "kernel_closure_contains_gamma8_but_not_hidden_sign_mode"
            )
            is True
            and finite_virasoro_string_kernel_candidate.get("checks", {}).get(
                "kernel_closure_keeps_constant_but_excludes_hidden_sign_projection"
            )
            is True
        ),
        "finite_virasoro_generator_algebra_is_certified": (
            finite_virasoro_generator_algebra_certified
        ),
        "finite_virasoro_generator_algebra_has_rank10_operator_basis": (
            finite_virasoro_generator_algebra.get("checks", {}).get(
                "operator_basis_has_1024_rank10_masks"
            )
            is True
            and finite_virasoro_generator_algebra_derived.get(
                "algebra_summary", {}
            ).get("operator_basis_rank")
            == 10
        ),
        "finite_virasoro_generator_algebra_commutators_vanish": (
            finite_virasoro_generator_algebra.get("checks", {}).get(
                "all_generator_commutators_vanish"
            )
            is True
            and finite_virasoro_generator_algebra_derived.get(
                "algebra_summary", {}
            ).get("all_commutators_zero")
            is True
        ),
        "finite_virasoro_generator_algebra_has_single_cross_composite_relation": (
            finite_virasoro_generator_algebra.get("checks", {}).get(
                "generator_masks_have_rank10_with_one_relation"
            )
            is True
            and finite_virasoro_generator_algebra_derived.get(
                "algebra_summary", {}
            ).get("relation_count_mod_involutions")
            == 1
        ),
        "finite_virasoro_generator_algebra_classifies_sector26_clock_defect": (
            finite_virasoro_generator_algebra.get("checks", {}).get(
                "sector26_clock_defect_is_classified_on_generator_products"
            )
            is True
            and finite_virasoro_generator_algebra.get("checks", {}).get(
                "sector26_clock_defect_is_only_overlap_cancellation"
            )
            is True
        ),
        "finite_central_extension_anomaly_cocycle_is_certified": (
            finite_central_extension_anomaly_cocycle_certified
        ),
        "finite_central_extension_anomaly_cocycle_kills_z26_alternating_term": (
            finite_central_extension_anomaly_cocycle.get("checks", {}).get(
                "canonical_z26_alternating_central_term_vanishes"
            )
            is True
            and finite_central_extension_anomaly_cocycle.get("checks", {}).get(
                "canonical_z26_clock_defect_is_symmetric"
            )
            is True
        ),
        "finite_central_extension_anomaly_cocycle_finds_f2_survivor": (
            finite_central_extension_anomaly_cocycle.get("checks", {}).get(
                "f2_compatible_alternating_solution_is_one_dimensional"
            )
            is True
            and finite_central_extension_anomaly_cocycle_derived.get(
                "central_extension_summary", {}
            ).get("compatible_f2_cocycle_dimension")
            == 1
        ),
        "finite_central_extension_anomaly_cocycle_tracks_composite_triangle": (
            finite_central_extension_anomaly_cocycle.get("checks", {}).get(
                "f2_representative_is_supported_on_cross_composite_triangle"
            )
            is True
            and finite_central_extension_anomaly_cocycle.get("checks", {}).get(
                "f2_representative_descends_through_cross_composite_relation"
            )
            is True
        ),
        "finite_parity_central_extension_group_is_certified": (
            finite_parity_central_extension_group_certified
        ),
        "finite_parity_central_extension_group_has_d8_c2_8_type": (
            finite_parity_central_extension_group.get("checks", {}).get(
                "central_extension_group_has_d8_times_c2_8_type"
            )
            is True
            and finite_parity_central_extension_group_derived.get(
                "central_extension_summary", {}
            ).get("extension_group_type")
            == "D8 x C2^8"
        ),
        "finite_parity_central_extension_group_commutator_is_composite_triangle": (
            finite_parity_central_extension_group.get("checks", {}).get(
                "named_commutator_table_is_exact_composite_triangle"
            )
            is True
            and finite_parity_central_extension_group.get("checks", {}).get(
                "cross_composite_relation_lifts_to_identity"
            )
            is True
        ),
        "finite_parity_central_extension_group_certifies_projective_kernel_action": (
            finite_parity_central_extension_group.get("checks", {}).get(
                "named_projective_actions_preserve_kernel_states"
            )
            is True
            and finite_parity_central_extension_group.get("checks", {}).get(
                "named_projective_action_composition_matches_group_law"
            )
            is True
            and finite_parity_central_extension_group.get("checks", {}).get(
                "central_bit_acts_as_global_sign"
            )
            is True
        ),
        "projective_kernel_packet_tenfold_way_is_certified": (
            projective_kernel_packet_tenfold_way_certified
        ),
        "projective_kernel_packet_tenfold_way_decomposes_512_packets": (
            projective_kernel_packet_tenfold_way.get("checks", {}).get(
                "packet_decomposition_has_total_dimension_1024"
            )
            is True
            and projective_kernel_packet_tenfold_way_derived.get("packet_summary", {}).get(
                "irreducible_packet_count"
            )
            == 512
        ),
        "projective_kernel_packet_tenfold_way_tracks_sector26_and_loop297": (
            projective_kernel_packet_tenfold_way.get("checks", {}).get(
                "packet_mode_sector26_clock_histogram_matches_kernel"
            )
            is True
            and projective_kernel_packet_tenfold_way.get("checks", {}).get(
                "packet_exposure_uses_all_25_loop297_atoms"
            )
            is True
        ),
        "projective_kernel_packet_tenfold_way_certifies_rank10_tenfold_witness": (
            projective_kernel_packet_tenfold_way.get("checks", {}).get(
                "rank10_bott_split_is_8_plus_2"
            )
            is True
            and projective_kernel_packet_tenfold_way.get("checks", {}).get(
                "tenfold_way_minimal_real_class_is_ai_without_extra_hamiltonian"
            )
            is True
            and projective_kernel_packet_tenfold_way.get("checks", {}).get(
                "tenfold_way_optional_active_clifford_hamiltonian_gives_bdi_witness"
            )
            is True
        ),
        "projective_packet_spectral_charge_table_is_certified": (
            projective_packet_spectral_charge_table_certified
        ),
        "projective_packet_spectral_charge_table_has_512_rows": (
            projective_packet_spectral_charge_table.get("checks", {}).get(
                "packet_table_has_512_rows_and_total_dimension_1024"
            )
            is True
            and projective_packet_spectral_charge_table_derived.get(
                "spectral_charge_summary", {}
            ).get("packet_count")
            == 512
        ),
        "projective_packet_spectral_charge_table_tracks_charge_histograms": (
            projective_packet_spectral_charge_table.get("checks", {}).get(
                "laplacian_trace_histogram_matches_packet_spectrum"
            )
            is True
            and projective_packet_spectral_charge_table.get("checks", {}).get(
                "sector26_clock_delta_splits_evenly"
            )
            is True
            and projective_packet_spectral_charge_table.get("checks", {}).get(
                "hidden_clock_cancels_packetwise"
            )
            is True
        ),
        "projective_packet_spectral_charge_table_identifies_unique_full_clock_zero_packet": (
            projective_packet_spectral_charge_table.get("checks", {}).get(
                "unique_full_loop_clock_zero_packet_is_239"
            )
            is True
            and projective_packet_spectral_charge_table.get("checks", {}).get(
                "distinguished_full_loop_packets_match"
            )
            is True
        ),
        "projective_packet_charge_frame_classifier_is_certified": (
            projective_packet_charge_frame_classifier_certified
        ),
        "projective_packet_charge_frame_classifier_has_47_classes": (
            projective_packet_charge_frame_classifier.get("checks", {}).get(
                "charge_frame_key_count_is_47"
            )
            is True
            and projective_packet_charge_frame_classifier_derived.get(
                "classifier_summary", {}
            ).get("charge_frame_class_count")
            == 47
        ),
        "projective_packet_charge_frame_classifier_names_all_axes": (
            projective_packet_charge_frame_classifier.get("checks", {}).get(
                "charge_frame_axes_are_named"
            )
            is True
            and projective_packet_charge_frame_classifier.get("checks", {}).get(
                "hidden_axis_is_cancelled_everywhere"
            )
            is True
            and projective_packet_charge_frame_classifier.get("checks", {}).get(
                "tenfold_axis_is_ai_bdi_everywhere"
            )
            is True
        ),
        "projective_packet_charge_frame_classifier_isolates_packet239": (
            projective_packet_charge_frame_classifier.get("checks", {}).get(
                "packet239_is_unique_full_exposure_clock_zero_packet"
            )
            is True
            and projective_packet_charge_frame_classifier.get("checks", {}).get(
                "packet239_is_unique_in_charge_frame_and_fine_key"
            )
            is True
        ),
        "packet239_stabilizer_seed_candidate_is_certified": (
            packet239_stabilizer_seed_candidate_certified
        ),
        "packet239_stabilizer_seed_candidate_has_uniform_stabilizers": (
            packet239_stabilizer_seed_candidate.get("checks", {}).get(
                "all_packets_have_full_setwise_stabilizer"
            )
            is True
            and packet239_stabilizer_seed_candidate.get("checks", {}).get(
                "all_packets_have_uniform_scalar_stabilizer"
            )
            is True
            and packet239_stabilizer_seed_candidate.get("checks", {}).get(
                "all_packets_have_uniform_identity_kernel_order"
            )
            is True
        ),
        "packet239_stabilizer_seed_candidate_compares_full_exposure_peers": (
            packet239_stabilizer_seed_candidate.get("checks", {}).get(
                "full_exposure_packets_have_same_stabilizer_orders"
            )
            is True
            and packet239_stabilizer_seed_candidate.get("checks", {}).get(
                "packet239_stabilizer_orders_match_full_exposure_peers"
            )
            is True
        ),
        "packet239_stabilizer_seed_candidate_preserves_charge_seed_uniqueness": (
            packet239_stabilizer_seed_candidate.get("checks", {}).get(
                "packet239_charge_frame_remains_unique"
            )
            is True
            and packet239_stabilizer_seed_candidate.get("checks", {}).get(
                "packet239_is_charge_seed_not_symmetry_fixed_vacuum"
            )
            is True
        ),
        "packet239_seed_propagation_is_certified": (
            packet239_seed_propagation_certified
        ),
        "packet239_seed_propagation_hits_two_odd_shadows": (
            packet239_seed_propagation.get("checks", {}).get(
                "one_step_crossing_rows_hit_two_odd_packet_shadows"
            )
            is True
            and packet239_seed_propagation.get("checks", {}).get(
                "one_step_crossing_rows_are_full_exposure_gamma_silent"
            )
            is True
        ),
        "packet239_seed_propagation_returns_only_238_239": (
            packet239_seed_propagation.get("checks", {}).get(
                "two_step_cross_return_rows_hit_only_packets_238_and_239"
            )
            is True
            and packet239_seed_propagation.get("checks", {}).get(
                "cross_return_charge_frames_are_seed_and_active_partner"
            )
            is True
        ),
        "packet239_seed_propagation_tracks_cross_return_flux": (
            packet239_seed_propagation.get("checks", {}).get(
                "two_step_cross_return_flux_histogram_matches"
            )
            is True
            and packet239_seed_propagation.get("checks", {}).get(
                "two_step_cross_return_action_histogram_matches"
            )
            is True
            and packet239_seed_propagation.get("checks", {}).get(
                "two_step_cross_returns_cancel_hidden_transfer"
            )
            is True
        ),
        "full_exposure_packet_propagation_cells_is_certified": (
            full_exposure_packet_propagation_cells_certified
        ),
        "full_exposure_packet_propagation_cells_covers_20_packets": (
            full_exposure_packet_propagation_cells.get("checks", {}).get(
                "full_exposure_packet_count_is_20"
            )
            is True
            and full_exposure_packet_propagation_cells_derived.get(
                "propagation_cell_summary", {}
            ).get("full_exposure_packet_count")
            == 20
        ),
        "full_exposure_packet_propagation_cells_has_uniform_shape": (
            full_exposure_packet_propagation_cells.get("checks", {}).get(
                "every_full_packet_has_two_odd_shadows"
            )
            is True
            and full_exposure_packet_propagation_cells.get("checks", {}).get(
                "each_source_returns_twice_and_partner_four_times"
            )
            is True
            and full_exposure_packet_propagation_cells.get("checks", {}).get(
                "two_step_cross_returns_target_each_full_packet_six_times"
            )
            is True
        ),
        "full_exposure_packet_propagation_cells_tracks_flux_and_exposure": (
            full_exposure_packet_propagation_cells.get("checks", {}).get(
                "one_step_crossings_preserve_full_exposure"
            )
            is True
            and full_exposure_packet_propagation_cells.get("checks", {}).get(
                "two_step_flux_and_action_histograms_match"
            )
            is True
            and full_exposure_packet_propagation_cells.get("checks", {}).get(
                "two_step_cross_returns_cancel_hidden_transfer"
            )
            is True
        ),
        "full_exposure_packet_propagation_graph_is_certified": (
            full_exposure_packet_propagation_graph_certified
        ),
        "full_exposure_packet_propagation_graph_has_ten_doublets": (
            full_exposure_packet_propagation_graph.get("checks", {}).get(
                "graph_decomposes_into_ten_active_partner_doublets"
            )
            is True
            and full_exposure_packet_propagation_graph_derived.get(
                "graph_summary", {}
            ).get("component_count")
            == 10
        ),
        "full_exposure_packet_propagation_graph_has_uniform_operator": (
            full_exposure_packet_propagation_graph.get("checks", {}).get(
                "graph_has_uniform_weighted_degrees"
            )
            is True
            and full_exposure_packet_propagation_graph.get("checks", {}).get(
                "graph_has_uniform_self_and_partner_weights"
            )
            is True
            and full_exposure_packet_propagation_graph.get("checks", {}).get(
                "spectral_readout_matches_ten_doublet_blocks"
            )
            is True
        ),
        "full_exposure_packet_propagation_graph_balances_flux": (
            full_exposure_packet_propagation_graph.get("checks", {}).get(
                "signed_flux_balances_per_source_and_component"
            )
            is True
            and full_exposure_packet_propagation_graph.get("checks", {}).get(
                "hidden_transfer_cancels_everywhere"
            )
            is True
            and full_exposure_packet_propagation_graph.get("checks", {}).get(
                "action_budget_is_uniform"
            )
            is True
        ),
        "full_exposure_rank10_tenfold_alignment_is_certified": (
            full_exposure_rank10_tenfold_alignment_certified
        ),
        "full_exposure_rank10_tenfold_alignment_maps_doublets": (
            full_exposure_rank10_tenfold_alignment.get("checks", {}).get(
                "doublets_are_active_partner_planes"
            )
            is True
            and full_exposure_rank10_tenfold_alignment.get("checks", {}).get(
                "active_plane_mode_masks_match_packet_model"
            )
            is True
        ),
        "full_exposure_rank10_tenfold_alignment_certifies_nonbasis": (
            full_exposure_rank10_tenfold_alignment.get("checks", {}).get(
                "component_support_is_not_rank10_basis"
            )
            is True
            and full_exposure_rank10_tenfold_alignment_derived.get(
                "alignment_summary", {}
            ).get("canonical_rank10_axis_basis")
            is False
            and full_exposure_rank10_tenfold_alignment_derived.get(
                "alignment_summary", {}
            ).get("full_mode_affine_direction_rank")
            == 6
        ),
        "full_exposure_rank10_tenfold_alignment_preserves_active_tenfold_block": (
            full_exposure_rank10_tenfold_alignment.get("checks", {}).get(
                "tenfold_active_block_is_preserved"
            )
            is True
            and full_exposure_rank10_tenfold_alignment_derived.get(
                "tenfold_alignment", {}
            ).get("canonical_module_class")
            == "AI"
            and full_exposure_rank10_tenfold_alignment_derived.get(
                "tenfold_alignment", {}
            ).get("optional_active_hamiltonian_class")
            == "BDI"
        ),
        "full_exposure_radical_gate_stabilizer_is_certified": (
            full_exposure_radical_gate_stabilizer_certified
        ),
        "full_exposure_radical_gate_stabilizer_has_expected_orders": (
            full_exposure_radical_gate_stabilizer.get("checks", {}).get(
                "linear_stabilizer_order_is_64"
            )
            is True
            and full_exposure_radical_gate_stabilizer.get("checks", {}).get(
                "affine_stabilizer_order_is_384"
            )
            is True
            and full_exposure_radical_gate_stabilizer_derived.get(
                "stabilizer_summary", {}
            ).get("linear_stabilizer_order")
            == 64
            and full_exposure_radical_gate_stabilizer_derived.get(
                "stabilizer_summary", {}
            ).get("affine_stabilizer_order")
            == 384
        ),
        "full_exposure_radical_gate_stabilizer_prism_decomposition": (
            full_exposure_radical_gate_stabilizer.get("checks", {}).get(
                "gate_complement_is_six_point_prism"
            )
            is True
            and full_exposure_radical_gate_stabilizer.get("checks", {}).get(
                "group_decomposition_orders_match"
            )
            is True
            and full_exposure_radical_gate_stabilizer_derived.get(
                "complement_prism_witness", {}
            ).get("product_point_count")
            == 6
        ),
        "full_exposure_radical_gate_stabilizer_orbits_and_translations": (
            full_exposure_radical_gate_stabilizer.get("checks", {}).get(
                "pure_translation_stabilizer_is_x7_flip"
            )
            is True
            and full_exposure_radical_gate_stabilizer.get("checks", {}).get(
                "all_affine_translation_parts_are_complement_patterns"
            )
            is True
            and full_exposure_radical_gate_stabilizer.get("checks", {}).get(
                "orbit_structure_matches_prism_gate"
            )
            is True
        ),
        "full_exposure_radical_gate_stabilizer_lift_is_certified": (
            full_exposure_radical_gate_stabilizer_lift_certified
        ),
        "full_exposure_radical_gate_stabilizer_lift_preserves_graph_action": (
            full_exposure_radical_gate_stabilizer_lift.get("checks", {}).get(
                "all_384_affine_stabilizers_lift_to_canonical_graph_action"
            )
            is True
            and full_exposure_radical_gate_stabilizer_lift.get("checks", {}).get(
                "active_flip_extension_has_expected_order"
            )
            is True
            and full_exposure_radical_gate_stabilizer_lift_derived.get(
                "graph_action_lift_summary", {}
            ).get("graph_action_lift_order")
            == 393216
        ),
        "full_exposure_radical_gate_stabilizer_lift_classifies_label_breaking": (
            full_exposure_radical_gate_stabilizer_lift.get("checks", {}).get(
                "combined_gamma_marker_reduces_canonical_lift_to_six"
            )
            is True
            and full_exposure_radical_gate_stabilizer_lift.get("checks", {}).get(
                "charge_frame_and_fine_spectral_labels_reduce_to_identity"
            )
            is True
            and full_exposure_radical_gate_stabilizer_lift.get("checks", {}).get(
                "packet239_is_the_unique_zero_pair_touched_packet"
            )
            is True
        ),
        "full_exposure_label_breaking_factorization_is_certified": (
            full_exposure_label_breaking_factorization_certified
        ),
        "full_exposure_label_breaking_factorization_has_expected_axis_counts": (
            full_exposure_label_breaking_factorization.get("checks", {}).get(
                "axis_family_counts_match_expected_factorization"
            )
            is True
            and full_exposure_label_breaking_factorization_derived.get(
                "breaker_summary", {}
            ).get("axis_family_survivor_counts")
            == {
                "mass": 2,
                "clock": 48,
                "gamma": 24,
                "sector26": 1,
                "spectral": 2,
            }
        ),
        "full_exposure_label_breaking_factorization_identifies_minimal_breakers": (
            full_exposure_label_breaking_factorization.get("checks", {}).get(
                "minimal_axis_identity_sets_are_exact"
            )
            is True
            and full_exposure_label_breaking_factorization.get("checks", {}).get(
                "minimal_atomic_identity_sets_are_exact"
            )
            is True
            and full_exposure_label_breaking_factorization.get("checks", {}).get(
                "atomic_counts_identify_true_single_label_breakers"
            )
            is True
        ),
        "full_exposure_canonical_labelled_frame_is_certified": (
            full_exposure_canonical_labelled_frame_certified
        ),
        "full_exposure_canonical_labelled_frame_is_identity_rigid": (
            full_exposure_canonical_labelled_frame.get("checks", {}).get(
                "canonical_frame_key_is_injective"
            )
            is True
            and full_exposure_canonical_labelled_frame.get("checks", {}).get(
                "minimal_breaker_frame_has_identity_stabilizer"
            )
            is True
            and full_exposure_canonical_labelled_frame_derived.get(
                "canonical_frame_summary", {}
            ).get("frame_key_count")
            == 20
        ),
        "full_exposure_canonical_labelled_frame_selects_packet239_intrinsically": (
            full_exposure_canonical_labelled_frame.get("checks", {}).get(
                "zero_pair_rule_selects_packet239_intrinsically"
            )
            is True
            and full_exposure_canonical_labelled_frame.get("checks", {}).get(
                "selection_rule_is_id_free"
            )
            is True
            and full_exposure_canonical_labelled_frame_derived.get(
                "packet239_selection", {}
            ).get("selected_packet_ids")
            == [239]
        ),
        "full_exposure_label_coordinate_transition_operator_is_certified": (
            full_exposure_label_coordinate_transition_operator_certified
        ),
        "full_exposure_label_coordinate_transition_operator_has_expected_blocks": (
            full_exposure_label_coordinate_transition_operator.get("checks", {}).get(
                "label_operator_has_expected_weight_profile"
            )
            is True
            and full_exposure_label_coordinate_transition_operator.get("checks", {}).get(
                "label_operator_has_ten_uniform_doublet_blocks"
            )
            is True
            and full_exposure_label_coordinate_transition_operator_derived.get(
                "transition_summary", {}
            ).get("edge_kind_weight_histogram")
            == {"active_partner|4": 20, "source_loop|2": 20}
        ),
        "full_exposure_label_coordinate_transition_operator_identifies_zero_pair_transition": (
            full_exposure_label_coordinate_transition_operator.get("checks", {}).get(
                "zero_pair_coordinate_transitions_are_identified"
            )
            is True
            and full_exposure_label_coordinate_transition_operator_derived.get(
                "zero_pair_target_weights", {}
            ).get("active_partner", {})
            .get("witness_target_packet_id")
            == 238
            and full_exposure_label_coordinate_transition_operator_derived.get(
                "zero_pair_target_weights", {}
            ).get("source_loop", {})
            .get("witness_target_packet_id")
            == 239
        ),
        "full_exposure_label_coordinate_spectral_boundary_is_certified": (
            full_exposure_label_coordinate_spectral_boundary_certified
        ),
        "full_exposure_label_coordinate_spectral_boundary_diagonalizes_operator": (
            full_exposure_label_coordinate_spectral_boundary.get("checks", {}).get(
                "spectra_match_ten_uniform_doublets"
            )
            is True
            and full_exposure_label_coordinate_spectral_boundary_derived.get(
                "global_spectrum", {}
            ).get("adjacency_eigenvalue_histogram")
            == {"-2": 10, "6": 10}
        ),
        "full_exposure_label_coordinate_spectral_boundary_rejects_zero_pair_eigenboundary": (
            full_exposure_label_coordinate_spectral_boundary.get("checks", {}).get(
                "zero_pair_delta_is_not_an_eigenvector_or_left_eigenfunctional"
            )
            is True
            and full_exposure_label_coordinate_spectral_boundary.get("checks", {}).get(
                "zero_pair_singleton_dirichlet_spectrum_is_not_unique"
            )
            is True
            and full_exposure_label_coordinate_spectral_boundary.get("checks", {}).get(
                "zero_pair_component_dirichlet_spectrum_is_not_unique"
            )
            is True
        ),
        "full_exposure_label_coordinate_green_response_is_certified": (
            full_exposure_label_coordinate_green_response_certified
        ),
        "full_exposure_label_coordinate_green_response_resolves_zero_pair_source": (
            full_exposure_label_coordinate_green_response.get("checks", {}).get(
                "zero_pair_source_is_unique_and_targets_packet238"
            )
            is True
            and full_exposure_label_coordinate_green_response.get("checks", {}).get(
                "zero_pair_response_has_two_coordinate_support"
            )
            is True
            and full_exposure_label_coordinate_green_response_derived.get(
                "zero_pair_source_response", {}
            ).get("support_witness_packet_ids")
            == [239, 238]
        ),
        "full_exposure_label_coordinate_green_response_identities_hold_exactly": (
            full_exposure_label_coordinate_green_response.get("checks", {}).get(
                "adjacency_resolvent_identity_holds_exactly"
            )
            is True
            and full_exposure_label_coordinate_green_response.get("checks", {}).get(
                "markov_resolvent_identity_holds_exactly"
            )
            is True
            and full_exposure_label_coordinate_green_response.get("checks", {}).get(
                "massive_laplacian_green_identity_holds_exactly"
            )
            is True
        ),
        "full_exposure_label_coordinate_green_response_is_label_specific_not_operator_unique": (
            full_exposure_label_coordinate_green_response.get("checks", {}).get(
                "all_sources_have_same_analytic_response_profile"
            )
            is True
            and full_exposure_label_coordinate_green_response.get("checks", {}).get(
                "zero_pair_response_profile_is_not_operator_unique"
            )
            is True
        ),
        "full_exposure_zero_pair_propagator_charge_kernel_is_certified": (
            full_exposure_zero_pair_propagator_charge_kernel_certified
        ),
        "full_exposure_zero_pair_propagator_charge_kernel_has_expected_support_axes": (
            full_exposure_zero_pair_propagator_charge_kernel.get("checks", {}).get(
                "support_has_shared_propagator_axes"
            )
            is True
            and full_exposure_zero_pair_propagator_charge_kernel.get("checks", {}).get(
                "support_is_same_radical_full_exposure_pair"
            )
            is True
            and full_exposure_zero_pair_propagator_charge_kernel_derived.get(
                "propagator_charge_kernel_summary", {}
            ).get("support_packet_ids")
            == [239, 238]
        ),
        "full_exposure_zero_pair_propagator_charge_kernel_clears_sector26_denominator": (
            full_exposure_zero_pair_propagator_charge_kernel.get("checks", {}).get(
                "raw_half_residues_are_recorded_as_non_native_z26_classes"
            )
            is True
            and full_exposure_zero_pair_propagator_charge_kernel.get("checks", {}).get(
                "denominator_cleared_sector26_images_are_integral_and_complementary"
            )
            is True
            and full_exposure_zero_pair_propagator_charge_kernel_derived.get(
                "propagator_charge_kernel_summary", {}
            ).get("plus_denominator_cleared_sector26_image")
            == {
                "sector26_clock_delta_mod26": 8,
                "sector26_clock_pair_mod26": [24, 6],
                "sector26_clock_sum_mod26": 4,
            }
            and full_exposure_zero_pair_propagator_charge_kernel_derived.get(
                "propagator_charge_kernel_summary", {}
            ).get("minus_denominator_cleared_sector26_image")
            == {
                "sector26_clock_delta_mod26": 18,
                "sector26_clock_pair_mod26": [2, 20],
                "sector26_clock_sum_mod26": 22,
            }
        ),
        "full_exposure_zero_pair_propagator_symmetry_ward_is_certified": (
            full_exposure_zero_pair_propagator_symmetry_ward_certified
        ),
        "full_exposure_zero_pair_propagator_symmetry_ward_has_identity_invariance": (
            full_exposure_zero_pair_propagator_symmetry_ward.get("checks", {}).get(
                "surviving_label_preserving_symmetry_is_identity"
            )
            is True
            and full_exposure_zero_pair_propagator_symmetry_ward.get("checks", {}).get(
                "kernel_is_fixed_by_surviving_label_symmetry"
            )
            is True
            and full_exposure_zero_pair_propagator_symmetry_ward_derived.get(
                "symmetry_summary", {}
            ).get("surviving_label_preserving_symmetry_order")
            == 1
        ),
        "full_exposure_zero_pair_propagator_symmetry_ward_is_packet_source_compatible": (
            full_exposure_zero_pair_propagator_symmetry_ward.get("checks", {}).get(
                "individual_kernel_residues_are_not_closed_return_ward_characters"
            )
            is True
            and full_exposure_zero_pair_propagator_symmetry_ward.get("checks", {}).get(
                "paired_kernel_residue_is_sector26_neutral"
            )
            is True
            and full_exposure_zero_pair_propagator_symmetry_ward.get("checks", {}).get(
                "public_flux_balance_context_is_rank_zero"
            )
            is True
            and full_exposure_zero_pair_propagator_symmetry_ward_derived.get(
                "compatibility_matrix", {}
            ).get("needs_source_to_closed_return_coupling_for_stronger_claim")
            is True
        ),
        "full_exposure_zero_pair_source_to_closed_return_coupling_is_certified": (
            full_exposure_zero_pair_source_to_closed_return_coupling_certified
        ),
        "full_exposure_zero_pair_source_to_closed_return_coupling_proves_individual_no_go": (
            full_exposure_zero_pair_source_to_closed_return_coupling.get("checks", {}).get(
                "individual_plus_minus_couplings_are_impossible"
            )
            is True
            and full_exposure_zero_pair_source_to_closed_return_coupling_derived.get(
                "coupling_summary", {}
            ).get("ward_character_image")
            == [0, 13]
            and full_exposure_zero_pair_source_to_closed_return_coupling_derived.get(
                "source_to_closed_return_coupling_matrix", {}
            ).get("individual_plus_source")
            == "no Ward-character-preserving target"
            and full_exposure_zero_pair_source_to_closed_return_coupling_derived.get(
                "source_to_closed_return_coupling_matrix", {}
            ).get("individual_minus_source")
            == "no Ward-character-preserving target"
        ),
        "full_exposure_zero_pair_source_to_closed_return_coupling_selects_only_trivial_neutral_map": (
            full_exposure_zero_pair_source_to_closed_return_coupling.get("checks", {}).get(
                "canonical_neutral_coupling_maps_to_ward_kernel"
            )
            is True
            and full_exposure_zero_pair_source_to_closed_return_coupling.get("checks", {}).get(
                "nontrivial_neutral_coupling_is_not_selected_by_current_invariants"
            )
            is True
            and full_exposure_zero_pair_source_to_closed_return_coupling_derived.get(
                "coupling_summary", {}
            )
            .get("canonical_trivial_coupling", {})
            .get("closed_return_mask")
            == 0
            and full_exposure_zero_pair_source_to_closed_return_coupling_derived.get(
                "coupling_summary", {}
            ).get("ward_kernel_size")
            == 1024
        ),
        "full_exposure_zero_pair_ward_kernel_height_selector_is_certified": (
            full_exposure_zero_pair_ward_kernel_height_selector_certified
        ),
        "full_exposure_zero_pair_ward_kernel_height_selector_selects_mask288": (
            full_exposure_zero_pair_ward_kernel_height_selector.get("checks", {}).get(
                "selector_has_unique_minimum_positive_kernel_action"
            )
            is True
            and full_exposure_zero_pair_ward_kernel_height_selector.get("checks", {}).get(
                "selected_mask_is_nonzero_ward_kernel_mask"
            )
            is True
            and full_exposure_zero_pair_ward_kernel_height_selector_derived.get(
                "selector_summary", {}
            ).get("selected_mask")
            == 288
            and full_exposure_zero_pair_ward_kernel_height_selector_derived.get(
                "selector_summary", {}
            ).get("selected_height_action")
            == 1065984
        ),
        "full_exposure_zero_pair_ward_kernel_height_selector_lifts_paired_source_nontrivially": (
            full_exposure_zero_pair_ward_kernel_height_selector.get("checks", {}).get(
                "selected_mask_is_nontrivial_sourced_ward_lift"
            )
            is True
            and full_exposure_zero_pair_ward_kernel_height_selector.get("checks", {}).get(
                "individual_source_no_go_remains_in_force"
            )
            is True
            and full_exposure_zero_pair_ward_kernel_height_selector_derived.get(
                "selector_summary", {}
            )
            .get("source_lift", {})
            .get("height_selected_nontrivial_mask")
            == 288
        ),
        "full_exposure_zero_pair_selected_sourced_ward_balance_is_certified": (
            full_exposure_zero_pair_selected_sourced_ward_balance_certified
        ),
        "full_exposure_zero_pair_selected_sourced_ward_balance_uses_mask288": (
            full_exposure_zero_pair_selected_sourced_ward_balance.get("checks", {}).get(
                "selector_selects_mask288"
            )
            is True
            and full_exposure_zero_pair_selected_sourced_ward_balance.get("checks", {}).get(
                "selected_balance_is_first_nontrivial_sourced_target"
            )
            is True
            and full_exposure_zero_pair_selected_sourced_ward_balance_derived.get(
                "sourced_balance_summary", {}
            ).get("selected_mask")
            == 288
        ),
        "full_exposure_zero_pair_selected_sourced_ward_balance_closes_public_and_hidden_terms": (
            full_exposure_zero_pair_selected_sourced_ward_balance.get("checks", {}).get(
                "selected_bms_row_closes_public_balance"
            )
            is True
            and full_exposure_zero_pair_selected_sourced_ward_balance.get("checks", {}).get(
                "selected_bms_row_closes_hidden_balance"
            )
            is True
            and full_exposure_zero_pair_selected_sourced_ward_balance_derived.get(
                "sourced_balance_summary", {}
            )
            .get("selected_hidden_terms", {})
            .get("hidden_balance_error")
            == 0
        ),
        "full_exposure_zero_pair_selected_sourced_ward_balance_is_scattering_realized": (
            full_exposure_zero_pair_selected_sourced_ward_balance.get("checks", {}).get(
                "gamma8_to_selected_scattering_step_is_generator5"
            )
            is True
            and full_exposure_zero_pair_selected_sourced_ward_balance.get("checks", {}).get(
                "selected_to_gamma8_reverse_scattering_step_is_generator5"
            )
            is True
            and full_exposure_zero_pair_selected_sourced_ward_balance_derived.get(
                "sourced_balance_summary", {}
            )
            .get("scattering_step", {})
            .get("generator_cycle_id")
            == 5
        ),
        "full_exposure_zero_pair_sourced_balance_cone_is_certified": (
            full_exposure_zero_pair_sourced_balance_cone_certified
        ),
        "full_exposure_zero_pair_sourced_balance_cone_classifies_gamma8_star": (
            full_exposure_zero_pair_sourced_balance_cone.get("checks", {}).get(
                "gamma8_star_has_expected_kernel_and_odd_targets"
            )
            is True
            and full_exposure_zero_pair_sourced_balance_cone.get("checks", {}).get(
                "height_ordered_kernel_targets_are_all_balanced"
            )
            is True
            and full_exposure_zero_pair_sourced_balance_cone_derived.get(
                "cone_summary", {}
            ).get("nonzero_kernel_target_count")
            == 9
        ),
        "full_exposure_zero_pair_sourced_balance_cone_keeps_mask288_as_height_apex": (
            full_exposure_zero_pair_sourced_balance_cone.get("checks", {}).get(
                "mask288_is_unique_nonzero_height_apex"
            )
            is True
            and full_exposure_zero_pair_sourced_balance_cone_derived.get(
                "cone_summary", {}
            )
            .get("height_apex", {})
            .get("mask")
            == 288
            and full_exposure_zero_pair_sourced_balance_cone_derived.get(
                "cone_summary", {}
            )
            .get("height_apex", {})
            .get("height_gap_to_next")
            == 82944
        ),
        "full_exposure_zero_pair_sourced_balance_cone_rejects_single_apex_algebraic_generation": (
            full_exposure_zero_pair_sourced_balance_cone.get("checks", {}).get(
                "mask288_does_not_generate_target_set_as_f2_span"
            )
            is True
            and full_exposure_zero_pair_sourced_balance_cone.get("checks", {}).get(
                "mask288_has_only_generator3_one_step_kernel_preserving_exit"
            )
            is True
            and full_exposure_zero_pair_sourced_balance_cone_derived.get(
                "cone_summary", {}
            ).get("apex_f2_span")
            == [0, 288]
        ),
        "full_exposure_zero_pair_sourced_balance_shortest_paths_is_certified": (
            full_exposure_zero_pair_sourced_balance_shortest_paths_certified
        ),
        "full_exposure_zero_pair_sourced_balance_shortest_paths_cover_all_nonzero_kernel_masks": (
            full_exposure_zero_pair_sourced_balance_shortest_paths.get("checks", {}).get(
                "all_nonzero_ward_kernel_masks_are_covered"
            )
            is True
            and full_exposure_zero_pair_sourced_balance_shortest_paths.get("checks", {}).get(
                "all_shortest_path_witnesses_end_at_target"
            )
            is True
            and full_exposure_zero_pair_sourced_balance_shortest_paths_derived.get(
                "shortest_path_summary", {}
            ).get("target_count")
            == 1023
        ),
        "full_exposure_zero_pair_sourced_balance_shortest_paths_close_all_target_balances": (
            full_exposure_zero_pair_sourced_balance_shortest_paths.get("checks", {}).get(
                "all_targets_close_public_and_hidden_balance"
            )
            is True
            and full_exposure_zero_pair_sourced_balance_shortest_paths.get("checks", {}).get(
                "all_paths_transfer_odd_source_to_kernel_clock"
            )
            is True
            and full_exposure_zero_pair_sourced_balance_shortest_paths.get("checks", {}).get(
                "all_signed_height_deltas_match_target_minus_source"
            )
            is True
        ),
        "full_exposure_zero_pair_sourced_balance_shortest_paths_keep_mask288_minimum": (
            full_exposure_zero_pair_sourced_balance_shortest_paths.get("checks", {}).get(
                "mask288_remains_unique_shortest_path_action_apex"
            )
            is True
            and full_exposure_zero_pair_sourced_balance_shortest_paths_derived.get(
                "shortest_path_summary", {}
            )
            .get("unique_minimum_path", {})
            .get("target_mask")
            == 288
            and full_exposure_zero_pair_sourced_balance_shortest_paths_derived.get(
                "shortest_path_summary", {}
            )
            .get("unique_minimum_path", {})
            .get("shortest_path_action")
            == 691200
        ),
        "full_exposure_zero_pair_sourced_balance_transport_families_is_certified": (
            full_exposure_zero_pair_sourced_balance_transport_families_certified
        ),
        "full_exposure_zero_pair_sourced_balance_transport_families_compress_scalar_data": (
            full_exposure_zero_pair_sourced_balance_transport_families.get("checks", {}).get(
                "path_and_height_scalar_families_have_805_values"
            )
            is True
            and full_exposure_zero_pair_sourced_balance_transport_families.get("checks", {}).get(
                "full_transport_signature_compresses_to_991_families"
            )
            is True
            and full_exposure_zero_pair_sourced_balance_transport_families_derived.get(
                "transport_family_summary", {}
            ).get("transport_signature_family_count")
            == 991
        ),
        "full_exposure_zero_pair_sourced_balance_transport_families_resolve_symmetry_levels": (
            full_exposure_zero_pair_sourced_balance_transport_families.get("checks", {}).get(
                "hidden_split_c2_compresses_targets_but_breaks_action_height_labels"
            )
            is True
            and full_exposure_zero_pair_sourced_balance_transport_families.get("checks", {}).get(
                "full_augmented_ledger_symmetry_compression_is_identity"
            )
            is True
            and full_exposure_zero_pair_sourced_balance_transport_families_derived.get(
                "transport_family_summary", {}
            ).get("full_augmented_ledger_stabilizer_order")
            == 1
        ),
        "full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient_is_certified": (
            full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient_certified
        ),
        "full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient_identifies_c2": (
            full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient.get(
                "checks", {}
            ).get("source_and_kernel_target_preserving_group_is_hidden_split_c2")
            is True
            and full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient.get(
                "checks", {}
            ).get("hidden_split_c2_quotient_has_543_kernel_target_orbits")
            is True
            and full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient_derived.get(
                "label_relaxation_summary", {}
            ).get("hidden_split_c2_orbit_count")
            == 543
        ),
        "full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient_names_forgotten_labels": (
            full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient.get(
                "checks", {}
            ).get(
                "hidden_split_c2_forgets_target_support_step_action_height_and_fourier_refinements"
            )
            is True
            and full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient.get(
                "checks", {}
            ).get("nonidentity_c2_requires_forgetting_six_augmented_ledger_axes")
            is True
            and full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient_derived.get(
                "public_level_summary", {}
            ).get("full_public_orbit_count")
            == 45
        ),
        "full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly_is_certified": (
            full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly_certified
        ),
        "full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly_is_exact": (
            full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly.get("checks", {}).get(
                "tau_cocycle_law_holds_for_action_and_height"
            )
            is True
            and full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly.get(
                "checks", {}
            ).get("path_action_and_target_height_have_the_same_c2_cocycle")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly.get(
                "checks", {}
            ).get("representative_counterterm_is_exact_coboundary_for_action_and_height")
            is True
        ),
        "full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly_descends_balance": (
            full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly.get("checks", {}).get(
                "twisted_quotient_hidden_balance_descends_on_every_target"
            )
            is True
            and full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly.get(
                "checks", {}
            ).get("public_balance_descends_without_extra_anomaly")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly_derived.get(
                "anomaly_summary", {}
            ).get("nonzero_anomaly_orbit_count")
            == 472
        ),
        "full_exposure_zero_pair_sourced_balance_c2_quotient_transport_ledger_is_certified": (
            full_exposure_zero_pair_sourced_balance_c2_quotient_transport_ledger_certified
        ),
        "full_exposure_zero_pair_sourced_balance_c2_quotient_transport_ledger_identifies_primal_operator": (
            full_exposure_zero_pair_sourced_balance_c2_quotient_transport_ledger.get(
                "checks", {}
            ).get("primal_operator_is_the_nonidentity_hidden_split_c2")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_quotient_transport_ledger.get(
                "checks", {}
            ).get("gamma8_is_fixed_source_anchor_not_the_quotient_anomaly")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_quotient_transport_ledger_derived.get(
                "operator_summary", {}
            ).get("quotient_anomaly_is_gamma8")
            is False
        ),
        "full_exposure_zero_pair_sourced_balance_c2_quotient_transport_ledger_is_markov_spectral_balanced": (
            full_exposure_zero_pair_sourced_balance_c2_quotient_transport_ledger.get(
                "checks", {}
            ).get("primal_operator_is_a_permutation_markov_operator")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_quotient_transport_ledger.get(
                "checks", {}
            ).get("orbit_projection_is_markov_and_idempotent")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_quotient_transport_ledger.get(
                "checks", {}
            ).get("quotient_ledger_is_ward_balanced")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_quotient_transport_ledger_derived.get(
                "operator_summary", {}
            ).get("orbit_count")
            == 543
        ),
        "full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator_is_certified": (
            full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator_certified
        ),
        "full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator_has_canonical_move_orbit": (
            full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator.get(
                "checks", {}
            ).get("move_set_is_c2_closed_and_kernel_preserving")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator.get(
                "checks", {}
            ).get("move_set_contains_generator3_and_tau_image_composite")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator_derived.get(
                "operator_summary", {}
            ).get("move_set_delta_masks")
            == [8, 1034]
        ),
        "full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator_is_markov_spectral_stationary": (
            full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator.get(
                "checks", {}
            ).get("operator_is_markov_on_every_quotient_orbit")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator.get(
                "checks", {}
            ).get("spectrum_matches_component_normal_forms")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator.get(
                "checks", {}
            ).get("stationary_data_is_ward_balanced")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator_derived.get(
                "operator_summary", {}
            ).get("component_count")
            == 144
        ),
        "full_exposure_zero_pair_sourced_balance_c2_move_orbit_family_is_certified": (
            full_exposure_zero_pair_sourced_balance_c2_move_orbit_family_certified
        ),
        "full_exposure_zero_pair_sourced_balance_c2_move_orbit_family_classifies_all_hidden_neutral_moves": (
            full_exposure_zero_pair_sourced_balance_c2_move_orbit_family.get(
                "checks", {}
            ).get("all_c2_hidden_neutral_move_orbits_are_classified")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_move_orbit_family_derived.get(
                "family_summary", {}
            ).get("move_orbit_count")
            == 543
            and full_exposure_zero_pair_sourced_balance_c2_move_orbit_family_derived.get(
                "family_summary", {}
            ).get("fixed_move_orbit_count")
            == 63
            and full_exposure_zero_pair_sourced_balance_c2_move_orbit_family_derived.get(
                "family_summary", {}
            ).get("paired_move_orbit_count")
            == 480
        ),
        "full_exposure_zero_pair_sourced_balance_c2_move_orbit_family_is_markov_spectral_stationary": (
            full_exposure_zero_pair_sourced_balance_c2_move_orbit_family.get(
                "checks", {}
            ).get("all_move_orbits_are_hidden_neutral_and_markov_symmetric")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_move_orbit_family.get(
                "checks", {}
            ).get("every_family_member_is_stationary_ward_balanced")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_move_orbit_family.get(
                "checks", {}
            ).get("operator_family_has_three_component_types")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_move_orbit_family.get(
                "checks", {}
            ).get("operator_family_has_three_spectrum_types")
            is True
        ),
        "full_exposure_zero_pair_sourced_balance_c2_move_orbit_family_separates_primitive_canonical_from_action_minimal": (
            full_exposure_zero_pair_sourced_balance_c2_move_orbit_family.get(
                "checks", {}
            ).get("primitive_seeded_operator_is_unique_and_matches_prior_scattering_operator")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_move_orbit_family.get(
                "checks", {}
            ).get("primitive_seeded_operator_is_not_global_action_minimum")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_move_orbit_family.get(
                "checks", {}
            ).get("paired_action_minimum_is_not_the_primitive_seeded_operator")
            is True
        ),
        "full_exposure_zero_pair_sourced_balance_c2_dynamics_selector_is_certified": (
            full_exposure_zero_pair_sourced_balance_c2_dynamics_selector_certified
        ),
        "full_exposure_zero_pair_sourced_balance_c2_dynamics_selector_splits_natural_criteria": (
            full_exposure_zero_pair_sourced_balance_c2_dynamics_selector.get(
                "checks", {}
            ).get("primitive_seeded_selector_is_unique_prior_operator")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_dynamics_selector.get(
                "checks", {}
            ).get("global_action_selector_is_unique_fixed_minimum")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_dynamics_selector.get(
                "checks", {}
            ).get("paired_action_selector_is_unique_paired_minimum")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_dynamics_selector.get(
                "checks", {}
            ).get("selection_criteria_are_not_equivalent")
            is True
        ),
        "full_exposure_zero_pair_sourced_balance_c2_dynamics_selector_spectral_gap_is_explicit": (
            full_exposure_zero_pair_sourced_balance_c2_dynamics_selector.get(
                "checks", {}
            ).get("raw_absolute_gap_is_degenerate_on_entire_family")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_dynamics_selector.get(
                "checks", {}
            ).get("lazy_gap_selects_exactly_fixed_singleton_family")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_dynamics_selector.get(
                "checks", {}
            ).get("lazy_gap_action_tiebreak_is_global_action_minimum")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_dynamics_selector.get(
                "checks", {}
            ).get("paired_lazy_gap_action_tiebreak_is_paired_action_minimum")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_dynamics_selector_derived.get(
                "selector_summary", {}
            ).get("lazy_spectral_gap_selected_count")
            == 63
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_skeleton_is_certified": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_skeleton_certified
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_skeleton_typecheck_artifact_present": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_skeleton.get(
                "checks", {}
            ).get("agda_source_exists_and_is_cubical_safe")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_skeleton.get(
                "checks", {}
            ).get("agda_source_imports_cubical_library")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_skeleton.get(
                "checks", {}
            ).get("agda_interface_artifact_present_after_typecheck")
            is True
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_skeleton_names_core_uf_interface": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_skeleton.get(
                "checks", {}
            ).get("agda_source_names_core_hit_and_universe_records")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_skeleton.get(
                "checks", {}
            ).get("agda_source_embeds_bridge_counts")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_skeleton.get(
                "checks", {}
            ).get("agda_source_proves_contractible_singleton_fibers")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_skeleton_derived.get(
                "source_summary", {}
            ).get("module")
            == "C2SelectorFoundation"
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_is_certified": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_certified
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_names_all_states_and_dynamics": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration.get(
                "checks", {}
            ).get("generated_source_has_all_quotient_state_constructors")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration.get(
                "checks", {}
            ).get("generated_source_has_all_dynamics_constructors")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration.get(
                "checks", {}
            ).get("generated_source_has_all_dynamics_code_rows")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_derived.get(
                "source_summary", {}
            )
            .get("constructor_counts", {})
            .get("quotient_state")
            == 543
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_derived.get(
                "source_summary", {}
            )
            .get("constructor_counts", {})
            .get("dynamics")
            == 543
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_names_all_selector_memberships": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration.get(
                "checks", {}
            ).get("generated_source_has_all_selector_memberships")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration.get(
                "checks", {}
            ).get("generated_source_has_expected_selector_fiber_counts")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration.get(
                "checks", {}
            ).get("generated_agda_interface_artifact_present_after_typecheck")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_derived.get(
                "expected_selector_membership_count"
            )
            == 1091
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_properties_is_certified": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_properties_certified
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_properties_have_counts_and_eliminators": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_properties.get(
                "checks", {}
            ).get("properties_source_has_counting_lemmas")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_properties.get(
                "checks", {}
            ).get("properties_source_has_exhaustive_eliminators")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_properties_derived.get(
                "source_summary", {}
            )
            .get("proof_counts", {})
            .get("quotient_state_elim_clauses")
            == 543
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_properties_derived.get(
                "source_summary", {}
            )
            .get("proof_counts", {})
            .get("dynamics_elim_clauses")
            == 543
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_properties_have_decidable_equality": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_properties.get(
                "checks", {}
            ).get("properties_source_has_id_roundtrips")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_properties.get(
                "checks", {}
            ).get("properties_source_has_decidable_equality_and_set_witnesses")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_properties.get(
                "checks", {}
            ).get("properties_agda_interface_artifact_present_after_typecheck")
            is True
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_membership_is_certified": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_membership_certified
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_membership_decision_is_total": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_membership.get(
                "checks", {}
            ).get("selector_membership_decision_function_is_total_over_selectors_and_dynamics")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_membership_derived.get(
                "source_summary", {}
            )
            .get("decision_counts", {})
            .get("decision_clause_count")
            == 4344
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_membership_counts_match_fibers": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_membership.get(
                "checks", {}
            ).get("selector_membership_decision_yes_no_counts_match_fibers")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_membership_derived.get(
                "source_summary", {}
            )
            .get("decision_counts", {})
            .get("yes_clause_count")
            == 1091
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_membership_derived.get(
                "source_summary", {}
            )
            .get("decision_counts", {})
            .get("no_clause_count")
            == 3253
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_membership_has_all_fiber_proofs": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_membership.get(
                "checks", {}
            ).get("selector_membership_source_has_all_fiber_count_proofs")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_membership.get(
                "checks", {}
            ).get("selector_membership_agda_interface_artifact_present_after_typecheck")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_membership_derived.get(
                "source_summary", {}
            )
            .get("decision_counts", {})
            .get("fiber_count_proof_count")
            == 8
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_singletons_is_certified": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_singletons_certified
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_singletons_are_fin1": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_singletons.get(
                "checks", {}
            ).get("singleton_source_has_all_five_iso_witnesses")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_singletons.get(
                "checks", {}
            ).get("singleton_agda_interface_artifact_present_after_typecheck")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_singletons_derived.get(
                "source_summary", {}
            )
            .get("proof_counts", {})
            .get("fin_equivalence_count")
            == 5
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lazy63_is_certified": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lazy63_certified
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lazy63_is_fin63": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lazy63.get(
                "checks", {}
            ).get("lazy_source_has_exact_63_fiber_witnesses")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lazy63.get(
                "checks", {}
            ).get("lazy63_agda_interface_artifact_present_after_typecheck")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lazy63_derived.get(
                "source_summary", {}
            )
            .get("proof_counts", {})
            .get("fin_equivalence_count")
            == 1
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lazy63_derived.get(
                "lazy_selector", {}
            ).get("selected_count")
            == 63
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_paired_lazy480_is_certified": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_paired_lazy480_certified
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_paired_lazy480_is_fin480": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_paired_lazy480.get(
                "checks", {}
            ).get("paired_lazy_source_has_exact_480_fiber_witnesses")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_paired_lazy480.get(
                "checks", {}
            ).get("paired_lazy480_agda_interface_artifact_present_after_typecheck")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_paired_lazy480_derived.get(
                "source_summary", {}
            )
            .get("proof_counts", {})
            .get("fin_equivalence_count")
            == 1
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_paired_lazy480_derived.get(
                "paired_lazy_selector", {}
            ).get("selected_count")
            == 480
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_is_certified": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_certified
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_is_fin543": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543.get(
                "checks", {}
            ).get("raw_source_has_exact_543_fiber_witnesses")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543.get(
                "checks", {}
            ).get("raw543_agda_interface_artifact_present_after_typecheck")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_derived.get(
                "source_summary", {}
            )
            .get("proof_counts", {})
            .get("fin_equivalence_count")
            == 1
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_derived.get(
                "raw_selector", {}
            ).get("selected_count")
            == 543
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_non_singleton_spine_uses_actual_c2_kernel_orbits": (
            RAW543_ACTUAL_C2_KERNEL_ORBITS_CSV.exists()
            and all(
                source.get("raw543_orbit_count") == 543
                and source.get("fixed63_orbit_count") == 63
                and source.get("paired480_two_cycle_orbit_count") == 480
                for source in actual_c2_kernel_orbit_sources.values()
            )
            and all(
                source.get("path") == str(RAW543_ACTUAL_C2_KERNEL_ORBITS_CSV)
                for source in actual_c2_kernel_orbit_source_consumers.values()
            )
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_emitter_factorization_is_certified": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_emitter_factorization_certified
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_emitter_factorization_preserves_sources": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_emitter_factorization.get(
                "checks", {}
            ).get("shared_emitter_reproduces_certified_agda_sources")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_emitter_factorization.get(
                "checks", {}
            ).get("all_agda_interfaces_remain_fresh")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_emitter_factorization_derived.get(
                "factorized_generator_count"
            )
            == 4
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_indexed_is_certified": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_indexed_certified
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_indexed_is_compact_fin543": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_indexed.get(
                "checks", {}
            ).get("indexed_source_has_fin543_equivalence")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_indexed.get(
                "checks", {}
            ).get("indexed_source_has_no_fd_suc_constructor_normal_forms")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_indexed.get(
                "checks", {}
            ).get("indexed_source_is_smaller_than_direct_raw543_source")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_indexed.get(
                "checks", {}
            ).get("raw543_indexed_agda_interface_artifact_present_after_typecheck")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_indexed_derived.get(
                "source_summary", {}
            )
            .get("proof_counts", {})
            .get("fin_equivalence_count")
            == 1
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_split_is_certified": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_split_certified
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_split_covers_lazy63_and_paired_lazy480": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_split.get(
                "checks", {}
            ).get("indexed_split_covers_lazy63_and_paired_lazy480")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_split.get(
                "checks", {}
            ).get("all_indexed_split_rows_certified")
            is True
            and indexed_split_row_by_name.get("lazy63", {})
            .get("selector", {})
            .get("selected_count")
            == 63
            and indexed_split_row_by_name.get("paired_lazy480", {})
            .get("selector", {})
            .get("selected_count")
            == 480
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_split_sources_have_no_fd_suc_constructor_normal_forms": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_split.get(
                "checks", {}
            ).get("all_indexed_split_sources_have_no_fd_suc_constructor_normal_forms")
            is True
            and all(
                row.get("source_summary", {})
                .get("compactness", {})
                .get("fd_suc_occurrence_count")
                == 0
                for row in indexed_split_rows
            )
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_lookup_is_certified": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_lookup_certified
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_lookup_covers_raw543_lazy63_and_paired_lazy480": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_lookup.get(
                "checks", {}
            ).get("lookup_covers_raw543_lazy63_and_paired_lazy480")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_lookup.get(
                "checks", {}
            ).get("all_lookup_rows_certified")
            is True
            and indexed_lookup_row_by_name.get("raw543", {})
            .get("selector", {})
            .get("selected_count")
            == 543
            and indexed_lookup_row_by_name.get("lazy63", {})
            .get("selector", {})
            .get("selected_count")
            == 63
            and indexed_lookup_row_by_name.get("paired_lazy480", {})
            .get("selector", {})
            .get("selected_count")
            == 480
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_lookup_collapses_right_inverse_rows": (
            all(
                row.get("source_summary", {})
                .get("compactness", {})
                .get("inspect_occurrence_count")
                == 0
                and row.get("source_summary", {})
                .get("compactness", {})
                .get("inj_to_nat_occurrence_count")
                == 0
                and row.get("source_summary", {})
                .get("compactness", {})
                .get("to_from_id_occurrence_count")
                == 0
                and row.get("source_summary", {})
                .get("compactness", {})
                .get("from_to_id_occurrence_count")
                == 1
                and row.get("source_summary", {})
                .get("proof_counts", {})
                .get("right_inverse_from_to_id_definition_count")
                == 1
                for row in indexed_lookup_rows
            )
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_lookup_sources_have_no_fd_suc_and_are_smaller": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_lookup.get(
                "checks", {}
            ).get("all_lookup_sources_have_no_fd_suc_constructor_normal_forms")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_lookup.get(
                "checks", {}
            ).get("all_lookup_sources_are_smaller_than_previous_indexed_sources")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_lookup.get(
                "checks", {}
            ).get("lookup_witness_table_source_is_halloween_package")
            is True
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table_is_certified": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table_certified
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table_has_1086_rows": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table.get(
                "checks", {}
            ).get("lookup_table_json_has_1086_rows")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table.get(
                "checks", {}
            ).get("lookup_table_csv_has_1086_rows")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table_derived.get(
                "lookup_table_row_count"
            )
            == 1086
            and lookup_table_row_count_by_selector == {"lazy63": 63, "paired_lazy480": 480, "raw543": 543}
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table_matches_lookup_sources": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table.get(
                "checks", {}
            ).get("lookup_table_rows_match_lookup_agda_sources")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table.get(
                "checks", {}
            ).get("lookup_table_selected_ids_match_actual_c2_kernel_order")
            is True
            and all(
                summary.get("all_exact_clauses_in_source") is True
                and summary.get("indices_are_contiguous") is True
                for summary in lookup_table_selector_summaries
            )
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table_soundness_agda_typechecked": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table.get(
                "checks", {}
            ).get("lookup_table_soundness_agda_interface_artifact_present_after_typecheck")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table.get(
                "checks", {}
            ).get("lookup_table_soundness_exports_three_fin_equivalences")
            is True
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table_source_package_verified": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table.get(
                "checks", {}
            ).get("lookup_source_package_standalone_verifier_passes")
            is True
            and full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table.get(
                "checks", {}
            ).get("lookup_source_package_uses_only_halloween_source_and_lookup_artifacts")
            is True
            and lookup_table_source_package_certificate.get("status")
            == "D20_C2_SELECTOR_LOOKUP_WITNESS_SOURCE_PACKAGE_VERIFIED"
            and lookup_table_source_package_certificate.get("all_checks_pass") is True
        ),
        "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table_source_package_registry_id_threaded": (
            full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table.get(
                "checks", {}
            ).get("lookup_source_package_registry_id_is_threaded")
            is True
            and lookup_table_source_package.get("source_registry_binding", {}).get(
                "all_checks_pass"
            )
            is True
        ),
        "character_table_only_hash_materialized": not character_values_materialized
        and character.get("character_table_sha256") is not None
        and character.get("shape") == [39, 985],
        "idempotent_matrix_only_hash_materialized": not idempotent_matrix_materialized
        and (
            idempotent_validation.get("embedded_idempotent_matrix_sha256") is not None
            or wedderburn_source.get("embedded_idempotent_matrix_sha256") is not None
        ),
        "complete_tube_section_coefficients_not_materialized": not complete_section_materialized
        and section.get("section_hash_root") is not None,
        "full_drinfeld_idempotent_matrix_still_hash_only": not idempotent_matrix_materialized,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_CYCLE8_PI33_FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LOOKUP_TABLE_CERTIFIED"
        if all_checks_pass
        else "D20_CYCLE8_PI33_PROJECTION_OBLIGATION_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.proof_obligation.cycle8_pi33_projection_coefficient.source_drop",
        "status": status,
        "closure_state": (
            "bare_lambda_zero; height_coherent_transport_recovers_nonzero_residual; "
            "sector33_unique_single_sector_public_zero_support; public_shadow_kernel_dimension_27; "
            "public_zero_idempotent_supports_classified; minimal_composite_superselection_transport_classified; "
            "augmented_flux_ledger_certified; typed_nonexact_optical_flux_update_certified; "
            "sector26_invariant_suite_certified; finite_anomaly_counter_certified; "
            "sector26_anomaly_cancellation_certified; anomaly_cancelled_flux_balance_recovery_certified; "
            "gamma8_obstruction_correction_certified; general_obstruction_correction_suite_certified"
            "; global_counterterm_lattice_certified; global_corrected_charge_map_certified; "
            "global_corrected_hidden_split_symmetry_certified; "
            "hidden_split_augmented_ledger_stabilizer_certified; canonical_flux_balance_gauge_certified; "
            "canonical_loop_pi33_obstruction_certified; canonical_finite_ward_identity_certified; "
            "canonical_all_mask_ward_identity_certified; finite_bms_carrollian_flux_balance_certified; "
            "hidden_packet_charge_frame_classifier_certified; canonical_finite_scattering_table_certified; "
            "loop297_scattering_amplitude_lift_certified; compact_amplitude_quotient_certified; "
            "reduced_amplitude_quotient_scattering_automaton_certified; "
            "amplitude_quotient_fourier_mode_classifier_certified; "
            "finite_virasoro_string_kernel_candidate_certified; "
            "finite_virasoro_generator_algebra_certified; "
            "finite_central_extension_anomaly_cocycle_certified; "
            "finite_parity_central_extension_group_certified; "
            "projective_kernel_packet_tenfold_way_certified; "
            "projective_packet_spectral_charge_table_certified; "
            "projective_packet_charge_frame_classifier_certified; "
            "packet239_stabilizer_seed_candidate_certified; "
            "packet239_seed_propagation_certified; "
            "full_exposure_packet_propagation_cells_certified; "
            "full_exposure_packet_propagation_graph_certified; "
            "full_exposure_rank10_tenfold_alignment_certified; "
            "full_exposure_radical_gate_stabilizer_certified; "
            "full_exposure_radical_gate_stabilizer_lift_certified; "
            "full_exposure_label_breaking_factorization_certified; "
            "full_exposure_canonical_labelled_frame_certified; "
            "full_exposure_label_coordinate_transition_operator_certified; "
            "full_exposure_label_coordinate_spectral_boundary_certified; "
            "full_exposure_label_coordinate_green_response_certified; "
            "full_exposure_zero_pair_propagator_charge_kernel_certified; "
            "full_exposure_zero_pair_propagator_symmetry_ward_certified; "
            "full_exposure_zero_pair_source_to_closed_return_coupling_certified; "
            "full_exposure_zero_pair_ward_kernel_height_selector_certified; "
            "full_exposure_zero_pair_selected_sourced_ward_balance_certified; "
            "full_exposure_zero_pair_sourced_balance_cone_certified; "
            "full_exposure_zero_pair_sourced_balance_shortest_paths_certified; "
            "full_exposure_zero_pair_sourced_balance_transport_families_certified; "
            "full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient_certified; "
            "full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly_certified; "
            "full_exposure_zero_pair_sourced_balance_c2_quotient_transport_ledger_certified; "
            "full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator_certified; "
            "full_exposure_zero_pair_sourced_balance_c2_move_orbit_family_certified; "
            "full_exposure_zero_pair_sourced_balance_c2_dynamics_selector_certified; "
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_skeleton_certified; "
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_certified; "
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_properties_certified; "
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_membership_certified; "
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_singletons_certified; "
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lazy63_certified; "
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_paired_lazy480_certified; "
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_certified; "
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_emitter_factorization_certified; "
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_indexed_certified; "
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_split_certified; "
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_lookup_certified; "
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table_certified"
        ),
        "object": "d20",
        "target": (
            "Compute c_33(gamma_8)=Pi_33(lambda_boundary(gamma_8)), where "
            "lambda_boundary maps D20 closed boundary chains into Loop_297."
        ),
        "claim": (
            "The boundary-to-Loop_297 lift for gamma_8 is certified, and the tube-visible Pi_33 functional "
            "has been reconstructed from the stored local pre-idempotents. For the bare lambda_boundary lift, "
            "c_33(gamma_8)=0. The refined height-coherent transport derives its scalar from the active edge "
            "circuit height action and recovers the sector-33 residual -374784 with zero A42/A12 public shadow. "
            "Materializing all 39 tube-visible sector idempotents proves that sector 33 is the unique "
            "single-sector public-zero support. The full linear public-zero sector span is also classified: "
            "the combined A42/A12 shadow matrix has rank 12 and kernel dimension 27, so Pi_33 uniqueness is "
            "coordinate-axis/single-sector uniqueness, not uniqueness in the unconstrained linear span. The "
            "idempotent support classification shows five nonzero public-zero boundary-null idempotent sector "
            "sums; Pi_33 is the unique primitive support and the unique support-exact support for the certified "
            "sector-33 height transport. The two minimal non-Pi_33 null composites are not gauge zero: "
            "{6,26} and {25,26} have positive self-transport and zero transport to/from Pi_33, so they are "
            "isolated public-zero superselection supports. The finite flux-balance ledger is extended with "
            "hidden components R33, K_mixed_S, and K_pure_Sminus so public-zero hidden transport is not "
            "collapsed into gauge zero. The non-exact optical/action update sends all certified nonzero "
            "height residuals to R33 while reserving K_mixed_S and K_pure_Sminus for separately certified "
            "superselection-null events. The sector-26 invariant suite now certifies the shared composite seam, "
            "stable A42/A12 quotient cancellation, hidden transport form diag-Smith data, and the complete "
            "mod-26 normalized optical residue clock. The finite anomaly-counter theorem proves that this "
            "mod-26 clock is not a linear xor character; its exact additivity defect is an even-valued "
            "sector-26 anomaly counter whose half hits all mod-13 classes while the mod-2 parity shadow "
            "remains the additive character. The anomaly-cancellation theorem classifies the cancelled "
            "closed-return packets: the maximal dimension is 3, there are 88 strongest size-8 packets and "
            "90 terminal size-4 packets, and gamma_8 is excluded by nonzero self half-anomaly. The "
            "anomaly-cancelled flux-balance recovery theorem then restricts the typed non-exact ledger to "
            "those packets: exact public flux closes and normalized R33 transport becomes additive modulo 26. "
            "The gamma_8 obstruction correction theorem identifies the unique local sector-26 counterterm: "
            "add +5 to normalized R33 on basis coordinate 8, sending gamma_8 to the order-two value 13. "
            "The general obstruction-correction suite proves this is one row of a full 11-coordinate table: "
            "every basis coordinate is self-anomalous and admits a rank-one correction. The global "
            "counterterm-lattice theorem activates all 11 corrections together, annihilates the full "
            "half-anomaly form, and makes normalized R33 an additive order-two character on all 2048 masks. "
            "The finite central-extension/anomaly cocycle theorem then separates the sector-26 clock "
            "nonlinearity from central charge: the canonical Z/26 defect is symmetric with zero alternating "
            "central term, while a unique compatible F2 parity cocycle survives on the paired cross-return "
            "composite triangle. The finite parity central-extension group theorem integrates that cocycle: "
            "the resulting group is D8 x C2^8, with the composite triangle as its exact named commutator "
            "support and a signed projective action on the 1024-state kernel. The projective kernel packet "
            "theorem decomposes that signed action into 512 two-dimensional central-negative packets, attaches "
            "sector-26 and Loop_297 exposure data, and records the finite tenfold-way witness: an 8+2 Bott "
            "split with canonical AI module structure and an optional BDI active-Clifford Hamiltonian readout. "
            "The packet spectral/charge table turns those packets into a 512-row ledger of spectral traces, "
            "sector-26 clocks, hidden-clock cancellation, gamma_8 incidence, and Loop_297 atom exposure; it "
            "isolates packet 239 as the unique full-exposure sector-26 clock-zero packet. The packet charge-frame "
            "classifier names the mass, clock, exposure, gamma_8, hidden, central, and tenfold axes and proves "
            "packet 239 is unique by both the named charge frame and the fine spectral/charge key. The "
            "packet-239 stabilizer theorem then tests the vacuum/seed interpretation: packet 239 has the same "
            "setwise, scalar, and identity-kernel stabilizer orders as every other packet, so it is a "
            "charge-frame seed candidate rather than a unique symmetry-fixed vacuum. The packet-239 seed "
            "propagation theorem then pushes this seed through the non-kernel crossing generators 5, 9, and 10: "
            "one-step crossings reach two odd packet shadows, while paired cross-returns close only on packets "
            "238 and 239 with hidden-transfer cancellation. The full-exposure propagation-cell theorem "
            "generalizes this seed law to all 20 full-exposure packets: every source has two odd shadows, "
            "six paired cross-returns, source/active-partner closure, and the same certified flux/action "
            "histograms. The full-exposure propagation-graph theorem then turns those cells into a weighted "
            "20-vertex transition operator, decomposing it into ten closed active-partner doublets with "
            "block [[2,4],[4,2]], spectrum 6^10 plus (-2)^10, and per-source signed flux cancellation. "
            "The rank-10/tenfold alignment theorem maps those doublets into the certified 8+2 kernel "
            "coordinate split and proves the crucial non-basis result: the ten components match the "
            "rank-10 dimension by count, but their moving support has rank 6, with common radical core "
            "83 and nonlinear radical gate x2 or (x3 and x5). The radical-gate stabilizer theorem "
            "then classifies this nonlinear gate symmetry: affine order 384, linear order 64, a "
            "six-point complement prism in x2=0, support orbits of sizes 8 and 2, and the x7 flip "
            "as the only pure translation symmetry. The radical-gate stabilizer lift theorem then "
            "separates graph/action symmetry from labelled physics: all 384 affine stabilizers lift "
            "to the unlabelled weighted packet graph, the active-flip graph/action extension has order "
            "393216, the combined gamma marker leaves only six canonical affine lifts, and the full "
            "charge-frame plus fine spectral labels leave only identity. The label-breaking factorization "
            "theorem then names the actual breaker axes: mass alone leaves two canonical lifts, clock "
            "leaves 48, gamma leaves 24, spectral trace leaves two, the full sector-26 clock family "
            "leaves identity, and at atomic resolution sector26_clock_sum_mod26 and the fine spectral "
            "key each individually kill every nonidentity radical-gate lift while sector26_clock_delta "
            "kills none. The canonical labelled full-exposure frame theorem then turns those breakers "
            "into an injective 20-packet coordinate frame and recovers packet 239 without using its "
            "external id: it is the unique full-exposure sector-26 zero-pair fixed point, with clock "
            "pair [0,0], sector-26 sum 0, and sector-26 delta 0. The label-coordinate transition "
            "operator theorem then rewrites the full-exposure two-step graph in intrinsic frame labels: "
            "the operator is still ten uniform [[2,4],[4,2]] doublet blocks, and the zero-pair coordinate "
            "has a self-loop of weight two plus an active-partner transition of weight four. The "
            "label-coordinate spectral-boundary theorem diagonalizes this operator into ten plus/minus "
            "doublets and proves the zero-pair coordinate is label-distinguished, but not an eigenvector, "
            "left eigenfunctional, singleton Dirichlet spectrum, or component Dirichlet spectrum. The "
            "label-coordinate Green-response theorem then inserts the zero-pair labelled source and computes "
            "the exact adjacency, Markov, and massive-Laplacian responses: the support is precisely packet "
            "239 and active partner packet 238, with pole residues fixed by the plus/minus doublet spectrum. "
            "The zero-pair propagator charge-kernel theorem then pushes those pole residues through the "
            "packet charge-frame and sector-26 ledger: raw half-residues live over Q, but after canonical "
            "denominator clearing the plus and minus residue classes are integral complementary mod-26 "
            "classes on the same full-exposure, gamma-silent, hidden-cancelled, central-negative AI|BDI pair. "
            "The propagator symmetry/Ward theorem then proves the denominator-cleared kernel is fixed by "
            "the surviving label-preserving symmetry because that symmetry is identity, and is Ward-compatible "
            "only as a packet-source pair: individual residues are not all-mask Ward characters, while the "
            "paired residue is sector-26 neutral and public-flux rank remains zero. The source-to-closed-return "
            "coupling theorem then closes the stronger test: no Ward-character-preserving coupling exists for "
            "the individual plus/minus source residues, and the paired neutral residue has only the canonical "
            "minimal map to the Ward-kernel zero mask until an extra selector chooses a nonzero kernel mask. "
            "The Ward-kernel height-selector theorem then supplies that extra invariant selector: the unique "
            "minimum positive action in the nonzero Ward kernel is mask 288 = cycle5 + gamma8, with height "
            "1065984 and corrected clock 0, giving the paired source its first certified nontrivial "
            "closed-return target. The selected sourced Ward-balance theorem then propagates mask 288 through "
            "the finite BMS/Carrollian and scattering ledgers: gamma8 reaches 288 by generator 5, public "
            "charge/flux/residual terms vanish, and the hidden balance closes as 0 - 1065984 + 1065984 = 0. "
            "The sourced-balance cone theorem then classifies the full one-step gamma8 Ward-kernel target "
            "star: there are nine nonzero balanced kernel targets, mask 288 is the unique height apex, and "
            "that apex is not an algebraic generator of the whole target set. The sourced-balance shortest-path "
            "theorem then extends this from the one-step star to all 1023 nonzero Ward-kernel masks: every "
            "target has a canonical gamma8-XOR shortest scattering path, closes public and hidden balance, "
            "and keeps mask 288 as the unique minimum-action target. The transport-family theorem then "
            "compresses the full atlas: action and height collapse to 805 scalar values, Fourier transport "
            "signatures give 991 families, the hidden-split C2 topologically compresses targets to 543 orbits "
            "but breaks most action-height labels, and the full augmented action/charge ledger leaves only "
            "identity symmetry. The label-relaxed orbit-quotient theorem then proves exactly what must be "
            "forgotten to recover nontrivial symmetry: the gamma8-sourced Ward-kernel atlas admits the C2 "
            "quotient only after dropping target identity, exact support, step/action/height, Fourier and "
            "sector-26 refinements, and the six augmented ledger breaker axes; source-fixed public symmetry "
            "requires enlarging to a 1983-mask closure, and the full 120 public action requires all 2047 "
            "nonzero residue masks and no gamma8 source anchor. The C2 quotient-anomaly theorem then proves "
            "that the action/height breaking is exact cocycle data: the path-action and target-height "
            "cocycles coincide, have even sector-26 shadow with complete mod-13 half-shadow, and make "
            "the sourced Ward/BMS balance descend after the representative height counterterm is subtracted "
            "from action/height and added to R33. The C2 quotient transport-ledger theorem then identifies "
            "the primal operator as the nonidentity hidden-split involution tau, not gamma8: tau fixes "
            "gamma8 as source anchor, acts as a Markov permutation on the 1023 quotient targets with "
            "spectrum +1^543 and -1^480, and induces a rank-543 idempotent Markov projection whose "
            "543-row anomaly-corrected quotient ledger is Ward/BMS-balanced. The quotient scattering "
            "operator theorem then builds the first nontrivial dynamics on that quotient: the C2-closed "
            "hidden-neutral move orbit {8,1034} gives a Markov operator with 144 components, spectrum "
            "1^144, 0^255, (-1)^143, and (-1/2)^1, and a degree-weighted stationary state whose "
            "public and hidden Ward/BMS errors vanish. The C2 move-orbit family theorem then classifies "
            "all 543 C2-closed hidden-neutral composite move orbits: 63 are fixed and 480 are paired, "
            "every zero-exit-closed move operator is symmetric Markov and stationary Ward-balanced, the "
            "family has exactly three component/spectrum types, and the earlier {8,1034} operator is "
            "unique only under the primitive-seeded criterion, not under global action minimization. The "
            "C2 dynamics selector theorem then certifies the split between natural physical criteria: "
            "primitive seeding selects {8,1034}, global action minimization selects {384}, paired-action "
            "minimization selects {288,320}, raw absolute spectral gap is degenerate on all 543 family "
            "members, and lazy componentwise spectral gap selects the 63 fixed singleton operators with "
            "{384} as its action tiebreak. The C2 Cubical foundation bridge then packages this selector "
            "layer as a complete finite skeletal candidate: C2 quotient targets are a set-truncated HIT "
            "with 543 quotient states, C2 Ward-balanced dynamics are a 543-code finite structure universe, "
            "selectors are dependent fibers, singleton selector fibers are contractible, and the remaining "
            "raw/lazy spectral ambiguity is preserved as noncontractible fibers. The bridge explicitly does "
            "not claim a proof-assistant formalization of univalence. The Cubical Agda skeleton theorem "
            "then emits and typechecks the module C2SelectorFoundation, naming the C2TargetQuotient HIT, "
            "WardBalancedDynamicsStructure, SelectedDynamics selector fibers, contractible singleton "
            "selector witnesses, and SkeletalIdentityRule target interface. The Cubical Agda enumeration "
            "theorem then emits and typechecks C2SelectorFoundationGenerated, naming all 543 quotient states, "
            "all 543 dynamics codes, and all 1091 selector membership constructors. The Cubical Agda "
            "enumeration-properties theorem then emits and typechecks C2SelectorFoundationGeneratedProperties, "
            "adding counting lemmas, exhaustive eliminators, decidable equality, and set witnesses for the "
            "quotient-state and dynamics enumerations. The Cubical Agda selector-membership theorem then emits "
            "and typechecks C2SelectorFoundationSelectorMembership, making selector membership decidable for "
            "all 4344 selector/dynamics pairs, with 1091 yes branches, 3253 no branches, and all eight fiber "
            "count proofs. The Cubical Agda selector finite-subtype singleton theorem then emits and typechecks "
            "C2SelectorFoundationSelectorFiniteSubtypeSingletons, packaging the five contractible selector "
            "fibers as Sigma subtypes and proving equivalences to Fin 1. The lazy63 finite-subtype theorem "
            "then emits and typechecks C2SelectorFoundationSelectorFiniteSubtypeLazy63, packaging the lazy "
            "componentwise spectral-gap fiber as a Sigma subtype and proving equivalence to Fin 63. The "
            "paired-lazy480 finite-subtype theorem then emits and typechecks "
            "C2SelectorFoundationSelectorFiniteSubtypePairedLazy480, packaging the paired lazy "
            "componentwise spectral-gap fiber as a Sigma subtype and proving equivalence to Fin 480. The "
            "raw543 finite-subtype theorem then emits and typechecks "
            "C2SelectorFoundationSelectorFiniteSubtypeRaw543, packaging the raw componentwise absolute "
            "spectral-gap fiber as the full dynamics Sigma subtype and proving equivalence to Fin 543. The "
            "finite-subtype emitter-factorization theorem then rewrites the singleton, lazy63, "
            "paired-lazy480, and raw543 generators through one shared emitter while reproducing the "
            "certified Agda sources byte-for-byte. The raw543 indexed finite-subtype theorem then "
            "certifies the same Fin 543 equivalence through natural-number indexed witnesses with no "
            "generated FD.suc constructor normal forms. The indexed split finite-subtype theorem then "
            "promotes that compact indexed proof mode to the lazy63 and paired-lazy480 selector fibers, "
            "certifying Fin 63 and Fin 480 equivalences with no generated FD.suc constructor normal forms. "
            "The indexed lookup finite-subtype theorem then collapses the raw543/lazy63/paired-lazy480 "
            "right inverses through a shared Nat-index helper and FinData fromToId', removing the generated "
            "inspect/injection inverse rows while preserving the certified Fin 543, Fin 63, and Fin 480 "
            "equivalences. The lookup-table theorem then externalizes all 1086 selected witness rows as "
            "JSON/CSV artifacts, checks each row against the lookup Agda source clauses, and typechecks a "
            "Cubical soundness module tying the table counts back to the certified Fin equivalences."
        ),
        "inputs": {
            "sector_attachment_report": {
                "path": rel(SECTOR_ATTACHMENT_REPORT),
                "sha256": sha_file(SECTOR_ATTACHMENT_REPORT),
            },
            "d20_edges": {
                "path": rel(D20_EDGES_CSV),
                "sha256": sha_file(D20_EDGES_CSV),
            },
            "primitive_cycles": {
                "path": rel(PRIMITIVE_CYCLES_CSV),
                "sha256": sha_file(PRIMITIVE_CYCLES_CSV),
            },
            "tube_projection_section": {
                "path": rel(TUBE_PROJECTION_SECTION),
                "sha256": sha_file(TUBE_PROJECTION_SECTION),
            },
            "full_a985_lift": {
                "path": rel(FULL_A985_LIFT),
                "sha256": sha_file(FULL_A985_LIFT),
            },
            "wedderburn_trace": {
                "path": rel(WEDDERBURN_TRACE),
                "sha256": sha_file(WEDDERBURN_TRACE),
            },
            "boundary_to_loop_report": {
                "path": rel(BOUNDARY_TO_LOOP_REPORT),
                "sha256": sha_file(BOUNDARY_TO_LOOP_REPORT) if BOUNDARY_TO_LOOP_REPORT.exists() else None,
            },
            "sector33_boundary_annihilation_report": {
                "path": rel(BOUNDARY_ANNIHILATION_REPORT),
                "sha256": sha_file(BOUNDARY_ANNIHILATION_REPORT)
                if BOUNDARY_ANNIHILATION_REPORT.exists()
                else None,
            },
            "sector33_height_coherent_transport_report": {
                "path": rel(HEIGHT_TRANSPORT_REPORT),
                "sha256": sha_file(HEIGHT_TRANSPORT_REPORT)
                if HEIGHT_TRANSPORT_REPORT.exists()
                else None,
            },
            "sector33_all_residue_height_transport_report": {
                "path": rel(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT),
                "sha256": sha_file(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT)
                if ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT.exists()
                else None,
            },
            "sector33_unique_public_zero_support_report": {
                "path": rel(UNIQUE_PUBLIC_ZERO_SUPPORT_REPORT),
                "sha256": sha_file(UNIQUE_PUBLIC_ZERO_SUPPORT_REPORT)
                if UNIQUE_PUBLIC_ZERO_SUPPORT_REPORT.exists()
                else None,
            },
            "sector_public_shadow_kernel_report": {
                "path": rel(SECTOR_PUBLIC_SHADOW_KERNEL_REPORT),
                "sha256": sha_file(SECTOR_PUBLIC_SHADOW_KERNEL_REPORT)
                if SECTOR_PUBLIC_SHADOW_KERNEL_REPORT.exists()
                else None,
            },
            "sector_idempotent_support_admissibility_report": {
                "path": rel(SECTOR_IDEMPOTENT_SUPPORT_ADMISSIBILITY_REPORT),
                "sha256": sha_file(SECTOR_IDEMPOTENT_SUPPORT_ADMISSIBILITY_REPORT)
                if SECTOR_IDEMPOTENT_SUPPORT_ADMISSIBILITY_REPORT.exists()
                else None,
            },
            "minimal_composite_null_supports_transport_report": {
                "path": rel(MINIMAL_COMPOSITE_TRANSPORT_REPORT),
                "sha256": sha_file(MINIMAL_COMPOSITE_TRANSPORT_REPORT)
                if MINIMAL_COMPOSITE_TRANSPORT_REPORT.exists()
                else None,
            },
            "superselection_flux_balance_extension_report": {
                "path": rel(SUPERSELECTION_FLUX_EXTENSION_REPORT),
                "sha256": sha_file(SUPERSELECTION_FLUX_EXTENSION_REPORT)
                if SUPERSELECTION_FLUX_EXTENSION_REPORT.exists()
                else None,
            },
            "typed_nonexact_optical_flux_update_report": {
                "path": rel(TYPED_NONEXACT_OPTICAL_FLUX_REPORT),
                "sha256": sha_file(TYPED_NONEXACT_OPTICAL_FLUX_REPORT)
                if TYPED_NONEXACT_OPTICAL_FLUX_REPORT.exists()
                else None,
            },
            "sector26_invariant_suite_report": {
                "path": rel(SECTOR26_INVARIANT_SUITE_REPORT),
                "sha256": sha_file(SECTOR26_INVARIANT_SUITE_REPORT)
                if SECTOR26_INVARIANT_SUITE_REPORT.exists()
                else None,
            },
            "finite_anomaly_counter_report": {
                "path": rel(FINITE_ANOMALY_COUNTER_REPORT),
                "sha256": sha_file(FINITE_ANOMALY_COUNTER_REPORT)
                if FINITE_ANOMALY_COUNTER_REPORT.exists()
                else None,
            },
            "sector26_anomaly_cancellation_report": {
                "path": rel(SECTOR26_ANOMALY_CANCELLATION_REPORT),
                "sha256": sha_file(SECTOR26_ANOMALY_CANCELLATION_REPORT)
                if SECTOR26_ANOMALY_CANCELLATION_REPORT.exists()
                else None,
            },
            "anomaly_cancelled_flux_balance_recovery_report": {
                "path": rel(ANOMALY_CANCELLED_FLUX_BALANCE_RECOVERY_REPORT),
                "sha256": sha_file(ANOMALY_CANCELLED_FLUX_BALANCE_RECOVERY_REPORT)
                if ANOMALY_CANCELLED_FLUX_BALANCE_RECOVERY_REPORT.exists()
                else None,
            },
            "gamma8_obstruction_correction_report": {
                "path": rel(GAMMA8_OBSTRUCTION_CORRECTION_REPORT),
                "sha256": sha_file(GAMMA8_OBSTRUCTION_CORRECTION_REPORT)
                if GAMMA8_OBSTRUCTION_CORRECTION_REPORT.exists()
                else None,
            },
            "general_obstruction_correction_suite_report": {
                "path": rel(GENERAL_OBSTRUCTION_CORRECTION_SUITE_REPORT),
                "sha256": sha_file(GENERAL_OBSTRUCTION_CORRECTION_SUITE_REPORT)
                if GENERAL_OBSTRUCTION_CORRECTION_SUITE_REPORT.exists()
                else None,
            },
            "global_counterterm_lattice_report": {
                "path": rel(GLOBAL_COUNTERTERM_LATTICE_REPORT),
                "sha256": sha_file(GLOBAL_COUNTERTERM_LATTICE_REPORT)
                if GLOBAL_COUNTERTERM_LATTICE_REPORT.exists()
                else None,
            },
            "global_corrected_charge_map_report": {
                "path": rel(GLOBAL_CORRECTED_CHARGE_MAP_REPORT),
                "sha256": sha_file(GLOBAL_CORRECTED_CHARGE_MAP_REPORT)
                if GLOBAL_CORRECTED_CHARGE_MAP_REPORT.exists()
                else None,
            },
            "global_corrected_hidden_split_symmetry_report": {
                "path": rel(GLOBAL_CORRECTED_HIDDEN_SPLIT_SYMMETRY_REPORT),
                "sha256": sha_file(GLOBAL_CORRECTED_HIDDEN_SPLIT_SYMMETRY_REPORT)
                if GLOBAL_CORRECTED_HIDDEN_SPLIT_SYMMETRY_REPORT.exists()
                else None,
            },
            "hidden_split_augmented_ledger_stabilizer_report": {
                "path": rel(HIDDEN_SPLIT_AUGMENTED_LEDGER_STABILIZER_REPORT),
                "sha256": sha_file(HIDDEN_SPLIT_AUGMENTED_LEDGER_STABILIZER_REPORT)
                if HIDDEN_SPLIT_AUGMENTED_LEDGER_STABILIZER_REPORT.exists()
                else None,
            },
            "canonical_flux_balance_gauge_report": {
                "path": rel(CANONICAL_FLUX_BALANCE_GAUGE_REPORT),
                "sha256": sha_file(CANONICAL_FLUX_BALANCE_GAUGE_REPORT)
                if CANONICAL_FLUX_BALANCE_GAUGE_REPORT.exists()
                else None,
            },
            "canonical_loop_pi33_obstruction_report": {
                "path": rel(CANONICAL_LOOP_PI33_OBSTRUCTION_REPORT),
                "sha256": sha_file(CANONICAL_LOOP_PI33_OBSTRUCTION_REPORT)
                if CANONICAL_LOOP_PI33_OBSTRUCTION_REPORT.exists()
                else None,
            },
            "canonical_finite_ward_identity_report": {
                "path": rel(CANONICAL_FINITE_WARD_IDENTITY_REPORT),
                "sha256": sha_file(CANONICAL_FINITE_WARD_IDENTITY_REPORT)
                if CANONICAL_FINITE_WARD_IDENTITY_REPORT.exists()
                else None,
            },
            "canonical_all_mask_ward_identity_report": {
                "path": rel(CANONICAL_ALL_MASK_WARD_IDENTITY_REPORT),
                "sha256": sha_file(CANONICAL_ALL_MASK_WARD_IDENTITY_REPORT)
                if CANONICAL_ALL_MASK_WARD_IDENTITY_REPORT.exists()
                else None,
            },
            "finite_bms_carrollian_flux_balance_report": {
                "path": rel(FINITE_BMS_CARROLLIAN_FLUX_BALANCE_REPORT),
                "sha256": sha_file(FINITE_BMS_CARROLLIAN_FLUX_BALANCE_REPORT)
                if FINITE_BMS_CARROLLIAN_FLUX_BALANCE_REPORT.exists()
                else None,
            },
            "hidden_packet_charge_frame_classifier_report": {
                "path": rel(HIDDEN_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT),
                "sha256": sha_file(HIDDEN_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT)
                if HIDDEN_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT.exists()
                else None,
            },
            "canonical_finite_scattering_table_report": {
                "path": rel(CANONICAL_FINITE_SCATTERING_TABLE_REPORT),
                "sha256": sha_file(CANONICAL_FINITE_SCATTERING_TABLE_REPORT)
                if CANONICAL_FINITE_SCATTERING_TABLE_REPORT.exists()
                else None,
            },
            "loop297_scattering_amplitude_lift_report": {
                "path": rel(LOOP297_SCATTERING_AMPLITUDE_LIFT_REPORT),
                "sha256": sha_file(LOOP297_SCATTERING_AMPLITUDE_LIFT_REPORT)
                if LOOP297_SCATTERING_AMPLITUDE_LIFT_REPORT.exists()
                else None,
            },
            "compact_amplitude_quotient_report": {
                "path": rel(COMPACT_AMPLITUDE_QUOTIENT_REPORT),
                "sha256": sha_file(COMPACT_AMPLITUDE_QUOTIENT_REPORT)
                if COMPACT_AMPLITUDE_QUOTIENT_REPORT.exists()
                else None,
            },
            "reduced_amplitude_quotient_scattering_automaton_report": {
                "path": rel(REDUCED_AMPLITUDE_QUOTIENT_SCATTERING_AUTOMATON_REPORT),
                "sha256": sha_file(REDUCED_AMPLITUDE_QUOTIENT_SCATTERING_AUTOMATON_REPORT)
                if REDUCED_AMPLITUDE_QUOTIENT_SCATTERING_AUTOMATON_REPORT.exists()
                else None,
            },
            "amplitude_quotient_fourier_mode_classifier_report": {
                "path": rel(AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER_REPORT),
                "sha256": sha_file(AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER_REPORT)
                if AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER_REPORT.exists()
                else None,
            },
            "finite_virasoro_string_kernel_candidate_report": {
                "path": rel(FINITE_VIRASORO_STRING_KERNEL_CANDIDATE_REPORT),
                "sha256": sha_file(FINITE_VIRASORO_STRING_KERNEL_CANDIDATE_REPORT)
                if FINITE_VIRASORO_STRING_KERNEL_CANDIDATE_REPORT.exists()
                else None,
            },
            "finite_virasoro_generator_algebra_report": {
                "path": rel(FINITE_VIRASORO_GENERATOR_ALGEBRA_REPORT),
                "sha256": sha_file(FINITE_VIRASORO_GENERATOR_ALGEBRA_REPORT)
                if FINITE_VIRASORO_GENERATOR_ALGEBRA_REPORT.exists()
                else None,
            },
            "finite_central_extension_anomaly_cocycle_report": {
                "path": rel(FINITE_CENTRAL_EXTENSION_ANOMALY_COCYCLE_REPORT),
                "sha256": sha_file(FINITE_CENTRAL_EXTENSION_ANOMALY_COCYCLE_REPORT)
                if FINITE_CENTRAL_EXTENSION_ANOMALY_COCYCLE_REPORT.exists()
                else None,
            },
            "finite_parity_central_extension_group_report": {
                "path": rel(FINITE_PARITY_CENTRAL_EXTENSION_GROUP_REPORT),
                "sha256": sha_file(FINITE_PARITY_CENTRAL_EXTENSION_GROUP_REPORT)
                if FINITE_PARITY_CENTRAL_EXTENSION_GROUP_REPORT.exists()
                else None,
            },
            "projective_kernel_packet_tenfold_way_report": {
                "path": rel(PROJECTIVE_KERNEL_PACKET_TENFOLD_WAY_REPORT),
                "sha256": sha_file(PROJECTIVE_KERNEL_PACKET_TENFOLD_WAY_REPORT)
                if PROJECTIVE_KERNEL_PACKET_TENFOLD_WAY_REPORT.exists()
                else None,
            },
            "projective_packet_spectral_charge_table_report": {
                "path": rel(PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_REPORT),
                "sha256": sha_file(PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_REPORT)
                if PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_REPORT.exists()
                else None,
            },
            "projective_packet_charge_frame_classifier_report": {
                "path": rel(PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT),
                "sha256": sha_file(PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT)
                if PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT.exists()
                else None,
            },
            "packet239_stabilizer_seed_candidate_report": {
                "path": rel(PACKET239_STABILIZER_SEED_CANDIDATE_REPORT),
                "sha256": sha_file(PACKET239_STABILIZER_SEED_CANDIDATE_REPORT)
                if PACKET239_STABILIZER_SEED_CANDIDATE_REPORT.exists()
                else None,
            },
            "packet239_seed_propagation_report": {
                "path": rel(PACKET239_SEED_PROPAGATION_REPORT),
                "sha256": sha_file(PACKET239_SEED_PROPAGATION_REPORT)
                if PACKET239_SEED_PROPAGATION_REPORT.exists()
                else None,
            },
            "full_exposure_packet_propagation_cells_report": {
                "path": rel(FULL_EXPOSURE_PACKET_PROPAGATION_CELLS_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_PACKET_PROPAGATION_CELLS_REPORT)
                if FULL_EXPOSURE_PACKET_PROPAGATION_CELLS_REPORT.exists()
                else None,
            },
            "full_exposure_packet_propagation_graph_report": {
                "path": rel(FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_REPORT)
                if FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_REPORT.exists()
                else None,
            },
            "full_exposure_rank10_tenfold_alignment_report": {
                "path": rel(FULL_EXPOSURE_RANK10_TENFOLD_ALIGNMENT_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_RANK10_TENFOLD_ALIGNMENT_REPORT)
                if FULL_EXPOSURE_RANK10_TENFOLD_ALIGNMENT_REPORT.exists()
                else None,
            },
            "full_exposure_radical_gate_stabilizer_report": {
                "path": rel(FULL_EXPOSURE_RADICAL_GATE_STABILIZER_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_RADICAL_GATE_STABILIZER_REPORT)
                if FULL_EXPOSURE_RADICAL_GATE_STABILIZER_REPORT.exists()
                else None,
            },
            "full_exposure_radical_gate_stabilizer_lift_report": {
                "path": rel(FULL_EXPOSURE_RADICAL_GATE_STABILIZER_LIFT_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_RADICAL_GATE_STABILIZER_LIFT_REPORT)
                if FULL_EXPOSURE_RADICAL_GATE_STABILIZER_LIFT_REPORT.exists()
                else None,
            },
            "full_exposure_label_breaking_factorization_report": {
                "path": rel(FULL_EXPOSURE_LABEL_BREAKING_FACTORIZATION_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_LABEL_BREAKING_FACTORIZATION_REPORT)
                if FULL_EXPOSURE_LABEL_BREAKING_FACTORIZATION_REPORT.exists()
                else None,
            },
            "full_exposure_canonical_labelled_frame_report": {
                "path": rel(FULL_EXPOSURE_CANONICAL_LABELLED_FRAME_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_CANONICAL_LABELLED_FRAME_REPORT)
                if FULL_EXPOSURE_CANONICAL_LABELLED_FRAME_REPORT.exists()
                else None,
            },
            "full_exposure_label_coordinate_transition_operator_report": {
                "path": rel(FULL_EXPOSURE_LABEL_COORDINATE_TRANSITION_OPERATOR_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_LABEL_COORDINATE_TRANSITION_OPERATOR_REPORT)
                if FULL_EXPOSURE_LABEL_COORDINATE_TRANSITION_OPERATOR_REPORT.exists()
                else None,
            },
            "full_exposure_label_coordinate_spectral_boundary_report": {
                "path": rel(FULL_EXPOSURE_LABEL_COORDINATE_SPECTRAL_BOUNDARY_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_LABEL_COORDINATE_SPECTRAL_BOUNDARY_REPORT)
                if FULL_EXPOSURE_LABEL_COORDINATE_SPECTRAL_BOUNDARY_REPORT.exists()
                else None,
            },
            "full_exposure_label_coordinate_green_response_report": {
                "path": rel(FULL_EXPOSURE_LABEL_COORDINATE_GREEN_RESPONSE_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_LABEL_COORDINATE_GREEN_RESPONSE_REPORT)
                if FULL_EXPOSURE_LABEL_COORDINATE_GREEN_RESPONSE_REPORT.exists()
                else None,
            },
            "full_exposure_zero_pair_propagator_charge_kernel_report": {
                "path": rel(FULL_EXPOSURE_ZERO_PAIR_PROPAGATOR_CHARGE_KERNEL_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_ZERO_PAIR_PROPAGATOR_CHARGE_KERNEL_REPORT)
                if FULL_EXPOSURE_ZERO_PAIR_PROPAGATOR_CHARGE_KERNEL_REPORT.exists()
                else None,
            },
            "full_exposure_zero_pair_propagator_symmetry_ward_report": {
                "path": rel(FULL_EXPOSURE_ZERO_PAIR_PROPAGATOR_SYMMETRY_WARD_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_ZERO_PAIR_PROPAGATOR_SYMMETRY_WARD_REPORT)
                if FULL_EXPOSURE_ZERO_PAIR_PROPAGATOR_SYMMETRY_WARD_REPORT.exists()
                else None,
            },
            "full_exposure_zero_pair_source_to_closed_return_coupling_report": {
                "path": rel(FULL_EXPOSURE_ZERO_PAIR_SOURCE_TO_CLOSED_RETURN_COUPLING_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_ZERO_PAIR_SOURCE_TO_CLOSED_RETURN_COUPLING_REPORT)
                if FULL_EXPOSURE_ZERO_PAIR_SOURCE_TO_CLOSED_RETURN_COUPLING_REPORT.exists()
                else None,
            },
            "full_exposure_zero_pair_ward_kernel_height_selector_report": {
                "path": rel(FULL_EXPOSURE_ZERO_PAIR_WARD_KERNEL_HEIGHT_SELECTOR_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_ZERO_PAIR_WARD_KERNEL_HEIGHT_SELECTOR_REPORT)
                if FULL_EXPOSURE_ZERO_PAIR_WARD_KERNEL_HEIGHT_SELECTOR_REPORT.exists()
                else None,
            },
            "full_exposure_zero_pair_selected_sourced_ward_balance_report": {
                "path": rel(FULL_EXPOSURE_ZERO_PAIR_SELECTED_SOURCED_WARD_BALANCE_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_ZERO_PAIR_SELECTED_SOURCED_WARD_BALANCE_REPORT)
                if FULL_EXPOSURE_ZERO_PAIR_SELECTED_SOURCED_WARD_BALANCE_REPORT.exists()
                else None,
            },
            "full_exposure_zero_pair_sourced_balance_cone_report": {
                "path": rel(FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_CONE_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_CONE_REPORT)
                if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_CONE_REPORT.exists()
                else None,
            },
            "full_exposure_zero_pair_sourced_balance_shortest_paths_report": {
                "path": rel(FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_SHORTEST_PATHS_REPORT),
                "sha256": sha_file(FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_SHORTEST_PATHS_REPORT)
                if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_SHORTEST_PATHS_REPORT.exists()
                else None,
            },
            "full_exposure_zero_pair_sourced_balance_transport_families_report": {
                "path": rel(FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_TRANSPORT_FAMILIES_REPORT),
                "sha256": sha_file(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_TRANSPORT_FAMILIES_REPORT
                )
                if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_TRANSPORT_FAMILIES_REPORT.exists()
                else None,
            },
            "full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient_report": {
                "path": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_LABEL_RELAXED_ORBIT_QUOTIENT_REPORT
                ),
                "sha256": sha_file(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_LABEL_RELAXED_ORBIT_QUOTIENT_REPORT
                )
                if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_LABEL_RELAXED_ORBIT_QUOTIENT_REPORT.exists()
                else None,
            },
            "full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly_report": {
                "path": rel(FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_ANOMALY_REPORT),
                "sha256": sha_file(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_ANOMALY_REPORT
                )
                if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_ANOMALY_REPORT.exists()
                else None,
            },
            "full_exposure_zero_pair_sourced_balance_c2_quotient_transport_ledger_report": {
                "path": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_TRANSPORT_LEDGER_REPORT
                ),
                "sha256": sha_file(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_TRANSPORT_LEDGER_REPORT
                )
                if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_TRANSPORT_LEDGER_REPORT.exists()
                else None,
            },
            "full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator_report": {
                "path": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_SCATTERING_OPERATOR_REPORT
                ),
                "sha256": sha_file(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_SCATTERING_OPERATOR_REPORT
                )
                if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_SCATTERING_OPERATOR_REPORT.exists()
                else None,
            },
            "full_exposure_zero_pair_sourced_balance_c2_move_orbit_family_report": {
                "path": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_MOVE_ORBIT_FAMILY_REPORT
                ),
                "sha256": sha_file(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_MOVE_ORBIT_FAMILY_REPORT
                )
                if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_MOVE_ORBIT_FAMILY_REPORT.exists()
                else None,
            },
            "full_exposure_zero_pair_sourced_balance_c2_dynamics_selector_report": {
                "path": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_DYNAMICS_SELECTOR_REPORT
                ),
                "sha256": sha_file(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_DYNAMICS_SELECTOR_REPORT
                )
                if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_DYNAMICS_SELECTOR_REPORT.exists()
                else None,
            },
            "raw543_actual_c2_kernel_orbits_csv": {
                "path": rel(RAW543_ACTUAL_C2_KERNEL_ORBITS_CSV),
                "sha256": sha_file(RAW543_ACTUAL_C2_KERNEL_ORBITS_CSV)
                if RAW543_ACTUAL_C2_KERNEL_ORBITS_CSV.exists()
                else None,
            },
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_skeleton_report": {
                "path": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SKELETON_REPORT
                ),
                "sha256": sha_file(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SKELETON_REPORT
                )
                if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SKELETON_REPORT.exists()
                else None,
            },
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_report": {
                "path": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_ENUMERATION_REPORT
                ),
                "sha256": sha_file(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_ENUMERATION_REPORT
                )
                if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_ENUMERATION_REPORT.exists()
                else None,
            },
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_properties_report": {
                "path": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_ENUMERATION_PROPERTIES_REPORT
                ),
                "sha256": sha_file(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_ENUMERATION_PROPERTIES_REPORT
                )
                if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_ENUMERATION_PROPERTIES_REPORT.exists()
                else None,
            },
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_membership_report": {
                "path": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_MEMBERSHIP_REPORT
                ),
                "sha256": sha_file(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_MEMBERSHIP_REPORT
                )
                if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_MEMBERSHIP_REPORT.exists()
                else None,
            },
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_singletons_report": {
                "path": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_SINGLETONS_REPORT
                ),
                "sha256": sha_file(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_SINGLETONS_REPORT
                )
                if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_SINGLETONS_REPORT.exists()
                else None,
            },
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lazy63_report": {
                "path": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LAZY63_REPORT
                ),
                "sha256": sha_file(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LAZY63_REPORT
                )
                if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LAZY63_REPORT.exists()
                else None,
            },
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_paired_lazy480_report": {
                "path": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_PAIRED_LAZY480_REPORT
                ),
                "sha256": sha_file(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_PAIRED_LAZY480_REPORT
                )
                if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_PAIRED_LAZY480_REPORT.exists()
                else None,
            },
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_report": {
                "path": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_REPORT
                ),
                "sha256": sha_file(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_REPORT
                )
                if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_REPORT.exists()
                else None,
            },
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_indexed_report": {
                "path": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_INDEXED_REPORT
                ),
                "sha256": sha_file(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_INDEXED_REPORT
                )
                if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_INDEXED_REPORT.exists()
                else None,
            },
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_split_report": {
                "path": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_SPLIT_REPORT
                ),
                "sha256": sha_file(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_SPLIT_REPORT
                )
                if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_SPLIT_REPORT.exists()
                else None,
            },
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_lookup_report": {
                "path": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_LOOKUP_REPORT
                ),
                "sha256": sha_file(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_LOOKUP_REPORT
                )
                if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_LOOKUP_REPORT.exists()
                else None,
            },
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table_report": {
                "path": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LOOKUP_TABLE_REPORT
                ),
                "sha256": sha_file(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LOOKUP_TABLE_REPORT
                )
                if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LOOKUP_TABLE_REPORT.exists()
                else None,
            },
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_emitter_factorization_report": {
                "path": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_EMITTER_FACTORIZATION_REPORT
                ),
                "sha256": sha_file(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_EMITTER_FACTORIZATION_REPORT
                )
                if FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_EMITTER_FACTORIZATION_REPORT.exists()
                else None,
            },
        },
        "known_certified_data": {
            "cycle8": cycle,
            "cycle8_edges": cycle_edges,
            "sector_interface": attachment.get("derived", {}).get("sector_attachment", {}),
            "tube_projection": tube_section.get("projection", {}),
            "tube_section": {
                "pivot_tube_pair_representatives": section.get("pivot_tube_pair_representatives"),
                "section_nonzero_coefficients": section.get("section_nonzero_coefficients"),
                "projection_section_identity": section.get("projection_section_identity"),
                "section_hash_root": section.get("section_hash_root"),
            },
            "pi33_public_zero_witness": attachment.get("derived", {}).get("sector33_witness", {}),
            "boundary_to_loop_lift": {
                "status": boundary_to_loop.get("status"),
                "definition": boundary_to_loop.get("definition"),
                "directed_object_pair_projection_count": boundary_to_loop.get("derived", {}).get(
                    "directed_object_pair_projection_count"
                ),
                "oriented_edge_count": boundary_to_loop.get("derived", {}).get("oriented_edge_count"),
                "cycle8_steps": boundary_cycle8.get("steps", []),
                "cycle8_vector": vector_summary(boundary_cycle8_vector),
                "cycle8_object_summary": boundary_cycle8_object_summary,
            },
            "pi33_tube_functional": {
                "status": annihilation.get("status"),
                "definition": annihilation.get("definition", {}),
                "sector33_tube_idempotent": {
                    "pieces": annihilation_e33.get("pieces"),
                    "vector": vector_summary(annihilation_e33.get("vector", {})),
                    "object_loop_coordinate_support": annihilation_e33.get(
                        "object_loop_coordinate_support"
                    ),
                    "identity_coefficients_signed": annihilation_e33.get(
                        "identity_coefficients_signed"
                    ),
                    "regular_trace": annihilation_e33.get("regular_trace"),
                },
                "cycle8_bare_lambda_coefficient": annihilation_cycle8.get("unweighted", {}).get(
                    "pi33_tube_character", {}
                ),
                "cycle8_optical_weighted_coefficient": annihilation_cycle8.get(
                    "optical_weighted", {}
                ).get("pi33_tube_character", {}),
            },
            "height_coherent_transport": {
                "status": height_transport.get("status"),
                "definition": height_transport.get("definition", {}),
                "active_circuit": height_transport_derived.get("active_circuit", {}),
                "edge_derived_residual": height_transport_derived.get("edge_derived_residual", {}),
                "height_transport_character": height_transport_character.get("height_transport", {}),
                "public_shadows": height_transport_derived.get("public_shadows", {}),
            },
            "all_residue_height_transport": {
                "status": all_residue_transport.get("status"),
                "definition": all_residue_transport.get("definition", {}),
                "residue_class_count": all_residue_derived.get("residue_class_count"),
                "nonzero_residue_class_count": all_residue_derived.get("nonzero_residue_class_count"),
                "min_nonzero_height_action": all_residue_derived.get("min_nonzero_height_action"),
                "max_height_action": all_residue_derived.get("max_height_action"),
                "field_zero_nonzero_residual_count": all_residue_derived.get(
                    "field_zero_nonzero_residual_count"
                ),
                "edge_mod2_height_incoherence": all_residue_derived.get("edge_mod2_height_incoherence"),
            },
            "unique_public_zero_support": {
                "status": unique_public_zero_support.get("status"),
                "definition": unique_public_zero_support.get("definition", {}),
                "sector_count": unique_public_zero_derived.get("sector_count"),
                "local_pre_idempotent_keys_used": unique_public_zero_derived.get(
                    "local_pre_idempotent_keys_used"
                ),
                "public_zero_sectors": unique_public_zero_derived.get("public_zero_sectors"),
                "nonzero_height_residual_count": unique_public_zero_derived.get(
                    "nonzero_height_residual_count"
                ),
                "field_zero_nonzero_residual_count": unique_public_zero_derived.get(
                    "field_zero_nonzero_residual_count"
                ),
                "unique_public_zero_support": unique_public_zero_derived.get(
                    "unique_public_zero_support"
                ),
            },
            "sector_public_shadow_kernel": {
                "status": sector_public_shadow_kernel.get("status"),
                "definition": sector_public_shadow_kernel.get("definition", {}),
                "shadow_matrix_shape": public_shadow_kernel_derived.get("shadow_matrix_shape"),
                "rank_mod_prime": public_shadow_kernel_derived.get("rank_mod_prime"),
                "kernel_dimension": public_shadow_kernel_derived.get("kernel_dimension"),
                "coordinate_axis_public_zero_sectors": public_shadow_kernel_derived.get(
                    "coordinate_axis_public_zero_sectors"
                ),
                "non_axis_kernel_basis_count": public_shadow_kernel_derived.get(
                    "non_axis_kernel_basis_count"
                ),
            },
            "sector_idempotent_support_admissibility": {
                "status": sector_idempotent_support_admissibility.get("status"),
                "definition": sector_idempotent_support_admissibility.get("definition", {}),
                "nonzero_public_zero_idempotent_supports": idempotent_admissibility_derived.get(
                    "nonzero_public_zero_idempotent_supports"
                ),
                "nonzero_public_zero_boundary_null_supports": idempotent_admissibility_derived.get(
                    "nonzero_public_zero_boundary_null_supports"
                ),
                "primitive_single_sector_public_zero": idempotent_admissibility_derived.get(
                    "primitive_single_sector_public_zero"
                ),
                "height_support_exact_supports_for_certified_transport": idempotent_admissibility_derived.get(
                    "height_support_exact_supports_for_certified_transport"
                ),
            },
            "minimal_composite_null_supports_transport": {
                "status": minimal_composite_transport.get("status"),
                "definition": minimal_composite_transport.get("definition", {}),
                "transport_components": minimal_composite_transport_derived.get("transport_components"),
                "self_transport_ranks": minimal_composite_transport_derived.get("self_transport_ranks"),
                "transport_to_pi33_ranks": minimal_composite_transport_derived.get(
                    "transport_to_pi33_ranks"
                ),
                "transport_from_pi33_ranks": minimal_composite_transport_derived.get(
                    "transport_from_pi33_ranks"
                ),
            },
            "superselection_flux_balance_extension": {
                "status": superselection_flux_extension.get("status"),
                "definition": superselection_flux_extension.get("definition", {}),
                "public_components": superselection_flux_extension_derived.get("public_components"),
                "hidden_components": superselection_flux_extension_derived.get("hidden_components"),
                "hidden_transport_rank_matrix": superselection_flux_extension_derived.get(
                    "hidden_transport_rank_matrix"
                ),
                "admissible_hidden_states": superselection_flux_extension_derived.get(
                    "admissible_hidden_states"
                ),
            },
            "typed_nonexact_optical_flux_update": {
                "status": typed_nonexact_optical_flux.get("status"),
                "definition": typed_nonexact_optical_flux.get("definition", {}),
                "typed_update_count": typed_nonexact_optical_flux_derived.get("typed_update_count"),
                "nonzero_typed_update_count": typed_nonexact_optical_flux_derived.get(
                    "nonzero_typed_update_count"
                ),
                "first_obstruction_update": typed_nonexact_optical_flux_derived.get(
                    "first_obstruction_update"
                ),
                "bosonic_string_26_alignment": typed_nonexact_optical_flux_derived.get(
                    "bosonic_string_26_alignment"
                ),
            },
            "sector26_invariant_suite": {
                "status": sector26_invariant_suite.get("status"),
                "definition": sector26_invariant_suite.get("definition", {}),
                "critical_26_marker": sector26_invariant_suite_derived.get("critical_26_marker"),
                "quotient_stability": sector26_invariant_suite_derived.get("quotient_stability"),
                "hidden_transport_form": sector26_invariant_suite_derived.get("hidden_transport_form"),
                "optical_action_normalization": sector26_invariant_suite_derived.get(
                    "optical_action_normalization"
                ),
            },
            "finite_anomaly_counter": {
                "status": finite_anomaly_counter.get("status"),
                "definition": finite_anomaly_counter.get("definition", {}),
                "clock_character_test": finite_anomaly_counter_derived.get("clock_character_test"),
                "anomaly_defect": finite_anomaly_counter_derived.get("anomaly_defect"),
                "sector26_coupling": finite_anomaly_counter_derived.get("sector26_coupling"),
            },
            "sector26_anomaly_cancellation": {
                "status": sector26_anomaly_cancellation.get("status"),
                "definition": sector26_anomaly_cancellation.get("definition", {}),
                "subspace_dimension_counts": sector26_anomaly_cancellation_derived.get(
                    "subspace_dimension_counts"
                ),
                "maximal_cancelled_packet_count_by_dimension": sector26_anomaly_cancellation_derived.get(
                    "maximal_cancelled_packet_count_by_dimension"
                ),
                "gamma8": sector26_anomaly_cancellation_derived.get("gamma8"),
            },
            "anomaly_cancelled_flux_balance_recovery": {
                "status": anomaly_cancelled_flux_balance_recovery.get("status"),
                "definition": anomaly_cancelled_flux_balance_recovery.get("definition", {}),
                "recovered_packet_count": anomaly_cancelled_flux_balance_recovery_derived.get(
                    "recovered_packet_count"
                ),
                "packet_dimension_histogram": anomaly_cancelled_flux_balance_recovery_derived.get(
                    "packet_dimension_histogram"
                ),
                "packet_clock_image_histogram": anomaly_cancelled_flux_balance_recovery_derived.get(
                    "packet_clock_image_histogram"
                ),
                "gamma8": anomaly_cancelled_flux_balance_recovery_derived.get("gamma8"),
            },
            "gamma8_obstruction_correction": {
                "status": gamma8_obstruction_correction.get("status"),
                "definition": gamma8_obstruction_correction.get("definition", {}),
                "gamma8": gamma8_obstruction_correction_derived.get("gamma8"),
                "corrected_packet_search": gamma8_obstruction_correction_derived.get(
                    "corrected_packet_search", {}
                ),
            },
            "general_obstruction_correction_suite": {
                "status": general_obstruction_correction_suite.get("status"),
                "definition": general_obstruction_correction_suite.get("definition", {}),
                "expected_minimal_signed_lifts": general_obstruction_correction_suite_derived.get(
                    "expected_minimal_signed_lifts"
                ),
                "expected_corrected_maximal_packet_counts": general_obstruction_correction_suite_derived.get(
                    "expected_corrected_maximal_packet_counts"
                ),
                "gamma8_coordinate": general_obstruction_correction_suite_derived.get(
                    "gamma8_coordinate"
                ),
            },
            "global_counterterm_lattice": {
                "status": global_counterterm_lattice.get("status"),
                "definition": global_counterterm_lattice.get("definition", {}),
                "counterterm_signed_lifts": global_counterterm_lattice_derived.get(
                    "counterterm_signed_lifts"
                ),
                "corrected_basis_clock_mod26": global_counterterm_lattice_derived.get(
                    "corrected_basis_clock_mod26"
                ),
                "corrected_clock_histogram": global_counterterm_lattice_derived.get(
                    "corrected_clock_histogram"
                ),
                "gamma8": global_counterterm_lattice_derived.get("gamma8"),
            },
            "character_table_metadata": character,
            "idempotent_matrix_metadata": {
                "full_lift": idempotent_validation,
                "wedderburn_trace": wedderburn_source,
            },
        },
        "certified_maps": {
            "boundary_to_loop_lift": {
                "needed_type": "lambda_boundary: C_1(D20; F_1000003) -> Loop_297",
                "needed_for": "convert the five D20 edges of gamma_8 into a closed-loop vector",
                "edge_table_lift_columns_found": edge_lift_columns,
                "cycle_table_lift_columns_found": cycle_lift_columns,
                "report": rel(BOUNDARY_TO_LOOP_REPORT),
                "cycle8_loop_vector_sha256": boundary_cycle8_vector.get("sha256"),
                "cycle8_loop_vector_support": boundary_cycle8_vector.get("support"),
                "cycle8_loop_vector_coefficient_sum": boundary_cycle8_vector.get("coefficient_sum"),
                "status": "certified",
            },
            "pi33_tube_functional": {
                "needed_type": "tube-visible Pi_33 idempotent/function chi_33^tube on Loop_297",
                "needed_for": "evaluate Pi_33(lambda_boundary(gamma_8)) for the bare structural lift",
                "report": rel(BOUNDARY_ANNIHILATION_REPORT),
                "coefficient_mod_prime": annihilation_cycle8.get("unweighted", {})
                .get("pi33_tube_character", {})
                .get("coefficient_mod_prime"),
                "status": "certified_zero_for_bare_lambda",
            },
            "height_coherent_transport": {
                "needed_type": "Lambda_hc(gamma)=lambda_boundary(gamma)-(A_h(gamma)/dim(Pi_33))e_33",
                "needed_for": "recover the nonzero sector-33 residual from edge/circuit height data",
                "report": rel(HEIGHT_TRANSPORT_REPORT),
                "height_action": height_transport_derived.get("edge_derived_residual", {}).get("height_action"),
                "coefficient_signed": height_transport_character.get("height_transport", {}).get(
                    "coefficient_signed"
                ),
                "status": "certified",
            },
            "all_residue_class_height_transport": {
                "needed_type": "global Lambda_hc over all 2047 nonzero D20 closed-return classes",
                "needed_for": "classify height-derived residuals under the selected sector-33 support",
                "report": rel(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT),
                "nonzero_residue_class_count": all_residue_derived.get("nonzero_residue_class_count"),
                "support_sector": 33,
                "status": "certified",
            },
            "unique_single_sector_public_zero_support": {
                "needed_type": "materialized comparison of all 39 tube-visible sector idempotents",
                "needed_for": "prove the selected sector-33 support is the only single-sector public-zero support",
                "report": rel(UNIQUE_PUBLIC_ZERO_SUPPORT_REPORT),
                "public_zero_sectors": unique_public_zero_derived.get("public_zero_sectors"),
                "local_pre_idempotent_keys_used": unique_public_zero_derived.get(
                    "local_pre_idempotent_keys_used"
                ),
                "status": "certified",
            },
            "sector_public_shadow_kernel": {
                "needed_type": "kernel of the combined A42/A12 shadow map on the 39 sector idempotents",
                "needed_for": (
                    "distinguish single-sector public-zero uniqueness from unconstrained linear public-zero "
                    "span uniqueness"
                ),
                "report": rel(SECTOR_PUBLIC_SHADOW_KERNEL_REPORT),
                "rank_mod_prime": public_shadow_kernel_derived.get("rank_mod_prime"),
                "kernel_dimension": public_shadow_kernel_derived.get("kernel_dimension"),
                "coordinate_axis_public_zero_sectors": public_shadow_kernel_derived.get(
                    "coordinate_axis_public_zero_sectors"
                ),
                "status": "certified",
            },
            "sector_idempotent_support_admissibility": {
                "needed_type": (
                    "Boolean idempotent support classification inside the 39-sector orthogonal idempotent algebra"
                ),
                "needed_for": (
                    "separate primitive/support-exact Pi_33 uniqueness from composite public-zero null supports"
                ),
                "report": rel(SECTOR_IDEMPOTENT_SUPPORT_ADMISSIBILITY_REPORT),
                "nonzero_public_zero_boundary_null_supports": idempotent_admissibility_derived.get(
                    "nonzero_public_zero_boundary_null_supports"
                ),
                "primitive_single_sector_public_zero": idempotent_admissibility_derived.get(
                    "primitive_single_sector_public_zero"
                ),
                "height_support_exact_supports_for_certified_transport": idempotent_admissibility_derived.get(
                    "height_support_exact_supports_for_certified_transport"
                ),
                "status": "certified",
            },
            "minimal_composite_null_supports_transport": {
                "needed_type": (
                    "transport-rank classification of the minimal non-Pi_33 public-zero composite supports"
                ),
                "needed_for": (
                    "decide whether {6,26} and {25,26} are gauge zero, superselection degeneracy, or "
                    "additional hidden boundary sectors"
                ),
                "report": rel(MINIMAL_COMPOSITE_TRANSPORT_REPORT),
                "self_transport_ranks": minimal_composite_transport_derived.get("self_transport_ranks"),
                "transport_to_pi33_ranks": minimal_composite_transport_derived.get(
                    "transport_to_pi33_ranks"
                ),
                "transport_components": minimal_composite_transport_derived.get("transport_components"),
                "status": "certified_superselection_not_gauge",
            },
            "superselection_flux_balance_extension": {
                "needed_type": "augmented finite boundary charge/flux ledger with hidden public-zero labels",
                "needed_for": (
                    "track R33, K_mixed_S, and K_pure_Sminus instead of conflating public-zero hidden "
                    "transport with gauge zero"
                ),
                "report": rel(SUPERSELECTION_FLUX_EXTENSION_REPORT),
                "public_components": superselection_flux_extension_derived.get("public_components"),
                "hidden_components": superselection_flux_extension_derived.get("hidden_components"),
                "status": "certified",
            },
            "typed_nonexact_optical_flux_update": {
                "needed_type": "non-exact optical/action flux update valued in the augmented hidden ledger",
                "needed_for": (
                    "send height residuals to R33 and reserve K_mixed_S/K_pure_Sminus for certified "
                    "superselection-null events"
                ),
                "report": rel(TYPED_NONEXACT_OPTICAL_FLUX_REPORT),
                "typed_update_count": typed_nonexact_optical_flux_derived.get("typed_update_count"),
                "nonzero_typed_update_count": typed_nonexact_optical_flux_derived.get(
                    "nonzero_typed_update_count"
                ),
                "status": "certified",
            },
            "sector26_invariant_suite": {
                "needed_type": (
                    "26-marker stability tests, hidden transport form classification, and mod-26 optical "
                    "normalization"
                ),
                "needed_for": (
                    "separate a genuine invariant role for sector 26 from mere numerical alignment with the "
                    "bosonic string critical dimension"
                ),
                "report": rel(SECTOR26_INVARIANT_SUITE_REPORT),
                "hidden_transport_form": sector26_invariant_suite_derived.get("hidden_transport_form"),
                "residue_classes_hit_mod26": sector26_invariant_suite_derived.get(
                    "optical_action_normalization", {}
                ).get("residue_classes_hit_mod26"),
                "status": "certified",
            },
            "finite_anomaly_counter": {
                "needed_type": "mod-26 optical-action additivity-defect counter on closed-return residues",
                "needed_for": (
                    "decide whether the complete mod-26 residue clock is an additive character or a finite "
                    "sector-26 anomaly counter"
                ),
                "report": rel(FINITE_ANOMALY_COUNTER_REPORT),
                "z26_clock_is_linear_character": finite_anomaly_counter_derived.get(
                    "clock_character_test", {}
                ).get("z26_clock_is_linear_character"),
                "z2_parity_shadow_is_linear_character": finite_anomaly_counter_derived.get(
                    "clock_character_test", {}
                ).get("z2_parity_shadow_is_linear_character"),
                "defect_classes_mod26": finite_anomaly_counter_derived.get(
                    "anomaly_defect", {}
                ).get("defect_classes_mod26"),
                "half_defect_classes_mod13": finite_anomaly_counter_derived.get(
                    "anomaly_defect", {}
                ).get("half_defect_classes_mod13"),
                "status": "certified",
            },
            "sector26_anomaly_cancellation": {
                "needed_type": "maximal closed-return packets where the certified sector-26 anomaly vanishes",
                "needed_for": (
                    "turn the finite anomaly counter into a cancellation law suitable for flux-balance "
                    "recovery"
                ),
                "report": rel(SECTOR26_ANOMALY_CANCELLATION_REPORT),
                "subspace_dimension_counts": sector26_anomaly_cancellation_derived.get(
                    "subspace_dimension_counts"
                ),
                "maximal_cancelled_packet_count_by_dimension": sector26_anomaly_cancellation_derived.get(
                    "maximal_cancelled_packet_count_by_dimension"
                ),
                "gamma8": sector26_anomaly_cancellation_derived.get("gamma8"),
                "status": "certified",
            },
            "anomaly_cancelled_flux_balance_recovery": {
                "needed_type": (
                    "finite flux-balance update restricted to certified anomaly-cancelled closed-return packets"
                ),
                "needed_for": (
                    "recover a finite balance law on the anomaly-cancelled subsector while keeping gamma_8 "
                    "classified as obstructed"
                ),
                "report": rel(ANOMALY_CANCELLED_FLUX_BALANCE_RECOVERY_REPORT),
                "recovered_packet_count": anomaly_cancelled_flux_balance_recovery_derived.get(
                    "recovered_packet_count"
                ),
                "packet_clock_image_histogram": anomaly_cancelled_flux_balance_recovery_derived.get(
                    "packet_clock_image_histogram"
                ),
                "gamma8": anomaly_cancelled_flux_balance_recovery_derived.get("gamma8"),
                "status": "certified",
            },
            "gamma8_obstruction_correction": {
                "needed_type": "minimal local counterterm that includes gamma_8 in a corrected balance law",
                "needed_for": (
                    "separate gamma_8 as a correctable first obstruction rather than leaving it only outside "
                    "the recovered sector"
                ),
                "report": rel(GAMMA8_OBSTRUCTION_CORRECTION_REPORT),
                "gamma8": gamma8_obstruction_correction_derived.get("gamma8"),
                "corrected_packet_search": gamma8_obstruction_correction_derived.get(
                    "corrected_packet_search", {}
                ),
                "status": "certified",
            },
            "general_obstruction_correction_suite": {
                "needed_type": "minimal rank-one counterterms for every self-anomalous basis coordinate",
                "needed_for": (
                    "decide whether gamma_8 is exceptional or part of a full basis-level correction table"
                ),
                "report": rel(GENERAL_OBSTRUCTION_CORRECTION_SUITE_REPORT),
                "expected_minimal_signed_lifts": general_obstruction_correction_suite_derived.get(
                    "expected_minimal_signed_lifts"
                ),
                "expected_corrected_maximal_packet_counts": general_obstruction_correction_suite_derived.get(
                    "expected_corrected_maximal_packet_counts"
                ),
                "status": "certified",
            },
            "global_counterterm_lattice": {
                "needed_type": "simultaneous activation law for the 11 rank-one sector-26 counterterms",
                "needed_for": (
                    "decide whether the whole closed-return residue group becomes corrected flux-balanced "
                    "when all counterterms are active together"
                ),
                "report": rel(GLOBAL_COUNTERTERM_LATTICE_REPORT),
                "counterterm_signed_lifts": global_counterterm_lattice_derived.get(
                    "counterterm_signed_lifts"
                ),
                "corrected_clock_histogram": global_counterterm_lattice_derived.get(
                    "corrected_clock_histogram"
                ),
                "gamma8": global_counterterm_lattice_derived.get("gamma8"),
                "status": "certified",
            },
            "global_corrected_charge_map": {
                "needed_type": (
                    "explicit homomorphism comparing global corrected R33 to the public D20 exact charge basis"
                ),
                "needed_for": (
                    "turn the corrected order-two hidden character into a recoverable finite charge map"
                ),
                "report": rel(GLOBAL_CORRECTED_CHARGE_MAP_REPORT),
                "public_exact_flux_charge_basis": global_corrected_charge_map_derived.get(
                    "public_exact_flux_charge_basis"
                ),
                "global_corrected_hidden_charge": {
                    key: value
                    for key, value in global_corrected_charge_map_derived.get(
                        "global_corrected_hidden_charge", {}
                    ).items()
                    if key != "all_mask_rows"
                },
                "comparison": global_corrected_charge_map_derived.get("comparison"),
                "status": "certified",
            },
            "global_corrected_hidden_split_symmetry": {
                "needed_type": (
                    "classification of public D20 state/edge symmetries preserving the corrected hidden split"
                ),
                "needed_for": (
                    "decide which public boundary symmetries survive after the rank-one hidden closed-return "
                    "character is imposed"
                ),
                "report": rel(GLOBAL_CORRECTED_HIDDEN_SPLIT_SYMMETRY_REPORT),
                "graph": global_corrected_hidden_split_symmetry_derived.get("graph"),
                "symmetry_classification": {
                    key: value
                    for key, value in global_corrected_hidden_split_symmetry_derived.get(
                        "symmetry_classification", {}
                    ).items()
                    if key not in {"preserving_automorphisms", "first_breaking_witnesses"}
                },
                "status": "certified",
            },
            "hidden_split_augmented_ledger_stabilizer": {
                "needed_type": (
                    "test whether the C2 hidden-split stabilizer preserves the augmented finite charge/action ledger"
                ),
                "needed_for": (
                    "decide whether the corrected hidden split supplies a nontrivial symmetry of the full "
                    "sector-26/public/optical ledger, or only of the order-two hidden character"
                ),
                "report": rel(HIDDEN_SPLIT_AUGMENTED_LEDGER_STABILIZER_REPORT),
                "candidate_group": hidden_split_augmented_ledger_stabilizer_derived.get(
                    "candidate_group"
                ),
                "summary": hidden_split_augmented_ledger_stabilizer_derived.get("summary"),
                "status": "certified",
            },
            "canonical_flux_balance_gauge": {
                "needed_type": (
                    "canonical finite boundary marking and root-fixed exact flux-balance gauge"
                ),
                "needed_for": (
                    "remove the remaining additive exact-flux gauge and graph-symmetry gauge from the "
                    "certified finite boundary screen"
                ),
                "report": rel(CANONICAL_FLUX_BALANCE_GAUGE_REPORT),
                "canonical_marking": canonical_flux_balance_gauge_derived.get("canonical_marking"),
                "exact_flux_gauge": {
                    key: value
                    for key, value in canonical_flux_balance_gauge_derived.get(
                        "exact_flux_gauge", {}
                    ).items()
                    if key not in {"root_zero_potential"}
                },
                "residual_symmetry_gauge": canonical_flux_balance_gauge_derived.get(
                    "residual_symmetry_gauge"
                ),
                "status": "certified",
            },
            "canonical_loop_pi33_obstruction": {
                "needed_type": (
                    "canonical-gauge pushforward through boundary-to-Loop_297 and tube-visible Pi_33 test"
                ),
                "needed_for": (
                    "prove that the cycle-8 Pi_33 obstruction statement survives the canonical finite "
                    "flux-balance gauge without materializing the full Drinfeld idempotent matrix"
                ),
                "report": rel(CANONICAL_LOOP_PI33_OBSTRUCTION_REPORT),
                "canonical_boundary_cycle": canonical_loop_pi33_obstruction_derived.get(
                    "canonical_boundary_cycle"
                ),
                "pi33_obstruction": canonical_loop_pi33_obstruction_derived.get("pi33_obstruction"),
                "hash_only_metadata": canonical_loop_pi33_obstruction_derived.get(
                    "hash_only_metadata"
                ),
                "status": "certified",
            },
            "canonical_finite_ward_identity": {
                "needed_type": (
                    "explicit finite Ward identity for gamma_8 in the canonical flux-balance gauge"
                ),
                "needed_for": (
                    "state the certified balance terms: exact public flux gauge zero, bare Pi_33 zero, "
                    "height-corrected R33 term -374784, height action +374784"
                ),
                "report": rel(CANONICAL_FINITE_WARD_IDENTITY_REPORT),
                "ward_identity": canonical_finite_ward_identity_derived.get("ward_identity"),
                "public_exact_flux": canonical_finite_ward_identity_derived.get(
                    "public_exact_flux"
                ),
                "tube_hidden_terms": canonical_finite_ward_identity_derived.get(
                    "tube_hidden_terms"
                ),
                "status": "certified",
            },
            "canonical_all_mask_ward_identity": {
                "needed_type": (
                    "explicit finite Ward identity over all 2048 closed-return residue masks"
                ),
                "needed_for": (
                    "promote the gamma_8 Ward witness to a full-residue finite Ward ledger with public "
                    "exact term zero, bare Pi_33 term zero, and height-corrected R33 cancelling height action"
                ),
                "report": rel(CANONICAL_ALL_MASK_WARD_IDENTITY_REPORT),
                "term_contract": canonical_all_mask_ward_identity_derived.get("term_contract"),
                "global_corrected_character": canonical_all_mask_ward_identity_derived.get(
                    "global_corrected_character"
                ),
                "gamma8_row": canonical_all_mask_ward_identity_derived.get("gamma8_row"),
                "ward_rows_sha256": canonical_all_mask_ward_identity_derived.get(
                    "ward_rows_sha256"
                ),
                "status": "certified",
            },
            "finite_bms_carrollian_flux_balance": {
                "needed_type": (
                    "finite BMS/Carrollian flux-balance projection of the all-mask Ward ledger"
                ),
                "needed_for": (
                    "name the public boundary charge vector, exact flux term, public A985 residual, "
                    "height flux, and hidden R33 residual for every closed-return mask"
                ),
                "report": rel(FINITE_BMS_CARROLLIAN_FLUX_BALANCE_REPORT),
                "public_charge_frame": finite_bms_carrollian_flux_balance_derived.get(
                    "public_charge_frame"
                ),
                "balance_summary": finite_bms_carrollian_flux_balance_derived.get(
                    "balance_summary"
                ),
                "gamma8_row": finite_bms_carrollian_flux_balance_derived.get("gamma8_row"),
                "status": "certified",
            },
            "hidden_packet_charge_frame_classifier": {
                "needed_type": (
                    "canonical charge-frame classifier for hidden kernel and odd flux packets"
                ),
                "needed_for": (
                    "classify the 1024 hidden-kernel and 1024 hidden-odd finite flux packets by root, "
                    "edge-support, public-flux moment, and action invariants"
                ),
                "report": rel(HIDDEN_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT),
                "packet_histograms": hidden_packet_charge_frame_classifier_derived.get(
                    "packet_histograms"
                ),
                "classifiers": hidden_packet_charge_frame_classifier_derived.get("classifiers"),
                "gamma8_row": hidden_packet_charge_frame_classifier_derived.get("gamma8_row"),
                "status": "certified",
            },
            "canonical_finite_scattering_table": {
                "needed_type": (
                    "canonical primitive-generator scattering table over complete packet signatures"
                ),
                "needed_for": (
                    "record incoming and outgoing packet signatures, signed height flux, and hidden "
                    "R33 transfer for every primitive closed-return generator move"
                ),
                "report": rel(CANONICAL_FINITE_SCATTERING_TABLE_REPORT),
                "transition_counts": canonical_finite_scattering_table_derived.get(
                    "transition_counts"
                ),
                "packet_transfer_histogram": canonical_finite_scattering_table_derived.get(
                    "packet_transfer_histogram"
                ),
                "hidden_R33_transfer_mod26_histogram": canonical_finite_scattering_table_derived.get(
                    "hidden_R33_transfer_mod26_histogram"
                ),
                "gamma8_scattering_star": canonical_finite_scattering_table_derived.get(
                    "gamma8_scattering_star"
                ),
                "status": "certified",
            },
            "loop297_scattering_amplitude_lift": {
                "needed_type": (
                    "Loop_297/tube amplitude lift for canonical finite scattering rows"
                ),
                "needed_for": (
                    "attach generator-level boundary-to-Loop_297 amplitude packets, bare zero Pi_33 "
                    "tube amplitudes, and height-corrected R33 transition balances"
                ),
                "report": rel(LOOP297_SCATTERING_AMPLITUDE_LIFT_REPORT),
                "lifted_transition_counts": loop297_scattering_amplitude_lift_derived.get(
                    "lifted_transition_counts"
                ),
                "hidden_R33_transfer_mod26_histogram": loop297_scattering_amplitude_lift_derived.get(
                    "hidden_R33_transfer_mod26_histogram"
                ),
                "gamma8_generator_amplitude_packet": loop297_scattering_amplitude_lift_derived.get(
                    "gamma8_generator_amplitude_packet"
                ),
                "gamma8_lifted_scattering_star": loop297_scattering_amplitude_lift_derived.get(
                    "gamma8_lifted_scattering_star"
                ),
                "status": "certified",
            },
            "compact_amplitude_quotient": {
                "needed_type": (
                    "compact quotient of the 11 primitive generator amplitude packets"
                ),
                "needed_for": (
                    "collapse the public tube-zero class while retaining the 25 Loop_297 "
                    "step atoms that separate primitive generator chains"
                ),
                "report": rel(COMPACT_AMPLITUDE_QUOTIENT_REPORT),
                "quotient_summary": compact_amplitude_quotient_derived.get(
                    "quotient_summary"
                ),
                "gamma8_quotient_row": compact_amplitude_quotient_derived.get(
                    "gamma8_quotient_row"
                ),
                "status": "certified",
            },
            "reduced_amplitude_quotient_scattering_automaton": {
                "needed_type": (
                    "finite automaton over the 2048 residue masks labelled by compact amplitude quotients"
                ),
                "needed_for": (
                    "certify the reduced transition system, hidden-sector quotient matrix, exact spectrum, "
                    "and Loop_297 step-atom exposure counts"
                ),
                "report": rel(REDUCED_AMPLITUDE_QUOTIENT_SCATTERING_AUTOMATON_REPORT),
                "automaton_summary": reduced_amplitude_quotient_scattering_automaton_derived.get(
                    "automaton_summary"
                ),
                "spectral_invariants": reduced_amplitude_quotient_scattering_automaton_derived.get(
                    "spectral_invariants"
                ),
                "sector_invariants": reduced_amplitude_quotient_scattering_automaton_derived.get(
                    "sector_invariants"
                ),
                "gamma8_transition_summary": reduced_amplitude_quotient_scattering_automaton_derived.get(
                    "gamma8_transition_summary"
                ),
                "status": "certified",
            },
            "amplitude_quotient_fourier_mode_classifier": {
                "needed_type": (
                    "finite Fourier character classifier for the reduced amplitude-quotient automaton"
                ),
                "needed_for": (
                    "diagonalize the automaton by F_2^11 characters and classify modes by eigenvalue, "
                    "hidden sector, gamma_8 support, sector-26 clock, and compact step-atom exposure"
                ),
                "report": rel(AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER_REPORT),
                "classifier_summary": amplitude_quotient_fourier_mode_classifier_derived.get(
                    "classifier_summary"
                ),
                "distinguished_modes": amplitude_quotient_fourier_mode_classifier_derived.get(
                    "distinguished_modes"
                ),
                "status": "certified",
            },
            "finite_virasoro_string_kernel_candidate": {
                "needed_type": (
                    "finite sector-26 string-kernel candidate inside the Fourier mode classifier"
                ),
                "needed_for": (
                    "isolate the clock-zero seed fiber, certify its rank-10 additive closure, "
                    "and identify primitive preserving moves plus paired cross-return composites"
                ),
                "report": rel(FINITE_VIRASORO_STRING_KERNEL_CANDIDATE_REPORT),
                "closure_summary": finite_virasoro_string_kernel_candidate_derived.get(
                    "closure_summary"
                ),
                "kernel_internal_graph": finite_virasoro_string_kernel_candidate_derived.get(
                    "kernel_internal_graph"
                ),
                "distinguished_membership": finite_virasoro_string_kernel_candidate_derived.get(
                    "distinguished_membership"
                ),
                "status": "certified",
            },
            "finite_virasoro_generator_algebra": {
                "needed_type": (
                    "finite generator algebra on the rank-10 string-kernel candidate"
                ),
                "needed_for": (
                    "certify the rank-10 translation operator algebra, its commutators, "
                    "cross-composite relation, and sector-26 clock defect"
                ),
                "report": rel(FINITE_VIRASORO_GENERATOR_ALGEBRA_REPORT),
                "algebra_summary": finite_virasoro_generator_algebra_derived.get(
                    "algebra_summary"
                ),
                "defining_relations": finite_virasoro_generator_algebra_derived.get(
                    "defining_relations"
                ),
                "status": "certified",
            },
            "finite_central_extension_anomaly_cocycle": {
                "needed_type": (
                    "finite central-extension/anomaly cocycle test on the string-kernel generator algebra"
                ),
                "needed_for": (
                    "separate the symmetric sector-26 clock coboundary from a surviving alternating "
                    "central cocycle and locate the parity anomaly support"
                ),
                "report": rel(FINITE_CENTRAL_EXTENSION_ANOMALY_COCYCLE_REPORT),
                "central_extension_summary": (
                    finite_central_extension_anomaly_cocycle_derived.get(
                        "central_extension_summary"
                    )
                ),
                "compatible_f2_alternating_search": (
                    finite_central_extension_anomaly_cocycle_derived.get(
                        "compatible_f2_alternating_search"
                    )
                ),
                "status": "certified",
            },
            "finite_parity_central_extension_group": {
                "needed_type": (
                    "finite parity central-extension group and signed projective kernel action"
                ),
                "needed_for": (
                    "integrate the surviving F2 cocycle, certify the named commutator support, "
                    "and realize the central bit as a projective sign on the rank-10 kernel"
                ),
                "report": rel(FINITE_PARITY_CENTRAL_EXTENSION_GROUP_REPORT),
                "central_extension_summary": finite_parity_central_extension_group_derived.get(
                    "central_extension_summary"
                ),
                "projective_action_summary": finite_parity_central_extension_group_derived.get(
                    "projective_action_summary"
                ),
                "status": "certified",
            },
            "projective_kernel_packet_tenfold_way": {
                "needed_type": (
                    "central-character packet decomposition and finite tenfold-way witness"
                ),
                "needed_for": (
                    "decompose the signed projective kernel action, attach sector-26 and Loop_297 "
                    "packet data, and record the 8+2 real Clifford/Bott readout"
                ),
                "report": rel(PROJECTIVE_KERNEL_PACKET_TENFOLD_WAY_REPORT),
                "packet_summary": projective_kernel_packet_tenfold_way_derived.get(
                    "packet_summary"
                ),
                "tenfold_way_witness": projective_kernel_packet_tenfold_way_derived.get(
                    "tenfold_way_witness"
                ),
                "loop297_packet_exposure_summary": (
                    projective_kernel_packet_tenfold_way_derived.get(
                        "loop297_packet_exposure_summary"
                    )
                ),
                "status": "certified",
            },
            "projective_packet_spectral_charge_table": {
                "needed_type": "packet-level spectral/charge table on the signed kernel packets",
                "needed_for": (
                    "name the packet spectral traces, sector-26 clocks, hidden-clock cancellation, "
                    "gamma8 incidence, Loop_297 exposure, and distinguished packet sets"
                ),
                "report": rel(PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_REPORT),
                "spectral_charge_summary": projective_packet_spectral_charge_table_derived.get(
                    "spectral_charge_summary"
                ),
                "distinguished_packet_sets": projective_packet_spectral_charge_table_derived.get(
                    "distinguished_packet_sets"
                ),
                "status": "certified",
            },
            "projective_packet_charge_frame_classifier": {
                "needed_type": "named finite charge-frame classifier on projective packets",
                "needed_for": (
                    "name the mass, clock, exposure, gamma8, hidden, central, and tenfold axes, "
                    "and isolate packet 239 as the distinguished full-exposure clock-zero packet"
                ),
                "report": rel(PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT),
                "classifier_summary": projective_packet_charge_frame_classifier_derived.get(
                    "classifier_summary"
                ),
                "distinguished_packet_239": projective_packet_charge_frame_classifier_derived.get(
                    "distinguished_packet_239"
                ),
                "status": "certified",
            },
            "packet239_stabilizer_seed_candidate": {
                "needed_type": "stabilizer comparison for the distinguished packet-239 seed candidate",
                "needed_for": (
                    "test whether packet 239 is symmetry-fixed or only charge-frame distinguished"
                ),
                "report": rel(PACKET239_STABILIZER_SEED_CANDIDATE_REPORT),
                "stabilizer_summary": packet239_stabilizer_seed_candidate_derived.get(
                    "stabilizer_summary"
                ),
                "packet239_stabilizer": packet239_stabilizer_seed_candidate_derived.get(
                    "packet239_stabilizer"
                ),
                "status": "certified",
            },
            "packet239_seed_propagation": {
                "needed_type": "local non-kernel propagation cell for packet 239",
                "needed_for": (
                    "push packet 239 through crossing generators 5, 9, and 10 and classify odd shadows "
                    "plus paired cross-return packets"
                ),
                "report": rel(PACKET239_SEED_PROPAGATION_REPORT),
                "propagation_summary": packet239_seed_propagation_derived.get(
                    "propagation_summary"
                ),
                "status": "certified",
            },
            "full_exposure_packet_propagation_cells": {
                "needed_type": "uniform non-kernel propagation cells for all full-exposure packets",
                "needed_for": (
                    "test whether packet-239 seed propagation is exceptional or one cell of a 20-packet "
                    "full-exposure propagation law"
                ),
                "report": rel(FULL_EXPOSURE_PACKET_PROPAGATION_CELLS_REPORT),
                "propagation_cell_summary": (
                    full_exposure_packet_propagation_cells_derived.get(
                        "propagation_cell_summary"
                    )
                ),
                "status": "certified",
            },
            "full_exposure_packet_propagation_graph": {
                "needed_type": "weighted graph quotient of the full-exposure propagation cells",
                "needed_for": (
                    "classify the two-step packet transition operator, its active-partner doublets, "
                    "and graph-level flux/action invariants"
                ),
                "report": rel(FULL_EXPOSURE_PACKET_PROPAGATION_GRAPH_REPORT),
                "graph_summary": full_exposure_packet_propagation_graph_derived.get(
                    "graph_summary"
                ),
                "spectral_summary": full_exposure_packet_propagation_graph_derived.get(
                    "spectral_summary"
                ),
                "status": "certified",
            },
            "full_exposure_rank10_tenfold_alignment": {
                "needed_type": "rank-10 coordinate and tenfold-way alignment test for graph doublets",
                "needed_for": (
                    "decide whether the ten full-exposure graph components form a canonical kernel "
                    "basis or only a ten-component screen inside the 8+2 split"
                ),
                "report": rel(FULL_EXPOSURE_RANK10_TENFOLD_ALIGNMENT_REPORT),
                "alignment_summary": full_exposure_rank10_tenfold_alignment_derived.get(
                    "alignment_summary"
                ),
                "boolean_gate_witness": full_exposure_rank10_tenfold_alignment_derived.get(
                    "boolean_gate_witness"
                ),
                "tenfold_alignment": full_exposure_rank10_tenfold_alignment_derived.get(
                    "tenfold_alignment"
                ),
                "status": "certified",
            },
            "full_exposure_radical_gate_stabilizer": {
                "needed_type": "affine stabilizer classification for the nonlinear full-exposure radical gate",
                "needed_for": (
                    "classify the symmetry group of the x2 or (x3 and x5) radical gate before lifting "
                    "those symmetries to packet propagation, charge-frame, gamma8, and action labels"
                ),
                "report": rel(FULL_EXPOSURE_RADICAL_GATE_STABILIZER_REPORT),
                "stabilizer_summary": full_exposure_radical_gate_stabilizer_derived.get(
                    "stabilizer_summary"
                ),
                "complement_prism_witness": full_exposure_radical_gate_stabilizer_derived.get(
                    "complement_prism_witness"
                ),
                "group_decomposition": full_exposure_radical_gate_stabilizer_derived.get(
                    "group_decomposition"
                ),
                "status": "certified",
            },
            "full_exposure_radical_gate_stabilizer_lift": {
                "needed_type": (
                    "canonical and active-flip lifts of the 384 radical-gate affine stabilizers to "
                    "the full packet propagation graph"
                ),
                "needed_for": (
                    "separate unlabelled graph/action symmetry from the label-breaking charge-frame, "
                    "gamma8, and spectral invariants"
                ),
                "report": rel(FULL_EXPOSURE_RADICAL_GATE_STABILIZER_LIFT_REPORT),
                "graph_action_lift_summary": full_exposure_radical_gate_stabilizer_lift_derived.get(
                    "graph_action_lift_summary"
                ),
                "label_preservation_summaries": (
                    full_exposure_radical_gate_stabilizer_lift_derived.get(
                        "label_preservation_summaries"
                    )
                ),
                "full_exposure_label_witness": full_exposure_radical_gate_stabilizer_lift_derived.get(
                    "full_exposure_label_witness"
                ),
                "status": "certified",
            },
            "full_exposure_label_breaking_factorization": {
                "needed_type": (
                    "minimal invariant-axis factorization of charge-frame symmetry breaking for the "
                    "canonical radical-gate lifts"
                ),
                "needed_for": (
                    "identify exactly which mass, clock, gamma, sector-26, and spectral labels break "
                    "the nonidentity radical-gate lifts"
                ),
                "report": rel(FULL_EXPOSURE_LABEL_BREAKING_FACTORIZATION_REPORT),
                "breaker_summary": full_exposure_label_breaking_factorization_derived.get(
                    "breaker_summary"
                ),
                "axis_family_rows": full_exposure_label_breaking_factorization_derived.get(
                    "axis_family_rows"
                ),
                "atomic_label_rows": full_exposure_label_breaking_factorization_derived.get(
                    "atomic_label_rows"
                ),
                "status": "certified",
            },
            "full_exposure_canonical_labelled_frame": {
                "needed_type": (
                    "injective intrinsic coordinate frame for the 20 labelled full-exposure packets"
                ),
                "needed_for": (
                    "recover packet 239 by an id-free sector-26 zero-pair fixed-point condition"
                ),
                "report": rel(FULL_EXPOSURE_CANONICAL_LABELLED_FRAME_REPORT),
                "canonical_frame_summary": full_exposure_canonical_labelled_frame_derived.get(
                    "canonical_frame_summary"
                ),
                "packet239_selection": full_exposure_canonical_labelled_frame_derived.get(
                    "packet239_selection"
                ),
                "minimal_identity_breakers": full_exposure_canonical_labelled_frame_derived.get(
                    "minimal_identity_breakers"
                ),
                "status": "certified",
            },
            "full_exposure_label_coordinate_transition_operator": {
                "needed_type": (
                    "weighted full-exposure transition operator expressed in intrinsic labelled-frame coordinates"
                ),
                "needed_for": (
                    "remove packet ids from the transition coordinates and identify the zero-pair "
                    "coordinate's self-loop and active-partner transition"
                ),
                "report": rel(FULL_EXPOSURE_LABEL_COORDINATE_TRANSITION_OPERATOR_REPORT),
                "transition_summary": full_exposure_label_coordinate_transition_operator_derived.get(
                    "transition_summary"
                ),
                "zero_pair_target_weights": (
                    full_exposure_label_coordinate_transition_operator_derived.get(
                        "zero_pair_target_weights"
                    )
                ),
                "status": "certified",
            },
            "full_exposure_label_coordinate_spectral_boundary": {
                "needed_type": (
                    "exact spectral and eigenboundary test of the intrinsic label-coordinate transition operator"
                ),
                "needed_for": (
                    "decide whether the zero-pair coordinate is operator-distinguished, rather than only "
                    "label-distinguished"
                ),
                "report": rel(FULL_EXPOSURE_LABEL_COORDINATE_SPECTRAL_BOUNDARY_REPORT),
                "spectral_boundary_summary": (
                    full_exposure_label_coordinate_spectral_boundary_derived.get(
                        "spectral_boundary_summary"
                    )
                ),
                "global_spectrum": full_exposure_label_coordinate_spectral_boundary_derived.get(
                    "global_spectrum"
                ),
                "zero_pair_coordinate_spectral_row": (
                    full_exposure_label_coordinate_spectral_boundary_derived.get(
                        "zero_pair_coordinate_spectral_row"
                    )
                ),
                "status": "certified",
            },
            "full_exposure_label_coordinate_green_response": {
                "needed_type": (
                    "exact Green/resolvent response of the intrinsic label-coordinate operator to a labelled source"
                ),
                "needed_for": (
                    "turn the zero-pair coordinate into a source insertion and compute its finite "
                    "propagator kernel"
                ),
                "report": rel(FULL_EXPOSURE_LABEL_COORDINATE_GREEN_RESPONSE_REPORT),
                "green_response_summary": full_exposure_label_coordinate_green_response_derived.get(
                    "green_response_summary"
                ),
                "zero_pair_source_response": (
                    full_exposure_label_coordinate_green_response_derived.get(
                        "zero_pair_source_response"
                    )
                ),
                "exact_identity_witnesses": (
                    full_exposure_label_coordinate_green_response_derived.get(
                        "exact_identity_witnesses"
                    )
                ),
                "status": "certified",
            },
            "full_exposure_zero_pair_propagator_charge_kernel": {
                "needed_type": (
                    "packet charge-frame and sector-26 ledger image of the zero-pair Green pole residues"
                ),
                "needed_for": (
                    "decide whether the zero-pair source response carries a finite propagator charge kernel"
                ),
                "report": rel(FULL_EXPOSURE_ZERO_PAIR_PROPAGATOR_CHARGE_KERNEL_REPORT),
                "propagator_charge_kernel_summary": (
                    full_exposure_zero_pair_propagator_charge_kernel_derived.get(
                        "propagator_charge_kernel_summary"
                    )
                ),
                "residue_charge_rows_sha256": (
                    full_exposure_zero_pair_propagator_charge_kernel_derived.get(
                        "residue_charge_rows_sha256"
                    )
                ),
                "status": "certified",
            },
            "full_exposure_zero_pair_propagator_symmetry_ward": {
                "needed_type": (
                    "surviving-label symmetry and finite Ward/flux compatibility test for the zero-pair propagator kernel"
                ),
                "needed_for": (
                    "separate identity-level symmetry invariance from a stronger sourced Ward identity claim"
                ),
                "report": rel(FULL_EXPOSURE_ZERO_PAIR_PROPAGATOR_SYMMETRY_WARD_REPORT),
                "symmetry_summary": full_exposure_zero_pair_propagator_symmetry_ward_derived.get(
                    "symmetry_summary"
                ),
                "ward_flux_summary": full_exposure_zero_pair_propagator_symmetry_ward_derived.get(
                    "ward_flux_summary"
                ),
                "compatibility_matrix": (
                    full_exposure_zero_pair_propagator_symmetry_ward_derived.get(
                        "compatibility_matrix"
                    )
                ),
                "status": "certified",
            },
            "full_exposure_zero_pair_source_to_closed_return_coupling": {
                "needed_type": (
                    "source-to-closed-return coupling test for the denominator-cleared zero-pair propagator kernel"
                ),
                "needed_for": (
                    "decide whether packet-source residues can be promoted to all-mask Ward characters"
                ),
                "report": rel(FULL_EXPOSURE_ZERO_PAIR_SOURCE_TO_CLOSED_RETURN_COUPLING_REPORT),
                "coupling_summary": (
                    full_exposure_zero_pair_source_to_closed_return_coupling_derived.get(
                        "coupling_summary"
                    )
                ),
                "source_to_closed_return_coupling_matrix": (
                    full_exposure_zero_pair_source_to_closed_return_coupling_derived.get(
                        "source_to_closed_return_coupling_matrix"
                    )
                ),
                "status": "certified",
            },
            "full_exposure_zero_pair_ward_kernel_height_selector": {
                "needed_type": (
                    "action-height selector on the nonzero all-mask Ward kernel for the paired zero-pair source"
                ),
                "needed_for": (
                    "choose a nontrivial closed-return target for the paired neutral packet-source residue"
                ),
                "report": rel(FULL_EXPOSURE_ZERO_PAIR_WARD_KERNEL_HEIGHT_SELECTOR_REPORT),
                "selector_summary": (
                    full_exposure_zero_pair_ward_kernel_height_selector_derived.get(
                        "selector_summary"
                    )
                ),
                "selector_candidates_by_height": (
                    full_exposure_zero_pair_ward_kernel_height_selector_derived.get(
                        "selector_candidates_by_height"
                    )
                ),
                "status": "certified",
            },
            "full_exposure_zero_pair_selected_sourced_ward_balance": {
                "needed_type": (
                    "selected finite BMS/Carrollian sourced Ward balance for the nontrivial zero-pair lift"
                ),
                "needed_for": (
                    "prove the selected closed-return target is realized by scattering and closes the public/hidden balance"
                ),
                "report": rel(FULL_EXPOSURE_ZERO_PAIR_SELECTED_SOURCED_WARD_BALANCE_REPORT),
                "sourced_balance_summary": (
                    full_exposure_zero_pair_selected_sourced_ward_balance_derived.get(
                        "sourced_balance_summary"
                    )
                ),
                "scattering_witness": (
                    full_exposure_zero_pair_selected_sourced_ward_balance_derived.get(
                        "scattering_witness"
                    )
                ),
                "status": "certified",
            },
            "full_exposure_zero_pair_sourced_balance_cone": {
                "needed_type": (
                    "height-ordered cone classifier for one-step gamma8 Ward-kernel sourced balance targets"
                ),
                "needed_for": (
                    "separate the height-apex result from the stronger algebraic-generation claim"
                ),
                "report": rel(FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_CONE_REPORT),
                "cone_summary": full_exposure_zero_pair_sourced_balance_cone_derived.get(
                    "cone_summary"
                ),
                "height_ordered_nonzero_kernel_targets": (
                    full_exposure_zero_pair_sourced_balance_cone_derived.get(
                        "height_ordered_nonzero_kernel_targets"
                    )
                ),
                "status": "certified",
            },
            "full_exposure_zero_pair_sourced_balance_shortest_paths": {
                "needed_type": (
                    "canonical shortest scattering-path classifier from gamma8 to every nonzero Ward-kernel target"
                ),
                "needed_for": (
                    "extend sourced Ward/BMS balance from the one-step cone to all nonzero Ward-kernel masks"
                ),
                "report": rel(FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_SHORTEST_PATHS_REPORT),
                "shortest_path_summary": (
                    full_exposure_zero_pair_sourced_balance_shortest_paths_derived.get(
                        "shortest_path_summary"
                    )
                ),
                "shortest_path_rows_sha256": (
                    full_exposure_zero_pair_sourced_balance_shortest_paths_derived.get(
                        "shortest_path_summary", {}
                    ).get("path_rows_sha256")
                ),
                "status": "certified",
            },
            "full_exposure_zero_pair_sourced_balance_transport_families": {
                "needed_type": (
                    "canonical transport-family compression and symmetry-level resolution for the 1023-path atlas"
                ),
                "needed_for": (
                    "separate scalar/Fourier/path compression from any nontrivial D20 symmetry quotient claim"
                ),
                "report": rel(FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_TRANSPORT_FAMILIES_REPORT),
                "transport_family_summary": (
                    full_exposure_zero_pair_sourced_balance_transport_families_derived.get(
                        "transport_family_summary"
                    )
                ),
                "hidden_split_c2_orbit_summary": (
                    full_exposure_zero_pair_sourced_balance_transport_families_derived.get(
                        "hidden_split_c2_orbit_summary"
                    )
                ),
                "status": "certified",
            },
            "full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient": {
                "needed_type": (
                    "label-relaxed orbit quotient ladder for nontrivial gamma8-sourced transport symmetry"
                ),
                "needed_for": (
                    "prove which transport, Fourier, charge, action, and source labels must be forgotten "
                    "to recover nontrivial D20 quotient symmetry"
                ),
                "report": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_LABEL_RELAXED_ORBIT_QUOTIENT_REPORT
                ),
                "label_relaxation_summary": (
                    full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient_derived.get(
                        "label_relaxation_summary"
                    )
                ),
                "public_level_summary": (
                    full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient_derived.get(
                        "public_level_summary"
                    )
                ),
                "status": "certified",
            },
            "full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly": {
                "needed_type": (
                    "exact C2 quotient anomaly/cocycle for sourced action-height label breaking"
                ),
                "needed_for": (
                    "test whether sourced Ward/BMS balance descends to the nontrivial hidden-split C2 quotient "
                    "after carrying the action-height anomaly as connection data"
                ),
                "report": rel(FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_ANOMALY_REPORT),
                "anomaly_summary": (
                    full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly_derived.get(
                        "anomaly_summary"
                    )
                ),
                "anomaly_rows_sha256": (
                    full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly_derived.get(
                        "anomaly_rows_sha256"
                    )
                ),
                "orbit_balance_rows_sha256": (
                    full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly_derived.get(
                        "orbit_balance_rows_sha256"
                    )
                ),
                "status": "certified",
            },
            "full_exposure_zero_pair_sourced_balance_c2_quotient_transport_ledger": {
                "needed_type": (
                    "C2 primal-operator, Markov projection, spectrum, and 543-orbit quotient transport ledger"
                ),
                "needed_for": (
                    "identify whether the quotient anomaly is gamma8, name the primal operator, and test "
                    "the anomaly-corrected quotient ledger for Markov/spectral Ward balance"
                ),
                "report": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_TRANSPORT_LEDGER_REPORT
                ),
                "operator_summary": (
                    full_exposure_zero_pair_sourced_balance_c2_quotient_transport_ledger_derived.get(
                        "operator_summary"
                    )
                ),
                "quotient_ledger_rows_sha256": (
                    full_exposure_zero_pair_sourced_balance_c2_quotient_transport_ledger_derived.get(
                        "quotient_ledger_rows_sha256"
                    )
                ),
                "status": "certified",
            },
            "full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator": {
                "needed_type": (
                    "nontrivial C2 quotient scattering operator from the minimal hidden-neutral move orbit"
                ),
                "needed_for": (
                    "turn the 543-orbit anomaly-corrected quotient ledger into Markov/spectral dynamics "
                    "with Ward-balanced stationary data"
                ),
                "report": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_QUOTIENT_SCATTERING_OPERATOR_REPORT
                ),
                "operator_summary": (
                    full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator_derived.get(
                        "operator_summary"
                    )
                ),
                "quotient_operator_rows_sha256": (
                    full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator_derived.get(
                        "quotient_operator_rows_sha256"
                    )
                ),
                "component_rows_sha256": (
                    full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator_derived.get(
                        "component_rows_sha256"
                    )
                ),
                "status": "certified",
            },
            "full_exposure_zero_pair_sourced_balance_c2_move_orbit_family": {
                "needed_type": (
                    "complete C2-closed hidden-neutral quotient dynamics family"
                ),
                "needed_for": (
                    "decide whether the primitive-seeded quotient scattering operator is canonical or one "
                    "member of a larger Ward-balanced dynamics family"
                ),
                "report": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_MOVE_ORBIT_FAMILY_REPORT
                ),
                "family_summary": (
                    full_exposure_zero_pair_sourced_balance_c2_move_orbit_family_derived.get(
                        "family_summary"
                    )
                ),
                "move_family_rows_sha256": (
                    full_exposure_zero_pair_sourced_balance_c2_move_orbit_family_derived.get(
                        "move_family_rows_sha256"
                    )
                ),
                "stationary_rows_sha256": (
                    full_exposure_zero_pair_sourced_balance_c2_move_orbit_family_derived.get(
                        "stationary_rows_sha256"
                    )
                ),
                "status": "certified",
            },
            "full_exposure_zero_pair_sourced_balance_c2_dynamics_selector": {
                "needed_type": (
                    "selector table for choosing among certified C2 quotient dynamics"
                ),
                "needed_for": (
                    "separate primitive-seeded, least-action, paired-transport, and spectral-gap "
                    "physical preference criteria"
                ),
                "report": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_DYNAMICS_SELECTOR_REPORT
                ),
                "selector_summary": (
                    full_exposure_zero_pair_sourced_balance_c2_dynamics_selector_derived.get(
                        "selector_summary"
                    )
                ),
                "selector_table_sha256": (
                    full_exposure_zero_pair_sourced_balance_c2_dynamics_selector_derived.get(
                        "selector_table_sha256"
                    )
                ),
                "scored_move_rows_sha256": (
                    full_exposure_zero_pair_sourced_balance_c2_dynamics_selector_derived.get(
                        "scored_move_rows_sha256"
                    )
                ),
                "status": "certified",
            },
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_skeleton": {
                "needed_type": (
                    "Cubical Agda target skeleton for the C2 foundation bridge"
                ),
                "needed_for": (
                    "move the finite UF candidate into a proof-assistant module with a typechecked "
                    "set-quotient HIT skeleton, selector fibers, and contractible singleton witnesses"
                ),
                "report": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SKELETON_REPORT
                ),
                "source_summary": (
                    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_skeleton_derived.get(
                        "source_summary"
                    )
                ),
                "status": "certified_typechecked_skeleton",
            },
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration": {
                "needed_type": (
                    "generated Cubical Agda finite enumeration for the C2 selector foundation"
                ),
                "needed_for": (
                    "make every quotient state, dynamics code, and selector membership an explicit "
                    "typechecked Agda constructor"
                ),
                "report": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_ENUMERATION_REPORT
                ),
                "source_summary": (
                    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_derived.get(
                        "source_summary"
                    )
                ),
                "selector_fiber_counts": (
                    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_derived.get(
                        "selector_fiber_counts"
                    )
                ),
                "status": "certified_typechecked_enumeration",
            },
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_properties": {
                "needed_type": (
                    "Cubical Agda decidable equality, eliminator, and counting layer for generated enumerations"
                ),
                "needed_for": (
                    "make quotient-state and dynamics enumerations usable as finite set-level types inside "
                    "Cubical Agda"
                ),
                "report": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_ENUMERATION_PROPERTIES_REPORT
                ),
                "source_summary": (
                    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_properties_derived.get(
                        "source_summary"
                    )
                ),
                "status": "certified_typechecked_properties",
            },
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_membership": {
                "needed_type": (
                    "Cubical Agda total selector-membership decision function and fiber count proofs"
                ),
                "needed_for": (
                    "turn selector fibers from generated constructors into decidable finite predicates over "
                    "all certified dynamics ids"
                ),
                "report": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_MEMBERSHIP_REPORT
                ),
                "source_summary": (
                    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_membership_derived.get(
                        "source_summary"
                    )
                ),
                "selector_fiber_counts": (
                    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_membership_derived.get(
                        "selector_fiber_counts"
                    )
                ),
                "status": "certified_typechecked_selector_membership",
            },
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_singletons": {
                "needed_type": (
                    "Cubical Agda finite Sigma subtype equivalences for singleton selector fibers"
                ),
                "needed_for": (
                    "turn the five contractible selector fibers into proof-assistant-native finite "
                    "subtypes equivalent to Fin 1"
                ),
                "report": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_SINGLETONS_REPORT
                ),
                "source_summary": (
                    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_singletons_derived.get(
                        "source_summary"
                    )
                ),
                "singleton_selectors": (
                    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_singletons_derived.get(
                        "singleton_selectors"
                    )
                ),
                "status": "certified_typechecked_singleton_finite_subtypes",
            },
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lazy63": {
                "needed_type": (
                    "Cubical Agda finite Sigma subtype equivalence for the lazy spectral-gap selector fiber"
                ),
                "needed_for": (
                    "turn the 63-element lazy spectral-gap ambiguity into a proof-assistant-native finite "
                    "subtype equivalent to Fin 63"
                ),
                "report": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LAZY63_REPORT
                ),
                "source_summary": (
                    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lazy63_derived.get(
                        "source_summary"
                    )
                ),
                "lazy_selector": (
                    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lazy63_derived.get(
                        "lazy_selector"
                    )
                ),
                "actual_c2_kernel_orbit_source": actual_c2_kernel_orbit_sources["lazy63"],
                "status": "certified_typechecked_lazy63_finite_subtype",
            },
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_paired_lazy480": {
                "needed_type": (
                    "Cubical Agda finite Sigma subtype equivalence for the paired lazy spectral-gap selector fiber"
                ),
                "needed_for": (
                    "turn the 480-element paired lazy spectral-gap ambiguity into a "
                    "proof-assistant-native finite subtype equivalent to Fin 480"
                ),
                "report": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_PAIRED_LAZY480_REPORT
                ),
                "source_summary": (
                    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_paired_lazy480_derived.get(
                        "source_summary"
                    )
                ),
                "paired_lazy_selector": (
                    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_paired_lazy480_derived.get(
                        "paired_lazy_selector"
                    )
                ),
                "actual_c2_kernel_orbit_source": actual_c2_kernel_orbit_sources[
                    "paired_lazy480"
                ],
                "status": "certified_typechecked_paired_lazy480_finite_subtype",
            },
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543": {
                "needed_type": (
                    "Cubical Agda finite Sigma subtype equivalence for the raw spectral-gap selector fiber"
                ),
                "needed_for": (
                    "turn the full 543-element raw spectral-gap ambiguity into a proof-assistant-native "
                    "finite subtype equivalent to Fin 543"
                ),
                "report": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_REPORT
                ),
                "source_summary": (
                    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_derived.get(
                        "source_summary"
                    )
                ),
                "raw_selector": (
                    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_derived.get(
                        "raw_selector"
                    )
                ),
                "actual_c2_kernel_orbit_source": actual_c2_kernel_orbit_sources["raw543"],
                "status": "certified_typechecked_raw543_finite_subtype",
            },
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_indexed": {
                "needed_type": (
                    "compact indexed Cubical Agda finite Sigma subtype equivalence for the raw spectral-gap selector fiber"
                ),
                "needed_for": (
                    "replace large generated FinData constructor normal forms on the raw543 finite-subtype path"
                ),
                "report": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_RAW543_INDEXED_REPORT
                ),
                "source_summary": (
                    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_indexed_derived.get(
                        "source_summary"
                    )
                ),
                "raw_selector": (
                    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_indexed_derived.get(
                        "raw_selector"
                    )
                ),
                "actual_c2_kernel_orbit_source": actual_c2_kernel_orbit_sources[
                    "raw543_indexed"
                ],
                "status": "certified_typechecked_raw543_indexed_finite_subtype",
            },
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_split": {
                "needed_type": (
                    "compact indexed Cubical Agda finite Sigma subtype equivalences for the lazy63 and paired-lazy480 selector fibers"
                ),
                "needed_for": (
                    "switch the active selector finite-subtype spine away from generated FinData "
                    "constructor normal forms for all non-singleton spectral fibers"
                ),
                "report": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_SPLIT_REPORT
                ),
                "actual_c2_kernel_orbit_source": actual_c2_kernel_orbit_sources[
                    "indexed_split"
                ],
                "indexed_selector_rows": indexed_split_rows,
                "status": "certified_typechecked_indexed_lazy63_and_paired_lazy480_finite_subtypes",
            },
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_lookup": {
                "needed_type": (
                    "lookup-collapsed indexed Cubical Agda finite Sigma subtype equivalences for raw543, lazy63, and paired-lazy480"
                ),
                "needed_for": (
                    "remove generated inspect/injection right-inverse rows from all non-singleton "
                    "spectral selector finite-subtype modules"
                ),
                "report": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_INDEXED_LOOKUP_REPORT
                ),
                "actual_c2_kernel_orbit_source": actual_c2_kernel_orbit_sources[
                    "indexed_lookup"
                ],
                "lookup_selector_rows": indexed_lookup_rows,
                "status": "certified_typechecked_lookup_collapsed_indexed_finite_subtypes",
            },
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table": {
                "needed_type": (
                    "verified JSON/CSV selected-witness table plus Cubical soundness module for raw543, lazy63, and paired-lazy480"
                ),
                "needed_for": (
                    "audit the selected selector witness rows as a standalone Halloween source "
                    "package consumed by the lookup emitter"
                ),
                "report": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_LOOKUP_TABLE_REPORT
                ),
                "lookup_table_row_count": (
                    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table_derived.get(
                        "lookup_table_row_count"
                    )
                ),
                "lookup_table_row_count_by_selector": lookup_table_row_count_by_selector,
                "lookup_table_selector_summaries": lookup_table_selector_summaries,
                "lookup_witness_source_package": lookup_table_source_package,
                "actual_c2_kernel_orbit_source": actual_c2_kernel_orbit_sources[
                    "lookup_table"
                ],
                "status": "certified_lookup_witness_table_source_package_and_typechecked_soundness",
            },
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_emitter_factorization": {
                "needed_type": (
                    "shared emitter for certified Cubical Agda selector finite-subtype modules"
                ),
                "needed_for": (
                    "keep singleton, lazy63, paired-lazy480, and raw543 finite-subtype proof "
                    "generators aligned without changing their certified Agda sources"
                ),
                "report": rel(
                    FULL_EXPOSURE_ZERO_PAIR_SOURCED_BALANCE_C2_CUBICAL_AGDA_SELECTOR_FINITE_SUBTYPE_EMITTER_FACTORIZATION_REPORT
                ),
                "source_summary": (
                    full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_emitter_factorization_derived.get(
                        "factorized_generators"
                    )
                ),
                "status": "certified_emitter_factorization_preserves_sources",
            },
        },
        "missing_maps": {
            "full_drinfeld_projection_coordinates": {
                "needed_type": "full 39 x 985 Drinfeld idempotent/character coordinate matrix",
                "needed_for": "compare the tube-visible zero coefficient against the full A985 projection model",
                "character_table_materialized": character_values_materialized,
                "idempotent_matrix_materialized": idempotent_matrix_materialized,
                "status": "hash-only in current JSON artifacts",
            },
            "complete_section_entries": {
                "needed_type": "full S: Loop_297 -> TubePair_44521 coefficient table, or deterministic recomputation",
                "needed_for": "lift an already-defined Loop_297 vector through the certified section",
                "complete_section_materialized": complete_section_materialized,
                "status": "hash-only but recomputable; not the primary blocker",
            },
        },
        "formal_obligation": {
            "define_boundary_lift": "discharged by data/invariants/d20/boundary_to_loop/report.json",
            "materialize_or_recompute_pi33_functional": (
                "discharged for the tube-visible Loop_297 functional by "
                "data/invariants/d20/theorems/sector33_boundary_annihilation/report.json"
            ),
            "then_compute": "c_33(gamma_8) = 0 for the certified bare lambda_boundary lift in F_1000003.",
            "height_coherent_recovery": (
                "discharged for gamma_8 by "
                "data/invariants/d20/theorems/sector33_height_coherent_transport/report.json"
            ),
            "unique_single_sector_support": (
                "discharged by "
                "data/invariants/d20/theorems/sector33_unique_public_zero_support/report.json"
            ),
            "public_shadow_kernel_classification": (
                "discharged by data/invariants/d20/theorems/sector_public_shadow_kernel/report.json"
            ),
            "idempotent_support_admissibility": (
                "discharged by "
                "data/invariants/d20/theorems/sector_idempotent_support_admissibility/report.json"
            ),
            "minimal_composite_transport_classification": (
                "discharged by "
                "data/invariants/d20/theorems/minimal_composite_null_supports_transport/report.json"
            ),
            "superselection_flux_balance_extension": (
                "discharged by "
                "data/invariants/d20/theorems/superselection_flux_balance_extension/report.json"
            ),
            "typed_nonexact_optical_flux_update": (
                "discharged by "
                "data/invariants/d20/theorems/typed_nonexact_optical_flux_update/report.json"
            ),
            "sector26_invariant_suite": (
                "discharged by data/invariants/d20/theorems/sector26_invariant_suite/report.json"
            ),
            "finite_anomaly_counter": (
                "discharged by data/invariants/d20/theorems/finite_anomaly_counter/report.json"
            ),
            "sector26_anomaly_cancellation": (
                "discharged by data/invariants/d20/theorems/sector26_anomaly_cancellation/report.json"
            ),
            "anomaly_cancelled_flux_balance_recovery": (
                "discharged by "
                "data/invariants/d20/theorems/anomaly_cancelled_flux_balance_recovery/report.json"
            ),
            "gamma8_obstruction_correction": (
                "discharged by data/invariants/d20/theorems/gamma8_obstruction_correction/report.json"
            ),
            "general_obstruction_correction_suite": (
                "discharged by data/invariants/d20/theorems/general_obstruction_correction_suite/report.json"
            ),
            "global_counterterm_lattice": (
                "discharged by data/invariants/d20/theorems/global_counterterm_lattice/report.json"
            ),
            "global_corrected_charge_map": (
                "discharged by data/invariants/d20/theorems/global_corrected_charge_map/report.json"
            ),
            "global_corrected_hidden_split_symmetry": (
                "discharged by "
                "data/invariants/d20/theorems/global_corrected_hidden_split_symmetry/report.json"
            ),
            "hidden_split_augmented_ledger_stabilizer": (
                "discharged by "
                "data/invariants/d20/theorems/hidden_split_augmented_ledger_stabilizer/report.json"
            ),
            "canonical_flux_balance_gauge": (
                "discharged by data/invariants/d20/theorems/canonical_flux_balance_gauge/report.json"
            ),
            "canonical_loop_pi33_obstruction": (
                "discharged by data/invariants/d20/theorems/canonical_loop_pi33_obstruction/report.json"
            ),
            "canonical_finite_ward_identity": (
                "discharged by data/invariants/d20/theorems/canonical_finite_ward_identity/report.json"
            ),
            "canonical_all_mask_ward_identity": (
                "discharged by "
                "data/invariants/d20/theorems/canonical_all_mask_ward_identity/report.json"
            ),
            "finite_bms_carrollian_flux_balance": (
                "discharged by "
                "data/invariants/d20/theorems/finite_bms_carrollian_flux_balance/report.json"
            ),
            "hidden_packet_charge_frame_classifier": (
                "discharged by "
                "data/invariants/d20/theorems/hidden_packet_charge_frame_classifier/report.json"
            ),
            "canonical_finite_scattering_table": (
                "discharged by "
                "data/invariants/d20/theorems/canonical_finite_scattering_table/report.json"
            ),
            "loop297_scattering_amplitude_lift": (
                "discharged by "
                "data/invariants/d20/theorems/loop297_scattering_amplitude_lift/report.json"
            ),
            "compact_amplitude_quotient": (
                "discharged by "
                "data/invariants/d20/theorems/compact_amplitude_quotient/report.json"
            ),
            "reduced_amplitude_quotient_scattering_automaton": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "reduced_amplitude_quotient_scattering_automaton/report.json"
            ),
            "amplitude_quotient_fourier_mode_classifier": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "amplitude_quotient_fourier_mode_classifier/report.json"
            ),
            "finite_virasoro_string_kernel_candidate": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "finite_virasoro_string_kernel_candidate/report.json"
            ),
            "finite_virasoro_generator_algebra": (
                "discharged by "
                "data/invariants/d20/theorems/finite_virasoro_generator_algebra/report.json"
            ),
            "finite_central_extension_anomaly_cocycle": (
                "discharged by "
                "data/invariants/d20/theorems/finite_central_extension_anomaly_cocycle/report.json"
            ),
            "finite_parity_central_extension_group": (
                "discharged by "
                "data/invariants/d20/theorems/finite_parity_central_extension_group/report.json"
            ),
            "projective_kernel_packet_tenfold_way": (
                "discharged by "
                "data/invariants/d20/theorems/projective_kernel_packet_tenfold_way/report.json"
            ),
            "projective_packet_spectral_charge_table": (
                "discharged by "
                "data/invariants/d20/theorems/projective_packet_spectral_charge_table/report.json"
            ),
            "projective_packet_charge_frame_classifier": (
                "discharged by "
                "data/invariants/d20/theorems/projective_packet_charge_frame_classifier/report.json"
            ),
            "packet239_stabilizer_seed_candidate": (
                "discharged by "
                "data/invariants/d20/theorems/packet239_stabilizer_seed_candidate/report.json"
            ),
            "packet239_seed_propagation": (
                "discharged by "
                "data/invariants/d20/theorems/packet239_seed_propagation/report.json"
            ),
            "full_exposure_packet_propagation_cells": (
                "discharged by "
                "data/invariants/d20/theorems/full_exposure_packet_propagation_cells/report.json"
            ),
            "full_exposure_packet_propagation_graph": (
                "discharged by "
                "data/invariants/d20/theorems/full_exposure_packet_propagation_graph/report.json"
            ),
            "full_exposure_rank10_tenfold_alignment": (
                "discharged by "
                "data/invariants/d20/theorems/full_exposure_rank10_tenfold_alignment/report.json"
            ),
            "full_exposure_radical_gate_stabilizer": (
                "discharged by "
                "data/invariants/d20/theorems/full_exposure_radical_gate_stabilizer/report.json"
            ),
            "full_exposure_radical_gate_stabilizer_lift": (
                "discharged by "
                "data/invariants/d20/theorems/full_exposure_radical_gate_stabilizer_lift/report.json"
            ),
            "full_exposure_label_breaking_factorization": (
                "discharged by "
                "data/invariants/d20/theorems/full_exposure_label_breaking_factorization/report.json"
            ),
            "full_exposure_canonical_labelled_frame": (
                "discharged by "
                "data/invariants/d20/theorems/full_exposure_canonical_labelled_frame/report.json"
            ),
            "full_exposure_label_coordinate_transition_operator": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "full_exposure_label_coordinate_transition_operator/report.json"
            ),
            "full_exposure_label_coordinate_spectral_boundary": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "full_exposure_label_coordinate_spectral_boundary/report.json"
            ),
            "full_exposure_label_coordinate_green_response": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "full_exposure_label_coordinate_green_response/report.json"
            ),
            "full_exposure_zero_pair_propagator_charge_kernel": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "full_exposure_zero_pair_propagator_charge_kernel/report.json"
            ),
            "full_exposure_zero_pair_propagator_symmetry_ward": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "full_exposure_zero_pair_propagator_symmetry_ward/report.json"
            ),
            "full_exposure_zero_pair_source_to_closed_return_coupling": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "full_exposure_zero_pair_source_to_closed_return_coupling/report.json"
            ),
            "full_exposure_zero_pair_ward_kernel_height_selector": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "full_exposure_zero_pair_ward_kernel_height_selector/report.json"
            ),
            "full_exposure_zero_pair_selected_sourced_ward_balance": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "full_exposure_zero_pair_selected_sourced_ward_balance/report.json"
            ),
            "full_exposure_zero_pair_sourced_balance_cone": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "full_exposure_zero_pair_sourced_balance_cone/report.json"
            ),
            "full_exposure_zero_pair_sourced_balance_shortest_paths": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "full_exposure_zero_pair_sourced_balance_shortest_paths/report.json"
            ),
            "full_exposure_zero_pair_sourced_balance_transport_families": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "full_exposure_zero_pair_sourced_balance_transport_families/report.json"
            ),
            "full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient/report.json"
            ),
            "full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly/report.json"
            ),
            "full_exposure_zero_pair_sourced_balance_c2_quotient_transport_ledger": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "full_exposure_zero_pair_sourced_balance_c2_quotient_transport_ledger/report.json"
            ),
            "full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator/report.json"
            ),
            "full_exposure_zero_pair_sourced_balance_c2_move_orbit_family": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "full_exposure_zero_pair_sourced_balance_c2_move_orbit_family/report.json"
            ),
            "full_exposure_zero_pair_sourced_balance_c2_dynamics_selector": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "full_exposure_zero_pair_sourced_balance_c2_dynamics_selector/report.json"
            ),
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_skeleton": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_skeleton/report.json"
            ),
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration/report.json"
            ),
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_properties": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_properties/report.json"
            ),
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_membership": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_membership/report.json"
            ),
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_singletons": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_singletons/report.json"
            ),
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lazy63": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lazy63/report.json"
            ),
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_paired_lazy480": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_paired_lazy480/report.json"
            ),
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543/report.json"
            ),
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_emitter_factorization": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_emitter_factorization/report.json"
            ),
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_indexed": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_indexed/report.json"
            ),
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_split": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_split/report.json"
            ),
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_lookup": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_lookup/report.json"
            ),
            "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table": (
                "discharged by "
                "data/invariants/d20/theorems/"
                "full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table/report.json"
            ),
            "remaining_recovery_obligation": (
                "Stage the Halloween source-registry, theorem-registry, and Agda replay artifacts for review."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Stage the Halloween source-registry, theorem-registry, and Agda replay artifacts for review."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_report(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_report()
    manifest = {
        "schema": "d20.proof_obligation.cycle8_pi33_projection_coefficient_manifest.source_drop",
        "name": OBLIGATION_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "validation_tests": [
            "verify gamma_8 is the certified first obstruction cycle",
            "verify Pi_33 sector attachment is certified",
            "verify the tube section exists and satisfies P S = I",
            "verify the certified boundary-to-Loop_297 map exists and lifts gamma_8",
            "verify the tube-visible Pi_33 functional evaluates the bare gamma_8 lift to zero",
            "verify the height-coherent transport recovers the sector-33 residual from edge/circuit data",
            "verify the global height-coherent transport covers all 2047 nonzero residue classes",
            "verify sector 33 is the unique single-sector public-zero support among all 39 sectors",
            "verify the full sector public-shadow kernel has rank 12 and nullity 27",
            "verify the public-zero idempotent boundary-null supports are classified",
            "verify minimal composite null supports have positive self-transport and zero transport to Pi_33",
            "verify the superselection flux-balance extension tracks hidden public-zero labels",
            "verify the typed non-exact optical flux update sends height residuals to R33",
            "verify the sector-26 invariant suite certifies quotient stability and the complete mod-26 clock",
            "verify the finite anomaly counter classifies the mod-26 clock additivity defect",
            "verify the sector-26 anomaly-cancellation theorem classifies maximal cancelled packets",
            "verify anomaly-cancelled flux-balance recovery on the certified packets",
            "verify the gamma_8 obstruction correction and corrected packet geometry",
            "verify the general obstruction-correction suite over all basis coordinates",
            "verify the global counterterm lattice balances the full closed-return residue group",
            "verify the global corrected charge map is rank-one beyond public exact closed-return flux",
            "verify the corrected hidden split reduces public graph symmetry to a C2 stabilizer",
            "verify the full augmented ledger stabilizer is identity after imposing counterterms/actions/charges",
            "verify the canonical root-fixed exact flux-balance gauge is unique",
            "verify the canonical gauge pushforward preserves the cycle-8 Loop_297/Pi_33 obstruction statement",
            "verify the canonical finite Ward identity balances public zero, bare Pi_33 zero, and R33 residual",
            "verify the canonical all-mask Ward identity balances all 2048 closed-return residues",
            "verify the finite BMS/Carrollian projection names and balances public and hidden terms",
            "verify the hidden packet charge-frame classifier separates packets through action invariants",
            "verify the canonical finite scattering table covers all primitive-generator transitions",
            "verify the Loop_297 scattering amplitude lift attaches generator packets and balances transfers",
            "verify the compact amplitude quotient collapses tube-zero packets and separates generator chains",
            "verify the reduced amplitude-quotient scattering automaton is regular, reversible, spectral, and sector-classified",
            "verify the amplitude-quotient Fourier mode classifier diagonalizes and sector-26-classifies all 2048 modes",
            "verify the finite Virasoro/string-kernel candidate identifies the rank-10 sector-26 closure",
            "verify the finite Virasoro generator algebra and its sector-26 clock defect",
            "verify the finite central-extension/anomaly cocycle separates the Z/26 coboundary from the F2 survivor",
            "verify the finite parity central-extension group and signed projective kernel action",
            "verify the projective kernel packet decomposition and finite tenfold-way witness",
            "verify the projective packet spectral/charge table and distinguished packet sets",
            "verify the projective packet charge-frame classifier and packet 239 isolation",
            "verify the packet-239 stabilizer comparison and seed-candidate status",
            "verify the packet-239 non-kernel seed propagation cell",
            "verify the uniform non-kernel propagation cells for all 20 full-exposure packets",
            "verify the weighted full-exposure propagation graph and its ten active-partner doublets",
            "verify the rank-10/tenfold alignment and non-basis result for the graph doublets",
            "verify the affine stabilizer classification of the nonlinear full-exposure radical gate",
            "verify the radical-gate stabilizer lift and label-breaking survivor counts",
            "verify the minimal invariant-axis factorization of label symmetry breaking",
            "verify the canonical labelled full-exposure frame and id-free packet-239 selection",
            "verify the full-exposure label-coordinate transition operator",
            "verify the full-exposure label-coordinate spectral-boundary theorem",
            "verify the full-exposure label-coordinate Green/resolvent response theorem",
            "verify the zero-pair propagator charge-kernel theorem",
            "verify the zero-pair propagator symmetry/Ward compatibility theorem",
            "verify the zero-pair source-to-closed-return coupling no-go and neutral kernel lift",
            "verify the zero-pair Ward-kernel height selector and selected mask 288",
            "verify the zero-pair selected sourced Ward/BMS balance for mask 288",
            "verify the zero-pair one-step sourced-balance cone and mask-288 apex limits",
            "verify the zero-pair all-kernel sourced-balance shortest-path classifier",
            "verify the zero-pair sourced-balance transport-family compression and symmetry-level resolution",
            "verify the zero-pair sourced-balance label-relaxed orbit quotient and forgotten-label certificate",
            "verify the zero-pair sourced-balance C2 quotient anomaly and twisted balance descent",
            "verify the zero-pair sourced-balance C2 quotient transport ledger, primal operator, and spectrum",
            "verify the zero-pair sourced-balance C2 quotient scattering operator and stationary Ward balance",
            "verify the zero-pair sourced-balance C2 move-orbit family and canonicality split",
            "verify the zero-pair sourced-balance C2 dynamics selector and spectral-gap split",
            "verify the zero-pair sourced-balance C2 Cubical foundation bridge candidate",
            "verify the zero-pair sourced-balance C2 Cubical Agda skeleton and typecheck artifact",
            "verify the zero-pair sourced-balance C2 Cubical Agda generated enumeration",
            "verify the zero-pair sourced-balance C2 Cubical Agda generated enumeration properties",
            "verify the zero-pair sourced-balance C2 Cubical Agda selector-membership decisions",
            "verify the zero-pair sourced-balance C2 Cubical Agda selector finite-subtype singletons",
            "verify the zero-pair sourced-balance C2 Cubical Agda lazy63 selector finite subtype",
            "verify the zero-pair sourced-balance C2 Cubical Agda paired-lazy480 selector finite subtype",
            "verify the zero-pair sourced-balance C2 Cubical Agda raw543 selector finite subtype",
            "verify the zero-pair sourced-balance C2 Cubical Agda finite-subtype emitter factorization",
            "verify the zero-pair sourced-balance C2 Cubical Agda selector finite-subtype lookup table and soundness module",
            "verify the full Drinfeld idempotent matrix remains hash-only in the current JSON artifacts",
        ],
    }
    manifest["report_sha256"] = report["certificate_sha256"]
    manifest["manifest_sha256"] = sha_json({k: v for k, v in manifest.items() if k != "manifest_sha256"})

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    update_obligation_index(report, out_dir)
    return report


def main() -> None:
    report = write_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report.get("all_checks_pass"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
