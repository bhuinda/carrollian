from pathlib import Path
import argparse, json
from collections import defaultdict, Counter
from common import *

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--d20", required=True); ap.add_argument("--t985", required=True); ap.add_argument("--quotients", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--sample", type=int, default=1000)
    args = ap.parse_args()
    out = Path(args.out) / "05_rho20_scalar_representation"; out.mkdir(parents=True, exist_ok=True)

    d20, tz, qz = load_inputs(Path(args.d20), Path(args.t985), Path(args.quotients))
    triples = tz["triples"].astype("int64"); reps = tz["reps"].astype("int64")
    block_i = qz["block_i"].astype("int16"); block_j = qz["block_j"].astype("int16")
    s = reps[:,4].astype("int64")
    pair_rhs = defaultdict(int)
    for a,b,c,p in triples:
        pair_rhs[(int(a),int(b))] += int(p)*int(s[c])

    eq_fail = []
    nonzero_product_pairs = 0
    for a in range(985):
        for b in range(985):
            lhs = int(s[a])*int(s[b]) if int(block_j[a]) == int(block_i[b]) else 0
            rhs = pair_rhs.get((a,b), 0)
            if rhs: nonzero_product_pairs += 1
            if lhs != rhs:
                eq_fail.append({"a": a, "b": b, "lhs": lhs, "rhs": rhs})
                break
        if eq_fail: break

    rows = []
    for r in range(985):
        rows.append({"relation": r, "i": int(block_i[r]), "j": int(block_j[r]), "scalar": int(s[r])})
    write_csv(out / "rho20_relation_table.csv", rows)
    cert = {"schema": "repro.rho20_scalar_representation@1", "status": "PASS" if not eq_fail else "FAIL", "pairs_checked": 985*985, "failure_count": len(eq_fail), "nonzero_product_pairs": nonzero_product_pairs}
    write_json(out / "certificate.json", cert)
    print(json.dumps(cert, indent=2))

if __name__ == "__main__":
    main()
