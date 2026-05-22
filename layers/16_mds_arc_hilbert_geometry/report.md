# MDS arc, Hilbert geometry, and quintic wall

```text
status = MDS_ARC_HILBERT_AND_QUINTIC_WALL_CERTIFIED
mds_arc_hilbert_geometry_sha256 =
b1c30c22d1c735714b5a6625d85390b0ed8ed5e5af83b2771209e3750868b09d
```

## Main result

The dependency geometry from v25 is now certified directly as an MDS arc.

```text
4x4 determinants checked:      82251
zero 4x4 determinants:         0
unique determinant values:     78979
Legendre histogram:            {'-1': 41084, '1': 41167}
```

Thus the dependency code is exactly `[39,4,36]` over `F_1000003`, and its dual is `[39,35,5]`.

```text
projective minimum words:      9139
dual minimum circuits:         575757
```

Every 3-sector plane gives a minimum word of weight 36, and every 5-sector subset is a dual circuit.

## Hilbert geometry of the dependency points

The 39 projective dependency points in `PG(3,F_p)` have Hilbert function:

```text
degree:             0   1   2   3   4   5   6   7
monomials:            1   4  10  20  35  56  84 120
Hilbert rank:         1   4  10  20  35  39  39  39
ideal dimension:      0   0   0   0   0  17  45  81
```

There is no quadric, cubic, or quartic surface through the configuration. The first algebraic envelope appears in degree 5:

```text
dim I_5 = 17
```

The degree-5 system generates the next ideal layers:

```text
rank(I5 * variables -> I6):     45 / 45
rank(I6 * variables -> I7):     81 / 81
linear syzygies among quintics: 23
```

The Hilbert numerator is:

```text
[1, 0, 0, 0, 0, -17, 23, -3, -4, 0, 0, 0]
```

Equivalently, the finite point ring has the forced resolution shape:

```text
0 -> R(-7)^3 + R(-8)^4 -> R(-6)^23 -> R(-5)^17 -> R -> A -> 0
```

## Quintic wall for sector observables

Every audited sector observable first appears at homogeneous degree 5 on the dependency `PG(3)`:

```json
{
  "block_dimensions": {
    "5": 1
  },
  "hessian_determinants": {
    "5": 1
  },
  "hessian_discriminants": {
    "5": 1
  },
  "hessian_legendre": {
    "5": 1
  },
  "hessian_monodromy_orders": {
    "5": 1
  },
  "multiplicities": {
    "5": 1
  },
  "permutation_ranks": {
    "5": 1
  },
  "primitive_character_basis_columns": {
    "5": 39
  },
  "q12_signature_columns": {
    "5": 6
  },
  "q42_signature_columns": {
    "5": 12
  },
  "separator_eigenvalues": {
    "5": 1
  }
}
```

So the dependency geometry has a genuine quintic wall:

```text
all tested sector readouts are invisible in degrees <= 4 and appear in degree 5.
```

This includes block dimensions, multiplicities, permutation ranks, Hessian monodromy data, q12/q42 signatures, separator eigenvalues, and all 39 primitive character-basis columns.

## Determinant-volume invariants

```text
determinant product mod p:       199419
determinant product Legendre:    1
power moments mod p:             {'1': 133091, '2': 498487, '3': 293191, '4': 253162, '5': 73868}
```

## Final theorem shape

```text
Hesse-tube pseudomodularity is governed by an MDS 39-arc with a quintic observable wall.
```

Strict modularity remains absent for the raw tube data. The surviving structure is:

```text
35-dimensional Hesse cut <-> [39,4,36] MDS dependency arc <-> degree-5 sector readout geometry.
```
