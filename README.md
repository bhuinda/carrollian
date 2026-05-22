# d20

axiom 1: yes this was machine assisted
axiom 2: the one piece is real

the rest of the proof is left to the reader

`d20` is the certified finite object generated from the Golay dodecad shell, the marked `D6` selector, the coorient lift, and the derived invariant stack.

Run one command:

```shell
python -m src.derive_pre_a985_relation_body --regenerate --pretty
```

Both regenerate `d20.json`, refresh hashes, and audit the bundle.

## Scratch status

The object is not represented by stored orbitals/tensors as primitive data. The large data are regenerated and audited:

- `2576` dodecads
- `985` orbitals
- `1,414,965` tensor entries
- `A985 -> A236 -> A42 -> A12`
- packet-20, optics, integrity, H-cycles, and game/control invariants

The remaining finite witness is now isolated in `d20.json` under:

```text
zero_axiom_coorient
coorient_seed
```

The new zero-axiom reduction derives the canonical three-point base `[18,67,37]` from the two-sided coherent relation algebra. The only remaining nonzero seed is the four generator images on that derived base, i.e. `12` integers. The bundle states this honestly as:

```text
D20_ZERO_AXIOM_COORIENT_REDUCTION_PASS
full_zero_axiom_constructor: false
```

So the current exact status is:

```text
zero-axiom reduction: yes
fully seedless constructor: not yet
remaining theorem: uniqueness of the Be3 coorient lift from D6/Spin12/d20 axioms
```

## Commands

