import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap
import argparse, json, numpy as np
from pathlib import Path
from common import *

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--d20", required=True); ap.add_argument("--t985", required=True); ap.add_argument("--quotients", required=True); ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out) / "05_rho20_residue_intersections"
    d20, tz, qz = load_inputs(args.d20, args.t985, args.quotients)
    reps = tz["reps"].astype(np.int64)
    block_i = qz["block_i"].astype(np.int16); block_j = qz["block_j"].astype(np.int16)
    q42 = qz["q42_map"].astype(np.int16); q12 = qz["q12_map"].astype(np.int16)
    s = reps[:,4].astype(np.int64)
    rho = rho20_rows(block_i, block_j, s)
    q42r = quotient_rows(q42, 42)
    q12r = quotient_rows(q12, 12)
    ranks = {
        "rank_rho20": rank_mod(rho),
        "rank_q42": rank_mod(q42r),
        "rank_q12": rank_mod(q12r),
        "rank_rho20_plus_q42": rank_mod(np.vstack([rho, q42r])),
        "rank_rho20_plus_q12": rank_mod(np.vstack([rho, q12r])),
        "rank_all": rank_mod(np.vstack([rho, q42r, q12r])),
    }
    kernels = {
        "ker_rho20": 985 - ranks["rank_rho20"],
        "ker_q42": 985 - ranks["rank_q42"],
        "ker_q12": 985 - ranks["rank_q12"],
        "ker_rho20_inter_ker_q42": 985 - ranks["rank_rho20_plus_q42"],
        "ker_rho20_inter_ker_q12": 985 - ranks["rank_rho20_plus_q12"],
        "ker_rho20_inter_ker_q42_inter_ker_q12": 985 - ranks["rank_all"],
    }
    write_csv(out / "linear_map_rank_intersections.csv", [{"name": k, "value": v} for k,v in {**ranks, **kernels}.items()])
    checks = {"rank_rho20_is_36": ranks["rank_rho20"] == 36, "ker_rho20_is_949": kernels["ker_rho20"] == 949, "rank_q42_is_42": ranks["rank_q42"] == 42, "rank_q12_is_12": ranks["rank_q12"] == 12}
    cert = {"status": "PASS" if all(checks.values()) else "FAIL", "ranks": ranks, "kernel_dimensions": kernels, "checks": checks}
    write_json(out / "certificate.json", cert)
    print(json.dumps(cert, indent=2))
if __name__ == "__main__":
    main()
