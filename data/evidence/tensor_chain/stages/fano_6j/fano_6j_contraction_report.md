# Fano nullification and the 6j contraction

## Main construction

Nullify the clean Fano point

```text
P0 = 001.
```

Then

```text
F7 \ {001} = {010,011,100,101,110,111}.
```

This six-point residue is exactly the six-edge set of a tetrahedron. The dictionary is:

| Fano point | channel | tetrahedron edge | opposite |
|---|---|---|---|
| `010` | `B-` | `e12` | `B+` |
| `011` | `B+` | `e34` | `B-` |
| `100` | `V-` | `e13` | `V+` |
| `101` | `V+` | `e24` | `V-` |
| `110` | `S-` | `e14` | `S+` |
| `111` | `S+` | `e23` | `S-` |

The three Fano lines through the null point become the three opposite-edge pairs of the tetrahedron. The four Fano lines not through the null point become the four vertex-stars of the tetrahedron.

## Why this is the 6j bridge

A 6j symbol is attached to a tetrahedron with six edge labels. The nullified Fano plane supplies exactly those six labels. Therefore the contraction is

```text
Fano plane + null point  ->  punctured Fano six-set  ->  tetrahedron edge labels  ->  6j symbol.
```

With the uniform compact test label `spin = 1` on all six edges, the Wigner scalar is

```text
{1 1 1; 1 1 1} = 1/6.
```

## Automorphism and signed extension

The stabilizer of the null point inside `GL(3,2)` has order `24` and acts on the six remaining points as the tetrahedral edge action of `S4`. Adjoining even sign flips gives the signed-Fano/D6 tetrahedral preimage:

```text
|S4| = 24
|even sign flips| = 32
|signed-Fano D6 tetrahedral preimage| = 768
|W(D6)| = 23040
index = 30.
```

The contracted six channels also carry the thirty projective `D6` transition roots `[e_i-e_j]` and `[e_i+e_j]`.

## Induced six-channel operator for R_Omega

Using the source_drop Fano-zone weights, I nullified the `P1` mass and split the surviving mass over the six channels:

```text
L3\P1 -> B-, B+
F7\L3 -> V-, V+, S-, S+.
```

Then I compressed the residual curvature matrix by least squares into

```text
R_Omega ≈ B6 · A6 · J6^T.
```

Raw six-channel compression:

- fit energy fraction: `0.007530`
- relative reconstruction error: `0.996228`
- S4-invariant energy fraction: `0.432125`
- S4-breaking energy fraction: `0.567875`
- signed-D6 invariant energy fraction: `0.165612`
- signed-D6 breaking energy fraction: `0.834388`

Normalized non-null six-channel compression:

- fit energy fraction: `0.009561`
- relative reconstruction error: `0.995208`
- S4-invariant energy fraction: `0.427540`
- S4-breaking energy fraction: `0.572460`
- signed-D6 invariant energy fraction: `0.164821`
- signed-D6 breaking energy fraction: `0.835179`

## Tetrahedral orbit coefficients

The `S4`-invariant part of a six-edge operator has three orbit coefficients: same edge, adjacent edges, and opposite edges. For the raw six-channel compression:

| orbit | count | coefficient |
|---|---:|---:|
| `same_edge` | 6 | 142538.619731 |
| `adjacent_edges` | 24 | 55629.401721 |
| `opposite_edges` | 6 | 142538.619731 |

For the normalized six-channel compression:

| orbit | count | coefficient |
|---|---:|---:|
| `same_edge` | 6 | 3420.343196 |
| `adjacent_edges` | 24 | 1318.014057 |
| `opposite_edges` | 6 | 3420.343196 |

## Result

The corrected structure is:

```text
R_Omega is Fano-punctured into a six-edge tetrahedral/6j channel.
The unsigned tetrahedral S4 component is meaningful and computable.
The signed-D6 invariant component is much smaller, so most curvature remains signed-stabilizer-breaking.
```

The remaining missing object is only the original 16-strategy signed permutation action. The Fano-to-6j contraction itself is now constructed.
