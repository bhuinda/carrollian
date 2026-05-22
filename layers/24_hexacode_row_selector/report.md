# Hexacode row selector construction

```text
status =
HEXACODE_ROW_SELECTOR_CONSTRUCTED_GOLAY_CERTIFIED_CANONICALITY_EXTERNAL

hexacode_row_selector_sha256 =
f24d9a5f35a9539ae6807af22779d274d08a2f9b97d0c4777af9fb478c2b7a33
```

## Construction

Starting with the intrinsic MOG column code `C_col`, v33 proved that the full row-refined Golay selector is not determined by the column-pair/Wu/6j incidence alone. v34 adjoins the missing row datum as a deterministic hexacode selector: the lexicographically first maximal totally singular 7-plane in `C_col^perp/C_col` containing the current row-pair quotient seed.

Selected quotient basis indices:

```text
[127, 8065, 395, 665, 1187, 2213, 8383]
```

The selector span has size `128` and all nonzero cosets have minimum representative weight at least `8`.

## Certified extended Golay code

```text
generator shape:         [12, 24]
rank:                    12
size:                    4096
self-orthogonal:         True
self-dual:               True
doubly even:             True
minimum nonzero weight:  8
weight histogram:        {'0': 1, '8': 759, '12': 2576, '16': 759, '24': 1}
```

So the constructed code is a Type-II self-dual `[24,12,8]` code with the extended Golay weight enumerator.

It contains:

```text
column-pair code:          True
current row-pair dodecads: True
Wu octad:                  True
active 6j edge code:        True
```

## Hexacode/F4 row labeling

Using the current four rows as the F4 labels `0,1,ω,ω+1`, every codeword has uniform column parity: all columns even or all columns odd.

The even-parity symbol words form a linear `[6,3,4]` hexacode over F4:

```text
even symbol words:          2048
even unique words:          64
even multiplicity histogram:{'32': 64}
even weight histogram:      {'0': 1, '4': 45, '6': 18}
F4 linear:                  True
F4 generator:
[[0, 0, 1, 3, 3, 1], [0, 1, 0, 3, 1, 3], [1, 0, 0, 1, 3, 3]]
```

The odd-parity sector is the paired MOG coset:

```text
odd unique words:           64
odd multiplicity histogram: {'32': 64}
odd weight histogram:       {'2': 3, '3': 8, '4': 18, '5': 24, '6': 11}
```

## Boundary

This constructs and certifies the missing row-refined Golay selector. It does not prove the selector is intrinsic to the column-pair/Wu/6j data alone. v33 already certified that such canonicity is impossible without adjoining row/F4 data.
