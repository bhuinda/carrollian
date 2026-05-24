# Fano layer supplement for source_drop `R_Omega` classification

## What was missing

The previous source_drop package classified `R_Omega`, but it did not include the explicit Fano-plane data or the original source_drop Fano-zone tables. This supplement adds both.

## Canonical Fano plane

The canonical Fano plane is `F_2^3 \ {0}` with seven points and seven lines. Lines are triples `{a,b,a+b}`.

Canonical incident flag:

```text
P1 = 001
L3 = {001,010,011}
F7 \ L3 = {100,101,110,111}
```

The full Fano automorphism group is `GL(3,2)` of order `168`; the stabilizer of the incident flag `(P1,L3)` has order `8`.

## Fano coefficients

Absorbed no-intercept coefficients in the basis `(P1, L3\P1, F7\L3)`:

| target | P1 | L3\P1 | F7\L3 | explained Frobenius |
|---|---:|---:|---:|---:|
| `P_G` | 170.686641 | 116.825276 | -114.370911 | 0.585977 |
| `Pi_flag` | 170.686641 | 116.825276 | -114.370911 | 1.000000 |
| `R_Omega` | -0.000000 | -0.000000 | -0.000000 | 0.000000 |

For `P_G`, these are the Fano-zone payoff coefficients. For `R_Omega`, the coefficients are near zero because `R_Omega` was constructed as the residual after removing the flag skeleton.

## Weighted residual by Fano zone

| zone | weighted mean R_Omega | weighted abs mean | weighted square mean | energy share |
|---|---:|---:|---:|---:|
| `P1_point` | -0.000000 | 110.223054 | 20331.833865 | 0.968499 |
| `L3_minus_P1` | -0.000000 | 90.697272 | 11126.478210 | 0.030316 |
| `F7_minus_L3` | -0.000000 | 64.379946 | 8477.888515 | 0.001185 |

## Equivariance caveat

This package now includes the unsigned Fano flag stabilizer explicitly. However, the available source_drop/source_drop data still do not contain a signed-Fano permutation representation on the 16 builder labels and 16 jabber labels. Therefore the full signed-Fano equivariance test on `R_Omega` remains uncertified.

What is now certified is the canonical Fano flag object and the exact source_drop/source_drop Fano-zone projection data.

## Added files

- `fano/fano_flag_ordered_pair_orbits.csv`
- `fano/fano_flag_stabilizer_GL3F2.csv`
- `fano/fano_flag_zones.csv`
- `fano/fano_layer_report.json`
- `fano/fano_plane_lines.csv`
- `fano/fano_plane_points.csv`
- `fano/fano_zone_coefficients_payoff_flag_residual.csv`
- `fano/fano_zone_leftover_P_G.csv`
- `fano/fano_zone_leftover_Pi_flag.csv`
- `fano/fano_zone_leftover_R_Omega.csv`
- `fano/fano_zone_projection_P_G.csv`
- `fano/fano_zone_projection_Pi_flag.csv`
- `fano/fano_zone_projection_R_Omega.csv`
- `fano/fano_zone_projection_arrays.npz`
- `fano/fano_zone_weighted_operator_summary.csv`
- `fano/input/g_builder_flag_simplex.csv`
- `fano/input/g_fano_zone_summary.csv`
- `fano/input/g_jabber_flag_simplex.csv`
- `fano/input/g_pair_flag_features.csv`
