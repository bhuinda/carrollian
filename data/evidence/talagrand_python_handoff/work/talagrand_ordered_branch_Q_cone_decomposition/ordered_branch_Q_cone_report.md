# Ordered-Branch Q Cone Decomposition

## Status

`ORDERED_BRANCH_Q_CONE_DECOMPOSITION_BUILT`

Certificate hash:

```text
31db8c1bd3fa291db6a3d1a05f10da4a89e8e97983bcb704909f52e78bd8f8af
```

## Move

The remaining target is:

```text
x_0 >= x_1, B_w >= 0 => Q_w >= 0.
```

On the ordered branch set:

```text
x_0 = x_1 + c,  c >= 0.
```

Any part of `Q_w` with nonnegative coefficients in `(c,x_1,rest)` is automatically positive.

## Result

| shell | groups | cone-positive groups | residual groups | residual terms | residual sign split |
|---:|---:|---:|---:|---:|---:|
| 12 | 32144 | 16688 | 15456 | 32256 | 2016+ / 30240- |
| 16 | 8503 | 4455 | 4048 | 8448 | 528+ / 7920- |


## Meaning

This trims the proof target.

The cone-positive part of `Q_w` is closed on the ordered branch without using the barrier. Only the residual rows still need the barrier condition.

The next exact target is:

```text
B_w >= 0 => Q_residual,w >= 0.
```

or, better,

```text
Q_residual,w = B_w R_w + ordered-cone-positive terms.
```
