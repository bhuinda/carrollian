# Multilevel Contact Normal Form

## Status

`MULTILEVEL_CONTACT_NORMAL_FORM_CERTIFIED`

Certificate hash:

```text
8ccf663fc8f3a955d1533bc3a47124e1a343ed33bd03a3665007d22f62bb469e
```

## What this does

This is the direct multilevel generalization.

Fix the ordered pair

```text
a=x0 >= b=x1
```

and allow arbitrary positive rest coordinates

```text
x2,...,x23.
```

Define four rest-polynomial coefficients:

```text
C11 = blocks containing 0 and 1
C10 = blocks containing 0 not 1
C01 = blocks containing 1 not 0
C00 = blocks containing neither
```

Then

```text
A = ab C11 + a C10 + b C01 + C00
S = a^2 + b^2 + R
```

where

```text
R = sum over i=2..23 of x_i^2.
```

## Exact formulas

The violation barrier is

```text
B = 24^h A - m S^h.
```

The pair-normal derivative is

```text
D(B)=24^h(a C10-b C01)-m w S^(h-1)(a^2-b^2).
```

The first-difference quotient is

```text
Q=wA(a^2-b^2)-S(a C10-b C01).
```

And the exact contact identity is

```text
24^h Q = w(a^2-b^2)B - S D(B).
```

## Verification

| shell | samples | identity failures | unweighted C11 | C10 | C01 | C00 |
|---:|---:|---:|---:|---:|---:|---:|
| 12 | 64 | 0 | 616 | 672 | 672 | 616 |
| 16 | 64 | 0 | 330 | 176 | 176 | 77 |


## What remains

On the contact surface

```text
B=0,
```

the final proof is exactly the weighted asymmetry bound:

```text
24^h(a C10-b C01) <= m w S^(h-1)(a^2-b^2).
```

This is the full multilevel version. The pair-stabilized proof is the special symmetric case; the real remaining obstruction is weighted asymmetry between `C10` and `C01`.
