#!/usr/bin/env python3
"""Readable verifier entrypoint for d20.

The `src.commands.certify` entrypoint remains authoritative. This module exposes
the practical verification modes without hiding file writes behind a default:

* core: validate the mathematical core and layer statuses only;
* audit: validate core plus constructor witness and the file manifest;
* rebuild: regenerate d20.json, refresh hashes, then audit;
  pass --cached-source to reuse checked source artifacts and skip heavy source refresh;
* refresh-certificate: rescan certified invariant reports into certificate.json;
* strict-replay: validate core plus a fresh zero-axiom coorient replay;
* evidence-index: validate the lightweight data/evidence registry;
* compiler-scene-selftest: validate the source-to-scene compiler smoke test;
* compiler-a42-d20-replay: validate compiler A42/D20 coordinate replay evidence;
* compiler-nonstrict: run the cheap compiler integration gates;
* integration-nonstrict: run the cheap compiler and cubic integration gates;
* jacobian-cubic-contract: validate the normalized cubic cache input contract;
* jacobian-cubic-intake: validate the normalized cubic certificate intake protocol;
* jacobian-cubic-closure: validate the normalized cubic closure checklist;
* jacobian-cubic-status: report the normalized cubic closure level and certificate counts;
* jacobian-cubic-nonstrict: run the cheap cubic integration gates, excluding strict cache;
* jacobian-cubic-cache: validate the cached normalized cubic elimination certificates;
* talagrand-chain-audit: validate the extracted Talagrand closure chain audit;
* talagrand-kkt-obligation: validate the extracted Talagrand KKT open proof obligation;
* c985-registry: validate the C985 typed simple-object registry proof obligation;
* c985-fusion: validate the C985 fusion multiplicity typing proof obligation;
* c985-associator: validate the C985 associator rebracketing oracle proof obligation;
* c985-unit: validate the C985 unit tensor laws proof obligation;
* c985-triangle: validate the C985 unit triangle coherence proof obligation;
* c985-duality: validate the C985 transpose duality support proof obligation;
* c985-pentagon: validate the C985 pentagon chain normal form proof obligation;
* c985-zigzag: validate the C985 dual zig-zag identities proof obligation;
* c985-final: validate the final C985 finite semisimple multi-fusion certificate;
* c985-geometry: validate the C985 tensor geometry invariant-discovery readout;
* c985-d20-atlas: validate the C985-to-d20 boundary invariant atlas;
* c985-hyperbolic-graph: validate the C985-derived d20 hyperbolic boundary graph;
* c985-poincare: validate the C985-derived d20 Poincare disk embedding;
* c985-filtration: validate the C985-derived d20 Poincare landmark filtration;
* c985-nerve: validate the C985-derived d20 signature-class nerve;
* c985-chart-atlas: validate the C985-derived d20 hyperbolic chart atlas;
* c985-transition-groupoid: validate the C985-derived d20 transition groupoid;
* c985-normal-words: validate the C985-derived d20 normal-form words;
* c985-symbolic-rewrites: validate the C985-derived d20 symbolic rewrite rules;
* c985-symbolic-associativity: validate the C985-derived d20 symbolic associativity diamond;
* c985-rewrite-complex: validate the C985-derived d20 rewrite-complex hyperbolicity;
* c985-interval-sheaf: validate the C985-derived d20 geodesic interval sheaf;
* c985-preserved-core: validate the C985-derived d20 preserved-core subcomplex;
* c985-chamber-spine: validate the C985-derived d20 chamber-spine orientation;
* c985-morse-reeb: validate the C985-derived d20 Morse/Reeb quotient;
* c985-boundary-transfer: validate the C985-derived d20 boundary transfer operator;
* c985-atom-flow: validate the C985-derived d20 stationary atom-flow lift;
* c985-signature-subboundary: validate the C985-derived d20 recurrent signature subboundary;
* c985-signature-transfer: validate the C985-derived d20 signature subboundary transfer operator;
* c985-signature-spectral-cut: validate the C985-derived d20 signature transfer spectral cut;
* c985-signature-quotient: validate the C985-derived d20 signature spectral quotient dynamics;
* c985-signature-geometry: validate the C985-derived d20 signature quotient Poincare geometry;
* c985-signature-geodesic: validate the C985-derived d20 signature geodesic order;
* c985-signature-residual-chart: validate the C985-derived d20 signature geodesic residual chart;
* c985-signature-cell-complex: validate the C985-derived d20 signature residual cell complex;
* c985-signature-boundary-flux: validate the C985-derived d20 signature boundary flux cells;
* c985-signature-boundary-rates: validate the C985-derived d20 signature boundary flux quotient rates;
* c985-signature-conductance-spine: validate the C985-derived d20 signature boundary conductance spine;
* c985-signature-spine-poincare: validate the C985-derived d20 signature conductance-spine Poincare path;
* c985-signature-routing-prefix: validate the C985-derived d20 signature Poincare spine routing prefix;
* c985-signature-branching-law: validate the C985-derived d20 signature Poincare spine branching law;
* c985-signature-typed-corridors: validate the C985-derived d20 signature typed corridor grammar;
* c985-signature-gate-automaton: validate the C985-derived d20 signature gate automaton;
* c985-signature-language-graph: validate the C985-derived d20 signature language graph;
* c985-signature-aperture-fan: validate the C985-derived d20 signature aperture geodesic fan;
* c985-signature-aperture-insertion: validate the C985-derived d20 signature aperture corridor insertion;
* c985-signature-x2-splice: validate the C985-derived d20 signature x2 splice obstruction;
* c985-signature-x2-detour: validate the C985-derived d20 signature x2 detour fan;
* c985-signature-x2-clean-detour: validate the C985-derived d20 signature x2 clean detour choice;
* c985-signature-x2-x4-aperture: validate the C985-derived d20 signature x2/x4 aperture completion;
* c985-signature-aperture-cycle: validate the C985-derived d20 signature aperture carrier-cycle language;
* c985-signature-aperture-cycle-ranking: validate the C985-derived d20 signature aperture carrier-cycle ranking;
* c985-signature-aperture-cycle-pareto: validate the C985-derived d20 signature aperture-cycle Pareto frontier;
* c985-signature-aperture-mixed-contact: validate the C985-derived d20 signature aperture mixed-contact atom audit;
* c985-signature-aperture-atom-selector: validate the C985-derived d20 signature aperture atom-selector refinement;
* c985-signature-aperture-atom-tradeoff: validate the C985-derived d20 signature aperture atom-selected tradeoff;
* c985-signature-aperture-tail-hybrid: validate the C985-derived d20 signature aperture x1-tail hybrid search;
* c985-signature-aperture-bounded-backtrack: validate the C985-derived d20 signature aperture bounded backtrack search;
* c985-signature-aperture-symbol-state: validate the C985-derived d20 signature aperture symbol-state obstruction;
* c985-signature-aperture-overhead2-carrier: validate the C985-derived d20 signature aperture overhead-2 carrier realizability obstruction;
* c985-signature-aperture-overhead2-repair: validate the C985-derived d20 signature aperture overhead-2 edit-repair layer;
* c985-signature-aperture-overhead2-tail: validate the C985-derived d20 signature aperture overhead-2 post-aperture tail closure layer;
* c985-signature-aperture-overhead2-cycle-rank: validate the C985-derived d20 signature aperture overhead-2 closed-repair cycle ranking layer;
* c985-signature-aperture-overhead3-trace-quotient: validate the C985-derived d20 signature aperture overhead-3 trace-class quotient layer;
* c985-signature-aperture-rank104-audit: validate the C985-derived d20 signature aperture rank-104 branch audit layer;
* c985-signature-aperture-overhead3-weak-promotion: validate the C985-derived d20 signature aperture overhead-3 weak-repair promotion audit layer;
* c985-signature-aperture-overhead3-strongification-gap: validate the C985-derived d20 signature aperture overhead-3 pre-node44 strongification gap layer;
* c985-signature-aperture-rank104-strongification-geometry: validate the C985-derived d20 signature aperture rank-104 strongification branch geometry layer;
* c985-signature-aperture-cost3-strongification-ranking: validate the C985-derived d20 signature aperture cost-three strongification geometry ranking layer;
* c985-signature-aperture-closure-outlier-geometry: validate the C985-derived d20 signature aperture closure-rich outlier geometry layer;
* c985-signature-aperture-closure-tail-endpoint-split: validate the C985-derived d20 signature aperture closure-tail carrier endpoint split layer;
* c985-signature-aperture-closure-tail-rewrite-lift: validate the C985-derived d20 signature aperture closure-tail rewrite-node lift layer;
* c985-signature-aperture-closure-tail-prefix-chord: validate the C985-derived d20 signature aperture closure-tail prefix-chord search layer;
* c985-signature-aperture-closure-tail-carrier-splice: validate the C985-derived d20 signature aperture closure-tail carrier-splice realization layer;
* c985-signature-aperture-closure-tail-splice-optimality: validate the C985-derived d20 signature aperture closure-tail carrier-splice optimality layer;
* c985-signature-aperture-closure-tail-lower-lift: validate the C985-derived d20 signature aperture closure-tail lower-variation lift obstruction layer;
* c985-signature-aperture-closure-tail-partial-splitter: validate the C985-derived d20 signature aperture closure-tail partial-splitter search layer;
* c985-signature-aperture-closure-tail-trim-neighborhood: validate the C985-derived d20 signature aperture closure-tail trim-neighborhood search layer;
* c985-signature-aperture-closure-tail-clear-corridor: validate the C985-derived d20 signature aperture closure-tail clear-corridor layer;
* c985-signature-aperture-closure-tail-clear-corridor-level2: validate the C985-derived d20 signature aperture closure-tail level-two clear-corridor layer;
* c985-signature-aperture-closure-tail-gate-repair: validate the C985-derived d20 signature aperture closure-tail gate-repair search layer;
* c985-signature-aperture-closure-tail-boundary-bridge: validate the C985-derived d20 signature aperture closure-tail boundary-pair bridge search layer;
* c985-signature-aperture-closure-tail-virtual-graft: validate the C985-derived d20 signature aperture closure-tail virtual repair-edge graft layer;
* c985-signature-aperture-closure-tail-native-insertion: validate the C985-derived d20 signature aperture closure-tail native trace-insertion layer;
* c985-signature-aperture-closure-tail-symbolic-window: validate the C985-derived d20 signature aperture closure-tail symbolic window-refinement layer;
* c985-signature-aperture-closure-tail-skip-window-grammar: validate the C985-derived d20 signature aperture closure-tail skip-window grammar layer;
* c985-signature-aperture-closure-tail-repaired-automaton: validate the C985-derived d20 signature aperture closure-tail repaired automaton layer;
* c985-signature-aperture-closure-tail-transfer: validate the C985-derived d20 signature aperture closure-tail transfer-operator layer;
* c985-signature-aperture-closure-tail-flow-window: validate the C985-derived d20 signature aperture closure-tail flow-window lift layer;
* c985-signature-aperture-closure-tail-promoted-window: validate the C985-derived d20 signature aperture closure-tail promoted-window layer;
* c985-signature-aperture-closure-tail-promoted-transfer: validate the C985-derived d20 signature aperture closure-tail promoted transfer-operator layer;
* c985-signature-aperture-closure-tail-second-window: validate the C985-derived d20 signature aperture closure-tail second-window search layer;
* c985-signature-aperture-closure-tail-second-window-promotion: validate the C985-derived d20 signature aperture closure-tail second-window promotion layer;
* c985-signature-aperture-closure-tail-second-window-transfer: validate the C985-derived d20 signature aperture closure-tail second-window transfer-operator layer;
* c985-signature-aperture-closure-tail-sixj-frame: validate the C985-derived d20 signature aperture closure-tail 6j bottleneck frame layer;
* c985-signature-aperture-closure-tail-sixj-recoupling-pair: validate the C985-derived d20 signature aperture closure-tail 6j recoupling-pair obstruction layer;
* c985-signature-aperture-closure-tail-sixj-recoupling-triple: validate the C985-derived d20 signature aperture closure-tail 6j recoupling-triple/face obstruction layer;
* c985-signature-aperture-closure-tail-sixj-recoupling-closure: validate the C985-derived d20 signature aperture closure-tail 6j tetrahedral-closure obstruction layer;
* c985-signature-aperture-closure-tail-sixj-nonlocal-screen: validate the C985-derived d20 signature aperture closure-tail 6j nonlocal F-symbol candidate screen;
* c985-signature-aperture-closure-tail-sixj-borromean-hypergraph: validate the C985-derived d20 signature aperture closure-tail 6j Borromean hypergraph screen;
* c985-signature-aperture-closure-tail-sixj-conductance-preservation: validate the C985-derived d20 signature aperture closure-tail 6j conductance-decreasing aperture-preservation layer;
* c985-signature-aperture-closure-tail-eta6-charge: validate the C985-derived d20 signature aperture closure-tail eta6 hexagonal support charge layer;
* c985-signature-aperture-closure-tail-eta6-holonomy: validate the C985-derived d20 signature aperture closure-tail eta6 relative holonomy layer;
* c985-signature-aperture-closure-tail-eta6-dini-torsion: validate the C985-derived d20 signature aperture closure-tail eta6 Dini torsion index layer;
* c985-signature-aperture-closure-tail-eta6-h4-precursor: validate the C985-derived d20 signature aperture closure-tail eta6 H4 precursor lift layer;
* c985-signature-aperture-closure-tail-eta6-graham-throat: validate the C985-derived d20 signature aperture closure-tail eta6 Graham throat screen;
* c985-signature-aperture-closure-tail-eta6-aperture-polygon: validate the C985-derived d20 signature aperture closure-tail eta6 aperture polygon area layer;
* c985-signature-aperture-closure-tail-eta6-truncated-skeleton: validate the C985-derived d20 signature aperture closure-tail eta6 truncated-icosahedral boundary skeleton layer;
* c985-signature-aperture-closure-tail-eta6-hex-face-barycenter: validate the C985-derived d20 signature aperture closure-tail eta6 hex-face barycenter Graham screen;
* c985-signature-aperture-closure-tail-eta6-nonholonomic-aperture: validate the C985-derived d20 signature aperture closure-tail eta6 nonholonomic aperture layer;
* eta6-ext-cone: validate the eta6 exterior support cone layer;
* eta6-gordan: validate the eta6 support-plane Gordan certificate;
* eta6-aext: validate the eta6 expanded exterior-cell A_ext certificate;
* eta6-srows: validate the eta6 signed circuit-row certificate;
* eta6-islack: validate the eta6 intrinsic slack-height degeneracy certificate;
* eta6-hpol: validate the eta6 holonomy-polarized height certificate;
* eta6-surg: validate the eta6 hpol first-cut survivor-cone certificate;
* eta6-repl: validate the eta6 face-31 replacement carrier certificate;
* eta6-xfer: validate the eta6 face-31 seam transfer certificate;
* eta6-hit2: validate the second eta6 hit/collapse certificate;
* eta6-gap: validate the eta6 positive margin/gap certificate;
* eta6-p2: validate the eta6 second-hit multi-face patch certificate;
* eta6-t2: validate the eta6 p2 non-cubic transfer certificate;
* eta6-f4: validate the eta6 fused-face C985 F-address certificate;
* eta6-p5: validate the eta6 fused-face pentagon extension certificate;
* eta6-p6: validate the eta6 two-move pentagon support-spread certificate;
* eta6-p7: validate the eta6 three-move pentagon support-spread certificate;
* eta6-p8: validate the eta6 four-move pentagon support-spread certificate;
* eta6-p9: validate the eta6 bounded five-move frontier certificate;
* eta6-p10: validate the eta6 p8-shadow five-move frontier certificate;
* eta6-p11: validate the eta6 complete five-move support-spread certificate;
* eta6-p12: validate the eta6 seeded six-move support-spread certificate;
* eta6-p13: validate the eta6 p11 top-32 six-move frontier certificate;
* eta6-p14: validate the eta6 p11-basin exact six-move certificate;
* eta6-p15: validate the eta6 full-144 centered grid six-move screen;
* eta6-p16: validate the eta6 p15 top-16 carrier-margin packet;
* eta6-p17: validate the eta6 exact 2+2+2 face/mask balance-class search;
* eta6-p18: validate the eta6 wide outside-2+2+2 grid screen;
* eta6-p19: validate the eta6 expanded outside-2+2+2 grid screen;
* eta6-p20: validate the eta6 global six-move floor by cell capture;
* eta6-p21: validate the eta6 exact-floor surgery gate packet;
* eta6-p22: validate the eta6 exact-floor symbolic carrier rebuild;
* eta6-p23: validate the eta6 symbolic-to-geometric carrier face lift;
* eta6-p24: validate the eta6 lifted-face C985 F-address recomputation;
* eta6-p25: validate the eta6 lifted-face pentagon recomputation;
* eta6-p26: validate the eta6 finite-horizon margin packet;
* eta6-p27: validate the eta6 lifted two-move compound screen;
* eta6-p28: validate the eta6 lifted three-move compound screen;
* eta6-p29: validate the eta6 lifted four-move compound screen;
* eta6-p30: validate the eta6 lifted bounded five-move frontier screen;
* eta6-p31: validate the eta6 lifted complete five-move screen;
* eta6-p32: validate the eta6 p32 seeded six-move screen;
* eta6-p33: validate the eta6 p33 basin screen;
* eta6-p34: validate the eta6 p34 top-128 basin screen;
* eta6-p35: validate the eta6 p35 top-512 basin screen;
* eta6-p36: validate the eta6 p36 top-2048 basin screen;
* eta6-p37: validate the eta6 p37 top-8192 basin screen;
* eta6-p38: validate the eta6 p38 p37-branch-bound screen;
* eta6-p39: validate the eta6 p39 packed top-32768 basin screen;
* eta6-p40: validate the eta6 p40 top-131072 branch envelope;
* eta6-core: validate the compact eta6 structural spine certificate;
* long-lln: validate the finite Alexandrov-line tensor lookup LLN certificate;
* long-kern: validate finite Alexandrov-line support kernels and principal-open LLN profiles;
* long-tri: validate the ternary Alexandrov closure and weak-order LLN profiles;
* long-basis: validate the irredundant closure basis for the finite line lookup;
* long-rec: validate the basis-owner transition kernel for the finite line lookup;
* long-eta: validate the eta6 gate sample bridge into the finite line transition kernel;
* long-eta2: validate the full p21 gate support-fiber projection into the finite line transition kernel;
* long-lap: validate the eta6 active-owner Laplacian/conductance certificate;
* long-cut: validate the eta6 active-owner cut/effective-resistance certificate;
* long-flow: validate the ambient leakage shell-flow certificate around the eta6 active owners;
* long-absorb: validate the inactive-owner absorbing Dirichlet kernel around the eta6 active owners;
* long-spec: validate the reduced three-terminal Schur/spectral boundary certificate;
* long-markov: validate the reversible boundary Markov/finite-LLN certificate;
* long-dev: validate the finite path-sum deviation/Chernoff certificate;
* long-prof: validate the finite profunctor tensor-lookup chain certificate;
* long-rate: validate the finite rational cumulant/rate certificate;
* long-conv: validate the finite stateful convolution tensor-lookup certificate;
* long-cls: validate the finite concentration/LLN shrinkage certificate;
* long-univ: validate the finite universal LLN profunctor diagram certificate;
* long-min: validate the finite universal LLN forcing-basis certificate;
* long-nat: validate the finite universal LLN naturality dependency certificate;
* long-hlim: validate the finite LLN horizon-limit obstruction certificate;
* long-ext: validate the finite LLN formal profunctor-extension certificate;
* long-obj: validate the finite LLN tensor-object gap certificate;
* long-tens: validate the finite LLN component-path tensor expansion gap certificate;
* long-lift: validate the finite LLN owner/component tensor-lift quotient certificate;
* long-raw: validate the finite LLN raw-owner support lift certificate;
* long-h16: validate the finite LLN horizon-16 profunctor boundary certificate;
* long-path: validate the finite LLN explicit raw product path witness certificate;
* long-comp: validate the finite LLN Alexandrov-zeta composable path certificate;
* long-sheaf: validate the finite LLN Alexandrov interval-support sheaf certificate;
* long-all: validate the finite LLN full raw oriented interval-sheaf certificate;
* long-orient: validate the finite LLN orientation-duality Mobius split certificate;
* long-dual: validate the finite LLN coefficient-dual witness-kernel certificate;
* long-prob: validate the finite LLN dual probability and variance-decomposition certificate;
* long-mart: validate the finite LLN conditional transport/martingale-boundary certificate;
* long-stop: validate the finite LLN stopped-tail transport certificate;
* long-dlim: validate the finite LLN drift-limit obstruction certificate;
* long-linf: validate the finite LLN lifted eventual-cone certificate;
* long-ind: validate the finite LLN symbolic drift-margin induction schema;
* long-suppind: validate the finite LLN support-shift cumulative inequality certificate;
* long-recind: validate the finite LLN support-gap recurrence graph certificate;
* long-formind: validate the finite LLN recurrence formula-index certificate;
* long-domind: validate the finite LLN recurrence tail-dominance certificate;
* long-gapind: validate the finite LLN global support-gap induction assembly;
* long-llnind: validate the finite LLN tensor-lookup induction bridge;
* long-thm: validate the finite LLN theorem-status certificate;
* long-inv: validate the finite-line invariant inventory certificate;
* long-inv-exhaust: validate the bounded finite-line invariant inventory cover;
* long-anom: validate the finite anomaly correction oracle certificate;
* long-mat: validate the finite matrix-theoretic charge-wall oracle boundary;
* long-auto: validate the finite automorphic/Fourier oracle boundary certificate;
* long-orac: validate the local oracle/anomaly status split certificate;
* long-gr: validate the A985-to-general-relativity derivation pathway certificate;
* long-lor: validate the finite Lorentzian time-quotient scaffold certificate;
* long-time-map: validate the materialized finite normal-form time-map certificate;
* long-time-sem: validate the semantic edge-operation obstruction certificate;
* long-metric-gate: validate the guarded finite metric pathway gate certificate;
* long-contact-lift: validate the owner-boundary contact-lift certificate;
* long-transition-sem: validate the contact-lift transition semantic obstruction certificate;
* long-stress20: validate the stress graph versus canonical 20-gon comparison certificate;
* long-stress-gate: validate the finite stress readout gate certificate;
* long-stress-couple: validate the stress-transition coupling current-boundary obstruction certificate;
* long-semstress: validate the semantic-row to stress-node source measure certificate;
* long-metric-rank-gate: validate the finite metric rank gate certificate;
* long-dim4-gate: validate the 1+3 reduction current-boundary obstruction certificate;
* long-rim: validate the complement-antipodal C20 rim defect phase classification certificate;
* long-rim-select: validate the golden rim phase selection current-boundary obstruction certificate;
* long-sel: validate the physical selector axiom current-boundary obstruction certificate;
* long-psel: validate the physical selector contract first-failure certificate;
* long-pax: validate the physical selector axiom candidate certificate;
* long-l63: validate the lazy63-to-rim bridge current-boundary obstruction certificate;
* long-f63: validate the fixed63 exterior D20 boundary bridge certificate;
* long-frim: validate the fixed63 rim/stress lift obstruction certificate;
* long-sfork: validate the selector branch frontier certificate;
* long-glaw: validate the formal golden selector law certificate;
* long-gclk: validate the Stage 5 F2^6 bridge and affine golden clock certificate;
* long-tlift: validate the affine tick transition-lift obstruction certificate;
* long-abmap: validate the atom-to-endpoint-basis functor obstruction certificate;
* long-rtick: validate the relation-valued affine tick cover certificate;
* long-rsem: validate the guarded relation-valued transition semantic law certificate;
* long-oprom: validate the golden guarded-relation operation-promotion gate;
* long-c60op: validate the Stage 5 C60 semantic opcode assignment certificate;
* long-c60negf: validate the Stage 6 C60 DFT/NEGF validation protocol certificate;
* long-c59x: validate the C59X signed sentinel edge-routing certificate;
* long-c59e: validate the C59X signed edge ansatz certificate;
* long-c59cf: validate the C59X minimal counterflow certificate;
* long-c59st: validate the C59X symmetric stress candidate certificate;
* long-c59kt: validate the C59X kernel/time seam certificate;
* long-c59q: validate the C59X gauge-null quotient certificate;
* long-c59pk: validate the C59X induced public-kernel restriction certificate;
* long-c59s3: validate the C59X principal three-subform search certificate;
* long-c59np3: validate the C59X non-principal three-plane witness certificate;
* long-c59p3s: validate the C59X non-principal three-plane selector gate certificate;
* long-c59p3v: validate the C59X low-support volume selector pair certificate;
* long-c59p3o: validate the C59X sign-dual orientation obstruction certificate;
* long-c59p3a: validate the C59X atom-overlap stress orientation candidate certificate;
* long-c59p3t: validate the C59X transition-stress lift gate certificate;
* long-c59p3b: validate the C59X basis-to-stress-atom bridge obstruction certificate;
* long-c59p3r: validate the C59X relation-valued stress-extension gate certificate;
* long-c59p3i: validate the C59X visible-tick stress-incidence obstruction certificate;
* long-c59p3f: validate the C59X formal selector stress-pushforward certificate;
* long-c59p3u: validate the C59X formal stress-source operation gate certificate;
* long-c59p3w: validate the C59X formal stress-source balance gate certificate;
* long-c59p3c: validate the C59X formal local counterterm certificate;
* long-c59p3d: validate the C59X counterterm selector-carrier certificate;
* long-c59p3e: validate the C59X exact selector-weight distribution certificate;
* long-c59p3g: validate the C59X operation schema-gap certificate;
* long-c59p3h: validate the C59X active endpoint-field address-map screen certificate;
* long-c59p3j: validate the C59X endpoint-projector degeneracy certificate;
* long-c59p3k: validate the C59X mixed contact address-screen certificate;
* long-c59p3m: validate the C59X normalized operation-promotion gate certificate;
* long-c59p3n: validate the C59X clock/packet denominator normalization certificate;
* long-frontier: validate the oracle-driven certificate frontier planner;
* long-cluster: validate the oracle reopen clustering certificate;
* long-c2uf: validate the focused C2 univalent-foundation seam certificate;
* long-hcinv: validate the height-coherent action-return invariant ledger;
* long-hcfoam: validate the Foam target operator matrix family;
* long-hcpi: validate the remaining height-coherent projection input gap;
* long-hcshape: validate the 56-to-33 projection-shape certificate;
* long-hcscalar: validate the abstract scalar-completion certificate;
* long-hcsupp: validate the e33 relation-support profile certificate;
* long-hcbasis: validate the sector33 local center-basis expansion certificate;
* long-hcgrade: validate the sector33 center-grade rank-lift certificate;
* long-hcperm: validate the signed-column lift obstruction certificate;
* long-k23: validate the sector33 K23 punctured-MOG syzygy aperture target certificate;
* long-k23oct: validate the sector33 K23 typed W24 octad-placement certificate;
* long-k23row: validate the selected sector33 K23/W24 rowspace-subcode certificate;
* long-k23max: validate the current delete/contract K23/W24 max-rank-one certificate;
* long-psec: validate the focused A985 perennial-sector address seam certificate;
* long-binc: validate the focused boundary/Loop/packet incidence seam certificate;
* long-krein: validate the provisional Krein denominator source-boundary report;
* long-kr39: validate the direct 39-sector A985 Hadamard screen certificate;
* long-b3mod: validate the Gamma action/module-basis source-boundary report;
* long-b3alg: validate the Gamma class-algebra multiplication tensor;
* long-gchar: validate the Gamma modular character diagonalization certificate;
* a985-direct-packet-bridge: validate the direct-label A985 packet-bridge no-go theorem;
* a985-mat2-hom-boundary: validate the faithful/nonfaithful A985 Mat2 homomorphism boundary;
* a985-labelled-nonfaithful-packet-hom: validate the labelled nonfaithful A985 packet homomorphism obstruction;
* long-pobj: validate the selected-witness path-object closure decision;
* long-paths: validate compressed raw product path-family accounting;
* long-measure: validate scoped active raw product-family probability laws;
* c985-signature-aperture-closure-tail-sixj-2114-neighborhood: validate the C985-derived d20 signature aperture closure-tail 6j nonlocal 2114 neighborhood screen;
* c985-signature-aperture-closure-tail-sixj-2114-triple: validate the C985-derived d20 signature aperture closure-tail 6j nonlocal 2114 triple screen;
* token-burn: validate bounded-output guard coverage for repo-defined runners;
* tamper: mutate certified evidence in memory and require verification failure.
"""
from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import argparse
import contextlib
import io
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.runtime import ensure_numpy_runtime  # noqa: E402

ensure_numpy_runtime(ROOT, __file__)

from src.commands import certify  # noqa: E402
from src.evidence_registry import EVIDENCE_INDEX_PATH, sha_file  # noqa: E402
from src.token_burn_guard import emit_json  # noqa: E402

EVIDENCE_INDEX = EVIDENCE_INDEX_PATH
DATA_INDEX = ROOT / "data" / "index.json"
CUBIC_EVIDENCE_ID = "jacobian_cubic_symbolic_elimination"
CUBIC_EVIDENCE_ROOT = "data/evidence/jacobian_cubic_symbolic_elimination"
CUBIC_DATA_DOMAIN = "jacobian_cubic_symbolic_elimination_evidence"
COMPILER_A42_D20_EVIDENCE_ID = "compiler_a42_d20_replay_test"
COMPILER_A42_D20_EVIDENCE_ROOT = "data/evidence/compiler_a42_d20_replay_test"
COMPILER_A42_D20_MANIFEST = "data/evidence/compiler_a42_d20_replay_test/manifest.json"
COMPILER_A42_D20_STATUS = "COMPILER_A42_D20_REPLAY_CERTIFIED"
COMPILER_A42_D20_DATA_DOMAIN = "compiler_a42_d20_replay_evidence"
TOKEN_BURN_EVIDENCE_ID = "token_burn_guard"
TOKEN_BURN_CERTIFICATE = "data/evidence/token_burn_guard/certificate.json"
TOKEN_BURN_STATUS = "TOKEN_BURN_GUARD_CERTIFIED"
TALAGRAND_EVIDENCE_ID = "talagrand_python_handoff"
TALAGRAND_EVIDENCE_ROOT = "data/evidence/talagrand_python_handoff"
TALAGRAND_MANIFEST = "data/evidence/talagrand_python_handoff/manifest.json"
TALAGRAND_DATA_DOMAIN = "talagrand_python_handoff_evidence"
TALAGRAND_STATUS = "TALAGRAND_PYTHON_HANDOFF_IMPORTED_WITH_OPEN_GLOBAL_TARGET"


MODES = {
    "core": "fast",
    "audit": "audit",
    "rebuild": "rebuild",
    "strict-replay": "strict-replay",
    "token-burn": "token-burn",
    "tamper": "tamper",
}


def emit(obj: dict[str, Any], pretty: bool) -> None:
    emit_json(obj, pretty=pretty)


def run(command: str, *, pretty: bool) -> int:
    mode = MODES[command]
    result = certify.run(mode)
    return finish(result, pretty)


def rebuild(*, pretty: bool, cached_source: bool = False) -> int:
    regen_info = certify.maybe_regenerate(
        "rebuild",
        pretty,
        True,
        refresh_sources=not cached_source,
    )
    result = certify.run("rebuild")
    result["regeneration"] = regen_info
    return finish(result, pretty)


def refresh_certificate(*, pretty: bool) -> int:
    from src.commands import regen

    certificate = regen.refresh_certificate()
    manifest_entry = regen.refresh_manifest_entry(ROOT / "certificate.json")
    cert_payload, cert_error = read_json_or_error(ROOT / "certificate.json")
    inventory = (
        cert_payload.get("invariant_report_inventory", {})
        if isinstance(cert_payload.get("invariant_report_inventory"), dict)
        else {}
    )
    checks = {
        "certificate_json_valid": cert_error is None,
        "certificate_refresh_scanned_all_reports": certificate.get("invariant_report_count")
        == inventory.get("report_count"),
        "certified_report_count_matches_inventory": certificate.get("certified_invariant_report_count")
        == inventory.get("certified_report_count"),
        "provisional_report_count_matches_inventory": certificate.get("provisional_invariant_report_count")
        == inventory.get("provisional_report_count"),
        "demoted_report_count_matches_inventory": certificate.get("demoted_invariant_report_count")
        == inventory.get("demoted_report_count"),
        "manifest_certificate_entry_updated": manifest_entry.get("manifest_entry_updated") is True,
    }
    result = {
        "schema": "d20.verification.refresh_certificate",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "certificate": certificate,
        "manifest_entry": manifest_entry,
        "errors": [] if all(checks.values()) else [key for key, passed in checks.items() if not passed],
    }
    return finish(result, pretty)


def read_json_or_error(path: Path) -> tuple[dict[str, Any], str | None]:
    if not path.exists():
        return {}, "missing"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {}, f"invalid_json: {exc}"
    if not isinstance(payload, dict):
        return {}, "not_object"
    return payload, None


def verify_evidence_index(*, pretty: bool) -> int:
    index, index_error = read_json_or_error(EVIDENCE_INDEX)
    data_index, data_index_error = read_json_or_error(DATA_INDEX)
    entries = index.get("evidence_roots", []) if isinstance(index.get("evidence_roots"), list) else []
    errors: list[str] = []
    if index_error is not None:
        errors.append(f"evidence index unreadable: {index_error}")
    if data_index_error is not None:
        errors.append(f"data registry unreadable: {data_index_error}")
    if index.get("schema") != "d20.evidence.index":
        errors.append("evidence index schema mismatch")

    seen_ids: set[str] = set()
    checked_entries: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("evidence index entry is not an object")
            continue
        entry_id = str(entry.get("id", ""))
        if not entry_id:
            errors.append("evidence index entry missing id")
        elif entry_id in seen_ids:
            errors.append(f"duplicate evidence index id: {entry_id}")
        seen_ids.add(entry_id)

        root_ref = str(entry.get("root", ""))
        entrypoint = entry.get("entrypoint", {})
        entrypoint_ref = str(entrypoint.get("path", "")) if isinstance(entrypoint, dict) else ""
        expected_sha = entrypoint.get("sha256") if isinstance(entrypoint, dict) else None
        root_path = ROOT / root_ref
        entrypoint_path = ROOT / entrypoint_ref
        actual_sha = sha_file(entrypoint_path) if entrypoint_path.exists() else None
        if not root_path.exists():
            errors.append(f"evidence root missing: {root_ref}")
        if not entrypoint_path.exists():
            errors.append(f"evidence entrypoint missing: {entrypoint_ref}")
        if expected_sha and actual_sha and expected_sha != actual_sha:
            errors.append(f"evidence entrypoint hash mismatch: {entrypoint_ref}")
        checked_entries.append(
            {
                "id": entry_id,
                "root": root_ref,
                "entrypoint": entrypoint_ref,
                "entrypoint_sha256": actual_sha,
                "status": entry.get("status"),
            }
        )

    data_domains = data_index.get("domains", {}) if isinstance(data_index.get("domains"), dict) else {}
    planned_layout = data_index.get("planned_layout", {}) if isinstance(data_index.get("planned_layout"), dict) else {}
    cubic_domain = data_domains.get(CUBIC_DATA_DOMAIN)
    cubic_registry_checks = {
        "evidence_index_has_cubic_root": any(
            entry.get("id") == CUBIC_EVIDENCE_ID and entry.get("root") == CUBIC_EVIDENCE_ROOT
            for entry in entries
            if isinstance(entry, dict)
        ),
        "data_registry_has_cubic_domain": isinstance(cubic_domain, dict),
        "data_registry_cubic_path_matches": isinstance(cubic_domain, dict)
        and cubic_domain.get("path") == CUBIC_EVIDENCE_ROOT,
        "data_registry_cubic_target_matches": isinstance(cubic_domain, dict)
        and cubic_domain.get("target_path") == CUBIC_EVIDENCE_ROOT,
        "data_registry_cubic_required_files": isinstance(cubic_domain, dict)
        and {
            "README.md",
            "manifest.json",
            "saturation_certificate_closure_checklist.json",
            "saturation_certificate_jobs.json",
            "saturation_certificate_queue.json",
            "saturation_certificate_queue_audit.json",
            "saturation_certificate_source_audit.json",
            "saturation_certificate_intake_protocol.json",
            "saturation_certificate_status_summary.json",
        }.issubset(
            set(cubic_domain.get("required_files", []))
        ),
        "planned_layout_describes_cubic_root": CUBIC_EVIDENCE_ROOT in planned_layout,
    }
    for check, passed in cubic_registry_checks.items():
        if not passed:
            errors.append(f"cubic registry coherence failed: {check}")

    compiler_entry = next(
        (
            entry
            for entry in entries
            if isinstance(entry, dict) and entry.get("id") == COMPILER_A42_D20_EVIDENCE_ID
        ),
        {},
    )
    compiler_entrypoint = compiler_entry.get("entrypoint", {}) if isinstance(compiler_entry, dict) else {}
    compiler_domain = data_domains.get(COMPILER_A42_D20_DATA_DOMAIN)
    compiler_registry_checks = {
        "evidence_index_has_compiler_a42_d20_root": bool(compiler_entry),
        "compiler_a42_d20_status_matches": isinstance(compiler_entry, dict)
        and compiler_entry.get("status") == COMPILER_A42_D20_STATUS,
        "compiler_a42_d20_root_matches": isinstance(compiler_entry, dict)
        and compiler_entry.get("root") == COMPILER_A42_D20_EVIDENCE_ROOT,
        "compiler_a42_d20_entrypoint_matches": isinstance(compiler_entrypoint, dict)
        and compiler_entrypoint.get("path") == COMPILER_A42_D20_MANIFEST,
        "compiler_a42_d20_manifest_exists": (ROOT / COMPILER_A42_D20_MANIFEST).exists(),
        "data_registry_has_compiler_a42_d20_domain": isinstance(compiler_domain, dict),
        "data_registry_compiler_a42_d20_path_matches": isinstance(compiler_domain, dict)
        and compiler_domain.get("path") == COMPILER_A42_D20_EVIDENCE_ROOT,
        "data_registry_compiler_a42_d20_target_matches": isinstance(compiler_domain, dict)
        and compiler_domain.get("target_path") == COMPILER_A42_D20_EVIDENCE_ROOT,
        "data_registry_compiler_a42_d20_required_files": isinstance(compiler_domain, dict)
        and {
            "CORE.lock.json",
            "manifest.json",
            "report.json",
            "support_coordinates.json",
            "positive/TURN.lock.json",
            "positive/08_residue_ledger.json",
            "missing_coordinate/08_residue_ledger.json",
            "tampered_coordinate/04_support_ledger.json",
        }.issubset(set(compiler_domain.get("required_files", []))),
        "planned_layout_describes_compiler_a42_d20_root": COMPILER_A42_D20_EVIDENCE_ROOT
        in planned_layout,
    }
    for check, passed in compiler_registry_checks.items():
        if not passed:
            errors.append(f"compiler A42/D20 registry coherence failed: {check}")

    token_entry = next(
        (
            entry
            for entry in entries
            if isinstance(entry, dict) and entry.get("id") == TOKEN_BURN_EVIDENCE_ID
        ),
        {},
    )
    token_entrypoint = token_entry.get("entrypoint", {}) if isinstance(token_entry, dict) else {}
    token_registry_checks = {
        "evidence_index_has_token_burn_root": bool(token_entry),
        "token_burn_status_matches": isinstance(token_entry, dict)
        and token_entry.get("status") == TOKEN_BURN_STATUS,
        "token_burn_entrypoint_matches": isinstance(token_entrypoint, dict)
        and token_entrypoint.get("path") == TOKEN_BURN_CERTIFICATE,
        "token_burn_certificate_exists": (ROOT / TOKEN_BURN_CERTIFICATE).exists(),
    }
    for check, passed in token_registry_checks.items():
        if not passed:
            errors.append(f"token-burn registry coherence failed: {check}")

    talagrand_domain = data_domains.get(TALAGRAND_DATA_DOMAIN)
    talagrand_entry = next(
        (
            entry
            for entry in entries
            if isinstance(entry, dict) and entry.get("id") == TALAGRAND_EVIDENCE_ID
        ),
        {},
    )
    talagrand_entrypoint = talagrand_entry.get("entrypoint", {}) if isinstance(talagrand_entry, dict) else {}
    talagrand_registry_checks = {
        "evidence_index_has_talagrand_root": bool(talagrand_entry),
        "talagrand_status_matches": isinstance(talagrand_entry, dict)
        and talagrand_entry.get("status") == TALAGRAND_STATUS,
        "talagrand_root_matches": isinstance(talagrand_entry, dict)
        and talagrand_entry.get("root") == TALAGRAND_EVIDENCE_ROOT,
        "talagrand_entrypoint_matches": isinstance(talagrand_entrypoint, dict)
        and talagrand_entrypoint.get("path") == TALAGRAND_MANIFEST,
        "talagrand_manifest_exists": (ROOT / TALAGRAND_MANIFEST).exists(),
        "data_registry_has_talagrand_domain": isinstance(talagrand_domain, dict),
        "data_registry_talagrand_path_matches": isinstance(talagrand_domain, dict)
        and talagrand_domain.get("path") == TALAGRAND_EVIDENCE_ROOT,
        "data_registry_talagrand_target_matches": isinstance(talagrand_domain, dict)
        and talagrand_domain.get("target_path") == TALAGRAND_EVIDENCE_ROOT,
        "data_registry_talagrand_required_files": isinstance(talagrand_domain, dict)
        and {"README_HANDOFF.md", "RUN_ORDER.md", "STATUS_LEDGER.json", "MANIFEST.csv", "manifest.json"}.issubset(
            set(talagrand_domain.get("required_files", []))
        ),
        "planned_layout_describes_talagrand_root": TALAGRAND_EVIDENCE_ROOT in planned_layout,
    }
    for check, passed in talagrand_registry_checks.items():
        if not passed:
            errors.append(f"talagrand handoff registry coherence failed: {check}")

    result = {
        "schema": "d20.verification.evidence_index",
        "status": "PASS" if not errors else "FAIL",
        "data_registry": str(DATA_INDEX.relative_to(ROOT).as_posix()),
        "cubic_registry_checks": cubic_registry_checks,
        "compiler_a42_d20_registry_checks": compiler_registry_checks,
        "token_burn_registry_checks": token_registry_checks,
        "talagrand_registry_checks": talagrand_registry_checks,
        "index": str(EVIDENCE_INDEX.relative_to(ROOT).as_posix()),
        "entry_count": len(entries),
        "checked_entries": checked_entries,
        "errors": errors,
    }
    return finish(result, pretty)


def compiler_a42_d20_replay(*, pretty: bool) -> int:
    from src.compiler.common import sha256_json
    from src.compiler_a42_d20_replay_test import (
        LOCK_FILE,
        MANIFEST,
        REPORT,
        STAGING_ROOT,
        STATUS,
        build_manifest,
        run_test,
    )

    generated_error = None
    try:
        generated_report = run_test()
    except Exception as exc:
        generated_report = {"status": "FAIL"}
        generated_error = f"{type(exc).__name__}: {exc}"
    report_payload, report_error = read_json_or_error(REPORT)
    manifest_payload, manifest_error = read_json_or_error(MANIFEST)
    report_body = {key: value for key, value in report_payload.items() if key != "certificate_sha256"}
    manifest_body = {key: value for key, value in manifest_payload.items() if key != "manifest_sha256"}
    expected_manifest = build_manifest(report_payload) if report_error is None else {}
    checks_payload = (
        manifest_payload.get("checks", {}) if isinstance(manifest_payload.get("checks"), dict) else {}
    )
    promotion = (
        manifest_payload.get("promotion", {}) if isinstance(manifest_payload.get("promotion"), dict) else {}
    )
    checks = {
        "test_report_generated": generated_report.get("status") == "PASS",
        "report_written": REPORT.exists(),
        "report_json_valid": report_error is None,
        "report_matches_generated_payload": report_payload == generated_report,
        "report_hash_matches_payload": report_payload.get("certificate_sha256") == sha256_json(report_body),
        "manifest_written": MANIFEST.exists(),
        "manifest_json_valid": manifest_error is None,
        "manifest_matches_report": manifest_payload == expected_manifest,
        "manifest_hash_matches_payload": manifest_payload.get("manifest_sha256") == sha256_json(manifest_body),
        "manifest_status_certified": manifest_payload.get("status") == STATUS,
        "manifest_declares_locked_staging_promotion": promotion.get("method")
        == "locked_staging_then_file_replace"
        and promotion.get("lock_file") == str(LOCK_FILE.relative_to(ROOT).as_posix())
        and promotion.get("manifest_promoted_last") is True,
        "write_lock_released": not LOCK_FILE.exists(),
        "staging_directory_clear": not STAGING_ROOT.exists() or not any(STAGING_ROOT.iterdir()),
        "positive_a42_d20_coordinate_replay_passed": checks_payload.get(
            "positive_a42_d20_coordinate_replay"
        )
        is True,
        "missing_coordinate_blocks_passed": checks_payload.get("missing_coordinate_blocks") is True,
        "tampered_coordinate_fails_replay_passed": checks_payload.get(
            "tampered_coordinate_fails_replay"
        )
        is True,
    }
    result = {
        "schema": "d20.verification.compiler_a42_d20_replay",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "generated_error": generated_error,
        "report": str(REPORT.relative_to(ROOT).as_posix()),
        "report_error": report_error,
        "manifest": str(MANIFEST.relative_to(ROOT).as_posix()),
        "manifest_error": manifest_error,
        "positive": generated_report.get("checks", {}).get("positive_a42_d20_coordinate_replay"),
        "missing_coordinate": generated_report.get("checks", {}).get("missing_coordinate_blocks"),
        "tampered_coordinate": generated_report.get("checks", {}).get("tampered_coordinate_fails_replay"),
    }
    return finish(result, pretty)


def compiler_scene_selftest(*, pretty: bool) -> int:
    from src.compiler.scene_compiler import run_scene_selftest

    selftest = run_scene_selftest()
    checks_payload = selftest.get("checks", {}) if isinstance(selftest.get("checks"), dict) else {}
    verification = selftest.get("verification", {}) if isinstance(selftest.get("verification"), dict) else {}
    checks = {
        "selftest_passes": selftest.get("status") == "PASS",
        "d20_boundary_present": checks_payload.get("d20_boundary") is True,
        "scene_ir_schema_present": checks_payload.get("scene_ir_schema") is True,
        "source_hash_present": checks_payload.get("has_source_hash") is True,
        "observation_ledger_present": checks_payload.get("has_observation_ledger") is True,
        "admission_ledger_present": checks_payload.get("has_admission_ledger") is True,
        "receipt_ledger_present": checks_payload.get("has_receipt_ledger") is True,
        "verify_scene_passes": verification.get("status") == "PASS",
        "verify_scene_promotes_claims": int(verification.get("promoted_claim_count", 0)) > 0,
        "no_pending_claims": int(verification.get("pending_claim_count", 0)) == 0,
    }
    result = {
        "schema": "d20.verification.compiler_scene_selftest",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "program_hash": selftest.get("program_hash"),
        "summary": selftest.get("summary"),
        "verification_status": verification.get("status"),
        "promoted_claim_count": verification.get("promoted_claim_count"),
        "pending_claim_count": verification.get("pending_claim_count"),
    }
    return finish(result, pretty)


def talagrand_handoff(*, pretty: bool) -> int:
    from src.verify_talagrand_handoff import validate_manifest

    return finish(validate_manifest(), pretty)


def talagrand_kkt_obligation(*, pretty: bool) -> int:
    from src.certify_d20_talagrand_multilevel_kkt_obstruction_system import (
        validate_d20_talagrand_multilevel_kkt_obstruction_system,
    )

    return finish(validate_d20_talagrand_multilevel_kkt_obstruction_system(), pretty)


def talagrand_chain_audit(*, pretty: bool) -> int:
    from src.certify_d20_talagrand_closure_chain_audit import (
        validate_d20_talagrand_closure_chain_audit,
    )

    return finish(validate_d20_talagrand_closure_chain_audit(), pretty)


def jacobian_cubic_cache(*, pretty: bool) -> int:
    from src.certify_jacobian_cubic_symbolic_elimination_attempt import verify_saturation_cache

    verification = verify_saturation_cache()
    indexed_contract = verification.get("indexed_contract")
    indexed_manifest = verification.get("indexed_manifest")
    cache_manifest = verification.get("manifest_file")
    errors = verification.get("errors", [])
    missing_certificate_count = sum(
        1 for error in errors if isinstance(error, dict) and error.get("check") == "cache_present"
    )
    checks = {
        "cache_verifier_passed": verification.get("status") == "PASS",
        "expected_certificate_count_is_48": verification.get("expected_certificate_count") == 48,
        "verified_certificate_count_is_48": verification.get("verified_certificate_count") == 48,
        "no_extra_cache_files": not verification.get("extra_cache_files"),
        "no_cache_errors": not errors,
        "cache_manifest_written": bool(cache_manifest) and (ROOT / str(cache_manifest)).exists(),
        "indexed_contract_written": bool(indexed_contract) and (ROOT / str(indexed_contract)).exists(),
        "indexed_manifest_status_matches_cache_status": verification.get("indexed_manifest_written") is True
        and verification.get("indexed_manifest_sha256") is not None,
    }
    result = {
        "schema": "d20.verification.jacobian_cubic_saturation_cache",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "cache_directory": verification.get("cache_directory"),
        "cache_manifest": cache_manifest,
        "cache_manifest_sha256": verification.get("manifest_sha256"),
        "error_count": len(errors),
        "first_errors": errors[:5],
        "indexed_contract": indexed_contract,
        "indexed_contract_sha256": verification.get("indexed_contract_sha256"),
        "indexed_manifest": indexed_manifest,
        "indexed_manifest_sha256": verification.get("indexed_manifest_sha256"),
        "missing_certificate_count": missing_certificate_count,
        "promoted_certificate_count": verification.get("promoted_certificate_count"),
        "promotion_requested": verification.get("promotion_requested"),
        "staging_cache_directory": verification.get("staging_cache_directory"),
        "verified_certificate_count": verification.get("verified_certificate_count"),
    }
    return finish(result, pretty)


def jacobian_cubic_contract(*, pretty: bool) -> int:
    from src.certify_jacobian_cubic_symbolic_elimination_attempt import (
        CERTIFICATE_JOB_PLAN,
        CERTIFICATE_QUEUE,
        CERTIFICATE_QUEUE_AUDIT,
        CERTIFICATE_SOURCE_AUDIT,
        CERTIFICATE_INTAKE_PROTOCOL,
        CERTIFICATE_CLOSURE_CHECKLIST,
        CERTIFICATE_STATUS_SUMMARY,
        EVIDENCE_MANIFEST,
        EVIDENCE_README,
        INDEXED_CACHE_CONTRACT,
        expected_saturation_cache_specs,
        saturation_certificate_job_plan,
        saturation_certificate_intake_protocol,
        saturation_certificate_queue,
        saturation_certificate_source_audit,
        saturation_cache_contract,
        saturation_closure_checklist,
        saturation_evidence_manifest,
        saturation_queue_audit,
        saturation_status_summary,
        sha_json,
    )

    specs = expected_saturation_cache_specs()
    expected_contract = saturation_cache_contract(specs)
    input_hashes = [spec["input_sha256"] for spec in specs]
    contract_payload, contract_error = read_json_or_error(INDEXED_CACHE_CONTRACT)
    contract_body = {key: value for key, value in contract_payload.items() if key != "contract_sha256"}
    expected_evidence_manifest = saturation_evidence_manifest(expected_contract)
    evidence_manifest_payload, evidence_manifest_error = read_json_or_error(EVIDENCE_MANIFEST)
    evidence_manifest_body = {
        key: value for key, value in evidence_manifest_payload.items() if key != "manifest_sha256"
    }
    expected_job_plan = saturation_certificate_job_plan(expected_contract)
    job_plan_payload, job_plan_error = read_json_or_error(CERTIFICATE_JOB_PLAN)
    job_plan_body = {key: value for key, value in job_plan_payload.items() if key != "job_plan_sha256"}
    job_plan_jobs = job_plan_payload.get("jobs", []) if isinstance(job_plan_payload.get("jobs"), list) else []
    expected_queue = saturation_certificate_queue(expected_contract)
    queue_payload, queue_error = read_json_or_error(CERTIFICATE_QUEUE)
    queue_body = {key: value for key, value in queue_payload.items() if key != "queue_sha256"}
    queue_jobs = queue_payload.get("jobs", []) if isinstance(queue_payload.get("jobs"), list) else []
    queue_policy = (
        queue_payload.get("queue_policy", {}) if isinstance(queue_payload.get("queue_policy"), dict) else {}
    )
    expected_queue_audit = saturation_queue_audit(
        expected_contract,
        queue_payload=queue_payload,
        queue_error=queue_error,
    )
    queue_audit_payload, queue_audit_error = read_json_or_error(CERTIFICATE_QUEUE_AUDIT)
    queue_audit_body = {
        key: value for key, value in queue_audit_payload.items() if key != "audit_sha256"
    }
    queue_audit_checks = (
        queue_audit_payload.get("checks", {})
        if isinstance(queue_audit_payload.get("checks"), dict)
        else {}
    )
    expected_source_audit = saturation_certificate_source_audit(expected_contract)
    source_audit_payload, source_audit_error = read_json_or_error(CERTIFICATE_SOURCE_AUDIT)
    source_audit_body = {
        key: value for key, value in source_audit_payload.items() if key != "audit_sha256"
    }
    source_audit_checks = (
        source_audit_payload.get("checks", {})
        if isinstance(source_audit_payload.get("checks"), dict)
        else {}
    )
    source_audit_counts = (
        source_audit_payload.get("counts", {})
        if isinstance(source_audit_payload.get("counts"), dict)
        else {}
    )
    expected_intake_protocol = saturation_certificate_intake_protocol(expected_contract)
    intake_protocol_payload, intake_protocol_error = read_json_or_error(CERTIFICATE_INTAKE_PROTOCOL)
    intake_protocol_body = {
        key: value for key, value in intake_protocol_payload.items() if key != "protocol_sha256"
    }
    intake_protocol_checks = (
        intake_protocol_payload.get("checks", {})
        if isinstance(intake_protocol_payload.get("checks"), dict)
        else {}
    )
    intake_transitions = (
        intake_protocol_payload.get("transitions", [])
        if isinstance(intake_protocol_payload.get("transitions"), list)
        else []
    )
    expected_closure_checklist = saturation_closure_checklist(expected_contract)
    closure_checklist_payload, closure_checklist_error = read_json_or_error(CERTIFICATE_CLOSURE_CHECKLIST)
    closure_checklist_body = {
        key: value for key, value in closure_checklist_payload.items() if key != "checklist_sha256"
    }
    closure_checklist_checks = (
        closure_checklist_payload.get("checks", {})
        if isinstance(closure_checklist_payload.get("checks"), dict)
        else {}
    )
    closure_levels = (
        closure_checklist_payload.get("levels", {})
        if isinstance(closure_checklist_payload.get("levels"), dict)
        else {}
    )
    expected_status_summary = saturation_status_summary(expected_contract)
    status_summary_payload, status_summary_error = read_json_or_error(CERTIFICATE_STATUS_SUMMARY)
    status_summary_body = {
        key: value for key, value in status_summary_payload.items() if key != "status_summary_sha256"
    }
    status_summary_checks = (
        status_summary_payload.get("checks", {})
        if isinstance(status_summary_payload.get("checks"), dict)
        else {}
    )
    status_summary_counts = (
        status_summary_payload.get("counts", {})
        if isinstance(status_summary_payload.get("counts"), dict)
        else {}
    )
    single_job_lookup = (
        job_plan_payload.get("single_job_lookup", {})
        if isinstance(job_plan_payload.get("single_job_lookup"), dict)
        else {}
    )
    single_job_producer = (
        job_plan_payload.get("single_job_producer", {})
        if isinstance(job_plan_payload.get("single_job_producer"), dict)
        else {}
    )
    single_job_verification = (
        job_plan_payload.get("single_job_verification", {})
        if isinstance(job_plan_payload.get("single_job_verification"), dict)
        else {}
    )
    batch_job_status = (
        job_plan_payload.get("batch_job_status", {})
        if isinstance(job_plan_payload.get("batch_job_status"), dict)
        else {}
    )
    checks = {
        "expected_certificate_count_is_48": len(specs) == 48,
        "input_hashes_are_unique": len(set(input_hashes)) == len(input_hashes),
        "contract_manifest_written": INDEXED_CACHE_CONTRACT.exists(),
        "contract_manifest_json_valid": contract_error is None,
        "contract_payload_matches_current_specs": contract_payload == expected_contract,
        "contract_hash_matches_payload": contract_payload.get("contract_sha256") == sha_json(contract_body),
        "certificate_job_plan_written": CERTIFICATE_JOB_PLAN.exists(),
        "certificate_job_plan_json_valid": job_plan_error is None,
        "certificate_job_plan_matches_current_contract": job_plan_payload == expected_job_plan,
        "certificate_job_plan_hash_matches_payload": job_plan_payload.get("job_plan_sha256")
        == sha_json(job_plan_body),
        "certificate_job_plan_declares_single_job_lookup": bool(single_job_lookup.get("command")),
        "certificate_job_plan_lookup_is_non_running": single_job_lookup.get("runs_expensive_computation") is False,
        "certificate_jobs_have_lookup_commands": len(job_plan_jobs) == 48
        and all(isinstance(job, dict) and bool(job.get("lookup_command")) for job in job_plan_jobs),
        "certificate_job_plan_declares_single_job_producer": bool(single_job_producer.get("command")),
        "certificate_job_plan_producer_is_plan_only_by_default": single_job_producer.get(
            "runs_expensive_computation_by_default"
        )
        is False,
        "certificate_job_plan_producer_has_explicit_run_flag": single_job_producer.get("explicit_run_flag")
        == "--run-saturation-job",
        "certificate_jobs_have_produce_plan_commands": len(job_plan_jobs) == 48
        and all(isinstance(job, dict) and bool(job.get("produce_plan_command")) for job in job_plan_jobs),
        "certificate_job_plan_declares_single_job_verification": bool(single_job_verification.get("command")),
        "certificate_job_plan_verification_is_non_running": single_job_verification.get(
            "runs_expensive_computation"
        )
        is False,
        "certificate_job_plan_verifies_existing_cache_only": single_job_verification.get(
            "validates_existing_cache_only"
        )
        is True,
        "certificate_jobs_have_verify_commands": len(job_plan_jobs) == 48
        and all(isinstance(job, dict) and bool(job.get("verify_command")) for job in job_plan_jobs),
        "certificate_queue_written": CERTIFICATE_QUEUE.exists(),
        "certificate_queue_json_valid": queue_error is None,
        "certificate_queue_matches_current_status": queue_payload == expected_queue,
        "certificate_queue_hash_matches_payload": queue_payload.get("queue_sha256") == sha_json(queue_body),
        "certificate_queue_is_non_running": queue_payload.get("runs_expensive_computation") is False,
        "certificate_queue_has_48_jobs": len(queue_jobs) == 48,
        "certificate_queue_declares_next_job": isinstance(queue_payload.get("next_job"), dict)
        or queue_payload.get("status") == "READY_FOR_STRICT_CACHE",
        "certificate_queue_requires_explicit_run_flag": queue_policy.get("run_requires_explicit_flag")
        == "--run-saturation-job",
        "certificate_queue_jobs_have_plan_run_verify_commands": len(queue_jobs) == 48
        and all(
            isinstance(job, dict)
            and bool(job.get("plan_command"))
            and bool(job.get("run_command"))
            and bool(job.get("verify_command"))
            for job in queue_jobs
        ),
        "certificate_queue_audit_written": CERTIFICATE_QUEUE_AUDIT.exists(),
        "certificate_queue_audit_json_valid": queue_audit_error is None,
        "certificate_queue_audit_matches_current_queue": queue_audit_payload == expected_queue_audit,
        "certificate_queue_audit_hash_matches_payload": queue_audit_payload.get("audit_sha256")
        == sha_json(queue_audit_body),
        "certificate_queue_audit_passes": queue_audit_payload.get("status") == "PASS",
        "certificate_queue_audit_is_non_running": queue_audit_payload.get("runs_expensive_computation")
        is False,
        "certificate_queue_audit_checks_monotonicity": queue_audit_checks.get("queue_positions_are_contiguous")
        is True
        and queue_audit_checks.get("job_ids_are_contiguous") is True,
        "certificate_queue_audit_checks_command_guards": queue_audit_checks.get("plan_commands_are_plan_only")
        is True
        and queue_audit_checks.get("run_commands_are_explicitly_guarded") is True
        and queue_audit_checks.get("verify_commands_are_non_producing") is True,
        "certificate_source_audit_written": CERTIFICATE_SOURCE_AUDIT.exists(),
        "certificate_source_audit_json_valid": source_audit_error is None,
        "certificate_source_audit_matches_current_sources": source_audit_payload == expected_source_audit,
        "certificate_source_audit_hash_matches_payload": source_audit_payload.get("audit_sha256")
        == sha_json(source_audit_body),
        "certificate_source_audit_passes": source_audit_payload.get("status") == "PASS",
        "certificate_source_audit_is_non_running": source_audit_payload.get("runs_expensive_computation")
        is False,
        "certificate_source_audit_distinguishes_sources": source_audit_checks.get(
            "staging_promotion_distinguished_from_missing"
        )
        is True
        and source_audit_checks.get("source_paths_are_distinct") is True,
        "certificate_source_audit_counts_cover_jobs": source_audit_checks.get("counts_partition_jobs")
        is True
        and source_audit_counts.get("produce_needed", 0)
        + source_audit_counts.get("promotion_ready", 0)
        + source_audit_counts.get("invalid_present", 0)
        + source_audit_counts.get("stable_verified", 0)
        == 48,
        "certificate_source_audit_checks_safe_commands": source_audit_checks.get("plan_commands_are_non_running")
        is True
        and source_audit_checks.get("run_commands_are_guarded") is True
        and source_audit_checks.get("verify_commands_are_non_producing") is True
        and source_audit_checks.get("promotion_command_is_non_recomputing") is True,
        "certificate_intake_protocol_written": CERTIFICATE_INTAKE_PROTOCOL.exists(),
        "certificate_intake_protocol_json_valid": intake_protocol_error is None,
        "certificate_intake_protocol_matches_current_artifacts": intake_protocol_payload
        == expected_intake_protocol,
        "certificate_intake_protocol_hash_matches_payload": intake_protocol_payload.get("protocol_sha256")
        == sha_json(intake_protocol_body),
        "certificate_intake_protocol_passes": intake_protocol_payload.get("status") == "PASS",
        "certificate_intake_protocol_is_non_running": intake_protocol_payload.get("runs_expensive_computation")
        is False,
        "certificate_intake_protocol_declares_run_guard": intake_protocol_checks.get(
            "single_job_run_requires_explicit_flag"
        )
        is True
        and intake_protocol_checks.get("single_job_run_writes_stable_cache") is True,
        "certificate_intake_protocol_declares_staging_promotion": intake_protocol_checks.get(
            "staging_promotion_path_declared"
        )
        is True
        and any(
            isinstance(transition, dict)
            and transition.get("name") == "verified_staging_source_to_stable_candidate"
            for transition in intake_transitions
        ),
        "certificate_intake_protocol_declares_strict_gate": intake_protocol_checks.get(
            "strict_cache_requires_48_verified"
        )
        is True
        and any(
            isinstance(transition, dict)
            and transition.get("name") == "verified_jobs_to_strict_cache"
            for transition in intake_transitions
        ),
        "certificate_intake_protocol_non_running_commands_are_safe": intake_protocol_checks.get(
            "non_running_commands_are_guarded"
        )
        is True,
        "certificate_closure_checklist_written": CERTIFICATE_CLOSURE_CHECKLIST.exists(),
        "certificate_closure_checklist_json_valid": closure_checklist_error is None,
        "certificate_closure_checklist_matches_current_artifacts": closure_checklist_payload
        == expected_closure_checklist,
        "certificate_closure_checklist_hash_matches_payload": closure_checklist_payload.get("checklist_sha256")
        == sha_json(closure_checklist_body),
        "certificate_closure_checklist_passes": closure_checklist_payload.get("status") == "PASS",
        "certificate_closure_checklist_is_non_running": closure_checklist_payload.get("runs_expensive_computation")
        is False,
        "certificate_closure_checklist_declares_three_levels": {
            "provisional_integrated",
            "intake_ready",
            "strict_certified",
        }.issubset(set(closure_levels)),
        "certificate_closure_checklist_lists_required_verifiers": closure_checklist_checks.get(
            "provisional_lists_contract_and_index"
        )
        is True
        and closure_checklist_checks.get("intake_ready_lists_focused_intake_verifier") is True
        and closure_checklist_checks.get("strict_certified_lists_strict_cache_verifier") is True,
        "certificate_status_summary_written": CERTIFICATE_STATUS_SUMMARY.exists(),
        "certificate_status_summary_json_valid": status_summary_error is None,
        "certificate_status_summary_matches_current_status": status_summary_payload
        == expected_status_summary,
        "certificate_status_summary_hash_matches_payload": status_summary_payload.get(
            "status_summary_sha256"
        )
        == sha_json(status_summary_body),
        "certificate_status_summary_passes": status_summary_payload.get("status") == "PASS",
        "certificate_status_summary_is_non_running": status_summary_payload.get(
            "runs_expensive_computation"
        )
        is False,
        "certificate_status_summary_declares_gates": status_summary_payload.get("recommended_verifier")
        == "python src/verify.py jacobian-cubic-nonstrict --pretty"
        and status_summary_payload.get("strict_verifier")
        == "python src/verify.py jacobian-cubic-cache --pretty",
        "certificate_status_summary_counts_cover_jobs": status_summary_checks.get(
            "counts_cover_48_jobs"
        )
        is True
        and status_summary_counts.get("stable_verified", 0)
        + status_summary_counts.get("promotion_ready", 0)
        + status_summary_counts.get("invalid_present", 0)
        + status_summary_counts.get("produce_needed", 0)
        == 48,
        "certificate_job_plan_declares_batch_status": bool(batch_job_status.get("command")),
        "certificate_job_plan_declares_batch_status_summary": bool(batch_job_status.get("summary_command")),
        "certificate_job_plan_batch_status_is_non_running": batch_job_status.get("runs_expensive_computation")
        is False,
        "certificate_job_plan_batch_status_uses_existing_cache_only": batch_job_status.get(
            "validates_existing_cache_only"
        )
        is True,
        "evidence_manifest_written": EVIDENCE_MANIFEST.exists(),
        "evidence_manifest_json_valid": evidence_manifest_error is None,
        "evidence_manifest_matches_current_contract": evidence_manifest_payload == expected_evidence_manifest,
        "evidence_manifest_hash_matches_payload": evidence_manifest_payload.get("manifest_sha256")
        == sha_json(evidence_manifest_body),
        "evidence_readme_written": EVIDENCE_README.exists(),
    }
    result = {
        "schema": "d20.verification.jacobian_cubic_saturation_cache_contract",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "contract_manifest": str(INDEXED_CACHE_CONTRACT.relative_to(ROOT).as_posix()),
        "contract_manifest_error": contract_error,
        "contract_sha256": expected_contract.get("contract_sha256"),
        "certificate_job_plan": str(CERTIFICATE_JOB_PLAN.relative_to(ROOT).as_posix()),
        "certificate_job_plan_error": job_plan_error,
        "certificate_job_plan_sha256": expected_job_plan.get("job_plan_sha256"),
        "certificate_queue": str(CERTIFICATE_QUEUE.relative_to(ROOT).as_posix()),
        "certificate_queue_error": queue_error,
        "certificate_queue_sha256": expected_queue.get("queue_sha256"),
        "certificate_queue_audit": str(CERTIFICATE_QUEUE_AUDIT.relative_to(ROOT).as_posix()),
        "certificate_queue_audit_error": queue_audit_error,
        "certificate_queue_audit_sha256": expected_queue_audit.get("audit_sha256"),
        "certificate_source_audit": str(CERTIFICATE_SOURCE_AUDIT.relative_to(ROOT).as_posix()),
        "certificate_source_audit_error": source_audit_error,
        "certificate_source_audit_sha256": expected_source_audit.get("audit_sha256"),
        "certificate_intake_protocol": str(CERTIFICATE_INTAKE_PROTOCOL.relative_to(ROOT).as_posix()),
        "certificate_intake_protocol_error": intake_protocol_error,
        "certificate_intake_protocol_sha256": expected_intake_protocol.get("protocol_sha256"),
        "certificate_closure_checklist": str(CERTIFICATE_CLOSURE_CHECKLIST.relative_to(ROOT).as_posix()),
        "certificate_closure_checklist_error": closure_checklist_error,
        "certificate_closure_checklist_sha256": expected_closure_checklist.get("checklist_sha256"),
        "certificate_status_summary": str(CERTIFICATE_STATUS_SUMMARY.relative_to(ROOT).as_posix()),
        "certificate_status_summary_error": status_summary_error,
        "certificate_status_summary_sha256": expected_status_summary.get("status_summary_sha256"),
        "evidence_manifest": str(EVIDENCE_MANIFEST.relative_to(ROOT).as_posix()),
        "evidence_manifest_error": evidence_manifest_error,
        "evidence_manifest_sha256": expected_evidence_manifest.get("manifest_sha256"),
        "evidence_readme": str(EVIDENCE_README.relative_to(ROOT).as_posix()),
        "expected_certificate_count": len(specs),
    }
    return finish(result, pretty)


def jacobian_cubic_intake(*, pretty: bool) -> int:
    from src.certify_jacobian_cubic_symbolic_elimination_attempt import (
        CERTIFICATE_INTAKE_PROTOCOL,
        CERTIFICATE_QUEUE,
        CERTIFICATE_SOURCE_AUDIT,
        expected_saturation_cache_specs,
        saturation_cache_contract,
        saturation_certificate_intake_protocol,
        sha_json,
    )

    specs = expected_saturation_cache_specs()
    expected_contract = saturation_cache_contract(specs)
    expected_protocol = saturation_certificate_intake_protocol(expected_contract)
    protocol_payload, protocol_error = read_json_or_error(CERTIFICATE_INTAKE_PROTOCOL)
    protocol_body = {
        key: value for key, value in protocol_payload.items() if key != "protocol_sha256"
    }
    commands = protocol_payload.get("commands", {}) if isinstance(protocol_payload.get("commands"), dict) else {}
    checks_payload = (
        protocol_payload.get("checks", {}) if isinstance(protocol_payload.get("checks"), dict) else {}
    )
    transitions = (
        protocol_payload.get("transitions", []) if isinstance(protocol_payload.get("transitions"), list) else []
    )
    transition_names = {
        transition.get("name")
        for transition in transitions
        if isinstance(transition, dict)
    }
    required_transition_names = {
        "declared_to_planned",
        "planned_to_stable_candidate",
        "staging_candidate_to_verified_source",
        "verified_staging_source_to_stable_candidate",
        "stable_candidate_to_verified_job",
        "verified_jobs_to_strict_cache",
    }
    required_command_names = {
        "inspect_job",
        "plan_job",
        "run_one_job",
        "verify_job",
        "audit_sources",
        "promote_staging",
        "strict_cache",
    }
    non_running_command_names = required_command_names - {"run_one_job"}
    non_running_commands = [str(commands.get(name, "")) for name in non_running_command_names]
    run_command = str(commands.get("run_one_job", ""))
    strict_transition = next(
        (
            transition
            for transition in transitions
            if isinstance(transition, dict) and transition.get("name") == "verified_jobs_to_strict_cache"
        ),
        {},
    )
    staging_transition = next(
        (
            transition
            for transition in transitions
            if isinstance(transition, dict)
            and transition.get("name") == "verified_staging_source_to_stable_candidate"
        ),
        {},
    )
    artifacts = protocol_payload.get("artifacts", {}) if isinstance(protocol_payload.get("artifacts"), dict) else {}
    current_state = (
        protocol_payload.get("current_state", {})
        if isinstance(protocol_payload.get("current_state"), dict)
        else {}
    )
    source_counts = (
        current_state.get("source_counts", {}) if isinstance(current_state.get("source_counts"), dict) else {}
    )
    checks = {
        "expected_certificate_count_is_48": len(specs) == 48,
        "protocol_written": CERTIFICATE_INTAKE_PROTOCOL.exists(),
        "protocol_json_valid": protocol_error is None,
        "protocol_matches_current_artifacts": protocol_payload == expected_protocol,
        "protocol_hash_matches_payload": protocol_payload.get("protocol_sha256") == sha_json(protocol_body),
        "protocol_status_passes": protocol_payload.get("status") == "PASS",
        "protocol_is_non_running": protocol_payload.get("runs_expensive_computation") is False,
        "declares_required_commands": required_command_names.issubset(set(commands)),
        "non_running_commands_are_guarded": all(
            "--run-saturation-job" not in command and "--recompute-saturations" not in command
            for command in non_running_commands
        ),
        "run_command_requires_explicit_flag": "--run-saturation-job" in run_command
        and "--recompute-saturations" not in run_command,
        "declares_required_transitions": required_transition_names.issubset(transition_names),
        "staging_promotion_transition_points_to_expected_paths": staging_transition.get("from_directory")
        == "data/evidence/jacobian_cubic_symbolic_elimination/saturation_staging_cache"
        and staging_transition.get("to_directory")
        == "data/evidence/jacobian_cubic_symbolic_elimination/saturation_cache",
        "strict_transition_requires_48_verified": strict_transition.get("requires", {}).get(
            "verified_certificate_count"
        )
        == 48,
        "artifact_dependencies_exist": CERTIFICATE_QUEUE.exists()
        and CERTIFICATE_SOURCE_AUDIT.exists()
        and artifacts.get("stable_cache_directory")
        == "data/evidence/jacobian_cubic_symbolic_elimination/saturation_cache"
        and artifacts.get("staging_source_directory")
        == "data/evidence/jacobian_cubic_symbolic_elimination/saturation_staging_cache",
        "current_state_counts_cover_jobs": source_counts.get("stable_verified", 0)
        + source_counts.get("promotion_ready", 0)
        + source_counts.get("invalid_present", 0)
        + source_counts.get("produce_needed", 0)
        == 48,
        "embedded_checks_pass": all(checks_payload.values()) if checks_payload else False,
    }
    result = {
        "schema": "d20.verification.jacobian_cubic_intake_protocol",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "certificate_intake_protocol": str(CERTIFICATE_INTAKE_PROTOCOL.relative_to(ROOT).as_posix()),
        "certificate_intake_protocol_error": protocol_error,
        "certificate_intake_protocol_sha256": expected_protocol.get("protocol_sha256"),
        "certificate_queue": str(CERTIFICATE_QUEUE.relative_to(ROOT).as_posix()),
        "certificate_source_audit": str(CERTIFICATE_SOURCE_AUDIT.relative_to(ROOT).as_posix()),
        "current_state": current_state,
        "transition_names": sorted(name for name in transition_names if isinstance(name, str)),
    }
    return finish(result, pretty)


def jacobian_cubic_closure(*, pretty: bool) -> int:
    from src.certify_jacobian_cubic_symbolic_elimination_attempt import (
        CERTIFICATE_CLOSURE_CHECKLIST,
        CERTIFICATE_INTAKE_PROTOCOL,
        CERTIFICATE_SOURCE_AUDIT,
        expected_saturation_cache_specs,
        saturation_cache_contract,
        saturation_closure_checklist,
        sha_json,
    )

    specs = expected_saturation_cache_specs()
    expected_contract = saturation_cache_contract(specs)
    expected_checklist = saturation_closure_checklist(expected_contract)
    checklist_payload, checklist_error = read_json_or_error(CERTIFICATE_CLOSURE_CHECKLIST)
    checklist_body = {
        key: value for key, value in checklist_payload.items() if key != "checklist_sha256"
    }
    checks_payload = (
        checklist_payload.get("checks", {}) if isinstance(checklist_payload.get("checks"), dict) else {}
    )
    levels = checklist_payload.get("levels", {}) if isinstance(checklist_payload.get("levels"), dict) else {}
    current_state = (
        checklist_payload.get("current_state", {})
        if isinstance(checklist_payload.get("current_state"), dict)
        else {}
    )
    source_counts = (
        current_state.get("source_counts", {}) if isinstance(current_state.get("source_counts"), dict) else {}
    )
    provisional = levels.get("provisional_integrated", {}) if isinstance(levels.get("provisional_integrated"), dict) else {}
    intake_ready = levels.get("intake_ready", {}) if isinstance(levels.get("intake_ready"), dict) else {}
    strict_certified = levels.get("strict_certified", {}) if isinstance(levels.get("strict_certified"), dict) else {}
    provisional_verifiers = (
        provisional.get("required_verifiers", []) if isinstance(provisional.get("required_verifiers"), list) else []
    )
    intake_verifiers = (
        intake_ready.get("required_verifiers", []) if isinstance(intake_ready.get("required_verifiers"), list) else []
    )
    strict_verifiers = (
        strict_certified.get("required_verifiers", [])
        if isinstance(strict_certified.get("required_verifiers"), list)
        else []
    )
    checks = {
        "expected_certificate_count_is_48": len(specs) == 48,
        "checklist_written": CERTIFICATE_CLOSURE_CHECKLIST.exists(),
        "checklist_json_valid": checklist_error is None,
        "checklist_matches_current_artifacts": checklist_payload == expected_checklist,
        "checklist_hash_matches_payload": checklist_payload.get("checklist_sha256") == sha_json(checklist_body),
        "checklist_status_passes": checklist_payload.get("status") == "PASS",
        "checklist_is_non_running": checklist_payload.get("runs_expensive_computation") is False,
        "declares_three_closure_levels": {
            "provisional_integrated",
            "intake_ready",
            "strict_certified",
        }.issubset(set(levels)),
        "provisional_level_lists_contract_and_index": {
            "python src/verify.py jacobian-cubic-contract --pretty",
            "python src/verify.py evidence-index --pretty",
        }.issubset(set(provisional_verifiers)),
        "intake_ready_level_lists_intake_and_status": {
            "python src/verify.py jacobian-cubic-intake --pretty",
            "python src/certify_jacobian_cubic_symbolic_elimination_attempt.py --saturation-job-status-summary",
        }.issubset(set(intake_verifiers)),
        "strict_level_lists_strict_cache": "python src/verify.py jacobian-cubic-cache --pretty"
        in strict_verifiers,
        "current_counts_cover_48_jobs": source_counts.get("stable_verified", 0)
        + source_counts.get("promotion_ready", 0)
        + source_counts.get("invalid_present", 0)
        + source_counts.get("produce_needed", 0)
        == 48,
        "current_missing_is_explicit": source_counts.get("missing_both", 0)
        == source_counts.get("produce_needed", 0),
        "strict_level_requires_48_stable_verified": strict_certified.get("required_state", {}).get(
            "stable_verified"
        )
        == 48,
        "artifact_dependencies_exist": CERTIFICATE_INTAKE_PROTOCOL.exists() and CERTIFICATE_SOURCE_AUDIT.exists(),
        "embedded_checks_pass": all(checks_payload.values()) if checks_payload else False,
    }
    result = {
        "schema": "d20.verification.jacobian_cubic_closure_checklist",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "certificate_closure_checklist": str(CERTIFICATE_CLOSURE_CHECKLIST.relative_to(ROOT).as_posix()),
        "certificate_closure_checklist_error": checklist_error,
        "certificate_closure_checklist_sha256": expected_checklist.get("checklist_sha256"),
        "current_level": checklist_payload.get("current_level"),
        "current_state": current_state,
        "levels": sorted(level for level in levels if isinstance(level, str)),
    }
    return finish(result, pretty)


def jacobian_cubic_status(*, pretty: bool) -> int:
    from src.certify_jacobian_cubic_symbolic_elimination_attempt import (
        CERTIFICATE_CLOSURE_CHECKLIST,
        CERTIFICATE_STATUS_SUMMARY,
        expected_saturation_cache_specs,
        saturation_cache_contract,
        saturation_closure_checklist,
        saturation_status_summary,
        sha_json,
    )

    specs = expected_saturation_cache_specs()
    expected_contract = saturation_cache_contract(specs)
    expected_checklist = saturation_closure_checklist(expected_contract)
    checklist_payload, checklist_error = read_json_or_error(CERTIFICATE_CLOSURE_CHECKLIST)
    checklist_body = {
        key: value for key, value in checklist_payload.items() if key != "checklist_sha256"
    }
    expected_summary = saturation_status_summary(expected_contract)
    summary_payload, summary_error = read_json_or_error(CERTIFICATE_STATUS_SUMMARY)
    summary_body = {
        key: value for key, value in summary_payload.items() if key != "status_summary_sha256"
    }
    current_state = (
        checklist_payload.get("current_state", {})
        if isinstance(checklist_payload.get("current_state"), dict)
        else {}
    )
    source_counts = (
        current_state.get("source_counts", {}) if isinstance(current_state.get("source_counts"), dict) else {}
    )
    summary_counts = (
        summary_payload.get("counts", {}) if isinstance(summary_payload.get("counts"), dict) else {}
    )
    next_job = summary_payload.get("next_job") if isinstance(summary_payload.get("next_job"), dict) else None
    stable_verified = int(summary_counts.get("stable_verified", 0))
    promotion_ready = int(summary_counts.get("promotion_ready", 0))
    invalid_present = int(summary_counts.get("invalid_present", 0))
    produce_needed = int(summary_counts.get("produce_needed", 0))
    staging_present = int(summary_counts.get("staging_present", 0))
    stable_present = int(summary_counts.get("stable_present", 0))
    current_level = summary_payload.get("current_level")
    is_strict_counts = (
        stable_verified == 48
        and promotion_ready == 0
        and invalid_present == 0
        and produce_needed == 0
    )
    checks = {
        "expected_certificate_count_is_48": len(specs) == 48,
        "checklist_written": CERTIFICATE_CLOSURE_CHECKLIST.exists(),
        "checklist_json_valid": checklist_error is None,
        "checklist_matches_current_artifacts": checklist_payload == expected_checklist,
        "checklist_hash_matches_payload": checklist_payload.get("checklist_sha256") == sha_json(checklist_body),
        "checklist_status_passes": checklist_payload.get("status") == "PASS",
        "status_summary_written": CERTIFICATE_STATUS_SUMMARY.exists(),
        "status_summary_json_valid": summary_error is None,
        "status_summary_matches_current_status": summary_payload == expected_summary,
        "status_summary_hash_matches_payload": summary_payload.get("status_summary_sha256")
        == sha_json(summary_body),
        "status_summary_status_passes": summary_payload.get("status") == "PASS",
        "status_summary_is_non_running": summary_payload.get("runs_expensive_computation") is False,
        "current_level_known": current_level
        in {"provisional_integrated", "intake_ready", "strict_certified"},
        "summary_level_matches_checklist": current_level == checklist_payload.get("current_level"),
        "summary_counts_match_checklist": summary_counts == {
            "stable_present": int(source_counts.get("stable_present", 0)),
            "staging_present": int(source_counts.get("staging_present", 0)),
            "stable_verified": int(source_counts.get("stable_verified", 0)),
            "promotion_ready": int(source_counts.get("promotion_ready", 0)),
            "invalid_present": int(source_counts.get("invalid_present", 0)),
            "produce_needed": int(source_counts.get("produce_needed", 0)),
            "missing_both": int(source_counts.get("missing_both", 0)),
        },
        "status_summary_declares_gates": summary_payload.get("recommended_verifier")
        == "python src/verify.py jacobian-cubic-nonstrict --pretty"
        and summary_payload.get("strict_verifier") == "python src/verify.py jacobian-cubic-cache --pretty",
        "counts_cover_48_jobs": stable_verified + promotion_ready + invalid_present + produce_needed == 48,
        "strict_level_matches_counts": (current_level == "strict_certified") == is_strict_counts,
        "non_strict_level_has_next_job": current_level == "strict_certified" or isinstance(next_job, dict),
    }
    result = {
        "schema": "d20.verification.jacobian_cubic_status",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "current_level": current_level,
        "counts": {
            "stable_present": stable_present,
            "staging_present": staging_present,
            "stable_verified": stable_verified,
            "promotion_ready": promotion_ready,
            "invalid_present": invalid_present,
            "produce_needed": produce_needed,
            "missing_both": int(source_counts.get("missing_both", 0)),
        },
        "next_job": (
            {
                "job_id": next_job.get("job_id"),
                "label": next_job.get("label"),
                "next_action": next_job.get("next_action"),
                "plan_command": next_job.get("plan_command"),
                "run_command": next_job.get("run_command"),
                "verify_command": next_job.get("verify_command"),
            }
            if isinstance(next_job, dict)
            else None
        ),
        "strict_cache_ready": is_strict_counts,
        "certificate_closure_checklist": str(CERTIFICATE_CLOSURE_CHECKLIST.relative_to(ROOT).as_posix()),
        "certificate_closure_checklist_error": checklist_error,
        "certificate_closure_checklist_sha256": expected_checklist.get("checklist_sha256"),
        "certificate_status_summary": str(CERTIFICATE_STATUS_SUMMARY.relative_to(ROOT).as_posix()),
        "certificate_status_summary_error": summary_error,
        "certificate_status_summary_sha256": expected_summary.get("status_summary_sha256"),
    }
    return finish(result, pretty)


def run_verify_subcommand(command: str) -> dict[str, Any]:
    commands = {
        "evidence-index": lambda: verify_evidence_index(pretty=False),
        "compiler-scene-selftest": lambda: compiler_scene_selftest(pretty=False),
        "compiler-a42-d20-replay": lambda: compiler_a42_d20_replay(pretty=False),
        "compiler-nonstrict": lambda: compiler_nonstrict(pretty=False),
        "integration-nonstrict": lambda: integration_nonstrict(pretty=False),
        "jacobian-cubic-status": lambda: jacobian_cubic_status(pretty=False),
        "jacobian-cubic-intake": lambda: jacobian_cubic_intake(pretty=False),
        "jacobian-cubic-closure": lambda: jacobian_cubic_closure(pretty=False),
        "jacobian-cubic-nonstrict": lambda: jacobian_cubic_nonstrict(pretty=False),
    }
    buffer = io.StringIO()
    if command not in commands:
        return {
            "command": f"python src/verify.py {command}",
            "exit_code": 1,
            "status": "FAIL",
            "payload": {
                "schema": "d20.verification.unknown_subcommand",
                "status": "FAIL",
                "error": f"unsupported non-strict subcommand: {command}",
            },
        }
    try:
        with contextlib.redirect_stdout(buffer):
            exit_code = commands[command]()
    except Exception as exc:
        return {
            "command": f"python src/verify.py {command}",
            "exit_code": 1,
            "status": "FAIL",
            "payload": {
                "schema": "d20.verification.subcommand_exception",
                "status": "FAIL",
                "error": f"{type(exc).__name__}: {exc}",
            },
        }
    stdout = buffer.getvalue()
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        payload = {
            "schema": "d20.verification.subcommand_unparseable",
            "status": "FAIL",
            "stdout": stdout,
        }
    return {
        "command": f"python src/verify.py {command}",
        "exit_code": exit_code,
        "status": payload.get("status"),
        "payload": payload,
    }


def compiler_nonstrict(*, pretty: bool) -> int:
    included_modes = [
        "compiler-scene-selftest",
        "compiler-a42-d20-replay",
        "evidence-index",
    ]
    excluded_modes = ["jacobian-cubic-cache", "rebuild", "strict-replay"]
    results = [run_verify_subcommand(command) for command in included_modes]
    by_command = {
        result["command"]: {
            "command": result["command"],
            "exit_code": result["exit_code"],
            "status": result["status"],
            "schema": result.get("payload", {}).get("schema"),
        }
        for result in results
    }
    scene_payload = next(
        (
            result.get("payload", {})
            for result in results
            if result["command"] == "python src/verify.py compiler-scene-selftest"
        ),
        {},
    )
    replay_payload = next(
        (
            result.get("payload", {})
            for result in results
            if result["command"] == "python src/verify.py compiler-a42-d20-replay"
        ),
        {},
    )
    evidence_payload = next(
        (
            result.get("payload", {})
            for result in results
            if result["command"] == "python src/verify.py evidence-index"
        ),
        {},
    )
    compiler_registry_checks = (
        evidence_payload.get("compiler_a42_d20_registry_checks", {})
        if isinstance(evidence_payload.get("compiler_a42_d20_registry_checks"), dict)
        else {}
    )
    checks = {
        "runs_only_declared_compiler_modes": [result["command"] for result in results]
        == [f"python src/verify.py {mode}" for mode in included_modes],
        "strict_and_expensive_modes_excluded": all(mode not in included_modes for mode in excluded_modes),
        "all_included_modes_pass": all(result["exit_code"] == 0 and result["status"] == "PASS" for result in results),
        "scene_selftest_promotes_claims": int(scene_payload.get("promoted_claim_count", 0)) > 0,
        "scene_selftest_has_no_pending_claims": int(scene_payload.get("pending_claim_count", 0)) == 0,
        "a42_d20_positive_replay_passes": replay_payload.get("positive", {}).get("verify_status")
        == "PASS_WITH_RESIDUE",
        "a42_d20_missing_coordinate_blocks": replay_payload.get("missing_coordinate", {}).get("verify_status")
        == "BLOCKED_WITH_RESIDUE",
        "a42_d20_tamper_fails": replay_payload.get("tampered_coordinate", {}).get(
            "tampered_verify_status"
        )
        == "FAIL",
        "evidence_index_has_compiler_replay_root": compiler_registry_checks.get(
            "evidence_index_has_compiler_a42_d20_root"
        )
        is True,
    }
    result = {
        "schema": "d20.verification.compiler_nonstrict",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "included_modes": included_modes,
        "excluded_modes": excluded_modes,
        "scene_summary": scene_payload.get("summary"),
        "a42_d20_replay": {
            "positive": replay_payload.get("positive"),
            "missing_coordinate": replay_payload.get("missing_coordinate"),
            "tampered_coordinate": replay_payload.get("tampered_coordinate"),
        },
        "results": by_command,
    }
    return finish(result, pretty)


def jacobian_cubic_nonstrict(*, pretty: bool) -> int:
    included_modes = [
        "evidence-index",
        "jacobian-cubic-status",
        "jacobian-cubic-intake",
        "jacobian-cubic-closure",
    ]
    excluded_modes = ["jacobian-cubic-cache"]
    results = [run_verify_subcommand(command) for command in included_modes]
    by_command = {
        result["command"]: {
            "command": result["command"],
            "exit_code": result["exit_code"],
            "status": result["status"],
            "schema": result.get("payload", {}).get("schema"),
        }
        for result in results
    }
    status_payload = next(
        (
            result.get("payload", {})
            for result in results
            if result["command"] == "python src/verify.py jacobian-cubic-status"
        ),
        {},
    )
    checks = {
        "runs_only_declared_non_strict_modes": [result["command"] for result in results]
        == [f"python src/verify.py {mode}" for mode in included_modes],
        "strict_cache_gate_excluded": "jacobian-cubic-cache" not in included_modes
        and excluded_modes == ["jacobian-cubic-cache"],
        "all_included_modes_pass": all(result["exit_code"] == 0 and result["status"] == "PASS" for result in results),
        "status_mode_reports_intake_ready_or_strict": status_payload.get("current_level")
        in {"intake_ready", "strict_certified"},
        "status_mode_reports_48_jobs": (
            status_payload.get("counts", {}).get("stable_verified", 0)
            + status_payload.get("counts", {}).get("promotion_ready", 0)
            + status_payload.get("counts", {}).get("invalid_present", 0)
            + status_payload.get("counts", {}).get("produce_needed", 0)
            == 48
        ),
        "strict_cache_not_ready_is_allowed": status_payload.get("strict_cache_ready") in {True, False},
    }
    result = {
        "schema": "d20.verification.jacobian_cubic_nonstrict",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "included_modes": included_modes,
        "excluded_modes": excluded_modes,
        "current_level": status_payload.get("current_level"),
        "strict_cache_ready": status_payload.get("strict_cache_ready"),
        "counts": status_payload.get("counts"),
        "next_job": status_payload.get("next_job"),
        "results": by_command,
    }
    return finish(result, pretty)


def integration_nonstrict(*, pretty: bool) -> int:
    included_modes = [
        "compiler-nonstrict",
        "jacobian-cubic-nonstrict",
    ]
    excluded_modes = ["jacobian-cubic-cache", "rebuild", "strict-replay"]
    results = [run_verify_subcommand(command) for command in included_modes]
    by_command = {
        result["command"]: {
            "command": result["command"],
            "exit_code": result["exit_code"],
            "status": result["status"],
            "schema": result.get("payload", {}).get("schema"),
        }
        for result in results
    }
    compiler_payload = next(
        (
            result.get("payload", {})
            for result in results
            if result["command"] == "python src/verify.py compiler-nonstrict"
        ),
        {},
    )
    cubic_payload = next(
        (
            result.get("payload", {})
            for result in results
            if result["command"] == "python src/verify.py jacobian-cubic-nonstrict"
        ),
        {},
    )
    checks = {
        "runs_only_declared_integration_modes": [result["command"] for result in results]
        == [f"python src/verify.py {mode}" for mode in included_modes],
        "strict_and_expensive_modes_excluded": all(mode not in included_modes for mode in excluded_modes),
        "all_included_modes_pass": all(result["exit_code"] == 0 and result["status"] == "PASS" for result in results),
        "compiler_gate_passes": compiler_payload.get("status") == "PASS",
        "cubic_gate_passes": cubic_payload.get("status") == "PASS",
        "cubic_reports_48_jobs": (
            cubic_payload.get("counts", {}).get("stable_verified", 0)
            + cubic_payload.get("counts", {}).get("promotion_ready", 0)
            + cubic_payload.get("counts", {}).get("invalid_present", 0)
            + cubic_payload.get("counts", {}).get("produce_needed", 0)
            == 48
        ),
        "strict_cache_not_claimed": cubic_payload.get("strict_cache_ready") in {True, False}
        and cubic_payload.get("current_level") in {"intake_ready", "strict_certified"},
    }
    result = {
        "schema": "d20.verification.integration_nonstrict",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "included_modes": included_modes,
        "excluded_modes": excluded_modes,
        "compiler": {
            "scene_summary": compiler_payload.get("scene_summary"),
            "a42_d20_replay": compiler_payload.get("a42_d20_replay"),
        },
        "cubic": {
            "current_level": cubic_payload.get("current_level"),
            "strict_cache_ready": cubic_payload.get("strict_cache_ready"),
            "counts": cubic_payload.get("counts"),
            "next_job": cubic_payload.get("next_job"),
        },
        "results": by_command,
    }
    return finish(result, pretty)


def c985_registry(*, pretty: bool) -> int:
    from src.certify_c985_typed_simple_object_registry import (
        validate_c985_typed_simple_object_registry,
    )

    try:
        result = validate_c985_typed_simple_object_registry()
    except Exception as exc:
        result = {
            "schema": "c985.verification.typed_simple_object_registry@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_fusion(*, pretty: bool) -> int:
    from src.certify_c985_fusion_multiplicity_typing import (
        validate_c985_fusion_multiplicity_typing,
    )

    try:
        result = validate_c985_fusion_multiplicity_typing()
    except Exception as exc:
        result = {
            "schema": "c985.verification.fusion_multiplicity_typing@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_associator(*, pretty: bool) -> int:
    from src.certify_c985_associator_rebracketing_oracle import (
        validate_c985_associator_rebracketing_oracle,
    )

    try:
        result = validate_c985_associator_rebracketing_oracle()
    except Exception as exc:
        result = {
            "schema": "c985.verification.associator_rebracketing_oracle@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_unit(*, pretty: bool) -> int:
    from src.certify_c985_unit_tensor_laws import validate_c985_unit_tensor_laws

    try:
        result = validate_c985_unit_tensor_laws()
    except Exception as exc:
        result = {
            "schema": "c985.verification.unit_tensor_laws@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_triangle(*, pretty: bool) -> int:
    from src.certify_c985_unit_triangle_coherence import (
        validate_c985_unit_triangle_coherence,
    )

    try:
        result = validate_c985_unit_triangle_coherence()
    except Exception as exc:
        result = {
            "schema": "c985.verification.unit_triangle_coherence@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_duality(*, pretty: bool) -> int:
    from src.certify_c985_duality_support import validate_c985_duality_support

    try:
        result = validate_c985_duality_support()
    except Exception as exc:
        result = {
            "schema": "c985.verification.duality_support@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_pentagon(*, pretty: bool) -> int:
    from src.certify_c985_pentagon_chain_normal_form import (
        validate_c985_pentagon_chain_normal_form,
    )

    try:
        result = validate_c985_pentagon_chain_normal_form()
    except Exception as exc:
        result = {
            "schema": "c985.verification.pentagon_chain_normal_form@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_zigzag(*, pretty: bool) -> int:
    from src.certify_c985_zigzag_identities import validate_c985_zigzag_identities

    try:
        result = validate_c985_zigzag_identities()
    except Exception as exc:
        result = {
            "schema": "c985.verification.zigzag_identities@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_final(*, pretty: bool) -> int:
    from src.certify_c985_final_multifusion_certificate import (
        validate_c985_final_multifusion_certificate,
    )

    try:
        result = validate_c985_final_multifusion_certificate()
    except Exception as exc:
        result = {
            "schema": "c985.verification.final_multifusion_certificate@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_geometry(*, pretty: bool) -> int:
    from src.certify_c985_tensor_geometry_invariants import (
        validate_c985_tensor_geometry_invariants,
    )

    try:
        result = validate_c985_tensor_geometry_invariants()
    except Exception as exc:
        result = {
            "schema": "c985.verification.tensor_geometry_invariants@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_d20_atlas(*, pretty: bool) -> int:
    from src.certify_c985_d20_boundary_invariant_atlas import (
        validate_c985_d20_boundary_invariant_atlas,
    )

    try:
        result = validate_c985_d20_boundary_invariant_atlas()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_boundary_invariant_atlas@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_hyperbolic_graph(*, pretty: bool) -> int:
    from src.certify_c985_d20_hyperbolic_boundary_graph import (
        validate_c985_d20_hyperbolic_boundary_graph,
    )

    try:
        result = validate_c985_d20_hyperbolic_boundary_graph()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_hyperbolic_boundary_graph@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_poincare(*, pretty: bool) -> int:
    from src.certify_c985_d20_poincare_embedding import (
        validate_c985_d20_poincare_embedding,
    )

    try:
        result = validate_c985_d20_poincare_embedding()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_poincare_embedding@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_filtration(*, pretty: bool) -> int:
    from src.certify_c985_d20_poincare_landmark_filtration import (
        validate_c985_d20_poincare_landmark_filtration,
    )

    try:
        result = validate_c985_d20_poincare_landmark_filtration()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_poincare_landmark_filtration@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_nerve(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_class_nerve import (
        validate_c985_d20_signature_class_nerve,
    )

    try:
        result = validate_c985_d20_signature_class_nerve()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_class_nerve@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_chart_atlas(*, pretty: bool) -> int:
    from src.certify_c985_d20_hyperbolic_chart_atlas import (
        validate_c985_d20_hyperbolic_chart_atlas,
    )

    try:
        result = validate_c985_d20_hyperbolic_chart_atlas()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_hyperbolic_chart_atlas@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_transition_groupoid(*, pretty: bool) -> int:
    from src.certify_c985_d20_transition_groupoid import (
        validate_c985_d20_transition_groupoid,
    )

    try:
        result = validate_c985_d20_transition_groupoid()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_transition_groupoid@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_normal_words(*, pretty: bool) -> int:
    from src.certify_c985_d20_normal_form_words import (
        validate_c985_d20_normal_form_words,
    )

    try:
        result = validate_c985_d20_normal_form_words()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_normal_form_words@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_symbolic_rewrites(*, pretty: bool) -> int:
    from src.certify_c985_d20_symbolic_rewrite_rules import (
        validate_c985_d20_symbolic_rewrite_rules,
    )

    try:
        result = validate_c985_d20_symbolic_rewrite_rules()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_symbolic_rewrite_rules@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_symbolic_associativity(*, pretty: bool) -> int:
    from src.certify_c985_d20_symbolic_associativity import (
        validate_c985_d20_symbolic_associativity,
    )

    try:
        result = validate_c985_d20_symbolic_associativity()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_symbolic_associativity@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_rewrite_complex(*, pretty: bool) -> int:
    from src.certify_c985_d20_rewrite_complex_hyperbolicity import (
        validate_c985_d20_rewrite_complex_hyperbolicity,
    )

    try:
        result = validate_c985_d20_rewrite_complex_hyperbolicity()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_rewrite_complex_hyperbolicity@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_interval_sheaf(*, pretty: bool) -> int:
    from src.certify_c985_d20_geodesic_interval_sheaf import (
        validate_c985_d20_geodesic_interval_sheaf,
    )

    try:
        result = validate_c985_d20_geodesic_interval_sheaf()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_geodesic_interval_sheaf@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_preserved_core(*, pretty: bool) -> int:
    from src.certify_c985_d20_preserved_core_subcomplex import (
        validate_c985_d20_preserved_core_subcomplex,
    )

    try:
        result = validate_c985_d20_preserved_core_subcomplex()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_preserved_core_subcomplex@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_chamber_spine(*, pretty: bool) -> int:
    from src.certify_c985_d20_chamber_spine import (
        validate_c985_d20_chamber_spine,
    )

    try:
        result = validate_c985_d20_chamber_spine()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_chamber_spine@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_morse_reeb(*, pretty: bool) -> int:
    from src.certify_c985_d20_morse_reeb_quotient import (
        validate_c985_d20_morse_reeb_quotient,
    )

    try:
        result = validate_c985_d20_morse_reeb_quotient()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_morse_reeb_quotient@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_boundary_transfer(*, pretty: bool) -> int:
    from src.certify_c985_d20_boundary_transfer_operator import (
        validate_c985_d20_boundary_transfer_operator,
    )

    try:
        result = validate_c985_d20_boundary_transfer_operator()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_boundary_transfer_operator@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_atom_flow(*, pretty: bool) -> int:
    from src.certify_c985_d20_stationary_atom_flow_lift import (
        validate_c985_d20_stationary_atom_flow_lift,
    )

    try:
        result = validate_c985_d20_stationary_atom_flow_lift()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_stationary_atom_flow_lift@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_subboundary(*, pretty: bool) -> int:
    from src.certify_c985_d20_recurrent_signature_subboundary import (
        validate_c985_d20_recurrent_signature_subboundary,
    )

    try:
        result = validate_c985_d20_recurrent_signature_subboundary()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_recurrent_signature_subboundary@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_transfer(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_subboundary_transfer_operator import (
        validate_c985_d20_signature_subboundary_transfer_operator,
    )

    try:
        result = validate_c985_d20_signature_subboundary_transfer_operator()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_subboundary_transfer_operator@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_spectral_cut(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_transfer_spectral_cut import (
        validate_c985_d20_signature_transfer_spectral_cut,
    )

    try:
        result = validate_c985_d20_signature_transfer_spectral_cut()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_transfer_spectral_cut@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_quotient(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_spectral_quotient_dynamics import (
        validate_c985_d20_signature_spectral_quotient_dynamics,
    )

    try:
        result = validate_c985_d20_signature_spectral_quotient_dynamics()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_spectral_quotient_dynamics@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_geometry(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_quotient_poincare_geometry import (
        validate_c985_d20_signature_quotient_poincare_geometry,
    )

    try:
        result = validate_c985_d20_signature_quotient_poincare_geometry()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_quotient_poincare_geometry@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_geodesic(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_geodesic_order import (
        validate_c985_d20_signature_geodesic_order,
    )

    try:
        result = validate_c985_d20_signature_geodesic_order()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_geodesic_order@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_residual_chart(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_geodesic_residual_chart import (
        validate_c985_d20_signature_geodesic_residual_chart,
    )

    try:
        result = validate_c985_d20_signature_geodesic_residual_chart()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_geodesic_residual_chart@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_cell_complex(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_residual_cell_complex import (
        validate_c985_d20_signature_residual_cell_complex,
    )

    try:
        result = validate_c985_d20_signature_residual_cell_complex()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_residual_cell_complex@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_boundary_flux(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_flux_cells import (
        validate_c985_d20_signature_boundary_flux_cells,
    )

    try:
        result = validate_c985_d20_signature_boundary_flux_cells()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_flux_cells@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_boundary_rates(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_flux_quotient_rates import (
        validate_c985_d20_signature_boundary_flux_quotient_rates,
    )

    try:
        result = validate_c985_d20_signature_boundary_flux_quotient_rates()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_flux_quotient_rates@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_conductance_spine(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_conductance_spine import (
        validate_c985_d20_signature_boundary_conductance_spine,
    )

    try:
        result = validate_c985_d20_signature_boundary_conductance_spine()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_conductance_spine@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_spine_poincare(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_poincare_path import (
        validate_c985_d20_signature_boundary_spine_poincare_path,
    )

    try:
        result = validate_c985_d20_signature_boundary_spine_poincare_path()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_poincare_path@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_routing_prefix(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_routing_prefix import (
        validate_c985_d20_signature_boundary_spine_routing_prefix,
    )

    try:
        result = validate_c985_d20_signature_boundary_spine_routing_prefix()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_routing_prefix@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_branching_law(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_branching_law import (
        validate_c985_d20_signature_boundary_spine_branching_law,
    )

    try:
        result = validate_c985_d20_signature_boundary_spine_branching_law()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_branching_law@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_typed_corridors(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_typed_corridors import (
        validate_c985_d20_signature_boundary_spine_typed_corridors,
    )

    try:
        result = validate_c985_d20_signature_boundary_spine_typed_corridors()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_typed_corridors@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_gate_automaton(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_gate_automaton import (
        validate_c985_d20_signature_boundary_spine_gate_automaton,
    )

    try:
        result = validate_c985_d20_signature_boundary_spine_gate_automaton()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_gate_automaton@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_language_graph(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_language_graph import (
        validate_c985_d20_signature_boundary_spine_language_graph,
    )

    try:
        result = validate_c985_d20_signature_boundary_spine_language_graph()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_language_graph@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_fan(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_geodesic_fan import (
        validate_c985_d20_signature_boundary_spine_aperture_geodesic_fan,
    )

    try:
        result = validate_c985_d20_signature_boundary_spine_aperture_geodesic_fan()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_geodesic_fan@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_insertion(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_corridor_insertion import (
        validate_c985_d20_signature_boundary_spine_aperture_corridor_insertion,
    )

    try:
        result = validate_c985_d20_signature_boundary_spine_aperture_corridor_insertion()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_corridor_insertion@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_x2_splice(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_x2_splice_obstruction import (
        validate_c985_d20_signature_boundary_spine_x2_splice_obstruction,
    )

    try:
        result = validate_c985_d20_signature_boundary_spine_x2_splice_obstruction()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_x2_splice_obstruction@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_x2_detour(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_x2_detour_fan import (
        validate_c985_d20_signature_boundary_spine_x2_detour_fan,
    )

    try:
        result = validate_c985_d20_signature_boundary_spine_x2_detour_fan()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_x2_detour_fan@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_x2_clean_detour(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_x2_clean_detour_choice import (
        validate_c985_d20_signature_boundary_spine_x2_clean_detour_choice,
    )

    try:
        result = validate_c985_d20_signature_boundary_spine_x2_clean_detour_choice()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_x2_clean_detour_choice@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_x2_x4_aperture(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_x2_x4_aperture_completion import (
        validate_c985_d20_signature_boundary_spine_x2_x4_aperture_completion,
    )

    try:
        result = validate_c985_d20_signature_boundary_spine_x2_x4_aperture_completion()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_x2_x4_aperture_completion@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_cycle(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_cycle_language import (
        validate_c985_d20_signature_boundary_spine_aperture_cycle_language,
    )

    try:
        result = validate_c985_d20_signature_boundary_spine_aperture_cycle_language()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_cycle_language@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_cycle_ranking(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_cycle_ranking import (
        validate_c985_d20_signature_boundary_spine_aperture_cycle_ranking,
    )

    try:
        result = validate_c985_d20_signature_boundary_spine_aperture_cycle_ranking()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_cycle_ranking@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_cycle_pareto(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_cycle_pareto_frontier import (
        validate_c985_d20_signature_boundary_spine_aperture_cycle_pareto_frontier,
    )

    try:
        result = validate_c985_d20_signature_boundary_spine_aperture_cycle_pareto_frontier()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_cycle_pareto_frontier@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_mixed_contact(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_mixed_contact_atoms import (
        validate_c985_d20_signature_boundary_spine_aperture_mixed_contact_atoms,
    )

    try:
        result = validate_c985_d20_signature_boundary_spine_aperture_mixed_contact_atoms()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_mixed_contact_atoms@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_atom_selector(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_atom_selector_refinement import (
        validate_c985_d20_signature_boundary_spine_aperture_atom_selector_refinement,
    )

    try:
        result = validate_c985_d20_signature_boundary_spine_aperture_atom_selector_refinement()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_atom_selector_refinement@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_atom_tradeoff(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_atom_selected_tradeoff import (
        validate_c985_d20_signature_boundary_spine_aperture_atom_selected_tradeoff,
    )

    try:
        result = validate_c985_d20_signature_boundary_spine_aperture_atom_selected_tradeoff()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_atom_selected_tradeoff@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_tail_hybrid(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_tail_hybrid_search import (
        validate_c985_d20_signature_boundary_spine_aperture_tail_hybrid_search,
    )

    try:
        result = validate_c985_d20_signature_boundary_spine_aperture_tail_hybrid_search()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_tail_hybrid_search@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_bounded_backtrack(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_bounded_backtrack_search import (
        validate_c985_d20_signature_boundary_spine_aperture_bounded_backtrack_search,
    )

    try:
        result = validate_c985_d20_signature_boundary_spine_aperture_bounded_backtrack_search()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_bounded_backtrack_search@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_symbol_state(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_symbol_state_obstruction import (
        validate_c985_d20_signature_boundary_spine_aperture_symbol_state_obstruction,
    )

    try:
        result = validate_c985_d20_signature_boundary_spine_aperture_symbol_state_obstruction()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_symbol_state_obstruction@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_overhead2_carrier(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_overhead2_carrier_realizability import (
        validate_c985_d20_signature_boundary_spine_aperture_overhead2_carrier_realizability,
    )

    try:
        result = validate_c985_d20_signature_boundary_spine_aperture_overhead2_carrier_realizability()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_overhead2_carrier_realizability@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_overhead2_repair(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_overhead2_edit_repair import (
        validate_c985_d20_signature_boundary_spine_aperture_overhead2_edit_repair,
    )

    try:
        result = validate_c985_d20_signature_boundary_spine_aperture_overhead2_edit_repair()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_overhead2_edit_repair@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_overhead2_tail(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure import (
        validate_c985_d20_signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure,
    )

    try:
        result = validate_c985_d20_signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_overhead2_cycle_rank(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking import (
        validate_c985_d20_signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking,
    )

    try:
        result = validate_c985_d20_signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_overhead3_trace_quotient(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_overhead3_trace_class_quotient import (
        validate_c985_d20_signature_boundary_spine_aperture_overhead3_trace_class_quotient,
    )

    try:
        result = validate_c985_d20_signature_boundary_spine_aperture_overhead3_trace_class_quotient()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_overhead3_trace_class_quotient@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_rank104_audit(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_rank104_branch_audit import (
        validate_c985_d20_signature_boundary_spine_aperture_rank104_branch_audit,
    )

    try:
        result = validate_c985_d20_signature_boundary_spine_aperture_rank104_branch_audit()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_rank104_branch_audit@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_overhead3_weak_promotion(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_overhead3_weak_promotion_audit import (
        validate_c985_d20_signature_boundary_spine_aperture_overhead3_weak_promotion_audit,
    )

    try:
        result = validate_c985_d20_signature_boundary_spine_aperture_overhead3_weak_promotion_audit()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_overhead3_weak_promotion_audit@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_overhead3_strongification_gap(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap import (
        validate_c985_d20_signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap,
    )

    try:
        result = validate_c985_d20_signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap()
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_rank104_strongification_geometry(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_rank104_strongification_branch_geometry import (
        validate_c985_d20_signature_boundary_spine_aperture_rank104_strongification_branch_geometry,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_rank104_strongification_branch_geometry()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_rank104_strongification_branch_geometry@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_cost3_strongification_ranking(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_cost3_strongification_geometry_ranking import (
        validate_c985_d20_signature_boundary_spine_aperture_cost3_strongification_geometry_ranking,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_cost3_strongification_geometry_ranking()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_cost3_strongification_geometry_ranking@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_outlier_geometry(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_rich_outlier_geometry import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_rich_outlier_geometry,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_rich_outlier_geometry()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_rich_outlier_geometry@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_endpoint_split(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_endpoint_split import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_endpoint_split,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_endpoint_split()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_endpoint_split@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_rewrite_lift(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_rewrite_node_lift import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_rewrite_node_lift,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_rewrite_node_lift()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_rewrite_node_lift@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_prefix_chord(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_prefix_chord_search import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_prefix_chord_search,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_prefix_chord_search()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_prefix_chord_search@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_carrier_splice(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_realization import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_realization,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_realization()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_realization@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_splice_optimality(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_lower_lift(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_partial_splitter(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_partial_splitter_search import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_partial_splitter_search,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_partial_splitter_search()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_partial_splitter_search@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_trim_neighborhood(
    *, pretty: bool
) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_clear_corridor(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_clear_corridor import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_clear_corridor,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_clear_corridor()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_clear_corridor@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_clear_corridor_level2(
    *, pretty: bool
) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_clear_corridor_level2 import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_clear_corridor_level2,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_clear_corridor_level2()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_clear_corridor_level2@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_gate_repair(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_gate_repair_search import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_gate_repair_search,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_gate_repair_search()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_gate_repair_search@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_boundary_bridge(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_boundary_bridge_search import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_boundary_bridge_search,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_boundary_bridge_search()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_boundary_bridge_search@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_virtual_graft(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_native_insertion(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_native_trace_insertion import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_native_trace_insertion,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_native_trace_insertion()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_native_trace_insertion@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_symbolic_window(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_skip_window_grammar(
    *, pretty: bool
) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_skip_window_grammar import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_skip_window_grammar,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_skip_window_grammar()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_skip_window_grammar@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_repaired_automaton(
    *, pretty: bool
) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_repaired_automaton import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_repaired_automaton,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_repaired_automaton()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_repaired_automaton@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_transfer(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_transfer_operator import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_transfer_operator,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_transfer_operator()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_transfer_operator@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_flow_window(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_flow_window_lift import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_flow_window_lift,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_flow_window_lift()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_flow_window_lift@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_promoted_window(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_promoted_window import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_promoted_window,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_promoted_window()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_promoted_window@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_promoted_transfer(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_promoted_transfer_operator import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_promoted_transfer_operator,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_promoted_transfer_operator()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_promoted_transfer_operator@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_second_window(*, pretty: bool) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_search import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_search,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_search()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_second_window_search@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_second_window_promotion(
    *,
    pretty: bool,
) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_promotion import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_promotion,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_promotion()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_second_window_promotion@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_second_window_transfer(
    *,
    pretty: bool,
) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_sixj_frame(
    *,
    pretty: bool,
) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_sixj_recoupling_pair(
    *,
    pretty: bool,
) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_sixj_recoupling_triple(
    *,
    pretty: bool,
) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_sixj_recoupling_closure(
    *,
    pretty: bool,
) -> int:
    from src.certify_c985_sixj_tetra_closure import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_tetrahedral_closure_obstruction,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_tetrahedral_closure_obstruction()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_tetrahedral_closure_obstruction@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_sixj_nonlocal_screen(
    *,
    pretty: bool,
) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_sixj_borromean_hypergraph(
    *,
    pretty: bool,
) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_borromean_hypergraph_screen import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_borromean_hypergraph_screen,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_borromean_hypergraph_screen()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_sixj_borromean_hypergraph_screen@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_sixj_conductance_preservation(
    *,
    pretty: bool,
) -> int:
    from src.certify_c985_sixj_conductance import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_conductance_decreasing_aperture_preservation,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_conductance_decreasing_aperture_preservation()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_sixj_conductance_decreasing_aperture_preservation@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_eta6_charge(
    *,
    pretty: bool,
) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_eta6_holonomy(
    *,
    pretty: bool,
) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_eta6_dini_torsion(
    *,
    pretty: bool,
) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_eta6_h4_precursor(
    *,
    pretty: bool,
) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_h4_precursor_lift import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_h4_precursor_lift,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_h4_precursor_lift()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_eta6_h4_precursor_lift@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_eta6_graham_throat(
    *,
    pretty: bool,
) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_graham_throat_screen import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_graham_throat_screen,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_graham_throat_screen()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_eta6_graham_throat_screen@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_eta6_aperture_polygon(
    *,
    pretty: bool,
) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_aperture_polygon_area import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_aperture_polygon_area,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_aperture_polygon_area()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_eta6_aperture_polygon_area@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_eta6_truncated_skeleton(
    *,
    pretty: bool,
) -> int:
    from src.certify_c985_eta6_truncated_skeleton import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_truncated_icosahedral_boundary_skeleton,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_truncated_icosahedral_boundary_skeleton()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_eta6_truncated_icosahedral_boundary_skeleton@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_eta6_hex_face_barycenter(
    *,
    pretty: bool,
) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_hex_face_barycenter_graham_screen import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_hex_face_barycenter_graham_screen,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_hex_face_barycenter_graham_screen()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_eta6_hex_face_barycenter_graham_screen@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_eta6_nonholonomic_aperture(
    *,
    pretty: bool,
) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_nonholonomic_aperture import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_nonholonomic_aperture,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_nonholonomic_aperture()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_eta6_nonholonomic_aperture@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_eta6_exterior_cone(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_ext_cone import (
        validate_eta6_ext_cone,
    )

    try:
        result = validate_eta6_ext_cone()
    except Exception as exc:
        result = {
            "schema": "eta6.ext_cone.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_gordan(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_gordan import validate_eta6_gordan

    try:
        result = validate_eta6_gordan()
    except Exception as exc:
        result = {
            "schema": "eta6.gordan.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_aext(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_aext import validate_eta6_aext

    try:
        result = validate_eta6_aext()
    except Exception as exc:
        result = {
            "schema": "eta6.aext.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_srows(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_srows import validate_eta6_srows

    try:
        result = validate_eta6_srows()
    except Exception as exc:
        result = {
            "schema": "eta6.srows.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_islack(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_islack import validate_eta6_islack

    try:
        result = validate_eta6_islack()
    except Exception as exc:
        result = {
            "schema": "eta6.islack.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_hpol(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_hpol import validate_eta6_hpol

    try:
        result = validate_eta6_hpol()
    except Exception as exc:
        result = {
            "schema": "eta6.hpol.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_surg(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_surg import validate_eta6_surg

    try:
        result = validate_eta6_surg()
    except Exception as exc:
        result = {
            "schema": "eta6.surg.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_repl(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_repl import validate_eta6_repl

    try:
        result = validate_eta6_repl()
    except Exception as exc:
        result = {
            "schema": "eta6.repl.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_xfer(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_xfer import validate_eta6_xfer

    try:
        result = validate_eta6_xfer()
    except Exception as exc:
        result = {
            "schema": "eta6.xfer.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_hit2(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_hit2 import validate_eta6_hit2

    try:
        result = validate_eta6_hit2()
    except Exception as exc:
        result = {
            "schema": "eta6.hit2.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_gap(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_gap import validate_eta6_gap

    try:
        result = validate_eta6_gap()
    except Exception as exc:
        result = {
            "schema": "eta6.gap.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p2(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p2 import validate_eta6_p2

    try:
        result = validate_eta6_p2()
    except Exception as exc:
        result = {
            "schema": "eta6.p2.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_t2(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_t2 import validate_eta6_t2

    try:
        result = validate_eta6_t2()
    except Exception as exc:
        result = {
            "schema": "eta6.t2.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_f4(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_f4 import validate_eta6_f4

    try:
        result = validate_eta6_f4()
    except Exception as exc:
        result = {
            "schema": "eta6.f4.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p5(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p5 import validate_eta6_p5

    try:
        result = validate_eta6_p5()
    except Exception as exc:
        result = {
            "schema": "eta6.p5.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p6(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p6 import validate_eta6_p6

    try:
        result = validate_eta6_p6()
    except Exception as exc:
        result = {
            "schema": "eta6.p6.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p7(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p7 import validate_eta6_p7

    try:
        result = validate_eta6_p7()
    except Exception as exc:
        result = {
            "schema": "eta6.p7.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p8(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p8 import validate_eta6_p8

    try:
        result = validate_eta6_p8()
    except Exception as exc:
        result = {
            "schema": "eta6.p8.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p9(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p9 import validate_eta6_p9

    try:
        result = validate_eta6_p9()
    except Exception as exc:
        result = {
            "schema": "eta6.p9.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p10(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p10 import validate_eta6_p10

    try:
        result = validate_eta6_p10()
    except Exception as exc:
        result = {
            "schema": "eta6.p10.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p11(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p11 import validate_eta6_p11

    try:
        result = validate_eta6_p11()
    except Exception as exc:
        result = {
            "schema": "eta6.p11.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p12(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p12 import validate_eta6_p12

    try:
        result = validate_eta6_p12()
    except Exception as exc:
        result = {
            "schema": "eta6.p12.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p13(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p13 import validate_eta6_p13

    try:
        result = validate_eta6_p13()
    except Exception as exc:
        result = {
            "schema": "eta6.p13.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p14(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p14 import validate_eta6_p14

    try:
        result = validate_eta6_p14()
    except Exception as exc:
        result = {
            "schema": "eta6.p14.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p15(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p15 import validate_eta6_p15

    try:
        result = validate_eta6_p15()
    except Exception as exc:
        result = {
            "schema": "eta6.p15.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p16(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p16 import validate_eta6_p16

    try:
        result = validate_eta6_p16()
    except Exception as exc:
        result = {
            "schema": "eta6.p16.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p17(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p17 import validate_eta6_p17

    try:
        result = validate_eta6_p17()
    except Exception as exc:
        result = {
            "schema": "eta6.p17.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p18(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p18 import validate_eta6_p18

    try:
        result = validate_eta6_p18()
    except Exception as exc:
        result = {
            "schema": "eta6.p18.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p19(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p19 import validate_eta6_p19

    try:
        result = validate_eta6_p19()
    except Exception as exc:
        result = {
            "schema": "eta6.p19.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p20(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p20 import validate_eta6_p20

    try:
        result = validate_eta6_p20()
    except Exception as exc:
        result = {
            "schema": "eta6.p20.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p21(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p21 import validate_eta6_p21

    try:
        result = validate_eta6_p21()
    except Exception as exc:
        result = {
            "schema": "eta6.p21.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p22(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p22 import validate_eta6_p22

    try:
        result = validate_eta6_p22()
    except Exception as exc:
        result = {
            "schema": "eta6.p22.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p23(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p23 import validate_eta6_p23

    try:
        result = validate_eta6_p23()
    except Exception as exc:
        result = {
            "schema": "eta6.p23.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p24(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p24 import validate_eta6_p24

    try:
        result = validate_eta6_p24()
    except Exception as exc:
        result = {
            "schema": "eta6.p24.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p25(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p25 import validate_eta6_p25

    try:
        result = validate_eta6_p25()
    except Exception as exc:
        result = {
            "schema": "eta6.p25.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p26(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p26 import validate_eta6_p26

    try:
        result = validate_eta6_p26()
    except Exception as exc:
        result = {
            "schema": "eta6.p26.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p27(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p27 import validate_eta6_p27

    try:
        result = validate_eta6_p27()
    except Exception as exc:
        result = {
            "schema": "eta6.p27.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p28(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p28 import validate_eta6_p28

    try:
        result = validate_eta6_p28()
    except Exception as exc:
        result = {
            "schema": "eta6.p28.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p29(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p29 import validate_eta6_p29

    try:
        result = validate_eta6_p29()
    except Exception as exc:
        result = {
            "schema": "eta6.p29.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p30(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p30 import validate_eta6_p30

    try:
        result = validate_eta6_p30()
    except Exception as exc:
        result = {
            "schema": "eta6.p30.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p31(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p31 import validate_eta6_p31

    try:
        result = validate_eta6_p31()
    except Exception as exc:
        result = {
            "schema": "eta6.p31.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p32(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p32 import validate_eta6_p32

    try:
        result = validate_eta6_p32()
    except Exception as exc:
        result = {
            "schema": "eta6.p32.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p33(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p33 import validate_eta6_p33

    try:
        result = validate_eta6_p33()
    except Exception as exc:
        result = {
            "schema": "eta6.p33.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p34(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p34 import validate_eta6_p34

    try:
        result = validate_eta6_p34()
    except Exception as exc:
        result = {
            "schema": "eta6.p34.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p35(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p35 import validate_eta6_p35

    try:
        result = validate_eta6_p35()
    except Exception as exc:
        result = {
            "schema": "eta6.p35.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p36(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p36 import validate_eta6_p36

    try:
        result = validate_eta6_p36()
    except Exception as exc:
        result = {
            "schema": "eta6.p36.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p37(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p37 import validate_eta6_p37

    try:
        result = validate_eta6_p37()
    except Exception as exc:
        result = {
            "schema": "eta6.p37.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p38(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p38 import validate_eta6_p38

    try:
        result = validate_eta6_p38()
    except Exception as exc:
        result = {
            "schema": "eta6.p38.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p39(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p39 import validate_eta6_p39

    try:
        result = validate_eta6_p39()
    except Exception as exc:
        result = {
            "schema": "eta6.p39.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_p40(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_p40 import validate_eta6_p40

    try:
        result = validate_eta6_p40()
    except Exception as exc:
        result = {
            "schema": "eta6.p40.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def eta6_core(
    *,
    pretty: bool,
) -> int:
    from src.certify_eta6_core import validate_eta6_core

    try:
        result = validate_eta6_core()
    except Exception as exc:
        result = {
            "schema": "eta6.core.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_lln(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_lln import validate_long_lln

    try:
        result = validate_long_lln()
    except Exception as exc:
        result = {
            "schema": "long.lln.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_kern(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_kern import validate_long_kern

    try:
        result = validate_long_kern()
    except Exception as exc:
        result = {
            "schema": "long.kern.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_tri(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_tri import validate_long_tri

    try:
        result = validate_long_tri()
    except Exception as exc:
        result = {
            "schema": "long.tri.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_basis(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_basis import validate_long_basis

    try:
        result = validate_long_basis()
    except Exception as exc:
        result = {
            "schema": "long.basis.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_rec(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_rec import validate_long_rec

    try:
        result = validate_long_rec()
    except Exception as exc:
        result = {
            "schema": "long.rec.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_eta(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_eta import validate_long_eta

    try:
        result = validate_long_eta()
    except Exception as exc:
        result = {
            "schema": "long.eta.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_eta2(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_eta2 import validate_long_eta2

    try:
        result = validate_long_eta2()
    except Exception as exc:
        result = {
            "schema": "long.eta2.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_lap(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_lap import validate_long_lap

    try:
        result = validate_long_lap()
    except Exception as exc:
        result = {
            "schema": "long.lap.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_cut(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_cut import validate_long_cut

    try:
        result = validate_long_cut()
    except Exception as exc:
        result = {
            "schema": "long.cut.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_flow(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_flow import validate_long_flow

    try:
        result = validate_long_flow()
    except Exception as exc:
        result = {
            "schema": "long.flow.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_absorb(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_absorb import validate_long_absorb

    try:
        result = validate_long_absorb()
    except Exception as exc:
        result = {
            "schema": "long.absorb.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_spec(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_spec import validate_long_spec

    try:
        result = validate_long_spec()
    except Exception as exc:
        result = {
            "schema": "long.spec.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_markov(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_markov import validate_long_markov

    try:
        result = validate_long_markov()
    except Exception as exc:
        result = {
            "schema": "long.markov.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_dev(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_dev import validate_long_dev

    try:
        result = validate_long_dev()
    except Exception as exc:
        result = {
            "schema": "long.dev.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_prof(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_prof import validate_long_prof

    try:
        result = validate_long_prof()
    except Exception as exc:
        result = {
            "schema": "long.prof.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_rate(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_rate import validate_long_rate

    try:
        result = validate_long_rate()
    except Exception as exc:
        result = {
            "schema": "long.rate.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_conv(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_conv import validate_long_conv

    try:
        result = validate_long_conv()
    except Exception as exc:
        result = {
            "schema": "long.conv.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_cls(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_cls import validate_long_cls

    try:
        result = validate_long_cls()
    except Exception as exc:
        result = {
            "schema": "long.cls.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_univ(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_univ import validate_long_univ

    try:
        result = validate_long_univ()
    except Exception as exc:
        result = {
            "schema": "long.univ.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_min(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_min import validate_long_min

    try:
        result = validate_long_min()
    except Exception as exc:
        result = {
            "schema": "long.min.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_nat(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_nat import validate_long_nat

    try:
        result = validate_long_nat()
    except Exception as exc:
        result = {
            "schema": "long.nat.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_hlim(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_hlim import validate_long_hlim

    try:
        result = validate_long_hlim()
    except Exception as exc:
        result = {
            "schema": "long.hlim.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_ext(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_ext import validate_long_ext

    try:
        result = validate_long_ext()
    except Exception as exc:
        result = {
            "schema": "long.ext.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_obj(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_obj import validate_long_obj

    try:
        result = validate_long_obj()
    except Exception as exc:
        result = {
            "schema": "long.obj.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_tens(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_tens import validate_long_tens

    try:
        result = validate_long_tens()
    except Exception as exc:
        result = {
            "schema": "long.tens.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_lift(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_lift import validate_long_lift

    try:
        result = validate_long_lift()
    except Exception as exc:
        result = {
            "schema": "long.lift.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_raw(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_raw import validate_long_raw

    try:
        result = validate_long_raw()
    except Exception as exc:
        result = {
            "schema": "long.raw.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_h16(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_h16 import validate_long_h16

    try:
        result = validate_long_h16()
    except Exception as exc:
        result = {
            "schema": "long.h16.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_path(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_path import validate_long_path

    try:
        result = validate_long_path()
    except Exception as exc:
        result = {
            "schema": "long.path.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_comp(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_comp import validate_long_comp

    try:
        result = validate_long_comp()
    except Exception as exc:
        result = {
            "schema": "long.comp.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_sheaf(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_sheaf import validate_long_sheaf

    try:
        result = validate_long_sheaf()
    except Exception as exc:
        result = {
            "schema": "long.sheaf.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_all(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_all import validate_long_all

    try:
        result = validate_long_all()
    except Exception as exc:
        result = {
            "schema": "long.all.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_orient(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_orient import validate_long_orient

    try:
        result = validate_long_orient()
    except Exception as exc:
        result = {
            "schema": "long.orient.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_dual(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_dual import validate_long_dual

    try:
        result = validate_long_dual()
    except Exception as exc:
        result = {
            "schema": "long.dual.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_prob(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_prob import validate_long_prob

    try:
        result = validate_long_prob()
    except Exception as exc:
        result = {
            "schema": "long.prob.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_mart(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_mart import validate_long_mart

    try:
        result = validate_long_mart()
    except Exception as exc:
        result = {
            "schema": "long.mart.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_stop(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_stop import validate_long_stop

    try:
        result = validate_long_stop()
    except Exception as exc:
        result = {
            "schema": "long.stop.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_dlim(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_dlim import validate_long_dlim

    try:
        result = validate_long_dlim()
    except Exception as exc:
        result = {
            "schema": "long.dlim.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_linf(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_linf import validate_long_linf

    try:
        result = validate_long_linf()
    except Exception as exc:
        result = {
            "schema": "long.linf.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_ind(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_ind import validate_long_ind

    try:
        result = validate_long_ind()
    except Exception as exc:
        result = {
            "schema": "long.ind.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_suppind(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_suppind import validate_long_suppind

    try:
        result = validate_long_suppind()
    except Exception as exc:
        result = {
            "schema": "long.suppind.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_recind(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_recind import validate_long_recind

    try:
        result = validate_long_recind()
    except Exception as exc:
        result = {
            "schema": "long.recind.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_formind(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_formind import validate_long_formind

    try:
        result = validate_long_formind()
    except Exception as exc:
        result = {
            "schema": "long.formind.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_domind(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_domind import validate_long_domind

    try:
        result = validate_long_domind()
    except Exception as exc:
        result = {
            "schema": "long.domind.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_gapind(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_gapind import validate_long_gapind

    try:
        result = validate_long_gapind()
    except Exception as exc:
        result = {
            "schema": "long.gapind.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_llnind(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_llnind import validate_long_llnind

    try:
        result = validate_long_llnind()
    except Exception as exc:
        result = {
            "schema": "long.llnind.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_thm(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_thm import validate_long_thm

    try:
        result = validate_long_thm()
    except Exception as exc:
        result = {
            "schema": "long.thm.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_inv(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_inv import validate_long_inv

    try:
        result = validate_long_inv()
    except Exception as exc:
        result = {
            "schema": "long.inv.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_inv_exhaust(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_inv_exhaust import validate_long_inv_exhaust

    try:
        result = validate_long_inv_exhaust()
    except Exception as exc:
        result = {
            "schema": "long.inv_exhaust.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_anom(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_anom import validate_long_anom

    try:
        result = validate_long_anom()
    except Exception as exc:
        result = {
            "schema": "long.anom.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_mat(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_mat import validate_long_mat

    try:
        result = validate_long_mat()
    except Exception as exc:
        result = {
            "schema": "long.mat.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_auto(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_auto import validate_long_auto

    try:
        result = validate_long_auto()
    except Exception as exc:
        result = {
            "schema": "long.auto.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_orac(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_orac import validate_long_orac

    try:
        result = validate_long_orac()
    except Exception as exc:
        result = {
            "schema": "long.orac.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_gr(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_gr import validate_long_gr

    try:
        result = validate_long_gr()
    except Exception as exc:
        result = {
            "schema": "long.gr.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_lor(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_lor import validate_long_lor

    try:
        result = validate_long_lor()
    except Exception as exc:
        result = {
            "schema": "long.lor.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_time_map(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_time_map import validate_long_time_map

    try:
        result = validate_long_time_map()
    except Exception as exc:
        result = {
            "schema": "long.time_map.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_time_sem(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_time_sem import validate_long_time_sem

    try:
        result = validate_long_time_sem()
    except Exception as exc:
        result = {
            "schema": "long.time_sem.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_metric_gate(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_metric_gate import validate_long_metric_gate

    try:
        result = validate_long_metric_gate()
    except Exception as exc:
        result = {
            "schema": "long.metric_gate.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_contact_lift(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_contact_lift import validate_long_contact_lift

    try:
        result = validate_long_contact_lift()
    except Exception as exc:
        result = {
            "schema": "long.contact_lift.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_transition_sem(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_transition_sem import validate_long_transition_sem

    try:
        result = validate_long_transition_sem()
    except Exception as exc:
        result = {
            "schema": "long.transition_sem.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_stress20(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_stress20 import validate_long_stress20

    try:
        result = validate_long_stress20()
    except Exception as exc:
        result = {
            "schema": "long.stress20.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_stress_gate(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_stress_gate import validate_long_stress_gate

    try:
        result = validate_long_stress_gate()
    except Exception as exc:
        result = {
            "schema": "long.stress_gate.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_stress_couple(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_stress_couple import validate_long_stress_couple

    try:
        result = validate_long_stress_couple()
    except Exception as exc:
        result = {
            "schema": "long.stress_couple.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_semstress(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_semstress import validate_long_semstress

    try:
        result = validate_long_semstress()
    except Exception as exc:
        result = {
            "schema": "long.semstress.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_metric_rank_gate(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_metric_rank_gate import validate_long_metric_rank_gate

    try:
        result = validate_long_metric_rank_gate()
    except Exception as exc:
        result = {
            "schema": "long.metric_rank_gate.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_dim4_gate(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_dim4_gate import validate_long_dim4_gate

    try:
        result = validate_long_dim4_gate()
    except Exception as exc:
        result = {
            "schema": "long.dim4_gate.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_rim(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_rim import validate_long_rim

    try:
        result = validate_long_rim()
    except Exception as exc:
        result = {
            "schema": "long.rim.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_rim_select(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_rim_select import validate_long_rim_select

    try:
        result = validate_long_rim_select()
    except Exception as exc:
        result = {
            "schema": "long.rim_select.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_sel(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_sel import validate_long_sel

    try:
        result = validate_long_sel()
    except Exception as exc:
        result = {
            "schema": "long.sel.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_psel(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_psel import validate_long_psel

    try:
        result = validate_long_psel()
    except Exception as exc:
        result = {
            "schema": "long.psel.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_l63(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_l63 import validate_long_l63

    try:
        result = validate_long_l63()
    except Exception as exc:
        result = {
            "schema": "long.l63.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_f63(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_f63 import validate_long_f63

    try:
        result = validate_long_f63()
    except Exception as exc:
        result = {
            "schema": "long.f63.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_frim(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_frim import validate_long_frim

    try:
        result = validate_long_frim()
    except Exception as exc:
        result = {
            "schema": "long.frim.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_sfork(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_sfork import validate_long_sfork

    try:
        result = validate_long_sfork()
    except Exception as exc:
        result = {
            "schema": "long.sfork.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_glaw(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_glaw import validate_long_glaw

    try:
        result = validate_long_glaw()
    except Exception as exc:
        result = {
            "schema": "long.glaw.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_gclk(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_gclk import validate_long_gclk

    try:
        result = validate_long_gclk()
    except Exception as exc:
        result = {
            "schema": "long.gclk.verification@2",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_tlift(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_tlift import validate_long_tlift

    try:
        result = validate_long_tlift()
    except Exception as exc:
        result = {
            "schema": "long.tlift.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_abmap(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_abmap import validate_long_abmap

    try:
        result = validate_long_abmap()
    except Exception as exc:
        result = {
            "schema": "long.abmap.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_rtick(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_rtick import validate_long_rtick

    try:
        result = validate_long_rtick()
    except Exception as exc:
        result = {
            "schema": "long.rtick.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_rsem(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_rsem import validate_long_rsem

    try:
        result = validate_long_rsem()
    except Exception as exc:
        result = {
            "schema": "long.rsem.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_oprom(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_oprom import validate_long_oprom

    try:
        result = validate_long_oprom()
    except Exception as exc:
        result = {
            "schema": "long.oprom.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_c60op(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_c60op import validate_long_c60op

    try:
        result = validate_long_c60op()
    except Exception as exc:
        result = {
            "schema": "long.c60op.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_c60negf(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_c60negf import validate_long_c60negf

    try:
        result = validate_long_c60negf()
    except Exception as exc:
        result = {
            "schema": "long.c60negf.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_c59x(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_c59x import validate_long_c59x

    try:
        result = validate_long_c59x()
    except Exception as exc:
        result = {
            "schema": "long.c59x.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_c59e(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_c59e import validate_long_c59e

    try:
        result = validate_long_c59e()
    except Exception as exc:
        result = {
            "schema": "long.c59e.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_c59cf(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_c59cf import validate_long_c59cf

    try:
        result = validate_long_c59cf()
    except Exception as exc:
        result = {
            "schema": "long.c59cf.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_c59st(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_c59st import validate_long_c59st

    try:
        result = validate_long_c59st()
    except Exception as exc:
        result = {
            "schema": "long.c59st.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_c59kt(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_c59kt import validate_long_c59kt

    try:
        result = validate_long_c59kt()
    except Exception as exc:
        result = {
            "schema": "long.c59kt.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_c59q(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_c59q import validate_long_c59q

    try:
        result = validate_long_c59q()
    except Exception as exc:
        result = {
            "schema": "long.c59q.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_c59pk(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_c59pk import validate_long_c59pk

    try:
        result = validate_long_c59pk()
    except Exception as exc:
        result = {
            "schema": "long.c59pk.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_c59s3(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_c59s3 import validate_long_c59s3

    try:
        result = validate_long_c59s3()
    except Exception as exc:
        result = {
            "schema": "long.c59s3.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_c59np3(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_c59np3 import validate_long_c59np3

    try:
        result = validate_long_c59np3()
    except Exception as exc:
        result = {
            "schema": "long.c59np3.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_c59p3s(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_c59p3s import validate_long_c59p3s

    try:
        result = validate_long_c59p3s()
    except Exception as exc:
        result = {
            "schema": "long.c59p3s.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_c59p3v(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_c59p3v import validate_long_c59p3v

    try:
        result = validate_long_c59p3v()
    except Exception as exc:
        result = {
            "schema": "long.c59p3v.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_c59p3o(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_c59p3o import validate_long_c59p3o

    try:
        result = validate_long_c59p3o()
    except Exception as exc:
        result = {
            "schema": "long.c59p3o.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_c59p3a(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_c59p3a import validate_long_c59p3a

    try:
        result = validate_long_c59p3a()
    except Exception as exc:
        result = {
            "schema": "long.c59p3a.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_c59p3t(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_c59p3t import validate_long_c59p3t

    try:
        result = validate_long_c59p3t()
    except Exception as exc:
        result = {
            "schema": "long.c59p3t.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_c59p3b(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_c59p3b import validate_long_c59p3b

    try:
        result = validate_long_c59p3b()
    except Exception as exc:
        result = {
            "schema": "long.c59p3b.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_c59p3r(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_c59p3r import validate_long_c59p3r

    try:
        result = validate_long_c59p3r()
    except Exception as exc:
        result = {
            "schema": "long.c59p3r.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_c59p3i(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_c59p3i import validate_long_c59p3i

    try:
        result = validate_long_c59p3i()
    except Exception as exc:
        result = {
            "schema": "long.c59p3i.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_c59p3f(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_c59p3f import validate_long_c59p3f

    try:
        result = validate_long_c59p3f()
    except Exception as exc:
        result = {
            "schema": "long.c59p3f.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_c59p3u(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_c59p3u import validate_long_c59p3u

    try:
        result = validate_long_c59p3u()
    except Exception as exc:
        result = {
            "schema": "long.c59p3u.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_c59p3w(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_c59p3w import validate_long_c59p3w

    try:
        result = validate_long_c59p3w()
    except Exception as exc:
        result = {
            "schema": "long.c59p3w.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_c59p3c(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_c59p3c import validate_long_c59p3c

    try:
        result = validate_long_c59p3c()
    except Exception as exc:
        result = {
            "schema": "long.c59p3c.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_c59p3d(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_c59p3d import validate_long_c59p3d

    try:
        result = validate_long_c59p3d()
    except Exception as exc:
        result = {
            "schema": "long.c59p3d.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_c59p3e(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_c59p3e import validate_long_c59p3e

    try:
        result = validate_long_c59p3e()
    except Exception as exc:
        result = {
            "schema": "long.c59p3e.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_c59p3g(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_c59p3g import validate_long_c59p3g

    try:
        result = validate_long_c59p3g()
    except Exception as exc:
        result = {
            "schema": "long.c59p3g.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_c59p3h(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_c59p3h import validate_long_c59p3h

    try:
        result = validate_long_c59p3h()
    except Exception as exc:
        result = {
            "schema": "long.c59p3h.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_c59p3j(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_c59p3j import validate_long_c59p3j

    try:
        result = validate_long_c59p3j()
    except Exception as exc:
        result = {
            "schema": "long.c59p3j.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_c59p3k(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_c59p3k import validate_long_c59p3k

    try:
        result = validate_long_c59p3k()
    except Exception as exc:
        result = {
            "schema": "long.c59p3k.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_c59p3m(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_c59p3m import validate_long_c59p3m

    try:
        result = validate_long_c59p3m()
    except Exception as exc:
        result = {
            "schema": "long.c59p3m.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_c59p3n(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_c59p3n import validate_long_c59p3n

    try:
        result = validate_long_c59p3n()
    except Exception as exc:
        result = {
            "schema": "long.c59p3n.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_pax(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_pax import validate_long_pax

    try:
        result = validate_long_pax()
    except Exception as exc:
        result = {
            "schema": "long.pax.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_frontier(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_frontier import validate_long_frontier

    try:
        result = validate_long_frontier()
    except Exception as exc:
        result = {
            "schema": "long.frontier.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_cluster(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_cluster import validate_long_cluster

    try:
        result = validate_long_cluster()
    except Exception as exc:
        result = {
            "schema": "long.cluster.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_c2uf(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_c2uf import validate_long_c2uf

    try:
        result = validate_long_c2uf()
    except Exception as exc:
        result = {
            "schema": "long.c2uf.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_hcinv(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_hcinv import validate_long_hcinv

    try:
        result = validate_long_hcinv()
    except Exception as exc:
        result = {
            "schema": "long.hcinv.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_hcfoam(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_hcfoam import validate_long_hcfoam

    try:
        result = validate_long_hcfoam()
    except Exception as exc:
        result = {
            "schema": "long.hcfoam.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_hcpi(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_hcpi import validate_long_hcpi

    try:
        result = validate_long_hcpi()
    except Exception as exc:
        result = {
            "schema": "long.hcpi.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_hcshape(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_hcshape import validate_long_hcshape

    try:
        result = validate_long_hcshape()
    except Exception as exc:
        result = {
            "schema": "long.hcshape.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_hcscalar(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_hcscalar import validate_long_hcscalar

    try:
        result = validate_long_hcscalar()
    except Exception as exc:
        result = {
            "schema": "long.hcscalar.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_hcsupp(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_hcsupp import validate_long_hcsupp

    try:
        result = validate_long_hcsupp()
    except Exception as exc:
        result = {
            "schema": "long.hcsupp.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_hcbasis(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_hcbasis import validate_long_hcbasis

    try:
        result = validate_long_hcbasis()
    except Exception as exc:
        result = {
            "schema": "long.hcbasis.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_hcgrade(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_hcgrade import validate_long_hcgrade

    try:
        result = validate_long_hcgrade()
    except Exception as exc:
        result = {
            "schema": "long.hcgrade.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_hcperm(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_hcperm import validate_long_hcperm

    try:
        result = validate_long_hcperm()
    except Exception as exc:
        result = {
            "schema": "long.hcperm.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_k23(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_k23 import validate_long_k23

    try:
        result = validate_long_k23()
    except Exception as exc:
        result = {
            "schema": "long.k23.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_k23oct(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_k23oct import validate_long_k23oct

    try:
        result = validate_long_k23oct()
    except Exception as exc:
        result = {
            "schema": "long.k23oct.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_k23row(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_k23row import validate_long_k23row

    try:
        result = validate_long_k23row()
    except Exception as exc:
        result = {
            "schema": "long.k23row.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_k23max(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_k23max import validate_long_k23max

    try:
        result = validate_long_k23max()
    except Exception as exc:
        result = {
            "schema": "long.k23max.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_psec(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_psec import validate_long_psec

    try:
        result = validate_long_psec()
    except Exception as exc:
        result = {
            "schema": "long.psec.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_binc(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_binc import validate_long_binc

    try:
        result = validate_long_binc()
    except Exception as exc:
        result = {
            "schema": "long.binc.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_krein(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_krein import validate_long_krein

    try:
        result = validate_long_krein()
    except Exception as exc:
        result = {
            "schema": "long.krein.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_kr39(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_kr39 import validate_long_kr39

    try:
        result = validate_long_kr39()
    except Exception as exc:
        result = {
            "schema": "long.kr39.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_b3mod(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_b3mod import validate_long_b3mod

    try:
        result = validate_long_b3mod()
    except Exception as exc:
        result = {
            "schema": "long.b3mod.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_b3alg(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_b3alg import validate_long_b3alg

    try:
        result = validate_long_b3alg()
    except Exception as exc:
        result = {
            "schema": "long.b3alg.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_gchar(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_gchar import validate_long_gchar

    try:
        result = validate_long_gchar()
    except Exception as exc:
        result = {
            "schema": "long.gchar.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_ctor(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_ctor import validate_long_ctor

    try:
        result = validate_long_ctor()
    except Exception as exc:
        result = {
            "schema": "long.ctor.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def a985_direct_packet_bridge(
    *,
    pretty: bool,
) -> int:
    from src.certify_d20_a985_direct_packet_bridge_obstruction import (
        validate_d20_a985_direct_packet_bridge_obstruction,
    )

    try:
        report = validate_d20_a985_direct_packet_bridge_obstruction()
        result = {
            "schema": "d20.a985_direct_packet_bridge_obstruction.verification@1",
            "status": "PASS",
            "verified_report": (
                "data/invariants/d20/theorems/"
                "d20_a985_direct_packet_bridge_obstruction/report.json"
            ),
            "certificate_sha256": report["certificate_sha256"],
            "summary": report["derived"]["direct_bridge_summary"],
            "multiplicativity_violation": report["derived"][
                "multiplicativity_violation"
            ],
            "closure_boundary": report["definition"]["scope"],
            "next_highest_yield_item": report.get("next_highest_yield_item"),
        }
    except Exception as exc:
        result = {
            "schema": "d20.a985_direct_packet_bridge_obstruction.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def a985_mat2_hom_boundary(
    *,
    pretty: bool,
) -> int:
    from src.certify_d20_a985_mat2_hom_boundary import (
        validate_d20_a985_mat2_hom_boundary,
    )

    try:
        report = validate_d20_a985_mat2_hom_boundary()
        result = {
            "schema": "d20.a985_mat2_hom_boundary.verification@1",
            "status": "PASS",
            "verified_report": (
                "data/invariants/d20/theorems/d20_a985_mat2_hom_boundary/report.json"
            ),
            "certificate_sha256": report["certificate_sha256"],
            "dimension_summary": report["derived"]["dimension_summary"],
            "homomorphism_boundary": report["derived"]["homomorphism_boundary"],
            "closure_boundary": report["closure_boundary"],
            "next_highest_yield_item": report.get("next_highest_yield_item"),
        }
    except Exception as exc:
        result = {
            "schema": "d20.a985_mat2_hom_boundary.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def a985_labelled_nonfaithful_packet_hom(
    *,
    pretty: bool,
) -> int:
    from src.certify_d20_a985_labelled_nonfaithful_packet_hom_obstruction import (
        validate_d20_a985_labelled_nonfaithful_packet_hom_obstruction,
    )

    try:
        report = validate_d20_a985_labelled_nonfaithful_packet_hom_obstruction()
        result = {
            "schema": "d20.a985_labelled_nonfaithful_packet_hom_obstruction.verification@1",
            "status": "PASS",
            "verified_report": (
                "data/invariants/d20/theorems/"
                "d20_a985_labelled_nonfaithful_packet_hom_obstruction/report.json"
            ),
            "certificate_sha256": report["certificate_sha256"],
            "evaluation_summary": report["derived"]["evaluation_summary"],
            "per_target_summary": report["derived"]["per_target_summary"],
            "closure_boundary": report["closure_boundary"],
            "next_highest_yield_item": report.get("next_highest_yield_item"),
        }
    except Exception as exc:
        result = {
            "schema": "d20.a985_labelled_nonfaithful_packet_hom_obstruction.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_pobj(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_pobj import validate_long_pobj

    try:
        result = validate_long_pobj()
    except Exception as exc:
        result = {
            "schema": "long.pobj.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_paths(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_paths import validate_long_paths

    try:
        result = validate_long_paths()
    except Exception as exc:
        result = {
            "schema": "long.paths.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def long_measure(
    *,
    pretty: bool,
) -> int:
    from src.certify_long_measure import validate_long_measure

    try:
        result = validate_long_measure()
    except Exception as exc:
        result = {
            "schema": "long.measure.verification@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_sixj_2114_neighborhood(
    *,
    pretty: bool,
) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def c985_signature_aperture_closure_tail_sixj_2114_triple(
    *,
    pretty: bool,
) -> int:
    from src.certify_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_triple_screen import (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_triple_screen,
    )

    try:
        result = (
            validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_triple_screen()
        )
    except Exception as exc:
        result = {
            "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_triple_screen@1",
            "status": "FAIL",
            "error": str(exc),
        }
    return finish(result, pretty)


def finish(result: dict[str, Any], pretty: bool) -> int:
    emit(result, pretty)
    return 0 if result.get("status") == "PASS" else 1


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify the d20 bundle.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in (
        "core",
        "audit",
        "rebuild",
        "refresh-certificate",
        "strict-replay",
        "evidence-index",
        "compiler-scene-selftest",
        "compiler-a42-d20-replay",
        "compiler-nonstrict",
        "integration-nonstrict",
        "jacobian-cubic-contract",
        "jacobian-cubic-intake",
        "jacobian-cubic-closure",
        "jacobian-cubic-status",
        "jacobian-cubic-nonstrict",
        "jacobian-cubic-cache",
        "talagrand-handoff",
        "talagrand-chain-audit",
        "talagrand-kkt-obligation",
        "c985-registry",
        "c985-fusion",
        "c985-associator",
        "c985-unit",
        "c985-triangle",
        "c985-duality",
        "c985-pentagon",
        "c985-zigzag",
        "c985-final",
        "c985-geometry",
        "c985-d20-atlas",
        "c985-hyperbolic-graph",
        "c985-poincare",
        "c985-filtration",
        "c985-nerve",
        "c985-chart-atlas",
        "c985-transition-groupoid",
        "c985-normal-words",
        "c985-symbolic-rewrites",
        "c985-symbolic-associativity",
        "c985-rewrite-complex",
        "c985-interval-sheaf",
        "c985-preserved-core",
        "c985-chamber-spine",
        "c985-morse-reeb",
        "c985-boundary-transfer",
        "c985-atom-flow",
        "c985-signature-subboundary",
        "c985-signature-transfer",
        "c985-signature-spectral-cut",
        "c985-signature-quotient",
        "c985-signature-geometry",
        "c985-signature-geodesic",
        "c985-signature-residual-chart",
        "c985-signature-cell-complex",
        "c985-signature-boundary-flux",
        "c985-signature-boundary-rates",
        "c985-signature-conductance-spine",
        "c985-signature-spine-poincare",
        "c985-signature-routing-prefix",
        "c985-signature-branching-law",
        "c985-signature-typed-corridors",
        "c985-signature-gate-automaton",
        "c985-signature-language-graph",
        "c985-signature-aperture-fan",
        "c985-signature-aperture-insertion",
        "c985-signature-x2-splice",
        "c985-signature-x2-detour",
        "c985-signature-x2-clean-detour",
        "c985-signature-x2-x4-aperture",
        "c985-signature-aperture-cycle",
        "c985-signature-aperture-cycle-ranking",
        "c985-signature-aperture-cycle-pareto",
        "c985-signature-aperture-mixed-contact",
        "c985-signature-aperture-atom-selector",
        "c985-signature-aperture-atom-tradeoff",
        "c985-signature-aperture-tail-hybrid",
        "c985-signature-aperture-bounded-backtrack",
        "c985-signature-aperture-symbol-state",
        "c985-signature-aperture-overhead2-carrier",
        "c985-signature-aperture-overhead2-repair",
        "c985-signature-aperture-overhead2-tail",
        "c985-signature-aperture-overhead2-cycle-rank",
        "c985-signature-aperture-overhead3-trace-quotient",
        "c985-signature-aperture-rank104-audit",
        "c985-signature-aperture-overhead3-weak-promotion",
        "c985-signature-aperture-overhead3-strongification-gap",
        "c985-signature-aperture-rank104-strongification-geometry",
        "c985-signature-aperture-cost3-strongification-ranking",
        "c985-signature-aperture-closure-outlier-geometry",
        "c985-signature-aperture-closure-tail-endpoint-split",
        "c985-signature-aperture-closure-tail-rewrite-lift",
        "c985-signature-aperture-closure-tail-prefix-chord",
        "c985-signature-aperture-closure-tail-carrier-splice",
        "c985-signature-aperture-closure-tail-splice-optimality",
        "c985-signature-aperture-closure-tail-lower-lift",
        "c985-signature-aperture-closure-tail-partial-splitter",
        "c985-signature-aperture-closure-tail-trim-neighborhood",
        "c985-signature-aperture-closure-tail-clear-corridor",
        "c985-signature-aperture-closure-tail-clear-corridor-level2",
        "c985-signature-aperture-closure-tail-gate-repair",
        "c985-signature-aperture-closure-tail-boundary-bridge",
        "c985-signature-aperture-closure-tail-virtual-graft",
        "c985-signature-aperture-closure-tail-native-insertion",
        "c985-signature-aperture-closure-tail-symbolic-window",
        "c985-signature-aperture-closure-tail-skip-window-grammar",
        "c985-signature-aperture-closure-tail-repaired-automaton",
        "c985-signature-aperture-closure-tail-transfer",
        "c985-signature-aperture-closure-tail-flow-window",
        "c985-signature-aperture-closure-tail-promoted-window",
        "c985-signature-aperture-closure-tail-promoted-transfer",
        "c985-signature-aperture-closure-tail-second-window",
        "c985-signature-aperture-closure-tail-second-window-promotion",
        "c985-signature-aperture-closure-tail-second-window-transfer",
        "c985-signature-aperture-closure-tail-sixj-frame",
        "c985-signature-aperture-closure-tail-sixj-recoupling-pair",
        "c985-signature-aperture-closure-tail-sixj-recoupling-triple",
        "c985-signature-aperture-closure-tail-sixj-recoupling-closure",
        "c985-signature-aperture-closure-tail-sixj-nonlocal-screen",
        "c985-signature-aperture-closure-tail-sixj-borromean-hypergraph",
        "c985-signature-aperture-closure-tail-sixj-conductance-preservation",
        "c985-signature-aperture-closure-tail-eta6-charge",
        "c985-signature-aperture-closure-tail-eta6-holonomy",
        "c985-signature-aperture-closure-tail-eta6-dini-torsion",
        "c985-signature-aperture-closure-tail-eta6-h4-precursor",
        "c985-signature-aperture-closure-tail-eta6-graham-throat",
        "c985-signature-aperture-closure-tail-eta6-aperture-polygon",
        "c985-signature-aperture-closure-tail-eta6-truncated-skeleton",
        "c985-signature-aperture-closure-tail-eta6-hex-face-barycenter",
        "c985-signature-aperture-closure-tail-eta6-nonholonomic-aperture",
        "eta6-ext-cone",
        "eta6-gordan",
        "eta6-aext",
        "eta6-srows",
        "eta6-islack",
        "eta6-hpol",
        "eta6-surg",
        "eta6-repl",
        "eta6-xfer",
        "eta6-hit2",
        "eta6-gap",
        "eta6-p2",
        "eta6-t2",
        "eta6-f4",
        "eta6-p5",
        "eta6-p6",
        "eta6-p7",
        "eta6-p8",
        "eta6-p9",
        "eta6-p10",
        "eta6-p11",
        "eta6-p12",
        "eta6-p13",
        "eta6-p14",
        "eta6-p15",
        "eta6-p16",
        "eta6-p17",
        "eta6-p18",
        "eta6-p19",
        "eta6-p20",
        "eta6-p21",
        "eta6-p22",
        "eta6-p23",
        "eta6-p24",
        "eta6-p25",
        "eta6-p26",
        "eta6-p27",
        "eta6-p28",
        "eta6-p29",
        "eta6-p30",
        "eta6-p31",
        "eta6-p32",
        "eta6-p33",
        "eta6-p34",
        "eta6-p35",
        "eta6-p36",
        "eta6-p37",
        "eta6-p38",
        "eta6-p39",
        "eta6-p40",
        "eta6-core",
        "long-lln",
        "long-kern",
        "long-tri",
        "long-basis",
        "long-rec",
        "long-eta",
        "long-eta2",
        "long-lap",
        "long-cut",
        "long-flow",
        "long-absorb",
        "long-spec",
        "long-markov",
        "long-dev",
        "long-prof",
        "long-rate",
        "long-conv",
        "long-cls",
        "long-univ",
        "long-min",
        "long-nat",
        "long-hlim",
        "long-ext",
        "long-obj",
        "long-tens",
        "long-lift",
        "long-raw",
        "long-h16",
        "long-path",
        "long-comp",
        "long-sheaf",
        "long-all",
        "long-orient",
        "long-dual",
        "long-prob",
        "long-mart",
        "long-stop",
        "long-dlim",
        "long-linf",
        "long-ind",
        "long-suppind",
        "long-recind",
        "long-formind",
        "long-domind",
        "long-gapind",
        "long-llnind",
        "long-thm",
        "long-inv",
        "long-inv-exhaust",
        "long-anom",
        "long-mat",
        "long-auto",
        "long-orac",
        "long-ctor",
        "long-gr",
        "long-lor",
        "long-time-map",
        "long-time-sem",
        "long-metric-gate",
        "long-contact-lift",
        "long-transition-sem",
        "long-stress20",
        "long-stress-gate",
        "long-stress-couple",
        "long-semstress",
        "long-metric-rank-gate",
        "long-dim4-gate",
        "long-rim",
        "long-rim-select",
        "long-sel",
        "long-psel",
        "long-pax",
        "long-l63",
        "long-f63",
        "long-frim",
        "long-sfork",
        "long-glaw",
        "long-gclk",
        "long-tlift",
        "long-abmap",
        "long-rtick",
        "long-rsem",
        "long-oprom",
        "long-c60op",
        "long-c60negf",
        "long-c59x",
        "long-c59e",
        "long-c59cf",
        "long-c59st",
        "long-c59kt",
        "long-c59q",
        "long-c59pk",
        "long-c59s3",
        "long-c59np3",
        "long-c59p3s",
        "long-c59p3v",
        "long-c59p3o",
        "long-c59p3a",
        "long-c59p3t",
        "long-c59p3b",
        "long-c59p3r",
        "long-c59p3i",
        "long-c59p3f",
        "long-c59p3u",
        "long-c59p3w",
        "long-c59p3c",
        "long-c59p3d",
        "long-c59p3e",
        "long-c59p3g",
        "long-c59p3h",
        "long-c59p3j",
        "long-c59p3k",
        "long-c59p3m",
        "long-c59p3n",
        "long-frontier",
        "long-cluster",
        "long-c2uf",
        "long-hcinv",
        "long-hcfoam",
        "long-hcpi",
        "long-hcshape",
        "long-hcscalar",
        "long-hcsupp",
        "long-hcbasis",
        "long-hcgrade",
        "long-hcperm",
        "long-k23",
        "long-k23oct",
        "long-k23row",
        "long-k23max",
        "long-psec",
        "long-binc",
        "long-krein",
        "long-kr39",
        "long-b3mod",
        "long-b3alg",
        "long-gchar",
        "a985-direct-packet-bridge",
        "a985-mat2-hom-boundary",
        "a985-labelled-nonfaithful-packet-hom",
        "long-pobj",
        "long-paths",
        "long-measure",
        "c985-signature-aperture-closure-tail-sixj-2114-neighborhood",
        "c985-signature-aperture-closure-tail-sixj-2114-triple",
        "token-burn",
        "tamper",
    ):
        p = sub.add_parser(name)
        p.add_argument("--pretty", action="store_true")
        if name == "rebuild":
            p.add_argument(
                "--cached-source",
                action="store_true",
                help="Reuse existing checked source artifacts and skip heavy source refresh.",
            )
    args = parser.parse_args()

    if args.command == "rebuild":
        raise SystemExit(rebuild(pretty=args.pretty, cached_source=args.cached_source))
    if args.command == "refresh-certificate":
        raise SystemExit(refresh_certificate(pretty=args.pretty))
    if args.command == "evidence-index":
        raise SystemExit(verify_evidence_index(pretty=args.pretty))
    if args.command == "compiler-scene-selftest":
        raise SystemExit(compiler_scene_selftest(pretty=args.pretty))
    if args.command == "compiler-a42-d20-replay":
        raise SystemExit(compiler_a42_d20_replay(pretty=args.pretty))
    if args.command == "compiler-nonstrict":
        raise SystemExit(compiler_nonstrict(pretty=args.pretty))
    if args.command == "integration-nonstrict":
        raise SystemExit(integration_nonstrict(pretty=args.pretty))
    if args.command == "jacobian-cubic-contract":
        raise SystemExit(jacobian_cubic_contract(pretty=args.pretty))
    if args.command == "jacobian-cubic-intake":
        raise SystemExit(jacobian_cubic_intake(pretty=args.pretty))
    if args.command == "jacobian-cubic-closure":
        raise SystemExit(jacobian_cubic_closure(pretty=args.pretty))
    if args.command == "jacobian-cubic-status":
        raise SystemExit(jacobian_cubic_status(pretty=args.pretty))
    if args.command == "jacobian-cubic-nonstrict":
        raise SystemExit(jacobian_cubic_nonstrict(pretty=args.pretty))
    if args.command == "jacobian-cubic-cache":
        raise SystemExit(jacobian_cubic_cache(pretty=args.pretty))
    if args.command == "talagrand-handoff":
        raise SystemExit(talagrand_handoff(pretty=args.pretty))
    if args.command == "talagrand-chain-audit":
        raise SystemExit(talagrand_chain_audit(pretty=args.pretty))
    if args.command == "talagrand-kkt-obligation":
        raise SystemExit(talagrand_kkt_obligation(pretty=args.pretty))
    if args.command == "c985-registry":
        raise SystemExit(c985_registry(pretty=args.pretty))
    if args.command == "c985-fusion":
        raise SystemExit(c985_fusion(pretty=args.pretty))
    if args.command == "c985-associator":
        raise SystemExit(c985_associator(pretty=args.pretty))
    if args.command == "c985-unit":
        raise SystemExit(c985_unit(pretty=args.pretty))
    if args.command == "c985-triangle":
        raise SystemExit(c985_triangle(pretty=args.pretty))
    if args.command == "c985-duality":
        raise SystemExit(c985_duality(pretty=args.pretty))
    if args.command == "c985-pentagon":
        raise SystemExit(c985_pentagon(pretty=args.pretty))
    if args.command == "c985-zigzag":
        raise SystemExit(c985_zigzag(pretty=args.pretty))
    if args.command == "c985-final":
        raise SystemExit(c985_final(pretty=args.pretty))
    if args.command == "c985-geometry":
        raise SystemExit(c985_geometry(pretty=args.pretty))
    if args.command == "c985-d20-atlas":
        raise SystemExit(c985_d20_atlas(pretty=args.pretty))
    if args.command == "c985-hyperbolic-graph":
        raise SystemExit(c985_hyperbolic_graph(pretty=args.pretty))
    if args.command == "c985-poincare":
        raise SystemExit(c985_poincare(pretty=args.pretty))
    if args.command == "c985-filtration":
        raise SystemExit(c985_filtration(pretty=args.pretty))
    if args.command == "c985-nerve":
        raise SystemExit(c985_nerve(pretty=args.pretty))
    if args.command == "c985-chart-atlas":
        raise SystemExit(c985_chart_atlas(pretty=args.pretty))
    if args.command == "c985-transition-groupoid":
        raise SystemExit(c985_transition_groupoid(pretty=args.pretty))
    if args.command == "c985-normal-words":
        raise SystemExit(c985_normal_words(pretty=args.pretty))
    if args.command == "c985-symbolic-rewrites":
        raise SystemExit(c985_symbolic_rewrites(pretty=args.pretty))
    if args.command == "c985-symbolic-associativity":
        raise SystemExit(c985_symbolic_associativity(pretty=args.pretty))
    if args.command == "c985-rewrite-complex":
        raise SystemExit(c985_rewrite_complex(pretty=args.pretty))
    if args.command == "c985-interval-sheaf":
        raise SystemExit(c985_interval_sheaf(pretty=args.pretty))
    if args.command == "c985-preserved-core":
        raise SystemExit(c985_preserved_core(pretty=args.pretty))
    if args.command == "c985-chamber-spine":
        raise SystemExit(c985_chamber_spine(pretty=args.pretty))
    if args.command == "c985-morse-reeb":
        raise SystemExit(c985_morse_reeb(pretty=args.pretty))
    if args.command == "c985-boundary-transfer":
        raise SystemExit(c985_boundary_transfer(pretty=args.pretty))
    if args.command == "c985-atom-flow":
        raise SystemExit(c985_atom_flow(pretty=args.pretty))
    if args.command == "c985-signature-subboundary":
        raise SystemExit(c985_signature_subboundary(pretty=args.pretty))
    if args.command == "c985-signature-transfer":
        raise SystemExit(c985_signature_transfer(pretty=args.pretty))
    if args.command == "c985-signature-spectral-cut":
        raise SystemExit(c985_signature_spectral_cut(pretty=args.pretty))
    if args.command == "c985-signature-quotient":
        raise SystemExit(c985_signature_quotient(pretty=args.pretty))
    if args.command == "c985-signature-geometry":
        raise SystemExit(c985_signature_geometry(pretty=args.pretty))
    if args.command == "c985-signature-geodesic":
        raise SystemExit(c985_signature_geodesic(pretty=args.pretty))
    if args.command == "c985-signature-residual-chart":
        raise SystemExit(c985_signature_residual_chart(pretty=args.pretty))
    if args.command == "c985-signature-cell-complex":
        raise SystemExit(c985_signature_cell_complex(pretty=args.pretty))
    if args.command == "c985-signature-boundary-flux":
        raise SystemExit(c985_signature_boundary_flux(pretty=args.pretty))
    if args.command == "c985-signature-boundary-rates":
        raise SystemExit(c985_signature_boundary_rates(pretty=args.pretty))
    if args.command == "c985-signature-conductance-spine":
        raise SystemExit(c985_signature_conductance_spine(pretty=args.pretty))
    if args.command == "c985-signature-spine-poincare":
        raise SystemExit(c985_signature_spine_poincare(pretty=args.pretty))
    if args.command == "c985-signature-routing-prefix":
        raise SystemExit(c985_signature_routing_prefix(pretty=args.pretty))
    if args.command == "c985-signature-branching-law":
        raise SystemExit(c985_signature_branching_law(pretty=args.pretty))
    if args.command == "c985-signature-typed-corridors":
        raise SystemExit(c985_signature_typed_corridors(pretty=args.pretty))
    if args.command == "c985-signature-gate-automaton":
        raise SystemExit(c985_signature_gate_automaton(pretty=args.pretty))
    if args.command == "c985-signature-language-graph":
        raise SystemExit(c985_signature_language_graph(pretty=args.pretty))
    if args.command == "c985-signature-aperture-fan":
        raise SystemExit(c985_signature_aperture_fan(pretty=args.pretty))
    if args.command == "c985-signature-aperture-insertion":
        raise SystemExit(c985_signature_aperture_insertion(pretty=args.pretty))
    if args.command == "c985-signature-x2-splice":
        raise SystemExit(c985_signature_x2_splice(pretty=args.pretty))
    if args.command == "c985-signature-x2-detour":
        raise SystemExit(c985_signature_x2_detour(pretty=args.pretty))
    if args.command == "c985-signature-x2-clean-detour":
        raise SystemExit(c985_signature_x2_clean_detour(pretty=args.pretty))
    if args.command == "c985-signature-x2-x4-aperture":
        raise SystemExit(c985_signature_x2_x4_aperture(pretty=args.pretty))
    if args.command == "c985-signature-aperture-cycle":
        raise SystemExit(c985_signature_aperture_cycle(pretty=args.pretty))
    if args.command == "c985-signature-aperture-cycle-ranking":
        raise SystemExit(c985_signature_aperture_cycle_ranking(pretty=args.pretty))
    if args.command == "c985-signature-aperture-cycle-pareto":
        raise SystemExit(c985_signature_aperture_cycle_pareto(pretty=args.pretty))
    if args.command == "c985-signature-aperture-mixed-contact":
        raise SystemExit(c985_signature_aperture_mixed_contact(pretty=args.pretty))
    if args.command == "c985-signature-aperture-atom-selector":
        raise SystemExit(c985_signature_aperture_atom_selector(pretty=args.pretty))
    if args.command == "c985-signature-aperture-atom-tradeoff":
        raise SystemExit(c985_signature_aperture_atom_tradeoff(pretty=args.pretty))
    if args.command == "c985-signature-aperture-tail-hybrid":
        raise SystemExit(c985_signature_aperture_tail_hybrid(pretty=args.pretty))
    if args.command == "c985-signature-aperture-bounded-backtrack":
        raise SystemExit(c985_signature_aperture_bounded_backtrack(pretty=args.pretty))
    if args.command == "c985-signature-aperture-symbol-state":
        raise SystemExit(c985_signature_aperture_symbol_state(pretty=args.pretty))
    if args.command == "c985-signature-aperture-overhead2-carrier":
        raise SystemExit(c985_signature_aperture_overhead2_carrier(pretty=args.pretty))
    if args.command == "c985-signature-aperture-overhead2-repair":
        raise SystemExit(c985_signature_aperture_overhead2_repair(pretty=args.pretty))
    if args.command == "c985-signature-aperture-overhead2-tail":
        raise SystemExit(c985_signature_aperture_overhead2_tail(pretty=args.pretty))
    if args.command == "c985-signature-aperture-overhead2-cycle-rank":
        raise SystemExit(c985_signature_aperture_overhead2_cycle_rank(pretty=args.pretty))
    if args.command == "c985-signature-aperture-overhead3-trace-quotient":
        raise SystemExit(c985_signature_aperture_overhead3_trace_quotient(pretty=args.pretty))
    if args.command == "c985-signature-aperture-rank104-audit":
        raise SystemExit(c985_signature_aperture_rank104_audit(pretty=args.pretty))
    if args.command == "c985-signature-aperture-overhead3-weak-promotion":
        raise SystemExit(c985_signature_aperture_overhead3_weak_promotion(pretty=args.pretty))
    if args.command == "c985-signature-aperture-overhead3-strongification-gap":
        raise SystemExit(c985_signature_aperture_overhead3_strongification_gap(pretty=args.pretty))
    if args.command == "c985-signature-aperture-rank104-strongification-geometry":
        raise SystemExit(
            c985_signature_aperture_rank104_strongification_geometry(pretty=args.pretty)
        )
    if args.command == "c985-signature-aperture-cost3-strongification-ranking":
        raise SystemExit(
            c985_signature_aperture_cost3_strongification_ranking(pretty=args.pretty)
        )
    if args.command == "c985-signature-aperture-closure-outlier-geometry":
        raise SystemExit(
            c985_signature_aperture_closure_outlier_geometry(pretty=args.pretty)
        )
    if args.command == "c985-signature-aperture-closure-tail-endpoint-split":
        raise SystemExit(
            c985_signature_aperture_closure_tail_endpoint_split(pretty=args.pretty)
        )
    if args.command == "c985-signature-aperture-closure-tail-rewrite-lift":
        raise SystemExit(
            c985_signature_aperture_closure_tail_rewrite_lift(pretty=args.pretty)
        )
    if args.command == "c985-signature-aperture-closure-tail-prefix-chord":
        raise SystemExit(
            c985_signature_aperture_closure_tail_prefix_chord(pretty=args.pretty)
        )
    if args.command == "c985-signature-aperture-closure-tail-carrier-splice":
        raise SystemExit(
            c985_signature_aperture_closure_tail_carrier_splice(pretty=args.pretty)
        )
    if args.command == "c985-signature-aperture-closure-tail-splice-optimality":
        raise SystemExit(
            c985_signature_aperture_closure_tail_splice_optimality(
                pretty=args.pretty
            )
        )
    if args.command == "c985-signature-aperture-closure-tail-lower-lift":
        raise SystemExit(
            c985_signature_aperture_closure_tail_lower_lift(pretty=args.pretty)
        )
    if args.command == "c985-signature-aperture-closure-tail-partial-splitter":
        raise SystemExit(
            c985_signature_aperture_closure_tail_partial_splitter(
                pretty=args.pretty
            )
        )
    if args.command == "c985-signature-aperture-closure-tail-trim-neighborhood":
        raise SystemExit(
            c985_signature_aperture_closure_tail_trim_neighborhood(
                pretty=args.pretty
            )
        )
    if args.command == "c985-signature-aperture-closure-tail-clear-corridor":
        raise SystemExit(
            c985_signature_aperture_closure_tail_clear_corridor(pretty=args.pretty)
        )
    if args.command == "c985-signature-aperture-closure-tail-clear-corridor-level2":
        raise SystemExit(
            c985_signature_aperture_closure_tail_clear_corridor_level2(
                pretty=args.pretty
            )
        )
    if args.command == "c985-signature-aperture-closure-tail-gate-repair":
        raise SystemExit(
            c985_signature_aperture_closure_tail_gate_repair(pretty=args.pretty)
        )
    if args.command == "c985-signature-aperture-closure-tail-boundary-bridge":
        raise SystemExit(
            c985_signature_aperture_closure_tail_boundary_bridge(pretty=args.pretty)
        )
    if args.command == "c985-signature-aperture-closure-tail-virtual-graft":
        raise SystemExit(
            c985_signature_aperture_closure_tail_virtual_graft(pretty=args.pretty)
        )
    if args.command == "c985-signature-aperture-closure-tail-native-insertion":
        raise SystemExit(
            c985_signature_aperture_closure_tail_native_insertion(pretty=args.pretty)
        )
    if args.command == "c985-signature-aperture-closure-tail-symbolic-window":
        raise SystemExit(
            c985_signature_aperture_closure_tail_symbolic_window(pretty=args.pretty)
        )
    if args.command == "c985-signature-aperture-closure-tail-skip-window-grammar":
        raise SystemExit(
            c985_signature_aperture_closure_tail_skip_window_grammar(
                pretty=args.pretty
            )
        )
    if args.command == "c985-signature-aperture-closure-tail-repaired-automaton":
        raise SystemExit(
            c985_signature_aperture_closure_tail_repaired_automaton(
                pretty=args.pretty
            )
        )
    if args.command == "c985-signature-aperture-closure-tail-transfer":
        raise SystemExit(
            c985_signature_aperture_closure_tail_transfer(pretty=args.pretty)
        )
    if args.command == "c985-signature-aperture-closure-tail-flow-window":
        raise SystemExit(
            c985_signature_aperture_closure_tail_flow_window(pretty=args.pretty)
        )
    if args.command == "c985-signature-aperture-closure-tail-promoted-window":
        raise SystemExit(
            c985_signature_aperture_closure_tail_promoted_window(pretty=args.pretty)
        )
    if args.command == "c985-signature-aperture-closure-tail-promoted-transfer":
        raise SystemExit(
            c985_signature_aperture_closure_tail_promoted_transfer(pretty=args.pretty)
        )
    if args.command == "c985-signature-aperture-closure-tail-second-window":
        raise SystemExit(
            c985_signature_aperture_closure_tail_second_window(pretty=args.pretty)
        )
    if args.command == "c985-signature-aperture-closure-tail-second-window-promotion":
        raise SystemExit(
            c985_signature_aperture_closure_tail_second_window_promotion(
                pretty=args.pretty
            )
        )
    if args.command == "c985-signature-aperture-closure-tail-second-window-transfer":
        raise SystemExit(
            c985_signature_aperture_closure_tail_second_window_transfer(
                pretty=args.pretty
            )
        )
    if args.command == "c985-signature-aperture-closure-tail-sixj-frame":
        raise SystemExit(
            c985_signature_aperture_closure_tail_sixj_frame(pretty=args.pretty)
        )
    if args.command == "c985-signature-aperture-closure-tail-sixj-recoupling-pair":
        raise SystemExit(
            c985_signature_aperture_closure_tail_sixj_recoupling_pair(
                pretty=args.pretty
            )
        )
    if args.command == "c985-signature-aperture-closure-tail-sixj-recoupling-triple":
        raise SystemExit(
            c985_signature_aperture_closure_tail_sixj_recoupling_triple(
                pretty=args.pretty
            )
        )
    if args.command == "c985-signature-aperture-closure-tail-sixj-recoupling-closure":
        raise SystemExit(
            c985_signature_aperture_closure_tail_sixj_recoupling_closure(
                pretty=args.pretty
            )
        )
    if args.command == "c985-signature-aperture-closure-tail-sixj-nonlocal-screen":
        raise SystemExit(
            c985_signature_aperture_closure_tail_sixj_nonlocal_screen(
                pretty=args.pretty
            )
        )
    if args.command == "c985-signature-aperture-closure-tail-sixj-borromean-hypergraph":
        raise SystemExit(
            c985_signature_aperture_closure_tail_sixj_borromean_hypergraph(
                pretty=args.pretty
            )
        )
    if args.command == "c985-signature-aperture-closure-tail-sixj-conductance-preservation":
        raise SystemExit(
            c985_signature_aperture_closure_tail_sixj_conductance_preservation(
                pretty=args.pretty
            )
        )
    if args.command == "c985-signature-aperture-closure-tail-eta6-charge":
        raise SystemExit(
            c985_signature_aperture_closure_tail_eta6_charge(
                pretty=args.pretty
            )
        )
    if args.command == "c985-signature-aperture-closure-tail-eta6-holonomy":
        raise SystemExit(
            c985_signature_aperture_closure_tail_eta6_holonomy(
                pretty=args.pretty
            )
        )
    if args.command == "c985-signature-aperture-closure-tail-eta6-dini-torsion":
        raise SystemExit(
            c985_signature_aperture_closure_tail_eta6_dini_torsion(
                pretty=args.pretty
            )
        )
    if args.command == "c985-signature-aperture-closure-tail-eta6-h4-precursor":
        raise SystemExit(
            c985_signature_aperture_closure_tail_eta6_h4_precursor(
                pretty=args.pretty
            )
        )
    if args.command == "c985-signature-aperture-closure-tail-eta6-graham-throat":
        raise SystemExit(
            c985_signature_aperture_closure_tail_eta6_graham_throat(
                pretty=args.pretty
            )
        )
    if args.command == "c985-signature-aperture-closure-tail-eta6-aperture-polygon":
        raise SystemExit(
            c985_signature_aperture_closure_tail_eta6_aperture_polygon(
                pretty=args.pretty
            )
        )
    if args.command == "c985-signature-aperture-closure-tail-eta6-truncated-skeleton":
        raise SystemExit(
            c985_signature_aperture_closure_tail_eta6_truncated_skeleton(
                pretty=args.pretty
            )
        )
    if args.command == "c985-signature-aperture-closure-tail-eta6-hex-face-barycenter":
        raise SystemExit(
            c985_signature_aperture_closure_tail_eta6_hex_face_barycenter(
                pretty=args.pretty
            )
        )
    if args.command == "c985-signature-aperture-closure-tail-eta6-nonholonomic-aperture":
        raise SystemExit(
            c985_signature_aperture_closure_tail_eta6_nonholonomic_aperture(
                pretty=args.pretty
            )
        )
    if args.command == "eta6-ext-cone":
        raise SystemExit(
            c985_signature_aperture_closure_tail_eta6_exterior_cone(
                pretty=args.pretty
            )
        )
    if args.command == "eta6-gordan":
        raise SystemExit(eta6_gordan(pretty=args.pretty))
    if args.command == "eta6-aext":
        raise SystemExit(eta6_aext(pretty=args.pretty))
    if args.command == "eta6-srows":
        raise SystemExit(eta6_srows(pretty=args.pretty))
    if args.command == "eta6-islack":
        raise SystemExit(eta6_islack(pretty=args.pretty))
    if args.command == "eta6-hpol":
        raise SystemExit(eta6_hpol(pretty=args.pretty))
    if args.command == "eta6-surg":
        raise SystemExit(eta6_surg(pretty=args.pretty))
    if args.command == "eta6-repl":
        raise SystemExit(eta6_repl(pretty=args.pretty))
    if args.command == "eta6-xfer":
        raise SystemExit(eta6_xfer(pretty=args.pretty))
    if args.command == "eta6-hit2":
        raise SystemExit(eta6_hit2(pretty=args.pretty))
    if args.command == "eta6-gap":
        raise SystemExit(eta6_gap(pretty=args.pretty))
    if args.command == "eta6-p2":
        raise SystemExit(eta6_p2(pretty=args.pretty))
    if args.command == "eta6-t2":
        raise SystemExit(eta6_t2(pretty=args.pretty))
    if args.command == "eta6-f4":
        raise SystemExit(eta6_f4(pretty=args.pretty))
    if args.command == "eta6-p5":
        raise SystemExit(eta6_p5(pretty=args.pretty))
    if args.command == "eta6-p6":
        raise SystemExit(eta6_p6(pretty=args.pretty))
    if args.command == "eta6-p7":
        raise SystemExit(eta6_p7(pretty=args.pretty))
    if args.command == "eta6-p8":
        raise SystemExit(eta6_p8(pretty=args.pretty))
    if args.command == "eta6-p9":
        raise SystemExit(eta6_p9(pretty=args.pretty))
    if args.command == "eta6-p10":
        raise SystemExit(eta6_p10(pretty=args.pretty))
    if args.command == "eta6-p11":
        raise SystemExit(eta6_p11(pretty=args.pretty))
    if args.command == "eta6-p12":
        raise SystemExit(eta6_p12(pretty=args.pretty))
    if args.command == "eta6-p13":
        raise SystemExit(eta6_p13(pretty=args.pretty))
    if args.command == "eta6-p14":
        raise SystemExit(eta6_p14(pretty=args.pretty))
    if args.command == "eta6-p15":
        raise SystemExit(eta6_p15(pretty=args.pretty))
    if args.command == "eta6-p16":
        raise SystemExit(eta6_p16(pretty=args.pretty))
    if args.command == "eta6-p17":
        raise SystemExit(eta6_p17(pretty=args.pretty))
    if args.command == "eta6-p18":
        raise SystemExit(eta6_p18(pretty=args.pretty))
    if args.command == "eta6-p19":
        raise SystemExit(eta6_p19(pretty=args.pretty))
    if args.command == "eta6-p20":
        raise SystemExit(eta6_p20(pretty=args.pretty))
    if args.command == "eta6-p21":
        raise SystemExit(eta6_p21(pretty=args.pretty))
    if args.command == "eta6-p22":
        raise SystemExit(eta6_p22(pretty=args.pretty))
    if args.command == "eta6-p23":
        raise SystemExit(eta6_p23(pretty=args.pretty))
    if args.command == "eta6-p24":
        raise SystemExit(eta6_p24(pretty=args.pretty))
    if args.command == "eta6-p25":
        raise SystemExit(eta6_p25(pretty=args.pretty))
    if args.command == "eta6-p26":
        raise SystemExit(eta6_p26(pretty=args.pretty))
    if args.command == "eta6-p27":
        raise SystemExit(eta6_p27(pretty=args.pretty))
    if args.command == "eta6-p28":
        raise SystemExit(eta6_p28(pretty=args.pretty))
    if args.command == "eta6-p29":
        raise SystemExit(eta6_p29(pretty=args.pretty))
    if args.command == "eta6-p30":
        raise SystemExit(eta6_p30(pretty=args.pretty))
    if args.command == "eta6-p31":
        raise SystemExit(eta6_p31(pretty=args.pretty))
    if args.command == "eta6-p32":
        raise SystemExit(eta6_p32(pretty=args.pretty))
    if args.command == "eta6-p33":
        raise SystemExit(eta6_p33(pretty=args.pretty))
    if args.command == "eta6-p34":
        raise SystemExit(eta6_p34(pretty=args.pretty))
    if args.command == "eta6-p35":
        raise SystemExit(eta6_p35(pretty=args.pretty))
    if args.command == "eta6-p36":
        raise SystemExit(eta6_p36(pretty=args.pretty))
    if args.command == "eta6-p37":
        raise SystemExit(eta6_p37(pretty=args.pretty))
    if args.command == "eta6-p38":
        raise SystemExit(eta6_p38(pretty=args.pretty))
    if args.command == "eta6-p39":
        raise SystemExit(eta6_p39(pretty=args.pretty))
    if args.command == "eta6-p40":
        raise SystemExit(eta6_p40(pretty=args.pretty))
    if args.command == "eta6-core":
        raise SystemExit(eta6_core(pretty=args.pretty))
    if args.command == "long-lln":
        raise SystemExit(long_lln(pretty=args.pretty))
    if args.command == "long-kern":
        raise SystemExit(long_kern(pretty=args.pretty))
    if args.command == "long-tri":
        raise SystemExit(long_tri(pretty=args.pretty))
    if args.command == "long-basis":
        raise SystemExit(long_basis(pretty=args.pretty))
    if args.command == "long-rec":
        raise SystemExit(long_rec(pretty=args.pretty))
    if args.command == "long-eta":
        raise SystemExit(long_eta(pretty=args.pretty))
    if args.command == "long-eta2":
        raise SystemExit(long_eta2(pretty=args.pretty))
    if args.command == "long-lap":
        raise SystemExit(long_lap(pretty=args.pretty))
    if args.command == "long-cut":
        raise SystemExit(long_cut(pretty=args.pretty))
    if args.command == "long-flow":
        raise SystemExit(long_flow(pretty=args.pretty))
    if args.command == "long-absorb":
        raise SystemExit(long_absorb(pretty=args.pretty))
    if args.command == "long-spec":
        raise SystemExit(long_spec(pretty=args.pretty))
    if args.command == "long-markov":
        raise SystemExit(long_markov(pretty=args.pretty))
    if args.command == "long-dev":
        raise SystemExit(long_dev(pretty=args.pretty))
    if args.command == "long-prof":
        raise SystemExit(long_prof(pretty=args.pretty))
    if args.command == "long-rate":
        raise SystemExit(long_rate(pretty=args.pretty))
    if args.command == "long-conv":
        raise SystemExit(long_conv(pretty=args.pretty))
    if args.command == "long-cls":
        raise SystemExit(long_cls(pretty=args.pretty))
    if args.command == "long-univ":
        raise SystemExit(long_univ(pretty=args.pretty))
    if args.command == "long-min":
        raise SystemExit(long_min(pretty=args.pretty))
    if args.command == "long-nat":
        raise SystemExit(long_nat(pretty=args.pretty))
    if args.command == "long-hlim":
        raise SystemExit(long_hlim(pretty=args.pretty))
    if args.command == "long-ext":
        raise SystemExit(long_ext(pretty=args.pretty))
    if args.command == "long-obj":
        raise SystemExit(long_obj(pretty=args.pretty))
    if args.command == "long-tens":
        raise SystemExit(long_tens(pretty=args.pretty))
    if args.command == "long-lift":
        raise SystemExit(long_lift(pretty=args.pretty))
    if args.command == "long-raw":
        raise SystemExit(long_raw(pretty=args.pretty))
    if args.command == "long-h16":
        raise SystemExit(long_h16(pretty=args.pretty))
    if args.command == "long-path":
        raise SystemExit(long_path(pretty=args.pretty))
    if args.command == "long-comp":
        raise SystemExit(long_comp(pretty=args.pretty))
    if args.command == "long-sheaf":
        raise SystemExit(long_sheaf(pretty=args.pretty))
    if args.command == "long-all":
        raise SystemExit(long_all(pretty=args.pretty))
    if args.command == "long-orient":
        raise SystemExit(long_orient(pretty=args.pretty))
    if args.command == "long-dual":
        raise SystemExit(long_dual(pretty=args.pretty))
    if args.command == "long-prob":
        raise SystemExit(long_prob(pretty=args.pretty))
    if args.command == "long-mart":
        raise SystemExit(long_mart(pretty=args.pretty))
    if args.command == "long-stop":
        raise SystemExit(long_stop(pretty=args.pretty))
    if args.command == "long-dlim":
        raise SystemExit(long_dlim(pretty=args.pretty))
    if args.command == "long-linf":
        raise SystemExit(long_linf(pretty=args.pretty))
    if args.command == "long-ind":
        raise SystemExit(long_ind(pretty=args.pretty))
    if args.command == "long-suppind":
        raise SystemExit(long_suppind(pretty=args.pretty))
    if args.command == "long-recind":
        raise SystemExit(long_recind(pretty=args.pretty))
    if args.command == "long-formind":
        raise SystemExit(long_formind(pretty=args.pretty))
    if args.command == "long-domind":
        raise SystemExit(long_domind(pretty=args.pretty))
    if args.command == "long-gapind":
        raise SystemExit(long_gapind(pretty=args.pretty))
    if args.command == "long-llnind":
        raise SystemExit(long_llnind(pretty=args.pretty))
    if args.command == "long-thm":
        raise SystemExit(long_thm(pretty=args.pretty))
    if args.command == "long-inv":
        raise SystemExit(long_inv(pretty=args.pretty))
    if args.command == "long-inv-exhaust":
        raise SystemExit(long_inv_exhaust(pretty=args.pretty))
    if args.command == "long-anom":
        raise SystemExit(long_anom(pretty=args.pretty))
    if args.command == "long-mat":
        raise SystemExit(long_mat(pretty=args.pretty))
    if args.command == "long-auto":
        raise SystemExit(long_auto(pretty=args.pretty))
    if args.command == "long-orac":
        raise SystemExit(long_orac(pretty=args.pretty))
    if args.command == "long-ctor":
        raise SystemExit(long_ctor(pretty=args.pretty))
    if args.command == "long-gr":
        raise SystemExit(long_gr(pretty=args.pretty))
    if args.command == "long-lor":
        raise SystemExit(long_lor(pretty=args.pretty))
    if args.command == "long-time-map":
        raise SystemExit(long_time_map(pretty=args.pretty))
    if args.command == "long-time-sem":
        raise SystemExit(long_time_sem(pretty=args.pretty))
    if args.command == "long-metric-gate":
        raise SystemExit(long_metric_gate(pretty=args.pretty))
    if args.command == "long-contact-lift":
        raise SystemExit(long_contact_lift(pretty=args.pretty))
    if args.command == "long-transition-sem":
        raise SystemExit(long_transition_sem(pretty=args.pretty))
    if args.command == "long-stress20":
        raise SystemExit(long_stress20(pretty=args.pretty))
    if args.command == "long-stress-gate":
        raise SystemExit(long_stress_gate(pretty=args.pretty))
    if args.command == "long-stress-couple":
        raise SystemExit(long_stress_couple(pretty=args.pretty))
    if args.command == "long-semstress":
        raise SystemExit(long_semstress(pretty=args.pretty))
    if args.command == "long-metric-rank-gate":
        raise SystemExit(long_metric_rank_gate(pretty=args.pretty))
    if args.command == "long-dim4-gate":
        raise SystemExit(long_dim4_gate(pretty=args.pretty))
    if args.command == "long-rim":
        raise SystemExit(long_rim(pretty=args.pretty))
    if args.command == "long-rim-select":
        raise SystemExit(long_rim_select(pretty=args.pretty))
    if args.command == "long-sel":
        raise SystemExit(long_sel(pretty=args.pretty))
    if args.command == "long-psel":
        raise SystemExit(long_psel(pretty=args.pretty))
    if args.command == "long-pax":
        raise SystemExit(long_pax(pretty=args.pretty))
    if args.command == "long-l63":
        raise SystemExit(long_l63(pretty=args.pretty))
    if args.command == "long-f63":
        raise SystemExit(long_f63(pretty=args.pretty))
    if args.command == "long-frim":
        raise SystemExit(long_frim(pretty=args.pretty))
    if args.command == "long-sfork":
        raise SystemExit(long_sfork(pretty=args.pretty))
    if args.command == "long-glaw":
        raise SystemExit(long_glaw(pretty=args.pretty))
    if args.command == "long-gclk":
        raise SystemExit(long_gclk(pretty=args.pretty))
    if args.command == "long-tlift":
        raise SystemExit(long_tlift(pretty=args.pretty))
    if args.command == "long-abmap":
        raise SystemExit(long_abmap(pretty=args.pretty))
    if args.command == "long-rtick":
        raise SystemExit(long_rtick(pretty=args.pretty))
    if args.command == "long-rsem":
        raise SystemExit(long_rsem(pretty=args.pretty))
    if args.command == "long-oprom":
        raise SystemExit(long_oprom(pretty=args.pretty))
    if args.command == "long-c60op":
        raise SystemExit(long_c60op(pretty=args.pretty))
    if args.command == "long-c60negf":
        raise SystemExit(long_c60negf(pretty=args.pretty))
    if args.command == "long-c59x":
        raise SystemExit(long_c59x(pretty=args.pretty))
    if args.command == "long-c59e":
        raise SystemExit(long_c59e(pretty=args.pretty))
    if args.command == "long-c59cf":
        raise SystemExit(long_c59cf(pretty=args.pretty))
    if args.command == "long-c59st":
        raise SystemExit(long_c59st(pretty=args.pretty))
    if args.command == "long-c59kt":
        raise SystemExit(long_c59kt(pretty=args.pretty))
    if args.command == "long-c59q":
        raise SystemExit(long_c59q(pretty=args.pretty))
    if args.command == "long-c59pk":
        raise SystemExit(long_c59pk(pretty=args.pretty))
    if args.command == "long-c59s3":
        raise SystemExit(long_c59s3(pretty=args.pretty))
    if args.command == "long-c59np3":
        raise SystemExit(long_c59np3(pretty=args.pretty))
    if args.command == "long-c59p3s":
        raise SystemExit(long_c59p3s(pretty=args.pretty))
    if args.command == "long-c59p3v":
        raise SystemExit(long_c59p3v(pretty=args.pretty))
    if args.command == "long-c59p3o":
        raise SystemExit(long_c59p3o(pretty=args.pretty))
    if args.command == "long-c59p3a":
        raise SystemExit(long_c59p3a(pretty=args.pretty))
    if args.command == "long-c59p3t":
        raise SystemExit(long_c59p3t(pretty=args.pretty))
    if args.command == "long-c59p3b":
        raise SystemExit(long_c59p3b(pretty=args.pretty))
    if args.command == "long-c59p3r":
        raise SystemExit(long_c59p3r(pretty=args.pretty))
    if args.command == "long-c59p3i":
        raise SystemExit(long_c59p3i(pretty=args.pretty))
    if args.command == "long-c59p3f":
        raise SystemExit(long_c59p3f(pretty=args.pretty))
    if args.command == "long-c59p3u":
        raise SystemExit(long_c59p3u(pretty=args.pretty))
    if args.command == "long-c59p3w":
        raise SystemExit(long_c59p3w(pretty=args.pretty))
    if args.command == "long-c59p3c":
        raise SystemExit(long_c59p3c(pretty=args.pretty))
    if args.command == "long-c59p3d":
        raise SystemExit(long_c59p3d(pretty=args.pretty))
    if args.command == "long-c59p3e":
        raise SystemExit(long_c59p3e(pretty=args.pretty))
    if args.command == "long-c59p3g":
        raise SystemExit(long_c59p3g(pretty=args.pretty))
    if args.command == "long-c59p3h":
        raise SystemExit(long_c59p3h(pretty=args.pretty))
    if args.command == "long-c59p3j":
        raise SystemExit(long_c59p3j(pretty=args.pretty))
    if args.command == "long-c59p3k":
        raise SystemExit(long_c59p3k(pretty=args.pretty))
    if args.command == "long-c59p3m":
        raise SystemExit(long_c59p3m(pretty=args.pretty))
    if args.command == "long-c59p3n":
        raise SystemExit(long_c59p3n(pretty=args.pretty))
    if args.command == "long-frontier":
        raise SystemExit(long_frontier(pretty=args.pretty))
    if args.command == "long-cluster":
        raise SystemExit(long_cluster(pretty=args.pretty))
    if args.command == "long-c2uf":
        raise SystemExit(long_c2uf(pretty=args.pretty))
    if args.command == "long-hcinv":
        raise SystemExit(long_hcinv(pretty=args.pretty))
    if args.command == "long-hcfoam":
        raise SystemExit(long_hcfoam(pretty=args.pretty))
    if args.command == "long-hcpi":
        raise SystemExit(long_hcpi(pretty=args.pretty))
    if args.command == "long-hcshape":
        raise SystemExit(long_hcshape(pretty=args.pretty))
    if args.command == "long-hcscalar":
        raise SystemExit(long_hcscalar(pretty=args.pretty))
    if args.command == "long-hcsupp":
        raise SystemExit(long_hcsupp(pretty=args.pretty))
    if args.command == "long-hcbasis":
        raise SystemExit(long_hcbasis(pretty=args.pretty))
    if args.command == "long-hcgrade":
        raise SystemExit(long_hcgrade(pretty=args.pretty))
    if args.command == "long-hcperm":
        raise SystemExit(long_hcperm(pretty=args.pretty))
    if args.command == "long-k23":
        raise SystemExit(long_k23(pretty=args.pretty))
    if args.command == "long-k23oct":
        raise SystemExit(long_k23oct(pretty=args.pretty))
    if args.command == "long-k23row":
        raise SystemExit(long_k23row(pretty=args.pretty))
    if args.command == "long-k23max":
        raise SystemExit(long_k23max(pretty=args.pretty))
    if args.command == "long-psec":
        raise SystemExit(long_psec(pretty=args.pretty))
    if args.command == "long-binc":
        raise SystemExit(long_binc(pretty=args.pretty))
    if args.command == "long-krein":
        raise SystemExit(long_krein(pretty=args.pretty))
    if args.command == "long-kr39":
        raise SystemExit(long_kr39(pretty=args.pretty))
    if args.command == "long-b3mod":
        raise SystemExit(long_b3mod(pretty=args.pretty))
    if args.command == "long-b3alg":
        raise SystemExit(long_b3alg(pretty=args.pretty))
    if args.command == "long-gchar":
        raise SystemExit(long_gchar(pretty=args.pretty))
    if args.command == "a985-direct-packet-bridge":
        raise SystemExit(a985_direct_packet_bridge(pretty=args.pretty))
    if args.command == "a985-mat2-hom-boundary":
        raise SystemExit(a985_mat2_hom_boundary(pretty=args.pretty))
    if args.command == "a985-labelled-nonfaithful-packet-hom":
        raise SystemExit(a985_labelled_nonfaithful_packet_hom(pretty=args.pretty))
    if args.command == "long-pobj":
        raise SystemExit(long_pobj(pretty=args.pretty))
    if args.command == "long-paths":
        raise SystemExit(long_paths(pretty=args.pretty))
    if args.command == "long-measure":
        raise SystemExit(long_measure(pretty=args.pretty))
    if args.command == "c985-signature-aperture-closure-tail-sixj-2114-neighborhood":
        raise SystemExit(
            c985_signature_aperture_closure_tail_sixj_2114_neighborhood(
                pretty=args.pretty
            )
        )
    if args.command == "c985-signature-aperture-closure-tail-sixj-2114-triple":
        raise SystemExit(
            c985_signature_aperture_closure_tail_sixj_2114_triple(
                pretty=args.pretty
            )
        )
    raise SystemExit(run(args.command, pretty=args.pretty))


if __name__ == "__main__":
    main()
