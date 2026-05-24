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
        validate_half_braiding_solver,
    )
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_half_braiding import (
        validate_half_braiding_full_solve,
        validate_half_braiding_prime_stability,
        validate_half_braiding_solver,
    )

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
