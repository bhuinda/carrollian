from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

try:
    from .derive_d20_sandpile_critical_group_theorem import rel, sha_file, sha_json
    from .paths import D20_INVARIANTS
except ImportError:  # Supports `python src/derive_d20_tube_sandpile_flip_sector_refinement.py`.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.derive_d20_sandpile_critical_group_theorem import rel, sha_file, sha_json
    from src.paths import D20_INVARIANTS


THEOREM_ID = "tube_sandpile_flip_sector_refinement"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
PROFILE_COMPRESSION_REPORT = (
    D20_INVARIANTS / "theorems" / "tube_sandpile_flip_profile_compression" / "report.json"
)
COSET_CLASSIFIER_REPORT = (
    D20_INVARIANTS / "theorems" / "tube_sandpile_flip_coset_classifier" / "report.json"
)
PRESENTATION_REPORT = (
    D20_INVARIANTS / "theorems" / "tube_sandpile_flip_move_presentation" / "report.json"
)
KERNEL_FLIPS_REPORT = (
    D20_INVARIANTS / "theorems" / "tube_sandpile_kernel_flips" / "report.json"
)
FOURIER_RESIDUE_REPORT = (
    D20_INVARIANTS / "theorems" / "fourier_residue_screen" / "report.json"
)
FOURIER_A985_REPORT = (
    D20_INVARIANTS / "theorems" / "fourier_a985_sector_character_candidates" / "report.json"
)

SCREEN0_DEFECT_MASK = (1 << 7) | (1 << 9)


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


def xor_all(values: list[int]) -> int:
    out = 0
    for value in values:
        out ^= value
    return out


def span_from_coordinate_masks(values: list[int]) -> set[int]:
    out: set[int] = set()
    for selector in range(1 << len(values)):
        selected = [values[idx] for idx in range(len(values)) if (selector >> idx) & 1]
        out.add(xor_all(selected))
    return out


def histogram(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(value) for key, value in sorted(counter.items())}


def freeze_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): freeze_json(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [freeze_json(item) for item in value]
    return value


def profile_key(row: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    return {field: freeze_json(row[field]) for field in fields}


def profile_classes(rows: list[dict[str, Any]], fields: list[str]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = profile_key(row, fields)
        key_hash = sha_json(key)
        grouped.setdefault(key_hash, {"profile_key": key, "coset_indices": []})
        grouped[key_hash]["coset_indices"].append(int(row["coset_index"]))

    out = []
    for class_index, (key_hash, item) in enumerate(
        sorted(grouped.items(), key=lambda pair: (pair[1]["coset_indices"][0], pair[0]))
    ):
        coset_indices = sorted(item["coset_indices"])
        out.append(
            {
                "profile_class_index": class_index,
                "profile_key_sha256": key_hash,
                "class_size": len(coset_indices),
                "coset_indices": coset_indices,
                "profile_key": item["profile_key"],
                "contains_cover_span_coset": 0 in coset_indices,
            }
        )
    return out


def screen_signature(mask: int, defect_vectors: list[int]) -> str:
    return "".join(
        "1" if (int(mask) & int(defect)).bit_count() & 1 else "0"
        for defect in defect_vectors
    )


def oriented_transition(pair: dict[str, Any], defect_vectors: list[int], tail_only: bool = False) -> str:
    left = screen_signature(int(pair["mask_a"]), defect_vectors)
    right = screen_signature(int(pair["mask_b"]), defect_vectors)
    if tail_only:
        left = left[1:]
        right = right[1:]
    if int(pair["grade_a"]) == -1 and int(pair["grade_b"]) == 1:
        return f"{left}->{right}"
    if int(pair["grade_a"]) == 1 and int(pair["grade_b"]) == -1:
        return f"{right}->{left}"
    raise ValueError("grade-flip pair does not have opposite grades")


def reconstruct_pairs_by_coset(
    presentation: dict[str, Any],
    kernel: dict[str, Any],
) -> dict[int, list[dict[str, Any]]]:
    pres_derived = presentation["derived"]
    cover_coordinate_masks = [
        int(row["basis_coordinate_mask"])
        for row in pres_derived["cover_coordinate_rows"]
    ]
    cover_coordinate_span = span_from_coordinate_masks(cover_coordinate_masks)
    coset_index_by_representative = {
        int(row["coset_representative_coordinate_mask"]): int(row["coset_index"])
        for row in pres_derived["cover_coset_rows"]
    }

    def representative(coords: int) -> int:
        return min(coords ^ span_coords for span_coords in cover_coordinate_span)

    delta_to_coset_index = {
        int(row["delta_mask"]): coset_index_by_representative[
            representative(int(row["basis_coordinate_mask"]))
        ]
        for row in pres_derived["generator_rows"]
    }

    by_coset: dict[int, list[dict[str, Any]]] = {idx: [] for idx in range(64)}
    for pair in kernel["derived"]["grade_flip_pair_rows"]:
        coset_index = delta_to_coset_index[int(pair["delta_mask"])]
        by_coset[coset_index].append(pair)

    for coset_index, pair_rows in by_coset.items():
        by_coset[coset_index] = sorted(
            pair_rows,
            key=lambda row: (
                int(row["fiber_index"]),
                int(row["pair_index"]),
                int(row["delta_mask"]),
            ),
        )
    return by_coset


def screen_summary(
    fourier_residue: dict[str, Any],
    fourier_a985: dict[str, Any],
) -> dict[str, Any]:
    residue_defects = [
        int(value)
        for value in fourier_residue["derived"]["combined_screen"]["defect_vectors"]
    ]
    candidates = sorted(
        fourier_a985["derived"]["candidates"],
        key=lambda row: int(row["screen_id"].split("_")[-1]),
    )
    candidate_rows = [
        {
            "screen_id": row["screen_id"],
            "defect_vector_mask": int(row["defect_vector_mask"]),
            "defect_cycle_ids": [int(value) for value in row["defect_cycle_ids"]],
            "homogeneous_sector_count": int(row["homogeneous_sector_count"]),
            "mixed_sector_count": int(row["mixed_sector_count"]),
            "descends_to_all_39_sector_scalars": bool(row["descends_to_all_39_sector_scalars"]),
            "all_nonzero_public_zero_supports_scalar": bool(
                row["all_nonzero_public_zero_supports_scalar"]
            ),
        }
        for row in candidates
    ]
    return {
        "screen_ids": [row["screen_id"] for row in candidate_rows],
        "defect_vectors": residue_defects,
        "candidate_rows": candidate_rows,
        "candidate_rows_sha256": sha_json(candidate_rows),
    }


def refinement_rows(
    coset_rows: list[dict[str, Any]],
    pairs_by_coset: dict[int, list[dict[str, Any]]],
    defect_vectors: list[int],
) -> list[dict[str, Any]]:
    out = []
    for row in coset_rows:
        coset_index = int(row["coset_index"])
        pair_rows = pairs_by_coset[coset_index]
        full_transition = Counter()
        tail_transition = Counter()
        endpoint_cells = Counter()
        delta_signatures = Counter()
        for pair in pair_rows:
            left = screen_signature(int(pair["mask_a"]), defect_vectors)
            right = screen_signature(int(pair["mask_b"]), defect_vectors)
            full_transition[oriented_transition(pair, defect_vectors)] += 1
            tail_transition[oriented_transition(pair, defect_vectors, tail_only=True)] += 1
            endpoint_cells[left] += 1
            endpoint_cells[right] += 1
            delta_signatures[screen_signature(int(pair["delta_mask"]), defect_vectors)] += 1

        full_histogram = histogram(full_transition)
        tail_histogram = histogram(tail_transition)
        endpoint_histogram = histogram(endpoint_cells)
        delta_histogram = histogram(delta_signatures)
        profile = {
            "pair_screen_signature_transition_histogram": full_histogram,
            "pair_screen12_transition_histogram": tail_histogram,
            "pair_screen_endpoint_histogram": endpoint_histogram,
            "pair_delta_screen_signature_histogram": delta_histogram,
        }
        out.append(
            {
                "coset_index": coset_index,
                "grade_flip_pair_count": int(row["grade_flip_pair_count"]),
                "exact_divisor_fiber_count": int(row["exact_divisor_fiber_count"]),
                "pair_sandpile_class_order_histogram": row["pair_sandpile_class_order_histogram"],
                "fiber_sandpile_class_order_histogram": row["fiber_sandpile_class_order_histogram"],
                "pair_screen_signature_transition_histogram": full_histogram,
                "pair_screen12_transition_histogram": tail_histogram,
                "pair_screen_endpoint_histogram": endpoint_histogram,
                "pair_delta_screen_signature_histogram": delta_histogram,
                "screen_refinement_key_sha256": sha_json(profile),
            }
        )
    return sorted(out, key=lambda row: int(row["coset_index"]))


def split_rows(
    combined_rows: list[dict[str, Any]],
    screen12_rows: list[dict[str, Any]],
    rows_by_coset: dict[int, dict[str, Any]],
) -> list[dict[str, Any]]:
    refined_class_by_coset = {
        int(coset_index): int(row["profile_class_index"])
        for row in screen12_rows
        for coset_index in row["coset_indices"]
    }
    out = []
    for row in combined_rows:
        if int(row["class_size"]) == 1:
            continue
        coset_indices = [int(value) for value in row["coset_indices"]]
        refined_indices = [refined_class_by_coset[idx] for idx in coset_indices]
        out.append(
            {
                "combined_profile_class_index": int(row["profile_class_index"]),
                "combined_profile_class_size": int(row["class_size"]),
                "coset_indices": coset_indices,
                "screen12_refined_class_indices": refined_indices,
                "singleton_after_screen12_refinement": len(set(refined_indices)) == len(coset_indices),
                "coset_screen12_rows": [
                    {
                        "coset_index": idx,
                        "screen_refinement_key_sha256": rows_by_coset[idx][
                            "screen_refinement_key_sha256"
                        ],
                        "pair_screen12_transition_histogram": rows_by_coset[idx][
                            "pair_screen12_transition_histogram"
                        ],
                    }
                    for idx in coset_indices
                ],
            }
        )
    return out


def build_theorem() -> dict[str, Any]:
    profile = load_json(PROFILE_COMPRESSION_REPORT)
    coset = load_json(COSET_CLASSIFIER_REPORT)
    presentation = load_json(PRESENTATION_REPORT)
    kernel = load_json(KERNEL_FLIPS_REPORT)
    fourier_residue = load_json(FOURIER_RESIDUE_REPORT)
    fourier_a985 = load_json(FOURIER_A985_REPORT)

    coset_rows = coset["derived"]["coset_rows"]
    pairs_by_coset = reconstruct_pairs_by_coset(presentation, kernel)
    screens = screen_summary(fourier_residue, fourier_a985)
    defect_vectors = screens["defect_vectors"]
    rows = refinement_rows(coset_rows, pairs_by_coset, defect_vectors)
    rows_by_coset = {int(row["coset_index"]): row for row in rows}

    combined_order_fields = [
        "grade_flip_pair_count",
        "exact_divisor_fiber_count",
        "pair_sandpile_class_order_histogram",
        "fiber_sandpile_class_order_histogram",
    ]
    full_transition_fields = combined_order_fields + [
        "pair_screen_signature_transition_histogram"
    ]
    screen12_transition_fields = combined_order_fields + [
        "pair_screen12_transition_histogram"
    ]
    endpoint_fields = combined_order_fields + ["pair_screen_endpoint_histogram"]

    combined_rows = profile["derived"]["combined_order_profile"]["class_rows"]
    combined_non_singletons = [
        row for row in combined_rows if int(row["class_size"]) > 1
    ]
    full_transition_classes = profile_classes(rows, full_transition_fields)
    screen12_transition_classes = profile_classes(rows, screen12_transition_fields)
    endpoint_classes = profile_classes(rows, endpoint_fields)
    combined_split_rows = split_rows(
        combined_rows,
        screen12_transition_classes,
        rows_by_coset,
    )

    pair_count_by_coset_matches = all(
        len(pairs_by_coset[int(row["coset_index"])]) == int(row["grade_flip_pair_count"])
        for row in coset_rows
    )
    all_delta_signatures_are_screen0_odd = all(
        signature.startswith("1")
        for row in rows
        for signature in row["pair_delta_screen_signature_histogram"]
    )
    checks = {
        "profile_compression_source_is_certified": profile.get("status")
        == "D20_TUBE_SANDPILE_FLIP_PROFILE_COMPRESSION_CERTIFIED"
        and profile.get("all_checks_pass") is True,
        "coset_classifier_source_is_certified": coset.get("status")
        == "D20_TUBE_SANDPILE_FLIP_COSET_CLASSIFIER_CERTIFIED"
        and coset.get("all_checks_pass") is True,
        "presentation_source_is_certified": presentation.get("status")
        == "D20_TUBE_SANDPILE_FLIP_MOVE_PRESENTATION_CERTIFIED"
        and presentation.get("all_checks_pass") is True,
        "kernel_flip_source_is_certified": kernel.get("status")
        == "D20_TUBE_SANDPILE_KERNEL_FLIPS_CERTIFIED"
        and kernel.get("all_checks_pass") is True,
        "fourier_residue_source_is_certified": fourier_residue.get("status")
        == "D20_FOURIER_RESIDUE_SCREEN_CERTIFIED"
        and fourier_residue.get("all_checks_pass") is True,
        "fourier_a985_sector_source_is_certified": fourier_a985.get("status")
        == "D20_FOURIER_A985_SECTOR_CHARACTER_CANDIDATES_EVALUATED"
        and fourier_a985.get("all_checks_pass") is True,
        "defect_vectors_match_sector_candidate_order": [
            row["defect_vector_mask"] for row in screens["candidate_rows"]
        ]
        == defect_vectors,
        "screen0_defect_vector_matches_tube_grade": defect_vectors[0] == SCREEN0_DEFECT_MASK,
        "coset_count_is_64": len(coset_rows) == 64,
        "pair_rows_cover_1285_grade_flips": sum(len(value) for value in pairs_by_coset.values())
        == 1285,
        "pair_count_by_coset_matches_classifier": pair_count_by_coset_matches,
        "full_screen_transition_profile_class_count_is_64": len(full_transition_classes) == 64,
        "screen12_transition_profile_class_count_is_64": len(screen12_transition_classes) == 64,
        "endpoint_screen_profile_class_count_is_64": len(endpoint_classes) == 64,
        "screen12_transition_size_histogram_is_singletons": histogram(
            Counter(row["class_size"] for row in screen12_transition_classes)
        )
        == {"1": 64},
        "combined_non_singleton_class_count_is_12": len(combined_non_singletons) == 12,
        "combined_non_singleton_coset_mass_is_28": sum(
            int(row["class_size"]) for row in combined_non_singletons
        )
        == 28,
        "all_non_singleton_combined_classes_split_to_singletons": all(
            row["singleton_after_screen12_refinement"] for row in combined_split_rows
        ),
        "all_flip_pair_delta_signatures_are_screen0_odd": all_delta_signatures_are_screen0_odd,
        "cover_span_coset_remains_singleton": any(
            row["coset_indices"] == [0] for row in screen12_transition_classes
        ),
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_TUBE_SANDPILE_FLIP_SECTOR_REFINEMENT_CERTIFIED"
        if all_checks_pass
        else "D20_TUBE_SANDPILE_FLIP_SECTOR_REFINEMENT_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.tube_sandpile_flip_sector_refinement",
        "status": status,
        "object": "d20",
        "claim": (
            "The three signed-turn residue screens refine the 48 combined-order "
            "flip-coset profile classes to all 64 cosets. The 12 non-singleton "
            "combined-order classes split into singleton classes when grade-flip "
            "pairs are profiled by oriented screen-signature transitions."
        ),
        "definition": {
            "screen_signature": (
                "For defect vectors d0,d1,d2, the screen signature of a mask is "
                "the three-bit vector (<d0,m>,<d1,m>,<d2,m>) over F2."
            ),
            "oriented_pair_transition": (
                "For each exact-divisor grade-flip pair, orient the transition from "
                "the screen-0 odd endpoint to the screen-0 even endpoint. The "
                "screen1/screen2 transition profile then records the remaining two "
                "screen bits."
            ),
            "scope_boundary": (
                "This is a finite residue-screen refinement grounded in the certified "
                "A985/tube sector-character candidate report. It does not construct a "
                "new 39-sector idempotent basis."
            ),
        },
        "inputs": {
            "tube_sandpile_flip_profile_compression_report": {
                "path": rel(PROFILE_COMPRESSION_REPORT),
                "sha256": sha_file(PROFILE_COMPRESSION_REPORT),
            },
            "tube_sandpile_flip_coset_classifier_report": {
                "path": rel(COSET_CLASSIFIER_REPORT),
                "sha256": sha_file(COSET_CLASSIFIER_REPORT),
            },
            "tube_sandpile_flip_move_presentation_report": {
                "path": rel(PRESENTATION_REPORT),
                "sha256": sha_file(PRESENTATION_REPORT),
            },
            "tube_sandpile_kernel_flips_report": {
                "path": rel(KERNEL_FLIPS_REPORT),
                "sha256": sha_file(KERNEL_FLIPS_REPORT),
            },
            "fourier_residue_screen_report": {
                "path": rel(FOURIER_RESIDUE_REPORT),
                "sha256": sha_file(FOURIER_RESIDUE_REPORT),
            },
            "fourier_a985_sector_character_candidates_report": {
                "path": rel(FOURIER_A985_REPORT),
                "sha256": sha_file(FOURIER_A985_REPORT),
            },
        },
        "derived": {
            "screen_summary": screens,
            "combined_order_profile": {
                "source_class_count": int(
                    profile["derived"]["combined_order_profile"]["class_count"]
                ),
                "source_class_size_histogram": profile["derived"]["combined_order_profile"][
                    "class_size_histogram"
                ],
                "non_singleton_class_count": len(combined_non_singletons),
                "non_singleton_coset_mass": sum(
                    int(row["class_size"]) for row in combined_non_singletons
                ),
                "non_singleton_rows": combined_non_singletons,
            },
            "screen_pair_transition_profile": {
                "fields": full_transition_fields,
                "class_count": len(full_transition_classes),
                "class_size_histogram": histogram(
                    Counter(row["class_size"] for row in full_transition_classes)
                ),
                "class_rows_sha256": sha_json(full_transition_classes),
                "class_rows": full_transition_classes,
            },
            "screen12_pair_transition_profile": {
                "fields": screen12_transition_fields,
                "class_count": len(screen12_transition_classes),
                "class_size_histogram": histogram(
                    Counter(row["class_size"] for row in screen12_transition_classes)
                ),
                "class_rows_sha256": sha_json(screen12_transition_classes),
                "class_rows": screen12_transition_classes,
            },
            "screen_endpoint_profile": {
                "fields": endpoint_fields,
                "class_count": len(endpoint_classes),
                "class_size_histogram": histogram(
                    Counter(row["class_size"] for row in endpoint_classes)
                ),
                "class_rows_sha256": sha_json(endpoint_classes),
                "class_rows": endpoint_classes,
            },
            "coset_screen_refinement_rows_sha256": sha_json(rows),
            "coset_screen_refinement_rows": rows,
            "combined_order_split_rows_sha256": sha_json(combined_split_rows),
            "combined_order_split_rows": combined_split_rows,
        },
        "interpretation": {
            "what_is_certified": (
                "The remaining combined-order profile collisions are not stable after "
                "adding the certified screen1/screen2 transition data on grade-flip pairs."
            ),
            "what_this_does_not_prove": (
                "The singleton refinement is not yet a proof that these screen-transition "
                "features are minimal, nor that they are equivalent to a full 39-sector "
                "idempotent classification."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Pull the singleton screen-transition refinement back to explicit 39-sector "
            "idempotent support data and test whether the same 64-way split survives."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.tube_sandpile_flip_sector_refinement_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "load the certified flip-coset profile compression",
            "reconstruct grade-flip pairs by quotient coset",
            "load the three certified signed-turn residue screens",
            "profile each coset by oriented screen-signature transitions",
            "verify the screen1/screen2 transition profile splits all 64 cosets",
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
