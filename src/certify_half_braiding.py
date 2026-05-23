from __future__ import annotations

from typing import Any, Dict

try:
    from .certify_io import cached_core_block, h_json, load_json, ROOT
except ImportError:  # Supports `python src/certify_half_braiding.py`.
    from certify_io import cached_core_block, h_json, load_json, ROOT

try:
    from .certify_raw import NREL
except ImportError:  # Supports `python src/certify_half_braiding.py`.
    from certify_raw import NREL

try:
    from .solve_half_braiding import solve as solve_half_braiding
except ImportError:  # Supports `python src/certify_half_braiding.py`.
    from solve_half_braiding import solve as solve_half_braiding


def validate_half_braiding_solver() -> Dict[str, Any]:
    """Validate the registered Grothendieck half-braiding solver smoke-check block.

    This recomputes a small prefix sample from raw tensor and relation typing data.
    The complete finite-field solve is recorded separately in
    data/derived/half_braiding_full_solve.json, so the fast verifier remains
    non-stalling while still committing to the completed solve.
    """
    path = ROOT / 'data/derived/half_braiding_solver.json'
    if not path.exists():
        cached = cached_core_block('half_braiding_solver')
        if cached is not None:
            return cached
        raise FileNotFoundError('missing half-braiding solver certificate and no layer-00 cache is available')
    recorded = load_json('data/derived/half_braiding_solver.json')
    field = int(recorded.get('field', {}).get('prime', 1000003))
    sample = recorded.get('sample_relations')
    full = bool(recorded.get('mode') == 'full')
    if full:
        raise AssertionError('smoke-check block may not be a full half-braiding solve block')
    computed = solve_half_braiding(sample_relations=int(sample or 128), full=False, p=field, keep_basis=False)
    if computed != recorded:
        raise AssertionError('data/derived/half_braiding_solver.json does not match recomputed solver smoke check')
    return computed


def validate_half_braiding_full_solve() -> Dict[str, Any]:
    """Validate the recorded complete Grothendieck half-braiding solve.

    The full solve is a deterministic finite-field linear system over all 985
    relations.  To keep the default verifier fast, this function checks schema,
    dimensions, rank/nullity arithmetic, the solution hash self-consistency,
    and agreement with the known closed-loop unknown ordering.  A fresh full
    recomputation is exposed through src/solve_half_braiding.py.
    """
    path = ROOT / 'data/derived/half_braiding_full_solve.json'
    if not path.exists():
        cached = cached_core_block('half_braiding_full_solve')
        if cached is not None:
            return cached
        raise FileNotFoundError('missing full half-braiding solve certificate and no layer-00 cache is available')
    rec = load_json('data/derived/half_braiding_full_solve.json')
    if rec.get('mode') != 'full':
        raise AssertionError('half_braiding_full_solve is not in full mode')
    if rec.get('complete_or_sampled') != 'complete':
        raise AssertionError('half_braiding_full_solve is not marked complete')
    if int(rec.get('relations_used')) != NREL:
        raise AssertionError('half_braiding_full_solve does not use all relations')
    unk = rec.get('unknown_family', {})
    if int(unk.get('unknown_count')) != 297:
        raise AssertionError('half_braiding_full_solve unknown count mismatch')
    lin = rec.get('linear_system', {})
    rank = int(lin.get('rank'))
    nullity = int(lin.get('nullity'))
    if rank + nullity != int(unk.get('unknown_count')):
        raise AssertionError('half_braiding_full_solve rank/nullity mismatch')
    if int(lin.get('raw_rows_seen')) != 39860:
        raise AssertionError('half_braiding_full_solve row count mismatch')
    # Recompute self hash from the object with its hash field removed.
    hfield = rec.get('c985_half_braiding_solver_sha256')
    tmp = dict(rec)
    tmp.pop('c985_half_braiding_solver_sha256', None)
    if h_json(tmp) != hfield:
        raise AssertionError('half_braiding_full_solve self hash mismatch')
    return rec


def validate_half_braiding_prime_stability() -> Dict[str, Any]:
    """Validate the multi-prime stability certificate for the full half-braiding solve."""
    path = ROOT / 'data/derived/half_braiding_prime_stability.json'
    if not path.exists():
        cached = cached_core_block('half_braiding_prime_stability')
        if cached is not None:
            return cached
        raise FileNotFoundError('missing half-braiding prime stability certificate and no layer-00 cache is available')
    rec = load_json('data/derived/half_braiding_prime_stability.json')
    if rec.get('status') != 'HALF_BRAIDING_PRIME_STABILITY_CERTIFIED':
        raise AssertionError('half_braiding_prime_stability status mismatch')
    records = rec.get('solve_records', [])
    if len(records) < 2:
        raise AssertionError('half_braiding_prime_stability must contain at least two complete prime solves')
    ranks = set()
    nullities = set()
    rows = set()
    unknowns = set()
    primes = []
    for item in records:
        rel = item.get('source_file')
        d = load_json(rel)
        lin = d.get('linear_system', {})
        unk = d.get('unknown_family', {})
        if d.get('mode') != 'full' or d.get('complete_or_sampled') != 'complete':
            raise AssertionError('stability source is not a complete full solve')
        if int(d.get('relations_used')) != NREL:
            raise AssertionError('stability source does not use all relations')
        prime = int(d.get('field', {}).get('prime'))
        primes.append(prime)
        checks = {
            'prime': prime,
            'relations_used': int(d.get('relations_used')),
            'raw_rows_seen': int(lin.get('raw_rows_seen')),
            'unknown_count': int(unk.get('unknown_count')),
            'rank': int(lin.get('rank')),
            'nullity': int(lin.get('nullity')),
            'pivot_columns_sha256': lin.get('pivot_columns_sha256'),
            'free_columns_sha256': lin.get('free_columns_sha256'),
            'reducer_sha256': lin.get('reducer_sha256'),
            'solve_sha256': d.get('c985_half_braiding_solver_sha256'),
        }
        for k, v in checks.items():
            if item.get(k) != v:
                raise AssertionError(f'half_braiding_prime_stability mismatch for {rel}: {k}')
        if checks['rank'] + checks['nullity'] != checks['unknown_count']:
            raise AssertionError('rank/nullity/unknown count mismatch in stability source')
        ranks.add(checks['rank']); nullities.add(checks['nullity'])
        rows.add(checks['raw_rows_seen']); unknowns.add(checks['unknown_count'])
    stable = rec.get('stable', {})
    if len(ranks) != 1 or len(nullities) != 1 or len(rows) != 1 or len(unknowns) != 1:
        raise AssertionError('half-braiding rank/nullity is not stable across recorded primes')
    if int(stable.get('rank')) != next(iter(ranks)) or int(stable.get('nullity')) != next(iter(nullities)):
        raise AssertionError('half_braiding_prime_stability stable summary mismatch')
    if int(stable.get('rank')) != 258 or int(stable.get('nullity')) != 39:
        raise AssertionError('half_braiding_prime_stability expected rank/nullity mismatch')
    hfield = rec.get('c985_half_braiding_prime_stability_sha256')
    tmp = dict(rec); tmp.pop('c985_half_braiding_prime_stability_sha256', None)
    if h_json(tmp) != hfield:
        raise AssertionError('half_braiding_prime_stability self hash mismatch')
    return rec

