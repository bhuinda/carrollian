from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

try:
    from src.paths import D20_INVARIANTS, ROOT
except ModuleNotFoundError:  # Supports `python src/derive_d20_matrix_lift_conjecture.py`.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "d20_matrix_lift_conjecture"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

CONSTANTS = ROOT / "data" / "raw" / "constants.json"
ZERO_AXIOM_COORIENT = D20_INVARIANTS / "zero_axiom_coorient.json"
ZERO_PAIR_CHARGE_KERNEL = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_propagator_charge_kernel"
    / "report.json"
)
ZERO_PAIR_SYMMETRY_WARD = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_propagator_symmetry_ward"
    / "report.json"
)
SECTOR26_INVARIANT_SUITE = (
    D20_INVARIANTS / "theorems" / "sector26_invariant_suite" / "report.json"
)
SECTOR33_UNIQUE_PUBLIC_ZERO_SUPPORT = (
    D20_INVARIANTS
    / "theorems"
    / "sector33_unique_public_zero_support"
    / "report.json"
)


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


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


def input_record(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": sha_file(path)}


def residue_rows_with_fractional_coefficients(rows: list[dict[str, Any]]) -> list[str]:
    residue_ids = []
    for row in rows:
        values = list(row.get("rational_coefficients", {}).values())
        if any("/" in str(value) for value in values):
            residue_ids.append(str(row.get("residue_id")))
    return residue_ids


def build_shadow_dictionary(
    constants: dict[str, Any],
    zero_axiom: dict[str, Any],
    charge_kernel: dict[str, Any],
    sector26: dict[str, Any],
    sector33: dict[str, Any],
) -> list[dict[str, Any]]:
    selector = zero_axiom["d6_selector"]["construction"]
    kernel_summary = charge_kernel["derived"]["propagator_charge_kernel_summary"]
    sector26_marker = sector26["derived"]["critical_26_marker"]
    return [
        {
            "d20_layer": "A985",
            "certified_evidence": {
                "dimension": constants["wedderburn"]["sum_squares"],
                "center_dimension": constants["wedderburn"]["center_dim"],
                "tensor_support": constants["tensor_shape"][0],
                "coefficient_total": constants["coefficient_total"],
            },
            "matrix_theoretic_reading": "finite matrix/algebraic bulk",
            "level": "certified finite algebra",
        },
        {
            "d20_layer": "D20 = Lambda^3 H6",
            "certified_evidence": {
                "face_count": selector["odd_spinor_face_basis_count"],
                "d6_projective_root_count": selector["d6_projective_root_count"],
                "face_space": selector["odd_spinor_face_space"],
            },
            "matrix_theoretic_reading": "public membrane-like boundary sector",
            "level": "certified finite public boundary",
        },
        {
            "d20_layer": "zero-pair Green residues",
            "certified_evidence": {
                "source_packet_id": kernel_summary["source_packet_id"],
                "support_packet_ids": kernel_summary["support_packet_ids"],
                "raw_half_residues_are_not_native_z26_classes": kernel_summary[
                    "raw_half_residues_are_not_native_z26_classes"
                ],
            },
            "matrix_theoretic_reading": "propagator/pole charge data",
            "level": "certified propagator charge kernel",
        },
        {
            "d20_layer": "1/2 raw residue",
            "certified_evidence": {
                "fractional_residue_ids": residue_rows_with_fractional_coefficients(
                    charge_kernel["derived"]["residue_charge_rows"]
                ),
                "native_sector26_obstruction": (
                    "Z/26 has no inverse for 2, so raw half residues are not native "
                    "ledger classes."
                ),
            },
            "matrix_theoretic_reading": "upstairs half-integral flux",
            "level": "certified denominator obstruction",
        },
        {
            "d20_layer": "Z/26 after clearing",
            "certified_evidence": {
                "plus_image": kernel_summary["plus_denominator_cleared_sector26_image"],
                "minus_image": kernel_summary["minus_denominator_cleared_sector26_image"],
                "sector26_marker": {
                    "sector": sector26_marker["sector"],
                    "d20_public_state_count_plus_h6_channel_count": sector26_marker[
                        "d20_public_state_count_plus_h6_channel_count"
                    ],
                },
            },
            "matrix_theoretic_reading": "downstairs ledger charge",
            "level": "certified denominator-cleared sector ledger",
        },
        {
            "d20_layer": "(+4,+8),(-4,-8)",
            "certified_evidence": {
                "plus_sum_delta": [
                    kernel_summary["plus_denominator_cleared_sector26_image"][
                        "sector26_clock_sum_mod26"
                    ],
                    kernel_summary["plus_denominator_cleared_sector26_image"][
                        "sector26_clock_delta_mod26"
                    ],
                ],
                "minus_sum_delta_mod26": [
                    kernel_summary["minus_denominator_cleared_sector26_image"][
                        "sector26_clock_sum_mod26"
                    ],
                    kernel_summary["minus_denominator_cleared_sector26_image"][
                        "sector26_clock_delta_mod26"
                    ],
                ],
                "minus_signed_representative": [-4, -8],
            },
            "matrix_theoretic_reading": "charge/anti-charge doublet",
            "level": "certified complementary residue pair",
        },
        {
            "d20_layer": "sector 33",
            "certified_evidence": {
                "public_zero_sectors": sector33["derived"]["public_zero_sectors"],
                "sector_count": sector33["derived"]["sector_count"],
                "local_pre_idempotent_keys_used": sector33["derived"][
                    "local_pre_idempotent_keys_used"
                ],
            },
            "matrix_theoretic_reading": "primitive public-zero wall/defect sector",
            "level": "certified unique single-sector public-zero support",
        },
        {
            "d20_layer": "OP11",
            "certified_evidence": {
                "current_status": "proposed finite closure label only",
                "not_used_as_certificate_input": True,
            },
            "matrix_theoretic_reading": "finite 11D closure opcode",
            "level": "conjectural name, not a proved bridge",
        },
    ]


def build_theorem() -> dict[str, Any]:
    constants = load_json(CONSTANTS)
    zero_axiom = load_json(ZERO_AXIOM_COORIENT)
    charge_kernel = load_json(ZERO_PAIR_CHARGE_KERNEL)
    symmetry_ward = load_json(ZERO_PAIR_SYMMETRY_WARD)
    sector26 = load_json(SECTOR26_INVARIANT_SUITE)
    sector33 = load_json(SECTOR33_UNIQUE_PUBLIC_ZERO_SUPPORT)

    selector = zero_axiom["d6_selector"]["construction"]
    kernel_summary = charge_kernel["derived"]["propagator_charge_kernel_summary"]
    ward_summary = symmetry_ward["derived"]["ward_flux_summary"]
    plus_image = kernel_summary["plus_denominator_cleared_sector26_image"]
    minus_image = kernel_summary["minus_denominator_cleared_sector26_image"]
    residue_ids = residue_rows_with_fractional_coefficients(
        charge_kernel["derived"]["residue_charge_rows"]
    )
    missing_bridges = [
        {
            "id": "A985_to_DLCQ_matrix_model",
            "needed_for": "actual Matrix-theory model rather than finite matrix-like evidence",
            "current_status": "missing",
        },
        {
            "id": "D20_to_M2_or_M5_charge_sector",
            "needed_for": "actual M-theory brane charge interpretation",
            "current_status": "missing",
        },
        {
            "id": "sector26_kernel_to_quantized_C_field_or_brane_charge_law",
            "needed_for": "physical flux quantization rather than a finite sector ledger",
            "current_status": "missing",
        },
    ]
    matrix_lift_conjecture = {
        "name": "D20 Matrix Lift Conjecture",
        "status": "registered_conjecture_not_proven",
        "statement": (
            "There exists a finite matrix-theoretic lift M_D20 whose public charge "
            "reduction is the denominator-cleared sector-26 propagator kernel, and "
            "whose primitive wall defect is sector 33."
        ),
        "current_evidence": [
            "A985 is a finite 985-dimensional coherent algebra with center dimension 39.",
            "The public D20 boundary is Lambda^3 H6 with 20 face states and 30 D6 root edges.",
            "The zero-pair Green residues are half-integral before denominator clearing.",
            "The cleared plus/minus residues land in complementary sector-26 charge classes.",
            "Sector 33 is the unique single-sector public-zero support.",
        ],
        "promotion_bridges": missing_bridges,
    }
    classification = {
        "safe_name": "Finite Matrix-Theoretic Charge-Wall Shadow",
        "strength": "finite_shadow_not_m_theory",
        "m_theory_claimed": False,
        "matrix_theory_wall_context": {
            "paper": "A Matrix Theory Construction of the IIA/IIB Wall",
            "arxiv": "2603.02199",
            "role": "motivation only; not used as a local certificate input",
        },
    }
    checks = {
        "a985_finite_matrix_body_is_certified": constants["wedderburn"]["sum_squares"] == 985
        and constants["wedderburn"]["center_dim"] == 39
        and constants["tensor_shape"] == [1414965, 4]
        and constants["coefficient_total"] == 2537360,
        "public_boundary_is_lambda3_h6_with_20_faces_and_30_edges": selector[
            "odd_spinor_face_space"
        ]
        == "Lambda^3 U"
        and selector["odd_spinor_face_basis_count"] == 20
        and selector["d6_projective_root_count"] == 30,
        "zero_pair_charge_kernel_is_certified": charge_kernel.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_PROPAGATOR_CHARGE_KERNEL_CERTIFIED"
        and charge_kernel.get("all_checks_pass") is True,
        "raw_half_residues_require_denominator_clearing": kernel_summary[
            "raw_half_residues_are_not_native_z26_classes"
        ]
        is True
        and len(residue_ids) == 6,
        "sector26_cleared_images_match_expected_doublet": plus_image
        == {
            "sector26_clock_delta_mod26": 8,
            "sector26_clock_pair_mod26": [24, 6],
            "sector26_clock_sum_mod26": 4,
        }
        and minus_image
        == {
            "sector26_clock_delta_mod26": 18,
            "sector26_clock_pair_mod26": [2, 20],
            "sector26_clock_sum_mod26": 22,
        },
        "paired_residue_is_sector26_neutral_in_ward_screen": symmetry_ward.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_PROPAGATOR_SYMMETRY_WARD_CERTIFIED"
        and symmetry_ward.get("all_checks_pass") is True
        and ward_summary["paired_residue_is_sector26_neutral"] is True,
        "sector26_clock_context_is_certified": sector26.get("status")
        == "D20_SECTOR26_INVARIANT_SUITE_CERTIFIED"
        and sector26.get("all_checks_pass") is True
        and sector26["checks"]["d20_public_plus_h6_count_is_26"] is True,
        "sector33_unique_public_zero_wall_is_certified": sector33.get("status")
        == "D20_SECTOR33_UNIQUE_PUBLIC_ZERO_SUPPORT_CERTIFIED"
        and sector33.get("all_checks_pass") is True
        and sector33["derived"]["public_zero_sectors"] == [33],
        "m_theory_promotion_is_not_claimed": classification["m_theory_claimed"] is False
        and classification["strength"] == "finite_shadow_not_m_theory"
        and all(row["current_status"] == "missing" for row in missing_bridges),
        "matrix_lift_conjecture_is_registered_not_proven": matrix_lift_conjecture["status"]
        == "registered_conjecture_not_proven"
        and len(matrix_lift_conjecture["promotion_bridges"]) == 3,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_MATRIX_LIFT_CONJECTURE_REGISTERED"
        if all_checks_pass
        else "D20_MATRIX_LIFT_CONJECTURE_NEEDS_REVIEW"
    )
    report = {
        "schema": "d20.theorem.d20_matrix_lift_conjecture",
        "status": status,
        "object": "d20",
        "claim": (
            "D20 exhibits a finite Matrix-theoretic charge-wall shadow: a finite "
            "matrix/algebraic bulk, a Lambda^3 H6 public boundary, a half-integral "
            "zero-pair propagator residue that descends to a denominator-cleared "
            "sector-26 charge ledger, and a primitive public-zero wall sector 33. "
            "This registers the D20 Matrix Lift Conjecture; it does not prove "
            "M-theory or a DLCQ matrix model."
        ),
        "definition": {
            "finite_matrix_theoretic_charge_wall_shadow": (
                "A local finite dictionary whose entries are all backed by D20 certificates, "
                "but whose physical Matrix/M-theory interpretation remains conjectural."
            ),
            "descended_charge_lattice": (
                "The observed sector-26 ledger after clearing rational pole residues that "
                "are not native Z/26 classes."
            ),
            "matrix_lift_conjecture": matrix_lift_conjecture["statement"],
        },
        "inputs": {
            "constants": input_record(CONSTANTS),
            "zero_axiom_coorient": input_record(ZERO_AXIOM_COORIENT),
            "zero_pair_charge_kernel_report": input_record(ZERO_PAIR_CHARGE_KERNEL),
            "zero_pair_symmetry_ward_report": input_record(ZERO_PAIR_SYMMETRY_WARD),
            "sector26_invariant_suite_report": input_record(SECTOR26_INVARIANT_SUITE),
            "sector33_unique_public_zero_support_report": input_record(
                SECTOR33_UNIQUE_PUBLIC_ZERO_SUPPORT
            ),
        },
        "derived": {
            "classification": classification,
            "finite_shadow_dictionary": build_shadow_dictionary(
                constants, zero_axiom, charge_kernel, sector26, sector33
            ),
            "half_integral_descent": {
                "fractional_residue_ids": residue_ids,
                "raw_half_residues_are_not_native_z26_classes": kernel_summary[
                    "raw_half_residues_are_not_native_z26_classes"
                ],
                "plus_denominator_cleared_sector26_image": plus_image,
                "minus_denominator_cleared_sector26_image": minus_image,
                "paired_residue_is_sector26_neutral": ward_summary[
                    "paired_residue_is_sector26_neutral"
                ],
            },
            "wall_sector": {
                "primitive_wall_sector": 33,
                "public_zero_sectors": sector33["derived"]["public_zero_sectors"],
                "sector_count": sector33["derived"]["sector_count"],
                "local_pre_idempotent_keys_used": sector33["derived"][
                    "local_pre_idempotent_keys_used"
                ],
            },
            "matrix_lift_conjecture": matrix_lift_conjecture,
            "missing_bridge_count": len(missing_bridges),
        },
        "interpretation": {
            "what_this_certifies": [
                "the finite Matrix-theoretic charge-wall dictionary is internally supported by local D20 certificates",
                "the zero-pair residue is half-integral before denominator clearing",
                "the visible sector-26 charge ledger is a descended finite ledger, not the primitive raw residue object",
                "sector 33 is the primitive single-sector public-zero wall candidate in the current D20 model",
            ],
            "what_this_does_not_certify": [
                "a DLCQ matrix model for A985",
                "an M2/M5 charge sector for D20",
                "a quantized C-field or physical brane charge law for the sector-26 kernel",
                "OP11 as a proved finite 11-dimensional physical opcode",
            ],
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Attack the first promotion bridge: construct or rule out an explicit finite "
            "matrix-model lift M_D20 whose public charge reduction is the "
            "denominator-cleared sector-26 propagator kernel."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {key: value for key, value in report.items() if key != "certificate_sha256"}
    )
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.d20_matrix_lift_conjecture_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify A985 finite matrix/algebraic body data",
            "verify D20 public boundary as Lambda^3 H6 with 20 faces and 30 D6 root edges",
            "verify zero-pair charge-kernel, symmetry/Ward, sector-26, and sector-33 inputs",
            "verify half-integral residues are recorded as non-native Z/26 classes",
            "verify denominator-cleared plus/minus sector-26 images",
            "verify the Matrix/M-theory promotion bridges are explicitly missing",
            "verify the D20 Matrix Lift Conjecture is registered but not proven",
        ],
    }
    manifest["report_sha256"] = report["certificate_sha256"]
    manifest["manifest_sha256"] = sha_json(
        {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    update_theorem_index(report, out_dir)
    return report


def main() -> None:
    report = write_theorem()
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report.get("all_checks_pass"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
