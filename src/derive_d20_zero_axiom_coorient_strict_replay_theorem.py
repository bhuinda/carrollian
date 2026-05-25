from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

try:
    from .derive_d20_sandpile_critical_group_theorem import rel, sha_file, sha_json
    from .derive_zero_axiom_coorient import derive as derive_zero_axiom_coorient
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports `python src/derive_d20_zero_axiom_coorient_strict_replay_theorem.py`.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.derive_d20_sandpile_critical_group_theorem import rel, sha_file, sha_json
    from src.derive_zero_axiom_coorient import derive as derive_zero_axiom_coorient
    from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "zero_axiom_coorient_strict_replay"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
ZERO_AXIOM_CACHE = D20_INVARIANTS / "zero_axiom_coorient.json"
ZERO_AXIOM_CACHE_THEOREM = (
    D20_INVARIANTS / "theorems" / "zero_axiom_coorient_cache" / "report.json"
)


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


def pretty_text(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def cache_newline(cache_bytes: bytes) -> str:
    return "\r\n" if b"\r\n" in cache_bytes else "\n"


def pretty_bytes(payload: dict[str, Any], newline: str = "\n") -> bytes:
    text = pretty_text(payload)
    if newline != "\n":
        text = text.replace("\n", newline)
    return text.encode("utf-8")


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def self_hash_ok(payload: dict[str, Any]) -> bool:
    hfield = payload.get("certificate_sha256")
    body = {key: value for key, value in payload.items() if key != "certificate_sha256"}
    return isinstance(hfield, str) and sha_json(body) == hfield


def build_theorem() -> dict[str, Any]:
    cache = load_json(ZERO_AXIOM_CACHE)
    cache_theorem = load_json(ZERO_AXIOM_CACHE_THEOREM)
    fresh = derive_zero_axiom_coorient()

    cache_pretty = ZERO_AXIOM_CACHE.read_bytes()
    newline = cache_newline(cache_pretty)
    fresh_pretty = pretty_bytes(fresh, newline)
    cache_canonical_sha = sha_json(cache)
    fresh_canonical_sha = sha_json(fresh)
    cache_body = {key: value for key, value in cache.items() if key != "certificate_sha256"}
    fresh_body = {key: value for key, value in fresh.items() if key != "certificate_sha256"}

    base = fresh.get("canonical_base_derivation", {})
    marker = fresh.get("coorient_generator_marker", {})
    marker_derivation = marker.get("derivation", {})
    selected = marker_derivation.get("selected_generators", {})
    closed_action = marker_derivation.get("closed_action", {})
    word = fresh.get("word_presentation", {})

    checks = {
        "cache_theorem_is_certified": cache_theorem.get("status")
        == "D20_ZERO_AXIOM_COORIENT_CACHE_CERTIFIED"
        and cache_theorem.get("all_checks_pass") is True,
        "cache_status_is_pass": cache.get("status") == "D20_ZERO_AXIOM_COORIENT_REDUCTION_PASS",
        "fresh_status_is_pass": fresh.get("status") == "D20_ZERO_AXIOM_COORIENT_REDUCTION_PASS",
        "cache_self_hash_matches": self_hash_ok(cache),
        "fresh_self_hash_matches": self_hash_ok(fresh),
        "fresh_certificate_hash_matches_cache": fresh.get("certificate_sha256") == cache.get("certificate_sha256"),
        "fresh_body_hash_matches_cache_body_hash": sha_json(fresh_body) == sha_json(cache_body),
        "fresh_canonical_payload_matches_cache": fresh_canonical_sha == cache_canonical_sha,
        "fresh_pretty_bytes_match_cache_file_bytes": fresh_pretty == cache_pretty,
        "fresh_pretty_sha_matches_cache_file_sha": sha_bytes(fresh_pretty) == sha_file(ZERO_AXIOM_CACHE),
        "canonical_base_is_expected": base.get("base") == [18, 67, 37],
        "canonical_base_separates_all_points": base.get("separates_all_points") is True,
        "final_signature_count_is_2576": int(base.get("trace", [{}])[-1].get("unique_two_sided_signatures", -1)) == 2576,
        "marker_integer_count_is_9": int(marker.get("integer_count", -1)) == 9,
        "selected_generators_reconstruct": selected.get("reconstructed_matches_selected_generators") is True,
        "selected_generator_orders_match": selected.get("generator_orders") == [2, 6, 2],
        "closed_action_order_is_9216": int(closed_action.get("group_order", -1)) == 9216,
        "word_presentation_closure_order_is_9216": int(word.get("closure_order", -1)) == 9216,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_ZERO_AXIOM_COORIENT_STRICT_REPLAY_CERTIFIED"
        if all_checks_pass
        else "D20_ZERO_AXIOM_COORIENT_STRICT_REPLAY_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.zero_axiom_coorient_strict_replay",
        "status": status,
        "object": "d20",
        "claim": (
            "A fresh strict replay of the zero-axiom coorient reduction reproduces the "
            "stored cache byte-for-byte under the repository's sorted pretty JSON rendering, "
            "including the same cache certificate hash."
        ),
        "definition": {
            "strict_replay": (
                "The replay calls src.derive_zero_axiom_coorient:derive directly, bypassing "
                "the fast derive_d20 cache loader."
            ),
            "byte_for_byte_comparison": (
                "The fresh payload is rendered as json.dumps(payload, indent=2, sort_keys=True) "
                "plus a trailing newline, using the cache file's newline convention, and compared "
                "to data/invariants/d20/zero_axiom_coorient.json."
            ),
        },
        "inputs": {
            "zero_axiom_coorient_cache": {
                "path": rel(ZERO_AXIOM_CACHE),
                "sha256": sha_file(ZERO_AXIOM_CACHE),
            },
            "zero_axiom_coorient_cache_theorem": {
                "path": rel(ZERO_AXIOM_CACHE_THEOREM),
                "sha256": sha_file(ZERO_AXIOM_CACHE_THEOREM),
            },
        },
        "derived": {
            "cache_certificate_sha256": cache.get("certificate_sha256"),
            "fresh_certificate_sha256": fresh.get("certificate_sha256"),
            "cache_canonical_payload_sha256": cache_canonical_sha,
            "fresh_canonical_payload_sha256": fresh_canonical_sha,
            "cache_body_sha256": sha_json(cache_body),
            "fresh_body_sha256": sha_json(fresh_body),
            "cache_file_sha256": sha_file(ZERO_AXIOM_CACHE),
            "fresh_pretty_sha256": sha_bytes(fresh_pretty),
            "cache_newline": "CRLF" if newline == "\r\n" else "LF",
            "cache_byte_length": len(cache_pretty),
            "fresh_pretty_byte_length": len(fresh_pretty),
            "canonical_base": base.get("base"),
            "final_signature_count": base.get("trace", [{}])[-1].get("unique_two_sided_signatures"),
            "marker_integer_count": marker.get("integer_count"),
            "selected_generator_indices": selected.get("generator_indices"),
            "selected_generator_orders": selected.get("generator_orders"),
            "closed_action_order": closed_action.get("group_order"),
            "word_presentation_closure_order": word.get("closure_order"),
        },
        "interpretation": {
            "what_is_certified": (
                "The fast zero-axiom cache is not merely source-hash current; it is exactly "
                "the payload produced by a fresh strict replay in this workspace."
            ),
            "what_this_does_not_prove": (
                "This theorem does not make the fast core verifier rerun the replay. It records "
                "a completed replay witness that validators can check cheaply."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Move the strict replay into an optional slow verification mode so routine core "
            "verification stays fast while release checks can demand a fresh replay."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.zero_axiom_coorient_strict_replay_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "run a fresh src.derive_zero_axiom_coorient strict replay",
            "verify fresh and cached payload self hashes",
            "compare fresh canonical payload hash to cached canonical payload hash",
            "compare fresh sorted pretty JSON bytes to the cache file bytes",
            "record the replay result as a cheap-to-validate theorem report",
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
