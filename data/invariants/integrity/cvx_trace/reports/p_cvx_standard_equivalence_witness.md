# P_CVX / Standard P Equivalence Witness

## Status

- `P_CVX_STANDARD_P_EQUIVALENCE_WITNESS_BOUND`

## Bound Fields

- `pcvxToStandardP`: passed=`True`; source=`data/invariants/integrity/cvx_trace/reports/public_bit_ram_standard_simulation.json`
- `standardPToPCVX`: passed=`True`; source=`data/invariants/integrity/cvx_trace/reports/standard_tm_public_bit_ram_frontend.json`
- `semanticXBoundary`: passed=`True`; source=`data/invariants/integrity/cvx_trace/reports/semantic_x_reclassification_theorem.json`
- `extensionalEquivalence`: passed=`True`; source=`data/invariants/integrity/cvx_trace/reports/p_cvx_standard_model_identification.json`

## Decision

- Equivalence witness bound: `True`
- P_CVX equals standard P: `True`
- Standard global P != NP from this artifact alone: `False`

## Next

Use the bound P_CVX/standard-P equivalence, model separation, SAT-complete E(phi), and standard-NP witness interface to emit the standard-statement promotion certificate.
