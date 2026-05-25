# Canonical Sector Matrix Units

Status: `D20_TINY_POINTER_A985_CANONICAL_SECTOR_MATRIX_UNITS_CERTIFIED`

Matrix units: `985`

Diagonal units: `159`

Off-diagonal units: `826`

## Checks

- `full_sector_match_certified`: `True`
- `full_matrix_unit_coo_certified`: `True`
- `support_restricted_multiplication_certified`: `True`
- `all_39_source_sectors_present`: `True`
- `all_985_matrix_units_present`: `True`
- `diagonal_count_is_159`: `True`
- `off_diagonal_count_is_826`: `True`
- `all_sector_unit_grids_complete`: `True`
- `all_units_have_raw_orbital_coo`: `True`
- `manifest_nonzero_counts_match_coo`: `True`
- `no_missing_local_matrix_unit_labels`: `True`
- `top_support_symbolic_matrix_unit_table_complete`: `True`
- `top_support_nonzero_products_match_sum_d_cubed`: `True`
- `perennial_join_key_emitted_when_available`: `True`

Gauge note: A later external convention may still differ by sector-local GL_d conjugacy, but that is a comparison problem. It is not a construction blocker for u_sector[s;i,j].

Next: Use the canonical source-sector matrix units as the default input for sector-local character, Fourier, or block trace calculations; only introduce GL_d comparison data if a separate external convention needs to be matched.
