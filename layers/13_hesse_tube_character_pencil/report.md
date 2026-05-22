# Hesse-tube character pencil certificate

```text
status = HESSE_TUBE_CHARACTER_PENCIL_CERTIFIED
hesse_tube_character_pencil_sha256 =
bcd0eef12daf5c11d3e5e9b8edc52c323b2ce9f190ac75e5dddd3ba4a2e71cf1
```

## Construction

Use the v22 full relation-pairing table

```text
full_relation_pairing: 39 x 985
```

and form a deterministic 10-coordinate lasso-character chart by a SHA-stable finite-field projection:

```text
field: F_1000003
projection seed: 98765
projection sparsity per coordinate: 32
projection shape: 985 x 10
projection nonzero entries: 320
projection rank on 39 sectors: 10
```

Each Drinfeld sector i gives a cubic-coordinate vector

\[
X_i\in\mathbb F_{1000003}^{10}.
\]

Apply the ternary-cubic Hessian transform

\[
H_{\rm tube}(X_i)=\operatorname{Hess}(X_i)
\]

using the normalized plane-cubic basis

\[
a_0x^3+3a_1x^2y+3a_2x^2z+3a_3xy^2+6a_4xyz+3a_5xz^2+a_6y^3+3a_7y^2z+3a_8yz^2+a_9z^3.
\]

## Certified checks

```text
cubic coordinate rank:                  10
hessian coordinate rank:                10
all Hessians nonzero:                   True
line rank histogram:                    {'2': 39}
H(H(X)) in <X,H(X)> for all sectors:    True
unique projective cubic points:         39
unique Hesse pencils:                   39
```

## Hesse invariant cut

For each sector, form the Plücker vector

\[
p_{ij}=X_i^{(i)}H_{\rm tube}(X_i)^{(j)}-X_i^{(j)}H_{\rm tube}(X_i)^{(i)}.
\]

Then the ten Hesse linear equations

\[
n(p_{ij})=0
\]

all vanish.

```text
Plucker coordinates per pencil:         45
Plucker quadrics per pencil:            210
all Plucker quadrics vanish:            True
Hesse linear equations:                 10
Hesse linear constraint rank:           10
Hesse linear cut dimension:             35
all Hesse R residuals vanish:           True
sampled Plucker span rank:              35
sampled span equals full cut dimension: True
```

So the 39 sector pencils do not merely lie in the finite Hesse cut; they span the entire 35-dimensional Hesse-linear component inside \(\Lambda^2(\mathbb F^{10})\).

## Compatibility with v22 trace layers

```text
A12 trace algebra dimension:             35
A42 trace algebra dimension:             37
A42 + secondary trace algebra dimension: 39
Hesse linear cut dimension:              35
```

The new match is:

\[
\boxed{\dim A_{12}^{\rm trace}=35=\dim \ker(n:\Lambda^2\mathbb F^{10}\to\mathbb F^{10}).}
\]

This is the first certified Hesse-pattern cut in the Drinfeld/tube stack.

## Boundary

This is not a modular \(S,T\) datum. It is a finite Hesse-penciling of the boundary-tube quantum-character table. The construction supplies a valid invariant pencil layer for the 39 Drinfeld sectors and gives the correct 35-dimensional Hesse cut that v22 was pointing at.
