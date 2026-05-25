# A985 perennial sector fingerprints

Status: `D20_TINY_POINTER_A985_PERENNIAL_SECTOR_FINGERPRINTS_CERTIFIED`

All 39 A985 source sectors now have label-independent perennial fingerprints. The semantic fingerprint payload excludes current source/raw sector labels and combines the six-identity trace fingerprint, canonical character row hash, Burning Ship static trace signature, public-zero support projector-hash memberships, and block dimension. A separate coordinate fingerprint binds the same semantic sector to the repository matrix-unit basis.

Boundary: These are canonical repository identifiers, not a theorem that all future external presentations must use the same raw relation order. External presentations should be matched by recomputing the semantic payload or by solving into the repo basis convention.

Perennial ID prefix: `a985pf`

Coordinate fingerprint prefix: `a985coord`

## Checks

- `full_sector_match_certified`: `True`
- `canonical_sector_characters_certified`: `True`
- `source_basis_convention_certified`: `True`
- `burning_static_representative_certified`: `True`
- `support_full_matrix_unit_coo_certified`: `True`
- `fingerprint_rows_cover_39_sectors`: `True`
- `perennial_ids_are_unique`: `True`
- `coordinate_fingerprint_ids_are_unique`: `True`
- `perennial_payload_hashes_are_unique`: `True`
- `coordinate_payload_hashes_are_unique`: `True`
- `semantic_payloads_exclude_current_labels`: `True`
- `matrix_unit_count_is_985`: `True`
- `dimension_histogram_matches_wedderburn_profile`: `True`
- `payload_json_emitted`: `True`
- `lookup_json_emitted`: `True`

Next: Use perennial_id as the sector name in new reports, and keep source/raw sector numbers only as current-coordinate aliases.
