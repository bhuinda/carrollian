import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap
import argparse, json, random
from pathlib import Path
from common import *

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--d20", required=True); ap.add_argument("--t985", required=True); ap.add_argument("--quotients", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--sample", type=int, default=10000)
    args = ap.parse_args()
    out = Path(args.out) / "06_pentagon_sample"
    d20, tz, qz = load_inputs(args.d20, args.t985, args.quotients)
    triples = tz["triples"].astype("int64")
    pairmap = build_pairmap(triples)
    pairs = list(pairmap.keys())
    by_first = defaultdict(list)
    for a,b in pairs: by_first[a].append(b)
    rng = random.Random(20260523)
    def sample_chain():
        for _ in range(1000):
            a,b = rng.choice(pairs)
            if not by_first.get(b): continue
            c = rng.choice(by_first[b])
            if not by_first.get(c): continue
            d = rng.choice(by_first[c])
            return a,b,c,d
        return tuple(rng.randrange(985) for _ in range(4))
    rows, failures = [], []
    scatter_words = 0; max_scatter = 0
    for t in range(args.sample):
        w = sample_chain()
        outs, sigs = pentagon_word(pairmap, *w)
        ok = all(outs[0] == o for o in outs[1:])
        if not ok:
            failures.append({"sample": t, "word": str(w)})
            break
        scatter = sum(sig_diff(sigs[i], sigs[j]) for i in range(5) for j in range(i+1,5))
        if scatter: scatter_words += 1
        max_scatter = max(max_scatter, scatter)
        if len(rows) < 100:
            rows.append({"sample": t, "word": str(w), "final_equal": ok, "internal_scatter_l1": scatter, "final_terms": len(outs[0]), "final_hash": vec_hash(outs[0])})
    write_csv(out / "t985_pentagon_sample.csv", rows)
    write_csv(out / "t985_pentagon_failures.csv", failures)
    cert = {"status": "PASS" if not failures else "FAIL", "sampled_words": args.sample, "failures": len(failures), "internal_scatter_words": scatter_words, "max_internal_scatter_l1": max_scatter}
    write_json(out / "certificate.json", cert)
    print(json.dumps(cert, indent=2))
if __name__ == "__main__":
    main()
