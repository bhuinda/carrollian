# Verifier Index

Each layer has `certificate.json` and usually `report.md`. Classes: positive, negative, obstruction, adjoined/external selector.

## Layer 00: `core`
- Directory: `layers/00_core/`
- Class: `positive`
- Expected status: `PASS`
- Declared SHA field: `certificate_sha256`

## Layer 01: `tube_projection_section`
- Directory: `layers/01_tube_projection_section/`
- Class: `positive`
- Declared SHA field: `c985_tube_projection_section_sha256`

## Layer 02: `drinfeld_boundary`
- Directory: `layers/02_drinfeld_boundary/`
- Class: `positive`
- Expected status: `DRINFELD_GROTHENDIECK_BOUNDARY_CERTIFIED`
- Declared SHA field: `drinfeld_boundary_certificate_sha256`

## Layer 03: `drinfeld_grothendieck_center`
- Directory: `layers/03_drinfeld_grothendieck_center/`
- Class: `positive`
- Expected status: `DRINFELD_GROTHENDIECK_CENTER_CERTIFIED`
- Declared SHA field: `drinfeld_grothendieck_center_sha256`

## Layer 04: `drinfeld_idempotent_gluing`
- Directory: `layers/04_drinfeld_idempotent_gluing/`
- Class: `positive`
- Expected status: `DRINFELD_IDEMPOTENT_GLUING_CERTIFIED`
- Declared SHA field: `drinfeld_idempotent_gluing_sha256`

## Layer 05: `drinfeld_wedderburn_trace`
- Directory: `layers/05_drinfeld_wedderburn_trace/`
- Class: `positive`
- Expected status: `DRINFELD_WEDDERBURN_TRACE_CERTIFIED`
- Declared SHA field: `drinfeld_wedderburn_trace_sha256`

## Layer 06: `drinfeld_full_A985_lift`
- Directory: `layers/06_drinfeld_full_A985_lift/`
- Class: `positive`
- Expected status: `DRINFELD_FULL_A985_LIFT_CERTIFIED`
- Declared SHA field: `drinfeld_full_A985_lift_sha256`

## Layer 07: `ribbon_modular_boundary`
- Directory: `layers/07_ribbon_modular_boundary/`
- Class: `negative`
- Expected status: `RIBBON_TWIST_TRIVIAL_AND_MODULAR_S_OBSTRUCTED`
- Declared SHA field: `ribbon_and_modular_boundary_sha256`

## Layer 08: `modular_completion_obstruction`
- Directory: `layers/08_modular_completion_obstruction/`
- Class: `negative`
- Expected status: `MODULAR_COMPLETION_OBSTRUCTION_CERTIFIED`
- Declared SHA field: `modular_completion_obstruction_sha256`

## Layer 09: `tube_kernel_descent_audit`
- Directory: `layers/09_tube_kernel_descent_audit/`
- Class: `negative`
- Expected status: `TUBE_KERNEL_DESCENT_AUDIT_CERTIFIED`
- Declared SHA field: `tube_kernel_descent_audit_sha256`

## Layer 10: `adjoined_hopf_operator`
- Directory: `layers/10_adjoined_hopf_operator/`
- Class: `positive_with_obstruction`
- Expected status: `ADJOINED_HOPF_OPERATOR_CONSTRUCTED`
- Declared SHA field: `adjoined_hopf_operator_sha256`

## Layer 11: `twist_completion_test`
- Directory: `layers/11_twist_completion_test/`
- Class: `negative`
- Expected status: `TWIST_COMPLETION_OBSTRUCTED_FOR_ADJOINED_HOPF_OPERATOR`
- Declared SHA field: `twist_completion_test_sha256`

## Layer 12: `derived_line_surface_trace`
- Directory: `layers/12_derived_line_surface_trace/`
- Class: `positive`
- Expected status: `DERIVED_LINE_SURFACE_TRACE_OPERATOR_CERTIFIED`
- Declared SHA field: `derived_line_surface_trace_sha256`

## Layer 13: `hesse_tube_character_pencil`
- Directory: `layers/13_hesse_tube_character_pencil/`
- Class: `positive`
- Expected status: `HESSE_TUBE_CHARACTER_PENCIL_CERTIFIED`
- Declared SHA field: `hesse_tube_character_pencil_sha256`

## Layer 14: `lasso_uniqueness_pseudomodular_audit`
- Directory: `layers/14_lasso_uniqueness_pseudomodular_audit/`
- Class: `positive_with_correction`
- Expected status: `LASSO_UNIQUENESS_AND_PSEUDOMODULAR_INVARIANT_AUDIT_CERTIFIED`
- Declared SHA field: `lasso_uniqueness_pseudomodular_audit_sha256`

## Layer 15: `intrinsic_carrier_dependency_geometry`
- Directory: `layers/15_intrinsic_carrier_dependency_geometry/`
- Class: `positive`
- Expected status: `INTRINSIC_CARRIER_DEPENDENCY_GEOMETRY_CERTIFIED`
- Declared SHA field: `intrinsic_carrier_dependency_geometry_sha256`

## Layer 16: `mds_arc_hilbert_geometry`
- Directory: `layers/16_mds_arc_hilbert_geometry/`
- Class: `positive`
- Expected status: `MDS_ARC_HILBERT_AND_QUINTIC_WALL_CERTIFIED`
- Declared SHA field: `mds_arc_hilbert_geometry_sha256`

## Layer 17: `wu_golay_quintic_resolvent`
- Directory: `layers/17_wu_golay_quintic_resolvent/`
- Class: `positive_with_open_boundary`
- Expected status: `WU_GOLAY_QUINTIC_RESOLVENT_CERTIFIED_WITH_GOLAY_EXTENSION_UNRESOLVED`
- Declared SHA field: `wu_golay_quintic_resolvent_sha256`

## Layer 18: `canonical_24_syzygy_frame`
- Directory: `layers/18_canonical_24_syzygy_frame/`
- Class: `positive_with_open_boundary`
- Expected status: `CANONICAL_24_COORDINATE_SYZYGY_FRAME_CERTIFIED_GOLAY_SELECTION_STILL_OPEN`
- Declared SHA field: `canonical_24_syzygy_frame_sha256`

## Layer 19: `quadratic_golay_selector_obstruction`
- Directory: `layers/19_quadratic_golay_selector_obstruction/`
- Class: `negative`
- Expected status: `QUADRATIC_GOLAY_SELECTOR_OBSTRUCTION_CERTIFIED`
- Declared SHA field: `quadratic_golay_selector_obstruction_sha256`

## Layer 20: `wu_spinh_6j_marking`
- Directory: `layers/20_wu_spinh_6j_marking/`
- Class: `positive_with_open_boundary`
- Expected status: `WU_SPINH_OCTAD_SPIN12_6J_MARKING_CERTIFIED_GOLAY_SELECTOR_STILL_EXTERNAL`
- Declared SHA field: `wu_spinh_6j_marking_sha256`

## Layer 21: `mog_resolvent_invariant`
- Directory: `layers/21_mog_resolvent_invariant/`
- Class: `positive_with_open_boundary`
- Expected status: `MOG_RESOLVENT_SEXTET_AND_WU_6J_TETRAHEDRON_CERTIFIED_GOLAY_SELECTOR_STILL_EXTERNAL`
- Declared SHA field: `mog_resolvent_invariant_sha256`

## Layer 22: `mog_canonicity_boundary`
- Directory: `layers/22_mog_canonicity_boundary/`
- Class: `positive_with_open_boundary`
- Expected status: `MOG_COLUMN_SEXTET_CANONICITY_CERTIFIED_FULL_ROW_GOLAY_SELECTOR_STILL_EXTERNAL`
- Declared SHA field: `mog_canonicity_boundary_sha256`

## Layer 23: `full_row_refined_selector_obstruction`
- Directory: `layers/23_full_row_refined_selector_obstruction/`
- Class: `negative`
- Expected status: `FULL_ROW_REFINED_GOLAY_SELECTOR_OBSTRUCTION_CERTIFIED_HEXACODE_REQUIRED`
- Declared SHA field: `full_row_refined_golay_selector_obstruction_sha256`

## Layer 24: `hexacode_row_selector`
- Directory: `layers/24_hexacode_row_selector/`
- Class: `positive_with_external_selector`
- Expected status: `HEXACODE_ROW_SELECTOR_CONSTRUCTED_GOLAY_CERTIFIED_CANONICALITY_EXTERNAL`
- Declared SHA field: `hexacode_row_selector_sha256`


## v38 engineering layer

- `.github/workflows/certify.yml`: clean-room CI recipe.
- `tests/tamper_tests.py`: negative verification suite.
- `release/SHA256SUMS.txt`: release checksum ledger.
- `release/SHA256SUMS.sig`: detached signature.
- `tools/verify_release_signature.py`: signature and checksum verifier.
- `tools/export_appendix.py`: paper appendix exporter.
