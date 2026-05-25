from __future__ import annotations

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = "data/invariants/d20/theorems/d20_triple_13_signature_uniqueness/report.json"
DOWNSTREAM_SURVEY_REL = (
    "data/invariants/d20/theorems/d20_raw_transport_3x3_discriminant13_search/report.json"
)
EXPECTED_TRIPLE = ["R33", "K_mixed_S", "K_pure_Sminus"]
EXPECTED_MATRIX = [[4, 0, 0], [0, 5, 1], [0, 1, 2]]
EXPECTED_SIGNATURE = "4d849f013271f81f2fea99ba563ea7425f10c3b3d429e2375c9d309024354c9f"


def _check_input_record(row: dict[str, Any]) -> None:
    rel_path = row.get("path")
    if not isinstance(rel_path, str) or not rel_path.endswith("/report.json"):
        raise AssertionError("D20 triple uniqueness input path mismatch")
    if rel_path == REPORT_REL:
        raise AssertionError("D20 triple uniqueness report cannot classify itself")
    path = ROOT / rel_path
    if not path.exists():
        raise AssertionError(f"D20 triple uniqueness missing corpus report: {rel_path}")
    if h_file(path) != row.get("sha256"):
        raise AssertionError(f"D20 triple uniqueness corpus hash mismatch: {rel_path}")
    if rel_path == DOWNSTREAM_SURVEY_REL:
        raise AssertionError("D20 triple uniqueness corpus cannot include downstream survey")


def validate_d20_triple_13_signature_uniqueness() -> Dict[str, Any]:
    rec: dict[str, Any] | None = None
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            rec = json.load(f)
    else:
        cached = cached_core_block("d20_triple_13_signature_uniqueness")
        if cached is not None:
            rec = cached
    if rec is None:
        raise FileNotFoundError("missing D20 triple 13-signature uniqueness certificate")

    if rec.get("status") != "D20_TRIPLE_13_SIGNATURE_UNIQUENESS_CERTIFIED":
        raise AssertionError("D20 triple uniqueness status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("D20 triple uniqueness checks did not pass")

    inputs = rec.get("inputs", {}).get("report_corpus", [])
    if len(inputs) <= 100:
        raise AssertionError("D20 triple uniqueness corpus is unexpectedly small")
    for row in inputs:
        _check_input_record(row)

    derived = rec.get("derived", {})
    corpus_rows = derived.get("corpus_rows", [])
    if len(corpus_rows) != len(inputs):
        raise AssertionError("D20 triple uniqueness corpus/input count mismatch")
    if h_json(corpus_rows) != derived.get("corpus_rows_sha256"):
        raise AssertionError("D20 triple uniqueness corpus hash mismatch")

    triple_records = derived.get("explicit_triple_records", [])
    if h_json(triple_records) != derived.get("explicit_triple_records_sha256"):
        raise AssertionError("D20 triple uniqueness explicit triple hash mismatch")
    unique = derived.get("unique_certified_triple_signatures", [])
    if h_json(unique) != derived.get("unique_certified_triple_signatures_sha256"):
        raise AssertionError("D20 triple uniqueness unique-signature hash mismatch")
    disc = derived.get("certified_discriminant13_records", [])
    if h_json(disc) != derived.get("certified_discriminant13_records_sha256"):
        raise AssertionError("D20 triple uniqueness discriminant record hash mismatch")
    order13 = derived.get("certified_order13_records", [])
    if h_json(order13) != derived.get("certified_order13_records_sha256"):
        raise AssertionError("D20 triple uniqueness order-13 record hash mismatch")
    triple13 = derived.get("triple_13_signatures", [])
    if h_json(triple13) != derived.get("triple_13_signatures_sha256"):
        raise AssertionError("D20 triple uniqueness 13-signature hash mismatch")

    summary = derived.get("summary", {})
    if summary.get("corpus_report_count") != len(corpus_rows):
        raise AssertionError("D20 triple uniqueness corpus summary mismatch")
    if summary.get("explicit_triple_record_count") != len(triple_records):
        raise AssertionError("D20 triple uniqueness triple-record summary mismatch")
    if summary.get("unique_certified_triple_signature_count") != 1:
        raise AssertionError("D20 triple uniqueness unique signature count mismatch")
    if summary.get("certified_discriminant13_record_count") != len(disc):
        raise AssertionError("D20 triple uniqueness discriminant count mismatch")
    if summary.get("certified_order13_record_count") != len(order13):
        raise AssertionError("D20 triple uniqueness order-13 count mismatch")
    if summary.get("triple_13_signature_count") != 1:
        raise AssertionError("D20 triple uniqueness 13-signature count mismatch")
    if summary.get("hidden_transport_triple_unique_for_13_signatures") is not True:
        raise AssertionError("D20 triple uniqueness hidden triple uniqueness mismatch")
    if summary.get("expected_hidden_transport_signature_sha256") != EXPECTED_SIGNATURE:
        raise AssertionError("D20 triple uniqueness expected signature mismatch")

    if len(unique) != 1 or len(triple13) != 1:
        raise AssertionError("D20 triple uniqueness signature list mismatch")
    signature = unique[0]
    if signature != triple13[0]:
        raise AssertionError("D20 triple uniqueness candidate list mismatch")
    if signature.get("signature_sha256") != EXPECTED_SIGNATURE:
        raise AssertionError("D20 triple uniqueness candidate signature mismatch")
    if signature.get("basis_order") != EXPECTED_TRIPLE:
        raise AssertionError("D20 triple uniqueness candidate basis mismatch")
    if signature.get("matrix") != EXPECTED_MATRIX:
        raise AssertionError("D20 triple uniqueness candidate matrix mismatch")
    if signature.get("has_discriminant_13") is not True:
        raise AssertionError("D20 triple uniqueness discriminant flag mismatch")
    if signature.get("has_order13_signature") is not True:
        raise AssertionError("D20 triple uniqueness order-13 flag mismatch")
    if set(signature.get("theorem_ids", [])) != {
        "d20_intrinsic_triple_ordering_clock",
        "finite_anomaly_counter",
        "sector26_invariant_suite",
    }:
        raise AssertionError("D20 triple uniqueness occurrence theorem mismatch")

    checks = rec.get("checks", {})
    required_true = [
        "corpus_has_reports",
        "all_triple_records_are_same_unique_signature",
        "unique_signature_is_hidden_transport_triple",
        "certified_discriminant13_records_exist",
        "certified_order13_records_exist",
        "only_hidden_transport_triple_has_13_signature",
        "expected_signature_occurs",
        "expected_signature_has_discriminant13",
        "expected_signature_has_order13_signature",
    ]
    for key in required_true:
        if checks.get(key) is not True:
            raise AssertionError(f"D20 triple uniqueness check failed: {key}")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("D20 triple uniqueness self hash mismatch")

    return rec


if __name__ == "__main__":
    rec = validate_d20_triple_13_signature_uniqueness()
    print(rec["status"])
    print(rec["certificate_sha256"])
