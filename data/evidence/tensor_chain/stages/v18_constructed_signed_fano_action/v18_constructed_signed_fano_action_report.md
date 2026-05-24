# v18 — constructed signed-Fano action

## Main result

```text
action_constructed                  = true
exact_on_Foam16                     = true
signed_Fano_group_order             = 768
full_WD6_order                      = 23040
data_induced_label_action           = constructed, low-rank
global_Romega_equivariance          = false
```

I constructed the action directly instead of trying to recover it from the v8/v17 zone aggregates.

The canonical carrier is

```text
Foam16 = 1 + Lambda^2 H6
```

where `H6` is obtained by nullifying the Fano point `011` and taking the remaining six Fano points as the six tetrahedral/6j edge channels.

## Six-channel dictionary

|   channel_index | channel   |   fano_point |   null_point |
|----------------:|:----------|-------------:|-------------:|
|               0 | B-        |          001 |          011 |
|               1 | B+        |          010 |          011 |
|               2 | V-        |          100 |          011 |
|               3 | V+        |          111 |          011 |
|               4 | S-        |          101 |          011 |
|               5 | S+        |          110 |          011 |

## Constructed group

- S4 edge permutations from `Stab_F7(011)`: `24`
- even D6 sign flips: `32`
- signed-Fano group constructed: `768`
- full W(D6) group constructed on the same Foam16 carrier: `23040`
- generators exported: `9`

Each signed channel action sends

```text
e_i -> s_i e_{p(i)}
```

and the induced Foam16 action is

```text
1 -> 1
e_i wedge e_j -> s_i s_j e_{p(i)} wedge e_{p(j)}
```

with the usual sign from reordering the wedge pair.

## Foam16 action test

| group           |   size |   invariant_energy_fraction_vs_Rfoam |   breaking_energy_fraction_vs_Rfoam |   invariant_cos2_with_Rfoam |   invariant_participation_rank |   breaking_participation_rank |
|:----------------|-------:|-------------------------------------:|------------------------------------:|----------------------------:|-------------------------------:|------------------------------:|
| signed_fano_768 |    768 |                          0.00068345  |                            0.999317 |                 0.00068345  |                        1.32204 |                       1.94066 |
| full_WD6_23040  |  23040 |                          0.000681236 |                            0.999319 |                 0.000681236 |                        1.32634 |                       1.94256 |

The exact action is now available, and the foam-projected residual is still strongly breaking the constructed symmetry. That is a real test, not a recovery failure.

## Data-induced 16-label action

I also constructed a data-induced action on the current 16 builder and 16 jabber labels by embedding each label into Foam16 and pulling back the exact Foam16 action by minimum-norm pseudoinverse.

Embedding ranks:

- builder six-channel rank: `3`
- jabber six-channel rank: `3`
- builder Foam16 rank: `5`
- jabber Foam16 rank: `5`

Signed-Fano 768-element induced-label equivariance summary:

|   min_relerr |   mean_relerr |   median_relerr |   max_relerr |   mean_cos2 |   median_cos2 |
|-------------:|--------------:|----------------:|-------------:|------------:|--------------:|
|     0.838218 |       644.414 |         487.077 |      2400.62 |  0.00284548 |   0.000513764 |

Generator composition defect summary:

|   builder_mean |   builder_max |   jabber_mean |   jabber_max |
|---------------:|--------------:|--------------:|-------------:|
|       0.406633 |       10.9944 |        3.1602 |      145.359 |

This confirms that the current strategy labels are not already a faithful signed-Fano module under the available embedding. The action is exact on Foam16; the pullback to labels is low-rank because the labels are not point/sign-resolved enough.

## Hard gauge action

For executability, I also wrote a declared hard gauge assigning the 16 builder labels and 16 jabber labels to the 16 Foam16 basis coordinates in their current order. This gives exact signed-monomial generator matrices on the label set. It is a gauge declaration, not a recovered label symmetry.

## Verdict

```text
The action is now constructed.
It is exact on Foam16 = 1 + Lambda^2 H6.
It can be pulled back to the current 16 labels, but only as a low-rank real action.
The current R_Omega is not globally equivariant under the constructed action.
Therefore the mechanism is a chamber-selection/breaking operator, not a signed-Fano invariant.
```