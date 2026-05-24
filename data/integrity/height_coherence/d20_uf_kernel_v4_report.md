# D20 UF Kernel v4: height coherence

## Status

`D20_UF_KERNEL_HEIGHT_COHERENCE_CERTIFIED`

## Main correction

The formal certificate is **height coherence**.

Use:

```text
BoxHeight(A_ext, h) := min(A_ext h) > 0
```

A height certificate is a single global height vector that makes every local exterior constraint point forward.

## Certified height-coherence tests

| certificate | nodes | edges | min margin | result |
|---|---:|---:|---:|---|
| `tower_descent_height_coherence` | 4 | 3 | 1 | PASS |
| `six_channel_to_D20_face_height_coherence` | 26 | 60 | 1 | PASS |
| `A42_to_A12_saturated_resizing_height_coherence` | 54 | 42 | 1 | PASS |
| `three_cycle_positive_annihilator_control` | 3 | 3 | -2 | PASS |

## Gordan interpretation

For a realized exterior matrix `A_ext`, Gordan duality gives exactly one of the following:

```text
exists h with A_ext h > 0
```

or

```text
exists nonzero y >= 0 with A_ext^T y = 0
```

The package certifies the positive side for the tower, the six-channel public face layer, and saturated `A42 -> A12` resizing. It also includes a three-cycle negative control with explicit annihilator:

```json
{"y": [1, 1, 1], "A_ext_T_y": [0, 0, 0], "is_positive_annihilator": true}
```

## Saturated quotient guard

The v2 correction is preserved:

```text
A42 -> A12 is valid only after saturation, not as pointwise atom projection.
```

Regression guard:

```text
pointwise atom projection failures = 510
```

Saturated bridge status:

```text
valid_saturated_bridge = True
```

## Kernel update

The judgment layer gains:

```text
Xi; Delta; Sigma; Gamma |- BoxHeight(A_ext,h)
```

with verifier rule:

```text
accept iff every entry of A_ext h is strictly positive.
```

Constructive univalence gate:

```text
equivalence witness + zero transport residue + height coherence
```

## Legacy term mapping

| legacy term | formal term | verifier meaning |
|---|---|---|
| `BoxMonism` | `BoxHeight` | checked global-height certificate |
| positive annihilator | positive circular obstruction | local constraints form a loop and no global height exists |
| saturated resizing | saturated resizing | compress whole fibers, not isolated atoms |
| residue equality | zero readout difference | two handles have the same certified readout |

## Current stack

```text
T985 -> typed normalizer -> saturated quotient resizing -> BoxHeight height coherence
```
