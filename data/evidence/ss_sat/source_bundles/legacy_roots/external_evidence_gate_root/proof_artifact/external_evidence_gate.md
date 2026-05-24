# External Evidence Gate external_evidence_gate

The purpose of external_evidence_gate is negative-control rigor.

A third-party solver/proof claim is admissible only if the package contains at least one external artifact whose parsed event route is nonempty and whose source file hash is recorded in `external_analysis.json`.

Current result:

```text
EVIDENCE_PENDING_NO_EVENTS
```

Therefore external_evidence_gate introduces no new computational theorem. It certifies the ingress path for the next theorem.

The next admissible theorem has the form:

```text
external solver/proof family F -> canonical events -> D20 route -> Sigma_{<=5} ranks
```

and must report:

- raw external artifact hashes;
- parsed event counts;
- canonical route hashes;
- degree 3/4/5 rank comparison over F2, F3, F5;
- whether the class-3 ceiling survives.
