#!/usr/bin/env python3
"""
Canonical full S20 enumerator for subscript H↺ theory.

Permutation convention:
    p[position] = face_index occupying that position.

Face order:
    0..19 are lexicographic 3-subsets of H6 =
    ["B-", "B+", "V-", "V+", "S-", "S+"].

Full enumeration:
    for k in range(20!):
        yield unrank_s20(k)
"""

from math import factorial
from itertools import combinations
import argparse, json

H6 = ["B-", "B+", "V-", "V+", "S-", "S+"]
FACES = list(combinations(range(6), 3))
FACE_LABELS = ["{" + ",".join(H6[i] for i in f) + "}" for f in FACES]
N = factorial(20)

def unrank_s20(k: int):
    if not (0 <= k < N):
        raise ValueError(f"rank out of range: {k}; expected 0 <= k < {N}")
    items = list(range(20))
    p = []
    for m in range(20, 0, -1):
        f = factorial(m - 1)
        q, k = divmod(k, f)
        p.append(items.pop(q))
    return tuple(p)

def rank_s20(p):
    if len(p) != 20 or sorted(p) != list(range(20)):
        raise ValueError("p must be a permutation of 0..19")
    items = list(range(20))
    rank = 0
    for i, x in enumerate(p):
        j = items.index(x)
        rank += j * factorial(19 - i)
        items.pop(j)
    return rank

def cycle_decomposition(p):
    seen = [False] * 20
    cycles = []
    for i in range(20):
        if seen[i]:
            continue
        cur = i
        cyc = []
        while not seen[cur]:
            seen[cur] = True
            cyc.append(cur)
            cur = p[cur]
        if len(cyc) > 1:
            cycles.append(tuple(cyc))
    return cycles

def cycle_type(p):
    lengths = sorted([len(c) for c in cycle_decomposition(p)], reverse=True)
    fixed = 20 - sum(lengths)
    lengths += [1] * fixed
    return tuple(sorted(lengths, reverse=True))

def stream(start=0, count=None, labels=False):
    stop = N if count is None else min(N, start + count)
    for k in range(start, stop):
        p = unrank_s20(k)
        obj = {"rank": k, "perm": p, "cycle_type": cycle_type(p)}
        if labels:
            obj["faces"] = [FACE_LABELS[i] for i in p]
        yield obj

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rank", type=int, help="print permutation at rank k")
    ap.add_argument("--inverse-rank", type=str, help="comma-separated permutation of 0..19; print rank")
    ap.add_argument("--start", type=int, default=0, help="stream start rank")
    ap.add_argument("--count", type=int, default=None, help="stream count")
    ap.add_argument("--labels", action="store_true", help="include face labels")
    ap.add_argument("--faces", action="store_true", help="print face index table")
    args = ap.parse_args()

    if args.faces:
        print(json.dumps([{"index": i, "triple": list(f), "label": FACE_LABELS[i]} for i, f in enumerate(FACES)], ensure_ascii=False))
        return

    if args.inverse_rank is not None:
        p = tuple(int(x) for x in args.inverse_rank.split(","))
        print(rank_s20(p))
        return

    if args.rank is not None:
        p = unrank_s20(args.rank)
        obj = {"rank": args.rank, "perm": p, "cycle_type": cycle_type(p)}
        if args.labels:
            obj["faces"] = [FACE_LABELS[i] for i in p]
        print(json.dumps(obj, ensure_ascii=False))
        return

    for obj in stream(args.start, args.count, args.labels):
        print(json.dumps(obj, ensure_ascii=False))

if __name__ == "__main__":
    main()
