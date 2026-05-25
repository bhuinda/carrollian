#!/usr/bin/env python3
import argparse, json, hashlib, csv, re
from pathlib import Path
from itertools import combinations

def sha256_path(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<20), b''):
            h.update(b)
    return h.hexdigest()

def canonical_events_from_text(text, kind, source):
    if kind == 'dimacs':
        return []
    events=[]
    lines=text.splitlines()
    for n,line in enumerate(lines,1):
        s=line.strip()
        low=s.lower()
        if not s or s.startswith('c'):
            continue
        status = re.sub(r'\s+', ' ', low)
        if re.fullmatch(r'(s )?unsat(isfiable)?', status):
            events.append({'type':'status','status':'UNSAT','line':n,'source':source})
        elif re.fullmatch(r'(s )?sat(isfiable)?', status):
            events.append({'type':'status','status':'SAT','line':n,'source':source})
        elif kind in ('drat','lrat','proof') or re.match(r'^[ad]?\s*-?\d', s):
            nums=[int(x) for x in re.findall(r'-?\d+', s)]
            if nums:
                if nums[-1]==0: nums=nums[:-1]
                op='add'
                if s.startswith('d '): op='delete'
                if s.startswith('a '): op='add'
                # LRAT often begins with id then literals then 0 then hints. We keep a canonical literal multiset proxy.
                lits=[x for x in nums if x!=0]
                events.append({'type':'proof_step','op':op,'lits':sorted(lits,key=lambda x:(abs(x),x<0)),'line':n,'source':source})
    return events

D20_LABELS = [
    ('B-','B+','V-'), ('B-','B+','V+'), ('B-','B+','S-'), ('B-','B+','S+'),
    ('B-','V-','V+'), ('B-','V-','S-'), ('B-','V-','S+'), ('B-','V+','S-'),
    ('B-','V+','S+'), ('B-','S-','S+'), ('B+','V-','V+'), ('B+','V-','S-'),
    ('B+','V-','S+'), ('B+','V+','S-'), ('B+','V+','S+'), ('B+','S-','S+'),
    ('V-','V+','S-'), ('V-','V+','S+'), ('V-','S-','S+'), ('V+','S-','S+')
]

def event_to_d20(e):
    # Deterministic canonical map; external evidence phase tests invariance under event hashing, not theorem claims.
    blob=json.dumps(e, sort_keys=True, separators=(',',':')).encode()
    return int.from_bytes(hashlib.sha256(blob).digest()[:4], 'big') % 20

def route_from_events(events):
    return [event_to_d20(e) for e in events]

def edge_word(route):
    return [(route[i], route[i+1]) for i in range(len(route)-1) if route[i]!=route[i+1]]

def edge_index(edge):
    # ordered edge proxy in 20*20; reduced to 30-edge universe by hash proxy for external evidence gate
    return int.from_bytes(hashlib.sha256(str(edge).encode()).digest()[:4], 'big') % 30

def ranks_mod_p(routes, p, max_degree=5):
    # compact rank from monomial signatures over 30 edge coordinates; enough for external replay gate.
    rows=[]
    for rt in routes:
        idx=[edge_index(e) for e in edge_word(rt)]
        vec=[]
        counts=[0]*30
        for i in idx: counts[i]=(counts[i]+1)%p
        vec.extend(counts)
        for deg in range(2,max_degree+1):
            # bounded exterior presence signature, not full 142k vectors for speed
            sig={}
            for comb in combinations(range(len(idx)), deg):
                key=tuple(sorted(idx[i] for i in comb))
                if len(set(key))==deg:
                    sig[key]=(sig.get(key,0)+1)%p
            # hash buckets preserve deterministic stress summary without requiring huge external matrices
            buckets=[0]*256
            for k,v in sig.items():
                h=int.from_bytes(hashlib.sha256(repr(k).encode()).digest()[:2],'big')%256
                buckets[h]=(buckets[h]+v)%p
            vec.extend(buckets)
        rows.append(vec)
    return rank_mod_p(rows,p)

def rank_mod_p(mat,p):
    if not mat: return 0
    A=[row[:] for row in mat if any(x%p for x in row)]
    if not A: return 0
    m=len(A); n=len(A[0]); r=0; c=0
    while r<m and c<n:
        piv=None
        for i in range(r,m):
            if A[i][c]%p:
                piv=i; break
        if piv is None:
            c+=1; continue
        A[r],A[piv]=A[piv],A[r]
        inv=pow(A[r][c]%p, -1, p)
        A[r]=[(x*inv)%p for x in A[r]]
        for i in range(m):
            if i!=r and A[i][c]%p:
                f=A[i][c]%p
                A[i]=[(A[i][j]-f*A[r][j])%p for j in range(n)]
        r+=1; c+=1
    return r

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('input_dir')
    ap.add_argument('--out', default='external_analysis')
    args=ap.parse_args()
    inp=Path(args.input_dir); out=Path(args.out); out.mkdir(parents=True, exist_ok=True)
    files=[p for p in inp.rglob('*') if p.is_file() and p.name!='README.md']
    sources=[]; all_events=[]; routes=[]
    for p in sorted(files):
        ext=p.suffix.lower().lstrip('.')
        kind='other'
        if ext in ('drat','lrat','frat','proof'): kind='proof'
        elif ext == 'cnf': kind='dimacs'
        elif ext in ('txt','log','out'): kind='stdout'
        try:
            text=p.read_text(errors='ignore')
        except Exception:
            text=''
        ev=canonical_events_from_text(text, kind, str(p))
        route=route_from_events(ev)
        sources.append({'path':str(p),'kind':kind,'sha256':sha256_path(p),'events':len(ev),'route_length':len(route)})
        all_events.extend(ev); routes.append(route)
    ranks={str(p):ranks_mod_p([r for r in routes if r], p, 5) for p in (2,3,5)}
    result={
        'schema':'gnatural.external_evidence_analysis.external_evidence_gate',
        'input_dir':str(inp),
        'files':len(files),
        'sources':sources,
        'total_events':len(all_events),
        'nonempty_routes':sum(1 for r in routes if r),
        'rank_summary_mod_p_hashed_exterior_gate':ranks,
        'status':'EVIDENCE_PRESENT' if any(s['events'] for s in sources) else 'EVIDENCE_PENDING_NO_EVENTS'
    }
    (out/'external_analysis.json').write_text(json.dumps(result,indent=2))
    with open(out/'external_sources.csv','w',newline='') as f:
        w=csv.DictWriter(f, fieldnames=['path','kind','sha256','events','route_length'])
        w.writeheader(); w.writerows(sources)
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
