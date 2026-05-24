# source_drop: Direct T985 -> CSDO -> A42 -> A12 -> Foam16 chain test

## Result

The direct chain is certified at the decategorified `T985` metadata / object-pair shadow level. The full raw tensor theorem is still blocked because the actual `[alpha,beta,gamma,p]` triples and `q42(alpha)` map are not present in the current files.

\[\boxed{T_{985}^{\mathrm{metadata}}\to M_6\to\mathrm{CSDO}\to A_{42}\to A_{12}\to\mathrm{Foam}_{16}	ext{ passes as a shadow chain.}}\]

\[\boxed{T_{985}	ext{ raw structure-constant theorem is not yet certified.}}\]

## Raw tensor availability

| tensor_triples_shape   | tensor_triples_sha256                                            |   tensor_support |   tensor_coefficient_total | actual_tensor_triples_file_present   | candidate_tensor_like_files                                                                                                                                                                                                                                                                                                                  | relation_to_A42_map_present   | A42_to_A12_map_present   |
|:-----------------------|:-----------------------------------------------------------------|-----------------:|---------------------------:|:-------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------|:-------------------------|
| [1414965, 4]           | f1ee8d848884bb9952e0412977ae37ca1bdf86ee26c60a871c5ec7b3b97367a6 |          1414965 |                    2537360 | False                                | ['/mnt/data/g_Romega_raw_tensor_chain_test/all_four_lifts/raw_T985_chamber_proof_obligation.schema.json', '/mnt/data/g_Romega_typeC_csdo_resolution/all_four_lifts/raw_T985_chamber_proof_obligation.schema.json', '/mnt/data/g_Romega_all_four_lifts/all_four_lifts/raw_T985_chamber_proof_obligation.schema.json'] | False                         | True                     |

## Direct chain ladder

| stage               | object                                       | available                     | status                      | key_value                                                          |
|:--------------------|:---------------------------------------------|:------------------------------|:----------------------------|:-------------------------------------------------------------------|
| T985 metadata       | raw structure-constant tensor                | hash/shape/support/total only | metadata-certified          | support=1414965; coefficient_total=2537360; sha256=f1ee8d848884... |
| T985 -> M6          | six-object Hom-dimension matrix e_i A985 e_j | yes in d20.json               | exact decategorified shadow | sum(M6)=985                                                        |
| M6 -> CSDO support  | six Type-C coordinates inside Lambda^2 H6    | yes                           | computed                    | energy=0.388927821                                                 |
| M6 -> CSDO signspan | span of four A42 sign chambers               | yes                           | computed                    | energy=0.341976174                                                 |
| A42 CSDO resolution | four signed tropical chambers                | yes from Type-C certificate   | passes                      | rank=4; chambers=4                                                 |
| A42 -> A12          | collapse of four CSDO sign chambers          | yes from Type-C certificate   | passes                      | unique_A12_images=1                                                |
| A12 -> Foam16       | CSDO face in 1+Lambda^2H6                    | yes from source_drop                  | computed                    | CSDO_support=0.062826778; signspan=0.062536298                     |
| Romega downstairs   | A6/A12 chamber dominance                     | yes from source_drop                  | passes                      | A6=0.993552637; A12=1.000000000                                    |

## Chain diagnostics

| source                   | map                                |   rank |   energy_fraction |   relative_error | comment                                                                    |
|:-------------------------|:-----------------------------------|-------:|------------------:|-----------------:|:---------------------------------------------------------------------------|
| relation_count_wedge15   | wedge15 -> CSDO_support_6coords    |      6 |          0.388928 |         0.781711 | energy of six Type-C CSDO coordinates inside full 15-edge D6 wedge carrier |
| relation_count_wedge15   | wedge15 -> CSDO_signspan_4chambers |      4 |          0.341976 |         0.811187 | projection onto span of the four A42 CSDO sign chambers                    |
| relation_count_wedge15   | CSDO_signspan / CSDO_support       |      4 |          0.879279 |       nan        | how much of the Type-C support is explained by the four sign chambers      |
| orbit_normalized_wedge15 | wedge15 -> CSDO_support_6coords    |      6 |          0.491873 |         0.71283  | energy of six Type-C CSDO coordinates inside full 15-edge D6 wedge carrier |
| orbit_normalized_wedge15 | wedge15 -> CSDO_signspan_4chambers |      4 |          0.47967  |         0.721339 | projection onto span of the four A42 CSDO sign chambers                    |
| orbit_normalized_wedge15 | CSDO_signspan / CSDO_support       |      4 |          0.975191 |       nan        | how much of the Type-C support is explained by the four sign chambers      |
| relation_count_pair3     | pair3 -> active_(B+S)/V_plane      |      2 |          0.83144  |         0.410561 | A985 object-pair shadow projected through B/V/S quotient                   |
| orbit_normalized_pair3   | pair3 -> active_(B+S)/V_plane      |      2 |          0.957294 |         0.206655 | A985 object-pair shadow projected through B/V/S quotient                   |
| coefficient_mass_pair3   | pair3 -> active_(B+S)/V_plane      |      2 |          0.810759 |         0.435018 | coefficient-mass shadow from certified level2 clopen boundary              |

## CSDO coordinate map

|   class_id | std_coordinate   | d20_coordinate   | wedge_coordinate   |   orientation_to_canonical_wedge | sign_pm   |   signed_coefficient | negative_coordinates_d20   | A12_image            |
|-----------:|:-----------------|:-----------------|:-------------------|---------------------------------:|:----------|---------------------:|:---------------------------|:---------------------|
|          1 | y_1,3            | y_{B-,S-}        | B-∧S-              |                                1 | -         |                   -1 | y_{B-,S-}                  | [7, 11, 8, 7, 11, 8] |
|          1 | y_1,1b           | y_{B-,B+}        | B-∧B+              |                                1 | +         |                    1 | y_{B-,S-}                  | [7, 11, 8, 7, 11, 8] |
|          1 | y_1,2b           | y_{B-,V+}        | B-∧V+              |                                1 | +         |                    1 | y_{B-,S-}                  | [7, 11, 8, 7, 11, 8] |
|          1 | y_2,2b           | y_{V-,V+}        | V-∧V+              |                                1 | +         |                    1 | y_{B-,S-}                  | [7, 11, 8, 7, 11, 8] |
|          1 | y_2,3b           | y_{V-,S+}        | V-∧S+              |                                1 | +         |                    1 | y_{B-,S-}                  | [7, 11, 8, 7, 11, 8] |
|          1 | y_3,3b           | y_{S-,S+}        | S-∧S+              |                                1 | +         |                    1 | y_{B-,S-}                  | [7, 11, 8, 7, 11, 8] |
|          2 | y_1,3            | y_{B-,S-}        | B-∧S-              |                                1 | +         |                    1 | y_{V-,S+}                  | [7, 11, 8, 7, 11, 8] |
|          2 | y_1,1b           | y_{B-,B+}        | B-∧B+              |                                1 | +         |                    1 | y_{V-,S+}                  | [7, 11, 8, 7, 11, 8] |
|          2 | y_1,2b           | y_{B-,V+}        | B-∧V+              |                                1 | +         |                    1 | y_{V-,S+}                  | [7, 11, 8, 7, 11, 8] |
|          2 | y_2,2b           | y_{V-,V+}        | V-∧V+              |                                1 | +         |                    1 | y_{V-,S+}                  | [7, 11, 8, 7, 11, 8] |
|          2 | y_2,3b           | y_{V-,S+}        | V-∧S+              |                                1 | -         |                   -1 | y_{V-,S+}                  | [7, 11, 8, 7, 11, 8] |
|          2 | y_3,3b           | y_{S-,S+}        | S-∧S+              |                                1 | +         |                    1 | y_{V-,S+}                  | [7, 11, 8, 7, 11, 8] |
|          3 | y_1,3            | y_{B-,S-}        | B-∧S-              |                                1 | +         |                    1 | y_{B-,V+}                  | [7, 11, 8, 7, 11, 8] |
|          3 | y_1,1b           | y_{B-,B+}        | B-∧B+              |                                1 | +         |                    1 | y_{B-,V+}                  | [7, 11, 8, 7, 11, 8] |
|          3 | y_1,2b           | y_{B-,V+}        | B-∧V+              |                                1 | -         |                   -1 | y_{B-,V+}                  | [7, 11, 8, 7, 11, 8] |
|          3 | y_2,2b           | y_{V-,V+}        | V-∧V+              |                                1 | +         |                    1 | y_{B-,V+}                  | [7, 11, 8, 7, 11, 8] |
|          3 | y_2,3b           | y_{V-,S+}        | V-∧S+              |                                1 | +         |                    1 | y_{B-,V+}                  | [7, 11, 8, 7, 11, 8] |
|          3 | y_3,3b           | y_{S-,S+}        | S-∧S+              |                                1 | +         |                    1 | y_{B-,V+}                  | [7, 11, 8, 7, 11, 8] |
|          4 | y_1,3            | y_{B-,S-}        | B-∧S-              |                                1 | +         |                    1 | (none)                     | [7, 11, 8, 7, 11, 8] |
|          4 | y_1,1b           | y_{B-,B+}        | B-∧B+              |                                1 | +         |                    1 | (none)                     | [7, 11, 8, 7, 11, 8] |
|          4 | y_1,2b           | y_{B-,V+}        | B-∧V+              |                                1 | +         |                    1 | (none)                     | [7, 11, 8, 7, 11, 8] |
|          4 | y_2,2b           | y_{V-,V+}        | V-∧V+              |                                1 | +         |                    1 | (none)                     | [7, 11, 8, 7, 11, 8] |
|          4 | y_2,3b           | y_{V-,S+}        | V-∧S+              |                                1 | +         |                    1 | (none)                     | [7, 11, 8, 7, 11, 8] |
|          4 | y_3,3b           | y_{S-,S+}        | S-∧S+              |                                1 | +         |                    1 | (none)                     | [7, 11, 8, 7, 11, 8] |

## A42 to A12 CSDO collapse

|   class_id | A42_resolved_negative_coordinates   | sign_vector_pm   | A12_image     | A12_period_three   |
|-----------:|:------------------------------------|:-----------------|:--------------|:-------------------|
|          1 | y_{B-,S-}                           | - + + + + +      | 7 11 8 7 11 8 | True               |
|          2 | y_{V-,S+}                           | + + + + - +      | 7 11 8 7 11 8 | True               |
|          3 | y_{B-,V+}                           | + + - + + +      | 7 11 8 7 11 8 | True               |
|          4 | (none)                              | + + + + + +      | 7 11 8 7 11 8 | True               |

## Interpretation

The available finite data now supports the exact shadow chain: the six-object Hom-dimension matrix `M6` is the decategorified `e_i A985 e_j` shadow of `T985`; its `B/V/S` quotient has the same `(B+S)/V` active plane; the Type-C CSDO coordinates define a four-dimensional signspan at `A42`; all four sign chambers collapse to one `A12` image; and the same CSDO data embeds as a proper face inside `Foam16`.

The raw tensor theorem requires the full tensor triples and quotient maps listed in `raw_T985_to_CSDO_theorem_input.schema.json`.
