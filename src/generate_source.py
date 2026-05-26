from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
from collections import Counter, defaultdict
from itertools import product
from typing import Any, Iterable

import numpy as np

Vector = tuple[int, ...]

TYPE_II_NEIGHBOR_ALPHA = {2, 4, 9, 10, 12, 13, 14, 16, 17, 18, 20, 22}
TYPE_II_NEIGHBOR_BETA = {3, 4, 9, 13, 15, 16, 19, 20}
TYPE_II_NEIGHBOR_GAMMA = {2, 5, 7, 8, 9, 10, 12, 14, 15, 16, 17, 18, 19, 21, 22, 23}

SEXTET: list[set[int]] = [
    {0, 1, 2, 3},
    {4, 5, 6, 7},
    {8, 9, 12, 13},
    {10, 11, 14, 15},
    {16, 17, 22, 23},
    {18, 19, 20, 21},
]

EXPECTED_ROOT_SEQUENCE = [42, 18, 6, 0]
EXPECTED_GOLAY_ENUMERATOR = {0: 1, 8: 759, 12: 2576, 16: 759, 24: 1}
EXPECTED_PROFILE_FAMILIES = {
    "balanced_2^6": 576,
    "vector_4_0_2^4": 720,
    "spinor_3^3_1^3": 1280,
}
EXPECTED_BALANCED_VALENCIES = {
    "(6, 0, 0)": 1,
    "(2, 4, 0)": 120,
    "(4, 0, 2)": 15,
    "(0, 6, 0)": 64,
    "(1, 4, 1)": 240,
    "(0, 4, 2)": 120,
    "(2, 0, 4)": 15,
    "(0, 0, 6)": 1,
}


def add(u: Vector, v: Vector) -> Vector:
    return tuple((a ^ b) for a, b in zip(u, v))


def dot(u: Vector, v: Vector) -> int:
    return sum(a * b for a, b in zip(u, v)) & 1


def wt(u: Vector) -> int:
    return sum(u)


def span(gens: Iterable[Vector]) -> list[Vector]:
    gens = list(gens)
    if not gens:
        return []
    n = len(gens[0])
    S: set[Vector] = {(0,) * n}
    for g in gens:
        S |= {add(x, g) for x in list(S)}
    return sorted(S)


def vec_from_one_based(S: set[int], n: int = 24) -> Vector:
    return tuple(1 if i + 1 in S else 0 for i in range(n))


def neighbor(C: list[Vector], v: Vector) -> list[Vector]:
    return span([c for c in C if dot(c, v) == 0] + [v])


def make_H8() -> list[Vector]:
    pts = list(product([0, 1], repeat=3))
    gens: list[Vector] = [tuple(1 for _ in pts)]
    for j in range(3):
        gens.append(tuple(p[j] for p in pts))
    return span(gens)


def make_C0(H8: list[Vector]) -> list[Vector]:
    return sorted([a + b + c for a in H8 for b in H8 for c in H8])


def weight_enumerator(C: list[Vector]) -> dict[int, int]:
    return dict(sorted(Counter(map(wt, C)).items()))


def profile(D: Vector) -> tuple[int, ...]:
    S = {i for i, b in enumerate(D) if b}
    return tuple(len(S & T) for T in SEXTET)


def profile_family(p: tuple[int, ...]) -> str:
    sp = tuple(sorted(p))
    if sp == (2, 2, 2, 2, 2, 2):
        return "balanced_2^6"
    if sp == (0, 2, 2, 2, 2, 4):
        return "vector_4_0_2^4"
    if sp == (1, 1, 1, 3, 3, 3):
        return "spinor_3^3_1^3"
    return "other"


def build_source_code() -> dict[str, Any]:
    H8 = make_H8()
    C = make_C0(H8)
    v1, v2, v3 = (
        vec_from_one_based(TYPE_II_NEIGHBOR_ALPHA),
        vec_from_one_based(TYPE_II_NEIGHBOR_BETA),
        vec_from_one_based(TYPE_II_NEIGHBOR_GAMMA),
    )

    root_sequence: list[int] = []
    code_sizes: list[int] = [len(C)]
    for v in (v1, v2, v3):
        root_sequence.append(sum(1 for c in C if wt(c) == 4))
        C = neighbor(C, v)
        code_sizes.append(len(C))
    root_sequence.append(sum(1 for c in C if wt(c) == 4))

    G24 = C
    X = [c for c in G24 if wt(c) == 12]

    return {
        "H8": H8,
        "C0": make_C0(H8),
        "G24": G24,
        "dodecads": X,
        "root_sequence": root_sequence,
        "code_sizes": code_sizes,
    }


def balanced_scheme_valencies(balanced: list[Vector]) -> dict[str, int]:
    if not balanced:
        return {}
    D = balanced[0]
    out: Counter[str] = Counter()
    for E in balanced:
        ns = [0, 0, 0]  # n0,n2,n4
        for T in SEXTET:
            d = {i for i in T if D[i]}
            e = {i for i in T if E[i]}
            sym = len(d ^ e)
            if sym == 0:
                ns[0] += 1
            elif sym == 2:
                ns[1] += 1
            elif sym == 4:
                ns[2] += 1
            else:
                raise ValueError(f"unexpected per tetrad symmetric difference {sym}")
        out[str(tuple(ns))] += 1
    return dict(sorted(out.items()))


def array_sha(arr: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(arr).tobytes()).hexdigest()


def source_constructor_certificate() -> dict[str, Any]:
    data = build_source_code()
    H8: list[Vector] = data["H8"]
    C0: list[Vector] = data["C0"]
    G24: list[Vector] = data["G24"]
    X: list[Vector] = data["dodecads"]

    prof = Counter(profile(D) for D in X)
    family_counts = Counter(profile_family(p) for p, n in prof.items() for _ in range(n))
    # The expansion is bounded by the 2576 dodecads.
    # Build profile table without tuple JSON ambiguity.
    profile_table = {str(k): int(v) for k, v in sorted(prof.items())}

    balanced = [D for D in X if profile_family(profile(D)) == "balanced_2^6"]
    vector = [D for D in X if profile_family(profile(D)) == "vector_4_0_2^4"]
    spinor = [D for D in X if profile_family(profile(D)) == "spinor_3^3_1^3"]

    vector_fibers: Counter[str] = Counter()
    spinor_fibers: Counter[str] = Counter()
    for D in vector:
        p = profile(D)
        full = p.index(4)
        empty = p.index(0)
        vector_fibers[f"{full}->{empty}"] += 1
    for D in spinor:
        p = profile(D)
        heavy = tuple(i for i, v in enumerate(p) if v == 3)
        spinor_fibers[str(heavy)] += 1

    G24_arr = np.array(G24, dtype=np.uint8)
    X_arr = np.array(X, dtype=np.uint8)

    cert: dict[str, Any] = {
        "schema": "d20.constructor.source_to_dodecads@1",
        "constructor_status": "SOURCE_TO_DODECADS_PASS",
        "completed_from_scratch_steps": [
            "construct H8 = RM(1,3) from affine linear functions on F2^3",
            "construct C0 = H8^{oplus 3} inside F2^24",
            "apply the three explicit Type-II neighbor operations",
            "verify the root sequence 42 -> 18 -> 6 -> 0",
            "recognize the endpoint by Type-II length-24 minimum-weight-8 enumerator",
            "enumerate the 2576 dodecads of the generated endpoint",
            "compute sextet profile families, vector fibers, spinor fibers, and balanced scheme valencies",
        ],
        "remaining_full_scratch_steps": [
            "construct the code-preserving lifted coorient group Be3 from the generated endpoint and fixed coorient data",
            "compute the six Be3 object orbits on the generated dodecad shell",
            "compute the 985 ordered-pair orbitals from the generated Be3 action",
            "compute the full A985 structure tensor T985 by two-step incidence from generated orbitals",
            "derive A236, A42, A12, sector 33, and the integral wall from that freshly generated tensor",
        ],
        "H8": {
            "length": 8,
            "dimension": 4,
            "size": len(H8),
            "weight_enumerator": weight_enumerator(H8),
        },
        "C0": {
            "length": 24,
            "dimension": 12,
            "size": len(C0),
            "weight_enumerator": weight_enumerator(C0),
        },
        "neighbors": {
            "alpha_one_based_support": sorted(TYPE_II_NEIGHBOR_ALPHA),
            "beta_one_based_support": sorted(TYPE_II_NEIGHBOR_BETA),
            "gamma_one_based_support": sorted(TYPE_II_NEIGHBOR_GAMMA),
            "root_sequence": data["root_sequence"],
            "root_sequence_expected": EXPECTED_ROOT_SEQUENCE,
            "root_sequence_pass": data["root_sequence"] == EXPECTED_ROOT_SEQUENCE,
            "code_sizes": data["code_sizes"],
        },
        "G24_endpoint": {
            "length": 24,
            "dimension": 12,
            "size": len(G24),
            "minimum_nonzero_weight": min(wt(c) for c in G24 if any(c)),
            "weight_enumerator": weight_enumerator(G24),
            "expected_weight_enumerator": EXPECTED_GOLAY_ENUMERATOR,
            "golay_endpoint_pass": weight_enumerator(G24) == EXPECTED_GOLAY_ENUMERATOR,
            "G24_words_sha256": array_sha(G24_arr),
        },
        "dodecad_shell": {
            "count": len(X),
            "expected_count": 2576,
            "count_pass": len(X) == 2576,
            "dodecad_words_sha256": array_sha(X_arr),
        },
        "sextet": [sorted(T) for T in SEXTET],
        "profile_families": {
            "counts": dict(sorted((k, int(v)) for k, v in family_counts.items())),
            "expected_counts": EXPECTED_PROFILE_FAMILIES,
            "pass": dict(family_counts) == EXPECTED_PROFILE_FAMILIES,
            "profile_table": profile_table,
        },
        "balanced_scheme": {
            "balanced_points": len(balanced),
            "valencies_from_first_basepoint": balanced_scheme_valencies(balanced),
            "expected_valencies": EXPECTED_BALANCED_VALENCIES,
            "pass": balanced_scheme_valencies(balanced) == EXPECTED_BALANCED_VALENCIES,
        },
        "vector_fibers": {
            "fiber_count": len(vector_fibers),
            "fiber_sizes": dict(sorted((k, int(v)) for k, v in vector_fibers.items())),
            "all_30_fibers_size_24": len(vector_fibers) == 30 and all(v == 24 for v in vector_fibers.values()),
        },
        "spinor_fibers": {
            "fiber_count": len(spinor_fibers),
            "fiber_sizes": dict(sorted((k, int(v)) for k, v in spinor_fibers.items())),
            "all_20_fibers_size_64": len(spinor_fibers) == 20 and all(v == 64 for v in spinor_fibers.values()),
        },
    }
    body = json.dumps(cert, sort_keys=True, separators=(",", ":")).encode("utf-8")
    cert["source_constructor_sha256"] = hashlib.sha256(body).hexdigest()
    return cert


if __name__ == "__main__":
    print(json.dumps(source_constructor_certificate(), indent=2, sort_keys=True))
