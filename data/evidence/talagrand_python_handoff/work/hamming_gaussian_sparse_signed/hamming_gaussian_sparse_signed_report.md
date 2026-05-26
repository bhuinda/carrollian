# Hamming Gaussian sparse signed call-order probe audit

Status: `HAMMING_GAUSSIAN_SPARSE_SIGNED_PROBE_PASS`

## Main result

Exhaustively tested all signed sparse linear projections `L=sum eps_i Y_i` with support size `1 <= k <= 5` for each stage of the chain `H8^3 -> neighbor1 -> neighbor2 -> Golay`.

For each projection distribution, the audit computed the full one-dimensional call-order defect against the matching Gaussian `N(0,k)` and the critical contraction scale needed for call domination.

## Stage code invariants

| stage | wt4 roots | min wt | Type II/self dual | code SHA256 prefix |
|---|---:|---:|---:|---|
| C0_H8_oplus_3 | 42 | 4 | True | `38d264462e02d2eb` |
| C1_neighbor_1 | 18 | 4 | True | `8e46cd3195f9b74e` |
| C2_neighbor_2 | 6 | 4 | True | `63b0473e6601af95` |
| C3_Golay_endpoint | 0 | 8 | True | `a0ae82a75890afd4` |

## Sparse signed profile

| stage | k | signed probes | distinct distributions | max unit call defect | min critical scale | excess over Golay max | scale loss vs Golay |
|---|---:|---:|---:|---:|---:|---:|---:|
| C0_H8_oplus_3 | 1 | 48 | 1 | 0.101057719599 | 0.797884560805 | 0.000000000000 | 0.000000000000 |
| C0_H8_oplus_3 | 2 | 1104 | 1 | 0.050596061106 | 0.898807877791 | 0.000000000000 | 0.000000000000 |
| C0_H8_oplus_3 | 3 | 16192 | 1 | 0.059011701057 | 0.921317731925 | 0.000000000000 | 0.000000000000 |
| C0_H8_oplus_3 | 4 | 170016 | 3 | 0.202115439197 | 0.797884560804 | 0.160164039835 | 0.146180240048 |
| C0_H8_oplus_3 | 5 | 1360128 | 3 | 0.107937941924 | 0.880001480187 | 0.062500000000 | 0.071531381762 |
| C1_neighbor_1 | 1 | 48 | 1 | 0.101057719599 | 0.797884560805 | 0.000000000000 | 0.000000000000 |
| C1_neighbor_1 | 2 | 1104 | 1 | 0.050596061106 | 0.898807877791 | 0.000000000000 | 0.000000000000 |
| C1_neighbor_1 | 3 | 16192 | 1 | 0.059011701057 | 0.921317731925 | 0.000000000000 | 0.000000000000 |
| C1_neighbor_1 | 4 | 170016 | 3 | 0.202115439197 | 0.797884560804 | 0.160164039835 | 0.146180240048 |
| C1_neighbor_1 | 5 | 1360128 | 3 | 0.107937941924 | 0.880001480187 | 0.062500000000 | 0.071531381762 |
| C2_neighbor_2 | 1 | 48 | 1 | 0.101057719599 | 0.797884560805 | 0.000000000000 | 0.000000000000 |
| C2_neighbor_2 | 2 | 1104 | 1 | 0.050596061106 | 0.898807877791 | 0.000000000000 | 0.000000000000 |
| C2_neighbor_2 | 3 | 16192 | 1 | 0.059011701057 | 0.921317731925 | 0.000000000000 | 0.000000000000 |
| C2_neighbor_2 | 4 | 170016 | 3 | 0.202115439197 | 0.797884560804 | 0.160164039835 | 0.146180240048 |
| C2_neighbor_2 | 5 | 1360128 | 3 | 0.107937941924 | 0.880001480187 | 0.062500000000 | 0.071531381762 |
| C3_Golay_endpoint | 1 | 48 | 1 | 0.101057719599 | 0.797884560805 | 0.000000000000 | 0.000000000000 |
| C3_Golay_endpoint | 2 | 1104 | 1 | 0.050596061106 | 0.898807877791 | 0.000000000000 | 0.000000000000 |
| C3_Golay_endpoint | 3 | 16192 | 1 | 0.059011701057 | 0.921317731925 | 0.000000000000 | 0.000000000000 |
| C3_Golay_endpoint | 4 | 170016 | 1 | 0.041951399362 | 0.944064800852 | 0.000000000000 | 0.000000000000 |
| C3_Golay_endpoint | 5 | 1360128 | 1 | 0.045437941924 | 0.951532861949 | 0.000000000000 | 0.000000000000 |

## Interpretation

The previous four-coordinate unsigned probe was only one slice. This audit includes all signed sparse projections up to the selected sparsity bound. The endpoint Golay code removes the special weight-four root obstruction, but the exact signed profile shows how much universal Rademacher baseline defect remains at each sparsity.

The decisive invariant remains the support-4 transition: the root chain `42 -> 18 -> 6 -> 0` is visible as a loss of the extra signed call-order obstruction and an improvement of the worst critical contraction scale at k=4.

## Boundary

This certificate is exact for sparse signed one-dimensional probes through kmax. It is not a proof of Talagrand's full convex-order theorem, and it does not cover arbitrary dense real coefficient vectors. The next target is to pass from finite sparse signed probes to a support-enumerator / dual-distance theorem that controls all coefficient vectors by symmetry and Krawtchouk/MacWilliams data.