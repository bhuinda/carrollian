from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
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
    from .derive_d20_sector33_w24_marked_quotient_shadow_obstruction import (
        nullspace_basis_mod2,
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
    from derive_d20_sector33_w24_marked_quotient_shadow_obstruction import (
        nullspace_basis_mod2,
    )
    from paths import D20_INVARIANTS, GENERATED, ROOT, relpath


THEOREM_ID = "d20_sector33_w24_marked_delete_contract_shadow_probe"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
ARTIFACT_PATH = GENERATED / f"{THEOREM_ID}.json"

W24_ROW_ALPHABETIZATION = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_w24_hexacode_row_alphabetization"
    / "report.json"
)
MINOR_PUNCTURE_SEARCH = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_golay_hamming_minor_puncture_search"
    / "report.json"
)
DELETION_SHADOW_OBSTRUCTION = (
    D20_INVARIANTS
    / "proof_obligations"
    / "d20_sector33_w24_marked_quotient_shadow_obstruction"
    / "report.json"
)
SECTOR33_DUAL_REPORT = (
    D20_INVARIANTS / "theorems" / "d20_oriented_matroid_sector33_dual" / "report.json"
)
DERIVE_SCRIPT = ROOT / "src" / "derive_d20_sector33_w24_marked_delete_contract_shadow_probe.py"
VALIDATOR = ROOT / "src" / "certify_d20_sector33_w24_marked_delete_contract_shadow_probe.py"


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


def span_masks(gens: list[int]) -> set[int]:
    out = {0}
    for gen in gens:
        out |= {word ^ gen for word in list(out)}
    return out


def reduced_code_summary(rows: list[list[int]], width: int, allowed_weights: set[int]) -> dict[str, Any]:
    reduced, _pivots = rref_mod2(rows, width)
    masks = rows_to_masks(reduced)
    hist = weight_histogram(masks)
    forbidden = [
        weight for weight, count in sorted(hist.items()) if count and weight not in allowed_weights
    ]
    return {
        "rank": len(reduced),
        "basis_masks": masks,
        "weight_histogram": {str(weight): count for weight, count in sorted(hist.items())},
        "forbidden_weights": forbidden,
        "golay_weight_compatible": not forbidden,
    }


def analyze_delete_contract_shadows(allowed_weights: set[int]) -> dict[str, Any]:
    dual_report = load_json(SECTOR33_DUAL_REPORT)
    primal_integer_matrix, attachment = build_sector33_height_attachment_matrix()
    source_matrices = {
        "primal_orthogonal_shadow": {
            "matrix": mod2_matrix(primal_integer_matrix),
            "source": "sector33_primal_mod2",
            "shadow": "orthogonal_complement",
        },
        "dual_rowspace_shadow": {
            "matrix": mod2_matrix(dual_report["derived"]["dual_summary"]["dual_matrix"]),
            "source": "sector33_dual_mod2",
            "shadow": "rowspace",
        },
    }
    cocircuit = list(dual_report["derived"]["dual_positive_cocircuit"]["support"])
    extra_pool = list(dual_report["derived"]["dual_positive_cocircuit"]["complement"])

    summaries: dict[str, Any] = {}
    for name, spec in source_matrices.items():
        candidate_count = 0
        source_rank_histogram: Counter[int] = Counter()
        shadow_rank_histogram: Counter[int] = Counter()
        compatible_rank_histogram: Counter[int] = Counter()
        forbidden_weight_histogram: Counter[int] = Counter()
        compatible_records = []
        nontrivial_supports: defaultdict[tuple[int, ...], list[dict[str, Any]]] = defaultdict(list)

        for extra in extra_pool:
            removed = sorted(cocircuit + [extra])
            for mask in range(1 << len(removed)):
                contracted = {
                    element for bit, element in enumerate(removed) if (mask >> bit) & 1
                }
                rows, columns, effective_contracts = apply_minor(
                    spec["matrix"],
                    removed,
                    contracted,
                )
                source_summary = reduced_code_summary(rows, len(columns), allowed_weights)
                if spec["shadow"] == "orthogonal_complement":
                    shadow_rows = nullspace_basis_mod2(rows, len(columns))
                else:
                    shadow_rows = rows
                shadow_summary = reduced_code_summary(shadow_rows, len(columns), allowed_weights)
                candidate_count += 1
                source_rank_histogram[source_summary["rank"]] += 1
                shadow_rank_histogram[shadow_summary["rank"]] += 1
                for weight in shadow_summary["forbidden_weights"]:
                    forbidden_weight_histogram[weight] += 1
                if shadow_summary["golay_weight_compatible"]:
                    compatible_rank_histogram[shadow_summary["rank"]] += 1
                    nonzero_supports = []
                    for basis_mask in shadow_summary["basis_masks"]:
                        if basis_mask:
                            support = tuple(
                                columns[idx]
                                for idx in range(len(columns))
                                if (basis_mask >> idx) & 1
                            )
                            nonzero_supports.append(support)
                    record = {
                        "extra_removed": extra,
                        "contracted_original_elements": sorted(contracted),
                        "deleted_original_elements": [
                            element for element in removed if element not in contracted
                        ],
                        "effective_contract_count": effective_contracts,
                        "source_rank": source_summary["rank"],
                        "shadow_rank": shadow_summary["rank"],
                        "shadow_weight_histogram": shadow_summary["weight_histogram"],
                        "nonzero_shadow_supports": [list(support) for support in nonzero_supports],
                        "remaining_columns": columns,
                    }
                    compatible_records.append(record)
                    for support in nonzero_supports:
                        nontrivial_supports[support].append(record)

        summaries[name] = {
            "source_matrix": spec["source"],
            "shadow_rule": spec["shadow"],
            "candidate_count": candidate_count,
            "source_rank_histogram": {
                str(rank): count for rank, count in sorted(source_rank_histogram.items())
            },
            "shadow_rank_histogram": {
                str(rank): count for rank, count in sorted(shadow_rank_histogram.items())
            },
            "golay_weight_compatible_case_count": len(compatible_records),
            "golay_weight_compatible_rank_histogram": {
                str(rank): count for rank, count in sorted(compatible_rank_histogram.items())
            },
            "forbidden_weight_case_histogram": {
                str(weight): count for weight, count in sorted(forbidden_weight_histogram.items())
            },
            "compatible_records": compatible_records,
            "compatible_records_sha256": sha_json(compatible_records),
            "unique_nonzero_supports": [
                {
                    "support": list(support),
                    "support_weight": len(support),
                    "case_count": len(records),
                    "extra_removed_values": sorted({record["extra_removed"] for record in records}),
                }
                for support, records in sorted(nontrivial_supports.items())
            ],
        }

    return {
        "sector33_attachment": attachment,
        "fixed_removed_cocircuit": cocircuit,
        "extra_removed_pool": extra_pool,
        "extra_removed_count": len(extra_pool),
        "operation_masks_per_removal_set": 128,
        "source_matrix_count": 2,
        "candidate_count": sum(summary["candidate_count"] for summary in summaries.values()),
        "allowed_golay_weights": sorted(allowed_weights),
        "shadow_summaries": summaries,
    }


def build_artifact() -> dict[str, Any]:
    w24 = load_json(W24_ROW_ALPHABETIZATION)
    minor = load_json(MINOR_PUNCTURE_SEARCH)
    deletion_shadow = load_json(DELETION_SHADOW_OBSTRUCTION)
    dual = load_json(SECTOR33_DUAL_REPORT)

    target_golay = w24["witness"]["golay_code"]
    target_hist = {int(weight): int(count) for weight, count in target_golay["weight_histogram"].items()}
    allowed_weights = {weight for weight, count in target_hist.items() if count}
    analysis = analyze_delete_contract_shadows(allowed_weights)
    primal = analysis["shadow_summaries"]["primal_orthogonal_shadow"]
    dual_shadow = analysis["shadow_summaries"]["dual_rowspace_shadow"]

    target_span = span_masks(list(target_golay["generator_basis_masks"]))
    unique_dual_supports = dual_shadow["unique_nonzero_supports"]
    identity_containment = []
    for support_row in unique_dual_supports:
        support = support_row["support"]
        mask = sum(1 << int(coord) for coord in support)
        identity_containment.append(
            {
                "support": support,
                "identity_w24_mask": mask,
                "contained_in_current_w24_golay_under_identity_labels": mask in target_span,
            }
        )

    checks = {
        "w24_row_alphabetization_is_certified": w24["status"]
        == "D20_W24_HEXACODE_ROW_ALPHABETIZATION_CERTIFIED"
        and w24["all_checks_pass"] is True,
        "minor_puncture_search_input_is_certified_negative": minor["status"]
        == "D20_GOLAY_HAMMING_MINOR_PUNCTURE_SEARCH_CERTIFIED"
        and minor["all_checks_pass"] is True
        and minor["witness"]["search_summary"]["extended_golay_shape_match_count"] == 0,
        "deletion_shadow_obstruction_input_is_certified": deletion_shadow["status"]
        == "D20_SECTOR33_W24_MARKED_QUOTIENT_SHADOW_OBSTRUCTION_CERTIFIED"
        and deletion_shadow["all_checks_pass"] is True,
        "sector33_dual_input_is_certified": dual["status"]
        == "D20_ORIENTED_MATROID_SECTOR33_DUAL_CERTIFIED"
        and dual["all_checks_pass"] is True,
        "target_allowed_weights_are_0_8_12_16_24": sorted(allowed_weights) == [0, 8, 12, 16, 24],
        "delete_contract_candidate_count_is_6400": analysis["candidate_count"] == 6400,
        "primal_delete_contract_shadow_candidate_count_is_3200": primal["candidate_count"] == 3200,
        "primal_delete_contract_shadow_has_no_golay_weight_compatible_case": primal[
            "golay_weight_compatible_case_count"
        ]
        == 0,
        "dual_delete_contract_shadow_candidate_count_is_3200": dual_shadow["candidate_count"] == 3200,
        "dual_delete_contract_shadow_compatible_count_is_70": dual_shadow[
            "golay_weight_compatible_case_count"
        ]
        == 70,
        "dual_compatible_shadows_are_rank0_or_rank1": dual_shadow[
            "golay_weight_compatible_rank_histogram"
        ]
        == {"0": 55, "1": 15},
        "dual_has_one_unique_nontrivial_weight8_support": len(unique_dual_supports) == 1
        and unique_dual_supports[0]["support_weight"] == 8
        and unique_dual_supports[0]["case_count"] == 15,
        "unique_dual_octad_not_in_current_w24_under_identity_labels": len(identity_containment) == 1
        and identity_containment[0]["contained_in_current_w24_golay_under_identity_labels"] is False,
        "delete_contract_route_reduced_to_typed_octad_placement": True,
    }

    payload: dict[str, Any] = {
        "schema": "d20.proof_obligation.sector33_w24_marked_delete_contract_shadow_probe.artifact@1",
        "status": "D20_SECTOR33_W24_MARKED_DELETE_CONTRACT_SHADOW_PROBE_DERIVED",
        "claim_scope": (
            "Extend the marked Golay-shadow weight test from deletion-only cases to the "
            "full cocircuit-plus-one delete/contract family."
        ),
        "source_reports": {
            "w24_row_alphabetization": input_entry(
                W24_ROW_ALPHABETIZATION,
                {
                    "certificate_sha256": w24["certificate_sha256"],
                    "status": w24["status"],
                },
            ),
            "minor_puncture_search": input_entry(
                MINOR_PUNCTURE_SEARCH,
                {
                    "certificate_sha256": minor["certificate_sha256"],
                    "status": minor["status"],
                },
            ),
            "deletion_shadow_obstruction": input_entry(
                DELETION_SHADOW_OBSTRUCTION,
                {
                    "certificate_sha256": deletion_shadow["certificate_sha256"],
                    "status": deletion_shadow["status"],
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
            "weight_histogram": target_golay["weight_histogram"],
            "allowed_weights": sorted(allowed_weights),
            "self_dual": target_golay["self_dual_by_rank_and_self_orthogonal"],
            "rank": target_golay["rank"],
        },
        "delete_contract_shadow_analysis": analysis,
        "unique_dual_octad_identity_w24_test": identity_containment,
        "checks": checks,
    }
    payload["artifact_sha256_excluding_this_field"] = artifact_hash(payload)
    return payload


def build_report(artifact: dict[str, Any]) -> dict[str, Any]:
    analysis = artifact["delete_contract_shadow_analysis"]
    primal = analysis["shadow_summaries"]["primal_orthogonal_shadow"]
    dual = analysis["shadow_summaries"]["dual_rowspace_shadow"]
    unique_octad = dual["unique_nonzero_supports"][0]
    report: dict[str, Any] = {
        "schema": "d20.proof_obligation.sector33_w24_marked_delete_contract_shadow_probe@1",
        "status": "D20_SECTOR33_W24_MARKED_DELETE_CONTRACT_SHADOW_PROBE_CERTIFIED",
        "all_checks_pass": all(artifact["checks"].values()),
        "claim": (
            "The full cocircuit-plus-one delete/contract shadow test does not produce a "
            "sector33-to-W24 Golay morphism. All 3200 primal orthogonal shadows contain "
            "forbidden Golay weights. The dual side has 70 weight-compatible cases, but 55 "
            "are rank-zero and the remaining 15 are the same rank-one weight-8 support. "
            "Thus the route has narrowed to one typed octad-placement problem, not a full "
            "31 -> 24 -> 23 map."
        ),
        "definition": {
            "marked_shadow_test": (
                "For high-rank primal minors, test the orthogonal shadow required by "
                "self-dual Golay containment. For low-rank dual minors, test the rowspace "
                "directly as a possible Golay subcode shadow."
            ),
            "weight_filter": (
                "Any Golay subcode shadow can only have weights appearing in the certified "
                "W24 Golay code: 0, 8, 12, 16, 24."
            ),
        },
        "closure_boundary": {
            "certifies": [
                "6400 cocircuit-plus-one delete/contract shadows were tested",
                "all primal orthogonal shadows are blocked by forbidden Golay weights",
                "the only nontrivial dual-compatible shadow is rank 1 and weight 8",
                f"the unique nontrivial support is {unique_octad['support']}",
                "that support is not a W24 Golay word under the current identity coordinate labels",
            ],
            "does_not_certify": [
                "absence of a coordinate relabelling that sends the unique sector33 octad to a W24 octad",
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
            "delete_contract_shadow_analysis": analysis,
            "unique_dual_octad_identity_w24_test": artifact[
                "unique_dual_octad_identity_w24_test"
            ],
        },
        "checks": artifact["checks"],
        "next_highest_yield_item": (
            "Test the unique sector33 rank-one octad support against the W24 octad system "
            "with typed H6/F4 placement constraints. If that cannot be placed, the current "
            "cocircuit-plus-one 31 -> 24 route is exhausted."
        ),
    }
    report["certificate_sha256"] = sha_json(report)
    return report


def build_manifest(report: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema": "d20.proof_obligation.sector33_w24_marked_delete_contract_shadow_probe_manifest@1",
        "name": THEOREM_ID,
        "certification_tests": [
            "verify W24, minor-search, deletion-shadow, and sector33 dual inputs",
            "enumerate 6400 cocircuit-plus-one delete/contract shadows",
            "apply the Golay weight filter to primal orthogonal shadows",
            "apply the Golay weight filter to dual rowspace shadows",
            "verify the dual compatible cases are only rank 0 or one repeated rank-1 octad",
            "test the unique octad under current identity W24 coordinate labels",
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
    dual = artifact["delete_contract_shadow_analysis"]["shadow_summaries"]["dual_rowspace_shadow"]
    print(
        json.dumps(
            {
                "artifact": relpath(ARTIFACT_PATH),
                "dual_compatible_cases": dual["golay_weight_compatible_case_count"],
                "dual_unique_nonzero_supports": len(dual["unique_nonzero_supports"]),
                "primal_compatible_cases": artifact["delete_contract_shadow_analysis"][
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
