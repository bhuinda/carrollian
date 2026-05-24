from pathlib import Path
import argparse, json, random
from common import *

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--d20", required=True); ap.add_argument("--t985", required=True); ap.add_argument("--quotients", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--sample", type=int, default=10000)
    args = ap.parse_args()
    out = Path(args.out) / "01_full_pentagon_genome"; out.mkdir(parents=True, exist_ok=True)

    d20, tz, qz = load_inputs(Path(args.d20), Path(args.t985), Path(args.quotients))
    triples = tz["triples"].astype("int64")
    pairmap = build_pairmap(triples)
    pairs_list = list(pairmap.keys())
    by_first = defaultdict(list)
    for a, b in pairs_list:
        by_first[a].append(b)

    def sample_chain(rng):
        for _ in range(1000):
            a, b = rng.choice(pairs_list)
            if not by_first.get(b): continue
            c = rng.choice(by_first[b])
            if not by_first.get(c): continue
            d = rng.choice(by_first[c])
            return (a, b, c, d)
        return tuple(rng.randrange(985) for _ in range(4))

    rng = random.Random(20260523)
    failures, sample_rows = [], []
    scatter_words = 0; max_scatter = 0; max_word = None
    for t in range(args.sample):
        w = sample_chain(rng)
        outs, sigs = pentagon_word(pairmap, *w)
        ok = all(outs[0] == o for o in outs[1:])
        if not ok:
            failures.append({"sample": t, "word": str(w), "hashes": ",".join(vec_hash(o) for o in outs)})
            break
        scatter = sum(sig_diff(sigs[i], sigs[j]) for i in range(5) for j in range(i + 1, 5))
        if scatter: scatter_words += 1
        if scatter > max_scatter:
            max_scatter, max_word = scatter, w
        if len(sample_rows) < 100:
            sample_rows.append({"sample": t, "word": str(w), "final_equal": ok, "internal_scatter_l1": scatter, "final_terms": len(outs[0]), "final_hash": vec_hash(outs[0])})

    write_csv(out / "t985_pentagon_sample.csv", sample_rows)
    write_csv(out / "t985_pentagon_failures.csv", failures)
    cert = {
        "schema": "repro.full_pentagon_genome@1",
        "status": "PASS" if not failures else "FAIL",
        "sampled_words": args.sample,
        "failures": len(failures),
        "internal_scatter_words": scatter_words,
        "max_internal_scatter_l1": max_scatter,
        "max_internal_scatter_word": str(max_word),
        "tensor_support": int(triples.shape[0]),
        "coefficient_total": int(triples[:,3].sum()),
    }
    write_json(out / "certificate.json", cert)
    print(json.dumps(cert, indent=2))

if __name__ == "__main__":
    main()
