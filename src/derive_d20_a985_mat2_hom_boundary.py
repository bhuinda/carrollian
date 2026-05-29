from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from src.paths import D20_INVARIANTS, ROOT
except ModuleNotFoundError:  # Supports direct script execution.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "d20_a985_mat2_hom_boundary"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

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
FULL_MATRIX_UNIT_COO_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "tiny_pointer_a985_full_matrix_unit_orbital_coo"
    / "report.json"
)
FULL_PACKET_MATRIX_LIFT_REPORT = (
    D20_INVARIANTS / "theorems" / "d20_full_packet_matrix_lift" / "report.json"
)
A985_DIRECT_PACKET_BRIDGE_OBSTRUCTION_REPORT = (
    D20_INVARIANTS
    / "theorems"
    / "d20_a985_direct_packet_bridge_obstruction"
    / "report.json"
)

TARGET_BLOCK_COUNT = 10
TARGET_BLOCK_DIMENSION = 2
TARGET_ALGEBRA_DIMENSION = TARGET_BLOCK_COUNT * TARGET_BLOCK_DIMENSION**2
EXPECTED_BLOCK_DIMENSION_HISTOGRAM = {
    "1": 7,
    "2": 8,
    "3": 4,
    "4": 8,
    "5": 4,
    "6": 2,
    "8": 1,
    "9": 1,
    "10": 2,
    "11": 1,
    "12": 1,
}


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


def read_sector_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with CANONICAL_SECTOR_SUMMARY_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rows.append(
                {
                    "source_sector": int(row["source_sector"]),
                    "block_dimension": int(row["block_dimension"]),
                    "matrix_units": int(row["matrix_units"]),
                    "expected_matrix_units": int(row["expected_matrix_units"]),
                    "diagonal_units": int(row["diagonal_units"]),
                    "expected_diagonal_units": int(row["expected_diagonal_units"]),
                    "off_diagonal_units": int(row["off_diagonal_units"]),
                    "expected_off_diagonal_units": int(row["expected_off_diagonal_units"]),
                    "coefficient_source": row["coefficient_source"],
                    "canonical_gauge_status": row["canonical_gauge_status"],
                    "perennial_id": row["perennial_id"],
                    "coordinate_fingerprint_id": row["coordinate_fingerprint_id"],
                }
            )
    return rows


def histogram(values: list[int]) -> dict[str, int]:
    counts = Counter(values)
    return {str(key): int(counts[key]) for key in sorted(counts)}


def small_block_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        if row["block_dimension"] > TARGET_BLOCK_DIMENSION:
            continue
        out.append(
            {
                "source_sector": row["source_sector"],
                "block_dimension": row["block_dimension"],
                "matrix_units": row["matrix_units"],
                "mat2_component_embedding_shape": (
                    "scalar_to_2x2_identity"
                    if row["block_dimension"] == 1
                    else "2x2_block_identity"
                ),
                "perennial_id": row["perennial_id"],
                "coordinate_fingerprint_id": row["coordinate_fingerprint_id"],
            }
        )
    return out


def build_report() -> dict[str, Any]:
    canonical_units = load_json(CANONICAL_SECTOR_MATRIX_UNITS_REPORT)
    full_coo = load_json(FULL_MATRIX_UNIT_COO_REPORT)
    full_packet = load_json(FULL_PACKET_MATRIX_LIFT_REPORT)
    direct_bridge = load_json(A985_DIRECT_PACKET_BRIDGE_OBSTRUCTION_REPORT)
    sector_rows = read_sector_rows()
    small_rows = small_block_rows(sector_rows)
    block_hist = histogram([row["block_dimension"] for row in sector_rows])
    source_algebra_dimension = sum(row["matrix_units"] for row in sector_rows)
    diagonal_dimension = sum(row["diagonal_units"] for row in sector_rows)
    larger_sector_count = sum(
        1 for row in sector_rows if row["block_dimension"] > TARGET_BLOCK_DIMENSION
    )
    direct_summary = direct_bridge["derived"]["direct_bridge_summary"]
    dimension_summary = {
        "source_sector_count": len(sector_rows),
        "source_algebra_dimension": source_algebra_dimension,
        "source_diagonal_dimension": diagonal_dimension,
        "target_block_count": TARGET_BLOCK_COUNT,
        "target_block_dimension": TARGET_BLOCK_DIMENSION,
        "target_algebra": "Mat_2(Q)^10",
        "target_algebra_dimension": TARGET_ALGEBRA_DIMENSION,
        "faithful_full_a985_embedding_possible_by_dimension": (
            source_algebra_dimension <= TARGET_ALGEBRA_DIMENSION
        ),
        "small_block_sector_count": len(small_rows),
        "small_block_sector_capacity_at_least_target_blocks": len(small_rows)
        >= TARGET_BLOCK_COUNT,
        "larger_than_mat2_sector_count": larger_sector_count,
        "block_dimension_histogram": block_hist,
    }
    hom_boundary = {
        "faithful_full_a985_to_mat2_power_10": "refuted_by_dimension",
        "literal_current_packet_label_map": "refuted_by_direct_restriction_certificate",
        "unconstrained_nonfaithful_full_domain_homomorphism": (
            "not_refuted_by_current_evidence"
        ),
        "reason_unconstrained_no_go_is_too_strong": (
            "The certified A985 block profile contains 15 source sectors of dimension 1 or "
            "2, enough to feed ten 2x2 target components as an abstract nonfaithful "
            "quotient shape. The current source matrix-unit evidence is finite-field "
            "block data, so this boundary does not certify a rational Q homomorphism; it "
            "only prevents upgrading the dimension argument into a universal no-go."
        ),
        "current_label_constraint_needed_for_a_real_no_go": (
            "A valid packet theorem must supply explicit A985/tube/q42/q12-to-packet "
            "columns, or a certificate that every label-compatible column assignment "
            "violates preservation, Mat_2(Q)^10 landing, target-action matching, or "
            "multiplication."
        ),
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
        "direct_packet_bridge_obstruction_certified": direct_bridge.get("status")
        == "D20_A985_DIRECT_PACKET_BRIDGE_OBSTRUCTION_CERTIFIED"
        and direct_bridge.get("all_checks_pass") is True,
        "sector_rows_count_is_39": len(sector_rows) == 39,
        "matrix_units_sum_to_985": source_algebra_dimension == 985,
        "diagonal_units_sum_to_159": diagonal_dimension == 159,
        "block_dimension_histogram_matches": block_hist
        == EXPECTED_BLOCK_DIMENSION_HISTOGRAM,
        "target_mat2_power_10_dimension_is_40": TARGET_ALGEBRA_DIMENSION == 40,
        "faithful_full_a985_embedding_refuted_by_dimension": source_algebra_dimension
        > TARGET_ALGEBRA_DIMENSION,
        "small_block_sector_count_is_15": len(small_rows) == 15,
        "small_block_sectors_can_fill_ten_target_components_as_abstract_shape": len(
            small_rows
        )
        >= TARGET_BLOCK_COUNT,
        "literal_current_label_bridge_refuted": direct_summary[
            "direct_compressed_map_is_multiplicative"
        ]
        is False
        and direct_summary["leaking_relation_count"] == 979
        and direct_summary["relation_target_action_matches"]
        == {"2I": [], "4S": [], "2I+4S": []}
        and direct_summary["quotient_target_action_matches"]
        == {
            "q42": {"2I": [], "4S": [], "2I+4S": []},
            "q12": {"2I": [], "4S": [], "2I+4S": []},
        },
        "unconstrained_no_homomorphism_claim_demoted": hom_boundary[
            "unconstrained_nonfaithful_full_domain_homomorphism"
        ]
        == "not_refuted_by_current_evidence",
    }
    report = {
        "schema": "d20.theorem.d20_a985_mat2_hom_boundary",
        "status": "D20_A985_MAT2_HOM_BOUNDARY_CERTIFIED",
        "object": "D20",
        "claim": (
            "The certified boundary is narrower than the informal no-go. A faithful full "
            "A985 action inside Mat_2(Q)^10 is impossible by dimension, and the literal "
            "current packet-label restriction has been refuted. But the current evidence "
            "does not certify the stronger claim that no nonfaithful full-domain "
            "A985-to-Mat_2(Q)^10 homomorphism exists; that stronger claim requires "
            "additional label-compatible column constraints or a rational block certificate."
        ),
        "definition": {
            "full_a985_source_dimension": (
                "The source algebra dimension is the sum of the certified source-sector "
                "matrix-unit counts."
            ),
            "faithful_operator_homomorphism_no_go": (
                "An injective algebra map from a 985-dimensional source into a "
                "40-dimensional target algebra is impossible."
            ),
            "nonfaithful_boundary": (
                "A nonfaithful full-domain homomorphism may factor through a small "
                "source-sector quotient; this certificate does not construct or refute a "
                "rational Q lift of that quotient."
            ),
        },
        "inputs": {
            "canonical_sector_matrix_units_report": input_record(
                CANONICAL_SECTOR_MATRIX_UNITS_REPORT
            ),
            "canonical_sector_summary_csv": input_record(CANONICAL_SECTOR_SUMMARY_CSV),
            "full_matrix_unit_coo_report": input_record(FULL_MATRIX_UNIT_COO_REPORT),
            "full_packet_matrix_lift_report": input_record(FULL_PACKET_MATRIX_LIFT_REPORT),
            "a985_direct_packet_bridge_obstruction_report": input_record(
                A985_DIRECT_PACKET_BRIDGE_OBSTRUCTION_REPORT
            ),
        },
        "derived": {
            "dimension_summary": dimension_summary,
            "small_block_sector_rows": small_rows,
            "small_block_sector_rows_sha256": sha_json(small_rows),
            "homomorphism_boundary": hom_boundary,
            "direct_label_bridge_summary": direct_summary,
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "closure_boundary": {
            "certifies": [
                "no faithful full A985 embedding can fit inside Mat_2(Q)^10 by dimension",
                "the literal mode-mask/raw-point packet-label map is not an A985/tube/q42/q12 packet bridge",
                "the current evidence is insufficient for the stronger unconstrained nonfaithful no-homomorphism claim",
            ],
            "does_not_certify": [
                "nonexistence of every abstract nonfaithful A985 -> Mat_2(Q)^10 homomorphism",
                "existence of a rational Q block quotient from the finite-field matrix-unit certificates",
                "exhaustion of all future label-compatible A985/tube/q42/q12 packet-column assignments",
            ],
        },
        "next_highest_yield_item": (
            "Turn the remaining homomorphism question into a finite labelled-column problem: "
            "enumerate q42/q12/object-compatible packet-column assignments and test each for "
            "subspace preservation, Mat_2(Q)^10 landing, target-action matching, and A985 "
            "multiplication."
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
        "schema": "d20.theorem.d20_a985_mat2_hom_boundary_manifest",
        "status": report["status"],
        "name": THEOREM_ID,
        "artifacts": {
            "report": rel(out_dir / "report.json"),
            "manifest": rel(out_dir / "manifest.json"),
        },
        "report_sha256": report["certificate_sha256"],
        "inputs": report["inputs"],
        "purpose": [
            "separate faithful full-A985 dimension no-go from nonfaithful homomorphism claims",
            "bind the direct packet-label bridge obstruction to the Mat_2(Q)^10 boundary",
            "prevent overclaiming an unconstrained no-homomorphism theorem",
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
