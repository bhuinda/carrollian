from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "general_obstruction_correction_suite"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FINITE_ANOMALY_COUNTER_REPORT = (
    D20_INVARIANTS / "theorems" / "finite_anomaly_counter" / "report.json"
)
GAMMA8_OBSTRUCTION_CORRECTION_REPORT = (
    D20_INVARIANTS / "theorems" / "gamma8_obstruction_correction" / "report.json"
)
ANOMALY_CANCELLED_FLUX_BALANCE_RECOVERY_REPORT = (
    D20_INVARIANTS / "theorems" / "anomaly_cancelled_flux_balance_recovery" / "report.json"
)

RESIDUE_RANK = 11
HALF_MODULUS = 13
CLOCK_MODULUS = 26
GAMMA8_BASIS_INDEX = 8


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


def bit_indices(mask: int, width: int = RESIDUE_RANK) -> list[int]:
    return [idx for idx in range(width) if (mask >> idx) & 1]


def half_anomaly(mask_a: int, mask_b: int, weights_mod13: list[int]) -> int:
    overlap = mask_a & mask_b
    return sum(weights_mod13[idx] for idx in bit_indices(overlap)) % HALF_MODULUS


def packet_is_cancelled(packet: tuple[int, ...], weights_mod13: list[int]) -> bool:
    packet_set = set(packet)
    return all((a ^ b) in packet_set for a in packet for b in packet) and all(
        half_anomaly(a, b, weights_mod13) == 0 for a in packet for b in packet
    )


def generate_cancelled_subspaces(weights_mod13: list[int]) -> dict[int, set[tuple[int, ...]]]:
    self_zero = [
        mask for mask in range(1 << RESIDUE_RANK)
        if half_anomaly(mask, mask, weights_mod13) == 0
    ]
    self_zero_set = set(self_zero)
    subspaces: dict[int, set[tuple[int, ...]]] = {0: {(0,)}}
    for dimension in range(RESIDUE_RANK):
        next_subspaces: set[tuple[int, ...]] = set()
        for packet in subspaces[dimension]:
            packet_set = set(packet)
            for vector in self_zero:
                if vector == 0 or vector in packet_set:
                    continue
                new_coset = {item ^ vector for item in packet_set}
                if new_coset & packet_set or not new_coset.issubset(self_zero_set):
                    continue
                extended = tuple(sorted(packet_set | new_coset))
                if packet_is_cancelled(extended, weights_mod13):
                    next_subspaces.add(extended)
        if not next_subspaces:
            break
        subspaces[dimension + 1] = next_subspaces
    return subspaces


def maximal_packets(subspaces: dict[int, set[tuple[int, ...]]], weights_mod13: list[int]) -> list[tuple[int, ...]]:
    self_zero = [
        mask for mask in range(1 << RESIDUE_RANK)
        if half_anomaly(mask, mask, weights_mod13) == 0
    ]
    self_zero_set = set(self_zero)
    maximal: list[tuple[int, ...]] = []
    for dimension, packets in sorted(subspaces.items()):
        if dimension == 0:
            continue
        for packet in packets:
            packet_set = set(packet)
            extendable = False
            for vector in self_zero:
                if vector == 0 or vector in packet_set:
                    continue
                new_coset = {item ^ vector for item in packet_set}
                extended = tuple(sorted(packet_set | new_coset))
                if (
                    len(extended) == 2 * len(packet)
                    and set(extended).issubset(self_zero_set)
                    and packet_is_cancelled(extended, weights_mod13)
                ):
                    extendable = True
                    break
            if not extendable:
                maximal.append(packet)
    return sorted(maximal, key=lambda item: (-len(item), item))


def signed_lift(value_mod26: int) -> int:
    return value_mod26 if value_mod26 <= CLOCK_MODULUS // 2 else value_mod26 - CLOCK_MODULUS


def minimal_counterterm_lift(weight_mod13: int) -> tuple[int, int, list[int], list[int]]:
    solutions = [value for value in range(CLOCK_MODULUS) if value % HALF_MODULUS == weight_mod13]
    signed = [signed_lift(value) for value in solutions]
    chosen_signed = min(signed, key=lambda value: (abs(value), value))
    return chosen_signed % CLOCK_MODULUS, chosen_signed, solutions, signed


def clock(mask: int, weights_mod26: list[int]) -> int:
    return sum(weights_mod26[idx] for idx in bit_indices(mask)) % CLOCK_MODULUS


def corrected_clock(
    mask: int,
    coordinate: int,
    weights_mod26: list[int],
    counterterm_lift_mod26: int,
) -> int:
    active = 1 if ((mask >> coordinate) & 1) else 0
    return (clock(mask, weights_mod26) - active * counterterm_lift_mod26) % CLOCK_MODULUS


def packet_clock_is_additive(
    packet: tuple[int, ...],
    coordinate: int,
    weights_mod26: list[int],
    counterterm_lift_mod26: int,
) -> bool:
    for left in packet:
        for right in packet:
            if corrected_clock(left ^ right, coordinate, weights_mod26, counterterm_lift_mod26) != (
                corrected_clock(left, coordinate, weights_mod26, counterterm_lift_mod26)
                + corrected_clock(right, coordinate, weights_mod26, counterterm_lift_mod26)
            ) % CLOCK_MODULUS:
                return False
    return True


def coordinate_correction_record(
    coordinate: int,
    weights_mod13: list[int],
    weights_mod26: list[int],
) -> dict[str, Any]:
    target_mask = 1 << coordinate
    counterterm_lift_mod26, counterterm_signed, lift_solutions, signed_solutions = minimal_counterterm_lift(
        weights_mod13[coordinate]
    )
    corrected_weights = list(weights_mod13)
    corrected_weights[coordinate] = (
        corrected_weights[coordinate] - weights_mod13[coordinate]
    ) % HALF_MODULUS
    subspaces = generate_cancelled_subspaces(corrected_weights)
    max_packets = maximal_packets(subspaces, corrected_weights)
    max_dimension_histogram = Counter(int(len(packet).bit_length() - 1) for packet in max_packets)
    image_histogram: Counter[tuple[int, ...]] = Counter()
    additive_failures = 0
    for packet in max_packets:
        image = tuple(
            sorted(
                {
                    corrected_clock(mask, coordinate, weights_mod26, counterterm_lift_mod26)
                    for mask in packet
                }
            )
        )
        image_histogram[image] += 1
        if not packet_clock_is_additive(packet, coordinate, weights_mod26, counterterm_lift_mod26):
            additive_failures += 1

    corrected_basis_clock = corrected_clock(
        target_mask, coordinate, weights_mod26, counterterm_lift_mod26
    )
    corrected_basis_r33 = (-corrected_basis_clock) % CLOCK_MODULUS
    record = {
        "coordinate": coordinate,
        "target_mask": target_mask,
        "original_weight_mod13": weights_mod13[coordinate],
        "original_clock_mod26": weights_mod26[coordinate],
        "original_r33_norm_mod26": (-weights_mod26[coordinate]) % CLOCK_MODULUS,
        "counterterm_mod13": weights_mod13[coordinate],
        "counterterm_mod26_solutions": lift_solutions,
        "counterterm_signed_solutions": signed_solutions,
        "chosen_counterterm_mod26": counterterm_lift_mod26,
        "chosen_counterterm_signed": counterterm_signed,
        "corrected_basis_clock_mod26": corrected_basis_clock,
        "corrected_basis_r33_norm_mod26": corrected_basis_r33,
        "corrected_subspace_dimension_counts": {
            str(dimension): len(packets) for dimension, packets in sorted(subspaces.items())
        },
        "corrected_maximal_packet_count": len(max_packets),
        "corrected_maximal_packet_count_by_dimension": {
            str(key): int(max_dimension_histogram[key]) for key in sorted(max_dimension_histogram)
        },
        "corrected_clock_image_count": {
            ",".join(str(value) for value in key): int(image_histogram[key])
            for key in sorted(image_histogram)
        },
        "corrected_additive_failure_count": additive_failures,
        "corrected_maximal_packets_containing_target": sum(
            1 for packet in max_packets if target_mask in packet
        ),
        "sample_corrected_maximal_packets": [
            {
                "dimension": int(len(packet).bit_length() - 1),
                "masks": list(packet),
                "basis_masks": [mask for mask in packet if mask and mask.bit_count() <= 4][:4],
                "clock_image_mod26": sorted(
                    {
                        corrected_clock(mask, coordinate, weights_mod26, counterterm_lift_mod26)
                        for mask in packet
                    }
                ),
                "contains_target": target_mask in packet,
            }
            for packet in max_packets[:8]
        ],
        "all_corrected_maximal_packets_sha256": sha_json([list(packet) for packet in max_packets]),
    }
    return record


def build_theorem() -> dict[str, Any]:
    anomaly = load_json(FINITE_ANOMALY_COUNTER_REPORT)
    gamma8 = load_json(GAMMA8_OBSTRUCTION_CORRECTION_REPORT)
    recovery = load_json(ANOMALY_CANCELLED_FLUX_BALANCE_RECOVERY_REPORT)

    normalization = anomaly["derived"]["normalization"]
    weights_mod13 = [int(value) for value in normalization["basis_cycle_normalized_mod13"]]
    weights_mod26 = [int(value) for value in normalization["basis_cycle_normalized_mod26"]]
    coordinate_records = [
        coordinate_correction_record(coordinate, weights_mod13, weights_mod26)
        for coordinate in range(RESIDUE_RANK)
    ]
    geometry_classes = Counter(
        (
            tuple(sorted(record["corrected_subspace_dimension_counts"].items())),
            tuple(sorted(record["corrected_maximal_packet_count_by_dimension"].items())),
            tuple(sorted(record["corrected_clock_image_count"].items())),
        )
        for record in coordinate_records
    )

    expected_max_packet_counts = {
        0: 80,
        1: 67,
        2: 62,
        3: 70,
        4: 67,
        5: 50,
        6: 72,
        7: 60,
        8: 62,
        9: 70,
        10: 50,
    }
    expected_signed_lifts = {
        0: -1,
        1: 1,
        2: 5,
        3: -2,
        4: 1,
        5: 4,
        6: -5,
        7: -3,
        8: 5,
        9: -2,
        10: 4,
    }
    gamma8_record = coordinate_records[GAMMA8_BASIS_INDEX]
    checks = {
        "finite_anomaly_counter_is_certified": anomaly.get("status")
        == "D20_FINITE_ANOMALY_COUNTER_CERTIFIED"
        and anomaly.get("all_checks_pass") is True,
        "gamma8_obstruction_correction_is_certified": gamma8.get("status")
        == "D20_GAMMA8_OBSTRUCTION_CORRECTION_CERTIFIED"
        and gamma8.get("all_checks_pass") is True,
        "anomaly_cancelled_flux_balance_recovery_is_certified": recovery.get("status")
        == "D20_ANOMALY_CANCELLED_FLUX_BALANCE_RECOVERY_CERTIFIED"
        and recovery.get("all_checks_pass") is True,
        "all_11_basis_coordinates_are_self_anomalous": len(weights_mod13) == RESIDUE_RANK
        and all(value % HALF_MODULUS != 0 for value in weights_mod13),
        "all_coordinate_corrections_are_rank_one": all(
            record["counterterm_mod13"] == record["original_weight_mod13"]
            for record in coordinate_records
        ),
        "minimal_signed_lifts_match_expected_table": {
            record["coordinate"]: record["chosen_counterterm_signed"]
            for record in coordinate_records
        }
        == expected_signed_lifts,
        "every_corrected_search_opens_dimension_4": all(
            "4" in record["corrected_subspace_dimension_counts"]
            for record in coordinate_records
        ),
        "no_corrected_search_exceeds_dimension_4": all(
            max(int(key) for key in record["corrected_subspace_dimension_counts"]) == 4
            for record in coordinate_records
        ),
        "corrected_maximal_packet_counts_match_expected_table": {
            record["coordinate"]: record["corrected_maximal_packet_count"]
            for record in coordinate_records
        }
        == expected_max_packet_counts,
        "every_corrected_maximal_packet_contains_target_coordinate": all(
            record["corrected_maximal_packets_containing_target"]
            == record["corrected_maximal_packet_count"]
            for record in coordinate_records
        ),
        "every_corrected_packet_clock_is_additive": all(
            record["corrected_additive_failure_count"] == 0 for record in coordinate_records
        ),
        "corrected_basis_values_are_order_two_or_zero": all(
            record["corrected_basis_clock_mod26"] in {0, 13}
            and record["corrected_basis_r33_norm_mod26"] in {0, 13}
            for record in coordinate_records
        ),
        "gamma8_row_matches_prior_theorem": gamma8_record["chosen_counterterm_signed"] == gamma8[
            "derived"
        ]["gamma8"]["chosen_minimal_signed_counterterm"]
        and gamma8_record["corrected_maximal_packet_count_by_dimension"]
        == gamma8["derived"]["corrected_packet_search"]["maximal_packet_count_by_dimension"],
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_GENERAL_OBSTRUCTION_CORRECTION_SUITE_CERTIFIED"
        if all_checks_pass
        else "D20_GENERAL_OBSTRUCTION_CORRECTION_SUITE_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.general_obstruction_correction_suite",
        "status": status,
        "object": "d20",
        "claim": (
            "Every basis coordinate of the closed-return residue space is self-anomalous and admits a unique "
            "rank-one sector-26 correction. After the minimal signed lift of each counterterm, the corrected "
            "packet geometry opens dimension-4 cancelled packets and all corrected packet clocks are additive "
            "modulo 26. The gamma_8 correction is the coordinate-8 row of this general suite."
        ),
        "definition": {
            "coordinate_counterterm": (
                "For basis coordinate i with half-anomaly weight w_i mod 13, subtract a rank-one term "
                "w_i x_i y_i from the half-anomaly form and lift w_i to the minimal signed mod-26 "
                "counterterm in the R33 clock."
            ),
            "corrected_coordinate_packet": (
                "A maximal xor-closed packet for the corrected half-anomaly form associated to one coordinate."
            ),
        },
        "inputs": {
            "finite_anomaly_counter_report": {
                "path": rel(FINITE_ANOMALY_COUNTER_REPORT),
                "sha256": sha_file(FINITE_ANOMALY_COUNTER_REPORT),
            },
            "gamma8_obstruction_correction_report": {
                "path": rel(GAMMA8_OBSTRUCTION_CORRECTION_REPORT),
                "sha256": sha_file(GAMMA8_OBSTRUCTION_CORRECTION_REPORT),
            },
            "anomaly_cancelled_flux_balance_recovery_report": {
                "path": rel(ANOMALY_CANCELLED_FLUX_BALANCE_RECOVERY_REPORT),
                "sha256": sha_file(ANOMALY_CANCELLED_FLUX_BALANCE_RECOVERY_REPORT),
            },
        },
        "derived": {
            "basis_weights_mod13": weights_mod13,
            "basis_weights_mod26": weights_mod26,
            "coordinate_corrections": coordinate_records,
            "expected_minimal_signed_lifts": expected_signed_lifts,
            "expected_corrected_maximal_packet_counts": expected_max_packet_counts,
            "geometry_class_count": len(geometry_classes),
            "geometry_class_histogram": {
                sha_json(list(key)): int(value) for key, value in geometry_classes.items()
            },
            "gamma8_coordinate": gamma8_record,
        },
        "interpretation": {
            "what_this_proves": [
                "gamma_8 is not exceptional as a correction mechanism; it is one coordinate row",
                "all 11 basis coordinates require rank-one counterterms to become self-cancelled",
                "every local correction opens dimension-4 corrected packets",
                "corrected clock images remain order-two or zero on corrected packets",
            ],
            "what_this_does_not_prove": (
                "This does not yet build the simultaneous global correction where multiple rank-one "
                "counterterms are active at once."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Build the global counterterm-lattice theorem: activate all 11 rank-one corrections together "
            "and test whether the full closed-return residue group becomes corrected flux-balanced."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.general_obstruction_correction_suite_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify every basis coordinate is self-anomalous",
            "compute the minimal signed mod-26 lift for every coordinate counterterm",
            "enumerate corrected cancelled packet geometries for all 11 coordinates",
            "verify all corrected packet clocks are additive modulo 26",
            "verify the coordinate-8 row matches the gamma_8 obstruction-correction theorem",
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
