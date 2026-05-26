# Three-level exact rationalization seed

## Status

`THREE_LEVEL_EXACT_RATIONAL_SEED_COMPLETE`

Certificate hash:

```text
310f9b89f03059f8220dc6912969cafd576fd85c06e5814b20a44ebfafd393fe
```

## Result

Selected profile supports from the pairwise-square NNLS cone were rationalized with exact SymPy linear solves.

Profiles attempted: `10`

Status counts:

```json
{
  "EXACT_RATIONAL_PASS": 4,
  "EXACT_ZERO_GAP_PASS": 4,
  "NO_SOLUTION": 2
}
```

This is not yet the all-profile exact certificate. It proves the rationalization path works on selected profiles and emits exact coefficient numerators/denominators for successful cases.

## Next step

Run the same exactification in chunks over all profiles. If exact solves remain nonnegative, emit per-profile JSON certificates.
