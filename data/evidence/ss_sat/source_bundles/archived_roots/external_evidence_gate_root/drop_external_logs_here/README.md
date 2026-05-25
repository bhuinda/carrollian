# External solver evidence dropbox

Place genuine external SAT solver outputs here. Preferred files:

- solver stdout/stderr logs (`*.stdout.txt`, `*.stderr.txt`, `*.log`)
- proof files (`*.drat`, `*.lrat`, `*.frat`, `*.proof`)
- the DIMACS CNF used to generate them (`*.cnf`)
- optional `external_evidence_manifest.json`

Then run:

```bash
python3 scripts/analyze_external_evidence.py drop_external_logs_here --out external_analysis
```

This package intentionally contains no third-party solver evidence yet.
