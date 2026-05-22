# v28 canonical 24-coordinate syzygy frame

status = `CANONICAL_24_COORDINATE_SYZYGY_FRAME_CERTIFIED_GOLAY_SELECTION_STILL_OPEN`

sha256 = `1164fc0ae884ec7fd3bce24ecde7f07264298aa786d82fb3fa05562c77298c1b`

## Construction

The canonical frame is

`W24 = <Euler_unit> direct_sum Syz_1(I)_6`.

Coordinates:

- coordinate 0: `Euler_unit`
- coordinates 1..23: the certified 23 linear syzygy coordinates `sigma_00..sigma_22`

The embedded frame has shape `[24, 69]`: one added Euler coordinate plus the original 68 multiplication coordinates of `I_5 tensor V^*`.

## Exact sector sequence

For each sector `i`, define

`ev_i_tilde: W24 -> F^17`

by sending the Euler coordinate to zero and using the evaluated syzygy coefficient matrix on the 23 syzygy coordinates.

Certified:

- rank histogram: `{'14': 39}`
- kernel dimension histogram: `{'10': 39}`
- quotient dimension histogram: `{'14': 39}`
- exact sequence errors: `{'0': 39}`

Thus each sector carries an exact sequence

`0 -> K_i^+ -> W24 -> S_i -> 0`

with

`dim K_i^+ = 10`, `dim W24 = 24`, `dim S_i = 14`.

## Kernel geometry

Unextended kernels inside the 23-syzygy space:

- `dim K_i = 9`
- off-diagonal pair intersection histogram: `{'0': 1482}`

Extended kernels inside `W24`:

- `dim K_i^+ = 10`
- off-diagonal pair intersection histogram: `{'1': 1482}`
- triple distinct common intersection histogram: `{'1': 9139}`

So distinct sector kernels meet exactly in the common Euler line.

## Dual image geometry

The v27 image-side relation spaces satisfy:

- local relation dimension: `14`
- ambient relation dimension: `17`
- off-diagonal image intersection histogram: `{'11': 1482}`

This is the `11` overlap layer: `dim(S_i cap S_j)=11` for `i != j`.

## Golay audit

The frame is now genuinely length 24, but naive binary reduction is not the extended Golay code:

- binary extended-kernel row-span rank: `24`
- sector support binary rank: `5`
- support weight histogram: `{'16': 2, '17': 1, '19': 1, '24': 35}`

Result: raw mod-2 reduction spans too much. The next missing invariant is a quadratic/isotropic selector on `W24` that cuts out a rank-12 doubly-even self-dual binary subspace, if one exists.
