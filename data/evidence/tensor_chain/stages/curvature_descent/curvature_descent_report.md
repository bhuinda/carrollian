# source_drop: R_Omega curvature, descent, and full W(D6) tests

## Scope

This pass turns the residual-curvature reading into finite tests on the contracted six-edge operators. It adds full `W(D6)` projection, pair-quotient descent, and finite 1-form curvature/closedness diagnostics.

## Full W(D6) result

For the six-edge action, full `W(D6)=2^5 ⋊ S6` conjugation has only scalar diagonal invariants:

```text
A_WD6 = (trace(A)/6) I_6.
```

So any off-diagonal, unequal diagonal, or signed-polarized structure is chamber data rather than a Regge-invariant scalar.

Best normalized six-channel operator:

- null point: `011`
- six-channel fit energy: `0.282513`
- full `W(D6)` invariant energy: `0.165271`
- full `W(D6)` breaking energy: `0.834729`

## Pair quotient descent

The quotient `H6 -> {B,V,S}` collapses opposite edge pairs:

```text
(B-,B+) -> B,   (V-,V+) -> V,   (S-,S+) -> S.
```

Best normalized pair3 descent energy: `0.993553`.

Best normalized pair3 breaking energy: `0.006447`.

This is the finite test for whether the six signed channels descend to a three-sector CY-style quotient or remain Pin/signed-channel data.

## Curvature / exactness test

Define the antisymmetric part of the six-edge operator by

```text
a = (A - A^T)/2.
```

Then test whether it is exact, `a_ij = phi_j - phi_i`, and measure triangle curls

```text
kappa(i,j,k)=a_ij+a_jk+a_ki.
```

Best normalized curvature diagnostics:

- antisymmetric energy fraction: `0.003390`
- non-exact skew energy fraction: `0.177793`
- Fano-star curl RMS: `0.000000`
- tetra-face curl RMS: `0.000000`
- top curl: `B-,V-,V+` / `other_triangle` = `16717.409766`

## Rank-tail curvature obstruction

| rank | best null | 6j fit | W(D6) inv. | pair3 descent | skew non-exact | Fano-star RMS | tetra-face RMS |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | `011` | 0.365203 | 0.000042 | 0.473316 | 0.203887 | 0.000 | 0.000 |
| 2 | `011` | 0.293167 | 0.165397 | 0.985424 | 0.175998 | 0.000 | 0.000 |
| 3 | `011` | 0.282741 | 0.163390 | 0.993971 | 0.173762 | 0.000 | 0.000 |
| 4 | `011` | 0.286103 | 0.163838 | 0.990937 | 0.175383 | 0.000 | 0.000 |
| 5 | `011` | 0.283906 | 0.164856 | 0.992256 | 0.177540 | 0.000 | 0.000 |
| 6 | `011` | 0.283810 | 0.164872 | 0.992245 | 0.177542 | 0.000 | 0.000 |
| 8 | `011` | 0.283233 | 0.165230 | 0.993416 | 0.177740 | 0.000 | 0.000 |
| 12 | `011` | 0.282520 | 0.165243 | 0.993455 | 0.177780 | 0.000 | 0.000 |
| 16 | `011` | 0.282513 | 0.165271 | 0.993553 | 0.177793 | 0.000 | 0.000 |

## Mode curvature/descent typing

| mode | best null | 6j fit | top orbit | W(D6) inv. | pair3 descent | skew non-exact | top curl type |
|---:|---|---:|---|---:|---:|---:|---|
| 1 | `011` | 0.365203 | `adjacent_edges` | 0.000042 | 0.473316 | 0.203887 | `other_triangle` |
| 2 | `010` | 0.188158 | `same_edge` | 0.165581 | 0.994418 | 0.120203 | `other_triangle` |
| 3 | `011` | 0.109828 | `opposite_edges` | 0.066723 | 0.754565 | 0.176730 | `other_triangle` |
| 4 | `010` | 0.038029 | `same_edge` | 0.163882 | 0.979255 | 0.176935 | `other_triangle` |
| 5 | `100` | 0.102427 | `same_edge` | 0.166490 | 0.215488 | 0.199071 | `other_triangle` |
| 6 | `001` | 0.000583 | `opposite_edges` | 0.141180 | 1.000000 | 0.000000 | `other_triangle` |

## Conclusion

The residual six-channel shadow is not a Regge-invariant scalar. It is a chamber-selecting operator with measurable signed-channel breaking, quotient-descent obstruction, and non-exact finite curl. The curvature language is therefore no longer just spectral: it has a concrete skew/exact/curl witness on the Fano-nullified 6j edge operator.
