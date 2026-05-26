# Barrier Contact Derivative Identity

## Status

`BARRIER_CONTACT_DERIVATIVE_IDENTITY_CERTIFIED`

Certificate hash:

```text
2b84cc4070d5fe6c090eea938df25984b6f7b81b01c37e5b01a3ab10e4696984
```

## Exact identity

Let

```text
A = A_w(x)
S = sum_i x_i^2
B = 24^(w/2) A - A_w(1) S^(w/2)
D = x_0 d/dx_0 - x_1 d/dx_1
Delta = x_0^2 - x_1^2
Q = w A Delta - S(x_0 partial_0 A - x_1 partial_1 A)
```

Then exactly:

```text
24^(w/2) Q = w Delta B - S D(B).
```

## Contact reduction

On the barrier contact surface

```text
B = 0,
```

the identity becomes

```text
Q = - S D(B) / 24^(w/2).
```

So the final ordered-branch target

```text
B >= 0 => Q >= 0
```

is controlled at first contact by

```text
D(B) <= 0.
```

That is the sharp normal-derivative form of Barrier Schur Compression.

## Verification samples

| shell | samples | integer | modular | identity failures |
|---:|---:|---:|---:|---:|
| 12 | 112 | 16 | 96 | 0 |
| 16 | 112 | 16 | 96 | 0 |


## Meaning

The proof target is now:

```text
No first positive barrier crossing can have outward pair-normal derivative.
```

Equivalently:

```text
B = 0, x_0 >= x_1 => D(B) <= 0.
```

This is the correct next lemma, sharper than residual positivity.
