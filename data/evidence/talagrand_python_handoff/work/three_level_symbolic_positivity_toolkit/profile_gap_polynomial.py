from __future__ import annotations
import argparse, json, math
import numpy as np
import pandas as pd
EXPECTED_COUNTS={12:2576,16:759}
def monomials_deg(d:int): return [(i,j,d-i-j) for i in range(d+1) for j in range(d+1-i)]
def gap_coefficients(row):
    shell=int(row.shell); d=shell//2; A1=EXPECTED_COUNTS[shell]
    mono=monomials_deg(shell); idx={m:i for i,m in enumerate(mono)}; coeff=[0]*len(mono)
    n1,n2,n3=int(row.first_size),int(row.second_size),int(row.rest_size)
    for p in range(d+1):
        for q in range(d+1-p):
            r=d-p-q
            val=A1*math.factorial(d)//(math.factorial(p)*math.factorial(q)*math.factorial(r))*(n1**p)*(n2**q)*(n3**r)
            coeff[idx[(2*p,2*q,2*r)]] += val
    prof=np.fromstring(row.profile,sep=',',dtype=np.int64).reshape((shell+1,shell+1)); scale=24**d
    for j in range(shell+1):
        for k in range(shell+1):
            count=int(prof[j,k])
            if count: coeff[idx[(j,k,shell-j-k)]] -= scale*count
    return mono,coeff
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('csv'); ap.add_argument('--shell',type=int,required=True); ap.add_argument('--profile-id',type=int,required=True); args=ap.parse_args()
    df=pd.read_csv(args.csv); row=df[(df.shell==args.shell)&(df.profile_id==args.profile_id)]
    if row.empty: raise SystemExit('profile not found')
    row=row.iloc[0]; mono,coeff=gap_coefficients(row)
    terms=[{'a':a,'b':b,'c':c,'coefficient':int(co)} for (a,b,c),co in zip(mono,coeff) if co]
    print(json.dumps({'shell':int(row.shell),'profile_id':int(row.profile_id),'first_size':int(row.first_size),'second_size':int(row.second_size),'rest_size':int(row.rest_size),'term_count':len(terms),'terms':terms},indent=2,sort_keys=True))
if __name__=='__main__': main()
