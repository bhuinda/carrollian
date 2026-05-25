# External Evidence Gate cadical_drat_evidence

cadical_drat_evidence is the first positive external proof-evidence package after the external_evidence_gate no-evidence gate.

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

Interpretation:

- The external_evidence_gate claim "evidence pending" is discharged for the CaDiCaL proof bundle.
- The package now contains raw artifact hashes, parsed event counts, route counts, and field-rank summaries.
- The result is not yet a universal solver theorem. It is a verified external proof-ingestion witness.

Next obligation:

```text
typed proof-route audit -> classify CaDiCaL DRAT events as C/V/X -> compare against class-3 ceiling
```
