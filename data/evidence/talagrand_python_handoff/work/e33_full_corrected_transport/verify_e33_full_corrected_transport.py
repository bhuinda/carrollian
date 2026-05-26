#!/usr/bin/env python3
import numpy as np, csv, json
P=1000003
e=np.load("e33_vector.npz")["e33"]%P
corr=np.load("all_mask_corrected_transport_vectors_dense.npz")["corrected"]%P
assert e.shape==(985,)
assert int(np.count_nonzero(e))==56
assert corr.shape==(2048,985)
# gamma8 known checks
g=corr[256]
def signed(x):
    x=int(x)%P
    return x-P if x>P//2 else x
vals=[signed(x) for x in g[np.nonzero(g)[0]]]
assert int(np.count_nonzero(g))==237
assert sum(vals)==53952
assert sum(abs(x) for x in vals)==230880
print("PASS e33 and all corrected transports")
