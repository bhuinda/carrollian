from pathlib import Path
import argparse, json
from collections import Counter
from common import *

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--d20", required=True); ap.add_argument("--t985", required=True); ap.add_argument("--quotients", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--sample", type=int, default=0)
    args = ap.parse_args()
    out = Path(args.out) / "03_central_wedderburn_lift"; out.mkdir(parents=True, exist_ok=True)

    d20 = json.loads(Path(args.d20).read_text())
    wd = d20["layer_certificates"]["05_drinfeld_wedderburn_trace"]
    lift = d20["layer_certificates"]["06_drinfeld_full_A985_lift"]
    sectors = wd["sector_profiles"]
    dims = lift["Wedderburn_recovery"]["block_dimensions_by_sector"]
    reg = lift["Wedderburn_recovery"]["regular_trace_values"]
    mult = wd["permutation_module_decomposition"]["multiplicities_by_sector"]
    ranks = wd["permutation_module_decomposition"]["permutation_ranks_by_sector"]

    rows = []
    for s in sectors:
        i = s["sector"]; d = dims[i]
        rows.append({"sector": i, "block_dimension_d": d, "regular_trace_d2": reg[i], "regular_trace_is_square": reg[i] == d*d, "multiplicity": mult[i], "rank": ranks[i], "rank_equals_d_times_m": ranks[i] == d*mult[i], "active_objects": ",".join(s.get("active_objects", []))})
    hist = Counter(dims)
    hist_rows = [{"d": d, "multiplicity": hist[d], "m_d2": hist[d]*d*d} for d in sorted(hist)]
    val = [
        {"check": "sector_count_39", "pass": len(sectors) == 39, "value": len(sectors)},
        {"check": "sum_m_d2_985", "pass": sum(r["m_d2"] for r in hist_rows) == 985, "value": sum(r["m_d2"] for r in hist_rows)},
        {"check": "trace_squares", "pass": all(r["regular_trace_is_square"] for r in rows), "value": True},
        {"check": "centrality_failures_zero", "pass": lift["full_A985_centrality_validation"]["failure_count"] == 0, "value": lift["full_A985_centrality_validation"]["failure_count"]},
    ]
    write_csv(out / "central_wedderburn_sector_profiles.csv", rows)
    write_csv(out / "central_block_dimension_histogram.csv", hist_rows)
    write_csv(out / "validation_checks.csv", val)
    cert = {"schema": "repro.central_wedderburn_lift@1", "status": "PASS" if all(x["pass"] for x in val) else "FAIL", "checks": val}
    write_json(out / "certificate.json", cert)
    print(json.dumps(cert, indent=2))

if __name__ == "__main__":
    main()
