from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "finite_anomaly_counter"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

SECTOR26_INVARIANT_SUITE_REPORT = (
    D20_INVARIANTS / "theorems" / "sector26_invariant_suite" / "report.json"
)
ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT = (
    D20_INVARIANTS / "theorems" / "sector33_all_residue_height_transport" / "report.json"
)
TYPED_NONEXACT_OPTICAL_FLUX_REPORT = (
    D20_INVARIANTS / "theorems" / "typed_nonexact_optical_flux_update" / "report.json"
)

MODULUS = 26
HALF_MODULUS = 13
RESIDUE_RANK = 11
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


def anomaly_defect(mask_a: int, mask_b: int, basis_mod26: list[int]) -> int:
    overlap = mask_a & mask_b
    return int((2 * sum(basis_mod26[idx] for idx in bit_indices(overlap))) % MODULUS)


def local_cocycle_identity_holds(weight: int) -> bool:
    def local_defect(x: int, y: int) -> int:
        return (2 * weight * x * y) % MODULUS

    for x in (0, 1):
        for y in (0, 1):
            for z in (0, 1):
                left = (local_defect(x, y) + local_defect(x ^ y, z)) % MODULUS
                right = (local_defect(y, z) + local_defect(x, y ^ z)) % MODULUS
                if left != right:
                    return False
    return True


def build_theorem() -> dict[str, Any]:
    sector26_suite = load_json(SECTOR26_INVARIANT_SUITE_REPORT)
    all_residue = load_json(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT)
    typed_flux = load_json(TYPED_NONEXACT_OPTICAL_FLUX_REPORT)

    rows = sorted(all_residue["derived"]["transport_rows"], key=lambda row: int(row["mask"]))
    masks = [int(row["mask"]) for row in rows]
    height_actions = [int(row["height_action"]) for row in rows if int(row["height_action"]) != 0]
    action_gcd = 0
    for action in height_actions:
        action_gcd = math.gcd(action_gcd, abs(action))

    basis_normalized = [
        int(value) // action_gcd for value in all_residue["derived"]["basis_cycle_height_vector"]
    ]
    basis_mod26 = [value % MODULUS for value in basis_normalized]
    basis_mod13 = [value % HALF_MODULUS for value in basis_normalized]
    basis_twice_mod26 = [(2 * value) % MODULUS for value in basis_mod26]

    clock = {int(row["mask"]): (int(row["height_action"]) // action_gcd) % MODULUS for row in rows}
    clock_mod13 = {mask: value % HALF_MODULUS for mask, value in clock.items()}
    clock_mod2 = {mask: value % 2 for mask, value in clock.items()}

    defect_histogram: Counter[int] = Counter()
    half_defect_histogram: Counter[int] = Counter()
    first_character_failure = None
    first_mod13_failure = None
    pair_formula_matches = True
    parity_is_linear = True

    for mask_a in masks:
        value_a = clock[mask_a]
        for mask_b in masks:
            xor_mask = mask_a ^ mask_b
            defect = (value_a + clock[mask_b] - clock[xor_mask]) % MODULUS
            formula_defect = anomaly_defect(mask_a, mask_b, basis_mod26)
            defect_histogram[defect] += 1
            half_defect_histogram[(defect // 2) % HALF_MODULUS] += 1
            if defect != formula_defect:
                pair_formula_matches = False
            if first_character_failure is None and defect != 0:
                first_character_failure = {
                    "mask_a": mask_a,
                    "mask_b": mask_b,
                    "clock_a": value_a,
                    "clock_b": clock[mask_b],
                    "clock_xor": clock[xor_mask],
                    "anomaly_defect_mod26": defect,
                }
            if (
                first_mod13_failure is None
                and (clock_mod13[mask_a] + clock_mod13[mask_b] - clock_mod13[xor_mask])
                % HALF_MODULUS
                != 0
            ):
                first_mod13_failure = {
                    "mask_a": mask_a,
                    "mask_b": mask_b,
                    "clock13_a": clock_mod13[mask_a],
                    "clock13_b": clock_mod13[mask_b],
                    "clock13_xor": clock_mod13[xor_mask],
                }
            if clock_mod2[xor_mask] != (clock_mod2[mask_a] + clock_mod2[mask_b]) % 2:
                parity_is_linear = False

    radical_masks = [
        mask_a
        for mask_a in masks
        if all((anomaly_defect(mask_a, mask_b, basis_mod26) // 2) % HALF_MODULUS == 0 for mask_b in masks)
    ]
    parity_kernel_masks = [mask for mask in masks if clock_mod2[mask] == 0]
    self_anomaly_histogram = Counter(anomaly_defect(mask, mask, basis_mod26) for mask in masks)
    self_zero_masks = [
        mask for mask in masks if (anomaly_defect(mask, mask, basis_mod26) // 2) % HALF_MODULUS == 0
    ]
    gamma8_self = anomaly_defect(FIRST_OBSTRUCTION_MASK, FIRST_OBSTRUCTION_MASK, basis_mod26)

    local_cocycle_checks = [local_cocycle_identity_holds(weight) for weight in basis_mod26]
    hidden_transport_form = sector26_suite["derived"]["hidden_transport_form"]
    composite_block = hidden_transport_form["composite_block"]["matrix"]
    optical_normalization = sector26_suite["derived"]["optical_action_normalization"]

    finite_anomaly_counter = {
        "domain": "H_return = (F2)^11 closed-return residue masks under xor",
        "clock": "f_26(mask) = normalized_height_action(mask) mod 26",
        "counter": "Anom_26(a,b) = f_26(a) + f_26(b) - f_26(a xor b) mod 26",
        "closed_form": "Anom_26(a,b) = 2 * sum_i basis_mod26[i] * a_i * b_i mod 26",
        "target_channel": "sector-26 seam K_mixed_S <-> K_pure_Sminus",
        "scope_note": (
            "This certifies a finite additivity-defect counter. It is not a continuum Virasoro or central-charge "
            "theorem."
        ),
    }
    derived = {
        "normalization": {
            "height_action_gcd": action_gcd,
            "basis_cycle_normalized_actions": basis_normalized,
            "basis_cycle_normalized_mod26": basis_mod26,
            "basis_cycle_twice_mod26": basis_twice_mod26,
            "basis_cycle_normalized_mod13": basis_mod13,
        },
        "clock_character_test": {
            "z26_clock_is_linear_character": first_character_failure is None,
            "first_z26_character_failure": first_character_failure,
            "z13_clock_is_linear_character": first_mod13_failure is None,
            "first_z13_character_failure": first_mod13_failure,
            "z2_parity_shadow_is_linear_character": parity_is_linear,
            "z2_parity_basis_vector": [value % 2 for value in basis_normalized],
            "z2_parity_kernel_size": len(parity_kernel_masks),
            "z2_parity_kernel_dimension": 10 if len(parity_kernel_masks) == 1024 else None,
            "z2_parity_kernel_sample_masks": parity_kernel_masks[:12],
        },
        "anomaly_defect": {
            "pair_count": len(masks) * len(masks),
            "defect_histogram_mod26": {
                str(key): int(defect_histogram[key]) for key in sorted(defect_histogram)
            },
            "half_defect_histogram_mod13": {
                str(key): int(half_defect_histogram[key]) for key in sorted(half_defect_histogram)
            },
            "defect_classes_mod26": sorted(int(key) for key in defect_histogram),
            "half_defect_classes_mod13": sorted(int(key) for key in half_defect_histogram),
            "formula_matches_all_pairs": pair_formula_matches,
            "basis_local_cocycle_identity": local_cocycle_checks,
            "radical_masks": radical_masks,
            "self_anomaly_histogram_mod26": {
                str(key): int(self_anomaly_histogram[key]) for key in sorted(self_anomaly_histogram)
            },
            "self_half_anomaly_zero_count": len(self_zero_masks),
            "self_half_anomaly_zero_sample_masks": self_zero_masks[:12],
            "gamma8_self_anomaly_mod26": gamma8_self,
            "gamma8_self_half_anomaly_mod13": (gamma8_self // 2) % HALF_MODULUS,
        },
        "sector26_coupling": {
            "sector26_suite_status": sector26_suite.get("status"),
            "critical_26_marker": sector26_suite["derived"]["critical_26_marker"],
            "hidden_transport_form": hidden_transport_form,
            "composite_seam_block": composite_block,
            "cross_transport_rank_through_sector26": composite_block[0][1],
            "mod26_clock_residue_classes": optical_normalization["residue_classes_hit_mod26"],
        },
    }

    checks = {
        "sector26_invariant_suite_is_certified": sector26_suite.get("status")
        == "D20_SECTOR26_INVARIANT_SUITE_CERTIFIED"
        and sector26_suite.get("all_checks_pass") is True,
        "typed_nonexact_optical_flux_update_is_certified": typed_flux.get("status")
        == "D20_TYPED_NONEXACT_OPTICAL_FLUX_UPDATE_CERTIFIED"
        and typed_flux.get("all_checks_pass") is True,
        "all_residue_height_transport_is_certified": all_residue.get("status")
        == "D20_ALL_RESIDUE_HEIGHT_COHERENT_TRANSPORT_CERTIFIED"
        and all_residue.get("all_checks_pass") is True,
        "residue_masks_are_complete": masks == list(range(2**RESIDUE_RANK)),
        "height_action_gcd_is_3072": action_gcd == 3072,
        "normalized_clock_hits_all_26_residues": sorted(set(clock.values())) == list(range(MODULUS)),
        "z26_clock_is_not_linear_character": first_character_failure is not None,
        "z13_clock_is_not_linear_character": first_mod13_failure is not None,
        "z2_parity_shadow_is_linear_character": parity_is_linear,
        "z2_parity_kernel_has_dimension_10": len(parity_kernel_masks) == 1024,
        "anomaly_defect_formula_matches_all_pairs": pair_formula_matches,
        "anomaly_defect_is_even_valued": all(key % 2 == 0 for key in defect_histogram),
        "anomaly_defect_hits_all_even_mod26_classes": sorted(defect_histogram)
        == list(range(0, MODULUS, 2)),
        "half_anomaly_hits_all_mod13_classes": sorted(half_defect_histogram)
        == list(range(HALF_MODULUS)),
        "basis_local_cocycle_identity_holds": all(local_cocycle_checks),
        "half_anomaly_radical_is_zero": radical_masks == [0],
        "gamma8_self_anomaly_is_10_mod26": gamma8_self == 10,
        "sector26_cross_transport_rank_is_one": composite_block == [[5, 1], [1, 2]],
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FINITE_ANOMALY_COUNTER_CERTIFIED"
        if all_checks_pass
        else "D20_FINITE_ANOMALY_COUNTER_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.finite_anomaly_counter",
        "status": status,
        "object": "d20",
        "claim": (
            "The normalized mod-26 optical clock is not a linear character on the closed-return xor residue "
            "group. Its failure is exactly the finite anomaly counter Anom_26(a,b), an even-valued normalized "
            "2-cocycle/coboundary defect that halves to a complete mod-13 overlap counter and is typed into "
            "the certified sector-26 seam."
        ),
        "definition": finite_anomaly_counter,
        "inputs": {
            "sector26_invariant_suite_report": {
                "path": rel(SECTOR26_INVARIANT_SUITE_REPORT),
                "sha256": sha_file(SECTOR26_INVARIANT_SUITE_REPORT),
            },
            "sector33_all_residue_height_transport_report": {
                "path": rel(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT),
                "sha256": sha_file(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT),
            },
            "typed_nonexact_optical_flux_update_report": {
                "path": rel(TYPED_NONEXACT_OPTICAL_FLUX_REPORT),
                "sha256": sha_file(TYPED_NONEXACT_OPTICAL_FLUX_REPORT),
            },
        },
        "derived": derived,
        "interpretation": {
            "what_this_proves": [
                "the mod-26 optical clock is complete but not additive under closed-return xor",
                "the additivity failure is controlled by an explicit overlap formula",
                "the defect lands in 2*Z/26 and therefore halves to all of Z/13",
                "the mod-2 parity shadow is the only additive character certified at this stage",
                "the half-anomaly has zero radical, so every nonzero residue mask is detected by some partner",
            ],
            "what_this_does_not_prove": (
                "This does not yet identify a continuum central charge, Virasoro representation, or string "
                "worldsheet. It certifies the finite counter that such a recovery would have to factor through."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Classify anomaly-cancelled closed-return sectors: compute maximal subspaces or admissible "
            "cycle packets where the sector-26 half-anomaly vanishes under the required pairings."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.finite_anomaly_counter_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify all 2048 closed-return residue masks are present",
            "verify the normalized mod-26 clock is complete but not a linear xor character",
            "verify the mod-2 parity shadow is a linear character",
            "verify the anomaly defect formula on all 2048^2 pairs",
            "verify the anomaly defect hits exactly the even mod-26 classes",
            "verify the half-anomaly hits all mod-13 classes and has zero radical",
            "verify the sector-26 seam is the certified rank-one cross-transport channel",
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
