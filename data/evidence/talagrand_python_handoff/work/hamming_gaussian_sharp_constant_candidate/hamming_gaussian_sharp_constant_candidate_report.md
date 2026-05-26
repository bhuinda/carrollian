# Hamming--Gaussian Sharp Constant Candidate

## Result

`HAMMING_GAUSSIAN_SHARP_CONSTANT_CANDIDATE_LOCAL_CERTIFIED`

This stage attacks the next conjectural residue: whether the sharp full-coordinate subgaussian proxy constant of the Golay sign vector is achieved by a codeword sign direction.

## Exact candidate direction

For any `d in G24`, set `s_i=(-1)^{d_i}` and `Y_i(c)=(-1)^{c_i}`. Then

```text
<s,Y(c)> = 24 - 2 wt(c+d).
```

Since `c+d` is uniform in `G24`, the distribution is exactly the Golay weight enumerator:

```json
{
  "-24": 1,
  "-8": 759,
  "0": 2576,
  "8": 759,
  "24": 1
}
```

## Stationary points in the codeword direction

The objective is

```text
F(u)=2 log E exp(<u,Y>) / ||u||^2.
```

For `u=t*s`, the stationary equation is

```text
t L'(t) = 2 L(t).
```

Stationary points found:

```json
[
  {
    "t": 0.176012148805274,
    "F": 0.9966163229310666,
    "K": 0.9983067278802976,
    "L": 0.3705053913093135,
    "ES": 4.209997932804188,
    "ES2": 42.10966917881448,
    "Var": 24.38558658459894,
    "stationarity_residual": -3.3306690738754696e-16
  },
  {
    "t": 0.6860808181332365,
    "F": 1.4448548592664316,
    "K": 1.2020211559146667,
    "L": 8.161237630521837,
    "ES": 23.79089289430309,
    "ES2": 569.3431597729495,
    "Var": 3.3365750647482173,
    "stationarity_residual": -7.105427357601002e-15
  }
]
```

The candidate maximum is

```text
K^2 = 1.444854859266432
K   = 1.202021155914667
t*  = 0.686080818133237
```

## Local maximum certificate

At `u=t*1`, the gradient norm is

```text
2.006648e-15
```

The Hessian eigenvalue range is

```text
min eigenvalue = -0.253660221741863
max eigenvalue = -0.231182598046061
```

Since the max eigenvalue is negative, this is a strict local maximum of `F`.

## Multistart diagnostic

Starts tested: `46`.

Best found:

```json
{
  "start_index": 5,
  "success": true,
  "F": 1.444854859266433,
  "K": 1.2020211559146674,
  "norm": 3.361095853500905,
  "nit": 7,
  "best_codeword_abs_corr": 1.0000000000000002,
  "best_codeword_weight": 12,
  "message": "CONVERGENCE: NORM OF PROJECTED GRADIENT <= PGTOL"
}
```

Converged to the candidate maximum with codeword-sign correlation `> 1-1e-7`:

```text
15
```

## Boundary

This is a local and numerical global-candidate certificate, not a rigorous global optimization proof over all directions in `R^24`.

The remaining theorem is to prove a global inequality:

```text
forall u in R^24, 2 log E exp(<u,Y>) / ||u||^2 <= 1.444854859266432.
```
