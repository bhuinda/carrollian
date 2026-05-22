# Lasso uniqueness and pseudomodular invariant audit

```text
status = LASSO_UNIQUENESS_AND_PSEUDOMODULAR_INVARIANT_AUDIT_CERTIFIED
lasso_uniqueness_pseudomodular_audit_sha256 =
eff96af60d1d66ccf7544381e5223341bc00d33d6d9ca0e3ee8145239439fd22
```

## Executive result

Naive lasso uniqueness is **not** the correct theorem.

A deterministic ensemble of 256 rank-10 lasso-character charts was tested. The Hesse mechanism is stable across many charts:

```text
rank-X histogram:                 {'10': 256}
unique cubic-point histogram:      {'37': 8, '38': 48, '39': 200}
unique Hesse-pencil histogram:     {'37': 33, '38': 38, '39': 185}
Plucker-span histogram:            {'35': 256}
strong rank10/unique39/span35:     185/256
```

So the correct conclusion is:

\[
\boxed{\text{lasso chart uniqueness is false without stronger naturality/equivariance constraints.}}
\]

The invariant object is not one special random lasso projection. The invariant object is the **rank-10 Hesse carrier mechanism** and the pseudomodular character algebra it induces.

## Minimality inside the certified v23 chart

Deleting any one of the 10 coordinates preserves point separation but destroys the full 35-dimensional Hesse span:

```text
rank after deleting one coordinate:       {'9': 10}
unique cubic points after deletion:       {'39': 10}
Plucker span after deletion:              {'30': 3, '32': 7}
unique pencils after deletion:            {'39': 10}
every deletion loses full 35-span:         True
```

Thus all 10 coordinates are needed for the **full Hesse cut**, even though 9-coordinate projections can still separate the 39 points.

## Stabilizer rigidity

The certified v23 configuration itself is rigid:

```text
labeled projective-point stabilizer A-dimension:  1
labeled point stabilizer scalar-only:             True
labeled Hesse-pencil stabilizer A-nullity:        1
labeled pencil stabilizer scalar-only:            True
```

So there is no hidden continuous/projective gauge symmetry left in the labeled 39-sector configuration.

## Hessian dynamics invariants

For each sector, write

\[
H(H(X_i))=\alpha_i X_i+\beta_i H(X_i).
\]

The closure pairs distinguish all 39 sectors:

```text
unique (alpha,beta) closure pairs:       39
unique beta traces:                      39
unique -alpha determinants:              39
unique discriminants:                    39
discriminant Legendre histogram:         {'-1': 22, '1': 17}
```

This gives a new 39-sector invariant independent of the previous q42/q12 signatures.

## Surface trace refinement ladder

```text
A12 signature classes:       35
A12 partition histogram:     {'1': 33, '3': 2}
A12 nonsingletons:           [[5, 22, 38], [16, 24, 34]]

A42 signature classes:       37
A42 partition histogram:     {'1': 36, '3': 1}
A42 nonsingletons:           [[16, 24, 34]]

A42 + secondary classes:     39
```

The sector separation ladder is:

```json
{
  "block_dimension_only": 11,
  "block_dimension_plus_multiplicity": 27,
  "block_dimension_plus_multiplicity_plus_permutation_rank": 27,
  "A12_signature": 35,
  "A42_signature": 37,
  "A42_plus_secondary_separator": 39,
  "Hessian_closure_pair": 39,
  "Hesse_cubic_projective_points": 39,
  "Hesse_projective_pencils": 39
}
```

## Quantum-character orthogonality

The A42+secondary lasso-character matrix is invertible over \(\mathbb F_{1000003}\):

```text
basis shape:                 [39, 39]
basis rank:                  39
left inverse check:           True
right inverse check:          True
```

This is the finite analogue of generalized tube-character orthogonality: representation-basis sectors and lasso/surface-basis insertions are related by an exact invertible character transform.

## Pseudomodular Verlinde algebra

The induced pointwise product algebra on the 39 lasso-character idempotents has:

```text
multiplication tensor:              [39, 39, 39]
multiplication support:             39
coefficients zero-one:              True
commutative:                        True
associativity failures:             0
identity support:                   39
identity laws failures:             0
split F_p^39 pointwise algebra:      True
```

So the replacement for strict modular Verlinde data is not an ordinary modular \(S,T\) pair. It is the split pseudomodular character algebra

\[
\boxed{\mathbb F_p^39}
\]

with 39 orthogonal primitive character idempotents.

## Final correction

Strict modularity remains dead for the current raw tube data. The new theorem shape is:

\[
\boxed{\text{Hesse-tube pseudomodularity}}
\]

consisting of:

\[
\text{rank-10 Hesse carrier}
+\text{35-dimensional A12/Hesse cut}
+\text{39-sector quantum-character orthogonality}
+\text{split pseudomodular Verlinde algebra}.
\]

The open theorem is no longer naive lasso uniqueness. It is **intrinsic carrier uniqueness**: prove which naturality/equivariance constraints select an equivalence class of rank-10 lasso carriers from the large family certified above.
