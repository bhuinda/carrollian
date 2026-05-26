# Current status

The uploaded three-level profile table is the right object for the next symbolic pass.

The all-profile pairwise-square NNLS route is computationally expensive in the interactive window. This toolkit therefore supports selected-profile and batch execution.

Next target:

1. Run pairwise_square_cone_attack.py on risky profiles from the grid audit.
2. If successful, parallelize profile batches.
3. Rationalize coefficients profile-by-profile.
4. Emit exact JSON certificates.
