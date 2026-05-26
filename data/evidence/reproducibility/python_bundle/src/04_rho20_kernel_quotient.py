import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap
import argparse, json, numpy as np
from pathlib import Path
from collections import defaultdict
from common import *

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--d20", required=True); ap.add_argument("--t985", required=True); ap.add_argument("--quotients", required=True); ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out) / "04_rho20_kernel_quotient"
    d20, tz, qz = load_inputs(args.d20, args.t985, args.quotients)
    triples = tz["triples"].astype(np.int64); reps = tz["reps"].astype(np.int64)
    block_i = qz["block_i"].astype(np.int16); block_j = qz["block_j"].astype(np.int16)
    s = reps[:,4].astype(np.int64)
    pairmap = build_pairmap(triples)
    pivots = {}
    for i in range(6):
        for j in range(6):
            inds = [int(r) for r in np.where((block_i == i) & (block_j == j))[0]]
            pivots[(i,j)] = min([r for r in inds if int(s[r]) != 0], key=lambda r: (abs(int(s[r])), r))
    kernel_rows, bad = [], []
    for i in range(6):
        for j in range(6):
            pvt = pivots[(i,j)]; sp = int(s[pvt])
            inds = [int(r) for r in np.where((block_i == i) & (block_j == j))[0]]
            for r in inds:
                if r == pvt: continue
                sr = int(s[r])
                ok = rho_image_of_vec({r: sp, pvt: -sr}, block_i, block_j, s) == {}
                kernel_rows.append({"i": i, "j": j, "relation": r, "pivot": pvt, "coeff_relation": sp, "coeff_pivot": -sr, "rho_image_zero": ok})
                if not ok: bad.append({"i": i, "j": j, "relation": r})
    matrix_rows = []
    for i in range(6):
        for j in range(6):
            for k in range(6):
                a,b,c = pivots[(i,j)], pivots[(j,k)], pivots[(i,k)]
                sa,sb,sc = int(s[a]), int(s[b]), int(s[c])
                diff = defaultdict(int)
                for rr,pp in pairmap.get((a,b), []):
                    diff[int(rr)] += sc*int(pp)
                diff[c] -= sa*sb
                diff = {kk:v for kk,v in diff.items() if v}
                ok = rho_image_of_vec(diff, block_i, block_j, s) == {}
                matrix_rows.append({"i": i, "j": j, "k": k, "rho_image_zero": ok, "terms": len(diff)})
    write_csv(out / "rho20_kernel_basis_sparse.csv", kernel_rows)
    write_csv(out / "rho20_matrix_unit_mod_kernel_laws.csv", matrix_rows)
    cert = {"status": "PASS" if not bad and all(x["rho_image_zero"] for x in matrix_rows) else "FAIL", "kernel_dim": len(kernel_rows), "image_dim": 36, "kernel_plus_image": len(kernel_rows)+36}
    write_json(out / "certificate.json", cert)
    print(json.dumps(cert, indent=2))
if __name__ == "__main__":
    main()
