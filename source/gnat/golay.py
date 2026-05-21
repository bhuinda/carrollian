from itertools import product, combinations
from collections import Counter, defaultdict

def add(u,v): return tuple(a^b for a,b in zip(u,v))
def dot(u,v): return sum(a*b for a,b in zip(u,v))&1
def wt(u): return sum(u)
def mask_of_codeword(c): return sum((1<<i) for i,b in enumerate(c) if b)
def mask_of_indices(xs): return sum(1<<i for i in xs)

def span(gens):
    S={(0,)*len(gens[0])}
    for g in gens:
        S |= {add(x,g) for x in list(S)}
    return sorted(S)

def vec(S): return tuple(1 if i+1 in S else 0 for i in range(24))
def neighbor(C,v): return span([c for c in C if dot(c,v)==0]+[v])
def root_count(C): return sum(1 for c in C if wt(c)==4)

def build_golay():
    pts=list(product([0,1], repeat=3))
    gens=[tuple(1 for _ in pts)] + [tuple(p[j] for p in pts) for j in range(3)]
    H8=span(gens)
    C=[a+b+c for a in H8 for b in H8 for c in H8]
    vs=[
        vec({2,4,9,10,12,13,14,16,17,18,20,22}),
        vec({3,4,9,13,15,16,19,20}),
        vec({2,5,7,8,9,10,12,14,15,16,17,18,19,21,22,23}),
    ]
    hist=[]
    for v in vs:
        hist.append(root_count(C)); C=neighbor(C,v)
    hist.append(root_count(C))
    return H8,C,hist

def sextet_data(C):
    octads=[mask_of_codeword(c) for c in C if wt(c)==8]
    dodecads=[mask_of_codeword(c) for c in C if wt(c)==12]
    tetrads=[mask_of_indices(xs) for xs in combinations(range(24),4)]
    mates=defaultdict(set)
    for O in octads:
        bits=[i for i in range(24) if (O>>i)&1]
        for xs in combinations(bits,4):
            A=mask_of_indices(xs); B=O^A
            if A!=B:
                mates[A].add(B); mates[B].add(A)
    mate_hist=Counter(len(mates[T]) for T in tetrads)
    assert mate_hist==Counter({5:10626})
    sextets={tuple(sorted([T]+list(mates[T]))) for T in tetrads}
    assert len(sextets)==1771
    S=next(iter(sorted(sextets)))
    patterns=Counter(tuple(sorted([(D&T).bit_count() for T in S])) for D in dodecads)
    return {
        'tetrads':len(tetrads),
        'sextets':len(sextets),
        'tetrad_mate_count_histogram':{str(k):int(v) for k,v in sorted(mate_hist.items())},
        'dodecad_sextet_pattern_counts':{str(k):int(v) for k,v in sorted(patterns.items())},
    }

def verify():
    H8,C,hist=build_golay()
    enum=dict(sorted(Counter(map(wt,C)).items()))
    out={'H8_size':len(H8),'code_size':len(C),'root_history':hist,'weight_enumerator':enum,'dodecads':enum.get(12,0)}
    assert out=={'H8_size':16,'code_size':4096,'root_history':[42,18,6,0],'weight_enumerator':{0:1,8:759,12:2576,16:759,24:1},'dodecads':2576}
    out.update(sextet_data(C))
    assert out['tetrads']==10626
    assert out['sextets']==1771
    assert out['dodecad_sextet_pattern_counts']=={'(0, 2, 2, 2, 2, 4)':720,'(1, 1, 1, 3, 3, 3)':1280,'(2, 2, 2, 2, 2, 2)':576}
    return out
