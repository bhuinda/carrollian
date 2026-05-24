# Sector 5 Nontrivial Normalization Fixture

Status: `D20_TINY_POINTER_A985_SECTOR5_NORMALIZATION_SOLVER_NONTRIVIAL_FIXTURE_CERTIFIED`

This verifies the sector-5 GL2 solver on a non-identity fixture generated from the certified raw matrix-unit chart. It proves the solver handles nontrivial basis changes, but remains a fixture rather than an independent legacy basis.

## Checks

- `pilot_certified`: `True`
- `selftest_certified`: `True`
- `source_gl2_is_nonidentity`: `True`
- `source_gl2_det_nonzero`: `True`
- `candidate_coo_rows_match_nonzeros`: `True`
- `candidate_has_four_nonzero_units`: `True`
- `row_chart_has_4_rows`: `True`
- `coordinate_matrix_matches_source_formula`: `True`
- `solved_gl2_det_nonzero`: `True`
- `solved_gl2_is_nonidentity`: `True`
- `solved_left_inverse_holds`: `True`
- `solved_right_inverse_holds`: `True`
- `solved_formula_reconstructs_candidate`: `True`
- `solver_residuals_zero`: `True`
- `candidate_raw_matrix_unit_law_exhaustive`: `True`

Next: Use the same verifier on an external sector-5 candidate file, because the solver has now been checked on both identity and non-identity controlled candidates.
