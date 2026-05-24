from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_d20_sandpile_critical_group_theorem import rel, sha_file, sha_json
    from .derive_sector33_boundary_annihilation_theorem import FIELD_PRIME, H6_LABELS, signed_mod
    from .derive_sector33_unique_public_zero_support_theorem import local_idempotent_cache
    from .paths import D20_INVARIANTS, LAYERS, ROOT
except ImportError:  # Supports `python src/derive_d20_fourier_screen0_tube_central_element.py`.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.derive_d20_sandpile_critical_group_theorem import rel, sha_file, sha_json
    from src.derive_sector33_boundary_annihilation_theorem import FIELD_PRIME, H6_LABELS, signed_mod
    from src.derive_sector33_unique_public_zero_support_theorem import local_idempotent_cache
    from src.paths import D20_INVARIANTS, LAYERS, ROOT


THEOREM_ID = "fourier_screen0_tube_central_element"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FOURIER_A985_REPORT = (
    D20_INVARIANTS / "theorems" / "fourier_a985_sector_character_candidates" / "report.json"
)
SECTOR_UNIQUE_REPORT = (
    D20_INVARIANTS / "theorems" / "sector33_unique_public_zero_support" / "report.json"
)
FULL_A985_LIFT = LAYERS / "drinfeld" / "full_a985_lift.json"
CORE_A985 = LAYERS / "core" / "a985.json"
RELATION_NPZ = ROOT / "data" / "raw" / "relation_memberships.npz"
TENSOR_NPZ = ROOT / "data" / "raw" / "T_985.npz"


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


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
        schema = index.get("schema", "d20.theorem_registry")
        theorems = [item for item in index.get("theorems", []) if item.get("id") != THEOREM_ID]
    else:
        schema = "d20.theorem_registry"
        theorems = []
    theorems.append(entry)
    theorems = sorted(theorems, key=lambda item: item["id"])
    index = {
        "schema": schema,
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": len(theorems),
        "theorems": theorems,
    }
    index["registry_sha256"] = sha_json({k: v for k, v in index.items() if k != "registry_sha256"})
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def vec_entries(vec: np.ndarray) -> list[list[int]]:
    return [[int(idx), int(vec[idx]) % FIELD_PRIME] for idx in np.nonzero(vec % FIELD_PRIME)[0]]


def vec_digest(vec: np.ndarray, include_entries: bool = False) -> dict[str, Any]:
    entries = vec_entries(vec)
    values = [int(value) for _, value in entries]
    signed_values = [signed_mod(value) for value in values]
    digest = {
        "support": len(entries),
        "coefficient_sum": int(sum(values) % FIELD_PRIME),
        "coefficient_sum_signed": signed_mod(int(sum(values))),
        "coefficient_abs_sum_signed_lift": int(sum(abs(value) for value in signed_values)),
        "sha256": hashlib.sha256(canonical(entries)).hexdigest(),
    }
    if include_entries:
        digest["entries"] = entries
        digest["signed_entries"] = [[idx, signed_mod(value)] for idx, value in entries]
    return digest


def pair_products_for_identity_terms(
    triples: np.ndarray,
    identity_relations: list[int],
) -> dict[tuple[int, int], list[tuple[int, int]]]:
    identity_set = set(identity_relations)
    out: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for alpha, beta, gamma, coeff in triples.tolist():
        if int(alpha) in identity_set or int(beta) in identity_set:
            out.setdefault((int(alpha), int(beta)), []).append((int(gamma), int(coeff) % FIELD_PRIME))
    return out


def product_from_terms(
    left_terms: list[tuple[int, int]],
    right_terms: list[tuple[int, int]],
    pair_products: dict[tuple[int, int], list[tuple[int, int]]],
    relation_count: int,
) -> np.ndarray:
    out = np.zeros(relation_count, dtype=np.int64)
    for alpha, left_coeff in left_terms:
        for beta, right_coeff in right_terms:
            scalar = (int(left_coeff) * int(right_coeff)) % FIELD_PRIME
            if scalar == 0:
                continue
            for gamma, coeff in pair_products.get((int(alpha), int(beta)), []):
                out[int(gamma)] = (int(out[int(gamma)]) + scalar * int(coeff)) % FIELD_PRIME
    return out % FIELD_PRIME


def first_commutator_failures(
    basis_ids: list[int],
    screen_terms: list[tuple[int, int]],
    pair_products: dict[tuple[int, int], list[tuple[int, int]]],
    relation_count: int,
    limit: int = 16,
) -> tuple[int, list[dict[str, Any]]]:
    failures = []
    count = 0
    for relation in basis_ids:
        basis = [(int(relation), 1)]
        left = product_from_terms(screen_terms, basis, pair_products, relation_count)
        right = product_from_terms(basis, screen_terms, pair_products, relation_count)
        diff = (left - right) % FIELD_PRIME
        if np.any(diff):
            count += 1
            if len(failures) < limit:
                failures.append(
                    {
                        "relation": int(relation),
                        "left_action": vec_digest(left, include_entries=True),
                        "right_action": vec_digest(right, include_entries=True),
                        "commutator": vec_digest(diff, include_entries=True),
                    }
                )
    return count, failures


def signed_identity_vector(identity_relations: list[int], phases_by_object: dict[str, int], relation_count: int) -> np.ndarray:
    vec = np.zeros(relation_count, dtype=np.int64)
    for obj, relation in enumerate(identity_relations):
        phase = phases_by_object[H6_LABELS[obj]]
        vec[int(relation)] = phase % FIELD_PRIME
    return vec % FIELD_PRIME


def reconstruct_from_local_primitive_pieces(
    cache: dict[tuple[int, int], np.ndarray],
    local_summaries: dict[int, dict[str, Any]],
    phases_by_object: dict[str, int],
    relation_count: int,
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    vec = np.zeros(relation_count, dtype=np.int64)
    pieces = []
    for obj in range(len(H6_LABELS)):
        label = H6_LABELS[obj]
        phase = int(phases_by_object[label])
        primitive_count = int(local_summaries[obj]["primitive_idempotent_count"])
        for local in range(primitive_count):
            piece = cache[(obj, local)]
            vec = (vec + (phase % FIELD_PRIME) * piece) % FIELD_PRIME
            pieces.append(
                {
                    "object": obj,
                    "label": label,
                    "local_pre_idempotent": local,
                    "phase": phase,
                    "piece_sha256": vec_digest(piece)["sha256"],
                }
            )
    return vec % FIELD_PRIME, pieces


def build_theorem() -> dict[str, Any]:
    fourier_a985 = load_json(FOURIER_A985_REPORT)
    sector_unique = load_json(SECTOR_UNIQUE_REPORT)
    full = load_json(FULL_A985_LIFT)
    core = load_json(CORE_A985)["blocks"]["tube_center_primitive_idempotents"]

    relation_npz = np.load(RELATION_NPZ)
    block_i = np.asarray(relation_npz["block_i"], dtype=np.int64)
    block_j = np.asarray(relation_npz["block_j"], dtype=np.int64)
    triples = np.asarray(np.load(TENSOR_NPZ)["triples"], dtype=np.int64)
    relation_count = int(block_i.shape[0])
    identity_relations = [
        int(value) for value in full["full_A985_idempotent_validation"]["identity_relations_by_object"]
    ]
    closed_loop_basis_ids = [int(value) for value in np.where(block_i == block_j)[0].tolist()]
    full_basis_ids = list(range(relation_count))

    screen0 = next(
        row
        for row in fourier_a985["derived"]["candidates"]
        if row["screen_id"] == "signed_turn_screen_0"
    )
    phases_by_object = {label: int(screen0["object_phase_assignment"][label]) for label in H6_LABELS}
    cache, local_summaries = local_idempotent_cache(core, triples, block_i, block_j)
    reconstructed, primitive_pieces = reconstruct_from_local_primitive_pieces(
        cache,
        local_summaries,
        phases_by_object,
        relation_count,
    )
    signed_unit = signed_identity_vector(identity_relations, phases_by_object, relation_count)
    closed_loop_unit = signed_identity_vector(
        identity_relations,
        {label: 1 for label in H6_LABELS},
        relation_count,
    )
    screen_terms = [
        (int(identity_relations[obj]), int(phases_by_object[H6_LABELS[obj]]) % FIELD_PRIME)
        for obj in range(len(H6_LABELS))
    ]
    pair_products = pair_products_for_identity_terms(triples, identity_relations)
    screen_square = product_from_terms(screen_terms, screen_terms, pair_products, relation_count)
    closed_failures, closed_failure_examples = first_commutator_failures(
        closed_loop_basis_ids,
        screen_terms,
        pair_products,
        relation_count,
    )
    full_failures, full_failure_examples = first_commutator_failures(
        full_basis_ids,
        screen_terms,
        pair_products,
        relation_count,
    )
    phase_mismatch_relations = [
        int(relation)
        for relation in range(relation_count)
        if phases_by_object[H6_LABELS[int(block_i[relation])]]
        != phases_by_object[H6_LABELS[int(block_j[relation])]]
    ]
    public_zero_supports = [
        row
        for row in screen0["public_zero_support_evaluations"]
        if row["public_zero"] and int(row["sector_count"]) > 0
    ]

    checks = {
        "fourier_a985_candidate_report_is_certified": fourier_a985.get("status")
        == "D20_FOURIER_A985_SECTOR_CHARACTER_CANDIDATES_EVALUATED"
        and fourier_a985.get("all_checks_pass") is True,
        "sector33_unique_public_zero_support_is_certified": sector_unique.get("status")
        == "D20_SECTOR33_UNIQUE_PUBLIC_ZERO_SUPPORT_CERTIFIED"
        and sector_unique.get("all_checks_pass") is True,
        "selected_screen_is_public_zero_compatible": screen0.get("all_nonzero_public_zero_supports_scalar") is True,
        "local_primitive_piece_count_is_109": len(primitive_pieces) == 109,
        "closed_loop_basis_count_is_297": len(closed_loop_basis_ids) == 297,
        "reconstructed_equals_signed_object_unit": bool(np.array_equal(reconstructed, signed_unit)),
        "screen_vector_support_is_six_identity_relations": vec_digest(reconstructed)["support"] == 6,
        "screen_square_is_closed_loop_unit": bool(np.array_equal(screen_square, closed_loop_unit)),
        "commutes_with_all_closed_loop_basis_relations": closed_failures == 0,
        "full_a985_commutator_failure_count_matches_phase_mismatch_relations": full_failures
        == len(phase_mismatch_relations),
        "not_full_a985_central": full_failures > 0,
        "all_nonzero_public_zero_supports_have_scalar_plus_one": all(
            row["scalar_on_support"] and int(row["support_scalar"]) == 1
            for row in public_zero_supports
        ),
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FOURIER_SCREEN0_TUBE_CENTRAL_ELEMENT_CERTIFIED"
        if all_checks_pass
        else "D20_FOURIER_SCREEN0_TUBE_CENTRAL_ELEMENT_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.fourier_screen0_tube_central_element",
        "status": status,
        "object": "d20",
        "claim": (
            "The first signed-turn Fourier residue screen materializes as a closed-loop tube "
            "central involution: summing its phases over all 109 local primitive idempotent "
            "pieces collapses to the signed object-unit vector -1_B- + 1_B+ -1_V- + "
            "1_V+ + 1_S- + 1_S+. It squares to the closed-loop unit and commutes with "
            "all 297 closed-loop basis relations, but it is not central in the full 985-relation algebra."
        ),
        "definition": {
            "closed_loop_tube_element": (
                "A vector supported on the diagonal relation blocks i->i, tested against the "
                "297-dimensional closed-loop multiplication inherited from T_985."
            ),
            "screen0_signed_object_unit": (
                "Use signed_turn_screen_0 phases B-=-1, B+=+1, V-=-1, V+=+1, S-=+1, S+=+1 "
                "on the six categorical identity relations."
            ),
            "scope_boundary": (
                "This is a closed-loop tube central element. The certificate also checks that it is "
                "not central on the full A985 relation algebra, because off-diagonal relations between "
                "oppositely phased objects have nonzero commutator."
            ),
        },
        "inputs": {
            "fourier_a985_sector_character_candidates_report": {
                "path": rel(FOURIER_A985_REPORT),
                "sha256": sha_file(FOURIER_A985_REPORT),
            },
            "sector33_unique_public_zero_support_report": {
                "path": rel(SECTOR_UNIQUE_REPORT),
                "sha256": sha_file(SECTOR_UNIQUE_REPORT),
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
            "t985_tensor": {
                "path": rel(TENSOR_NPZ),
                "sha256": sha_file(TENSOR_NPZ),
            },
        },
        "derived": {
            "field_prime": FIELD_PRIME,
            "screen_id": "signed_turn_screen_0",
            "object_phase_assignment": phases_by_object,
            "identity_relations_by_object": identity_relations,
            "closed_loop_basis_count": len(closed_loop_basis_ids),
            "full_relation_count": relation_count,
            "local_primitive_piece_count": len(primitive_pieces),
            "primitive_piece_phase_counts": {
                "+1": sum(1 for row in primitive_pieces if int(row["phase"]) == 1),
                "-1": sum(1 for row in primitive_pieces if int(row["phase"]) == -1),
            },
            "primitive_piece_rows_sha256": hashlib.sha256(canonical(primitive_pieces)).hexdigest(),
            "signed_object_unit": vec_digest(signed_unit, include_entries=True),
            "reconstructed_from_local_primitives": vec_digest(reconstructed, include_entries=True),
            "closed_loop_unit": vec_digest(closed_loop_unit, include_entries=True),
            "screen_square": vec_digest(screen_square, include_entries=True),
            "closed_loop_commutator": {
                "basis_relations_checked": len(closed_loop_basis_ids),
                "failure_count": closed_failures,
                "failures_first_16": closed_failure_examples,
            },
            "full_a985_commutator_boundary": {
                "basis_relations_checked": relation_count,
                "failure_count": full_failures,
                "phase_mismatch_relation_count": len(phase_mismatch_relations),
                "phase_mismatch_relations_first_32": phase_mismatch_relations[:32],
                "failures_first_16": full_failure_examples,
            },
            "public_zero_support_action": [
                {
                    "sector_support": row["sector_support"],
                    "support_scalar": row["support_scalar"],
                    "regular_trace": row["regular_trace"],
                    "dimension_sum": row["dimension_sum"],
                }
                for row in public_zero_supports
            ],
        },
        "interpretation": {
            "what_is_certified": (
                "The surviving screen is now an explicit closed-loop tube central involution, "
                "not merely a residue-mask character candidate."
            ),
            "what_this_does_not_prove": (
                "It is not a full A985 central element, and it does not yet map closed-return masks "
                "to sandpile divisor classes."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Use this closed-loop central involution to grade the 2048 residue masks by tube action, "
            "then compare that grading with the sandpile critical group through an explicit divisor map."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.fourier_screen0_tube_central_element_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify screen 0 is the public-zero-compatible Fourier/A985 candidate",
            "reconstruct the signed element from all 109 local primitive idempotent pieces",
            "verify the reconstructed element equals the signed object-unit vector",
            "verify the element squares to the closed-loop unit",
            "verify commutation against all 297 closed-loop basis relations",
            "verify the element is not central in the full 985-relation algebra",
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
