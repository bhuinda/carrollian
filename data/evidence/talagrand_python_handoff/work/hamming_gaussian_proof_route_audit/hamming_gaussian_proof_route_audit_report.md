# Hamming/Gaussian Proof Route Audit

Status:

```text
HAMMING_GAUSSIAN_PROOF_ROUTE_AUDIT_COMPLETE
```

Certificate hash:

```text
aa0b59cf22ec8f26724c4b566da128bf1ce5b395ee171d0a67ff635df4ea1fd9
```

## Routes rejected

### Uniform elementary-symmetric domination

The naive inequality A_w <= (A_w(1)/binom(24,w)) e_w is false. Counterexample ratios found:

- w=8: ratio 35.206371, cv 2.905
- w=12: ratio 78.934387, cv 3.860
- w=16: ratio 29.792354, cv 3.270

### Pairwise RMS smoothing

Replacing a coordinate pair by its common RMS can decrease A_w. Worst sampled deltas:

- w=8: delta -9.211629e-01, bad fraction 0.1046
- w=12: delta -1.794959e-02, bad fraction 0.0425
- w=16: delta -2.694018e-03, bad fraction 0.0228

## Meaning

The remaining proof cannot be a crude complete-hypergraph comparison or simple coordinate smoothing. The surviving route is a Veronese-constrained Krawtchouk/SOS certificate for w=12 and w=16.
