# Ingress Handoff Policy

`ingress/` is a local agent handoff area. It is not part of the canonical
certificate, invariant, proof-obligation, or evidence layout.

Canonical material promoted from a handoff must land in the matching repository
surface:

- source logic goes under `src/`, usually as `derive_*`, `certify_*`, or a
  clearly named probe module;
- certified or provisional mathematical payloads go under
  `data/invariants/` with report, manifest, and registry entries;
- non-certificate evidence archives go under `data/evidence/` with their own
  manifest;
- root registries and `d20.json` must not point at `ingress/`.

The current pairwise-square cone handoff is canonicalized at
`src/derive_d20_golay_shell_three_level_pairwise_square_cone_probe.py`. It is an
exploratory NNLS probe for Terwilliger profile support patterns, not a rational
SOS certificate. The Terwilliger profile representative derivation itself is
canonicalized at `src/derive_d20_golay_shell_three_level_terwilliger_profile_reps.py`
with artifacts under
`data/invariants/d20/proof_obligations/d20_golay_shell_three_level_terwilliger_profile_reps/`.

The Talagrand/Hamming/Golay Python handoff bundle from
`ingress/talagrand_python_handoff/` is canonicalized as an evidence archive at
`data/evidence/talagrand_python_handoff/`. Its verifier is
`python src/verify.py talagrand-handoff --pretty`. The archive is intentionally
registered as an open-target handoff: it records
`FINAL_GLOBAL_TALAGRAND_PROOF_NOT_CLAIMED` and keeps the multilevel KKT
obstruction system as the remaining exact target.

The remaining exact Talagrand target is also promoted as a D20 proof obligation
at
`data/invariants/d20/proof_obligations/d20_talagrand_multilevel_kkt_obstruction_system/`.
Its verifier is `python src/verify.py talagrand-kkt-obligation --pretty`. This
entry records the exact KKT obstruction system and the numerical
weighted-asymmetry audit, but it does not certify the final global Talagrand
proof.

The full 12-step Talagrand RUN_ORDER chain is promoted as a separate audit at
`data/invariants/d20/proof_obligations/d20_talagrand_closure_chain_audit/`.
Its verifier is `python src/verify.py talagrand-chain-audit --pretty`. This
audit classifies the imported steps as supporting bridge, exact slice,
reduction/normal-form, numerical audit, or open obstruction, and keeps the
final proof boundary explicit.
