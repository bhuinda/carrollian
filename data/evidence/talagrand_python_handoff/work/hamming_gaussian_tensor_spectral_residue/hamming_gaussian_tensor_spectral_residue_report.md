# Hamming/Gaussian Tensor Spectral Residue Reduction

Status:

```text
HAMMING_GAUSSIAN_TENSOR_SPECTRAL_RESIDUE_REDUCTION_COMPLETE
```

Certificate hash:

```text
89082a891b562f01fe57681565a0a5344747038251b416d90bd4247e0d478922
```

## Result

This pass attacks the remaining block-RMS domination lemma

A_w(x) <= A_w(1) ( (1/24) sum_i x_i^2 )^(w/2), x_i >= 0.

## What closed

1. Every shell has a strict local maximum at the all-equal point.
2. The octad shell w=8 is certified by a split spectral relaxation with ratio exactly 1.
3. Nonnegative multistart optimization found no counterexample for w=8,12,16,24.

## What did not close

The naive split spectral relaxation is not sharp for w=12 and w=16. This does not disprove the block-RMS lemma; it shows that a proof must use that split variables are constrained Veronese monomials y_I = product_i x_i, not arbitrary vectors.

## Best multistart ratios
- shell 8: ratio 1.000000000000001, cv 0.000e+00
- shell 12: ratio 1.000000000000001, cv 4.401e-13
- shell 16: ratio 1.000000000000001, cv 3.706e-11
- shell 24: ratio 1.000000000000000, cv 0.000e+00

## New precise residue

remaining problem = interior Veronese tensor spectral certificate.

The next route should be a Krawtchouk/SOS certificate using both the Golay association scheme and the monomial constraints.
