#!/usr/bin/env python3
from __future__ import annotations
import json, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable

def run_certify(root: Path, mode: str = 'fast') -> subprocess.CompletedProcess[str]:
    return subprocess.run([PY, 'certify.py', '--mode', mode, '--pretty'], cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

def copy_root() -> Path:
    td = Path(tempfile.mkdtemp(prefix='qstar_tamper_'))
    dst = td / 'verifier'
    ignore = shutil.ignore_patterns('__pycache__', '.pytest_cache')
    shutil.copytree(ROOT, dst, ignore=ignore)
    return dst

def expect_failure(name: str, mutate, mode: str = 'fast') -> None:
    work = copy_root()
    try:
        mutate(work)
        cp = run_certify(work, mode=mode)
        if cp.returncode == 0:
            print(cp.stdout)
            raise SystemExit(f'{name}: verifier accepted tampered bundle')
        print(name)
    finally:
        shutil.rmtree(work.parent, ignore_errors=True)

def mutate_root_certificate(work: Path) -> None:
    p = work / 'certificate.json'
    data = json.loads(p.read_text())
    data['status'] = 'TAMPERED'
    p.write_text(json.dumps(data, indent=2, sort_keys=True))

def mutate_layer_certificate(work: Path) -> None:
    p = work / 'layers/13_hesse_tube_character_pencil/certificate.json'
    data = json.loads(p.read_text())
    data['status'] = 'TAMPERED'
    p.write_text(json.dumps(data, indent=2, sort_keys=True))

def mutate_array(work: Path) -> None:
    p = work / 'data/raw/tensor_sparse.npz'
    b = bytearray(p.read_bytes())
    b[-17] ^= 1
    p.write_bytes(bytes(b))

def mutate_manifest(work: Path) -> None:
    p = work / 'manifests/array_hashes.json'
    data = json.loads(p.read_text())
    data['schema'] = 'tampered.schema'
    p.write_text(json.dumps(data, indent=2, sort_keys=True))

def mutate_guardrail(work: Path) -> None:
    p = work / 'manifests/theorem_status.json'
    data = json.loads(p.read_text())
    data['statuses']['strict_modularity'] = 'CERTIFIED_NONTRIVIAL_MODULAR_ST'
    p.write_text(json.dumps(data, indent=2, sort_keys=True))

if __name__ == '__main__':
    expect_failure('TAMPER_CERTIFICATE_DETECTED', mutate_root_certificate)
    expect_failure('TAMPER_LAYER_CERTIFICATE_DETECTED', mutate_layer_certificate)
    expect_failure('TAMPER_ARRAY_DETECTED', mutate_array)
    expect_failure('TAMPER_MANIFEST_DETECTED', mutate_manifest)
    expect_failure('TAMPER_GUARDRAIL_DETECTED', mutate_guardrail)
    print('TAMPER_TESTS_PASS')
