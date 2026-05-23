# v20: all four lifts for the R_Ω chamber mechanism

## Main result

All four requested directions were executed. The strongest certified result is:

\[ R_\Omega^{(6)} \text{ is an } A_{42}/\mathrm{Pin}\text{-level chamber-selection operator whose } A_{12}\text{ shadow is }(B+S)/V. \]

The chamber lifts functorially to foam by:

\[ P_{16}=\operatorname{diag}(1,\Lambda^2P_{(B+S)/V}). \]

The canonical 16-label foam module is the natural basis \(1\oplus\Lambda^2H_6\). It is projective for signed-Fano: the central all-sign flip is invisible on \(\Lambda^2H_6\), so the effective foam action has order \(384\), while the exact six-channel signed action has order \(768\).

## 1. Foam-projector lift

| operator                                     | shape   |   projector_rank |   energy_inside_projector |   energy_outside_projector |   relative_error_projected_to_original |   projected_participation_rank |   original_participation_rank |   cos2_projected_with_original |   functorial_relative_error_to_direct_lift |   direct_lift_energy_vs_compound |
|:---------------------------------------------|:--------|-----------------:|--------------------------:|---------------------------:|---------------------------------------:|-------------------------------:|------------------------------:|-------------------------------:|-------------------------------------------:|---------------------------------:|
| label_embedding_Rfoam16                      | 16x16   |                2 |                 0.0138591 |                   0.986141 |                               0.993046 |                        1.94947 |                       1.9319  |                      0.0138591 |                              nan           |                      nan         |
| compound_lift_Foam16_from_A6                 | 16x16   |                2 |                 0.0300932 |                   0.969907 |                               0.984838 |                        1.00091 |                       1.51814 |                      0.0300932 |                              nan           |                      nan         |
| functorial_check_P16_liftA_P16_vs_lift_P6AP6 | 16x16   |                2 |                 0.0300932 |                   0.969907 |                               0.984838 |                        1.00091 |                       1.51814 |                      0.0300932 |                                1.86166e-07 |                        0.0300932 |

## 2. Canonical 16-label foam module

| diagnostic                                       |   value |
|:-------------------------------------------------|--------:|
| basis_rank                                       |      16 |
| signed_fano_group_order_on_H6                    |     768 |
| distinct_projective_actions_on_Foam16            |     384 |
| central_kernel_size_on_Foam16                    |       2 |
| full_WD6_group_order                             |   23040 |
| all_signed_fano_G_orthogonal                     |    True |
| all_signed_fano_G_signed_monomial                |    True |
| current_builder_embedding_rank                   |       5 |
| current_jabber_embedding_rank                    |       5 |
| closure_generated_by_listed_generators_on_Foam16 |     384 |

## 3. Internal A985 chamber derivation proxy

Using the available `d20.json` object-pair shadow of `A985`, the `B/V/S` quotient already favors the same active plane. This is not the full raw-tensor proof, because the package does not contain the raw `1,414,965` tensor triples.

| matrix                                  | diagnostic                         |     value |
|:----------------------------------------|:-----------------------------------|----------:|
| A985_object_pair_pair3_raw              | active_BplusS_vs_V_energy_fraction | 0.83144   |
| A985_object_pair_pair3_raw              | excluded_BminusS_energy_fraction   | 0.16856   |
| A985_object_pair_pair3_raw              | active_relative_error              | 0.410561  |
| A985_object_pair_pair3_raw              | participation_rank                 | 1.5224    |
| A985_object_pair_pair3_raw              | active_participation_rank          | 1.37462   |
| A985_object_pair_pair3_orbit_normalized | active_BplusS_vs_V_energy_fraction | 0.957294  |
| A985_object_pair_pair3_orbit_normalized | excluded_BminusS_energy_fraction   | 0.0427065 |
| A985_object_pair_pair3_orbit_normalized | active_relative_error              | 0.206655  |
| A985_object_pair_pair3_orbit_normalized | participation_rank                 | 1.64812   |
| A985_object_pair_pair3_orbit_normalized | active_participation_rank          | 1.4252    |

## 4. Quotient-tower typing

| level                                    |   dimension |   active_chamber_energy |   non_chamber_energy |   relative_error_after_chamber_projection |   participation_rank |   active_participation_rank |
|:-----------------------------------------|------------:|------------------------:|---------------------:|------------------------------------------:|---------------------:|----------------------------:|
| A42_or_signed_edge_A6                    |           6 |               0.993553  |          0.00644736  |                               0.0802955   |              1.00659 |                     1.00093 |
| A12_pair3_from_A6_QAQ                    |           3 |               1         |          1.71431e-29 |                               4.14042e-15 |              1.00093 |                     1.00093 |
| A12_pair3_v15                            |           3 |               1         |          1.76063e-29 |                               4.19599e-15 |              1.00093 |                     1.00093 |
| A985_object_pair_shadow_pair3            |           3 |               0.83144   |          0.16856     |                               0.410561    |              1.5224  |                     1.37462 |
| A985_object_pair_shadow_pair3_normalized |           3 |               0.957294  |          0.0427065   |                               0.206655    |              1.64812 |                     1.4252  |
| Foam16_compound_lift                     |          16 |               0.0300932 |          0.969907    |                               0.984838    |              1.51814 |                     1.00091 |
| Foam16_label_embedding_Rfoam             |          16 |               0.0138591 |          0.986141    |                               0.993046    |              1.9319  |                     1.94947 |

## Intertwining checks

| map               | identity                        |   relative_error |   rank_P16 |   idempotence_error |
|:------------------|:--------------------------------|-----------------:|-----------:|--------------------:|
| Q:H6_to_A12_pair3 | Q P6 = P3 Q                     |      1.9439e-16  |        nan |                 nan |
| Lambda2 functor   | P16 = 1 + Lambda2(P6)           |    nan           |          2 |                   0 |
| A6 quotient       | Q(P6 A6 P6)Q^T = P3(Q A6 Q^T)P3 |      3.03649e-16 |        nan |                 nan |

## Verdict

- The foam projector is constructed and functorial.

- The canonical 16-label foam module is constructed on `1 + Lambda^2 H6`; it is faithful after quotienting the central all-sign flip, giving an effective projective action of order 384.

- The current labels remain rank-5 shadows, so they are not the faithful module.

- The available A985 object-pair quotient shadow supports the same `(B+S)/V` chamber.

- The strict raw `T985` theorem remains a proof obligation until the raw tensor triples are in the package.

- The tower type is: `A42/Pin chamber selector -> A12 (B+S)/V shadow -> Foam16 functorial lift`.
