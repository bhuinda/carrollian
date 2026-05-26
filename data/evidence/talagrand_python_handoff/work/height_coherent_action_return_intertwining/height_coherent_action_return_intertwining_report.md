# Height-Coherent Action-Return Intertwining Target

## Status

`HEIGHT_COHERENT_ACTION_RETURN_INTERTWINING_TARGET_LOCKED`

## What changed

The uploaded compatibility batch proves that the raw multiplication-homomorphism route is wrong.

The correct theorem is not

```text
pi_Foam33(xy) = pi_Foam33(x) pi_Foam33(y).
```

That fails on the full 56-support relation algebra.

The correct theorem is

```text
pi_Foam33 ∘ R_hc = R_Foam ∘ pi_Foam33.
```

So Foam33 must be compatible with height-coherent action-return transport, not bare multiplication.

## Certified facts

| item | value |
|---|---:|
| e33 support | 56 |
| positive / negative entries | 28 / 28 |
| signed coefficient sum | 0 |
| q42/q12 visible count | 0 / 0 |
| all 30 directed pair lifts pi33-zero | True |
| cycle8 support | 193 |
| cycle8 coefficient sum | 53952 |
| cycle8 optical action | 374784 |
| A8 candidate dimension | 8 |
| Lambda^3 A8 candidate | 56 |
| hidden kernel generator index | 6 |
| hidden pair height difference | 903168 |
| basis6 TDO height | 903168 |
| gamma8 height | 374784 |

## Interpretation

Sector 33 is not recovered by bare boundary-to-loop transport.  Bare boundary transport touches the bridge support, but only in a signed-balanced way, so the character/readout vanishes.

The height-coherent layer supplies the missing carrier:

```text
A8 candidate dimension = 8
Lambda^3(A8) = 56
basis-6 invisible primitive height = 903168
gamma8 height = 374784
```

That is exactly the layer where action-return can see what the bare boundary map annihilates.

## Proof obligation now

Construct or load the height/action-return operator `R_hc` and test:

```text
pi_Foam33 R_hc = R_Foam pi_Foam33
```

for every relevant generator.

This is the next finite verifier. It is narrower and cleaner than trying to make `pi_Foam33` into an algebra homomorphism.
