# D20 boundary physics discovery notes

Status: provisional boundary-physics discovery note generated from the certified black-hole atom lab report.

## Scope

- This note records C985/d20 finite boundary physics. It is not a GR black-hole solution.
- The visualization is only a witness surface. Evidence comes from the atlas, Ward/BMS operator, C985 charge labels, and null tests.
- Current falsification status: BOUNDARY_SINK_SUPPORTED_COUPLING_NOT_SUPPORTED. Candidate coupling is admitted only when a named observable beats its null distribution; this remains a boundary notebook, not a GR closure.

## Fixed invariants used

- Public shell: D=d20=Lambda^3 H6 with dim D=C(6,3)=20.
- Descent body: A985 -> A236 -> A42 -> A12.
- RGBA closure: 32 channels, with RGB=24 and alpha octet=8.
- Fine coupling: alpha*=1/137 from 128+8+1.
- Alpha wall: A_alpha=1/4, cutting the public shell as 20=6+14.
- Hydrogen scale: Lambda=54.4 eV; fine denominator=75076; Lamb reference=1057.845020 MHz.

## C985 boundary ledger facts

- Boundary vector: (M,J,P,Phi;R33,K_mixed_S,K_pure_Sminus).
- R33 rule: R33_global(mask)=13*<[1,1,1,0,1,1,1,1,1,1,1],mask> mod 26.
- R33 sourced closed returns: 16.
- K supports: mixed S=20, pure S-=7.
- Transition gate sequence: 5,5,0,0,1,3,1,5,3,5,5,3,5,3,1,0.
- R33 pulse persistence: 16/16 steps; longest run=16.
- Dominant sink atom: 8.

## Supported evidence

- finite_boundary_sink: 16 top sinks beat null p95; 16 are R33-sourced [finite BMS/Carrollian boundary sink projection]

## Failed or unproved coupling claims

- simultaneous_hydrogen_horizon_coupling: Pearson(binding, absorption)=0.0 -> failed_zero_correlation
- raw_pressure_margin_phase_coupling: best lag 4 rho=0.372787663 null_p=0.805555556 -> failed_null
- signed_C985_flux_phase_coupling: best lag 1 rho=0.448022272 null_p=0.351388889 -> failed_null
- signed_C985_height_flux_phase_coupling: best lag 1 rho=-0.448022272 null_p=0.5125 -> failed_null
- zero_pair_ward_height_selector_phase_coupling: mask 288 best lag 4 rho=-0.433160731 null_p=0.388888889 -> failed_null
- c2_markov_orbit_height_drift_phase_coupling: 543-orbit Markov drift best lag 2 rho=0.278872718 null_p=0.815277778 -> failed_null
- c2_selector_family_mask_overlap_phase_coupling: primitive_seeded best lag 2 rho=0.282707941 null_p=0.959722222 -> failed_null
- c2_markov_trajectory_distribution_coupling: TV=0.515700921 null_p=0.125 -> failed_null
- signed_packet_quotient_hydrogen_coupling: candidate 740 support [14, 15] best lag 2 rho=-0.409577042 null_p=0.118055556 -> failed_null
- support3_signed_packet_quotient_hydrogen_coupling: candidate 2079 support [3, 8, 14] best lag 4 rho=-0.431555414 null_p=0.565277778 -> failed_null

## Boundary motif notebook

- Motif total: 16.
- Unique motifs: 4.
- Top motifs:
  - c4_row4_orbit2_targets2 x12
  - c3_row2_orbit1_targets1 x2
  - c2_row4_orbit2_targets2 x1
  - c3_row4_orbit2_targets2 x1

## Boundary motif prediction test

- Test: walk-forward motif-to-next-R33-sink prediction using only earlier pulse history.
- Best motif alphabet: component_inlet.
- Attempts: 7/15.
- Motif accuracy: 0.857142857.
- Prior-majority baseline accuracy: 0.857142857.
- Baseline lift: 0.0.
- Rotation/reversal null p-value: 0.1875.
- Verdict: MOTIF_PREDICTOR_NOT_ABOVE_BASELINE.
- Alphabet family:
  - coarse: acc=0.818181818, baseline=0.818181818, lift=0.0, p=0.3125, MOTIF_PREDICTOR_NOT_ABOVE_BASELINE
  - component_inlet: acc=0.857142857, baseline=0.857142857, lift=0.0, p=0.1875, MOTIF_PREDICTOR_NOT_ABOVE_BASELINE
  - component_sector: acc=0.857142857, baseline=0.857142857, lift=0.0, p=0.1875, MOTIF_PREDICTOR_NOT_ABOVE_BASELINE
  - c985_charge: acc=0.818181818, baseline=0.818181818, lift=0.0, p=0.3125, MOTIF_PREDICTOR_NOT_ABOVE_BASELINE
  - source_atom: acc=0.8, baseline=0.8, lift=0.0, p=0.375, MOTIF_PREDICTOR_NOT_ABOVE_BASELINE
  - source_atom_inlet: acc=0.857142857, baseline=0.857142857, lift=0.0, p=0.1875, MOTIF_PREDICTOR_NOT_ABOVE_BASELINE

## Long boundary motif forecast

- Scope: identity plus certified null-row pulse histories, still boundary-only.
- Histories: 720.
- Samples: 11520.
- Best motif alphabet: source_atom_inlet.
- Attempts: 10746/10800.
- Motif accuracy: 0.451796017.
- Prior-majority baseline accuracy: 0.131397729.
- Baseline lift: 0.320398288.
- Rotation/reversal null p-value: 0.75.
- Verdict: LONG_MOTIF_PREDICTOR_WITHIN_ROTATION_NULL.
- Alphabet family:
  - coarse: acc=0.15561319, baseline=0.131067062, lift=0.024546128, p=0.5625, LONG_MOTIF_PREDICTOR_WITHIN_ROTATION_NULL
  - component_inlet: acc=0.203447956, baseline=0.130874038, lift=0.072573918, p=0.4375, LONG_MOTIF_PREDICTOR_WITHIN_ROTATION_NULL
  - component_sector: acc=0.203447956, baseline=0.130874038, lift=0.072573918, p=0.4375, LONG_MOTIF_PREDICTOR_WITHIN_ROTATION_NULL
  - c985_charge: acc=0.247612867, baseline=0.131176416, lift=0.116436451, p=0.6875, LONG_MOTIF_PREDICTOR_WITHIN_ROTATION_NULL
  - source_atom: acc=0.384751114, baseline=0.131315007, lift=0.253436107, p=0.875, LONG_MOTIF_PREDICTOR_WITHIN_ROTATION_NULL
  - source_atom_inlet: acc=0.451796017, baseline=0.131397729, lift=0.320398288, p=0.75, LONG_MOTIF_PREDICTOR_WITHIN_ROTATION_NULL

## Held-out motif forecast splits

- Overall verdict: SPLIT_MOTIF_SIGNAL_NOT_CERTIFIED.
- History split best alphabet: source_atom_inlet.
- History split accuracy: 0.496388889.
- History split baseline: 0.133333333.
- History split null p-value: 0.013157895.
- History split verdict: SPLIT_MOTIF_PREDICTOR_ABOVE_ROTATION_NULL.
- Time-offset split best alphabet: source_atom_inlet.
- Time-offset split accuracy: 0.234190556.
- Time-offset split baseline: 0.098650927.
- Time-offset split null p-value: 0.592105263.
- Time-offset split verdict: SPLIT_MOTIF_PREDICTOR_WITHIN_ROTATION_NULL.

## Time-offset obstruction phase audit

- Variant audited: source_atom_inlet.
- Phase count: 15.
- Passing phases: 0.
- Failing phases: 15.
- Verdict: TIME_OFFSET_OBSTRUCTION_GLOBAL.
- Weakest held-out phases:
  - step 4 inlet 1 -> target inlet 3: acc=0.036111111, baseline=0.0, lift=0.036111111, p=1.0, dominant_atom=16, PHASE_WITHIN_ROTATION_NULL
  - step 14 inlet 1 -> target inlet 0: acc=0.055555556, baseline=0.0, lift=0.055555556, p=1.0, dominant_atom=5, PHASE_WITHIN_ROTATION_NULL
  - step 3 inlet 0 -> target inlet 1: acc=0.069767442, baseline=0.0, lift=0.069767442, p=1.0, dominant_atom=11, PHASE_WITHIN_ROTATION_NULL
  - step 12 inlet 5 -> target inlet 3: acc=0.14619883, baseline=0.0, lift=0.14619883, p=0.8125, dominant_atom=16, PHASE_WITHIN_ROTATION_NULL
  - step 10 inlet 5 -> target inlet 3: acc=0.163888889, baseline=0.0, lift=0.163888889, p=0.8125, dominant_atom=16, PHASE_WITHIN_ROTATION_NULL

## Explicit phase-clock baseline

- Overall verdict: MOTIF_NOT_SEPARATED_FROM_PHASE_CLOCK.
- History motif: source_atom_inlet acc=0.496388889.
- History clock: clock_step_atom acc=0.802685185.
- History residual lift: -0.306296296 -> PHASE_CLOCK_DOMINATES_HISTORY.
- Time-offset motif: source_atom_inlet acc=0.234190556.
- Time-offset clock: clock_inlet acc=0.055555556.
- Time-offset residual lift: 0.178635 -> MOTIF_TIED_WITH_PHASE_CLOCK_TIME_OFFSET.

## Paired phase-residual observable

- Overall verdict: PAIRED_MOTIF_RESIDUAL_NOT_CERTIFIED.
- History paired residual: motif_only=230, clock_only=3538, p=1.0, PAIRED_CLOCK_DOMINATES_MOTIF.
- Time-offset paired residual: motif_only=2074, clock_only=344, p=0.0, PAIRED_MOTIF_RESIDUAL_BEATS_CLOCK.

## Source-state transport separation

- Overall verdict: SOURCE_STATE_TRANSPORT_DOMINATES_WARD_MOTIF.
- History source-state best: source_atom_inlet acc=0.496388889.
- History Ward-motif best: c985_charge acc=0.248240741.
- History Ward-minus-source lift: -0.248148148.
- Time-offset source-state best: source_atom_inlet acc=0.234190556.
- Time-offset Ward-motif best: coarse acc=0.088377274.
- Time-offset Ward-minus-source lift: -0.145813282.
- Paired Ward-vs-source history: ward_only=850, source_only=3530.
- Paired Ward-vs-source time-offset: ward_only=904, source_only=2222.

## Source-conditioned Ward residual

- Overall verdict: SOURCE_CONDITIONED_WARD_RESIDUAL_NOT_CERTIFIED.
- History split: source=source_atom, ward=component_inlet, ward_acc=0.496388889, source_acc=0.423148148, residual_lift=0.073240741, null_p=0.0625, SOURCE_CONDITIONED_WARD_RESIDUAL_BEATS_NULL_PROVISIONAL.
- Time-offset split: source=source_atom, ward=component_inlet, ward_acc=0.234190556, source_acc=0.203625632, residual_lift=0.030564924, null_p=0.125, SOURCE_CONDITIONED_WARD_WITHIN_NULL.
- Null model: within-source rotations of Ward/C985 keys while source atom/inlet transport and next atoms are held fixed.

## C985 boundary-packet bridge seam

- Receipt status: BOUNDARY_PACKET_BRIDGE_SEAM_CERTIFIED_RECEIPTS.
- Raw pairing obstruction: compatible raw pairs=0, first scalar with matching=6, joint boundary/packet clearing bound=12.
- Row-normalization obstruction: all rows require even scalar=True, row scalar divisibility=6, only compatible even residue mod 6=[0, 0].
- Low-support candidate atlas: candidates=800, even-image support-2 rows=12, compatible doublets=6, all rank-one=True, support families=[[0, 11], [6, 17], [14, 15]].
- Physical reading: the current d20 boundary cannot be naively paired into ten packet horizons; any black-hole-like atom now needs a non-diagonal signed quotient or normalization stronger than scalar clearing.

## Rank-one packet families against R33/source residual

- Verdict: PACKET_FAMILY_TOUCHES_R33_AND_PROVISIONAL_RESIDUAL.
- R33 sink overlap: 3/16 transition steps, sink hit rate=0.1875.
- Family hit rows: [{'family': [0, 11], 'sink_hits': 0, 'r33_sink_hits': 0, 'steps': []}, {'family': [6, 17], 'sink_hits': 0, 'r33_sink_hits': 0, 'steps': []}, {'family': [14, 15], 'sink_hits': 3, 'r33_sink_hits': 3, 'steps': [4, 6, 14]}].
- Packet-family history residual: actual_family_attempts=3800, ward_family_acc=0.719473684, source_family_acc=0.683684211, lift=0.035789473, null_p=0.0625, PACKET_FAMILY_WARD_RESIDUAL_BEATS_NULL_PROVISIONAL.
- Packet-family time-offset residual: actual_family_attempts=3302, ward_family_acc=0.56632344, source_family_acc=0.430648092, lift=0.135675348, null_p=0.0625, PACKET_FAMILY_WARD_RESIDUAL_BEATS_NULL_PROVISIONAL.

## Signed rank-one packet quotient observable

- Overall verdict: SIGNED_PACKET_QUOTIENT_OBSERVABLE_CERTIFIED.
- Best signed support row: candidate 740 support=[{'public_atom_id': 14, 'coefficient': -1, 'public_atom_label': '{B+,V+,S+}'}, {'public_atom_id': 15, 'coefficient': -1, 'public_atom_label': '{B+,S-,S+}'}].
- R33 touch steps: [4, 6, 14]; identity mean |quotient|=90.802131805; null p95=78.159985392; null p=0.002777778; SIGNED_PACKET_QUOTIENT_TOUCHES_R33_AND_BEATS_NULL.
- Null model: signed support-2 packet quotient strength over identity pulse sequence compared with per-inlet null pulse histories.

## Signed packet quotient hydrogen-lag test

- Observable: signed_rank_one_packet_quotient_hydrogen_lag.
- Candidate/support: 740 support_atoms=[14, 15].
- Best hydrogen lag: 2 with rho=-0.409577042 and null p=0.118055556.
- Null verdict: SIGNED_PACKET_QUOTIENT_HYDROGEN_WITHIN_NULL; coupling verdict: SIGNED_PACKET_QUOTIENT_HYDROGEN_WITHIN_NULL.
- Interpretation: Tests whether the certified signed packet quotient also phase-couples to the d20 hydrogen scale; this is a null-tested coupling candidate, not a black-hole claim.

## Support-3 signed quotient screen

- Screened observable: support3_signed_public_boundary_quotient_screen.
- Candidate count: 4560; null-tested top rows=480.
- Best support-3 row: candidate 2079 support=[{'public_atom_id': 3, 'coefficient': 1, 'public_atom_label': '{B-,B+,S+}'}, {'public_atom_id': 8, 'coefficient': 1, 'public_atom_label': '{B-,V+,S+}'}, {'public_atom_id': 14, 'coefficient': 1, 'public_atom_label': '{B+,V+,S+}'}].
- Boundary quotient null result: identity mean |quotient|=157.432986694, null p=0.001388889, SUPPORT3_SIGNED_QUOTIENT_TOUCHES_R33_AND_BEATS_NULL.
- Hydrogen-lag result: best lag 4 rho=-0.431555414 null p=0.565277778, SUPPORT3_SIGNED_QUOTIENT_HYDROGEN_WITHIN_NULL.
- Interpretation: Explores the next non-diagonal C985 boundary seam after the certified support-2 rank-one quotient failed hydrogen-lag null certification; this is a screened search, not a certified packet bridge.

## A985/q12 packet projection bridge probe

- Artifact: generated/d20_hydrogen_sandpile_golay_bridge_probe.json.
- Status: D20_HYDROGEN_SANDPILE_GOLAY_BRIDGE_PROBE_PROVISIONAL_ASSIGNMENT_DEGENERATE; checks_pass=True.
- Ingress projection inventory: INGRESS_BOUNDARY_TO_LOOP_PRESENT_PACKET_PROJECTION_MISSING; missing bridge count=3.
- Mask288 q12 support-3 seed: MASK288_Q12_PACKET_SEED_SUPPORT3_EXTENSION_BLOCKED_BY_PARITY; candidates=32; even-image candidates=0; compatible doublets=0.
- one-sided seed correction: MASK288_Q12_ONE_SIDED_SEED_CORRECTION_FINDS_NEW_RANK2_FAMILIES_PROJECTION_OPEN; compatible doublets=4628; combined rank-2 families=28.
- Corrected rank-20 selection: MASK288_Q12_CORRECTED_RANK20_SELECTION_BLOCKED_BY_RANK9_IMAGE_CEILING; boundary image rank=9/20; shortfall=11.
- Natural 25-to-20 packet projection: BOUNDARY_PACKET_NATURAL_25_TO_20_PROJECTION_REJECTED_BY_PACKET_SNF; passing columns=[].
- Q42/A985 capacity: HIDDEN_Q42_A985_MATRIX_UNIT_SHADOW_RANK42_REQUIRES_PACKET_KERNEL_CHOICE; matrix-unit rank=42; packet-target excess=22.
- Physical reading: Ingress-backed C985/A985 evidence is now present, but the A985/q12-to-full-packet projection is still open: support-3 seed parity blocks the direct extension, one-sided correction finds rank-2 families, and the corrected selection is capped at rank 9 instead of the rank-20 packet target.
- Next bridge item: Lift the q12-vs-sector26 charge-sum partition fingerprint from size-profile matching to labelled class constraints; start with the residual raw11/raw36 q12=4 twin and the three size-2 packet sector26 charge-sum classes.

## Working physical interpretation

- The visible coil is best read as polarization of the finite boundary transition operator, not as an electron eigenmode and not as a micro black hole.
- The hard positive result is a stable R33-sourced boundary sink under the C985 pulse history.
- The hard negative result is that the earlier scalar, diagonal, zero-pair Ward, and C2 Markov hydrogen proxies remain inside their current null distributions.
- The source-state separation resolves the earlier phase-residual ambiguity: current atom plus inlet transport dominates the Ward/C985 motif alphabets on both held-out history and time-offset splits.
- The source-conditioned Ward residual keeps source atom/inlet transport fixed and perturbs only C985/Ward keys before any renewed hydrogen comparison.
- The source-conditioned Ward residual does not certify overall, so the sharper boundary problem is now the C985 boundary-packet bridge/normalization seam.
- The rank-one packet-family test now records whether those support-2 families touch the R33 sink and whether they explain the source-conditioned residual.
- The signed rank-one packet quotient test now decides whether the actual support-2 signed rows are strong enough as non-diagonal quotient observables.
- The ingress-backed A985/q12 bridge probe now shows the obstruction sharply: rank-2 packet families exist, but the corrected q12 image is still rank 9 rather than rank 20.
- The next useful discovery step is to label the q12-vs-sector26 charge-sum partition enough to break the remaining A985/q12 packet assignment ambiguity.

## Artifacts

- Generated report: generated/d20_black_hole_atom_lab_report.json
- Proof report: data/invariants/d20/proof_obligations/d20_black_hole_atom_lab_report/report.json
- Report sha256: fbddf1ec3f56522e8142afd20831f6546a7c357eb278ae7a74c78e48d28052d8
- Pressure atlas JS sha256: c77e52231440495699def2ecd5670a48751c65cb123da9378c3cdf82763beb04
