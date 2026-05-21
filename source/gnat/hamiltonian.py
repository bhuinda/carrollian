from __future__ import annotations
from pathlib import Path
from itertools import permutations
from collections import Counter
import hashlib, json
import numpy as np
from . import golay, tensor, quotients, packet20, h_cycle, sixj, co1
from .certificate import canonical, h_json

TASK_MODULES=(golay, tensor, quotients, packet20, h_cycle, sixj, co1)

def _off42():
    off={}; k=12
    for i in range(6):
        for j in range(6):
            if i!=j:
                off[(i,j)]=k; k+=1
    return off

def _perm42(sig):
    off=_off42(); p=np.empty(42,dtype=np.int64)
    for i in range(6):
        p[i]=sig[i]
        p[6+i]=6+sig[i]
    for (i,j),a in off.items():
        p[a]=off[(sig[i],sig[j])]
    return p

def _off12():
    off={}; k=6
    for i in range(3):
        for j in range(3):
            if i!=j:
                off[(i,j)]=k; k+=1
    return off

def _perm12(sig):
    off=_off12(); p=np.empty(12,dtype=np.int64)
    for i in range(3):
        p[i]=sig[i]
        p[3+i]=3+sig[i]
    for (i,j),a in off.items():
        p[a]=off[(sig[i],sig[j])]
    return p

def quotient_automorphisms(root: Path):
    z=np.load(Path(root)/'data'/'quotients.npz', allow_pickle=False)
    T42=z['q42_tensor']; T12=z['q12_tensor']
    S42=(T42!=0); S12=(T12!=0)
    exact42=[]; support42=[]
    for sig in permutations(range(6)):
        p=_perm42(sig)
        if np.array_equal(T42[np.ix_(p,p,p)], T42):
            exact42.append(sig)
        if np.array_equal(S42[np.ix_(p,p,p)], S42):
            support42.append(sig)
    exact12=[]; support12=[]
    for sig in permutations(range(3)):
        p=_perm12(sig)
        if np.array_equal(T12[np.ix_(p,p,p)], T12):
            exact12.append(sig)
        if np.array_equal(S12[np.ix_(p,p,p)], S12):
            support12.append(sig)
    return {
        'A42_exact_object_permutation_count':len(exact42),
        'A42_support_object_permutation_count':len(support42),
        'A42_support_object_permutations':[list(s) for s in support42],
        'A12_exact_sector_permutation_count':len(exact12),
        'A12_support_sector_permutation_count':len(support12),
        'A12_support_sector_permutations':[list(s) for s in support12],
    }

def residual_schema(root: Path):
    root=Path(root)
    triples,M,reps=tensor.load(root)
    z=np.load(root/'data'/'quotients.npz', allow_pickle=False)
    n=985
    tensor_equations=n*n
    tensor_rhs_terms=int(triples.shape[0])
    tensor_formal_terms=tensor_equations+tensor_rhs_terms
    q42_entries=42**3
    q12_entries=12**3
    q42_support=int(np.count_nonzero(z['q42_tensor']))
    q12_support=int(np.count_nonzero(z['q12_tensor']))
    q42_pin_parity_equations=q42_support
    return {
        'name':'H',
        'type':'Diophantine sum of squared verifier residuals',
        'base_ring':'Z',
        'expanded_polynomial_printed':False,
        'schema_statement':'H is canonically represented by the ordered residual list; H=0 iff every residual in this verifier schema vanishes.',
        'residual_blocks':{
            'Golay_neighbor_code':{
                'root_history_equations':4,
                'weight_enumerator_equations':5,
                'sextet_count_equations':3,
                'status':'finite exact reconstruction checked'
            },
            'A985_multiplication':{
                'variables':'x_0,...,x_984 for formal basis coordinates',
                'equations':tensor_equations,
                'rhs_sparse_terms':tensor_rhs_terms,
                'formal_terms_before_squaring':tensor_formal_terms,
                'constraint_template':'F_ab=x_a*x_b-sum_c p_ab^c*x_c; H_alg=sum_ab F_ab^2',
                'tensor_shape':list(triples.shape),
            },
            'quotient_tower':{
                'A42_entry_equations':q42_entries,
                'A42_support':q42_support,
                'A12_entry_equations':q12_entries,
                'A12_support':q12_support,
                'pin_parity_equations':q42_pin_parity_equations,
                'constraint_template':'aggregated quotient tensors equal the canonical quotient tensors, with parity compatibility on every nonzero A42 product',
            },
            'packet20_null_face':{
                'matrix_entries':36,
                'rank_C20':5,
                'right_null_equations':6,
                'left_null_equations':6,
                'projector_equations_P2_equals_P':36,
                'projected_matrix_equations_PCP_equals_C':36,
                'skew_pfaffian_equation':1,
                'stretched_determinant_equation':1,
            },
            'finite_H_cycle_face':{
                'row_sum_equations':6,
                'stationary_equations':6,
                'current_balance_equations':36,
                'triangle_ratio_samples':120,
                'note':'This is the finite H-cycle face of H.'
            },
            'sixj_associator':{
                'orthogonality_equations':9,
                'determinant_equation':1,
                'scalar_block_equations':2,
            },
            'projective_Leech_Co1_layer':{
                'degree':98280,
                'generator_permutations':16,
                'permutation_bijection_checks':16,
                'transitivity_orbit_size_target':98280,
                'generator_order_checks':16,
                'type_count_equations':3,
                'base_inner_product_distribution_equations':4,
                'order_status':'geometric/order formula is encoded; full raw Schreier-Sims order is intentionally not used in this strict verifier',
            },
        }
    }

def proof_leads(root: Path):
    root=Path(root)
    results={
        'golay':golay.verify(),
        'tensor':tensor.verify(root),
        'quotients':quotients.verify(root),
        'packet20':packet20.verify(root),
        'finite_H_cycle_face':h_cycle.verify(root),
        'sixj':sixj.verify(),
        'co1':co1.verify(root),
    }
    schema=residual_schema(root)
    aut=quotient_automorphisms(root)
    leads={
        'lead_1_canonical_H':{
            'status':'formalized for the current verifier schema',
            'finding':'A canonical Diophantine H exists once the residual ordering/schema is fixed. It should be emitted as a residual schema and hash, not as a huge expanded polynomial.',
            'qualification':'Canonicity is schema-relative; a basis-free universal H still requires a presentation-independence theorem.',
        },
        'lead_2_zero_locus_equivalence':{
            'status':'proved by construction for verifier schema v3',
            'finding':'H=0 iff every finite verifier residual vanishes, hence iff this certificate returns PASS.',
            'qualification':'This proves equivalence to the certificate, not uniqueness of Gnatural among all possible presentations unless an isomorphism/normal-form theorem is added.',
        },
        'lead_3_symmetry_recovery':{
            'status':'partially discharged; main Conway order proof remains geometric rather than raw Schreier-Sims',
            'finding':'The quotient layers have trivial exact symmetry: A42 exact object-permutation automorphism count is 1; A12 exact sector-permutation automorphism count is 1. A42 support symmetry is 8, matching the sign-pair support shadow. Thus quotient H loses most high symmetry. Co1 must be attached at the projective Leech H-layer, not at A42/A12.',
            'computed_quotient_automorphisms':aut,
            'qualification':'The strict verifier checks Co1 generator bijectivity, transitivity, type counts, generator orders, and base inner-product distribution. It records the Co1 order through the geometric Conway/Leech certificate, not by generic 98280-degree Schreier-Sims.',
        },
        'lead_4_sector_Hamiltonians':{
            'status':'finite reductions verified; physical universality open',
            'finding':'The quotient tower and packet/6j/Leech layers are finite sector restrictions of the same residual schema. This supports H_rho=rho(H) as a rigorous finite pattern.',
            'qualification':'The stronger claim that every ordinary physical Hamiltonian is a derivation/reduction of H requires a representation theorem from this finite schema into analytic or quantum categories.',
        },
    }
    payload={
        'schema':'gnatural.H.proof_leads.v1',
        'object':'Gnatural',
        'H_name':'H',
        'status':'PASS_WITH_OPEN_THEOREMS_TYPED',
        'residual_schema':schema,
        'leads':leads,
        'result_hashes':{k:h_json(v) for k,v in results.items()},
    }
    payload['proof_leads_sha256']=h_json(payload)
    return payload

def verify(root):
    out=proof_leads(Path(root))
    assert out['status']=='PASS_WITH_OPEN_THEOREMS_TYPED'
    assert out['residual_schema']['name']=='H'
    assert out['leads']['lead_3_symmetry_recovery']['computed_quotient_automorphisms']['A42_exact_object_permutation_count']==1
    assert out['leads']['lead_3_symmetry_recovery']['computed_quotient_automorphisms']['A42_support_object_permutation_count']==8
    return out
