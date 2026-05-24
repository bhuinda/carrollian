# External Evidence Gate v18

v18 preserves the v17 positive external proof-evidence gate and adds a C/V/X proof-route classification.

Admissibility condition:

```text
external solver/proof family F -> canonical events -> D20 route -> Sigma_{<=5} ranks
```

Current witness:

```text
F = CaDiCaL 3.0.0 textual DRAT proof run
benchmarks = 5 bundled DIMACS UNSAT fixtures
proof verifier = drat-trim
verification status = 5/5 VERIFIED
proof-route type = C_PUBLIC_PROOF_TRACE
```

Current analyzer result:

```text
status = EVIDENCE_PRESENT
files = 21
total_events = 88
nonempty_routes = 10
rank_F2 = 5
rank_F3 = 5
rank_F5 = 5
```

Current C/V/X audit:

```text
proof_steps = 83
C_steps = 83
V_steps = 0
X_steps = 0
extension_variables = 0
red_flags = 0
```

Interpretation:

- The v17 external proof evidence remains present and DRAT-verified.
- The emitted proof traces are typed `C` under tier 1 of the integrity ladder.
- The supplied DRAT traces do not supply an `X` extractor and do not extract `e33`.
- The classification scope is the emitted proof logs, not all solver internals.

Next obligation:

```text
LRAT/FRAT or internal trace audit -> classify checked derivation steps beyond textual DRAT surface
```
