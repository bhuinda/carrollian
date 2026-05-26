#!/usr/bin/env python3
import csv
P = 1000003
INV2 = (P+1)//2

def main():
    rows=list(csv.DictReader(open("all_residue_height_transport_rows.csv", newline="", encoding="utf-8")))
    assert len(rows)==2048
    for r in rows:
        h=int(r["height_action"])
        res=int(r["residual_integral"])
        assert res == -h
        assert int(r["residual_mod_1000003"]) == res % P
        assert int(r["transport_scalar_mod_1000003"]) == ((res % P) * INV2) % P
        assert int(r["q42_shadow_nonzero"]) == 0
        assert int(r["q12_shadow_nonzero"]) == 0
    print("PASS all-residue scalar height/action-return table")
if __name__ == "__main__":
    main()
