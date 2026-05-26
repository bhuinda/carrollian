from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .common import ROOT, read_json, repo_rel, sha256_file, sha256_json


PRODUCT_PATTERNS = (
    re.compile(r"\bA985\[(\d{1,4})\]\s*\*\s*A985\[(\d{1,4})\]"),
    re.compile(r"\bA985\((\d{1,4})\s*,\s*(\d{1,4})\)"),
    re.compile(r"\bresidue\(\s*(?:alpha\s*=\s*)?(\d{1,4})\s*,\s*(?:beta\s*=\s*)?(\d{1,4})\s*\)", re.IGNORECASE),
)


def extract_product_terms(
    texts: dict[str, str],
    *,
    relation_count: int = 985,
    claim_id: str | None = None,
) -> list[dict[str, Any]]:
    terms: list[dict[str, Any]] = []
    seen: set[tuple[int, int]] = set()
    for source, text in texts.items():
        for pattern in PRODUCT_PATTERNS:
            for match in pattern.finditer(text):
                alpha = int(match.group(1))
                beta = int(match.group(2))
                key = (alpha, beta)
                if key in seen:
                    continue
                seen.add(key)
                terms.append(
                    {
                        "term_id": f"term_{len(terms) + 1:03d}",
                        "source": source,
                        "alpha": alpha,
                        "beta": beta,
                        "valid": 0 <= alpha < relation_count and 0 <= beta < relation_count,
                        "syntax": match.group(0),
                    }
                )
                if claim_id is not None:
                    terms[-1]["claim_id"] = claim_id
    return terms


def _canonical_section_indices(qmap: Any, class_count: int) -> list[int]:
    import numpy as np

    out: list[int] = []
    for cls in range(class_count):
        hits = np.flatnonzero(qmap == cls)
        if hits.size == 0:
            raise ValueError(f"empty quotient class: {cls}")
        out.append(int(hits[0]))
    return out


def load_q12_section(qmap: Any, *, root: Path = ROOT) -> dict[str, Any]:
    section_path = root / "src/compiler/core/sigma_q12.json"
    class_count = int(qmap.max()) + 1
    if not section_path.exists():
        return {
            "method": "canonical_min_relation_per_q12_class",
            "source": "derived_from_q12_map",
            "indices": _canonical_section_indices(qmap, class_count),
        }

    payload = read_json(section_path)
    indices = [int(x) for x in payload.get("section_indices", [])]
    if len(indices) != class_count:
        raise ValueError(f"q12 section length mismatch: {len(indices)} != {class_count}")
    for cls, rel_id in enumerate(indices):
        if int(qmap[rel_id]) != cls:
            raise ValueError(f"q12 section class mismatch at {cls}: relation {rel_id}")
    return {
        "method": payload.get("section_method", "canonical_min_relation_per_q12_class"),
        "source": repo_rel(section_path, root=root),
        "sha256": sha256_file(section_path),
        "indices": indices,
    }


def _sparse_hash(sparse: list[list[int]]) -> str:
    return sha256_json({"sparse": sparse})


def _vector_hash(vector: list[int]) -> str:
    return sha256_json({"vector": vector})


def _sparse_from_coeffs(coeffs: dict[int, int]) -> list[list[int]]:
    return [[int(index), int(coeff)] for index, coeff in sorted(coeffs.items()) if coeff]


def _boundary_coefficients(sparse: list[list[int]], qmap: Any, class_count: int) -> Any:
    import numpy as np

    out = np.zeros(class_count, dtype=np.int64)
    for relation_id, coeff in sparse:
        out[int(qmap[int(relation_id)])] += int(coeff)
    return out


def _q42_to_q12_map(q42: Any, q12: Any, q42_class_count: int) -> list[int | None]:
    import numpy as np

    out: list[int | None] = []
    for cls in range(q42_class_count):
        vals = np.unique(q12[q42 == cls])
        out.append(int(vals[0]) if vals.size == 1 else None)
    return out


def _transport_q42_coeffs_to_q12(q42_coeffs: Any, q42_to_q12: list[int | None], q12_class_count: int) -> Any:
    import numpy as np

    out = np.zeros(q12_class_count, dtype=np.int64)
    for q42_cls, coeff in enumerate(q42_coeffs.tolist()):
        target = q42_to_q12[q42_cls]
        if target is not None:
            out[int(target)] += int(coeff)
    return out


def _section_residue(
    *,
    rows: Any,
    qmap: Any,
    section: list[int],
    class_count: int,
) -> tuple[list[int], list[list[int]], list[list[int]], Any]:
    import numpy as np

    quotient_coeffs = np.zeros(class_count, dtype=np.int64)
    residue: dict[int, int] = {}
    product_sparse: list[list[int]] = []
    for gamma, coeff in zip(rows[:, 2], rows[:, 3]):
        g = int(gamma)
        c = int(coeff)
        product_sparse.append([g, c])
        quotient_coeffs[int(qmap[g])] += c
        residue[g] = residue.get(g, 0) + c

    for cls, coeff in enumerate(quotient_coeffs.tolist()):
        if coeff:
            lift = int(section[cls])
            residue[lift] = residue.get(lift, 0) - int(coeff)

    residue_sparse = _sparse_from_coeffs(residue)
    boundary = _boundary_coefficients(residue_sparse, qmap, class_count)
    return quotient_coeffs.astype(int).tolist(), product_sparse, residue_sparse, boundary


def _canonical_cycle(cycle: list[int]) -> tuple[int, ...]:
    variants: list[tuple[int, ...]] = []
    n = len(cycle)
    for seq in (cycle, list(reversed(cycle))):
        for i in range(n):
            rotated = seq[i:] + seq[:i]
            variants.append(tuple(rotated))
    return min(variants)


def _d20_selector(root: Path) -> dict[str, Any]:
    selector_path = root / "data/invariants/d20/d20_d6_selector_derivation.json"
    payload = read_json(selector_path)
    root_edges = payload.get("root_edges", [])
    edge_set: set[tuple[int, int]] = set()
    labels: dict[int, list[str]] = {}
    for edge in root_edges:
        indices = [int(x) for x in edge.get("edge_indices", [])]
        face_labels = edge.get("face_labels", [])
        if len(indices) != 2:
            continue
        edge_set.add(tuple(sorted(indices)))
        for index, label in zip(indices, face_labels):
            labels[index] = [str(part) for part in label]

    vertices = sorted(labels)
    adjacency: dict[int, set[int]] = {vertex: set() for vertex in vertices}
    for a, b in edge_set:
        adjacency.setdefault(a, set()).add(b)
        adjacency.setdefault(b, set()).add(a)

    cycles: set[tuple[int, ...]] = set()
    for start in vertices:
        stack: list[tuple[int, list[int]]] = [(start, [start])]
        while stack:
            current, path = stack.pop()
            if len(path) == 5:
                if start in adjacency[current]:
                    cycles.add(_canonical_cycle(path))
                continue
            for nxt in sorted(adjacency[current]):
                if nxt in path:
                    continue
                stack.append((nxt, path + [nxt]))

    pentagons = [list(cycle) for cycle in sorted(cycles)]
    degree_histogram: dict[str, int] = {}
    for degree in (len(adjacency.get(vertex, ())) for vertex in vertices):
        degree_histogram[str(degree)] = degree_histogram.get(str(degree), 0) + 1
    graph_checks = {
        "vertex_count_is_20": len(vertices) == 20,
        "edge_count_is_30": len(edge_set) == 30,
        "degree_histogram_is_3_regular": degree_histogram == {"3": 20},
        "pentagon_cycle_count_is_12": len(pentagons) == 12,
        "source_status_is_d20_selector": payload.get("status") == "D20_SELECTOR_DERIVED_FROM_D6_COXETER_POLARITY",
    }
    return {
        "source": repo_rel(selector_path, root=root),
        "sha256": sha256_file(selector_path),
        "vertices": [{"index": index, "label": labels[index]} for index in vertices],
        "edges": [list(edge) for edge in sorted(edge_set)],
        "degree_histogram": degree_histogram,
        "pentagon_cycles": pentagons,
        "graph_checks": graph_checks,
        "graph_valid": all(graph_checks.values()),
    }


def _d20_readout(coefficients_q12: list[int], selector: dict[str, Any]) -> dict[str, Any]:
    cycles = selector.get("pentagon_cycles", [])
    vector = [0 for _ in range(20)]
    for q12_class, coeff in enumerate(coefficients_q12):
        if q12_class >= len(cycles):
            continue
        for vertex in cycles[q12_class]:
            vector[int(vertex)] += int(coeff)
    return {
        "method": "canonical_sorted_d20_pentagon_incidence_from_q12",
        "vector": vector,
        "zero": all(value == 0 for value in vector),
        "sha256": _vector_hash(vector),
    }


def compute_q12_section_residues(terms: list[dict[str, Any]], *, root: Path = ROOT) -> dict[str, Any]:
    import numpy as np

    tensor_path = root / "data/raw/Halloween.npz"
    quotient_path = root / "data/raw/quotients.npz"
    tensor = np.load(tensor_path, allow_pickle=False)
    quotients = np.load(quotient_path, allow_pickle=False)
    triples = np.asarray(tensor["triples"], dtype=np.int64)
    q42 = np.asarray(quotients["q42_map"], dtype=np.int64)
    q12 = np.asarray(quotients["q12_map"], dtype=np.int64)
    q42_class_count = int(q42.max()) + 1
    q12_class_count = int(q12.max()) + 1
    q42_section = _canonical_section_indices(q42, q42_class_count)
    section_payload = load_q12_section(q12, root=root)
    q12_section = section_payload["indices"]
    q42_to_q12 = _q42_to_q12_map(q42, q12, q42_class_count)
    d20_selector = _d20_selector(root)

    computed: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []
    for term in terms:
        alpha = int(term["alpha"])
        beta = int(term["beta"])
        if not term.get("valid", False):
            invalid.append({**term, "status": "INVALID_RELATION_ID"})
            continue

        rows = triples[(triples[:, 0] == alpha) & (triples[:, 1] == beta)]
        q42_coeffs, product_sparse, q42_residue_sparse, q42_boundary = _section_residue(
            rows=rows,
            qmap=q42,
            section=q42_section,
            class_count=q42_class_count,
        )
        q12_coeffs, _product_sparse, q12_residue_sparse, q12_boundary = _section_residue(
            rows=rows,
            qmap=q12,
            section=q12_section,
            class_count=q12_class_count,
        )
        q42_to_q12_coeffs = _transport_q42_coeffs_to_q12(np.asarray(q42_coeffs, dtype=np.int64), q42_to_q12, q12_class_count)
        q42_boundary_to_q12 = _transport_q42_coeffs_to_q12(q42_boundary, q42_to_q12, q12_class_count)
        product_d20 = _d20_readout(q12_coeffs, d20_selector)
        q12_residue_d20 = _d20_readout(q12_boundary.astype(int).tolist(), d20_selector)
        q42_residue_d20 = _d20_readout(q42_boundary_to_q12.astype(int).tolist(), d20_selector)

        computed.append(
            {
                **term,
                "status": "COMPUTED",
                "alpha_q42": int(q42[alpha]),
                "beta_q42": int(q42[beta]),
                "alpha_q12": int(q12[alpha]),
                "beta_q12": int(q12[beta]),
                "product": {
                    "sparse": product_sparse,
                    "nnz": len(product_sparse),
                    "coefficient_total": int(rows[:, 3].sum()) if rows.size else 0,
                    "sha256": _sparse_hash(product_sparse),
                },
                "a42": {
                    "section": {
                        "method": "canonical_min_relation_per_q42_class",
                        "source": "derived_from_q42_map",
                        "indices": q42_section,
                    },
                    "quotient_coefficients_q42": q42_coeffs,
                    "residue": {
                        "sparse": q42_residue_sparse,
                        "nnz": len(q42_residue_sparse),
                        "l1": int(sum(abs(coeff) for _, coeff in q42_residue_sparse)),
                        "q42_boundary_zero": bool(np.all(q42_boundary == 0)),
                        "q42_boundary_coefficients": q42_boundary.astype(int).tolist(),
                        "q12_transport_boundary_zero": bool(np.all(q42_boundary_to_q12 == 0)),
                        "q12_transport_boundary_coefficients": q42_boundary_to_q12.astype(int).tolist(),
                        "sha256": _sparse_hash(q42_residue_sparse),
                    },
                    "transport_to_q12": {
                        "q42_to_q12": q42_to_q12,
                        "direct_q12_coefficients": q12_coeffs,
                        "from_q42_coefficients": q42_to_q12_coeffs.astype(int).tolist(),
                        "coefficients_consistent": bool(np.array_equal(q42_to_q12_coeffs, np.asarray(q12_coeffs, dtype=np.int64))),
                    },
                },
                "q12": {
                    "section": {
                        "method": section_payload.get("method"),
                        "source": section_payload.get("source"),
                        "sha256": section_payload.get("sha256"),
                        "indices": q12_section,
                    },
                    "quotient_coefficients_q12": q12_coeffs,
                    "residue": {
                        "sparse": q12_residue_sparse,
                        "nnz": len(q12_residue_sparse),
                        "l1": int(sum(abs(coeff) for _, coeff in q12_residue_sparse)),
                        "q12_boundary_zero": bool(np.all(q12_boundary == 0)),
                        "q12_boundary_coefficients": q12_boundary.astype(int).tolist(),
                        "sha256": _sparse_hash(q12_residue_sparse),
                    },
                },
                "d20": {
                    "selector": d20_selector,
                    "product_readout": product_d20,
                    "q12_residue_readout": q12_residue_d20,
                    "a42_residue_readout": q42_residue_d20,
                    "q12_residue_boundary_zero": q12_residue_d20["zero"],
                    "a42_residue_boundary_zero": q42_residue_d20["zero"],
                    "graph_valid": d20_selector["graph_valid"],
                },
                "quotient_coefficients_q12": q12_coeffs,
                "residue": {
                    "sparse": q12_residue_sparse,
                    "nnz": len(q12_residue_sparse),
                    "l1": int(sum(abs(coeff) for _, coeff in q12_residue_sparse)),
                    "q12_boundary_zero": bool(np.all(q12_boundary == 0)),
                    "q12_boundary_coefficients": q12_boundary.astype(int).tolist(),
                    "sha256": _sparse_hash(q12_residue_sparse),
                },
            }
        )

    return {
        "schema": "holotopy.quotient_tower_residue",
        "sections": {
            "q42": {
                "method": "canonical_min_relation_per_q42_class",
                "source": "derived_from_q42_map",
                "indices": q42_section,
            },
            "q12": section_payload,
        },
        "quotient": "A12",
        "class_count": q12_class_count,
        "q42_class_count": q42_class_count,
        "d20_selector": d20_selector,
        "term_count": len(terms),
        "computed_count": len(computed),
        "invalid_count": len(invalid),
        "terms": computed,
        "invalid_terms": invalid,
    }
