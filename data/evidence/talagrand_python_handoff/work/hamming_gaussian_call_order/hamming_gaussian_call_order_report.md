# Hamming Gaussian call-order probe audit

Status: `HAMMING_GAUSSIAN_CALL_ORDER_PROBE_PASS`

## Main result

The quartic obstruction has now been refined to the full one-dimensional convex-order call-function test for the canonical four-coordinate projections.

For each four-subset `S`, the marginal `L_S=sum_{i in S}Y_i` has one of two distributions:

- root type if `1_S in C`: `P(-4)=1/8, P(0)=6/8, P(4)=1/8`;
- nonroot type otherwise: four-independent-Rademacher sum.

Against the Gaussian reference `N(0,4)`, the maximum call defects at unit scale are:

- root type: `0.088292939656713` at threshold `-2.300698760752016`;
- nonroot type: `0.041951399362246` at threshold `-0.977552822229339`.

The critical contraction scales for domination by `N(0,4)` over this one-dimensional call family are:

- root type: `0.823414120688574`;
- nonroot type: `0.944064800851673`.

## Stage profile

| stage | wt4 roots | critical scale for all 4-call probes | max unit call defect | root-specific extra defect |
|---|---:|---:|---:|---:|
| C0_H8_oplus_3 | 42 | 0.823414120689 | 0.088292939657 | 1.946344692368 |
| C1_neighbor_1 | 18 | 0.823414120689 | 0.088292939657 | 0.834147725300 |
| C2_neighbor_2 | 6 | 0.823414120689 | 0.088292939657 | 0.278049241767 |
| C3_Golay_endpoint | 0 | 0.944064800852 | 0.041951399362 | 0.000000000000 |

## Interpretation

This is a correction and strengthening of the fourth-moment result. The Golay endpoint kills the root-specific fourth-order/Hermite obstruction, but full one-dimensional convex order is stricter than fourth moments: even a nonroot four-Rademacher marginal has a small positive call defect relative to the matching Gaussian at unit scale.

Thus root killing should be read as improving the necessary contraction scale from the root threshold to the nonroot threshold, not as proving full unit-scale convex order.

## Boundary

This audit proves exact one-dimensional call-order data for all four-coordinate probes by symmetry/type. It does not prove full multivariate convex order or the Talagrand theorem. It isolates the root-specific obstruction from the universal nonroot Rademacher baseline.
