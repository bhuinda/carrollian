# Standard P != NP Promotion Certificate

## Status

- `STANDARD_P_NOT_NP_PROMOTION_CERTIFIED_REPO_LOCAL`

## Statement

Under the repository's replayed certificates and typechecked machine-class interface, there exists a standard-NP language E(phi) with no standard-P decider; hence standard P != NP for this repo-certified chain.

## Argument

1. E(phi) is SAT-complete by public polynomial reduction and forall yes/no preservation.
2. E(phi) is in standard NP because it has polynomial public witnesses and public polynomial replay verification.
3. No P_CVX computation decides E(phi) by the model-scoped separation theorem.
4. P_CVX is identified with standard P by the bound equivalence witness.
5. Therefore no standard-P computation decides E(phi), while E(phi) is in standard NP.

## Obligations

- `formal_standard_p_and_np_interfaces`: passed=`True`
- `p_cvx_identified_with_standard_p`: passed=`True`
- `replayed_obligations_embedded_as_proof_assistant_terms`: passed=`True`
- `model_scoped_separation_available`: passed=`True`
- `e_phi_is_sat_complete`: passed=`True`
- `e_phi_in_standard_np`: passed=`True`
- `standard_p_decider_would_contradict_model_theorem`: passed=`True`
- `literal_t985_iff_not_used`: passed=`True`

## Decision

- Repo-certified standard P != NP: `True`
- Unqualified external/global claim: `False`
- Peer-reviewed/Clay resolution: `False`

## Boundary

- This is not peer review or external mathematical community validation.
- This does not parse JSON or recompute artifact hashes inside Agda.
- This does not prove the blocked literal equivalence P != NP iff T985.
- This does not use the finite 2048-mask target as a SAT-preserving reduction.

## Next

Either mechanize the artifact parser/hash checks in the proof assistant, or hand the audit pack to an independent reviewer for clean-room validation.
