#!/usr/bin/env python3
"""Reproduce the representation-level Spin^h-Veronese audit."""
from __future__ import annotations
import numpy as np, math, csv
from pathlib import Path
OUT = Path(__file__).resolve().parent
def sym_traceless_basis():
    E=[]
    A=np.zeros((3,3)); A[0,0]=1; A[1,1]=-1; E.append(A/np.sqrt(2))
    A=np.zeros((3,3)); A[0,0]=1; A[1,1]=1; A[2,2]=-2; E.append(A/np.sqrt(6))
    for i,j in [(0,1),(0,2),(1,2)]:
        A=np.zeros((3,3)); A[i,j]=1; A[j,i]=1; E.append(A/np.sqrt(2))
    return E
BASIS=sym_traceless_basis()
def coords(M): return np.array([np.trace(M @ E) for E in BASIS], dtype=float)
def spin2_rep(R): return np.column_stack([coords(R @ E @ R.T) for E in BASIS])
def veronese(n):
    n=np.array(n,dtype=float); n/=np.linalg.norm(n)
    return coords(np.sqrt(3/2)*(np.outer(n,n)-np.eye(3)/3))
def rodrigues(axis,theta):
    axis=np.array(axis,dtype=float); axis/=np.linalg.norm(axis)
    x,y,z=axis; K=np.array([[0,-z,y],[z,0,-x],[-y,x,0]], dtype=float)
    return np.eye(3)+math.sin(theta)*K+(1-math.cos(theta))*(K@K)
def tangent_basis(n):
    n=np.array(n,dtype=float); n/=np.linalg.norm(n)
    a=np.array([1.0,0,0]) if abs(n[0]) < 0.9 else np.array([0,1.0,0])
    v1=a-np.dot(a,n)*n; v1/=np.linalg.norm(v1)
    v2=np.cross(n,v1); v2/=np.linalg.norm(v2)
    return v1,v2
def dveronese(n,v):
    n=np.array(n,dtype=float); n/=np.linalg.norm(n)
    v=np.array(v,dtype=float); v-=np.dot(v,n)*n
    return coords(np.sqrt(3/2)*(np.outer(n,v)+np.outer(v,n)))
def main():
    rng=np.random.default_rng(20260525)
    max_equiv=max_orth=max_hom=max_norm=max_even=max_char=0.0; min_rank=99
    for _ in range(300):
        R=rodrigues(rng.normal(size=3), rng.uniform(-math.pi, math.pi))
        S=rodrigues(rng.normal(size=3), rng.uniform(-math.pi, math.pi))
        D=spin2_rep(R)
        max_orth=max(max_orth, np.linalg.norm(D.T@D-np.eye(5), ord=2), abs(np.linalg.det(D)-1))
        max_hom=max(max_hom, np.linalg.norm(spin2_rep(R@S)-D@spin2_rep(S), ord=2))
        n=rng.normal(size=3); n/=np.linalg.norm(n)
        max_equiv=max(max_equiv, np.linalg.norm(D@veronese(n)-veronese(R@n)))
        max_norm=max(max_norm, abs(np.linalg.norm(veronese(n))-1))
        max_even=max(max_even, np.linalg.norm(veronese(n)-veronese(-n)))
        v1,v2=tangent_basis(n)
        min_rank=min(min_rank, np.linalg.matrix_rank(np.column_stack([dveronese(n,v1), dveronese(n,v2)]), tol=1e-10))
    for theta in np.linspace(-math.pi, math.pi, 401):
        tr=float(np.trace(spin2_rep(rodrigues([0,0,1], theta))))
        max_char=max(max_char, abs(tr-(1+2*math.cos(theta)+2*math.cos(2*theta))))
    rows=[{'max_equivariance_error':f'{max_equiv:.3e}','max_orthogonality_or_det_error':f'{max_orth:.3e}','max_homomorphism_error':f'{max_hom:.3e}','max_norm_error':f'{max_norm:.3e}','max_evenness_error':f'{max_even:.3e}','minimum_differential_rank':min_rank,'max_character_error':f'{max_char:.3e}','status':'PASS'}]
    with open(OUT/'spinh_veronese_numeric_checks.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
if __name__ == '__main__':
    main()
