from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
import sys
from pathlib import Path
from typing import Any

try:
    from .derive_d20_sandpile_critical_group_theorem import rel, sha_file, sha_json
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports `python src/derive_d20_zero_axiom_coorient_cache_theorem.py`.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.derive_d20_sandpile_critical_group_theorem import rel, sha_file, sha_json
    from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "zero_axiom_coorient_cache"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
ZERO_AXIOM_CACHE = D20_INVARIANTS / "zero_axiom_coorient.json"


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


def cache_self_hash_ok(cache: dict[str, Any]) -> bool:
    hfield = cache.get("certificate_sha256")
    body = {key: value for key, value in cache.items() if key != "certificate_sha256"}
    return isinstance(hfield, str) and sha_json(body) == hfield


def source_file_rows(cache: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    source_files = cache.get("source_files", {})
    if not isinstance(source_files, dict):
        return rows
    for source_id, entry in sorted(source_files.items()):
        if not isinstance(entry, dict):
            continue
        rel_path = entry.get("path")
        recorded = entry.get("sha256")
        exists = isinstance(rel_path, str) and (ROOT / rel_path).exists()
        actual = sha_file(ROOT / rel_path) if exists else None
        rows.append(
            {
                "source_id": source_id,
                "path": rel_path,
                "exists": exists,
                "recorded_sha256": recorded,
                "actual_sha256": actual,
                "matches": exists and isinstance(recorded, str) and recorded == actual,
            }
        )
    return rows


def build_theorem() -> dict[str, Any]:
    cache = load_json(ZERO_AXIOM_CACHE)
    base = cache.get("canonical_base_derivation", {})
    marker = cache.get("coorient_generator_marker", {})
    marker_derivation = marker.get("derivation", {})
    closed_action = marker_derivation.get("closed_action", {})
    selected = marker_derivation.get("selected_generators", {})
    word = cache.get("word_presentation", {})
    source_rows = source_file_rows(cache)
    trace = base.get("trace", [])
    trace_last = trace[-1] if trace else {}

    checks = {
        "cache_status_is_pass": cache.get("status") == "D20_ZERO_AXIOM_COORIENT_REDUCTION_PASS",
        "cache_self_hash_matches": cache_self_hash_ok(cache),
        "all_source_files_exist_and_match": all(row["matches"] for row in source_rows) and len(source_rows) == 5,
        "canonical_base_is_expected": base.get("base") == [18, 67, 37],
        "stored_base_matches_canonical_base": base.get("matches_stored_canonical_base") is True,
        "canonical_base_is_not_seed": base.get("base_is_seed") is False,
        "canonical_base_separates_all_points": base.get("separates_all_points") is True,
        "trace_has_three_steps": [row.get("step") for row in trace] == [1, 2, 3],
        "trace_final_signature_count_is_2576": int(trace_last.get("unique_two_sided_signatures", -1)) == 2576,
        "marker_integer_count_is_9": int(marker.get("integer_count", -1)) == 9,
        "marker_is_not_seed": marker.get("is_still_seed") is False,
        "marker_uses_generated_relation_body": marker_derivation.get("uses_pre_a985_generated_relation_body") is True,
        "marker_does_not_use_supplied_relation_partition": marker_derivation.get("uses_supplied_relation_partition") is False,
        "selected_generators_reconstruct": selected.get("reconstructed_matches_selected_generators") is True,
        "selected_generator_orders_match": selected.get("generator_orders") == [2, 6, 2],
        "closed_action_order_is_9216": int(closed_action.get("group_order", -1)) == 9216,
        "word_presentation_closure_order_is_9216": int(word.get("closure_order", -1)) == 9216,
        "full_zero_axiom_constructor_boundary_recorded": cache.get("full_zero_axiom_constructor") is False,
        "zero_axiom_reduction_recorded": cache.get("zero_axiom_reduction") is True,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_ZERO_AXIOM_COORIENT_CACHE_CERTIFIED"
        if all_checks_pass
        else "D20_ZERO_AXIOM_COORIENT_CACHE_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.zero_axiom_coorient_cache",
        "status": status,
        "object": "d20",
        "claim": (
            "The stored zero-axiom coorient cache is a checked finite certificate boundary: "
            "its source hashes match the current workspace, its self hash is valid, the "
            "canonical base [18,67,37] separates all 2576 points, and the derived lift closes "
            "to order 9216."
        ),
        "definition": {
            "cache_path": rel(ZERO_AXIOM_CACHE),
            "cache_policy": (
                "d20 derivation may load this cache when the recorded source hashes match; "
                "otherwise it must recompute the zero-axiom coorient reduction."
            ),
            "certified_boundary": (
                "This is a finite cache-validity certificate, not a claim that the full "
                "zero-axiom constructor is primitive input."
            ),
        },
        "inputs": {
            "zero_axiom_coorient_cache": {
                "path": rel(ZERO_AXIOM_CACHE),
                "sha256": sha_file(ZERO_AXIOM_CACHE),
            },
            "source_files": source_rows,
        },
        "derived": {
            "cache_certificate_sha256": cache.get("certificate_sha256"),
            "canonical_base": base.get("base"),
            "canonical_base_trace": trace,
            "final_signature_count": trace_last.get("unique_two_sided_signatures"),
            "marker_integer_count": marker.get("integer_count"),
            "selected_generator_indices": selected.get("generator_indices"),
            "selected_generator_orders": selected.get("generator_orders"),
            "selected_generator_base_images": selected.get("generator_base_images"),
            "generator_permutations_sha256": selected.get("generator_permutations_sha256"),
            "closed_action": {
                "degree": closed_action.get("degree"),
                "group_order": closed_action.get("group_order"),
                "action_sha256": closed_action.get("action_sha256"),
            },
            "word_presentation": {
                "generators": word.get("generators"),
                "closure_order": word.get("closure_order"),
                "presentation_sha256": word.get("presentation_sha256"),
            },
            "source_file_rows_sha256": sha_json(source_rows),
        },
        "interpretation": {
            "what_is_certified": (
                "The cached zero-axiom coorient payload is current with respect to its stated "
                "finite source files and can be used by derive_d20 without repeating the slow "
                "matrix reconstruction step."
            ),
            "what_this_does_not_prove": (
                "This cache certificate does not replace strict-scratch reconstruction; it "
                "documents the fast path boundary and its invalidation rule."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Add an explicit strict-scratch theorem that compares a fresh zero-axiom "
            "recomputation against this cache certificate byte-for-byte."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.zero_axiom_coorient_cache_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify the zero-axiom cache self hash",
            "verify every recorded source-file hash against the current workspace",
            "verify the canonical base and 2576-point separation result",
            "verify the selected generator data and 9216-element closure order",
            "record the cache invalidation policy used by derive_d20",
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
