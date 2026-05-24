# external_evidence_gate — mechanism vs defect test for `R_Omega`

## Question

Does the `(B+S)/V` chamber behave like a random `W(D6)` defect, or like the mechanism that organizes the Fano-nullified `6j` shadow?

## Short answer

It is testable, and the result is split:

- **inside the six-channel Fano/6j contraction:** mechanism test passes; random-defect reading fails;
- **for the full 16×16 `R_Omega` e-lock:** not certified from the current source_drop Fano resolution.

## Six-channel component ablation

| component            |   frobenius_norm |   energy_fraction_of_A6 |   energy_fraction_of_WD6_breaking |   participation_rank |   WD6_scalar_energy_fraction_internal |   pair_chamber_energy_fraction_internal |   nonpair_residual_energy_fraction_internal |
|:---------------------|-----------------:|------------------------:|----------------------------------:|---------------------:|--------------------------------------:|----------------------------------------:|--------------------------------------------:|
| scalar               |         319671   |              0.165271   |                         0.197994  |              6       |                           1           |                             9.1695e-32  |                                 0           |
| chamber              |         715698   |              0.828417   |                         0.992438  |              3.32705 |                           3.34329e-08 |                             1           |                                 1.11022e-16 |
| nonpair              |          63138.8 |              0.00644736 |                         0.0077239 |              1.51748 |                           4.29576e-06 |                             4.29576e-06 |                                 0.999991    |
| Wbreak               |         718419   |              0.834729   |                         1         |              3.31983 |                           9.23139e-34 |                             0.992276    |                                 0.00772384  |
| scalar_plus_chamber  |         783792   |              0.993553   |                         1.19027   |              1.00093 |                           0.166208    |                             0.833792    |                                 1.11022e-16 |
| scalar_plus_nonpair  |         325976   |              0.171854   |                         0.20588   |              5.82897 |                           0.962484    |                             1.61162e-07 |                                 0.0375162   |
| chamber_plus_nonpair |         718419   |              0.834729   |                         1         |              3.31983 |                           9.23139e-34 |                             0.992276    |                                 0.00772384  |

The chamber component carries nearly all of the `W(D6)`-breaking part of the six-channel operator. Removing it leaves the scalar plus tiny non-pair remainder; keeping it retains the organized breaking.

## Random defect controls

- trials: `5000`
- observed pair-chamber share of `W(D6)` breaking: `0.992276`
- random-control mean: `0.256599`
- random-control max: `0.673790`
- observed percentile: `1.000000`

So the observed chamber is at the extreme top of the sampled random `W(D6)`-breaking controls. That rejects the simple defect/noise reading for the six-channel operator.

## Global e-lock ablation

| operator             |   energy_fraction_vs_R |   cos2_with_R |   participation_rank_operator |   participation_rank_flag_plus_operator_alpha1 | e_reachable   |   first_root |   closest_alpha |   closest_pr |   closest_gap |   max_pr |   alpha_at_max_pr |
|:---------------------|-----------------------:|--------------:|------------------------------:|-----------------------------------------------:|:--------------|-------------:|----------------:|-------------:|--------------:|---------:|------------------:|
| scalar               |          758460        |   1.15255e-06 |                       1.0041  |                                        1.00404 | False         |    nan       |            0    |      1.16063 |    1.55765    |  1.16063 |              0    |
| pair3                |              34.1783   |   0.00167351  |                       1.00538 |                                        1.02337 | False         |    nan       |           -0.2  |      1.93935 |    0.778933   |  1.93935 |             -0.2  |
| chamber              |          748480        |   1.84183e-06 |                       1.00421 |                                        1.00434 | False         |    nan       |            0    |      1.16063 |    1.55765    |  1.16063 |              0    |
| nonpair              |              33.9825   |   5.53078e-05 |                       1.0138  |                                        1.04038 | False         |    nan       |            0.2  |      2.26109 |    0.457189   |  2.26109 |              0.2  |
| scalar_plus_chamber  |              34.1783   |   0.00167351  |                       1.00538 |                                        1.02337 | False         |    nan       |           -0.2  |      1.93935 |    0.778933   |  1.93935 |             -0.2  |
| scalar_plus_nonpair  |          748478        |   1.06212e-06 |                       1.00408 |                                        1.00402 | False         |    nan       |            0    |      1.16063 |    1.55765    |  1.16063 |              0    |
| chamber_plus_nonpair |          758462        |   1.95429e-06 |                       1.00422 |                                        1.00435 | False         |    nan       |            0    |      1.16063 |    1.55765    |  1.16063 |              0    |
| six_hat              |               0.282513 |   0.282513    |                       2.07752 |                                        1.1056  | False         |    nan       |          -20    |      2.08657 |    0.631715   |  2.08657 |            -20    |
| full_R               |               1        |   1           |                       3.84256 |                                        2.59035 | True          |     -1.20479 |           -1.2  |      2.71392 |    0.00436465 |  3.8445  |             39.74 |
| R_minus_six_hat      |               0.717487 |   0.717487    |                       4.09901 |                                        2.53303 | True          |     -1.06899 |            1.16 |      2.71088 |    0.00740195 |  4.10484 |            -20    |
| R_minus_chamber_hat  |          748479        |   4.05091e-08 |                       1.00562 |                                        1.00553 | False         |    nan       |            0    |      1.16063 |    1.55765    |  1.16063 |              0    |

The six-channel shadow itself is not sufficient to reproduce the full e-rank lock. The full residual reaches the e-lock, but the six-channel reconstruction does not. The complement `R - R_6j` still has enough structure to reach the e-lock.

## Lift conditioning diagnostic

- B rank: `3`, condition number: `None`
- J rank: `3`, condition number: `None`

The separate lifted scalar/chamber/non-pair components are therefore not stable enough to treat as independent global 16×16 mechanisms. They are reliable as a six-channel quotient decomposition, not as standalone full-space operators.

## Verdict

```text
six_channel_mechanism_test: PASS
six_channel_reason: The pair chamber accounts for essentially all WD6-breaking energy and beats random WD6-breaking controls at the top of the sampled distribution.
global_elock_mechanism_test: NOT_CERTIFIED
global_reason: The current six-channel Fano/6j contraction captures only about 28.25% of full R_Omega energy; the lifted component split is numerically ill-conditioned, and the six-channel shadow alone does not reach the full e-rank lock.
defect_reading_status: Rejected for six-channel shadow; not decidable for full R_Omega with current source_drop-resolved Fano data.
mechanism_reading_status: Certified inside the Fano-nullified 6j quotient; not yet certified as the global payoff/e-lock mechanism.
```

## Files

- `A6_mechanism_component_ablation.csv`
- `random_WD6_breaking_defect_controls.csv`
- `random_WD6_breaking_defect_control_summary.json`
- `global_elock_sufficiency_ablation.csv`
- `lift_conditioning_diagnostic.json`