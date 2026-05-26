# Hamming Gaussian Talagrand Bridge

## Result

`HAMMING_GAUSSIAN_TALAGRAND_BRIDGE_CONSTRUCTED`

This package installs the theorem-ledger bridge

```text
G24 dual distance 8
  -> sparse real coefficient projections below weight 8 are independent Rademacher forms
  -> Rademacher forms are subgaussian by the cosh/MGF bound
  -> universal Gaussian convex-order calibration by subgaussian comparison
  -> finite Gaussian assembly by the three-Gaussian/Talagrand theorem
```

## Core finite implication

For every support `S` with `|S| < 8` and every real coefficient vector `a`, the endpoint law

```text
sum_{i in S} a_i (-1)^{c_i},  c uniform in G24
```

is exactly the independent Rademacher law

```text
sum_{i in S} a_i eps_i.
```

This follows from the dual-distance 8 layer established in the previous certificate.

## Analytic calibration

For independent Rademacher variables,

```text
E exp(lambda sum a_i eps_i) = prod_i cosh(lambda a_i)
                         <= exp(lambda^2 ||a||_2^2 / 2).
```

So every such sparse projection is 1-subgaussian with Gaussian variance proxy `||a||_2^2`.

The bridge then imports the standard subgaussian comparison theorem used in the Talagrand paper: there is a universal constant `c > 0` such that a scaled centered 1-subgaussian vector is dominated in convex order by the corresponding Gaussian. The three-Gaussian theorem then supplies finite Gaussian assembly.

## Sanity check

MGF profile rows checked: `243`  
MGF bound all pass: `True`  
Maximum MGF ratio observed: `1.0`

## Boundary

This is a theorem-ledger bridge, not a sharp constant computation. The exact sharp Rademacher to Gaussian convex-order scale for arbitrary real coefficient vectors is left as a separate optimization problem.
