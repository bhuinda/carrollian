# Q Residual Oriented-Block Factorization

## Status

`Q_RESIDUAL_ORIENTED_BLOCK_FACTORIZATION_CERTIFIED`

Certificate hash:

```text
abc00e7937fd57bacb7bbb3a7c94ca3cbb021b22ac43fa1ae5bb8b18abea33d3
```

## What this proves

The hard residual of \(Q_w\) on the ordered branch is not arbitrary.

Set

```text
x0 = x1 + c,  b = x1,  R = sum_i>=2 x_i^2.
```

For each shell \(w\), let

```text
O_w = { T : {0} union T is a shell block and 1 is not in that block }.
```

Then exactly:

```text
Q_res,w =
sum_{T in O_w} x_T[
  -2 b^3
  +(2w-4)c b^2
  +(3w-3)c^2 b
  +(w-1)c^3
  -(b+c)R
].
```

Equivalently:

```text
Q_res,w =
sum_{T in O_w} x_T*x0*((w-1)*x0^2-(w+1)*x1^2-R).
```

## Certified summary

| shell | oriented blocks | residual terms | difference terms | verified |
|---:|---:|---:|---:|---|
| 12 | 672 | 32256 | 0 | True |
| 16 | 176 | 8448 | 0 | True |


## Meaning

The remaining obstruction has a compact trace form:

```text
oriented asymmetric blocks times one universal cubic template.
```

The next proof target is therefore sharper:

```text
B_w >= 0
=> sum_{T in O_w} x_T*x0*((w-1)*x0^2-(w+1)*x1^2-R) >= 0.
```

This is much smaller than the raw residual polynomial.
