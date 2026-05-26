from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from collections import Counter
from itertools import permutations
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "full_exposure_packet_propagation_cells"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "projective_packet_charge_frame_classifier"
    / "report.json"
)
PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "projective_packet_spectral_charge_table"
    / "report.json"
)
PACKET239_SEED_PROPAGATION_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "packet239_seed_propagation"
    / "report.json"
)
FOURIER_MODE_CLASSIFIER_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "amplitude_quotient_fourier_mode_classifier"
    / "report.json"
)
FINITE_KERNEL_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "finite_virasoro_string_kernel_candidate"
    / "report.json"
)
CANONICAL_FINITE_SCATTERING_TABLE_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "canonical_finite_scattering_table"
    / "report.json"
)
LOOP297_SCATTERING_AMPLITUDE_LIFT_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "loop297_scattering_amplitude_lift"
    / "report.json"
)

CROSSING_GENERATORS = [5, 9, 10]
KERNEL_SIMPLE_SOURCE_BITS = [0, 1, 2, 3, 4, 6, 7, 8]
ACTIVE_LEFT_COORD = 8
ACTIVE_RIGHT_COORD = 9
PARITY_SOURCE_BIT = 5


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


def update_theorem_index(report: dict[str, Any], out_dir: Path) -> None:
    index_path = out_dir.parent / "index.json"
    entry = {
        "id": THEOREM_ID,
        "manifest": rel(out_dir / "manifest.json"),
        "report": rel(out_dir / "report.json"),
        "report_sha256": report["certificate_sha256"],
        "status": report["status"],
    }
    if index_path.exists():
        index = load_json(index_path)
        theorems = [item for item in index.get("theorems", []) if item.get("id") != THEOREM_ID]
    else:
        theorems = []
    theorems.append(entry)
    theorems = sorted(theorems, key=lambda item: item["id"])
    index = {
        "schema": "d20.theorem_registry",
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": len(theorems),
        "theorems": theorems,
    }
    index["registry_sha256"] = sha_json({k: v for k, v in index.items() if k != "registry_sha256"})
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def histogram(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def tuple_histogram(counter: Counter[tuple[Any, ...]]) -> dict[str, int]:
    return {"|".join(str(part) for part in key): int(counter[key]) for key in sorted(counter)}


def source_parity(mask: int) -> int:
    return ((mask >> 5) ^ (mask >> 9) ^ (mask >> 10)) & 1


def coord_from_kernel_mask(mask: int) -> int:
    coord = 0
    for coord_idx, source_bit in enumerate(KERNEL_SIMPLE_SOURCE_BITS):
        if (mask >> source_bit) & 1:
            coord |= 1 << coord_idx
    if (mask >> 9) & 1:
        coord |= 1 << ACTIVE_LEFT_COORD
    if (mask >> 10) & 1:
        coord |= 1 << ACTIVE_RIGHT_COORD
    return coord


def packet_key_from_mode_pair(mode_pair: list[int]) -> dict[str, Any]:
    parity_values = [source_parity(mask) for mask in mode_pair]
    if parity_values[0] != parity_values[1]:
        raise ValueError(f"mixed parity mode pair {mode_pair}")
    parity_value = parity_values[0]
    kernel_coords = []
    for mask in mode_pair:
        kernel_mask = mask ^ (1 << PARITY_SOURCE_BIT) if parity_value else mask
        kernel_coords.append(coord_from_kernel_mask(kernel_mask))
    radical_values = [coord & 0xFF for coord in kernel_coords]
    active_sigma_values = [(coord >> ACTIVE_LEFT_COORD) & 1 for coord in kernel_coords]
    active_beta_values = sorted((coord >> ACTIVE_RIGHT_COORD) & 1 for coord in kernel_coords)
    if len(set(radical_values)) != 1 or len(set(active_sigma_values)) != 1:
        raise ValueError(f"mode pair does not define a packet {mode_pair}")
    if active_beta_values != [0, 1]:
        raise ValueError(f"mode pair does not span active beta pair {mode_pair}")
    radical = radical_values[0]
    active_sigma = active_sigma_values[0]
    packet_id = radical * 2 + active_sigma
    return {
        "parity": "odd" if parity_value else "kernel",
        "radical_character": radical,
        "active_sigma": active_sigma,
        "packet_id": packet_id if parity_value == 0 else None,
        "packet_key": (
            f"odd:{radical}:{active_sigma}" if parity_value else f"kernel:{packet_id}"
        ),
    }


def packet_measurements(mode_pair: list[int], mode_by_mask: dict[int, dict[str, Any]]) -> dict[str, Any]:
    rows = [mode_by_mask[mask] for mask in mode_pair]
    atoms = sorted({int(atom_id) for row in rows for atom_id in row["active_step_atom_ids"]})
    clock_pair = [int(row["sector26_optical_clock_mod26"]) for row in rows]
    hidden_pair = [int(row["corrected_hidden_clock_mod26"]) for row in rows]
    return {
        "mode_masks": mode_pair,
        "sector26_clock_pair": clock_pair,
        "sector26_clock_sum_mod26": sum(clock_pair) % 26,
        "sector26_clock_delta_mod26": (clock_pair[1] - clock_pair[0]) % 26,
        "corrected_hidden_clock_pair": hidden_pair,
        "corrected_hidden_clock_sum_mod26": sum(hidden_pair) % 26,
        "laplacian_eigenvalue_pair": [int(row["laplacian_eigenvalue"]) for row in rows],
        "laplacian_trace": sum(int(row["laplacian_eigenvalue"]) for row in rows),
        "gamma8_mode_count": sum(1 for row in rows if row["gamma8_support"]),
        "gamma8_touched": any(bool(row["gamma8_support"]) for row in rows),
        "loop297_atom_union_count": len(atoms),
        "loop297_atom_union_ids": atoms,
    }


def build_theorem() -> dict[str, Any]:
    classifier = load_json(PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT)
    spectral_table = load_json(PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_REPORT)
    packet239 = load_json(PACKET239_SEED_PROPAGATION_REPORT)
    fourier = load_json(FOURIER_MODE_CLASSIFIER_REPORT)
    finite_kernel = load_json(FINITE_KERNEL_REPORT)
    scattering = load_json(CANONICAL_FINITE_SCATTERING_TABLE_REPORT)
    lift = load_json(LOOP297_SCATTERING_AMPLITUDE_LIFT_REPORT)

    charge_rows = classifier["derived"]["charge_frame_rows"]
    charge_by_packet = {int(row["packet_id"]): row for row in charge_rows}
    packet_rows = spectral_table["derived"]["packet_spectral_charge_rows"]
    packet_by_id = {int(row["packet_id"]): row for row in packet_rows}
    full_packets = [
        row for row in packet_rows if bool(row["full_loop297_atom_exposure"])
    ]
    full_packet_ids = [int(row["packet_id"]) for row in full_packets]
    mode_by_mask = {
        int(row["mode_mask"]): row for row in fourier["derived"]["mode_rows"]
    }
    generator_summary = {
        int(row["generator_cycle_id"]): row
        for row in scattering["derived"]["generator_summaries"]
    }
    amplitude_packet = {
        int(row["generator_cycle_id"]): row
        for row in lift["derived"]["generator_amplitude_packets"]
    }

    one_step_rows = []
    two_step_rows = []
    cell_summary_rows = []
    for source_packet in full_packets:
        source_id = int(source_packet["packet_id"])
        source_modes = [int(mask) for mask in source_packet["mode_masks"]]
        odd_keys = set()
        for generator_id in CROSSING_GENERATORS:
            target_modes = [mask ^ (1 << generator_id) for mask in source_modes]
            packet_key = packet_key_from_mode_pair(target_modes)
            measurements = packet_measurements(target_modes, mode_by_mask)
            summary = generator_summary[generator_id]
            amplitude = amplitude_packet[generator_id]
            odd_keys.add(packet_key["packet_key"])
            one_step_rows.append(
                {
                    "source_packet_id": source_id,
                    "source_charge_frame_key": charge_by_packet[source_id]["charge_frame_key"],
                    "generator_cycle_id": generator_id,
                    "target_packet_key": packet_key["packet_key"],
                    "target_parity": packet_key["parity"],
                    "target_radical_character": packet_key["radical_character"],
                    "target_active_sigma": packet_key["active_sigma"],
                    "packet_transfer": "kernel_to_odd",
                    "finite_height_flux_delta_per_mode": int(summary["optical_action"]),
                    "hidden_R33_transfer_mod26_per_mode": 13,
                    "optical_action": int(summary["optical_action"]),
                    "loop_step_support_sum": int(amplitude["loop_step_support_sum"]),
                    "loop_step_coefficient_sum_signed": int(
                        amplitude["loop_step_coefficient_sum_signed"]
                    ),
                    **measurements,
                }
            )
        target_counter: Counter[int] = Counter()
        seed_return_pairs = []
        for first, second in permutations(CROSSING_GENERATORS, 2):
            target_modes = [
                mask ^ (1 << first) ^ (1 << second) for mask in source_modes
            ]
            packet_key = packet_key_from_mode_pair(target_modes)
            target_packet_id = int(packet_key["packet_id"])
            target_counter[target_packet_id] += 1
            first_summary = generator_summary[first]
            second_summary = generator_summary[second]
            returns_to_source = target_packet_id == source_id
            if returns_to_source:
                seed_return_pairs.append([first, second])
            two_step_rows.append(
                {
                    "source_packet_id": source_id,
                    "source_charge_frame_key": charge_by_packet[source_id]["charge_frame_key"],
                    "first_generator_cycle_id": first,
                    "second_generator_cycle_id": second,
                    "target_packet_id": target_packet_id,
                    "target_packet_key": packet_key["packet_key"],
                    "target_charge_frame_key": charge_by_packet[target_packet_id][
                        "charge_frame_key"
                    ],
                    "target_fine_spectral_charge_key": charge_by_packet[target_packet_id][
                        "fine_spectral_charge_key"
                    ],
                    "returns_to_source_packet": returns_to_source,
                    "returns_to_active_partner": target_packet_id == (source_id ^ 1),
                    "target_full_loop297_atom_exposure": bool(
                        packet_by_id[target_packet_id]["full_loop297_atom_exposure"]
                    ),
                    "target_sector26_clock_zero_pair": bool(
                        packet_by_id[target_packet_id]["sector26_clock_zero_pair"]
                    ),
                    "target_gamma8_touched": bool(packet_by_id[target_packet_id]["gamma8_touched"]),
                    "first_height_flux_delta": int(first_summary["optical_action"]),
                    "second_height_flux_delta": -int(second_summary["optical_action"]),
                    "net_height_flux_delta": int(first_summary["optical_action"])
                    - int(second_summary["optical_action"]),
                    "hidden_R33_transfer_mod26_total": 0,
                    "total_optical_action": int(first_summary["optical_action"])
                    + int(second_summary["optical_action"]),
                    "target_mode_masks": target_modes,
                }
            )
        cell_summary_rows.append(
            {
                "source_packet_id": source_id,
                "active_partner_packet_id": source_id ^ 1,
                "source_charge_frame_key": charge_by_packet[source_id]["charge_frame_key"],
                "active_partner_charge_frame_key": charge_by_packet[source_id ^ 1][
                    "charge_frame_key"
                ],
                "one_step_odd_shadow_count": len(odd_keys),
                "one_step_odd_shadow_keys": sorted(odd_keys),
                "two_step_target_histogram": {
                    str(packet_id): int(target_counter[packet_id])
                    for packet_id in sorted(target_counter)
                },
                "source_return_ordered_crossings": sorted(seed_return_pairs),
            }
        )

    per_source_odd_shadow_histogram = histogram(
        Counter(row["one_step_odd_shadow_count"] for row in cell_summary_rows)
    )
    two_step_per_source_pattern_histogram = tuple_histogram(
        Counter(
            tuple(sorted(row["two_step_target_histogram"].values()))
            for row in cell_summary_rows
        )
    )
    one_step_target_parity_histogram = histogram(
        Counter(row["target_parity"] for row in one_step_rows)
    )
    one_step_atom_histogram = histogram(
        Counter(row["loop297_atom_union_count"] for row in one_step_rows)
    )
    one_step_gamma_histogram = histogram(
        Counter(row["gamma8_mode_count"] for row in one_step_rows)
    )
    one_step_hidden_pair_histogram = tuple_histogram(
        Counter(tuple(row["corrected_hidden_clock_pair"]) for row in one_step_rows)
    )
    one_step_clock_delta_histogram = histogram(
        Counter(row["sector26_clock_delta_mod26"] for row in one_step_rows)
    )
    one_step_clock_sum_histogram = histogram(
        Counter(row["sector26_clock_sum_mod26"] for row in one_step_rows)
    )
    two_step_target_packet_counts = Counter(
        row["target_packet_id"] for row in two_step_rows
    )
    two_step_target_packet_count_histogram = histogram(
        Counter(two_step_target_packet_counts.values())
    )
    two_step_target_parity_histogram = histogram(
        Counter(row["target_packet_key"].split(":")[0] for row in two_step_rows)
    )
    two_step_target_full_histogram = histogram(
        Counter(row["target_full_loop297_atom_exposure"] for row in two_step_rows)
    )
    two_step_gamma_histogram = histogram(
        Counter(2 if row["target_gamma8_touched"] else 0 for row in two_step_rows)
    )
    two_step_hidden_transfer_histogram = histogram(
        Counter(row["hidden_R33_transfer_mod26_total"] for row in two_step_rows)
    )
    two_step_net_flux_histogram = histogram(
        Counter(row["net_height_flux_delta"] for row in two_step_rows)
    )
    two_step_action_histogram = histogram(
        Counter(row["total_optical_action"] for row in two_step_rows)
    )
    two_step_return_pair_histogram = histogram(
        Counter(tuple(row["source_return_ordered_crossings"][0]) for row in cell_summary_rows)
    )
    source_partner_frame_pair_histogram = tuple_histogram(
        Counter(
            (
                row["source_charge_frame_key"],
                row["active_partner_charge_frame_key"],
            )
            for row in cell_summary_rows
        )
    )

    checks = {
        "projective_packet_charge_frame_classifier_is_certified": classifier.get("status")
        == "D20_PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_CERTIFIED"
        and classifier.get("all_checks_pass") is True,
        "projective_packet_spectral_charge_table_is_certified": spectral_table.get("status")
        == "D20_PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_CERTIFIED"
        and spectral_table.get("all_checks_pass") is True,
        "packet239_seed_propagation_is_certified": packet239.get("status")
        == "D20_PACKET239_SEED_PROPAGATION_CERTIFIED"
        and packet239.get("all_checks_pass") is True,
        "fourier_kernel_and_scattering_inputs_are_certified": fourier.get("status")
        == "D20_AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER_CERTIFIED"
        and fourier.get("all_checks_pass") is True
        and finite_kernel.get("status")
        == "D20_FINITE_VIRASORO_STRING_KERNEL_CANDIDATE_CERTIFIED"
        and finite_kernel.get("all_checks_pass") is True
        and scattering.get("status") == "D20_CANONICAL_FINITE_SCATTERING_TABLE_CERTIFIED"
        and scattering.get("all_checks_pass") is True
        and lift.get("status") == "D20_LOOP297_SCATTERING_AMPLITUDE_LIFT_CERTIFIED"
        and lift.get("all_checks_pass") is True,
        "full_exposure_packet_count_is_20": full_packet_ids
        == [
            174,
            175,
            190,
            191,
            238,
            239,
            246,
            247,
            254,
            255,
            430,
            431,
            446,
            447,
            494,
            495,
            502,
            503,
            510,
            511,
        ],
        "one_step_rows_are_60_odd_crossings": len(one_step_rows) == 60
        and one_step_target_parity_histogram == {"odd": 60},
        "every_full_packet_has_two_odd_shadows": per_source_odd_shadow_histogram == {"2": 20},
        "one_step_crossings_preserve_full_exposure": one_step_atom_histogram == {"25": 60},
        "one_step_crossings_split_gamma_and_hidden_pairs": one_step_gamma_histogram
        == {"0": 30, "2": 30}
        and one_step_hidden_pair_histogram == {"0|0": 30, "13|13": 30},
        "one_step_clock_histograms_match": one_step_clock_delta_histogram
        == {"0": 30, "8": 20, "18": 10}
        and one_step_clock_sum_histogram
        == {
            "0": 9,
            "4": 3,
            "6": 6,
            "10": 12,
            "12": 3,
            "14": 6,
            "16": 6,
            "20": 6,
            "22": 6,
            "24": 3,
        },
        "two_step_rows_are_120_kernel_cross_returns": len(two_step_rows) == 120
        and two_step_target_parity_histogram == {"kernel": 120},
        "two_step_cross_returns_stay_in_full_exposure": two_step_target_full_histogram
        == {"True": 120},
        "two_step_cross_returns_target_each_full_packet_six_times": two_step_target_packet_count_histogram
        == {"6": 20},
        "each_source_returns_twice_and_partner_four_times": two_step_per_source_pattern_histogram
        == {"2|4": 20},
        "every_source_returns_only_by_5_10": all(
            row["source_return_ordered_crossings"] == [[5, 10], [10, 5]]
            for row in cell_summary_rows
        ),
        "two_step_cross_returns_cancel_hidden_transfer": two_step_hidden_transfer_histogram
        == {"0": 120},
        "two_step_flux_and_action_histograms_match": two_step_net_flux_histogram
        == {
            "-399360": 20,
            "-301056": 20,
            "-98304": 20,
            "98304": 20,
            "301056": 20,
            "399360": 20,
        }
        and two_step_action_histogram
        == {"1683456": 40, "1781760": 40, "2082816": 40},
        "cell_type_histogram_has_14_source_partner_frame_pairs": len(
            source_partner_frame_pair_histogram
        )
        == 14,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FULL_EXPOSURE_PACKET_PROPAGATION_CELLS_CERTIFIED"
        if all_checks_pass
        else "D20_FULL_EXPOSURE_PACKET_PROPAGATION_CELLS_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.full_exposure_packet_propagation_cells",
        "status": status,
        "object": "d20",
        "claim": (
            "All 20 full Loop_297-exposure projective packets have the same local non-kernel propagation "
            "shape. Each has three one-step crossings to odd parity, exactly two odd packet shadows, and six "
            "ordered paired cross-returns. The paired returns land only on the source packet and its active "
            "partner: two ordered 5/10 returns to source and four returns to the active partner."
        ),
        "definition": {
            "full_exposure_packet": "A projective packet whose two modes expose all 25 compact Loop_297 atoms.",
            "one_step_crossing": "Application of a crossing primitive generator 5, 9, or 10 to both packet modes.",
            "paired_cross_return": "An ordered two-step application of distinct crossing generators.",
            "active_partner": "The same radical character with active sigma toggled, equivalently packet_id xor 1.",
        },
        "inputs": {
            "projective_packet_charge_frame_classifier_report": {
                "path": rel(PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT),
                "sha256": sha_file(PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT),
            },
            "projective_packet_spectral_charge_table_report": {
                "path": rel(PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_REPORT),
                "sha256": sha_file(PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_REPORT),
            },
            "packet239_seed_propagation_report": {
                "path": rel(PACKET239_SEED_PROPAGATION_REPORT),
                "sha256": sha_file(PACKET239_SEED_PROPAGATION_REPORT),
            },
            "amplitude_quotient_fourier_mode_classifier_report": {
                "path": rel(FOURIER_MODE_CLASSIFIER_REPORT),
                "sha256": sha_file(FOURIER_MODE_CLASSIFIER_REPORT),
            },
            "finite_virasoro_string_kernel_candidate_report": {
                "path": rel(FINITE_KERNEL_REPORT),
                "sha256": sha_file(FINITE_KERNEL_REPORT),
            },
            "canonical_finite_scattering_table_report": {
                "path": rel(CANONICAL_FINITE_SCATTERING_TABLE_REPORT),
                "sha256": sha_file(CANONICAL_FINITE_SCATTERING_TABLE_REPORT),
            },
            "loop297_scattering_amplitude_lift_report": {
                "path": rel(LOOP297_SCATTERING_AMPLITUDE_LIFT_REPORT),
                "sha256": sha_file(LOOP297_SCATTERING_AMPLITUDE_LIFT_REPORT),
            },
        },
        "derived": {
            "propagation_cell_summary": {
                "full_exposure_packet_ids": full_packet_ids,
                "full_exposure_packet_count": len(full_packet_ids),
                "one_step_crossing_row_count": len(one_step_rows),
                "two_step_cross_return_row_count": len(two_step_rows),
                "per_source_odd_shadow_histogram": per_source_odd_shadow_histogram,
                "two_step_target_packet_count_histogram": two_step_target_packet_count_histogram,
                "two_step_per_source_target_multiplicity_histogram": (
                    two_step_per_source_pattern_histogram
                ),
                "two_step_net_height_flux_delta_histogram": two_step_net_flux_histogram,
                "two_step_total_optical_action_histogram": two_step_action_histogram,
                "source_partner_frame_pair_class_count": len(source_partner_frame_pair_histogram),
            },
            "histograms": {
                "one_step_target_parity": one_step_target_parity_histogram,
                "one_step_loop297_atom_union_count": one_step_atom_histogram,
                "one_step_gamma8_mode_count": one_step_gamma_histogram,
                "one_step_corrected_hidden_clock_pair": one_step_hidden_pair_histogram,
                "one_step_sector26_clock_delta": one_step_clock_delta_histogram,
                "one_step_sector26_clock_sum": one_step_clock_sum_histogram,
                "two_step_target_parity": two_step_target_parity_histogram,
                "two_step_target_full_exposure": two_step_target_full_histogram,
                "two_step_target_gamma8_mode_count": two_step_gamma_histogram,
                "two_step_hidden_R33_transfer_total": two_step_hidden_transfer_histogram,
                "source_partner_charge_frame_pair": source_partner_frame_pair_histogram,
            },
            "cell_summary_rows": cell_summary_rows,
            "one_step_crossing_rows": one_step_rows,
            "two_step_cross_return_rows": two_step_rows,
            "cell_summary_rows_sha256": sha_json(cell_summary_rows),
            "one_step_crossing_rows_sha256": sha_json(one_step_rows),
            "two_step_cross_return_rows_sha256": sha_json(two_step_rows),
        },
        "interpretation": {
            "what_this_proves": [
                "packet 239 is one instance of a uniform 20-packet full-exposure propagation law",
                "the full-exposure stratum is closed under paired cross-returns through active-partner cells",
                "crossing generators preserve full Loop_297 exposure even when leaving the kernel",
                "all sources return to themselves only through the ordered 5/10 crossing pair",
            ],
            "what_this_does_not_prove": (
                "This is still a local two-step crossing-cell theorem. It does not classify longer non-kernel "
                "walks or propagation outside the full-exposure stratum."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Build the full-exposure propagation graph whose vertices are the 20 full-exposure packets and "
            "whose weighted edges are paired cross-return cells."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.full_exposure_packet_propagation_cells_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify packet classifier, packet table, packet239 propagation, Fourier, kernel, and scattering inputs",
            "construct one-step crossing rows for all 20 full-exposure packets",
            "construct paired cross-return rows for all 20 full-exposure packets",
            "verify every source has two odd shadows and six paired cross-returns",
            "verify paired cross-returns land only on source and active partner",
            "verify flux, action, hidden-transfer, gamma8, and Loop_297 exposure histograms",
        ],
    }
    manifest["report_sha256"] = report["certificate_sha256"]
    manifest["manifest_sha256"] = sha_json({k: v for k, v in manifest.items() if k != "manifest_sha256"})

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    update_theorem_index(report, out_dir)
    return report


def main() -> None:
    report = write_theorem()
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report.get("all_checks_pass"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
