# v30 Wu/spin^h and 6j marking certificate

status = `WU_SPINH_OCTAD_SPIN12_6J_MARKING_CERTIFIED_GOLAY_SELECTOR_STILL_EXTERNAL`

sha256 = `0cf932c4883f61044f4f76f234d11f91740a71683fdbb039a93fb76d2a0ffa78`

## Input

The input is the v29 canonical 24-coordinate syzygy frame obstruction layer.  v29 proved that the support-nullspace has dimension 19, restricted bilinear rank 18, and a one-dimensional radical of weight 8.

## Wu/spin^h marking

The radical vector is unique and has weight 8:

```text
Wu octad support = [1, 4, 7, 10, 13, 16, 19, 22]
```

It splits the 24-frame into

```text
8 Wu obstruction coordinates + 16 Spin12/Foam coordinates.
```

The 16-coordinate complement is:

```text
Spin12 complement = [0, 2, 3, 5, 6, 8, 9, 11, 12, 14, 15, 17, 18, 20, 21, 23]
```

Since coordinate 0, the Euler/unit coordinate, lies in the 16-complement, the complement has the exact shape

```text
1 + 15 = 1 + binom(6,2).
```

Thus the finite replacement for the failed Golay selector is now a certified spin^h marking:

```text
W24 = O8^Wu  ⊕  Foam16^Spin12.
```

## Sector profiles

```text
octad intersection histogram:       {'0': 1, '6': 1, '8': 37}
Spin12 complement histogram:        {'8': 1, '9': 1, '13': 1, '16': 36}
K_i octad projection ranks:         {'0': 1, '6': 1, '8': 37}
K_i Spin12 projection ranks:        {'8': 1, '9': 1, '10': 37}
```

Special sectors:

```json
[
  {
    "sector": 35,
    "octad_support_count": 6,
    "spinor_complement_support_count": 13,
    "support": [
      0,
      1,
      2,
      3,
      5,
      6,
      7,
      8,
      9,
      10,
      11,
      13,
      14,
      15,
      16,
      18,
      20,
      22,
      23
    ]
  },
  {
    "sector": 36,
    "octad_support_count": 8,
    "spinor_complement_support_count": 9,
    "support": [
      0,
      1,
      2,
      4,
      5,
      7,
      8,
      10,
      11,
      13,
      14,
      16,
      17,
      19,
      20,
      22,
      23
    ]
  },
  {
    "sector": 37,
    "octad_support_count": 0,
    "spinor_complement_support_count": 16,
    "support": [
      0,
      2,
      3,
      5,
      6,
      8,
      9,
      11,
      12,
      14,
      15,
      17,
      18,
      20,
      21,
      23
    ]
  },
  {
    "sector": 38,
    "octad_support_count": 8,
    "spinor_complement_support_count": 8,
    "support": [
      0,
      1,
      3,
      4,
      6,
      7,
      9,
      10,
      12,
      13,
      15,
      16,
      18,
      19,
      21,
      22
    ]
  }
]
```

## 6j / D6 bridge

The 16-complement is identified with the pure-spinor big cell

```text
Foam16 = 1 ⊕ Λ² H6.
```

with

```text
H6 = ['B-', 'B+', 'V-', 'V+', 'S-', 'S+']
dim Λ²H6 = 15
```

The corresponding D6 counts are:

```text
positive D6 roots:        30
full D6 roots:            60
|W(D6)|:                  23040
|W(D6)| / |Be3|:          5/2
ambient half-spin dim:    32
big-cell dim:             16
```

The all-spin-one tetrahedral scalar is

```text
{1 1 1; 1 1 1} = 1/6
normalized F coefficient = 1/2
```

Over F_1000003 this is

```text
6j = 833336
F  = 500002
```

## Separation refinement

```text
q12 + Wu classes:                   36 / 39
q42 + Wu classes:                   37 / 39
q42 + Wu + Hessian order classes:   38 / 39
q42 + Wu + Hessian discriminant:    39 / 39
```

So Wu/spin^h marking supplies the missing 8+16 obstruction/spinor split, while the final sector separation is still completed by the Hessian discriminant.

## Boundary

This certifies the Wu/spin^h marking and its Spin12/6j carrier. It does not certify a Golay selector. The rank-12 Type-II/Golay code remains external to the current data unless an additional marking is supplied.
