#!/usr/bin/env python3
import csv, json
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def rows(name):
    with open(ROOT/name, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

cert=json.load(open(ROOT/'registered_support_matrix_units_certificate.json', encoding='utf-8'))
assert cert['status']=='D20_TINY_POINTER_A985_REGISTERED_SUPPORT_MATRIX_UNITS_CERTIFIED'
match=rows('source_to_raw_sector_match.csv')
expected={6:9,25:30,26:29,33:19}
for k,v in expected.items():
    row=[item for item in match if int(item['source_sector'])==k]
    assert len(row)==1
    assert int(row[0]['raw_sector'])==v
supports=rows('registered_support_source_resolution.csv')
assert len(supports)==7
assert {row['resolution_status'] for row in supports}.issubset({'RAW_RESOLVED','TOP_RAW_ALL_SECTORS','ZERO_SUPPORT'})
manifest=rows('registered_support_source_matrix_unit_manifest.csv')
hom=rows('registered_support_raw_hom_basis_counts.csv')
assert len(hom)==49
assert len(manifest)==cert['support_matrix_unit_manifest_rows']
print(cert['status'])
