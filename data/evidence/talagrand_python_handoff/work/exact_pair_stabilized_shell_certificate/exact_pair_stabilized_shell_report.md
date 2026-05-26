# Exact Pair-Stabilized Shell Gap Certificate

## Status

`EXACT_PAIR_STABILIZED_SHELL_GAP_CERTIFIED`

Certificate hash:

```text
fcc385844da640b418c36cb0f15e1ddec923e815d6593e6a9802bf012fb90c54
```

## What this proves

Take a vector with two distinguished coordinates:

```text
x_0=A, x_1=B, x_2=...=x_23=C.
```

By homogeneity set \(C=1\). The shell gap is

```text
P_w(A,B)
=
A_w(1)(A^2+B^2+22)^(w/2)
-
24^(w/2)(n11 AB+n10(A+B)+n00).
```

For \(w=12,16\), substitute

```text
A=u+v, B=u-v, y=v^2.
```

Then exactly:

```text
P_w = (u-1)^2 Q_w(u) + v^2 R_w(u,v^2)
```

with all coefficients of \(Q_w\) and \(R_w\) nonnegative integers.

## Certified rows

| shell | Q nonnegative | R nonnegative | Q min | R min |
|---:|---|---|---:|---:|
| 12 | True | True | 164864 | 164864 |
| 16 | True | True | 194304 | 194304 |


## Meaning

This is an exact proof for the pair-stabilized 3-level family. It does not prove the full multilevel theorem, but it closes the natural stabilizer model for one pair and strengthens the route to Barrier Schur Compression.
