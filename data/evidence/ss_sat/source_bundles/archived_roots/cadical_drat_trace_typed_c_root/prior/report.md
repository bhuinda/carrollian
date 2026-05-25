# G^natural Ontological Computation cadical_drat_evidence

## Scope

cadical_drat_evidence promotes the external evidence gate from the external_evidence_gate negative-control state to a positive third-party proof-evidence witness.

The new evidence source is a CaDiCaL 3.0.0 proof run over the five bundled DIMACS benchmarks. Each benchmark has:

- the DIMACS input (`*.cnf`);
- captured solver stdout (`*.stdout.txt`);
- captured solver stderr (`*.stderr.txt`);
- a textual DRAT proof (`*.drat`);
- a bundle manifest with SHA-256 hashes and command information.

The finite base remains \(G^natural=A_{985}\), and the public domain remains \(D_{20}=\Lambda^3H_6\).

## Evidence Gate Audit

| invariant | value |
|---|---:|
| files in strong evidence bundle | 21 |
| parsed external events | 88 |
| nonempty external routes | 10 |
| rank summary over F2 | 5 |
| rank summary over F3 | 5 |
| rank summary over F5 | 5 |
| evidence status | `EVIDENCE_PRESENT` |

## Proof Verification

All five CaDiCaL DRAT proofs were independently checked with the bundled `drat-trim` verifier build.

| invariant | value |
|---|---:|
| DRAT proofs present | 5 |
| DRAT proofs verified | 5/5 |
| verifier exit code | 0 for every proof |

## What Changed From external_evidence_gate

1. Added a strong CaDiCaL evidence bundle with CNF/stdout/stderr/DRAT artifacts.
2. Recorded artifact hashes in `external_evidence_manifest.json`.
3. Re-ran the deterministic external-evidence analyzer on the strong bundle.
4. Fixed the analyzer so DIMACS inputs are recorded as input artifacts, not parsed as proof events.
5. Verified all DRAT proofs with `drat-trim`.

## Status

\[
\boxed{\text{external proof evidence is present and verified for the CaDiCaL benchmark bundle}}
\]

This is still an evidence-gate result. The next theorem-level update should type the parsed proof routes against the C/V/X integrity ladder and decide whether the class-3 ceiling survives under these external proof traces.
