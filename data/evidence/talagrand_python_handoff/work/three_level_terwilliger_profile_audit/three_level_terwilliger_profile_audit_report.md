# Three-level Terwilliger profile audit

## Status

`THREE_LEVEL_TERWILLIGER_PROFILE_AUDIT_NO_COUNTEREXAMPLE`

Certificate hash:

```text
f88e50bc62cf2860bb8c447a65bcf1e814185e3c28862a5d8c2e483ba1bfd790
```

## Uploaded inputs

- CSV: `three_level_terwilliger_profiles.csv`
- derive script: `derive_d20_golay_shell_three_level_terwilliger_profile_reps.py`

## CSV validation

| check | value |
|---|---:|
| rows | `9224` |
| shell 12 rows | `4612` |
| shell 16 rows | `4612` |
| validation failures | `0` |

Validation checked profile length, shell-count sums, and first/second/rest moment consistency.

## Numerical profile-gap audit

For each profile, the tested gap was

```text
F = log(A_profile(r,s)/A_w(1))
    - (w/2) log((n1 r^2+n2 s^2+n3)/24).
```

The theorem target is `F <= 0`.

### Grid audit

| shell | profiles | grid points | max grid F | profile |
|---:|---:|---:|---:|---:|
| 12 | 4612 | 1089 | 1.776e-15 | 3190 |
| 16 | 4612 | 1089 | 1.776e-15 | 3190 |


### Optimization audit

Top grid-risk profiles were refined with bounded analytic-gradient L-BFGS.

```text
max optimized F: 1.421e-14
optimization counterexamples: 0
```

## Interpretation

The uploaded table passes structural validation. Numerical grid and local optimization found no three-level counterexample in the emitted Terwilliger profile space.

This does not replace symbolic positivity certificates. The next target is per-profile bivariate certificate generation: factor/equality extraction, nonnegative residuals where possible, then SOS for the residue.
