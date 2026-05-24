# All Open-Sector Normalization Fixture Atlas

Status: `D20_TINY_POINTER_A985_ALL_OPEN_SECTOR_NORMALIZATION_FIXTURE_ATLAS_CERTIFIED`

Open sectors: `30`

Open matrix units: `970`

Coordinate nonzeros: `72272`

## Checks

- `full_matrix_unit_coo_certified`: `True`
- `normalization_obligations_certified`: `True`
- `sector5_nontrivial_fixture_certified`: `True`
- `open_sector_count_is_30`: `True`
- `open_matrix_unit_count_is_970`: `True`
- `coordinate_rows_match_summary`: `True`
- `all_source_gl_nonidentity`: `True`
- `all_solved_gl_nonidentity`: `True`
- `all_solved_left_inverses_hold`: `True`
- `all_solved_right_inverses_hold`: `True`
- `all_formula_residuals_zero`: `True`
- `all_diagonal_sums_preserved`: `True`
- `sampled_raw_candidate_products_pass`: `True`

Boundary: No independent legacy off-diagonal matrix-unit basis is supplied by this fixture atlas.

Next: Wire the same all-sector verifier to accept an external legacy candidate COO file, then run it as soon as a genuine legacy off-diagonal source exists.
