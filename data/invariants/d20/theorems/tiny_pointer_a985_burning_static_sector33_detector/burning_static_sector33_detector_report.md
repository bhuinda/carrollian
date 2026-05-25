# Burning static sector-33 detector

Status: `D20_TINY_POINTER_A985_BURNING_STATIC_SECTOR33_DETECTOR_CERTIFIED`

The constructed Burning/A985 frame-section traces provide a reusable detector for source sector 33: the selected constructed quotient generators vanish exactly on source sector 33, so either their individual vanishing or their joint vanishing selects that sector.

Boundary: This is a repo-native constructed A985-side detector. It does not assert that an external Burning_static_fields artifact uses the same generator names.

## Detector

- generators: `['z2_a12_parity', 'z4_a42_clock']`
- detected by all-zero test: `[33]`
- detected by any-zero test: `[33]`
- source sector 33 raw sector: `19`, block dimension: `2`

## Checks

- `alignment_certified`: `True`
- `constructed_representative_certified`: `True`
- `full_sector_match_certified`: `True`
- `sector33_unique_public_zero_certified`: `True`
- `detector_generators_are_expected`: `True`
- `detector_generators_have_exact_sector33_kernel`: `True`
- `detector_table_has_all_39_source_sectors`: `True`
- `all_zero_detector_is_unique_sector33`: `True`
- `any_zero_detector_is_unique_sector33`: `True`
- `sector33_source_to_raw_match_recorded`: `True`
- `sector33_block_dimension_is_two`: `True`
- `perennial_join_key_emitted_when_available`: `True`

Next: Use this sector-33 detector as the acceptance test for any future imported Burning_static_fields representative rows, then attach accepted rows to the source-sector matching ledger.
