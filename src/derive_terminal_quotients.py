from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def sha_array(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def load_json(path: Path) -> Any:
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def relation_hashes(encoded: np.ndarray, offsets: np.ndarray) -> list[str]:
    out: list[str] = []
    for a in range(offsets.size - 1):
        seg = np.sort(encoded[int(offsets[a]):int(offsets[a + 1])]).astype(np.int64, copy=False)
        out.append(sha_array(seg))
    return out


def offdiag_q42_label(i: int, j: int) -> int:
    if i == j:
        raise ValueError('offdiag_q42_label requires i != j')
    k = 0
    for a in range(6):
        for b in range(6):
            if a == b:
                continue
            if a == i and b == j:
                return 12 + k
            k += 1
    raise AssertionError('unreachable')


def cross_q12_label(s: int, t: int) -> int:
    if s == t:
        raise ValueError('cross_q12_label requires s != t')
    k = 0
    for a in range(3):
        for b in range(3):
            if a == b:
                continue
            if a == s and b == t:
                return 6 + k
            k += 1
    raise AssertionError('unreachable')


def quotient_tensor_from_sparse(triples: np.ndarray, qmap: np.ndarray, nclasses: int) -> tuple[np.ndarray, dict[str, Any]]:
    a = qmap[triples[:, 0]]
    b = qmap[triples[:, 1]]
    c = qmap[triples[:, 2]]
    w = triples[:, 3].astype(np.int64, copy=False)
    agg = np.zeros((nclasses, nclasses, nclasses), dtype=np.int64)
    np.add.at(agg, (a, b, c), w)
    sizes = np.bincount(qmap, minlength=nclasses).astype(np.int64)
    divisible = True
    for k in range(nclasses):
        if sizes[k] and np.any(agg[:, :, k] % sizes[k]):
            divisible = False
            break
    return agg, {
        'classes': int(nclasses),
        'class_size_min': int(sizes.min()),
        'class_size_max': int(sizes.max()),
        'class_sizes': sizes.astype(int).tolist(),
        'nonzero': int(np.count_nonzero(agg)),
        'coefficient_total_raw_aggregated': int(agg.sum()),
        'normalized_integer_divisibility': bool(divisible),
        'tensor_sha256': sha_array(agg),
        'stored_convention': 'raw_expanded_aggregation_total',
    }


def derive_terminal_quotients(
    relation_npz: Path,
    tensor_npz: Path,
    selector_json: Path,
    out_npz: Path | None = None,
    compare_npz: Path | None = None,
) -> dict[str, Any]:
    rel = np.load(relation_npz)
    encoded = np.asarray(rel['encoded_pairs'], dtype=np.int64)
    offsets = np.asarray(rel['offsets'], dtype=np.int64)
    block_i = np.asarray(rel['block_i'], dtype=np.int16)
    block_j = np.asarray(rel['block_j'], dtype=np.int16)
    reps = np.asarray(rel['reps'], dtype=np.int32)
    nrel = offsets.size - 1
    selector = load_json(selector_json)
    object_to_sector = [int(x) for x in selector['object_to_sector']]
    if len(object_to_sector) != 6:
        raise ValueError('selector object_to_sector must have length 6')

    hashes = relation_hashes(encoded, offsets)
    special_by_obj: dict[int, int] = {}
    hash_to_relation = {h: a for a, h in enumerate(hashes)}
    missing = []
    for item in selector['diagonal_special_relation_hashes']:
        obj = int(item['object'])
        h = item['relation_hash']
        a = hash_to_relation.get(h)
        if a is None:
            missing.append({'object': obj, 'relation_hash': h})
            continue
        if int(block_i[a]) != obj or int(block_j[a]) != obj:
            raise ValueError(f'special selector for object {obj} matched non-diagonal/non-object relation {a}')
        special_by_obj[obj] = int(a)
    if missing:
        raise ValueError(f'missing special relation hashes: {missing}')
    if sorted(special_by_obj) != list(range(6)):
        raise ValueError(f'special_by_obj missing objects: {special_by_obj}')

    q42 = np.empty(nrel, dtype=np.int16)
    q12 = np.empty(nrel, dtype=np.int16)
    special_set = set(special_by_obj.values())
    for a in range(nrel):
        i = int(block_i[a]); j = int(block_j[a])
        si = object_to_sector[i]; sj = object_to_sector[j]
        if i == j:
            if a in special_set:
                q42[a] = i
                q12[a] = si
            else:
                q42[a] = 6 + i
                q12[a] = 3 + si
        else:
            q42[a] = offdiag_q42_label(i, j)
            if si == sj:
                q12[a] = 3 + si
            else:
                q12[a] = cross_q12_label(si, sj)

    T = np.load(tensor_npz)
    triples = np.asarray(T['triples'], dtype=np.int64)
    q42t, q42_meta = quotient_tensor_from_sparse(triples, q42.astype(np.int64), 42)
    q12t, q12_meta = quotient_tensor_from_sparse(triples, q12.astype(np.int64), 12)

    q42_to_q12 = []
    q42_to_q12_consistent = True
    for cls in range(42):
        vals = np.unique(q12[q42 == cls])
        if vals.size != 1:
            q42_to_q12.append(None)
            q42_to_q12_consistent = False
        else:
            q42_to_q12.append(int(vals[0]))

    if out_npz is not None:
        out_npz.parent.mkdir(parents=True, exist_ok=True)
        np.savez(
            out_npz,
            q42_map=q42,
            q12_map=q12,
            q42_tensor=q42t,
            q12_tensor=q12t,
            block_i=block_i,
            block_j=block_j,
            special_relations=np.array([special_by_obj[i] for i in range(6)], dtype=np.int32),
            object_to_sector=np.array(object_to_sector, dtype=np.int16),
        )

    comparison: dict[str, Any] = {}
    if compare_npz is not None and compare_npz.exists():
        z = np.load(compare_npz)
        cq42 = np.asarray(z['q42_map'], dtype=np.int16)
        cq12 = np.asarray(z['q12_map'], dtype=np.int16)
        cq42t = np.asarray(z['q42_tensor'], dtype=np.int64)
        cq12t = np.asarray(z['q12_tensor'], dtype=np.int64)
        comparison = {
            'matches_supplied_q42_map': bool(np.array_equal(q42, cq42)),
            'matches_supplied_q12_map': bool(np.array_equal(q12, cq12)),
            'matches_supplied_q42_tensor': bool(np.array_equal(q42t, cq42t)),
            'matches_supplied_q12_tensor': bool(np.array_equal(q12t, cq12t)),
            'supplied_q42_tensor_sha256': sha_array(cq42t),
            'supplied_q12_tensor_sha256': sha_array(cq12t),
        }

    ok = q42_to_q12_consistent and q42_meta['classes'] == 42 and q12_meta['classes'] == 12
    if comparison:
        ok = ok and all(v for k, v in comparison.items() if k.startswith('matches_'))

    result: dict[str, Any] = {
        'schema': 'd20.constructor.terminal_quotients@1',
        'constructor_status': 'TERMINAL_QUOTIENTS_PASS' if ok else 'TERMINAL_QUOTIENTS_FAIL',
        'construction_method': 'derive A42 and A12 maps from generated Gamma relation partition using a six-hash terminal diagonal selector, then aggregate the generated T985 tensor',
        'predicate': 'is integral',
        'input_boundary': 'uses a small terminal quotient selector containing object-to-sector labels and six diagonal special relation hashes; does not use supplied q42/q12 maps or quotient tensors',
        'relation_npz': str(relation_npz.relative_to(ROOT)) if relation_npz.is_relative_to(ROOT) else str(relation_npz),
        'tensor_npz': str(tensor_npz.relative_to(ROOT)) if tensor_npz.is_relative_to(ROOT) else str(tensor_npz),
        'selector_json': str(selector_json.relative_to(ROOT)) if selector_json.is_relative_to(ROOT) else str(selector_json),
        'relations': int(nrel),
        'special_relations_by_object': {str(k): int(v) for k, v in special_by_obj.items()},
        'object_to_sector': object_to_sector,
        'q42': q42_meta,
        'q12': q12_meta,
        'q42_to_q12_consistent': bool(q42_to_q12_consistent),
        'q42_to_q12': q42_to_q12,
        'q42_map_sha256': sha_array(q42),
        'q12_map_sha256': sha_array(q12),
        'comparison': comparison,
        'output_npz': str(out_npz.relative_to(ROOT)) if out_npz is not None and out_npz.exists() and out_npz.is_relative_to(ROOT) else (str(out_npz) if out_npz is not None and out_npz.exists() else None),
        'remaining_boundary': [
            'derive the six diagonal special selector hashes from an intrinsic coorient formula instead of storing them as a selector seed',
            'derive the A985->A236 semisimple profunctor/fusion functor from generated T985/tube data',
            'derive sector 33 and the integral wall from generated center/idempotent data rather than the proof-system integrity layer certificate',
        ],
    }
    body = json.dumps(result, sort_keys=True, separators=(',', ':')).encode('utf-8')
    result['constructor_result_sha256'] = hashlib.sha256(body).hexdigest()
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description='Derive A42/A12 terminal quotient maps and tensors without using supplied quotient maps.')
    ap.add_argument('--relation-npz', default='generated/relation_memberships_from_source_coorient_aligned.npz')
    ap.add_argument('--tensor-npz', default='generated/tensor_from_source_coorient.npz')
    ap.add_argument('--selector-json', default='data/quotient/terminal_quotient_selector.json')
    ap.add_argument('--out-npz', default='generated/terminal_quotients_from_source_coorient.npz')
    ap.add_argument('--out-json', default='generated/terminal_quotients_from_source_coorient_report.json')
    ap.add_argument('--compare', default='data/raw/quotients.npz')
    ap.add_argument('--pretty', action='store_true')
    args = ap.parse_args()
    result = derive_terminal_quotients(
        ROOT / args.relation_npz,
        ROOT / args.tensor_npz,
        ROOT / args.selector_json,
        ROOT / args.out_npz if args.out_npz else None,
        ROOT / args.compare if args.compare else None,
    )
    out = ROOT / args.out_json
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True), encoding='utf-8')
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))


if __name__ == '__main__':
    main()
