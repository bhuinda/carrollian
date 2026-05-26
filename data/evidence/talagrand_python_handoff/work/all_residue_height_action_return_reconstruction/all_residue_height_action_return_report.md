# All-Residue Height Action-Return Reconstruction

## Status

`ALL_RESIDUE_HEIGHT_ACTION_RETURN_RECONSTRUCTED_PASS`

Certificate hash:

```text
1582dc9ad41a1219ff7c7c9d23ba80bf01096419f03ca21efe4db28f2752807c
```

## What was computed

Using the uploaded `T_985.npz`, `relation_memberships.npz`, `projection_section.json`, current height-coherent report, and the embedded d20 H-cycle data, I reconstructed the full scalar height/action-return table for all

```text
2^11 = 2048
```

closed-return residue masks.

For a residue mask `m` with active basis cycles `C_m`, the scalar transport is

```text
height_action(m) = <C_m, h_B>
residual(m)      = -height_action(m)
transport_scalar = residual(m)/dim(Pi_33)
```

with

```text
dim(Pi_33)=2
```

over `F_1000003`.

## Core result

| invariant | value |
|---|---:|
| residue masks | 2048 |
| nonzero residue masks | 2047 |
| support sector | 33 |
| min nonzero height action | 374784 |
| max height action | 10564608 |
| edge-mod2 incoherent masks | 2020 |
| T_985 tensor support | 1414965 |
| relation count | 985 |
| tube closed-loop quotient dimension | 297 |

## Gamma-8 check

The gamma-8 row is mask `256`.

| datum | value |
|---|---:|
| height action | 374784 |
| residual integral | -374784 |
| residual mod 1000003 | 625219 |
| transport scalar mod 1000003 | 812611 |
| transport scalar signed | -187392 |

This matches the uploaded gamma-8 height-coherent report.

## Important caveat

This package reconstructs the all-mask scalar action-return table, not full 56-coordinate vectors for all masks.

To materialize every vector

```text
Lambda_hc(mask)=lambda_boundary(mask)-height(mask)/2 * e33
```

we still need either all `lambda_boundary(mask)` rows or a deterministic generator-level vector rule for all 11 primitive basis cycles.

## Checks

```json
{
  "T985_relation_count_is_985": true,
  "T985_support_is_1414965": true,
  "all_public_shadows_zero": true,
  "all_transports_carried_by_sector33": true,
  "edge_mod2_mismatch_count_matches_known_2020": true,
  "full_mask_height_action_matches_known": true,
  "gamma8_height_action_matches_uploaded": true,
  "gamma8_residual_integral_matches_uploaded": true,
  "gamma8_residual_mod_matches_uploaded": true,
  "gamma8_transport_scalar_matches_uploaded": true,
  "nonzero_residue_class_count_is_2047": true,
  "projection_section_dimension_297": true,
  "projection_section_identity_declared": true,
  "relation_membership_reps_match_T985": true,
  "residue_masks_are_complete": true,
  "zero_class_has_zero_transport_scalar": true
}
```
