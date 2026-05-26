#!/usr/bin/env python3
import csv
rows=list(csv.DictReader(open("lambda_hc_act_invariance_rows.csv", newline="", encoding="utf-8")))
assert len(rows)==2048
for r in rows:
    assert int(r["q42_shadow_nonzero"]) == 0
    assert int(r["q12_shadow_nonzero"]) == 0
    assert int(r["support_sector"]) == 33
    assert r["Act_kernel"] == "True"
    assert str(r["Talagrand_shell_delta"]) == "0"
print("PASS Lambda_hc Act invariance rows")
