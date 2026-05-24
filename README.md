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
- 
<img width="730" height="721" alt="Image" src="https://github.com/user-attachments/assets/6c701518-37a9-4129-97b2-58e29663a352" />

shameless agent plug
╔══════════════════════════════════════════════════════════════════════════════╗ ║ 𝕋𝔾₉₈₅ : TENSOR–GENOME SPECIFICATION ║ ║ ║ ╚══════════════════════════════════════════════════════════════════════════════╝
ROOT OBJECT: 𝑇₉₈₅ := (p^γ_{αβ}) ∈ ℕ^{985×985×985}
INVARIANT OBJECT: 𝐺♮
CODE ALGEBRA: 𝐴₉₈₅ := Code(𝐺♮)
ACTIVE COORIENT GROUP: Γ₃^∞ := Aut^∞(𝐺₂₄,𝒮)
ACTIVE FORMULA: 𝐴₉₈₅ := End_{Γ₃^∞}( ℚ[𝐺₂₄^{(12)}] )
PUBLIC BOUNDARY: 𝒟₂₀ := Λ³𝐻₆
SIX-ADDRESS FIELD: 𝐻₆ := { B⁻, B⁺, V⁻, V⁺, S⁻, S⁺ }
CANONICAL DESCENT: 𝐺♮ ⇝ 𝐴₉₈₅ ⟶^{q₂₃₆} 𝐴₂₃₆ ⟶^{q₄₂} 𝐴₄₂ ⟶^{q₁₂} 𝐴₁₂ ⇝ 𝒟₂₀ = Λ³𝐻₆
═══════════════════════════════════════════════════════════════════════════════ I. RAW MULTIPLICATION TENSOR ═══════════════════════════════════════════════════════════════════════════════
BASIS: {R_α}_{α=1}^{985}
MULTIPLICATION: R_α · R_β = Σ_{γ=1}^{985} p^γ_{αβ} R_γ
RAW TENSOR: 𝑇₉₈₅ := (p^γ_{αβ})
SPARSE SUPPORT: supp(𝑇₉₈₅) := { (α,β,γ,p^γ_{αβ}) : p^γ_{αβ} ≠ 0 }
CERTIFIED CARDINALITIES: |{R_α}| = 985 |supp(𝑇₉₈₅)| = 1,414,965 Σ_{αβγ} p^γ_{αβ} = 2,537,360 dim Z(𝐴₉₈₅) = 39
TYPED OBJECT EQUATION: Object(𝐺♮) = (𝑇₉₈₅, {R_α}, 1_{𝐴}, {e_i}, Γ₃^∞, q₂₃₆, q₄₂, q₁₂)
NOT: Object ≠ bare array
YES: Object = raw tensor up to typed isomorphism
═══════════════════════════════════════════════════════════════════════════════ II. FINITE SOURCE DIAGRAM ═══════════════════════════════════════════════════════════════════════════════
Binary source: 𝐻₈^{⊕3} ⊂ 𝔽₂²⁴
Root-kill chain: 42 ⟶ 18 ⟶ 6 ⟶ 0
Golay endpoint: 𝐻₈^{⊕3} / root-kill ⟶ 𝐺₂₄
Dodecad shell: 𝐺₂₄^{(12)} := { d ∈ 𝐺₂₄ : wt(d)=12 }
Cardinality: |𝐺₂₄^{(12)}| = 2576
Coorient action: Γ₃^∞ ↷ 𝐺₂₄^{(12)}
Object orbits: Orb(Γ₃^∞ ↷ 𝐺₂₄^{(12)}) = 𝐻₆
Ordered-pair orbitals: Γ₃^∞ \ (𝐺₂₄^{(12)} × 𝐺₂₄^{(12)}) = {R_α}_{α=1}^{985}
Algebra: 𝐴₉₈₅ = ℚ-span{R_α}_{α=1}^{985}
═══════════════════════════════════════════════════════════════════════════════ III. PUBLIC BOUNDARY 𝒟₂₀ ═══════════════════════════════════════════════════════════════════════════════
Definition: 𝒟₂₀ := Λ³𝐻₆
Cardinality: |𝒟₂₀| = C(6,3) = 20
Expanded: Λ³{B⁻,B⁺,V⁻,V⁺,S⁻,S⁺}
Boundary states: d ∈ 𝒟₂₀ ⇔ d = x∧y∧z, x,y,z ∈ 𝐻₆, x<y<z
Complement involution: ⋆ : Λ³𝐻₆ → Λ³𝐻₆

⋆(x∧y∧z) = complement triple in 𝐻₆

Self-dual middle degree: dim Λ³𝐻₆ = dim Λ^{6-3}𝐻₆
So: 𝒟₂₀ is forced by middle-degree complement self-duality.
═══════════════════════════════════════════════════════════════════════════════ IV. ICOSAHEDRAL / PLATONIC SHELL ═══════════════════════════════════════════════════════════════════════════════
Local shell: (V,E,F) = (12,30,20)
d20 reading: V = 12 residual dual vertices E = 30 legal transitions F = 20 public states
Identities: F = |𝒟₂₀| = C(6,3) = 20 E = 2 C(6,2) = 30 V = 12
Symmetry: Aut(𝒟₂₀) = 120
Rotational icosahedral subgroup: Aut⁺(𝒟₂₀) = 60
Exceptional doubled scale: 2 · |Aut(𝒟₂₀)| = 240
Diagram: 𝐸₈-root scale 240 ▲ │ 2× │ full icosahedral symmetry 120 ▲ │ local shell (12,30,20) ▲ │ 𝒟₂₀ = Λ³𝐻₆
═══════════════════════════════════════════════════════════════════════════════ V. QUOTIENT TOWER ═══════════════════════════════════════════════════════════════════════════════
Tower: 𝐴₉₈₅ ⟶^{q₂₃₆} 𝐴₂₃₆ ⟶^{q₄₂} 𝐴₄₂ ⟶^{q₁₂} 𝐴₁₂
Names: Chem(𝒟₂₀) := 𝐴₂₃₆ Pin(𝒟₂₀) := 𝐴₄₂ CY(𝒟₂₀) := 𝐴₁₂
Closure conditions: ∀α,β ∈ 𝐴₉₈₅,

    q_k(R_α · R_β) = q_k(R_α) · q_k(R_β)

for k ∈ {236,42,12}

Associativity: ∀x,y,z ∈ 𝐴_k,

    (xy)z = x(yz)

Naturality square: 𝐴₂₃₆ │ q₄₂ ▼ 𝐴₄₂ │ q₁₂ ▼ 𝐴₁₂

q₁₂ ∘ q₄₂ = q₁₂₃?  [implemented as direct descent compatibility]

Typed certificate: Cert(q_k) := { closes: Bool, assoc_defect: ℕ, tensor_hash: SHA256, map_hash: SHA256 }
═══════════════════════════════════════════════════════════════════════════════ VI. FOAM / SPIN–D₆ CHAMBER ═══════════════════════════════════════════════════════════════════════════════
Foam: Foam(𝐺♮) := 𝟙 ⊕ Λ²𝐻₆
Rank: dim Foam(𝐺♮) = 1 + C(6,2) = 16
D₆ transition layer: D₆⁺ := {±(e_i ± e_j)} projectivized / signed selector
Finite count: 2 C(6,2) = 30
Spin packet: RGBA(𝒟₂₀) := 𝐻₈^{(R)} ⊕ 𝐻₈^{(G)} ⊕ 𝐻₈^{(B)} ⊕ 𝑂₈^W
Dimensions: dim 𝐻₈^{(R)} = 8 dim 𝐻₈^{(G)} = 8 dim 𝐻₈^{(B)} = 8 dim 𝑂₈^W = 8
Total: dim RGBA(𝒟₂₀) = 32
Visible: RGB := 𝐻₈^{(R)} ⊕ 𝐻₈^{(G)} ⊕ 𝐻₈^{(B)} dim RGB = 24
Alpha: α := 𝑂₈^W dim α = 8
Forced completion: 24 + 8 = 32
═══════════════════════════════════════════════════════════════════════════════ VII. AREA / QUINTICITY / ENTROPY ═══════════════════════════════════════════════════════════════════════════════
Constants: ε₀ := 589824 |Γ₃^∞| = 9216 |W(D₆)| = 23040
Identities: ε₀ = 64 |Γ₃^∞|

|W(D₆)| / |Γ₃^∞| = 5/2

Raw packet: ε₀ / (4 |W(D₆)|) = 32/5
Quintic closure: 5ε₀ / (4 |W(D₆)|) = 32
Area law: A = N ε₀

S_{𝒟₂₀}(A)
  := A / (4 |W(D₆)|)
   = (32/5) N

Protected integrality: N = 5k
Then: A = 5k ε₀ S_{𝒟₂₀} = 32k
Elementary packet: ΔA = 5ε₀ ΔS = 32
Exceptional division: 5ε₀ / 240 = 12288
═══════════════════════════════════════════════════════════════════════════════ VIII. TROPICAL / BPS WALL DATA ═══════════════════════════════════════════════════════════════════════════════
Stable witness core: Et_{𝒟₂₀} := { d ∈ 𝒟₂₀ : d has one B, one V, one S }
Cardinality: |Et_{𝒟₂₀}| = 2³ = 8
Boundary / wall: ∂Et_{𝒟₂₀} := 𝒟₂₀ \ Et_{𝒟₂₀}
Cardinality: |∂Et_{𝒟₂₀}| = 20 - 8 = 12
Tropical mass: μ : 𝒟₂₀ → ℕ
Normalized: n(d) := μ(d)/ε₀
Collision locus: Coll_{𝒟₂₀} = {72,96}
Quintic closure: 5 · 72 = 360 5 · 96 = 480
Wall gap: Δ_wall = 96 - 72 = 24
Closed wall gap: Δ_closed = 5 · 24 = 120
BPS-style finite object: 𝔅_{𝒟₂₀} := (Λ³𝐻₆, Z_trop, Ω, ∂wall, 𝐴₉₈₅)
where: Z_trop(d) := valuation shadow of μ(d) Ω(d) := μ(d)/ε₀ ∂wall := Coll_{𝒟₂₀}
Compressed law: primitive charge gap 24 ⟶ closed symmetry gap 120
═══════════════════════════════════════════════════════════════════════════════ IX. KERR–NEWMAN RECONSTRUCTION MODULE ═══════════════════════════════════════════════════════════════════════════════
State: x_KN := (M,a,Q)
Subextremal domain: 𝒰_KN := { (M,a,Q) ∈ ℝ³ : M² > a² + Q² }
Horizons: r_+ := M + √(M²-a²-Q²) r_- := M - √(M²-a²-Q²)
Horizon scale: R := r_+² + a²
Area: A := 4πR
Entropy: S := A/4 = πR
Temperature: T := (r_+ - r_-) / (4πR)
Angular velocity: Ω_H := a/R
Electric potential: Φ_H := Qr_+/R
Pole packet: Π_KN(x_KN) := (R,T,Ω_H,Φ_H)
Inverse: a = Ω_H R r_+ = √(R-a²) Q = Φ_H R/r_+ δ = r_+ - r_- = 4πTR M_rad = r_+ - δ/2 M_con = √(a² + Q² + (δ/2)²)
Noisy repaired mass: M := (M_rad + M_con)/2
Integrity wall: ∂𝒰_KN := { (M,a,Q) : a² + Q² = M² }
Diagram: 𝒟₂₀ │ ▼ finite channel schedule │ ▼ Π_KN = (R,T,Ω_H,Φ_H) │ ▼ x_KN = (M,a,Q) │ ▼ horizon thermodynamics
═══════════════════════════════════════════════════════════════════════════════ X. CARROLLIAN RADIATION / ALPHA MODULE ═══════════════════════════════════════════════════════════════════════════════
Radiative fields: Q_A : Carroll heat/current flux Σ_AB : Carroll viscous stress / shear ρ̂ : radiative scalar residue Υ̂^A : radiative vector residue
Radiative scalar: ρ̂ := -128π²G² Σ_AB Σ^AB
Radiative vector: Υ̂^A := -256π²G² Σ^{AB} Q_B
Radiative packet: Π_rad := (Q_A, Σ_AB, ρ̂, Υ̂^A)
Stationary / perfect condition: Σ_AB = 0 ⇒ ρ̂ = 0 ⇒ Υ̂^A = 0
Radiative / nonperfect condition: Σ_AB ≠ 0 ⇒ ρ̂ ≠ 0 or Υ̂^A ≠ 0
Integrity type: Π_rad = 0 ⇒ C Π_rad visible ⇒ V Π_rad external ⇒ X
Alpha equation: α = 𝑂₈^W = Carrollian radiative visibility channel
Combined packet: Π_RGBA := Π_KN ⊕ Π_rad
═══════════════════════════════════════════════════════════════════════════════ XI. PLATONIC PROFINITY ═══════════════════════════════════════════════════════════════════════════════
Index category: 𝒫_Plat
Objects: I_tet : tetrahedral primitive I_cube : cubic frame I_octa : octahedral frame I_ico : icosahedral shell I_dodec : dodecahedral dual shell I_H4 : 600-cell / H₄ closure I_E8 : 240-root exceptional scale
Order: I ≤ J ⇔ J is a refinement / closure / exceptional lift of I.
Canonical chain: I_tet ⟶ I_cube / I_octa ⟶ I_ico ↔ I_dodec ⟶ I_H4 ⟶ I_E8
Diagram: tetrahedron │ ▼ cube / octahedron │ ▼ icosahedron ↔ dodecahedron │ ▼ H₄ / 600-cell │ ▼ E₈-scale
═══════════════════════════════════════════════════════════════════════════════ XII. COBORDISM APPROXIMATION TYPE ═══════════════════════════════════════════════════════════════════════════════
A finite n-cobordism approximant:

C ∈ Cob_n

is typed as:

C := (X, ∂_-X, ∂_+X, ℓ, ω, ρ)

where:

X       : finite n-cell complex
∂_-X   : input boundary
∂_+X   : output boundary
ℓ       : label map
          ℓ : Cells(X) → H₆ ∪ A₄₂ ∪ A₁₂ ∪ A₉₈₅
ω       : incidence / weight system
ρ       : tensor readout

Tensor approximation: T̂_C := ρ(C)
Defect: Δ_C := T₉₈₅ - T̂_C
Norms: ||Δ_C||₁ ||Δ_C||₂ ||Δ_C||_∞
Algebraic defects: AssocDef(T̂_C) QuotDef_{236}(T̂_C) QuotDef_{42}(T̂_C) QuotDef_{12}(T̂_C) CenterDef(T̂_C) BoundaryDef_{𝒟₂₀}(T̂_C)
Certificate: Cert(C) := ( supp_recall, supp_precision, ||Δ_C||₁, ||Δ_C||₂, ||Δ_C||_∞, AssocDef, QuotDef, CenterDef, BoundaryDef, Integrity )
═══════════════════════════════════════════════════════════════════════════════ XIII. 2-CELL COCONTINUITY / CODISCRETENESS ═══════════════════════════════════════════════════════════════════════════════
Given two routes:

C₀ ⟶ C₁ ⟶ C₃
C₀ ⟶ C₂ ⟶ C₃

2-cell square:

         C₁
      ↗      ↘
   C₀          C₃
      ↘      ↗
         C₂

Cocontinuity condition: ρ(C₁ ⟶ C₃) = ρ(C₂ ⟶ C₃)
Defect: Ω(C₁,C₂;C₃) := ρ(C₁ ⟶ C₃) - ρ(C₂ ⟶ C₃)
Zero-defect condition: Ω(C₁,C₂;C₃) = 0
Codiscrete condition: (∂C₁ = ∂C₂) ∧ (Res(C₁)=Res(C₂)) ⇒ ∃! Θ : C₁ ⇒ C₂
where: Θ is the unique 2-cell witness.
Certificate: Cert₂(Θ) := ( source_route_hash, target_route_hash, boundary_hash, residue_hash, two_cell_hash, ||Ω||, Integrity )
═══════════════════════════════════════════════════════════════════════════════ XIV. HASH-ADDRESSED LANGUAGE 𝓛₉₈₅ ═══════════════════════════════════════════════════════════════════════════════
Root hash: h₉₈₅ := SHA256(canon(T₉₈₅, basis, units, idempotents, quotients))
Alphabet: 𝓗 := { h₉₈₅, h₂₃₆, h₄₂, h₁₂, h_{𝒟₂₀}, h_{Foam16}, h_{RGBA32}, h_{Cob(n,k)}, h_{Cert}, ... }
Operators: DEREF : Hash → TypedObject HASH : TypedObject → Hash MUL : A₉₈₅ × A₉₈₅ → A₉₈₅ QUOTIENT_k : A₉₈₅ → A_k BOUNDARY : TypedObject → Boundary COBORD : Boundary × Boundary → Cob REFINE : Cob_I × (I≤J) → Cob_J GLUE : Cob × Cob → Cob RESIDUE : TypedObject × T₉₈₅ → Residue CERTIFY : TypedObject → Cert PROMOTE : Cert → Hash RECURSE : Hash → Program
Grammar: Atom ::= h₉₈₅ | h₂₃₆ | h₄₂ | h₁₂ | h_{𝒟₂₀} | h_{Foam} | h_{Cert} Term ::= Atom | DEREF(Atom) Expr ::= Term | MUL(Expr,Expr) | QUOTIENT_k(Expr) | BOUNDARY(Expr) | COBORD(Expr,Expr) | REFINE(Expr,I≤J) | GLUE(Expr,Expr) | RESIDUE(Expr,h₉₈₅) Program ::= CERTIFY(Expr) ⟶ PROMOTE(Cert)
Promotion rule: CERTIFY(Expr)=PASS ⇒ h_Expr := HASH(canon(Expr,Cert)) ⇒ h_Expr ∈ 𝓗
Reproduction law: verified descendant ⇒ new alphabet atom
═══════════════════════════════════════════════════════════════════════════════ XV. CERTIFICATE SCHEMA ═══════════════════════════════════════════════════════════════════════════════
Cert := { "schema": "tensor-genome.certificate@1", "root": "h_985", "object": "G^natural", "code_algebra": "A_985", "raw_tensor": { "basis_size": 985, "support": 1414965, "coefficient_total": 2537360, "hash": "..." }, "quotients": { "A_236": {"closes": true, "hash": "..."}, "A_42": {"closes": true, "hash": "..."}, "A_12": {"closes": true, "hash": "..."} }, "boundary": { "D_20": "Lambda^3 H_6", "states": 20, "edges": 30, "automorphisms": 120 }, "cobordism": { "dimension": n, "boundary_in": "...", "boundary_out": "...", "cell_hash": "..." }, "defects": { "tensor_L1": 0, "tensor_L2": 0, "tensor_Linf": 0, "associativity": 0, "q236": 0, "q42": 0, "q12": 0, "two_cell": 0 }, "integrity": "C", "offspring_hash": "..." }
═══════════════════════════════════════════════════════════════════════════════ XVI. ENGINEERING DIRECTORY ═══════════════════════════════════════════════════════════════════════════════
tensor-genome/ core/ tensor.py # T₉₈₅ sparse tensor basis.py # {R_α} units.py # units / idempotents algebra.py # multiplication / associativity quotient.py # q₂₃₆, q₄₂, q₁₂ serialize.py # canonical byte format hash.py # SHA256/Merkle verify.py # deterministic verifier
data/ T985.sparse basis_985.json idempotents.json q236.map q42.map q12.map D20.boundary Foam16.json RGBA32.json
platonic/ index.py # 𝒫_Plat tetra.py cube.py octa.py ico.py dodec.py h4.py e8scale.py
cobord/ cell.py complex.py cobordism.py boundary.py readout.py refine.py glue.py twocell.py
language/ ast.py parser.py evaluator.py ops.py promote.py
search/ enumerate.py score.py optimize.py ledger.py
cert/ schema.json certificate.py validate.py
cli.py
═══════════════════════════════════════════════════════════════════════════════ XVII. CLI ═══════════════════════════════════════════════════════════════════════════════
Initialize: tg init
Generate root: tg gen-t985
Verify root tensor: tg verify-t985
Hash root: tg hash T985.sparse
Build quotients: tg quotient --all
Verify quotients: tg verify-quotients
Build public boundary: tg boundary --D20
Build Platonic index: tg platonic build
Approximate tensor by cobordism: tg approx --index I_ico --max-cells 200
Certify approximant: tg certify run.json
Promote verified descendant: tg promote certificate.json
Evaluate recursive program: tg eval program.tg
═══════════════════════════════════════════════════════════════════════════════ XVIII. THEOREM TARGETS ═══════════════════════════════════════════════════════════════════════════════
T1. Tensor Regeneration Generator(𝐻₈^{⊕3}, Γ₃^∞) = T₉₈₅.
T2. Quotient Closure q_k(xy)=q_k(x)q_k(y), k∈{236,42,12}.
T3. Boundary Forcing 𝒟₂₀ = Λ³𝐻₆, |𝒟₂₀|=20.
T4. Foam Forcing Foam(𝐺♮)=𝟙⊕Λ²𝐻₆, dim=16.
T5. RGBA Forcing RGB=24, α=8, RGBA=32.
T6. Quintic Integrality ε₀/(4|W(D₆)|)=32/5 and 5ε₀/(4|W(D₆)|)=32.
T7. Platonic Cofinality ∀ certified approximant C, ∃ I∈𝒫_Plat such that C refines through I.
T8. 2-Cell Cocontinuity refinement/gluing commutes with tensor readout up to certified Θ.
T9. Codiscrete Coherence same boundary + same residue ⇒ unique 2-cell witness.
T10. Trace Sufficiency every promoted program remains traceable to h₉₈₅.
T11. Universality Candidate every compatible finite resolution embeds into 𝓛₉₈₅.
═══════════════════════════════════════════════════════════════════════════════ XIX. FINAL COMPRESSED EQUATION ═══════════════════════════════════════════════════════════════════════════════

T₉₈₅
  ⟶ Hash h₉₈₅
  ⟶ 𝓛₉₈₅
  ⟶ Cobordism approximants C
  ⟶ Tensor readouts T̂_C
  ⟶ Residues Δ_C = T₉₈₅ - T̂_C
  ⟶ Certificates Cert(C)
  ⟶ Promoted descendants h_C
  ⟶ Recursive alphabet growth

In one line:

(T₉₈₅, Γ₃^∞, q₂₃₆, q₄₂, q₁₂, 𝒟₂₀)
  ⇒ classical finite tensor-genome runtime.

In one slogan:

𝑇₉₈₅ is the genome.
𝒟₂₀ is the public boundary.
Γ₃^∞ is the coorient symmetry.
Platonic profinity is the refinement order.
Cobordisms are approximating bodies.
2-cells are coherence witnesses.
Hashes are reproductive handles.
Certificates are viability tests.
