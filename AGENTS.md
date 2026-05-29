VERIFY BEFORE CLOSURE

This repository is certificate-driven. Do not report work as complete until the
relevant verifier has passed. If a claim has not been checked, call it
provisional or blocked.

Required stage order for proof work:

1. draft: read the existing certificate boundary and source artifacts.
2. witness: emit explicit rows, tables, hashes, and reports.
3. coherence: validate shapes, counts, hashes, and dependency seams.
4. closure: state exactly what is certified and what is not certified.
5. emit: update generated artifacts, verifier hooks, and report indexes.

## Repository Operation

Use the repository as a finite proof bundle, not as an ad hoc scratchpad.

- Canonical proof artifacts live under
  `data/invariants/d20/proof_obligations/<id>/`.
- A proof obligation should normally have:
  - `src/derive_<id>.py`
  - `src/certify_<id>.py`
  - `report.json`
  - `cert.json`
  - `manifest.json`
  - typed CSV witnesses
  - `tables.npz`
  - an entry in `data/invariants/d20/proof_obligations/index.json`
  - a verifier mode in `src/verify.py`
- Do not put canonical data in `upload/`. That directory is noncanonical and
  should not be used for new proof state.
- Use short certificate names. Prefer names like `long_inv`, `long_pobj`,
  `long_assoc`, and `long_h16`.
- Use finite-line naming for the line-address construction. Do not introduce
  alternate line-name prefixes.
- Preserve unrelated worktree changes. This repo is often dirty with generated
  or staged artifacts. Do not revert files you did not intentionally change.
- Prefer `rg` for search and targeted file reads before edits.
- Use `apply_patch` for manual edits. Mechanical formatting or generated
  artifact refreshes may use the repo's scripts.

## Separation Of Concerns

The repo has four distinct layers. Keep them separate.

1. Proof obligations prove local mathematical claims.
   - Source: `src/derive_*.py`
   - Validator: `src/certify_*.py`
   - Output: `data/invariants/d20/proof_obligations/<id>/`
   - Focused gate: `python src\verify.py <mode> --pretty`
   - Responsibility: theorem rows, witnesses, exact counts, hashes, and local
     closure boundaries.

2. The verifier routes proof checks.
   - Source: `src/verify.py`
   - Responsibility: expose human-readable validation modes and return pass/fail
     JSON.
   - Non-responsibility: inventing new theorem content.

3. The compiler assembles the certified surface.
   - Source: `src/commands/regen.py` and `src/derive_d20.py`
   - Output: `d20.json`, `certificate.json`, and refreshed manifests.
   - Responsibility: package certified fragments into the public object,
     refresh registry/hash surfaces, and catch integration drift.
   - Non-responsibility: proving unresolved theorem debt.

4. Bundle certification checks global coherence.
   - Source: `src/commands/certify.py`
   - Typical fast gate:
     `python -B src\commands\certify.py --mode fast --pretty --no-regenerate`
   - Responsibility: ensure the assembled object, certificate registry,
     invariant report inventory, and evidence surfaces still cohere.
   - Non-responsibility: replacing focused theorem validators.

If these layers disagree, trust the most local focused certificate first, then
inspect the compiler/registry wiring. A compiler failure often means stale
hashes, missing files, or index drift. It does not automatically mean the
underlying theorem is false.

## Compiler Boundary

The compiler exists to produce a canonical object from certified artifacts.

It may certify:

- `d20.json` object shape and object hash;
- `certificate.json` registry shape and self hash;
- file-hash manifest freshness;
- invariant report inventory counts;
- integration surfaces for evidence and compiler smoke tests.

It must not claim:

- semantic C985 associator composition;
- pentagon or zig-zag coherence beyond the dedicated certificates;
- a probability measure on the full raw tensor support;
- all raw product paths in each fiber;
- horizon-16 profunctor existence;
- exhaustiveness of every finite-line invariant.

When adding a proof obligation, do not hide new theorem content inside
`regen.py`, `derive_d20.py`, or `certificate.json`. Put the theorem content in a
dedicated `derive_*/certify_*` pair, then let the compiler package it.

## Constructing d20 From Halloween.npz

`Halloween.npz` is the compact raw multiplication tensor seed. Treat it as the
single mathematical tensor input, not as a proof by itself and not as a complete
scratch construction from nothing. The repository still supplies deterministic
source code, validators, certificate formats, and, in the current default raw
constructor, a small checked seed boundary for relation memberships, terminal
quotients, and simple branching. The raw tensor is located through the
`raw_tensor` role in `data/raw/index.json`; if that role is absent, the first
fallback is `data/raw/Halloween.npz`.

Starting from that tensor, the construction first normalizes the sparse
985-address multiplication table. The constructor reads the tensor support,
coefficient weights, representative relation rows, and object-pair relation
matrix, then checks that the support count, coefficient mass, relation range,
and object-pair typing cohere with the finite object. This is the point where
the raw tensor becomes the audited `A985`/`C985` multiplication body instead of
an anonymous archive.

The next step is to derive or audit the public quotient surfaces from that core
body. The current supplied-seed constructor regenerates the `A42` and `A12`
quotient tensors from the sparse 985 tensor and checks them against the stored
quotient maps. It also checks the simple branching matrices and the integral
wall language used by the public certificate surface. If the operator wants a
literal Halloween-only data path, the missing work is to replace those remaining
stored membership, quotient, and branching seeds with derivations from the
tensor or with the stricter source/coorient constructor. Do not blur that seam.

After the local constructor and focused proof obligations pass, the compiler
packages the certified surface into `d20.json`. This packaging step refreshes
`certificate.json`, report indexes, and file hashes. It is assembly, not theorem
discovery: unresolved claims must live in dedicated proof obligations, not in
`regen.py`, `derive_d20.py`, or hand-edited JSON.

The practical operator path is to place the seed at `data/raw/Halloween.npz` or
point `data/raw/index.json` at it as `raw_tensor`, run the constructor or rebuild
entrypoint, run any focused validators touched by the change, then run the broad
certificate gate. A successful result means the object was reconstructed from
the supplied raw tensor seed plus the repository's checked code and current seed
boundary. It does not mean semantic C985 associator composition, a full raw
support probability measure, all raw product paths, a horizon-16 profunctor, or
invariant-family exhaustiveness has been certified.

## Standard Proof-Obligation Workflow

For a new certificate `<id>`:

1. Read the upstream reports and CSV/table inputs.
2. Add `src/derive_<id>.py`.
3. Add `src/certify_<id>.py`.
4. Wire `src/verify.py` with a `<id-with-dashes>` command.
5. Run the derive script once. If row fingerprints are new, the first run may
   be provisional.
6. Lock the computed fingerprints in the derive script.
7. Regenerate the proof artifacts.
8. Run the focused validator.
9. Run the focused `src/verify.py` mode.
10. Refresh top-level registry data when the proof obligation is meant to be
    part of the certified bundle.
11. Run the broad certificate gate.
12. Run diff hygiene checks.

Typical commands:

```shell
python -m src.derive_<id>
python -m src.certify_<id>
python src\verify.py <id-with-dashes> --pretty
python -B src\commands\regen.py --cached-source --no-audit
python -B src\commands\certify.py --mode fast --pretty --no-regenerate
git diff --check
git diff --cached --check
```

Use `python src\verify.py audit` when a full audit is required. Use
`python src\verify.py rebuild --cached-source` when the bundle itself must be
rebuilt through the verifier entrypoint.

## Current Certified Boundary

The current theorem boundary is `long_thm`.

Certified by `long_thm`:

- finite tensor-lookup LLN theorem status for the 985-address finite-line
  bridge;
- tensor support count: `1,414,965`;
- tensor coefficient mass: `2,537,360`;
- universal LLN laws: `306`;
- probability path witnesses: `288`;
- support-gap checks: `131,586`;
- nonnegative support-gap checks: `131,586`;
- tail formula classes: `26`;
- certified layers: `8`;
- seam matches: `8`;
- proof inventory rows: `6`.

The finite theorem is closed, but the broader invariant-discovery objective is
not closed. `long_thm` explicitly keeps `complete_goal_claim_flag = 0`.

The current inventory boundary is `long_inv`.

Certified by `long_inv`:

- `long_thm` remains the input theorem boundary;
- the finite theorem has `0` remaining theorem-critical boundary items;
- semantic C985 associator debt is retired by the focused C985 final
  certificate;
- there are `0` focused broader invariant families still open under the current
  oracle ontology;
- `6` inventory families are certified;
- `0` active-goal inventory rows remain in the focused frontier;
- `0` of the remaining focused families are high-priority;
- the current horizon-16 active frontier is retired by `long_h16` as a
  current-model obstruction while reserving absolute nonexistence for changed
  object/support models;
- scoped active-product measure debt is retired by `long_measure` as a scoped
  probability law with the full raw-support gap preserved;
- bounded finite-line inventory cover is retired by `long_inv_exhaust`;
- the next highest-yield item is broad integration only when the operator
  permits long gates.

Certified by `long_inv_exhaust`:

- all five `long_thm` source boundary rows are covered by focused
  current-oracle certificates;
- the current finite-line invariant-family inventory has zero active frontier
  rows under the focused oracle ontology;
- associator, path accounting, scoped measure, and h16 current-model
  obstruction debts are retired as focused guardrails;
- absolute invariant exhaustiveness outside the current oracle ontology remains
  out of scope.

Certified by `long_h16`:

- horizon-16 is raw-backed at the compressed owner/support quotient;
- one explicit raw product-path witness exists for every horizon-16 sum-state
  fiber;
- the sample witnesses are Alexandrov-zeta composable but not exact
  source/target composable;
- the full raw tensor support has an oriented interval sheaf, not a
  positive-zeta sheaf;
- global support-gap induction is available as the finite-line support oracle;
- no materialized genuine `long_prof` horizon-16 profunctor exists in the
  current artifact boundary;
- the current-model h16 active frontier is closed as an obstruction under the
  certified artifact constraints.

The existing `long_prof` certificate is still useful, but it is not the missing
horizon-16 object. It certifies a finite Alexandrov-line profunctor/tensor-lookup
chain through horizon eight. `long_raw`, `long_path`, and `long_comp` then show
that the horizon-16 extension is raw-backed and zeta-composable at the selected
witness level, while exact source/target C985 composability, all raw paths, and
a genuine horizon-16 `long_prof` remain out of scope.

Certified by `long_orac`:

- the C985 oracle chain is reproducible through the final multi-fusion
  certificate;
- canonical A985 source-sector matrix units and character tables are available;
- `screen12=11` is obstructed by the current six-object/109-piece support
  constraints;
- the zeta-composable sample-path sheaf and horizon-128 witness lift are
  explicit certified boundary surfaces;
- the current horizon-16 boundary is recorded as a raw-backed quotient/sample
  path obstruction without a materialized `long_prof` profunctor;
- the orientation-duality Mobius split, coefficient-dual witness kernel, finite
  dual path probability curve, finite transport martingale boundary, stopped-tail
  bounds, and single-defect drift-limit obstruction are now explicit oracle
  surfaces;
- the formal horizon-16 object/profunctor gap chain is explicit: finite
  horizon-eight `long_prof`, formal convolution shadow, 208 object-gap rows,
  64,560,240 component-path gap words, owner/component lift boundary,
  raw-support lift boundary, and single-witness raw path boundary;
- compressed active raw product-path family accounting is explicit for the
  `64,570,080` component paths;
- scoped active raw product-family probability laws are explicit, with the full
  raw-support gap preserved;
- bounded finite-line inventory cover is explicit through `long_inv_exhaust`;
- finite anomaly correction is explicit through `long_anom`: sector-26 anomaly
  detection, cancelled-packet recovery, gamma8 correction, all-coordinate
  rank-one correction, global counterterm lattice, hidden-split symmetry
  reduction, strict sector-26 clock boundary, Ward/BMS closure, superselection
  extension, and C2 quotient counterterm;
- finite automorphic/Fourier/string-kernel closure is explicit through
  `long_auto`: Loop_297 amplitude quotienting, the 2048-state Fourier-mode
  automaton, rank-10 finite string-kernel algebra, central/parity extension,
  512 projective packets, A985 sector trace tests, sector-11 support
  obstruction, and finite anomaly correction cohere as a current-model oracle
  surface;
- finite matrix-theoretic charge-wall closure is explicit through `long_mat`:
  canonical flux/Ward gauges, Pi33 obstruction, typed non-exact optical updates,
  Fourier screens, full COO-backed A985 matrix units, packet charge frames,
  zero-pair propagator kernel, packet239 seed propagation, full-exposure packet
  doublets, quotient packet actions, explicit packet-restriction gaps,
  low-support packet candidate obstructions, prime-support alignment, finite
  packet matrix lifts, and packet-bridge obstructions cohere as a
  37-surface current-model oracle surface;
- `long_inv` is synchronized with the now-passing C985 final certificate and
  the focused inventory cover.

Current `long_orac` witness counts:

- input reports: `31`;
- certified input reports: `31`;
- resolved oracle surfaces: `29`;
- open oracle boundaries: `22`.

Certified by `long_frontier`:

- the operational process ontology is certificate-frontier planning:
  certified surface -> open boundary -> candidate operator -> witness artifact
  -> focused verifier -> oracle refresh;
- matrix-sector gauge, `screen12=11`, C2, the `long_pobj` decision, compressed
  `long_paths` accounting, scoped `long_measure` laws, the current-model h16
  obstruction, bounded `long_inv_exhaust` cover, finite `long_anom` correction,
  finite `long_auto` automorphic/Fourier closure, finite `long_mat`
  matrix-theory closure, and oracle synchronization are closed guardrails rather
  than current search targets;
- there are `0` active focused theorem-debt frontier targets;
- focused token reduction now comes from avoiding broad integration gates until
  the operator permits them.

Certified by `long_pobj`:

- the 288 selected witness paths, including all 208 horizon-9..16 gap fibers,
  form a finite Alexandrov-zeta-composable sample section;
- the current selected representatives have `0` exact raw endpoint component
  pair matches and `0` identity components for an exact raw path object;
- the selected witness family is not the full `64,570,080`-word component-path
  object; `64,569,792` component paths remain unmaterialized;
- the result does not prove absolute nonexistence under changed representatives
  or a changed object/support model.

Certified by `long_paths`:

- all 288 current active-component sum fibers have exact compressed raw
  product-family counts;
- the 208 gap fibers are included in the compressed path-family accounting;
- the full `64,570,080` component-path family is accounted for by fiber and
  horizon, including `64,560,240` gap component paths;
- active raw-support path counts and active raw-coefficient masses are
  reproducible by digit counts and modular witnesses;
- materialized rows for every raw address path, exact C985 source/target
  composability of all raw paths, and a full raw-support probability measure
  remain out of scope.

Certified by `long_measure`:

- two scoped probability laws are normalized over the compressed active raw
  product family: one by active raw-support counts and one by active
  raw-coefficient mass;
- both scoped laws have exact conditional normalization over horizons `1..16`;
- both scoped laws have exact mixed-horizon normalization, sample-average
  variance shrinkage, and exact law-of-total-variance decomposition;
- the inactive full raw-support gap is explicit: `318,374` support rows and
  `551,520` coefficient mass;
- `long_measure` does not certify a probability measure on the full raw tensor
  support independent of the current active-product boundary.

Current public-object status after the latest broad fast gate:

- `D20_CERTIFIED`;
- invariant reports: `414`;
- certified invariant reports: `404`;
- provisional invariant reports: `10`;
- demoted invariant reports: `0`.

Treat those as bundle inventory counts, not as theorem-completion claims.

## Outstanding Theorem Debt

Do not claim final mathematical closure until these debts are resolved or
explicitly demoted by certificate.

Focused theorem-debt frontier:

- empty under the current oracle ontology;
- broad bundle integration remains intentionally unrun while the operator is
  still resolving the automorphic-form/profunctorial investigation;
- absolute claims outside the current oracle ontology remain out of scope unless
  a new dedicated certificate is emitted.

Retired by focused certificate:

- `long_assoc`: semantic C985 associator composition is retired by
  `c985_final_multifusion_certificate`; optional pivotal, spherical, unitary,
  braided, ribbon, and Drinfeld-center modular structures remain out of scope.
- `long_paths`: raw/component product-family accounting is retired by
  `long_paths`; materialized raw-address rows and exact C985/profunctor
  composability remain out of scope.
- `long_measure`: scoped active raw product-family probability laws are retired
  by `long_measure`; a full raw-support probability measure independent of the
  current active-product boundary remains out of scope.
- `long_h16`: the current-model horizon-16 active frontier is retired by
  `long_h16` as an obstruction under the certified artifact constraints;
  absolute nonexistence under changed object/support models remains out of
  scope.
- `long_inv_exhaust`: bounded finite-line inventory cover is retired by
  `long_inv_exhaust`; absolute invariant omniscience outside the current oracle
  ontology remains out of scope.
- `long_anom`: finite anomaly correction is retired by `long_anom`; continuum
  anomaly cancellation outside the finite d20 oracle remains out of scope.
- `long_auto`: finite automorphic/Fourier/string-kernel closure is retired by
  `long_auto`; continuum automorphic-form classification outside the finite d20
  oracle remains out of scope.
- `long_mat`: finite matrix-theoretic charge-wall closure is retired by
  `long_mat`; packet propagation, packet239 seed status, quotient packet
  actions, explicit restriction gaps, low-support packet candidates, and
  prime-support alignment are direct oracle inputs. A full A985-to-packet
  operator homomorphism or continuum Matrix-theory model remains out of scope.

Immediate next item:

- Keep broad/long gates deferred until the operator permits them; use
  `long_frontier` as the focused oracle boundary in the meantime.

## Where To Look First

Use this map before starting new work:

- finite theorem closure: `data/invariants/d20/proof_obligations/long_thm/`
- theorem-debt inventory: `data/invariants/d20/proof_obligations/long_inv/`
- bounded inventory cover:
  `data/invariants/d20/proof_obligations/long_inv_exhaust/`
- finite anomaly correction oracle:
  `data/invariants/d20/proof_obligations/long_anom/`
- finite automorphic/Fourier boundary:
  `data/invariants/d20/proof_obligations/long_auto/`
- finite matrix-theoretic charge-wall boundary:
  `data/invariants/d20/proof_obligations/long_mat/`
- horizon-16 profunctor boundary:
  `data/invariants/d20/proof_obligations/long_h16/`
- local oracle/anomaly status split:
  `data/invariants/d20/proof_obligations/long_orac/`
- oracle-driven certificate frontier:
  `data/invariants/d20/proof_obligations/long_frontier/`
- path-object closure decision:
  `data/invariants/d20/proof_obligations/long_pobj/`
- compressed active raw product-path family:
  `data/invariants/d20/proof_obligations/long_paths/`
- scoped active raw product-family measure boundary:
  `data/invariants/d20/proof_obligations/long_measure/`
- finite dual-probability and drift-limit chain:
  `data/invariants/d20/proof_obligations/long_orient/`,
  `data/invariants/d20/proof_obligations/long_dual/`,
  `data/invariants/d20/proof_obligations/long_prob/`,
  `data/invariants/d20/proof_obligations/long_mart/`,
  `data/invariants/d20/proof_obligations/long_stop/`,
  `data/invariants/d20/proof_obligations/long_dlim/`
- LLN induction bridge: `data/invariants/d20/proof_obligations/long_llnind/`
- global support-gap induction:
  `data/invariants/d20/proof_obligations/long_gapind/`
- eta6 compact structural spine:
  `data/invariants/d20/proof_obligations/eta6_core/`
- proof-obligation registry:
  `data/invariants/d20/proof_obligations/index.json`
- public compiled object: `d20.json`
- bundle certificate: `certificate.json`
- file manifest: `manifests/file_hashes.json`

## Claim Discipline

- A report may say the finite theorem is certified only when its verifier
  passes.
- A report must say the broader goal remains open while any theorem debt above
  remains unresolved.
- Never state that C985 semantic composition, full raw-support measure, all raw
  paths, horizon-16 profunctor existence, or invariant exhaustiveness is proven
  unless a dedicated certificate proves it.
- Negative or obstruction results are productive only when they reduce the
  debt surface, sharpen a boundary, or demote a candidate by certificate.
- Always include the next highest-yield item after emitting a proof report.

## README And Documentation Edits

For documentation-only changes:

- Preserve certified numbers and canonical names.
- Keep numeric ladders strictly increasing and deduplicated.
- If a table is edited, check row count, pipe count, sortedness, and uniqueness.
- Run `git diff --check` before reporting closure.

## Validation Minimums

For proof code:

- focused validator passes;
- focused `src/verify.py` mode passes;
- regenerated registry sees the report if it is a certified bundle artifact;
- broad fast certificate pass returns `PASS`;
- diff hygiene passes.

For documentation:

- structural checks for the edited section pass;
- `git diff --check` passes.

If any validation is skipped, state exactly what was skipped and why.
