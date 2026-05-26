# e33 Vector and Full Corrected Transport

## Status

`E33_VECTOR_AND_ALL_CORRECTED_TRANSPORTS_CERTIFIED`

Certificate hash:

```text
b1450772bc495a50e83c25ccf7ba570ef092c72bceda8c6fea5005c9785701df
```

## What was computed

This pass reconstructs the explicit sector-33 idempotent vector

```text
e33
```

in the \(985\)-relation basis, then materializes all corrected height-coherent transport vectors

```text
Lambda_hc(mask) = lambda_boundary(mask) - A_h(mask)/2 * e33
```

for all

```text
2048
```

closed-return residue masks.

## e33

| invariant | value |
|---|---:|
| support | 56 |
| positive / negative entries | 28 / 28 |
| signed sum | 0 |
| signed-lift absolute mass | 13343790 |
| identity coefficients | [0, -31250, 0, 0, 0, 492189] |
| B+ local candidate | 3 |
| S+ local candidate | 17 |

The unique central/idempotent combination was:

```text
B+ candidate 3
S+ candidate 17
```

## Corrected transport

| invariant | value |
|---|---:|
| masks | 2048 |
| total sparse corrected entries | 607600 |
| max corrected support | 297 |
| min nonzero corrected support | 237 |

## Gamma-8 check

For mask `256`:

| datum | value |
|---|---:|
| corrected support | 237 |
| corrected signed sum | 53952 |
| corrected signed-lift abs sum | 230880 |

These match the uploaded gamma-8 height-coherent transport report.

## Meaning

The full vector-level \(R_{hc}\) correction is now materialized for the complete 2048-mask residue family.

The previous scalar table supplied the coefficient

```text
-A_h(mask)/2
```

and the previous boundary-to-loop table supplied

```text
lambda_boundary(mask).
```

This package supplies the missing vector

```text
e33
```

and therefore closes

```text
Lambda_hc(mask)
```

at the finite vector level.
