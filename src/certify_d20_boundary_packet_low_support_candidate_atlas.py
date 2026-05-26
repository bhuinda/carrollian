from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = (
    "data/invariants/d20/theorems/d20_boundary_packet_low_support_candidate_atlas/report.json"
)
INPUT_RELS = {
    "d20_boundary_loop_step_atom_incidence_report": (
        "data/invariants/d20/theorems/d20_boundary_loop_step_atom_incidence/report.json"
    ),
    "d20_boundary_packet_row_normalization_obstruction_report": (
        "data/invariants/d20/theorems/d20_boundary_packet_row_normalization_obstruction/report.json"
    ),
    "d20_packet_bridge_snf_obstruction_report": (
        "data/invariants/d20/theorems/d20_packet_bridge_snf_obstruction/report.json"
    ),
}


def _check_input_hash(inputs: dict[str, Any], key: str, rel_path: str) -> None:
    if inputs.get(key, {}).get("path") != rel_path:
        raise AssertionError(f"D20 boundary low-support atlas {key} path mismatch")
    path = ROOT / rel_path
    if path.exists() and h_file(path) != inputs[key].get("sha256"):
        raise AssertionError(f"D20 boundary low-support atlas {key} hash mismatch")


def validate_d20_boundary_packet_low_support_candidate_atlas() -> Dict[str, Any]:
    rec: dict[str, Any] | None = None
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            rec = json.load(f)
    else:
        cached = cached_core_block("d20_boundary_packet_low_support_candidate_atlas")
        if cached is not None:
            rec = cached
    if rec is None:
        raise FileNotFoundError("missing D20 boundary packet low-support candidate atlas")

    if rec.get("schema") != "d20.theorem.d20_boundary_packet_low_support_candidate_atlas":
        raise AssertionError("D20 boundary low-support atlas schema mismatch")
    if rec.get("status") != "D20_BOUNDARY_PACKET_LOW_SUPPORT_CANDIDATE_ATLAS_CERTIFIED":
        raise AssertionError("D20 boundary low-support atlas status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("D20 boundary low-support atlas checks did not pass")

    for key, rel_path in INPUT_RELS.items():
        _check_input_hash(rec.get("inputs", {}), key, rel_path)

    definition = rec.get("definition", {})
    if definition.get("coefficient_set") != [-1, 1]:
        raise AssertionError("D20 boundary low-support atlas coefficient set mismatch")
    if definition.get("support_limit") != 2:
        raise AssertionError("D20 boundary low-support atlas support limit mismatch")
    if definition.get("packet_snf_image_test") != (
        "u = 0 mod 2, v = 0 mod 2, and u+v = 0 mod 6 on each packet doublet"
    ):
        raise AssertionError("D20 boundary low-support atlas image test mismatch")

    derived = rec.get("derived", {})
    summary = derived.get("low_support_summary", {})
    if summary.get("candidate_count") != 800:
        raise AssertionError("D20 boundary low-support atlas candidate count mismatch")
    if summary.get("candidate_support_size_histogram") != {"1": 40, "2": 760}:
        raise AssertionError("D20 boundary low-support atlas support histogram mismatch")
    if summary.get("even_image_candidate_count") != 12:
        raise AssertionError("D20 boundary low-support atlas even candidate count mismatch")
    if summary.get("even_image_support_size_histogram") != {"2": 12}:
        raise AssertionError("D20 boundary low-support atlas even support histogram mismatch")
    if summary.get("even_image_support_family_count") != 3:
        raise AssertionError("D20 boundary low-support atlas support family count mismatch")
    if summary.get("even_image_support_families") != [[0, 11], [6, 17], [14, 15]]:
        raise AssertionError("D20 boundary low-support atlas support families mismatch")
    if summary.get("even_image_span_rank_over_Q") != 6:
        raise AssertionError("D20 boundary low-support atlas image rank mismatch")
    if summary.get("compatible_doublet_count") != 6:
        raise AssertionError("D20 boundary low-support atlas doublet count mismatch")
    if summary.get("compatible_doublet_rank_histogram") != {"1": 6}:
        raise AssertionError("D20 boundary low-support atlas doublet rank mismatch")
    if summary.get("all_compatible_doublets_are_opposite_rows") is not True:
        raise AssertionError("D20 boundary low-support atlas opposite-row mismatch")
    if summary.get("full_packet_doublet_map_available") is not False:
        raise AssertionError("D20 boundary low-support atlas full-map overclaim")

    even_rows = derived.get("even_image_candidate_rows", [])
    if len(even_rows) != 12:
        raise AssertionError("D20 boundary low-support atlas even row count mismatch")
    if h_json(even_rows) != derived.get("even_image_candidate_rows_sha256"):
        raise AssertionError("D20 boundary low-support atlas even row hash mismatch")
    for row in even_rows:
        if row.get("support_size") != 2:
            raise AssertionError("D20 boundary low-support atlas support-size mismatch")
        if row.get("image_is_even") is not True:
            raise AssertionError("D20 boundary low-support atlas odd image row")
        if len(row.get("image_vector", [])) != 25:
            raise AssertionError("D20 boundary low-support atlas image length mismatch")
        if any(value % 2 != 0 for value in row.get("image_vector", [])):
            raise AssertionError("D20 boundary low-support atlas image parity mismatch")

    families = derived.get("even_image_support_family_rows", [])
    if len(families) != 3:
        raise AssertionError("D20 boundary low-support atlas family row count mismatch")
    if h_json(families) != derived.get("even_image_support_family_rows_sha256"):
        raise AssertionError("D20 boundary low-support atlas family hash mismatch")
    if [row.get("public_atom_support") for row in families] != [[0, 11], [6, 17], [14, 15]]:
        raise AssertionError("D20 boundary low-support atlas family support mismatch")
    if any(row.get("signed_candidate_count") != 4 for row in families):
        raise AssertionError("D20 boundary low-support atlas family signed count mismatch")

    doublets = derived.get("compatible_doublet_candidate_rows", [])
    if len(doublets) != 6:
        raise AssertionError("D20 boundary low-support atlas doublet row count mismatch")
    if h_json(doublets) != derived.get("compatible_doublet_candidate_rows_sha256"):
        raise AssertionError("D20 boundary low-support atlas doublet hash mismatch")
    for row in doublets:
        if row.get("passes_packet_snf_image") is not True:
            raise AssertionError("D20 boundary low-support atlas doublet pass mismatch")
        if row.get("right_is_negative_left") is not True:
            raise AssertionError("D20 boundary low-support atlas doublet sign mismatch")
        if row.get("doublet_rank_over_Q") != 1:
            raise AssertionError("D20 boundary low-support atlas doublet rank overclaim")

    checks = rec.get("checks", {})
    if not checks or any(value is not True for value in checks.values()):
        raise AssertionError("D20 boundary low-support atlas check table mismatch")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("D20 boundary low-support atlas self hash mismatch")

    return rec


if __name__ == "__main__":
    rec = validate_d20_boundary_packet_low_support_candidate_atlas()
    print(rec["status"])
    print(rec["certificate_sha256"])
