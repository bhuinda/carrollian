# v15 — R_Omega chamber-source test

## Main result

The source of the full `W(D6)` breaking is now identified:

\[
\boxed{
R_\Omega^{(6)}\text{ breaks }W(D_6)\text{ mainly through the }B/S\text{ mirror chamber with }V\text{-sector suppression.}
}
\]

It is not primarily six-independent noise, and it is not primarily skew curl.  It is a pair-quotient chamber selection.

## Best normalized six-channel contraction

- best null point: `011`
- six-channel fit energy: `0.282513`
- WD6 scalar energy: `0.165271`
- pair diagonal-contrast energy: `0.327880`
- pair off-diagonal chamber energy: `0.500401`
- total orthogonal pair-chamber energy: `0.828281`
- non-pair residual energy: `0.006447`

Thus the orthogonal decomposition is approximately:

\[
R_\Omega^{(6)} = R_{W(D_6)} + R_{\mathrm{pair\ chamber}} + R_{\mathrm{nonpair}}
\]

with

\[\|R_{W(D_6)}\|^2/\|R\|^2=0.165271,\]
\[\|R_{\mathrm{pair\ chamber}}\|^2/\|R\|^2=0.828281,\]
\[\|R_{\mathrm{nonpair}}\|^2/\|R\|^2=0.006447.\]

So among the `W(D6)`-breaking part alone, the pair chamber accounts for

\[0.992276\]

of the breaking energy.

## Top pair-quotient components

| operator_id   |   null_point | operator_kind   | left_basis    | right_basis   |      coefficient |   energy_fraction_in_C |
|:--------------|-------------:|:----------------|:--------------|:--------------|-----------------:|-----------------------:|
| R_full        |          011 | normalized      | u0_scalar     | u0_scalar     | 241305           |            0.379132    |
| R_full        |          011 | normalized      | uV_BS_vs_V    | u0_scalar     | 202368           |            0.266652    |
| R_full        |          011 | normalized      | u0_scalar     | uV_BS_vs_V    | 178567           |            0.207616    |
| R_full        |          011 | normalized      | uV_BS_vs_V    | uV_BS_vs_V    | 150051           |            0.146601    |
| R_full        |          011 | normalized      | uBS_B_minus_S | u0_scalar     |      1.19145e-09 |            9.24287e-30 |
| R_full        |          011 | normalized      | uBS_B_minus_S | uV_BS_vs_V    |      8.81465e-10 |            5.05905e-30 |

The B-S splitting basis is essentially zero.  The active plane is the scalar/V-contrast plane:

\[
\langle u_0=(B+V+S)/\sqrt3,\quad u_V=(B-2V+S)/\sqrt6\rangle.
\]

## Entry chamber

| operator_id   |   null_point | operator_kind   | entry_chamber   |   entry_count |   energy_fraction_in_C |      mean |       rms |
|:--------------|-------------:|:----------------|:----------------|--------------:|-----------------------:|----------:|----------:|
| R_full        |          011 | normalized      | BS_core_2x2     |             4 |            0.992693    | 195231    | 195231    |
| R_full        |          011 | normalized      | B_S_diag_only   |             2 |            0.496346    | 195231    | 195231    |
| R_full        |          011 | normalized      | B_S_cross_only  |             2 |            0.496346    | 195231    | 195231    |
| R_full        |          011 | normalized      | V_row_to_BS     |             2 |            0.00682362  | -22890.9  |  22890.9  |
| R_full        |          011 | normalized      | BS_to_V_col     |             2 |            0.000478324 |  -6060.62 |   6060.62 |
| R_full        |          011 | normalized      | V_self          |             1 |            5.20804e-06 |    894.35 |    894.35 |

The raw quotient matrix is dominated by the `B,S` two-by-two block.  In entry energy, the `B/S` core carries almost all of the descended quotient.

## Rank-4 e-lock tail

| operator_id      |   null_point |   fit_energy_fraction |   WD6_scalar_energy_fraction |   pair_diag_contrast_energy_fraction |   pair_offdiag_chamber_energy_fraction |   orthogonal_pair_chamber_energy_fraction |   orthogonal_residual_not_pair_or_WD6 | top_quotient_component   |   top_quotient_energy_fraction_in_C |
|:-----------------|-------------:|----------------------:|-----------------------------:|-------------------------------------:|---------------------------------------:|------------------------------------------:|--------------------------------------:|:-------------------------|------------------------------------:|
| rank3_cumulative |          011 |             0.282741  |                     0.16339  |                             0.329091 |                               0.501495 |                                  0.830586 |                            0.00602478 | u0_scalar→u0_scalar      |                            0.38317  |
| rank3_cumulative |          010 |             0.282741  |                     0.16339  |                             0.329091 |                               0.501495 |                                  0.830586 |                            0.00602478 | u0_scalar→u0_scalar      |                            0.38317  |
| rank4_cumulative |          011 |             0.286103  |                     0.163838 |                             0.325938 |                               0.501162 |                                  0.827099 |                            0.00906273 | u0_scalar→u0_scalar      |                            0.368996 |
| rank4_cumulative |          010 |             0.286103  |                     0.163838 |                             0.325938 |                               0.501162 |                                  0.827099 |                            0.00906273 | u0_scalar→u0_scalar      |                            0.368996 |
| mode4_increment  |          011 |             0.0380289 |                     0.163882 |                             0.315888 |                               0.499497 |                                  0.815385 |                            0.0207332  | u0_scalar→u0_scalar      |                            0.333167 |
| mode4_increment  |          010 |             0.0380289 |                     0.163882 |                             0.315888 |                               0.499497 |                                  0.815385 |                            0.0207332  | u0_scalar→u0_scalar      |                            0.333167 |

The rank-4 e-lock tail does not introduce a new six-edge curl chamber.  It enters the same scalar/V-contrast quotient plane.

## Singular mode chamber typing

|   original_Romega_mode |   mode_singular_value |   null_point |   fit_energy_fraction |   WD6_scalar_energy_fraction |   pair_diag_contrast_energy_fraction |   pair_offdiag_chamber_energy_fraction |   orthogonal_pair_chamber_energy_fraction |   orthogonal_residual_not_pair_or_WD6 |   pair_chamber_share_of_WD6_breaking | top_quotient_left_basis   | top_quotient_right_basis   |   top_quotient_energy_fraction_in_C |
|-----------------------:|----------------------:|-------------:|----------------------:|-----------------------------:|-------------------------------------:|---------------------------------------:|------------------------------------------:|--------------------------------------:|-------------------------------------:|:--------------------------|:---------------------------|------------------------------------:|
|                      1 |              1659.57  |          011 |           0.365203    |                  4.16503e-05 |                           0.00378797 |                               0.469549 |                                  0.473337 |                           0.526621    |                             0.473357 | uV_BS_vs_V                | u0_scalar                  |                            0.356082 |
|                      2 |              1395.9   |          010 |           0.188158    |                  0.165581    |                           0.329492   |                               0.499347 |                                  0.828838 |                           0.00558081  |                             0.993312 | u0_scalar                 | u0_scalar                  |                            0.484027 |
|                      3 |               515.473 |          011 |           0.109828    |                  0.0667232   |                           0.207382   |                               0.481458 |                                  0.68884  |                           0.244437    |                             0.738087 | u0_scalar                 | uV_BS_vs_V                 |                            0.644719 |
|                      4 |               198.304 |          010 |           0.0380289   |                  0.163882    |                           0.315888   |                               0.499497 |                                  0.815385 |                           0.0207332   |                             0.975203 | u0_scalar                 | u0_scalar                  |                            0.333167 |
|                      5 |               150.906 |          100 |           0.102427    |                  0.16649     |                           0.00107521 |                               0.143465 |                                  0.14454  |                           0.68897     |                             0.173411 | u0_scalar                 | u0_scalar                  |                            0.998193 |
|                      6 |               130.259 |          001 |           0.000583068 |                  0.14118     |                           0.162883   |                               0.695938 |                                  0.85882  |                           2.22045e-16 |                             1        | uV_BS_vs_V                | uV_BS_vs_V                 |                            0.845513 |

## Files

- `Romega_chamber_source_summary.csv`
- `Romega_orthogonal_chamber_basis_components.csv`
- `Romega_pair3_quotient_basis_components.csv`
- `Romega_pair3_entry_chamber_energy.csv`
- `rank_truncation_chamber_source.csv`
- `singular_mode_chamber_source.csv`
- `rank4_elock_tail_chamber_source.csv`
- `A6_best_normalized_full_operator.csv`
- `pair3_best_normalized_quotient_matrix.csv`