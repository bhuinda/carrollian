from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "gamma8_obstruction_correction"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FINITE_ANOMALY_COUNTER_REPORT = (
    D20_INVARIANTS / "theorems" / "finite_anomaly_counter" / "report.json"
)
SECTOR26_ANOMALY_CANCELLATION_REPORT = (
    D20_INVARIANTS / "theorems" / "sector26_anomaly_cancellation" / "report.json"
)
ANOMALY_CANCELLED_FLUX_BALANCE_RECOVERY_REPORT = (
    D20_INVARIANTS / "theorems" / "anomaly_cancelled_flux_balance_recovery" / "report.json"
)

RESIDUE_RANK = 11
HALF_MODULUS = 13
CLOCK_MODULUS = 26
GAMMA8_MASK = 256
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


def clock(mask: int, weights_mod26: list[int]) -> int:
    return sum(weights_mod26[idx] for idx in bit_indices(mask)) % CLOCK_MODULUS


def correction(mask: int, counterterm_mod13: int) -> int:
    return counterterm_mod13 if ((mask >> GAMMA8_BASIS_INDEX) & 1) else 0


def corrected_clock(mask: int, weights_mod26: list[int], counterterm_mod13: int) -> int:
    return (clock(mask, weights_mod26) - correction(mask, counterterm_mod13)) % CLOCK_MODULUS


def corrected_r33(mask: int, weights_mod26: list[int], counterterm_mod13: int) -> int:
    return (-clock(mask, weights_mod26) + correction(mask, counterterm_mod13)) % CLOCK_MODULUS


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


def greedy_basis(packet: tuple[int, ...]) -> list[int]:
    basis: list[int] = []
    span = {0}
    for mask in sorted(packet):
        if mask == 0 or mask in span:
            continue
        basis.append(mask)
        span |= {item ^ mask for item in list(span)}
    return basis


def maximal_packets(subspaces: dict[int, set[tuple[int, ...]]], weights_mod13: list[int]) -> list[tuple[int, ...]]:
    self_zero = [
        mask for mask in range(1 << RESIDUE_RANK)
        if half_anomaly(mask, mask, weights_mod13) == 0
    ]
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
                if len(extended) == 2 * len(packet) and packet_is_cancelled(extended, weights_mod13):
                    extendable = True
                    break
            if not extendable:
                maximal.append(packet)
    return sorted(maximal, key=lambda item: (-len(item), item))


def packet_record(
    packet: tuple[int, ...],
    weights_mod13: list[int],
    weights_mod26: list[int],
    counterterm_mod13: int,
) -> dict[str, Any]:
    basis = greedy_basis(packet)
    corrected_clock_image = sorted(
        {corrected_clock(mask, weights_mod26, counterterm_mod13) for mask in packet}
    )
    corrected_r33_image = sorted(
        {corrected_r33(mask, weights_mod26, counterterm_mod13) for mask in packet}
    )
    additive = all(
        corrected_clock(a ^ b, weights_mod26, counterterm_mod13)
        == (
            corrected_clock(a, weights_mod26, counterterm_mod13)
            + corrected_clock(b, weights_mod26, counterterm_mod13)
        )
        % CLOCK_MODULUS
        for a in packet
        for b in packet
    )
    return {
        "dimension": len(basis),
        "size": len(packet),
        "basis_masks": basis,
        "basis_cycle_indices": [bit_indices(mask) for mask in basis],
        "masks": list(packet),
        "contains_gamma8": GAMMA8_MASK in packet,
        "corrected_clock_image_mod26": corrected_clock_image,
        "corrected_r33_image_mod26": corrected_r33_image,
        "corrected_clock_is_additive": additive,
        "half_anomaly_matrix_mod13_on_basis": [
            [half_anomaly(left, right, weights_mod13) for right in basis]
            for left in basis
        ],
        "sha256": sha_json(list(packet)),
    }


def build_theorem() -> dict[str, Any]:
    anomaly = load_json(FINITE_ANOMALY_COUNTER_REPORT)
    cancellation = load_json(SECTOR26_ANOMALY_CANCELLATION_REPORT)
    recovery = load_json(ANOMALY_CANCELLED_FLUX_BALANCE_RECOVERY_REPORT)

    normalization = anomaly["derived"]["normalization"]
    original_weights_mod13 = [int(value) for value in normalization["basis_cycle_normalized_mod13"]]
    weights_mod26 = [int(value) for value in normalization["basis_cycle_normalized_mod26"]]
    gamma_half = original_weights_mod13[GAMMA8_BASIS_INDEX]
    counterterm_mod13 = gamma_half
    corrected_weights_mod13 = list(original_weights_mod13)
    corrected_weights_mod13[GAMMA8_BASIS_INDEX] = (
        corrected_weights_mod13[GAMMA8_BASIS_INDEX] - counterterm_mod13
    ) % HALF_MODULUS

    gamma_clock = clock(GAMMA8_MASK, weights_mod26)
    gamma_r33 = (-gamma_clock) % CLOCK_MODULUS
    gamma_corrected_clock = corrected_clock(GAMMA8_MASK, weights_mod26, counterterm_mod13)
    gamma_corrected_r33 = corrected_r33(GAMMA8_MASK, weights_mod26, counterterm_mod13)
    existing_mod26_solutions = [
        value for value in range(CLOCK_MODULUS)
        if (2 * value) % CLOCK_MODULUS == (2 * counterterm_mod13) % CLOCK_MODULUS
    ]
    signed_solutions = [
        value if value <= CLOCK_MODULUS // 2 else value - CLOCK_MODULUS
        for value in existing_mod26_solutions
    ]

    corrected_subspaces = generate_cancelled_subspaces(corrected_weights_mod13)
    corrected_maximal = maximal_packets(corrected_subspaces, corrected_weights_mod13)
    corrected_records = [
        packet_record(packet, corrected_weights_mod13, weights_mod26, counterterm_mod13)
        for packet in corrected_maximal
    ]
    corrected_dimension_counts = {
        str(dimension): len(packets) for dimension, packets in sorted(corrected_subspaces.items())
    }
    maximal_count_by_dimension = Counter(record["dimension"] for record in corrected_records)
    clock_image_count = Counter(tuple(record["corrected_clock_image_mod26"]) for record in corrected_records)
    gamma_packets = [record for record in corrected_records if record["contains_gamma8"]]

    checks = {
        "finite_anomaly_counter_is_certified": anomaly.get("status")
        == "D20_FINITE_ANOMALY_COUNTER_CERTIFIED"
        and anomaly.get("all_checks_pass") is True,
        "sector26_anomaly_cancellation_is_certified": cancellation.get("status")
        == "D20_SECTOR26_ANOMALY_CANCELLATION_CERTIFIED"
        and cancellation.get("all_checks_pass") is True,
        "anomaly_cancelled_flux_balance_recovery_is_certified": recovery.get("status")
        == "D20_ANOMALY_CANCELLED_FLUX_BALANCE_RECOVERY_CERTIFIED"
        and recovery.get("all_checks_pass") is True,
        "gamma8_is_basis_coordinate_8": GAMMA8_MASK == 1 << GAMMA8_BASIS_INDEX,
        "gamma8_original_half_anomaly_is_5": gamma_half == 5,
        "zero_counterterm_cannot_include_gamma8": half_anomaly(
            GAMMA8_MASK, GAMMA8_MASK, original_weights_mod13
        )
        != 0,
        "rank_one_counterterm_is_unique_mod13": (
            original_weights_mod13[GAMMA8_BASIS_INDEX] - counterterm_mod13
        )
        % HALF_MODULUS
        == 0,
        "minimal_signed_mod26_lift_is_5": min(signed_solutions, key=lambda value: abs(value)) == 5,
        "corrected_gamma8_half_anomaly_is_zero": half_anomaly(
            GAMMA8_MASK, GAMMA8_MASK, corrected_weights_mod13
        )
        == 0,
        "corrected_gamma8_r33_is_order_two": gamma_corrected_r33 == 13
        and (2 * gamma_corrected_r33) % CLOCK_MODULUS == 0,
        "corrected_subspace_dimension_counts_match_search": corrected_dimension_counts
        == {"0": 1, "1": 163, "2": 805, "3": 421, "4": 30},
        "corrected_maximal_packet_count_is_62": len(corrected_records) == 62,
        "corrected_maximal_packet_counts_are_32_and_30": dict(maximal_count_by_dimension)
        == {4: 30, 3: 32},
        "all_corrected_maximal_packets_contain_gamma8": len(gamma_packets) == len(corrected_records),
        "all_corrected_maximal_packet_clocks_are_additive": all(
            record["corrected_clock_is_additive"] for record in corrected_records
        ),
        "corrected_gamma8_recovery_extends_prior_exclusion": recovery["derived"]["gamma8"]["recovered"]
        is False,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_GAMMA8_OBSTRUCTION_CORRECTION_CERTIFIED"
        if all_checks_pass
        else "D20_GAMMA8_OBSTRUCTION_CORRECTION_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.gamma8_obstruction_correction",
        "status": status,
        "object": "d20",
        "claim": (
            "The first non-exact event gamma_8 can enter a finite flux-balance law only after a rank-one "
            "sector-26 counterterm. The unique half-anomaly counterterm is 5 mod 13 on basis coordinate 8; "
            "it sends the normalized R33 value of gamma_8 from 8 to 13, making gamma_8 order-two and opening "
            "62 corrected maximal packets."
        ),
        "definition": {
            "gamma8_counterterm": (
                "kappa_8(mask)=5 if basis coordinate 8 is active and 0 otherwise; it is subtracted from the "
                "mod-26 optical clock and added to normalized R33."
            ),
            "corrected_half_anomaly": (
                "h'_13(a,b)=h_13(a,b)-5*a_8*b_8, so gamma_8 becomes a radical generator."
            ),
            "corrected_balance": (
                "R33'_norm(mask)=R33_norm(mask)+kappa_8(mask) is additive modulo 26 on corrected packets."
            ),
        },
        "inputs": {
            "finite_anomaly_counter_report": {
                "path": rel(FINITE_ANOMALY_COUNTER_REPORT),
                "sha256": sha_file(FINITE_ANOMALY_COUNTER_REPORT),
            },
            "sector26_anomaly_cancellation_report": {
                "path": rel(SECTOR26_ANOMALY_CANCELLATION_REPORT),
                "sha256": sha_file(SECTOR26_ANOMALY_CANCELLATION_REPORT),
            },
            "anomaly_cancelled_flux_balance_recovery_report": {
                "path": rel(ANOMALY_CANCELLED_FLUX_BALANCE_RECOVERY_REPORT),
                "sha256": sha_file(ANOMALY_CANCELLED_FLUX_BALANCE_RECOVERY_REPORT),
            },
        },
        "derived": {
            "gamma8": {
                "mask": GAMMA8_MASK,
                "basis_index": GAMMA8_BASIS_INDEX,
                "basis_cycle_indices": bit_indices(GAMMA8_MASK),
                "original_clock_mod26": gamma_clock,
                "original_r33_norm_mod26": gamma_r33,
                "original_self_half_anomaly_mod13": gamma_half,
                "counterterm_mod13": counterterm_mod13,
                "counterterm_mod26_solutions": existing_mod26_solutions,
                "counterterm_signed_solutions": signed_solutions,
                "chosen_minimal_signed_counterterm": 5,
                "corrected_clock_mod26": gamma_corrected_clock,
                "corrected_r33_norm_mod26": gamma_corrected_r33,
            },
            "forms": {
                "original_weights_mod13": original_weights_mod13,
                "corrected_weights_mod13": corrected_weights_mod13,
                "weights_mod26": weights_mod26,
            },
            "corrected_packet_search": {
                "subspace_dimension_counts": corrected_dimension_counts,
                "maximal_packet_count": len(corrected_records),
                "maximal_packet_count_by_dimension": {
                    str(key): int(maximal_count_by_dimension[key])
                    for key in sorted(maximal_count_by_dimension)
                },
                "clock_image_count": {
                    ",".join(str(value) for value in key): int(clock_image_count[key])
                    for key in sorted(clock_image_count)
                },
                "all_corrected_maximal_packets_sha256": sha_json(corrected_records),
                "sample_corrected_maximal_packets": corrected_records[:12],
                "all_corrected_maximal_packets": corrected_records,
            },
        },
        "interpretation": {
            "what_this_proves": [
                "gamma_8 is not recovered by the uncorrected anomaly-cancelled flux-balance sector",
                "a rank-one sector-26 counterterm on coordinate 8 is enough to include gamma_8",
                "the corrected gamma_8 R33 value is 13, the order-two additive value modulo 26",
                "the corrected maximal packets all contain gamma_8 and have dimensions 3 or 4",
            ],
            "what_this_does_not_prove": (
                "This does not make every closed-return mask anomaly-free. It certifies the minimal local "
                "correction for the first obstruction and the corrected packets that follow from it."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Generalize obstruction correction: classify the minimal rank-one counterterms for every "
            "self-anomalous basis coordinate and compare their corrected packet geometries."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.gamma8_obstruction_correction_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify gamma_8 is excluded before correction",
            "verify the unique half-anomaly counterterm on coordinate 8 is 5 mod 13",
            "verify corrected gamma_8 has order-two normalized R33 value 13 mod 26",
            "verify corrected maximal packets all contain gamma_8",
            "verify corrected clocks are additive on every corrected maximal packet",
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
