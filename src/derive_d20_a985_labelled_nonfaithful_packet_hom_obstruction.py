from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

try:
    from src.paths import D20_INVARIANTS, ROOT
except ModuleNotFoundError:  # Supports direct script execution.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "d20_a985_labelled_nonfaithful_packet_hom_obstruction"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FIELD_PRIME = 1_000_003
RELATION_COUNT = 985
TARGET_BLOCK_COUNT = 10
TARGET_BLOCK_DIMENSION = 2

HALLOWEEN_NPZ = ROOT / "data" / "raw" / "Halloween.npz"
QUOTIENTS_NPZ = ROOT / "data" / "raw" / "quotients.npz"
FULL_MATRIX_UNIT_ARRAYS_NPZ = (
    D20_INVARIANTS
    / "theorems"
    / "tiny_pointer_a985_full_matrix_unit_orbital_coo"
    / "source_sector_matrix_units_raw_orbital_arrays.npz"
)
FULL_MATRIX_UNIT_COO_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "tiny_pointer_a985_full_matrix_unit_orbital_coo"
    / "report.json"
)
CANONICAL_SECTOR_MATRIX_UNITS_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "tiny_pointer_a985_canonical_sector_matrix_units"
    / "report.json"
)
CANONICAL_SECTOR_SUMMARY_CSV = (
    D20_INVARIANTS
    / "theorems"
    / "tiny_pointer_a985_canonical_sector_matrix_units"
    / "canonical_source_sector_matrix_unit_summary.csv"
)
FULL_PACKET_MATRIX_LIFT_REPORT = (
    D20_INVARIANTS / "theorems" / "d20_full_packet_matrix_lift" / "report.json"
)
PACKET_QUOTIENT_ACTION_PROBE_REPORT = (
    D20_INVARIANTS / "theorems" / "d20_packet_quotient_action_probe" / "report.json"
)
FOURIER_SCREEN0_TUBE_CENTRAL_ELEMENT_REPORT = (
    D20_INVARIANTS / "theorems" / "fourier_screen0_tube_central_element" / "report.json"
)
A985_MAT2_HOM_BOUNDARY_REPORT = (
    D20_INVARIANTS / "theorems" / "d20_a985_mat2_hom_boundary" / "report.json"
)

TARGETS = {
    "2I": np.asarray([[2, 0], [0, 2]], dtype=np.int64),
    "4S": np.asarray([[0, 4], [4, 0]], dtype=np.int64),
    "2I+4S": np.asarray([[2, 4], [4, 2]], dtype=np.int64),
}
SMALL_SECTORS = [5, 6, 7, 10, 13, 19, 20, 21, 22, 24, 25, 26, 32, 33, 34]


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} is not a JSON object")
    return payload


def input_record(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": sha_file(path)}


def signed_mod(value: int, mod: int = FIELD_PRIME) -> int:
    value %= mod
    return value if value <= mod // 2 else value - mod


def target_signature_rows() -> list[dict[str, Any]]:
    rows = []
    for name, matrix in TARGETS.items():
        matrix = matrix % FIELD_PRIME
        trace = int((matrix[0, 0] + matrix[1, 1]) % FIELD_PRIME)
        determinant = int(
            (matrix[0, 0] * matrix[1, 1] - matrix[0, 1] * matrix[1, 0])
            % FIELD_PRIME
        )
        rows.append(
            {
                "target": name,
                "matrix": matrix.astype(int).tolist(),
                "trace_mod": trace,
                "trace_signed": signed_mod(trace),
                "determinant_mod": determinant,
                "determinant_signed": signed_mod(determinant),
            }
        )
    return rows


def read_small_sector_rows() -> list[dict[str, Any]]:
    rows = []
    with CANONICAL_SECTOR_SUMMARY_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            sector = int(row["source_sector"])
            if sector not in SMALL_SECTORS:
                continue
            rows.append(
                {
                    "source_sector": sector,
                    "block_dimension": int(row["block_dimension"]),
                    "matrix_units": int(row["matrix_units"]),
                    "perennial_id": row["perennial_id"],
                    "coordinate_fingerprint_id": row["coordinate_fingerprint_id"],
                }
            )
    return rows


def regular_trace_coefficients(triples: np.ndarray) -> np.ndarray:
    trace = np.zeros(RELATION_COUNT, dtype=np.int64)
    mask = triples[:, 2] == triples[:, 1]
    np.add.at(trace, triples[mask, 0], triples[mask, 3] % FIELD_PRIME)
    return trace % FIELD_PRIME


def candidate_rows() -> list[dict[str, Any]]:
    quotients = np.load(QUOTIENTS_NPZ)
    q42 = np.asarray(quotients["q42_map"], dtype=np.int64)
    q12 = np.asarray(quotients["q12_map"], dtype=np.int64)
    rows: list[dict[str, Any]] = []
    for relation_id in range(RELATION_COUNT):
        rows.append(
            {
                "candidate_kind": "raw_relation",
                "candidate_id": relation_id,
                "relation_ids": [relation_id],
                "coefficients_mod": [1],
            }
        )
    for class_id in range(42):
        relation_ids = np.where(q42 == class_id)[0].astype(int).tolist()
        rows.append(
            {
                "candidate_kind": "q42_class_sum",
                "candidate_id": class_id,
                "relation_ids": relation_ids,
                "coefficients_mod": [1] * len(relation_ids),
            }
        )
    for class_id in range(12):
        relation_ids = np.where(q12 == class_id)[0].astype(int).tolist()
        rows.append(
            {
                "candidate_kind": "q12_class_sum",
                "candidate_id": class_id,
                "relation_ids": relation_ids,
                "coefficients_mod": [1] * len(relation_ids),
            }
        )
    tube = load_json(FOURIER_SCREEN0_TUBE_CENTRAL_ELEMENT_REPORT)
    for key in ("closed_loop_unit", "signed_object_unit"):
        entries = tube["derived"][key]["entries"]
        rows.append(
            {
                "candidate_kind": f"tube_{key}",
                "candidate_id": 0,
                "relation_ids": [int(rel_id) for rel_id, _coefficient in entries],
                "coefficients_mod": [int(coefficient) % FIELD_PRIME for _rel_id, coefficient in entries],
            }
        )
    return rows


def small_sector_relation_matrices() -> dict[int, np.ndarray]:
    arrays = np.load(FULL_MATRIX_UNIT_ARRAYS_NPZ)
    matrix_units = np.asarray(arrays["matrix_units"], dtype=np.int64) % FIELD_PRIME
    unit_sector = np.asarray(arrays["source_sector"], dtype=np.int64)
    unit_i = np.asarray(arrays["i"], dtype=np.int64)
    unit_j = np.asarray(arrays["j"], dtype=np.int64)
    triples = np.asarray(np.load(HALLOWEEN_NPZ)["triples"], dtype=np.int64)
    triples[:, 3] %= FIELD_PRIME
    alpha = triples[:, 0]
    beta = triples[:, 1]
    gamma = triples[:, 2]
    weights = triples[:, 3]
    regular_trace = regular_trace_coefficients(triples)
    sector_matrices: dict[int, np.ndarray] = {}
    for sector in SMALL_SECTORS:
        sector_units = np.where(unit_sector == sector)[0]
        block_dimension = int(max(unit_i[sector_units].max(), unit_j[sector_units].max()) + 1)
        entry_by_relation = np.zeros(
            (block_dimension, block_dimension, RELATION_COUNT), dtype=np.int64
        )
        inv_dimension = pow(block_dimension, -1, FIELD_PRIME)
        for row_i in range(block_dimension):
            for col_j in range(block_dimension):
                unit = np.where(
                    (unit_sector == sector)
                    & (unit_i == col_j)
                    & (unit_j == row_i)
                )[0]
                if len(unit) != 1:
                    raise AssertionError(
                        f"missing matrix unit E_{{{col_j},{row_i}}} for sector {sector}"
                    )
                unit_vector = matrix_units[int(unit[0])]
                support = np.nonzero(unit_vector)[0]
                coefficient_by_left = np.zeros(RELATION_COUNT, dtype=np.int64)
                coefficient_by_left[support] = unit_vector[support]
                mask = np.isin(alpha, support)
                contributions = (
                    coefficient_by_left[alpha[mask]]
                    * weights[mask]
                    * regular_trace[gamma[mask]]
                ) % FIELD_PRIME
                out = np.zeros(RELATION_COUNT, dtype=np.int64)
                np.add.at(out, beta[mask], contributions)
                entry_by_relation[row_i, col_j, :] = (out * inv_dimension) % FIELD_PRIME
        sector_matrices[sector] = entry_by_relation
    return sector_matrices


def evaluate_candidates(
    candidates: list[dict[str, Any]],
    sector_matrices: dict[int, np.ndarray],
) -> dict[str, Any]:
    target_rows = target_signature_rows()
    target_by_name = {row["target"]: row for row in target_rows}
    exact_matches = []
    signature_matches = []
    evaluated_count = 0
    per_target_summary = {
        name: {
            "target": name,
            "exact_match_count": 0,
            "signature_match_count": 0,
            "candidate_kinds_with_signature_match": [],
        }
        for name in TARGETS
    }
    for candidate in candidates:
        relation_ids = np.asarray(candidate["relation_ids"], dtype=np.int64)
        coefficients = np.asarray(candidate["coefficients_mod"], dtype=np.int64) % FIELD_PRIME
        for sector, relation_matrices in sector_matrices.items():
            block_dimension = int(relation_matrices.shape[0])
            matrix = np.tensordot(
                relation_matrices[:, :, relation_ids],
                coefficients,
                axes=([2], [0]),
            ) % FIELD_PRIME
            if block_dimension == 1:
                matrix_2 = np.asarray(
                    [[matrix[0, 0], 0], [0, matrix[0, 0]]],
                    dtype=np.int64,
                )
            else:
                matrix_2 = matrix
            evaluated_count += 1
            trace = int((matrix_2[0, 0] + matrix_2[1, 1]) % FIELD_PRIME)
            determinant = int(
                (
                    matrix_2[0, 0] * matrix_2[1, 1]
                    - matrix_2[0, 1] * matrix_2[1, 0]
                )
                % FIELD_PRIME
            )
            for target_name, target_matrix in TARGETS.items():
                target = target_by_name[target_name]
                exact = bool(np.array_equal(matrix_2 % FIELD_PRIME, target_matrix % FIELD_PRIME))
                signature = (
                    trace == target["trace_mod"]
                    and determinant == target["determinant_mod"]
                )
                if exact:
                    exact_matches.append(
                        {
                            "candidate_kind": candidate["candidate_kind"],
                            "candidate_id": candidate["candidate_id"],
                            "source_sector": sector,
                            "target": target_name,
                            "matrix_mod": matrix_2.astype(int).tolist(),
                        }
                    )
                    per_target_summary[target_name]["exact_match_count"] += 1
                if signature:
                    signature_matches.append(
                        {
                            "candidate_kind": candidate["candidate_kind"],
                            "candidate_id": candidate["candidate_id"],
                            "source_sector": sector,
                            "target": target_name,
                            "matrix_mod": matrix_2.astype(int).tolist(),
                            "trace_mod": trace,
                            "trace_signed": signed_mod(trace),
                            "determinant_mod": determinant,
                            "determinant_signed": signed_mod(determinant),
                        }
                    )
                    per_target_summary[target_name]["signature_match_count"] += 1
    for target_name, summary in per_target_summary.items():
        kinds = sorted(
            {
                row["candidate_kind"]
                for row in signature_matches
                if row["target"] == target_name
            }
        )
        summary["candidate_kinds_with_signature_match"] = kinds
    return {
        "evaluated_candidate_sector_pairs": evaluated_count,
        "exact_matches": exact_matches,
        "signature_matches": signature_matches,
        "per_target_summary": [
            per_target_summary[name] for name in ("2I", "4S", "2I+4S")
        ],
    }


def build_report() -> dict[str, Any]:
    canonical_units = load_json(CANONICAL_SECTOR_MATRIX_UNITS_REPORT)
    full_coo = load_json(FULL_MATRIX_UNIT_COO_REPORT)
    full_packet = load_json(FULL_PACKET_MATRIX_LIFT_REPORT)
    packet_probe = load_json(PACKET_QUOTIENT_ACTION_PROBE_REPORT)
    tube = load_json(FOURIER_SCREEN0_TUBE_CENTRAL_ELEMENT_REPORT)
    mat2_boundary = load_json(A985_MAT2_HOM_BOUNDARY_REPORT)
    small_rows = read_small_sector_rows()
    candidates = candidate_rows()
    candidate_family_rows = [
        {
            "candidate_kind": kind,
            "candidate_count": count,
        }
        for kind, count in sorted(
            Counter(row["candidate_kind"] for row in candidates).items()
        )
    ]
    sector_matrices = small_sector_relation_matrices()
    evaluation = evaluate_candidates(candidates, sector_matrices)
    exact_matches = evaluation["exact_matches"]
    signature_matches = evaluation["signature_matches"]
    signature_by_target = {
        row["target"]: row["signature_match_count"]
        for row in evaluation["per_target_summary"]
    }
    exact_by_target = {
        row["target"]: row["exact_match_count"]
        for row in evaluation["per_target_summary"]
    }
    checks = {
        "canonical_sector_matrix_units_certified": canonical_units.get("status")
        == "D20_TINY_POINTER_A985_CANONICAL_SECTOR_MATRIX_UNITS_CERTIFIED"
        and canonical_units.get("all_checks_pass") is True,
        "full_matrix_unit_coo_certified": full_coo.get("status")
        == "D20_TINY_POINTER_A985_FULL_MATRIX_UNIT_ORBITAL_COO_CERTIFIED"
        and full_coo.get("all_checks_pass") is True,
        "full_packet_matrix_lift_certified": full_packet.get("status")
        == "D20_FULL_PACKET_MATRIX_LIFT_CERTIFIED"
        and full_packet.get("all_checks_pass") is True,
        "packet_quotient_action_probe_certified": packet_probe.get("status")
        == "D20_PACKET_QUOTIENT_ACTION_PROBE_CERTIFIED"
        and packet_probe.get("all_checks_pass") is True,
        "tube_screen0_certified": tube.get("status")
        == "D20_FOURIER_SCREEN0_TUBE_CENTRAL_ELEMENT_CERTIFIED"
        and tube.get("all_checks_pass") is True,
        "mat2_hom_boundary_certified": mat2_boundary.get("status")
        == "D20_A985_MAT2_HOM_BOUNDARY_CERTIFIED"
        and mat2_boundary.get("all_checks_pass") is True,
        "small_sector_count_is_15": len(small_rows) == 15,
        "candidate_count_is_1041": len(candidates) == 1041,
        "evaluated_candidate_sector_pairs_is_15615": evaluation[
            "evaluated_candidate_sector_pairs"
        ]
        == 15615,
        "only_2i_has_matches": signature_by_target == {"2I": 9, "4S": 0, "2I+4S": 0},
        "exact_matches_equal_signature_matches": exact_matches == [
            {
                "candidate_kind": row["candidate_kind"],
                "candidate_id": row["candidate_id"],
                "source_sector": row["source_sector"],
                "target": row["target"],
                "matrix_mod": row["matrix_mod"],
            }
            for row in signature_matches
        ],
        "only_raw_relations_match_2i": sorted(
            {
                row["candidate_kind"]
                for row in signature_matches
                if row["target"] == "2I"
            }
        )
        == ["raw_relation"],
        "matching_2i_relation_ids_are_expected": [
            row["candidate_id"]
            for row in signature_matches
            if row["target"] == "2I"
        ]
        == [358, 362, 369, 370, 383, 385, 388, 389, 427],
        "all_2i_matches_are_sector34_scalar": all(
            row["source_sector"] == 34 and row["matrix_mod"] == [[2, 0], [0, 2]]
            for row in signature_matches
        ),
        "no_labelled_candidate_realizes_4s": signature_by_target["4S"] == 0,
        "no_labelled_candidate_realizes_2i_plus_4s": signature_by_target["2I+4S"] == 0,
        "no_q42_q12_or_tube_candidate_matches_any_target": all(
            not row["candidate_kind"].startswith(("q42", "q12", "tube"))
            for row in signature_matches
        ),
    }
    report = {
        "schema": "d20.theorem.d20_a985_labelled_nonfaithful_packet_hom_obstruction",
        "status": "D20_A985_LABELLED_NONFAITHFUL_PACKET_HOM_OBSTRUCTION_CERTIFIED",
        "object": "D20",
        "field_prime": FIELD_PRIME,
        "claim": (
            "Under the current certified A985 source-sector matrix-unit model and the "
            "current raw/q42/q12/tube labelled candidate set, no nonfaithful "
            "A985-to-Mat_2^10 packet homomorphism can realize the non-diagonal packet "
            "actions 4S or 2I+4S. The scan covers every certified 1D/2D source sector "
            "available to a 2D target component and every labelled raw relation, q42 "
            "class sum, q12 class sum, and screen-0 tube unit candidate. Only nine raw "
            "relations match the scalar 2I action, all through source sector 34; no "
            "candidate has even the conjugacy-invariant trace/determinant of 4S or "
            "2I+4S in any 1D/2D sector."
        ),
        "definition": {
            "nonfaithful_packet_component_model": (
                "A nonfaithful component Mat_2 target can only see a certified A985 "
                "source sector of dimension at most 2; larger source sectors cannot act "
                "on a two-dimensional target component."
            ),
            "labelled_candidate_set": (
                "The finite current-label set consists of raw A985 relation basis "
                "elements, q42 class sums, q12 class sums, the closed-loop tube unit, "
                "and the signed screen-0 tube object unit."
            ),
            "basis_change_invariant_test": (
                "Trace and determinant of the 2x2 component matrix are invariant under "
                "target-basis change; if they do not match a packet target block, no "
                "conjugate labelled operator can realize that target block."
            ),
        },
        "inputs": {
            "halloween_npz": input_record(HALLOWEEN_NPZ),
            "quotients_npz": input_record(QUOTIENTS_NPZ),
            "full_matrix_unit_arrays_npz": input_record(FULL_MATRIX_UNIT_ARRAYS_NPZ),
            "full_matrix_unit_coo_report": input_record(FULL_MATRIX_UNIT_COO_REPORT),
            "canonical_sector_matrix_units_report": input_record(
                CANONICAL_SECTOR_MATRIX_UNITS_REPORT
            ),
            "canonical_sector_summary_csv": input_record(CANONICAL_SECTOR_SUMMARY_CSV),
            "full_packet_matrix_lift_report": input_record(FULL_PACKET_MATRIX_LIFT_REPORT),
            "packet_quotient_action_probe_report": input_record(
                PACKET_QUOTIENT_ACTION_PROBE_REPORT
            ),
            "fourier_screen0_tube_central_element_report": input_record(
                FOURIER_SCREEN0_TUBE_CENTRAL_ELEMENT_REPORT
            ),
            "a985_mat2_hom_boundary_report": input_record(A985_MAT2_HOM_BOUNDARY_REPORT),
        },
        "derived": {
            "small_sector_rows": small_rows,
            "small_sector_rows_sha256": sha_json(small_rows),
            "candidate_family_rows": candidate_family_rows,
            "candidate_family_rows_sha256": sha_json(candidate_family_rows),
            "target_signature_rows": target_signature_rows(),
            "target_signature_rows_sha256": sha_json(target_signature_rows()),
            "evaluation_summary": {
                "candidate_count": len(candidates),
                "small_sector_count": len(small_rows),
                "evaluated_candidate_sector_pairs": evaluation[
                    "evaluated_candidate_sector_pairs"
                ],
                "exact_match_count": len(exact_matches),
                "signature_match_count": len(signature_matches),
                "exact_match_count_by_target": exact_by_target,
                "signature_match_count_by_target": signature_by_target,
                "non_diagonal_target_signature_match_count": signature_by_target["4S"]
                + signature_by_target["2I+4S"],
            },
            "per_target_summary": evaluation["per_target_summary"],
            "signature_match_rows": signature_matches,
            "signature_match_rows_sha256": sha_json(signature_matches),
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "closure_boundary": {
            "certifies": [
                "no current-label raw/q42/q12/tube candidate realizes 4S in any certified 1D/2D A985 source sector",
                "no current-label raw/q42/q12/tube candidate realizes 2I+4S in any certified 1D/2D A985 source sector",
                "therefore no current-label nonfaithful A985 packet homomorphism can realize the certified non-diagonal packet action",
            ],
            "does_not_certify": [
                "nonexistence of arbitrary unlabelled linear-combination A985 elements that synthesize a 2x2 matrix inside a chosen sector",
                "a rational Q lift beyond the current finite-field matrix-unit certificate",
                "future externally supplied label sets or packet-column assignments not present in the current certificates",
            ],
        },
        "next_highest_yield_item": (
            "If the goal is a fully rational theorem, lift the relevant small-sector "
            "matrix-unit traces from the finite-field certificate to a rational row "
            "certificate, or explicitly demote rational lift as outside the current "
            "labelled packet bridge boundary."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {key: value for key, value in report.items() if key != "certificate_sha256"}
    )
    return report


def write_report(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_report()
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "schema": "d20.theorem.d20_a985_labelled_nonfaithful_packet_hom_obstruction_manifest",
        "status": report["status"],
        "name": THEOREM_ID,
        "artifacts": {
            "report": rel(out_dir / "report.json"),
            "manifest": rel(out_dir / "manifest.json"),
        },
        "report_sha256": report["certificate_sha256"],
        "inputs": report["inputs"],
        "purpose": [
            "certify the current-label nonfaithful A985 packet homomorphism obstruction",
            "test all certified 1D/2D source-sector images of raw/q42/q12/tube labels",
            "separate labelled packet no-go from arbitrary unlabelled linear combinations",
        ],
    }
    manifest["manifest_sha256"] = sha_json(
        {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    )
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> None:
    report = write_report()
    print(report["status"])
    print(report["certificate_sha256"])


if __name__ == "__main__":
    main()
