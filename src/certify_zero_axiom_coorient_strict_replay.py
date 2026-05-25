from __future__ import annotations

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_json
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_io import ROOT, cached_core_block, h_json


def validate_zero_axiom_coorient_strict_replay() -> Dict[str, Any]:
    candidates = [
        ROOT / "data/invariants/d20/theorems/zero_axiom_coorient_strict_replay/report.json",
    ]
    rec: dict[str, Any] | None = None
    for path in candidates:
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                rec = json.load(f)
            break
    if rec is None:
        cached = cached_core_block("zero_axiom_coorient_strict_replay")
        if cached is not None:
            rec = cached
        else:
            raise FileNotFoundError("missing D20 zero-axiom coorient strict replay certificate")

    if rec.get("status") != "D20_ZERO_AXIOM_COORIENT_STRICT_REPLAY_CERTIFIED":
        raise AssertionError("zero-axiom coorient strict replay status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("zero-axiom coorient strict replay checks did not pass")

    checks = rec.get("checks", {})
    if not checks or any(value is not True for value in checks.values()):
        raise AssertionError("zero-axiom coorient strict replay check map mismatch")

    derived = rec.get("derived", {})
    if derived.get("cache_certificate_sha256") != derived.get("fresh_certificate_sha256"):
        raise AssertionError("zero-axiom coorient strict replay certificate hash mismatch")
    if derived.get("cache_body_sha256") != derived.get("fresh_body_sha256"):
        raise AssertionError("zero-axiom coorient strict replay body hash mismatch")
    if derived.get("cache_canonical_payload_sha256") != derived.get("fresh_canonical_payload_sha256"):
        raise AssertionError("zero-axiom coorient strict replay canonical payload hash mismatch")
    if derived.get("cache_file_sha256") != derived.get("fresh_pretty_sha256"):
        raise AssertionError("zero-axiom coorient strict replay byte hash mismatch")
    if int(derived.get("cache_byte_length")) != int(derived.get("fresh_pretty_byte_length")):
        raise AssertionError("zero-axiom coorient strict replay byte length mismatch")
    if derived.get("cache_newline") not in {"CRLF", "LF"}:
        raise AssertionError("zero-axiom coorient strict replay newline marker mismatch")

    if derived.get("canonical_base") != [18, 67, 37]:
        raise AssertionError("zero-axiom coorient strict replay base mismatch")
    if int(derived.get("final_signature_count")) != 2576:
        raise AssertionError("zero-axiom coorient strict replay signature count mismatch")
    if int(derived.get("marker_integer_count")) != 9:
        raise AssertionError("zero-axiom coorient strict replay marker integer count mismatch")
    if derived.get("selected_generator_indices") != [1, 4, 192]:
        raise AssertionError("zero-axiom coorient strict replay selected generator indices mismatch")
    if derived.get("selected_generator_orders") != [2, 6, 2]:
        raise AssertionError("zero-axiom coorient strict replay selected generator orders mismatch")
    if int(derived.get("closed_action_order")) != 9216:
        raise AssertionError("zero-axiom coorient strict replay closed action order mismatch")
    if int(derived.get("word_presentation_closure_order")) != 9216:
        raise AssertionError("zero-axiom coorient strict replay word closure order mismatch")

    inputs = rec.get("inputs", {})
    cache_input = inputs.get("zero_axiom_coorient_cache", {})
    cache_path = ROOT / str(cache_input.get("path", ""))
    if not cache_path.exists():
        raise AssertionError("zero-axiom coorient strict replay cache file missing")
    if cache_input.get("sha256") != derived.get("cache_file_sha256"):
        raise AssertionError("zero-axiom coorient strict replay cache input hash mismatch")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("zero-axiom coorient strict replay theorem self hash mismatch")
    return rec
