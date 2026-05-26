#!/usr/bin/env python3
from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
STATUS = "D20_A985_WEIGHTED_STACK_SERIES_CERTIFIED_RAW_TENSOR_SHADOW_MOTIVIC_COHA_OPEN"
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


def assert_coefficients(name: str, nmax: int, qmax: int) -> int:
    rows = read_csv(name)
    assert rows, f"{name} has no coefficient rows"
    for row in rows:
        assert int(row["total_dimension_n"]) <= nmax, f"{name} exceeds n bound"
        assert int(row["q_exponent"]) <= qmax, f"{name} exceeds q bound"
        assert int(row["coefficient"]) > 0, f"{name} has nonpositive coefficient"
    return len(rows)


def main() -> None:
    cert = load_json("a985_weighted_stack_series_certificate.json")
    assert cert["status"] == STATUS
    assert cert["gate"] == "D20_A985_WEIGHTED_STACK_SERIES"
    assert cert["bounds"]["NMAX"] == 40
    assert cert["bounds"]["QMAX"] == 512

    assert_manifest_hashes()

    sources = load_json("a985_weight_sources.json")
    tensor = sources["tensor_metadata"]
    assert tensor["relation_count"] == 985
    assert tensor["support"] == 1414965
    assert tensor["coefficient_total"] == 2537360
    assert tensor["point_fiber"] == 2576
    assert tensor["composability_failures"] == 0
    assert tensor["gamma_collapses_to_point_fiber_m6"] is True
    assert tensor["raw_tensor_min_positive_weight"] > cert["bounds"]["QMAX"]
    assert sources["t985_output_mass_normalized_by_point_fiber"] == sources["m6_relation_count_matrix"]

    m6_rows = assert_coefficients("a985_m6_weighted_coefficients.csv", 40, 512)
    raw_rows = assert_coefficients("a985_t985_raw_qwindow_coefficients.csv", 40, 512)
    assert m6_rows == cert["coefficient_files"]["m6_relation_count"]["rows"]
    assert raw_rows == cert["coefficient_files"]["t985_raw_output_mass"]["rows"]

    tests = {row["test"]: row["status"] for row in read_csv("a985_weighted_series_tests.csv")}
    assert tests["m6_relation_count_series_computed"] == "PASS"
    assert tests["t985_raw_output_mass_qwindow_computed"] == "PASS"
    assert tests["t985_triples_composable_over_object_pairs"] == "PASS"
    assert tests["t985_output_mass_collapses_to_2576_m6"] == "PASS"
    assert tests["t985_raw_qwindow_trivial_mixed_terms"] == "PASS"
    assert tests["full_a985_weighted_sheafified_CoHA"] == "OPEN"

    hits = read_csv("a985_weighted_invariant_hits.csv")
    hit_targets = {int(row["target"]) for row in hits}
    assert FOCUS_TARGETS <= hit_targets

    formulas = load_json("a985_weighted_series_formulas.json")
    assert "a985_m6_budget" in formulas
    assert "raw_t985_output_mass_budget" in formulas
    print(STATUS)


if __name__ == "__main__":
    main()
