#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def sha_array(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def dimension_rows_ok(B: np.ndarray, source_dims: np.ndarray, target_dims: np.ndarray) -> bool:
    return bool(np.array_equal(B @ target_dims, source_dims))


def build_a236_representation_fusion(simple_branching_npz: Path, terminal_npz: Path, out_npz: Path | None = None) -> dict[str, Any]:
    """Build the representation/fusion presentation of A236.

    This is intentionally not an orbital-basis relation partition.  The previous
    selector search proves that the true 236-dimensional layer is invisible to
    low-order relation fusion.  The finite object present in this bundle at this
    layer is the semisimple representation presentation: 34 simple blocks with
    dimensions whose squared sum is 236, plus exact branching into A42 and A12.
    """
    z = np.load(simple_branching_npz)
    B236_42 = np.asarray(z["B236_42"], dtype=np.int64)
    B42_12 = np.asarray(z["B42_12"], dtype=np.int64)
    B236_12 = np.asarray(z["B236_12"], dtype=np.int64)
    comp = np.asarray(z["comp"], dtype=np.int64)
    dims236 = np.asarray(z["dims236"], dtype=np.int64)
    dims42 = np.asarray(z["dims42"], dtype=np.int64)
    dims12 = np.asarray(z["dims12"], dtype=np.int64)

    term = np.load(terminal_npz)
    q42 = np.asarray(term["q42_map"], dtype=np.int64)
    q12 = np.asarray(term["q12_map"], dtype=np.int64)
    q42t = np.asarray(term["q42_tensor"], dtype=np.int64)
    q12t = np.asarray(term["q12_tensor"], dtype=np.int64)

    q42_to_q12_ok = True
    q42_to_q12 = []
    for c in range(42):
        vals = np.unique(q12[q42 == c])
        if vals.size != 1:
            q42_to_q12_ok = False
            q42_to_q12.append(None)
        else:
            q42_to_q12.append(int(vals[0]))

    if out_npz is not None:
        out_npz.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            out_npz,
            dims236=dims236.astype(np.int64),
            dims42=dims42.astype(np.int64),
            dims12=dims12.astype(np.int64),
            B236_42=B236_42.astype(np.int64),
            B42_12=B42_12.astype(np.int64),
            B236_12=B236_12.astype(np.int64),
            comp=(B236_42 @ B42_12).astype(np.int64),
            q42_to_q12=np.array([-1 if x is None else x for x in q42_to_q12], dtype=np.int64),
        )

    result = {
        "selector_kind": "representation/fusion semisimple presentation, not orbital relation partition",
        "A236": {
            "simple_count": int(dims236.size),
            "dimension_sum_squares": int(np.sum(dims236 * dims236)),
            "center_dimension": int(dims236.size),
            "simple_dimensions": dims236.astype(int).tolist(),
            "simple_dimension_histogram": {str(int(k)): int(v) for k, v in zip(*np.unique(dims236, return_counts=True))},
        },
        "A42": {
            "simple_count": int(dims42.size),
            "dimension_sum_squares": int(np.sum(dims42 * dims42)),
            "center_dimension": int(dims42.size),
            "simple_dimensions": dims42.astype(int).tolist(),
            "terminal_tensor_nonzero": int(np.count_nonzero(q42t)),
            "terminal_tensor_coefficient_total": int(q42t.sum()),
        },
        "A12": {
            "simple_count": int(dims12.size),
            "dimension_sum_squares": int(np.sum(dims12 * dims12)),
            "center_dimension": int(dims12.size),
            "simple_dimensions": dims12.astype(int).tolist(),
            "terminal_tensor_nonzero": int(np.count_nonzero(q12t)),
            "terminal_tensor_coefficient_total": int(q12t.sum()),
        },
        "branching": {
            "B236_to_A42_shape": list(B236_42.shape),
            "B42_to_A12_shape": list(B42_12.shape),
            "B236_to_A12_shape": list(B236_12.shape),
            "B236_to_A42_row_dimension_check": dimension_rows_ok(B236_42, dims236, dims42),
            "B42_to_A12_row_dimension_check": dimension_rows_ok(B42_12, dims42, dims12),
            "B236_to_A12_row_dimension_check": dimension_rows_ok(B236_12, dims236, dims12),
            "naturality_B236_12_equals_B236_42_B42_12": bool(np.array_equal(B236_42 @ B42_12, B236_12)),
            "stored_comp_matches": bool(np.array_equal(comp, B236_12) and np.array_equal(comp, B236_42 @ B42_12)),
            "defect_l1": int(np.abs(B236_12 - B236_42 @ B42_12).sum()),
            "matrices_sha256": {
                "B236_42": sha_array(B236_42),
                "B42_12": sha_array(B42_12),
                "B236_12": sha_array(B236_12),
                "dims236": sha_array(dims236),
            },
        },
        "terminal_compatibility": {
            "q42_to_q12_consistent": bool(q42_to_q12_ok),
            "q42_to_q12": q42_to_q12,
            "q42_map_sha256": sha_array(q42),
            "q12_map_sha256": sha_array(q12),
        },
        "interpretation": (
            "The A236 layer in this bundle is now treated as a 34-simple semisimple fusion/representation presentation. "
            "It is not a 236-class relation fusion of the 985 orbital basis; the low-order selector search already obstructs that reading."
        ),
    }
    result["all_checks_pass"] = bool(
        result["A236"]["dimension_sum_squares"] == 236
        and result["A236"]["center_dimension"] == 34
        and result["A42"]["dimension_sum_squares"] == 42
        and result["A12"]["dimension_sum_squares"] == 12
        and result["branching"]["B236_to_A42_row_dimension_check"]
        and result["branching"]["B42_to_A12_row_dimension_check"]
        and result["branching"]["B236_to_A12_row_dimension_check"]
        and result["branching"]["naturality_B236_12_equals_B236_42_B42_12"]
        and result["branching"]["stored_comp_matches"]
        and result["terminal_compatibility"]["q42_to_q12_consistent"]
    )
    return result


def derive_sector33_integral_wall(center_cert_json: Path, integrity_cert_json: Path) -> dict[str, Any]:
    center = load_json(center_cert_json)
    integrity = load_json(integrity_cert_json)
    profiles = center["gluing_and_sector_profiles"]["sector_profiles"]

    public_zero_candidates = []
    for i, p in enumerate(profiles):
        if int(p.get("q42_nonzero_count", -1)) == 0 and int(p.get("q12_nonzero_count", -1)) == 0:
            public_zero_candidates.append(i)
    if len(public_zero_candidates) != 1:
        raise RuntimeError(f"expected one public-zero Drinfeld sector, got {public_zero_candidates}")
    sector = public_zero_candidates[0]
    p = profiles[sector]

    fb = integrity.get("summary", {}).get("finite_base", {})
    primitive_kernel_sector = fb.get("primitive_kernel_sector")

    result = {
        "sector33_derivation_rule": "unique public-zero primitive Drinfeld/Wedderburn sector in the generated center profile",
        "public_zero_candidates": public_zero_candidates,
        "sector": int(sector),
        "sector_is_33": bool(sector == 33),
        "center_profile": {
            "block_dimension": int(p["block_dimension"]),
            "regular_trace_block_square": int(p["regular_trace_block_square"]),
            "permutation_multiplicity": int(p["permutation_multiplicity"]),
            "permutation_rank": int(p["permutation_rank"]),
            "character_support_size": int(p["character_support_size"]),
            "active_objects": p["active_objects"],
            "active_cy_sectors": p["active_cy_sectors"],
            "q42_nonzero_count": int(p["q42_nonzero_count"]),
            "q12_nonzero_count": int(p["q12_nonzero_count"]),
            "object_pre_idempotent_counts": p["object_pre_idempotent_counts"],
            "loop_coordinate_support_total": int(p["loop_coordinate_support_total"]),
        },
        "coorientation_character": {
            "parity_idempotent": "e_-",
            "maps_to": "e_33",
            "meaning": "the sign/odd coorient character is represented by the public-zero central sector",
        },
        "integral_wall": {
            "primitive_kernel_sector": primitive_kernel_sector,
            "public_rank": int(fb.get("public_rank")),
            "public_kernel_dimension": int(fb.get("public_kernel_dimension")),
            "operation_algebra_dimension": int(fb.get("operation_algebra_dimension")),
            "integrity_integral_dimension": int(fb.get("integrity_integral_dimension")),
            "integrity_integral_codimension": int(fb.get("integrity_integral_codimension")),
            "Pi33_in_full_operation_algebra": bool(fb.get("Pi33_in_full_operation_algebra")),
            "delta33_after_public_integral_operations": bool(fb.get("delta33_after_public_integral_operations")),
        },
    }
    result["all_checks_pass"] = bool(
        result["sector_is_33"]
        and result["center_profile"]["block_dimension"] == 2
        and result["center_profile"]["regular_trace_block_square"] == 4
        and result["center_profile"]["permutation_multiplicity"] == 18
        and result["center_profile"]["permutation_rank"] == 36
        and result["center_profile"]["character_support_size"] == 56
        and result["center_profile"]["active_objects"] == ["B+", "S+"]
        and result["center_profile"]["active_cy_sectors"] == ["B", "S"]
        and primitive_kernel_sector == [33]
        and result["integral_wall"]["integrity_integral_dimension"] == 1
        and result["integral_wall"]["integrity_integral_codimension"] == 35
        and result["integral_wall"]["Pi33_in_full_operation_algebra"] is False
        and result["integral_wall"]["delta33_after_public_integral_operations"] is False
    )
    return result


def derive_all(
    simple_branching_npz: Path,
    terminal_npz: Path,
    center_cert_json: Path,
    integrity_cert_json: Path,
    out_npz: Path | None = None,
    out_json: Path | None = None,
) -> dict[str, Any]:
    a236 = build_a236_representation_fusion(simple_branching_npz, terminal_npz, out_npz)
    sector33 = derive_sector33_integral_wall(center_cert_json, integrity_cert_json)
    result = {
        "schema": "d20.constructor.remaining_representation_integral_chain@1",
        "constructor_status": "REPRESENTATION_FUSION_AND_SECTOR33_INTEGRAL_WALL_PASS" if (a236["all_checks_pass"] and sector33["all_checks_pass"]) else "REPRESENTATION_FUSION_AND_SECTOR33_INTEGRAL_WALL_FAIL",
        "predicate": "is integral",
        "corrected_midlevel_reading": "A236 is a semisimple representation/fusion presentation; not a 236-relation orbital selector.",
        "a236_representation_fusion": a236,
        "sector33_integral_wall": sector33,
        "what_is_now_generated_or_derived": [
            "A236 semisimple presentation from representation/fusion simple data",
            "B236->A42, A42->A12, and B236->A12 branching matrices with exact naturality",
            "sector 33 from the unique public-zero central/Wedderburn profile",
            "integral wall invariants from the sector-33 proof-system integrity ladder",
        ],
        "remaining_boundary": [
            "derive fixed coorient generator permutations from a smaller typed coorient formula",
            "materialize primitive central idempotent coordinate matrices from generated T985 rather than using the certified Drinfeld center profile",
            "derive the A236 semisimple branching data directly from generated primitive central/idempotent coordinates rather than loading the compact simple-branching seed",
        ],
    }
    result["constructor_result_sha256"] = sha_json({k: v for k, v in result.items() if k != "constructor_result_sha256"})
    if out_json is not None:
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--simple-branching", default="data/raw/simple_branching_matrices.npz")
    ap.add_argument("--terminal", default="generated/terminal_quotients_from_source_coorient.npz")
    ap.add_argument("--center-cert", default="layers/06_drinfeld_full_A985_lift/certificate.json")
    ap.add_argument("--integrity-cert", default="layers/25_proof_system_integrity/certificate.json")
    ap.add_argument("--out-npz", default="generated/a236_representation_fusion_from_center.npz")
    ap.add_argument("--out-json", default="generated/remaining_representation_integral_chain_report.json")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()
    res = derive_all(
        ROOT / args.simple_branching,
        ROOT / args.terminal,
        ROOT / args.center_cert,
        ROOT / args.integrity_cert,
        ROOT / args.out_npz,
        ROOT / args.out_json,
    )
    print(json.dumps(res, indent=2 if args.pretty else None, sort_keys=True))


if __name__ == "__main__":
    main()
