import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap
import argparse, json, numpy as np
from pathlib import Path
from collections import defaultdict
from common import *

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--d20", required=True); ap.add_argument("--t985", required=True); ap.add_argument("--quotients", required=True); ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out) / "03_rho20_scalar_representation"
    d20, tz, qz = load_inputs(args.d20, args.t985, args.quotients)
    triples = tz["triples"].astype(np.int64); reps = tz["reps"].astype(np.int64)
    block_i = qz["block_i"].astype(np.int16); block_j = qz["block_j"].astype(np.int16)
    s = reps[:,4].astype(np.int64)
    rhs = defaultdict(int)
    for a,b,c,p in triples:
        rhs[(int(a),int(b))] += int(p)*int(s[c])
    fails = []
    nonzero = 0
    for a in range(985):
        for b in range(985):
            lhs = int(s[a])*int(s[b]) if int(block_j[a]) == int(block_i[b]) else 0
            r = rhs.get((a,b), 0)
            if r: nonzero += 1
            if lhs != r:
                fails.append({"a": a, "b": b, "lhs": lhs, "rhs": r})
                break
        if fails:
            break
    write_csv(out / "rho20_relation_table.csv", [{"relation": r, "i": int(block_i[r]), "j": int(block_j[r]), "scalar": int(s[r])} for r in range(985)])
    cert = {"status": "PASS" if not fails else "FAIL", "pairs_checked": 985*985, "failure_count": len(fails), "nonzero_product_pairs": nonzero}
    write_json(out / "certificate.json", cert)
    print(json.dumps(cert, indent=2))
if __name__ == "__main__":
    main()
