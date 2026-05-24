# D20 q-Weighted Stack Series v26

## Result

```text
D20_Q_WEIGHTED_STACK_SERIES_CERTIFIED_MOTIVIC_COHA_OPEN
```

This gate adds q-weights to the derived stack dimension-vector series.

It computes three q-weighted budget systems:

1. half-arrow budget

```text
A_half(n)=sum_i n_Ci n_Fi
```

2. doubled-arrow budget

```text
A_double(n)=2 A_half(n)
```

3. gauge budget

```text
G(n)=sum_v n_v^2
```

The computation is truncated to

```text
total dimension n <= 40
q exponent <= 512
```

This is a certified truncated q-series computation, not yet a motivic or sheafified CoHA series.

## Pair kernels

For each pair `(F_i,C_i)` and parity class `(f,c) in F2^2`, the half-arrow kernel is

```text
K_fc(t,q)=sum_{a=f mod 2, b=c mod 2} t^(a+b) q^(ab)
```

The doubled and gauge kernels replace `ab` by `2ab` and `a^2+b^2`.

## Grade decomposition

The wall grades are computed by:

```text
grade0 = K_00^6
grade1 = binom(6,3) K_10^3 K_00^3
grade2 = sum_r binom(6,r) K_10^r K_00^(6-r), r in {1,2,4,5,6}
grade3 = (K_00+K_10+K_01+K_11)^6 - (K_00+K_10)^6
```

## Invariant scan

The scan searched for:

```text
[32, 39, 91, 243, 455, 2275, 4095, 6825, 6912, 14560, 455640, 531441, 534656, 1414965, 2537360]
```

across half-arrow, doubled-arrow, and gauge weighted coefficients.

Important status:

```text
39: exact hits recorded if present in invariant_weighted_hits.csv
243: exact hits recorded if present in invariant_weighted_hits.csv
455640: no direct hit in this q-window
534656: no direct hit in this q-window
```

The Terwilliger numbers remain diagnostic unless a stable coefficient law appears at higher bounds or with A985 tensor weights.

## Correct status

```text
q-weighted stack-counting series certified
motivic/sheafified CoHA series open
```

## Files

- `q_weighted_series_formulas.json`
- `half_weighted_coefficients.csv`
- `double_weighted_coefficients.csv`
- `gauge_weighted_coefficients.csv`
- `weighted_moments_by_dimension.csv`
- `invariant_weighted_hits.csv`
- `q_weighted_series_tests.csv`
- `q_weighted_stack_series_certificate.json`
- `verify_q_weighted_stack_series.py`
