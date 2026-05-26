# Hamming-Gaussian Entropy Residue and Spin^h Veronese Bridge

## Status

`ENTROPY_SPINH_VERONESE_BRIDGE_CONSTRUCTED_WITH_OPEN_ENTROPY_RESIDUE`

Certificate hash:

```text
8dc5edf77f2cedd774ecbce9d25a259b6c98a7bb3d8ea7c7997246c063b2d4f6
```

## 1. Entropy residue

The remaining Hamming/Golay-to-Gaussian proof residue is the shell entropy contraction

```text
D(q || u_B) >= (w/2) D(p_q || u_24)
```

for the Golay shells `w=12,16`, where `q` is a probability law on shell blocks and `p_q` is the coordinate-inclusion marginal.

Equivalently, in polynomial form:

```text
A_w(x) <= A_w(1) ((1/24) sum_i x_i^2)^(w/2),   x_i >= 0.
```

The important retyping is that this is not an ambient spectral problem. It is a **Veronese-constrained** problem:

```text
y_I = prod_{i in I} x_i.
```

The spectral ghost vectors found in earlier audits exist because the relaxation left the Veronese cone.

## 2. Spin^h Veronese construction

The requested 5-dimensional geometry / Spin^h map is constructed at the representation level.

Let

```text
E = R^3,
W = Sym^2_0(E).
```

Then `dim W = 5`, and the map

```text
nu: RP^2 -> S(W) ~= S^4
```

is

```text
nu([n]) = sqrt(3/2)(nn^T - I/3).
```

This is the degree-2 Veronese surface in the 5-dimensional traceless-symmetric tangent representation. It is even under `n -> -n`, so it descends from `S^2` to `RP^2`.

## 3. Numerical representation checks

| check | value |
|---|---:|
| max SO(3)-equivariance error | `1.146e-15` |
| max orthogonality/determinant error | `4.663e-15` |
| max representation homomorphism error | `6.829e-16` |
| max Veronese norm error | `3.331e-16` |
| max evenness error | `0.000e+00` |
| minimum differential rank | `2` |
| max spin-2 character error | `1.776e-15` |

So the local model `Sym^2_0(R^3)` is numerically certified as the correct 5-dimensional SO(3)-equivariant Veronese target.

## 4. Spin^h bundle map

For the Wu-type homogeneous geometry

```text
M = SU(3)/SO(3),
```

the tangent model is

```text
TM ~= P x_SO(3) Sym^2_0(R^3).
```

The Spin^h candidate is the diagonal structure-group map

```text
SO(3) -> SO(5) x SO(3),
h |-> (Sym^2_0 h, h).
```

The obstruction ledger is

```text
w2(TM) + w2(E_gauge) = 0 mod 2.
```

This is the Spin^h cancellation: the same SO(3) holonomy that obstructs ordinary spin is paired with the gauge SO(3) factor.

## 5. Interpretation

The entropy problem and the Spin^h construction now share the same warning:

```text
do not prove in the ambient linear relaxation; prove on the Veronese image.
```

For Golay shell domination, the Veronese image is

```text
y_I = prod_{i in I} x_i.
```

For the 5-dimensional Spin^h geometry, the Veronese image is

```text
[n] |-> sqrt(3/2)(nn^T-I/3).
```

Both are constrained quadratic/monomial lifts. The next real target is still the finite entropy contraction inequality for `w=12,16`, but the Spin^h construction gives the correct geometric model for why the Veronese constraint is load-bearing.
