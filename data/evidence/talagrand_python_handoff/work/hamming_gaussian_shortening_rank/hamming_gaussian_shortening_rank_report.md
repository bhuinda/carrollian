# Hamming--Gaussian shortening-rank reduction

Status: `HAMMING_GAUSSIAN_SHORTENING_RANK_REDUCTION_PASS`

Certificate hash:

```text
0840294daa0758b89541b909b510a971d7d44cf68f3cb458f103c83f3c31347a
```

## Main theorem-grade reduction

Let `C=G24` and let `Y=(-1)^c` for uniform `c in C`. For a support `S`, the law of `Y|_S` is uniform on the image of the projection `C -> F_2^S`. Since `G24` is self-dual, the annihilator of that image is exactly the shortened subcode

`C_S = { d in C : supp(d) subset S }`.

Therefore `Y|_S` is a vector of independent Rademacher signs iff `C_S=0`.

Because the minimum weight of `G24` is 8, every projection with `|S|<8` is exactly independent Rademacher. At `|S|=8`, the only non-independent supports are the 759 octads.

## Exact rank spectrum through support size 12

```text
"+"
".join(str(r) for r in rank_rows)+"
```

## Interpretation

This replaces the previous sparse-probe statement by a linear-code theorem: sparse Gaussian/Rademacher behavior is governed by the shortened Golay subcode rank. The global inequality is now reduced to higher-support shortened-subcode spectra and association-scheme domination.
