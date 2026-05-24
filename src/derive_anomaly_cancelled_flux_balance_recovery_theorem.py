from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "anomaly_cancelled_flux_balance_recovery"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FINITE_FLUX_BALANCE_REPORT = (
    D20_INVARIANTS / "theorems" / "finite_flux_balance" / "report.json"
)
TYPED_NONEXACT_OPTICAL_FLUX_REPORT = (
    D20_INVARIANTS / "theorems" / "typed_nonexact_optical_flux_update" / "report.json"
)
FINITE_ANOMALY_COUNTER_REPORT = (
    D20_INVARIANTS / "theorems" / "finite_anomaly_counter" / "report.json"
)
SECTOR26_ANOMALY_CANCELLATION_REPORT = (
    D20_INVARIANTS / "theorems" / "sector26_anomaly_cancellation" / "report.json"
)
ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT = (
    D20_INVARIANTS / "theorems" / "sector33_all_residue_height_transport" / "report.json"
)

NORMALIZED_MODULUS = 26
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


def bit_indices(mask: int, width: int = 11) -> list[int]:
    return [idx for idx in range(width) if (mask >> idx) & 1]


def packet_clock_is_additive(masks: list[int], clock: dict[int, int]) -> bool:
    mask_set = set(masks)
    for left in masks:
        for right in masks:
            xor_mask = left ^ right
            if xor_mask not in mask_set:
                return False
            if clock[xor_mask] != (clock[left] + clock[right]) % NORMALIZED_MODULUS:
                return False
    return True


def packet_record(packet: dict[str, Any], clock: dict[int, int], height_action: dict[int, int]) -> dict[str, Any]:
    masks = [int(mask) for mask in packet["masks"]]
    clock_values = {mask: clock[mask] for mask in masks}
    r33_values = {mask: (-clock[mask]) % NORMALIZED_MODULUS for mask in masks}
    image = sorted(set(clock_values.values()))
    r33_image = sorted(set(r33_values.values()))
    max_integral_height = max(abs(height_action[mask]) for mask in masks)
    nonzero_masks = [mask for mask in masks if mask != 0]
    return {
        "dimension": int(packet["dimension"]),
        "size": int(packet["size"]),
        "basis_masks": packet["basis_masks"],
        "basis_cycle_indices": packet["basis_cycle_indices"],
        "masks": masks,
        "clock_image_mod26": image,
        "r33_normalized_image_mod26": r33_image,
        "clock_is_additive_on_packet": packet_clock_is_additive(masks, clock),
        "nonzero_mask_count": len(nonzero_masks),
        "max_integral_height_action_abs": max_integral_height,
        "balance_statement": (
            "On this packet, exact public flux closes and normalized hidden R33 update is additive modulo 26."
        ),
        "sha256": sha_json(
            {
                "masks": masks,
                "clock_values": clock_values,
                "r33_values": r33_values,
            }
        ),
    }


def build_theorem() -> dict[str, Any]:
    finite_flux = load_json(FINITE_FLUX_BALANCE_REPORT)
    typed_flux = load_json(TYPED_NONEXACT_OPTICAL_FLUX_REPORT)
    anomaly_counter = load_json(FINITE_ANOMALY_COUNTER_REPORT)
    cancellation = load_json(SECTOR26_ANOMALY_CANCELLATION_REPORT)
    all_residue = load_json(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT)

    transport_rows = sorted(all_residue["derived"]["transport_rows"], key=lambda row: int(row["mask"]))
    height_actions = [int(row["height_action"]) for row in transport_rows if int(row["height_action"]) != 0]
    action_gcd = 0
    for action in height_actions:
        action_gcd = math.gcd(action_gcd, abs(action))
    height_by_mask = {int(row["mask"]): int(row["height_action"]) for row in transport_rows}
    clock = {
        int(row["mask"]): (int(row["height_action"]) // action_gcd) % NORMALIZED_MODULUS
        for row in transport_rows
    }

    maximal_packets = cancellation["derived"]["all_maximal_cancelled_packets"]
    packet_records = [packet_record(packet, clock, height_by_mask) for packet in maximal_packets]
    dimension_histogram = Counter(record["dimension"] for record in packet_records)
    clock_image_histogram = Counter(tuple(record["clock_image_mod26"]) for record in packet_records)
    strongest_packets = [record for record in packet_records if record["dimension"] == 3]
    terminal_packets = [record for record in packet_records if record["dimension"] == 2]
    additive_packets = [record for record in packet_records if record["clock_is_additive_on_packet"]]
    all_recovered_masks = sorted({mask for record in packet_records for mask in record["masks"]})
    gamma8_recovered = FIRST_OBSTRUCTION_MASK in all_recovered_masks

    zero_image_packets = [
        record for record in packet_records if record["clock_image_mod26"] == [0]
    ]
    z2_image_packets = [
        record for record in packet_records if record["clock_image_mod26"] == [0, 13]
    ]

    exact_public_balance = finite_flux["checks"]["primitive_flux_residuals_zero"] and finite_flux["checks"][
        "all_residue_vectors_are_cycles"
    ]
    typed_hidden_ok = typed_flux["checks"]["all_nonzero_updates_go_to_R33"] and typed_flux["checks"][
        "composite_superselection_labels_are_reserved_not_optically_excited"
    ]
    gamma8_cancellation = cancellation["derived"]["gamma8"]

    checks = {
        "finite_exact_flux_balance_is_certified": finite_flux.get("status")
        == "D20_FINITE_EXACT_FLUX_BALANCE_CERTIFIED"
        and finite_flux.get("all_checks_pass") is True,
        "typed_nonexact_optical_flux_update_is_certified": typed_flux.get("status")
        == "D20_TYPED_NONEXACT_OPTICAL_FLUX_UPDATE_CERTIFIED"
        and typed_flux.get("all_checks_pass") is True,
        "finite_anomaly_counter_is_certified": anomaly_counter.get("status")
        == "D20_FINITE_ANOMALY_COUNTER_CERTIFIED"
        and anomaly_counter.get("all_checks_pass") is True,
        "sector26_anomaly_cancellation_is_certified": cancellation.get("status")
        == "D20_SECTOR26_ANOMALY_CANCELLATION_CERTIFIED"
        and cancellation.get("all_checks_pass") is True,
        "all_residue_height_transport_is_certified": all_residue.get("status")
        == "D20_ALL_RESIDUE_HEIGHT_COHERENT_TRANSPORT_CERTIFIED"
        and all_residue.get("all_checks_pass") is True,
        "normalization_gcd_is_3072": action_gcd == 3072,
        "maximal_cancelled_packet_count_is_178": len(packet_records) == 178,
        "strongest_dimension3_packet_count_is_88": len(strongest_packets) == 88,
        "terminal_dimension2_packet_count_is_90": len(terminal_packets) == 90,
        "all_packet_clocks_are_additive_mod26": len(additive_packets) == len(packet_records),
        "all_packet_clock_images_are_0_or_13": all(
            set(record["clock_image_mod26"]) <= {0, 13} for record in packet_records
        ),
        "exact_public_flux_closes_on_certified_cycle_space": exact_public_balance,
        "typed_hidden_flux_is_R33_only_on_recovery_packets": typed_hidden_ok,
        "gamma8_is_not_recovered": not gamma8_recovered
        and gamma8_cancellation["self_half_anomaly_mod13"] == 5,
        "recovery_covers_all_self_cancelled_masks": len(all_recovered_masks) == 158,
        "zero_and_z2_packet_types_are_both_present": len(zero_image_packets) == 37
        and len(z2_image_packets) == 141,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_ANOMALY_CANCELLED_FLUX_BALANCE_RECOVERY_CERTIFIED"
        if all_checks_pass
        else "D20_ANOMALY_CANCELLED_FLUX_BALANCE_RECOVERY_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.anomaly_cancelled_flux_balance_recovery",
        "status": status,
        "object": "d20",
        "claim": (
            "On each certified sector-26 anomaly-cancelled closed-return packet, exact public D20 flux closes "
            "and the normalized non-exact R33 update becomes additive modulo 26. The recovered finite "
            "flux-balance sector is therefore the union of the 178 maximal cancelled packets; gamma_8 is not "
            "part of that recovered sector."
        ),
        "definition": {
            "recovered_packet_balance": (
                "For a maximal cancelled packet P, Delta Q_public^exact=0 on closed returns and "
                "Delta R33_norm(a xor b)=Delta R33_norm(a)+Delta R33_norm(b) mod 26 for all a,b in P."
            ),
            "normalization": "R33_norm(mask)=(-height_action(mask)/3072) mod 26.",
            "scope": (
                "This is a finite modular flux-balance recovery on anomaly-cancelled packets, not a claim of "
                "unrestricted continuum BMS/Carrollian flux balance."
            ),
        },
        "inputs": {
            "finite_flux_balance_report": {
                "path": rel(FINITE_FLUX_BALANCE_REPORT),
                "sha256": sha_file(FINITE_FLUX_BALANCE_REPORT),
            },
            "typed_nonexact_optical_flux_update_report": {
                "path": rel(TYPED_NONEXACT_OPTICAL_FLUX_REPORT),
                "sha256": sha_file(TYPED_NONEXACT_OPTICAL_FLUX_REPORT),
            },
            "finite_anomaly_counter_report": {
                "path": rel(FINITE_ANOMALY_COUNTER_REPORT),
                "sha256": sha_file(FINITE_ANOMALY_COUNTER_REPORT),
            },
            "sector26_anomaly_cancellation_report": {
                "path": rel(SECTOR26_ANOMALY_CANCELLATION_REPORT),
                "sha256": sha_file(SECTOR26_ANOMALY_CANCELLATION_REPORT),
            },
            "all_residue_height_transport_report": {
                "path": rel(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT),
                "sha256": sha_file(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT),
            },
        },
        "derived": {
            "normalization_gcd": action_gcd,
            "recovered_packet_count": len(packet_records),
            "recovered_mask_count": len(all_recovered_masks),
            "recovered_mask_sample": all_recovered_masks[:24],
            "packet_dimension_histogram": {
                str(key): int(dimension_histogram[key]) for key in sorted(dimension_histogram)
            },
            "packet_clock_image_histogram": {
                ",".join(str(value) for value in key): int(clock_image_histogram[key])
                for key in sorted(clock_image_histogram)
            },
            "zero_image_packet_count": len(zero_image_packets),
            "z2_image_packet_count": len(z2_image_packets),
            "gamma8": {
                "mask": FIRST_OBSTRUCTION_MASK,
                "recovered": gamma8_recovered,
                "self_half_anomaly_mod13": gamma8_cancellation["self_half_anomaly_mod13"],
                "reason_excluded": "gamma_8 has nonzero sector-26 self half-anomaly.",
            },
            "packet_samples": {
                "dimension3": strongest_packets[:8],
                "dimension2": terminal_packets[:8],
            },
            "all_packet_balance_records_sha256": sha_json(packet_records),
            "all_packet_balance_records": packet_records,
        },
        "interpretation": {
            "what_this_proves": [
                "the exact public D20 flux sector remains closed on all recovered packets",
                "the normalized hidden R33 update is additive mod 26 on every recovered packet",
                "the only recovered hidden images are trivial {0} and order-two {0,13}",
                "gamma_8 remains a genuine anomaly-obstructed first non-exact event",
            ],
            "what_this_does_not_prove": (
                "It does not remove the non-exact optical residual on all 2048 masks. It identifies the finite "
                "subsector where the residual composes without the sector-26 anomaly."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Classify the anomaly-obstructed complement: determine the minimal correction or extension needed "
            "to include gamma_8 in a flux-balance law."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.anomaly_cancelled_flux_balance_recovery_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify exact finite flux balance is certified",
            "verify typed non-exact optical updates are R33-only",
            "verify sector-26 anomaly cancellation is certified",
            "verify normalized R33 update is additive mod 26 on every maximal cancelled packet",
            "verify gamma_8 is excluded from the recovered packets",
            "verify recovered packet image types are {0} and {0,13}",
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
