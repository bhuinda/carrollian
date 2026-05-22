# Intrinsic carrier dependency geometry

```text
status = INTRINSIC_CARRIER_DEPENDENCY_GEOMETRY_CERTIFIED
intrinsic_carrier_dependency_geometry_sha256 =
6fb58b531c6897b65aa73bbcb70843fbb626d2daeecbb64f600ecc154ab988e1
```

## Main result

The v24 correction remains in force: naive lasso uniqueness is false. The new invariant is the dependency geometry of the 39 Hesse pencils inside the 35-dimensional Hesse cut.

```text
Plucker/Hesse pencil rank:        35
dependency code dimension:        4
dependency code length:           39
minimum row circuit weight:       36
```

So the pencil configuration carries a finite linear dependency code

\[
[39,4,36]_{1000003}.
\]

## Dependency PG(3) geometry

The four independent dependencies give 39 projective columns in \(\mathbb P^3(\mathbb F_p)\).

```text
zero projective columns:          0
unique projective columns:        39
unique lines:                     741
line size histogram:              {'2': 741}
max collinear count:              2
unique planes:                    9139
plane size histogram:             {'3': 9139}
max coplanar count:               3
uniform position certificate:      True
```

Thus no three dependency columns are collinear and no four are coplanar. This is the intrinsic carrier invariant that replaces naive projection uniqueness.

## Hessian monodromy signature

For each sector, the Hesse closure is

\[
H(H(X_i))=lpha_iX_i+eta_iH(X_i).
\]

The associated companion signature has discriminant

\[
\Delta_i=eta_i^2+4lpha_i
\]

and projective eigenratio order.

```text
Legendre histogram:               {'-1': 22, '1': 17}
order histogram:                  {'9434': 1, '166667': 7, '250001': 10, '500001': 10, '500002': 11}
unique order count:               5
min order:                        9434
max order:                        500002
```

Field factorizations:

```text
p-1 = 1000002: {'2': 1, '3': 1, '166667': 1}
p+1 = 1000004: {'2': 2, '53': 2, '89': 1}
```

## Refined separation ladder

```json
{
  "Hessian_order_only": 5,
  "Hessian_legendre_plus_order": 5,
  "order_plus_block_dimension": 24,
  "order_plus_block_dimension_plus_multiplicity": 35,
  "order_plus_block_dimension_plus_multiplicity_plus_permutation_rank": 35,
  "q12_signature_plus_order": 37,
  "q42_signature_plus_order": 38,
  "q42_signature_plus_discriminant": 39,
  "block_mult_rank_plus_closure_pair": 39,
  "block_mult_rank_plus_order_legendre": 35,
  "A42_plus_secondary_separator": 39
}
```

The important new separator is:

```text
q42 + Hessian discriminant:        39 / 39
q42 + Hessian order:               38 / 39
```

So the Hessian discriminant is the smallest new scalar found here that finishes the q42 surface split.

## Character-basis refinement

```text
basis shape:                       [39, 39]
rank:                              39
determinant of basis transpose:    1
basis support:                     39
basis row weights:                 {'1': 39}
basis column weights:              {'1': 39}
dual inverse support:              39
dual inverse zero-one:             True
```

The A42+secondary character basis has already reached the primitive point basis. There is no hidden residual multiplicity in the pseudomodular Verlinde algebra.

## Final theorem shape

Hesse-tube pseudomodularity is controlled by a [39,4,36] dependency geometry over the 35-cut.

The remaining theorem is no longer chart uniqueness. It is an intrinsic characterization of this dependency geometry from the original lasso/tube data.
