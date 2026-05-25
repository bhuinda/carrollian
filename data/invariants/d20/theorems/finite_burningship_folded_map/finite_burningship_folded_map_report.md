# finite Burning Ship folded map

Status: `D20_FINITE_BURNINGSHIP_FOLDED_MAP_CERTIFIED`

A literal finite folded version of the Burning Ship recurrence has been evaluated on cyclic grids. Its direct mod-4 parameter frame gives Z/4^2; the A985 static Z/2 x Z/4^2 shape appears when the finite model keeps the order-two fold-sheet bit.

Boundary: This is a finite dynamical-system model of the classical formula. It does not prove that the imported sandpile_burningship certificate used this exact finite fold rule.

## Checks

- `bridge_certified`: `True`
- `target_quotient_factors_are_z2_z4_z4`: `True`
- `mod4_direct_shape_is_z4_squared`: `True`
- `mod4_branch_lift_matches_static_2primary`: `True`
- `mod20_branch_lift_matches_static_2primary`: `True`
- `mod60_branch_lift_matches_static_2primary`: `True`
- `all_finite_maps_are_total_on_grid`: `True`
- `all_transition_indegrees_uniform_when_parameters_vary`: `True`
- `mod60_has_nontrivial_orbit_variety`: `True`
- `semantics_file_emitted`: `True`

Next: Use the branch-lifted Z/2 x Z/4^2 finite frame as a naming and normalization model for the A985 static 2-primary readout.
