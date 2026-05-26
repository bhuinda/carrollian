#!/usr/bin/env python3
import numpy as np, csv, json, hashlib
data=np.load("all_mask_lambda_vectors_sparse.npz")
entries=data["entries"]
shape=tuple(data["shape"])
assert shape==(2048,985)
assert entries.shape[1]==3
# rebuild gamma8 summary
mask=256
sub=entries[entries[:,0]==mask]
assert len(sub)==193
assert int(sub[:,2].sum())==53952
print("PASS all-mask bare lambda sparse table; gamma8 support/sum verified")
