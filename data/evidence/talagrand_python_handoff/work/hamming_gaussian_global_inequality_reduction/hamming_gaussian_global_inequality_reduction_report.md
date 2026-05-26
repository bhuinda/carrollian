# Hamming--Gaussian Global Inequality Reduction

## Result

`HAMMING_GAUSSIAN_GLOBAL_INEQUALITY_REDUCTION_AND_STRESS_PASS`

## Candidate

```text
K^2 = 1.444854859266431
K   = 1.202021155914667
t*  = 0.686080818133236
```

## Exact MGF reduction

For `C=G24` and `Y=(-1)^c`, `c` uniform in `C`, the Fourier/MacWilliams identity gives

```text
M_C(u)=E exp(<u,Y>)
      = prod_i cosh(u_i) * sum_{d in C} prod_{i in supp(d)} tanh(u_i).
```

The remaining global theorem is therefore exactly

```text
M_C(u) <= exp((K^2/2)||u||^2) for every u in R^24.
```

Equivalently, prove the 24-variable polynomial-exponential inequality

```text
sum_{d in C} prod_{i in supp(d)} tanh(u_i)
<= exp((K^2/2)||u||^2 - sum_i log cosh(u_i)).
```

## Checks

MacWilliams identity max absolute error over deterministic samples:

```text
3.730e-14
```

Direction-scale stress rows: `107`

Best direction-scale result:

```json
{
  "index": 0,
  "label": "all_ones",
  "F": 1.4448548592664323,
  "K": 1.202021155914667,
  "scale": 3.3610958543805296,
  "gap_to_candidate": -8.881784197001252e-16,
  "codeword_abs_corr": 1.0000000000000002
}
```

Full multistart stress rows: `26`

Best full multistart result:

```json
{
  "index": 1,
  "label": "random_0",
  "F": 1.444854859266432,
  "K": 1.202021155914667,
  "norm": 3.3610958514044853,
  "gap_to_candidate": -6.661338147750939e-16,
  "codeword_abs_corr": 1.0000000000000002,
  "success": true,
  "nit": 20
}
```

No tested direction exceeded the candidate.

## Remaining residue

The remaining task is to prove the displayed global inequality, preferably by a Golay association-scheme / Krawtchouk domination argument.
