from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "canonical_all_mask_ward_identity"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FINITE_FLUX_BALANCE_REPORT = (
    D20_INVARIANTS / "theorems" / "finite_flux_balance" / "report.json"
)
BOUNDARY_ANNIHILATION_REPORT = (
    D20_INVARIANTS / "theorems" / "sector33_boundary_annihilation" / "report.json"
)
ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT = (
    D20_INVARIANTS / "theorems" / "sector33_all_residue_height_transport" / "report.json"
)
GLOBAL_COUNTERTERM_LATTICE_REPORT = (
    D20_INVARIANTS / "theorems" / "global_counterterm_lattice" / "report.json"
)
CANONICAL_FINITE_WARD_IDENTITY_REPORT = (
    D20_INVARIANTS / "theorems" / "canonical_finite_ward_identity" / "report.json"
)

RESIDUE_RANK = 11
MASK_COUNT = 1 << RESIDUE_RANK
CLOCK_MODULUS = 26
ORDER_TWO_VALUE = 13
GAMMA8_MASK = 1 << 8


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


def clock(mask: int, basis_clock_mod26: list[int]) -> int:
    return sum(basis_clock_mod26[idx] for idx in bit_indices(mask)) % CLOCK_MODULUS


def corrected_r33(mask: int, basis_clock_mod26: list[int]) -> int:
    return (-clock(mask, basis_clock_mod26)) % CLOCK_MODULUS


def build_ward_rows(
    transport_rows: list[dict[str, Any]],
    basis_clock_mod26: list[int],
) -> list[dict[str, Any]]:
    ward_rows = []
    for row in transport_rows:
        mask = int(row["mask"])
        height_action = int(row["height_action"])
        height_corrected_r33 = int(row["residual_integral"])
        ward_scalar_sum = 0 + 0 + height_corrected_r33 + height_action
        r33_mod26 = corrected_r33(mask, basis_clock_mod26)
        ward_rows.append(
            {
                "mask": mask,
                "basis_cycle_indices": bit_indices(mask),
                "public_exact_gauge_scalar": 0,
                "bare_pi33": 0,
                "height_corrected_R33": height_corrected_r33,
                "height_action": height_action,
                "ward_scalar_sum": ward_scalar_sum,
                "corrected_clock_mod26": clock(mask, basis_clock_mod26),
                "global_corrected_R33_mod26": r33_mod26,
                "in_global_corrected_kernel": r33_mod26 == 0,
            }
        )
    return ward_rows


def first_additive_failure(basis_clock_mod26: list[int]) -> dict[str, int] | None:
    if all(value in {0, ORDER_TWO_VALUE} for value in basis_clock_mod26):
        return None
    for left in range(MASK_COUNT):
        left_value = corrected_r33(left, basis_clock_mod26)
        for right in range(MASK_COUNT):
            xor_mask = left ^ right
            expected = (left_value + corrected_r33(right, basis_clock_mod26)) % CLOCK_MODULUS
            if corrected_r33(xor_mask, basis_clock_mod26) != expected:
                return {"left": left, "right": right, "xor": xor_mask}
    return None


def build_theorem() -> dict[str, Any]:
    finite_flux = load_json(FINITE_FLUX_BALANCE_REPORT)
    annihilation = load_json(BOUNDARY_ANNIHILATION_REPORT)
    all_residue = load_json(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT)
    global_lattice = load_json(GLOBAL_COUNTERTERM_LATTICE_REPORT)
    canonical_finite_ward = load_json(CANONICAL_FINITE_WARD_IDENTITY_REPORT)

    transport_rows = sorted(
        all_residue["derived"]["transport_rows"],
        key=lambda row: int(row["mask"]),
    )
    basis_clock_mod26 = [
        int(value) for value in global_lattice["derived"]["corrected_basis_clock_mod26"]
    ]
    ward_rows = build_ward_rows(transport_rows, basis_clock_mod26)
    histogram = Counter(row["global_corrected_R33_mod26"] for row in ward_rows)
    kernel_masks = [row["mask"] for row in ward_rows if row["in_global_corrected_kernel"]]
    image13_masks = [
        row["mask"] for row in ward_rows if row["global_corrected_R33_mod26"] == ORDER_TWO_VALUE
    ]
    gamma8_row = ward_rows[GAMMA8_MASK]
    gamma8_previous_terms = canonical_finite_ward["derived"]["ward_identity"]["terms"]
    gamma8_previous_total = int(
        canonical_finite_ward["derived"]["ward_identity"]["total_scalar_balance"]
    )
    additive_failure = first_additive_failure(basis_clock_mod26)

    checks = {
        "finite_exact_flux_balance_is_certified": finite_flux.get("status")
        == "D20_FINITE_EXACT_FLUX_BALANCE_CERTIFIED"
        and finite_flux.get("all_checks_pass") is True,
        "sector33_boundary_annihilation_is_certified": annihilation.get("status")
        == "D20_SECTOR33_BOUNDARY_TO_LOOP_ANNIHILATION_CERTIFIED"
        and annihilation.get("all_checks_pass") is True,
        "all_residue_height_transport_is_certified": all_residue.get("status")
        == "D20_ALL_RESIDUE_HEIGHT_COHERENT_TRANSPORT_CERTIFIED"
        and all_residue.get("all_checks_pass") is True,
        "global_counterterm_lattice_is_certified": global_lattice.get("status")
        == "D20_GLOBAL_COUNTERTERM_LATTICE_CERTIFIED"
        and global_lattice.get("all_checks_pass") is True,
        "canonical_finite_ward_identity_is_certified": canonical_finite_ward.get("status")
        == "D20_CANONICAL_FINITE_WARD_IDENTITY_CERTIFIED"
        and canonical_finite_ward.get("all_checks_pass") is True,
        "residue_masks_are_complete": len(transport_rows) == MASK_COUNT
        and [int(row["mask"]) for row in transport_rows] == list(range(MASK_COUNT)),
        "all_public_exact_flux_terms_are_zero": finite_flux["checks"][
            "all_residue_vectors_are_cycles"
        ]
        is True
        and finite_flux["derived"]["cycle_space"]["mod2_residue_vectors_checked"] == MASK_COUNT,
        "all_bare_pi33_terms_are_zero": annihilation["checks"][
            "pi33_annihilates_all_directed_pair_lifts_left_and_right"
        ]
        is True,
        "all_height_corrected_terms_are_negative_height_action": all(
            int(row["residual_integral"]) == -int(row["height_action"])
            for row in transport_rows
        ),
        "all_height_corrected_terms_have_zero_public_shadow": all_residue["checks"][
            "all_scalar_e33_transports_have_zero_public_shadow"
        ]
        is True,
        "all_ward_scalar_sums_are_zero": all(row["ward_scalar_sum"] == 0 for row in ward_rows),
        "global_corrected_character_is_additive": additive_failure is None
        and global_lattice["checks"]["corrected_clock_is_additive_on_all_2048_masks"] is True,
        "global_corrected_character_has_order_two_image": {
            str(key): int(histogram[key]) for key in sorted(histogram)
        }
        == global_lattice["derived"]["corrected_r33_histogram"],
        "global_corrected_kernel_has_dimension_10": len(kernel_masks) == 1024
        and len(image13_masks) == 1024
        and global_lattice["derived"]["kernel"]["dimension"] == 10,
        "gamma8_row_extends_canonical_finite_ward_identity": gamma8_row[
            "basis_cycle_indices"
        ]
        == [8]
        and gamma8_row["public_exact_gauge_scalar"]
        == int(gamma8_previous_terms["public_exact_gauge_scalar"])
        and gamma8_row["bare_pi33"] == int(gamma8_previous_terms["bare_pi33"])
        and gamma8_row["height_corrected_R33"]
        == int(gamma8_previous_terms["height_corrected_R33"])
        and gamma8_row["height_action"] == int(gamma8_previous_terms["height_action"])
        and gamma8_row["ward_scalar_sum"] == gamma8_previous_total,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_CANONICAL_ALL_MASK_WARD_IDENTITY_CERTIFIED"
        if all_checks_pass
        else "D20_CANONICAL_ALL_MASK_WARD_IDENTITY_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.canonical_all_mask_ward_identity",
        "status": status,
        "object": "d20",
        "claim": (
            "The canonical finite Ward identity extends from gamma_8 to the full 2048-element closed-return "
            "residue group. For every mask, exact public flux contributes zero, the bare tube-visible Pi_33 "
            "boundary term contributes zero, and the height-corrected R33 term is exactly the negative of "
            "the certified finite height action."
        ),
        "definition": {
            "all_mask_finite_ward_identity": (
                "|Delta Q_public^exact-Flux_D20|_1 + chi_33(lambda_boundary) + "
                "chi_33(Lambda_hc) + A_h(mask) = 0 for every closed-return residue mask."
            ),
            "public_exact_term": (
                "Zero on every mask because finite_flux_balance certifies exact boundary flux as a "
                "coboundary on all 2048 residue cycles."
            ),
            "bare_pi33_term": (
                "Zero on every mask by linearity from the sector-33 boundary-annihilation test on all "
                "30 directed pair lifts."
            ),
            "height_corrected_r33_term": (
                "The all-residue sector-33 transport residual residual_integral(mask), certified as "
                "-A_h(mask)."
            ),
            "global_corrected_character": (
                "R33_global(mask)=13*<[1,1,1,0,1,1,1,1,1,1,1],mask> mod 26, with a 1024-mask kernel."
            ),
        },
        "inputs": {
            "finite_flux_balance_report": {
                "path": rel(FINITE_FLUX_BALANCE_REPORT),
                "sha256": sha_file(FINITE_FLUX_BALANCE_REPORT),
            },
            "sector33_boundary_annihilation_report": {
                "path": rel(BOUNDARY_ANNIHILATION_REPORT),
                "sha256": sha_file(BOUNDARY_ANNIHILATION_REPORT),
            },
            "all_residue_height_transport_report": {
                "path": rel(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT),
                "sha256": sha_file(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT),
            },
            "global_counterterm_lattice_report": {
                "path": rel(GLOBAL_COUNTERTERM_LATTICE_REPORT),
                "sha256": sha_file(GLOBAL_COUNTERTERM_LATTICE_REPORT),
            },
            "canonical_finite_ward_identity_report": {
                "path": rel(CANONICAL_FINITE_WARD_IDENTITY_REPORT),
                "sha256": sha_file(CANONICAL_FINITE_WARD_IDENTITY_REPORT),
            },
        },
        "derived": {
            "residue_rank": RESIDUE_RANK,
            "mask_count": MASK_COUNT,
            "term_contract": {
                "public_exact_gauge_scalar": 0,
                "bare_pi33": 0,
                "height_corrected_R33": "-height_action",
                "ward_scalar_sum": 0,
            },
            "global_corrected_character": {
                "basis_clock_mod26": basis_clock_mod26,
                "basis_z2_vector": [
                    1 if value == ORDER_TWO_VALUE else 0 for value in basis_clock_mod26
                ],
                "histogram": {str(key): int(histogram[key]) for key in sorted(histogram)},
                "kernel": {
                    "size": len(kernel_masks),
                    "dimension": 10,
                    "sample_masks": kernel_masks[:24],
                },
                "image_13": {
                    "size": len(image13_masks),
                    "sample_masks": image13_masks[:24],
                },
            },
            "gamma8_row": gamma8_row,
            "ward_rows": ward_rows,
            "ward_rows_sha256": sha_json(ward_rows),
        },
        "interpretation": {
            "what_this_proves": [
                "the finite Ward cancellation is no longer just a gamma_8 witness",
                "every closed-return residue has an explicit four-term scalar balance",
                "the only non-public finite residue is the height-corrected sector-33/R33 action term",
                "the global sector-26 corrected R33 character remains the order-two split of the residue group",
            ],
            "what_this_does_not_prove": (
                "This is a finite all-mask Ward identity on the certified D20 residue group. It still needs "
                "a separate recovery theorem to identify a continuum BMS/Carrollian flux-balance limit."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Project the all-mask Ward ledger into a finite BMS/Carrollian flux-balance theorem by naming "
            "the public charge update, finite flux term, and R33 residual for every closed return."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.canonical_all_mask_ward_identity_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify finite exact flux balance, boundary annihilation, all-residue height transport, and global counterterm inputs",
            "verify all 2048 residue masks are present",
            "verify every public exact flux term is zero",
            "verify every bare Pi_33 term is zero",
            "verify every height-corrected R33 term is the negative height action",
            "verify every all-mask Ward scalar sum is zero",
            "verify gamma_8 matches the prior canonical finite Ward identity",
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
