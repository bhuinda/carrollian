from pathlib import Path
from collections import Counter, deque
import math
import numpy as np

ORDER=4157776806543360000
DEGREE=98280
TYPE_COUNTS={'A_pair_44':552,'B_octad_22222222':48576,'C_golay_311':49152}
IP={0:46575,8:47104,16:4600,32:1}
ORDER_FACTORS={2:21,3:9,5:4,7:2,11:1,13:1,23:1}
STABILIZER_ORDER=ORDER//DEGREE
STABILIZER_FACTORS={2:18,3:6,5:3,7:1,11:1,23:1}

def load(root):
    p=Path(root)/'generators'/'co1'/'projective_generators.npz'
    z=np.load(p, allow_pickle=False)
    return z['generator_names'],z['projective_leech_permutations'].astype(np.int32,copy=False),z['projective_leech_vectors'].astype(np.int8,copy=False),z['projective_leech_types']

def validate_perms(P):
    k,n=P.shape
    s=n*(n-1)//2; ss=n*(n-1)*(2*n-1)//6
    for row in P:
        r=row.astype(np.int64,copy=False)
        assert int(r.min())==0 and int(r.max())==n-1
        assert int(r.sum())==s and int(np.dot(r,r))==ss
        assert int(np.unique(row).size)==n
    return {'generators':int(k),'degree':int(n)}

def orbit(P,start=0):
    k,n=P.shape; seen=np.zeros(n,dtype=np.bool_); q=deque([start]); seen[start]=True; scans=0
    while q:
        x=q.popleft()
        for i in range(k):
            y=int(P[i,x]); scans+=1
            if not seen[y]: seen[y]=True; q.append(y)
    return int(seen.sum()),scans

def generator_family(name: str) -> str:
    if name.startswith('coord_'): return 'coordinate'
    if name.startswith('epsilon_'): return 'golay_sign_change'
    if name.startswith('zeta_'): return 'conway_tetrad'
    return 'other'

def perm_order_and_cycles(p):
    n=len(p); seen=np.zeros(n,dtype=np.bool_); lcm=1; dist=Counter()
    for i in range(n):
        if not seen[i]:
            j=i; m=0
            while not seen[j]:
                seen[j]=True; j=int(p[j]); m+=1
            dist[m]+=1
            lcm=math.lcm(lcm,m)
    return int(lcm), {int(k):int(v) for k,v in sorted(dist.items()) if k>1}

def generator_report(names,P):
    names=[str(x) for x in names.tolist()]
    families=Counter(generator_family(x) for x in names)
    orders={}
    cycle_distributions={}
    for name,p in zip(names,P):
        o,d=perm_order_and_cycles(p)
        orders[name]=o
        cycle_distributions[name]=d
    return {
        'names':names,
        'count':len(names),
        'family_counts':{str(k):int(v) for k,v in sorted(families.items())},
        'order_counts':{str(k):int(v) for k,v in sorted(Counter(orders.values()).items(), key=lambda x:int(x[0]))},
        'orders_by_name':orders,
        'nontrivial_cycle_counts_by_name':cycle_distributions,
    }

def verify(root):
    names,P,V,T=load(root)
    val=validate_perms(P)
    assert val=={'generators':16,'degree':DEGREE}
    o,scans=orbit(P,0)
    assert o==DEGREE
    counts={str(k):int(v) for k,v in Counter(T.tolist()).items()}
    assert counts==TYPE_COUNTS
    dots=np.abs(V.astype(np.int16) @ V[0].astype(np.int16))
    ip={int(k):int(v) for k,v in Counter(int(x) for x in dots.tolist()).items()}
    assert ip==IP
    greport=generator_report(names,P)
    assert greport['family_counts']=={'conway_tetrad':1,'coordinate':3,'golay_sign_change':12}
    assert greport['order_counts']=={'2':14,'11':1,'23':1}
    return {
        'group':'Co1_projective_Leech_shell',
        'order':ORDER,
        'order_factorization':{str(k):v for k,v in ORDER_FACTORS.items()},
        'degree':DEGREE,
        'point_stabilizer_order':STABILIZER_ORDER,
        'point_stabilizer_order_factorization':{str(k):v for k,v in STABILIZER_FACTORS.items()},
        'generators':greport,
        'orbit':o,
        'transitive':o==DEGREE,
        'type_counts':counts,
        'base_abs_inner_products':{str(k):int(v) for k,v in ip.items()},
        'edge_scans':scans,
    }
