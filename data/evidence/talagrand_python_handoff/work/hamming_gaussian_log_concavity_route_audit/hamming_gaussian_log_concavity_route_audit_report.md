# Hamming/Gaussian Log-Concavity Route Audit

Status:

```text
HAMMING_GAUSSIAN_LOG_CONCAVITY_ROUTE_AUDIT_COMPLETE
```

Certificate hash:

```text
d13fd8af4c6720afa036d2b74f5de0a73b6db81f2993337a96c1a623ae9d493c
```

## Purpose

The remaining shell-domination lemma is

\[
A_w(x)\le A_w(1)\left(rac1{24}\sum_i x_i^2ight)^{w/2},\qquad x_i\ge0.
\]

In log coordinates \(x_i=e^{z_i}\), this becomes the assertion that

\[
F_w(z)=\log A_w(e^z)-\log A_w(1)-rac w2\log\left(rac1{24}\sum_i e^{2z_i}ight)\le0.
\]

A tempting route would be to prove \(F_w\) is globally concave and maximize at the all-equal point.

## Result

That route is rejected.

Positive Hessian directions occur away from the all-equal point, so \(F_w\) is not globally concave.

| shell | Hessian max at equal | max sampled Hessian eigenvalue | best sampled ratio |
|---:|---:|---:|---:|
| 8 | -8.11850586757e-15 | 1.91923987117 | 1.0000000000000000 |
| 12 | 1.13797860024e-13 | 1.91533495457 | 1.0000000000000000 |
| 16 | 1.06581410364e-14 | 2.21660222069 | 1.0000000000000000 |


## Meaning

The shell-domination lemma is still numerically supported: no sampled point exceeded ratio 1.

But the proof cannot be a simple global log-concavity proof. The remaining residue is sharper:

```text
prove Veronese-constrained Krawtchouk/SOS domination, or prove uniqueness of the positive KKT fixed point.
```
