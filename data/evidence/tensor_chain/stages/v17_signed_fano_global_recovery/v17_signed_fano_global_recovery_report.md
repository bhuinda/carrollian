# v17 — signed-Fano global action recovery test

## Question

Can the current v8/v16 data certify the `(B+S)/V` chamber as the global signed-Fano payoff mechanism by recovering a signed-Fano action on the 16 builder and 16 jabber labels?

## Result

```text
global_signed_fano_action_certified = false
six_channel_mechanism_status       = certified inside quotient shadow
global_mechanism_status            = not certified
blocking obstruction               = missing label-level signed-Fano resolution
```

## What was tested

For each of the 168 elements of `GL(3,2) = Aut(F7)`, I transported the available Fano point distributions of the 16 builder and 16 jabber labels. Since v8 only gives the three zones

```text
P1_point, L3_minus_P1, F7_minus_L3
```

I used the strongest possible reconstruction from v8 alone: split each zone uniformly over its Fano points, then solve the optimal assignment back to the 16 labels by Hungarian matching. If a genuine 16-label signed-Fano action were already encoded in v8, this transport-and-match test would recover low-cost permutations beyond the incident flag stabilizer.

## Automorphism recovery

| class                     |   count |   joint_cost_mean |   joint_cost_min |   joint_cost_max |   R_equiv_err_mean |   R_equiv_err_min |   R_equiv_err_max |   F_equiv_err_mean |   exact_recoverable |
|:--------------------------|--------:|------------------:|-----------------:|-----------------:|-------------------:|------------------:|------------------:|-------------------:|--------------------:|
| flag_stabilizer           |       8 |         0         |        0         |        0         |            0       |          0        |           0       |          0         |                   8 |
| moves_null_point          |     144 |         1.32312   |        1.29584   |        1.335     |            1.11035 |          0.816864 |           1.28495 |          0.0183287 |                   0 |
| point_stabilizer_not_flag |      16 |         0.0525716 |        0.0525716 |        0.0525716 |            0       |          0        |           0       |          0         |                   0 |

Exactly recoverable automorphisms: `8`.

Those are precisely the automorphisms visible to the coarse incident-flag zoning. The point-stabilizer `S4` and the signed `D6` data are not recoverable from the current 16-label features.

## Recovered-action composition defects

| group             |   pair_tests |   builder_composition_defect_mean |   builder_composition_defect_max |   jabber_composition_defect_mean |   jabber_composition_defect_max |
|:------------------|-------------:|----------------------------------:|---------------------------------:|---------------------------------:|--------------------------------:|
| all_GL3F2         |        28224 |                          0.488095 |                             0.75 |                         0.546769 |                          0.8125 |
| exact_recoverable |           64 |                          0        |                             0    |                         0        |                          0      |
| point_stabilizer  |          576 |                          0        |                             0    |                         0        |                          0      |
| flag_stabilizer   |           64 |                          0        |                             0    |                         0        |                          0      |

The exact recoverable subgroup composes, but it is only the coarse flag-level action. The larger attempted actions have nontrivial assignment/composition defects because the label data do not resolve full Fano points, let alone signs.

## Projection under attempted recovered actions

| group             |   size |   projection_energy_fraction_vs_R |   breaking_energy_fraction_vs_R |   projection_cos2_with_R |   projection_participation_rank |   breaking_participation_rank |   projection_relerr_to_R |
|:------------------|-------:|----------------------------------:|--------------------------------:|-------------------------:|--------------------------------:|------------------------------:|-------------------------:|
| exact_recoverable |      8 |                          1        |                     1.36266e-32 |                 1        |                         3.84256 |                       9.01799 |              1.16733e-16 |
| flag_stabilizer   |      8 |                          1        |                     1.36266e-32 |                 1        |                         3.84256 |                       9.01799 |              1.16733e-16 |
| point_stabilizer  |     24 |                          1        |                     1.51345e-31 |                 1        |                         3.84256 |                       7.88325 |              3.8903e-16  |
| all_GL3F2         |    168 |                          0.577726 |                     0.653542    |                 0.369602 |                         3.65502 |                       4.04252 |              0.80842     |

Averaging under the larger attempted actions is not a certified symmetry projection, because those actions are reconstructed with nonzero assignment cost. It is included only as a diagnostic of what would happen under the best available coarse reconstruction.

## Resolution loss

- builder point-distribution rank: `3`
- jabber point-distribution rank: `3`
- available Fano resolution: `3`
- full point resolution required: `7`
- signed-D6 observable from current data: `False`

## Verdict

The v16 six-channel result still stands: `(B+S)/V` is a real mechanism inside the Fano-nullified `6j` quotient shadow. But the current bundle cannot certify it as the full 16×16 signed-Fano payoff mechanism, because the available label data are only incident-flag zone aggregates.

The missing object is now precise: a point- and sign-resolved action of the signed-Fano/D6 generators on the 16 builder labels and the 16 jabber labels.

## Files

- `GL3F2_fano_automorphism_classes.csv`
- `fano_label_action_recovery_all_GL3F2.csv`
- `fano_action_recovery_summary_by_class.csv`
- `exactly_recoverable_zone_action_subgroup.csv`
- `recovered_label_action_composition_defects.csv`
- `Romega_recovered_action_projection_summary.csv`
- `fano_resolution_loss_diagnostic.json`
- `required_data_for_global_signed_fano_certification.schema.json`