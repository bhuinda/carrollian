# G^natural Ontological Computation v20

## Scope

v20 adds native textual FRAT proof evidence after the v19 native LRAT package.

The audited solver evidence is a new CaDiCaL FRAT bundle:

- DIMACS inputs (`*.cnf`);
- captured solver stdout (`*.stdout.txt`);
- captured solver stderr (`*.stderr.txt`);
- native textual FRAT proofs with antecedents (`*.frat`);
- `external_evidence_manifest.json` with solver version, command line, and artifact hashes.

The finite base remains \(G^natural=A_{985}\), and the public domain remains \(D_{20}=\Lambda^3H_6\).

## Witness Replay

| invariant | value |
|---|---:|
| files in FRAT evidence bundle | 21 |
| CaDiCaL FRAT runs | 5/5 UNSAT exits |
| solver stderr files | 5/5 empty |
| standalone FRAT checker found locally | no |
| extracted LRAT proofs verified | 5/5 |

The FRAT runs used:

```text
cadical.exe --frat=1 --checkproof=3 --no-binary <benchmark.cnf> <benchmark.cadical.frat>
```

`--frat=1` emits FRAT with antecedents. `--checkproof=3` enables CaDiCaL internal proof checking while producing the trace.

## Verification Seam

No standalone FRAT checker or FRAT-to-LRAT checker was found in the local tree. v20 therefore does not claim full external FRAT-format verification.

Instead, v20 verifies the checked derivation content embedded in the FRAT files:

```text
FRAT line: a <id> <lits> 0 l <antecedent_ids> 0
extracted LRAT line: <id> <lits> 0 <antecedent_ids> 0
```

The extracted LRAT traces verify with `lrat-trim`:

| invariant | value |
|---|---:|
| extracted LRAT traces | 5 |
| extracted LRAT traces verified | 5/5 |
| verifier status line | `s VERIFIED` for every proof |
| verifier exit code | 20 for every proof |

This validates the antecedent-bearing derived-clause content of the FRAT files, but it is still not a substitute for a full standalone FRAT checker.

## Analyzer Seam

The inherited external route-rank analyzer was designed for smaller DRAT/LRAT proof surfaces. It timed out on the full FRAT surface because FRAT has 214 proof-line events and the legacy degree-5 route-rank stage enumerates proof-route combinations.

The replacement replay witness is the extracted LRAT subtrace:

| invariant | value |
|---|---:|
| extracted LRAT files | 5 |
| parsed extracted LRAT events | 44 |
| nonempty extracted routes | 5 |
| extracted LRAT rank over F2 | 4 |
| extracted LRAT rank over F3 | 4 |
| extracted LRAT rank over F5 | 4 |
| extracted LRAT evidence status | `EVIDENCE_PRESENT` |

The full FRAT surface is therefore classified by the C/V/X surface audit, not by the legacy route-rank analyzer.

## C/V/X FRAT Surface Audit

The v20 classifier parses FRAT as:

```text
o <id> <lits> 0
a <id> <lits> 0 l <antecedent_ids> 0
d <id> <lits> 0
f <id> <lits> 0
```

Only clause literals are compared against the DIMACS variable boundary. Clause IDs and antecedent IDs are proof references and are not treated as variables.

| invariant | value |
|---|---:|
| proofs audited | 5 |
| FRAT surface events | 214 |
| FRAT original-clause events | 63 |
| FRAT derived-clause events | 44 |
| FRAT deletion events | 39 |
| FRAT finalization events | 68 |
| FRAT antecedent references | 91 |
| C-classified events | 214 |
| V-classified events | 0 |
| X-classified events | 0 |
| extension variables detected | 0 |
| native XOR/GF(2) proof steps detected | 0 |
| red flags | 0 |
| verdict | `C_PUBLIC_FRAT_SURFACE_TRACE` |

## Interpretation

Under tier 1 of the integrity ladder, public proof-logged clausal traces are typed `C`. The supplied FRAT surface meets that criterion: every audited clause event is over the original DIMACS variables, and every antecedent reference is a public proof ID.

By the Proof-Logged Public Solver Corollary, this FRAT surface and its extracted LRAT derivation do not provide an `X` extractor and do not extract `e33`. They therefore do not challenge the class-3 ceiling under the audited public proof-log surface.

## Status

\[
\boxed{\text{native FRAT evidence is present; embedded LRAT derivations verify; FRAT surface is typed C}}
\]

This status is intentionally narrower than full FRAT certification: a standalone FRAT checker is still missing.

Next obligation: add a standalone FRAT checker or a bounded FRAT route-rank analyzer, then replay the full FRAT surface end to end.
