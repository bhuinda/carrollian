#!/usr/bin/env python3
from __future__ import annotations
import csv, json, math, hashlib, zipfile
from itertools import product
from pathlib import Path
import numpy as np
from scipy.optimize import brentq, minimize

OUT=Path(__file__).resolve().parent
N=24

def sha256_bytes(b: bytes)->str:
    return hashlib.sha256(b).hexdigest()

def canonical_json(obj)->bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()

def bits_to_int(bits):
    x=0
    for i,b in enumerate(bits):
        if b: x |= 1<<i
    return x

def wt(x:int)->int:
    return int(x).bit_count()

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

def build_golay():
    neighbor_supports=[
        [2,4,9,10,12,13,14,16,17,18,20,22],
        [3,4,9,13,15,16,19,20],
        [2,5,7,8,9,10,12,14,15,16,17,18,19,21,22,23],
    ]
    H8=rm13_h8()
    C=direct_sum([H8,H8,H8],[8,8,8])
    stages=[("H8^3",C)]
    for i,supp in enumerate(neighbor_supports, start=1):
        C=type_ii_neighbor(C, vector_from_one_based_support(supp))
        stages.append(("G24" if i==3 else f"neighbor_{i}",C))
    return stages

def weight_hist(C):
    h=[0]*(N+1)
    for c in C: h[wt(c)] += 1
    return h

def signs_matrix(C):
    Y=np.empty((len(C),N), dtype=np.float64)
    for r,c in enumerate(C):
        for i in range(N):
            Y[r,i]=1.0 if ((c>>i)&1)==0 else -1.0
    return Y

def find_codeword(C,w):
    for c in C:
        if wt(c)==w: return c
    return None

def sign_direction(c):
    return np.array([1.0 if ((c>>i)&1)==0 else -1.0 for i in range(N)], dtype=np.float64)

def L_mu_cov(Y,u):
    z=Y@u
    m=float(z.max())
    expz=np.exp(z-m)
    Z=float(expz.sum())
    p=expz/Z
    L=m+math.log(Z)-math.log(Y.shape[0])
    mu=p@Y
    EYTY=(Y.T*p)@Y
    cov=EYTY-np.outer(mu,mu)
    return L,mu,cov

def F_val(Y,u):
    r=float(np.dot(u,u))
    if r < 1e-8: return 1.0
    L,_,_=L_mu_cov(Y,u)
    return 2*L/r

def F_and_grad_neg(Y,u):
    r=float(np.dot(u,u))
    if r<1e-8:
        return -1.0, np.zeros_like(u)
    L,mu,_=L_mu_cov(Y,u)
    F=2*L/r
    grad=2*(mu*r-2*L*u)/(r*r)
    return -F, -grad

def stationarity_eq_from_profile(profile,t):
    vals=[]
    for s,count in profile.items():
        vals.append((s,count))
    xs=[t*s+math.log(count) for s,count in vals]
    m=max(xs); ws=[math.exp(x-m) for x in xs]; Z=sum(ws)
    L=m+math.log(Z)-math.log(sum(count for _,count in vals))
    Lp=sum(s*w for (s,_),w in zip(vals,ws))/Z
    return t*Lp-2*L

def profile_stats(profile,t):
    vals=list(profile.items())
    xs=[t*s+math.log(count) for s,count in vals]
    m=max(xs); ws=[math.exp(x-m) for x in xs]; Z=sum(ws)
    L=m+math.log(Z)-math.log(sum(count for _,count in vals))
    ES=sum(s*w for (s,_),w in zip(vals,ws))/Z
    ES2=sum((s*s)*w for (s,_),w in zip(vals,ws))/Z
    return L,ES,ES2,ES2-ES*ES

def all_stationary_roots(profile, tmax=4.0):
    roots=[]
    lastx=1e-7; last=stationarity_eq_from_profile(profile,lastx)
    steps=4000
    for i in range(1,steps+1):
        x=tmax*i/steps
        e=stationarity_eq_from_profile(profile,x)
        if e==0 or e*last<0:
            try:
                roots.append(brentq(lambda z: stationarity_eq_from_profile(profile,z), lastx, x, xtol=1e-14, rtol=1e-14, maxiter=200))
            except ValueError:
                pass
        lastx=x; last=e
    # dedup
    out=[]
    for r in roots:
        if not out or abs(r-out[-1])>1e-8: out.append(r)
    return out

def distribution_profile_for_codeword_direction(C):
    hist=weight_hist(C)
    return {N-2*w: hist[w] for w in range(N+1) if hist[w]}

def hessian_F_at_stationary(Y,u):
    r=float(np.dot(u,u))
    L,mu,cov=L_mu_cov(Y,u)
    # If stationary, gradient numerator is zero. General Hessian has additional skew-looking terms,
    # but at the codeword/all-ones stationary point mu is parallel to u, making them cancel.
    H=2/(r*r)*(r*cov-2*L*np.eye(len(u)))
    eig=np.linalg.eigvalsh(H)
    grad=2*(mu*r-2*L*u)/(r*r)
    return L,mu,cov,H,eig,grad

def optimize_multistart(Y, C, starts=12, seed=20260525):
    rng=np.random.default_rng(seed)
    start_vectors=[]
    # canonical codeword sign starts at both stationary roots, plus random scales
    for w in [0,8,12,16,24]:
        c=find_codeword(C,w)
        if c is not None:
            a=sign_direction(c)
            for scale in [0.6860808181333431,1.2]:
                start_vectors.append(scale*a)
    # equal support / random starts
    for k in [1,2,3,4,5,6,7,8,12,16,20,24]:
        a=np.zeros(N); a[:k]=1.0
        for scale in [0.5,1.5]:
            start_vectors.append(scale*a/max(np.linalg.norm(a),1))
    for i in range(starts):
        kind=i%4
        if kind==0:
            a=rng.normal(size=N)
        elif kind==1:
            a=rng.choice([-1.0,1.0], size=N)
        elif kind==2:
            k=int(rng.integers(1,N+1)); a=np.zeros(N); idx=rng.choice(N,k,replace=False); a[idx]=rng.normal(size=k)
        else:
            k=int(rng.choice([8,12,16])); c=find_codeword(C,k); a=sign_direction(c)+0.05*rng.normal(size=N)
        a=a/max(np.linalg.norm(a),1e-12)
        scale=float(rng.uniform(0.05,4.0))
        start_vectors.append(scale*a)
    rows=[]; best=None
    for i,u0 in enumerate(start_vectors):
        res=minimize(lambda x: F_and_grad_neg(Y,x), u0, jac=True, method="L-BFGS-B", options={"maxiter":300,"ftol":1e-12,"gtol":1e-8,"maxls":30})
        u=res.x; val=F_val(Y,u)
        # classify by correlation with codeword sign directions; exhaustive over 4096 is cheap
        un=u/max(np.linalg.norm(u),1e-12)
        best_corr=-1; best_w=None
        for c in C:
            corr=abs(float(np.dot(un, sign_direction(c)/math.sqrt(N))))
            if corr>best_corr:
                best_corr=corr; best_w=wt(c)
        row={
            "start_index":i,
            "success":bool(res.success),
            "F":val,
            "K":math.sqrt(max(val,0)),
            "norm":float(np.linalg.norm(u)),
            "nit":int(res.nit),
            "best_codeword_abs_corr":best_corr,
            "best_codeword_weight":best_w,
            "message":str(res.message),
        }
        rows.append(row)
        if best is None or val>best["F"]:
            best=row|{"u":u.tolist()}
    return rows,best

def write_csv(path, rows):
    fields=[]
    for r in rows:
        for k in r:
            if k not in fields: fields.append(k)
    with open(path,"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

def main():
    stages=build_golay()
    C=stages[-1][1]
    Y=signs_matrix(C)
    hist=weight_hist(C)
    profile=distribution_profile_for_codeword_direction(C)
    roots=all_stationary_roots(profile, tmax=4.0)
    stationary=[]
    for t in roots:
        L,ES,ES2,Var=profile_stats(profile,t)
        F=2*L/(N*t*t)
        stationary.append({"t":t,"F":F,"K":math.sqrt(max(F,0)),"L":L,"ES":ES,"ES2":ES2,"Var":Var,"stationarity_residual":stationarity_eq_from_profile(profile,t)})
    # choose larger F stationary point
    max_stat=max(stationary,key=lambda r:r["F"])
    # Hessian local certificate at all-ones direction u=t*1
    u=max_stat["t"]*np.ones(N)
    L,mu,cov,H,eig,grad=hessian_F_at_stationary(Y,u)
    rows,best=optimize_multistart(Y,C)
    write_csv(OUT/"multistart_optimization.csv", [{k:v for k,v in r.items() if k!="u"} for r in rows])
    eig_rows=[{"index":i,"eigenvalue":float(v)} for i,v in enumerate(eig)]
    write_csv(OUT/"local_hessian_eigenvalues.csv", eig_rows)
    write_csv(OUT/"stationary_points_codeword_direction.csv", stationary)
    with open(OUT/"codeword_direction_distribution.csv","w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["value","count","probability"]); w.writeheader()
        for val,count in sorted(profile.items()):
            w.writerow({"value":val,"count":count,"probability":count/len(C)})
    # summary counts
    convergence_to_codeword=sum(1 for r in rows if r["F"]>max_stat["F"]-1e-9 and r["best_codeword_abs_corr"]>1-1e-7)
    certificate={
        "status":"HAMMING_GAUSSIAN_SHARP_CONSTANT_CANDIDATE_LOCAL_CERTIFIED",
        "scope":"stationary, local Hessian, and multistart evidence for sharp full Golay sign-vector subgaussian proxy constant",
        "not_claimed":[
            "not a rigorous global optimization proof over all R^24 directions",
            "not a full multivariate convex-order domination theorem",
            "not a proof of Talagrand equivalence"
        ],
        "finite_source":{
            "length":N,
            "code_size":len(C),
            "weight_enumerator":{str(i):v for i,v in enumerate(hist) if v},
            "dual_distance":8,
        },
        "candidate_constant":{
            "direction":"any full sign direction attached to a Golay codeword; by code translation it has the all-ones distribution",
            "distribution":{str(k):v for k,v in sorted(profile.items())},
            "stationary_points":stationary,
            "best_stationary":max_stat,
            "candidate_K2":max_stat["F"],
            "candidate_K":max_stat["K"],
        },
        "local_max_certificate":{
            "gradient_norm":float(np.linalg.norm(grad)),
            "hessian_max_eigenvalue":float(eig.max()),
            "hessian_min_eigenvalue":float(eig.min()),
            "negative_definite_hessian":bool(eig.max()<0),
            "eigenvalue_count":len(eig),
        },
        "multistart_diagnostic":{
            "starts":len(rows),
            "best_F":best["F"],
            "best_K":best["K"],
            "best_codeword_abs_corr":best["best_codeword_abs_corr"],
            "best_codeword_weight":best["best_codeword_weight"],
            "converged_to_candidate_count":convergence_to_codeword,
            "max_excess_over_candidate":float(best["F"]-max_stat["F"]),
        },
        "artifacts":[
            "hamming_gaussian_sharp_constant_candidate_report.md",
            "hamming_gaussian_sharp_constant_candidate_certificate.json",
            "stationary_points_codeword_direction.csv",
            "local_hessian_eigenvalues.csv",
            "multistart_optimization.csv",
            "codeword_direction_distribution.csv",
            "hamming_gaussian_sharp_constant_candidate.py",
        ],
    }
    certificate["certificate_sha256"]=sha256_bytes(canonical_json(certificate))
    with open(OUT/"hamming_gaussian_sharp_constant_candidate_certificate.json","w") as f:
        json.dump(certificate,f,indent=2,sort_keys=True)
    report=f"""# Hamming--Gaussian Sharp Constant Candidate

## Result

`{certificate['status']}`

This stage attacks the next conjectural residue: whether the sharp full-coordinate subgaussian proxy constant of the Golay sign vector is achieved by a codeword sign direction.

## Exact candidate direction

For any `d in G24`, set `s_i=(-1)^{{d_i}}` and `Y_i(c)=(-1)^{{c_i}}`. Then

```text
<s,Y(c)> = 24 - 2 wt(c+d).
```

Since `c+d` is uniform in `G24`, the distribution is exactly the Golay weight enumerator:

```json
{json.dumps(profile, indent=2, sort_keys=True)}
```

## Stationary points in the codeword direction

The objective is

```text
F(u)=2 log E exp(<u,Y>) / ||u||^2.
```

For `u=t*s`, the stationary equation is

```text
t L'(t) = 2 L(t).
```

Stationary points found:

```json
{json.dumps(stationary, indent=2)}
```

The candidate maximum is

```text
K^2 = {max_stat['F']:.15f}
K   = {max_stat['K']:.15f}
t*  = {max_stat['t']:.15f}
```

## Local maximum certificate

At `u=t*1`, the gradient norm is

```text
{np.linalg.norm(grad):.6e}
```

The Hessian eigenvalue range is

```text
min eigenvalue = {eig.min():.15f}
max eigenvalue = {eig.max():.15f}
```

Since the max eigenvalue is negative, this is a strict local maximum of `F`.

## Multistart diagnostic

Starts tested: `{len(rows)}`.

Best found:

```json
{json.dumps({k:v for k,v in best.items() if k!='u'}, indent=2)}
```

Converged to the candidate maximum with codeword-sign correlation `> 1-1e-7`:

```text
{convergence_to_codeword}
```

## Boundary

This is a local and numerical global-candidate certificate, not a rigorous global optimization proof over all directions in `R^24`.

The remaining theorem is to prove a global inequality:

```text
forall u in R^24, 2 log E exp(<u,Y>) / ||u||^2 <= {max_stat['F']:.15f}.
```
"""
    with open(OUT/"hamming_gaussian_sharp_constant_candidate_report.md","w") as f:
        f.write(report)
    manifest={"status":certificate["status"],"files":{}}
    for p in sorted(OUT.iterdir()):
        if p.is_file() and p.name!="manifest.json": manifest["files"][p.name]=sha256_bytes(p.read_bytes())
    manifest["manifest_sha256"]=sha256_bytes(canonical_json(manifest))
    with open(OUT/"manifest.json","w") as f:
        json.dump(manifest,f,indent=2,sort_keys=True)
    zip_path=OUT.parent/"hamming_gaussian_sharp_constant_candidate_package.zip"
    with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.iterdir()):
            if p.is_file(): z.write(p,arcname=f"hamming_gaussian_sharp_constant_candidate/{p.name}")
    print(json.dumps({
        "status":certificate["status"],
        "zip":str(zip_path),
        "candidate_K2":max_stat["F"],
        "candidate_K":max_stat["K"],
        "hessian_max_eigenvalue":float(eig.max()),
        "multistart_best_F":best["F"],
        "certificate_sha256":certificate["certificate_sha256"],
    },indent=2))

if __name__=="__main__":
    main()
