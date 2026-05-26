# Talagrand Act-SDPI Reduction

## Status

`TALAGRAND_REDUCED_TO_ACT_SDPI_WITH_NO_NUMERICAL_VIOLATION`

Certificate hash:

```text
2cd840f340984f404490c9905018d32adbbc813e7baf605846a1c067ff6bb4c6
```

## What this pass does

The sector-33 obstruction is now handled by the finite certificate

```text
Lambda_hc(m) in ker(Act), for all 2048 masks.
```

Therefore the remaining Talagrand problem is not hidden-sector accounting. It is the Act-visible shell-domination inequality.

## Exact remaining target

Polynomial form:

```text
A_w(x) <= A_w(1) ((sum_i x_i^2)/24)^(w/2), x_i >= 0,
w in {12,16}.
```

Entropy/channel form:

```text
D(q || u_B) >= (w/2) D(p_q || u_24),
p_q(i)=P_q(i in B)/w.
```

## Channel spectral invariants

| shell | blocks | chi2/local eta | target 2/w | margin |
|---:|---:|---:|---:|---:|
| 12 | 2576 | 0.043478260870 | 0.166666666667 | 0.123188405797 |
| 16 | 759 | 0.021739130435 | 0.125000000000 | 0.103260869565 |


The local/Fisher-level contraction is far below the target. This is strong evidence, but not by itself a global KL-SDPI proof.

## Numerical log-sum-exp stress

The direct dual objective

```text
psi(theta)=log(A_w(exp(theta))/A_w(1)) - (w/2)log(mean_i exp(2 theta_i))
```

was optimized from multiscale random and indicator-like starts.

| shell | best psi | best ratio | grad norm | theta std |
|---:|---:|---:|---:|---:|
| 12 | 3.5527136788005009e-15 | 1.0000000000000036e+00 | 2.561e-10 | 7.072e-11 |
| 16 | 4.4408920985006262e-15 | 1.0000000000000044e+00 | 1.723e-09 | 3.194e-10 |


No positive violation was found. The best point is the equal vector, up to numerical tolerance.

## Proof-state consequence

The proof has now been reduced to one clean analytic theorem:

```text
Global KL-SDPI for the Golay shell incidence channel.
```

The sector-33 / height-correction ledger is closed; it cannot change the Act-dependent shell functional.
