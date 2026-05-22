# v29 quadratic / Golay selector obstruction audit

status = `QUADRATIC_GOLAY_SELECTOR_OBSTRUCTION_CERTIFIED`

sha256 = `89f5bcf84e30b49a15d68addafe6ce1f69c7d5800b20d314cd7cb37cf639958d`

## Input

The input is the v28 canonical 24-coordinate frame

`W24 = <Euler_unit> direct_sum Syz_1(I)_6`.

Each of the 39 sectors has a 10-dimensional extended kernel `K_i^+` inside `W24`.

## Kernel-isotropy selector tests

A natural Golay selector would be a quadratic/isotropic structure on `W24`.  I tested the strongest direct version: require all 39 sector kernels to be totally isotropic.

| form type | field | variables | constraints | rank | nullity |
|---|---:|---:|---:|---:|---:|
| symmetric | F_1000003 | 300 | 2145 | 300 | 0 |
| alternating | F_1000003 | 276 | 1755 | 276 | 0 |
| symmetric | F_2 | 300 | 2145 | 300 | 0 |
| alternating | F_2 | 276 | 1755 | 276 | 0 |

Result: no nonzero form exists in any of these four natural selector systems.

So the sector-kernel family does not itself carry a hidden symmetric/alternating form that selects Golay.

## Binary support-incidence audit

The sector coordinate-support matrix has rank `5` over F_2, so its nullspace has dimension `19`.

Restricted to this nullspace, the standard Type-II quadratic form `q(x)=wt(x)/2 mod 2` has:

- bilinear rank: `18`
- radical dimension: `1`
- radical weights: `[8]`
- Arf invariant on the quotient: `0`
- maximum totally singular dimension: `10`

Therefore the support-incidence nullspace cannot contain a rank-12 Type-II/self-dual Golay code.

## Consequence

The v28 `W24` frame is correct, but the Golay layer is not selected by naive binary reduction, sector support, or total-isotropy of the 39 sector kernels.

The precise result is:

`Golay selector not constructed; natural quadratic/isotropic selectors obstructed.`

The next object must be an additional Wu/spin^h marking or an external Golay marking compatible with the certified `W24` frame.

## Invariant interpretation

This is a real obstruction, not a timeout:

`24 = 23 + Euler` is certified,

but

`24 -> Golay [24,12,8]`

requires more than the present syzygy-frame geometry.
