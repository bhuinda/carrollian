#!/usr/bin/env python3
from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
STATUS = "D20_A985_RELATION_PAIR_QUOTIENT_STACK_SERIES_CERTIFIED_MOTIVIC_COHA_OPEN"
BUDGETS = {
    "full_pair_coefficient_mass",
    "full_pair_output_support",
    "q42_pair_coefficient_mass",
    "q42_pair_row_support",
    "q42_pair_output_classes",
    "q42_tensor_coefficient_mass",
    "q12_pair_coefficient_mass",
    "q12_pair_row_support",
    "q12_pair_output_classes",
    "q12_tensor_coefficient_mass",
}
FOCUS_TARGETS = {39, 243, 455640, 534656}


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def read_csv(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def assert_manifest_hashes() -> None:
    manifest = load_json("MANIFEST.json")
    assert manifest["status"] == STATUS
    for name, record in manifest["files"].items():
        path = ROOT / name
        assert path.exists(), f"missing manifest file: {name}"
        assert path.stat().st_size == int(record["size_bytes"]), f"size mismatch: {name}"
        assert sha256_path(path) == record["sha256"], f"sha256 mismatch: {name}"


def main() -> None:
    cert = load_json("relation_pair_stack_series_certificate.json")
    assert cert["status"] == STATUS
    assert cert["gate"] == "D20_A985_RELATION_PAIR_QUOTIENT_STACK_SERIES"
    assert cert["bounds"]["NMAX"] == 40
    assert cert["bounds"]["QMAX"] == 512
    assert_manifest_hashes()

    sources = load_json("relation_pair_weight_sources.json")
    meta = sources["tensor_metadata"]
    assert meta["relation_pair_cells"] == 985 * 985
    assert meta["nonzero_relation_pairs"] == 198029
    assert meta["zero_relation_pairs"] == 985 * 985 - 198029
    assert meta["support"] == 1414965
    assert meta["coefficient_total"] == 2537360
    assert meta["q42_to_q12_consistent"] is True
    assert meta["q42_tensor_matches_supplied"] is True
    assert meta["q12_tensor_matches_supplied"] is True

    distributions = read_csv("relation_pair_weight_distributions.csv")
    assert {row["budget"] for row in distributions} == BUDGETS
    assert any(row["budget"] == "full_pair_coefficient_mass" and row["weight"] == "0" for row in distributions)
    assert any(row["budget"] == "q42_tensor_coefficient_mass" and row["weight"] == "0" for row in distributions)

    coefficients = read_csv("relation_pair_weighted_coefficients.csv")
    assert coefficients
    assert {row["weight_type"] for row in coefficients} == BUDGETS
    for row in coefficients:
        assert int(row["total_dimension_n"]) <= 40
        assert int(row["q_exponent"]) <= 512
        assert int(row["coefficient"]) > 0

    tests = {row["test"]: row["status"] for row in read_csv("relation_pair_series_tests.csv")}
    assert tests["relation_pair_series_computed"] == "PASS"
    assert tests["full_relation_pair_cells_accounted"] == "PASS"
    assert tests["q42_tensor_matches_supplied"] == "PASS"
    assert tests["q12_tensor_matches_supplied"] == "PASS"
    assert tests["q42_to_q12_consistent"] == "PASS"
    assert tests["raw_tensor_metadata"] == "PASS"
    assert tests["target_39_full_pair_coefficient_mass_exact_hit"] == "EXACT_HIT"
    assert tests["target_455640_full_pair_coefficient_mass_exact_hit"] == "NO_HIT_DIAGNOSTIC"
    assert tests["target_534656_full_pair_coefficient_mass_exact_hit"] == "NO_HIT_DIAGNOSTIC"
    assert tests["independent_985_by_985_dimension_vector_bilinear_series"] == "OPEN"
    assert tests["full_a985_sheafified_CoHA"] == "OPEN"

    hits = read_csv("relation_pair_invariant_hits.csv")
    assert FOCUS_TARGETS <= {int(row["target"]) for row in hits}
    formulas = load_json("relation_pair_series_formulas.json")
    assert "relation_pair_stack_formula" in formulas
    assert "Independent 985-by-985" in formulas["seam"]
    print(STATUS)


if __name__ == "__main__":
    main()
