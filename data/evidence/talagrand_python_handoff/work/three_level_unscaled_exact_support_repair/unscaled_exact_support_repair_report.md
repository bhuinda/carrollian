# Unscaled exact support repair seed

## Status

`UNSCALED_EXACT_SUPPORT_REPAIR_SEED_COMPLETE`

Certificate hash:

```text
5735d62cde8eb478fb744a8e7ef6f6f481af375938bdf56035e706b7bcb68dab
```

## Result

Using unscaled NNLS support instead of scaled NNLS support repairs the selected `w=16` profiles that previously failed exact rationalization.

Status counts:

```json
{
  "EXACT_RATIONAL_PASS": 5
}
```

The selected successful profiles emit exact rational nonnegative coefficients in:

```text
unscaled_exact_support_repair_coefficients.csv
```

## Key correction

Do not rationalize from scaled NNLS support. Use unscaled NNLS support:

```text
nnls(A, b_integer)
```

then exact solve:

```text
A_support x = b_integer
```

This produced exact nonnegative rational coefficients for the selected repair profiles.

## Next step

Run:

```bash
python chunked_exact_pairwise_square_rationalize.py three_level_terwilliger_profiles.csv \
  --shell 16 --start 0 --stop 250 --out exact_w16_000_250
```

Then batch all profiles.
