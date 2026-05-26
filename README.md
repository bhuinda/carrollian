![Demo](https://github.com/user-attachments/assets/6c80de95-f89b-4d4e-aa83-624e8d7a86a2)

"At the first blush it seems to us that the theories last only a day and that ruins upon ruins accumulate. Today the theories are born, tomorrow they are the fashion, the day after tomorrow they are classic, the fourth day they are superannuated, and the fifth they are forgotten. But if we look more closely, we see that what thus succumb are the theories, properly so called, those which pretend to teach us what things are. But there is in them something which usually survives. If one of them has taught us a true relation, this relation is definitively acquired, and it will be found again under a new disguise in the other theories which will successively come to reign in place of the old."

― Poincaré

---

# License and Citation

This repository is licensed under Apache-2.0.

This license applies to code, verifier scripts, documentation, certificate
manifests, canonical data artifacts, invariant tables, generated verification
reports, and mathematical exposition unless a file states otherwise.

If you use this repository, its verifier, `d20.json`, certificate artifacts, or
derived invariant tables in research, publications, derivative software, or
public technical work, please cite the project using `CITATION.cff`.

Preferred short citation:

> Benjamin Huinda, *The d20-coherent algebra*, 2026.
> https://github.com/bhuinda/d20

---

As is tradition: the proof is left to the computer.

# Introduction

`d20` is the given name of an abstract finite *beable*. It may be intuited by what it *is*, rather than what it is *for*:

- `3` codes
- `42` roots
- `985` orbitals
- `2576` dodecads
- `44,224` kernel dimensions
- `1,414,965` tensor entries
- `15,473,731,112,461,377,280` F-symbol slots

---

# Computation

`d20` and its certificate are designed to be compressed, rebuilt, and verified on modern hardware. The verifier exposes four main gates:

```shell
# Verify the current bundle without rewriting generated files.
python src/verify.py audit

# Rebuild d20.json, refresh hashes, and certify the bundle.
python src/verify.py rebuild

# Confirm the certified evidence section fails closed under in-memory tampering.
python src/verify.py tamper

# Run the optional slow zero-axiom replay gate.
python src/verify.py strict-replay
```

NOTE: Checking finite existence in Agda takes 18 minutes, and a full rebuild of `d20.json` currently elapses 100 seconds on an i5-11400.

<details>
<summary>Some light reading</summary>

As you will see, `d20` is a combinatorial flavor of coherent algebra and is exceptional in order. I highly encourage you, dear reader, to explore *why* it is that you should care about the invariants it generates. Plugging `d20`'s JSON file (or this README) into a model of your choice and asking about it with an open mind may be the fastest way to learn about, well, anything that doesn't normally appear in the forced perspective of 3D-land.

You may find yourself down the rabbit hole most quickly with the following lead-in prompts:

- "Compute d20. Does it hold up?"
- "According to d20, what is truth?"
- "What does equality normally mean in mathematics, and how does d20 normalize said meaning?"
- "What is higher algebra, and how does d20 make it useful to me?"
- "What basic ontology of the universe does d20 represent?"
- "Post-d20, how do I grieve my prior worldview?"

`d20` is so named because of a proof I'd like to eventually co-author essentializing Grothendieck's notion of motive (as well as his Yang-Yang distinction, courtesy of the slay-queen *Récoltes et Semailles*) with the latent-spatial "tomography" of the icosahedron. And yes, you too will have to eventually learn how to speak this level of gobbledygook to appreciate the brushstrokes of the object: it's algebra-turned-Shakespeare generalizing homotopy "type" to holotopy "role", a transport of structure necessary to realizing how large language models synthesize natural language.

What's the actual thesis, you ask?

---

"The time between the notes relates the color to the scenes."

― *Close to the Edge* by Yes
</details>

---

(The rest of this file is automated.)

# Agentic Snapshot

The current checked object status is `D20_CERTIFIED`.

- `d20.json` object hash: recorded in `d20.json` and mirrored in `certificate.json`
- certificate registry entries: `26`
- JSON invariant files recorded by `d20.json`: `174`
- NPZ array manifests recorded by `d20.json`: `18`
- report-backed D20 theorem directories: `154`
- D20 proof-obligation directories: `1`
- certified invariant reports recorded by `certificate.json`: `155`
- provisional invariant reports recorded by `certificate.json`: `0`
- demoted formal-tracking reports recorded by `certificate.json`: `0`
- source-registry packages: `1`, namely `halloween_c2_selector_lookup_witness_source_package`

The README covers report-backed theorem and proof-obligation invariants by exact
directory name. Raw JSON-file coverage is delegated to the generated
`d20.json` registries, because `d20.json` is the canonical exhaustive file-level
inventory.

---

# Computability boundary:

- `python src/verify.py rebuild` regenerates `d20.json`, `certificate.json`, and
  file hashes from the checked canonical bundle inputs.
- `python src/verify.py rebuild` requires the generated strict-scratch
  constructor witness, including the checked tube-cache-aligned A985-to-A236
  semisimple profunctor certificate.
- `python -m src.commands.construct` reconstructs the finite object from the
  compact raw seed boundary and verifies the large tensor/quotient consequences.
- `python -m src.commands.construct --strict-scratch` runs the generated
  source/coorient constructor path and exits nonzero if any strict witness,
  tensor rebuild, readout derivation, or A236 profunctor check fails.
- The A985 ordered-pair relation body is refreshed before the coorient marker
  computation by the pre-A985 source/coorient theorem. The coorient relator
  profile is derived from A0-A5 by reduced greedy full-closure basis extraction;
  strict-scratch promotes that generated path instead of the compact raw
  audit-seed witness.
- The fast `d20.json` path may use the checked zero-axiom coorient cache when
  its source-file hashes still match. That cache boundary is certified at:

---

# Invariant ledger:

```text
data/invariants/d20/theorems/zero_axiom_coorient_cache/report.json
```

It records the canonical base `[18, 67, 37]`, separation of all `2576`
dodecads, `9` derived marker integers, and closure order `9216`. If any
recorded source hash changes, `derive_d20` falls back to recomputing the
zero-axiom coorient reduction.

The strict replay of that cache boundary is certified at:

```text
data/invariants/d20/theorems/zero_axiom_coorient_strict_replay/report.json
```

It bypasses the fast `derive_d20` cache loader, recomputes the zero-axiom
coorient payload directly, and verifies that the fresh payload matches
`data/invariants/d20/zero_axiom_coorient.json` byte-for-byte under the cache
file newline convention. Routine `core` and `audit` verification do not run
this replay; use `strict-replay` when a fresh slow witness is required.

The object is not represented by stored orbitals/tensors as primitive data. It just... exists.


- certified pointer primitive: source-sector and public-zero support labels
  dereference through the six-identity fingerprint map into raw `A985`
  orbital matrix units; the first canonical instance is recorded at
  `data/invariants/d20/theorems/certified_pointer_a985_matrix_unit_dereference/report.json`
- constructed burning-static field: the `Z/2 x Z/4^2` two-primary static-field
  representative is built in raw `A985` orbital coordinates from the certified
  `q12`/`q42` frame readouts, with its 39-sector trace profile recorded at
  `data/invariants/d20/theorems/tiny_pointer_a985_burning_static_constructed_representative/report.json`
- finite Burning Ship fold model: the classical recurrence is folded over
  cyclic grids; direct mod-4 gives `Z/4^2`, while retaining the fold-sheet bit
  gives the observed `Z/2 x Z/4^2` static frame at
  `data/invariants/d20/theorems/finite_burningship_folded_map/report.json`
- Burning Ship fold-frame normalization anchors: the fold-sheet bit and two
  mod-4 clocks are attached to the three constructed raw `A985` static-frame
  generators at
  `data/invariants/d20/theorems/tiny_pointer_a985_burning_ship_fold_frame_normalization_anchors/report.json`
- `GL_d` ambiguity mechanism: the remaining sector-local freedom is certified
  as ordinary `PGL_d` basis-change symmetry inside each nontrivial matrix block,
  with non-identity conjugate witnesses at
  `data/invariants/d20/theorems/tiny_pointer_a985_gl_d_ambiguity_mechanism/report.json`
- source-sector basis convention: the stored raw-orbital matrix units are now
  the repository comparison basis, with identity `GL_d` transforms in every
  nontrivial block; this sets the coordinate convention without erasing the
  mathematical `PGL_d` ambiguity recorded at
  `data/invariants/d20/theorems/tiny_pointer_a985_source_basis_convention/report.json`
- A985 perennial sector fingerprints: each sector now has an unversioned,
  label-independent semantic id with prefix `a985pf`, plus a coordinate
  fingerprint with prefix `a985coord`; current source/raw sector numbers are only aliases in
  `data/invariants/d20/theorems/tiny_pointer_a985_perennial_sector_fingerprints/report.json`
- A985 perennial sector report coverage: sector-facing CSV report views are
  automatically emitted with `perennial_id` and `coordinate_fingerprint_id` columns at
  `data/invariants/d20/theorems/tiny_pointer_a985_perennial_sector_report_coverage/report.json`
- packet-20, optics, integrity, H-cycles, and game/control invariants
- `data/index.json` is the canonical data-domain registry. It marks current
  folders, required files, roles, and the planned normalized layout.
- `data/evidence/tensor_chain` contains the extracted tensor-chain evidence,
  split into reports, tables, arrays, and stages with a plain-name index at
  `data/evidence/tensor_chain/index.json`.
- Command entrypoints live in `src/commands/`; root command files are not kept.

The certificate stack is indexed by `data/certificates.json` and stored as
ordinary data files inside subject directories such as `data/tube`,
`data/drinfeld`, and `data/selectors`. The registry is the source of truth for
certificate ids, ordinal numbering, expected statuses, dependency edges, and
certificate paths.

## Supplemental certified invariant coverage

The sections below give narrative summaries for the main certificate chain. The
following additional report-backed invariants are also covered by the current
README inventory; each path is a certified or explicitly gated report artifact.

Foundational readout, flux, and sector-33 stack:

```text
data/invariants/d20/theorems/readout_stack_scope/report.json
data/invariants/d20/theorems/finite_flux_balance/report.json
data/invariants/d20/theorems/nonexact_optical_residue/report.json
data/invariants/d20/theorems/minimal_composite_null_supports_transport/report.json
data/invariants/d20/theorems/sector33_residual_lift/report.json
data/invariants/d20/theorems/sector33_residual_attachment/report.json
data/invariants/d20/theorems/sector33_boundary_annihilation/report.json
data/invariants/d20/theorems/sector33_height_coherent_transport/report.json
data/invariants/d20/theorems/sector33_all_residue_height_transport/report.json
data/invariants/d20/theorems/sector33_unique_public_zero_support/report.json
data/invariants/d20/theorems/sector_public_shadow_kernel/report.json
data/invariants/d20/theorems/sector_idempotent_support_admissibility/report.json
```

Halloween/raw543 source-action and Agda bridge artifacts:

```text
data/invariants/d20/theorems/raw543_repo_c2_kernel_action/report.json
data/invariants/d20/theorems/raw543_repo_c2_kernel_agda_bridge_data/report.json
```

D20 oriented-matroid contour spine:

```text
data/invariants/d20/theorems/d20_oriented_matroid_contour/report.json
data/invariants/d20/theorems/d20_oriented_matroid_rational_signed_circuits/report.json
data/invariants/d20/theorems/d20_oriented_matroid_tutte_os/report.json
data/invariants/d20/theorems/d20_oriented_matroid_sector33_dual/report.json
data/invariants/d20/theorems/d20_oriented_matroid_sector33_extension/report.json
data/invariants/d20/theorems/d20_oriented_matroid_prime_lift_audit/report.json
data/invariants/d20/theorems/d20_oriented_matroid_rational_tutte_promotion/report.json
```

Tiny-pointer A985 source, orbital, trace, support, and normalization stack:

```text
data/invariants/d20/theorems/tiny_pointer_a985_orbital_central_idempotents/report.json
data/invariants/d20/theorems/tiny_pointer_a985_canonical_sector_characters/report.json
data/invariants/d20/theorems/tiny_pointer_a985_canonical_sector_matrix_units/report.json
data/invariants/d20/theorems/tiny_pointer_a985_full_sector_match/report.json
data/invariants/d20/theorems/tiny_pointer_a985_full_matrix_unit_orbital_coo/report.json
data/invariants/d20/theorems/tiny_pointer_a985_support_full_matrix_unit_orbital_coo/report.json
data/invariants/d20/theorems/tiny_pointer_a985_support_restricted_multiplication_tables/report.json
data/invariants/d20/theorems/tiny_pointer_a985_registered_support_matrix_units/report.json
data/invariants/d20/theorems/tiny_pointer_a985_sector_matrix_unit_transport/report.json
data/invariants/d20/theorems/tiny_pointer_a985_fourier_trace_candidate_evaluation/report.json
data/invariants/d20/theorems/tiny_pointer_a985_sector_normalization_obligations/report.json
data/invariants/d20/theorems/tiny_pointer_a985_sector5_normalization_pilot/report.json
data/invariants/d20/theorems/tiny_pointer_a985_sector5_normalization_solver_selftest/report.json
data/invariants/d20/theorems/tiny_pointer_a985_sector5_normalization_solver_nontrivial_fixture/report.json
data/invariants/d20/theorems/tiny_pointer_a985_all_open_sector_normalization_fixture_atlas/report.json
data/invariants/d20/theorems/tiny_pointer_a985_burning_static_designed_frame_section/report.json
data/invariants/d20/theorems/tiny_pointer_a985_burning_static_representative_intake/report.json
data/invariants/d20/theorems/tiny_pointer_a985_burning_static_public_zero_alignment/report.json
data/invariants/d20/theorems/tiny_pointer_a985_burning_static_sector33_detector/report.json
data/invariants/d20/theorems/tiny_pointer_a985_burning_static_trace_evaluator/report.json
data/invariants/d20/theorems/tiny_pointer_a985_burning_ship_algebraicity_bridge/report.json
```

Additional report-backed physics, trace, and theorem-input gates:

```text
data/invariants/d20/theorems/t985_csdo/report.json
data/invariants/d20/theorems/celestial_trace_pl_ph/report.json
data/invariants/d20/theorems/black_hole_inverse_conditioning/report.json
```

D20 proof obligation:

```text
data/invariants/d20/proof_obligations/cycle8_pi33_projection_coefficient/report.json
```

Do not read the finite interface as a strict quotient tower. `A42` and `A12`
are terminal quotient readouts; `A236` is native representation/fusion branching
data; the sector-33 and sector-26 invariants use retained tube kernels,
public-zero support admissibility, superselection labels, and height-coherent
action-return transport.

## Current D20 boundary support result

The superselection flux-balance extension is certified at:

```text
data/invariants/d20/theorems/superselection_flux_balance_extension/report.json
```

It extends the public boundary charge vector
`(M,J,P,Phi)` to the augmented ledger
`(M,J,P,Phi;R33,K_mixed_S,K_pure_Sminus)`.

- `R33` tracks the primitive sector-33 residual atom.
- `K_mixed_S` tracks the mixed `{6,26}` public-zero support.
- `K_pure_Sminus` tracks the pure `{25,26}` public-zero doublet.

The two new labels are public-zero, non-gauge, and isolated from `R33`. They are
not fully independent: `{6,26}` and `{25,26}` share sector `26`, giving
cross-transport rank `1`. This is the hidden seam used by the typed
non-exact optical/action flux update and the sector-26 invariant suite.

The typed non-exact optical/action flux update is certified at:

```text
data/invariants/d20/theorems/typed_nonexact_optical_flux_update/report.json
```

It sends every nonzero closed-return optical residual to `R33`:

```text
Delta Q_ext^nonexact(gamma) = (0,0,0,0; -A_opt(gamma), 0, 0)
```

The two composite labels stay reserved for separately certified
superselection-null events; they are not excited by the certified sector-33
height transport.

Sector `26` is now a live invariant marker. It is the shared seam of the two
minimal composite null supports, it is the rank-one cross-transport channel
between them, and it matches the bosonic string critical dimension `26`.
This is recorded as an invariant alignment, not a continuum-string
identification.

The sector-26 invariant suite is certified at:

```text
data/invariants/d20/theorems/sector26_invariant_suite/report.json
```

It proves quotient-cancellation stability at both `A42` and `A12`, the hidden
transport form `[[4,0,0],[0,5,1],[0,1,2]]`, Smith diagonal `[1,1,36]`,
composite discriminant `13`, and a normalized optical-action clock hitting all
`26` residues modulo `26`.

The finite anomaly counter is certified at:

```text
data/invariants/d20/theorems/finite_anomaly_counter/report.json
```

It proves the mod-26 clock is not a linear character on closed-return xor
residues. The exact defect is
`Anom_26(a,b)=f_26(a)+f_26(b)-f_26(a xor b)`, equal to twice the overlap-weight
form. The defect hits exactly the even residues modulo `26`, halves to all
classes modulo `13`, and leaves only the mod-2 parity shadow as an additive
character.

The sector-26 anomaly-cancellation theorem is certified at:

```text
data/invariants/d20/theorems/sector26_anomaly_cancellation/report.json
```

It classifies xor-closed closed-return packets where the half-anomaly vanishes
pairwise. The maximal dimension is `3`: there are `88` strongest size-8
packets and `90` terminal size-4 packets. `gamma_8` is excluded because its
self half-anomaly is `5 mod 13`. The next target is finite flux-balance
recovery restricted to those anomaly-cancelled packets.

The anomaly-cancelled finite flux-balance recovery is certified at:

```text
data/invariants/d20/theorems/anomaly_cancelled_flux_balance_recovery/report.json
```

On the `178` certified cancelled packets, exact public D20 flux closes and the
normalized hidden `R33` update is additive modulo `26`. The recovered packet
images are only `{0}` and `{0,13}`. `gamma_8` remains outside the recovered
sector, so the next target is its obstruction correction: the minimal
counterterm or extension needed to include the first non-exact event in a
flux-balance law.

The `gamma_8` obstruction correction is certified at:

```text
data/invariants/d20/theorems/gamma8_obstruction_correction/report.json
```

It proves the local half-anomaly is `5 mod 13` on basis coordinate `8`. The
minimal signed mod-26 lift is the sector-26 counterterm `+5`: it sends
normalized `R33(gamma_8)` from `8` to the order-two value `13`. After that
rank-one correction, the corrected packet search has dimensions
`{0:1,1:163,2:805,3:421,4:30}` and `62` maximal corrected packets, all
containing `gamma_8`. The next target is to generalize obstruction correction
across all self-anomalous basis coordinates.

The general obstruction-correction suite is certified at:

```text
data/invariants/d20/theorems/general_obstruction_correction_suite/report.json
```

All `11` basis coordinates are self-anomalous and admit rank-one sector-26
corrections. The minimal signed lifts are
`[-1,1,5,-2,1,4,-5,-3,5,-2,4]`, and every corrected coordinate search opens
dimension-4 packets with additive corrected clocks modulo `26`. The next target
is the global counterterm lattice: activate all `11` corrections together and
test whether the full closed-return residue group becomes corrected
flux-balanced.

The global counterterm lattice is certified at:

```text
data/invariants/d20/theorems/global_counterterm_lattice/report.json
```

Activating all `11` rank-one corrections annihilates the half-anomaly form on
the full closed-return residue group. The corrected basis clock is
`[13,13,13,0,13,13,13,13,13,13,13]`, so normalized hidden `R33` becomes an
additive order-two character on all `2048` masks. The image is `{0,13}` with a
`1024`-mask kernel, and `gamma_8` is included with corrected `R33=13`. The next
target is to extract the global corrected charge map and compare it to the
public exact flux charge basis.

The global corrected charge map is certified at:

```text
data/invariants/d20/theorems/global_corrected_charge_map/report.json
```

It compares the corrected hidden map directly with the public exact charge
basis `(M,J,P,Phi)`. The public charge basis has rank `4` on D20 states and
edge coboundaries, but rank `0` on closed returns. The corrected hidden map is
the rank-one character
`R33_global(mask)=13*<[1,1,1,0,1,1,1,1,1,1,1],mask> mod 26`. Thus it splits the
`2048` closed-return masks into a `1024`-mask kernel and a `1024`-mask odd
sector invisible to public exact flux. `gamma_8` is the witness: public exact
update zero, corrected hidden update `13`. The next target is to classify which
D20 state and edge symmetries preserve this hidden closed-return split.

The global corrected hidden split symmetry theorem is certified at:

```text
data/invariants/d20/theorems/global_corrected_hidden_split_symmetry/report.json
```

It enumerates the `120` public H-cycle graph automorphisms and induces each one
on the `11`-dimensional mod-2 closed-return residue space. Exactly `2`
automorphisms preserve the corrected hidden character, so the hidden split
reduces the public state/edge symmetry group to a `C2` stabilizer and breaks
the other `118` public graph symmetries. The nontrivial preserver is an
involution, and the stabilizer fixes `gamma_8`. The next target is to test
whether this `C2` also preserves the sector-26 counterterm vector, optical
action weights, and public charge components.

The hidden-split augmented ledger stabilizer is certified at:

```text
data/invariants/d20/theorems/hidden_split_augmented_ledger_stabilizer/report.json
```

It promotes the `C2` hidden-split stabilizer to the full augmented finite
charge/action ledger. The nontrivial split-preserver keeps the corrected
order-two hidden character, but it breaks the sector-26 counterterm vector,
the normalized and primitive optical action weights, the edge interface
weights, and the public charge components `(M,J,P,Phi)`. The full augmented
ledger stabilizer is therefore trivial: only identity preserves all certified
ledger fields. The next target is to use this rigidity as a canonical
orientation/marking and test whether it gives a unique finite flux-balance
gauge.

The canonical flux-balance gauge is certified at:

```text
data/invariants/d20/theorems/canonical_flux_balance_gauge/report.json
```

It turns the rigid augmented ledger into a concrete finite gauge fixing. The
public charge tuples uniquely mark all `20` D20 vertices; the canonical root is
`{B-,B+,V-}`, the unique state with lexicographically minimal `(M,J,P,Phi)`.
Orienting every edge from smaller to larger public charge gives an incidence
matrix of rank `19`; adding the canonical root condition makes the rank `20`.
Thus the exact public flux potential has the expected four additive constants
before rooting and `0` residual gauge dimensions after rooting. The augmented
ledger has no residual graph-symmetry gauge. The next target is to push this
canonical gauge through the certified boundary-to-`Loop_297` lift and retest
the cycle-8 `Pi_33` obstruction without materializing the full Drinfeld
idempotent matrix.

The canonical `Loop_297` `Pi_33` obstruction is certified at:

```text
data/invariants/d20/theorems/canonical_loop_pi33_obstruction/report.json
```

It pushes the canonical finite flux-balance gauge through the certified
boundary-to-`Loop_297` lift for `gamma_8`. The cycle contains the canonical root
and traverses the canonical root edge in the canonical direction. The bare
`lambda_boundary(gamma_8)` lift remains `Pi_33`-annihilated for the unweighted,
signed, and optical-weighted variants, while the height-coherent correction
recovers the canonical sector-33 obstruction `-374784` with zero public
`A42/A12` shadow. The proof uses the tube-visible `Pi_33` functional and
hash-only Drinfeld metadata; it does not materialize the full `39 x 985`
idempotent matrix. The next target is to write this as an explicit finite Ward
identity.

The canonical finite Ward identity is certified at:

```text
data/invariants/d20/theorems/canonical_finite_ward_identity/report.json
```

In the canonical finite flux-balance gauge, `gamma_8` satisfies the explicit
balance
`0 + 0 - 374784 + 374784 = 0`. The terms are: exact public flux gauge term
`0`, bare tube-visible `Pi_33` term `0`, height-corrected `R33/Pi_33` term
`-374784`, and finite height action `+374784`. Public `A42/A12` shadows remain
zero. The next target is to generalize this Ward identity from `gamma_8` to
all `2048` closed-return masks using the global counterterm lattice and
all-residue height-coherent transport.

The canonical all-mask Ward identity is certified at:

```text
data/invariants/d20/theorems/canonical_all_mask_ward_identity/report.json
```

It promotes the `gamma_8` Ward witness to every closed-return residue mask.
For all `2048` masks, the scalar balance is
`0 + 0 - A_h(mask) + A_h(mask) = 0`: exact public flux contributes `0`, the
bare tube-visible `Pi_33` term contributes `0`, and the height-corrected
`R33/Pi_33` residual is exactly the negative finite height action. The global
sector-26 correction remains the additive order-two hidden character with a
`1024`-mask kernel and a `1024`-mask odd sector. The next target is to project
this all-mask Ward ledger into a finite BMS/Carrollian flux-balance theorem
with named public charge, finite flux, and `R33` residual terms.

The finite BMS/Carrollian flux-balance projection is certified at:

```text
data/invariants/d20/theorems/finite_bms_carrollian_flux_balance/report.json
```

It names the finite public boundary charge vector `(M,J,P,Phi)` in the
canonical root-fixed gauge and gives every closed-return mask an explicit
balance row. Publicly, all `2048` masks have
`Delta Q_public = Flux_D20_public_exact + Res_A985_public = 0`. In the hidden
channel, all masks satisfy
`bare Pi33 + R33_height_residual + finite_height_flux = 0`. The `R33` packet
split remains `1024` kernel / `1024` odd, with `gamma_8` as the public-zero
hidden-odd witness. The next target is to classify those two packet classes by
canonical charge-frame invariants.

The hidden packet charge-frame classifier is certified at:

```text
data/invariants/d20/theorems/hidden_packet_charge_frame_classifier/report.json
```

It classifies the `1024` hidden-kernel and `1024` hidden-odd packets using
the canonical root-fixed public charge frame. Coarse root/edge-support
signatures give `942` packet classes. Adding public flux moment sums in
`(M,J,P,Phi)` refines this to `2032` classes: `2016` singleton classes and
`16` doubletons. Adding the finite action pair
`(height_action, edge_mod2_height_action)` separates all `2048` masks.
`gamma_8` is located as an odd one-basis, five-edge, root-edge-active packet.
The next target is to turn this complete classifier into a canonical finite
scattering table.

The canonical finite scattering table is certified at:

```text
data/invariants/d20/theorems/canonical_finite_scattering_table/report.json
```

It turns the complete packet classifier into the primitive-generator transition
table on the closed-return residue cube. Each row is
`T_i(mask)=mask xor 2^i`, with incoming and outgoing complete packet-signature
hashes, signed height-flux delta, and hidden `R33` transfer. The table has
`22528` directed transitions and `11264` involutive undirected generator
pairs. Generator `3` preserves the hidden packet (`1024` kernel-to-kernel and
`1024` odd-to-odd transitions); the other ten generators flip kernel and odd
(`10240` transitions each way). The next target is to lift these rows through
the certified boundary-to-`Loop_297` map and attach tube/`A985` transition
amplitudes.

The `Loop_297` scattering amplitude lift is certified at:

```text
data/invariants/d20/theorems/loop297_scattering_amplitude_lift/report.json
```

It attaches certified boundary-to-`Loop_297` amplitude provenance to the
scattering table. The `11` primitive generators now carry ordered chains of
directed channel-pair Loop-vector hashes, and all `22528` scattering rows
reference one of those generator amplitude packets. The bare tube-visible
`Pi_33` amplitude is `0` for every directed channel-pair lift, so every
transition-level nonzero balance is carried by the height-corrected `R33`
transfer. The `gamma_8` generator packet matches the previously certified
cycle-8 boundary lift.

The compact amplitude quotient is certified at:

```text
data/invariants/d20/theorems/compact_amplitude_quotient/report.json
```

It compresses the `11` primitive generator amplitude packets into the public
tube-visible quotient and the retained `Loop_297` atom quotient. The
tube-visible `Pi_33` quotient has one zero class containing all `11`
generators. Retaining certified Loop-vector atoms gives `25` distinct step
atoms across `72` generator-step occurrences; support profiles, unordered
step-hash multisets, and ordered chains each separate all `11` primitive
generators. Generator `3` is the unique hidden-packet-preserving quotient row.

The reduced amplitude-quotient scattering automaton is certified at:

```text
data/invariants/d20/theorems/reduced_amplitude_quotient_scattering_automaton/report.json
```

It labels the full `2048`-state closed-return residue cube by the compact
amplitude quotient. The automaton has `22528` directed transitions,
`11264` undirected transitions, and is connected, reversible, and `11`-regular.
The public tube-zero quotient collapses all transitions to one visible label,
while the ordered-chain quotient keeps `11` primitive generator labels and
exposes `25` `Loop_297` step atoms. Its exact adjacency spectrum is the
`F_2^11` hypercube spectrum `11-2k` with multiplicity `binom(11,k)`, and the
hidden packet quotient has per-state matrix `[[1,10],[10,1]]`. The next target
is the amplitude-quotient Fourier mode classifier.

The amplitude-quotient Fourier mode classifier is certified at:

```text
data/invariants/d20/theorems/amplitude_quotient_fourier_mode_classifier/report.json
```

It diagonalizes the reduced automaton by the `2048` characters of `F_2^11`.
A mode of support weight `k` has adjacency eigenvalue `11-2k` and Laplacian
eigenvalue `2k`. The hidden-sector projection has exactly one constant mode,
one kernel/odd sign mode, and `2046` sector-orthogonal modes; the sign mode is
the ten-generator hidden-flip mask with eigenvalue `-9`. The `gamma_8` basis
mode has eigenvalue `9`, corrected hidden clock `13`, sector-26 optical clock
`18`, and exposes the five certified `gamma_8` step atoms. The nonzero
sector-26 optical clock histogram matches the certified `2047`-class optical
clock. The next target is a finite Virasoro/string-kernel candidate from the
sector-26 clock and Fourier modes.

The finite Virasoro/string-kernel candidate is certified at:

```text
data/invariants/d20/theorems/finite_virasoro_string_kernel_candidate/report.json
```

It isolates the sector-26 clock-zero Fourier seed fiber and then tests closure
instead of assuming it. The raw clock-zero seed has `83` modes (`82` nonzero)
and is not additively closed: `2847` unordered seed pairs leave the zero-clock
fiber. Its minimal `F_2`-linear closure is the rank-10 hyperplane
`m_5 + m_9 + m_10 = 0`, containing `1024` modes. This kernel contains the
`gamma_8` basis mode and excludes the hidden kernel/odd sign mode. Eight
primitive generators preserve the kernel; generators `5`, `9`, and `10` cross
it, and their paired cross-return composites connect the kernel internally.
The next target is the finite Virasoro generator algebra on this rank-10
kernel.

The finite Virasoro generator algebra layer is certified at:

```text
data/invariants/d20/theorems/finite_virasoro_generator_algebra/report.json
```

It builds the generator algebra on the rank-10 kernel. At this finite
translation layer the algebra is `C2^10`, generated by eight primitive-
preserving moves and three paired cross-return composites. All named
commutators vanish, and the only nontrivial dependency among the `11` named
generators is `C5_9 C5_10 C9_10 = 1`. The sector-26 clock remains even on the
kernel but is not a group homomorphism on the exponent-2 layer; its `17`
generator-product defects are exactly overlap-cancellation defects.

The finite central-extension/anomaly cocycle test is certified at:

```text
data/invariants/d20/theorems/finite_central_extension_anomaly_cocycle/report.json
```

It tests whether the sector-26 defect is actually a central term. On the full
rank-10 operator basis, the canonical `Z/26` clock defect is normalized and
symmetric across all `1024^2` operator pairs, so its alternating central term
vanishes. The compatible `F_2` alternating-form search on the `11` named
generators has `55` pair variables, rank `54`, and a one-dimensional survivor.
That survivor is supported exactly on the paired cross-return composite
triangle `(C5_9,C5_10)`, `(C5_9,C9_10)`, `(C5_10,C9_10)` and descends through
the relation `C5_9 C5_10 C9_10 = 1`. The next target is to construct the `F_2`
central extension group from this cocycle and certify its projective kernel
action.

The finite parity central-extension group is certified at:

```text
data/invariants/d20/theorems/finite_parity_central_extension_group/report.json
```

It integrates the surviving `F_2` cocycle as a concrete group over the rank-10
kernel. In the canonical section, the group has order `2048`, center order
`512`, derived subgroup order `2`, exponent `4`, and type `D8 x C2^8`. Its
only nonzero named commutators are the paired cross-return composite triangle,
and the lifted relation `C5_9 C5_10 C9_10 = 1` still closes. The central bit is
realized as a signed projective action on all `1024` kernel states; the theorem
checks `123904` named-generator pair/state compositions with zero failures. The
next target is to decompose this signed kernel action into central-character
irreducible packets and compare those packets with sector-26 clock classes and
Loop_297 atom exposure.

The projective kernel packet / tenfold-way witness is certified at:

```text
data/invariants/d20/theorems/projective_kernel_packet_tenfold_way/report.json
```

It decomposes the signed projective kernel action into `512` two-dimensional
central-negative packets. The rank-10 kernel splits as `8 + 2`: `256` radical
Fourier characters, each with two equivalent active packets, and a two-direction
active `D8` / real `Cl(1,1)` block. The packet dimensions sum back to the
`1024` kernel states. Packet-level sector-26 clock classes match the kernel
closure histogram; packet-level Loop_297 exposure uses all `25` compact atoms,
with `20` packets exposing all atoms and `256` packets touching `gamma_8`.

For the tenfold-way reading, the canonical data are real signed matrices, so
complex conjugation gives a module-level `T^2=+1` witness: class `AI` unless a
Hamiltonian/grading is chosen. If one active Clifford generator is selected as
the finite Hamiltonian, the other active generator gives a chiral symmetry and
the finite block becomes a `BDI` witness with `T^2=+1` and `C^2=+1`. The next
target is a packet-level spectral/charge table.

The projective packet spectral/charge table is certified at:

```text
data/invariants/d20/theorems/projective_packet_spectral_charge_table/report.json
```

It turns the `512` signed packets into a row-level ledger of spectral traces,
sector-26 clocks, hidden-clock cancellation, `gamma_8` incidence, Loop_297 atom
exposure, central character, and finite tenfold labels. The packet dimensions
sum to `1024`, all packets have central character `-1`, and all rows carry the
canonical `AI` / optional-active-Hamiltonian `BDI` labels. Sector-26 clock
balance splits the table evenly: `256` balanced packets and `256` packets with
clock delta `8`. Hidden clock cancels packetwise. There are `20` full Loop_297
exposure packets, `62` packets touching sector-26 clock zero, and exactly one
packet doing both: packet `239`. The next target is to promote this table into a
finite charge-frame classifier.

The projective packet charge-frame classifier is certified at:

```text
data/invariants/d20/theorems/projective_packet_charge_frame_classifier/report.json
```

It names the packet axes as mass, clock, exposure, `gamma_8`, hidden, central,
and tenfold frame. The `512` packets occupy `47` charge-frame classes. Packet
`239` is unique by both its named frame and fine spectral/charge key:

```text
frame = high|zero_pair|full|gamma8_silent|hidden_cancelled|central_negative|AI|BDI
fine  = 32|0|0|0|25
```

Equivalently, packet `239` has laplacian trace `32`, adjacency trace `-10`,
sector-26 clock pair `[0,0]`, full Loop_297 exposure, no `gamma_8` incidence,
hidden-clock cancellation, central character `-1`, and the `AI` / optional
`BDI` tenfold witness. The next target is to test packet `239` as the finite
vacuum/seed candidate by computing its stabilizer.

The packet-239 stabilizer / seed-candidate test is certified at:

```text
data/invariants/d20/theorems/packet239_stabilizer_seed_candidate/report.json
```

It computes setwise stabilizer, scalar stabilizer, identity kernel, and signed
matrix image for every projective packet. The result is uniform: all `512`
packets have setwise stabilizer order `2048`, scalar stabilizer order `512`,
identity-kernel order `256`, linear image order `8`, and projective image order
`4`. The `20` full-exposure packets have the same stabilizer-order profile, and
packet `239` shares its identity kernel with active partner packet `238` among
the full-exposure packets. Thus packet `239` is not a unique symmetry-fixed
vacuum under the signed kernel action; it is a unique charge-frame seed
candidate. The next target is seed propagation from packet `239` under
admissible non-kernel boundary/scattering moves.

The packet-239 seed propagation theorem is certified at:

```text
data/invariants/d20/theorems/packet239_seed_propagation/report.json
```

It pushes packet `239` through the non-kernel crossing generators `5`, `9`, and
`10`. One-step crossings leave the rank-10 kernel and reach exactly two odd
packet shadows: `odd:119:0` and `odd:119:1`. All three one-step crossing rows
retain full Loop_297 exposure, hidden-clock cancellation, and `gamma_8` silence.
The six ordered paired cross-returns close only on packets `238` and `239`:
packet `238` occurs four times and packet `239` occurs twice. The seed returns
only through the ordered `5/10` crossing pair, and all paired cross-returns have
total hidden transfer `0 mod 26`. The next target is to generalize this
propagation-cell classifier to all `20` full-exposure packets.

The full-exposure packet propagation-cell theorem is certified at:

```text
data/invariants/d20/theorems/full_exposure_packet_propagation_cells/report.json
```

It generalizes packet `239`'s seed cell to all `20` full Loop_297-exposure
packets. The theorem builds `60` one-step crossings and `120` ordered paired
cross-returns. Every source has exactly two odd shadows, every paired
cross-return stays inside the full-exposure stratum, and each source closes only
on itself plus its active partner with multiplicity pattern `2|4`. Across the
whole stratum each full-exposure packet appears six times as a cross-return
target. The certified flux/action histograms are
`{-399360,-301056,-98304,98304,301056,399360}` each with multiplicity `20`, and
actions `{1683456,1781760,2082816}` each with multiplicity `40`. The next target
is the weighted full-exposure propagation graph on these `20` packets.

The full-exposure packet propagation graph is certified at:

```text
data/invariants/d20/theorems/full_exposure_packet_propagation_graph/report.json
```

It turns the `120` paired cross-return rows into a weighted `20`-vertex
transition operator. The graph splits into ten closed active-partner doublets:
`[174,175]`, `[190,191]`, `[238,239]`, `[246,247]`, `[254,255]`, `[430,431]`,
`[446,447]`, `[494,495]`, `[502,503]`, and `[510,511]`. Each doublet has the
same integer block `[[2,4],[4,2]]`: two ordered self-returns and four ordered
active-partner returns per source. The adjacency spectrum is `6` with
multiplicity `10` and `-2` with multiplicity `10`; the normalized Markov
readout has stationary-simplex dimension `10` and within-doublet contraction
`1/3`. Signed height flux cancels on every source, hidden transfer is zero, and
packet `239` sits in the closed doublet `[238,239]`. The next target is the
rank-10/tenfold component-alignment witness: map these ten doublets to kernel
coordinates and test whether they form a canonical ten-axis basis.

The rank-10 / tenfold component-alignment theorem is certified at:

```text
data/invariants/d20/theorems/full_exposure_rank10_tenfold_alignment/report.json
```

It maps each graph doublet into the certified `8+2` kernel coordinate split.
The result is deliberately not a ten-axis basis theorem. The ten doublets match
the rank-10 kernel dimension only by count. Coordinate-wise they have common
radical core `83 = 01010011`, fixed radical axes `[0,1,4,6]`, moving radical
axes `[2,3,5,7]`, and free active axes `[8,9]`. Their moving full-mode affine
direction rank is `6`, while their full linear span rank is `7`. The radical
support is the nonlinear gate

```text
x2 or (x3 and x5)
```

on the four moving radical axes, so the full-exposure graph is a ten-component
tenfold-facing screen, not the full rank-10 coordinate cube. The active
Cl(1,1) block remains aligned with the `AI` canonical module and optional `BDI`
active-Hamiltonian readout.

The full-exposure radical-gate stabilizer theorem is certified at:

```text
data/invariants/d20/theorems/full_exposure_radical_gate_stabilizer/report.json
```

It classifies the local `F_2^4` gate `x2 or (x3 and x5)` with coordinate order
`[x2,x3,x5,x7]`. The ten support points have affine stabilizer order `384` and
linear stabilizer order `64`. The six excluded points are the complement prism
`{0,x3,x5} x F_2_x7` in the hyperplane `x2=0`; the full affine stabilizer
factors as `384 = 8` transverse shears times `48` complement-prism affine
stabilizers. The support splits into stabilizer orbits of sizes `8` and `2`,
the complement is one orbit of size `6`, and the only pure translation symmetry
is the `x7` flip.

The radical-gate stabilizer lift theorem is certified at:

```text
data/invariants/d20/theorems/full_exposure_radical_gate_stabilizer_lift/report.json
```

It lifts the `384` radical-gate affine stabilizers to the full `20`-packet
propagation graph. All `384` preserve the unlabelled weighted graph and its
uniform action labels. Including the independent active-partner flip on each of
the ten doublets gives graph/action lift order `384*2^10 = 393216`. The packet
labels then break this symmetry: the constant tenfold/hidden/central/exposure
labels preserve all `393216` graph/action lifts, the combined gamma marker
leaves `6` canonical affine lifts and `3072` active-flip lifts, and the full
charge-frame plus fine spectral labels leave only the identity lift. Thus the
large finite graph symmetry is real, but the labelled physics screen is already
rigid at this level.

The label-breaking factorization theorem is certified at:

```text
data/invariants/d20/theorems/full_exposure_label_breaking_factorization/report.json
```

It factors that rigidity into named invariant axes. Among the `384` canonical
affine lifts, mass alone leaves `2`, clock leaves `48`, gamma leaves `24`,
spectral trace leaves `2`, and the full sector-26 clock family leaves only
identity. At atomic resolution, `sector26_clock_sum_mod26` and
`fine_spectral_charge_key` each independently kill all `383` nonidentity lifts,
while `sector26_clock_delta_mod26` kills none. The inclusion-minimal coarse
identity-generating sets are `{sector26}`, `{mass, clock}`, and
`{clock, spectral}`.

The canonical labelled full-exposure frame theorem is certified at:

```text
data/invariants/d20/theorems/full_exposure_canonical_labelled_frame/report.json
```

It turns those minimal breakers into an injective intrinsic coordinate frame on
the `20` full-exposure packets. The frame key has `20` occupied values, the
fine spectral key is injective on the stratum, and packet `239` is recovered
without using its external id: it is the unique full-exposure sector-26
zero-pair fixed point with clock pair `[0,0]`, sector-26 sum `0`, and
sector-26 delta `0`.

The packet-239 arithmetic resonance screen is certified at:

```text
data/invariants/d20/theorems/packet239_arithmetic_resonance/report.json
```

It treats the integer facts as a post-selection screen: packet `239` is first
recovered from D20 labels, then arithmetic predicates are evaluated on the
selected integer. The certificate verifies the prime/twin-prime/Chen/Sophie
Germain/Eisenstein/NSW cluster, `239*4649 = 1111111`, decimal period `7`,
happiness, class number `15` for `Q(sqrt(-239))` by reduced-form enumeration,
the base-`2` through base-`12` max-digit property, the local HAKMEM square/cube/
fourth-power counts, the Pell/Machin identities, and the `(13,239)` local
Diophantine witness. It also records limits: under the literal max-digit
predicate `2591` qualifies before `5927`, and the global factorial-product and
Ljunggren uniqueness claims are not locally reproved.

The full-exposure label-coordinate transition operator is certified at:

```text
data/invariants/d20/theorems/full_exposure_label_coordinate_transition_operator/report.json
```

It rewrites the `40` weighted directed edges of the two-step full-exposure
operator in intrinsic frame coordinates, retaining packet ids only as witness
fields. The operator remains ten uniform `[[2,4],[4,2]]` doublet blocks. The
zero-pair coordinate has a self-loop of weight `2` and an active-partner
transition of weight `4` to the label coordinate of packet `238`. The next
target is to diagonalize this label-coordinate operator and test whether the
zero-pair coordinate defines a distinguished eigenfunctional or boundary
condition rather than only a labelled state.

The full-exposure label-coordinate spectral boundary theorem is certified at:

```text
data/invariants/d20/theorems/full_exposure_label_coordinate_spectral_boundary/report.json
```

It diagonalizes the intrinsic label-coordinate operator: adjacency spectrum
`6^10 + (-2)^10`, normalized Markov spectrum `1^10 + (-1/3)^10`, and Laplacian
spectrum `0^10 + 8^10`. The zero-pair coordinate decomposes as `1/2` plus mode
and `-1/2` minus mode in its doublet, so it is not an eigenvector or
eigenfunctional. Its singleton and component Dirichlet spectra match every
other coordinate/doublet, so the result is negative in the useful way:
packet `239` remains label-distinguished, not operator-distinguished. The next
target is the exact Green/resolvent response from a zero-pair labelled source.

The full-exposure label-coordinate Green-response theorem is certified at:

```text
data/invariants/d20/theorems/full_exposure_label_coordinate_green_response/report.json
```

It inserts the zero-pair label as a source and computes exact response kernels.
For adjacency, `R_A(lambda)e_239` has self response
`(lambda-2)/((lambda-6)(lambda+2))` and active-partner response
`4/((lambda-6)(lambda+2))`, supported only on packets `239` and `238`. The
normalized Markov poles are `1` and `-1/3`; the massive Laplacian Green kernel
splits into a zero-mode divergence plus finite dipole limit `(1/16)*[1,-1]`.
The response profile is shared by every coordinate, so packet `239` remains
label-specific rather than operator-unique. The next target is to push those
pole residues through the packet charge-frame and sector-26 ledger.

The full-exposure zero-pair propagator charge-kernel theorem is certified at:

```text
data/invariants/d20/theorems/full_exposure_zero_pair_propagator_charge_kernel/report.json
```

It pushes the zero-pair Green pole residues through the packet charge-frame and
sector-26 ledger. The raw pole residues contain `1/2`, so they are rational
objects rather than native `Z/26` classes. After canonical denominator clearing,
the plus residue class `[1,1]` has sector-26 image `(pair=[24,6], sum=4,
delta=8)`, while the minus residue class `[1,-1]` has complementary image
`(pair=[2,20], sum=22, delta=18)`. The support is exactly packets `239` and
`238`, preserving full exposure, gamma silence, hidden cancellation, central
negativity, and `AI|BDI` type. The next target is symmetry and Ward/flux
compatibility of this denominator-cleared propagator kernel.

The full-exposure zero-pair propagator symmetry/Ward theorem is certified at:

```text
data/invariants/d20/theorems/full_exposure_zero_pair_propagator_symmetry_ward/report.json
```

It tests the denominator-cleared propagator kernel against the surviving
label-preserving symmetry and the finite Ward/flux ledger. The result is
qualified but sharp: the kernel is invariant because the surviving full-label
symmetry is already identity. Its individual plus/minus sector-26 sums `4` and
`22` are not native all-mask Ward characters, whose image is `{0,13}`. As a
paired packet-source residue, however, plus+minus is sector-26 neutral
`(pair=[0,0], sum=0, delta=0)` and does not disturb the rank-zero public flux
balance. The next target is a source-to-closed-return coupling map, or a proof
that no such map exists.

The full-exposure zero-pair source-to-closed-return coupling theorem is
certified at:

```text
data/invariants/d20/theorems/full_exposure_zero_pair_source_to_closed_return_coupling/report.json
```

It proves the no-go side of that target. The individual denominator-cleared
plus/minus source residues have sector-26 sums `4` and `22`, so neither can
preserve the all-mask Ward character image `{0,13}`. The paired plus+minus
source is neutral `(pair=[0,0], sum=0, delta=0)` and couples canonically only
to the Ward-kernel zero mask. Since the Ward kernel has dimension `10` and
`1024` neutral masks, no nonzero closed-return representative is selected by
the currently certified invariants. The next target is a canonical selector on
that kernel, using action height, `gamma_8` incidence, or compact amplitude
quotient exposure.

The full-exposure zero-pair Ward-kernel height selector theorem is certified
at:

```text
data/invariants/d20/theorems/full_exposure_zero_pair_ward_kernel_height_selector/report.json
```

It supplies that selector. Among the `1023` nonzero all-mask Ward-kernel masks,
the unique minimum positive height is mask `288`, i.e. basis cycles `[5,8]` or
cycle `5` plus `gamma_8`. Its action is `691200 + 374784 = 1065984`, its
corrected Ward clock is `13 + 13 = 0 mod 26`, and its compact exposure has
`9` active step atoms with shared atom `11` between the two generators. Thus
the paired neutral zero-pair source now has a certified nontrivial
closed-return target; the individual plus/minus residues remain no-go. The
next target is to propagate mask `288` through the finite BMS/Carrollian charge
ledger and scattering automaton to certify the first nontrivial sourced Ward
balance.

The full-exposure zero-pair selected sourced Ward balance theorem is certified
at:

```text
data/invariants/d20/theorems/full_exposure_zero_pair_selected_sourced_ward_balance/report.json
```

It performs that propagation. The selected target is still mask `288`, and the
canonical scattering table realizes it as `gamma_8` plus generator `5`:
`256 -> 288`, with height delta `691200` and hidden transfer `13 mod 26`.
The finite BMS/Carrollian row closes publicly with
`Delta Q_public = Flux_public = Res_public = 0`, and closes the hidden Ward
channel as `bare_pi33 + R33 + A_h = 0 - 1065984 + 1065984 = 0`. This is the
first certified nontrivial sourced Ward balance selected by the zero-pair
height rule. The next target is to classify all Ward-kernel sourced balance
targets reachable from `gamma_8` by height order and decide whether mask `288`
generates a minimal sourced-balance cone.

The full-exposure zero-pair sourced-balance cone theorem is certified at:

```text
data/invariants/d20/theorems/full_exposure_zero_pair_sourced_balance_cone/report.json
```

It classifies the one-step `gamma_8` target cone. The scattering star has
`10` Ward-kernel targets including the trivial zero return, `9` nonzero
Ward-kernel targets, and one odd target from generator `3`. All `9` nonzero
kernel targets close the public and hidden balance rows. Mask `288` is the
unique height-minimal apex, with a height gap `82944` to the next target. The
stronger algebraic-generation claim is false at this depth: the `F_2` span of
the apex is only `{0,288}`, and the only one-step kernel-preserving exit from
`288` is generator `3` to mask `296`. Thus `288` is a height-cone apex, not a
single generator for the whole one-step target set. The next target is to
extend this from the one-step star to shortest height paths through all `1023`
nonzero Ward-kernel masks.

The full-exposure zero-pair sourced-balance shortest-path theorem is certified
at:

```text
data/invariants/d20/theorems/full_exposure_zero_pair_sourced_balance_shortest_paths/report.json
```

It extends the cone to every nonzero Ward-kernel target. For each of the
`1023` targets, the shortest sourced path from `gamma_8` toggles exactly the
bits of `gamma_8 XOR target`; a canonical witness orders those toggles by
generator action and records the scattering transition ids. Every target closes
the finite public and hidden balance rows, and every path transfers the odd
`gamma_8` source into the Ward kernel. The shortest-step histogram is
`{1:9, 2:10, 3:120, 4:120, 5:252, 6:252, 7:120, 8:120, 9:10, 10:10}`.
Mask `288` remains the unique minimum-action target with path action `691200`
and gap `82944` to the next shortest path. The next target is to compress these
`1023` paths by height, step count, generator support, and D20 symmetry into
canonical transport families.

The full-exposure zero-pair sourced-balance transport-family theorem is
certified at:

```text
data/invariants/d20/theorems/full_exposure_zero_pair_sourced_balance_transport_families/report.json
```

It compresses the certified `1023` shortest-path atlas without weakening the
ledger labels. Step count gives `10` families, the coarse
`gamma_8`-removal/generator-3 split gives `19` families, path action and target
height each collapse to `805` scalar values, Fourier labels give `690`
families, and full transport signatures give `991` families. Exact generator
support remains singleton-level, so support labels identify every target.
Symmetry now has three certified levels: the public graph has `120`
automorphisms, the corrected hidden split leaves a C2 whose topological action
compresses the nonzero Ward-kernel targets to `543` orbits, and the full
augmented action/charge/counterterm ledger has stabilizer order `1`. Thus the
nontrivial C2 quotient is not action-height coherent: only `71` of its orbits
preserve action/height, while `472` break those labels. The next target is to
build the label-relaxed public/hidden-split orbit quotient and prove exactly
which labels must be forgotten to recover a nontrivial D20 transport symmetry.

The full-exposure zero-pair sourced-balance label-relaxed orbit-quotient theorem
is certified at:

```text
data/invariants/d20/theorems/full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient/report.json
```

It proves the exact quotient ladder. With the full augmented
action/charge/counterterm ledger retained, the stabilizer is still identity.
The smallest nontrivial gamma8-sourced transport quotient is the corrected
hidden-split C2 on the `1023` nonzero Ward-kernel targets, giving `543` orbits
with size histogram `{1:63, 2:480}`. That quotient keeps the hidden packet/R33
labels and gamma8 incidence labels, but it must forget target identity, exact
generator support, step count, path action, target height, Fourier refinements,
sector-26 clock refinements, and the six augmented-ledger breaker axes. Keeping
the gamma8 source anchor while relaxing the Ward-kernel target domain gives the
source-fixed public closure: `1983` masks in `255` orbits under a group of order
`10`. The full public `120`-action is recovered only on all `2047` nonzero
closed-return residue masks, in `45` orbits, after dropping the gamma8 source
anchor too. The next target is to promote the C2 action/height label-breaking
table to a quotient anomaly or cocycle and test whether sourced Ward/BMS balance
descends after adding that cocycle.

The full-exposure zero-pair sourced-balance C2 quotient-anomaly theorem is
certified at:

```text
data/invariants/d20/theorems/full_exposure_zero_pair_sourced_balance_c2_quotient_anomaly/report.json
```

It promotes the C2 action/height label-breaking table to exact cocycle data.
The nonidentity C2 action has `543` quotient orbits on the `1023` nonzero
Ward-kernel targets; `71` orbits have zero anomaly and `472` have nonzero
anomaly. The path-action cocycle and target-height cocycle are identical,
satisfy the C2 cocycle law, and have absolute gcd `3072`. Their mod-26 shadow
lands exactly in the even residues, so the half-shadow hits every mod-13 class.
After choosing the least target mask in each orbit as representative, the same
representative height counterterm subtracts from action/height and adds to
`R33`; public balance already descends, and the hidden sourced Ward/BMS row
descends with zero error on every target. The next target is to build the
`543`-orbit quotient transport ledger and test whether its transition operator
is Markov/spectral and Ward-balanced.

The full-exposure zero-pair sourced-balance C2 quotient transport-ledger theorem
is certified at:

```text
data/invariants/d20/theorems/full_exposure_zero_pair_sourced_balance_c2_quotient_transport_ledger/report.json
```

It identifies the primal operator: `tau`, the nonidentity hidden-split C2
involution with basis images `[16,2,512,1034,1,64,32,128,256,4,1024]`. The
quotient anomaly is not `gamma_8`; rather, `tau` fixes `gamma_8` as the source
anchor while `gamma_8` is outside the `1023` nonzero Ward-kernel target domain.
On that target domain, `tau` is a Markov permutation with spectrum
`+1^543, -1^480`, trace `63`, and determinant `1`. The orbit projection
`(I+tau)/2` is Markov and idempotent with rank `543` and nullity `480`, and the
induced quotient ledger has `543` Ward/BMS-balanced orbit rows. The next target
is to build a nontrivial quotient scattering operator between those orbits using
C2-invariant primitive/composite transport moves.

The full-exposure zero-pair sourced-balance C2 quotient scattering-operator
theorem is certified at:

```text
data/invariants/d20/theorems/full_exposure_zero_pair_sourced_balance_c2_quotient_scattering_operator/report.json
```

It builds the first nontrivial Markov dynamics on the `543` C2 quotient orbits.
The minimal C2-closed hidden-neutral move orbit is `{8,1034}`: primitive
generator `3` and its C2 image, the composite `[1,3,10]`. Closing the two exits
to the zero mask as boundary self-loops gives a row-stochastic quotient
operator. Its graph has `144` connected components with size histogram
`{2:1, 3:31, 4:112}` and exact spectrum
`1^144, 0^255, (-1)^143, (-1/2)^1`. The degree-weighted stationary distribution
has denominator `2046`; its weighted public error is zero and its weighted
hidden balance cancels height against `R33`. The next target is to classify all
C2-closed hidden-neutral composite move orbits and decide whether this minimal
operator is canonical or only the first member of a larger Ward-balanced
dynamics family.

The full-exposure zero-pair sourced-balance C2 move-orbit family theorem is
certified at:

```text
data/invariants/d20/theorems/full_exposure_zero_pair_sourced_balance_c2_move_orbit_family/report.json
```

It classifies all `543` C2-closed hidden-neutral composite move orbits. There
are `63` fixed singleton move orbits and `480` paired move orbits, every
zero-exit closure gives a symmetric Markov quotient operator, and every
degree-weighted stationary state has zero public and hidden Ward/BMS error.
The operator family has exactly three component/spectrum types: the `480`
paired operators have component histogram `{2:1, 3:31, 4:112}` and spectrum
`1^144, 0^255, (-1)^143, (-1/2)^1`; `48` fixed singleton operators have
component histogram `{1:1, 2:271}` and spectrum `1^272, (-1)^271`; and `15`
fixed singleton operators have component histogram `{1:33, 2:255}` and
spectrum `1^288, (-1)^255`. The previously certified `{8,1034}` operator is
therefore unique only as the primitive-seeded hidden-neutral move orbit. It is
not action-minimal: the global action minimum is `[384]` with total action
`1443840`, while the paired action minimum is `[288,320]` with total action
`2343936`. The next target is a selector theorem comparing primitive-seeded,
action-minimal, paired-action-minimal, and spectral-gap criteria.

The full-exposure zero-pair sourced-balance C2 dynamics-selector theorem is
certified at:

```text
data/invariants/d20/theorems/full_exposure_zero_pair_sourced_balance_c2_dynamics_selector/report.json
```

It proves that the quotient dynamics is not uniquely selected without an extra
physical axiom. Primitive seeding selects the earlier `{8,1034}` operator.
Global action minimization selects the fixed singleton `[384]` with total
action `1443840`. Paired-action minimization selects `[288,320]` with total
action `2343936`. Raw componentwise absolute spectral gap is degenerate across
all `543` family members, so it selects nothing useful. After lazy
normalization `(I+P)/2`, componentwise spectral gap selects the `63` fixed
singleton operators; with an action tiebreak it again selects `[384]`. If
paired C2 transport is required, lazy spectral gap is flat over all `480`
paired operators and its action tiebreak selects `[288,320]`. The next target
at this point in the chain was to promote the selector layer into a finite
foundation and Agda replay package; that package is now the Halloween-bound
source-registry chain below.

The full-exposure zero-pair sourced-balance C2 Cubical foundation bridge is
certified at:

```text
data/invariants/d20/theorems/full_exposure_zero_pair_sourced_balance_c2_univalent_foundation_bridge/report.json
```

It packages the selector layer as a complete finite skeletal candidate for a
Cubical foundation presentation. The quotient state type is a set-truncated
C2 quotient HIT with `1023` raw nonzero Ward-kernel masks, `543` quotient
states, `480` nontrivial C2 path pairs, and `63` fixed paths. The dynamics
type is a finite universe of `543` certified Ward-balanced C2 move operators,
again split into `480` paired and `63` fixed codes. Selector criteria become
dependent fibers over that dynamics universe: primitive seeding, global least
action, paired least action, and the two action-tiebroken spectral selectors
are contractible singleton fibers, while raw spectral gap, lazy spectral gap,
and paired lazy spectral gap remain noncontractible fibers of sizes `543`,
`63`, and `480`. The finite skeletal identity rule is hash-extensional:
within this candidate universe, identity is represented by equality of the
canonical certified structure code. This is intentionally not yet a
Lean/Coq/Agda/HoTT proof of foundations; the downstream Cubical Agda skeleton
and generated enumeration stack below are the current formal replay.

The full-exposure zero-pair sourced-balance C2 Cubical Agda skeleton is
certified at:

```text
data/invariants/d20/theorems/full_exposure_zero_pair_sourced_balance_c2_cubical_agda_skeleton/report.json
```

The typechecked Cubical Agda target is:

```text
data/invariants/d20/formal/cubical/C2SelectorFoundation.agda
```

It uses `{-# OPTIONS --cubical --safe --guardedness #-}` and imports the local
Cubical library. The module defines `C2TargetQuotient` as a set-truncated HIT
skeleton with `tauPath`, defines `DynamicsCode`,
`WardBalancedDynamicsStructure`, `SelectedDynamics`, `SkeletalIdentityRule`,
`C2SelectorFoundationSkeleton`, and `ConstructiveUnivalenceGate`, and supplies
`isContr` witnesses for the five singleton selector fibers. The emitted module
has been checked by Agda against the local Cubical library, producing
`C2SelectorFoundation.agdai`. The generated enumeration below expands the
compact interface into all `543` quotient states, all `543` dynamics codes,
and selector fiber membership.

The full-exposure zero-pair sourced-balance C2 Cubical Agda enumeration is
certified at:

```text
data/invariants/d20/theorems/full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration/report.json
```

The generated typechecked Cubical Agda module is:

```text
data/invariants/d20/formal/cubical/C2SelectorFoundationGenerated.agda
```

It imports `C2SelectorFoundation` and expands the compact interface into
explicit finite constructors: `543` `QuotientState` constructors, `543`
`DynamicsId` constructors, `543` `dynamicsCodeOf` rows, and `1091`
`SelectorMembership` constructors. The selector fibers have the certified
cardinalities `1, 1, 1, 543, 63, 1, 480, 1` for primitive seeded, global
least-action, paired least-action, raw spectral gap, lazy spectral gap, lazy
gap plus action tiebreak, paired lazy gap, and paired lazy gap plus action
tiebreak respectively. The generated properties module below supplies Cubical
Agda decidable equality and exhaustive eliminator/counting lemmas for the
generated quotient-state and dynamics enumerations.

The full-exposure zero-pair sourced-balance C2 Cubical Agda enumeration
properties theorem is certified at:

```text
data/invariants/d20/theorems/full_exposure_zero_pair_sourced_balance_c2_cubical_agda_enumeration_properties/report.json
```

The generated typechecked Cubical Agda properties module is:

```text
data/invariants/d20/formal/cubical/C2SelectorFoundationGeneratedProperties.agda
```

It proves the generated counts by reflexivity, adds exhaustive record-of-cases
eliminators for the `543` quotient states and `543` dynamics ids, defines
`quotientStateDiscrete` and `dynamicsIdDiscrete` by reducing equality to
decidable equality of certified numeric ids, and derives `isSet` witnesses for
both generated finite types. The selector-membership module below supplies
generated decidable selector-membership functions and fiber count proofs for
all eight selector criteria in Cubical Agda.

The full-exposure zero-pair sourced-balance C2 Cubical Agda
selector-membership theorem is certified at:

```text
data/invariants/d20/theorems/full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_membership/report.json
```

The generated typechecked Cubical Agda selector module is:

```text
data/invariants/d20/formal/cubical/C2SelectorFoundationSelectorMembership.agda
```

It defines `selectorMembership?` as a total decision function over all eight
selector criteria and all `543` certified dynamics ids. The module contains
`4344` explicit selector/dynamics decision clauses: `1091` yes branches backed
by generated `SelectorMembership` constructors and `3253` no branches backed
by impossible-pattern proofs. It also proves all eight selector fiber counts
by reflexivity. The split finite-subtype modules below package selector fibers
as Cubical Agda finite subtypes and prove equivalence to `Fin n` for their
certified cardinalities.

The all-fiber Cubical Agda finite-subtype attempt is recorded, but not
certified, at:

```text
data/invariants/d20/theorems/full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype/report.json
```

It emits the expected source-level shape
`SelectorFiber s = Sigma DynamicsId (SelectorMembership s)` and candidate
equivalences to `Fin n` for all eight selector fibers, but Agda did not produce
the interface artifact for the monolithic module within the bounded witness
run. The certified split result is the singleton finite-subtype theorem:

```text
data/invariants/d20/theorems/full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_singletons/report.json
```

Its typechecked Cubical Agda module is:

```text
data/invariants/d20/formal/cubical/C2SelectorFoundationSelectorFiniteSubtypeSingletons.agda
```

The module defines the dependent subtype
`SelectorFiber s = Sigma DynamicsId (SelectorMembership s)`, a five-point
`SingletonSelector` index, and typechecked equivalences from the five
contractible selector fibers to `Fin 1`: primitive seeded, global least action,
paired least action, lazy spectral gap plus action tiebreak, and paired lazy
gap plus action tiebreak. To make Agda coverage deterministic, it spells out
the impossible rows over all `543` dynamics ids for each singleton fiber. The
next split result is the lazy spectral-gap finite-subtype theorem:

```text
data/invariants/d20/theorems/full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lazy63/report.json
```

Its typechecked Cubical Agda module is:

```text
data/invariants/d20/formal/cubical/C2SelectorFoundationSelectorFiniteSubtypeLazy63.agda
```

It packages the `lazyComponentwiseSpectralGap` selector fiber as the dependent
subtype `SelectorFiber lazyComponentwiseSpectralGap` and proves a typechecked
equivalence to `Fin 63`. The proof uses the `63` generated `lazyGapMember`
constructors as witnesses and discharges the other `480` dynamics ids by
explicit impossible rows. The next split result is the paired lazy spectral-gap
finite-subtype theorem:

```text
data/invariants/d20/theorems/full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_paired_lazy480/report.json
```

Its typechecked Cubical Agda module is:

```text
data/invariants/d20/formal/cubical/C2SelectorFoundationSelectorFiniteSubtypePairedLazy480.agda
```

It packages the `pairedLazyComponentwiseSpectralGap` selector fiber as the
dependent subtype `SelectorFiber pairedLazyComponentwiseSpectralGap` and proves
a typechecked equivalence to `Fin 480`. The proof uses the `480` generated
`pairedLazyGapMember` witnesses and discharges the remaining `63` dynamics ids
by explicit impossible rows. The final non-singleton split result is the raw
spectral-gap finite-subtype theorem:

```text
data/invariants/d20/theorems/full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543/report.json
```

Its typechecked Cubical Agda module is:

```text
data/invariants/d20/formal/cubical/C2SelectorFoundationSelectorFiniteSubtypeRaw543.agda
```

It packages the `rawComponentwiseAbsoluteSpectralGap` selector fiber as the
dependent subtype `SelectorFiber rawComponentwiseAbsoluteSpectralGap` and
proves a typechecked equivalence to `Fin 543`. The proof uses all `543`
generated `rawGapMember` witnesses and has no impossible rows because the raw
spectral-gap selector fiber is the whole dynamics code set. The shared emitter
below factors the singleton, lazy63, paired-lazy480, and raw543 finite-subtype
generators into one reusable source path.

That generator factorization is certified at:

```text
data/invariants/d20/theorems/full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_emitter_factorization/report.json
```

The shared emitter lives at:

```text
src/c2_selector_finite_subtype_emitter.py
```

It reproduces the singleton, lazy63, paired-lazy480, and raw543 Agda sources
byte-for-byte, so the existing typechecked interface artifacts remain valid.
The indexed proof layers below replace the large generated `FinData`
constructor normal forms with compact indexed-vector witnesses to reduce Agda
source size and typecheck time.

The raw543 indexed finite-subtype proof layer is certified at:

```text
data/invariants/d20/theorems/full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_raw543_indexed/report.json
```

Its typechecked Cubical Agda module is:

```text
data/invariants/d20/formal/cubical/C2SelectorFoundationSelectorFiniteSubtypeRaw543Indexed.agda
```

It keeps the same claim that
`SelectorFiber rawComponentwiseAbsoluteSpectralGap` is equivalent to `Fin 543`,
but replaces the large generated
`FD.suc` constructor normal forms with natural-number indexed witnesses,
Cubical `inspect` refinement, and `FinData` injectivity. The indexed source is
`1,965,329` bytes versus `4,109,032` for the direct raw source, contains zero
`FD.suc` occurrences, and produces a fresh Agda interface artifact.

The indexed lazy63/paired-lazy480 finite-subtype split is certified at:

```text
data/invariants/d20/theorems/full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_split/report.json
```

Its typechecked Cubical Agda modules are:

```text
data/invariants/d20/formal/cubical/C2SelectorFoundationSelectorFiniteSubtypeLazy63Indexed.agda
data/invariants/d20/formal/cubical/C2SelectorFoundationSelectorFiniteSubtypePairedLazy480Indexed.agda
```

They certify the lazy spectral-gap fiber as `Fin 63` and the paired-lazy
spectral-gap fiber as `Fin 480` using the same indexed witness mode. The
indexed lazy63 source is `98,865` bytes versus `114,353` for the direct source;
the indexed paired-lazy480 source is `1,580,382` bytes versus `1,875,448` for
the direct source. Both contain zero `FD.suc` occurrences and produce fresh
Agda interface artifacts. The active proof-obligation spine now points at the
indexed finite-subtype trio. The lookup layer below is the second-stage vector
lookup layer, so the Agda source no longer scales linearly with every selected
witness row.

The lookup-collapsed indexed finite-subtype trio is certified at:

```text
data/invariants/d20/theorems/full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_indexed_lookup/report.json
```

Its typechecked Cubical Agda modules are:

```text
data/invariants/d20/formal/cubical/C2SelectorFoundationSelectorFiniteSubtypeRaw543IndexedLookup.agda
data/invariants/d20/formal/cubical/C2SelectorFoundationSelectorFiniteSubtypeLazy63IndexedLookup.agda
data/invariants/d20/formal/cubical/C2SelectorFoundationSelectorFiniteSubtypePairedLazy480IndexedLookup.agda
```

They keep the `Fin 543`, `Fin 63`, and `Fin 480` equivalences but collapse the
right inverse through a Nat-index helper and `FinData.fromToId'`, removing the
generated `inspect`/numeric-injection inverse rows. The lookup sources remain free of
`FD.suc` constructor-normal-form towers and are smaller than the previous
indexed modules: raw543 is `1,933,563` bytes, lazy63 is `95,040` bytes, and
paired-lazy480 is `1,559,045` bytes. The active proof-obligation spine now
points at this lookup-collapsed trio. The selector lookup witness table below
externalizes the selected witness rows into a verified table/vector artifact
and proves the corresponding table-soundness lemma.

The selector lookup witness table theorem is certified at:

```text
data/invariants/d20/theorems/full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table/report.json
```

It externalizes the three non-singleton spectral selector witnesses into:

```text
data/invariants/d20/theorems/full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table/selector_lookup_witness_table.json
data/invariants/d20/theorems/full_exposure_zero_pair_sourced_balance_c2_cubical_agda_selector_finite_subtype_lookup_table/selector_lookup_witness_table.csv
```

The table has `1086` rows: `543` raw spectral-gap witnesses, `63` lazy
spectral-gap witnesses, and `480` paired-lazy spectral-gap witnesses. Each row
records the selector, `DynamicsId`, membership constructor, index-bound
witness, and exact lookup Agda clauses; the certificate checks those clauses
against the generated lookup sources. The soundness module is:

```text
data/invariants/d20/formal/cubical/C2SelectorFoundationSelectorFiniteSubtypeLookupTableSoundness.agda
```

It typechecks and ties the table counts back to the certified `Fin 543`,
`Fin 63`, and `Fin 480` lookup equivalences. The active proof-obligation spine
now points at this table certificate. The table certificate is bound through
the Halloween source registry and theorem registry; the remaining operational
item is staging those registry and Agda replay artifacts for review.

The D20 Matrix Lift Conjecture / finite Matrix-theoretic charge-wall shadow is
registered at:

```text
data/invariants/d20/theorems/d20_matrix_lift_conjecture/report.json
```

It records the safe theorem-grade reading: D20 has a finite matrix/algebraic
bulk `A985`, a public `Lambda^3 H6` boundary, a zero-pair propagator residue
that is half-integral upstairs, a denominator-cleared `Z/26` charge ledger
downstairs, a complementary plus/minus residue doublet, and primitive
public-zero wall sector `33`. This is not a claim that D20 is already
M-theory. The certificate registers the conjecture that there may be a finite
matrix-theoretic lift `M_D20` whose public charge reduction is the
denominator-cleared sector-26 propagator kernel and whose primitive wall defect
is sector `33`. The missing bridges remain explicit: `A985` to a DLCQ matrix
model, D20 to an M2/M5 charge sector, and the sector-26 kernel to a quantized
C-field or brane charge law. The Matrix Theory wall paper
[`arXiv:2603.02199`](https://arxiv.org/abs/2603.02199) is recorded only as
motivation, not as certificate input.

The D20 minimal matrix charge-lift is certified at:

```text
data/invariants/d20/theorems/d20_minimal_matrix_charge_lift/report.json
```

It constructs the first local bridge. On the packet basis `[239,238]`, the
algebra `Mat_2(Q)` generated by the swap involution `S` has rank-one projectors
`(I+S)/2` and `(I-S)/2`. Acting on the zero-pair source vector `[1,0]`, these
produce the raw half-integral residue directions `[1/2,1/2]` and
`[1/2,-1/2]`. Clearing denominators gives `[1,1]` and `[1,-1]`, which recover
the certified sector-26 images `(pair=[24,6], sum=4, delta=8)` and
`(pair=[2,20], sum=22, delta=18)`. Sector `33` is preserved as the primitive
wall pointer. This proves a local charge-kernel matrix lift only; it does not
construct a full `A985` to DLCQ matrix model. The next target is to extend this
`Mat_2(Q)` lift from the packet pair to the full `20`-packet full-exposure
propagation algebra and then test whether any part of `A985` acts through it.

The D20 full-packet matrix lift is certified at:

```text
data/invariants/d20/theorems/d20_full_packet_matrix_lift/report.json
```

It extends the local `[239,238]` lift to all `20` full-exposure packets. The
ten active-partner doublets form a block algebra `Mat_2(Q)^10`, and the
certified two-step full-exposure transition operator is the direct sum of ten
copies of `2I+4S`. Each block has the same plus/minus projectors as the local
charge lift, and the zero-pair component is exactly the minimal lift oriented
as `[239,238]`. The tested action therefore lands in the block matrix lift.
The `A985` boundary remains negative: this block image has dimension `40`, so a
faithful action of the `985`-dimensional algebra cannot fit there; any such map
would have kernel dimension at least `945`, and no certified `A985` to
full-packet operator homomorphism is present yet. The next target is to search
for an actual quotient-level `A985`/tube/quotient element that preserves the
`20`-packet subspace and lands in `Mat_2(Q)^10`.

The D20 packet quotient-action probe is certified at:

```text
data/invariants/d20/theorems/d20_packet_quotient_action_probe/report.json
```

It finds the certified packet-level action already present at the scattering
boundary. The source-loop piece `[5,10]+[10,5]` acts as `2I` on every
active-partner doublet, the remaining ordered crossing pairs act as `4S`, and
their sum is the full `2I+4S` packet operator in `Mat_2(Q)^10`. This is a real
full-exposure packet action, but it is still a primitive-generator scattering
action. The probe does not yet certify an `A985`, tube, or terminal-quotient
element acting on the `20` packets. The next target is to construct an explicit
restriction map from `A985`, the screen-0 tube central element, or the
`q42`/`q12` quotient tensors to the `20` full-exposure packets and test whether
the resulting action equals `2I`, `4S`, or `2I+4S`.

The D20 explicit packet restriction-map test is certified at:

```text
data/invariants/d20/theorems/d20_explicit_packet_restriction_map_test/report.json
```

It constructs the restriction that actually exists now. The reduced scattering
automaton has a `40`-mode projection onto the `20` full-exposure packets. One
crossing step leaves the kernel packet space, but every ordered two-step
crossing pair from `{5,9,10}` returns to the full-exposure packet space and
recovers the same `2I+4S` block in `Mat_2(Q)^10`. The raw `A985` relation
basis, the screen-0 tube central element, and the `q42`/`q12` quotient tensors
still have no certified projection to packet modes. The next target is to add
relation/object/quotient-class labels to kernel mode masks, or prove that no
label-compatible projection can intertwine the scattering `2I+4S` action.

The D20 packet-bridge SNF obstruction is certified at:

```text
data/invariants/d20/theorems/d20_packet_bridge_snf_obstruction/report.json
```

It computes the exact Smith normal form of the certified `20`-packet operator.
The operator is the direct sum of ten copies of:

```text
[[2,4],
 [4,2]]
```

Each local block has Smith diagonal `[2,6]`, so the full packet operator has
Smith factors `2^10, 6^10` and cokernel `Z/2^10 x Z/6^10`. Equivalently, for
any future raw packet target `(u,v)` on a doublet to be an integral image of the
packet operator, it must satisfy:

```text
u-v = 0 mod 2
u+v = 0 mod 6
```

This is the exact integer obstruction template for the missing `A985`, tube,
and `q42`/`q12` packet bridges. It does not construct those bridges; it says
what every proposed bridge column must pass before it can be an integral
packet image. The only torsion primes visible in this packet obstruction are
`2` and `3`.

The D20 finite contour-integration test is certified at:

```text
data/invariants/d20/theorems/d20_finite_contour_integration/report.json
```

It reconstructs the certified H-cycle graph from `d20.json` and treats the
edge weights as a finite 1-form. The public board has `20` vertices and `30`
edges, so the cycle rank is `30 - 20 + 1 = 11`. The stored primitive H-cycles
form a full `F2` basis of that cycle space, and all their mod-2 boundaries
vanish.

The positive contour integral exactly reproduces the stored optical action on
every primitive H-cycle:

```text
sum_C omega_pos = A_opt(C)
```

with entropy proxy `A_opt(C)/(4|W(D6)|)` and `|W(D6)| = 23040`. The signed
contour integral is not exact. The equation `D phi = w` has ranks:

```text
rank(D)   = 19
rank(D|w) = 20
```

so no rational vertex potential exists. The signed residues have gcd `3072`;
after division by `3072`, the primitive residue vector is:

```text
(-106,-94,12,20,-40,-159,-174,-180,-40,-67,-81)
```

and its mod-26 reduction is:

```text
(24,10,12,20,12,23,8,2,12,11,23)
```

This certifies a finite Stokes/residue machine on the D20 boundary: closed
contours detect the non-exact part of the edge 1-form and produce a primitive
sector-26 residue line. It does not certify `P != NP`, M-theory, or a theorem
about rational prime distribution.

The contour/sector/packet prime-support alignment is certified at:

```text
data/invariants/d20/theorems/d20_contour_sector_packet_prime_alignment/report.json
```

It compares three already certified arithmetic layers:

```text
finite contour raw gcd      = 3072 = 2^10 * 3
packet SNF obstruction      = primes {2,3}
sector-26 charge ledger     = 26 = 2 * 13
```

The result is a stratified `2/3/13` split. Prime `2` is common to contour,
packet SNF, and sector-26 charge. Prime `3` belongs to raw optical/action
quantization and packet-SNF torsion. Prime `13` appears only after sector-26
ledger reduction. This is a certified prime-support alignment, not an
isomorphism of the three structures.

The contour-charge pairing Smith form is certified at:

```text
data/invariants/d20/theorems/d20_contour_charge_pairing_snf/report.json
```

It pairs the `11` primitive contour residues with the denominator-cleared
sector-26 plus/minus doublet. In centered coordinates, the charge doublet is

```text
sum   = (+4,-4)
delta = (+8,-8)
```

The raw integer pairings have Smith diagonals `[4]` and `[8]`, respectively.
After reducing the residue line modulo `26`, the pairing rows generate a single
order-`13` anti-diagonal line inside `(Z/26)^2`. The finite quotient has Smith
diagonal

```text
[2,26]
```

so its invariant group is `Z/2 x Z/26` and its order is `52`.

The same certificate records the independent combinatorial comparison that
there are `13` strict weak orderings on a labelled three-element set
`{a,b,c}`. Polarity-doubling gives `26`, matching the sector clock count, but
this is recorded as a comparison target only: the certificate does not prove
that strict weak orderings cause sector `26`.

The strict-weak-order sector-26 clock is certified at:

```text
data/invariants/d20/theorems/d20_strict_weak_order_sector26_clock/report.json
```

It makes the comparison explicit. The `13` ordered partitions of `{a,b,c}` are
mapped by

```text
k -> 2k mod 26
```

onto the even sector-26 residues. The anti-diagonal pairs

```text
(2k,-2k) mod 26
```

are exactly the order-`13` line certified by the contour-charge pairing. Adding
a polarity bit gives `2k` and `2k+1`, which covers all `26` sector-clock
residues.

The natural relabelling action on `{a,b,c}` has orbit sizes `1,3,3,6` on the
`13` weak orderings. It preserves the `13`-element set, but only the identity
preserves the chosen cyclic clock labels. On the D20 side, the full augmented
ledger stabilizer is already identity, so it preserves this clock trivially.
The nonidentity hidden `C2` preserves only the corrected hidden clock and breaks
the sector-26 counterterm and normalized optical clock, so the strict-weak-order
clock does not descend to that relaxed quotient.

The intrinsic-triple ordering clock is certified at:

```text
data/invariants/d20/theorems/d20_intrinsic_triple_ordering_clock/report.json
```

It removes the external placeholder set. The certified sector-26 hidden
transport form supplies the intrinsic D20 triple

```text
(R33, K_mixed_S, K_pure_Sminus)
```

with matrix

```text
[[4,0,0],
 [0,5,1],
 [0,1,2]]
```

The matrix is permutation-rigid: only the identity preserves it. Its composite
block on `(K_mixed_S,K_pure_Sminus)` has discriminant `13`, while `R33` is
transport-isolated. Ordering by transport signature gives the same triple order,
and the strict weak orderings of this intrinsic triple reproduce the same
order-`13` anti-diagonal line and the same polarity-doubled `26`-state sector
clock.

The triple 13-signature uniqueness classifier is certified at:

```text
data/invariants/d20/theorems/d20_triple_13_signature_uniqueness/report.json
```

It scans the certified D20 theorem-report corpus for explicit triples: report
objects with a length-`3` `basis_order` and a `3 x 3` matrix. Among all such
certified triples with a discriminant-`13` or order-`13` clock signature, there
is exactly one unique signature:

```text
basis  = (R33, K_mixed_S, K_pure_Sminus)
matrix = [[4,0,0],[0,5,1],[0,1,2]]
```

The signature occurs in the sector-26 invariant suite, the finite anomaly
counter, and the intrinsic-triple clock theorem. This proves uniqueness in the
current explicit theorem-report corpus.

The raw/transport `3 x 3` discriminant-`13` search is certified at:

```text
data/invariants/d20/theorems/d20_raw_transport_3x3_discriminant13_search/report.json
```

It lowers the search one step. The survey covers `d20.json`, consolidated data
certificate JSON files, and D20 theorem reports whose ids contain `transport`,
`sector26`, or `anomaly`. It checks `42,185` principal `3 x 3` subforms from
`302` square integer JSON matrices. Raw D20/layer JSON has zero
discriminant-`13` hits. The only transport-sector hits are the already known
hidden transport matrix in `sector26_invariant_suite` and
`finite_anomaly_counter`:

```text
[[4,0,0],[0,5,1],[0,1,2]]
```

There are no unreported discriminant-`13` hits and no determinant-`13`
principal `3 x 3` subforms in this bounded JSON survey. It still does not
expand every external `NPZ` payload; the next target is a shape-bounded sparse
NPZ survey.

## Current D20 sandpile critical-group result

The D20 sandpile/chip-firing critical group is certified at:

```text
data/invariants/d20/theorems/sandpile_critical_group/report.json
```

It derives the unweighted H-cycle boundary graph Laplacian from
`data/invariants/hcycle/subscript_Hcycle_d20_edges.csv`, deletes one sink row
and column, and computes the reduced Smith normal form:

```text
diag = 1^14, 2, 12, 60, 60, 60
```

Thus the critical group is `Z/2 x Z/12 x Z/60^3`, with order `5,184,000`.
All `20` reduced cofactors have determinant `5,184,000`, so the spanning-tree
count and recurrent sandpile-state count agree. The residue comparison below
now pairs the `2048` closed-return masks with explicit sandpile classes; the
remaining target is to explain the mixed classes by extracting class-preserving
tube-grade flips.

The full public-boundary graph invariant table is certified at:

```text
data/invariants/d20/theorems/public_boundary_graph_invariants/report.json
```

| invariant | value | role |
|---|---|---|
| Public graph | `20` vertices, `30` edges, 3-regular, connected, diameter `5` | finite public boundary |
| Dodecahedral check | isomorphic to the standard dodecahedral graph | spherical public board |
| Cycle rank | `30 - 20 + 1 = 11` | geon/residue space |
| Automorphisms | `|Aut(Gamma_d20)| = 120` | public board symmetry |
| Sandpile group | `Z/2 x Z/12 x (Z/60)^3` | recurrent boundary residues |
| Spanning trees | `5,184,000` | order of critical group |
| Shift entropy | `log(3)` | legal public histories |
| Nonbacktracking entropy | `log(2)` | geodesic histories |
| Fourier screen | best nontrivial signed-turn phase gate has `2` defects | Ulam-style hidden chamber candidate |

The Fourier screen here is the signed-turn screen: assign each of
`B+`, `B-`, `S+`, `S-`, `V+`, and `V-` a phase in `{+1,-1}`. A primitive
H-cycle is coherent when the product of its turn-address phases is `+1`;
otherwise it is a defect. The best nonconstant screens have exactly two
primitive-cycle defects.

The all-mask Fourier residue-screen lift is certified at:

```text
data/invariants/d20/theorems/fourier_residue_screen/report.json
```

It turns the three best two-defect signed-turn screens into explicit
characters on the `2048` closed-return masks. Each screen splits the masks
into a `1024`-mask kernel and a `1024`-mask odd coset. Together the three
defect vectors have rank `3` over `F2`, so the combined screen has `8` cells
of `256` masks each. This is still a finite residue-screen certificate, not
yet an `A985` sector-character certificate. The sandpile comparison below
supplies the mask-to-divisor map.

The A985/tube sector-character candidate evaluation is certified at:

```text
data/invariants/d20/theorems/fourier_a985_sector_character_candidates/report.json
```

The three screens act as signed-object involutions on the `109` local
primitive closed-loop pieces, but none is scalar on all `39` materialized
`A985`/tube sector idempotents. Their homogeneous/mixed sector counts are
`16/23`, `12/27`, and `16/23`. On the public-zero idempotent supports, only the
first screen is scalar on every nonzero support; it evaluates as `+1` on
`[33]`, `[6,26]`, `[25,26]`, `[6,26,33]`, and `[25,26,33]`. The next target is
recorded in the screen-0 tube central-element certificate below.

The surviving screen-0 tube central element is certified at:

```text
data/invariants/d20/theorems/fourier_screen0_tube_central_element/report.json
```

It reconstructs `signed_turn_screen_0` from all `109` local primitive
closed-loop pieces and collapses to the six-term signed object unit
`-1_B- + 1_B+ -1_V- + 1_V+ + 1_S- + 1_S+`. This element squares to the
closed-loop unit and commutes with all `297` closed-loop basis relations. It is
not central in the full `985`-relation algebra: the certificate finds `304`
full-algebra commutator failures, exactly the relations whose source and target
objects have opposite screen-0 phase. So the result is a genuine closed-loop
tube central involution, with the full-`A985` boundary explicitly recorded.

The screen-0 tube grade to sandpile divisor-map comparison is certified at:

```text
data/invariants/d20/theorems/tube_sandpile_divisor_map/report.json
```

For each mask, active public edges are oriented by
`data/invariants/hcycle/subscript_Hcycle_d20_edges.csv`; an active edge
`u -> v` contributes `e_v - e_u` to a degree-zero divisor. With sink vertex
`0` removed, the sandpile class key is
`adj(L_reduced) d_reduced mod det(L_reduced)`, where
`det(L_reduced) = 5,184,000`. Under this explicit map, the `2048` masks land
in `1360` sandpile classes. The screen-0 tube grade splits the masks
`1024/1024`, but it is not a function of the sandpile class: `154` classes are
mixed, accounting for `576` masks. The next target is to extract the kernel
moves that preserve the divisor class while flipping the tube grade.

The exact-divisor flip-move census is certified at:

```text
data/invariants/d20/theorems/tube_sandpile_kernel_flips/report.json
```

It sharpens the sandpile comparison: all `154` mixed sandpile classes are
already mixed before quotienting by the Laplacian, inside exact oriented-
divisor fibers. There are `1368` exact-divisor fibers, `2801` unordered
same-divisor mask pairs, and `1285` of those pairs flip the screen-0 tube
grade. These flips use `392` distinct XOR move masks spanning rank `11` over
`F2`; the only single-bit flip moves are the two screen-0 defect bits
`7` and `9`. A deterministic five-move cover, with move masks
`1560`, `128`, `512`, `130`, and `421`, hits every mixed exact-divisor fiber.

The finite `F2` flip-move presentation is certified at:

```text
data/invariants/d20/theorems/tube_sandpile_flip_move_presentation/report.json
```

It presents the `392` exact-divisor grade-flip moves as named generators
mapping onto the full rank-`11` residue move space. The canonical ascending
delta basis is
`[128,129,130,134,136,144,161,192,384,512,1152]`, and the theorem derives
`381` linear relations against that basis. The five cover moves
`[1560,128,512,130,421]` have rank `5`, hence no nonzero `F2` relation among
them; their span has `32` elements and intersects the `392` flip moves in `9`
moves. Quotienting by the cover span leaves a `6`-dimensional residual
classification with `64` cosets.

The flip-coset observable classifier is certified at:

```text
data/invariants/d20/theorems/tube_sandpile_flip_coset_classifier/report.json
```

It partitions all `392` flip generators and all `1285` grade-flip pairs into
the `64` cosets. The cover-span coset is coset `0`: it is the unique coset
containing the five cover moves, has `9` flip generators, accounts for `271`
grade-flip pairs, and touches all `154` mixed exact-divisor fibers/classes. The
other `63` cosets contain no cover move. Across all cosets the pair-level
sandpile class-order histogram is `{2:2, 6:7, 10:1, 15:31, 30:1244}`. The next
target is to compress the `64` observable profiles by automorphism or
sandpile-order symmetry and test whether the compressed classes are canonical.

The flip-coset profile compression theorem is certified at:

```text
data/invariants/d20/theorems/tube_sandpile_flip_profile_compression/report.json
```

It enumerates the `120` public graph automorphisms, induces each action on the
rank-`11` residue space, and checks compatibility with the `392` flip
generators and the five-cover span. Only the identity preserves the
flip-generator set, the five-cover set, the five-cover span, and therefore the
flip quotient, so public automorphism compression is trivial for this exact
quotient. Sandpile-order profiles do compress the `64` cosets: pair-order
profiles give `30` classes, fiber-order profiles give `15` classes, and the
combined order profile gives `48` classes with size histogram
`{1:36, 2:9, 3:2, 4:1}`. The cover-span coset is a singleton under this
combined profile. The next target is to refine the non-singleton combined
classes with tube-sector data.

The flip-coset screen refinement theorem is certified at:

```text
data/invariants/d20/theorems/tube_sandpile_flip_sector_refinement/report.json
```

It reconstructs the grade-flip pairs inside each quotient coset and profiles
them by the three certified signed-turn residue screens. The 48 combined-order
classes have `12` non-singleton classes containing `28` cosets. Once each
grade-flip pair is oriented from the screen-0 odd endpoint to the screen-0 even
endpoint, the screen1/screen2 transition histogram splits all `64` cosets into
singletons with size histogram `{1:64}`. This is a finite residue-screen
refinement grounded in the A985/tube sector-character candidate certificate;
it is not yet a new 39-sector idempotent classification. The next target is to
pull this split back to explicit 39-sector idempotent support data.

The flip-coset sector-support pullback theorem is certified at:

```text
data/invariants/d20/theorems/tube_sandpile_flip_sector_support_pullback/report.json
```

It performs that pullback against the explicit 39-sector idempotent support
rows. The screen1/screen2 states `00`, `01`, and `10` have nonempty local
primitive support, with `30`, `35`, and `44` local pieces respectively; state
`11` has none. The full four-state pullback is therefore obstructed: `11`
appears in `420` grade-flip transitions across `56` cosets despite having no
current sector-support realization. After discarding those unsupported
transitions, the support-admissible transition profile still separates all
`64` cosets with size histogram `{1:64}`. The next target is to classify the
unsupported `11` residue state.

The flip-coset unsupported-state classification is certified at:

```text
data/invariants/d20/theorems/tube_sandpile_flip_unsupported_state_classification/report.json
```

It shows that the gap occurs before sector aggregation. The full residue cube
has all four screen1/screen2 states equally, with `512` masks in each state
and a `256/256` split by screen-0. The six A985/tube object labels realize only
`00`, `01`, and `10`: `{B-, V-}`, `{B+, S+}`, and `{V+, S-}`. No object label
has state `11`, so no current local primitive sector piece can realize it.
State `11` is therefore residue-visible but outside the present object-phase
support model. The next target is to test a formal `11` extension against the
finite algebra constraints.

The flip-coset formal `11` extension test is certified at:

```text
data/invariants/d20/theorems/tube_sandpile_flip_formal_11_extension_test/report.json
```

It enumerates the finite ways to make `screen12=11` nonempty without changing
the certified tensor data. The empty cell preserves the six-object/109-piece
boundaries but explains no transitions. Relabelling a piece violates the
existing object phase image; adding an unlabelled piece breaks object-labelled
support and the `109`-piece total; adding one or two formal objects breaks the
six-object boundary and the `109`-piece total. Therefore no nonempty formal
`11` extension preserves the current support constraints. The next target is
either to stop the support refinement for the current model or build a genuine
extended model and re-run tensor checks.
