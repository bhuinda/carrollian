# v31 MOG resolvent invariant certificate

status = `MOG_RESOLVENT_SEXTET_AND_WU_6J_TETRAHEDRON_CERTIFIED_GOLAY_SELECTOR_STILL_EXTERNAL`

sha256 = `312e4b0a9465c1985b567c979b13103ba37e00c95afb47e6241fa44a8f0b5f24`

## Main result

The canonical 24-coordinate syzygy frame now carries a certified MOG sextet:

```text
MOG grid = 4 x 6
columns = six tetrads of size 4
pair-column octads = 15
```

The certified row-major grid is

```text
[[0, 1, 2, 3, 4, 5], [6, 7, 8, 9, 10, 11], [12, 13, 14, 15, 16, 17], [18, 19, 20, 21, 22, 23]]
```

The v30 Wu radical octad is exactly the union of two MOG columns:

```text
Wu octad = [1, 4, 7, 10, 13, 16, 19, 22]
column pair = [1, 4] = ['B+', 'S-']
```

So the previous 8+16 split is not merely a support split. It is a MOG split:

```text
W24 = two MOG columns  +  four MOG columns
    = 8 Wu coordinates + 16 Spin12/Foam coordinates.
```

## MOG sextet invariants

```text
columns cover 24:                 True
columns pairwise disjoint:         True
pair octads all weight 8:          True
pair-octad intersection histogram: {'0': 45, '4': 60}
each coordinate lies in:           {'5': 24} pair-octads
pair-octad span rank over F2:      5
MOG even-column code weights:      {'0': 1, '8': 15, '16': 15, '24': 1}
```

Thus the six columns give the standard MOG sextet skeleton: every pair of columns is an octad.

## The support-nullspace selects a unique tetrahedron

Among the 15 MOG pair-octads, exactly 6 lie in the v29 support-nullspace:

```text
[['B+', 'V+'], ['B+', 'S-'], ['B+', 'S+'], ['V+', 'S-'], ['V+', 'S+'], ['S-', 'S+']]
```

These six edges form a unique complete graph K4 on the four MOG columns

```text
columns = [1, 3, 4, 5]
labels  = ['B+', 'V+', 'S-', 'S+']
```

Certified graph data:

```text
null-pair graph degrees:       [0, 3, 0, 3, 3, 3]
unique max clique size:        4
unique max clique columns:     [1, 3, 4, 5]
edge set is K4:                True
```

This is the promised 6j object: four vertices and six edge-octads.

## Tetrahedral / 6j edge frame

The tetrahedral vertices are

```text
['B+', 'V+', 'S-', 'S+']
```

The six edge-octads are

```text
[['B+', 'V+'], ['B+', 'S-'], ['B+', 'S+'], ['V+', 'S-'], ['V+', 'S+'], ['S-', 'S+']]
```

Opposite edge pairs are

```text
[(['B+', 'V+'], ['S-', 'S+']), (['B+', 'S-'], ['V+', 'S+']), (['B+', 'S+'], ['V+', 'S-'])]
```

The radical Wu octad is the edge

```text
['B+', 'S-']
```

and its opposite edge is

```text
['V+', 'S+']
```

The K4 edge code is a small Type-II subcode:

```text
rank over F2:          3
code size:             8
weight histogram:      {'0': 1, '8': 6, '16': 1}
doubly even:           True
```

This is not the full Golay code. It is the MOG-resolvent subobject that the data actually selects.

## Spin12 / D6 interpretation

The 15 MOG pair-octads are exactly the unordered pair addresses

```text
Λ²H6,  dim = binom(6,2) = 15.
```

Adding the scalar coordinate gives

```text
1 + Λ²H6 = 16,
```

the Spin12 pure-spinor big-cell carrier already seen in v30.

The signed double of the 15 pair-octads gives the D6 positive-root count:

```text
2 * 15 = 30 positive D6 roots
60 full D6 roots
|W(D6)| = 23040
|W(D6)| / |Be3| = 5/2
```

The all-spin-one tetrahedral scalar remains

```text
6j = 1/6 = 833336 mod 1000003
F  = 1/2 = 500002 mod 1000003
```

## Sector signatures

The K4/tetrahedral edge-octad projections produce five sector classes:

```text
active edge rank unique classes:     5
active edge support unique classes:  5
generic all-edge-full-rank sectors:  35
active edge rank histogram:          {'0': 1, '4': 10, '5': 4, '6': 2, '8': 217}
```

Special sectors:

```json
[
  {
    "sector": 35,
    "active_edge_projection_ranks": [
      5,
      6,
      5,
      5,
      5,
      6
    ],
    "active_edge_support_counts": [
      6,
      6,
      6,
      6,
      6,
      6
    ],
    "active_column_projection_ranks": [
      3,
      3,
      3,
      3
    ],
    "active_column_support_counts": [
      3,
      3,
      3,
      3
    ]
  },
  {
    "sector": 36,
    "active_edge_projection_ranks": [
      4,
      8,
      8,
      4,
      4,
      8
    ],
    "active_edge_support_counts": [
      4,
      8,
      8,
      4,
      4,
      8
    ],
    "active_column_projection_ranks": [
      4,
      0,
      4,
      4
    ],
    "active_column_support_counts": [
      4,
      0,
      4,
      4
    ]
  },
  {
    "sector": 37,
    "active_edge_projection_ranks": [
      4,
      0,
      4,
      4,
      8,
      4
    ],
    "active_edge_support_counts": [
      4,
      0,
      4,
      4,
      8,
      4
    ],
    "active_column_projection_ranks": [
      0,
      4,
      0,
      4
    ],
    "active_column_support_counts": [
      0,
      4,
      0,
      4
    ]
  },
  {
    "sector": 38,
    "active_edge_projection_ranks": [
      8,
      8,
      4,
      8,
      4,
      4
    ],
    "active_edge_support_counts": [
      8,
      8,
      4,
      8,
      4,
      4
    ],
    "active_column_projection_ranks": [
      4,
      4,
      4,
      0
    ],
    "active_column_support_counts": [
      4,
      4,
      4,
      0
    ]
  }
]
```

## Interpretation

The MOG object is now certified as the resolvent invariant:

```text
six MOG columns       -> H6 addresses
15 pair-column octads -> Λ²H6
unique K4 subgraph    -> tetrahedral/6j edge frame
radical edge          -> Wu octad
four-column complement-> Spin12/Foam16 carrier
```

The full Golay selector is still external. What is internal is stronger and sharper than before: the verifier selects a MOG sextet and, inside it, a unique Wu-marked tetrahedral 6j resolvent.
