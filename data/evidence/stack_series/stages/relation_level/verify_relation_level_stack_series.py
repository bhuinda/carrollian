#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
STATUS = "D20_A985_RELATION_LEVEL_STACK_SERIES_CERTIFIED_RAW_TENSOR_MOTIVIC_COHA_OPEN"
FOCUS_TARGETS = {39, 243, 455640, 534656}
BUDGETS = {
    "tensor_coefficient_value",
    "relation_orbit_size",
    "left_relation_coefficient_mass",
    "right_relation_coefficient_mass",
    "output_relation_coefficient_mass",
    "left_relation_support",
    "right_relation_support",
    "output_relation_support",
}


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
    cert = load_json("relation_level_stack_series_certificate.json")
    assert cert["status"] == STATUS
    assert cert["gate"] == "D20_A985_RELATION_LEVEL_STACK_SERIES"
    assert cert["bounds"]["NMAX"] == 40
    assert cert["bounds"]["QMAX"] == 512
    assert_manifest_hashes()

    sources = load_json("relation_level_weight_sources.json")
    tensor = sources["tensor_metadata"]
    assert tensor["relation_count"] == 985
    assert tensor["support"] == 1414965
    assert tensor["coefficient_total"] == 2537360
    assert tensor["composability_failures"] == 0
    assert tensor["output_relation_mass_uniform"] is True
    assert tensor["output_relation_mass_value"] == 2576

    distributions = read_csv("relation_level_weight_distributions.csv")
    assert {row["budget"] for row in distributions} == BUDGETS
    assert any(row["budget"] == "tensor_coefficient_value" and row["weight"] == "1" for row in distributions)
    assert any(row["budget"] == "relation_orbit_size" and row["weight"] == "64" for row in distributions)

    coefficients = read_csv("relation_level_weighted_coefficients.csv")
    assert coefficients, "no coefficient rows"
    assert {row["weight_type"] for row in coefficients} == BUDGETS
    for row in coefficients:
        assert int(row["total_dimension_n"]) <= 40
        assert int(row["q_exponent"]) <= 512
        assert int(row["coefficient"]) > 0

    tests = {row["test"]: row["status"] for row in read_csv("relation_level_series_tests.csv")}
    assert tests["relation_level_series_computed"] == "PASS"
    assert tests["t985_triples_composable_over_relation_object_pairs"] == "PASS"
    assert tests["output_relation_mass_uniform"] == "PASS"
    assert tests["raw_tensor_metadata"] == "PASS"
    assert tests["full_relation_pair_bilinear_stack"] == "OPEN"
    assert tests["full_a985_relation_level_sheafified_CoHA"] == "OPEN"

    hits = read_csv("relation_level_invariant_hits.csv")
    assert FOCUS_TARGETS <= {int(row["target"]) for row in hits}
    formulas = load_json("relation_level_series_formulas.json")
    assert "series_formula" in formulas
    assert "full 985x985 relation-pair bilinear stack" in formulas["seam"]
    print(STATUS)


if __name__ == "__main__":
    main()
