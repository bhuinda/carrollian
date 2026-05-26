from __future__ import annotations
import argparse, json, math, csv
from functools import lru_cache
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import nnls
EXPECTED_COUNTS={12:2576,16:759}
def monomials_deg(d): return [(i,j,d-i-j) for i in range(d+1) for j in range(d+1-i)]
@lru_cache(None)
def pairwise_square_matrix(w):
    mono=monomials_deg(w); idx={m:i for i,m in enumerate(mono)}; cols=[]; meta=[]
    for name,pair in [('ab',(0,1)),('ac',(0,2)),('bc',(1,2))]:
        for m in monomials_deg(w-2):
            col=np.zeros(len(mono),dtype=float); p,q=pair
            e=list(m); e[p]+=2; col[idx[tuple(e)]]+=1
            e=list(m); e[p]+=1; e[q]+=1; col[idx[tuple(e)]]+=-2
            e=list(m); e[q]+=2; col[idx[tuple(e)]]+=1
            cols.append(col); meta.append((name,m[0],m[1],m[2]))
    return mono,np.stack(cols,axis=1),meta
def H_vec(row):
    w=int(row.shell); d=w//2; A1=EXPECTED_COUNTS[w]
    mono,A,meta=pairwise_square_matrix(w); idx={m:i for i,m in enumerate(mono)}; b=np.zeros(len(mono),dtype=float)
    n1,n2,n3=int(row.first_size),int(row.second_size),int(row.rest_size)
    for p in range(d+1):
        for q in range(d+1-p):
            r=d-p-q; val=A1*math.factorial(d)//(math.factorial(p)*math.factorial(q)*math.factorial(r))*(n1**p)*(n2**q)*(n3**r)
            b[idx[(2*p,2*q,2*r)]]+=val
    prof=np.fromstring(row.profile,sep=',',dtype=np.int64).reshape((w+1,w+1)); scale=24**d
    for j in range(w+1):
        for k in range(w+1):
            c=int(prof[j,k])
            if c: b[idx[(j,k,w-j-k)]]-=scale*c
    return b
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('csv'); ap.add_argument('--shell',type=int,required=True); ap.add_argument('--profile-ids',required=True); ap.add_argument('--out',default='out_pairwise'); ap.add_argument('--maxiter',type=int,default=5000); args=ap.parse_args()
    out=Path(args.out); out.mkdir(parents=True,exist_ok=True); df=pd.read_csv(args.csv); sub=df[df.shell==args.shell].copy()
    if args.profile_ids!='all':
        ids={int(x) for x in args.profile_ids.split(',') if x.strip()}; sub=sub[sub.profile_id.isin(ids)]
    mono,A,meta=pairwise_square_matrix(args.shell); rows=[]
    for _,row in sub.iterrows():
        b=H_vec(row); scale=max(1.0,float(np.max(np.abs(b)))); bs=b/scale
        x,resnorm=nnls(A,bs,maxiter=args.maxiter); residual=A@x-bs; linf=float(np.max(np.abs(residual)))
        rows.append({'shell':int(row.shell),'profile_id':int(row.profile_id),'linf_residual':linf,'l2_residual':float(np.linalg.norm(residual)),'resnorm':float(resnorm),'nonzero_coefficients':int(np.sum(x>1e-10)),'status':'PASS_NUMERICAL' if linf<1e-8 else 'FAIL_NUMERICAL'})
    with (out/'pairwise_square_results.csv').open('w',newline='',encoding='utf-8') as f:
        fields=list(rows[0].keys()) if rows else ['status']; writer=csv.DictWriter(f,fieldnames=fields); writer.writeheader(); writer.writerows(rows)
    print(json.dumps({'rows':len(rows),'failures':sum(r['status']!='PASS_NUMERICAL' for r in rows),'max_linf':max((r['linf_residual'] for r in rows), default=None),'out':str(out/'pairwise_square_results.csv')},indent=2))
if __name__=='__main__': main()
