# Hamming/Gaussian Critical-Point Audit

Status:

```text
HAMMING_GAUSSIAN_CRITICAL_POINT_AUDIT_COMPLETE
```

Certificate hash:

```text
20bf4513b7f4e28c627ea8d2681e9de64d70d6e6894f0f8eb5837f59e4f88a94
```

## Purpose

This pass attacks the remaining block-RMS shell domination lemma for the Golay dodecad and complement-octad shells:

```text
A_w(x) <= A_w(1) ((1/24) sum_i x_i^2)^(w/2), x_i >= 0.
```

The Boolean boundary faces were already certified. This pass searches for an interior positive counterexample via the KKT/log-coordinate objective.

## Result

No interior counterexample was found. The best point for w=12 and w=16 is the all-equal point.

| shell | best ratio | cv(x) at best | grad norm | Hessian max eigen at equal |
|---:|---:|---:|---:|---:|
| 12 | 1.0000000000000016 | 8.388e-10 | 3.037e-09 | -7.391304e-01 |
| 16 | 1.0000000000000009 | 2.922e-10 | 1.577e-09 | -1.101449e+00 |


## What this closes

It closes another likely failure mode: there is no numerical evidence for an interior positive maximizer away from the all-equal point for the two remaining shells.

## What remains

This still does not prove the global shell domination lemma. The remaining theorem is now sharpened:

```text
Prove positive critical-point uniqueness for the w=12 and w=16 Golay shell polynomials,
or produce a Krawtchouk/SOS certificate implying it.
```
