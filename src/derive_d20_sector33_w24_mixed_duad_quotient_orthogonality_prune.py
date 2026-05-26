from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from .derive_d20_golay_hamming_minor_puncture_search import mod2_matrix
    from .derive_d20_oriented_matroid_contour import edge_table
    from .derive_d20_oriented_matroid_sector33_dual import (
        build_sector33_height_attachment_matrix,
    )
    from .derive_d20_sector33_w24_marked_big_cell_quotient_search import (
        marked_big_cell_profile,
        selector_duad_profile,
    )
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_d20_golay_hamming_minor_puncture_search import mod2_matrix
    from derive_d20_oriented_matroid_contour import edge_table
    from derive_d20_oriented_matroid_sector33_dual import (
        build_sector33_height_attachment_matrix,
    )
    from derive_d20_sector33_w24_marked_big_cell_quotient_search import (
        marked_big_cell_profile,
        selector_duad_profile,
    )
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_sector33_w24_mixed_duad_quotient_orthogonality_prune"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
ARTIFACT_PATH = GENERATED / "d20_sector33_w24_mixed_duad_quotient_orthogonality_prune.json"

D20_JSON = ROOT / "d20.json"
W24_ROW_ALPHABETIZATION = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_w24_hexacode_row_alphabetization"
    / "report.json"
)
MARKED_BIG_CELL_QUOTIENT_SEARCH = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_sector33_w24_marked_big_cell_quotient_search"
    / "report.json"
)
SECTOR33_DUAL_REPORT = (
    D20_INVARIANTS / "theorems" / "d20_oriented_matroid_sector33_dual" / "report.json"
)
WU_SPINH_6J_MARKING = ROOT / "data" / "selectors" / "wu_spinh_6j_marking.json"
DERIVE_SCRIPT = ROOT / "src" / "derive_d20_sector33_w24_mixed_duad_quotient_orthogonality_prune.py"
VALIDATOR = ROOT / "src" / "certify_d20_sector33_w24_mixed_duad_quotient_orthogonality_prune.py"

CHOICE_NAMES = ("first_edge_selector", "second_edge_selector", "duplicate_xor_collapse")
LEFT_DUAD_COUNT = 7


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


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} is not a JSON object")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def input_entry(path: Path, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    entry = {"path": relpath(path), "sha256": sha_file(path)}
    if extra:
        entry.update(extra)
    return entry


def artifact_hash(payload: dict[str, Any]) -> str:
    tmp = dict(payload)
    tmp.pop("artifact_sha256_excluding_this_field", None)
    return sha_json(tmp)


def column_masks(matrix: list[list[int]]) -> list[int]:
    masks: list[int] = []
    for col in range(len(matrix[0])):
        mask = 0
        for row_idx, row in enumerate(matrix):
            if row[col]:
                mask |= 1 << row_idx
        masks.append(mask)
    return masks


def upper_triangle_pairs(row_count: int) -> list[tuple[int, int]]:
    return [(i, j) for i in range(row_count) for j in range(i, row_count)]


def gram_column(mask: int, row_count: int, pair_index: dict[tuple[int, int], int]) -> int:
    bits = [idx for idx in range(row_count) if (mask >> idx) & 1]
    gram = 0
    for left_pos, left in enumerate(bits):
        for right in bits[left_pos:]:
            gram ^= 1 << pair_index[(left, right)]
    return gram


def counter_digest(counter: Counter[int]) -> str:
    return sha_json([[format(key, "x"), value] for key, value in sorted(counter.items())])


def enumerate_gram_states(
    gram_options: list[tuple[int, int, int]],
    start: int,
    count: int,
) -> Counter[int]:
    states: Counter[int] = Counter()
    for choices in itertools.product(range(len(CHOICE_NAMES)), repeat=count):
        gram = 0
        for offset, choice in enumerate(choices):
            gram ^= gram_options[start + offset][choice]
        states[gram] += 1
    return states


def mixed_orthogonality_search(rows: list[dict[str, Any]]) -> dict[str, Any]:
    primal_integer_matrix, attachment = build_sector33_height_attachment_matrix()
    primal_mod2 = mod2_matrix(primal_integer_matrix)
    row_count = len(primal_mod2)
    selector_profile = selector_duad_profile(rows)
    selector_duads = selector_profile["selector_duads"]
    masks = column_masks(primal_mod2)
    pairs = upper_triangle_pairs(row_count)
    pair_index = {pair: idx for idx, pair in enumerate(pairs)}

    column_options: list[dict[str, Any]] = []
    gram_options: list[tuple[int, int, int]] = []
    for record in selector_duads:
        first, second = record["edge_ids"]
        option_masks = (masks[first], masks[second], masks[first] ^ masks[second])
        gram_options.append(
            tuple(gram_column(mask, row_count, pair_index) for mask in option_masks)
        )
        column_options.append(
            {
                "selector_duad_index": record["selector_duad_index"],
                "selector_duad": record["selector_duad"],
                "pair": record["pair"],
                "source_edge_ids": record["edge_ids"],
                "choice_names": list(CHOICE_NAMES),
                "choice_column_masks_hex": [format(mask, "x") for mask in option_masks],
            }
        )

    right_duad_count = len(selector_duads) - LEFT_DUAD_COUNT
    left_states = enumerate_gram_states(gram_options, 0, LEFT_DUAD_COUNT)
    right_states = enumerate_gram_states(gram_options, LEFT_DUAD_COUNT, right_duad_count)
    scalar_gram = gram_column(masks[30], row_count, pair_index)
    self_orthogonal_assignment_count = sum(
        left_count * right_states.get(scalar_gram ^ left_gram, 0)
        for left_gram, left_count in left_states.items()
    )
    assignment_count = len(CHOICE_NAMES) ** len(selector_duads)

    return {
        "source_matrix": "sector33_primal_mod2",
        "source_shape": {"rows": row_count, "cols": len(primal_mod2[0])},
        "sector33_attachment": attachment,
        "d20_selector_duad_profile": selector_profile,
        "choice_family": {
            "choice_names": list(CHOICE_NAMES),
            "choice_count_per_duad": len(CHOICE_NAMES),
            "duad_count": len(selector_duads),
            "assignment_count": assignment_count,
            "column_options": column_options,
            "scalar_source_element_id": 30,
            "scalar_column_mask_hex": format(masks[30], "x"),
        },
        "gram_encoding": {
            "row_count": row_count,
            "upper_triangle_coordinate_count": len(pairs),
            "self_orthogonality_condition": (
                "Q Q^T = 0 over F2, encoded by the upper triangle including diagonal"
            ),
            "scalar_gram_hex": format(scalar_gram, "x"),
            "scalar_gram_bit_count": scalar_gram.bit_count(),
        },
        "meet_in_middle": {
            "left_duad_count": LEFT_DUAD_COUNT,
            "right_duad_count": right_duad_count,
            "left_assignment_count": len(CHOICE_NAMES) ** LEFT_DUAD_COUNT,
            "right_assignment_count": len(CHOICE_NAMES) ** right_duad_count,
            "left_gram_state_count": len(left_states),
            "right_gram_state_count": len(right_states),
            "left_max_state_multiplicity": max(left_states.values()) if left_states else 0,
            "right_max_state_multiplicity": max(right_states.values()) if right_states else 0,
            "left_gram_state_counter_sha256": counter_digest(left_states),
            "right_gram_state_counter_sha256": counter_digest(right_states),
            "matching_state_pair_count": sum(
                1 for left_gram in left_states if (scalar_gram ^ left_gram) in right_states
            ),
            "self_orthogonal_assignment_count": self_orthogonal_assignment_count,
        },
        "candidate_gate": {
            "orthogonality_precondition": "candidate must have self-orthogonal binary rowspace",
            "rank_precondition": "candidate would then need rank 12 before W24 basis comparison",
            "rank12_count_computed": False,
            "rank12_count_not_needed_reason": (
                "self-orthogonality is necessary for Type-II/Golay comparison and no mixed "
                "assignment passes it"
            ),
            "assignment_count_pruned_by_orthogonality": assignment_count
            if self_orthogonal_assignment_count == 0
            else assignment_count - self_orthogonal_assignment_count,
            "basis_compare_attempted": False,
        },
    }


def build_artifact() -> dict[str, Any]:
    d20 = load_json(D20_JSON)
    w24 = load_json(W24_ROW_ALPHABETIZATION)
    marked = load_json(MARKED_BIG_CELL_QUOTIENT_SEARCH)
    dual = load_json(SECTOR33_DUAL_REPORT)
    marking = load_json(WU_SPINH_6J_MARKING)

    rows = edge_table(d20)
    target_golay = w24["witness"]["golay_code"]
    search = mixed_orthogonality_search(rows)
    big_cell = marked_big_cell_profile(
        marking, search["d20_selector_duad_profile"]["selector_duads"]
    )
    mitm = search["meet_in_middle"]
    family = search["choice_family"]

    checks = {
        "d20_input_is_certified": d20.get("status") == "D20_CERTIFIED",
        "w24_row_alphabetization_is_certified": w24["status"]
        == "D20_W24_HEXACODE_ROW_ALPHABETIZATION_CERTIFIED"
        and w24["all_checks_pass"] is True,
        "marked_big_cell_quotient_input_is_certified": marked["status"]
        == "D20_SECTOR33_W24_MARKED_BIG_CELL_QUOTIENT_SEARCH_CERTIFIED"
        and marked["all_checks_pass"] is True,
        "sector33_dual_input_is_certified": dual["status"]
        == "D20_ORIENTED_MATROID_SECTOR33_DUAL_CERTIFIED"
        and dual["all_checks_pass"] is True,
        "wu_marking_is_certified_external_boundary": marking["status"]
        == "WU_SPINH_OCTAD_SPIN12_6J_MARKING_CERTIFIED_GOLAY_SELECTOR_STILL_EXTERNAL"
        and marking["selector_status"]["golay_selector_constructed"] is False,
        "source_matrix_shape_is_21_by_31": search["source_shape"] == {"rows": 21, "cols": 31},
        "d20_selector_duad_profile_has_15_pairs": search["d20_selector_duad_profile"][
            "selector_duad_count"
        ]
        == 15,
        "d20_selector_duads_have_two_edges_each": search["d20_selector_duad_profile"][
            "all_selector_duads_have_two_edges"
        ],
        "big_cell_pair_order_matches_d20_selector_duad_index": big_cell[
            "pair_order_matches_d20_selector_duad_index"
        ],
        "choice_family_size_is_3_to_15": family["choice_count_per_duad"] == 3
        and family["duad_count"] == 15
        and family["assignment_count"] == 14348907,
        "gram_upper_triangle_has_231_coordinates": search["gram_encoding"][
            "upper_triangle_coordinate_count"
        ]
        == 231,
        "meet_in_middle_split_is_7_and_8": mitm["left_duad_count"] == 7
        and mitm["right_duad_count"] == 8,
        "left_assignment_count_is_3_to_7": mitm["left_assignment_count"] == 2187,
        "right_assignment_count_is_3_to_8": mitm["right_assignment_count"] == 6561,
        "left_gram_states_are_collision_free": mitm["left_gram_state_count"] == 2187
        and mitm["left_max_state_multiplicity"] == 1,
        "right_gram_states_are_collision_free": mitm["right_gram_state_count"] == 6561
        and mitm["right_max_state_multiplicity"] == 1,
        "no_matching_gram_state_pairs": mitm["matching_state_pair_count"] == 0,
        "no_mixed_assignment_is_self_orthogonal": mitm["self_orthogonal_assignment_count"] == 0,
        "all_mixed_assignments_pruned_by_orthogonality": search["candidate_gate"][
            "assignment_count_pruned_by_orthogonality"
        ]
        == 14348907,
        "rank12_count_not_needed_after_orthogonality_prune": search["candidate_gate"][
            "rank12_count_computed"
        ]
        is False
        and mitm["self_orthogonal_assignment_count"] == 0,
        "explicit_morphism_remains_open": True,
    }

    payload: dict[str, Any] = {
        "schema": "d20.proof_obligation.sector33_w24_mixed_duad_quotient_orthogonality_prune.artifact@1",
        "status": "D20_SECTOR33_W24_MIXED_DUAD_QUOTIENT_ORTHOGONALITY_PRUNE_DERIVED",
        "claim_scope": (
            "Close the finite mixed local-duad quotient family where each of the 15 H6 duads "
            "independently chooses first edge, second edge, or duplicate xor collapse."
        ),
        "source_reports": {
            "d20_json": input_entry(D20_JSON, {"status": d20.get("status")}),
            "w24_row_alphabetization": input_entry(
                W24_ROW_ALPHABETIZATION,
                {
                    "certificate_sha256": w24["certificate_sha256"],
                    "status": w24["status"],
                },
            ),
            "marked_big_cell_quotient_search": input_entry(
                MARKED_BIG_CELL_QUOTIENT_SEARCH,
                {
                    "certificate_sha256": marked["certificate_sha256"],
                    "status": marked["status"],
                },
            ),
            "sector33_dual": input_entry(
                SECTOR33_DUAL_REPORT,
                {
                    "certificate_sha256": dual["certificate_sha256"],
                    "status": dual["status"],
                },
            ),
            "wu_spinh_6j_marking": input_entry(
                WU_SPINH_6J_MARKING,
                {
                    "status": marking["status"],
                    "recorded_selector_status": marking["selector_status"][
                        "golay_selector_status"
                    ],
                },
            ),
        },
        "target_golay_profile": {
            "length": target_golay["length"],
            "rank": target_golay["rank"],
            "weight_histogram": target_golay["weight_histogram"],
            "generator_basis_masks_sha256": sha_json(target_golay["generator_basis_masks"]),
        },
        "marked_big_cell_profile": big_cell,
        "mixed_orthogonality_search": search,
        "checks": checks,
    }
    payload["artifact_sha256_excluding_this_field"] = artifact_hash(payload)
    return payload


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    search = artifact["mixed_orthogonality_search"]
    family = search["choice_family"]
    mitm = search["meet_in_middle"]
    report: dict[str, Any] = {
        "schema": "d20.proof_obligation.sector33_w24_mixed_duad_quotient_orthogonality_prune@1",
        "status": "D20_SECTOR33_W24_MIXED_DUAD_QUOTIENT_ORTHOGONALITY_PRUNE_CERTIFIED",
        "all_checks_pass": all(artifact["checks"].values()),
        "claim": (
            "The full mixed local-duad quotient family has no self-orthogonal candidate. "
            "Across 3^15 = 14,348,907 assignments, the split Gram search finds zero "
            "solutions to Q Q^T = 0, so every mixed first/second/xor duad quotient is "
            "pruned before rank-12 Golay basis comparison."
        ),
        "definition": {
            "mixed_duad_family": (
                "each of the 15 Lambda^2 H6 selector duads independently chooses the lower "
                "edge, upper edge, or xor of both duplicate sector33 edge columns; e33 is "
                "kept as the scalar coordinate"
            ),
            "orthogonality_test": search["gram_encoding"]["self_orthogonality_condition"],
            "meet_in_middle": {
                "left_duad_count": mitm["left_duad_count"],
                "right_duad_count": mitm["right_duad_count"],
                "left_assignment_count": mitm["left_assignment_count"],
                "right_assignment_count": mitm["right_assignment_count"],
                "self_orthogonal_assignment_count": mitm["self_orthogonal_assignment_count"],
            },
        },
        "closure_boundary": {
            "certifies": [
                f"{family['assignment_count']} mixed local-duad quotient assignments were covered",
                "the Gram upper-triangle encoding has 231 coordinates for the 21 source rows",
                "the 7+8 meet-in-middle split has no matching Gram state pairs",
                "no mixed local-duad quotient assignment is self-orthogonal",
                "therefore no mixed local-duad quotient assignment reaches Type-II/Golay comparison",
            ],
            "does_not_certify": [
                "absence of a morphism using a general 30-to-16 linear quotient",
                "absence of a morphism using coordinates outside the local first/second/xor duad rules",
                "absence of a morphism using the Wu octad together with the Spin12 complement",
                "an intrinsic Golay selector independent of external Wu/hexacode marking data",
                "a rebuild of d20.json or any finite critical group artifact",
            ],
        },
        "inputs": {
            "artifact": input_entry(
                ARTIFACT_PATH,
                {
                    "artifact_sha256_excluding_this_field": artifact[
                        "artifact_sha256_excluding_this_field"
                    ],
                    "schema": artifact["schema"],
                    "status": artifact["status"],
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR),
            **artifact["source_reports"],
        },
        "witness": {
            "target_golay_profile": artifact["target_golay_profile"],
            "marked_big_cell_profile": artifact["marked_big_cell_profile"],
            "mixed_orthogonality_search": search,
        },
        "checks": artifact["checks"],
        "next_highest_yield_item": (
            "Move beyond local-duad selectors and solve the general F2 linear quotient "
            "constraints for a 30-to-16 Spin12 map, with Q Q^T = 0 and rank 12 as hard gates."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": "d20.proof_obligation.sector33_w24_mixed_duad_quotient_orthogonality_prune_manifest@1",
        "name": THEOREM_ID,
        "certification_tests": [
            "verify D20, W24 row-alphabetization, marked-big-cell quotient, sector33 dual, and Wu/Spin12 inputs",
            "verify the mixed choice family has 3 choices on each of 15 selector duads",
            "encode self-orthogonality as the upper triangle of Q Q^T over F2",
            "enumerate the left 3^7 Gram states",
            "enumerate the right 3^8 Gram states",
            "verify no split Gram state pair cancels the scalar contribution",
            "verify zero mixed assignments are self-orthogonal",
            "record rank comparison as blocked by the orthogonality prune",
        ],
        "inputs": report["inputs"],
        "outputs": {
            "artifact": relpath(ARTIFACT_PATH),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "report_sha256": report["certificate_sha256"],
        "artifact_sha256_excluding_hash_field": artifact["artifact_sha256_excluding_this_field"],
    }
    manifest["manifest_sha256"] = sha_json(manifest)
    return manifest


def update_index(report: dict[str, Any]) -> None:
    if INDEX_PATH.exists():
        index = load_json(INDEX_PATH)
        obligations = [row for row in index.get("obligations", []) if row.get("id") != THEOREM_ID]
        schema = index.get("schema", "d20.proof_obligation_registry.source_drop")
    else:
        obligations = []
        schema = "d20.proof_obligation_registry.source_drop"
    obligations.append(
        {
            "id": THEOREM_ID,
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
            "report_sha256": report["certificate_sha256"],
            "status": report["status"],
        }
    )
    index = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": sorted(obligations, key=lambda row: row["id"]),
    }
    index["registry_sha256"] = sha_json(index)
    write_json(INDEX_PATH, index)


def main() -> None:
    artifact = build_artifact()
    write_json(ARTIFACT_PATH, artifact)
    report = build_report(artifact)
    manifest = build_manifest(report, artifact)
    write_json(OUT_DIR / "report.json", report)
    write_json(OUT_DIR / "manifest.json", manifest)
    update_index(report)
    print(
        json.dumps(
            {
                "artifact": relpath(ARTIFACT_PATH),
                "assignment_count": artifact["mixed_orthogonality_search"]["choice_family"][
                    "assignment_count"
                ],
                "report": relpath(OUT_DIR / "report.json"),
                "report_sha256": report["certificate_sha256"],
                "self_orthogonal_assignment_count": artifact[
                    "mixed_orthogonality_search"
                ]["meet_in_middle"]["self_orthogonal_assignment_count"],
                "status": report["status"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
