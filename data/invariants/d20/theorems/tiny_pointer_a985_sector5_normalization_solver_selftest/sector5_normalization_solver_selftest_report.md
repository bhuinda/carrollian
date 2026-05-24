# Sector 5 Normalization Solver Self-Test

Status: `D20_TINY_POINTER_A985_SECTOR5_NORMALIZATION_SOLVER_SELFTEST_CERTIFIED`

This proves the GL2 solver and raw-coordinate verifier on a controlled self-candidate. The candidate is the already certified sector-5 raw matrix-unit chart, so this is an executable normalization path, not an independent legacy-basis solution.

## Checks

- `pilot_certified`: `True`
- `self_candidate_has_144_coo_rows`: `True`
- `row_chart_has_4_rows`: `True`
- `coordinate_matrix_is_identity`: `True`
- `gl2_solution_g_is_identity`: `True`
- `gl2_solution_ginv_is_identity`: `True`
- `gl2_left_inverse_holds`: `True`
- `gl2_right_inverse_holds`: `True`
- `formula_reconstructs_candidate`: `True`
- `solver_residuals_zero`: `True`
- `candidate_raw_matrix_unit_law_exhaustive`: `True`

Next: Run this solver against a non-self sector-5 candidate source, or derive such a candidate from an upstream legacy off-diagonal construction.
