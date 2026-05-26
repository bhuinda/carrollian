# Three-level pairwise-square cone full numerical pass

## Status

`THREE_LEVEL_PAIRWISE_SQUARE_CONE_FULL_NUMERICAL_PASS`

Certificate hash:

```text
345bef3cb547d5a6daed4fe29d9c9bae6a89690189c43888cb8cde87b70d6ec7
```

## Cone form

For every uploaded three-level Terwilliger profile, the homogeneous gap polynomial was tested for numerical membership in

```text
Gap(a,b,c)
=
(a-b)^2 P_ab(a,b,c)
+
(a-c)^2 P_ac(a,b,c)
+
(b-c)^2 P_bc(a,b,c),
```

where the residual polynomials `P_ab`, `P_ac`, and `P_bc` are represented by nonnegative monomial coefficients.

This is a direct positivity certificate form over `a,b,c >= 0`, because the square factors and residual monomials are nonnegative.

## Results

| shell | profiles | failures | worst L∞ residual | worst L2 residual | median nonzero coeffs | max nonzero coeffs |
|---:|---:|---:|---:|---:|---:|---:|
| 12 | 4612 | 0 | 3.553e-15 | 6.196e-15 | 78.0 | 86 |
| 16 | 4612 | 0 | 9.603e-15 | 1.176e-14 | 130.0 | 144 |


## Interpretation

This completes the floating-point NNLS pass for both open shells:

```text
w=12: 4612 / 4612 profiles pass
w=16: 4612 / 4612 profiles pass
```

So every three-level Terwilliger profile now has a numerical pairwise-square cone certificate.

## Boundary

This is still not the final theorem-grade certificate. The next step is rationalization:

1. take each profile's NNLS support pattern;
2. solve the exact rational linear system on that support;
3. verify all rational coefficients are nonnegative;
4. emit per-profile exact JSON certificates.

The present pass gives the correct cone ansatz and shows the exact certificate is very likely to exist.
