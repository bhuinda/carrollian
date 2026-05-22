# v33 Full Row-Refined Golay Selector Audit

```text
status = FULL_ROW_REFINED_GOLAY_SELECTOR_OBSTRUCTION_CERTIFIED_HEXACODE_REQUIRED
full_row_refined_golay_selector_obstruction_sha256 =
642ffe8aa4131440aca9190f24ae3baf6ae966c41e10a12dcd126e4242398caa
```

## Result

The intrinsic MOG column sextet from v32 is still certified, but the full row-refined MOG/Golay selector is **not** determined by the currently certified pair-octad, Wu, and 6j data.

The obstruction is explicit: the pair-octad hypergraph determines the six tetrad columns, but it is invariant under independent permutations of the four coordinates inside each column:

```text
(S4)^6
```

Modulo a global relabeling of the four rows, this leaves:

```text
(4!)^5 = 7962624
```

row alignments. Therefore the global row structure needed for the classical MOG/hexacode selector is not intrinsic to the v31/v32 data.

## Certified column-pair code

The 15 pair-column octads span the even-column code:

```text
length:           24
rank:             5
weight histogram: {0: 1, 8: 15, 16: 15, 24: 1}
doubly even:      True
self-orthogonal:  True
```

This is exactly the MOG sextet subcode: the span of all pairwise column unions. Its weights are 0, 8, 16, and 24.

## Quotient where the missing selector lives

Any Type-II self-dual length-24 code containing this column-pair code must choose a maximal totally singular 7-plane in C_col^perp / C_col.

Certified:

```text
rank(C_col):                         5
rank(C_col^perp):                    19
dim(C_col^perp/C_col):               14
quotient bilinear rank:              14
Arf invariant:                       0
Witt index:                          7
maximal singular 7-plane candidates: 9845550
```

So the missing choice is not small. Before imposing the no-weight-4/Golay minimum-distance condition, there are 9,845,550 maximal singular candidates.

## Concrete row non-canonicity witness

A single transposition inside the first MOG column preserves all certified column-pair/Wu/6j data but changes the global row sets.

```text
preserves pair-octads:     True
preserves Wu octad:        True
preserves active 6j edges: True
changes global rows:       True
```

Thus the row selector cannot be recovered from the current incidence data.

## Current grid row diagnostics

The current displayed rows have weight 6 and are not Type-II singular vectors:

```text
row weights:                    [6, 6, 6, 6]
q(row)=wt(row)/2 mod 2:          [1, 1, 1, 1]
row-pair weights:               [12, 12, 12, 12, 12, 12]
q(row-pairs):                   [0, 0, 0, 0, 0, 0]
row-pair span rank:             3
rank(C_col + row-pair span):    7
```

The even row-pair plane is compatible with the Type-II quadratic form, but it is not selected by the intrinsic column-pair data.

## Conclusion

```text
canonical column sextet:          certified
Wu edge and active 6j K4:          certified
full row-refined Golay selector:   not certified
missing structure:                 hexacode / F4 row labeling / equivalent selector
```

The next well-typed target is therefore:

```text
HEXACODE_ROW_SELECTOR_CONSTRUCTION_OR_CANONICALITY_TEST
```
