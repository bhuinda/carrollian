# Token-Burn Guard Evidence

This directory stores the compact certificate for the repository bounded-output
guard. The full audit report is generated at
`generated/token_burn_guard_audit.json`; this tracked certificate records the
stable pass/fail coverage counts and policy.

Use:

```shell
python src/verify.py token-burn
```

The same guard check is also part of `python src/verify.py audit`.
For a pre-commit or local pre-push check, run the `token-burn` command above;
it is intentionally much lighter than the full mathematical audit.
Each run refreshes this certificate and its `data/evidence/index.json` registry
entry from the certificate file hash.

Policy:

- Repo-defined Python entrypoints must import the token-burn bootstrap marker.
- Direct-entrypoint directories must contain a local `sitecustomize.py` guard.
- Active subprocess calls must capture or redirect stdout/stderr.
- New active non-Python scripts fail the guard audit until explicitly reviewed.
- Active PowerShell scripts are allowlisted by exact path and must either
  redirect high-volume tool output or be wrapped.
- Tracked source archives are guarded where practical, but remain evidence
  payloads rather than supported execution APIs.
- Imported handoff evidence payloads, including the Talagrand Python handoff
  work tree, are validated by their own manifests and are not direct repo
  runner surfaces.
- Arbitrary manual shell commands are outside repo-file control.
