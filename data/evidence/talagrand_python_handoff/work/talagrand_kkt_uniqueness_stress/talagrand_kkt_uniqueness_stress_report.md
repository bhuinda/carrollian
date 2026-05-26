# Talagrand KKT Uniqueness Stress

## Status

`TALAGRAND_KKT_UNIQUENESS_STRESS_NO_NON_EQUAL_FIXED_POINT_FOUND`

Certificate hash:

```text
03d8e51b4f7a51ddf15173bd9500330034d76a1f9f469298cd11af57848c521d
```

## Purpose

After the sector-33 correction was proved to lie in `ker(Act)`, the remaining Talagrand target is the Act-visible shell-domination / SDPI inequality.

This pass stress-tests the interior KKT equations.  For shell weight `w`, an interior critical point must satisfy

```text
x_i^2 = (24/w) P_q(i in B),
q(B) ∝ prod_{i in B} x_i.
```

## Results

| shell | starts | converged equal | non-equal | monotone | best ratio | max final CV | max iterations |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 12 | 251 | 215 | 36 | 251 | 1.0000000000000044e+00 | 1.000e+00 | 28 |
| 16 | 251 | 211 | 40 | 251 | 1.0000000000000044e+00 | 7.071e-01 | 25 |


## Meaning

No non-equal positive KKT fixed point was found.

The proof obligation is now very specific:

```text
Prove KKT uniqueness for the Golay shell incidence channel.
```

Boundary indicator cases are already certified; if the only positive interior KKT point is equal, the Act-visible shell-domination inequality follows.
