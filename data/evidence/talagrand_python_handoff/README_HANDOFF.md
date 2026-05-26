# Talagrand Python Handoff Bundle

Created: 2026-05-26T22:30:33.713229+00:00

This bundle collects the Python-generated artifacts from the Talagrand/Hamming/Golay proof-development chain:
scripts, verifier scripts, machine certificates, reports, CSV/JSON tables, and derived data.

## Current proof status

`FINAL_GLOBAL_TALAGRAND_PROOF_NOT_CLAIMED`

Closed pieces include:

- all two-level threshold directions;
- the pair-stabilized three-level shell/contact slice;
- the exterior first-difference normal form `P_w=(x0-x1)Q_w`;
- the ordered-branch cone split of `Q_w`;
- the oriented-block factorization of the residual;
- the barrier contact derivative identity;
- the multilevel four-coefficient contact normal form.

The remaining exact target is:

```text
Exclude all solutions of the multilevel KKT obstruction system with dF > 0.
```

Equivalently:

```text
F_w(theta)=0, theta0>=theta1
=> partial_0 F_w - partial_1 F_w <= 0.
```

## Important latest directories

- `talagrand_multilevel_contact_normal_form/`
- `talagrand_weighted_asymmetry_contact_audit/`
- `talagrand_multilevel_KKT_obstruction_system/`
- `talagrand_barrier_contact_derivative_identity/`
- `talagrand_Q_residual_oriented_block_factorization/`
- `talagrand_ordered_branch_Q_cone_decomposition/`
- `talagrand_exterior_trace_first_difference/`
- `talagrand_global_pairwise_schur_polynomial/`
- `exact_all_two_level_shell_certificate/`
- `exact_pair_stabilized_shell_certificate/`

## Manifest

See:

```text
MANIFEST.csv
STATUS_LEDGER.json
```

Nested `.zip` files were intentionally excluded to avoid recursive duplication. This archive is the handoff archive of record.
