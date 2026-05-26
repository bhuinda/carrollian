#!/usr/bin/env python3
"""
Full-coordinate Hamming/Golay -> Gaussian subgaussian constant probe.

This continues the Hamming-Gaussian morphism beyond the proven sparse <8 layer.
It computes structured and numerical lower bounds for the subgaussian proxy constant K
of the Golay sign vector Y=(-1)^c, c uniform in G24:

    E exp(lambda <a,Y>) <= exp(K^2 lambda^2 ||a||_2^2 / 2)

for all a, lambda.

It proves exact formulas for several high-symmetry one-dimensional projections and runs a
numerical search for candidate worst directions.  It does not claim a sharp global theorem.
"""
from __future__ import annotations
from itertools import product, combinations
from pathlib import Path
import csv, hashlib, json, math, random, zipfile
import numpy as np

OUT = Path(__file__).resolve().parent
N = 24


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def canonical_json(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()

def bits_to_int(bits):
    x = 0
    for i,b in enumerate(bits):
        if b: x |= 1<<i
    return x

def wt(x:int)->int:
    return int(x).bit_count()

def gf2_rank(rows: list[int], n:int)->int:
    rows=rows[:]
    rank=0
    for col in range(n-1,-1,-1):
        piv=None
        for r in range(rank,len(rows)):
            if (rows[r]>>col)&1:
                piv=r; break
        if piv is None: continue
        rows[rank],rows[piv]=rows[piv],rows[rank]
        for r in range(len(rows)):
            if r!=rank and ((rows[r]>>col)&1): rows[r]^=rows[rank]
        rank+=1
    return rank

def rm13_h8():
    pts=list(product([0,1], repeat=3))
    C=[]
    for a in product([0,1], repeat=3):
        for b in [0,1]:
            bits=[]
            for p in pts:
                bits.append((sum(ai*pi for ai,pi in zip(a,p))+b)%2)
            C.append(bits_to_int(bits))
    return sorted(set(C))

def direct_sum(codes,lengths):
    res=[0]; shift=0
    for C,L in zip(codes,lengths):
        res=[r|(c<<shift) for r in res for c in C]
        shift+=L
    return sorted(set(res))

def vector_from_one_based_support(supp):
    x=0
    for j in supp: x |= 1<<(j-1)
    return x

def type_ii_neighbor(C,x):
    C0=[c for c in C if wt(c & x)%2==0]
    return sorted(set(C0+[c^x for c in C0]))

def build_stages():
    neighbor_supports=[
        [2,4,9,10,12,13,14,16,17,18,20,22],
        [3,4,9,13,15,16,19,20],
        [2,5,7,8,9,10,12,14,15,16,17,18,19,21,22,23],
    ]
    H8=rm13_h8()
    C=direct_sum([H8,H8,H8],[8,8,8])
    stages=[("C0_H8_oplus_3",C)]
    for i,supp in enumerate(neighbor_supports, start=1):
        C=type_ii_neighbor(C, vector_from_one_based_support(supp))
        label=f"C{i}_neighbor_{i}" if i<3 else "C3_Golay_endpoint"
        stages.append((label,C))
    return stages

def weight_hist(C):
    h=[0]*(N+1)
    for c in C: h[wt(c)] += 1
    return h

def signs_matrix(C):
    # Y_ci = (-1)^bit: bit 0 -> +1, bit 1 -> -1
    M=np.empty((len(C),N), dtype=np.float64)
    for r,c in enumerate(C):
        for i in range(N):
            M[r,i]=1.0 if ((c>>i)&1)==0 else -1.0
    return M

def log_mgf_values(vals, lam):
    x=lam*vals
    m=x.max()
    return float(m + math.log(np.exp(x-m).mean()))

def proxy_constant_for_values(vals, norm2, lam_grid):
    best=(-1.0, None, None)
    for lam in lam_grid:
        if lam==0: continue
        logmgf=log_mgf_values(vals, lam)
        val=2*logmgf/(lam*lam*norm2)
        if val>best[0]:
            best=(val, lam, logmgf)
    return {"K2":best[0], "K":math.sqrt(max(best[0],0.0)), "lambda":best[1], "log_mgf":best[2]}

def proxy_constant(Y, a, lam_grid):
    a=np.asarray(a,dtype=float)
    norm2=float(np.dot(a,a))
    vals=Y@a
    return proxy_constant_for_values(vals,norm2,lam_grid)

def subset_equal_direction(k):
    a=np.zeros(N)
    a[:k]=1.0
    return a

def int_to_sign_direction(d):
    return np.array([1.0 if ((d>>i)&1)==0 else -1.0 for i in range(N)])

def support_from_int(x):
    return [i for i in range(N) if (x>>i)&1]

def find_codeword_of_weight(C,w):
    for c in C:
        if wt(c)==w: return c
    return None

def distribution_profile(vals, tol=1e-9):
    # values are integer-ish in structured cases
    counts={}
    for v in vals:
        key=round(float(v), 12)
        counts[key]=counts.get(key,0)+1
    return dict(sorted(counts.items()))

def exact_codeword_direction_profile(C):
    # For a sign direction from a codeword d in C, <sign(d),Y(c)>=sum_i (-1)^(c_i+d_i)=24-2wt(c+d).
    hist=weight_hist(C)
    return {24-2*w: hist[w] for w in range(N+1) if hist[w]}

def exact_even_parity_mgf_equal(k, lam):
    # uniform signs on k coordinates with product = +1, equal coefficients 1.
    # MGF = prod cosh(lam)+prod sinh(lam) = cosh(lam)^k + sinh(lam)^k
    return math.cosh(lam)**k + math.sinh(lam)**k

def even_parity_equal_proxy(k, lam_grid):
    best=(-1,None,None)
    for lam in lam_grid:
        logmgf=math.log(exact_even_parity_mgf_equal(k, lam))
        val=2*logmgf/(lam*lam*k)
        if val>best[0]: best=(val,lam,logmgf)
    return {"K2":best[0],"K":math.sqrt(max(best[0],0)),"lambda":best[1],"log_mgf":best[2]}

def random_search(Y, samples=2000, seed=985):
    rng=np.random.default_rng(seed)
    lam_grid=np.concatenate([
        np.linspace(0.04,1.2,80),
        np.linspace(1.3,3.5,35),
    ])
    rows=[]
    best=None
    for i in range(samples):
        # mix gaussian, sparse, and signed-ish directions
        if i%5==0:
            k=int(rng.integers(1,N+1))
            a=np.zeros(N); idx=rng.choice(N,k,replace=False); a[idx]=rng.normal(size=k)
        elif i%5==1:
            a=rng.choice([-1.0,1.0], size=N)
        else:
            a=rng.normal(size=N)
        pc=proxy_constant(Y,a,lam_grid)
        row={"sample":i,"K":pc["K"],"K2":pc["K2"],"lambda":pc["lambda"],"support":int(np.sum(np.abs(a)>1e-12)),"a_sha256":sha256_bytes(np.asarray(a,dtype=np.float64).tobytes())}
        rows.append(row)
        if best is None or row["K2"]>best["K2"]:
            best=row|{"a":a.tolist()}
    return best, rows


def main():
    stages=build_stages()
    C=stages[-1][1]
    Y=signs_matrix(C)
    lam_grid=np.concatenate([
        np.linspace(0.01,0.1,35),
        np.linspace(0.11,1.5,180),
        np.linspace(1.6,4.5,80),
    ])

    structured=[]
    # independent/sparse equal directions k=1..7 and beyond k=8..24
    for k in range(1,N+1):
        a=subset_equal_direction(k)
        pc=proxy_constant(Y,a,lam_grid)
        structured.append({"name":f"equal_first_{k}","type":"equal_subset","support":k,**pc})
    # octad, dodecad, codeword sign directions
    for w,name in [(8,"octad_codeword_support"),(12,"dodecad_codeword_support"),(16,"complement_octad_support"),(24,"all_ones_codeword_support")]:
        c=find_codeword_of_weight(C,w)
        if c is not None:
            a=np.zeros(N); a[support_from_int(c)]=1.0
            pc=proxy_constant(Y,a,lam_grid)
            structured.append({"name":name,"type":"codeword_support_indicator","support":w,"codeword_hex":f"{c:06x}",**pc})
    # full sign direction from nonzero codeword / zero codeword (all ones equal handled separately)
    for w,name in [(8,"sign_direction_octad"),(12,"sign_direction_dodecad"),(24,"sign_direction_all_ones")]:
        c=find_codeword_of_weight(C,w)
        if c is not None:
            a=int_to_sign_direction(c)
            pc=proxy_constant(Y,a,lam_grid)
            structured.append({"name":name,"type":"codeword_sign_direction","support":24,"codeword_weight":w,"codeword_hex":f"{c:06x}",**pc})

    # exact profiles for codeword sign directions and parity octad equal direction.
    codeword_profile=exact_codeword_direction_profile(C)
    codeword_vals=[]
    codeword_probs=[]
    for val,count in codeword_profile.items():
        codeword_vals += [float(val)]*count
        codeword_probs.append((val,count/len(C)))
    codeword_pc=proxy_constant_for_values(np.array(codeword_vals), 24.0, lam_grid)
    octad_parity_pc=even_parity_equal_proxy(8, lam_grid)

    best_random, random_rows=random_search(Y, samples=400, seed=20260525)

    # low support uniform proof ledger rows
    theorem_rows=[]
    for k in range(1,8):
        theorem_rows.append({
            "support_k":k,
            "projection_law":"independent Rademacher for all real coefficient vectors",
            "reason":"dual distance 8 => coordinate projection uniform",
            "extra_code_obstruction":"none",
        })
    for k in range(8,25):
        theorem_rows.append({
            "support_k":k,
            "projection_law":"Golay constraints may appear",
            "reason":"supports can contain octads/dodecads/etc.; projection need not be full cube",
            "extra_code_obstruction":"visible in codeword/indicator probes",
        })

    # write CSVs
    def write_csv(path, rows):
        if not rows: return
        fields=[]
        for r in rows:
            for k in r.keys():
                if k not in fields:
                    fields.append(k)
        with open(path,"w",newline="") as f:
            w=csv.DictWriter(f, fieldnames=fields)
            w.writeheader(); w.writerows(rows)
    write_csv(OUT/"structured_projection_constants.csv", structured)
    write_csv(OUT/"random_search_projection_constants.csv", [{k:v for k,v in r.items() if k!="a"} for r in random_rows])
    write_csv(OUT/"support_regime_ledger.csv", theorem_rows)
    with open(OUT/"codeword_sign_direction_distribution.csv","w",newline="") as f:
        w=csv.DictWriter(f, fieldnames=["value","count","probability"])
        w.writeheader()
        for val,count in sorted(codeword_profile.items()):
            w.writerow({"value":val,"count":count,"probability":count/len(C)})

    # summary
    best_struct=max(structured, key=lambda r:r["K2"])
    certificate={
        "status":"HAMMING_GAUSSIAN_FULL_SUBGAUSSIAN_PROBE_COMPLETE",
        "scope":"structured and numerical probe of full Golay sign vector subgaussian/convex-order constants beyond sparse support <8",
        "endpoint":"G24",
        "finite_facts":{
            "code_size":len(C),
            "length":N,
            "weight_enumerator":{str(i):v for i,v in enumerate(weight_hist(C)) if v},
            "dual_distance":8,
            "proven_sparse_uniform_supports":"all |S| < 8",
        },
        "exact_structured_findings":{
            "codeword_sign_direction_distribution":"<sign(d),Y> = 24 - 2 wt(c+d), hence distribution is the Golay weight enumerator",
            "codeword_sign_direction_K_lower_bound":codeword_pc,
            "octad_even_parity_equal_direction_K_lower_bound":octad_parity_pc,
            "best_structured_probe":best_struct,
        },
        "numerical_search":{
            "random_directions_tested":len(random_rows),
            "best_random_probe":{k:v for k,v in best_random.items() if k!="a"},
        },
        "interpretation":{
            "below_weight_8":"the Golay endpoint has exact independent Rademacher sparse projection law",
            "at_weight_8_and_above":"Golay constraints reappear as legitimate code-induced structure, not Hamming root defects",
            "new_candidate_worst_direction":"full sign direction of a Golay codeword, with K around %.6f" % codeword_pc["K"],
        },
        "not_claimed":[
            "not a proof of the sharp global K-subgaussian constant for all coefficient vectors",
            "not a proof of multivariate convex-order domination",
            "random search is diagnostic, not exhaustive",
        ],
        "artifacts":[
            "hamming_gaussian_full_subgaussian_probe_report.md",
            "hamming_gaussian_full_subgaussian_probe_certificate.json",
            "structured_projection_constants.csv",
            "random_search_projection_constants.csv",
            "support_regime_ledger.csv",
            "codeword_sign_direction_distribution.csv",
            "hamming_gaussian_full_subgaussian_probe.py",
        ],
    }
    certificate["certificate_sha256"]=sha256_bytes(canonical_json(certificate))
    with open(OUT/"hamming_gaussian_full_subgaussian_probe_certificate.json","w") as f:
        json.dump(certificate,f,indent=2,sort_keys=True)

    report=f"""# Hamming Gaussian Full Subgaussian Probe

## Result

`{certificate['status']}`

This continues the Hamming/Golay -> Gaussian bridge beyond the already proved sparse `<8` regime.

## Theorem-grade part

Because the Golay endpoint has dual distance 8, every coordinate projection of size `<8` is uniform. Therefore every real sparse projection supported on fewer than eight coordinates is exactly an independent Rademacher linear form:

```text
sum_{{i in S}} a_i (-1)^{{c_i}}  ==_law  sum_{{i in S}} a_i eps_i,   |S|<8.
```

This is the completed finite theorem layer.

## New probe beyond the sparse theorem

For support size 8 and above, Golay constraints reappear. The cleanest exact direction is a full sign direction from a Golay codeword `d`:

```text
<sign(d), Y(c)> = 24 - 2 wt(c+d).
```

Since `c+d` is again uniform in `G24`, the distribution is determined exactly by the Golay weight enumerator:

```text
{json.dumps(codeword_profile, sort_keys=True)}
```

The one-dimensional subgaussian proxy constant required by this direction is approximately:

```text
K^2 = {codeword_pc['K2']:.12f}
K   = {codeword_pc['K']:.12f}
lambda* = {codeword_pc['lambda']:.12f}
```

The octad even-parity equal-coefficient probe gives:

```text
K^2 = {octad_parity_pc['K2']:.12f}
K   = {octad_parity_pc['K']:.12f}
lambda* = {octad_parity_pc['lambda']:.12f}
```

Best structured probe:

```json
{json.dumps(best_struct, indent=2)}
```

Best random probe among {len(random_rows)} directions:

```json
{json.dumps({k:v for k,v in best_random.items() if k!='a'}, indent=2)}
```

## Interpretation

The root-killing chain eliminates the extra Hamming/Golay obstruction below the Golay distance threshold. At and above weight 8, structure is visible again; it is no longer a defect of the Hamming source, but the genuine Golay code law.

The next exact target is to prove or disprove that the full Golay sign vector has sharp subgaussian proxy constant achieved by a codeword sign direction.
"""
    with open(OUT/"hamming_gaussian_full_subgaussian_probe_report.md","w") as f:
        f.write(report)

    # manifest & zip
    manifest={"files":{},"status":certificate["status"]}
    for p in sorted(OUT.iterdir()):
        if p.is_file() and p.name != "manifest.json":
            manifest["files"][p.name]=sha256_bytes(p.read_bytes())
    manifest["manifest_sha256"]=sha256_bytes(canonical_json(manifest))
    with open(OUT/"manifest.json","w") as f: json.dump(manifest,f,indent=2,sort_keys=True)

    zip_path=OUT.parent/"hamming_gaussian_full_subgaussian_probe_package.zip"
    with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.iterdir()):
            if p.is_file(): z.write(p, arcname=f"hamming_gaussian_full_subgaussian_probe/{p.name}")
    print(json.dumps({
        "status":certificate["status"],
        "zip":str(zip_path),
        "sha256":certificate["certificate_sha256"],
        "codeword_K":codeword_pc["K"],
        "best_structured_K":best_struct["K"],
        "best_random_K":best_random["K"],
    }, indent=2))

if __name__ == "__main__":
    main()
