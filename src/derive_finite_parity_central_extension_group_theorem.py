from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "finite_parity_central_extension_group"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FINITE_KERNEL_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "finite_virasoro_string_kernel_candidate"
    / "report.json"
)
FINITE_GENERATOR_ALGEBRA_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "finite_virasoro_generator_algebra"
    / "report.json"
)
FINITE_CENTRAL_EXTENSION_ANOMALY_COCYCLE_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "finite_central_extension_anomaly_cocycle"
    / "report.json"
)

COORDINATE_COUNT = 10
ACTIVE_LEFT_COORD = 8
ACTIVE_RIGHT_COORD = 9
CENTER_BIT = 1 << COORDINATE_COUNT
KERNEL_SIMPLE_SOURCE_BITS = [0, 1, 2, 3, 4, 6, 7, 8]


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


def gf2_rank(vectors: list[int], width: int = 11) -> int:
    basis = [0] * width
    rank = 0
    for vector in vectors:
        value = vector
        while value:
            pivot = value.bit_length() - 1
            if basis[pivot] == 0:
                basis[pivot] = value
                rank += 1
                break
            value ^= basis[pivot]
    return rank


def mask_from_coord(coord: int) -> int:
    mask = 0
    for coord_idx, source_bit in enumerate(KERNEL_SIMPLE_SOURCE_BITS):
        if (coord >> coord_idx) & 1:
            mask ^= 1 << source_bit
    if (coord >> ACTIVE_LEFT_COORD) & 1:
        mask ^= (1 << 5) | (1 << 9)
    if (coord >> ACTIVE_RIGHT_COORD) & 1:
        mask ^= (1 << 5) | (1 << 10)
    return mask


def coord_from_mask(mask: int) -> int:
    coord = 0
    for coord_idx, source_bit in enumerate(KERNEL_SIMPLE_SOURCE_BITS):
        if (mask >> source_bit) & 1:
            coord |= 1 << coord_idx
    if (mask >> 9) & 1:
        coord |= 1 << ACTIVE_LEFT_COORD
    if (mask >> 10) & 1:
        coord |= 1 << ACTIVE_RIGHT_COORD
    return coord


def coord_bits(coord: int) -> list[int]:
    return [idx for idx in range(COORDINATE_COUNT) if (coord >> idx) & 1]


def parity_cocycle(left: int, right: int) -> int:
    return ((left >> ACTIVE_LEFT_COORD) & 1) & ((right >> ACTIVE_RIGHT_COORD) & 1)


def commutator_pairing(left: int, right: int) -> int:
    return parity_cocycle(left, right) ^ parity_cocycle(right, left)


def encode_group_element(coord: int, central: int) -> int:
    return coord | ((central & 1) << COORDINATE_COUNT)


def decode_group_element(element: int) -> tuple[int, int]:
    return element & (CENTER_BIT - 1), (element >> COORDINATE_COUNT) & 1


def multiply(left_element: int, right_element: int) -> int:
    left_coord, left_central = decode_group_element(left_element)
    right_coord, right_central = decode_group_element(right_element)
    product_coord = left_coord ^ right_coord
    product_central = left_central ^ right_central ^ parity_cocycle(left_coord, right_coord)
    return encode_group_element(product_coord, product_central)


def inverse(element: int) -> int:
    coord, central = decode_group_element(element)
    return encode_group_element(coord, central ^ parity_cocycle(coord, coord))


def square(element: int) -> int:
    return multiply(element, element)


def commutator(left_element: int, right_element: int) -> int:
    return multiply(multiply(multiply(left_element, right_element), inverse(left_element)), inverse(right_element))


def projective_phase(coord: int, central: int, state_coord: int) -> int:
    return central ^ (((coord >> ACTIVE_LEFT_COORD) & 1) & ((state_coord >> ACTIVE_RIGHT_COORD) & 1))


def projective_action(element: int, state_mask: int) -> tuple[int, int]:
    coord, central = decode_group_element(element)
    state_coord = coord_from_mask(state_mask)
    target_coord = coord ^ state_coord
    return mask_from_coord(target_coord), projective_phase(coord, central, state_coord)


def projective_named_action_digest(
    named_lifts: list[dict[str, Any]],
    operator_basis: list[int],
) -> str:
    h = hashlib.sha256()
    h.update(b"[")
    first = True
    for row in named_lifts:
        element = encode_group_element(int(row["coord"]), 0)
        for state_mask in operator_basis:
            target_mask, phase = projective_action(element, state_mask)
            if not first:
                h.update(b",")
            first = False
            h.update(
                json.dumps(
                    [row["generator_label"], int(state_mask), int(target_mask), int(phase)],
                    separators=(",", ":"),
                ).encode("utf-8")
            )
    h.update(b"]")
    return h.hexdigest()


def build_named_lifts(generator_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    lifts = []
    for row in generator_rows:
        mask = int(row["operator_mask"])
        coord = coord_from_mask(mask)
        element = encode_group_element(coord, 0)
        square_element = square(element)
        square_coord, square_central = decode_group_element(square_element)
        lifts.append(
            {
                "generator_label": row["generator_label"],
                "generator_type": row["generator_type"],
                "operator_mask": mask,
                "source_generators": row["source_generators"],
                "coord": coord,
                "coord_support": coord_bits(coord),
                "lift_element": element,
                "square_coord": square_coord,
                "square_central_bit": square_central,
                "lift_order": 4 if square_central else 2,
            }
        )
    return lifts


def named_commutator_table(named_lifts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    table = []
    for left in named_lifts:
        for right in named_lifts:
            comm = commutator(
                encode_group_element(int(left["coord"]), 0),
                encode_group_element(int(right["coord"]), 0),
            )
            comm_coord, comm_central = decode_group_element(comm)
            table.append(
                {
                    "left": left["generator_label"],
                    "right": right["generator_label"],
                    "commutator_coord": comm_coord,
                    "commutator_central_bit": comm_central,
                }
            )
    return table


def build_group_summary(operator_basis: list[int]) -> dict[str, Any]:
    elements = list(range(1 << (COORDINATE_COUNT + 1)))
    order_counter: Counter[int] = Counter()
    square_counter: Counter[int] = Counter()
    inverse_failures = 0
    for element in elements:
        sq = square(element)
        square_counter[sq] += 1
        if element == 0:
            order_counter[1] += 1
        elif sq == 0:
            order_counter[2] += 1
        elif square(sq) == 0:
            order_counter[4] += 1
        else:
            order_counter["other"] += 1
        if multiply(element, inverse(element)) != 0 or multiply(inverse(element), element) != 0:
            inverse_failures += 1

    commutator_counter: Counter[int] = Counter()
    noncentral_commutator_count = 0
    for left_coord in range(1 << COORDINATE_COUNT):
        for right_coord in range(1 << COORDINATE_COUNT):
            comm = commutator(
                encode_group_element(left_coord, 0),
                encode_group_element(right_coord, 0),
            )
            comm_coord, comm_central = decode_group_element(comm)
            commutator_counter[comm_central] += 1
            if comm_coord != 0:
                noncentral_commutator_count += 1

    center_coords = [
        coord
        for coord in range(1 << COORDINATE_COUNT)
        if all(commutator_pairing(coord, test_coord) == 0 for test_coord in range(1 << COORDINATE_COUNT))
    ]
    radical_masks = [mask_from_coord(coord) for coord in center_coords]

    return {
        "group_order": len(elements),
        "base_kernel_order": len(operator_basis),
        "central_order": 2,
        "extension_group_type": "D8 x C2^8",
        "nilpotency_class": 2,
        "exponent": 4,
        "derived_subgroup_order": len([key for key, value in commutator_counter.items() if value]),
        "center_order": len(center_coords) * 2,
        "commutator_pairing_rank": 2,
        "radical_dimension": gf2_rank(radical_masks),
        "radical_coord_count": len(center_coords),
        "element_order_histogram": histogram(order_counter),
        "square_histogram_by_encoded_element": histogram(square_counter),
        "commutator_central_bit_histogram_on_base_pairs": histogram(commutator_counter),
        "noncentral_commutator_count": noncentral_commutator_count,
        "inverse_failure_count": inverse_failures,
    }


def active_bit_cocycle_identity_rows() -> list[dict[str, int]]:
    rows = []
    for x_left in (0, 1):
        for x_right in (0, 1):
            x = (x_left << ACTIVE_LEFT_COORD) | (x_right << ACTIVE_RIGHT_COORD)
            for y_left in (0, 1):
                for y_right in (0, 1):
                    y = (y_left << ACTIVE_LEFT_COORD) | (y_right << ACTIVE_RIGHT_COORD)
                    for z_left in (0, 1):
                        for z_right in (0, 1):
                            z = (z_left << ACTIVE_LEFT_COORD) | (z_right << ACTIVE_RIGHT_COORD)
                            lhs = parity_cocycle(y, z) ^ parity_cocycle(x, y ^ z)
                            rhs = parity_cocycle(x, y) ^ parity_cocycle(x ^ y, z)
                            rows.append(
                                {
                                    "x_left": x_left,
                                    "x_right": x_right,
                                    "y_left": y_left,
                                    "y_right": y_right,
                                    "z_left": z_left,
                                    "z_right": z_right,
                                    "lhs": lhs,
                                    "rhs": rhs,
                                    "passes": int(lhs == rhs),
                                }
                            )
    return rows


def active_bit_projective_identity_rows() -> list[dict[str, int]]:
    rows = []
    for x_left in (0, 1):
        for x_right in (0, 1):
            x = (x_left << ACTIVE_LEFT_COORD) | (x_right << ACTIVE_RIGHT_COORD)
            for y_left in (0, 1):
                for y_right in (0, 1):
                    y = (y_left << ACTIVE_LEFT_COORD) | (y_right << ACTIVE_RIGHT_COORD)
                    for state_right in (0, 1):
                        state = state_right << ACTIVE_RIGHT_COORD
                        lhs = projective_phase(y, 0, state) ^ projective_phase(x, 0, state ^ y)
                        rhs = parity_cocycle(x, y) ^ projective_phase(x ^ y, 0, state)
                        rows.append(
                            {
                                "x_left": x_left,
                                "x_right": x_right,
                                "y_left": y_left,
                                "y_right": y_right,
                                "state_right": state_right,
                                "lhs": lhs,
                                "rhs": rhs,
                                "passes": int(lhs == rhs),
                            }
                        )
    return rows


def build_theorem() -> dict[str, Any]:
    kernel = load_json(FINITE_KERNEL_REPORT)
    algebra = load_json(FINITE_GENERATOR_ALGEBRA_REPORT)
    cocycle = load_json(FINITE_CENTRAL_EXTENSION_ANOMALY_COCYCLE_REPORT)
    operator_basis = [int(mask) for mask in kernel["derived"]["kernel_closure_mode_masks"]]
    operator_basis_set = set(operator_basis)
    generator_rows = algebra["derived"]["generator_rows"]
    named_lifts = build_named_lifts(generator_rows)
    named_lift_order = {
        str(row["generator_label"]): idx for idx, row in enumerate(named_lifts)
    }
    commutator_table = named_commutator_table(named_lifts)
    nonzero_named_commutators = [
        row
        for row in commutator_table
        if int(row["commutator_central_bit"]) != 0
    ]
    unordered_nonzero_named_commutators = [
        {
            "left": row["left"],
            "right": row["right"],
            "commutator_central_bit": row["commutator_central_bit"],
        }
        for row in nonzero_named_commutators
        if named_lift_order[row["left"]] < named_lift_order[row["right"]]
    ]
    relation_lift_product = 0
    for label in ["C5_9", "C5_10", "C9_10"]:
        coord = next(int(row["coord"]) for row in named_lifts if row["generator_label"] == label)
        relation_lift_product = multiply(relation_lift_product, encode_group_element(coord, 0))
    relation_coord, relation_central = decode_group_element(relation_lift_product)
    active_cocycle_rows = active_bit_cocycle_identity_rows()
    active_projective_rows = active_bit_projective_identity_rows()
    group_summary = build_group_summary(operator_basis)

    roundtrip_failures = [
        mask
        for mask in operator_basis
        if mask_from_coord(coord_from_mask(mask)) != mask
    ]
    coord_image = {coord_from_mask(mask) for mask in operator_basis}
    generator_projection_failures = []
    for row in named_lifts:
        element = encode_group_element(int(row["coord"]), 0)
        for state_mask in operator_basis:
            target_mask, _phase = projective_action(element, state_mask)
            if target_mask not in operator_basis_set:
                generator_projection_failures.append([row["generator_label"], state_mask, target_mask])
    named_composition_failure_count = 0
    for left in named_lifts:
        left_element = encode_group_element(int(left["coord"]), 0)
        for right in named_lifts:
            right_element = encode_group_element(int(right["coord"]), 0)
            product_element = multiply(left_element, right_element)
            for state_mask in operator_basis:
                mid_mask, mid_phase = projective_action(right_element, state_mask)
                target_mask, target_phase = projective_action(left_element, mid_mask)
                product_mask, product_phase = projective_action(product_element, state_mask)
                if target_mask != product_mask or (mid_phase ^ target_phase) != product_phase:
                    named_composition_failure_count += 1

    expected_unordered_triangle = [
        {"left": "C5_10", "right": "C9_10", "commutator_central_bit": 1},
        {"left": "C5_9", "right": "C5_10", "commutator_central_bit": 1},
        {"left": "C5_9", "right": "C9_10", "commutator_central_bit": 1},
    ]
    expected_unordered_triangle = sorted(expected_unordered_triangle, key=lambda row: (row["left"], row["right"]))
    unordered_nonzero_named_commutators = sorted(
        unordered_nonzero_named_commutators,
        key=lambda row: (row["left"], row["right"]),
    )

    checks = {
        "finite_kernel_candidate_is_certified": kernel.get("status")
        == "D20_FINITE_VIRASORO_STRING_KERNEL_CANDIDATE_CERTIFIED"
        and kernel.get("all_checks_pass") is True,
        "finite_generator_algebra_is_certified": algebra.get("status")
        == "D20_FINITE_VIRASORO_GENERATOR_ALGEBRA_CERTIFIED"
        and algebra.get("all_checks_pass") is True,
        "finite_central_extension_anomaly_cocycle_is_certified": cocycle.get("status")
        == "D20_FINITE_CENTRAL_EXTENSION_ANOMALY_COCYCLE_CERTIFIED"
        and cocycle.get("all_checks_pass") is True,
        "input_cocycle_has_unique_f2_composite_triangle_survivor": cocycle.get("checks", {}).get(
            "f2_compatible_alternating_solution_is_one_dimensional"
        )
        is True
        and cocycle.get("checks", {}).get(
            "f2_representative_is_supported_on_cross_composite_triangle"
        )
        is True,
        "chosen_kernel_coordinates_roundtrip_all_1024_masks": len(roundtrip_failures) == 0
        and len(coord_image) == 1024
        and coord_image == set(range(1 << COORDINATE_COUNT)),
        "chosen_kernel_coordinate_basis_has_rank10": gf2_rank(
            [mask_from_coord(1 << idx) for idx in range(COORDINATE_COUNT)]
        )
        == 10,
        "parity_cocycle_is_normalized": all(
            parity_cocycle(0, coord) == 0 and parity_cocycle(coord, 0) == 0
            for coord in range(1 << COORDINATE_COUNT)
        ),
        "parity_cocycle_identity_holds_on_active_bits": all(
            row["passes"] == 1 for row in active_cocycle_rows
        )
        and len(active_cocycle_rows) == 64,
        "central_extension_group_has_expected_order_center_derived_and_exponent": (
            group_summary["group_order"] == 2048
            and group_summary["center_order"] == 512
            and group_summary["derived_subgroup_order"] == 2
            and group_summary["exponent"] == 4
        ),
        "central_extension_group_has_d8_times_c2_8_type": group_summary[
            "extension_group_type"
        ]
        == "D8 x C2^8"
        and group_summary["radical_dimension"] == 8
        and group_summary["commutator_pairing_rank"] == 2,
        "all_group_elements_have_inverses": group_summary["inverse_failure_count"] == 0,
        "named_commutator_table_is_exact_composite_triangle": unordered_nonzero_named_commutators
        == expected_unordered_triangle
        and len(nonzero_named_commutators) == 6,
        "cross_composite_relation_lifts_to_identity": relation_coord == 0
        and relation_central == 0,
        "c9_10_lift_has_order4_while_c5_9_and_c5_10_lifts_have_order2": {
            row["generator_label"]: row["lift_order"]
            for row in named_lifts
            if row["generator_label"] in {"C5_9", "C5_10", "C9_10"}
        }
        == {"C5_9": 2, "C5_10": 2, "C9_10": 4},
        "projective_action_phase_identity_holds_on_active_bits": all(
            row["passes"] == 1 for row in active_projective_rows
        )
        and len(active_projective_rows) == 32,
        "named_projective_actions_preserve_kernel_states": len(generator_projection_failures) == 0,
        "named_projective_action_composition_matches_group_law": named_composition_failure_count == 0,
        "central_bit_acts_as_global_sign": all(
            projective_action(encode_group_element(0, 1), state_mask) == (state_mask, 1)
            for state_mask in operator_basis
        ),
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FINITE_PARITY_CENTRAL_EXTENSION_GROUP_CERTIFIED"
        if all_checks_pass
        else "D20_FINITE_PARITY_CENTRAL_EXTENSION_GROUP_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.finite_parity_central_extension_group",
        "status": status,
        "object": "d20",
        "claim": (
            "The unique compatible F2 parity cocycle on the finite Virasoro generator layer integrates to "
            "a certified central extension of the rank-10 kernel translation group. In the canonical section "
            "the extension has order 2048, center order 512, derived subgroup order 2, exponent 4, and group "
            "type D8 x C2^8. Its nonzero named commutators are exactly the paired cross-return composite "
            "triangle, and it admits a signed projective action on all 1024 kernel states."
        ),
        "definition": {
            "kernel_coordinates": (
                "Use the eight primitive-preserving coordinates P0,P1,P2,P3,P4,P6,P7,P8 plus "
                "a=C5_9 and b=C5_10; C9_10 is represented by a+b."
            ),
            "central_cocycle": "c(x,y)=x_a y_b in F2.",
            "group_law": "(x,z)(y,t)=(x+y, z+t+c(x,y)).",
            "projective_kernel_action": (
                "rho(x,z)|m> = (-1)^(z + x_a m_b) |m+x>, where m_b is the C5_10 coordinate of the state."
            ),
        },
        "inputs": {
            "finite_virasoro_string_kernel_candidate_report": {
                "path": rel(FINITE_KERNEL_REPORT),
                "sha256": sha_file(FINITE_KERNEL_REPORT),
            },
            "finite_virasoro_generator_algebra_report": {
                "path": rel(FINITE_GENERATOR_ALGEBRA_REPORT),
                "sha256": sha_file(FINITE_GENERATOR_ALGEBRA_REPORT),
            },
            "finite_central_extension_anomaly_cocycle_report": {
                "path": rel(FINITE_CENTRAL_EXTENSION_ANOMALY_COCYCLE_REPORT),
                "sha256": sha_file(FINITE_CENTRAL_EXTENSION_ANOMALY_COCYCLE_REPORT),
            },
        },
        "derived": {
            "central_extension_summary": group_summary,
            "kernel_coordinate_basis": [
                {
                    "coord_index": idx,
                    "basis_mask": mask_from_coord(1 << idx),
                    "basis_source": (
                        f"P{KERNEL_SIMPLE_SOURCE_BITS[idx]}"
                        if idx < len(KERNEL_SIMPLE_SOURCE_BITS)
                        else ("C5_9" if idx == ACTIVE_LEFT_COORD else "C5_10")
                    ),
                }
                for idx in range(COORDINATE_COUNT)
            ],
            "named_lifts": named_lifts,
            "named_lift_commutator_table": commutator_table,
            "named_lift_commutator_table_sha256": sha_json(commutator_table),
            "nonzero_named_lift_commutators": nonzero_named_commutators,
            "cross_composite_relation_lift": {
                "relation_labels": ["C5_9", "C5_10", "C9_10"],
                "product_coord": relation_coord,
                "product_central_bit": relation_central,
            },
            "active_bit_cocycle_identity_rows": active_cocycle_rows,
            "active_bit_projective_identity_rows": active_projective_rows,
            "projective_action_summary": {
                "state_count": len(operator_basis),
                "named_generator_count": len(named_lifts),
                "checked_named_generator_pair_state_compositions": len(named_lifts)
                * len(named_lifts)
                * len(operator_basis),
                "named_composition_failure_count": named_composition_failure_count,
                "generator_projection_failure_count": len(generator_projection_failures),
                "named_projective_action_digest_sha256": projective_named_action_digest(
                    named_lifts, operator_basis
                ),
            },
        },
        "interpretation": {
            "what_this_proves": [
                "the parity cocycle is integrable as a finite central extension group",
                "the extension is nonabelian only in the two-dimensional composite sector",
                "the named commutator anomaly is exactly the composite triangle found by the cocycle search",
                "the central bit acts as a genuine projective sign on the 1024-state kernel action",
            ],
            "what_this_does_not_prove": (
                "This does not yet decompose the signed projective kernel action into irreducible central-character "
                "packets or compare those packets with Loop_297 atom exposure."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Decompose the signed projective kernel action into central-character irreducible packets and compare "
            "the packets with sector-26 clock classes and Loop_297 atom exposure."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.finite_parity_central_extension_group_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify finite kernel, generator algebra, and cocycle inputs",
            "construct the ten-coordinate kernel section and roundtrip all 1024 masks",
            "verify the active-bit F2 cocycle identity and normalized central group law",
            "certify group order, center, derived subgroup, exponent, radical dimension, and D8 x C2^8 type",
            "certify the named commutator table and lifted cross-composite relation",
            "certify the signed projective action on the 1024 kernel states",
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
