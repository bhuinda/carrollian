# Burning static trace evaluator

Status: `D20_TINY_POINTER_A985_BURNING_STATIC_TRACE_EVALUATOR_CONTRACT_CERTIFIED`

The Burning_static_fields representative-to-sector trace evaluator is ready: supplied raw 985-orbital coordinates will be mapped through the canonical A985 character table into all 39 source-sector traces.

Boundary: The contract-certified status means no Burning_static_fields raw representative was present; only the evaluator contract and identity selftest are certified. It is not a Burning support profile.

## Checks

- `burning_intake_report_passed`: `True`
- `canonical_sector_characters_certified`: `True`
- `character_table_shape_is_39_by_985`: `True`
- `input_schema_matches_required_columns`: `True`
- `identity_selftest_passed`: `True`
- `contract_emitted`: `True`
- `no_profile_rows_without_input`: `True`
- `perennial_join_key_emitted_when_available`: `True`
- `input_absent_recorded`: `True`
- `input_validation_rows_empty`: `True`
- `support_summary_rows_empty`: `True`

## Derived

- input present: `False`
- identity selftest rows: `39`
- profile rows: `0`
- support summary rows: `0`

Next: Place the raw Burning_static_fields representative CSV at data/invariants/d20/theorems/tiny_pointer_a985_burning_static_representative_intake/burning_static_representative_input.csv using the emitted schema, then rerun this evaluator to certify the 39-sector trace support.
