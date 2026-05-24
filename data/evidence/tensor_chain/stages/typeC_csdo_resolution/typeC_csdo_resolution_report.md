# source_drop: Type-C / CSDO resolution of the Lambda^2 foam-energy drop

## Main result

The cadical_frat_surface_lrat_verified anomaly is explained by the Type-C cluster-shadow layer. The chamber is not meant to be energy-preserving under the full `1 + Lambda^2 H6` foam lift. It is a signed tropical / CSDO face resolved at `A42` and folded by `A12`.

The computed verdict is:

\[\boxed{\Lambda^2\text{ embeds the chamber into a larger Spin/D6 foam envelope, where it becomes a proper face rather than the whole support.}}\]

## Input Type-C construction

- Cluster-shadow status: `A985_CLUSTER_SHADOW_CONSTRUCTED_PASS`.

- Certificate SHA-256: `3ba139c038f2c3cc02c612b090af7f85be894c65d60116066f683ff1804d7f55`.

- The construction gives four CSDO sign chambers at `A42`; all collapse to the same repeated `A12` image.


## CSDO chamber coordinate map

|   class_id | std_coordinate   | d20_coordinate   | foam_basis_coordinate   |   orientation_to_foam_basis | sign_pm   |   sign_numeric |   signed_basis_coefficient | negative_coordinates_d20   | A12_image            |
|-----------:|:-----------------|:-----------------|:------------------------|----------------------------:|:----------|---------------:|---------------------------:|:---------------------------|:---------------------|
|          1 | y_1,3            | y_{B-,S-}        | B-∧S-                   |                           1 | -         |             -1 |                         -1 | y_{B-,S-}                  | [7, 11, 8, 7, 11, 8] |
|          1 | y_1,1b           | y_{B-,B+}        | B-∧B+                   |                           1 | +         |              1 |                          1 | y_{B-,S-}                  | [7, 11, 8, 7, 11, 8] |
|          1 | y_1,2b           | y_{B-,V+}        | B-∧V+                   |                           1 | +         |              1 |                          1 | y_{B-,S-}                  | [7, 11, 8, 7, 11, 8] |
|          1 | y_2,2b           | y_{V-,V+}        | V-∧V+                   |                           1 | +         |              1 |                          1 | y_{B-,S-}                  | [7, 11, 8, 7, 11, 8] |
|          1 | y_2,3b           | y_{V-,S+}        | V-∧S+                   |                           1 | +         |              1 |                          1 | y_{B-,S-}                  | [7, 11, 8, 7, 11, 8] |
|          1 | y_3,3b           | y_{S-,S+}        | S-∧S+                   |                           1 | +         |              1 |                          1 | y_{B-,S-}                  | [7, 11, 8, 7, 11, 8] |
|          2 | y_1,3            | y_{B-,S-}        | B-∧S-                   |                           1 | +         |              1 |                          1 | y_{V-,S+}                  | [7, 11, 8, 7, 11, 8] |
|          2 | y_1,1b           | y_{B-,B+}        | B-∧B+                   |                           1 | +         |              1 |                          1 | y_{V-,S+}                  | [7, 11, 8, 7, 11, 8] |
|          2 | y_1,2b           | y_{B-,V+}        | B-∧V+                   |                           1 | +         |              1 |                          1 | y_{V-,S+}                  | [7, 11, 8, 7, 11, 8] |
|          2 | y_2,2b           | y_{V-,V+}        | V-∧V+                   |                           1 | +         |              1 |                          1 | y_{V-,S+}                  | [7, 11, 8, 7, 11, 8] |
|          2 | y_2,3b           | y_{V-,S+}        | V-∧S+                   |                           1 | -         |             -1 |                         -1 | y_{V-,S+}                  | [7, 11, 8, 7, 11, 8] |
|          2 | y_3,3b           | y_{S-,S+}        | S-∧S+                   |                           1 | +         |              1 |                          1 | y_{V-,S+}                  | [7, 11, 8, 7, 11, 8] |
|          3 | y_1,3            | y_{B-,S-}        | B-∧S-                   |                           1 | +         |              1 |                          1 | y_{B-,V+}                  | [7, 11, 8, 7, 11, 8] |
|          3 | y_1,1b           | y_{B-,B+}        | B-∧B+                   |                           1 | +         |              1 |                          1 | y_{B-,V+}                  | [7, 11, 8, 7, 11, 8] |
|          3 | y_1,2b           | y_{B-,V+}        | B-∧V+                   |                           1 | -         |             -1 |                         -1 | y_{B-,V+}                  | [7, 11, 8, 7, 11, 8] |
|          3 | y_2,2b           | y_{V-,V+}        | V-∧V+                   |                           1 | +         |              1 |                          1 | y_{B-,V+}                  | [7, 11, 8, 7, 11, 8] |
|          3 | y_2,3b           | y_{V-,S+}        | V-∧S+                   |                           1 | +         |              1 |                          1 | y_{B-,V+}                  | [7, 11, 8, 7, 11, 8] |
|          3 | y_3,3b           | y_{S-,S+}        | S-∧S+                   |                           1 | +         |              1 |                          1 | y_{B-,V+}                  | [7, 11, 8, 7, 11, 8] |
|          4 | y_1,3            | y_{B-,S-}        | B-∧S-                   |                           1 | +         |              1 |                          1 |                            | [7, 11, 8, 7, 11, 8] |
|          4 | y_1,1b           | y_{B-,B+}        | B-∧B+                   |                           1 | +         |              1 |                          1 |                            | [7, 11, 8, 7, 11, 8] |
|          4 | y_1,2b           | y_{B-,V+}        | B-∧V+                   |                           1 | +         |              1 |                          1 |                            | [7, 11, 8, 7, 11, 8] |
|          4 | y_2,2b           | y_{V-,V+}        | V-∧V+                   |                           1 | +         |              1 |                          1 |                            | [7, 11, 8, 7, 11, 8] |
|          4 | y_2,3b           | y_{V-,S+}        | V-∧S+                   |                           1 | +         |              1 |                          1 |                            | [7, 11, 8, 7, 11, 8] |
|          4 | y_3,3b           | y_{S-,S+}        | S-∧S+                   |                           1 | +         |              1 |                          1 |                            | [7, 11, 8, 7, 11, 8] |

## CSDO A42 to A12 collapse

|   class_id | sign_vector_pm   | negative_coordinates_d20   | A12_image            | A12_period_three   |
|-----------:|:-----------------|:---------------------------|:---------------------|:-------------------|
|          1 | -+++++           | y_{B-,S-}                  | [7, 11, 8, 7, 11, 8] | True               |
|          2 | ++++-+           | y_{V-,S+}                  | [7, 11, 8, 7, 11, 8] | True               |
|          3 | ++-+++           | y_{B-,V+}                  | [7, 11, 8, 7, 11, 8] | True               |
|          4 | ++++++           | (none)                     | [7, 11, 8, 7, 11, 8] | True               |

## Projection-energy summary

| matrix                  | projector                      |   projector_rank_int |   two_sided_energy_fraction |   one_sided_left_energy_fraction |   one_sided_right_energy_fraction |   relative_error_two_sided_projection |   projected_participation_rank |
|:------------------------|:-------------------------------|---------------------:|----------------------------:|---------------------------------:|----------------------------------:|--------------------------------------:|-------------------------------:|
| compound_Foam16_from_A6 | active_chamber_P16_rank2       |                    2 |                 0.0300932   |                         0.560221 |                          0.246615 |                              0.984838 |                        1.00091 |
| compound_Foam16_from_A6 | pair_P16_rank?                 |                    4 |                 0.0300932   |                         0.560221 |                          0.246615 |                              0.984838 |                        1.00091 |
| compound_Foam16_from_A6 | CSDO_support_unit_plus_6coords |                    7 |                 0.0628268   |                         0.2507   |                          0.250606 |                              0.968077 |                        1.53148 |
| compound_Foam16_from_A6 | CSDO_signspan_unit_plus_4signs |                    5 |                 0.0625363   |                         0.250078 |                          0.250067 |                              0.968227 |                        1.52017 |
| compound_Foam16_from_A6 | CSDO_support_wedge_only        |                    6 |                 0.0628268   |                         0.2507   |                          0.250606 |                              0.968077 |                        1.5307  |
| compound_Foam16_from_A6 | CSDO_signspan_wedge_only       |                    4 |                 0.0625363   |                         0.250078 |                          0.250067 |                              0.968227 |                        1.51939 |
| label_embedding_Rfoam16 | active_chamber_P16_rank2       |                    2 |                 0.0138591   |                         0.323808 |                          0.689955 |                              0.993046 |                        1.94947 |
| label_embedding_Rfoam16 | pair_P16_rank?                 |                    4 |                 0.064693    |                         0.349732 |                          0.714933 |                              0.967113 |                        1.98964 |
| label_embedding_Rfoam16 | CSDO_support_unit_plus_6coords |                    7 |                 0.955675    |                         0.976788 |                          0.978887 |                              0.210535 |                        1.92476 |
| label_embedding_Rfoam16 | CSDO_signspan_unit_plus_4signs |                    5 |                 0.353086    |                         0.555281 |                          0.797765 |                              0.804309 |                        1.93555 |
| label_embedding_Rfoam16 | CSDO_support_wedge_only        |                    6 |                 5.45829e-05 |                         0.659996 |                          0.29511  |                              0.999973 |                        1.29391 |
| label_embedding_Rfoam16 | CSDO_signspan_wedge_only       |                    4 |                 1.67607e-05 |                         0.238489 |                          0.113988 |                              0.999992 |                        1.32002 |

## Layer explanation

| layer                                  |   support_dimension | projector                              |   projector_rank |   energy_fraction | interpretation                                                            |
|:---------------------------------------|--------------------:|:---------------------------------------|-----------------:|------------------:|:--------------------------------------------------------------------------|
| A6 signed-edge / A42-style six-channel |                   6 | (B+S)/V active two-plane               |                2 |         0.993553  | dominant six-channel mechanism                                            |
| A12 pair quotient                      |                   3 | same active plane after B/V/S quotient |                2 |         1         | CSDO sign differences folded to terminal A12 image                        |
| Foam16 active chamber                  |                  16 | unit + Lambda^2(active two-plane)      |                2 |         0.0300932 | active six-channel chamber becomes a low-rank foam face                   |
| Foam16 CSDO support                    |                  16 | unit + six CSDO tropical coordinates   |                7 |         0.0628268 | type-C CSDO face: larger than active chamber but still a proper foam face |
| Foam16 CSDO signspan                   |                  16 | unit + span of four CSDO sign vectors  |                5 |         0.0625363 | signspan captures nearly all CSDO support energy                          |

## Key numeric conclusion

- Six-channel/A42 active chamber energy: `0.993552637`.

- A12 folded active energy: `1.000000000`.

- Foam16 active chamber energy: `0.030093243`.

- Foam16 CSDO support energy: `0.062826778`.

- Foam16 CSDO signspan energy: `0.062536298`.

- CSDO signspan / CSDO support ratio: `0.995376497`.


## Interpretation

The Type-C/CSDO sign data is an `A42`-resolved signed tropical chamber system. `A12` folds the four sign chambers to one terminal image, so the chamber looks total downstairs. The `Lambda^2` foam chart is a bigger Spin/D6 envelope. In that envelope the CSDO chamber is a face; its signspan accounts for almost all of the CSDO support energy, but the CSDO face itself is a small closed two-sided suboperator of the whole foam lift.

Thus the cadical_frat_surface_lrat_verified low foam energy is not a failure of the chamber. It is the expected result of moving from a folded Type-C tropical quotient to the full foam envelope.

## Remaining proof obligation

The raw `T985` tensor proof remains open until the raw structure-constant triples are present. This source_drop result is certified at the Type-C shadow / CSDO / Foam16 projection level.
