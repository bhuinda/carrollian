# SS-SAT External Solver Evidence

This is the canonical repository evidence archive for the SAT solver work. The old `gnatural_ontological_computation_v*` directories are staging sources only; the retained evidence lives under `data/evidence/ss_sat`.

## Solver Runs

- Benchmarks: 5 DIMACS fixtures.
- Solver logs: 15 stdout/stderr pairs across CaDiCaL, Kissat, and MiniSat.
- CaDiCaL: 5/5 UNSAT.
- MiniSat: 5/5 UNSAT.
- Kissat: 3/5 UNSAT, 2/5 SIGSEGV residues.

## Proof Evidence

| family | result | verifier |
|---|---:|---|
| CaDiCaL DRAT | 5/5 verified | drat-trim |
| CaDiCaL LRAT | 5/5 verified | lrat-trim |
| CaDiCaL FRAT embedded LRAT | 5/5 verified | lrat-trim over extracted antecedent LRAT |
| CaDiCaL FRAT full format | blocked | no standalone FRAT checker found locally |

## C/V/X Interpretation

| surface | events | verdict |
|---|---:|---|
| DRAT | 83 | `C_PUBLIC_PROOF_TRACE` |
| LRAT | 62 | `C_PUBLIC_CHECKED_PROOF_TRACE` |
| FRAT | 214 | `C_PUBLIC_FRAT_SURFACE_TRACE` |

All audited proof-log events are typed `C`; no `V`, no `X`, no extension variables, and no native GF(2) proof steps are present in the supplied public proof logs.

## Residues

- `residues/kissat_sigsegv.json`: Kissat crashed on `php_3_2.cnf` and `xor_unsat.cnf`.
- `residues/frat_checker_status.json`: full standalone FRAT checking is blocked locally.
- `residues/full_frat_inherited_analyzer_blocked.json`: the inherited degree-5 full-FRAT route-rank analyzer is blocked by route explosion; the extracted LRAT replay remains available and verified.
