#!/usr/bin/env python3
"""D20 UF kernel v4: height-coherence certificates.

A height certificate for a finite exterior system is a scalar potential h such
that every realized exterior side is strictly oriented:

    A_ext h > 0.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Sequence, Tuple
import itertools
import numpy as np

H6_LABELS = ["B-", "B+", "V-", "V+", "S-", "S+"]

@dataclass
class HeightCoherenceCertificate:
    name: str
    nodes: List[str]
    edges: List[Tuple[int, int, str]]
    A_ext: np.ndarray
    h: np.ndarray
    margins: np.ndarray
    acyclic: bool
    positive: bool
    negative_control: bool = False

    @property
    def min_margin(self) -> int:
        return int(np.min(self.margins)) if self.margins.size else 0

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    def to_json(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "rank_A_ext": int(np.linalg.matrix_rank(self.A_ext.astype(float))) if self.A_ext.size else 0,
            "positive_height_certificate": bool(self.positive),
            "acyclic_incidence_system": bool(self.acyclic),
            "min_margin": self.min_margin,
            "height_vector": [int(x) for x in self.h.tolist()],
            "edge_preview": [
                [self.nodes[u], self.nodes[v], label, int(self.margins[i])]
                for i, (u, v, label) in enumerate(self.edges[:20])
            ],
            "negative_control": bool(self.negative_control),
            "plain_meaning": (
                "one global height h makes every local exterior inequality strictly positive"
                if self.positive else
                "no global height is supplied; this entry is either a rejected obstruction or a negative control"
            ),
        }


def incidence_matrix(n: int, edges: Sequence[Tuple[int, int, str]]) -> np.ndarray:
    A = np.zeros((len(edges), n), dtype=np.int64)
    for r, (u, v, _) in enumerate(edges):
        A[r, v] = 1
        A[r, u] -= 1
    return A


def is_acyclic(n: int, edges: Sequence[Tuple[int, int, str]]) -> bool:
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for u, v, _ in edges:
        adj[u].append(v)
        indeg[v] += 1
    q = [i for i, d in enumerate(indeg) if d == 0]
    seen = 0
    while q:
        u = q.pop()
        seen += 1
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return seen == n


def make_certificate(name: str, nodes: List[str], edges: List[Tuple[int, int, str]], h: Sequence[int], negative_control: bool = False) -> HeightCoherenceCertificate:
    A = incidence_matrix(len(nodes), edges)
    hh = np.array(h, dtype=np.int64)
    margins = A @ hh
    positive = bool(edges and np.all(margins > 0)) or (len(edges) == 0)
    return HeightCoherenceCertificate(
        name=name,
        nodes=nodes,
        edges=edges,
        A_ext=A,
        h=hh,
        margins=margins,
        acyclic=is_acyclic(len(nodes), edges),
        positive=positive,
        negative_control=negative_control,
    )


def tower_descent_height_coherence() -> HeightCoherenceCertificate:
    nodes = ["A985/raw", "A42/Pin", "A12/CY", "D20/public"]
    edges = [
        (0, 1, "q985_to_q42"),
        (1, 2, "saturated_q42_to_q12"),
        (2, 3, "public_middle_boundary"),
    ]
    return make_certificate("tower_descent_height_coherence", nodes, edges, [0, 1, 2, 3])


def d20_face_height_coherence() -> HeightCoherenceCertificate:
    channels = H6_LABELS
    faces = ["{" + ",".join(channels[i] for i in tri) + "}" for tri in itertools.combinations(range(6), 3)]
    nodes = channels + faces
    edges = []
    for fidx, tri in enumerate(itertools.combinations(range(6), 3)):
        face_node = 6 + fidx
        for c in tri:
            edges.append((c, face_node, f"{channels[c]}_supports_{faces[fidx]}"))
    h = [0] * 6 + [1] * 20
    return make_certificate("six_channel_to_D20_face_height_coherence", nodes, edges, h)


def a42_to_a12_height_coherence(a42_to_a12: np.ndarray) -> HeightCoherenceCertificate:
    nodes = [f"A42:{i}" for i in range(42)] + [f"A12:{k}" for k in range(12)]
    edges = []
    for i, k in enumerate(a42_to_a12.tolist()):
        edges.append((i, 42 + int(k), f"class_{i}_descends_to_A12_{int(k)}"))
    h = [0] * 42 + [1] * 12
    return make_certificate("A42_to_A12_saturated_resizing_height_coherence", nodes, edges, h)


def cycle_negative_control() -> HeightCoherenceCertificate:
    nodes = ["x0", "x1", "x2"]
    edges = [(0, 1, "x0_to_x1"), (1, 2, "x1_to_x2"), (2, 0, "x2_to_x0")]
    # Any h fails somewhere; the cycle also gives y=(1,1,1) with A_ext^T y=0.
    return make_certificate("three_cycle_positive_annihilator_control", nodes, edges, [0, 1, 2], negative_control=True)


def positive_annihilator_witness_for_cycle(cert: HeightCoherenceCertificate) -> Dict[str, Any]:
    y = np.ones(cert.edge_count, dtype=np.int64)
    residual = cert.A_ext.T @ y
    return {
        "y": [int(v) for v in y.tolist()],
        "A_ext_T_y": [int(v) for v in residual.tolist()],
        "is_positive_annihilator": bool(np.all(y >= 0) and np.any(y > 0) and np.all(residual == 0)),
    }
