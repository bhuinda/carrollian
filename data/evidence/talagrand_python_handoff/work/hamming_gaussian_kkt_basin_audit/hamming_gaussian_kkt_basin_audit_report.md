# Hamming/Gaussian KKT Basin Audit

Status:

```text
HAMMING_GAUSSIAN_KKT_BASIN_AUDIT_COMPLETE
```

Certificate hash:

```text
685422d0b3d6e6a8a3326f8d1bb95d8d1a8152cb707206a8709c8c76e0b155ca
```

## Purpose

The remaining shell domination residue is equivalent to ruling out non-equal positive maximizers of

```text
A_w(x) / (A_w(1) ((1/24) sum_i x_i^2)^(w/2))
```

for the Golay shells w=12 and w=16.

For a positive maximizer, the KKT condition is:

```text
P_x(i in B) = (w/24) x_i^2
```

where B is drawn from the weight-w Golay shell with probability proportional to prod_{i in B} x_i.

## Result

| shell | starts | all converged to equal | best ratio | max KKT residual | KKT tangent spectral radius at equal |
|---:|---:|---:|---:|---:|---:|
| 12 | 296 | False | 1.0000000000000027 | 1.078e-11 | 0.260869565217 |
| 16 | 296 | False | 1.0000000000000040 | 1.312e-11 | 0.173913043478 |


## Meaning

No positive fixed point other than the all-equal point was found. The equal point is also a strict local attractor for the KKT map.

This does not close the global theorem. It narrows the residue to:

```text
prove global uniqueness of the positive KKT fixed point for w=12,16,
or produce a Veronese-constrained Krawtchouk/SOS certificate.
```
