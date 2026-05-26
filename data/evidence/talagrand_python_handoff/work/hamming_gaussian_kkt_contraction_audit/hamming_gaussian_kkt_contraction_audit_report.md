# Hamming--Gaussian KKT contraction route audit

## Result

`HAMMING_GAUSSIAN_KKT_CONTRACTION_ROUTE_AUDIT_COMPLETE`

Certificate hash:

```text
6a6fd32ba5aa3173df7d256b8ca13f6505f7d2699a03d64ec45d4dd766792174
```

## What was tested

For the remaining Golay shell-domination lemma

```math
A_w(x) \le A_w(1)\left(rac1{24}\sum_i x_i^2ight)^{w/2},\quad x_i\ge0,\quad w=12,16,
```

I audited the KKT fixed-point map

```math
T_i(x)=\sqrt{rac{24}{w}\,\mathbb P_x(i\in B)}
```

with RMS normalization. Interior positive maximizers are fixed points of this map.

## Summary

| shell | max sampled eig radius | max sampled singular norm | converged starts | starts | monotone starts | max Hilbert pair contraction |
|---:|---:|---:|---:|---:|---:|---:|
| 12 | 1.844757724013 | 2.102419635150 | 62 | 62 | 62 | 0.433386041279 |
| 16 | 1.976744582036 | 2.416777180752 | 62 | 62 | 62 | 0.409139135559 |


## Interpretation

The simple Euclidean/log-coordinate contraction route is too strong: sampled singular norms or projective-pair contractions exceed one. This does not disprove the shell-domination lemma; it says the KKT proof must use a sharper metric, a Lyapunov function, or an SOS/Krawtchouk certificate rather than naïve global contraction.


## Current residue

The remaining rigorous closure is still one of:

```math
	ext{global KKT fixed-point uniqueness}
```

or

```math
	ext{Veronese-constrained Krawtchouk/SOS certificate.}
```
