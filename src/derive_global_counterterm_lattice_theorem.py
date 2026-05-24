from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "global_counterterm_lattice"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FINITE_ANOMALY_COUNTER_REPORT = (
    D20_INVARIANTS / "theorems" / "finite_anomaly_counter" / "report.json"
)
GENERAL_OBSTRUCTION_CORRECTION_SUITE_REPORT = (
    D20_INVARIANTS / "theorems" / "general_obstruction_correction_suite" / "report.json"
)
ANOMALY_CANCELLED_FLUX_BALANCE_RECOVERY_REPORT = (
    D20_INVARIANTS / "theorems" / "anomaly_cancelled_flux_balance_recovery" / "report.json"
)
ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT = (
    D20_INVARIANTS / "theorems" / "sector33_all_residue_height_transport" / "report.json"
)
FINITE_FLUX_BALANCE_REPORT = (
    D20_INVARIANTS / "theorems" / "finite_flux_balance" / "report.json"
)

RESIDUE_RANK = 11
HALF_MODULUS = 13
CLOCK_MODULUS = 26
GAMMA8_MASK = 256


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


def signed_to_mod26(value: int) -> int:
    return value % CLOCK_MODULUS


def clock(mask: int, weights_mod26: list[int]) -> int:
    return sum(weights_mod26[idx] for idx in bit_indices(mask)) % CLOCK_MODULUS


def corrected_clock(mask: int, weights_mod26: list[int], counterterms_mod26: list[int]) -> int:
    raw = clock(mask, weights_mod26)
    correction = sum(counterterms_mod26[idx] for idx in bit_indices(mask))
    return (raw - correction) % CLOCK_MODULUS


def corrected_half_anomaly(
    mask_a: int,
    mask_b: int,
    weights_mod13: list[int],
    counterterms_mod13: list[int],
) -> int:
    overlap = mask_a & mask_b
    return sum(
        (weights_mod13[idx] - counterterms_mod13[idx]) % HALF_MODULUS
        for idx in bit_indices(overlap)
    ) % HALF_MODULUS


def build_theorem() -> dict[str, Any]:
    anomaly = load_json(FINITE_ANOMALY_COUNTER_REPORT)
    general_suite = load_json(GENERAL_OBSTRUCTION_CORRECTION_SUITE_REPORT)
    recovery = load_json(ANOMALY_CANCELLED_FLUX_BALANCE_RECOVERY_REPORT)
    all_residue = load_json(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT)
    finite_flux = load_json(FINITE_FLUX_BALANCE_REPORT)

    weights_mod13 = [int(value) for value in anomaly["derived"]["normalization"]["basis_cycle_normalized_mod13"]]
    weights_mod26 = [int(value) for value in anomaly["derived"]["normalization"]["basis_cycle_normalized_mod26"]]
    signed_lifts_by_key = general_suite["derived"]["expected_minimal_signed_lifts"]
    signed_lifts = [int(signed_lifts_by_key[str(idx)]) for idx in range(RESIDUE_RANK)]
    counterterms_mod26 = [signed_to_mod26(value) for value in signed_lifts]
    counterterms_mod13 = [value % HALF_MODULUS for value in counterterms_mod26]
    corrected_basis_mod13 = [
        (weights_mod13[idx] - counterterms_mod13[idx]) % HALF_MODULUS
        for idx in range(RESIDUE_RANK)
    ]
    corrected_basis_clock = [
        (weights_mod26[idx] - counterterms_mod26[idx]) % CLOCK_MODULUS
        for idx in range(RESIDUE_RANK)
    ]

    masks = list(range(1 << RESIDUE_RANK))
    corrected_clock_by_mask = {
        mask: corrected_clock(mask, weights_mod26, counterterms_mod26) for mask in masks
    }
    corrected_r33_by_mask = {
        mask: (-value) % CLOCK_MODULUS for mask, value in corrected_clock_by_mask.items()
    }
    clock_histogram = Counter(corrected_clock_by_mask.values())
    r33_histogram = Counter(corrected_r33_by_mask.values())
    additive_failures: list[dict[str, int]] = []
    half_anomaly_failures: list[dict[str, int]] = []
    for left in masks:
        for right in masks:
            xor_mask = left ^ right
            if corrected_clock_by_mask[xor_mask] != (
                corrected_clock_by_mask[left] + corrected_clock_by_mask[right]
            ) % CLOCK_MODULUS:
                additive_failures.append(
                    {
                        "left": left,
                        "right": right,
                        "left_clock": corrected_clock_by_mask[left],
                        "right_clock": corrected_clock_by_mask[right],
                        "xor_clock": corrected_clock_by_mask[xor_mask],
                    }
                )
                break
            defect = corrected_half_anomaly(left, right, weights_mod13, counterterms_mod13)
            if defect != 0:
                half_anomaly_failures.append({"left": left, "right": right, "defect": defect})
                break
        if additive_failures or half_anomaly_failures:
            break

    kernel_masks = [mask for mask in masks if corrected_clock_by_mask[mask] == 0]
    image13_masks = [mask for mask in masks if corrected_clock_by_mask[mask] == 13]
    transport_rows = sorted(all_residue["derived"]["transport_rows"], key=lambda row: int(row["mask"]))
    height_action_by_mask = {int(row["mask"]): int(row["height_action"]) for row in transport_rows}
    gamma8_record = {
        "mask": GAMMA8_MASK,
        "basis_cycle_indices": bit_indices(GAMMA8_MASK),
        "height_action": height_action_by_mask[GAMMA8_MASK],
        "corrected_clock_mod26": corrected_clock_by_mask[GAMMA8_MASK],
        "corrected_r33_norm_mod26": corrected_r33_by_mask[GAMMA8_MASK],
        "included_in_global_corrected_group": True,
    }

    checks = {
        "finite_anomaly_counter_is_certified": anomaly.get("status")
        == "D20_FINITE_ANOMALY_COUNTER_CERTIFIED"
        and anomaly.get("all_checks_pass") is True,
        "general_obstruction_correction_suite_is_certified": general_suite.get("status")
        == "D20_GENERAL_OBSTRUCTION_CORRECTION_SUITE_CERTIFIED"
        and general_suite.get("all_checks_pass") is True,
        "anomaly_cancelled_flux_balance_recovery_is_certified": recovery.get("status")
        == "D20_ANOMALY_CANCELLED_FLUX_BALANCE_RECOVERY_CERTIFIED"
        and recovery.get("all_checks_pass") is True,
        "all_residue_height_transport_is_certified": all_residue.get("status")
        == "D20_ALL_RESIDUE_HEIGHT_COHERENT_TRANSPORT_CERTIFIED"
        and all_residue.get("all_checks_pass") is True,
        "finite_exact_flux_balance_is_certified": finite_flux.get("status")
        == "D20_FINITE_EXACT_FLUX_BALANCE_CERTIFIED"
        and finite_flux.get("all_checks_pass") is True,
        "all_11_counterterms_are_active": len(signed_lifts) == RESIDUE_RANK
        and all(value % HALF_MODULUS == weights_mod13[idx] for idx, value in enumerate(counterterms_mod26)),
        "corrected_half_anomaly_form_is_zero": corrected_basis_mod13 == [0] * RESIDUE_RANK,
        "corrected_basis_clock_is_order_two_or_zero": corrected_basis_clock
        == [13, 13, 13, 0, 13, 13, 13, 13, 13, 13, 13],
        "corrected_clock_is_additive_on_all_2048_masks": additive_failures == [],
        "corrected_half_anomaly_vanishes_on_all_pairs": half_anomaly_failures == [],
        "corrected_clock_image_is_order_two": dict(clock_histogram) == {0: 1024, 13: 1024},
        "corrected_r33_image_is_order_two": dict(r33_histogram) == {0: 1024, 13: 1024},
        "corrected_kernel_has_dimension_10": len(kernel_masks) == 1024,
        "gamma8_is_included_with_order_two_value": gamma8_record["corrected_r33_norm_mod26"] == 13,
        "exact_public_flux_closes_on_full_cycle_space": finite_flux["checks"]["all_residue_vectors_are_cycles"]
        is True,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_GLOBAL_COUNTERTERM_LATTICE_CERTIFIED"
        if all_checks_pass
        else "D20_GLOBAL_COUNTERTERM_LATTICE_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.global_counterterm_lattice",
        "status": status,
        "object": "d20",
        "claim": (
            "Activating all 11 certified rank-one sector-26 counterterms annihilates the half-anomaly form on "
            "the full closed-return residue group. The corrected normalized optical/R33 clock is an additive "
            "order-two character on all 2048 masks, so the full finite closed-return group becomes corrected "
            "flux-balanced."
        ),
        "definition": {
            "global_counterterm_lattice": (
                "The 11-coordinate counterterm vector with signed lifts "
                "[-1,1,5,-2,1,4,-5,-3,5,-2,4], activated on the corresponding basis cycle coordinates."
            ),
            "corrected_clock": (
                "f_global(mask)=f_26(mask)-sum_i k_i mask_i mod 26, where k_i are the signed-lift "
                "counterterms reduced modulo 26."
            ),
            "corrected_balance": (
                "Exact public D20 flux closes, and R33_global(mask)=-f_global(mask) is additive modulo 26 "
                "on the whole closed-return residue group."
            ),
        },
        "inputs": {
            "finite_anomaly_counter_report": {
                "path": rel(FINITE_ANOMALY_COUNTER_REPORT),
                "sha256": sha_file(FINITE_ANOMALY_COUNTER_REPORT),
            },
            "general_obstruction_correction_suite_report": {
                "path": rel(GENERAL_OBSTRUCTION_CORRECTION_SUITE_REPORT),
                "sha256": sha_file(GENERAL_OBSTRUCTION_CORRECTION_SUITE_REPORT),
            },
            "anomaly_cancelled_flux_balance_recovery_report": {
                "path": rel(ANOMALY_CANCELLED_FLUX_BALANCE_RECOVERY_REPORT),
                "sha256": sha_file(ANOMALY_CANCELLED_FLUX_BALANCE_RECOVERY_REPORT),
            },
            "all_residue_height_transport_report": {
                "path": rel(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT),
                "sha256": sha_file(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT),
            },
            "finite_flux_balance_report": {
                "path": rel(FINITE_FLUX_BALANCE_REPORT),
                "sha256": sha_file(FINITE_FLUX_BALANCE_REPORT),
            },
        },
        "derived": {
            "basis_weights_mod13": weights_mod13,
            "basis_weights_mod26": weights_mod26,
            "counterterm_signed_lifts": signed_lifts,
            "counterterm_lifts_mod26": counterterms_mod26,
            "counterterm_lifts_mod13": counterterms_mod13,
            "corrected_basis_half_anomaly_mod13": corrected_basis_mod13,
            "corrected_basis_clock_mod26": corrected_basis_clock,
            "corrected_clock_histogram": {
                str(key): int(clock_histogram[key]) for key in sorted(clock_histogram)
            },
            "corrected_r33_histogram": {
                str(key): int(r33_histogram[key]) for key in sorted(r33_histogram)
            },
            "kernel": {
                "size": len(kernel_masks),
                "dimension": 10,
                "sample_masks": kernel_masks[:24],
            },
            "image_13": {
                "size": len(image13_masks),
                "sample_masks": image13_masks[:24],
            },
            "gamma8": gamma8_record,
            "corrected_clock_rows_sha256": sha_json(corrected_clock_by_mask),
            "corrected_r33_rows_sha256": sha_json(corrected_r33_by_mask),
        },
        "interpretation": {
            "what_this_proves": [
                "the sector-26 correction suite globalizes over the entire closed-return residue group",
                "all pairwise half-anomaly defects vanish after simultaneous correction",
                "the corrected hidden R33 ledger reduces to an order-two character",
                "gamma_8 is included in the globally corrected flux-balance sector",
            ],
            "what_this_does_not_prove": (
                "This is still a finite modular correction theorem. It does not identify a continuum charge "
                "algebra or prove a continuum BMS/Carrollian theorem without an additional recovery map."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Extract the resulting global corrected charge map as an explicit homomorphism and compare it "
            "against the public D20 exact flux charge basis."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.global_counterterm_lattice_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify all 11 rank-one counterterms are active",
            "verify the corrected half-anomaly form is zero",
            "verify the corrected clock is additive on all 2048 masks",
            "verify the corrected R33 image is the order-two image {0,13}",
            "verify gamma_8 is included in the globally corrected balance sector",
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
