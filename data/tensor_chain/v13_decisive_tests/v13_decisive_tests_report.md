# v13 decisive tests for R_Omega

## Scope

This pass runs the next tests after the Fano-to-6j construction: seven-null-point sweep, Spin12 foam lift, mode-by-mode 6j typing, rank-lock truncation, and shuffle controls. The tests use the v8 three-zone Fano data; seven-point distributions are reconstructed by uniform splitting inside `L3\P1` and `F7\L3`.

## Seven-null-point sweep

Best raw nullification:

- null point: `110`
- fit energy: `0.281512`
- S4 invariant energy: `0.308791`
- signed-D6 invariant energy: `0.166267`

Best normalized nullification:

- null point: `011`
- fit energy: `0.282513`
- S4 invariant energy: `0.449515`
- signed-D6 invariant energy: `0.165271`

Interpretation: nullifying `001` deletes the dominant clean point corridor. Other null choices preserve that mass as one tetrahedral edge, so they carry far more six-channel fit energy.

## Mode-by-mode 6j typing

| R_Omega mode | best null | fit energy | top tetrahedral orbit | S4 inv. | signed-D6 inv. |
|---:|---|---:|---|---:|---:|
| 1 | `011` | 0.365203 | `adjacent_edges` | 0.170565 | 0.000042 |
| 2 | `010` | 0.188158 | `same_edge` | 0.526695 | 0.165581 |
| 3 | `011` | 0.109828 | `opposite_edges` | 0.165720 | 0.066723 |
| 4 | `010` | 0.038029 | `same_edge` | 0.412120 | 0.163882 |
| 5 | `100` | 0.102427 | `same_edge` | 0.310641 | 0.166490 |
| 6 | `001` | 0.000583 | `opposite_edges` | 0.422757 | 0.141180 |

## Spin12 foam lift

The lift used here is the compound-matrix lift

```text
Foam(A6) = diag(trace(A6)/6, compound_2(A6)) on 1 ⊕ Λ²H6.
```

The strongest wedge-square lift occurs for null `010` / `raw` with wedge2 norm `2061782239.635779` and foam participation rank `1.554031`.

## Rank-lock truncation

Minimal truncated rank reaching participation-rank `e` in `alpha ∈ [0,5]`: `4`.

| rank k | R_k energy | e reachable | alpha | PR(alpha) | PR(alpha=1) |
|---:|---:|---|---:|---:|---:|
| 1 | 0.543292 | False | 1.220000 | 1.298405 | 1.294832 |
| 2 | 0.927663 | False | 5.000000 | 2.016707 | 1.663468 |
| 3 | 0.980078 | False | 5.000000 | 2.574824 | 1.996588 |
| 4 | 0.987835 | True | 2.773585 | 2.718282 | 2.118523 |
| 5 | 0.992327 | True | 1.894798 | 2.718282 | 2.220883 |
| 6 | 0.995674 | True | 1.566014 | 2.718282 | 2.313059 |
| 7 | 0.997240 | True | 1.413594 | 2.718282 | 2.378353 |
| 8 | 0.998490 | True | 1.298560 | 2.718282 | 2.444460 |

## Shuffle controls

Original best normalized 6j-fit energy: `0.282513`.

| control | trials | mean | std | max | original percentile |
|---|---:|---:|---:|---:|---:|
| `random_orthogonal_same_singular_values` | 50 | 0.032085 | 0.021376 | 0.098458 | 1.000000 |
| `random_row_col_permutation` | 50 | 0.112671 | 0.115886 | 0.535777 | 0.920000 |
| `random_strategy_fano_weight_shuffle` | 50 | 0.117725 | 0.109266 | 0.492761 | 0.900000 |

## Result

The decisive split is now visible: the clean-point nullification is the correct geometric contraction to expose the small 6j shadow, while the all-null sweep shows that the dominant residual mass can be reintroduced as a single tetrahedral edge whenever a non-clean point is nullified. The e-lock test determines whether the two-mode band alone suffices or whether monodromy/tail structure is required.
