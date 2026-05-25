# Standard P != NP Replay Terms

## Status

- `STANDARD_P_NOT_NP_REPLAY_TERMS_TYPECHECKED`

## Formal File

- `data/invariants/integrity/cvx_trace/formal/StandardPNotNPReplayTerms.agda`
- Validation command: `agda -v0 -i data/invariants/integrity/cvx_trace/formal data/invariants/integrity/cvx_trace/formal/StandardPNotNPReplayTerms.agda`

## Embedded Terms

- `equivalence_terms`: `PcvxStandardEquivalenceReplayTerms`
- `np_side_terms`: `EphiStandardNPReplayTerms`
- `no_standard_p_decider_terms`: `StandardPNoDeciderReplayTerms`
- `standard_statement_term`: `RepoCertifiedStandardPNotNPReplayTerm`
- `canonical_value`: `repoCertifiedStandardPNotNPReplayTermValue`

## Source Audit

- `formal_machine_interface`: passed=`True` status=`P_CVX_STANDARD_P_FORMAL_MACHINE_INTERFACE_DEFINED`
- `public_bit_ram_standard_simulation`: passed=`True` status=`PUBLIC_BIT_RAM_STANDARD_SIMULATION_CERTIFIED`
- `standard_tm_public_bit_ram_frontend`: passed=`True` status=`STANDARD_TM_TO_PUBLIC_BIT_RAM_FRONTEND_CERTIFIED`
- `semantic_x_reclassification`: passed=`True` status=`SEMANTIC_X_RECLASSIFICATION_THEOREM_CERTIFIED`
- `p_cvx_standard_model_identification`: passed=`True` status=`P_CVX_STANDARD_P_IDENTIFICATION_CERTIFIED`
- `p_cvx_standard_equivalence_witness`: passed=`True` status=`P_CVX_STANDARD_P_EQUIVALENCE_WITNESS_BOUND`
- `p_not_np_model_scoped_theorem`: passed=`True` status=`P_NOT_NP_CVX_MODEL_THEOREM_EXTRACTED`
- `encoded_family_sat_frontier`: passed=`True` status=`ENCODED_FAMILY_SAT_COMPLETE_REDUCTION_CERTIFIED`
- `forall_yes_no_preservation`: passed=`True` status=`FORALL_YES_NO_PRESERVATION_THEOREM_CERTIFIED`
- `t985_univalent_equivalence_obligation`: passed=`True` status=`T985_UNIVALENT_EQUIVALENCE_BLOCKED_BACKWARD_DIRECTION_MISSING`

## Next

Either mechanize the artifact parser/hash checks in the proof assistant, or hand the audit pack to an independent reviewer for clean-room validation.
