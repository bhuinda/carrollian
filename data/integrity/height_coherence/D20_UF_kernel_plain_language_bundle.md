# The D20 proof-kernel bundle in plain language

## One-sentence summary

D20 is a finite proof-kernel prototype: it composes relations, compresses them safely, and accepts a comparison only when a global height certificate proves that no positive circular obstruction remains.

## The parts

- `A985` is the full multiplication table.
- `T985` is the raw list of allowed two-step compositions.
- `A42` is the signed routing layer.
- `A12` is the final small readout layer.
- `D20 = Lambda^3 H6` is the 20-state public interface generated from six channels.
- The normalizer reduces expressions to standard forms.
- Saturated resizing compresses whole fibers, not isolated atoms.
- Height coherence means one global height vector orients all local exterior constraints.
- A positive annihilator is a circular obstruction.

## Formal rule

```text
BoxHeight(A_ext,h) accepts iff A_ext h > 0 entrywise.
```

## Why this matters for foundations

- Higher coherence becomes finite obstruction clearance.
- Resizing becomes certified quotient descent.
- Constructive univalence becomes reversible translation plus zero residue plus height coherence.

## Terminology fix

Use `height coherence` in papers and code.

The phrase `monism` is only an internal reading: a height certificate witnesses one coherent global orientation. It is not the formal certificate name.
