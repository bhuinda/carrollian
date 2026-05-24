from pathlib import Path
import argparse, json
from collections import defaultdict
from common import *

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--d20", required=True); ap.add_argument("--t985", required=True); ap.add_argument("--quotients", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--sample", type=int, default=0)
    args = ap.parse_args()
    out = Path(args.out) / "06_rho20_kernel_quotient"; out.mkdir(parents=True, exist_ok=True)

    d20, tz, qz = load_inputs(Path(args.d20), Path(args.t985), Path(args.quotients))
    triples = tz["triples"].astype("int64"); reps = tz["reps"].astype("int64")
    block_i = qz["block_i"].astype("int16"); block_j = qz["block_j"].astype("int16")
    s = reps[:,4].astype("int64")
    pairmap = build_pairmap(triples)

    pivots = {}
    for i in range(6):
        for j in range(6):
            inds = [int(r) for r in np.where((block_i == i) & (block_j == j))[0]]
            nonzero = [r for r in inds if int(s[r]) != 0]
            pivots[(i,j)] = min(nonzero, key=lambda r:(abs(int(s[r])), r))

    kernel_rows, bad = [], []
    for i in range(6):
        for j in range(6):
            pvt = pivots[(i,j)]; sp = int(s[pvt])
            inds = [int(r) for r in np.where((block_i == i) & (block_j == j))[0]]
            for r in inds:
                if r == pvt: continue
                sr = int(s[r])
                vec = {r: sp, pvt: -sr}
                ok = rho_image_of_vec(vec, block_i, block_j, s) == {}
                if not ok: bad.append({"i": i, "j": j, "r": r, "pivot": pvt})
                kernel_rows.append({"i": i, "j": j, "relation": r, "pivot": pvt, "coeff_relation": sp, "coeff_pivot": -sr, "rho_image_zero": ok})

    matrix_rows = []
    for i in range(6):
        for j in range(6):
            for k in range(6):
                a, b, c = pivots[(i,j)], pivots[(j,k)], pivots[(i,k)]
                sa, sb, sc = int(s[a]), int(s[b]), int(s[c])
                diff = defaultdict(int)
                for rr, pp in pairmap.get((a,b), []): diff[int(rr)] += sc*int(pp)
                diff[c] -= sa*sb
                diff = {kk:v for kk,v in diff.items() if v}
                ok = rho_image_of_vec(diff, block_i, block_j, s) == {}
                matrix_rows.append({"i": i, "j": j, "k": k, "rho_image_zero": ok, "terms": len(diff)})
    sector18 = d20["layer_certificates"]["05_drinfeld_wedderburn_trace"]["sector_profiles"][18]
    support_by_object = [0]*6
    identity_candidates = [6,163,227,349,618,893]
    char_unit = 0
    for r in range(985):
        val = int(s[r]) if int(block_i[r]) == int(block_j[r]) else 0
        if val: support_by_object[int(block_i[r])] += 1
        if r in identity_candidates: char_unit += val
    sector18_match = sector18["object_loop_coordinate_support"] == support_by_object and sector18["block_dimension"] == 6 and sector18["permutation_multiplicity"] == 1
    write_csv(out / "rho20_kernel_basis_sparse.csv", kernel_rows)
    write_csv(out / "rho20_matrix_unit_mod_kernel_laws.csv", matrix_rows)
    write_csv(out / "bad_kernel_rows.csv", bad)
    cert = {
        "schema": "repro.rho20_kernel_quotient@1",
        "status": "PASS" if not bad and all(r["rho_image_zero"] for r in matrix_rows) and sector18_match else "FAIL",
        "kernel_dim": len(kernel_rows),
        "image_dim": 36,
        "kernel_plus_image": len(kernel_rows)+36,
        "sector18_match": sector18_match,
        "support_by_object": support_by_object,
    }
    write_json(out / "certificate.json", cert)
    print(json.dumps(cert, indent=2))

if __name__ == "__main__":
    main()
