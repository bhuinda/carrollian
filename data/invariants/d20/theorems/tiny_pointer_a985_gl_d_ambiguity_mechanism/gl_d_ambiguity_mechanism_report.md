# GL_d ambiguity mechanism

Status: `D20_TINY_POINTER_A985_GL_D_AMBIGUITY_MECHANISM_CERTIFIED`

The sector-local GL_d ambiguity is the ordinary basis-change symmetry of each matrix block e_s A985 e_s. Central idempotents and matrix-unit laws determine the block algebra but not an ordered simple-module basis; non-identity GL_d conjugates give equally valid raw-orbital matrix units.

Boundary: This explains and witnesses the ambiguity. It does not choose the missing external basis for the 30 open sectors.

Intrinsic PGL dimension: `946`

Residual unanchored PGL dimension: `940`

## Checks

- `normalization_obligations_certified`: `True`
- `all_open_fixture_atlas_certified`: `True`
- `fold_frame_anchors_certified`: `True`
- `full_matrix_unit_coo_certified`: `True`
- `sector_rows_cover_39`: `True`
- `dimension_histogram_matches_wedderburn_profile`: `True`
- `intrinsic_pgl_dimension_is_946`: `True`
- `residual_unanchored_pgl_dimension_is_940`: `True`
- `open_sector_count_is_30`: `True`
- `dimension_one_sector_count_is_7`: `True`
- `registered_support_anchored_nontrivial_count_is_2`: `True`
- `every_open_sector_has_nontrivial_witness`: `True`
- `every_open_witness_has_zero_residual`: `True`
- `every_open_witness_preserves_central_page`: `True`
- `nontrivial_sectors_have_pgl_group`: `True`
- `perennial_join_key_emitted_when_available`: `True`

Next: Either accept the current constructed basis as the repo convention for open sectors, or add an external criterion that selects a rank-one idempotent flag in each open block.
