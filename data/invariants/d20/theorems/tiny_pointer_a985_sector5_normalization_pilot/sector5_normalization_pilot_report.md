# Sector 5 Normalization Pilot

Status: `D20_TINY_POINTER_A985_SECTOR5_NORMALIZATION_PILOT_CERTIFIED`

This isolates the first minimum-dimension open sector. It certifies the current raw-orbital matrix units and emits the GL2 normalization equation needed to compare a genuine source-sector off-diagonal basis when one is supplied.

## Checks

- `normalization_obligations_certified`: `True`
- `full_matrix_unit_coo_certified`: `True`
- `target_sector_is_5`: `True`
- `target_sector_is_open`: `True`
- `target_sector_has_min_open_dimension_two`: `True`
- `source_lift_has_no_matrix_unit_basis`: `True`
- `current_manifest_has_4_units`: `True`
- `current_coo_rows_match_manifest_nonzeros`: `True`
- `sector_units_array_shape_is_985_by_4`: `True`
- `sector5_matrix_unit_law_exhaustive`: `True`
- `sector5_diagonal_sum_equals_central_page`: `True`
- `gl2_change_of_basis_has_16_terms`: `True`
- `gl2_constraints_have_9_rows`: `True`

Next: Supply four candidate source sector-5 matrix units in the candidate schema, then solve for the GL2 variables and verify equality in raw-orbital coordinates.
