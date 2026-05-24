# G^natural Ontological Computation cadical_drat_trace_typed_c

## Scope

cadical_drat_trace_typed_c promotes the cadical_drat_evidence CaDiCaL evidence package from verified external DRAT proof evidence to a typed proof-route audit against the C/V/X integrity ladder.

The audited solver evidence is the existing strong CaDiCaL bundle:

- DIMACS inputs (`*.cnf`);
- captured solver stdout (`*.stdout.txt`);
- captured solver stderr (`*.stderr.txt`);
- textual DRAT proofs (`*.drat`);
- `external_evidence_manifest.json` with solver identity, command line, and artifact hashes.

The finite base remains \(G^natural=A_{985}\), and the public domain remains \(D_{20}=\Lambda^3H_6\).

## Witness Replay

| invariant | value |
|---|---:|
| files in strong evidence bundle | 21 |
| parsed external events | 88 |
| nonempty external routes | 10 |
| rank summary over F2 | 5 |
| rank summary over F3 | 5 |
| rank summary over F5 | 5 |
| evidence status | `EVIDENCE_PRESENT` |
| DRAT proofs verified | 5/5 |

All five DRAT proofs were rechecked with the bundled `drat-trim` verifier build. Every proof check exited 0.

## C/V/X Proof-Route Audit

The cadical_drat_trace_typed_c classifier parses the emitted textual DRAT proof lines and compares every proof-line event against the DIMACS variable boundary.

| invariant | value |
|---|---:|
| proofs audited | 5 |
| DRAT proof-line events | 83 |
| C-classified proof-line events | 83 |
| V-classified proof-line events | 0 |
| X-classified proof-line events | 0 |
| extension variables detected | 0 |
| native XOR/GF(2) proof steps detected | 0 |
| cutting-plane/PB proof steps detected | 0 |
| spectral/Fourier proof steps detected | 0 |
| red flags | 0 |
| verdict | `C_PUBLIC_PROOF_TRACE` |

The `xor_unsat` benchmark is an XOR-shaped input fixture, but the emitted CaDiCaL certificate is still a public clausal DRAT trace. The audit sees no native GF(2) row-addition proof step and no extension variable.

## Interpretation

Under tier 1 of the integrity ladder, public resolution/proof-logged CDCL traces over public clauses are typed `C`. The supplied CaDiCaL DRAT traces meet that criterion: every audited proof-line event is a public clausal addition, deletion, or empty-clause event over the original DIMACS variables.

By the Proof-Logged Public Solver Corollary, this external trace does not provide an `X` extractor and does not extract `e33`. It therefore does not challenge the class-3 ceiling under the audited proof-log surface.

## Status

\[
\boxed{\text{the supplied CaDiCaL DRAT proof traces are typed C under the tier-1 public proof-log rule}}
\]

This is a theorem-level classification of the supplied emitted proof traces. It is not a universal claim about all solver internals, all CaDiCaL runs, or future proof formats.

Next obligation: audit an LRAT/FRAT proof stream or a solver-internal trace export if the package needs evidence about checked proof derivations beyond textual DRAT surface classification.
