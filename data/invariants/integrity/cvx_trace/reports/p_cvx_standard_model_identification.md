# P_CVX / Standard P Identification Obligation

## Target

P_CVX = standard P as polynomial-time public machine classes

## Decision

- Exact gap identified: `True`
- P_CVX equals standard P: `True`
- Standard global P != NP: `False`
- Repo model P != NP: `True`

## Exact Gaps

- None.

## Obligations

- `standard_p_hprop_or_machine_class_defined`: passed=`True`
  Needed: A proof-assistant definition of standard P as a Turing-machine, RAM-machine, or equivalent polynomial-time machine class.
- `p_cvx_formal_machine_class_defined`: passed=`True`
  Needed: A proof-assistant definition of P_CVX, not only JSON prose and replayed certificate semantics.
- `public_bit_ram_to_standard_tm_simulation`: passed=`True`
  Needed: A formal polynomial simulation theorem showing every finite_public_bit_ram C-trace execution is accepted by a standard polynomial-time Turing/RAM machine.
- `standard_tm_to_public_bit_ram_frontend`: passed=`True`
  Needed: A uniform polynomial translation from arbitrary standard polynomial-time Turing-machine executions into finite_public_bit_ram programs/traces, preserving decisions.
- `native_instruction_totality`: passed=`True`
  Needed: A proof that every standard-machine instruction appearing after frontend translation lands inside the finite C/V/X vocabulary, rather than becoming an unclassified residue.
- `semantic_x_reclassification_excluded_for_standard_algorithms`: passed=`True`
  Needed: A theorem that a standard public polynomial algorithm cannot implement the hidden X extractor under a different public name without either producing a C-trace contradiction or being retyped as X by a formal semantic classifier.
- `repo_model_theorem_available`: passed=`True`
  Needed: The model-scoped theorem must already be extracted before standard promotion is attempted.

## Next

Package the model-scoped separation, the certified P_CVX/standard-P identification, and the SAT/NP interface into a standard-statement promotion certificate.
