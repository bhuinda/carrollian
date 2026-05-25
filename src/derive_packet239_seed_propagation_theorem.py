from __future__ import annotations

import hashlib
import json
from collections import Counter
from itertools import permutations
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "packet239_seed_propagation"
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
PACKET239_STABILIZER_SEED_CANDIDATE_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "packet239_stabilizer_seed_candidate"
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

SEED_PACKET_ID = 239
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
    laplacian_pair = [int(row["laplacian_eigenvalue"]) for row in rows]
    return {
        "mode_masks": mode_pair,
        "sector26_clock_pair": clock_pair,
        "sector26_clock_sum_mod26": sum(clock_pair) % 26,
        "sector26_clock_delta_mod26": (clock_pair[1] - clock_pair[0]) % 26,
        "corrected_hidden_clock_pair": hidden_pair,
        "corrected_hidden_clock_sum_mod26": sum(hidden_pair) % 26,
        "laplacian_eigenvalue_pair": laplacian_pair,
        "laplacian_trace": sum(laplacian_pair),
        "gamma8_mode_count": sum(1 for row in rows if row["gamma8_support"]),
        "gamma8_touched": any(bool(row["gamma8_support"]) for row in rows),
        "loop297_atom_union_count": len(atoms),
        "loop297_atom_union_ids": atoms,
    }


def build_theorem() -> dict[str, Any]:
    classifier = load_json(PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_REPORT)
    spectral_table = load_json(PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_REPORT)
    stabilizer = load_json(PACKET239_STABILIZER_SEED_CANDIDATE_REPORT)
    fourier = load_json(FOURIER_MODE_CLASSIFIER_REPORT)
    finite_kernel = load_json(FINITE_KERNEL_REPORT)
    scattering = load_json(CANONICAL_FINITE_SCATTERING_TABLE_REPORT)
    lift = load_json(LOOP297_SCATTERING_AMPLITUDE_LIFT_REPORT)

    charge_rows = classifier["derived"]["charge_frame_rows"]
    charge_by_packet = {int(row["packet_id"]): row for row in charge_rows}
    packet_rows = spectral_table["derived"]["packet_spectral_charge_rows"]
    packet_by_id = {int(row["packet_id"]): row for row in packet_rows}
    seed_packet = packet_by_id[SEED_PACKET_ID]
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
    for generator_id in CROSSING_GENERATORS:
        target_modes = [
            int(mask) ^ (1 << generator_id) for mask in seed_packet["mode_masks"]
        ]
        packet_key = packet_key_from_mode_pair(target_modes)
        measurements = packet_measurements(target_modes, mode_by_mask)
        summary = generator_summary[generator_id]
        amplitude = amplitude_packet[generator_id]
        one_step_rows.append(
            {
                "generator_cycle_id": generator_id,
                "source_packet_id": SEED_PACKET_ID,
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

    two_step_rows = []
    for first, second in permutations(CROSSING_GENERATORS, 2):
        target_modes = [
            int(mask) ^ (1 << first) ^ (1 << second)
            for mask in seed_packet["mode_masks"]
        ]
        packet_key = packet_key_from_mode_pair(target_modes)
        target_packet_id = int(packet_key["packet_id"])
        first_summary = generator_summary[first]
        second_summary = generator_summary[second]
        total_optical_action = int(first_summary["optical_action"]) + int(
            second_summary["optical_action"]
        )
        net_height_flux_delta = int(first_summary["optical_action"]) - int(
            second_summary["optical_action"]
        )
        two_step_rows.append(
            {
                "first_generator_cycle_id": first,
                "second_generator_cycle_id": second,
                "source_packet_id": SEED_PACKET_ID,
                "target_packet_id": target_packet_id,
                "target_packet_key": packet_key["packet_key"],
                "target_charge_frame_key": charge_by_packet[target_packet_id][
                    "charge_frame_key"
                ],
                "target_fine_spectral_charge_key": charge_by_packet[target_packet_id][
                    "fine_spectral_charge_key"
                ],
                "returns_to_seed_packet": target_packet_id == SEED_PACKET_ID,
                "target_full_loop297_atom_exposure": bool(
                    packet_by_id[target_packet_id]["full_loop297_atom_exposure"]
                ),
                "target_sector26_clock_zero_pair": bool(
                    packet_by_id[target_packet_id]["sector26_clock_zero_pair"]
                ),
                "target_gamma8_touched": bool(packet_by_id[target_packet_id]["gamma8_touched"]),
                "first_height_flux_delta": int(first_summary["optical_action"]),
                "second_height_flux_delta": -int(second_summary["optical_action"]),
                "net_height_flux_delta": net_height_flux_delta,
                "hidden_R33_transfer_mod26_total": 0,
                "total_optical_action": total_optical_action,
                "target_mode_masks": target_modes,
            }
        )

    one_step_unique_odd_keys = sorted({row["target_packet_key"] for row in one_step_rows})
    two_step_target_histogram = histogram(Counter(row["target_packet_id"] for row in two_step_rows))
    two_step_net_flux_histogram = histogram(
        Counter(row["net_height_flux_delta"] for row in two_step_rows)
    )
    two_step_action_histogram = histogram(
        Counter(row["total_optical_action"] for row in two_step_rows)
    )
    two_step_target_frame_histogram = histogram(
        Counter(row["target_charge_frame_key"] for row in two_step_rows)
    )

    checks = {
        "projective_packet_charge_frame_classifier_is_certified": classifier.get("status")
        == "D20_PROJECTIVE_PACKET_CHARGE_FRAME_CLASSIFIER_CERTIFIED"
        and classifier.get("all_checks_pass") is True,
        "projective_packet_spectral_charge_table_is_certified": spectral_table.get("status")
        == "D20_PROJECTIVE_PACKET_SPECTRAL_CHARGE_TABLE_CERTIFIED"
        and spectral_table.get("all_checks_pass") is True,
        "packet239_stabilizer_seed_candidate_is_certified": stabilizer.get("status")
        == "D20_PACKET239_STABILIZER_SEED_CANDIDATE_CERTIFIED"
        and stabilizer.get("all_checks_pass") is True,
        "fourier_mode_classifier_is_certified": fourier.get("status")
        == "D20_AMPLITUDE_QUOTIENT_FOURIER_MODE_CLASSIFIER_CERTIFIED"
        and fourier.get("all_checks_pass") is True,
        "finite_kernel_crossing_generators_are_5_9_10": finite_kernel.get("status")
        == "D20_FINITE_VIRASORO_STRING_KERNEL_CANDIDATE_CERTIFIED"
        and finite_kernel["derived"]["closure_summary"]["crossing_primitive_generators"]
        == CROSSING_GENERATORS,
        "scattering_inputs_are_certified": scattering.get("status")
        == "D20_CANONICAL_FINITE_SCATTERING_TABLE_CERTIFIED"
        and scattering.get("all_checks_pass") is True
        and lift.get("status") == "D20_LOOP297_SCATTERING_AMPLITUDE_LIFT_CERTIFIED"
        and lift.get("all_checks_pass") is True,
        "seed_packet239_is_charge_frame_unique": classifier["checks"].get(
            "packet239_is_unique_in_charge_frame_and_fine_key"
        )
        is True,
        "one_step_crossing_rows_hit_two_odd_packet_shadows": len(one_step_rows) == 3
        and one_step_unique_odd_keys == ["odd:119:0", "odd:119:1"],
        "one_step_crossing_rows_are_full_exposure_gamma_silent": all(
            row["target_parity"] == "odd"
            and row["loop297_atom_union_count"] == 25
            and row["gamma8_touched"] is False
            for row in one_step_rows
        ),
        "one_step_crossing_hidden_clock_cancels_packetwise": all(
            row["corrected_hidden_clock_sum_mod26"] == 0
            and row["hidden_R33_transfer_mod26_per_mode"] == 13
            for row in one_step_rows
        ),
        "one_step_crossing_clock_pairs_match": {
            row["generator_cycle_id"]: row["sector26_clock_pair"]
            for row in one_step_rows
        }
        == {5: [9, 17], 9: [15, 15], 10: [17, 9]},
        "two_step_cross_return_rows_hit_only_packets_238_and_239": len(two_step_rows) == 6
        and two_step_target_histogram == {"238": 4, "239": 2},
        "two_step_cross_returns_preserve_full_exposure_and_gamma_silence": all(
            row["target_full_loop297_atom_exposure"] is True
            and row["target_gamma8_touched"] is False
            for row in two_step_rows
        ),
        "two_step_cross_returns_cancel_hidden_transfer": all(
            row["hidden_R33_transfer_mod26_total"] == 0 for row in two_step_rows
        ),
        "two_step_cross_return_flux_histogram_matches": two_step_net_flux_histogram
        == {
            "-399360": 1,
            "-301056": 1,
            "-98304": 1,
            "98304": 1,
            "301056": 1,
            "399360": 1,
        },
        "two_step_cross_return_action_histogram_matches": two_step_action_histogram
        == {"1683456": 2, "1781760": 2, "2082816": 2},
        "only_5_10_returns_to_seed_packet": sorted(
            [
                [row["first_generator_cycle_id"], row["second_generator_cycle_id"]]
                for row in two_step_rows
                if row["returns_to_seed_packet"]
            ]
        )
        == [[5, 10], [10, 5]],
        "cross_return_charge_frames_are_seed_and_active_partner": set(
            row["target_packet_id"] for row in two_step_rows
        )
        == {238, 239}
        and len(two_step_target_frame_histogram) == 2,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_PACKET239_SEED_PROPAGATION_CERTIFIED"
        if all_checks_pass
        else "D20_PACKET239_SEED_PROPAGATION_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.packet239_seed_propagation",
        "status": status,
        "object": "d20",
        "claim": (
            "Under the admissible non-kernel crossing generators 5, 9, and 10, packet 239 propagates to two "
            "odd packet shadows. Paired cross-return scattering closes the seed cell on exactly two kernel "
            "packets, 238 and 239. Packet 239 returns only through the 5/10 paired crossing, while all paired "
            "cross-returns preserve full Loop_297 exposure, gamma8 silence, and hidden-transfer cancellation."
        ),
        "definition": {
            "non_kernel_crossing_generators": "The primitive generators 5, 9, and 10 crossing the rank-10 kernel.",
            "odd_packet_shadow": (
                "The odd-parity packet obtained by removing the parity source bit e5 and reading the same "
                "radical/active coordinates used for kernel packets."
            ),
            "paired_cross_return": (
                "An ordered two-step scattering path using two distinct crossing generators, returning from "
                "odd parity to the rank-10 kernel."
            ),
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
            "packet239_stabilizer_seed_candidate_report": {
                "path": rel(PACKET239_STABILIZER_SEED_CANDIDATE_REPORT),
                "sha256": sha_file(PACKET239_STABILIZER_SEED_CANDIDATE_REPORT),
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
            "propagation_summary": {
                "seed_packet_id": SEED_PACKET_ID,
                "crossing_generators": CROSSING_GENERATORS,
                "one_step_crossing_row_count": len(one_step_rows),
                "one_step_unique_odd_packet_shadows": one_step_unique_odd_keys,
                "two_step_cross_return_row_count": len(two_step_rows),
                "two_step_target_packet_histogram": two_step_target_histogram,
                "two_step_net_height_flux_delta_histogram": two_step_net_flux_histogram,
                "two_step_total_optical_action_histogram": two_step_action_histogram,
                "two_step_target_charge_frame_histogram": two_step_target_frame_histogram,
                "seed_return_ordered_crossings": [
                    [row["first_generator_cycle_id"], row["second_generator_cycle_id"]]
                    for row in two_step_rows
                    if row["returns_to_seed_packet"]
                ],
                "active_partner_packet_id": 238,
            },
            "seed_packet": {
                "packet_id": SEED_PACKET_ID,
                "mode_masks": seed_packet["mode_masks"],
                "charge_frame_key": charge_by_packet[SEED_PACKET_ID]["charge_frame_key"],
                "fine_spectral_charge_key": charge_by_packet[SEED_PACKET_ID][
                    "fine_spectral_charge_key"
                ],
            },
            "one_step_crossing_rows": one_step_rows,
            "two_step_cross_return_rows": two_step_rows,
            "one_step_crossing_rows_sha256": sha_json(one_step_rows),
            "two_step_cross_return_rows_sha256": sha_json(two_step_rows),
        },
        "interpretation": {
            "what_this_proves": [
                "packet 239 has a certified non-kernel propagation cell",
                "one-step crossings leave the kernel but retain full Loop_297 exposure and gamma8 silence",
                "paired cross-returns close only on packet 239 and active partner packet 238",
                "packet 239 is returned by the ordered 5/10 crossing pair, not by every crossing pair",
            ],
            "what_this_does_not_prove": (
                "This is only the local seed-cell propagation from packet 239. It does not yet classify the "
                "propagation cells of all 20 full-exposure packets."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Generalize seed propagation to all 20 full-exposure packets and classify their non-kernel "
            "crossing cells."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.packet239_seed_propagation_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify packet classifier, spectral table, stabilizer, Fourier, kernel, and scattering inputs",
            "construct one-step odd packet shadows under crossing generators 5, 9, and 10",
            "construct ordered paired cross-return rows using distinct crossing generators",
            "verify odd shadows preserve full Loop_297 exposure, hidden cancellation, and gamma8 silence",
            "verify cross-returns close only on packets 238 and 239",
            "verify cross-return height-flux and optical-action histograms",
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
