from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from .derive_d20_golay_hamming_minor_puncture_search import (
        apply_minor,
        mod2_matrix,
        rref_mod2,
        rows_to_masks,
        weight_histogram,
    )
    from .derive_d20_oriented_matroid_sector33_dual import (
        build_sector33_height_attachment_matrix,
    )
    from .paths import D20_INVARIANTS, GENERATED, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_d20_golay_hamming_minor_puncture_search import (
        apply_minor,
        mod2_matrix,
        rref_mod2,
        rows_to_masks,
        weight_histogram,
    )
    from derive_d20_oriented_matroid_sector33_dual import (
        build_sector33_height_attachment_matrix,
    )
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_sector33_w24_marked_quotient_shadow_obstruction"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
ARTIFACT_PATH = GENERATED / f"{THEOREM_ID}.json"

W24_ROW_ALPHABETIZATION = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_w24_hexacode_row_alphabetization"
    / "report.json"
)
PER_EDGE_ROWSPACE_PRUNE = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_sector33_w24_per_edge_rowspace_prune"
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
DERIVE_SCRIPT = ROOT / "src" / "derive_d20_sector33_w24_marked_quotient_shadow_obstruction.py"
VALIDATOR = ROOT / "src" / "certify_d20_sector33_w24_marked_quotient_shadow_obstruction.py"


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


def nullspace_basis_mod2(rows: list[list[int]], ncols: int) -> list[list[int]]:
    reduced, pivots = rref_mod2(rows, ncols)
    pivot_set = set(pivots)
    free_columns = [col for col in range(ncols) if col not in pivot_set]
    basis: list[list[int]] = []
    for free_col in free_columns:
        vector = [0] * ncols
        vector[free_col] = 1
        for row_idx, pivot_col in enumerate(pivots):
            if reduced[row_idx][free_col]:
                vector[pivot_col] = 1
        basis.append(vector)
    return basis


def summarize_code(
    basis_rows: list[list[int]],
    width: int,
    allowed_weights: set[int],
) -> dict[str, Any]:
    reduced, _pivots = rref_mod2(basis_rows, width)
    row_masks = rows_to_masks(reduced)
    hist = weight_histogram(row_masks)
    forbidden_weights = [
        weight for weight, count in sorted(hist.items()) if count and weight not in allowed_weights
    ]
    return {
        "rank": len(reduced),
        "weight_histogram": {str(weight): count for weight, count in sorted(hist.items())},
        "forbidden_weights": forbidden_weights,
        "golay_weight_compatible": not forbidden_weights,
    }


def analyze_deletion_shadows(allowed_weights: set[int]) -> dict[str, Any]:
    dual_report = load_json(SECTOR33_DUAL_REPORT)
    primal_integer_matrix, attachment = build_sector33_height_attachment_matrix()
    primal_mod2 = mod2_matrix(primal_integer_matrix)
    dual_mod2 = mod2_matrix(dual_report["derived"]["dual_summary"]["dual_matrix"])
    cocircuit = list(dual_report["derived"]["dual_positive_cocircuit"]["support"])
    fixed_old_edges = [element for element in cocircuit if element != 30]
    extra_pool = [edge_id for edge_id in range(30) if edge_id not in fixed_old_edges]

    source_specs = {
        "primal_orthogonal_shadow": {
            "source_matrix": primal_mod2,
            "shadow_rule": (
                "If a rank-12 self-dual Golay code G were contained in the high-rank "
                "sector33 deletion code C after coordinate relabelling, then C_perp would "
                "be contained in G_perp=G. Test C_perp by weight."
            ),
            "use_orthogonal_complement": True,
        },
        "dual_rowspace_shadow": {
            "source_matrix": dual_mod2,
            "shadow_rule": (
                "The low-rank dual deletion rowspace is tested directly as a possible "
                "marked Golay subcode shadow."
            ),
            "use_orthogonal_complement": False,
        },
    }

    summaries: dict[str, Any] = {}
    for name, spec in source_specs.items():
        rank_histogram: Counter[int] = Counter()
        forbidden_weight_histogram: Counter[int] = Counter()
        histogram_classes: Counter[str] = Counter()
        compatible_cases = 0
        records = []

        for extra in extra_pool:
            removed = sorted(set(cocircuit) | {extra})
            rows, columns, _effective_contracts = apply_minor(
                spec["source_matrix"],
                removed,
                set(),
            )
            if spec["use_orthogonal_complement"]:
                shadow_rows = nullspace_basis_mod2(rows, len(columns))
            else:
                shadow_rows = rows
            summary = summarize_code(shadow_rows, len(columns), allowed_weights)
            rank_histogram[summary["rank"]] += 1
            compatible_cases += int(summary["golay_weight_compatible"])
            for weight in summary["forbidden_weights"]:
                forbidden_weight_histogram[weight] += 1
            histogram_classes[sha_json(summary["weight_histogram"])] += 1
            records.append(
                {
                    "extra_removed": extra,
                    "remaining_columns": columns,
                    "shadow_rank": summary["rank"],
                    "weight_histogram": summary["weight_histogram"],
                    "forbidden_weights": summary["forbidden_weights"],
                    "golay_weight_compatible": summary["golay_weight_compatible"],
                }
            )

        summaries[name] = {
            "shadow_rule": spec["shadow_rule"],
            "case_count": len(records),
            "rank_histogram": {str(rank): count for rank, count in sorted(rank_histogram.items())},
            "golay_weight_compatible_case_count": compatible_cases,
            "all_cases_have_forbidden_weights": compatible_cases == 0,
            "forbidden_weight_case_histogram": {
                str(weight): count for weight, count in sorted(forbidden_weight_histogram.items())
            },
            "weight_histogram_class_count": len(histogram_classes),
            "sample_records": records[:8],
            "all_records_sha256": sha_json(records),
        }

    return {
        "sector33_attachment": attachment,
        "fixed_removed_cocircuit": cocircuit,
        "fixed_removed_old_edges": fixed_old_edges,
        "extra_removed_pool": extra_pool,
        "extra_removed_count": len(extra_pool),
        "allowed_golay_weights": sorted(allowed_weights),
        "shadow_summaries": summaries,
    }


def build_artifact() -> dict[str, Any]:
    w24 = load_json(W24_ROW_ALPHABETIZATION)
    per_edge = load_json(PER_EDGE_ROWSPACE_PRUNE)
    f4_solver = load_json(F4_ROW_LIFT_SOLVER)
    dual = load_json(SECTOR33_DUAL_REPORT)

    target_hist = {
        int(weight): int(count)
        for weight, count in w24["witness"]["golay_code"]["weight_histogram"].items()
    }
    allowed_weights = {weight for weight, count in target_hist.items() if count}
    shadows = analyze_deletion_shadows(allowed_weights)
    primal_shadow = shadows["shadow_summaries"]["primal_orthogonal_shadow"]
    dual_shadow = shadows["shadow_summaries"]["dual_rowspace_shadow"]

    checks = {
        "w24_row_alphabetization_is_certified": w24["status"]
        == "D20_W24_HEXACODE_ROW_ALPHABETIZATION_CERTIFIED"
        and w24["all_checks_pass"] is True,
        "per_edge_rowspace_prune_input_is_certified": per_edge["status"]
        == "D20_SECTOR33_W24_PER_EDGE_ROWSPACE_PRUNE_CERTIFIED"
        and per_edge["all_checks_pass"] is True,
        "f4_row_lift_solver_input_is_certified": f4_solver["status"]
        == "D20_SECTOR33_W24_F4_ROW_LIFT_SOLVER_CERTIFIED"
        and f4_solver["all_checks_pass"] is True,
        "sector33_dual_input_is_certified": dual["status"]
        == "D20_ORIENTED_MATROID_SECTOR33_DUAL_CERTIFIED"
        and dual["all_checks_pass"] is True,
        "target_golay_is_self_dual_rank12": w24["witness"]["golay_code"]["rank"] == 12
        and w24["witness"]["golay_code"]["self_dual_by_rank_and_self_orthogonal"] is True,
        "target_allowed_weights_are_0_8_12_16_24": sorted(allowed_weights) == [0, 8, 12, 16, 24],
        "extra_removed_pool_has_25_edges": shadows["extra_removed_count"] == 25,
        "primal_orthogonal_shadow_cases_are_25": primal_shadow["case_count"] == 25,
        "primal_orthogonal_shadow_rank_histogram_is_5_6": primal_shadow["rank_histogram"]
        == {"5": 20, "6": 5},
        "primal_orthogonal_shadow_has_no_golay_weight_compatible_case": primal_shadow[
            "golay_weight_compatible_case_count"
        ]
        == 0,
        "dual_rowspace_shadow_cases_are_25": dual_shadow["case_count"] == 25,
        "dual_rowspace_shadow_rank_histogram_is_3": dual_shadow["rank_histogram"] == {"3": 25},
        "dual_rowspace_shadow_has_no_golay_weight_compatible_case": dual_shadow[
            "golay_weight_compatible_case_count"
        ]
        == 0,
        "weight_obstruction_is_coordinate_permutation_invariant": True,
        "marked_quotient_shadow_route_remains_open_outside_tested_family": True,
    }

    payload: dict[str, Any] = {
        "schema": "d20.proof_obligation.sector33_w24_marked_quotient_shadow_obstruction.artifact@1",
        "status": "D20_SECTOR33_W24_MARKED_QUOTIENT_SHADOW_OBSTRUCTION_DERIVED",
        "claim_scope": (
            "Weight-invariant obstruction for the deletion-only marked quotient shadows "
            "left after direct sector33-to-W24 coordinate matching failed."
        ),
        "source_reports": {
            "w24_row_alphabetization": input_entry(
                W24_ROW_ALPHABETIZATION,
                {
                    "certificate_sha256": w24["certificate_sha256"],
                    "status": w24["status"],
                },
            ),
            "per_edge_rowspace_prune": input_entry(
                PER_EDGE_ROWSPACE_PRUNE,
                {
                    "certificate_sha256": per_edge["certificate_sha256"],
                    "status": per_edge["status"],
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
        "target_golay_weight_test": {
            "target_rank": w24["witness"]["golay_code"]["rank"],
            "self_dual": w24["witness"]["golay_code"][
                "self_dual_by_rank_and_self_orthogonal"
            ],
            "weight_histogram": w24["witness"]["golay_code"]["weight_histogram"],
            "allowed_nonzero_weights": [weight for weight in sorted(allowed_weights) if weight],
            "coordinate_permutation_invariant": True,
        },
        "deletion_shadow_analysis": shadows,
        "checks": checks,
    }
    payload["artifact_sha256_excluding_this_field"] = artifact_hash(payload)
    return payload


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    shadows = artifact["deletion_shadow_analysis"]["shadow_summaries"]
    report: dict[str, Any] = {
        "schema": "d20.proof_obligation.sector33_w24_marked_quotient_shadow_obstruction@1",
        "status": "D20_SECTOR33_W24_MARKED_QUOTIENT_SHADOW_OBSTRUCTION_CERTIFIED",
        "all_checks_pass": all(artifact["checks"].values()),
        "claim": (
            "The cocircuit-plus-one deletion family is also blocked after weakening the target "
            "from direct W24 equality to marked Golay-compatible shadows. The high-rank primal "
            "codes would require their orthogonal shadows to sit inside the self-dual W24 Golay "
            "code, and the low-rank dual shadows would have to sit inside it directly. Every "
            "tested shadow has forbidden word weights, so no coordinate relabelling can make "
            "these shadows Golay subcodes."
        ),
        "definition": {
            "weight_test": (
                "A subcode of the certified extended Golay code can only contain words of "
                "weights 0, 8, 12, 16, or 24. Hamming weight is invariant under coordinate "
                "permutation."
            ),
            "primal_orthogonal_shadow": shadows["primal_orthogonal_shadow"]["shadow_rule"],
            "dual_rowspace_shadow": shadows["dual_rowspace_shadow"]["shadow_rule"],
        },
        "closure_boundary": {
            "certifies": [
                "25 cocircuit-plus-one deletion shadows were tested for the primal sector33 matrix",
                "25 cocircuit-plus-one deletion shadows were tested for the dual sector33 matrix",
                "the primal orthogonal shadows have ranks 5 or 6 and all contain forbidden Golay weights",
                "the dual rowspace shadows have rank 3 and all contain forbidden Golay weights",
                "coordinate relabelling cannot repair the obstruction because word weight is invariant",
            ],
            "does_not_certify": [
                "absence of a morphism using delete/contract shadows beyond deletion-only cases",
                "absence of a morphism using non-edge coordinates or additional quotienting",
                "absence of a morphism using external Wu/spin or hexacode marking data",
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
            "target_golay_weight_test": artifact["target_golay_weight_test"],
            "deletion_shadow_analysis": artifact["deletion_shadow_analysis"],
        },
        "checks": artifact["checks"],
        "next_highest_yield_item": (
            "If the 31 -> 24 route is still pursued, leave deletion-only shadows and test "
            "marked delete/contract or non-edge quotient maps; the remaining map must change "
            "the code before the Golay weight test, not merely relabel coordinates."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": (
            "d20.proof_obligation.sector33_w24_marked_quotient_shadow_obstruction_manifest@1"
        ),
        "name": THEOREM_ID,
        "certification_tests": [
            "verify W24, per-edge rowspace, F4 row-lift, and sector33 dual inputs",
            "extract allowed Hamming weights from the certified self-dual W24 Golay code",
            "compute primal orthogonal shadows for 25 cocircuit-plus-one deletions",
            "compute dual rowspace shadows for the same 25 deletions",
            "verify every shadow contains a forbidden Golay weight",
            "record the coordinate-permutation invariance of the weight obstruction",
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
                "dual_compatible_cases": artifact["deletion_shadow_analysis"][
                    "shadow_summaries"
                ]["dual_rowspace_shadow"]["golay_weight_compatible_case_count"],
                "primal_compatible_cases": artifact["deletion_shadow_analysis"][
                    "shadow_summaries"
                ]["primal_orthogonal_shadow"]["golay_weight_compatible_case_count"],
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
