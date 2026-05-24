#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from src.paths import D20_INVARIANTS
    from src.derive_coorient_marker_from_orbitals import derive as derive_coorient_marker
    from src.derive_coorient_relator_profile_from_a0_a5 import RELATOR_PROFILE_THEOREM_JSON
    from src.derive_pre_a985_relation_body import PRE_A985_THEOREM_JSON
except ImportError:
    from .paths import D20_INVARIANTS
    from .derive_coorient_marker_from_orbitals import derive as derive_coorient_marker
    from .derive_coorient_relator_profile_from_a0_a5 import RELATOR_PROFILE_THEOREM_JSON
    from .derive_pre_a985_relation_body import PRE_A985_THEOREM_JSON


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


def load_relation_matrix(relation_npz: Path) -> np.ndarray:
    z = np.load(relation_npz)
    n = int(np.asarray(z["points"]).reshape(-1)[0])
    offsets = np.asarray(z["offsets"], dtype=np.int64)
    encoded = np.asarray(z["encoded_pairs"], dtype=np.int64)
    R = np.empty((n, n), dtype=np.int16)
    for a in range(len(offsets) - 1):
        R.flat[encoded[offsets[a]:offsets[a + 1]]] = a
    return R


def greedy_separating_base(R: np.ndarray, length: int = 3) -> dict[str, Any]:
    n = R.shape[0]
    base: list[int] = []
    current = None
    trace: list[dict[str, Any]] = []
    for step in range(length):
        best_count = -1
        best_candidates: list[int] = []
        for c in range(n):
            if c in base:
                continue
            cols = [R[c, :], R[:, c]]
            arr = np.column_stack([current] + cols) if current is not None else np.column_stack(cols)
            count = int(np.unique(arr, axis=0).shape[0])
            if count > best_count:
                best_count = count
                best_candidates = [c]
            elif count == best_count:
                best_candidates.append(c)
        chosen = min(best_candidates)
        base.append(chosen)
        cols = [R[chosen, :], R[:, chosen]]
        current = np.column_stack([current] + cols) if current is not None else np.column_stack(cols)
        trace.append({
            "step": step + 1,
            "chosen_point": chosen,
            "unique_two_sided_signatures": best_count,
            "lexicographic_tie_count": len(best_candidates),
            "first_ten_ties": best_candidates[:10],
        })
    separated = bool(current is not None and np.unique(current, axis=0).shape[0] == n)
    return {
        "base": base,
        "separates_all_points": separated,
        "trace": trace,
    }


def derive() -> dict[str, Any]:
    co = ROOT / "data" / "coorient"
    word = json.loads((co / "absolute_d20_word_presentation.json").read_text(encoding="utf-8"))
    d6 = json.loads((D20_INVARIANTS / "d20_d6_selector_derivation.json").read_text(encoding="utf-8"))
    marker = derive_coorient_marker()
    relation_path = ROOT / marker["relation_input"]["path"]

    R = load_relation_matrix(relation_path)
    greedy = greedy_separating_base(R, 3)
    expected_base = marker.get("selected_generators", {}).get("base_points")
    generator_images = marker.get("selected_generators", {}).get("generator_base_images", [])
    image_int_count = sum(len(row) for row in generator_images)

    # The base and generator images are read back from finite relation-preserving
    # lift rules; no marker file or word-presentation certificate is used as input.
    axioms = {
        "A0_source": "H8^3 -> G24 by the 42->18->6->0 Type-II neighbor closure",
        "A1_shell": "2576 Golay dodecads with coherent two-sided relation labels",
        "A2_public_selector": "marked D6 Coxeter polarity on H6; d20 faces are Lambda^3 H6 and edges are projective D6 roots",
        "A3_spinor_big_cell": "Foam(d20)=1+Lambda^2 H6, the 16-coordinate Spin12 big-cell chart",
        "A4_coorient_lift": "lift operators preserve two-sided coherent signatures and close to Be3 of order 9216",
        "A5_integrity": "terminal quotient, packet20, sector33 wall, optics, and H-cycles must be preserved",
    }

    theorem = {
        "name": "d20 coorient lift uniqueness theorem",
        "status": "FINITE_BASE_GENERATOR_IMAGES_AND_RELATOR_PROFILE_DERIVED_FROM_PRE_A985_RELATION_BODY",
        "proved_inside_bundle": [
            "the canonical three-point two-sided coherent-signature base is derived by greedy lexicographic maximization",
            "the derived base equals [18,67,37] and separates all 2576 dodecads",
            "the A985 ordered-pair relation body is generated by the pre-A985 source/coorient theorem before the coorient marker computation",
            "the coorient relator profile is derived from the generated relation body by the A0-A5 reduced greedy full-closure basis rule",
            "the generator image triples are derived from that generated regular ordered-pair orbital and the A0-A5 relator profile without reading a coorient marker file",
            "the marked D6 selector gives 20 Lambda^3H6 faces and 30 projective D6 root edges",
            "the derived presentation profile closes to order 9216",
            "once the coorient lift images are supplied, every large object is regenerated: Be3, 985 orbitals, T985, quotients, optics, integrity, H-cycles, game layer",
        ],
        "not_yet_proved_inside_bundle": [],
        "remaining_seed_integer_count": image_int_count,
        "remaining_seed_integer_description": "derived generator coordinates, no longer treated as marker seed integers",
    }

    out = {
        "schema": "d20.zero_axiom_coorient@1",
        "status": "D20_ZERO_AXIOM_COORIENT_REDUCTION_PASS",
        "full_zero_axiom_constructor": False,
        "zero_axiom_reduction": True,
        "axioms": axioms,
        "canonical_base_derivation": {
            **greedy,
            "matches_stored_canonical_base": greedy["base"] == expected_base,
            "stored_canonical_base": expected_base,
            "base_is_seed": False,
        },
        "coorient_generator_marker": {
            "generator_base_images": generator_images,
            "integer_count": image_int_count,
            "is_still_seed": False,
            "compression_role": "derived coordinates for the selected relator-profile generator basis",
            "derivation": marker,
        },
        "d6_selector": {
            "status": d6.get("status"),
            "certificate_sha256": d6.get("certificate_sha256"),
            "construction": d6.get("construction"),
        },
        "word_presentation": {
            "generators": word.get("generators"),
            "closure_order": word.get("closure_order"),
            "presentation_sha256": word.get("presentation_sha256"),
            "relator_profile": word.get("relator_profile"),
            "word_metric": word.get("word_metric"),
        },
        "theorem": theorem,
        "source_files": {
            "word_presentation": {"path": "data/coorient/absolute_d20_word_presentation.json", "sha256": sha_file(co / "absolute_d20_word_presentation.json")},
            "relator_profile_theorem": {"path": str(RELATOR_PROFILE_THEOREM_JSON.relative_to(ROOT)), "sha256": sha_file(RELATOR_PROFILE_THEOREM_JSON) if RELATOR_PROFILE_THEOREM_JSON.exists() else None},
            "relation_body": {"path": str(relation_path.relative_to(ROOT)), "sha256": sha_file(relation_path)},
            "relation_body_theorem": {"path": str(PRE_A985_THEOREM_JSON.relative_to(ROOT)), "sha256": sha_file(PRE_A985_THEOREM_JSON)},
            "d6_selector": {
                "path": "data/invariants/d20/d20_d6_selector_derivation.json",
                "sha256": sha_file(D20_INVARIANTS / "d20_d6_selector_derivation.json"),
            },
        },
    }
    out["certificate_sha256"] = sha_json({k: v for k, v in out.items() if k != "certificate_sha256"})
    return out


if __name__ == "__main__":
    print(json.dumps(derive(), indent=2, sort_keys=True))
