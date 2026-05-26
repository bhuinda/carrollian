# Hamming Gaussian convex-order probe audit

Status: `HAMMING_GAUSSIAN_CONVEX_ORDER_PROBE_PASS`

## Main result

For the explicit Type II neighbor chain `H8^3 -> Golay`, positive Gaussian convex-order violations for the quartic probes

```text
f_S(x) = (sum_{i in S} x_i)^4, |S|=4
```

are exactly the weight-four Hamming roots. The exact identity is

```text
E_C f_S(Y) - E_G f_S(G) = -8 + 24 * 1_{1_S in C}.
```

So a root gives `+16` excess above the Gaussian reference, and a nonroot gives `-8`.

## Defect chain

| stage | wt4 roots | D4+ positive excess | max moment | Gaussian moment | max ratio | unit violation |
|---|---:|---:|---:|---:|---:|---:|
| C0_H8_oplus_3 | 42 | 672 | 64 | 48 | 1.333333 | True |
| C1_neighbor_1 | 18 | 288 | 64 | 48 | 1.333333 | True |
| C2_neighbor_2 | 6 | 96 | 64 | 48 | 1.333333 | True |
| C3_Golay_endpoint | 0 | 0 | 40 | 48 | 0.833333 | False |

Thus:

```text
R4:  42 -> 18 -> 6 -> 0
D4+: 672 -> 288 -> 96 -> 0
```

## Meaning

This proves the first exact Hamming-to-Gaussian convex-order bridge: the Hamming root-killing chain is precisely cancellation of the first positive fourth-order Gaussian convex-probe defect. The endpoint has no positive fourth-probe obstruction at unit scale.

## Boundary

This does not prove full Talagrand convex order over every convex function. It proves the exact equality for the canonical fourth-order quartic probe family, which is the first finite obstruction family visible under the Walsh-Hermite lift.
