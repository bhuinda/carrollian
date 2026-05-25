# P_CVX / Standard P Formal Machine Interface

## Status

- `P_CVX_STANDARD_P_FORMAL_MACHINE_INTERFACE_DEFINED`

## Formal File

- `data/invariants/integrity/cvx_trace/formal/PcvxStandardMachineInterface.agda`
- Validation command: `agda -v0 -i data/invariants/integrity/cvx_trace/formal data/invariants/integrity/cvx_trace/formal/PcvxStandardMachineInterface.agda`

## Definitions

- `standard_p`: StandardP is a language-indexed proof-assistant machine class witnessed by a public standard machine, a polynomial time bound, and a decision proof.
- `p_cvx`: P_CVX is a language-indexed proof-assistant machine class witnessed by a finite public C/V/X program whose traces are C-only/no-X and decide the language.
- `equivalence_package`: PCVXStandardPIdentificationPackage names the two class maps plus the semantic X boundary needed to package an extensional equivalence.

## Declaration Audit

- `Language`: passed=`True`
- `StandardMachine`: passed=`True`
- `StandardP`: passed=`True`
- `StandardNP`: passed=`True`
- `CvxProgram`: passed=`True`
- `COnlyTrace`: passed=`True`
- `NoXTrace`: passed=`True`
- `P_CVX`: passed=`True`
- `NP_CVX`: passed=`True`
- `PCVXStandardPEquivalence`: passed=`True`
- `SemanticXBoundary`: passed=`True`
- `PCVXStandardPIdentificationPackage`: passed=`True`

## Next

Bind the certified P_CVX-to-standard and standard-to-P_CVX simulation reports to the PCVXStandardPIdentificationPackage fields.
