# Talagrand Boundary AM-GM Sieve

## Status

`TALAGRAND_BOUNDARY_AMGM_SIEVE_COMPLETE`

Certificate hash:

```text
2383b458fdd42f0b457eda492df96182747c23b05fa39b6c1da2458cf7020d7a
```

## Bound

For a support face \(S\), let \(N_S\) be the number of Golay shell blocks contained in \(S\).

For \(x\) supported on \(S\),

```text
A_S(x) <= N_S (||x||_2^2 / w)^(w/2).
```

So the target

```text
A_w(x) <= A_w(1) (||x||_2^2/24)^(w/2)
```

is certified whenever

```text
N_S <= A_w(1) (w/24)^(w/2).
```

## Results

| shell | threshold N_S | certified supports | uncertified supports | uncertified support range |
|---:|---:|---:|---:|---|
| 12 | 40.250000000000 | 16721761 | 55455 | 19..24 |
| 16 | 29.614997713763 | 16776915 | 301 | 22..24 |


## Meaning

For `w=12`, this rigorous sieve certifies every support of size at most 18.

For `w=16`, it certifies every support of size at most 21.

So the boundary problem has been narrowed to high-support faces only:

```text
w=12: support sizes 19..24
w=16: support sizes 22..24
```

This does not finish Talagrand, but it removes the small and medium boundary strata from the remaining proof debt.
