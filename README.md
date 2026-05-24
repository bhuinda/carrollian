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

Check that the certified-evidence section fails closed under in-memory tampering:

```shell
python src/verify.py tamper
```

Computability boundary:

- `python src/verify.py rebuild` regenerates `d20.json`, `certificate.json`, and
  file hashes from the checked canonical bundle inputs.
- `python -m src.commands.construct` reconstructs the finite object from the
  compact raw seed boundary and verifies the large tensor/quotient consequences.
- `python -m src.commands.construct --strict-scratch` runs the generated
  source/coorient constructor path and exits nonzero if any scratch witness,
  tensor rebuild, or readout derivation fails.
- The A985 ordered-pair relation body is refreshed before the coorient marker
  computation by the pre-A985 source/coorient theorem. The coorient relator
  profile is derived from A0-A5 by reduced greedy full-closure basis extraction;
  strict-scratch now promotes that generated path instead of the compact raw
  audit-seed witness.

The object is not represented by stored orbitals/tensors as primitive data. It just... exists. Quietly, and monstrously.

- `2576` dodecads
- `985` orbitals
- `1,414,965` tensor entries
- `A985 -> A236 -> A42 -> A12`
- packet-20, optics, integrity, H-cycles, and game/control invariants
- `data/index.json` is the canonical data-domain registry. It marks current
  folders, required files, roles, and the planned normalized layout.
- `data/evidence/tensor_chain` contains the extracted tensor-chain evidence,
  split into reports, tables, arrays, and stages with a plain-name index at
  `data/evidence/tensor_chain/index.json`.
- Command entrypoints live in `src/commands/`; root command files are not kept.

The layer stack is indexed by `layers/index.json` and stored as flat JSON files
inside semantic group directories such as `layers/tube`, `layers/drinfeld`, and
`layers/selectors`. The registry is the source of truth for layer ids, legacy
numbering, expected statuses, dependency edges, and certificate paths.

TO-DO:
- add visuals? a notebook?
- 
<img width="730" height="721" alt="Image" src="https://github.com/user-attachments/assets/6c701518-37a9-4129-97b2-58e29663a352" />
