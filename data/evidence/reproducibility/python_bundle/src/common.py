from pathlib import Path
from collections import defaultdict
import csv, hashlib, json, zipfile
import numpy as np

P = 1000003

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def write_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = []
    for r in rows:
        for k in r:
            if k not in fields:
                fields.append(k)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fields)
        w.writeheader()
        w.writerows(rows)

def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")

def load_inputs(d20_path, t985_path, quotients_path):
    d20 = json.loads(Path(d20_path).read_text(encoding="utf-8"))
    tz = np.load(t985_path, allow_pickle=True)
    qz = np.load(quotients_path, allow_pickle=True)
    return d20, tz, qz

def build_pairmap(triples):
    pairmap = defaultdict(list)
    for a, b, c, p in triples:
        pairmap[(int(a), int(b))].append((int(c), int(p)))
    return pairmap

def rank_mod(mat, p=P):
    A = np.array(mat, dtype=np.int64) % p
    m, n = A.shape
    rank = 0
    row = 0
    for col in range(n):
        pivot = None
        for r in range(row, m):
            if A[r, col] % p:
                pivot = r
                break
        if pivot is None:
            continue
        if pivot != row:
            A[[row, pivot]] = A[[pivot, row]]
        inv = pow(int(A[row, col]), -1, p)
        A[row, :] = (A[row, :] * inv) % p
        for r in range(m):
            if r != row and A[r, col] % p:
                A[r, :] = (A[r, :] - A[r, col] * A[row, :]) % p
        rank += 1
        row += 1
        if row == m:
            break
    return rank

def rho20_rows(block_i, block_j, scalars, n=985):
    rows = np.zeros((36, n), dtype=np.int64)
    for a in range(n):
        rows[int(block_i[a]) * 6 + int(block_j[a]), a] = int(scalars[a]) % P
    return rows

def quotient_rows(qmap, qn, n=985):
    rows = np.zeros((qn, n), dtype=np.int64)
    for a in range(n):
        rows[int(qmap[a]), a] = 1
    return rows

def rho_image_of_vec(vec, block_i, block_j, scalars):
    out = defaultdict(int)
    for r, coef in vec.items():
        out[(int(block_i[r]), int(block_j[r]))] += int(coef) * int(scalars[r])
    return {k: v for k, v in out.items() if v}

def basis_vec(r):
    return {int(r): 1}

def mul_vec(pairmap, x, y):
    out = {}
    for a, ca in x.items():
        for b, cb in y.items():
            for c, p in pairmap.get((a, b), ()):
                out[c] = out.get(c, 0) + ca * cb * p
    return {k: v for k, v in out.items() if v}

def vec_hash(d):
    s = ";".join(f"{k}:{v}" for k, v in sorted(d.items()))
    return hashlib.sha256(s.encode()).hexdigest()

def sig_diff(sig1, sig2):
    total = 0
    for idx in [0, 1]:
        keys = set(sig1[idx]) | set(sig2[idx])
        for k in keys:
            total += abs(sig1[idx].get(k, 0) - sig2[idx].get(k, 0))
    return total

def pentagon_word(pairmap, a, b, c, d):
    A, B, C, D = map(basis_vec, [a, b, c, d])
    ab, bc, cd = mul_vec(pairmap, A, B), mul_vec(pairmap, B, C), mul_vec(pairmap, C, D)
    p1m = mul_vec(pairmap, ab, C); p1 = mul_vec(pairmap, p1m, D)
    p2 = mul_vec(pairmap, ab, cd)
    p3m = mul_vec(pairmap, A, bc); p3 = mul_vec(pairmap, p3m, D)
    p4m = mul_vec(pairmap, bc, D); p4 = mul_vec(pairmap, A, p4m)
    p5m = mul_vec(pairmap, B, cd); p5 = mul_vec(pairmap, A, p5m)
    return [p1, p2, p3, p4, p5], [(ab, p1m), (ab, cd), (bc, p3m), (bc, p4m), (cd, p5m)]
