from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

try:
    from src.paths import D20_INVARIANTS, ROOT
except ModuleNotFoundError:  # Supports `python src/derive_d20_minimal_matrix_charge_lift.py`.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "d20_minimal_matrix_charge_lift"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

ZERO_PAIR_CHARGE_KERNEL = (
    D20_INVARIANTS
    / "theorems"
    / "full_exposure_zero_pair_propagator_charge_kernel"
    / "report.json"
)
MATRIX_LIFT_CONJECTURE = (
    D20_INVARIANTS / "theorems" / "d20_matrix_lift_conjecture" / "report.json"
)


Matrix = list[list[Fraction]]
Vector = list[Fraction]


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


def frac(value: str | int) -> Fraction:
    return Fraction(value)


def frac_string(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def matrix_to_strings(matrix: Matrix) -> list[list[str]]:
    return [[frac_string(value) for value in row] for row in matrix]


def vector_to_strings(vector: Vector) -> list[str]:
    return [frac_string(value) for value in vector]


def mat_mul(left: Matrix, right: Matrix) -> Matrix:
    return [
        [
            sum(left[i][k] * right[k][j] for k in range(len(right)))
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def mat_vec(matrix: Matrix, vector: Vector) -> Vector:
    return [sum(matrix[i][j] * vector[j] for j in range(len(vector))) for i in range(len(matrix))]


def mat_add(left: Matrix, right: Matrix) -> Matrix:
    return [
        [left[i][j] + right[i][j] for j in range(len(left[0]))]
        for i in range(len(left))
    ]


def scalar_mat(scalar: Fraction, matrix: Matrix) -> Matrix:
    return [[scalar * value for value in row] for row in matrix]


def zero_matrix(rows: int, cols: int) -> Matrix:
    return [[Fraction(0) for _ in range(cols)] for _ in range(rows)]


def rank_2x2(matrix: Matrix) -> int:
    if matrix == zero_matrix(2, 2):
        return 0
    det = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    return 2 if det != 0 else 1


def vector_is_proportional(left: Vector, right: Vector) -> bool:
    ratio: Fraction | None = None
    for a, b in zip(left, right):
        if b == 0:
            if a != 0:
                return False
            continue
        current = a / b
        if ratio is None:
            ratio = current
        elif current != ratio:
            return False
    return ratio is not None


def mod26_charge_image(coefficients: dict[int, int], charges: dict[int, dict[str, Any]]) -> dict[str, Any]:
    pair = [
        sum(coeff * int(charges[packet]["sector26_clock_pair"][idx]) for packet, coeff in coefficients.items())
        % 26
        for idx in range(2)
    ]
    total = (
        sum(coeff * int(charges[packet]["sector26_clock_sum_mod26"]) for packet, coeff in coefficients.items())
        % 26
    )
    delta = (
        sum(
            coeff * int(charges[packet]["sector26_clock_delta_mod26"])
            for packet, coeff in coefficients.items()
        )
        % 26
    )
    return {
        "sector26_clock_pair_mod26": pair,
        "sector26_clock_sum_mod26": total,
        "sector26_clock_delta_mod26": delta,
    }


def support_charges(charge_kernel: dict[str, Any]) -> dict[int, dict[str, Any]]:
    rows = charge_kernel["derived"]["support_charge_frame_rows"]
    return {
        int(row["packet_id"]): {
            "sector26_clock_pair": row["sector26_clock_pair"],
            "sector26_clock_sum_mod26": row["sector26_clock_sum_mod26"],
            "sector26_clock_delta_mod26": row["sector26_clock_delta_mod26"],
        }
        for row in rows
    }


def residue_vector(row: dict[str, Any], basis_order: list[int]) -> Vector:
    coeffs = row.get("rational_coefficients", {})
    return [frac(coeffs[str(packet_id)]) for packet_id in basis_order]


def build_theorem() -> dict[str, Any]:
    charge_kernel = load_json(ZERO_PAIR_CHARGE_KERNEL)
    matrix_lift = load_json(MATRIX_LIFT_CONJECTURE)

    basis_order = [239, 238]
    identity: Matrix = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]]
    swap: Matrix = [[Fraction(0), Fraction(1)], [Fraction(1), Fraction(0)]]
    p_plus = scalar_mat(Fraction(1, 2), mat_add(identity, swap))
    p_minus = scalar_mat(Fraction(1, 2), mat_add(identity, scalar_mat(Fraction(-1), swap)))
    source = [Fraction(1), Fraction(0)]
    plus_raw = mat_vec(p_plus, source)
    minus_raw = mat_vec(p_minus, source)
    plus_cleared = [int(2 * value) for value in plus_raw]
    minus_cleared = [int(2 * value) for value in minus_raw]

    charges = support_charges(charge_kernel)
    plus_image = mod26_charge_image(dict(zip(basis_order, plus_cleared)), charges)
    minus_image = mod26_charge_image(dict(zip(basis_order, minus_cleared)), charges)
    kernel_summary = charge_kernel["derived"]["propagator_charge_kernel_summary"]

    mode_direction_checks = []
    for row in charge_kernel["derived"]["residue_charge_rows"]:
        direction = plus_raw if row["mode"] == "plus" else minus_raw
        mode_direction_checks.append(
            {
                "residue_id": row["residue_id"],
                "mode": row["mode"],
                "kernel_vector": vector_to_strings(residue_vector(row, basis_order)),
                "projector_direction": vector_to_strings(direction),
                "direction_matches": vector_is_proportional(residue_vector(row, basis_order), direction),
            }
        )

    missing_bridge = next(
        bridge
        for bridge in matrix_lift["derived"]["matrix_lift_conjecture"]["promotion_bridges"]
        if bridge["id"] == "A985_to_DLCQ_matrix_model"
    )
    minimal_lift = {
        "algebra": "Mat_2(Q)",
        "coefficient_ring": "Z[1/2] inside Q",
        "basis_order": basis_order,
        "source_vector": vector_to_strings(source),
        "swap_involution": matrix_to_strings(swap),
        "plus_projector": matrix_to_strings(p_plus),
        "minus_projector": matrix_to_strings(p_minus),
        "plus_raw_residue_vector": vector_to_strings(plus_raw),
        "minus_raw_residue_vector": vector_to_strings(minus_raw),
        "plus_denominator_cleared_vector": plus_cleared,
        "minus_denominator_cleared_vector": minus_cleared,
        "boundary_charge_map_mod26": {str(packet): charges[packet] for packet in basis_order},
        "plus_denominator_cleared_sector26_image": plus_image,
        "minus_denominator_cleared_sector26_image": minus_image,
        "primitive_wall_sector": matrix_lift["derived"]["wall_sector"]["primitive_wall_sector"],
        "lift_status": "minimal_charge_kernel_lift_constructed_full_A985_DLCQ_lift_not_constructed",
    }
    checks = {
        "zero_pair_charge_kernel_is_certified": charge_kernel.get("status")
        == "D20_FULL_EXPOSURE_ZERO_PAIR_PROPAGATOR_CHARGE_KERNEL_CERTIFIED"
        and charge_kernel.get("all_checks_pass") is True,
        "matrix_lift_conjecture_input_is_registered": matrix_lift.get("status")
        == "D20_MATRIX_LIFT_CONJECTURE_REGISTERED"
        and matrix_lift.get("all_checks_pass") is True,
        "swap_is_involution": mat_mul(swap, swap) == identity,
        "projectors_are_idempotent": mat_mul(p_plus, p_plus) == p_plus
        and mat_mul(p_minus, p_minus) == p_minus,
        "projectors_are_orthogonal_and_complete": mat_mul(p_plus, p_minus) == zero_matrix(2, 2)
        and mat_mul(p_minus, p_plus) == zero_matrix(2, 2)
        and mat_add(p_plus, p_minus) == identity,
        "projectors_are_rank_one": rank_2x2(p_plus) == 1 and rank_2x2(p_minus) == 1,
        "source_decomposition_has_half_integral_vectors": plus_raw == [Fraction(1, 2), Fraction(1, 2)]
        and minus_raw == [Fraction(1, 2), Fraction(-1, 2)],
        "residue_directions_match_projector_directions": all(
            row["direction_matches"] for row in mode_direction_checks
        ),
        "denominator_cleared_vectors_match_kernel_classes": plus_cleared == [1, 1]
        and minus_cleared == [1, -1],
        "boundary_charge_map_recovers_sector26_images": plus_image
        == kernel_summary["plus_denominator_cleared_sector26_image"]
        and minus_image == kernel_summary["minus_denominator_cleared_sector26_image"],
        "raw_half_vectors_are_not_native_z26_classes": kernel_summary[
            "raw_half_residues_are_not_native_z26_classes"
        ]
        is True
        and Fraction(1, 2).denominator == 2
        and 26 % 2 == 0,
        "primitive_wall_sector_is_preserved_as_pointer": minimal_lift["primitive_wall_sector"] == 33,
        "full_A985_DLCQ_lift_remains_open": missing_bridge["current_status"] == "missing",
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_MINIMAL_MATRIX_CHARGE_LIFT_CERTIFIED"
        if all_checks_pass
        else "D20_MINIMAL_MATRIX_CHARGE_LIFT_NEEDS_REVIEW"
    )
    report = {
        "schema": "d20.theorem.d20_minimal_matrix_charge_lift",
        "status": status,
        "object": "d20",
        "claim": (
            "The denominator-cleared zero-pair propagator charge kernel admits an explicit "
            "minimal finite matrix charge-lift in Mat_2(Q). On the packet basis [239,238], "
            "the swap involution gives projectors (I+S)/2 and (I-S)/2; applying them to "
            "the zero-pair source produces the certified half-integral plus/minus residue "
            "directions, and clearing denominators recovers the sector-26 ledger images. "
            "This is a charge-kernel lift only, not a full A985-to-DLCQ matrix model."
        ),
        "definition": {
            "minimal_matrix_charge_lift": (
                "The two-dimensional rational matrix algebra generated by the packet-swap "
                "involution on the certified support packets 239 and 238."
            ),
            "boundary_charge_reduction": (
                "The homomorphism from denominator-cleared packet vectors to the sector-26 "
                "ledger, using the certified packet sector-26 charge rows."
            ),
            "scope_boundary": (
                "This constructs the finite charge-kernel lift only. A full Matrix-theory "
                "bridge still needs an A985 representation by matrix degrees of freedom and "
                "a DLCQ-style dynamics."
            ),
        },
        "inputs": {
            "zero_pair_charge_kernel_report": input_record(ZERO_PAIR_CHARGE_KERNEL),
            "d20_matrix_lift_conjecture_report": input_record(MATRIX_LIFT_CONJECTURE),
        },
        "derived": {
            "minimal_matrix_charge_lift": minimal_lift,
            "mode_direction_checks": mode_direction_checks,
            "remaining_promotion_bridge": missing_bridge,
        },
        "interpretation": {
            "what_this_certifies": [
                "the half-integral zero-pair source decomposition is realized by rank-one rational matrix projectors",
                "denominator clearing turns those matrix-residue directions into the certified sector-26 plus/minus ledger classes",
                "the primitive wall sector 33 remains attached as a boundary pointer from the registered conjecture",
            ],
            "what_this_does_not_certify": [
                "a representation of the full A985 multiplication tensor in a DLCQ matrix model",
                "physical time evolution or supersymmetry",
                "a Matrix/M-theory identification beyond the local charge-kernel lift",
            ],
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Try to extend the Mat_2(Q) charge-kernel lift from the packet pair [239,238] "
            "to a representation of the full 20-packet full-exposure propagation algebra, "
            "then test whether any part of A985 acts through that representation."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {key: value for key, value in report.items() if key != "certificate_sha256"}
    )
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.d20_minimal_matrix_charge_lift_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify charge-kernel and matrix-lift-conjecture inputs",
            "verify the packet-swap matrix is an involution",
            "verify plus/minus matrices are rank-one orthogonal projectors summing to identity",
            "verify the zero-pair source decomposes into half-integral plus/minus directions",
            "verify all certified residue rows are proportional to those projector directions",
            "verify denominator-cleared packet vectors recover the sector-26 ledger images",
            "verify the full A985-to-DLCQ bridge remains open",
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
