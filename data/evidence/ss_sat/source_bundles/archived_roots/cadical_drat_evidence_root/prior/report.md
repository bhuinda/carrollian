# G^natural Ontological Computation external_evidence_gate

## Scope

external_evidence_gate hardens the external-evidence gate. source_drop built the harness and found no third-party solver or proof tools on the sandbox PATH. external_evidence_gate adds a dropbox, cross-platform runner scripts, an external evidence manifest schema, a deterministic external-log analyzer, and a no-evidence audit.

It does **not** claim genuine MiniSat/CaDiCaL/Kissat/DRAT/LRAT evidence. The package is ready to receive external logs, and it records that the current artifact contains no external event evidence.

The finite base remains \(G^
atural=A_{985}\), and the public domain remains \(D_{20}=\Lambda^3H_6\).

## Evidence gate audit

| invariant | value |
|---|---:|
| files in external dropbox | 0 |
| parsed external events | 0 |
| nonempty external routes | 0 |
| evidence status | `EVIDENCE_PENDING_NO_EVENTS` |

## What changed from source_drop

1. Added `drop_external_logs_here/` as the canonical evidence ingress.
2. Added `external_evidence_manifest.schema.json` and a template manifest.
3. Added `run_external_solvers.sh` and `run_external_solvers.ps1` for local external runs.
4. Added `analyze_external_evidence.py`, which parses stdout/proof-like files into canonical events and route summaries.
5. Added an explicit no-evidence audit so the chain cannot silently pretend that third-party logs were ingested.

## Status

\[
oxed{	ext{external evidence gate is hardened; evidence remains pending}}
\]

Next real update requires actual external logs/proofs placed into `drop_external_logs_here/` and reanalysis with:

```bash
python3 scripts/analyze_external_evidence.py drop_external_logs_here --out external_analysis
```
