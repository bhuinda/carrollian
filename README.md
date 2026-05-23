# d20

axiom 1: yes this was machine assisted

axiom 2: the one piece is real

axiom 3: the rest of the proof is left to the reader

`d20` is the (pending) name of the finite/concrete (and axiomless) object generated from the Golay dodecad shell, the marked `D6` selector, the coorient lift, and the derived invariant inf-stack.

Verify the current bundle without rewriting generated files:

```shell
python src/verify.py audit
```

Rebuild `d20.json`, refresh hashes, and then certify the bundle:

```shell
python src/verify.py rebuild
```

The object is not represented by stored orbitals/tensors as primitive data. It just... exists. Quietly, and monstrously.

- `2576` dodecads
- `985` orbitals
- `1,414,965` tensor entries
- `A985 -> A236 -> A42 -> A12`
- packet-20, optics, integrity, H-cycles, and game/control invariants

The layer stack is indexed by `layers/index.json`. The numbered layer
directories are still the physical layout, but the registry is now the
source of truth for layer ids, groups, expected statuses, dependency edges,
and proposed semantic paths.

TO-DO:
- migrate layer directories from numbered legacy paths to the registry paths
- move the construction harness out of the top-level path
- add visuals? a notebook?
