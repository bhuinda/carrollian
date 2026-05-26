from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = "data/invariants/d20/theorems/d20_oriented_matroid_sector33_dual/report.json"
EXPECTED_DUAL_MATRIX_SHA256 = "a1ae4125242bae65b25cf8c5b320b34e56cccc383d9ab6715ac7cddbd5d5c10f"

INPUT_RELS = {
    "d20_json": "d20.json",
    "d20_oriented_matroid_sector33_extension_report": (
        "data/invariants/d20/theorems/d20_oriented_matroid_sector33_extension/report.json"
    ),
    "sector33_height_coherent_transport_report": (
        "data/invariants/d20/theorems/sector33_height_coherent_transport/report.json"
    ),
}


def _check_input_hash(inputs: dict[str, Any], key: str, rel_path: str) -> None:
    if inputs.get(key, {}).get("path") != rel_path:
        raise AssertionError(f"D20 oriented matroid sector33 dual {key} path mismatch")
    path = ROOT / rel_path
    if path.exists() and h_file(path) != inputs[key].get("sha256"):
        if key == "d20_json":
            with path.open("r", encoding="utf-8") as f:
                d20 = json.load(f)
            if d20.get("status") == "D20_CERTIFIED":
                return
        raise AssertionError(f"D20 oriented matroid sector33 dual {key} hash mismatch")


def validate_d20_oriented_matroid_sector33_dual() -> Dict[str, Any]:
    rec: dict[str, Any] | None = None
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            rec = json.load(f)
    else:
        cached = cached_core_block("d20_oriented_matroid_sector33_dual")
        if cached is not None:
            rec = cached
    if rec is None:
        raise FileNotFoundError("missing D20 oriented matroid sector33 dual certificate")

    if rec.get("status") != "D20_ORIENTED_MATROID_SECTOR33_DUAL_CERTIFIED":
        raise AssertionError("D20 oriented matroid sector33 dual status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("D20 oriented matroid sector33 dual checks did not pass")

    inputs = rec.get("inputs", {})
    for key, rel_path in INPUT_RELS.items():
        _check_input_hash(inputs, key, rel_path)

    derived = rec.get("derived", {})
    attachment = derived.get("sector33_height_attachment", {})
    if attachment.get("active_support") != [1, 2, 11, 21, 22]:
        raise AssertionError("D20 oriented matroid sector33 dual active support mismatch")
    if attachment.get("new_element_id") != 30 or attachment.get("new_element") != "e33":
        raise AssertionError("D20 oriented matroid sector33 dual e33 element mismatch")
    if attachment.get("sector33_dimension") != 2:
        raise AssertionError("D20 oriented matroid sector33 dual dimension mismatch")
    if attachment.get("sector33_transport_scalar") != -187392:
        raise AssertionError("D20 oriented matroid sector33 dual scalar mismatch")

    summary = derived.get("dual_summary", {})
    if summary.get("primal_ground_set_size") != 31:
        raise AssertionError("D20 oriented matroid sector33 dual ground-set mismatch")
    if summary.get("primal_rank") != 20 or summary.get("dual_rank") != 11:
        raise AssertionError("D20 oriented matroid sector33 dual rank mismatch")
    if summary.get("rank_sum") != 31:
        raise AssertionError("D20 oriented matroid sector33 dual rank-duality mismatch")
    if summary.get("nullspace_basis_rows") != 11 or summary.get("nullspace_basis_cols") != 31:
        raise AssertionError("D20 oriented matroid sector33 dual nullspace shape mismatch")
    if summary.get("nullspace_free_columns") != [18, 19, 20, 22, 23, 24, 26, 27, 28, 29, 30]:
        raise AssertionError("D20 oriented matroid sector33 dual free column mismatch")
    if summary.get("dual_matrix_sha256") != EXPECTED_DUAL_MATRIX_SHA256:
        raise AssertionError("D20 oriented matroid sector33 dual matrix hash mismatch")
    if h_json(summary.get("dual_matrix")) != summary.get("dual_matrix_sha256"):
        raise AssertionError("D20 oriented matroid sector33 dual matrix self hash mismatch")

    vector = derived.get("positive_primal_circuit_vector", [])
    if len(vector) != 31:
        raise AssertionError("D20 oriented matroid sector33 dual positive vector length mismatch")
    if [idx for idx, value in enumerate(vector) if value] != [1, 2, 11, 21, 22, 30]:
        raise AssertionError("D20 oriented matroid sector33 dual positive vector support mismatch")
    if [value for value in vector if value] != [1, 1, 1, 1, 1, 2]:
        raise AssertionError("D20 oriented matroid sector33 dual positive vector coefficient mismatch")
    if any(value != 0 for value in derived.get("positive_vector_kernel_image", [])):
        raise AssertionError("D20 oriented matroid sector33 dual kernel image mismatch")
    if derived.get("positive_vector_in_dual_rowspace") is not True:
        raise AssertionError("D20 oriented matroid sector33 dual rowspace mismatch")

    cocircuit = derived.get("dual_positive_cocircuit", {})
    if cocircuit.get("support") != [1, 2, 11, 21, 22, 30]:
        raise AssertionError("D20 oriented matroid sector33 dual cocircuit support mismatch")
    if cocircuit.get("support_is_dual_cocircuit") is not True:
        raise AssertionError("D20 oriented matroid sector33 dual cocircuit mismatch")
    if cocircuit.get("complement_is_dual_hyperplane") is not True:
        raise AssertionError("D20 oriented matroid sector33 dual hyperplane mismatch")
    if cocircuit.get("support_is_dual_circuit") is not False:
        raise AssertionError("D20 oriented matroid sector33 dual circuit overclaim")
    if cocircuit.get("dual_hyperplane_rank") != 10:
        raise AssertionError("D20 oriented matroid sector33 dual hyperplane rank mismatch")
    if cocircuit.get("is_positive") is not True:
        raise AssertionError("D20 oriented matroid sector33 dual positivity mismatch")
    if sorted(cocircuit.get("dual_addback_ranks", {}).values()) != [11, 11, 11, 11, 11, 11]:
        raise AssertionError("D20 oriented matroid sector33 dual addback rank mismatch")

    element_tests = derived.get("element_tests", {})
    if element_tests.get("e33_dual_singleton_cocircuit") is not False:
        raise AssertionError("D20 oriented matroid sector33 dual singleton cocircuit overclaim")
    if element_tests.get("old_ground_dual_hyperplane") is not False:
        raise AssertionError("D20 oriented matroid sector33 dual old-ground hyperplane overclaim")
    if element_tests.get("e33_dual_singleton_rank") != 1:
        raise AssertionError("D20 oriented matroid sector33 dual e33 rank mismatch")
    if element_tests.get("dual_total_rank") != 11:
        raise AssertionError("D20 oriented matroid sector33 dual total rank mismatch")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("D20 oriented matroid sector33 dual self hash mismatch")
    return rec


if __name__ == "__main__":
    rec = validate_d20_oriented_matroid_sector33_dual()
    print(rec["status"])
    print(rec["certificate_sha256"])
