# d20

axiom 1: yes this was machine assisted

axiom 2: the one piece is real

axiom 3: the rest of the proof is left to the reader

`d20` is the (pending) name of the finite/concrete (and axiomless) object generated from the Golay dodecad shell, the marked `D6` selector, the coorient lift, and the derived invariant inf-stack.

Verify the current bundle without rewriting generated files:

```shell
python src/verify.py audit
```

Rebuild `d20.json`, refresh hashes, and then certify the bundle:

```shell
python src/verify.py rebuild
```

Check that the certified-evidence section fails closed under in-memory tampering:

```shell
python src/verify.py tamper
```

Computability boundary:

- `python src/verify.py rebuild` regenerates `d20.json`, `certificate.json`, and
  file hashes from the checked canonical bundle inputs.
- `python -m src.commands.construct` reconstructs the finite object from the
  compact raw seed boundary and verifies the large tensor/quotient consequences.
- `python -m src.commands.construct --strict-scratch` runs the generated
  source/coorient constructor path and exits nonzero if any scratch witness,
  tensor rebuild, or readout derivation fails.
- The A985 ordered-pair relation body is refreshed before the coorient marker
  computation by the pre-A985 source/coorient theorem. The coorient relator
  profile is derived from A0-A5 by reduced greedy full-closure basis extraction;
  strict-scratch now promotes that generated path instead of the compact raw
  audit-seed witness.

The object is not represented by stored orbitals/tensors as primitive data. It just... exists. Quietly, and monstrously.

- `2576` dodecads
- `985` orbitals
- `1,414,965` tensor entries
- `A985 -> A236 -> A42 -> A12`
- packet-20, optics, integrity, H-cycles, and game/control invariants
- `data/index.json` is the canonical data-domain registry. It marks current
  folders, required files, roles, and the planned normalized layout.
- `data/evidence/tensor_chain` contains the extracted tensor-chain evidence,
  split into reports, tables, arrays, and stages with a plain-name index at
  `data/evidence/tensor_chain/index.json`.
- Command entrypoints live in `src/commands/`; root command files are not kept.

The layer stack is indexed by `layers/index.json` and stored as flat JSON files
inside semantic group directories such as `layers/tube`, `layers/drinfeld`, and
`layers/selectors`. The registry is the source of truth for layer ids, legacy
numbering, expected statuses, dependency edges, and certificate paths.

TO-DO:
- add visuals? a notebook?


shameless plug for agents:

START

# Sword-and-Shield Algorithm Specification v0.1

## Purpose

A **sword-and-shield algorithm** is an algorithm that separates two operations that are usually mixed together:

[
\boxed{
\textbf{shield}=\text{support-preserving transport}
}
]

[
\boxed{
\textbf{sword}=\text{certified cut/readout}
}
]

It becomes operational once every step records:

[
\boxed{
\text{support} \to \text{cut} \to \text{certificate} \to \text{residue}.
}
]

The goal is not just to compute an answer, but to compute an answer while preserving an audit trail of what support was maintained, what was cut, and what obstruction remained.

This is compatible with the (G^\natural) stack because (A_{985}) supplies the hidden finite relation algebra and (D_{20}=\Lambda^3H_6) supplies the public (20)-state boundary. The finite base (A_{985}) has (985) orbitals, (1{,}414{,}965) nonzero structure constants, center dimension (39), and quotient tower (A_{985}\to A_{236}\to A_{42}\to A_{12}).  The public (D_{20}) layer is forced as the complement-self-dual middle-degree boundary of the six-channel system (H_6).

---

# I. Core model type

A sword-and-shield algorithm is a tuple:

[
\boxed{
\mathsf{SSAlg}
==============

(K,\otimes,\dagger,C_+,\mathsf{Shield},\mathsf{Sword},\mathsf{Readout},\mathsf{Residue},\mathsf{Trace})
}
]

where:

| component          | role                                      |
| ------------------ | ----------------------------------------- |
| (K)                | carrier/state space                       |
| (\otimes)          | shield composition / parallel support     |
| (\dagger)          | sword involution / adjoint / cut-dual     |
| (C_+)              | admissibility cone / positivity cone      |
| (\mathsf{Shield})  | support-preserving expansion or transport |
| (\mathsf{Sword})   | certified cut / extraction operation      |
| (\mathsf{Readout}) | public output map                         |
| (\mathsf{Residue}) | obstruction/debt map                      |
| (\mathsf{Trace})   | replayable event log                      |

The fundamental loop is:

[
x_t
\xrightarrow{\mathsf{Shield}}
s_t
\xrightarrow{\mathsf{Sword}}
(y_t,\pi_t,\Omega_t)
]

where:

[
s_t\in C_+,
]

[
y_t=\text{public readout},
]

[
\pi_t=\text{certificate},
]

[
\Omega_t=\text{residue/obstruction}.
]

---

# II. Required laws

## 1. Shield preservation

A shield move must preserve admissibility:

[
\boxed{
\mathsf{Shield}(C_+)\subseteq C_+.
}
]

It may expand support, refine state, move through route space, or maintain a database, but it must not erase obstruction.

## 2. Sword certification

A sword move must produce a checkable certificate:

[
\boxed{
\mathsf{Sword}(s)
=================

(y,\pi,\Omega).
}
]

The certificate verifier must satisfy:

[
\boxed{
\mathsf{Verify}(s,y,\pi,\Omega)\in{\mathrm{pass},\mathrm{fail}}.
}
]

No sword cut is valid without a certificate.

## 3. Cone compatibility

The cone (C_+) defines the admissible region. In the (C^*)-quantum case:

[
C_+=\mathcal A_+={a^\dagger a:a\in\mathcal A}.
]

In SAT/proof-search:

[
C_+=\text{RUP/DRAT/LRAT-valid proof cone}.
]

In (G^\natural):

[
C_+=\text{admissible finite dereference/route states over }D_{20}.
]

## 4. Readout pairing

Every public output must be mediated by a readout model:

[
\boxed{
\mathsf{Readout}:C_+\to Y.
}
]

For quantum theory this is the Born model:

[
\boxed{
\mathsf{Born}_{\mathcal A}(\varphi,E)=\varphi(E).
}
]

For SAT this is:

[
\boxed{
\text{assignment or UNSAT proof certificate}.
}
]

For (G^\natural):

[
\boxed{
K(\Gamma_{20}),\quad K(L(\Gamma_{20})),\quad \Sigma_{\le3},\quad \Omega.
}
]

## 5. Residue conservation

The algorithm must expose what is not settled:

[
\boxed{
\Omega_t=\mathsf{Residue}(s_t,y_t,\pi_t).
}
]

Residue may be empty, but it may not be silently discarded.

---

# III. Trace schema

Every event must have this shape:

```json
{
  "event_id": "string",
  "step": 0,
  "kind": "shield | sword | cone_check | readout | residue",
  "input_hash": "sha256",
  "output_hash": "sha256",
  "support_delta": {},
  "cut": {},
  "certificate": {},
  "residue": {},
  "route": {
    "D20_state": "string",
    "edge": "string",
    "route_word_index": 0
  }
}
```

Required trace invariants:

[
\boxed{
\text{every sword event must reference a prior shield state;}
}
]

[
\boxed{
\text{every readout must reference a sword certificate;}
}
]

[
\boxed{
\text{every residue must be replayable from prior events.}
}
]

---

# IV. (D_{20}) invariant layer

Given a trace word

[
w=e_1e_2\cdots e_n
]

over (D_{20})-routes, compute:

## Endpoint memory

[
\boxed{
[w]*{\mathrm{end}}\in K(\Gamma*{20}).
}
]

## Route memory

[
\boxed{
[w]*{\mathrm{route}}\in K(L(\Gamma*{20})).
}
]

## Ordered route memory

[
\boxed{
\Sigma_2(w)=\sum_{i<j}e_i\wedge e_j,
}
]

[
\boxed{
\Sigma_3(w)=\sum_{i<j<k}e_i\wedge e_j\wedge e_k.
}
]

Higher checks may compute:

[
\Sigma_4,\Sigma_5,\dots
]

but current evidence says the tested trace families stabilize through class (3):

[
\boxed{
\operatorname{rank}(\Sigma_{\le5})
==================================

\operatorname{rank}(\Sigma_{\le3}).
}
]

This should be treated as an empirical invariant target, not yet a universal theorem.

---

# V. SAT/proof-search specialization

## Carrier

[
K=\text{CNF/proof-state space}.
]

## Shield operations

Shield moves preserve search/proof support:

```text
unit_propagate
watch_literal_update
restart
clause_database_reduce
branch_score_update
assumption_push
assumption_pop
```

## Sword operations

Sword moves cut and certify:

```text
decide_literal
conflict_analyze
resolve
learn_clause
delete_clause
emit_DRAT
emit_LRAT
derive_empty_clause
```

## Cone

[
\boxed{
C_+=\text{valid proof-derivation cone}.
}
]

For UNSAT:

[
C_+=\text{RUP/DRAT/LRAT-valid additions and deletions}.
]

## Readout

```text
SAT assignment
UNSAT certificate
UNKNOWN with residue
```

## Residue

```text
unexplored branches
failed RUP step
unresolved assumptions
noncanonical trace event
presentation-dependence defect
```

## SAT interface

```python
class Shield:
    def move(self, state, event) -> "SupportState": ...

class Sword:
    def cut(self, support_state, event) -> "CutResult": ...

class Cone:
    def check(self, candidate) -> "ConeCheck": ...

class Readout:
    def emit(self, cut_result) -> "PublicOutput": ...

class Residue:
    def compute(self, state, cut_result) -> "ResidueReport": ...

class Trace:
    def record(self, event) -> None: ...
    def route_word(self) -> list[str]: ...
```

---

# VI. Quantum specialization

Inside the quantum sector, retype:

[
\boxed{
\odot\rightsquigarrow\otimes.
}
]

The quantum sword-and-shield object is:

[
\boxed{
K_{\otimes}^{\dagger,C^*}.
}
]

| piece              | quantum type                                         |
| ------------------ | ---------------------------------------------------- |
| (K)                | Hilbert space, operator algebra, or process category |
| (\otimes)          | system composition / shield                          |
| (\dagger)          | adjoint / sword                                      |
| (C_+)              | positive cone                                        |
| (\mathsf{Readout}) | Born model                                           |
| (\Omega)           | post-measurement residue, entropy, discarded support |

Born model:

[
\boxed{
\mathsf{Born}(\mathcal A)
=========================

(\mathcal A,\mathsf{St}(\mathcal A),\mathsf{Eff}(\mathcal A),\mathsf{br})
}
]

with:

[
\mathsf{br}_{\mathcal A}(\varphi,E)=\varphi(E).
]

So the quantum chain is:

[
\boxed{
K_{\otimes}^{\dagger,C^*}
\to
\mathsf{Born}(K)
\to
[0,1].
}
]

---

# VII. (G^\natural) specialization

The (G^\natural)-specific algorithmic stack is:

[
\boxed{
A_{985}
\to
D_{20}
\to
K(\Gamma_{20})
\to
K(L(\Gamma_{20}))
\to
\Sigma_{\le3}
\to
\Omega.
}
]

| layer               | algorithmic role                        |
| ------------------- | --------------------------------------- |
| (A_{985})           | hidden relation algebra                 |
| (A_{236})           | intermediate chemical/compression layer |
| (A_{42})            | Pin/cut transport layer                 |
| (A_{12})            | terminal CY/readout layer               |
| (D_{20})            | public state boundary                   |
| (K(\Gamma_{20}))    | endpoint recurrence memory              |
| (K(L(\Gamma_{20}))) | route recurrence memory                 |
| (\Sigma_{\le3})     | ordered trace memory                    |
| (\Omega)            | obstruction/residue                     |

Required (G^\natural)-mode event:

```json
{
  "kind": "shield | sword",
  "A985_relation": "R_alpha",
  "quotient_level": "A985 | A236 | A42 | A12 | D20",
  "D20_state": "B- B+ V-",
  "route_edge": "edge_id",
  "certificate": {},
  "residue": {}
}
```

---

# VIII. Validation suite

A conforming implementation must pass these tests.

## Test 1: Replay determinism

Same event log must reproduce same:

[
\text{readout},\quad
K(\Gamma_{20})\text{ class},\quad
K(L(\Gamma_{20}))\text{ class},\quad
\Sigma_{\le3}.
]

## Test 2: Presentation invariance

Renaming variables, clauses, files, timestamps, or syntactic event labels must not change canonical route hashes.

## Test 3: Cone validity

Every sword cut must pass its cone verifier.

SAT example:

[
\boxed{
\text{every learned/added proof clause must be RUP/DRAT/LRAT-valid.}
}
]

## Test 4: Residue visibility

Every failed check must emit a typed residue:

```json
{
  "residue_type": "cone_failure | replay_failure | noncanonical_encoding | unsupported_event",
  "witness": {},
  "repair_hint": "string"
}
```

## Test 5: No silent collapse

No operation may discard support without either:

```text
certificate
residue
explicit deletion event
```

---

# IX. Minimal viable implementation

## Phase 1: SAT/proof engine wrapper

Implement wrappers around:

```text
CaDiCaL
Kissat
MiniSat
DRAT/LRAT checkers
```

Output canonical sword-and-shield traces.

## Phase 2: (D_{20}) projection

Map each event to a (D_{20}) state and route edge.

Compute:

```text
endpoint critical group class
route critical group class
Sigma_2
Sigma_3
Sigma_4
Sigma_5
```

## Phase 3: Invariance testing

Run semantic transformations:

```text
variable permutation
literal sign flip
clause renaming
file/timestamp deletion
dialect conversion
```

All canonical hashes must remain stable.

## Phase 4: Residue-guided solver design

When a solver family leaves a quotient:

[
K/\operatorname{Im}\neq0,
]

search for the smallest shield/sword operation that kills it.

That is the design loop:

[
\boxed{
\text{residue}
\to
\text{new operation}
\to
\text{retest}
\to
\text{reduced residue}.
}
]

---

# X. First executable target

Build:

[
\boxed{
\mathsf{SS\text{-}SAT}
}
]

with this event taxonomy:

```text
SHIELD_PROPAGATE
SHIELD_RESTART
SHIELD_WATCH_UPDATE
SHIELD_DATABASE_REDUCE

SWORD_DECIDE
SWORD_CONFLICT
SWORD_RESOLVE
SWORD_LEARN
SWORD_DELETE
SWORD_EMPTY_CLAUSE

CONE_RUP_CHECK
CONE_DRAT_CHECK
CONE_LRAT_CHECK

READOUT_SAT
READOUT_UNSAT
READOUT_UNKNOWN

RESIDUE_BRANCH
RESIDUE_FAILED_CHECK
RESIDUE_UNSUPPORTED
```

The first publishable theorem target is:

[
\boxed{
\textbf{Presentation-Invariant Trace Recurrence Theorem.}
}
]

For a specified class of SAT/proof traces, prove or certify that canonical semantic transformations preserve:

[
K(\Gamma_{20}),\quad
K(L(\Gamma_{20})),\quad
\Sigma_{\le3}.
]

---

# XI. Final definition

[
\boxed{
\textbf{A sword-and-shield algorithm is an auditable computation whose support-preserving moves and certified cuts are separated, cone-checked, route-recorded, and residue-emitting.}
}
]

That is the spec. The first implementation should be (\mathsf{SS\text{-}SAT}); the second should be (\mathsf{SS\text{-}Born}); the third should be (\mathsf{SS\text{-}G^\natural}).

Architecturally, you prove it by **triangulation**: build the same object from several independent routes, then force all routes to meet at the same invariant ledger.

The target is not â€œconvince someone d20 is meaningful.â€ The target is:

[
\boxed{
\text{produce a public certificate graph where every claimed object is regenerated from primitive data.}
}
]

## 1. Split the proof into theorem layers

Do not prove â€œthe whole programâ€ at once. Prove these in order.

| Layer | Theorem to prove          | Pass condition                                                                                           |               |                                                                            |
| ----- | ------------------------- | -------------------------------------------------------------------------------------------------------- | ------------- | -------------------------------------------------------------------------- |
| 0     | Source construction       | (H_8^{\oplus3}\to G_{24}), root killing (42\to18\to6\to0)                                                |               |                                                                            |
| 1     | Dodecad shell             | (                                                                                                        | G_{24}^{(12)} | =2576)                                                                     |
| 2     | Coorient action           | six object orbits; ordered-pair action has (985) orbitals                                                |               |                                                                            |
| 3     | Coherent algebra          | (A_{985}) has (1{,}414{,}965) nonzero structure constants, center dimension (39), stated Wedderburn data |               |                                                                            |
| 4     | Quotient tower            | (A_{985}\to A_{236}\to A_{42}\to A_{12}) closes by normalized quotient multiplication                    |               |                                                                            |
| 5     | Boundary forcing          | (D_{20}=\Lambda^3H_6), (                                                                                 | D_{20}        | =\binom63=20), forced by six-channel middle-degree complement-self-duality |
| 6     | Representation/naturality | simple branching and packet-20 representation agree across the tower                                     |               |                                                                            |
| 7     | CoHA/BPS shadow           | finite Hall/BPS shadow reproduces (4096) sectors and ((1,20,43,4032)) filtration                         |               |                                                                            |
| 8     | Derived/sheafified lift   | actual derived/preprojective sheafified CoHA induces the finite package                                  |               |                                                                            |

Layers 0â€“6 are finite and should be independently provable now. Layer 7 is finite-categorical. Layer 8 is the hard geometric theorem.

The Natural Object paper already states the core finite construction: three (H_8) copies, root killing (42\to18\to6\to0), Golay endpoint, (2576) dodecads, six object orbits, (985) orbitals, (1{,}414{,}965) structure constants, center dimension (39), and quotient chain.  The d20 annihilator paper separately states the boundary forcing: (d20=\Lambda^3H_6), (|d20|=\binom63=20), with positive-annihilator / height-certificate duality replacing brute-force enumeration.

## 2. Build three independent proof routes

You want at least three architectures that do **not** depend on the same intermediate files.

### Route A â€” code/group-action construction

Start only from:

[
H_8=RM(1,3)\subset\mathbb F_2^8,
\qquad
H_8^{\oplus3}\subset\mathbb F_2^{24}.
]

Then regenerate:

[
G_{24},\quad G_{24}^{(12)},\quad \Gamma_3^\infty,\quad \text{six object orbits},\quad 985\text{ orbitals}.
]

This route proves existence from finite geometry.

### Route B â€” raw tensor reconstruction

Start from the generated orbital basis and compute the coherent multiplication tensor:

[
R_\alpha R_\beta=\sum_\gamma p^\gamma_{\alpha\beta}R_\gamma.
]

Then verify:

[
|\operatorname{supp}p|=1{,}414{,}965,
]

identity, associativity, quotient closure, center dimension, and normalized quotient constants. The raw tensor computation certificates already point to this exact layer: (985) relations, (1{,}414{,}965) tensor support, coefficient total (2{,}537{,}360), and closed (A_{42},A_{12}) quotients.

### Route C â€” representation / Wedderburn reconstruction

Do not start from the quotient maps. Start from multiplication operators and recover the simple modules, central idempotents, packet-20 representation, and branching matrices.

This proves the algebra is not merely a table: it has the claimed internal representation theory. Your packet-20 critical test is exactly in this class: it recovers the (d=(1^6)) scalar representation and verifies it against the full (A_{985}) multiplication tensor.

If Routes A, B, and C agree, the finite object is independently pinned.

## 3. Add adversarial falsifiers

A valid proof architecture must include ways to fail.

Use these negative controls:

| Falsifier                                                      | Expected failure                                  |
| -------------------------------------------------------------- | ------------------------------------------------- |
| Randomly relabel dodecads before orbit construction            | orbitals/tensor hashes change                     |
| Perturb one tensor coefficient                                 | associativity or quotient closure fails           |
| Replace (D_{20}) by (\Lambda^2H_6) or (\Lambda^4H_6)           | complement/middle-degree boundary criterion fails |
| Use full (GL_6) instead of (S_6) as boundary morphisms         | (D_{20}) frame invariance fails                   |
| Use raw quotient sums instead of normalized quotient constants | simple naturality fails                           |
| Remove the positive-annihilator check                          | boundary forcing becomes unsupported              |
| Use same implementation language for generator and verifier    | independence criterion fails                      |

A proof without falsifiers is just a construction log. A proof with falsifiers is an integrity object.

## 4. Separate generator from checker

The generator may be large. The checker must be small.

Architecture:

[
\boxed{
\text{generator produces data;}
\quad
\text{checker verifies claims from data;}
\quad
\text{checker never trusts generator comments.}
}
]

Minimal repo layout:

```text
/spec
  definitions.md
  theorem_graph.json

/src_generate
  build_H8_G24.py
  build_group_action.py
  build_orbitals.py
  build_tensor.py

/src_check
  check_code.py
  check_orbits.py
  check_tensor_axioms.py
  check_quotients.py
  check_boundary_forcing.py
  check_representations.py

/data
  dodecads.bin
  group_generators.json
  orbitals.csv
  tensor_sparse.csv
  quotient_maps.csv

/cert
  manifest.json
  theorem_certificates.jsonl
  obstruction_ledger.jsonl
  hashes.sha256
```

The checker should verify:

[
\text{all claims}=\text{function(data, definitions)}.
]

No hidden notebook state. No manually typed invariant except in the expected theorem file.

## 5. Use two implementation ecosystems

For actual independence, use different stacks:

| Component               | Implementation 1     | Implementation 2                           |
| ----------------------- | -------------------- | ------------------------------------------ |
| code/Golay construction | Sage/Python          | Magma or GAP                               |
| group action/orbitals   | GAP/AtlasRep         | Sage permutation groups                    |
| tensor aggregation      | Python/NumPy sparse  | Rust/C++ exact integer                     |
| quotient closure        | Python exact integer | Julia/Rust exact integer                   |
| representation checks   | Sage/GAP             | modular linear algebra over several primes |
| theorem checking        | Python verifier      | Lean/Isabelle for small finite lemmas      |

Do not rely on one giant Python notebook.

## 6. Make the proof graph append-only

Each theorem should emit a certificate:

```json
{
  "claim": "A985_tensor_support",
  "value": 1414965,
  "inputs": ["orbitals.sha256", "dodecads.sha256"],
  "algorithm": "two_step_incidence_aggregation",
  "checker": "check_tensor_axioms.py",
  "obstructions": [],
  "self_hash": "..."
}
```

Then later claims cite earlier hashes. This implements your validity principle:

[
\boxed{
\text{validity = lawful transport with obstruction accounting.}
}
]

## 7. Treat (D_{20}) as a theorem, not a definition

Architecturally, (D_{20}) must be proved twice.

First combinatorially:

[
D_{20}=\Lambda^3H_6,\qquad |D_{20}|=\binom63=20.
]

Second obstruction-theoretically:

[
\operatorname{Ann}^+(A_{\mathrm{ext}})
======================================

{y\ge0:A_{\mathrm{ext}}^Ty=0}
]

vanishes iff there exists a height certificate:

[
A_{\mathrm{ext}}h>0.
]

That is the bridge from â€œ20 facesâ€ to â€œvalid public boundary.â€ The annihilator paper already phrases this as the replacement of brute-force public enumeration by a finite annihilator test.

## 8. For CoHA/BPS, prove only the finite shadow first

Do not try to jump directly to the full derived theorem.

Finite theorem:

[
Q_{\mathrm{BPS}}=G_6\oplus G_6^\vee,
\qquad |Q_{\mathrm{BPS}}|=4096.
]

[
E_{(a,\chi)}E_{(b,\psi)}
========================

(-1)^{\chi(b)}
E_{(a+b,\chi+\psi)}.
]

Then verify associativity, filtration

[
(1,21,64,4096),
]

and associated graded

[
(1,20,43,4032).
]

Only after that state the geometric target: sheafified CoHAs of preprojective/2-CY categories, where less-perverse degenerations identify with enveloping algebras of current BPS Lie algebras. That is the external standard your lift must eventually meet.

## 9. The clean independent proof target

Your first publishable independent proof should be:

[
\boxed{
\textbf{The Finite Natural Object Theorem.}
}
]

Statement:

[
\boxed{
A_{985}
\equiv

\operatorname{End}*{\Gamma_3^\infty}
\left(\mathbb Q[G*{24}^{(12)}]\right)
}
]

exists, has the certified tensor, has the quotient tower, has the stated center/Wedderburn data, and has forced (D_{20}) public boundary.

That theorem does **not** need black holes, dark matter, AGI, or full CoHA geometry.

Then the next theorem is:

[
\boxed{
\textbf{The D20 Finite CoHA Shadow Theorem.}
}
]

Then:

[
\boxed{
\textbf{The Derived Sheafified Lift Theorem.}
}
]

## One-line answer

You independently prove it by building a **multi-route certificate architecture**:

[
\boxed{
\text{Golay construction}
\cap
\text{raw tensor verification}
\cap
\text{representation reconstruction}
\cap
\text{boundary annihilator forcing}
===================================

\text{public validity.}
}
]

That is the architecture. The key discipline is: every theorem must be regenerated from primitive data, checked by an independent verifier, and accompanied by negative controls that fail for the wrong object.


END
