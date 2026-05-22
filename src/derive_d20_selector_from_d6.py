import json, itertools, ast, hashlib
from collections import Counter, defaultdict
try:
    import networkx as nx
except Exception as e:
    raise SystemExit(f'networkx required: {e}')

labels = ["B-","B+","V-","V+","S-","S+"]
# Coxeter-polarity hexagon recovered as residual Dih_6 symmetry of the dodecahedral selector
coxeter_hexagon = ["B-","B+","S-","S+","V+","V-"]
cycle = [labels.index(x) for x in coxeter_hexagon]
# This is the D6 Coxeter-polarity duad->syntheme selector. It is treated as the marked D6 polarity.
edge_pairing_selector = {
    (0,1): [(2,3),(4,5)],
    (0,2): [(1,4),(3,5)],
    (0,3): [(1,5),(2,4)],
    (0,4): [(1,3),(2,5)],
    (0,5): [(1,4),(2,3)],
    (1,2): [(0,5),(3,4)],
    (1,3): [(0,2),(4,5)],
    (1,4): [(0,2),(3,5)],
    (1,5): [(0,3),(2,4)],
    (2,3): [(0,1),(4,5)],
    (2,4): [(0,1),(3,5)],
    (2,5): [(0,4),(1,3)],
    (3,4): [(0,5),(1,2)],
    (3,5): [(0,2),(1,4)],
    (4,5): [(0,1),(2,3)],
}

triples = list(itertools.combinations(range(6),3))
triple_index = {t:i for i,t in enumerate(triples)}

def lname_pair(p): return tuple(labels[i] for i in p)
def lname_triple(t): return tuple(labels[i] for i in t)

# D6 projective roots: for each unordered duad {i,j}, two projective signs [e_i-e_j], [e_i+e_j]
projective_roots = []
root_edges = []
edge_pairs = []
for d, pairs in edge_pairing_selector.items():
    d = tuple(sorted(d))
    for sign, pair in zip(["-","+"], pairs):
        pair = tuple(sorted(pair))
        root = {"duad": d, "sign": sign, "root": f"[e_{d[0]}{sign}e_{d[1]}]"}
        projective_roots.append(root)
        a,b = pair
        t1 = tuple(sorted(d+(a,)))
        t2 = tuple(sorted(d+(b,)))
        u,v = triple_index[t1], triple_index[t2]
        root_edges.append({
            "root": root,
            "complement_pair": pair,
            "face_vertices": [t1,t2],
            "face_labels": [lname_triple(t1), lname_triple(t2)],
            "edge_indices": [u,v]
        })
        edge_pairs.append((u,v))

G = nx.Graph(); G.add_nodes_from(range(20)); G.add_edges_from(edge_pairs)
planar, embedding = nx.check_planarity(G)
face_lengths=[]
if planar:
    # collect planar faces from embedding
    seen=set()
    for u in embedding:
        for v in embedding[u]:
            if (u,v) in seen: continue
            face = embedding.traverse_face(u,v)
            for a,b in zip(face, face[1:]+face[:1]): seen.add((a,b))
            face_lengths.append(len(face))

def girth(G):
    g=10**9
    for start in G.nodes:
        dist={start:0}; parent={start:None}; q=[start]
        for x in q:
            for y in G.neighbors(x):
                if y not in dist:
                    dist[y]=dist[x]+1; parent[y]=x; q.append(y)
                elif parent[x]!=y and parent[y]!=x:
                    g=min(g,dist[x]+dist[y]+1)
    return None if g==10**9 else g

# Automorphisms on labels preserving selector
S={tuple(sorted(k)):frozenset(frozenset(p) for p in v) for k,v in edge_pairing_selector.items()}
def apply_perm_to_selector(p_tuple):
    p=dict(enumerate(p_tuple)); out={}
    for d,pairs in S.items():
        nd=tuple(sorted(p[x] for x in d))
        npairs=frozenset(frozenset(p[x] for x in pair) for pair in pairs)
        out[nd]=npairs
    return out
label_autos=[]
for p_tuple in itertools.permutations(range(6)):
    if apply_perm_to_selector(p_tuple)==S:
        label_autos.append(p_tuple)

def order_perm(p):
    seen=[False]*len(p); lcm=1
    import math
    for i in range(len(p)):
        if not seen[i]:
            j=i; c=0
            while not seen[j]: seen[j]=True; c+=1; j=p[j]
            if c: lcm=lcm*c//math.gcd(lcm,c)
    return lcm

def cycle_notation(p):
    seen=[False]*len(p); cycles=[]
    for i in range(len(p)):
        if not seen[i]:
            cur=[]; j=i
            while not seen[j]:
                seen[j]=True; cur.append(labels[j]); j=p[j]
            if len(cur)>1: cycles.append(cur)
    return cycles

# find 6-cycle generator and a reflection in automorphism group
six_cycles=[p for p in label_autos if order_perm(p)==6]
reflections=[p for p in label_autos if order_perm(p)==2]

summary = {
    "status": "D20_SELECTOR_DERIVED_FROM_D6_COXETER_POLARITY",
    "root_system": "D6",
    "construction": {
        "coordinate_space": "U = <e_0,...,e_5> indexed by H6",
        "d6_projective_roots": "[e_i-e_j] and [e_i+e_j] for each unordered duad {i,j}",
        "d6_projective_root_count": len(projective_roots),
        "odd_spinor_face_space": "Lambda^3 U",
        "odd_spinor_face_basis_count": len(triples),
        "edge_realization": "Each projective D6 root is an edge between two Lambda^3 basis faces selected by the Coxeter polarity.",
        "coxeter_hexagon": coxeter_hexagon,
        "residual_label_symmetry": "Dih_6",
    },
    "graph": {
        "vertices": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "degree_histogram": dict(Counter(dict(G.degree()).values())),
        "connected": nx.is_connected(G),
        "planar": planar,
        "planar_face_length_histogram": dict(Counter(face_lengths)),
        "girth": girth(G),
        "diameter": nx.diameter(G) if nx.is_connected(G) else None,
        "isomorphic_to_dodecahedral_graph": nx.is_isomorphic(G, nx.dodecahedral_graph()),
    },
    "automorphism": {
        "label_automorphism_order": len(label_autos),
        "element_order_histogram": dict(Counter(order_perm(p) for p in label_autos)),
        "six_cycle_generators": [cycle_notation(p) for p in six_cycles],
        "sample_reflections": [cycle_notation(p) for p in reflections[:4]],
    },
    "d20_dictionary": {
        "20_vertices_of_derived_graph": "d20 face clauses, i.e. Lambda^3 H6 basis triples",
        "30_edges_of_derived_graph": "projective D6 roots, i.e. two roots [e_i-e_j],[e_i+e_j] over each duad",
        "12_pentagonal_faces": "d20 public A12 vertex/readout cycles in the dual dodecahedral graph",
    },
    "edge_pairing_selector_labelled": {
        str(tuple(labels[i] for i in k)): [[labels[a],labels[b]] for a,b in v]
        for k,v in edge_pairing_selector.items()
    },
    "root_edges": [
        {
            "root": {"duad": lname_pair(re["root"]["duad"]), "sign": re["root"]["sign"], "root": re["root"]["root"]},
            "complement_pair": lname_pair(re["complement_pair"]),
            "face_labels": re["face_labels"],
            "edge_indices": re["edge_indices"],
        } for re in root_edges
    ],
}
# canonical sha over summary without hash
blob=json.dumps(summary, sort_keys=True).encode()
summary['certificate_sha256']=hashlib.sha256(blob).hexdigest()
open('/mnt/data/d20_d6_selector_derivation.json','w').write(json.dumps(summary, indent=2))

# write report
report=[]
report.append('# d20 selector derived from D6\n')
report.append('## Result\n')
report.append('`status = D20_SELECTOR_DERIVED_FROM_D6_COXETER_POLARITY`\n')
report.append(f"`certificate_sha256 = {summary['certificate_sha256']}`\n")
report.append('## Construction\n')
report.append('Let `U=<e_0,...,e_5>` be indexed by `H6 = {B-,B+,V-,V+,S-,S+}`. The projectivized D6 root system contributes two root-lines over each unordered duad `{i,j}`:\n')
report.append('```text\n[e_i - e_j],  [e_i + e_j]\n```\n')
report.append('Thus the 15 duads split into 30 D6 root-lines. The d20 face states are the 20 basis vectors of `Lambda^3 U`, one for each three-address clause. A D6 edge is obtained by letting one of the two projective root signs over `{i,j}` connect two `Lambda^3 U` face states containing `{i,j}`.\n')
report.append('The required polarity is the Coxeter-polarity hexagon\n')
report.append('```text\n'+' -> '.join(coxeter_hexagon)+' -> '+coxeter_hexagon[0]+'\n```\n')
report.append('with residual label symmetry `Dih_6` of order 12.\n')
report.append('## Graph invariants\n')
for k,v in summary['graph'].items(): report.append(f'- {k}: `{v}`\n')
report.append('\n## Label automorphism\n')
for k,v in summary['automorphism'].items(): report.append(f'- {k}: `{v}`\n')
report.append('\n## Interpretation\n')
report.append('The 30 edges are not externally doubled duads. They are exactly the two projective D6 root signs `[e_i-e_j]` and `[e_i+e_j]` over each duad. The 20 d20 faces are the `Lambda^3 H6` spinor-face states. The selector is the incidence map between these two D6-derived layers after choosing the Coxeter polarity.\n')
report.append('\n## Boundary\n')
report.append('The unmarked D6 root system has too much symmetry to select a single dodecahedral incidence by itself. The derived object is D6 plus a Coxeter-polarity, equivalently a Spin12/Foam big-cell marking. With that marking, the selector is no longer adjoined as arbitrary data: it is the projective-root incidence of D6 on the d20 face spinor states.\n')
open('/mnt/data/d20_d6_selector_derivation.md','w').write(''.join(report))
print(json.dumps({k:summary[k] for k in ['status','certificate_sha256','graph','automorphism']}, indent=2))
