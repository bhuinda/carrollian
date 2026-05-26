# D20 Combinatorial Invariant Theorem-Flag Report

Status: provisional draft, validated against the current inventory scan. The
global verifier is not green in this worktree, so this report does not claim
bundle-level closure.

## Draft

This report inventories combinatorial invariant strata that are already present
in the `d20` object or adjacent certificate data, but are either unused by the
main theorem-report registry, under-theoremized, or still represented as proof
obligations rather than theorem flags.

The highest-yield theorem flags are not the already-certified theorem reports.
They are the places where the object exposes stable combinatorial structure but
the registry still lacks a clean theorem boundary, demotion marker, or promotion
condition.

## Witness

Current scan of `d20.json`:

- Object status: `D20_CERTIFIED`.
- Object hash recorded in `d20_sha256`:
  `dc7d6827e55630769a41420d5f1add739ef0fcc91045f16995b5c4ffdd733fd6`.
- JSON invariant entries: `174`.
- CSV invariant entries: `398`.
- NPZ array manifest entries: `18`.

Current scan of `certificate.json`:

- Certified invariant report count: `177`.
- Provisional invariant report count: `5`.
- Demoted invariant report count: `0`.
- Inventory automation scans:
  `data/invariants/d20/{theorems,proof_obligations}/*/report.json`.

Filesystem report scan after tiny-pointer canonicalization:

- Theorem directories: `156`.
- Proof-obligation directories: `27`.
- Directories with report files: `183`.
- Directories without `report.json`: `0`.
- Newly populated canonical alias registry:
  `data/invariants/d20/theorems/tiny_pointer_a985_sector_label_alias_registry/report.json`.

The three empty tiny-pointer placeholder directories with noncanonical label
language were removed after confirming they had no files, no tracked git
entries, and no evidence payloads.

The five provisional proof-obligation reports are:

- `d20_geon_rgba_replay_frame_archive`
- `d20_golay_shell_two_level_lift_probe`
- `d20_golay_shell_three_level_structured_probe`
- `d20_golay_shell_three_level_terwilliger_profile_reps`
- `d20_hamming_gaussian_python_work_archive_import`

## Theorem-Flag Candidates

### 1. Native A236 Midlevel Selector

Evidence:

- `data/a236_compute/cache/*.csv` contributes six A236/B236 branching CSV
  invariants.
- `data/invariants/d20/derived_invariant_reports.json` records the natural
  `S->S` clopen block as dimension `236` and closed under `T985`, but not the
  certified A236 algebra because the center rank is `29` rather than `34`.
- The midlevel selector search says the true A236 selector is not an
  object-induced clopen block, not the natural `S->S` block, not a low-order
  partition from terminal invariants, and not a stable WL-style refinement.

Suggested theorem flags:

- `D20_A236_MIDLEVEL_SELECTOR_STILL_MISSING`
- `D20_A236_NATIVE_FUSION_FUNCTOR_BOUNDARY`
- `D20_A236_BRANCHING_SEED_NOT_CENTER_PROJECTION`

Why it matters:

This is the clearest unused combinatorial seam. The data exists as CSV and
constructor-boundary evidence, but there are no report-backed theorem entries
whose names expose A236 directly. The missing theorem would explain the
`A985 -> A236 -> A42 -> A12` descent without treating A236 as a compact
branching seed.

### 2. Lifted Coorient Formula

Evidence:

- `d20.json` records six coorient/pre-A985 JSON invariant files.
- Only two coorient-facing report directories are theoremized:
  `zero_axiom_coorient_cache` and `zero_axiom_coorient_strict_replay`.
- Generated boundary reports repeatedly state that the four 2576-point lifted
  coorient generator permutations should be derived from a smaller typed
  coorient formula rather than stored as permutations.
- The coorient obstruction report states that ordinary M24 coordinate
  permutations are not enough; the missing formula must include a lifted
  coorient action on the dodecad shell.

Suggested theorem flags:

- `D20_TYPED_COORIENT_LIFT_FORMULA_OPEN`
- `D20_COORIENT_GENERATORS_NOT_M24_COORDINATE_PERMUTATIONS`
- `D20_BE3_ACTION_FROM_ORBITALS_INPUT_BOUNDARY`

Why it matters:

The object already has strong coorient cache and replay evidence, but the
semantic theorem flag should point at the remaining formula problem: replacing
large stored permutations with an intrinsic typed action.

### 3. Golay/W24 Shell Entropy Closure

Evidence:

- There are `17` Golay/W24/Hamming-facing report directories.
- Five provisional proof obligations sit in this zone or directly depend on it.
- The two-level and three-level shell probes report no counterexample for
  `w=12` or `w=16`, but explicitly do not certify the full arbitrary-vector
  shell domination theorem.
- The Terwilliger profile representatives close profile coverage while leaving
  M24 single-orbit separation and SOS inequality certificates open.
- The Hamming/Gaussian archive import replays strong finite layers but keeps
  final entropy contraction inequalities open.

Suggested theorem flags:

- `D20_GOLAY_SHELL_ARBITRARY_VECTOR_THEOREM_OPEN`
- `D20_GOLAY_THREE_LEVEL_SOS_CERTIFICATE_OPEN`
- `D20_W24_TERWILLIGER_PROFILE_COVERAGE_ONLY`
- `D20_HAMMING_GAUSSIAN_PARTIAL_REPLAY`

Why it matters:

This is the biggest cluster of almost-theorem evidence. The existing reports
are useful, but their status strings are too long and diagnostic. A small set
of theorem flags would make the open proof obligations readable at the bundle
level.

### 4. MOG/Hexacode Intrinsic Canonicity

Evidence:

- `data/invariants/d20/d20_research_directions.json` says the hexacode row
  selector is adjoined and certified, while intrinsic canonicity remains a
  research boundary.
- Selector JSON files include MOG, hexacode, W24, and Wu/Golay resolvent
  certificates.
- The current Golay/W24 proof-obligation chain relies on these selectors but
  still marks final canonicity and shell closure separately.

Suggested theorem flags:

- `D20_HEXACODE_ROW_SELECTOR_CERTIFIED`
- `D20_HEXACODE_INTRINSIC_CANONICITY_OPEN`
- `D20_MOG_ROW_GOLAY_SELECTOR_EXTERNAL`

Why it matters:

The selector artifacts are present and useful, but the canonicity boundary is
currently easier to find in research-direction prose than in theorem flags.

### 5. H-Cycle Game-Control Ledger

Evidence:

- `d20.json` embeds a substantial `game_theory` section.
- H-cycle artifacts include primitive cycles, mod-2 residue spectra, pair
  transposition costs, strategy-class atlas data, and automorphism summaries.
- Keyword coverage shows only two report-backed hits for this family, while
  the object carries six JSON and sixteen CSV H-cycle/game-control artifacts.

Suggested theorem flags:

- `D20_HCYCLE_LEDGER_UNDER_THEOREMIZED`
- `D20_HCYCLE_MOD2_RESIDUE_SPECTRUM_PRESENT`
- `D20_HCYCLE_STRATEGY_CLASS_ATLAS_PRESENT`
- `D20_PAIR_TRANSPOSITION_COST_TABLE_PRESENT`

Why it matters:

This is a found-but-underused combinatorial layer. The data is rich enough to
deserve flags that distinguish solved-board, residue-spectrum, and strategy
atlas claims.

### 6. SS-SAT External Evidence

Evidence:

- `d20.json` records `24` SS-SAT JSON invariant entries and `17` SS-SAT CSV
  entries.
- No report-backed theorem directory is keyed directly to SS-SAT.
- The evidence records standalone FRAT checking as blocked and inherited full
  FRAT replay as blocked by analyzer-route explosion.

Suggested theorem flags:

- `D20_SS_SAT_EXTERNAL_EVIDENCE_PRESENT`
- `D20_SS_SAT_STANDALONE_FRAT_CHECKER_BLOCKED`
- `D20_SS_SAT_INHERITED_FRAT_ROUTE_EXPLOSION`
- `D20_SS_SAT_THEOREM_REPORT_MISSING`

Why it matters:

This is not a missing dataset; it is a missing theorem surface. The current
state should be explicit that solver evidence exists, but independent
standalone replay is not theorem-closed.

### 7. Tensor/Stack-Series Evidence

Evidence:

- Keyword coverage sees `41` tensor/stack JSON entries and `345` CSV entries.
- The stack-series stages report certified weighted series data while leaving
  motivic/CoHA realization open.
- The tensor-chain section has plain-name and mechanism-test evidence, but
  little theorem-report coverage keyed directly to tensor/stack names.

Suggested theorem flags:

- `D20_STACK_SERIES_EVIDENCE_PRESENT`
- `D20_STACK_SERIES_MOTIVIC_COHA_OPEN`
- `D20_TENSOR_CHAIN_RAW_SHADOW_CERTIFIED`
- `D20_TENSOR_STACK_THEOREM_SURFACE_THIN`

Why it matters:

This is the largest raw combinatorial inventory by file count. It should not be
forced through one generic readout theorem when the file inventory is already
separated into stack stages and tensor-chain stages.

### 8. Tube, Drinfeld, and Modular Boundary

Evidence:

- The report scan finds `11` tube/modular/sandpile theorem reports.
- `d20.json` also carries `14` tube/Drinfeld/modular JSON entries.
- Existing certificate prose distinguishes closed-loop/tube-center facts from
  full tube modules and full modular data.
- Strict modularity is obstructed, while pseudomodular/lasso layers are
  certified.

Suggested theorem flags:

- `D20_TUBE_CENTER_CERTIFIED_FULL_MODULES_OPEN`
- `D20_HALF_BRAIDING_FULL_SOLVE_REQUIRED`
- `D20_STRICT_MODULARITY_OBSTRUCTED`
- `D20_PSEUDOMODULAR_LAYER_CERTIFIED`

Why it matters:

This layer is partly theoremized already. The missing value is not more generic
coverage, but sharper flags distinguishing what is certified from what is only
scaffolded.

### 9. Tiny-Pointer Canonical Alias Registry

Evidence:

- The tiny-pointer family has `28` theorem directories, all with report-backed
  payloads.
- `tiny_pointer_a985_sector_label_alias_registry` now emits a canonical
  theorem report plus three machine-readable tables:
  `d20_atom_domain.csv`, `sector_label_alias_registry.csv`, and
  `tiny_pointer_d20_atom_primitive_schema.json`.
- The d20 atom source domain is materialized as `C(H6,3)` with `20` atoms.
- The A985 source/raw/perennial/coordinate labels are registered as a
  `39`-row address-alias layer for the certified tiny pointer.

Suggested theorem flags:

- `D20_TINY_POINTER_A985_SECTOR_LABEL_ALIAS_REGISTRY_CERTIFIED`
- `D20_TINY_POINTER_D20_ATOM_PRIMITIVE_SCHEMA_EMITTED`
- `D20_TINY_POINTER_ATOM_TO_SUPPORT_INCIDENCE_OPEN`

Why it matters:

The tiny pointer should be treated as the primitive dereference structure
associated to d20 atoms, not as a loose naming layer around A985 sectors. The
new registry fixes the native atom domain and the A985 address aliases while
leaving the atom-to-support incidence theorem as the next explicit boundary.

### 10. Geon RGBA Replay

Evidence:

- `d20_geon_rgba_replay_frame_archive` has `all_checks_pass=true`.
- Its status is provisional because browser `getImageData` capture remains
  blocked and is not claimed by the certificate.

Suggested theorem flags:

- `D20_GEON_RGBA_ARCHIVE_CERTIFIED`
- `D20_GEON_BROWSER_CAPTURE_BLOCKED`

Why it matters:

The theorem flag should split archive validity from live browser capture. The
current long status string encodes both facts but is awkward to consume.

## Coherence

The candidate list divides into three classes:

1. Present but not report-backed:
   A236 CSV evidence, SS-SAT evidence, tensor/stack-series evidence, H-cycle
   ledgers, and atom-to-support incidence for the tiny-pointer primitive.

2. Report-backed but still proof-obligation/provisional:
   Golay/W24 shell entropy probes, Hamming/Gaussian partial replay, and geon
   RGBA browser-capture blockage.

3. Certified but semantically under-flagged:
   coorient cache/replay, tube/modular boundary strata, MOG/hexacode selector
   strata, and tiny-pointer matrix-unit/address strata.

The highest-yield next theorem flag is the A236 midlevel selector boundary,
because it is central to the object descent and currently has strong negative
evidence without an explicit theorem-report surface.

## Closure

Scoped report validation:

- The inventory counts above were checked against the current `d20.json`,
  `certificate.json`, and report-directory scan.
- The provisional report list was checked against report payloads and their
  current status strings.
- The A236, coorient, and center-idempotent boundary claims were checked
  against `data/invariants/d20/derived_invariant_reports.json`.
- The tiny-pointer alias registry was checked for `20` d20 atom rows, `39`
  A985 alias rows, emitted primitive schema, no noncanonical tiny-pointer
  theorem directory names, and no theorem/proof-obligation directory missing a
  `report.json`.

Global validation:

- `python src\verify.py core` currently fails in this worktree.
- Earlier `python src\verify.py audit` also failed.
- The latest core verifier run reports `24` errors: `16` source-gene hash
  mismatches, genome fixed-point failure, data registry hash mismatch, root
  invariant inventory mismatches, and missing Jacobian saturation cache files.

Therefore, this report is suitable as a draft archaeology map and theorem-flag
work queue, but it is not a certificate of the whole bundle.

## Emit

Recommended next action:

Add a small theorem-flag registry layer for the top three findings:

1. `D20_A236_MIDLEVEL_SELECTOR_STILL_MISSING`
2. `D20_TYPED_COORIENT_LIFT_FORMULA_OPEN`
3. `D20_GOLAY_SHELL_ARBITRARY_VECTOR_THEOREM_OPEN`

Then attach certified per-atom support incidence to the new tiny-pointer alias
registry, so the primitive can dereference from each `C(H6,3)` atom without
collapsing the 20-atom source domain into the 39-sector A985 address layer.
