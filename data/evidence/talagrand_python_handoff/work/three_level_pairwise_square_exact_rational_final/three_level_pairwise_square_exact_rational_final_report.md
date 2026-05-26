# Three-level pairwise-square exact rational final pass

## Status

`THREE_LEVEL_PAIRWISE_SQUARE_CONE_EXACT_RATIONAL_FULL_PASS`

Certificate hash:

```text
e548c6b499ebb3a16a6815689bfeffb9ef8ad9332935b564365124465e967b1b
```

## Exact certificate form

Every emitted three-level Terwilliger profile gap for shells `w=12` and `w=16` is certified in the exact rational cone

```text
Gap(a,b,c) = (a-b)^2 P_ab(a,b,c)
           + (a-c)^2 P_ac(a,b,c)
           + (b-c)^2 P_bc(a,b,c),
```

with `P_ab`, `P_ac`, and `P_bc` having nonnegative rational monomial coefficients.

## Results

| shell | profiles | exact rational pass | zero gap pass | parametric repaired | failures | max support | median support | total nonzero exact coeffs |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 12 | 4612 | 4609 | 3 | 0 | 0 | 88 | 86.0 | 351344 |
| 16 | 4612 | 4606 | 3 | 3 | 0 | 151 | 150.0 | 583994 |

## Parametric repairs

Three `w=16` profiles initially produced one-parameter exact solution families. Choosing an explicit rational parameter inside the nonnegative interval repaired all three.

## Meaning

This upgrades the floating NNLS cone pass into an exact rational certificate for all `9,224` emitted three-level Terwilliger profiles.

The certified scope is the three-level Terwilliger profile table. The next proof layer is to connect this profile-level exact positivity to arbitrary nonnegative vectors, either through level-partition induction, four-level certificates, or a global Veronese/SOS argument.
