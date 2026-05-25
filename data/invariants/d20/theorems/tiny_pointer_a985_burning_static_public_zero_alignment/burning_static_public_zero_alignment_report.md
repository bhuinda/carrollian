# Burning static public-zero alignment

Status: `D20_TINY_POINTER_A985_BURNING_STATIC_PUBLIC_ZERO_ALIGNMENT_CERTIFIED`

The constructed Burning/A985 frame-section traces align with the certified public-zero sector structure: all three constructed generators vanish on sector 33, and two have kernel exactly {33}, the unique primitive public-zero and height-exact support.

Boundary: This compares the repo-native constructed A985-side Burning trace profile to certified public-zero sector supports. It does not assert that an external artifact uses the same generator names.

## Kernels

- `z2_a12_parity` kernel: `[33]`
- `z4_a12_frame_clock` kernel: `[20,33]`
- `z4_a42_clock` kernel: `[33]`

## Checks

- `constructed_representative_certified`: `True`
- `trace_evaluator_ready_or_profile_certified`: `True`
- `public_zero_supports_certified`: `True`
- `sector33_unique_public_zero_certified`: `True`
- `fourier_trace_candidate_evaluation_certified`: `True`
- `public_zero_support_count_is_6_including_zero`: `True`
- `height_exact_public_zero_support_is_33`: `True`
- `all_constructed_generators_vanish_on_sector33`: `True`
- `at_least_two_generators_have_exact_sector33_kernel`: `True`
- `exact_sector33_generators_detect_minimal_public_zero_without_sector33`: `True`
- `kernel_summary_has_three_rows`: `True`
- `alignment_rows_are_3_by_6`: `True`
- `perennial_set_keys_emitted_when_available`: `True`

Next: Promote the exact-{33} constructed generators into a sector-33 detector theorem, then compare future imported Burning_static_fields rows against that detector.
