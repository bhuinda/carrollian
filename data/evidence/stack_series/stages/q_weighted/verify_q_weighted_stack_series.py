#!/usr/bin/env python3
import csv, json
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def main():
    cert=json.loads((ROOT/"q_weighted_stack_series_certificate.json").read_text())
    assert cert["status"]=="D20_Q_WEIGHTED_STACK_SERIES_CERTIFIED_MOTIVIC_COHA_OPEN"
    assert cert["bounds"]["NMAX"] == 40
    assert cert["bounds"]["QMAX"] == 512

    for fname in ["half_weighted_coefficients.csv","double_weighted_coefficients.csv","gauge_weighted_coefficients.csv"]:
        rows=list(csv.DictReader((ROOT/fname).open()))
        assert len(rows)>0
        assert all(int(r["total_dimension_n"]) <= 40 for r in rows)
        assert all(int(r["q_exponent"]) <= 512 for r in rows)
        assert all(int(r["coefficient"]) > 0 for r in rows)

    hits=list(csv.DictReader((ROOT/"invariant_weighted_hits.csv").open()))
    assert len(hits)>0
    targets={int(r["target"]) for r in hits}
    assert 39 in targets
    assert 243 in targets
    assert 455640 in targets
    assert 534656 in targets

    tests={r["test"]:r["status"] for r in csv.DictReader((ROOT/"q_weighted_series_tests.csv").open())}
    assert tests["half_weighted_series_computed"]=="PASS"
    assert tests["double_weighted_series_computed"]=="PASS"
    assert tests["gauge_weighted_series_computed"]=="PASS"
    assert tests["full_q_weighted_sheafified_CoHA"]=="OPEN"

    spec=json.loads((ROOT/"q_weighted_series_formulas.json").read_text())
    assert "grade_decomposition" in spec

    print("D20_Q_WEIGHTED_STACK_SERIES_CERTIFIED_MOTIVIC_COHA_OPEN")

if __name__=="__main__":
    main()
