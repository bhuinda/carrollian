#!/usr/bin/env python3
"""Chunked exact rationalizer for three-level pairwise-square cone certificates.

Uses unscaled NNLS support, then exact SymPy solve on that support.

Example:
  python chunked_exact_pairwise_square_rationalize.py three_level_terwilliger_profiles.csv \
    --shell 16 --start 0 --stop 250 --out exact_w16_000_250
"""
from __future__ import annotations
import argparse, csv, json, math, hashlib
from pathlib import Path
from functools import lru_cache
import numpy as np
import pandas as pd
from scipy.optimize import nnls
import sympy as sp

EXPECTED = {12: 2576, 16: 759}

def monomials_deg(d):
    return [(i,j,d-i-j) for i in range(d+1) for j in range(d+1-i)]

@lru_cache(None)
def pairwise_basis(w):
    mono=monomials_deg(w); idx={m:i for i,m in enumerate(mono)}
    cols=[]; meta=[]
    for name,pair in [('ab',(0,1)),('ac',(0,2)),('bc',(1,2))]:
        for m in monomials_deg(w-2):
            col=np.zeros(len(mono), dtype=int)
            p,q=pair
            e=list(m); e[p]+=2; col[idx[tuple(e)]] += 1
            e=list(m); e[p]+=1; e[q]+=1; col[idx[tuple(e)]] += -2
            e=list(m); e[q]+=2; col[idx[tuple(e)]] += 1
            cols.append(col); meta.append((name,*m))
    return mono, np.stack(cols, axis=1), meta

def gap_vec_integer(row):
    w=int(row.shell); d=w//2; A1=EXPECTED[w]
    mono,A,meta=pairwise_basis(w); idx={m:i for i,m in enumerate(mono)}
    b=np.zeros(len(mono), dtype=object)
    n1,n2,n3=int(row.first_size), int(row.second_size), int(row.rest_size)
    fact=math.factorial; fd=fact(d)
    for p in range(d+1):
        for q in range(d+1-p):
            r=d-p-q
            b[idx[(2*p,2*q,2*r)]] += A1*fd//(fact(p)*fact(q)*fact(r))*(n1**p)*(n2**q)*(n3**r)
    prof=np.fromstring(row.profile, sep=',', dtype=np.int64).reshape((w+1,w+1))
    scale=24**d
    for j,k in np.argwhere(prof):
        b[idx[(int(j),int(k),w-int(j)-int(k))]] -= scale*int(prof[j,k])
    return [int(x) for x in b]

def exactify(row, tol):
    shell=int(row.shell); pid=int(row.profile_id)
    mono,A_np,meta=pairwise_basis(shell)
    b_int=gap_vec_integer(row)
    b_np=np.array([float(x) for x in b_int])
    if np.max(np.abs(b_np)) == 0:
        return {'shell':shell,'profile_id':pid,'status':'EXACT_ZERO_GAP_PASS','support_size':0,'nnls_linf_unscaled':0.0,'exact_residual_zero':True,'all_coefficients_nonnegative':True}, []
    x,res=nnls(A_np,b_np,maxiter=5000)
    support=[i for i,v in enumerate(x) if v>tol]
    A_S=sp.Matrix([[int(A_np[r,c]) for c in support] for r in range(A_np.shape[0])])
    b_S=sp.Matrix(b_int)
    sol=sp.linsolve((A_S,b_S))
    if sol == sp.EmptySet:
        return {'shell':shell,'profile_id':pid,'status':'NO_SOLUTION','support_size':len(support),'nnls_linf_unscaled':float(np.max(np.abs(A_np@x-b_np))),'nnls_resnorm_unscaled':float(res)}, []
    sol_tuple=list(next(iter(sol)))
    free=sorted(set().union(*[expr.free_symbols for expr in sol_tuple]), key=lambda s:str(s))
    if free:
        return {'shell':shell,'profile_id':pid,'status':'PARAMETRIC','support_size':len(support),'free_parameter_count':len(free),'nnls_linf_unscaled':float(np.max(np.abs(A_np@x-b_np))),'nnls_resnorm_unscaled':float(res)}, []
    vals=[sp.Rational(v) for v in sol_tuple]
    residual=A_S*sp.Matrix(vals)-b_S
    ok=all(v==0 for v in residual)
    nonneg=all(v>=0 for v in vals)
    coeffs=[]
    if ok and nonneg:
        for loc,val in enumerate(vals):
            if val != 0:
                col=support[loc]; pair,i,j,k=meta[col]
                coeffs.append({'shell':shell,'profile_id':pid,'column':col,'pair':pair,'monomial_a':i,'monomial_b':j,'monomial_c':k,'coefficient_num':int(sp.numer(val)),'coefficient_den':int(sp.denom(val))})
    return {'shell':shell,'profile_id':pid,'status':'EXACT_RATIONAL_PASS' if ok and nonneg else 'EXACT_RATIONAL_FAIL','support_size':len(support),'nnls_linf_unscaled':float(np.max(np.abs(A_np@x-b_np))),'nnls_resnorm_unscaled':float(res),'exact_residual_zero':ok,'all_coefficients_nonnegative':nonneg,'nonzero_exact_coefficients':len(coeffs),'min_coefficient':str(min(vals)) if vals else '0'}, coeffs

def write_csv(path, rows):
    rows=list(rows)
    with open(path,'w',newline='',encoding='utf-8') as f:
        if rows:
            w=csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)
        else:
            f.write('')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('csv')
    ap.add_argument('--shell', type=int, required=True, choices=[12,16])
    ap.add_argument('--start', type=int, default=0)
    ap.add_argument('--stop', type=int, default=None)
    ap.add_argument('--out', required=True)
    ap.add_argument('--tol', type=float, default=1e-6)
    args=ap.parse_args()
    out=Path(args.out); out.mkdir(parents=True, exist_ok=True)
    df=pd.read_csv(args.csv)
    sub=df[df.shell==args.shell].sort_values('profile_id').reset_index(drop=True)
    stop=args.stop if args.stop is not None else len(sub)
    sub=sub.iloc[args.start:stop]
    summary=[]; coeffs=[]
    for n,(_,row) in enumerate(sub.iterrows(),1):
        res,cs=exactify(row,args.tol)
        summary.append(res); coeffs.extend(cs)
        if n%50==0:
            print('processed', n, 'of', len(sub))
    write_csv(out/'exact_rational_summary.csv', summary)
    write_csv(out/'exact_rational_coefficients.csv', coeffs)
    report={'shell':args.shell,'start':args.start,'stop':stop,'rows':len(summary),'status_counts':{s:sum(1 for r in summary if r['status']==s) for s in sorted(set(r['status'] for r in summary))}}
    (out/'exact_rational_report.json').write_text(json.dumps(report, indent=2, sort_keys=True), encoding='utf-8')
    print(json.dumps(report, indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
