# C/V/X Proof-Route Audit v18

## Claim

For the bundled CaDiCaL 3.0.0 textual DRAT proof traces, the emitted proof-route surface is typed `C` under the G^natural C/V/X integrity ladder.

## Inputs

```text
bundle = external_solver_evidence_bundle_strong_cadical/
solver = CaDiCaL 3.0.0
proof format = textual DRAT
benchmarks = contradiction_4, horn_chain_8, horn_chain_12, php_3_2, xor_unsat
```

The solver stdout/stderr logs are preserved in the bundle. The command line and SHA-256 hashes are recorded in `external_evidence_manifest.json`.

## Witness Conditions

The audit verifies the following conditions for the supplied proof files:

1. Each `.drat` file is paired with its `.cnf` file.
2. Each DIMACS header supplies an original public variable boundary.
3. Each parsed DRAT line is a clausal add/delete/empty-clause event.
4. No proof-line event uses a variable greater than the original DIMACS variable count.
5. No native XOR/GF(2), cutting-plane/PB, spectral/Fourier, or extension-variable event is detected.
6. Each DRAT proof independently verifies with `drat-trim`.

## Audit Result

```text
proof_count = 5
proof_steps = 83
C steps = 83
V steps = 0
X steps = 0
red_flags = []
verdict = C_PUBLIC_PROOF_TRACE
```

Per-proof summary:

| proof | DRAT steps | max variable seen | DIMACS variables | type |
|---|---:|---:|---:|---|
| contradiction_4.cadical.drat | 5 | 4 | 4 | C |
| horn_chain_8.cadical.drat | 16 | 8 | 8 | C |
| horn_chain_12.cadical.drat | 24 | 12 | 12 | C |
| php_3_2.cadical.drat | 7 | 6 | 6 | C |
| xor_unsat.cadical.drat | 31 | 4 | 5 | C |

## Theorem Route

Tier 1 of the integrity ladder assigns public resolution/proof-logged CDCL traces to integrity type `C` when the proof witnesses are public clausal objects. The emitted DRAT lines are public clauses and deletions over the original DIMACS variable set.

Therefore, for this supplied evidence bundle:

```text
CaDiCaL textual DRAT proof trace -> public clausal proof route -> C
```

## Non-Claims

This audit does not classify every internal solver heuristic used before a proof line is emitted. It also does not prove a universal property of all CaDiCaL traces or all SAT solvers. It classifies the supplied public DRAT artifacts.

Under the Proof-Logged Public Solver Corollary, these traces do not instantiate an `X` extractor and do not extract `e33`.
