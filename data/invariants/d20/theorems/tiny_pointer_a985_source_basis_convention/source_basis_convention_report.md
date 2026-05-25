# Source-sector basis convention

Status: `D20_TINY_POINTER_A985_SOURCE_BASIS_CONVENTION_CERTIFIED`

The repository now fixes a source-sector matrix-unit basis convention: the stored raw-orbital matrix units from full_matrix_unit_orbital_coo are the comparison basis, so the convention transform is g_s = I in every nontrivial block.

Boundary: This is a coordinate convention. The mathematical PGL_d basis-change symmetry remains recorded by the ambiguity mechanism theorem.

Convention residual gauge dimension: `0`

Mathematical PGL dimension retained: `946`

## Checks

- `full_matrix_unit_coo_certified`: `True`
- `normalization_obligations_certified`: `True`
- `gl_d_ambiguity_mechanism_certified`: `True`
- `burning_ship_fold_frame_anchors_certified`: `True`
- `convention_rows_cover_39_sectors`: `True`
- `matrix_unit_count_is_985`: `True`
- `convention_status_counts_match_expected`: `True`
- `identity_gl_rows_match_nontrivial_blocks`: `True`
- `mathematical_pgl_dimension_retained_is_946`: `True`
- `prior_unanchored_pgl_dimension_was_940`: `True`
- `repo_convention_residual_gauge_dimension_is_zero`: `True`
- `all_direct_products_pass`: `True`
- `all_diagonal_sums_are_central_pages`: `True`
- `contract_emitted`: `True`
- `perennial_join_key_emitted_when_available`: `True`

Next: Use this convention as the target coordinate system for any future external sector basis or rank-one idempotent flag.
