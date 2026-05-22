import json, time, collections
from pathlib import Path
import numpy as np, sympy as sp
P=1000003
root=Path('/mnt/data/tensorial_object'); out=Path('/mnt/data')
def inv_mod(a,p=P): return pow(int(a)%p,-1,p)
def rref_mod(A,p=P,verbose=False):
    A=np.array(A,dtype=np.int64,copy=True)%p; nrows,ncols=A.shape; piv=[]; row=0
    for col in range(ncols):
        nz=np.nonzero(A[row:,col])[0]
        if nz.size==0: continue
        pi=row+int(nz[0])
        if pi!=row: A[[row,pi]]=A[[pi,row]]
        A[row]=(A[row]*inv_mod(A[row,col],p))%p
        nzr=np.nonzero(A[:,col])[0]; nzr=nzr[nzr!=row]
        if nzr.size:
            pr=A[row].copy()
            for st in range(0,nzr.size,4096):
                rr=nzr[st:st+4096]; fac=A[rr,col].copy()%p
                A[rr]=(A[rr]-fac[:,None]*pr)%p
        piv.append(col); row+=1
        if verbose and (len(piv)%25==0 or col==ncols-1): print(' pivot',len(piv),'col',col,flush=True)
        if row==nrows: break
    return A,piv
def nullspace_mod(A,p=P,verbose=False):
    R,piv=rref_mod(A,p,verbose); n=A.shape[1]; free=[j for j in range(n) if j not in set(piv)]; basis=[]
    for f in free:
        v=np.zeros(n,dtype=np.int64); v[f]=1
        for r,pc in enumerate(piv): v[pc]=(-R[r,f])%p
        basis.append(v)
    return (np.vstack(basis)%p if basis else np.zeros((0,n),dtype=np.int64)),piv
def mat_inv_mod(M,p=P):
    n=M.shape[0]; Aug=np.concatenate([M%p,np.eye(n,dtype=np.int64)],axis=1)%p
    R,piv=rref_mod(Aug,p)
    if piv[:n]!=list(range(n)): raise ValueError('singular')
    return R[:n,n:]%p
def independent_cols(M,p=P): return rref_mod(M,p)[1]
# load maps
orbs=json.load(open(root/'golay_full_tensor_out__golay_985_orbital_reps.json'))['orbitals']
triples=np.load(root/'golay_full_tensor_out__golay_985_tensor_sparse.npz')['triples'].astype(np.int64)
ids=set(o['id'] for o in orbs if o['x']==o['y'])
def norm(vals):
    mp={}; out=[]; labels=[]
    for v in vals:
        if v not in mp: mp[v]=len(mp); labels.append(v)
        out.append(mp[v])
    return np.array(out,dtype=np.int64),labels
q42,lab42=norm([('id',o['i']) if o['id'] in ids else (('nonid',o['i']) if o['i']==o['j'] else ('block',o['i'],o['j'])) for o in orbs])
sector={0:'B',1:'B',2:'V',3:'V',4:'S',5:'S'}
q12,lab12=norm([('id',sector[o['i']]) if o['id'] in ids else (('nonid',sector[o['i']]) if sector[o['i']]==sector[o['j']] else ('block',sector[o['i']],sector[o['j']])) for o in orbs])
q236=np.load(out/'q236_reconstructed.npy'); qs={'236':q236,'42':q42,'12':q12}
def quotient_tensor_normalized(qmap,name):
    cache=out/f'Tnorm_{name}.npy'
    if cache.exists(): return np.load(cache)
    n=int(qmap.max()+1); sizes=np.bincount(qmap,minlength=n).astype(np.int64)
    Tsum=np.zeros((n,n,n),dtype=np.int64)
    for a,b,g,c in triples: Tsum[int(qmap[a]),int(qmap[b]),int(qmap[g])] += int(c)
    T=np.zeros_like(Tsum)
    bad=[]
    for i,j,k in np.argwhere(Tsum!=0):
        tot=int(Tsum[i,j,k]); s=int(sizes[k])
        if tot%s: bad.append((i,j,k,tot,s))
        T[i,j,k]=tot//s
    if bad: raise ValueError(f'bad division {name} {bad[:5]}')
    np.save(cache,T%P); return T%P
def identity_vector(qmap):
    n=int(qmap.max()+1); v=np.zeros(n,dtype=np.int64)
    for oid in ids: v[int(qmap[oid])]=1
    return v%P
def multiply(T,x,y): return np.einsum('i,j,ijk->k',x%P,y%P,T,optimize=True)%P
def trace_basis(T):
    n=T.shape[0]
    return np.array([sum(int(T[k,j,j]) for j in range(n))%P for k in range(n)],dtype=np.int64)
def build_comm(T):
    n=T.shape[0]; A=np.empty((n*n,n),dtype=np.int64)
    for i in range(n): A[i*n:(i+1)*n,:]=(T[:,i,:]-T[i,:,:]).T%P
    return A
def center_basis(T,name):
    cache=out/f'center_basis_norm_{name}.npy'
    if cache.exists(): return np.load(cache)
    print('center',name,flush=True); Z,piv=nullspace_mod(build_comm(T),P,verbose=True); np.save(cache,Z); return Z
def coords_setup(Z):
    piv=independent_cols(Z,P)[:Z.shape[0]]; return np.array(piv,dtype=np.int64), mat_inv_mod(Z[:,piv],P)
def coords(v,piv,Sinv): return (v[piv]@Sinv)%P
def roots_of_char(M):
    x=sp.symbols('x'); Ms=sp.Matrix([[int(a)%P for a in row] for row in M.tolist()])
    fl=sp.factor_list(Ms.charpoly(x).as_expr(),x,modulus=P)
    roots=[]; bad=[]
    for fac,exp in fl[1]:
        pp=sp.Poly(fac,x,modulus=P)
        if pp.degree()==1 and exp==1:
            a,b=[int(c)%P for c in pp.all_coeffs()]; roots.append((-b*inv_mod(a,P))%P)
        else: bad.append((pp.degree(),exp))
    return roots,bad
def central_idempotents_fast(T,Z,qmap,name):
    cache=out/f'central_idempotents_norm_{name}.npy'; mcache=out/f'central_idempotents_norm_{name}.json'
    if cache.exists() and mcache.exists(): return np.load(cache), json.load(open(mcache))
    r,n=Z.shape; piv,Sinv=coords_setup(Z); one=identity_vector(qmap); cI=coords(one,piv,Sinv)
    rng=np.random.default_rng(5521+n)
    for attempt in range(100):
        coeff=rng.integers(0,P,size=r,dtype=np.int64); h=(coeff@Z)%P
        M=np.zeros((r,r),dtype=np.int64)
        for j,z in enumerate(Z): M[:,j]=coords(multiply(T,h,z),piv,Sinv)
        roots,bad=roots_of_char(M)
        print(name,'attempt',attempt,'roots',len(roots),'bad',bad[:3],flush=True)
        if len(roots)==r and not bad and len(set(roots))==r:
            I=np.eye(r,dtype=np.int64); Ecoords=[]
            for lam in roots:
                c=cI.copy()
                for mu in roots:
                    if mu==lam: continue
                    c=((M - (mu%P)*I)%P @ c)%P
                    c=(c*inv_mod((lam-mu)%P,P))%P
                Ecoords.append(c%P)
            Ecoords=np.vstack(Ecoords)%P
            E=(Ecoords@Z)%P
            tr=trace_basis(T); traces=[int((e@tr)%P) for e in E]
            dims=[]
            for tv in traces:
                found=None
                for d in range(1,100):
                    if d*d==tv: found=d; break
                dims.append(found if found is not None else tv)
            # verify with full multiplication, but only 34+orth maybe okay
            sum_ok=bool(np.array_equal(E.sum(axis=0)%P,one%P))
            id_ok=True
            for e in E:
                if not np.array_equal(multiply(T,e,e)%P,e%P): id_ok=False; break
            orth=True
            for i in range(len(E)):
                for j in range(i+1,len(E)):
                    if np.any(multiply(T,E[i],E[j])%P): orth=False; break
                if not orth: break
            meta={'dims':dims,'trace_squares':traces,'attempt':attempt,'roots':[int(x) for x in roots],'sum_identity_ok':sum_ok,'idempotent_ok':id_ok,'orthogonal_ok':orth}
            np.save(cache,E); open(mcache,'w').write(json.dumps(meta,indent=2)); return E,meta
    raise RuntimeError('failed idempotents '+name)
def maps_between(qfine,qcoarse):
    mp={}
    for i,m in enumerate(qfine):
        m=int(m); c=int(qcoarse[i])
        if m in mp and mp[m]!=c: raise ValueError('not factored')
        mp[m]=c
    arr=np.empty(max(mp)+1,dtype=np.int64)
    for k,v in mp.items(): arr[k]=v
    return arr
def lift_vec(vsmall,fmap): return np.array([vsmall[int(fmap[i])] for i in range(len(fmap))],dtype=np.int64)%P
def branch(Tbig,Ebig,dbig,Esmall,dsmall,fmap):
    tr=trace_basis(Tbig); B=np.zeros((len(Ebig),len(Esmall)),dtype=np.int64)
    for i,eb in enumerate(Ebig):
        for j,es in enumerate(Esmall):
            prod=multiply(Tbig,eb,lift_vec(es,fmap)); val=int((prod@tr)%P); m=val*inv_mod((dbig[i]*dsmall[j])%P,P)%P
            if m>P//2: m-=P
            B[i,j]=m
    row=B@np.array(dsmall,dtype=np.int64); ok=[int(row[i])==int(dbig[i]) for i in range(len(dbig))]
    return B,row,ok
Ts={name:quotient_tensor_normalized(qs[name],name) for name in ['236','42','12']}
for name,T in Ts.items(): print('T',name,T.shape,'support',np.count_nonzero(T),'coeffsum',int(T.sum()))
Zs={}; Es={}; metas={}
for name in ['236','42','12']:
    Zs[name]=center_basis(Ts[name],name); print('Z',name,Zs[name].shape)
    Es[name],metas[name]=central_idempotents_fast(Ts[name],Zs[name],qs[name],name)
    print('dims',name,collections.Counter(metas[name]['dims']),metas[name]['sum_identity_ok'],metas[name]['idempotent_ok'],metas[name]['orthogonal_ok'])
f236_42=maps_between(q236,q42); f42_12=maps_between(q42,q12); f236_12=maps_between(q236,q12)
assert np.all(np.array([f42_12[x] for x in f236_42])==f236_12)
B236_42,row1,ok1=branch(Ts['236'],Es['236'],metas['236']['dims'],Es['42'],metas['42']['dims'],f236_42)
B42_12,row2,ok2=branch(Ts['42'],Es['42'],metas['42']['dims'],Es['12'],metas['12']['dims'],f42_12)
B236_12,row3,ok3=branch(Ts['236'],Es['236'],metas['236']['dims'],Es['12'],metas['12']['dims'],f236_12)
comp=B236_42@B42_12; nat=np.array_equal(comp,B236_12)
print('oks',all(ok1),all(ok2),all(ok3),'nat',nat,'defect',np.count_nonzero(comp-B236_12))
np.savez(out/'simple_branching_matrices.npz',B236_42=B236_42,B42_12=B42_12,B236_12=B236_12,comp=comp,dims236=np.array(metas['236']['dims']),dims42=np.array(metas['42']['dims']),dims12=np.array(metas['12']['dims']))
trip=[i for i,d in enumerate(metas['236']['dims']) if d==3]
rep={'status':'PASS_FULL_SIMPLE_NATURALITY' if nat and all(ok1) and all(ok2) and all(ok3) else 'FAIL_OR_PARTIAL','prime':P,
     'center_dims':{name:len(metas[name]['dims']) for name in ['236','42','12']},
     'simple_dimension_counts':{name:{str(k):int(v) for k,v in sorted(collections.Counter(metas[name]['dims']).items())} for name in ['236','42','12']},
     'row_dimension_checks':{'B236_to_42':bool(all(ok1)),'B42_to_12':bool(all(ok2)),'B236_to_12':bool(all(ok3))},
     'naturality':{'passes':bool(nat),'defect_nonzero_entries':int(np.count_nonzero(comp-B236_12)),'defect_l1':int(np.abs(comp-B236_12).sum())},
     'branch_shapes':{'B236_to_42':list(B236_42.shape),'B42_to_12':list(B42_12.shape),'B236_to_12':list(B236_12.shape)},
     'A236_tenfold':{'triplet_rows':trip,'triplet_count':len(trip),'triplet_ideal_dimension':len(trip)*9,'B236_to_42_triplet_rows':B236_42[trip].astype(int).tolist(),'B236_to_12_triplet_rows':B236_12[trip].astype(int).tolist()},
     'dims':{name:metas[name]['dims'] for name in ['236','42','12']},
     'matrices':{'B236_to_42':B236_42.astype(int).tolist(),'B42_to_12':B42_12.astype(int).tolist(),'B236_to_12':B236_12.astype(int).tolist()}}
open(out/'simple_branching_naturality_report.json','w').write(json.dumps(rep,indent=2,sort_keys=True))
md=['# Simple branching naturality report','',f"status: **{rep['status']}**",'', '## Simple dimension counts']
for name in ['236','42','12']: md.append(f"- A{name}: center={rep['center_dims'][name]}, counts={rep['simple_dimension_counts'][name]}")
md += ['', '## Branching naturality', f"B236→12 = B236→42 · B42→12: **{rep['naturality']['passes']}**", f"defect nonzero entries: `{rep['naturality']['defect_nonzero_entries']}`", f"defect L1: `{rep['naturality']['defect_l1']}`", '', '## A236 tenfold triplet layer', f"triplet rows: `{trip}`", f"triplet count: `{len(trip)}`", f"triplet ideal dimension: `{len(trip)*9}`", '', '`B236→42` on triplet rows:', '```text', str(B236_42[trip].astype(int).tolist()), '```', '', '`B236→12` on triplet rows:', '```text', str(B236_12[trip].astype(int).tolist()), '```']
open(out/'simple_branching_naturality_report.md','w').write('\n'.join(md))
print('wrote reports')
