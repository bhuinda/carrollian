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
    rref_nullspace_mod,
    signed_mod,
    vec_digest,
)
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


THEOREM_ID = "sector_public_shadow_kernel"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

UNIQUE_PUBLIC_ZERO_SUPPORT_REPORT = (
    D20_INVARIANTS / "theorems" / "sector33_unique_public_zero_support" / "report.json"
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


def quotient_vector(vec: np.ndarray, quotient_map: np.ndarray, dimension: int) -> np.ndarray:
    out = np.zeros(dimension, dtype=np.int64)
    for idx in np.nonzero(vec % FIELD_PRIME)[0]:
        q = int(quotient_map[int(idx)])
        out[q] = (out[q] + int(vec[int(idx)])) % FIELD_PRIME
    return out


def support_digest(vec: np.ndarray) -> dict[str, Any]:
    return vec_digest(vec % FIELD_PRIME)


def kernel_row(coefficients: np.ndarray, sectors: list[int]) -> dict[str, Any]:
    entries = []
    for idx, value in enumerate((coefficients % FIELD_PRIME).tolist()):
        if int(value) == 0:
            continue
        entries.append(
            {
                "sector": sectors[idx],
                "coefficient_mod_prime": int(value),
                "coefficient_signed": signed_mod(int(value)),
            }
        )
    return {
        "support": [entry["sector"] for entry in entries],
        "support_size": len(entries),
        "entries": entries,
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
    unique_support = load_json(UNIQUE_PUBLIC_ZERO_SUPPORT_REPORT)
    full = load_json(FULL_A985_LIFT)
    core = load_json(CORE_A985)["blocks"]["tube_center_primitive_idempotents"]
    relation_npz = np.load(RELATION_NPZ)
    block_i = np.asarray(relation_npz["block_i"], dtype=np.int64)
    block_j = np.asarray(relation_npz["block_j"], dtype=np.int64)
    quotients = np.load(QUOTIENT_NPZ)
    q42 = np.asarray(quotients["q42_map"], dtype=np.int64)
    q12 = np.asarray(quotients["q12_map"], dtype=np.int64)
    triples = np.asarray(np.load(TENSOR_NPZ)["triples"], dtype=np.int64)

    profiles = full["gluing_and_sector_profiles"]["sector_profiles"]
    cache, _ = local_idempotent_cache(core, triples, block_i, block_j)

    sectors: list[int] = []
    shadow_columns: list[np.ndarray] = []
    sector_rows: list[dict[str, Any]] = []
    for profile in profiles:
        sector = int(profile["sector"])
        vec, keys = sector_vector(profile, cache, int(block_i.shape[0]))
        q42_shadow = quotient_vector(vec, q42, 42)
        q12_shadow = quotient_vector(vec, q12, 12)
        combined_shadow = np.concatenate([q42_shadow, q12_shadow]) % FIELD_PRIME
        sectors.append(sector)
        shadow_columns.append(combined_shadow)
        sector_rows.append(
            {
                "sector": sector,
                "local_pre_idempotent_keys": [[int(obj), int(local)] for obj, local in keys],
                "q42_shadow": support_digest(q42_shadow),
                "q12_shadow": support_digest(q12_shadow),
                "combined_public_shadow": support_digest(combined_shadow),
                "is_coordinate_axis_public_zero": bool(np.count_nonzero(combined_shadow) == 0),
            }
        )

    shadow_matrix = np.stack(shadow_columns, axis=1) % FIELD_PRIME
    kernel_basis = rref_nullspace_mod(shadow_matrix, FIELD_PRIME)
    kernel_dimension = int(kernel_basis.shape[1])
    rank_mod_prime = int(shadow_matrix.shape[1] - kernel_dimension)
    kernel_basis_rows = [
        kernel_row(kernel_basis[:, idx], sectors) for idx in range(kernel_dimension)
    ]
    coordinate_axis_public_zero_sectors = [
        row["sector"] for row in sector_rows if row["is_coordinate_axis_public_zero"]
    ]
    e33_basis_column_indices = [
        idx
        for idx, row in enumerate(kernel_basis_rows)
        if row["support"] == [33]
        and row["entries"][0]["coefficient_mod_prime"] == 1
    ]
    non_axis_kernel_basis_count = sum(row["support"] != [33] for row in kernel_basis_rows)
    nullspace_residual = (shadow_matrix @ kernel_basis) % FIELD_PRIME
    kernel_relation_nullspace = rref_nullspace_mod(kernel_basis, FIELD_PRIME)

    checks = {
        "unique_public_zero_support_theorem_is_certified": unique_support.get("status")
        == "D20_SECTOR33_UNIQUE_PUBLIC_ZERO_SUPPORT_CERTIFIED"
        and unique_support.get("all_checks_pass") is True,
        "sector_count_is_39": len(sectors) == 39,
        "combined_shadow_matrix_shape_is_54_by_39": list(shadow_matrix.shape) == [54, 39],
        "kernel_basis_annihilates_public_shadow_matrix": int(np.count_nonzero(nullspace_residual)) == 0,
        "kernel_basis_columns_are_independent": kernel_relation_nullspace.shape[1] == 0,
        "rank_nullity_sum_is_39": rank_mod_prime + kernel_dimension == 39,
        "coordinate_axis_public_zero_sector_is_only_33": coordinate_axis_public_zero_sectors == [33],
        "e33_axis_vector_is_kernel_basis_element": len(e33_basis_column_indices) == 1,
        "full_public_shadow_kernel_dimension_is_27": kernel_dimension == 27,
        "full_public_zero_sector_span_is_not_one_dimensional": kernel_dimension > 1
        and non_axis_kernel_basis_count > 0,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_SECTOR_PUBLIC_SHADOW_KERNEL_CERTIFIED"
        if all_checks_pass
        else "D20_SECTOR_PUBLIC_SHADOW_KERNEL_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.sector_public_shadow_kernel.source_drop",
        "status": status,
        "object": "d20",
        "claim": (
            "The combined A42/A12 public-shadow map on the 39 materialized tube-visible sector idempotents "
            "has rank 12 and kernel dimension 27 over F_1000003. Sector 33 is the only coordinate-axis "
            "public-zero sector idempotent, but it is not the only vector in the full linear public-zero "
            "sector span."
        ),
        "definition": {
            "sector_shadow_matrix": (
                "The 54 x 39 matrix whose sector column is q42(e_s) concatenated with q12(e_s), where "
                "e_s is reconstructed from the local closed-loop pre-idempotents in the sector profile."
            ),
            "coordinate_axis_public_zero": "A single sector e_s whose combined A42/A12 shadow column is zero.",
            "linear_public_zero_span": "The kernel of the sector_shadow_matrix over F_1000003.",
        },
        "inputs": {
            "unique_public_zero_support_report": {
                "path": rel(UNIQUE_PUBLIC_ZERO_SUPPORT_REPORT),
                "sha256": sha_file(UNIQUE_PUBLIC_ZERO_SUPPORT_REPORT),
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
            "shadow_matrix_shape": list(shadow_matrix.shape),
            "shadow_matrix_sha256": sha_json(shadow_matrix.tolist()),
            "rank_mod_prime": rank_mod_prime,
            "kernel_dimension": kernel_dimension,
            "coordinate_axis_public_zero_sectors": coordinate_axis_public_zero_sectors,
            "e33_basis_column_indices": e33_basis_column_indices,
            "non_axis_kernel_basis_count": non_axis_kernel_basis_count,
            "kernel_basis_sha256": sha_json(kernel_basis.tolist()),
            "kernel_basis": kernel_basis_rows,
            "sector_rows_sha256": sha_json(sector_rows),
            "sector_rows": sector_rows,
        },
        "interpretation": {
            "single_sector_result": (
                "The prior unique-support theorem remains true: e_33 is the only individual sector "
                "idempotent with zero A42/A12 shadow."
            ),
            "linear_span_result": (
                "The stronger kernel-one conjecture is false for the unconstrained sector-idempotent span: "
                "there are 26 additional basis directions in the public-zero kernel."
            ),
            "admissibility_boundary": (
                "Any statement that Pi_33 is the unique physical support must include an admissibility "
                "condition stronger than linear public invisibility, such as coordinate-axis sector selection, "
                "idempotent support selection, or height-coherent transport compatibility."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Classify which of the 27 public-zero kernel directions are admissible supports under the "
            "multiplicative idempotent and height-coherent transport constraints."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.sector_public_shadow_kernel_manifest.source_drop",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "reconstruct all 39 tube-visible sector idempotents",
            "build the combined A42/A12 sector public-shadow matrix",
            "compute the F_1000003 kernel of the 54 x 39 public-shadow matrix",
            "verify the kernel basis annihilates the public-shadow matrix",
            "verify sector 33 is the only coordinate-axis public-zero sector",
            "verify the full linear public-zero sector span has dimension 27",
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
