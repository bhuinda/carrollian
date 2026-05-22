#!/usr/bin/env python3
from __future__ import annotations
import argparse, zipfile
from pathlib import Path

FIXED_ZIP_DATE=(2024,1,1,0,0,0)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    ap.add_argument('--out', required=True)
    args=ap.parse_args()
    root=Path(args.root).resolve()
    out=Path(args.out).resolve()
    files=sorted(p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in files:
            rel=p.relative_to(root.parent).as_posix()
            info=zipfile.ZipInfo(rel)
            info.date_time=FIXED_ZIP_DATE
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=(0o644 & 0xFFFF) << 16
            z.writestr(info, p.read_bytes())
    print(out)
if __name__=='__main__':
    main()
