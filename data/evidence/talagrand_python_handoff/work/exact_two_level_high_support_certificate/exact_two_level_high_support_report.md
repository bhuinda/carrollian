# Exact Two-Level High-Support Gap Certificate

## Status

`EXACT_TWO_LEVEL_HIGH_SUPPORT_GAP_FACTOR_CERTIFIED`

Certificate hash:

```text
fda864c48ca3c8547206117db97743a71cce111818ea9158ed1899322a243d71
```

## What this proves

For the high-support boundary strata left by the AM-GM sieve, restrict to two-level directions:

```text
x_i = z on a support of size k,
x_i = 1 on its complement of size r.
```

The exact shell gap is

```text
Gap_w(z)
=
A_w(1)(k z^2+r)^(w/2)
-
24^(w/2) sum_j N_j z^j.
```

For every checked high-support case,

```text
Gap_w(z) = (z-1)^2 Q_w,r(z)
```

and every coefficient of `Q_w,r` is a nonnegative integer. The full-support row is the identically zero equality case.

Therefore

```text
Gap_w(z) >= 0 for all z >= 0.
```

## Certified rows

| shell | complement r | support k | factor | nonnegative Q |
|---:|---:|---:|---|---|
| 12 | 0 | 24 | True | True |
| 12 | 1 | 23 | True | True |
| 12 | 2 | 22 | True | True |
| 12 | 3 | 21 | True | True |
| 12 | 4 | 20 | True | True |
| 12 | 5 | 19 | True | True |
| 16 | 0 | 24 | True | True |
| 16 | 1 | 23 | True | True |
| 16 | 2 | 22 | True | True |


## Meaning

This is an exact algebraic step beyond the numerical barrier scans.

It closes the high-support **two-level threshold** part of the boundary/barrier problem. The remaining gap is not two-level; it is arbitrary multilevel KKT/barrier behavior.
