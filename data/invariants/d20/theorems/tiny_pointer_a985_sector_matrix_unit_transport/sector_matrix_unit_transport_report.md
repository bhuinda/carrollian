# Sector Matrix-Unit Transport

Status: `D20_TINY_POINTER_A985_SECTOR_MATRIX_UNIT_TRANSPORT_CERTIFIED`

The full source-sector map is now applied to the registered raw matrix-unit manifest. Rows with blank source-sector labels in the top support are filled from the certified all-39 match, while previously registered support rows are preserved and checked.

## Checks

- `full_match_is_certified`: `True`
- `registered_stage_is_certified`: `True`
- `transported_manifest_row_count_is_1011`: `True`
- `all_rows_have_source_sector`: `True`
- `no_transport_mismatch_rows`: `True`
- `top_support_has_985_rows`: `True`
- `top_support_covers_all_39_source_sectors`: `True`
- `top_support_counts_are_d_squared`: `True`
- `sector_profile_count_is_39`: `True`
- `sector_profile_matrix_unit_counts_match_d_squared`: `True`
- `registered_support_source_transport_matches_source`: `True`
- `perennial_join_key_emitted_when_available`: `True`

Next: Attach raw orbital COO coefficients to the all-39 source-sector matrix-unit manifest, not only to the registered public-zero support subset.
