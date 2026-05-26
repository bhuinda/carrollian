import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap
import argparse, json
from pathlib import Path
from collections import Counter
from common import *

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--d20", required=True); ap.add_argument("--t985", required=True); ap.add_argument("--quotients", required=True); ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out) / "02_wedderburn_from_d20json"
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
        rows.append({"sector": i, "d": d, "regular_trace": reg[i], "trace_square": reg[i] == d*d, "multiplicity": mult[i], "rank": ranks[i], "rank_equals_d_times_m": ranks[i] == d*mult[i], "active_objects": ",".join(s.get("active_objects", []))})
    hist = Counter(dims)
    hist_rows = [{"d": d, "multiplicity": hist[d], "m_d2": hist[d]*d*d} for d in sorted(hist)]
    checks = {
        "sector_count_39": len(sectors) == 39,
        "sum_m_d2_985": sum(x["m_d2"] for x in hist_rows) == 985,
        "trace_squares": all(x["trace_square"] for x in rows),
        "centrality_failures_zero": lift["full_A985_centrality_validation"]["failure_count"] == 0,
    }
    write_csv(out / "central_wedderburn_sector_profiles.csv", rows)
    write_csv(out / "central_block_dimension_histogram.csv", hist_rows)
    write_json(out / "certificate.json", {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks})
    print(json.dumps({"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}, indent=2))
if __name__ == "__main__":
    main()
