# Pairwise Schur Naive Square-Factor Obstruction

## Status

`PAIRWISE_SCHUR_NAIVE_SQUARE_FACTOR_OBSTRUCTED`

Certificate hash:

```text
60e5c8c99dc2140331b7a00734f376bfbedccebb49bb9afdc417d66a94e4a478
```

## What was tested

The tempting shortcut was:

```text
P_w = (x_0-x_1)^2 R_w.
```

This would remove the pairwise equality factor and reduce the proof to a smaller quotient.

## Result

That shortcut is false.

| shell | rest groups | quotient terms | remainder terms | square divisibility |
|---:|---:|---:|---:|---|
| 12 | 32144 | 20608 | 61824 | False |
| 16 | 8503 | 5566 | 16192 | False |


## Meaning

The visible factor `x_0-x_1` is present by construction, but a second literal factor does not divide the global labeled polynomial.

This is not a counterexample to Talagrand. It blocks a false shortcut.

The reason is structural: the Golay shell is invariant under `M24`, not under arbitrary coordinate transpositions fixing the other 22 labels. High transitivity does not imply literal `S24` symmetry of the polynomial.

## Correct next route

The final proof must use one of:

```text
1. M24-equivariant pair-stabilizer compression,
2. exact semialgebraic barrier certificate,
3. Krawtchouk/Terwilliger block SOS.
```

Naive Schur-square coefficient factorization is ruled out.
