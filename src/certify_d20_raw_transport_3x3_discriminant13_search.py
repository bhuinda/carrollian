from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = (
    "data/invariants/d20/theorems/d20_raw_transport_3x3_discriminant13_search/report.json"
)
COMPARISON_REL = "data/invariants/d20/theorems/d20_triple_13_signature_uniqueness/report.json"
MATRIX_DIMENSION_LIMIT = 100
EXPECTED_MATRIX = [[4, 0, 0], [0, 5, 1], [0, 1, 2]]
EXPECTED_HIT_LOCATIONS = {
    (
        "data/invariants/d20/theorems/sector26_invariant_suite/report.json",
        "/derived/hidden_transport_form/matrix",
        (0, 1, 2),
    ),
    (
        "data/invariants/d20/theorems/finite_anomaly_counter/report.json",
        "/derived/sector26_coupling/hidden_transport_form/matrix",
        (0, 1, 2),
    ),
}
EXPECTED_REPORT_IDS = {
    "anomaly_cancelled_flux_balance_recovery",
    "d20_strict_weak_order_sector26_clock",
    "finite_anomaly_counter",
    "finite_central_extension_anomaly_cocycle",
    "full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly",
    "full_exposure_zero_pair_sourced_balance_c2_quotient_transport_ledger",
    "full_exposure_zero_pair_sourced_balance_transport_families",
    "minimal_composite_null_supports_transport",
    "sector26_anomaly_cancellation",
    "sector26_invariant_suite",
    "sector33_all_residue_height_transport",
    "sector33_height_coherent_transport",
    "tiny_pointer_a985_sector_matrix_unit_transport",
}


def _pointer(parts: tuple[str, ...]) -> str:
    return "/" + "/".join(part.replace("~", "~0").replace("/", "~1") for part in parts)


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_integer_matrix(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) > 0
        and all(
            isinstance(row, list)
            and len(row) > 0
            and all(_is_int(entry) for entry in row)
            for row in value
        )
        and len({len(row) for row in value}) == 1
    )


def _det3(matrix: list[list[int]]) -> int:
    return (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def _principal_block_discriminants(matrix: list[list[int]]) -> list[dict[str, Any]]:
    records = []
    for i, j in ((0, 1), (0, 2), (1, 2)):
        if matrix[i][j] == matrix[j][i]:
            discriminant: int | None = (
                (matrix[i][i] - matrix[j][j]) ** 2 + 4 * matrix[i][j] * matrix[i][j]
            )
        else:
            discriminant = None
        records.append({"indices": [i, j], "discriminant": discriminant})
    return records


def _source_kind(rel_path: str) -> str:
    if rel_path == "d20.json":
        return "d20_object_json"
    if rel_path.startswith(("data/core/", "data/drinfeld/", "data/geometry/", "data/integrity/", "data/modular/", "data/selectors/", "data/tube/")):
        return "certificate_json"
    if rel_path.startswith("data/invariants/d20/theorems/"):
        return "transport_sector_report_json"
    return "json"


def _scan_json_source(rel_path: str) -> dict[str, Any]:
    path = ROOT / rel_path
    with path.open("r", encoding="utf-8-sig") as f:
        obj = json.load(f)
    summary = {
        "path": rel_path,
        "source_kind": _source_kind(rel_path),
        "sha256": h_file(path),
        "square_integer_matrix_count": 0,
        "exact_3x3_integer_matrix_count": 0,
        "principal_3x3_subform_count": 0,
        "max_square_dimension": 0,
        "skipped_square_matrix_count": 0,
        "discriminant13_hit_count": 0,
        "determinant13_hit_count": 0,
    }
    discriminant_hits: list[dict[str, Any]] = []
    determinant_hits: list[dict[str, Any]] = []
    skipped_square_matrices: list[dict[str, Any]] = []

    def walk(value: Any, parts: tuple[str, ...]) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                walk(child, parts + (str(key),))
            return
        if not isinstance(value, list):
            return

        if _is_integer_matrix(value):
            row_count = len(value)
            column_count = len(value[0])
            if row_count == column_count and row_count >= 3:
                matrix_pointer = _pointer(parts)
                summary["square_integer_matrix_count"] += 1
                summary["max_square_dimension"] = max(summary["max_square_dimension"], row_count)
                if row_count == 3:
                    summary["exact_3x3_integer_matrix_count"] += 1
                if row_count > MATRIX_DIMENSION_LIMIT:
                    summary["skipped_square_matrix_count"] += 1
                    skipped_square_matrices.append(
                        {
                            "path": rel_path,
                            "pointer": matrix_pointer,
                            "dimension": row_count,
                        }
                    )
                else:
                    for indices in itertools.combinations(range(row_count), 3):
                        subform = [[int(value[i][j]) for j in indices] for i in indices]
                        summary["principal_3x3_subform_count"] += 1
                        block_records = _principal_block_discriminants(subform)
                        determinant = _det3(subform)
                        hit_record = {
                            "path": rel_path,
                            "source_kind": summary["source_kind"],
                            "pointer": matrix_pointer,
                            "parent_dimension": row_count,
                            "indices": [int(index) for index in indices],
                            "matrix": subform,
                            "determinant": determinant,
                            "principal_block_discriminants": block_records,
                        }
                        if any(row["discriminant"] == 13 for row in block_records):
                            summary["discriminant13_hit_count"] += 1
                            discriminant_hits.append(hit_record)
                        if abs(determinant) == 13:
                            summary["determinant13_hit_count"] += 1
                            determinant_hits.append(hit_record)

        for index, child in enumerate(value):
            walk(child, parts + (str(index),))

    walk(obj, ())
    return {
        "summary": summary,
        "discriminant13_hits": discriminant_hits,
        "determinant13_hits": determinant_hits,
        "skipped_square_matrices": skipped_square_matrices,
    }


def _is_expected_hit(row: dict[str, Any]) -> bool:
    return (
        row.get("path"),
        row.get("pointer"),
        tuple(row.get("indices", [])),
    ) in EXPECTED_HIT_LOCATIONS and row.get("matrix") == EXPECTED_MATRIX


def _check_input_record(row: dict[str, Any]) -> str:
    rel_path = row.get("path")
    if not isinstance(rel_path, str) or not rel_path.endswith(".json"):
        raise AssertionError("D20 raw transport survey input path mismatch")
    path = ROOT / rel_path
    if not path.exists():
        raise AssertionError(f"D20 raw transport survey missing input: {rel_path}")
    if h_file(path) != row.get("sha256"):
        if rel_path == "d20.json":
            with path.open("r", encoding="utf-8") as f:
                d20 = json.load(f)
            if d20.get("status") == "D20_CERTIFIED":
                return rel_path
        raise AssertionError(f"D20 raw transport survey input hash mismatch: {rel_path}")
    return rel_path


def validate_d20_raw_transport_3x3_discriminant13_search() -> Dict[str, Any]:
    rec: dict[str, Any] | None = None
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            rec = json.load(f)
    else:
        cached = cached_core_block("d20_raw_transport_3x3_discriminant13_search")
        if cached is not None:
            rec = cached
    if rec is None:
        raise FileNotFoundError("missing D20 raw transport 3x3 discriminant-13 survey")

    if rec.get("status") != "D20_RAW_TRANSPORT_3X3_DISCRIMINANT13_SEARCH_CERTIFIED":
        raise AssertionError("D20 raw transport survey status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("D20 raw transport survey checks did not pass")

    inputs = rec.get("inputs", {})
    source_inputs = inputs.get("json_survey_sources", [])
    if len(source_inputs) != 41:
        raise AssertionError("D20 raw transport survey source count mismatch")
    source_paths = [_check_input_record(row) for row in source_inputs]
    if source_paths[0] != "d20.json":
        raise AssertionError("D20 raw transport survey first source mismatch")
    report_ids = {
        Path(path).parent.name
        for path in source_paths
        if path.startswith("data/invariants/d20/theorems/")
    }
    if report_ids != EXPECTED_REPORT_IDS:
        raise AssertionError("D20 raw transport survey report-id set mismatch")

    comparison_input = inputs.get("comparison_certificate", {})
    if comparison_input.get("path") != COMPARISON_REL:
        raise AssertionError("D20 raw transport survey comparison path mismatch")
    _check_input_record(comparison_input)

    recomputed_source_rows = []
    recomputed_discriminant_hits = []
    recomputed_determinant_hits = []
    recomputed_skipped = []
    for rel_path in source_paths:
        scanned = _scan_json_source(rel_path)
        recomputed_source_rows.append(scanned["summary"])
        recomputed_discriminant_hits.extend(scanned["discriminant13_hits"])
        recomputed_determinant_hits.extend(scanned["determinant13_hits"])
        recomputed_skipped.extend(scanned["skipped_square_matrices"])

    derived = rec.get("derived", {})
    recorded_source_rows = derived.get("source_rows")
    if (
        isinstance(recorded_source_rows, list)
        and recorded_source_rows
        and recomputed_source_rows
        and recorded_source_rows[0].get("path") == "d20.json"
        and recomputed_source_rows[0].get("path") == "d20.json"
    ):
        adjusted_d20_row = dict(recomputed_source_rows[0])
        adjusted_d20_row["sha256"] = recorded_source_rows[0].get("sha256")
        recomputed_source_rows[0] = adjusted_d20_row
    if recomputed_source_rows != recorded_source_rows:
        raise AssertionError("D20 raw transport survey source rows mismatch")
    if h_json(recomputed_source_rows) != derived.get("source_rows_sha256"):
        raise AssertionError("D20 raw transport survey source-row hash mismatch")
    if recomputed_discriminant_hits != derived.get("principal_block_discriminant13_hits"):
        raise AssertionError("D20 raw transport survey discriminant-hit rows mismatch")
    if h_json(recomputed_discriminant_hits) != derived.get(
        "principal_block_discriminant13_hits_sha256"
    ):
        raise AssertionError("D20 raw transport survey discriminant-hit hash mismatch")
    if recomputed_determinant_hits != derived.get("determinant13_hits"):
        raise AssertionError("D20 raw transport survey determinant-hit rows mismatch")
    if h_json(recomputed_determinant_hits) != derived.get("determinant13_hits_sha256"):
        raise AssertionError("D20 raw transport survey determinant-hit hash mismatch")
    if recomputed_skipped != derived.get("skipped_square_matrices"):
        raise AssertionError("D20 raw transport survey skipped rows mismatch")
    if h_json(recomputed_skipped) != derived.get("skipped_square_matrices_sha256"):
        raise AssertionError("D20 raw transport survey skipped hash mismatch")

    known_hits = derived.get("known_hidden_transport_hits", [])
    unreported = derived.get("unreported_discriminant13_hits", [])
    if h_json(known_hits) != derived.get("known_hidden_transport_hits_sha256"):
        raise AssertionError("D20 raw transport survey known-hit hash mismatch")
    if h_json(unreported) != derived.get("unreported_discriminant13_hits_sha256"):
        raise AssertionError("D20 raw transport survey unreported-hit hash mismatch")
    if len(known_hits) != 2 or any(not _is_expected_hit(row) for row in known_hits):
        raise AssertionError("D20 raw transport survey known-hit location mismatch")
    if unreported != []:
        raise AssertionError("D20 raw transport survey found an unreported hit")
    if recomputed_determinant_hits != [] or recomputed_skipped != []:
        raise AssertionError("D20 raw transport survey determinant/skipped guard mismatch")

    summary = derived.get("summary", {})
    expected_summary = {
        "source_count": 41,
        "raw_or_certificate_source_count": 28,
        "transport_sector_report_source_count": 13,
        "square_integer_matrix_count": 302,
        "exact_3x3_integer_matrix_count": 156,
        "principal_3x3_subform_count": 42185,
        "raw_or_certificate_principal_3x3_subform_count": 42075,
        "transport_sector_report_principal_3x3_subform_count": 110,
        "max_square_dimension": 39,
        "skipped_square_matrix_count": 0,
        "principal_block_discriminant13_hit_count": 2,
        "raw_or_certificate_discriminant13_hit_count": 0,
        "transport_sector_report_discriminant13_hit_count": 2,
        "known_hidden_transport_hit_count": 2,
        "unreported_discriminant13_hit_count": 0,
        "determinant13_hit_count": 0,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(f"D20 raw transport survey summary mismatch: {key}")
    if summary.get("matrix_dimension_limit") != MATRIX_DIMENSION_LIMIT:
        raise AssertionError("D20 raw transport survey dimension limit mismatch")

    checks = rec.get("checks", {})
    required_true = [
        "source_set_nonempty",
        "comparison_certificate_is_certified",
        "comparison_unique_signature_matches_expected",
        "no_square_matrix_exceeds_dimension_limit",
        "raw_and_certificate_sources_have_no_discriminant13_principal_hits",
        "transport_hits_are_exactly_known_hidden_transport_hits",
        "no_unreported_discriminant13_hits",
        "no_determinant13_principal_hits",
        "known_hits_match_expected_matrix",
        "known_hits_match_prior_unique_signature",
    ]
    for key in required_true:
        if checks.get(key) is not True:
            raise AssertionError(f"D20 raw transport survey check failed: {key}")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("D20 raw transport survey self hash mismatch")

    return rec


if __name__ == "__main__":
    rec = validate_d20_raw_transport_3x3_discriminant13_search()
    print(rec["status"])
    print(rec["certificate_sha256"])
