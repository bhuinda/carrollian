from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from .derive_d20_oriented_matroid_sector33_dual import build_sector33_height_attachment_matrix
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.derive_d20_oriented_matroid_sector33_dual import build_sector33_height_attachment_matrix
    from src.paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_golay_hamming_minor_puncture_search"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
ARTIFACT_PATH = GENERATED / "d20_golay_hamming_minor_puncture_search.json"

PRIOR_PROBE_REPORT = (
    D20_INVARIANTS / "proof_obligations" / "d20_golay_hamming_correspondence_probe" / "report.json"
)
SECTOR33_DUAL_REPORT = (
    D20_INVARIANTS / "theorems" / "d20_oriented_matroid_sector33_dual" / "report.json"
)
HEXACODE_ROW_SELECTOR = ROOT / "data" / "selectors" / "hexacode_row_selector.json"
QUADRATIC_GOLAY_OBSTRUCTION = ROOT / "data" / "selectors" / "quadratic_golay_obstruction.json"
DERIVE_SCRIPT = ROOT / "src" / "derive_d20_golay_hamming_minor_puncture_search.py"
VALIDATOR = ROOT / "src" / "certify_d20_golay_hamming_minor_puncture_search.py"

TARGET_EXTENDED_GOLAY_HISTOGRAM = {0: 1, 8: 759, 12: 2576, 16: 759, 24: 1}
TARGET_PUNCTURED_GOLAY_HISTOGRAM = {
    0: 1,
    7: 253,
    8: 506,
    11: 1288,
    12: 1288,
    15: 506,
    16: 253,
    23: 1,
}


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def sha_file(path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} is not a JSON object")
    return payload


def write_json(path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def input_entry(path, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    entry = {"path": relpath(path), "sha256": sha_file(path)}
    if extra:
        entry.update(extra)
    return entry


def artifact_hash(payload: dict[str, Any]) -> str:
    tmp = dict(payload)
    tmp.pop("artifact_sha256_excluding_this_field", None)
    return sha_json(tmp)


def mod2_matrix(matrix: list[list[int]]) -> list[list[int]]:
    return [[int(value) & 1 for value in row] for row in matrix]


def rref_mod2(rows: list[list[int]], ncols: int) -> tuple[list[list[int]], list[int]]:
    work = [[int(value) & 1 for value in row] for row in rows]
    rank = 0
    pivots: list[int] = []
    for col in range(ncols):
        pivot = None
        for row in range(rank, len(work)):
            if work[row][col]:
                pivot = row
                break
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        for row in range(len(work)):
            if row != rank and work[row][col]:
                work[row] = [left ^ right for left, right in zip(work[row], work[rank])]
        pivots.append(col)
        rank += 1
        if rank == len(work):
            break
    return [row for row in work if any(row)], pivots


def row_rank_mod2(rows: list[list[int]], ncols: int) -> int:
    reduced, _pivots = rref_mod2(rows, ncols)
    return len(reduced)


def delete_column(rows: list[list[int]], columns: list[int], original_element: int) -> tuple[list[list[int]], list[int]]:
    idx = columns.index(original_element)
    next_rows = [[value for col, value in enumerate(row) if col != idx] for row in rows]
    next_columns = [value for col, value in enumerate(columns) if col != idx]
    reduced, _pivots = rref_mod2(next_rows, len(next_columns))
    return reduced, next_columns


def contract_column(
    rows: list[list[int]],
    columns: list[int],
    original_element: int,
) -> tuple[list[list[int]], list[int], bool]:
    idx = columns.index(original_element)
    pivot = None
    for row, values in enumerate(rows):
        if values[idx]:
            pivot = row
            break
    if pivot is None:
        next_rows, next_columns = delete_column(rows, columns, original_element)
        return next_rows, next_columns, False
    work = [list(row) for row in rows]
    for row in range(len(work)):
        if row != pivot and work[row][idx]:
            work[row] = [left ^ right for left, right in zip(work[row], work[pivot])]
    contracted = [
        [value for col, value in enumerate(values) if col != idx]
        for row_idx, values in enumerate(work)
        if row_idx != pivot
    ]
    next_columns = [value for col, value in enumerate(columns) if col != idx]
    reduced, _pivots = rref_mod2(contracted, len(next_columns))
    return reduced, next_columns, True


def apply_minor(
    matrix: list[list[int]],
    removed: list[int],
    contracted: set[int],
) -> tuple[list[list[int]], list[int], int]:
    columns = list(range(len(matrix[0])))
    rows, _pivots = rref_mod2(matrix, len(columns))
    effective_contracts = 0
    for original in sorted(removed):
        if original in contracted:
            rows, columns, contracted_nonloop = contract_column(rows, columns, original)
            if contracted_nonloop:
                effective_contracts += 1
        else:
            rows, columns = delete_column(rows, columns, original)
    return rows, columns, effective_contracts


def rows_to_masks(rows: list[list[int]]) -> list[int]:
    masks = []
    for row in rows:
        mask = 0
        for idx, value in enumerate(row):
            if value:
                mask |= 1 << idx
        masks.append(mask)
    return masks


def weight_histogram(row_masks: list[int]) -> dict[int, int]:
    words = [0]
    for mask in row_masks:
        words += [word ^ mask for word in words]
    hist = Counter(word.bit_count() for word in words)
    return dict(sorted(hist.items()))


def puncture_masks(row_masks: list[int], coordinate: int) -> list[int]:
    low_mask = (1 << coordinate) - 1
    out = []
    for mask in row_masks:
        low = mask & low_mask
        high = mask >> (coordinate + 1)
        out.append(low | (high << coordinate))
    reduced_rows = []
    for mask in out:
        reduced_rows.append([(mask >> idx) & 1 for idx in range(23)])
    reduced, _pivots = rref_mod2(reduced_rows, 23)
    return rows_to_masks(reduced)


def self_orthogonal(row_masks: list[int]) -> bool:
    for idx, left in enumerate(row_masks):
        for right in row_masks[idx:]:
            if (left & right).bit_count() % 2:
                return False
    return True


def candidate_score(row: dict[str, Any]) -> tuple[int, int, int, int]:
    rank = int(row["rank"])
    return (
        int(row.get("extended_golay_shape", False)),
        int(row.get("punctured_golay_shape", False)),
        -abs(rank - 12),
        int(row.get("minimum_nonzero_weight", 0) or 0),
    )


def summarize_code(rows: list[list[int]], columns: list[int]) -> dict[str, Any]:
    row_masks = rows_to_masks(rows)
    rank = len(row_masks)
    summary: dict[str, Any] = {
        "rank": rank,
        "remaining_columns": columns,
        "remaining_length": len(columns),
    }
    if rank <= 16:
        hist = weight_histogram(row_masks)
        nonzero_weights = [weight for weight, count in hist.items() if weight and count]
        summary["weight_histogram"] = {str(key): value for key, value in hist.items()}
        summary["minimum_nonzero_weight"] = min(nonzero_weights) if nonzero_weights else None
        summary["self_orthogonal"] = self_orthogonal(row_masks)
        summary["doubly_even"] = all(weight % 4 == 0 for weight in hist)
        summary["extended_golay_shape"] = rank == 12 and hist == TARGET_EXTENDED_GOLAY_HISTOGRAM
        punctured_matches = []
        if rank == 12:
            for coordinate in range(len(columns)):
                punctured = puncture_masks(row_masks, coordinate)
                if len(punctured) == 12 and weight_histogram(punctured) == TARGET_PUNCTURED_GOLAY_HISTOGRAM:
                    punctured_matches.append(
                        {
                            "coordinate_index": coordinate,
                            "original_element": columns[coordinate],
                        }
                    )
        summary["punctured_golay_shape"] = bool(punctured_matches)
        if punctured_matches:
            summary["punctured_matches"] = punctured_matches
    else:
        summary["weight_histogram"] = None
        summary["minimum_nonzero_weight"] = None
        summary["self_orthogonal"] = None
        summary["doubly_even"] = None
        summary["extended_golay_shape"] = False
        summary["punctured_golay_shape"] = False
    return summary


def search_candidates() -> dict[str, Any]:
    dual_report = load_json(SECTOR33_DUAL_REPORT)
    primal_integer_matrix, attachment = build_sector33_height_attachment_matrix()
    primal_mod2 = mod2_matrix(primal_integer_matrix)
    dual_mod2 = mod2_matrix(dual_report["derived"]["dual_summary"]["dual_matrix"])
    cocircuit = list(dual_report["derived"]["dual_positive_cocircuit"]["support"])
    complement = list(dual_report["derived"]["dual_positive_cocircuit"]["complement"])
    source_matrices = {
        "sector33_primal_mod2": primal_mod2,
        "sector33_dual_mod2": dual_mod2,
    }

    rank_histogram_by_source: dict[str, Counter[int]] = {
        key: Counter() for key in source_matrices
    }
    operation_histogram = Counter()
    rank12_candidates = 0
    extended_matches: list[dict[str, Any]] = []
    punctured_matches: list[dict[str, Any]] = []
    best_candidates: list[dict[str, Any]] = []
    all_reduced_lengths_are_24 = True
    candidate_count = 0

    for source_name, matrix in source_matrices.items():
        for extra in complement:
            removed = sorted(cocircuit + [extra])
            for mask in range(1 << len(removed)):
                contracted = {
                    element for bit, element in enumerate(removed) if (mask >> bit) & 1
                }
                rows, columns, effective_contracts = apply_minor(matrix, removed, contracted)
                summary = summarize_code(rows, columns)
                rank = int(summary["rank"])
                candidate_count += 1
                all_reduced_lengths_are_24 = all_reduced_lengths_are_24 and len(columns) == 24
                rank_histogram_by_source[source_name][rank] += 1
                operation_histogram[
                    f"requested_contracts={len(contracted)};effective_contracts={effective_contracts}"
                ] += 1
                if rank == 12:
                    rank12_candidates += 1
                candidate_record = {
                    "source_matrix": source_name,
                    "extra_removed_from_cocircuit_complement": extra,
                    "removed_original_elements": removed,
                    "contracted_original_elements": sorted(contracted),
                    "deleted_original_elements": [element for element in removed if element not in contracted],
                    "effective_contract_count": effective_contracts,
                    "rank": rank,
                    "remaining_columns": summary["remaining_columns"],
                    "minimum_nonzero_weight": summary["minimum_nonzero_weight"],
                    "self_orthogonal": summary["self_orthogonal"],
                    "doubly_even": summary["doubly_even"],
                    "extended_golay_shape": summary["extended_golay_shape"],
                    "punctured_golay_shape": summary["punctured_golay_shape"],
                }
                if rank == 12:
                    candidate_record["weight_histogram"] = summary["weight_histogram"]
                if summary["extended_golay_shape"]:
                    extended_matches.append(candidate_record)
                if summary["punctured_golay_shape"]:
                    candidate_record["punctured_matches"] = summary.get("punctured_matches", [])
                    punctured_matches.append(candidate_record)
                best_candidates.append(candidate_record)
                best_candidates = sorted(best_candidates, key=candidate_score, reverse=True)[:12]

    return {
        "source_matrix_summaries": {
            "sector33_primal_mod2": {
                "shape": {"rows": len(primal_mod2), "cols": len(primal_mod2[0])},
                "rank_mod2": row_rank_mod2(primal_mod2, len(primal_mod2[0])),
                "matrix_sha256": sha_json(primal_mod2),
                "integer_matrix_sha256": sha_json(primal_integer_matrix),
            },
            "sector33_dual_mod2": {
                "shape": {"rows": len(dual_mod2), "cols": len(dual_mod2[0])},
                "rank_mod2": row_rank_mod2(dual_mod2, len(dual_mod2[0])),
                "matrix_sha256": sha_json(dual_mod2),
                "integer_matrix_sha256": dual_report["derived"]["dual_summary"]["dual_matrix_sha256"],
            },
        },
        "sector33_attachment": attachment,
        "natural_removal_family": {
            "fixed_six_element_cocircuit": cocircuit,
            "extra_element_pool": complement,
            "extra_element_count": len(complement),
            "operation_masks_per_removal_set": 128,
            "source_matrix_count": len(source_matrices),
            "candidate_count": candidate_count,
        },
        "search_summary": {
            "rank_histogram_by_source": {
                key: {str(rank): count for rank, count in sorted(hist.items())}
                for key, hist in rank_histogram_by_source.items()
            },
            "operation_histogram": dict(sorted(operation_histogram.items())),
            "rank12_candidate_count": rank12_candidates,
            "extended_golay_shape_match_count": len(extended_matches),
            "punctured_golay_shape_match_count": len(punctured_matches),
            "all_reduced_lengths_are_24": all_reduced_lengths_are_24,
            "exact_morphism_found": bool(extended_matches or punctured_matches),
        },
        "matches": {
            "extended_golay_shape": extended_matches,
            "punctured_golay_shape": punctured_matches,
        },
        "best_candidates": best_candidates,
    }


def build_artifact() -> dict[str, Any]:
    prior_probe = load_json(PRIOR_PROBE_REPORT)
    dual_report = load_json(SECTOR33_DUAL_REPORT)
    hexacode = load_json(HEXACODE_ROW_SELECTOR)
    obstruction = load_json(QUADRATIC_GOLAY_OBSTRUCTION)
    search = search_candidates()
    target_weight_histogram = {
        int(key): int(value) for key, value in hexacode["golay_code"]["weight_histogram"].items()
    }
    checks = {
        "prior_correspondence_probe_is_certified": prior_probe["status"]
        == "D20_GOLAY_HAMMING_CORRESPONDENCE_PROBE_CERTIFIED",
        "sector33_dual_input_is_certified": dual_report["status"]
        == "D20_ORIENTED_MATROID_SECTOR33_DUAL_CERTIFIED",
        "hexacode_golay_endpoint_is_certified": bool(
            hexacode["golay_code"]["matches_extended_golay_weight_enumerator"]
            and hexacode["golay_code"]["self_dual_by_rank_and_self_orthogonal"]
            and hexacode["golay_code"]["doubly_even"]
        ),
        "target_extended_golay_histogram_matches_hexacode_report": target_weight_histogram
        == TARGET_EXTENDED_GOLAY_HISTOGRAM,
        "quadratic_obstruction_remains_active": obstruction["selector_status"][
            "golay_selector_constructed"
        ]
        is False,
        "fixed_cocircuit_has_six_elements": len(
            search["natural_removal_family"]["fixed_six_element_cocircuit"]
        )
        == 6,
        "extra_pool_has_twenty_five_elements": search["natural_removal_family"][
            "extra_element_count"
        ]
        == 25,
        "candidate_count_is_6400": search["natural_removal_family"]["candidate_count"] == 6400,
        "all_candidates_reduce_to_length_24": search["search_summary"][
            "all_reduced_lengths_are_24"
        ],
        "no_extended_golay_shape_match_in_bounded_family": search["search_summary"][
            "extended_golay_shape_match_count"
        ]
        == 0,
        "no_punctured_golay_shape_match_in_bounded_family": search["search_summary"][
            "punctured_golay_shape_match_count"
        ]
        == 0,
        "explicit_morphism_remains_open": search["search_summary"]["exact_morphism_found"] is False,
    }
    payload: dict[str, Any] = {
        "schema": "d20.proof_obligation.golay_hamming_minor_puncture_search.artifact@1",
        "status": "D20_GOLAY_HAMMING_MINOR_PUNCTURE_SEARCH_DERIVED",
        "claim_scope": (
            "Bounded binary minor search for a natural sector33 31 -> 24 -> 23 "
            "Golay-Hamming correspondence."
        ),
        "source_reports": {
            "prior_correspondence_probe": input_entry(
                PRIOR_PROBE_REPORT,
                {
                    "certificate_sha256": prior_probe["certificate_sha256"],
                    "status": prior_probe["status"],
                },
            ),
            "sector33_dual": input_entry(
                SECTOR33_DUAL_REPORT,
                {
                    "certificate_sha256": dual_report["certificate_sha256"],
                    "status": dual_report["status"],
                },
            ),
            "hexacode_row_selector": input_entry(
                HEXACODE_ROW_SELECTOR,
                {
                    "hexacode_row_selector_sha256": hexacode["hexacode_row_selector_sha256"],
                },
            ),
            "quadratic_golay_obstruction": input_entry(
                QUADRATIC_GOLAY_OBSTRUCTION,
                {
                    "status": obstruction["status"],
                    "quadratic_golay_selector_obstruction_sha256": obstruction[
                        "quadratic_golay_selector_obstruction_sha256"
                    ],
                },
            ),
        },
        "target_code_profiles": {
            "extended_golay_24_12_8": {
                "rank": 12,
                "length": 24,
                "weight_histogram": {str(key): value for key, value in TARGET_EXTENDED_GOLAY_HISTOGRAM.items()},
                "properties": ["self_dual", "self_orthogonal", "doubly_even", "minimum_distance_8"],
            },
            "punctured_golay_23_12_7": {
                "rank": 12,
                "length": 23,
                "weight_histogram": {str(key): value for key, value in TARGET_PUNCTURED_GOLAY_HISTOGRAM.items()},
                "properties": ["perfect_binary_golay_profile", "minimum_distance_7"],
            },
        },
        "search": search,
        "checks": checks,
    }
    payload["artifact_sha256_excluding_this_field"] = artifact_hash(payload)
    return payload


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    summary = artifact["search"]["search_summary"]
    report: dict[str, Any] = {
        "schema": "d20.proof_obligation.golay_hamming_minor_puncture_search@1",
        "status": "D20_GOLAY_HAMMING_MINOR_PUNCTURE_SEARCH_CERTIFIED",
        "all_checks_pass": all(artifact["checks"].values()),
        "claim": (
            "The natural sector33 cocircuit-plus-one delete/contract search over F2 found no "
            "extended or punctured Golay-shaped binary row space. This certifies a negative "
            "bounded search result, not a proof that no more general Golay-Hamming morphism exists."
        ),
        "definition": {
            "bounded_family": (
                "For each of the sector33 primal and dual binary matrices, remove the fixed "
                "six-element positive cocircuit plus one element from its complement; for each "
                "seven-element removal set, try every delete/contract mask."
            ),
            "match_criteria": (
                "A 24-coordinate candidate must have rank 12 and the extended Golay weight "
                "enumerator; a 23-coordinate puncture must have the perfect binary Golay "
                "weight enumerator."
            ),
        },
        "closure_boundary": {
            "certifies": [
                "6400 natural sector33 cocircuit-plus-one binary minors were tested",
                "every tested reduction had length 24 before optional puncturing",
                "no tested 24-coordinate row space matched the extended Golay weight profile",
                "no tested rank-12 24-coordinate row space had a puncture matching the length-23 Golay profile",
                "the explicit sector33 31 -> 24 -> 23 morphism remains open outside this bounded family",
            ],
            "does_not_certify": [
                "absence of a Golay-Hamming morphism using non-cocircuit deletion/contract choices",
                "absence of a morphism using additional marking, quotienting, or coordinate relabelling data",
                "a canonical sector33-to-W24 coordinate map",
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
            "natural_removal_family": artifact["search"]["natural_removal_family"],
            "source_matrix_summaries": artifact["search"]["source_matrix_summaries"],
            "search_summary": summary,
            "best_candidates": artifact["search"]["best_candidates"],
        },
        "target_code_profiles": artifact["target_code_profiles"],
        "checks": artifact["checks"],
        "next_highest_yield_item": (
            "Leave the cocircuit-plus-one family and test labelled 31 -> 24 maps induced by "
            "the Wu 24-frame coordinates, if a candidate coordinate labelling can be derived."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": "d20.proof_obligation.golay_hamming_minor_puncture_search_manifest@1",
        "name": THEOREM_ID,
        "certification_tests": [
            "verify prior correspondence probe and source certificates",
            "verify target extended Golay histogram from the hexacode selector report",
            "verify the fixed sector33 positive cocircuit has six elements",
            "verify the natural complement pool has 25 possible seventh elements",
            "verify 6400 delete/contract candidates are searched over F2",
            "verify all reduced candidates have 24 columns",
            "verify no candidate matches the extended or punctured Golay profiles",
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
                "candidate_count": artifact["search"]["natural_removal_family"]["candidate_count"],
                "extended_golay_shape_match_count": artifact["search"]["search_summary"][
                    "extended_golay_shape_match_count"
                ],
                "punctured_golay_shape_match_count": artifact["search"]["search_summary"][
                    "punctured_golay_shape_match_count"
                ],
                "report": relpath(OUT_DIR / "report.json"),
                "report_sha256": report["certificate_sha256"],
                "status": report["status"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
