# External Evidence Gate v19

v19 preserves the positive external proof-evidence gate and adds native checked LRAT proof-route evidence.

Admissibility condition:

```text
external solver/proof family F -> canonical events -> D20 route -> Sigma_{<=5} ranks
```

Current witness:

```text
F = CaDiCaL 3.0.0 native textual LRAT proof run
benchmarks = 5 bundled DIMACS UNSAT fixtures
proof verifier = lrat-trim 0.2.1-dev
verification status = 5/5 VERIFIED
proof-route type = C_PUBLIC_CHECKED_PROOF_TRACE
```

Current analyzer result:

```text
status = EVIDENCE_PRESENT
files = 21
total_events = 67
nonempty_routes = 10
rank_F2 = 4
rank_F3 = 4
rank_F5 = 4
```

Current C/V/X audit:

```text
proof_steps = 62
antecedent_references = 109
C_steps = 62
V_steps = 0
X_steps = 0
extension_variables = 0
red_flags = 0
```

Interpretation:

- The external LRAT proof evidence is present and independently verified.
- The emitted checked proof traces are typed `C` under tier 1 of the integrity ladder.
- The supplied LRAT traces do not supply an `X` extractor and do not extract `e33`.
- The classification scope is the emitted checked proof logs, not all solver internals.

Next obligation:

```text
FRAT or internal trace audit -> classify proof-production internals beyond checked public certificates
```
