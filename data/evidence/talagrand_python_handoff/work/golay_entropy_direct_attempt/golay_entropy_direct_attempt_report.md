# Direct attempt: Golay entropy shell domination

## Status

`DIRECT_VARIATIONAL_AND_SANDPILE_ATTEMPT_COMPLETE_NO_COUNTEREXAMPLE`

Certificate hash:

```text
6a9b87b2a874244e124ae6ee6e7531bda4240c44881516aa5789b6b8f3830a65
```

## Target

For \(w=12,16\), maximize

\[
F_w(z)
=
\log A_w(e^z)-\log A_w(1)
-rac w2\log\left(rac1{24}\sum_i e^{2z_i}ight).
\]

The shell domination lemma is equivalent to

\[
F_w(z)\le0
\qquadorall z\in\mathbb R^{24}.
\]

## What was attempted

1. Structured pattern search: one-hot, two-level supports, random high-variance directions.
2. Analytic-gradient L-BFGS multistart optimization.
3. KKT fixed-point iteration.
4. Sandpile-like gradient balancing, treating the gradient as block-coordinate load imbalance.

## Summary

| shell | blocks | best structured F | best L-BFGS F | best KKT F | counterexample? |
|---:|---:|---:|---:|---:|---:|
| 12 | 2576 | 0.000e+00 | 2.048e-15 | 1.721e-15 | False |
| 16 | 759 | 0.000e+00 | 1.509e-15 | 9.622e-16 | False |


All searches returned to the equality orbit within numerical tolerance. No counterexample was found.

## Interpretation

This strengthens the empirical state but does not close the theorem. The result is consistent with the sandpile/least-action hypothesis: high-variance configurations flow back toward the all-equal recurrent state under KKT and gradient-balancing dynamics.

## Files

- `structured_pattern_search.csv`
- `lbfgs_multistart_search.csv`
- `kkt_sandpile_iteration_trace.csv`
- `sandpile_like_gradient_balancing.csv`
- `direct_attempt_summary.csv`
- `golay_entropy_direct_attempt_certificate.json`
