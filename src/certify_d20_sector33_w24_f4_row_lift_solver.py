from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_sector33_w24_f4_row_lift_solver import build_artifact
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_d20_sector33_w24_f4_row_lift_solver import build_artifact


THEOREM_ID = "d20_sector33_w24_f4_row_lift_solver"
ARTIFACT_REL = "generated/d20_sector33_w24_f4_row_lift_solver.json"
REPORT_REL = f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json"
MANIFEST_REL = f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json"
INDEX_REL = "data/invariants/d20/proof_obligations/index.json"

SOURCE_RELS = {
    "d20_json": "d20.json",
    "w24_row_alphabetization": (
        "data/invariants/d20/proof_obligations/d20_w24_hexacode_row_alphabetization/report.json"
    ),
    "typed_coordinate_search": (
        "data/invariants/d20/proof_obligations/d20_sector33_w24_typed_coordinate_search/report.json"
    ),
    "sector33_dual": "data/invariants/d20/theorems/d20_oriented_matroid_sector33_dual/report.json",
}


def _load_json(rel_path: str) -> dict[str, Any]:
    with (ROOT / rel_path).open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise AssertionError(f"{rel_path} is not a JSON object")
    return payload


def _self_hash(payload: dict[str, Any], field: str) -> str:
    tmp = dict(payload)
    tmp.pop(field, None)
    return h_json(tmp)


def _artifact_hash(payload: dict[str, Any]) -> str:
    tmp = dict(payload)
    tmp.pop("artifact_sha256_excluding_this_field", None)
    return h_json(tmp)


def _check_input_file(entry: dict[str, Any], rel_path: str, label: str) -> None:
    if entry.get("path") != rel_path:
        raise AssertionError(f"{label} input path mismatch")
    if h_file(ROOT / rel_path) != entry.get("sha256"):
        raise AssertionError(f"{label} input file hash mismatch")


def validate_d20_sector33_w24_f4_row_lift_solver() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != "d20.proof_obligation.sector33_w24_f4_row_lift_solver.artifact@1":
        raise AssertionError("sector33 W24 F4 row lift artifact schema mismatch")
    if artifact.get("status") != "D20_SECTOR33_W24_F4_ROW_LIFT_SOLVER_DERIVED":
        raise AssertionError("sector33 W24 F4 row lift artifact status mismatch")
    artifact_sha = _artifact_hash(artifact)
    if artifact_sha != artifact.get("artifact_sha256_excluding_this_field"):
        raise AssertionError("sector33 W24 F4 row lift artifact self hash mismatch")
    if build_artifact() != artifact:
        raise AssertionError("sector33 W24 F4 row lift artifact does not replay")

    checks = artifact.get("checks", {})
    required_checks = {
        "w24_row_alphabetization_is_certified",
        "typed_coordinate_search_input_is_certified",
        "sector33_dual_input_is_certified",
        "target_has_four_f4_rows_and_six_columns",
        "source_has_six_intrinsic_local_edge_states",
        "extra_removed_pool_has_twenty_five_edges",
        "row_lift_rule_count_per_extra_is_4096",
        "row_lift_rule_total_is_102400",
        "all_remaining_sets_have_24_edges",
        "no_intrinsic_state_to_f4_row_rule_is_balanced",
        "best_row_count_defect_is_positive",
        "golay_rowspace_test_blocked_before_basis_compare",
    }
    if set(checks) != required_checks or any(checks.get(key) is not True for key in required_checks):
        raise AssertionError("sector33 W24 F4 row lift check mismatch")

    target = artifact.get("target_w24_row_type", {})
    if len(target.get("f4_row_labels", [])) != 4:
        raise AssertionError("sector33 W24 F4 row lift target row count mismatch")
    if target.get("required_total_per_f4_row") != 6:
        raise AssertionError("sector33 W24 F4 row lift row target mismatch")

    search = artifact.get("row_lift_search", {})
    if len(search.get("local_states", [])) != 6:
        raise AssertionError("sector33 W24 F4 row lift local state count mismatch")
    if search.get("fixed_removed_cocircuit") != [1, 2, 11, 21, 22, 30]:
        raise AssertionError("sector33 W24 F4 row lift cocircuit mismatch")
    if search.get("fixed_removed_old_edges") != [1, 2, 11, 21, 22]:
        raise AssertionError("sector33 W24 F4 row lift old edge removal mismatch")
    if search.get("extra_removed_count") != 25 or len(search.get("extra_removed_pool", [])) != 25:
        raise AssertionError("sector33 W24 F4 row lift extra pool mismatch")
    if search.get("row_lift_rule_count_per_extra") != 4096:
        raise AssertionError("sector33 W24 F4 row lift per-extra rule count mismatch")
    if search.get("row_lift_rule_total") != 102400:
        raise AssertionError("sector33 W24 F4 row lift total rule count mismatch")
    if search.get("row_balanced_rule_count") != 0:
        raise AssertionError("sector33 W24 F4 row lift unexpectedly balanced")
    if int(search.get("best_l1_defect_from_six_per_f4_row", 0)) <= 0:
        raise AssertionError("sector33 W24 F4 row lift best defect mismatch")
    if len(search.get("per_extra_records", [])) != 25:
        raise AssertionError("sector33 W24 F4 row lift per-extra record count mismatch")
    if not all(record.get("remaining_edge_count") == 24 for record in search.get("per_extra_records", [])):
        raise AssertionError("sector33 W24 F4 row lift remaining length mismatch")
    if not all(record.get("balanced_row_lift_rule_count") == 0 for record in search.get("per_extra_records", [])):
        raise AssertionError("sector33 W24 F4 row lift per-extra balance mismatch")

    boundary = artifact.get("basis_compare_boundary", {})
    if boundary.get("attempted_compare") is not False:
        raise AssertionError("sector33 W24 F4 row lift basis boundary mismatch")

    for key, rel_path in SOURCE_RELS.items():
        _check_input_file(artifact.get("source_reports", {}).get(key, {}), rel_path, f"artifact {key}")

    if report.get("schema") != "d20.proof_obligation.sector33_w24_f4_row_lift_solver@1":
        raise AssertionError("sector33 W24 F4 row lift report schema mismatch")
    if report.get("status") != "D20_SECTOR33_W24_F4_ROW_LIFT_SOLVER_CERTIFIED":
        raise AssertionError("sector33 W24 F4 row lift report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("sector33 W24 F4 row lift report checks did not pass")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("sector33 W24 F4 row lift report self hash mismatch")
    artifact_input = report.get("inputs", {}).get("artifact", {})
    _check_input_file(artifact_input, ARTIFACT_REL, "report artifact")
    if artifact_input.get("artifact_sha256_excluding_this_field") != artifact_sha:
        raise AssertionError("sector33 W24 F4 row lift report artifact hash mismatch")
    witness = report.get("witness", {})
    if witness.get("target_w24_row_type") != artifact.get("target_w24_row_type"):
        raise AssertionError("sector33 W24 F4 row lift report target mismatch")
    if witness.get("row_lift_search") != artifact.get("row_lift_search"):
        raise AssertionError("sector33 W24 F4 row lift report search mismatch")
    if witness.get("basis_compare_boundary") != artifact.get("basis_compare_boundary"):
        raise AssertionError("sector33 W24 F4 row lift report boundary mismatch")
    if report.get("checks") != artifact.get("checks"):
        raise AssertionError("sector33 W24 F4 row lift report checks mismatch")
    for key, rel_path in SOURCE_RELS.items():
        _check_input_file(report.get("inputs", {}).get(key, {}), rel_path, f"report {key}")

    if manifest.get("schema") != "d20.proof_obligation.sector33_w24_f4_row_lift_solver_manifest@1":
        raise AssertionError("sector33 W24 F4 row lift manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("sector33 W24 F4 row lift manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact_sha:
        raise AssertionError("sector33 W24 F4 row lift manifest artifact hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("sector33 W24 F4 row lift manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("sector33 W24 F4 row lift registry entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("sector33 W24 F4 row lift registry report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("sector33 W24 F4 row lift registry status mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_sector33_w24_f4_row_lift_solver()
    print("D20 sector33 W24 F4 row lift solver proof obligation validated")
