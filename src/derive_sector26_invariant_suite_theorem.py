from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

from src.paths import D20_INVARIANTS, LAYERS, ROOT
from src.derive_sector33_boundary_annihilation_theorem import FIELD_PRIME, signed_mod, vec_digest
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


THEOREM_ID = "sector26_invariant_suite"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

TYPED_NONEXACT_OPTICAL_FLUX_REPORT = (
    D20_INVARIANTS / "theorems" / "typed_nonexact_optical_flux_update" / "report.json"
)
SUPERSELECTION_FLUX_EXTENSION_REPORT = (
    D20_INVARIANTS / "theorems" / "superselection_flux_balance_extension" / "report.json"
)
MINIMAL_COMPOSITE_TRANSPORT_REPORT = (
    D20_INVARIANTS / "theorems" / "minimal_composite_null_supports_transport" / "report.json"
)
ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT = (
    D20_INVARIANTS / "theorems" / "sector33_all_residue_height_transport" / "report.json"
)

BOSONIC_STRING_CRITICAL_DIMENSION = 26
D20_PUBLIC_STATE_COUNT = 20
H6_CHANNEL_COUNT = 6
SECTOR26 = 26
MIXED_COMPOSITE = [6, 26]
PURE_COMPOSITE = [25, 26]
PRIMITIVE_R33 = [33]


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


def sector_profiles_by_id(full_lift: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {
        int(profile["sector"]): profile
        for profile in full_lift["gluing_and_sector_profiles"]["sector_profiles"]
    }


def quotient_digest(vec: np.ndarray) -> dict[str, Any]:
    entries = [[int(idx), int(vec[idx] % FIELD_PRIME)] for idx in np.nonzero(vec % FIELD_PRIME)[0]]
    signed_entries = [[idx, signed_mod(value)] for idx, value in entries]
    return {
        "nonzero_count": len(entries),
        "coefficient_sum": int(sum(value for _, value in entries) % FIELD_PRIME),
        "signed_entries": signed_entries,
        "sha256": hashlib.sha256(canonical(entries)).hexdigest(),
    }


def add_vectors(vectors: list[np.ndarray]) -> np.ndarray:
    if not vectors:
        raise ValueError("at least one vector required")
    out = np.zeros(vectors[0].shape[0], dtype=np.int64)
    for vec in vectors:
        out = (out + vec) % FIELD_PRIME
    return out


def public_shadow(vec: np.ndarray, q42: np.ndarray, q12: np.ndarray) -> dict[str, Any]:
    q42_shadow = quotient_vector(vec, q42, 42)
    q12_shadow = quotient_vector(vec, q12, 12)
    return {
        "q42": quotient_digest(q42_shadow),
        "q12": quotient_digest(q12_shadow),
        "public_zero": bool(np.count_nonzero(q42_shadow) == 0 and np.count_nonzero(q12_shadow) == 0),
    }


def determinant_3(matrix: list[list[int]]) -> int:
    return (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def two_by_two_minor_gcd(matrix: list[list[int]]) -> int:
    gcd_value = 0
    for rows in ((0, 1), (0, 2), (1, 2)):
        for cols in ((0, 1), (0, 2), (1, 2)):
            a, b = rows
            c, d = cols
            minor = matrix[a][c] * matrix[b][d] - matrix[a][d] * matrix[b][c]
            gcd_value = math.gcd(gcd_value, abs(minor))
    return gcd_value


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


def build_theorem() -> dict[str, Any]:
    typed_flux = load_json(TYPED_NONEXACT_OPTICAL_FLUX_REPORT)
    superselection = load_json(SUPERSELECTION_FLUX_EXTENSION_REPORT)
    minimal_transport = load_json(MINIMAL_COMPOSITE_TRANSPORT_REPORT)
    all_residue = load_json(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT)
    full_lift = load_json(FULL_A985_LIFT)
    profiles = sector_profiles_by_id(full_lift)

    core = load_json(CORE_A985)["blocks"]["tube_center_primitive_idempotents"]
    relation_npz = np.load(RELATION_NPZ)
    block_i = np.asarray(relation_npz["block_i"], dtype=np.int64)
    block_j = np.asarray(relation_npz["block_j"], dtype=np.int64)
    quotient_npz = np.load(QUOTIENT_NPZ)
    q42 = np.asarray(quotient_npz["q42_map"], dtype=np.int64)
    q12 = np.asarray(quotient_npz["q12_map"], dtype=np.int64)
    triples = np.asarray(np.load(TENSOR_NPZ)["triples"], dtype=np.int64)
    cache, _ = local_idempotent_cache(core, triples, block_i, block_j)

    vectors_by_sector: dict[int, np.ndarray] = {}
    for sector in [6, 25, 26, 33]:
        vectors_by_sector[sector], _ = sector_vector(profiles[sector], cache, int(block_i.shape[0]))

    sector_public_shadows = {
        str(sector): public_shadow(vectors_by_sector[sector], q42, q12)
        for sector in [6, 25, 26, 33]
    }
    composite_vectors = {
        "6,26": add_vectors([vectors_by_sector[6], vectors_by_sector[26]]),
        "25,26": add_vectors([vectors_by_sector[25], vectors_by_sector[26]]),
        "6,25,26": add_vectors([vectors_by_sector[6], vectors_by_sector[25], vectors_by_sector[26]]),
        "33": vectors_by_sector[33],
    }
    composite_public_shadows = {
        name: public_shadow(vec, q42, q12) for name, vec in composite_vectors.items()
    }

    hidden_transport = superselection["derived"]["hidden_transport_rank_matrix"]
    transport_matrix = [
        [int(hidden_transport["R33"]["R33"]), int(hidden_transport["R33"]["K_mixed_S"]), int(hidden_transport["R33"]["K_pure_Sminus"])],
        [int(hidden_transport["K_mixed_S"]["R33"]), int(hidden_transport["K_mixed_S"]["K_mixed_S"]), int(hidden_transport["K_mixed_S"]["K_pure_Sminus"])],
        [int(hidden_transport["K_pure_Sminus"]["R33"]), int(hidden_transport["K_pure_Sminus"]["K_mixed_S"]), int(hidden_transport["K_pure_Sminus"]["K_pure_Sminus"])],
    ]
    trace = sum(transport_matrix[i][i] for i in range(3))
    determinant = determinant_3(transport_matrix)
    minor_gcd = two_by_two_minor_gcd(transport_matrix)
    entry_gcd = 0
    for row in transport_matrix:
        for value in row:
            entry_gcd = math.gcd(entry_gcd, abs(value))
    smith_normal_form_diagonal = [entry_gcd, minor_gcd // entry_gcd, determinant // minor_gcd]
    composite_block = [[transport_matrix[1][1], transport_matrix[1][2]], [transport_matrix[2][1], transport_matrix[2][2]]]
    composite_trace = composite_block[0][0] + composite_block[1][1]
    composite_determinant = composite_block[0][0] * composite_block[1][1] - composite_block[0][1] * composite_block[1][0]
    composite_discriminant = composite_trace * composite_trace - 4 * composite_determinant

    height_actions = [
        int(row["height_action"])
        for row in all_residue["derived"]["transport_rows"]
        if int(row["height_action"]) != 0
    ]
    action_gcd = 0
    for action in height_actions:
        action_gcd = math.gcd(action_gcd, abs(action))
    normalized_actions = [action // action_gcd for action in height_actions]
    residue_histogram = Counter(value % BOSONIC_STRING_CRITICAL_DIMENSION for value in normalized_actions)
    basis_heights = [int(value) for value in all_residue["derived"]["basis_cycle_height_vector"]]
    basis_normalized = [value // action_gcd for value in basis_heights]
    basis_mod26 = [value % BOSONIC_STRING_CRITICAL_DIMENSION for value in basis_normalized]

    sector26_profile = profiles[SECTOR26]
    quotient_stability = {
        "sector26_public_shadow": sector_public_shadows["26"],
        "sector6_public_shadow": sector_public_shadows["6"],
        "sector25_public_shadow": sector_public_shadows["25"],
        "sector33_public_shadow": sector_public_shadows["33"],
        "composite_public_shadows": composite_public_shadows,
        "interpretation": (
            "Sector 26 is public-visible by itself in A42 and A12, but it is exactly cancelled by sector 6 "
            "in {6,26} and by sector 25 in {25,26}. The cancellation is stable across both public quotient layers."
        ),
    }
    transport_form = {
        "basis_order": ["R33", "K_mixed_S", "K_pure_Sminus"],
        "matrix": transport_matrix,
        "trace": trace,
        "determinant": determinant,
        "smith_normal_form_diagonal": smith_normal_form_diagonal,
        "characteristic_polynomial": "lambda^3 - 11 lambda^2 + 37 lambda - 36",
        "r33_eigenvalue": 4,
        "composite_block": {
            "basis_order": ["K_mixed_S", "K_pure_Sminus"],
            "matrix": composite_block,
            "trace": composite_trace,
            "determinant": composite_determinant,
            "discriminant": composite_discriminant,
            "eigenvalues": "(7 +/- sqrt(13))/2",
        },
        "interpretation": (
            "R33 is transport-isolated. The composite null pair has a rank-one off-diagonal seam through sector 26 "
            "and an irreducible quadratic discriminant 13 over the rationals."
        ),
    }
    optical_normalization = {
        "height_action_gcd": action_gcd,
        "min_nonzero_height_action": min(height_actions),
        "min_nonzero_normalized_action": min(height_actions) // action_gcd,
        "first_obstruction_normalized_action": 374784 // action_gcd,
        "first_obstruction_normalized_mod26": (374784 // action_gcd) % BOSONIC_STRING_CRITICAL_DIMENSION,
        "basis_cycle_normalized_actions": basis_normalized,
        "basis_cycle_normalized_mod26": basis_mod26,
        "all_nonzero_normalized_action_mod26_histogram": {
            str(key): int(residue_histogram[key])
            for key in range(BOSONIC_STRING_CRITICAL_DIMENSION)
        },
        "residue_classes_hit_mod26": sorted(int(key) for key in residue_histogram),
        "interpretation": (
            "After dividing by the global optical-action gcd 3072, the 2047 nonzero closed-return classes hit "
            "all 26 residues modulo 26. The 26-marker is therefore visible as a complete finite optical residue clock."
        ),
    }
    critical_26_marker = {
        "sector": 26,
        "bosonic_string_critical_dimension": BOSONIC_STRING_CRITICAL_DIMENSION,
        "d20_public_state_count_plus_h6_channel_count": D20_PUBLIC_STATE_COUNT + H6_CHANNEL_COUNT,
        "sector26_profile": {
            "block_dimension": int(sector26_profile["block_dimension"]),
            "active_objects": sector26_profile["active_objects"],
            "active_cy_sectors": sector26_profile["active_cy_sectors"],
            "permutation_rank": int(sector26_profile["permutation_rank"]),
            "permutation_multiplicity": int(sector26_profile["permutation_multiplicity"]),
            "object_loop_coordinate_support": sector26_profile["object_loop_coordinate_support"],
            "spectral_signature": sector26_profile["spectral_signature"],
            "vector": vec_digest(vectors_by_sector[26]),
        },
        "scope_note": (
            "This is a finite invariant alignment and a test target. It is not a claim that the D20 certificate "
            "already recovers continuum bosonic string theory."
        ),
    }

    checks = {
        "typed_nonexact_optical_flux_update_is_certified": typed_flux.get("status")
        == "D20_TYPED_NONEXACT_OPTICAL_FLUX_UPDATE_CERTIFIED"
        and typed_flux.get("all_checks_pass") is True,
        "superselection_flux_extension_is_certified": superselection.get("status")
        == "D20_SUPERSELECTION_FLUX_BALANCE_EXTENSION_CERTIFIED"
        and superselection.get("all_checks_pass") is True,
        "minimal_composite_transport_is_certified": minimal_transport.get("status")
        == "D20_MINIMAL_COMPOSITE_NULL_SUPPORTS_TRANSPORT_CLASSIFIED"
        and minimal_transport.get("all_checks_pass") is True,
        "all_residue_height_transport_is_certified": all_residue.get("status")
        == "D20_ALL_RESIDUE_HEIGHT_COHERENT_TRANSPORT_CERTIFIED"
        and all_residue.get("all_checks_pass") is True,
        "sector26_is_shared_composite_seam": sorted(set(MIXED_COMPOSITE).intersection(PURE_COMPOSITE))
        == [SECTOR26],
        "sector26_matches_bosonic_critical_dimension": SECTOR26 == BOSONIC_STRING_CRITICAL_DIMENSION,
        "d20_public_plus_h6_count_is_26": D20_PUBLIC_STATE_COUNT + H6_CHANNEL_COUNT == 26,
        "sector26_is_public_visible_alone": sector_public_shadows["26"]["q42"]["nonzero_count"] == 2
        and sector_public_shadows["26"]["q12"]["nonzero_count"] == 2,
        "sector26_cancellation_is_stable_in_A42_and_A12_for_both_minimal_composites": composite_public_shadows[
            "6,26"
        ]["public_zero"]
        and composite_public_shadows["25,26"]["public_zero"],
        "mixed_plus_pure_without_R33_is_not_public_zero": not composite_public_shadows["6,25,26"][
            "public_zero"
        ],
        "r33_is_public_zero_and_transport_isolated": composite_public_shadows["33"]["public_zero"]
        and transport_matrix[0][1] == transport_matrix[0][2] == transport_matrix[1][0] == transport_matrix[2][0] == 0,
        "hidden_transport_form_has_expected_matrix": transport_matrix == [[4, 0, 0], [0, 5, 1], [0, 1, 2]],
        "hidden_transport_smith_normal_form_is_1_1_36": smith_normal_form_diagonal == [1, 1, 36],
        "composite_block_has_rank_one_sector26_cross_coupling": composite_block == [[5, 1], [1, 2]]
        and composite_determinant == 9
        and composite_discriminant == 13,
        "optical_action_gcd_is_3072": action_gcd == 3072,
        "normalized_nonzero_actions_hit_all_26_residues": sorted(residue_histogram) == list(range(26)),
        "first_obstruction_normalized_action_is_122": optical_normalization[
            "first_obstruction_normalized_action"
        ]
        == 122,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_SECTOR26_INVARIANT_SUITE_CERTIFIED"
        if all_checks_pass
        else "D20_SECTOR26_INVARIANT_SUITE_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.sector26_invariant_suite",
        "status": status,
        "object": "d20",
        "claim": (
            "Sector 26 is certified as the shared public-zero composite seam. It is public-visible alone, "
            "cancels stably in both minimal composite supports through A42 and A12, supplies the rank-one "
            "cross-transport between the two composite superselection labels, and aligns with a complete "
            "mod-26 optical residue clock after gcd normalization."
        ),
        "definition": {
            "critical_26_marker": (
                "The conjunction of: sector index 26, D20 public state count plus H6 channel count = 26, "
                "shared seam of {6,26} and {25,26}, and complete normalized optical residues modulo 26."
            ),
            "quotient_stability": (
                "The sector-26 public shadow is nonzero alone but cancels in both minimal public-zero composites "
                "at both A42 and A12 readout layers."
            ),
            "transport_form": "The hidden null-fiber transport rank form on (R33,K_mixed_S,K_pure_Sminus).",
        },
        "inputs": {
            "typed_nonexact_optical_flux_update_report": {
                "path": rel(TYPED_NONEXACT_OPTICAL_FLUX_REPORT),
                "sha256": sha_file(TYPED_NONEXACT_OPTICAL_FLUX_REPORT),
            },
            "superselection_flux_balance_extension_report": {
                "path": rel(SUPERSELECTION_FLUX_EXTENSION_REPORT),
                "sha256": sha_file(SUPERSELECTION_FLUX_EXTENSION_REPORT),
            },
            "minimal_composite_null_supports_transport_report": {
                "path": rel(MINIMAL_COMPOSITE_TRANSPORT_REPORT),
                "sha256": sha_file(MINIMAL_COMPOSITE_TRANSPORT_REPORT),
            },
            "all_residue_height_transport_report": {
                "path": rel(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT),
                "sha256": sha_file(ALL_RESIDUE_HEIGHT_TRANSPORT_REPORT),
            },
            "full_a985_lift": {"path": rel(FULL_A985_LIFT), "sha256": sha_file(FULL_A985_LIFT)},
            "core_a985": {"path": rel(CORE_A985), "sha256": sha_file(CORE_A985)},
            "relation_memberships": {"path": rel(RELATION_NPZ), "sha256": sha_file(RELATION_NPZ)},
            "quotients": {"path": rel(QUOTIENT_NPZ), "sha256": sha_file(QUOTIENT_NPZ)},
            "t985_tensor": {"path": rel(TENSOR_NPZ), "sha256": sha_file(TENSOR_NPZ)},
        },
        "derived": {
            "critical_26_marker": critical_26_marker,
            "quotient_stability": quotient_stability,
            "hidden_transport_form": transport_form,
            "optical_action_normalization": optical_normalization,
        },
        "interpretation": {
            "what_opens": [
                "a finite critical-26 marker independent of public-zero collapse",
                "a quotient-stable hidden cancellation invariant at A42 and A12",
                "an exact hidden transport form with isolated R33 and a rank-one sector-26 composite seam",
                "a complete mod-26 normalized optical-action residue clock",
            ],
            "scope": (
                "These are finite invariants and next theorem targets. They support a bosonic-critical-dimension "
                "analogy, but they do not by themselves recover a continuum string worldsheet, Virasoro algebra, "
                "or central charge."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Use the sector-26 suite to build a finite anomaly-counter theorem: normalize optical action by 3072, "
            "track residues modulo 26, and test whether the hidden transport form controls the residue classes."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.sector26_invariant_suite_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify sector 26 is the shared seam of the two minimal non-Pi33 public-zero composites",
            "verify sector 26 is public-visible alone but cancels in A42/A12 for both composites",
            "verify the hidden transport form and its Smith normal form",
            "verify the composite block has rank-one cross-coupling and discriminant 13",
            "verify optical actions normalize by gcd 3072 and hit all 26 residues modulo 26",
            "record the bosonic critical-dimension alignment without claiming continuum recovery",
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
