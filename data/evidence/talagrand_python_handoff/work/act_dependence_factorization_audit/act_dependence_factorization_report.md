# Actor dependence factorization audit

## Status

`ACT_DEPENDENCE_FACTORIZATION_PASS`

## Test

Use the public shell readout as the actor

```text
Act : C2 -> public three-level shell profiles.
```

This audit verifies two finite facts:

1. every C2 face has a well-defined `Act` profile in the three-level table;
2. every `Act` image of an H2 basis representative is zero or a finite sum of already-certified three-level nonnegative shell gaps.

## Results

| shell | C2 faces | Act profile classes | hash mismatches | uncertified C2 profiles | H2 reps | zero Act images | uncertified Act images |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 12 | 2553 | 1483 | 0 | 0 | 547 | 1 | 0 |
| 16 | 2553 | 1483 | 0 | 0 | 547 | 1 | 0 |


## Consequence

For the audited band, the actor-visible H2 obstruction is closed:

```text
Act(H2) is nonnegative.
```

The remaining distinction is only between raw H2 before actor readout and the shell functional. If the shell functional is accepted as actor-dependent by definition, then this closes the audited H2 obstruction.
