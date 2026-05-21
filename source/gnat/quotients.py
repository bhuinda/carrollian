from pathlib import Path
import numpy as np
from .tensor import load, block_arrays

SECTOR=np.array([0,0,1,1,2,2], dtype=np.int16)

def maps_from_M(M):
    bi,bj=block_arrays(M); identity={0,151,227,349,613,881}
    q42=np.empty(985,dtype=np.int16); off={}; k=12
    for i in range(6):
        for j in range(6):
            if i!=j: off[(i,j)]=k; k+=1
    for a in range(985):
        i=int(bi[a]); j=int(bj[a])
        q42[a]=i if (i==j and a in identity) else (6+i if i==j else off[(i,j)])
    q12=np.empty(985,dtype=np.int16); off2={}; k=6
    for i in range(3):
        for j in range(3):
            if i!=j: off2[(i,j)]=k; k+=1
    for a in range(985):
        i=int(SECTOR[bi[a]]); j=int(SECTOR[bj[a]])
        q12[a]=i if (i==j and a in identity) else (3+i if i==j else off2[(i,j)])
    return q42,q12,bi,bj

def aggregate(triples,q,n):
    A=q[triples[:,0]].astype(np.int64); B=q[triples[:,1]].astype(np.int64); C=q[triples[:,2]].astype(np.int64)
    flat=(A*n+B)*n+C
    return np.bincount(flat, weights=triples[:,3].astype(np.int64), minlength=n*n*n).astype(np.int64).reshape(n,n,n)

def verify(root):
    root=Path(root); triples,M,_=load(root)
    q42,q12,_,_=maps_from_M(M)
    z=np.load(root/'data'/'quotients.npz')
    assert np.array_equal(q42,z['q42_map'])
    assert np.array_equal(q12,z['q12_map'])
    T42=aggregate(triples,q42,42); T12=aggregate(triples,q12,12)
    q42_ok=np.array_equal(T42,z['q42_tensor'])
    q12_ok=np.array_equal(T12,z['q12_tensor'])
    assert q42_ok
    assert q12_ok
    assert int(T42.sum())==2537360 and int(T12.sum())==2537360
    assert int(np.count_nonzero(T42))==340
    assert int(np.count_nonzero(T12))==62
    par=np.zeros(42,dtype=np.int16); objpar=[0,1,0,1,0,1]
    k=12
    for i in range(6): par[i]=0; par[6+i]=0
    for i in range(6):
        for j in range(6):
            if i!=j: par[k]=(objpar[i]+objpar[j])&1; k+=1
    for a,b,c in zip(*np.nonzero(T42)):
        assert ((int(par[a])+int(par[b]))&1)==int(par[c])
    return {'A42_classes':42,'A12_classes':12,'A42_support':340,'A12_support':62,'coefficient_total':2537360,'pin_parity':True,'Q42_equals_aggregated_A985_tensor':bool(q42_ok),'Q12_equals_aggregated_A985_tensor':bool(q12_ok),'Q42_tensor_shape':list(T42.shape),'Q12_tensor_shape':list(T12.shape)}
