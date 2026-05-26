from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from src.paths import D20_INVARIANTS, DATA, ROOT
from src.derive_sector33_boundary_annihilation_theorem import (
    FIELD_PRIME,
    build_pair_projections,
    multiply,
    rref_nullspace_mod,
    regular_trace_coefficients,
    signed_mod,
    vec_digest,
)
from src.derive_sector33_residual_lift_theorem import quotient_shadow
from src.derive_sector33_unique_public_zero_support_theorem import (
    CORE_A985,
    FULL_A985_LIFT,
    QUOTIENT_NPZ,
    RELATION_NPZ,
    TENSOR_NPZ,
    load_json,
    local_idempotent_cache,
    sector_vector,
)
from src.derive_sector_public_shadow_kernel_theorem import quotient_vector


THEOREM_ID = "sector_idempotent_support_admissibility"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

SECTOR_PUBLIC_SHADOW_KERNEL_REPORT = (
    D20_INVARIANTS / "theorems" / "sector_public_shadow_kernel" / "report.json"
)
ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT = (
    D20_INVARIANTS / "theorems" / "sector33_all_residue_height_transport" / "report.json"
)


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


def rank_mod(matrix: np.ndarray, mod: int = FIELD_PRIME) -> int:
    matrix = np.asarray(matrix, dtype=np.int64)
    return int(matrix.shape[1] - rref_nullspace_mod(matrix, mod).shape[1])


def independent_row_indices(matrix: np.ndarray) -> list[int]:
    selected: list[int] = []
    current = np.zeros((0, matrix.shape[1]), dtype=np.int64)
    current_rank = 0
    for row_index in range(matrix.shape[0]):
        candidate = np.vstack([current, matrix[row_index : row_index + 1]]) % FIELD_PRIME
        candidate_rank = rank_mod(candidate)
        if candidate_rank > current_rank:
            selected.append(row_index)
            current = candidate
            current_rank = candidate_rank
        if current_rank == rank_mod(matrix):
            break
    return selected


def subset_sum_map(columns: np.ndarray) -> dict[tuple[int, ...], list[int]]:
    sums: dict[tuple[int, ...], list[int]] = {}
    vector_count = int(columns.shape[1])
    for mask in range(1 << vector_count):
        total = np.zeros(int(columns.shape[0]), dtype=np.int64)
        bitset = mask
        bit = 0
        while bitset:
            if bitset & 1:
                total = (total + columns[:, bit]) % FIELD_PRIME
            bitset >>= 1
            bit += 1
        key = tuple(int(value) for value in total.tolist())
        sums.setdefault(key, []).append(mask)
    return sums


def boolean_kernel_solutions(reduced_matrix: np.ndarray) -> list[int]:
    column_count = int(reduced_matrix.shape[1])
    split = column_count // 2
    left = reduced_matrix[:, :split]
    right = reduced_matrix[:, split:]
    left_sums = subset_sum_map(left)
    solutions: list[int] = []
    for right_mask in range(1 << int(right.shape[1])):
        total = np.zeros(int(right.shape[0]), dtype=np.int64)
        bitset = right_mask
        bit = 0
        while bitset:
            if bitset & 1:
                total = (total + right[:, bit]) % FIELD_PRIME
            bitset >>= 1
            bit += 1
        need = tuple(int((-value) % FIELD_PRIME) for value in total.tolist())
        for left_mask in left_sums.get(need, []):
            solutions.append(int(left_mask | (right_mask << split)))
    return sorted(solutions)


def mask_to_sectors(mask: int, sectors: list[int]) -> list[int]:
    return [sector for idx, sector in enumerate(sectors) if (mask >> idx) & 1]


def sector_sum_vector(sector_support: list[int], vectors_by_sector: dict[int, np.ndarray], relation_count: int) -> np.ndarray:
    vector = np.zeros(relation_count, dtype=np.int64)
    for sector in sector_support:
        vector = (vector + vectors_by_sector[sector]) % FIELD_PRIME
    return vector


def support_is_minimal(support: list[int], nonzero_supports: list[list[int]]) -> bool:
    own = set(support)
    return not any(set(other) < own for other in nonzero_supports)


def candidate_summary(
    sector_support: list[int],
    vector: np.ndarray,
    q42: np.ndarray,
    q12: np.ndarray,
    triples: np.ndarray,
    trace_coeff: np.ndarray,
    profiles_by_sector: dict[int, dict[str, Any]],
    projections: dict[tuple[int, int], np.ndarray],
) -> dict[str, Any]:
    q42_shadow = quotient_shadow(vector, q42, 42)
    q12_shadow = quotient_shadow(vector, q12, 12)
    square = multiply(triples, vector, vector)
    boundary_left_nonzero = 0
    boundary_right_nonzero = 0
    boundary_pair_failures = []
    for removed_added, pair_vector in sorted(projections.items()):
        left = multiply(triples, vector, pair_vector)
        right = multiply(triples, pair_vector, vector)
        left_support = int(np.count_nonzero(left))
        right_support = int(np.count_nonzero(right))
        if left_support or right_support:
            boundary_left_nonzero += int(left_support > 0)
            boundary_right_nonzero += int(right_support > 0)
            boundary_pair_failures.append(
                {
                    "removed_added": [int(removed_added[0]), int(removed_added[1])],
                    "left_support": left_support,
                    "right_support": right_support,
                }
            )
    trace_value = int((trace_coeff @ vector) % FIELD_PRIME)
    return {
        "sector_support": sector_support,
        "sector_count": len(sector_support),
        "sector_dimensions": [int(profiles_by_sector[sector]["block_dimension"]) for sector in sector_support],
        "dimension_sum": int(sum(int(profiles_by_sector[sector]["block_dimension"]) for sector in sector_support)),
        "regular_trace": trace_value,
        "regular_trace_signed": signed_mod(trace_value),
        "regular_trace_block_square_sum": int(
            sum(int(profiles_by_sector[sector]["block_dimension"]) ** 2 for sector in sector_support)
        ),
        "vector": vec_digest(vector),
        "is_idempotent": bool(np.array_equal(square, vector % FIELD_PRIME)),
        "q42_nonzero_count": int(q42_shadow["nonzero_count"]),
        "q12_nonzero_count": int(q12_shadow["nonzero_count"]),
        "public_zero": bool(q42_shadow["nonzero_count"] == 0 and q12_shadow["nonzero_count"] == 0),
        "boundary_left_nonzero_pair_count": boundary_left_nonzero,
        "boundary_right_nonzero_pair_count": boundary_right_nonzero,
        "boundary_null": bool(boundary_left_nonzero == 0 and boundary_right_nonzero == 0),
        "boundary_pair_failures": boundary_pair_failures,
    }


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
        index = json.loads(index_path.read_text(encoding="utf-8"))
        theorems = [item for item in index.get("theorems", []) if item.get("id") != THEOREM_ID]
    else:
        theorems = []
    theorems.append(entry)
    theorems = sorted(theorems, key=lambda item: item["id"])
    index = {
        "schema": "d20.theorem_registry.source_drop",
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": len(theorems),
        "theorems": theorems,
    }
    index["registry_sha256"] = sha_json({k: v for k, v in index.items() if k != "registry_sha256"})
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_theorem() -> dict[str, Any]:
    public_shadow_kernel = load_json(SECTOR_PUBLIC_SHADOW_KERNEL_REPORT)
    all_residue_transport = load_json(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT)
    full = load_json(FULL_A985_LIFT)
    core = load_json(CORE_A985)["blocks"]["tube_center_primitive_idempotents"]
    relation_npz = np.load(RELATION_NPZ)
    block_i = np.asarray(relation_npz["block_i"], dtype=np.int64)
    block_j = np.asarray(relation_npz["block_j"], dtype=np.int64)
    quotient_npz = np.load(QUOTIENT_NPZ)
    q42 = np.asarray(quotient_npz["q42_map"], dtype=np.int64)
    q12 = np.asarray(quotient_npz["q12_map"], dtype=np.int64)
    triples = np.asarray(np.load(TENSOR_NPZ)["triples"], dtype=np.int64)
    trace_coeff = regular_trace_coefficients(triples, int(block_i.shape[0]))
    projections = build_pair_projections(triples, block_i, block_j)

    profiles = full["gluing_and_sector_profiles"]["sector_profiles"]
    profiles_by_sector = {int(profile["sector"]): profile for profile in profiles}
    cache, _ = local_idempotent_cache(core, triples, block_i, block_j)

    sectors: list[int] = []
    vectors_by_sector: dict[int, np.ndarray] = {}
    shadow_columns: list[np.ndarray] = []
    for profile in profiles:
        sector = int(profile["sector"])
        vector, _ = sector_vector(profile, cache, int(block_i.shape[0]))
        sectors.append(sector)
        vectors_by_sector[sector] = vector
        shadow_columns.append(
            np.concatenate(
                [
                    quotient_vector(vector, q42, 42),
                    quotient_vector(vector, q12, 12),
                ]
            )
            % FIELD_PRIME
        )

    orthogonality_failures = []
    for left_index, left_sector in enumerate(sectors):
        for right_index, right_sector in enumerate(sectors[left_index:], start=left_index):
            product = multiply(triples, vectors_by_sector[left_sector], vectors_by_sector[right_sector])
            expected = (
                vectors_by_sector[left_sector] % FIELD_PRIME
                if left_index == right_index
                else np.zeros(int(block_i.shape[0]), dtype=np.int64)
            )
            if not np.array_equal(product, expected):
                orthogonality_failures.append(
                    {
                        "left_sector": left_sector,
                        "right_sector": right_sector,
                        "difference_support": int(np.count_nonzero((product - expected) % FIELD_PRIME)),
                    }
                )

    shadow_matrix = np.stack(shadow_columns, axis=1) % FIELD_PRIME
    independent_rows = independent_row_indices(shadow_matrix)
    reduced_shadow_matrix = shadow_matrix[independent_rows, :] % FIELD_PRIME
    boolean_masks = boolean_kernel_solutions(reduced_shadow_matrix)
    candidate_rows = []
    for mask in boolean_masks:
        support = mask_to_sectors(mask, sectors)
        vector = sector_sum_vector(support, vectors_by_sector, int(block_i.shape[0]))
        candidate_rows.append(
            candidate_summary(
                support,
                vector,
                q42,
                q12,
                triples,
                trace_coeff,
                profiles_by_sector,
                projections,
            )
        )

    nonzero_rows = [row for row in candidate_rows if row["sector_support"]]
    nonzero_supports = [row["sector_support"] for row in nonzero_rows]
    for row in candidate_rows:
        row["inclusion_minimal_nonzero"] = bool(
            row["sector_support"] and support_is_minimal(row["sector_support"], nonzero_supports)
        )
        row["contains_sector33"] = 33 in row["sector_support"]
        row["height_support_exact_for_certified_transport"] = row["sector_support"] == [33]

    primitive_single_sector_public_zero = [
        row["sector_support"][0]
        for row in nonzero_rows
        if row["sector_count"] == 1 and row["public_zero"] and row["is_idempotent"]
    ]
    nonzero_public_zero_idempotent_supports = [
        row["sector_support"] for row in nonzero_rows if row["public_zero"] and row["is_idempotent"]
    ]
    nonzero_public_zero_boundary_null_supports = [
        row["sector_support"]
        for row in nonzero_rows
        if row["public_zero"] and row["is_idempotent"] and row["boundary_null"]
    ]
    inclusion_minimal_supports = [
        row["sector_support"] for row in nonzero_rows if row["inclusion_minimal_nonzero"]
    ]
    height_support_exact_supports = [
        row["sector_support"] for row in nonzero_rows if row["height_support_exact_for_certified_transport"]
    ]
    contains_sector33_supports = [
        row["sector_support"] for row in nonzero_rows if row["contains_sector33"]
    ]

    reduced_rank = rank_mod(reduced_shadow_matrix)
    full_rank = rank_mod(shadow_matrix)
    checks = {
        "sector_public_shadow_kernel_is_certified": public_shadow_kernel.get("status")
        == "D20_SECTOR_PUBLIC_SHADOW_KERNEL_CERTIFIED"
        and public_shadow_kernel.get("all_checks_pass") is True,
        "all_residue_height_transport_is_certified": all_residue_transport.get("status")
        == "D20_ALL_RESIDUE_HEIGHT_COHERENT_TRANSPORT_CERTIFIED"
        and all_residue_transport.get("all_checks_pass") is True,
        "sector_count_is_39": len(sectors) == 39,
        "sector_idempotents_are_pairwise_orthogonal": not orthogonality_failures,
        "shadow_matrix_rank_matches_prior_kernel_report": full_rank
        == int(public_shadow_kernel["derived"]["rank_mod_prime"])
        == 12,
        "reduced_shadow_matrix_has_full_row_rank": reduced_shadow_matrix.shape == (12, 39)
        and reduced_rank == 12,
        "boolean_public_zero_solution_count_is_6_including_zero": len(candidate_rows) == 6,
        "all_boolean_solutions_are_public_zero_idempotents": all(
            row["public_zero"] and row["is_idempotent"] for row in candidate_rows
        ),
        "all_boolean_public_zero_idempotents_are_boundary_null": all(
            row["boundary_null"] for row in candidate_rows
        ),
        "nonzero_public_zero_idempotent_count_is_5": len(nonzero_public_zero_idempotent_supports) == 5,
        "primitive_single_sector_public_zero_is_only_33": primitive_single_sector_public_zero == [33],
        "inclusion_minimal_nonzero_public_zero_idempotents_are_three": inclusion_minimal_supports
        == [[6, 26], [25, 26], [33]],
        "certified_height_transport_support_exact_support_is_only_33": height_support_exact_supports
        == [[33]]
        and all_residue_transport.get("checks", {}).get("all_transports_carried_by_sector33") is True,
        "public_zero_idempotent_alone_does_not_imply_pi33_uniqueness": nonzero_public_zero_idempotent_supports
        == [[6, 26], [25, 26], [33], [6, 26, 33], [25, 26, 33]],
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_SECTOR_IDEMPOTENT_SUPPORT_ADMISSIBILITY_CLASSIFIED"
        if all_checks_pass
        else "D20_SECTOR_IDEMPOTENT_SUPPORT_ADMISSIBILITY_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.sector_idempotent_support_admissibility.source_drop",
        "status": status,
        "object": "d20",
        "claim": (
            "In the orthogonal sector-idempotent algebra, public-zero idempotent supports are exactly the "
            "six Boolean sector sums listed in this certificate, including zero. There are five nonzero "
            "public-zero boundary-null idempotent supports, so public-zero idempotence alone does not make "
            "Pi_33 unique. Pi_33 is unique only under primitive/single-sector support, and it is the only "
            "support-exact support for the already-certified sector-33 height transport."
        ),
        "definition": {
            "boolean_sector_idempotent": (
                "Because the 39 sector idempotents are verified pairwise orthogonal, an idempotent in their "
                "span with sector-coordinate coefficients restricted by multiplication has 0/1 sector support."
            ),
            "public_zero_idempotent_support": (
                "A Boolean sector sum whose combined A42/A12 public shadow is zero."
            ),
            "boundary_null": (
                "The support annihilates all 30 directed boundary-to-loop pair projections on both left and right."
            ),
            "height_support_exact": (
                "The support support is exactly the certified support sector support {33} used by the all-residue "
                "height-coherent transport report."
            ),
        },
        "inputs": {
            "sector_public_shadow_kernel_report": {
                "path": rel(SECTOR_PUBLIC_SHADOW_KERNEL_REPORT),
                "sha256": sha_file(SECTOR_PUBLIC_SHADOW_KERNEL_REPORT),
            },
            "all_residue_height_transport_report": {
                "path": rel(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT),
                "sha256": sha_file(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT),
            },
            "full_a985_lift": {
                "path": rel(FULL_A985_LIFT),
                "sha256": sha_file(FULL_A985_LIFT),
            },
            "core_a985": {
                "path": rel(CORE_A985),
                "sha256": sha_file(CORE_A985),
            },
            "relation_memberships": {
                "path": rel(RELATION_NPZ),
                "sha256": sha_file(RELATION_NPZ),
            },
            "quotients": {
                "path": rel(QUOTIENT_NPZ),
                "sha256": sha_file(QUOTIENT_NPZ),
            },
            "t985_tensor": {
                "path": rel(TENSOR_NPZ),
                "sha256": sha_file(TENSOR_NPZ),
            },
        },
        "derived": {
            "field_prime": FIELD_PRIME,
            "sector_order": sectors,
            "orthogonality_failure_count": len(orthogonality_failures),
            "orthogonality_failures": orthogonality_failures,
            "shadow_matrix_shape": list(shadow_matrix.shape),
            "shadow_matrix_rank": full_rank,
            "independent_shadow_row_indices": independent_rows,
            "reduced_shadow_matrix_shape": list(reduced_shadow_matrix.shape),
            "reduced_shadow_matrix_rank": reduced_rank,
            "boolean_public_zero_solution_count_including_zero": len(candidate_rows),
            "nonzero_public_zero_idempotent_supports": nonzero_public_zero_idempotent_supports,
            "nonzero_public_zero_boundary_null_supports": nonzero_public_zero_boundary_null_supports,
            "primitive_single_sector_public_zero": primitive_single_sector_public_zero,
            "inclusion_minimal_nonzero_public_zero_idempotents": inclusion_minimal_supports,
            "public_zero_idempotents_containing_sector33": contains_sector33_supports,
            "height_support_exact_supports_for_certified_transport": height_support_exact_supports,
            "candidate_rows_sha256": sha_json(candidate_rows),
            "candidate_rows": candidate_rows,
        },
        "interpretation": {
            "what_survives": (
                "Pi_33 remains the unique primitive/single-sector public-zero support and the unique support-exact "
                "support for the certified height transport."
            ),
            "what_fails": (
                "The stronger claim that Pi_33 is the only public-zero idempotent support is false: two "
                "non-Pi_33 composites, {6,26} and {25,26}, are also public-zero boundary-null idempotents."
            ),
            "admissibility_boundary": (
                "Future physics statements must specify whether supports are primitive, support-exact, or allowed "
                "to include null composite sectors. Without that seam, public invisibility has gauge-like degeneracy."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Classify the observable meaning of the two non-Pi_33 null composite supports {6,26} and {25,26}: "
            "gauge redundancy, superselection degeneracy, or additional hidden boundary sectors."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.sector_idempotent_support_admissibility_manifest.source_drop",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify the 39 sector idempotents are pairwise orthogonal",
            "reduce the combined A42/A12 sector-shadow matrix to an independent 12-row witness",
            "enumerate all Boolean sector sums with zero public shadow",
            "verify each Boolean solution is an idempotent",
            "verify each Boolean solution annihilates all directed boundary pair projections",
            "separate primitive/single-sector support from composite null supports",
            "identify the unique support-exact support for the certified sector-33 height transport",
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
