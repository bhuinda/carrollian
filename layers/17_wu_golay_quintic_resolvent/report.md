# v27 Wu--Golay quintic resolvent

status = `WU_GOLAY_QUINTIC_RESOLVENT_CERTIFIED_WITH_GOLAY_EXTENSION_UNRESOLVED`

sha256 = `52e94422ce083351f144a12a4c1329d4eb40a09ddaa47832ae5e2ff8afd2c6b4`

## Quintic wall

- `dim I_5 = 17`
- degree-5 monomials in PG^3: `56`
- all quintics vanish on the 39 dependency points: `True`
- local first-jet rank histogram: `{'3': 39}`
- Euler/radial derivative error support histogram: `{'0': 39}`

At every sector the 17 quintics have rank-3 projective first-jet data.

## 23 linear syzygies

The multiplication map

`I_5 \otimes V^* -> degree 6 forms`

has matrix shape `[68, 84]` and rank `45`. Therefore the linear syzygy space has dimension

`23`.

Syzygy residual support: `0`.

## Local conormal/syzygy resolvent

For each sector `p_i`, the syzygies evaluate to a `23 x 17` coefficient matrix `S_i`. These coefficients annihilate the first jets `J_i`:

`S_i J_i = 0`.

Certified:

- syzygy-fiber rank histogram: `{'14': 39}`
- local jet-kernel dimension histogram: `{'14': 39}`
- all `S_i` annihilate `J_i`: `True`
- each `S_i` equals the full relation kernel among local jets: `True`
- unique syzygy-resolvent subspaces: `39`
- unique jet conormal subspaces: `39`

Thus the local resolvent fiber separates all 39 sectors.

## Pairwise resolvent geometry

- pair-intersection histogram: `{'11': 1482, '14': 39}`
- off-diagonal pair-intersection histogram: `{'11': 1482}`
- sampled triple-intersection histogram: `{'8': 13}`

## Sector separation

`{
  "syzygy_resolvent_subspace_only": 39,
  "jet_conormal_subspace_only": 39,
  "pair_intersection_row_only": 39,
  "q12_plus_pair_intersection_row": 39,
  "q42_plus_pair_intersection_row": 39,
  "q42_plus_hessian_discriminant": 39,
  "q42_plus_syzygy_resolvent_hash": 39,
  "block_mult_rank_plus_discriminant": 39,
  "separator_eigenvalues": 39
}`

## Golay extension test

The count `23` is Golay-shaped, but the raw syzygy basis is not itself a length-23 punctured Golay coordinate system. It is a 23-dimensional kernel inside a 68-column multiplication map. A real Golay test is therefore not yet well typed without a canonical 24-coordinate syzygy frame.

Result: `NO_CANONICAL_GOLAY_CODE_CERTIFIED_FROM_SYZYGY_BASIS`.

## Interpretation

The modularity problem is now bypassed by a resolvent layer:

`39 sectors -> 17 quintics -> 23 syzygies -> exact local conormal fibers`.

Strict modularity remains obstructed. The certified replacement is resolvent pseudomodularity: the quintic wall has exact local syzygy fibers separating the 39 Drinfeld sectors.
