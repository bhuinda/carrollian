# Public shell actor audit

## Status

`PUBLIC_SHELL_ACTOR_AUDIT_PASS`

## Test

Treat the public shell readout as an actor

```text
Act_pub : C2 faces -> public three-level profile IDs
```

that forgets the deletion-face placement/color label and remembers only the public three-level shell profile.

Then apply this actor to each extracted H2 basis representative.

## Results

| shell | H2 dim | public profile coordinates | killed basis reps | surviving reps | image rank |
|---:|---:|---:|---:|---:|---:|
| 12 | 547 | 1483 | 1 | 546 | 541 |
| 16 | 547 | 1483 | 1 | 546 | 540 |


## Interpretation

The hint is only partly right.

A public shell is an actor: it acts on C2 face scenes by forgetting internal placement and reading only the public shell profile.

But this actor does not kill the entire audited H2 sector. It compresses it. The H2 face-residue sector has a much smaller public image, but it is not zero.

So the Talagrand closure is reduced again:

```text
not 547 raw H2 generators,
but the public actor image of H2.
```

The next proof step is to certify nonnegativity or cancellation on this smaller public actor image.
