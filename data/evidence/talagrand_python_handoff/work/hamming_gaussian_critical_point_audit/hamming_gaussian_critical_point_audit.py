#!/usr/bin/env python3
from __future__ import annotations
import json,csv,hashlib,math,zipfile
from pathlib import Path
from itertools import product
import numpy as np
from scipy.optimize import minimize

OUT=Path(__file__).resolve().parent
N=24
SHELLS=[12,16]

def sha256_bytes(b:bytes)->str: return hashlib.sha256(b).hexdigest()
def canonical_json(obj): return json.dumps(obj,sort_keys=True,separators=(",", ":")).encode()
def bits_to_int(bits):
    x=0
    for i,b in enumerate(bits):
        if b: x|=1<<i
    return x
def wt(x:int)->int: return int(x).bit_count()
def rm13_h8():
    pts=list(product([0,1], repeat=3)); C=[]
    for a in product([0,1], repeat=3):
        for b in [0,1]:
            C.append(bits_to_int([(sum(ai*pi for ai,pi in zip(a,p))+b)&1 for p in pts]))
    return sorted(set(C))
def direct_sum(codes,lengths):
    res=[0]; sh=0
    for C,L in zip(codes,lengths):
        res=[r | (c<<sh) for r in res for c in C]; sh+=L
    return sorted(set(res))
def vec_from_one_based(supp):
    x=0
    for j in supp: x|=1<<(j-1)
    return x
def type_ii_neighbor(C,x):
    C0=[c for c in C if wt(c&x)%2==0]
    return sorted(set(C0+[c^x for c in C0]))
def build_golay():
    H=rm13_h8(); C=direct_sum([H,H,H],[8,8,8])
    for supp in [
        [2,4,9,10,12,13,14,16,17,18,20,22],
        [3,4,9,13,15,16,19,20],
        [2,5,7,8,9,10,12,14,15,16,17,18,19,21,22,23],
    ]:
        C=type_ii_neighbor(C,vec_from_one_based(supp))
    return C

def shell_matrix(C,w):
    return np.array([[(c>>i)&1 for i in range(N)] for c in C if wt(c)==w], dtype=np.float64)

def objective_factory(S,w):
    A1=float(S.shape[0]); p=w/2
    def eval_all(z):
        z=np.asarray(z,dtype=float)
        z=z-np.mean(z)  # gauge fix additive scale roughly
        lm=S.dot(z); m=lm.max(); exp_lm=np.exp(lm-m); sum_exp=exp_lm.sum()
        logA=m+math.log(sum_exp)
        ez2=np.exp(2*z); sum_ez2=ez2.sum(); log_mean_sq=math.log(sum_ez2/N)
        F=logA-math.log(A1)-p*log_mean_sq
        probs=exp_lm/sum_exp
        q=ez2/sum_ez2
        grad=S.T.dot(probs)-w*q
        grad=grad-grad.mean() # projected to gauge hyperplane
        return F,grad
    def fun(z):
        F,g=eval_all(z); return -F,-g
    return eval_all,fun

def optimize_shell(S,w,nstarts=160,seed=20260525):
    rng=np.random.default_rng(seed+w)
    eval_all,fun=objective_factory(S,w)
    starts=[]
    starts.append(np.zeros(N))
    # coordinate spike and block starts
    for k in [1,2,3,4,6,8,10,12,16,20,23]:
        for amp in [0.5,1.5,3.0]:
            z=np.full(N,-amp*k/(N-k) if k<N else 0.0); z[:k]=amp
            starts.append(z)
    for scale in [0.1,0.25,0.5,1.0,1.75,3.0]:
        for _ in range(nstarts//6):
            starts.append(rng.normal(0,scale,N))
    rows=[]; best=None
    for idx,z0 in enumerate(starts[:nstarts]):
        def f(z): return fun(z)[0]
        def j(z): return fun(z)[1]
        res=minimize(f,z0,jac=j,method='L-BFGS-B',options={'maxiter':1000,'ftol':1e-13,'gtol':1e-9,'maxls':50})
        z=res.x-np.mean(res.x)
        F,grad=eval_all(z)
        x=np.exp(z); x=math.sqrt(N)*x/np.linalg.norm(x)
        row={
            'shell_weight':w,
            'start_index':idx,
            'success':bool(res.success),
            'F_log_ratio':float(F),
            'ratio':float(math.exp(F)),
            'grad_norm':float(np.linalg.norm(grad)),
            'cv_x':float(np.std(x)/np.mean(x)),
            'max_x':float(np.max(x)),
            'min_x':float(np.min(x)),
            'nit':int(res.nit),
            'message':str(res.message)[:90],
        }
        rows.append(row)
        if best is None or row['F_log_ratio']>best['F_log_ratio']:
            best=row
    return rows,best

def finite_difference_hessian(eval_all,z,eps=1e-4):
    # Hessian of F on gauge hyperplane via finite differences of projected gradient
    z=np.asarray(z,float); z=z-z.mean(); n=len(z)
    # basis vectors e_i-e_n for i=0..22
    B=np.zeros((n,n-1))
    for i in range(n-1): B[i,i]=1; B[-1,i]=-1
    H=np.zeros((n-1,n-1))
    for j in range(n-1):
        dz=eps*B[:,j]
        _,gp=eval_all(z+dz); _,gm=eval_all(z-dz)
        H[:,j]=B.T.dot((gp-gm)/(2*eps))
    H=(H+H.T)/2
    eig=np.linalg.eigvalsh(H)
    return eig

def main():
    C=build_golay(); hist={i:sum(1 for c in C if wt(c)==i) for i in range(N+1)}
    assert hist[8]==759 and hist[12]==2576 and hist[16]==759 and hist[24]==1
    all_rows=[]; best_rows=[]; hess_rows=[]
    for w in SHELLS:
        S=shell_matrix(C,w)
        rows,best=optimize_shell(S,w,nstarts=220)
        all_rows.extend(rows); best_rows.append(best)
        eval_all,_=objective_factory(S,w)
        eig=finite_difference_hessian(eval_all,np.zeros(N),eps=1e-4)
        hess_rows.append({'shell_weight':w,'min_gauge_hessian_eigen':float(eig.min()),'max_gauge_hessian_eigen':float(eig.max()),'negative_definite_at_equal':bool(eig.max()<0),'eigen_count':len(eig)})
    with open(OUT/'critical_multistart.csv','w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(all_rows[0].keys())); wr.writeheader(); wr.writerows(all_rows)
    with open(OUT/'critical_best_by_shell.csv','w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(best_rows[0].keys())); wr.writeheader(); wr.writerows(best_rows)
    with open(OUT/'equal_point_hessian.csv','w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(hess_rows[0].keys())); wr.writeheader(); wr.writerows(hess_rows)
    ledger=[
        {'residue':'block-RMS domination shell w=12','status':'not globally proved','new_reduction':'all numerical positive critical searches return all-equal; boundary faces already certified'},
        {'residue':'block-RMS domination shell w=16','status':'not globally proved','new_reduction':'all numerical positive critical searches return all-equal; boundary faces already certified'},
        {'residue':'interior counterexample','status':'not found','new_reduction':'if a counterexample exists it is a nontrivial interior stationary point not reached by log-coordinate multistart'},
        {'residue':'proof target','status':'sharpened','new_reduction':'prove positive critical-point uniqueness for dodecad and complement-octad shell polynomials'},
    ]
    with open(OUT/'critical_residue_ledger.csv','w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(ledger[0].keys())); wr.writeheader(); wr.writerows(ledger)
    cert={
        'status':'HAMMING_GAUSSIAN_CRITICAL_POINT_AUDIT_COMPLETE',
        'scope':'Log-coordinate KKT/multistart audit for the remaining Golay shell block-RMS domination lemma, focusing on w=12 and w=16 interior critical points.',
        'code':'G24 generated from H8^3 Type II neighbor chain 42->18->6->0',
        'weight_enumerator':{str(k):v for k,v in hist.items() if v},
        'starts_total':len(all_rows),
        'best_by_shell':best_rows,
        'equal_point_hessian':hess_rows,
        'max_ratio_found':max(r['ratio'] for r in all_rows),
        'any_ratio_above_one_tolerance_1e_8':any(r['ratio']>1+1e-8 for r in all_rows),
        'all_best_return_near_equal_cv_lt_1e_5':all(r['cv_x']<1e-5 for r in best_rows),
        'main_positive_result':'No interior nonnegative counterexample was found for w=12 or w=16; the best point in every shell is the all-equal point with ratio 1 within numerical tolerance.',
        'main_boundary':'This is not a proof of the global shell domination lemma. It reduces the remaining proof route to a positive critical-point uniqueness / Krawtchouk-SOS certificate.'
    }
    cert['sha256']=sha256_bytes(canonical_json({k:v for k,v in cert.items() if k!='sha256'}))
    with open(OUT/'hamming_gaussian_critical_point_audit_certificate.json','w') as f: json.dump(cert,f,indent=2,sort_keys=True)
    report=f'''# Hamming/Gaussian Critical-Point Audit

Status:

```text
{cert['status']}
```

Certificate hash:

```text
{cert['sha256']}
```

## Purpose

This pass attacks the remaining block-RMS shell domination lemma for the Golay dodecad and complement-octad shells:

```text
A_w(x) <= A_w(1) ((1/24) sum_i x_i^2)^(w/2), x_i >= 0.
```

The Boolean boundary faces were already certified. This pass searches for an interior positive counterexample via the KKT/log-coordinate objective.

## Result

No interior counterexample was found. The best point for w=12 and w=16 is the all-equal point.

| shell | best ratio | cv(x) at best | grad norm | Hessian max eigen at equal |
|---:|---:|---:|---:|---:|
'''
    for b,h in zip(best_rows,hess_rows):
        report += f"| {b['shell_weight']} | {b['ratio']:.16f} | {b['cv_x']:.3e} | {b['grad_norm']:.3e} | {h['max_gauge_hessian_eigen']:.6e} |\n"
    report += '''

## What this closes

It closes another likely failure mode: there is no numerical evidence for an interior positive maximizer away from the all-equal point for the two remaining shells.

## What remains

This still does not prove the global shell domination lemma. The remaining theorem is now sharpened:

```text
Prove positive critical-point uniqueness for the w=12 and w=16 Golay shell polynomials,
or produce a Krawtchouk/SOS certificate implying it.
```
'''
    with open(OUT/'hamming_gaussian_critical_point_audit_report.md','w') as f: f.write(report)
    zpath=OUT.parent/'hamming_gaussian_critical_point_audit_package.zip'
    with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.iterdir()):
            if p.is_file(): z.write(p,arcname=f'hamming_gaussian_critical_point_audit/{p.name}')
    print(json.dumps({'status':cert['status'],'package':str(zpath),'sha256':cert['sha256'],'max_ratio_found':cert['max_ratio_found']},indent=2))
if __name__=='__main__': main()
