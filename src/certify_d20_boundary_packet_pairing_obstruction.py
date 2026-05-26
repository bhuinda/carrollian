from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = "data/invariants/d20/theorems/d20_boundary_packet_pairing_obstruction/report.json"
INPUT_RELS = {
    "d20_boundary_loop_step_atom_incidence_report": (
        "data/invariants/d20/theorems/d20_boundary_loop_step_atom_incidence/report.json"
    ),
    "d20_packet_bridge_snf_obstruction_report": (
        "data/invariants/d20/theorems/d20_packet_bridge_snf_obstruction/report.json"
    ),
    "full_exposure_packet_propagation_graph_report": (
        "data/invariants/d20/theorems/full_exposure_packet_propagation_graph/report.json"
    ),
}


def _check_input_hash(inputs: dict[str, Any], key: str, rel_path: str) -> None:
    if inputs.get(key, {}).get("path") != rel_path:
        raise AssertionError(f"D20 boundary packet pairing obstruction {key} path mismatch")
    path = ROOT / rel_path
    if path.exists() and h_file(path) != inputs[key].get("sha256"):
        raise AssertionError(f"D20 boundary packet pairing obstruction {key} hash mismatch")


def validate_d20_boundary_packet_pairing_obstruction() -> Dict[str, Any]:
    rec: dict[str, Any] | None = None
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            rec = json.load(f)
    else:
        cached = cached_core_block("d20_boundary_packet_pairing_obstruction")
        if cached is not None:
            rec = cached
    if rec is None:
        raise FileNotFoundError("missing D20 boundary packet pairing obstruction certificate")

    if rec.get("schema") != "d20.theorem.d20_boundary_packet_pairing_obstruction":
        raise AssertionError("D20 boundary packet pairing obstruction schema mismatch")
    if rec.get("status") != "D20_BOUNDARY_PACKET_PAIRING_OBSTRUCTION_CERTIFIED":
        raise AssertionError("D20 boundary packet pairing obstruction status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("D20 boundary packet pairing obstruction checks did not pass")

    for key, rel_path in INPUT_RELS.items():
        _check_input_hash(rec.get("inputs", {}), key, rel_path)

    derived = rec.get("derived", {})
    summary = derived.get("obstruction_summary", {})
    if summary.get("public_atom_count") != 20:
        raise AssertionError("D20 boundary packet pairing obstruction public atom count mismatch")
    if summary.get("step_atom_column_count") != 25:
        raise AssertionError("D20 boundary packet pairing obstruction step atom count mismatch")
    if summary.get("packet_doublet_count") != 10:
        raise AssertionError("D20 boundary packet pairing obstruction packet doublet count mismatch")
    if summary.get("all_unordered_public_pair_count") != 190:
        raise AssertionError("D20 boundary packet pairing obstruction unordered pair count mismatch")
    if summary.get("raw_compatible_pair_count") != 0:
        raise AssertionError("D20 boundary packet pairing obstruction raw compatible pair overclaim")
    if summary.get("raw_perfect_matching_exists") is not False:
        raise AssertionError("D20 boundary packet pairing obstruction raw matching overclaim")
    if summary.get("minimal_scalar_with_any_compatible_pair") != 6:
        raise AssertionError("D20 boundary packet pairing obstruction any-pair scalar mismatch")
    if summary.get("minimal_scalar_with_perfect_matching") != 6:
        raise AssertionError("D20 boundary packet pairing obstruction matching scalar mismatch")
    if summary.get("boundary_incidence_nonunit_factors") != [2, 4, 4]:
        raise AssertionError("D20 boundary packet pairing obstruction boundary factors mismatch")
    if summary.get("boundary_lattice_exponent") != 4:
        raise AssertionError("D20 boundary packet pairing obstruction boundary exponent mismatch")
    if summary.get("joint_boundary_packet_scalar_lcm") != 12:
        raise AssertionError("D20 boundary packet pairing obstruction joint scalar mismatch")
    if summary.get("complement_pair_columns_passing_packet_snf") != []:
        raise AssertionError("D20 boundary packet pairing obstruction complement column overclaim")
    if summary.get("complement_pair_raw_failure_histogram", {}).get("pass") != 184:
        raise AssertionError("D20 boundary packet pairing obstruction complement pass count mismatch")

    raw_pairs = derived.get("raw_compatible_public_atom_pairs", [])
    if raw_pairs != []:
        raise AssertionError("D20 boundary packet pairing obstruction raw pairs should be empty")
    if h_json(raw_pairs) != derived.get("raw_compatible_public_atom_pairs_sha256"):
        raise AssertionError("D20 boundary packet pairing obstruction raw pair hash mismatch")

    scan_rows = derived.get("scalar_compatibility_scan_rows", [])
    if len(scan_rows) != 12:
        raise AssertionError("D20 boundary packet pairing obstruction scan row count mismatch")
    if h_json(scan_rows) != derived.get("scalar_compatibility_scan_rows_sha256"):
        raise AssertionError("D20 boundary packet pairing obstruction scan row hash mismatch")
    for idx, row in enumerate(scan_rows, start=1):
        if row.get("scalar") != idx:
            raise AssertionError("D20 boundary packet pairing obstruction scan scalar order mismatch")
        if idx <= 5:
            if row.get("compatible_pair_count") != 0 or row.get("perfect_matching_exists") is not False:
                raise AssertionError("D20 boundary packet pairing obstruction early scalar mismatch")
        if idx == 6:
            if row.get("compatible_pair_count") != 190 or row.get("perfect_matching_exists") is not True:
                raise AssertionError("D20 boundary packet pairing obstruction scalar 6 mismatch")
            if len(row.get("first_perfect_matching", [])) != 10:
                raise AssertionError("D20 boundary packet pairing obstruction scalar 6 matching mismatch")

    complement_rows = derived.get("canonical_complement_pair_rows", [])
    if len(complement_rows) != 10:
        raise AssertionError("D20 boundary packet pairing obstruction complement row count mismatch")
    if h_json(complement_rows) != derived.get("canonical_complement_pair_rows_sha256"):
        raise AssertionError("D20 boundary packet pairing obstruction complement hash mismatch")
    seen = sorted(atom for row in complement_rows for atom in row.get("public_atom_pair", []))
    if seen != list(range(20)):
        raise AssertionError("D20 boundary packet pairing obstruction complement coverage mismatch")

    packet_pairs = derived.get("packet_component_pairs", [])
    if len(packet_pairs) != 10:
        raise AssertionError("D20 boundary packet pairing obstruction packet pair count mismatch")
    if h_json(packet_pairs) != derived.get("packet_component_pairs_sha256"):
        raise AssertionError("D20 boundary packet pairing obstruction packet pair hash mismatch")

    checks = rec.get("checks", {})
    if not checks or any(value is not True for value in checks.values()):
        raise AssertionError("D20 boundary packet pairing obstruction check table mismatch")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("D20 boundary packet pairing obstruction self hash mismatch")

    return rec


if __name__ == "__main__":
    rec = validate_d20_boundary_packet_pairing_obstruction()
    print(rec["status"])
    print(rec["certificate_sha256"])
