from pathlib import Path
import json, numpy as np

def constants(root): return json.load(open(Path(root)/'data'/'constants.json'))
def load(root):
    z=np.load(Path(root)/'data'/'tensor_sparse.npz')
    return z['triples'],z['M'],z['reps']

def verify(root):
    c=constants(root); triples,M,reps=load(root)
    assert list(triples.shape)==c['tensor_shape']
    assert int(triples[:,3].sum())==c['coefficient_total']
    assert M.astype(int).tolist()==c['M']
    assert int(M.sum())==985
    assert list(reps.shape)==[985,5]
    mult={int(k):int(v) for k,v in c['wedderburn']['block_size_multiplicities'].items()}
    assert c['wedderburn']['center_dim']==39
    assert sum(mult.values())==39
    assert sum(k*k*v for k,v in mult.items())==985
    assert c['A236']=={'dimension':236,'center_dim':34,'sum_squares':236}
    return {'tensor_nonzeros':int(triples.shape[0]),'coefficient_total':int(triples[:,3].sum()),'M_sum':int(M.sum()),'center_dim':39,'A236_dimension':236}

def block_arrays(M):
    bi=np.empty(int(M.sum()), dtype=np.int16); bj=np.empty(int(M.sum()), dtype=np.int16)
    s=0
    for i in range(6):
        for j in range(6):
            n=int(M[i,j]); bi[s:s+n]=i; bj[s:s+n]=j; s+=n
    return bi,bj
