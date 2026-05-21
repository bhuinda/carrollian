
from __future__ import annotations
from fractions import Fraction

def to_frac_matrix(A):
    return [[Fraction(x) for x in row] for row in A]

def matmul(A,B):
    m=len(A); n=len(B[0]); k=len(B)
    return [[sum(A[i][t]*B[t][j] for t in range(k)) for j in range(n)] for i in range(m)]

def transpose(A):
    return [list(row) for row in zip(*A)]

def eye(n):
    return [[Fraction(int(i==j)) for j in range(n)] for i in range(n)]

def outer(u,v):
    return [[u[i]*v[j] for j in range(len(v))] for i in range(len(u))]

def sub(A,B):
    return [[A[i][j]-B[i][j] for j in range(len(A[0]))] for i in range(len(A))]

def add(A,B):
    return [[A[i][j]+B[i][j] for j in range(len(A[0]))] for i in range(len(A))]

def vecmul(A,v):
    return [sum(A[i][j]*v[j] for j in range(len(v))) for i in range(len(A))]

def rowmul(v,A):
    return [sum(v[i]*A[i][j] for i in range(len(v))) for j in range(len(A[0]))]

def rank(A):
    A=[row[:] for row in to_frac_matrix(A)]
    if not A: return 0
    m,n=len(A),len(A[0])
    r=0
    for c in range(n):
        pivot=None
        for i in range(r,m):
            if A[i][c] != 0:
                pivot=i; break
        if pivot is None: continue
        A[r],A[pivot]=A[pivot],A[r]
        pv=A[r][c]
        A[r]=[x/pv for x in A[r]]
        for i in range(m):
            if i!=r and A[i][c]!=0:
                fac=A[i][c]
                A[i]=[A[i][j]-fac*A[r][j] for j in range(n)]
        r+=1
        if r==m: break
    return r

def det_bareiss_int(A):
    A=[list(map(int,row)) for row in A]
    n=len(A)
    if n==0: return 1
    sign=1; denom=1
    for k in range(n-1):
        pivot=k
        while pivot<n and A[pivot][k]==0: pivot+=1
        if pivot==n: return 0
        if pivot!=k:
            A[k],A[pivot]=A[pivot],A[k]; sign*=-1
        pv=A[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                A[i][j]=(A[i][j]*pv - A[i][k]*A[k][j])//denom
        denom=pv
        for i in range(k+1,n): A[i][k]=0
        for j in range(k+1,n): A[k][j]=0
    return sign*A[n-1][n-1]

def pfaffian_6(A):
    # Recursive exact Pfaffian; A must be 6x6 antisymmetric.
    A=to_frac_matrix(A)
    def pf(indices):
        if not indices: return Fraction(1)
        i=indices[0]
        total=Fraction(0)
        for pos in range(1,len(indices)):
            j=indices[pos]
            rest=indices[1:pos]+indices[pos+1:]
            total += ((-1)**(pos+1)) * A[i][j] * pf(rest)
        return total
    return pf(list(range(6)))
