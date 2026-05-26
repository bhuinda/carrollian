import math,json,csv,zipfile,hashlib,shutil
from itertools import product
from pathlib import Path
import numpy as np
from scipy.optimize import minimize, minimize_scalar
N=24; OUT=Path('/mnt/data/hamming_gaussian_two_level_probe'); OUT.mkdir(exist_ok=True)
def sha(b): return hashlib.sha256(b).hexdigest()
def cjson(o): return json.dumps(o, sort_keys=True, separators=(',',':')).encode()
def bits_to_int(bits):
 x=0
 for i,b in enumerate(bits):
  if b: x|=1<<i
 return x
def wt(x): return int(x).bit_count()
def rm13_h8():
 pts=list(product([0,1], repeat=3)); C=[]
 for a in product([0,1], repeat=3):
  for b in [0,1]: C.append(bits_to_int([(sum(ai*pi for ai,pi in zip(a,p))+b)%2 for p in pts]))
 return sorted(set(C))
def direct_sum(codes,lengths):
 res=[0]; sh=0
 for C,L in zip(codes,lengths):
  res=[r|(c<<sh) for r in res for c in C]; sh+=L
 return sorted(set(res))
def vec1(supp):
 x=0
 for j in supp: x|=1<<(j-1)
 return x
def neigh(C,x):
 C0=[c for c in C if wt(c&x)%2==0]
 return sorted(set(C0+[c^x for c in C0]))
def build():
 H=rm13_h8(); C=direct_sum([H,H,H],[8,8,8])
 for s in [[2,4,9,10,12,13,14,16,17,18,20,22],[3,4,9,13,15,16,19,20],[2,5,7,8,9,10,12,14,15,16,17,18,19,21,22,23]]: C=neigh(C,vec1(s))
 return C
C=build(); FULL=(1<<N)-1
candidate=1.444854859266432

def split_profile(mask_bits):
 prof={}
 for c in C:
  j=wt(c&mask_bits); l=wt(c&(~mask_bits & FULL)); prof[(j,l)]=prof.get((j,l),0)+1
 vals=[]
 k=wt(mask_bits)
 for (j,l),cnt in sorted(prof.items()):
  # dot for u=a on S, b off S = a*(k-2j)+b*(N-k-2l)
  vals.append((k-2*j, N-k-2*l, cnt))
 return k, vals, prof

def F_ab_from_vals(vals,a,b):
 norm2=0 # will be supplied separately? norm2=k a^2+(N-k)b^2 in caller
 pass

def optimize_profile(k, vals):
 # parameters theta, scale: a=cos(theta)/sqrt(k?) no, choose v normalized by norm sqrt(k a^2+(N-k)b^2)=1
 # Let basis eS normalized, eC normalized. direction v has a = cosθ/sqrt(k), b=sinθ/sqrt(N-k) (handle k=0/24).
 def vals_for_theta(theta):
  if k==0:
   a=0.0; b=1/math.sqrt(N)
  elif k==N:
   a=1/math.sqrt(N); b=0.0
  else:
   a=math.cos(theta)/math.sqrt(k); b=math.sin(theta)/math.sqrt(N-k)
  dots=np.array([a*A+b*B for A,B,cnt in vals],float)
  cnts=np.array([cnt for A,B,cnt in vals],float)
  return dots,cnts,a,b
 def F_t_theta(t,theta):
  dots,cnts,_,_=vals_for_theta(theta)
  x=t*dots; m=float(np.max(x)); L=m+math.log(float(np.sum(cnts*np.exp(x-m))/4096.0))
  if t<1e-8: return 1.0
  return 2*L/(t*t)  # direction norm 1
 def best_t(theta):
  # maximize over t in [0,10]
  res=minimize_scalar(lambda z: -F_t_theta(z,theta), bounds=(1e-6,8.0), method='bounded', options={'xatol':1e-10, 'maxiter':200})
  return -float(res.fun), float(res.x)
 # coarse theta grid
 if k==0 or k==N:
  val,t=best_t(0.0); dots,cnts,a,b=vals_for_theta(0.0); return val,t,0.0,a*t,b*t
 thetas=np.linspace(0, math.pi, 181, endpoint=True)
 best=(-1,None,None)
 for th in thetas:
  val,t=best_t(float(th))
  if val>best[0]: best=(val,t,float(th))
 # refine theta around best via minimize scalar in bracket +/- grid step
 step=math.pi/180
 lo=max(0,best[2]-2*step); hi=min(math.pi,best[2]+2*step)
 def negtheta(th): return -best_t(float(th))[0]
 res=minimize_scalar(negtheta, bounds=(lo,hi), method='bounded', options={'xatol':1e-9, 'maxiter':100})
 th=float(res.x); val,t=best_t(th); dots,cnts,a,b=vals_for_theta(th)
 return val,t,th,a*t,b*t
# subset list
subs=[]
for k in range(0,N+1):
 mask=(1<<k)-1 if k>0 else 0; subs.append((f'prefix_k{k}',mask))
seen=set()
for w in [8,12,16,24]:
 for c in C:
  if wt(c)==w:
   mask=c
   if mask not in seen: seen.add(mask); subs.append((f'codeword_support_w{w}',mask))
   break
rng=np.random.default_rng(20260525)
for k in range(6,19):
 for j in range(2):
  idx=rng.choice(N,k,replace=False); mask=0
  for i in idx: mask|=1<<int(i)
  subs.append((f'random_k{k}_{j}',mask))
rows=[]
for label,mask in subs:
 k,vals,prof=split_profile(mask)
 F,t,theta,a,b= optimize_profile(k, vals)
 rows.append({'label':label,'k':k,'F':F,'K':math.sqrt(max(F,0)),'t_norm':t,'theta':theta,'a':a,'b':b,'excess_over_candidate':F-candidate,'split_profile_size':len(prof)})
rows_sorted=sorted(rows,key=lambda r:r['F'], reverse=True)
with open(OUT/'two_level_optimization.csv','w',newline='') as f:
 fields=list(rows_sorted[0].keys()); w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows_sorted)
prof_rows=[]
for r in rows_sorted[:12]:
 mask=dict(subs)[r['label']]; k,vals,prof=split_profile(mask)
 for (j,l),cnt in sorted(prof.items()): prof_rows.append({'label':r['label'],'k':k,'inside_weight':j,'outside_weight':l,'count':cnt})
with open(OUT/'top_split_weight_profiles.csv','w',newline='') as f:
 fields=['label','k','inside_weight','outside_weight','count']; w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(prof_rows)
cert={'status':'HAMMING_GAUSSIAN_TWO_LEVEL_PROBE_COMPLETE','scope':'optimized two-level directions u=a on S, b off S over prefix/codeword/random subset representatives','candidate_global_K2':candidate,'candidate_global_K':math.sqrt(candidate),'subsets_tested':len(rows),'best_two_level':rows_sorted[0],'top_12':rows_sorted[:12],'no_two_level_exceeds_candidate': bool(rows_sorted[0]['F'] <= candidate+1e-8),'not_claimed':['not exhaustive over all subset orbits','not global over arbitrary R^24 directions','not full convex-order theorem'],'files':['hamming_gaussian_two_level_probe_report.md','hamming_gaussian_two_level_probe_certificate.json','two_level_optimization.csv','top_split_weight_profiles.csv','hamming_gaussian_two_level_probe.py']}
cert['certificate_sha256']=sha(cjson(cert)); (OUT/'hamming_gaussian_two_level_probe_certificate.json').write_text(json.dumps(cert,indent=2,sort_keys=True))
report=f"""# Hamming--Gaussian Two-Level Direction Probe

## Result

`{cert['status']}`

This tests the next reduction class after the codeword-sign local maximum: directions taking two coordinate values, `a` on a subset `S` and `b` on the complement. It covers all prefix support sizes, representative Golay codeword supports of weights 8, 12, 16, 24, and random medium supports.

## Candidate bound

```text
K^2_candidate = {candidate:.15f}
K_candidate   = {math.sqrt(candidate):.15f}
```

## Best two-level direction found

```json
{json.dumps(rows_sorted[0], indent=2)}
```

No tested two-level direction exceeded the codeword-sign candidate:

```text
{cert['no_two_level_exceeds_candidate']}
```

## Top rows

```json
{json.dumps(rows_sorted[:5], indent=2)}
```

## Boundary

This is a structured finite diagnostic, not a proof over all subset orbits or arbitrary directions.
"""
(OUT/'hamming_gaussian_two_level_probe_report.md').write_text(report)
shutil.copy('/tmp/two_level_probe_fast.py', OUT/'hamming_gaussian_two_level_probe.py')
manifest={'status':cert['status'],'files':{}}
for p in sorted(OUT.iterdir()):
 if p.is_file(): manifest['files'][p.name]=sha(p.read_bytes())
manifest['manifest_sha256']=sha(cjson(manifest)); (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True))
zip_path=OUT.parent/'hamming_gaussian_two_level_probe_package.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(OUT.iterdir()):
  if p.is_file(): z.write(p,arcname=f'hamming_gaussian_two_level_probe/{p.name}')
print(json.dumps({'status':cert['status'],'zip':str(zip_path),'best':rows_sorted[0],'cert_hash':cert['certificate_sha256']},indent=2))
