# FRAT Surface Route Audit v20

## Claim

For the bundled CaDiCaL 3.0.0 native textual FRAT proof traces, the emitted FRAT surface is typed `C` under the G^natural C/V/X integrity ladder.

## Inputs

```text
bundle = external_solver_evidence_bundle_strong_cadical_frat/
solver = CaDiCaL 3.0.0
proof format = native textual FRAT with antecedents
benchmarks = contradiction_4, horn_chain_8, horn_chain_12, php_3_2, xor_unsat
command = cadical.exe --frat=1 --checkproof=3 --no-binary <benchmark.cnf> <benchmark.cadical.frat>
```

The solver stdout/stderr logs are preserved in the bundle. The command line and SHA-256 hashes are recorded in `external_evidence_manifest.json`.

## Witness Conditions

The audit verifies the following conditions for the supplied proof files:

1. Each `.frat` file is paired with its `.cnf` file.
2. Each DIMACS header supplies an original public variable boundary.
3. Each FRAT original, derived, deletion, and finalization line is parsed as a public clausal event.
4. FRAT clause IDs and antecedent IDs are treated as proof references, not variables.
5. No FRAT clause uses a variable greater than the original DIMACS variable count.
6. No native XOR/GF(2), cutting-plane/PB, spectral/Fourier, or extension-variable event is detected.
7. Every antecedent-bearing FRAT derived line is extracted to LRAT form and verified by `lrat-trim`.

## Audit Result

```text
proof_count = 5
frat_surface_events = 214
antecedent_references = 91
C steps = 214
V steps = 0
X steps = 0
red_flags = []
verdict = C_PUBLIC_FRAT_SURFACE_TRACE
```

Per-proof summary:

| proof | FRAT events | antecedent refs | max variable seen | DIMACS variables | type |
|---|---:|---:|---:|---:|---|
| contradiction_4.cadical.frat | 12 | 2 | 4 | 4 | C |
| horn_chain_8.cadical.frat | 34 | 16 | 8 | 8 | C |
| horn_chain_12.cadical.frat | 50 | 24 | 12 | 12 | C |
| php_3_2.cadical.frat | 38 | 18 | 6 | 6 | C |
| xor_unsat.cadical.frat | 80 | 31 | 5 | 5 | C |

## Verification Boundary

No standalone FRAT checker was found locally. The package therefore uses two checks:

```text
CaDiCaL internal checkproof=3 during FRAT production
FRAT antecedent extraction -> LRAT -> lrat-trim verification
```

This verifies the emitted antecedent-bearing derivation content, but it does not certify the full FRAT format with an independent FRAT checker.

## Theorem Route

Tier 1 of the integrity ladder assigns public proof-logged clausal traces to integrity type `C`. FRAT original, derived, deletion, and finalization events over DIMACS literals remain public clausal proof events.

Therefore, for this supplied evidence bundle:

```text
CaDiCaL native textual FRAT surface -> public clausal proof route -> C
```

Under the Proof-Logged Public Solver Corollary, these traces do not instantiate an `X` extractor and do not extract `e33`.
