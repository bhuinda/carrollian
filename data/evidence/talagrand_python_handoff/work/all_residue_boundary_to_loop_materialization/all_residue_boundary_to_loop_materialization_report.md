# All-Residue Boundary-to-Loop Vector Materialization

## Status

`ALL_RESIDUE_BOUNDARY_TO_LOOP_VECTORS_MATERIALIZED_PASS`

Certificate hash:

```text
73553f0b77bf91647729fa28472c62b50d846ab6a7f916eb5d1ddecb96045926
```

## What this computes

This pass uses the uploaded raw multiplication tensor

```text
T_985.npz
relation_memberships.npz
```

to materialize the bare boundary-to-loop vectors

```text
lambda_boundary(r -> a) = sum_{alpha:r->a, beta:a->r} alpha beta
```

for all 30 directed object-pair lifts.

It then builds:

```text
11 primitive H-cycle lambda vectors
2048 all-mask lambda vectors
```

by summing the directed object-pair lifts along each closed-return cycle.

## Result summary

| invariant | value |
|---|---:|
| directed object-pair lifts | 30 |
| primitive basis cycles | 11 |
| all residue masks | 2048 |
| gamma8 lambda support | 193 |
| gamma8 lambda coefficient sum | 53952 |
| full-mask lambda support | 297 |
| full-mask lambda coefficient sum | 1512352 |
| max lambda support | 297 |

## Gamma-8 check

For mask `256`, the computed vector has:

```text
support = 193
sum     = 53952
```

matching the certified cycle-8 boundary-to-loop report.

## Boundary

These are bare `lambda_boundary` vectors.

The height-corrected vector is

```text
Lambda_hc(mask)=lambda_boundary(mask)-height(mask)/2 * e33.
```

The scalar correction for every mask was already reconstructed in the previous package. This package supplies the missing bare lambda rows for all masks. Full corrected 56-coordinate hidden-sector vectors still require the explicit e33 coordinate vector.
