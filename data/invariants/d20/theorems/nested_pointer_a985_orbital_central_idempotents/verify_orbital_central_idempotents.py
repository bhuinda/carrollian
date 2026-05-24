#!/usr/bin/env python3
import numpy as np, json, sys
from pathlib import Path
P=1000003
base=Path(__file__).resolve().parent
ROOT=base.parents[4]
T=np.load(ROOT/'data'/'raw'/'T_985.npz')['triples'].astype(np.int64)
Z=np.load(base/'a985_center_and_primitive_central_idempotents.npz')
E=Z['idempotents']; ids=Z['identity_indices']
by_b=[T[T[:,1]==j] for j in range(985)]; by_a=[T[T[:,0]==j] for j in range(985)]
def prod(x,y):
 vals=(x[T[:,0]]*y[T[:,1]])%P; vals=(vals*T[:,3])%P
 out=np.zeros(985,dtype=np.int64); np.add.at(out,T[:,2],vals); return out%P
def central_nz(x):
 for j in range(985):
  out=np.zeros(985,dtype=np.int64)
  tt=by_b[j]
  if len(tt): np.add.at(out,tt[:,2],(x[tt[:,0]]*tt[:,3])%P)
  tt=by_a[j]
  if len(tt): np.add.at(out,tt[:,2],(-x[tt[:,1]]*tt[:,3])%P)
  out%=P
  c=int(np.count_nonzero(out))
  if c: return c
 return 0
fails=[]
for i,e in enumerate(E):
 c=central_nz(e)
 if c: fails.append(['central',i,c])
for i in range(len(E)):
 for j in range(len(E)):
  got=prod(E[i],E[j]); want=E[i] if i==j else np.zeros(985,dtype=np.int64)
  if not np.array_equal(got,want): fails.append(['prod',i,j])
unit=np.zeros(985,dtype=np.int64); unit[ids]=1
if not np.array_equal(E.sum(axis=0)%P,unit): fails.append(['unit'])
status='D20_NESTED_POINTER_A985_ORBITAL_CENTRAL_IDEMPOTENTS_VERIFIED' if not fails else 'FAIL'
print(status)
Path(base/'orbital_central_idempotents_verify_result.json').write_text(json.dumps({'status':status,'failures_first20':fails[:20]},indent=2))
sys.exit(0 if not fails else 1)
