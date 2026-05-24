from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, HCYCLE_INVARIANTS, LAYERS, ROOT


OBLIGATION_ID = "cycle8_pi33_projection_coefficient"
DEFAULT_OUT_DIR = D20_INVARIANTS / "proof_obligations" / OBLIGATION_ID

SECTOR_ATTACHMENT_REPORT = (
    D20_INVARIANTS / "theorems" / "sector33_residual_attachment" / "report.json"
)
D20_EDGES_CSV = HCYCLE_INVARIANTS / "subscript_Hcycle_d20_edges.csv"
PRIMITIVE_CYCLES_CSV = HCYCLE_INVARIANTS / "subscript_Hcycle_primitive_cycles.csv"
TUBE_PROJECTION_SECTION = LAYERS / "tube" / "projection_section.json"
FULL_A985_LIFT = LAYERS / "drinfeld" / "full_a985_lift.json"
WEDDERBURN_TRACE = LAYERS / "drinfeld" / "wedderburn_trace.json"
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
UNIQUE_PUBLIC_ZERO_CARRIER_REPORT = (
    D20_INVARIANTS / "theorems" / "sector33_unique_public_zero_carrier" / "report.json"
)
SECTOR_PUBLIC_SHADOW_KERNEL_REPORT = (
    D20_INVARIANTS / "theorems" / "sector_public_shadow_kernel" / "report.json"
)
SECTOR_IDEMPOTENT_CARRIER_ADMISSIBILITY_REPORT = (
    D20_INVARIANTS / "theorems" / "sector_idempotent_carrier_admissibility" / "report.json"
)
MINIMAL_COMPOSITE_TRANSPORT_REPORT = (
    D20_INVARIANTS / "theorems" / "minimal_composite_null_carriers_transport" / "report.json"
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
    unique_public_zero_carrier = (
        load_json(UNIQUE_PUBLIC_ZERO_CARRIER_REPORT)
        if UNIQUE_PUBLIC_ZERO_CARRIER_REPORT.exists()
        else {}
    )
    sector_public_shadow_kernel = (
        load_json(SECTOR_PUBLIC_SHADOW_KERNEL_REPORT)
        if SECTOR_PUBLIC_SHADOW_KERNEL_REPORT.exists()
        else {}
    )
    sector_idempotent_carrier_admissibility = (
        load_json(SECTOR_IDEMPOTENT_CARRIER_ADMISSIBILITY_REPORT)
        if SECTOR_IDEMPOTENT_CARRIER_ADMISSIBILITY_REPORT.exists()
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
    unique_public_zero_derived = unique_public_zero_carrier.get("derived", {})
    public_shadow_kernel_derived = sector_public_shadow_kernel.get("derived", {})
    idempotent_admissibility_derived = sector_idempotent_carrier_admissibility.get("derived", {})
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
    unique_public_zero_carrier_certified = (
        unique_public_zero_carrier.get("status")
        == "D20_SECTOR33_UNIQUE_PUBLIC_ZERO_CARRIER_CERTIFIED"
        and unique_public_zero_carrier.get("all_checks_pass") is True
    )
    sector_public_shadow_kernel_certified = (
        sector_public_shadow_kernel.get("status") == "D20_SECTOR_PUBLIC_SHADOW_KERNEL_CERTIFIED"
        and sector_public_shadow_kernel.get("all_checks_pass") is True
    )
    sector_idempotent_carrier_admissibility_certified = (
        sector_idempotent_carrier_admissibility.get("status")
        == "D20_SECTOR_IDEMPOTENT_CARRIER_ADMISSIBILITY_CLASSIFIED"
        and sector_idempotent_carrier_admissibility.get("all_checks_pass") is True
    )
    minimal_composite_transport_certified = (
        minimal_composite_transport.get("status")
        == "D20_MINIMAL_COMPOSITE_NULL_CARRIERS_TRANSPORT_CLASSIFIED"
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
        "unique_public_zero_carrier_is_certified": unique_public_zero_carrier_certified,
        "sector33_is_unique_single_sector_public_zero_carrier": unique_public_zero_derived.get(
            "public_zero_sectors"
        )
        == [33]
        and unique_public_zero_carrier.get("checks", {}).get(
            "sector33_is_unique_single_sector_public_zero_carrier"
        )
        is True,
        "all_nonzero_height_residuals_are_field_nonzero_for_unique_carrier": unique_public_zero_derived.get(
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
        "sector_idempotent_carrier_admissibility_is_certified": (
            sector_idempotent_carrier_admissibility_certified
        ),
        "public_zero_idempotent_boundary_null_carriers_are_classified": idempotent_admissibility_derived.get(
            "nonzero_public_zero_boundary_null_supports"
        )
        == [[6, 26], [25, 26], [33], [6, 26, 33], [25, 26, 33]],
        "pi33_is_unique_primitive_and_height_support_exact_carrier": idempotent_admissibility_derived.get(
            "primitive_single_sector_public_zero"
        )
        == [33]
        and idempotent_admissibility_derived.get("height_support_exact_carriers_for_certified_transport")
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
        "D20_CYCLE8_PI33_GAMMA8_OBSTRUCTION_CORRECTION_CERTIFIED"
        if all_checks_pass
        else "D20_CYCLE8_PI33_PROJECTION_OBLIGATION_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.proof_obligation.cycle8_pi33_projection_coefficient.source_drop",
        "status": status,
        "closure_state": (
            "bare_lambda_zero; height_coherent_transport_recovers_nonzero_residual; "
            "sector33_unique_single_sector_public_zero_carrier; public_shadow_kernel_dimension_27; "
            "public_zero_idempotent_carriers_classified; minimal_composite_superselection_transport_classified; "
            "augmented_flux_ledger_certified; typed_nonexact_optical_flux_update_certified; "
            "sector26_invariant_suite_certified; finite_anomaly_counter_certified; "
            "sector26_anomaly_cancellation_certified; anomaly_cancelled_flux_balance_recovery_certified; "
            "gamma8_obstruction_correction_certified"
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
            "single-sector public-zero carrier. The full linear public-zero sector span is also classified: "
            "the combined A42/A12 shadow matrix has rank 12 and kernel dimension 27, so Pi_33 uniqueness is "
            "coordinate-axis/single-sector uniqueness, not uniqueness in the unconstrained linear span. The "
            "idempotent carrier classification shows five nonzero public-zero boundary-null idempotent sector "
            "sums; Pi_33 is the unique primitive carrier and the unique support-exact carrier for the certified "
            "sector-33 height transport. The two minimal non-Pi_33 null composites are not gauge zero: "
            "{6,26} and {25,26} have positive self-transport and zero transport to/from Pi_33, so they are "
            "isolated public-zero superselection carriers. The finite flux-balance ledger is extended with "
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
            "add +5 to normalized R33 on basis coordinate 8, sending gamma_8 to the order-two value 13."
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
            "sector33_unique_public_zero_carrier_report": {
                "path": rel(UNIQUE_PUBLIC_ZERO_CARRIER_REPORT),
                "sha256": sha_file(UNIQUE_PUBLIC_ZERO_CARRIER_REPORT)
                if UNIQUE_PUBLIC_ZERO_CARRIER_REPORT.exists()
                else None,
            },
            "sector_public_shadow_kernel_report": {
                "path": rel(SECTOR_PUBLIC_SHADOW_KERNEL_REPORT),
                "sha256": sha_file(SECTOR_PUBLIC_SHADOW_KERNEL_REPORT)
                if SECTOR_PUBLIC_SHADOW_KERNEL_REPORT.exists()
                else None,
            },
            "sector_idempotent_carrier_admissibility_report": {
                "path": rel(SECTOR_IDEMPOTENT_CARRIER_ADMISSIBILITY_REPORT),
                "sha256": sha_file(SECTOR_IDEMPOTENT_CARRIER_ADMISSIBILITY_REPORT)
                if SECTOR_IDEMPOTENT_CARRIER_ADMISSIBILITY_REPORT.exists()
                else None,
            },
            "minimal_composite_null_carriers_transport_report": {
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
            "unique_public_zero_carrier": {
                "status": unique_public_zero_carrier.get("status"),
                "definition": unique_public_zero_carrier.get("definition", {}),
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
                "unique_public_zero_carrier": unique_public_zero_derived.get(
                    "unique_public_zero_carrier"
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
            "sector_idempotent_carrier_admissibility": {
                "status": sector_idempotent_carrier_admissibility.get("status"),
                "definition": sector_idempotent_carrier_admissibility.get("definition", {}),
                "nonzero_public_zero_idempotent_supports": idempotent_admissibility_derived.get(
                    "nonzero_public_zero_idempotent_supports"
                ),
                "nonzero_public_zero_boundary_null_supports": idempotent_admissibility_derived.get(
                    "nonzero_public_zero_boundary_null_supports"
                ),
                "primitive_single_sector_public_zero": idempotent_admissibility_derived.get(
                    "primitive_single_sector_public_zero"
                ),
                "height_support_exact_carriers_for_certified_transport": idempotent_admissibility_derived.get(
                    "height_support_exact_carriers_for_certified_transport"
                ),
            },
            "minimal_composite_null_carriers_transport": {
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
                "needed_for": "classify height-derived residuals under the selected sector-33 carrier",
                "report": rel(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT),
                "nonzero_residue_class_count": all_residue_derived.get("nonzero_residue_class_count"),
                "carrier_sector": 33,
                "status": "certified",
            },
            "unique_single_sector_public_zero_carrier": {
                "needed_type": "materialized comparison of all 39 tube-visible sector idempotents",
                "needed_for": "prove the selected sector-33 carrier is the only single-sector public-zero carrier",
                "report": rel(UNIQUE_PUBLIC_ZERO_CARRIER_REPORT),
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
            "sector_idempotent_carrier_admissibility": {
                "needed_type": (
                    "Boolean idempotent carrier classification inside the 39-sector orthogonal idempotent algebra"
                ),
                "needed_for": (
                    "separate primitive/support-exact Pi_33 uniqueness from composite public-zero null carriers"
                ),
                "report": rel(SECTOR_IDEMPOTENT_CARRIER_ADMISSIBILITY_REPORT),
                "nonzero_public_zero_boundary_null_supports": idempotent_admissibility_derived.get(
                    "nonzero_public_zero_boundary_null_supports"
                ),
                "primitive_single_sector_public_zero": idempotent_admissibility_derived.get(
                    "primitive_single_sector_public_zero"
                ),
                "height_support_exact_carriers_for_certified_transport": idempotent_admissibility_derived.get(
                    "height_support_exact_carriers_for_certified_transport"
                ),
                "status": "certified",
            },
            "minimal_composite_null_carriers_transport": {
                "needed_type": (
                    "transport-rank classification of the minimal non-Pi_33 public-zero composite carriers"
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
        },
        "missing_maps": {
            "full_drinfeld_projection_coordinates": {
                "needed_type": "full 39 x 985 Drinfeld idempotent/character coordinate matrix",
                "needed_for": "compare the tube-visible zero coefficient against the full A985 projection model",
                "character_table_materialized": character_values_materialized,
                "idempotent_matrix_materialized": idempotent_matrix_materialized,
                "status": "hash-only in current JSON artifacts",
            },
            "general_obstruction_correction_suite": {
                "needed_type": (
                    "minimal rank-one counterterms for all self-anomalous basis coordinates"
                ),
                "needed_for": (
                    "compare corrected packet geometries across the full closed-return basis and determine "
                    "whether gamma_8 is exceptional or representative"
                ),
                "status": "not yet certified",
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
            "unique_single_sector_carrier": (
                "discharged by "
                "data/invariants/d20/theorems/sector33_unique_public_zero_carrier/report.json"
            ),
            "public_shadow_kernel_classification": (
                "discharged by data/invariants/d20/theorems/sector_public_shadow_kernel/report.json"
            ),
            "idempotent_carrier_admissibility": (
                "discharged by "
                "data/invariants/d20/theorems/sector_idempotent_carrier_admissibility/report.json"
            ),
            "minimal_composite_transport_classification": (
                "discharged by "
                "data/invariants/d20/theorems/minimal_composite_null_carriers_transport/report.json"
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
            "remaining_recovery_obligation": (
                "Generalize obstruction correction: classify minimal rank-one counterterms for every "
                "self-anomalous basis coordinate and compare their corrected packet geometries."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Generalize obstruction correction across all self-anomalous basis coordinates."
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
            "verify sector 33 is the unique single-sector public-zero carrier among all 39 sectors",
            "verify the full sector public-shadow kernel has rank 12 and nullity 27",
            "verify the public-zero idempotent boundary-null carriers are classified",
            "verify minimal composite null carriers have positive self-transport and zero transport to Pi_33",
            "verify the superselection flux-balance extension tracks hidden public-zero labels",
            "verify the typed non-exact optical flux update sends height residuals to R33",
            "verify the sector-26 invariant suite certifies quotient stability and the complete mod-26 clock",
            "verify the finite anomaly counter classifies the mod-26 clock additivity defect",
            "verify the sector-26 anomaly-cancellation theorem classifies maximal cancelled packets",
            "verify anomaly-cancelled flux-balance recovery on the certified packets",
            "verify the gamma_8 obstruction correction and corrected packet geometry",
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
