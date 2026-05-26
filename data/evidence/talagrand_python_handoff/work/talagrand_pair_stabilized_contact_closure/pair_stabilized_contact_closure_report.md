# Pair-Stabilized Contact Derivative Closure

## Status

`PAIR_STABILIZED_CONTACT_DERIVATIVE_CLOSED_EXACT`

Certificate hash:

```text
1307212822b2afc236e07a18fdf3879cd9d9afec64f340d24f558908eacb702d
```

## What this proves

Restrict to the pair-stabilized three-level family:

```text
x = (A,B,1,...,1).
```

Let

```text
B_w = 24^(w/2) A_w - A_w(1) S^(w/2)
```

be the violation barrier.

The contact derivative target is:

```text
B_w=0, A>=B => D(B_w)<=0,
D=A d/dA - B d/dB.
```

## Exact closure

The negative barrier gap

```text
Gap = -B_w
```

factors as

```text
Gap = (u-1)^2 Q(u) + v^2 R(u,v^2)
```

under

```text
A=u+v, B=u-v.
```

For both shells, all coefficients of `Q` and `R` are strictly positive.

Therefore, for `A,B>=0`,

```text
Gap=0 => u=1 and v=0 => A=B=1.
```

At that point,

```text
D(B_w)=0.
```

## Certified rows

| shell | Q min | R min | contact set | D(B) at contact |
|---:|---:|---:|---|---:|
| 12 | 164864 | 164864 | equal point | 0 |
| 16 | 194304 | 194304 | equal point | 0 |


## Meaning

The contact derivative lemma is now exactly closed on the pair-stabilized slice.

The remaining proof debt is only the arbitrary multilevel contact case.
