from __future__ import annotations

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_json
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_io import ROOT, cached_core_block, h_json


def validate_zero_axiom_coorient_cache() -> Dict[str, Any]:
    candidates = [
        ROOT / "data/invariants/d20/theorems/zero_axiom_coorient_cache/report.json",
    ]
    rec: dict[str, Any] | None = None
    for path in candidates:
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                rec = json.load(f)
            break
    if rec is None:
        cached = cached_core_block("zero_axiom_coorient_cache")
        if cached is not None:
            rec = cached
        else:
            raise FileNotFoundError("missing D20 zero-axiom coorient cache certificate")

    if rec.get("status") != "D20_ZERO_AXIOM_COORIENT_CACHE_CERTIFIED":
        raise AssertionError("zero-axiom coorient cache status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("zero-axiom coorient cache checks did not pass")

    checks = rec.get("checks", {})
    if not checks or any(value is not True for value in checks.values()):
        raise AssertionError("zero-axiom coorient cache check map mismatch")

    derived = rec.get("derived", {})
    if derived.get("canonical_base") != [18, 67, 37]:
        raise AssertionError("zero-axiom coorient cache base mismatch")
    if int(derived.get("final_signature_count")) != 2576:
        raise AssertionError("zero-axiom coorient cache final signature count mismatch")
    if int(derived.get("marker_integer_count")) != 9:
        raise AssertionError("zero-axiom coorient cache marker integer count mismatch")
    if derived.get("selected_generator_indices") != [1, 4, 192]:
        raise AssertionError("zero-axiom coorient cache selected generator indices mismatch")
    if derived.get("selected_generator_orders") != [2, 6, 2]:
        raise AssertionError("zero-axiom coorient cache selected generator orders mismatch")
    if derived.get("selected_generator_base_images") != [
        [260, 120, 235],
        [669, 702, 720],
        [18, 151, 39],
    ]:
        raise AssertionError("zero-axiom coorient cache selected generator image mismatch")

    closed = derived.get("closed_action", {})
    if int(closed.get("degree")) != 2576:
        raise AssertionError("zero-axiom coorient cache closed action degree mismatch")
    if int(closed.get("group_order")) != 9216:
        raise AssertionError("zero-axiom coorient cache closed action order mismatch")

    word = derived.get("word_presentation", {})
    if int(word.get("closure_order")) != 9216:
        raise AssertionError("zero-axiom coorient cache word closure order mismatch")

    trace = derived.get("canonical_base_trace", [])
    if [row.get("step") for row in trace] != [1, 2, 3]:
        raise AssertionError("zero-axiom coorient cache trace step mismatch")
    if [row.get("unique_two_sided_signatures") for row in trace] != [284, 2274, 2576]:
        raise AssertionError("zero-axiom coorient cache trace signature mismatch")
    if [row.get("chosen_point") for row in trace] != [18, 67, 37]:
        raise AssertionError("zero-axiom coorient cache trace point mismatch")

    inputs = rec.get("inputs", {})
    source_rows = inputs.get("source_files", [])
    if len(source_rows) != 5:
        raise AssertionError("zero-axiom coorient cache source row count mismatch")
    if h_json(source_rows) != derived.get("source_file_rows_sha256"):
        raise AssertionError("zero-axiom coorient cache source row hash mismatch")
    if any(row.get("matches") is not True for row in source_rows):
        raise AssertionError("zero-axiom coorient cache source hash mismatch")

    cache_input = inputs.get("zero_axiom_coorient_cache", {})
    cache_path = ROOT / str(cache_input.get("path", ""))
    if not cache_path.exists():
        raise AssertionError("zero-axiom coorient cache file missing")
    cache_payload = json.loads(cache_path.read_text(encoding="utf-8"))
    cache_hash = cache_payload.get("certificate_sha256")
    cache_body = {key: value for key, value in cache_payload.items() if key != "certificate_sha256"}
    if h_json(cache_body) != cache_hash:
        raise AssertionError("zero-axiom coorient cache file self hash mismatch")
    if cache_hash != derived.get("cache_certificate_sha256"):
        raise AssertionError("zero-axiom coorient cache certificate hash mismatch")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("zero-axiom coorient cache theorem self hash mismatch")
    return rec
