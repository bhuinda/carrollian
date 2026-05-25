# External Evidence Gate cadical_frat_surface_lrat_verified

cadical_frat_surface_lrat_verified adds native FRAT evidence and records two verification seams:

```text
standalone FRAT checker = not found locally
inherited full-FRAT route-rank analyzer = blocked by route explosion
```

Current witness:

```text
F = CaDiCaL 3.0.0 native textual FRAT proof run
benchmarks = 5 bundled DIMACS UNSAT fixtures
solver-side checking = checkproof=3
extracted LRAT verifier = lrat-trim 0.2.1-dev
extracted LRAT verification = 5/5 VERIFIED
proof-route type = C_PUBLIC_FRAT_SURFACE_TRACE
```

Current extracted-LRAT analyzer result:

```text
status = EVIDENCE_PRESENT
files = 5
total_events = 44
nonempty_routes = 5
rank_F2 = 4
rank_F3 = 4
rank_F5 = 4
```

Current FRAT C/V/X audit:

```text
frat_surface_events = 214
antecedent_references = 91
C_steps = 214
V_steps = 0
X_steps = 0
extension_variables = 0
red_flags = 0
```

Interpretation:

- Native FRAT artifacts are present and hash-manifested.
- The FRAT-embedded LRAT derivations verify independently with `lrat-trim`.
- The full FRAT surface is typed `C` by the cadical_frat_surface_lrat_verified classifier.
- Full independent FRAT-format verification remains blocked until a standalone FRAT checker is supplied.

Next obligation:

```text
standalone FRAT checker or bounded FRAT route-rank analyzer -> replay full FRAT surface end to end
```
