# C/V/X Model P != NP Separation

## Statement

In the repository C/V/X public computation model, no public polynomial-time C-only computation decides the SAT-complete parameterized E(phi) family. Equivalently, P_CVX != NP_CVX for this encoded family under the certified C/V/X interface.

Conditional standard form:

If the repository C/V/X public trace model is proved extensionally equivalent to the standard Turing-machine definition of polynomial-time public computation, then this model-scoped theorem promotes to the standard statement P != NP.

## Definitions

- `P_CVX`: Polynomial-time public computations whose executions compile with polynomial overhead into the certified public C/V/X trace model and do not use X extractor/oracle/advice events.
- `NP_CVX`: Certificate-bearing computations over the encoded E(phi) family with public witness checking and inverse assignment projection.
- `E_phi`: The parameterized assignment-bearing e33 target family produced from DIMACS CNF inputs.

## Proof Chain

1. SAT completeness: DIMACS CNF-SAT reduces publicly and polynomially to the E(phi) encoded family with forall yes/no preservation.
   Witness: `data/invariants/integrity/cvx_trace/reports/encoded_family_sat_frontier_certificate.json`
2. Trace universality: Accepted public polynomial executions compile to the C/V/X trace vocabulary with polynomial overhead.
   Witness: `data/invariants/integrity/cvx_trace/reports/universal_trace_compiler_report.json`
3. Total typing: Accepted trace events are C, V, X, or explicit residues; no untyped escape is silently accepted.
   Witness: `data/invariants/integrity/cvx_trace/reports/universal_trace_typing_report.json`
4. Pure-C no escape: Pure public C traces do not recover the hidden e33 obstruction needed to decide the family.
   Witness: `data/invariants/integrity/cvx_trace/reports/universal_pure_c_no_escape_report.json`
5. V accounting: Visible V wall crossings are public boundary certificates, not hidden advice.
   Witness: `data/invariants/integrity/cvx_trace/reports/universal_v_wall_crossing_accounting_report.json`
6. X boundary: Successful hidden-sector extraction is typed X and excluded from public-P computation.
   Witness: `data/invariants/integrity/cvx_trace/reports/x_policy_boundary_certificate.json`
7. No-escape closure: A public polynomial decider would need either an impossible pure-C recovery or an X extractor outside public P.
   Witness: `data/invariants/integrity/cvx_trace/reports/full_no_escape_closure_ledger.json`

## Boundary

- The theorem is extracted inside the repository C/V/X model.
- The standard global P != NP statement is conditional on identifying `P_CVX` with standard polynomial-time public computation.
- The document does not use the blocked literal `P != NP iff T985` equivalence.
- The finite 2048-mask candidate remains lookup-only; SAT preservation is carried by the parameterized `E(phi)` family.

## Decision

- Repo model P != NP: `True`
- Standard global P != NP: `False`
- Conditional standard promotion: `True`

## Verification Sources

- `bridge_checklist`: `P_VS_NP_BRIDGE_CHECKLIST_FORMALIZED` at `data/invariants/integrity/p_vs_np_bridge_checklist.json`
- `encoded_family_sat_frontier`: `ENCODED_FAMILY_SAT_COMPLETE_REDUCTION_CERTIFIED` at `data/invariants/integrity/cvx_trace/reports/encoded_family_sat_frontier_certificate.json`
- `forall_yes_no_preservation`: `FORALL_YES_NO_PRESERVATION_THEOREM_CERTIFIED` at `data/invariants/integrity/cvx_trace/reports/forall_yes_no_preservation_theorem.json`
- `universal_trace_compiler`: `UNIVERSAL_TRACE_COMPILER_POLYNOMIAL_OVERHEAD_PASS` at `data/invariants/integrity/cvx_trace/reports/universal_trace_compiler_report.json`
- `universal_trace_typing`: `UNIVERSAL_TRACE_TYPING_TOTALITY_WITNESS_PASS` at `data/invariants/integrity/cvx_trace/reports/universal_trace_typing_report.json`
- `universal_pure_c_no_escape`: `UNIVERSAL_PURE_C_NO_ESCAPE_WITNESS_PASS` at `data/invariants/integrity/cvx_trace/reports/universal_pure_c_no_escape_report.json`
- `universal_v_wall_crossing`: `UNIVERSAL_V_WALL_CROSSING_ACCOUNTING_PASS` at `data/invariants/integrity/cvx_trace/reports/universal_v_wall_crossing_accounting_report.json`
- `x_policy_boundary`: `X_POLICY_BOUNDARY_CERTIFIED_PUBLIC_P_EXCLUDES_X` at `data/invariants/integrity/cvx_trace/reports/x_policy_boundary_certificate.json`
- `quotient_kernel_reflection`: `QUOTIENT_KERNEL_REFLECTION_CERTIFIED_ROLEWISE` at `data/invariants/integrity/cvx_trace/reports/quotient_kernel_reflection_certificate.json`
- `full_no_escape_closure`: `FULL_NO_ESCAPE_CLOSURE_LEDGER_BUILT_CLOSED` at `data/invariants/integrity/cvx_trace/reports/full_no_escape_closure_ledger.json`
- `t985_univalent_equivalence_obligation`: `T985_UNIVALENT_EQUIVALENCE_BLOCKED_BACKWARD_DIRECTION_MISSING` at `data/invariants/integrity/cvx_trace/reports/t985_univalent_equivalence_obligation.json`

## Next

Formalize P_CVX and standard P in a proof assistant, then prove or refute their extensional equivalence.
