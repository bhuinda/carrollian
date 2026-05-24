#!/usr/bin/env python3
import json, pandas as pd
from pathlib import Path
ROOT=Path(__file__).resolve().parent
cert=json.load(open(ROOT/'registered_support_matrix_units_certificate.json'))
assert cert['status']=='D20_TINY_POINTER_A985_REGISTERED_SUPPORT_MATRIX_UNITS_CERTIFIED'
match=pd.read_csv(ROOT/'legacy_to_raw_sector_match.csv')
expected={6:9,25:30,26:29,33:19}
for k,v in expected.items():
    row=match[match.legacy_sector==k]
    assert len(row)==1
    assert int(row.iloc[0].raw_sector)==v
supports=pd.read_csv(ROOT/'registered_support_raw_resolution.csv')
assert len(supports)==7
assert set(supports.resolution_status).issubset({'RAW_RESOLVED','TOP_RAW_ALL_SECTORS','ZERO_SUPPORT'})
manifest=pd.read_csv(ROOT/'registered_support_matrix_unit_manifest.csv')
hom=pd.read_csv(ROOT/'registered_support_raw_hom_basis_counts.csv')
assert len(hom)==49
assert len(manifest)==cert['support_matrix_unit_manifest_rows']
print(cert['status'])
