from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "sector26_anomaly_cancellation"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FINITE_ANOMALY_COUNTER_REPORT = (
    D20_INVARIANTS / "theorems" / "finite_anomaly_counter" / "report.json"
)
SECTOR26_INVARIANT_SUITE_REPORT = (
    D20_INVARIANTS / "theorems" / "sector26_invariant_suite" / "report.json"
)

RESIDUE_RANK = 11
HALF_MODULUS = 13
CLOCK_MODULUS = 26
FIRST_OBSTRUCTION_MASK = 256


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


def clock_value(mask: int, weights_mod26: list[int]) -> int:
    return sum(weights_mod26[idx] for idx in bit_indices(mask)) % CLOCK_MODULUS


def greedy_basis(packet: tuple[int, ...]) -> list[int]:
    basis: list[int] = []
    span = {0}
    for mask in sorted(packet):
        if mask == 0 or mask in span:
            continue
        basis.append(mask)
        span |= {item ^ mask for item in list(span)}
    return basis


def is_xor_closed(packet: tuple[int, ...]) -> bool:
    packet_set = set(packet)
    return all((left ^ right) in packet_set for left in packet_set for right in packet_set)


def is_cancelled_packet(packet: tuple[int, ...], weights_mod13: list[int]) -> bool:
    return is_xor_closed(packet) and all(
        half_anomaly(left, right, weights_mod13) == 0
        for left in packet
        for right in packet
    )


def generate_cancelled_subspaces(weights_mod13: list[int]) -> dict[int, set[tuple[int, ...]]]:
    masks = list(range(1 << RESIDUE_RANK))
    self_zero = [
        mask for mask in masks if half_anomaly(mask, mask, weights_mod13) == 0
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
                if is_cancelled_packet(extended, weights_mod13):
                    next_subspaces.add(extended)
        if not next_subspaces:
            break
        subspaces[dimension + 1] = next_subspaces

    return subspaces


def packet_record(packet: tuple[int, ...], weights_mod13: list[int], weights_mod26: list[int]) -> dict[str, Any]:
    basis = greedy_basis(packet)
    clock_image = sorted({clock_value(mask, weights_mod26) for mask in packet})
    half_anomaly_matrix = [
        [half_anomaly(left, right, weights_mod13) for right in basis]
        for left in basis
    ]
    return {
        "dimension": len(basis),
        "size": len(packet),
        "basis_masks": basis,
        "basis_cycle_indices": [bit_indices(mask) for mask in basis],
        "masks": list(packet),
        "clock_image_mod26": clock_image,
        "half_anomaly_matrix_mod13_on_basis": half_anomaly_matrix,
        "sha256": sha_json(list(packet)),
    }


def build_theorem() -> dict[str, Any]:
    anomaly_counter = load_json(FINITE_ANOMALY_COUNTER_REPORT)
    sector26_suite = load_json(SECTOR26_INVARIANT_SUITE_REPORT)

    normalization = anomaly_counter["derived"]["normalization"]
    weights_mod13 = [int(value) for value in normalization["basis_cycle_normalized_mod13"]]
    weights_mod26 = [int(value) for value in normalization["basis_cycle_normalized_mod26"]]

    subspaces = generate_cancelled_subspaces(weights_mod13)
    max_dimension = max(subspaces)
    dim_counts = {str(dimension): len(items) for dimension, items in sorted(subspaces.items())}

    maximal_packets: list[tuple[int, ...]] = []
    for dimension, packets in sorted(subspaces.items()):
        if dimension == 0:
            continue
        for packet in packets:
            packet_set = set(packet)
            extendable = False
            for candidate in subspaces.get(dimension + 1, set()):
                if packet_set <= set(candidate):
                    extendable = True
                    break
            if not extendable:
                maximal_packets.append(packet)

    maximal_packets = sorted(maximal_packets, key=lambda item: (-len(item), item))
    maximal_records = [
        packet_record(packet, weights_mod13, weights_mod26) for packet in maximal_packets
    ]
    maximal_count_by_dimension = Counter(record["dimension"] for record in maximal_records)
    clock_image_count = Counter(tuple(record["clock_image_mod26"]) for record in maximal_records)

    self_zero_masks = sorted([
        mask for mask in range(1 << RESIDUE_RANK)
        if half_anomaly(mask, mask, weights_mod13) == 0
    ])
    covered_by_maximal = sorted({mask for packet in maximal_packets for mask in packet})
    uncovered_self_zero = sorted(set(self_zero_masks) - set(covered_by_maximal))
    gamma8_self_half = half_anomaly(FIRST_OBSTRUCTION_MASK, FIRST_OBSTRUCTION_MASK, weights_mod13)
    gamma8_in_any_packet = any(FIRST_OBSTRUCTION_MASK in packet for packet in maximal_packets)

    strongest_packets = [
        record for record in maximal_records if record["dimension"] == max_dimension
    ]
    terminal_pair_packets = [
        record for record in maximal_records if record["dimension"] == 2
    ]

    checks = {
        "finite_anomaly_counter_is_certified": anomaly_counter.get("status")
        == "D20_FINITE_ANOMALY_COUNTER_CERTIFIED"
        and anomaly_counter.get("all_checks_pass") is True,
        "sector26_invariant_suite_is_certified": sector26_suite.get("status")
        == "D20_SECTOR26_INVARIANT_SUITE_CERTIFIED"
        and sector26_suite.get("all_checks_pass") is True,
        "basis_weight_count_is_11": len(weights_mod13) == RESIDUE_RANK
        and len(weights_mod26) == RESIDUE_RANK,
        "all_basis_weights_are_nonzero_mod13": all(value % HALF_MODULUS != 0 for value in weights_mod13),
        "self_cancelled_mask_count_is_158": len(self_zero_masks) == 158,
        "subspace_dimension_counts_match_search": dim_counts == {
            "0": 1,
            "1": 157,
            "2": 480,
            "3": 88,
        },
        "maximal_cancelled_packet_dimension_is_3": max_dimension == 3,
        "no_dimension_4_cancelled_packet_exists": 4 not in subspaces,
        "maximal_packet_count_is_178": len(maximal_records) == 178,
        "maximal_packet_counts_by_dimension_are_90_and_88": dict(maximal_count_by_dimension)
        == {3: 88, 2: 90},
        "all_maximal_packets_are_xor_closed_and_pairwise_cancelled": all(
            is_cancelled_packet(tuple(record["masks"]), weights_mod13)
            for record in maximal_records
        ),
        "all_self_cancelled_masks_are_covered_by_maximal_packets": uncovered_self_zero == [],
        "gamma8_is_not_self_cancelled": gamma8_self_half == 5,
        "gamma8_is_excluded_from_all_cancelled_packets": not gamma8_in_any_packet,
        "restricted_clock_images_are_0_or_13_only": all(
            set(record["clock_image_mod26"]) <= {0, 13} for record in maximal_records
        ),
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_SECTOR26_ANOMALY_CANCELLATION_CERTIFIED"
        if all_checks_pass
        else "D20_SECTOR26_ANOMALY_CANCELLATION_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.sector26_anomaly_cancellation",
        "status": status,
        "object": "d20",
        "claim": (
            "Sector-26 anomaly cancellation is possible only on proper closed-return packets. The maximal "
            "xor-closed pairwise half-anomaly-zero packets have dimension 3, with 88 strongest size-8 packets "
            "and 90 terminal size-4 packets. The first obstruction gamma_8 is excluded because its self "
            "half-anomaly is nonzero."
        ),
        "definition": {
            "half_anomaly": (
                "h_13(a,b)=sum_i basis_mod13[i] a_i b_i mod 13, the half of the certified Anom_26 defect."
            ),
            "cancelled_packet": (
                "An xor-closed packet P in (F2)^11 such that h_13(a,b)=0 for every a,b in P."
            ),
            "maximal_cancelled_packet": (
                "A cancelled packet that is not properly contained in any larger cancelled xor-closed packet."
            ),
        },
        "inputs": {
            "finite_anomaly_counter_report": {
                "path": rel(FINITE_ANOMALY_COUNTER_REPORT),
                "sha256": sha_file(FINITE_ANOMALY_COUNTER_REPORT),
            },
            "sector26_invariant_suite_report": {
                "path": rel(SECTOR26_INVARIANT_SUITE_REPORT),
                "sha256": sha_file(SECTOR26_INVARIANT_SUITE_REPORT),
            },
        },
        "derived": {
            "basis_weights_mod13": weights_mod13,
            "basis_weights_mod26": weights_mod26,
            "subspace_dimension_counts": dim_counts,
            "maximal_cancelled_packet_dimension": max_dimension,
            "maximal_cancelled_packet_count": len(maximal_records),
            "maximal_cancelled_packet_count_by_dimension": {
                str(key): int(maximal_count_by_dimension[key])
                for key in sorted(maximal_count_by_dimension)
            },
            "maximal_packet_clock_image_count": {
                ",".join(str(value) for value in key): int(clock_image_count[key])
                for key in sorted(clock_image_count)
            },
            "self_cancelled_masks": {
                "count": len(self_zero_masks),
                "support_size_histogram": {
                    str(key): int(value)
                    for key, value in sorted(
                        Counter(len(bit_indices(mask)) for mask in self_zero_masks).items()
                    )
                },
                "sample_masks": self_zero_masks[:20],
            },
            "gamma8": {
                "mask": FIRST_OBSTRUCTION_MASK,
                "basis_cycle_indices": bit_indices(FIRST_OBSTRUCTION_MASK),
                "self_half_anomaly_mod13": gamma8_self_half,
                "contained_in_any_maximal_cancelled_packet": gamma8_in_any_packet,
            },
            "strongest_dimension3_packets": {
                "count": len(strongest_packets),
                "sample": strongest_packets[:12],
            },
            "terminal_dimension2_packets": {
                "count": len(terminal_pair_packets),
                "sample": terminal_pair_packets[:12],
            },
            "all_maximal_cancelled_packets_sha256": sha_json(maximal_records),
            "all_maximal_cancelled_packets": maximal_records,
        },
        "interpretation": {
            "what_this_proves": [
                "full closed-return anomaly cancellation cannot contain gamma_8",
                "the largest anomaly-cancelled closed-return sectors have eight masks",
                "all admissible cancelled packets restrict the mod-26 clock to the additive image {0,13} or {0}",
                "the half-anomaly has zero global radical, but it has proper maximal cancelled packets",
            ],
            "what_this_does_not_prove": (
                "This does not yet construct a physical flux-balance law; it identifies the finite packets on "
                "which such a law can be anomaly-cancelled."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Build the anomaly-cancelled finite flux-balance recovery theorem by restricting the typed "
            "non-exact flux ledger to the certified maximal cancelled packets."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.sector26_anomaly_cancellation_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify the finite anomaly counter is certified",
            "enumerate all xor-closed pairwise half-anomaly-zero closed-return subspaces",
            "verify maximal dimension is 3 and no dimension-4 packet exists",
            "verify there are 88 maximal dimension-3 packets and 90 terminal dimension-2 packets",
            "verify every maximal packet is xor-closed and pairwise cancelled",
            "verify gamma_8 is excluded by nonzero self half-anomaly",
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
