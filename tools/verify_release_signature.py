#!/usr/bin/env python3
from __future__ import annotations
import hashlib, shutil, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUMS = ROOT / 'release' / 'SHA256SUMS.txt'
SIG = ROOT / 'release' / 'SHA256SUMS.sig'
PUB = ROOT / 'release' / 'signing_public_key.pem'

def sha_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20), b''):
            h.update(chunk)
    return h.hexdigest()

def main() -> None:
    missing=[str(p.relative_to(ROOT)) for p in [SUMS,SIG,PUB] if not p.exists()]
    if missing:
        raise SystemExit('missing release signature files: '+', '.join(missing))
    for line in SUMS.read_text().splitlines():
        line=line.strip()
        if not line or line.startswith('#'):
            continue
        digest, rel = line.split(maxsplit=1)
        rel = rel.lstrip('*')
        p=ROOT/rel
        if not p.exists():
            raise SystemExit(f'SHA256SUMS path missing: {rel}')
        got=sha_file(p)
        if got != digest:
            raise SystemExit(f'SHA256SUMS mismatch: {rel}: {got} != {digest}')
    if shutil.which('openssl'):
        cp=subprocess.run(['openssl','pkeyutl','-verify','-pubin','-inkey',str(PUB),'-rawin','-in',str(SUMS),'-sigfile',str(SIG)], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if cp.returncode != 0:
            print(cp.stdout)
            raise SystemExit('release signature verification failed')
        print('RELEASE_SIGNATURE_VERIFIED')
    else:
        print('RELEASE_HASHES_VERIFIED_OPENSSL_NOT_AVAILABLE')

if __name__ == '__main__':
    main()
