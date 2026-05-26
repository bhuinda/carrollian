from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = "data/invariants/d20/theorems/d20_boundary_loop_step_atom_incidence/report.json"
INPUT_RELS = {
    "d20_edges_csv": "data/invariants/hcycle/subscript_Hcycle_d20_edges.csv",
    "d20_primitive_cycles_csv": "data/invariants/hcycle/subscript_Hcycle_primitive_cycles.csv",
    "boundary_to_loop_report": "data/invariants/d20/boundary_to_loop/report.json",
    "loop297_scattering_amplitude_lift_report": (
        "data/invariants/d20/theorems/loop297_scattering_amplitude_lift/report.json"
    ),
    "compact_amplitude_quotient_report": (
        "data/invariants/d20/theorems/compact_amplitude_quotient/report.json"
    ),
}
CSV_RELS = {
    "boundary_atom_step_incidence": (
        "data/invariants/d20/theorems/d20_boundary_loop_step_atom_incidence/"
        "boundary_atom_step_incidence.csv"
    ),
    "directed_pair_projection_step_atom_alignment": (
        "data/invariants/d20/theorems/d20_boundary_loop_step_atom_incidence/"
        "directed_pair_projection_step_atom_alignment.csv"
    ),
}
EXPECTED_MISSING_PAIRS = ["B+->V-", "B-->V+", "B-->V-", "S+->B+", "S-->B-"]


def _check_input_hash(inputs: dict[str, Any], key: str, rel_path: str) -> None:
    if inputs.get(key, {}).get("path") != rel_path:
        raise AssertionError(f"D20 boundary-loop step incidence {key} path mismatch")
    path = ROOT / rel_path
    if path.exists() and h_file(path) != inputs[key].get("sha256"):
        raise AssertionError(f"D20 boundary-loop step incidence {key} hash mismatch")


def validate_d20_boundary_loop_step_atom_incidence() -> Dict[str, Any]:
    rec: dict[str, Any] | None = None
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            rec = json.load(f)
    else:
        cached = cached_core_block("d20_boundary_loop_step_atom_incidence")
        if cached is not None:
            rec = cached
    if rec is None:
        raise FileNotFoundError("missing D20 boundary-loop step atom incidence certificate")

    if rec.get("schema") != "d20.theorem.d20_boundary_loop_step_atom_incidence":
        raise AssertionError("D20 boundary-loop step incidence schema mismatch")
    if rec.get("status") != "D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE_CERTIFIED":
        raise AssertionError("D20 boundary-loop step incidence status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("D20 boundary-loop step incidence checks did not pass")

    for key, rel_path in INPUT_RELS.items():
        _check_input_hash(rec.get("inputs", {}), key, rel_path)

    derived = rec.get("derived", {})
    summary = derived.get("incidence_summary", {})
    if summary.get("public_atom_count") != 20:
        raise AssertionError("D20 boundary-loop step incidence public atom count mismatch")
    if summary.get("d20_edge_count") != 30:
        raise AssertionError("D20 boundary-loop step incidence edge count mismatch")
    if summary.get("primitive_cycle_count") != 11:
        raise AssertionError("D20 boundary-loop step incidence primitive cycle count mismatch")
    if summary.get("boundary_directed_pair_projection_count") != 30:
        raise AssertionError("D20 boundary-loop step incidence directed pair count mismatch")
    if summary.get("compact_loop_step_atom_count") != 25:
        raise AssertionError("D20 boundary-loop step incidence step atom count mismatch")
    if summary.get("observed_directed_pair_count") != 25:
        raise AssertionError("D20 boundary-loop step incidence observed pair count mismatch")
    if summary.get("missing_directed_pair_count") != 5:
        raise AssertionError("D20 boundary-loop step incidence missing pair count mismatch")
    if summary.get("missing_directed_pairs_from_compact_step_atoms") != EXPECTED_MISSING_PAIRS:
        raise AssertionError("D20 boundary-loop step incidence missing pairs mismatch")
    if summary.get("incidence_matrix_shape") != [20, 25]:
        raise AssertionError("D20 boundary-loop step incidence matrix shape mismatch")
    if summary.get("rank_over_Q") != 19:
        raise AssertionError("D20 boundary-loop step incidence rank mismatch")
    if summary.get("nonunit_invariant_factors") != [2, 4, 4]:
        raise AssertionError("D20 boundary-loop step incidence Smith factor mismatch")
    if summary.get("zero_sum_boundary_lattice_index") != 32:
        raise AssertionError("D20 boundary-loop step incidence lattice index mismatch")
    if summary.get("quotient_reading") != "Z^20 / image = Z x Z/2 x Z/4 x Z/4":
        raise AssertionError("D20 boundary-loop step incidence quotient reading mismatch")

    public_rows = derived.get("public_atom_rows", [])
    if len(public_rows) != 20:
        raise AssertionError("D20 boundary-loop step incidence public rows mismatch")
    if h_json(public_rows) != derived.get("public_atom_rows_sha256"):
        raise AssertionError("D20 boundary-loop step incidence public rows hash mismatch")
    if [row.get("public_atom_id") for row in public_rows] != list(range(20)):
        raise AssertionError("D20 boundary-loop step incidence public row order mismatch")
    if any(row.get("native_domain") != "Lambda^3 H6" for row in public_rows):
        raise AssertionError("D20 boundary-loop step incidence public domain mismatch")

    pair_rows = derived.get("directed_pair_projection_step_atom_alignment_rows", [])
    if len(pair_rows) != 30:
        raise AssertionError("D20 boundary-loop step incidence pair alignment row count mismatch")
    if h_json(pair_rows) != derived.get("directed_pair_projection_step_atom_alignment_rows_sha256"):
        raise AssertionError("D20 boundary-loop step incidence pair alignment hash mismatch")
    missing = [row.get("directed_pair") for row in pair_rows if not row.get("observed_in_compact_step_atoms")]
    if missing != EXPECTED_MISSING_PAIRS:
        raise AssertionError("D20 boundary-loop step incidence pair alignment missing rows mismatch")
    for row in pair_rows:
        if row.get("observed_in_compact_step_atoms"):
            if row.get("boundary_projection_support") != row.get("step_atom_vector_support"):
                raise AssertionError("D20 boundary-loop step incidence support mismatch")
            if row.get("boundary_projection_coefficient_sum") != row.get(
                "step_atom_vector_coefficient_sum_signed"
            ):
                raise AssertionError("D20 boundary-loop step incidence coefficient mismatch")

    step_rows = derived.get("step_atom_boundary_incidence_rows", [])
    if len(step_rows) != 25:
        raise AssertionError("D20 boundary-loop step incidence step row count mismatch")
    if h_json(step_rows) != derived.get("step_atom_boundary_incidence_rows_sha256"):
        raise AssertionError("D20 boundary-loop step incidence step row hash mismatch")
    for atom_id, row in enumerate(step_rows):
        if row.get("step_atom_id") != atom_id:
            raise AssertionError("D20 boundary-loop step incidence step row order mismatch")
        vector = row.get("signed_vertex_vector_target_minus_source", [])
        if len(vector) != 20 or sum(vector) != 0:
            raise AssertionError("D20 boundary-loop step incidence signed vector mismatch")
        if row.get("signed_vertex_total") != 0:
            raise AssertionError("D20 boundary-loop step incidence signed total mismatch")
        if row.get("consistent_vector_data") is not True:
            raise AssertionError("D20 boundary-loop step incidence inconsistent vector data")
        if any(occurrence.get("tube_zero") is not True for occurrence in row.get("occurrences", [])):
            raise AssertionError("D20 boundary-loop step incidence nonzero tube occurrence")

    matrix = derived.get("boundary_atom_step_incidence_matrix", [])
    if len(matrix) != 20 or any(len(row) != 25 for row in matrix):
        raise AssertionError("D20 boundary-loop step incidence matrix dimensions mismatch")
    if h_json(matrix) != derived.get("boundary_atom_step_incidence_matrix_sha256"):
        raise AssertionError("D20 boundary-loop step incidence matrix hash mismatch")
    for col in range(25):
        if sum(matrix[row][col] for row in range(20)) != 0:
            raise AssertionError("D20 boundary-loop step incidence column sum mismatch")

    snf = derived.get("boundary_atom_step_incidence_smith_normal_form", {})
    if snf.get("diagonal") != [1] * 16 + [2, 4, 4]:
        raise AssertionError("D20 boundary-loop step incidence Smith diagonal mismatch")
    if snf.get("nonunit_invariant_factors") != [2, 4, 4]:
        raise AssertionError("D20 boundary-loop step incidence SNF nonunit mismatch")
    if snf.get("off_diagonal_nonzero") != 0 or snf.get("divisibility_chain_valid") is not True:
        raise AssertionError("D20 boundary-loop step incidence SNF form mismatch")

    generator_rows = derived.get("generator_boundary_closure_rows", [])
    if len(generator_rows) != 11:
        raise AssertionError("D20 boundary-loop step incidence generator row count mismatch")
    if h_json(generator_rows) != derived.get("generator_boundary_closure_rows_sha256"):
        raise AssertionError("D20 boundary-loop step incidence generator rows hash mismatch")
    if any(row.get("path_closes") is not True for row in generator_rows):
        raise AssertionError("D20 boundary-loop step incidence generator path mismatch")
    if any(row.get("signed_boundary_zero") is not True for row in generator_rows):
        raise AssertionError("D20 boundary-loop step incidence generator boundary mismatch")

    csv_hashes = derived.get("csv_artifact_hashes", {})
    for key, rel_path in CSV_RELS.items():
        if derived.get("csv_artifacts", {}).get(key) != rel_path:
            raise AssertionError(f"D20 boundary-loop step incidence {key} CSV path mismatch")
        if (ROOT / rel_path).exists() and h_file(ROOT / rel_path) != csv_hashes.get(key):
            raise AssertionError(f"D20 boundary-loop step incidence {key} CSV hash mismatch")

    checks = rec.get("checks", {})
    if not checks or any(value is not True for value in checks.values()):
        raise AssertionError("D20 boundary-loop step incidence check table mismatch")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("D20 boundary-loop step incidence self hash mismatch")

    return rec


if __name__ == "__main__":
    rec = validate_d20_boundary_loop_step_atom_incidence()
    print(rec["status"])
    print(rec["certificate_sha256"])
