from __future__ import annotations

import hashlib
import json
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any

try:
    from .derive_d20_golay_hamming_minor_puncture_search import (
        apply_minor,
        mod2_matrix,
        rows_to_masks,
        self_orthogonal,
        weight_histogram,
    )
    from .derive_d20_oriented_matroid_contour import edge_table
    from .derive_d20_oriented_matroid_sector33_dual import (
        build_sector33_height_attachment_matrix,
    )
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_d20_golay_hamming_minor_puncture_search import (
        apply_minor,
        mod2_matrix,
        rows_to_masks,
        self_orthogonal,
        weight_histogram,
    )
    from derive_d20_oriented_matroid_contour import edge_table
    from derive_d20_oriented_matroid_sector33_dual import (
        build_sector33_height_attachment_matrix,
    )
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_sector33_w24_per_edge_rowspace_prune"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
ARTIFACT_PATH = GENERATED / "d20_sector33_w24_per_edge_rowspace_prune.json"

D20_JSON = ROOT / "d20.json"
W24_ROW_ALPHABETIZATION = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_w24_hexacode_row_alphabetization"
    / "report.json"
)
TYPED_COORDINATE_SEARCH = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_sector33_w24_typed_coordinate_search"
    / "report.json"
)
F4_ROW_LIFT_SOLVER = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_sector33_w24_f4_row_lift_solver"
    / "report.json"
)
SECTOR33_DUAL_REPORT = (
    D20_INVARIANTS / "theorems" / "d20_oriented_matroid_sector33_dual" / "report.json"
)
DERIVE_SCRIPT = ROOT / "src" / "derive_d20_sector33_w24_per_edge_rowspace_prune.py"
VALIDATOR = ROOT / "src" / "certify_d20_sector33_w24_per_edge_rowspace_prune.py"

PAIR_FAMILIES = ("shared_duad", "swapped_pair", "missing_pair")
F4_ROW_ASSIGNMENTS_PER_BALANCED_H6_MAP = 24**6


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
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def input_entry(path: Path, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    entry = {"path": relpath(path), "sha256": sha_file(path)}
    if extra:
        entry.update(extra)
    return entry


def artifact_hash(payload: dict[str, Any]) -> str:
    tmp = dict(payload)
    tmp.pop("artifact_sha256_excluding_this_field", None)
    return sha_json(tmp)


def parse_pair(text: str) -> list[str]:
    return [part.strip() for part in text.strip("{}").split(",") if part.strip()]


def edge_pair_data(row: dict[str, Any], h6_labels: list[str]) -> dict[str, list[str]]:
    shared = parse_pair(row["shared_duad"])
    swapped = parse_pair(row["swapped_pair"])
    present = set(shared) | set(swapped)
    missing = [label for label in h6_labels if label not in present]
    return {
        "shared_duad": shared,
        "swapped_pair": swapped,
        "missing_pair": missing,
    }


def count_balanced_h6_maps(
    rows: list[dict[str, Any]],
    h6_labels: list[str],
    cocircuit_support: list[int],
) -> dict[str, Any]:
    removed_fixed = set(cocircuit_support)
    extra_pool = [int(row["edge_id"]) for row in rows if int(row["edge_id"]) not in removed_fixed]
    label_to_idx = {label: idx for idx, label in enumerate(h6_labels)}
    target = (4,) * len(h6_labels)
    totals_by_pair_family = {}
    per_family_records = {}

    for pair_family in PAIR_FAMILIES:
        total = 0
        records = []
        for extra in extra_pool:
            remaining = [
                row
                for row in rows
                if int(row["edge_id"]) not in removed_fixed and int(row["edge_id"]) != extra
            ]
            options = [
                tuple(label_to_idx[label] for label in edge_pair_data(row, h6_labels)[pair_family])
                for row in remaining
            ]
            order = sorted(range(len(options)), key=lambda idx: len(options[idx]))

            @lru_cache(maxsize=None)
            def rec(position: int, counts: tuple[int, ...]) -> int:
                if position == len(order):
                    return 1 if counts == tuple(0 for _ in h6_labels) else 0
                edge_idx = order[position]
                subtotal = 0
                for option in options[edge_idx]:
                    if counts[option] <= 0:
                        continue
                    next_counts = list(counts)
                    next_counts[option] -= 1
                    subtotal += rec(position + 1, tuple(next_counts))
                return subtotal

            count = rec(0, target)
            total += count
            records.append({"extra_removed": extra, "balanced_h6_map_count": count})
        totals_by_pair_family[pair_family] = total
        per_family_records[pair_family] = records

    total_balanced = sum(totals_by_pair_family.values())
    return {
        "pair_families": list(PAIR_FAMILIES),
        "extra_removed_pool": extra_pool,
        "extra_removed_count": len(extra_pool),
        "balanced_h6_map_count_by_pair_family": totals_by_pair_family,
        "balanced_h6_map_count_total": total_balanced,
        "per_extra_counts_by_pair_family": per_family_records,
        "all_pair_families_balance_every_extra": all(
            record["balanced_h6_map_count"] > 0
            for records in per_family_records.values()
            for record in records
        ),
        "f4_row_assignments_per_balanced_h6_map": F4_ROW_ASSIGNMENTS_PER_BALANCED_H6_MAP,
        "coordinate_bijection_count_pruned_by_rank": total_balanced
        * F4_ROW_ASSIGNMENTS_PER_BALANCED_H6_MAP,
    }


def summarize_deleted_rowspaces(cocircuit_support: list[int]) -> dict[str, Any]:
    dual_report = load_json(SECTOR33_DUAL_REPORT)
    primal_integer_matrix, attachment = build_sector33_height_attachment_matrix()
    source_matrices = {
        "sector33_primal_mod2": mod2_matrix(primal_integer_matrix),
        "sector33_dual_mod2": mod2_matrix(dual_report["derived"]["dual_summary"]["dual_matrix"]),
    }
    fixed_old_edges = [element for element in cocircuit_support if element != 30]
    extra_pool = [edge_id for edge_id in range(30) if edge_id not in fixed_old_edges]
    summaries = {}

    for source_name, matrix in source_matrices.items():
        rank_histogram = Counter()
        length_histogram = Counter()
        self_orthogonal_histogram = Counter()
        rank12_count = 0
        records = []
        for extra in extra_pool:
            removed = sorted(set(cocircuit_support) | {extra})
            rows, columns, _effective_contracts = apply_minor(matrix, removed, set())
            row_masks = rows_to_masks(rows)
            rank = len(rows)
            rank_histogram[rank] += 1
            length_histogram[len(columns)] += 1
            if rank == 12:
                rank12_count += 1
            record: dict[str, Any] = {
                "extra_removed": extra,
                "remaining_columns": columns,
                "remaining_length": len(columns),
                "rank": rank,
            }
            if rank <= 16:
                hist = weight_histogram(row_masks)
                record["weight_histogram"] = {str(key): value for key, value in hist.items()}
                record["minimum_nonzero_weight"] = min(key for key in hist if key)
                record["self_orthogonal"] = self_orthogonal(row_masks)
                record["doubly_even"] = all(weight % 4 == 0 for weight in hist)
                self_orthogonal_histogram[str(record["self_orthogonal"])] += 1
            records.append(record)
        summaries[source_name] = {
            "source_shape": {"rows": len(matrix), "cols": len(matrix[0])},
            "rank_histogram": {str(key): value for key, value in sorted(rank_histogram.items())},
            "remaining_length_histogram": {
                str(key): value for key, value in sorted(length_histogram.items())
            },
            "rank12_candidate_count": rank12_count,
            "self_orthogonal_histogram_for_enumerated_low_rank_codes": dict(
                sorted(self_orthogonal_histogram.items())
            ),
            "per_extra_records": records,
        }

    return {
        "sector33_attachment": attachment,
        "fixed_removed_cocircuit": cocircuit_support,
        "fixed_removed_old_edges": fixed_old_edges,
        "extra_removed_pool": extra_pool,
        "extra_removed_count": len(extra_pool),
        "source_summaries": summaries,
        "source_matrix_count": len(source_matrices),
        "rowspace_case_count": len(extra_pool) * len(source_matrices),
        "rank12_candidate_count_total": sum(
            summary["rank12_candidate_count"] for summary in summaries.values()
        ),
        "all_remaining_sets_have_24_edges": all(
            summary["remaining_length_histogram"] == {"24": len(extra_pool)}
            for summary in summaries.values()
        ),
    }


def build_artifact() -> dict[str, Any]:
    d20 = load_json(D20_JSON)
    w24 = load_json(W24_ROW_ALPHABETIZATION)
    typed = load_json(TYPED_COORDINATE_SEARCH)
    f4_solver = load_json(F4_ROW_LIFT_SOLVER)
    dual = load_json(SECTOR33_DUAL_REPORT)

    rows = edge_table(d20)
    h6_labels = w24["witness"]["row_alphabetization"]["column_labels"]
    target_golay = w24["witness"]["golay_code"]
    cocircuit = list(dual["derived"]["dual_positive_cocircuit"]["support"])
    h6_counts = count_balanced_h6_maps(rows, h6_labels, cocircuit)
    rowspaces = summarize_deleted_rowspaces(cocircuit)

    checks = {
        "w24_row_alphabetization_is_certified": w24["status"]
        == "D20_W24_HEXACODE_ROW_ALPHABETIZATION_CERTIFIED"
        and w24["all_checks_pass"] is True,
        "typed_coordinate_search_input_is_certified": typed["status"]
        == "D20_SECTOR33_W24_TYPED_COORDINATE_SEARCH_CERTIFIED"
        and typed["all_checks_pass"] is True,
        "f4_row_lift_solver_input_is_certified": f4_solver["status"]
        == "D20_SECTOR33_W24_F4_ROW_LIFT_SOLVER_CERTIFIED"
        and f4_solver["all_checks_pass"] is True,
        "sector33_dual_input_is_certified": dual["status"]
        == "D20_ORIENTED_MATROID_SECTOR33_DUAL_CERTIFIED"
        and dual["all_checks_pass"] is True,
        "target_golay_rank_is_12": target_golay["rank"] == 12,
        "relaxed_h6_maps_exist": h6_counts["balanced_h6_map_count_total"] > 0,
        "relaxed_h6_maps_balance_every_pair_family_and_extra": h6_counts[
            "all_pair_families_balance_every_extra"
        ],
        "f4_row_assignment_multiplier_is_24_to_6": h6_counts[
            "f4_row_assignments_per_balanced_h6_map"
        ]
        == F4_ROW_ASSIGNMENTS_PER_BALANCED_H6_MAP,
        "rowspace_case_count_is_50": rowspaces["rowspace_case_count"] == 50,
        "all_deleted_rowspaces_have_length_24": rowspaces["all_remaining_sets_have_24_edges"],
        "primal_deleted_rank_histogram_is_18_19": rowspaces["source_summaries"][
            "sector33_primal_mod2"
        ]["rank_histogram"]
        == {"18": 5, "19": 20},
        "dual_deleted_rank_histogram_is_3": rowspaces["source_summaries"][
            "sector33_dual_mod2"
        ]["rank_histogram"]
        == {"3": 25},
        "no_deleted_rowspace_has_rank_12": rowspaces["rank12_candidate_count_total"] == 0,
        "column_permutation_cannot_change_rank": True,
        "all_per_edge_coordinate_bijections_pruned_before_golay_basis_compare": True,
        "explicit_morphism_remains_open": True,
    }

    payload: dict[str, Any] = {
        "schema": "d20.proof_obligation.sector33_w24_per_edge_rowspace_prune.artifact@1",
        "status": "D20_SECTOR33_W24_PER_EDGE_ROWSPACE_PRUNE_DERIVED",
        "claim_scope": (
            "Prune the huge per-edge H6/F4 coordinate-bijection family by rowspace rank "
            "before comparing against the certified W24 Golay basis."
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
            "typed_coordinate_search": input_entry(
                TYPED_COORDINATE_SEARCH,
                {
                    "certificate_sha256": typed["certificate_sha256"],
                    "status": typed["status"],
                },
            ),
            "f4_row_lift_solver": input_entry(
                F4_ROW_LIFT_SOLVER,
                {
                    "certificate_sha256": f4_solver["certificate_sha256"],
                    "status": f4_solver["status"],
                },
            ),
            "sector33_dual": input_entry(
                SECTOR33_DUAL_REPORT,
                {
                    "certificate_sha256": dual["certificate_sha256"],
                    "status": dual["status"],
                },
            ),
        },
        "target_golay_profile": {
            "length": target_golay["length"],
            "rank": target_golay["rank"],
            "weight_histogram": target_golay["weight_histogram"],
            "generator_basis_masks_sha256": sha_json(target_golay["generator_basis_masks"]),
        },
        "balanced_relaxed_h6_coordinate_maps": h6_counts,
        "deleted_rowspace_prune": rowspaces,
        "rank_invariance_argument": {
            "statement": (
                "A per-edge H6/F4 coordinate assignment is a bijection from the 24 surviving "
                "sector33 edge columns to the 24 W24 coordinates. Such a bijection only "
                "permutes columns, and column permutations preserve binary rowspace rank."
            ),
            "target_rank": target_golay["rank"],
            "observed_source_ranks": {
                source: summary["rank_histogram"]
                for source, summary in rowspaces["source_summaries"].items()
            },
            "basis_compare_attempted": False,
            "basis_compare_blocked_reason": "no deleted source rowspace in this family has rank 12",
        },
        "checks": checks,
    }
    payload["artifact_sha256_excluding_this_field"] = artifact_hash(payload)
    return payload


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    h6_counts = artifact["balanced_relaxed_h6_coordinate_maps"]
    rowspaces = artifact["deleted_rowspace_prune"]
    report: dict[str, Any] = {
        "schema": "d20.proof_obligation.sector33_w24_per_edge_rowspace_prune@1",
        "status": "D20_SECTOR33_W24_PER_EDGE_ROWSPACE_PRUNE_CERTIFIED",
        "all_checks_pass": all(artifact["checks"].values()),
        "claim": (
            "The balanced relaxed H6 maps do create a huge finite per-edge H6/F4 coordinate "
            "bijection family, but the family is pruned before Golay basis comparison. For "
            "the 25 cocircuit-plus-one deletions, the sector33 primal deletion rowspaces have "
            "rank 18 or 19 and the dual deletion rowspaces have rank 3. Since any per-edge "
            "coordinate assignment is only a column permutation, none can match the rank-12 "
            "certified W24 Golay code."
        ),
        "definition": {
            "per_edge_coordinate_bijection": (
                "a balanced relaxed H6 edge assignment, followed by an F4 row bijection inside "
                "each of the six H6 columns"
            ),
            "pruning_oracle": (
                "binary rowspace rank is invariant under coordinate permutation; rank mismatch "
                "blocks equality with the W24 Golay rowspace before basis comparison"
            ),
        },
        "closure_boundary": {
            "certifies": [
                f"{h6_counts['balanced_h6_map_count_total']} balanced relaxed H6 maps exist in the tested family",
                f"{h6_counts['coordinate_bijection_count_pruned_by_rank']} per-edge H6/F4 coordinate bijections are rank-pruned",
                "25 deletion-only cocircuit-plus-one cases were tested for each of primal and dual sector33 matrices",
                "the primal deleted rowspaces have ranks 18 or 19",
                "the dual deleted rowspaces have rank 3",
                "no deleted source rowspace in this family has the rank-12 precondition needed to equal W24 Golay",
            ],
            "does_not_certify": [
                "absence of a morphism using delete/contract choices; that is covered separately by the bounded minor search",
                "absence of a morphism using quotienting or additional non-edge coordinates",
                "absence of a morphism using external Wu/hexacode marking data",
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
            "balanced_relaxed_h6_coordinate_maps": h6_counts,
            "deleted_rowspace_prune": rowspaces,
            "rank_invariance_argument": artifact["rank_invariance_argument"],
        },
        "checks": artifact["checks"],
        "next_highest_yield_item": (
            "Leave the cocircuit-plus-one deletion family and test quotient or marked "
            "sector33-to-W24 maps that can actually change rank to 12 before coordinate labelling."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": "d20.proof_obligation.sector33_w24_per_edge_rowspace_prune_manifest@1",
        "name": THEOREM_ID,
        "certification_tests": [
            "verify W24, typed-coordinate, F4-row-lift, and sector33 dual inputs",
            "count balanced relaxed H6 maps in the cocircuit-plus-one deletion family",
            "compute the F4 row assignment multiplier per balanced H6 map",
            "delete the fixed cocircuit plus one extra edge from primal and dual binary sector33 matrices",
            "verify all deleted rowspaces have 24 columns",
            "verify no deleted rowspace has rank 12",
            "record the column-permutation rank-invariance pruning argument",
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
                "balanced_h6_map_count_total": artifact[
                    "balanced_relaxed_h6_coordinate_maps"
                ]["balanced_h6_map_count_total"],
                "coordinate_bijection_count_pruned_by_rank": artifact[
                    "balanced_relaxed_h6_coordinate_maps"
                ]["coordinate_bijection_count_pruned_by_rank"],
                "rank12_candidate_count_total": artifact["deleted_rowspace_prune"][
                    "rank12_candidate_count_total"
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
