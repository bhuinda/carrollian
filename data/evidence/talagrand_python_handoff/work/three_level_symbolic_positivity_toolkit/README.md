# Three-Level Terwilliger Symbolic Positivity Toolkit

Next-step toolkit for the remaining Golay shell domination problem.

Input expected:

```text
three_level_terwilliger_profiles.csv
```

Target for each emitted profile:

```text
Gap_{w,pi}(a,b,c) >= 0  for a,b,c >= 0
```

where

```text
Gap = A_w(1)(n1 a^2+n2 b^2+n3 c^2)^(w/2)
      - 24^(w/2) A_profile(a,b,c).
```

The uploaded table has 4,612 profiles for w=12 and 4,612 profiles for w=16.

## Run

```bash
pip install numpy pandas scipy
python validate_three_level_profiles.py three_level_terwilliger_profiles.csv --out out_validate
python profile_gap_polynomial.py three_level_terwilliger_profiles.csv --shell 12 --profile-id 3190
python pairwise_square_cone_attack.py three_level_terwilliger_profiles.csv --shell 12 --profile-ids 3190 --out out_pairwise_3190
```

## What this is

A toolkit for generating exact/near-exact profile positivity certificates. It does not itself prove all 9,224 profile inequalities until the per-profile certificates are emitted and rationally verified.
