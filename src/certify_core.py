#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any, Dict

try:
    from .certify_report import assemble_certificate, verified_claims
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_report import assemble_certificate, verified_claims

try:
    from .certify_io import cached_core_block, file_manifest, h_json, load_json, raw_tensor_relpath, ROOT
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_io import cached_core_block, file_manifest, h_json, load_json, raw_tensor_relpath, ROOT

try:
    from .layer_registry import layer_relpath
except ImportError:  # Supports `python src/certify_core.py`.
    from layer_registry import layer_relpath

try:
    from .certify_raw import (
        validate_clopen,
        validate_f_symbol_shape,
        validate_quotients,
        validate_relations,
        validate_simple_branching,
        validate_tensor,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_raw import (
        validate_clopen,
        validate_f_symbol_shape,
        validate_quotients,
        validate_relations,
        validate_simple_branching,
        validate_tensor,
    )

try:
    from .certify_half_braiding import (
        validate_half_braiding_full_solve,
        validate_half_braiding_prime_stability,
        validate_half_braiding_snf_certificate,
        validate_half_braiding_solver,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_half_braiding import (
        validate_half_braiding_full_solve,
        validate_half_braiding_prime_stability,
        validate_half_braiding_snf_certificate,
        validate_half_braiding_solver,
    )

try:
    from .certify_sandpile import validate_sandpile_critical_group
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_sandpile import validate_sandpile_critical_group

try:
    from .certify_public_boundary import validate_public_boundary_graph_invariants
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_public_boundary import validate_public_boundary_graph_invariants

try:
    from .certify_fourier_residue import validate_fourier_residue_screen
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_fourier_residue import validate_fourier_residue_screen

try:
    from .certify_fourier_a985 import validate_fourier_a985_sector_character_candidates
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_fourier_a985 import validate_fourier_a985_sector_character_candidates

try:
    from .certify_fourier_screen0_tube import validate_fourier_screen0_tube_central_element
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_fourier_screen0_tube import validate_fourier_screen0_tube_central_element

try:
    from .certify_tube_sandpile import validate_tube_sandpile_divisor_map
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_tube_sandpile import validate_tube_sandpile_divisor_map

try:
    from .certify_tube_center import (
        validate_tube_center_algebra_lift,
        validate_tube_center_primitive_idempotents,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_tube_center import (
        validate_tube_center_algebra_lift,
        validate_tube_center_primitive_idempotents,
    )

try:
    from .certify_tube_lift import (
        validate_tube_algebra_lift,
        validate_tube_center_lift,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_tube_lift import (
        validate_tube_algebra_lift,
        validate_tube_center_lift,
    )

try:
    from .certify_tube_projection import (
        validate_full_tube_algebra_solver,
        validate_tube_pair_product_oracle,
        validate_tube_projection_section,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_tube_projection import (
        validate_full_tube_algebra_solver,
        validate_tube_pair_product_oracle,
        validate_tube_projection_section,
    )

CORE_FILES = [
    'data/raw/constants.json',
    raw_tensor_relpath(),
    'data/raw/quotients.npz',
    'data/raw/relation_memberships.npz',
    'data/raw/simple_branching_matrices.npz',
    'data/raw/leech_projective_generators.npz',
    layer_relpath('core.a985'),
    'src/certify_core.py',
    'src/certify_half_braiding.py',
    'src/certify_io.py',
    'src/certify_linear.py',
    'src/layer_registry.py',
    'src/certify_raw.py',
    'src/certify_tube_center.py',
    'src/certify_tube_lift.py',
    'src/certify_tube_projection.py',
    'src/certify_report.py',
    'src/solve_half_braiding.py',
    'src/derive_half_braiding_prime_sweep.py',
    'src/derive_half_braiding_local_snf.py',
    'src/derive_half_braiding_snf_certificate.py',
    'src/certify_sandpile.py',
    'src/derive_d20_sandpile_critical_group_theorem.py',
    'data/invariants/hcycle/subscript_Hcycle_d20_edges.csv',
    'data/invariants/d20/theorems/sandpile_critical_group/manifest.json',
    'data/invariants/d20/theorems/sandpile_critical_group/report.json',
    'src/certify_public_boundary.py',
    'src/derive_d20_public_boundary_graph_theorem.py',
    'data/invariants/hcycle/subscript_Hcycle_primitive_cycles.csv',
    'data/invariants/hcycle/d20_Hcycle_automorphism_summary.json',
    'data/invariants/d20/theorems/public_boundary_graph_invariants/manifest.json',
    'data/invariants/d20/theorems/public_boundary_graph_invariants/report.json',
    'src/certify_fourier_residue.py',
    'src/derive_d20_fourier_residue_screen_theorem.py',
    'data/invariants/hcycle/d20_Hcycle_mod2_residue_spectrum_all_subsets.csv',
    'data/invariants/d20/theorems/fourier_residue_screen/manifest.json',
    'data/invariants/d20/theorems/fourier_residue_screen/report.json',
    'src/certify_fourier_a985.py',
    'src/derive_d20_fourier_a985_sector_character_candidates.py',
    'data/invariants/d20/theorems/sector33_unique_public_zero_support/report.json',
    'data/invariants/d20/theorems/sector_idempotent_support_admissibility/report.json',
    'layers/drinfeld/full_a985_lift.json',
    'data/invariants/d20/theorems/fourier_a985_sector_character_candidates/manifest.json',
    'data/invariants/d20/theorems/fourier_a985_sector_character_candidates/report.json',
    'src/certify_fourier_screen0_tube.py',
    'src/derive_d20_fourier_screen0_tube_central_element.py',
    'data/invariants/d20/theorems/fourier_screen0_tube_central_element/manifest.json',
    'data/invariants/d20/theorems/fourier_screen0_tube_central_element/report.json',
    'src/certify_tube_sandpile.py',
    'src/derive_d20_tube_sandpile_divisor_map.py',
    'data/invariants/d20/theorems/tube_sandpile_divisor_map/manifest.json',
    'data/invariants/d20/theorems/tube_sandpile_divisor_map/report.json',
]


def block_or_compute(name: str, compute) -> Dict[str, Any]:
    block = cached_core_block(name)
    if block is not None:
        return block
    return compute()


def build_certificate() -> Dict[str, Any]:
    constants = load_json('data/raw/constants.json')
    manifest = file_manifest(CORE_FILES)
    blocks = {
        'finite_algebra': validate_tensor(constants),
        'relations': validate_relations(),
        'quotients': validate_quotients(),
        'simple_branching': validate_simple_branching(),
        'f_symbol_shape': validate_f_symbol_shape(cached_core_block('f_symbol_shape')),
        'clopen_boundary': validate_clopen(),
        # The derived blocks below are side certificates committed through
        # file_manifest/data_catalog.  Loading them keeps core certification
        # fast; certify_tube_lift and certify_tube_center keep strict
        # recomputation paths.
        'tube_center_lift': block_or_compute('tube_center_lift', validate_tube_center_lift),
        'tube_algebra_lift': block_or_compute('tube_algebra_lift', validate_tube_algebra_lift),
        'tube_center_algebra': block_or_compute('tube_center_algebra', validate_tube_center_algebra_lift),
        'tube_center_primitive_idempotents': validate_tube_center_primitive_idempotents(),
        'tube_pair_product_oracle': block_or_compute('tube_pair_product_oracle', validate_tube_pair_product_oracle),
        'full_tube_algebra_solver': block_or_compute('full_tube_algebra_solver', validate_full_tube_algebra_solver),
        'tube_projection_section': block_or_compute('tube_projection_section', validate_tube_projection_section),
        'half_braiding_solver': validate_half_braiding_solver(),
        'half_braiding_full_solve': validate_half_braiding_full_solve(),
        'half_braiding_prime_stability': validate_half_braiding_prime_stability(),
        'half_braiding_snf_certificate': validate_half_braiding_snf_certificate(),
        'sandpile_critical_group': validate_sandpile_critical_group(),
        'public_boundary_graph_invariants': validate_public_boundary_graph_invariants(),
        'fourier_residue_screen': validate_fourier_residue_screen(),
        'fourier_a985_sector_character_candidates': validate_fourier_a985_sector_character_candidates(),
        'fourier_screen0_tube_central_element': validate_fourier_screen0_tube_central_element(),
        'tube_sandpile_divisor_map': validate_tube_sandpile_divisor_map(),
    }
    return assemble_certificate(
        constants=constants,
        manifest=manifest,
        blocks=blocks,
        claims=verified_claims(blocks),
        hash_json=h_json,
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='certificate.core.json')
    ap.add_argument('--pretty', action='store_true')
    args = ap.parse_args()
    cert = build_certificate()
    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w', encoding='utf-8') as f:
        if args.pretty:
            json.dump(cert, f, indent=2, sort_keys=True)
        else:
            json.dump(cert, f, sort_keys=True, separators=(',', ':'))
        f.write('\n')
    print('PASS')
    print('certificate_sha256 =', cert['certificate_sha256'])
    print('written =', out)


if __name__ == '__main__':
    main()
