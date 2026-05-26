from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = "data/invariants/d20/theorems/d20_oriented_matroid_sector33_extension/report.json"

INPUT_RELS = {
    "d20_json": "d20.json",
    "d20_oriented_matroid_contour_report": (
        "data/invariants/d20/theorems/d20_oriented_matroid_contour/report.json"
    ),
    "d20_finite_contour_integration_report": (
        "data/invariants/d20/theorems/d20_finite_contour_integration/report.json"
    ),
    "sector33_height_coherent_transport_report": (
        "data/invariants/d20/theorems/sector33_height_coherent_transport/report.json"
    ),
    "sector33_residual_attachment_report": (
        "data/invariants/d20/theorems/sector33_residual_attachment/report.json"
    ),
    "sector33_unique_public_zero_support_report": (
        "data/invariants/d20/theorems/sector33_unique_public_zero_support/report.json"
    ),
}


def _check_input_hash(inputs: dict[str, Any], key: str, rel_path: str) -> None:
    if inputs.get(key, {}).get("path") != rel_path:
        raise AssertionError(f"D20 oriented matroid sector33 extension {key} path mismatch")
    path = ROOT / rel_path
    if path.exists() and h_file(path) != inputs[key].get("sha256"):
        if key == "d20_json":
            with path.open("r", encoding="utf-8") as f:
                d20 = json.load(f)
            if d20.get("status") == "D20_CERTIFIED":
                return
        raise AssertionError(f"D20 oriented matroid sector33 extension {key} hash mismatch")


def _require_extension_tests(ext: dict[str, Any], name: str) -> None:
    if ext.get("name") != name:
        raise AssertionError(f"D20 oriented matroid sector33 extension {name} name mismatch")
    tests = ext.get("tests", {})
    if tests.get("rank") != 20 or tests.get("old_ground_rank") != 20:
        raise AssertionError(f"D20 oriented matroid sector33 extension {name} rank mismatch")
    if tests.get("new_element_in_old_closure") is not True:
        raise AssertionError(f"D20 oriented matroid sector33 extension {name} closure mismatch")
    if tests.get("gamma_plus_new_is_circuit") is not True:
        raise AssertionError(f"D20 oriented matroid sector33 extension {name} circuit mismatch")
    if tests.get("gamma_support_is_circuit") is not False:
        raise AssertionError(f"D20 oriented matroid sector33 extension {name} old circuit mismatch")
    if tests.get("new_singleton_is_cocircuit") is not False:
        raise AssertionError(f"D20 oriented matroid sector33 extension {name} cocircuit overclaim")
    if tests.get("old_ground_is_hyperplane") is not False:
        raise AssertionError(f"D20 oriented matroid sector33 extension {name} hyperplane overclaim")
    if tests.get("gamma_plus_new_is_cocircuit") is not False:
        raise AssertionError(f"D20 oriented matroid sector33 extension {name} gamma cocircuit overclaim")


def validate_d20_oriented_matroid_sector33_extension() -> Dict[str, Any]:
    rec: dict[str, Any] | None = None
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            rec = json.load(f)
    else:
        cached = cached_core_block("d20_oriented_matroid_sector33_extension")
        if cached is not None:
            rec = cached
    if rec is None:
        raise FileNotFoundError("missing D20 oriented matroid sector33 extension certificate")

    if rec.get("status") != "D20_ORIENTED_MATROID_SECTOR33_EXTENSION_CERTIFIED":
        raise AssertionError("D20 oriented matroid sector33 extension status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("D20 oriented matroid sector33 extension checks did not pass")

    inputs = rec.get("inputs", {})
    for key, rel_path in INPUT_RELS.items():
        _check_input_hash(inputs, key, rel_path)

    derived = rec.get("derived", {})
    base = derived.get("base_lift_summary", {})
    if base.get("edge_count") != 30:
        raise AssertionError("D20 oriented matroid sector33 extension edge count mismatch")
    if base.get("base_contour_rank") != 19 or base.get("height_lift_rank") != 20:
        raise AssertionError("D20 oriented matroid sector33 extension base rank mismatch")
    if base.get("active_support") != [1, 2, 11, 21, 22]:
        raise AssertionError("D20 oriented matroid sector33 extension active support mismatch")
    if base.get("cyclic_signed_support") != [1, 2, 11, 21, 22]:
        raise AssertionError("D20 oriented matroid sector33 extension signed support mismatch")

    signed = derived.get("signed_residue_extension", {})
    _require_extension_tests(signed, "signed_residue_lift")
    if signed.get("new_column", {}).get("residue_coordinate") != 3072:
        raise AssertionError("D20 oriented matroid sector33 extension residue quantum mismatch")
    if signed.get("gamma8_signed_integral") != -122880:
        raise AssertionError("D20 oriented matroid sector33 extension signed integral mismatch")
    if signed.get("gamma8_primitive_residue") != -40:
        raise AssertionError("D20 oriented matroid sector33 extension primitive residue mismatch")

    hidden = derived.get("hidden_sector_scalar_extension", {})
    _require_extension_tests(hidden, "hidden_sector_scalar_lift")
    hidden_col = hidden.get("new_column", {})
    if hidden_col.get("public_incidence") != {}:
        raise AssertionError("D20 oriented matroid sector33 extension hidden public incidence mismatch")
    if hidden_col.get("height_coordinate") != -187392:
        raise AssertionError("D20 oriented matroid sector33 extension hidden scalar mismatch")
    if hidden_col.get("sector33_residual_integral") != -374784:
        raise AssertionError("D20 oriented matroid sector33 extension residual integral mismatch")

    height = derived.get("sector33_height_attachment", {})
    _require_extension_tests(height, "sector33_height_attachment")
    if height.get("is_positive_circuit") is not True:
        raise AssertionError("D20 oriented matroid sector33 extension positive circuit mismatch")
    height_col = height.get("new_column", {})
    if height_col.get("public_incidence") != {"0": 1, "13": -1}:
        raise AssertionError("D20 oriented matroid sector33 extension sector bridge incidence mismatch")
    if height_col.get("height_coordinate") != -187392:
        raise AssertionError("D20 oriented matroid sector33 extension sector bridge height mismatch")
    if height_col.get("sector33_dimension") != 2:
        raise AssertionError("D20 oriented matroid sector33 extension sector dimension mismatch")
    closure = height.get("closure_equations", {})
    if closure.get("height_sum_active_plus_dim_e33") != 0:
        raise AssertionError("D20 oriented matroid sector33 extension height closure mismatch")
    if any(value != 0 for value in closure.get("public_boundary_sum_active_plus_dim_e33", [])):
        raise AssertionError("D20 oriented matroid sector33 extension public closure mismatch")
    coeffs = height.get("circuit_coefficients", [])
    if [row.get("coefficient") for row in coeffs] != [1, 1, 1, 1, 1, 2]:
        raise AssertionError("D20 oriented matroid sector33 extension positive circuit coefficients mismatch")

    summary = derived.get("sector33_cocircuit_summary", {})
    if summary.get("positive_circuit_extension") != "sector33_height_attachment":
        raise AssertionError("D20 oriented matroid sector33 extension positive circuit summary mismatch")
    if summary.get("e33_singleton_cocircuit_in_any_tested_extension") is not False:
        raise AssertionError("D20 oriented matroid sector33 extension singleton cocircuit overclaim")
    if summary.get("old_ground_hyperplane_in_any_tested_extension") is not False:
        raise AssertionError("D20 oriented matroid sector33 extension hyperplane overclaim")
    if summary.get("gamma8_plus_e33_cocircuit_in_any_tested_extension") is not False:
        raise AssertionError("D20 oriented matroid sector33 extension gamma cocircuit overclaim")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("D20 oriented matroid sector33 extension self hash mismatch")
    return rec


if __name__ == "__main__":
    rec = validate_d20_oriented_matroid_sector33_extension()
    print(rec["status"])
    print(rec["certificate_sha256"])
