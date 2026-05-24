from pathlib import Path
import argparse, json
from common import *

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--d20", required=True); ap.add_argument("--t985", required=True); ap.add_argument("--quotients", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--sample", type=int, default=0)
    args = ap.parse_args()
    out = Path(args.out) / "07_rho20_residue_intersections"; out.mkdir(parents=True, exist_ok=True)

    d20, tz, qz = load_inputs(Path(args.d20), Path(args.t985), Path(args.quotients))
    reps = tz["reps"].astype("int64")
    block_i = qz["block_i"].astype("int16"); block_j = qz["block_j"].astype("int16")
    q42 = qz["q42_map"].astype("int16"); q12 = qz["q12_map"].astype("int16")
    s = reps[:,4].astype("int64")
    rho = rho20_rows(block_i, block_j, s)
    q42r = quotient_rows(q42, 42)
    q12r = quotient_rows(q12, 12)
    ranks = {
        "rank_rho20": rank_mod(rho),
        "rank_q42": rank_mod(q42r),
        "rank_q12": rank_mod(q12r),
        "rank_rho20_plus_q42": rank_mod(np.vstack([rho,q42r])),
        "rank_rho20_plus_q12": rank_mod(np.vstack([rho,q12r])),
        "rank_all": rank_mod(np.vstack([rho,q42r,q12r])),
    }
    kernels = {
        "ker_rho20": 985 - ranks["rank_rho20"],
        "ker_q42": 985 - ranks["rank_q42"],
        "ker_q12": 985 - ranks["rank_q12"],
        "ker_rho20_inter_ker_q42": 985 - ranks["rank_rho20_plus_q42"],
        "ker_rho20_inter_ker_q12": 985 - ranks["rank_rho20_plus_q12"],
        "ker_rho20_inter_ker_q42_inter_ker_q12": 985 - ranks["rank_all"],
    }
    rows = [{"map": k, "rank_or_dim": v} for k,v in {**ranks, **kernels}.items()]
    write_csv(out / "linear_map_rank_intersections.csv", rows)
    cert = {
        "schema": "repro.rho20_residue_intersections@1",
        "status": "PASS",
        "ranks": ranks,
        "kernel_dimensions": kernels,
        "checks": {
            "rank_rho20_is_36": ranks["rank_rho20"] == 36,
            "ker_rho20_is_949": kernels["ker_rho20"] == 949,
            "rank_q42_is_42": ranks["rank_q42"] == 42,
            "rank_q12_is_12": ranks["rank_q12"] == 12,
        }
    }
    cert["status"] = "PASS" if all(cert["checks"].values()) else "FAIL"
    write_json(out / "certificate.json", cert)
    print(json.dumps(cert, indent=2))

if __name__ == "__main__":
    main()
