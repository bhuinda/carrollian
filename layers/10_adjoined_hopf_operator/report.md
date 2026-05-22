# Adjoined Hopf operator construction

status: `ADJOINED_HOPF_OPERATOR_CONSTRUCTED`
sha256: `6c95176ce65381ca72e08fc9e81647128d295ab298813076fd9de0b9386ea6d3`

## Operator

\[
\Omega_{HB}=I_{39}+A_{\mathrm{swap}}+A_{\mathrm{dual\ each}}.
\]

On the closed-loop quotient:

\[
R_\Omega=I_{297}+B(A_{\mathrm{swap}}+A_{\mathrm{dual\ each}})L.
\]

On the full tube-pair space it is represented factored as:

\[
\Phi_\Omega=S R_\Omega P.
\]

This is a deterministic section-mediated kernel renormalization, not a raw annular permutation.

## Certified properties

| property | value |
|---|---:|
| preserves projection kernel | `True` |
| quotient rank | `297` |
| quotient invertible | `True` |
| HB39 stable | `True` |
| primitive rank | `39` |
| primitive invertible | `True` |
| primitive support | `183` |
| primitive diagonal | `False` |
| primitive scalar identity | `False` |
| small order <= 64 | `None` |

## Modular status

The inherited certified twist is still \(T=I_{39}\). With that inherited twist, this new nontrivial operator does not satisfy the modular relations, so this certificate constructs the missing operator layer but does not claim a completed modular datum.

- `omega_squared_identity`: `False`
- `omega_fourth_identity`: `False`
- `omega_cubed_equals_omega_squared`: `False`
- `ST3_minus_S2_support_with_T_identity`: `152`
- `ST3_minus_S2_rank_with_T_identity`: `10`

## Sparse first rows

- row 0: [[0, 1]]
- row 1: [[1, 1]]
- row 2: [[2, 1], [7, -499916], [10, 499895], [12, -375015], [16, -124997], [19, 249925], [22, -20], [23, 375003], [24, -125048], [28, 374994], [34, -30]]
- row 3: [[3, 1], [7, 26], [10, -102], [12, 500000], [16, 499997], [19, -43], [22, -16], [23, 499991], [24, 499937], [28, -500000], [34, -24]]
- row 4: [[4, 1]]
- row 5: [[5, 1], [7, -499992], [10, 499997], [19, -4]]
- row 6: [[6, 1], [7, -416607], [8, -48], [10, 249868], [12, 187488], [16, 62515], [17, -333361], [19, 208264], [21, -333265], [22, 333311], [23, -187683], [24, -437569]]
- row 7: [[7, 5], [19, -2]]
- row 8: [[8, 1]]
- row 9: [[7, 166665], [9, 1], [10, -499967], [12, -62503], [16, -187500], [19, 41670], [22, 2], [23, -437494], [24, 312515], [28, 62500], [34, 3]]
