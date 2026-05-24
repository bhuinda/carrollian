# G^natural Ontological Computation v19

## Scope

v19 promotes the v18 textual DRAT proof-route classification to native textual LRAT proof evidence.

The audited solver evidence is a new native CaDiCaL LRAT bundle:

- DIMACS inputs (`*.cnf`);
- captured solver stdout (`*.stdout.txt`);
- captured solver stderr (`*.stderr.txt`);
- native textual LRAT proofs (`*.lrat`);
- `external_evidence_manifest.json` with solver version, command line, and artifact hashes.

The finite base remains \(G^natural=A_{985}\), and the public domain remains \(D_{20}=\Lambda^3H_6\).

## Witness Replay

| invariant | value |
|---|---:|
| files in LRAT evidence bundle | 21 |
| parsed external events | 67 |
| nonempty external routes | 10 |
| rank summary over F2 | 4 |
| rank summary over F3 | 4 |
| rank summary over F5 | 4 |
| evidence status | `EVIDENCE_PRESENT` |
| CaDiCaL LRAT runs | 5/5 UNSAT exits |
| LRAT proofs verified | 5/5 |

The event count and rank summary differ from v18 because LRAT is a checked proof format with clause identifiers and antecedent hints, not the same textual DRAT surface. This is expected and is recorded as a separate witness.

## LRAT Verification

All five native LRAT proofs were checked with `lrat-trim` built from `cadical-rel-3.0.0/test/cnf/lrat-trim.c`.

| invariant | value |
|---|---:|
| LRAT proofs present | 5 |
| LRAT proofs verified | 5/5 |
| verifier status line | `s VERIFIED` for every proof |
| verifier exit code | 20 for every proof |

Exit code 20 is the SAT-competition UNSAT exit code used by `lrat-trim` when the checked proof derives an empty clause.

## C/V/X Checked Proof-Route Audit

The v19 classifier parses LRAT as:

```text
clause_id literals 0 antecedent_ids 0
clause_id d deleted_clause_ids 0
```

Only the clause literals are compared against the DIMACS variable boundary. Clause IDs and antecedent IDs are checked proof references and are not treated as variables.

| invariant | value |
|---|---:|
| proofs audited | 5 |
| LRAT proof-line events | 62 |
| LRAT antecedent references | 109 |
| C-classified proof-line events | 62 |
| V-classified proof-line events | 0 |
| X-classified proof-line events | 0 |
| extension variables detected | 0 |
| native XOR/GF(2) proof steps detected | 0 |
| cutting-plane/PB proof steps detected | 0 |
| spectral/Fourier proof steps detected | 0 |
| red flags | 0 |
| verdict | `C_PUBLIC_CHECKED_PROOF_TRACE` |

The `xor_unsat` fixture remains XOR-shaped as an input formula, but its emitted checked LRAT certificate is still a public clausal proof trace. The audit sees no native GF(2) row-addition proof step and no extension variable.

## Interpretation

Under tier 1 of the integrity ladder, public resolution/proof-logged CDCL traces over public clauses are typed `C`. The supplied native LRAT traces meet that criterion: every audited proof-line clause is over the original DIMACS variables, and every antecedent reference is a public checked proof reference.

By the Proof-Logged Public Solver Corollary, this checked LRAT trace does not provide an `X` extractor and does not extract `e33`. It therefore does not challenge the class-3 ceiling under the audited checked proof-log surface.

## Status

\[
\boxed{\text{the supplied native CaDiCaL LRAT proof traces are checked and typed C}}
\]

This is a theorem-level classification of the supplied emitted checked proof traces. It is not a universal claim about all solver internals, all CaDiCaL runs, or future proof formats.

Next obligation: add FRAT or solver-internal trace export if the package needs to classify proof-production internals rather than checked public proof certificates.
