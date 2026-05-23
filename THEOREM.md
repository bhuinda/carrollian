# d20 Theorem Ledger

This file is the short, human-readable contract for the verifier. It separates
the central finite object from the derived reports and from bundle hygiene.

## Core Object

`d20` is the finite object whose core algebra is `A985`.

The core construction is:

1. Build `H8 = RM(1,3)`.
2. Build `C0 = H8^3` inside `F2^24`.
3. Apply the three Type-II neighbor operations and verify the root sequence
   `42 -> 18 -> 6 -> 0`.
4. Enumerate the 2,576 dodecads of the generated Golay endpoint.
5. Apply the lifted coorient action of order 9,216.
6. Take the 985 ordered-pair orbitals on `Omega x Omega`.
7. Build the sparse multiplication tensor `T985` by two-step incidence.

The resulting relation algebra has:

- `|Omega| = 2576`
- `985` relations
- `1,414,965` nonzero tensor rows
- total tensor coefficient mass `2,537,360`
- center dimension `39`

## Readouts

The canonical readout tower is:

```text
A985 -> A236 -> A42 -> A12
```

The `d20.json` names these readouts as:

- `Code(d20) = A985`
- `Chem(d20) = A236`
- `Pin(d20) = A42`
- `CY(d20) = A12`
- `Foam(d20) = 1 + Lambda^2 H6`
- `Optics(d20) = etendue, Snell transport, complement conservation, caustic resolvent`
- `Integrity(d20) = sector-33 integral wall`

## Certified Claims

The core verifier checks:

- the 985 relations partition all `2576^2` ordered dodecad pairs;
- the sparse tensor has the expected shape and coefficient mass;
- `A42 -> A12` is consistent;
- the `A236 -> A42 -> A12` branching square has zero defect;
- the Leech boundary array has shape `[98280, 24]`;
- the sector-33 integrity gate has the recorded rank and kernel data;
- `layers/index.json` names all 26 layer certificates, their groups,
  dependency edges, expected statuses, legacy numbering, and flat semantic paths;
- all 26 layer certificates have their expected statuses through that registry.

## Boundary

The verifier does not currently claim:

- strict modularity or a nontrivial modular `S,T` pair;
- an unconditional physical interpretation;
- an unconditional complexity-theory theorem;
- intrinsic row canonicity without the adjoined hexacode/F4 row selector;
- a complete exposition-level derivation of the object before the A985 relation
  body is available.

The strongest current finite uniqueness statement is over `A985`: the coherent
coorient lift group has order `9216`, and the named generator coordinates
generate all admissible coherent-signature lifts.

## Commands

Core validation, without rewriting files:

```shell
python -m src.verify core --pretty
```

Full bundle audit, without rewriting files:

```shell
python -m src.verify audit --pretty
```

Deep core certificate writer:

```shell
python src/certify_core.py --out certificate.core.json --pretty
```

Regenerate `d20.json`, refresh certificate and manifest hashes, then audit:

```shell
python -m src.verify rebuild --pretty
```
