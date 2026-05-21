from __future__ import annotations
from pathlib import Path
import hashlib, json
import numpy as np
from . import golay,tensor,quotients,packet20,h_cycle,sixj,co1,deepcheck

TASKS=(
    ('golay', lambda root: golay.verify()),
    ('tensor', lambda root: tensor.verify(root)),
    ('quotients', lambda root: quotients.verify(root)),
    ('packet20', lambda root: packet20.verify(root)),
    ('H-cycle', lambda root: h_cycle.verify(root)),
    ('sixj', lambda root: sixj.verify()),
    ('co1', lambda root: co1.verify(root)),
)

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',',':'), ensure_ascii=False).encode('utf-8')

def h_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def h_json(obj) -> str:
    return h_bytes(canonical(obj))

def h_file(path: Path) -> str:
    d=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda: f.read(1<<20), b''):
            d.update(chunk)
    return d.hexdigest()

def array_payload(a):
    a=np.ascontiguousarray(a)
    if a.dtype.kind in {'U','S'}:
        values=a.astype(str).tolist()
        raw=canonical({'dtype':str(a.dtype),'shape':list(a.shape),'values':values})
    else:
        raw=canonical({'dtype':str(a.dtype),'shape':list(a.shape)}) + b'\n' + a.view(np.uint8).tobytes()
    return {'dtype':str(a.dtype),'shape':list(a.shape),'sha256':h_bytes(raw)}

def npz_payload(path: Path):
    z=np.load(path, allow_pickle=False)
    return {key:array_payload(z[key]) for key in sorted(z.files)}

def data_hashes(root: Path):
    constants_path=root/'data'/'constants.json'
    constants=json.load(open(constants_path, 'r', encoding='utf-8'))
    return {
        'data/constants.json':{'file_sha256':h_file(constants_path),'canonical_sha256':h_json(constants)},
        'data/tensor_sparse.npz':npz_payload(root/'data'/'tensor_sparse.npz'),
        'data/quotients.npz':npz_payload(root/'data'/'quotients.npz'),
        'generators/co1/projective_generators.npz':npz_payload(root/'generators'/'co1'/'projective_generators.npz'),
    }

def constants(root: Path):
    return json.load(open(root/'data'/'constants.json','r',encoding='utf-8'))

def object_counters(root: Path, results: dict):
    c=constants(root)
    co1r=results['co1']
    return {
        'finite_code':{
            'H8_size':results['golay']['H8_size'],
            'Golay_code_size':results['golay']['code_size'],
            'root_history':results['golay']['root_history'],
            'weight_enumerator':{str(k):v for k,v in results['golay']['weight_enumerator'].items()},
            'octads':results['golay']['weight_enumerator'].get(8,0),
            'dodecads':results['golay']['dodecads'],
            'tetrads':results['golay']['tetrads'],
            'sextets':results['golay']['sextets'],
            'tetrad_mate_count_histogram':results['golay']['tetrad_mate_count_histogram'],
            'dodecad_sextet_pattern_counts':results['golay']['dodecad_sextet_pattern_counts'],
        },
        'coherent_algebra':{
            'name':'A985',
            'dimension':985,
            'orbitals':c['be3']['orbitals'],
            'points':c['be3']['points'],
            'multiplication_tensor_nonzero_entries':results['tensor']['tensor_nonzeros'],
            'structure_constant_total':results['tensor']['coefficient_total'],
            'center_dimension':c['wedderburn']['center_dim'],
            'wedderburn_block_size_multiplicities':{str(k):v for k,v in c['wedderburn']['block_size_multiplicities'].items()},
            'wedderburn_sum_squares':c['wedderburn']['sum_squares'],
            'object_matrix_shape':[6,6],
            'object_matrix_sum':results['tensor']['M_sum'],
            'object_matrix':c['M'],
        },
        'quotient_tower':{
            'A985':985,
            'A236':c['A236'],
            'A42':{'classes':results['quotients']['A42_classes'],'support':results['quotients']['A42_support']},
            'A12':{'classes':results['quotients']['A12_classes'],'support':results['quotients']['A12_support']},
            'coefficient_total':results['quotients']['coefficient_total'],
            'pin_parity':results['quotients']['pin_parity'],
        },
        'packet20':{
            'packet':c['packet20']['packet'],
            'rank':results['packet20']['rank_C20'],
            'right_null':results['packet20']['right_null'],
            'left_null':results['packet20']['left_null'],
            'rank_CtC':results['packet20']['rank_CtC'],
            'rank_skew':results['packet20']['rank_skew'],
            'pfaffian_skew':results['packet20']['pfaffian_skew'],
            'det_stretched':results['packet20']['det_stretched'],
            'C20':c['packet20']['C20'],
        },
        'H-cycle':results['H-cycle'],
        'sixj_scalar_block':results['sixj'],
        'projective_Leech_shell':{
            'degree':co1r['degree'],
            'type_counts':co1r['type_counts'],
            'base_abs_inner_products':co1r['base_abs_inner_products'],
        },
    }

def group_theory_counters(root: Path, results: dict):
    c=constants(root)
    co1r=results['co1']
    return {
        'Be3':{
            'order':c['be3']['order'],
            'order_factorization':{'2':10,'3':2},
            'points':c['be3']['points'],
            'orbitals':c['be3']['orbitals'],
            'coherent_algebra':'A985',
        },
        'Co1_projective_Leech':{
            'order':co1r['order'],
            'order_factorization':co1r['order_factorization'],
            'degree':co1r['degree'],
            'transitive':co1r['transitive'],
            'orbit':co1r['orbit'],
            'point_stabilizer_order':co1r['point_stabilizer_order'],
            'point_stabilizer_order_factorization':co1r['point_stabilizer_order_factorization'],
            'generator_count':co1r['generators']['count'],
            'generator_family_counts':co1r['generators']['family_counts'],
            'generator_order_counts':co1r['generators']['order_counts'],
            'generator_orders_by_name':co1r['generators']['orders_by_name'],
            'generator_nontrivial_cycle_counts_by_name':co1r['generators']['nontrivial_cycle_counts_by_name'],
            'projective_vertex_type_counts':co1r['type_counts'],
            'base_abs_inner_product_distribution':co1r['base_abs_inner_products'],
        },
        'quotient_symmetries':{
            'Pin_to_CY':'A42_to_A12',
            'pin_parity_verified':results['quotients']['pin_parity'],
            'A42_classes':results['quotients']['A42_classes'],
            'A12_classes':results['quotients']['A12_classes'],
        },
    }

def build(root):
    root=Path(root)
    results={name: fn(root) for name,fn in TASKS}
    assert all(results[name] for name,_ in TASKS)
    result_hashes={name:h_json(results[name]) for name,_ in TASKS}
    counters=object_counters(root,results)
    groups=group_theory_counters(root,results)
    from . import hamiltonian
    H_payload={
        'name':'H',
        'interpretation':'Diophantine Hamiltonian of the verifier residuals',
        'residual_schema':hamiltonian.residual_schema(root),
        'quotient_automorphisms':hamiltonian.quotient_automorphisms(root),
    }
    payload={
        'schema':'gnatural.certificate.v3.H-cycle',
        'object':'Gnatural',
        'status':'PASS',
        'counters':counters,
        'group_theory':groups,
        'H':H_payload,
        'data_hashes':data_hashes(root),
        'results':results,
        'result_hashes':result_hashes,
    }
    payload['deep_invariant_audit']=deepcheck.analyze(payload)
    payload['certificate_sha256']=h_json(payload)
    return payload
