# Global Pairwise Schur Polynomial Target

## Status

`GLOBAL_PAIRWISE_SCHUR_POLYNOMIAL_TARGET_MATERIALIZED`

Certificate hash:

```text
40023551c171d985715e18fd91124ca699e9d1b2baa906251239cb3b9038b870
```

## What this computes

For the representative pair `(0,1)`, define

```text
A = A_w(x)
S = sum_i x_i^2
N = x_0 d_0 A - x_1 d_1 A
```

The pairwise Schur compression inequality is equivalent to

```text
P_w(x) >= 0
```

on the barrier region, where

```text
P_w = -(x_0-x_1)(S N - w A (x_0^2-x_1^2)).
```

The barrier region is

```text
24^(w/2) A_w(x) >= A_w(1) S^(w/2).
```

## Computed sparse polynomial targets

| shell | A terms | P terms | P degree | negative P terms | positive P terms |
|---:|---:|---:|---:|---:|---:|
| 12 | 2576 | 69440 | 15 | 34720 | 34720 |
| 16 | 759 | 18524 | 19 | 9262 | 9262 |


## Meaning

This is the exact global pairwise Schur target.

It explains why coefficientwise positivity alone cannot finish the theorem: `P_w` has negative coefficients and can fail below the barrier.

The final certificate must prove the semialgebraic implication

```text
24^(w/2) A_w - A_w(1) S^(w/2) >= 0
        =>
P_w >= 0.
```

That is now the concrete final algebraic target.
