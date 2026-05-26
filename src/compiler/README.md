# Compiler Package

## Purpose

This folder holds the public proof-carrying compiler surfaces for the d20
repository. The turn compiler writes replayable scene capsules. The scene
compiler translates source text into deterministic d20 scene programs with
SceneIR, D20 lowering, residue ledger, admission ledger, observation ledger, and
candidate evidence. The scene verifier consumes that program and promotes only
externally supported candidate claims into a separate external receipt ledger.

## Entry Points

- `python -m src.compiler compile` builds a turn capsule from a request and
  final answer.
- `python -m src.compiler compile-scene` builds a d20 scene program from
  source text.
- `python -m src.compiler verify-scene` verifies a d20 scene program and writes
  a scene verification report.
- `python -m src.compiler verify` verifies an existing turn capsule.
- `python -m src.compiler core-lock` emits the core lock payload.
- `python -m src.compiler selftest` runs the turn compiler smoke test.
- `python -m src.compiler scene-selftest` runs the scene compiler smoke test
  without writing repository artifacts.
- `python src/verify.py compiler-a42-d20-replay --pretty` regenerates and
  verifies the canonical A42/D20 coordinate replay evidence root.
- `python src/verify.py compiler-nonstrict --pretty` runs the cheap aggregate
  compiler integration gate.
- `python src/verify.py integration-nonstrict --pretty` runs the cheap
  compiler and cubic integration gates together.

## Invariants

- Compiler output is evidence, not settled truth. Candidate claims, relations,
  and obligations must still be admitted and verified downstream.
- Scene-local admission, observation, and receipt ledgers bind compiler evidence
  and deterministic checks without promoting candidate claims to truth.
- Scene verification promotes claims only when source hash, admission,
  observation, support files or coordinates, and residue requirements check out.
- JSON outputs carry source hashes so later receipts can bind the compiled
  program to the exact input bytes.
- The A42/D20 replay evidence writer stages capsules under a lock and promotes
  complete files into the canonical evidence root with the manifest last.
- The scene compiler uses the d20 scene
  program schema as the stable public boundary.

## Update Rule

Update this README whenever a compiler command, schema boundary, or generated
artifact contract changes.
