#!/usr/bin/env python3
"""Reproduce the local SDPI part of the entropy log-Sobolev route audit."""
from itertools import product
import numpy as np, csv
from pathlib import Path
OUT=Path(__file__).resolve().parent
def bits_to_int(bits):
    x=0
    for i,b in enumerate(bits):
        if b: x|=1<<i
    return x
def wt(x): return int(x).bit_count()
def rm13_h8():
    pts=list(product([0,1], repeat=3)); C=[]
    for a in product([0,1], repeat=3):
        for b in [0,1]:
            C.append(bits_to_int([(sum(ai*pi for ai,pi in zip(a,p))+b)%2 for p in pts]))
    return sorted(set(C))
def direct_sum(codes,lengths):
    res=[0]; shift=0
    for C,L in zip(codes,lengths):
        res=[r | (c<<shift) for r in res for c in C]; shift+=L
    return sorted(set(res))
def v(supp):
    x=0
    for j in supp: x|=1<<(j-1)
    return x
def neigh(C,x):
    C0=[c for c in C if wt(c&x)%2==0]
    return sorted(set(C0+[c^x for c in C0]))
def golay():
    H8=rm13_h8(); C=direct_sum([H8,H8,H8],[8,8,8])
    for supp in [[2,4,9,10,12,13,14,16,17,18,20,22],[3,4,9,13,15,16,19,20],[2,5,7,8,9,10,12,14,15,16,17,18,19,21,22,23]]:
        C=neigh(C,v(supp))
    return C
def incidence(blocks):
    B=np.zeros((len(blocks),24))
    for r,b in enumerate(blocks):
        for i in range(24):
            if (b>>i)&1: B[r,i]=1
    return B
rows=[]
C=golay()
for w in [8,12,16]:
    blocks=[c for c in C if wt(c)==w]
    B=incidence(blocks); m=len(blocks)
    eig=np.sort(np.linalg.eigvalsh(B.T@B))[::-1]
    eta=(24/(m*w*w))*eig[1]
    rows.append({'shell':w,'blocks':m,'local_SDPI_eta':eta,'target_eta_2_over_w':2/w,'margin':2/w-eta})
with open(OUT/'local_sdpi_spectrum.csv','w',newline='') as f:
    wr=csv.DictWriter(f,fieldnames=list(rows[0].keys())); wr.writeheader(); wr.writerows(rows)
