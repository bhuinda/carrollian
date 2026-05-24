# LRAT Checked Proof-Route Audit v19

## Claim

For the bundled CaDiCaL 3.0.0 native textual LRAT proof traces, the emitted checked proof-route surface is typed `C` under the G^natural C/V/X integrity ladder.

## Inputs

```text
bundle = external_solver_evidence_bundle_strong_cadical_lrat/
solver = CaDiCaL 3.0.0
proof format = native textual LRAT
benchmarks = contradiction_4, horn_chain_8, horn_chain_12, php_3_2, xor_unsat
checker = lrat-trim 0.2.1-dev
```

The solver stdout/stderr logs are preserved in the bundle. The command line and SHA-256 hashes are recorded in `external_evidence_manifest.json`.

## Witness Conditions

The audit verifies the following conditions for the supplied proof files:

1. Each `.lrat` file is paired with its `.cnf` file.
2. Each DIMACS header supplies an original public variable boundary.
3. Each LRAT addition line is parsed as public clause literals plus checked antecedent references.
4. Each LRAT deletion line is parsed as proof bookkeeping over clause IDs.
5. No proof-line clause uses a variable greater than the original DIMACS variable count.
6. No native XOR/GF(2), cutting-plane/PB, spectral/Fourier, or extension-variable event is detected.
7. Each LRAT proof independently verifies with `lrat-trim`.

## Audit Result

```text
proof_count = 5
proof_steps = 62
antecedent_references = 109
C steps = 62
V steps = 0
X steps = 0
red_flags = []
verdict = C_PUBLIC_CHECKED_PROOF_TRACE
```

Per-proof summary:

| proof | LRAT steps | antecedent refs | max variable seen | DIMACS variables | type |
|---|---:|---:|---:|---:|---|
| contradiction_4.cadical.lrat | 1 | 2 | 0 | 4 | C |
| horn_chain_8.cadical.lrat | 15 | 23 | 8 | 8 | C |
| horn_chain_12.cadical.lrat | 23 | 35 | 12 | 12 | C |
| php_3_2.cadical.lrat | 7 | 18 | 6 | 6 | C |
| xor_unsat.cadical.lrat | 16 | 31 | 4 | 5 | C |

## Theorem Route

Tier 1 of the integrity ladder assigns public resolution/proof-logged CDCL traces to integrity type `C` when the proof witnesses are public clausal objects. LRAT strengthens the witness by including antecedent references checked by `lrat-trim`.

Therefore, for this supplied evidence bundle:

```text
CaDiCaL native textual LRAT proof trace -> checked public clausal proof route -> C
```

## Non-Claims

This audit does not classify every internal solver heuristic used before a proof line is emitted. It also does not prove a universal property of all CaDiCaL traces or all SAT solvers. It classifies the supplied public LRAT artifacts.

Under the Proof-Logged Public Solver Corollary, these traces do not instantiate an `X` extractor and do not extract `e33`.
