# Claims Ledger

This verifier certifies a finite, Golay-conditioned object and its derived invariant stack.  It does not claim to derive the extended Golay code from no prior Golay input.

## Certified

- `A985` coherent algebra and quotient tower `A985 -> A236 -> A42 -> A12`.
- Tube projection section `TubePair^44521 -> Loop^297` with a certified right inverse.
- Drinfeld/Grothendieck center boundary with 39 sectors and full `A985` Wedderburn lift.
- Hesse-tube character-pencil layer, 35-dimensional Hesse cut, and `[39,4,36]` MDS dependency geometry.
- Quintic wall: 17 quintics and 23 linear syzygies.
- Canonical 24-coordinate syzygy frame `W24 = <Euler> ⊕ Syz_23`.
- Wu octad split and Spin^h/6j marking.
- Intrinsic MOG column sextet and active `K4` 6j tetrahedron.
- Hexacode row selector constructing a Type-II `[24,12,8]` Golay presentation.

## Obstructed

- Nontrivial strict modular `S,T` from the current raw tube data.
- Raw annular Hopf operators that fail kernel descent.
- Quadratic/internal Golay selector from the unmarked `W24` kernel/support geometry.
- Full row-refined Golay selector from pair-octad/Wu/6j incidence alone.

## Adjoined / External Selector

- The row-refined Golay selector is supplied by a deterministic hexacode / `F4` row-labeling selector.

## Not Claimed

- Golay independence from the source.
- A nontrivial modular tensor category datum from the raw tube algebra.
- Row canonicity from column-pair/Wu/6j data alone.

## v38 release hardening

- CI workflow: added.
- Tamper rejection suite: added.
- Detached release signature: added.
- Certificate-only edition: produced as separate artifact.
- Rebuildable edition: produced as full artifact.
- Mathematical claim stack: unchanged from v37.
