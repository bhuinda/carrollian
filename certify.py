#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, sys, os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
MUTABLE = {
    'certificate.json',
    'manifests/file_hashes.json',
    'manifests/canonical.json',
}

LAYER_EXPECTATIONS = [
  ('00_core','core','PASS','certificate_sha256'),
  ('01_tube_projection_section','tube_projection_section',None,'c985_tube_projection_section_sha256'),
  ('02_drinfeld_boundary','drinfeld_boundary','DRINFELD_GROTHENDIECK_BOUNDARY_CERTIFIED','drinfeld_boundary_certificate_sha256'),
  ('03_drinfeld_grothendieck_center','drinfeld_grothendieck_center','DRINFELD_GROTHENDIECK_CENTER_CERTIFIED','drinfeld_grothendieck_center_sha256'),
  ('04_drinfeld_idempotent_gluing','drinfeld_idempotent_gluing','DRINFELD_IDEMPOTENT_GLUING_CERTIFIED','drinfeld_idempotent_gluing_sha256'),
  ('05_drinfeld_wedderburn_trace','drinfeld_wedderburn_trace','DRINFELD_WEDDERBURN_TRACE_CERTIFIED','drinfeld_wedderburn_trace_sha256'),
  ('06_drinfeld_full_A985_lift','drinfeld_full_A985_lift','DRINFELD_FULL_A985_LIFT_CERTIFIED','drinfeld_full_A985_lift_sha256'),
  ('07_ribbon_modular_boundary','ribbon_modular_boundary','RIBBON_TWIST_TRIVIAL_AND_MODULAR_S_OBSTRUCTED','ribbon_and_modular_boundary_sha256'),
  ('08_modular_completion_obstruction','modular_completion_obstruction','MODULAR_COMPLETION_OBSTRUCTION_CERTIFIED','modular_completion_obstruction_sha256'),
  ('09_tube_kernel_descent_audit','tube_kernel_descent_audit','TUBE_KERNEL_DESCENT_AUDIT_CERTIFIED','tube_kernel_descent_audit_sha256'),
  ('10_adjoined_hopf_operator','adjoined_hopf_operator','ADJOINED_HOPF_OPERATOR_CONSTRUCTED','adjoined_hopf_operator_sha256'),
  ('11_twist_completion_test','twist_completion_test','TWIST_COMPLETION_OBSTRUCTED_FOR_ADJOINED_HOPF_OPERATOR','twist_completion_test_sha256'),
  ('12_derived_line_surface_trace','derived_line_surface_trace','DERIVED_LINE_SURFACE_TRACE_OPERATOR_CERTIFIED','derived_line_surface_trace_sha256'),
  ('13_hesse_tube_character_pencil','hesse_tube_character_pencil','HESSE_TUBE_CHARACTER_PENCIL_CERTIFIED','hesse_tube_character_pencil_sha256'),
  ('14_lasso_uniqueness_pseudomodular_audit','lasso_uniqueness_pseudomodular_audit','LASSO_UNIQUENESS_AND_PSEUDOMODULAR_INVARIANT_AUDIT_CERTIFIED','lasso_uniqueness_pseudomodular_audit_sha256'),
  ('15_intrinsic_carrier_dependency_geometry','intrinsic_carrier_dependency_geometry','INTRINSIC_CARRIER_DEPENDENCY_GEOMETRY_CERTIFIED','intrinsic_carrier_dependency_geometry_sha256'),
  ('16_mds_arc_hilbert_geometry','mds_arc_hilbert_geometry','MDS_ARC_HILBERT_AND_QUINTIC_WALL_CERTIFIED','mds_arc_hilbert_geometry_sha256'),
  ('17_wu_golay_quintic_resolvent','wu_golay_quintic_resolvent','WU_GOLAY_QUINTIC_RESOLVENT_CERTIFIED_WITH_GOLAY_EXTENSION_UNRESOLVED','wu_golay_quintic_resolvent_sha256'),
  ('18_canonical_24_syzygy_frame','canonical_24_syzygy_frame','CANONICAL_24_COORDINATE_SYZYGY_FRAME_CERTIFIED_GOLAY_SELECTION_STILL_OPEN','canonical_24_syzygy_frame_sha256'),
  ('19_quadratic_golay_selector_obstruction','quadratic_golay_selector_obstruction','QUADRATIC_GOLAY_SELECTOR_OBSTRUCTION_CERTIFIED','quadratic_golay_selector_obstruction_sha256'),
  ('20_wu_spinh_6j_marking','wu_spinh_6j_marking','WU_SPINH_OCTAD_SPIN12_6J_MARKING_CERTIFIED_GOLAY_SELECTOR_STILL_EXTERNAL','wu_spinh_6j_marking_sha256'),
  ('21_mog_resolvent_invariant','mog_resolvent_invariant','MOG_RESOLVENT_SEXTET_AND_WU_6J_TETRAHEDRON_CERTIFIED_GOLAY_SELECTOR_STILL_EXTERNAL','mog_resolvent_invariant_sha256'),
  ('22_mog_canonicity_boundary','mog_canonicity_boundary','MOG_COLUMN_SEXTET_CANONICITY_CERTIFIED_FULL_ROW_GOLAY_SELECTOR_STILL_EXTERNAL','mog_canonicity_boundary_sha256'),
  ('23_full_row_refined_selector_obstruction','full_row_refined_selector_obstruction','FULL_ROW_REFINED_GOLAY_SELECTOR_OBSTRUCTION_CERTIFIED_HEXACODE_REQUIRED','full_row_refined_golay_selector_obstruction_sha256'),
  ('24_hexacode_row_selector','hexacode_row_selector','HEXACODE_ROW_SELECTOR_CONSTRUCTED_GOLAY_CERTIFIED_CANONICALITY_EXTERNAL','hexacode_row_selector_sha256'),
]

def sha_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20), b''):
            h.update(chunk)
    return h.hexdigest()

def sha_json(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',',':')).encode()).hexdigest()

def load_json(rel: str | Path) -> dict:
    p = ROOT / rel if isinstance(rel, str) else rel
    return json.loads(p.read_text(encoding='utf-8'))

def require(cond: bool, msg: str, errors: list[str]) -> None:
    if not cond:
        errors.append(msg)

def verify_root(errors: list[str]) -> dict:
    cert=load_json('certificate.json')
    require(cert.get('schema') in {'qstar.verifier.full_certificate.v37','qstar.verifier.full_certificate.v38'}, 'root schema mismatch', errors)
    require(cert.get('status')=='QSTAR_VERIFIER_FULL_CERTIFIED', 'root status mismatch', errors)
    h=cert.get('qstar_full_certificate_sha256')
    body={k:v for k,v in cert.items() if k!='qstar_full_certificate_sha256'}
    require(isinstance(h,str) and len(h)==64 and h==sha_json(body), 'root self-hash mismatch', errors)
    return cert

def verify_layers(errors: list[str]) -> list[dict[str,Any]]:
    rows=[]
    for d,lid,status,sha_field in LAYER_EXPECTATIONS:
        rel=f'layers/{d}/certificate.json'
        p=ROOT/rel
        require(p.exists(), f'missing layer certificate {rel}', errors)
        if not p.exists(): continue
        data=load_json(p)
        if status is not None:
            require(data.get('status')==status, f'{lid}: status {data.get("status")!r} != {status!r}', errors)
        val=data.get(sha_field)
        require(isinstance(val,str) and len(val)==64, f'{lid}: missing/invalid declared sha field {sha_field}', errors)
        rows.append({'id':lid,'certificate':rel,'declared_sha_field':sha_field,'declared_sha256':val,'file_sha256':sha_file(p)})
    return rows

def verify_file_hashes(errors: list[str]) -> None:
    man=load_json('manifests/file_hashes.json')
    for ent in man.get('entries',[]):
        rel=ent['path']; p=ROOT/rel
        require(p.exists(), f'file manifest path missing: {rel}', errors)
        if p.exists():
            require(p.stat().st_size==ent['size'], f'file size mismatch: {rel}', errors)
            require(sha_file(p)==ent['sha256'], f'file sha mismatch: {rel}', errors)

def verify_dependencies(errors: list[str]) -> None:
    dep=load_json('manifests/dependency_hashes.json')
    for layer in dep.get('layers',[]):
        for ent in layer.get('dependency_hashes',[]):
            rel=ent['path']; p=ROOT/rel
            require(p.exists(), f'dependency missing: {layer.get("id")} -> {rel}', errors)
            if p.exists():
                require(sha_file(p)==ent['sha256'], f'dependency sha mismatch: {layer.get("id")} -> {rel}', errors)

def verify_theorem_status(errors: list[str]) -> None:
    th=load_json('manifests/theorem_status.json')
    require(th.get('statuses',{}).get('golay_independence_from_source')=='NOT_CLAIMED','Golay guardrail missing',errors)
    require(th.get('statuses',{}).get('strict_modularity')=='OBSTRUCTED_FOR_CURRENT_RAW_TUBE_DATA','modularity obstruction guardrail missing',errors)
    require(th.get('statuses',{}).get('hexacode_row_selector')=='ADJOINED_AND_CERTIFIES_EXTENDED_GOLAY','hexacode selector status missing',errors)

def verify_array_hashes(errors: list[str]) -> None:
    import numpy as np
    arr=load_json('manifests/array_hashes.json')
    for f in arr.get('npz_files',[]):
        p=ROOT/f['path']
        require(p.exists(), f'array file missing: {f["path"]}', errors)
        if not p.exists(): continue
        require(sha_file(p)==f['file_sha256'], f'array file sha mismatch: {f["path"]}', errors)
        data=np.load(p, allow_pickle=False)
        for aent in f.get('arrays',[]):
            name=aent['name']
            require(name in data.files, f'{f["path"]}: missing array {name}', errors)
            if name not in data.files: continue
            a=np.asarray(data[name])
            require(list(a.shape)==aent['shape'], f'{f["path"]}/{name}: shape mismatch', errors)
            require(str(a.dtype)==aent['dtype'], f'{f["path"]}/{name}: dtype mismatch', errors)
            digest=hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()
            require(digest==aent['sha256'], f'{f["path"]}/{name}: array sha mismatch', errors)

def run_lightweight_invariants(errors: list[str]) -> dict:
    import numpy as np
    out={}
    t=np.load(ROOT/'data/raw/tensor_sparse.npz', allow_pickle=False)['triples']
    out['tensor_support']=int(t.shape[0])
    out['tensor_coefficient_total']=int(t[:,3].sum())
    require(t.shape==(1414965,4), 'tensor_sparse triples shape mismatch', errors)
    require(int(t[:,3].sum())==2537360, 'tensor coefficient total mismatch', errors)
    q=np.load(ROOT/'data/raw/quotients.npz', allow_pickle=False)
    out['q42_classes']=len(set(map(int,q['q42_map'])))
    out['q12_classes']=len(set(map(int,q['q12_map'])))
    require(out['q42_classes']==42, 'q42 class count mismatch', errors)
    require(out['q12_classes']==12, 'q12 class count mismatch', errors)
    sb=np.load(ROOT/'data/raw/simple_branching_matrices.npz', allow_pickle=False)
    ok=bool(np.array_equal(sb['B236_42'] @ sb['B42_12'], sb['B236_12']))
    out['simple_branching_naturality']=ok
    require(ok, 'simple branching naturality fails', errors)
    leech=np.load(ROOT/'data/raw/leech_projective_generators.npz', allow_pickle=False)['projective_leech_vectors']
    out['leech_projective_vectors_shape']=list(leech.shape)
    require(tuple(leech.shape)==(98280,24), 'Leech projective vector shape mismatch', errors)
    return out


def verify_release_hashes(errors: list[str]) -> None:
    sums = ROOT / 'release' / 'SHA256SUMS.txt'
    require(sums.exists(), 'release/SHA256SUMS.txt missing', errors)
    if not sums.exists():
        return
    for line in sums.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split(maxsplit=1)
        require(len(parts)==2, f'malformed SHA256SUMS line: {line!r}', errors)
        if len(parts)!=2:
            continue
        digest, rel = parts
        rel = rel.lstrip('*')
        p = ROOT / rel
        require(p.exists(), f'release SHA256SUMS path missing: {rel}', errors)
        if p.exists():
            require(sha_file(p)==digest, f'release SHA256SUMS mismatch: {rel}', errors)

def do_fast() -> dict:
    errors=[]
    cert=verify_root(errors)
    layers=verify_layers(errors)
    verify_file_hashes(errors)
    verify_dependencies(errors)
    verify_theorem_status(errors)
    verify_release_hashes(errors)
    if errors:
        raise SystemExit('FAST verification failed:\n'+'\n'.join(errors))
    return {'mode':'fast','status':'QSTAR_VERIFIER_FULL_CERTIFIED','layers':len(layers),'root_sha256':cert['qstar_full_certificate_sha256']}

def do_audit() -> dict:
    out=do_fast()
    errors=[]
    verify_array_hashes(errors)
    inv=run_lightweight_invariants(errors)
    if errors:
        raise SystemExit('AUDIT verification failed:\n'+'\n'.join(errors))
    out.update({'mode':'audit','audit_invariants':inv})
    return out

def do_rebuild() -> dict:
    out=do_audit()
    present=[]
    for rel in ['src/certify_core.py','src/solve_half_braiding.py']:
        present.append({'path':rel,'present':(ROOT/rel).exists()})
    out.update({'mode':'rebuild','rebuild_boundary':'compact release: expensive historical reconstruction scripts are not all included; audit-grade certificates and lightweight raw-data checks are included','available_scripts':present})
    return out

def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['fast','audit','rebuild'], default='fast')
    ap.add_argument('--pretty', action='store_true')
    ap.add_argument('--json', action='store_true')
    args=ap.parse_args()
    if args.mode=='fast': out=do_fast()
    elif args.mode=='audit': out=do_audit()
    else: out=do_rebuild()
    if args.json:
        print(json.dumps(out, indent=2, sort_keys=True))
    else:
        print(out['status'])
        print('mode =', out['mode'])
        print('qstar_full_certificate_sha256 =', out['root_sha256'])
        print('layers =', out['layers'])
        if args.mode in {'audit','rebuild'}:
            for k,v in out.get('audit_invariants',{}).items():
                print(f'{k} = {v}')
        if args.mode=='rebuild':
            print('rebuild_boundary =', out['rebuild_boundary'])

if __name__=='__main__':
    main()
