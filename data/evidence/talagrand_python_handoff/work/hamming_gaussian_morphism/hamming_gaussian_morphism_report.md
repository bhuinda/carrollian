# Hamming Gaussian morphism invariant audit
Status: `HAMMING_GAUSSIAN_MORPHISM_INVARIANTS_PASS`

## Core result
The explicit Type II neighbor chain from `H8^3` to the Golay endpoint kills exactly the fourth order Walsh/Hermite obstruction modes:

```text
42 -> 18 -> 6 -> 0
```

The endpoint has the extended Golay weight enumerator:

```json
{
  "0": 1,
  "8": 759,
  "12": 2576,
  "16": 759,
  "24": 1
}
```

## Stage table

| stage | min wt | wt4/root count | wt8 | wt12 | wt16 | wt20 | Type II/self dual | orthant mass |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| C0_H8_oplus_3 | 4 | 42 | 591 | 2828 | 591 | 42 | True | 2^-12 |
| C1_neighbor_1 | 4 | 18 | 687 | 2684 | 687 | 18 | True | 2^-12 |
| C2_neighbor_2 | 4 | 6 | 735 | 2612 | 735 | 6 | True | 2^-12 |
| C3_neighbor_3 | 8 | 0 | 759 | 2576 | 759 | 0 | True | 2^-12 |

## Explicit bridge invariant

For uniform signs over a self-dual binary code `C`, the Walsh correlation rule is:

```text
E prod_{i in S} Y_i = 1 iff 1_S in C, else 0.
```
Thus the number of weight four codewords equals the squared norm of the fourth order Walsh correlation tensor. Under the Walsh-Hermite lift, this is the fourth order Hermite obstruction.

## Neighbor vectors

- neighbor 1: weight 12, support `[2, 4, 9, 10, 12, 13, 14, 16, 17, 18, 20, 22]`
- neighbor 2: weight 8, support `[3, 4, 9, 13, 15, 16, 19, 20]`
- neighbor 3: weight 16, support `[2, 5, 7, 8, 9, 10, 12, 14, 15, 16, 17, 18, 19, 21, 22, 23]`

## What this proves

It proves the finite invariant skeleton needed for a Hamming to Gaussian morphism: the Hamming root killing sequence is exactly fourth-order Walsh/Hermite obstruction cancellation, while orthant mass, Type II parity, self-duality, and code size stay fixed.

## What remains

- Identify the fourth-order Hermite obstruction with a convex-order defect functional in Talagrand/Song/Hua-Tudose style.
- Construct or locate a martingale/Laguerre partition whose cells realize the H8^3 neighbor-chain obstruction cancellation.
- Prove the finite Type-II neighbor closure is functorial under the Walsh-Hermite lift rather than merely invariant-compatible.
- Relate the endpoint Golay/G24 theta or moment series to the Gaussian convexification body produced by the finite assembly theorem.
