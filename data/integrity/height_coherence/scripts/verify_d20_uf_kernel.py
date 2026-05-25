#!/usr/bin/env python3
"""Verifier for D20 UF kernel source_drop: height coherence certificates."""
from __future__ import annotations
import argparse, csv, hashlib, json, sys
from pathlib import Path
from typing import Any, Dict
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from d20_height_coherence import (
    tower_descent_height_coherence,
    d20_face_height_coherence,
    a42_to_a12_height_coherence,
    cycle_negative_control,
    positive_annihilator_witness_for_cycle,
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def sha256_array(arr: np.ndarray) -> str:
    arr = np.ascontiguousarray(arr)
    return hashlib.sha256(arr.tobytes()).hexdigest()


def bridge_saturation_check(data: np.lib.npyio.NpzFile) -> Dict[str, Any]:
    q = data['a42_to_a12'].astype(np.int64)
    C42 = data['q42_structure_constants'].astype(object)
    C12 = data['q12_structure_constants'].astype(object)
    L = np.zeros((12, 42), dtype=object)
    for i, k in enumerate(q):
        L[int(k), i] = 1

    product_bad = []
    lift_bad = []
    for K in range(12):
        if sum(int(x) for x in L[K]) != int(np.sum(q == K)):
            lift_bad.append(K)
    for I in range(12):
        for J in range(12):
            prod42 = np.einsum('i,j,ijk->k', L[I], L[J], C42, optimize=True)
            rhs42 = np.einsum('K,Ki->i', C12[I, J, :], L, optimize=True)
            if not np.array_equal(prod42, rhs42):
                product_bad.append([I, J])

    # Regression guard: atom-by-atom projection is known to be too strong and must remain rejected.
    pointwise_failures = 0
    for i in range(42):
        for j in range(42):
            prod42 = C42[i, j, :]
            projected = np.zeros(12, dtype=object)
            for k, c in enumerate(prod42):
                if c:
                    projected[int(q[k])] += c
            prod12 = C12[int(q[i]), int(q[j]), :]
            if not np.array_equal(projected, prod12):
                pointwise_failures += 1

    return {
        'valid_saturated_bridge': not product_bad and not lift_bad,
        'lift_bad_preview': lift_bad[:10],
        'saturated_product_bad_preview': product_bad[:10],
        'pointwise_atom_projection_failures': int(pointwise_failures),
        'pointwise_atom_projection_status': 'REJECTED_AS_TOO_STRONG' if pointwise_failures else 'UNEXPECTEDLY_VALID',
    }


def write_cert_table(path: Path, certs: list) -> None:
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['name', 'nodes', 'edges', 'rank_A_ext', 'acyclic', 'positive_height_certificate', 'min_margin', 'negative_control'])
        for c in certs:
            j = c.to_json()
            w.writerow([
                j['name'], j['node_count'], j['edge_count'], j['rank_A_ext'],
                j['acyclic_incidence_system'], j['positive_height_certificate'],
                j['min_margin'], j['negative_control'],
            ])


def write_edges(path: Path, cert) -> None:
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['source', 'target', 'label', 'margin'])
        for i, (u, v, label) in enumerate(cert.edges):
            w.writerow([cert.nodes[u], cert.nodes[v], label, int(cert.margins[i])])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--arrays', default='arrays/d20_uf_kernel_arrays.npz')
    ap.add_argument('--outdir', default='.')
    args = ap.parse_args()

    outdir = Path(args.outdir).resolve()
    arrays = Path(args.arrays)
    if not arrays.is_absolute():
        arrays = outdir / arrays
    arrays = arrays / 'd20_uf_kernel_arrays.npz' if arrays.is_dir() else arrays
    data = np.load(arrays, allow_pickle=True)
    q = data['a42_to_a12'].astype(np.int64)

    certs = [
        tower_descent_height_coherence(),
        d20_face_height_coherence(),
        a42_to_a12_height_coherence(q),
        cycle_negative_control(),
    ]
    pos = [c for c in certs if not c.negative_control]
    neg = [c for c in certs if c.negative_control]

    tables = outdir / 'tables'
    examples = outdir / 'examples'
    tables.mkdir(exist_ok=True)
    examples.mkdir(exist_ok=True)
    write_cert_table(tables / 'height_coherence_certificates.csv', certs)
    for c in certs:
        write_edges(tables / (c.name + '_edges.csv'), c)

    neg_witness = positive_annihilator_witness_for_cycle(neg[0])
    bridge = bridge_saturation_check(data)
    status_ok = (
        all(c.positive and c.acyclic for c in pos)
        and all((not c.positive) and (not c.acyclic) for c in neg)
        and neg_witness['is_positive_annihilator']
        and bridge['valid_saturated_bridge']
    )

    certificate = {
        'schema': 'd20.uf_kernel.height_coherence.source_drop',
        'status': 'D20_UF_KERNEL_HEIGHT_COHERENCE_CERTIFIED' if status_ok else 'D20_UF_KERNEL_HEIGHT_COHERENCE_FAILED',
        'official_terms': {
            'box_judgment': 'BoxHeight(A_ext,h)',
            'formal_name': 'height coherence',
            'source_terms': {
                'BoxMonism': 'BoxHeight(A_ext,h)',
                'height monism': 'height coherence',
            },
        },
        'input': {
            'arrays_path': str(arrays),
            'arrays_sha256': sha256_file(arrays),
            'a42_to_a12_sha256': sha256_array(q),
            'raw_halloween_npz_present': Path('/mnt/data/halloween.npz').exists(),
            'raw_halloween_npz_sha256': sha256_file(Path('/mnt/data/halloween.npz')) if Path('/mnt/data/halloween.npz').exists() else None,
        },
        'definition': {
            'height_certificate': 'A_ext h > 0',
            'height_coherence': 'one global height h makes every local exterior inequality strictly positive',
            'box_rule': 'BoxHeight(A_ext,h) is accepted exactly when min(A_ext h)>0',
            'obstruction': 'a nonzero y>=0 with A_ext^T y=0 is a positive circular obstruction',
            'gordan_alternative': 'exactly one: exists h with A_ext h > 0, or exists nonzero y>=0 with A_ext^T y=0',
        },
        'height_coherence_certificates': [c.to_json() for c in certs],
        'negative_control_positive_annihilator': neg_witness,
        'saturated_resizing_guard': bridge,
        'kernel_update': {
            'new_primitive_judgment': 'BoxHeight(A_ext,h)',
            'acceptance_rule': 'accept iff every entry of A_ext h is strictly positive',
            'rejection_rule': 'if a nonzero y>=0 with A_ext^T y=0 is exhibited, reject and return the annihilator witness',
            'constructive_univalence_gate': {
                'required_witnesses': [
                    'equivalence_witness',
                    'zero_transport_residue',
                    'height_coherence',
                ],
            },
        },
    }

    (outdir / 'certificate.json').write_text(json.dumps(certificate, indent=2), encoding='utf-8')
    (examples / 'box_height_examples.json').write_text(json.dumps({
        'BoxHeight_examples': [
            {'name': 'tower descent', 'edges': 'tables/tower_descent_height_coherence_edges.csv', 'h': '[0,1,2,3]'},
            {'name': 'six-channel public D20 faces', 'edges': 'tables/six_channel_to_D20_face_height_coherence_edges.csv', 'h': '0 on H6, 1 on Lambda^3 H6'},
            {'name': 'A42 to A12 saturated descent', 'edges': 'tables/A42_to_A12_saturated_resizing_height_coherence_edges.csv', 'h': '0 on A42 atoms, 1 on A12 fused classes'},
            {'name': 'negative control cycle', 'annihilator': 'y=(1,1,1), A_ext^T y=0'},
        ]
    }, indent=2), encoding='utf-8')

    rows = []
    for c in certs:
        j = c.to_json()
        result = 'PASS' if (j['positive_height_certificate'] and not j['negative_control']) or ((not j['positive_height_certificate']) and j['negative_control']) else 'FAIL'
        rows.append(f"| `{j['name']}` | {j['node_count']} | {j['edge_count']} | {j['min_margin']} | {result} |")

    report = f"""# D20 UF Kernel source_drop: height coherence

## Status

`{certificate['status']}`

## Main correction

The formal certificate is **height coherence**.

Use:

```text
BoxHeight(A_ext, h) := min(A_ext h) > 0
```

A height certificate is a single global height vector that makes every local exterior constraint point forward.

## Certified height-coherence tests

| certificate | nodes | edges | min margin | result |
|---|---:|---:|---:|---|
""" + "\n".join(rows) + f"""

## Gordan interpretation

For a realized exterior matrix `A_ext`, Gordan duality gives exactly one of the following:

```text
exists h with A_ext h > 0
```

or

```text
exists nonzero y >= 0 with A_ext^T y = 0
```

The package certifies the positive side for the tower, the six-channel public face layer, and saturated `A42 -> A12` resizing. It also includes a three-cycle negative control with explicit annihilator:

```json
{json.dumps(neg_witness)}
```

## Saturated quotient guard

The source_drop correction is preserved:

```text
A42 -> A12 is valid only after saturation, not as pointwise atom projection.
```

Regression guard:

```text
pointwise atom projection failures = {bridge['pointwise_atom_projection_failures']}
```

Saturated bridge status:

```text
valid_saturated_bridge = {bridge['valid_saturated_bridge']}
```

## Kernel update

The judgment layer gains:

```text
Xi; Delta; Sigma; Gamma |- BoxHeight(A_ext,h)
```

with verifier rule:

```text
accept iff every entry of A_ext h is strictly positive.
```

Constructive univalence gate:

```text
equivalence witness + zero transport residue + height coherence
```

## Source term mapping

| source term | formal term | verifier meaning |
|---|---|---|
| `BoxMonism` | `BoxHeight` | checked global-height certificate |
| positive annihilator | positive circular obstruction | local constraints form a loop and no global height exists |
| saturated resizing | saturated resizing | compress whole fibers, not isolated atoms |
| residue equality | zero readout difference | two handles have the same certified readout |

## Current stack

```text
T985 -> typed normalizer -> saturated quotient resizing -> BoxHeight height coherence
```
"""
    (outdir / 'd20_uf_kernel_report.md').write_text(report, encoding='utf-8')
    print(json.dumps(certificate, indent=2))

if __name__ == '__main__':
    main()
