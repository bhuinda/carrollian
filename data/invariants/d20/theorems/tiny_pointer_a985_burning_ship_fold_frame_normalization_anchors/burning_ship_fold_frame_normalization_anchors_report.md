# Burning Ship fold-frame normalization anchors

Status: `D20_TINY_POINTER_A985_BURNING_SHIP_FOLD_FRAME_NORMALIZATION_ANCHORS_CERTIFIED`

The A985 static 2-primary frame is normalized by the finite Burning Ship branch-lift convention: fold-sheet bit, primary mod-4 clock, and framed mod-4 clock map to the three constructed raw-orbital generators.

Boundary: These anchors normalize the static Z/2 x Z/4^2 frame. They do not remove the separate sector-local GL_d matrix-unit basis ambiguity for all open blocks.

## Checks

- `finite_burning_ship_folded_map_certified`: `True`
- `constructed_static_representative_certified`: `True`
- `trace_evaluator_ready_or_profile_certified`: `True`
- `public_zero_alignment_certified`: `True`
- `sector33_detector_certified`: `True`
- `mod4_direct_shape_is_z4_squared`: `True`
- `mod4_branch_lift_shape_matches_static`: `True`
- `mod20_branch_lift_shape_matches_static`: `True`
- `mod60_branch_lift_shape_matches_static`: `True`
- `anchor_order_profile_is_2_4_4`: `True`
- `exact_sector33_detector_generators_are_fold_sheet_and_primary_clock`: `True`
- `all_anchor_rows_vanish_on_sector33`: `True`
- `framed_clock_records_extra_zero_sector20`: `True`
- `anchor_rows_count_is_3`: `True`

Next: Thread this fold-frame convention into the sector-local normalization ledger as the static 2-primary anchor, while keeping the remaining GL_d block-basis obligations explicit.
