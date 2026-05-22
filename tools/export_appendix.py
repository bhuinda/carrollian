#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'appendices'
OUT.mkdir(exist_ok=True)

BS = chr(92)
ROW = BS + BS

def load(rel):
    return json.loads((ROOT/rel).read_text())

def esc(s: object) -> str:
    text=str(s)
    return (text.replace(BS, BS+'textbackslash{}')
                .replace('_', BS+'_')
                .replace('&', BS+'&')
                .replace('%', BS+'%')
                .replace('#', BS+'#'))

status=load('manifests/theorem_status.json')
deps=load('manifests/dependency_hashes.json')

cert_rows=[]
for i, layer in enumerate(deps.get('layers', [])):
    cert_rows.append(f"{i} & {esc(layer.get('id'))} & {esc(layer.get('class'))} & {BS}texttt{{{esc(str(layer.get('declared_sha256',''))[:16])}}} {ROW}")
(OUT/'appendix_certificates.tex').write_text(
    BS+'section*{Certificate Ledger}\n'
    + BS+'begin{longtable}{rlll}\n'
    + BS+'toprule\n'
    + 'Layer & Identifier & Class & Declared hash prefix '+ROW+'\n'
    + BS+'midrule\n'
    + '\n'.join(cert_rows)+'\n'
    + BS+'bottomrule\n'
    + BS+'end{longtable}\n', encoding='utf-8')

claim_rows=[]
for k,v in status.get('statuses', {}).items():
    claim_rows.append(f"{esc(k)} & {esc(v)} {ROW}")
(OUT/'appendix_claims_table.tex').write_text(
    BS+'section*{Claim Status Ledger}\n'
    + BS+'begin{longtable}{ll}\n'
    + BS+'toprule\n'
    + 'Claim & Status '+ROW+'\n'
    + BS+'midrule\n'
    + '\n'.join(claim_rows)+'\n'
    + BS+'bottomrule\n'
    + BS+'end{longtable}\n', encoding='utf-8')

index_rows=[]
for i, layer in enumerate(deps.get('layers', [])):
    index_rows.append(f"{i} & {BS}texttt{{{esc(layer.get('certificate'))}}} & {len(layer.get('depends_on', []))} {ROW}")
(OUT/'appendix_layer_index.tex').write_text(
    BS+'section*{Layer Index}\n'
    + BS+'begin{longtable}{rll}\n'
    + BS+'toprule\n'
    + 'Layer & Certificate & Dependencies '+ROW+'\n'
    + BS+'midrule\n'
    + '\n'.join(index_rows)+'\n'
    + BS+'bottomrule\n'
    + BS+'end{longtable}\n', encoding='utf-8')
print(OUT)
